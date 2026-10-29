# Operator Runbook — Emergency Diesel Generator Controller
## CS 581 | Original author: Sindi Banda | Incoming owner: Santiago Vargas | Updated: 2026-10-29 UTC

This document is written for a person who has never seen this system. After W4 the system
changes hands. The person taking it over for W5 uses this to bring it up, understand what every
point means, and know what to look for.

---

## System identity

| | |
|---|---|
| System | Emergency Diesel Generator Controller (EDGC) |
| Role account | `edgc` |
| Hostname | `edgc.plant.sanctumsec.com` |
| Purdue level | Level 1, Basic Control |
| Protocol | Modbus TCP, device id 1 |
| Port block | 5010 to 5019 |
| HMI URL | `https://edgc.plant.sanctumsec.com` (gunicorn backend on `127.0.0.1:5010`) |

The Modbus service binds `127.0.0.1:5011`. It is not reachable from off-host by design. The HMI
is the only externally presented interface, and it is read-only.

---

## Starting the system

Log in as the role account and inspect the existing services first. Both services were already
active at the October 28 incoming-owner check; no restart was needed. Only link/start units when
an approved maintenance action requires it, after preserving evidence and posting advance notice
in the handover thread. The following is an installation/start procedure, not a routine health check:

```bash
ssh edgc@plant.sanctumsec.com
mkdir -p ~/.config/systemd/user
cp ~/lab/units/*.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now plant-edgc plant-edgc-hmi
```

`plant-edgc` runs the Modbus server (`edgc_server.py`). `plant-edgc-hmi` runs the HMI
(`gunicorn -w 2 -b 127.0.0.1:5010 hmi.app:app`). Lingering is enabled on the account, so both
services survive logout and reboot. The venv at `~/lab/.venv` must exist; if it does not, create
it with `python3 -m venv ~/lab/.venv && ~/lab/.venv/bin/pip install pymodbus flask gunicorn`.

**How to confirm it started:**

```bash
systemctl --user status plant-edgc plant-edgc-hmi --no-pager
ss -ltnp | grep -E '5010|5011'
~/lab/.venv/bin/python - <<'PY'
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient("127.0.0.1", port=5011, timeout=3); c.connect()
r = c.read_holding_registers(0, count=7, device_id=1)
print("registers:", None if r.isError() else r.registers); c.close()
PY
```

Both services should report `active (running)`. `ss` should show listeners on `127.0.0.1:5010`
and `127.0.0.1:5011`, loopback only. The read should return seven values. If the listeners show
`0.0.0.0` instead of `127.0.0.1`, stop and fix the bind, because that exposes the unauthenticated
protocol service on every interface.

---

## Stopping the system

```bash
systemctl --user stop plant-edgc-hmi plant-edgc
systemctl --user is-active plant-edgc
```

`is-active` should print `inactive`. Note one behavior that matters for monitoring: a stop sends
SIGTERM, and the server emits a `service.state` stop event only on SIGINT (`KeyboardInterrupt`).
A normal `systemctl` stop therefore produces no stop event in the OT-SIEM. Record stops manually.

To disable autostart as well, add `systemctl --user disable plant-edgc plant-edgc-hmi`.

---

## Point map

Seven holding registers and one coil. Read holding registers with function code 3, read the coil
with function code 1, write the coil with function code 5. All values are unsigned 16-bit
integers. Three values are scaled by 10, and the scale factor exists only in this table and in
`points.md`, not on the wire.

