"""Write one incident record per trial with a failed acceptance step (ISO/IEC/IEEE 29119-3 style).

    python -I incidents.py JOB_OR_JOBS_DIR [MORE ...] [--out INCIDENTS.md] [--last 8]

A record has: an ID; the trial; the step it concerns (the FIRST failed AT step, since later steps do not
count towards the product; other failed steps are listed too); expected vs actual (expected from
spikes/keyless/constants.py when it is importable, actual from the measured values in details.json);
the agent's own claim for that step (report.json); evidence pointers (the last tool calls before the end,
as log-file:line, plus the grader log); and blank fields for a human: root cause (the agent's decision
behind the failure, quoted), classification (agent fault / grader fault / spec ambiguity), and
"confirmed by". Nothing here decides a root cause: the template is filled by reading the trajectory.

Graders without AT steps (older spikes) get a record for each failed check in details.json instead.
Also writes incidents.json with the same records.
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import harbor_io as H  # noqa: E402


def load_constants():
    p = os.path.join(os.path.dirname(HERE), "constants.py")
    try:
        spec = importlib.util.spec_from_file_location("keyless_constants", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    except Exception:  # noqa: BLE001  (constants.py missing or mid-edit: fall back to words)
        return None


def expected(C):
    g = (lambda name, default=None: getattr(C, name, default)) if C else (lambda name, default=None: default)

    def v(name, fmt="%g"):
        x = g(name)
        return (fmt % x) if isinstance(x, (int, float)) else "(see constants.py: %s)" % name
    band = g("WIND_BAND")
    band = "%g to %g" % tuple(band) if band else "(WIND_BAND)"
    return {
        "AT-0": "Files load (keyless.json, closed-manifold STLs); no pair overlaps more than the tolerance at rest; "
                "every free or sprung part is held (a %s mm shift hits something); everything inside the case "
                "and the stem protrudes at least %s mm." % (v("HOLD_SHIFT"), v("STEM_PROTRUDE")),
        "AT-1": "Position 1, crown turned forward %s turn(s): not blocked, %s crown turns per barrel-arbor turn, "
                "minute wheel still (|Δ| ≤ %s°)." % (v("WIND_TURNS"), band, v("STILL_TOL")),
        "AT-2": "Crown let go for %s steps with a tap every %s: the arbor runs back at most %s°."
                % (v("HOLD_STEPS"), v("TAP_EVERY"), v("CLICK_RUNBACK")),
        "AT-3": "Power reserve from full wind (%s turns × %s h, less the run-back) at least %s h, and the arbor "
                "turns forward %s° by itself without being dragged or locked (free_run_blocked = 0)."
                % (v("CAPACITY_TURNS"), v("BARREL_HOURS_PER_TURN"), v("RESERVE_MIN"), v("FREE_RUN_DEG")),
        "AT-4": "Crown turned backward one turn: not blocked, arbor loses at most %s°, minute wheel still."
                % v("HOLD_TOL"),
        "AT-5": "Pull to position 2 in %s stops, clean mode at each (wind at the start, set at the end, never "
                "both, never jammed); then ±%s° sets the minute wheel at least %s° each way, arbor loses ≤ %s°."
                % (v("SWEEP_SAMPLES"), v("SET_TURN"), v("SET_MIN"), v("HOLD_TOL")),
        "AT-6": "Push back in through %s stops, clean at each; then a %s° forward turn winds the barrel again "
                "(more than %s°)." % (v("SWEEP_SAMPLES"), v("REWIND_TURN"), v("STILL_TOL")),
    }


def actual(t, step):
    d = t["details"] if isinstance(t["details"], dict) else {}
    det = d.get("details") if isinstance(d.get("details"), dict) else {}
    if step == "AT-0":
        keep = {k: det.get(k) for k in ("files", "rest", "rest_overlap", "bounds", "held") if k in det}
        return {"gates": d.get("gates"), "conditions": d.get("conditions"), **keep}
    name = H.STEP_NAMES[H.AT_STEPS.index(step)] if step in H.AT_STEPS else step
    seq = det.get("sequence") if isinstance(det.get("sequence"), dict) else {}
    out = dict(seq.get(name) or {})
    for k in ("samples",):                   # long sample lists: keep the count and the first bad one
        if isinstance(out.get(k), list):
            out[k] = "%d samples (see details.json)" % len(out[k])
    if not out and det.get("sequence_error"):
        out = {"sequence_error": det["sequence_error"]}
    return out or {"note": "no measured values for this step in details.json (earlier failure stopped it?)"}


def records(t, last, C, exp):
    """One record for a keyless trial (first failed AT step); one per failed check for other graders."""
    recs = []
    calls = H.tool_calls(t["trial"], last=last)
    ev = ["%s:%d  %s  %s" % (os.path.basename(p), ln, tool, txt) for p, ln, tool, txt in calls]
    msg = H.final_message(t["trial"])
    base = {"trial": t["trial_name"], "trial_dir": t["trial"], "group": t["group"], "reward": t["reward"],
            "product": t["product"], "honesty": t["honesty"], "valid": t["reward_valid"],
            "exceptions": t["exceptions"], "agent_log": t["agent_log"], "trajectory": t["trajectory"],
            "grade_log": t["grade_log"], "details_path": t["details_path"], "last_tool_calls": ev,
            "final_message_excerpt": (msg or "")[:600] or None,
            "root_cause_decision": "", "classification": "", "confirmed_by": ""}
    if t["at"]:
        step = t["first_failed"]
        if not step:
            return recs
        name = H.STEP_NAMES[H.AT_STEPS.index(step)] if step in H.AT_STEPS else step
        claim = ((t["report"] or {}).get("steps") or {}).get(name) if isinstance(t["report"], dict) else None
        recs.append({**base, "id": "INC-%s-%s" % (t["trial_name"], step), "step": step,
                     "also_failed": [s for s in H.AT_STEPS if s in t["at"] and not t["at"][s] and s != step],
                     "expected": exp.get(step, ""), "actual": actual(t, step),
                     "agent_claim": claim})
        return recs
    checks = t["conditions"] or {}
    failed = [k for k, v in list((t["gates"] or {}).items()) + list(checks.items()) if v is False]
    if failed:                                    # one record per trial, on the first failed check
        k = failed[0]
        sub = (t["details"] or {}).get("details") if isinstance(t["details"], dict) else None
        recs.append({**base, "id": "INC-%s-%s" % (t["trial_name"], k), "step": k, "also_failed": failed[1:],
                     "expected": "check `%s` passes (see the spike's grader)" % k,
                     "actual": sub.get(k) if isinstance(sub, dict) else None,
                     "agent_claim": None})
    return recs


def md(recs, sources):
    L = ["# Incident records", "",
         "Generated by `spikes/keyless/report/incidents.py` from " + ", ".join("`%s`" % s for s in sources) + ". "
         "Format after ISO/IEC/IEEE 29119-3:2021 *incident report* (IEEE 829's *test incident report*): one "
         "record per trial, on the first failed acceptance step. The three fields at the end are for a human "
         "who has read the trajectory; until they are filled the record is **unconfirmed**.", "",
         "Records: %d." % len(recs), ""]
    for r in recs:
        aid = "inc-" + "".join(c.lower() if c.isalnum() else "-" for c in r["trial"])
        L += ['<a id="%s"></a>' % aid, "", "## %s" % r["id"], "",
              "| Field | Value |", "|---|---|",
              "| Trial | `%s` (%s) |" % (r["trial"], r["group"]),
              "| Step | **%s**%s |" % (r["step"], ("; also failed: " + ", ".join(r["also_failed"])) if r["also_failed"] else ""),
              "| Reward / product / honesty | %s / %s / %s |" % tuple(
                  "–" if x is None else "%.3f" % x for x in (r["reward"], r["product"], r["honesty"])),
              "| Reward valid | %s%s |" % ("yes" if r["valid"] else "**no**",
                                          ("; exceptions: " + ", ".join(r["exceptions"])) if r["exceptions"] else ""),
              "| Expected | %s |" % r["expected"].replace("|", "\\|"),
              "| Actual | `%s` |" % json.dumps(r["actual"], default=str).replace("|", "\\|")[:1200],
              "| Agent's claim (report.json) | %s |" % (r["agent_claim"] or "–"),
              "| Agent log | `%s` |" % (r["agent_log"] or "missing"),
              "| Trajectory | `%s` |" % (r["trajectory"] or "missing"),
              "| Score breakdown | `%s` |" % (r["details_path"] or "missing"),
              "| Grader log | `%s` |" % (r["grade_log"] or "missing"),
              "", "Last tool calls before the end (log file:line, tool, input):", "", "```"]
        L += r["last_tool_calls"] or ["(no tool calls found in the agent log)"]
        L += ["```", ""]
        if r["final_message_excerpt"]:
            L += ["Agent's final message (excerpt):", ""] + ["> " + x for x in r["final_message_excerpt"].splitlines()] + [""]
        L += ["- **Root cause (the agent's decision behind it, quoted from the trajectory):** ",
              "- **Classification (agent fault / grader fault / spec ambiguity):** ",
              "- **Confirmed by (name, date):** ", ""]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out", default="INCIDENTS.md")
    ap.add_argument("--last", type=int, default=8, help="tool calls to quote before the end of each run")
    ap.add_argument("--include-reference", action="store_true", help="also record oracle and nop failures")
    a = ap.parse_args(argv)
    C = load_constants()
    exp = expected(C)
    recs = []
    for t in H.load_trials(a.paths):
        if t["group"] in ("oracle", "nop") and not a.include_reference:
            continue
        recs.extend(records(t, a.last, C, exp))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w").write(md(recs, a.paths))
    jpath = os.path.splitext(a.out)[0] + ".json"
    json.dump(recs, open(jpath, "w"), indent=1, default=str)
    print("wrote", a.out, "and", jpath, "with", len(recs), "records", "" if C else "(constants.py not found)")


if __name__ == "__main__":
    main()
