# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and the shared layout, for
savupiippu_brick_round.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
plan, heights, the stack's batter, the lifts and their bands, the head, the
platform, the ladder, side counts, region rectangles -- so a change here
cannot leave the UVs pointing at the wrong artwork.

The stack is 46.5 m tall and a 1024 atlas holds 16 m at 64 px/m, so the
shaft is cut into 4 m lifts, each sampling a band 256 rows tall whose V
tiles. Round the stack the bands tile too: every shaft band repeats every
SHAFT_P = 256 px (4 m) in U, painted SHAFT_ML px further left and an overrun
further right from its own period, so each facet's chord, wherever it falls,
samples continuous brick. A band is then only 256 px of artwork, and four of
them fit: MID, the clean lift every lift below 32.7 m samples, and U1-U3,
copies of MID with the soot thickening up the stack's upper third, so the
gradient runs on unbroken from lift to lift. Rows from the bottom:

    y    0 ..  269   BASE    the base's square brick walls, z 0 .. 4.2 m over a
                             cast concrete footing; range A (x 0 .. 435) is the
                             east, rear and west walls', range B (x 435 .. 870)
                             the front's, with the inlet's lintel. The walls'
                             trapezoids and the corner fillets above 4.2 m
                             sample range A 14 courses lower.
    x  880 .. 992            the inlet's closure; the wash seen from above
    y  276 ..  540   MID | U1          shaft bands, each with the strip the
    y  544 ..  808   U2  | U3          back facet of LOD2/LOD3 samples: brick
                                       with the painted ladder
    x  940 .. 1004           the hatch, the lamp, flat patches
    y  816 ..  933   HEAD    the concrete head band, 1.8 m, unwrapped round
                             the stack at 64 px/m; the steel cap ring
    x  532 ..  712           the octagon's concrete coping, one side

Rasterising is scripts/atlas.py's; dirt, algae, rust and faded paint are
scripts/weathering.py's fields, placed by weather() below. weathering.py has
no soot, so the soot is this module's own shade and dirt (see soot()).
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import weathering  # noqa: E402

ASSET = "savupiippu_brick_round"
ATLAS = 1024
PPM = 64.0
PAD = 2


def m(v):
    return v * PPM


# ------------------------------------------------------------------ the base
BH = 3.4                # the base: 6.8 x 6.8 m at its walls
Z_FOOT = 0.3125         # 20 px; cast concrete footing course
Z_SQ = 4.2              # the square walls' head, where the corner fillets start
Z_OCT = 5.4             # the fillets' head: the plan is an octagon from here
Z_CAP = 5.7             # the octagon's concrete coping
Z_SHAFT0 = 6.2          # the wash rises from the coping to the shaft's foot
OCT_A = BH * math.tan(math.pi / 8)      # half an octagon side, 1.408 m

# ------------------------------------------------------------------ the shaft
SEG = 4.0               # one lift, 256 px: the bands' V period
NLIFT = 9               # full lifts, from the ladder's foot to the head
Z_LADDER0 = Z_SHAFT0 + 2.5              # 8.7: the ladder's foot, the lifts' phase
Z_HEAD0 = Z_LADDER0 + SEG * NLIFT       # 44.7: the shaft's top, the head's foot
R0, R1 = 2.06, 1.19     # outside radius at the shaft's foot and its top


def r_shaft(z):
    """The shaft's outside radius at height *z*: a straight batter of
    2.26 %, extrapolated above Z_HEAD0 for the ladder's line."""
    return R0 + (R1 - R0) * (z - Z_SHAFT0) / (Z_HEAD0 - Z_SHAFT0)


# Sides of the round, per tier. Vertices stand at r * k(n) so that the
# polygon's mean of apothem and corner radius is the true radius, and the
# shaft keeps its apparent width as the side count drops.
SIDES = (24, 16, 12, 8)


def k_sides(n):
    return 2.0 / (1.0 + math.cos(math.pi / n))


def chord(r, n):
    """One facet's width at radius r, metres."""
    return 2.0 * r * k_sides(n) * math.sin(math.pi / n)


# The lifts: (z0, z1, band, first row, last row in the band, carries the
# ladder). The first is the part lift from the wash to the ladder's foot,
# on MID's top 2.5 m; then nine full lifts. The soot starts at Z_SOOT0.
Z_SOOT0 = Z_LADDER0 + 6 * SEG           # 32.7
SOOT_BANDS = ("U1", "U2", "U3")


def _lifts():
    out = [(Z_SHAFT0, Z_LADDER0, "MID", m(SEG - (Z_LADDER0 - Z_SHAFT0)), m(SEG), False)]
    for i in range(NLIFT):
        z0 = Z_LADDER0 + i * SEG
        band = "MID" if z0 < Z_SOOT0 - 1e-6 else SOOT_BANDS[i - 6]
        out.append((z0, z0 + SEG, band, 0.0, m(SEG), True))
    return out


LIFTS = _lifts()
BAND_Z0 = {"U1": Z_SOOT0, "U2": Z_SOOT0 + SEG, "U3": Z_SOOT0 + 2 * SEG}

# ------------------------------------------------------------------ the head
HEAD_PROUD = 0.06
R_HEAD = R1 + HEAD_PROUD                # 1.25: the cast concrete head band
Z_TOP = 46.5
CAP_RING = 0.10                         # the steel cap ring, painted at the band's head
R_FLUE = 0.95
FLUE_DEPTH = 1.0

# ------------------------------------------------- the platform and ladder
Z_DECK = 45.0           # the service platform's deck, 1.5 m under the rim
DECK_T = 0.12
R_DECK = 2.0
RAIL_R = (1.93, 1.98)   # the railing's ring rails, radially
RAIL_Z = (46.0, 45.5)   # their tops: the hand rail and the knee rail
RAIL_H = 0.05
POSTS = tuple(60.0 * i for i in range(6))          # degrees from +X; the ladder is at 90
POST_W = 0.05
STRUT_Z = 44.1          # the platform's brackets leave the shaft here
STRUT_R = 1.82          # and meet the deck's underside here
STRUT_W = 0.06

LADDER_HALF = 0.22      # each rail's centre from the ladder's axis
RAIL_W, RAIL_D = 0.05, 0.07
STANDOFF = 0.20         # the rails' centre line off the back facet
Z_LADDER1 = Z_DECK + 1.0                # the rails run on as grab handles
RUNG_PITCH = SEG / 12.0                 # 0.333 m
RUNG = 0.03
RUNG_EVERY = (1, 3, None, None)         # LOD0 every rung, LOD1 every third
LADDER_BRACKETS = tuple([Z_LADDER0 + 0.2] + [Z_LADDER0 + SEG * i for i in range(1, NLIFT)]
                        + [Z_HEAD0 - 0.4])
