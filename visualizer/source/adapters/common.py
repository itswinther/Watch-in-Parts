"""Parts every adapter shares: reading grader output, finding versions, quoting text.

Rule for everything here: copy numbers and words from the files, never make them up.
A score is only ever taken from the grader's own output (details.json / manifest.json).
"""
import json
import os
import re
import subprocess

STAGE_NAMES = {1: "Design", 2: "Extend", 3: "Change", 4: "Assemble"}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def quote(text, limit=220):
    """A verbatim quote, shortened at a sentence or word boundary, with an ellipsis if cut."""
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "), cut.rfind(": "))
    if end > limit * 0.5:
        return cut[: end + 1] + " …"
    return cut[: cut.rfind(" ")].rstrip(",;") + " …"


def git(repo, *args):
    out = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return out.stdout.strip()


def spec_version_at(repo, commit):
    """The 'Version: X' line of SPEC.md at a commit."""
    text = git(repo, "show", f"{commit}:SPEC.md")
    m = re.search(r"Version:\s*([0-9][0-9.]*)", text)
    return m.group(1) if m else "unknown"


def versions_for(repo, rel_path):
    """Task and grader version for a run stored in the repo.

    details.json does not record a grader version, so we use the commit that added the
    graded files to the repo and the SPEC.md version at that commit, and say so."""
    commit = git(repo, "log", "--diff-filter=A", "-1", "--format=%h", "--", rel_path)
    if not commit:
        commit = git(repo, "log", "-1", "--format=%h", "--", rel_path)
    when = git(repo, "log", "-1", "--format=%ad", "--date=format:%Y-%m-%d %H:%M", commit) if commit else ""
    spec = spec_version_at(repo, commit) if commit else "unknown"
    head = git(repo, "rev-parse", "--short", "HEAD")
    current = spec_version_at(repo, head)
    return {
        "task_version": f"staged watch, SPEC {spec}",
        "grader_version": f"tests/grade_watch.py, SPEC {spec}",
        "graded_at_commit": commit,
        "graded_at_time": when,
        "current_spec": current,
        "regraded_on_current": False,
        "version_note": (
            "The grader output does not record its own version. This is the SPEC.md version at "
            f"commit {commit}, which added these graded files to the repo."
            + (f" The repo is now on SPEC {current}; this run has not been regraded on it."
               if current != spec else "")
        ),
    }


def failures_from_details(details, introduced_in=None):
    """One entry per failed gate or check, with the grader's own detail for it."""
    out = []
    inner = details.get("details", {})
    parts = inner.get("parts", {}) if isinstance(inner, dict) else {}
    for kind in ("gates", "checks"):
        for name, ok in details.get(kind, {}).items():
            if ok:
                continue
            d = parts.get(name) if name in parts else inner.get(name)
            entry = {"name": name, "kind": kind[:-1], "detail": d}
            if isinstance(d, dict):
                for k in ("format_messages", "hit", "pose_index", "poses", "worst_volume"):
                    if k in d:
                        entry[k] = d[k]
            if introduced_in and name in introduced_in:
                entry["introduced_in_section"] = introduced_in[name]
            out.append(entry)
    return out


def part_first_seen(stage_dirs):
    """{part name: first stage number whose submission has that part file}."""
    seen = {}
    for n, d in stage_dirs:
        names = []
        pj = os.path.join(d, "submission", "parts.json")
        pd = os.path.join(d, "submission", "parts")
        if os.path.exists(pj):
            names = list(load_json(pj))
        elif os.path.isdir(pd):
            names = os.listdir(pd)
        for f in names:
            seen.setdefault(os.path.splitext(f)[0], n)
    return seen
