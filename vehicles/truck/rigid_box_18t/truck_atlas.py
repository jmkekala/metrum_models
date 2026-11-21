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

# The shell: the dark lower module (bumper, corner and step fairings) and the
# cab on it, one loft of plan rings (z, sc, bow, wf, rf, sb, wb, rb): sc the
# front station on the centre line, the front a parabola in plan that falls
# back by *bow* to the corner radius rf, wf the half width where the side
# starts, sb the back station, wb the half width there, rb the rear radius.
CAB_HW = 1.15                         # the cab at its foot
BELT_HW = 1.162                       # and at the belt, where its sides are widest
LOW_HW = 1.19                         # the lower module's sides, 40 mm proud
CAB_BACK = 1.80
BOW = 0.11
Z_FOOT = 0.38                         # the valance's lower edge
Z_CHIN = 0.585                        # the bumper face's foot, over the set-back chin
Z_LEDGE = 1.00                        # the bumper's top, the painted cab's foot
Z_DOOR = 1.10                         # painted cab side above, dark plastic below
Z_BELT = 1.54
Z_SCREEN = (1.62, 2.52)               # the screen panel, raked 10 degrees
SHELL_RINGS = [
    (Z_FOOT, 0.085, BOW, 1.165, 0.22, 1.80, 1.165, 0.05),   # valance, tucked back
    (0.43, 0.035, BOW, 1.180, 0.22, 1.80, 1.180, 0.05),     # the chin, 35 mm behind the face
    (Z_CHIN - 0.03, 0.035, BOW, 1.180, 0.22, 1.80, 1.180, 0.05),
    (Z_CHIN, 0.000, BOW, LOW_HW, 0.22, 1.80, LOW_HW, 0.05),  # the face carrying the lamps
    (0.955, 0.000, BOW, LOW_HW, 0.22, 1.80, LOW_HW, 0.05),
    (0.995, 0.030, BOW, 1.175, 0.22, 1.80, 1.175, 0.05),    # the bumper's top edge
    (Z_LEDGE, 0.085, BOW, CAB_HW, 0.24, 1.80, CAB_HW, 0.07),  # the cab's foot, a ledge back
    (Z_DOOR, 0.086, BOW, 1.152, 0.24, 1.80, 1.152, 0.07),
    # the belt: the front panel's brow, 35 mm proud of the screen's foot, and
    # the crown of the sides
    (Z_BELT, 0.080, BOW, BELT_HW, 0.22, 1.80, BELT_HW, 0.07),
    (Z_SCREEN[0], 0.115, BOW, 1.150, 0.15, 1.80, 1.150, 0.07),   # shoulder: the pillar's tighter corner
    (Z_SCREEN[1], 0.275, BOW, 1.095, 0.13, 1.80, 1.095, 0.07),   # sides lean in 3.5 degrees
    (2.665, 0.318, BOW, 1.072, 0.13, 1.79, 1.072, 0.06),
    (2.75, 0.460, 0.09, 0.985, 0.10, 1.755, 0.985, 0.04),
]
N_LOWER = 6                           # rings 0..5 are the lower module
I_CHIN, I_FACE, I_TOP = (1, 2), (3, 4), 5   # the chin's and the face's rings, the rolled top
I_LEDGE, I_DOOR, I_BELT, I_SCR0, I_SCR1, I_ROOF = 6, 7, 8, 9, 10, 12

# openings on the front (|x|, z): the screen a trapezoid with rounded corners,
# the grille a trapezoid wider at its foot
WSCREEN = (0.995, 1.665, 0.955, 2.495, 0.09)   # half width at foot, z0, at head, z1, corner radius
GRILLE = (0.76, 1.045, 0.64, 1.42, 0.045)
COWL_Z = 1.60                         # dark wiper cowl from here up to the screen
CORNER_X = 0.90                       # the corner panels' shut line on the front
# The front flap between the corner panels: its top shut line under the brow,
# a shallow recessed field round the grille, and in the band over it a centre
# intake slot between two grab handle recesses.
FLAP_TOP = 1.528
FIELD = (0.815, 1.02, 0.70, 1.452, 0.05, 0.010)   # as GRILLE, then its depth
SLOT_F = (0.21, 1.492, 0.014)         # centre intake slot: half width, z, half height
GRAB_F = (0.56, 0.76, 1.492, 0.022)   # grab handle recesses: |x|0, |x|1, z, half height
PIVOT_X = 0.45                        # the two wiper pivots' bosses on the cowl, |x| (the texture is mirrored)
# Corner air deflectors: a painted blade rooted in the front panel and standing
# off the cab's corner toward its tail, an open slot behind it. z0, z1 and
# stations (arc fraction, outer and inner face off the corner's surface).
BLADE_Z = (1.035, 1.52)
BLADE = ((0.10, -0.012, -0.036), (0.38, 0.010, -0.018), (0.62, 0.030, 0.014),
         (0.86, 0.048, 0.034))
BLADE_SLOT = (0.50, 0.90)             # the dark slot drawn on the corner panel behind it
BLADE_LOD1 = ((0.45, 0.040, 0.026), (0.86, 0.060, 0.046))   # off LOD1's own, more conical corner
# the side (s, z)
DOOR = (0.445, 1.40)                  # door shut lines, s, below the belt
DOOR_TOP = 2.49
PILLAR = 0.156                        # the A-pillar's rake, s per z, above Z_SCREEN[0]
DOOR_GLASS = [(0.47, 1.56), (0.82, 1.56), (0.92, 1.70), (1.30, 1.70), (1.34, 1.74),
              (1.34, 2.37), (1.29, 2.42), (0.60, 2.42)]   # dropped front corner
DOOR_GLASS_LOD1 = [DOOR_GLASS[k] for k in (0, 1, 2, 4, 6, 7)]
REPEATER = (0.47, 0.54, 1.24, 1.30)   # s0, s1, z0, z1 on the cab side
HANDLE = (1.19, 1.37, 1.495)          # the door handle's recess: s0, s1, z
GRAB_B = (1.455, 1.25, 1.80)          # the grab handle behind the door: s, z0, z1
VENT = (1.50, 1.70, 1.76, 2.06)       # quarter panel intake: s0, s1, z0, z1
STEP_UP = (0.40, 0.80, 0.80, 0.94, 0.20)    # s0, s1, z0, z1, depth (lower module side)
STEP_LO = (0.40, 0.72, 0.46, 0.64, 0.20)
ARCH = (FRONT_AXLE, R_WHEEL, 0.64, 0.58)  # s, centre z, radius, inner |x|
FLARE = (0.615, 0.705, 1.14, 1.21, 32.0, 124.0)   # r0, r1, |x|0, |x|1, from, to (degrees)
WING = (0.645, 0.685, 0.90, 1.19, 130.0, 181.0)   # the mudguard's rear quarter, behind the cab
WING_FLAP = 0.26                      # its flap's lower edge
COLLAR = (1.775, 1.878, 1.238, 1.55, 2.694, 0.022)   # cab side collar: s at the cab, s and |x| at its
#                                     outer edge by the box corner, z0, z1, thickness

