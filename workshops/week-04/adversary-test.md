# Adversary Test - Radiation Monitoring System (RMS)
## CS 581 Workshop 4 | Santiago Vargas | October 15, 2026

**System:** Radiation Monitoring System (authorized CS 581 simulation)
**Attacks run:** Attack C on October 12 and follow-up on October 13, 2026 (MDT).
Attack A on October 14, after policy design. Attack B is Untestable under the
verified current scope as of October 15; no live execution is claimed.

Three attacks drawn from your W2 threat cards, run against the access control policy
you wrote in rbac-policy.md. Run them in this order: design first, then attack, then revise.

**Sequence disclosure:** The original October 12 Attack C preceded the written
policy. Following the professor's clarification, I retained that evidence, wrote
the policy on October 13, added enforcement, and repeated the same threshold-write
scenario. The two results below are **Executable before, Blocked after** on the
tested port 5062 path; the first result has not been deleted or reclassified.

**October 15 read-only handover verification:** After reviewing Attack B's scope,
the authorized `rms` SSH account queried its hostname and three user-unit states
(all active), performed one device-1 FC3 read of holding offsets 0-5 on 5061
(`[89, 103, 247, 250, 98, 49970]`), and requested its local HMI API without
credentials (401). The public board and its advertised status API were read.
A local browser then authenticated to our public HMI and allowed ordinary polling
to capture its ONLINE display. These requests can generate ordinary auth/read
events; no points, services, credentials, or logs were changed. Collection
context, commands, and screenshot provenance are in
[October 15 evidence](session-log.md#october-15-collection) and session 11. These are
health/evidence checks, not reruns of A, B, or C, nor access to a peer service.

---

## Attack A — Insider

**Threat card source:** W2 card 5, Maroochy Water Breach Insider;
T1692.001, Unauthorized Message: Command Message
(`../week-02/threat-cards/cards.json`, card 5). This models an insider's misuse of
legitimate engineering access, not the historical incident's radio equipment or
an actual radiation-monitoring compromise.
**Hypothesis:** The legitimate `rms` account could write raw 301 to the threshold
through backend port 5061 despite the written routine band of 200-300. RMS would
log an accepted write, but normal and prohibited writes would not be differentiated
by identity, approval context, or an explicit policy-violation alert in the visible
SIEM stream.

### What you did

At 16:01:52 MDT on October 14 (`22:01:52Z`), the guarded
`../week-03/lab/attack_a_insider.py` probe ran over the existing authorized SSH
connection as `rms`, after the October 13 policy. It used the maintenance-accessible
backend at `127.0.0.1:5061`, device 1, holding-register offset 3, FC3 reads and FC6
writes. No credentials were attacked, no service was stopped, and no log was erased.

The exercise authorization scoped these reversible changes; the scenario being
modeled is an insider violating the routine operational policy, not an unapproved
attack on a real plant. Raw 301 (3.01 uSv/h) is just above the selected upper bound,
not a claimed physical safety threshold. The test sequence was:

1. Read-only preflight confirmed original raw 250.
2. In-band comparison: write 300, verify 300, restore and verify 250.
3. Insider action: write 301, verify 301, restore and verify 250.
4. Independently reread after the probe and confirm 250.
5. Inspect RMS source events, ingestion acknowledgements, and the actual SIEM stream.

The comparison models a routine-band adjustment; it does not claim an independently
verified supervisor approval. Both cycles restored the recorded original in a
`finally` block. The probe is read-only unless explicitly given `--execute`.

```bash
ssh rms@plant.sanctumsec.com '"$HOME/lab/.venv/bin/python" -B "$HOME/lab/attack_a_insider.py" --execute'
```

### Evidence

Complete client output, RMS event/acknowledgement lines, exact collection commands,
and four matching SIEM records are preserved below.

| Observation | Evidence |
|---|---|
| Routine-band comparison | Client readbacks `250 -> 300 -> 250`. |
| Prohibited action | FC6 accepted raw 301; client readback `301`, then restored `250`. |
| Source detection | Four medium `protocol.write` events; `detail.values` were `[300]`, `[250]`, `[301]`, `[250]`; source identity was null. |
| Delivery | Four `OT-SIEM accepted protocol.write: {"accepted":1,"rejected":[]}` acknowledgements. |
| Independent SIEM check | Live stream records 67083-67086 at `2026-10-14T22:01:52Z`, all medium `protocol.write`, flags null, target/value unpopulated. |
| Final state | Separate read at `22:01:57.938278Z` confirmed 250. |

The stream was retrieved from the endpoint used by the actual SIEM dashboard:

```text
https://siem.plant.sanctumsec.com/api/v1/stream?limit=20&system=RMS&severity=medium
```

**Is the insider action distinguishable from normal operation?** In the full RMS
journal, yes: a reviewer can compare `detail.values=[301]` with the written band.
In the observed SIEM dashboard projection, no policy-specific distinction is
visible. The comparison, prohibited write, and restorations share the event type,
severity, message, loopback source, and second-resolution timestamp. The projection
does not expose the values, actor, or approval state, and all four flags are null.
The same T1692.001 label is attached to every source write, including the in-band
comparison; it is not a decision that misuse occurred. We observed no distinguishing
alert in this stream, not the absence of all possible SIEM rules or hidden storage.

#### Attack A evidence - October 14, 2026

Authorized RMS simulation, performed through SSH as the existing `rms` account
after the October 13 written policy. This is not an authentication attack.
UTC client time 22:01:52 corresponds to 16:01:52 MDT (UTC-6).

#### Commands

The probe was uploaded to `~/lab/attack_a_insider.py` in the RMS account. Local
unit tests verified baseline guards and restoration behavior before deployment.

```bash
ssh rms@plant.sanctumsec.com '"$HOME/lab/.venv/bin/python" -B "$HOME/lab/attack_a_insider.py"'
ssh rms@plant.sanctumsec.com '"$HOME/lab/.venv/bin/python" -B "$HOME/lab/attack_a_insider.py" --execute'
ssh rms@plant.sanctumsec.com 'journalctl --user -u plant-rms --since "2026-10-14 16:01:45" --until "2026-10-14 16:02:10" -o short-iso --no-pager'
```

The first invocation is read-only. The execution explicitly scopes an in-band
comparison at 300 and the prohibited out-of-band action at 301. It restores the
recorded original value in `finally` after each attempt. The in-band comparison
models routine value selection, not an independently verified supervisor approval.

#### Client output

```text
2026-10-14T22:01:46.631236+00:00 Account: rms
2026-10-14T22:01:46.631279+00:00 Endpoint: 127.0.0.1:5061; device=1; holding offset=3; FC3/FC6
2026-10-14T22:01:46.633598+00:00 Original: 250
2026-10-14T22:01:46.633627+00:00 Read-only preflight; no writes performed
```

```text
2026-10-14T22:01:52.418314+00:00 Account: rms
2026-10-14T22:01:52.418355+00:00 Endpoint: 127.0.0.1:5061; device=1; holding offset=3; FC3/FC6
2026-10-14T22:01:52.420500+00:00 Original: 250
2026-10-14T22:01:52.420854+00:00 in_band_comparison: attempt=300; documented routine band=200-300
2026-10-14T22:01:52.421288+00:00 in_band_comparison: FC6 response=WriteSingleRegisterResponse(dev_id=1, transaction_id=3, address=3, count=0, bits=[], registers=[300], status=1, retries=0)
2026-10-14T22:01:52.421687+00:00 in_band_comparison: readback=300
2026-10-14T22:01:52.422972+00:00 in_band_comparison: restore FC6 response=WriteSingleRegisterResponse(dev_id=1, transaction_id=5, address=3, count=0, bits=[], registers=[250], status=1, retries=0)
2026-10-14T22:01:52.423243+00:00 in_band_comparison: restored readback=250
2026-10-14T22:01:52.423568+00:00 out_of_band_test: attempt=301; documented routine band=200-300
2026-10-14T22:01:52.424025+00:00 out_of_band_test: FC6 response=WriteSingleRegisterResponse(dev_id=1, transaction_id=8, address=3, count=0, bits=[], registers=[301], status=1, retries=0)
2026-10-14T22:01:52.424482+00:00 out_of_band_test: readback=301
2026-10-14T22:01:52.424891+00:00 out_of_band_test: restore FC6 response=WriteSingleRegisterResponse(dev_id=1, transaction_id=10, address=3, count=0, bits=[], registers=[250], status=1, retries=0)
2026-10-14T22:01:52.425187+00:00 out_of_band_test: restored readback=250
2026-10-14T22:01:52.425213+00:00 Completed; final threshold=250
```

A separate read-only invocation after journal collection confirmed restoration:

```text
2026-10-14T22:01:57.935999+00:00 Account: rms
2026-10-14T22:01:57.936043+00:00 Endpoint: 127.0.0.1:5061; device=1; holding offset=3; FC3/FC6
2026-10-14T22:01:57.938278+00:00 Original: 250
2026-10-14T22:01:57.938308+00:00 Read-only preflight; no writes performed
```

#### RMS source journal and ingestion acknowledgements

```text
2026-10-14T16:01:52-06:00 ip-172-26-0-239 python[230612]: 2026-10-14 16:01:52,421 INFO events event={'ts': '2026-10-14T22:01:52Z', 'system': 'RMS', 'purdue_level': 2, 'event_type': 'protocol.write', 'severity': 'medium', 'source': {'ip': '127.0.0.1', 'port': None, 'identity': None}, 'message': 'Modbus client changed an RMS control point', 'detail': {'protocol': 'modbus-tcp', 'function_code': 6, 'offset': 3, 'values': [300], 'detection_opportunity': 'T1692.001 Unauthorized Message'}}
2026-10-14T16:01:52-06:00 ip-172-26-0-239 python[230612]: 2026-10-14 16:01:52,499 INFO events OT-SIEM accepted protocol.write: {"accepted":1,"rejected":[]}
2026-10-14T16:01:52-06:00 ip-172-26-0-239 python[230612]: 2026-10-14 16:01:52,500 INFO events event={'ts': '2026-10-14T22:01:52Z', 'system': 'RMS', 'purdue_level': 2, 'event_type': 'protocol.write', 'severity': 'medium', 'source': {'ip': '127.0.0.1', 'port': None, 'identity': None}, 'message': 'Modbus client changed an RMS control point', 'detail': {'protocol': 'modbus-tcp', 'function_code': 6, 'offset': 3, 'values': [250], 'detection_opportunity': 'T1692.001 Unauthorized Message'}}
2026-10-14T16:01:52-06:00 ip-172-26-0-239 python[230612]: 2026-10-14 16:01:52,525 INFO events OT-SIEM accepted protocol.write: {"accepted":1,"rejected":[]}
2026-10-14T16:01:52-06:00 ip-172-26-0-239 python[230612]: 2026-10-14 16:01:52,525 INFO events event={'ts': '2026-10-14T22:01:52Z', 'system': 'RMS', 'purdue_level': 2, 'event_type': 'protocol.write', 'severity': 'medium', 'source': {'ip': '127.0.0.1', 'port': None, 'identity': None}, 'message': 'Modbus client changed an RMS control point', 'detail': {'protocol': 'modbus-tcp', 'function_code': 6, 'offset': 3, 'values': [301], 'detection_opportunity': 'T1692.001 Unauthorized Message'}}
2026-10-14T16:01:52-06:00 ip-172-26-0-239 python[230612]: 2026-10-14 16:01:52,550 INFO events OT-SIEM accepted protocol.write: {"accepted":1,"rejected":[]}
2026-10-14T16:01:52-06:00 ip-172-26-0-239 python[230612]: 2026-10-14 16:01:52,550 INFO events event={'ts': '2026-10-14T22:01:52Z', 'system': 'RMS', 'purdue_level': 2, 'event_type': 'protocol.write', 'severity': 'medium', 'source': {'ip': '127.0.0.1', 'port': None, 'identity': None}, 'message': 'Modbus client changed an RMS control point', 'detail': {'protocol': 'modbus-tcp', 'function_code': 6, 'offset': 3, 'values': [250], 'detection_opportunity': 'T1692.001 Unauthorized Message'}}
2026-10-14T16:01:52-06:00 ip-172-26-0-239 python[230612]: 2026-10-14 16:01:52,575 INFO events OT-SIEM accepted protocol.write: {"accepted":1,"rejected":[]}
```

#### Independently retrieved SIEM stream

The live SIEM page at `https://siem.plant.sanctumsec.com/` uses
`/api/v1/stream` to populate its dashboard. The following read-only query was made
after the test, without the ingestion token:

```text
GET https://siem.plant.sanctumsec.com/api/v1/stream?limit=20&system=RMS&severity=medium
```

Below are the four matching event objects from the response, in its returned
newest-first order. The response envelope and unrelated earlier records are
omitted. Its `now` field was `1792015342.9700243` and `seeded` was `false`.

```json
[
  {"event_type":"protocol.write","flags":null,"id":67086,"message":"Modbus client changed an RMS control point","purdue_level":2,"received":1792015312.5530863,"severity":"medium","source_ip":"127.0.0.1","source_port":null,"system":"RMS","target_name":null,"target_value":"null","ts":"2026-10-14T22:01:52Z"},
  {"event_type":"protocol.write","flags":null,"id":67085,"message":"Modbus client changed an RMS control point","purdue_level":2,"received":1792015312.5276637,"severity":"medium","source_ip":"127.0.0.1","source_port":null,"system":"RMS","target_name":null,"target_value":"null","ts":"2026-10-14T22:01:52Z"},
  {"event_type":"protocol.write","flags":null,"id":67084,"message":"Modbus client changed an RMS control point","purdue_level":2,"received":1792015312.5027666,"severity":"medium","source_ip":"127.0.0.1","source_port":null,"system":"RMS","target_name":null,"target_value":"null","ts":"2026-10-14T22:01:52Z"},
  {"event_type":"protocol.write","flags":null,"id":67083,"message":"Modbus client changed an RMS control point","purdue_level":2,"received":1792015312.4724283,"severity":"medium","source_ip":"127.0.0.1","source_port":null,"system":"RMS","target_name":null,"target_value":"null","ts":"2026-10-14T22:01:52Z"}
]
```

The four records establish SIEM-side visibility, not merely source-side delivery
acknowledgement. They have the same event type, severity, message, source IP, and
claimed timestamp; none has a distinguishing flag or populated target/value.
The stream does not expose the source event's `detail.values` or caller identity.
The full RMS journal distinguishes 301 from 300; the observed dashboard projection
does not. This does not establish whether some other SIEM storage/API retains the
detail, nor prove the absence of every possible detection rule.

The initially assumed hostname `ot-siem.plant.sanctumsec.com` did not resolve from
the host. The configured nonsecret ingestion URL identified the actual SIEM host;
the public page then supplied the stream route. No authentication settings or
monitoring controls were changed to obtain the evidence.

### Result

- [x] **Executable** - legitimate account access successfully changed the threshold
  outside the routine policy band, and verified restoration completed.
- [ ] **Blocked** — stopped by a control; name the control
- [ ] **Untestable** — explain why

### What this reveals about the RBAC policy

The TLS gateway's blocked peer-write result does not constrain a legitimate RMS
account using its own backend maintenance path. The backend enforces addresses and
function codes but not the policy's numeric band, job role, or approval state.
Logging every write makes the action visible without making it attributable or
automatically recognizable as a policy violation. The observed SIEM projection
further loses the value needed to distinguish the outside-band write.

The revised policy requires source-value review and timestamp correlation when
investigating a threshold change. Human attribution, validated approval context,
centralized value visibility, and a dedicated outside-band detection remain
documented gaps rather than controls claimed to be deployed.

---

## Attack B — Supply Chain

**Threat card source:** W2 card 2, Dragonfly, T0862 Supply Chain Compromise
(`../week-02/threat-cards/cards.json`). The analogy is trust in supplied software,
not a claim that Dragonfly targeted this RMS implementation.

**Hypothesis, not a finding:** A tampered dependency/configuration loaded by RMS
could alter exported status that an independently connected process peer trusts.
The gateway's read-only role would not prove the integrity of the data it returns.

### What you did

On October 15 I reviewed the prepared `attack_b_supply_chain.py` and the actual
RMS source before execution. The script stages a modified `events.py`, starts an
isolated RMS copy on 5063, changes an active startup report to inactive, and sends
the false event to OT-SIEM. This would manipulate what the excluded SIEM records.
A test marker and later corrective event do not override the rules of engagement.
**I did not run this script or its preflight.**

The repository documents historical DCS responses and coordinated SFPCM requests,
but no verified downstream observation for Attack B. No connected-system effect
is claimed, and a local mock is not substituted for the required evidence.

### Evidence

See [October 15 collection](session-log.md#october-15-collection). Static evidence is the
wrapper in `staged_dependency()` and telemetry submission in `main()` of the
prepared script. The local wrapper tests passed with mocked emission; they neither
contact the SIEM nor prove a downstream consequence. There is no Attack B SIEM
output or packet capture because no authorized live attempt was made. This is a
scope/evidence limitation, not a named technical control blocking execution.

### Result

- [ ] **Executable**
- [ ] **Blocked**
- [x] **Untestable** - the prepared downstream target is excluded by the ROE, and
  no verified permitted receiving consumer was available for a replacement test.
  This does not satisfy the stronger claim of a completed supply-chain attack;
  instructor acceptance of this limitation is not assumed.

### What this reveals about the RBAC policy

The maintenance account can edit dependencies and configuration, so admission is
not code-integrity assurance. That is supported by source/ownership assumptions,
not a demonstrated downstream compromise. The revised policy requires review of
dependencies and separately verified peer-consumer scope, and expressly forbids
synthetic false SIEM telemetry. Signed artifacts, isolated deployment authority,
and independent consumer validation remain proposals, not deployed controls.

---

## Attack C — Pivot

**Threat card source:** Sandworm Team, Unauthorized Message: Command Message
(MITRE ATT&CK for ICS T1692.001)
**Attacker system:** Spent Fuel Pool Cooling and Monitoring (SFPCM)
**Starting role account:** `sfpcm`
**Boundary crossed:** SFPCM Level 1 to RMS Level 2
**Hypothesis:** If the SFPCM attacker could reach a new transparent relay in front of
the RMS Modbus service, the RMS would accept a function-code 6 setpoint write because
neither traditional Modbus nor the relay carries or enforces a user role. I expected
the RMS to report an accepted write to OT-SIEM, but not to determine whether the
attacker was authorized to make it.

### Original Run - October 12: What You Built

We created a new path on the shared plant host:

```text
SFPCM test client
  -> RMS transparent TCP relay at 127.0.0.1:5062
  -> RMS Modbus/TCP service at 127.0.0.1:5061, device ID 1
```

The RMS relay was a Python `asyncio` byte-forwarding service managed by the
`plant-rms-relay.service` user unit. It bound only to loopback and forwarded traffic
to the existing loopback-only RMS controller. The relay did not authenticate the
client, attach an identity, restrict Modbus function codes, or enforce register-level
permissions.

For a reciprocal control comparison, the SFPCM system also exposed an HTTP/JSON
gateway at `127.0.0.1:5022`. Its `/v1/temperature-alarm` endpoint required a bearer
token and assigned my identity the `partner_read` role. The token is intentionally
excluded from this report.

### What you did

From the `sfpcm` role account, the attacker connected a Modbus client to the new RMS
relay. The client read holding-register offset 3 with function code 3 and stopped if
the baseline was not the agreed raw value of 250 (2.50 uSv/h). It then used function
code 6 to write the agreed test value 300 (3.00 uSv/h), read the value back, restored
the recorded original value in a `finally` block, and verified restoration. This
register is the RMS high-radiation alarm threshold, not a simulated sensor reading.

I independently read offset 3 through the relay after the test and received 250.
For the reciprocal comparison, I reached the SFPCM gateway from the `rms` role. An
unauthenticated request received 401. With a valid short-lived token, a GET succeeded,
but a POST attempting to set `temperature_alarm_c` to 44.0 received 403 because the
`partner_read` role did not have write permission.

### Evidence

The SFPCM-side client recorded the complete RMS change and restoration in
`~/lab/w4-rms-attack-c.txt`:

```text
2026-10-13T02:05:36.847333+00:00 Before: 250
2026-10-13T02:05:36.847977+00:00 Test FC6 response: WriteSingleRegisterResponse(dev_id=1, transaction_id=2, address=3, registers=[300], status=1, retries=0)
2026-10-13T02:05:36.850129+00:00 After test: 300
2026-10-13T02:05:36.850659+00:00 Restore FC6 response: WriteSingleRegisterResponse(dev_id=1, transaction_id=4, address=3, registers=[250], status=1, retries=0)
2026-10-13T02:05:36.851091+00:00 After restoration: 250
```

My independent post-test Modbus read through port 5062 confirmed the safe state:

```text
Value: 250
```

At the same instant, the RMS journal recorded two `protocol.write` events: one for
the test and one for restoration. OT-SIEM acknowledged both:

```text
Oct 12 20:05:36 RMS event_type=protocol.write severity=medium
Oct 12 20:05:36 OT-SIEM accepted protocol.write: {"accepted":1,"rejected":[]}
Oct 12 20:05:36 RMS event_type=protocol.write severity=medium
Oct 12 20:05:36 OT-SIEM accepted protocol.write: {"accepted":1,"rejected":[]}
```

The apparent date difference is only time-zone presentation: the client printed UTC
on October 13 while `journalctl` printed the host's local time on October 12.

The reciprocal SFPCM gateway logs demonstrated separate authentication and
authorization decisions:

```text
2026-10-13T02:28:31.859719+00:00 identity=null method=POST status=401
2026-10-13T02:33:33.858344+00:00 identity=santiago-rms method=POST status=403 role=partner_read decision=write_denied parameter=temperature_alarm_c
2026-10-13T02:33:34.682810+00:00 identity=santiago-rms method=GET status=200 decision=read_allowed
```

This reciprocal evidence is a control comparison; the SFPCM-to-RMS write determines
the result of the original Attack C run.

### Original Run Result - October 12

- [x] **Executable** — the SFPCM client changed the RMS alarm threshold through the
  newly created relay and restored it successfully.
- [ ] **Blocked**
- [ ] **Untestable**

### What this reveals about the RBAC policy

Loopback binding separated the protocol from external network interfaces but did not
separate role accounts on the shared host. Once the new relay made the path available,
the RMS accepted an unauthenticated Modbus write from the SFPCM client. The RMS and
OT-SIEM detected that a write occurred, but the event contained no authenticated
attacker identity and could not determine whether the action was authorized. Detection
therefore did not compensate for missing enforcement.

The reciprocal SFPCM gateway showed the control the RMS path lacked: it authenticated
`santiago-rms`, permitted a read for the `partner_read` role, and denied a write. The
RMS policy needs an enforcing intermediary that authenticates each peer and separates
read and write permission by role, register, range, and function code. Until that is
implemented, this remains a lab access-control gap rather than full RBAC. At the
time of the October 12 test, the relay was transparent. The replacement read-only
gateway described below is subsequent partial remediation, not a change to that
historical result.

### Follow-Up - October 13: Authenticated Write-Denial Test

**Policy boundary:** An authenticated individual operating from the `sfpcm` role
may read the RMS alarm threshold but must not write it. Network reachability or a
valid credential does not grant write permission. The baseline policy also records
that the original relay was unauthenticated; that was the actual pre-remediation
control gap, not a permission the new policy grants.

**Hypothesis:** After replacing transparent forwarding with an enforcing gateway,
The attacker's approved client certificate would authenticate successfully and permit
a function 3 threshold read. The same function 6 attempt to change raw 250 to 300
would receive a Modbus exception, with the threshold remaining at 250.

**Control deployed:** The existing `plant-rms-relay.service` now runs a
certificate-authenticated, read-only Modbus gateway on port 5062. It requires a
CA-verified certificate and an explicitly allowlisted SHA-256 certificate
fingerprint, assigns `partner_read`, and permits only device 1 function 1/3 reads
within the documented point blocks. Writes are denied before forwarding to the
backend. The tested connection was:

```text
Authenticated individual using the sfpcm account
  -> mutual TLS gateway at 127.0.0.1:5062, role partner_read
  -> permitted Modbus reads to RMS at 127.0.0.1:5061, device ID 1
```

**What was repeated:** The attacker used the supplied TLS-enabled client with the
issued certificate and matching key. The target register, device ID, write
function, starting value, and attempted value matched the original attack:

| Parameter | Follow-up value |
|---|---|
| Starting account | `sfpcm` |
| Gateway | `127.0.0.1:5062` |
| Authentication | Issued client certificate and matching private key |
| Assigned role | `partner_read` |
| Device ID | `1` |
| Holding-register offset | `3` (`40004`, alarm threshold) |
| Read / write functions | `3` / `6` |
| Original / attempted raw values | `250` / `300` |
| Final readback | `250` |

The transport/client changed to support TLS; this was a repeat of the same attack
action, not a claim that the original plain-TCP command was used unchanged.
No private keys or credential contents are included in this report.

#### Attacker-Side Evidence

The attacker supplied the following client output and execution context:

```text
2026-10-14T01:40:24.603537+00:00 Threshold: 250
Write response: 8601 (expected 8601)
Threshold after denied write: 250
Starting account: sfpcm
Gateway: 127.0.0.1:5062
Authentication: your supplied client certificate and key
Device ID: 1
Holding register offset: 3
Write function: 6
Original value: 250
Attempted value: 300
Response: 8601 — write denied
Final readback: 250; no restoration write needed
Time: October 13, 2026, 7:40:24 PM MDT
```

`86` is function 6 with the Modbus exception bit set; `01` means Illegal Function.
This is an explicit rejection, not a timeout or failed authentication. The attempted
value of 300 is established by the attacker's execution record; the gateway denial
log identifies the function and offset but does not include the attempted value.

#### Server-Side Evidence

The supplied plant journal shows deployment at 19:36:19 MDT, a successful initial
read at 19:39:59, and the read/write-denial/read sequence at 19:40:24:

```text
Oct 13 19:36:19 ip-172-26-0-239 systemd[113370]: Started plant-rms-relay.service - CS581 RMS certificate-authenticated read-only Modbus gateway.
Oct 13 19:36:19 ip-172-26-0-239 python[500409]: 2026-10-13 19:36:19,388 INFO rms-gateway read-only Modbus gateway on 127.0.0.1:5062, backend 127.0.0.1:5061; device=1 allowed_functions=1,3 mutual_tls=required approved_certificates=1
Oct 13 19:39:59 ip-172-26-0-239 python[500409]: 2026-10-13 19:39:59,245 INFO rms-gateway client authenticated: peer=('127.0.0.1', 55286) identity=2ed6b19f65c3f2f2b867d3fa88ec580d0bf74dcd0f43f0beee12d9ce726633b6 role=partner_read
Oct 13 19:39:59 ip-172-26-0-239 python[500409]: 2026-10-13 19:39:59,246 INFO rms-gateway decision=allowed peer=('127.0.0.1', 55286) identity=2ed6b19f65c3f2f2b867d3fa88ec580d0bf74dcd0f43f0beee12d9ce726633b6 role=partner_read transaction=1 unit=1 function=3 offset=3 count=1
Oct 13 19:39:59 ip-172-26-0-239 python[500409]: 2026-10-13 19:39:59,247 INFO rms-gateway client disconnected: ('127.0.0.1', 55286)
Oct 13 19:40:24 ip-172-26-0-239 python[500409]: 2026-10-13 19:40:24,602 INFO rms-gateway client authenticated: peer=('127.0.0.1', 58262) identity=2ed6b19f65c3f2f2b867d3fa88ec580d0bf74dcd0f43f0beee12d9ce726633b6 role=partner_read
Oct 13 19:40:24 ip-172-26-0-239 python[500409]: 2026-10-13 19:40:24,603 INFO rms-gateway decision=allowed peer=('127.0.0.1', 58262) identity=2ed6b19f65c3f2f2b867d3fa88ec580d0bf74dcd0f43f0beee12d9ce726633b6 role=partner_read transaction=1 unit=1 function=3 offset=3 count=1
Oct 13 19:40:24 ip-172-26-0-239 python[500409]: 2026-10-13 19:40:24,603 WARNING rms-gateway decision=denied peer=('127.0.0.1', 58262) identity=2ed6b19f65c3f2f2b867d3fa88ec580d0bf74dcd0f43f0beee12d9ce726633b6 role=partner_read transaction=2 unit=1 function=6 offset=3 count=None exception=1
Oct 13 19:40:24 ip-172-26-0-239 python[500409]: 2026-10-13 19:40:24,604 INFO rms-gateway decision=allowed peer=('127.0.0.1', 58262) identity=2ed6b19f65c3f2f2b867d3fa88ec580d0bf74dcd0f43f0beee12d9ce726633b6 role=partner_read transaction=3 unit=1 function=3 offset=3 count=1
Oct 13 19:40:24 ip-172-26-0-239 python[500409]: 2026-10-13 19:40:24,605 INFO rms-gateway client disconnected: ('127.0.0.1', 58262)
```

The UTC client time `2026-10-14T01:40:24+00:00` is October 13 at 19:40:24 MDT
(UTC-6), matching the server journal. Transactions 1, 2, and 3 on the same connection
show an allowed read, denied write, and allowed read. The certificate fingerprint
identifies the approved credential; the `sfpcm` starting account is reported by
the attacker, not independently authenticated as a Linux username by TLS.

#### Follow-Up Result - Blocked

- [ ] **Executable**
- [x] **Blocked** - the gateway authenticated the credential, allowed the threshold
  reads, and denied function 6 at offset 3. Client response `8601` and unchanged
  readback 250 corroborate the server's authorization decision. No restoration
  write was needed.
- [ ] **Untestable**

| Run | Result | Evidence |
|---|---|---|
| October 12, before written policy and enforcement | Executable | Threshold `250 -> 300 -> 250`; RMS write events and SIEM acknowledgements. |
| October 13, after policy design and gateway enforcement | Blocked on port 5062 | Approved credential could read, FC6 received `8601`, final threshold remained 250, and gateway logged the denial. |

**Policy implication and limits:** The follow-up tests the intended read/no-write
boundary for the enrolled SFPCM credential, rather than merely demonstrating
network connectivity or logging an accepted write. It is live evidence of
gateway authentication and authorization, separate from the 24 local tests.
No follow-up SIEM receipt, missing-certificate live test, or direct-backend
isolation test is established by these excerpts. Port 5061 remains a potential
bypass, and the gateway does not implement all seven human roles. The Blocked
result is limited to this tested path and operation, not all access to RMS.

---

## Revised policy items

| Item | Changed / Accepted | Reason |
|---|---|---|
| Attack B dependency review and test scope; policy common rules / limitation 6 | Changed procedurally October 15 | Require reviewed code/configuration and a verified in-scope downstream consumer before a supply-chain test; do not manipulate excluded SIEM records. No new deployment control is claimed. |
| Supply-chain integrity and downstream execution | Accepted, unvalidated gap | B is Untestable: the available probe targets an excluded system, while a permitted consumer was not verified. Local wrapper tests are not connected-system evidence. Deployment separation/signature verification and peer validation require further implementation and authorized testing. |
| Attack A monitoring review; RBAC policy "Common access and change rules" | Changed | Require review of threshold-write values against raw 200-300 and correlation of source journal, SIEM records, and change documentation. Test 301 was visible locally, while stream records 67083-67086 did not expose values or identify a violation. This is a procedural review rule, not a deployed automatic detector. |
| Attack A backend role/range checks and audit fidelity; RBAC policy "What This Policy Cannot Enforce," items 1, 3, and 5 | Accepted gap for this submission | The legitimate RMS account could write 301. Events had no authenticated actor or approval state, and the visible SIEM projection omitted values. Remediation requires controlled maintenance identity, server-side range/approval enforcement, preserved point/value telemetry, and tested detection logic; none is claimed as implemented by this test. |
| SFPCM read/no-write boundary; RBAC policy "Purdue Zone Mapping" and "Required remediation and next tests" | Changed; deployed and retested October 13 | Mutual TLS and an explicit certificate-fingerprint allowlist admit the credential as `partner_read`. Live FC3 reads were allowed and FC6 at offset 3 was denied with exception 1; readback stayed 250. Original October 12 Executable evidence is retained alongside the Blocked follow-up. |
| Gateway attribution; RBAC policy "What This Policy Cannot Enforce," item 5 | Changed | The October 13 journal records the credential fingerprint, role, transaction, function, offset, and decision. This supports credential-level attribution and authorization evidence, not exclusive human identity or demonstrated SIEM ingestion. |
| Direct backend access on port 5061; RBAC policy "What This Policy Cannot Enforce," item 2 | Accepted gap for this submission | Application changes protect the tested gateway path but do not isolate accounts on the shared host. Backend isolation requires administrator-managed access restrictions and a separate test from the SFPCM account; no such control or live result is claimed. |
| Broader human-role coverage; RBAC policy "The Seven Roles" | Accepted gap for this submission | The enforcing gateway assigns only read-only access to enrolled credentials. Implementing the other roles requires additional identity-to-permission mappings and operation-specific enforcement. The seven-role policy is not presented as seven deployed roles. |
