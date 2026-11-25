# Readiness Handoff

<!--
Phase 1. Written for the system you hold NOW, for the classmate who takes it over on
November 24. One page. A new owner should be able to act on it at 2 AM without you.
Book: Section 2.1 (Written Authorities) and Section 4.4 (Pre-Plan for Staff Turn-Over).
-->

## System, owner, date

SFPCM (Spent Fuel Pool Cooling & Monitoring), Purdue Level 1, account `sfpcm` on plant.sanctumsec.com. From Tamas Gyalay (W6 owner) to Santiago Vargas at the 2026-11-24 rotation. Revised 2026-11-25T01:02Z, after the 6:00 PM MT deadline. The version submitted at the deadline is commit `856ecdd` in my repo.

**State at handoff, checked on the host 2026-11-25T00:33Z (5:33 PM MT on 2026-11-24).** Controller and HMI running. Pump 1 on at 1,747 rpm, pump 2 off, makeup open. Pool at 30.3 °C and 12,483 mm, flow 1,657 L/min, no alarm. Threshold 45 °C, revision 2. The journal shows no coil write, alarm, service start, threshold change or HMI login since 2026-11-17T03:11:22Z.

The procedures are in the runbook, `/home/sfpcm/RUNBOOK.md` (SHA-256 `31003236…`). Section names in quotes below are its sections. The book's advice for turnover is a frequently updated set of SOPs (*11 Strategies of a World-Class Cybersecurity Operations Center*, MITRE 2022, Section 4.4, p. 113). On this system that's the runbook, last updated 2026-11-17.

## What this system protects, and why it matters to the plant

<!-- The physical function, the consequence if it is wrong or unavailable, and whether it is
safety-related. -->

SFPCM commands the pool's two cooling pumps and its makeup valve, and reports temperature, level and flow. With the pumps off, this build's pool settles near 50 °C, above the 45 °C alarm. With makeup closed, the level falls to 11,000 mm, below the 11,500 mm alarm. No alarm starts a pump or opens the valve. The course materials class SFPCM as safety-critical, and as a safety-related CDA. These are simulation values, documented for this build ("What normal looks like").

**At 2 AM.** A controller restart sets the three command coils to off: pump 1 run, pump 2 run and makeup valve open. Nothing puts them back. On 2026-10-14 that raised both alarms inside 5 minutes, and they stood for 34 days, until I wrote the coils on 2026-11-17 (host journal). Until the controller restores its commands at startup, the owner re-applies them by hand: pump 1 on, pump 2 off, makeup open ("Intended command state"). Run the preserve block before the write. The coil state as you find it is the evidence of what happened, and your write replaces it. The block's diagnostic step is a comment, so run it by hand before the block's last line ("Preserve before operating"). Without it, no saved file records the coils, level, flow or pump speeds as found. The coils could only be rebuilt from the journal's write events.

## Authorities

<!-- Who may disable a connection, trip, restart, change a setpoint or rotate a credential, and
with whose agreement. Say what the owner may do alone and what needs someone else. -->

This section says what the owner may do and who has to agree. The runbook says how. That's the split the book gives a charter (Section 2.1.1, p. 41). The rows cover the two charter authorities that fit one system: applying countermeasures, such as disabling a connection, and gathering and keeping digital artifacts (Section 2.1.2, p. 42).

The instructor is the only approving authority. Two rules are written down.

