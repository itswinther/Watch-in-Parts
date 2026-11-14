"""Read Harbor job and trial directories into plain dicts (shared by summarize.py, index.py, incidents.py).

Standard library only. Works on:
  - Harbor 0.25 / 0.26 job dirs: JOB/{config.json,result.json,lock.json} + JOB/<trial>/{result.json,
    agent/,verifier/,artifacts/};
  - a folder of jobs (e.g. -o jobs), searched recursively;
  - collected copies in the repo (flat: result.json, reward.txt, details.json, codex.txt next to each other).
Every field is optional: a missing file gives None, never an exception.
"""
import glob
import json
import math
import os
import re
from datetime import datetime

AT_STEPS = ("AT-0", "AT-1", "AT-2", "AT-3", "AT-4", "AT-5", "AT-6")
STEP_NAMES = ("assemble", "wind", "hold", "run", "backward", "set", "return")
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp")


def load_json(path):
    try:
        with open(path, errors="replace") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def first(*paths):
    for p in paths:
        if p and os.path.isfile(p):
            return p
    return None


def _t(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def span(d):
    """Seconds between d['started_at'] and d['finished_at'], or None."""
    if not isinstance(d, dict):
        return None
    a, b = _t(d.get("started_at")), _t(d.get("finished_at"))
    if a is None or b is None:
        return None
    if (a.tzinfo is None) != (b.tzinfo is None):
        a, b = a.replace(tzinfo=None), b.replace(tzinfo=None)
    return (b - a).total_seconds()


def find_trials(roots):
    """Every trial directory under the given paths (a trial is a dir whose result.json has trial_name, or a
    collected run dir with reward.txt or details.json)."""
    out = []
    for root in roots:
        root = os.path.abspath(root)
        for dirpath, dirnames, files in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("artifacts", "agent", "verifier", "node_modules",
                                                            "sessions", "parts_store", "scripts")]
            r = load_json(os.path.join(dirpath, "result.json")) if "result.json" in files else None
            if isinstance(r, dict) and "trial_name" in r:
                out.append(dirpath)                        # a Harbor trial (or a collected copy of one)
            elif r is None and "reward.txt" in files:
                out.append(dirpath)                        # a collected run without Harbor's result.json
    return sorted(set(out))


def job_of(trial):
    """(job_dir, job_result, job_lock) for a trial dir, if its parent is a Harbor job."""
    job = os.path.dirname(trial)
    jr = load_json(os.path.join(job, "result.json"))
    if isinstance(jr, dict) and "n_total_trials" in jr:
        return job, jr, load_json(os.path.join(job, "lock.json"))
    return None, None, None


def agent_log(trial):
    return first(os.path.join(trial, "agent", "opencode.txt"), os.path.join(trial, "agent", "codex.txt"),
                 os.path.join(trial, "opencode.txt"), os.path.join(trial, "codex.txt"))


def opencode_usage(path):
    """Cost and tokens summed over OpenCode step_finish events (as harbor/watch4/cost.py)."""
    cost, tin, tout, tcache, n = 0.0, 0, 0, 0, 0
    try:
        with open(path, errors="replace") as f:
            for line in f:
                if '"step_finish"' not in line:
                    continue
                try:
                    p = json.loads(line).get("part") or {}
                except ValueError:
                    continue
                n += 1
                cost += float(p.get("cost") or 0)
                tk = p.get("tokens") or {}
                tin += int(tk.get("input") or 0)
                tout += int(tk.get("output") or 0) + int(tk.get("reasoning") or 0)
                tcache += int((tk.get("cache") or {}).get("read") or 0)
    except OSError:
        return None
    return {"cost_usd": cost, "n_input_tokens": tin, "n_output_tokens": tout, "n_cache_tokens": tcache,
            "steps": n} if n else None


def tool_calls(trial, last=None):
    """[(log_path, line_no, tool, short_input)] for the agent's tool calls, in order.
    Reads the raw OpenCode or Codex JSON stream so that line numbers point into the saved log."""
    p = agent_log(trial)
    calls = []
    if not p:
        return calls
    with open(p, errors="replace") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if ev.get("type") == "tool_use":                              # OpenCode
                part = ev.get("part") or {}
                inp = (part.get("state") or {}).get("input")
                calls.append((p, i, str(part.get("tool", "?")), _short(inp)))
                continue
            item = ev.get("item") or {}
            if ev.get("type") == "item.started" and item.get("type") in (
                    "command_execution", "function_call", "custom_tool_call", "mcp_tool_call", "file_change"):
                text = item.get("command") or item.get("arguments") or item.get("input") or item.get("changes")
                calls.append((p, i, item.get("type"), _short(text)))
    return calls[-last:] if last else calls


