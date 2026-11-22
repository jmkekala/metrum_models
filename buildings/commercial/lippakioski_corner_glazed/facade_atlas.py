# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
lippakioski_corner_glazed.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
the plan, the heights, the glazing band's pane rhythm, the region rectangles
-- so a change here cannot leave the UVs pointing at the wrong artwork.

A Helsinki-type straight-front canopy kiosk: a 4.8 x 3.4 m box of narrow
vertical ribbed boarding on a low concrete plinth, its front-right corner
rounded, under a thin flat canopy slab with rounded plan corners that
projects far over the front and the serving side. The atlas holds two tiling
bands and a set of unique regions:

    wall band     rows 0-192, z 0-3.0 m: plinth, ribbed boarding, the shadow
                  line under the soffit. U runs round the wall outline.
    fascia band   rows 198-217, the canopy's 0.30 m edge: ribs in the wall
                  colour, a galvanised edge flashing along the top.
    regions       the soffit and the roof deck (plan-mapped), the glazing
                  band, the doors, the posters, the shutter stack's front
                  and side, the rack, the bench, the wall lamp's face and
                  the sign board's face.

Rasterising is scripts/atlas.py's (supersampled canvas, height channel for
the normal map); weathering is scripts/weathering.py's; the panes are
scripts/glazing.py's rooms() by day and night_rooms() by night, with the
kiosk's goods on their shelves painted into the room afterwards (albedo
only).

Density is 64 texels/metre everywhere a person looks, except the sign
board's face at 128 (its lettering) and the roof deck at 32, seen only from
above.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import glazing  # noqa: E402
import lettering  # noqa: E402
import weathering  # noqa: E402

ASSET = "lippakioski_corner_glazed"
ATLAS = 1024
PPM = 64.0
SIGN_PPM = 128.0
DECK_PPM = 32.0
PAD = 2

# ================================================================== plan
# Build frame: Z up, front toward -Y. The walls are a 4.8 x 3.4 m box with
# the front-right (serving) corner rounded at R_WALL.
WX0, WX1 = -2.4, 2.4
WY0, WY1 = -1.7, 1.7
R_WALL = 0.6
WALL_C = (WX1 - R_WALL, WY0 + R_WALL)          # (1.8, -1.1), the corner's centre
WALL_FACETS = (4, 4, 2, 1)                     # per tier, round the corner

# The canopy ("lippa"): far out over the front and the serving side, a
# hand's breadth at the rear and the left.
OUT_FRONT, OUT_RIGHT, OUT_REAR, OUT_LEFT = 1.6, 1.6, 0.35, 0.35
CX0, CX1 = WX0 - OUT_LEFT, WX1 + OUT_RIGHT     # -2.75, 4.0
CY0, CY1 = WY0 - OUT_FRONT, WY1 + OUT_REAR     # -3.3, 2.05
# plan corner radii: front-right, rear-right, rear-left, front-left
R_CANOPY = {"fr": 0.8, "rr": 0.8, "rl": 0.3, "fl": 0.8}
CANOPY_SEGS = {"big": (6, 4, 2, 2), "small": (3, 2, 1, 1)}
RIM = 0.08                                     # the flashing round the hidden deck

# ================================================================ heights
Z_PLINTH = 0.15          # cast concrete under the boarding
Z_COUNTER = 1.05         # the glazing band's sill, the serving counter
Z_LEAF = 2.10            # the customer door's leaf; the band's transom bar
Z_BAR = 2.16             # top of the transom bar
Z_MID = 2.17             # staff door casing top, poster frames' top
Z_HEAD = 2.84            # head of the glazing band and the customer door
Z_SOFFIT = 2.85          # the canopy's underside
Z_BODY = 3.00            # the wall solid's top, buried in the canopy
Z_DECK = 3.09            # the felt deck behind the fascia
Z_TOP = 3.15             # the fascia's top: the canopy is 0.30 m thick
WALL_Z = (0.0, Z_COUNTER, Z_MID, Z_HEAD, Z_BODY)   # every wall shares these rows

# =========================================================== glazing band
# From x BAND_X0 along the front, round the corner, to y BAND_Y1 on the
# serving side. s is measured along the band, LOD0's corner facets as chords.
BAND_X0 = 0.2
BAND_Y1 = 0.1
FRONT_RUN = WALL_C[0] - BAND_X0                         # 1.6
CHORD = 2.0 * R_WALL * np.sin(np.pi / 4.0 / WALL_FACETS[0])
CORNER_RUN = WALL_FACETS[0] * CHORD                     # 0.936
SIDE_RUN = BAND_Y1 - WALL_C[1]                          # 1.2
BAND_LEN = FRONT_RUN + CORNER_RUN + SIDE_RUN            # 3.736
FRONT_PANES, SIDE_PANES = 3, 2
BAND_MULLIONS = tuple(
    [FRONT_RUN * k / FRONT_PANES for k in range(1, FRONT_PANES)]
    + [FRONT_RUN + CHORD * k for k in range(WALL_FACETS[0] + 1)]
    + [FRONT_RUN + CORNER_RUN + SIDE_RUN * k / SIDE_PANES for k in range(1, SIDE_PANES)])
HATCH_PANE = 1           # the front's middle pane slides: the serving hatch
BAND_DEPTH = 0.06        # glass set back at LOD0/LOD1

# ============================================================== openings
# Casing rectangles on their wall, (width, height) in metres. The customer
# door: a 0.90 x 2.10 glazed leaf, a transom bar and transom light above it
# up to the soffit, in a 0.07 m frame. The staff door: 0.90 x 2.10, cased.
DOOR_LEAF_W, DOOR_LEAF_H, DOOR_FRAME = 0.90, Z_LEAF, 0.07
DOOR_SIZE = (DOOR_LEAF_W + 2 * DOOR_FRAME, Z_HEAD)          # 1.04 x 2.84
STAFF_LEAF_W, STAFF_LEAF_H, STAFF_FRAME = 0.90, 2.10, 0.07
STAFF_SIZE = (STAFF_LEAF_W + 2 * STAFF_FRAME, Z_MID)        # 1.04 x 2.17
POSTER_SIZE = (0.70, Z_MID - Z_COUNTER)                     # 0.70 x 1.12
DOOR_DEPTH, STAFF_DEPTH = 0.10, 0.06

