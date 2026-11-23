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

  * the wall: glazed ceramic tile, 250 x 125 mm in half bond, with its
    joints in the height channel, from the ground up -- a dark tile plinth, the accent
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
bands, and so does each door's concrete floor slab (scripts/door_floor.py). atlas.pad() fills every sample no region claims from the nearest
region's own edge.

Rasterising is scripts/atlas.py's: a canvas supersampled SS x SS per pixel
with a height channel the normal map is derived from. The lettering is set in
the catalog's stroked alphabet (scripts/lettering.py) and the light box's
scissors are stroked here; no font file is read.

Density is 64 texels/metre on every wall, opening and fitting, 96 on the
light box face, 32 on the roof deck (notes.md records both).

Each display window and the curved shopfront has a region of its own, so
the three rooms behind the glass differ: their blinds, pot plants and
goods are room content, painted in the albedo under glass roughness and
lit only as the pane in the emission.

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
import door_floor as DF  # noqa: E402
import glazing  # noqa: E402
import lettering  # noqa: E402
import weathering  # noqa: E402

ASSET = "kampaamo_tile_corner"
ATLAS = 1024
PPM = 64.0
TILE = 0.125                # tile course, metres: 8 px
TILE_L = 0.25               # tile length, metres: 16 px, 64 tiles per atlas width,
                            # laid in half bond, so the courses read as lines
TILE_PX = TILE * PPM
TILE_LPX = TILE_L * PPM

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

# Arc segments per tier, body, band, coping and parapet alike. LOD3 keeps
# three, so the corner still reads round at the last switch; it has no
# column or light box to need a vertex at the curve's middle.
ARC_SEGMENTS = (8, 6, 4, 3)

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
# The free-standing column under the band, at the curve's middle, on a
# short steel shoe at the pavement.
COLUMN_R = 0.11
COLUMN_AT = R_OUT - 0.25                # its axis's radius from ARC_C
SHOE = (0.15, 0.15)                     # the shoe's radius and height

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
ROW_A, ROW_B, ROW_C = 380, 576, 722
CURVE_R = (8, ROW_A, 191, 176)          # ARC_IN_LEN x Z_HEAD, kick included
DOOR_R = (211, ROW_A, 64, 176)          # 1.0 x 2.75 m
DISPLAY_R = (287, ROW_A, 152, 152)      # the left display window, 2.375 x
                                        # 2.375 m, z Z_SILL .. Z_HEAD
DISPLAY2_R = (320, ROW_C, 152, 152)     # the right one: its own room
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
DECK_R = (8, ROW_C, 300, 268)           # the deck, 9.375 x 8.375 m at 32 px/m
DECK_PPM = 32.0
# The concrete floor slabs (scripts/door_floor.py), each unfolded at 64 px/m:
# U along the wall from the opening's left side, V up the slab's 0.02 m
# nosing from the ground and then back across its top from the wall plane.
# - "shop": the shop door's reveal, back to the door (SHOP_DEPTH);
# - "staff": the staff door's reveal at the back, back to its door
#   (SERVICE_DEPTH).
# The corner recess has no slab, by the owner's decision: a consumer paves
# the forecourt into it, so its ground is the consumer's.
FLOORS = {"shop": DF.Floor(520, 760, DOOR_W, SHOP_DEPTH, falloff=0.06, spread=0.30),
          "staff": DF.Floor(520, 790, SERVICE_DOOR[0], SERVICE_DEPTH)}

PATCH_NAMES = ("blank", "metal", "metal_edge", "drip", "soffit", "column",
               "fabric_under", "awn_cheek", "box_side", "felt", "galv")
PATCHES = {n: (690 + 26 * i, ROW_B, 14, 14) for i, n in enumerate(PATCH_NAMES)}

REGIONS = {"curve": CURVE_R, "door": DOOR_R, "display": DISPLAY_R,
           "display2": DISPLAY2_R, "service": SERVICE_R, "side": SIDE_R, "meter": METER_R,
           "rear": REAR_R, "louvre": LOUVRE_R, "lightbox": LIGHTBOX_R,
           "cowl": COWL_R, "pipe": PIPE_R, "sign": SIGN_R,
           "awn_top": AWN_TOP_R, "awn_val": AWN_VAL_R, "deck": DECK_R}