BRACKET_W = 0.04
BRACKET_EVERY = (1, None, None, None)   # LOD0 every pair; none beyond (under a pixel)

# Every attachment is its own closed solid, held this far off whatever it
# would touch (the shaft, a rail, the deck), so nothing is boolean-cut.
GAP = 0.0015

# The safety cage: flat-bar hoops from 2.5 m above the ladder's foot to under
# the deck, every CAGE_PITCH along the batter, and three vertical straps
# outside them. A hoop is four chords in plan, (x, out from the rails' centre
# line) from one rail's outer face round behind the climber to the other's.
CAGE_Z0 = Z_LADDER0 + 2.5               # 11.2
CAGE_PITCH = 1.65
CAGE_N = 21                             # the top hoop at 44.2
CAGE_EVERY = (1, 3, None, None)         # LOD1 every third hoop, and the top one
HOOP = ((0.35, 0.38), (0.0, 0.70))      # the corner and the back, x >= 0
HOOP_T, HOOP_H = 0.008, 0.05            # the flat bar's thickness and depth
STRAP_W, STRAP_T = 0.05, 0.008

# The lightning down conductor: a copper strap beside the ladder, COND_X
# east of its axis, COND_OFF off the brickwork on saddles; up the head band
# to a clamp block under the air terminal. Down the wash, the coping and the
# base's rear wall it is paint (COND_*_R).
COND_X = 0.275
COND_W, COND_T = 0.025, 0.012
COND_OFF = 0.04
# The air terminal, on the strap's line: a copper rod ROD_W square at its
# foot, tapering to ROD_W_TOP at its shoulder and a point ROD_POINT long,
# its tip a metre over the rim (the stack's height), its inner face COND_OFF
# off the band. Below it a clamp block joins the strap (CLAMP_Z, CLAMP_W
# wide, CLAMP_OFF out from the band), and a small bracket under the cap ring
# holds it to the band (ROD_BRACKET_Z), on LOD0/LOD1. LOD2/LOD3 keep a
# three-sided spike SPIKE_W wide from ROD_FOOT to the same tip, so every
# tier has the same height.
ROD_TIP = Z_TOP + 1.0                   # 47.5
CLAMP_Z = (46.11, 46.20)
ROD_FOOT = CLAMP_Z[1] + GAP
ROD_W, ROD_W_TOP, ROD_POINT = 0.045, 0.026, 0.12
CLAMP_W, CLAMP_OFF = 0.07, (0.012, 0.095)
ROD_BRACKET_Z, ROD_BRACKET_W = (46.33, 46.37), 0.03
SPIKE_W = 0.05

# The obstruction lamps on the head band: east, west and front, the back
# being the ladder's (degrees from +X, counter-clockwise from above). Each is
# a hexagonal body, a cast housing under a red lens with a domed top, on a
# short arm from the band.
LAMP_ANGLES = (0.0, 180.0, 270.0)
LAMP_Z = (46.06, 46.11, 46.22, 46.27)   # foot, housing's head / lens's foot, lens's top, dome
LAMP_RAD = 0.065                        # the body's corner radius
LAMP_OUT = 0.13                         # its axis off the band
LAMP_ARM = (0.03, 0.025)                # the arm's width and depth

# ------------------------------------------------------------- the atlas
SHAFT_P = 256           # px: every shaft band's period round the stack (4 m)
SHAFT_ML = 40           # its left margin: a lift's taper moves a facet's top
                        # chord up to 2 pi (R0 - R1) / NLIFT ... 36 px left
BLEND = 32              # px over which the period's end is blended into its start
# name: (x0 of the period, y0, overrun past the period, strip x, strip width)
BANDS = {
    "MID": (44, 280, 110, 418, 110),
    "U1": (576, 280, 78, 922, 78),
    "U2": (44, 548, 78, 386, 78),
    "U3": (512, 548, 78, 854, 78),
}
BAND_H = 256

PL_Y0 = 0
BASE_TOP_PX = m(Z_SQ)                   # 268.8
U_OFF = {"east": 0.0, "rear": 0.0, "west": 0.0, "front": 2 * BH}
FILLET_SHIFT_COURSES = 14               # trapezoids and fillets sample 14 courses lower

# The flue inlet, on the front (-Y), toward the hall: a closed opening in
# the base under a cast concrete lintel. The cleanout hatch: low on the
# east wall. (centre along the wall from its p0, sill z, width, height)
INLET = (BH, 1.0, 1.625, 2.0)
INLET_REVEAL = 0.25
Z_LINTEL = (3.0, 3.25)
LINTEL_HALF = 1.0625
HATCH = (BH, 0.4375, 0.703125, 0.90625)

