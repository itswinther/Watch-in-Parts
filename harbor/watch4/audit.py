"""Audit Codex transcripts from Harbor trials for outside access.

    python3 harbor/watch4/audit.py TRIAL_DIR [TRIAL_DIR ...]

Reads <trial>/agent/codex.txt (the `codex exec --json` event stream). Flags, per trial:
  web_search    any web_search_call event (Codex's built-in search)
  codex_auth    any command or code that touches auth.json or ~/.codex
  model_api     any mention of chatgpt.com, backend-api or api.openai.com in a command or code
  http_client   any curl, wget, urllib, requests, http.client, httpx, aiohttp, socket, nc use
  outside_app   any absolute path outside /app, /tmp and system/interpreter paths in a command
A trial with any of the first four flags is treated as contaminated. The agent's own final
"Outside access:" line is reported as well. Only commands and code the agent ran are scanned,
not the task text it was given.
"""
import json
import os
import re
import sys

PATTERNS = {
    "codex_auth": re.compile(r"auth\.json|~/\.codex|/root/\.codex|\.codex/"),
    "model_api": re.compile(r"chatgpt\.com|backend-api|api\.openai\.com|api\.anthropic\.com|anthropic\.env|ANTHROPIC_API_KEY"),
    "http_client": re.compile(r"\bcurl\b|\bwget\b|urllib|\brequests\b|http\.client|\bhttpx\b|aiohttp|"
                              r"\bsocket\b|\bnc\s|\bnetcat\b|\bping\b|\bpip3? install|\bnpm install|apt-get"),
}
ABS = re.compile(r"(?<![\w.])(/[A-Za-z_][\w.\-/]*)")
OK_PREFIX = ("/app", "/tmp", "/usr", "/bin", "/dev/null", "/proc/self", "/etc/os-release", "/opt/conda",
             "/usr/local", "/lib", "/sbin")


def commands(path):
    """Yield (kind, text) for every command or tool input in a codex --json stream, and web searches."""
    with open(path, errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            blob = json.dumps(ev)
            if "web_search" in blob and ("web_search_call" in blob or '"type": "web_search"' in blob):
                yield "web_search", blob[:300]
            if ev.get("type") == "tool_use":                       # OpenCode stream
                part = ev.get("part") or {}
                tool = str(part.get("tool", ""))
                if tool.lower() in ("webfetch", "websearch", "web_search", "fetch"):
                    yield "web_search", blob[:300]
                yield "cmd", tool + " " + json.dumps((part.get("state") or {}).get("input", ""))
                continue
            if ev.get("type") == "text":
                yield "message", (ev.get("part") or {}).get("text", "")
                continue
            item = ev.get("item") or {}
            t = item.get("type") or ev.get("type") or ""
            if ev.get("type") == "item.started":
                continue
            if t in ("command_execution", "local_shell_call", "function_call", "custom_tool_call", "file_change",
                     "mcp_tool_call"):
                text = item.get("command") or item.get("arguments") or item.get("input") or json.dumps(item.get("changes", ""))
                if isinstance(text, list):
                    text = " ".join(map(str, text))
                yield "cmd", str(text)
            if t == "agent_message" and ev.get("type") == "item.completed":
                yield "message", item.get("text", "")


def audit(trial):
    p = os.path.join(trial, "agent", "codex.txt")
    if not os.path.isfile(p):
        p = os.path.join(trial, "agent", "opencode.txt")
    out = {"trial": trial, "flags": {}, "outside_paths": set(), "n_commands": 0, "outside_access_line": None}
    if not os.path.isfile(p):
        out["error"] = "no codex.txt or opencode.txt"
        return out
    for kind, text in commands(p):
        if kind == "web_search":
            out["flags"].setdefault("web_search", []).append(text)
            continue
        if kind == "message":
            m = re.search(r"Outside access:.*", text)
            if m:
                out["outside_access_line"] = m.group(0)[:200]
            continue
        out["n_commands"] += 1
        for k, rx in PATTERNS.items():
            if rx.search(text):
                out["flags"].setdefault(k, []).append(text[:300])
        for a in ABS.findall(text):
            if not a.startswith(OK_PREFIX):
                out["outside_paths"].add(a)
    return out


def main(argv):
    bad = 0
    for t in argv:
        r = audit(t)
        contaminated = any(k in r["flags"] for k in ("web_search", "codex_auth", "model_api", "http_client"))
        bad += contaminated
        print("== %s" % r["trial"])
        print("   commands scanned: %d; contaminated: %s" % (r["n_commands"], "YES" if contaminated else "no"))
        for k, v in r["flags"].items():
            print("   FLAG %s (%d): %s" % (k, len(v), v[0]))
        if r["outside_paths"]:
            print("   absolute paths outside /app (check by hand): %s" % sorted(r["outside_paths"])[:15])
        print("   agent says: %s" % r["outside_access_line"])
        if "error" in r:
            print("   ERROR: %s" % r["error"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
