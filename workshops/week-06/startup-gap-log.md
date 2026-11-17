# Startup Gap Log — Physical Security Integration (PSI)
Santiago Vargas | Incoming from Dominick Wheeler | November 16, 2026 MST / November 17 UTC

## What I was handed

Read-only inputs: `handoff-received.md` (especially section 7), `runbook-update-received.md`, and `/home/psi/RUNBOOK.md` on `plant.sanctumsec.com`. Both received files were read before SSH and remain unchanged. The host runbook names Tiffany Fuhrmann as original author and records Dominick's October 28 key cleanup. This is PSI, not outgoing EDGC.

The received documents describe an October 30 **scenario** in which a corporate-disabled vendor identity still authenticated through a local cache, enabled FHB-02 dual-person bypass, and inhibited a camera trigger. They explicitly do not establish passage, material diversion, EDG failure, implemented remediation, or recovery. Register reversion is not closure. Scenario register 40210 and the token database are not established lab interfaces.

## Bringing it up

This is orientation of an already-running simulation, not a cold boot. No restart, command-coil write, key removal, dependency install, credential retrieval, or firewall change was performed.

The 05:49–05:57 UTC entries below are retained from the earlier recorded session. The fresh verification performed for this follow-up is separately recorded under **Read-only re-verification — 06:14 UTC**. Read-only requests can generate access/monitoring records; they do not mean zero observable side effects.

| Discovery / verification time (UTC) | Documented step and actual check | Result and limit |
|---|---|---|
| 2026-11-17 05:49:34 | Existing authorized key, strict-host-key SSH as `psi`; `cat ~/RUNBOOK.md` | Login and host-runbook retrieval succeeded. No new access provisioned. |
| 05:49:47 | `sha256sum ~/RUNBOOK.md` | Inherited baseline: `0e994a242ce088edc435aa0884c768e6002ea86498162dc84ade75d9019b9a08`. |
| 05:49:47 | `systemctl --user show plant-psi plant-psi-hmi` with state/PID/restart/timestamp fields | Both active/running; PIDs 420315 and 316821; zero reported automatic restarts. Systemd reports activation on October 11 and October 4 respectively. These timestamps do not establish deployment history, loaded-code identity, functional health, or protective behavior. |
| 05:49:47 | `ss -ltn` filtered to 5080/5081 | Both listen on `127.0.0.1`, matching the runbook. Binding alone does not prove isolation from other shared-host accounts; actual cross-account reachability was not tested. |
| 05:49:47 collection | Public HTTPS HMI GET, status only | HTTP 401: reachable authentication boundary, not an authenticated dashboard/function check. No Basic-auth credential supplied or extracted. |
| 05:49:47 collection | Last 15 user-journal entries for both units | Returned protocol-debug records dated October 15. Last retained entries are not proof of recent health or absence of subsequent activity. |

## Where the handoff held

- Documented account, units, ports and HTTPS HMI matched observed login, processes, listeners and 401 responses. The SIEM environment-file reference was confirmed, not its contents or successful loading. Dominick is the named documentation contact; his availability/response was not verified.
- Explicitly labeled midterm controls as proposals with acceptance tests, not completion records.
- Warned against translating scenario 40210 into a lab command or declaring recovery from a normal value.
- Distinguished historical SSH cleanup from cached-token revocation and warned about shared-host loopback.
- The host runbook's approximately five-minute SIEM sampling claim was supported by recent received events during the 06:14 UTC follow-up. SIEM authentication-failure records matched both unauthenticated HMI checks, supporting bounded end-to-end reporting, not complete monitoring coverage or independently proven request attribution.

## Where it did not

| Gap | Expected versus found | Status / resolution |
|---|---|---|
| No explicit host runbook path | Startup points mainly to Dominick's GitHub W5 copy; assignment requires the host copy. | Discovered `/home/psi/RUNBOOK.md` by read-only check of the account home; read it successfully. Did not substitute the linked GitHub copy. |
| Authentication-limited HMI acceptance | Runbook requires HMI loading after Basic auth but no specific approved credential-delivery reference accompanies it. | Host-verified 401 only. Obtain credentials through instructor's approved process, not from source or GitHub. |
| Historical header and proposed response replacement | Header says October 11; change log reaches October 28. Old response still says return to resting state through HMI. | Host-verified documentation gap: proposed occupancy/egress-qualified replacement is not in inherited host text. Do not automatically lock portals or raise barriers. |
| Authentication is not authorization | Host text expects preceding HMI `auth.success`, but its emitted-event list names `auth.failure`, not success. Received update correctly warns successful authentication does not authorize an override. | Documentary inconsistency; inspect implementation before relying on correlation. Missing success cannot identify an intruder or writer. |
| Relative incident links do not travel | `technical-analysis.md`, `incident-classification.md`, `rotation-announcement.md`, and `scenario.md` refer to outgoing-repo context, not W6 files here. | Repository-verified portability gap. No extra outgoing analysis was used as startup instructions; scenario assertions remain attributed to received documents. |
| Monitoring acceptance lacks a reproducible receipt check | Startup mentions a `service.state` event on start, but an already-running takeover should not require a restart to prove reporting. | At 06:14 UTC, used the public dashboard's own read-only stream endpoint to confirm existing samples and check-generated `auth.failure` events. This does not verify paging, independent observation, or selective-loss detection. |
| Current alarm disposition is unknown | SIEM returned high-severity tamper assertions followed by clears; no cause, acknowledgment, or response record was established. | Discovered during the 06:14 UTC review. Keep open for PSI/physical-security follow-up; do not call them benign because the current coil is false. These are new observations, not proof the outgoing owner knew of them. |

