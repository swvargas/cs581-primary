# Session Log — Workshop 4
## Santiago Vargas | Codex | October 12-15, 2026

This log records work completed so far for Workshop 4. The original Attack C ran
on October 12 before the written policy; policy design and the enforcing-control
follow-up occurred on October 13. Attack A ran on October 14 after that design.
All systems, identities,
commands, attacks, and process effects described here belong to the authorized CS 581
simulation on the shared plant lab host. They do not describe activity against a
production nuclear facility.

---

## Session 1 — October 12 | Requirements and Pivot Planning

**Estimated duration:** 20 minutes
**Outcome:** Identified the RMS endpoints and translated the Attack C requirement into
a testable path from the SFPCM system.

I reviewed the existing RMS source, systemd units, Workshop 3 brief, and session log.
This confirmed the RMS HMI at `127.0.0.1:5060`, the Modbus/TCP service at
`127.0.0.1:5061`, device ID 1, and the RMS Modbus service as the Level 2 starting
point.

I reduced the plan to a concise coordinated test procedure: connect the two
simulated systems, make one safe change, check whether it is blocked or logged, and
restore it. I verified the port and point details against my own files before sharing
them.

There was an early ambiguity around the phrase "peer link." The Workshop 3 evidence
showed that the earlier DCS peer on port 5051 had responded successfully, so it was
incorrect to describe that historical link as down. The missing connection was the new
Workshop 4 SFPCM-to-RMS pivot. Reading the Attack C instructions changed the question
from troubleshooting an old peer to deliberately building a new path that did not
already exist.

The agreed inbound path became:

```text
SFPCM test client
  -> RMS relay at 127.0.0.1:5062
  -> RMS Modbus/TCP service at 127.0.0.1:5061, device ID 1
```

The RMS allocation is ports 5060 through 5069. Ports 5060 and 5061 were already in
use, so I selected 5062 after planning to confirm it was free on the live host.

---

## Session 2 — October 12 | Relay Implementation and Deployment Preparation

**Estimated duration:** 30 minutes
**Outcome:** Added a persistent loopback-only RMS relay and documented how to deploy
and operate it.

This was the material coding task for which I used Codex. I asked it to create
`workshops/week-03/lab/rms_relay.py`, a small Python `asyncio` TCP forwarder that
listens on `127.0.0.1:5062` and forwards byte streams to `127.0.0.1:5061`. It also
generated `plant-rms-relay.service` so the relay could run as a user systemd service
and restart after failure. I reviewed the bind addresses, ports, startup dependency,
restart behavior, and README commands before using the files.

The implementation was deliberately transparent. It did not add authentication,
roles, function-code restrictions, or register allowlists. That made it suitable for
testing whether the existing RMS access controls enforced the intended boundary,
but it also meant the relay itself could not be described as an RBAC control.

The local environment did not initially have `python3` on `PATH`, so the first syntax
check failed for an environmental reason rather than a code error. Codex used a Nix
Python 3.12 development environment for the syntax check and used
`systemd-analyze verify` on the unit. The unit check produced sandbox-related socket
warnings but no unit-file error. `git diff --check` passed.

I deployed the files through the repository workflow and checked the user service and
listening port on the lab host. The repository briefly diverged because my relay commit
and the remote Workshop 4 setup commit had the same parent. I chose a rebase rather
than an extra merge commit, then verified the resulting linear history before pushing.

---

## Session 3 — October 12 | Authorized Simulated Pivot Test

**Estimated duration:** 1 hour 10 minutes
**Outcome:** Demonstrated an executable SFPCM-to-RMS Modbus pivot, restored the RMS
setpoint, and compared it with a role-enforcing SFPCM HTTP gateway.

