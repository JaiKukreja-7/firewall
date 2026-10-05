from pathlib import Path
from datetime import datetime, timezone
import json, sys, unittest, io, html
from zipfile import ZipFile, ZIP_DEFLATED
from docx import Document
from docx.shared import Inches as DocInches
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from model import run_demo
from reporting_demo import create_fixture, validate
from tempfile import TemporaryDirectory
out=ROOT/'deliverables'
stream=io.StringIO()
r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/'tests')))
assert r.wasSuccessful() and r.testsRun==16
(out/'test-results.txt').write_text(stream.getvalue())
fw,scenarios=run_demo()
evidence={'scope':'Educational policy model and static ACL subset analysis. Not Packet Tracer, IOS, or real application traffic.', 'generated_utc':datetime.now(timezone.utc).isoformat(),'python_test_methods':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'browser_checks_verified':20,'reporting_checks_verified':13,'corporate_boundary_cases':254*3*7,'admin_source_cases':253,'scenarios':scenarios,'translations':fw.translations,'outstanding':['Packet Tracer/IOS execution','Real HTTPS, SSH and RDP handshakes','Networked industrial database synchronization','Full stateful inspection']}
with TemporaryDirectory() as td:
 db=Path(td)/'telemetry.sqlite';create_fixture(db);reporting=validate(db)
 assert len(reporting['results'])==13 and all(x['passed'] for x in reporting['results'])
