"""Keyless v2 reference: crown-winding works in workstream B's watch frame, sized from DS-101..501.

    python3 spikes/keyless/reference_v2.py OUT --ref REF_JOB [--check] [--grade] [--set NAME=VALUE ...]

REF_JOB is B's job reference delivery (`python3 solution/reference_watch.py REF_JOB --job`). Writes:
  OUT/parts/<name>.stl        the keyless parts in B's frame (mm, +z the dial side, barrel axis x = y = 0)
  OUT/keyless_section.json    the `keyless` section for B's movement.json (B's frame), with the sizing record
  OUT/sizing_v2.json          every sizing choice with its datasheet cell and the margin it leaves
--check   collision table of every keyless part against every part of B's delivery (the barrel as its two
          bodies), plus AT-0 (rest overlap, held, bounds) on the joined model with main's engine
--grade   the full keyless acceptance AT-0..AT-6 with main's unmodified engine.py and grade.py (one worker)
Both checks build a temporary submission in the keyless frame V (below) and patch only grade.py's constants
module in memory (frame, PULL 1.294, capacity 4.9 turns); engine.py and grade.py are not edited.

Frames. B: as above. V (the keyless v1 frame): x along the stem from the case centre's foot outwards, z_V =
5.5 - z_B (so the crown wheel is "above" the stem in V, as in v1, and on B's train side). p_B = Rz(THETA) .
diag(1, -1, -1) . p_V + (cc_x, cc_y, 5.5), a proper rotation, so v1's senses carry over unchanged: forward
crown = clockwise seen from outside, winding = anticlockwise about +z_V = clockwise seen from B's dial side.

Architecture (Grossmann's: winding pinion, crown wheel, ratchet, click; sliding pinion with Breguet teeth;
two setting wheels): stem -> winding pinion (12, face module 0.2) -> crown wheel (28-tooth face ring, 24-tooth
spur, inward of the winding pinion, its axis on the stem line) -> intermediate wheel (12) -> ratchet (36, on
the arbor's square) with a 24-tooth click ring and a sprung click; position 2: sliding pinion (12) -> setting
wheel (28-tooth face ring, 16-tooth spur) -> setting idler (16) -> B's hour wheel (48) -> minute wheel.
"""
import json
import math
import os
import sys

import numpy as np
import manifold3d as m3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import constants as C  # noqa: E402
import gears as G  # noqa: E402
import shapes as S  # noqa: E402
import reference as R1  # noqa: E402  (v1: Breguet teeth builder only)

S_SCALE = 1.617                 # one demonstration scale (DS-101 section 1, Decisions 14:45)

# ---------------------------------------------------------------- parameters (every one recorded in sizing)
P = dict(
    # B's supplied barrel (geometry/watch.py at 51568b7; kept as parameters, defaults = B's new chamber)
    chamber_inner_d=12.12, core_r=2.02, square_side=1.4, square_z=(3.3, 4.9),
    # stem line: radial from B's case centre, at z 5.5 in the bridge's thickness, through a gap between bars
    theta_deg=66.0, z_stem=5.5,
    t_wc=10.75,                  # winding pinion's centre along the stem from the case centre
    # winding train
    m_face=0.2, z_pinion=12, z_face=28,         # winding / sliding pinion, crown and setting face rings
    m_wind=0.2 * S_SCALE, z_ratchet=36, z_crown_spur=24, z_inter=12,
    z_ratchet_spur=(3.31, 3.7), z_crown_spur_z=(3.75, 4.03), z_click_ring=(4.25, 4.55),
    click_ring=(24, 3.19, 3.70), click_angle_deg=150.0,
    # setting train
    m_set=0.2, z_set_spur=16, z_set_idler=24, z_hour=48, hour_layer=(7.6, 8.4),
    # stem and crown
    square_af=0.809,            # DS-401 Table 3 VM-ST-090-050-DS
    stem_r=0.467, crown_d=6.47, crown_len=1.29, crown_gap=0.16,
    pull=1.294, collar_gap=0.2,  # lost motion stem -> sliding pinion: groove clearance + finger gap in the neck
    stem_in_r=0.38,             # inner pivot: passes the sliding pinion's square bore (stem inserted from outside)
    groove_r=0.35, groove_c=0.015, finger_w=0.2, neck_r=0.85,     # yoke: stem groove, finger, pinion neck
    spur_chamfer=0.0,           # cone on the sliding pinion's leading tooth ends (entry into the setting wheel)
    breguet_refine=0.03,        # facet length of the Breguet teeth's warp (v1: 0.03)
    yoke_y=(1.5, 2.9), yoke_z=(-0.3, 0.45), stud_r=0.25, guide_r=0.6,
    breguet_n=8, breguet_h=0.2, clear=0.012,
    # pivots (DS-301 Table 3 bushings)
    bore_crown=0.647, bore_inter=0.647, bore_click=0.485, bore_set=0.485,
    plate_z=(4.6, 5.0),         # keyless bridge under B's bridge (touches its underside)
)
K_V1 = P["m_face"] / 0.15       # v1's stem and pinion details (module 0.15) scaled to module 0.2
BL = 0.004

# ---------------------------------------------------------------- datasheet cells (exact values as printed)
CELLS = {
    "DS-101 T1 L": dict(h=0.78, t=0.162, L=437, D=12.1, src="DS-101 section 3 Table 1, row L (scaled columns)"),
    "DS-101 T2 L M_el": dict(v=8.4, src="DS-101 section 4 Table 2, row L, M_el (N·mm)"),
    "DS-101 T2a slip": dict(v=70.1, src="DS-101 section 4a Table 2a, 'Slipping torque of the bridle (min. to max.)', This series, upper end (maker's limit); also B's stated design load for the train (Decisions 20:36)"),
    "DS-101 T3 L": dict(r=2.02, N=4.9, h=40, src="DS-101 section 5 Table 3, row L, r = D/6, N, run time"),
    "DS-101 Note 1": dict(src="DS-101 Notes 1: fit a spring only in a barrel of its listed inner diameter"),
    "DS-201 s8 steel": dict(v=725.0, src="DS-201 section 8, Steel AD-C100-HT, 1.000 to < 1.575 mm, Allowable (MPa) (lowest steel row)"),
    "DS-201 s8 brass": dict(v=110.0, src="DS-201 section 8, Brass CW614N, Allowable (MPa)"),
    "DS-201 T7 mu": dict(v=0.51, src="DS-201 section 7 Table 7, Brass on steel, clean and dry, static"),
    "DS-301 5.1": dict(v=0.016, d=0.226, src="DS-301 section 5.1, hole = pivot + 0.016 mm at 0.226 mm, proportional"),
    "DS-301 T3/T4 RL-B-40-150-55-DS": dict(hole=0.647, F=63.3, src="DS-301 Table 3 and section 5.3 Table 4"),
    "DS-301 T3/T4 RL-B-30-100-30-DS": dict(hole=0.485, F=25.9, src="DS-301 Table 3 and section 5.3 Table 4"),
    "DS-401 T1 VM-CR-400-R-DS": dict(d=6.47, src="DS-401 section 3 Table 1"),
    "DS-401 T2 travel": dict(v=1.29, src="DS-401 section 4 Table 2, 'Stem travel between adjacent positions', this series"),
    "DS-401 T2 gap": dict(v=0.16, src="DS-401 section 4 Table 2, gap crown to case middle, at most"),
    "DS-401 T3 VM-ST-090-050-DS": dict(a=0.809, T_rec=46.0, T_y=92.1, src="DS-401 section 5 Table 3"),
    "DS-401 T4 withstand": dict(v=179.3, src="DS-401 section 5a Table 4, torque at the crown against a fully wound spring"),
    "DS-501 T4": dict(src="DS-501 section 5 Table 4, T_rec = min(4.20 D, 32) N·mm"),
}


# ---------------------------------------------------------------- frames
def frame():
    th = math.radians(P["theta_deg"])
    c, s = math.cos(th), math.sin(th)
    M = np.array([[c, s, 0.0], [s, -c, 0.0], [0.0, 0.0, -1.0]])
    return M


CC = (4.0391, -9.6417)           # B's reference case centre (movement.json), overwritten from REF


def v2b_T():
    M = frame()
    t = np.array([CC[0], CC[1], P["z_stem"]])
    return np.hstack([M, t[:, None]])


def b2v_T():
    M = frame()
    t = np.array([CC[0], CC[1], P["z_stem"]])
    return np.hstack([M.T, (-M.T @ t)[:, None]])


def tf(man, T):
    return man.transform(np.asarray(T).tolist())


def pt(T, p):
    T = np.asarray(T)
    return T[:, :3] @ np.asarray(p, float) + T[:, 3]


def vec(T, v):
    return np.asarray(T)[:, :3] @ np.asarray(v, float)


def zv(z_b):
    return P["z_stem"] - z_b


def circles(p, rp, q, rq):
    p, q = np.asarray(p, float), np.asarray(q, float)
    d = np.linalg.norm(q - p)
    if not abs(rp - rq) <= d <= rp + rq:
        raise ValueError("no mesh position: %.3f apart, radii %.3f and %.3f" % (d, rp, rq))
    a = (rp * rp - rq * rq + d * d) / (2 * d)
    h = math.sqrt(max(rp * rp - a * a, 0.0))
    e = (q - p) / d
    n = np.array([-e[1], e[0]])
    return [p + a * e + h * n, p + a * e - h * n]


