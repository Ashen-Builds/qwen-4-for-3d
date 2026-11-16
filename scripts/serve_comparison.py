"""Serve only the selected deliverable directory on loopback."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy",
                         "default-src 'self' data: blob:; script-src 'self' 'unsafe-inline'; "
                         "style-src 'self' 'unsafe-inline'; connect-src 'self'; "
                         "img-src 'self' data: blob:; object-src 'none'; base-uri 'none'")
        super().end_headers()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory", required=True)
    p.add_argument("--port", type=int, default=8767)
    args = p.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port),
                                 partial(Handler, directory=args.directory))
    print(f"Comparison server on http://localhost:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
