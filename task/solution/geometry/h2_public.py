"""Instance H2: public numbers, supplied bodies and measurements. Safe to ship to the agent.
Bodies are given in their own frames; the agent chooses every final pose."""
import numpy as np
import manifold3d as m3
from scipy import ndimage
from . import constants as C1_
from . import bodies as H1
from . import core
from .core import box, cyl_z, union, FormatError

# ---- supplied bodies, own frames (mm) ----
BODY_NAMES = ("A", "B", "battery", "speaker")
# Board A is the H1 board: PCB 70 x 45 x 1.6 with J1, J2, C1, J4 (see geometry.constants).
B_PCB = ((0.0, 0.0, 0.0), (38.0, 27.5, 1.6))
B_SHIELD = ((2.0, 5.0, 1.6), (24.0, 22.0, 4.6))
B_J3 = ((26.0, -1.0, 1.6), (37.0, 9.0, 3.8))        # card slot, pokes 1.0 past the -Y edge
B_L1 = ((28.0, 16.0, -2.2), (34.0, 22.0, 0.0))      # inductor on the bottom
SPEAKER_DIA, SPEAKER_H = 18.0, 6.5                   # cylinder, axis z, centred on x = y = 0, z 0..6.5
BATTERY_SIZE = C1_.BATTERY_SIZE

# Connectors: owner body, and in the owner's frame the outward axis, the keep-out
# (a prism starting at the connector's outer face, KEEPOUT_LEN long) and its section.
KEEPOUT_LEN = 20.0
PLUG_GROW = 1.0          # opening may exceed the keep-out section by this much per side
PLUG_INSIDE = 3.0        # the plug also covers this far inward of the connector face
LID_THICKNESS = 2.0
LID_TOL = 0.01
VOL_TOL = 0.2
MAX_STEP, MAX_POSES, START_MIN_DIST, ROT_TOL = C1_.MAX_STEP, C1_.MAX_POSES, C1_.START_MIN_DIST, C1_.ROT_TOL
MAX_TRIANGLES, MAX_STL_BYTES, MAX_JSON_BYTES, SELF_UNION_TOL = C1_.MAX_TRIANGLES, C1_.MAX_STL_BYTES, C1_.MAX_JSON_BYTES, C1_.SELF_UNION_TOL
COORD_LIMIT = 500.0

SUPPORT_MOVE = 0.3
LOCATE_MOVE = 0.6
SWELL = 1.0
LEAD_MAX = 40.0
BATTERY_LEAD_CENTRE = C1_.BATTERY_LEAD_CENTRE
J4_CENTRE = C1_.J4_CENTRE

BALL_DIA = 1.0
ENCLOSE_VOXEL = 0.25
ENCLOSE_DEPTH = 2.5      # a ball from outside may not get deeper than this below the bounding box faces
W_VOXEL, W_BALL, W_ERODE_VOX, W_DILATE_VOX, W_DEV = C1_.W_VOXEL, C1_.W_BALL, C1_.W_ERODE_VOX, C1_.W_DILATE_VOX, C1_.W_DEV
GRID_JITTER = C1_.GRID_JITTER

# ---- score ----
V_ZERO = 95000.0         # bounding-box volume (mm3) at which the size term is 0
V_REF = 81343.3          # bounding-box volume of the reference design; size term is 1 at or below it


def body(name):
    if name == "A":
        return H1.board()
    if name == "B":
        return union([box(*B_PCB), box(*B_SHIELD), box(*B_J3), box(*B_L1)])
    if name == "battery":
        return box((0, 0, 0), BATTERY_SIZE)
    if name == "speaker":
        return cyl_z(0, 0, 0, SPEAKER_H, SPEAKER_DIA / 2)
    raise FormatError("unknown part name '%s'" % name)


def sub_parts():
    """Named pieces in their owner's frame: name -> (owner, Manifold)."""
    out = {"A_pcb": ("A", H1.pcb())}
    out.update({k: ("A", v) for k, v in H1.components().items()})
    out.update({"B_pcb": ("B", box(*B_PCB)), "B_shield": ("B", box(*B_SHIELD)),
                "J3": ("B", box(*B_J3)), "L1": ("B", box(*B_L1))})
    return out


def _j3_box(grow, y0, y1):
    return box((25.0 - grow, y0, 1.2 - grow), (38.0 + grow, y1, 4.2 + grow))   # section 13 x 3


