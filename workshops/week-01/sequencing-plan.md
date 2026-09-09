# W1 to W9 Sequencing Plan - Santiago Vargas

**Student:** Santiago Vargas
**W1 System:** ICT-SIEM - ICT Security Information & Event Mgmt
**Created:** Week 1, September 6, 2026
**Last revised:** Week 1, September 8, 2026

This plan assigns all 11 course systems across the nine workshops. W1 is locked to ICT-SIEM because it is the closest system to my data and database background. Two workshops include two related systems so the plan reaches full coverage by W9. The sequence may change as I learn more about the systems, but I will record any changes in the revision log.

## Workshop-System Map

| Workshop | Theme | System(s) | Justification |
|---|---|---|---|
| W1 Sep 8 | Attack Surface Mapping and System Selection | ICT-SIEM | The ICT-SIEM gives me a familiar starting point for mapping how security data enters, moves through, and is stored in a Level 4 enterprise system. |
| W2 Sep 21 | Adversary Profiling and Threat Modeling | RMS | An attacker could target radiation measurements or monitoring availability, which makes the RMS useful for studying adversary goals and possible consequences. |
| W3 Oct 5 | Protocol Security and Access Control | DCS | The DCS uses control communications and restricted operator access, so it supports analysis of protocol weaknesses, authentication, and authorization. |
| W3 Oct 5 | Protocol Security and Access Control | PPC | The PPC receives and stores plant process data, which creates clear questions about trusted data sources, access permissions, and protection against altered records. |
| W4 Oct 12 | ICS/SCADA and Digital I&C Security | TCS | The TCS is a Level 1 operational control system where changes to commands, logic, or availability can affect turbine operation. |
| W5 Oct 26 | Physical Protection and Regulatory Frameworks | RPS | The RPS is safety critical and provides a direct case for studying how cyber protection supports reactor safety requirements. |
| W5 Oct 26 | Physical Protection and Regulatory Frameworks | EDGC | The EDGC supports emergency power, so physical access, cyber compromise, and regulatory controls must be considered together. |
| W6 Nov 16 | Monitoring Strategy and Supply Chain Security | OT-SIEM | The OT-SIEM is designed to monitor operational networks and can show how plant events, alert thresholds, vendor products, and monitoring gaps affect detection. |
| W7 Nov 30 | Incident Response in Nuclear Environments | SFPCM | A cyber incident affecting spent fuel pool cooling or monitoring would require a response that protects evidence without interfering with continued safe operation. |
| W8 Dec 7 | Side Channels, AI and Emerging Threats | SMR I&C | The integrated and highly digital design of SMR I&C makes it a useful system for studying side channels, automation, AI use, and new attack paths. |
| W9 Dec 14 | Ethics, Policy and Portfolio Synthesis | PSI | PSI combines cyber monitoring with physical access and surveillance, which raises ethical and policy questions about privacy, authority, evidence, and security decisions. |

## Coverage Check

| System | Workshop | Status |
|---|---|---|
| ICT-SIEM | W1 | Planned |
| RMS | W2 | Planned |
| DCS | W3 | Planned as paired system |
| PPC | W3 | Planned as paired system |
| TCS | W4 | Planned |
| RPS | W5 | Planned as paired system |
| EDGC | W5 | Planned as paired system |
| OT-SIEM | W6 | Planned |
| SFPCM | W7 | Planned |
| SMR I&C | W8 | Planned |
| PSI | W9 | Planned |

All 11 systems are covered. W3 pairs DCS with PPC because process data connects the two systems. W5 pairs RPS with EDGC because both are Level 1 safety-critical systems.

## Semester Arc

The sequence begins with the ICT-SIEM because it is closest to my background in data and databases. I can start by studying how security records are collected, stored, and searched at Level 4. The plan then moves toward systems that produce or depend on operational data, including the RMS, DCS, PPC, and OT-SIEM. This creates a common thread around data integrity, access, monitoring, and the effect of bad or missing information on security decisions. Pairing the DCS with the PPC also lets me study the connection between a control system and the system that records its process data.

The sequence also requires me to move beyond database topics into plant operations, safety systems, physical protection, and nuclear regulation. W5 will be difficult because I will need to understand how the RPS and EDGC support safety and how regulatory requirements affect their protection. W7 will also be challenging because an incident involving the SFPCM requires both technical response and attention to continued safe operation. I expect W8 to be the hardest because side channels, SMR instrumentation, and AI risks are new subjects for me and may require more research into hardware and control engineering.

## Risks and Uncertainties

- W2 may require more research because I do not yet know which attacks are most realistic for a radiation monitoring system.
- W5 includes two safety-critical systems, so I may need to limit the analysis to their shared protection and regulatory concerns.
- W8 covers hardware, side channels, AI, and SMR technology, which are all outside my current data and database experience.
- PSI is placed in W9 because it raises useful ethics and policy questions, but I may move it earlier if the physical protection material requires a more detailed technical analysis.

## Revision Log

| Date | Change | Reason |
|---|---|---|
| 2026-09-06 | Initial plan | First version of the semester sequence |
| 2026-09-08 | Expanded plan layout | Added plan context, coverage verification, and risks after reviewing the course example |
