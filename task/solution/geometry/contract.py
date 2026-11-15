"""assembly.json: parsing, contract rules (gate G4) and the pose-by-pose replay.

Format: {"board": [P, ...], "lid": [...], "battery": [...], "door": [...]}
Each P is a 4x4 row-major matrix that maps the body from its supplied frame
(board, lid, door: final-pose frame; battery: own frame) to the world.
Messages state format facts only.
"""
import json
import os
import numpy as np
from . import constants as C
from .core import FormatError, apply, verts, ivol


def load_assembly(path):
    if os.path.getsize(path) > C.MAX_JSON_BYTES:
        raise FormatError("assembly.json larger than %d bytes" % C.MAX_JSON_BYTES)
    with open(path, "r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except ValueError as e:
            raise FormatError("assembly.json is not valid JSON") from e
    return parse_assembly(doc)


def parse_assembly(doc):
    if not isinstance(doc, dict):
        raise FormatError("top level must be an object")
    out = {}
    for name in C.BODY_ORDER:
        if name not in doc:
            raise FormatError("missing body '%s'" % name)
        poses = doc[name]
        if not isinstance(poses, list) or len(poses) < 2:
            raise FormatError("'%s' needs a list of at least 2 poses" % name)
        if len(poses) > C.MAX_POSES:
            raise FormatError("'%s' has more than %d poses" % (name, C.MAX_POSES))
        try:
            arr = np.array(poses, dtype=np.float64)
        except (ValueError, TypeError) as e:
            raise FormatError("'%s' poses are not numeric 4x4 matrices" % name) from e
        if arr.shape != (len(poses), 4, 4):
            raise FormatError("'%s' poses must each be a 4x4 matrix" % name)
        if not np.isfinite(arr).all():
            raise FormatError("'%s' has a non-finite number" % name)
        out[name] = arr
    return out


def check_contract(paths, bodies, envelope):
    """Rules 1 to 5. bodies: name -> Manifold in supplied frame. Returns a list of
    format messages; empty means the contract holds."""
    msgs = []
    for name in C.BODY_ORDER:
        P = paths[name]
        V = verts(bodies[name])
        R, t = P[:, :3, :3], P[:, :3, 3]
        if np.abs(P[:, 3, :] - np.array([0, 0, 0, 1.0])).max() > C.ROT_TOL:
            msgs.append("%s: last row of a matrix is not 0 0 0 1" % name)
            continue
        rtr = np.einsum("nji,njk->nik", R, R) - np.eye(3)
        det = np.linalg.det(R)
        bad = np.nonzero((np.abs(rtr).max(axis=(1, 2)) > C.ROT_TOL) | (np.abs(det - 1) > C.ROT_TOL))[0]
        if len(bad):
            msgs.append("%s: pose %d is not a proper rotation plus translation" % (name, bad[0]))
            continue
        W = np.einsum("nij,vj->nvi", R, V) + t[:, None, :]          # poses x verts x 3
        step = np.linalg.norm(W[1:] - W[:-1], axis=2).max(axis=1)
        bad = np.nonzero(step > C.MAX_STEP + 1e-9)[0]
        if len(bad):
            msgs.append("%s: a vertex moves %.4f between poses %d and %d (limit %.2f)"
                        % (name, step[bad[0]], bad[0], bad[0] + 1, C.MAX_STEP))
        if name in C.FIXED_FINAL and np.abs(P[-1] - np.eye(4)).max() > C.FINAL_POSE_TOL:
            msgs.append("%s: last pose is not the fixed final pose (identity)" % name)
        if ivol(apply(bodies[name], P[0]), envelope) > 1e-9:
            msgs.append("%s: first pose is not wholly outside the envelope" % name)
        c = V.mean(axis=0)
        d = np.linalg.norm((R[0] @ c + t[0]) - (R[-1] @ c + t[-1]))
        if d < C.START_MIN_DIST:
            msgs.append("%s: first pose is %.3f from the last pose (minimum %.1f)" % (name, d, C.START_MIN_DIST))
    return msgs


def replay(moving, poses, placed):
    """Rule 6. placed: name -> Manifold already in the world. Returns the worst
    intersection volume, its pose index and the body it was with."""
    worst = (0.0, -1, None)
    for i, T in enumerate(poses):
        mv = apply(moving, T)
        for pname, pm in placed.items():
            v = ivol(mv, pm)
            if v > worst[0]:
                worst = (v, i, pname)
    return {"worst_volume": worst[0], "pose_index": worst[1], "with": worst[2]}
