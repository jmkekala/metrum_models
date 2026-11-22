# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
kampaamo_tile_corner.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
the plan, the heights, the opening sizes, the band rows and the region
rectangles -- so a change here cannot leave the UVs pointing at the wrong
artwork.

The atlas is a trim sheet. Three bands run the full width and tile in U:

  * the wall: glazed ceramic tile on a true 125 mm grid with its joints in
    the height channel, from the ground up -- a dark tile plinth, the accent
    tile of the shopfront storey, the white tile sign band with a single
    accent course near its top, and above the coping's drip the coping's
    own face (seen only on LOD3, where the coping is painted rather than
    modelled). Every wall, the curved band, the reveals and the corner
    recess's soffit sample it, so the tile grid runs on round the corner;
  * the coping: its face and its top, whose middle rows are PIPE_STRIP, the
    colour the wall ladder takes;
  * the roof felt's upturn on the parapet's inner face.

Everything singular -- the curved shopfront, the display windows, the shop
door, the lettered stretch of the sign band, the light box, the awning
fabric, the side and back windows, the back door, the meter cupboard, the
louvre, the roof deck and the roof fan -- gets a region of its own above the
bands. atlas.pad() fills every sample no region claims from the nearest
region's own edge.

Rasterising is scripts/atlas.py's: a canvas supersampled SS x SS per pixel
with a height channel the normal map is derived from. The lettering and the
light box's scissors are stroked here from centreline glyphs; no font file is
read.

Density is 64 texels/metre on every wall, opening and fitting, 96 on the
light box face, 16 on the roof deck (notes.md records both).

Dirt, algae and faded paint are scripts/weathering.py's fields: weather()
below says where they go on this layout. Glazed tile sheds dirt, so the
walls carry less grime than render would.
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "kampaamo_tile_corner"
ATLAS = 1024
PPM = 64.0
TILE = 0.125                # tile module, metres: 8 px, 128 tiles per atlas width
TILE_PX = TILE * PPM

# ================================================================ plan, metres
# Build frame: Z up, the street front toward -Y. The wall plan is a 10 x 9 m
# rectangle whose front-right corner is a quarter circle of radius R_OUT; at
# ground level the shopfront in that corner stands RECESS back from the wall
# line, under the sign band, which carries straight on round the curve.
HX, HY = 5.0, 4.5
R_OUT = 2.5
ARC_C = (HX - R_OUT, -HY + R_OUT)       # (2.5, -2.0)
RECESS = 0.6
R_IN = R_OUT - RECESS                   # 1.9: the curved shopfront's line
PARAPET_T = 0.3125                      # 20 px; the parapet's thickness
COPING_OUT = 0.0625                     # 4 px; the coping's oversail each side
FRONT_L = 2.0 * HX - R_OUT              # 7.5, the straight front
ARC_OUT_LEN = R_OUT * math.pi / 2.0     # 3.927 m of curved band
ARC_IN_LEN = R_IN * math.pi / 2.0       # 2.985 m of curved shopfront

# Arc segments per tier, body, band, coping and parapet alike.
ARC_SEGMENTS = (8, 6, 4, 2)

# =========================================================== heights, metres
# Every height that bounds a tile course is a whole number of courses.
Z_PLINTH = 0.375            # 3 courses of dark tile
Z_SILL = Z_PLINTH           # the display windows and the curved shopfront's
                            # kick stop at the plinth line
Z_LEAF = 2.1                # door leaf head, and the transom bar across every
                            # shopfront at the same height
Z_HEAD = 2.75               # 22 courses; shopfront head and foot of the band
Z_DECK = 3.5                # roof deck, top of the felt
Z_STRIPE = (3.75, 3.875)    # one accent course near the band's top
Z_COP0 = 4.03125            # the coping's drip
Z_PAR = 4.09375             # where the parapet stops, inside the coping
Z_COP = 4.125               # the coping's top
COP_FACE_H = Z_COP - Z_COP0  # 0.09375: 6 px

# ---------------------------------------------------------- the straight front
# s from the front-left corner. A corner pier, two display windows on a pier,
# a pier, the shop door, and a narrow pier against the corner recess's return.
DISPLAYS = ((0.5, 2.875), (3.375, 5.75))
DISPLAY_W = DISPLAYS[0][1] - DISPLAYS[0][0]          # 2.375
DOOR_SPAN = (6.25, 7.25)
DOOR_W = DOOR_SPAN[1] - DOOR_SPAN[0]                 # 1.0 opening
DOOR_FRAME = 0.03                                    # jamb frames each side
LEAF_W = DOOR_W - 2.0 * DOOR_FRAME                   # 0.94 m leaf
SHOP_DEPTH = 0.15                                    # display windows and door
                                                     # stand this far back

# The lettered stretch of the sign band: a region of its own on the front
# wall, tiled to the band's own grid so it cannot be told from the band.
SIGN_SPAN = (0.5, 5.75)
SIGN_Z = (3.0, 3.75)
SIGN_TEXT = "KAMPAAMO"
LETTER_CAP = 0.5            # metres
LETTER_BASE = 3.125
LETTER_H = 0.04             # the channel letters stand this proud of the tile

# Awnings over the display windows: closed wedges, profile (out, z).
AWN_OVER = 0.05             # past each jamb
AWN_PROFILE = ((-0.05, 3.0), (0.85, 2.45), (0.85, 2.25), (-0.05, 2.85))
AWN_SLOPE = math.hypot(0.85, 3.0 - 0.05 * 0.55 / 0.9 - 2.45)  # wall line -> front
AWN_VAL_H = 0.2

# The entrance canopy: a thin flat steel slab over the door, hung from two
# tie rods.
CANOPY = (1.75, 1.4, 0.9, 2.85, 2.95)   # centre x, width, projection, z0, z1
# and a smaller one over the staff door at the back, on the same pattern
REAR_CANOPY = (-2.0, 1.2, 0.5, 2.40, 2.48)

# The light box over the column, standing radially out of the curved band.
LIGHTBOX = (0.625, 0.8125, 0.12, 2.95)  # projection, height, thickness, z0
LIGHTBOX_PPM = 96.0
# The free-standing column under the band, at the curve's middle.
COLUMN_R = 0.11
COLUMN_AT = R_OUT - 0.25                # its axis's radius from ARC_C

# ------------------------------------------------------- the other elevations
# (width, height) of each opening, and its sill.
SIDE_WIN = (1.25, 1.375, 0.875)         # head 2.25
REAR_WIN = (0.625, 0.625, 1.5)
SERVICE_DOOR = (1.0, 2.15, 0.0)         # a 0.9 x 2.1 m leaf in 0.05 m frames
SERVICE_LEAF = (0.9, 2.1)
METER = (0.75, 1.25, 0.5)
LOUVRE = (0.625, 0.375, 2.25)
WINDOW_DEPTH = 0.12
SERVICE_DEPTH = 0.10

# ================================================================ atlas bands
PAD = 6                     # rows/columns each band or region paints beyond
                            # its own edge, so near-mip sampling stays on it

