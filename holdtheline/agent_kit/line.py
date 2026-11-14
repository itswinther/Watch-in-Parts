"""Your controls for the production line.

    python3 line.py status
    python3 line.py inspect N
    python3 line.py act ship|sort|scrap [--adjust D | --replace]
"""
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "episode.json")))


def call(payload):
    payload["episode"] = CFG["episode"]
    req = urllib.request.Request(CFG["url"], json.dumps(payload).encode(), {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    if argv[0] == "status":
        out = call({"cmd": "status"})
    elif argv[0] == "inspect" and len(argv) == 2:
        out = call({"cmd": "inspect", "n": int(argv[1])})
    elif argv[0] == "act" and len(argv) >= 2:
        p = {"cmd": "act", "dispose": argv[1]}
        rest = argv[2:]
        if rest[:1] == ["--replace"]:
            p["replace"] = True
        elif rest[:1] == ["--adjust"] and len(rest) == 2:
            p["adjust"] = float(rest[1])
        elif rest:
            print(json.dumps({"error": "usage: act ship|sort|scrap [--adjust D | --replace]"}))
            return
        out = call(p)
    else:
        print(__doc__)
        return
    print(json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1:])
