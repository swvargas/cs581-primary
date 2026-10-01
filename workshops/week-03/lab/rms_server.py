"""Changing RMS process model exposed over loopback-only Modbus TCP."""

from __future__ import annotations

import asyncio
import logging
import math
import random
import time

from pymodbus.constants import ExcCodes
from pymodbus.server import StartAsyncTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

from events import emit

HOST = "127.0.0.1"
PORT = 5061
DEVICE_ID = 1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOG = logging.getLogger("rms-server")


class RadiationProcess:
    def __init__(self) -> None:
        self.started = time.monotonic()
        self.read_count = 0
        self.last_read_event = 0.0
        self.alarm = False
        self.threshold_raw = 250

    def values(self, threshold_raw: int) -> list[int]:
        elapsed = time.monotonic() - self.started
        radiation = max(
            0.01,
            1.35 + 0.55 * math.sin(elapsed / 18) + random.uniform(-0.08, 0.08),
        )
        count_rate = max(0, round(radiation * 118 + random.uniform(-4, 4)))
        temperature = 24.0 + 1.2 * math.sin(elapsed / 75)
        health = max(90, min(100, round(98 - radiation / 8)))
        sample_counter = int(elapsed) % 65536

        new_alarm = round(radiation * 100) > threshold_raw
        if new_alarm != self.alarm:
            self.alarm = new_alarm
            emit(
                "process.alarm",
                "High radiation alarm changed state",
                severity="critical" if new_alarm else "info",
                details={
                    "active": new_alarm,
                    "radiation_uSv_h": round(radiation, 2),
                    "threshold_uSv_h": threshold_raw / 100,
                },
            )

        return [
            round(radiation * 100),
            count_rate,
            round(temperature * 10),
            threshold_raw,
            health,
            sample_counter,
        ]

    def sampled_read(self, function_code: int, address: int, count: int) -> None:
        self.read_count += 1
        now = time.monotonic()
        if now - self.last_read_event >= 600:
            self.last_read_event = now
            emit(
                "protocol.read",
                "Sampled Modbus read",
                details={
                    "protocol": "modbus-tcp",
                    "function_code": function_code,
                    "offset": address,
                    "count": count,
                },
            )

    async def action(
        self,
        function_code: int,
        start_address: int,
        address: int,
        count: int,
        current_registers: list[int],
        set_values: list[int] | list[bool] | None,
    ) -> ExcCodes | None:
        """Refresh reads, constrain writes, and record protocol activity."""
        is_write = set_values is not None
        is_holding = function_code in {3, 6, 16, 22, 23}
        is_coil = function_code in {1, 5, 15}

        if is_holding:
            threshold_index = 3 - start_address
            threshold = (
                int(current_registers[threshold_index])
                if 0 <= threshold_index < len(current_registers)
                else 250
            )
            self.threshold_raw = threshold
            process_values = self.values(threshold)
            for point_address, value in enumerate(process_values):
                index = point_address - start_address
                if 0 <= index < len(current_registers):
                    current_registers[index] = value

        if is_coil:
            # Non-shared bit blocks are packed into 16-bit registers internally.
            self.values(self.threshold_raw)
            alarm_mask = 1 << 1
            current_registers[0] = (
                current_registers[0] | alarm_mask
                if self.alarm
                else current_registers[0] & ~alarm_mask
            )

        if not is_write:
            self.sampled_read(function_code, address, count)
            return None

        permitted = (
            (function_code in {6, 16} and address == 3 and count == 1)
            or (function_code in {5, 15} and address == 0 and count == 1)
        )
        if not permitted:
            return ExcCodes.ILLEGAL_ADDRESS

        if function_code in {6, 16}:
            self.threshold_raw = int(set_values[0])

        emit(
            "protocol.write",
            "Modbus client changed an RMS control point",
            severity="warning",
            details={
                "protocol": "modbus-tcp",
                "function_code": function_code,
                "offset": address,
                "values": list(set_values),
                "detection_opportunity": "T1692.001 Unauthorized Message",
            },
        )
        return None


async def main() -> None:
    process = RadiationProcess()

    # Tuple order: coils, discrete inputs, holding registers, input registers.
    device = SimDevice(
        DEVICE_ID,
        simdata=(
            [
                SimData(0, values=[False], datatype=DataType.BITS),
                SimData(1, values=[False], datatype=DataType.BITS, readonly=True),
            ],
            [SimData(0, values=[False], datatype=DataType.BITS, readonly=True)],
            [
                SimData(0, values=[135, 159, 240], datatype=DataType.REGISTERS,
                        readonly=True),
                SimData(3, values=[250], datatype=DataType.REGISTERS),
                SimData(4, values=[98, 0], datatype=DataType.REGISTERS,
                        readonly=True),
            ],
            [SimData(0, datatype=DataType.INVALID)],
        ),
        action=process.action,
    )

    emit(
        "service.state",
        "RMS Modbus service started",
        details={"state": "active", "bind": f"{HOST}:{PORT}"},
    )
    LOG.info("starting Modbus TCP on %s:%s", HOST, PORT)
    try:
        await StartAsyncTcpServer(context=device, address=(HOST, PORT))
    finally:
        emit(
            "service.state",
            "RMS Modbus service stopped",
            severity="warning",
            details={"state": "inactive"},
        )


if __name__ == "__main__":
    asyncio.run(main())