# the lower module's front (|x|, z)
HEADLAMP = (0.775, 0.735, 0.215, 0.125)  # centre |x|, z, half width, half height
LAMP_SPLIT = (0.11, -0.035, -0.070)   # indicator from here out; low | high at; DRL below
PLATE_F = (0.27, 0.436, 0.550)        # the plate on its plinth: half width, z0, z1 (on the chin)
PLINTH = 0.018                        # the plinth's depth
CSTEP = (0.44, 0.66, 0.925, 0.08)     # centre recess between the lamp pods: half width, z0, z1, depth
INTAKE = (0.34, 0.72, 0.465, 0.535)   # the chin's intake slots: |x|0, |x|1, z0, z1
FOG = (0.875, 0.497, 0.062, 0.031, 0.012)   # front fog lamps on the chin: centre |x|, z, half width, half height, depth
POD = 0.040                           # the lamp pods' dark insert, this far round each unit
POD_STEP = (0.014, 0.006)             # the step down into the unit at LOD0: its width and depth
TOWEYE = (0.50, 0.70, 0.034)          # tow-eye covers between pods and recess: |x|, z, half size
TREAD_X = 0.52                        # the step tread on the bumper's top, half width

# deflector: a moulded roof fairing, plan rings as the shell's, its nose a
# convex curve in side view
DEFL_Z0 = 2.70
DEFL_TOP = 3.56
DEFL_BACK = 1.86
# The nose: a quadratic Bezier (s, z) that leaves the roof at 44 degrees and
# reaches the top at 22, flattening all the way: neither a ramp nor a dome.
DEFL_NOSE = ((0.62, 2.745), (1.18, 3.285), (DEFL_BACK, DEFL_TOP))
DEFL_Z = (DEFL_Z0, 2.94, 3.16, 3.34, 3.46, 3.535)
DEFL_W = (1.22, 1.245)                # half width at the back (by the box corners), base and from 60 % up
DEFL_CROWN = 0.05                     # the half width lost toward the top, a rounded shoulder
DEFL_TAPER = 0.24                     # the sides close in toward the nose, x per s
DEFL_FIELD = (0.17, 0.14, 0.20, 0.008)   # the front's recessed field: in from the corner arc, from
#                                     the foot, from the top (along the nose), depth

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
TANK = (2.17, 3.07, 0.70, 0.70, 0.27)  # s0, s1, |x| centre, z centre, radius (left)
BATTERY = (2.17, 2.82, 0.427, 0.98, 0.52, 0.92)  # right
GUARD_S = (2.14, 5.20)
GUARD_X = (1.195, 1.225)
GUARD_Z = ((0.46, 0.56), (0.76, 0.86))
GUARD_BRACKETS = (2.24, 3.65, 5.12)
BAR = (7.66, 7.80, 1.18, 0.40, 0.55)   # s0, s1, half width, z0, z1
REAR_LAMP = (7.70, 7.84, 0.78, 1.16, 0.55, 0.73)   # s0, s1, |x|0, |x|1, z0, z1
REAR_LENS_Z = (0.585, 0.705)
# rear cells from the outer edge in: (|x| outer, |x| inner, kind); fog on the left
REAR_CELLS_L = [(1.16, 1.08, 4), (1.08, 0.96, 3), (0.96, 0.87, 11), (0.87, 0.78, 6)]
REAR_CELLS_R = [(1.16, 1.08, 5), (1.08, 0.96, 3), (0.96, 0.87, "reflector"), (0.87, 0.78, 6)]
PLATE_R = (0.26, 0.42, 0.53)
MUDGUARD = (5.22, 6.58, 0.58, 1.255, 1.07, 1.11)   # s0, s1, |x|0, |x|1, z0, z1 (LOD1's flat guard)
MUDGUARD_ARC = (0.577, 0.615, 20.0, 160.0)   # LOD0's, round the twins: radii about the axle, from, to

# glass and lamp groups the truck carries
MARKER = 15

# ================================================================ atlas
REG = {
    "box_side": (4, 4, 388, 166), "box_rear": (400, 4, 166, 166),
    "box_front": (20, 640, 166, 166), "cab_band": (752, 4, 268, 178),
    "box_roof": (4, 178, 388, 166), "cab_roof": (400, 178, 152, 104),
    "defl": (708, 192, 164, 112), "grille": (584, 192, 108, 32),
    "tread_f": (4, 352, 216, 24), "tread_r": (4, 382, 216, 46),
    "wheel_f": (228, 352, 76, 76), "wheel_r": (312, 352, 76, 76),
    "glass_ws": (396, 352, 136, 60), "glass_side": (540, 352, 62, 60),
    "lod3_side": (612, 352, 132, 64), "lod3_front": (752, 352, 46, 64),
    "lod3_rear": (806, 352, 46, 64),
    "rail": (4, 448, 388, 16),
    "plate": (4 + 64 * 10, 578, 40, 12),
}
# Small patches each alone in a 32-texel block on a 64-texel grid, so the
# mips down to level 5 (32 x 32 blocks, beyond 400 m) average one colour:
# a red marker lens no longer bleeds into the black visor's patch.
PATCHES = ("dark", "liner", "alu", "reflector", "tank", "guard", "rubber", "plastic",
           "step", "housing", "mirror", "seal", "mirror_body", "bezel", "mesh", "cabpaint")
for _k, _n in enumerate(PATCHES):
    REG[_n] = (2 + 64 * _k, 514, 28, 28)
LENS_KINDS = ("low", "high", "drl", "ind", "tail_brake", "reverse", "fog", "mark_white",
              "mark_amber", "mark_red", "fog_front")
for _k, _n in enumerate(LENS_KINDS):
    REG["lens_" + _n] = (4 + 64 * (_k + (_k > 9)), 578, 24, 24)    # block 10 is the plate's
# The headlamp unit's lenses are mapped whole, at about 240 texels per metre,
# in the open field right of the box front: the white ones together, the
# amber indicator a block away.
REG["insert"] = (2 + 64 * 12, 578, 28, 28)
REG.update({"lens_high": (260, 660, 48, 52), "lens_low": (324, 660, 40, 52),
            "lens_drl": (260, 728, 84, 18), "lens_ind": (452, 660, 30, 66)})
PAD = 2.0                              # region origin to the first mapped texel
LOD3_PPM = 16.0


def lens_kind(lamp, colour=None):
    """Atlas lens patch for a lamp id (and a marker's colour)."""
    if lamp == MARKER:
        return "lens_mark_" + colour
    return "lens_" + {7: "low", 8: "high", 9: "drl", 4: "ind", 5: "ind", 3: "tail_brake",
                      6: "reverse", 11: "fog", 10: "fog_front"}[lamp]


