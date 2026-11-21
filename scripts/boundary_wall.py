# SPDX-License-Identifier: GPL-3.0-or-later

"""The brick perimeter wall of props/boundary/: one atlas, the geometry, the
tiers and the facts of every piece, which each piece's build.py names.

A lot's wall is assembled by the consumer from separate pieces placed by
coordinates and 90-degree turns: straight runs, a free-standing pier and the
two sides of an open truck gate. They share one 512 atlas and one set of
rules, so both live here; a piece's build.py says only which piece it is:

    PIECE = boundary_wall.Run(10.0)
    BUILD, build_all, facts = boundary_wall.piece_asset(ASSET, HERE, PIECE)

Two steps rebuild a piece. The atlas (system Python with scipy and Pillow),
painted once and written into each piece's export/ under its own name:

    python3 scripts/boundary_wall.py export props/boundary/tiilimuuri_*

then each piece in Blender, which only reads the PNGs:

    blender --background --python props/boundary/<piece>/build.py

Frame (the build frame; the export makes it glTF's +Y up, +Z front): metres,
Z up, the street face toward -Y, the pivot at the origin, on the ground and on
the wall's centre line. Blender (x, y, z) is glTF (x, z, -y).

The joint rule. A run of length L has its joint planes at x = -L/2 and +L/2,
and is placed with its joint planes on its neighbours', so L is the placement
pitch. It carries one pier centred on its -X joint plane and more every
PIER_PITCH along it, and none at its +X end. Its wall stops END_INSET short of
the +X joint plane, so the end is always inside whatever closes it: the next
run's -X pier, the free-standing pier at a free end, or a gate pier; no wall
end is ever coplanar with a pier face. At a 90-degree corner both centre
lines meet on the corner point, a joint plane for both, and the departing
run's pier there swallows both wall ends.

A gate piece has its pivot on the opening's edge plane, its pier wholly on
the side away from the opening and its leaf swung back along the yard face
beyond it. gate_left's pier closes the +X end of the run it stands on, as a
pier would; the run on the far side of gate_right starts at the gate pier,
so it is the pierless run, whose wall starts END_INSET inside its -X joint
plane: a run with its own pier there would put half of it in the opening.

Imports numpy alone at the top, so Blender's Python can read the layout;
painting needs scipy and Pillow, the geometry bpy, each imported where used.
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import atlas  # noqa: E402
import weathering  # noqa: E402

ATLAS = 512
PPM = 64.0
PAD = 2
EPS = 1e-6

# ------------------------------------------------------------------ the wall
WALL_T = 0.25               # one brick
HW = WALL_T / 2.0
WALL_H = 2.10               # the coping's top
Z_COPING = 2.02             # precast concrete coping, 0.08 thick
COPING_W = 0.35             # overhanging 0.05 each side
HC = COPING_W / 2.0
Z_PLINTH = 0.25             # cast concrete plinth course, flush with the brick
END_INSET = 0.10            # a run's wall stops this far short of its +X joint

# run piers and the free-standing pier: brick, a plain concrete cap
PIER_W = 0.40
HP = PIER_W / 2.0
PIER_SHAFT = 2.17           # the brick's top, under the cap
CAP_OVER = 0.025            # every cap overhangs its shaft by this much
HCAP = HP + CAP_OVER        # 0.225: a run pier's cap, and so the run's plan
PIER_H = 2.25
PIER_PITCH = 5.0

# the gate: a heavier, taller pier; a hinge post on its yard face; one
# sheet-steel leaf swung fully back along the yard face beyond it. The pier
# stands 0.05 toward the street of the centre line, so its yard face is the
# run piers' and the leaf, which must clear them, lies close to the wall.
GATE_PIER_W = 0.50
GATE_SHAFT = 2.48
GATE_H = 2.60
GATE_Y = -0.05              # the gate pier's centre line
HG = GATE_PIER_W / 2.0
HGCAP = HG + CAP_OVER
POST_W = 0.08               # the hinge post, along the wall
POST_H = 2.15
LEAF_W, LEAF_H, LEAF_T = 3.00, 2.00, 0.04
LEAF_Z0 = 0.05              # ground clearance
LEAF_Y = (0.23, 0.27)       # the leaf's two faces: 0.03 off the piers' yard faces
POST_Y = (GATE_Y + HG, LEAF_Y[1])
HINGE_D = CAP_OVER + POST_W     # the leaf's hinge end, from the opening edge

# ---------------------------------------------------------------- the atlas
# V up, in pixels. Two bands run the full width and tile in U, their V the
# height from the ground, so the weather that follows height is exact on
# every piece; a third, narrower one carries the coping's top:
#
#   rows   0 .. 140   WALL   z 0 .. 2.10: plinth course, brick, coping sides
#   rows 142 .. 314   PIER   z 0 .. 2.60: plinth course, brick, cap sides
#   rows 318 .. 460   unique: the leaf, the hinge post, cap tops, patches
#   rows 466 .. 502   TOP    the coping's top, V across the wall
W_Y0 = 2.0
P_Y0 = 144.0
TOP_C = 484.0                       # v of the wall's centre line on TOP
BAND_ROWS = {"WALL": (0, 140), "PIER": (142, 314), "TOP": (466, 502)}
UNI_Y = 318
GATE_R = (4, UNI_Y, 192, 128)       # the leaf's face, 3.0 x 2.0 m
POST_R = (204, UNI_Y, 8, 140)       # the hinge post: U across a face, V up
CAPTOP_R = (220, UNI_Y, 36, 36)     # a cap's top, centred
PATCH_NAMES = ("blank", "soffit", "paint", "conc")
PATCHES = {n: (264 + 18 * i, UNI_Y, 12, 12) for i, n in enumerate(PATCH_NAMES)}

COURSE = 0.078125                   # brick course: 5 px
BRICK_L = 0.25                      # stretcher: 16 px, 32 to the atlas width
TONE_COURSES = 48
COPING_JOINT = 1.0                  # precast coping units

ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_CONC, ID_PAINT, ID_HW, ID_DARK, ID_SIGN_W, ID_SIGN_R = 5, 6, 7, 8, 9, 10

SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.82, 0.0), ID_MORTAR: (0.94, 0.0), ID_CONC: (0.90, 0.0),
    ID_PAINT: (0.55, 0.0), ID_HW: (0.45, 0.55), ID_DARK: (0.92, 0.0),
    ID_SIGN_W: (0.40, 0.0), ID_SIGN_R: (0.40, 0.0),
}

# The plant's brick (voimalaitos_brick_hall and the rest of the plant) and the
# yard gate's paint as muuntajakentta_walled pairs it with each brick.
VARIANTS = {
    "red_brick": {"brick": (114, 73, 62), "brick2": (90, 59, 51),
                  "mortar": (125, 123, 118), "paint": (66, 82, 76)},
    "yellow_brick": {"brick": (188, 166, 122), "brick2": (164, 142, 104),
                     "mortar": (160, 156, 148), "paint": (104, 56, 44)},
    "brown_brick": {"brick": (80, 59, 57), "brick2": (62, 46, 45),
                    "mortar": (108, 106, 102), "paint": (60, 68, 76)},
}
DEFAULT_VARIANT = "red_brick"
FIXED = {
    ID_BLANK: (52, 52, 52), ID_PLINTH: (150, 148, 142), ID_CONC: (166, 164, 156),
    ID_HW: (120, 120, 118), ID_DARK: (26, 26, 26), ID_SIGN_W: (196, 196, 190),
    ID_SIGN_R: (150, 42, 36),
}
BRICKISH = (ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR, ID_CONC)
BAND_IDS = {name: (rows, set(BRICKISH)) for name, rows in BAND_ROWS.items()}

# relief, metres, relative to the face each region maps onto
BRICK_FACE = 0.006
COPING_H = 0.020
FRAME_H = 0.025
RIB_H = 0.008


def m(v):
    """Metres -> pixels."""
    return v * PPM


# ================================================================== pieces
class Run:
    """A straight run, L between its joint planes. piers=False is the run
    that starts at a gate pier: no pier, its wall inset at both ends."""

    kind = "run"

    def __init__(self, length, piers=True):
        self.length = float(length)
        n = int(math.ceil(self.length / PIER_PITCH - EPS))
        self.piers = [-self.length / 2.0 + PIER_PITCH * k for k in range(n)] if piers else []
        x1 = self.length / 2.0 - END_INSET
        x0 = -self.length / 2.0 if piers else -x1
        self.wall = (x0, x1)


class Pier:
    """The free-standing pier, centred on the joint plane it closes."""

    kind = "pier"


class Gate:
    """One side of an open truck gate; *side* "left" stands on the opening's
    -X edge (its pier and leaf toward -X), "right" mirrors it."""

    kind = "gate"

    def __init__(self, side):
        if side not in ("left", "right"):
            raise ValueError("side is left or right, not %r" % side)
        self.side = side
        self.away = -1.0 if side == "left" else 1.0     # from the opening

    def x(self, d0, d1):
        """Plan x range of distances d0..d1 from the opening's edge."""
        a, b = self.away * d0, self.away * d1
        return min(a, b), max(a, b)