INLET_R = (880, 6, 104, 128)            # 1.625 x 2.0 m
WASH_PPM = 16.0                         # the wash, seen from above
WASH_R = (880, 146, 112, 112)           # 7.0 x 7.0 m at 16 px/m
HATCH_R = (940, 556, 45, 58)            # 0.703 x 0.906 m
LAMP_R = (940, 626, 16, 10)             # 0.25 x 0.16 m: housing, then lens
HEAD_R = (4, 816, 516, m(Z_TOP - Z_HEAD0))
COPING_R = (532, 816, m(2 * OCT_A), m(Z_CAP - Z_OCT))
# The conductor's painted run down the base: the rear wall's strip, 12 px of
# range A's brick with the strap on it (the rear wall and its trapezoid
# sample it), and the rear coping side's strip, likewise
COND_S0 = BH - COND_X - 6 / PPM         # the strip's start along the rear wall
COND_SW = 12
COND_BASE_R = (998, 0, COND_SW, BASE_TOP_PX)
COND_COPING_R = (724, 816, COND_SW, m(Z_CAP - Z_OCT))
PATCH_NAMES = ("blank", "soot", "conc", "under", "rim", "steel", "deck", "copper")
PATCHES = {n: (940 + 24 * (i % 3), 660 + 24 * (i // 3), 16, 16)
           for i, n in enumerate(PATCH_NAMES)}

# ------------------------------------------------------------------ brick
# Finnish brick, 285 x 135 x 85 mm with 10 mm joints. The shaft is radial
# brick in header bond; the base is stretcher bond. 42 courses to a lift,
# so the bond and its tone repeat with the bands' V period, and the half-brick
# offset alternates across a lift's joint too.
COURSES = 42
COURSE = SEG / COURSES                  # 0.0952 m, 6.10 px
HEADER_N = 27                           # header bricks to the shaft bands' period
STRETCH_N = 54                          # stretchers across the atlas
FILLET_SHIFT = FILLET_SHIFT_COURSES * COURSE      # 1.333 m

# Galvanised flats round the top 10 m, thin and dulled by soot.
BANDS_Z = (38.5, 41.5, 43.9)
BAND_W = 0.05

# ----------------------------------------------------------- material ids
ID_BLANK, ID_CONC, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_GALV, ID_LADDER, ID_HATCH, ID_PLATE, ID_SOOT = 5, 6, 7, 8, 9
ID_HEADC, ID_LAMP, ID_LENS, ID_DARK, ID_STEEL, ID_DECK = 10, 11, 12, 13, 14, 15
ID_COPPER, ID_CAP = 16, 17

SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_CONC: (0.90, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.80, 0.0), ID_MORTAR: (0.94, 0.0), ID_GALV: (0.55, 0.45),
    ID_LADDER: (0.62, 0.20), ID_HATCH: (0.58, 0.0), ID_PLATE: (0.74, 0.10),
    ID_SOOT: (0.97, 0.0), ID_HEADC: (0.95, 0.0), ID_LAMP: (0.50, 0.0),
    ID_LENS: (0.06, 0.0), ID_DARK: (0.96, 0.0), ID_STEEL: (0.60, 0.35),
    ID_DECK: (0.70, 0.20), ID_COPPER: (0.58, 0.30), ID_CAP: (0.66, 0.25),
}

# One brick per instance, the same three as the plant's other brick
# buildings, so the stack matches its hall. red_brick is the plant's dulled
# red: every brick-face constant c of the catalog's red brick (144, 72, 52),
# (114, 58, 45) and mortar (150, 145, 136) taken to Y + 0.6 (c - Y), Y its
# Rec.709 luma, then times 0.94; the mortar a further 10 % darker.
# brown_brick is a dark purple-brown clinker, well below the red in value
# and redness; both are the same constants in all five of the plant's pieces.
VARIANTS = {
    "red_brick": {"brick": (114, 73, 62), "brick2": (90, 59, 51),
                  "mortar": (125, 123, 118)},
    "yellow_brick": {"brick": (188, 166, 122), "brick2": (164, 142, 104),
                     "mortar": (160, 156, 148)},
    "brown_brick": {"brick": (80, 59, 57), "brick2": (62, 46, 45),
                    "mortar": (108, 106, 102)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_BLANK: (52, 52, 52), ID_CONC: (156, 154, 147), ID_GALV: (104, 105, 102),
    ID_LADDER: (40, 40, 41), ID_HATCH: (58, 66, 62), ID_PLATE: (44, 43, 42),
    ID_SOOT: (22, 21, 20), ID_HEADC: (158, 155, 148), ID_LAMP: (92, 94, 96),
    ID_LENS: (112, 30, 26), ID_DARK: (24, 24, 24), ID_STEEL: (70, 71, 70),
    ID_DECK: (58, 58, 58), ID_COPPER: (96, 110, 90), ID_CAP: (46, 46, 47),
}

BRICK_IDS = (ID_BRICK, ID_BRICK2, ID_MORTAR)

# ---------------------------------------------------------------- relief
BRICK_FACE = 0.006      # brick proud of the recessed joint
BAND_RELIEF = 0.008     # the galvanised flats
LADDER_RELIEF = 0.03    # the painted ladder of the far tiers


# ================================================================== brick
def paint_brick(c, x0, x1, y0, y1, y_ref, blen, n_period, x_ref=0.0):
    """Brick over the rect, courses counted from row *y_ref*, bricks *blen*
    px long from column *x_ref*, alternate courses offset by half a brick.
    Tone repeats every COURSES courses and every *n_period* bricks, so a
    band painted with it tiles in both directions."""
    course = m(COURSE)
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    r = np.floor((Y - y_ref) / course).astype(np.int64)
    off = (r % 2) * blen * 0.5
    b = np.floor((X - x_ref - off) / blen).astype(np.int64) % n_period
    rr = r % COURSES
    bed = (Y - y_ref - r * course) < 1.0
    perp = ((X - x_ref - off) % blen) < 1.0
    joint = bed | perp
    tone = 0.88 + 0.22 * atlas.hash_unit(b, rr, 17 + n_period)
    dark = atlas.hash_unit(b, rr, 29 + n_period) < 0.16
    c.mid[sy, sx] = np.where(joint, ID_MORTAR, np.where(dark, ID_BRICK2, ID_BRICK))
    c.shade[sy, sx] = np.where(joint, 0.94, tone)
    c.ao[sy, sx] = np.where(joint, 0.82, 1.0)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)


def _period_rows(y0, y1, ref, period, offsets):
    """Rows within y0..y1 at *offsets* (px) into every *period* from *ref*."""
    out = []
    k0 = int(math.floor((y0 - ref) / period)) - 1
    k1 = int(math.ceil((y1 - ref) / period)) + 1
    for k in range(k0, k1 + 1):
        for o in offsets:
            y = ref + k * period + o
            if y0 - 8 <= y <= y1 + 8:
                out.append(y)
    return out


# ================================================================ the base
def paint_base(c):
    """The base band: a cast concrete footing course and stretcher-bond
    brick to the square walls' head. Range B, the front's, carries the
    inlet's cast concrete lintel."""
    y0 = PL_Y0
    top = y0 + BASE_TOP_PX
    x1 = m(4 * BH)
    paint_brick(c, -PAD, x1 + PAD, y0 + m(Z_FOOT), top + PAD, y0 + m(Z_FOOT),
                ATLAS / STRETCH_N, STRETCH_N)
    c.paint(-PAD, x1 + PAD, y0 - PAD, y0 + m(Z_FOOT), ID_CONC, 1.0, 1.0, height=0.0)
    c.mul(-PAD, x1 + PAD, y0 + m(Z_FOOT) - 1.5, y0 + m(Z_FOOT), 0.88, ao=0.85)
    c.lift(-PAD, x1 + PAD, y0 + m(Z_FOOT) - 1.0, y0 + m(Z_FOOT), 0.004)
    s0 = m(U_OFF["front"] + INLET[0] - LINTEL_HALF)
    s1 = m(U_OFF["front"] + INLET[0] + LINTEL_HALF)
    l0, l1 = y0 + m(Z_LINTEL[0]), y0 + m(Z_LINTEL[1])
    c.paint(s0, s1, l0, l1, ID_CONC, 0.95, 1.0)
    c.bevel(s0, s1, l0, l1, 0.008, 1.0)
    c.mul(s0, s1, l0 - 1.5, l0, 0.86, ao=0.82)


def paint_coping(c):
    """One side of the octagon's coping: trowelled concrete, an arris at its
    head, its drip shadow on the brick below being the fillets' own."""
    x, y, w, h = COPING_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CONC, 0.97, 1.0, height=0.0)
    c.paint(x - PAD, x + w + PAD, y + h - 2, y + h + PAD, ID_CONC, 1.03, 1.0, height=0.004)
    c.mul(x - PAD, x + w + PAD, y - PAD, y + 1.5, 0.86, ao=0.82)