def at(reg, u_m, v_m, ppm=PPM):
    """Atlas pixels of a point u_m, v_m metres into region *reg*."""
    x, y, _w, _h = REG[reg]
    return (x + PAD + u_m * ppm, y + PAD + v_m * ppm)


# ----------------------------------------------------------- plan rings
def plan_frame(sc, bow, wf, rf, sb, wb, rb):
    """Where a plan ring's pieces meet (numpy-friendly): xe, the bowed
    front's half width; th0, the front's tangent angle there; tau, the
    side's taper angle; (cx, cs), the corner arc's centre; se, the station
    where the side starts; ls, the side's length."""
    xe = wf - rf
    tau = np.zeros_like(xe, dtype=float) if isinstance(xe, np.ndarray) else 0.0
    for _ in range(10):
        th0 = np.arctan2(2.0 * bow, xe)
        xe = wf - rf * (np.cos(tau) - np.sin(th0))
        se = sc + bow + rf * (np.cos(th0) - np.sin(tau))
        tau = np.arctan2(wb - wf, sb - rb - se)
    th0 = np.arctan2(2.0 * bow, xe)
    cx, cs = xe - rf * np.sin(th0), sc + bow + rf * np.cos(th0)
    se = cs - rf * np.sin(tau)
    ls = np.hypot(wb - wf, sb - rb - se)
    return xe, th0, tau, cx, cs, se, ls


def plan_half(ring, nbow=3, nf=4, nb=2):
    """The x >= 0 half of one plan ring from the front centre to the back
    centre: [(x, s, U)], U the perimeter parameter in metres (x across the
    bowed front, true length on the arcs and the side)."""
    _z, sc, bow, wf, rf, sb, wb, rb = ring
    xe, th0, tau, cx, cs, se, ls = (float(v) for v in plan_frame(sc, bow, wf, rf, sb, wb, rb))
    out = [(xe * k / nbow, sc + bow * (k / nbow) ** 2, xe * k / nbow) for k in range(nbow + 1)]
    th1 = math.pi / 2 - tau
    for k in range(1, nf + 1):
        th = th0 + (th1 - th0) * k / nf
        out.append((cx + rf * math.sin(th), cs - rf * math.cos(th), xe + rf * (th - th0)))
    u2 = xe + rf * (th1 - th0)
    if nb == 0:
        ll = math.hypot(wb - wf, sb - se)
        return out + [(wb, sb, u2 + ll), (0.0, sb, u2 + ll + wb)]
    u3 = u2 + ls
    out.append((wb, sb - rb, u3))
    for k in range(1, nb):
        t = 0.5 * math.pi * k / nb
        out.append((wb - rb + rb * math.cos(t), sb - rb + rb * math.sin(t), u3 + rb * t))
    u4 = u3 + rb * math.pi / 2
    out.append((wb - rb, sb, u4))
    out.append((0.0, sb, u4 + wb - rb))
    return out


class Loft:
    """A stack of plan rings and its band of the atlas: U round the
    perimeter from the front centre, V the profile length up the front
    centre line (so a ledge between two rings at one height has its own
    rows)."""

    def __init__(self, rings, reg, v=None):
        self.rings = [tuple(float(c) for c in r) for r in rings]
        self.reg = reg
        if v is None:
            v = [0.0]
            for a, b in zip(self.rings, self.rings[1:]):
                v.append(v[-1] + math.hypot(b[1] - a[1], b[0] - a[0]))
        self.v = [float(c) for c in v]

    def px(self, U, V):
        return at(self.reg, U, V)

    def ring_at(self, z, lo=0, hi=None):
        """The ring at height z, between rings lo..hi."""
        hi = len(self.rings) - 1 if hi is None else hi
        zs = [self.rings[i][0] for i in range(lo, hi + 1)]
        return (float(z),) + tuple(
            float(np.interp(z, zs, [self.rings[i][k] for i in range(lo, hi + 1)]))
            for k in range(1, 8))

    def v_at(self, z, lo=0, hi=None):
        hi = len(self.rings) - 1 if hi is None else hi
        return float(np.interp(z, [self.rings[i][0] for i in range(lo, hi + 1)],
                               self.v[lo:hi + 1]))

    def front(self, x, z, lo=0, hi=None, nbow=None):
        """Station of the bowed front at (x, z); with *nbow* the chords a
        mesh of that many segments a side makes of it."""
        r = self.ring_at(z, lo, hi)
        xe = float(plan_frame(*r[1:])[0])
        t = min(abs(x) / xe, 1.0)
        if nbow:
            k = min(int(t * nbow), nbow - 1)
            t0, t1 = k / nbow, (k + 1) / nbow
            return r[1] + r[2] * (t0 ** 2 + (t1 ** 2 - t0 ** 2) * (t - t0) / (t1 - t0))
        return r[1] + r[2] * t * t

    def xe(self, z, lo=0, hi=None):
        return float(plan_frame(*self.ring_at(z, lo, hi)[1:])[0])

    def side(self, z, lo=0, hi=None):
        """(half width, station) where the side starts at height z."""
        r = self.ring_at(z, lo, hi)
        return r[3], float(plan_frame(*r[1:])[5])

    def world(self, U, V, back_pad=0.0):
        """Band (U, V) in metres to world (x, s, z), the segment (0 front,
        1 front arc, 2 side, 3 rear arc, 4 back) and the arc fraction,
        elementwise. *back_pad* starts the back that far early."""
        cols = [np.interp(V, self.v, [r[k] for r in self.rings]) for k in range(8)]
        z, sc, bow, wf, rf, sb, wb, rb = cols
        xe, th0, tau, cx, cs, se, ls = plan_frame(sc, bow, wf, rf, sb, wb, rb)
        th1 = np.pi / 2 - tau
        u1 = xe
        u2 = u1 + rf * (th1 - th0)
        u3 = u2 + ls
        u4 = u3 + rb * np.pi / 2
        seg = np.select([U < u1, U < u2, U < u3, U < u4 - back_pad], [0, 1, 2, 3], 4)
        th = np.clip(th0 + (U - u1) / rf, th0, th1)
        t = np.clip((U - u2) / np.maximum(ls, 1e-6), 0, 1)
        ph = np.clip((U - u3) / np.maximum(rb, 1e-6), 0, np.pi / 2)
        x = np.select([seg == 0, seg == 1, seg == 2, seg == 3],
                      [U, cx + rf * np.sin(th), wf + (wb - wf) * t, wb - rb + rb * np.cos(ph)],
                      np.maximum(wb - rb - (U - u4), 0))
        s = np.select([seg == 0, seg == 1, seg == 2, seg == 3],
                      [sc + bow * (U / xe) ** 2, cs - rf * np.cos(th),
                       se + (sb - rb - se) * t, sb - rb + rb * np.sin(ph)], sb)
        frac = np.clip((U - u1) / (u2 - u1), 0, 1)
        return x, s, z, seg, frac


SHELL = Loft(SHELL_RINGS, "cab_band")