# ---------------------------------------------------------------- sizing from the datasheets
def T_rec(D):
    return min(4.20 * D, 32.0)


def sizing(Y):
    """Every sizing number, with the cell it comes from and the margin it leaves. Y: Lewis form factors
    (geometry/data/lewis_y.json, the table B's strength check uses)."""
    out = {"cells": {k: v["src"] for k, v in CELLS.items()}, "checks": []}
    ok = True

    def chk(name, value, limit, rel, cell, note=""):
        nonlocal ok
        good = value <= limit if rel == "<=" else value >= limit
        ok = ok and good
        out["checks"].append(dict(name=name, value=round(value, 4), limit=limit, rel=rel, ok=good, cell=cell,
                                  note=note))

    # mainspring
    L = CELLS["DS-101 T1 L"]
    chk("spring L height fits the 1.0-tall drum", L["h"], 1.0, "<=", "DS-101 T1 L")
    chk("spring L listed barrel D vs chamber inner diameter (Note 1), |difference|", abs(L["D"] - P["chamber_inner_d"]),
        0.05, "<=", "DS-101 Note 1", "chamber 12.12 = 7.5 x 1.617 (L's 1:1 D); the table rounds to 12.1")
    chk("arbor core radius = D/6", abs(P["core_r"] - P["chamber_inner_d"] / 6), 1e-6, "<=", "DS-101 T3 L")
    N = CELLS["DS-101 T3 L"]["N"]
    chk("reserve from full wind, less 30 deg click run-back (h)", (N - 30 / 360) * 8, 38.0, ">=", "DS-101 T3 L",
        "AT-3: (N - run-back) x 8 h; run time 40 h in the cell")
    T_des = CELLS["DS-101 T2a slip"]["v"]
    out["design_torque_nmm"] = T_des
    out["design_torque_note"] = ("L is a manual (M-end) spring: no bridle. Its first-yield torque M_el = 8.4 N·mm "
                                 "(DS-101 T2), but DS-101 Note 2 says M_el is not an upper bound and that the "
                                 "highest torque the sheet states for the 11 1/2''' class is the slipping torque "
                                 "70.1 N·mm. The teeth are sized for 70.1 (the larger); margins at 8.4 follow.")
    # train
    mw = P["m_wind"]
    zR, zc, zi, zf, zp = P["z_ratchet"], P["z_crown_spur"], P["z_inter"], P["z_face"], P["z_pinion"]
    ratio = (zR / zc) * (zf / zp)                       # the intermediate wheel is an idler
    out["crown_turns_per_arbor_turn"] = ratio
    chk("crown turns per arbor turn (rig band 3..12)", ratio, 3.0, ">=", "constants.WIND_BAND")
    chk("crown turns per arbor turn (rig band 3..12), upper", ratio, 12.0, "<=", "constants.WIND_BAND")
    Tc = T_des / ratio
    out["crown_torque_nmm"] = Tc
    chk("winding torque at the crown <= T_rec(crown D)", Tc, T_rec(P["crown_d"]), "<=", "DS-501 T4",
        "crown VM-CR-400-R-DS, D 6.47: T_rec = 4.20 x 6.47 = %.1f N·mm" % T_rec(P["crown_d"]))
    chk("winding torque at the crown <= stem square recommended max", Tc, 46.0, "<=", "DS-401 T3 VM-ST-090-050-DS")
    chk("finger limit T_rec on the crown <= stem square recommended max", T_rec(P["crown_d"]), 46.0, "<=",
        "DS-401 T3 VM-ST-090-050-DS")
    # the yoke's groove: its core carries the crown torque at the shear the DS-401 T3 square is rated at
    tau_sq = 46.0 / (0.208 * P["square_af"] ** 3)
    Tg = math.pi * P["groove_r"] ** 3 * tau_sq / 2
    out["stem_groove"] = dict(core_r=P["groove_r"], tau_mpa=tau_sq, T_capacity_nmm=Tg)
    chk("stem groove core: torsion capacity >= finger limit T_rec on the crown", Tg, T_rec(P["crown_d"]), ">=",
        "DS-401 T3 VM-ST-090-050-DS (46 N·mm on af 0.809: tau = 46 / (0.208 af^3)) and DS-501 T4",
        "core r 0.35: pi r^3 tau / 2")
    # Lewis: sigma = F / (b m Y), F = T / r at the mesh (B's strength method, geometry/watch.py strength_run)
    allow = CELLS["DS-201 s8 steel"]["v"]
    brass = CELLS["DS-201 s8 brass"]["v"]
    rR = mw * zR / 2
    F_r = T_des / rR                                    # ratchet / intermediate / crown spur: same tangential force
    bR = P["z_ratchet_spur"][1] - P["z_ratchet_spur"][0]
    bC = P["z_crown_spur_z"][1] - P["z_crown_spur_z"][0]
    lew = []
    for name, z, b in (("ratchet", zR, bR), ("intermediate (ratchet side)", zi, bR),
                       ("intermediate (crown side)", zi, bC), ("crown wheel spur", zc, bC)):
        sig = F_r / (b * mw * Y[z])
        lew.append(dict(gear=name, teeth=z, module=mw, face=b, Y=Y[z], force_n=F_r, sigma_mpa=sig))
    Tcw = T_des * zc / zR                               # torque on the crown wheel
    R_f = P["m_face"] * zf / 2
    F_f = Tcw / R_f
    b_f = 0.7                                           # face ring width 2 x 0.35
    for name, z in (("winding pinion (face mesh)", zp), ("crown wheel face ring (as a rack, Y of 28)", zf)):
        sig = F_f / (b_f * P["m_face"] * Y[z])
        lew.append(dict(gear=name, teeth=z, module=P["m_face"], face=b_f, Y=Y[z], force_n=F_f, sigma_mpa=sig))
    for e in lew:
        e["margin_steel"] = allow / e["sigma_mpa"] - 1
        e["brass_would_pass"] = e["sigma_mpa"] <= brass
        e["sigma_at_M_el"] = e["sigma_mpa"] * CELLS["DS-101 T2 L M_el"]["v"] / T_des
        chk("Lewis %s <= steel allowable" % e["gear"], e["sigma_mpa"], allow, "<=", "DS-201 s8 steel")
    out["lewis"] = lew
    out["materials"] = {"all winding and setting wheels, pinions, ratchet, click": "AD-C100-HT",
                        "why": "brass (110 MPa) fails the ratchet and pinions at 70.1 N·mm; steel passes"}
    # Breguet teeth: crown torque on n teeth at mean radius, one tooth taken as carrying it all
    rin, rout = 0.45 * K_V1, 0.85 * K_V1
    rm = (rin + rout) / 2
    F_b = Tc / rm
    pitch = 2 * math.pi * rm / P["breguet_n"]
    sig_b = 6 * F_b * P["breguet_h"] / ((rout - rin) * pitch ** 2)
    out["breguet"] = dict(n=P["breguet_n"], h=P["breguet_h"], r=(rin, rout), force_n=F_b, sigma_mpa=sig_b,
                          method="cantilever 6 F h / (w p^2), one tooth, root = one pitch (sawtooth)")
    chk("Breguet tooth bending <= steel allowable", sig_b, allow, "<=", "DS-201 s8 steel")
    # click ring tooth and click tip (same force: the arbor torque at the click ring's tip radius)
    zk, rk0, rk1 = P["click_ring"]
    F_k = T_des / rk1
    pk = 2 * math.pi * rk1 / zk
    bk = P["z_click_ring"][1] - P["z_click_ring"][0]
    sig_k = 6 * F_k * (rk1 - rk0) / (bk * pk ** 2)
    out["click"] = dict(force_n=F_k, sigma_tooth_mpa=sig_k)
    chk("click ring tooth bending <= steel allowable", sig_k, allow, "<=", "DS-201 s8 steel")
    # pivots: radial load from the meshes vs DS-301 Table 4
    F_crown = math.hypot(F_r, F_f)
    out["pivots"] = {
        "crown wheel": dict(load_n=F_crown, bushing="RL-B-40-150-55-DS", F_max=63.3),
        "intermediate wheel": dict(load_n=2 * F_r, bushing="RL-B-40-150-55-DS", F_max=63.3),
        "click": dict(load_n=F_k, bushing="RL-B-30-100-30-DS", F_max=25.9),
        "setting wheels": dict(load_n=None, bushing="RL-B-30-100-30-DS", F_max=25.9,
                               note="setting loads are the hands' friction only (not rated by the rig)"),
    }
    for k, v in out["pivots"].items():
        if v["load_n"] is not None:
            chk("pivot radial load, %s" % k, v["load_n"], v["F_max"], "<=", "DS-301 T3/T4 " + v["bushing"])
    cl = CELLS["DS-301 5.1"]
    out["pivot_clearance_rule"] = "diametral clearance = 0.016 x (hole / 0.226), DS-301 5.1 applied proportionally"
    # withstand case (information, not a design requirement of the brief)
    W = CELLS["DS-401 T4 withstand"]["v"]
    out["withstand_case"] = dict(crown_torque=W, arbor_torque=W * ratio,
                                 ratchet_sigma=lew[0]["sigma_mpa"] * W * ratio / T_des,
                                 stem_square_T_yield=92.1,
                                 note="DS-401 Table 4's 179.3 N·mm withstand is not met: the VM-ST-090-050-DS square "
                                      "yields at 92.1 and the teeth would see about %.0fx the design load. No square "
                                      "that fits the 1.4-tip pinions reaches it; recorded as a known limit."
                                      % (W * ratio / T_des))
    out["all_ok"] = ok
    _ = cl
    return out