# attached furniture
SHUTTER = (0.52, 0.10, 1.08, 2.88)       # width, thickness, z0, z1 (into the soffit)
# The folded stack, wall outward: a hinge rail set back from both edges
# (the shadow gap), then three leaves, each a little narrower than the one
# behind it, so their edges step. (half-width inset from the stack's edge,
# out0, out1), metres from the wall plane.
SHUTTER_LAYERS = ((0.05, -0.02, 0.025), (0.0, 0.025, 0.05),
                  (0.012, 0.05, 0.075), (0.024, 0.075, 0.10))
RACK = (0.60, 0.20, 0.40, 1.35)          # width, depth, z0, z1
BENCH = (2.0, 0.32, 0.42, 0.47)          # length, depth, z0, z1
# The lit board: a slim galvanised-framed box standing on two short posts
# over the canopy's front edge, a gap between it and the flashing.
SIGN_W, SIGN_H = 2.8, 0.42
SIGN_GAP = 0.10                          # clear between the fascia top and the board
SIGN_CAP = 0.32                          # KIOSKI's cap height as seen, strokes included
SIGN_STYLE = "dark"                      # "dark": lit letters; "cream": a lit face (notes.md)


def m(v):
    """Metres -> pixels at 64 px/m."""
    return v * PPM


# ================================================================ layout
WALL_Y0, WALL_H = 0, 192.0                      # z 0 .. 3.0
FASCIA_Y0 = 198.0
FASCIA_H = (Z_TOP - Z_SOFFIT) * PPM             # 19.2
RIB_PX = 3.2                                    # 50 mm rib pitch, 320 to the sheet

SOFFIT = (4.0, 226.0, (CX1 - CX0) * PPM, (CY1 - CY0) * PPM)            # 432 x 342.4
DECK = (444.0, 226.0, (CX1 - CX0) * DECK_PPM, (CY1 - CY0) * DECK_PPM)  # 216 x 171.2
BAND = (668.0, 226.0, BAND_LEN * PPM, (Z_HEAD - Z_COUNTER) * PPM)      # 239 x 114.6
DOOR = (912.0, 226.0, m(DOOR_SIZE[0]), m(DOOR_SIZE[1]))                # 66.6 x 181.8
STAFF = (444.0, 406.0, m(STAFF_SIZE[0]), m(STAFF_SIZE[1]))             # 66.6 x 138.9
POSTER_A = (518.0, 406.0, m(POSTER_SIZE[0]), m(POSTER_SIZE[1]))        # 44.8 x 71.7
POSTER_B = (570.0, 406.0, m(POSTER_SIZE[0]), m(POSTER_SIZE[1]))
SHUTTER_FACE = (622.0, 406.0, m(SHUTTER[0]), m(SHUTTER[3] - SHUTTER[2]))   # 33.3 x 110.1
# the stack's side faces, U = metres out from 0.02 m inside the wall
SHUTTER_EDGE = (662.0, 406.0, m(SHUTTER[1] + 0.02), m(SHUTTER[3] - SHUTTER[2]))  # 7.7 x 115
RACK_FACE = (676.0, 406.0, m(RACK[0]), m(RACK[3] - RACK[2]))               # 38.4 x 60.8
BENCH_TOP = (722.0, 406.0, m(BENCH[0]), m(BENCH[1]))                       # 128 x 20.5
LAMP_FACE = (722.0, 432.0, m(0.16), m(0.14))                              # 10.2 x 9.0
SIGN = (4.0, 576.0, SIGN_W * SIGN_PPM, SIGN_H * SIGN_PPM)                  # 358.4 x 53.8

PATCH_NAMES = ("blank", "reveal", "flash", "steel", "bin", "post", "lamp",
               "lens", "timber", "shutter_top", "sign_edge", "light", "fitting")
PATCHES = {n: (4.0 + 20.0 * i, 690.0, 16.0, 16.0) for i, n in enumerate(PATCH_NAMES)}

REGIONS = {"soffit": SOFFIT, "deck": DECK, "band": BAND, "door": DOOR,
           "staff": STAFF, "poster_a": POSTER_A, "poster_b": POSTER_B,
           "shutter_face": SHUTTER_FACE, "shutter_edge": SHUTTER_EDGE,
           "rack": RACK_FACE, "bench": BENCH_TOP, "lamp_face": LAMP_FACE, "sign": SIGN}

# ------------------------------------------------------------ material ids
(ID_BLANK, ID_PLINTH, ID_BOARD, ID_FLASH, ID_SOFFIT, ID_FELT, ID_FRAME,
 ID_GLASS, ID_DOOR, ID_STEEL, ID_SIGN, ID_SIGN_T, ID_LIGHT, ID_POSTER,
 ID_POSTER_A, ID_POSTER_B, ID_POSTER_C, ID_SHUTTER, ID_TIMBER, ID_BIN,
 ID_MAG_A, ID_MAG_B, ID_MAG_C, ID_LAMP, ID_SEAL, ID_FITTING, ID_SIGN_LIT,
 ID_HINGE) = range(28)

# (roughness, metallic). Powder-coated frames, painted boards and steel are
# dielectric; galvanised flashing and the stainless counter are metal.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_BOARD: (0.70, 0.0),
    ID_FLASH: (0.38, 0.80), ID_SOFFIT: (0.82, 0.0), ID_FELT: (0.95, 0.0),
    ID_FRAME: (0.45, 0.0), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_DOOR: (0.52, 0.0), ID_STEEL: (0.28, 0.90), ID_SIGN: (0.30, 0.0),
    ID_SIGN_T: (0.20, 0.0), ID_LIGHT: (0.20, 0.0), ID_POSTER: (0.55, 0.0),
    ID_POSTER_A: (0.55, 0.0), ID_POSTER_B: (0.55, 0.0), ID_POSTER_C: (0.55, 0.0),
    # the shutter leaves are enamelled, a sheen apart from the boards' paint
    ID_SHUTTER: (0.46, 0.0), ID_TIMBER: (0.78, 0.0), ID_BIN: (0.50, 0.0),
    ID_MAG_A: (0.45, 0.0), ID_MAG_B: (0.45, 0.0), ID_MAG_C: (0.45, 0.0),
    ID_LAMP: (0.20, 0.0), ID_SEAL: (0.80, 0.0), ID_FITTING: (0.40, 0.0),
    ID_SIGN_LIT: (0.25, 0.0), ID_HINGE: (0.42, 0.75),
}

# ---------------------------------------------------------------- palettes
# Only the boarding (walls, fascia ribs, the shutter leaves) changes colour.
VARIANTS = {
    "ochre_boards": {"board": (178, 152, 102)},
    "cream_boards": {"board": (210, 198, 166)},
    "green_boards": {"board": (126, 138, 114)},
    "red_boards": {"board": (146, 84, 64)},
}
DEFAULT_VARIANT = "ochre_boards"