The RMS operator and SFPCM attacker coordinated this simulated exercise using the RMS
point map and server code to identify the writable alarm threshold: holding-register
offset 3, Modbus function code 6 for a single-register write, device ID 1. The expected
baseline was 250 raw, or 2.50 uSv/h. We agreed on 300, or 3.00 uSv/h, as the temporary
test value. We required the client to read the actual original first and restore that
recorded value rather than assuming it was 250.

From the `sfpcm` role account, the attacker ran a guarded Modbus client against the new
relay. The client read 250, wrote 300, read back 300, restored 250 in a `finally` block,
and verified 250 after restoration. It saved its timestamped output in
`~/lab/w4-rms-attack-c.txt`. I independently read the value through port 5062 afterward
and also received 250.

The RMS journal recorded two `protocol.write` events at the same time: the test write
and restoration. OT-SIEM acknowledged both events. This demonstrated detection, but
the Modbus messages and RMS event records did not contain an authenticated SFPCM
identity or an authorization decision. The inbound Attack C result was therefore
**Executable**.

During troubleshooting I caught an important wording error: a Python one-liner had
been described as the protocol. I corrected it because the protocol was Modbus TCP;
the Python command was only a client using function code 3 to read the register. I kept
the protocol fields separate from the evidence-collection command in the write-up.

The reciprocal path into SFPCM used HTTP/JSON rather than raw Modbus:

```text
RMS client -> SFPCM gateway at 127.0.0.1:5022
           -> /v1/temperature-alarm
```

An unauthenticated request returned 401. A valid short-lived token authenticated the
simulated identity `santiago-rms` with role `partner_read`. A GET returned 200, but a
POST attempting to change `temperature_alarm_c` returned 403 with decision
`write_denied`. This showed the difference between authentication and authorization:
the token did not automatically grant write access. The bearer token was shared during
live coordination but was intentionally excluded from repository files and evidence.

The reciprocal SFPCM test was **Blocked** by RBAC and provided a useful control
comparison. It did not change the primary result for my Attack C, which is based on the
attacker's successful pivot into RMS.

---

## Session 4 — October 12 | Evidence Review and Attack C Draft

**Estimated duration:** 30 minutes
**Outcome:** Converted the coordinated lab output into the required Attack C structure
and committed the draft.

I collected the attacker's complete client output, my independent RMS read, the RMS and
OT-SIEM journal excerpts, the reciprocal HTTP responses, and the SFPCM gateway
authorization logs. I made the analytical decision to separate the two directions
instead of treating the 403 on the SFPCM gateway as the result of my inbound test.
I used Codex for editorial organization of the evidence after the lab work; the test
plan, test coordination, commands, execution, restoration check, and conclusions
came from my review of the assignment and observed results.

The Attack C draft now documents the Sandworm Unauthorized Message: Command Message
card and MITRE ATT&CK for ICS T1692.001, the Level 1-to-Level 2 boundary, connection
mechanism, loopback ports, test actions, restoration, SIEM evidence, executable result,
and access-control finding. It also explains why the client timestamps show October 13
UTC while the host journal shows October 12 local time.

I reviewed the draft for accidental credential disclosure. The short-lived bearer
token does not appear in the file. The report identifies the attack source by system
and role account, keeping the analysis focused on the technical boundary and evidence.

The evidence showed that loopback binding prevented external exposure but did not
separate role accounts on the shared host once a relay created a path. The RMS logged
the writes but did not authorize them. By contrast, the SFPCM gateway authenticated a
named peer role, allowed its read, and denied its write. This comparison supports a
specific RMS policy revision: an enforcing intermediary should authenticate peers and
authorize reads and writes by role, function code, register, and range.

I committed the Attack C draft as commit `7a2b8fd` with message `Document RMS pivot
adversary test`.

---

## Session 5 - October 13 | Requirements Review and RBAC Policy Draft

**Estimated duration:** 20 minutes (retrospective estimate, not timed).
**Outcome:** Drafted the RMS policy and identified the remaining W4 deliverables.
**Draft status:** AI-assisted reconstruction from this conversation and tool output;
review the wording and time accounting before treating it as a final session record.

