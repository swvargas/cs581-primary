# Attack Surface Map - ICT Security Information & Event Mgmt (ICT-SIEM) IT Layer

**Student:** Santiago Vargas
**Course:** CS 581 Nuclear Cybersecurity
**Date:** 2026-09-08
**System:** ICT Security Information & Event Mgmt (ICT-SIEM)
**Purdue Zone:** Level 4
**Course Classification:** Corporate security

This map examines the Level 4 interfaces that collect, store, and present security information. It does not assume that the ICT-SIEM is a Critical Digital Asset or that it has a direct connection to lower plant zones.

## Layer 1 - IT (Level 4 / Corporate)

| Interface / Component | Protocol or Connection Type | Threat Vector | Confidence | Provenance |
|---|---|---|---|---|
| Level 3/4 log transfer boundary | Unidirectional gateway, data diode, or firewall-controlled connection; the application protocol is facility-specific | A misconfigured boundary rule or unintended reverse path could allow unauthorized traffic from Level 4 toward a more protected plant zone | Medium | NIST SP 800-82 Rev. 3 Section 5.2.3.1, 2023; NRC RG 5.71 Section 3.2 and Appendix B Section B.3.3, 2010 |
| Enterprise log collectors | Syslog, vendor agents, or another approved collection method; the actual method is not public | An attacker could spoof, alter, delay, or stop event records before they reach the SIEM | Medium | NIST SP 800-82 Rev. 3 Appendix E Sections E.2 and E.2.1, 2023; NRC RG 5.71 Appendix B Sections B.2.2 and B.2.3, 2010 |
| Central SIEM database and event index | Internal database connections between collection, processing, and storage services | Unauthorized access, record deletion, or storage exhaustion could remove evidence and prevent new events from being processed | High | NIST SP 800-82 Rev. 3 Appendix E Section E.2.1, 2023; NRC RG 5.71 Appendix B Sections B.2.4, B.2.5, and B.2.9, 2010 |
| Analyst and administrator console | Web console or vendor management client; HTTPS is a likely implementation but is not confirmed | Stolen credentials or excessive privileges could allow an attacker to change searches, alerts, users, or retention settings | Low | NIST SP 800-82 Rev. 3 Sections 6.2.1 and 6.2.10, 2023; NRC RG 5.71 Appendix B Sections B.1 and B.4, 2010; protocol is inferred from common enterprise SIEM products |
| Enterprise identity service | Directory or identity-provider connection; LDAP, Kerberos, or another protocol may be used but is not confirmed | A compromised identity account or authentication service could give unauthorized access to SIEM data and administrative functions | Medium | NIST SP 800-82 Rev. 3 Section 6.2.1, 2023; NRC RG 5.71 Appendix B Sections B.3.8 and B.4, 2010 |
| Time synchronization service | NTP or SNTP from an approved time source | Spoofed or incorrect time could break event correlation and create an inaccurate incident timeline | High | NIST SP 800-82 Rev. 3 Section 6.2.12, 2023; NRC RG 5.71 Appendix B Section B.2.8, 2010 |
| Network monitoring sensor or traffic feed | Passive network tap, switch mirror port, or sensor feed; the exact design is facility-specific | A missing collection point, altered sensor configuration, or encrypted traffic could create blind spots and false results | Medium | NIST SP 800-82 Rev. 3 Sections 5.2.3.3 and Appendix E.2.2, 2023; NRC RG 5.71 Appendix A Section A.4.1 and Appendix B Section B.2.6, 2010 |

## Layer Summary

The main IT-layer risk is loss of trust in the security data. An attacker who compromises a collector, administrator account, time source, or storage service could hide activity without directly attacking a plant control system. The Level 3/4 boundary is also important because a monitoring connection should not create an unintended path from the corporate network into a more protected plant zone. Public guidance supports segmentation, centralized logging, protected audit records, and time synchronization, but it does not identify the design used at a specific facility.

## What This Map Cannot Tell You

Public sources do not show whether a specific nuclear facility sends any Level 3 or lower event data to the Level 4 ICT-SIEM. NRC-licensed architecture records or direct facility observation would be needed to confirm whether the boundary uses a data diode, firewall, intermediate collector, removable media transfer, or no connection at all. Vendor documentation under a nondisclosure agreement would be needed to identify the SIEM product, enabled services, ports, agents, APIs, database design, and security settings. Facility records would also be needed to verify the actual log sources, identity integration, time source, retention period, alert rules, and administrator access paths.