WALL_Y0, WALL_H = 6, 264            # z 0 .. Z_COP at 64 px/m
COP_Y0, COP_FACE, COP_TOP = 282, 6, 28   # face rows, then the top's width
COP_H = COP_FACE + COP_TOP
UPST_Y0, UPST_H = 328, 40           # z Z_DECK .. Z_COP
PIPE_STRIP = (COP_Y0 + COP_FACE + 6, COP_Y0 + COP_H - 6)

# ----------------------------------------------------------- unique regions
# (x, y, w, h) in atlas pixels; check_regions() proves they do not collide.
ROW_A, ROW_B = 380, 576
CURVE_R = (8, ROW_A, 191, 176)          # ARC_IN_LEN x Z_HEAD, kick included
DOOR_R = (211, ROW_A, 64, 176)          # 1.0 x 2.75 m
DISPLAY_R = (287, ROW_A, 152, 152)      # 2.375 x 2.375 m, z Z_SILL .. Z_HEAD
SERVICE_R = (451, ROW_A, 64, 138)       # 1.0 x 2.15 m
SIDE_R = (527, ROW_A, 80, 88)           # 1.25 x 1.375 m
METER_R = (619, ROW_A, 48, 80)          # 0.75 x 1.25 m
REAR_R = (679, ROW_A, 40, 40)           # 0.625 x 0.625 m
LOUVRE_R = (679, ROW_A + 52, 40, 24)    # 0.625 x 0.375 m
LIGHTBOX_R = (731, ROW_A, 60, 78)       # 0.625 x 0.8125 m at 96 px/m
COWL_R = (803, ROW_A, 64, 48)           # a roof fan's drum and hood
PIPE_R = (879, ROW_A, 24, 64)           # a vent pipe
SIGN_R = (8, ROW_B, 336, 48)            # SIGN_SPAN x SIGN_Z at 64 px/m
AWN_TOP_R = (356, ROW_B, 160, 68)       # 2.475 m across x the slope
AWN_VAL_R = (356, ROW_B + 80, 160, 13)  # 2.475 x 0.2 m
DECK_R = (528, ROW_B, 150, 134)         # the deck at 16 px/m
DECK_PPM = 16.0

PATCH_NAMES = ("blank", "metal", "metal_edge", "drip", "soffit", "column",
               "fabric_under", "awn_cheek", "box_side", "felt", "galv")
PATCHES = {n: (690 + 26 * i, ROW_B, 14, 14) for i, n in enumerate(PATCH_NAMES)}

REGIONS = {"curve": CURVE_R, "door": DOOR_R, "display": DISPLAY_R,
           "service": SERVICE_R, "side": SIDE_R, "meter": METER_R,
           "rear": REAR_R, "louvre": LOUVRE_R, "lightbox": LIGHTBOX_R,
           "cowl": COWL_R, "pipe": PIPE_R, "sign": SIGN_R,
           "awn_top": AWN_TOP_R, "awn_val": AWN_VAL_R, "deck": DECK_R}
REGIONS.update(PATCHES)

# ============================================================= material ids
ID_BLANK, ID_TILE_HI, ID_TILE_LO, ID_TILE_DK, ID_GROUT = 0, 1, 2, 3, 4
ID_METAL, ID_FELT, ID_GLASS, ID_FRAME, ID_DOOR = 5, 6, 7, 8, 9
ID_LETTER, ID_BOX_F, ID_BOX_G, ID_AWN_W, ID_AWN_S = 10, 11, 12, 13, 14
ID_PAINT_W, ID_GALV, ID_BLIND, ID_PLANT, ID_POT = 15, 16, 17, 18, 19
ID_RUBBER, ID_METER = 20, 21
TILE_IDS = (ID_TILE_HI, ID_TILE_LO, ID_TILE_DK)
# what stands behind the glass is seen through it: glass's surface, the
# room's colour, the same pane in the emission mask
BEHIND_GLASS = (ID_BLIND, ID_PLANT, ID_POT)
PANE_IDS = (ID_GLASS,) + BEHIND_GLASS

# (roughness, metallic). Glazed tile is glossy; its grout is not. The coping,
# the canopy and the doors are painted sheet, dielectric; the roof plant is
# galvanised and the only real metal.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_TILE_HI: (0.30, 0.0), ID_TILE_LO: (0.32, 0.0),
    ID_TILE_DK: (0.36, 0.0), ID_GROUT: (0.90, 0.0), ID_METAL: (0.46, 0.0),
    ID_FELT: (0.92, 0.0), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_FRAME: (0.40, 0.0), ID_DOOR: (0.50, 0.0), ID_LETTER: (0.34, 0.0),
    ID_BOX_F: (0.22, 0.0), ID_BOX_G: (0.24, 0.0), ID_AWN_W: (0.88, 0.0),
    ID_AWN_S: (0.88, 0.0), ID_PAINT_W: (0.55, 0.0), ID_GALV: (0.44, 0.72),
    ID_BLIND: (glazing.ROUGHNESS, 0.0), ID_PLANT: (glazing.ROUGHNESS, 0.0),
    ID_POT: (glazing.ROUGHNESS, 0.0), ID_RUBBER: (0.80, 0.0),
    ID_METER: (0.50, 0.0),
}

# ---------------------------------------------------------------- palettes
# One coherent treatment per instance: the band tile, the accent tile (the
# shopfront storey and the band's one course) and the awning stripe that
# follows it, and the coping's paint. The sign is the salon's and is the same
# dark red in every colour.
VARIANTS = {
    "teal_tile": {"hi": (228, 229, 224), "lo": (92, 138, 132),
                  "stripe": (88, 132, 126), "metal": (126, 130, 130),
                  "door": (96, 104, 104), "plinth": (60, 63, 63)},
    "rose_tile": {"hi": (230, 227, 222), "lo": (182, 130, 116),
                  "stripe": (172, 112, 100), "metal": (128, 126, 124),
                  "door": (104, 98, 96), "plinth": (62, 60, 60)},
    "blue_tile": {"hi": (226, 228, 228), "lo": (110, 130, 150),
                  "stripe": (100, 120, 144), "metal": (122, 126, 132),
                  "door": (92, 98, 106), "plinth": (58, 60, 64)},
    "brown_tile": {"hi": (222, 212, 188), "lo": (122, 92, 72),
                   "stripe": (126, 90, 68), "metal": (90, 78, 68),
                   "door": (92, 80, 70), "plinth": (62, 55, 50)},
}
DEFAULT_VARIANT = "teal_tile"

FIXED = {
    ID_BLANK: (52, 52, 52), ID_GROUT: (150, 150, 146), ID_FELT: (50, 50, 52),
    ID_GLASS: glazing.BASE, ID_FRAME: (214, 214, 208), ID_LETTER: (124, 38, 36),
    ID_BOX_F: (228, 226, 220), ID_BOX_G: (128, 36, 34), ID_AWN_W: (222, 219, 210),
    ID_PAINT_W: (220, 220, 214), ID_GALV: (150, 152, 154),
    ID_BLIND: (98, 96, 91), ID_PLANT: (50, 66, 42), ID_POT: (108, 70, 56),
    ID_RUBBER: (40, 40, 40), ID_METER: (156, 158, 154),
}