| Address | Type | Name | Normal range | Out-of-range means |
|---|---|---|---|---|
| HR 0 (40001) | holding, R | engine_running_status | 0 or 1 | Set to 1 at or above 1440 rpm, 0 below. Any other value is corruption. A 1 while rpm reads near 0 means the status was written directly, not derived. |
| HR 1 (40002) | holding, R | engine_rpm | 0 to 1800 | Rated speed is 1800. Above 1800, or a value that does not track oil pressure and frequency, indicates tampering or a stuck value. |
| HR 2 (40003) | holding, R | oil_pressure, psi x10 | 0 to 550 raw (0.0 to 55.0 psi), about 500 at rated speed | Nonzero oil pressure with rpm near 0 is physically impossible in the model and signals an injected value. |
| HR 3 (40004) | holding, R | generator_voltage, V | 0 to 4160 | Should be 0 below about 1200 rpm. Voltage present at low rpm means the value was written, not generated. |
| HR 4 (40005) | holding, R | generator_frequency, Hz x10 | 0 to 630 raw (0.0 to 63.0 Hz), about 600 (60.0 Hz) at rated speed | Frequency that does not scale with rpm indicates an inconsistent or injected reading. |
| HR 5 (40006) | holding, R | engine_coolant_temperature, degC x10 | 0 to 1200 raw (0.0 to 120.0 degC), about 850 (85.0) when running, near 200 (20.0) ambient when stopped | Slowest-moving value. A sudden jump, or a reading of 0 at startup, is suspect. |
| HR 6 (40007) | holding, R | fuel_level, percent | 0 to 100 | Falls only while running, never refills on its own. Below 20 triggers the low-fuel alarm. A value rising without a restart means it was written. |
| Coil 0 (00001) | coil, R/W | start_stop_command | 0 or 1 | 1 commands start, 0 commands stop. This is the only intended writable point; W4 confirmed a holding-register write was also accepted. |

Source: `workshops/week-03/points.md`. If that file and this table disagree, this table is wrong,
fix it against `points.md`.

---

## What normal looks like

The HMI polls the Modbus server with FC3, reading all seven holding registers starting at
address 0, device id 1. The HMI page refreshes every 5 seconds, so in steady state you see one
FC3 read roughly every 5 seconds from a loopback client. A read request is 12 bytes on the wire,
and a full seven-register response is larger. Writes (FC5 to coil 0) are rare and tied to a
start or stop action, so a steady stream of reads with no writes is normal.

The values are coupled, not independent, and that coupling is how you tell normal from tampered:

- Stopped: rpm 0, oil pressure 0, voltage 0, frequency 0, coolant drifting toward 200 (20.0 degC),
  running status 0, fuel steady.
- Starting: rpm approaches 1800 exponentially, with a 0.10 update fraction per nominal one-second
  tick. From rest, the running-status threshold of 1440 rpm takes about 16 updates; near-rated
  speed takes longer. Oil pressure follows, voltage appears above 1200 rpm, and frequency tracks rpm.
- Running: rpm near 1800, oil pressure near 500, voltage near 4160, frequency near 600, coolant
  near 850 (85.0 degC), running status 1, fuel slowly falling.
- Stopping: rpm approaches zero exponentially, with a 0.067 update fraction per nominal
  one-second tick, and clamps to zero below 5 rpm. From rated speed this takes about 85 updates,
  not a fixed fifteen-second stop. These are source-model estimates, not live acceptance timings.

Small jitter on oil pressure, voltage, frequency, and coolant is expected while running. Changes
between reads support activity, but identical reads alone do not prove the loop stopped: stopped,
rounded or clamped values may legitimately remain unchanged. Corroborate persistent staleness with
services, source behavior and other evidence. An inconsistent value is grounds for investigation,
not by itself proof of a writer or cause.

### Fuel, Liveness And Readiness Limits

The observed source selects target rpm from `start_stop_command` without a fuel-exhaustion
shutdown. Fuel clamps at zero while the generator can continue reporting running. The low-fuel
alarm is emitted on transition below 20%, not on every subsequent zero-fuel read. Current fuel
zero does not prove that an alarm was delivered, or that real standby power is available.
Do not refill a register or restart merely to make the display look normal.

HR0 `engine_running_status=1` means rpm is at least 1440. It is not an all-equipment-ready
indication. The unauthenticated HMI `/healthz` route returns `{"ok": true}` without checking
Modbus, fuel, peer communications or functional readiness. Keep process liveness, consistency,
and credited safety-function availability separate.