# ============================================================ layout checks
def check_layout(piece):
    """What the numbers must keep true for the joint rule to hold."""
    p = []
    if not HC < HP:
        p.append("the coping is wider than a pier: wall ends would show")
    if not 0.0 < END_INSET < HP - 0.05:
        p.append("END_INSET leaves a wall end outside or at a pier's face")
    if not (WALL_H < PIER_SHAFT and Z_COPING < WALL_H):
        p.append("the pier does not rise over the coping")
    if not (CAP_OVER < END_INSET < CAP_OVER + GATE_PIER_W):
        p.append("a run's end would not land inside a gate pier's shaft")
    if not (GATE_Y - HG <= -HC and GATE_Y + HG >= HC):
        p.append("a gate pier is narrower than the coping it closes")
    if not LEAF_Y[0] > max(HCAP, GATE_Y + HGCAP) + 0.004:
        p.append("the leaf does not clear the piers' and caps' yard faces")
    if not LEAF_Z0 + LEAF_H < min(PIER_SHAFT, GATE_SHAFT):
        p.append("the leaf reaches a cap")
    if not POST_Y[0] <= GATE_Y + HG and POST_Y[1] >= LEAF_Y[1]:
        p.append("the hinge post does not join the pier to the leaf")
    if isinstance(piece, Run):
        for a, b in zip(piece.piers, piece.piers[1:]):
            if b - a < 2 * HCAP + 0.5:
                p.append("piers %.2f and %.2f crowd each other" % (a, b))
        if piece.piers and piece.piers[-1] + HCAP > piece.wall[1] - 0.3:
            p.append("a pier stands at the +X end")
    if W_Y0 + m(WALL_H) + PAD > BAND_ROWS["WALL"][1]:
        p.append("the wall band runs off its rows")
    if P_Y0 + m(GATE_H) + PAD > BAND_ROWS["PIER"][1]:
        p.append("the pier band runs off its rows")
    if TOP_C + m(HCAP) + PAD > BAND_ROWS["TOP"][1] or TOP_C - m(HCAP) - PAD < BAND_ROWS["TOP"][0]:
        p.append("the top strip runs off its rows")
    if m(LEAF_W) > GATE_R[2] + 0.01 or m(LEAF_H) > GATE_R[3] + 0.01:
        p.append("the leaf overruns its region")
    if m(POST_H) > POST_R[3] or m(POST_W) > POST_R[2] or m(POST_Y[1] - POST_Y[0]) > POST_R[2]:
        p.append("the hinge post overruns its region")
    if m(2 * HGCAP) > CAPTOP_R[2] or m(2 * HGCAP) > CAPTOP_R[3]:
        p.append("a cap's top overruns its region")
    rects = dict(PATCHES, leaf=GATE_R, post=POST_R, captop=CAPTOP_R)
    names = sorted(rects)
    for i, a in enumerate(names):
        ax, ay, aw, ah = rects[a]
        if ax < PAD or ax + aw > ATLAS - PAD or ay + ah > BAND_ROWS["TOP"][0] - PAD \
                or ay < BAND_ROWS["PIER"][1] + PAD:
            p.append("%s leaves the unique rows" % a)
        for b in names[i + 1:]:
            bx, by, bw, bh = rects[b]
            if ax - 4 < bx + bw and bx - 4 < ax + aw and ay - 4 < by + bh and by - 4 < ay + ah:
                p.append("%s and %s overlap" % (a, b))
    return p