# A stray sample in a tiling band repeats under every surface sampling it.
BAND_IDS = {
    "WALL": ((WALL_Y0, WALL_Y0 + WALL_H), {ID_TILE_HI, ID_TILE_LO, ID_TILE_DK,
                                           ID_GROUT, ID_METAL}),
    "COPING": ((COP_Y0, COP_Y0 + COP_H), {ID_METAL}),
    "UPSTAND": ((UPST_Y0, UPST_Y0 + UPST_H), {ID_FELT, ID_METAL}),
}

# The candidate-glazing mask doubles as the emission map. Panes are neutral
# white (glazing.night_rooms() then makes each a room), and what stands behind
# the glass is lit as the pane it is seen through. The letters and the light
# box are luminous fixtures and carry their own colours, so
# scripts/validate_asset.py reads them as fixtures rather than glazing: the
# letters glow red; the box's diffuser a warm white, well off neutral, with
# its red graphics far dimmer than the field so the mark reads after dark as
# it does by day.
EMIT = {ID_GLASS: (255, 255, 255), ID_BLIND: (255, 255, 255),
        ID_PLANT: (255, 255, 255), ID_POT: (255, 255, 255),
        ID_LETTER: (226, 60, 44), ID_BOX_F: (255, 230, 200),
        ID_BOX_G: (150, 26, 20)}
# Linear RGB: a salon is lit by fluorescent tubes, as the catalog's shops are.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
TILE_FACE = 0.003    # a glazed tile's face, cushioned, proud of its joint
FRAME_H = 0.025      # aluminium window and door sections, proud of the glass
SEAM_H = 0.006       # coping joints, felt laps


# ================================================================== painting
def m(v):
    """Metres -> pixels."""
    return v * PPM


def tiles(c, x0, x1, y0, y1, u0=0.0, v0=0.0, seed=17, joint=0.55):
    """Lay the 125 mm tile grid over a rect whose ids are already painted.

    (X - x0 + u0, Y - y0 + v0) is the grid's phase, so a region painted
    elsewhere on the sheet can carry the band's own joints. Joints between
    the white and the accent tiles are grout, an id of their own, a mid grey
    that is darker than the white and close to the accent in value; the dark
    plinth is grouted dark, so its joints are only its own tile in shade.
    A joint is a little over half a texel, which supersampling draws as a
    fine line rather than a white grid. Faces are cushioned up to
    TILE_FACE, and each tile takes its own slight tone, hashed from its grid
    cell modulo the atlas width, so the band still tiles in U.
    """
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    if Y.size == 0:
        return
    gu, gv = X - x0 + u0, Y - y0 + v0
    fu, fv = np.mod(gu, TILE_PX), np.mod(gv, TILE_PX)
    mid = c.mid[sy, sx]
    on = np.isin(mid, TILE_IDS)
    dark = mid == ID_TILE_DK
    joint_m = ((fu < joint) | (fv < joint)) & on
    iu = np.floor(gu / TILE_PX).astype(np.int64) % int(ATLAS / TILE_PX)
    iv = np.floor(gv / TILE_PX).astype(np.int64)
    tone = 0.965 + 0.07 * atlas.hash_unit(iu, iv, seed)
    d = np.minimum(np.minimum(fu - joint, TILE_PX - fu),
                   np.minimum(fv - joint, TILE_PX - fv))
    face = TILE_FACE * np.clip(d / 0.9, 0.0, 1.0)
    c.mid[sy, sx] = np.where(joint_m & ~dark, ID_GROUT, mid)
    c.shade[sy, sx] = np.where(joint_m, np.where(dark, 0.70, 1.0),
                               np.where(on, tone, c.shade[sy, sx]))
    c.ao[sy, sx] = np.where(joint_m, 0.84, c.ao[sy, sx])
    c.height[sy, sx] = np.where(joint_m, 0.0, np.where(on, face, c.height[sy, sx]))


def zones(c, x0, x1, y0, z0, z1):
    """Paint the wall's tile ids for heights z0..z1 into rows from y0 (which
    stands for z0): plinth, accent storey, white band, accent course."""
    spans = ((0.0, Z_PLINTH, ID_TILE_DK), (Z_PLINTH, Z_HEAD, ID_TILE_LO),
             (Z_HEAD, Z_STRIPE[0], ID_TILE_HI), (Z_STRIPE[0], Z_STRIPE[1], ID_TILE_LO),
             (Z_STRIPE[1], Z_COP0, ID_TILE_HI))
    for a, b, mid in spans:
        lo, hi = max(a, z0), min(b, z1)
        if hi > lo:
            c.paint(x0, x1, y0 + m(lo - z0), y0 + m(hi - z0), mid=mid, shade=1.0,
                    ao=1.0, height=0.0)


# ------------------------------------------------------------------- bands
def paint_wall(c):
    """The wall band, z 0 .. Z_COP: tile to the coping's drip, the coping's
    face above it (buried in the coping on every tier that models one)."""
    y0 = WALL_Y0
    zones(c, 0, ATLAS, y0 - PAD, -PAD / PPM, Z_COP0)
    zones(c, 0, ATLAS, y0, 0.0, Z_COP0)
    tiles(c, 0, ATLAS, y0 - PAD, y0 + m(Z_COP0), v0=-PAD)
    c.paint(0, ATLAS, y0 + m(Z_COP0), y0 + WALL_H + PAD, mid=ID_METAL, shade=1.0,
            ao=0.94, height=0.0)
    # the coping's drip throws a line of occlusion on the tile under it
    c.mul(0, ATLAS, y0 + m(Z_COP0) - 3, y0 + m(Z_COP0), 0.94, ao=0.84)
    # the shopfront head's flashing along the colour change: a hairline of
    # sealant, the only trim the tile wall shows
    yh = y0 + m(Z_HEAD)
    c.mul(0, ATLAS, yh - 0.5, yh + 0.5, 0.86, ao=0.86)


def paint_coping(c):
    """Painted sheet coping: its face (rows 0..COP_FACE) and its top, with a
    folded joint every 2 m."""
    y0 = COP_Y0
    c.paint(0, ATLAS, y0 - PAD, y0 + COP_H + PAD, mid=ID_METAL, shade=1.0, ao=1.0,
            height=0.0)
    c.mul(0, ATLAS, y0 - PAD, y0 + 1, 0.86, ao=0.86)                 # drip edge
    c.bevel(0, ATLAS, y0 + COP_FACE - 1, y0 + COP_FACE + 1, 0.004, 1.0, axes="y")
    for i in range(int(ATLAS / 128) + 1):
        x = i * 128.0
        c.mul(x - 1, x + 1, y0, y0 + COP_H, 0.88, ao=0.86)
        c.lift(x - 1, x + 1, y0, y0 + COP_H, SEAM_H)
    # the top falls inward to the roof: slightly darker toward its inner edge
    sy, sx, Y, _ = c.field(0, ATLAS, y0 + COP_FACE, y0 + COP_H + PAD)
    t = np.clip((Y - y0 - COP_FACE) / COP_TOP, 0.0, 1.0)
    c.shade[sy, sx] *= 1.0 - 0.06 * t


