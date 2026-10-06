# Protocol Security Analysis — RMS Modbus/TCP

## 1. Scope, Method, and Observed Exchange

This analysis concerns the Radiation Monitoring System (RMS) simulation running
`pymodbus 3.15.0` on `127.0.0.1:5061`, device ID 1. I captured 60 packets on the
server loopback interface on October 5, 2026. The capture contains RMS traffic on
port 5061 and a peer Modbus service on port 5051. I decoded the Ethernet, IPv4,
TCP, Modbus Application Protocol (MBAP), and protocol data unit fields and compared
them with the running service and `points.md`.

An RMS request in `capture.pcap` contains the bytes
`0001 0000 0006 01 03 0000 0001`: transaction 1, protocol 0, following length 6,
unit 1, function 3, starting offset 0, quantity 1. The response contains
`0001 0000 0005 01 03 02 007e`, exposing the raw value 126, or 1.26 uSv/h after
the documented scale factor. Subsequent requests expose offsets 1 through 5 and
their values. Nothing in the exchange is encrypted.

**Confidence: documented.** The byte values, endpoints, timing, and operation are
direct observations from `capture.pcap`; the scale and meaning of each RMS value
come from the implementation and `points.md`. **Provenance:** local packet capture,
`lab/rms_server.py`, and `points.md`, October 5, 2026.

## 2. Native Security Properties Evidenced by the Capture

The traditional Modbus/TCP profile observed in this capture provides useful transaction
semantics but no observed authentication, authorization, or encryption. The MBAP
transaction identifier lets a client associate a
response with its request. The protocol identifier distinguishes Modbus from other
possible uses, the length supports framing checks, the unit identifier selects a
logical device, and exception responses identify invalid requests. These properties
support reliable processing; they are not proof of identity, authorization, secrecy,
or origin integrity.

The capture demonstrates the distinction. Unit ID 1 is a routing/application value,
not an authenticated principal. Function code 3 and the offsets are visible, and the
server replies without a credential, signature, nonce, or message authentication
code. Transaction identifiers increased sequentially and were accepted, but they do
not provide replay protection because the client chooses them and no freshness or
cryptographic binding is present. TCP supplies ordered, checksummed delivery within
a connection, but an on-path party could still read or alter the application data.
The server also accepted a connection from an ephemeral local port without any
Modbus-layer authentication negotiation.

The Modbus Organization now specifies a separate Modbus/TCP Security profile on
port 802 using TLS, mutual X.509 authentication, and optional certificate-carried
roles. That profile shows that authentication and integrity can be designed around
Modbus messages, but those properties were not present in this port-5061 capture.

