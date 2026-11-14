"""Grader for instance H2. Run from this directory as:
    python -I grade_h2.py /abs/base.stl /abs/lid.stl /abs/assembly.json [--reward FILE] [--details FILE]
Opens exactly those three files, never runs submitted code, writes reward 0 first."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (HERE, os.path.dirname(HERE)):
    if os.path.isdir(os.path.join(cand, "geometry")):
        sys.path.insert(0, cand)
        break


def main(argv):
    opts = dict(zip(argv, argv[1:]))
    reward_file = opts.get("--reward", "/logs/verifier/reward.txt")
    details_file = opts.get("--details")
    os.makedirs(os.path.dirname(os.path.abspath(reward_file)), exist_ok=True)
    with open(reward_file, "w") as f:
        f.write("0\n")
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or not argv[i - 1].startswith("--"))]
    if len(args) != 3 or not all(os.path.isabs(a) for a in args):
        print("usage: grade_h2.py /abs/base.stl /abs/lid.stl /abs/assembly.json")
        return 2
    from geometry.h2_checks import grade
    res = grade(*args)
    if details_file:
        with open(details_file, "w") as f:
            json.dump(res, f, indent=1, default=str)
    with open(reward_file, "w") as f:
        f.write("%.6f\n" % res["reward"])
    print(json.dumps({k: res[k] for k in ("reward", "p", "size_term", "bbox_volume", "gates", "checks")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
