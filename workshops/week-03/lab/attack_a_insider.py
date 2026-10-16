"""Authorized RMS simulation: compare in-band and policy-prohibited writes."""

import argparse
from datetime import datetime, timezone
import os
import pwd

from pymodbus.client import ModbusTcpClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true",
                        help="Perform temporary writes 300 and 301; otherwise read only")
    args = parser.parse_args()

    def record(message):
        print(f"{datetime.now(timezone.utc).isoformat()} {message}", flush=True)

    record(f"Account: {pwd.getpwuid(os.geteuid()).pw_name}")
    record("Endpoint: 127.0.0.1:5061; device=1; holding offset=3; FC3/FC6")
    client = ModbusTcpClient("127.0.0.1", port=5061, timeout=3, retries=0)

    def read():
        response = client.read_holding_registers(address=3, count=1, device_id=1)
        if response.isError():
            raise RuntimeError(f"Read failed: {response}")
        return response.registers[0]

    try:
        if not client.connect():
            raise ConnectionError("RMS backend unavailable")
        original = read()
        record(f"Original: {original}")
        if not args.execute:
            record("Read-only preflight; no writes performed")
            return
        if original != 250:
            raise RuntimeError("Expected baseline 250; stopping without writes")

        for label, value in (("in_band_comparison", 300), ("out_of_band_test", 301)):
            if read() != original:
                raise RuntimeError("Baseline changed; stopping before next test")
            record(f"{label}: attempt={value}; documented routine band=200-300")
            try:
                response = client.write_register(address=3, value=value, device_id=1)
                record(f"{label}: FC6 response={response}")
                if response.isError():
                    raise RuntimeError(f"{label}: write blocked; inspect evidence")
                observed = read()
                record(f"{label}: readback={observed}")
                if observed != value:
                    raise RuntimeError(f"{label}: expected readback {value}")
            finally:
                # Restore even if the response/readback fails after a write attempt.
                response = client.write_register(address=3, value=original, device_id=1)
                record(f"{label}: restore FC6 response={response}")
                restored = read()
                record(f"{label}: restored readback={restored}")
                if response.isError() or restored != original:
                    raise RuntimeError("RESTORATION FAILED; notify RMS owner immediately")
        record("Completed; final threshold=250")
    finally:
        client.close()


if __name__ == "__main__":
    main()