# ================================================================= painting
def paint_brick(c, y_z0, z_from, z_to, seed):
    """Stretcher bond, two tones, the mortar recessed, courses counted from
    z_from; bond and tone repeat at the atlas wrap in U."""
    y0, top = y_z0 + m(z_from), y_z0 + m(z_to)
    course, blen = m(COURSE), m(BRICK_L)
    c.paint(0, ATLAS, y0, top, ID_BRICK, 1.0, 1.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0, top)
    r = np.floor((Y - y0) / course).astype(np.int64)
    off = (r % 2) * blen * 0.5
    b = np.floor((X - off) / blen).astype(np.int64) % int(ATLAS / blen)
    rr = r % TONE_COURSES
    joint = ((Y - y0 - r * course) < 1.0) | (((X - off) % blen) < 1.0)
    tone = 0.90 + 0.20 * atlas.hash_unit(b, rr, seed)
    dark = atlas.hash_unit(b, rr, seed + 12) < 0.17
    c.mid[sy, sx] = np.where(joint, ID_MORTAR, np.where(dark, ID_BRICK2, ID_BRICK))
    c.shade[sy, sx] = np.where(joint, 0.94, tone)
    c.ao[sy, sx] = np.where(joint, 0.80, 1.0)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)


def paint_plinth(c, y_z0):
    """The cast plinth course from the ground to Z_PLINTH, darker at its
    foot, the occluded strip under the brick's bottom course."""
    h = m(Z_PLINTH)
    c.paint(0, ATLAS, y_z0 - PAD, y_z0 + h, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, y_z0 - PAD, y_z0 + h)
    z = (Y - y_z0) / PPM
    c.shade[sy, sx] *= 0.84 + 0.16 * np.clip(z / 0.20, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.86 + 0.14 * np.clip(z / 0.20, 0, 1))
    c.mul(0, ATLAS, y_z0 + h - 2, y_z0 + h, 0.88, ao=0.86)


def paint_coping_side(c, y0, y1, joints=True):
    """Precast concrete seen from the side: its arrises catching the light,
    the drip's shadow on the brick under it, a joint every COPING_JOINT."""
    c.paint(0, ATLAS, y0, y1, ID_CONC, 1.0, 1.0)
    c.bevel(0, ATLAS, y0, y1, COPING_H, 1.0, axes="y")
    c.mul(0, ATLAS, y0, y0 + 1, 0.86, ao=0.86)
    c.mul(0, ATLAS, y0 - 2, y0, 0.86, ao=0.84)
    if joints:
        _coping_joints(c, y0, y1)


