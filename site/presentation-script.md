## Slide 1: Firewall & NAT Security Lab

This demonstration implements a four-zone policy model for a manufacturing scenario. It runs offline in a browser. Cisco configuration files accompany the model, but I do not claim they have been executed in Packet Tracer.

## Slide 2: Threat model

A flat architecture makes it easier for a corporate compromise to reach critical systems. Segmentation adds checkpoints. Blocking Telnet and unauthorized outbound ports reduces exposure, but allowed HTTPS can still carry harmful traffic.

## Slide 3: Four security zones

The gateway separates Corporate, Factory OT, Administration and the simulated Internet. Corporate initiations to OT and Admin are denied. Hosts within a VLAN bypass gateway filtering, so this is not complete host isolation or a physical air gap.

## Slide 4: Firewall and PAT

Default deny drops routed flows unless a rule permits them. PAT maps allowed outbound flows to one public address with distinct ports. It does not guarantee topology secrecy. Cisco established ACL rules inspect ACK or RST flags rather than tracking sessions.

## Slide 5: Verification results

I can show the browser validation suite, PAT table, decision log, matching replies and rejected wrong-source replies. Automated tests also evaluate the limited syntax used by our Cisco ACLs. These are model and static analysis results, not observed IOS counters or encrypted application handshakes.

## Slide 6: Limits and recommendations

A separate real SQLite demonstration now verifies read-only telemetry queries and rejected writes. A narrow reporting exception is modeled for Corporate host 192.168.10.60 to OT service 192.168.20.10 on TCP 8443. This is an explicit design assumption, not a running network service. Industrial inspection and hardware one-way gateways are future controls. The original Cisco execution requirement remains unfulfilled.