# Attack Surface Verification - ICT Security Information & Event Mgmt (ICT-SIEM)

**Student:** Santiago Vargas
**System:** ICT Security Information & Event Mgmt (ICT-SIEM), Level 4, Corporate security
**Date:** 2026-09-08

## Sources Used

- Source A: National Institute of Standards and Technology, [NIST SP 800-82 Rev. 3, Guide to Operational Technology Security](https://doi.org/10.6028/NIST.SP.800-82r3), Sections 5.2.2, 5.2.3, 6.2, 6.3, 6.4, and Appendix E, 2023
- Source B: U.S. Nuclear Regulatory Commission, [Regulatory Guide 5.71, Cyber Security Programs for Nuclear Facilities](https://scp.nrc.gov/slo/regguide571.pdf), Section 3.2 and Appendices B and C, 2010

## Corrections

| Layer | Original Claim | Error Type | Corrected Entry | Source |
|---|---|---|---|---|
| All layers | NRC RG 5.71 controls were cited as support for ICT-SIEM interfaces | Scope overclaim | RG 5.71 supports these controls only if the facility places the ICT-SIEM or a connected asset within its cyber security program; the guide does not prove that a Level 4 corporate SIEM is a Critical Digital Asset | NRC RG 5.71 Section 3.1 and Appendices A and B |
| IT | Enterprise identity service using LDAP, Kerberos, or another identity protocol was rated Medium | Wrong confidence level | Keep the identity service as a possible interface, but rate it Low because neither selected source confirms LDAP, Kerberos, or an identity connection for ICT-SIEM | NIST SP 800-82 Rev. 3 Section 6.2.1; NRC RG 5.71 Appendix B Sections B.3.8 and B.4 |
| OT | OT-SIEM export through a unidirectional gateway, data diode, or firewall was rated High | Overclaim and wrong confidence level | Rate the row Medium because both sources support controlled boundary devices, but neither confirms that a specific ICT-SIEM receives an OT-SIEM export or identifies the device used | NIST SP 800-82 Rev. 3 Section 5.2.3.1 and Appendix E.1; NRC RG 5.71 Section 3.2 and Appendix B Section B.3.3 |
| OT | A Level 3/4 boundary firewall for ICT-SIEM was rated High | Wrong confidence level | Rate the row Medium because boundary filtering is well supported, but the use of a firewall instead of physical separation or a unidirectional gateway is facility-specific | NIST SP 800-82 Rev. 3 Section 5.2.3.1; NRC RG 5.71 Appendix B Sections B.1.15 and B.3.3 |
| OT | Email, ticketing, phone, or orchestration was listed as the alert escalation path with Medium confidence | Unsupported protocol and wrong confidence level | Rate the row Low and describe the connection as a facility-defined notification process because the sources require alert review and notification but do not name the delivery service used by ICT-SIEM | NIST SP 800-82 Rev. 3 Sections 6.3.3 and 6.4.2; NRC RG 5.71 Appendix C Sections C.3.5 and C.8.1 |
| OT | Buffered event transfer and centralized storage were rated High as one entry | Mixed support and wrong confidence level | Keep centralized storage and storage exhaustion as High, but treat the use of a buffered export queue as Medium because neither source confirms that implementation | NIST SP 800-82 Rev. 3 Appendix E Section E.2.1; NRC RG 5.71 Appendix B Sections B.2.4, B.2.5, and B.3.4 |
| Physical and cyber-physical | A physical access and intrusion alert feed into ICT-SIEM was rated Medium | Wrong confidence level | Rate the row Low because the sources support monitoring physical access and intrusion alarms but do not confirm that those events are sent to the Level 4 ICT-SIEM | NIST SP 800-82 Rev. 3 Sections 2.3.6 and 5.2.2; NRC RG 5.71 Appendix C Sections C.5.8 and C.8.1 |
| Physical and cyber-physical | Physical access to network ports and cables was rated High as a path for hiding events before they reach ICT-SIEM | Wrong confidence level | Rate the row Medium because physical protection of communication paths is documented, but the existence and route of a plant event feed to ICT-SIEM are not public | NIST SP 800-82 Rev. 3 Sections 5.2.2 and 5.2.3.1; NRC RG 5.71 Appendix C Section C.5.6 |

## Confidence Adjustments

The IT Enterprise identity service row changes from Medium to Low because NIST Section 6.2.1 and RG 5.71 Appendix B support access control but do not identify LDAP, Kerberos, or Active Directory for this system. The OT-SIEM export pipeline and Level 3/4 boundary firewall rows change from High to Medium because NIST Section 5.2.3.1 and RG 5.71 Section 3.2 support segmentation and controlled data flow without confirming the facility's connection design. The OT alert escalation row changes from Medium to Low because the sources describe notification responsibilities but do not identify email, telephone, ticketing, or orchestration as the actual channel. The OT export queue is split so centralized storage remains High while buffering is Medium. The physical access alert feed changes from Medium to Low, and the network port and cable row changes from High to Medium, because neither source proves that plant physical-security events are delivered to ICT-SIEM.

## What This Verification Cannot Resolve

The two public sources cannot establish whether a nuclear facility connects its OT-SIEM, historian, physical access system, or plant time source to the Level 4 ICT-SIEM. NRC-licensed architecture and cyber security program records would be required to confirm the boundary devices, data direction, firewall rules, regulatory scope, and approved escalation path. Vendor documentation under a nondisclosure agreement would be required to confirm the SIEM product, enabled APIs, collectors, buffering behavior, database services, LDAP or Active Directory configuration, and authentication methods. Direct facility observation and testing would be required to measure event loss, alert delay, storage exhaustion behavior, physical port controls, backup power, and the response taken after an ICT-SIEM alert.
