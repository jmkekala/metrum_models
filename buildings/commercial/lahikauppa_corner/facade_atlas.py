# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
lahikauppa_corner.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
storey heights, band rows, opening sizes, region rectangles -- so a change here
cannot leave the UVs pointing at the wrong artwork.

The atlas is a trim sheet. Four bands run the full width and tile horizontally:
the brick, the white render, the shopfront glazing and the white eave soffit.
The brick and the render bands each start at the ground and carry the concrete
plinth in their own bottom 24 rows, so a wall is two courses of region rather
than three and no opening has to straddle a band edge. Everything singular --
the entrance, the sign, the goods door, the roof deck, the plant -- gets a
region of its own above them. Bands are separated by four
rows of padding, and atlas.pad() fills every sample no region claims from the
nearest region's own edge, so base-level and mip sampling stays on the right
artwork.

Rasterising is scripts/atlas.py's: a canvas supersampled SS x SS per pixel,
with a height channel the normal map is derived from, so the lettering, the
badge and the plant's discs come out anti-aliased like everything else
(numpy and scipy; Pillow to save).

Density is 64 texels/metre on everything a customer stands in front of. The
back-of-house surfaces are deliberately coarser -- the goods door at 40, the
roof deck at about 5 -- because they are seen from a van bay or from the air.
notes.md lists each deviation.

