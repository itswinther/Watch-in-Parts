"""Pack one clean-agent chain run into a self-contained trajectory record.
    python3 tests/pack_run.py RUN_DIR OUT_DIR [--harness TEXT]
    python3 tests/pack_run.py --unpack PACK_DIR OUT_DIR    # rebuild every stageN/submission/parts/ byte for byte

RUN_DIR is what environment/run_clean_chain.sh leaves (stages are discovered by what exists,
not by a fixed count):
    stageN/            the agent's folder for stage N (INSTRUCTION.md, SPEC_WATCH.md, scripts/, submission/, ...)
    stageN.jsonl       headless `claude -p --output-format stream-json` transcript
    stageN.start/.end  epoch seconds
    stageN.skipped     present when the stage did not run (no submission from the stage before)
    chain.log          lines "stage N exit CODE" (124 = killed by the time limit)
    stageN.reward, stageN.details.json   grader outputs (after tests/grade_chain.py)

OUT_DIR schema (version "watch-chain-pack/2"):
    manifest.json
    parts_store/<sha256>.<ext>.gz                  each distinct submitted part file once (by SHA-256 of its
                                                   bytes), gzip with mtime 0 and no file name: deterministic
    stageN/INSTRUCTION.md, stageN/SPEC_WATCH.md   what the agent was given
    stageN/transcript.jsonl                        the transcript
    stageN/scripts/                                the agent's scripts (stageN/scripts in RUN_DIR)
    stageN/submission/                             movement.json, assembly.json, scripts/ as submitted, and
                                                   parts.json {"<name>.step": {"sha256": ..., "bytes": N}} in place
                                                   of parts/ (the part files are in parts_store/)
    stageN/details.json, stageN/reward.txt         grader outputs

manifest.json:
    schema           "watch-chain-pack/2"
    parts_store      {"files": distinct part files stored, "stored_bytes": total gz bytes, "raw_bytes": total
                      bytes of those distinct files, "references": part files over all stages}
    run              name of RUN_DIR (its basename only)
    model            model named in the first transcript's init event (or null)
    harness          --harness, else "claude-code <version> headless (claude -p, stream-json)"
    chain_score      product of the rewards of the expected stages 1 to 4 (EXPECTED_STAGES) and any other
                     stage found; a skipped or missing stage counts 0; null if a stage that ran is ungraded
    stages_run       number of stages with a transcript
    stages: list of {stage, ran, skipped, missing, start, end, duration_s, exit_code, killed_by_time_limit,
                     tool_calls, num_turns, cost_usd, result_subtype, reward, p, failed_gates,
                     failed_checks, inherited_failures, new_failures}
        inherited_failures / new_failures: failed checks of this stage that also / did not fail
        (as a check of the same name) in the stage before.
    total_cost_usd, total_tool_calls

Nothing outside RUN_DIR/stageN/{INSTRUCTION.md, SPEC_WATCH.md, scripts/, submission/} is copied apart from
the transcript and the grader outputs above (never tools/, work/, previous/). Every absolute host path in
text files (transcripts included) is rewritten: the stage folder (and the cwd the transcript's init event
names) becomes ".", RUN_DIR (and that cwd's parent) becomes "RUN", and
any other path under /home, /tmp, /root, /Users, /private, /var, /mnt or /workspace becomes "<host>/<basename>".
Binary files are copied unchanged. Part files (submission/parts/*) are never rewritten: they are stored
byte for byte (STEP headers written by the task's write_step carry only the base name, no host path), so an
unpacked part is exactly the submitted file and its SHA-256 is checked on unpack."""
import gzip
import hashlib
import json
import os
import re
import shutil
import sys

MAX_FILE_BYTES = 64 * 1024 * 1024
EXPECTED_STAGES = (1, 2, 3, 4)      # the chain; same list as STAGES in tests/grade_chain.py
HOST = re.compile(r"(?:/home|/tmp|/root|/Users|/private|/var|/mnt|/workspace)(?:/[^\s\"'\\<>|:;,()\[\]{}`]*)*")


def make_scrub(run, stage_dir, agent_cwd=None):
    pairs = {(os.path.realpath(stage_dir), "."), (os.path.abspath(stage_dir), "."),
             (os.path.realpath(run), "RUN"), (os.path.abspath(run), "RUN")}
    if agent_cwd and agent_cwd.startswith("/") and len(agent_cwd) > 1:     # where the agent ran, from the transcript
        pairs |= {(agent_cwd.rstrip("/"), "."), (os.path.dirname(agent_cwd.rstrip("/")), "RUN")}
    pairs = sorted((p for p in pairs if len(p[0]) > 1), key=lambda p: -len(p[0]))

    def scrub(text):
        for a, b in pairs:
            text = text.replace(a, b)
        return HOST.sub(lambda m: "<host>/" + (m.group(0).rstrip("/").rsplit("/", 1)[-1] or ""), text)
    return scrub