def paint_wash(c):
    """The wash from the coping up to the shaft, seen from above at 16 px/m:
    trowelled concrete, darker with soot fallout and wet near the shaft."""
    x, y, w, h = WASH_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CONC, 0.95, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    r = np.hypot(X - (x + w / 2), Y - (y + h / 2)) / WASH_PPM
    c.shade[sy, sx] *= 0.74 + 0.26 * np.clip((r - R0) / 0.4, 0.0, 1.0)
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.7 + 0.3 * np.clip((r - R0) / 0.2, 0, 1))


# ================================================================ the shaft
def paint_mid(c):
    """MID, the clean lift: header bond over the band's period, its margins
    and its overrun, and PAD + 2 rows into both gutters from the formula
    itself, so the gutters carry the band's opposite end."""
    x0, y0, ov, _sx, _sw = BANDS["MID"]
    paint_brick(c, x0 - SHAFT_ML - PAD, x0 + SHAFT_P + ov + PAD, y0 - 4, y0 + BAND_H + 4,
                y0, SHAFT_P / HEADER_N, HEADER_N, x_ref=x0)


def _shaft_rows(c, y0):
    return slice(c._idx(y0 - 4), c._idx(y0 + BAND_H + 4))


def tile_shaft(c, arrays):
    """Make MID periodic in U and copy it to U1-U3 and to every band's
    ladder strip, for each array (sample resolution) in *arrays*.

    The brick is periodic already; the noise painted over it (tone wear,
    grime, the weathering fields) is the whole canvas's. Over the period's
    last BLEND px it is blended into what lies just left of the period's
    start, so the period's end meets its start, and the period is then
    written out over the margin and the overrun. Ids are copied, not
    blended."""
    ss = c.ss
    x0, y0, ov, sx, sw = BANDS["MID"]
    rs = _shaft_rows(c, y0)
    X0, Ps, Ls, Bs, ps = x0 * ss, SHAFT_P * ss, (SHAFT_ML + PAD) * ss, BLEND * ss, PAD * ss
    t = atlas.smoothstep(0.0, 1.0, (np.arange(Bs, dtype=np.float32) + 0.5) / Bs)[None, :]
    span = np.arange(-Ls, Ps + (ov + PAD) * ss) % Ps
    for A in arrays:
        base = A[rs, X0:X0 + Ps].copy()
        if A.dtype != np.uint8:
            base[:, Ps - Bs:] = (1.0 - t) * base[:, Ps - Bs:] + t * A[rs, X0 - Bs:X0]
        A[rs, X0 - Ls:X0 + Ps + (ov + PAD) * ss] = base[:, span]
    for name, (bx, by, bov, bsx, bsw) in BANDS.items():
        rd = _shaft_rows(c, by)
        for A in arrays:
            if name != "MID":
                W = Ls + Ps + (bov + PAD) * ss
                A[rd, bx * ss - Ls:bx * ss - Ls + W] = A[rs, X0 - Ls:X0 - Ls + W]
            # the strip: the period's first columns, under the painted ladder
            A[rd, bsx * ss - ps:(bsx + bsw) * ss + ps] = A[rs, X0:X0 + bsw * ss + 2 * ps]


def band_extent(name):
    """(x0, x1) of a band's periodic area and of its strip, padded."""
    x0, y0, ov, sx, sw = BANDS[name]
    return ((x0 - SHAFT_ML - PAD, x0 + SHAFT_P + ov + PAD), (sx - PAD, sx + sw + PAD))


def paint_galv(c):
    """The galvanised flats in the top 10 m: thin, a raised arris top and
    bottom, a little occlusion under each. On the lifts' copies, periodic
    and strip alike."""
    for name in SOOT_BANDS:
        x0, y0, ov, sx, sw = BANDS[name]
        for zb in BANDS_Z:
            v = (zb - BAND_Z0[name]) * PPM
            if not (-4 < v < BAND_H + 4):
                continue
            yb = y0 + v
            for a, b in band_extent(name):
                c.paint(a, b, yb, yb + m(BAND_W), ID_GALV, 1.0, 1.0)
                c.bevel(a, b, yb, yb + m(BAND_W), BAND_RELIEF, 0.8, axes="y")
                c.mul(a, b, yb - 1.5, yb, 0.88, ao=0.82)


def paint_ladder(c):
    """The far tiers' ladder, painted on every band's strip (the back facet
    of LOD2/LOD3): two dark rails 0.44 m apart and a rung every third of a
    metre, the brick between them in the ladder's shade, so at 70 m and
    beyond it reads as one dark line up the back."""
    hw, rw = m(LADDER_HALF), m(0.05)
    pitch = m(RUNG_PITCH)
    for name, (x0, y0, ov, sx, sw) in BANDS.items():
        cx = sx + sw / 2.0
        y_a, y_b = y0 - 4, y0 + BAND_H + 4
        c.mul(cx - hw, cx + hw, y_a, y_b, 0.55, ao=0.7)
        for side in (-1, 1):
            xr = cx + side * hw
            c.paint(xr - rw / 2, xr + rw / 2, y_a, y_b, ID_LADDER, 1.0, 0.9,
                    height=LADDER_RELIEF)
            c.mul(xr - rw / 2 - 1.5, xr + rw / 2 + 1.5, y_a, y_b, 0.85)
        for yr in _period_rows(y_a, y_b, y0, pitch, [pitch * 0.5]):
            c.paint(cx - hw, cx + hw, max(yr, y_a), min(yr + 1.8, y_b), ID_LADDER, 1.0,
                    0.9, height=LADDER_RELIEF)
        # the down conductor, COND_X east of the ladder's axis (U runs west
        # across the back facet), the far tiers' only trace of it
        paint_conductor(c, cx - m(COND_X), y_a, y_b, y0)