def _coping_joints(c, y0, y1):
    sy, sx, _, X = c.field(0, ATLAS, y0, y1)
    j = (X % m(COPING_JOINT)) < 0.8
    c.shade[sy, sx] = np.where(j, c.shade[sy, sx] * 0.70, c.shade[sy, sx])
    c.height[sy, sx] = np.where(j, c.height[sy, sx] - 0.006, c.height[sy, sx])


def paint_bands(c):
    # the wall: plinth course, brick, the coping's sides
    paint_brick(c, W_Y0, Z_PLINTH, Z_COPING, seed=41)
    paint_plinth(c, W_Y0)
    paint_coping_side(c, W_Y0 + m(Z_COPING), BAND_ROWS["WALL"][1])
    # the piers: the same brick on to GATE_SHAFT, then a cap's sides (a run
    # pier's cap maps its 0.08 m onto the first rows of the gate's 0.12 m)
    paint_brick(c, P_Y0, Z_PLINTH, GATE_SHAFT, seed=43)
    paint_plinth(c, P_Y0)
    paint_coping_side(c, P_Y0 + m(GATE_SHAFT), BAND_ROWS["PIER"][1], joints=False)
    # the coping's top across the wall, brick tops past it (a former LOD3
    # box's; no tier samples them now)
    y0, y1 = BAND_ROWS["TOP"]
    c.paint(0, ATLAS, y0, y1, ID_BRICK, 0.90, 0.92, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0, y1)
    hdr = np.floor(X / m(0.125)).astype(np.int64)
    c.shade[sy, sx] *= 0.92 + 0.12 * atlas.hash_unit(hdr, 7)
    a, b = TOP_C - m(HC), TOP_C + m(HC)
    c.paint(0, ATLAS, a, b, ID_CONC, 1.0, 1.0)
    c.bevel(0, ATLAS, a, b, COPING_H, 1.5, axes="y")
    _coping_joints(c, a, b)


def _bar(c, a0, a1, b0, b1, mid, h, shade=1.0, ao=0.9, axes="xy"):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, 1.0, axes=axes)


def paint_no_entry(c, cx, cy, side):
    """A generic no-entry plate: a pale square plate, a red roundel and its
    pale bar, no lettering. *side* in pixels."""
    s = side / 2.0
    c.paint(cx - s, cx + s, cy - s, cy + s, ID_SIGN_W, 1.0, 1.0, height=0.004)
    c.mul(cx - s, cx + s, cy - s - 1.5, cy - s, 0.80, ao=0.80)
    c.disc(cx, cy, 0.42 * side, ID_SIGN_R, 1.0, height=0.004)
    c.paint(cx - 0.28 * side, cx + 0.28 * side, cy - 0.065 * side, cy + 0.065 * side,
            ID_SIGN_W, 1.0, height=0.004)


def paint_leaf(c):
    """The leaf, as the yard gate's: a frame of square tube round a sheet
    with pressed vertical ribs, a mid rail, heavy hinge straps on the hinge
    stile (U = 0), a drop bolt and a latch on the free stile, and the plate.
    U from the hinge end, V from the leaf's foot."""
    x, y, w, h = GATE_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_PAINT, 1.0, 1.0, height=0.0)
    F = m(0.06)
    sy, sx, _, X = c.field(x + F, x + w - F, y, y + h)
    r = (X - x) % m(0.15)
    c.height[sy, sx] = np.where(r < 3.0, RIB_H * np.sin(np.pi * np.clip(r / 3.0, 0, 1)), 0.0)
    c.shade[sy, sx] = np.where((r >= 3.0) & (r < 4.0), 0.92, 1.0)
    for b0, b1 in ((y - PAD, y + F), (y + m(0.95), y + m(0.95) + F), (y + h - F, y + h + PAD)):
        _bar(c, x - PAD, x + w + PAD, b0, b1, ID_PAINT, FRAME_H, 1.0, 0.9, "y")
        c.mul(x - PAD, x + w + PAD, b0 - 2, b0, 0.88, ao=0.84)
    _bar(c, x - PAD, x + F, y - PAD, y + h + PAD, ID_PAINT, FRAME_H, 1.0, 0.9, "x")
    _bar(c, x + w - F, x + w + PAD, y - PAD, y + h + PAD, ID_PAINT, FRAME_H, 1.0, 0.9, "x")
    for zz in (0.30, 1.70):
        hy = y + m(zz)
        c.paint(x - PAD, x + m(0.34), hy - 3, hy + 3, ID_HW, 0.80, 0.86, height=0.040)
        c.mul(x - PAD, x + m(0.34), hy - 5, hy - 3, 0.82, ao=0.80)
    fx = x + w - F
    c.paint(fx - 5, fx - 2, y + 1, y + m(0.62), ID_HW, 0.85, 0.85, height=0.030)
    c.paint(fx - 7, fx - 1, y + m(0.58), y + m(0.62), ID_HW, 0.85, 0.85, height=0.035)
    c.paint(fx - 9, fx, y + m(1.02), y + m(1.08), ID_HW, 0.90, 0.85, height=0.035)
    paint_no_entry(c, x + m(1.55), y + m(1.45), m(0.30))
    c.mul(x - PAD, x + w + PAD, y - PAD, y + 1.5, 0.80, ao=0.8)