def copy_file(src, dst, scrub):
    if os.path.islink(src) or not os.path.isfile(src) or os.path.getsize(src) > MAX_FILE_BYTES:
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(src, "rb") as f:
        data = f.read()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = None
    if text is not None and "\x00" not in text:
        with open(dst, "w", encoding="utf-8") as f:
            f.write(scrub(text))
    else:
        with open(dst, "wb") as f:
            f.write(data)
    return True


def copy_tree(src, dst, scrub, skip_top=()):
    if not os.path.isdir(src) or os.path.islink(src):
        return 0
    n = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__" and not os.path.islink(os.path.join(root, d))
                         and not (root == src and d in skip_top))
        for f in sorted(files):
            if f.endswith(".pyc"):
                continue
            n += copy_file(os.path.join(root, f), os.path.join(dst, os.path.relpath(os.path.join(root, f), src)), scrub)
    return n


def store_parts(src, out, stats):
    """submission/parts/* -> parts_store/<sha256>.<ext>.gz (once each) and the parts.json mapping."""
    table = {}
    if not os.path.isdir(src) or os.path.islink(src):
        return table
    os.makedirs(os.path.join(out, "parts_store"), exist_ok=True)
    for f in sorted(os.listdir(src)):
        p = os.path.join(src, f)
        if os.path.islink(p) or not os.path.isfile(p) or os.path.getsize(p) > MAX_FILE_BYTES:
            continue
        with open(p, "rb") as fh:
            data = fh.read()
        h = hashlib.sha256(data).hexdigest()
        ext = os.path.splitext(f)[1].lstrip(".").lower() or "bin"
        dst = os.path.join(out, "parts_store", "%s.%s.gz" % (h, ext))
        if not os.path.isfile(dst):
            with open(dst, "wb") as raw:
                with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
                    gz.write(data)
            stats["files"] += 1
            stats["raw_bytes"] += len(data)
            stats["stored_bytes"] += os.path.getsize(dst)
        stats["references"] += 1
        table[f] = {"sha256": h, "bytes": len(data)}
    return table


def unpack(pack, out):
    """Rebuild PACK_DIR as a plain folder with every stageN/submission/parts/ restored, hashes checked."""
    if os.path.isdir(out):
        shutil.rmtree(out)
    shutil.copytree(pack, out, ignore=shutil.ignore_patterns("parts_store"))
    n = 0
    for st in sorted(os.listdir(out)):
        pj = os.path.join(out, st, "submission", "parts.json")
        if not os.path.isfile(pj):
            continue
        with open(pj) as f:
            table = json.load(f)
        pd = os.path.join(out, st, "submission", "parts")
        os.makedirs(pd, exist_ok=True)
        for name, e in table.items():
            if os.path.basename(name) != name or name.startswith("."):
                raise SystemExit("bad part name in %s: %r" % (pj, name))
            ext = os.path.splitext(name)[1].lstrip(".").lower() or "bin"
            with gzip.open(os.path.join(pack, "parts_store", "%s.%s.gz" % (e["sha256"], ext)), "rb") as gz:
                data = gz.read()
            if hashlib.sha256(data).hexdigest() != e["sha256"] or len(data) != e["bytes"]:
                raise SystemExit("hash mismatch for %s/%s" % (st, name))
            with open(os.path.join(pd, name), "wb") as f:
                f.write(data)
            n += 1
        os.remove(pj)
    print("unpacked %d part files into %s, every SHA-256 checked" % (n, os.path.basename(out)))


def read_num(path):
    try:
        with open(path) as f:
            return float(f.read().strip())
    except (OSError, ValueError):
        return None


def transcript_facts(path):
    facts = {"cwd": None, "model": None, "version": None, "tool_calls": 0, "num_turns": None, "cost_usd": None, "result_subtype": None}
    if not os.path.isfile(path):
        return facts
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if not isinstance(d, dict):
                continue
            if d.get("type") == "system" and d.get("subtype") == "init" and facts["model"] is None:
                facts["model"], facts["version"] = d.get("model"), d.get("claude_code_version")
                facts["cwd"] = d.get("cwd") if isinstance(d.get("cwd"), str) else None
            elif d.get("type") == "assistant":
                for b in (d.get("message") or {}).get("content") or []:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        facts["tool_calls"] += 1
            elif d.get("type") == "result":
                facts["num_turns"], facts["cost_usd"] = d.get("num_turns"), d.get("total_cost_usd")
                facts["result_subtype"] = d.get("subtype")
    return facts


def discover(run):
    found = set()
    for name in os.listdir(run):
        m = re.fullmatch(r"stage(\d+)(?:\.jsonl|\.skipped|\.start|\.reward)?", name)
        if m:
            found.add(int(m.group(1)))
    return sorted(found)


