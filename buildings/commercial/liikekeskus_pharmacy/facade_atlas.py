# SPDX-License-Identifier: GPL-2.0-only

"""Albedo, ORM, normal and emission atlas, and shared layout, for
liikekeskus_pharmacy.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
storey heights, band rows, bay positions, opening sizes, region rectangles --
so a change here cannot leave the UVs pointing at the wrong artwork.

The atlas is a trim sheet. Three bands run the full width and tile
horizontally: the coursed stone, the shopfront glazing and the white eave. The
stone band also tiles *vertically*, with a period of 4 m, because the gable
walls run to 9.5 m and a band tall enough to cover them at 64 texels/metre
would eat two thirds of the sheet. build.py cuts the gable into horizontal
courses at the wrap lines and the band carries periodic padding at both, so the
seam samples the artwork that actually continues there rather than a neighbour.

Everything singular -- the doors, the sign boards, the gable curtain wall, the
roof, the plant -- gets a region of its own above the bands. atlas.pad() fills
every sample no region claims from the nearest region's own edge.

Rasterising is scripts/atlas.py's: a canvas supersampled SS x SS per pixel,
with a height channel the normal map is derived from, so the sign boards'
lettering and marks come out anti-aliased like everything else (numpy and
scipy; Pillow to save).

Density is 64 texels/metre on everything a customer stands in front of. The
gable curtain wall runs at 48 and the roof at 14, because one is seen across a
car park and the other from the air; notes.md lists both.

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
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "liikekeskus_pharmacy"
ATLAS = 1024
PPM = 64.0

# ============================================================ massing, metres
# Plan is centred on the origin; the shopfront elevation faces -Y.
HX, HY = 12.0, 8.0          # half width (24 m of front), half depth (16 m)
SLOPE = 0.45                # roof pitch, rise per metre of run: 24.23 degrees
EAVE_OUT = 0.9              # roof projection past the two side walls
RAKE_OUT = 1.2              # roof projection past the two gable walls
ROOF_T = 0.375              # roof slab thickness, measured vertically; this is
                            # also the depth of the white fascia and rake board
WALL_INTO_ROOF = 0.12       # walls run this far into the slab, which trims them

Z_EAVE = 4.0                # roof underside at the side wall line; one storey
Z_RIDGE = Z_EAVE + SLOPE * HX                    # 9.4
Z_EAVE_OUT = Z_EAVE - SLOPE * EAVE_OUT           # underside at the eave edge


def roof_under(x):
    """Underside of the roof slab over plan position *x*."""
    return Z_EAVE + SLOPE * (HX - abs(x))


# ----------------------------------------------------------- front elevation
Z_KICK = 0.35               # top of the shopfront's kick panel
Z_LEAF = 2.25               # door leaf head, and the transom bar across the
                            # shopfront at the same height
Z_HEAD = 3.25               # shopfront head: 208 px, the band's full height
Z_FASCIA = Z_EAVE           # top of the sign boards; the eave springs here
GLAZE_DEPTH = 0.18          # the shopfront sits this far back in its opening

# The front is four quarters. The pharmacy has the middle two, the beauty salon
# the left one and the barber the right one, so the two party walls land on 6.0
# and 18.0 m. Every bay is 4 m wide, which is four of the shopfront band's
# 1 m lights and two of its heavier structural mullions.
FRONT_W = 2.0 * HX          # 24.0
BAY_W = 4.0
PIER_CORNER = 1.4
PIER_PARTY = 1.2
PIER_MID = 2.8              # carries the gable apex, so it is the wide one

BAYS = [
    ("salon", PIER_CORNER, PIER_CORNER + BAY_W),
    ("pharmacy_left", 6.6, 10.6),
    ("pharmacy_right", 13.4, 17.4),
    ("barber", 18.6, 22.6),
]
PIERS = [(0.0, 1.4), (5.4, 6.6), (10.6, 13.4), (17.4, 18.6), (22.6, 24.0)]

# (bay, centre s, leaf count). The pharmacy's pair is deliberately not on the
# building's centre line: it sits in the second quarter of the front, two
# whole shopfront lights wide. The salon's and the barber's are centred in
# their own bays instead -- against a party pier a single door reads as an
# afterthought squeezed into the corner of the glazing rather than as that
# unit's way in.
DOORS = [("pharmacy_left", 8.6, 2), ("salon", 3.4, 1), ("barber", 20.6, 1)]
DOOR_W = {1: 1.0, 2: 2.0}

# The gable curtain wall stands over the pharmacy, one panel each side of the
# middle pier. Its head follows the rake down to the eaves and is capped flat
# before it reaches the band's wrap line, which keeps the opening inside one
# region and leaves a proper head of stone under the rafters.
GABLE_SILL = Z_FASCIA
GABLE_HEAD_CAP = 7.7
GABLE_HEAD_DROP = 0.3       # head this far below the roof underside
GABLE_PANELS = [(6.6, 10.6), (13.4, 17.4)]
STONE_WRAP = 4.0            # the stone band's vertical period, in metres

# ------------------------------------------------------- the other elevations
# (width, height, casing side, casing bottom, casing top) of each cut opening.
OPENINGS = {
    "side_window": (1.6, 1.4, 0.15, 0.15, 0.15),
    "maint_door": (1.0, 2.25, 0.10, 0.0, 0.10),
}
REVEAL_DEPTH = {"side_window": 0.14, "maint_door": 0.12}

SIDE_WINDOWS = (4.0, 7.6, 11.2)     # s along either side wall, sill at Z_WIN
Z_WIN = 1.1
# Stone buttresses between those windows, in the wall's own material, standing
# proud of it and running up until the falling soffit cuts them off. They are
# decorative rather than structural, so they are parallel-sided: the same
# width and the same projection from the pavement to the eave, with no batter.
BUTTRESSES = (5.8, 9.4)
BUTTRESS_W = 0.7
BUTTRESS_OUT = 0.30
MAINT_DOOR_S = 11.0                 # rear wall, behind the pharmacy
LOUVRES = ((10.0, 5.2), (14.0, 5.2))  # rear gable roof-space vents, (s, z)
LOUVRE_WH = (0.8, 0.6)

# The wall-hung air handler on the right-hand elevation, and the black stacks
# standing on the roof.
AHU = {"s": 13.8, "z": 1.5, "w": 1.9, "h": 1.2, "d": 0.55}
# (kind, plan position, across, height clear of the roof surface). None of
# them straddles the ridge, so each one's foot is a slice of a single plane.
VENTS = [("box", (-3.2, 2.6), 0.85, 1.00), ("box", (3.0, -0.6), 0.70, 0.85),
         ("pipe", (-1.6, 5.4), 0.30, 0.80), ("pipe", (1.5, 2.0), 0.26, 0.70),
         ("pipe", (-5.4, -3.2), 0.24, 0.65)]

# The white crest capping the ridge from rake to rake: a painted box, square
# sided and flat topped, standing clear of the shingles so the ridge reads as
# a white line against the dark roof. It runs a few centimetres past each rake
# board, so its end caps the apex instead of dying into it.
Z_RIDGE_TOP = Z_RIDGE + ROOF_T                   # 9.775, the shingles at the ridge
CREST = {"w": 0.6, "h": 0.30, "end": 0.04}
Z_CREST = Z_RIDGE_TOP + CREST["h"]               # 10.075

# The illuminated sign over the ridge near the front gable, a cube on a stand
# of four steel legs. The legs stand on the crest, so they go in two pairs
# along it: the crest is only 0.6 m across, and a leg beside it would stand on
# the shingles. The cube carries the mark on all four sides, because a shopping
# centre in a car park is approached from every direction and a flat blade
# would show nothing but its edge to half of them. Square is also what lets the
# four faces share one region: LOGO is checked against w and h, and build.py
# maps it along x on two faces and along y on the other two.
STAND = {"leg": 0.08, "x": 0.20, "y": 0.60, "clear": 0.25}   # section, leg
                                                             # centres, height
SIGN = {"w": 1.6, "h": 1.6, "d": 1.6, "y": -7.3, "z0": Z_CREST + STAND["clear"]}
SIGN_Z1 = SIGN["z0"] + SIGN["h"]                 # 11.925

# ================================================================ atlas bands
PAD = 6                     # rows/columns each band or region paints beyond
                            # its own edge, so near-mip sampling stays on it

# Every band starts PAD rows above whatever is under it, so it has real
# padding on both sides; the stone band's is periodic rather than clamped,
# because that is what continues across its wrap line.
STONE_Y0, STONE_H = 6, 256          # 4.0 m at 64 px/m, periodic in both axes
SHOP_Y0, SHOP_H = 274, 208          # z 0 .. 3.25 of shopfront
SOF_Y0, SOF_H = 494, 104            # 0.375 m of fascia, then 1.25 m of soffit
SOF_FASCIA = 24                     # rows of the band that are the fascia face

COURSE = 0.125                      # stone course pitch: 8 px, 32 per period
BLOCK = (24, 40)                    # stone block length in pixels
LIGHT = 1.0                         # shopfront light pitch, metres
MULLION = 2.0                       # heavier structural mullion pitch

# ---------------------------------------------------------- unique regions
# (x, y, w, h) in atlas pixels. check_regions() proves they do not collide.
SHELF_A, SHELF_B = 610, 824

DOOR_DOUBLE = (8, SHELF_A, 128, 208)        # 2.00 x 3.25 m at 64 px/m
DOOR_SINGLE = (142, SHELF_A, 64, 208)       # 1.00 x 3.25 m
MAINT_DOOR = (212, SHELF_A, 77, 150)        # 1.20 x 2.35 m
SIDE_WINDOW = (295, SHELF_A, 122, 109)      # 1.90 x 1.70 m
LOGO = (423, SHELF_A, 102, 102)             # 1.60 x 1.60 m of sign face
GABLE_GLAZE = (531, SHELF_A, 192, 178)      # 4.00 x 3.71 m at 48 px/m
AHU_SIDE = (729, SHELF_A, 122, 77)          # 1.90 x 1.20 m
AHU_TOP = (729, SHELF_A + 83, 122, 38)      # 1.90 x 0.60 m
LOUVRE = (729, SHELF_A + 127, 51, 38)       # 0.80 x 0.60 m

ROOF = (8, SHELF_B, 240, 184)               # 18.4 x 14.15 m at 13 px/m
FASCIA_W, FASCIA_H = 256, 48                # 4.00 x 0.75 m at 64 px/m
FASCIA = {"salon": (254, SHELF_B, FASCIA_W, FASCIA_H),
          "pharmacy_left": (254, SHELF_B + 54, FASCIA_W, FASCIA_H),
          "pharmacy_right": (516, SHELF_B, FASCIA_W, FASCIA_H),
          "barber": (516, SHELF_B + 54, FASCIA_W, FASCIA_H)}
VENT_BOX = (778, SHELF_B, 45, 96)           # 0.70 x 1.50 m, seat to cowl
VENT_PIPE = (829, SHELF_B, 19, 80)          # 0.30 x 1.25 m

GABLE_PPM = 48.0
ROOF_PPM = 13.0

# Only surfaces with genuinely nothing to say get a flat swatch: caps buried
# by the union, the sign box's lid and underside, its stand, and the painted
# returns of the plant. Every stone reveal and return samples the stone band
# itself, wrapped round its corner, because a 0.3 m cheek of flat grey beside
# coursed stone reads as a missing texture rather than as a surface turning
# away from the light.
PATCH_NAMES = ("blank", "sign_side", "steel")
PATCHES = {n: (856 + 20 * (i % 5), SHELF_B + 20 * (i // 5), 12, 12)
           for i, n in enumerate(PATCH_NAMES)}


def item_size_m(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    return w + 2.0 * cs, h + cb + ct


# ============================================================= material ids
ID_BLANK, ID_STONE, ID_ROOF, ID_EAVE, ID_GLASS = 0, 1, 2, 3, 4
ID_FRAME, ID_DOOR, ID_KICK, ID_STEEL, ID_METAL = 5, 6, 7, 8, 9
ID_SIGN, ID_SIGN_G, ID_SIGN_T = 10, 11, 12

# (roughness, metallic). Painted steel stays dielectric: the paint is what the
# light sees. The shopfront sections are anodised aluminium and the roof stacks
# are galvanised under their paint, so those are the only real metals here.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_STONE: (0.82, 0.0), ID_ROOF: (0.88, 0.0),
    ID_EAVE: (0.44, 0.0), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_FRAME: (0.32, 0.74), ID_DOOR: (0.36, 0.70), ID_KICK: (0.62, 0.0),
    ID_STEEL: (0.52, 0.0), ID_METAL: (0.44, 0.72),
    ID_SIGN: (0.18, 0.0), ID_SIGN_G: (0.20, 0.0), ID_SIGN_T: (0.22, 0.0),
}

# ---------------------------------------------------------------- palettes
# One coherent treatment per instance: the stone changes and the roof and the
# white move a little with it, never within one building. The shop signs are
# the centre's identity and are the same in every colour.
VARIANTS = {
    "grey_stone": {"stone": (152, 147, 138), "roof": (50, 50, 52),
                   "eave": (236, 235, 230), "door": (62, 66, 64),
                   "kick": (96, 94, 90)},
    "beige_stone": {"stone": (181, 165, 136), "roof": (58, 54, 50),
                    "eave": (238, 236, 229), "door": (64, 64, 60),
                    "kick": (104, 99, 90)},
    "red_stone": {"stone": (148, 99, 82), "roof": (52, 48, 48),
                  "eave": (234, 232, 227), "door": (60, 60, 60),
                  "kick": (94, 88, 84)},
    "brown_stone": {"stone": (120, 102, 88), "roof": (46, 47, 49),
                    "eave": (232, 231, 226), "door": (58, 60, 58),
                    "kick": (92, 88, 82)},
}
DEFAULT_VARIANT = "grey_stone"

FIXED = {
    ID_GLASS: glazing.BASE, ID_FRAME: (74, 78, 76), ID_BLANK: (52, 52, 52),
    ID_STEEL: (38, 39, 40), ID_METAL: (150, 152, 154),
    ID_SIGN: (233, 237, 234), ID_SIGN_G: (20, 98, 64), ID_SIGN_T: (34, 46, 42),
}

# A stray pixel in a tiling band is not a local blemish: every surface that
# samples the band repeats it.
BAND_IDS = {
    "STONE": ((STONE_Y0, STONE_Y0 + STONE_H), {ID_STONE}),
    "SHOP": ((SHOP_Y0, SHOP_Y0 + SHOP_H), {ID_GLASS, ID_FRAME, ID_KICK}),
    "SOFFIT": ((SOF_Y0, SOF_Y0 + SOF_H), {ID_EAVE}),
}

# The candidate-glazing mask doubles as the emission map. Glass is neutral
# white so scripts/validate_asset.py can pick it out as glazing; the four sign
# boards and the roof sign are luminous fixtures rather than windows and carry
# their own colours. A lit box is a bright diffuser with the graphics printed
# on it, and print transmits far less light than the blank panel does, so the
# ink emits roughly twenty times less than the field it sits on.
# A lit board's white is written cool rather than neutral, and that is not
# only how a fluorescent diffuser looks: downstream the mask is read as
# glazing wherever it is bright *and* neutral, so a neutral white sign would
# be measured against the glazing band and drag it two stops brighter.
EMIT = {ID_GLASS: (255, 255, 255), ID_SIGN: (186, 200, 214),
        ID_SIGN_G: (14, 58, 38), ID_SIGN_T: (12, 14, 13)}
# Linear RGB. A shop's interior is fluorescent, not a living-room bulb, so the
# catalog's warm reference factor would misread it; notes.md records this.
LIT_FACTOR = (1.0, 0.88, 0.72)


# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto: only the few
# centimetres of stone, frame and sheet the mesh does not model. Regions
# painted coarser than 64 px/m scale their relief by their px/m over PPM, so
# the slope the normal map derives stays physical.
STONE_FACE = 0.012   # split-face block, proud of its recessed bed joint
FRAME_H = 0.030      # aluminium shopfront, door and curtain-wall sections
BOARD_JOINT = 0.003  # soffit and fascia board joints
SIGN_FRAME = 0.015   # the sign boxes' edges; the printed faces are flat


# ================================================================== painting
def m(v):
    """Metres -> pixels."""
    return v * PPM


def text(c, word, x, y, cap, weight, mid, tracking=0.16, shade=None, ao=None,
         clip=None):
    """Set *word* with its baseline at y and its left edge at x.

    The letterforms are stroked centrelines from GLYPHS, drawn at *cap*
    pixels per em. Everything on this sheet is generated, this included:
    no font file is read, so the bake has no external dependency and the
    artwork carries no third party's licence. The canvas is supersampled, so
    the strokes come out anti-aliased without a separate coverage pass.
    """
    cx, prev, ratio = float(x), None, weight / float(cap)
    for ch in word:
        cx += _step(prev, ch, tracking, ratio) * cap
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
# letters the sign boards need exist, which is the point of drawing them here
# rather than shipping a font: PHARMACY, BEAUTY SALON, BARBER.
GLYPHS = {
    " ": (0.34, []),
    "A": (0.70, [[(0.00, 0.00), (0.35, 1.00), (0.70, 0.00)],
                 [(0.105, 0.30), (0.595, 0.30)]]),
    # Stem, upper bowl and waist in one polyline, then the lower bowl from the
    # waist back to the baseline: the two meet on the stem at half height.
    "B": (0.64, [[(0.00, 0.00), (0.00, 1.00), (0.28, 1.00)]
                 + _arc(0.28, 0.75, 0.30, 0.25, 90, -90, 10)
                 + [(0.00, 0.50)],
                 [(0.00, 0.50), (0.30, 0.50)]
                 + _arc(0.30, 0.25, 0.32, 0.25, 90, -90, 10)
                 + [(0.00, 0.00)]]),
    "C": (0.72, [_arc(0.36, 0.50, 0.36, 0.50, 55, 305, 18)]),
    "E": (0.60, [[(0.60, 1.00), (0.00, 1.00), (0.00, 0.00), (0.60, 0.00)],
                 [(0.00, 0.50), (0.48, 0.50)]]),
    "H": (0.70, [[(0.00, 1.00), (0.00, 0.00)], [(0.70, 1.00), (0.70, 0.00)],
                 [(0.00, 0.50), (0.70, 0.50)]]),
    "L": (0.54, [[(0.00, 1.00), (0.00, 0.00), (0.54, 0.00)]]),
    "M": (0.86, [[(0.00, 0.00), (0.00, 1.00), (0.43, 0.30), (0.86, 1.00),
                  (0.86, 0.00)]]),
    "N": (0.72, [[(0.00, 0.00), (0.00, 1.00), (0.72, 0.00), (0.72, 1.00)]]),
    "O": (0.76, [_arc(0.38, 0.50, 0.38, 0.50, 0, 360, 24)]),
    "P": (0.62, [[(0.00, 0.00), (0.00, 1.00), (0.30, 1.00)]
                 + _arc(0.30, 0.755, 0.32, 0.245, 90, -90, 10)
                 + [(0.00, 0.51)]]),
    "R": (0.64, [[(0.00, 0.00), (0.00, 1.00), (0.30, 1.00)]
                 + _arc(0.30, 0.755, 0.32, 0.245, 90, -90, 10)
                 + [(0.00, 0.51)],
                 [(0.28, 0.51), (0.64, 0.00)]]),
    # Two bowls that hand over across the middle: the last point of the upper
    # arc and the first of the lower are joined by the segment between them,
    # which is the S's spine.
    "S": (0.62, [_arc(0.31, 0.745, 0.28, 0.255, 20, 235, 14)
                 + _arc(0.31, 0.255, 0.28, 0.255, 55, -145, 14)]),
    "T": (0.68, [[(0.00, 1.00), (0.68, 1.00)], [(0.34, 1.00), (0.34, 0.00)]]),
    "U": (0.66, [[(0.00, 1.00), (0.00, 0.24)]
                 + _arc(0.33, 0.24, 0.33, 0.24, 180, 360, 12)
                 + [(0.66, 1.00)]]),
    "Y": (0.68, [[(0.00, 1.00), (0.34, 0.48), (0.68, 1.00)],
                 [(0.34, 0.48), (0.34, 0.00)]]),
}


def _step(prev, ch, tracking, ratio):
    """How far the pen moves before setting *ch*, in em.

    *tracking* is the gap between one letter's **ink** and the next's, not
    between their centrelines. The glyphs are stroked, so each one's ink
    overruns its box by half a stroke at both ends, and spacing measured on
    centrelines therefore tightens as the weight goes up. Adding the
    stroke-to-cap *ratio* back in makes the gap mean what it says at any
    weight.
    """
    if prev is None:
        return 0.0
    return GLYPHS[prev][0] + tracking + ratio


def text_width(word, cap, tracking=0.16, weight=0.0):
    if not word:
        return 0.0
    ratio = weight / float(cap)
    w = sum(_step(word[i - 1], word[i], tracking, ratio)
            for i in range(1, len(word)))
    return (w + GLYPHS[word[-1]][0]) * cap


# ------------------------------------------------------------------- bands
def _blocks(width, rs, lo, hi):
    """Block boundaries across *width* pixels that sum to it exactly, so the
    course still tiles."""
    out, x = [], 0
    while x < width:
        w = int(rs.randint(lo, hi + 1))
        if width - (x + w) < lo:
            w = width - x
        out.append((x, x + w))
        x += w
    return out


def paint_stone(c):
    """Coursed split-face stone, 32 courses of 0.125 m over a 4 m period.

    Periodic in both axes: horizontally over the sheet's own width, and
    vertically over the band, because the gable walls sample it twice and
    build.py cuts them at the wrap line rather than stretching the courses.
    Each block stands STONE_FACE proud of its bed joint with a rough split
    face; the roughness is noise with the band's own vertical period.
    """
    y0, h = STONE_Y0, STONE_H
    c.paint(0, ATLAS, y0, y0 + h, mid=ID_STONE, shade=1.0, ao=1.0, height=0.0)
    rows = int(round(COURSE * PPM))                 # 8 px per course
    for j in range(h // rows):
        rs = np.random.RandomState(1700 + j)
        cy = y0 + j * rows
        for bx0, bx1 in _blocks(ATLAS, rs, *BLOCK):
            t = float(atlas.hash_unit(j, bx0))
            # split face: the block is brighter where it was cleaved and a
            # little darker along the bed it sits on
            c.mul(bx0, bx1, cy + 1, cy + rows, 0.88 + 0.26 * t)
            c.mul(bx0, bx1, cy + rows - 2, cy + rows, 0.94)
            c.bevel(bx0 + 1, bx1, cy + 1, cy + rows, STONE_FACE, 0.8)
            c.mul(bx0 + 1, bx0 + 2, cy + 1, cy + rows, 0.84, ao=0.86)
        # the bed joint: recessed mortar, so it is both darker and occluded
        c.mul(0, ATLAS, cy, cy + 1, 0.74, ao=0.74)
    rough = atlas.noise(c, 21, 1.2, tile_y=4)
    sy, sx = c.sl(0, ATLAS, y0, y0 + h)
    face = c.height[sy, sx] > 0.0
    c.height[sy, sx] += np.where(face, 0.004 * rough[sy, sx], 0.0)


def paint_shop(c):
    """The shopfront: 1 m lights, a heavier mullion every second one, a
    transom at door head height and a kick panel on the ground.

    The mullions are placed by distance to the nearest light line, so the one
    at u = 0 is whole at both edges of the sheet and the band tiles."""
    y0 = SHOP_Y0
    c.paint(0, ATLAS, y0, y0 + SHOP_H, mid=ID_GLASS, shade=1.0, ao=1.0, height=0.0)
    c.paint(0, ATLAS, y0, y0 + m(Z_KICK), mid=ID_KICK, shade=1.0, ao=0.92, height=0.010)
    for a0, a1, ao in ((m(Z_KICK), m(Z_KICK + 0.07), 0.80),
                       (m(Z_LEAF - 0.04), m(Z_LEAF + 0.04), 0.84),
                       (m(Z_HEAD - 0.10), SHOP_H, 0.78)):
        c.paint(0, ATLAS, y0 + a0, y0 + a1, mid=ID_FRAME, ao=ao)
        c.bevel(0, ATLAS, y0 + a0, y0 + min(a1, SHOP_H), FRAME_H, 1.0, axes="y")
    sy, sx, _, X = c.field(0, ATLAS, y0 + m(Z_KICK), y0 + SHOP_H)
    lp = m(LIGHT)
    k = np.round(X / lp)
    d = np.abs(X - k * lp)
    heavy = (k.astype(np.int64) % int(round(MULLION / LIGHT))) == 0
    hw = np.where(heavy, m(0.09) / 2.0, m(0.05) / 2.0)
    hit = d < hw
    c.mid[sy, sx] = np.where(hit, ID_FRAME, c.mid[sy, sx])
    c.ao[sy, sx] = np.where(hit, np.where(heavy, 0.80, 0.86), c.ao[sy, sx])
    c.height[sy, sx] = np.where(
        hit, np.maximum(c.height[sy, sx], FRAME_H * np.clip(hw - d, 0.0, 1.0)),
        c.height[sy, sx])
    # glass sits behind its frame, so the pane is occluded at its edges
    grad = np.linspace(0.90, 1.0, int(m(0.25)))
    for i, g in enumerate(grad):
        c.mul(0, ATLAS, y0 + m(Z_KICK + 0.07) + i, y0 + m(Z_KICK + 0.07) + i + 1,
              1.0, ao=g)
        c.mul(0, ATLAS, y0 + m(Z_HEAD - 0.10) - i - 1, y0 + m(Z_HEAD - 0.10) - i,
              1.0, ao=g)


def paint_soffit(c):
    """White painted wood: the fascia face in the band's bottom 0.375 m, the
    boarded soffit above it, running out from the wall."""
    y0 = SOF_Y0
    c.paint(0, ATLAS, y0, y0 + SOF_H, mid=ID_EAVE, shade=1.0, ao=1.0, height=0.0)
    c.mul(0, ATLAS, y0, y0 + 2, 0.82, ao=0.80)                  # drip edge
    c.mul(0, ATLAS, y0 + SOF_FASCIA - 2, y0 + SOF_FASCIA, 0.90, ao=0.86)
    pitch = m(0.20)                                             # board width
    for i in range(int(ATLAS / pitch) + 1):
        u = i * pitch
        c.mul(u - 1, u + 1, y0 + SOF_FASCIA, y0 + SOF_H, 0.92, ao=0.88)
        c.lift(u - 1, u + 1, y0 + SOF_FASCIA, y0 + SOF_H, -BOARD_JOINT)
        c.mul(u - 1, u + 1, y0, y0 + SOF_FASCIA - 2, 0.96)
        c.lift(u - 1, u + 1, y0, y0 + SOF_FASCIA - 2, -BOARD_JOINT)
    # a soffit is a ceiling: darkest where it meets the wall, which is v = 0
    sy, sx, Y, _ = c.field(0, ATLAS, y0 + SOF_FASCIA, y0 + SOF_H)
    f = 0.70 + 0.30 * np.minimum(1.0, (Y - (y0 + SOF_FASCIA)) / m(0.9))
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], f)


def pad_periodic(c, y0, h, n=PAD):
    """Carry a band that repeats vertically into its gutter from its *other*
    end, because that is the artwork a sample straddling the wrap line should
    find. atlas.pad() then fills everything else from the nearest edge."""
    s = c.ss
    a, b = int(round(y0 * s)), int(round((y0 + h) * s))
    fields = tuple(c.weather.f.values()) if c.weather is not None else ()
    for arr in (c.mid, c.shade, c.ao, c.height) + fields:
        arr[a - n * s:a] = arr[b - n * s:b]
        arr[b:b + n * s] = arr[a:a + n * s]


# ----------------------------------------------------------------- regions
def _border(c, rect, t, mid, shade=1.0, ao=0.9, height=0.0):
    x, y, w, h = rect
    c.paint(x, x + w, y, y + h, mid=mid, shade=shade, ao=ao, height=height)
    return (x + t, y + t, w - 2 * t, h - 2 * t)


def paint_roof(c):
    """Bitumen shingles, seen from a first-floor window or from the air.

    14 texels/metre: a tab is 13 px across and a course 5 deep, which is
    enough to read as a shingled slope at the distances this roof is seen
    from and a twentieth of the sheet rather than a quarter of it. Each course
    steps down at its lower edge; the relief is scaled by ROOF_PPM over PPM.
    """
    x, y, w, h = ROOF
    k = ROOF_PPM / PPM
    c.paint(x, x + w, y, y + h, mid=ID_ROOF, shade=1.0, ao=1.0, height=0.0)
    course = max(4, int(round(0.36 * ROOF_PPM)))
    tab = max(9, int(round(0.90 * ROOF_PPM)))
    sy, sx, Y, _ = c.field(x, x + w, y, y + h)
    s = (Y - y) % course
    c.height[sy, sx] = 0.008 * k * (1.0 - s / course)
    for j in range(h // course + 1):
        cy = y + j * course
        off = (j % 2) * (tab // 2)
        c.mul(x, x + w, cy, cy + 1, 0.82, ao=0.88)          # under the course above
        for i in range(-1, w // tab + 2):
            bx = x + off + i * tab
            c.mul(bx, bx + 1, cy + 1, cy + course, 0.88)    # tab slot
            c.lift(bx, bx + 1, cy + 1, cy + course, -0.004 * k)
            c.mul(max(x, bx + 1), min(x + w, bx + tab), cy + 1, cy + course,
                  0.90 + 0.20 * float(atlas.hash_unit(j, i)))
    c.mul(x, x + w, y + h - 4, y + h, 0.94, ao=0.94)        # ridge cap
    c.mul(x, x + w, y, y + 2, 0.88, ao=0.92)                # eave course


def paint_gable_glaze(c):
    """The curtain wall in the gable: 1 m lights, a transom every 1.2 m.

    48 texels/metre. The panel is a pentagon and this region is its bounding
    box, so the corners past the rake are never sampled; the sloped head is
    the opening's own reveal, not artwork.
    """
    x, y, w, h = GABLE_GLAZE
    k = GABLE_PPM / PPM
    c.paint(x, x + w, y, y + h, mid=ID_GLASS, shade=1.0, ao=1.0, height=0.0)
    t = GABLE_PPM * 0.07
    for u in np.arange(0.0, w + 1, GABLE_PPM * 1.0):
        c.paint(x + u - t / 2, x + u + t / 2, y, y + h, mid=ID_FRAME, ao=0.84)
        c.bevel(x + u - t / 2, x + u + t / 2, y, y + h, FRAME_H * k, 1.0, axes="x")
    for v in np.arange(0.0, h + 1, GABLE_PPM * 1.2):
        c.paint(x, x + w, y + v - t / 2, y + v + t / 2, mid=ID_FRAME, ao=0.84)
        c.bevel(x, x + w, y + v - t / 2, y + v + t / 2, FRAME_H * k, 1.0, axes="y")
    for a0, a1, b0, b1, axes in ((x, x + w, y, y + t, "y"), (x, x + t, y, y + h, "x"),
                                 (x + w - t, x + w, y, y + h, "x")):
        c.paint(a0, a1, b0, b1, mid=ID_FRAME, ao=0.78)       # sill and jamb members
        c.bevel(a0, a1, b0, b1, FRAME_H * k, 1.0, axes=axes)


def paint_door(c, leaves):
    """A shopfront entrance: leaves to 2.25 m, a transom light over them.

    A pair opens in the middle, so its two pull handles sit either side of the
    meeting stile rather than one in the middle and one out at the jamb.
    """
    rect = DOOR_DOUBLE if leaves == 2 else DOOR_SINGLE
    x, y, w, h = rect
    c.paint(x, x + w, y, y + h, mid=ID_FRAME, shade=1.0, ao=0.82, height=FRAME_H)
    c.paint(x, x + w, y, y + m(0.05), mid=ID_KICK, ao=0.78, height=0.010)   # threshold
    c.paint(x + m(0.05), x + w - m(0.05), y + m(Z_LEAF + 0.07),
            y + h - m(0.10), mid=ID_GLASS, ao=0.86, height=0.0)             # transom
    lw = (w - m(0.10)) / leaves
    for i in range(leaves):
        lx = x + m(0.05) + i * lw
        c.paint(lx, lx + lw, y + m(0.05), y + m(Z_LEAF), mid=ID_DOOR, ao=0.88)
        c.bevel(lx, lx + lw, y + m(0.05), y + m(Z_LEAF), 0.020, 1.0)
        c.paint(lx + m(0.10), lx + lw - m(0.10), y + m(0.42),
                y + m(Z_LEAF - 0.14), mid=ID_GLASS, ao=0.84, height=0.0)
        c.mul(lx, lx + m(0.02), y + m(0.05), y + m(Z_LEAF), 0.84, ao=0.80)
        c.lift(lx, lx + m(0.02), y + m(0.05), y + m(Z_LEAF), -0.010)
        # the opening edge: the far stile on a single leaf, the meeting stile
        # on the second leaf of a pair
        hx = lx + m(0.10) if (leaves == 2 and i) else lx + lw - m(0.16)
        c.paint(hx, hx + m(0.06), y + m(0.85), y + m(1.35), mid=ID_METAL,
                ao=0.86, height=0.045)


def paint_side_window(c):
    """A staff window in a stone wall, with the stone reveal painted round it
    so the flush tiers keep the same surround the cut ones have."""
    x, y, w, h = SIDE_WINDOW
    inner = _border(c, SIDE_WINDOW, int(m(0.15)), ID_STONE, 0.86, 0.80)
    ix, iy, iw, ih = inner
    c.paint(ix, ix + iw, iy, iy + ih, mid=ID_FRAME, ao=0.84)
    c.bevel(ix, ix + iw, iy, iy + ih, FRAME_H, 1.0)
    c.paint(ix + m(0.07), ix + iw - m(0.07), iy + m(0.07), iy + ih - m(0.07),
            mid=ID_GLASS, ao=0.88, height=0.0)
    c.paint(ix + iw / 2 - m(0.03), ix + iw / 2 + m(0.03), iy, iy + ih,
            mid=ID_FRAME, ao=0.86)
    c.bevel(ix + iw / 2 - m(0.03), ix + iw / 2 + m(0.03), iy + m(0.07),
            iy + ih - m(0.07), FRAME_H, 1.0, axes="x")
    c.mul(x, x + w, y, y + m(0.06), 0.78, ao=0.76)              # weathered sill


def paint_maint_door(c):
    x, y, w, h = MAINT_DOOR
    inner = _border(c, MAINT_DOOR, int(m(0.10)), ID_FRAME, 1.0, 0.80, height=0.020)
    ix, iy, iw, ih = inner
    c.paint(ix, ix + iw, iy, iy + ih, mid=ID_DOOR, ao=0.88, height=0.0)
    for i in range(4):                                          # bottom louvre
        ly = iy + m(0.18) + i * m(0.08)
        c.paint(ix + m(0.12), ix + iw - m(0.12), ly, ly + m(0.04),
                mid=ID_STEEL, ao=0.72)
        sy, sx, Y, _ = c.field(ix + m(0.12), ix + iw - m(0.12), ly, ly + m(0.04))
        c.height[sy, sx] = 0.012 * (1.0 - (Y - ly) / m(0.04))
    c.paint(ix + iw - m(0.16), ix + iw - m(0.11), iy + m(0.95), iy + m(1.15),
            mid=ID_METAL, ao=0.84, height=0.030)
    c.mul(ix, ix + iw, iy, iy + m(0.10), 0.84, ao=0.80)


def paint_ahu(c):
    """The wall-hung air handler: a painted steel case, mostly grille."""
    x, y, w, h = AHU_SIDE
    inner = _border(c, AHU_SIDE, int(m(0.08)), ID_STEEL, 1.0, 0.86, height=0.020)
    ix, iy, iw, ih = inner
    c.paint(ix, ix + iw, iy, iy + ih, mid=ID_STEEL, shade=0.82, ao=0.78, height=-0.010)
    for i in range(int(ih / m(0.10)) + 1):                      # louvre blades
        ly = iy + i * m(0.10)
        c.paint(ix, ix + iw, ly, ly + m(0.05), mid=ID_STEEL, shade=1.0, ao=0.90)
        sy, sx, Y, _ = c.field(ix, ix + iw, ly, ly + m(0.05))
        c.height[sy, sx] = 0.015 * (1.0 - (Y - ly) / m(0.05))
    c.paint(ix + iw - m(0.45), ix + iw - m(0.06), iy + ih - m(0.34),
            iy + ih - m(0.06), mid=ID_STEEL, shade=1.0, ao=0.92)
    c.bevel(ix + iw - m(0.45), ix + iw - m(0.06), iy + ih - m(0.34),
            iy + ih - m(0.06), 0.012, 1.0)
    tx, ty, tw, th = AHU_TOP
    c.paint(tx, tx + tw, ty, ty + th, mid=ID_METAL, shade=1.0, ao=0.92, height=0.0)
    for i in range(6):
        a0, a1 = tx + m(0.10) + i * m(0.28), tx + m(0.13) + i * m(0.28)
        c.mul(a0, a1, ty, ty + th, 0.88, ao=0.86)
        c.lift(a0, a1, ty, ty + th, -0.004)


def paint_louvre(c):
    x, y, w, h = LOUVRE
    inner = _border(c, LOUVRE, 3, ID_STEEL, 1.0, 0.84, height=0.015)
    ix, iy, iw, ih = inner
    c.paint(ix, ix + iw, iy, iy + ih, mid=ID_STEEL, shade=0.72, ao=0.70, height=-0.010)
    for i in range(int(ih / m(0.09)) + 1):
        ly = iy + i * m(0.09)
        c.paint(ix, ix + iw, ly, ly + m(0.045), mid=ID_STEEL, shade=1.0, ao=0.88)
        sy, sx, Y, _ = c.field(ix, ix + iw, ly, ly + m(0.045))
        c.height[sy, sx] = 0.012 * (1.0 - (Y - ly) / m(0.045))


def paint_vents(c):
    x, y, w, h = VENT_BOX
    c.paint(x, x + w, y, y + h, mid=ID_STEEL, shade=1.0, ao=0.94, height=0.0)
    c.mul(x, x + w, y + h - m(0.14), y + h, 0.88, ao=0.86)      # weather hood
    c.bevel(x, x + w, y + h - m(0.14), y + h, 0.030, 1.0, axes="y")
    for i in range(3):
        a0, a1 = x + m(0.10) + i * m(0.20), x + m(0.12) + i * m(0.20)
        c.mul(a0, a1, y + m(0.10), y + h - m(0.18), 0.88)
        c.lift(a0, a1, y + m(0.10), y + h - m(0.18), -0.004)
    x, y, w, h = VENT_PIPE
    c.paint(x, x + w, y, y + h, mid=ID_STEEL, shade=1.0, ao=0.94)
    sy, sx, _, X = c.field(x, x + w, y, y + h)                  # a cylinder, across U
    u = 2.0 * (X - x) / w - 1.0
    c.height[sy, sx] = 0.05 * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.mul(x, x + w, y + h - m(0.10), y + h, 0.82, ao=0.86)
    c.mul(x, x + w, y, y + m(0.08), 0.86, ao=0.84)


# ------------------------------------------------------------ the sign work
def _mark(c, cx, cy, r, mid):
    """The centre's pharmacy mark: a bold cross with a broken ring, four short
    arcs sitting in the quadrants between its arms.

    A closed ring round a cross collapses into a phi at sign size, which is
    why the ring is cut: at twenty pixels the arcs read as a halo and the
    cross stays the shape the eye resolves first. Drawn here rather than taken
    from anywhere -- it is this asset's own device, and no real pharmacy's.
    """
    bar = 0.40 * r
    c.stroke((cx - 0.98 * r, cy), (cx + 0.98 * r, cy), bar, mid=mid)
    c.stroke((cx, cy - 0.98 * r), (cx, cy + 0.98 * r), bar, mid=mid)
    for a0 in (0, 90, 180, 270):
        pts = _arc(cx, cy, 0.86 * r, 0.86 * r, a0 + 28, a0 + 62, 8)
        for p, q in zip(pts, pts[1:]):
            c.stroke(p, q, 0.16 * r, mid=mid)


# (word, green field). The pharmacy has two boards and is not named twice: the
# left one, over its doors, is the one that carries the word, and the right is
# the mark on its own.
FASCIA_TEXT = {"salon": ("BEAUTY SALON", False), "barber": ("BARBER", False),
               "pharmacy_left": ("PHARMACY", True),
               "pharmacy_right": ("", True)}


def paint_fascia(c, key):
    """One shop's lit sign board, 4.0 x 0.75 m of it.

    The two pharmacy boards are a green field with white out of it; the salon
    and the barber are dark on white. Generic trade words, set in this sheet's
    own letterforms. The face is a flat printed diffuser.

    A board sets its word as large as it will go and no larger, so BARBER
    fills its board at the full cap height while BEAUTY SALON, twice as long,
    steps down to fit. Two tenants' signs being different sizes is what a
    parade of shops actually looks like; one of them running off its board is
    not.
    """
    word, green = FASCIA_TEXT[key]
    x0, y0, w, h = FASCIA[key]
    field, ink = (ID_SIGN_G, ID_SIGN) if green else (ID_SIGN, ID_SIGN_T)
    c.paint(x0, x0 + w, y0, y0 + h, mid=field, shade=1.0, ao=1.0, height=0.0)
    c.paint(x0, x0 + w, y0, y0 + 2, mid=ink if green else ID_SIGN_T)
    margin, x = 14.0, 14.0
    if key == "pharmacy_left":
        r = 17.0
        _mark(c, x0 + x + r, y0 + h / 2.0, r, ink)
        x += 2.9 * r
    elif not word:
        _mark(c, x0 + w / 2.0, y0 + h / 2.0, 0.34 * h, ink)
        return
    cap, weight = 26.0, 4.6
    # text_width measures centrelines; stroked letters overrun them by half a
    # stroke at each end, so the last glyph needs that back or it sets flush
    # against the edge of the board.
    avail = w - x - margin - weight
    tw = text_width(word, cap, weight=weight)
    if tw > avail:                      # uniform, so the ratio is unchanged
        cap, weight, tw = cap * avail / tw, weight * avail / tw, avail
    if key != "pharmacy_left":
        x = (w - tw) / 2.0
    text(c, word, x0 + x, y0 + (h - cap) / 2.0, cap, weight, ink)


def paint_logo(c):
    """The box sign on its stand. The whole face is clear of the roof, so
    the mark is centred on the square, between a white edge top and bottom."""
    x, y, w, h = LOGO
    c.paint(x, x + w, y, y + h, mid=ID_SIGN_G, shade=1.0, ao=1.0, height=0.0)
    c.paint(x, x + w, y + h - 4, y + h, mid=ID_SIGN)
    c.paint(x, x + w, y, y + 4, mid=ID_SIGN)
    _mark(c, x + w / 2.0, y + h / 2.0, 0.30 * h, ID_SIGN)


def paint_patches(c):
    """Flat swatches for surfaces with nothing to say: buried caps, the sign
    box's lid and underside and its stand, the plant's returns."""
    spec = {"blank": (ID_BLANK, 1.0, 1.0),
            "sign_side": (ID_SIGN_G, 0.92, 0.90),
            "steel": (ID_STEEL, 0.94, 0.90)}
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x, x + w, y, y + h, mid=mid, shade=sh, ao=ao, height=0.0)


# ------------------------------------------------------------------ checks
REGIONS = {"door_double": DOOR_DOUBLE, "door_single": DOOR_SINGLE,
           "maint_door": MAINT_DOOR, "side_window": SIDE_WINDOW, "logo": LOGO,
           "gable_glaze": GABLE_GLAZE, "ahu_side": AHU_SIDE,
           "ahu_top": AHU_TOP, "louvre": LOUVRE, "roof": ROOF,
           "vent_box": VENT_BOX, "vent_pipe": VENT_PIPE}
REGIONS.update({"fascia_" + k: v for k, v in FASCIA.items()})
REGIONS.update(PATCHES)


def check_regions():
    """Fail the bake if two regions overlap, collide with the bands, or run
    off the sheet -- including the gutter each of them needs."""
    bands_top = SOF_Y0 + SOF_H + PAD
    names = sorted(REGIONS)
    problems = []
    for i, a in enumerate(names):
        ax, ay, aw, ah = REGIONS[a]
        if (ax - PAD < 0 or ay - PAD < 0 or ax + aw + PAD > ATLAS
                or ay + ah + PAD > ATLAS):
            problems.append("%s has no room for its gutter" % a)
        if ay - PAD < bands_top:
            problems.append("%s overlaps the tiling bands" % a)
        for b in names[i + 1:]:
            bx, by, bw, bh = REGIONS[b]
            if (ax - PAD < bx + bw and bx - PAD < ax + aw
                    and ay - PAD < by + bh and by - PAD < ay + ah):
                problems.append("%s and %s overlap" % (a, b))
    for y0, h in ((STONE_Y0, STONE_H), (SHOP_Y0, SHOP_H), (SOF_Y0, SOF_H)):
        if y0 - PAD < 0:
            problems.append("band at %d has no gutter below it" % y0)
    if problems:
        raise ValueError("atlas layout: " + "; ".join(sorted(set(problems))))


# ----------------------------------------------------------------- the bake
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    The stone band repeats every 4 m up the gables, so nothing that follows
    height goes on it -- ground splash would come back at 4 and 8 m -- and its
    noise repeats on the band's period (tile_y=4). Splash goes on the
    shopfront's kick panels instead, whose band starts at the pavement. The
    shop signs are their tenants' to keep clean."""
    steel = (ID_ROOF, ID_METAL, ID_STEEL, ID_FRAME, ID_DOOR)
    w = weathering.Weather(c, clean=(ID_GLASS, ID_SIGN, ID_SIGN_G, ID_SIGN_T),
                           steel=steel, tile_y=4)
    w.grime()
    w.fade((ID_EAVE, ID_KICK))
    w.wash((ID_STONE,))
    w.splash(0, ATLAS, SHOP_Y0, SHOP_Y0 + m(Z_KICK) + 6, (ID_KICK, ID_FRAME))
    x, y, rw, rh = ROOF
    w.roof(x, x + rw, y, rh, rh / ROOF_PPM, (ID_ROOF,))
    # the shop doors: kicked feet, hand grime round the pulls
    for rect, leaves in ((DOOR_DOUBLE, 2), (DOOR_SINGLE, 1)):
        x, y, dw, dh = rect
        w.splash(x, x + dw, y, y + m(Z_LEAF), (ID_DOOR, ID_FRAME, ID_KICK),
                 amount=0.18, fall=0.15, specks=0.0)
        lw = (dw - m(0.10)) / leaves
        for i in range(leaves):
            lx = x + m(0.05) + i * lw
            hx = lx + m(0.10) if (leaves == 2 and i) else lx + lw - m(0.16)
            w.spot(hx + m(0.03), y + m(1.10), m(0.10), (ID_DOOR, ID_FRAME))
    x, y, mw, mh = MAINT_DOOR
    t = int(m(0.10))
    ix, iy, iw, ih = x + t, y + t, mw - 2 * t, mh - 2 * t
    w.door(ix, ix + iw, iy, iy + ih, (ID_DOOR, ID_STEEL),
           handle=(ix + iw - m(0.135), iy + m(1.05)))
    # the staff window's bottom rail, and runs down the stone below it
    x, y, sw, sh = SIDE_WINDOW
    t = int(m(0.15))
    w.add("D", x + t, x + sw - t, y + t, y + t + m(0.07), 0.12, (ID_FRAME,))
    w.runs(x, x + sw, y, y + t, (ID_STONE,), 0.15, fall=float(t))
    # the gable curtain wall's sill member
    x, y, gw, gh = GABLE_GLAZE
    w.add("D", x, x + gw, y, y + GABLE_PPM * 0.07, 0.10, (ID_FRAME,))
    # the plant and the vents: runs down their cases
    for x, y, pw, ph in (AHU_SIDE, LOUVRE, VENT_BOX):
        w.runs(x, x + pw, y, y + ph, (ID_STEEL,), 0.12, fall=ph / 2.0)
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_stone(c)
    paint_shop(c)
    paint_soffit(c)
    c.check_bands(BAND_IDS)

    # Wear. The stone band repeats every 256 rows, so its noise repeats on
    # that period too (tile_y=4) -- anything else would put a different
    # blemish either side of the wrap line.
    sy, _ = c.sl(0, 1, STONE_Y0, STONE_Y0 + STONE_H)
    wear = 0.025 * atlas.noise(c, 3, 40.0, tile_y=4) + 0.015 * atlas.noise(c, 4, 8.0, tile_y=4)
    rain = 0.030 * atlas.noise(c, 7, 0.8, 40.0, tile_y=4)
    c.shade[sy] *= 1.0 + wear[sy] + rain[sy]
    c.ao[sy] = np.clip(c.ao[sy] * (1.0 + wear[sy] * 0.5), 0.0, 1.0)

    paint_roof(c)
    paint_gable_glaze(c)
    paint_door(c, 2)
    paint_door(c, 1)
    paint_side_window(c)
    paint_maint_door(c)
    paint_ahu(c)
    paint_louvre(c)
    paint_vents(c)
    for key in FASCIA:
        paint_fascia(c, key)
    paint_logo(c)
    paint_patches(c)

    sheeted = np.isin(c.mid, (ID_EAVE, ID_ROOF, ID_STEEL, ID_METAL, ID_DOOR))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    soft = atlas.noise(c, 11, 20.0)
    c.shade[sheeted] *= 1.0 + 0.014 * grain[sheeted] + 0.02 * soft[sheeted]

    weather(c)
    pad_periodic(c, STONE_Y0, STONE_H)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    t[ID_STONE] = pal["stone"]
    t[ID_ROOF] = pal["roof"]
    t[ID_EAVE] = pal["eave"]
    t[ID_DOOR] = pal["door"]
    t[ID_KICK] = pal["kick"]
    return t


