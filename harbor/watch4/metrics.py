"""Post-hoc size and margin numbers for graded watch stages (does not change B's grader or score).

    python3 harbor/watch4/metrics.py LABEL=DETAILS.json [LABEL=DETAILS.json ...]

Per stage: case radius used and movement height (z_max - z_min) from details.size, the smallest
drive overlap and largest mesh gap over all meshes (details.train), the largest thickness
deviation (details.printable), and the reward. "Volume" is pi r^2 h, the case cylinder it needs.
"""
import json
import math
import sys


def row(label, path):
    d = json.load(open(path))
    det = d.get("details", {})
    size = det.get("size") or {}
    r, z0, z1 = size.get("radius"), size.get("z_min"), size.get("z_max")
    h = (z1 - z0) if z0 is not None and z1 is not None else None
    meshes = (det.get("train") or {}).get("meshes") or []
    ov = [m["smallest_drive_overlap"] for m in meshes if m.get("smallest_drive_overlap") is not None]
    gap = [m["largest_gap"] for m in meshes if m.get("largest_gap") is not None]
    pr = det.get("printable") or {}
    dev = [v.get("max_deviation") for v in pr.values() if isinstance(v, dict) and v.get("max_deviation") is not None]
    vol = math.pi * r * r * h if r and h else None
    f = lambda x, n=2: "-" if x is None else ("%.*f" % (n, x))
    return "| %s | %s | %s | %s | %s | %s | %s | %s |" % (
        label, f(d.get("reward"), 4), f(r), f(h), f(vol, 0), f(min(ov) if ov else None, 4),
        f(max(gap) if gap else None, 4), f(max(dev) if dev else None, 3))


def main(argv):
    print("| Run | Reward | Radius | Height | Case volume mm3 | Min drive overlap | Max mesh gap | Max thickness dev |")
    print("|---|---|---|---|---|---|---|---|")
    for a in argv:
        label, path = a.split("=", 1)
        try:
            print(row(label, path))
        except Exception as e:  # noqa: BLE001
            print("| %s | unreadable (%s) | | | | | | |" % (label, type(e).__name__))


if __name__ == "__main__":
    main(sys.argv[1:])
