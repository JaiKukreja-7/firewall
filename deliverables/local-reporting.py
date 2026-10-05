from pathlib import Path
from datetime import datetime
from html import escape
import sqlite3, json, webbrowser

folder = Path.home() / 'Desktop' / 'NS-P02-Model' / ('reporting-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
folder.mkdir(parents=True)
db = folder / 'telemetry.sqlite'
with sqlite3.connect(db) as setup:
    setup.execute('CREATE TABLE telemetry(machine TEXT, status TEXT, units INTEGER)')
    setup.executemany('INSERT INTO telemetry VALUES (?, ?, ?)', [('PLC-01', 'RUNNING', 1240), ('PLC-02', 'RUNNING', 980)])
setup.close()
results = []
for name, source, destination, protocol, port, expected in [
    ('Dedicated reporting host', '192.168.10.60', '192.168.20.10', 'TCP', 8443, 'PERMIT'),
    ('Ordinary corporate PC blocked', '192.168.10.50', '192.168.20.10', 'TCP', 8443, 'DENY'),
    ('Wrong port blocked', '192.168.10.60', '192.168.20.10', 'TCP', 5432, 'DENY'),
    ('PLC direct access blocked', '192.168.10.60', '192.168.20.50', 'TCP', 8443, 'DENY'),
    ('Wrong protocol blocked', '192.168.10.60', '192.168.20.10', 'UDP', 8443, 'DENY')]:
    permitted = (source, destination, protocol, port) == ('192.168.10.60', '192.168.20.10', 'TCP', 8443)
    observed = 'PERMIT' if permitted else 'DENY'
    results.append({'name': name, 'passed': observed == expected, 'observed': observed})
reader = sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True)
reader.execute('PRAGMA query_only=ON')
def authorize(action, table, column, database, trigger):
    allowed = action == sqlite3.SQLITE_SELECT or (action == sqlite3.SQLITE_READ and table == 'telemetry')
    return sqlite3.SQLITE_OK if allowed else sqlite3.SQLITE_DENY
reader.set_authorizer(authorize)
data = reader.execute('SELECT machine,status,units FROM telemetry ORDER BY machine').fetchall()
results.append({'name': 'Read telemetry', 'passed': data == [('PLC-01', 'RUNNING', 1240), ('PLC-02', 'RUNNING', 980)]})
for name, sql in [
    ('Reject UPDATE', 'UPDATE telemetry SET units=0'),
    ('Reject DELETE', 'DELETE FROM telemetry'),
    ('Reject INSERT', "INSERT INTO telemetry VALUES ('PLC-X','STOPPED',0)"),
    ('Reject schema changes', 'DROP TABLE telemetry'),
    ('Reject read-only override', 'PRAGMA query_only=OFF'),
    ('Reject attached database', "ATTACH DATABASE ':memory:' AS other")]:
    try:
        reader.execute(sql)
        passed = False
    except sqlite3.DatabaseError:
        passed = True
    results.append({'name': name, 'passed': passed})
reader.close()
check = sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True)
results.append({'name': 'Underlying data unchanged', 'passed': check.execute('SELECT machine,status,units FROM telemetry ORDER BY machine').fetchall() == data})
check.close()
count = sum(r['passed'] for r in results)
scope = 'Real local SQLite read-only checks plus simulated network policy. No actual HTTPS endpoint, VLAN forwarding, database synchronization or Packet Tracer execution.'
(folder / 'evidence.json').write_text(json.dumps({'scope': scope, 'telemetry': data, 'results': results}, indent=2))
page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Read-only Reporting Lab</title><style>body{font:16px system-ui;max-width:900px;margin:30px auto;padding:20px;background:#f4f7fb;color:#233044}p{line-height:1.7}td,th{padding:12px;text-align:left;border-bottom:1px solid #ccc}table{width:100%;border-collapse:collapse}button{padding:12px}@media print{button{display:none}}</style>'
page += '<h1>Read-only Reporting Lab</h1><h2>' + str(count) + '/13 checks passed</h2><p>' + scope + '</p>'
page += '<p>Proposed exception: reporting host 192.168.10.60 to OT service 192.168.20.10, TCP 8443. This new design assumption is demonstrated separately; your original dashboard retains its strict Corporate-to-OT deny.</p>'
page += '<button onclick="window.print()">Print / Save as PDF</button><h2>Test results</h2><table><tr><th>Check</th><th>Outcome</th></tr>'
for r in results:
    page += '<tr><td>' + escape(r['name']) + '</td><td>' + ('PASS' if r['passed'] else 'FAIL') + '</td></tr>'
page += '</table><h2>Telemetry read from SQLite</h2><pre>' + escape(str(data)) + '</pre><p>Read-only controls apply to this connection. A file owner or administrator can still open a separate writable connection; this does not guarantee immutable storage.</p></html>'
report = folder / 'report.html'
report.write_text(page, encoding='utf-8')
print(str(count) + '/13 reporting checks passed')
print('Report and evidence saved:', folder)
webbrowser.open(report.as_uri())
if count != 13:
    raise SystemExit('One or more checks failed; inspect report.')
