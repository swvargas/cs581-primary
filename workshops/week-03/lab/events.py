"""Small, failure-tolerant client for the course OT-SIEM event API."""

from __future__ import annotations

import atexit
import logging
import os
import queue
import threading
from datetime import datetime, timezone
from typing import Any

import requests

LOG = logging.getLogger(__name__)
_EVENTS: queue.Queue[dict[str, Any] | None] = queue.Queue(maxsize=256)
_STARTED = False
_LOCK = threading.Lock()


def _worker() -> None:
    url = os.getenv("OT_SIEM_URL", "").strip()
    token = os.getenv("OT_SIEM_TOKEN", "").strip()
    if not url or not token:
        LOG.warning("OT-SIEM is not configured; events will only be logged locally")

    session = requests.Session()
    while True:
        event = _EVENTS.get()
        if event is None:
            _EVENTS.task_done()
            return
        try:
            LOG.info("event=%s", event)
            if url and token:
                response = session.post(
                    url,
                    json=event,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=3,
                )
                if not response.ok:
                    LOG.warning(
                        "OT-SIEM rejected event: status=%s body=%s",
                        response.status_code,
                        response.text[:1000],
                    )
                response.raise_for_status()
                LOG.info("OT-SIEM accepted %s: %s", event["event_type"], response.text)
        except requests.RequestException as exc:
            LOG.warning("OT-SIEM delivery failed: %s", exc)
        finally:
            _EVENTS.task_done()


def _ensure_worker() -> None:
    global _STARTED
    with _LOCK:
        if not _STARTED:
            threading.Thread(target=_worker, name="ot-siem", daemon=True).start()
            _STARTED = True


def emit(
    event_type: str,
    message: str,
    *,
    severity: str = "info",
    details: dict[str, Any] | None = None,
) -> None:
    """Queue an event without allowing a SIEM outage to stop the RMS."""
    _ensure_worker()
    severity_map = {
        "info": "low",
        "warning": "medium",
        "critical": "high",
    }
    event = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "system": "RMS",
        "purdue_level": 2,
        "event_type": event_type,
        "severity": severity_map.get(severity, severity),
        "source": {"ip": "127.0.0.1", "port": None, "identity": None},
        "message": message,
        "detail": details or {},
    }
    try:
        _EVENTS.put_nowait(event)
    except queue.Full:
        LOG.warning("OT-SIEM queue full; dropped %s", event_type)


@atexit.register
def _shutdown() -> None:
    if _STARTED:
        try:
            _EVENTS.put_nowait(None)
        except queue.Full:
            pass