REGIONS.update(PATCHES)
REGIONS.update({"floor_" + k: f.rect for k, f in FLOORS.items()})

# ============================================================= material ids
ID_BLANK, ID_TILE_HI, ID_TILE_LO, ID_TILE_DK, ID_GROUT = 0, 1, 2, 3, 4
ID_METAL, ID_FELT, ID_GLASS, ID_FRAME, ID_DOOR = 5, 6, 7, 8, 9
ID_LETTER, ID_BOX_F, ID_BOX_G, ID_AWN_W, ID_AWN_S = 10, 11, 12, 13, 14
ID_PAINT_W, ID_GALV, ID_BLIND, ID_PLANT, ID_POT = 15, 16, 17, 18, 19
ID_RUBBER, ID_METER, ID_GROUT_HI, ID_FLOWER, ID_GOODS = 20, 21, 22, 23, 24
ID_FLOOR = 25               # the cast concrete floor slabs (scripts/door_floor.py)
TILE_IDS = (ID_TILE_HI, ID_TILE_LO, ID_TILE_DK)
GROUT_IDS = (ID_GROUT, ID_GROUT_HI)
# what stands behind the glass is seen through it: glass's surface, the
# room's colour, the same pane in the emission mask
BEHIND_GLASS = (ID_BLIND, ID_PLANT, ID_POT, ID_FLOWER, ID_GOODS)
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
    ID_METER: (0.50, 0.0), ID_GROUT_HI: (0.90, 0.0),
    ID_FLOWER: (glazing.ROUGHNESS, 0.0), ID_GOODS: (glazing.ROUGHNESS, 0.0),
    ID_FLOOR: DF.SURFACE,
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
                   "door": (92, 80, 70), "plinth": (62, 55, 50),
                   # a light joint on brown half bond reads as brick
                   "grout": (112, 102, 92)},
}
DEFAULT_VARIANT = "teal_tile"

FIXED = {
    ID_BLANK: (52, 52, 52), ID_GROUT: (156, 156, 150), ID_GROUT_HI: (194, 194, 188),
    ID_FELT: (50, 50, 52),
    ID_GLASS: glazing.BASE, ID_FRAME: (214, 214, 208), ID_LETTER: (124, 38, 36),
    ID_BOX_F: (228, 226, 220), ID_BOX_G: (128, 36, 34), ID_AWN_W: (222, 219, 210),
    ID_PAINT_W: (220, 220, 214), ID_GALV: (150, 152, 154),
    ID_BLIND: (98, 96, 91), ID_PLANT: (50, 60, 43), ID_POT: (104, 72, 60),
    ID_FLOWER: (146, 98, 100), ID_GOODS: (124, 118, 112),
    ID_RUBBER: (40, 40, 40), ID_METER: (156, 158, 154),
    ID_FLOOR: DF.COLOUR,
}