def _defl_rings():
    (s0, z0), (s1, z1), (s2, z2) = DEFL_NOSE
    out = []
    for z in DEFL_Z:
        # the nose's station at this height: solve the Bezier's z(t) = z
        a, b, c = z0 - 2 * z1 + z2, 2 * (z1 - z0), z0 - max(z, z0)
        t = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a) if abs(a) > 1e-9 else -c / b
        sc = (1 - t) ** 2 * s0 + 2 * t * (1 - t) * s1 + t * t * s2
        k = (z - DEFL_Z0) / (DEFL_TOP - DEFL_Z0)
        k = min(1.0, k * 1.6)                        # full width from 60 % up
        wb = DEFL_W[0] + (DEFL_W[1] - DEFL_W[0]) * k
        f = (z - DEFL_Z0) / (DEFL_TOP - DEFL_Z0)
        wb -= DEFL_CROWN * max(0.0, (f - 0.75) / 0.25) ** 2      # the top edge rounded over
        depth = DEFL_BACK - sc
        wf = wb - DEFL_TAPER * depth
        out.append((z, sc, min(0.10, depth * 0.25), wf, min(0.22, depth * 0.45), DEFL_BACK,
                    wb, 0.0))
    return out


DEFL = Loft(_defl_rings(), "defl")


# ================================================================ materials
(M_CAB, M_BOX, M_ROOF, M_PLASTIC, M_DARK, M_LINER, M_ALU, M_TANK, M_GUARD, M_RUBBER,
 M_TYRE, M_RIM, M_HUB, M_GLASS, M_MIRROR, M_PLATE, M_PLATE_EDGE, M_HOUSING, M_GRILLE,
 M_GRILLE_HOLE, M_DOOR, M_STEP, M_SEAL, M_TAPE, M_TAPE_RED, M_PIC_LAMP, M_PIC_TAIL,
 M_HANDLE, M_ALU_DARK) = range(1, 30)
M_BEZEL = 32                    # the headlamp units' light reflector walls
M_INSERT = 33                   # gloss black inserts round the lamp units
M_LENS_DIV = 34                 # light chrome dividers inside the lamp units, lit with them
# The LOD3 pictures' own paint: the whole far side and front are one or two
# painted faces, so their windows, grille and lower plastic sit inside the
# painted mean; a lighter far field keeps the tier as bright as LOD0 under
# the same paint (the consumer's tier-switch rule, within 10 %).
M_CAB_FAR, M_BOX_FAR = 30, 31
FAR_GREY = 0.83                 # linear
M_LENS = {"low": 40, "high": 41, "drl": 42, "ind": 43, "tail_brake": 44, "reverse": 45,
          "fog": 46, "mark_white": 47, "mark_amber": 48, "mark_red": 49, "fog_front": 50}
LENS_COLOUR = {"low": "white", "high": "white", "drl": "white", "ind": "amber",
               "tail_brake": "red", "reverse": "white", "fog": "red", "mark_white": "white",
               "mark_amber": "amber", "mark_red": "red", "fog_front": "white"}
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
    M_HUB: (70, 71, 72), M_GLASS: glazing.BASE, M_MIRROR: (58, 61, 64),
    M_PLATE: (236, 236, 232), M_PLATE_EDGE: (40, 40, 42), M_HOUSING: (64, 65, 66),
    M_GRILLE: (40, 41, 42), M_GRILLE_HOLE: (16, 16, 17), M_DOOR: (196, 198, 198),
    M_STEP: (44, 44, 45), M_SEAL: (24, 24, 25), M_TAPE: (214, 170, 40),
    M_TAPE_RED: (170, 40, 34), M_PIC_LAMP: (150, 152, 150), M_PIC_TAIL: (110, 28, 24),
    M_HANDLE: (30, 30, 31), M_ALU_DARK: (120, 122, 123), M_BEZEL: (186, 188, 190),
    M_INSERT: (27, 27, 28), M_LENS_DIV: (226, 228, 231),
    M_CAB_FAR: (0, 0, 0), M_BOX_FAR: (0, 0, 0),         # set below from FAR_GREY
}
LENS_UNLIT = {"low": (202, 205, 208), "high": (198, 201, 205), "drl": (213, 215, 218),
              "ind": (206, 124, 34), "fog_front": (198, 201, 205), "tail_brake": (124, 26, 24), "reverse": (178, 180, 180),
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
    M_BEZEL: (0.28, 0.0), M_INSERT: (0.34, 0.0), M_LENS_DIV: (0.18, 0.0),
}
for _m in M_LENS.values():
    SURFACE[_m] = (0.12, 0.0)
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
    # the door's guide tracks, its bottom rail and rubber seal, a lock and a
    # pull strap
    P.where("box_rear", lambda u, v: door(u, v) & (np.abs(u - BOX_HW) > REAR_POST_HW - 0.035),
            mid=M_ALU_DARK, add_h=0.003)
    P.where("box_rear", lambda u, v: door(u, v) & (v + BOX_Z0 < SILL_Z + 0.11), mid=M_ALU,
            height=0.004)
    P.where("box_rear", lambda u, v: door(u, v) & (v + BOX_Z0 < SILL_Z + 0.024), mid=M_RUBBER,
            height=0.0)
    P.where("box_rear", lambda u, v: (np.abs(u - BOX_HW) < 0.075)
            & (np.abs(v + BOX_Z0 - SILL_Z - 0.066) < 0.032), mid=M_HANDLE, add_h=0.012)
    P.where("box_rear", lambda u, v: (np.abs(u - BOX_HW - 0.42) < 0.014)
            & (v + BOX_Z0 > SILL_Z + 0.11) & (v + BOX_Z0 < SILL_Z + 0.36), mid=M_RUBBER,
            add_h=0.003)
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
def inside(poly, a, b):
    """Even-odd point-in-polygon test of arrays a, b against [(a, b), ...]."""
    m = np.zeros(np.shape(a), bool)
    n = len(poly)
    for i in range(n):
        (a0, b0), (a1, b1) = poly[i], poly[(i + 1) % n]
        if b0 == b1:
            continue
        hit = ((b0 > b) != (b1 > b)) & (a < a0 + (a1 - a0) * (b - b0) / (b1 - b0))
        m ^= hit
    return m


def trapezoid_hw(t, z):
    """Half width at height z of a trapezoid (hw0, z0, hw1, z1, ...)."""
    hw0, z0, hw1, z1 = t[:4]
    return hw0 + (hw1 - hw0) * np.clip((z - z0) / (z1 - z0), 0, 1)


