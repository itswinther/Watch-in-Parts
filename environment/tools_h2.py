"""Measurement tools for instance H2, as a command line. The MCP server wraps the same functions.
Tools take whitelisted part names and numbers only, return geometry facts and format errors,
and never run submitted code.

    python tools_h2.py <tool> [args]        (--help lists the tools)

Part names
  your files:       base, lid                      (work/base.stl, work/lid.stl)
  supplied bodies:  A, B, battery, speaker
  pieces of them:   A_pcb, J1, J2, C1, J4, B_pcb, B_shield, J3, L1
  keep-outs:        keepout_J1, keepout_J2, keepout_J3
Supplied bodies, pieces and keep-outs are returned in the final pose that
work/assembly.json gives their body. Add --local to get them in the body's own frame.
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
from geometry import core
from geometry import h2_public as P
from geometry.core import FormatError
from geometry.contract import replay

WORK = os.environ.get("BIB_WORK", os.path.join(os.getcwd(), "work"))
SUBMIT = os.environ.get("BIB_SUBMIT", os.path.join(os.getcwd(), "submission"))
ASM = os.path.join(WORK, "assembly.json")


def final_poses():
    order, paths = P.load_assembly(ASM)
    return {n: paths[n][-1] for n in P.BODY_NAMES}


def part(name, local=False, move=None):
    if name == "base":
        m = P.load_base(os.path.join(WORK, "base.stl"))
    elif name == "lid":
        m = P.load_lid(os.path.join(WORK, "lid.stl"))
    else:
        if name in P.BODY_NAMES:
            owner, m = name, P.body(name)
        elif name in P.sub_parts():
            owner, m = P.sub_parts()[name]
        elif name.startswith("keepout_") and name[8:] in P.keepouts():
            owner, m = P.keepouts()[name[8:]]
        else:
            raise FormatError("unknown part name '%s'" % name)
        if not local:
            m = core.apply(m, final_poses()[owner])
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
    m = part(a.part, a.local, pose_arg(a.move))
    bb = m.bounding_box()
    return {"volume": m.volume(), "bbox_min": bb[:3], "bbox_max": bb[3:], "triangles": m.num_tri()}


def t_section(a):
    m = part(a.part, a.local, pose_arg(a.move))
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
    return {"min_distance": core.min_distance(part(a.a, a.local, pose_arg(a.move)), part(a.b, a.local), a.search),
            "search_limit": a.search}


def t_interference(a):
    return {"intersection_volume": core.ivol(part(a.a, a.local, pose_arg(a.move)), part(a.b, a.local))}


def t_thickness(a):
    n, dev = P.wall_opening(part("base"))
    return {"ball_radius": P.W_BALL, "pieces_after_opening": n, "max_distance_from_opened": dev}


def _world():
    base, lid = part("base"), part("lid")
    order, paths = P.load_assembly(ASM)
    local = {n: P.body(n) for n in P.BODY_NAMES}
    local["lid"] = lid
    lo, hi = P.printed_bbox(base, lid)
    return base, lid, order, paths, local, lo, hi


def t_bbox(a):
    base, lid = part("base"), part("lid")
    lo, hi = P.printed_bbox(base, lid)
    return {"bbox_min": lo.tolist(), "bbox_max": hi.tolist(), "bbox_volume": float(np.prod(hi - lo))}


def t_sweep(a):
    base, lid, order, paths, local, lo, hi = _world()
    out = {"format_messages": P.contract_messages(paths, local, lo, hi), "order": order + ["lid"]}
    placed = {"base": base}
    for name in order + ["lid"]:
        r = replay(local[name], paths[name], placed)
        r["poses"] = len(paths[name])
        out[name] = r
        placed[name] = core.apply(local[name], paths[name][-1])
    return out


def t_probe(a):
    base, lid, order, paths, local, lo, hi = _world()
    T = {n: paths[n][-1] for n in P.BODY_NAMES}
    solids = [base, lid] + [core.apply(local[n], T[n]) for n in P.BODY_NAMES]
    plugs = [core.apply(m, T[o]) for o, m in P.plugs().values()]
    return {"ball_diameter": P.BALL_DIA, "deepest_outside_ball_centre_below_bbox_faces": P.enclosure_depth(solids, plugs, lo, hi)}


def t_submit(a):
    base, lid, order, paths, local, lo, hi = _world()
    msgs = P.contract_messages(paths, local, lo, hi)
    if msgs:
        raise FormatError("; ".join(msgs))
    os.makedirs(SUBMIT, exist_ok=True)
    for f in ("base.stl", "lid.stl", "assembly.json"):
        shutil.copyfile(os.path.join(WORK, f), os.path.join(SUBMIT, f))
    return {"result": "accepted"}


def t_get_spec(a):
    with open(os.path.join(HERE, "public", "SPEC_H2.md")) as f:
        print(f.read())


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="tool", required=True)
    mv = dict(nargs="+", type=float, help="extra move for the first part: 3 numbers or a 4x4 matrix (16 numbers)")

    def add(name, fn, *args):
        p = sub.add_parser(name)
        for flags, kw in args:
            p.add_argument(*flags, **kw)
        p.set_defaults(fn=fn, local=False)
        return p
    loc = (("--local",), dict(action="store_true"))
    add("get_spec", t_get_spec)
    add("measure", t_measure, (("part",), {}), (("--move",), mv), loc)
    add("section", t_section, (("part",), {}), (("--axis",), dict(choices="xyz", required=True)),
        (("--at",), dict(type=float, required=True)), (("--polygons",), dict(action="store_true")), (("--move",), mv), loc)
    add("distance", t_distance, (("a",), {}), (("b",), {}), (("--move",), mv), (("--search",), dict(type=float, default=5.0)), loc)
    add("interference", t_interference, (("a",), {}), (("b",), {}), (("--move",), mv), loc)
    add("thickness", t_thickness)
    add("bbox", t_bbox)
    add("sweep", t_sweep)
    add("probe", t_probe)
    add("submit", t_submit)
    a = ap.parse_args(argv)
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
