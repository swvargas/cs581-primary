# RBAC Policy - Radiation Monitoring System (RMS)
## CS 581 Workshop 4 | Santiago Vargas | October 15, 2026

**System:** Radiation Monitoring System (authorized CS 581 simulation)
**Purdue Zone:** Level 2
**Role account on plant host:** `rms` on `plant.sanctumsec.com`
**HMI:** `https://rms.plant.sanctumsec.com`, backed by port `5060`
**Modbus TCP:** `127.0.0.1:5061`, device ID `1`
**Read-only authenticated gateway:** mutual TLS at `127.0.0.1:5062`, validated Modbus reads to port `5061`

---

## Overview

RMS displays simulated radiation, detector status, and a high-radiation alarm. This
policy protects the integrity of its alarm threshold, availability of monitoring,
and evidence sent to OT-SIEM. Changing the threshold can change whether an alarm
appears without changing the radiation reading. Access to a host account, network
port, or HMI credential therefore must not imply permission to change every point.
These rules apply to the course simulation, not to a production radiation detector.

**Chronology:** The October 12 SFPCM pivot was performed before this policy was
completed; it was not a test of a policy that already existed. Following the
professor's clarification, the policy was written on October 13 to define the
intended boundary, then enforcement was added and Attack C was repeated at
19:40:24 MDT. The original run remains Executable; the follow-up was Blocked on
the gateway path. This is a post-retest revision, not a claim that the current
controls existed on October 12. Attack A ran against RMS on October 14 after the
design step: the legitimate account wrote 301 and restored 250. Attack B was
classified Untestable on October 15: its prepared probe would manipulate excluded
SIEM records, and no permissible downstream consumer was verified.

### Design baseline and intended boundary

Before remediation, SSH keys controlled admission to the shared `rms` account,
the HMI checked one Basic-auth credential pair, and Modbus bound to loopback.
The relay on 5062 was an unauthenticated byte-forwarding path to 5061: neither
authenticated the SFPCM caller or enforced read-only peer access. Recording that
actual enforcement does not authorize those writes. The intended boundary is
that an authenticated SFPCM individual may read the alarm threshold but may not
write it; a valid credential or reachable endpoint must not imply write access.
The role rules below state permitted responsibilities independently of whether
the original attack succeeded. The October 13 gateway is enforcement added after
that design, and its observed limits remain documented below.

### Common access and change rules

- Deny actions not explicitly allowed below. Peer systems, including SFPCM and DCS,
  receive read-only access to the documented RMS status points unless a separate,
  time-bounded lab exercise explicitly authorizes a test write.
- Normal threshold is raw `250` (2.50 uSv/h). This policy selects raw `200-300`
  (2.00-3.00 uSv/h) as the permitted routine adjustment band for the simulation.
  This is a new lab policy choice, not a physical safety limit or a currently
  enforced software range. Changing it requires supervisor approval and a policy
  revision; an exceptional test outside it requires explicit scope and restoration.
- Only an approved maintenance action may write `alarm_threshold` at holding
  register `40004` (offset `3`), using function code `6` or a one-register function
  code `16` request. The operator may acknowledge an observed alarm through coil
  `00001` (offset `0`), using function code `5` or a one-coil function code `15` request.
- Radiation, count rate, temperature, health, sample counter, and the derived alarm
  state are read-only. Acknowledgement is not permission to suppress an alarm or
  change its threshold. The current HMI exposes reads, not acknowledgement writes.
- Before an authorized write, record the actor, approving person, purpose, time,
  endpoint, and original value. Read back the result. For a temporary test, restore
  the recorded original even if the test fails, then verify restoration.
- When investigating threshold changes, review source `protocol.write` values
  against raw 200-300 and correlate them with SIEM records and the change record.
  An outside-band value requires investigation even if its event has ordinary
  write severity. The October 14 test showed that the visible SIEM stream omitted
  the value and did not distinguish the prohibited action. This is a procedural
  review requirement, not an existing automatic alert or actor-attribution control.
- Add SSH keys only for approved access and retain a fingerprint-to-person record.
  Review access before handoff and remove keys when their approved work ends.
  Temporary vendor or test access must have a recorded end time. These reviews and
  removals are procedural requirements; automatic expiry is not implemented.
