# Session Log, Workshop 2
## Santiago Vargas | Codex | September 18–21, 2026

This log records how I used Codex during Workshop 2 and how I reviewed and changed its output. I used the tool for structure, comparison, and drafting, but I made the main scope decisions: RMS remained the W2 system from my semester plan, TEMP.Veles became the deep-profile actor, the five cards were selected to span the course taxonomy, and unsupported RMS connections were retained only when clearly labeled as inferred or theoretical.

## Session 1, September 18 | Requirements and System Continuity

**Duration:** Not recorded

**Outcome:** Defined the W2 scope and connected it to the W1 attack-surface map.

**Prompt focus:** Read the W2 schema, use RMS from my W1 sequencing plan, and identify what the profile had to carry forward from my ICT-SIEM map.

Codex summarized the required fields and initially treated the assignment as if it needed a route from the Level 4 ICT-SIEM into RMS. I compared that assumption with my W1 OT map. The map describes possible plant data moving outward through a Level 3 collector, historian or PPC feed, OT-SIEM export, and Level 3/4 boundary. It does not establish a reverse route, a direct RMS connection, or an operational-control path.

I changed the approach so `pivot_path` gives a negative answer instead of inventing connectivity. The final field says that no verified pivot exists and explains that a correctly implemented unidirectional gateway would prevent a reverse network pivot. This became a constraint for the rest of the profile: W1 interfaces could be named as possible observation points, but not presented as confirmed RMS interfaces.

## Session 2, September 18 | Actor Selection and Attribution

**Duration:** Not recorded

**Outcome:** Selected TEMP.Veles for the deep profile and separated reported facts from attribution assessments.

**Prompt focus:** Compare publicly reported ICS actors that could support six to ten MITRE ATT&CK for ICS techniques without claiming documented RMS targeting.

Codex proposed actors with energy or industrial-control histories. I selected TEMP.Veles because the TRITON campaign provides a documented safety-controller precedent and enough technical behaviors for an in-depth profile. That selection was mine; the tool helped organize the comparison and later draft the JSON.

The first wording compressed TEMP.Veles, XENOTIME, TsNIIKhM, and the named defendant into one identity. I checked the distinctions in CISA/FBI/DOE AA22-083A, the Department of Justice announcement, and MITRE's associated-group description. I revised `attributed_to` and `provenance` so the file distinguishes government reporting, an indictment allegation, MITRE's association, and Mandiant's assessment. I also added an explicit warning that the labels and every operator are not proven identical. The actor-level confidence is therefore `assessed`, not `documented`.

I made the same correction in `nuclear_targeting_evidence`. AA22-083A discusses two Russian campaigns, but the fact that the separate FSB campaign included nuclear-sector targeting does not prove that the TsNIIKhM-linked TRITON actors targeted nuclear facilities. The final profile says that applying TEMP.Veles behavior to RMS is a threat-model exercise, not historical evidence of an RMS attack.

## Session 3, September 19 | TTP Selection and MITRE Verification

**Duration:** Not recorded

**Outcome:** Built eight `primary_ttps` entries and mapped each to a specific W1 interface.

**Prompt focus:** Identify documented TEMP.Veles procedures in MITRE ATT&CK for ICS, verify each ID in the ICS matrix, and explain its possible relevance without extending the source beyond its claim.

Codex produced a candidate list. I retained eight entries: Adversary-in-the-Middle (T0830), Indicator Removal on Host (T0872), Lateral Tool Transfer (T0867), Program Download: Program Append (T0843.003), Remote Services (T0886), Scripting (T0853), Unauthorized Message: Command Message (T1692.001), and Valid Accounts (T0859). I checked that these were ICS techniques rather than guessing from the number prefix, because the assignment specifically warns that both older and newer numbering appear in the ICS matrix.

The first draft sometimes moved too quickly from a TRITON procedure to an RMS scenario. I rewrote each entry in two parts. `nuclear_relevance` first states what the public source reports about TRITON, then labels the RMS application inferred or theoretical. `system_relevance` names an interface from my own W1 map: the historian or PPC event feed, Level 3 collector, OT sensor, Level 3/4 firewall, or possible identity integration. I preserved the W1 confidence limitation for each interface. For example, the historian feed might expose inconsistent measurements, but it is not a demonstrated programming path into RMS.

## Session 4, September 20 | Precedent, Detection, and Knowledge Gaps

**Duration:** Not recorded

**Outcome:** Completed the historical, defensive, and uncertainty fields.

**Prompt focus:** Turn the verified TTPs into detection opportunities and list what open reporting cannot establish.

Codex drafted detections for RDP, internal transfers, PowerShell, missing logs, program downloads, and unauthorized messages. I changed these from guaranteed controls to conditional opportunities. The final entries say to use a sensor or log source only where the facility actually has it and acknowledge that the W1 map cannot confirm the feed. I added comparison with independent RMS indications so the SIEM is not treated as its own source of truth.

The `gaps_in_public_knowledge` array received a separate review instead of being treated as a closing disclaimer. I recorded unresolved group-name overlap, limits on identifying or proving government direction of every operator, the absence of documented RMS or nuclear targeting, missing details about the victim architecture and initial-access chain, uncertainty about the final intended physical effect, and the lack of a verified W1-to-W2 path. This was important because a detailed profile can look complete even when its most consequential claims remain assessments.

