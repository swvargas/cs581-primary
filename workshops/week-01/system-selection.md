# System Selection — Workshop 1

**Student:** Santiago Vargas
**Tool:** Codex
**Date:** 2026-09-08

## System
ICT Security Information & Event Mgmt (ICT-SIEM)

## Purdue Zone and Safety Classification
The course architecture places the ICT-SIEM at Purdue Level 4 as a Corporate security system, so attackers may target it through enterprise accounts, servers, endpoints, remote services, and administrative tools, while defenders must protect its security data and control any approved connection that receives information from lower plant zones.

## Rationale
I selected the ICT-SIEM because its main data problems connect well with my background in data and databases. A SIEM collects security records from different sources and puts them into a format that analysts can search. Depending on the facility design, those sources may include Windows events, Syslog messages, database audit records, identity systems, and application data. My experience helps me recognize problems such as missing records, duplicate events, clock differences, failed parsers, slow queries, and schema changes. These problems can prevent an analyst from seeing an attack even when the security tool is running.

My database background also helps me evaluate whether investigators can trust the information stored in the SIEM. Retention, indexes, partitions, user permissions, service accounts, encryption, backups, and tamper-resistant storage all affect detection and investigation. The [MITRE ATT&CK Enterprise Matrix](https://attack.mitre.org/matrices/enterprise/) includes attacker behaviors such as Valid Accounts, credential theft, defense impairment, log clearing, and data destruction. I can study whether the available data would reveal these behaviors and whether an attacker could hide them by deleting, delaying, or overwhelming security records.

The nuclear setting adds limits that I need to consider. I cannot assume that the ICT-SIEM connects directly to plant control networks or that every Level 4 asset is automatically covered by 10 CFR 73.54. The facility would need to determine whether the ICT-SIEM supports safety, security, or emergency preparedness functions, or whether its compromise could adversely affect those functions. NRC Regulatory Guide 5.71 and NEI 08-09 provide guidance for defensive architecture, but public information does not show the actual log sources, network paths, or regulatory scope of a specific facility's ICT-SIEM. I will treat those details as unknown unless a source documents them.

## Workshop Fit Analysis
- **Workshop 1, Nuclear Plant Attack Surface Map + System Selection: Strong fit.** The ICT-SIEM has enterprise components, administrative interfaces, data sources, and possible connections to other plant security systems that can be examined in a layered attack-surface map.
- **Workshop 2, Adversary Profile: Strong fit.** Behaviors such as Valid Accounts, credential theft, remote service abuse, defense impairment, and log clearing can be connected to possible ICT-SIEM data sources using the MITRE ATT&CK Enterprise Matrix.
- **Workshop 3, Protocol Security Analysis: Weak fit.** Modbus and DNP3 are used in operational environments rather than the enterprise focus of this system, so my sequencing plan will use a Level 1 or Level 2 control system where protocol behavior can be studied directly.
- **Workshop 4, Access Control Policy Design: Strong fit.** SIEM administrators, analysts, incident responders, auditors, and service accounts need separate permissions, separation of duties, emergency access, and controlled authentication.
- **Workshop 5, Three-Framework Incident Analysis: Moderate fit.** ICT-SIEM records may help build a timeline and compare enterprise activity with plant events, but the system cannot determine Safety, Security, or Safeguards consequences by itself and its actual lower-zone data sources are facility-specific.
- **Workshop 6, Monitoring Strategy + Supply Chain Assessment: Strong fit.** Log collection, detection rules, alert thresholds, storage, blind spots, vendor integrations, and software updates are central parts of ICT-SIEM operation.
- **Workshop 7, Zimmerman in Nuclear Context: Strong fit.** The ICT-SIEM may provide useful incident evidence, making data preservation, query availability, escalation, and access logging concrete response issues.
- **Workshop 8, Side-Channel Technical Brief: Weak fit.** The [MITRE ATT&CK ICS Matrix](https://attack.mitre.org/matrices/ics/) focuses on control-system behaviors and consequences, while timing, power, electromagnetic, and acoustic leakage are more directly studied on embedded equipment, so my sequencing plan will use a safety PLC or nuclear instrumentation component.
- **Workshop 9, AI in Nuclear Operations Risk Assessment: Strong fit.** AI-based anomaly detection depends on accurate telemetry, protected training data, model monitoring, understandable alerts, and appropriate human review.