def keepouts():
    """name -> (owner, keep-out prism) in the owner's frame."""
    k = H1.keepouts()
    return {"J1": ("A", k["J1"]), "J2": ("A", k["J2"]), "J3": ("B", _j3_box(0.0, -1.0 - KEEPOUT_LEN, -1.0))}


def keepout_far_centres():
    return {"J1": ("A", (-21.5, 22.5, 3.25)), "J2": ("A", (92.5, 12.0, -2.5)), "J3": ("B", (31.5, -21.0, 2.7))}


def plugs():
    """Solid plugs used by the enclosure test, owner frame."""
    return {"J1": ("A", H1.j1_section_box(PLUG_GROW, -21.5, -1.5 + PLUG_INSIDE)),
            "J2": ("A", H1.j2_section_cyl(PLUG_GROW, 72.5 - PLUG_INSIDE, 92.5)),
            "J3": ("B", _j3_box(PLUG_GROW, -1.0 - KEEPOUT_LEN, -1.0 + PLUG_INSIDE))}


# ---- files ----
def load_base(path):
    return core.load_part(path, MAX_TRIANGLES, MAX_STL_BYTES, SELF_UNION_TOL)


def load_lid(path):
    """The lid must be a flat rectangular plate, LID_THICKNESS thick in z, edges along x and y."""
    m = core.load_part(path, MAX_TRIANGLES, MAX_STL_BYTES, SELF_UNION_TOL)
    bb = np.array(m.bounding_box())
    size = bb[3:] - bb[:3]
    if abs(m.volume() - float(np.prod(size))) > 1e-3 * float(np.prod(size)):
        raise FormatError("lid is not a rectangular plate aligned with the axes")
    if abs(size[2] - LID_THICKNESS) > LID_TOL:
        raise FormatError("lid is %.3f thick in z, must be %.1f" % (size[2], LID_THICKNESS))
    return m


def printed_bbox(base, lid):
    a, b = np.array(base.bounding_box()), np.array(lid.bounding_box())
    lo, hi = np.minimum(a[:3], b[:3]), np.maximum(a[3:], b[3:])
    if np.abs(np.concatenate([lo, hi])).max() > COORD_LIMIT:
        raise FormatError("a printed vertex is further than %.0f from the origin" % COORD_LIMIT)
    return lo, hi


def parse_assembly(doc):
    """{"order": [four body names], "paths": {name: [4x4, ...] for the four bodies and "lid"}}"""
    if not isinstance(doc, dict) or "order" not in doc or "paths" not in doc:
        raise FormatError("top level must be an object with 'order' and 'paths'")
    order = doc["order"]
    if not isinstance(order, list) or sorted(map(str, order)) != sorted(BODY_NAMES):
        raise FormatError("'order' must list each of %s exactly once" % (BODY_NAMES,))
    if not isinstance(doc["paths"], dict):
        raise FormatError("'paths' must be an object")
    paths = {}
    for name in list(BODY_NAMES) + ["lid"]:
        if name not in doc["paths"]:
            raise FormatError("missing path for '%s'" % name)
        poses = doc["paths"][name]
        if not isinstance(poses, list) or len(poses) < 2:
            raise FormatError("'%s' needs a list of at least 2 poses" % name)
        if len(poses) > MAX_POSES:
            raise FormatError("'%s' has more than %d poses" % (name, MAX_POSES))
        try:
            arr = np.array(poses, dtype=np.float64)
        except (ValueError, TypeError) as e:
            raise FormatError("'%s' poses are not numeric 4x4 matrices" % name) from e
        if arr.shape != (len(poses), 4, 4):
            raise FormatError("'%s' poses must each be a 4x4 matrix" % name)
        if not np.isfinite(arr).all():
            raise FormatError("'%s' has a non-finite number" % name)
        paths[name] = arr
    return [str(o) for o in order], paths


