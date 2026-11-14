"""Summarise Harbor runs of the keyless task: RESULTS.md and results.json, one row per model.

    python -I summarize.py JOB_OR_JOBS_DIR [MORE ...] [--out DIR] [--threshold 1.0] [--k 1,3]
                           [--task TASK_DIR] [--label GROUP=NAME ...]

For every trial it reads the reward (verifier/reward.txt), details.json (product, honesty, AT-0..AT-6,
gates, conditions), the agent's /app/submission/report.json (collected as an artifact), and cost, tokens
and times from result.json (falling back to OpenCode's step_finish events). Trials are grouped by agent
and model (oracle and nop are their own groups).

Statistics, per group, over the trials whose reward Harbor marks valid (`reward_valid`; API and
rate-limit errors are excluded from the mean, as Harbor itself does; agent timeouts are graded and count):
  - mean, 95 % CI (Student t on the trial rewards), sd, min, max of reward, product and honesty;
  - a trial passes when reward >= THRESHOLD (default 1.0: full acceptance and a fully honest report);
  - pass@k = 1 - C(n-c, k) / C(n, k), the unbiased estimator of Chen et al. 2021, "Evaluating Large
    Language Models Trained on Code", arXiv:2107.03374, section 2.1 (n trials, c passing);
  - pass^k = C(c, k) / C(n, k), the probability that k trials drawn without replacement all pass
    (Yao et al. 2024, tau-bench, arXiv:2406.12045; Anthropic, "Demystifying evals for AI agents");
  - pass@1 also gets a Wilson 95 % interval;
  - AT-0..AT-6: trials passing each step, and how many trials first failed at each step.
Standard library only; never imports the grader. Missing fields are reported as missing, not as zero.
"""
import argparse
import json
import math
import os
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harbor_io as H  # noqa: E402

T95 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.160, 2.145,
       2.131, 2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048,
       2.045, 2.042]


def stats(xs):
    xs = [float(x) for x in xs if isinstance(x, (int, float)) and math.isfinite(x)]
    n = len(xs)
    if not n:
        return {"n": 0, "mean": None, "ci95": None, "sd": None, "min": None, "max": None}
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    h = (T95[n - 2] if n - 1 <= len(T95) else 1.96) * sd / math.sqrt(n) if n > 1 else None
    return {"n": n, "mean": m, "ci95": [max(0.0, m - h), min(1.0, m + h)] if h is not None else None,
            "sd": sd, "min": min(xs), "max": max(xs)}


def pass_at_k(n, c, k):
    """Chen et al. 2021 unbiased estimator."""
    if k > n:
        return None
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def pass_hat_k(n, c, k):
    if k > n:
        return None
    return math.comb(c, k) / math.comb(n, k)


def wilson(c, n, z=1.96):
    if not n:
        return None
    p = c / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, centre - h), min(1.0, centre + h)]