def paint_conductor(c, xc, y0, y1, ref, face=1.0, edge=0.86):
    """The copper strap, a column at *xc* from row y0 to y1: a dull,
    weathered copper face COND_W wide at shade *face*, raised, a soft
    shadow *edge* either side, and a saddle every metre from row *ref* (a
    band's V period is four metres, so they tile)."""
    hw = m(COND_W) / 2.0
    c.mul(xc - hw - 1.2, xc + hw + 1.2, y0, y1, edge, ao=0.85)
    c.paint(xc - hw, xc + hw, y0, y1, ID_COPPER, face, 0.95, height=0.006)
    for yr in _period_rows(y0, y1, ref, m(1.0), [m(0.5)]):
        c.paint(xc - hw - 0.8, xc + hw + 0.8, max(yr - 0.7, y0), min(yr + 0.7, y1),
                ID_COPPER, 0.8 * face, 0.85, height=0.009)


# ================================================================= the head
HEAD_BOARDS = 80        # formwork staves round the head band (~0.1 m)
HEAD_LIFT = 0.9         # the lift joint, above the band's foot


def paint_head(c):
    """The head band: cast concrete in two lifts against narrow vertical
    staves, so its face carries the boards' marks: each stave its own tone
    and a millimetre or two proud or back, a fin at every joint, the grain
    of the wood, and a row of form-tie holes in each lift. The lift joint
    is a dark groove with the upper lift's staves offset half a board. The
    top 0.1 m is the cap ring, distinct dark steel with a drip shadow."""
    x, y, w, h = HEAD_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_HEADC, 1.0, 1.0, height=0.0)
    bw = w / HEAD_BOARDS
    yj = y + m(HEAD_LIFT)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    upper = Y >= yj
    off = np.where(upper, 0.5 * bw, 0.0)
    b = np.floor((X - x - off) / bw).astype(np.int64) % HEAD_BOARDS
    lift = upper.astype(np.int64)
    fin = ((X - x - off) % bw) < 0.45
    tone = 0.95 + 0.10 * atlas.hash_unit(b, lift, 71)
    proud = 0.0015 * (atlas.hash_unit(b, lift, 73) - 0.5)
    c.shade[sy, sx] = tone * np.where(upper, 0.97, 1.0)
    c.height[sy, sx] = np.where(fin, 0.0018, proud)
    c.ao[sy, sx] = np.where(fin, 0.92, 1.0)
    # the grain: long streaks along the staves, in height and tone
    grain = atlas.noise(c, 41, 0.5, 14.0)[sy, sx]
    c.height[sy, sx] += 0.0005 * grain
    c.shade[sy, sx] *= 1.0 + 0.025 * grain
    # the lift joint
    c.paint(x - PAD, x + w + PAD, yj - 0.5, yj + 0.5, ID_HEADC, 0.72, 0.7, height=-0.004)
    c.mul(x - PAD, x + w + PAD, yj - 2.0, yj - 0.5, 0.92)
    # form-tie holes, a row in each lift, every fourth stave
    for zt in (0.40, HEAD_LIFT + 0.45):
        for k in range(HEAD_BOARDS // 4):
            cx = x + (4 * k + 2 + (0.5 if zt > HEAD_LIFT else 0.0)) * bw
            c.disc(cx, y + m(zt), 0.9, ID_HEADC, 0.55, 0.6, height=-0.004)
    # the cap ring
    yc = y + h - m(CAP_RING)
    c.paint(x - PAD, x + w + PAD, yc, y + h + PAD, ID_CAP, 1.0, 1.0, height=0.0)
    c.bevel(x - PAD, x + w + PAD, yc, y + h + PAD, 0.006, 1.0, axes="y")
    c.mul(x - PAD, x + w + PAD, yc - 2.5, yc, 0.78, ao=0.72)
    # the band stands 0.06 proud: its foot's arris
    c.paint(x - PAD, x + w + PAD, y - PAD, y + 1.5, ID_HEADC, 0.92, 0.9, height=0.0)


def paint_lamp(c):
    """An obstruction lamp's sides: the grey cast housing, then the red
    glass lens. The body's faces sample it by height; the dome samples the
    lens's top rows, the underside the housing."""
    x, y, w, h = LAMP_R
    yl = y + m(LAMP_Z[1] - LAMP_Z[0])
    c.paint(x - PAD, x + w + PAD, y - PAD, yl, ID_LAMP, 1.0, 0.95, height=0.0)
    c.paint(x - PAD, x + w + PAD, yl, y + h + PAD, ID_LENS, 1.0, 1.0, height=0.0)
    c.mul(x - PAD, x + w + PAD, yl - 1.0, yl, 0.8, ao=0.8)


# ================================================================= regions
def paint_inlet(c):
    """The flue inlet's closure: a steel angle frame round a blanking plate
    of two bolted sheets with a stiffener, black and sooted, a small
    inspection door low in it."""
    x, y, w, h = INLET_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_PLATE, 0.9, 0.85,
            height=0.025)
    c.bevel(x - PAD, x + w + PAD, y - PAD, y + h + PAD, 0.025, 1.0)
    F = 5
    c.paint(x + F, x + w - F, y + F, y + h - F, ID_PLATE, 1.0, 0.92, height=0.0)
    c.mul(x + F, x + w - F, y + h - F - 2, y + h - F, 0.82, ao=0.78)
    c.paint(x + w / 2 - 0.5, x + w / 2 + 0.5, y + F, y + h - F, ID_DARK, 1.0, 0.7,
            height=-0.002)
    ym = y + h * 0.55
    c.paint(x + F, x + w - F, ym, ym + 4, ID_PLATE, 1.1, 0.95, height=0.03)
    c.bevel(x + F, x + w - F, ym, ym + 4, 0.03, 1.0, axes="y")
    c.mul(x + F, x + w - F, ym - 2, ym, 0.84, ao=0.8)
    for bx in np.arange(x + 2.5, x + w - 1, 8.0):
        for by in (y + 2.5, y + h - 2.5):
            c.disc(bx, by, 1.1, ID_PLATE, 1.15, 0.9, height=0.035)
    for by in np.arange(y + 2.5, y + h - 1, 8.0):
        for bx in (x + 2.5, x + w - 2.5):
            c.disc(bx, by, 1.1, ID_PLATE, 1.15, 0.9, height=0.035)
    dx0, dx1, dy0, dy1 = x + w / 2 - 20, x + w / 2 + 20, y + 14, y + 44
    c.paint(dx0, dx1, dy0, dy1, ID_PLATE, 1.05, 0.95, height=0.02)
    c.bevel(dx0, dx1, dy0, dy1, 0.02, 1.0)
    c.mul(dx0, dx1, dy0 - 2, dy0, 0.82, ao=0.8)
    c.paint(dx1 - 7, dx1 - 3, dy0 + 10, dy0 + 20, ID_STEEL, 0.9, 0.9, height=0.03)