- Keep HMI passwords, SIEM tokens, and peer bearer tokens out of Git and evidence
  excerpts. Never fabricate telemetry, erase evidence, or disable logging to hide
  an action. Review dependencies and configuration changes before deployment.
  Verify an in-scope downstream consumer before supply-chain testing. Never run
  the prepared false-SIEM-telemetry probe; a test marker does not authorize it.

The following roles are policy responsibilities, not seven deployed Linux accounts
or seven implemented HMI roles. Where enforcement is missing, the mechanism field
states that explicitly.

---

## The Seven Roles

### 1. Plant Operator

**Allowed:** Read the HMI and documented process points, report abnormal readings,
and acknowledge an observed alarm through an approved local client.

**Not allowed:** Change the alarm threshold, stop services, install software, edit
access keys, alter detector readings, or delete logs.

**Mechanism:** HTTP Basic authentication gates the HMI's `/` and `/api/status`
routes; those routes only read Modbus data. The Modbus server permits writes to the
acknowledgement coil but does not verify that the caller is an operator. Operator
shell access is not required for HMI viewing and must not be granted by default.

### 2. Supervisor

**Allowed:** Read RMS status, approve maintenance and test windows, approve threshold
adjustments within the policy band, and review restoration and incident records.

**Not allowed:** Treat approval as unrestricted shell access, silently widen the
threshold band, bypass change records, or suppress monitoring evidence.

**Mechanism:** The authenticated HMI provides viewing. Approval is a recorded
procedural decision; neither the HMI nor Modbus checks supervisor approval or
implements a separate supervisor role.

### 3. Cybersecurity Manager

**Allowed:** Review RMS/SIEM evidence through separately authorized access, maintain
the access inventory, approve scoped security tests, and coordinate containment
with the supervisor and system owner.

**Not allowed:** Perform unapproved process writes, invent SIEM events, disclose
credentials, erase logs, or assume monitoring access grants control of RMS.

**Mechanism:** Approved keys in `rms`'s `~/.ssh/authorized_keys` gate SSH access;
user-service journals provide local evidence. SIEM viewing requires its own access
grant and is not established by possession of the RMS ingestion token. The shared
`rms` account does not technically restrict a security reviewer to read-only work.

### 4. Maintenance Technician

**Allowed:** During an approved window, operate RMS user services, deploy reviewed
code/configuration, and adjust the threshold within raw `200-300`. Record before
and after values and verify monitoring after any restart or temporary test.

**Not allowed:** Make out-of-band or unapproved threshold changes, make protocol
ports public, modify unrelated systems, install unreviewed dependencies, or disable
logging to conceal maintenance.

**Mechanism:** An authorized SSH key grants the shared `rms` account access to its
files and user systemd services. The Modbus handler restricts writable addresses
and function codes, but does not enforce the maintenance role, approval window,
or numeric band. Those restrictions remain procedural in this build.

### 5. Vendor / Contractor

**Allowed:** Supply reviewable code or configuration and perform explicitly scoped,
supervised diagnostics. If status access is approved, read only the agreed points.

**Not allowed:** Receive standing RMS shell access by default, write process points,
change keys or services, retrieve tokens, or deploy vendor material without review.

**Mechanism:** Withholding or removing the vendor's key from `authorized_keys`
controls direct SSH admission to `rms`. It does not prevent access from another
account on the same host to loopback Modbus. The replacement gateway restricts
port 5062 to documented reads from trusted, explicitly allowlisted client
certificates. Do not enroll vendors by default. Direct access to 5061 remains a
bypass. Review and timely SSH key/certificate allowlist removal are manual.

### 6. Emergency Response

**Allowed:** Read status and alarm information, preserve evidence, notify the
supervisor and cybersecurity manager, and coordinate an approved response.

**Not allowed:** Raise the threshold to make an alarm disappear, clear evidence,
change simulated readings, or claim emergency status grants unrestricted control.

**Mechanism:** HMI authentication permits viewing; no separate emergency role or
break-glass authorization exists. Any required service intervention uses explicitly
approved maintenance/administrative access and a recorded decision.

### 7. IT Administrator

**Allowed:** Within assigned host authority, maintain SSH admission, HMI credential
configuration, RMS user-service configuration, dependencies, and loopback bindings.
Coordinate service-affecting changes and access revocation with the system owner.

