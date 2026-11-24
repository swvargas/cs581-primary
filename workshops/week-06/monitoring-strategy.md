# Monitoring Strategy — Physical Security Integration (PSI)
Santiago Vargas | November 16, 2026 MST / November 17 UTC

## Scope, CCE method, and evidence labels

Consequence-driven Cyber-informed Engineering (CCE) starts with unacceptable physical harm, works backward through the conditions and cyber actions needed to cause it, then places monitoring before and at the protective-function failure. These three priorities require physical-security/operations review; they are not quantified risk rankings or observed physical incidents.

**Method source:** Freeman, St Michel, Smith and Assante, *Consequence-driven Cyber-informed Engineering (CCE)*, Idaho National Laboratory, INL/EXT-16-39212, October 18, 2016, [OSTI 1341416, full report](https://www.osti.gov/servlets/purl/1341416), §2 and §§2.1–2.4, printed pp. 2–5. The four ordered phases are **Consequence Prioritization**, **System of Systems Breakdown**, **Consequence-based Targeting**, and **Mitigations and Protections**. The report includes tripwires within the last phase; CCE is not merely anomaly detection or a list of cyber vulnerabilities.

| INL phase and page | Application in this strategy | Evidence boundary |
|---|---|---|
| Consequence Prioritization, §2.1, pp. 3–4 | Select C1–C3 by potential physical harm to protected assets, people and emergency access. | Proposed priorities require operations/security validation; no harm is claimed to have occurred. |
| System of Systems Breakdown, §2.2, p. 4 | Identify PSI command points, HMI, credentials, telemetry and required physical feedback/dependencies. | Observed endpoints and modeled points do not establish real actuators, independent sensors or emergency-release design. |
| Consequence-based Targeting, §2.3, p. 4 | Work backward from each harm to protection failure, command/logic changes and adversary access requirements. | Pathways remain conditional where permissions, connectivity, product presence or physical behavior are unverified. |
| Mitigations and Protections, §2.4, pp. 4–5 | Place M1–M8 tripwires at authorization, command, receipt-health and physical-function boundaries, alongside proposed access/engineering safeguards. | Monitoring does not replace prevention; independent collection, physical evidence, paging and safe acceptance tests are not presumed installed. |

This is a bounded workshop application of the CCE framework, not a claim to have completed a plant-wide engineering assessment. In particular, the incomplete system/dependency evidence limits confidence in downstream targeting and protection recommendations.

Evidence comes from the [startup gap log](startup-gap-log.md), [received handoff](handoff-received.md), and [received runbook update](runbook-update-received.md). The host runbook was read at `/home/psi/RUNBOOK.md`. PSI is a simulation: returned coil values are not observations of real doors, barriers, people, or material.

- **Observed:** directly returned by the read-only host/HTTP/SIEM checks, with times in the gap log.
- **Documented/source-inspected:** described by the host runbook or earlier recorded source inspection; not necessarily tested runtime behavior.
- **Scenario-only:** attributed to the October 30 exercise; equivalence to lab implementation is unestablished.
- **Proposed:** monitoring/control improvement or response target below; not deployed or acceptance-tested by this work.

## Existing capabilities and their limits

| Capability | Evidence status | What it does not establish |
|---|---|---|
| `plant-psi` and `plant-psi-hmi` active/running; loopback listeners on 5081/5080 | **Observed**, 06:14 UTC | Protective-function correctness, software provenance, or isolation from other shared-host accounts. Cross-account reachability was not tested. |
| Public HTTPS and local HTTP HMI return 401; public TLS verification succeeds | **Observed** | Authenticated dashboard loading, operator functionality, or adequate authorization. |
| FC1 coils and FC3 registers, device ID 1, wire addresses 0–3 respond | **Observed** | Command writes, mechanical behavior, dual-person enforcement, or safe egress. No writes were exercised. |
| Recent SIEM `protocol.read`, `process.alarm`, and `auth.failure` records | **Observed** through the public dashboard stream; samples approximately 301 seconds apart | Complete event capture, event truth, durable retention, paging, or acknowledgment. Authentication failures match our requests but lack independently traced request IDs. |
| Once-per-second coil comparison; approximately 300-tick register export; shared-auth HMI write routes | **Documented/source-inspected** | Transaction-complete audit or attestation of loaded code. Source `protocol.write` labels FC5 without proving the actual transaction function code or writer. |
| Independent transaction capture, physical contacts/video/position monitoring, trusted artifact checks, approval correlation and paging | **Proposed; installation/effectiveness unknown** | These must not be presented as existing protection. |

The received update explicitly says its author did not deploy or test its proposed changes while preparing it. The proposed response replacement was absent from the inspected host runbook; approval/expiry gates were not found in the inspected HMI routes. System-wide or later implementation remains unknown, not proven absent everywhere.

## Top three physical consequences and backward pathways

### C1 — Theft, tampering, or sabotage after unauthorized protected-area access

**Backward chain:** physical harm to material/vital equipment ← unauthorized person reaches it ← access/dual-person protection defeated ← unauthorized release or bypass ← attacker obtains command authority or reaches a command interface. Alarm/camera suppression can conceal access but is not required for entry.

**Interface distinction:** readable Modbus `127.0.0.1:5081` and the HMI authentication boundary are observed. The host map identifies `00001`/wire 0 as door release and `00003`/wire 2 as alarm armed; source inspection describes HMI writes. Actual attacker write access, cross-account reachability and physical entry were not tested. Retained vendor-token use, FHB-02 bypass and camera inhibition are scenario-only; register `40210` is not a verified lab command point. Compromised support identities or substituted dependencies are hypothetical enablers, not current compromise findings.

**Monitoring placement:** support identity/approval before access → independently captured command and approval at the control interface → independent badge/dual-person decision, door contact, camera continuity and material reconciliation at the physical boundary.

### C2 — Injury from unexpected barrier movement, or vehicle intrusion enabling harm

**Backward chain:** person struck or vehicle gains unauthorized access ← unsafe movement/clearance while a person or vehicle is exposed ← malicious barrier command or altered controller logic ← compromised HMI, command-capable local access or substituted software.

**Interface distinction:** the read endpoint is observed; the runbook maps `00002`/wire 1 to barrier clear and `40004`/wire 3 to a modeled cycle counter. Neither physical movement nor independent lane-clearance, position or safety-interlock signals was verified. Real injury/intrusion remains hypothetical and depends on physical conditions and defeated safeguards.

**Monitoring placement:** trusted software/session monitoring before control → command/approval correlation → independent lane occupancy, actual position and safety-interlock feedback during movement. The application counter is corroboration, not proof of mechanical movement.

### C3 — Injury or death from blocked evacuation or delayed emergency response

**Backward chain:** people cannot escape or responders cannot enter ← obstruction persists during emergency demand ← malicious lock/block commands, altered release logic or loss of a required control path ← compromised identity/software or service disruption.

**Interface distinction:** active services and sampled locked/blocking simulation values are observed. Door/barrier commands are documented. Whether cyber control can override emergency release, whether equipment fails safe, and whether mechanical/independent release works are unknown. HMI outage alone does not establish blocked egress; this pathway is conditional on the actual emergency-access design.

**Monitoring placement:** trusted release-logic/configuration monitoring → emergency demand/release request → independently verified contact/position and witnessed egress. A locked indication is not automatically a safe state.

## Proposed monitoring points, thresholds, and rationale

**All rules, collection cadences, timing limits and escalation targets below are proposed design choices, not observed capabilities, legal deadlines, or accepted safety limits.** Validate device latency, travel times, baseline noise and approved operating conditions before commissioning. Existing source events may inform triage but cannot substitute for independent capture/physical evidence.

| ID / consequence | Monitoring points and required improvement | Alert threshold and rationale |
|---|---|---|
| M1 / C1 | `00001` door release and `00003` alarm armed; source events plus **proposed independent transaction audit**, named approval, point, session and allowed window | **Critical on the first unapproved release or alarm disarm**, or a release with lost observation. No burst required: one action can defeat protection. Unknown approval is high pending immediate verification, critical if release/protection impairment is observed. Nearby `auth.success` alone is not approval. |
| M2 / C1 | **Proposed independent** door contacts, badge/dual-person decision and camera-trigger receipt; documented lab `40003` camera alert | Lab `40003=2`: high; `=3`: critical, corresponding to documented 15/45-second modeled stages, not verified intrusion. Missing camera acknowledgment **5 seconds** after a verified release: high, critical when access is unauthorized or observation is lost. Five seconds is an initial latency budget requiring measurement; never wait for this timer when impairment is already known. |
| M3 / C2 | `00002` commands and `40004` counter; **proposed independent** position, lane-clear and safety-interlock feedback | **Critical immediately** for an unapproved barrier command/movement or movement into an occupied lane. Position disagreement exceeding approved travel time plus **2 seconds**: critical; the margin is provisional, not a two-second universal travel limit. Unexplained counter delta: high; calculate modulo 1000 and verify independently before asserting physical movement. |
| M4 / C3 | **Proposed independent** emergency-demand/release input, contacts and barrier position; witnessed emergency-access checks | **Any failed release or verified obstruction during emergency demand: immediate critical voice escalation.** Use engineering-approved release latency for automatic checks; no latency is established here. A human report of blocked egress must not wait for SIEM correlation. |
| M5 / C1–C3 | **Proposed separately administered** FC1/FC3 reader every **1 second**, backend connection checks, service state and approved authenticated read-only HMI health check | **3 consecutive failed reads**: high; synthetic occupancy unchanged across **5 seconds** of successful reads: high health warning, not evidence of people or a physical outage. **2 consecutive failed 5-second application checks**: high. These short windows reject isolated glitches; validate polling load and false-positive rate. Critical when independent evidence shows protective/emergency-access impairment. Expected 401 alone is only an authentication-boundary check. |
| M6 / C1–C3 | **Proposed independent** SIEM receipt/stream-health monitor, source/receipt clocks and durable event archive | No periodic PSI sample for **>360 seconds**: high (approximately 300-second schedule plus 60-second allowance). Claimed/receipt time difference **>2 seconds**: quality warning pending a measured clock/network baseline. Silence means unknown monitoring state, not healthy operation; ordinary samples cannot exclude selective suppression. |
| M7 / C1–C3 | **Proposed trusted host-admin** SSH/session audit, actual protocol transactions and approved package/source/unit manifest; IAM/local-store revocation records | **One unapproved executable/configuration change or command-capable session**: high; critical with protective impairment. Directory-disabled identity accepted locally: critical on first success. Missing revocation acknowledgment after **5 minutes**: high and ticket stays open. Five minutes adopts the received design target; cache/session interfaces and negative tests remain unverified. |
| M8 / C1–C3 | Existing SIEM tamper assertions/clears; **proposed independent** sensor-loop observation and acknowledgment tracking | **One high-severity tamper assertion** opens a high incident; critical with unauthorized access or loss of required protection. Keep it open after a clear until reviewed. The two approximately one-second assertions found in our checks must not be suppressed by a two-sample debounce before their cause is understood. |

Independent means a separate administrative/trust domain, not another script controlled by `psi`. New collectors, transaction capture and physical inputs require authorized engineering; none was installed by this strategy.

## Proposed escalation and acknowledgment targets

| Severity / trigger | Route and immediate action | Delivery, acknowledgment and escalation target |
|---|---|---|
| Critical physical-function impairment | On-duty physical security, shift supervisor/operations and cyber incident lead **in parallel**. Security/operations assess protective coverage, emergency access and safe containment. | Start notification immediately; page delivery **within 60 seconds**, explicit human acknowledgment **within 2 minutes of delivery**. No acknowledgment by two minutes: alternate voice contact; by **5 minutes from first notification attempt**, escalate to shift supervisor/incident coordinator and backup roster. Confirmed life-safety obstruction uses immediate voice action without waiting for any timer. |
| High security/integrity event, including tamper | PSI owner **Santiago Vargas**, monitoring/host administrator, and physical security when protective sensors/access are implicated | Deliver **within 60 seconds**; acknowledgment **within 5 minutes**. Missed acknowledgment: supervisor/incident coordinator by alternate channel. Unresolved **10 minutes from first notification**, recurrence, or corroborating protective change: incident-lead review; upgrade to critical when consequences warrant. |
| High availability/telemetry loss without confirmed physical impairment | PSI owner and monitoring/host administrator; advise security/operations if protective assurance is lost | Same high targets. Confirm monitoring blind spot and request approved independent observation rather than declaring the area unaffected. |
| Informational or correlation-quality warning | Monitoring queue with PSI owner review | Review **within one staffed shift**; escalate immediately if correlated with access, emergency demand or integrity evidence. |

Acknowledgment must name an accountable person, their accepted task, current protective status/unknowns and next review time. Delivery receipts, a SIEM event, automatic ticket creation, and an alarm clear are not human acknowledgment or closure. These are response targets, not permission to leave an impaired area unprotected.

IAM owns directory/local credential and session investigation; network/ICT-SIEM owners own connector scope and dependencies; material control owns inventory reconciliation. The incident coordinator assigns named on-duty leads/backups and routes the **10 CFR §73.77 cyber security event notification assessment** described below to the designated notifier/licensing lead. Dominick Wheeler is the outgoing documentation contact, not a presumed on-duty responder. Missing role names, backup contacts and notification tests are **commissioning blockers**. No page, notification, acknowledgment or protective measure is claimed as completed.

Do not automatically lock doors, move barriers, restart services, disable emergency access, or re-enable a compromised credential/broad connector rule. Any change requires the responsible operational/security owners and an approved recovery path.

### Regulatory basis for “notification assessment”

The rule is **10 CFR §73.77, “Cyber security event notifications.”** Accessible official published sources are the [2026 annual CFR, pp. 597–599](https://www.govinfo.gov/content/pkg/CFR-2026-title10-vol2/pdf/CFR-2026-title10-vol2-sec73-77.pdf) and the [March 30, 2026 final rule, amendatory instruction 160, 91 FR 15871](https://www.govinfo.gov/content/pkg/FR-2026-03-30/html/2026-06048.htm). The annual edition is dated January 1, 2026; read it together with the amendment, effective April 29, 2026, which revises paragraphs (a), (b)(1), (c)(6) and (c)(7). In particular, the amended applicability clause covers licensees subject to **§73.54 or §73.110**; the annual edition alone omits the latter. These sources were checked for this revision on November 23, 2026 and provide the published text supporting the October 30 scenario analysis below. They replace the access-restricted eCFR link without treating the annual edition as a complete point-in-time consolidation. They do not establish what sources were available to the outgoing owner during their earlier review or alter the received document. The rule is not a universal reporting requirement for every security alarm or supplier vulnerability.

| Rule provision | Required action for an applicable licensee when its criterion is met | PSI assessment relevance |
|---|---|---|
| §73.77(a)(1)(i) | Notify within **one hour after discovery** of a cyberattack that adversely impacted the specified safety, security or emergency-preparedness functions within §73.54 scope, including qualifying support-system impacts. | Under the received scenario's licensing/scope assumptions, bypass and camera inhibition warrant assessment of actual security-function impairment. Entry, material loss or actor attribution is not required by this trigger's text. The lab findings do not independently establish this criterion. |
| §73.77(a)(2)(i)–(ii) | **Four-hour** criteria include discovery of an attack that could have caused the specified adverse impacts, or discovery of a suspected/actual attack initiated by personnel with relevant physical/electronic access. | Evaluate the actual facts and scope; do not assume a vendor identity alone proves the actor or automatically selects a reporting category. A one-hour criterion must not be deferred to the four-hour category. |
| §73.77(a)(3) | Notify within **eight hours after receipt or collection** of qualifying information indicating intelligence gathering or pre-operational planning. | Reconnaissance requires its own fact-specific assessment, not a presumption that every read is reportable. |
| §73.77(b), (c)(1), (d) | Applicable 24-hour corrective-action recording; required telephonic notification to NRC Headquarters Operations Center via ENS or the specified alternative; **60-day** written follow-up for notifications under (a)(1), (a)(2)(i) and (a)(2)(ii). | Record actual discovery, category, notification and follow-up evidence. An internal page or Canvas post is not an NRC notification. |

For interpretation, **NRC Regulatory Guide 5.83, *Cyber Security Event Notifications*, July 2015**, ADAMS **ML14269A388**, is available as a [government-hosted copy on Reginfo.gov](https://www.reginfo.gov/public/do/DownloadDocument?objectID=66702701). Its title, date, accession reference and cited printed pages were checked against the previously retrieved NRC document; this is an alternate host, not a newer revision. Pages **4–5** discuss timely assessment and discourage delaying initial notification for final analysis. Section C.1.1, example **c**, p. **5**, specifically identifies adverse effects on intrusion assessment, barriers and access control as security-function examples. This supports evaluating the received bypass/camera-inhibit scenario even without established passage or loss. The guide is explanatory guidance, not a substitute for the regulation (pp. 2–3); its older scope discussion must be read against the published rule and amendment above, which also include §73.110.

**Applicability and evidence limits:** the course simulation is not established to be an NRC-licensed facility, its point map is not proven equivalent to the scenario, and the two short tamper assertions do not by themselves establish a cyberattack or adverse security-function impact. Preserve their claimed/receipt/discovery times and escalate for investigation; the designated notifier/licensing lead must determine actual facility/asset scope, applicable criteria and the legally relevant discovery time. Do not start a hypothetical regulatory clock from a raw timestamp alone or assume a later review resets an already-triggered clock. The 60-second page and two-/five-minute acknowledgment targets above are **internal proposed targets**, not §73.77 deadlines. No actual NRC reportability determination or notification is claimed here, and separate physical-security/safeguards reporting obligations are not resolved by this cyber rule assessment.

## Proposed alert fatigue mitigation

- Notify on the first actionable event, then group repeats by asset/portal and incident for **60 seconds** while retaining all raw records. Re-page on increased severity, a different portal, recurrence after apparent recovery, or acknowledgment timeout. Deduplication must not delay the first page or its escalation timer.
- Enrich events with narrowly scoped approval, named initiator/approver, point and expiry. Label approved activity rather than globally suppressing protection changes. Expired/mismatched approval still alerts; shared HMI authentication alone never authorizes suppression.
- Keep scheduled samples informational. A single simulated badge mismatch warrants contextual review, not an assertion of physical intrusion; correlate repeated mismatches with tamper, release and independent evidence before changing severity. Do not assume unexplained tamper is benign or tune it away because it clears quickly.
- Aggregate collector loss into one visible health incident rather than thousands of stale-point pages. Do not mark dependent streams healthy or auto-close the incident when a single sample returns.
- Weekly, review false-positive rates, missed detections, delivery/acknowledgment latency and unreviewed high events with security/operations. Adjust thresholds only through approved tests and recorded rationale; never require repeated unauthorized release to alert.

## Blind spots and acceptance work

- Once-per-second change detection and polling can miss write/reversion between samples. Source FC5 labels and shared authentication cannot identify the actual transaction/writer. Trusted transaction capture reduces this gap but cannot prove mechanical movement.
- Occupancy is a synthetic modulo counter, not people counting; modeled camera alerts and cycle counts are not independent camera/position evidence. Real contact, lane-clearance, dual-person and emergency-release functions remain unverified.
- HMI 401, active services, normal values and periodic SIEM samples prove neither protective behavior nor recovery. Same-host collectors and hashes can be manipulated by a sufficiently privileged adversary; observed hashes are not approved provenance or loaded-code attestation.
- Scenario cached-token storage, register `40210`, secure OSDP, connector enforcement and support revocation tests are not established lab capabilities. Historical PSI-to-EDGC pivot documentation does not prove current reachability or an EDG consequence.
- SIEM truth, completeness, retention, clock accuracy, page delivery and responder availability are not independently established. Empty local journals do not mean no activity; selected recent receipts cannot reconstruct overwritten entry history or resolve inventory questions.
- The tamper assertions received around **06:05:04/06:05:21 UTC** and sampled badge mismatch were discovered during the later **06:14 UTC** review. Causes, physical significance and acknowledgment remain unknown; clears/current normal values do not close them.

**Before commissioning:** assign named responders; validate point/asset mappings and physical failure behavior; baseline traffic/latency; approve independent collection and retention; and exercise authorized approved/unapproved event cases, telemetry loss, page delivery, acknowledgment failure and safe rollback. Use test identities and a controlled window, without unauthorized entry, real material movement or unsafe actuation. Record measured results and owner acceptance separately from this proposal. Until assurance exists, security/operations decide any required approved guard/observer or emergency-access measures; this document does not claim they were established.