## What I had to discover myself

Actual host runbook location/hash, its older header, current service PIDs/listeners, and the difference between a reachable auth gate and a verified dashboard. Follow-up implementation/state checks are recorded below. Discovery time is not the time a weakness first existed.

During the 06:14 UTC follow-up I also had to discover the dashboard's public `/api/v1/stream` endpoint from its HTML, distinguish recent SIEM receipt from an empty local journal, and identify tamper events whose review status is unknown. Two authentication-failure records matched our HMI checks in time and description; individual request-to-event attribution was not independently traced. The received package did not provide a dated current monitoring acceptance result.

## First fix for the previous owner

Add one **host-verified startup acceptance block** naming `/home/psi/RUNBOOK.md`, its dated hash, exact read-only FC1/FC3 commands with expected values, and the approved HMI credential-delivery route. End with a capability table distinguishing lab coils from scenario-only cache/40210 controls. This connects a strong incident proposal to a reproducible incoming-owner check.

Include a no-restart monitoring check in that same block: where to retrieve recent PSI events, how to compare claimed event time with receipt time, which check-generated events to expect, and who owns unexplained high-severity events. Explain that an HMI 401 verifies only the authentication gate and may emit `auth.failure`; it is not full HMI acceptance. This is the first documentation fix, not a request to implement all proposed incident controls before clarifying startup.

Canvas question to Dominick (draft, **not posted**): “Can you confirm the host runbook baseline and approved HMI access route, and identify which midterm controls have implementation/acceptance records? I found inherited response text still present. Please provide evidence references, not credentials.” No acknowledgment or answer is invented.

## Verified versus assumed

**Verified on host and public monitoring endpoint:** SSH, inherited runbook/hash, active services, loopback listeners, configured SIEM environment-file references, public/local HMI 401, successful HTTPS certificate verification, responding FC1/FC3 reads, and limited journal output. Recent SIEM samples and two authentication failures matching our checks were retrieved. This establishes partial startup availability and some reporting, not protective-function recovery or complete telemetry.

**Unverified:** scenario/lab equivalence; incident containment and cached-token revocation; physical passage/contacts, dual-person enforcement, egress, camera function, inventory reconciliation, alert delivery and named on-duty responders. Numerical targets remain proposals. Historical attacks are attributed claims, not reproduced tests.

**Evidence limits:** a running service establishes reported process availability, not that the protective function works. Normal sampled coils/registers establish only returned simulation values at those instants, not physical protection, absence of intervening changes, or recovery. The received update explicitly says its author did not deploy or execute the proposals while preparing it. Our checks found the proposed response replacement absent from the host runbook and no approval/expiry gate in the inspected HMI routes; they do **not** prove every proposed control is absent everywhere or exclude later work by someone else. No implementation/acceptance records were obtained. Overall deployment and recovery status remain **unknown/not demonstrated**, not complete.

## Read-only follow-up — 05:52:32–05:52:50 UTC

Source inspection followed the inherited runbook's map; it did not supply a replacement startup procedure. Secret-bearing lines were excluded from displayed output. No code was changed.

| UTC sample | FC3 wire addresses 0–3 (40001–40004) | FC1 wire addresses 0–3 (00001–00004) |
|---|---|---|
| 05:52:46.307738 | `[1,945,0,0]` | `[false,false,true,false]` |
| 05:52:48.308785 | `[1,947,0,0]` | `[false,false,true,false]` |
| 05:52:50.309840 | `[1,949,0,0]` | `[false,false,true,false]` |

Used the existing `~/lab/.venv/bin/python`, `ModbusTcpClient('127.0.0.1', port=5081)`, `read_holding_registers(0,count=4,device_id=1)` and `read_coils(0,count=4,device_id=1)`, two seconds between samples. No FC5/FC15 or other write was issued. Returned coil values map to simulated door locked, barrier blocking, alarm armed and tamper false; the synthetic occupancy counter rose by two per two seconds. Badge value 1 persisted over this four-second interval, shorter than the documented five-second refresh, so this does not establish a stuck reader. These are simulated indications, not observed physical portal behavior or verified protective enforcement.

