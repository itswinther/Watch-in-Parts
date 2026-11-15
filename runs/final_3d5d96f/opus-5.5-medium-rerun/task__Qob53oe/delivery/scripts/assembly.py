"""Assembly plan of movement.json: every part is lowered vertically onto its place, in this order."""
import json, math, os, sys
import numpy as np
OUT = os.environ.get("WATCH_OUT", "/app/delivery")
ORDER = ["bottom_plate", "barrel", "mid_plate", "m2a", "min", "x", "mw", "y", "m4", "m3", "m2b", "s",
         "motion_bridge", "i", "d", "hour_collar", "top_bridge", "hour",
         "hand_seconds", "hand_24h", "hand_hour", "hand_minute"]
STEP = 0.19


def make(zmin_of, top_of_movement):
    paths = {}
    for n in ORDER:
        dz0 = (top_of_movement + 5.0 + 0.3) - zmin_of[n]
        k = int(math.ceil(dz0 / STEP))
        poses = []
        for i in range(k, -1, -1):
            dz = dz0 * i / k
            T = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, round(dz, 9)], [0.0, 0.0, 0.0, 1.0]]
            poses.append(T)
        paths[n] = poses
    return {"order": ORDER, "paths": paths}