def paint_hatch(c):
    """The cleanout hatch: a cast iron frame and a painted door on two strap
    hinges, a wedge latch, a raised panel."""
    x, y, w, h = HATCH_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_PLATE, 1.0, 0.85,
            height=0.02)
    c.bevel(x - PAD, x + w + PAD, y - PAD, y + h + PAD, 0.02, 1.0)
    F = 3
    c.paint(x + F, x + w - F, y + F, y + h - F, ID_HATCH, 1.0, 0.95, height=0.0)
    c.mul(x + F, x + w - F, y + h - F - 2, y + h - F, 0.82, ao=0.78)
    c.paint(x + F + 5, x + w - F - 5, y + F + 6, y + h - F - 6, ID_HATCH, 1.04, 1.0,
            height=0.012)
    c.bevel(x + F + 5, x + w - F - 5, y + F + 6, y + h - F - 6, 0.012, 1.5)
    for hy in (y + 12, y + h - 14):
        c.paint(x + F - 1, x + F + 16, hy, hy + 3, ID_HATCH, 0.8, 0.9, height=0.02)
    c.paint(x + w - F - 6, x + w - F - 2, y + h / 2 - 6, y + h / 2 + 6, ID_STEEL,
            0.9, 0.9, height=0.03)


def conductor_strips(c, arrays):
    """The conductor's run down the base, painted: range A's columns under
    the rear wall's strip and the coping's under its rear side's copied, for
    each array in *arrays*, into their own regions, so the brick and the
    concrete run on across the strip's edges, and the strap painted down
    the middle of each; and the strap across the wash, seen from above."""
    ss = c.ss
    s_cop = OCT_A - COND_X - (COND_SW / 2.0) / PPM      # the rear coping side runs west
    for (x, y, w, h), u0 in ((COND_BASE_R, m(U_OFF["rear"] + COND_S0)),
                             (COND_COPING_R, COPING_R[0] + m(s_cop))):
        rows = slice(c._idx(y - PAD), c._idx(y + h + PAD))
        a0, d0 = int(round((u0 - PAD) * ss)), int(round((x - PAD) * ss))
        n = (w + 2 * PAD) * ss
        for A in arrays:
            A[rows, d0:d0 + n] = A[rows, a0:a0 + n]
        # darker than the shaft's strap and with a deeper shadow, so it
        # still reads on the base's rear wall in shade
        paint_conductor(c, x + w / 2.0, y - PAD, y + h + PAD, PL_Y0, face=0.78, edge=0.72)
    # across the wash, 2 px (0.125 m at the wash's 16 px/m) of dark
    # weathered copper: a lighter or thinner line reads as a seam
    x, y, w, h = WASH_R
    xc = x + w / 2.0 + COND_X * WASH_PPM
    c.stroke((xc, y + h / 2.0 + (R0 + 0.02) * WASH_PPM), (xc, y + h / 2.0 + BH * WASH_PPM + 1.0),
             2.0, ID_COPPER, 0.6, ao=0.85, height=0.006)


def paint_patches(c):
    spec = {"blank": (ID_BLANK, 1.0, 1.0), "soot": (ID_SOOT, 0.9, 0.5),
            "conc": (ID_CONC, 0.92, 0.9), "under": (ID_HEADC, 0.55, 0.6),
            "rim": (ID_SOOT, 1.25, 0.8), "steel": (ID_STEEL, 1.0, 1.0),
            "deck": (ID_DECK, 1.0, 0.9), "copper": (ID_COPPER, 0.9, 1.0)}
    atlas.paint_patches(c, PATCHES, spec)


# ------------------------------------------------------------------ checks
def _rects():
    out = {"inlet": INLET_R, "wash": WASH_R, "hatch": HATCH_R, "lamp": LAMP_R,
           "head": HEAD_R, "coping": COPING_R, "cond_base": COND_BASE_R,
           "cond_coping": COND_COPING_R,
           "base": (0, PL_Y0, m(4 * BH), BASE_TOP_PX)}
    for name, (x0, y0, ov, sx, sw) in BANDS.items():
        out[name] = (x0 - SHAFT_ML, y0 - 2, SHAFT_ML + SHAFT_P + ov, BAND_H + 4)
        out[name + "_strip"] = (sx, y0 - 2, sw, BAND_H + 4)
    out.update(PATCHES)
    return out


def check_regions():
    rects = _rects()
    problems = []
    names = sorted(rects)
    for i, a in enumerate(names):
        ax, ay, aw, ah = rects[a]
        if ax < 0 or ay < 0 or ax + aw + PAD > ATLAS or ay + ah + PAD > ATLAS:
            problems.append("%s runs off the atlas" % a)
        for b in names[i + 1:]:
            bx, by, bw, bh = rects[b]
            if (ax - 2 * PAD < bx + bw and bx - 2 * PAD < ax + aw
                    and ay - 2 * PAD < by + bh and by - 2 * PAD < ay + ah):
                problems.append("%s and %s overlap" % (a, b))
    if abs(INLET_R[2] / PPM - INLET[2]) > 0.02 or abs(INLET_R[3] / PPM - INLET[3]) > 0.02:
        problems.append("the inlet region does not match the opening")
    if abs(HATCH_R[2] / PPM - HATCH[2]) > 0.02 or abs(HATCH_R[3] / PPM - HATCH[3]) > 0.02:
        problems.append("the hatch region does not match the hatch")
    if WASH_R[2] < 2 * BH * WASH_PPM:
        problems.append("the wash region is too small")
    if abs(m(SEG) - BAND_H) > 1e-6 or BAND_H * 4 != ATLAS:
        problems.append("a lift is not a band's height, or it does not divide the atlas")
    if abs(SHAFT_P / HEADER_N / PPM - 0.148) > 0.005:
        problems.append("the header bricks are not 135 mm and a joint long")
    if FILLET_SHIFT_COURSES % 2:
        problems.append("the fillets' shift breaks the stretcher bond")
    if Z_OCT - FILLET_SHIFT < Z_FOOT + 1.6 or Z_OCT - FILLET_SHIFT > Z_SQ - 0.05:
        problems.append("the trapezoids sample outside the base band's plain brick")
    if Z_LINTEL[1] + 0.2 > Z_SQ:
        problems.append("the lintel crowds the square walls' head")
    lamp_px = m(LAMP_Z[2] - LAMP_Z[0])
    if abs(lamp_px - LAMP_R[3]) > 1.0 or LAMP_R[2] < m(LAMP_RAD) + 2:
        problems.append("the lamp region does not match the lamp")
    if abs(m(COND_S0) - round(m(COND_S0))) > 1e-6 or COND_BASE_R[3] != BASE_TOP_PX:
        problems.append("the conductor's wall strip is not whole columns of the base band")
    if abs(COND_COPING_R[3] - COPING_R[3]) > 1e-6 or COND_COPING_R[1] != COPING_R[1]:
        problems.append("the conductor's coping strip does not match the coping")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def soot(c, x0, x1, y0, y1, fn):
    """Soot staining, which scripts/weathering.py has no field for: shade
    darkened and pulled toward its dirt by fn(Y, X) in 0..1, per sample."""
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    s = fn(Y, X)
    c.shade[sy, sx] *= 1.0 - 0.70 * s
    c.weather.f["D"][sy, sx] += 0.45 * s