# ---------------------------------------------------------------- geometry in frame V
def layout(ref_axes):
    """Axes and stations in V. ref_axes: B's mobile axes {name: (x, y)} and the case centre."""
    TB = b2v_T()
    th = math.radians(P["theta_deg"])
    O = pt(TB, (0, 0, P["z_stem"]))[:2]                 # barrel axis in V
    Rf = P["m_face"] * P["z_face"] / 2
    twc = P["t_wc"]
    tK = twc - Rf                                       # crown wheel inward of the winding pinion
    K = np.array([tK, 0.0])
    mw = P["m_wind"]
    rc, ri, rR = mw * P["z_crown_spur"] / 2, mw * P["z_inter"] / 2, mw * P["z_ratchet"] / 2
    cand = circles(K, rc + ri, O, rR + ri)
    I = max(cand, key=lambda q: abs(q[1]))             # the root away from the stem line (its post hangs from
                                                        # the keyless bridge beside the pinions' path)
    # stem stations (v1 x K_V1 from the winding pinion's centre)
    k = K_V1
    xw0, xw1 = twc - 0.25 * k, twc + 0.25 * k
    bx0 = xw1 + 0.35 * k
    bx1 = bx0 + P["breguet_h"]
    sx0 = bx1 + P["clear"]
    st0 = bx1 + 0.8 * k
    st1 = st0 + 0.5 * k
    travel = P["pull"] - P["collar_gap"]
    tsp2 = (st0 + st1) / 2 + travel
    Rs = Rf
    tS = tsp2 - Rs                                      # setting wheel inward of the pulled sliding pinion
    S1 = np.array([tS, 0.0])
    H = pt(TB, (*ref_axes["hour_wheel"], 0))[:2]
    r1, r2, rh = P["m_set"] * P["z_set_spur"] / 2, P["m_set"] * P["z_set_idler"] / 2, P["m_set"] * P["z_hour"] / 2
    cand = circles(S1, r1 + r2, H, rh + r2)
    Mw = pt(TB, (*ref_axes["minute_wheel"], 0))[:2]
    S2 = max(cand, key=lambda q: np.linalg.norm(q - Mw))  # the root away from B's minute wheel
    return dict(O=O, K=K, I=I, S1=S1, S2=S2, H=H, Rf=Rf, Rs=Rs, xw0=xw0, xw1=xw1, bx0=bx0, bx1=bx1, sx0=sx0,
                st0=st0, st1=st1, travel=travel, tsp2=tsp2, twc=twc, tK=tK, rc=rc, ri=ri, rR=rR, r1=r1, r2=r2)


def clear_phase(make, others, n=40):
    """make(phase_fraction) -> solid; returns the solid at the middle of the longest clear run of phases."""
    ok = []
    for j in range(n):
        g = make(j / n)
        v = sum((g ^ o).volume() for o in others)
        ok.append(v < 1e-6)
    if not any(ok):
        raise RuntimeError("no clear phase")
    best, run, start = (0, 0), 0, 0
    for j in range(2 * n):
        if ok[j % n]:
            if run == 0:
                start = j
            run += 1
            if run > best[0] and run <= n:
                best = (run, start)
        else:
            run = 0
    mid = (best[1] + (best[0] - 1) / 2.0) % n
    return make(mid / n), mid / n


def _exact():
    import exact_v2
    return exact_v2


def _warp_cyl_x(man, r_mean):
    """v1's warp (reference.warp_cyl_x) with the facet length as a parameter: coarser facets give a STEP file with
    fewer flat triangles."""
    def f(v):
        u, x, r = v
        t = u / r_mean
        return (x, r * math.cos(t), r * math.sin(t))
    out = man.refine_to_length(P["breguet_refine"]).warp(f)
    if out.volume() < 0 or out.status() != m3.Error.NoError:
        raise RuntimeError("warp failed")
    return out


EXACT = {}     # part -> function returning its B-rep in V (exact_v2): the parts whose surfaces are not planar facets


