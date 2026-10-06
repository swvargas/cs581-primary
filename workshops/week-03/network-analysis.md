# Network Analysis — RMS and One Peer Link

## Capture and Method

I captured `capture.pcap` on the plant host loopback interface on October 5, 2026.
The file contains 60 packets selected by `tcp port 5061 or tcp port 5051`. During an
authorized link test, I used a Modbus client to issue read-only function-code 3 requests
to the RMS service and the peer. No write was sent to the peer. I examined TCP endpoints
and flags, MBAP fields, protocol data units, response values, timing, and exception
behavior.

The capture is intentionally narrow. It is evidence of these exchanges, not a complete
inventory or a statistical baseline.

**Confidence: documented. Provenance:** `capture.pcap` and the capture command run on
the live plant host, October 5, 2026.

## My Service: RMS on 127.0.0.1:5061

The client completed a TCP handshake and issued six Modbus/TCP read-holding-register
requests to unit 1. The requests used sequential transaction IDs and read one register
at offsets 0 through 5. Responses returned the values 126, 169, 234, 25, 98, and 33218
at the moment sampled. The first five correspond structurally to 1.26 uSv/h, 169 CPS,
23.4 C, a 0.25 uSv/h threshold, and 98 percent health under the committed RMS point
map. Offset 5 is a changing sample counter.

The capture reveals that the service uses Modbus/TCP, unit ID 1, function code 3,
six contiguous holding registers, two-byte unsigned representations, and no encrypted
or authenticated application layer. It also reveals query ordering and response
latency. The address and values are readable directly from packet bytes.

The unexpectedly low threshold of 25 was the residue of an earlier authorized lab
test, not evidence of an attacker. This is an example of why traffic shows an action
or state but does not establish intent. I restored the configured threshold after the
capture.

**Confidence: documented** for endpoints, fields, and raw values. **Confidence:
assessed** for semantic labels because the packet carries no point names or units;
those meanings require `points.md`.

## Identifying the Other Student System from Traffic Alone

The second endpoint listened on `127.0.0.1:5051`, accepted Modbus/TCP unit 1 function
3 reads, and returned six valid holding-register values: 3229, 1547, 999, 1000, 800,
and 10 during the live probe. Reads above its implemented range returned Modbus
exception code 2 (`Illegal Data Address`). The peer therefore behaves like a compact
controller or supervisory aggregation service with a six-register process map.

My identification is **DCS (Distributed Control System), confidence: assessed**. The
evidence for that inference is the endpoint's multi-value register set, repeated
supervisory-style measurements, and behavior as a Modbus aggregation endpoint. I did
not rely on a banner, DNS name, process list, repository, or statement from the other
student when interpreting the packets. Crucially, the payload contains no ASCII system
label, vendor name, or point map, so “DCS” is not directly proven by the payload. A
blind analyst without architecture or port-allocation context could defensibly conclude
only “a second Modbus server with six implemented holding registers.”

That limitation is analytically important: protocol and behavioral fingerprinting can
narrow device role, but assigning a plant function from six unlabeled integers risks
confirmation bias.

**Confidence: documented** for the endpoint, function, values, and exception.
**Confidence: assessed** for DCS identity. **Provenance:** `capture.pcap` and read-only
live probe, October 5, 2026.

## What a Passive Observer Learns Without Sending a Packet

An observer positioned on this path can learn, without transmitting:

- communicating IP addresses and TCP ports, connection timing, duration, direction,
  volume, and polling periodicity;
- that the application is Modbus/TCP from the MBAP layout and function codes;
- transaction IDs, unit IDs, read/write function codes, start addresses, quantities,
  exception codes, and all returned raw values;
- which points change, approximate process cycles, normal ranges, and likely alarm or
  control transitions after enough observation;
- when a client writes a coil or register, including the new raw value, even though
  traditional Modbus supplies no authenticated operator identity; and
- outages or degraded behavior from resets, retries, missing responses, latency, and
  exception patterns.

The observer does not need to scan or query to obtain this information if legitimate
traffic crosses the observation point. On this host, however, loopback binding means
an ordinary observer on an external network would not see the raw protocol flow; the
observer must already have access to the endpoint host, an SSH tunnel endpoint, or a
monitoring point where the traffic is visible.

**Confidence: documented** for fields present in this capture and **assessed** for
longer-term process inference, which would require a longer sample.

## What an Active Observer Would Have to Send to Learn More

To enumerate the point map, a client could send function-code 1, 2, 3, or 4 reads over
candidate offsets and use successful replies and exception code 2 to identify valid
ranges. It could request function 43/14 (`Read Device Identification`) to test whether
the server exposes vendor, product, revision, or model objects. It could vary unit IDs
to discover logical devices and observe timing and exception differences. Those are
active packets and should require authorization because even reads can load fragile
devices, change audit state, or trigger implementation defects.

To learn write permissions, a client would have to send write-single or write-multiple
coil/register requests. I did not send such requests to the peer because that would
change another student's system. A production assessment should use an approved test
window, safe values, owner coordination, rollback steps, and independent process
observation.

**Confidence: documented** that these functions are defined by Modbus and that the
capture already showed exception-based range information. **Confidence: unknown** as
to which additional functions the peer implements because I did not probe them.

## Detection Opportunity Carried Forward from W2

My W2 profile proposed alerting on unauthorized command messages under MITRE ATT&CK
for ICS T1692.001. The RMS emits a `protocol.write` event for every accepted Modbus
write, including the function code, offset, values, and the detection-opportunity
label. This provides an observable event when a client changes the alarm threshold or
acknowledgement point.

The event is not proof of authorization or independent proof that the write occurred.
Traditional Modbus provides no user identity, and the source process can suppress or
forge its own event. A stronger detection design would compare passive network records,
server events, approved work orders, SSH key fingerprints, and independent RMS state.

**Confidence: documented. Provenance:** W2 `adversary-profile.json`, T1692.001 entry
and detection opportunity; `lab/rms_server.py`; observed OT-SIEM acceptance in the
live service log on October 5, 2026.

## What This Network Analysis Cannot Determine

The capture cannot identify the human behind a connection, distinguish maintenance
from attack intent, validate physical sensor truth, prove a complete point map, or show
traffic outside its short filter and interval. It cannot establish that the inferred
peer is a DCS from payload alone. It also cannot prove firewall rules, tunnel policy,
TLS termination, SIEM receipt of every event, or the absence of compromise.

A longer independent capture, approved device-identification query, peer point map,
host and firewall configurations, identity records, and a known physical/process test
would be required to answer those questions.