I asked Codex to compare the current files with the professor's required order
and then write `rbac-policy.md`. I specifically asked it to reread W4 so the policy
would account for the pivot and reflection already documented. The updated review
recognized the original Attack C as Executable rather than treating the relay code
alone as the evidence.

Codex drafted all seven roles, named the implemented controls, mapped logical
Purdue levels, and distinguished policy restrictions from technical enforcement.
The policy states that the first pivot happened before this written policy was
completed. It does not backdate the policy or claim that the October 12 test followed
the required policy-first sequence.

The draft uses raw 250 as the normal threshold and proposes raw 200-300 as the routine
adjustment band. That band is an AI-proposed simulation policy choice requiring my
review, not a measured physical safety limit or a software-enforced range. We also
clarified that the original test parameters were unchanged: an individual without
ordinary write permission could violate the policy even by writing a value inside
the band. Changing who can write is different from choosing another test value.

Attack A, Attack B, the RUNBOOK, the Purdue annotation, and the secondary synthesis
were still incomplete. The policy is a baseline for those tests, not proof that
they have been performed.

---

## Session 6 - October 13 | Read-Only Modbus Gateway and Local Verification

**Estimated duration:** 45 minutes (retrospective estimate, not timed).
**Outcome:** Replaced transparent forwarding in source with request-level read-only
enforcement while retaining the existing port and service name.
**Draft status:** AI-assisted reconstruction; no live remediation result claimed.

I asked how a read-only credential could make the threshold write fail. Codex
explained that the transparent relay had no authentication or permission check.
I chose to keep the Modbus interface and asked it to implement a read-only gateway.

Codex replaced the implementation in `rms_relay.py` and updated the existing
`plant-rms-relay.service`. The gateway checks complete Modbus TCP frames rather than
assuming TCP reads correspond to requests. It permits device 1 function 3 reads of
holding offsets 0-5 and function 1 reads of coil offsets 0-1. It rejects writes,
including function 6, before forwarding them. A denied threshold write receives
exception bytes `8601` (Illegal Function).

During editing, the transport lookup field was changed from `peername` to an
individual's handle, which produced `peer=None` in the logs. I reported that I had
accidentally undone changes and asked Codex to restore them. It found that the
gateway source had reverted to transparent forwarding, restored the filtering,
and retained `peername` as the connection-address field. A connection address is
not an authenticated identity.

Codex ran isolated tests using temporary listeners and a fake backend. The suite
initially passed 8 tests and expanded to 11, covering reads, denied writes, fragmented
and combined frames, malformed requests, backend failures, and logging. These tests
did not connect to the plant or change its threshold. Local user-unit verification
could not confirm the deployment because the plant-specific `~/lab/.venv/bin/python`
path did not exist on this workstation.

The original Executable Attack C evidence was preserved. Its revision table now
separates later source changes from the historical test result. Direct access to
backend port 5061 remained an identified bypass requiring host-level restrictions.

---

## Session 7 - October 13 | Certificate Authentication and Credential Preparation

**Estimated duration:** 1 hour (retrospective estimate, not timed).
**Outcome:** Added mutual TLS authentication and an explicit client-certificate
allowlist, with read-only permission for admitted identities.
**Draft status:** AI-assisted reconstruction; certificate issuance is not deployment.

I asked how to restrict reads to an approved individual rather than make the endpoint
read-only for every reachable client. Codex added mutual TLS and a SHA-256
certificate-fingerprint allowlist. A certificate must validate against the configured
CA and also appear on the allowlist before any Modbus request reaches the backend.
The assigned role is `partner_read`; no certificate enables gateway writes.

The implementation requires server certificate, server key, CA certificate, and
allowlist configuration. Missing configuration prevents startup. It records the
certificate fingerprint with allowed and denied read/write decisions. The new
`rms_gateway_client.py` verifies the server certificate and can read the threshold
or perform the explicitly authorized write-denial probe.

