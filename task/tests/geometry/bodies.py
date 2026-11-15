"""The supplied bodies and keep-outs, built from constants. Board, lid: final-pose frame.
Battery: its own frame (x 0..48, y 0..30, z 0..7.5)."""
import numpy as np
import manifold3d as m3
from . import constants as C
from .core import box, cyl_z, cyl_x, union


def pcb():
    p = box((0, 0, 0), C.PCB_SIZE)
    holes = union([cyl_z(x, y, -1, C.PCB_SIZE[2] + 1, C.HOLE_DIA / 2) for x, y in C.HOLES])
    return p - holes


def components():
    return {
        "J1": box(*C.J1_BOX),
        "J2": box(*C.J2_BOX),
        "C1": cyl_z(C.C1_CENTRE[0], C.C1_CENTRE[1], C.C1_Z[0], C.C1_Z[1], C.C1_DIA / 2),
        "J4": box(*C.J4_BOX),
    }


def board():
    return union([pcb()] + list(components().values()))


def battery():
    return box((0, 0, 0), C.BATTERY_SIZE)


def lid():
    return box(*C.LID_BOX)


def envelope_box():
    return box(*C.ENVELOPE)


def j1_section_box(grow, x0, x1):
    (y0, z0), (y1, z1) = C.J1_KEEPOUT_YZ
    return box((x0, y0 - grow, z0 - grow), (x1, y1 + grow, z1 + grow))


def j2_section_cyl(grow, x0, x1):
    cy, cz = C.J2_KEEPOUT_CENTRE_YZ
    return cyl_x(cy, cz, x0, x1, C.J2_KEEPOUT_DIA / 2 + grow, 128)


def keepouts():
    return {"J1": j1_section_box(0.0, *C.J1_KEEPOUT_X), "J2": j2_section_cyl(0.0, *C.J2_KEEPOUT_X)}


def j1_section_2d(grow):
    (y0, z0), (y1, z1) = C.J1_KEEPOUT_YZ
    return m3.CrossSection.square([y1 - y0 + 2 * grow, z1 - z0 + 2 * grow]).translate([y0 - grow, z0 - grow])


def j2_section_2d(grow):
    return m3.CrossSection.circle(C.J2_KEEPOUT_DIA / 2 + grow, 256).translate(list(C.J2_KEEPOUT_CENTRE_YZ))


def supplied():
    return {"board": board(), "lid": lid(), "battery": battery()}
