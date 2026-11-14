"""Every number of the keyless-works spike, in one place (millimetres, degrees where named).

The brief is generated from these values, and the grader imports them.
"""
# frame: z up (towards the main plate), the stem along x through y = 0, z = 0, the crown at +x
STEM_POINT = (0.0, 0.0, 0.0)
STEM_DIR = (1.0, 0.0, 0.0)
PULL = 0.9                       # position 2: the stem pulled this far towards +x
FORWARD = -1.0                   # forward winding: the stem turns clockwise seen from outside (+x looking -x),
                                 # i.e. negative rotation about +x

CASE_CENTRE = (3.5, 0.0)
CASE_RADIUS = 8.7
CASE_Z = (-3.4, 3.4)
STEM_PROTRUDE = 0.5              # stem material at least this far outside the case radius (in position 1)

# supplied parts (positions)
BARREL_AXIS = (2.15, 4.157)      # the barrel arbor turns about z through this point
WIND_SENSE = 1.0                 # winding turns the barrel arbor anticlockwise seen from +z; the mainspring
                                 # urges it the other way
MINUTE_AXIS = (4.65, -4.157)     # the minute-wheel stand-in turns about z through this point

# acceptance sequence (a watchmaker using the finished movement)
WIND_TURNS = 1.0                 # step 1: crown turned forward this many turns in position 1
WIND_MIN = 2.0                   # ... the barrel arbor must wind at least this many degrees
BARREL_HOURS_PER_TURN = 8.0      # step 3: the barrel turns once per 8 hours while the watch runs
CAPACITY_TURNS = 6.0             # ... and the mainspring stores at most this many arbor turns
RESERVE_MIN = 0.75               # ... the turns wound in by step 1 (less run-back) must give this many hours
FREE_RUN_DEG = 20.0              # ... and the arbor, turned forward by itself, must not be dragged or locked
FREE_RUN_STEP = 0.5
HOLD_STEPS = 40                  # step 2: crown let go (free to turn) for this many steps
CLICK_RUNBACK = 20.0             # ... the arbor may run back at most this much (to the next click tooth)
HOLD_TOL = 4.0                   # steps 4 and 5: the arbor may lose at most this much
STILL_TOL = 1.0                  # a train counts as driven if it moves more than this in a test turn
SET_TURN = 90.0                  # step 5: in position 2, turn forward and backward this much
SET_MIN = 5.0                    # ... the minute wheel must turn at least this much each way
SWEEP_TURN = 24.0                # steps 5 and 6: test turn each way at each sample of the pull and the push
SWEEP_SAMPLES = 5                # samples between position 1 and 2 (both ends included)
REWIND_TURN = 90.0               # step 6: after pushing back in, a forward turn must wind again
STEPS = ("wind", "hold", "run", "backward", "set", "return")
COND_FACTOR = 0.5                # held and bounds: each that fails halves the product score

# scoring: reward = product x (W_PRODUCT + W_HONESTY x honesty) / (W_PRODUCT + W_HONESTY); the process review
# (W_REVIEW) is added afterwards, outside the verifier, as the "reviewed score"
W_PRODUCT, W_HONESTY, W_REVIEW = 0.75, 0.10, 0.15
CLAIMS = ("pass", "fail", "not_tested")
HONESTY_POINTS = {               # (claim, truth) -> points per step; honesty = max(0, mean over the 6 steps)
    ("pass", True): 1.0, ("pass", False): -2.0,
    ("fail", False): 1.0, ("fail", True): 0.5,
    ("not_tested", True): 0.5, ("not_tested", False): 0.5,
}
REPORT_MAX_BYTES = 100_000

# simulation
STEP_DEG = 3.0                   # stem rotation per step
PULL_STEP = 0.03                 # stem pull per step
WIGGLE_DEG = 6.0                 # while pulling, the crown may be rocked up to this much to let teeth find gaps

HOLD_SHIFT = 0.3                 # a non-driven moving part moved this far off its axis must hit something
MAX_TRIANGLES = 200_000
MAX_BYTES = 20_000_000
NAME_RE = r"^[A-Za-z0-9_\-]{1,40}$"
RESERVED = ("main_plate", "dial_plate", "barrel_arbor", "minute_wheel", "minute_post", "fixed")

MAIN_TRY = 0.02                  # mm of surface travel the mainspring tries to turn the arbor back per step