def summarise_group(trials, threshold, ks):
    valid = [t for t in trials if t["reward_valid"] and t["reward"] is not None]
    n = len(valid)
    c = sum(1 for t in valid if t["reward"] >= threshold - 1e-9)
    out = OrderedDict()
    out["n_trials"] = len(trials)
    out["n_valid"] = n
    out["reward"] = stats([t["reward"] for t in valid])
    out["product"] = stats([t["product"] for t in valid])
    out["honesty"] = stats([t["honesty"] for t in valid])
    out["pass_threshold"] = threshold
    out["n_pass"] = c
    out["pass_at_k"] = {str(k): pass_at_k(n, c, k) for k in sorted(set(ks + [n])) if 1 <= k <= n}
    out["pass_hat_k"] = {str(k): pass_hat_k(n, c, k) for k in sorted(set(ks + [n])) if 1 <= k <= n}
    out["pass_at_1_wilson95"] = wilson(c, n)
    with_at = [t for t in valid if t["at"]]
    out["at_n"] = len(with_at)
    out["at_pass"] = {s: sum(1 for t in with_at if t["at"].get(s)) for s in H.AT_STEPS}
    ff = Counter(t["first_failed"] or "none (all passed)" for t in with_at)
    out["first_failed"] = {s: ff.get(s, 0) for s in list(H.AT_STEPS) + ["none (all passed)"]}
    gates, conds = Counter(), Counter()
    for t in valid:
        for k, v in (t["gates"] or {}).items():
            gates[k] += bool(v)
        for k, v in (t["conditions"] or {}).items():
            conds[k] += bool(v) if not isinstance(v, dict) else bool(v.get("ok"))
    out["gates_pass"], out["conditions_pass"] = dict(gates), dict(conds)
    costs = [t["cost_usd"] for t in trials if isinstance(t["cost_usd"], (int, float))]
    out["cost_usd_mean"] = sum(costs) / len(costs) if costs else None
    out["cost_usd_total"] = sum(costs) if costs else None
    for key in ("n_input_tokens", "n_output_tokens", "n_cache_tokens"):
        v = [t[key] for t in trials if isinstance(t[key], (int, float))]
        out[key + "_mean"] = sum(v) / len(v) if v else None
    at = [t["agent_seconds"] for t in trials if t["agent_seconds"] is not None]
    out["agent_seconds_mean"] = sum(at) / len(at) if at else None
    out["agent_seconds_max"] = max(at) if at else None
    tos = [t["agent_timeout_sec"] for t in trials if t["agent_timeout_sec"]]
    out["agent_timeout_sec"] = max(tos) if tos else None
    out["agent_max_share_of_timeout"] = (out["agent_seconds_max"] / out["agent_timeout_sec"]
                                         if at and tos else None)
    vs = [t["verifier_seconds"] for t in trials if t["verifier_seconds"] is not None]
    out["verifier_seconds_max"] = max(vs) if vs else None
    out["n_timeouts"] = sum(1 for t in trials if t["timed_out"])
    out["n_invalid"] = sum(1 for t in trials if not t["reward_valid"])
    out["exceptions"] = dict(Counter(e for t in trials for e in t["exceptions"]))
    rep = [t for t in valid if t["report"] is not None]
    out["n_with_report_json"] = len(rep)
    out["harness"] = sorted({"%s %s" % (t["agent"], t["agent_version"] or "?") for t in trials})
    out["models"] = sorted({t["model"] or "-" for t in trials})
    out["agent_kwargs"] = sorted({json.dumps(t["agent_kwargs"], sort_keys=True) for t in trials})
    out["harbor"] = sorted({"%s (%s)" % (t["harbor_version"] or "?", (t["harbor_commit"] or "?")[:8])
                            for t in trials})
    out["grader_versions"] = sorted({t["grader_version"] or "-" for t in trials})
    out["task_names"] = sorted({t["task_name"] or "-" for t in trials})
    out["task_checksums"] = sorted({(t["task_checksum"] or "-")[:12] for t in trials})
    out["jobs"] = sorted({t["job_name"] or os.path.basename(os.path.dirname(t["trial"])) for t in trials})
    out["trials"] = [{"trial": t["trial_name"], "reward": t["reward"], "product": t["product"],
                      "honesty": t["honesty"], "first_failed": t["first_failed"], "valid": t["reward_valid"],
                      "exceptions": t["exceptions"], "cost_usd": t["cost_usd"],
                      "agent_seconds": t["agent_seconds"]} for t in trials]
    return out


def f(x, nd=3):
    if x is None:
        return "–"
    if isinstance(x, float):
        return ("%." + str(nd) + "f") % x
    return str(x)


def ci(s):
    return "[%s, %s]" % (f(s["ci95"][0]), f(s["ci95"][1])) if s.get("ci95") else "–"


def mins(s):
    return "–" if s is None else "%.1f" % (s / 60.0)