Codex expanded and ran 24 isolated tests. Missing, untrusted, and trusted-but-
unlisted certificates were rejected. An approved certificate could read but not
write. The supplied client produced a successful read, denial `8601`, and an unchanged
readback against the fake backend. A wrong server hostname was also rejected.

At my request, Codex generated short-lived lab credentials locally, including an
individual's client certificate and private key. OpenSSL verified the certificate
chain, server hostname, and correspondence between the client certificate and key.
The client certificate expires October 20, 2026 at 21:31 UTC. Private keys were mode
600, and the credential directory was ignored by Git. Because the key was generated
on my workstation, this workflow does not establish exclusive custody by the
authenticated individual; generating their own key and submitting a CSR is preferable.

Codex performed one read-only SSH check that reported the existing relay service
as active. That result did not identify the deployed source version or prove TLS was
active. No updated gateway or credentials were deployed by Codex. It provided
deployment commands. At this stage, execution and a live authenticated test had
not yet been recorded; the later evidence appears in Session 9. Backend port 5061
isolation is not demonstrated.

---

## Session 8 - October 13 | Generic Test Runner and Nix Environment

**Estimated duration:** 30 minutes (retrospective estimate, not timed).
**Outcome:** Added a reusable unittest runner and verified the tests in a Nix
development environment.
**Draft status:** AI-assisted reconstruction from the observed build and test output.

I asked Codex for a small generic test script and a flake containing the required
dependencies. It added `scripts/test.sh`, which accepts a test directory and optional
filename pattern, and a development shell with Python 3.12, Flask, Gunicorn,
Pymodbus, Requests, OpenSSL, and Bash. `flake.lock` pins the Nix package source.

My direnv output first showed that Nix could not see the untracked `flake.nix`.
After I added the Nix file to Git, evaluation proceeded but the build failed in
upstream AnyIO tests reached through the Pymodbus package's test dependency chain.
That failure happened before the RMS tests ran; it was not evidence of a gateway
failure.

Codex applied a targeted override disabling Pymodbus's upstream package checks,
not the repository's tests. The flake then built successfully. It ran:

```bash
nix develop --command bash scripts/test.sh workshops/week-03/lab test_rms_gateway.py
```

The output ended with `Ran 24 tests` and `OK`. A separate import check succeeded
for the lab's Python dependencies, the shell script passed `bash -n`, and
`git diff --check` passed. TLS rejection errors in the test output were expected
negative cases, not failed tests. These results establish local behavior only.

The W4 audit still identified A/B, the RUNBOOK, the Purdue annotation, and the
secondary synthesis as unfinished. Passing the gateway tests does not replace
those deliverables or prove a new Attack C result on the live plant.

---

## Session 9 - October 13 | Live Attack C Follow-Up and Evidence Review

**Estimated duration:** 20 minutes (retrospective estimate, not timed).
**Outcome:** Recorded Executable before enforcement and Blocked after enforcement
for the SFPCM-to-RMS path on port 5062.
**Evidence source:** The attacker's client transcript and the supplied plant
service/gateway journal excerpts. Codex organized this write-up;
the live execution is evidenced by those records, not by another local test run.

The professor clarified that the October 12 pivot was valid evidence and should
not be deleted, but it had preceded the written policy. The requested sequence was
to state that chronology plainly, design the intended boundary, then repeat the
same attack after adding enforcement if time permitted. Otherwise, the intermediary
could be listed as an accepted gap with a reason and remediation requirements.
The professor also emphasized that Attacks A/B still need to run against RMS after
policy design and that the operator RUNBOOK remains required.

The October 13 policy defines the SFPCM boundary as authenticated read access to
the alarm threshold with no write permission. It records the original relay as
an unauthenticated path rather than pretending that an authorization control had
already existed. The deployed gateway then provided the enforcing intermediary.

