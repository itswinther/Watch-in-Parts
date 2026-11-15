#!/usr/bin/env python3
"""Check Replay's data files against their sources.

    python3 check_data.py [--repo PATH]

For every run in data/runs/*.json:
  - every log line points at a line of its transcript that exists;
  - every quoted line (say, think, done, result, error, harness, submit-tool reply) appears
    word for word in that transcript line (ignoring spacing and the trailing "…");
  - every section score equals the grader output file it names;
  - the chain score equals the manifest.
Prints one line per problem and exits 1 if there are any.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
QUOTED = {"say", "think", "done", "result", "error", "harness"}


def strings(x):
    """Every string inside a decoded JSON event, joined."""
    if isinstance(x, str):
        return [x]
    if isinstance(x, dict):
        return [t for v in x.values() for t in strings(v)]
    if isinstance(x, list):
        return [t for v in x for t in strings(v)]
    return []


def norm(s):
    return " ".join(str(s).replace("\\n", " ").replace('\\"', '"').split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.join(os.path.dirname(HERE), "board-in-a-box"))
    repo = os.path.abspath(ap.parse_args().repo)
    problems, lines_checked, quotes_checked = [], 0, 0
    cache = {}

    for path in sorted(glob.glob(os.path.join(HERE, "data", "runs", "*.json"))):
        d = json.load(open(path))
        rid = d["run"]["id"]
        # sources live in the team repo, or (Harbor runs taken from a branch) in this folder's work/
        base = HERE if d["run"].get("source_root") == "replay" else repo
        man_path = os.path.join(base, d["run"]["chain_score_source"])
        if os.path.exists(man_path):
            m = json.load(open(man_path))
            cs = m.get("chain_score", m.get("reward"))
            if cs != d["run"]["chain_score"]:
                problems.append(f"{rid}: chain score {d['run']['chain_score']} != {man_path} {cs}")
        else:
            problems.append(f"{rid}: score source missing: {man_path}")
        for s in d["sections"]:
            src = os.path.join(base, s["score_source"])
            g = json.load(open(src))
            if s.get("score_key"):                     # one graded part inside the file, e.g. parts.P1
                for k in s["score_key"].split("."):
                    g = g[k]
                want = (g.get("s"), g.get("share_of_checks"))
            else:
                want = (g.get("reward"), g.get("p"))
            if want != (s["reward"], s["p"]):
                problems.append(f"{rid} {s['id']}: score {s['reward']}/{s['p']} != {src} {want}")
            if s.get("review"):                        # Part 5: every number in the breakdown
                sc = s["review"]["score"]
                if sc["reward"] != g.get("reward"):
                    problems.append(f"{rid} review: reward {sc['reward']} != {src}")
                for r in sc["rows"]:
                    gp = g["parts"][r["id"]]
                    if (r["s"], r["weight"]) != (gp["s"], gp["weight"]):
                        problems.append(f"{rid} review: {r['id']} row != {src}")
                if sc["honesty"]["factor"] != g["honesty"]["factor"] or sc["all_pass"] != g["all_pass"]:
                    problems.append(f"{rid} review: honesty factor or all-pass != {src}")
                quotes_checked += len(sc["rows"]) + 2
            for name in s.get("failed_checks", []):
                if g.get("checks", {}).get(name, True):
                    problems.append(f"{rid} {s['id']}: {name} shown failed but passes in {src}")
            for l in s["log"]:
                lines_checked += 1
                f = os.path.join(base, l["src"]["file"])
                if f not in cache:
                    cache[f] = open(f).read().splitlines()
                raw_lines = cache[f]
                n = l["src"]["line"]
                if not (1 <= n <= len(raw_lines)):
                    problems.append(f"{rid} {s['id']}: line {n} not in {f}")
                    continue
                quoted = None
                if f.endswith(".jsonl"):
                    raw = norm(" ".join(strings(json.loads(raw_lines[n - 1]))))  # decoded event, all text inside it
                else:                                  # a plain file (report.json): every line is a quote
                    raw = norm(raw_lines[n - 1])
                    quoted = l["text"]
                if quoted is not None:
                    pass
                elif l["kind"] in QUOTED:
                    quoted = l["text"]
                elif l["kind"] == "submit" and l["text"].startswith("Submit tool: "):
                    quoted = l["text"][len("Submit tool: "):]
                if quoted is not None:
                    quotes_checked += 1
                    q = norm(quoted.removesuffix(" …").removesuffix("…"))
                    if q not in raw:
                        problems.append(f"{rid} {s['id']} line {n} [{l['kind']}]: quote not found: {q[:90]}")
    for p in problems:
        print("PROBLEM", p)
    print(f"checked {lines_checked} log lines ({quotes_checked} quotes) and every score: "
          f"{len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