- **W6 rule.** Post the change before making it, and add a change-log line after. No sign-off is needed ([W6 Handover](https://boisestatecanvas.instructure.com/courses/48925/discussion_topics/1205724) topic text, and [the instructor's reply to my gap log on 2026-11-15](https://boisestatecanvas.instructure.com/courses/48925/discussion_topics/1205724?entry_id=7100501)).
- **W7 rule, from tonight.** Get the instructor's approval in [W7 Incident](https://boisestatecanvas.instructure.com/courses/48925/discussion_topics/1212457) before changing a shared service or touching evidence. It names restarts, stopped processes, and removing or editing files you didn't create. Reading is always fine.

The W7 rule says no restarts, with no exception. So it covers SFPCM's own controller and HMI, including the HMI restart that a password rotation needs. Its file limit is written under changing a shared service or touching evidence. So I read it as service files and evidence, not the owner's runbook, which the W7 text doesn't mention.

**Who to tell.** Tiffany Fuhrmann is incident lead and the W7 DCS owner. The lead keeps [the 00 log](https://boisestatecanvas.instructure.com/courses/48925/discussion_topics/1212457?entry_id=7123752) in order. The thread gives the lead no approval role. Every finding or action gets one line there: time (UTC), who, what was found or done, and what's still open. Keep event time and receipt time apart. The evidence goes under [the SFPCM post](https://boisestatecanvas.instructure.com/courses/48925/discussion_topics/1212457?entry_id=7123757).

| Action | Who may do it | Agreement needed from | Where this is written |
|---|---|---|---|
| Read anything. Run the preserve block. | Owner | None | W7 rule, "Preserve before operating" (documented) |
| Re-apply the intended pump and makeup valve commands (FC5, coil offsets 0 and 2) | Owner | None. Preserve first. Don't wait for a reply. | "Intended command state." The W7 rule doesn't name coil writes, so this is my reading (inferred) |
| Put the alarm threshold back to 45 °C | Owner | None. Preserve first, since it copies `parameter.json`. | "Recovery." Same reading (inferred) |
| Give another owner evidence from SFPCM: journal lines, diagnostic output, copies from the evidence directories | Owner | None. Answer in writing in W7 Incident. Leave out `hmi.env`, `credentials.json` and the SIEM token. | W7 rule: the owner is the system's custodian (documented). The exclusions follow "Preserve before operating" (inferred) |
| Edit the runbook and append to its change log | Owner | None. Post first. Preserve first, since it copies the runbook. | W6 rule. The W7 file limit is about service files and evidence (inferred) |
| Any other coil write or threshold value | Owner | Instructor | This handoff (inferred) |
| Restart or stop the controller or the HMI. Rotate the HMI password, which restarts the HMI. | Owner | Instructor | W7 rule, "Handover procedure" (documented) |
| Remove or edit anything in `~/lab/w4-evidence/`, `w4-backups/` or `w6-evidence/` | Owner | Instructor | W7 rule (documented) |
| Trip | Not possible | SFPCM has no trip function. The nearest action is a coil write, above. | "Point map" (documented) |
| Disable one connection | Instructor, as root | The owner asks in W7 Incident. A firewall rule that matches the sender's account could block one peer, since each system runs under its own account. The `sfpcm` account can't install one and has no sudo. Without it, the owner's only cut is stopping the controller, which cuts every peer. | Checked on the host 2026-11-25: `nft` answers "you must be root" (documented). The rule itself is untested (theoretical) |
| Start the gateway on 5022, or issue its tokens | Nobody during W7 | It stays closed | My decision. State is in "Final temporary-access teardown" (documented) |
| SSH keys, other accounts, the SIEM, a reboot | Instructor | None | "SSH access and credentials" (documented) |

## What data it produces, and what it does not

<!-- Points, events and logs; where each one lands; how long it is kept. Then the gaps: what
this system cannot tell you. -->

| Data | Where it lands | Kept | Confidence & Provenance |
|---|---|---|---|
| Six registers, three coils | Modbus 5021, on request. The HMI shows the registers only. | Not stored | documented, "Point map" |
| Events: service starts, coil writes, sampled reads, alarms, HMI logins, threshold changes | The user journal, then an HTTPS POST to the course SIEM | Journal back to 2026-09-29. The SIEM board shows the newest 500 rows per system. | documented, host journal and "SIEM and monitoring gaps" |
| Loop status and the threshold | `~/lab/w4-state/` | Overwritten in place | documented, "System identity and files" |

It can't tell you who wrote a coil or who reached the HMI. Writes carry no identity, and every HMI request arrives from 127.0.0.1. It can't tell you an alarm is still standing, since alarms are sent on change only. FC2 reads, FC4 reads and rejected register writes leave no event. Every value comes from one process, so nothing here shows whether the controller is honest.

Nothing notifies anyone. I found no alerting on the SIEM board ("SIEM and monitoring gaps"). An alarm reaches the owner only when the owner looks. That's how both alarms stood for 34 days.

## Links to other systems

<!-- Each link in and out: the other system, direction, what crosses it. -->

| Other system | Direction | What crosses it | Confidence & Provenance |
|---|---|---|---|
| Course SIEM | Out | Event JSON over HTTPS, with the account's token | documented, "SIEM and monitoring gaps" |
| DCS (W7 owner: Tiffany Fuhrmann) | In, 5021 | A connect-and-close check about every 2 seconds. My W3 capture found no Modbus request in it. | documented. Checked on the host 2026-11-25T00:43Z: 31 closed connections to 5021 in about a minute, and all 20 sampled client sockets belonged to the `dcs` account. It isn't in the runbook's peer table. |
| Course status board probe | In, HMI and 5021 | FC3 reads of the holding registers from offset 0, and one HMI request with no credentials, logged as `auth.failure`. It runs when someone opens the status board. | documented. Part of the course build since W3, when I captured it. [The instructor confirmed how it runs on 2026-11-17](https://boisestatecanvas.instructure.com/courses/48925/discussion_topics/1205724?entry_id=7111733). |
| Public URL visitors | In, HMI | HTTPS through the host's proxy, arriving from 127.0.0.1 | inferred |
| RMS, through the gateway on 5022 | Closed | Nothing since 2026-10-14 | documented, "Known peer connections and boundaries" |

Nothing separates the systems. Any account on the host can reach 5021, and the controller accepts coil writes from all of them. That's a gap, not permission. Each owner is limited to their own account and the scope the instructor authorizes (runbook header). So another owner asks in the thread before reading or writing 5021 outside the links above.

## Open items

<!-- Anything unfinished, unexplained or left running. Be complete. The next owner inherits
all of it whether or not you write it down. -->

1. **HMI password.** I set it on 2026-11-17 and still know it. Rotate it, with approval ("Handover procedure").
2. **Pump and makeup valve commands don't survive a controller restart.** The three command coils reset to off. The fix, restoring them at startup, isn't built.
3. **Runbook.** It still names me as owner. Its peer table doesn't list the DCS connect check. It calls the status probe a regular poller, though the instructor says it runs when someone opens the status board. Its change log has no line for my read-only check at 2026-11-25T00:33Z. Its preserve block leaves the diagnostic as a comment, above the hash line. Making it a command would close that.
4. **Deferred code changes, none built.** Logging rejected register writes, a SIEM-to-journal comparison, and a clock record ("SIEM and monitoring gaps"). In W6 I also proposed a status heartbeat and a longer SIEM timeout. Neither is on the host.
5. **Untested or unexplained.** Coil offsets 3 to 47 likely accept writes ("Point map"). 83 `auth.failure` events from 2026-10-20 to 2026-11-08 don't match the probe, and are most likely page visitors ("SIEM and monitoring gaps").
6. **Left on the host.** The controller (running since 2026-10-14T01:05:12Z), the HMI (since 2026-11-17T03:08:23Z), `~/lab/w6-evidence/20261117T030805Z`, and the W4 evidence and backups. `sfpcm-vendor-update-B.py` in the backups is deliberately corrupted. Never install it.
7. **My SIEM archive.** I've pulled the board every 3 hours since 2026-11-08 into a private repo. It doesn't transfer. Ask me in the thread for rows that have rolled off.
8. **First check.** If your first diagnostic reads near 50 °C with zero flow, the controller restarted or someone wrote the coils ("No-command reference state").

## Confidence & Provenance

<!-- What you verified on the host, what you were told, what you are assuming. -->

- **Verified on the host, 2026-11-25T00:33Z.** The state at the top, the controller's hash (`59568abd…`), the gateway stopped and disabled, no crontab, and one key in `authorized_keys`, mine. The instructor hadn't replaced it yet. The DCS connect check, at 00:43Z. The same journal filter, started earlier, returns my 2026-11-17 coil writes, so its empty result since then isn't a broken filter.
- **Verified earlier, 2026-11-08 to 2026-11-17.** The point-map tests, the login-failure attribution, and the password rotation (runbook change log, and [my gap log post in W6 Handover](https://boisestatecanvas.instructure.com/courses/48925/discussion_topics/1205724?entry_id=7091978)).
- **Told by the instructor.** The W6 and W7 rules, and that the status probe runs only when someone opens the status board.
- **Assumed.** That the W7 rule's file limit means service files and evidence, not the owner's runbook. That the owner may re-apply the commands and the 45 °C threshold without waiting. The instructor hasn't confirmed either.
