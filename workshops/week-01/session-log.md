# Session Log, Workshop 1
## Santiago Vargas | Codex | September 6 to September 9, 2026

This log records how I used Codex during Workshop 1, including the claims I questioned and the changes I requested.

## Session 1, September 6 | System Selection and Semester Planning

**Duration:** Not recorded

**Outcome:** Drafted `system-selection.md` and `sequencing-plan.md`.

**Initial prompt:** "Write the content for my system-selection.md" using ICT-SIEM, Level 4, Corporate security, and my Data and Database background.

I selected ICT-SIEM because it connects to my data and database background. I asked Codex to explain what I bring to the topic instead of giving a general description of SIEM. The useful parts were the discussion of missing records, duplicate events, parser failures, time differences, indexing, retention, permissions, and storage exhaustion.

The first system-selection draft was too confident about the Purdue placement and regulatory meaning. I asked Codex to check the claims against the MITRE ATT&CK Enterprise and ICS matrices. That review showed that MITRE describes attacker behavior but does not prove that a specific facility uses a particular ICT-SIEM interface. I redirected the writing so Level 4 and Corporate security are course architecture labels, not proof that the system is a Critical Digital Asset under 10 CFR 73.54.

For the sequencing plan, I asked Codex to cover all 11 systems across W1 through W9. I then compared the result with the course example and asked for a clearer title, created date, coverage check, risks, and revision log. I changed the initial date to September 6 because that is when I started the plan. The final map covers all 11 systems and uses paired systems in W3 and W5.

## Session 2, September 8 | Three-Layer Attack Surface Map

**Duration:** Not recorded

**Outcome:** Created the IT, OT, and physical attack-surface files.

**Initial prompt:** "I am mapping the layer 1 IT Level 4 Corporate attack surface of ICT Security Information & Event Mgmt" with a table of interfaces, protocols, threat vectors, confidence, and provenance.

I asked for the three layers separately so each prompt could focus on a smaller set of interfaces. For the IT layer, I focused on the Level 3 and Level 4 boundary, enterprise collection, storage, identity, time, and analyst access. For the OT layer, I focused on the possible OT-SIEM export, plant log collectors, historian data, alert escalation, and analyst API access. For the physical layer, I focused on server rooms, removable media, power and cooling, cables, ports, physical alert feeds, and the lack of a confirmed plant actuation path.

Codex initially produced several plausible connections that public sources could not confirm for a real facility. These included a data diode at the OT-SIEM export, LDAP or Active Directory integration, REST API access, email or ticketing escalation, and physical-security alert feeds. I kept them only as possible interfaces and lowered confidence where the protocol or connection was inferred. I also required a facility-specific limits section so the maps would not look like completed plant assessments.

## Session 3, September 8 | Source Verification and Corrections

**Duration:** Not recorded

**Outcome:** Created `attack-surface-verification.md` using NIST SP 800-82 Rev. 3 and NRC RG 5.71.

**Initial prompt:** "Review the attack surface map I produced across all three layers. For each row, verify the protocol, threat vector, and confidence level against these two sources."

I asked Codex to audit each layer using two public primary sources. The verification found that the sources support segmentation, protected audit records, time synchronization, monitoring, and physical protection, but they do not document a specific ICT-SIEM design. The largest changes were lowering the OT-SIEM export and boundary firewall rows from High to Medium, lowering identity and alert service assumptions to Low, and separating well-supported centralized storage from the less-supported buffered export queue.

This was the main pushback point in the workshop. A control recommendation is not evidence that a facility implemented that control in a specific way. The correction table now separates an authoritative security principle from an unverified protocol or product configuration.

## Session 4, September 8 | Regulatory Reasoning Test

**Duration:** Not recorded

**Outcome:** Tested Codex on a manipulated OT-SIEM export scenario.

**Initial prompt:** "Under NRC regulations, an adversary manipulates data at the OT-SIEM export layer so ICT-SIEM analysts see normal alerts while the actual OT environment is under attack. What are the regulatory implications of this detection gap?"

I asked what RG 5.71 would mean if an adversary made ICT-SIEM analysts see normal alerts while OT was under attack. Codex identified possible failures in monitoring, audit integrity, transmission integrity, defense in depth, investigation, and corrective action. It appropriately qualified the answer. The facts did not establish that ICT-SIEM was in the licensee's cyber security program, that an SSEP function was adversely affected, when discovery occurred, or which reporting deadline applied.

The reasoning test did not expose private chain-of-thought. The useful part was the visible evidence summary and the distinction between RG 5.71 guidance and binding requirements in 10 CFR 73.54 and 10 CFR 73.77. It did not surface a major conclusion that the final answer omitted.

## Session 5, September 8 | Architecture Vision Test

**Duration:** Not recorded

**Outcome:** Tested diagram reading and recorded the result.

**Initial prompt:** "Without reading any labels outside of what is visible in the image," list every system and connection, identify ICT-SIEM connections, describe direction indicators, and explain the zone coding.

I asked Codex to inspect the full CS 581 Plant Architecture Diagram using only labels visible in the image. It identified all 11 system nodes, the one-way OT-SIEM to ICT-SIEM export, the other labeled system connections, the direction indicators, and the Level 4 through Level 0 bands. It did not add Syslog, HTTPS, LDAP, or another protocol to the ICT-SIEM link because the diagram only labels it as a one-way export.

The unresolved detail was the four short vertical marks in Level 0. They align with Level 1 systems but do not visibly reach the system boxes. Codex did not count them as direct connections. This was a reasonable choice, but it is still a detail I would verify against the diagram author or supporting documentation.

## Session 6, September 9 | Deliverable Audit

**Duration:** Not recorded

**Outcome:** Checked both repositories against the submission list.

The audit found that the first `tool-selection.json` still contained placeholders, blank model fields, an incorrect evaluation date, and no completed seven-dimension capability evaluation. It also found that the secondary synthesis only contained the vision-test paragraph and did not analyze the NRC Regulator and Plant Cybersecurity Manager roles. I corrected both files using the course templates and retained the earlier vision result as evidence in the tool evaluation.

## Reflection

**What worked:** Narrow prompts produced better results than asking for the whole assignment at once. Requiring a source and confidence level for each row made unsupported interfaces easier to find. Comparing the output with the course template also caught structural problems that a technical source review would not catch.

**What did not work:** The first drafts sometimes treated standard security controls as proof of a facility-specific architecture. The first tool evaluation also looked complete at a glance even though it contained placeholders and did not follow the required schema.

**What I would do differently:** I would open the course template before generating the first file. I would also separate three questions in every attack-surface prompt. What does the source require, what does the course diagram show, and what is only a reasonable facility-specific possibility.

**Time spent:** I did not track time consistently enough to provide accurate totals for reading, AI sessions, and editing.
