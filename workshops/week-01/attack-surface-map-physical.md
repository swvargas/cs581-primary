# Attack Surface Map - ICT Security Information & Event Mgmt (ICT-SIEM) Physical and Cyber-Physical Layer

**Student:** Santiago Vargas
**Course:** CS 581 Nuclear Cybersecurity
**Date:** 2026-09-08
**System:** ICT Security Information & Event Mgmt (ICT-SIEM)
**Purdue Zone:** Level 4
**Course Classification:** Corporate security

The ICT-SIEM is an enterprise monitoring system and should not directly control plant equipment. Its physical consequences are mainly caused by physical tampering, loss of supporting infrastructure, false physical-security data, or a failure to deliver information to people who must respond.

Evidence status uses Documented when the cited sources directly support the component or control, Inferred when the facility implementation is a reasoned possibility, and Theoretical when no public evidence establishes the interface for ICT-SIEM.

## Layer 3 - Physical & Cyber-Physical

| Interface / Component | Threat Vector | Physical Consequence | Confidence | Provenance |
|---|---|---|---|---|
| Plant actuation interface | The ICT-SIEM should have no authorized path for issuing plant commands, but an undocumented or bidirectional connection could violate that separation | If such a path existed and were compromised, an attacker might reach a system that can change equipment state; no direct actuation capability is established for ICT-SIEM | Low, Theoretical | NIST SP 800-82 Rev. 3 Section 5.2.3.1, 2023; NRC RG 5.71 Section 3.2 and Appendix C Section C.6, 2010; consequence is theoretical because no public source documents an ICT-SIEM actuation path |
| Server room and local administrator console | An intruder with physical access could shut down servers, attach unauthorized equipment, alter storage, or use a local console | Monitoring and alerting could stop, which could delay the security staff response to a separate plant event | High, Documented | NIST SP 800-82 Rev. 3 Section 5.2.2, 2023; NRC RG 5.71 Appendix C Sections C.5.3 through C.5.5, 2010 |
| USB ports and removable media | Malicious or unauthorized media could introduce software, remove security data, or change the SIEM configuration | Loss of monitoring could delay recognition of physical intrusion or other plant security activity | High, Documented | NIST SP 800-82 Rev. 3 Section 6.2.7, 2023; NRC RG 5.71 Appendix B Section B.1.19 and Appendix C Sections C.1.2 through C.1.5, 2010 |
| Power, cooling, fire protection, and water protection | Loss or manipulation of power or environmental support could damage hardware or force the ICT-SIEM offline | The security operations center could lose event visibility and alert delivery until service is restored or moved to a backup system | High, Documented | NIST SP 800-82 Rev. 3 Section 5.2.2 and OT Overlay controls PE-11 through PE-15, 2023; NRC RG 5.71 Appendix A Section A.3.1.4 and Appendix C Section C.5.3, 2010 |
| Network ports, cables, and boundary equipment | Physical access to a switch, firewall, sensor cable, or unused port could allow traffic interception, rogue device attachment, or disconnection | Plant security events could be hidden, delayed, or altered before they reach the ICT-SIEM and SOC staff | Medium, Inferred | NIST SP 800-82 Rev. 3 Sections 5.2.2 and 5.2.3.1, 2023; NRC RG 5.71 Appendix B Sections B.1.15 and B.3.6 and Appendix C Section C.5.6, 2010; the event-feed route is not public |
| Physical access and intrusion alert feed | False, suppressed, or delayed badge, door, or intrusion events could produce an incorrect SOC alert; the specific integration is not confirmed | Security personnel could miss an actual intrusion or be sent to investigate a false event | Low, Inferred | NIST SP 800-82 Rev. 3 Sections 2.3.6 and 5.2.2, 2023; NRC RG 5.71 Appendix C Sections C.5.8 and C.8.1, 2010; ICT-SIEM integration is not confirmed |

## Layer Summary

The ICT-SIEM does not normally create a direct physical process change. Its main cyber-physical role is to help people recognize and respond to activity reported by digital and physical security systems. Physical access to servers, removable media, network equipment, or support infrastructure could remove that visibility. The highest-consequence actuation scenario remains Low confidence because public sources do not show an authorized command path from ICT-SIEM to plant equipment.

## What This Map Cannot Tell You

Public sources cannot confirm where the ICT-SIEM servers and analyst consoles are physically located or who can enter those areas. NRC-licensed facility documentation and direct observation would be needed to verify power redundancy, cooling, fire protection, network cabling, unused ports, removable-media controls, and local console access. Vendor documentation under a nondisclosure agreement would be needed to determine whether any connector, plug-in, or response feature can send commands to another system. Facility configuration and response procedures would also be needed to confirm whether physical access alerts reach the ICT-SIEM and what actions security personnel take after receiving them.
