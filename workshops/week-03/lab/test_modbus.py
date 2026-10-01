"""End-to-end check for the RMS Modbus service."""

import time

from pymodbus.client import ModbusTcpClient


def main() -> None:
    client = ModbusTcpClient("127.0.0.1", port=5061, timeout=3)
    try:
        assert client.connect(), "could not connect to 127.0.0.1:5061"

        first = client.read_holding_registers(address=0, count=6, device_id=1)
        assert not first.isError(), f"first read failed: {first}"
        print("first: ", first.registers)

        print("waiting 30 seconds...")
        time.sleep(30)

        second = client.read_holding_registers(address=0, count=6, device_id=1)
        assert not second.isError(), f"second read failed: {second}"
        print("second:", second.registers)
        assert first.registers != second.registers, "process values did not change"

        threshold = client.write_register(address=3, value=25, device_id=1)
        assert not threshold.isError(), f"threshold write failed: {threshold}"

        acknowledge = client.write_coil(address=0, value=True, device_id=1)
        assert not acknowledge.isError(), f"acknowledge write failed: {acknowledge}"

        coils = client.read_coils(address=0, count=2, device_id=1)
        assert not coils.isError(), f"coil read failed: {coils}"
        print("coils: ", coils.bits[:2])

        restored = client.write_register(address=3, value=250, device_id=1)
        assert not restored.isError(), f"threshold restore failed: {restored}"
        cleared = client.write_coil(address=0, value=False, device_id=1)
        assert not cleared.isError(), f"acknowledgement reset failed: {cleared}"
        print("PASS: Modbus reads, changing values, and writes work")
    finally:
        client.close()


if __name__ == "__main__":
    main()
