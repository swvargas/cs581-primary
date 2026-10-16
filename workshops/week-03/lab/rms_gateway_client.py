"""Partner probe: standard Modbus TCP frames inside mutually authenticated TLS."""

import argparse
from datetime import datetime, timezone
import socket
import ssl
import struct


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5062)
    parser.add_argument("--server-name", default="localhost")
    parser.add_argument("--ca", required=True)
    parser.add_argument("--cert", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--test-write", action="store_true",
                        help="Authorized lab test only: attempt 300, require baseline 250")
    args = parser.parse_args()
    context = ssl.create_default_context(cafile=args.ca)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(args.cert, args.key)

    with socket.create_connection((args.host, args.port), timeout=10) as tcp:
        with context.wrap_socket(tcp, server_hostname=args.server_name) as connection:
            transaction = 0

            def exchange(function, value):
                nonlocal transaction
                transaction += 1
                connection.sendall(
                    struct.pack(">HHHBBHH", transaction, 0, 6, 1, function, 3, value)
                )

                def receive(count):
                    data = bytearray()
                    while len(data) < count:
                        chunk = connection.recv(count - len(data))
                        if not chunk:
                            raise ConnectionError("Gateway closed the connection")
                        data.extend(chunk)
                    return bytes(data)

                header = receive(7)
                response_id, protocol, length, unit = struct.unpack(">HHHB", header)
                if (response_id != transaction or protocol != 0 or unit != 1
                        or not 2 <= length <= 254):
                    raise RuntimeError("Invalid Modbus response header")
                return receive(length - 1)

            def read():
                response = exchange(3, 1)
                if len(response) != 4 or response[:2] != b"\x03\x02":
                    raise RuntimeError(f"Unexpected read response: {response.hex()}")
                return struct.unpack(">H", response[2:])[0]

            original = read()
            print(f"{datetime.now(timezone.utc).isoformat()} Threshold: {original}")
            if args.test_write:
                if original != 250:
                    raise RuntimeError("Expected baseline 250; stopping without a write")
                # A regression or incorrect deployment could allow the write.
                # Attempt restoration unless an explicit denial was received.
                denied = False
                try:
                    response = exchange(6, 300)
                    denied = response == b"\x86\x01"
                    print(f"Write response: {response.hex()} (expected 8601)")
                    if not denied:
                        raise RuntimeError("Write was not explicitly denied")
                finally:
                    if not denied:
                        exchange(6, original)
                        restored = read()
                        if restored != original:
                            raise RuntimeError("Restoration failed; contact RMS owner immediately")
                after = read()
                print(f"Threshold after denied write: {after}")
                if after != original:
                    raise RuntimeError("Threshold changed; contact RMS owner immediately")


if __name__ == "__main__":
    main()