The service journal shows startup at 19:36:19 MDT with mutual TLS required and one
approved certificate. At 19:39:59, it authenticated that credential as `partner_read`
and allowed a threshold read. The attacker repeated the write scenario from the `sfpcm`
account at 19:40:24, using the issued certificate/key and the TLS-enabled client:
device 1, holding offset 3, function 6, original raw 250, attempted raw 300.
The target and operation matched the first attack; TLS support changed the client
transport, not the setpoint-write scenario.

The client printed `Write response: 8601 (expected 8601)` and final readback 250.
The matching gateway connection recorded transaction 1 as an allowed function 3
read, transaction 2 as a denied function 6 write at offset 3 with exception 1, and
transaction 3 as another allowed function 3 read. No restoration write was needed
because the attempted change was denied. The client timestamp
`2026-10-14T01:40:24.603537+00:00` matches October 13 at 19:40:24 MDT (UTC-6).

I retained the original Executable result and added a separate Blocked follow-up
under Attack C. The policy and revision table now describe the deployed and tested
read/no-write boundary rather than leaving it marked as source-only or pending.
The evidence identifies the certificate credential and authorization decision;
it does not prove exclusive human key custody or independently establish the
attacker's Linux username. The starting account is supplied in the attacker's record.

The follow-up is not evidence of SIEM receipt, all negative authentication cases,
or backend port 5061 isolation. Direct-backend access and broader role enforcement
remain documented gaps. Attacks A/B, the RUNBOOK, the Purdue annotation, and the
secondary synthesis are still separate unfinished deliverables.

---

## Session 10 - October 14 | Attack A: Insider Write and SIEM Detectability

**Estimated duration:** 20 minutes (retrospective estimate, not timed).
**Outcome:** Executable insider action, verified restoration, and a demonstrated
difference between source-event detail and visible SIEM information.

I asked Codex to proceed with Attack A after the policy was written. The selected
scenario models misuse of legitimate RMS account access, not a challenge to
authentication. W2 card 5, Maroochy Water Breach Insider / T1692.001, supplies the
insider command-message analogy; it does not establish a historical RMS incident.

Codex checked the policy's raw 200-300 band and the server's writable offset/function
checks. It proposed a small, reversible outside-band value of 301, compared with
an in-band 300 write. These are simulation values, not physical safety limits.
It added a guarded probe that reads by default, requires `--execute` for writes,
stops unless the baseline is 250, and restores the recorded original in `finally`.
Four local mock-based tests passed before the live run, including failure-path
restoration and refusal to write when the baseline is unexpected.

Through authorized SSH as `rms`, Codex confirmed all three RMS services were active,
uploaded only the probe, and read the threshold without changing it. The live run at
`2026-10-14T22:01:52Z` (16:01:52 MDT) completed comparison `250 -> 300 -> 250`,
then insider action `250 -> 301 -> 250`, using FC6 at holding offset 3 on backend
5061, device 1. A separate read at `22:01:57Z` confirmed 250. No service restart,
authentication attack, log deletion, or changes to monitoring were part of this test.

The RMS journal contained four medium `protocol.write` events and four successful
ingestion acknowledgements. Each event used the same message and T1692.001 label;
only the detailed value distinguished 301 from 300. Source identity was null, and
the events carried no approval or policy-violation decision. This verified the AI's
claim that permitted backend addresses/functions do not enforce the policy band:
the readback, not merely a successful connection or event label, proved the write.

An initially assumed SIEM hostname did not resolve. Codex checked only the nonsecret
configured ingestion URL, then inspected the actual public SIEM page to identify
the stream endpoint. It retrieved matching RMS records 67083-67086 independently
of the source acknowledgements. In the observed stream projection, the write values
and actor were absent, target fields were unpopulated, flags were null, and all four
writes had the same medium severity and message. The dashboard showed that writes
occurred, but not which was outside the routine band. This does not prove that no
other SIEM storage or detector exists; it describes what was actually observed.