def load_assembly(path):
    import json, os
    if os.path.getsize(path) > MAX_JSON_BYTES:
        raise FormatError("assembly.json larger than %d bytes" % MAX_JSON_BYTES)
    with open(path, "r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except ValueError as e:
            raise FormatError("assembly.json is not valid JSON") from e
    return parse_assembly(doc)


def contract_messages(paths, local, lo, hi):
    """Path format rules. local: name -> Manifold in the frame the poses apply to."""
    msgs = []
    env = box(lo, hi)
    for name, P in paths.items():
        V = core.verts(local[name])
        R, t = P[:, :3, :3], P[:, :3, 3]
        if np.abs(P[:, 3, :] - np.array([0, 0, 0, 1.0])).max() > ROT_TOL:
            msgs.append("%s: last row of a matrix is not 0 0 0 1" % name)
            continue
        rtr = np.einsum("nji,njk->nik", R, R) - np.eye(3)
        bad = np.nonzero((np.abs(rtr).max(axis=(1, 2)) > ROT_TOL) | (np.abs(np.linalg.det(R) - 1) > ROT_TOL))[0]
        if len(bad):
            msgs.append("%s: pose %d is not a proper rotation plus translation" % (name, bad[0]))
            continue
        W = np.einsum("nij,vj->nvi", R, V) + t[:, None, :]
        step = np.linalg.norm(W[1:] - W[:-1], axis=2).max(axis=1)
        bad = np.nonzero(step > MAX_STEP + 1e-9)[0]
        if len(bad):
            msgs.append("%s: a vertex moves %.4f between poses %d and %d (limit %.2f)"
                        % (name, step[bad[0]], bad[0], bad[0] + 1, MAX_STEP))
        if name == "lid" and np.abs(P[-1] - np.eye(4)).max() > 1e-6:
            msgs.append("lid: last pose is not the identity")
        if np.abs(W[-1]).max() > COORD_LIMIT:
            msgs.append("%s: final pose is further than %.0f from the origin" % (name, COORD_LIMIT))
        if core.ivol(core.apply(local[name], P[0]), env) > 1e-9:
            msgs.append("%s: first pose is not wholly outside the bounding box of the printed parts" % name)
        c = V.mean(axis=0)
        d = np.linalg.norm((R[0] @ c + t[0]) - (R[-1] @ c + t[-1]))
        if d < START_MIN_DIST:
            msgs.append("%s: first pose is %.3f from the last pose (minimum %.1f)" % (name, d, START_MIN_DIST))
    return msgs


# ---- measurements ----
def wall_opening(part):
    """(pieces left after opening with the wall ball, largest distance in mm from the part to what is left)."""
    h = W_VOXEL
    bb = np.array(part.bounding_box())
    lo_i = np.floor((bb[:3] + GRID_JITTER) / h).astype(int) - 1
    hi_i = np.ceil((bb[3:] + GRID_JITTER) / h).astype(int) + 1
    origin = lo_i * h - GRID_JITTER
    solid = core.voxelize(part, origin, tuple(int(v) for v in hi_i - lo_i), h)
    n, dev = core.opening_test(solid, W_ERODE_VOX, W_DILATE_VOX)
    return n, (dev * h if np.isfinite(dev) else 1e9)


def enclosure_depth(all_solids, plug_solids, lo, hi):
    """Flood free space from far outside with a ball of diameter BALL_DIA, connector
    openings plugged. Returns how deep (mm) below the faces of the printed parts'
    bounding box the ball centre gets; 0 if it never enters the box."""
    h = ENCLOSE_VOXEL
    pad = 3.0
    lo_i = np.floor((np.asarray(lo) - pad + GRID_JITTER) / h).astype(int)
    hi_i = np.ceil((np.asarray(hi) + pad + GRID_JITTER) / h).astype(int)
    origin = lo_i * h - GRID_JITTER
    shape = tuple(int(v) for v in hi_i - lo_i)
    solid = core.voxelize(union(list(all_solids) + list(plug_solids)), origin, shape, h)
    passable = core.edt(~np.pad(solid, 1, constant_values=False)) >= (BALL_DIA / 2) / h
    lab, _ = ndimage.label(passable)
    edge = np.zeros_like(passable)
    edge[0], edge[-1], edge[:, 0], edge[:, -1], edge[:, :, 0], edge[:, :, -1] = (True,) * 6
    ids = np.unique(lab[edge & passable])
    outside = np.isin(lab, ids[ids > 0])[1:-1, 1:-1, 1:-1]
    idx = np.argwhere(outside)
    if len(idx) == 0:
        return 0.0
    pts = origin + (idx + 0.5) * h
    depth = np.minimum(pts - np.asarray(lo), np.asarray(hi) - pts).min(axis=1)
    return float(max(depth.max(), 0.0))