def rounded_outline(t, nseg=2):
    """The x >= 0 half of a symmetric trapezoid with rounded corners (hw0,
    z0, hw1, z1, r), from the foot's centre round to the head's centre:
    [(x, z)], nseg segments a corner."""
    hw0, z0, hw1, z1, r = t
    lean = math.atan2(hw0 - hw1, z1 - z0)         # the side's lean inward
    out = [(0.0, z0)]
    # foot corner: turns from +x to the side's direction, through 90 + lean degrees
    a_end = math.pi / 2 + lean
    k = math.tan(a_end / 2)                       # tangent length factor
    cx, cz = hw0 - r * k, z0 + r
    for i in range(nseg + 1):
        a = a_end * i / nseg
        out.append((cx + r * math.sin(a), cz - r * math.cos(a)))
    b_end = math.pi / 2 - lean
    k = math.tan(b_end / 2)
    cx, cz = hw1 - r * k, z1 - r
    for i in range(nseg + 1):
        a = a_end + b_end * i / nseg
        out.append((cx + r * math.sin(a), cz - r * math.cos(a)))
    out.append((0.0, z1))
    return out


def door_front(z):
    """The door's front shut line: straight up to the screen's foot, then
    up the A-pillar."""
    return DOOR[0] + PILLAR * np.clip(z - Z_SCREEN[0], 0, None)


