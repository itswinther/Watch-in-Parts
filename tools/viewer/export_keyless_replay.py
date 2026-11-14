"""Replay page for a keyless-works submission: the grader's recorded simulation, frame by frame.

    python -I spikes/keyless/grade.py SUB spikes/keyless/data --reward r.txt --details d.json --trace t.json
    python tools/viewer/export_keyless_replay.py SUB OUT.html --supplied spikes/keyless/data \
        --trace t.json --details d.json --title "Reference"

Every mobile moves exactly as the contact simulation moved it (no animation of our own). Phases are
labelled; a legend says what each part does. Supplied plates are drawn see-through.
"""
import argparse
import base64
import json
import os

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
STEM = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
BARREL = ((2.15, 4.157, 0.0), (0.0, 0.0, 1.0))
MINUTE = ((4.65, -4.157, 0.0), (0.0, 0.0, 1.0))

ROLE_HINTS = [   # plain-words description by name fragment (reference names); generic text otherwise
    ("stem", "Stem and crown: the owner turns it, and pulls it out to set the hands."),
    ("sliding", "Sliding pinion: turns with the stem; pushed in, its ratchet teeth drive the winding pinion; "
                "pulled out, its outer teeth turn the setting wheel."),
    ("winding_pinion", "Winding pinion: driven by the sliding pinion's ratchet teeth; drives the crown wheel."),
    ("crown_wheel", "Crown wheel: turns the motion through a right angle, from the stem to the barrel."),
    ("barrel", "Barrel arbor and ratchet: winding turns it; the mainspring always pulls it back."),
    ("click", "Click: a spring-loaded pawl that lets the ratchet turn one way only."),
    ("setting_wheel", "Setting wheel: in position 2, carries the crown's turning to the minute wheel."),
    ("minute_wheel", "Minute wheel (supplied): turning it sets the hands."),
]
PHASES = [("wind", "Winding"), ("hold", "Let go: the click holds"), ("backward", "Backward: the ratchet slips"),
          ("set", "Pulling the crown and setting the hands"), ("return", "Push back in and rewind")]


def mesh(path):
    m = trimesh.load(path, force="mesh")
    return (base64.b64encode(np.asarray(m.vertices, np.float32).tobytes()).decode(),
            base64.b64encode(np.asarray(m.faces, np.uint32).tobytes()).decode(), int(len(m.faces)))


def role(name, kind):
    for frag, text in ROLE_HINTS:
        if frag in name:
            return text
    return {"free": "A wheel or part that turns or slides only when pushed.",
            "spring": "A spring-loaded part: it yields when pushed and returns to its rest side."}.get(
        kind, "Part of the mechanism.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sub"); ap.add_argument("out")
    ap.add_argument("--supplied", required=True); ap.add_argument("--trace", required=True)
    ap.add_argument("--details"); ap.add_argument("--title", default="")
    ap.add_argument("--every", type=int, default=1, help="keep every n-th frame")
    a = ap.parse_args()
    k = json.load(open(os.path.join(a.sub, "keyless.json")))
    tr = json.load(open(a.trace))["trace"]
    det = json.load(open(a.details)) if a.details and os.path.exists(a.details) else {}
    mobiles = {}
    for name, m in k.get("mobiles", {}).items():
        kind = m.get("kind")
        if name == "stem":
            mobiles[name] = {"dof": "stem", "point": STEM[0], "dir": STEM[1], "kind": "stem"}
        elif name == "barrel":
            mobiles[name] = {"dof": "rot", "point": BARREL[0], "dir": BARREL[1], "kind": "barrel"}
        else:
            mobiles[name] = {"dof": m.get("dof"), "point": m.get("point", [0, 0, 0]), "dir": m.get("direction"),
                             "kind": kind, "carrier": "stem" if m.get("on_stem") else None}
        mobiles[name]["role"] = role(name, kind)
        mobiles[name]["parts"] = list(m.get("parts", []))
    mobiles["minute_wheel"] = {"dof": "rot", "point": MINUTE[0], "dir": MINUTE[1], "kind": "supplied",
                               "role": role("minute_wheel", "free"), "parts": ["minute_wheel"]}
    mobiles["barrel"]["parts"] = mobiles["barrel"]["parts"] + ["barrel_arbor"]
    owner = {p: n for n, m in mobiles.items() for p in m["parts"]}
    parts = []
    pdir = os.path.join(a.sub, "parts")
    for f in sorted(os.listdir(pdir)):
        if f.endswith(".stl") and not os.path.islink(os.path.join(pdir, f)):
            pos, idx, t = mesh(os.path.join(pdir, f))
            parts.append({"name": f[:-4], "mobile": owner.get(f[:-4]), "ghost": False, "pos": pos, "idx": idx})
    for f in sorted(os.listdir(a.supplied)):
        if f.endswith(".stl"):
            n = f[:-4]
            pos, idx, t = mesh(os.path.join(a.supplied, f))
            parts.append({"name": n, "mobile": owner.get(n), "ghost": n in ("main_plate", "dial_plate"),
                          "pos": pos, "idx": idx})
    frames = []
    for key, label in PHASES:
        fr = tr.get(key, [])[:: max(1, a.every)]
        for f in fr:
            frames.append({"phase": key, "phase_label": label, "label": f["label"], "q": f["q"]})
    at = det.get("at", {})
    data = {"title": a.title, "mobiles": mobiles, "parts": parts, "frames": frames, "at": at,
            "reward": det.get("reward"), "product": det.get("product"),
            "phases": [{"key": k_, "label": l, "at": {"wind": "AT-1", "hold": "AT-2", "backward": "AT-4",
                                                      "set": "AT-5", "return": "AT-6"}[k_]} for k_, l in PHASES]}
    html = open(os.path.join(HERE, "keyless_replay_template.html")).read().replace("/*__DATA__*/null", json.dumps(data))
    open(a.out, "w").write(html)
    print(a.out, len(parts), "parts", len(frames), "frames", round(os.path.getsize(a.out) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
