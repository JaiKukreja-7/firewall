# Assemble the Cisco model

Use Packet Tracer 8.2+ locally. This guide and configurations are a build kit, not a validated `.pkt` artifact. Device commands can vary by simulated IOS; record unsupported commands instead of claiming they worked.

## 1. Place and cable devices

- Two Cisco 2911 routers: `Lab-GW-Router` and `ISP-Router`.
- One Cisco 2960 switch: `Factory-Switch`.
- Corporate PCs, a SCADA Server-PT, a PC labelled PLC (a stand-in, not a real industrial process), Admin PCs, and two external Server-PT devices.

| Device A | Port A | Device B | Port B |
|---|---|---|---|
| Gateway | G0/0 | ISP | G0/0 |
| Gateway | G0/1 | Factory switch | G0/1 |
| Corporate PC 01 | FastEthernet0 | Switch | F0/1 |
| CAD workstation | FastEthernet0 | Switch | F0/2 |
| SCADA server | FastEthernet0 | Switch | F0/3 |
| PLC stand-in | FastEthernet0 | Switch | F0/4 |
| Admin jump host | FastEthernet0 | Switch | F0/5 |
| Security console | FastEthernet0 | Switch | F0/6 |
| ISP | G0/1 | Web Server | FastEthernet0 |
| ISP | G0/2 | DNS Server | FastEthernet0 |

Use auto-connect or appropriate copper cabling. The external DNS segment uses the report's `8.8.8.8` only inside this isolated simulation; it is not connected to Google's actual resolver. ISP does not need routes to private networks because external replies target the PAT address on its directly connected link.

## 2. Address hosts

Use Desktop → IP Configuration; static addresses, subnet mask `255.255.255.0` for all endpoints.

| Host | IP | Default gateway | DNS |
|---|---|---|---|
| Corporate PC | 192.168.10.50 | 192.168.10.1 | 8.8.8.8 |
| CAD workstation | 192.168.10.51 | 192.168.10.1 | 8.8.8.8 |
| SCADA | 192.168.20.10 | 192.168.20.1 | Leave blank |
| PLC stand-in | 192.168.20.50 | 192.168.20.1 | Leave blank |
| Jump host | 192.168.30.10 | 192.168.30.1 | 8.8.8.8 |
| Security console | 192.168.30.11 | 192.168.30.1 | 8.8.8.8 |
| Web Server | 198.51.100.10 | 198.51.100.1 | 8.8.8.8 |
| DNS Server | 8.8.8.8 | 8.8.8.1 | 8.8.8.8 |

## 3. Load configurations and enable SSH

On each router/switch, enter `enable`, then `configure terminal`, then paste the matching file from `configs/`. Start with fresh lab devices; don't replace configurations on real equipment. The files end with `end`.

On the gateway, configure a local username and secret **of your own choosing** using `username labadmin secret <your-local-lab-secret>` in configuration mode. Replace the bracketed text rather than pasting it. Do not put real credentials into the repository. Generate RSA keys using `crypto key generate rsa`, entering 2048 when prompted for modulus (use the largest supported size if the simulated IOS limits it). Domain name and hostname are already set. Confirm `show ip ssh`; VTY access is restricted to the jump host and SSH only.

Run `copy running-config startup-config` on every network device and accept the destination filename. This prompt is normal in the local simulator.

## 4. Configure external services

On Web Server → Services → HTTP, enable HTTPS. HTTP can be disabled. On DNS Server → Services → DNS, enable DNS and add an A record `www.manufacturing.example` → `198.51.100.10`.

SCADA and PLC are labelled stand-ins. Generic Packet Tracer PCs/servers may not offer SSH or RDP listeners. For an actual SSH session use the gateway, whose listener is configured. For permitted admin-to-OT port rules, use Simulation mode / Add Complex PDU to observe forwarding or a supported listening endpoint. A forwarded SYN is **not** proof of an established RDP/SSH session. Do not substitute HTTP and call it RDP.

## 5. Validate and save evidence

First verify `show ip interface brief`, `show interfaces trunk`, `show vlan brief`, `show ip route`, and `show access-lists`. Ensure router physical links are up and switch ports belong to the expected VLANs. ARP can cause the first PDU attempt to time out; inspect events and retry after resolution.

| Test | Action | Required evidence |
|---|---|---|
| Corporate HTTPS | PC browser: `https://198.51.100.10` | Page loads, TCP 443 flow and PAT mapping |
| DNS | Browser: `https://www.manufacturing.example` | UDP 53 query/reply in Simulation mode, page loads |
| PAT multiplexing | Open HTTPS from both corporate hosts | Two inside-local addresses sharing 203.0.113.2 in `show ip nat translations` |
| Corporate → OT block | PC `ping 192.168.20.10`; also TCP 3389/502 Complex PDU | Drop at gateway and corporate deny counter increases |
| Corporate → Admin block | PC `ping 192.168.30.10` | Gateway drop / deny hit |
| Gateway SSH | Jump host command: `ssh -l labadmin 192.168.30.1` | Authentication and router prompt |
| Unauthorized management | Security console attempts same SSH | Session denied by VTY source restriction |
| Telnet | Corporate PC `telnet 192.168.20.10` | TCP 23 dropped at gateway, explicit Telnet deny counter |
| OT Internet block | SCADA `ping 198.51.100.10` | OT deny counter; no OT NAT entry |
| Unsolicited external | External TCP 22 PDU to 203.0.113.2 | WAN default deny counter increases |
| Lab positive ping | Corporate PC `ping 198.51.100.10` | Echo/reply and ICMP PAT entry |
| Admin → OT permitted | Complex PDU from jump host to SCADA TCP 3389 | Forwarded request; response only if listener exists |

Inspect `show ip nat translations`, `show ip nat statistics`, and `show access-lists` immediately after traffic; dynamic entries expire. Capture Simulation-mode packet events and ACL match counts. IOS `log` rendering varies in Packet Tracer; a counter plus the drop event is useful evidence even when syslog isn't rendered. ACL drops usually time out rather than return a connection-refused message.

In particular, test WAN ACL/NAT order on your simulated IOS. The provided rules target `203.0.113.2` at outside ingress, not the private address. Do not weaken the default deny to fix a failure: inspect interfaces, routing, service enablement, ACL hits, and NAT translations to locate it.

Save as `NS-P02_Manufacturing.pkt` after tests. Keep a test record of **passed / failed / unsupported / unrun** checks and screenshots; do not claim the report's historical “100% compliance” for this new lab without your own evidence.
