# Audit against NS-P02_Report (2).docx

Reviewed the uploaded report's seven objectives, rule matrix R-01–R-09, five test cases, addressing plan and IOS annexure. The report is source material, not proof of this implementation's behavior.

## Evidence from this revision

- Chromium UI test: 20/20 browser policy checks (16 flows, PAT uniqueness, matching HTTPS reply, wrong-source reply rejection, OT RDP reply).
- Browser controls verified: presets, custom denial, invalid IPv4 feedback, reply controls, coverage table, JSON download, reset, desktop and 390px mobile layout without page overflow.
- Existing Python model: six unittest methods pass, including its 16 scenarios, PAT reuse/collision, DNS/HTTPS/admin replies and invalid input.
- No Cisco IOS or Packet Tracer execution. No real TLS/SSH/RDP handshake, SCADA process, PLC operation, ransomware experiment, database sync or industrial DPI.

## Requirement mapping

| Report requirement | Implemented evidence | Remaining limitation |
|---|---|---|
| Objective 1: four isolated zones | UI zones and source/destination policy; VLAN 10/20/30 Cisco switch config | Browser doesn't implement switching. Real VLAN/trunk forwarding remains unrun. Hosts within one VLAN are not isolated. |
| Objective 2: NAT/PAT | Source-port-aware PAT mappings for Corporate/Admin; separate mappings for two workstations | Objective says all zones; annexure explicitly excludes OT. We follow OT isolation and annexure. |
| Objective 3: default deny | Cross-zone catch-all deny; browser timestamped decision log; IOS ACL deny log rules | Browser log is not IOS syslog. Same-VLAN bypass is explicit. |
| Objective 4: HTTPS/DNS/Telnet | TCP 443, UDP 53 only to 8.8.8.8; routed Telnet blocked | Protocol numbers only; no encryption/handshake validation. Telnet within a VLAN cannot be stopped by gateway ACLs. |
| Objective 5: IT/OT isolation and admin | Corporate lateral denies; jump-host SSH and SCADA RDP permits; OT reply match | Access decisions, not running SSH/RDP servers. |
| Objective 5: read-only reporting/database exception | Not enabled | No corporate reporting IP, OT database endpoint, port or direction is specified. Layer 3/4 rules cannot enforce read-only SQL. Need a defined reporting service and DB read-only account/application enforcement. |
| Objective 6: stateful analysis | UI explains session tuple lookup versus stateless ACK/RST ACL; matching/unmatched reply controls | No full TCP state machine, sequence validation, FIN/RST handling, timeout, flood protection, or IOS ZBF configured. |
| Objective 7: empirical validation | Executed policy/UI checks with exportable model evidence | Actual Packet Tracer test cases and packet captures unrun. Report's 100% Cisco compliance not reproduced. |

## Rule matrix differences

- R-01/R-02: restrict SSH/RDP to `192.168.30.10`, rather than the whole Admin subnet. SSH to internal zones/gateway only; external SSH is not enabled. RDP targets SCADA only, not arbitrary OT services. This follows the objective of authorized jump hosts and avoids the matrix's ambiguous “TCP 3389 / Any.”
- R-03: Corporate outbound TCP 443 implemented, after internal zone denies.
- R-04: DNS limited to Corporate/Admin. The report's “All” rule conflicts with its OT isolation annexure. OT is denied all initiated Internet traffic.
- R-05: Corporate initiations to OT denied. The unspecified database exception remains absent.
- R-06: Telnet is denied across routed zones; no claim of same-VLAN enforcement.
- R-07/R-08: unsolicited Internet initiations denied; matching model replies allowed. In a literal ordered ACL, R-07 preceding R-08 could shadow its permit. The Cisco build kit instead permits narrow stateless responses before its final deny, matching the public pre-NAT address at outside ingress.
- R-09: default-deny routed policy implemented.
- Annexure ping exception: Corporate/Admin ICMP echo only to external lab web host. This is a documented diagnostic exception, narrower than the annexure's arbitrary Internet ping permission.

## TC-01 through TC-05

TC-01 PAT mappings and TC-03 IT/OT deny are demonstrated as model outputs. TC-02 HTTPS permit is not observed TLS; TC-04 gateway SSH permit is not an authenticated session; TC-05 OT Internet denial is a rule decision, not measured packet loss. Follow `packet-tracer.md` to obtain actual simulator evidence.

## Claims that need correction in the presentation

Say "segmented network" rather than "air gap." Say "ACL dropped the traffic" rather than "connection refused" unless a reject response was observed. PAT does not completely obscure topology. Segmentation reduces lateral access, but cannot eliminate ransomware or exfiltration over permitted traffic. ACK/RST checks do not establish stateful inspection or guarantee SYN-flood protection. A permit rule alone does not prove a service connection succeeded.

Industrial DPI, USB restrictions, host firewalls and hardware data diodes are recommendations, not implemented lab features. Physical controls and industrial protocol inspection are outside the report's lab scope.

## Read-only reporting supplement

A subsequent no-install local SQLite demonstration now exists: `reporting_demo.py`, described in `reporting-exception.md`. All 13 reporting checks pass; complete Python tests now total 16 passing methods. The proposed dedicated host/service tuple is a new explicit design assumption and is evaluated separately. Local read-only database behavior is verified, but the base dashboard does not enable this exception; actual industrial database synchronization and the proposed TCP 8443 service remain unimplemented. This supplements, rather than retroactively changes, the previous browser-model evidence.
