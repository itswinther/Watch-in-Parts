"""Every number the tools, the grader and the reference share. SPEC.md version 0.1.

Nothing here may be copied into another file. Import it.
Values marked INTERPRETATION are not stated in SPEC.md 0.1; they are logged in
SESSION.md and need a human yes before they count as spec.
"""
SPEC_VERSION = "0.1"

# --- supplied bodies (mm) ---
PCB_SIZE = (70.0, 45.0, 1.6)
HOLE_DIA = 3.2
HOLES = ((3.5, 3.5), (66.5, 3.5), (3.5, 41.5), (66.5, 41.5))
J1_BOX = ((-1.5, 18.0, 1.6), (6.0, 27.0, 4.9))
J2_BOX = ((58.0, 9.0, -5.0), (72.5, 15.0, 0.0))
J4_BOX = ((9.0, 38.0, -4.5), (15.0, 43.0, 0.0))
C1_CENTRE = (15.0, 33.0)
C1_DIA = 8.0
C1_Z = (1.6, 12.1)
BATTERY_SIZE = (48.0, 30.0, 7.5)   # own frame: x 0..48, y 0..30, z 0..7.5
LID_BOX = ((-2.0, -2.0, 12.5), (73.5, 47.0, 15.5))
J4_CENTRE = (12.0, 40.5, -2.25)

# Plug keep-outs. INTERPRETATION: centred on the connector body's section,
# starting at the connector's outer face.
J1_KEEPOUT_YZ = ((16.25, -0.25), (28.75, 6.75))   # 12.5 x 7
J1_KEEPOUT_X = (-21.5, -1.5)
J2_KEEPOUT_CENTRE_YZ = (12.0, -2.5)
J2_KEEPOUT_DIA = 8.0
J2_KEEPOUT_X = (72.5, 92.5)
KEEPOUT_LEN = 20.0
# INTERPRETATION: "wall mid-plane" is a fixed plane, the middle of the nominal wall.
J1_WALL_PLANE_X = -1.05
J2_WALL_PLANE_X = 72.55
# INTERPRETATION: battery lead face is the x = 0 face of its own frame, top face z = 7.5.
BATTERY_LEAD_CENTRE = (0.0, 15.0, 3.75)

# --- limits ---
ENVELOPE = ((-2.0, -2.0, -10.25), (73.5, 47.0, 12.5))
ENVELOPE_TOL = 0.01
MIN_WALL = 1.6
MATERIAL_FACTOR = 1.15
REFERENCE_VOLUME = 15072.56   # mm3, base + door of solution/reference.py at SPEC 0.1

# --- contract ---
BODY_ORDER = ("board", "lid", "battery", "door")
FIXED_FINAL = ("board", "lid", "door")
START_MIN_DIST = 30.0
MAX_STEP = 0.5
MAX_POSES = 2000
ROT_TOL = 1e-6
FINAL_POSE_TOL = 1e-6
VOL_TOL = 0.2            # mm3, every "intersects by at most / more than"
MAX_TRIANGLES = 200_000
SELF_UNION_TOL = 0.005
MAX_STL_BYTES = 64 * 1024 * 1024
MAX_JSON_BYTES = 8 * 1024 * 1024

# --- checks ---
F1_GAP = 0.1
F1_AREA = 4.0
F1_RING_DIA = 7.0
F1_MIN_HOLES = 3
F2_MOVE = 0.6
F3_MOVE = 2.0
F4_CLEAR = 0.4
F5_SWELL = 1.0
F6_LEAD = 40.0
K_GROW_OUTER = 3.0
K_GROW_INNER = 1.0
S1_MOVE = 1.0
S2_MOVE = 0.2

# Voxel checks. Grids are anchored to a fixed origin so results are deterministic.
# Distances are measured between voxel centres, so the effective thresholds
# carry up to one voxel of error; the margins below are what is graded.
GRID_JITTER = 0.0137     # keeps slice planes off round-number faces
G5_VOXEL = 0.25
G5_SPHERE_DIA = 1.0      # INTERPRETATION: "1.0 sphere" is a diameter
G5_MARGIN = 3.0
G5_NEAR = 1.5            # INTERPRETATION: "the cavity" = within 1.5 of board A or battery
W_VOXEL = 0.2
W_BALL = 0.8
W_ERODE_VOX = 3.5        # 0.8 / 0.2 minus half a voxel of margin
W_DILATE_VOX = 3.0
W_DEV = 0.5 + W_VOXEL    # 0.5 plus one voxel of margin

WEIGHTS = {
    "A1": 3, "A2": 1, "A3": 3, "A4": 1,
    "F1": 1, "F2": 1, "F3": 1, "F4": 1, "F5": 1, "F6": 1,
    "K1": 1, "K2": 1, "K3": 1, "K4": 1,
    "W1": 1, "W2": 1, "S1": 1, "S2": 1, "M1": 1,
}
GATES = ("G1", "G2", "G3", "G4", "G5")
CHECK_TIMEOUT_S = 120