# Graphite frames sit a step above the glass (~55) so no pane measures
# brighter than its casing.
FIXED = {
    ID_BLANK: (52, 52, 52), ID_PLINTH: (132, 130, 124), ID_FLASH: (150, 152, 152),
    ID_SOFFIT: (222, 222, 216), ID_FELT: (66, 66, 64), ID_FRAME: (72, 74, 76),
    ID_GLASS: glazing.BASE, ID_DOOR: (86, 92, 90), ID_STEEL: (172, 174, 174),
    ID_SIGN: (40, 42, 44), ID_SIGN_T: (236, 226, 200), ID_LIGHT: (226, 222, 210),
    ID_POSTER: (214, 210, 198), ID_POSTER_A: (170, 96, 66), ID_POSTER_B: (78, 108, 132),
    ID_POSTER_C: (102, 102, 100), ID_TIMBER: (128, 96, 64), ID_BIN: (66, 76, 68),
    ID_MAG_A: (168, 72, 58), ID_MAG_B: (70, 104, 140), ID_MAG_C: (196, 186, 160),
    ID_LAMP: (214, 210, 196), ID_SEAL: (28, 28, 28), ID_FITTING: (208, 208, 202),
    ID_SIGN_LIT: (230, 224, 204), ID_HINGE: (118, 120, 120),
}

BAND_IDS = {
    "WALL": ((WALL_Y0, WALL_H + PAD), {ID_BOARD, ID_PLINTH, ID_FLASH}),
    "FASCIA": ((FASCIA_Y0 - PAD, FASCIA_Y0 + FASCIA_H + PAD), {ID_BOARD, ID_FLASH}),
}

# Emission. Glass is neutral white, so scripts/validate_asset.py reads it
# as glazing; every other lit thing carries its own warm colour (channel
# spread far over 24) and is reported as a luminous fixture: the sign
# letters, the soffit downlights and the staff door's lamp.
EMIT = {ID_GLASS: (255, 255, 255), ID_SIGN_T: (255, 226, 160),
        ID_SIGN_LIT: (255, 232, 184), ID_LIGHT: (255, 212, 146),
        ID_LAMP: (255, 194, 118)}
# Linear RGB: a kiosk's fluorescent interior, as the catalog's other shops.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
RIB_H = 0.006            # the boarding's rib crowns over their grooves
FRAME_H = 0.020          # window frames, proud of the glass
FLASH_H = 0.010          # flashing folds
SLAT_H = 0.008           # bench slats over their gaps

# the downlights under the soffit, world (x, y): surface-mounted drums at
# LOD0/LOD1 (an opal band and an opal base under a white housing), painted
# discs of the same size from LOD2
DOWNLIGHTS = ((-1.65, -2.55), (1.0, -2.55), (3.25, -0.45))
DOWNLIGHT_R = 0.13
DOWNLIGHT_Z = (Z_SOFFIT - 0.10, Z_SOFFIT - 0.045)   # the drum's foot, its opal band's top
SOFFIT_JOINT = 1.2       # the soffit's sheet joints, along X
FELT_ROLL = 1.0          # felt rolls laid along X, lapped every metre in Y
DRAIN = (-1.5, 1.15)     # the deck's outlet, over the sales room's rear corner


# ================================================================ helpers
def plan_px(rect, x, y, ppm):
    """World plan point -> atlas pixel in a plan-mapped region."""
    return rect[0] + (x - CX0) * ppm, rect[1] + (y - CY0) * ppm


def in_rounded(X, Y, x0, y0, x1, y1, r):
    """Samples inside a rectangle with per-corner radii r (fr, rr, rl, fl)."""
    inside = (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)
    for key, cx, cy, sx, sy in (("fr", x1 - r["fr"], y0 + r["fr"], 1, -1),
                                ("rr", x1 - r["rr"], y1 - r["rr"], 1, 1),
                                ("rl", x0 + r["rl"], y1 - r["rl"], -1, 1),
                                ("fl", x0 + r["fl"], y0 + r["fl"], -1, -1)):
        corner = ((X - cx) * sx > 0) & ((Y - cy) * sy > 0)
        inside &= ~corner | (np.hypot(X - cx, Y - cy) <= r[key])
    return inside


def _frame(c, x0, y0, x1, y1, t, mid, ao=0.86, h=FRAME_H, sides="lrtb"):
    """A frame *t* px wide inside the rect, bevelled."""
    parts = {"b": (x0, x1, y0, y0 + t, "y"), "t": (x0, x1, y1 - t, y1, "y"),
             "l": (x0, x0 + t, y0, y1, "x"), "r": (x1 - t, x1, y0, y1, "x")}
    for k in sides:
        a0, a1, b0, b1, axes = parts[k]
        c.paint(a0, a1, b0, b1, mid, 1.0, ao)
        c.bevel(a0, a1, b0, b1, h, 1.0, axes=axes)


def ribs(c, x0, x1, y0, y1):
    """Narrow vertical ribbed boarding: a rib crown every RIB_PX in U, a
    groove between, every eighth groove a board joint a little deeper."""
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    ph = (X % RIB_PX) / RIB_PX
    d = np.abs(ph - 0.5) * 2.0                        # 0 at the crown, 1 in the groove
    prof = np.clip((0.86 - d) / 0.30, 0.0, 1.0)
    c.height[sy, sx] = RIB_H * prof
    # every eighth groove a board joint, only a little deeper: at a distance
    # the ribs must read as one fine texture, not as 0.4 m planks
    joint = (np.floor(X / RIB_PX).astype(np.int64) % 8 == 0) & (d > 0.70)
    c.shade[sy, sx] = (0.90 + 0.10 * prof) * np.where(joint, 0.94, 1.0)
    c.ao[sy, sx] = (0.78 + 0.22 * prof) * np.where(joint, 0.92, 1.0)
    tone = 0.994 + 0.012 * atlas.hash_unit(np.floor(X / (8 * RIB_PX)).astype(np.int64), 5)
    c.shade[sy, sx] *= tone


