"""Read-only Modbus TCP gateway; the former transparent relay is removed."""

from __future__ import annotations

import asyncio
from functools import partial
import hashlib
import logging
import os
import ssl
import struct

RELAY_HOST = "127.0.0.1"
RELAY_PORT = 5062
RMS_HOST = "127.0.0.1"
RMS_PORT = 5061
TIMEOUT = 10

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOG = logging.getLogger("rms-gateway")


def allowed_fingerprints() -> frozenset[str]:
    fingerprints = frozenset(
        value.strip().lower()
        for value in os.environ["RMS_GATEWAY_CLIENT_SHA256"].split(",")
    )
    if not fingerprints or any(
        len(value) != 64 or any(char not in "0123456789abcdef" for char in value)
        for value in fingerprints
    ):
        raise ValueError("RMS_GATEWAY_CLIENT_SHA256 requires SHA-256 fingerprints (64 hex digits)")
    return fingerprints


def tls_context() -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(
        os.environ["RMS_GATEWAY_CERT"], os.environ["RMS_GATEWAY_KEY"]
    )
    context.load_verify_locations(cafile=os.environ["RMS_GATEWAY_CA"])
    return context


async def handle_client(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    allowed: frozenset[str],
) -> None:
    peer = client_writer.get_extra_info("peername")
    rms_writer = None
    try:
        tls = client_writer.get_extra_info("ssl_object")
        certificate = tls.getpeercert(binary_form=True) if tls else None
        identity = hashlib.sha256(certificate).hexdigest() if certificate else None
        if identity not in allowed:
            LOG.warning(
                "decision=denied peer=%s identity=%s reason=unapproved_certificate",
                peer, identity,
            )
            return
        LOG.info("client authenticated: peer=%s identity=%s role=partner_read", peer, identity)
        while True:
            # TCP chunks are not Modbus frames. Validate an entire ADU before
            # forwarding any bytes, including when clients pipeline requests.
            header = await asyncio.wait_for(client_reader.readexactly(7), TIMEOUT)
            transaction, protocol, length, unit = struct.unpack(">HHHB", header)
            if protocol != 0 or not 2 <= length <= 254:
                LOG.warning("decision=denied peer=%s reason=invalid_mbap", peer)
                return
            pdu = await asyncio.wait_for(
                client_reader.readexactly(length - 1), TIMEOUT
            )
            function = pdu[0]
            address = quantity = None
            if function in {5, 6, 15, 16, 22, 23} and len(pdu) >= 5:
                address = struct.unpack(">H", pdu[1:3])[0]
            exception = 0
            if unit != 1:
                exception = 2  # Illegal Data Address: only device 1 is exposed.
            elif function not in {1, 3}:
                exception = 1  # Illegal Function: every write is denied.
            elif len(pdu) != 5:
                exception = 3  # Illegal Data Value: malformed read request.
            else:
                address, quantity = struct.unpack(">HH", pdu[1:])
                limit = 2 if function == 1 else 6
                if quantity == 0:
                    exception = 3
                elif address + quantity > limit:
                    exception = 2

            if exception:
                LOG.warning(
                    "decision=denied peer=%s identity=%s role=partner_read transaction=%s unit=%s "
                    "function=%s offset=%s count=%s exception=%s",
                    peer, identity, transaction, unit, function, address, quantity, exception,
                )
                client_writer.write(
                    struct.pack(">HHHBBB", transaction, 0, 3, unit,
                                function | 0x80, exception)
                )
                await asyncio.wait_for(client_writer.drain(), TIMEOUT)
                continue

            if rms_writer is None:
                rms_reader, rms_writer = await asyncio.wait_for(
                    asyncio.open_connection(RMS_HOST, RMS_PORT), TIMEOUT
                )
            rms_writer.write(header + pdu)
            await asyncio.wait_for(rms_writer.drain(), TIMEOUT)
            response_header = await asyncio.wait_for(
                rms_reader.readexactly(7), TIMEOUT
            )
            response_transaction, response_protocol, response_length, response_unit = (
                struct.unpack(">HHHB", response_header)
            )
            if (
                response_transaction != transaction
                or response_protocol != 0
                or response_unit != unit
                or not 2 <= response_length <= 254
            ):
                LOG.warning("decision=closed peer=%s reason=invalid_backend_mbap", peer)
                return
            response = await asyncio.wait_for(
                rms_reader.readexactly(response_length - 1), TIMEOUT
            )
            if response[0] not in {function, function | 0x80}:
                LOG.warning("decision=closed peer=%s reason=invalid_backend_function", peer)
                return
            client_writer.write(response_header + response)
            await asyncio.wait_for(client_writer.drain(), TIMEOUT)
            LOG.info(
                "decision=allowed peer=%s identity=%s role=partner_read transaction=%s unit=%s "
                "function=%s offset=%s count=%s",
                peer, identity, transaction, unit, function, address, quantity,
            )
    except asyncio.IncompleteReadError as exc:
        if exc.partial:
            LOG.warning("decision=closed peer=%s reason=truncated_frame", peer)
    except (OSError, TimeoutError) as exc:
        LOG.warning("decision=closed peer=%s reason=%s", peer, type(exc).__name__)
    finally:
        writers = [client_writer]
        if rms_writer is not None:
            writers.append(rms_writer)
        for writer in writers:
            writer.close()
        await asyncio.gather(
            *(writer.wait_closed() for writer in writers), return_exceptions=True
        )
        LOG.info("client disconnected: %s", peer)


async def main() -> None:
    allowed = allowed_fingerprints()
    context = tls_context()
    server = await asyncio.start_server(
        partial(handle_client, allowed=allowed), RELAY_HOST, RELAY_PORT,
        ssl=context, ssl_handshake_timeout=TIMEOUT, ssl_shutdown_timeout=TIMEOUT,
    )
    LOG.info(
        "read-only Modbus gateway on %s:%s, backend %s:%s; "
        "device=1 allowed_functions=1,3 mutual_tls=required approved_certificates=%s",
        RELAY_HOST, RELAY_PORT, RMS_HOST, RMS_PORT,
        len(allowed),
    )
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