def build(bV):
    R1.warp_cyl_x = _warp_cyl_x
    EXACT.clear()
    """bV: B's parts in V (for phasing): {'hour_wheel': solid}. Returns (parts in V, spec in V, layout)."""
    Lo = layout(AXES)
    k = K_V1
    parts, fixed = {}, []
    mf, zp, zf = P["m_face"], P["z_pinion"], P["z_face"]
    rp = mf * zp / 2
    zt, zr = rp - mf, rp + 1.25 * mf                    # face ring tip plane and root, from the stem axis
    O, K, I, S1, S2 = Lo["O"], Lo["K"], Lo["I"], Lo["S1"], Lo["S2"]
    mw = P["m_wind"]
    zRs = sorted(zv(z) for z in P["z_ratchet_spur"])
    zCs = sorted(zv(z) for z in P["z_crown_spur_z"])
    zKr = sorted(zv(z) for z in P["z_click_ring"])
    zH = sorted(zv(z) for z in P["hour_layer"])
    z_plate = sorted(zv(z) for z in P["plate_z"])       # (0.5, 0.9)
    o = {"breguet_n": P["breguet_n"], "breguet_steep": 0.03, "clear": P["clear"]}

    # ---- ratchet: 36-tooth spur on the square, click ring above (barrel mobile, with B's arbor)
    TBV = b2v_T()
    sq = P["square_side"] / 2
    square_V = tf(S.box([-sq, -sq, P["square_z"][0] - 0.01], [sq, sq, P["square_z"][1] + 0.01]), TBV)
    ratchet = G.spur(P["z_ratchet"], mw, zRs[0], zRs[1], thin=BL).translate([O[0], O[1], 0])
    ratchet = S.union([ratchet, S.cyl_z(O[0], O[1], zKr[0], zRs[1], 1.3, 96)])
    kz, kr0, kr1 = P["click_ring"]
    sc = kr1 / 2.9                                      # v1 ring 2.5/2.9 and its click, scaled in plan
    ring_v1 = S.ratchet_wheel(kz, 2.5, 2.9, 0.0, 1.0)
    ck_v1, piv = S.click(kz, 2.5, 2.9, 0.0, 1.0)
    al = P["click_angle_deg"]

    def plan(mm, z0, z1):
        return mm.scale([sc, sc, z1 - z0]).translate([0, 0, z0]).rotate([0, 0, al]).translate([O[0], O[1], 0])
    ring_k = plan(ring_v1.rotate([0, 0, 180]), zKr[0], zKr[1])
    ratchet = S.union([ratchet, ring_k]) - square_V
    parts["ratchet"] = ratchet
    # click: v1 construction (pivot on the tangent through the tip), opened 1.5 degrees, scaled, turned
    ck = ck_v1.rotate([0, 0, 180])
    pv0 = np.array([-piv[0], -piv[1]])
    ck = ck - S.cyl_z(pv0[0], pv0[1], -1, 2, 0.2425 / sc, 48)
    ck = ck.translate([-pv0[0], -pv0[1], 0]).rotate([0, 0, -1.5]).translate([pv0[0], pv0[1], 0])
    ck = plan(ck, zKr[0], zKr[1])
    a = math.radians(al)
    pv = O + sc * np.array([math.cos(a) * pv0[0] - math.sin(a) * pv0[1], math.sin(a) * pv0[0] + math.cos(a) * pv0[1]])
    parts["click"] = ck
    r_ck = 0.2425 - 0.5 * 0.016 * (0.485 / 0.226)       # DS-301 5.1, proportional diametral clearance
    parts["click_post"] = S.union([S.cyl_z(pv[0], pv[1], z_plate[1], zKr[1] + 0.12, r_ck, 48),
                                   S.cyl_z(pv[0], pv[1], zKr[1] + 0.02, zv(3.75), 0.5, 48)])   # head down to 0.05 over the ratchet: thicker than
    # B's HOLD_SHIFT (0.485), so the held test's jump lands in it
    fixed.append("click_post")

    # ---- intermediate wheel (12, on the ratchet's and crown spur's layers)
    zI = (min(zRs[0], zCs[0]), max(zRs[1], zCs[1]))
    r_bI = P["bore_inter"] / 2
    r_pI = r_bI - 0.5 * 0.016 * (P["bore_inter"] / 0.226)

    def inter(f):
        g = G.spur(P["z_inter"], mw, zI[0], zI[1], thin=BL, phase=2 * math.pi * f / P["z_inter"])
        return g.translate([I[0], I[1], 0])
    gI, _ = clear_phase(inter, [ratchet])
    gI = gI - S.cyl_z(I[0], I[1], zI[0] - 1, zI[1] + 1, r_bI, 48)
    parts["intermediate_wheel"] = gI
    parts["intermediate_post"] = S.union([S.cyl_z(I[0], I[1], z_plate[1], zI[1] + 0.09, r_pI, 48),
                                          S.cyl_z(I[0], I[1], zI[1] + 0.02, zI[1] + 0.09, 0.6, 48)])
    fixed.append("intermediate_post")

    # ---- crown wheel: face ring (28) facing the winding pinion, spur (24) meshing the intermediate wheel
    R = Lo["Rf"]
    ring = G.face_gear(zf, zp, mf, (0.0, 0.0), R - 0.35, R + 0.35, zr, zt, 0.0, cutter_thin=-BL, steps_per_pitch=16)
    ring = ring.rotate([0, 0, 180])                     # pinion on the +x side (crown wheel inward)
    web = S.cyl_z(0, 0, zr - 0.01, zCs[0] + 0.01, R + 0.35, 128)
    r_bK = P["bore_crown"] / 2
    r_pK = r_bK - 0.5 * 0.016 * (P["bore_crown"] / 0.226)
    hub = S.cyl_z(0, 0, zr - 0.01, zCs[1], 1.2, 64)

    def crown(f):
        sp = G.spur(P["z_crown_spur"], mw, zCs[0], zCs[1], thin=BL)
        g = S.union([ring, web, hub, sp]).rotate([0, 0, 360.0 * f / P["z_crown_spur"]])
        return g.translate([K[0], K[1], 0])
    # the crown wheel turns as one: choose its turn so the spur clears the intermediate wheel
    cw, fK = clear_phase(crown, [gI])
    cw = cw - S.cyl_z(K[0], K[1], 0, 3, r_bK, 48)
    parts["crown_wheel"] = cw

    def crown_exact(fK=fK, sp=(G.spur(P["z_crown_spur"], mw, zCs[0], zCs[1], thin=BL)
                               .rotate([0, 0, 360.0 * fK / P["z_crown_spur"]]).translate([K[0], K[1], 0]))):
        # B-rep: the face ring lofted (exact_v2), web, hub and bore as true cylinders (web 0.001 inside the ring's
        # rim so no two faces coincide), the spur's planar faces from the mesh
        X = _exact()
        rg = X.face_ring(X.face_gear_gap(zf, zp, mf, R - 0.35, R + 0.35, zr, zt, -BL, 200), zf, R - 0.35, R + 0.35,
                         zt, zr)[0]
        rg = X.moved(X.moved(X.moved(rg, X.rot_z(180)), X.rot_z(360.0 * fK / P["z_crown_spur"])),
                     X.translate(K[0], K[1], 0))
        sh = X.fuse(mesh_to_shape(sp)[0], rg)
        sh = X.fuse(sh, X.cyl_z(K[0], K[1], zr - 0.01, zCs[0] + 0.01, R + 0.349))
        sh = X.fuse(sh, X.cyl_z(K[0], K[1], zr - 0.01, zCs[1], 1.2))
        return X.one_solid(X.cut(sh, X.cyl_z(K[0], K[1], 0, 3, r_bK)))
    EXACT["crown_wheel"] = crown_exact
    parts["crown_post"] = S.union([S.cyl_z(K[0], K[1], z_plate[1], zCs[1] + 0.12, r_pK, 48),
                                   S.cyl_z(K[0], K[1], zCs[1] + 0.02, zCs[1] + 0.12, 0.6, 48)])
    fixed.append("crown_post")

    # ---- winding pinion (spur teeth phased into the crown ring, Breguet teeth facing +x)
    xw0, xw1, bx0, bx1 = Lo["xw0"], Lo["xw1"], Lo["bx0"], Lo["bx1"]

    phiK = 2 * math.pi * fK / P["z_crown_spur"]          # the crown wheel's turn; the pinion follows it

    def wpin(sg):
        return G.pinion_along_x(zp, mf, xw0, xw1, 0.0, 0.0, phase=sg * phiK * zf / zp)
    wp = min((wpin(sg) for sg in (1, -1)), key=lambda g: (g ^ cw).volume())
    hubw = S.cyl_x(0, 0, xw1 - 0.01, bx0 + 0.01, 0.68 * k, 64)
    wteeth = R1.breguet(o, bx0, bx1, 0.45 * k, 0.85 * k, sliding=False)
    bore_w = S.cyl_x(0, 0, xw0 - 1, bx1 + 1, P["stem_in_r"] + 0.026, 48)
    parts["winding_pinion"] = S.union([wp, hubw, wteeth]) - bore_w

    def wpin_exact(rest=S.union([wp, hubw]) - bore_w):
        X = _exact()
        t = X.breguet(o, bx0, bx1, 0.45 * k, 0.85 * k, sliding=False)   # inner radius 0.6 clears the bore
        return X.one_solid(X.fuse(mesh_to_shape(rest)[0], t))
    EXACT["winding_pinion"] = wpin_exact

    # ---- sliding pinion: Breguet teeth, square bore, spur teeth at its outer end
    sx0, st0, st1 = Lo["sx0"], Lo["st0"], Lo["st1"]
    steeth = R1.breguet(o, bx0 + P["clear"] / 2, sx0, 0.45 * k, 0.85 * k, sliding=True)
    body = S.cyl_x(0, 0, sx0 - 0.002, st0 + 0.01, 0.85 * k, 64)
    xn0, xn1 = sx0 + 0.2, st0 - 0.15                    # the neck the yoke's finger sits in
    neck = S.cyl_x(0, 0, xn0, xn1, 2.0, 64) - S.cyl_x(0, 0, xn0 - 0.01, xn1 + 0.01, P["neck_r"], 64)
    hsq = P["square_af"] / 2

    # ---- setting wheel (28 face ring over the pulled sliding pinion, 16 spur on the hour-wheel layer)
    Rs = Lo["Rs"]
    sring = G.face_gear(zf, zp, mf, (0.0, 0.0), Rs - 0.35, Rs + 0.35, zr, zt, 0.0, cutter_thin=-BL,
                        steps_per_pitch=16).mirror([0, 0, 1]).rotate([0, 0, 180])
    sweb = S.cyl_z(0, 0, -zr - 0.2, -zr + 0.01, Rs + 0.35, 128)
    shub = S.cyl_z(0, 0, zH[0], -zr + 0.01, 0.9, 64)
    r_bS = P["bore_set"] / 2
    r_pS = r_bS - 0.5 * 0.016 * (P["bore_set"] / 0.226)

    def sidle(f):
        g = G.spur(P["z_set_idler"], P["m_set"], zH[0], zH[1], thin=BL, phase=2 * math.pi * f / P["z_set_idler"])
        return g.translate([S2[0], S2[1], 0])
    g2, _ = clear_phase(sidle, [bV["hour_wheel"]])
    z_dial = zv(8.8)
    g2 = S.union([g2, S.cyl_z(S2[0], S2[1], zH[0], zH[1], 0.7, 48)]) - S.cyl_z(S2[0], S2[1], -5, 0, r_bS, 48)
    parts["setting_idler"] = g2
    # B's dial is a skeleton with nothing over S2: the idler sits on a seat on the keyless bridge and is held by a
    # headed post (a screw) put in through it after it; head 0.5 thick (> B's HOLD_SHIFT 0.485)
    parts["setting_idler_seat"] = S.cyl_z(S2[0], S2[1], zH[1] + 0.02, z_plate[0], 0.5, 48) \
        - S.cyl_z(S2[0], S2[1], zH[1], z_plate[0] + 0.1, r_pS + 0.005, 48)
    fixed.append("setting_idler_seat")
    parts["setting_idler_post"] = S.union([S.cyl_z(S2[0], S2[1], zH[0] - 0.02, z_plate[0], r_pS, 48),
                                           S.cyl_z(S2[0], S2[1], zH[0] - 0.52, zH[0] - 0.02, 0.5, 48)])
    fixed.append("setting_idler_post")

    def setw(f):
        sp = G.spur(P["z_set_spur"], P["m_set"], zH[0], zH[1], thin=BL)
        g = S.union([sring, sweb, shub, sp]).rotate([0, 0, 360.0 * f / P["z_set_spur"]])
        return g.translate([S1[0], S1[1], 0])
    sw, fS1 = clear_phase(setw, [g2])
    phiS = 2 * math.pi * fS1 / P["z_set_spur"]
    sw = sw - S.cyl_z(S1[0], S1[1], -5, 0, r_bS, 48)
    parts["setting_wheel"] = sw

    def setw_exact(fS1=fS1, sp=(G.spur(P["z_set_spur"], P["m_set"], zH[0], zH[1], thin=BL)
                                .rotate([0, 0, 360.0 * fS1 / P["z_set_spur"]]).translate([S1[0], S1[1], 0]))):
        X = _exact()     # as crown_exact
        rg = X.face_ring(X.face_gear_gap(zf, zp, mf, Rs - 0.35, Rs + 0.35, zr, zt, -BL, 200), zf, Rs - 0.35,
                         Rs + 0.35, zt, zr)[0]
        for M in (X.MIRROR_Z, X.rot_z(180), X.rot_z(360.0 * fS1 / P["z_set_spur"]), X.translate(S1[0], S1[1], 0)):
            rg = X.moved(rg, M)
        sh = X.fuse(mesh_to_shape(sp)[0], rg)
        sh = X.fuse(sh, X.cyl_z(S1[0], S1[1], -zr - 0.2, -zr + 0.01, Rs + 0.349))
        sh = X.fuse(sh, X.cyl_z(S1[0], S1[1], zH[0], -zr + 0.01, 0.9))
        return X.one_solid(X.cut(sh, X.cyl_z(S1[0], S1[1], -5, 0, r_bS)))
    EXACT["setting_wheel"] = setw_exact
    # no head under the setting wheel: its axis is over the winding pinion, which holds it from below
    parts["setting_post"] = S.union([S.cyl_z(S1[0], S1[1], z_dial, -zr - 0.05, r_pS, 48),
                                     S.cyl_z(S1[0], S1[1], z_dial, zH[0] - 0.02, 0.5, 48)])      # shoulder
    fixed.append("setting_post")

    def spin(sg):
        return G.pinion_along_x(zp, mf, st0, st1, 0.0, 0.0, phase=sg * phiS * zf / zp)
    tr = Lo["travel"]
    spur_t = min((spin(sg) for sg in (1, -1)), key=lambda g: (g.translate([tr, 0, 0]) ^ sw).volume())
    ch = P["spur_chamfer"]
    if ch > 0:      # leading (outer) ends of the teeth turned to a cone: radius 1.02 at st1, the tip radius ch inwards
        cone = m3.Manifold.cylinder(ch, 1.45, 1.02, 96).transform([[0, 0, 1, st1 - ch], [1, 0, 0, 0], [0, 1, 0, 0]])
        spur_t = spur_t ^ S.union([cone, S.cyl_x(0, 0, st0 - 1, st1 - ch + 0.001, 2.0, 96)])
    sp = S.union([steeth, body, spur_t])
    bore_s = S.cyl_x(0, 0, bx0 - 1, sx0 + 0.05, 0.62, 48)
    sq_s = S.box([sx0, -hsq - 0.013, -hsq - 0.013], [st1 + 1, hsq + 0.013, hsq + 0.013])
    sp = sp - neck - bore_s
    sp = sp - sq_s
    parts["sliding_pinion"] = sp

    def spin_exact(rest=S.union([body, spur_t]) - neck - bore_s - sq_s):
        X = _exact()
        t = X.breguet(o, bx0 + P["clear"] / 2, sx0, 0.45 * k, 0.85 * k, sliding=True)
        t = X.cut(X.cut(t, X.cyl_x(0, 0, bx0 - 1, sx0 + 0.05, 0.62)),
                  X.box([sx0, -hsq - 0.013, -hsq - 0.013], [st1 + 1, hsq + 0.013, hsq + 0.013]))
        return X.one_solid(X.fuse(mesh_to_shape(rest)[0], t))
    EXACT["sliding_pinion"] = spin_exact

    # ---- stem: round inner end, collar in the counterbore, square, round shaft, crown outside the case
    xa = sx0 + 0.1                                      # the square starts inside the sliding pinion
    t_face = 20.7 + P["crown_gap"]
    sq_end = st1 + tr + 0.3
    gc, fw = P["groove_c"], P["finger_w"]
    g0 = sq_end + 0.15
    g1 = g0 + fw + 2 * gc
    parts["stem"] = S.union([
        S.cyl_x(0, 0, xw0 - 1.0 * k, xa + 0.01, P["stem_in_r"], 48),
        S.box([xa, -hsq, -hsq], [sq_end, hsq, hsq]),
        S.cyl_x(0, 0, sq_end - 0.01, g0, P["stem_r"], 48),
        S.cyl_x(0, 0, g0 - 0.01, g1 + 0.01, P["groove_r"], 48),
        S.cyl_x(0, 0, g1, t_face + 0.01, P["stem_r"], 48),
        S.cyl_x(0, 0, t_face, t_face + P["crown_len"], P["crown_d"] / 2, 96),
    ])
    # stem bridge (inner bearing, holds the winding pinion axially) and stem guide (case tube side)
    parts["stem_bridge"] = S.box([xw0 - 0.5 * k, -0.8 * k, -0.9], [xw0 - 0.12 * k, 0.8 * k, z_plate[0]]) \
        - S.cyl_x(0, 0, xw0 - 2, xw0 + 1, P["stem_in_r"] + 0.026, 48)
    fixed.append("stem_bridge")
    parts["stem_guide"] = S.box([19.0, -0.6 * k, -0.8 * k], [19.6, 0.6 * k, 0.8 * k]) \
        - S.cyl_x(0, 0, 18, 21, P["guide_r"], 48)
    fixed.append("stem_guide")

    # ---- keyless bridge under B's bridge: carries the crown, intermediate and click posts and the stem bridge
    # ---- yoke: a slide on two shouldered studs; one finger in the stem's groove, one in the sliding pinion's neck.
    # Pulling the stem, the groove's inner wall drives the yoke out and its finger draws the pinion out of the
    # winding pinion's Breguet teeth onto the setting wheel; pushing in, the outer wall brings it back and the
    # pinion's spring follows. Put in after the stem (its fingers drop into the groove and the neck from the dial side).
    yl, yh = P["yoke_y"]
    yz0, yz1 = P["yoke_z"]
    fA0, fA1 = g0 + gc, g1 - gc
    fB1 = xn1 - (P["collar_gap"] - gc)
    fB0 = fB1 - fw
    ys = -(yl + yh) / 2
    xb0 = fB0 - 0.1
    xs0 = xb0 + 0.2
    sa = xs0 + P["stud_r"] + P["pull"] + 0.1
    sb = sa + 1.8
    xs1 = sb + P["stud_r"] + 0.05
    xb1 = xs1 + 0.2
    wsl = P["stud_r"] + 0.02
    yoke = S.union([S.box([xb0, -yh, yz0], [xb1, -yl, yz1]),
                    S.box([fA0, -yl - 0.01, yz0], [fA1, -(P["groove_r"] + 0.02), yz1]),
                    S.box([fB0, -yl - 0.01, yz0], [fB1, -(P["neck_r"] + 0.04), yz1])])
    yoke = yoke - S.box([xs0, ys - wsl, yz0 - 1], [xs1, ys + wsl, yz1 + 1])
    parts["yoke"] = yoke
    for nm, xs in (("yoke_stud_a", sa), ("yoke_stud_b", sb)):
        parts[nm] = S.union([S.cyl_z(xs, ys, yz0 - 0.05, z_plate[0], P["stud_r"], 48),
                             S.cyl_z(xs, ys, yz0 - 0.15, yz0 - 0.05, 0.45, 48)])
        fixed.append(nm)

    Bbar = bar_point(K)
    pts = [K, I, pv, np.array([xw0 - 0.3 * k, 0.0]), Bbar, np.array([sa, ys]), np.array([sb, ys])]
    discs = [S.cyl_z(p[0], p[1], z_plate[0], z_plate[1], 0.9, 48) for p in pts]
    plate = m3.Manifold.batch_hull(discs)
    keep = S.box([xw0 - 0.1 * k, -1.65, z_plate[0] - 1], [30, 1.65, z_plate[1] + 1])      # the pinions' path
    plate = plate - keep - S.cyl_z(O[0], O[1], -5, 5, 1.1, 64)
    for n_ in ("third", "centre"):
        a_ = pt(b2v_T(), (*AXES[n_], 0))[:2]
        plate = plate - S.cyl_z(a_[0], a_[1], -5, 5, 0.8, 48)
    parts["keyless_bridge"] = plate
    fixed.append("keyless_bridge")

    mobiles = {
        "stem": {"kind": "stem", "parts": ["stem"]},
        "winding_pinion": {"kind": "free", "dof": "rot", "point": [0, 0, 0], "direction": [1, 0, 0],
                           "parts": ["winding_pinion"]},
        "sliding_pinion": {"kind": "spring", "dof": "slide", "direction": [1, 0, 0], "on_stem": True, "rest": -1,
                           "parts": ["sliding_pinion"]},
        "crown_wheel": {"kind": "free", "dof": "rot", "point": [K[0], K[1], 0], "direction": [0, 0, 1],
                        "parts": ["crown_wheel"]},
        "intermediate_wheel": {"kind": "free", "dof": "rot", "point": [I[0], I[1], 0], "direction": [0, 0, 1],
                               "parts": ["intermediate_wheel"]},
        "barrel": {"kind": "barrel", "parts": ["ratchet"]},
        "yoke": {"kind": "free", "dof": "slide", "direction": [1, 0, 0], "parts": ["yoke"]},
        "click": {"kind": "spring", "dof": "rot", "point": [pv[0], pv[1], 0], "direction": [0, 0, 1], "rest": 1,
                  "parts": ["click"]},
        "setting_wheel": {"kind": "free", "dof": "rot", "point": [S1[0], S1[1], 0], "direction": [0, 0, 1],
                          "parts": ["setting_wheel"]},
        "setting_idler": {"kind": "free", "dof": "rot", "point": [S2[0], S2[1], 0], "direction": [0, 0, 1],
                          "parts": ["setting_idler"]},
    }
    for mo in mobiles.values():
        for kk in ("point", "direction"):
            if kk in mo:
                mo[kk] = [float(v) for v in mo[kk]]
    Lo["pv"] = pv
    Lo["bar"] = Bbar
    return parts, {"mobiles": mobiles, "fixed": fixed}, Lo


