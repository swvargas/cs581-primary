# Operator Runbook - Radiation Monitoring System (RMS)

CS 581 | Santiago Vargas | Handoff baseline: October 15, 2026

This is the authorized course simulation, not a calibrated detector or a production
plant procedure. Its readings and policy bands are not physical safety limits.
This document combines source review, dated W4 attack evidence, and October 15
read-only checks. All three units were active, a backend FC3 read confirmed threshold
250, unauthenticated HMI access returned 401, and an authenticated browser showed
ONLINE. See [collection evidence](session-log.md#october-15-collection). No service
operation or new attack was performed on October 15. Maintenance commands below
are instructions for an authorized successor, not claims of executed operations.

## Identity and Authority

| Item | Value |
|---|---|
| System / logical zone | Radiation Monitoring System, Purdue Level 2 |
| Plant host / shared role account | `plant.sanctumsec.com` / `rms` |
| Public HMI | `https://rms.plant.sanctumsec.com/` |
| Allocation | TCP ports 5060-5069; only 5060-5062 have services defined here |
| HMI backend | Gunicorn, two workers, HTTP at `127.0.0.1:5060`; lab routing supplies public HTTPS |
| Process backend | Unauthenticated Modbus TCP, `127.0.0.1:5061`, device ID 1 |
| Peer gateway | Modbus TCP frames inside mutual TLS, `127.0.0.1:5062`, device ID 1; not HTTP or plaintext Modbus |
| Deployment directory | `~/lab` in the `rms` account, not this repository's workshop directory |
| Configuration | `~/lab/.env`, required by all three user units |
| Services | `plant-rms.service`, `plant-rms-hmi.service`, `plant-rms-relay.service` |
| Evidence | User-service journals; source events posted to the configured OT-SIEM API |

Follow [rbac-policy.md](rbac-policy.md). Operators view status and report anomalies;
they do not stop services or change thresholds. Maintenance needs a recorded
supervisor-approved window. Security tests need explicit scope and authorization.
The seven policy roles are responsibilities, not seven implemented application or
Linux roles. SSH keys admit people to the same `rms` account. No sudo privilege is
assumed. Loopback binding does not isolate other accounts on the shared host.

Normal threshold is raw **250**, or **2.50 uSv/h**. The routine maintenance band is
raw **200-300**, or **2.00-3.00 uSv/h**. This is a procedural lab rule, not a
server-enforced range. Before an approved change, record actor, approver, purpose,
UTC time, endpoint, original value, and restoration plan; read back the result.
Temporary tests must restore the recorded original, not blindly assume 250.
No write or attack command is part of routine verification below.

## Prerequisites and Credentials

1. Obtain authorized SSH admission and verify the host key through the course's
   trusted channel. Do not disable host-key checking. Key provisioning is described
   in [infra/README.md](../../infra/README.md).
2. Obtain the approved deployed revision from the RMS owner. Preserve local changes
   and evidence before deployment. Do not run an unreviewed dependency or vendor file.
   The service expects `~/lab/rms_server.py`, `events.py`, `rms_relay.py`, the `hmi/`
   package/templates, `requirements.txt`, and the three files under `units/`.
3. Require Python 3.12 with venv support, pip, systemd user services, and OpenSSL.
   The pinned deployment dependencies are Flask 3.1.3, Gunicorn 26.2.0,
   Pymodbus 3.15.0, and Requests 2.34.2. Use the venv because the host enforces
   PEP 668. A Nix development shell is not the deployed service interpreter.
4. Confirm the course-provided HTTPS route and user-service lingering with the host
   administrator. The lab README says lingering is already enabled; this handoff
   does not independently verify it. Do not attempt privileged host changes yourself.
5. Obtain HMI access from the RMS owner through an approved private channel. The
   ingestion token is provisioned in `~/lab/ASSIGNMENT.txt` on the host, per the W3
   brief; it is not an HMI password or a grant to query the SIEM. SIEM viewing access
   must be separately authorized. Do not invent a token or infer a password.

For an authorized maintainer, these commands open secrets privately rather than
printing them into a transcript. Use a trusted, non-recorded terminal; stop screen
sharing/session capture first. Never paste their contents into chat or evidence.

```bash
# Workstation: authorized login only.
ssh rms@plant.sanctumsec.com
```

```bash
# Plant host, as rms. Leave editors without changing provisioned material unless approved.
id -un
pwd
test -d "$HOME/lab"
stat -c '%a %U %n' "$HOME/lab/.env" "$HOME/lab/ASSIGNMENT.txt"
vi -R "$HOME/lab/ASSIGNMENT.txt"
vi "$HOME/lab/.env"
```

If `.env` is missing, the owner must populate it from approved provisioning before
startup. Preserve existing entries. Use systemd `EnvironmentFile` assignments, not
shell `export` commands; do not `source` this file. Do not put literal `$HOME` in
certificate paths: supply the actual absolute home path shown by `pwd` after login.
This is a key checklist, not a ready-to-use file containing credentials:

| Key | Required configuration |
|---|---|
| `RMS_HMI_USERNAME` | Owner-provisioned username; source defaults to `operator` if absent |
| `RMS_HMI_PASSWORD` | Nonempty owner-provisioned secret; empty/missing rejects all HMI authentication |
| `OT_SIEM_URL` | Exact provisioned ingestion API URL, not the dashboard or stream URL |
| `OT_SIEM_TOKEN` | Provisioned ingestion secret from the assignment; keep private |
| `RMS_GATEWAY_CERT` | Absolute path to the approved server certificate, normally `~/lab/tls/server.pem` expanded to the real home |
| `RMS_GATEWAY_KEY` | Absolute path to its private key, normally expanded `~/lab/tls/server.key` |
| `RMS_GATEWAY_CA` | Absolute path to the trusted client CA certificate, normally expanded `~/lab/tls/ca.pem` |
| `RMS_GATEWAY_CLIENT_SHA256` | Approved client certificate SHA-256 fingerprint(s): 64 hexadecimal digits each, comma-separated, no colons or labels |

The RMS/HMI can run without SIEM variables but then only log events locally. That
is degraded monitoring, not successful handoff. Missing/invalid gateway configuration
fails gateway startup; never replace it with the old transparent relay.

Use [TLS_SETUP.md](../week-03/lab/TLS_SETUP.md) for separately approved certificate
issuance/enrollment. Do not regenerate the CA on routine startup. Clients need their
own certificate/private key and the verified CA certificate; never give them the CA
or server private key. Prefer a client-generated key and CSR. Maintain a
fingerprint-to-person inventory and verify CA fingerprints over the trusted channel.
The recorded client certificate expires **October 20, 2026 at 21:31 UTC**; arrange
renewal, and check actual server/client certificate dates before use. Existing
records do not establish exclusive custody of the generated client key.

```bash
# Plant host, as rms; inspect metadata/public certificates, not private key contents.
chmod 600 "$HOME/lab/.env" "$HOME/lab/tls/server.key"
stat -c '%a %U %n' "$HOME/lab/.env" "$HOME/lab/tls/server.key"
openssl x509 -in "$HOME/lab/tls/server.pem" -noout -subject -issuer -dates
openssl x509 -in "$HOME/lab/tls/server.pem" -noout -checkend 0
openssl verify -CAfile "$HOME/lab/tls/ca.pem" -verify_hostname localhost "$HOME/lab/tls/server.pem"
```

Keep all private keys mode 600 and credential directories owner-only. Never commit
`.env`, assignment contents, tokens, passwords, or private keys. Avoid
`systemctl show ... Environment`, `env`, shell tracing, or process arguments containing
secrets. Password rotation affects all HMI users. Revocation on the gateway requires
removing the fingerprint and restarting the gateway to terminate existing sessions;
there is no automatic reload or CRL/OCSP support.

## Preserve Before Operating

Before deployment, restart, stop, or incident containment, preserve the available
journals and nonsecret service state. Run this block in the same plant shell used
for the later stop/start commands; it establishes `EVIDENCE` for later exports.
Do not put raw logs in Git. Logs may contain sensitive request/response data.

```bash
# Plant host, as rms. This creates a new restricted evidence directory, not a log reset.
umask 077
EVIDENCE="$HOME/rms-evidence/$(date -u +%Y%m%dT%H%M%SZ)-$$"
mkdir -p "$EVIDENCE"
date -u --iso-8601=seconds > "$EVIDENCE/collection-time.txt"
systemctl --user show plant-rms plant-rms-hmi plant-rms-relay --property=Id,ActiveState,SubState,MainPID,NRestarts,FragmentPath > "$EVIDENCE/services-before.txt"
journalctl --user --utc -u plant-rms -u plant-rms-hmi -u plant-rms-relay -o short-iso-precise --no-pager > "$EVIDENCE/journal-before.txt"
sha256sum "$EVIDENCE/collection-time.txt" "$EVIDENCE/services-before.txt" "$EVIDENCE/journal-before.txt" > "$EVIDENCE/SHA256SUMS-before"
```

Record the reason, approving person, affected users, and time in the change/incident
record. Preserve exports in approved restricted storage and share only redacted
copies. Never vacuum journals, truncate logs, erase evidence, or disable monitoring.
Retention/persistence of the host journal is not established here: export promptly.

## Install and Start

These are maintenance commands, not ordinary HMI-operator actions. For an existing
deployment, skip venv installation and unit copying unless the approved change
requires them. If `~/lab` or the reviewed source is missing, stop and obtain the
approved release from the owner; do not guess a clone URL or overwrite live files.

```bash
# Plant host, as rms; source/configuration/certificates already staged and reviewed.
test -f "$HOME/lab/rms_server.py"
test -f "$HOME/lab/hmi/app.py"
test -f "$HOME/lab/.env"
python3 --version
python3 -m venv "$HOME/lab/.venv"
"$HOME/lab/.venv/bin/pip" install -r "$HOME/lab/requirements.txt"
"$HOME/lab/.venv/bin/pip" check
mkdir -p "$HOME/.config/systemd/user"
cp "$HOME/lab/units/plant-rms.service" "$HOME/.config/systemd/user/"
cp "$HOME/lab/units/plant-rms-hmi.service" "$HOME/.config/systemd/user/"
cp "$HOME/lab/units/plant-rms-relay.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable plant-rms plant-rms-hmi plant-rms-relay
systemctl --user start plant-rms
systemctl --user start plant-rms-hmi plant-rms-relay
systemctl --user is-active plant-rms plant-rms-hmi plant-rms-relay
systemctl --user status plant-rms plant-rms-hmi plant-rms-relay --no-pager
ss -ltn '( sport = :5060 or sport = :5061 or sport = :5062 )'
journalctl --user --utc -u plant-rms -u plant-rms-hmi -u plant-rms-relay -n 100 -o short-iso-precise --no-pager
```

Stop at any failed prerequisite/command and investigate; do not continue a partial
installation blindly. All three listeners must bind **127.0.0.1**, not `0.0.0.0`
or `::`. Expected logs include `starting Modbus TCP on 127.0.0.1:5061`, HMI worker
startup, and `read-only Modbus gateway ... mutual_tls=required` with the intended
approved-certificate count. A legacy forwarding message is a failed handoff.
`active` or a startup event alone does not prove successful polling or SIEM delivery.

The units use `Restart=always` and `RestartSec=3`; failures can loop. HMI and gateway
both `Require` and start `After` the backend, but ordering is not a readiness probe.
Do not start extra foreground copies. Changing `.env` requires restarting the
affected services; changing unit files also requires `daemon-reload`. A backend
restart resets threshold to 250, acknowledgement to false, the elapsed-time origin,
and alarm state; it is not a neutral way to investigate a changed threshold.

## Read-Only Acceptance

Use the public HMI in a browser. Enter the privately obtained HMI credentials when
prompted. Expected: `ONLINE`, numeric values in the source-derived ranges below,
threshold 2.50 unless an approved change is recorded, and normally `NORMAL` alarm.
For a precise API check, run this on the authorized workstation. `curl --user`
without a password prompts privately; do not append the password to the command.

```bash
# Workstation; the first request intentionally exercises the 401 path and logs auth.failure.
curl --silent --show-error --output /dev/null --write-out '%{http_code}\n' https://rms.plant.sanctumsec.com/api/status
read -r -p 'Approved HMI username: ' HMI_USER
curl --fail-with-body --silent --show-error --user "$HMI_USER" https://rms.plant.sanctumsec.com/api/status
unset HMI_USER
```

Expected unauthenticated result: HTTP 401. Authenticated result: HTTP 200 JSON with
`ok: true` and eight process fields. HTTP 503 with `ok: false` means the HMI could
not read the backend, not necessarily that the browser credentials are wrong.
The browser marks `OFFLINE` on request failure but leaves old numbers displayed;
do not interpret those numbers as fresh readings. A page load alone is insufficient.

An enrolled peer can verify its gateway access with the supplied client, from its
own `~/lab` on the shared plant host, with its own provisioned files:

```bash
# Authorized peer account, not a public Internet connection to port 5062.
python3 "$HOME/lab/rms_gateway_client.py" --host 127.0.0.1 --port 5062 --server-name localhost --ca "$HOME/lab/tls/ca.pem" --cert "$HOME/lab/tls/partner.pem" --key "$HOME/lab/tls/partner.key"
```

This command only reads FC3 offset 3 and prints the threshold. Do not add
`--test-write` during routine checks. Never use `test_modbus.py` as a read-only
health check: it writes backend state. Do not run either attack script for handoff.
Do not disable TLS hostname validation or fall back to plaintext on 5062.

## Point Map and Expected Values

Device ID is **1**; use zero-based client offsets, not the human reference numbers
as offsets. The W3 [points.md](../week-03/points.md) documents eight points and broad
design ranges. The table below preserves those ranges while identifying actual
source-derived behavior. These are **source facts**, not October 15 live readings.
The source additionally defines a discrete input not documented or live-verified
in that map. Input registers are invalid/unimplemented, not a duplicate of holding
registers. Do not probe undocumented addresses as part of normal operation.

| Reference / offset | Type / access | Name and meaning | Documented range; actual expected behavior | Investigate |
|---|---|---|---|---|
| 40001 / 0 | Holding, FC3, R | `area_radiation`, raw / 100 uSv/h | Map 0-10000 raw; formula gives about 72-198 raw, 0.72-1.98 uSv/h | Outside model envelope, unexplained discontinuity, or stale display; not a physical dose assessment |
| 40002 / 1 | Holding, FC3, R | `count_rate`, CPS | Map 0-65535; model rounds radiation * 118 plus noise of +/-4, giving about 81-238 CPS | Values inconsistent with model; independently noisy, not exactly 118 times displayed rounded radiation |
| 40003 / 2 | Holding, FC3, R | `detector_temperature`, raw / 10 deg C | Map 0-1000 raw; model 228-252 raw, 22.8-25.2 deg C | Outside source envelope or unexplained step |
| 40004 / 3 | Holding, FC3 R; FC6 or FC16 count 1 W | `alarm_threshold`, raw / 100 uSv/h | Map 1-10000 raw; startup 250; policy routine 200-300; numeric band not enforced by source | Any unapproved change, including an in-band write; outside-band values require immediate review |
| 40005 / 4 | Holding, FC3, R | `detector_health`, percent | Map 0-100; code clamps 90-100, but the current radiation envelope makes `round(98 - radiation/8)` equal 98 throughout | Other values suggest changed code/state; 98 does not prove real detector health |
| 40006 / 5 | Holding, FC3, R | `sample_counter` | Map 0-65535; actually `int(elapsed_monotonic_seconds) % 65536` when refreshed, not a sample count | Unexpected reset without approved restart, or lack of progress across successful time-separated reads; wrap is expected |
| 00001 / 0 | Coil, FC1 R; FC5 or FC15 count 1 W | `alarm_acknowledge`, stored Boolean | 0/1, starts false; no source logic resets it or uses it to suppress the alarm | Unrecorded write or unexplained value; true is not proof an alarm was handled |
| 00002 / 1 | Coil, FC1, R | `high_radiation_alarm`, derived Boolean | True only when `round(radiation * 100) > threshold_raw`; false at default 250 under unchanged model | True at default threshold, unauthorized lowering, or code/configuration mismatch; acknowledgement does not clear it |
| Conventional 10001 / 0, source-only | Discrete input, FC2, R in backend definition | Unnamed static false input in `SimDevice`; no assigned process meaning | Source initializes false; absent from `points.md`, HMI, and verified live W4 reads; gateway rejects FC2 | Treat as undocumented/source-only, not a validated process/safety signal |

The server allows only threshold offset 3/count 1 via FC6/16 and acknowledgement
offset 0/count 1 via FC5/15 for writes, subject also to datastore read-only controls.
It has no role, approval, or explicit numeric-band check. Other writes are not an
approved diagnostic. The gateway allows only FC1 coil offsets 0-1 and FC3 holding
offsets 0-5, within each block, for enrolled certificates; all writes are denied.

### Timing and Model Derivation

`rms_server.py` computes radiation as
`1.35 + 0.55*sin(elapsed/18) + uniform(-0.08, 0.08)`, with a floor of 0.01 that
never binds in this envelope. Thus its bounds are approximately 0.72-1.98 uSv/h.
Temperature is `24 + 1.2*sin(elapsed/75)`. The sine denominators are not periods:
the periods are about 113 and 471 seconds, respectively. These mathematical
envelopes do not promise that a short observation visits either endpoint.

There is **no one-second background update loop**. Holding/coil requests invoke
the model, taking new random samples; idle time does not independently emit an
alarm or update datastore values. Counter values derive from elapsed seconds and
wrap after 65536 seconds (about 18 h 12 min 16 s), with repeated/skipped values
depending on read timing. This corrects the once-per-second update and
per-update sample-counter prose in `points.md`; that file remains unchanged.

Holding and coil reads refresh separately, so a JSON radiation value and alarm
coil are not an atomic snapshot. A boundary-near mismatch can arise from the two
random samples; do not assert perfect equivalence between them. At default 250,
the unchanged model cannot reach the threshold, and even the policy lower bound
200 exceeds its maximum rounded radiation of 198. There is no modeled high-alarm
cycle at those settings. Do not lower a threshold merely to generate evidence.

## Normal Polling and Peers

The browser calls `/api/status` immediately and schedules another call every
**3000 ms**. This is a client-side requested cadence, not a guaranteed network or
process sampling interval; stalled/overlapping requests and multiple browser tabs
can change observed traffic. Each successful API call opens a backend Modbus
connection, requests FC3 offset 0/count 6 and then FC1 offset 0/count 2, device 1,
and closes it. The client timeout is 2 seconds, not a guaranteed total request
duration. `/` only renders the page; it does not itself read Modbus.

Normal viewing produces authentication events on every protected request, reads,
and no writes. Unexplained FC5/6/15/16, threshold changes, unexpected accounts or
certificate fingerprints, or exposed non-loopback listeners require review.

| Peer / flow | Protocol and endpoint | What is established |
|---|---|---|
| Browser -> HMI -> RMS | Public HTTPS -> local HTTP 5060 -> Modbus TCP 5061 | Source implements authenticated status viewing, not control routes |
| SFPCM Level 1 -> RMS Level 2 | Mutual TLS 5062 -> permitted Modbus reads at 5061 | Live October 13 evidence establishes an enrolled credential's read/no-write boundary on 5062; no fixed peer polling rate established |
| RMS -> DCS, intended W3 telemetry relationship | W3 specifies analog + Modbus; historical peer at loopback 5051 | W4 log records an earlier successful W3 peer response, not a verified continuous RMS-to-DCS consumer or current schedule; reviewed service source implements no DCS export loop |
| RMS -> SFPCM reciprocal comparison | HTTP/JSON at `127.0.0.1:5022/v1/temperature-alarm`, bearer token | Recorded GET 200 and POST 403 for `partner_read`; this is a comparison, not enforcement of inbound RMS access or a standing polling service |
| RMS/HMI -> OT-SIEM | HTTP(S) POST to `OT_SIEM_URL` with bearer ingestion token | Actual implementation is an event API, not the brief's generic syslog/OPC-UA description; October 14 records identify `siem.plant.sanctumsec.com` as the working SIEM host |

Do not assume `ot-siem.plant.sanctumsec.com` resolves: the Attack A evidence records
that it did not. Use the provisioned ingestion URL, not a guessed hostname or
the dashboard stream endpoint. Logical Purdue levels are not separate network
segments on this shared host. Do not make backend ports public to connect peers.

## SIEM and Monitoring Gaps

`events.py` timestamps events in UTC to seconds, sets system `RMS`, Purdue level 2,
and uses a daemon worker to POST JSON with a 3-second request timeout. Severity
maps info/warning/critical to low/medium/high. The standard event source is
`127.0.0.1` with null port and identity, not the actual authenticated caller.

| Event / journal | Source behavior and operational interpretation |
|---|---|
| `service.state` | Backend startup and attempted finally-block stop event; HMI worker startup, potentially one per worker; not a periodic health check or assured shutdown receipt |
| `protocol.read` | First eligible read and then at most one emitted per 600-second monotonic gate across reads in the process; a read must occur after the gate opens; no timer-driven heartbeat or full read audit |
| `protocol.write` | Accepted control writes, medium severity, function/offset/values and T1692.001 label in source detail; no role, approval, or out-of-band decision |
| `auth.success` / `auth.failure` | Each protected HMI request, low/medium; remote address/path in detail; forwarded address is not a verified human identity |
| `process.alarm` | On evaluated alarm transitions only, high on activation, low on clearing; dependent on requests, not an independent detector |
| Gateway journal | Certificate fingerprint, `partner_read`, transaction, function, offset, count and allowed/denied decision; no direct gateway SIEM emitter |

Follow logs during authorized operation:

```bash
# Plant host, as rms; Ctrl-C ends journal viewing, not the services.
journalctl --user --utc -u plant-rms -u plant-rms-hmi -u plant-rms-relay -f -o short-iso-precise
```

Look for `OT-SIEM accepted`, rejected responses, `delivery failed`, queue-full
warnings, repeated restarts, and gateway denials. An ingestion acknowledgement is
not an authorization decision, an alarm notification, or proof of SIEM rendering.
With separately authorized SIEM viewing, inspect the real dashboard at
`https://siem.plant.sanctumsec.com/` and correlate RMS records by UTC time/type.
Attack A used `/api/v1/stream?limit=20&system=RMS&severity=medium`; that filter is
not a complete history or an all-severity incident search. Do not use the ingestion
token as a dashboard credential and never send synthetic events for verification.

Known gaps to carry into W5:

- The per-process queue holds 256 events, has no disk spool or retry, drops on full,
  and logs delivery failures without replay. Its daemon worker is not joined or
  drained at shutdown. There is no guaranteed final event, delivery time, or lossless
  recovery. HMI workers have separate queues; process availability can mask SIEM loss.
- Sampled reads do not measure browser cadence or prove absence of unauthorized
  reads. Rejected backend writes are not explicitly emitted by the server action.
  Gateway TLS handshake failures precede its handler; retain client failures too.
- The gateway journal is not shown to be ingested by SIEM. October 13 denial evidence
  does not establish SIEM receipt or live rejection of all invalid-certificate cases.
- Attack A's visible SIEM records omitted source values/actor, had unpopulated target
  fields and null flags, and did not distinguish 301 from 300/restoration. Retain the
  full source journal to compare values with policy; no dedicated alert was shown.
  This does not prove that every SIEM store or detector lacks those details.
- Shared credentials and raw backend Modbus do not attribute actions to humans.
  A certificate proves possession of a key, not exclusive custody or Linux username.
  Port 5061 remains a gateway bypass unless separately isolated by the administrator.
- Source telemetry is self-asserted. The ingestion token authenticates a source,
  not the truth of an event. Protect dependencies/configuration and preserve
  independent observations; never fabricate telemetry to demonstrate this weakness.

## Stop and Restore Service

Only authorized maintenance may stop services. Notify users, record the window,
and run the preservation block first. Stop dependents before the backend:

```bash
# Plant host, as rms; planned shutdown, not a remedy for an unexplained alarm.
systemctl --user stop plant-rms-hmi plant-rms-relay
systemctl --user stop plant-rms
systemctl --user is-active plant-rms plant-rms-hmi plant-rms-relay
ss -ltn '( sport = :5060 or sport = :5061 or sport = :5062 )'
journalctl --user --utc -u plant-rms -u plant-rms-hmi -u plant-rms-relay -o short-iso-precise --no-pager > "$EVIDENCE/journal-after.txt"
sha256sum "$EVIDENCE/journal-after.txt" > "$EVIDENCE/SHA256SUMS-after"
```

Expected: inactive units and no listeners on these ports. `is-active` returning
nonzero for stopped units is expected. Explicit `systemctl stop` is not undone by
`Restart=always`; killing a process directly may cause a restart. Stopping does not
disable boot activation. Disable units only for separately approved decommissioning.
Do not delete logs, `.env`, TLS files, or source. Failure to see a final SIEM stop
event is not proof the process stayed running; check unit state/listeners.

To resume without reinstalling:

```bash
systemctl --user start plant-rms
systemctl --user start plant-rms-hmi plant-rms-relay
systemctl --user status plant-rms plant-rms-hmi plant-rms-relay --no-pager
```

Repeat listener, authenticated HMI, gateway read, and monitoring checks. Record the
reset threshold/counter and notify the supervisor of any pre-stop approved threshold
that differs from startup 250. Reapplying it is a separate approved maintenance
write, not an automatic part of restart. No persistent setpoint storage exists.

## W4 Results and Limits

These are **recorded live results**, not new tests, except Attack B's explicitly
unexecuted disposition. Full chronology and excerpts are in
[adversary-test.md](adversary-test.md), [session-log.md](session-log.md), and
[Attack A evidence](adversary-test.md#attack-a--insider).

| Test | Result and recorded evidence | Operator consequence |
|---|---|---|
| A: legitimate-account insider, October 14 after policy design | **Executable.** At 22:01:52Z (16:01:52 MDT), backend FC6 offset 3 accepted `250 -> 300 -> 250`, then `250 -> 301 -> 250`. A separate read at 22:01:57.938278Z confirmed 250. Four source writes carried values `[300]`, `[250]`, `[301]`, `[250]`; four ingestion acknowledgements and independently retrieved SIEM records 67083-67086 corroborated visibility. | Backend does not enforce policy range, role, or approval. All visible SIEM records had the same medium severity/message and null flags; source-value review is necessary. No distinguishing policy alert was demonstrated. |
| B: supply-chain trust | **Untestable as of October 15, 2026; not run.** The existing `attack_b_supply_chain.py` stages a modified `events.py` that falsely reports an active service as inactive to the connected SIEM. False SIEM telemetry is prohibited by the ROE, even if marked as a test. No permissible, verified downstream consumer is available to demonstrate the required connected-system consequence. | Do not run the script, including its network-reading preflight, or treat local tests/staging as a successful attack. No live downstream effect, receipt, or blocked-control result is claimed. A future permissible scenario requires reviewed scope and a verified consumer first. |
| C: SFPCM pivot, October 12 before written policy | **Executable.** Transparent 5062 relay forwarded FC6: `250 -> 300 -> 250`; independent final read 250, two RMS write events and SIEM acknowledgements. Client UTC 2026-10-13 02:05:36 corresponds to October 12 20:05:36 MDT. | Preserve the historical finding: loopback and logging did not enforce peer read-only access. Do not restore the transparent relay. |
| C: October 13 after policy design and gateway deployment | **Blocked on the tested 5062 path.** At 19:40:24 MDT (2026-10-14 01:40:24Z), enrolled credential read 250, attempted FC6 raw 300, received `8601` (Illegal Function), then read 250. Gateway journal correlates allowed/denied/allowed transactions. No restoration write was needed. | Validated credential-level read/no-write boundary for this operation; not backend isolation, seven-role RBAC, all live negative-auth cases, or SIEM receipt of the denial. |

The W4 reports record the same October 15 **Untestable** disposition; it does not
convert an unrun test into evidence. All 31 local gateway/probe unit tests passed
on October 15; they are implementation checks, not live plant attack evidence.
Direct backend isolation, broader role coverage,
range enforcement, actor/approval attribution, and centralized value visibility
remain open, not implied by the Blocked gateway result.

## Incident First Actions

1. Treat unexpected readings, `OFFLINE`, threshold changes, missing monitoring,
   repeated authentication failures, or an unrecognized gateway credential as an
   anomaly. Note the UTC time, HMI freshness, displayed threshold/alarm, and affected
   endpoint. A real-world safety concern goes through the site's established safety
   response, not this simulation runbook.
2. Notify the RMS owner (Santiago Vargas), supervisor, and cybersecurity manager
   through the course's approved coordination channel. For routing, account, or
   backend-isolation issues involve the host administrator/instructor. Contact
   addresses and on-call coverage are not provided in the repository: establish
   them at handoff rather than inventing an emergency number.
3. Preserve available journals/service state with the block above before any
   restart or containment. Save relevant browser/API observations and approved SIEM
   records with timestamps, timezone, event IDs, and collection method. Keep raw
   evidence restricted and immutable in the approved evidence store; redact shared
   excerpts. Record errors even if collection fails; do not fabricate missing data.
4. Read status only if authorized. Correlate `protocol.write` offset 3 values with
   raw 200-300 and the change record; an in-band value is not automatically approved.
   Examine both source and SIEM records, gateway identities/decisions, and available
   SSH fingerprint-to-person records. Do not assign a human identity from loopback
   source IP or a shared account alone.
5. Do not raise the threshold to hide an alarm, acknowledge merely to clear a
   display, replay attacks, modify readings, disable logging, expose ports, rotate
   credentials indiscriminately, or restart as a first diagnostic. Restart destroys
   volatile state and resets setpoints. An unexplained 301 is evidence, not an
   instruction to overwrite it immediately.
6. Have the supervisor/security manager approve containment and maintenance. The
   administrator must address a suspected direct-5061 bypass; tightening only the
   gateway is insufficient. If credential revocation is approved, preserve the
   inventory/decision, remove the affected fingerprint/key through authorized
   administration, and coordinate the gateway restart. Preserve evidence first.
7. After authorized recovery, verify the intended threshold by readback, HMI
   freshness, loopback bindings, gateway reads, and truthful monitoring delivery.
   Record residual gaps, approver, restoration state, and handoff time. Do not
   declare success from `active`, SIEM acknowledgement, or one green HMI card alone.

## Reference Priority

Use the course ROE/assignment and [RBAC policy](rbac-policy.md) for authorization;
use [server source](../week-03/lab/rms_server.py),
[event source](../week-03/lab/events.py),
[HMI source](../week-03/lab/hmi/app.py), its template, and
[user units](../week-03/lab/units/) for implementation facts. The
[lab README](../week-03/lab/README.md) and TLS setup describe deployment. The
[W3 brief](../week-03/README.md) defines allocation and intended links, not proof
of their implementation. Existing live W4 evidence establishes only the specific
dated observations above. If source, documentation, and the deployed service
disagree, preserve the discrepancy and escalate; do not claim current live state
from source alone or silently change the scope of a historical test.