def paint_cab(P):
    c = P.c
    x0, y0, w, h = REG["cab_band"]
    sy, sx, Y_, X_ = c.field(x0, x0 + w, y0, y0 + h)
    U = (X_ - x0 - PAD) / PPM
    V = (Y_ - y0 - PAD) / PPM
    tx = 1.0 / PPM
    x, s, z, seg, frac = SHELL.world(U, V, back_pad=tx)
    rv = SHELL.v
    mid = np.full(U.shape, M_CAB, np.uint8)
    hgt = np.zeros(U.shape, np.float32)
    shade = np.ones(U.shape, np.float32)
    ao = np.ones(U.shape, np.float32)
    side, front, arc = seg == 2, seg == 0, seg == 1
    # Dark plastic: the lower module with its ledge, and the cab's sides and
    # back below the door line. Each runs a texel past its faces' outline,
    # so no unpainted face samples the paint.
    lower = V < rv[I_LEDGE] + tx
    lowside = (V < rv[I_DOOR] + tx) & ((seg >= 2) | (frac > 0.94))
    mid[lower | lowside] = M_PLASTIC
    cab = ~lower

    def groove(m, d=0.002, sh=0.6):
        hgt[m] -= d
        shade[m] *= sh
        ao[m] = np.minimum(ao[m], 0.7)

    gw = 2.0 / PPM                                # a shut line: two texels

    def gap(m):
        """A panel shut line: a dark gap two texels wide, grooved."""
        hgt[m] -= 0.004
        shade[m] *= 0.34
        ao[m] = np.minimum(ao[m], 0.5)

    # ------------------------------------------------------------ the side
    d0, d1 = DOOR
    df = door_front(z)
    arch_top = R_WHEEL + FLARE[1]
    gap(cab & side & (np.abs(s - df) < gw / 2) & (z > Z_DOOR) & (z < DOOR_TOP))
    gap(cab & side & (np.abs(s - d1) < gw / 2) & (z > arch_top) & (z < DOOR_TOP))
    gap(cab & side & (np.abs(z - DOOR_TOP) < gw / 2) & (s > df) & (s < d1))
    gap(cab & side & (np.abs(z - Z_DOOR - 0.014) < gw / 2) & (s > d0) & (s < 1.14))
    # the arch's black lip, drawn where LOD0's fender lip stands, so LOD1 and
    # LOD2 keep it
    ra = np.hypot(s - FRONT_AXLE, z - R_WHEEL)
    ang = np.degrees(np.arctan2(z - R_WHEEL, FRONT_AXLE - s))
    mid[cab & side & (ra < FLARE[1] - 0.004) & (ang > FLARE[4] + 1.0) & (ang < FLARE[5] - 1.0)] \
        = M_PLASTIC
    # door glass: the opening dark, for LOD2 and round the recess
    win = cab & side & inside(DOOR_GLASS, s, z)
    mid[win] = M_SEAL
    # the door handle: a pull across a rounded dark recess
    h0, h1, hz = HANDLE
    dh = np.hypot(np.maximum(np.abs(s - (h0 + h1) / 2) - ((h1 - h0) / 2 - 0.04), 0), z - hz)
    hdl = cab & side & (dh < 0.04)
    mid[hdl] = M_HANDLE
    hgt[hdl] -= 0.012
    ao[hdl] = 0.6
    bar = cab & side & (s > h0 + 0.02) & (s < h1 - 0.02) & (np.abs(z - hz - 0.008) < 0.011)
    mid[bar] = M_PLASTIC
    hgt[bar] += 0.010
    # the grab handle behind the door: a dark bar standing in a shallow recess
    gs, gz0, gz1 = GRAB_B
    dg = np.hypot(s - gs, np.maximum(np.abs(z - (gz0 + gz1) / 2) - ((gz1 - gz0) / 2 - 0.03), 0))
    rec = cab & side & (dg < 0.04)
    hgt[rec] -= 0.006
    shade[rec] *= 0.80
    ao[rec] = np.minimum(ao[rec], 0.7)
    gbar = cab & side & (np.abs(s - gs) < 0.017) & (z > gz0 + 0.02) & (z < gz1 - 0.02)
    mid[gbar] = M_HANDLE
    hgt[gbar] += 0.012
    # the quarter panel behind the door: an intake grille
    v0, v1, vz0, vz1 = VENT
    vent = cab & side & (s > v0) & (s < v1) & (z > vz0) & (z < vz1)
    mid[vent] = M_GRILLE
    slots = vent & (np.mod(z - vz0, 0.032) < 0.014)
    mid[slots] = M_GRILLE_HOLE
    hgt[vent & ~slots] += 0.004
    # the step fairing under the door: the wells dark, tread lines (the
    # LOD0 wells are cut; LOD1 and LOD2 show these)
    for a0, a1, b0, b1, _d in (STEP_UP, STEP_LO):
        well = lower & side & (s > a0) & (s < a1) & (z > b0) & (z < b1)
        mid[well] = M_STEP
        shade[well] *= 0.70
        tread = well & (z < b0 + 0.035)
        shade[tread] *= 1.9
        hgt[well] -= 0.004
    # the bumper's parting line under its rolled top edge, all round
    groove((V > rv[I_FACE[1]] - 0.022) & (V < rv[I_FACE[1]] - 0.010) & (seg <= 2), d=0.002,
           sh=0.72)

    # ----------------------------------------------------------- the front
    # the screen's dark surround: seal round the pane, the wiper cowl under it
    # with its vent slats and the wiper pivots' bosses
    wz0, wz1 = WSCREEN[1], WSCREEN[3]
    whw = trapezoid_hw(WSCREEN, z)
    sur = cab & (seg <= 1) & (x < whw + 0.032) & (z > COWL_Z) & (z < wz1 + 0.026)
    mid[sur] = M_SEAL
    cowl = cab & (seg <= 1) & (x < whw + 0.032) & (z > COWL_Z) & (z < wz0)
    slat = cowl & (x < whw - 0.03) & (np.mod(z - COWL_Z, 0.022) < 0.009)
    mid[slat] = M_PLASTIC
    hgt[slat] += 0.004
    boss = cowl & (np.hypot(x - PIVOT_X, z - (COWL_Z + wz0) / 2) < 0.028)
    mid[boss] = M_HOUSING
    hgt[boss] += 0.012
    # the front flap: a shut line all round it (the corner panels' lines and
    # one under the brow)
    gap(cab & front & (np.abs(x - CORNER_X) < gw / 2) & (z > Z_LEDGE + 0.03) & (z < FLAP_TOP))
    gap(cab & front & (np.abs(z - FLAP_TOP) < gw / 2) & (x < CORNER_X))
    # a shallow recessed field with rounded corners round the grille: relief
    # only, its edge a soft bevel 12 mm wide
    fhw = trapezoid_hw(FIELD, z)
    fr = FIELD[4]
    ex, ez = fhw - x, np.minimum(z - FIELD[1], FIELD[3] - z)
    dfield = np.where((ex < fr) & (ez < fr), fr - np.hypot(fr - ex, fr - ez), np.minimum(ex, ez))
    infield = cab & front & (dfield > 0)
    hgt[infield] -= FIELD[5] * np.clip(dfield[infield] / 0.012, 0.0, 1.0)
    # the grille in it: dark slats over darkness, its frame a little proud
    gz0, gz1 = GRILLE[1], GRILLE[3]
    ghw = trapezoid_hw(GRILLE, z)
    gr = cab & front & (x < ghw) & (z > gz0) & (z < gz1)
    mid[gr] = M_GRILLE
    holes = gr & (x < ghw - 0.03) & (z > gz0 + 0.025) & (z < gz1 - 0.025) \
        & (np.mod(z - gz0 - 0.025, 0.066) > 0.026)
    mid[holes] = M_GRILLE_HOLE
    hgt[gr & ~holes] += 0.008
    # over it: a centre intake slot between two grab handle recesses
    sh, sz, shh = SLOT_F
    dslot = np.hypot(np.maximum(x - (sh - shh), 0), z - sz)
    slot = cab & front & (dslot < shh)
    mid[slot] = M_GRILLE_HOLE
    hgt[slot] -= 0.012
    ao[slot] = 0.55
    lip = cab & front & (dslot >= shh) & (dslot < shh + 0.012)
    hgt[lip] += 0.003
    g0, g1, gz, ghh = GRAB_F
    dgr = np.hypot(np.maximum(np.abs(x - (g0 + g1) / 2) - ((g1 - g0) / 2 - ghh), 0), z - gz)
    grab = cab & front & (dgr < ghh)
    mid[grab] = M_HANDLE
    hgt[grab] -= 0.014
    ao[grab] = 0.55
    gbar = grab & (np.abs(z - gz - 0.004) < 0.008) & (np.abs(x - (g0 + g1) / 2) < (g1 - g0) / 2 - 0.02)
    mid[gbar] = M_PLASTIC
    hgt[gbar] += 0.012
    # the corner air deflectors: the dark slot behind the blade's tail, drawn
    # on the corner panel (LOD2 has no blade and shows it alone)
    f0, f1 = BLADE_SLOT
    slot = cab & arc & (frac > f0) & (frac < f1) & (z > BLADE_Z[0]) & (z < BLADE_Z[1])
    mid[slot] = M_GRILLE_HOLE
    ao[slot] = 0.6

    # ---------------------------------------------------- the lower module
    lf = lower & front & (V < rv[I_TOP])
    # the chin: the plate (LOD1 and LOD2; LOD0's plinth stands over it) in a
    # dark surround, intake slots, the fog lamps' dark inserts
    ph, pz0, pz1 = PLATE_F
    pl = lf & (x < ph) & (z > pz0) & (z < pz1)
    mid[lf & (x < ph + 0.02) & (z > pz0 - 0.012) & (z < pz1 + 0.012)] = M_INSERT
    mid[pl] = M_PLATE
    mid[pl & ((x > ph - 0.012) | (z < pz0 + 0.012) | (z > pz1 - 0.012))] = M_PLATE_EDGE
    i0, i1, iz0, iz1 = INTAKE
    hz_ = (iz1 - iz0) / 2
    dist = np.hypot(np.maximum(np.abs(x - (i0 + i1) / 2) - ((i1 - i0) / 2 - hz_), 0),
                    z - (iz0 + iz1) / 2)
    intake = lf & (dist < hz_)
    mid[intake] = M_GRILLE_HOLE
    hgt[intake] -= 0.010
    ao[intake] = 0.6
    bar = intake & (np.abs(z - (iz0 + iz1) / 2) < 0.008)
    mid[bar] = M_GRILLE
    hgt[bar] += 0.008

    def insert(cx_, cz_, hu_, hv_, margin, rad):
        """A gloss black insert with a proud rim round a lamp unit."""
        ax, az = np.abs(x - cx_) - (hu_ + margin - rad), np.abs(z - cz_) - (hv_ + margin - rad)
        dd = np.hypot(np.maximum(ax, 0), np.maximum(az, 0)) + np.minimum(np.maximum(ax, az), 0) \
            - rad
        m = lf & (dd < 0)
        mid[m] = M_INSERT
        hgt[m] += 0.004 * np.clip(-dd[m] / 0.010, 0.0, 1.0)
        shade[m & (dd > -0.010)] *= 1.5            # the rim catches a little light
    fx, fz, fhu, fhv, _fd = FOG
    insert(fx, fz, fhu, fhv, 0.020, 0.025)
    # the face: the lamp pods' inserts, the recess between them drawn dark
    # with a moulded rim (a recess at LOD0), tow-eye covers
    lx, lz, lhu, lhv = HEADLAMP
    insert(lx, lz, lhu, lhv, POD, 0.05)
    ch, cz0, cz1, _cd = CSTEP
    rimc = lf & (x < ch + 0.022) & (z > cz0 - 0.022) & (z < cz1 + 0.022)
    hgt[rimc] += 0.004
    shade[rimc] *= 1.18
    cs_ = lf & (x < ch) & (z > cz0) & (z < cz1)
    mid[cs_] = M_GRILLE
    mid[cs_ & (np.mod(z - cz0, 0.04) > 0.016) & (z > cz0 + 0.03)] = M_GRILLE_HOLE
    hgt[cs_] -= 0.004
    shade[cs_] *= 0.8                             # a recess at LOD0, drawn dark here
    shade[cs_ & (z < cz0 + 0.03)] *= 1.8          # the tread's edge
    tx_, tz_, th_ = TOWEYE
    dt = np.maximum(np.abs(x - tx_), np.abs(z - tz_))
    groove(lf & (np.abs(dt - th_) < 0.005), d=0.003, sh=0.6)
    hgt[lf & (dt < th_ - 0.005)] += 0.002
    # the bumper's top: a non-slip step tread across its middle, on the rolled
    # edge and the ledge behind it
    tread = lower & front & (V > rv[I_FACE[1]] + 0.004) & (x < TREAD_X)
    mid[tread] = M_STEP
    rib = tread & (np.mod(x, 0.045) < 0.020)
    hgt[rib] += 0.003
    shade[rib] *= 1.45
    # the valance's lower edge, shaded
    shade[lower & (V < rv[1])] *= 0.85
    # the back wall: dark, unpainted, so the gap to the box reads as a clean
    # shadow
    mid[cab & (seg == 4)] = M_DARK
    c.mid[sy, sx] = mid
    c.shade[sy, sx] = shade
    c.height[sy, sx] = hgt
    c.ao[sy, sx] = ao
    # roof: u = x + 1.15, v = s - 0.30; a hatch outline
    P.fill("cab_roof", M_CAB)
    seam(P, "cab_roof", lambda u, v: (
        (np.abs(np.abs(u - CAB_HW) - 0.38) < 0.006) & (np.abs(v + 0.30 - 1.10) < 0.26)) | (
        (np.abs(np.abs(v + 0.30 - 1.10) - 0.26) < 0.006) & (np.abs(u - CAB_HW) < 0.38)))
    # deflector: U round each plan ring from the nose, V up the nose's profile
    P.fill("defl", M_CAB)
    # a shallow recessed field with rounded corners on the fairing's front
    # (relief only): it follows the nose's width, 8 mm deep, a 16 mm bevel
    xes = [float(plan_frame(*r[1:])[0]) for r in DEFL.rings]
    dx, dy, dw, dh = REG["defl"]
    sy, sx, Y_, X_ = P.c.field(dx, dx + dw, dy, dy + dh)
    U = (X_ - dx - PAD) / PPM
    V = (Y_ - dy - PAD) / PPM
    fr = 0.10
    ex = np.interp(V, DEFL.v, xes) - DEFL_FIELD[0] - U
    ev = np.minimum(V - DEFL_FIELD[1], DEFL.v[-1] - DEFL_FIELD[2] - V)
    dfl = np.where((ex < fr) & (ev < fr), fr - np.hypot(fr - ex, fr - ev), np.minimum(ex, ev))
    hh = P.c.height[sy, sx]
    hh -= DEFL_FIELD[3] * np.clip(dfl / 0.016, 0.0, 1.0)
    P.c.height[sy, sx] = hh
    # grille: horizontal slats over darkness (the LOD0 recess's floor)
    P.fill("grille", M_GRILLE_HOLE)
    P.where("grille", lambda u, v: np.mod(v - 0.025, 0.066) < 0.026, mid=M_GRILLE,
            height=0.010)


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
        hole = rim & (np.abs(r - 0.236) < 0.027) & (np.cos(n_holes * a) > 0.55)
        mid[hole] = M_SEAL
        hgt[hole] = -0.01
        # ten wheel nuts on the disc round the hub (335 mm circle), each a
        # dark dot standing proud
        na = np.mod(a + np.pi / 10, 2 * np.pi / 10) - np.pi / 10
        studs = np.hypot(r * np.cos(na) - 0.1675, r * np.sin(na)) < 0.017
        mid[studs] = M_HUB
        hgt[studs] = 0.008
        # the hub: the front one a cone standing out of the dished disc, a
        # tone darker with a dark cap; the rear one the axle's dark flange
        hub = r < (0.15 if front else 0.14)
        mid[hub] = M_HUB if not front else M_RIM
        if front:
            shade[hub] *= 0.84
            mid[r < 0.062] = M_HUB
        else:
            shade[hub & (r < 0.06)] *= 0.8
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
                      ("reflector", M_TAPE_RED), ("tank", M_TANK), ("guard", M_GUARD),
                      ("rubber", M_RUBBER), ("plastic", M_PLASTIC), ("step", M_STEP),
                      ("housing", M_HOUSING), ("mirror", M_MIRROR), ("seal", M_SEAL),
                      ("mirror_body", M_PLASTIC), ("bezel", M_BEZEL),
                      ("mesh", M_GRILLE_HOLE), ("cabpaint", M_CAB), ("insert", M_INSERT)):
        P.fill(name, mid)
    # step treads: non-slip ribs and a light nosing
    P.where("step", lambda u, v: np.mod(v, 0.035) < 0.012, add_h=0.002, shade=1.3)
    P.where("step", lambda u, v: (np.mod(u, 0.07) < 0.012), add_h=-0.002, shade=0.8)
    # the tank: U along it, V round it; two dark rubber-lined straps, a weld seam
    P.where("tank", lambda u, v: np.abs(u - 0.21) < 0.004, add_h=0.002, shade=0.9)
    P.where("tank", lambda u, v: np.abs(np.abs(u - 0.21) - 0.13) < 0.018, mid=M_RUBBER,
            add_h=0.004)
    # a red retro-reflector: a fine prism grid
    P.where("reflector", lambda u, v: (np.mod(u, 0.045) < 0.008) | (np.mod(v, 0.045) < 0.008),
            shade=1.12)
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
    P.where("mesh", lambda u, v: (np.mod(u + v, 0.06) < 0.012) | (np.mod(u - v, 0.06) < 0.012),
            mid=M_GRILLE, add_h=0.004)
    for name in ("low", "high", "drl", "ind", "fog_front"):
        # Each front lens is mapped whole onto its patch (inner edge to outer,
        # foot to head): bright silver behind clear glass, a field of about
        # sRGB 200, its cells parted by light chrome dividers. No darker
        # line anywhere inside a unit (no joints, rings, outlines or flute
        # lines) and no glints: the structure is soft tonal shading only.
        x, y, w, h = REG["lens_" + name]
        sy, sx, Y_, X_ = P.c.field(x, x + w, y, y + h)
        u, v = (X_ - x - 1.5) / (w - 3.0), (Y_ - y - 1.5) / (h - 3.0)
        asp = {"low": 0.145 / 0.195, "high": 0.180 / 0.195, "drl": 0.325 / 0.055,
               "ind": 0.105 / 0.250, "fog_front": 0.150 / 0.080}[name]
        # distance in from the cell's edge, in units of its short side
        du, dv = np.minimum(u, 1 - u), np.minimum(v, 1 - v)
        du, dv = (du * asp, dv) if asp < 1 else (du, dv / asp)
        r = 0.18
        d = r - np.hypot(np.maximum(r - du, 0), np.maximum(r - dv, 0))   # rounded inset
        rim = d < 0.055
        # the reflector: a soft bowl across the whole cell, a smooth fall
        # from the field (sRGB about 200) to a darker heart (about 162) with
        # no edge, and in it a small soft bulb cap, a low oval a shade
        # darker still (about 150)
        cu, cv, ru, rv_ = {"low": (0.5, 0.52, 0.52, 0.52), "high": (0.5, 0.52, 0.54, 0.52),
                           "fog_front": (0.5, 0.5, 0.52, 0.56)}.get(name, (0.5, 0.5, 1, 1))
        rr = np.hypot((u - cu) / ru, (v - cv) / rv_)
        bowl = 1.0 - 0.39 * np.clip(1.0 - rr ** 2, 0.0, 1.0) ** 1.5
        cap = -0.10 * np.exp(-(((u - cu) / 0.11) ** 2 + ((v - cv) / 0.045) ** 2))
        if name in ("low", "high", "fog_front"):
            body = bowl + cap
            if name == "high":       # faint upright flutes, lighter than the bowl
                body = body * np.where(np.mod(u * 9.0, 1.0) < 0.4, 1.04, 1.0)
        elif name == "ind":
            body = np.where(np.mod(v * 7.0, 1.0) < 0.35, 1.08, 1.0)
        else:
            body = np.ones_like(u)
        P.c.shade[sy, sx] *= body
        if name in ("low", "high", "fog_front"):
            P.c.height[sy, sx] -= 0.005 * np.clip(1.0 - rr ** 2, 0, 1)
        if name == "ind":
            P.c.shade[sy, sx][rim] *= 1.10            # a lighter amber edge, no chrome: it blinks
        else:
            P.c.mid[sy, sx][rim] = M_LENS_DIV
            P.c.shade[sy, sx][rim] = 1.0
            P.c.height[sy, sx][rim] = 0.002
    for name in ("tail_brake", "reverse", "fog"):
        # rear lenses: soft ribs a few per cent apart, no dark lines
        x, y, w, h = REG["lens_" + name]
        sy, sx, Y_, X_ = P.c.field(x, x + w, y, y + h)
        rib = np.mod(Y_ - y, 4.0) < 2.0
        P.c.shade[sy, sx][rib] *= 0.95
    # glass
    P.fill("glass_ws", M_GLASS)
    P.fill("glass_side", M_GLASS)