def paint_upstand(c):
    """The roof felt's upturn on the parapet's inner face: felt from the deck
    to a termination bar under the coping, laps every metre."""
    y0 = UPST_Y0
    c.paint(0, ATLAS, y0 - PAD, y0 + UPST_H + PAD, mid=ID_FELT, shade=1.0, ao=1.0,
            height=0.0)
    yb = y0 + m(Z_COP0 - Z_DECK) - 4
    c.paint(0, ATLAS, yb, yb + 2, mid=ID_METAL, shade=0.9, ao=0.9, height=0.004)
    c.paint(0, ATLAS, yb + 2, y0 + UPST_H + PAD, mid=ID_METAL, shade=0.8, ao=0.80)
    for i in range(int(ATLAS / 64) + 1):
        x = i * 64.0
        c.mul(x, x + 1, y0, yb, 0.90, ao=0.92)
        c.lift(x, x + 1, y0, yb, SEAM_H)
    c.mul(0, ATLAS, y0, y0 + 4, 0.9, ao=0.78)          # the deck's fillet


# ----------------------------------------------------------------- regions
def _frame(c, rect, t, mid=ID_FRAME, ao=0.88, height=FRAME_H):
    """A border *t* px wide round *rect*, bevelled."""
    x, y, w, h = rect
    for a0, a1, b0, b1, axes in ((x, x + w, y, y + t, "y"), (x, x + w, y + h - t, y + h, "y"),
                                 (x, x + t, y, y + h, "x"), (x + w - t, x + w, y, y + h, "x")):
        c.paint(a0, a1, b0, b1, mid=mid, shade=1.0, ao=ao)
        c.bevel(a0, a1, b0, b1, height, 1.0, axes=axes)


def _bar(c, x0, x1, y0, y1, axes, ao=0.88, mid=ID_FRAME, height=FRAME_H):
    c.paint(x0, x1, y0, y1, mid=mid, shade=1.0, ao=ao)
    c.bevel(x0, x1, y0, y1, height, 1.0, axes=axes)


def _plant(c, cx, y_sill, scale, seed, clip):
    """A pot plant standing on a sill, behind the glass: a tapered pot and a
    clump of leaves, drawn as discs and strokes. *clip* = (x0, x1, y0, y1)
    keeps it inside its pane."""
    rs = np.random.RandomState(seed)
    x0, x1, y0, y1 = clip
    ph, pw = 0.20 * scale * PPM, 0.17 * scale * PPM

    def inside(X, Y):
        return (X >= x0) & (X < x1) & (Y >= y0) & (Y < y1)

    def test_pot(X, Y):
        t = np.clip((Y - y_sill) / ph, 0.0, 1.0)
        half = pw * (0.36 + 0.14 * t)
        return (np.abs(X - cx) <= half) & (Y >= y_sill) & (Y <= y_sill + ph) & inside(X, Y)
    c.shape(cx - pw, cx + pw, y_sill, y_sill + ph, test_pot, mid=ID_POT, shade=1.0, ao=0.9)
    top = y_sill + ph
    for _ in range(int(9 * scale) + 5):
        a = rs.uniform(0.15, math.pi - 0.15)
        ln = rs.uniform(0.18, 0.42) * scale * PPM
        bx, by = cx + math.cos(a) * ln, top + math.sin(a) * ln * 0.9
        w = rs.uniform(2.2, 3.6) * scale
        c.stroke((cx, top), (bx, by), w, mid=ID_PLANT,
                 shade=rs.uniform(0.75, 1.25), clip=(x0, y0, x1 - x0, y1 - y0))
        c.disc(bx, by, w * 0.9, mid=ID_PLANT, shade=rs.uniform(0.8, 1.3))


def _blinds(c, gx0, gx1, gy0, gy1, spans, seed):
    """Vertical blinds hanging in a pane, over the fractions *spans* of its
    width: slats 0.09 m wide, each turned a little differently, so a gap of
    room shows between some of them."""
    rs = np.random.RandomState(seed)
    pitch = 6.0
    for f0, f1 in spans:
        a0, a1 = gx0 + f0 * (gx1 - gx0), gx0 + f1 * (gx1 - gx0)
        x = a0
        while x + pitch <= a1 + 0.5:
            turn = rs.uniform(0.55, 1.0)
            w = pitch * turn
            sh = rs.uniform(0.88, 1.05)
            c.paint(x, x + w, gy0, gy1, mid=ID_BLIND, shade=sh, ao=1.0, height=0.0)
            # each slat darkens toward its turned edge and its foot
            c.mul(x + w - 1.0, x + w, gy0, gy1, 0.85)
            sy, sx, Y, _ = c.field(x, x + w, gy0, gy1)
            c.shade[sy, sx] *= 0.86 + 0.14 * np.clip((Y - gy0) / max(1.0, gy1 - gy0), 0, 1)
            x += pitch
        # the head rail the slats hang from
        c.paint(a0, a1, gy1 - 3, gy1, mid=ID_BLIND, shade=0.92, ao=0.9)


def paint_display(c):
    """A display window, 2.375 x 2.375 m from the plinth to the shopfront
    head: white aluminium frame, one big light below a transom at the door's
    leaf head, two top lights over it. Vertical blinds hang in the big light,
    drawn to both sides, and pot plants stand on the sill in front of them."""
    x, y, w, h = DISPLAY_R
    c.paint(x, x + w, y, y + h, mid=ID_GLASS, shade=1.0, ao=1.0, height=0.0)
    t = m(0.05)
    yt = y + m(Z_LEAF - Z_SILL)
    gx0, gx1, gy0 = x + t, x + w - t, y + m(0.07)
    _blinds(c, gx0, gx1, gy0 + m(0.06), yt - 2, ((0.0, 0.30), (0.74, 1.0)), 41)
    _plant(c, x + w * 0.20, gy0, 1.15, 7, (gx0, gx1, gy0, yt))
    _plant(c, x + w * 0.52, gy0, 0.85, 8, (gx0, gx1, gy0, yt))
    _plant(c, x + w * 0.83, gy0, 1.0, 9, (gx0, gx1, gy0, yt))
    _frame(c, DISPLAY_R, t)
    _bar(c, x, x + w, y, y + m(0.07), "y", ao=0.80)                 # sill rail
    _bar(c, x, x + w, yt - m(0.03), yt + m(0.03), "y")              # transom
    _bar(c, x + w / 2 - m(0.025), x + w / 2 + m(0.025), yt, y + h, "x")
    c.mul(x, x + w, y + h - m(0.20), y + h - t, 1.0, ao=0.88)       # the head's shade


def paint_curve(c):
    """The curved shopfront, unrolled along its own arc: a tiled kick to the
    plinth line, then four tall lights between slim mullions, a transom at the
    door's leaf head and a top light over each. A plant or two on the sill."""
    x, y, w, h = CURVE_R
    zones(c, x - PAD, x + w + PAD, y, 0.0, Z_SILL)          # the plinth's dark tile
    tiles(c, x - PAD, x + w + PAD, y, y + m(Z_SILL), u0=-PAD)
    c.paint(x, x + w, y + m(Z_SILL), y + h, mid=ID_GLASS, shade=1.0, ao=1.0, height=0.0)
    pane = w / 4.0
    yt = y + m(Z_LEAF)
    sill = y + m(Z_SILL + 0.06)
    _plant(c, x + pane * 0.5, sill, 1.1, 11, (x, x + w, sill, yt))
    _plant(c, x + pane * 3.4, sill, 0.9, 12, (x, x + w, sill, yt))
    _bar(c, x, x + w, y + m(Z_SILL), sill, "y", ao=0.80)
    _bar(c, x, x + w, yt - m(0.03), yt + m(0.03), "y")
    _bar(c, x, x + w, y + h - m(0.06), y + h, "y", ao=0.84)
    for k in range(5):
        cx = x + k * pane
        hw = m(0.025) if 0 < k < 4 else m(0.05)
        a0, a1 = max(x, cx - hw), min(x + w, cx + hw)
        _bar(c, a0, a1, y + m(Z_SILL), y + h, "x")
    c.mul(x, x + w, y + h - m(0.30), y + h - m(0.06), 1.0, ao=0.86)


