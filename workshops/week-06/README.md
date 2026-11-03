# Workshop 6 — New System Takeover: Monitoring Strategy & Supply Chain Assessment

This week the plant systems rotate. You hand your current system to the classmate you named in
your midterm, and you take over a new one. The W6 rotation announcement tells you which system you
receive and who you receive it from.

Read this file first, then read what the previous owner left you.

## What this week is

You inherit a system you have not run before. Your first job is to bring it up from the
documentation the previous owner handed you, not from scratch. Then you build its monitoring
strategy and its supply chain assessment.

Two handoffs are being tested at once:

1. The handoff note and runbook update you wrote in the midterm are now in the hands of the
   classmate who inherited your old system. They are grading your handoff by using it.
2. The handoff note and runbook update the previous owner wrote are now yours. You test them here,
   in `startup-gap-log.md`, by bringing the system up and logging where the documentation held and
   where it did not.

The Canvas assignment is authoritative on content, structure, and point values. If this README and
the assignment disagree, the assignment wins and please tell me so I can fix this file.

## What you are given

After the midterm closes, I place two files from the previous owner into this folder:

- `handoff-received.md`: the previous owner's full midterm stakeholder notes (their
  `stakeholder-comms.md`). It holds their coordination notes to other owners and, as its final
  section, the handoff note written to you. The handoff section is the part written for you; the rest
  is context on what the incident touched.
- `runbook-update-received.md`: the runbook changes they made because of the midterm incident
  (their midterm `runbook-update.md`).

These two repo files, plus the system's existing runbook on the host, are your starting point. Do not
edit `handoff-received.md` or `runbook-update-received.md`; they are your input, the same way the
midterm `scenario.md` was. The existing runbook lives on the host, not in this folder, and as the new
owner you keep it the way you kept your W5 system's runbook. Your access to the new system switches
over on the host at the same time, so you can bring it up and confirm what the documents claim.

## The four deliverables

Write all four in this folder.

- `startup-gap-log.md`: bring the new system up using only `handoff-received.md`,
  `runbook-update-received.md`, and the system's existing runbook. Log what the handoff got right,
  what was missing, wrong, or ambiguous, what you had to discover yourself and how, and the first
  thing you would tell the previous owner to fix in their handoff. Separate what you verified on the
  host from what you are still assuming.
- `monitoring-strategy.md`: a consequence-driven monitoring strategy for your new system, using the
  CCE (Consequence-driven Cyber-informed Engineering) method. Top three physical consequences, the
  cyber pathways to each, and the monitoring points that would catch them. Include alert thresholds,
  escalation paths, alert fatigue mitigation, and blind spots.
- `supply-chain-assessment.md`: the top three supply chain attack vectors for your new system, each
  with its confidence and provenance, and the detection opportunities and compensating controls for
  each. Retrieve a current CISA ICS advisory with web search and integrate it into your analysis.
- `session-log.md`: your full AI session log, including how you ran the web search and which CISA
  advisory you retrieved. Show the dead ends and corrections, not only the prompts that worked.

Secondary repo: `role-analyses/week-06/synthesis.md`: Incident Response Coordinator versus Supply
Chain Manager.

Each deliverable below is already here as a skeleton: section headings with prompts inside HTML
comments (the `<!-- ... -->` lines). Replace the prompts with your work. The comments do not render
on GitHub, so they will not show in your submission. Leave them or delete them, your call.

## How to work

- Read `handoff-received.md` and `runbook-update-received.md` before you touch the host. The system is
  already running, so bringing it up means orienting and verifying it against those docs, including
  whether the runbook changes they describe are live on the host or only on paper, not a cold boot.
  Write the gap log as you go, not after.
- Keep occurrence, discovery, and verification distinct. A gap you confirmed on the host is not the
  same as one you suspect from reading.
- Pull the CISA advisory live and cite it. Do not describe an advisory from memory.
- The monitoring strategy and supply chain assessment are about the system you now own, not the one
  you handed off.

## If this folder is not in your checkout

The W6 files are pushed to your repo on `main`. If you do not see them:

```
git checkout main
git pull
```

If `git pull` reports local changes in the way, stash them first, pull, then reapply:

```
git stash
git pull
git stash pop
```

## Submit

Submit the URL to your `workshops/week-06/` folder in Canvas. We evaluate the last commit before
the deadline on the assignment page.