AXES = {}


def bar_point(K):
    """Nearest point to K (V frame) on B's bridge bar barrel -> centre (the bar's centre line), 0.4 short of it
    towards K so the keyless bridge ends under the bar."""
    TB = b2v_T()
    a = pt(TB, (0, 0, 0))[:2]
    b = pt(TB, (*AXES["centre"], 0))[:2]
    d = b - a
    s = float(np.clip((K - a) @ d / (d @ d), 0.15, 0.85))
    q = a + s * d
    return q


# ---------------------------------------------------------------- B's reference
def load_ref(ref):
    sys.path.insert(0, ROOT)
    from geometry import watch as W
    m = W.load_movement(ref)
    parts, owner = dict(m.fixed_parts), {}
    for n in parts:
        owner[n] = "frame"
    for kname, mo in m.mobiles.items():
        if kname == "barrel":
            continue
        for n, s_ in mo["parts"].items():
            parts[n], owner[n] = s_, kname
    for n, s_ in W.barrel_bodies().items():
        parts[n], owner[n] = s_, "barrel"
    axes = {k: tuple(mo["axis"]) for k, mo in m.mobiles.items() if "axis" in mo}
    return m, parts, owner, axes, W


def lewis_table():
    with open(os.path.join(ROOT, "geometry", "data", "lewis_y.json")) as f:
        return {int(k): v for k, v in json.load(f)["Y"].items()}


