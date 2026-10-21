#!/usr/bin/env python3
"""Serve this checkout or extracted snapshot locally using Python's standard library."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import webbrowser

ROOT = Path(__file__).resolve().parents[1]

class PreviewHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8846)
    parser.add_argument('--open', choices=['home', 'console', 'api'])
    args = parser.parse_args()
    if not (ROOT / 'index.html').is_file():
        parser.error(f'Website source not found: {ROOT / "index.html"}')
    if not 1 <= args.port <= 65535:
        parser.error('--port must be between 1 and 65535')
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(PreviewHandler, directory=str(ROOT)))
    except OSError as exc:
        print(f'Cannot start preview on port {args.port}: {exc}. Try --port 8847.', file=sys.stderr)
        return 1
    base = f'http://127.0.0.1:{args.port}/'
    print(f'Root: {ROOT}\nHome: {base}#home\nConsole: {base}#console-preview\nAPI docs: {base}#api\nStop: Ctrl+C', flush=True)
    if args.open:
        route = 'console-preview' if args.open == 'console' else args.open
        try:
            webbrowser.open(base + '#' + route)
        except webbrowser.Error as exc:
            print(f'Open the printed URL manually: {exc}', file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nPreview stopped.')
    finally:
        server.server_close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