# ================================================================= bands
def paint_wall_band(c):
    """Ground to the wall solid's top: concrete plinth, a galvanised drip
    over it, ribbed boarding, the shadow line where the boards meet the
    soffit. V is height from the ground on every wall."""
    top = WALL_Y0 + WALL_H
    c.paint(0, ATLAS, WALL_Y0 - PAD, top + PAD, ID_BOARD, 1.0, 1.0, height=0.0)
    ribs(c, 0, ATLAS, m(Z_PLINTH), top + PAD)
    yp = m(Z_PLINTH)
    c.paint(0, ATLAS, WALL_Y0 - PAD, yp, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, WALL_Y0 - PAD, yp)
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.86 + 0.14 * np.clip(Y / yp, 0, 1))
    c.paint(0, ATLAS, yp - 1.0, yp + 1.2, ID_FLASH, 0.95, 0.85)
    c.bevel(0, ATLAS, yp - 1.0, yp + 1.2, FLASH_H, 0.6, axes="y")
    c.mul(0, ATLAS, yp - 2.8, yp - 1.0, 0.84, ao=0.80)          # the drip's shadow
    # the soffit's shadow line along the top of the boards
    ys = m(Z_SOFFIT)
    sy, sx, Y, _ = c.field(0, ATLAS, ys - 6.0, ys)
    t = np.clip((Y - (ys - 6.0)) / 6.0, 0.0, 1.0)
    c.ao[sy, sx] *= 1.0 - 0.30 * t * t
    c.shade[sy, sx] *= 1.0 - 0.10 * t * t


def paint_fascia_band(c):
    """The canopy's 0.30 m edge: ribs in the wall colour, a thin galvanised
    flashing folded over the top, a drip line at the soffit."""
    y0, h = FASCIA_Y0, FASCIA_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_BOARD, 1.0, 1.0, height=0.0)
    ribs(c, 0, ATLAS, y0 - PAD, y0 + h + PAD)
    c.paint(0, ATLAS, y0 + h - 1.6, y0 + h + PAD, ID_FLASH, 1.0, 0.95)
    c.bevel(0, ATLAS, y0 + h - 1.6, y0 + h, FLASH_H, 0.6, axes="y")
    c.mul(0, ATLAS, y0 + h - 3.0, y0 + h - 1.6, 0.86, ao=0.82)   # under the fold
    c.paint(0, ATLAS, y0 - PAD, y0 + 0.8, ID_FLASH, 0.80, 0.85)  # the drip
    c.height[c.sl(0, ATLAS, y0 - PAD, y0 + 0.8)] = 0.0


# =============================================================== regions
def paint_soffit(c):
    """Plain white soffit, darkening toward the walls where it sees least
    sky, with the three round downlights in it."""
    x, y, w, h = SOFFIT
    c.paint(x, x + w, y, y + h, ID_SOFFIT, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x, x + w, y, y + h)
    wx = CX0 + (X - x) / PPM
    wy = CY0 + (Y - y) / PPM
    dx = np.maximum(np.maximum(WX0 - wx, wx - WX1), 0.0)
    dy = np.maximum(np.maximum(WY0 - wy, wy - WY1), 0.0)
    d = np.hypot(dx, dy)
    c.ao[sy, sx] = 0.72 + 0.28 * np.clip(d / 0.9, 0.0, 1.0)
    c.shade[sy, sx] = 0.94 + 0.06 * np.clip(d / 0.9, 0.0, 1.0)
    # the soffit's sheet joints, 1.2 m apart across the slab
    for k in range(1, int((CX1 - CX0) / SOFFIT_JOINT) + 1):
        u = x + m(k * SOFFIT_JOINT)
        c.mul(u - 0.4, u + 0.4, y, y + h, 0.93, ao=0.90)
        c.lift(u - 0.4, u + 0.4, y, y + h, -0.002)
    # under the drums at LOD0/LOD1, the lamps themselves from LOD2
    for wxl, wyl in DOWNLIGHTS:
        px, py = plan_px(SOFFIT, wxl, wyl, PPM)
        c.disc(px, py, m(DOWNLIGHT_R + 0.02), ID_FITTING, 1.0, 0.9, height=0.006)
        c.disc(px, py, m(DOWNLIGHT_R - 0.02), ID_LIGHT, 1.0, 1.0, height=0.0)


def paint_deck(c):
    """The roof seen from above, plan-mapped at 32 px/m over the whole
    canopy: the galvanised rim flashing round the outline, dark felt inside
    it, laid in rolls and a little ponded."""
    x, y, w, h = DECK
    c.paint(x, x + w, y, y + h, ID_FLASH, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x, x + w, y, y + h)
    wx = CX0 + (X - x) / DECK_PPM
    wy = CY0 + (Y - y) / DECK_PPM
    r_in = {k: v - RIM for k, v in R_CANOPY.items()}
    felt = in_rounded(wx, wy, CX0 + RIM, CY0 + RIM, CX1 - RIM, CY1 - RIM, r_in)
    c.mid[sy, sx] = np.where(felt, ID_FELT, ID_FLASH).astype(np.uint8)
    # the felt's rolls, each a shade apart, lapped every metre: the lap's
    # bead a little raised and lighter, its shadow below it
    rs = np.random.RandomState(7)
    roll = np.floor((Y - y) / (FELT_ROLL * DECK_PPM)).astype(np.int64)
    lap = (Y - y) / (FELT_ROLL * DECK_PPM) - roll          # 0 at the lap, up to 1
    tone = 0.92 + 0.16 * atlas.hash_unit(roll, 11)
    bead = (lap * FELT_ROLL * DECK_PPM < 1.3) & (roll > 0)
    under = (lap * FELT_ROLL * DECK_PPM > FELT_ROLL * DECK_PPM - 1.0)
    k = np.where(bead, 1.32, np.where(under, 0.84, 1.0)) * tone
    c.shade[sy, sx] = np.where(felt, c.shade[sy, sx] * k, c.shade[sy, sx])
    c.height[sy, sx] = np.where(felt & bead, 0.003, c.height[sy, sx])
    c.ao[sy, sx] = np.where(felt & under, np.minimum(c.ao[sy, sx], 0.88), c.ao[sy, sx])
    for _ in range(8):
        cx, cy = rs.uniform(x + 20, x + w - 20), rs.uniform(y + 20, y + h - 20)
        c.disc(cx, cy, rs.uniform(5, 12), None, rs.uniform(0.92, 0.98), 0.97)
    # the outlet: ponding stain round it, a galvanised ring, a dark domed grate
    dx, dy = (DRAIN[0] - CX0) * DECK_PPM + x, (DRAIN[1] - CY0) * DECK_PPM + y
    sy, sx, Y, X = c.field(dx - 24, dx + 24, dy - 24, dy + 24)
    r = np.hypot(X - dx, Y - dy) / DECK_PPM
    c.shade[sy, sx] *= 1.0 - 0.12 * np.clip(1.0 - r / 0.7, 0.0, 1.0)
    c.disc(dx, dy, 0.17 * DECK_PPM, ID_FLASH, 0.9, 0.85, height=0.004)
    c.disc(dx, dy, 0.11 * DECK_PPM, ID_FRAME, 0.55, 0.6, height=0.0)
    for k in range(-2, 3):
        c.paint(dx - 0.10 * DECK_PPM, dx + 0.10 * DECK_PPM, dy + k * 0.7 - 0.2,
                dy + k * 0.7 + 0.2, None, 0.9)
    # the upstand's shadow along the felt's edge
    sy, sx, Y, X = c.field(x, x + w, y, y + h)
    wx = CX0 + (X - x) / DECK_PPM
    wy = CY0 + (Y - y) / DECK_PPM
    near = np.zeros(Y.shape, bool)
    for k in range(1, 5):
        r_k = {kk: vv - RIM - 0.04 * k for kk, vv in R_CANOPY.items()}
        r_k = {kk: max(vv, 0.01) for kk, vv in r_k.items()}
        near |= ~in_rounded(wx, wy, CX0 + RIM + 0.04 * k, CY0 + RIM + 0.04 * k,
                            CX1 - RIM - 0.04 * k, CY1 - RIM - 0.04 * k, r_k)
    felt = c.mid[sy, sx] == ID_FELT
    c.ao[sy, sx] = np.where(felt & near, np.minimum(c.ao[sy, sx], 0.80), c.ao[sy, sx])


