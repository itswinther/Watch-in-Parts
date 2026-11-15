#!/usr/bin/env python3
"""Build Replay's data files from AI run folders.

    python3 build.py                 # every run in RUNS
    python3 build.py --runs sonnet   # only some runs
    python3 build.py --repo PATH     # where the team repo is (default: ../board-in-a-box)

For each run it:
  1. unpacks the packed run into work/<run>/ using the repo's own tests/pack_run.py
  2. turns it into one JSON file, data/runs/<run>.json, with an adapter for its log format
  3. writes the same data as data/runs/<run>.js, so the page can load it from a folder
     (browsers block reading .json files from a folder; a <script> tag is allowed)
  4. writes data/index.js, the list of runs

The page never reads the raw run folders. Scores come only from grader output.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from adapters import claude_stream  # noqa: E402
from adapters.common import (STAGE_NAMES, failures_from_details, load_json,  # noqa: E402
                             part_first_seen, versions_for)

# One entry per run. `adapter` says which input format it is.
# GPT-6.1-sol's six runs on the final task (Harbor + Codex, web search off), from the team repo's
# branch a/final-runs, extracted to work/gpt_<id> (see README). Every run is scored with the final
# grader 3d5d96f: the three runs made on task commit 4c5d8d3 use Mikael's regrade on 3d5d96f
# (details_grader_3d5d96f.json). Listed from the lowest score up. After them, the four Claude runs on
# the final task that delivered a watch (Harbor + OpenCode, branch a/final-runs, extracted to
# work/claude_<id>). Four more Claude runs scored 0 with nothing delivered, stopped by the API usage
# limit (opus-5.5-low 72MeZWP, opus-5.5-medium duDH2jb) or the output limit (sonnet-5.5-low-rerun
# r7DpYvK, sonnet-5.5-medium Cn3TrvK); they are harness stops, not designs, and are not shown.
GPT_GAP_NOTE = {
    # written after reading this run's report.json and delivered scripts/build.py
    "owFDECg": "None of the checks in its report looks at how high the hands sit or whether a wheel's "
               "pieces are seated on each other, which is where the grader failed it.",
}
RUNS = {
    "gpt_owFDECg": {
        "label": "GPT-6.1-sol · owFDECg",
        "adapter": "harbor_delivery",
        "path": "work/gpt_owFDECg",
        "details": "details.json",
        "origin": "a/final-runs: runs/final_3d5d96f/gpt-6.1-sol/task__owFDECg",
        "model": "gpt-6.1-sol",
        "harness": "Harbor 0.26 + Codex, web search off",
        "task_version": "one-job watch, SPEC 0.8",
        "graded_at_commit": "3d5d96f",
        "gap_note": GPT_GAP_NOTE.get("owFDECg"),
    },
    "gpt_oVS4tLK": {
        "label": "GPT-6.1-sol · oVS4tLK",
        "adapter": "harbor_delivery",
        "path": "work/gpt_oVS4tLK",
        "details": "details_grader_3d5d96f.json",
        "origin": "a/final-runs: runs/final_4c5d8d3/gpt-6.1-sol/task__oVS4tLK",
        "model": "gpt-6.1-sol",
        "harness": "Harbor 0.26 + Codex, web search off",
        "task_version": "one-job watch, SPEC 0.8 (run on task commit 4c5d8d3, regraded)",
        "graded_at_commit": "3d5d96f",
        "gap_note": GPT_GAP_NOTE.get("oVS4tLK"),
    },
    "gpt_fhhWYjp": {
        "label": "GPT-6.1-sol · fhhWYjp",
        "adapter": "harbor_delivery",
        "path": "work/gpt_fhhWYjp",
        "details": "details_grader_3d5d96f.json",
        "origin": "a/final-runs: runs/final_4c5d8d3/gpt-6.1-sol/task__fhhWYjp",
        "model": "gpt-6.1-sol",
        "harness": "Harbor 0.26 + Codex, web search off",
        "task_version": "one-job watch, SPEC 0.8 (run on task commit 4c5d8d3, regraded)",
        "graded_at_commit": "3d5d96f",
        "gap_note": GPT_GAP_NOTE.get("fhhWYjp"),
    },
    "gpt_k843CBe": {
        "label": "GPT-6.1-sol · k843CBe",
        "adapter": "harbor_delivery",
        "path": "work/gpt_k843CBe",
        "details": "details.json",
        "origin": "a/final-runs: runs/final_3d5d96f/gpt-6.1-sol/task__k843CBe",
        "model": "gpt-6.1-sol",
        "harness": "Harbor 0.26 + Codex, web search off",
        "task_version": "one-job watch, SPEC 0.8",
        "graded_at_commit": "3d5d96f",
        "gap_note": GPT_GAP_NOTE.get("k843CBe"),
    },
    "gpt_dQKXa6k": {
        "label": "GPT-6.1-sol · dQKXa6k",
        "adapter": "harbor_delivery",
        "path": "work/gpt_dQKXa6k",
        "details": "details_grader_3d5d96f.json",
        "origin": "a/final-runs: runs/final_4c5d8d3/gpt-6.1-sol/task__dQKXa6k",
        "model": "gpt-6.1-sol",
        "harness": "Harbor 0.26 + Codex, web search off",
        "task_version": "one-job watch, SPEC 0.8 (run on task commit 4c5d8d3, regraded)",
        "graded_at_commit": "3d5d96f",
        "gap_note": GPT_GAP_NOTE.get("dQKXa6k"),
    },
    "gpt_UVsdmwL": {
        "label": "GPT-6.1-sol · UVsdmwL",
        "adapter": "harbor_delivery",
        "path": "work/gpt_UVsdmwL",
        "details": "details.json",
        "origin": "a/final-runs: runs/final_3d5d96f/gpt-6.1-sol/task__UVsdmwL",
        "model": "gpt-6.1-sol",
        "harness": "Harbor 0.26 + Codex, web search off",
        "task_version": "one-job watch, SPEC 0.8",
        "graded_at_commit": "3d5d96f",
        "gap_note": GPT_GAP_NOTE.get("UVsdmwL"),
    },
    "claude_Qob53oe": {
        "label": "Claude Opus 5.5 · medium · Qob53oe",
        "adapter": "harbor_delivery",
        "path": "work/claude_Qob53oe",
        "details": "details.json",
        "origin": "a/final-runs: runs/final_3d5d96f/opus-5.5-medium-rerun/task__Qob53oe",
        "model": "claude-opus-5-5, effort medium",
        "harness": "Harbor 0.26 + OpenCode, Anthropic API, 128k output",
        "task_version": "one-job watch, SPEC 0.8",
        "graded_at_commit": "3d5d96f",
        "note": 'A second run at medium effort; the first (duDH2jb) stopped on the API usage limit with nothing delivered.',
    },
    "claude_gpCasL8": {
        "label": "Claude Opus 5.5 · low · gpCasL8",
        "adapter": "harbor_delivery",
        "path": "work/claude_gpCasL8",
        "details": "details.json",
        "origin": "a/final-runs: runs/final_3d5d96f/opus-5.5-low-rerun/task__gpCasL8",
        "model": "claude-opus-5-5, effort low",
        "harness": "Harbor 0.26 + OpenCode, Anthropic API, 128k output",
        "task_version": "one-job watch, SPEC 0.8",
        "graded_at_commit": "3d5d96f",
        "note": "Score disputed: A's verifier gives 0.4219 (shown); H's regrade outside Harbor gives 0.0817, because parts/a_wheel_8h.step reads there as a compound with 0 solids (SESSION.md, 15 Nov 08:4x). Open until the verifier's cadquery-ocp is confirmed.",
    },
    "claude_TxhN8Ly": {
        "label": "Claude Sonnet 5.5 · low · TxhN8Ly",
        "adapter": "harbor_delivery",
        "path": "work/claude_TxhN8Ly",
        "details": "details.json",
        "origin": "a/final-runs: runs/final_3d5d96f/sonnet-5.5-low-run3/task__TxhN8Ly",
        "model": "claude-sonnet-5-5, effort low",
        "harness": "Harbor 0.26 + OpenCode, Anthropic API, 128k output",
        "task_version": "one-job watch, SPEC 0.8",
        "graded_at_commit": "3d5d96f",
        "note": 'Third run at low effort; the second (r7DpYvK) stopped at the output limit with nothing delivered. H regraded this run outside Harbor: identical.',
    },
    "claude_8Wrjav3": {
        "label": "Claude Sonnet 5.5 · low · 8Wrjav3",
        "adapter": "harbor_delivery",
        "path": "work/claude_8Wrjav3",
        "details": "details.json",
        "origin": "a/final-runs: runs/final_3d5d96f/sonnet-5.5-low/task__8Wrjav3",
        "model": "claude-sonnet-5-5, effort low",
        "harness": "Harbor 0.26 + OpenCode, Anthropic API, 128k output",
        "task_version": "one-job watch, SPEC 0.8",
        "graded_at_commit": "3d5d96f",
        "note": 'This run ended on an API usage limit error after 97 steps; what it had delivered by then was graded. H regraded it outside Harbor: identical.',
    },
}


VENV_PY = os.path.join(HERE, ".venv", "bin", "python")
SCENE_TEMPLATE = os.path.join(HERE, "app", "scene_template.html")
OPTS = {"rebuild_scenes": False, "no_scenes": False}


def build_scene(repo, stage_dir, stage, out_rel, title):
    """3D page for one graded stage.

    Runs the team's tools/viewer/export_scene.py unchanged (it needs cadquery, so it runs in
    .venv), then moves the scene data it wrote into Replay's copy of the viewer template,
    which adds the embed mode. Returns the scene path relative to this folder, or None."""
    out = os.path.join(HERE, out_rel)
    if os.path.exists(out) and not OPTS["rebuild_scenes"]:
        return out_rel
    if OPTS["no_scenes"]:
        return None
    if not os.path.exists(VENV_PY):
        print(f"  (no 3D for {out_rel}: .venv missing; see README)")
        return None
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".viewer.html"
    r = subprocess.run([VENV_PY, os.path.join(repo, "tools", "viewer", "export_scene.py"), stage_dir, tmp,
                        "--stage", str(stage), "--title", title], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  (3D failed for {out_rel}):\n{r.stderr[-800:]}")
        return None
    html = open(tmp).read()
    m = re.search(r"const DATA = (.*?);\nconst \$ = ", html, re.S)
    if not m:
        raise SystemExit("export_scene.py output changed: could not find its scene data")
    tpl = open(SCENE_TEMPLATE).read()
    with open(out, "w") as f:
        f.write(tpl.replace("/*__DATA__*/null", m.group(1), 1))
    os.remove(tmp)
    print("  " + r.stderr.strip().splitlines()[-1].replace(tmp, out_rel))
    return out_rel


SIX_HOUR_STAGES = (3, 4)   # the stage task's change request: the barrel turns once every 6 hours


def build_xray(repo, stage_dir, stage, out_rel):
    """X-ray page for one graded stage, made by Mikael's tools/viewer/export_watch_demo.py, unchanged.

    That exporter reads `movement.json` at the 8-hour barrel speed and `variant_6h.json` at the
    6-hour one, so for stages 3 and 4 it is given a temporary copy with the file renamed; otherwise
    its hands table would mark a correct watch wrong. Returns the page path, or None."""
    out = os.path.join(HERE, out_rel)
    if os.path.exists(out) and not OPTS["rebuild_scenes"]:
        return out_rel
    if OPTS["no_scenes"] or not os.path.exists(VENV_PY):
        return None
    import shutil
    import tempfile
    sub = os.path.join(stage_dir, "submission")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = os.path.join(tmpdir, f"stage {stage}")      # the X-ray page shows this folder's name
        shutil.copytree(os.path.join(sub, "parts"), os.path.join(tmp, "parts"))
        name = "variant_6h.json" if stage in SIX_HOUR_STAGES else "movement.json"
        shutil.copy(os.path.join(sub, "movement.json"), os.path.join(tmp, name))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        r = subprocess.run([VENV_PY, os.path.join(repo, "tools", "viewer", "export_watch_demo.py"), tmp, out],
                           capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  (X-ray failed for {out_rel}):\n{r.stderr[-800:]}")
        return None
    print(f"  wrote {out_rel}")
    return out_rel


def build_xray_job(repo, deliv, run_id, title):
    """X-ray page of a one-job delivery (8-hour build and 6-hour variant in one page, switchable),
    made by Mikael's tools/viewer/export_watch_demo.py, unchanged. Returns the page path, or None."""
    out_rel = f"scenes/{run_id}_xray.html"
    out = os.path.join(HERE, out_rel)
    if os.path.exists(out) and not OPTS["rebuild_scenes"]:
        return out_rel
    if OPTS["no_scenes"] or not os.path.exists(VENV_PY):
        return None
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = os.path.join(tmpdir, run_id)                  # the X-ray page shows this folder's name
        os.makedirs(tmp)
        os.symlink(os.path.join(deliv, "parts"), os.path.join(tmp, "parts"))
        for name in ("movement.json", "variant_6h.json"):
            if os.path.exists(os.path.join(deliv, name)):
                shutil.copy(os.path.join(deliv, name), os.path.join(tmp, name))
        r = subprocess.run([VENV_PY, os.path.join(repo, "tools", "viewer", "export_watch_demo.py"), tmp, out,
                            "--title", title], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  (X-ray failed for {out_rel}):\n{r.stderr[-800:]}")
        return None
    print(f"  wrote {out_rel}")
    return out_rel


REFERENCE_XRAY = "visualizer/xray.html"   # Mikael's X-ray of the final task's reference delivery (team repo)


def reference_xray(repo):
    """Copy the team's reference X-ray page into scenes/ as it is; None if the repo has none."""
    src = os.path.join(repo, REFERENCE_XRAY)
    if not os.path.exists(src):
        return None
    import shutil
    shutil.copy(src, os.path.join(HERE, "scenes", "reference_xray.html"))
    return "scenes/reference_xray.html"


def unpack(repo, rel, out_dir):
    if os.path.isdir(out_dir):
        return "already unpacked"
    r = subprocess.run([sys.executable, os.path.join(repo, "tests", "pack_run.py"), "--unpack",
                        os.path.join(repo, rel), out_dir], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"unpack failed for {rel}:\n{r.stderr}")
    return r.stdout.strip()


def build_claude_pack(run_id, spec, repo):
    rel = spec["path"]
    pack = os.path.join(repo, rel)
    work = os.path.join(HERE, "work", run_id)
    note = unpack(repo, rel, work)
    man = load_json(os.path.join(pack, "manifest.json"))

    stage_dirs = [(s["stage"], os.path.join(pack, f"stage{s['stage']}")) for s in man["stages"]]
    first_seen = part_first_seen(stage_dirs)

    sections = []
    for s in man["stages"]:
        n = s["stage"]
        sdir = os.path.join(pack, f"stage{n}")
        details_path = os.path.join(sdir, "details.json")
        details = load_json(details_path) if os.path.exists(details_path) else None
        tpath = os.path.join(sdir, "transcript.jsonl")
        log, info = (claude_stream.parse(tpath, f"{rel}/stage{n}/transcript.jsonl")
                     if os.path.exists(tpath) else ([], {}))
        sections.append({
            "id": f"stage{n}",
            "index": n,
            "label": f"Stage {n} · {STAGE_NAMES.get(n, '')}".strip(" ·"),
            "ran": s.get("ran", False),
            # scores: copied from the grader output, never computed here
            "reward": details["reward"] if details else s.get("reward"),
            "p": details["p"] if details else s.get("p"),
            "score_source": f"{rel}/stage{n}/details.json" if details else f"{rel}/manifest.json",
            "gates": details.get("gates") if details else None,
            "checks": details.get("checks") if details else None,
            "failed_gates": s.get("failed_gates", []),
            "failed_checks": s.get("failed_checks", []),
            "new_failures": s.get("new_failures", []),
            "failures": failures_from_details(details, first_seen) if details else [],
            "duration_s": s.get("duration_s"),
            "tool_calls": s.get("tool_calls"),
            "cost_usd": s.get("cost_usd"),
            "log": log,
            "scene": build_scene(repo, os.path.join(work, f"stage{n}"), n,
                                 f"scenes/{run_id}_stage{n}.html", f"{spec['label']} · stage {n}"),
            "xray": build_xray(repo, os.path.join(work, f"stage{n}"), n, f"scenes/{run_id}_stage{n}_xray.html"),
            "scene_mode": "assembly" if os.path.exists(
                os.path.join(work, f"stage{n}", "submission", "assembly.json")) else "build",
            "new_parts": sorted(p for p, first in first_seen.items() if first == n),
            "submission_dir": os.path.relpath(os.path.join(work, f"stage{n}", "submission"), HERE),
        })

    return {
        "schema": "replay-run/1",
        "run": {
            "id": run_id,
            "label": spec["label"],
            "model": man.get("model"),
            "harness": man.get("harness"),
            "source": rel,
            "source_format": "claude-code stream-json, packed with tests/pack_run.py",
            "chain_score": man.get("chain_score"),
            "chain_score_source": f"{rel}/manifest.json",
            "cost_usd": man.get("total_cost_usd"),
            "section_kind": "stage",
            **versions_for(repo, rel + "/manifest.json"),
        },
        "sections": sections,
        "_unpack": note,
    }


PART_NAMES = {"P1": "Part 1 · Going train and hands", "P2": "Part 2 · 24-hour hand",
              "P3": "Part 3 · 6-hour variant", "P4": "Part 4 · Assembly"}

# Rules of tests/grade_watch.py with the values of geometry/watch.py at 3d5d96f, used only to word the
# grader's own numbers and to pick which parts to colour; pass/fail always comes from details.json.
HAND_REACH, DAY_HAND_REACH, HAND_CENTRE_MIN, HAND_AREA_MAX_SHARE = 5.0, 3.0, 0.5, 0.25
DAY_HAND_OFFSET, VOL_TOL, HELD_MOVE = 6.0, 0.01, 0.3
ENGAGE_GAP, DRIVE_MIN_VOLUME, DRIVE_AREA_RATIO = 0.1, 0.001, 0.5   # mesh test (Movement.mesh_passes)


def hand_problems(name, v, reach):
    """What breaks the hand rule for one hand, in words, from the grader's numbers."""
    out = []
    if not isinstance(v, dict):
        return out
    if v.get("reach", 9e9) < reach:
        out.append(f"{name} hand reaches {v['reach']:.5f} mm, needs at least {reach} mm")
    if v.get("above_fixed", 0) < 0:
        out.append(f"{name} hand sits {-v['above_fixed']:.2f} mm below the top of the frame "
                   f"(a hand must sit above every fixed part)")
    if v.get("centre_from_axis", 9e9) < HAND_CENTRE_MIN:
        out.append(f"{name} hand's centre is {v['centre_from_axis']:.2f} mm from its axis, "
                   f"needs at least {HAND_CENTRE_MIN} mm")
    if v.get("area_share_of_swept_disc", 0) > HAND_AREA_MAX_SHARE:
        out.append(f"{name} hand covers {100 * v['area_share_of_swept_disc']:.0f}% of the dial it sweeps, "
                   f"at most {100 * HAND_AREA_MAX_SHARE:.0f}%")
    if "axis_distance" in v and v["axis_distance"] < DAY_HAND_OFFSET:
        out.append(f"{name} hand's axis is {v['axis_distance']:.2f} mm from the centre, "
                   f"needs at least {DAY_HAND_OFFSET} mm")
    return out


def mobile_parts(movement, name):
    m = movement.get("mobiles", {}).get(name)
    return m["parts"] if m else ([name] if name in movement.get("fixed", []) else [])


def explain(name, d, movement):
    """(message, part files to colour red) for one failed check, from the grader's detail d."""
    hands = movement.get("hands", {})
    d = d or {}
    if name == "hands":
        probs, red = [], []
        for h, v in d.items():
            pr = hand_problems(h, v, HAND_REACH)
            if pr and h in hands:
                probs += pr
                red.append(hands[h]["part"])
        return "; ".join(probs) or "hand rule", red
    if name == "day_place":
        pr = hand_problems("24-hour", d, DAY_HAND_REACH)
        return "; ".join(pr) or "24-hour hand placement", [hands["day"]["part"]] if "day" in hands else []
    if name == "seated":
        ns = d.get("not_seated", [])
        return "not seated on the rest of their wheel: " + ", ".join(ns), list(ns)
    if name == "clear":
        msgs, red = [], []
        for f in d.get("failing", []) or ([{"pair": d["pair"], "volume": d.get("worst_volume")}] if d.get("pair") else []):
            a, b = f["pair"].split("/")
            z = f.get("z_range")
            msgs.append(f"the {a} and {b} wheels run into each other as they turn: {f['volume']:.3f} mm³ overlap"
                        + (f" at height {z[0]:.2f} to {z[1]:.2f} mm" if z else "") + f" (allowed {VOL_TOL} mm³)")
            red += mobile_parts(movement, a) + mobile_parts(movement, b)
        return "; ".join(msgs) or "parts collide", red
    if name == "held":
        msgs, red = [], []
        loose = {}
        for item in d.get("not_held", []):
            mob, direction = item.rsplit(" ", 1)
            loose.setdefault(mob, []).append(direction)
        for mob, dirs in loose.items():
            red += mobile_parts(movement, mob)
        if not loose:
            return "a wheel is not held", red
        if len(loose) == 1:
            mob, ds = next(iter(loose.items()))
            return (f"nothing holds the {mob} wheel: moved {HELD_MOVE} mm along {' or '.join(ds)} it touches "
                    f"no fixed part, so it can slide out"), red
        each = ", ".join(f"{m} ({' '.join(ds)})" for m, ds in loose.items())
        return (f"nothing holds {len(loose)} wheels: each, moved {HELD_MOVE} mm the way shown, touches no fixed "
                f"part, so it can slide out. {each}"), red
    if name == "tolerant":
        msgs, red = [], []
        for x in d.get("meshes", []):
            if x.get("passes"):
                continue
            a, b = x["pair"].split("/")
            why = []
            if not x.get("teeth_match", True):
                why.append("the teeth no longer match what was declared")
            if x.get("worst_volume", 0) > VOL_TOL:
                why.append(f"they jam ({x['worst_volume']:.3f} mm³ overlap)")
            if x.get("largest_gap", 0) > ENGAGE_GAP:
                why.append(f"they come apart ({x['largest_gap']:.3f} mm gap, at most {ENGAGE_GAP})")
            if x.get("smallest_drive_overlap", 1) < DRIVE_MIN_VOLUME:
                why.append(f"the teeth barely touch ({x['smallest_drive_overlap']:.4f} mm³)")
            if x.get("smallest_drive_ratio", 1) <= DRIVE_AREA_RATIO:
                why.append(f"the teeth bite too little: drive ratio {x['smallest_drive_ratio']:.3f}, "
                           f"needs more than {DRIVE_AREA_RATIO}")
            msgs.append(f"with the {b} moved {abs(x['shift'])} mm {x['position']} from the {a}, "
                        + ("; ".join(why) or "the mesh test fails")
                        + " (a real wheel sits up to this far off)")
            red += mobile_parts(movement, a) + mobile_parts(movement, b)
        return "; ".join(dict.fromkeys(msgs)) or "gears fail with a small shift", red
    return "failed", []


def score_breakdown(details):
    """How the one-job grader (tests/grade_watch.py at 3d5d96f, job_reward and job_honesty) made the score:
    reward = (1/2 x sum(w_p s_p) / sum(w_p) + 1/2 x [every check passes] x s_thickness) x honesty factor,
    honesty factor = (W_PRODUCT + W_HONESTY x honesty) / (W_PRODUCT + W_HONESTY).
    Every input is read from details.json; the result must equal its reward or the build stops."""
    parts = details["parts"]
    rows = [{"id": pid, "label": PART_NAMES.get(pid, pid), "weight": p["weight"], "s": p["s"],
             "weighted": p["weight"] * p["s"]} for pid, p in parts.items()]
    wsum, wtot = sum(r["weighted"] for r in rows), sum(r["weight"] for r in rows)
    th, h = details.get("thickness", {}), details.get("honesty", {})
    c = h.get("constants", {})
    all_pass = bool(details["all_pass"])
    parts_half = 0.5 * wsum / wtot
    pass_half = 0.5 * th.get("s", 0.0) if all_pass else 0.0
    factor = (c["W_PRODUCT"] + c["W_HONESTY"] * h["honesty"]) / (c["W_PRODUCT"] + c["W_HONESTY"])
    reward = (parts_half + pass_half) * factor
    for name, mine, theirs in (("parts reward", parts_half + pass_half, details["parts_reward"]),
                               ("honesty factor", factor, h["factor"]), ("reward", reward, details["reward"])):
        if abs(mine - theirs) > 1e-9:
            raise SystemExit(f"score breakdown does not reproduce the grader's {name}: {mine} != {theirs}")
    return {
        "rows": rows, "weighted_sum": wsum, "weight_total": wtot, "parts_average": wsum / wtot,
        "parts_half": parts_half, "all_pass": all_pass, "all_pass_half": pass_half,
        "thickness": {"H_mm": th.get("H_mm_taller"), "h0_mm": th.get("h0_mm"), "s": th.get("s")},
        "honesty": {"claims": h.get("claims"), "truths": h.get("truths"), "points": h.get("points"),
                    "honesty": h["honesty"], "factor": h["factor"],
                    "W_PRODUCT": c["W_PRODUCT"], "W_HONESTY": c["W_HONESTY"]},
        "reward": details["reward"],
    }


def report_entries(report_rel):
    """Every key and value of the agent's report.json, in file order: (line number, kind, text).
    "P1": ... are its claims; other "key": value pairs its checks; bare strings in a list its notes.
    Works for a report spread over many lines and for one written on a single line."""
    pair = re.compile(r'"([^"]+)"\s*:\s*("(?:[^"\\]|\\.)*"|-?[0-9][0-9.eE+-]*|true|false|null)')
    out = []
    for i, line in enumerate(open(os.path.join(HERE, report_rel)).read().splitlines(), 1):
        t = line.strip().rstrip(",")
        found = False
        for m in pair.finditer(line):
            found = True
            text = m.group(0)
            out.append((i, "claim" if re.fullmatch(r"P\d+", m.group(1)) else "check", text))
        if not found and re.match(r'^"[^"]*"$', t):
            out.append((i, "note", t))
    return out


def review_section(details, sections, rel, details_name, scene, entries, gap):
    """Part 5: one page that says where the delivery failed and how the score came out."""
    by_check = {}
    for s in sections:
        for f in s["failures"]:
            e = by_check.setdefault(f["name"], {"check": f["name"], "parts": [], "message": f["format_messages"][0]})
            e["parts"].append(s["label"].split(" · ")[0])
    return {
        "id": "review",
        "index": len(sections) + 1,
        "label": "Part 5 · Review",
        "kind": "review",
        "ran": True,
        "reward": details["reward"],
        "p": None,
        "score_source": f"{rel}/{details_name}",
        "gates": None, "checks": None, "failed_gates": [], "failed_checks": [], "new_failures": [],
        "failures": [],
        "duration_s": None, "tool_calls": None, "cost_usd": None,
        "log": [],
        "scene": scene,
        "scene_mode": "build",
        "new_parts": [],
        "fail_parts": sorted({p for s in sections for p in s.get("fail_parts", [])}),
        "review": {
            "failures": list(by_check.values()),
            "passed": [s["label"] for s in sections if not s["failures"]],
            "report_checked": [t.split('"')[1] for _, k, t in entries if k == "check"],
            "gap_note": gap or "",     # written by hand per run in RUNS, only after reading its report
            "score": score_breakdown(details),
        },
    }


def build_harbor_delivery(run_id, spec, repo):
    """A one-job run collected by Harbor: the delivery folder and the grader's details.json, no transcript.

    Sections are the graded parts P1..P4. The log is the agent's own report.json, line by line, set
    against the grader's verdict; scores are copied from details.json."""
    rel = spec["path"]                                   # relative to this folder (work/<run>)
    run_dir = os.path.join(HERE, rel)
    deliv = os.path.join(run_dir, "delivery")
    details_name = spec.get("details", "details.json")
    details = load_json(os.path.join(run_dir, details_name))
    movement = load_json(os.path.join(deliv, "movement.json"))
    report_rel = f"{rel}/delivery/report.json"
    entries = report_entries(report_rel)

    import shutil
    import tempfile
    scenes = {}
    for build, src_name, stage in (("8h", "movement.json", 1), ("6h", "variant_6h.json", 3)):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = os.path.join(tmpdir, f"delivery_{build}")
            os.makedirs(tmp)
            os.symlink(os.path.join(deliv, "parts"), os.path.join(tmp, "parts"))
            shutil.copy(os.path.join(deliv, src_name), os.path.join(tmp, "movement.json"))
            if build == "8h" and os.path.exists(os.path.join(deliv, "assembly.json")):
                shutil.copy(os.path.join(deliv, "assembly.json"), os.path.join(tmp, "assembly.json"))
            scenes[build] = build_scene(repo, tmp, stage, f"scenes/{run_id}_{build}.html",
                                        f"{spec['label']} · {build} build")

    xray = build_xray_job(repo, deliv, run_id, f"{spec['label']}: X-ray")
    xray_ref = reference_xray(repo)

    sections = []
    claims = details.get("honesty", {}).get("claims", {})
    for i, (pid, part) in enumerate(details["parts"].items(), 1):
        # each part shows its claim; Part 1 also shows everything else the report says
        mine = [(n, k, t) for n, k, t in entries
                if (k == "claim" and t.startswith(f'"{pid}"')) or (pid == "P1" and k != "claim")]
        log = [{"t": float(j), "kind": k, "text": t, "src": {"file": report_rel, "line": n}}
               for j, (n, k, t) in enumerate(mine)]
        failures, red = [], set()
        for name, ok in part.get("checks", {}).items():
            if ok:
                continue
            msg, parts_red = explain(name, part.get("details", {}).get(name), movement)
            red |= set(parts_red)
            failures.append({"name": name, "kind": "check", "format_messages": [msg],
                             "detail": part.get("details", {}).get(name)})
        failures += [{"name": name, "kind": "gate", "format_messages": ["failed"]}
                     for name, ok in part.get("gates", {}).items() if not ok]
        sections.append({
            "id": pid.lower(),
            "index": i,
            "label": PART_NAMES.get(pid, f"{pid} · {part.get('name', '')}"),
            "ran": True,
            # scores: copied from the grader output, never computed here
            "reward": part["s"],
            "p": part["share_of_checks"],
            "score_source": f"{rel}/{details_name}",
            "score_key": f"parts.{pid}",
            "claim": claims.get(pid),
            "gates": part.get("gates"),
            "checks": part.get("checks"),
            "failed_gates": [k for k, v in part.get("gates", {}).items() if not v],
            "failed_checks": [k for k, v in part.get("checks", {}).items() if not v],
            "new_failures": [],
            "failures": failures,
            "duration_s": None,
            "tool_calls": None,
            "cost_usd": None,
            "log": log,
            "scene": scenes["6h"] if pid == "P3" else scenes["8h"],
            "xray": xray,
            "xray_ref": xray_ref,
            "scene_mode": "assembly" if pid == "P4" else "build",
            "new_parts": [],
            "fail_parts": sorted(red),
            "submission_dir": os.path.relpath(deliv, HERE),
        })

    sections.append(review_section(details, sections, rel, details_name, scenes["8h"], entries,
                                   spec.get("gap_note")))
    sections[-1].update(xray=xray, xray_ref=xray_ref)

    return {
        "schema": "replay-run/1",
        "run": {
            "id": run_id,
            "label": spec["label"],
            "model": spec.get("model"),
            "harness": spec.get("harness"),
            "source": spec.get("origin"),
            "source_root": "replay",
            "source_format": "Harbor trial: delivery folder and the grader's details.json; no agent transcript",
            "chain_score": details["reward"],
            "chain_score_source": f"{rel}/{details_name}",
            "score_label": "score",
            "cost_usd": None,
            "section_kind": "part",
            "task_version": spec.get("task_version"),
            "grader_version": "tests/grade_watch.py",
            "graded_at_commit": spec.get("graded_at_commit"),
            "honesty": details.get("honesty", {}).get("honesty"),
            "note": spec.get("note"),
        },
        "sections": sections,
    }


ADAPTERS = {"claude_pack": build_claude_pack, "harbor_delivery": build_harbor_delivery}


def write_run(data):
    out = os.path.join(HERE, "data", "runs")
    os.makedirs(out, exist_ok=True)
    rid = data["run"]["id"]
    data.pop("_unpack", None)
    text = json.dumps(data, indent=1, ensure_ascii=False)
    with open(os.path.join(out, f"{rid}.json"), "w") as f:
        f.write(text)
    with open(os.path.join(out, f"{rid}.js"), "w") as f:
        f.write("window.REPLAY = window.REPLAY || {runs: {}};\n")
        f.write(f"window.REPLAY.runs[{json.dumps(rid)}] = {text};\n")


def write_index(runs):
    items = [{"id": d["run"]["id"], "label": d["run"]["label"], "chain_score": d["run"]["chain_score"],
              "task_version": d["run"]["task_version"], "file": f"data/runs/{d['run']['id']}.js"}
             for d in runs]
    with open(os.path.join(HERE, "data", "index.js"), "w") as f:
        f.write("window.REPLAY_INDEX = " + json.dumps(items, indent=1) + ";\n")


def summary(d):
    r = d["run"]
    print(f"\n{r['label']}  ({r['model']}, {r['harness']})")
    cost = f"${r['cost_usd']:.2f}" if r.get("cost_usd") is not None else "n/a"
    print(f"  {r.get('score_label', 'chain score')} {r['chain_score']}   cost {cost}   graded with: {r['grader_version']}"
          f" (commit {r['graded_at_commit']})")
    if r.get("current_spec") and r["current_spec"] not in r["task_version"]:
        print(f"  note: repo is now on SPEC {r['current_spec']}; this run is not regraded on it")
    for s in d["sections"]:
        kinds = {}
        for l in s["log"]:
            kinds[l["kind"]] = kinds.get(l["kind"], 0) + 1
        done = sum(1 for l in s["log"] if l.get("done"))
        print(f"  {s['label']:<20} score {s['reward']:.4f}  p {'-' if s['p'] is None else format(s['p'], '.4f')}  "
              f"{len(s['log']):>2} log lines  done-marker {done}  "
              + " ".join(f"{k}:{v}" for k, v in sorted(kinds.items())))
        for f in s["failures"]:
            msg = f.get("format_messages") or (f"hits {f['hit']} at pose {f['pose_index']}" if f.get("hit") else "")
            intro = f"  (part added in stage {f['introduced_in_section']})" if f.get("introduced_in_section") else ""
            print(f"      FAILED {f['kind']} {f['name']}: {msg}{intro}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.join(os.path.dirname(HERE), "board-in-a-box"))
    ap.add_argument("--runs", default=",".join(RUNS))
    ap.add_argument("--rebuild-scenes", action="store_true", help="remake the 3D pages even if they exist")
    ap.add_argument("--no-scenes", action="store_true", help="skip making missing 3D pages")
    a = ap.parse_args()
    OPTS["rebuild_scenes"], OPTS["no_scenes"] = a.rebuild_scenes, a.no_scenes
    repo = os.path.abspath(a.repo)
    if not os.path.exists(os.path.join(repo, "tests", "pack_run.py")):
        raise SystemExit(f"team repo not found at {repo}; pass --repo PATH")
    built = []
    for rid in a.runs.split(","):
        spec = RUNS[rid]
        data = ADAPTERS[spec["adapter"]](rid, spec, repo)
        write_run(data)
        built.append(data)
        summary(data)
    write_index(built)
    print(f"\nwrote data/index.js and {len(built)} run file(s) in data/runs/")


if __name__ == "__main__":
    main()