def paint_post(c):
    """The hinge post: square steel tube in the leaf's paint, the leaf's two
    pintles at its hinges' heights, a base plate at its foot."""
    x, y, w, h = POST_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_PAINT, 0.96, 1.0, height=0.0)
    for zz in (LEAF_Z0 + 0.30, LEAF_Z0 + 1.70):
        hy = y + m(zz)
        c.paint(x - PAD, x + w + PAD, hy - 4, hy + 4, ID_HW, 0.80, 0.85, height=0.030)
        c.mul(x - PAD, x + w + PAD, hy - 6, hy - 4, 0.80, ao=0.80)
    c.paint(x - PAD, x + w + PAD, y - PAD, y + 4, ID_HW, 0.75, 0.85, height=0.010)
    c.mul(x - PAD, x + w + PAD, y + h - 2, y + h + PAD, 0.90)


def paint_captop(c):
    """A cap's top: precast concrete, arrises catching the light."""
    x, y, w, h = CAPTOP_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CONC, 1.0, 1.0, height=0.0)
    c.bevel(x - PAD, x + w + PAD, y - PAD, y + h + PAD, COPING_H, 2.0)


def paint_patches(c):
    spec = {"blank": (ID_BLANK, 1.0, 1.0), "soffit": (ID_CONC, 0.78, 0.75),
            "paint": (ID_PAINT, 0.94, 0.95), "conc": (ID_CONC, 0.92, 0.92)}
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x - 2, x + w + 2, y - 2, y + h + 2, mid, sh, ao, height=0.0)


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it is. Both
    bands' V is height from the ground: soil and damp at the plinth,
    splash-back above it, a little salt bloom, light runs under the coping
    and the caps. The leaf takes kicked-up dirt at its foot and grime at its
    latch; the steel a little rust where it meets the ground."""
    brick = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    w = weathering.Weather(c, steel=(ID_PAINT, ID_HW))
    w.grime()
    w.fade((ID_PAINT,))
    w.wash(brick)
    for y_z0, top in ((W_Y0, Z_COPING), (P_Y0, GATE_SHAFT)):
        w.plinth(0, ATLAS, y_z0, y_z0 + m(Z_PLINTH), (ID_PLINTH,))
        w.splash(0, ATLAS, y_z0 + m(Z_PLINTH), y_z0 + m(top), brick)
        w.bloom(0, ATLAS, y_z0 + m(Z_PLINTH), y_z0 + m(1.1), brick, amount=0.10,
                fade=m(0.55))
        cap = y_z0 + m(top)
        w.runs(0, ATLAS, cap - m(0.45), cap, brick, 0.12, fall=10.0)
    for y0, y1 in ((W_Y0 + m(Z_COPING), BAND_ROWS["WALL"][1]),
                   (P_Y0 + m(GATE_SHAFT), BAND_ROWS["PIER"][1]), BAND_ROWS["TOP"]):
        w.add("D", 0, ATLAS, y0, y1, lambda Y, X, nz: 0.08 + 0.10 * nz("blotch"), (ID_CONC,))
    x, y, wd, hd = CAPTOP_R
    w.add("D", x - PAD, x + wd + PAD, y - PAD, y + hd + PAD,
          lambda Y, X, nz: 0.10 + 0.10 * nz("blotch"), (ID_CONC,))
    x, y, wd, hd = GATE_R
    w.door(x, x + wd, y, y + hd, (ID_PAINT,), handle=(x + wd - 8, y + m(1.05)))
    w.add("R", x - PAD, x + wd + PAD, y - PAD, y + 8, lambda Y, X, nz: 0.12 * nz("blotch"),
          (ID_PAINT, ID_HW))
    x, y, wd, hd = POST_R
    w.add("R", x - PAD, x + wd + PAD, y - PAD, y + 10, lambda Y, X, nz: 0.14 * nz("blotch"),
          (ID_PAINT, ID_HW))
    w.splash(x - PAD, x + wd + PAD, y, y + m(0.6), (ID_PAINT,), amount=0.14)
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height; colour comes per variant."""
    problems = check_layout(None)
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_bands(c)
    c.check_bands(BAND_IDS)
    paint_leaf(c)
    paint_post(c)
    paint_captop(c)
    paint_patches(c)
    c.shade *= 1.0 + 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    walls = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH))
    c.shade[walls] *= 1.0 + 0.03 * atlas.noise(c, 7, 0.8, 40.0)[walls]
    sheet = c.mid == ID_PAINT
    c.shade[sheet] *= 1.0 + 0.016 * atlas.noise(c, 5, 60.0, 0.35)[sheet]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_CONC, ID_MORTAR))
    pores = atlas.noise(c, 9, 0.8)
    c.shade[mineral] *= 1.0 + 0.03 * pores[mineral]
    c.height[mineral] += 0.0006 * pores[mineral]
    weather(c)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    for key, i in (("brick", ID_BRICK), ("brick2", ID_BRICK2), ("mortar", ID_MORTAR),
                   ("paint", ID_PAINT)):
        t[i] = pal[key]
    return t


