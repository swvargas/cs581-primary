# Session Log, Workshop 3
## Santiago Vargas | Codex | October 5, 2026

This log records how I used Codex during Workshop 3, including the evidence I reviewed, the conclusions I challenged, and the revisions made before submission.

## Session 1, October 5 | Requirements and Existing-Build Audit

**Estimated duration:** 25 minutes

**Outcome:** Reviewed the assignment, confirmed the assigned RMS system, and identified the missing deliverables.

**Initial prompt:** “Review and complete my Workshop 3 protocol-security assignment, including the lab audit, protocol analysis, network analysis, packet capture, session log, and role synthesis.”

I used Codex to compare the assignment with the repository. The review confirmed that my assigned system was the Radiation Monitoring System at Purdue Level 2. Its HMI uses port 5060, and its Modbus/TCP service uses port 5061.

The existing repository already contained the dynamic RMS process server, HMI, point map, OT-SIEM event client, test client, and two systemd user units. The protocol analysis, network analysis, packet capture, session log, and secondary role synthesis were still missing.

I asked Codex to organize the remaining work around direct evidence from my running service. I did not want the analysis to rely only on protocol specifications or generic Modbus security statements.

## Session 2, October 5 | Live Service Verification

**Estimated duration:** 35 minutes

**Outcome:** Verified the deployed services, bindings, authentication response, and OT-SIEM behavior.

**Prompt focus:** Check the live RMS build against the assignment and identify any gap between the repository and the deployed system.

I used Codex to connect to the `rms` role account with my existing SSH key and inspect the live services. Both `plant-rms.service` and `plant-rms-hmi.service` were enabled and active. Their status showed that they had remained running for four days.

The socket review confirmed that the HMI was bound to `127.0.0.1:5060` and the Modbus service was bound to `127.0.0.1:5061`. This met the requirement that raw protocol services remain on loopback.

I checked the HMI without credentials through both the public HTTPS hostname and the local port. Both requests returned HTTP 401. This proved that an unauthenticated request was rejected, although it did not prove that Basic authentication was a strong access-control system.

The journal contained accepted `protocol.read` events from the OT-SIEM as well as intermittent delivery timeouts. I kept both results in the analysis because successful delivery alone would hide the possibility of missing monitoring records. The RMS continues running when SIEM delivery fails, but its event queue is held in memory and is not a durable audit record.

## Session 3, October 5 | Packet Capture and Peer Analysis

**Estimated duration:** 45 minutes

**Outcome:** Captured real Modbus/TCP traffic from the RMS service and one peer endpoint.

**Prompt focus:** Capture my service and a peer link without changing the other student’s process.

I used `tcpdump` on the plant host’s loopback interface with a filter for TCP ports 5061 and 5051. During the authorized link test, I issued read-only Modbus function-code 3 requests to the RMS and peer services. I did not send a write request to the peer.

The final `capture.pcap` contains 60 packets. It records TCP handshakes, Modbus Application Protocol headers, transaction identifiers, unit ID 1, function code 3, register offsets, quantities, responses, timing, and exception behavior.

The RMS returned six holding-register values matching the structure of my documented point map. The peer also exposed six valid holding registers and returned Modbus exception code 2 when the request moved beyond its implemented range.

I initially considered identifying the peer solely from its port and the course connection table. That would not satisfy the requirement to reason from traffic. The final analysis instead treats DCS as an assessed identification based on the endpoint’s multi-value register pattern and supervisory behavior. The packet payload does not contain a system name, vendor name, or point labels, so the identity is not presented as certain.

## Session 4, October 5 | Protocol Security and CVE Research

**Estimated duration:** 60 minutes

**Outcome:** Analyzed the observed Modbus exchange and retrieved three relevant CVE records from the NVD API.

**Prompt focus:** Separate native protocol properties from product vulnerabilities and support the conclusions with my capture.

I used Codex to help decode a request and response from the packet capture. The request included a transaction identifier, protocol identifier, message length, unit identifier, function code, starting offset, and requested quantity. The response included the same transaction identifier and the requested raw value.

The transaction and length fields help the client and server process requests reliably, but they do not authenticate a person or device. The captured exchange contained no credential, signature, nonce, message authentication code, or TLS negotiation. The register address and value were readable directly from the packet bytes.

I reviewed the distinction between ordinary Modbus/TCP and the separate Modbus/TCP Security profile. The security profile can use TLS, mutual X.509 authentication, and certificate-carried roles, but those features were not present in my port-5061 capture.

I used Codex to query the official NVD CVE API 2.0 for:

- CVE-2018-7857
- CVE-2024-11737
- CVE-2025-55221

These records describe implementation vulnerabilities involving crafted or out-of-range Modbus requests in named commercial products. I did not treat them as proof that `pymodbus 3.15.0` was vulnerable. Their affected-product lists do not include this lab.

The analysis therefore separates two findings. Traditional Modbus/TCP lacks the security fields needed for authentication and message protection, while individual products can also contain parser and input-validation vulnerabilities documented by CVEs.

## Session 5, October 5 | Compensating Controls and W2 Detection Continuity

**Estimated duration:** 45 minutes

