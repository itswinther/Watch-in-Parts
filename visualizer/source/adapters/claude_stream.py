"""Adapter: Claude Code stream-json transcript (claude -p --output-format stream-json).

Turns one transcript.jsonl into short log lines with plain rules, no AI calls.
Every line keeps `src` = the 1-based line number in the transcript it came from.

Line kinds:
  read    the AI read a file or listed a folder
  write   the AI wrote or edited a file
  run     the AI ran a script or snippet
  check   the AI ran one of its own checks (a script whose name says check/verify/test/debug,
          or a diff/cmp between folders)
  result  the last lines a check printed (tool output, verbatim)
  error   a command failed; the last line of its output, verbatim
  harness a message from Claude Code itself (a blocked or timed-out tool call), not the AI
  wait    the AI waited for a background job
  submit  the AI called the submit tool, or the submit tool replied
  say     something the AI wrote to the user, quoted (shortened, never reworded)
  think   a thinking summary the transcript shows, quoted
  done    the AI's final message: the moment it says it is done
"""
import datetime
import json
import os
import re

from .common import quote

HARNESS = re.compile(r"(tool_use_error|no such tool available|did not complete within its|schema was not sent|"
                     r"can't be checked before it runs|moved to the background|permission)", re.I)
CHECK_NAME = re.compile(r"(check|verify|valid|test|dbg|debug|probe)", re.I)


def _ts(s):
    try:
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def _result_text(block):
    c = block.get("content")
    if isinstance(c, list):
        c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
    return c or ""


def _last_lines(text, n=1, limit=160):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    lines = [l for l in lines if re.search(r"[A-Za-z0-9]", l) and not l.startswith("[exited with code") and not l.startswith("real")
             and not l.startswith("user\t") and not l.startswith("sys\t")]
    return [quote(l, limit) for l in lines[-n:]]


def _files_in(cmd, exts=(".md", ".py", ".json", ".txt", ".step", ".png", ".log")):
    found = []
    for tok in re.findall(r"[\w./<>-]+", cmd):
        if tok.endswith(exts) and tok not in found and not tok.startswith("-"):
            found.append(tok)
    return found


def describe_bash(cmd, background=False):
    """Plain-language lines for one shell command. Returns [(kind, text)]."""
    out = []
    # heredoc bodies hold code, not commands; look only at the command lines around them
    shell = re.sub(r"<<\s*'?(\w+)'?\n.*?\n\1(\n|$)", "<<HEREDOC\n", cmd, flags=re.S)

    for path in re.findall(r"cat\s*>\s*(\S+)\s*<<", shell):
        out.append(("write", f"Writes {path}"))
    for m in re.finditer(r"python3?\s+-\s*<<", shell):
        edited = (re.findall(r"open\(['\"]([^'\"]+)['\"]\s*,\s*['\"]w['\"]", cmd)
                  or re.findall(r"open\(['\"]([^'\"]+)['\"]\)\.read\(\)", cmd))
        writes_back = re.search(r"open\([^)]*['\"]w['\"]\)", cmd) or ".write(" in cmd
        if edited and (".replace(" in cmd or writes_back):
            out.append(("write", f"Edits {edited[0]}"))
        else:
            out.append(("run", "Runs a Python snippet"))
    for path in re.findall(r"sed\s+-i\S*\s+(?:'[^']*'|\"[^\"]*\")\s+(\S+)", shell):
        out.append(("write", f"Edits {path.rstrip(';&|')}"))
    if re.search(r"(python3?\s+|\./)(\S*/)?submit\.py", shell):
        out.append(("submit", "Calls the submit tool"))
    for script in re.findall(r"python3?\s+(?:-\w+\s+)*([\w./-]+\.py)", shell):
        if "submit.py" in script:
            continue
        base = os.path.basename(script)
        if CHECK_NAME.search(base):
            out.append(("check", f"Runs its own check {script}"))
        else:
            out.append(("run", f"Runs {script}"))
    if re.search(r"(^|[;&|\s])(diff|cmp)\s", shell):
        args = [a for a in re.findall(r"(?:diff|cmp)\s+(?:-\w+\s+)*(\S+)\s+(\S+)", shell)]
        if args:
            out.append(("check", f"Compares {args[0][0]} with {args[0][1]}"))
    if re.search(r"(^|[;&|\s])(sleep|until)\s", shell):
        out.append(("wait", "Waits for a background job"))
    if not out and re.search(r"\.output\b", shell):
        out.append(("wait", "Reads the output of its background job"))
    if not out:
        files = _files_in(shell)
        if re.search(r"(^|[;&|\s])(cat|sed|head|tail|grep|less|wc)\s", shell) and files:
            shown = ", ".join(files[:3]) + (" …" if len(files) > 3 else "")
            out.append(("read", f"Reads {shown}"))
        elif re.search(r"(^|[;&|\s])ls\b", shell):
            out.append(("read", "Lists the files"))
        else:
            first = shell.strip().splitlines()[0] if shell.strip() else cmd
            out.append(("run", "Runs `" + quote(first, 70) + "`"))
    if background:
        out = [(k, t + " (in the background)") if k in ("run", "check") else (k, t) for k, t in out]
    # one line per distinct text, in order
    seen, uniq = set(), []
    for k, t in out:
        if t not in seen:
            seen.add(t)
            uniq.append((k, t))
    return uniq


