"""DS-101's Tables 1 to 4 for one spring, from the sheet's own footnote formulas (b/thin-cat, the barrel catalogue).
    python3 spikes/thin_cat/spring_rows.py
Prints the scaled row of every spring named in SPRINGS, as DS-101 Rev F prints it, and fails if the rows it
recomputes for L and LT (already on the sheet) differ from the sheet. Formulas (DS-101 footnotes):
  [^s]  every length x s = 1.617
  [^d2] M = E h t^3 2 pi n / (12 L), k = E h t^3 / (12 L), n_el = M_el / (2 pi k)
  [^d3] M_el = Rp0.2 h t^2 / 6, Rp0.2 = 2475 MPa
  [^d1] t' = t + 0.003 s; n_w = (sqrt(r^2 + L t'/pi) - r) / t'; n_d = (R - sqrt(R^2 - L t'/pi)) / t', R = D/2; N = n_w - n_d
  Table 3: run time = N x 8 h; Table 4: torque 2 pi k n for n = 1..8, a dash past N at r = 12 t; last column the
  torque at N (r = 12 t), at most M_el.
E = 220 GPa ([^vac]). The 1:1 sizes are the sheet's Table 1 (L, LT) and A's row L39 (a/barrel-catalogue,
geometry/watch.py BARREL_CATALOGUE: spring L with a 0.39 mm strip at 1:1, scaled 0.63, in the BR-096-45 drum of
0.6818 mm). L39 is not printed on the sheet (Mikael 04:16: the agent's documents carry no torque); this script
checks A's grader-internal torque figures for it (BARREL_SPRING_TORQUE) against the formulas."""
import math
import os
import re
import sys

S, E, RP = 1.617, 220000.0, 2475.0
SPRINGS = {"L": (0.48, 0.100, 270, 7.5), "L39": (0.39, 0.100, 270, 7.5), "LT": (0.25, 0.100, 270, 7.5)}
ON_SHEET = ("L", "LT")
SHEET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "keyless", "datasheets",
                     "DS-101_mainspring_barrel.md")


def f1(x):
    return "%.1f" % x


def rows(h1, t1, L1, D1):
    """The scaled row in each of DS-101's Tables 1 to 4, as the sheet prints it (strings, without the Var. cell)."""
    h, t, L, D = h1 * S, t1 * S, L1 * S, D1 * S
    k = E * h * t ** 3 / (12 * L)
    mel = RP * h * t * t / 6
    tp = t + 0.003 * S
    R = D / 2

    def N(r):
        return (math.sqrt(r * r + L * tp / math.pi) - r) / tp - (R - math.sqrt(R * R - L * tp / math.pi)) / tp
    t1_ = ["%.2f" % h, "%.3f" % t, "%d" % round(L), "%.1f" % D]
    t2 = [f1(mel), f1(mel / (2 * math.pi * k))]
    t3 = []
    for r in (D / 6, 12 * t, 16 * t):
        n = N(r)
        t3 += ["%.2f" % r] + (["%.1f" % (r / t)] if r == D / 6 else []) + [f1(n), "%d" % round(8 * n)]
    n12 = N(12 * t)
    t4 = [f1(2 * math.pi * k * n) if n <= n12 else "–" for n in range(1, 9)] + [f1(min(2 * math.pi * k * n12, mel))]
    return {"Table 1": t1_, "Table 2": t2, "Table 3": t3, "Table 4": t4}


def sheet_row(text, table_heading, var):
    sec = text[text.index(table_heading):]
    m = re.search(r"^\|\s*%s\s*\|(.*)\|\s*$" % re.escape(var), sec, re.M)
    return [c.strip() for c in m.group(1).split("|")] if m else None


HEADINGS = {"Table 1": "## 3. Dimensions (Table 1)", "Table 2": "## 4. Absolute maximum ratings (Table 2",
            "Table 3": "## 5. Turns and run time (Table 3", "Table 4": "## 6. Torque against arbor turns (Table 4"}


def main():
    text = open(SHEET, encoding="utf-8").read()
    bad = 0
    for var, size in SPRINGS.items():
        got = rows(*size)
        for tab, cells in got.items():
            print("%-3s %-8s | %s |" % (var, tab, " | ".join(cells)))
            if var in ON_SHEET or sheet_row(text, HEADINGS[tab], var) is not None:
                on = sheet_row(text, HEADINGS[tab], var)
                want = on[-len(cells):] if on else None
                if tab == "Table 1" and on:
                    want = [c.strip("*") for c in on[3:]]
                if want != cells:
                    print("    sheet has %s" % want)
                    bad += 1
    print("rows differing from the sheet: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
