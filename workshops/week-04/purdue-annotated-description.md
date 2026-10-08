# Purdue Model Annotation — [System Name]
## CS 581 Workshop 4 | [Your Name] | [Date]

**System:** <!-- your system -->
**Purdue Level:** <!-- where your system sits -->

---

## The topology as the status board shows it

<!--
Describe what the W3 status board and architecture page show about your system's
position in the plant. Which systems are adjacent? Which links were live during W3?
Include a screenshot of your own HMI or service interface here if useful.
-->

---

## Where the board's Purdue levels meet the host's reality

<!--
The status board displays systems by Purdue level. The plant host has no zone
separation — all eight systems run on the same machine, bound to the same loopback
interface. Describe that gap specifically for your system.

A model asked to annotate the topology diagram will probably miss this gap.
If yours did, document what it said and why it was wrong.
-->

---

## Boundary crossings that involve your system

<!--
Which other systems communicate with yours? For each connection:
- What protocol or mechanism?
- Which Purdue boundary does it cross, if any?
- What does the current RBAC policy say about who can initiate it?
- What does the host actually enforce?
-->

| Connected system | Protocol | Boundary crossed | RBAC says | Host enforces |
|---|---|---|---|---|
| | | | | |

---

## Gaps between the diagram and the host

<!--
List the places where the Purdue diagram implies a control that does not exist
on the actual host. These feed directly into the adversary-test.md attacks and
into your RUNBOOK.md.
-->
