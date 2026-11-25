# Workshop 7 scenario

This file is your input. Do not edit it. It is the same for every system.

## What happened

On the morning of Wednesday, November 25, the day shift flagged a hot-leg temperature and a
reactor power reading on the DCS that do not agree with each other. At about the same time
the OT-SIEM's collector delivered a batch of events it had been holding. Its store-and-forward
buffer had stopped forwarding some events and released them all at once.

So the SIEM now holds events whose claimed time is days or weeks old and whose receipt time
is Wednesday morning. The board marks them with its "skew" tag. Some of them are on your system.

Nobody has told you what the incident is. Finding that out is the work.

## What you know for certain

- The events are in the SIEM now. They were not visible before Wednesday morning.
- An event's claimed time is what the reporting system says. Its receipt time is when the
  SIEM got it. Discovery is Wednesday morning. Keep the three apart in everything you write.
- You have owned your system since Wednesday morning. Most of the claimed times fall before that.
- The plant is at power. Nothing has tripped.

## How to pull your slice

- Filter the SIEM by your system and severity `high`. On RPS and PSI filter by `critical`
  instead; those two systems produce many high events of their own.
- The read interface returns only the newest 500 rows. Save your filtered snapshot in your
  repo within 24 hours of the Phase 2 announcement.
- The SIEM shows what was reported. Your system's own log on the host shows what your system
  did. They are different sources. Compare them.

## What you are asked to do

The Canvas assignment has the deliverables. In short:

1. Work your system's slice and record it in `incident-record.md`.
2. Find any reading the plant could not have produced, and show why.
3. Post your evidence under your system in the W7 Incident discussion, and add to the shared
   log in its first post. Tiffany Fuhrmann is incident lead.
4. If the evidence touches a system you used to own, say so in the discussion and hand that
   thread to its current owner. You do not investigate your own tenure. If another owner asks
   you for evidence from the system you hold now, you are its custodian; answer in writing.
5. Decide what you would do to contain it and what you would not, with the Technical
   Specification condition each action would enter.

## Rules for the host

- Record what you find, and propose any containment, in the W7 Incident discussion.
- Get my approval in the discussion before you change a shared service or touch evidence:
  no restarts, no stopping processes, no removing or editing files you did not create.
- Reading is always fine. What looks like clutter may be evidence.

## What this scenario is and is not

The plant is fictional. The techniques come from publicly documented cases, including the ones
the class profiled in Workshop 2. No regulatory answer is given to you; retrieve the rules live.
