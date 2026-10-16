"""Authorized RMS dependency-tampering test on isolated loopback port 5063."""

import argparse
from datetime import datetime, timezone
import hashlib
import logging
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time

from pymodbus.client import ModbusTcpClient


def staged_dependency(original: str, marker: str) -> str:
    """Append a scoped malicious wrapper to a copy of the trusted event library."""
    return original + f'''

_original_emit = emit

def emit(event_type, message, *, severity="info", details=None):
    if event_type == "service.state" and details and details.get("state") == "active":
        details = dict(details)
        details["state"] = "inactive"
        details["w4_test"] = {marker!r}
        message = "W4B TEST " + {marker!r} + ": reported_state=inactive (injected dependency)"
        severity = "warning"
    return _original_emit(event_type, message, severity=severity, details=details)
'''


def threshold(port: int) -> int:
    client = ModbusTcpClient("127.0.0.1", port=port, timeout=1, retries=0)
    try:
        if not client.connect():
            raise ConnectionError(f"No RMS listener on port {port}")
        response = client.read_holding_registers(address=3, count=1, device_id=1)
        if response.isError():
            raise RuntimeError(f"RMS read failed on port {port}: {response}")
        return response.registers[0]
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true",
                        help="Run the staged RMS and send explicitly marked test telemetry")
    args = parser.parse_args()
    lab = Path(__file__).resolve().parent
    paths = [lab / "events.py", lab / "rms_server.py"]
    sources = [path.read_bytes() for path in paths]

    def record(message):
        print(f"{datetime.now(timezone.utc).isoformat()} {message}", flush=True)

    original = threshold(5061)
    record(f"Primary RMS threshold before: {original}")
    for path, source in zip(paths, sources):
        record(f"Original {path.name} SHA256: {hashlib.sha256(source).hexdigest()}")
    if not args.execute:
        record("Read-only preflight; no dependency changes or test events")
        return
    if original != 250:
        raise RuntimeError("Expected primary threshold 250; stopping")
    with socket.socket() as guard:
        guard.bind(("127.0.0.1", 5063))

    marker = "RMS-W4B-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record(f"Marker: {marker}")
    logging.basicConfig(level=logging.INFO)
    try:
        with tempfile.TemporaryDirectory(prefix="w4-b-", dir=lab) as directory:
            stage = Path(directory)
            dependency = staged_dependency(sources[0].decode(), marker).encode()
            (stage / "events.py").write_bytes(dependency)
            (stage / "rms_server.py").write_bytes(sources[1])
            record(f"Staged dependency SHA256: {hashlib.sha256(dependency).hexdigest()}")
            record("Staged RMS source unchanged; only events.py differs; test port=5063")
            child_code = (
                "import asyncio, events, rms_server\n"
                "rms_server.PORT = 5063\n"
                "try:\n"
                "    asyncio.run(rms_server.main())\n"
                "except KeyboardInterrupt:\n"
                "    pass\n"
                "finally:\n"
                "    events._EVENTS.join()\n"
            )
            with tempfile.TemporaryFile(mode="w+t") as output:
                process = subprocess.Popen(
                    [sys.executable, "-B", "-c", child_code], cwd=stage,
                    stdout=output, stderr=subprocess.STDOUT,
                )
                try:
                    deadline = time.monotonic() + 10
                    while True:
                        if process.poll() is not None:
                            raise RuntimeError("Staged RMS exited before readiness")
                        try:
                            with socket.create_connection(("127.0.0.1", 5063), timeout=0.2):
                                break
                        except OSError:
                            if time.monotonic() >= deadline:
                                raise TimeoutError("Staged RMS did not start")
                            time.sleep(0.1)
                    observed = threshold(5063)
                    record(f"Actual staged RMS reachable: threshold={observed}; reported state is inactive")
                    if observed != 250:
                        raise RuntimeError("Unexpected staged threshold")
                    time.sleep(2)  # Allow the existing telemetry worker to finish delivery.
                finally:
                    if process.poll() is None:
                        process.send_signal(signal.SIGINT)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                    output.seek(0)
                    print("--- staged RMS output ---", flush=True)
                    print(output.read(), flush=True)
                    print("--- end staged RMS output ---", flush=True)
            record("Staged RMS stopped; temporary dependency removed on context exit")
    finally:
        for path, before in zip(paths, sources):
            if path.read_bytes() != before:
                raise RuntimeError(f"Primary {path.name} changed; investigate")
        final = threshold(5061)
        record(f"Primary files unchanged; final primary threshold: {final}")
        if final != original:
            raise RuntimeError("Primary threshold changed unexpectedly; investigate")

    # A clearly marked corrective record closes the telemetry test; it is not a
    # process write, and imports the untouched primary events.py in this process.
    import events
    events.emit(
        "service.state", f"W4B TEST {marker}: complete; primary RMS active; staged dependency removed",
        details={"state": "active", "w4_test": marker, "threshold_raw": final},
    )
    events._EVENTS.join()
    record("Completed; confirm injected and corrective records on the connected SIEM")


if __name__ == "__main__":
    main()
