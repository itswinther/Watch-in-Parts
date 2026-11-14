"""Hidden physics of one watch on a timing machine. Used by the sidecar server, the reference
watchmaker and the grader. The agent never sees this file; it gets the formula structure in its
instructions and must measure the numbers.

Model (per seed, numbers hidden):
  amplitude A(p, w) = A0 - (dV if p vertical) - (dW if w == "24h")              degrees
  rate(p, w)        = R + K_iso * (A - 250) / 100
                      + H * (+1 if p == "DU", -1 if p == "DD", 0 otherwise)
                      + P * (u . g_p) * j(A)                                      s/day
  with j(A) = J1(a) / a, a = A in radians, scaled so j(250 deg) ~ -1 is NOT assumed:
  j is used exactly as written, times 400.  g_p is the direction of gravity in the balance
  plane for the four vertical positions (0 for dial up / dial down).
  R depends on the regulator index x and on balance mass: R = R0 + 60 x + 9 * removed - 9 * added
  u (poise vector, mg) changes with every mass change at a rim screw.
"""
import math
import random
import sys

POSITIONS = {"DU": None, "DD": None, "CU": (0.0, 1.0), "CD": (0.0, -1.0), "CL": (-1.0, 0.0), "CR": (1.0, 0.0)}
WINDS = ("full", "24h")
SCREWS = 8                      # screws at angles 0, 45, ..., 315 degrees on the balance rim
RATE_PER_MG = 9.0               # s/day faster per mg removed (lighter balance)
POISE_PER_MG = 1.0              # unbalance vector change per mg at a screw
WASHER_MG = 0.5
WASHERS = 4
TIME_BUDGET_MIN = 480
SETUP_MIN = 1                   # every measurement costs this plus its duration
NOISE_RATE_60 = 1.2             # s/day noise of a 60-minute measurement; scales 1/sqrt(t)
NOISE_AMP = 3.0                 # degrees


def j1(x):
    # Bessel J1 by series; fine for 0 < x < 8
    s, term, k = 0.0, x / 2, 0
    while k < 40:
        s += term
        k += 1
        term *= -(x * x / 4) / (k * (k + 1))
    return s


def jfac(A):
    a = math.radians(A)
    return 400.0 * j1(a) / a