(out/'reporting-evidence.json').write_text(json.dumps(reporting,indent=2))
evidence['reporting']=reporting
(out/'validation-evidence.json').write_text(json.dumps(evidence,indent=2))
slides=[
('Firewall & NAT Security Lab','NS-P02 | Manufacturing Company',[
'Four-zone manufacturing security redesign',
'Offline browser model with Cisco configuration build kit',
'Validated policy behavior; Cisco topology execution remains unrun'],
'This demonstration implements a four-zone policy model for a manufacturing scenario. It runs offline in a browser. Cisco configuration files accompany the model, but I do not claim they have been executed in Packet Tracer.'),
('Threat model','Why a flat IT/OT network is risky',[
'Compromised corporate hosts can attempt lateral access to OT',
'Telnet exposes credentials in cleartext',
'Unrestricted outbound flows can enable exfiltration',
'Permitted HTTPS still needs endpoint and application controls'],
'A flat architecture makes it easier for a corporate compromise to reach critical systems. Segmentation adds checkpoints. Blocking Telnet and unauthorized outbound ports reduces exposure, but allowed HTTPS can still carry harmful traffic.'),
('Four security zones','VLANs and routed security boundaries',[
'Internet: gateway 203.0.113.2; lab web 198.51.100.10',
'Corporate VLAN 10: 192.168.10.0/24',
'Factory OT VLAN 20: 192.168.20.0/24',
'Admin VLAN 30: 192.168.30.0/24; jump host .10'],
'The gateway separates Corporate, Factory OT, Administration and the simulated Internet. Corporate initiations to OT and Admin are denied. Hosts within a VLAN bypass gateway filtering, so this is not complete host isolation or a physical air gap.'),
('Firewall and PAT','Explicit permits, followed by default deny',[
'Corporate/Admin: TCP 443 and DNS to 8.8.8.8',
'Jump host only: internal SSH and SCADA TCP 3389',
'OT: no initiated cross-zone traffic and no PAT',
'Corporate/Admin share public address through PAT',
'Browser replies match tuples; Cisco ACLs are stateless'],
'Default deny drops routed flows unless a rule permits them. PAT maps allowed outbound flows to one public address with distinct ports. It does not guarantee topology secrecy. Cisco established ACL rules inspect ACK or RST flags rather than tracking sessions.'),
('Verification results','Measured checks, with evidence boundaries',[
'20 browser checks passed; desktop/mobile controls verified',
'16 Python test methods passed',
'5,334 Corporate boundary cases and 253 admin-source cases checked',
'PAT reuse, port uniqueness, allowed replies and denied pivots verified',
'No real TLS/SSH/RDP or Packet Tracer traffic was tested'],
'I can show the browser validation suite, PAT table, decision log, matching replies and rejected wrong-source replies. Automated tests also evaluate the limited syntax used by our Cisco ACLs. These are model and static analysis results, not observed IOS counters or encrypted application handshakes.'),
('Limits and recommendations','What remains outside this implementation',[
'Local read-only SQLite demo verified; network service remains unrun',
'Full TCP state, expiration and industrial DPI are not implemented',
'Physical USB threats and same-VLAN access remain',
'Production: endpoint hardening, industrial NGFW and data diodes',
'Packet Tracer is optional for this demo but required for original Cisco validation'],
'A separate real SQLite demonstration now verifies read-only telemetry queries and rejected writes. A narrow reporting exception is modeled for Corporate host 192.168.10.60 to OT service 192.168.20.10 on TCP 8443. This is an explicit design assumption, not a running network service. Industrial inspection and hardware one-way gateways are future controls. The original Cisco execution requirement remains unfulfilled.')]
coverage=[
('Four-zone architecture','Simulated; Cisco VLAN wiring unrun'),
('PAT / default deny / HTTPS / DNS','Implemented and tested in the policy models'),
('Jump-host management','Permission decisions tested; actual services unrun'),
('Telnet blocking','Routed boundaries only; not same-VLAN'),
('Stateful inspection','Tuple reply matching only; no full TCP state machine'),
('Read-only database reporting','Local SQLite read-only enforcement verified; cross-zone service unrun'),
('Packet Tracer evidence','Unrun: no .pkt, Cisco counters or packet captures'),
('Industrial DPI / USB controls / data diodes','Recommendations, not implemented controls')]
sections=[
('Executive summary','This project delivers an offline educational network-policy demonstration and a Cisco router/switch build kit. Four address zones protect the intended IT/OT boundary. Policy decisions, PAT mappings and simplified reply matching are implemented and tested. The attached Word report serves as a design source, not evidence that this implementation ran in Cisco Packet Tracer.'),
('Workflow delivered','Open dashboard.html locally or serve web/index.html with Python. Use Live lab for custom traffic, Validation & evidence for the 20-check suite and JSON export, and Report coverage for the requirement audit. No additional Mac software is required for the browser workflow.'),
('Policy decisions','Corporate and Admin may initiate HTTPS and approved DNS. The jump host 192.168.30.10 may initiate SSH to internal systems and RDP to SCADA 192.168.20.10. Corporate initiations to OT/Admin, OT Internet access, unsolicited Internet traffic, and routed Telnet are denied. Lab-only ping to 198.51.100.10 is a documented diagnostic exception. Corporate/Admin have PAT; OT is intentionally excluded.'),
('Verification','Twenty browser checks passed, including scenario decisions, PAT uniqueness, matching replies and a wrong-source denial. Browser automation also verified presets, input errors, export, reset and responsive layout. Sixteen Python test methods passed. The ACL subset evaluator checked 5,334 Corporate boundary cases and 253 Admin source cases. The underlying IOS command parser, device forwarding, and actual TLS/SSH/RDP were not executed.'),
('Stateful comparison','The browser and Python models match reverse flow tuples to simulated sessions. They do not validate TCP sequence numbers or implement FIN/RST teardown or idle expiration. The Cisco configuration uses stateless established checks, which accept ACK/RST flags even without a session table. The static ACL test demonstrates this weaker guarantee.'),
('Read-only reporting demonstration','A separate Python standard-library SQLite demo passed 13 reporting checks: the dedicated-host policy tuple, allowed reads, rejected writes/schema changes/overrides and unchanged data. SQLite mode=ro, query_only and a restricted authorizer enforce read-only access on this connection. The assumed reporting host is 192.168.10.60 and the proposed service is 192.168.20.10 TCP 8443. The original strict-deny dashboard does not enable this exception. No HTTPS reporting listener, real cross-VLAN flow or industrial database synchronization is claimed. Local administrators can still open a separate writable connection.'),
('Report corrections','Do not claim that segmentation eliminates ransomware or that NAT completely obscures topology. This is not an air gap. Gateway filters do not inspect same-VLAN flows. Say traffic was dropped rather than connection refused unless a reject was observed. Do not reuse the source report\'s claimed 100% Cisco compliance as evidence for this implementation.'),
('Completion status','The no-install browser demonstration and supporting materials are complete. The original Packet Tracer execution requirement is not complete. No .pkt topology, Cisco packet captures or real application handshakes are claimed. Production controls, including industrial DPI, endpoint hardening, USB restrictions and hardware data diodes, remain recommendations.')]
# Word report
doc=Document();doc.add_heading('NS-P02: Implementation and Verification Report',0)
doc.add_paragraph('Manufacturing Company | Browser model + Cisco build kit')
for title,text in sections: doc.add_heading(title,1);doc.add_paragraph(text)
doc.add_heading('Requirement coverage',1)
t=doc.add_table(rows=1,cols=2);t.style='Light Shading Accent 1'
t.rows[0].cells[0].text='Requirement';t.rows[0].cells[1].text='Status'
for a,b in coverage:
 cells=t.add_row().cells;cells[0].text=a;cells[1].text=b
doc.add_heading('Model screenshots',1)
for name in ['dashboard-desktop.png','dashboard-mobile.png']:
 doc.add_picture(str(ROOT/'docs'/name),width=DocInches(5.5 if 'desktop' in name else 2.5))
