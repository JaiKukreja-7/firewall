"""No-install reporting exception demo: policy model + real SQLite read-only access.

The declared TCP 8443 endpoint is a proposed HTTPS reporting service, not a
running listener. SQLite queries execute locally, not across VLANs.
"""
import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

REPORTER = '192.168.10.60'
OT_SERVICE = '192.168.20.10'
SERVICE_PORT = 8443

def reporting_policy(source, destination, protocol, port):
    return 'PERMIT' if (source, destination, protocol, port) == (
        REPORTER, OT_SERVICE, 'TCP', SERVICE_PORT
    ) else 'DENY'

def create_fixture(path):
    """Initialize a new local fixture, never replace an existing database."""
    con = sqlite3.connect(f'file:{path.as_posix()}?mode=rwc', uri=True)
    try:
        con.execute('CREATE TABLE telemetry(machine TEXT, status TEXT, units INTEGER)')
        con.executemany('INSERT INTO telemetry VALUES (?, ?, ?)',
                        [('PLC-01', 'RUNNING', 1240), ('PLC-02', 'RUNNING', 980)])
        con.commit()
    finally:
        con.close()

def open_reader(path):
    con = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)
    con.execute('PRAGMA query_only=ON')
    # Restrict this connection to SELECT and reads of the telemetry table.
    def authorize(action, arg1, arg2, database, trigger):
        allowed = action == sqlite3.SQLITE_SELECT or (
            action == sqlite3.SQLITE_READ and arg1 == 'telemetry'
        )
        return sqlite3.SQLITE_OK if allowed else sqlite3.SQLITE_DENY
    con.set_authorizer(authorize)
    return con

def validate(path):
    results = []
    for name, src, dst, proto, port, expected in [
        ('Dedicated reporting host', REPORTER, OT_SERVICE, 'TCP', 8443, 'PERMIT'),
        ('Ordinary corporate workstation', '192.168.10.50', OT_SERVICE, 'TCP', 8443, 'DENY'),
        ('Wrong service port', REPORTER, OT_SERVICE, 'TCP', 5432, 'DENY'),
        ('PLC direct access', REPORTER, '192.168.20.50', 'TCP', 8443, 'DENY'),
        ('Wrong protocol', REPORTER, OT_SERVICE, 'UDP', 8443, 'DENY'),
    ]:
        observed = reporting_policy(src, dst, proto, port)
        results.append(dict(name=name, expected=expected, observed=observed, passed=observed == expected))
    con = open_reader(path)
    try:
        rows = con.execute('SELECT machine, status, units FROM telemetry ORDER BY machine').fetchall()
        results.append(dict(name='Read telemetry', passed=rows == [('PLC-01', 'RUNNING', 1240), ('PLC-02', 'RUNNING', 980)]))
        for name, sql in [
            ('Reject UPDATE', "UPDATE telemetry SET units=0"),
            ('Reject DELETE', 'DELETE FROM telemetry'),
            ('Reject INSERT', "INSERT INTO telemetry VALUES ('PLC-X','STOPPED',0)"),
            ('Reject schema changes', 'DROP TABLE telemetry'),
            ('Reject query-only override', 'PRAGMA query_only=OFF'),
            ('Reject attached database', "ATTACH DATABASE ':memory:' AS other"),
        ]:
            try:
                con.execute(sql)
                passed = False
            except sqlite3.DatabaseError:
                passed = True
            results.append(dict(name=name, passed=passed))
    finally:
        con.close()
    con = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)
    try:
        unchanged = con.execute('SELECT machine,status,units FROM telemetry ORDER BY machine').fetchall() == rows
        results.append(dict(name='Underlying data unchanged', passed=unchanged))
    finally:
        con.close()
    return dict(scope='Local SQLite read-only enforcement and simulated network exception; no real HTTPS, VLAN or industrial DB service', policy=dict(source=REPORTER, destination=OT_SERVICE, protocol='TCP', port=SERVICE_PORT), telemetry=rows, results=results)

if __name__ == '__main__':
    with TemporaryDirectory(prefix='ns-p02-reporting-') as folder:
        db = Path(folder) / 'ot-telemetry.sqlite'
        create_fixture(db)
        evidence = validate(db)
        print(json.dumps(evidence, indent=2))
        raise SystemExit(0 if all(r['passed'] for r in evidence['results']) else 1)
