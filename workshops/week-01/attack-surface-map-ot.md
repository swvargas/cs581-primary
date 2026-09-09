# Attack Surface Map - ICT Security Information & Event Mgmt (ICT-SIEM) OT Layer

**Student:** Santiago Vargas
**Course:** CS 581 Nuclear Cybersecurity
**Date:** 2026-09-08
**System:** ICT Security Information & Event Mgmt (ICT-SIEM)
**Purdue Zone:** Level 4
**Course Classification:** Corporate security

This map examines possible paths that carry security information from plant systems toward the Level 4 ICT-SIEM. It does not assume that the ICT-SIEM directly connects to a control system or that any named protocol is used at a specific facility.

## Layer 2 - OT (Levels 1-3 / Plant)

| Interface / Component | Protocol or Connection Type | Threat Vector | Confidence | Provenance |
|---|---|---|---|---|
| OT-SIEM export pipeline | Unidirectional gateway, data diode, or tightly controlled firewall path; the export format is facility-specific | A configuration error or unintended return path could expose the OT-SIEM or allow unauthorized traffic toward the plant network | High | NIST SP 800-82 Rev. 3 Section 5.2.3.1 and Appendix E.1, 2023; NRC RG 5.71 Section 3.2 and Appendix B Section B.3.3, 2010; IAEA NSS No. 17-T paragraphs 5.18 and 5.21, 2021 |
| Level 3 security log collector | Syslog or a vendor collection agent; the specific transport and security settings are not public | Spoofed, altered, delayed, or dropped logs could give the ICT-SIEM an incomplete view of plant activity | Medium | NIST SP 800-82 Rev. 3 Appendix E Sections E.2 and E.2.1, 2023; NRC RG 5.71 Appendix B Sections B.2.2, B.2.3, and B.2.9, 2010 |
| Plant historian or PPC event feed | Database export, file transfer, Syslog, or vendor API; the actual connection is not confirmed | Manipulated process records or false event data could produce incorrect alerts or hide the timing of an incident | Medium | NIST SP 800-82 Rev. 3 Appendix E Section E.2.1, 2023; NRC RG 5.71 Appendix B Sections B.2.3 and B.3.6, 2010 |
| Level 3/4 boundary firewall | Filtered and monitored network connection between approved endpoints | Overly broad rules, unauthorized rule changes, or a failure to monitor the boundary could permit traffic that was not part of the approved data flow | High | NIST SP 800-82 Rev. 3 Section 5.2.3.1, 2023; NRC RG 5.71 Appendix B Sections B.1.15 and B.3.3, 2010; IAEA NSS No. 17-T paragraph 5.23, 2021 |
| OT network monitoring sensor | Passive network tap, switch mirror port, or sensor feed | A missing monitoring point, changed mirror configuration, or encrypted traffic could create a blind spot in the data exported to the ICT-SIEM | Medium | NIST SP 800-82 Rev. 3 Section 5.2.3.3 and Appendix E.2.2, 2023; NRC RG 5.71 Appendix C Section C.3.4, 2010 |
| LDAP or Active Directory integration | LDAP, LDAPS, Kerberos, or a separate identity service; the actual protocol and trust relationship are not confirmed | A compromised corporate identity or an overly broad trust relationship could provide unauthorized access to monitoring functions or plant-side accounts | Low | NIST SP 800-82 Rev. 3 Section 6.2.1, 2023; NRC RG 5.71 Appendix B Sections B.1.6 and B.4, 2010; protocol choice is inferred from common enterprise identity systems |
| Alert escalation path | Email, ticketing platform, phone notification, or security orchestration workflow; the actual method is facility-specific | An attacker could suppress, redirect, delay, or flood notifications so that plant staff do not receive a valid alert | Medium | NRC RG 5.71 Appendix B Section B.2.6 and Appendix C Sections C.3.5 and C.8.1, 2010; NIST SP 800-82 Rev. 3 Sections 6.3.3 and 6.4.2, 2023 |
| SOC analyst workstation and SIEM API | HTTPS web session, REST API, or vendor management client; no public source confirms the implementation | Stolen credentials, session tokens, or excessive API permissions could allow changes to alerts, searches, users, or collected data | Low | NIST SP 800-82 Rev. 3 Sections 6.2.1 and 6.2.10, 2023; NRC RG 5.71 Appendix B Sections B.1.6, B.3.8, and B.4, 2010; protocol is inferred from common SIEM products |
| Plant time source | NTP or SNTP through an approved and protected path | Time spoofing or loss of synchronization could prevent accurate correlation between OT-SIEM and ICT-SIEM records | High | NIST SP 800-82 Rev. 3 Section 6.2.12, 2023; NRC RG 5.71 Appendix B Section B.2.8, 2010 |
| Export queue and receiving storage | Buffered event transfer and centralized database storage | Event flooding or storage exhaustion could delay plant alerts, overwrite records, or stop new records from being accepted | High | NIST SP 800-82 Rev. 3 Appendix E Section E.2.1, 2023; NRC RG 5.71 Appendix B Sections B.2.4 and B.2.5 and Section B.3.4, 2010 |

## Layer Summary

The OT layer depends on controlled movement of event data from more protected plant zones toward the Level 4 ICT-SIEM. The export pipeline, boundary firewall, identity connection, and alert path can improve detection, but each connection can also create a new route for false data, lost records, or unauthorized access. The strongest public support exists for segmentation, controlled data flow, protected audit records, time synchronization, and monitoring at security boundaries. Specific uses of LDAP, Active Directory, REST APIs, email, and ticketing systems remain assumptions until facility or vendor records confirm them.

## What This Map Cannot Tell You

Public sources cannot confirm whether a specific facility exports OT-SIEM data to the ICT-SIEM or keeps the two systems fully separate. NRC-licensed architecture records and direct observation would be needed to identify the direction of data flow, boundary devices, firewall rules, collectors, and approved alert escalation process. Vendor documentation under a nondisclosure agreement would be needed to confirm the export format, LDAP or Active Directory design, API endpoints, authentication methods, and analyst workstation software. Facility testing and operational records would be needed to measure event loss, transfer delay, storage capacity, clock accuracy, and whether an alert reaches the correct responder.
