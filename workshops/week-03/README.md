# Workshop 3 — Your system: RMS

**Radiation Monitoring System** · Purdue Level 2 · Modbus, Syslog

This is your brief. Everyone in the class has a different system. Together the eight builds
are the plant from the course architecture diagram.

## Your allocation on the lab host

| | |
|---|---|
| Host | `plant.sanctumsec.com` |
| Role account | `rms` |
| Your hostname | `rms.plant.sanctumsec.com` |
| Port block | `5060`–`5069` |
| HMI port | `5060` — served over HTTPS at your hostname |
| Protocol services | `5061` onward — **bind to 127.0.0.1 only** |

### This is a role account, not a personal one

You log in as **`rms`**, the system, not as yourself. Anyone whose public key is in
that account's `~/.ssh/authorized_keys` can operate this system. Right now that is only you.

Two consequences worth holding onto, because W4 is about exactly this:

- `authorized_keys` **is** an access control list. Granting access is adding a line;
  revoking it is removing one. That is the whole mechanism.
- A shared account costs attribution. The login record says `rms`, not your name.
  sshd does log the key fingerprint on every login, so who did what is recoverable, but only
  if someone kept a map from fingerprints to people. Notice which half of that is a
  technical control and which half is a filing decision.

You get access once your public key is committed. See `infra/README.md`.

    ssh rms@plant.sanctumsec.com

To see your own HMI from your laptop before TLS routing is confirmed, tunnel it:

    ssh -N -L 5060:127.0.0.1:5060 rms@plant.sanctumsec.com

## Your links

Your system connects to these. The links come from the architecture diagram, not from me
inventing them. You need at least one working peer link.

| Peer system | Direction | Link | Address |
|---|---|---|---|
| DCS | one-way out | analog + Modbus | `dcs.plant.sanctumsec.com` |
| OT-SIEM | one-way out | syslog / OPC-UA | `ot-siem.plant.sanctumsec.com` |

Peers are named by **system**, not by person. If a peer is down, log the failed attempt and
capture it; a documented failure earns the same credit as a success.

## Bind rules

- **HMI** → your port `5060`, reachable publicly over HTTPS, **basic auth required**.
  An unauthenticated request must return 401.
- **Protocol services** → `127.0.0.1` only. Modbus, DNP3 and OPC-UA authenticate nothing
  and have nowhere to put a credential, so they do not go on a public interface. That gap is
  the finding of the week. W4 is where you design what sits around it.


## What we are doing wrong this week, on purpose

This lab has a security posture you should not copy. Some of it is the protocols, which you
cannot fix. Some of it is shortcuts we took, which you could fix and will be asked to in W4.
Telling those apart is most of the skill.

| What we do | Why it is questionable | Whose fault |
|---|---|---|
| **Shared role accounts.** You log in as `rms`, not as yourself. | The login record names the system, not the person. If three people hold the role, the log cannot tell you which one acted. | **Ours.** Chosen for convenience. |
| **Unauthenticated protocol services.** Anyone who reaches your port can read and write. | There is no credential to present and no identity to check. A write is a write. | **The protocol's.** Modbus and DNP3 have no authentication field. You cannot fix this, only design around it. |
| **Network position is the only control.** Loopback binding is what keeps your protocol service private. | One bind address is a single point of failure. Change `127.0.0.1` to `0.0.0.0` and every control is gone at once. | **Ours.** Real plants layer this. |
| **HTTP Basic auth on your HMI.** | The credential is replayed on every request. No lockout, no session, no second factor, no revocation short of changing it for everyone. | **Ours.** The weakest thing that beats nothing. |
| **Self-asserted SIEM events.** Your token proves which system you are. Nothing proves the event happened. | A monitoring system that trusts its sources completely can be fed whatever the source chooses to say, including silence. | **Ours.** Worth sitting with before W4. |
| **Access never expires.** A key added is a key forever. | No review cycle, no revocation trigger, no expiry. Several of you cited the 31-day account review window in W2. We do not have one. | **Ours.** |

Five of those six are ours, not the protocol's. That ratio is the point.

One of them has a partial answer already built in. Your role account destroys attribution by
default, but sshd records the **key fingerprint** on every login, so who did what is recoverable.
Only if somebody kept a map from fingerprints to people, though. Notice which half of that is a
technical control and which half is a filing decision. That gap is where most real access-control
failures live.

**W4 is the remediation.** You will write the RBAC policy for the plant you are about to build,
map it to Purdue zones, and test whether it stops three TTPs from your own W2 adversary. Every row
above is something you can take a position on there. Keep notes this week on what annoyed you.

## What goes in this directory

    workshops/week-03/
      lab/              your server, HMI, systemd units
      points.md         your point map
      protocol-analysis.md
      network-analysis.md
      capture.pcap
      session-log.md

## Events to the OT-SIEM

Your ingest token is in `~/lab/ASSIGNMENT.txt` on the host once your account exists.
The event API spec is linked from the Canvas assignment. At minimum emit `service.state`,
every `protocol.write`, sampled `protocol.read`, `auth.success` / `auth.failure` from your
HMI, and `process.alarm`.

**One requirement worth reading twice:** at least one event you emit must correspond to a
`detection_opportunity` you wrote in your own W2 adversary profile. Say which one in
`network-analysis.md`. In W2 you said what you would detect. This week you make it emit.

Watch the plant at `plant.sanctumsec.com`.
