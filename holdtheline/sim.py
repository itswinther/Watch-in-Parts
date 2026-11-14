"""Hold the Line: a seeded machining-line simulation. Spike, not a spec.

One machine makes one lot of 100 parts per time slot, for 120 slots. Each part has a
deviation from nominal in micrometres; a part outside +/-LIMIT is defective. The process
mean drifts as the tool wears, jumps at random, and the spread grows with tool age.

Per lot the operator may inspect parts (limited budget), must dispose of the lot
(ship / sort / scrap), and may adjust the machine or replace the tool. Shipped defects are
charged RETURN_DELAY slots later. Everything outstanding is settled when the episode ends,
so stopping early never avoids a penalty.

Everything the agent is told is in INSTRUCTION.md. The numbers drawn per seed below
(wear rates, shock times, setup errors) are hidden.
"""
import math
import random

SLOTS = 120
LOT = 100
LIMIT = 10.0
GAUGE_SD = 1.0
INSPECT_BUDGET = 400
INSPECT_COST = 0.5
SHIP_PRICE = 1.0          # per part shipped
DEFECT_PENALTY = 30.0     # per defective part shipped, charged RETURN_DELAY slots later
SORT_COST = 35.0          # 100% inspection of the lot: only good parts ship
SCRAP_COST = 20.0
ADJUST_COST = 5.0
ADJUST_MAX = 10.0
ADJUST_ERR = 0.08         # relative actuation error (sd)
REPLACE_COST = 300.0      # plus one idle slot
RETURN_DELAY = 5
SETUP_SD = 3.0            # mean offset right after a tool change
SIGMA0 = 2.0

# Hidden per-seed parameter ranges (announced as ranges in the instruction).
WEAR_A = (0.05, 0.20)     # drift per lot at age 0
WEAR_B = (0.002, 0.008)   # extra drift per lot per lot of age
SPREAD_K = (0.02, 0.05)   # sigma growth per lot of age
SHOCK_P = 0.05
SHOCK_SD = 4.0
WALK_SD = 0.3


class Episode:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        r = self.rng
        self.a = r.uniform(*WEAR_A)
        self.b = r.uniform(*WEAR_B)
        self.k = r.uniform(*SPREAD_K)
        self.slot = 1                 # current time slot, 1..SLOTS
        self.age = 0                  # lots made with the current tool
        self.mu = r.gauss(0, SETUP_SD)
        self.cash = 0.0
        self.budget = INSPECT_BUDGET
        self.pending = []             # (due_slot, lot_slot, defects)
        self.reports = []             # delivered return reports
        self.log = []
        self.done = False
        self.lot = None
        self.idle = False
        self._make_lot()

    # -- internals -------------------------------------------------------
    def sigma(self):
        return SIGMA0 + self.k * self.age

    def _make_lot(self):
        s = self.sigma()
        self.lot = [self.rng.gauss(self.mu, s) for _ in range(LOT)]
        self.inspected = 0

    def _deliver(self):
        out = []
        keep = []
        for due, lot_slot, d in self.pending:
            if due <= self.slot or self.done:
                self.cash -= DEFECT_PENALTY * d
                rep = {"lot": lot_slot, "defects_returned": d, "charged": DEFECT_PENALTY * d}
                self.reports.append(rep)
                out.append(rep)
            else:
                keep.append((due, lot_slot, d))
        self.pending = keep
        return out

    # -- agent-visible actions ------------------------------------------
    def status(self):
        return {
            "slot": self.slot, "slots_total": SLOTS, "done": self.done,
            "lot_available": (not self.done) and (not self.idle),
            "tool_age_lots": self.age,
            "inspect_budget_left": self.budget,
            "inspected_this_lot": self.inspected if not self.done else 0,
            "cash": round(self.cash, 2),
            "shipments_awaiting_return_report": len(self.pending),
        }

    def inspect(self, n):
        if self.done:
            return {"error": "episode is over"}
        if not isinstance(n, int) or n < 1:
            return {"error": "n must be a positive whole number"}
        if n > self.budget:
            return {"error": "only %d inspections left in the budget" % self.budget}
        if self.inspected + n > LOT:
            return {"error": "a lot has only %d parts" % LOT}
        parts = self.rng.sample(self.lot, n)
        self.budget -= n
        self.inspected += n
        self.cash -= INSPECT_COST * n
        vals = [round(x + self.rng.gauss(0, GAUGE_SD), 1) for x in parts]
        self.log.append({"slot": self.slot, "inspect": n})
        return {"readings_um": vals, "inspect_budget_left": self.budget}

    def act(self, dispose, adjust=0.0, replace=False):
        if self.done:
            return {"error": "episode is over"}
        if dispose not in ("ship", "sort", "scrap"):
            return {"error": "dispose must be ship, sort or scrap"}
        try:
            adjust = float(adjust)
        except (TypeError, ValueError):
            return {"error": "adjust must be a number"}
        if not math.isfinite(adjust) or abs(adjust) > ADJUST_MAX:
            return {"error": "adjust must be between -%g and %g" % (ADJUST_MAX, ADJUST_MAX)}
        if replace and adjust != 0:
            return {"error": "choose adjust or replace, not both"}
        out = {"slot": self.slot, "disposed": dispose}
        defects = sum(1 for x in self.lot if abs(x) > LIMIT)
        if dispose == "ship":
            self.cash += SHIP_PRICE * LOT
            self.pending.append((self.slot + RETURN_DELAY, self.slot, defects))
        elif dispose == "sort":
            self.cash += SHIP_PRICE * (LOT - defects) - SORT_COST
            out["rejected_by_sort"] = defects
        else:
            self.cash -= SCRAP_COST
        self.log.append({"slot": self.slot, "dispose": dispose, "adjust": adjust, "replace": bool(replace),
                         "true_mu": round(self.mu, 3), "true_sigma": round(self.sigma(), 3),
                         "defects": defects, "age": self.age})
        # machine action, then the process moves on
        r = self.rng
        self.age += 1
        self.mu += self.a + self.b * self.age + r.gauss(0, WALK_SD)
        if r.random() < SHOCK_P:
            self.mu += r.gauss(0, SHOCK_SD)
        if replace:
            self.cash -= REPLACE_COST
            self.age = 0
            self.mu = r.gauss(0, SETUP_SD)
            self.slot += 1            # idle slot: no lot is made
            out["tool_replaced"] = True
        elif adjust != 0:
            self.cash -= ADJUST_COST
            self.mu += adjust * (1 + r.gauss(0, ADJUST_ERR))
        self.slot += 1
        if self.slot > SLOTS:
            self.done = True
            self.slot = SLOTS
            out["return_reports"] = self._deliver()
            out["episode_over"] = True
            out["final_cash"] = round(self.cash, 2)
            return out
        out["return_reports"] = self._deliver()
        self._make_lot()
        out["next_slot"] = self.slot
        out["cash"] = round(self.cash, 2)
        return out

    def settle(self):
        """Final profit if the episode stopped now: every outstanding penalty is charged."""
        owed = sum(DEFECT_PENALTY * d for _, _, d in self.pending)
        return self.cash - owed