SIEM incident 116181 (October 22, 04:45 UTC) names `egen_status`; that point name is absent from
the observed source/point map. Mapping it to HR0, identifying the underlying fault and establishing
first recognition time remain questions for Sindi/instructor. Current reads are not proof of
historical fault recovery. An October 22 04:35-04:55 UTC user-journal query returned no entries;
that absence does not refute the SIEM event.

---

## Known peer connections

| Peer system | Direction | Protocol / port | Notes |
|---|---|---|---|
| DCS | Bidirectional | Modbus, per the architecture diagram | Architecture peer named in the W3 brief. This is the documented plant link for EDGC. |
| PSI, workstation-originated exercise | Workstation -> PSI, not EDGC -> PSI | SSH local forward on workstation port 15081 to PSI port 5081 | October 21 handover describes the completed read-only Attack C; not a standing EDGC consumer. |
| PSI, optional October 22 test | EDGC -> PSI | Temporary SSH local forward `127.0.0.1:15081` -> PSI port 5081, using a forwarded workstation agent | Later change log records FC3 result `[3]`, closure at 18:26:27 and no EDGC-held private key. PSI key status afterward was not re-verified. No listener on EDGC port 15081 at the October 28 check. |
| OT-SIEM | Outbound from EDGC and HMI | HTTP POST, event API | Telemetry only. See the next section. |

A connection through an SSH forward reaches its destination Modbus service from loopback and
does not carry a verified human identity in Modbus. Loopback is not an account boundary on this
shared host. Historical forwarding tests do not prove an always-on link or campaign attribution.

## Incoming-Owner Baseline And Access

On October 28 at 21:29:42/44/46 UTC, read-only FC3 HR0-6 and FC1 coil-0 requests succeeded.
Status/rpm were `1/1799`, oil raw `498/499/502`, voltage `4152/4154/4160`, frequency raw `599`,
coolant raw `849`, fuel `0`, and coil 0 true. Both units were active with PIDs `233434/233440`,
`NRestarts=0`, and reported start October 1 at 03:47:46 MDT; listeners were loopback 5011/5010.
This is a dated simulation baseline, not proof of physical operability or historical restoration.

After the user confirmed posting the incoming-owner reply and advance notice, a fresh connection
using Santiago's explicitly selected key succeeded before the announced handover revocation.
On October 29 at 04:37:54 UTC, only `edgc:bandsind` was removed. A separate fresh login succeeded
at 04:38:03 UTC afterward; the authorized-key inventory now contains only `edgc:swvargas`,
fingerprint `SHA256:nFwZvzHOR2Nnqo/KsEs+UmirDcWo2X7yYLTX/ahWZCg`. The file remains mode 600.
A mode-600 pre-change public-key inventory is preserved at
`~/.ssh/authorized_keys.before-handoff-20261029T043754Z`; it is not an active authorization file.
Both services remained active. This change does not revoke credentials on PSI or identify who
used any credential during the incident.

---

## SIEM and monitoring

Both the server and the HMI post events to the OT-SIEM. The server emits `service.state`,
`protocol.read`, `protocol.write`, and `process.alarm`. The HMI emits `auth.success` and
`auth.failure`. Delivery depends on the `SIEM_TOKEN` environment variable: if it is unset, the
`emit()` function returns without sending, and any transmission error is discarded silently.

**Known monitoring gaps, all confirmed in the W3 source:**

- `protocol.read` fires on the process loop counter roughly every 15 minutes, not on each client
  read. The event stream does not show who read what or how often.
- `protocol.write` is inferred by comparing the coil value between one-second samples, and the
  function code in the event is a constant. A write reverted within one second, or a repeated
  write of the same value, is not recorded.
- A SIGTERM stop emits no `service.state` event. Only a SIGINT does.
- Authentication events cover HMI route `/` only. Route `/healthz` has no authentication and emits
  nothing.
- Events are self-asserted. The SIEM receives what the application reports and cannot confirm the
  reported action occurred. Absence of an event is not evidence that nothing happened.
