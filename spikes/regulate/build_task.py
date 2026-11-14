"""Write a Harbor task for regulating one hidden watch.

    python3 build_task.py SEED OUTDIR

The hidden watch lives in a compose sidecar ("timer"). The agent's image holds only the brief
and the command-line client. The verifier collects the final true error from the sidecar
after the agent stops, and scores it against precomputed untouched and reference errors.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timing  # noqa: E402


def build(seed, out):
    if os.path.exists(out):
        shutil.rmtree(out)
    env = os.path.join(out, "environment")
    os.makedirs(os.path.join(env, "app"))
    os.makedirs(os.path.join(env, "timer"))
    shutil.copy(os.path.join(HERE, "BRIEF.md"), os.path.join(out, "instruction.md"))
    shutil.copy(os.path.join(HERE, "BRIEF.md"), os.path.join(env, "app", "BRIEF.md"))
    shutil.copy(os.path.join(HERE, "timer.py"), os.path.join(env, "app", "timer.py"))
    open(os.path.join(env, "Dockerfile"), "w").write(
        "FROM python:3.12-slim\n"
        "RUN apt-get update && apt-get install -y --no-install-recommends curl bash ripgrep ca-certificates nodejs npm \\\n"
        " && npm install -g @openai/codex && codex --version && pip install --no-cache-dir scipy==1.18.1 numpy==2.5.3 \\\n"
        " && rm -rf /var/lib/apt/lists/*\n"
        "WORKDIR /app\nCOPY app/ /app/\n")
    for f in ("timing.py", "server.py"):
        shutil.copy(os.path.join(HERE, f), os.path.join(env, "timer", f))
    open(os.path.join(env, "timer", "seed.txt"), "w").write(str(seed))
    import secrets
    open(os.path.join(env, "timer", "token.txt"), "w").write(secrets.token_hex(16))
    open(os.path.join(env, "timer", "Dockerfile"), "w").write(
        "FROM python:3.12-slim\nWORKDIR /srv\nCOPY . /srv/\nEXPOSE 8000\nCMD [\"python3\", \"-u\", \"/srv/server.py\"]\n")
    open(os.path.join(env, "docker-compose.yaml"), "w").write(
        "services:\n"
        "  main:\n"
        "    depends_on:\n"
        "      timer:\n"
        "        condition: service_healthy\n"
        "  timer:\n"
        "    build:\n"
        "      context: ./timer\n"
        "    healthcheck:\n"
        "      test: [\"CMD\", \"python3\", \"-c\", \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)\"]\n"
        "      interval: 2s\n"
        "      timeout: 5s\n"
        "      retries: 15\n"
        "      start_period: 3s\n")
    none = timing.Watch(seed).error()
    ref = timing.reference(seed).error()
    os.makedirs(os.path.join(out, "tests"))
    json.dump({"untouched_error": none, "reference_error": ref}, open(os.path.join(out, "tests", "anchors.json"), "w"), indent=1)
    open(os.path.join(out, "tests", "test.sh"), "w").write(
        "#!/bin/bash\nset -u\nmkdir -p /logs/verifier\necho 0 > /logs/verifier/reward.txt\n"
        "python3 -I - <<'PY'\n"
        "import json, math\n"
        "a = json.load(open('/tests/anchors.json'))\n"
        "try:\n"
        "    f = json.load(open('/tmp/final.json'))\n"
        "    e = float(f['error_s_per_day'])\n"
        "except Exception as ex:\n"
        "    print('no final state:', type(ex).__name__); raise SystemExit\n"
        "if not math.isfinite(e):\n"
        "    raise SystemExit\n"
        "n, r = a['untouched_error'], a['reference_error']\n"
        "s = max(0.0, min(1.0, (n - e) / (n - r))) if n > r else 0.0\n"
        "json.dump({'error': e, 'untouched': n, 'reference': r, 'score': s, 'actions': len(f.get('log', []))}, open('/logs/verifier/details.json', 'w'), indent=1)\n"
        "open('/logs/verifier/reward.txt', 'w').write('%.4f\\n' % s)\n"
        "print('error %.2f untouched %.2f reference %.2f score %.4f' % (e, n, r, s))\n"
        "PY\n")
    os.chmod(os.path.join(out, "tests", "test.sh"), 0o755)
    os.makedirs(os.path.join(out, "solution"))
    # oracle: replay the reference watchmaker's actions through the same client
    w = timing.reference(seed)
    lines = ["#!/bin/bash", "cd /app"]
    for e in w.log:
        if e[0] == "measure":
            lines.append("python3 timer.py measure %s %s %d" % (e[1], e[2], e[3]))
        elif e[0] == "remove":
            lines.append("python3 timer.py remove %d %s" % (e[1], e[2]))
        elif e[0] == "regulate":
            lines.append("python3 timer.py regulate %s" % e[1])
        elif e[0] == "washer":
            lines.append("python3 timer.py washer %d" % e[1])
    open(os.path.join(out, "solution", "solve.sh"), "w").write("\n".join(lines) + "\n")
    os.chmod(os.path.join(out, "solution", "solve.sh"), 0o755)
    open(os.path.join(out, "task.toml"), "w").write(
        'schema_version = "1.3"\n'
        'artifacts = [{ source = "/tmp/final.json", service = "timer" }]\n\n'
        '[task]\nname = "junction/regulate-watch-s%d"\n'
        'description = "Regulate a hidden mechanical watch on a timing machine with a time budget and irreversible adjustments."\n\n'
        '[metadata]\ncategory = "engineering-measurement"\n\n'
        '[verifier]\ntimeout_sec = 120.0\nenvironment_mode = "separate"\nnetwork_mode = "no-network"\n\n'
        '[[verifier.collect]]\nservice = "timer"\n'
        'command = "python3 -c \\"import urllib.request; open(\'/tmp/final.json\',\'wb\').write(urllib.request.urlopen(\'http://localhost:8000/final?token=\' + open(\'/srv/token.txt\').read().strip()).read())\\""\n'
        'timeout_sec = 30.0\n\n'
        '[agent]\ntimeout_sec = 2400.0\n\n'
        '[environment]\nnetwork_mode = "allowlist"\nallowed_hosts = ["chatgpt.com"]\n'
        'build_timeout_sec = 900.0\ncpus = 2\nmemory_mb = 2048\n' % seed)
    return none, ref


if __name__ == "__main__":
    n, r = build(int(sys.argv[1]), sys.argv[2])
    print("untouched error %.1f, reference error %.1f" % (n, r))