Earlier recorded source-on-disk findings (not runtime attestation):

- `psi_server.py` lines 145–158 compare coil values once per second and emit changes. The runbook's “every command-coil change” is not transaction-level audit: a write/reversion within a tick can be missed. Its `function_code: 5` field is hardcoded, not independent proof of the actual request's function code or writer.
- Lines 179–191 emit a register sample every 300 ticks. Sample receipt cannot establish monitoring completeness or prove every reconnaissance read was logged.
- HMI source line 94 contains an `auth.success` emission: the runbook's event list omits a source-defined event, not proof the implementation lacks success logging. Routes 171–195 contain shared Basic authentication then coil writes; those inspected routes show no independent approval/expiry gate. No successful login or write was exercised. Source on disk is not attestation of the code already loaded in a long-running process or of every enforcement layer.
- Metadata: pymodbus 3.15.0, Flask 3.1.3, gunicorn 26.2.0. An initial query also requested `requests` and failed because its metadata was absent; a per-package retry confirmed that absence. Server/HMI imports use `urllib.request`; absence of `requests` is not a missing runtime dependency finding.
- Source SHA-256: server `9251508528c089beff80dd48c6ff0f63afb24c18b21bec1eac346242ade4c35d`; HMI `89aedd20d8466eefa251d15d9a6e9a424a093c65b8a3ff0e3b54eff0b55b8920`. Baselines identify inspected files, not approved provenance or clean installation.

### Midterm-control status at takeover

| Received proposal | Actual verification / disposition |
|---|---|
| Effective cached-token revocation within five minutes | **Unknown/not verified in these checks:** scenario cache/identity interface not established in lab; no test identity or live revocation test. This is an assessment limit, not proof the control cannot be verified later. |
| Independently approved, expiring overrides | **Not found in inspected source routes; runtime/system-wide enforcement unknown:** shared auth then direct coil write in those routes. No claim about every possible enforcement layer. |
| Restrict connector and shared-host paths | **Unknown:** loopback binding verified; no cross-system connection test, firewall change, or connector configuration inspection. |
| Protective-function paging, acknowledgment, escalation | **Unknown:** source contains event-emission logic and selected SIEM receipts were observed; page delivery, acknowledgment, escalation and response were not tested. |
| Independent telemetry health and durable reader/latch retention | **Not demonstrated:** inspected source specifies 300-tick sampling and selected SIEM samples were received; no independent collector/contact archive or retention acceptance test verified. |
| Authenticated encrypted OSDP | **Not applicable to this simulated Modbus interface;** physical-reader support unknown. |

Host runbook remains in place and unchanged. Any operational revision should preserve its baseline and add dated implementation/acceptance entries after an approved change, rather than copying proposals into it as completed work. No Canvas tool or actual outgoing-owner answer was available.

The earlier session's final check at **05:57:05 UTC** recorded identical runbook/server/HMI hashes, unchanged service PIDs, active services and zero reported automatic restarts. Those observations do not demonstrate incident remediation. The later follow-up below rechecked the runbook hash and service PIDs, but did not rehash application source.

## Read-only re-verification — 06:14 UTC

On November 17 UTC (November 16 MST), I checked the received instructions against the actual host runbook again. SSH used the existing key with batch mode and strict host-key checking. No `start`, `stop`, `restart`, configuration edit, test alert injection, or Modbus write was issued. No SIEM token, HMI password, or other working credential was read or copied. Python bytecode writing was disabled for the read-only Modbus client.

| Discovery / collection time (UTC, 2026-11-17) | Actual check | Verified result and boundary |
|---|---|---|
| 06:14:11 command batch | Read `/home/psi/RUNBOOK.md`; SHA-256 | Same hash as above. Host text still contains the older resting-state response rather than the proposed egress-qualified replacement. The reading time does not establish when that gap began. |
| 06:14:23 command batch | `systemctl --user show plant-psi plant-psi-hmi` for state, PID, restart count, activation time and `EnvironmentFiles` | Both active/running, PIDs 420315 and 316821, zero reported automatic restarts; activation dates October 11 and October 4 respectively. Both reference `/home/psi/lab/siem.env` with `ignore_errors=yes`: this proves the reference, not that its contents were loaded or are valid. |
| Same batch | `ss -ltnp` restricted to ports 5080/5081 | Python PID 420315 listens on `127.0.0.1:5081`; gunicorn listens on `127.0.0.1:5080`. This matches the runbook, not an enforced boundary between shared-host accounts. |
| Same batch | User journals for both units, preceding 30 minutes, maximum 20 records | `-- No entries --`. No conclusion that no activity occurred: SIEM records below show activity despite the empty journal result. |
| Same batch; SIEM timestamps 06:14:23 | Public HTTPS HMI and local HTTP HMI GETs, response status only | Both 401. Public HTTPS certificate verification returned 0 (success). Authentication boundary and local backend respond; authenticated dashboard and operator actions remain untested. |
| Approximately 06:14:37; stream response `now` field | Public dashboard HTML, then its `/api/v1/stream?limit=10&system=PSI` GET | PSI events returned with `seeded=false`, including recent periodic samples and two authentication failures consistent with our checks. The flag describes the SIEM dataset, not independent proof of event truth. No token or authenticated event API was needed. Dashboard JavaScript was inspected, not browser-render tested. |
| 06:14:38–06:14:44 | Three FC3/FC1 reads, device ID 1, wire addresses 0–3, three seconds apart | Protocol responds and sampled simulated state is recorded below. No physical movement or protection-function test. |

