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

# behaviour required (degrees)
WIND_BAND = (8.0, 40.0)          # stem turns per barrel-arbor turn in position 1, forwards
SET_MIN = 20.0                   # position 2: the minute wheel turns at least this much per stem turn
HOLD_TOL = 4.0                   # the barrel arbor may move at most this much where it must stay put
STILL_TOL = 1.0                  # a train counts as driven if it moves more than this in a test turn
SWEEP_TURN = 30.0                # pull sweep: test turn at each sample, each direction
SWEEP_SAMPLES = 10               # samples between position 1 and 2 (both ends included)

# simulation
STEP_DEG = 3.0                   # stem rotation per step
PULL_STEP = 0.03                 # stem pull per step
WIGGLE_DEG = 6.0                 # while pulling, the crown may be rocked up to this much to let teeth find gaps

HOLD_SHIFT = 0.3                 # a non-driven moving part moved this far off its axis must hit something
MAX_TRIANGLES = 200_000
MAX_BYTES = 20_000_000
NAME_RE = r"^[A-Za-z0-9_\-]{1,40}$"
RESERVED = ("main_plate", "dial_plate", "barrel_arbor", "minute_wheel", "minute_post")

WEIGHTS = {"wind": 3, "slip": 2, "click": 2, "set": 3, "sweep": 3, "held": 2, "bounds": 1}
