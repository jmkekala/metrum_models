# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM and normal atlas, and the shared layout, for
savupiippu_brick_round.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
plan, heights, the stack's profile, side counts, band rows, region
rectangles -- so a change here cannot leave the UVs pointing at the wrong
artwork.

The stack is 45.5 m tall, and a 1024 atlas holds 16 m at 64 px/m, so the
shaft cannot have a band whose V is height from the ground. It is cut into
ten 4 m lifts instead, nine of which sample the same tiling band:

    y    0 ..  215   PLINTH  the square plinth's walls, z 0 .. 3.0 m, then its
                             sloped concrete coping; U walks round the four
                             walls and wraps
    y  224 ..  480   MID     the shaft, one 4 m lift of header-bond brick with
                             two steel tension bands, tiling in V (every noise
                             repeats on its 256 rows) and painted 4 rows into
                             its gutters with its own opposite end
    y  488 ..  999   TOPHEAD unique, 736 px wide: the shaft's top lift
                             (z 39.25 .. 43.25, soot thickening upward and rain
                             runs under the corbel), then the head with V
                             along its profile: three corbel steps, the head
                             band with the obstruction lamps, the crown
                             course, the cap and the rim
    x  744 .. 1020           the flue inlet's closure, the cleanout hatch,
                             the plinth's flat top (16 px/m) and flat patches

U round the shaft is chord length at 64 px/m, so every facet of every tier
shows bricks of their true size; the back facet (+Y), which carries the step
irons, samples a strip of its own at U 0 .. 112, and the other facets run on
from U 112 without wrapping. The one place the brick bond cannot run on --
where the circumference closes -- is therefore at the back facet's two
edges, under the ladder.

Rasterising is scripts/atlas.py's; dirt, algae, rust and faded paint are
scripts/weathering.py's fields, placed by weather() below. weathering.py has
no soot, so the soot at the head is this module's own shade and dirt (see
soot()).
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

# ------------------------------------------------------------------ plan
PH = 2.8                # the plinth: 5.6 x 5.6 m at its walls
Z_FOOT = 0.3125         # 20 px; cast concrete footing course
Z_PLINTH = 4.0          # 256 px; top of the plinth's brick walls
WASH_IN = 0.25          # the coping slopes 0.25 in and 0.25 up, at 45 degrees
Z_SHAFT0 = Z_PLINTH + WASH_IN        # 4.25: the coping's top, the shaft's foot
PH_TOP = PH - WASH_IN                # 2.55: the coping's flat top

# ------------------------------------------------------------------ shaft
SEG = 4.0               # one lift, 256 px: the MID band's V period
NSEG = 10
Z_HEAD0 = Z_SHAFT0 + SEG * NSEG      # 44.25: the shaft's top, the corbel's foot
R0, R1 = 2.10, 1.20     # outside radius at the foot and at the corbel


def r_shaft(z):
    """The shaft's outside radius at height *z*: a straight batter."""
    return R0 + (R1 - R0) * (z - Z_SHAFT0) / (Z_HEAD0 - Z_SHAFT0)


# The head, as (z, r) up its outside and in across the rim: three corbel
# steps of 0.08 out by 0.20 up, the 1.3 m head band, a crown course
# projecting 0.08, a cast concrete cap sloping in to the rim, the rim.
R_FLUE = 1.02
FLUE_DEPTH = 1.0
Z_TOP = 46.5
HEAD = [(44.25, 1.20), (44.25, 1.28), (44.45, 1.28), (44.45, 1.36),
        (44.65, 1.36), (44.65, 1.44), (45.95, 1.44), (45.95, 1.52),
        (46.30, 1.52), (Z_TOP, 1.30), (Z_TOP, R_FLUE)]
# The simplified head of the far tiers: the corbel as one flare from the
# shaft's top to the head band; the rest unchanged.
HEAD_FLARE = [0, 5, 6, 7, 8, 9, 10]

# Sides of the round, per tier. Vertices stand at r * k(n) so that the
# polygon's mean of apothem and corner radius is the true radius, and the
# shaft keeps its apparent width as the side count drops.
SIDES = (24, 16, 12, 8)


def k_sides(n):
    return 2.0 / (1.0 + math.cos(math.pi / n))


# ------------------------------------------------------------------ plinth
# The four walls are walked counter-clockwise from above; U along each runs
# on round the corners from the east wall, so the bond turns three corners
# unbroken and the front's own range (the inlet's lintel and soot) is used by
# no other wall. The one break is the front's west corner.
U_OFF = {"east": 0.0, "rear": 5.6, "front": 10.4, "west": 0.0}