def paint_door(c):
    """The salon's door: a glazed leaf 0.94 x 2.1 m in white aluminium, a
    transom bar and a transom light to the shopfront head, a long pull."""
    x, y, w, h = DOOR_R
    c.paint(x, x + w, y, y + h, mid=ID_FRAME, shade=1.0, ao=0.9, height=FRAME_H)
    fr = m(DOOR_FRAME)
    lx0, lx1 = x + fr, x + w - fr
    yl = y + m(Z_LEAF)
    # transom light, between the bar and the head frame
    c.paint(lx0, lx1, yl + m(0.06), y + h - m(0.04), mid=ID_GLASS, ao=1.0, height=0.0)
    _bar(c, x, x + w, yl, yl + m(0.06), "y", ao=0.84)
    # the leaf: stiles and rails round a vision panel, a deep bottom rail
    c.paint(lx0, lx1, y, yl, mid=ID_FRAME, ao=0.9)
    c.bevel(lx0, lx1, y, yl, FRAME_H, 1.0)
    c.paint(lx0 + m(0.08), lx1 - m(0.08), y + m(0.22), yl - m(0.08), mid=ID_GLASS,
            ao=1.0, height=0.0)
    c.mul(lx0, lx0 + 1, y, yl, 0.70, ao=0.70)                      # hinge-side gap
    c.mul(lx1 - 1, lx1, y, yl, 0.70, ao=0.70)
    c.paint(lx0, lx1, y, y + m(0.03), mid=ID_RUBBER, ao=0.8, height=0.0)  # sweep
    px = lx1 - m(0.12)
    c.paint(px - m(0.02), px + m(0.02), y + m(0.75), y + m(1.45), mid=ID_GALV,
            shade=1.0, ao=0.9, height=0.035)


def door_pull():
    x, y, w, _h = DOOR_R
    return x + w - m(DOOR_FRAME) - m(0.12), y + m(1.1)


def paint_service_door(c):
    """The back door: a painted steel leaf in a steel frame, a kick plate and
    a lever."""
    x, y, w, h = SERVICE_R
    c.paint(x, x + w, y, y + h, mid=ID_DOOR, shade=0.92, ao=0.86, height=0.02)
    lw, lh = SERVICE_LEAF
    lx0 = x + (w - m(lw)) / 2.0
    lx1 = lx0 + m(lw)
    c.paint(lx0, lx1, y, y + m(lh), mid=ID_DOOR, shade=1.0, ao=0.95, height=0.0)
    c.mul(lx0, lx0 + 1, y, y + m(lh), 0.7, ao=0.7)
    c.mul(lx1 - 1, lx1, y, y + m(lh), 0.7, ao=0.7)
    c.mul(lx0, lx1, y + m(lh) - 1, y + m(lh), 0.7, ao=0.7)
    for yy in (0.7, 1.4):                                           # pressed panels
        c.mul(lx0 + 5, lx1 - 5, y + m(yy) - 1, y + m(yy), 0.88, ao=0.9)
        c.lift(lx0 + 5, lx1 - 5, y + m(yy) - 1, y + m(yy), -0.003)
    c.paint(lx0, lx1, y, y + m(0.25), mid=ID_GALV, shade=0.9, ao=0.9, height=0.002)
    c.paint(lx1 - m(0.16), lx1 - m(0.04), y + m(1.02), y + m(1.06), mid=ID_GALV,
            ao=0.85, height=0.03)


def paint_side_window(c):
    """A side window, 1.25 x 1.375 m: white aluminium, a narrow opening light
    and a fixed one, and the metal sill flashing at its foot."""
    x, y, w, h = SIDE_R
    c.paint(x, x + w, y, y + h, mid=ID_GLASS, shade=1.0, ao=1.0, height=0.0)
    _frame(c, SIDE_R, m(0.06))
    mx = x + m(0.48)
    _bar(c, mx - m(0.03), mx + m(0.03), y, y + h, "x")
    _frame(c, (x + m(0.06), y + m(0.06), mx - m(0.03) - x - m(0.06), h - m(0.12)),
           m(0.04), height=FRAME_H * 0.7)
    c.paint(x, x + w, y, y + m(0.05), mid=ID_METAL, shade=0.95, ao=0.9, height=0.0)
    c.mul(x, x + w, y + h - m(0.15), y + h - m(0.06), 1.0, ao=0.88)


def paint_rear_window(c):
    x, y, w, h = REAR_R
    c.paint(x, x + w, y, y + h, mid=ID_GLASS, shade=1.0, ao=1.0, height=0.0)
    _frame(c, REAR_R, m(0.06))
    c.paint(x, x + w, y, y + m(0.05), mid=ID_METAL, shade=0.95, ao=0.9, height=0.0)


def paint_meter(c):
    """The electricity meter cupboard: a painted steel door in a frame, a
    louvre near its foot, a lock, and the reading window."""
    x, y, w, h = METER_R
    c.paint(x, x + w, y, y + h, mid=ID_METER, shade=0.9, ao=0.86, height=0.015)
    c.paint(x + 2, x + w - 2, y + 2, y + h - 2, mid=ID_METER, shade=1.0, ao=0.96,
            height=0.0)
    c.paint(x + m(0.2), x + w - m(0.2), y + m(0.85), y + m(1.05), mid=ID_RUBBER,
            shade=0.9, ao=0.9, height=-0.002)
    for i in range(4):
        ly = y + m(0.12) + i * m(0.06)
        c.paint(x + m(0.15), x + w - m(0.15), ly, ly + m(0.03), mid=ID_METER,
                shade=0.6, ao=0.7)
        sy, sx, Y, _ = c.field(x + m(0.15), x + w - m(0.15), ly, ly + m(0.03))
        c.height[sy, sx] = 0.008 * (1.0 - (Y - ly) / m(0.03))
    c.disc(x + w - m(0.1), y + m(0.62), 1.6, mid=ID_GALV, ao=0.8, height=0.01)


def paint_louvre(c):
    x, y, w, h = LOUVRE_R
    c.paint(x, x + w, y, y + h, mid=ID_METAL, shade=0.95, ao=0.86, height=0.012)
    ix0, ix1, iy0, iy1 = x + 3, x + w - 3, y + 3, y + h - 3
    c.paint(ix0, ix1, iy0, iy1, mid=ID_RUBBER, shade=1.0, ao=0.7, height=-0.01)
    for i in range(int((iy1 - iy0) / m(0.06)) + 1):
        ly = iy0 + i * m(0.06)
        c.paint(ix0, ix1, ly, min(iy1, ly + m(0.035)), mid=ID_METAL, shade=0.95, ao=0.86)
        sy, sx, Y, _ = c.field(ix0, ix1, ly, min(iy1, ly + m(0.035)))
        c.height[sy, sx] = 0.01 * (1.0 - (Y - ly) / m(0.035))


