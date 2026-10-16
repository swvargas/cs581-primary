"""Isolated gateway tests: no plant connection or actual process writes."""

import asyncio
from functools import partial
import hashlib
import os
from pathlib import Path
import ssl
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import rms_relay


def setUpModule():
    global certificates, certificate_directory, tls_environment, fingerprints
    certificate_directory = tempfile.TemporaryDirectory(prefix="rms-gateway-tests-")
    unittest.addModuleCleanup(certificate_directory.cleanup)
    certificates = Path(certificate_directory.name)

    def openssl(*arguments):
        subprocess.run(
            ["openssl", *arguments], cwd=certificates, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )

    openssl("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "2",
            "-subj", "/CN=Gateway Test CA", "-keyout", "ca.key", "-out", "ca.pem",
            "-addext", "basicConstraints=critical,CA:TRUE",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign")
    for name in ("server", "approved", "unlisted"):
        extensions = (
            ["-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1",
             "-addext", "extendedKeyUsage=serverAuth"]
            if name == "server" else ["-addext", "extendedKeyUsage=clientAuth"]
        )
        openssl("req", "-new", "-newkey", "rsa:2048", "-nodes",
                "-subj", "/CN=localhost" if name == "server" else "/CN=Same Partner",
                "-keyout", f"{name}.key", "-out", f"{name}.csr", *extensions)
        openssl("x509", "-req", "-in", f"{name}.csr", "-CA", "ca.pem",
                "-CAkey", "ca.key", "-CAcreateserial", "-days", "2",
                "-copy_extensions", "copy", "-out", f"{name}.pem")
    openssl("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "2",
            "-subj", "/CN=Same Partner", "-keyout", "rogue.key", "-out", "rogue.pem",
            "-addext", "extendedKeyUsage=clientAuth")
    fingerprints = {
        name: hashlib.sha256(ssl.PEM_cert_to_DER_cert(
            (certificates / f"{name}.pem").read_text()
        )).hexdigest()
        for name in ("approved", "unlisted", "rogue")
    }
    tls_environment = {
        "RMS_GATEWAY_CERT": str(certificates / "server.pem"),
        "RMS_GATEWAY_KEY": str(certificates / "server.key"),
        "RMS_GATEWAY_CA": str(certificates / "ca.pem"),
        "RMS_GATEWAY_CLIENT_SHA256": fingerprints["approved"],
    }


class ConfigurationTests(unittest.TestCase):
    def test_tls_context_requires_verified_client_certificates(self):
        with patch.dict(os.environ, tls_environment, clear=True):
            context = rms_relay.tls_context()
        self.assertIsInstance(context, ssl.SSLContext)
        self.assertEqual(context.protocol, ssl.PROTOCOL_TLS_SERVER)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)

    def test_missing_tls_environment_fails_closed(self):
        for name in ("RMS_GATEWAY_CERT", "RMS_GATEWAY_KEY", "RMS_GATEWAY_CA"):
            with self.subTest(name=name):
                environment = {key: value for key, value in tls_environment.items()
                               if key != name}
                with patch.dict(os.environ, environment, clear=True):
                    with self.assertRaises((KeyError, ValueError, RuntimeError, OSError)):
                        rms_relay.tls_context()

    def test_empty_tls_paths_fail_closed(self):
        for name in ("RMS_GATEWAY_CERT", "RMS_GATEWAY_KEY", "RMS_GATEWAY_CA"):
            with self.subTest(name=name):
                with patch.dict(os.environ, {**tls_environment, name: ""}, clear=True):
                    with self.assertRaises((KeyError, ValueError, RuntimeError, OSError)):
                        rms_relay.tls_context()

    def test_allowlist_is_a_frozenset_of_certificate_fingerprints(self):
        value = fingerprints["approved"] + "," + fingerprints["unlisted"]
        with patch.dict(os.environ, {"RMS_GATEWAY_CLIENT_SHA256": value}, clear=True):
            allowed = rms_relay.allowed_fingerprints()
        self.assertIsInstance(allowed, frozenset)
        self.assertEqual(allowed, frozenset((fingerprints["approved"], fingerprints["unlisted"])))

    def test_missing_empty_and_malformed_allowlist_fail_closed(self):
        for value in (None, "", " ", ",", "a" * 63, "a" * 65, "g" * 64,
                      ":".join(["aa"] * 32), fingerprints["approved"] + ",",
                      fingerprints["approved"] + ",invalid"):
            with self.subTest(value=value):
                environment = {} if value is None else {"RMS_GATEWAY_CLIENT_SHA256": value}
                with patch.dict(os.environ, environment, clear=True):
                    with self.assertRaises((KeyError, ValueError, RuntimeError)):
                        rms_relay.allowed_fingerprints()


