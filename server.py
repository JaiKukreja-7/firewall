"""Local browser demonstration, using only the Python standard library."""
import argparse
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit
from model import Firewall, run_demo
from reporting_demo import create_fixture, open_reader, validate

ROOT = Path(__file__).parent
fw = Firewall()
database_directory = TemporaryDirectory(prefix='ns-p02-service-')
database_path = Path(database_directory.name) / 'telemetry.sqlite'
create_fixture(database_path)

class Handler(BaseHTTPRequestHandler):
    def respond(self, code, data, content_type='application/json'):
        body = data.encode() if isinstance(data, str) else json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if path == '/health':
            self.respond(200, dict(status='ok', scope='Educational simulation'))
        elif path == '/api/report':
            reader = open_reader(database_path)
            try:
                rows = reader.execute('SELECT machine,status,units FROM telemetry ORDER BY machine').fetchall()
            finally:
                reader.close()
            self.respond(200, dict(mode='live-local-sqlite', scope='Real read-only SQLite query inside this web service; no actual IT/OT VLAN traffic', telemetry=rows))
        elif path == '/api/reporting-validation':
            self.respond(200, validate(database_path))
        elif path == '/api/state':
            self.respond(200, dict(translations=fw.translations, events=fw.events))
        else:
            site = ROOT / ('site' if (ROOT/'site/index.html').exists() else 'web')
            target = (site / ('index.html' if path == '/' else path.lstrip('/'))).resolve()
            if not target.is_relative_to(site.resolve()) or not target.is_file():
                self.respond(404, dict(error='Not found'))
                return
            body = target.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', mimetypes.guess_type(target.name)[0] or 'application/octet-stream')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def do_POST(self):
        global fw
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 <= size <= 4096:
                raise ValueError('Request too large')
            data = json.loads(self.rfile.read(size) or '{}')
            if not isinstance(data, dict):
                raise ValueError('Request body must be a JSON object')
            if self.path == '/api/flow':
                self.respond(200, fw.evaluate(**data))
            elif self.path == '/api/reply':
                self.respond(200, fw.reply(**data))
            elif self.path == '/api/demo':
                fw, results = run_demo()
                self.respond(200, dict(results=results, translations=fw.translations))
            elif self.path == '/api/reset':
                fw = Firewall()
                self.respond(200, dict(status='reset'))
            else:
                self.respond(404, dict(error='Not found'))
        except (ValueError, TypeError) as exc:
            self.respond(400, dict(error=str(exc)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', '8000')))
    parser.add_argument('--host', default='127.0.0.1')
    args = parser.parse_args()
    print(f'NS-P02 educational simulation on port {args.port}', flush=True)
    HTTPServer((args.host, args.port), Handler).serve_forever()
