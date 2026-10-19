# Workshop 4 — Access Control Policy Design

Deliverables for this week, per the Canvas assignment:

Primary repo, `workshops/week-04/`:

- `rbac-policy.md` — seven roles mapped to Purdue zones, access mechanism named as it actually exists on the lab host
- `purdue-annotated-description.md` — Purdue Model annotated against the real lab topology, not a generic diagram
- `adversary-test.md` — three attacks from your W2 threat cards, run against your system: executable, blocked, or untestable, with evidence
- `RUNBOOK.md` — operator handover document; written so a stranger could bring the system up, understand every point, and know what normal looks like
- `session-log.md`

Secondary repo: `role-analyses/week-04/synthesis.md` (Plant Cybersecurity Manager vs Physical Security Officer)

**Order matters:** design the RBAC policy first, then run the attacks, then revise. Attacking before you write the policy defeats the exercise.

**Repo cleanup:** if your `week-04/` directory contains `ics-security-analysis.md`, delete it — that file is from an earlier template version and is not a W4 deliverable.

The Canvas assignment is authoritative on content, structure, and point values. If this README and the assignment disagree, the assignment wins and please tell me so I can fix this file.

## Deliverable Index and Evidence Status

Reviewed October 18, 2026. All required files exist; that is not a claim that every
required experiment was completed. The operational baseline remains the dated
October 15 collection, not a new live-host verification.

| Deliverable | Contents and evidence status |
|---|---|
| [rbac-policy.md](rbac-policy.md) | All seven roles, allowed/prohibited actions, concrete mechanisms, and explicit unenforceable limits. The raw 200-300 threshold band is procedural, not a server control. |
| [purdue-annotated-description.md](purdue-annotated-description.md) | Dated status-board observation, authenticated HMI screenshot, shared-loopback gap, and boundary-crossing table. Original architecture diagram/page remains unavailable; the W3 link table is explicitly a substitute. |
| [adversary-test.md](adversary-test.md) | W2 card mappings, commands/results, source and SIEM evidence, restoration, and policy revisions. A: Executable. B: Untestable, not run. C: Executable originally, then Blocked only on the tested gateway path. |
| [RUNBOOK.md](RUNBOOK.md) | Account/endpoints, prerequisites, start/stop and read-only checks, complete source-backed point map, polling, peers, monitoring limits, and operator response. |
| [session-log.md](session-log.md) | Recorded partner coordination, original sequencing error, follow-up tests, AI-claim checks, and dated evidence collection. Historical draft entries are retained rather than rewritten as personal attestations. |
| Secondary `role-analyses/week-04/synthesis.md` | Cybersecurity and physical-security lenses, their different boundaries and containment choices, and joint handover obligations. Located in the sibling secondary repository. |

## Outstanding Submission Decisions

1. Supply the original course architecture URL/image and compare its RMS links,
   directions, and Purdue labels with the board and actual endpoints. Do not claim
   diagram review based solely on the W3 table.
2. Retain B as Untestable unless a separately authorized experiment can demonstrate
   an effect at a verified connected consumer. The prepared false-SIEM-telemetry
   script is out of scope and must not be run. Instructor acceptance is unknown.
3. The author must review the selected lab policy band and AI-assisted historical
   entries before submission. Technical review cannot attest to personal review or
   recreate missing contemporaneous evidence. The October 12 policy-first sequence
   violation remains disclosed; later work does not retroactively correct it.

No obsolete `ics-security-analysis.md` remains in this directory. Local tests are
verification of software behavior, not substitutes for live attack evidence.