def frame(function, address=3, value=1, transaction=7, unit=1):
    return struct.pack(">HHHBBHH", transaction, 0, 6, unit, function, address, value)


class GatewayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.forwarded = []
        self.tasks = set()
        self.writers = []
        self.backend_response = None
        self.backend_connections = 0

        async def backend(reader, writer):
            self.backend_connections += 1
            try:
                while True:
                    header = await reader.readexactly(7)
                    transaction, _, length, unit = struct.unpack(">HHHB", header)
                    pdu = await reader.readexactly(length - 1)
                    self.forwarded.append(header + pdu)
                    if self.backend_response is not None:
                        writer.write(self.backend_response)
                        await writer.drain()
                        return
                    if pdu[0] == 3:
                        quantity = struct.unpack(">H", pdu[3:5])[0]
                        response = bytes([3, quantity * 2]) + b"\x00\xfa" * quantity
                    else:
                        response = b"\x01\x01\x00"
                    writer.write(struct.pack(">HHHB", transaction, 0,
                                             len(response) + 1, unit) + response)
                    await writer.drain()
            except asyncio.IncompleteReadError:
                pass
            finally:
                writer.close()
                await writer.wait_closed()

        def tracked(handler):
            def start(reader, writer):
                task = asyncio.create_task(handler(reader, writer))
                self.tasks.add(task)
            return start

        self.backend = await asyncio.start_server(tracked(backend), "127.0.0.1", 0)
        port = self.backend.sockets[0].getsockname()[1]
        self.patch = patch.object(rms_relay, "RMS_PORT", port)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        with patch.dict(os.environ, tls_environment, clear=True):
            context = rms_relay.tls_context()
            allowed = rms_relay.allowed_fingerprints()
        self.gateway = await asyncio.start_server(
            tracked(partial(rms_relay.handle_client, allowed=allowed)), "127.0.0.1", 0,
            ssl=context, ssl_handshake_timeout=10, ssl_shutdown_timeout=10,
        )

    async def asyncTearDown(self):
        for writer in self.writers:
            writer.close()
        await asyncio.gather(*(writer.wait_closed() for writer in self.writers),
                             return_exceptions=True)
        self.gateway.close()
        self.backend.close()
        await self.gateway.wait_closed()
        await self.backend.wait_closed()
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)

    async def connect(self, certificate="approved"):
        context = ssl.create_default_context(cafile=str(certificates / "ca.pem"))
        if certificate is not None:
            context.load_cert_chain(str(certificates / f"{certificate}.pem"),
                                    str(certificates / f"{certificate}.key"))
        reader, writer = await asyncio.open_connection(
            "127.0.0.1", self.gateway.sockets[0].getsockname()[1],
            ssl=context, server_hostname="localhost", ssl_handshake_timeout=2,
            ssl_shutdown_timeout=2,
        )
        self.writers.append(writer)
        return reader, writer

    async def response(self, reader):
        header = await asyncio.wait_for(reader.readexactly(7), 1)
        length = struct.unpack(">HHHB", header)[2]
        return header, await asyncio.wait_for(reader.readexactly(length - 1), 1)

    async def test_reads_and_fragmented_frames(self):
        reader, writer = await self.connect()
        for request in (frame(3), frame(3, 0, 6), frame(1, 0, 2)):
            for byte in request:
                writer.write(bytes([byte]))
                await writer.drain()
                await asyncio.sleep(0)
            header, pdu = await self.response(reader)
            self.assertEqual(header[:4], request[:4])
            self.assertEqual(pdu[0], request[7])
        self.assertEqual(len(self.forwarded), 3)

    async def test_all_writes_and_unknown_functions_denied(self):
        reader, writer = await self.connect()
        for function in (5, 6, 15, 16, 22, 23, 2, 4, 43, 255):
            writer.write(frame(function, value=300))
            await writer.drain()
            _, pdu = await self.response(reader)
            self.assertEqual(pdu, bytes([function | 128, 1]))
        self.assertEqual(self.forwarded, [])

    async def test_coalesced_read_write_read(self):
        reader, writer = await self.connect()
        first = frame(3, transaction=1)
        write = frame(6, value=300, transaction=2)
        last = frame(3, transaction=3)
        writer.write(first + write + last)
        await writer.drain()
        self.assertEqual((await self.response(reader))[1], b"\x03\x02\x00\xfa")
        self.assertEqual((await self.response(reader))[1], b"\x86\x01")
        self.assertEqual((await self.response(reader))[1], b"\x03\x02\x00\xfa")
        self.assertEqual(self.forwarded, [first, last])

    async def test_invalid_reads_denied(self):
        reader, writer = await self.connect()
        for request, code in (
            (frame(3, unit=0), 2), (frame(3, unit=2), 2),
            (frame(3, value=0), 3), (frame(3, 6, 1), 2),
            (frame(3, 5, 2), 2), (frame(1, 2, 1), 2),
            (struct.pack(">HHHB", 7, 0, 2, 1) + b"\x03", 3),
        ):
            writer.write(request)
            await writer.drain()
            _, pdu = await self.response(reader)
            self.assertEqual(pdu, bytes([request[7] | 128, code]))
        self.assertEqual(self.forwarded, [])

    async def test_bad_mbap_closes_without_forwarding(self):
        for protocol, length in ((1, 6), (0, 0), (0, 1), (0, 255)):
            reader, writer = await self.connect()
            writer.write(struct.pack(">HHHB", 7, protocol, length, 1))
            await writer.drain()
            self.assertEqual(await asyncio.wait_for(reader.read(1), 1), b"")
        self.assertEqual(self.forwarded, [])

    async def test_truncated_frame_closes_without_forwarding(self):
        for fragment in (frame(3)[:3], frame(3)[:-1]):
            reader, writer = await self.connect()
            writer.write(fragment)
            await writer.drain()
            # TLS has no half-close; close_notify ends the incomplete frame.
            writer.close()
            await writer.wait_closed()
            self.assertEqual(await asyncio.wait_for(reader.read(1), 1), b"")
        await asyncio.wait_for(asyncio.gather(*self.tasks), 2)
        self.assertEqual(self.forwarded, [])

    async def test_incomplete_frame_timeout(self):
        with patch.object(rms_relay, "TIMEOUT", 0.05):
            reader, writer = await self.connect()
            writer.write(frame(3)[:8])
            await writer.drain()
            self.assertEqual(await asyncio.wait_for(reader.read(1), 1), b"")
        self.assertEqual(self.forwarded, [])

    async def test_backend_unavailable_closes_read_but_still_denies_write(self):
        self.backend.close()
        await self.backend.wait_closed()
        reader, writer = await self.connect()
        writer.write(frame(6, value=300))
        await writer.drain()
        self.assertEqual((await self.response(reader))[1], b"\x86\x01")
        writer.write(frame(3))
        await writer.drain()
        self.assertEqual(await asyncio.wait_for(reader.read(1), 1), b"")

    async def test_denial_log_records_certificate_identity_and_role(self):
        with self.assertLogs("rms-gateway", level="INFO") as logs:
            reader, writer = await self.connect()
            writer.write(frame(6, value=300))
            await writer.drain()
            self.assertEqual((await self.response(reader))[1], b"\x86\x01")
        denial = next(line for line in logs.output if "decision=denied" in line)
        self.assertIn("peer=('127.0.0.1',", denial)
        self.assertIn(f"identity={fingerprints['approved']}", denial)
        self.assertIn("role=partner_read", denial)
        self.assertIn("function=6 offset=3", denial)
        self.assertEqual(self.forwarded, [])

    async def test_approved_read_logs_certificate_identity_and_role(self):
        with self.assertLogs("rms-gateway", level="INFO") as logs:
            reader, writer = await self.connect()
            writer.write(frame(3))
            await writer.drain()
            self.assertEqual((await self.response(reader))[1], b"\x03\x02\x00\xfa")
        allowed = next(line for line in logs.output if "decision=allowed" in line)
        self.assertIn(f"identity={fingerprints['approved']}", allowed)
        self.assertIn("role=partner_read", allowed)
        self.assertEqual(self.forwarded, [frame(3)])

    async def test_missing_untrusted_and_unlisted_certificates_never_forward(self):
        for certificate in (None, "rogue", "unlisted"):
            with self.subTest(certificate=certificate):
                # TLS 1.3 may report server rejection only on the first read.
                try:
                    reader, writer = await asyncio.wait_for(self.connect(certificate), 2)
                    writer.write(frame(3))
                    await writer.drain()
                    self.assertEqual(await asyncio.wait_for(reader.read(1), 2), b"")
                except (ssl.SSLError, ConnectionError):
                    pass
                self.assertEqual(self.forwarded, [])
                self.assertEqual(self.backend_connections, 0)

    async def test_plaintext_on_tls_listener_never_forwards(self):
        reader, writer = await asyncio.open_connection(
            "127.0.0.1", self.gateway.sockets[0].getsockname()[1]
        )
        self.writers.append(writer)
        writer.write(frame(3))
        await writer.drain()
        try:
            self.assertEqual(await asyncio.wait_for(reader.read(1), 2), b"")
        except ConnectionError:
            pass
        self.assertEqual(self.forwarded, [])
        self.assertEqual(self.backend_connections, 0)

    async def test_main_starts_only_tls_server_with_required_timeouts(self):
        server = MagicMock()
        server.__aenter__.return_value = server
        server.serve_forever = AsyncMock()
        with patch.dict(os.environ, tls_environment, clear=True):
            with patch.object(rms_relay.asyncio, "start_server", new_callable=AsyncMock,
                              return_value=server) as start:
                await rms_relay.main()
        start.assert_awaited_once()
        arguments, options = start.call_args
        handler = arguments[0]
        self.assertIsInstance(handler, partial)
        self.assertIs(handler.func, rms_relay.handle_client)
        self.assertEqual(handler.keywords["allowed"], frozenset((fingerprints["approved"],)))
        self.assertIsInstance(options["ssl"], ssl.SSLContext)
        self.assertEqual(options["ssl"].verify_mode, ssl.CERT_REQUIRED)
        self.assertEqual(options["ssl_handshake_timeout"], 10)
        self.assertEqual(options["ssl_shutdown_timeout"], 10)

    async def test_main_invalid_configuration_never_opens_listener(self):
        for name in tls_environment:
            with self.subTest(name=name):
                environment = {key: value for key, value in tls_environment.items()
                               if key != name}
                with patch.dict(os.environ, environment, clear=True):
                    with patch.object(rms_relay.asyncio, "start_server",
                                      new_callable=AsyncMock) as start:
                        with self.assertRaises((KeyError, ValueError, RuntimeError, OSError)):
                            await rms_relay.main()
                        start.assert_not_awaited()

    async def test_handler_without_tls_or_peer_certificate_fails_closed(self):
        for has_ssl in (False, True):
            with self.subTest(has_ssl=has_ssl):
                reader = AsyncMock()
                writer = MagicMock()
                writer.wait_closed = AsyncMock()
                ssl_object = MagicMock()
                ssl_object.getpeercert.return_value = None
                writer.get_extra_info.side_effect = lambda name: (
                    ssl_object if name == "ssl_object" and has_ssl else None
                )
                with patch.object(rms_relay.asyncio, "open_connection",
                                  new_callable=AsyncMock) as backend:
                    await rms_relay.handle_client(
                        reader, writer, allowed=frozenset((fingerprints["approved"],))
                    )
                backend.assert_not_awaited()
                reader.readexactly.assert_not_awaited()
                writer.close.assert_called_once()
                if has_ssl:
                    ssl_object.getpeercert.assert_called_once_with(binary_form=True)

    async def test_invalid_or_truncated_backend_response_closes(self):
        for response in (
            struct.pack(">HHHB", 8, 0, 5, 1),  # Wrong transaction.
            struct.pack(">HHHB", 7, 1, 5, 1),  # Wrong protocol.
            struct.pack(">HHHB", 7, 0, 5, 2),  # Wrong device.
            struct.pack(">HHHB", 7, 0, 255, 1),  # Oversized response.
            struct.pack(">HHHB", 7, 0, 2, 1) + b"\x06",  # Wrong function.
            frame(3)[:3],  # Truncated header.
            struct.pack(">HHHB", 7, 0, 5, 1) + b"\x03",  # Truncated body.
        ):
            with self.subTest(response=response):
                self.backend_response = response
                reader, writer = await self.connect()
                writer.write(frame(3))
                await writer.drain()
                self.assertEqual(await asyncio.wait_for(reader.read(1), 1), b"")

    async def test_backend_exception_preserved(self):
        self.backend_response = struct.pack(">HHHB", 7, 0, 3, 1) + b"\x83\x02"
        reader, writer = await self.connect()
        writer.write(frame(3))
        await writer.drain()
        header, pdu = await self.response(reader)
        self.assertEqual(header + pdu, self.backend_response)

    async def test_partner_probe_reads_and_checks_write_denial(self):
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-B", str(Path(__file__).with_name("rms_gateway_client.py")),
            "--port", str(self.gateway.sockets[0].getsockname()[1]),
            "--ca", str(certificates / "ca.pem"),
            "--cert", str(certificates / "approved.pem"),
            "--key", str(certificates / "approved.key"), "--test-write",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), 5)
        self.assertEqual(process.returncode, 0, stderr.decode())
        self.assertIn(b"Threshold: 250", stdout)
        self.assertIn(b"Write response: 8601", stdout)
        self.assertIn(b"Threshold after denied write: 250", stdout)
        self.assertEqual([request[7] for request in self.forwarded], [3, 3])

    async def test_partner_probe_verifies_server_hostname(self):
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-B", str(Path(__file__).with_name("rms_gateway_client.py")),
            "--port", str(self.gateway.sockets[0].getsockname()[1]),
            "--server-name", "wrong.example",
            "--ca", str(certificates / "ca.pem"),
            "--cert", str(certificates / "approved.pem"),
            "--key", str(certificates / "approved.key"),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await asyncio.wait_for(process.communicate(), 5)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn(b"CERTIFICATE_VERIFY_FAILED", stderr)
        self.assertEqual(self.forwarded, [])


if __name__ == "__main__":
    unittest.main()