### Current simulated values

Used the existing `~/lab/.venv/bin/python` with `ModbusTcpClient("127.0.0.1", port=5081)`, `read_holding_registers(0, count=4, device_id=1)` and `read_coils(0, count=4, device_id=1)`.

| UTC sample | FC3: badge, occupancy, camera alert, barrier cycles | FC1: door release, barrier clear, alarm armed, tamper |
|---|---|---|
| 06:14:38.291223 | `[1,255,0,0]` | `[false,false,true,false]` |
| 06:14:41.292315 | `[1,258,0,0]` | `[false,false,true,false]` |
| 06:14:44.293370 | `[3,261,0,0]` | `[false,false,true,false]` |

By the documented map, the returned coils indicate simulated door locked, barrier blocking, alarm armed and tamper false **at the three sampled instants only**. Occupancy advanced by three per three seconds, consistent with the synthetic counter. Camera alert and barrier-cycle count were zero in all three samples; intervening values were not observed. Badge result 3 is labeled **biometric mismatch** by the runbook; its cause and duration were not established. It is not proof of a real biometric incident, and the six-second sample does not establish a persistent reader fault. A normal camera-alert register does not verify a functioning physical camera, dual-person enforcement, safe egress, or recovery.

### Monitoring evidence: occurrence versus discovery

All events below were **discovered during the approximately 06:14:37 UTC stream retrieval**, not when they originally occurred. “Event time” is claimed by PSI; “receipt” is recorded by the SIEM. Neither independently proves a physical event or identifies a person.

| PSI-claimed event time (UTC) | SIEM record / receipt evidence | Interpretation and open question |
|---|---|---|
| 06:02:15, 06:07:16, 06:12:17 | `protocol.read` samples, occupancy 514, 814, 114; receipt timestamps within roughly one second of claimed seconds | Approximately 301-second spacing supports scheduled reporting. Counter wraps are consistent with the map. This is not an audit of every client read or evidence that no events were selectively suppressed. |
| 06:05:04 | High `process.alarm`, tamper true, ID 161171; receipt 06:05:04.184 | Unexplained reported tamper assertion received before our 06:14 checks; not attributable to those later requests. Underlying physical/simulated cause and acknowledgment unknown. |
| 06:05:05 | Tamper cleared, ID 161172; receipt 06:05:05.243 | Reported clear about one second later does not prove investigation or recovery acceptance. |
| 06:05:21 | High `process.alarm`, tamper true, ID 161173; receipt 06:05:21.318 | Second unexplained reported assertion; same follow-up needed. |
| 06:05:22 | Tamper cleared, ID 161175; receipt 06:05:22.376 | Current false coil is compatible with the clear but cannot establish the earlier cause. |
| 06:14:23 | Two medium `auth.failure` records, IDs 161183/161184; receipts 06:14:23.130 and 06:14:23.194 | Both say “HMI request with no credentials,” matching our public and local requests in count, time and description. This supports bounded HMI-to-SIEM reporting and expected logging side effects; no unique request identifier independently ties each record to a particular request. It does not establish an unknown intruder or complete event delivery. |

**Follow-up, not completed action:** ask the outgoing documentation contact about known simulated tamper behavior and ask the PSI/physical-security or instructor role to review the two high-severity events, their acknowledgment history and the sampled badge mismatch. No answer, page, Canvas post or operational response was obtained in these checks. Assign named owners and review times rather than inventing them here.

### Takeover conclusion

The documented services, ports, authentication boundary, Modbus reads and some recent SIEM reporting are verified. Full authenticated HMI acceptance, complete/independent monitoring, paging, incident containment and actual physical protection are not. The October 30 scenario remains attributed historical context; no result here closes its physical-entry or inventory questions. Both received files and the host runbook remain unchanged; this update changes only my startup gap log.