class Watch:
    def __init__(self, seed, budget=TIME_BUDGET_MIN):
        r = random.Random(seed)
        self.R0 = r.uniform(-120, 120) if budget == TIME_BUDGET_MIN else r.uniform(-55, 55)
        self.K_iso = r.uniform(-6, 6)
        self.H = r.uniform(-3, 3)
        ang = r.uniform(0, 2 * math.pi)
        mag = r.uniform(0.6, 1.6)
        self.u = [mag * math.cos(ang), mag * math.sin(ang)]
        self.P = 1.0
        self.A0 = r.uniform(270, 305)
        self.dV = r.uniform(25, 45)
        self.dW = r.uniform(20, 40)
        self.x = 0.0
        self.removed = 0.0
        self.added = 0.0
        self.washers = WASHERS
        self.time_left = budget
        self.rng = random.Random(seed * 7919 + 1)
        self.log = []

    # ------------------------------------------------------------- truth
    def amplitude(self, p, w):
        return self.A0 - (self.dV if POSITIONS[p] else 0) - (self.dW if w == "24h" else 0)

    def rate(self, p, w):
        A = self.amplitude(p, w)
        R = self.R0 + 60 * self.x + RATE_PER_MG * (self.removed - self.added)
        r = R + self.K_iso * (A - 250) / 100
        r += self.H * (1 if p == "DU" else -1 if p == "DD" else 0)
        g = POSITIONS[p]
        if g:
            r += self.P * (self.u[0] * g[0] + self.u[1] * g[1]) * jfac(A)
        return r

    def error(self):
        """Grading metric: worst absolute rate over all 12 conditions, plus their spread."""
        rs = [self.rate(p, w) for p in POSITIONS for w in WINDS]
        return max(abs(x) for x in rs) + (max(rs) - min(rs))

    # ------------------------------------------------------------- actions
    def measure(self, p, w, minutes):
        if p not in POSITIONS or w not in WINDS:
            return {"error": "position must be one of %s and wind one of %s" % (list(POSITIONS), list(WINDS))}
        try:
            minutes = int(minutes)
        except (TypeError, ValueError):
            return {"error": "minutes must be a whole number"}
        if not 2 <= minutes <= 120:
            return {"error": "minutes must be between 2 and 120"}
        cost = minutes + SETUP_MIN
        if cost > self.time_left:
            return {"error": "only %d minutes of timing time left" % self.time_left}
        self.time_left -= cost
        sd = NOISE_RATE_60 * math.sqrt(60.0 / minutes)
        out = {"position": p, "wind": w, "minutes": minutes,
               "rate_s_per_day": round(self.rate(p, w) + self.rng.gauss(0, sd), 2),
               "amplitude_deg": round(self.amplitude(p, w) + self.rng.gauss(0, NOISE_AMP), 1),
               "time_left_min": self.time_left}
        self.log.append(("measure", p, w, minutes))
        return out

    def regulate(self, x):
        try:
            x = float(x)
        except (TypeError, ValueError):
            return {"error": "index must be a number"}
        if not (math.isfinite(x) and -1.0 <= x <= 1.0):
            return {"error": "regulator index must be between -1 and 1"}
        self.x = x + self.rng.gauss(0, 0.004)   # setting slop of about 0.25 s/day
        self.log.append(("regulate", x))
        return {"regulator_index": round(x, 4), "note": "set; the index lands within about 0.004 of the request"}

    def remove(self, screw, mg):
        try:
            screw, mg = int(screw), float(mg)
        except (TypeError, ValueError):
            return {"error": "screw must be a whole number and mg a number"}
        if not 0 <= screw < SCREWS or not (math.isfinite(mg) and 0.05 <= mg <= 1.0):
            return {"error": "screw 0..7, mg between 0.05 and 1.0"}
        if self.removed + mg > 3.0:
            return {"error": "at most 3.0 mg may be removed in total"}
        real = mg * (1 + self.rng.gauss(0, 0.08))
        a = math.radians(45 * screw)
        # removing mass at angle a moves the heavy spot away from a
        self.u[0] -= POISE_PER_MG * real * math.cos(a)
        self.u[1] -= POISE_PER_MG * real * math.sin(a)
        self.removed += real
        self.log.append(("remove", screw, mg))
        return {"screw": screw, "requested_mg": mg, "note": "removed; actual amount within about 8% of the request"}

    def washer(self, screw):
        try:
            screw = int(screw)
        except (TypeError, ValueError):
            return {"error": "screw must be a whole number"}
        if not 0 <= screw < SCREWS:
            return {"error": "screw 0..7"}
        if self.washers <= 0:
            return {"error": "no timing washers left"}
        self.washers -= 1
        a = math.radians(45 * screw)
        self.u[0] += POISE_PER_MG * WASHER_MG * math.cos(a)
        self.u[1] += POISE_PER_MG * WASHER_MG * math.sin(a)
        self.added += WASHER_MG
        self.log.append(("washer", screw))
        return {"screw": screw, "washers_left": self.washers}

    def status(self):
        return {"time_left_min": self.time_left, "washers_left": self.washers,
                "removed_mg_requested_total": round(sum(e[2] for e in self.log if e[0] == "remove"), 3),
                "regulator_index_requested": next((e[1] for e in reversed(self.log) if e[0] == "regulate"), 0.0)}