def parse(transcript_path, src_name):
    """Return (lines, info) for one transcript."""
    events = []
    with open(transcript_path) as f:
        for i, raw in enumerate(f, start=1):
            raw = raw.strip()
            if raw:
                try:
                    events.append((i, json.loads(raw)))
                except json.JSONDecodeError:
                    pass

    t0 = None
    for _, e in events:
        if e.get("timestamp"):
            t0 = _ts(e["timestamp"])
            break

    lines = []
    tool_kind = {}   # tool_use_id -> kinds produced
    last_t = 0.0

    def add(kind, text, src, t, **extra):
        lines.append({"t": t, "kind": kind, "text": text,
                      "src": {"file": src_name, "line": src}, **extra})

    for i, e in events:
        t = None
        if e.get("timestamp") and t0 is not None:
            t = round(_ts(e["timestamp"]) - t0, 1)
            last_t = t
        t = last_t if t is None else t
        typ = e.get("type")

        if typ == "assistant":
            for b in e["message"].get("content", []):
                bt = b.get("type")
                if bt == "text" and b.get("text", "").strip():
                    add("say", quote(b["text"]), i, t)
                elif bt == "thinking" and b.get("thinking", "").strip():
                    add("think", quote(b["thinking"]), i, t)
                elif bt == "tool_use":
                    name, inp = b.get("name"), b.get("input", {})
                    if name.lower() == "bash":
                        descr = describe_bash(inp.get("command", ""), inp.get("run_in_background", False))
                    elif name == "Read":
                        p = inp.get("file_path", "")
                        verb = "Looks at the picture" if p.lower().endswith((".png", ".jpg")) else "Reads"
                        descr = [("read", f"{verb} {p}")]
                    elif name in ("Write", "Edit"):
                        descr = [("write", f"{'Writes' if name == 'Write' else 'Edits'} {inp.get('file_path', '')}")]
                    elif name == "Monitor":
                        descr = [("wait", "Waits for a background job")]
                    else:
                        descr = [("run", f"Uses the {name} tool")]
                    for k, txt in descr:
                        add(k, txt, i, t, tool_use_id=b.get("id"))
                    tool_kind[b.get("id")] = {k for k, _ in descr}

        elif typ == "user":
            content = e["message"].get("content")
            if not isinstance(content, list):
                continue
            for b in content:
                if b.get("type") != "tool_result":
                    continue
                text = _result_text(b)
                kinds = tool_kind.get(b.get("tool_use_id"), set())
                low = text.lower()
                if '"result": "accepted"' in text or '"result":"accepted"' in text:
                    m = re.search(r"\{[^{}]*\"result\":\s*\"accepted\"[^{}]*\}", text)
                    add("submit", "Submit tool: " + quote(m.group(0) if m else "accepted", 160), i, t)
                elif HARNESS.search((text.strip().splitlines() or [""])[0]) or text.lstrip().startswith(("<tool_use_error>", "Error: No such tool")):
                    first = re.sub(r"</?tool_use_error>", "", text).strip().splitlines()[0]
                    add("harness", quote(first, 140), i, t)
                elif b.get("is_error") or "traceback (most recent call last)" in low:
                    last = _last_lines(text, 1)
                    if last:
                        add("error", last[0], i, t)
                elif "check" in kinds:
                    for l in _last_lines(text, 2, 120):
                        add("result", l, i, t)

        elif typ == "result":
            final = e.get("result")
            if final:
                add("done", quote(final, 360), i, t, done=True, full=final)

    # The final message also appears as an assistant text just before the result event: keep one.
    if lines and lines[-1]["kind"] == "done":
        for j in range(len(lines) - 2, -1, -1):
            if lines[j]["kind"] == "say":
                if lines[-1]["text"][:80] == lines[j]["text"][:80]:
                    del lines[j]
                break

    # merge runs of the same line (e.g. three edits of the same file in a row)
    merged = []
    for l in lines:
        if merged and merged[-1]["text"] == l["text"] and merged[-1]["kind"] == l["kind"]:
            merged[-1]["repeat"] = merged[-1].get("repeat", 1) + 1
            merged[-1].setdefault("src_more", []).append(l["src"]["line"])
            continue
        merged.append(l)

    info = {"events": len(events), "tool_calls": sum(1 for l in lines if l.get("tool_use_id"))}
    return merged, info
