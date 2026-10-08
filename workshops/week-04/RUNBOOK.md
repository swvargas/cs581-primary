# Operator Runbook — [System Name]
## CS 581 | [Your Name] | Last updated: [Date]

This document is written for a person who has never seen this system.
After W4, your system changes hands. The person taking it over for W5 will use this
to bring it up, understand what every point means, and know what to look for.

---

## System identity

| | |
|---|---|
| System | <!-- e.g., Turbine Control System (TCS) --> |
| Role account | <!-- e.g., tcs --> |
| Hostname | <!-- e.g., tcs.plant.sanctumsec.com --> |
| Purdue level | |
| Protocol | <!-- e.g., Modbus TCP --> |
| Port block | |
| HMI URL | |

---

## Starting the system

```bash
# Commands to start the server and confirm it is running
```

**How to confirm it started:** <!-- what to check — a port, a log line, the HMI loading -->

---

## Stopping the system

```bash
# Commands to stop cleanly
```

---

## Point map

Every register or coil this system exposes, what it represents in process terms,
its normal range, and what an out-of-range value means.

| Address | Type | Name | Normal range | Out-of-range means |
|---|---|---|---|---|
| | | | | |

Source: `points.md` in `workshops/week-03/lab/`. If that file and this table disagree, this table is wrong — fix it.

---

## What normal looks like

<!--
Describe a normal polling cycle: who polls, how often, what function codes, typical values.
A stranger should be able to look at live traffic and say "yes, this is normal" or "something is different."
-->

---

## Known peer connections

Which other plant systems connect to this one, under what conditions, and what they send.

| Peer system | Direction | Protocol / port | Notes |
|---|---|---|---|
| | | | |

---

## SIEM and monitoring

How events from this system reach the OT-SIEM. What gets logged. What does not.

**Known monitoring gap:** <!-- from W3 and W4 analysis -->

---

## Known weaknesses from W4

The three attacks from adversary-test.md, summarised for an operator:

1. **[Attack A type]:** What it did, whether it was blocked, what to watch for.
2. **[Attack B type]:** What it did, whether it was blocked, what to watch for.
3. **[Attack C type — pivot]:** What path was built, what it revealed.

---

## What to do if something looks wrong

<!--
Concrete steps: who to contact, what to log, what not to do.
This does not need to be a full incident response plan — that is W5.
It needs to be enough that an operator can make a sensible first move.
-->
