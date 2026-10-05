from pathlib import Path
from datetime import datetime
from html import escape
import json, webbrowser

folder = Path.home() / 'Desktop' / 'NS-P02-Model'
folder.mkdir(parents=True, exist_ok=True)
links = []
for name in ['dashboard.html']:
    file = folder / name
    if file.exists():
        links.append(('Open network dashboard', file.as_uri()))
reports = sorted(folder.glob('reporting-*/report.html'), key=lambda p: p.stat().st_mtime)
if reports:
    links.append(('Open read-only database results', reports[-1].as_uri()))
    evidence = reports[-1].parent / 'evidence.json'
    if evidence.exists():
        links.append(('Open database evidence JSON', evidence.as_uri()))

slides = [
('Firewall & NAT Security Lab', 'NS-P02: Manufacturing Company. An offline four-zone policy simulation, with a real local read-only database demonstration. No additional software installation is needed.'),
('Threat model', 'A flat IT/OT network exposes factory systems to lateral access from compromised corporate hosts. Cleartext Telnet and uncontrolled egress add risk. Segmentation reduces exposure; it does not eliminate every threat.'),
('Four security zones', 'Internet: gateway 203.0.113.2. Corporate: VLAN 10, 192.168.10.0/24. Factory OT: VLAN 20, 192.168.20.0/24. Admin: VLAN 30, 192.168.30.0/24. Jump host: 192.168.30.10.'),
('Firewall and PAT', 'Default-deny routed policy. Corporate/Admin may use HTTPS and approved DNS. The jump host may use internal SSH and SCADA RDP. Ordinary Corporate-to-OT flows, OT Internet access and routed Telnet are denied. PAT maps permitted Corporate/Admin flows to 203.0.113.2.'),
('Verification and reporting', 'Cloud checks: 20 browser checks and 16 Python test methods passed. Static ACL analysis covered 5,334 Corporate boundary cases and 253 Admin source cases. The separate reporting demonstration passed 13 checks, including real SQLite reads and rejected writes. Its proposed narrow exception is host 192.168.10.60 to service 192.168.20.10 TCP 8443; no actual network service runs on that port.'),
('Conclusion and limitations', 'The no-install simulation and local database demo are complete. Packet Tracer execution, real VLAN forwarding and actual TLS/SSH/RDP sessions are unverified. Reply matching is not a full stateful firewall. Industrial DPI, endpoint hardening, USB controls and data diodes remain recommendations.')
]
coverage = [
('Four-zone design', 'Implemented as a policy model; actual Cisco VLAN forwarding unrun.'),
('Default deny and logging', 'Model decisions and logs verified; Cisco runtime logging unrun.'),
('PAT, HTTPS and DNS', 'Model decisions and mappings verified; actual TLS/DNS traffic unrun.'),
('IT/OT and jump-host rules', 'Simulated permissions verified; actual SSH/RDP sessions unrun.'),
('Read-only reporting', 'Real local SQLite read-only enforcement verified. Dedicated-host exception simulated separately; no actual cross-zone database service.'),
('Stateful analysis', 'Reply-tuple checks demonstrated; TCP state machine, teardown and expiration absent.'),
('Empirical validation', 'Browser, Python and local SQLite evidence available; original Packet Tracer tests unrun.'),
('Production recommendations', 'Industrial DPI, USB restrictions and data diodes documented, not deployed.')
]
page = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NS-P02 Final Project</title><style>
body{font:16px system-ui;background:#0a1220;color:#dbe6f2;max-width:1100px;margin:auto;padding:24px}
h1,h2{color:#65ddc0}p{line-height:1.7}section{padding:24px;background:#111f33;border:1px solid #34465f;border-radius:12px;margin:20px 0}
a{display:inline-block;color:#65ddc0;margin:10px}button{padding:12px;background:#193f43;color:white;border:1px solid #65ddc0;border-radius:8px;cursor:pointer;margin:5px}
table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:12px;border-bottom:1px solid #34465f}.scroll{overflow:auto}
.presenting .slide{min-height:65vh}.presenting .slide h2{font-size:36px}.presenting .slide p{font-size:25px}
@media print{body{background:white;color:black;padding:0}h1,h2{color:black}section{background:white;border:0;break-inside:avoid}button,nav{display:none}}
</style></head><body><h1>NS-P02: Final No-Install Project</h1>
<p>Manufacturing Network Security Policy Simulation with Read-Only Reporting</p>
<button onclick="window.print()">Print report / Save as PDF</button>
<button onclick="document.body.classList.toggle('presenting')">Toggle presentation layout</button>
<nav>'''
for label, url in links:
    page += '<a href="' + escape(url, quote=True) + '" target="_blank" rel="noopener">' + escape(label) + '</a>'
if not links:
    page += '<p>No earlier demonstration files were found in this folder. This report can still be read independently.</p>'
page += '</nav><section><h2>Executive summary</h2><p>The no-install edition implements a browser-based manufacturing network policy model and a separate real local SQLite read-only demonstration. It prepares design, model behavior, evidence and a six-slide presentation. It does not reproduce Cisco Packet Tracer or complete the original Cisco execution requirement.</p></section>'
page += '<section><h2>Verification record</h2><p>Cloud verification: 20 browser checks, 16 Python test methods and 13 reporting checks passed. These counts describe different suites and should not be combined into one test total. Static ACL checks included 5,334 Corporate boundary cases and 253 Admin source cases; they do not prove IOS syntax acceptance or actual packet forwarding.</p></section>'
page += '<section><h2>Requirement audit</h2><div class="scroll"><table><tr><th>Requirement</th><th>Status</th></tr>'
for requirement, status in coverage:
    page += '<tr><td>' + escape(requirement) + '</td><td>' + escape(status) + '</td></tr>'
page += '</table></div></section>'
page += '<section><h2>Database design supplement</h2><p>The dedicated Corporate reporting host is assumed to be 192.168.10.60, targeting a proposed OT HTTPS reporting service at 192.168.20.10 TCP 8443. This is a new documented design assumption, not a field specified in the original report. The separate demo enforces SQLite mode=ro, query_only and a restricted authorizer. Reads succeed; writes, schema changes, read-only overrides and database attachment fail. The base dashboard retains strict Corporate-to-OT denial. No actual HTTPS listener, industrial database synchronization or cross-VLAN connection is claimed.</p></section>'
page += '<section><h2>Security limitations</h2><p>Same-VLAN traffic bypasses gateway ACLs. Segmentation is not a physical air gap. PAT does not guarantee topology secrecy or stop malicious content in permitted HTTPS. Cisco established ACL rules check ACK/RST flags rather than keeping session state. The modeled reply table has no full TCP validation, teardown or idle expiration. Local database administrators can open a separate writable connection.</p></section><h2>Six-slide presentation</h2>'
for index, (title, text) in enumerate(slides, 1):
    page += '<section class="slide"><small>SLIDE ' + str(index) + '</small><h2>' + escape(title) + '</h2><p>' + escape(text) + '</p></section>'
page += '<section><h2>Submission description</h2><p>Describe this submission as an offline policy simulation and local read-only reporting demonstration. The original report specified Packet Tracer: an instructor must accept this alternative if that tool is mandatory. No genuine .pkt file, Cisco runtime counters or network-service handshake evidence is supplied.</p></section></body></html>'
output = folder / 'final-project.html'
if output.exists():
    output = folder / ('final-project-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.html')
output.write_text(page, encoding='utf-8')
print('Final project page saved:', output)
webbrowser.open(output.as_uri())