- The server posts to `http://127.0.0.1:5090` and the HMI posts to the course SIEM hostname over
  HTTPS. Confirm which endpoint actually ingests before trusting either event stream.

The practical consequence for an operator: the HMI and a packet capture on `lo` are more reliable
than the event log for knowing the current state.

---

## Known weaknesses from W4

Status after W4 testing. Attacks A, B, and C were completed and are documented in
`adversary-test.md`, with evidence in `workshops/week-04/findings/`. The optional EDGC-to-PSI test
was completed read-only on 2026-10-22.

1. **Attack A, Insider: completed.** An FC6 write to holding register 6 (`fuel_level`), documented
   read-only, was accepted by the service. The read-back showed the written value, and the process
   loop restored the original value on the next tick. This confirms the R marking is documentation,
   not an enforced control. Watch for coil-0 changes and for register values that break the normal
   coupling.

2. **Attack B, Supply chain: completed as an isolated simulation.** A modified EDGC instance on a
   separate port reported a false fuel value, and a temporary HMI displayed it with no validation.
   The production services were not touched. Nothing in the build verifies a signature on code or
   dependencies. Watch for changes to `edgc_server.py`, the unit files, or the venv contents.

3. **Attack C, pivot: completed as a read-only test.** A read-only FC3 request succeeded from my
   Ubuntu workstation to PSI over an SSH local forward (local port 15081 to PSI port 5081). This
   was a workstation-to-PSI connection, not an EDGC-to-PSI pivot. The forwarded connection reaches
   a loopback-bound Modbus service from `127.0.0.1`, so a loopback bind does not distinguish it from
   a local client, and no event marks it as remote. Watch for Modbus traffic on the service when no
   local client should be active.

4. **Optional EDGC-to-PSI test: completed read-only, 2026-10-22.** A pivot originating on the EDGC
   host was run as a read-only test. EDGC holds no private key of its own, so the connection
   authenticated with my workstation key through SSH agent forwarding (`ssh -A`). From EDGC
   (`ip-172-26-0-239`) an SSH local forward on `127.0.0.1:15081` reached PSI's Modbus service on
   port 5081, and one FC3 read of register 0, device id 1, returned `[3]` (`Connected: True`,
   `isError: False`). No writes were made. The forward was closed and the listener verified closed
   at 18:26:27. The access depended on a forwarded workstation credential, not an EDGC-held key, so
   reachability is governed at the SSH layer, including forwarded agents, not by the loopback bind.
   Write-up in `adversary-test.md`, evidence in `findings/attack-c/`.

## What to do if something looks wrong

This is a first-move guide, not a full incident response plan. That is W5.

1. **Observe before acting.** Read the seven registers and the coil, and note whether the values
   are internally consistent per the coupling in "What normal looks like." Do not write anything
   yet.
2. **Capture what you can with this account.** A loopback packet capture (`tcpdump -i lo`) is the
   strongest record, but it requires root and the `edgc` account has no sudo, so it cannot run
   under this account's current permissions. Packet capture here needs approved elevated privileges
   that this account does not hold. If those are granted, capture `tcp port 5011` to
   `~/incident-$(date +%Y%m%d-%H%M).pcap`. Without them, use the read-only alternatives available to
   this account: record the PyModbus client responses (the response object and register values from
   each read) and pull the existing user-service logs with
   `journalctl --user -u plant-edgc -u plant-edgc-hmi --since "-15 min" --no-pager`. These show what
   the application reported, not the raw frames, so they are weaker evidence than a capture and are
   not equivalent to one. Modbus carries no client identity, so neither source attributes an action
   to a person.
3. **Check the services.** `systemctl --user status plant-edgc plant-edgc-hmi --no-pager` and
   `journalctl --user -u plant-edgc -n 50 --no-pager`. A restart loop shows as a short uptime that
   keeps resetting.
4. **Check access.** `cat ~/.ssh/authorized_keys` and confirm only expected keys are present.
   Remove any leftover exercise key. `ss -ltnp | grep 5011` should show loopback only.