The complete live output and retrieved event excerpts are in
`adversary-test.md`, under Attack A's Evidence section. The policy/revision table now require procedural
range review and document backend range/role enforcement, identity, approval
context, and centralized value visibility as remaining gaps. Those changes do
not claim automatic detection was implemented. Attack B, the RUNBOOK, the Purdue
annotation, and the secondary synthesis remain outstanding.

After documentation, the generic Nix runner passed all 28 local tests: the four
insider-probe guardrail tests plus the 24 gateway tests. `git diff --check` passed.

---

## Session 11 - October 15 | Due-Date Review, Scope Check, and Handover

**Time:** October 15 MDT, collection around 22:49 onward (October 16 UTC).
Duration not separately timed; not added to retrospective estimates below.
**AI assistance:** Codex inspected source/evidence, performed the read-only
checks listed here, and drafted/updated the remaining deliverables. This entry
records observed tool activity, not invented personal review or partner contact.

The policy already existed before this session; Attack A's October 14 evidence
and Attack C's original/follow-up chronology were retained. No new partner contact,
pivot path, Attack A write, or Attack C retest occurred today.

Before considering Attack B, Codex inspected `attack_b_supply_chain.py` and
found it would change an active service report to inactive in `events.py` and
send false telemetry to OT-SIEM. I had provided the explicit rule that OT-SIEM and
manipulating its records are excluded. The script was therefore not executed,
including its preflight. Source review found no verified alternative in-scope
downstream process consumer: W3 has historical DCS responses, not a persistent
consumer/export loop; the SFPCM records establish the agreed pivot tests, not a
currently available independent consumer. B is documented **Untestable**, not
Blocked by a nonexistent integrity control or Executable based on local mocks.
No SIEM write/query or peer-system request was made for Attack B.

**Plant actions, all through existing authorized RMS access:**

- Ran `ssh -o BatchMode=yes -o ConnectTimeout=10 rms@plant.sanctumsec.com 'hostname; systemctl --user is-active plant-rms plant-rms-hmi plant-rms-relay'`. Output identified `ip-172-26-0-239`; all three units were active.
- Ran the deployed venv interpreter with `-B -c` to perform one FC3 read, offset 0/count 6/device 1, against our `127.0.0.1:5061`. Result `[89, 103, 247, 250, 98, 49970]`; no write was sent.
- In that same SSH invocation, used curl against our `http://127.0.0.1:5060/api/status` without credentials; result HTTP 401. This intentionally creates an ordinary auth-failure event.
- Read the public status board and its advertised `/api/v1/status` endpoint. At generation `2026-10-16T04:49:04Z`, RMS was L2, online, 9/10 with `peer=false`. No other system endpoint was contacted; public aggregate board data is not a peer scan.
- Captured our public HMI. The initial unauthenticated headless image was blank because of Basic auth, so it was replaced, not used as meaningful evidence. A temporary local Selenium helper retrieved only RMS HMI username/password fields from our `~/lab/.env` into private subprocess memory over SSH, supplied an in-memory browser Authorization header, visited our public HMI, allowed normal 3-second polling, confirmed `ONLINE`, and saved `evidence/rms-hmi-auth-2026-10-15.png`. No credential contents were printed or committed. The browser closed afterward. Browser tools ran locally via Nix, not on the lab host.

These reads and HMI requests may create ordinary service-generated auth/read events.
No source/configuration, credentials, units, service states, point values, or logs
were changed on the plant; no excluded host administration, reference-system action,
other home-directory access, SIEM manipulation, or unagreed peer connection occurred.
The precise collection results are preserved below and summarized in
`adversary-test.md` as read-only context, not new attack results.

### October 15 Collection

Collector: Codex for Santiago Vargas. Local date October 15 MDT; UTC date
October 16. These are actual read-only collection results, not a new attack run.