# A stray sample in a tiling band repeats under every surface sampling it.
BAND_IDS = {
    "WALL": ((WALL_Y0, WALL_Y0 + WALL_H), {ID_TILE_HI, ID_TILE_LO, ID_TILE_DK,
                                           ID_GROUT, ID_GROUT_HI, ID_METAL}),
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
        ID_FLOWER: (255, 255, 255), ID_GOODS: (255, 255, 255),
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


def tiles(c, x0, x1, y0, y1, u0=0.0, v0=0.0, seed=17, joint=0.42):
    """Lay the 250 x 125 mm tiles, in half bond, over a rect whose ids are
    already painted.

    (X - x0 + u0, Y - y0 + v0) is the grid's phase, so a region painted
    elsewhere on the sheet can carry the band's own joints; every other
    course is shifted half a tile, so the bed joints run on as lines and the
    perpends stagger. Joints are grout, ids of their own: a light grey in
    the white band (ID_GROUT_HI), a mid grey a little lighter than the
    accent tile in the shopfront storey (ID_GROUT). The dark plinth is
    grouted dark, so its joints are only its own tile in shade. A joint is
    0.42 texel, 6.5 mm, a little over a real 4-5 mm joint so that
    supersampling still draws it as a fine line. Faces are cushioned up to
    TILE_FACE, and each tile takes its own slight tone, hashed from its cell
    modulo the atlas width, so the band still tiles in U.
    """
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    if Y.size == 0:
        return
    gu, gv = X - x0 + u0, Y - y0 + v0
    iv = np.floor(gv / TILE_PX).astype(np.int64)
    gu = gu + np.mod(iv, 2) * (TILE_LPX / 2.0)
    fu, fv = np.mod(gu, TILE_LPX), np.mod(gv, TILE_PX)
    mid = c.mid[sy, sx]
    on = np.isin(mid, TILE_IDS)
    dark = mid == ID_TILE_DK
    joint_m = ((fu < joint) | (fv < joint)) & on
    iu = np.floor(gu / TILE_LPX).astype(np.int64) % int(ATLAS / TILE_LPX)
    tone = 0.97 + 0.06 * atlas.hash_unit(iu, iv, seed)
    d = np.minimum(np.minimum(fu - joint, TILE_LPX - fu),
                   np.minimum(fv - joint, TILE_PX - fv))
    face = TILE_FACE * np.clip(d / 0.9, 0.0, 1.0)
    grout = np.where(mid == ID_TILE_HI, ID_GROUT_HI, ID_GROUT)
    c.mid[sy, sx] = np.where(joint_m & ~dark, grout, mid)
    c.shade[sy, sx] = np.where(joint_m, np.where(dark, 0.78, 1.0),
                               np.where(on, tone, c.shade[sy, sx]))
    c.ao[sy, sx] = np.where(joint_m, 0.88, c.ao[sy, sx])
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


def _pot(c, cx, y_sill, h, w, shade):
    """A tapered pot *h* x *w* metres on the sill, its rim a shade lighter."""
    ph, pw = m(h), m(w)

    def test(X, Y):
        t = np.clip((Y - y_sill) / ph, 0.0, 1.0)
        return (np.abs(X - cx) <= 0.5 * pw * (0.74 + 0.26 * t)) & (Y >= y_sill) & \
            (Y <= y_sill + ph)
    c.shape(cx - pw, cx + pw, y_sill, y_sill + ph, test, mid=ID_POT, shade=shade, ao=0.92)
    c.paint(cx - 0.5 * pw, cx + 0.5 * pw, y_sill + ph - 1.0, y_sill + ph, mid=ID_POT,
            shade=shade * 1.08)
    return y_sill + ph


def _leaves(c, rs, cx, cy, rx, ry, n, r=(0.7, 1.2), shade=(0.72, 1.08), mid=ID_PLANT):
    """A mound of *n* small leaves in an ellipse round (cx, cy): darker
    toward its foot and its inside, as foliage occludes itself."""
    for _ in range(n):
        a, t = rs.uniform(0.0, 2.0 * math.pi), math.sqrt(rs.uniform(0.0, 1.0))
        lx, ly = cx + rx * t * math.cos(a), cy + ry * t * math.sin(a)
        up = np.clip((ly - (cy - ry)) / max(2.0 * ry, 1e-6), 0.0, 1.0)
        sh = rs.uniform(*shade) * (0.86 + 0.14 * up) * (1.0 - 0.10 * (1.0 - t))
        c.disc(lx, ly, rs.uniform(*r), mid=mid, shade=sh)


def _plant(c, kind, cx, y_sill, size, seed):
    """A modest pot plant behind the glass, standing on the sill: a pot and
    foliage in a muted green, *size* metres tall overall. Kinds:

      bush      a rounded mound of small leaves
      upright   a few stiff tapering blades (a snake plant)
      trailing  a low mound with strands hanging over the pot's rim
      flowering a small mound with a few dusty-rose flowers on it
    """
    rs = np.random.RandomState(seed)
    pot_h = min(0.13, 0.42 * size)
    top = _pot(c, cx, y_sill, pot_h, 0.75 * pot_h + 0.03, rs.uniform(0.82, 1.05))
    fh = m(size - pot_h)                       # the foliage's height, px
    if kind == "upright":
        for _ in range(rs.randint(4, 7)):
            bx = cx + rs.uniform(-1.2, 1.2)
            tip = (bx + rs.uniform(-0.35, 0.35) * fh, top + rs.uniform(0.6, 1.0) * fh)
            _taper(c, (bx, top - 0.5), tip, rs.uniform(1.4, 1.9), 0.45, ID_PLANT,
                   shade=rs.uniform(0.80, 1.12))
        return
    rx = 0.5 * m(size) * rs.uniform(0.85, 1.15)
    if kind == "trailing":
        ry = 0.42 * fh
        for side in (-1.0, 1.0, rs.choice((-1.0, 1.0))):
            x, y = cx + side * 0.6 * m(0.75 * pot_h + 0.03), top
            for _ in range(rs.randint(4, 8)):
                x += side * rs.uniform(0.0, 0.9)
                y -= rs.uniform(1.0, 1.6)
                if y < y_sill + 1.0:
                    break
                c.disc(x, y, rs.uniform(0.6, 0.95), mid=ID_PLANT,
                       shade=rs.uniform(0.70, 0.95))
    else:
        ry = 0.55 * fh
    n = int(2.2 * rx * ry / 1.0) + 6
    _leaves(c, rs, cx, top + 0.85 * ry, rx, ry, n)
    if kind == "flowering":
        for _ in range(rs.randint(4, 8)):
            a, t = rs.uniform(0.2, math.pi - 0.2), rs.uniform(0.35, 0.95)
            c.disc(cx + rx * t * math.cos(a), top + 0.85 * ry + ry * t * math.sin(a),
                   rs.uniform(0.6, 0.9), mid=ID_FLOWER, shade=rs.uniform(0.85, 1.05))


def _goods(c, x0, y_sill, n, seed):
    """A row of *n* hair-care bottles on the sill, 0.12-0.22 m tall, each
    with a darker cap, from *x0* rightward."""
    rs = np.random.RandomState(seed)
    x = x0
    for _ in range(n):
        w, h = m(rs.uniform(0.045, 0.07)), m(rs.uniform(0.12, 0.22))
        sh = rs.uniform(0.55, 1.1)
        c.rounded_rect(x, y_sill, w, h, min(1.0, w / 2.0), mid=ID_GOODS, shade=sh)
        c.paint(x + 0.25 * w, x + 0.75 * w, y_sill + h, y_sill + h + m(0.025),
                mid=ID_GOODS, shade=0.45)
        x += w + m(rs.uniform(0.01, 0.03))
    return x


def _venetian(c, gx0, gx1, gy_top, drop, seed):
    """A venetian blind let down *drop* px from the head of a pane: light
    slats 0.0625 m apart, tilted half open, so each slat has a thin dark
    line of room under it, and a heavier bottom rail."""
    rs = np.random.RandomState(seed)
    gy0 = gy_top - drop
    c.paint(gx0, gx1, gy0, gy_top, mid=ID_BLIND, shade=0.92, ao=1.0, height=0.0)
    pitch = 4.0
    y = gy_top
    while y - pitch > gy0 + 1.0:
        y -= pitch
        c.mul(gx0, gx1, y, y + 0.9, 0.62)
        c.mul(gx0, gx1, y + 0.9, y + 2.0, rs.uniform(0.96, 1.04))
    c.paint(gx0, gx1, gy0, gy0 + 1.5, mid=ID_BLIND, shade=0.72, ao=0.9)
    c.paint(gx0, gx1, gy_top - 2.0, gy_top, mid=ID_BLIND, shade=0.80, ao=0.88)


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


def paint_display(c, rect, room):
    """A display window, 2.375 x 2.375 m from the plinth to the shopfront
    head: white aluminium frame, one big light below a transom at the door's
    leaf head, two top lights over it. The two windows are two rooms:

      left   vertical blinds drawn to both sides, a snake plant, a small
             flowering plant and a low bush on the sill;
      right  a venetian blind let down two fifths of the big light, a bush,
             a row of hair-care bottles and a trailing plant.
    """
    x, y, w, h = rect
    c.paint(x, x + w, y, y + h, mid=ID_GLASS, shade=1.0, ao=1.0, height=0.0)
    t = m(0.05)
    yt = y + m(Z_LEAF - Z_SILL)
    gx0, gx1, gy0 = x + t, x + w - t, y + m(0.07)
    if room == "left":
        _blinds(c, gx0, gx1, gy0 + m(0.06), yt - 2, ((0.0, 0.20), (0.83, 1.0)), 41)
        _plant(c, "upright", x + w * 0.30, gy0, 0.42, 7)
        _plant(c, "flowering", x + w * 0.49, gy0, 0.28, 8)
        _plant(c, "bush", x + w * 0.68, gy0, 0.26, 9)
    else:
        top = yt - m(0.03)
        _venetian(c, gx0, gx1, top, 0.40 * (top - gy0), 43)
        _plant(c, "bush", x + w * 0.20, gy0, 0.36, 21)
        _goods(c, x + w * 0.44, gy0, 5, 22)
        _plant(c, "trailing", x + w * 0.80, gy0, 0.26, 23)
    _frame(c, rect, t)
    _bar(c, x, x + w, y, y + m(0.07), "y", ao=0.80)                 # sill rail
    _bar(c, x, x + w, yt - m(0.03), yt + m(0.03), "y")              # transom
    _bar(c, x + w / 2 - m(0.025), x + w / 2 + m(0.025), yt, y + h, "x")
    c.mul(x, x + w, y + h - m(0.20), y + h - t, 1.0, ao=0.88)       # the head's shade


def paint_curve(c):
    """The curved shopfront, unrolled along its own arc: a tiled kick to the
    plinth line, then four tall lights between slim mullions, a transom at the
    door's leaf head and a top light over each. A third room again: a small
    trailing plant in the first light, a snake plant in the third, and a
    venetian blind let a third of the way down the last."""
    x, y, w, h = CURVE_R
    zones(c, x - PAD, x + w + PAD, y, 0.0, Z_SILL)          # the plinth's dark tile
    tiles(c, x - PAD, x + w + PAD, y, y + m(Z_SILL), u0=-PAD)
    c.paint(x, x + w, y + m(Z_SILL), y + h, mid=ID_GLASS, shade=1.0, ao=1.0, height=0.0)
    pane = w / 4.0
    yt = y + m(Z_LEAF)
    sill = y + m(Z_SILL + 0.06)
    _plant(c, "trailing", x + pane * 0.45, sill, 0.24, 11)
    _plant(c, "upright", x + pane * 2.6, sill, 0.34, 12)
    top = yt - m(0.03)
    _venetian(c, x + pane * 3.0, x + w, top, 0.33 * (top - sill), 13)
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


def _taper(c, p0, p1, w0, w1, mid, shade=None):
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
            max(ay, by) + r, test, mid=mid, shade=shade)


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
    tw = lettering.text_width(SIGN_TEXT, cap, tracking, weight)
    lettering.text(c, SIGN_TEXT, x + (w - tw) / 2.0, y + m(LETTER_BASE - SIGN_Z[0]), cap,
                   weight, ID_LETTER, tracking, shade=1.0, ao=1.0, height=LETTER_H)


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
            # a binding tape in the accent colour along the valance's foot,
            # stitched over the stripes, and the fold at its top
            c.paint(x - PAD, x + w + PAD, y - PAD, y + 2.5, mid=ID_AWN_S, shade=0.90,
                    ao=0.92)
            c.lift(x - PAD, x + w + PAD, y - PAD, y + 2.5, 0.002)
            c.mul(x - PAD, x + w + PAD, y + 2.5, y + 3.0, 0.88, ao=0.9)
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


