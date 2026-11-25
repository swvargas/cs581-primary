# Readiness Handoff

## System, owner, date

Santiago Vargas, outgoing PSI owner

Physical Security Integration, or PSI. Prepared November 25, 2026 for the November 25 rotation. Next owner assignment and acceptance remain unconfirmed.

## What this system protects, and why it matters to the plant

Physical Security Integration manages door release, barrier clearance, alarm arming and tamper indications. Its purpose is to protect controlled areas while preserving safe evacuation and emergency access. Wrong commands could allow unauthorized access, unsafe barrier movement or blocked exits. A formal safety classification and actual physical protection have not been established.

## Authorities

Under Section 2.1, authority must be written and agreed. I may inspect assigned PSI services, read values and document findings without changing them. Access does not authorize control changes. Week 7 requires instructor approval in the W7 Incident discussion before changing shared services or touching evidence beyond reading.

These roles are proposed until approved. The network or host administrator may disable a connection with PSI owner agreement and security and operations review of monitoring and emergency access effects. An authorized operator may perform a protective stop or trip through a validated procedure with security and operations agreement. No PSI trip command is established. The host administrator or authorized PSI operator may restart services with security and operations agreement, an approved recovery plan and preserved evidence. Command or setpoint changes need operator and security approval. Credential rotation needs the identity administrator and PSI owner. All changes also require instructor approval. No automatic locking, barrier movement or restart is authorized here.

## What data it produces, and what it does not

Modbus uses device ID 1. FC1 reads coils 00001 through 00004 for door release, barrier clear, alarm armed and tamper. FC3 reads registers 40001 through 40004 for badge result, occupancy counter, camera alert and barrier cycles. Both groups use wire addresses 0 through 3.

PSI sends alarm, authentication and periodic point records to the SIEM. The user service journals are another log location. Retention and complete delivery are unverified. Occupancy does not count people. Returned values do not independently establish passage, camera function, barrier movement or safe exits. Empty journals do not prove inactivity.

## Links to other systems

SSH reaches psi@plant.sanctumsec.com. The public operator dashboard is psi.plant.sanctumsec.com. Its local backend uses 127.0.0.1 port 5080. Local Modbus clients use port 5081. Dashboard and Modbus clients send requests to PSI and receive responses. PSI sends event records outward to the SIEM. Other current connections have not been verified.

## Open items

Tamper assertions 161171 and 161173, followed by clears 161172 and 161175, still need cause and acknowledgment review. Each lasted about one second. Proposed M8 opens a high incident on one assertion and retains it after a clear. Unauthorized access or lost required protection warrants critical escalation. Notify the current PSI owner and host administrator, involving physical security and operations when protection is implicated. Immediate voice contact is needed for blocked evacuation.

The instructor must confirm responders, backups and authority acceptance. Authenticated dashboard access, badge mismatch, credential revocation, approval controls, retention and paging remain open. Earlier bypass incident recovery and physical consequences remain unresolved. Independent collection requires separate administration and remains proposed. The new owner should record accepted tasks and the next review date rather than assume recovery.

## Confidence & Provenance

For continuity under Section 4.4, confirm assignment and obtain access through the instructor. Read /home/psi/RUNBOOK.md before acting. The backend and dashboard user services are `plant-psi` and `plant-psi-hmi`. Confirm service state, ports, point mapping and recent SIEM receipt without restarting. Last recorded checks were November 16 Mountain Standard Time, not a current health check. Both services ran and Modbus responded. Both dashboard endpoints returned HTTP 401, not authenticated access. No control changes were made. Authority roles and M8 remain proposals, not accepted permissions or tested controls.