def band_px(s, z):
    return BAND[0] + s * PPM, BAND[1] + (z - Z_COUNTER) * PPM


def paint_band(c):
    """The serving corner's glazing: graphite frames, slim mullions at every
    pane joint and corner facet, a transom bar level with the door's, and
    the front's middle pane a sliding hatch with a stainless pass rail."""
    x, y, w, h = BAND
    c.paint(x, x + w, y, y + h, ID_GLASS, 1.0, 1.0, height=0.0)
    fr = m(0.06)
    _frame(c, x, y, x + w, y + h, fr, ID_FRAME)
    mw = m(0.05)
    for s in BAND_MULLIONS:
        u = x + s * PPM
        c.paint(u - mw / 2, u + mw / 2, y, y + h, ID_FRAME, 1.0, 0.88)
        c.bevel(u - mw / 2, u + mw / 2, y, y + h, FRAME_H, 1.0, axes="x")
    _, yb0 = band_px(0, Z_LEAF)
    _, yb1 = band_px(0, Z_BAR)
    c.paint(x, x + w, yb0, yb1, ID_FRAME, 1.0, 0.88)
    c.bevel(x, x + w, yb0, yb1, FRAME_H, 1.0, axes="y")
    c.mul(x, x + w, yb0 - 1.5, yb0, 0.9, ao=0.85)                  # under the bar
    # the hatch: two sliding sashes inside the middle pane, the right in front
    s0 = FRONT_RUN * HATCH_PANE / FRONT_PANES
    s1 = FRONT_RUN * (HATCH_PANE + 1) / FRONT_PANES
    hx0, hx1 = x + s0 * PPM + mw / 2, x + s1 * PPM - mw / 2
    hy0, hy1 = y + fr, yb0
    sash = m(0.035)
    _frame(c, hx0, hy0, hx1, hy1, sash, ID_FRAME, 0.84, FRAME_H * 0.7)
    mx = (hx0 + hx1) / 2.0
    c.paint(mx - sash, mx + sash, hy0, hy1, ID_FRAME, 1.0, 0.84)
    c.bevel(mx - sash, mx + sash, hy0, hy1, FRAME_H, 1.0, axes="x")
    c.mul(mx - 0.4, mx + 0.4, hy0, hy1, 0.7, ao=0.7)
    c.paint(hx0, hx1, hy0, hy0 + m(0.05), ID_STEEL, 1.0, 0.86)
    c.bevel(hx0, hx1, hy0, hy0 + m(0.05), FRAME_H, 1.0, axes="y")
    c.paint(mx + sash, mx + sash + 1.4, hy0 + m(0.4), hy0 + m(0.52), ID_STEEL, 1.0,
            0.85, height=0.02)
    # glass seals: a dark hairline inside every frame edge
    c.mul(x + fr, x + w - fr, y + h - fr - 1.0, y + h - fr, 0.80, ao=0.80)


def paint_door(c):
    """Customer door: graphite frame, a glazed leaf with stiles, a deep
    bottom rail and a stainless push bar, the transom bar at 2.10 m and the
    transom light over it up to the soffit."""
    x, y, w, h = DOOR
    c.paint(x, x + w, y, y + h, ID_GLASS, 1.0, 1.0, height=0.0)
    f = m(DOOR_FRAME)
    _frame(c, x, y, x + w, y + h, f, ID_FRAME, sides="lrt")
    lx0, lx1 = x + f, x + w - f
    st = m(0.07)
    yl = y + m(Z_LEAF)
    _frame(c, lx0, y, lx1, yl, st, ID_FRAME, 0.9)
    c.paint(lx0, lx1, y, y + m(0.24), ID_FRAME, 1.0, 0.9)
    c.bevel(lx0, lx1, y, y + m(0.24), FRAME_H, 1.0)
    c.mul(lx0, lx1, y, y + 1.5, 0.75, ao=0.70)                       # threshold
    c.paint(x, x + w, yl, y + m(Z_BAR), ID_FRAME, 1.0, 0.86)           # transom bar
    c.bevel(x, x + w, yl, y + m(Z_BAR), FRAME_H, 1.0, axes="y")
    c.mul(lx0, lx1, yl - 1.5, yl, 0.85, ao=0.8)
    yb = y + m(1.0)
    c.paint(lx0 + st, lx1 - st, yb - 1.4, yb + 1.4, ID_STEEL, 1.0, 0.9)
    c.bevel(lx0 + st, lx1 - st, yb - 1.4, yb + 1.4, 0.03, 1.0, axes="y")
    c.mul(lx0 + st, lx1 - st, yb - 3.0, yb - 1.4, 0.80, ao=0.80)
    # the hinge side's dark gap and the closer's shoe under the bar
    c.mul(lx0, lx0 + 0.8, y, yl, 0.7, ao=0.7)


