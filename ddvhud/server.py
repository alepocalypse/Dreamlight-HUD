"""Localhost-only HTTP server: serves the static page and /report.json."""
import datetime
import json
import os
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import app, config

# Under a PyInstaller bundle, data files live under sys._MEIPASS rather than next to the module.
_BASE = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(__file__))), "ddvhud")
_STATIC = os.path.join(_BASE, "static")
PAGE = os.path.join(_STATIC, "index.html")

# One row per served asset folder: (URL prefix, folder, filename pattern). PNG only.
ASSET_ROUTES = [
    ("/roles/", os.path.realpath(os.path.join(_STATIC, "roles")), re.compile(r"[a-z]+\.png")),
    ("/portraits/", os.path.realpath(os.path.join(_STATIC, "portraits")), re.compile(r"[0-9]+\.png")),
]


def asset_for(url_path):
    """Bytes of the PNG that `url_path` names under an ASSET_ROUTES prefix, else None.

    The file must full-match the row's pattern, resolve directly inside its folder and exist."""
    for prefix, folder, pattern in ASSET_ROUTES:
        if url_path.startswith(prefix):
            name = urllib.parse.unquote(url_path[len(prefix):].split("?", 1)[0])
            if not pattern.fullmatch(name):
                return None
            path = os.path.realpath(os.path.join(folder, name))
            if os.path.dirname(path) != folder or not os.path.isfile(path):
                return None
            with open(path, "rb") as f:
                return f.read()
    return None


def make_handler(root_or_file, picker=None, config_file=None):
    """`picker`, if given, is called to let the user choose a save; it returns a path or None.

    The chosen path replaces `root_or_file` and is remembered in the config file."""
    state = {"save": root_or_file}

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, ctype, body, cache="no-store"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", cache)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                with open(PAGE, "rb") as f:
                    self._send(200, "text/html; charset=utf-8", f.read())
            elif self.path == "/report.json":
                self._send(200, "application/json", json.dumps(self.report()).encode())
            elif (body := asset_for(self.path)) is not None:
                self._send(200, "image/png", body, "max-age=86400")
            else:
                self._send(404, "text/plain", b"not found")

        def do_POST(self):
            if self.path != "/pick-save" or picker is None:
                self._send(404, "text/plain", b"not found")
                return
            chosen = picker()
            if chosen:
                state["save"] = chosen
                try:
                    config.store_save_path(chosen, config_file)
                except OSError:
                    pass  # still used for this session
            self._send(200, "application/json", json.dumps({"picked": bool(chosen)}).encode())

        def report(self):
            r = app.current_report(state["save"], datetime.datetime.now(datetime.timezone.utc))
            r["can_pick_save"] = picker is not None
            return r

        def log_message(self, *a):
            pass

    return Handler


def make_server(root_or_file, port, picker=None):
    return ThreadingHTTPServer(("127.0.0.1", port), make_handler(root_or_file, picker))


def serve(root_or_file, port):
    httpd = make_server(root_or_file, port)
    print(f"Dreamlight HUD on http://127.0.0.1:{port}/  (save: {root_or_file})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