# The flue inlet, on the front (-Y), toward the hall: a closed opening in
# the plinth under a cast concrete lintel. The cleanout hatch: low on the
# east wall. (centre along the wall from its p0, sill z, width, height)
INLET = (PH, 1.0, 1.625, 2.0)
INLET_REVEAL = 0.25
Z_LINTEL = (3.0, 3.25)                  # its lintel, painted on the front
LINTEL_HALF = 1.0625                    # half the lintel's length
HATCH = (PH, 0.4375, 0.703125, 0.90625)

# ------------------------------------------------------------------ bands
PL_Y0 = 0
PL_WALL_PX = Z_PLINTH * PPM                         # 192
WASH_SLANT = WASH_IN * math.sqrt(2.0)               # the coping's slope, m
PL_TOP_PX = PL_WALL_PX + WASH_SLANT * PPM           # 214.6
MID_Y0, MID_H = 288, 256
TH_Y0, TH_W = 552, 736
TH_SHAFT_Z0 = Z_HEAD0 - SEG                         # 39.25: the top lift's foot
STRIP_W, STRIP_C = 112, 56.0                        # the back facet's strip


def head_v(profile=HEAD):
    """Atlas row of every head point: V runs on from the top lift's head at
    64 px per metre of profile, so steps, undersides and slopes each get
    their true size."""
    v = [TH_Y0 + SEG * PPM]
    for (z0, r0), (z1, r1) in zip(profile, profile[1:]):
        v.append(v[-1] + math.hypot(z1 - z0, r1 - r0) * PPM)
    return v


HEAD_V = head_v()
TH_TOP = HEAD_V[-1]

# ------------------------------------------------------------ unique regions
RC_X = 744
INLET_R = (752, 552, 104, 128)          # 1.625 x 2.0 m
HATCH_R = (868, 552, 45, 58)            # 0.703 x 0.906 m
PLTOP_PPM = 16.0                        # the plinth's flat top, seen from above
PLTOP_R = (924, 552, 84, 84)            # 5.25 x 5.25 m at 16 px/m
PATCH_NAMES = ("blank", "soot", "conc", "under")
PATCHES = {n: (752 + 20 * i, 700, 16, 16) for i, n in enumerate(PATCH_NAMES)}

# ------------------------------------------------------------------ brick
# Finnish brick, 285 x 135 x 85 mm with 10 mm joints. The shaft is radial
# brick in header bond; the plinth is stretcher bond. 43 courses to a lift,
# so the bond and its tone repeat exactly with MID's period.
COURSES = 43
COURSE = SEG / COURSES                  # 0.0930 m, 5.95 px
HEADER_N, STRETCH_N = 108, 54           # bricks across the atlas width
TENSION = (1.0, 3.0)                    # tension bands, metres into each lift
TENSION_H = 0.078125                    # 5 px of steel flat
IRONS = 12                              # step irons to a lift: 0.333 m pitch
IRON_HALF = 0.15                        # half a rung's width
CONDUCTOR_U = STRIP_W + 20.0            # down conductor, beside the back facet
IRONS_FROM = 2.5                        # the lowest step iron, on the plinth
CONDUCTOR_W = 1.8                       # px: 28 mm copper tape

# ----------------------------------------------------------- material ids
ID_BLANK, ID_CONC, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_STEEL, ID_IRON, ID_CU, ID_HATCH, ID_PLATE = 5, 6, 7, 8, 9
ID_SOOT, ID_CAP, ID_LAMP, ID_LENS, ID_DARK = 10, 11, 12, 13, 14

SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_CONC: (0.90, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.80, 0.0), ID_MORTAR: (0.94, 0.0), ID_STEEL: (0.62, 0.0),
    ID_IRON: (0.55, 0.35), ID_CU: (0.50, 0.45), ID_HATCH: (0.58, 0.0),
    ID_PLATE: (0.74, 0.10), ID_SOOT: (0.97, 0.0), ID_CAP: (0.92, 0.0),
    ID_LAMP: (0.45, 0.0), ID_LENS: (0.18, 0.0), ID_DARK: (0.96, 0.0),
}

# One brick per instance, the same three as the catalog's brick industrial
# buildings, so the stack matches its hall.
VARIANTS = {
    "red_brick": {"brick": (144, 72, 52), "brick2": (114, 58, 45),
                  "mortar": (150, 145, 136)},
    "yellow_brick": {"brick": (188, 166, 122), "brick2": (164, 142, 104),
                     "mortar": (160, 156, 148)},
    "brown_brick": {"brick": (98, 68, 54), "brick2": (78, 54, 44),
                    "mortar": (124, 118, 110)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_BLANK: (52, 52, 52), ID_CONC: (156, 154, 147), ID_STEEL: (50, 50, 52),
    ID_IRON: (112, 112, 108), ID_CU: (92, 70, 54), ID_HATCH: (58, 66, 62),
    ID_PLATE: (44, 43, 42), ID_SOOT: (22, 21, 20), ID_CAP: (120, 118, 113),
    ID_LAMP: (124, 126, 128), ID_LENS: (104, 34, 30), ID_DARK: (24, 24, 24),
}

BAND_IDS = {
    "PLINTH": ((0, 281), {ID_CONC, ID_BRICK, ID_BRICK2, ID_MORTAR, ID_CU, ID_IRON,
                          ID_STEEL}),
    "MID": ((284, 548), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_STEEL, ID_IRON,
                         ID_CU}),
}

