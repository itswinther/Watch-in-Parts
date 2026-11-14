"""Grader for Moving Day. Run from this directory as:
    python -I grade_md.py /abs/plan.json [--instance flat-1] [--reward FILE] [--details FILE]
Opens exactly that one file, never runs submitted code, writes reward 0 first."""
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
    os.makedirs(os.path.dirname(os.path.abspath(reward_file)), exist_ok=True)
    with open(reward_file, "w") as f:
        f.write("0\n")
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or not argv[i - 1].startswith("--"))]
    if len(args) != 1 or not os.path.isabs(args[0]):
        print("usage: grade_md.py /abs/plan.json")
        return 2
    from geometry.md import grade
    res = grade(args[0], opts.get("--instance", "flat-1"))
    if opts.get("--details"):
        with open(opts["--details"], "w") as f:
            json.dump(res, f, indent=1, default=str)
    with open(reward_file, "w") as f:
        f.write("%.6f\n" % res["reward"])
    print(json.dumps({k: res[k] for k in ("reward", "p", "delivered", "notes")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
