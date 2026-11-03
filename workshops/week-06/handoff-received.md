# Midterm Stakeholder Communications — PSI

Dominick Wheeler | CS 581 | Prepared November 1, 2026

**Status: exercise drafts; not sent.** These notes describe the response I would coordinate at scenario discovery on October 30. Preparation on November 1 does not establish that any earlier communication, notification, containment action, or test occurred. Requests below are proposed actions, not completed work.

The evidence basis is the [scenario and Artifacts A–C](https://github.com/DomArmWheel/CS581-Primary/blob/main/workshops/midterm/scenario.md), with interpretation and prior-work references in [technical-analysis.md](technical-analysis.md). Reporting decisions and their applicability/currency limitations are in [incident-classification.md](incident-classification.md). Proposed changes are in [runbook-update.md](runbook-update.md).

The [instructor rotation announcement supplied November 2](rotation-announcement.md) now confirms Sindi Banda as current SFPCM owner, Santiago Vargas as current EDGC owner, and Dominick Wheeler as current PSI owner. On November 3, Santiago receives PSI from Dominick, Dominick receives EDGC from Santiago, and Tamas Gyalay receives SFPCM from Sindi. These confirmed assignments supersede the earlier uncertainty based only on W5 contacts. ICT-SIEM and plant support-role assignees remain unspecified. All incident timestamps below are UTC on October 30, 2026.

## Recipient coverage and routing

| Implicated function | Note | Ownership basis |
|---|---|---|
| ICT-SIEM connector / Level 3–4 boundary | 2 | Directly implicated in B and the scenario; current person not supplied. |
| SFPCM | 3 | Directly implicated; Sindi Banda is confirmed current owner; Tamas Gyalay receives SFPCM November 3. |
| PSI / FHB-02 | 4 and 7 | Dominick Wheeler owns PSI now; Santiago Vargas receives it November 3, per the instructor roster. |
| EDG-room interlock information / EDG operations | 5 | Read exposure in A; no EDG compromise established. Santiago Vargas currently owns EDGC; Dominick receives it November 3. |
| SNM inventory / accounting assurance | 6 | Affected inventory window; no accounting-system compromise established. Route through material control, who should involve the actual records-system owner. |
| Overall response decisions | 1 | Plant manager/incident lead is an exercise role, not an identified classmate. |

For a live coordination cycle, the incident lead should route missing-name notes immediately by system role, request acknowledgment and a first findings/ETA response at the initial briefing, and assign the next review time. Missing names must not delay escalation. Those proposed milestones are not regulatory deadlines or claims that messages were sent.

## 1. Plant manager / incident lead

**Subject: Confirmed PSI protection impairment during inventory; physical consequences unresolved**

At the scenario's recorded discovery time, 03:14, PSI evidence showed that a contractor credential disabled in corporate AD had successfully authenticated through PSI's local token cache. The controller recorded an FHB-02 dual-person bypass and adjacent camera-trigger inhibition from 02:41:28 to 02:52:19, overlapping an SNM inventory window. The register subsequently returned to its normal value; that alone does not demonstrate recovery of the system or physical security.

The confirmed consequence is impaired access protection and observation. We have not established that anyone entered, that material moved, that accounting records changed, or that cooling or emergency power was impaired. Fourteen reader-link frames are routine supervision traffic, not evidence of passage. The overwritten badge buffer and absent latch records limit reconstruction.

I request assignment of an incident coordinator and designated regulatory notifier, with physical security, operations, cyber response, and material control participating. Please have the responsible leads establish appropriate protective coverage, assess whether inventory activity should continue, preserve remaining evidence, and coordinate access-path containment through validated procedures. Protective actions must account for emergency egress.

The classification draft identifies an actual-impact cyber reporting basis under its stated licensing assumptions. Route that assessment immediately to the designated notifier; actor attribution and final inventory reconciliation should not delay assessment of the already-established impairment. Additional safety, physical-security, and safeguards criteria remain conditional. This note is an internal escalation draft, not an NRC notification or proof that a call occurred.

Please return the assigned owners, actions authorized, actual action times, unresolved decisions, and the next briefing time. Status reporting should distinguish confirmed protection impairment from still-unresolved physical and material consequences.

## 2. Current ICT-SIEM owner / network boundary owner

**Subject: Preserve connector evidence and coordinate containment of FW-RULE-309**

Artifact B records permitted traffic from `ict-siem-conn01.L4` (`10.40.12.88`) toward SFPCM at 02:39:04 and PSI at 02:41:11 under `FW-RULE-309`. The rule is described as a temporary collector exception that never expired. Artifact A records successful PSI cached-token authentication from the same source one second after the PSI allow event. The scenario identifies the active-response connector as part of the campaign path.

Please preserve the rule's approval/change/expiry history, connector configuration and session audits, identity-use records, relevant network records, and SIEM event 124802 with alert delivery/acknowledgment history. Include source clock information and collection provenance. Preserve sensitive credentials through approved evidence handling; do not put working tokens in the repository.

Please identify the required telemetry flows and propose a bounded restriction of the unauthorized response path and associated sessions, with rollback and continued monitoring verified. Confirm whether other destinations or identities were exposed. An `ALLOW` record alone does not establish application success, and these excerpts do not prove an SFPCM-originated pivot to PSI. Please report what your records actually establish about that intermediate path.

My W1 maps identified boundary-rule and automation risks but did not verify reverse reachability or a hardware diode. The scenario now supplies the widened-path fact. Please return preserved evidence references, confirmed scope, proposed containment, and any monitoring dependencies before a coordinated change is approved.

## 3. Sindi Banda — current SFPCM owner

**Subject: Verify SFPCM consequences independently of the PSI override**

Sindi, please carry any unresolved SFPCM findings into your November 3 handoff to Tamas Gyalay. Your current assessment is needed for this incident; the rotation does not itself resolve it.

The scenario states that the campaign enumerated SFPCM process/tag metadata. Artifact B corroborates permitted connector traffic to `10.20.14.22:502` at 02:39:04, but supplies no application response, enumeration output, or SFPCM write. We therefore cannot infer a cooling change or loss from that record.

Please preserve gateway/controller authentication, read/write and configuration histories, and any relevant maintenance approvals. Compare contemporaneous temperature, level, flow, pump/valve state, and alarm indications with available independent sources. Cover the known campaign interval and sufficient surrounding history to establish a baseline; document unavailable sources and clock uncertainty.

My W4 SFPCM tests showed that an authenticated maintenance role could change a threshold without enforced approval, that an HMI could display biased data in a simulated update attack, and that tested gateway restrictions could block particular writes. Those are reasons to check authorization and independent indications; they are not evidence that those attacks occurred here or that every alternate path is blocked.

Please return a supported statement of whether control changes or functional impairment were found, the observation interval and sources, and remaining limits. Escalate any newly discovered safety-function concern to operations and the incident lead with its discovery time. A lack of retained evidence should be reported as unknown, not as proof of unaffected operation.

## 4. Physical-security lead / IAM owner

**Subject: Verify FHB-02 protection and effective revocation across credential stores**

Artifacts A/C show that `svc_maint_vendor04` authenticated through PSI's cached-token mechanism despite corporate disablement documented in `IAM-4418`. The cache's last recorded synchronization was October 4. The override weakened dual-person control and inhibited the adjacent camera trigger; the supplied records do not establish physical entry.

Please coordinate independent verification of portal protection, badge-group permissions, observation coverage, occupancy, and emergency egress. The badge-group override is stipulated by the scenario; A does not supply its complete configuration diff. Preserve any separately retained camera, access-decision, door-contact, guard, and inventory-team evidence before further loss. The routine OSDP frame count cannot substitute for a passage record.

For IAM/PSI coordination, identify all applicable credential stores and active sessions, preserve relevant metadata, and propose effective local revocation and session invalidation through supported interfaces. My W5 removal of obsolete SSH keys did not establish removal of this separate cached service token. Ticket closure and the normal register value are insufficient recovery evidence.

Please return the verified protection state, compensatory measures actually authorized or established, effective-revocation evidence, and unresolved gaps. Do not report the proposed runbook acceptance tests as completed tests.

## 5. Santiago Vargas — current EDGC owner, with operations

**Subject: Check scope of EDG interlock reconnaissance; no EDG failure established**

Santiago, this request addresses your current EDGC responsibility. Please carry the evidence baseline and unresolved questions into your EDGC handoff to me on November 3. Your separate incoming PSI handoff follows in note 7.

Artifact A records a read of the vital-area interlock table at 02:41:19, including EDG A and EDG B labels. Returned values are not supplied. The record does not show an EDG control write or emergency-power failure.

Please preserve relevant access/configuration histories and assess EDG availability using the appropriate operations records and approved checks. Identify whether activity extended beyond this recorded table read. Return the evidence interval, findings, and limitations; escalate any actual functional concern with its discovery time. No live equipment actuation is requested by this draft.

## 6. Material-control lead / licensing lead

**Subject: Reconcile the affected inventory window and resolve safeguards applicability**

The FHB-02 override and camera-trigger inhibition overlapped SNM inventory. This creates a material-access concern but does not establish material loss, diversion, attempted theft, or accounting alteration.

Please preserve and reconcile physical inventory, authorized transfer records, accounting changes, and independent observations. Report discrepancies and any evidence of attempted removal with the time first discovered; distinguish missing evidence from a negative finding. Please also verify the facility's licensing basis, IAEA selection status, applicable containment arrangements, and license conditions for the notification assessment.

Use the classification draft's separate trigger analysis rather than assuming every safeguards report requires confirmed loss. The November 1 direct eCFR recheck confirms the displayed current rules through October 29; the site does not yet provide the October 30 date. Preserve that specific publication limit rather than claiming complete incident-date coverage. Return applicability findings and supporting records to the designated notifier; these requests do not establish that reconciliation or notification has occurred.

## 7. Handoff to Santiago Vargas — incoming PSI owner

**Subject: PSI handoff — confirmed override, proposed controls, and unresolved consequences**

Santiago,

You receive PSI on Tuesday, November 3, and I receive EDGC from you. Your W6 startup will use my handoff and runbook changes together with PSI's existing runbook, so please follow the startup/documentation section added to [runbook-update.md](runbook-update.md). After the instructor places the received files, pull `main` and read `workshops/week-06/handoff-received.md` and `runbook-update-received.md`. These file placements and the access change are scheduled, not verified as completed.

The October 30 scenario adds a confirmed bypass/camera-inhibit event to the retained-credential concerns in my W5 work. The register returned to normal after 10 minutes 51 seconds, but physical passage, material consequences, and full access-path recovery remain unresolved. Do not treat that reversion as incident closure.

Start with the scenario's A–C, then the technical analysis, classification, and runbook update linked above. The technical analysis references my W1 boundary assumptions, submitted W2 Dragonfly profile, W4 SFPCM test findings and limits, and W5 retained-access evidence. Dragonfly is the scenario's actor model; these excerpts do not independently establish attribution.

The runbook changes are proposals: effective cached-credential revocation, restricted response connectivity, approved/time-bounded overrides, protective-function paging, and durable reader/latch evidence. None was implemented or tested while preparing this package. Historical W5 SSH-key cleanup is separately documented and does not prove revocation of the midterm token.

Before implementation, validate the actual environment: the inherited lab's services, ports, and command coils are not proven equivalent to the scenario's controller, token database, addresses, or register 40210. Use qualified owners and supported procedures for any subsequent change.

Outstanding handoff items are ICT-SIEM/support-role routing; connector/session scope; independent physical-entry and inventory findings; SFPCM/EDG assessments; site-specific reporting applicability and the disclosed eCFR publication cutoff; and approved implementation/test plans. No actual notification record, new compensatory-measure record, or recovery test result was produced in this drafting session. Obtain those records if actions occur and record their actual times.

Please record startup successes and documentation gaps in your W6 `startup-gap-log.md`, and ask PSI questions to me in writing in the shared Canvas thread. I will direct EDGC questions to you. Please acknowledge receipt, identify the owner and next review time for each open item, and carry forward uncertainty where evidence is unrecoverable. Keep implemented changes separate from proposed work, and never include working credentials in the repository.

— Dominick Wheeler
