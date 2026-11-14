"""Review verifier: keep only scores backed by verbatim evidence.

    python -I check_review.py REVIEW_JSON EVIDENCE_TXT --reward FILE --details FILE

An item scored above 0 keeps its score only if at least one of its quotes (at least 8 characters,
whitespace normalised) appears in the evidence (commands and outputs). Reward = sum / 8.
"""
import json
import math
import os
import re
import sys

ITEMS = ("verified", "consequences", "recovery", "used_information")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main(a):
    rev_p, ev_p = a[0], a[1]
    opts = dict(zip(a[2:], a[3:]))
    with open(opts["--reward"], "w") as f:
        f.write("0\n")
    ev = norm(open(ev_p, errors="replace").read())
    out = {"items": {}, "error": None}
    total = 0
    try:
        if os.path.islink(rev_p):
            raise ValueError("review.json is a link")
        rev = json.load(open(rev_p))
        for k in ITEMS:
            it = rev.get(k, {})
            s = it.get("score", 0)
            if s not in (0, 1, 2):
                s = 0
            quotes = [q for q in it.get("evidence", []) if isinstance(q, str)]
            found = [q for q in quotes if len(norm(q)) >= 8 and norm(q) in ev]
            kept = s if (s == 0 or found) else 0
            out["items"][k] = {"claimed": s, "kept": kept, "quotes": len(quotes), "quotes_found": len(found),
                               "why": str(it.get("why", ""))[:500]}
            total += kept
    except Exception as e:  # noqa: BLE001
        out["error"] = "%s: %s" % (type(e).__name__, e)
        total = 0
    r = total / 8.0
    if not math.isfinite(r):
        r = 0.0
    out["process"] = r
    json.dump(out, open(opts["--details"], "w"), indent=1)
    with open(opts["--reward"], "w") as f:
        f.write("%.6f\n" % r)
    print(json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1:])