def paint_staff(c):
    """Staff door: a painted steel leaf in a graphite casing, a lever, a
    stainless kick plate, two stiffener lines."""
    x, y, w, h = STAFF
    f = m(STAFF_FRAME)
    c.paint(x, x + w, y, y + h, ID_DOOR, 1.0, 0.95, height=0.0)
    _frame(c, x, y, x + w, y + h, f, ID_FRAME, 0.84, FLASH_H, sides="lrt")
    x0, x1, y0, y1 = x + f, x + w - f, y, y + m(STAFF_LEAF_H)
    for k in (1, 2):
        yy = y0 + (y1 - y0) * k / 3.0
        c.mul(x0 + 3, x1 - 3, yy - 0.6, yy + 0.6, 0.88, ao=0.88)
        c.lift(x0 + 3, x1 - 3, yy - 0.6, yy + 0.6, -0.003)
    c.paint(x0, x1, y0, y0 + m(0.20), ID_STEEL, 1.0, 0.9)
    hx, hy = x1 - m(0.08), y0 + m(1.05)
    c.paint(hx - m(0.12), hx + 1.0, hy - 1.0, hy + 1.0, ID_STEEL, 1.0, 0.85, height=0.03)
    c.disc(hx, hy, 2.0, ID_STEEL, 0.9, 0.85, height=0.015)
    c.mul(x0, x0 + 0.8, y0, y1, 0.7, ao=0.7)


def paint_poster(c, rect, seed):
    """A poster case on the blank wall: aluminium-grey frame, a paper of
    abstract blocks and grey bars, no lettering and no brand."""
    x, y, w, h = rect
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 0.9, height=0.0)
    c.bevel(x, x + w, y, y + h, FRAME_H, 1.0)
    f = m(0.04)
    x0, x1, y0, y1 = x + f, x + w - f, y + f, y + h - f
    c.paint(x0, x1, y0, y1, ID_POSTER, 1.0, 1.0, height=0.0)
    iw, ih = x1 - x0, y1 - y0
    rs = np.random.RandomState(seed)
    a, b = (ID_POSTER_A, ID_POSTER_B) if seed % 2 else (ID_POSTER_B, ID_POSTER_A)
    c.paint(x0 + 2, x1 - 2, y1 - 0.20 * ih, y1 - 2, a, 1.0, 1.0)
    top = 0.30 + 0.1 * rs.rand()
    c.paint(x0 + 3, x0 + (0.55 + 0.1 * rs.rand()) * iw, y0 + top * ih, y1 - 0.26 * ih,
            b, 1.0, 1.0)
    c.disc(x0 + 0.78 * iw, y0 + (0.45 + 0.1 * rs.rand()) * ih, 0.14 * iw, a, 1.0, 1.0)
    for k in range(4):
        yy = y0 + 0.07 * ih + k * 0.055 * ih
        c.paint(x0 + 3, x0 + (0.9 - 0.18 * (k % 2)) * iw, yy, yy + 1.4, ID_POSTER_C, 1.0, 1.0)
    c.mul(x0, x1, y0, y1, 1.0, ao=0.92)
    c.mul(x0, x1, y1 - 1.5, y1, 0.85, ao=0.85)                       # the frame's shadow


SHUTTER_HINGES = (0.10, 0.50, 0.90)      # hinge heights, fractions of the leaf


def paint_shutters(c):
    """The folding shutter leaves held open, enamelled in the wall colour.

    SHUTTER_FACE is the stack seen from the front, U along the wall: the
    outer leaf's face with a bevelled edge and hinge knuckles at both edges
    (the leaves fold accordion-wise), and at each side the stepped edges of
    the two leaves behind it with dark gaps between. SHUTTER_EDGE is the
    stack's side, U outward from inside the wall: the hinge rail in the
    shadow gap, then the three leaves' edges with the knuckles across
    their joints."""
    x, y, w, h = SHUTTER_FACE
    c.paint(x, x + w, y, y + h, ID_SHUTTER, 1.0, 1.0, height=0.0)
    insets = [lay[0] for lay in SHUTTER_LAYERS[1:]]           # back, middle, front leaf
    for i, inset in enumerate(insets):
        a0, a1 = x + m(inset), x + w - m(inset)
        c.paint(a0, a1, y, y + h, ID_SHUTTER, 1.0 - 0.04 * (2 - i), 1.0 - 0.08 * (2 - i))
        for u in (a0, a1):                                     # the gap at each leaf edge
            c.mul(u - 0.45, u + 0.45, y, y + h, 0.45, ao=0.5)
    a0, a1 = x + m(insets[-1]), x + w - m(insets[-1])
    c.bevel(a0, a1, y, y + h, 0.004, 1.4)                      # the leaf's rounded arrises
    # a slim pressed panel line round the leaf, and its foot's kick wear
    t = m(0.05)
    c.mul(a0 + t, a1 - t, y + t, y + t + 0.6, 0.88, ao=0.88)
    c.mul(a0 + t, a1 - t, y + h - t - 0.6, y + h - t, 0.88, ao=0.88)
    c.mul(a0 + t, a0 + t + 0.6, y + t, y + h - t, 0.88, ao=0.88)
    c.mul(a1 - t - 0.6, a1 - t, y + t, y + h - t, 0.88, ao=0.88)
    for k in SHUTTER_HINGES:
        hy = y + h * k
        for u0, u1 in ((x, a0 + 1.2), (a1 - 1.2, x + w)):
            c.paint(u0, u1, hy - 3.0, hy + 3.0, ID_HINGE, 1.0, 0.85, height=0.01)
            c.mul(u0, u1, hy - 3.8, hy - 3.0, 0.7, ao=0.75)
    x, y, w, h = SHUTTER_EDGE
    c.paint(x, x + w, y, y + h, ID_SHUTTER, 0.9, 0.85, height=0.0)
    rail = m(SHUTTER_LAYERS[0][2] + 0.02)
    c.paint(x, x + rail, y, y + h, ID_HINGE, 0.45, 0.45)       # the rail in the gap
    for lay in SHUTTER_LAYERS[1:]:
        u = x + m(lay[1] + 0.02)
        c.mul(u - 0.3, u + 0.3, y, y + h, 0.5, ao=0.5)
        c.lift(u - 0.3, u + 0.3, y, y + h, -0.004)
        for k in SHUTTER_HINGES:
            hy = y + h * k
            c.paint(u - 0.8, u + 0.8, hy - 3.0, hy + 3.0, ID_HINGE, 1.0, 0.85, height=0.006)