**Confidence: documented** for cleartext fields and absence of a security handshake
in this capture. **Confidence: assessed** for replay and modification exposure: the
message structure permits them, but I did not perform either attack. **Provenance:**
`capture.pcap`; Modbus Organization, [Modbus Application Protocol V1.1b3](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf)
and [Modbus/TCP Security v3.6](https://www.modbus.org/docs/MB-TCP-Security-v36_2021-07-30.pdf).

## 3. Known Vulnerabilities: Protocol Weaknesses Versus CVEs

The absence of authentication, authorization, confidentiality, and replay protection
in the observed traditional Modbus/TCP exchange is a protocol/profile weakness, not
a CVE. A CVE identifies a defect in a particular implementation or product.
Conflating the two would incorrectly imply that patching one library adds credentials
to ordinary Modbus/TCP.

I queried the NVD CVE API 2.0 by `cveId` on October 5, 2026. Three records illustrate
what network reachability to an unauthenticated parser can make possible:

| CVE | NVD result | Relevance and limit |
|---|---|---|
| [CVE-2018-7857](https://nvd.nist.gov/vuln/detail/CVE-2018-7857) | Out-of-bounds Modbus variable writes can cause denial of service in specified Modicon M580, M340, Quantum, and Premium versions. NVD CVSS 3.1 is 7.5 High (`AV:N/AC:L/PR:N/UI:N/.../A:H`). | It demonstrates the availability consequence of unauthenticated, malformed writes reaching an affected controller. It does **not** establish that `pymodbus 3.15.0` is vulnerable. |
| [CVE-2024-11737](https://nvd.nist.gov/vuln/detail/CVE-2024-11737) | An unauthenticated crafted Modbus packet can affect confidentiality, integrity, and availability of listed Modicon M241/M251 and M258/LMC058 products. The CNA CVSS 3.1 score is 9.8 Critical. | It shows that input validation and protocol exposure interact. The RMS is not one of the affected products. |
| [CVE-2025-55221](https://nvd.nist.gov/vuln/detail/CVE-2025-55221) | A crafted unauthenticated Modbus/TCP packet can deny service to Socomec DIRIS Digiware M-70 firmware 1.6.9. NVD scores it 7.5 High. | It is a recent example of parser availability risk, not evidence of compromise or applicability to this Python simulation. |

The NVD product lists do not include `pymodbus 3.15.0`, so these records are precedents
for risk analysis rather than findings against this build. The RMS still has an
application-level risk even without one of these CVEs: a reachable
client can use normal, valid function codes to change the alarm threshold or alarm
acknowledgement. That is intended protocol behavior, so a vulnerability scanner may
find no CVE while the operational consequence remains serious.

**Confidence: documented** for the CVE descriptions, affected products, and scores.
**Confidence: documented** that none of the named product lists includes this lab.
**Provenance:** NVD CVE API 2.0 responses for the three IDs, retrieved October 5,
2026; local requirements file and service source.

## 4. Compensating Controls and the Controls Actually Present

| Control | Present in this build? | Evidence and residual risk |
|---|---|---|
| Bind protocol service to loopback | Yes | `ss` and the systemd process show `127.0.0.1:5061`. A bind/configuration change would remove this boundary. |
| SSH tunnel for remote protocol access | Yes, as the intended access path | SSH authenticates and encrypts the tunnel, but Modbus still cannot identify the person once traffic emerges on loopback. The shared `rms` account weakens direct attribution. |
| HTTPS and Basic authentication for HMI | Yes | Unauthenticated requests to both the public hostname and local port returned 401 on October 5. Basic credentials are replayed on each request and there is no lockout, individual account, MFA, or session revocation. |
| Point-level write restrictions | Partial | Code permits writes only to holding offset 3 and coil offset 0 and rejects other addresses. A permitted client is not authenticated, and the documented numeric range depends on application validation. |
| Protocol and authentication event reporting | Partial | The service emits `service.state`, sampled `protocol.read`, every `protocol.write`, HMI `auth.success`/`auth.failure`, and `process.alarm`. OT-SIEM accepted observed events but intermittently timed out; the local queue is bounded and not durable. |
| Network firewall/ACL allowlist and independent sensor | Not demonstrated | Loopback exposure is narrower than a LAN bind, but the capture does not prove host firewall rules, client allowlisting, deep inspection, or an independent passive sensor. |
| Modbus/TCP Security (TLS/mutual certificates) | No | The capture is traditional cleartext Modbus/TCP, not the port-802 security profile. |
| Redundancy, fail-safe behavior, signed configuration, and tested recovery | Not demonstrated | No redundant detector/server, cryptographic configuration protection, or recovery exercise is in scope. |

The `protocol.write` event carries `detection_opportunity: T1692.001 Unauthorized
Message`. It operationalizes my W2 proposal to alert on unauthorized command messages.
It is still self-asserted telemetry: the same RMS process that handles the write tells
the SIEM that it occurred, and can instead lie or remain silent.

**Confidence: documented** for controls observable in source, live status, HTTP
responses, and service logs. **Confidence: unknown** for upstream TLS termination,
host firewall policy, and organizational key-to-person records because I did not
receive their configurations. **Provenance:** live checks on October 5, 2026;
`lab/`; W2 `adversary-profile.json`; NIST SP 800-82 Rev. 3, section 6.2.1.3.

## 5. Secure-by-Design Requirements

A production replacement should meet requirements stated as testable outcomes:

1. Deny protocol access by default and permit only documented source/destination,
   direction, port, unit, and function-code flows across segmented OT zones.
2. Use mutually authenticated, integrity-protected transport, preferably the current
   Modbus/TCP Security profile where all endpoints support it; otherwise use a
   managed security gateway or tunnel without representing that as native Modbus
   authentication.
3. Authorize reads and writes separately by named role, point, permitted range,
   operating mode, and time window. Safety-significant threshold changes should
   require an independent approval or local enable condition.
4. Validate MBAP lengths, unit IDs, function codes, address/count pairs, and values;
   fail closed without crashing or applying partial writes. Fuzz and load test the
   exact deployed parser.
5. Produce tamper-evident, independently collected records containing the human or
   workload identity, source, old and new values, decision, device time, and result.
6. Detect loss of telemetry as an event, buffer through SIEM outages, reconcile after
   recovery, and alarm on mismatches between RMS readings and an independent channel.
7. Use individual, expiring SSH identities; retain a reviewed fingerprint-to-person
   mapping; remove access on role change; and test revocation.
8. Preserve safe process behavior during authentication, network, logging, and HMI
   failures, with documented backups, restoration tests, and manual fallback.

These requirements layer security around the protocol and process instead of claiming
that a password can be inserted into the observed traditional Modbus request.

**Confidence: assessed.** These are design requirements derived from observed gaps,
not evidence that the lab or a nuclear facility implements them. **Provenance:** local
capture and build; Modbus/TCP Security v3.6; NIST SP 800-82 Rev. 3.

## 6. What This Analysis Cannot Determine

This capture cannot determine who operated the client, whether its host was approved,
whether a packet was malicious, or whether an observed value represented the physical
world correctly. Loopback addresses identify a host context, not a person. The capture
does not prove exploitation of any CVE, and the three reviewed CVEs do not apply merely
because this service speaks Modbus.

It also cannot determine the effectiveness of upstream HTTPS/TLS configuration,
firewall policy, SSH key custody, patch management, SIEM retention, alert response,
or recovery procedures. It cannot show that packets absent from this short interval
never occur. The simulation is not a calibrated detector and does not establish the
safety consequence of changing a real plant alarm threshold. Those conclusions would
require asset/version inventory, configuration review, longer independent captures,
identity records, physical-process validation, and authorized adversarial testing.

**Confidence: documented** that these data sources were outside the method. The
absence of evidence here is not evidence that each control is absent.
