"""Load cases from a sim.py result: the barrel driven by the mainspring's own torque (DS-101) and by the 70.1 N mm
strength / stall case.

Why this is a post-process and not a re-run: the engine's kinematics do not depend on torque, and with Coulomb
friction every contact force and every transmitted torque of the quasi-static solve is proportional to the input
torque (efficiencies are torque-independent). A re-run at another barrel torque gives exactly these numbers
scaled. Per mesh, the input torque is the previous mesh's delivered torque (chained mean efficiencies; the worst
case chains the per-mesh minimum efficiencies).

DS-101 cells used (spikes/keyless/datasheets/DS-101_mainspring_barrel.md, Rev F):
  row L (the spring the supplied barrel's 12.12 mm chamber is listed for), Table 4:
    full wind  = column "at N (r = 12 t)" = 4.5 N mm
    low end    = column "n = 1" (the lowest torque in the row) = 0.9 N mm
  thin barrel: x 0.83 (the "L-thin" 0.40 high strip, SESSION.md A 02:59): 3.735 and 0.747 N mm.
  strength / stall: Table 2a, bridle slipping torque, upper end 70.1 N mm (the grader's DS-W04 load).
Table 4 is frictionless torque gained above let-down (DS-101 Note 2), so these are nominal spring torques.

Usage (in Docker): python torque_cases.py <result.json> [--thin]  -> prints and writes <result>_torque_cases.json
"""
import json
import sys

ROW_L_FULL, ROW_L_LOW, THIN = 4.5, 0.9, 0.83
STRENGTH = 70.1


def cases(summary, thin):
    k = THIN if thin else 1.0
    out = {}
    for name, T in (("spring_full_wind", ROW_L_FULL * k), ("spring_low_end", ROW_L_LOW * k), ("strength_stall_70.1", STRENGTH)):
        case = {"barrel_torque_nmm": round(T, 4)}
        for mu in ("mu0.15", "mu0.44", "mu0.51"):
            Tm, Tw, ideal, meshes = T, T, T, []
            for s in summary["meshes"]:
                za, zb = s["teeth"]
                scale_m = Tm / s["T_in_nominal_nmm"]          # forces at this mesh scale with its input torque
                scale_w = Tw / s["T_in_nominal_nmm"]
                e = s[mu]
                meshes.append({"pair": s["pair"], "T_in_nmm": Tm,
                               "peak_total_normal_n": e["max_total_normal_n"] * max(scale_m, scale_w),
                               "grader_formula_force_n": s["grader_force_n"] * ideal / s["T_in_nominal_nmm"]})
                Tm *= zb / za * e["eff_mean"]
                Tw *= zb / za * e["eff_min"]
                ideal *= zb / za
            case[mu] = {"seconds_torque_ideal_nmm": ideal, "seconds_torque_mean_nmm": Tm,
                        "seconds_torque_worst_nmm": Tw, "overall_eff_mean": Tm / ideal,
                        "overall_eff_worst": Tw / ideal, "meshes": meshes,
                        "advances_if_seconds_load_below_nmm": Tw}
        out[name] = case
    return out


def main():
    p = sys.argv[1]
    thin = "--thin" in sys.argv
    d = json.load(open(p))
    s = d.get("summary", d)
    c = cases(s, thin)
    json.dump(c, open(p.replace(".json", "_torque_cases.json"), "w"), indent=1)
    for name, case in c.items():
        print("%s  T_barrel %.3f N mm" % (name, case["barrel_torque_nmm"]))
        for mu in ("mu0.15", "mu0.44", "mu0.51"):
            x = case[mu]
            print("   %s seconds torque ideal %.3e  mean %.3e  worst-phase %.3e N mm (eff %.3f / %.3f); peak normal "
                  "per mesh %s" % (mu, x["seconds_torque_ideal_nmm"], x["seconds_torque_mean_nmm"],
                                   x["seconds_torque_worst_nmm"], x["overall_eff_mean"], x["overall_eff_worst"],
                                   ", ".join("%s %.3g N" % (m["pair"], m["peak_total_normal_n"]) for m in x["meshes"])))


if __name__ == "__main__":
    main()