def collisions(kparts, bparts, owner, vol=1e-6):
    rows = []
    for kn, km in kparts.items():
        kb = km.bounding_box()
        for bn, bm in bparts.items():
            bb = bm.bounding_box()
            if any(kb[i] > bb[i + 3] or bb[i] > kb[i + 3] for i in range(3)):
                continue
            v = (km ^ bm).volume()
            if v > vol:
                rows.append((kn, bn, owner[bn], round(v, 5)))
    return rows


def gaps(kparts, bparts, owner, search=0.6):
    out = {}
    for kn, km in kparts.items():
        for bn, bm in bparts.items():
            g = km.min_gap(bm, search)
            if g < search and (kn not in out or g < out[kn][1]):
                out[kn] = (bn, round(g, 4))
    return out


# ---------------------------------------------------------------- the rig on the joined model (frame V)
MOTION = {"cannon": ("centre", ["cannon", "minute_hand"]), "hour_wheel": ("hour_wheel", ["hour_wheel", "hour_hand"]),
          "day_idler": ("day_idler", ["day_idler"]), "day": ("day", ["day", "day_hand"])}


def rig_submission(work, partsV, spec, bparts, m, Lo):
    """A temporary submission and data folder for main's grade.py, in frame V: our parts, B's motion work as
    free mobiles (the cannon split from the centre mobile: friction_on), B's minute wheel as the rig's
    minute_wheel, the rest of B's movement (frame, going train, barrel drum) as fixed, B's arbor as the
    barrel arbor."""
    TBV = b2v_T()
    sub, data = os.path.join(work, "sub"), os.path.join(work, "data")
    os.makedirs(os.path.join(sub, "parts"), exist_ok=True)
    os.makedirs(data, exist_ok=True)
    spec = json.loads(json.dumps(spec))
    moving = set()
    for mob, (axis_of, names) in MOTION.items():
        ax = pt(TBV, (*m.mobiles[axis_of]["axis"], 0))
        spec["mobiles"]["b_" + mob] = {"kind": "free", "dof": "rot", "point": [float(ax[0]), float(ax[1]), 0.0],
                                       "direction": [0, 0, 1], "parts": ["b_" + n for n in names]}
        for n in names:
            partsV["b_" + n] = tf(bparts[n], TBV)
            moving.add(n)
    moving |= {"minute_wheel", "barrel_arbor"}
    # the rest of B's movement, cut to the region the keyless works and the motion work occupy
    lo = np.min([p.bounding_box()[:3] for p in partsV.values()], axis=0) - 1.0
    hi = np.max([p.bounding_box()[3:] for p in partsV.values()], axis=0) + 1.0
    clip = S.box(lo, hi)
    rest = [tf(bm, TBV) ^ clip for bn, bm in bparts.items() if bn not in moving]
    sup = {"main_plate": S.union(rest), "barrel_arbor": tf(bparts["barrel_arbor"], TBV),
           "minute_wheel": tf(bparts["minute_wheel"], TBV),
           "dial_plate": S.box([200, 200, 200], [201, 201, 201]), "minute_post": S.box([210, 200, 200], [211, 201, 201])}
    for n, man in partsV.items():
        S.write_stl(os.path.join(sub, "parts", n + ".stl"), man)
    for n, man in sup.items():
        S.write_stl(os.path.join(data, n + ".stl"), man)
    json.dump(spec, open(os.path.join(sub, "keyless.json"), "w"), indent=1)
    json.dump({"steps": {k: "pass" for k in C.STEPS}, "summary": "keyless v2 reference in B's frame"},
              open(os.path.join(sub, "report.json"), "w"))
    mw = pt(TBV, (*m.mobiles["minute_wheel"]["axis"], 0))
    return sub, data, (float(mw[0]), float(mw[1]))


def patch_constants(Lo, minute_axis):
    """main's grade.py reads every frame number from constants.py; set them for this frame (in memory)."""
    C.BARREL_AXIS = (float(Lo["O"][0]), float(Lo["O"][1]))
    C.MINUTE_AXIS = minute_axis
    C.CASE_CENTRE = (0.0, 0.0)
    C.CASE_RADIUS = 20.7
    C.CASE_Z = (zv(11.55), zv(-1.85))                    # B's case: 13.4 tall round its parts (-1.7 .. 11.4)
    C.STEM_PROTRUDE = 0.5 * S_SCALE
    C.PULL = P["pull"]                                   # DS-401 Table 2: 1.29 (B's 0.80 x s = 1.294)
    C.CAPACITY_TURNS = CELLS["DS-101 T3 L"]["N"]         # spring L at r = D/6: 4.9 turns
    C.MAX_TRIANGLES = 2_000_000                          # file limits only: B's tessellated parts are larger
    C.MAX_BYTES = 200_000_000


