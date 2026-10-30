# Midterm — Scenario Exercise

This folder is your midterm. It was placed directly in your repo, already holding your personalized
scenario. Everything here is explained below, so read this file first, then open `scenario.md`.

## What this midterm is

Your scenario is built from your own work across the term: the systems you have held from W1 through
W5, the gaps you flagged in your "What This Map Cannot Tell You" sections, and the threat actor you
profiled in W2. It does two things at once:

1. It traces one campaign from the first system you held, through the systems you held since, to the
   system you hold now, carried out by the actor you profiled in W2. The actor follows you across the
   term, not the plant diagram.
2. It lands on your current system as a live incident and asks you to respond as its owner: classify
   it, analyze it, harden your runbook against it, and hand the situation to the people who need it,
   including the classmate who inherits your system next week.

You have 72 hours from release. It is due Monday, November 2, 11:59 PM MT.

## What is in this folder

- `scenario.md`: your personalized scenario and its Evidence Appendix. Read it first. It names your
  actor, your current system, the incident, the three evidence artifacts you reason from, and the
  classmate who inherits your system next week. This file is your input; you do not edit it.
- The five files below are yours to write. Each is already here as a skeleton: section headings with
  prompts inside HTML comments (the `<!-- ... -->` lines). Replace the prompts with your work. The
  comments do not render on GitHub, so they will not show in your submission; leave them or delete
  them, your call.

## The five deliverables

Write all five in this folder.

- `incident-classification.md`: which of Safety (10 CFR 50), Security (10 CFR 73.54 / 73.77), and
  Safeguards (10 CFR 74 / Part 75) your incident implicates, the NRC notification each one triggers,
  and when each clock starts. Evaluate all three even if one is not implicated; saying why a
  framework is not triggered is a real answer. Retrieve every rule and deadline live from the
  regulations (eCFR), as in W5. Do not state a deadline from memory.
- `technical-analysis.md`: the trace. How your actor reached the system you hold now, the attack
  vector, the systems affected, and the physical consequence chain. Cite your own W1 map rows, W2
  threat card, W4 attack, and W5 evidence by name. Mark what the evidence cannot establish.
- `runbook-update.md`: the changes your current system runbook needs because of this incident. The
  detection or control that would have caught or contained it, stated concretely, and what you fix,
  accept, or defer, with the reason.
- `stakeholder-comms.md`: the notes you owe other people. A short coordination note to each current
  owner your trace implicates, and a handoff note to the classmate who inherits your system next
  week (named in your scenario). Be clear about what you can verify now and what you cannot yet.
- `session-log.md`: your full AI session log. Show the dead ends and the corrections, not only the
  prompts that worked. The prompting is graded on its own.

## How to work

- Read `scenario.md` and its Evidence Appendix before anything else.
- Lean on your prior workshops. The whole point is that this continues your own W1 to W5 thread.
- Pull the regulations live and cite the paragraph. Keep occurrence, discovery, and the notification
  clock distinct, as the regulation text does.

## Submit

Commit all five files to `workshops/midterm/` in this (your primary) repo, and submit the URL to
this folder in Canvas within the 72 hours.

## If this folder is not in your checkout

It was pushed to your `main` branch. If you do not see it, run `git checkout main` then `git pull`.
If `git pull` reports that local changes would be overwritten, run `git stash`, then `git pull`,
then `git stash pop`.

## Points

100 points. The Canvas assignment and its rubric are authoritative; if this file disagrees with
them, the assignment wins, and tell me so I can fix it.