def _taper(c, p0, p1, w0, w1, mid):
    """A segment whose width runs from *w0* at p0 to *w1* at p1."""
    (ax, ay), (bx, by) = p0, p1
    r = max(w0, w1)
    dx, dy = bx - ax, by - ay
    ll = max(dx * dx + dy * dy, 1e-9)

    def test(X, Y):
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / ll, 0.0, 1.0)
        dist = np.hypot(X - (ax + t * dx), Y - (ay + t * dy))
        return dist <= 0.5 * (w0 + (w1 - w0) * t)
    c.shape(min(ax, bx) - r, max(ax, bx) + r, min(ay, by) - r,
            max(ay, by) + r, test, mid=mid)


def _scissors(c, cx, cy, s, mid, field):
    """Open scissors, points up, in a unit *s* px across: two tapered blades
    crossing at a pivot, each running on below it as a shank into a finger
    ring. Strokes and discs only; no real business's device."""
    k = s / 96.0
    px, py = cx, cy + 2.0 * k
    for side in (-1.0, 1.0):
        dx, dy = side * 12.6 * k, 29.4 * k
        tip = (px + dx, py + dy)
        tail = (px - 0.27 * dx, py - 0.27 * dy)
        _taper(c, tail, tip, 8.0 * k, 2.2 * k, mid)
        ring = (cx - side * 12.0 * k, cy - 22.0 * k)
        c.stroke(tail, (ring[0] + side * 3.0 * k, ring[1] + 7.6 * k), 5.0 * k, mid=mid)
        c.disc(ring[0], ring[1], 9.0 * k, mid=mid, inner=5.0 * k)
    c.disc(px, py, 1.8 * k, mid=field)


def paint_lightbox(c):
    """The light box's face, 0.625 x 0.8125 m at 96 px/m: a white diffuser in
    a dark red border, the scissors over a comb."""
    x, y, w, h = LIGHTBOX_R
    c.paint(x, x + w, y, y + h, mid=ID_BOX_G, shade=1.0, ao=0.9, height=0.01)
    b = 4
    c.paint(x + b, x + w - b, y + b, y + h - b, mid=ID_BOX_F, shade=1.0, ao=1.0,
            height=0.0)
    s = w * 0.86
    _scissors(c, x + w / 2.0, y + h * 0.60, s, ID_BOX_G, ID_BOX_F)
    # the comb: a spine and its teeth
    cy = y + h * 0.18
    c.paint(x + w * 0.2, x + w * 0.8, cy + 5, cy + 8, mid=ID_BOX_G)
    for i in range(12):
        tx = x + w * 0.22 + i * (w * 0.56 / 11.0)
        c.paint(tx - 0.6, tx + 0.6, cy, cy + 6, mid=ID_BOX_G)
    # the tubes behind the diffuser: brightest down the middle
    sy, sx, _, X = c.field(x + b, x + w - b, y + b, y + h - b)
    t = (X - (x + w / 2.0)) / (w / 2.0)
    c.shade[sy, sx] *= 1.0 - 0.05 * t * t


def paint_sign(c):
    """The lettered stretch of the white band over the display windows: the
    band's own tile, on its own grid phase, and KAMPAAMO in dark red block
    capitals standing LETTER_H proud."""
    x, y, w, h = SIGN_R
    zones(c, x - PAD, x + w + PAD, y - PAD, SIGN_Z[0] - PAD / PPM, SIGN_Z[1] + PAD / PPM)
    tiles(c, x - PAD, x + w + PAD, y - PAD, y + h + PAD,
          u0=m(SIGN_SPAN[0]) - PAD, v0=m(SIGN_Z[0]) - PAD)
    cap, weight = m(LETTER_CAP), m(0.10)
    tracking = 0.20
    tw = text_width(SIGN_TEXT, cap, tracking, weight)
    text(c, SIGN_TEXT, x + (w - tw) / 2.0, y + m(LETTER_BASE - SIGN_Z[0]), cap,
         weight, ID_LETTER, tracking, height=LETTER_H)


def text(c, word, x, y, cap, weight, mid, tracking=0.16, height=None):
    """Set *word* with its baseline at y and its left edge at x, in the
    stroked centreline letterforms of GLYPHS. No font file is read."""
    cx, prev, ratio = float(x), None, weight / float(cap)
    for ch in word:
        cx += _step(prev, ch, tracking, ratio) * cap
        for poly in GLYPHS[ch][1]:
            for (ax, ay), (bx, by) in zip(poly, poly[1:]):
                c.stroke((cx + ax * cap, y + ay * cap), (cx + bx * cap, y + by * cap),
                         weight, mid=mid, shade=1.0, ao=1.0, height=height)
        prev = ch
    return cx + GLYPHS[prev][0] * cap - x if prev else 0.0


def _arc(cx, cy, rx, ry, a0, a1, n=16):
    a = np.radians(np.linspace(a0, a1, n + 1))
    return list(zip(cx + rx * np.cos(a), cy + ry * np.sin(a)))


# A plain block sans, drawn as stroked centrelines on a unit em: y = 0 the
# baseline, y = 1 the cap line, the advance first. Only the sign's letters.
GLYPHS = {
    "A": (0.70, [[(0.00, 0.00), (0.35, 1.00), (0.70, 0.00)],
                 [(0.12, 0.33), (0.58, 0.33)]]),
    "K": (0.62, [[(0.00, 0.00), (0.00, 1.00)],
                 [(0.62, 1.00), (0.00, 0.40)],
                 [(0.20, 0.59), (0.64, 0.00)]]),
    "M": (0.84, [[(0.00, 0.00), (0.00, 1.00), (0.42, 0.34), (0.84, 1.00),
                  (0.84, 0.00)]]),
    "O": (0.82, [_arc(0.41, 0.50, 0.41, 0.50, 0, 360, 36)]),
    "P": (0.62, [[(0.00, 0.00), (0.00, 1.00), (0.32, 1.00)]
                 + _arc(0.32, 0.75, 0.30, 0.25, 90, -90, 12)
                 + [(0.00, 0.50)]]),
}


def _step(prev, ch, tracking, ratio):
    if prev is None:
        return 0.0
    return GLYPHS[prev][0] + tracking + ratio


def text_width(word, cap, tracking=0.16, weight=0.0):
    ratio = weight / float(cap)
    w = sum(_step(word[i - 1], word[i], tracking, ratio) for i in range(1, len(word)))
    return (w + GLYPHS[word[-1]][0]) * cap