def export(asset_dirs, ss=atlas.SS):
    """Paint once; write each piece's albedo per variant, ORM and normal map
    into its export/, named for the piece. No emission: the wall is unlit."""
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.010)
    c.weather.dust(cav, (ID_BRICK, ID_BRICK2, ID_MORTAR))
    rough = 0.04 * atlas.noise(c, 13, 20.0)
    maps = {"orm": atlas.orm(c, SURFACE, rough, 0.5 * cav), "normal": atlas.normal_map(c)}
    for v in VARIANTS:
        maps["albedo_" + v] = atlas.albedo(c, lut(v), grime=0.25 * cav)
    written = []
    for d in asset_dirs:
        name = os.path.basename(os.path.normpath(d))
        out = os.path.join(d, "export")
        os.makedirs(out, exist_ok=True)
        for key, arr in maps.items():
            written.append(atlas.save(arr, os.path.join(out, "%s_%s.png" % (name, key))))
    return written


# ================================================================ geometry
# Everything below runs inside Blender only.
class Builder:
    """One closed solid, UVs set as faces are made; vertices shared through
    a position cache so faces meeting on an edge meet on its vertices."""

    def __init__(self):
        import bmesh
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cache = {}

    def v(self, co):
        key = tuple(round(c, 5) for c in co)
        vert = self.cache.get(key)
        if vert is None:
            vert = self.bm.verts.new(co)
            self.cache[key] = vert
        return vert

    def face(self, cos, uvfn):
        verts = []
        for co in cos:
            vv = self.v(co)
            if not verts or verts[-1] is not vv:
                verts.append(vv)
        if len(verts) > 2 and verts[0] is verts[-1]:
            verts.pop()
        if len(verts) < 3:
            return None
        f = self.bm.faces.new(verts)
        for loop in f.loops:
            u, w = uvfn(loop.vert.co)
            loop[self.uv].uv = (u / ATLAS, w / ATLAS)
        return f


def patch(name):
    x0, y0, w, h = PATCHES[name]
    return lambda co: (x0 + w / 2.0, y0 + h / 2.0)


def captop(cx, cy):
    x0, y0, w, h = CAPTOP_R
    return lambda co: (x0 + w / 2.0 + (co.x - cx) * PPM, y0 + h / 2.0 + (co.y - cy) * PPM)


def top_strip(co):
    return (co.x * PPM, TOP_C + co.y * PPM)


def box(x0, x1, y0, y1, z0, z1, side, top, bottom):
    """A closed box; side(a, b) gives the uv function of the side face from
    plan point a to b, walked counter-clockwise (outward on the right)."""
    B = Builder()
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for k in range(4):
        a, b = ring[k], ring[(k + 1) % 4]
        B.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)],
               side(a, b))
    B.face([(x, y, z1) for x, y in ring], top)
    B.face([(x, y, z0) for x, y in reversed(ring)], bottom)
    return B