def _short(x, n=160):
    if x is None:
        return ""
    s = x if isinstance(x, str) else json.dumps(x)
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n - 1] + "…"


def final_message(trial):
    """The agent's last text message (OpenCode text event, Codex agent_message, or ATIF last agent step)."""
    traj = load_json(os.path.join(trial, "agent", "trajectory.json"))
    if isinstance(traj, dict):
        for st in reversed(traj.get("steps") or []):
            if st.get("source") == "agent" and st.get("message"):
                return st["message"] if isinstance(st["message"], str) else json.dumps(st["message"])
    return None


def read_reward(trial):
    p = first(os.path.join(trial, "verifier", "reward.txt"), os.path.join(trial, "reward.txt"))
    if not p:
        return None
    try:
        v = float(open(p).read().strip().split()[0])
        return v if math.isfinite(v) else None
    except (OSError, ValueError, IndexError):
        return None


def submission_dir(trial):
    for c in (os.path.join(trial, "artifacts", "app", "submission"), os.path.join(trial, "submission")):
        if os.path.isdir(c):
            return c
    hits = glob.glob(os.path.join(trial, "artifacts", "**", "submission"), recursive=True)
    return hits[0] if hits else None


def images(trial, limit=12):
    out = []
    for root in (os.path.join(trial, "artifacts"), trial):
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, files in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("node_modules", "agent", "verifier", "sessions")]
            for fn in sorted(files):
                if fn.lower().endswith(IMAGE_EXT):
                    out.append(os.path.join(dirpath, fn))
            if root == trial:
                break
        if out:
            break
    return sorted(set(out))[:limit]


def task_timeout(task_path):
    """[agent] timeout_sec from task.toml, if the task directory is readable here."""
    p = os.path.join(task_path or "", "task.toml")
    if not os.path.isfile(p):
        return None
    sec = None
    for line in open(p, errors="replace"):
        s = line.split("#")[0].strip()
        if s.startswith("["):
            sec = s
        elif sec == "[agent]" and s.startswith("timeout_sec"):
            try:
                return float(s.split("=", 1)[1])
            except ValueError:
                return None
    return None


def at_results(details):
    """{AT-n: bool} from a keyless details.json, or {} for another grader's format."""
    if not isinstance(details, dict):
        return {}
    at = details.get("at")
    if isinstance(at, dict) and at:
        return {k: bool(v) for k, v in at.items()}
    st = details.get("steps")
    if isinstance(st, dict) and any(k in st for k in STEP_NAMES):
        return {AT_STEPS[i]: bool(st.get(k)) for i, k in enumerate(STEP_NAMES)}
    return {}


def first_failed(details, at):
    d = (details or {}).get("details") if isinstance(details, dict) else None
    if isinstance(d, dict) and "first_failed" in d:
        return d["first_failed"]
    for k in AT_STEPS:
        if k in at and not at[k]:
            return k
    return None


def classify_exception(r):
    ei = (r or {}).get("exception_info") or {}
    t = ei.get("exception_type")
    excs = [t] if t else []
    for sr in (r or {}).get("step_results") or []:
        e = (sr or {}).get("exception_info") or {}
        if e.get("exception_type"):
            excs.append(e["exception_type"])
    return excs