## Session 5, September 20 | Threat-Card Landscape

**Duration:** Not recorded

**Outcome:** Created the five card records in `threat-cards/cards.json` and five matching SVG card files.

**Prompt focus:** Choose five actors other than TEMP.Veles, cover at least three actor types, give each one distinguishing evidence, and avoid depicting real people.

Codex suggested a broader candidate list. I chose Sandworm Team, Dragonfly, CyberAv3ngers, DarkSide, and the Maroochy Water Breach insider case because together they cover nation-state, hacktivist, criminal, and insider categories and show different failure paths: unauthorized commands, supply-chain compromise, default credentials, ransomware-driven interruption, and knowledgeable insider misuse. I rejected an all-nation-state set because it would not meet the assignment's purpose or show differences in motivation and resources.

I reviewed each proposed “signature” against the named source. The resulting cards use T1692.001 for Sandworm, T0862 for Dragonfly, T0859 for CyberAv3ngers, T0828 for DarkSide, and T1692.001 for the Maroochy case. I kept CyberAv3ngers as `hacktivist` because that is the persona's public presentation, then separately recorded the government assessment of IRGC affiliation. DarkSide remains criminal rather than Russian state-sponsored. The Maroochy Water Breach Insider card describes the documented case without treating its facts as a generic insider template.

I also changed the RMS lines so none of the cards implies actual RMS targeting. Every entry separates its sourced incident from the hypothetical RMS relevance and includes `what_this_card_cannot_tell_you`. The visual concepts use devices, symbols, or abstract scenes rather than real faces. Codex helped phrase and structure these entries; I chose the actors, checked the classification spread, and required the evidence limits.

I later asked Codex to implement the five designs as SVG because that format keeps the text readable and the source files reviewable. I checked that each card displays the actor, type, signature TTP, MITRE ICS ID, provenance, and a short limits statement. I retained the abstract equipment imagery and the explicit no-person descriptions rather than generating portraits for named or alleged operators.

## Session 6, September 21 | Role Synthesis and Deliverable Review

**Duration:** Not recorded

**Outcome:** Added the W2 role synthesis in the secondary repository and checked the written artifacts for consistency.

**Prompt focus:** Apply the Nation-State Threat Analyst and Insider Threat Investigator roles to my own profile and cards, with the investigator grounded in Anderson rather than MITRE.

I used the nation-state lens to ask where TEMP.Veles-like TTPs could be observed and the insider lens to ask what behavior is actually observable before assigning motive. I required the synthesis to name Anderson's security-usability, credential-stuffing/password-reuse, and password-canary concepts. I shortened the result to one page and kept the negative pivot finding. I then checked the JSON and Markdown for internal consistency and made sure the synthesis did not convert theoretical RMS relevance into fact.

## Reflection

The card exercise made me uncomfortable in a useful way. A compact card forced me to choose one actor type, one signature technique, one date, and one sentence that would represent a complicated and contested history. That made the comparison readable, but it also removed uncertainty. The source did not say that a dragonfly, sandstorm, broken seal, dark pipeline, or transmitter was the correct symbol for an actor. It did not say that one TTP was the actor's defining move. It did not give the actors equal evidentiary status. The card format and the generative tool added those choices.

Anderson's discussion of **authority compliance** helps explain why this matters. A MITRE technique number, government-agency name, formal stat line, and consistent card layout act as authority signals. A reader may comply with the implied judgment—“this actor is known, classified, and relevant”—without reopening the underlying report. The identifier proves that MITRE defines or maps a technique; it does not prove my hypothetical RMS application, settle attribution, or show that the actor will repeat the behavior.

The **halo effect** is also present. Clean typography, matched fields, and attractive art can transfer a feeling of quality from the presentation to the evidence. The prose claim does not become more reliable when placed inside a polished frame, but it feels more finished and therefore more certain. The generative tool intensified this because it could make every actor description sound equally fluent even when the sources differed in strength.

Anderson's treatment of cognitive shortcuts also makes the **availability heuristic** relevant. A vivid image and short “signature TTP” are easier to remember than caveats about associated-group naming or an unverified RMS connection. That memorability can make the pictured scenario seem more likely than the evidence supports. The card's most psychologically available detail may be the least important analytical fact.

I tried to counter this with confidence labels, provenance, and `what_this_card_cannot_tell_you`, but those fields do not fully undo the design. The large actor name and TTP remain the visual conclusion; the limitations remain smaller text. I also noticed that I wanted each card to have a satisfying identity and clean narrative. That desire came from the format, not the intelligence record.

I would want a reader to know that these cards are indexes into sources, not evidence by themselves. “Assessed affiliation” is not the same as proven identity; an indictment is an allegation; aliases can overlap without being exact; a documented technique in one incident does not establish RMS targeting; and a card's artwork is entirely interpretive. For Module 9, the lesson is that an AI-supported nuclear decision aid could be most persuasive precisely when it is most polished. Usability is necessary, but presentation must keep uncertainty, provenance, and dissent visible at the same level as the recommendation rather than hiding them behind it.

**Time spent:** I did not consistently record minutes for research, prompting, source checking, and editing, so I cannot provide a reliable total.