The hostname/user-service command above returned:

```text
ip-172-26-0-239
active
active
active
```

The second SSH invocation performed the FC3 read described above, then ran:

```bash
curl --silent --output /dev/null --write-out 'HMI unauthenticated HTTP %{http_code}\n' http://127.0.0.1:5060/api/status
```

```text
FC3 offsets0-5: [89, 103, 247, 250, 98, 49970]
local backend reachable as rms; no peer-account isolation claim
HMI unauthenticated HTTP 401
```

The public status API generation time was `2026-10-16T04:49:04Z`.
Its exact RMS projection was:

```json
{"level":2,"milestones":{"account":true,"auth":true,"events":true,"files":true,"hmi":true,"login":true,"moving":true,"peer":false,"proto":true,"units":true},"of":10,"online":true,"progress":9,"system":"RMS"}
```

Board labels were SFPCM L1, DCS/RMS/SMR/TCS L2, PSI L3. The public page had no
architecture-page link. Board milestones do not establish RBAC or segmentation.
The temporary screenshot helper was `capture_rms.py`; it used captured
subprocess memory for credentials, as described above, and did not persist them.
The actual image remains `evidence/rms-hmi-auth-2026-10-15.png`.

Local test output was `Ran 31 tests in 2.537s`, `OK`; expected TLS negative-case
errors occurred while tests passed. Four insider guardrail, three mocked
dependency-wrapper, and 24 gateway tests ran without live Attack B telemetry.
Static inspection of `../week-03/lab/attack_b_supply_chain.py` established the
scope issue described above; neither its execution nor its preflight was run.

**AI access-control verification:** I did not accept the source-level claim that
the HMI rejects unauthenticated requests without a check: the live curl returned
401. The FC3 read independently confirmed that the own-account backend path is
reachable and threshold remained 250. Neither check establishes that SFPCM cannot
reach 5061; Codex explicitly rejected equating loopback binding with account
isolation. The existing Attack A readback remains the stronger live verification
that address checks do not enforce the policy's numeric band.

Codex replaced the RUNBOOK and Purdue templates, updated policy/revisions and
B's status, and wrote the secondary role synthesis. The RUNBOOK includes all eight
documented points plus a source-only discrete input, request-triggered model updates
rather than a fictional one-second background task, exact user-service commands,
configuration prerequisites, normal polling, peer distinctions, SIEM losses, and
operator response steps. The Purdue annotation uses the actual board and HMI
screenshot but explicitly discloses that the original architecture page/diagram
was unavailable; the assigned W3 link table is the proxy, not a claimed page review.

Local verification ran:

```bash
nix develop --command bash scripts/test.sh workshops/week-03/lab 'test_*.py'
```

All **31 tests passed**: four insider guardrail, three mocked dependency-wrapper,
and 24 gateway tests. These are isolated tests, not new plant attacks. B remains
an unvalidated permitted-scope limitation, and the architecture source still needs
to be supplied for full rubric coverage. No instructor acceptance or full-credit
claim is made for either gap.

---

## Documentation Consolidation

At the user's request, supporting evidence documents were consolidated into the
required deliverables. Attack A's original commands, client transcript, source
journal, ingestion acknowledgements, and SIEM JSON are now embedded in
`adversary-test.md`; October 15 collection evidence is embedded in session 11
above. The two redundant evidence Markdown files were removed, references in both
repositories updated, and the required HMI image retained. No tests, implementation
files, original evidence values, or live services were changed by this cleanup.

## Additional Read-Only RMS Check