def along(a, b, y_z0, vscale=1.0, zshift=0.0, cx=0.0, cy=0.0):
    """A side face from a to b on a band: U the plan distance along the face
    (from the solid's centre line), V height from the ground."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    tx, ty = dx / n, dy / n
    return lambda co: (((co.x - cx) * tx + (co.y - cy) * ty) * PPM,
                       y_z0 + (co.z + zshift) * vscale * PPM)


def wall(x0, x1, profile):
    """The wall from x0 to x1 as a prism of *profile* ((y, z) round its
    section): side faces on the WALL band, the top on TOP, the coping's
    underside on the soffit patch, the ends on the band across."""
    B = Builder()
    n = len(profile)
    ztop = max(z for _, z in profile)
    for i in range(n):
        (ya, za), (yb, zb) = profile[i], profile[(i + 1) % n]
        if abs(ya - yb) < EPS:
            s = 1.0 if ya < 0 else -1.0
            uv = (lambda s: lambda co: (s * co.x * PPM, W_Y0 + co.z * PPM))(s)
        elif abs(za - ztop) < EPS:
            uv = top_strip
        elif za < EPS:
            uv = patch("blank")
        else:
            uv = patch("soffit")
        B.face([(x0, ya, za), (x1, ya, za), (x1, yb, zb), (x0, yb, zb)], uv)
    for x, s in ((x0, -1.0), (x1, 1.0)):
        B.face([(x, y, z) for y, z in profile],
               (lambda s: lambda co: (s * co.y * PPM, W_Y0 + co.z * PPM))(s))
    return B


T_PROFILE = [(-HW, 0.0), (HW, 0.0), (HW, Z_COPING), (HC, Z_COPING), (HC, WALL_H),
             (-HC, WALL_H), (-HC, Z_COPING), (-HW, Z_COPING)]
RECT_PROFILE = [(-HW, 0.0), (HW, 0.0), (HW, WALL_H), (-HW, WALL_H)]


def stepped(cx, cy, rings, vmap):
    """A square pier on (cx, cy): *rings* (half-width, z) from the foot up;
    a change of z is a band of four side faces, a change of width at one z
    the cap's underside. vmap(z0, z1) gives the band's (V of z = 0, scale,
    shift)."""
    B = Builder()
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    def P(h, z, k):
        return (cx + sq[k % 4][0] * h, cy + sq[k % 4][1] * h, z)
    for (h0, z0), (h1, z1) in zip(rings, rings[1:]):
        for k in range(4):
            quad = [P(h0, z0, k), P(h0, z0, k + 1), P(h1, z1, k + 1), P(h1, z1, k)]
            if abs(z0 - z1) < EPS:
                B.face(quad, patch("soffit"))
            else:
                y_z0, sc, sh = vmap(z0, z1)
                a, b = P(h0, z0, k), P(h0, z0, k + 1)
                B.face(quad, along(a, b, y_z0, sc, sh, cx, cy))
    h, z = rings[-1]
    B.face([P(h, z, k) for k in range(4)], captop(cx, cy))
    h, z = rings[0]
    B.face([P(h, z, k) for k in reversed(range(4))], patch("blank"))
    return B


def run_pier(cx, level):
    """A run's pier (and the free-standing pier): LOD0 the brick shaft under
    its overhanging cap; LOD1 one box of the cap's plan, the cap painted on
    its top 0.08 m; LOD2 and LOD3 that box with the band stretched so the
    cap's paint still lands on its top."""
    def vmap(z0, z1):
        if z0 >= PIER_SHAFT - EPS:                       # the cap's sides
            return P_Y0, 1.0, GATE_SHAFT - PIER_SHAFT
        if level >= 2:
            return P_Y0, (GATE_SHAFT + PIER_H - PIER_SHAFT) / PIER_H, 0.0
        return P_Y0, 1.0, 0.0
    if level == 0:
        rings = [(HP, 0.0), (HP, PIER_SHAFT), (HCAP, PIER_SHAFT), (HCAP, PIER_H)]
    elif level == 1:
        rings = [(HCAP, 0.0), (HCAP, PIER_SHAFT), (HCAP, PIER_H)]
    else:
        rings = [(HCAP, 0.0), (HCAP, PIER_H)]
    return stepped(cx, 0.0, rings, vmap)


def gate_parts(g, level):
    """The gate pier (LOD0 shaft and cap, below one box of the cap's plan,
    the band's cap rows on its top), the hinge post (to LOD1) and the leaf."""
    cx = g.away * (CAP_OVER + HG)

    def vmap(z0, z1):
        return P_Y0, 1.0, 0.0
    if level == 0:
        rings = [(HG, 0.0), (HG, GATE_SHAFT), (HGCAP, GATE_SHAFT), (HGCAP, GATE_H)]
    else:
        rings = [(HGCAP, 0.0), (HGCAP, GATE_H)]
    parts = [stepped(cx, GATE_Y, rings, vmap)]
    if level <= 1:
        px0, px1 = g.x(CAP_OVER, HINGE_D)
        y0, y1 = POST_Y

        def post_side(a, b):
            x0, yy0, w, h = POST_R
            if abs(a[1] - b[1]) < EPS:
                return lambda co: (x0 + (abs(co.x) - CAP_OVER) * PPM, yy0 + co.z * PPM)
            return lambda co: (x0 + (co.y - y0) * PPM, yy0 + co.z * PPM)
        parts.append(box(px0, px1, y0, y1, 0.0, POST_H, post_side, patch("paint"),
                         patch("blank")))
    lx0, lx1 = g.x(HINGE_D, HINGE_D + LEAF_W)

    def leaf_side(a, b):
        if abs(a[1] - b[1]) < EPS:
            x0, y0, w, h = GATE_R
            return lambda co: (x0 + (abs(co.x) - HINGE_D) * PPM, y0 + (co.z - LEAF_Z0) * PPM)
        return patch("paint")
    parts.append(box(lx0, lx1, LEAF_Y[0], LEAF_Y[1], LEAF_Z0, LEAF_Z0 + LEAF_H, leaf_side,
                     patch("paint"), patch("paint")))
    return parts