def _streak(seed, period, amount=0.30):
    """Vertical soot streaks: a sum of cosines round the stack, periodic on
    *period* px, mean 1, standard deviation *amount*."""
    rs = np.random.RandomState(seed)
    ks = np.arange(3, 28)
    amp = rs.uniform(0.3, 1.0, len(ks)) / ks ** 0.6
    ph = rs.uniform(0, 2 * np.pi, len(ks))
    amp *= amount / np.sqrt(0.5 * np.sum(amp ** 2))

    def f(X):
        out = np.ones_like(X)
        for k, a, p in zip(ks, amp, ph):
            out += a * np.cos(2 * np.pi * k * X / period + p)
        return out
    return f


STREAK = _streak(31, SHAFT_P)


def soot_shaft(z):
    """The shaft's soot by height: none below Z_SOOT0, then thickening
    almost linearly over the shaft's upper third, from its first trace at
    32.7 m to heaviest under the head. MID repeats under every lift below
    Z_SOOT0, so the grade cannot start lower without a fifth band."""
    t = np.clip((z - Z_SOOT0) / (Z_HEAD0 - Z_SOOT0), 0.0, None)
    return 0.98 * t ** 1.05


def soot_head(z):
    """The head band's, before its runs: a moderate film at its foot
    grading to heavy under the cap ring."""
    t = np.clip((z - Z_HEAD0) / (Z_TOP - Z_HEAD0 - CAP_RING), 0.0, 1.0)
    return 0.34 + 0.52 * t ** 1.3


# The head band is the stack's one surface unwrapped once round (it does not
# tile), so its soot can favour one side: the leeward, taken as east (+X).
LEE = 0.0


def head_angle(U):
    """The angle round the stack, degrees, of head-band column *U* on LOD0
    (24 sides, the unwrap starting at facet 0's first corner); the coarser
    tiers' unwraps differ by a few columns."""
    n = SIDES[0]
    w = chord(R_HEAD, n) * PPM * n
    return 90.0 - 180.0 / n + 360.0 * (U - HEAD_R[0]) / w


def head_runs(seed=53, count=90):
    """Soot runs hanging from the cap ring: narrow streaks of random width,
    length and weight, periodic round the band's width. Returns f(Y, X)."""
    x, y, w, h = HEAD_R
    top = y + h - m(CAP_RING)
    rs = np.random.RandomState(seed)
    xs = rs.uniform(0, w, count)
    wid = rs.uniform(0.7, 2.6, count)
    length = m(rs.uniform(0.15, 1.5, count))
    amp = rs.uniform(0.2, 0.65, count)

    def f(Y, X):
        out = np.zeros_like(X)
        d = np.clip(top - Y, 0.0, None)
        for xk, wk, lk, ak in zip(xs, wid, length, amp):
            dx = (X - x - xk + w / 2.0) % w - w / 2.0
            out += ak * np.exp(-(dx / wk) ** 2) * np.clip(1.0 - d / lk, 0.0, 1.0) ** 1.5
        return out
    return f