**Outcome:** Evaluated the controls present in the lab and connected the build to my W2 adversary profile.

**Prompt focus:** Identify which compensating controls exist, which are missing, and which W2 detection opportunity the RMS implements.

The controls review found that the build uses loopback binding, SSH-tunneled protocol access, HTTPS for the HMI, Basic authentication, limited writable points, systemd restart behavior, and OT-SIEM event reporting.

The review also identified important limitations. Loopback binding is one configuration setting rather than layered segmentation. Basic authentication has no individual account, session control, lockout, or second factor. The shared role account weakens attribution. SIEM events are self-asserted, and the same process that handles a write can suppress or falsify its report.

I carried forward MITRE ATT&CK for ICS technique T1692.001, Unauthorized Message: Command Message, from my W2 adversary profile. The RMS emits a `protocol.write` event whenever a Modbus client changes an allowed point. The event includes the function code, offset, values, and the W2 detection-opportunity label.

I did not treat that event as independent proof. Traditional Modbus does not identify the human operator, and the RMS is reporting on its own behavior. A stronger design would compare the server event with passive network evidence, SSH key fingerprints, approved work orders, and independent process state.

## Session 6, October 5 | Network Analysis and Secure-Design Requirements

**Estimated duration:** 45 minutes

**Outcome:** Completed the passive-versus-active network analysis and developed testable security requirements.

**Prompt focus:** Explain what an observer learns without transmitting and what additional packets would be required to learn more.

The passive-observation section identifies what is visible to an observer positioned on the Modbus path: endpoints, ports, timing, polling behavior, transaction IDs, unit IDs, function codes, addresses, quantities, exception codes, and raw values. A longer observation period could reveal normal ranges, process cycles, alarm transitions, and unexpected writes.

The active-analysis section explains that a tester would need to send additional read requests to enumerate address ranges, try other unit IDs, or request function 43/14 device identification. Testing write permissions would require actual write requests, which I did not send to the peer because they could alter another student’s system.

The secure-design requirements were written as testable outcomes. They include default-deny network flows, mutually authenticated transport, point-level authorization, strict request validation, independent and tamper-evident logging, detection of telemetry loss, expiring individual access, and safe behavior during communication or monitoring failures.

## Session 7, October 5 | Engineer and General Counsel Synthesis

**Estimated duration:** 40 minutes

**Outcome:** Compared how an ICS/SCADA Engineer and General Counsel would use the same evidence.

**Prompt focus:** Apply both roles without converting engineering guidance into an unsupported legal conclusion.

The engineer’s analysis emphasizes process availability, deterministic behavior, input validation, redundancy, independent monitoring, maintenance windows, and safe failure modes. An access-control improvement that interrupts required monitoring could create its own operational hazard.

The General Counsel analysis emphasizes system scope, attribution, preservation, chain of custody, notification decisions, and defensible statements about what the evidence proves. A shared account, indefinite SSH keys, Basic authentication, and self-reported events complicate attribution and evidence quality.

The roles can recommend different immediate actions. Counsel may favor isolation to contain exposure and preserve evidence. The engineer may oppose disconnecting a monitoring path until an alternate indication is available. The joint recommendation is to define those decisions in advance through an incident runbook that protects both evidence and plant safety.

## Final Review

**Estimated duration:** 20 minutes

**Outcome:** Checked the required files, restored the test configuration, and reviewed the final claims.

I checked the primary and secondary repositories for missing sections, placeholder text, stale template language, formatting errors, and private-key material. I confirmed that the SSH file was a valid Ed25519 public key.

The packet capture showed an alarm-threshold value of 25, or 0.25 uSv/h, left by an authorized test. I restored the live threshold to 250 raw, or 2.50 uSv/h, and confirmed that both RMS services remained active.

I also reviewed every strong conclusion for its evidentiary basis. Direct packet fields and live service results are marked documented. Peer identity, replay exposure, longer-term process inference, and recommended controls are marked assessed. Missing configurations and out-of-scope facts are identified as unknown rather than treated as absent.

## Reflection

**What worked:** Using the running service and a real packet capture produced a stronger analysis than relying only on the Modbus specification. Comparing packet bytes, the point map, source code, socket bindings, HTTP responses, systemd status, and journal records made it possible to distinguish observed controls from assumed controls.

**What did not work:** The first NVD-processing command expected a JSON utility that was not installed, so I changed the retrieval method and reviewed the API responses directly. The first SSH command also inherited a local configuration problem, which I corrected by using an explicit SSH configuration. The short capture supports protocol analysis but is not a long-term operational baseline.

**What I challenged:** I did not treat a port number as conclusive peer identity, a CVE as proof that my Python library was affected, a SIEM event as independent truth, or an HTTP 401 response as proof of strong authentication. I also separated protocol weaknesses from product-specific vulnerabilities.

**What I would do differently:** I would begin with a longer capture plan, record exact test start and stop times, establish a normal-traffic baseline, and coordinate an approved peer-identification request. I would also record configuration values before and after each test so authorized changes cannot be mistaken for unexplained activity.

**Total estimated time:** 5 hours 15 minutes.