def paint_awning(c):
    """Awning cloth: white with muted stripes in the accent colour, 0.25 m
    a repeat, running down the slope; the valance the same stripes under a
    hem. The cloth sags a little between the arms."""
    for (x, y, w, h), hem in ((AWN_TOP_R, False), (AWN_VAL_R, True)):
        c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, mid=ID_AWN_W, shade=1.0,
                ao=1.0, height=0.0)
        sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
        ph = np.mod(X - x, 16.0)
        stripe = (ph >= 9.0) & (ph < 15.0)
        c.mid[sy, sx] = np.where(stripe, ID_AWN_S, ID_AWN_W)
        c.height[sy, sx] = np.where(np.abs(ph - 9.0) < 0.6, -0.002, 0.0)
        if hem:
            c.mul(x - PAD, x + w + PAD, y - PAD, y + 2, 0.85, ao=0.85)
            c.mul(x - PAD, x + w + PAD, y + h - 2, y + h + PAD, 0.9, ao=0.9)
        else:
            # the cloth sags between the arms at each end and the middle
            for fx in (0.0, 0.5, 1.0):
                ax = x + fx * w
                c.mul(ax - 1.5, ax + 1.5, y - PAD, y + h + PAD, 0.92, ao=0.9)
            sag = 0.5 - 0.5 * np.cos(2.0 * np.pi * np.mod((X - x) / (w / 2.0), 1.0))
            c.shade[sy, sx] *= 1.0 - 0.05 * sag
    weave = atlas.noise(c, 31, 0.6, 0.6)
    sy, sx = c.sl(AWN_TOP_R[0] - PAD, AWN_TOP_R[0] + AWN_TOP_R[2] + PAD,
                  AWN_TOP_R[1] - PAD, AWN_VAL_R[1] + AWN_VAL_R[3] + PAD)
    c.shade[sy, sx] *= 1.0 + 0.015 * weave[sy, sx]


def paint_deck(c):
    """Bitumen felt on the flat deck, at 16 px/m: one-metre rolls, shallow
    ponding, a worn walking line from the ladder to the fan."""
    x, y, w, h = DECK_R
    c.paint(x, x + w, y, y + h, mid=ID_FELT, shade=1.0, ao=1.0, height=0.0)
    for i in range(1, int(h / DECK_PPM) + 1):
        yy = y + i * DECK_PPM
        c.mul(x, x + w, yy - 0.5, yy + 0.5, 0.90, ao=0.92)
    rs = np.random.RandomState(5)
    for _ in range(14):
        cx, cy = rs.uniform(x + 8, x + w - 8), rs.uniform(y + 8, y + h - 8)
        c.disc(cx, cy, rs.uniform(4, 11), None, rs.uniform(0.93, 0.99), 0.97)
    c.mul(x, x + w, y, y + 3, 0.92, ao=0.86)
    c.mul(x, x + w, y + h - 3, y + h, 0.92, ao=0.86)
    c.mul(x, x + 3, y, y + h, 0.92, ao=0.86)
    c.mul(x + w - 3, x + w, y, y + h, 0.92, ao=0.86)


def paint_plant_room(c):
    """The roof fan's drum and hood, and a vent pipe: galvanised."""
    x, y, w, h = COWL_R
    c.paint(x, x + w, y, y + h, mid=ID_GALV, shade=1.0, ao=0.95, height=0.0)
    c.paint(x, x + w, y + h - 12, y + h, mid=ID_GALV, shade=0.86, ao=0.82, height=0.02)
    c.mul(x, x + w, y + h - 13, y + h - 11, 0.62, ao=0.68)
    for i in range(1, 6):
        xx = x + w * i / 6.0
        c.mul(xx - 1, xx + 1, y, y + h - 12, 0.90, ao=0.88)
        c.lift(xx - 1, xx + 1, y, y + h - 12, -0.003)
    c.paint(x, x + w, y, y + 5, mid=ID_GALV, shade=0.8, ao=0.8)       # the curb
    x, y, w, h = PIPE_R
    c.paint(x, x + w, y, y + h, mid=ID_GALV, shade=0.92, ao=0.92)
    sy, sx, _, X = c.field(x, x + w, y, y + h)
    u = 2.0 * (X - x) / w - 1.0
    c.height[sy, sx] = 0.03 * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(x, x + w, y + h - 5, y + h, mid=ID_GALV, shade=0.72, ao=0.72)


def paint_patches(c):
    spec = {"blank": (ID_BLANK, 1.0, 1.0), "metal": (ID_METAL, 1.0, 0.96),
            "metal_edge": (ID_METAL, 0.88, 0.9), "drip": (ID_METAL, 0.72, 0.72),
            "soffit": (ID_PAINT_W, 0.86, 0.78), "column": (ID_PAINT_W, 1.0, 0.95),
            "fabric_under": (ID_AWN_W, 0.70, 0.66), "awn_cheek": (ID_AWN_W, 0.90, 0.88),
            "box_side": (ID_METAL, 0.92, 0.9), "felt": (ID_FELT, 0.9, 0.9),
            "galv": (ID_GALV, 0.95, 0.92)}
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x, x + w, y, y + h, mid=mid, shade=sh, ao=ao, height=0.0)


# ------------------------------------------------------------------ checks
def check_regions():
    """Fail the bake if two regions overlap, collide with the bands, or run
    off the sheet, gutters included."""
    bands_top = UPST_Y0 + UPST_H + PAD
    names = sorted(REGIONS)
    problems = []
    for i, a in enumerate(names):
        ax, ay, aw, ah = REGIONS[a]
        if ax - PAD < 0 or ay - PAD < 0 or ax + aw + PAD > ATLAS or ay + ah + PAD > ATLAS:
            problems.append("%s has no room for its gutter" % a)
        if ay - PAD < bands_top:
            problems.append("%s overlaps the tiling bands" % a)
        for b in names[i + 1:]:
            bx, by, bw, bh = REGIONS[b]
            if (ax - 2 * PAD < bx + bw and bx - 2 * PAD < ax + aw
                    and ay - 2 * PAD < by + bh and by - 2 * PAD < ay + ah):
                problems.append("%s and %s are closer than two gutters" % (a, b))
    prev = 0
    for y0, h in ((WALL_Y0, WALL_H), (COP_Y0, COP_H), (UPST_Y0, UPST_H)):
        if y0 - PAD < prev:
            problems.append("band at %d has no gutter below it" % y0)
        prev = y0 + h + PAD
    if abs(WALL_H - m(Z_COP)) > 1e-6 or abs(UPST_H - m(Z_COP - Z_DECK)) > 1e-6:
        problems.append("a band's height disagrees with the heights it stands for")
    if abs(COP_FACE - m(COP_FACE_H)) > 1e-6 or abs(COP_TOP - m(PARAPET_T + 2 * COPING_OUT)) > 1e-6:
        problems.append("the coping band disagrees with the coping")
    if abs(SIGN_R[2] - m(SIGN_SPAN[1] - SIGN_SPAN[0])) > 1e-6 or \
            abs(SIGN_R[3] - m(SIGN_Z[1] - SIGN_Z[0])) > 1e-6:
        problems.append("the sign region is not its stretch of wall at 64 px/m")
    if abs(DISPLAY_R[2] - m(DISPLAY_W)) > 1e-6 or abs(DISPLAY_R[3] - m(Z_HEAD - Z_SILL)) > 1e-6:
        problems.append("the display region is not the display window")
    if abs(CURVE_R[2] - m(ARC_IN_LEN)) > 0.5:
        problems.append("the curve region is not the curved shopfront's length")
    for z in (Z_PLINTH, Z_HEAD, Z_STRIPE[0], Z_STRIPE[1], SIGN_Z[0], SIGN_Z[1]):
        if abs(z / TILE - round(z / TILE)) > 1e-9:
            problems.append("z %.4f is not on a tile course" % z)
    if problems:
        raise ValueError("atlas layout: " + "; ".join(sorted(set(problems))))


