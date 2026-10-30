# Midterm Scenario — Santiago Vargas (EDGC (Emergency Diesel Generator Controller))

This scenario is fiction at a fictional nuclear plant, grounded in the public reporting you cited this term. Investigation of the enterprise monitoring boundary you mapped in W1 on the ICT-SIEM confirms both of the architectural unknowns you flagged: the facility forwards Level 3 operational logs directly to Level 4 over a persistent TCP session, and the ICT-SIEM hosts an active remediation connector configured with service credentials capable of issuing remote commands back into lower Purdue zones. Consistent with the TEMP.Veles / XENOTIME (TRITON) tradecraft you profiled in W2 (valid accounts, lateral tool transfer over remote services, scripted execution, indicator removal on host, and unauthorized command messages), an actor compromised that ICT-SIEM connector to move into the plant network, staged through the Radiation Monitoring System (RMS, your W2 and W4 system) while clearing local transfer logs, and reached the Emergency Diesel Generator Controller (EDGC, the system you hold now).

At 04:05 UTC today, during a routine review of standby power readiness ahead of a grid-switchyard maintenance evolution, you discover a live discrepancy on EDGC that extends the exact masked-availability pattern and model artifact you analyzed in W5: the EDGC summary status register polled by the control room and SIEM reports Train A and Train B emergency diesels in normal standby readiness with zero active faults, but a raw diagnostic register read on the local controller shows the starting-air solenoid interlock bit latched in a trip-inhibit state and the day-tank fuel register pinned to a static zero value since 21:40 UTC yesterday. The local systemd journal shows an unauthenticated Modbus write to the status-mask register at 21:40 UTC, followed by a six-hour gap in the local audit log, and no physical local-panel gauge reading is reachable from your terminal. From EDGC alone, you cannot verify whether both emergency diesel trains were physically incapable of auto-starting on a loss-of-offsite-power signal during that six-hour window (which determines whether the Technical Specification LCO action clock and 10 CFR 50.72 safety notification clock started at 21:40 UTC or at 04:05 UTC discovery), or whether only the diagnostic registers were corrupted while the mechanical starting-air system remained operable. Respond as the owner of EDGC, coordinate with the current owners your trace implicates, and write your handoff note for Dominick Wheeler, who inherits EDGC next week.

### Evidence Appendix (EDGC)

**Artifact A: Local EDGC Register Dump and Systemd Journal (`2026-10-29T21:40:00Z` to `2026-10-30T04:05:00Z`)**
```text
2026-10-29T21:40:14Z edgc-server[844]: MODBUS_WRITE src="UNAUTHENTICATED" fc=0x06 reg=40009 (Status_Mask_Reg) old=0x0000 new=0xFFFF
2026-10-29T21:40:15Z edgc-server[844]: MODBUS_WRITE src="UNAUTHENTICATED" fc=0x05 coil=0004 (Train_A_B_Start_Air_Solenoid_Inhibit) val=1 (LATCHED)
-- [GAP: No journal entries between 2026-10-29T21:40:15Z and 2026-10-30T03:40:15Z; rsyslog/journald rate-limit & manual flush detected] --
2026-10-30T04:05:00Z edgc-cli[2190]: RAW_VS_SUMMARY_REGISTER_AUDIT
   Holding Reg 40001 (Summary_Standby_Ready, polled by MCR & SIEM): 1 (NORMAL_READY; computed as Raw_Fault_Word & ~Reg_40009)
   Holding Reg 40009 (Status_Mask_Reg):                             0xFFFF (All fault bits masked)
   Input Reg   30004 (Raw_Diag_Fault_Word):                         0x0008 (Bit 3 = Start_Air_Solenoid_Inhibit ACTIVE on Train A & B)
   Input Reg   30006 (Day_Tank_Fuel_Litres):                        0      (Static 0 since service build)
```

**Artifact B: Boundary Connector and RMS Staging SIEM Excerpt**
```json
[
  {"ts": "2026-10-29T21:31:02Z", "siem_id": 124102, "system": "ICT-SIEM", "purdue_level": 4, "severity": "high", "event_type": "connector.cmd", "summary": "L4 remediation connector (10.40.12.88) executed remote script transfer to 10.20.15.10 (rms.L2) over persistent L3->L4 TCP link"},
  {"ts": "2026-10-29T21:36:49Z", "siem_id": 124118, "system": "RMS", "purdue_level": 2, "severity": "high", "event_type": "log.clear", "summary": "RMS staging directory /tmp/.edgc_stage unlinked and transfer log truncated prior to outbound TCP/502 session to 10.20.16.10 (edgc.L1)"},
  {"ts": "2026-10-30T04:00:00Z", "siem_id": 124920, "system": "EDGC", "purdue_level": 1, "severity": "info", "event_type": "status.poll", "summary": "EDGC reported Summary_Standby_Ready=1 (Normal) during switchyard pre-maintenance check"}
]
```

**Artifact C: `/opt/edgc/edgc_server.py` Code Comment and Tech Spec LCO 3.8.1 Note**
```python
# /opt/edgc/edgc_server.py (lines 48-55):
SIM_FUEL_TANK_IMPLEMENTED = False  # Reg 30006 is unmodeled placeholder (always returns 0)
# Coil 0004 (Start_Air_Solenoid_Inhibit) is wired to live auto-start logic: when 1, blocks EDG crank on LOOP signal.
# Plant Tech Spec LCO 3.8.1 Action B / D: Two inoperable EDG trains require restoration of at least one train within 2 hours or entry into Mode 3 shutdown within 6 hours.
```

