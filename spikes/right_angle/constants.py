"""Every number of the right-angle winding spike, in one place (millimetres, radians).

The brief is generated from these values, and the grader imports them.
"""
CASE_CENTRE = (4.0391, -9.6417)
CASE_RADIUS = 20.7
CASE_Z = (-5.0, 11.4)

STEM_Y, STEM_Z = 0.0, -3.9            # stem axis: the line y = STEM_Y, z = STEM_Z, along x
STEM_DIR = (1.0, 0.0, 0.0)            # points from the crown end (outside, -x) into the case
STEM_PROTRUDE = 0.5                   # some stem material at least this far outside the case radius

ARBOR_AXIS = ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
SQUARE_SIDE = 0.6                     # the supplied arbor square, centred on the axis, sides along x and y
SQUARE_Z = (-2.5, -1.9)
SEAT_SHELL = 0.04                     # the ratchet must fill the shell 0.04 around the square ...
SEAT_FILL = 0.5                       # ... for at least half its volume, without entering the square

RATIO_BAND = (8.0, 12.0)              # stem turns per arbor turn, both inclusive

MAX_OVERLAP = 0.002                   # mm3: allowed overlap of any two bodies at any sampled pose
NUDGE_FRACTION = 0.03                 # a driven wheel turned back by 3 % of its tooth pitch ...
MIN_CONTACT = 0.0002                  # ... must overlap its driver by at least this (mm3)
SAMPLES_PER_TOOTH = 6                 # mesh samples per tooth of the driver
HOLD_SHIFT = 0.3                      # a mobile moved this far must hit a fixed part
ANCHOR_SHIFT = 0.05                   # a fixed part moved this far must touch the movement or an anchored part
SPIN_SAMPLES = 36

MAX_TRIANGLES = 400_000
MAX_BYTES = 40_000_000
SELF_UNION_TOL = 1e-3
NAME_RE = r"^[A-Za-z0-9_\-]{1,40}$"
RESERVED = ("arbor_square",)

WEIGHTS = {"drive": 3, "direction": 1, "ratio": 1, "clear": 2, "held": 2, "seated": 1, "anchored": 1, "bounds": 1}