def export(out_dir, ss=atlas.SS):
    """Candidate glazing in the emission map is neutral white so it reads as
    glazing downstream; the four shop boards and the sign on the ridge carry
    their own colours (EMIT). No occupancy or schedule is baked in."""
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.012)
    c.weather.dust(cav, (ID_STONE,))                 # in the bed joints
    rough = 0.04 * atlas.noise(c, 13, 20.0, tile_y=4)
    path = os.path.join(out_dir, ASSET)
    # A door unit is one opening into one shop, so its leaves, their vision
    # panels and the transom above them have to be one room, by day and by
    # night. The default merge bridges a glazing bar, not a pair of 0.10 m
    # meeting stiles, and left to it the two leaves of the pharmacy's doors
    # came out at different levels with a lit wall behind one of them. The
    # doors are painted first, with a merge wide enough to reach across their
    # stiles; everything else keeps the shared default.
    cover = atlas.coverage(c, ID_GLASS)
    glass = cover >= 0.5
    door = np.zeros_like(glass)
    for dx, dy, dw, dh in (DOOR_DOUBLE, DOOR_SINGLE):
        door[dy:dy + dh, dx:dx + dw] = True
    emit = atlas.emission_colours(c, EMIT)
    emit = glazing.night_rooms((cover > 0) & door, emit, merge=8)
    emit = glazing.night_rooms((cover > 0) & ~door, emit)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS,)), path + "_normal.png"),
               atlas.save(emit, path + "_emission.png")]
    for v in VARIANTS:
        rgb = atlas.albedo(c, lut(v), grime=0.25 * cav)
        rgb = glazing.rooms(glass & door, rgb, merge=8)
        rgb = glazing.rooms(glass & ~door, rgb)
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(os.path.basename(p))
    else:
        paint()
        print("atlas layout and bands check out")