doc.save(out/'NS-P02_Verification_Report.docx')
# PDF report
styles=getSampleStyleSheet();story=[Paragraph('NS-P02: Implementation and Verification Report',styles['Title'])]
for title,text in sections: story += [Paragraph(html.escape(title),styles['Heading2']),Paragraph(html.escape(text),styles['BodyText']),Spacer(1,8)]
SimpleDocTemplate(str(out/'NS-P02_Verification_Report.pdf'),pagesize=A4).build(story)
# Presentation
prs=Presentation();prs.slide_width=Inches(13.33);prs.slide_height=Inches(7.5)
for i,(title,subtitle,bullets,notes) in enumerate(slides):
 slide=prs.slides.add_slide(prs.slide_layouts[6]);slide.background.fill.solid();slide.background.fill.fore_color.rgb=RGBColor.from_string('0A1220')
 for text,y,size,color in [(f'NS-P02 / {i+1:02d}',.5,14,'65DDC0'),(title,1,32,'DBE6F2'),(subtitle,1.8,18,'A5B6CC')]:
  tf=slide.shapes.add_textbox(Inches(.8),Inches(y),Inches(11.7),Inches(.7)).text_frame;tf.text=text
  p=tf.paragraphs[0];p.font.size=Pt(size);p.font.color.rgb=RGBColor.from_string(color)
 tf=slide.shapes.add_textbox(Inches(.8),Inches(2.8),Inches(11.7),Inches(4)).text_frame;tf.word_wrap=True
 for j,line in enumerate(bullets):
  p=tf.paragraphs[0] if j==0 else tf.add_paragraph();p.text='• '+line;p.font.size=Pt(22);p.font.color.rgb=RGBColor.from_string('DBE6F2');p.space_after=Pt(20)
 slide.notes_slide.notes_text_frame.text=notes
prs.save(out/'NS-P02_Presentation.pptx')
(out/'presentation-script.md').write_text('\n\n'.join(f'## Slide {i+1}: {s[0]}\n\n{s[3]}' for i,s in enumerate(slides)))
# Self-contained printable report + presentation for no-install delivery.
css='body{font:16px system-ui;background:#0a1220;color:#dbe6f2;max-width:1100px;margin:auto;padding:24px}h1,h2{color:#65ddc0}p,li{line-height:1.7}section{border:1px solid #34465f;background:#111f33;border-radius:12px;padding:24px;margin:20px 0}table{width:100%;border-collapse:collapse}td,th{padding:12px;text-align:left;border-bottom:1px solid #34465f}button{padding:12px;background:#193f43;border:1px solid #65ddc0;color:white;border-radius:8px;cursor:pointer;margin:6px}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{margin:15px 0}small{color:#a5b6cc}@media print{body{background:white;color:black;padding:0}section{background:white;border:0;break-inside:avoid}h1,h2{color:black}button{display:none}}'
page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NS-P02 Submission Pack</title><style>'+css+'</style></head><body><h1>NS-P02: Submission & Demonstration Pack</h1><p>No installation required. This report complements your existing dashboard.</p><button onclick="window.print()">Print / Save as PDF</button><p><strong>Verified:</strong> 20 browser checks; 13 Python test methods; 5,334 Corporate boundary cases; 253 Admin source cases.</p><p><strong>Scope:</strong> educational policy simulation and static ACL analysis. Packet Tracer and real application handshakes remain unrun.</p><h2>Implementation report</h2>'
for title,text in sections: page+='<section><h2>'+html.escape(title)+'</h2><p>'+html.escape(text)+'</p></section>'
page+='<section><h2>Requirements checklist</h2><table><tr><th>Requirement</th><th>Status</th></tr>'+''.join('<tr><td>'+html.escape(a)+'</td><td>'+html.escape(b)+'</td></tr>' for a,b in coverage)+'</table></section><h2>Six-slide presentation script</h2>'
for i,(title,subtitle,bullets,notes) in enumerate(slides):
 page+='<section><small>SLIDE '+str(i+1)+'</small><h2>'+html.escape(title)+'</h2><p>'+html.escape(subtitle)+'</p><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in bullets)+'</ul><details><summary>Speaker notes</summary><p>'+html.escape(notes)+'</p></details></section>'
page+='<section><h2>Cisco build kit</h2><p>These files have passed limited static policy checks; they have not been executed in IOS. SSH credentials must be chosen locally; no secrets are supplied.</p>'
for f in sorted((ROOT/'configs').glob('*.cfg')):page+='<details><summary>'+f.name+'</summary><pre>'+html.escape(f.read_text())+'</pre></details>'
page+='</section><section><h2>Automated test output</h2><pre>'+html.escape(stream.getvalue())+'</pre></section><section><h2>Model evidence</h2><details><summary>Scenario results and PAT mappings (JSON)</summary><pre>'+html.escape(json.dumps(evidence,indent=2))+'</pre></details></section></body></html>'
(out/'submission.html').write_text(page)
# Verify files are readable, not just created.
assert len(Presentation(out/'NS-P02_Presentation.pptx').slides)==6
assert len(Document(out/'NS-P02_Verification_Report.docx').paragraphs)>10
assert (out/'NS-P02_Verification_Report.pdf').read_bytes().startswith(b'%PDF')
with ZipFile('/workspace/NS-P02_Complete_Package.zip','w',ZIP_DEFLATED) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file() and not any(x in ('.git','__pycache__') for x in p.relative_to(ROOT).parts):z.write(p,Path('NS-P02')/p.relative_to(ROOT))
print('Created verified Word/PDF report, six-slide PowerPoint with notes, presentation script, evidence JSON, offline submission page, and complete package.')
