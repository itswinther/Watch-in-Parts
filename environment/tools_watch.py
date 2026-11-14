"""Measurement tools for the watch gear-train task, as a command line.
They read your work folder (work/movement.json and work/parts/<name>.stl), return
measurements and format errors, and never run submitted code.

    python tools_watch.py <tool> [args]        (--help lists the tools)

A PART is the name of one of your part files (without .stl), or "barrel".
A MOBILE is a mobile name from your movement.json, or "barrel".
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
from geometry import watch as W
from geometry.core import FormatError

WORK = os.environ.get("BIB_WORK", os.path.join(os.getcwd(), "work"))
SUBMIT = os.environ.get("BIB_SUBMIT", os.path.join(os.getcwd(), "submission"))


def part(name):
    if name == "barrel":
        return W.barrel()
    if not W.NAME_RE.match(name):
        raise FormatError("bad part name")
    p = os.path.join(WORK, "parts", name + ".stl")
    if not os.path.isfile(p):
        raise FormatError("part file parts/%s.stl not found" % name)
    return core.load_part(p, W.MAX_TRIANGLES, W.MAX_STL_BYTES, 0.005)


def mob(m, name):
    if name not in m.mobiles:
        raise FormatError("unknown mobile '%s'" % name)
    return name


def t_measure(a):
    m = part(a.part)
    bb = m.bounding_box()
    return {"volume": m.volume(), "bbox_min": bb[:3], "bbox_max": bb[3:], "triangles": m.num_tri()}


def t_section(a):
    m = part(a.part)
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
    return {"min_distance": core.min_distance(part(a.a), part(a.b), a.search), "search_limit": a.search}


def t_interference(a):
    return {"intersection_volume": core.ivol(part(a.a), part(a.b))}


def t_speeds(a):
    m = W.load_movement(WORK)
    w, conflicts = m.speeds()
    return {"clockwise_turns_per_hour": {k: str(v) for k, v in w.items()},
            "not_driven": [k for k in m.mobiles if k not in w], "conflicting_meshes": conflicts}


def t_spin(a):
    m = W.load_movement(WORK)
    return m.spin(mob(m, a.mobile))


def t_held(a):
    m = W.load_movement(WORK)
    return {"move": W.HELD_MOVE, "overlap_after_move": m.held(mob(m, a.mobile))}


def t_mesh(a):
    m = W.load_movement(WORK)
    for x, tx, y, ty in m.meshes:
        if (x, y) == (a.driver, a.driven):
            return m.mesh_run(x, tx, y, ty)
    raise FormatError("no mesh with that driver and driven in movement.json")


def t_clear(a):
    m = W.load_movement(WORK)
    w, _ = m.speeds()
    return m.clear_run(mob(m, a.a), mob(m, a.b), w.get(a.a, 0), w.get(a.b, 0))


def t_extent(a):
    m = W.load_movement(WORK)
    out = m.extent()
    out["hand_reach"] = {h: m.hand_reach(h) for h in m.hands}
    return out


def t_submit(a):
    W.load_movement(WORK)
    with open(os.path.join(WORK, "movement.json")) as f:
        doc = json.load(f)
    names = list(doc["fixed"]) + [p for mm in doc["mobiles"].values() for p in mm["parts"]]
    if os.path.isdir(SUBMIT):
        shutil.rmtree(SUBMIT)
    os.makedirs(os.path.join(SUBMIT, "parts"))
    shutil.copyfile(os.path.join(WORK, "movement.json"), os.path.join(SUBMIT, "movement.json"))
    for n in names:
        shutil.copyfile(os.path.join(WORK, "parts", n + ".stl"), os.path.join(SUBMIT, "parts", n + ".stl"))
    return {"result": "accepted", "parts": len(names)}


def t_get_spec(a):
    with open(os.path.join(HERE, "public", "SPEC_WATCH.md")) as f:
        print(f.read())


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="tool", required=True)

    def add(name, fn, *args):
        p = sub.add_parser(name)
        for flags, kw in args:
            p.add_argument(*flags, **kw)
        p.set_defaults(fn=fn)
    add("get_spec", t_get_spec)
    add("measure", t_measure, (("part",), {}))
    add("section", t_section, (("part",), {}), (("--axis",), dict(choices="xyz", required=True)),
        (("--at",), dict(type=float, required=True)), (("--polygons",), dict(action="store_true")))
    add("distance", t_distance, (("a",), {}), (("b",), {}), (("--search",), dict(type=float, default=5.0)))
    add("interference", t_interference, (("a",), {}), (("b",), {}))
    add("speeds", t_speeds)
    add("spin", t_spin, (("mobile",), {}))
    add("held", t_held, (("mobile",), {}))
    add("mesh", t_mesh, (("driver",), {}), (("driven",), {}))
    add("clear", t_clear, (("a",), {}), (("b",), {}))
    add("extent", t_extent)
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