# ----------------------------------------------------------------- the bake
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    The wall band's V is height from the ground on every wall, so the
    plinth's soil and the splash above it land alike all round, and the runs
    from the coping's drip hang from its top. Glazed tile sheds dirt, so the
    film over everything is lighter than on render. The salon's sign, the
    light box and what is behind the glass stay clean."""
    steel = (ID_METAL, ID_FELT, ID_GALV, ID_DOOR, ID_METER)
    w = weathering.Weather(c, clean=PANE_IDS + (ID_LETTER, ID_BOX_F, ID_BOX_G),
                           steel=steel)
    w.grime(amount=0.02)
    w.fade((ID_AWN_W, ID_AWN_S, ID_DOOR, ID_METER, ID_METAL), amount=0.08)
    w.wash((ID_TILE_HI, ID_TILE_LO, ID_GROUT), amount=0.008)
    w.plinth(0, ATLAS, WALL_Y0, WALL_Y0 + m(Z_PLINTH), (ID_TILE_DK, ID_GROUT))
    w.splash(0, ATLAS, WALL_Y0 + m(Z_PLINTH), WALL_Y0 + m(Z_HEAD),
             (ID_TILE_LO, ID_GROUT), amount=0.10, specks=0.10)
    # runs from the coping's drip, short: tile does not hold them far down
    w.runs(0, ATLAS, WALL_Y0 + m(Z_STRIPE[1]), WALL_Y0 + m(Z_COP0),
           (ID_TILE_HI, ID_GROUT), 0.14, fall=m(0.10))
    # the curved shopfront's kick and the door's foot
    x, y, cw, _ = CURVE_R
    w.splash(x - PAD, x + cw + PAD, y, y + m(Z_SILL) + 6, (ID_TILE_LO, ID_GROUT, ID_FRAME),
             amount=0.14)
    x, y, dw, _ = DOOR_R
    w.splash(x, x + dw, y, y + m(0.6), (ID_FRAME, ID_RUBBER), amount=0.16, fall=0.12,
             specks=0.0)
    w.spot(*door_pull(), m(0.10), (ID_FRAME, ID_GALV))
    x, y, sw, sh = SERVICE_R
    w.door(x, x + sw, y, y + sh, (ID_DOOR, ID_GALV),
           handle=(x + sw - m(0.15), y + m(1.04)))
    for rect in (SIDE_R, REAR_R):
        x, y, rw, _ = rect
        w.add("D", x, x + rw, y, y + m(0.05), 0.14, (ID_METAL,))
    x, y, mw, mh = METER_R
    w.splash(x, x + mw, y, y + mh, (ID_METER,), amount=0.10, fall=0.2, specks=0.0)
    w.runs(x, x + mw, y, y + mh, (ID_METER,), 0.08, fall=mh / 3.0)
    # the deck: dirt where it ponds and along the walking line
    x, y, dw, dh = DECK_R
    w.add("D", x, x + dw, y, y + dh, lambda Y, X, nz: 0.10 * nz("big") + 0.06 * nz("blotch"),
          (ID_FELT,))
    for x, y, rw, rh in (COWL_R, PIPE_R):
        w.runs(x, x + rw, y, y + rh, (ID_GALV,), 0.10, fall=rh / 2.0)
    # the awning cloth greys toward its valance, where the rain leaves it
    x, y, aw, ah = AWN_TOP_R
    w.add("D", x - PAD, x + aw + PAD, y - PAD, y + ah + PAD,
          lambda Y, X, nz: 0.05 * np.clip(1.0 - (Y - y) / ah, 0, 1) + 0.03 * nz("blotch"),
          (ID_AWN_W, ID_AWN_S))
    x, y, aw, ah = AWN_VAL_R
    w.add("D", x - PAD, x + aw + PAD, y - PAD, y + ah + PAD, 0.06, (ID_AWN_W, ID_AWN_S))
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_wall(c)
    paint_coping(c)
    paint_upstand(c)
    c.check_bands(BAND_IDS)
    paint_curve(c)
    paint_door(c)
    paint_display(c)
    paint_service_door(c)
    paint_side_window(c)
    paint_rear_window(c)
    paint_meter(c)
    paint_louvre(c)
    paint_lightbox(c)
    paint_sign(c)
    paint_awning(c)
    paint_deck(c)
    paint_plant_room(c)
    paint_patches(c)

    # glazed tile: a faint broad unevenness, no more; sheet and felt grain
    wear = 0.012 * atlas.noise(c, 3, 40.0) + 0.008 * atlas.noise(c, 4, 8.0)
    tiled = np.isin(c.mid, TILE_IDS + (ID_GROUT,))
    c.shade[tiled] *= 1.0 + wear[tiled]
    sheeted = np.isin(c.mid, (ID_METAL, ID_FELT, ID_GALV, ID_DOOR, ID_METER))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    soft = atlas.noise(c, 11, 20.0)
    c.shade[sheeted] *= 1.0 + 0.014 * grain[sheeted] + 0.02 * soft[sheeted]

    weather(c)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    t[ID_TILE_HI] = pal["hi"]
    t[ID_TILE_LO] = pal["lo"]
    t[ID_TILE_DK] = pal["plinth"]
    t[ID_AWN_S] = pal["stripe"]
    t[ID_METAL] = pal["metal"]
    t[ID_DOOR] = pal["door"]
    return t


def _door_mask(shape):
    door = np.zeros(shape, bool)
    dx, dy, dw, dh = DOOR_R
    door[dy:dy + dh, dx:dx + dw] = True
    return door


def export(out_dir, ss=atlas.SS):
    """Glazing in the emission map is neutral, painted as rooms; the letters
    and the light box carry their own colours (EMIT). No occupancy is baked
    in. The door's vision panel and transom are one room (merge=8)."""
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.006)
    c.weather.dust(cav, (ID_GROUT,), amount=0.10)
    rough = 0.03 * atlas.noise(c, 13, 20.0)
    path = os.path.join(out_dir, ASSET)
    cover = atlas.coverage(c, PANE_IDS)
    door = _door_mask(cover.shape)
    emit = atlas.emission_colours(c, EMIT)
    emit = glazing.night_rooms((cover > 0) & door, emit, merge=8)
    emit = glazing.night_rooms((cover > 0) & ~door, emit)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=PANE_IDS), path + "_normal.png"),
               atlas.save(emit, path + "_emission.png")]
    glass = atlas.coverage(c, ID_GLASS) >= 0.5
    for v in VARIANTS:
        rgb = atlas.albedo(c, lut(v), grime=0.25 * cav)
        rgb = glazing.rooms(glass & door, rgb, merge=8)
        rgb = glazing.rooms(glass & ~door, rgb)
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
        panes = cover >= 0.999
        print("%s: panes sRGB mean %.1f" % (v, rgb[panes].mean()))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(os.path.basename(p))
    else:
        paint()
        print("atlas layout and bands check out")