# ------------------------------------------------------------- reference watchmaker
def reference(seed):
    """A scripted watchmaker: measure, poise from the vertical positions, regulate, verify.
    Uses only the agent's actions and the formula structure, never hidden fields."""
    w = Watch(seed)
    m = lambda p, wd, t: w.measure(p, wd, t)
    # 1. amplitudes and vertical rates at full wind
    obs = {p: m(p, "full", 30) for p in ("DU", "CU", "CD", "CL", "CR")}
    Av = sum(obs[p]["amplitude_deg"] for p in ("CU", "CD", "CL", "CR")) / 4
    jf = jfac(Av)
    uy = (obs["CU"]["rate_s_per_day"] - obs["CD"]["rate_s_per_day"]) / (2 * jf)
    ux = (obs["CR"]["rate_s_per_day"] - obs["CL"]["rate_s_per_day"]) / (2 * jf)
    # 2. correct poise: remove mass at the heavy side (the screw nearest the poise vector)
    for _ in range(2):
        mag = math.hypot(ux, uy)
        if mag < 0.15:
            break
        ang = math.degrees(math.atan2(uy, ux)) % 360
        screws = [(int(math.floor(ang / 45)) % 8), (int(math.ceil(ang / 45)) % 8)]
        a0, a1 = math.radians(45 * screws[0]), math.radians(45 * screws[1])
        # split the removal between the two neighbouring screws
        det = math.cos(a0) * math.sin(a1) - math.sin(a0) * math.cos(a1)
        if abs(det) < 1e-9:
            w.remove(screws[0], min(1.0, mag))
        else:
            m0 = (ux * math.sin(a1) - uy * math.cos(a1)) / det
            m1 = (math.cos(a0) * uy - math.sin(a0) * ux) / det
            for s, mm in ((screws[0], m0), (screws[1], m1)):
                mm = max(0.0, min(1.0, mm))
                if mm >= 0.05:
                    w.remove(s, round(mm, 2))
        o = {p: m(p, "full", 30) for p in ("CU", "CD", "CL", "CR")}
        uy = (o["CU"]["rate_s_per_day"] - o["CD"]["rate_s_per_day"]) / (2 * jf)
        ux = (o["CR"]["rate_s_per_day"] - o["CL"]["rate_s_per_day"]) / (2 * jf)
    # 3. regulate to the mean over all conditions
    rs = [m(p, wd, 15)["rate_s_per_day"] for p in POSITIONS for wd in WINDS if w.time_left > 40]
    if rs:
        mean = sum(rs) / len(rs)
        w.regulate(max(-1, min(1, -mean / 60)))
    return w


def reference_scarce(seed, budget=100):
    """Scripted watchmaker for a short budget: verticals first (poise), one horizontal check,
    then regulate on the model's predicted mid-range. Uses only the agent's actions."""
    w = Watch(seed, budget)
    m = lambda p, wd, t: w.measure(p, wd, t)
    obs = {p: m(p, "full", 18) for p in ("CU", "CD", "CL", "CR")}
    Av = sum(obs[p]["amplitude_deg"] for p in obs) / 4
    jf = jfac(Av)
    uy = (obs["CU"]["rate_s_per_day"] - obs["CD"]["rate_s_per_day"]) / (2 * jf)
    ux = (obs["CR"]["rate_s_per_day"] - obs["CL"]["rate_s_per_day"]) / (2 * jf)
    vmean = sum(obs[p]["rate_s_per_day"] for p in obs) / 4
    removed = 0.0
    mag = math.hypot(ux, uy)
    if mag >= 0.15:
        ang = math.degrees(math.atan2(uy, ux)) % 360
        s0, s1 = int(math.floor(ang / 45)) % 8, int(math.ceil(ang / 45)) % 8
        a0, a1 = math.radians(45 * s0), math.radians(45 * s1)
        det = math.cos(a0) * math.sin(a1) - math.sin(a0) * math.cos(a1)
        parts = [(s0, mag)] if abs(det) < 1e-9 else [
            (s0, (ux * math.sin(a1) - uy * math.cos(a1)) / det), (s1, (math.cos(a0) * uy - math.sin(a0) * ux) / det)]
        for sc, mm in parts:
            mm = max(0.0, min(1.0, mm))
            if mm >= 0.05:
                w.remove(sc, round(mm, 2))
                removed += mm
    du = m("DU", "full", 18)
    # predicted mean over conditions after the poise fix: vertical mean (poise terms cancel) and DU, plus removal
    level = 0.5 * (vmean + du["rate_s_per_day"]) + RATE_PER_MG * removed
    w.regulate(max(-1, min(1, -level / 60)))
    return w


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "scarce":
        import statistics
        a, b = [], []
        for s in range(100, 160):
            a.append(Watch(s, 100).error())
            b.append(reference_scarce(s).error())
        print("100-minute budget: untouched mean %.1f, reference mean %.1f (median %.1f, worst %.1f)" % (
            statistics.fmean(a), statistics.fmean(b), statistics.median(b), max(b)))
        raise SystemExit
    import statistics
    errs_ref, errs_none = [], []
    for s in range(100, 160):
        n = Watch(s).error()
        r = reference(s).error()
        errs_none.append(n)
        errs_ref.append(r)
    print("untouched: mean error %.1f, reference: mean error %.1f (median %.1f, worst %.1f)" % (
        statistics.fmean(errs_none), statistics.fmean(errs_ref), statistics.median(errs_ref), max(errs_ref)))
