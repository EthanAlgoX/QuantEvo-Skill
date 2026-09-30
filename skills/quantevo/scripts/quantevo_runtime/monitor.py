"""Loopback-only, read-only website and JSON monitoring API."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from . import paper


def stop(home):
    with paper.database(home) as con:
        paper.set_meta(con, 'stop_server', True); con.commit()
    return {'server_stop_requested': True}


def serve(home, port=8765):
    if not 1024 <= port <= 65535:
        raise ValueError('Port must be in [1024,65535]')
    page = Path(__file__).with_name('dashboard.html').read_bytes()
    allowed_hosts = {f'localhost:{port}', f'127.0.0.1:{port}'}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send_body(self, code, body, content_type):
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; frame-ancestors 'none'; object-src 'none'")
            self.end_headers(); self.wfile.write(body)

        def do_GET(self):
            if self.headers.get('Host') not in allowed_hosts:
                self.send_body(403, b'Loopback host required', 'text/plain'); return
            route = urlparse(self.path).path
            try:
                if route == '/':
                    self.send_body(200, page, 'text/html; charset=utf-8'); return
                if route == '/api/status':
                    value = paper.status(home)
                elif route.startswith('/api/accounts/'):
                    key = route.rsplit('/', 1)[-1]
                    if len(key) != 12 or any(c not in '0123456789abcdef' for c in key):
                        raise ValueError('Account not found')
                    value = paper.status(home, key)
                else:
                    self.send_body(404, b'Not found', 'text/plain'); return
                self.send_body(200, json.dumps(value, ensure_ascii=False, allow_nan=False).encode(), 'application/json; charset=utf-8')
            except ValueError as exc:
                self.send_body(404, json.dumps({'error': str(exc)}).encode(), 'application/json')
            except (OSError, RuntimeError) as exc:
                self.send_body(503, json.dumps({'error': str(exc)}).encode(), 'application/json')

    with paper.worker_lock(home, filename='.server.lock'):
        server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
        server.daemon_threads = True
        server.timeout = .5
        with paper.database(home) as con:
            paper.set_meta(con, 'stop_server', False)
            paper.set_meta(con, 'server', {'pid': os.getpid(), 'running': True, 'url': f'http://127.0.0.1:{port}'})
            con.commit()
        try:
            while True:
                with paper.database(home) as con:
                    if paper.get_meta(con, 'stop_server', False):
                        break
                server.handle_request()
        finally:
            server.server_close()
            with paper.database(home) as con:
                paper.set_meta(con, 'server', {'pid': os.getpid(), 'running': False, 'url': f'http://127.0.0.1:{port}'})
                con.commit()