def parts_for(piece, level):
    """(solids, whether they meet and need the union)."""
    if isinstance(piece, Pier):
        return [run_pier(0.0, level)], False
    if isinstance(piece, Gate):
        return gate_parts(piece, level), level <= 1
    x0, x1 = piece.wall

    def side(a, b):
        return along(a, b, W_Y0)
    if level == 3 and not piece.piers:
        # the pierless run: one box of its plan, the coping's width
        return [box(x0, x1, -HC, HC, 0.0, WALL_H, side, top_strip, patch("blank"))], False
    if level == 3:
        # The piers stay (a consumer switching by screen size shows LOD3 at
        # ~25 m): LOD2's pier boxes, and the wall body as boxes between them,
        # each abutting a pier's face, so every solid is a separate closed
        # box and none passes into another. The +X end stays END_INSET short
        # of the joint, in the next piece's pier, 0.15 under its top and
        # 0.10 inside its faces: nothing coplanar with a neighbour.
        spans, a = [], x0
        for p in sorted(piece.piers):
            if p - HCAP > a + EPS:
                spans.append((a, p - HCAP))
            a = max(a, p + HCAP)
        spans.append((a, x1))
        walls = [box(s0, s1, -HW, HW, 0.0, WALL_H, side, top_strip, patch("blank"))
                 for s0, s1 in spans]
        return walls + [run_pier(p, level) for p in piece.piers], False
    # a pierless run keeps its coping on every tier: it sets the run's plan
    prof = T_PROFILE if level == 0 or not piece.piers else RECT_PROFILE
    return [wall(x0, x1, prof)] + [run_pier(p, level) for p in piece.piers], bool(piece.piers)


def build_lod(name, piece, level):
    """One tier as an unlinked object: the solids unioned (or, where they
    touch nothing, joined), welded, coplanar faces with continuous UVs
    dissolved, triangulated, and checked closed with no zero-area face."""
    import bmesh
    import bpy
    from asset_build import to_object, union
    solids, meet = parts_for(piece, level)
    objs = [to_object(B, "tmp_%s_%d" % (name, i)) for i, B in enumerate(solids)]
    if meet:
        obj = union(objs[0], objs[1:])
    else:
        obj = objs[0]
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for o in objs[1:]:
            bm.from_mesh(o.data)
            d = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.meshes.remove(d)
        bm.to_mesh(obj.data)
        bm.free()
    obj.name = "{}_LOD{}".format(name, level)
    obj.data.name = obj.name + "_mesh"
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.dissolve_limit(bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
                             delimit={'UV'})
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    if any(f.calc_area() < 1e-8 for f in bm.faces):
        bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges[:])
    flat = [f for f in bm.faces if f.calc_area() < 1e-8]
    open_ = [e for e in bm.edges if len(e.link_faces) != 2]
    if flat or open_:
        raise ValueError("%s LOD%d: %d zero-area faces, %d edges not on two faces"
                         % (name, level, len(flat), len(open_)))
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# ==================================================================== facts
def outline(piece):
    """The piece's plan outline at ground level, build frame: the wall and
    the piers' brick shafts (caps and coping overhang are above the ground);
    a gate piece's pier alone, the leaf and its post being no outer wall."""
    if isinstance(piece, Pier):
        return [(-HP, -HP), (HP, -HP), (HP, HP), (-HP, HP)]
    if isinstance(piece, Gate):
        x0, x1 = piece.x(CAP_OVER, CAP_OVER + GATE_PIER_W)
        return [(x0, GATE_Y - HG), (x1, GATE_Y - HG), (x1, GATE_Y + HG), (x0, GATE_Y + HG)]
    spans = [(piece.wall[0], piece.wall[1], HW)] + [(p - HP, p + HP, HP) for p in piece.piers]
    xs = sorted({x for a, b, _ in spans for x in (a, b)})
    cells = []
    for a, b in zip(xs, xs[1:]):
        mid = (a + b) / 2.0
        w = max((h for s0, s1, h in spans if s0 <= mid <= s1), default=0.0)
        if w <= 0.0:
            raise ValueError("the run's plan is not continuous at x %.3f" % mid)
        cells.append((a, b, w))
    lo, hi = [], []
    for a, b, w in cells:
        lo += [(a, -w), (b, -w)]
        hi += [(a, w), (b, w)]
    pts = lo + list(reversed(hi))
    out = []
    for p in pts:                       # drop repeats and collinear points
        if out and abs(p[0] - out[-1][0]) < EPS and abs(p[1] - out[-1][1]) < EPS:
            continue
        out.append(p)
    changed = True
    while changed:
        changed = False
        for i in range(len(out)):
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            if abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) < 1e-12:
                del out[i]
                changed = True
                break
    return out


def facts(piece):
    """The facts sidecar's per-piece half (scripts/model_facts.py): no
    storeys, no dwellings, no doors (an opening is a gap between pieces)."""
    return {"hero": False, "dwellings": 0, "footprint": outline(piece),
            "storeys": [], "doors": []}


# ==================================================================== asset
def piece_asset(name, here, piece):
    """(Asset, build_all, facts) for one piece; the pivot is authored at
    the origin (asset_build.Asset's pivot=), not the plan's centre."""
    import asset_build
    asset_build.check_toolchain()
    A = asset_build.Asset(name, here, VARIANTS, DEFAULT_VARIANT, night_lit=False,
                          pivot=(0.0, 0.0, 0.0))

    def build_all():
        return A.build_all(lambda: check_layout(piece),
                           lambda level: build_lod(name, piece, level))
    return A, build_all, (lambda: facts(piece))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "export":
        for path in export(sys.argv[2:]):
            print(path)
    else:
        print(__doc__)