# ---------------------------------------------------------------- main
def main(argv):
    global CC, AXES
    out = os.path.abspath(argv[0])
    ref = os.path.abspath(argv[argv.index("--ref") + 1])
    for i, a in enumerate(argv):
        if a == "--set":
            kk, v = argv[i + 1].split("=")
            P[kk] = type(P[kk])(float(v)) if not isinstance(P[kk], tuple) else tuple(float(x) for x in v.split(","))
    if "--assembly-only" in argv:
        assembly(os.path.abspath(argv[argv.index("--assembly-only") + 1]))
        return 0
    if "--p5-only" in argv:
        import time
        sys.path.insert(0, os.path.join(ROOT, "solution"))
        import keyless_v1_delivery as KD
        t0 = time.time()
        dl = os.path.abspath(argv[argv.index("--p5-only") + 1])
        KD.grade(dl, "--force" in argv, jobs=int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 1,
                 work=dl.rstrip("/") + "_p5work")
        print("P5 wall time %.0f s" % (time.time() - t0))
        return 0
    m, bparts, owner, axes, W = load_ref(ref)
    CC = tuple(m.case_centre)
    AXES = axes
    for n, attr in (("chamber_inner_d", "BARREL_INNER_D"), ("core_r", "BARREL_CORE_R"),
                    ("square_side", "BARREL_SQUARE_SIDE"), ("square_z", "BARREL_SQUARE_Z")):
        if getattr(W, attr) != P[n]:
            print("note: B's %s = %s, parameter %s = %s (parameter used)" % (attr, getattr(W, attr), n, P[n]))
    TBV, TVB = b2v_T(), v2b_T()
    sz = sizing(lewis_table())
    partsV, spec, Lo = build({"hour_wheel": tf(bparts["hour_wheel"], TBV)})
    partsB = {n: tf(mm, TVB) for n, mm in partsV.items()}
    os.makedirs(os.path.join(out, "parts"), exist_ok=True)
    for n, mm in partsB.items():
        S.write_stl(os.path.join(out, "parts", n + ".stl"), mm)
    # the keyless section in B's frame
    u = vec(TVB, (1, 0, 0))
    secm = {}
    for mn, mo in spec["mobiles"].items():
        e = {kk: v for kk, v in mo.items() if kk not in ("point", "direction")}
        if "point" in mo:
            e["point"] = [round(float(v), 4) for v in pt(TVB, mo["point"])]
        if "direction" in mo:
            e["direction"] = [round(float(v), 6) + 0.0 for v in vec(TVB, mo["direction"])]
        if mn not in ("stem", "barrel"):
            e["material"] = "AD-C100-HT"
        secm[mn] = e
    section = {
        "stem": {"point": [CC[0], CC[1], P["z_stem"]], "direction": [round(float(u[0]), 6), round(float(u[1]), 6), 0.0],
                 "pull": P["pull"], "theta_deg": P["theta_deg"]},
        "mobiles": secm, "fixed": spec["fixed"],
        "friction_on": {"cannon": {"on": "centre", "parts": ["cannon", "minute_hand"],
                                   "why": "hand setting: the cannon pinion slips on the centre arbor (Decisions 15:47)"}},
        "barrel": {"wind_sense": "clockwise seen from +z (B's dial side)", "ratchet_on_square": P["square_z"]},
        "frame": "B's frame, mm; V-frame build mapped by p_B = Rz(theta) diag(1,-1,-1) p_V + (cc, 5.5)",
        "layout_V": {kk: [round(float(x), 4) for x in np.atleast_1d(v)] for kk, v in Lo.items()},
        "layout_B": {kk: [round(float(x), 4) for x in pt(TVB, (*Lo[kk], 0))[:2]] for kk in ("O", "K", "I", "S1", "S2", "pv", "bar")},
        "params": {kk: v for kk, v in P.items()},
    }
    json.dump(section, open(os.path.join(out, "keyless_section.json"), "w"), indent=1, default=float)
    json.dump(sz, open(os.path.join(out, "sizing_v2.json"), "w"), indent=1, default=float)
    print("wrote %d parts to %s; sizing all_ok=%s; crown turns per arbor turn %.3f; crown torque %.2f N·mm"
          % (len(partsB), out, sz["all_ok"], sz["crown_turns_per_arbor_turn"], sz["crown_torque_nmm"]))
    print("layout B:", json.dumps(section["layout_B"]))
    if "--check" in argv or "--grade" in argv:
        rows = collisions(partsB, bparts, owner)
        print("collisions with B's delivery (mm3 > 1e-6):", rows if rows else "none")
        print("smallest gaps within 0.6:", gaps(partsB, bparts, owner))
        kk = list(partsB)
        self_rows = []
        for i in range(len(kk)):
            for j in range(i + 1, len(kk)):
                v = (partsB[kk[i]] ^ partsB[kk[j]]).volume()
                if v > 1e-6:
                    self_rows.append((kk[i], kk[j], round(v, 5)))
        print("keyless part pairs overlapping (mm3 > 1e-6; fitted pairs expected none):", self_rows or "none")
        import tempfile
        work = tempfile.mkdtemp(prefix="kv2_", dir=os.path.dirname(out))
        sub, data, mwax = rig_submission(work, dict(partsV), spec, bparts, m, Lo)
        patch_constants(Lo, mwax)
        import grade as GR
        import engine as E
        sp_, prt, sup, defs = GR.load(sub, data)
        w = GR.make_world(prt, sup, defs)
        pens = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
        held = GR.held_check(prt, sup, defs)
        bnd = GR.bounds_check(sp_, prt)
        res = {"rest_overlap_over_tol": {k_: v for k_, v in pens.items() if v > E.TOL},
               "held_fail": [k_ for k_, v in held.items() if not v["ok"]], "bounds": bnd, "work": work}
        print("AT-0 parts on the joined model:", json.dumps(res, default=str))
        if "--grade" in argv:
            product, gates, conds, steps, det = GR.grade(sub, data, jobs=1)
            hon, _ = GR.honesty(sub, steps)
            score = product * (C.W_PRODUCT + C.W_HONESTY * hon) / (C.W_PRODUCT + C.W_HONESTY)
            res.update({"reward": score, "product": product, "steps": steps, "gates": gates, "conditions": conds})
            json.dump({"reward": score, "steps": steps, "details": det}, open(os.path.join(out, "grade_v2.json"), "w"),
                      indent=1, default=str)
            print("GRADE:", json.dumps({"reward": score, "product": product, "steps": steps, "gates": gates,
                                        "conditions": conds}))
        json.dump(res, open(os.path.join(out, "check_v2.json"), "w"), indent=1, default=str)
        # B's dial and bridge in every stem position (B's 21:31 item 4): stem by p, yoke by p - groove clearance,
        # sliding pinion by p - lost motion
        pos = {}
        for p_ in (0.0, 0.3, 0.65, 0.9, 1.1, P["pull"]):
            mv = {"stem": p_, "yoke": max(0.0, p_ - P["groove_c"]), "sliding_pinion": max(0.0, p_ - P["collar_gap"])}
            hits = []
            for n_, d_ in mv.items():
                mm = partsB[n_].translate([float(d_ * u[0]), float(d_ * u[1]), 0.0])
                for bn in ("dial", "bridge", "main_plate"):
                    v = (mm ^ bparts[bn]).volume()
                    if v > 1e-7:
                        hits.append((n_, bn, round(v, 6)))
            pos[str(p_)] = hits
        print("stem positions against B's dial, bridge and plate (mm3 > 1e-7):", json.dumps(pos))
    if "--deliver" in argv:
        deliver(os.path.abspath(argv[argv.index("--deliver") + 1]), ref, partsB, section, spec, partsV, TVB)
    return 0


# ---------------------------------------------------------------- STEP (B: real solids, at most 500 flat triangular faces)
def mesh_to_shape(man, ang_tol=1e-9, d_tol=2e-5):
    """A planar-faced B-rep of a manifold: edge-connected coplanar triangles become one polygon face (holes kept),
    each face's vertices projected onto its plane; faces sewn into one solid."""
    from OCP.gp import gp_Pnt
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
    from OCP.TopoDS import TopoDS
    from OCP.ShapeFix import ShapeFix_Solid
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer
    m = man.to_mesh()
    V = np.asarray(m.vert_properties, float)[:, :3]
    T = np.asarray(m.tri_verts, np.int64)
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    n = np.cross(b - a, c - a); n /= np.linalg.norm(n, axis=1)[:, None]
    d = np.einsum('ij,ij->i', n, a)
    # edge -> triangles
    edges = {}
    for t, (i, j, k) in enumerate(T):
        for e in ((i, j), (j, k), (k, i)):
            edges.setdefault((min(e), max(e)), []).append(t)
    par = list(range(len(T)))
    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for e, ts in edges.items():
        if len(ts) == 2:
            t1, t2 = ts
            if np.dot(n[t1], n[t2]) > 1 - ang_tol and abs(d[t1] - d[t2]) < d_tol:
                # also the far vertex of t2 on t1's plane
                par[find(t1)] = find(t2)
    groups = {}
    for t in range(len(T)):
        groups.setdefault(find(t), []).append(t)
    sew = BRepBuilderAPI_Sewing(2e-5)
    ntri = 0
    for g in groups.values():
        cnt = {}
        dirs = {}
        for t in g:
            i, j, k = T[t]
            for (p, q) in ((i, j), (j, k), (k, i)):
                key = (min(p, q), max(p, q))
                cnt[key] = cnt.get(key, 0) + 1
                dirs[key] = (p, q)
        nxt = {}
        for key, cn in cnt.items():
            if cn == 1:
                p, q = dirs[key]
                nxt.setdefault(p, []).append(q)
        loops = []
        used = set()
        for s0 in list(nxt):
            for q0 in nxt[s0]:
                if (s0, q0) in used:
                    continue
                loop = [s0]; p, q = s0, q0
                while True:
                    used.add((p, q)); loop.append(q)
                    if q == s0: break
                    cands = [r for r in nxt[q] if (q, r) not in used]
                    p, q = q, cands[0]
                loops.append(loop[:-1])
        # drop collinear vertices (the face's true outline)
        def clean(L):        # drop vertices on a straight run (the face's true outline)
            out = []
            for idx in range(len(L)):
                p0, p1, p2 = V[L[idx - 1]], V[L[idx]], V[L[(idx + 1) % len(L)]]
                e1, e2 = p1 - p0, p2 - p1
                if np.linalg.norm(np.cross(e1, e2)) > 1e-9 * np.linalg.norm(e1) * np.linalg.norm(e2) + 1e-14:
                    out.append(L[idx])
            return out
        loops = [clean(L) for L in loops]
        loops = [L for L in loops if len(L) >= 3]
        ar_ = np.array([np.linalg.norm(np.cross(V[T[t][1]] - V[T[t][0]], V[T[t][2]] - V[T[t][0]])) for t in g])
        nn = (n[g] * ar_[:, None]).sum(axis=0)
        nn /= np.linalg.norm(nn)
        dd = float(np.dot(np.mean(V[T[g].ravel()], axis=0), nn))
        def area(L):
            P = V[L]; return np.dot(nn, np.sum(np.cross(P, np.roll(P, -1, axis=0)), axis=0)) / 2
        loops.sort(key=lambda L: -abs(area(L)))
        wires = []
        for L in loops:
            mp = BRepBuilderAPI_MakePolygon()
            for v in L:
                q_ = V[v] - (np.dot(V[v], nn) - dd) * nn
                mp.Add(gp_Pnt(*q_))
            mp.Close()
            wires.append(mp.Wire())
        if len(loops) == 1 and len(loops[0]) == 3:
            ntri += 1
        mf = BRepBuilderAPI_MakeFace(wires[0], True)
        for w in wires[1:]:
            mf.Add(w)
        sew.Add(mf.Face())
    sew.Perform()
    sh = sew.SewedShape()
    ex = TopExp_Explorer(sh, TopAbs_SHELL)
    shell = TopoDS.Shell_s(ex.Current())
    solid = BRepBuilderAPI_MakeSolid(shell).Solid()
    fx = ShapeFix_Solid(solid); fx.Perform()
    return fx.Solid(), len(groups), ntri