def trial_info(trial, task_dir=None):
    """Everything the reports need about one trial, as a flat dict."""
    r = load_json(os.path.join(trial, "result.json")) or {}
    if "trial_name" not in r:
        r = {}
    job, jr, lock = job_of(trial)
    cfg = r.get("config") or {}
    ag_cfg = cfg.get("agent") or {}
    ainfo = r.get("agent_info") or {}
    minfo = ainfo.get("model_info") or {}
    agent = ag_cfg.get("name") or ainfo.get("name")
    model = ag_cfg.get("model_name") or ("%s/%s" % (minfo.get("provider"), minfo.get("name"))
                                         if minfo.get("name") else None)
    if not agent:
        agent = "codex" if first(os.path.join(trial, "codex.txt")) else (
            "opencode" if first(os.path.join(trial, "opencode.txt")) else "unknown")
    details = load_json(first(os.path.join(trial, "verifier", "details.json"),
                              os.path.join(trial, "details.json")) or "")
    vr = (r.get("verifier_result") or {}).get("rewards") or {}
    reward = read_reward(trial)
    if reward is None and isinstance(vr.get("reward"), (int, float)):
        reward = float(vr["reward"])
    if reward is None and isinstance(details, dict) and isinstance(details.get("reward"), (int, float)):
        reward = float(details["reward"])
    excs = classify_exception(r)
    if "reward_valid" in r:
        valid = bool(r["reward_valid"])
    else:
        valid = reward is not None and not any(e not in ("AgentTimeoutError",) for e in excs)
    ar = r.get("agent_result") or {}
    usage = {k: ar.get(k) for k in ("cost_usd", "n_input_tokens", "n_output_tokens", "n_cache_tokens")}
    log = agent_log(trial)
    if usage.get("cost_usd") is None and log and log.endswith("opencode.txt"):
        u = opencode_usage(log)
        if u:
            usage.update({k: u[k] for k in usage})
    at = at_results(details)
    task_path = (cfg.get("task") or {}).get("path") or ((r.get("task_id") or {}).get("path"))
    timeout = (ag_cfg.get("override_timeout_sec") or task_timeout(task_dir) or task_timeout(task_path))
    mult = cfg.get("agent_timeout_multiplier") or cfg.get("timeout_multiplier") or 1.0
    sub = submission_dir(trial)
    report = load_json(os.path.join(sub, "report.json")) if sub else None
    hon = details.get("honesty") if isinstance(details, dict) else None
    product = details.get("product") if isinstance(details, dict) else None
    if product is None and isinstance(details, dict) and isinstance(details.get("p"), (int, float)):
        product = details["p"]        # older spikes (right angle) call the product "p"
    return {
        "id": r.get("id"), "trial": trial, "trial_name": r.get("trial_name") or os.path.basename(trial),
        "task_name": r.get("task_name"), "task_checksum": r.get("task_checksum"),
        "job_dir": job, "job_name": os.path.basename(job) if job else None,
        "harbor_version": ((lock or {}).get("harbor") or {}).get("version"),
        "harbor_commit": ((lock or {}).get("harbor") or {}).get("git_commit_hash"),
        "agent": agent, "agent_version": ainfo.get("version"), "model": model,
        "agent_kwargs": ag_cfg.get("kwargs") or {},
        "group": agent if agent in ("oracle", "nop") or not model else "%s %s" % (agent, model),
        "reward": reward, "reward_valid": valid, "exceptions": excs,
        "timed_out": "AgentTimeoutError" in excs,
        "product": product, "honesty": hon,
        "honesty_detail": details.get("honesty_detail") if isinstance(details, dict) else None,
        "gates": details.get("gates") if isinstance(details, dict) else None,
        "conditions": (details.get("conditions") or details.get("checks")) if isinstance(details, dict) else None,
        "at": at, "first_failed": first_failed(details, at) if at else None,
        "grader_version": (details or {}).get("grader_version") if isinstance(details, dict) else None,
        "grader_seconds": (details or {}).get("seconds") if isinstance(details, dict) else None,
        "details": details, "report": report if isinstance(report, dict) else None,
        "submission": sub,
        "cost_usd": usage.get("cost_usd"), "n_input_tokens": usage.get("n_input_tokens"),
        "n_output_tokens": usage.get("n_output_tokens"), "n_cache_tokens": usage.get("n_cache_tokens"),
        "agent_seconds": span(r.get("agent_execution")), "trial_seconds": span(r),
        "verifier_seconds": span(r.get("verifier")),
        "agent_timeout_sec": (timeout * float(mult)) if timeout else None,
        "agent_log": log,
        "trajectory": first(os.path.join(trial, "agent", "trajectory.json")),
        "grade_log": first(os.path.join(trial, "verifier", "grade.log"), os.path.join(trial, "grade.log")),
        "details_path": first(os.path.join(trial, "verifier", "details.json"), os.path.join(trial, "details.json")),
        "report_path": first(os.path.join(sub, "report.json")) if sub else None,
        "started_at": r.get("started_at"),
    }


def load_trials(paths, task_dir=None):
    """trial_info for every trial under paths, each Harbor trial once (a collected copy of a trial that is
    also given as a job dir has the same result.json id; the first one found is kept)."""
    seen, out = set(), []
    for p in find_trials(paths):
        t = trial_info(p, task_dir)
        if t["id"] and t["id"] in seen:
            continue
        seen.add(t["id"])
        out.append(t)
    return out