# ---------------------------------------------------------------- LOD3
LOD3_UPPER = [(0.09, Z_LEDGE), (0.27, 2.50), (0.50, 2.75), (1.88, 3.70), (7.90, 3.70),
              (7.90, 1.15), (1.90, 1.15)]
LOD3_LOWER = [(0.0, 0.99), (0.0, 0.46), (1.00, 0.0), (1.75, 0.0), (1.95, 0.45), (5.30, 0.45),
              (5.50, 0.0), (6.30, 0.0), (7.84, 0.45), (7.84, 1.13)]


def paint_lod3(P):
    """Pictures for the 60-triangle LOD3: a side elevation, the front and
    the rear, at 16 texels per metre."""
    reg = "lod3_side"
    P.fill(reg, M_DARK)
    pp = LOD3_PPM

    def W(fn, mid):
        P.where(reg, fn, mid=mid, ppm=pp)
    W(lambda s, z: (s > BOX_S0) & (z > BOX_Z0), M_BOX_FAR)
    W(lambda s, z: (s > BOX_S0) & (np.abs(z - 1.23) < 0.08), M_ALU)
    W(lambda s, z: (s < CAB_BACK) & (z > Z_DOOR), M_CAB_FAR)
    W(lambda s, z: (s < CAB_BACK) & (z > Z_FOOT) & (z <= Z_DOOR), M_PLASTIC)
    nose = [(r[1], r[0]) for r in DEFL.rings] + [(DEFL_BACK, DEFL_TOP), (DEFL_BACK, 2.70)]
    W(lambda s, z: (z > 2.74) & (s < 1.89) & (inside(nose, s, z) | (s > 1.80)), M_CAB_FAR)
    W(lambda s, z: inside(DOOR_GLASS, s, z), M_GLASS)
    # the under-body solid's sides are unpainted: its guards, tank and rims
    # in their own colours, light under dark paint as LOD0's are
    W(lambda s, z: (s > GUARD_S[0]) & (s < GUARD_S[1]) & (
        (np.abs(z - 0.51) < 0.07) | (np.abs(z - 0.81) < 0.07)), M_GUARD)
    W(lambda s, z: (s > TANK[0] - 0.05) & (s < TANK[1] + 0.05) & (np.abs(z - TANK[3]) < 0.26),
      M_TANK)
    for sc in (FRONT_AXLE, REAR_AXLE):
        W(lambda s, z, sc=sc: np.hypot(s - sc, z - R_WHEEL) < R_WHEEL, M_TYRE)
        W(lambda s, z, sc=sc: np.hypot(s - sc, z - R_WHEEL) < 0.32, M_RIM)
    reg = "lod3_front"
    P.fill(reg, M_DARK)
    # the cab front from the bumper's top, across the extrusion's full width
    W(lambda u, z: z > Z_LEDGE, M_CAB_FAR)
    W(lambda u, z: (z > 2.75), M_BOX_FAR)
    W(lambda u, z: (z > 2.75) & (z < DEFL_TOP) & (np.abs(u - BOX_HW) < DEFL_W[1]), M_CAB_FAR)
    W(lambda u, z: (np.abs(u - BOX_HW) < trapezoid_hw(WSCREEN, z) + 0.03) & (z > COWL_Z)
      & (z < WSCREEN[3] + 0.02), M_GLASS)
    W(lambda u, z: (np.abs(u - BOX_HW) < trapezoid_hw(GRILLE, z)) & (z > GRILLE[1])
      & (z < GRILLE[3]), M_GRILLE)
    W(lambda u, z: (z > Z_FOOT) & (z < Z_LEDGE) & (np.abs(u - BOX_HW) < LOW_HW), M_PLASTIC)
    W(lambda u, z: (np.abs(np.abs(u - BOX_HW) - HEADLAMP[0]) < HEADLAMP[2])
      & (np.abs(z - HEADLAMP[1]) < HEADLAMP[3]), M_PIC_LAMP)
    W(lambda u, z: (z < Z_FOOT) & (np.abs(np.abs(u - BOX_HW) - FRONT_X) < 0.15), M_TYRE)
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
    lens = tuple(M_LENS.values()) + (M_LENS_DIV,)
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
        -np.clip((Y_ - y - PAD) / PPM - SHELL.v[I_DOOR], 0, None) / 0.25)
        * (0.6 + 0.4 * nz("blotch")), (M_CAB,))
    w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.14 * (0.5 + 0.5 * nz("blotch")),
          (M_PLASTIC,))
    # deflector front lip: insects and road dust
    x, y, wd, h = REG["defl"]
    w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.07 * np.exp(
        -((Y_ - y - PAD) / PPM) / 0.25) * (0.5 + 0.5 * nz("blotch"))
        + 0.06 * nz("speck") * np.exp(-((Y_ - y - PAD) / PPM) / 0.4), (M_CAB,))
    # steps, the chassis, mudflaps, guards: road dirt
    for reg, amt in (("step", 0.20), ("dark", 0.22), ("liner", 0.35),
                     ("rubber", 0.30), ("guard", 0.18), ("tank", 0.12),
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
    t[M_LENS_DIV] = vi.LENS_LIT["white"]
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
