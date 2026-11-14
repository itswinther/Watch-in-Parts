"""The agent's measurement tools as a command line. The MCP server wraps the same functions.
Tools take whitelisted part names and numbers only, return geometry facts and format errors,
and never run submitted code.

    python tools_cli.py <tool> [args]        (run with --help for the list)

Part names: your own files  work/base.stl -> "base", work/door.stl -> "door";
supplied bodies "board" (PCB with components), "pcb", "J1", "J2", "C1", "J4", "lid",
"battery" (in its own frame unless --battery-pose is given), "keepout_J1", "keepout_J2", "envelope".
"""
import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (HERE, os.path.dirname(HERE)):
    if os.path.isdir(os.path.join(cand, "geometry")):
        sys.path.insert(0, cand)
        break
import numpy as np
from geometry import constants as C
from geometry import bodies as B
from geometry import core, measure
from geometry.core import FormatError
from geometry.contract import load_assembly, check_contract, replay

WORK = os.environ.get("BIB_WORK", os.path.join(os.getcwd(), "work"))
SUBMIT = os.environ.get("BIB_SUBMIT", os.path.join(os.getcwd(), "submission"))
OWN = ("base", "door")


def part(name, move=None):
    if name in OWN:
        m = core.load_part(os.path.join(WORK, name + ".stl"), C.MAX_TRIANGLES, C.MAX_STL_BYTES, C.SELF_UNION_TOL)
    else:
        table = {"board": B.board, "pcb": B.pcb, "lid": B.lid, "battery": B.battery, "envelope": B.envelope_box,
                 "keepout_J1": lambda: B.keepouts()["J1"], "keepout_J2": lambda: B.keepouts()["J2"]}
        table.update({k: (lambda k=k: B.components()[k]) for k in ("J1", "J2", "C1", "J4")})
        if name not in table:
            raise FormatError("unknown part name '%s'" % name)
        m = table[name]()
    if move is not None:
        m = core.apply(m, move)
    return m


def pose_arg(vals):
    if vals is None:
        return None
    if len(vals) == 3:
        return core.translation(vals)
    if len(vals) == 16:
        return np.array(vals, float).reshape(4, 4)
    raise FormatError("a move is 3 numbers (translation) or 16 numbers (4x4 row-major)")


def t_measure(a):
    m = part(a.part, pose_arg(a.move))
    bb = m.bounding_box()
    return {"volume": m.volume(), "surface_area": m.surface_area(), "bbox_min": bb[:3], "bbox_max": bb[3:],
            "triangles": m.num_tri()}


def t_section(a):
    m = part(a.part, pose_arg(a.move))
    if a.axis == "x":
        cs, axes = core.section_x(m, a.at), "y,z"
    elif a.axis == "y":
        cs, axes = m.transform([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]]).slice(a.at), "z,x"
    else:
        cs, axes = m.slice(a.at), "x,y"
    out = {"axes": axes, "area": cs.area(), "contours": cs.num_contour()}
    if not cs.is_empty():
        out["bounds"] = list(cs.bounds())
    if a.polygons:
        out["polygons"] = [np.round(np.asarray(p), 4).tolist() for p in cs.to_polygons()]
    return out


def t_distance(a):
    return {"min_distance": core.min_distance(part(a.a, pose_arg(a.move)), part(a.b), a.search), "search_limit": a.search}


def t_interference(a):
    return {"intersection_volume": core.ivol(part(a.a, pose_arg(a.move)), part(a.b))}


def t_thickness(a):
    n, dev = measure.wall_opening(part(a.part))
    return {"ball_radius": C.W_BALL, "pieces_after_opening": n, "max_distance_from_opened": dev}


def _world(path):
    paths = load_assembly(path)
    local = {"board": B.board(), "lid": B.lid(), "battery": B.battery(), "door": part("door")}
    return paths, local


def t_sweep(a):
    path = a.assembly or os.path.join(WORK, "assembly.json")
    paths, local = _world(path)
    out = {"format_messages": check_contract(paths, local, B.envelope_box())}
    placed = {"base": part("base")}
    for name in C.BODY_ORDER:
        r = replay(local[name], paths[name], placed)
        r["poses"] = len(paths[name])
        out[name] = r
        placed[name] = core.apply(local[name], paths[name][-1])
    return out


def t_probe(a):
    path = a.assembly or os.path.join(WORK, "assembly.json")
    paths, local = _world(path)
    batt = core.apply(local["battery"], paths["battery"][-1])
    bodies = [part("base"), local["door"], local["board"], local["lid"], batt]
    return {"ball_diameter": C.G5_SPHERE_DIA,
            "closest_outside_ball_centre_to_board_or_battery": measure.enclosure_reach(bodies, core.union([local["board"], batt]))}


def t_submit(a):
    for n in OWN:
        part(n)
    paths, local = _world(os.path.join(WORK, "assembly.json"))
    msgs = check_contract(paths, local, B.envelope_box())
    if msgs:
        raise FormatError("; ".join(msgs))
    os.makedirs(SUBMIT, exist_ok=True)
    for f in ("base.stl", "door.stl", "assembly.json"):
        shutil.copyfile(os.path.join(WORK, f), os.path.join(SUBMIT, f))
    return {"result": "accepted"}


def t_get_spec(a):
    with open(os.path.join(HERE, "public", "SPEC_PUBLIC.md")) as f:
        print(f.read())
    return None


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="tool", required=True)
    mv = dict(nargs="+", type=float, help="move the first part: 3 numbers or a 4x4 matrix (16 numbers)")
    p = sub.add_parser("get_spec"); p.set_defaults(fn=t_get_spec)
    p = sub.add_parser("measure"); p.add_argument("part"); p.add_argument("--move", **mv); p.set_defaults(fn=t_measure)
    p = sub.add_parser("section"); p.add_argument("part"); p.add_argument("--axis", choices="xyz", required=True)
    p.add_argument("--at", type=float, required=True); p.add_argument("--polygons", action="store_true")
    p.add_argument("--move", **mv); p.set_defaults(fn=t_section)
    p = sub.add_parser("distance"); p.add_argument("a"); p.add_argument("b"); p.add_argument("--move", **mv)
    p.add_argument("--search", type=float, default=5.0); p.set_defaults(fn=t_distance)
    p = sub.add_parser("interference"); p.add_argument("a"); p.add_argument("b"); p.add_argument("--move", **mv); p.set_defaults(fn=t_interference)
    p = sub.add_parser("thickness"); p.add_argument("part", choices=OWN); p.set_defaults(fn=t_thickness)
    p = sub.add_parser("sweep"); p.add_argument("--assembly"); p.set_defaults(fn=t_sweep)
    p = sub.add_parser("probe"); p.add_argument("--assembly"); p.set_defaults(fn=t_probe)
    p = sub.add_parser("submit"); p.set_defaults(fn=t_submit)
    a = ap.parse_args(argv)
    if getattr(a, "assembly", None) is not None:
        a.assembly = None      # no path arguments: always work/assembly.json
    try:
        out = a.fn(a)
    except FormatError as e:
        print(json.dumps({"format_error": str(e)}))
        return 1
    except FileNotFoundError as e:
        print(json.dumps({"format_error": "file not found: %s" % os.path.basename(str(e.filename))}))
        return 1
    if out is not None:
        print(json.dumps(out, default=lambda o: list(o) if hasattr(o, "__iter__") else float(o)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