def main(argv):
    if argv and argv[0] == "--unpack":
        if len(argv) != 3:
            raise SystemExit(__doc__.split("\n\n")[0])
        return unpack(os.path.abspath(argv[1]), os.path.abspath(argv[2]))
    if len(argv) < 2:
        raise SystemExit(__doc__.split("\n\n")[0])
    stats = {"files": 0, "stored_bytes": 0, "raw_bytes": 0, "references": 0}
    run, out = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    harness = argv[argv.index("--harness") + 1] if "--harness" in argv else None
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    exits = {}
    if os.path.isfile(os.path.join(run, "chain.log")):
        for line in open(os.path.join(run, "chain.log")):
            m = re.match(r"stage (\d+) exit (-?\d+)", line.strip())
            if m:
                exits[int(m.group(1))] = int(m.group(2))
    stages, prev_failed, model, version = [], None, None, None
    chain, ungraded = 1.0, False
    for st in sorted(set(EXPECTED_STAGES) | set(discover(run))):
        sd = os.path.join(run, "stage%d" % st)
        od = os.path.join(out, "stage%d" % st)
        tr = os.path.join(run, "stage%d.jsonl" % st)
        facts = transcript_facts(tr)
        scrub = make_scrub(run, sd, facts["cwd"])
        skipped = os.path.isfile(os.path.join(run, "stage%d.skipped" % st))
        ran = os.path.isfile(tr)
        os.makedirs(od)
        for f in ("INSTRUCTION.md", "SPEC_WATCH.md"):
            copy_file(os.path.join(sd, f), os.path.join(od, f), scrub)
        copy_file(tr, os.path.join(od, "transcript.jsonl"), scrub)
        n_scripts = copy_tree(os.path.join(sd, "scripts"), os.path.join(od, "scripts"), scrub)
        n_sub = copy_tree(os.path.join(sd, "submission"), os.path.join(od, "submission"), scrub, skip_top=("parts",))
        table = store_parts(os.path.join(sd, "submission", "parts"), out, stats)
        if table:
            os.makedirs(os.path.join(od, "submission"), exist_ok=True)
            with open(os.path.join(od, "submission", "parts.json"), "w") as f:
                json.dump(table, f, indent=1, sort_keys=True)
        n_sub += len(table)
        copy_file(os.path.join(run, "stage%d.details.json" % st), os.path.join(od, "details.json"), scrub)
        copy_file(os.path.join(run, "stage%d.reward" % st), os.path.join(od, "reward.txt"), scrub)
        model = model or facts["model"]
        version = version or facts["version"]
        start, end = read_num(os.path.join(run, "stage%d.start" % st)), read_num(os.path.join(run, "stage%d.end" % st))
        reward = read_num(os.path.join(run, "stage%d.reward" % st))
        details = {}
        try:
            with open(os.path.join(run, "stage%d.details.json" % st)) as f:
                details = json.load(f)
        except (OSError, ValueError):
            pass
        if reward is None and isinstance(details.get("reward"), (int, float)):
            reward = float(details["reward"])
        failed_checks = sorted(k for k, v in (details.get("checks") or {}).items() if not v)
        failed_gates = sorted(k for k, v in (details.get("gates") or {}).items() if not v)
        failed = failed_gates + failed_checks
        inherited = sorted(set(failed) & prev_failed) if prev_failed is not None else []
        new = sorted(set(failed) - set(inherited))
        missing = not ran and not os.path.isdir(sd) and reward is None
        if skipped or missing:
            chain *= 0.0
        elif reward is None:
            ungraded = True
        else:
            chain *= reward
        code = exits.get(st)
        stages.append({"stage": st, "ran": ran, "skipped": skipped, "missing": missing, "start": start, "end": end,
                       "duration_s": (end - start) if start is not None and end is not None else None,
                       "exit_code": code, "killed_by_time_limit": code == 124,
                       "tool_calls": facts["tool_calls"], "num_turns": facts["num_turns"], "cost_usd": facts["cost_usd"],
                       "result_subtype": facts["result_subtype"], "reward": reward, "p": details.get("p"),
                       "failed_gates": failed_gates, "failed_checks": failed_checks,
                       "inherited_failures": inherited, "new_failures": new,
                       "files": {"scripts": n_scripts, "submission": n_sub}})
        prev_failed = set(failed) if details else None
    manifest = {"schema": "watch-chain-pack/2", "parts_store": stats, "run": os.path.basename(run.rstrip("/")), "model": model,
                "harness": harness or ("claude-code %s headless (claude -p, stream-json)" % version if version else None),
                "chain_score": None if ungraded or not stages else chain,
                "stages_run": sum(s["ran"] for s in stages),
                "total_cost_usd": sum(s["cost_usd"] or 0.0 for s in stages),
                "total_tool_calls": sum(s["tool_calls"] for s in stages),
                "stages": stages}
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print("packed %d stages of %s into %s" % (len(stages), manifest["run"], os.path.basename(out)))


if __name__ == "__main__":
    main(sys.argv[1:])
