"""Scripted policies for Hold the Line: the reference and the anchors.

Each policy sees only what an agent sees (status, readings, act results). None reads the
episode's hidden fields.
"""
import math
import statistics
from sim import (Episode, LOT, LIMIT, GAUGE_SD, SLOTS, SIGMA0, SHIP_PRICE, DEFECT_PENALTY,
                 SORT_COST, SCRAP_COST, REPLACE_COST, RETURN_DELAY, WEAR_A, WEAR_B, SPREAD_K)


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def p_defect(mu, sd):
    return (1 - phi((LIMIT - mu) / sd)) + phi((-LIMIT - mu) / sd)


def run(policy, seed):
    ep = Episode(seed)
    policy(ep)
    return ep.settle(), ep


# ---- anchors ----------------------------------------------------------
def do_nothing(ep):
    pass


def ship_blind(ep):
    while not ep.done:
        ep.act("ship")


def never_ship(ep):
    while not ep.done:
        ep.act("scrap")


def sort_all(ep):
    while not ep.done:
        ep.act("sort")


def stop_early(ep, n=20):
    """Ship the first n lots unseen and walk away before any return report arrives."""
    for _ in range(n):
        if not ep.done:
            ep.act("ship")


def tamper(ep):
    """Adjust every lot by minus the mean of 3 readings (the classic over-control mistake)."""
    while not ep.done:
        n = min(3, ep.budget)
        m = statistics.fmean(ep.inspect(n)["readings_um"]) if n else 0.0
        ep.act("ship", adjust=max(-10, min(10, -m)) if n else 0.0)


# ---- reference: a filter plus economic rules --------------------------
class Reference:
    """Tracks the process mean with a scalar Kalman filter and the spread from tool age.

    Knobs are tuned on training seeds only. It uses the announced model structure and the
    announced parameter ranges (their midpoints), never an episode's hidden values.
    """

    def __init__(self, n_base=3, n_alert=8, dead=1.5, replace_margin=0.0, innov_gate=2.5, last_replace=12):
        self.n_base, self.n_alert = n_base, n_alert
        self.dead, self.replace_margin = dead, replace_margin
        self.innov_gate, self.last_replace = innov_gate, last_replace

    def __call__(self, ep):
        a = sum(WEAR_A) / 2
        b = sum(WEAR_B) / 2
        k = sum(SPREAD_K) / 2
        m, P = 0.0, 9.0           # belief about the mean after a tool change
        drift_err = 0.0           # learned correction to the wear model
        alert = True
        while not ep.done:
            st = ep.status()
            age = st["tool_age_lots"]
            sd = SIGMA0 + k * age
            left = SLOTS - st["slot"] + 1
            # how many parts to look at
            n = self.n_alert if alert else self.n_base
            per_lot = st["inspect_budget_left"] / max(1, left)
            n = int(min(n, max(1, round(per_lot * (2.0 if alert else 0.8))), st["inspect_budget_left"]))
            innov = 0.0
            if n > 0:
                xs = ep.inspect(n)["readings_um"]
                xbar = statistics.fmean(xs)
                R = (sd * sd + GAUGE_SD ** 2) / n
                innov = (xbar - m) / math.sqrt(P + R)
                if abs(innov) > self.innov_gate and st["inspect_budget_left"] - n >= n:
                    # surprised: look again before believing it
                    xs += ep.inspect(n)["readings_um"]
                    xbar = statistics.fmean(xs)
                    R = (sd * sd + GAUGE_SD ** 2) / len(xs)
                    P += 16.0     # a shock is plausible
                K = P / (P + R)
                drift_err += 0.05 * K * (xbar - m)
                m += K * (xbar - m)
                P *= (1 - K)
                if len(xs) >= 6:
                    s_obs = statistics.pstdev(xs)
                    sd = max(sd, 0.5 * sd + 0.5 * math.sqrt(max(0.25, s_obs ** 2 - GAUGE_SD ** 2)))
            alert = abs(innov) > 1.8 or P > 2.0
            # disposition
            eff = math.sqrt(sd * sd + P)
            p = p_defect(m, eff)
            ship = SHIP_PRICE * LOT - DEFECT_PENALTY * LOT * p
            sort = SHIP_PRICE * LOT * (1 - p) - SORT_COST
            dispose = "ship" if ship >= sort and ship >= -SCRAP_COST else ("sort" if sort >= -SCRAP_COST else "scrap")
            # machine action
            step = a + b * (age + 1) + drift_err
            nxt = m + step
            # value of a fresh tool: compare expected margin per lot now with a new tool's
            new_tool = SHIP_PRICE * LOT - DEFECT_PENALTY * LOT * p_defect(0.0, math.sqrt(SIGMA0 ** 2 + 2.0))
            sd_next = SIGMA0 + k * (age + 1)
            cur = max(SHIP_PRICE * LOT - DEFECT_PENALTY * LOT * p_defect(0.0, math.sqrt(sd_next ** 2 + 1.0)),
                      SHIP_PRICE * LOT * (1 - p_defect(0.0, sd_next)) - SORT_COST)
            gain = (new_tool - cur) * (left - 2) - REPLACE_COST - new_tool
            if left > self.last_replace and gain > self.replace_margin:
                ep.act(dispose, replace=True)
                m, P, drift_err, alert = 0.0, 9.0, 0.0, True
                continue
            adj = 0.0
            if abs(nxt) > self.dead:
                adj = max(-10.0, min(10.0, -nxt - 0.5 * step))   # aim a little low: wear pushes up
            ep.act(dispose, adjust=adj)
            m = nxt + adj
            P += 0.3 ** 2 + 0.05 * 16.0 + (0.08 * adj) ** 2 + 0.02


ANCHORS = {"do_nothing": do_nothing, "ship_blind": ship_blind, "never_ship": never_ship,
           "sort_all": sort_all, "stop_early_20": stop_early, "tamper": tamper}

if __name__ == "__main__":
    import sys
    seeds = range(1000, 1000 + int(sys.argv[1]) if len(sys.argv) > 1 else 1040)
    ref = Reference()
    rows = {"reference": [run(ref, s)[0] for s in seeds]}
    for name, pol in ANCHORS.items():
        rows[name] = [run(pol, s)[0] for s in seeds]
    print("%-14s %9s %9s %9s" % ("policy", "mean", "min", "max"))
    for name, v in rows.items():
        print("%-14s %9.0f %9.0f %9.0f" % (name, statistics.fmean(v), min(v), max(v)))
    r = rows["reference"]
    for name, v in rows.items():
        if name != "reference":
            sc = [max(0.0, min(1.0, x / y)) for x, y in zip(v, r)]
            print("score %-14s mean %.3f max %.3f" % (name, statistics.fmean(sc), max(sc)))
