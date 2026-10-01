"""Authenticated web HMI for the RMS process."""

from __future__ import annotations

import os
import secrets
from functools import wraps

from flask import Flask, Response, jsonify, render_template, request
from pymodbus.client import ModbusTcpClient

from events import emit

app = Flask(__name__)


def _authorized() -> bool:
    supplied = request.authorization
    username = os.getenv("RMS_HMI_USERNAME", "operator")
    password = os.getenv("RMS_HMI_PASSWORD", "")
    return bool(
        supplied
        and password
        and secrets.compare_digest(supplied.username or "", username)
        and secrets.compare_digest(supplied.password or "", password)
    )


def basic_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        remote = request.headers.get("X-Forwarded-For", request.remote_addr)
        if not _authorized():
            emit("auth.failure", "RMS HMI authentication failed", severity="warning",
                 details={"remote_address": remote, "path": request.path})
            return Response(
                "Authentication required\n",
                401,
                {"WWW-Authenticate": 'Basic realm="RMS HMI"'},
            )
        emit("auth.success", "RMS HMI authentication succeeded",
             details={"remote_address": remote, "path": request.path})
        return view(*args, **kwargs)

    return wrapped


def read_process() -> dict[str, object]:
    client = ModbusTcpClient("127.0.0.1", port=5061, timeout=2)
    try:
        if not client.connect():
            raise ConnectionError("Modbus connection failed")
        registers = client.read_holding_registers(address=0, count=6, device_id=1)
        coils = client.read_coils(address=0, count=2, device_id=1)
        if registers.isError() or coils.isError():
            raise RuntimeError(f"Modbus error: {registers!s}; {coils!s}")
        values = registers.registers
        return {
            "area_radiation": values[0] / 100,
            "count_rate": values[1],
            "detector_temperature": values[2] / 10,
            "alarm_threshold": values[3] / 100,
            "detector_health": values[4],
            "sample_counter": values[5],
            "alarm_acknowledge": bool(coils.bits[0]),
            "high_radiation_alarm": bool(coils.bits[1]),
        }
    finally:
        client.close()


@app.get("/")
@basic_auth
def index():
    return render_template("index.html")


@app.get("/api/status")
@basic_auth
def status():
    try:
        return jsonify({"ok": True, "process": read_process()})
    except (ConnectionError, RuntimeError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


emit("service.state", "RMS HMI worker started", details={"state": "active"})
