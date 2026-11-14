"""Timing-machine sidecar. Holds one hidden watch in memory; the agent talks to it over HTTP.

The /final endpoint (true error and action log) needs a token stored only in this image;
the verifier collects the result with it after the agent has finished.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timing  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = int(open(os.path.join(HERE, "seed.txt")).read())
# The agent shares this sidecar's network namespace under Harbor's egress control, so
# "localhost only" is not a boundary. /final needs a token that exists only in this image.
TOKEN = open(os.path.join(HERE, "token.txt")).read().strip()
BUDGET = int(open(os.path.join(HERE, "budget.txt")).read()) if os.path.exists(os.path.join(HERE, "budget.txt")) else timing.TIME_BUDGET_MIN
W = timing.Watch(SEED, BUDGET)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path == "/final":
                if q.get("token") != TOKEN:
                    return self._send({"error": "unknown command"}, 404)
                return self._send({"error_s_per_day": W.error(), "log": W.log, "time_left": W.time_left})
            if u.path == "/health":
                return self._send({"ok": True})
            if u.path == "/status":
                return self._send(W.status())
            if u.path == "/measure":
                return self._send(W.measure(q.get("position"), q.get("wind"), q.get("minutes")))
            if u.path == "/regulate":
                return self._send(W.regulate(q.get("index")))
            if u.path == "/remove":
                return self._send(W.remove(q.get("screw"), q.get("mg")))
            if u.path == "/washer":
                return self._send(W.washer(q.get("screw")))
            return self._send({"error": "unknown command"}, 404)
        except Exception as ex:
            return self._send({"error": "bad request (%s)" % type(ex).__name__}, 400)


ThreadingHTTPServer(("0.0.0.0", 8000), H).serve_forever()
