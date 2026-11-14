"""Holds episodes in memory so an agent cannot rewind or copy the state.

    python3 server.py PORT LOGDIR SEED name1 name2 ...

Each name is one independent episode on the same seed. The seed is read from argv and then
only lives in this process.
"""
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import Episode

PORT, LOGDIR, SEED = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
EPISODES = {name: Episode(SEED) for name in sys.argv[4:]}
os.makedirs(LOGDIR, exist_ok=True)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0) or b"{}")
            ep = EPISODES.get(body.get("episode"))
            cmd = body.get("cmd")
            if ep is None:
                out = {"error": "unknown episode"}
            elif cmd == "status":
                out = ep.status()
            elif cmd == "inspect":
                out = ep.inspect(body.get("n"))
            elif cmd == "act":
                out = ep.act(body.get("dispose"), body.get("adjust", 0.0), bool(body.get("replace", False)))
            else:
                out = {"error": "unknown command"}
            with open(os.path.join(LOGDIR, "%s.jsonl" % body.get("episode")), "a") as f:
                f.write(json.dumps({"t": time.time(), "in": body, "out": out,
                                    "settled": ep.settle() if ep else None}) + "\n")
        except Exception as e:  # never leak a traceback to the agent
            out = {"error": "bad request (%s)" % type(e).__name__}
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