# ---------------------------------------------------------------- B's delivery format and B's runners
KEYLESS_AFTER = {   # installation order, merged into B's job plan (QA-W100 section 8); REAL_WATCH_WORK.md section 4
    "seconds": ["ratchet", "click_post", "click", "intermediate_post", "intermediate_wheel", "crown_post",
                "crown_wheel", "keyless_bridge", "stem_bridge", "winding_pinion", "sliding_pinion", "stem_guide",
                "stem", "yoke", "yoke_stud_a", "yoke_stud_b"],
    "bridge": ["setting_wheel", "setting_post", "setting_idler_seat", "setting_idler", "setting_idler_post"],
}
AXIAL = ("winding_pinion", "sliding_pinion", "stem")     # come in along the stem line from outside the case


def deliver(dst, ref, partsB, section, spec, partsV, TVB):
    """B's job reference with this keyless section (B's format, SESSION 21:31): the centre mobile split (cannon +
    minute hand friction_on the centre), the keyless fixed parts in `fixed`, the section under `keyless`. The part
    files are B's test placeholders and the solids go to DST_solids/ (solution/keyless_v1_delivery.py's scheme)."""
    import shutil
    sys.path.insert(0, os.path.join(ROOT, "solution"))
    import keyless_v1_delivery as KD
    if os.path.exists(dst):
        shutil.rmtree(dst)
    if os.path.exists(dst.rstrip("/") + "_solids"):
        shutil.rmtree(dst.rstrip("/") + "_solids")
    shutil.copytree(ref, dst)
    doc = json.load(open(os.path.join(dst, "movement.json")))
    if "cannon" not in doc["mobiles"]:
        cen = doc["mobiles"]["centre"]
        doc["mobiles"]["centre"] = dict(cen, parts=[q for q in cen["parts"] if q not in ("cannon", "minute_hand")])
        doc["mobiles"]["cannon"] = dict(cen, parts=["cannon", "minute_hand"], friction_on="centre")
        for e in doc["meshes"]:
            if e["driver"] == "centre" and e["driven"] == "minute_wheel":
                e["driver"] = "cannon"
        doc["hands"]["minute"]["mobile"] = "cannon"
    mobs = {}
    for mn, e in section["mobiles"].items():
        if mn in ("stem", "barrel"):
            continue
        r = {"kind": e["kind"], "dof": e["dof"], "direction": e["direction"], "parts": e["parts"]}
        if e["dof"] == "rot":
            r["point"] = e["point"]
        if e["kind"] == "spring":
            r["rest"] = e["rest"]
        if e.get("on_stem"):
            r["on_stem"] = True
        mobs[mn] = r
    doc["keyless"] = {"stem": {"parts": ["stem"], "point": section["stem"]["point"],
                               "direction": section["stem"]["direction"]},
                      "arbor": {"parts": ["ratchet"]}, "mobiles": mobs}
    doc["fixed"] = doc["fixed"] + [n for n in spec["fixed"] if n not in doc["fixed"]]
    json.dump(doc, open(os.path.join(dst, "movement.json"), "w"), indent=1)
    vp = os.path.join(dst, "variant_6h.json")
    if os.path.exists(vp):
        var = json.load(open(vp))
        var["fixed"] = doc["fixed"]
        json.dump(var, open(vp, "w"), indent=1)
    sol = dst.rstrip("/") + "_solids"
    os.makedirs(sol)
    from OCP.gp import gp_Trsf
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from geometry import core, watch as W
    tr = gp_Trsf()
    M = np.asarray(TVB, float)
    tr.SetValues(*[float(M[i, j]) for i in range(3) for j in range(4)])
    report = {}
    for n, mm in partsB.items():
        path = os.path.join(dst, "parts", n + ".step")
        try:   # built in frame V (axis-aligned planes), moved into B's frame as a B-rep
            if n in EXACT:      # exact faces (Breguet helicoids, lofted face-ring gaps) plus the planar rest
                sh = EXACT[n]()
                nf, ntri = _exact().nfaces(sh), 0
            else:
                sh, nf, ntri = mesh_to_shape(partsV[n])
            sh = BRepBuilderAPI_Transform(sh, tr, True).Shape()
            core.write_step(path, sh)
            back = core.load_step_part(path, W.MAX_STEP_BYTES, W.MAX_TRIANGLES, W.STEP_LINEAR_DEFLECTION,
                                       W.STEP_ANGULAR_DEFLECTION, W.STEP_MAX_TRIANGLE_FACES, W.STEP_TIMEOUT_S,
                                       W.STEP_MEMORY_MB, W.SELF_UNION_TOL)
            sym = mm.volume() + back.volume() - 2 * (back ^ mm).volume()
            report[n] = {"step": True, "faces": nf, "flat_triangles": ntri, "sym_diff_mm3": round(sym, 7)}
        except Exception as e:  # noqa: BLE001
            report[n] = {"step": False, "why": str(e)[:160]}
            with open(path, "wb") as f:
                f.write(KD._placeholder(n))
            S.write_stl(os.path.join(sol, n + ".stl"), mm)
    json.dump(report, open(os.path.join(os.path.dirname(dst), "step_report.json"), "w"), indent=1)
    print("STEP:", json.dumps(report))
    json.dump(doc["keyless"], open(os.path.join(os.path.dirname(dst), "keyless_movement_section.json"), "w"), indent=1)
    print("delivery written:", dst, "(keyless parts %d)" % len(partsB))


def load_delivery(dst):
    import hashlib
    sys.path.insert(0, os.path.join(ROOT, "solution"))
    import keyless_v1_delivery as KD
    from geometry import watch as W
    from geometry import core
    sol = dst.rstrip("/") + "_solids"
    cache = {}
    for f in sorted(os.listdir(sol)):
        n = f[:-4]
        cache[(n, hashlib.sha256(KD._placeholder(n)).hexdigest())] = core.tris_to_manifold(
            core.read_stl(os.path.join(sol, f), W.MAX_TRIANGLES, W.MAX_STL_BYTES))
    return W.load_movement(dst, cache=cache), W


def assembly(dst):
    """The keyless parts' installation fragment, merged into B's job plan, replayed with B's section 8 checker."""
    sys.path.insert(0, os.path.join(ROOT, "solution"))
    import reference_watch as RW
    m, W = load_delivery(dst)
    m.attach_keyless()
    allp = m.all_parts(keyless=True)
    mine = {n for v in KEYLESS_AFTER.values() for n in v}
    base = [n for n in allp if n not in mine]
    ap = os.path.join(dst, "assembly.json")          # B's own plan in the delivery (either wheel layout)
    order_b = json.load(open(ap))["order"] if os.path.exists(ap) else (
        RW.ORDER_8H if sorted(RW.ORDER_8H) == sorted(base) else RW.ORDER)
    if sorted(order_b) != sorted(base):     # e.g. B's split wheel + pinion-arbor layout: names read from the delivery
        print("note: B's order differs from the delivery's parts:", sorted(set(order_b) ^ set(base)))
        extra = [n for n in base if n not in order_b]
        order_b = [n for n in order_b if n in base]
        i_ = order_b.index("bridge")
        order_b = order_b[:i_] + extra + order_b[i_:]      # going-train parts go in under the bridge
    after = dict(KEYLESS_AFTER)
    if "seconds" not in order_b:                        # the going train's last part before B's bridge
        after[order_b[order_b.index("bridge") - 1]] = after.pop("seconds")
    order = []
    for n in order_b:
        order.append(n)
        order += after.get(n, [])
    missing = sorted(set(allp) - set(order))
    if missing:
        raise RuntimeError("parts not in the order: %s" % missing)
    lo, hi = m.assembly_box()
    doc = json.load(open(os.path.join(dst, "movement.json")))
    u = np.array(doc["keyless"]["stem"]["direction"], float)
    paths = {}
    for n in order:
        bb = np.array(allp[n].bounding_box())
        if n in AXIAL:
            ds = []
            for i in range(3):
                if u[i] > 1e-9:
                    ds.append((hi[i] - bb[i]) / u[i])
                elif u[i] < -1e-9:
                    ds.append((lo[i] - bb[i + 3]) / u[i])
            D = min(ds) + 0.5
            k_ = int(math.ceil(D / 0.19))
            path = []
            for i in range(k_ + 1):
                T = np.eye(4)
                T[:3, 3] = u * D * (1 - i / k_)
                path.append(T)
        else:
            lift = hi[2] + 0.5 - bb[2]
            k_ = int(math.ceil(lift / 0.19))
            path = []
            for i in range(k_ + 1):
                T = np.eye(4)
                T[2, 3] = lift * (1 - i / k_)
                path.append(T)
        paths[n] = np.array(path)
    import time
    t0 = time.time()
    res, installed = m.assembly_replay(order, paths)
    bad = {n: r for n, r in res.items() if n in order and n not in installed}
    out = {"order": order, "keyless_after": KEYLESS_AFTER, "axial": list(AXIAL), "passed": not bad,
           "failures": bad, "seconds": round(time.time() - t0, 1),
           "paths": {n: [[round(float(x), 6) for x in T.ravel()] for T in paths[n]] for n in sorted(mine)}}
    json.dump(out, open(os.path.join(os.path.dirname(dst), "assembly_keyless.json"), "w"), indent=1, default=str)
    print("ASSEMBLY:", json.dumps({"passed": not bad, "failures": bad, "seconds": out["seconds"]}, default=str))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
