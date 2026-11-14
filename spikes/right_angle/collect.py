"""Copy the small, reviewable parts of Harbor trials into the repo.

    python collect.py JOB_DIR OUT_DIR LABEL

Per trial: reward, grader details, winding.json, the agent's final message, the list of shell
commands it ran, and token/cost totals. The STL parts are not copied (megabytes each); their
names and triangle counts are listed instead. Refuses to write anything containing "sk-ant-".
"""
import glob
import gzip
import json
import os
import shutil
import sys


def final_and_commands(agent_dir):
    msgs, cmds, usage = [], [], {}
    cx = os.path.join(agent_dir, "codex.txt")
    oc = os.path.join(agent_dir, "opencode.txt")
    if os.path.exists(cx):
        for line in open(cx, errors="replace"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            it = e.get("item") or {}
            if it.get("type") == "agent_message" and e.get("type") == "item.completed":
                msgs.append(it.get("text", ""))
            if it.get("type") == "command_execution" and e.get("type") == "item.started":
                cmds.append(it.get("command", ""))
            if e.get("type") == "turn.completed":
                usage = e.get("usage", {})
    if os.path.exists(oc):
        cost, tok = 0.0, 0
        for line in open(oc, errors="replace"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            p = e.get("part") or {}
            if e.get("type") == "text" and p.get("text"):
                msgs.append(p["text"])
            if e.get("type") == "tool_use":
                st = p.get("state") or {}
                inp = st.get("input") or {}
                cmds.append("%s %s" % (p.get("tool"), json.dumps(inp)[:2000]))
            if e.get("type") == "step_finish":
                cost += float(p.get("cost") or 0)
                tok += int((p.get("tokens") or {}).get("total") or 0)
        usage = {"cost_usd": round(cost, 4), "tokens_total": tok}
    return (msgs[-1] if msgs else ""), cmds, usage


def main(job, out, label):
    for trial in sorted(glob.glob(os.path.join(job, "*", "*", ""))):
        if not os.path.isdir(os.path.join(trial, "agent")):
            continue
        name = os.path.basename(os.path.normpath(trial))
        d = os.path.join(out, label + "__" + name)
        os.makedirs(d, exist_ok=True)
        res = json.load(open(os.path.join(trial, "result.json")))
        ae = res.get("agent_execution") or {}
        rw = os.path.join(trial, "verifier", "reward.txt")
        final, cmds, usage = final_and_commands(os.path.join(trial, "agent"))
        sub = os.path.join(trial, "artifacts", "app", "submission")
        parts = {}
        if os.path.isdir(os.path.join(sub, "parts")):
            for f in sorted(os.listdir(os.path.join(sub, "parts"))):
                parts[f] = os.path.getsize(os.path.join(sub, "parts", f))
        summary = {"label": label, "trial": name, "reward": open(rw).read().strip() if os.path.exists(rw) else None,
                   "agent_started": ae.get("started_at"), "agent_finished": ae.get("finished_at"),
                   "usage": usage, "parts_bytes": parts, "commands": len(cmds)}
        blobs = {
            "summary.json": json.dumps(summary, indent=1),
            "final_message.md": final,
            "commands.txt": "\n\n---\n\n".join(cmds),
        }
        det = os.path.join(trial, "verifier", "details.json")
        if os.path.exists(det):
            blobs["details.json"] = open(det).read()
        if os.path.exists(os.path.join(sub, "winding.json")):
            blobs["winding.json"] = open(os.path.join(sub, "winding.json")).read()
        for fn, text in blobs.items():
            if "sk-ant-" in text:
                raise SystemExit("refusing: key-like string in %s/%s" % (name, fn))
            open(os.path.join(d, fn), "w").write(text)
        scripts = os.path.join(sub, "..", "scripts")
        if os.path.isdir(scripts):
            for f in glob.glob(os.path.join(scripts, "*.py")):
                t = open(f, errors="replace").read()
                if "sk-ant-" not in t:
                    os.makedirs(os.path.join(d, "scripts"), exist_ok=True)
                    shutil.copyfile(f, os.path.join(d, "scripts", os.path.basename(f)))
        print(name, summary["reward"], usage)


if __name__ == "__main__":
    main(*sys.argv[1:4])