Dirt, algae, rust and faded paint are scripts/weathering.py's fields: weather()
below says where they go on this layout, and each variant resolves them
against its own colours.
"""

import os
import sys

import numpy as np

# Windows are painted the same way across the whole catalog, and every atlas is
# rasterised the same way, so both live in scripts/ and not here; see
# CLAUDE.md's Style Direction and Texture Requirements.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import brickwork  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "lahikauppa_corner"
ATLAS = 1024
PPM = 64.0

# ------------------------------------------------------------ vertical layout
# Every height is a whole number of texels at 64 px/m, so a band's rows and the
# metres it stands for never drift apart.
Z_PLINTH = 0.375        # 24 px; cast concrete base under every wall
Z_BRICK = 3.5           # 224 px; top of the brickwork
Z_WALL = 4.3125         # 276 px; top of the wall, where the eave soffit springs
# The roof deck is the high side and the eave falls away from it, outward and
# down, so snow pushed off the deck goes over the edge instead of piling behind
# a parapet. That is what the type does and it is why the eave is this long.
Z_DECK = 4.5625         # 292 px; flat roof deck, top surface, at the wall line
Z_EAVE_B = 3.8125       # 244 px; outer bottom edge of the eave, 0.5 m lower
Z_EAVE_T = 4.0625       # 260 px; outer top edge; the fascia is 0.25 m of it
EAVE_OUT = 1.5          # how far the eave projects past the wall
EAVE_FALL = Z_WALL - Z_EAVE_B                             # 0.5 m of fall
EAVE_RUN = float(np.hypot(EAVE_OUT, EAVE_FALL))           # 1.5811 m of slope
WALL_INTO_ROOF = 0.125  # walls run this far into the roof slab, which trims them

# the shopfront
Z_SILL = Z_PLINTH       # the glazing stands on the plinth
Z_TRANSOM = 2.3125      # 148 px; door-leaf head, and the transom bar across
Z_HEAD = 3.25           # 208 px; shopfront head

# the sign over the entrance, planted on the eave's outer slope
SIGN_W = 4.75
SIGN_H = 1.65625        # 106 px
SIGN_T = 0.3
Z_SIGN = 4.0625        # its foot, a little under the slope it stands on

# ---------------------------------------------------------------- openings
# (width, height, casing width at the sides, below, above)
OPENINGS = {
    "staff_window": (1.2, 1.3, 0.09, 0.09, 0.09),
    "service_door": (1.1, 2.125, 0.1, 0.0, 0.1),
    "goods_door": (3.2, 3.2, 0.1, 0.0, 0.1),
}
REVEAL_DEPTH = {"staff_window": 0.14, "service_door": 0.12, "goods_door": 0.18}
GLAZE_DEPTH = 0.20      # the shopfront sits this far back in its opening
DOOR_DEPTH = 0.70       # the entrance is set back further again, into a lobby

# ------------------------------------------------------------------- bands
BRICK_Y0, BRICK_H = 0, 224        # z 0 .. Z_BRICK, plinth in the bottom 24
STUCCO_Y0, STUCCO_H = 228, 276    # z 0 .. Z_WALL, plinth in the bottom 24
SHOP_Y0, SHOP_H = 508, 184        # z Z_SILL .. Z_HEAD
SOF_Y0, SOF_H = 696, 56           # the eave's slope, compressed across it
PAD = 2                 # rows each band paints beyond its own edge

COURSE = brickwork.COURSE      # brick course pitch: 5 px, 40 courses over the brickwork
BRICK_L = brickwork.BRICK_L    # stretcher length: 16 px, 64 bricks per atlas width
SHOP_BAY = 2.0          # 128 px; the shopfront's structural mullion pitch

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels. check_regions() asserts they neither overlap nor run
# off the sheet; the metres each one stands for are beside it.
DOOR_UNIT = (4, 760, 205, 208)        # 3.203125 x 3.25 m at 64 px/m: ground to head
DOOR_UNIT_W = 205 / PPM
PLACARD = (547, 760, 304, 106)        # SIGN_W x SIGN_H at 64 px/m
GOODS_DOOR = (871, 760, 136, 132)     # 3.4 x 3.3 m at 40 px/m
BAY_CEILING = (547, 870, 112, 74)     # 7 x 5 m of loading-bay ceiling
ROOF_DECK = (213, 760, 330, 184)      # 32 x 18 m of membrane at ~10 px/m
SERVICE_DOOR = (788, 948, 44, 74)     # 1.3 x 2.225 m at ~33 px/m
STAFF_WINDOW = (836, 948, 68, 74)     # 1.38 x 1.48 m at ~49 px/m
AHU_SIDE = (268, 948, 96, 43)         # 2.0 x 0.9 m of plant casing at 48 px/m
AHU_TOP = (368, 948, 96, 64)          # 2.0 x 1.33 m of plant lid
COWL = (468, 948, 60, 48)             # a roof fan's drum and hood
PIPE = (532, 948, 24, 32)             # a vent pipe

ITEM_REGION = {"staff_window": STAFF_WINDOW, "service_door": SERVICE_DOOR,
               "goods_door": GOODS_DOOR}

PATCH_NAMES = ("blank", "reveal_dark", "reveal_light", "cap", "parapet",
               "fascia", "column", "sign_edge", "deck_edge", "wall_top",
               "plinth_top")
PATCHES = {n: (560 + 20 * i, 1002, 16, 16) for i, n in enumerate(PATCH_NAMES)}


def item_size_px(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    x, y, rw, rh = ITEM_REGION[kind]
    return rw, rh


def item_size_m(kind):
    """The casing rectangle an opening occupies on the wall, in metres."""
    w, h, cs, cb, ct = OPENINGS[kind]
    return w + 2.0 * cs, h + cb + ct


# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_STUCCO, ID_ROOF, ID_EAVE = 0, 1, 2, 3, 4, 5
ID_TRIM, ID_GLASS, ID_DOOR, ID_SIGN, ID_SIGN_M, ID_METAL, ID_STEEL = \
    6, 7, 8, 9, 10, 11, 12
ID_FRAME = 13           # the shopfront's anodised aluminium, light not dark

# (roughness, metallic). Painted steel stays dielectric -- the paint is what
# the light sees. The mullions are anodised aluminium and the roof plant is
# galvanised, so those two are the only real metals on the building.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_BRICK: (0.84, 0.0),
    ID_STUCCO: (0.78, 0.0), ID_ROOF: (0.94, 0.0), ID_EAVE: (0.42, 0.0),
    ID_TRIM: (0.36, 0.70), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_DOOR: (0.48, 0.0), ID_SIGN: (0.14, 0.0), ID_SIGN_M: (0.16, 0.0),
    ID_METAL: (0.46, 0.72), ID_STEEL: (0.44, 0.0),
    ID_FRAME: (0.30, 0.75),
}

# ---------------------------------------------------------------- palettes
# One coherent treatment per instance: the brick changes, and the render and
# the roof move with it, but never within one building. The sign is the shop's
# identity and stays the same blue in every colour.
VARIANTS = {
    "red_brick": {"brick": (138, 82, 66), "stucco": (222, 218, 208),
                  "roof": (52, 52, 54), "trim": (58, 58, 62),
                  "eave": (232, 231, 226), "door": (86, 88, 90)},
    "brown_brick": {"brick": (120, 84, 68), "stucco": (216, 211, 200),
                    "roof": (54, 53, 52), "trim": (54, 54, 56),
                    "eave": (228, 226, 220), "door": (84, 84, 86)},
    "yellow_brick": {"brick": (188, 170, 132), "stucco": (232, 230, 224),
                     "roof": (56, 55, 54), "trim": (60, 58, 58),
                     "eave": (236, 235, 231), "door": (88, 88, 88)},
    "grey_brick": {"brick": (138, 132, 124), "stucco": (226, 225, 222),
                   "roof": (52, 54, 56), "trim": (56, 58, 60),
                   "eave": (233, 233, 231), "door": (86, 88, 90)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (150, 148, 142),
    ID_SIGN: (206, 212, 218), ID_SIGN_M: (22, 56, 118),
    ID_METAL: (146, 150, 152), ID_STEEL: (92, 94, 96),
    ID_BLANK: (52, 52, 52), ID_FRAME: (148, 150, 152),
}

# A stray pixel in a tiling band is not a local blemish: every surface that
# samples the band repeats it.
BAND_IDS = {
    "BRICK": ((0, 226), {ID_BRICK, ID_PLINTH}),
    "STUCCO": ((226, 506), {ID_STUCCO, ID_PLINTH}),
    "SHOPFRONT": ((506, 694), {ID_GLASS, ID_FRAME}),
    "SOFFIT": ((694, 754), {ID_EAVE, ID_TRIM}),
}

# The candidate-glazing mask doubles as the emission map. Glass is neutral
# white, so scripts/validate_asset.py can pick it out as glazing; the sign is
# a luminous fixture rather than a window and is written in its own colours.
# A lit sign box is a bright diffuser with the graphics printed on it, and
# print transmits far less light than the blank panel does. Giving the blue the
# same order of emission as the panel washed the wordmark out at night -- it
# glowed nearly as hard as the ground it sat on. Roughly twenty times dimmer is
# what makes it read as deep blue on a lit panel after dark, which is how the
# sign reads by day too.
EMIT = {ID_GLASS: (255, 255, 255), ID_SIGN: (176, 198, 222),
        ID_SIGN_M: (16, 44, 118)}
# Linear RGB. A shop's interior is fluorescent, not a living-room bulb, so the
# catalog's warm reference factor would misread it; notes.md records this.
LIT_FACTOR = (1.0, 0.88, 0.72)


# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto: only the few
# centimetres of brick, frame and sheet that the mesh does not model. Regions
# painted coarser than 64 px/m scale their relief by their own px/m over PPM,
# so the slope the normal map derives stays physical; the roof deck (~10 px/m)
# and the bay ceiling stay flat.
BRICK_FACE = brickwork.BRICK_FACE   # brick face proud of the recessed mortar
FRAME_H = 0.030      # aluminium shopfront and door frames, proud of the glass
SEAM_H = 0.015       # the white eave's standing seams
DOOR_FRAME_H = 0.015  # steel door frames


# ================================================================== painting
def m(v):
    """Metres -> pixels."""
    return v * PPM


def text(c, word, x, y, cap, weight, mid, tracking=0.14, shade=1.0, ao=None,
         clip=None, join=()):
    """Set *word* with its baseline at y and its left edge at x.

    The letterforms are stroked centrelines from GLYPHS, drawn at *cap*
    pixels per em. Everything on this sheet is generated, this included:
    no font file is read, so the bake has no external dependency and the
    artwork carries no third party's licence. The canvas is supersampled, so
    the strokes come out anti-aliased without a separate coverage pass.
    """
    cx, prev, ratio = float(x), None, weight / float(cap)
    for ch in word:
        cx += _step(prev, ch, tracking, ratio, join) * cap
        for poly in GLYPHS[ch][1]:
            for (ax, ay), (bx, by) in zip(poly, poly[1:]):
                c.stroke((cx + ax * cap, y + ay * cap), (cx + bx * cap, y + by * cap),
                         weight, mid, shade, ao, clip)
        prev = ch
    return cx + GLYPHS[prev][0] * cap - x if prev else 0.0


def _arc(cx, cy, rx, ry, a0, a1, n=16):
    """Points along an elliptical arc, in glyph space."""
    a = np.radians(np.linspace(a0, a1, n + 1))
    return list(zip(cx + rx * np.cos(a), cy + ry * np.sin(a)))


# A geometric sans, drawn as stroked centrelines on a unit em: y = 0 is the
# baseline, y = 1 the cap line, and the advance is the first item. Only the
# letters the sign needs exist, which is the whole point of drawing them here
# rather than shipping a font: METRUM first, then the two MARKET adds.
GLYPHS = {
    " ": (0.34, []),
    "M": (0.86, [[(0.00, 0.00), (0.00, 1.00), (0.43, 0.30), (0.86, 1.00),
                  (0.86, 0.00)]]),
    "E": (0.60, [[(0.60, 1.00), (0.00, 1.00), (0.00, 0.00), (0.60, 0.00)],
                 [(0.00, 0.50), (0.48, 0.50)]]),
    "T": (0.68, [[(0.00, 1.00), (0.68, 1.00)], [(0.34, 1.00), (0.34, 0.00)]]),
    "R": (0.64, [[(0.00, 0.00), (0.00, 1.00), (0.30, 1.00)]
                 + _arc(0.30, 0.755, 0.32, 0.245, 90, -90, 10)
                 + [(0.00, 0.51)],
                 [(0.28, 0.51), (0.64, 0.00)]]),
    "U": (0.66, [[(0.00, 1.00), (0.00, 0.24)]
                 + _arc(0.33, 0.24, 0.33, 0.24, 180, 360, 12)
                 + [(0.66, 1.00)]]),
    # The crossbar sits where the diagonals actually are at y = 0.30, so the
    # three strokes meet instead of the bar overshooting into white space.
    "A": (0.70, [[(0.00, 0.00), (0.35, 1.00), (0.70, 0.00)],
                 [(0.105, 0.30), (0.595, 0.30)]]),
    # Arm and leg are one polyline through a vertex on the stem: at any weight
    # this sheet uses, 0.02 em is inside the stem's own half-width, so the
    # junction closes without a separate joining stroke.
    "K": (0.64, [[(0.00, 1.00), (0.00, 0.00)],
                 [(0.62, 1.00), (0.02, 0.44), (0.64, 0.00)]]),
}


# The wordmark is a connected logotype: these pairs are set with no gap at all,
# so the stroke one letter ends on is the stroke the next one starts from.
#
#   M|E and U|M share a full-height stem. Left to ordinary tracking those two
#   verticals land a third of a stroke apart and fuse into one bar of twice the
#   intended weight, which reads as a blot; made to coincide they give one
#   stroke of the right weight, and the collision becomes a ligature.
#
#   E|T and T|R meet on the cap line, where the E's top arm, the T's crossbar
#   and the R's shoulder run into one another as a single unbroken seam across
#   the top of the word. The T is therefore tied to both its neighbours.
#
# What is left loose is R|U, which has no shared stroke to make -- the R ends
# on a diagonal at the baseline and the U starts on a stem at the cap line --
# so it takes ordinary tracking and gives the word its one breath.
#
# These belong to the wordmark alone and are passed in, never applied by
# default. The sub-line is set from the same glyphs at a fifth of the size and
# shares letter pairs with the name above it -- MARKET has METRUM's E|T in it
# -- and a ligature drawn there, at that scale and at 0.40 of letterspacing,
# reads as two letters that have collided rather than as a joined logotype.
JOIN = {("M", "E"), ("E", "T"), ("T", "R"), ("U", "M")}


def _step(prev, ch, tracking, ratio, join=()):
    """How far the pen moves before setting *ch*, in em.

    *tracking* is the gap between one letter's **ink** and the next's, not
    between their centrelines. The glyphs are stroked, so each one's ink
    overruns its box by half a stroke at both ends, and spacing measured on
    centrelines therefore tightens as the weight goes up. In METRUM that closed
    the gaps between the E's arm, the T's bar and the R's shoulder -- three
    horizontals all sitting on the cap line -- until they fused into one
    continuous bar across the top of the word. Adding the stroke-to-cap *ratio*
    back in makes the gap mean what it says at any weight.
    """
    if prev is None:
        return 0.0
    if (prev, ch) in join:
        return GLYPHS[prev][0]
    return GLYPHS[prev][0] + tracking + ratio


def text_width(word, cap, tracking=0.14, weight=0.0, join=()):
    if not word:
        return 0.0
    ratio = weight / float(cap)
    w = sum(_step(word[i - 1], word[i], tracking, ratio, join)
            for i in range(1, len(word)))
    return (w + GLYPHS[word[-1]][0]) * cap


# ------------------------------------------------------------------- bands
def paint_plinth(c, y0):
    """Cast concrete, the 0.375 m base every wall stands on.

    Both cladding bands start at the ground and carry their own copy, so a
    rendered panel and a brick one meet the pavement on the same concrete.
    """
    h = m(Z_PLINTH)
    c.paint(0, ATLAS, y0 - PAD, y0 + h, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, y0 - PAD, y0 + h)
    z = (Y - y0) / PPM
    splash = 0.80 + 0.20 * np.clip(z / 0.20, 0.0, 1.0) ** 0.7
    c.shade[sy, sx] *= splash
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.20, 0, 1))
    # board-formed pour line, and the occluded strip under the cladding's drip
    c.mul(0, ATLAS, y0 + m(0.18), y0 + m(0.18) + 1, 0.94, ao=0.94)
    c.lift(0, ATLAS, y0 + m(0.18), y0 + m(0.18) + 1, -0.002)
    c.mul(0, ATLAS, y0 + h - 2, y0 + h + 1, 0.90, ao=0.88)


def paint_brick(c):
    """Stretcher-bond facing brick, 0.25 x 0.078125 m, 64 bricks per width.

    Mortar recessed, brick faces BRICK_FACE proud. Tone is hashed from the
    brick's position modulo the band's periods, so the bond and its colour
    both repeat exactly at the atlas wrap.
    """
    y0, h = BRICK_Y0 + m(Z_PLINTH), BRICK_H - m(Z_PLINTH)
    c.paint(0, ATLAS, y0, y0 + h + PAD, ID_BRICK, 1.0, 1.0)
    course, blen = m(COURSE), m(BRICK_L)
    sy, sx, Y, X = c.field(0, ATLAS, y0, y0 + h + PAD)
    r, b, bed, perp = brickwork.bond(Y, X, y0, course, blen, int(ATLAS / blen))
    tone = 0.90 + 0.20 * atlas.hash_unit(b, r, 17)
    c.shade[sy, sx] = np.where(bed, 0.78, np.where(perp, 0.80, tone))
    c.ao[sy, sx] = np.where(bed, 0.72, np.where(perp, 0.76, 1.0))
    c.height[sy, sx] = np.where(bed | perp, 0.0, BRICK_FACE)
    paint_plinth(c, BRICK_Y0)


def paint_stucco(c):
    """White render: the ornament panels, and the band along the top of
    every wall. Both sample these rows, so their joints line up."""
    y0 = STUCCO_Y0 + m(Z_PLINTH)
    h = STUCCO_H - m(Z_PLINTH)
    c.paint(0, ATLAS, y0, y0 + h + PAD, ID_STUCCO, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, y0, y0 + h + PAD)
    z = Z_PLINTH + (Y - y0) / PPM
    # rain runs off the eave and washes the render below it clean, and the
    # bottom of a rendered panel picks up splash-back from the pavement
    c.shade[sy, sx] *= 0.90 + 0.10 * np.clip((z - Z_PLINTH) / 0.35, 0, 1)
    # the movement joint where the render meets the brickwork's top
    yb = y0 + m(Z_BRICK - Z_PLINTH)
    c.mul(0, ATLAS, yb - 1, yb + 1, 0.88, ao=0.86)
    c.lift(0, ATLAS, yb - 1, yb + 1, -0.004)
    # vertical panel joints every 4 m: 256 px, so the band still tiles
    for i in range(4):
        x = i * 256.0
        c.mul(x, x + 1, y0, y0 + h + PAD, 0.90, ao=0.90)
        c.lift(x, x + 1, y0, y0 + h + PAD, -0.004)
    # a shallow drip under the eave
    c.mul(0, ATLAS, y0 + h - 3, y0 + h + PAD, 0.93, ao=0.90)
    paint_plinth(c, STUCCO_Y0)


def paint_shopfront(c):
    """The glazing band: a structural mullion every 2 m with a lighter one
    between, a transom at the door head, and sill and head rails.

    The mullion is split across the cell edge so no pane straddles u = 0 and
    the band tiles; scripts/glazing.py then paints one room per bay. The
    frames stand FRAME_H proud of the glass with rounded arrises.
    """
    y0, h = SHOP_Y0, SHOP_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_GLASS, 1.0, 1.0, height=0.0)
    bay = m(SHOP_BAY)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    xb = X % bay
    d_main = np.minimum(xb, bay - xb)                    # to the structural mullion
    d_mid = np.abs(xb - bay / 2.0)                       # to the light one
    main, mid = d_main < 5.0, d_mid < 1.5
    frame = main | mid
    c.mid[sy, sx] = np.where(frame, ID_FRAME, c.mid[sy, sx])
    c.ao[sy, sx] = np.where(main, 0.86, np.where(mid, 0.90, c.ao[sy, sx]))
    height = np.where(main, FRAME_H * np.clip(5.0 - d_main, 0, 1), 0.0)
    height = np.where(mid, np.maximum(height, 0.02 * np.clip(1.5 - d_mid, 0, 1)), height)
    c.height[sy, sx] = height
    yt = y0 + m(Z_TRANSOM - Z_SILL)
    for a0, a1, ao in ((yt - 2, yt + 2, 0.88), (y0 - PAD, y0 + 6, 0.80),
                       (y0 + h - 6, y0 + h + PAD, 0.82)):
        c.paint(0, ATLAS, a0, a1, ID_FRAME, 1.0, ao)
        c.bevel(0, ATLAS, max(a0, y0), min(a1, y0 + h), FRAME_H, 1.0, axes="y")
    # the head rail throws a line of shade down the top of every pane
    c.mul(0, ATLAS, y0 + h - 16, y0 + h - 6, 0.92, ao=0.86)


def paint_soffit(c):
    """The white eave: standing-seam sheet running down the slope, with the
    rafter ends that show along its outer edge. Both faces of the skirt sample
    these rows -- the underside a customer looks up at, and the top the snow
    is pushed over."""
    y0, h = SOF_Y0, SOF_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_EAVE, 1.0, 1.0, height=0.0)
    # seams every 0.5 m along the run: 32 px, so the band tiles
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    xs = X % 32.0
    seam = xs < 1.5
    c.shade[sy, sx] = np.where(seam, 0.92, 1.0)
    c.ao[sy, sx] = np.where(seam, 0.88, 1.0)
    c.height[sy, sx] = np.where(seam, SEAM_H * np.sin(np.pi * xs / 1.5), 0.0)
    # the soffit darkens toward the wall, where it sees least sky
    t = np.clip((Y - y0) / float(h), 0.0, 1.0)
    c.shade[sy, sx] *= 0.82 + 0.18 * t
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.78 + 0.22 * t)
    # rafter ends, one per 0.5 m, showing along the outer edge of the slope
    for i in range(int(ATLAS / 32)):
        x = i * 32.0 + 16.0
        c.paint(x - 1, x + 1, y0 + h - 8, y0 + h - 3, ID_TRIM, 0.9, 0.80, height=0.03)


# ----------------------------------------------------------------- regions
def _frame(c, rect, t, mid, shade=1.0, ao=0.9, height=None):
    x, y, w, h = rect
    for a0, a1, b0, b1, axes in ((x, x + w, y, y + t, "y"), (x, x + w, y + h - t, y + h, "y"),
                                 (x, x + t, y, y + h, "x"), (x + w - t, x + w, y, y + h, "x")):
        c.paint(a0, a1, b0, b1, mid, shade, ao)
        if height is not None:
            c.bevel(a0, a1, b0, b1, height, 1.0, axes=axes)


def paint_door_unit(c):
    """The entrance: two glass leaves that slide apart, a fixed screen each
    side for them to slide behind, and a transom light over the lot.

    The leaves are drawn with their meeting stiles together in the middle and
    the pocket stile at each side, which is what tells a slider from a pair of
    hinged doors at a glance.
    """
    x, y, w, h = DOOR_UNIT
    c.paint(x, x + w, y, y + h, ID_GLASS, 1.0, 1.0, height=0.0)
    _frame(c, DOOR_UNIT, 5, ID_FRAME, 1.0, 0.84, FRAME_H)
    # the unit stands on the pavement, not on the plinth the shopfront has:
    # its region runs from the ground to the shopfront head
    yt = y + m(Z_TRANSOM)

    def bar(a0, a1, b0, b1, shade, ao, axes):
        c.paint(a0, a1, b0, b1, ID_FRAME, shade, ao)
        c.bevel(a0, a1, b0, b1, FRAME_H, 1.0, axes=axes)
    bar(x, x + w, yt - 3, yt + 3, 1.0, 0.86, "y")                  # transom bar
    # side screens: 0.35 m each, the pockets the leaves run into
    for px in (x + m(0.35), x + w - m(0.35)):
        bar(px - 2.5, px + 2.5, y, yt, 1.0, 0.86, "x")
    # the two leaves, meeting on the centre line
    cx = x + w / 2.0
    bar(cx - 3, cx + 3, y, yt, 1.0, 0.82, "x")
    for lx in (cx - m(1.2), cx + m(1.2)):
        bar(lx - 2, lx + 2, y, yt, 1.0, 0.86, "x")
    # the head track the leaves hang from, and the threshold they run over
    bar(x, x + w, yt - 9, yt - 3, 0.92, 0.80, "y")
    bar(x, x + w, y + 5, y + 10, 0.90, 0.78, "y")
    # a hand-height rail across each leaf, and the lobby's own shade
    for lx in (cx - m(0.6), cx + m(0.6)):
        bar(lx - m(0.5), lx + m(0.5), y + m(0.95) - 2, y + m(0.95) + 2, 1.0, 0.88, "y")
    c.mul(x, x + w, y, y + h, 0.94, ao=0.80)


def _draw_sign(c, x, y, w, h):
    """The sign's artwork.

    A badge with the initial reversed out of it, then the name in geometric
    caps over a hairline rule, with the shop type letterspaced small beneath.
    The hierarchy is what makes it read as a shop sign rather than a nameplate:
    one thing to recognise at a hundred metres, one to read at ten. The face is
    a flat printed diffuser; only its frame stands proud.
    """
    c.paint(x, x + w, y, y + h, ID_SIGN, 1.0, 1.0, height=0.0)
    _frame(c, (x, y, w, h), 4, ID_TRIM, 1.0, 0.84, 0.02)

    bs, bx, by = 68, x + 13, y + 19
    c.rounded_rect(bx, by, bs, bs, 16, ID_SIGN_M, 1.0, 1.0)
    cap = 38
    text(c, "M", bx + (bs - GLYPHS["M"][0] * cap) / 2.0, by + (bs - cap) / 2.0,
         cap, 6.2, ID_SIGN, 0.0, 1.0)

    tx = x + 96
    wide = text(c, "METRUM", tx, y + 52, 40, 6.8, ID_SIGN_M, 0.14, join=JOIN)
    c.paint(tx - 3, tx + wide + 3, y + 44, y + 46, ID_SIGN_M, 0.92, 0.96)
    # the shop type is centred on the name above it, not ranged left with it:
    # a short letterspaced line hung off the left edge of a much longer one
    # reads as a stray rather than as part of the lockup
    sub_cap, sub_w = 16, 2.8
    narrow = text_width("MARKET", sub_cap, 0.40, sub_w)
    text(c, "MARKET", tx + (wide - narrow) / 2.0, y + 20, sub_cap, sub_w,
         ID_SIGN_M, 0.40)


def paint_placard(c):
    """The lit sign over the entrance.

    The canvas is supersampled, so the letterforms get real edge coverage in
    the albedo and the emission alike without a separate scratch canvas: a
    stroked letterform at 35 px of cap height does not survive a stair-step,
    and no mip level puts it back.

    The name is this repository's own, not a real retailer's, and no existing
    chain's mark, colours or trade dress is reproduced -- see CLAUDE.md's
    Reference Image Policy.
    """
    x, y, w, h = PLACARD
    _draw_sign(c, x, y, w, h)
    # the panel is brightest at the middle, where the tubes behind it are
    sy, sx, Y, _ = c.field(x, x + w, y, y + h)
    t = (Y - (y + h / 2.0)) / (h / 2.0)
    c.shade[sy, sx] *= 1.0 - 0.06 * t * t


def paint_item(c, kind):
    """One repeated opening: casing, reveal shade, and what closes it."""
    x, y, w, h = ITEM_REGION[kind]
    ow, oh = item_size_m(kind)
    _w, _h, cs, cb, ct = OPENINGS[kind]
    px, py = w / ow, h / oh                       # pixels per metre, this region
    k = px / PPM                                  # relief scale for this density
    if kind == "staff_window":
        c.paint(x, x + w, y, y + h, ID_STUCCO, 1.0, 0.92, height=0.0)
        gx0, gx1 = x + cs * px, x + w - cs * px
        gy0, gy1 = y + cb * py, y + h - ct * py
        c.paint(gx0, gx1, gy0, gy1, ID_GLASS, 1.0, 1.0)
        _frame(c, (gx0, gy0, gx1 - gx0, gy1 - gy0), 3, ID_FRAME, 1.0, 0.84, FRAME_H * k)
        c.mul(gx0, gx1, gy1 - 6, gy1, 0.92, ao=0.82)
        return
    # the two steel doors: ribbed leaf, a frame round it, a shadow at the head
    c.paint(x, x + w, y, y + h, ID_BRICK if kind == "goods_door" else ID_STUCCO,
            1.0, 0.92, height=0.0)
    dx0, dx1 = x + cs * px, x + w - cs * px
    dy0, dy1 = y + cb * py, y + h - ct * py
    c.paint(dx0, dx1, dy0, dy1, ID_DOOR, 1.0, 0.94)
    _frame(c, (dx0, dy0, dx1 - dx0, dy1 - dy0), 3, ID_TRIM, 0.95, 0.82, DOOR_FRAME_H * k)
    if kind == "goods_door":
        for i in range(1, 8):                      # sectional panel joints
            yy = dy0 + (dy1 - dy0) * i / 8.0
            c.mul(dx0, dx1, yy - 1, yy + 1, 0.86, ao=0.80)
            c.lift(dx0, dx1, yy - 1, yy + 1, -0.006 * k)
        c.mul(dx0, dx1, dy1 - 6, dy1, 0.86, ao=0.78)
    else:
        for i in range(1, 3):
            yy = dy0 + (dy1 - dy0) * i / 3.0
            c.mul(dx0 + 6, dx1 - 6, yy - 1, yy + 1, 0.90, ao=0.86)
            c.lift(dx0 + 6, dx1 - 6, yy - 1, yy + 1, -0.004 * k)
        c.disc(dx1 - 7, dy0 + (dy1 - dy0) * 0.45, 3, ID_TRIM, 1.0, 0.8, height=0.03 * k)
    c.mul(x, x + w, y, y + h, 1.0, ao=0.88)


def paint_roof_deck(c):
    """Bitumen membrane: laid in rolls, ponded where it has settled, with the
    grit worn off the walking lines between the plant. Flat: ~10 px/m."""
    x, y, w, h = ROOF_DECK
    c.paint(x, x + w, y, y + h, ID_ROOF, 1.0, 1.0, height=0.0)
    for i in range(1, 19):                         # roll seams, one per metre
        yy = y + h * i / 18.0
        c.mul(x, x + w, yy - 0.5, yy + 0.5, 0.90, ao=0.90)
    rs = np.random.RandomState(11)
    for _ in range(22):                            # shallow ponding
        cx, cy = rs.uniform(x + 12, x + w - 12), rs.uniform(y + 10, y + h - 10)
        c.disc(cx, cy, rs.uniform(7, 18), None, rs.uniform(0.93, 0.99), 0.97)
    c.mul(x, x + w, y, y + h, 1.0, ao=0.96)


def paint_bay_ceiling(c):
    """The roof slab's underside over the loading bay: sprayed soffit, dirty
    where the vans breathe on it. Flat: ~16 px/m."""
    x, y, w, h = BAY_CEILING
    c.paint(x, x + w, y, y + h, ID_EAVE, 0.72, 0.62, height=0.0)
    for i in range(1, 7):
        xx = x + w * i / 7.0
        c.mul(xx - 1, xx + 1, y, y + h, 0.88, ao=0.80)
    sy, sx, Y, _ = c.field(x, x + w, y, y + h)
    t = np.clip((Y - y) / float(h), 0, 1)
    c.shade[sy, sx] *= 0.80 + 0.28 * t             # brighter toward the opening
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.58 + 0.34 * t)


def paint_plant(c):
    """Roof plant: an air-handling unit's casing and lid, a fan cowl, a pipe.
    Painted at ~48 px/m, so its relief is scaled by 0.75."""
    k = 0.75
    x, y, w, h = AHU_SIDE
    c.paint(x, x + w, y, y + h, ID_METAL, 1.0, 0.95, height=0.0)
    c.paint(x, x + w, y + h - 4, y + h, ID_METAL, 0.88, 0.86, height=0.02 * k)
    for i in range(1, 6):                          # casing panel joints
        xx = x + w * i / 6.0
        c.mul(xx - 1, xx + 1, y, y + h, 0.88, ao=0.86)
        c.lift(xx - 1, xx + 1, y, y + h, -0.004 * k)
    c.paint(x + 6, x + w // 2 - 4, y + 8, y + h - 8, ID_METAL, 0.72, 0.70, height=-0.01 * k)
    for i in range(6):                             # an intake louvre
        yy = y + 8 + (h - 16) * i / 6.0
        c.mul(x + 6, x + w // 2 - 4, yy, yy + 2, 0.60, ao=0.62)
        sy, sx, Y, _ = c.field(x + 6, x + w // 2 - 4, yy, yy + 2)
        c.height[sy, sx] = 0.015 * k * (1.0 - (Y - yy) / 2.0)

    x, y, w, h = AHU_TOP
    c.paint(x, x + w, y, y + h, ID_METAL, 0.94, 0.94, height=0.0)
    for cx in (x + w * 0.3, x + w * 0.7):
        c.disc(cx, y + h * 0.5, 13, ID_METAL, 0.66, 0.66, height=-0.02 * k)
        c.disc(cx, y + h * 0.5, 13, ID_METAL, 0.48, 0.55, inner=10, height=0.02 * k)
        for j in range(4):
            a = np.pi * j / 4.0
            c.stroke((cx - 10 * np.cos(a), y + h * 0.5 - 10 * np.sin(a)),
                     (cx + 10 * np.cos(a), y + h * 0.5 + 10 * np.sin(a)),
                     3, ID_METAL, 0.80, 0.70, height=0.0)

    x, y, w, h = COWL
    c.paint(x, x + w, y, y + h, ID_METAL, 1.0, 0.95, height=0.0)
    c.paint(x, x + w, y + h - 12, y + h, ID_METAL, 0.86, 0.80, height=0.03 * k)   # the hood
    c.mul(x, x + w, y + h - 13, y + h - 11, 0.62, ao=0.68)
    for i in range(1, 5):
        xx = x + w * i / 5.0
        c.mul(xx - 1, xx + 1, y, y + h - 12, 0.90, ao=0.88)
        c.lift(xx - 1, xx + 1, y, y + h - 12, -0.004 * k)

    x, y, w, h = PIPE
    c.paint(x, x + w, y, y + h, ID_METAL, 0.92, 0.90)
    sy, sx, _, X = c.field(x, x + w, y, y + h)       # a cylinder, across U
    u = 2.0 * (X - x) / w - 1.0
    c.height[sy, sx] = 0.04 * k * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(x, x + w, y + h - 5, y + h, ID_METAL, 0.72, 0.72)


def paint_patches(c):
    """Flat cells for the surfaces a whole face takes one colour from."""
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0),
        "reveal_dark": (ID_TRIM, 0.80, 0.62),
        "reveal_light": (ID_STUCCO, 0.82, 0.66),
        "cap": (ID_EAVE, 0.98, 0.98),
        "parapet": (ID_EAVE, 0.86, 0.82),
        "fascia": (ID_EAVE, 1.0, 0.96),
        "column": (ID_STEEL, 0.94, 0.86),
        "sign_edge": (ID_TRIM, 0.88, 0.84),
        "deck_edge": (ID_ROOF, 0.84, 0.86),
        "wall_top": (ID_BLANK, 1.0, 1.0),
        "plinth_top": (ID_PLINTH, 0.88, 0.84),
    }
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x - 2, x + w + 2, y - 2, y + h + 2, mid, sh, ao, height=0.0)


# ------------------------------------------------------------------ checks
def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands, or
    run off the sheet."""
    rects = {"door_unit": DOOR_UNIT,
             "placard": PLACARD, "goods_door": GOODS_DOOR,
             "bay_ceiling": BAY_CEILING, "roof_deck": ROOF_DECK,
             "service_door": SERVICE_DOOR, "staff_window": STAFF_WINDOW,
             "ahu_side": AHU_SIDE, "ahu_top": AHU_TOP, "cowl": COWL,
             "pipe": PIPE}
    rects.update(PATCHES)
    bands_top = SOF_Y0 + SOF_H + PAD
    names = sorted(rects)
    problems = []
    for i, a in enumerate(names):
        ax, ay, aw, ah = rects[a]
        if ax - 2 < 0 or ay - 2 < 0 or ax + aw + 2 > ATLAS or ay + ah + 2 > ATLAS:
            problems.append("%s runs off the atlas" % a)
        if ay - 4 < bands_top:
            problems.append("%s overlaps the tiling bands" % a)
        for b in names[i + 1:]:
            bx, by, bw, bh = rects[b]
            if (ax - 4 < bx + bw and bx - 4 < ax + aw
                    and ay - 4 < by + bh and by - 4 < ay + ah):
                problems.append("%s and %s overlap" % (a, b))
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    Both cladding bands start at the ground, so splash and the plinth's soil
    land the same on every wall; the render under the deep eave stays dry and
    gathers dust instead. The sign is the shop's to keep clean."""
    steel = (ID_ROOF, ID_METAL, ID_EAVE, ID_TRIM, ID_FRAME, ID_STEEL)
    w = weathering.Weather(c, clean=(ID_GLASS, ID_SIGN, ID_SIGN_M), steel=steel)
    w.grime()
    w.fade((ID_DOOR, ID_EAVE, ID_STEEL))
    w.wash((ID_BRICK, ID_STUCCO))
    for y0, top, clad in ((BRICK_Y0, BRICK_Y0 + BRICK_H + PAD, ID_BRICK),
                          (STUCCO_Y0, STUCCO_Y0 + STUCCO_H + PAD, ID_STUCCO)):
        w.plinth(0, ATLAS, y0, y0 + m(Z_PLINTH), (ID_PLINTH,))
        w.splash(0, ATLAS, y0 + m(Z_PLINTH), top, (clad,))
    w.shelter(0, ATLAS, STUCCO_Y0 + m(Z_WALL - 0.5), STUCCO_Y0 + m(Z_WALL), (ID_STUCCO,),
              amount=0.08, top=STUCCO_Y0 + STUCCO_H + PAD)
    # the shopfront's sill rail, a hand's height off the pavement
    w.add("D", 0, ATLAS, SHOP_Y0 - PAD, SHOP_Y0 + 6,
          lambda Y, X, nz: 0.12 + 0.08 * nz("blotch"), (ID_FRAME,))
    # the entrance's threshold, walked over all day
    x, y, dw, dh = DOOR_UNIT
    w.add("D", x, x + dw, y, y + 10, lambda Y, X, nz: 0.15 + 0.08 * nz("blotch"), (ID_FRAME,))
    # the staff window's sill and the runs below it; the doors' feet
    for kind in OPENINGS:
        x, y, rw, rh = ITEM_REGION[kind]
        ow, oh = item_size_m(kind)
        _w, _h, cs, cb, ct = OPENINGS[kind]
        px, py = rw / ow, rh / oh
        x0, x1, y0, y1 = x + cs * px, x + rw - cs * px, y + cb * py, y + rh - ct * py
        if kind == "staff_window":
            w.add("D", x0, x1, y0, y0 + 3, 0.12, (ID_FRAME,))
            w.runs(x, x + rw, y, y0, (ID_STUCCO,), 0.15, fall=max(y0 - y, 1.0))
        else:
            handle = (x1 - 7, y0 + (y1 - y0) * 0.45) if kind == "service_door" else None
            w.door(x0, x1, y0, y1, (ID_DOOR,), handle=handle, ppm=px)
    # the flat roof: dirt where the membrane ponds and along the walking lines
    x, y, rw, rh = ROOF_DECK
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.10 * nz("big") + 0.06 * nz("blotch"),
          (ID_ROOF,))
    # the plant: runs down its casings from the lids and the hood
    for x, y, rw, rh in (AHU_SIDE, COWL):
        w.runs(x, x + rw, y, y + rh, (ID_METAL,), 0.12, fall=rh / 2.0)
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_brick(c)
    paint_stucco(c)
    paint_shopfront(c)
    paint_soffit(c)
    c.check_bands(BAND_IDS)
    paint_door_unit(c)
    paint_placard(c)
    for kind in OPENINGS:
        paint_item(c, kind)
    paint_roof_deck(c)
    paint_bay_ceiling(c)
    paint_plant(c)
    paint_patches(c)

    # Weathering. Every field is periodic, so the bands still wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    # the streaks are rain running down a wall, so the deck is left out of
    # them: on a horizontal surface they read as a second set of seams, and at
    # the deck's density they crossed the roll seams into a grid
    weathered = np.isin(c.mid, (ID_BRICK, ID_PLINTH, ID_STUCCO))
    streak = atlas.noise(c, 7, 0.8, 40.0)
    c.shade[weathered] *= 1.0 + 0.03 * streak[weathered]
    sheeted = np.isin(c.mid, (ID_EAVE, ID_METAL, ID_DOOR))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    c.shade[sheeted] *= 1.0 + 0.016 * grain[sheeted]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_STUCCO))
    pores = atlas.noise(c, 9, 0.8)
    c.shade[mineral] *= 1.0 + 0.025 * pores[mineral]
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
    t[ID_STUCCO] = pal["stucco"]
    t[ID_ROOF] = pal["roof"]
    t[ID_TRIM] = pal["trim"]
    t[ID_EAVE] = pal["eave"]
    t[ID_DOOR] = pal["door"]
    return t


def export(out_dir, ss=atlas.SS):
    """Candidate glazing in the emission map is neutral white, so it reads as
    glazing downstream; the sign carries its own colours, because a lit sign
    is not a window (EMIT). No occupancy or schedule is baked in."""
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.012)
    c.weather.dust(cav, (ID_BRICK, ID_STUCCO))       # in the joints
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
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
