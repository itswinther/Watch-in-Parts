"""Audit agent transcripts of a Harbor job for outside access.

    python audit.py JOB_DIR

Scans every trial's agent/ folder (codex.txt, opencode.txt, trajectory.json) for: web search events,
network tools and libraries, model endpoints, auth files, and absolute paths outside /app that
the agent touched. Prints one block per trial with counts and a few context snippets.
"""
import glob
import os
import re
import sys

PATTERNS = {
    "web_search_call": r"web_search_call",
    "network command": r"\b(curl|wget|nc|ssh|scp|ping|pip install|apt-get install|apt install|git clone|npm install)\b",
    "network library": r"\b(urllib|requests\.(get|post)|http\.client|socket\.socket|httpx|aiohttp)\b",
    "endpoint": r"(chatgpt\.com|backend-api|api\.openai\.com|api\.anthropic\.com|generativelanguage)",
    "auth file": r"(auth\.json|\.codex/|ANTHROPIC_API_KEY|OPENAI_API_KEY|sk-ant-)",
    "outside /app": r"(?<![\w/.])/(?!app\b|app/|tmp\b|tmp/|dev/null|usr/|bin/|lib/|proc/self)(etc|root|home|logs|tests|solution|opt|var|Users|private|mnt|srv)(/[\w.\-/]*)?",
}


def scan(text):
    out = {}
    for name, pat in PATTERNS.items():
        hits = [m for m in re.finditer(pat, text)]
        if hits:
            out[name] = (len(hits), [text[max(0, h.start() - 60):h.end() + 60].replace("\n", " ") for h in hits[:3]])
    return out


def main(job):
    for trial in sorted(glob.glob(os.path.join(job, "*", ""))):
        agent = os.path.join(trial, "agent")
        if not os.path.isdir(agent):
            continue
        texts = []
        for f in glob.glob(os.path.join(agent, "**", "*"), recursive=True):
            if os.path.isfile(f) and f.endswith((".txt", ".json", ".jsonl", ".log")):
                try:
                    texts.append(open(f, errors="replace").read())
                except OSError:
                    pass
        res = scan("\n".join(texts))
        print("==", os.path.basename(os.path.normpath(trial)))
        if not res:
            print("   nothing flagged")
        for k, (n, ex) in res.items():
            print("   %-16s %d" % (k, n))
            for e in ex:
                print("      ...%s..." % e[:220])


if __name__ == "__main__":
    main(sys.argv[1])
