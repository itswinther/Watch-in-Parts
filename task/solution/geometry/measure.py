"""Voxel measurements shared by the grader and the tools. They return numbers, never pass/fail."""
import numpy as np
from scipy import ndimage
from . import constants as C
from . import bodies as B
from . import core
from .core import union


def enclosure_reach(all_bodies, inner):
    """Flood the free space from far outside with a ball of diameter G5_SPHERE_DIA,
    with both connector openings plugged by their sections grown by K_GROW_OUTER.
    Returns the smallest distance (mm) from any reachable ball centre to `inner`."""
    h = C.G5_VOXEL
    lo = np.minimum(C.ENVELOPE[0], C.LID_BOX[0]) - C.G5_MARGIN
    hi = np.maximum(C.ENVELOPE[1], C.LID_BOX[1]) + C.G5_MARGIN
    origin, shape = core.grid_for(lo, hi, h, C.GRID_JITTER)
    plugs = [B.j1_section_box(C.K_GROW_OUTER, lo[0] - 1, 0.0),
             B.j2_section_cyl(C.K_GROW_OUTER, C.PCB_SIZE[0], hi[0] + 1)]
    solid = core.voxelize(union(list(all_bodies) + plugs), origin, shape, h)
    passable = core.edt(~np.pad(solid, 1, constant_values=False)) >= (C.G5_SPHERE_DIA / 2) / h
    lab, _ = ndimage.label(passable)
    edge = np.zeros_like(passable)
    edge[0], edge[-1], edge[:, 0], edge[:, -1], edge[:, :, 0], edge[:, :, -1] = (True,) * 6
    ids = np.unique(lab[edge & passable])
    outside = np.isin(lab, ids[ids > 0])
    inner_vox = np.pad(core.voxelize(inner, origin, shape, h), 1)
    d = core.edt(~inner_vox)[outside]
    nearest = float(d.min() * h) if d.size else 1e9
    return nearest if np.isfinite(nearest) else 1e9


def wall_opening(part):
    """Open the part with the wall ball on the fixed voxel grid. Returns (number of
    connected pieces left, largest distance in mm from the part to what is left)."""
    bb = part.bounding_box()
    origin, shape = core.grid_for(np.array(C.ENVELOPE[0]) - 1.0, np.array(C.ENVELOPE[1]) + 1.0, C.W_VOXEL, C.GRID_JITTER)
    lo_i = np.maximum(np.floor((np.array(bb[:3]) - origin) / C.W_VOXEL).astype(int) - 1, 0)
    hi_i = np.minimum(np.ceil((np.array(bb[3:]) - origin) / C.W_VOXEL).astype(int) + 1, np.array(shape))
    sub_origin = origin + lo_i * C.W_VOXEL
    solid = core.voxelize(part, sub_origin, tuple(int(v) for v in hi_i - lo_i), C.W_VOXEL)
    n, dev = core.opening_test(solid, C.W_ERODE_VOX, C.W_DILATE_VOX)
    return n, (dev * C.W_VOXEL if np.isfinite(dev) else 1e9)
