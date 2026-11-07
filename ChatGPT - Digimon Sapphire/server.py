#!/usr/bin/env python3
"""Digimon Sapphire: a loopback-only local arcade."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, unquote
from urllib.request import urlopen
import json
import sys
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent
PORT = 8746
APP_ID = 'digimon-sihappiere'
URL = f'http://127.0.0.1:{PORT}'
GAMES = {'sihappiere': 'digimon-sihappiere.gba', 'ruby': 'digimon-ruby.gba'}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def safe_request(self):
        if self.headers.get('Host') not in (f'127.0.0.1:{PORT}', f'localhost:{PORT}'):
            self.send_error(403)
            return False
        path = unquote(urlsplit(self.path).path)
        target = (ROOT / path.lstrip('/')).resolve()
        if not target.is_relative_to(ROOT) or any(p.startswith('.') for p in Path(path).parts):
            self.send_error(403)
            return False
        return True

    def do_GET(self):
        if not self.safe_request(): return
        if urlsplit(self.path).path == '/api/health':
            data = json.dumps({'app': APP_ID, 'version': 1,
                'games': {key: (ROOT / 'roms' / name).is_file() for key, name in GAMES.items()}}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()

    def do_HEAD(self):
        if self.safe_request(): super().do_HEAD()

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def list_directory(self, path):
        self.send_error(403, 'Directory browsing is disabled')

def main():
    try:
        server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    except OSError:
        try:
            with urlopen(URL + '/api/health', timeout=2) as response:
                if json.load(response).get('app') == APP_ID:
                    if '--open' in sys.argv: webbrowser.open(URL)
                    print('Digimon Sapphire is already running at ' + URL)
                    return
        except Exception:
            pass
        raise SystemExit(f'Port {PORT} is busy. Close the app using that port, then launch again.')
    if '--open' in sys.argv:
        threading.Timer(0.5, lambda: webbrowser.open(URL)).start()
    print('Digimon Sapphire is ready: ' + URL, flush=True)
    print('Keep this window open while playing. Press Control+C to stop.', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__ == '__main__': main()