Codex ran this read-only command using existing RMS SSH admission:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 rms@plant.sanctumsec.com 'date -u +%Y-%m-%dT%H:%M:%SZ; ls -1 "$HOME/lab"; journalctl --user -u plant-rms-relay --since "20 minutes ago" -n 30 -o short-iso --no-pager'
```

The host time was `2026-10-16T05:16:52Z` (October 15, 23:16:52 MDT). The
RMS-owned lab directory contained the server, gateway, HMI, probes, certificates
directory, and units, but no additional integration entry point was apparent
in its top-level filenames. The gateway journal query returned `-- No entries --`.
This establishes no recorded gateway traffic during the queried window, not that
SFPCM is down, that the gateway is stopped, or that no peer integration exists.
No peer endpoint, other account's directory, or SIEM endpoint was contacted;
no service, point, source file, credential, or log was changed on the plant.

## Reflection

**What worked:** Starting with the actual RMS source, point map, systemd units, live
client output, and journals kept the test tied to observable facts. The guarded client
made the baseline check and restoration part of the simulated attack rather than an
afterthought. Testing both the unauthenticated and authenticated SFPCM requests clearly
separated 401 authentication failure from 403 authorization denial. Comparing that
gateway with the transparent RMS relay exposed the exact control missing from RMS.

**What did not work:** Early discussion used too much terminology for test
coordination and briefly treated the old peer link as if it were the new pivot. I also
needed to correct the description of a Python command as a protocol. The first local
syntax-check command assumed Python was installed directly, and the first Git pull
attempt created an unfinished merge because the local and remote branches had diverged.
Each issue was corrected before it affected the simulated test or final repository
history.

**What I challenged:** I did not accept a successful TCP connection as proof that a
write occurred. I required the attacker's before/after output, my independent restored
read, RMS `protocol.write` records, and OT-SIEM acknowledgments. I also did not treat a
valid bearer token as automatic authorization; the 200 read and 403 write showed the
actual role boundary. Finally, I kept the reverse SFPCM test as a comparison rather
than using it to replace the assignment's required pivot into my RMS.

**What I would do differently:** I would agree on both directions, protocols, request
formats, roles, safe values, and evidence commands before writing either relay. I would
capture the full, untruncated RMS event JSON during the test and record the relay
journal at the same time. I would also record the attack source account and protocol
parameters before drafting the deliverable and design the RMS enforcing gateway
before exposing a transparent relay.

### October 13 Follow-Up Reflection Draft

The later work separated three claims that are easy to confuse: a written rule,
an implemented control, and a control observed on the live host. A policy can say
that an individual is read-only without enforcing it. A function-code filter can
deny writes without identifying the caller. Mutual TLS plus an explicit certificate
allowlist adds identity checking, but still does not eliminate a direct backend path.

The important corrections were to preserve the original successful attack, disclose
that the policy came afterward, restore accidentally reverted filtering code, and
avoid presenting local certificate tests as a live retest. The proposed threshold
band and these AI-assisted log entries still need my review. Session 9 now adds
separate live evidence: an authenticated read succeeded, a write was explicitly
denied, and the threshold remained unchanged. This supports the intended boundary
on the tested path without erasing the original attack. Completing the other
deliverables and addressing the untested backend route remain separate work.

**Time accounting:**

- Reading requirements, source, and point maps: approximately 20 minutes
- AI-assisted relay implementation and editorial help: approximately 30 minutes
- Coordinated attack planning and simulated testing: 1 hour 10 minutes
- Evidence review and writing: approximately 30 minutes
- October 12 subtotal: approximately 2 hours 30 minutes
- Requirements review and RBAC policy draft: approximately 20 minutes
- Read-only gateway implementation and verification: approximately 45 minutes
- Certificate authentication and credential preparation: approximately 1 hour
- Generic test runner and Nix environment: approximately 30 minutes
- Live Attack C follow-up and evidence review: approximately 20 minutes
- October 13 subtotal: approximately 2 hours 55 minutes (retrospective estimate)
- Attack A preparation, live execution, and SIEM review: approximately 20 minutes
- October 14 subtotal: approximately 20 minutes (retrospective estimate)
- Overall estimated total: approximately 5 hours 45 minutes
