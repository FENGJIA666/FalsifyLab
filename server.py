"""Local-only HTTP UI; Python standard library, no installation required."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse
from falsifylab import ValidationError, search, markdown
import review as reviews
ROOT = Path(__file__).resolve().parent

class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data, kind='application/json'):
        body = data.encode() if isinstance(data, str) else json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', kind+'; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlparse(self.path).path
        files = {'/': ('static/index.html', 'text/html'), '/app.js': ('static/app.js', 'text/javascript'),
                 '/sandbox': ('static/sandbox.html', 'text/html'), '/sandbox.js': ('static/sandbox.js', 'text/javascript'),
                 '/style.css': ('static/style.css', 'text/css'), '/api/examples': ('examples/cases.json', 'application/json')}
        if route == '/api/health':
            return self.respond(200, {'ok': True, 'version': reviews.REVIEW_VERSION, 'source': reviews.SOURCE})
        if route not in files:
            return self.respond(404, {'error': 'Not found'})
        file, kind = files[route]
        self.respond(200, (ROOT/file).read_text(), kind)

    def do_POST(self):
        if self.path not in {'/api/search', '/api/propose', '/api/review'}:
            return self.respond(404, {'error': 'Not found'})
        host = self.headers.get('Host', '')
        allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        if host not in allowed or self.headers.get('Origin', f'http://{host}') != f'http://{host}':
            return self.respond(403, {'error': 'Local same-origin requests only.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 512000:
                raise ValidationError('Request must be 1–512,000 bytes.')
            spec = json.loads(self.rfile.read(size))
            if not isinstance(spec,dict):
                raise ValidationError('Request must be an object.')
            if self.path == '/api/propose':
                if set(spec) != {'raw_text','search_min','search_max','step'}:
                    raise ValidationError('Proposal request fields do not match the schema.')
                return self.respond(200, {'proposal': reviews.propose(**spec)})
            if self.path == '/api/review':
                if not {'proposal','confirmed_digest'} <= set(spec) or set(spec)-{'proposal','confirmed_digest','parent'}:
                    raise ValidationError('Review request fields do not match the schema.')
                report=reviews.review(**spec)
                return self.respond(200, {'report':report,'markdown':reviews.markdown(report)})
            report = search(spec)
            self.respond(200, {'report': report, 'markdown': markdown(report)})
        except (ValidationError, ValueError, TypeError, RecursionError) as exc:
            self.respond(400, {'error': str(exc)[:300]})

    def log_message(self, *_):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = HTTPServer(('127.0.0.1', args.port), Handler)
    print(f'FalsifyLab ready: http://127.0.0.1:{args.port}', flush=True)
    server.serve_forever()
