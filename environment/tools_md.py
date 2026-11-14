"""Measurement tools for Moving Day, as a command line. The MCP server wraps the same functions.
Tools take part names and numbers only, return geometry facts and format messages,
and never run submitted code.

    python tools_md.py <tool> [args]        (--help lists the tools)

Part names: "apartment", and each furniture piece by name (see the spec).
A piece is in its own frame unless you pass --final (its given final pose) or
--pose with 16 numbers (a 4x4 matrix, row by row). --pose2 does the same for
the second part of `distance` and `interference`.
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
from geometry import core, md
from geometry.core import FormatError

INSTANCE = os.environ.get("MD_INSTANCE", "flat-1")
WORK = os.environ.get("BIB_WORK", os.path.join(os.getcwd(), "work"))
SUBMIT = os.environ.get("BIB_SUBMIT", os.path.join(os.getcwd(), "submission"))
PLAN = os.path.join(WORK, "plan.json")


def part(inst, name, final=False, pose=None):
    if name == "apartment":
        return inst.apartment()
    m = inst.piece(name)
    if pose is not None:
        if len(pose) != 16:
            raise FormatError("a pose is 16 numbers (4x4 matrix, row by row)")
        return core.apply(m, np.array(pose, float).reshape(4, 4))
    if final:
        return core.apply(m, inst.final(name))
    return m


def t_measure(a, inst):
    m = part(inst, a.part, a.final, a.pose)
    bb = m.bounding_box()
    return {"volume": m.volume(), "bbox_min": bb[:3], "bbox_max": bb[3:], "triangles": m.num_tri()}


def t_section(a, inst):
    m = part(inst, a.part, a.final, a.pose)
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
        out["polygons"] = [np.round(np.asarray(p), 3).tolist() for p in cs.to_polygons()]
    return out


def t_distance(a, inst):
    A, B = part(inst, a.a, a.final, a.pose), part(inst, a.b, a.final2, a.pose2)
    return {"min_distance": core.min_distance(A, B, a.search), "search_limit": a.search}


def t_interference(a, inst):
    return {"intersection_volume": core.ivol(part(inst, a.a, a.final, a.pose), part(inst, a.b, a.final2, a.pose2))}


def t_sweep(a, inst):
    order, paths, notes = md.load_plan(PLAN, inst)
    results, delivered = md.replay(inst, order, paths)
    return {"notes": notes, "order_used": order, "pieces": results}


def t_submit(a, inst):
    md.load_plan(PLAN, inst)
    os.makedirs(SUBMIT, exist_ok=True)
    shutil.copyfile(PLAN, os.path.join(SUBMIT, "plan.json"))
    return {"result": "accepted"}


def t_get_spec(a, inst):
    with open(os.path.join(HERE, "public", "SPEC_MD.md")) as f:
        print(f.read())


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="tool", required=True)
    pose = dict(nargs=16, type=float)

    def add(name, fn, *args):
        p = sub.add_parser(name)
        for flags, kw in args:
            p.add_argument(*flags, **kw)
        p.set_defaults(fn=fn, final=False, pose=None, final2=False, pose2=None)
    one = [(("--final",), dict(action="store_true")), (("--pose",), pose)]
    two = one + [(("--final2",), dict(action="store_true")), (("--pose2",), pose)]
    add("get_spec", t_get_spec)
    add("measure", t_measure, (("part",), {}), *one)
    add("section", t_section, (("part",), {}), (("--axis",), dict(choices="xyz", required=True)),
        (("--at",), dict(type=float, required=True)), (("--polygons",), dict(action="store_true")), *one)
    add("distance", t_distance, (("a",), {}), (("b",), {}), (("--search",), dict(type=float, default=50.0)), *two)
    add("interference", t_interference, (("a",), {}), (("b",), {}), *two)
    add("sweep", t_sweep)
    add("submit", t_submit)
    a = ap.parse_args(argv)
    try:
        out = a.fn(a, md.INSTANCES[INSTANCE]())
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
