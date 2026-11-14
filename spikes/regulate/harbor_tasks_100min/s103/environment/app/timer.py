"""Command line for the timing machine.

    python3 timer.py status
    python3 timer.py measure POSITION WIND MINUTES
    python3 timer.py regulate INDEX
    python3 timer.py remove SCREW MG
    python3 timer.py washer SCREW
"""
import json
import sys
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000/"


def call(path, **q):
    url = BASE + path + ("?" + urllib.parse.urlencode(q) if q else "")
    try:
        return json.loads(urllib.request.urlopen(url, timeout=30).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b'{"error": "http error"}')


def main(a):
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    c = a[0]
    if c == "status" and len(a) == 1:
        out = call("status")
    elif c == "measure" and len(a) == 4:
        out = call("measure", position=a[1], wind=a[2], minutes=a[3])
    elif c == "regulate" and len(a) == 2:
        out = call("regulate", index=a[1])
    elif c == "remove" and len(a) == 3:
        out = call("remove", screw=a[1], mg=a[2])
    elif c == "washer" and len(a) == 2:
        out = call("washer", screw=a[1])
    else:
        print(__doc__)
        return
    print(json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1:])