def paint_rack(c):
    """The wall-fixed newspaper and magazine rack: a graphite frame, three
    tiers of covers (abstract colour blocks, no titles), a steel retaining
    bar across each tier."""
    x, y, w, h = RACK_FACE
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 0.9, height=0.0)
    rs = np.random.RandomState(31)
    tiers = 3
    f = m(0.03)
    th = (h - 2 * f) / tiers
    for k in range(tiers):
        ty0 = y + f + k * th
        u = x + f
        while u < x + w - f - 4:
            cw = min(rs.uniform(6.5, 9.5), x + w - f - u)
            mid = (ID_MAG_A, ID_MAG_B, ID_MAG_C, ID_POSTER)[rs.randint(4)]
            c.paint(u + 0.4, u + cw - 0.4, ty0 + 2.0, ty0 + th - 1.0, mid,
                    rs.uniform(0.75, 1.0), 0.9, height=0.004)
            c.paint(u + 1.2, u + cw - 1.2, ty0 + th - 5.0, ty0 + th - 3.2,
                    ID_POSTER_C, 1.0, 1.0)
            u += cw
        c.paint(x + f, x + w - f, ty0 + 0.25 * th, ty0 + 0.25 * th + 1.2, ID_STEEL,
                1.0, 0.85, height=0.012)
        c.mul(x + f, x + w - f, ty0, ty0 + 2.0, 0.7, ao=0.7)


def paint_bench(c):
    """The bench seat from above: three timber slats along its length."""
    x, y, w, h = BENCH_TOP
    c.paint(x, x + w, y, y + h, ID_TIMBER, 1.0, 1.0, height=0.0)
    slat = h / 3.0
    for k in range(3):
        c.bevel(x, x + w, y + k * slat + 0.5, y + (k + 1) * slat - 0.5, SLAT_H, 0.8, axes="y")
        c.mul(x, x + w, y + k * slat - 0.5, y + k * slat + 0.5, 0.55, ao=0.55)
    grain = atlas.noise(c, 21, 30.0, 0.6)
    sy, sx = c.sl(x, x + w, y, y + h)
    c.shade[sy, sx] *= 1.0 + 0.05 * grain[sy, sx]


SIGN_TRACKING = 0.55     # wide-set capitals, as mid-century boards were lettered
SIGN_WEIGHT = 0.055      # stroke, metres
SIGN_FRAME = 0.02        # the galvanised frame round the face, metres


def paint_sign(c):
    """The sign board's face: a slim galvanised frame round it and KIOSKI in
    the catalog's stroked capitals (scripts/lettering.py), wide-set, a short
    rule either side.
    SIGN_STYLE "dark": warm-white lit letters on a graphite face; "cream": a
    lit cream opal face with graphite letters. Generic: the building type in
    Finnish, in no chain's colours or letterforms."""
    x, y, w, h = SIGN
    face, ink = (ID_SIGN, ID_SIGN_T) if SIGN_STYLE == "dark" else (ID_SIGN_LIT, ID_SIGN)
    c.paint(x, x + w, y, y + h, face, 1.0, 1.0, height=0.0)
    e = SIGN_FRAME * SIGN_PPM
    for a0, a1, b0, b1, axes in ((x, x + w, y, y + e, "y"), (x, x + w, y + h - e, y + h, "y"),
                                 (x, x + e, y, y + h, "x"), (x + w - e, x + w, y, y + h, "x")):
        c.paint(a0, a1, b0, b1, ID_FLASH, 1.0, 0.9)
        c.bevel(a0, a1, b0, b1, 0.010, 1.2, axes=axes)
    c.mul(x + e, x + w - e, y + h - e - 1.2, y + h - e, 0.9, ao=0.85)   # the frame's lip
    # the glyphs are centrelines: the stroke adds half its weight above and below
    cap, weight = (SIGN_CAP - SIGN_WEIGHT) * SIGN_PPM, SIGN_WEIGHT * SIGN_PPM
    lettering.centred_text(c, "KIOSKI", SIGN, cap, weight, ink, SIGN_TRACKING, shade=1.0,
                           ao=1.0, height=0.004)
    wide = lettering.text_width("KIOSKI", cap, SIGN_TRACKING, weight)
    ym = y + h / 2.0
    for side in (-1, 1):
        a = x + w / 2.0 + side * (wide / 2.0 + 0.16 * SIGN_PPM)
        b = a + side * 0.20 * SIGN_PPM
        c.stroke((a, ym), (b, ym), weight, ink, 1.0, 1.0, height=0.004)


def paint_lamp_face(c):
    """The staff door lamp's front: a graphite bulkhead with its opal lens
    in the lower part, under a shallow hood."""
    x, y, w, h = LAMP_FACE
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 0.92, height=0.0)
    c.paint(x + 1.0, x + w - 1.0, y + 0.8, y + h * 0.62, ID_LAMP, 1.0, 1.0)
    c.mul(x + 1.0, x + w - 1.0, y + h * 0.62 - 0.7, y + h * 0.62, 0.85, ao=0.8)


def paint_patches(c):
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0),
        "reveal": (ID_FRAME, 0.90, 0.70),
        "flash": (ID_FLASH, 1.0, 0.92),
        "steel": (ID_STEEL, 1.0, 0.92),
        "bin": (ID_BIN, 1.0, 0.92),
        "post": (ID_FRAME, 1.0, 0.92),
        "lamp": (ID_FRAME, 1.0, 0.92),
        "lens": (ID_LAMP, 1.0, 1.0),
        "timber": (ID_TIMBER, 0.85, 0.85),
        "shutter_top": (ID_SHUTTER, 0.75, 0.6),
        "sign_edge": (ID_SIGN, 1.0, 0.92),
        "light": (ID_LIGHT, 1.0, 1.0),
        "fitting": (ID_FITTING, 1.0, 0.95),
    }
    atlas.paint_patches(c, PATCHES, spec)