def paint_soot(c):
    """The soot gradient, on U1-U3 and their strips, and on the head."""
    for name in SOOT_BANDS:
        x0, y0, ov, sx, sw = BANDS[name]
        z0 = BAND_Z0[name]
        for (a, b), ref in zip(band_extent(name), (x0, sx)):
            soot(c, a, b, y0 - 4, y0 + BAND_H + 4,
                 lambda Y, X, ref=ref, y0=y0, z0=z0: np.clip(
                     soot_shaft(z0 + (Y - y0) / PPM) * STREAK(X - ref), 0.0, 1.0))
    # the shadow under the head band's 0.06 m projection, on the top lift
    x0, y0, ov, sx, sw = BANDS["U3"]
    for a, b in band_extent("U3"):
        c.mul(a, b, y0 + BAND_H - 2.5, y0 + BAND_H + 4, 0.80, ao=0.75)
    x, y, w, h = HEAD_R
    runs, streak = head_runs(), _streak(37, w, 0.18)

    def head(Y, X):
        side = 1.0 + 0.22 * np.cos(np.radians(head_angle(X) - LEE))
        s = soot_head(Z_HEAD0 + (Y - y) / PPM) * streak(X - x) + runs(Y, X)
        return np.clip(s * side, 0.0, 1.0)
    soot(c, x - PAD, x + w + PAD, y - PAD, y + h - m(CAP_RING), head)
    # the cap ring itself: sooted steel, a little more on the lee
    soot(c, x - PAD, x + w + PAD, y + h - m(CAP_RING), y + h + PAD,
         lambda Y, X: 0.35 + 0.1 * np.cos(np.radians(head_angle(X) - LEE)))


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    BASE's V is height from the ground: soil and algae on the footing,
    splash and salt bloom on the brick above it. MID tiles in V, so it gets
    only noise on its 256-row period (tile_y = 4); its copies get the soot
    after (paint_soot). The head gets rain runs down from the cap ring.
    """
    brick = BRICK_IDS
    steel = (ID_GALV, ID_LADDER, ID_HATCH, ID_PLATE, ID_LAMP, ID_STEEL, ID_DECK, ID_CAP,
             ID_COPPER)
    w = weathering.Weather(c, clean=(ID_LENS,), steel=steel, tile_y=ATLAS // BAND_H)
    w.grime()
    w.fade((ID_HATCH, ID_LAMP))
    w.wash(brick)
    xb = m(4 * BH)
    w.plinth(-PAD, xb + PAD, PL_Y0, PL_Y0 + m(Z_FOOT), (ID_CONC,))
    w.splash(-PAD, xb + PAD, PL_Y0 + m(Z_FOOT), PL_Y0 + BASE_TOP_PX, brick)
    w.bloom(-PAD, xb + PAD, PL_Y0 + m(Z_FOOT), PL_Y0 + m(1.6), brick, amount=0.12,
            fade=m(0.8))
    # the front: soot and rust stains up from the inlet onto its lintel
    f0 = m(U_OFF["front"])
    s0, s1 = f0 + m(INLET[0] - INLET[2] / 2 - 0.15), f0 + m(INLET[0] + INLET[2] / 2 + 0.15)
    soot(c, s0, s1, m(Z_LINTEL[0]), PL_Y0 + BASE_TOP_PX,
         lambda Y, X: 0.35 * np.exp(-(Y - m(Z_LINTEL[0])) / 14.0)
         * (0.6 + 0.4 * np.cos(np.pi * (X - (s0 + s1) / 2) / (s1 - s0))))
    # MID: periodic noise only
    x0, y0, ov, sx, sw = BANDS["MID"]
    w.add("D", x0 - SHAFT_ML - PAD, x0 + SHAFT_P + ov + PAD, y0 - 4, y0 + BAND_H + 4,
          lambda Y, X, nz: 0.07 * nz("big"), brick)
    # the head: runs from under the cap ring
    x, y, hw, hh = HEAD_R
    w.runs(x - PAD, x + hw + PAD, y, y + hh - m(CAP_RING), (ID_HEADC,), 0.22,
           fall=40.0, noise="long")
    w.add("R", x - PAD, x + hw + PAD, y + hh - m(CAP_RING), y + hh + PAD,
          lambda Y, X, nz: 0.10 + 0.14 * nz("blotch"), (ID_CAP,))
    # the coping and the wash
    x, y, cw, ch = COPING_R
    w.add("D", x - PAD, x + cw + PAD, y - PAD, y + ch + PAD,
          lambda Y, X, nz: 0.14 + 0.10 * nz("blotch"), (ID_CONC,))
    x, y, rw, rh = WASH_R
    w.add("D", x - PAD, x + rw + PAD, y - PAD, y + rh + PAD,
          lambda Y, X, nz: 0.14 + 0.12 * nz("blotch"), (ID_CONC,))
    # the inlet and hatch
    x, y, rw, rh = INLET_R
    w.add("R", x - PAD, x + rw + PAD, y - PAD, y + rh + PAD,
          lambda Y, X, nz: 0.16 * nz("blotch"), (ID_PLATE,))
    w.runs(x, x + rw, y, y + rh, (ID_PLATE,), 0.10, fall=rh / 2)
    x, y, rw, rh = HATCH_R
    w.add("R", x - PAD, x + rw + PAD, y - PAD, y + 8,
          lambda Y, X, nz: 0.25 * nz("blotch"), (ID_HATCH, ID_PLATE))
    w.splash(x - PAD, x + rw + PAD, y - PAD, y + rh, (ID_HATCH,), amount=0.12)
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_base(c)
    paint_mid(c)
    x0, y0, ov, sx, sw = BANDS["MID"]
    c.check_bands({"MID": ((y0 - 4, y0 + BAND_H + 4), set(BRICK_IDS))})
    paint_coping(c)
    paint_wash(c)
    paint_head(c)
    paint_lamp(c)
    paint_inlet(c)
    paint_hatch(c)
    paint_patches(c)

    # Tone wear, grain and pores, on the bands' V period
    ty = ATLAS // BAND_H
    wear = 0.025 * atlas.noise(c, 3, 40.0, tile_y=ty) + 0.015 * atlas.noise(c, 4, 8.0, tile_y=ty)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, BRICK_IDS)
    streak = atlas.noise(c, 7, 0.8, 40.0, tile_y=ty)
    c.shade[walls] *= 1.0 + 0.03 * streak[walls]
    mineral = np.isin(c.mid, (ID_CONC, ID_HEADC, ID_MORTAR))
    pores = atlas.noise(c, 9, 0.8, tile_y=ty)
    c.shade[mineral] *= 1.0 + 0.03 * pores[mineral]
    c.height[mineral] += 0.0006 * pores[mineral]
    w = weather(c)
    tile_shaft(c, [c.mid, c.shade, c.ao, c.height] + list(w.f.values()))
    conductor_strips(c, [c.mid, c.shade, c.ao, c.height] + list(w.f.values()))
    paint_galv(c)
    paint_ladder(c)
    paint_soot(c)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    t[ID_BRICK] = pal["brick"]
    t[ID_BRICK2] = pal["brick2"]
    t[ID_MORTAR] = pal["mortar"]
    return t


# The lenses' emission colour. An obstruction lamp is red by definition, so
# unlike a window pane (neutral grey, its colour the consumer's) the mask is
# painted saturated red: the consumer's tint and intensity multiply a red
# source (notes.md, Night lighting).
LAMP_GLOW = (255, 26, 14)


def lamp_emission(c):
    """The emission map: the lamps' lenses and nothing else, each lens a
    soft bright core falling to about 0.6 at its rim, in LAMP_GLOW's red,
    blended in linear light."""
    cov = atlas.coverage(c, ID_LENS)
    Y, X = np.mgrid[0:ATLAS, 0:ATLAS].astype(np.float32) + 0.5
    x, y, w, h = LAMP_R
    yl = y + m(LAMP_Z[1] - LAMP_Z[0])
    cx, cy = x + w / 2.0, (yl + y + h) / 2.0
    glow = 0.6 + 0.4 * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (2 * 5.0 ** 2))
    near = (np.abs(X - cx) < w / 2 + 2 * PAD) & (Y > yl - 2) & (Y < y + h + 2 * PAD)
    v = np.where(near, cov * glow, 0.0)
    red = atlas.srgb_to_linear(np.array(LAMP_GLOW, np.float32))
    return atlas.linear_to_srgb(v[..., None] * red[None, None, :])


def export(out_dir, ss=atlas.SS):
    """Albedo per variant, one ORM, one normal map, one emission map."""
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.010)
    c.weather.dust(cav, BRICK_IDS)
    rough = 0.04 * atlas.noise(c, 13, 20.0, tile_y=ATLAS // BAND_H)
    tile_shaft(c, [rough])
    path = os.path.join(out_dir, ASSET)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_LENS,)), path + "_normal.png"),
               atlas.save(lamp_emission(c), path + "_emission.png")]
    for v in VARIANTS:
        rgb = atlas.albedo(c, lut(v), grime=0.25 * cav)
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