# ---------------------------------------------------------------- relief
BRICK_FACE = 0.006      # brick proud of the recessed joint
BAND_RELIEF = 0.010     # the tension bands' steel flat
IRON_RELIEF = 0.030     # the step irons (they stand ~0.12 m off; kept shallow)
CU_RELIEF = 0.003
LAMP_RELIEF = 0.060


def m(v):
    return v * PPM


# ================================================================== brick
def paint_brick(c, x0, x1, y0, y1, y_ref, n_across, ids=None):
    """Brick over rows y0..y1, courses counted from row *y_ref*, *n_across*
    bricks per atlas width, alternate courses offset by half a brick. Tone
    repeats every COURSES courses and every atlas width, so a band painted
    with it tiles in both directions."""
    course = m(COURSE)
    blen = ATLAS / n_across
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    r = np.floor((Y - y_ref) / course).astype(np.int64)
    off = (r % 2) * blen * 0.5
    b = np.floor((X - off) / blen).astype(np.int64) % n_across
    rr = r % COURSES
    bed = (Y - y_ref - r * course) < 1.0
    perp = ((X - off) % blen) < 1.0
    joint = bed | perp
    tone = 0.88 + 0.22 * atlas.hash_unit(b, rr, 17 + n_across)
    dark = atlas.hash_unit(b, rr, 29 + n_across) < 0.16
    mid = np.where(joint, ID_MORTAR, np.where(dark, ID_BRICK2, ID_BRICK))
    if ids is not None:
        keep = ~np.isin(c.mid[sy, sx], ids)
        mid = np.where(keep, c.mid[sy, sx], mid)
    c.mid[sy, sx] = mid
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


def paint_tension(c, x0, x1, y0, y1, ref):
    """Steel flats round the shaft at TENSION metres into every lift: a
    raised band with lit arrises in height, occlusion along both edges."""
    h = m(TENSION_H)
    for yb in _period_rows(y0, y1, ref, m(SEG), [m(t) for t in TENSION]):
        a, b = max(yb, y0), min(yb + h, y1)
        if b <= a:
            continue
        c.paint(x0, x1, a, b, ID_STEEL, 1.0, 1.0)
        c.bevel(x0, x1, yb, yb + h, BAND_RELIEF, 1.0, axes="y")
        c.mul(x0, x1, max(yb - 1.5, y0), max(yb, y0), 0.86, ao=0.80)
        c.mul(x0, x1, min(yb + h, y1), min(yb + h + 1, y1), 0.94, ao=0.90)
        # the band's tensioner: a bolted lug beside the ladder
        lx = STRIP_C + m(IRON_HALF) + 6
        c.paint(lx, lx + 7, max(yb - 1, y0), min(yb + h + 1, y1), ID_STEEL, 0.9, 0.9,
                height=BAND_RELIEF * 2.2)


def paint_irons(c, y0, y1, ref, x_c=STRIP_C):
    """Galvanised step irons up the back, one every SEG / IRONS: a rung on two
    legs, with occlusion under it where its legs enter the joint."""
    hw = m(IRON_HALF)
    pitch = m(SEG) / IRONS
    for yi in _period_rows(y0, y1, ref, pitch, [pitch * 0.5]):
        if not (y0 <= yi < y1 - 2):
            continue
        c.paint(x_c - hw, x_c + hw, yi, yi + 1.6, ID_IRON, 1.0, 0.95,
                height=IRON_RELIEF)
        c.bevel(x_c - hw, x_c + hw, yi, yi + 1.6, IRON_RELIEF, 0.8, axes="y")
        for lx in (x_c - hw, x_c + hw - 1.5):
            c.paint(lx, lx + 1.5, yi - 3.0, yi + 1.6, ID_IRON, 0.85, 0.9,
                    height=IRON_RELIEF * 0.7)
        c.mul(x_c - hw, x_c + hw, yi - 1.2, yi, 0.90, ao=0.80)