def deck_px(bx, by):
    """Build-frame plan metres -> atlas pixels on the deck region."""
    x, y, _w, _h = DECK_R
    return (x + (bx + HX - PARAPET_T) * DECK_PPM, y + (by + HY - PARAPET_T) * DECK_PPM)


# Painted on the deck, in build-frame plan metres: the two roof drains the
# deck falls to, the roof hatch's lid (x0, y0, x1, y1), and the walking line
# from the wall ladder's head to the fan.
DRAINS = ((-3.2, -2.9), (0.6, 2.8))
HATCH = (-3.85, 2.30, -3.05, 3.10)
WALK = ((3.0, 3.95), (1.2, 2.6), (-1.2, 1.7))


def paint_deck(c):
    """Bitumen felt on the flat deck, at 32 px/m: one-metre rolls lapped
    along X with staggered end laps, shallow ponding, two roof drains with a
    dark grate in a galvanised ring, and the roof hatch's lid in its curb."""
    x, y, w, h = DECK_R
    k = DECK_PPM
    c.paint(x, x + w, y, y + h, mid=ID_FELT, shade=1.0, ao=1.0, height=0.0)
    rs = np.random.RandomState(5)
    for i in range(int(h / k) + 1):
        yy = y + i * k
        if i:
            c.mul(x, x + w, yy - 0.5, yy + 0.6, 0.84, ao=0.88)
            c.lift(x, x + w, yy, yy + 2.5, SEAM_H)
        x_end = x + rs.uniform(0.0, 5.0) * k
        while x_end < x + w:
            c.mul(x_end - 0.5, x_end + 0.6, yy, min(y + h, yy + k), 0.88, ao=0.9)
            c.lift(x_end, x_end + 2.5, yy, min(y + h, yy + k), SEAM_H)
            x_end += rs.uniform(4.0, 6.0) * k
    for _ in range(16):
        cx, cy = rs.uniform(x + 12, x + w - 12), rs.uniform(y + 12, y + h - 12)
        c.disc(cx, cy, rs.uniform(6, 18), None, rs.uniform(0.93, 0.99), 0.97)
    for bx, by in DRAINS:
        px, py = deck_px(bx, by)
        c.disc(px, py, 0.20 * k, mid=ID_GALV, shade=0.80, ao=0.80, height=0.004)
        c.disc(px, py, 0.13 * k, mid=ID_RUBBER, shade=0.70, ao=0.60, height=-0.01)
        for a in range(4):
            ang = a * math.pi / 4.0
            dx, dy = math.cos(ang) * 0.12 * k, math.sin(ang) * 0.12 * k
            c.stroke((px - dx, py - dy), (px + dx, py + dy), 0.8, mid=ID_GALV, shade=0.7)
    hx0, hy0 = deck_px(HATCH[0], HATCH[1])
    hx1, hy1 = deck_px(HATCH[2], HATCH[3])
    c.paint(hx0, hx1, hy0, hy1, mid=ID_GALV, shade=0.78, ao=0.84, height=0.0)
    c.bevel(hx0, hx1, hy0, hy1, 0.03, 1.5)
    c.paint(hx0 + 2.5, hx1 - 2.5, hy0 + 2.5, hy1 - 2.5, mid=ID_GALV, shade=0.96, ao=1.0)
    c.mul(hx0 + 2.5, hx1 - 2.5, hy1 - 4.0, hy1 - 3.0, 0.75, ao=0.85)   # hinge line
    c.mul(hx0, hx1, hy0 - 2.0, hy0, 0.85, ao=0.80)                      # curb's foot
    c.mul(x, x + w, y, y + 5, 0.92, ao=0.86)
    c.mul(x, x + w, y + h - 5, y + h, 0.92, ao=0.86)
    c.mul(x, x + 5, y, y + h, 0.92, ao=0.86)
    c.mul(x + w - 5, x + w, y, y + h, 0.92, ao=0.86)


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
    atlas.paint_patches(c, PATCHES, spec, bleed=0)