def write_md(groups, path, threshold, sources):
    L = ["# Keyless works: results", "",
         "Generated by `spikes/keyless/report/summarize.py` from: " + ", ".join("`%s`" % s for s in sources) + ".",
         "", "Reward = product × (0.75 + 0.10 × honesty) / 0.85, written by the verifier. A trial **passes** "
         "when reward ≥ %g. Statistics use the trials whose reward Harbor marks valid (`reward_valid`)." % threshold,
         "pass@k is the unbiased estimator of Chen et al. 2021 (arXiv:2107.03374): 1 − C(n−c,k)/C(n,k). "
         "pass^k = C(c,k)/C(n,k), the chance that k trials all pass (tau-bench, arXiv:2406.12045).", "",
         "## Headline", "",
         "| Group | n valid / trials | Reward mean | 95 % CI | sd | min–max | Product mean | Honesty mean "
         "| pass@1 (Wilson 95 %) | pass@n | pass^n | Cost mean ($) | Agent time mean / max (min) | Timeouts | Invalid |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for g, s in groups.items():
        n = s["n_valid"]
        p1 = s["pass_at_k"].get("1")
        w = s["pass_at_1_wilson95"]
        L.append("| %s | %d / %d | %s | %s | %s | %s–%s | %s | %s | %s %s | %s | %s | %s | %s / %s | %d | %d |" % (
            g, n, s["n_trials"], f(s["reward"]["mean"]), ci(s["reward"]), f(s["reward"]["sd"]),
            f(s["reward"]["min"]), f(s["reward"]["max"]), f(s["product"]["mean"]), f(s["honesty"]["mean"]),
            f(p1), "[%s, %s]" % (f(w[0], 2), f(w[1], 2)) if w else "", f(s["pass_at_k"].get(str(n))),
            f(s["pass_hat_k"].get(str(n))), f(s["cost_usd_mean"], 2), mins(s["agent_seconds_mean"]),
            mins(s["agent_seconds_max"]), s["n_timeouts"], s["n_invalid"]))
    L += ["", "## pass@k and pass^k", "", "| Group | k | pass@k | pass^k |", "|---|---|---|---|"]
    for g, s in groups.items():
        for k in s["pass_at_k"]:
            L.append("| %s | %s | %s | %s |" % (g, k, f(s["pass_at_k"][k]), f(s["pass_hat_k"][k])))
    L += ["", "## Acceptance steps", "",
          "Trials passing each step (a step counts in the product only if every earlier step passed), then "
          "how many trials **first** failed at each step.", "",
          "| Group | n with AT | " + " | ".join(H.AT_STEPS) + " | first failed: " +
          " / ".join(H.AT_STEPS) + " / none |", "|---|---|" + "---|" * (len(H.AT_STEPS) + 1)]
    for g, s in groups.items():
        if not s["at_n"]:
            L.append("| %s | 0 | " % g + " | ".join("–" for _ in H.AT_STEPS) + " | (no AT results in details.json) |")
            continue
        L.append("| %s | %d | %s | %s |" % (g, s["at_n"], " | ".join(str(s["at_pass"][k]) for k in H.AT_STEPS),
                                            " / ".join(str(v) for v in s["first_failed"].values())))
    L += ["", "## Gates and conditions (trials passing)", "", "| Group | Gates | Conditions |", "|---|---|---|"]
    for g, s in groups.items():
        L.append("| %s | %s | %s |" % (g, ", ".join("%s %d" % kv for kv in s["gates_pass"].items()) or "–",
                                       ", ".join("%s %d" % kv for kv in s["conditions_pass"].items()) or "–"))
    L += ["", "## Cost, time and errors", "",
          "| Group | Cost total ($) | Tokens in / cached / out (mean) | Agent max (min) | Timeout (min) | "
          "Max share of timeout | Verifier max (min) | Exceptions | report.json present |",
          "|---|---|---|---|---|---|---|---|---|"]
    for g, s in groups.items():
        L.append("| %s | %s | %s / %s / %s | %s | %s | %s | %s | %s | %d of %d |" % (
            g, f(s["cost_usd_total"], 2), f(s["n_input_tokens_mean"], 0), f(s["n_cache_tokens_mean"], 0),
            f(s["n_output_tokens_mean"], 0), mins(s["agent_seconds_max"]), mins(s["agent_timeout_sec"]),
            f(s["agent_max_share_of_timeout"], 2), mins(s["verifier_seconds_max"]),
            ", ".join("%s ×%d" % kv for kv in s["exceptions"].items()) or "none",
            s["n_with_report_json"], s["n_valid"]))
    L += ["", "## Harness and versions", "",
          "| Group | Harness | Model | Agent options | Harbor | Grader | Task | Task checksum | Jobs |",
          "|---|---|---|---|---|---|---|---|---|"]
    for g, s in groups.items():
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            g, ", ".join(s["harness"]), ", ".join(s["models"]),
            ", ".join("`%s`" % a for a in s["agent_kwargs"]), ", ".join(s["harbor"]),
            ", ".join(s["grader_versions"]), ", ".join(s["task_names"]), ", ".join(s["task_checksums"]),
            ", ".join(s["jobs"])))
    L += ["", "## Per trial", "", "| Group | Trial | Reward | Product | Honesty | First failed | Valid | "
          "Exceptions | Cost ($) | Agent (min) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for g, s in groups.items():
        for t in s["trials"]:
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                g, t["trial"], f(t["reward"]), f(t["product"]), f(t["honesty"]), t["first_failed"] or "–",
                "yes" if t["valid"] else "**no**", ", ".join(t["exceptions"]) or "–", f(t["cost_usd"], 2),
                mins(t["agent_seconds"])))
    open(path, "w").write("\n".join(L) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", help="Harbor job dirs, folders of jobs, or collected run dirs")
    ap.add_argument("--out", default=".", help="folder for RESULTS.md and results.json")
    ap.add_argument("--threshold", type=float, default=1.0, help="reward at or above which a trial passes")
    ap.add_argument("--k", default="1", help="comma-separated k values for pass@k and pass^k (n is always added)")
    ap.add_argument("--task", help="task dir, to read [agent] timeout_sec when the job's task path is gone")
    ap.add_argument("--label", action="append", default=[], help="rename a group: 'opencode anthropic/x=Sonnet'")
    a = ap.parse_args(argv)
    ks = [int(k) for k in a.k.split(",") if k.strip()]
    trials = H.load_trials(a.paths, a.task)
    if not trials:
        sys.exit("no Harbor trials found under: " + ", ".join(a.paths))
    rename = dict(x.split("=", 1) for x in a.label if "=" in x)
    if len({t["task_name"] for t in trials}) > 1:          # several tasks in the inputs: never pool them
        for t in trials:
            t["group"] = "%s · %s" % (t["task_name"] or "?", t["group"])
    order = {"oracle": 0, "nop": 1}
    by = OrderedDict()
    for t in sorted(trials, key=lambda t: (order.get(t["group"], 2), t["group"], t["started_at"] or "")):
        by.setdefault(rename.get(t["group"], t["group"]), []).append(t)
    groups = OrderedDict((g, summarise_group(ts, a.threshold, ks)) for g, ts in by.items())
    os.makedirs(a.out, exist_ok=True)
    json.dump({"generator": "spikes/keyless/report/summarize.py", "sources": a.paths, "threshold": a.threshold,
               "estimators": {"pass@k": "Chen et al. 2021, arXiv:2107.03374: 1 - C(n-c,k)/C(n,k)",
                              "pass^k": "C(c,k)/C(n,k) (tau-bench, arXiv:2406.12045)",
                              "ci95": "Student t on trial rewards; Wilson for pass@1"},
               "groups": groups}, open(os.path.join(a.out, "results.json"), "w"), indent=1, default=str)
    write_md(groups, os.path.join(a.out, "RESULTS.md"), a.threshold, a.paths)
    for g, s in groups.items():
        print("%-45s n=%d/%d reward=%s pass@1=%s cost=%s" % (g, s["n_valid"], s["n_trials"], f(s["reward"]["mean"]),
                                                            f(s["pass_at_k"].get("1")), f(s["cost_usd_mean"], 2)))
    print("wrote", os.path.join(a.out, "RESULTS.md"), "and results.json")


if __name__ == "__main__":
    main()