**Not allowed:** Use infrastructure access as permission to change process setpoints,
share secrets, expose Modbus publicly, alter peer systems without authorization,
or erase audit evidence.

**Mechanism:** SSH keys and filesystem ownership control entry to and modification
of the `rms` account's files; user systemd units control its services. Host-wide or
privileged changes require separately granted host-administrator authority. This
policy does not assume that `rms` has sudo or that its effective privileges have
been verified. Administrators able to edit the application can bypass its controls.

---

## Purdue Zone Mapping

These levels describe responsibilities and logical flows. They are not separate
network segments on the shared plant host.

| Role | Logical level | Permitted interaction with RMS Level 2 |
|---|---|---|
| Plant Operator | Level 2 | View status and perform approved alarm acknowledgement. |
| Supervisor | Levels 2-3 | Review status and approve work; no automatic write grant. |
| Cybersecurity Manager | Level 3 | Review evidence and coordinate scoped tests/containment. |
| Maintenance Technician | Levels 1-2 | Perform approved RMS maintenance; no implied control of peer Level 1 systems. |
| Vendor / Contractor | External to the OT zones | Enter only through explicitly approved, supervised access. |
| Emergency Response | Levels 2-3 | View alarms and coordinate response without unrestricted writes. |
| IT Administrator | Level 3 / host infrastructure | Administer assigned infrastructure without process-control authority by default. |

| Connection | Policy permission | Actual control and limitation |
|---|---|---|
| HMI viewer to RMS Level 2 | Authenticated status viewing only. | HTTPS routing is specified by the lab; the application checks Basic credentials and serves read-only routes. One credential pair does not distinguish the seven roles. |
| SFPCM Level 1 to RMS Level 2 via `5062 -> 5061` | Only enrolled client certificates get `partner_read`; read the threshold, no gateway writes. | On October 13, the deployed gateway authenticated the enrolled credential, allowed FC3 reads at offset 3, and denied FC6 with exception 1; threshold stayed 250. This follows the preserved October 12 Executable result. Direct port 5061 isolation remains unverified. |
| DCS to RMS, logical Level 2 peer link | Read documented RMS status; no threshold or acknowledgement writes. | The W3 brief specifies an RMS-to-DCS telemetry link. An intended read-only relationship is not enforced by raw RMS Modbus; do not assume every planned direction was demonstrated. |
| RMS to OT-SIEM, supervisory monitoring | Send truthful service, authentication, protocol, and alarm events. | The ingestion token identifies an event source, not the human actor or truth of its report. SIEM acknowledgements evidence receipt, not write authorization. |

The reciprocal RMS-to-SFPCM gateway test is a comparison, not an RMS control:
SFPCM authenticated `santiago-rms` as `partner_read`, allowed a GET, and denied a
POST with `403 write_denied`. RMS must not claim that this authenticates its own peers.

---

## What This Policy Cannot Enforce

1. **Shared account, not seven-role RBAC.** An accepted SSH key grants the `rms`
   account rather than a restricted job function. SSH fingerprints can support
   login attribution if mapped to people, but Modbus actions are not linked to them.
2. **Unauthenticated backend and incomplete role coverage.** Port `5061` still
   accepts unauthenticated Modbus. The replacement gateway requires a CA-verified,
   allowlisted client certificate and assigns only `partner_read`; it does not
   implement the seven human roles. Certificates identify possession of private
   keys, so sharing a key destroys person-level attribution. Direct backend access
   bypasses gateway authentication and filtering.
3. **Address controls do not enforce role or range.** The server restricts writes
   to threshold offset `3` and acknowledgement offset `0` with the listed function
   codes. It has no explicit check for raw `200-300`, maintenance approval, or peer
   read-only permission on the backend. The gateway denies every write on port 5062,
   regardless of value. Attack A demonstrated a backend write of 301 outside the
   routine band, followed by restoration. A value inside the band can still be an
   unauthorized backend write.
4. **HMI authentication is shared.** One configured username/password pair gates
   read-only routes; it does not implement per-person permissions, MFA, expiry, or
   lockout. Changing the password affects everyone using it.