5. **Do not trust the absence of a SIEM event.** Given the gaps above, a quiet event log does not
   mean nothing happened. Use the response and log records and the live register values instead.
6. **Escalate.** Contact the Cybersecurity Manager and the Control Room Supervisor. Preserve the
   evidence files and your notes. Do not stop or restart the service unless instructed, because a
   restart resets the simulation state and destroys the live evidence.

If a register value is clearly wrong but the engine state it depends on is normal, the likely cause
is a direct write to that register, which the process loop overwrites within about a second. Note
the time and the value before it is overwritten, because the event log will not capture it.

---

## Change log

This log records changes relevant to the RUNBOOK. Each entry is marked as a documentation edit to
this file or a host action such as installation, a key change, or a test. The documentation edits below changed no host configuration,
service, or key.

- **2026-10-21, Sindi Banda, runbook installed.** Installed RUNBOOK.md at /home/edgc/RUNBOOK.md.
  Verified that the file exists and is owned by edgc. No service or SSH configuration changes were
  made during installation.

- **2026-10-21, Sindi Banda, documentation.** Corrected the incident-response capture step: the `edgc` account has
  no sudo, so the `sudo tcpdump` instruction cannot run under its permissions; replaced it with the
  permission limitation and read-only alternatives (PyModbus responses and user-service logs).
  Updated "Known weaknesses from W4" to the verified results of Attacks A, B, and C, and marked the
  optional EDGC-to-PSI test as not completed. Source: `adversary-test.md` and `findings/`.

- **2026-10-21, Sindi Banda, host change.** Removed the W4 partner public key
  (`tiffanyfuhrmann@u.boisestate.edu`) from EDGC `~/.ssh/authorized_keys` after the partner
  exercise ended. Verified with `ssh-keygen -lf ~/.ssh/authorized_keys`, which lists only
  `edgc:bandsind` (ED25519) remaining. Recorded in the W4-to-W5 handover post.

- **2026-10-22, Sindi Banda, host change.** Ran the optional EDGC-originated read-only test to PSI,
  announced in the handover thread beforehand. Opened a temporary SSH local forward from EDGC
  (`127.0.0.1:15081`) to PSI's Modbus service on port 5081, authenticated with my workstation key
  through SSH agent forwarding (`ssh -A`); no private key was placed on EDGC. Ran one Modbus FC3
  read of register 0, device id 1, which returned `[3]`. No writes or service changes were made.
  Closed the forward and verified the listener closed at 18:26:27. No new key was installed on PSI.
  The prior authorized key's current status on PSI is not re-verified here, and no revocation is
  claimed. Evidence in `workshops/week-04/findings/attack-c/`.

- **2026-10-22, Sindi Banda, documentation.** Updated "Known weaknesses from W4" item 4 from "not
  completed" to completed, recording the EDGC-originated read-only result `[3]` and the SSH
  agent-forwarding authentication method. The workstation-originated Attack C result in item 3 is
   unchanged. Source: `adversary-test.md` and `findings/attack-c/`.

- **2026-10-29 04:37:54 UTC, Santiago Vargas with OpenCode assistance, host key change.** After
  Santiago confirmed the incoming-owner/advance-change reply was posted in Canvas, verified a
  separate fresh login with his explicit key and fingerprint. Removed only `edgc:bandsind`,
  preserved the restricted pre-change public-key inventory, and retained `edgc:swvargas` at mode
  600. A separate fresh login at 04:38:03 UTC succeeded; both services were still active. No
  service restart, process write, certificate or network change was performed.

- **2026-10-29, Santiago Vargas with OpenCode assistance, documentation.** Applied the announced
  runbook corrections: zero-fuel model behavior, running-bit and `/healthz` limitations, qualified
  staleness/ramp guidance, intended versus enforced write access, actual PSI test directions, dated
  incoming baseline and current key inventory. Preserved Sindi's historical entries and left
  `egen_status` mapping, underlying incident fault/recognition and PSI key lifecycle unresolved.
  Repository evidence preserves the inherited runbook separately as `RUNBOOK-inherited-20261028.md`.