def paint_conductor(c, x, y0, y1):
    """The copper tape down conductor, with a fixing clip every metre."""
    c.paint(x, x + CONDUCTOR_W, y0, y1, ID_CU, 1.0, 0.95, height=CU_RELIEF)
    for yy in np.arange(math.ceil(y0 / PPM) * PPM, y1, PPM):
        c.paint(x - 1.0, x + CONDUCTOR_W + 1.0, yy, yy + 1.5, ID_CU, 0.82, 0.9,
                height=CU_RELIEF * 2)


# ================================================================ the plinth
def paint_plinth(c):
    """The plinth band: a cast concrete footing course, stretcher-bond brick
    to the wall head, and the sloped concrete coping above it, the drip line
    shadowed. The front's own range carries the inlet's lintel; the rear's
    the earthing end of the down conductor."""
    y0 = PL_Y0
    top = PL_TOP_PX
    paint_brick(c, 0, ATLAS, y0 + m(Z_FOOT), y0 + PL_WALL_PX, y0 + m(Z_FOOT), STRETCH_N)
    # footing
    c.paint(0, ATLAS, y0 - PAD, y0 + m(Z_FOOT), ID_CONC, 1.0, 1.0, height=0.0)
    c.mul(0, ATLAS, y0 + m(Z_FOOT) - 1.5, y0 + m(Z_FOOT), 0.88, ao=0.85)
    c.lift(0, ATLAS, y0 + m(Z_FOOT) - 1.0, y0 + m(Z_FOOT), 0.004)
    # coping: trowelled concrete, the arris at its foot, a drip shadow
    c.paint(0, ATLAS, y0 + PL_WALL_PX, top + PAD, ID_CONC, 0.97, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 + PL_WALL_PX, y0 + PL_WALL_PX + 2, ID_CONC, 1.02, 1.0,
            height=0.006)
    c.mul(0, ATLAS, y0 + PL_WALL_PX - 2.5, y0 + PL_WALL_PX, 0.84, ao=0.80)
    # the inlet's cast concrete lintel, on the front only
    s0 = U_OFF["front"] * PPM + m(INLET[0] - LINTEL_HALF)
    s1 = U_OFF["front"] * PPM + m(INLET[0] + LINTEL_HALF)
    l0, l1 = y0 + m(Z_LINTEL[0]), y0 + m(Z_LINTEL[1])
    c.paint(s0, s1, l0, l1, ID_CONC, 0.95, 1.0)
    c.bevel(s0, s1, l0, l1, 0.008, 1.0)
    c.mul(s0, s1, l0 - 1.5, l0, 0.86, ao=0.82)
    # the rear: the down conductor coming off the coping to a test clamp and
    # into the ground
    cu = U_OFF["rear"] * PPM + m(CONDUCTOR_S)
    paint_conductor(c, cu, y0 - PAD, top + PAD)
    # the step irons start out of reach, 2.5 m up the rear wall, under the
    # back facet's centre, and run up to the coping
    xi = U_OFF["rear"] * PPM + m(PH)
    paint_irons(c, y0 + m(IRONS_FROM), y0 + PL_WALL_PX - 4, y0 + m(Z_SHAFT0), x_c=xi)
    c.paint(cu - 4, cu + CONDUCTOR_W + 4, y0 + m(1.5), y0 + m(1.5) + 8, ID_STEEL,
            0.95, 0.9, height=0.02)
    c.mul(cu - 4, cu + CONDUCTOR_W + 4, y0 + m(1.5) - 1.5, y0 + m(1.5), 0.86, ao=0.8)


def _conductor_s():
    """Where the shaft's down conductor reaches the plinth: just west of the
    back facet (LOD0), measured along the rear wall from its east end."""
    n = SIDES[0]
    rv = R0 * k_sides(n)
    w = 2.0 * rv * math.sin(math.pi / n)
    a1 = math.pi / 2 + math.pi / n                 # the back facet's west corner
    a2 = a1 + 2.0 * math.pi / n
    t = (CONDUCTOR_U - STRIP_W) / PPM / w
    x = rv * ((1 - t) * math.cos(a1) + t * math.cos(a2))
    return PH - x                                   # rear wall runs from x = +PH


CONDUCTOR_S = _conductor_s()


# ================================================================ the shaft
def paint_mid(c):
    """One 4 m lift of the shaft, tiling in U and V: header bond, two steel
    tension bands, the step irons and the down conductor on the back strip,
    painted PAD+2 rows into both gutters from the formula itself, so the
    gutters carry the band's opposite end."""
    y0, y1 = MID_Y0 - 4, MID_Y0 + MID_H + 4
    paint_brick(c, 0, ATLAS, y0, y1, MID_Y0, HEADER_N)
    paint_tension(c, 0, ATLAS, y0, y1, MID_Y0)
    paint_irons(c, y0, y1, MID_Y0)
    paint_conductor(c, CONDUCTOR_U, y0, y1)