# ------------------------------------------------------------------ checks
def check_regions():
    """Fail the bake if two regions overlap, collide with the bands, or run
    off the sheet, gutters included."""
    problems = atlas.region_problems(REGIONS, ATLAS, edge=PAD, gap=2 * PAD,
                                     bands_top=UPST_Y0 + UPST_H + PAD, band_gap=PAD)
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
    for r in (DISPLAY_R, DISPLAY2_R):
        if abs(r[2] - m(DISPLAY_W)) > 1e-6 or abs(r[3] - m(Z_HEAD - Z_SILL)) > 1e-6:
            problems.append("a display region is not the display window")
    if abs(DECK_R[2] - DECK_PPM * 2 * (HX - PARAPET_T)) > 1e-6 or \
            abs(DECK_R[3] - DECK_PPM * 2 * (HY - PARAPET_T)) > 1e-6:
        problems.append("the deck region is not the deck at DECK_PPM")
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
    w.wash((ID_TILE_HI, ID_TILE_LO) + GROUT_IDS, amount=0.008)
    w.plinth(0, ATLAS, WALL_Y0, WALL_Y0 + m(Z_PLINTH), (ID_TILE_DK, ID_GROUT))
    w.splash(0, ATLAS, WALL_Y0 + m(Z_PLINTH), WALL_Y0 + m(Z_HEAD),
             (ID_TILE_LO, ID_GROUT), amount=0.10, specks=0.10)
    # runs from the coping's drip, short: tile does not hold them far down
    w.runs(0, ATLAS, WALL_Y0 + m(Z_STRIPE[1]), WALL_Y0 + m(Z_COP0),
           (ID_TILE_HI, ID_GROUT_HI), 0.14, fall=m(0.10))
    # the curved shopfront's kick and the door's foot
    x, y, cw, _ = CURVE_R
    w.splash(x - PAD, x + cw + PAD, y, y + m(Z_SILL) + 6, (ID_TILE_LO, ID_GROUT, ID_FRAME),
             amount=0.14)
    x, y, dw, _ = DOOR_R
    w.splash(x, x + dw, y, y + m(0.6), (ID_FRAME, ID_RUBBER), amount=0.16, fall=0.12,
             specks=0.0)
    w.spot(*door_pull(), m(0.10), (ID_FRAME, ID_GALV))
    # the floor slabs: trodden-in dirt, blotchy
    for f in FLOORS.values():
        DF.weather(w, f, ID_FLOOR, bleed=PAD)
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
    # silt dried round each drain, where the deck ponds last
    for bx, by in DRAINS:
        px, py = deck_px(bx, by)
        r = 0.7 * DECK_PPM
        w.add("D", px - 2 * r, px + 2 * r, py - 2 * r, py + 2 * r,
              lambda Y, X, nz, px=px, py=py, r=r: 0.16 * np.exp(
                  -((X - px) ** 2 + (Y - py) ** 2) / r ** 2) * (0.6 + 0.4 * nz("blotch")),
              (ID_FELT, ID_GALV))
    # the walking line from the ladder's head to the fan, scuffed paler
    pts = [deck_px(*p) for p in WALK]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        def scuff(Y, X, nz, ax=ax, ay=ay, bx=bx, by=by):
            dx, dy = bx - ax, by - ay
            t = np.clip(((X - ax) * dx + (Y - ay) * dy) / (dx * dx + dy * dy), 0.0, 1.0)
            d = np.hypot(X - (ax + t * dx), Y - (ay + t * dy))
            return 0.10 * np.exp(-(d / (0.28 * DECK_PPM)) ** 2) * (0.5 + 0.5 * nz("blotch"))
        r = 0.6 * DECK_PPM
        w.add("F", min(ax, bx) - r, max(ax, bx) + r, min(ay, by) - r, max(ay, by) + r,
              scuff, (ID_FELT,))
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
    for f in FLOORS.values():
        DF.paint(c, f, ID_FLOOR, bleed=PAD)
    paint_display(c, DISPLAY_R, "left")
    paint_display(c, DISPLAY2_R, "right")
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
    tiled = np.isin(c.mid, TILE_IDS + GROUT_IDS)
    c.shade[tiled] *= 1.0 + wear[tiled]
    sheeted = np.isin(c.mid, (ID_METAL, ID_FELT, ID_GALV, ID_DOOR, ID_METER))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    soft = atlas.noise(c, 11, 20.0)
    c.shade[sheeted] *= 1.0 + 0.014 * grain[sheeted] + 0.02 * soft[sheeted]
    DF.grain(c, ID_FLOOR, atlas.noise(c, 9, 0.7))

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
    t[ID_GROUT] = pal.get("grout", FIXED[ID_GROUT])
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
    c.weather.dust(cav, GROUT_IDS, amount=0.10)
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
