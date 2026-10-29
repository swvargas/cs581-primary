# Workshop 5 — The Incident

Read this, then go look at your own system's SIEM history. This describes what the plant
saw. Your job is to find your part of it, and to work out the parts you cannot see from
your system alone.

## What happened, as the plant noticed it

At 02:47, the night shift supervisor sees three reactor-coolant readings that do not agree
with one another. That is the moment of discovery. It is not the moment the incident
started.

Investigation over the following hours finds:

- The control data path was compromised about two weeks ago. Corrupted process values have
  been flowing from the control hub to the systems that read it since then.
- During that window, at least two safety-related displays showed readings that did not
  match the true process state.
- Six days ago, someone reached a system using a credential that should have been revoked
  after the last workshop. The physical and logical access record shows the entry; it does
  not show who.
- Radiation and material-accounting records on one system were altered.
- One standby-power status was masked so a problem read as normal.

It is one actor and one campaign. The traces are spread across eight systems, and no single
system's log contains the whole thing.

## Your system is one of the eight

You inherited your system on Friday. It is somewhere in this incident. Some of what touched
it happened before you had the keys. Your own SIEM shows you a slice: it logs reads as a
count every fifteen minutes with no source and no values, and writes with no identity. So
you can see that something happened to your system and roughly when, but not, from your own
logs alone, who did it or where it started.

## The question the deliverables answer

A single cyber campaign has triggered Safety, Security, and Safeguards obligations at once.
Three NRC offices, three notification clocks, three definitions of "resolved." For each
framework: is it triggered, who is notified, by when, and on what regulatory basis. Retrieve
the actual notification timing from NRC's current regulations with the web reader. Do not
state a deadline from memory.

The hard field is the clock. A notification deadline counts from the first observable moment
of the thing that triggers it, and that moment is not in this document. You reconstruct it
from evidence, and some of the evidence is on a classmate's system, not yours.

## Working with the other owners

Use the "W5 Incident Timeline" discussion in Canvas. Post what your system saw: the events,
their times, what you can and cannot tell from them. Read what the other owners post.
You will not be able to set the security clock, or decide whether a safety function was
actually affected, from your system alone. That is the point. The coordination is the work,
and your analysis has to show whose evidence you relied on for the parts you could not see.

The clock doesn't wait. In a real incident an NRC notification deadline does not pause
because another owner has not answered their page. If you are ready and someone you depend
on has not posted yet, pull what you can from the plant-wide SIEM at
siem.plant.sanctumsec.com, log the unconfirmed handoff in the 00 IR Log on the timeline
discussion, and record the dependency in your analysis: the missing piece in `open_questions`
and the fact you could not confirm it in `coordination_gaps`. Naming what you could not
confirm beats waiting past the clock.

## Finding your system's traces

Your system's live SIEM view shows only recent activity, newest first, and a busy system's
window is short. Filter to your system and to high severity to pull the incident out of
routine traffic. Do it early and save what you find. On a high-traffic system the incident
events scroll out of the live window within a day or two as normal traffic piles up, so
snapshot your system's events on your first day. Preserving the log before it rolls is part
of the response, not a workaround.

## How this is graded

The standard Workshop Rubric applies, on the Canvas assignment page: Domain Accuracy, AI
Tool Use Quality, Epistemic Integrity, Analytical Depth, Session Log Quality. Two of them
carry the weight of this particular workshop, so know where the points are:

- Analytical Depth. Your coordination fields and your reconstructed clock cite at least one
  other owner's evidence, and you state a start time you worked out rather than one you were
  handed. Analysis that stops at what your own system shows does not reach the top of this
  criterion.
- Epistemic Integrity. You mark plainly what you could not see from your own system and had
  to get from someone else, and you do not claim attribution the SIEM cannot support. Reads
  are counts without a source; writes have no identity. Saying so is worth more than
  guessing a name.