def paint_tophead(c):
    """The top lift and the head, unique: brick, bands, irons and conductor
    on the same phase as MID below the corbel; then the corbel steps with
    their dark undersides, the head band with a steel band at each edge, a
    recessed course of dark headers and four obstruction lamps, the crown in
    soldier course, and the cap and rim in cast concrete. The flue's lining
    and floor take the soot patch."""
    x0, x1 = 0, TH_W
    v = HEAD_V
    paint_brick(c, x0 - PAD, x1 + PAD, TH_Y0 - PAD, v[8], TH_Y0, HEADER_N)
    paint_tension(c, x0 - PAD, x1 + PAD, TH_Y0 - PAD, v[0], TH_Y0)
    # corbel undersides: brick soffits in their own shadow
    for a, b in ((0, 1), (2, 3), (4, 5), (6, 7)):
        c.mul(x0 - PAD, x1 + PAD, v[a], v[b], 0.62, ao=0.55)
        c.mul(x0 - PAD, x1 + PAD, v[b] - 1.0, v[b], 0.85)
    # the head band: a steel band at its foot and head, and between them a
    # sunk course of dark burnt headers, the stack's only ornament
    hb0, hb1 = v[5], v[6]
    for yb in (hb0 + 3, hb1 - 3 - m(TENSION_H)):
        c.paint(x0 - PAD, x1 + PAD, yb, yb + m(TENSION_H), ID_STEEL, 1.0, 1.0)
        c.bevel(x0 - PAD, x1 + PAD, yb, yb + m(TENSION_H), BAND_RELIEF, 1.0, axes="y")
    p0, p1 = hb0 + m(0.45), hb0 + m(0.45) + 3 * m(COURSE)
    sy, sx = c.sl(x0 - PAD, x1 + PAD, p0, p1)
    brick = np.isin(c.mid[sy, sx], (ID_BRICK, ID_BRICK2))
    c.mid[sy, sx] = np.where(brick, ID_BRICK2, c.mid[sy, sx])
    c.shade[sy, sx] *= np.where(brick, 0.80, 1.0)
    c.height[sy, sx] -= 0.012
    c.mul(x0 - PAD, x1 + PAD, p1 - 1.5, p1, 0.84, ao=0.78)
    # crown: soldier course, bricks on end
    cr0, cr1 = v[7], v[8]
    sy, sx, Y, X = c.field(x0 - PAD, x1 + PAD, cr0, cr1)
    w = m(COURSE)
    b = np.floor(X / w).astype(np.int64)
    joint = ((X % w) < 1.0) | ((Y - cr0) < 1.0) | ((cr1 - Y) < 1.0)
    tone = 0.86 + 0.2 * atlas.hash_unit(b, 3, 41)
    c.mid[sy, sx] = np.where(joint, ID_MORTAR, ID_BRICK)
    c.shade[sy, sx] = np.where(joint, 0.92, tone)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)
    c.ao[sy, sx] = np.where(joint, 0.82, 1.0)
    # cap and rim: cast concrete, an arris where the slope meets the rim
    c.paint(x0 - PAD, x1 + PAD, v[8], v[10] + PAD, ID_CAP, 1.0, 1.0, height=0.0)
    c.mul(x0 - PAD, x1 + PAD, v[8], v[8] + 1.5, 0.82, ao=0.8)
    c.paint(x0 - PAD, x1 + PAD, v[9] - 1, v[9] + 1, ID_CAP, 1.05, 1.0, height=0.004)
    # the rim's inner edge, where it turns down into the flue
    c.mul(x0 - PAD, x1 + PAD, v[10] - 3, v[10] + PAD, 0.70, ao=0.75)
    # irons up the shaft's top lift, the corbel's faces, the band and crown
    for a, b in ((TH_Y0 - PAD, v[0]), (v[1], v[2]), (v[3], v[4]), (v[5], v[6]),
                 (v[7], v[8])):
        paint_irons(c, a, b, TH_Y0)
    # a hand grip over the cap: the irons' last rung, at the rim
    c.paint(STRIP_C - m(IRON_HALF), STRIP_C + m(IRON_HALF), v[8] + 3, v[8] + 5,
            ID_IRON, 1.0, 0.95, height=IRON_RELIEF)
    paint_conductor(c, CONDUCTOR_U, TH_Y0 - PAD, v[9])
    paint_lamps(c)


# The obstruction lamps' U on the head band, from LOD0's mapping: west, front
# and east of the stack, the back being the ladder's.
def lamp_u(angle_from_back):
    n = SIDES[0]
    w = 2.0 * HEAD[5][1] * k_sides(n) * math.sin(math.pi / n)
    j = angle_from_back / (2.0 * math.pi / n)       # facets from the back's centre
    return STRIP_W + (j - 0.5) * w * PPM


