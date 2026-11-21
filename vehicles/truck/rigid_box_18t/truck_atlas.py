# SPDX-License-Identifier: GPL-3.0-or-later

"""rigid_box_18t: the truck's stations and its 1024 atlas.

    python3 truck_atlas.py export

writes export/rigid_box_18t_albedo_plain.png, _albedo_haulier.png, _orm.png,
_normal.png, _emission.png and glass_texels.png beside this file.

Stations are in (x, s, z): x the driver's left (+X), s metres back from the
front of the bumper, z up from the ground. The build frame's y is s - HL, so
the origin sits on the ground at the centre of the 7.90 m plan box. build.py
imports this module, so the UV functions below are the same numbers the
atlas is painted with: a change to one is a change to the other.

The atlas is painted at 64 texels per metre in final pixels (V up, row 0 at
the bottom) and resolved by scripts/atlas.py; every region maps a part of
the truck at that density except the uniform patches (chassis black, liner,
aluminium, rubber...) and the LOD3 pictures, which are recorded in notes.md.
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def _scripts(d):
    while not os.path.isfile(os.path.join(d, "scripts", "asset_build.py")):
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError("no scripts/ above %s" % HERE)
        d = parent
    return os.path.join(d, "scripts")


SCRIPTS = _scripts(HERE)
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import atlas  # noqa: E402
import glazing  # noqa: E402
import vehicle_ids as vi  # noqa: E402

ASSET = "rigid_box_18t"
ATLAS = 1024
PPM = 64.0
VARIANTS = [("plain", True), ("haulier", False)]
DEFAULT_VARIANT = "plain"

# ================================================================ stations
LENGTH = 7.90
HL = LENGTH / 2.0


def Y(s):
    """Build-frame y of station s."""
    return s - HL


def S(y):
    return y + HL


# wheels: radius, axle stations, wheel-centre |x|, tyre (pair) widths
R_WHEEL = 0.52
FRONT_AXLE, REAR_AXLE = 1.40, 5.90
FRONT_X, REAR_X = 1.025, 0.92          # front track 2.05, twin centres 1.84
FRONT_W, REAR_W = 0.30, 0.64           # one 295 tyre; a twin pair, 2.48 over both
WHEELS = [  # part, x, s, width, steer, twin
    (1, FRONT_X, FRONT_AXLE, FRONT_W, True, False),
    (2, -FRONT_X, FRONT_AXLE, FRONT_W, True, False),
    (3, REAR_X, REAR_AXLE, REAR_W, False, True),
    (4, -REAR_X, REAR_AXLE, REAR_W, False, True),
]

# cab: rings (z, front station, half width, front corner radius, back
# station, rear corner radius), bottom to roof
CAB_HW = 1.15
CAB_BACK = 1.80
CAB_RINGS = [   # front station at the corners; the centre is CAB_BOW proud of it
    (0.80, 0.080, 1.150, 0.18, 1.800, 0.06),
    (1.10, 0.09875, 1.150, 0.18, 1.800, 0.06),
    (1.55, 0.126875, 1.150, 0.18, 1.800, 0.06),
    (1.60, 0.130, 1.150, 0.18, 1.800, 0.06),
    (2.55, 0.230, 1.150, 0.18, 1.800, 0.06),
    (2.66, 0.265, 1.140, 0.17, 1.790, 0.055),
    (2.725, 0.320, 1.115, 0.15, 1.775, 0.05),
    (2.75, 0.390, 1.080, 0.12, 1.755, 0.04),
]
CAB_BOW = 0.04                        # the front panel bowed in plan, centre proud
Z_DOOR = 1.10                         # painted cab above, dark plastic below
GRILLE = (0.70, 1.17, 1.49)           # half width, z0, z1 (front plane)
WSCREEN = (0.92, 1.64, 2.51)          # half width, z0, z1 (front plane)
DOOR = (0.42, 1.25)                   # door seams, s
DOOR_GLASS = (0.47, 1.20, 1.72, 2.40)  # s0, s1, z0, z1 on the cab side
REPEATER = (0.34, 0.44, 1.22, 1.28)   # s0, s1, z0, z1 on the cab side
STEP_UP = (0.33, 0.73, 0.86, 1.06, 0.20)    # s0, s1, z0, z1, depth
ARCH = (FRONT_AXLE, R_WHEEL, 0.64, 0.58)  # s, centre z, radius, inner |x|

# bumper: plan half width, corner radius, depth; rings (z, front station)
BUMPER_HW, BUMPER_R, BUMPER_D = 1.17, 0.15, 0.32
# rings (z, station at the corners): a chamfered lower edge, a vertical face
# carrying the lamps, a small chamfer back at the top, 2 mm under the cab
BUMPER_RINGS = [(0.40, 0.09), (0.47, 0.02), (0.775, 0.02), (0.798, 0.045)]
BUMPER_BOW = 0.02
HEADLAMP = (0.60, 0.98, 0.585, 0.765)  # |x| inner, outer, z0, z1 (bumper face)
PLATE_F = (0.26, 0.47, 0.58)          # half width, z0, z1
CARRIER = (0.322, 0.74, 0.92, 1.14, 0.40, 0.798)  # s0, s1, |x|0, |x|1, z0, z1
STEP_LO = (0.36, 0.70, 0.47, 0.67, 0.18)

# deflector: stations (s, top z, half width at the base, at the top)
DEFL_Z0 = 2.70
DEFL = [(0.82, 2.80, 0.98, 0.92), (1.06, 3.10, 1.03, 0.98), (1.31, 3.33, 1.07, 1.03),
        (1.56, 3.48, 1.10, 1.07), (1.82, 3.55, 1.12, 1.10)]
FLAP = (1.70, 1.87, 1.115, 1.145, 1.90, 3.50)  # s0, s1, |x|0, |x|1, z0, z1

# box
BOX_S0, BOX_S1 = 1.90, 7.90
BOX_Z0, BOX_Z1 = 1.15, 3.70
BOX_HW = 1.265
PANEL_HW = 1.253                      # side panels 12 mm in from the rails
RAIL_LO, RAIL_HI = (1.15, 1.32), (3.58, 3.70)
RAIL_T = 0.03                         # rail depth
POST_F = 0.09                         # front corner posts
REAR_POST_HW = 1.12                   # rear frame posts from |x| 1.12 out
HEADER_Z, SILL_Z = 3.45, 1.28
REAR_FRAME = 0.09                     # rear frame depth (s 7.81..7.90)
DOOR_FACE = 7.80                      # roller door face, 0.10 inside the frame
MARK_SIDE_S = (2.30, 4.60, 6.90)
MARK_SIDE = (0.10, 1.205, 1.265)      # width along s, z0, z1
MARK_END = (1.06, 1.16)               # |x| of the front and rear end-outline lamps
MARK_FRONT_Z = (3.60, 3.66)
MARK_REAR_Z = (3.56, 3.64)

# chassis
RAIL_X = (0.345, 0.425)
RAIL_Z = (0.70, 0.97)
SUB_X = (0.35, 0.43)
TANK = (2.05, 2.95, 0.73, 0.70, 0.27)  # s0, s1, |x| centre, z centre, radius (left)
BATTERY = (2.10, 2.75, 0.47, 0.98, 0.52, 0.92)  # right
GUARD_S = (2.10, 5.20)
GUARD_X = (1.195, 1.225)
GUARD_Z = ((0.46, 0.56), (0.76, 0.86))
GUARD_BRACKETS = (2.20, 3.65, 5.12)
BAR = (7.66, 7.80, 1.18, 0.40, 0.55)   # s0, s1, half width, z0, z1
REAR_LAMP = (7.70, 7.84, 0.78, 1.16, 0.55, 0.73)   # s0, s1, |x|0, |x|1, z0, z1
REAR_LENS_Z = (0.585, 0.705)
# rear cells from the outer edge in: (|x| outer, |x| inner, kind); fog on the left
REAR_CELLS_L = [(1.16, 1.08, 4), (1.08, 0.96, 3), (0.96, 0.87, 11), (0.87, 0.78, 6)]
REAR_CELLS_R = [(1.16, 1.08, 5), (1.08, 0.96, 3), (0.96, 0.87, "housing"), (0.87, 0.78, 6)]
PLATE_R = (0.26, 0.42, 0.53)
MUDGUARD = (5.22, 6.58, 0.58, 1.255, 1.07, 1.11)   # s0, s1, |x|0, |x|1, z0, z1

# glass and lamp groups the truck carries
MARKER = 15

# ================================================================ atlas
REG = {
    "box_side": (4, 4, 388, 166), "box_rear": (400, 4, 166, 166),
    "box_front": (20, 640, 166, 166), "cab_band": (752, 4, 268, 140),
    "box_roof": (4, 178, 388, 166), "cab_roof": (400, 178, 152, 104),
    "defl": (560, 178, 140, 96), "bumper": (708, 178, 180, 36),
    "grille": (896, 178, 110, 32),
    "tread_f": (4, 352, 216, 24), "tread_r": (4, 382, 216, 46),
    "wheel_f": (228, 352, 76, 76), "wheel_r": (312, 352, 76, 76),
    "glass_ws": (396, 352, 128, 64), "glass_side": (532, 352, 56, 48),
    "lod3_side": (596, 352, 132, 64), "lod3_front": (736, 352, 46, 64),
    "lod3_rear": (790, 352, 46, 64),
    "rail": (4, 448, 388, 16),
    "plate": (4 + 64 * 10, 578, 40, 12),
}
# Small patches each alone in a 32-texel block on a 64-texel grid, so the
# mips down to level 5 (32 x 32 blocks, beyond 400 m) average one colour:
# a red marker lens no longer bleeds into the black visor's patch.
PATCHES = ("dark", "liner", "alu", "alu_low", "tank", "guard", "rubber", "plastic",
           "step", "housing", "mirror", "seal", "mirror_body", "roof_edge", "hub", "cabpaint")
for _k, _n in enumerate(PATCHES):
    REG[_n] = (2 + 64 * _k, 514, 28, 28)
LENS_KINDS = ("low", "high", "drl", "ind", "tail_brake", "reverse", "fog", "mark_white",
              "mark_amber", "mark_red")
for _k, _n in enumerate(LENS_KINDS):
    REG["lens_" + _n] = (8 + 64 * _k, 578, 18, 12)
PAD = 2.0                              # region origin to the first mapped texel
LOD3_PPM = 16.0


def lens_kind(lamp, colour=None):
    """Atlas lens patch for a lamp id (and a marker's colour)."""
    if lamp == MARKER:
        return "lens_mark_" + colour
    return "lens_" + {7: "low", 8: "high", 9: "drl", 4: "ind", 5: "ind", 3: "tail_brake",
                      6: "reverse", 11: "fog"}[lamp]


# ----------------------------------------------------------- cab mapping
def ring_v():
    """Profile length up the front centre line at each cab ring."""
    v = [0.0]
    for a, b in zip(CAB_RINGS, CAB_RINGS[1:]):
        v.append(v[-1] + math.hypot(b[1] - a[1], b[0] - a[0]))
    return v


RING_V = ring_v()


def bowed(x, sf, xe, bow):
    """Station of a front bowed in plan: sf at the corners (x = xe), the
    centre *bow* proud, a parabola between."""
    return sf - bow * (1.0 - (x / xe) ** 2)


def ring_half(ring, nf=4, nb=2, nbow=2):
    """The x >= 0 half of one cab ring from the front centre to the back
    centre: [(x, s, U)], U the perimeter parameter in metres (true arc
    length on the arcs, whatever their segments; x across the bowed
    front)."""
    _z, sf, w, rf, sb, rb = ring
    xe = w - rf
    out = [(xe * k / nbow, bowed(xe * k / nbow, sf, xe, CAB_BOW), xe * k / nbow)
           for k in range(nbow + 1)]
    for k in range(1, nf):
        t = 0.5 * math.pi * k / nf
        out.append((w - rf + rf * math.sin(t), sf + rf - rf * math.cos(t), w - rf + rf * t))
    u2 = w - rf + rf * math.pi / 2
    out.append((w, sf + rf, u2))
    u3 = u2 + (sb - rb - sf - rf)
    if nb == 0:
        out.append((w, sb, u3 + rb))
        out.append((0.0, sb, u3 + rb + w))
        return out
    out.append((w, sb - rb, u3))
    for k in range(1, nb):
        t = 0.5 * math.pi * k / nb
        out.append((w - rb + rb * math.cos(t), sb - rb + rb * math.sin(t), u3 + rb * t))
    u4 = u3 + rb * math.pi / 2
    out.append((w - rb, sb, u4))
    out.append((0.0, sb, u4 + w - rb))
    return out


def cab_band_px(U, V):
    x, y, _w, _h = REG["cab_band"]
    return (x + PAD + U * PPM, y + PAD + V * PPM)


def cab_v(z):
    return float(np.interp(z, [r[0] for r in CAB_RINGS], RING_V))


def band_world(U, V):
    """Cab band (U, V) in metres to world (x, s, z) and the segment (0
    front, 1 front arc, 2 side, 3 rear arc, 4 back), elementwise."""
    zs = np.array([r[0] for r in CAB_RINGS])
    z = np.interp(V, RING_V, zs)
    sf, w, rf, sb, rb = (np.interp(z, zs, [r[k] for r in CAB_RINGS]) for k in range(1, 6))
    u1 = w - rf
    u2 = u1 + rf * np.pi / 2
    u3 = u2 + (sb - rb - sf - rf)
    u4 = u3 + rb * np.pi / 2
    seg = np.select([U < u1, U < u2, U < u3, U < u4], [0, 1, 2, 3], 4)
    th1 = np.clip((U - u1) / rf, 0, np.pi / 2)
    th3 = np.clip((U - u3) / np.maximum(rb, 1e-6), 0, np.pi / 2)
    x = np.select([seg == 0, seg == 1, seg == 2, seg == 3],
                  [U, u1 + rf * np.sin(th1), w, w - rb + rb * np.cos(th3)],
                  np.maximum(w - rb - (U - u4), 0))
    s = np.select([seg == 0, seg == 1, seg == 2, seg == 3],
                  [sf - CAB_BOW * (1 - (U / u1) ** 2), sf + rf - rf * np.cos(th1), sf + rf + (U - u2),
                   sb - rb + rb * np.sin(th3)], sb)
    return x, s, z, seg


def defl_half(st, nc=3):
    """Half cross-section of a deflector station, from the top centre down
    to the base centre: [(x, z, U)]."""
    _s, h, wb, wt = st
    d = min(0.12, (h - DEFL_Z0) * 0.6)
    pts = [(0.0, h)]
    cx, cz = wt - d, h - d
    for k in range(nc + 1):
        t = 0.5 * math.pi * k / nc
        pts.append((cx + d * math.sin(t), cz + d * math.cos(t)))
    pts += [(wb, DEFL_Z0), (0.0, DEFL_Z0)]
    out, u = [], 0.0
    for i, (x, z) in enumerate(pts):
        if i:
            u += math.hypot(x - pts[i - 1][0], z - pts[i - 1][1])
        out.append((x, z, u))
    return out


def defl_v():
    v = [0.0]
    for a, b in zip(DEFL, DEFL[1:]):
        v.append(v[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return v


DEFL_V = defl_v()


def bumper_half(z_ring, nf=3, nbow=2):
    """Half bumper ring at a ring's corner station: [(x, s, U)]."""
    sf = z_ring
    w, r = BUMPER_HW, BUMPER_R
    out = [((w - r) * k / nbow, bowed((w - r) * k / nbow, sf, w - r, BUMPER_BOW),
            (w - r) * k / nbow) for k in range(nbow + 1)]
    for k in range(1, nf):
        t = 0.5 * math.pi * k / nf
        out.append((w - r + r * math.sin(t), sf + r - r * math.cos(t), w - r + r * t))
    u2 = w - r + r * math.pi / 2
    out.append((w, sf + r, u2))
    u3 = u2 + BUMPER_D - sf - r
    out.append((w, BUMPER_D, u3))
    out.append((0.0, BUMPER_D, u3 + w))
    return out


def bumper_v():
    v = [0.0]
    for a, b in zip(BUMPER_RINGS, BUMPER_RINGS[1:]):
        v.append(v[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return v


BUMPER_V = bumper_v()


def at(reg, u_m, v_m, ppm=PPM):
    """Atlas pixels of a point u_m, v_m metres into region *reg*."""
    x, y, _w, _h = REG[reg]
    return (x + PAD + u_m * ppm, y + PAD + v_m * ppm)


# ================================================================ materials
(M_CAB, M_BOX, M_ROOF, M_PLASTIC, M_DARK, M_LINER, M_ALU, M_TANK, M_GUARD, M_RUBBER,
 M_TYRE, M_RIM, M_HUB, M_GLASS, M_MIRROR, M_PLATE, M_PLATE_EDGE, M_HOUSING, M_GRILLE,
 M_GRILLE_HOLE, M_DOOR, M_STEP, M_SEAL, M_TAPE, M_TAPE_RED, M_PIC_LAMP, M_PIC_TAIL,
 M_HANDLE, M_ALU_DARK) = range(1, 30)
# The LOD3 pictures' own paint: the whole far side and front are one or two
# painted faces, so their windows, grille and lower plastic sit inside the
# painted mean; a lighter far field keeps the tier as bright as LOD0 under
# the same paint (the consumer's tier-switch rule, within 10 %).
M_CAB_FAR, M_BOX_FAR = 30, 31
FAR_GREY = 0.83                 # linear
M_LENS = {"low": 40, "high": 41, "drl": 42, "ind": 43, "tail_brake": 44, "reverse": 45,
          "fog": 46, "mark_white": 47, "mark_amber": 48, "mark_red": 49}
LENS_COLOUR = {"low": "white", "high": "white", "drl": "white", "ind": "amber",
               "tail_brake": "red", "reverse": "white", "fog": "red", "mark_white": "white",
               "mark_amber": "amber", "mark_red": "red"}
PAINTED = (M_CAB, M_BOX)

# The painted panels' base, 0.78 linear: with seams, rivets, cavity shading
# and the light road film the panel field resolves to about 0.75-0.76, and
# the mean over every painted face of every tier (dark window and grille
# texels in the LOD2/LOD3 faces included) lands at 0.74-0.75.
GREY = 255.0 * (1.055 * 0.78 ** (1 / 2.4) - 0.055)
BASE = {
    M_CAB: (GREY, GREY, GREY), M_BOX: (GREY, GREY, GREY), M_ROOF: (214, 215, 212),
    M_PLASTIC: (52, 53, 54), M_DARK: (36, 36, 37), M_LINER: (28, 28, 29),
    M_ALU: (170, 172, 172), M_TANK: (186, 188, 189), M_GUARD: (128, 130, 131),
    M_RUBBER: (34, 34, 35), M_TYRE: (38, 38, 39), M_RIM: (176, 177, 176),
    M_HUB: (70, 71, 72), M_GLASS: glazing.BASE, M_MIRROR: (120, 124, 128),
    M_PLATE: (236, 236, 232), M_PLATE_EDGE: (40, 40, 42), M_HOUSING: (64, 65, 66),
    M_GRILLE: (40, 41, 42), M_GRILLE_HOLE: (16, 16, 17), M_DOOR: (196, 198, 198),
    M_STEP: (44, 44, 45), M_SEAL: (24, 24, 25), M_TAPE: (214, 170, 40),
    M_TAPE_RED: (170, 40, 34), M_PIC_LAMP: (150, 152, 150), M_PIC_TAIL: (110, 28, 24),
    M_HANDLE: (30, 30, 31), M_ALU_DARK: (120, 122, 123),
    M_CAB_FAR: (0, 0, 0), M_BOX_FAR: (0, 0, 0),         # set below from FAR_GREY
}
LENS_UNLIT = {"low": (168, 172, 174), "high": (160, 164, 166), "drl": (186, 188, 188),
              "ind": (176, 104, 30), "tail_brake": (124, 26, 24), "reverse": (178, 180, 180),
              "fog": (112, 24, 22), "mark_white": (180, 182, 182), "mark_amber": (184, 110, 30),
              "mark_red": (128, 26, 24)}
for _n, _m in M_LENS.items():
    BASE[_m] = LENS_UNLIT[_n]
_far = 255.0 * (1.055 * FAR_GREY ** (1 / 2.4) - 0.055)
BASE[M_CAB_FAR] = BASE[M_BOX_FAR] = (_far, _far, _far)
# the livery: a muted dark blue cab and a white box, panels in full colour
HAULIER = {M_CAB: (34, 52, 84), M_BOX: (232, 233, 230),
           M_CAB_FAR: (34, 52, 84), M_BOX_FAR: (232, 233, 230)}

SURFACE = {  # roughness, metallic
    M_CAB: (0.32, 0.0), M_BOX: (0.40, 0.0), M_ROOF: (0.55, 0.0), M_PLASTIC: (0.68, 0.0),
    M_DARK: (0.62, 0.0), M_LINER: (0.85, 0.0), M_ALU: (0.42, 1.0), M_TANK: (0.30, 1.0),
    M_GUARD: (0.48, 0.0), M_RUBBER: (0.86, 0.0), M_TYRE: (0.90, 0.0), M_RIM: (0.40, 0.0),
    M_HUB: (0.50, 0.6), M_GLASS: (glazing.ROUGHNESS, 0.0), M_MIRROR: (0.05, 1.0),
    M_PLATE: (0.40, 0.0), M_PLATE_EDGE: (0.5, 0.0), M_HOUSING: (0.40, 0.0),
    M_GRILLE: (0.62, 0.0), M_GRILLE_HOLE: (0.9, 0.0), M_DOOR: (0.45, 0.8),
    M_STEP: (0.75, 0.0), M_SEAL: (0.80, 0.0), M_TAPE: (0.30, 0.0), M_TAPE_RED: (0.30, 0.0),
    M_PIC_LAMP: (0.2, 0.0), M_PIC_TAIL: (0.2, 0.0), M_HANDLE: (0.5, 0.0),
    M_ALU_DARK: (0.5, 0.8), M_CAB_FAR: (0.32, 0.0), M_BOX_FAR: (0.40, 0.0),
}
for _m in M_LENS.values():
    SURFACE[_m] = (0.15, 0.0)
CABIN_LEVEL = 0.25
# Vehicle glass is not glazing.rooms(): a cab seen through its screen is a
# dark, neutral interior, not a room with a lit far wall (which read as a
# brown stain on the screen). Each pane is a neutral, slightly cool base with
# a gentle vertical falloff, the dashboard's shadow at its foot and a little
# more sky-lit headlining toward its top; no per-pane level, no wall patch.
GLASS_BASE = (54, 58, 62)
GLASS_FALL = (0.80, 1.10)              # foot .. head of a pane
GLASS_PANES = ("glass_ws", "glass_side")


def vehicle_glass(mask, rgb):
    """Paint every glass texel of *rgb* (V up) as the cab behind the pane."""
    out = np.asarray(rgb, np.float32).copy()
    base = np.asarray(GLASS_BASE, np.float32)
    out[mask] = base
    rs = np.random.RandomState(7)
    grain = 1.0 + 0.015 * rs.standard_normal(mask.shape).astype(np.float32)
    for reg in GLASS_PANES:
        x, y, w, h = REG[reg]
        rows = np.arange(y, y + h)
        t = np.clip((rows - y - PAD) / max(h - 2 * PAD, 1), 0, 1) ** 0.8
        f = GLASS_FALL[0] + (GLASS_FALL[1] - GLASS_FALL[0]) * t
        sub = mask[y:y + h, x:x + w]
        blk = out[y:y + h, x:x + w]
        blk[sub] = (base[None, None, :] * f[:, None, None]
                    * np.ones((1, w, 1), np.float32))[sub]
    out[mask] *= grain[mask][:, None]
    return out


def lut(variant):
    t = np.zeros((256, 3), np.float32)
    for mid, col in BASE.items():
        t[mid] = col
    if variant == "haulier":
        for mid, col in HAULIER.items():
            t[mid] = col
    return t


# ================================================================ painting
class Painter:
    """Region painting in metres on top of atlas.Canvas."""

    def __init__(self, c):
        self.c = c

    def field(self, reg, ppm=PPM):
        """(rows, cols, u, v) over a whole region, u and v in metres from
        the region's mapped origin."""
        x, y, w, h = REG[reg]
        sy, sx, Y_, X_ = self.c.field(x, x + w, y, y + h)
        return sy, sx, (X_ - x - PAD) / ppm, (Y_ - y - PAD) / ppm

    def fill(self, reg, mid, height=0.0):
        x, y, w, h = REG[reg]
        self.c.paint(x, x + w, y, y + h, mid=mid, shade=1.0, ao=1.0, height=height)

    def where(self, reg, mask_fn, mid=None, shade=None, height=None, ao=None, add_h=None,
              ppm=PPM):
        sy, sx, u, v = self.field(reg, ppm)
        m = mask_fn(u, v)
        if not np.any(m):
            return
        c = self.c
        if mid is not None:
            c.mid[sy, sx][m] = mid
        if shade is not None:
            c.shade[sy, sx][m] *= shade
        if height is not None:
            c.height[sy, sx][m] = height
        if add_h is not None:
            hh = c.height[sy, sx]
            hh[m] += add_h
            c.height[sy, sx] = hh
        if ao is not None:
            c.ao[sy, sx][m] = np.minimum(c.ao[sy, sx][m], ao)


def line(a, b, w):
    """|a - b| <= w / 2: a line of width w metres."""
    return np.abs(a - b) <= w / 2.0


def seam(P, reg, mask_fn, depth=0.002, shade=0.62):
    """A panel seam: a darkened groove."""
    P.where(reg, mask_fn, shade=shade, add_h=-depth, ao=0.7)


def paint(ss=atlas.SS):
    c = atlas.Canvas(size=ATLAS, ss=ss, ppm=PPM)
    P = Painter(c)
    paint_box(P)
    paint_cab(P)
    paint_front(P)
    paint_wheels(P)
    paint_patches(P)
    paint_lod3(P)
    return c


# ---------------------------------------------------------------- box
def paint_box(P):
    # sides: u = s - 1.90, v = z - 1.15
    P.fill("box_side", M_BOX)
    joints = [BOX_S0 + POST_F + k * (BOX_S1 - REAR_FRAME - BOX_S0 - POST_F) / 5.0
              for k in range(1, 5)]
    for js in joints:
        seam(P, "box_side", lambda u, v, js=js: line(u + BOX_S0, js, 0.012), depth=0.0015,
             shade=0.80)
        # rivet columns either side of the joint
        for off in (-0.03, 0.03):
            P.where("box_side", lambda u, v, js=js, off=off: (
                np.hypot(u + BOX_S0 - js - off, np.mod(v, 0.10) - 0.05) < 0.006),
                add_h=0.001, shade=0.92)
    for zr in (RAIL_LO[1] + 0.025, RAIL_HI[0] - 0.025):
        P.where("box_side", lambda u, v, zr=zr: (np.hypot(np.mod(u, 0.10) - 0.05,
                                                          v + BOX_Z0 - zr) < 0.006),
                add_h=0.001, shade=0.92)
    # roof: translucent-white panel, transverse bows every 0.6 m
    P.fill("box_roof", M_ROOF)
    for k in range(1, 10):
        sb = BOX_S0 + k * 0.6
        P.where("box_roof", lambda u, v, sb=sb: line(u + BOX_S0, sb, 0.04), add_h=0.004)
    P.where("box_roof", lambda u, v: (v < 0.04) | (v > 2 * BOX_HW - 0.04), mid=M_ALU)
    # front wall: painted panel, a central joint
    P.fill("box_front", M_BOX)
    seam(P, "box_front", lambda u, v: line(u, BOX_HW, 0.012), depth=0.0015, shade=0.82)
    # rear: aluminium frame, roller door
    P.fill("box_rear", M_ALU)

    def door(u, v):
        x, z = u - BOX_HW, v + BOX_Z0
        return (np.abs(x) < REAR_POST_HW) & (z > SILL_Z) & (z < HEADER_Z)
    P.where("box_rear", door, mid=M_DOOR)
    P.where("box_rear", lambda u, v: door(u, v) & (np.mod(v + BOX_Z0 - SILL_Z, 0.115) < 0.016),
            add_h=-0.004, shade=0.78, ao=0.8)
    P.where("box_rear", lambda u, v: door(u, v) & (np.abs(u - BOX_HW) < 0.09)
            & (np.abs(v + BOX_Z0 - 1.36) < 0.02), mid=M_HANDLE, add_h=0.01)
    # yellow contour marking on the rear frame: the posts' outer edge and
    # the header, broken in short lengths
    def tape(u, v):
        x, z = u - BOX_HW, v + BOX_Z0
        post = (np.abs(np.abs(x) - 1.21) < 0.025) & (z > 1.30) & (z < 3.40) \
            & (np.mod(z, 0.60) < 0.48)
        head = (np.abs(z - 3.50) < 0.025) & (np.abs(x) < 1.02) & (np.mod(x + 3, 0.60) < 0.48)
        return post | head
    P.where("box_rear", tape, mid=M_TAPE, add_h=0.0005)
    # bottom rail strip: u = s - 1.90, v = z - 1.15; tape along it, broken
    # round the markers
    P.fill("rail", M_ALU)
    P.where("rail", lambda u, v: (np.abs(v + BOX_Z0 - 1.30) < 0.015)
            & (np.mod(u, 0.6) < 0.48), mid=M_TAPE, add_h=0.0005)
    P.where("rail", lambda u, v: np.abs(v + BOX_Z0 - 1.17) < 0.012, add_h=0.002)


# ---------------------------------------------------------------- cab
def paint_cab(P):
    c = P.c
    x0, y0, w, h = REG["cab_band"]
    sy, sx, Y_, X_ = c.field(x0, x0 + w, y0, y0 + h)
    U = (X_ - x0 - PAD) / PPM
    V = (Y_ - y0 - PAD) / PPM
    x, s, z, seg = band_world(U, V)
    mid = np.full(U.shape, M_CAB, np.uint8)
    hgt = np.zeros(U.shape, np.float32)
    shade = np.ones(U.shape, np.float32)
    ao = np.ones(U.shape, np.float32)
    side, front = seg == 2, seg == 0
    mid[(z < Z_DOOR) & (seg >= 2)] = M_PLASTIC
    # the painted lower front: a seam, and a slot of a lower air intake
    low = (z < Z_DOOR) & (seg <= 1)
    mid[low & (x < 0.70) & (np.abs(z - 0.90) < 0.03)] = M_GRILLE_HOLE
    # a soft shadow line where the painted cab meets the plastic
    shade[(z >= Z_DOOR) & (z < Z_DOOR + 0.02)] *= 0.8

    def groove(m, d=0.002, sh=0.6):
        hgt[m] -= d
        shade[m] *= sh
        ao[m] = np.minimum(ao[m], 0.7)
    sw = 0.010                                    # seam width
    # door outline, its top following the roof's rounding
    d0, d1 = DOOR
    groove(side & (np.abs(s - d0) < sw / 2) & (z > Z_DOOR) & (z < 2.50))
    groove(side & (np.abs(s - d1) < sw / 2) & (z > Z_DOOR) & (z < 2.50))
    groove(side & (np.abs(z - 2.50) < sw / 2) & (s > d0) & (s < d1))
    # door glass: black rubber surround, and the opening dark for LOD2
    g0, g1, gz0, gz1 = DOOR_GLASS
    win = side & (s > g0) & (s < g1) & (z > gz0) & (z < gz1)
    mid[win] = M_SEAL
    # door handle and a key plate
    hdl = side & (s > 1.08) & (s < 1.21) & (np.abs(z - 1.52) < 0.025)
    mid[hdl] = M_HANDLE
    hgt[hdl] += 0.006
    # the quarter panel behind the door: an intake grille
    vent = side & (s > 1.44) & (s < 1.66) & (z > 1.74) & (z < 2.06)
    mid[vent] = M_GRILLE
    slots = vent & (np.mod(z - 1.74, 0.032) < 0.014)
    mid[slots] = M_GRILLE_HOLE
    hgt[vent & ~slots] += 0.004
    # the front corner panel's seam, just round the corner on the side
    corner = np.interp(z, [r[0] for r in CAB_RINGS], [r[1] + r[3] for r in CAB_RINGS])
    groove(side & (np.abs(s - corner - 0.025) < sw / 2) & (z > Z_DOOR) & (z < 2.48))
    # front: service flap seam round the grille, a seam under the screen
    gh, gz0_, gz1_ = GRILLE
    groove(front & (np.abs(z - 1.575) < sw / 2))
    groove(front & (np.abs(z - (Z_DOOR + 0.02)) < sw / 2))
    gr = front & (x < gh) & (z > gz0_) & (z < gz1_)
    mid[gr] = M_GRILLE
    holes = front & (x < gh - 0.02) & (z > gz0_ + 0.02) & (z < gz1_ - 0.02) \
        & (np.mod(z - gz0_, 0.067) > 0.024)
    mid[holes] = M_GRILLE_HOLE
    hgt[gr & ~holes] += 0.008
    # windscreen rubber, for the screen's edges and LOD2
    wh, wz0, wz1 = WSCREEN
    ws = front & (x < wh) & (z > wz0) & (z < wz1)
    mid[ws] = M_SEAL
    # the screen's foot: a black cowl strip with the wiper spindles
    # (the screen's foot is the recess wall in 3D: no painted cowl strip)
    # back wall: a horizontal seam
    groove((seg == 4) & (np.abs(z - 1.30) < sw / 2))
    c.mid[sy, sx] = mid
    c.shade[sy, sx] = shade
    c.height[sy, sx] = hgt
    c.ao[sy, sx] = ao
    # roof: u = x + 1.15, v = s - 0.30; a hatch outline
    P.fill("cab_roof", M_CAB)
    for a, b in ((0.50, 0.50),):
        seam(P, "cab_roof", lambda u, v: (
            (np.abs(np.abs(u - CAB_HW) - 0.38) < 0.006) & (np.abs(v + 0.30 - 0.95) < 0.30)) | (
            (np.abs(np.abs(v + 0.30 - 0.95) - 0.30) < 0.006) & (np.abs(u - CAB_HW) < 0.38)))
    # deflector: u round the section from the top centre, v along the top
    P.fill("defl", M_CAB)
    seam(P, "defl", lambda u, v: line(v, DEFL_V[-1] - 0.06, 0.012), depth=0.0015)
    # side flap faces share the deflector region's lower rows
    # bumper: u round from the front centre, v up the profile from z 0.40
    P.fill("bumper", M_PLASTIC)
    zb = lambda v: np.interp(v, BUMPER_V, [r[0] for r in BUMPER_RINGS])  # noqa: E731
    P.where("bumper", lambda u, v: np.abs(zb(v) - 0.585) < 0.006, add_h=-0.003, shade=0.7)
    P.where("bumper", lambda u, v: zb(v) < 0.46, shade=0.82)
    ph, pz0, pz1 = PLATE_F
    P.where("bumper", lambda u, v: (u < ph) & (zb(v) > pz0) & (zb(v) < pz1), mid=M_PLATE)
    P.where("bumper", lambda u, v: (u < ph) & (zb(v) > pz0) & (zb(v) < pz1) & (
        (u > ph - 0.012) | (zb(v) < pz0 + 0.012) | (zb(v) > pz1 - 0.012)), mid=M_PLATE_EDGE)
    hx0, hx1, hz0, hz1 = HEADLAMP
    P.where("bumper", lambda u, v: (u > hx0 - 0.02) & (u < hx1 + 0.02)
            & (zb(v) > hz0 - 0.02) & (zb(v) < hz1 + 0.02), mid=M_HOUSING)
    # tow pin slot
    P.where("bumper", lambda u, v: (u < 0.06) & (np.abs(zb(v) - 0.64) < 0.03),
            mid=M_GRILLE_HOLE, add_h=-0.01)
    # grille: horizontal slats over darkness
    P.fill("grille", M_GRILLE_HOLE)
    P.where("grille", lambda u, v: np.mod(v, 0.067) > 0.030, mid=M_GRILLE, height=0.010)


def paint_front(P):
    pass


# ---------------------------------------------------------------- wheels
def paint_wheels(P):
    c = P.c
    for reg, front in (("wheel_f", True), ("wheel_r", False)):
        x, y, w, h = REG[reg]
        cx, cy = x + w / 2.0, y + h / 2.0
        ppm = (w - 2 * PAD) / (2 * R_WHEEL)
        sy, sx, Y_, X_ = c.field(x, x + w, y, y + h)
        r = np.hypot(X_ - cx, Y_ - cy) / ppm
        a = np.arctan2(Y_ - cy, X_ - cx)
        mid = np.full(r.shape, M_TYRE, np.uint8)
        hgt = np.zeros(r.shape, np.float32)
        shade = np.ones(r.shape, np.float32)
        rim = r < 0.285
        mid[rim] = M_RIM
        hgt[(r > 0.27) & (r < 0.285)] = 0.004
        # hand holes, studs and the hub
        n_holes = 8 if front else 10
        hole = rim & (np.abs(r - 0.205) < 0.035) & (np.cos(n_holes * a) > 0.55)
        mid[hole] = M_SEAL
        hgt[hole] = -0.01
        studs = (np.abs(r - 0.125) < 0.013) & (np.cos(10 * a) > 0.6)
        mid[studs] = M_HUB
        hgt[studs] = 0.006
        hub = r < (0.10 if front else 0.09)
        mid[hub] = M_HUB if not front else M_RIM
        shade[hub & (r < 0.05)] *= 0.85
        hgt[hub] = 0.003
        # sidewall: faint lettering band as relief, no words
        hgt[(np.abs(r - 0.43) < 0.012)] = 0.0015
        shade[(r > 0.285) & (r < 0.30)] *= 0.75
        c.mid[sy, sx] = mid
        c.height[sy, sx] = hgt
        c.shade[sy, sx] = shade
    for reg, wdt in (("tread_f", FRONT_W), ("tread_r", REAR_W)):
        P.fill(reg, M_TYRE)
        # circumferential grooves, as relief
        for g in ((0.08, 0.15, 0.22) if wdt < 0.5 else (0.08, 0.17, 0.25, 0.39, 0.47, 0.56)):
            P.where(reg, lambda u, v, g=g: line(v, g, 0.012), add_h=-0.008, shade=0.8)
        if wdt > 0.5:
            P.where(reg, lambda u, v: line(v, wdt / 2, 0.04), mid=M_SEAL, add_h=-0.03)
        # sipes across the shoulders
        P.where(reg, lambda u, v: ((v < 0.05) | (v > wdt - 0.05)) & (np.mod(u, 0.06) < 0.012),
                add_h=-0.006, shade=0.85)


# ---------------------------------------------------------------- patches
def paint_patches(P):
    for name, mid in (("dark", M_DARK), ("liner", M_LINER), ("alu", M_ALU),
                      ("alu_low", M_ALU), ("tank", M_TANK), ("guard", M_GUARD),
                      ("rubber", M_RUBBER), ("plastic", M_PLASTIC), ("step", M_STEP),
                      ("housing", M_HOUSING), ("mirror", M_MIRROR), ("seal", M_SEAL),
                      ("mirror_body", M_PLASTIC), ("roof_edge", M_ALU), ("hub", M_HUB),
                      ("cabpaint", M_CAB)):
        P.fill(name, mid)
    P.where("step", lambda u, v: (np.mod(u, 0.05) < 0.02) & (np.mod(v, 0.05) < 0.02),
            add_h=0.002, shade=1.15)
    P.where("tank", lambda u, v: np.mod(v, 0.12) < 0.02, add_h=0.003)
    P.where("guard", lambda u, v: np.mod(v, 0.08) < 0.012, add_h=-0.002, shade=0.85)
    # plate: blank white with a thin dark border
    P.fill("plate", M_PLATE)
    x, y, w, h = REG["plate"]
    P.c.paint(x, x + w, y, y + 1.6, mid=M_PLATE_EDGE)
    P.c.paint(x, x + w, y + h - 1.6, y + h, mid=M_PLATE_EDGE)
    P.c.paint(x, x + 1.6, y, y + h, mid=M_PLATE_EDGE)
    P.c.paint(x + w - 1.6, x + w, y, y + h, mid=M_PLATE_EDGE)
    for name in LENS_KINDS:
        P.fill("lens_" + name, M_LENS[name])
    for name in ("low", "high"):
        x, y, w, h = REG["lens_" + name]
        P.c.disc(x + w / 2, y + h / 2, h * 0.36, shade=0.82, height=-0.004)
        P.c.disc(x + w / 2, y + h / 2, h * 0.12, shade=1.15)
    for name in ("tail_brake", "ind", "reverse", "fog"):
        x, y, w, h = REG["lens_" + name]
        sy, sx, Y_, X_ = P.c.field(x, x + w, y, y + h)
        rib = np.mod(Y_ - y, 2.0) < 0.7
        P.c.shade[sy, sx][rib] *= 0.88
    # glass
    P.fill("glass_ws", M_GLASS)
    P.fill("glass_side", M_GLASS)


# ---------------------------------------------------------------- LOD3
def paint_lod3(P):
    """Pictures for the 60-triangle LOD3: a side elevation, the front and
    the rear, at 16 texels per metre."""
    def side(u, v):
        s, z = u, v
        return s, z
    reg = "lod3_side"
    P.fill(reg, M_DARK)
    pp = LOD3_PPM

    def W(fn, mid):
        P.where(reg, fn, mid=mid, ppm=pp)
    W(lambda s, z: (s > BOX_S0) & (z > BOX_Z0), M_BOX_FAR)
    W(lambda s, z: (s > BOX_S0) & (np.abs(z - 1.23) < 0.08), M_ALU)
    W(lambda s, z: (s < CAB_BACK) & (z > Z_DOOR), M_CAB_FAR)
    W(lambda s, z: (s < CAB_BACK) & (z > 0.80) & (z <= Z_DOOR), M_PLASTIC)
    W(lambda s, z: (s > 0.75) & (s < 1.82) & (z > 2.75), M_CAB_FAR)    # deflector
    W(lambda s, z: (s > DOOR_GLASS[0]) & (s < DOOR_GLASS[1]) & (z > DOOR_GLASS[2])
      & (z < DOOR_GLASS[3]), M_GLASS)
    W(lambda s, z: (s < 0.32) & (z > 0.40) & (z < 0.80), M_PLASTIC)
    # the under-body solid's sides are unpainted: its guards, tank and rims
    # in their own colours, light under dark paint as LOD0's are
    W(lambda s, z: (s > GUARD_S[0]) & (s < GUARD_S[1]) & (
        (np.abs(z - 0.51) < 0.05) | (np.abs(z - 0.81) < 0.05)), M_GUARD)
    W(lambda s, z: (s > TANK[0]) & (s < TANK[1]) & (np.abs(z - TANK[3]) < 0.22), M_TANK)
    for sc in (FRONT_AXLE, REAR_AXLE):
        W(lambda s, z, sc=sc: np.hypot(s - sc, z - R_WHEEL) < R_WHEEL, M_TYRE)
        W(lambda s, z, sc=sc: np.hypot(s - sc, z - R_WHEEL) < 0.29, M_RIM)
    reg = "lod3_front"
    P.fill(reg, M_DARK)
    # the cab front, painted down to its foot as LOD0's (the lower intake slot
    # drawn), across the extrusion's full width
    W(lambda u, z: z > 0.80, M_CAB_FAR)
    W(lambda u, z: (np.abs(u - BOX_HW) < 0.70) & (np.abs(z - 0.90) < 0.03), M_GRILLE_HOLE)
    W(lambda u, z: (z > 2.75), M_BOX_FAR)
    W(lambda u, z: (z > 2.75) & (z < 3.55) & (np.abs(u - BOX_HW) < 1.08), M_CAB_FAR)
    W(lambda u, z: (np.abs(u - BOX_HW) < WSCREEN[0]) & (z > WSCREEN[1]) & (z < WSCREEN[2]),
      M_GLASS)
    W(lambda u, z: (np.abs(u - BOX_HW) < GRILLE[0]) & (z > GRILLE[1]) & (z < GRILLE[2]),
      M_GRILLE)
    W(lambda u, z: (z > 0.40) & (z < 0.80) & (np.abs(u - BOX_HW) < BUMPER_HW), M_PLASTIC)
    W(lambda u, z: (np.abs(np.abs(u - BOX_HW) - 0.79) < 0.19) & (z > 0.60) & (z < 0.76),
      M_PIC_LAMP)
    W(lambda u, z: (z < 0.40) & (np.abs(np.abs(u - BOX_HW) - FRONT_X) < 0.15), M_TYRE)
    reg = "lod3_rear"
    P.fill(reg, M_DARK)
    W(lambda u, z: z > BOX_Z0, M_ALU)
    W(lambda u, z: (z > SILL_Z) & (z < HEADER_Z) & (np.abs(u - BOX_HW) < REAR_POST_HW), M_DOOR)
    W(lambda u, z: (z > 0.40) & (z < 0.55) & (np.abs(u - BOX_HW) < BAR[2]), M_GUARD)
    W(lambda u, z: (z > 0.55) & (z < 0.73) & (np.abs(np.abs(u - BOX_HW) - 0.97) < 0.19),
      M_PIC_TAIL)
    W(lambda u, z: (z < 1.04) & (np.abs(np.abs(u - BOX_HW) - REAR_X) < 0.32), M_TYRE)


# ================================================================ weather
def weather(c):
    import weathering
    lens = tuple(M_LENS.values())
    w = weathering.Weather(c, clean=(M_GLASS, M_MIRROR) + lens,
                           steel=(M_CAB, M_BOX, M_CAB_FAR, M_BOX_FAR, M_ROOF, M_ALU, M_DOOR,
                                  M_TANK, M_GUARD, M_PLATE, M_TAPE, M_PLASTIC, M_STEP, M_GRILLE, M_HOUSING))
    w.grime(0.03)
    # box sides: road film from the foot, spray behind the rear wheels,
    # faint runs from the top rail
    x, y, wd, h = REG["box_side"]
    oy = y + PAD
    w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.07 * np.exp(
        -((Y_ - oy) / PPM) / 0.35) * (0.6 + 0.4 * nz("blotch")), (M_BOX,))
    sp = lambda X_: np.exp(-(((X_ - x - PAD) / PPM + BOX_S0 - 6.3) / 0.9) ** 2)  # noqa: E731
    w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.05 * sp(X_) * np.exp(
        -((Y_ - oy) / PPM) / 0.6), (M_BOX,))
    w.runs(x, x + wd, y, y + h - PAD - (BOX_Z1 - RAIL_HI[0]) * PPM, (M_BOX,), 0.05, 90.0)
    w.wash((M_BOX,), 0.006)
    # box front: a light film above the deflector
    x, y, wd, h = REG["box_front"]
    w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.03 * (0.5 + 0.5 * nz("blotch")),
          (M_BOX,))
    # rear: lower half of the door and frame grimy from the wake
    x, y, wd, h = REG["box_rear"]
    oy = y + PAD
    w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.30 * np.clip(
        1.0 - ((Y_ - oy) / PPM) / 1.4, 0, 1) * (0.6 + 0.4 * nz("blotch")),
        (M_DOOR, M_ALU, M_TAPE))
    w.runs(x, x + wd, y, y + h - 20, (M_DOOR,), 0.08, 60.0)
    # roof: dust settles, darker toward the edges
    x, y, wd, h = REG["box_roof"]
    w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.10 * (0.4 + 0.6 * nz("big")),
          (M_ROOF,))
    # cab band: spray behind the arch, a film over the lower panels
    x, y, wd, h = REG["cab_band"]
    w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.08 * np.exp(
        -np.clip((Y_ - y - PAD) / PPM - (cab_v(Z_DOOR)), 0, None) / 0.25)
        * (0.6 + 0.4 * nz("blotch")), (M_CAB,))
    w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.14 * (0.5 + 0.5 * nz("blotch")),
          (M_PLASTIC,))
    # deflector front lip: insects and road dust
    x, y, wd, h = REG["defl"]
    w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.07 * np.exp(
        -((Y_ - y - PAD) / PPM) / 0.25) * (0.5 + 0.5 * nz("blotch"))
        + 0.06 * nz("speck") * np.exp(-((Y_ - y - PAD) / PPM) / 0.4), (M_CAB,))
    # bumper and steps, the chassis, mudflaps, guards: road dirt
    for reg, amt in (("bumper", 0.12), ("step", 0.20), ("dark", 0.22), ("liner", 0.35),
                     ("rubber", 0.30), ("guard", 0.18), ("alu_low", 0.30), ("tank", 0.12),
                     ("rail", 0.18), ("plastic", 0.10), ("tread_f", 0.25),
                     ("tread_r", 0.25), ("housing", 0.10)):
        x, y, wd, h = REG[reg]
        w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz, amt=amt: amt * (
            0.5 + 0.5 * nz("blotch")))
    for reg in ("wheel_f", "wheel_r"):
        x, y, wd, h = REG[reg]
        w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.16 * (0.5 + 0.5 * nz("blotch")),
              (M_TYRE, M_RIM, M_HUB))
        w.add("R", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.06 * nz("speck"), (M_RIM,))
    w.fade((M_CAB,), 0.04, 0.0)
    return w