# ================================================================ checks
def check_regions():
    """Fail the bake if two regions overlap, meet the bands, or run off."""
    rects = dict(REGIONS)
    rects.update(PATCHES)
    problems = atlas.region_problems(rects, ATLAS, bands_top=FASCIA_Y0 + FASCIA_H + PAD)
    if FASCIA_Y0 - PAD < WALL_Y0 + WALL_H + PAD + 2:
        problems.append("the fascia band meets the wall band")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    The wall band's V is height from the ground, so splash and soil land on
    every wall alike, and the canopy shelters the top of the boards. Glass,
    signs, posters, lenses and downlights stay clean."""
    steel = (ID_FELT, ID_FLASH, ID_FRAME, ID_STEEL, ID_DOOR, ID_BIN)
    w = weathering.Weather(c, clean=(ID_GLASS, ID_SIGN, ID_SIGN_T, ID_SIGN_LIT, ID_LIGHT,
                                     ID_LAMP, ID_POSTER, ID_POSTER_A, ID_POSTER_B,
                                     ID_POSTER_C, ID_MAG_A, ID_MAG_B, ID_MAG_C),
                           steel=steel + (ID_HINGE,))
    w.grime()
    w.fade((ID_BOARD, ID_SHUTTER, ID_DOOR, ID_TIMBER))
    w.wash((ID_BOARD,))
    w.plinth(0, ATLAS, WALL_Y0, m(Z_PLINTH), (ID_PLINTH,))
    w.splash(0, ATLAS, m(Z_PLINTH), m(Z_SOFFIT), (ID_BOARD,))
    w.shelter(0, ATLAS, m(2.2), m(Z_SOFFIT), (ID_BOARD,), amount=0.06, top=WALL_H)
    # the fascia: runs from under the top flashing, dust on its drip
    w.runs(0, ATLAS, FASCIA_Y0, FASCIA_Y0 + FASCIA_H - 1.6, (ID_BOARD,), 0.08, fall=9.0)
    # the soffit: a little dust, more toward its outer edge
    x, y, rw, rh = SOFFIT
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.025 * nz("big"), (ID_SOFFIT,))
    x, y, rw, rh = DECK
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.08 * nz("big") + 0.05 * nz("blotch"),
          (ID_FELT, ID_FLASH))
    # the doors: wear at the push bar and handle, kicked-up dirt at the foot
    x, y, rw, rh = DOOR
    f = m(DOOR_FRAME)
    w.door(x + f, x + rw - f, y, y + m(Z_LEAF), (ID_FRAME,))
    w.spot(x + rw / 2.0, y + m(1.0), m(0.10), (ID_STEEL,), 0.18)
    x, y, rw, rh = STAFF
    f = m(STAFF_FRAME)
    w.door(x + f, x + rw - f, y, y + m(STAFF_LEAF_H), (ID_DOOR, ID_STEEL),
           handle=(x + rw - f - m(0.08), y + m(1.05)))
    # the glazing band: dust on the sill frame and the pass rail
    x, y, rw, rh = BAND
    w.add("D", x, x + rw, y, y + m(0.06), 0.10, (ID_FRAME, ID_STEEL))
    x, y, rw, rh = BENCH_TOP
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.06 + 0.06 * nz("blotch"), (ID_TIMBER,))
    x, y, rw, rh = SHUTTER_FACE
    w.splash(x, x + rw, y, y + rh, (ID_SHUTTER,), amount=0.08, fall=0.2, specks=0.0)
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_wall_band(c)
    paint_fascia_band(c)
    c.check_bands(BAND_IDS)
    paint_soffit(c)
    paint_deck(c)
    paint_band(c)
    paint_door(c)
    paint_staff(c)
    paint_poster(c, POSTER_A, 3)
    paint_poster(c, POSTER_B, 8)
    paint_shutters(c)
    paint_rack(c)
    paint_bench(c)
    paint_sign(c)
    paint_lamp_face(c)
    paint_patches(c)

    wear = 0.02 * atlas.noise(c, 3, 40.0) + 0.012 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, (ID_BOARD, ID_PLINTH, ID_SHUTTER))
    streak = atlas.noise(c, 7, 0.8, 40.0)
    c.shade[walls] *= 1.0 + 0.025 * streak[walls]
    mineral = np.isin(c.mid, (ID_PLINTH,))
    pores = atlas.noise(c, 9, 0.8)
    c.shade[mineral] *= 1.0 + 0.03 * pores[mineral]
    c.height[mineral] += 0.0004 * pores[mineral]
    weather(c)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    t[ID_BOARD] = pal["board"]
    t[ID_SHUTTER] = [0.94 * v for v in pal["board"]]
    return t


# ------------------------------------------------------------------ goods
GOODS = ((168, 70, 56), (64, 96, 136), (190, 160, 76), (92, 122, 84), (206, 196, 176),
         (128, 64, 96), (220, 120, 60), (70, 70, 74))
SHELVES = (1.32, 1.62, 1.92, 2.48)       # shelf boards seen through the glass


def goods(rgb, glass):
    """The kiosk's stock on its shelves, painted into the room behind the
    band's panes after glazing.rooms(): dim shelf edges and rows of packets
    in muted colours, darkened to the unlit room's level so the panes stay
    in the glazing band. Albedo only; the emission keeps its plain rooms."""
    x, y, w, h = BAND
    rs = np.random.RandomState(53)
    r0, r1 = int(np.floor(y)), int(np.ceil(y + h))
    c0, c1 = int(np.floor(x)), int(np.ceil(x + w))
    for z in SHELVES:
        yy = y + (z - Z_COUNTER) * PPM
        top = min(yy + rs.uniform(9.0, 12.0), y + h - 3)
        u = float(c0)
        while u < c1:
            cw = rs.uniform(2.0, 5.0)
            ph = rs.uniform(0.45, 1.0) * (top - yy)
            col = np.asarray(GOODS[rs.randint(len(GOODS))], np.float32)
            a0, a1 = int(u), int(min(u + cw - 0.6, c1))
            b0, b1 = int(yy + 1), int(yy + 1 + ph)
            if a1 > a0 and b1 > b0:
                sub = rgb[b0:b1, a0:a1]
                m_ = glass[b0:b1, a0:a1]
                sub[m_] = 0.45 * sub[m_] + 0.55 * (0.40 * col)
            u += cw
        b = int(round(yy))
        if r0 <= b < r1:
            m_ = glass[b:b + 1, c0:c1]
            sub = rgb[b:b + 1, c0:c1]
            sub[m_] = 0.5 * sub[m_] + 0.5 * 62.0
    return rgb


def export(out_dir, ss=atlas.SS):
    """Bake every map into *out_dir*. Glass is neutral white in the emission
    map and each pane its own lit room (glazing.night_rooms); the signs, the
    downlights and the lamp keep their own warm colours. No occupancy or
    schedule is baked in."""
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.2, depth_m=0.006)
    c.weather.dust(cav, (ID_BOARD, ID_PLINTH, ID_SHUTTER))
    rough = 0.04 * atlas.noise(c, 13, 20.0)
    path = os.path.join(out_dir, ASSET)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS,)), path + "_normal.png"),
               atlas.save(glazing.night_rooms(atlas.coverage(c, ID_GLASS) > 0,
                                              atlas.emission_colours(c, EMIT)),
                          path + "_emission.png")]
    glass = atlas.coverage(c, ID_GLASS) >= 0.5
    for v in VARIANTS:
        rgb = glazing.rooms(glass, atlas.albedo(c, lut(v), grime=0.25 * cav))
        rgb = goods(rgb, glass)
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        os.makedirs(os.path.join(here, "export"), exist_ok=True)
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