LAMP_U = [lamp_u(math.radians(a)) for a in (90.0, 180.0, 270.0)]
LAMP_Z = 0.80                                       # metres up the head band


def paint_lamps(c):
    """Three aviation obstruction lamps on the head band: a grey housing on a
    bracket, a dark red lens dome. Painted, unlit (notes.md, Night
    lighting)."""
    y = HEAD_V[5] + m(LAMP_Z)
    for u in LAMP_U:
        c.paint(u - 4, u + 4, y - 7, y - 4, ID_LAMP, 0.85, 0.9, height=LAMP_RELIEF * 0.5)
        c.mul(u - 4, u + 4, y - 9, y - 7, 0.80, ao=0.75)
        c.rounded_rect(u - 5, y - 4, 10, 6, 1.5, ID_LAMP, 1.0, 0.95,
                       height=LAMP_RELIEF)
        c.disc(u, y + 4, 4.2, ID_LENS, 1.0, 0.95, height=LAMP_RELIEF * 1.2)
        c.paint(u - 4.5, u + 4.5, y + 1.5, y + 2.5, ID_LAMP, 0.9, 0.9)


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
    # the two sheets' joint and the mid stiffener
    c.paint(x + w / 2 - 0.5, x + w / 2 + 0.5, y + F, y + h - F, ID_DARK, 1.0, 0.7,
            height=-0.002)
    ym = y + h * 0.55
    c.paint(x + F, x + w - F, ym, ym + 4, ID_PLATE, 1.1, 0.95, height=0.03)
    c.bevel(x + F, x + w - F, ym, ym + 4, 0.03, 1.0, axes="y")
    c.mul(x + F, x + w - F, ym - 2, ym, 0.84, ao=0.8)
    # bolt heads round the frame
    for bx in np.arange(x + 2.5, x + w - 1, 8.0):
        for by in (y + 2.5, y + h - 2.5):
            c.disc(bx, by, 1.1, ID_PLATE, 1.15, 0.9, height=0.035)
    for by in np.arange(y + 2.5, y + h - 1, 8.0):
        for bx in (x + 2.5, x + w - 2.5):
            c.disc(bx, by, 1.1, ID_PLATE, 1.15, 0.9, height=0.035)
    # an inspection door low in the plate
    dx0, dx1, dy0, dy1 = x + w / 2 - 20, x + w / 2 + 20, y + 14, y + 44
    c.paint(dx0, dx1, dy0, dy1, ID_PLATE, 1.05, 0.95, height=0.02)
    c.bevel(dx0, dx1, dy0, dy1, 0.02, 1.0)
    c.mul(dx0, dx1, dy0 - 2, dy0, 0.82, ao=0.8)
    c.paint(dx1 - 7, dx1 - 3, dy0 + 10, dy0 + 20, ID_IRON, 0.8, 0.9, height=0.03)


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
    c.paint(x + w - F - 6, x + w - F - 2, y + h / 2 - 6, y + h / 2 + 6, ID_IRON,
            0.85, 0.9, height=0.03)


def paint_pltop(c):
    """The plinth's flat top round the shaft, at 16 px/m: trowelled
    concrete, a darker ring of soot fallout and wet near the shaft."""
    x, y, w, h = PLTOP_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CONC, 0.95, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    r = np.hypot(X - (x + w / 2), Y - (y + h / 2)) / PLTOP_PPM
    c.shade[sy, sx] *= 0.78 + 0.22 * np.clip((r - R0) / 0.25, 0.0, 1.0)
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.7 + 0.3 * np.clip((r - R0) / 0.15, 0, 1))


def paint_patches(c):
    spec = {"blank": (ID_BLANK, 1.0, 1.0), "soot": (ID_SOOT, 0.9, 0.5),
            "conc": (ID_CONC, 0.92, 0.9), "under": (ID_BRICK2, 0.6, 0.6)}
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x - 2, x + w + 2, y - 2, y + h + 2, mid, sh, ao, height=0.0)


