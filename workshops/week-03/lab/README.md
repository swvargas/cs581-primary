# lab/ — your RMS build

Clone or develop here, then link the units:

    mkdir -p ~/.config/systemd/user
    cp units/*.service ~/.config/systemd/user/
    systemctl --user daemon-reload
    systemctl --user enable --now plant-rms plant-rms-hmi plant-rms-relay
    systemctl --user status plant-rms plant-rms-hmi plant-rms-relay

Lingering is already enabled on your account, so your services survive logout and reboot.
The status board checks that they come back.

Python 3.12 with PEP 668 enforced, so use a venv:

    python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt

## Read-only Modbus gateway

`rms_relay.py` now replaces the old transparent relay in place. The existing
`plant-rms-relay.service` name is retained; do not run a second relay. The gateway
listens on `127.0.0.1:5062` and uses RMS at `127.0.0.1:5061` as its backend.
It carries Modbus TCP frames inside mutually authenticated TLS, not HTTP/JSON,
and uses Python's standard library. Plain TCP clients cannot use port 5062 anymore.
Follow [TLS_SETUP.md](TLS_SETUP.md) to issue certificates, configure the required
environment variables, and enroll your partner before restarting the service.

Only device ID 1 and these reads are allowed:

- Function 3: holding-register offsets 0 through 5, within that block.
- Function 1: coil offsets 0 through 1, within that block.

Every write and other function is rejected with Modbus exception 1 (Illegal
Function), without forwarding it. Invalid read ranges/devices receive exception 2;
invalid read quantities or PDU sizes receive exception 3. Malformed MBAP headers,
truncated requests, backend failures, and timeouts close the connection. Complete
frames are validated even when TCP fragments or combines requests. Decisions go
to the service journal; the gateway does not emit its own SIEM events.

Access requires a CA-verified client certificate whose SHA-256 fingerprint is
explicitly allowed by `RMS_GATEWAY_CLIENT_SHA256`. Approved certificates receive
only `partner_read`, with certificate identity in read/write decision logs. This
does not implement all seven policy roles. Local peer accounts may still bypass
it through port 5061 unless the host administrator implements backend isolation.

### Replace the deployed relay

Deploy the updated `rms_relay.py` and unit into the `rms` account's `~/lab` tree
using your repository workflow. Complete the certificate setup first; without it
the service fails closed. Then run from `~/lab` on the plant host:

```bash
cp units/plant-rms-relay.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user restart plant-rms-relay
systemctl --user status plant-rms-relay
journalctl --user -u plant-rms-relay -n 20 --no-pager
```

Confirm the startup log says `read-only Modbus gateway` and `mutual_tls=required`,
not the old forwarding message. A stale deployed file or unrestarted process can
still accept writes.

### Verification

Local isolated tests (no plant connection), from the repository root:

```bash
nix develop --command bash scripts/test.sh workshops/week-03/lab test_rms_gateway.py
```

The root flake provides Python 3.12, Flask, Gunicorn, Pymodbus, Requests, OpenSSL,
and Bash. The generic runner accepts any unittest discovery directory and an
optional filename pattern (default `test_*.py`). It does not run standalone
integration scripts' `main()` functions. Pin dependencies with `flake.lock`;
the Nix package versions may differ from the pip deployment pins in `requirements.txt`.
Pymodbus's upstream package checks are disabled to avoid a failing test-only
Twisted/AnyIO dependency chain; this does not disable the repository's tests.

For a coordinated live test, use the certificate-enabled client in `TLS_SETUP.md`,
port 5062 and device 1:
read offset 3 with function 3, record the original (expected 250), attempt function
6 with value 300, and expect exception `0x86 / 0x01`. Read again and verify the
original is unchanged. Keep the client output and gateway denial log. Arrange
restoration with the RMS owner in case an old deployment unexpectedly allows the
write; the new gateway intentionally denies restoration writes too.

Separately test access to port 5061 from the partner account. If it is reachable,
report the bypass gap rather than claiming the entire RMS is protected. Do not use
`test_modbus.py` for read-only verification: it targets the backend and changes state.

Check the gateway and follow its logs with:

    ss -ltn | grep 5062
    journalctl --user -u plant-rms-relay -f