5. **Detection is not prevention.** Accepted writes generate events, but those
   events do not contain an authenticated client identity or authorization
   decision. The TLS gateway separately logs certificate identity and allowed/
   denied commands in its journal, not directly to SIEM. Delivery failures,
   sampled reads, and self-asserted events limit completeness and trust. TLS
   handshake failures happen before the handler; retain client-side evidence too.
   Attack A's four writes reached the live SIEM stream, but its visible projection
   omitted the source values and actor, showed no populated target, and gave all
   four the same severity/message with null flags. The RMS journal can support a
   manual range comparison; no dedicated outside-band alert was demonstrated.
6. **Trusted code and configuration can defeat controls.** The account that edits
   RMS source, dependencies, environment, or units can change behavior and emitted
   telemetry. A vendor file or dependency is not trustworthy merely because it
   loads successfully. Attack B remains unvalidated: the prepared probe targeted
   excluded SIEM telemetry and was not run. A permitted receiving consumer must
   be verified before testing this trust assumption; local mocks are insufficient.
7. **Approvals and access review are manual.** The build does not enforce
   separation of duties, two-person approval, SSH key expiry, or safe restoration.
   TLS checks certificate validity dates, but early revocation requires removing
   its fingerprint and restarting the gateway to terminate existing sessions.
   There is no automatic configuration reload or CRL/OCSP integration.

### Required remediation and next tests

The transparent relay has been replaced by a read-only Modbus gateway using the
existing service and endpoint. The supplied live journal records startup on
October 13 at 19:36:19 MDT and the coordinated retest at 19:40:24 MDT. Port 5062
requires mutual TLS: the certificate must validate against the configured CA and
its SHA-256 fingerprint
must be explicitly listed in `RMS_GATEWAY_CLIENT_SHA256`. No plaintext fallback
exists. Each approved certificate receives only `partner_read`. The gateway
validates complete Modbus TCP frames and permits only device 1 function 1 reads
of coil offsets 0-1 and function 3 reads of
holding offsets 0-5, and rejects writes with Illegal Function without forwarding
them. Decisions and certificate identity are recorded in the service journal.
The 24 local tests verify authentication and filtering in isolation. Separately,
the Attack C follow-up contains live client output and journal evidence of an
authenticated read, denied function 6 write, and unchanged final threshold 250.

This is partial remediation. Broader role coverage and enforced restrictions on
direct backend access remain outstanding. Protecting only `5062` is insufficient
while peers can reach `5061`. Approved maintenance
writes use the backend, not a gateway exception; the read-only gateway has no
credential or override that enables writes.

Attack A verified legitimate-account misuse and compared the observed SIEM records
with the detailed source events. Backend role/range checks, approval context,
identity attribution, centralized value visibility, and automatic detection remain
accepted gaps requiring separate implementation and validation. Attack B is
Untestable in the verified current scope, not proof of dependency integrity. A
future test must use a permitted downstream consumer, never false SIEM telemetry. The Attack C
follow-up verifies the enrolled credential's read/no-write
boundary on 5062, not blanket protection of RMS. Live rejection of missing,
untrusted, and trusted-but-unlisted certificates remains unverified by the supplied
logs, although covered by local tests. Separately verify whether direct backend
access is blocked. Record each result, then update specific policy sections or
explicitly justify accepting the remaining
lab gap in `adversary-test.md`.

### Evidence and implementation references

- `session-log.md`, Sessions 3-5 and 9: original test, policy design, and live retest chronology.
- `adversary-test.md`, Attack C: SFPCM client output, RMS/SIEM acknowledgements,
  reciprocal gateway authorization results, and October 13 Blocked follow-up.
- `adversary-test.md`, Attack A Evidence: live insider test, restoration, full source
  write records, ingestion acknowledgements, and independently retrieved SIEM records.
- `../week-03/README.md`: RMS allocation, SSH ACL, intended links, and bind rules.
- `../week-03/points.md`: point names, addresses, device ID, and scaling.
- `../week-03/lab/rms_server.py`: writable-point restrictions and event generation.
- `../week-03/lab/hmi/app.py`: Basic authentication and read-only HMI routes.
- `../week-03/lab/rms_relay.py`: certificate-authenticated read-only Modbus gateway.
- `../week-03/lab/TLS_SETUP.md`: certificate enrollment, configuration, and authenticated client probe.
- `../week-03/lab/test_rms_gateway.py`: isolated authentication/filtering tests, not live attack evidence.