# ================================================================ export
EMIT = None


def emission_table():
    t = {}
    for name, mid in M_LENS.items():
        t[mid] = vi.LENS_LIT[LENS_COLOUR[name]]
    t[M_GLASS] = (255, 255, 255)
    return t


def export(out_dir, ss=atlas.SS):
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    w = weather(c)
    c.pad()
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.006)
    glass = atlas.coverage(c, M_GLASS)
    mask = glass >= 0.5
    path = os.path.join(out_dir, ASSET)
    out = []
    rough = 0.03 * atlas.noise(c, 31, 12.0)
    out.append(atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"))
    out.append(atlas.save(atlas.normal_map(c, flat_ids=(M_GLASS,)), path + "_normal.png"))
    emit = atlas.emission_colours(c, emission_table())
    cabin = glazing.night_rooms(mask, np.where(mask[..., None], 255.0, 0.0)) * CABIN_LEVEL
    emit = np.where(mask[..., None], cabin, np.where(glass[..., None] > 0, 0.0, emit))
    out.append(atlas.save(emit, path + "_emission.png"))
    for v, _paint in VARIANTS:
        rgb = atlas.albedo(c, lut(v), grime=0.25 * cav)
        rgb = vehicle_glass(mask, rgb)
        out.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    out.append(vi.save_glass_texels(mask, os.path.join(HERE, vi.GLASS_TEXELS)))
    del w
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["export"]:
        for p in export(os.path.join(HERE, "export")):
            print(p)
    else:
        print(__doc__)