# ------------------------------------------------------------------ checks
def check_regions():
    rects = {"inlet": INLET_R, "hatch": HATCH_R, "pltop": PLTOP_R}
    rects.update(PATCHES)
    problems = []
    names = sorted(rects)
    for i, a in enumerate(names):
        ax, ay, aw, ah = rects[a]
        if ax - 2 < RC_X or ay - 2 < TH_Y0 - 2 or ax + aw + 2 > ATLAS or ay + ah + 2 > ATLAS:
            problems.append("%s runs out of the right-hand column" % a)
        for b in names[i + 1:]:
            bx, by, bw, bh = rects[b]
            if (ax - 4 < bx + bw and bx - 4 < ax + aw
                    and ay - 4 < by + bh and by - 4 < ay + ah):
                problems.append("%s and %s overlap" % (a, b))
    if abs(INLET_R[2] / PPM - INLET[2]) > 0.02 or abs(INLET_R[3] / PPM - INLET[3]) > 0.02:
        problems.append("the inlet region does not match the opening")
    if abs(HATCH_R[2] / PPM - HATCH[2]) > 0.02 or abs(HATCH_R[3] / PPM - HATCH[3]) > 0.02:
        problems.append("the hatch region does not match the hatch")
    if PLTOP_R[2] < 2 * PH_TOP * PLTOP_PPM:
        problems.append("the plinth-top region is too small")
    if PL_TOP_PX + PAD + 2 > MID_Y0 - 4:
        problems.append("PLINTH runs into MID's gutter")
    if MID_Y0 + MID_H + 4 > TH_Y0 - PAD:
        problems.append("MID runs into TOPHEAD")
    if TH_TOP + PAD > ATLAS:
        problems.append("TOPHEAD runs off the atlas at row %.1f" % TH_TOP)
    if TH_W > RC_X - 4:
        problems.append("TOPHEAD runs into the right-hand column")
    if (ATLAS // MID_H) * MID_H != ATLAS:
        problems.append("MID's period does not divide the atlas: noise cannot tile")
    if abs(m(SEG) - MID_H) > 1e-6:
        problems.append("a lift is not MID's height")
    if abs(TH_SHAFT_Z0 - Z_SHAFT0 - SEG * (NSEG - 1)) > 1e-9:
        problems.append("the top lift is not on the lifts' phase")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def soot(c, x0, x1, y0, y1, fn):
    """Soot staining, which scripts/weathering.py has no field for: shade
    darkened and pulled toward its dirt by fn(Y) in 0..1, per sample. Soot
    on a stack is the flue gas's, so it thickens toward the head."""
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    s = fn(Y, X)
    c.shade[sy, sx] *= 1.0 - 0.70 * s
    c.weather.f["D"][sy, sx] += 0.45 * s


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    PLINTH's V is height from the ground: soil and algae on the footing,
    splash and salt bloom on the brick above it, dirt on the coping. MID
    tiles in V, so it gets only noise on its 256-row period (tile_y = 4).
    TOPHEAD's V is height up the stack and then along the head's profile,
    so the soot thickening toward the head and the rain runs from under the
    corbel go there.
    """
    brick = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    steel = (ID_STEEL, ID_IRON, ID_CU, ID_HATCH, ID_PLATE, ID_LAMP)
    w = weathering.Weather(c, clean=(ID_LENS,), steel=steel, tile_y=ATLAS // MID_H)
    w.grime()
    w.fade((ID_HATCH, ID_LAMP, ID_STEEL))
    w.wash(brick)
    # the plinth
    w.plinth(0, ATLAS, PL_Y0, PL_Y0 + m(Z_FOOT), (ID_CONC,))
    w.splash(0, ATLAS, PL_Y0 + m(Z_FOOT), PL_Y0 + PL_WALL_PX, brick + (ID_CU,))
    w.bloom(0, ATLAS, PL_Y0 + m(Z_FOOT), PL_Y0 + m(1.6), brick, amount=0.12,
            fade=m(0.8))
    w.add("D", 0, ATLAS, PL_Y0 + PL_WALL_PX, PL_TOP_PX + PAD,
          lambda Y, X, nz: 0.14 + 0.10 * nz("blotch"), (ID_CONC,))
    w.runs(0, ATLAS, PL_Y0 + PL_WALL_PX - m(0.8), PL_Y0 + PL_WALL_PX, brick, 0.10,
           fall=20.0)
    # the front: soot and rust stains up from the inlet onto the lintel
    f0 = U_OFF["front"] * PPM
    s0, s1 = f0 + m(INLET[0] - INLET[2] / 2 - 0.15), f0 + m(INLET[0] + INLET[2] / 2 + 0.15)
    soot(c, s0, s1, m(Z_LINTEL[0]), PL_Y0 + PL_WALL_PX,
         lambda Y, X: 0.35 * np.exp(-(Y - m(Z_LINTEL[0])) / 14.0)
         * (0.6 + 0.4 * np.cos(np.pi * (X - (s0 + s1) / 2) / (s1 - s0))))
    w.add("R", 0, ATLAS, PL_Y0 + m(1.5) - 2, PL_Y0 + m(1.5) + 10,
          lambda Y, X, nz: 0.2 * nz("blotch"), (ID_STEEL,))
    # MID: periodic noise only -- soot specks, rust runs under the bands and
    # the irons, a little rust on the steel
    w.add("D", 0, ATLAS, MID_Y0 - 4, MID_Y0 + MID_H + 4,
          lambda Y, X, nz: 0.08 * nz("big"), brick)
    for t in TENSION:
        yb = MID_Y0 + m(t)
        w.add("R", 0, ATLAS, yb - 18, yb, lambda Y, X, nz, yb=yb: 0.10 * atlas.smoothstep(
            0.4, 1.6, nz("runs")) * np.exp(-(yb - Y) / 8.0), brick)
    w.add("R", 0, ATLAS, MID_Y0 - 4, MID_Y0 + MID_H + 4,
          lambda Y, X, nz: 0.10 + 0.15 * nz("blotch"), (ID_STEEL, ID_IRON))
    # TOPHEAD: the same noise below; soot thickening up the top lift and the
    # head, heaviest at the crown and on the cap; rain runs under the corbel
    v = HEAD_V
    w.add("D", 0, TH_W, TH_Y0 - PAD, v[0], lambda Y, X, nz: 0.08 * nz("big"), brick)
    w.add("R", 0, TH_W, TH_Y0 - PAD, v[9],
          lambda Y, X, nz: 0.10 + 0.15 * nz("blotch"), (ID_STEEL, ID_IRON))
    soot(c, -PAD, TH_W + PAD, TH_Y0, v[0],
         lambda Y, X: 0.30 * ((Y - TH_Y0) / (v[0] - TH_Y0)) ** 2
         * (0.8 + 0.2 * atlas.noise(c, 21, 6.0, 40.0)[c.sl(-PAD, TH_W + PAD, TH_Y0, v[0])]))
    soot(c, -PAD, TH_W + PAD, v[0], v[8],
         lambda Y, X: 0.30 + 0.40 * np.clip((Y - v[0]) / (v[8] - v[0]), 0, 1))
    soot(c, -PAD, TH_W + PAD, v[8], v[10] + PAD,
         lambda Y, X: 0.85 + 0.25 * np.clip((Y - v[8]) / (v[10] - v[8]), 0, 1))
    w.runs(0, TH_W, v[0] - m(1.6), v[0], brick, 0.22, fall=40.0, noise="long")
    w.runs(0, TH_W, v[5] - 2, v[6], brick, 0.12, fall=30.0)
    # the regions
    x, y, rw, rh = INLET_R
    w.add("R", x - PAD, x + rw + PAD, y - PAD, y + rh + PAD,
          lambda Y, X, nz: 0.16 * nz("blotch"), (ID_PLATE,))
    w.runs(x, x + rw, y, y + rh, (ID_PLATE,), 0.10, fall=rh / 2)
    x, y, rw, rh = HATCH_R
    w.add("R", x - PAD, x + rw + PAD, y - PAD, y + 8,
          lambda Y, X, nz: 0.25 * nz("blotch"), (ID_HATCH, ID_PLATE))
    w.splash(x - PAD, x + rw + PAD, y - PAD, y + rh, (ID_HATCH,), amount=0.12)
    x, y, rw, rh = PLTOP_R
    w.add("D", x - PAD, x + rw + PAD, y - PAD, y + rh + PAD,
          lambda Y, X, nz: 0.12 + 0.12 * nz("blotch"), (ID_CONC,))
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_plinth(c)
    paint_mid(c)
    c.check_bands(BAND_IDS)
    paint_tophead(c)
    paint_inlet(c)
    paint_hatch(c)
    paint_pltop(c)
    paint_patches(c)

    # Tone wear, grain and pores, on MID's period so the band tiles
    ty = ATLAS // MID_H
    wear = 0.025 * atlas.noise(c, 3, 40.0, tile_y=ty) + 0.015 * atlas.noise(c, 4, 8.0, tile_y=ty)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR))
    streak = atlas.noise(c, 7, 0.8, 40.0, tile_y=ty)
    c.shade[walls] *= 1.0 + 0.03 * streak[walls]
    mineral = np.isin(c.mid, (ID_CONC, ID_CAP, ID_MORTAR))
    pores = atlas.noise(c, 9, 0.8, tile_y=ty)
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
    t[ID_BRICK] = pal["brick"]
    t[ID_BRICK2] = pal["brick2"]
    t[ID_MORTAR] = pal["mortar"]
    return t


def export(out_dir, ss=atlas.SS):
    """Albedo per variant, one ORM and one normal map. No emission map: the
    stack has no glazing, and its obstruction lamps are painted unlit."""
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.010)
    c.weather.dust(cav, (ID_BRICK, ID_BRICK2, ID_MORTAR))
    rough = 0.04 * atlas.noise(c, 13, 20.0, tile_y=ATLAS // MID_H)
    path = os.path.join(out_dir, ASSET)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_LENS,)), path + "_normal.png")]
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
