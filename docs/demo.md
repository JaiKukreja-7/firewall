# Five-to-ten-minute demonstration

1. **Problem (1 minute):** Explain how a flat IT/OT network permits lateral movement. Point to the four zones. Describe this as routed segmentation, not a physical air gap.
2. **Controls (1 minute):** Explain default deny, VLANs, jump-host restrictions, and PAT. Mention that all hosts within a VLAN can still communicate without crossing the gateway.
3. **Positive path (1 minute):** In the browser model, run the scenarios. Show corporate HTTPS and DNS permits, then the two workstations' distinct PAT mappings under one public IP. These are policy-model outputs, not observed TLS handshakes.
4. **Blocked paths (1 minute):** Send Corporate `192.168.10.50` → SCADA `192.168.20.10`, TCP 3389. Show the deny. Try OT → external TCP 443, and jump host → SCADA TCP 23. Both are denied.
5. **Administration (1 minute):** Show jump host → SCADA TCP 3389 permitted, then change source to `192.168.30.11` to demonstrate denial. In Packet Tracer, separately demonstrate real simulated SSH to the gateway.
6. **Evidence and limits (1–3 minutes):** Show unit-test output. If you assembled Packet Tracer, show its own ACL counters, PAT entries and HTTPS traffic. Explain that stateless ACL `established` is weaker than session inspection and industrial DPI remains future work. HTTPS filtering cannot guarantee prevention of ransomware or exfiltration.

Avoid saying all threats are eliminated, internal topology is completely hidden, or simulated permits prove application handshakes. Report exactly what the model and Packet Tracer tests show.
