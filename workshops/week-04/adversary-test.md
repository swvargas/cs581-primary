# Adversary Test — [System Name]
## CS 581 Workshop 4 | [Your Name] | [Date]

**System:** <!-- your system -->
**Attacks run:** <!-- date range -->

Three attacks drawn from your W2 threat cards, run against the access control policy
you wrote in rbac-policy.md. Run them in this order: design first, then attack, then revise.

---

## Attack A — Insider

**Threat card source:** <!-- which W2 card, which TTP -->
**Hypothesis:** <!-- what you expected to find -->

### What you did

<!--
You hold the role account. You are the legitimate credential holder.
Use access you are entitled to in a way you should not: write a setpoint outside the
band you documented, read points no client of yours has read, stop and restart a service,
clear a log. Be specific about the commands or actions.
-->

### Evidence

<!--
Paste the relevant SIEM events or capture output. What did the system record?
-->

### Result

- [ ] **Executable** — completed as described
- [ ] **Blocked** — stopped by a control; name the control
- [ ] **Untestable** — explain why

### What this reveals about the RBAC policy

---

## Attack B — Supply Chain

**Threat card source:** <!-- which W2 card, which TTP -->
**Hypothesis:** <!-- what you expected to find -->

### What you did

<!--
Undermine something your system trusts: a library, a vendor file, a config a peer
sends, a value taken on faith from upstream. Show the consequence landing on a connected
system, not just your own.
-->

### Evidence

### Result

- [ ] **Executable**
- [ ] **Blocked**
- [ ] **Untestable**

### What this reveals about the RBAC policy

---

## Attack C — Pivot

**Threat card source:** <!-- which W2 card, which TTP -->
**Partner system:** <!-- your assigned pair, e.g., TCS -->
**Partner:** <!-- their GitHub handle -->
**Boundary crossed:** <!-- e.g., L2 → L2, or L3 → L1 -->
**Hypothesis:**

### What you built

<!--
Describe the path from your partner's system to yours (or yours to theirs).
Neither of you is attacking an existing link — you built a new one together.
Document what you created: the connection mechanism, which loopback addresses,
which ports.
-->

### What you did

<!--
Use the path you built. Document the specific actions taken from the attacker's side.
-->

### Evidence

### Result

- [ ] **Executable**
- [ ] **Blocked**
- [ ] **Untestable** — if your partner's system was down: document the attempt and what you confirmed about your own side.

### What this reveals about the RBAC policy

---

## Revised policy items

<!--
List the specific lines or sections in rbac-policy.md you changed after running
these attacks, and why. If you accepted a gap rather than fixing it, say so and give
the reason.
-->

| Item | Changed / Accepted | Reason |
|---|---|---|
| | | |
