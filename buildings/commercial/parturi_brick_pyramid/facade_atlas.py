# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
parturi_brick_pyramid.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
plan size, wall heights, the roof's pitch, band rows, opening sizes, region
rectangles -- so a change here cannot leave the UVs pointing at the wrong
artwork.

The atlas is a trim sheet. Four bands run the full width and tile in U:

    rows   0 .. 220   BRICK    facing brick in stretcher bond, z 0 .. 3.4375 m,
                               the dark plinth brick in its five lowest courses
    rows 226 .. 456   ROOF     brown standing-seam steel, V up the slope
    rows 462 .. 478   FASCIA   brown sheet fascia with the gutter across its top
    rows 482 .. 511   SOFFIT   stained soffit boards, V out from the wall

Above them, one region for everything singular: the lobby's glazed screen,
the windows and the service door (each with the soldier course over it and,
for a window, the sheet sill under it), the meter cupboard, the louvre, the
ventilation housing, the projecting light box's face, and the lettered sign
band across the front. A row of flat 16 px patches serves faces that take one
colour. atlas.pad() fills every sample no region claims.

The brick is drawn at its true size: a 285 x 85 mm module, joints included
(56 stretchers across the 16 m atlas, 5.5 px a course), so a 2.1 m door leaf
stands 24 or 25 courses tall, as it would on site. Every height the walls
share with the coursing -- plinth, sills, heads, soldier courses, the sign
band -- falls on a course line.

Rasterising is scripts/atlas.py's (numpy, scipy; Pillow to save);
weathering is scripts/weathering.py's at the catalog's moderate level, and
glass is scripts/glazing.py's room behind the pane.
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

ASSET = "parturi_brick_pyramid"
ATLAS = 1024
PPM = 64.0

# ------------------------------------------------------------------- plan
HX, HY = 5.0, 4.0           # half the wall plan: 10 x 8 m, front along X
EAVE_OUT = 0.453125         # 29 px; the eave's projection on all four sides
TAN = 0.40                  # rise per metre, all four slopes: 21.8 degrees

# --------------------------------------------------------------- brickwork
COURSE_PX = 5.5             # one course, bed joint included: 85.9 mm
COURSE = COURSE_PX / PPM
BRICK_PX = ATLAS / 56.0     # one stretcher, perpend included: 285.7 mm
BRICK_L = BRICK_PX / PPM
JOINT_PX = 0.75             # a 12 mm joint
BRICK_FACE = 0.006          # the brick face proud of the recessed joint


def course(n):
    """The height of course line *n* above the ground, in metres."""
    return n * COURSE


# ------------------------------------------------------------ vertical layout
Z_PLINTH = course(5)        # 0.430 m of dark plinth brick
Z_SILL_BOARD = course(9)    # the front windows' sheet sill, 0.773 .. 0.859
Z_SILL = course(10)         # the front and side windows' sill: 0.859 m
Z_SMALL_BOARD = course(14)
Z_SMALL_SILL = course(15)   # the small windows' sill: 1.289 m
Z_LEAF = 2.1                # the entrance leaf's head and every transom bar
Z_HEAD = course(27.5)       # 2.363 m: the head of every opening but one
Z_SERVICE_HEAD = course(24.5)   # 2.105 m: the service door's frame head
SOLDIER = course(3.5)       # 0.301 m: the soldier course over each opening
Z_SOLDIER = Z_HEAD + SOLDIER    # 2.664 m, on course line 31
Z_BAND0 = course(32)        # 2.75 m: the foot of the brown sign band
Z_EAVE = 3.3125             # 212 px; the level soffit meets the wall here
Z_TOP = course(40)          # 3.4375 m: the walls run into the roof to here
FASC_M = 0.25               # the fascia's depth
Z_FT = Z_EAVE + FASC_M      # 3.5625 m: the roof's top at the fascia
SLOPE_LEN = (HY + EAVE_OUT) * math.sqrt(1.0 + TAN * TAN)   # fascia to ridge
Z_RIDGE = Z_FT + (HY + EAVE_OUT) * TAN                     # 5.34 m
SERVICE_LEAF = (0.94, Z_SERVICE_HEAD - 0.05)   # the service door's clear leaf

# ------------------------------------------------------------------ openings
# kind -> width, opening bottom, opening top, the strip under it (a sheet
# sill), the strip over it (the soldier course), reveal depth, style.
ITEMS = {
    "screen": dict(w=2.2, z0=0.0, z1=Z_HEAD, cb=0.0, ct=SOLDIER, depth=0.90),
    "window": dict(w=1.8, z0=Z_SILL, z1=Z_HEAD, cb=COURSE, ct=SOLDIER, depth=0.12),
    "side_window": dict(w=1.4, z0=Z_SILL, z1=Z_HEAD, cb=COURSE, ct=SOLDIER, depth=0.12),
    "small_window": dict(w=0.9, z0=Z_SMALL_SILL, z1=Z_HEAD, cb=COURSE, ct=SOLDIER,
                         depth=0.12),
    "service_door": dict(w=1.06, z0=0.0, z1=Z_SERVICE_HEAD, cb=0.0, ct=SOLDIER,
                         depth=0.12),
    "meter": dict(w=0.6, z0=0.55, z1=1.65, cb=0.0, ct=0.0, depth=0.0),
    "louvre": dict(w=0.5, z0=2.15, z1=2.45, cb=0.0, ct=0.0, depth=0.0),
}
SCREEN_FRAME = 0.06         # the lobby screen's frame and mullion
DOOR_LEAF_W = 0.95          # the entrance leaf, stiles included
DOOR_S0 = SCREEN_FRAME      # the leaf's left edge, from the screen's left


def item_box(kind):
    """(bottom, top) of the rectangle an item takes on its wall."""
    it = ITEMS[kind]
    return it["z0"] - it["cb"], it["z1"] + it["ct"]


def item_size_m(kind):
    b, t = item_box(kind)
    return ITEMS[kind]["w"], t - b


# ------------------------------------------------------------------- bands
PAD = 2
BRICK_Y0, BRICK_H = 0, Z_TOP * PPM            # 220 rows
ROOF_Y0, ROOF_RPM = 226, 48.0                 # roof band, rows per metre of slope
ROOF_H = SLOPE_LEN * ROOF_RPM                 # 230.2 rows
FASC_Y0, FASC_H = 462, FASC_M * PPM           # 16 rows
GUTTER_PX = 9.0
PIPE_STRIP = (FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 - 2.5,
              FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 + 2.5)
SOF_Y0, SOF_H = 482, EAVE_OUT * PPM           # 29 rows
SEAM_PX = 32.0              # standing seams every 0.5 m

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels, 64 px/m unless stated. check_regions() asserts they
# neither overlap nor run off the sheet.
SIGN_BAND_S = (0.2, 9.8)    # the band's run along the front wall
SIGN_PPM = 160.0            # the light box's face is denser: lettering


def _region(x, y, kind):
    w, h = item_size_m(kind)
    return (x, y, w * PPM, h * PPM)


ITEM_REGION = {
    "screen": _region(4, 516, "screen"),
    "window": _region(150, 516, "window"),
    "side_window": _region(270, 516, "side_window"),
    "small_window": _region(364, 516, "small_window"),
    "service_door": _region(426, 516, "service_door"),
    "meter": _region(500, 516, "meter"),
    "louvre": _region(544, 516, "louvre"),
}
# the ventilation housing: one side's run (up to 1.0 m) by its height
HOUSING_HALF = (0.5, 0.4)   # half its plan, along X and Y
HOUSING_BURY = 0.45         # below the ridge, into the roof
HOUSING_UP = 0.50           # above the ridge to its lid
HOUSING_LID = (0.06, 0.05)  # lid thickness, overhang
HOUSING = (584, 516, 64.0, (HOUSING_BURY + HOUSING_UP) * PPM)
SIGN_BOX_M = 0.70           # the light box's face, square
SIGN_BOX = (656, 516, SIGN_BOX_M * SIGN_PPM, SIGN_BOX_M * SIGN_PPM)
SIGN_BAND = (4, 700, (SIGN_BAND_S[1] - SIGN_BAND_S[0]) * PPM, (Z_TOP - Z_BAND0) * PPM)

PATCH_NAMES = ("blank", "reveal", "sill_top", "flashing", "lid", "sign_rim",
               "bracket", "band_edge", "canopy_top", "canopy_edge", "canopy_under",
               "screen_frame")
PATCHES = {n: (4 + 20 * i, 1000, 16, 16) for i, n in enumerate(PATCH_NAMES)}

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_MORTAR, ID_ROOF, ID_FASCIA = 0, 1, 2, 3, 4, 5
ID_SOFFIT, ID_FRAME, ID_GLASS, ID_DOOR, ID_GUTTER = 6, 7, 8, 9, 10
ID_SIGN_W, ID_SIGN_INK, ID_SIGN_RIM, ID_LETTER, ID_METAL = 11, 12, 13, 14, 15
ID_SEAL = 16                # black rubber and the dark gap round a leaf

# (roughness, metallic). The roof, fascia, gutter and frames are factory
# polyester-coated steel and aluminium: painted, so not metallic.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.84, 0.0), ID_BRICK: (0.86, 0.0),
    ID_MORTAR: (0.93, 0.0), ID_ROOF: (0.46, 0.0), ID_FASCIA: (0.46, 0.0),
    ID_SOFFIT: (0.78, 0.0), ID_FRAME: (0.40, 0.0), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_DOOR: (0.48, 0.0), ID_GUTTER: (0.40, 0.0), ID_SIGN_W: (0.22, 0.0),
    ID_SIGN_INK: (0.22, 0.0), ID_SIGN_RIM: (0.42, 0.0), ID_LETTER: (0.36, 0.0),
    ID_METAL: (0.50, 0.60), ID_SEAL: (0.70, 0.0),
}

# ---------------------------------------------------------------- palettes
# A late-1980s brick pavilion's four bricks. The brown roof, fascia, soffit,
# frames and doors move a little with each; the signs do not.
VARIANTS = {
    "yellow_brick": {"brick": (198, 174, 130), "mortar": (166, 160, 148),
                     "plinth": (84, 62, 50), "roof": (98, 68, 52),
                     "fascia": (88, 63, 48), "soffit": (122, 92, 68),
                     "frame": (94, 68, 50), "door": (100, 73, 54)},
    "red_brick": {"brick": (150, 82, 64), "mortar": (156, 150, 140),
                  "plinth": (72, 54, 46), "roof": (86, 60, 50),
                  "fascia": (80, 58, 48), "soffit": (114, 86, 66),
                  "frame": (84, 62, 50), "door": (92, 68, 54)},
    "brown_brick": {"brick": (118, 82, 62), "mortar": (146, 138, 126),
                    "plinth": (64, 48, 42), "roof": (74, 57, 48),
                    "fascia": (70, 53, 44), "soffit": (108, 82, 62),
                    "frame": (74, 56, 46), "door": (84, 63, 50)},
    "white_brick": {"brick": (214, 210, 198), "mortar": (184, 182, 176),
                    "plinth": (86, 66, 54), "roof": (102, 72, 55),
                    "fascia": (92, 66, 50), "soffit": (126, 96, 72),
                    "frame": (96, 70, 52), "door": (104, 77, 57)},
}
DEFAULT_VARIANT = "yellow_brick"

FIXED = {
    ID_GLASS: glazing.BASE, ID_BLANK: (52, 52, 52),
    ID_SIGN_W: (232, 230, 222), ID_SIGN_INK: (34, 48, 104),
    ID_SIGN_RIM: (52, 58, 72), ID_LETTER: (226, 212, 178),
    ID_METAL: (128, 126, 120), ID_SEAL: (34, 33, 32),
}

# The candidate-glazing mask doubles as the emission map. Glass is neutral
# white, so scripts/validate_asset.py picks it out as glazing. The light box
# and the band's letters are luminous fixtures, not windows, and are written
# in their own clearly coloured light (channel spread far above the
# validator's 24): a bright neutral pixel would be measured as glazing. The
# light box's opal face glows a warm white and its letters and pictogram a
# deep blue through the acrylic; the band's brown field stays dark and only
# its cut letters, backlit, glow cream.
EMIT = {ID_GLASS: (255, 255, 255), ID_SIGN_W: (255, 228, 170),
        ID_SIGN_INK: (52, 84, 200), ID_LETTER: (255, 214, 140)}
# Linear RGB: a lit salon's fluorescent tubes, not a living room's lamp.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
FRAME_H = 0.025      # frames proud of the glass
SEAM_H = 0.025       # the roof's standing seams
GUTTER_R = 0.06      # the half-round gutter's roll
LETTER_H = 0.02      # the band's cut letters, proud of the sheet
PANEL_H = 0.004      # pressed lines in sheet steel


# ================================================================== painting
def m(v):
    """Metres -> pixels."""
    return v * PPM


def text(c, word, x, y, cap, weight, mid, tracking=0.14, shade=1.0, ao=None,
         height=None):
    """Set *word* with its baseline at y and its left edge at x, as stroked
    centrelines from GLYPHS at *cap* pixels per em. No font file is read, so
    the artwork carries no third party's licence."""
    cx, prev, ratio = float(x), None, weight / float(cap)
    for ch in word:
        cx += _step(prev, ch, tracking, ratio) * cap
        for poly in GLYPHS[ch][1]:
            for (ax, ay), (bx, by) in zip(poly, poly[1:]):
                c.stroke((cx + ax * cap, y + ay * cap), (cx + bx * cap, y + by * cap),
                         weight, mid, shade, ao, height=height)
        prev = ch
    return cx + GLYPHS[prev][0] * cap - x if prev else 0.0


def _arc(cx, cy, rx, ry, a0, a1, n=16):
    a = np.radians(np.linspace(a0, a1, n + 1))
    return list(zip(cx + rx * np.cos(a), cy + ry * np.sin(a)))


# A plain geometric sans, stroked centrelines on a unit em: y = 0 the
# baseline, y = 1 the cap line, the advance first. Only P A R T U I.
GLYPHS = {
    "P": (0.62, [[(0.00, 0.00), (0.00, 1.00), (0.30, 1.00)]
                 + _arc(0.30, 0.755, 0.32, 0.245, 90, -90, 10)
                 + [(0.00, 0.51)]]),
    "A": (0.70, [[(0.00, 0.00), (0.35, 1.00), (0.70, 0.00)],
                 [(0.105, 0.30), (0.595, 0.30)]]),
    "R": (0.64, [[(0.00, 0.00), (0.00, 1.00), (0.30, 1.00)]
                 + _arc(0.30, 0.755, 0.32, 0.245, 90, -90, 10)
                 + [(0.00, 0.51)],
                 [(0.28, 0.51), (0.64, 0.00)]]),
    "T": (0.68, [[(0.00, 1.00), (0.68, 1.00)], [(0.34, 1.00), (0.34, 0.00)]]),
    "U": (0.66, [[(0.00, 1.00), (0.00, 0.24)]
                 + _arc(0.33, 0.24, 0.33, 0.24, 180, 360, 12)
                 + [(0.66, 1.00)]]),
    "I": (0.00, [[(0.00, 0.00), (0.00, 1.00)]]),
}


def _step(prev, ch, tracking, ratio):
    if prev is None:
        return 0.0
    return GLYPHS[prev][0] + tracking + ratio


def text_width(word, cap, tracking=0.14, weight=0.0):
    """Centreline extent of *word*; the ink is *weight* wider."""
    if not word:
        return 0.0
    ratio = weight / float(cap)
    w = sum(_step(word[i - 1], word[i], tracking, ratio) for i in range(1, len(word)))
    return (w + GLYPHS[word[-1]][0]) * cap


# ------------------------------------------------------------------- brick
def bond(c, x0, x1, y0, y1, y_ref, x_ref=0.0, plinth_rows=None):
    """Stretcher bond over a rect: courses counted up from row *y_ref* (the
    ground), stretchers from column *x_ref*. Joints are ID_MORTAR, recessed;
    each brick's tone is hashed from its index modulo the atlas's 56
    stretchers, so a band's bond and colour both wrap exactly. Courses under
    *plinth_rows* rows are the dark plinth brick."""
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    if Y.size == 0:
        return
    yy = Y - y_ref
    r = np.floor(yy / COURSE_PX).astype(np.int64)
    off = (r % 2) * BRICK_PX * 0.5
    xb = X - x_ref - off
    b = np.floor(xb / BRICK_PX).astype(np.int64)
    bed = (yy - r * COURSE_PX) < JOINT_PX
    perp = (xb - b * BRICK_PX) < JOINT_PX
    joint = bed | perp
    bi = b % 56
    tone = 0.88 + 0.22 * atlas.hash_unit(bi, r % 4096, 17)
    # a few darker, harder-fired bricks, as in any buff brickwork
    tone = np.where(atlas.hash_unit(bi, r % 4096, 29) > 0.93, tone * 0.86, tone)
    brick = np.full(Y.shape, ID_BRICK, np.uint8)
    if plinth_rows is not None:
        brick = np.where(yy < plinth_rows, ID_PLINTH, ID_BRICK).astype(np.uint8)
    c.mid[sy, sx] = np.where(joint, ID_MORTAR, brick).astype(np.uint8)
    c.shade[sy, sx] = np.where(joint, 1.0, tone)
    c.ao[sy, sx] = np.where(joint, 0.76, 1.0)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)


def soldier(c, x0, x1, y0, y1):
    """A soldier course: bricks on end, one course wide, from column x0;
    bed joints along its foot and its head."""
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    if Y.size == 0:
        return
    k = np.floor((X - x0) / COURSE_PX).astype(np.int64)
    perp = (X - x0 - k * COURSE_PX) < JOINT_PX
    bed = ((Y - y0) < JOINT_PX) | ((y1 - Y) < JOINT_PX * 0.5)
    joint = perp | bed
    # a shade under the walling: soldiers show their ends' harder skin, and
    # the course reads as a lintel from the street
    tone = 0.80 + 0.18 * atlas.hash_unit(k, int(x0), 41)
    c.mid[sy, sx] = np.where(joint, ID_MORTAR, ID_BRICK).astype(np.uint8)
    c.shade[sy, sx] = np.where(joint, 1.0, tone)
    c.ao[sy, sx] = np.where(joint, 0.76, 1.0)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)


def paint_brick_band(c):
    """Every wall, the lobby's cheeks and the side of every reveal: buff
    stretcher bond from the ground, the lowest five courses the dark plinth
    brick, laid in the same bond."""
    bond(c, 0, ATLAS, BRICK_Y0 - PAD, BRICK_Y0 + BRICK_H + PAD, BRICK_Y0,
         plinth_rows=m(Z_PLINTH))
    # the plinth's top joint reads a little deeper: a damp-proof course
    y = BRICK_Y0 + m(Z_PLINTH)
    c.mul(0, ATLAS, y - 0.2, y + JOINT_PX, 0.86, ao=0.70)


# -------------------------------------------------------------------- roof
def paint_roof(c):
    """Standing-seam steel, V up the slope at ROOF_RPM rows a metre. Seams
    vary in U only; the snow guard and the ridge flashing vary in V, so
    their heights are scaled by the band's px/m over PPM to keep the slope
    the normal map derives from physical."""
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_ROOF, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    xm = X % SEAM_PX
    v = Y - y0
    rib = xm < 2.0
    height = np.where(rib, SEAM_H * np.clip(np.sin(np.pi * xm / 2.0), 0.0, 1.0), 0.0)
    shade = np.where((xm >= 2.0) & (xm < 3.0), 0.92, 1.0)
    ao = np.where((xm >= 2.0) & (xm < 3.0), 0.84, 1.0)
    # the pan's faint stiffening lines
    shade = np.where((np.abs(xm - 12.0) < 0.5) | (np.abs(xm - 22.0) < 0.5), shade * 0.97, shade)
    shade = np.where(v < 3, shade * 0.86, shade)                  # drip edge
    rpm = ROOF_RPM
    k = rpm / PPM
    g = round(0.55 * rpm)
    for t0, t1 in ((g, g + 2.0), (g + 3.0, g + 4.5)):
        inside = (v >= t0) & (v < t1)
        tube = 0.035 * k * np.sqrt(np.clip(1.0 - (2.0 * (v - t0) / (t1 - t0) - 1.0) ** 2, 0, 1))
        height = np.where(inside, np.maximum(height, tube), height)
    shade = np.where((v >= g - 3) & (v < g - 1), shade * 0.82, shade)
    ao = np.where((v >= g - 3) & (v < g + 4.5), np.minimum(ao, 0.85), ao)
    bracket = (xm >= 29.0) & (xm < 31.0) & (v >= g - 3) & (v < g + 4.5)
    height = np.where(bracket, 0.030 * k, height)
    shade = np.where(bracket, shade * 0.76, shade)
    ridge = v >= h - 10
    height = np.where(ridge, 0.008 * k, height)
    shade = np.where(ridge, 0.97, shade)
    shade = np.where((v >= h - 10) & (v < h - 9), shade * 0.84, shade)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao


def paint_fascia(c):
    """The eave's vertical edge: brown sheet fascia, with the half-round
    gutter hung across its top, where the water leaves the roof."""
    y0 = FASC_Y0
    top = y0 + FASC_H
    c.paint(0, ATLAS, y0 - PAD, top + PAD, ID_FASCIA, 1.0, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 - PAD, y0 + 1, ID_FASCIA, 0.84)           # folded lower edge
    gh = GUTTER_PX
    g0 = top - 1 - gh
    c.paint(0, ATLAS, g0, top - 1, ID_GUTTER, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top - 1)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_GUTTER, 0.80)
    c.paint(0, ATLAS, top - 1, top + PAD, ID_GUTTER, 0.78, height=0.0)   # the roof's drip
    c.ao[c.sl(0, ATLAS, g0 - 3, top + PAD)] = 0.9
    for i, f in enumerate((0.90, 0.85, 0.80)):                     # under the gutter
        c.mul(0, ATLAS, g0 - 3 + i, g0 - 2 + i, f)
    sy, sx, _, X = c.field(0, ATLAS, g0 + 2, top - 1)
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.80, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_soffit(c):
    """Stained tongue-and-groove soffit boards running along the eave, a
    ventilation gap at the wall. V is the distance out from the wall."""
    y0, h = SOF_Y0, SOF_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_SOFFIT, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    board = h / 5.0
    vb = (Y - y0) % board
    groove = vb < 0.6
    c.shade[sy, sx] = np.where(groove, 0.80, 1.0)
    c.ao[sy, sx] = np.where(groove, 0.80, 1.0)
    c.height[sy, sx] = np.where(groove, -0.003, 0.0)
    # darker toward the wall, where it sees least sky; the vent gap there
    t = np.clip((Y - y0) / float(h), 0.0, 1.0)
    c.shade[sy, sx] *= 0.80 + 0.20 * t
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.78 + 0.22 * t)
    c.paint(0, ATLAS, y0 - PAD, y0 + 1.5, ID_SEAL, 1.0, 0.7)
    sy, sx, _, X = c.field(0, ATLAS, y0 - PAD, y0 + 1.5)
    c.shade[sy, sx] = np.where((X % 4.0) < 1.0, 1.4, 1.0)


# ----------------------------------------------------------------- regions
def _frame(c, rect, t, mid, shade=1.0, ao=0.9, height=None):
    x, y, w, h = rect
    for a0, a1, b0, b1, axes in ((x, x + w, y, y + t, "y"), (x, x + w, y + h - t, y + h, "y"),
                                 (x, x + t, y, y + h, "x"), (x + w - t, x + w, y, y + h, "x")):
        c.paint(a0, a1, b0, b1, mid, shade, ao)
        if height is not None:
            c.bevel(a0, a1, b0, b1, height, 1.0, axes=axes)


def bar(c, a0, a1, b0, b1, mid=ID_FRAME, shade=1.0, ao=0.86, h=FRAME_H, axes="xy"):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, 1.0, axes=axes)


def _sill(c, x, y, w, rows):
    """A folded sheet-steel sill in the frame colour, its nose catching the
    light and a shadow line under its drip."""
    c.paint(x, x + w, y, y + rows, ID_FRAME, 1.0, 0.9)
    c.bevel(x, x + w, y + 1.0, y + rows, 0.012, 1.5, axes="y")
    c.mul(x, x + w, y, y + 1.0, 0.70, ao=0.70)


def paint_window(c, kind):
    """A window: the sheet sill below, the brown frame with one big light
    under a top light (the side window also split by a mullion; the small
    one a single opening light), and the soldier course over it."""
    x, y, w, h = ITEM_REGION[kind]
    it = ITEMS[kind]
    yb = y + m(it["cb"])
    yt = yb + m(it["z1"] - it["z0"])
    _sill(c, x, y, w, m(it["cb"]))
    c.paint(x, x + w, yb, yt, ID_GLASS, 1.0, 1.0, height=0.0)
    f = m(0.06)
    bar(c, x, x + w, yb, yb + f, axes="y")
    bar(c, x, x + w, yt - f, yt, axes="y")
    bar(c, x, x + f, yb, yt, axes="x")
    bar(c, x + w - f, x + w, yb, yt, axes="x")
    c.mul(x, x + w, yt - f - 3, yt - f, 0.9, ao=0.82)       # under the head frame
    if kind != "small_window":
        ytr = yb + m(Z_LEAF - it["z0"])
        bar(c, x, x + w, ytr - 1.6, ytr + 1.6, axes="y")
    if kind == "side_window":
        mx = x + w * 0.5
        bar(c, mx - 1.6, mx + 1.6, yb, yb + m(Z_LEAF - it["z0"]), axes="x")
    if kind == "small_window":
        # an opening light: its own sash inside the frame
        _frame(c, (x + f, yb + f, w - 2 * f, yt - yb - 2 * f), 2.2, ID_FRAME, 0.94,
               0.84, FRAME_H * 0.6)
    soldier(c, x, x + w, yt, y + h)


def paint_screen(c):
    """The lobby's glazed screen, set 0.9 m back: the entrance leaf on the
    left, a sidelight with a kick panel on the right, a transom bar across
    both at the leaf's 2.1 m head and a transom light above; brown aluminium
    throughout. The soldier course over the lobby's mouth is in the region's
    top rows, on the wall plane."""
    x, y, w, h = ITEM_REGION["screen"]
    it = ITEMS["screen"]
    yt = y + m(it["z1"])
    c.paint(x, x + w, y, yt, ID_GLASS, 1.0, 1.0, height=0.0)
    f = m(SCREEN_FRAME)
    ytr = y + m(Z_LEAF)
    bar(c, x, x + f, y, yt, axes="x")
    bar(c, x + w - f, x + w, y, yt, axes="x")
    bar(c, x, x + w, yt - f, yt, axes="y")
    bar(c, x, x + w, ytr, ytr + f, axes="y")                 # transom bar
    lx0 = x + m(DOOR_S0)
    lx1 = lx0 + m(DOOR_LEAF_W)
    bar(c, lx1, lx1 + f, y, ytr, axes="x")                   # mullion
    bar(c, x + f, x + w - f, y, y + 2.0, mid=ID_SEAL, h=0.0, axes="y")   # threshold
    # the leaf: a dark gap round it, then stiles, rails, a kick rail and a
    # long pull handle on the lock side
    c.paint(lx0, lx1, y + 1.0, ytr, ID_SEAL, 1.0, 0.7)
    g = 0.6
    st = m(0.075)
    c.paint(lx0 + g, lx1 - g, y + 1.0, ytr - g, ID_GLASS, 1.0, 1.0, height=0.0)
    bar(c, lx0 + g, lx0 + g + st, y + 1.0, ytr - g, axes="x")
    bar(c, lx1 - g - st, lx1 - g, y + 1.0, ytr - g, axes="x")
    bar(c, lx0 + g, lx1 - g, ytr - g - st, ytr - g, axes="y")
    bar(c, lx0 + g, lx1 - g, y + 1.0, y + m(0.24), axes="y")
    hx = lx1 - g - st - 5.0
    bar(c, hx - 1.4, hx + 1.4, y + m(0.80), y + m(1.40), mid=ID_METAL, h=0.05)
    c.disc(hx + 2.5, y + m(1.02), 1.1, ID_METAL, 0.8, 0.8, height=0.03)
    # the sidelight's kick panel
    bar(c, lx1 + f, x + w - f, y, y + m(0.45), shade=0.94, axes="y")
    c.mul(lx1 + f, x + w - f, y + m(0.45), y + m(0.45) + 2, 0.86, ao=0.84)
    soldier(c, x, x + w, yt, y + h)


def paint_service_door(c):
    """The rear door: a brown steel leaf in a steel frame, a lever handle and
    a low grille, under its soldier course."""
    x, y, w, h = ITEM_REGION["service_door"]
    it = ITEMS["service_door"]
    yt = y + m(it["z1"])
    c.paint(x, x + w, y, yt, ID_DOOR, 1.0, 0.94, height=0.0)
    f = m(0.03)
    _frame(c, (x, y - 1, w, yt - y + 1), f, ID_FRAME, 0.9, 0.82, 0.015)
    lx0, lx1 = x + f, x + w - f
    c.paint(lx0, lx1, y, y + 1.0, ID_SEAL, 1.0, 0.7)
    for yy in (y + m(0.70), y + m(1.45)):
        c.mul(lx0 + 4, lx1 - 4, yy - 0.6, yy + 0.6, 0.86, ao=0.86)
        c.lift(lx0 + 4, lx1 - 4, yy - 0.6, yy + 0.6, -PANEL_H)
    hx, hy = lx1 - 7, y + m(1.02)
    c.disc(hx, hy, 2.4, ID_METAL, 0.85, 0.8, height=0.02)
    c.stroke((hx, hy), (hx - 7, hy), 1.6, ID_METAL, 0.9, 0.8, height=0.04)
    gy = y + m(0.12)
    c.paint(lx0 + 10, lx1 - 10, gy, gy + m(0.16), ID_DOOR, 0.9, 0.86)
    for k in range(5):
        yy = gy + 1.5 + k * 1.8
        c.mul(lx0 + 11, lx1 - 11, yy, yy + 0.8, 0.70, ao=0.75)
    soldier(c, x, x + w, yt, y + h)


def paint_meter(c):
    """The electricity meter cupboard: a grey steel door in its frame, a
    small reading window and a triangular-key lock."""
    x, y, w, h = ITEM_REGION["meter"]
    c.paint(x, x + w, y, y + h, ID_METAL, 0.92, 0.9, height=0.0)
    _frame(c, (x, y, w, h), 2.0, ID_METAL, 0.80, 0.80, 0.012)
    c.mul(x + 2, x + w - 2, y + 2, y + 3, 0.82, ao=0.8)
    c.paint(x + 8, x + w - 8, y + h - 22, y + h - 12, ID_GLASS, 1.0, 1.0, height=0.0)
    _frame(c, (x + 8, y + h - 22, w - 16, 10), 1.0, ID_METAL, 0.85, 0.84, 0.006)
    c.disc(x + w - 6, y + h * 0.45, 1.5, ID_SEAL, 1.0, 0.8, height=0.01)
    c.paint(x + 6, x + 16, y + 10, y + 14, ID_SIGN_W, 0.95, 0.9)   # a label


def paint_louvre(c):
    """A brown steel air louvre: horizontal blades in a frame."""
    x, y, w, h = ITEM_REGION["louvre"]
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 0.9, height=0.0)
    _frame(c, (x, y, w, h), 1.6, ID_FRAME, 0.92, 0.84, 0.012)
    sy, sx, Y, X = c.field(x + 1.6, x + w - 1.6, y + 1.6, y + h - 1.6)
    t = (Y - y) % 2.4
    c.shade[sy, sx] = np.where(t < 0.9, 0.55, 1.0)
    c.ao[sy, sx] = np.where(t < 0.9, 0.6, 0.92)
    c.height[sy, sx] = 0.010 * np.clip(t / 2.4, 0, 1)


def paint_housing(c):
    """The ventilation housing's sides: brown sheet, louvred in the band
    above the roof, the lowest part buried in the slope."""
    x, y, w, h = HOUSING
    c.paint(x, x + w, y, y + h, ID_FASCIA, 1.0, 0.92, height=0.0)
    z0 = y + m(HOUSING_BURY + 0.10)
    z1 = y + m(HOUSING_BURY + HOUSING_UP - 0.08)
    _frame(c, (x + 3, z0, w - 6, z1 - z0), 1.5, ID_FASCIA, 0.9, 0.86, 0.01)
    sy, sx, Y, X = c.field(x + 4.5, x + w - 4.5, z0 + 1.5, z1 - 1.5)
    t = (Y - z0) % 2.6
    c.shade[sy, sx] = np.where(t < 1.0, 0.52, 1.0)
    c.ao[sy, sx] = np.where(t < 1.0, 0.6, 0.9)
    c.height[sy, sx] = 0.010 * np.clip(t / 2.6, 0, 1)
    c.mul(x, x + w, y + h - 3, y + h, 0.82, ao=0.80)          # under the lid


def _rot(p, a):
    ca, sa = math.cos(a), math.sin(a)
    return (p[0] * ca - p[1] * sa, p[0] * sa + p[1] * ca)


def pictogram(c, cx, cy, s, mid):
    """This asset's comb and scissors: a straight comb laid at a slight
    tilt, its teeth down, and an open pair of scissors crossing its right
    end, blades up and to the right, finger rings below. *s* is pixels per
    unit; (cx, cy) the mark's centre."""
    tilt = math.radians(-8.0)

    def P(u, v):
        x, y = _rot((u, v), tilt)
        return (cx + x * s, cy + y * s)
    # the comb: a spine and a row of teeth, finer toward one end
    c.stroke(P(-3.0, 0.75), P(0.2, 0.75), 0.60 * s, mid)
    n = 19
    for k in range(n):
        u = -2.85 + 2.9 * k / (n - 1)
        length = 0.80 if k < n // 2 else 0.62
        c.stroke(P(u, 0.60), P(u, 0.60 - length), 0.14 * s, mid)
    # the scissors, open, crossing the comb's end: two blades from the
    # pivot up to the right, two finger rings down to the left
    pv = (0.55, 0.10)
    for sign in (1.0, -1.0):
        a = math.radians(40.0 + sign * 17.0)
        tip = (pv[0] + 2.6 * math.cos(a), pv[1] + 2.6 * math.sin(a))
        c.stroke(P(*pv), P(*tip), 0.26 * s, mid)
        mid_b = (pv[0] + 1.3 * math.cos(a), pv[1] + 1.3 * math.sin(a))
        c.stroke(P(*pv), P(*mid_b), 0.40 * s, mid)
        b = math.radians(40.0) + math.pi - sign * 0.42
        ring = (pv[0] + 1.25 * math.cos(b), pv[1] + 1.25 * math.sin(b))
        c.stroke(P(*pv), P(*ring), 0.26 * s, mid)
        rx, ry = P(*ring)
        c.disc(rx, ry, 0.50 * s, mid, inner=0.27 * s)
    px, py = P(*pv)
    c.disc(px, py, 0.14 * s, ID_SIGN_W)


def paint_sign_box(c):
    """The projecting light box's face, both sides alike: an opal white face
    in a thin dark rim, PARTURI in deep blue capitals across the top and
    the comb-and-scissors mark under it. 160 px/m, denser than the walls,
    so the word holds up at the distance a projecting sign is read from."""
    x, y, w, h = SIGN_BOX
    c.paint(x, x + w, y, y + h, ID_SIGN_W, 1.0, 1.0, height=0.0)
    _frame(c, SIGN_BOX, 2.5, ID_SIGN_RIM, 1.0, 0.86)
    _frame(c, (x + 5.5, y + 5.5, w - 11, h - 11), 1.1, ID_SIGN_INK)
    cap, weight, tr = 14.0, 3.0, 0.10
    word = "PARTURI"
    wide = text_width(word, cap, tr, weight)
    text(c, word, x + (w - wide) / 2.0, y + h - 15.0 - cap, cap, weight, ID_SIGN_INK, tr)
    pictogram(c, x + w * 0.54, y + h * 0.35, 12.5, ID_SIGN_INK)


def paint_sign_band(c):
    """The brown sheet band across the front: panels with pressed joints,
    folded edges top and bottom, and PARTURI in cut cream capitals proud of
    it, centred over the two windows (LETTERS_S)."""
    x, y, w, h = SIGN_BAND
    c.paint(x, x + w, y, y + h, ID_FASCIA, 1.0, 0.94, height=0.0)
    vis = m(Z_EAVE - Z_BAND0)                   # under the soffit
    c.paint(x, x + w, y, y + 1.2, ID_FASCIA, 0.80, 0.80)      # folded foot
    c.mul(x, x + w, y + vis - 2.5, y + h, 0.86, ao=0.80)
    for k in range(1, 8):
        xx = x + k * m(1.2)
        c.mul(xx - 0.5, xx + 0.5, y, y + h, 0.80, ao=0.84)
        c.lift(xx - 0.5, xx + 0.5, y, y + h, -PANEL_H)
    cap, weight, tr = 22.0, 4.6, 0.20
    word = "PARTURI"
    wide = text_width(word, cap, tr, weight)
    sc = x + m(LETTERS_S - SIGN_BAND_S[0])
    base = y + (vis - cap) / 2.0 + 0.5
    # a soft shadow ring under each letter first, then the letters
    text(c, word, sc - wide / 2.0 + 0.6, base - 0.8, cap, weight + 1.6, None, tr,
         shade=0.78, ao=0.82)
    text(c, word, sc - wide / 2.0, base, cap, weight, ID_LETTER, tr, shade=1.0, ao=1.0,
         height=LETTER_H)


LETTERS_S = 6.7             # the band's word, centred over the two windows


def paint_patches(c):
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0),
        "reveal": (ID_BRICK, 0.80, 0.66),
        "sill_top": (ID_FRAME, 0.92, 0.80),
        "flashing": (ID_ROOF, 1.06, 0.95),
        "lid": (ID_FASCIA, 1.02, 0.95),
        "sign_rim": (ID_SIGN_RIM, 1.0, 0.9),
        "bracket": (ID_SIGN_RIM, 0.9, 0.85),
        "band_edge": (ID_FASCIA, 0.84, 0.82),
        "canopy_top": (ID_ROOF, 1.0, 0.95),
        "canopy_edge": (ID_FASCIA, 1.0, 0.92),
        "canopy_under": (ID_SOFFIT, 0.82, 0.78),
        "screen_frame": (ID_FRAME, 0.9, 0.80),
    }
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x - 2, x + w + 2, y - 2, y + h + 2, mid, sh, ao, height=0.0)


# ------------------------------------------------------------------ checks
BAND_IDS = {
    "BRICK": ((0, 222), {ID_BRICK, ID_PLINTH, ID_MORTAR}),
    "ROOF": ((224, 458), {ID_ROOF}),
    "FASCIA": ((460, 480), {ID_FASCIA, ID_GUTTER}),
    "SOFFIT": ((480, 513), {ID_SOFFIT, ID_SEAL}),
}


def check_regions():
    """Fail the bake if two regions overlap, collide with the bands, run off
    the sheet, or leave their density."""
    rects = dict(ITEM_REGION)
    rects.update({"housing": HOUSING, "sign_box": SIGN_BOX, "sign_band": SIGN_BAND})
    rects.update(PATCHES)
    bands_top = SOF_Y0 + SOF_H + PAD
    names = sorted(rects)
    problems = []
    for i, a in enumerate(names):
        ax, ay, aw, ah = rects[a]
        if ax - 2 < 0 or ay - 2 < 0 or ax + aw + 2 > ATLAS or ay + ah + 2 > ATLAS:
            problems.append("%s runs off the atlas" % a)
        if ay - 2 < bands_top:
            problems.append("%s overlaps the tiling bands" % a)
        for b in names[i + 1:]:
            bx, by, bw, bh = rects[b]
            if (ax - 4 < bx + bw and bx - 4 < ax + aw
                    and ay - 4 < by + bh and by - 4 < ay + ah):
                problems.append("%s and %s overlap" % (a, b))
    if ROOF_Y0 + ROOF_H + PAD > FASC_Y0 - PAD:
        problems.append("the roof band runs into the fascia band")
    if BRICK_Y0 + BRICK_H + PAD > ROOF_Y0 - PAD:
        problems.append("the brick band runs into the roof band")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    The brick band's V is height from the ground, so splash and the
    plinth's soil land the same on every wall. Signs and glass stay clean."""
    steel = (ID_ROOF, ID_FASCIA, ID_GUTTER, ID_METAL, ID_FRAME, ID_DOOR)
    w = weathering.Weather(c, clean=(ID_GLASS, ID_SIGN_W, ID_SIGN_INK, ID_SIGN_RIM,
                                     ID_LETTER, ID_SEAL), steel=steel)
    w.grime()
    w.fade((ID_DOOR, ID_FASCIA, ID_SOFFIT, ID_FRAME))
    w.wash((ID_BRICK, ID_MORTAR))
    top = BRICK_Y0 + BRICK_H + PAD
    w.plinth(0, ATLAS, BRICK_Y0, BRICK_Y0 + m(Z_PLINTH), (ID_PLINTH, ID_MORTAR))
    w.splash(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), top, (ID_BRICK, ID_MORTAR))
    w.shelter(0, ATLAS, BRICK_Y0 + m(Z_EAVE - 0.45), BRICK_Y0 + m(Z_EAVE),
              (ID_BRICK, ID_MORTAR), amount=0.07, top=top)
    w.bloom(0, ATLAS, BRICK_Y0, BRICK_Y0 + m(0.9), (ID_BRICK, ID_MORTAR, ID_PLINTH),
            amount=0.10, fade=m(0.5))
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, SLOPE_LEN, (ID_ROOF,))
    g0 = FASC_Y0 + FASC_H - 10.0
    w.add("D", 0, ATLAS, FASC_Y0 - PAD, g0, 0.05, (ID_FASCIA,))
    w.runs(0, ATLAS, FASC_Y0 - PAD, g0, (ID_FASCIA,), 0.20, fall=6.0, lo=0.4, hi=1.6)
    # sills and frames: dirt on the sheet sill and on each frame's foot
    for kind in ("window", "side_window", "small_window"):
        x, y, rw, rh = ITEM_REGION[kind]
        it = ITEMS[kind]
        yb = y + m(it["cb"])
        w.add("D", x, x + rw, y, yb, lambda Y, X, nz: 0.10 + 0.12 * atlas.smoothstep(
            0.2, 1.4, nz("short")), (ID_FRAME,))
        w.add("D", x, x + rw, yb, yb + m(0.06), 0.10, (ID_FRAME,))
    x, y, rw, rh = ITEM_REGION["screen"]
    w.add("D", x, x + rw, y, y + m(0.45), lambda Y, X, nz: 0.12 + 0.08 * nz("blotch"),
          (ID_FRAME,))
    x, y, rw, rh = ITEM_REGION["service_door"]
    f = m(0.03)
    w.door(x + f, x + rw - f, y, y + m(ITEMS["service_door"]["z1"]), (ID_DOOR,),
           handle=(x + rw - f - 7, y + m(1.02)))
    x, y, rw, rh = HOUSING
    w.runs(x, x + rw, y, y + rh, (ID_FASCIA,), 0.16, fall=10.0)
    x, y, rw, rh = ITEM_REGION["meter"]
    w.add("D", x, x + rw, y, y + m(0.3), 0.08, (ID_METAL,))
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_brick_band(c)
    paint_roof(c)
    paint_fascia(c)
    paint_soffit(c)
    c.check_bands(BAND_IDS)
    paint_screen(c)
    for kind in ("window", "side_window", "small_window"):
        paint_window(c, kind)
    paint_service_door(c)
    paint_meter(c)
    paint_louvre(c)
    paint_housing(c)
    paint_sign_box(c)
    paint_sign_band(c)
    paint_patches(c)

    # Wear. Every field is periodic, so the bands still wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.012 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    masonry = np.isin(c.mid, (ID_BRICK, ID_PLINTH, ID_MORTAR))
    pores = atlas.noise(c, 9, 0.7)
    c.shade[masonry] *= 1.0 + 0.04 * pores[masonry]
    c.height[masonry] += 0.0006 * pores[masonry]
    sheeted = np.isin(c.mid, (ID_ROOF, ID_FASCIA, ID_DOOR, ID_GUTTER))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    c.shade[sheeted] *= 1.0 + 0.014 * grain[sheeted]
    wood = c.mid == ID_SOFFIT
    fibre = atlas.noise(c, 6, 30.0, 0.5)
    c.shade[wood] *= 1.0 + 0.05 * fibre[wood]
    weather(c)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    t[ID_BRICK] = pal["brick"]
    t[ID_MORTAR] = pal["mortar"]
    t[ID_PLINTH] = pal["plinth"]
    t[ID_ROOF] = pal["roof"]
    t[ID_FASCIA] = pal["fascia"]
    t[ID_GUTTER] = pal["fascia"]
    t[ID_SOFFIT] = pal["soffit"]
    t[ID_FRAME] = pal["frame"]
    t[ID_DOOR] = pal["door"]
    return t


BLIND = (88, 86, 80)        # sRGB: pale vertical blinds, seen in the room's shade
BLIND_MIX = 0.42
BLIND_PITCH_PX = m(0.089)   # 89 mm slats


def blinds(rgb, glass):
    """Vertical blinds behind the front windows' big lights: part of the
    room, so albedo only (the emission's panes are untouched). Painted after
    glazing.rooms(), on the glass pixels of the window region below its
    transom bar, as slats with a darker gap between them."""
    x, y, w, h = ITEM_REGION["window"]
    it = ITEMS["window"]
    yb = y + m(it["cb"])
    y0, y1 = int(math.floor(yb)), int(math.ceil(yb + m(Z_LEAF - it["z0"])))
    x0, x1 = int(math.floor(x)), int(math.ceil(x + w))
    sub = rgb[y0:y1, x0:x1]
    msk = glass[y0:y1, x0:x1]
    xs = (np.arange(x0, x1) + 0.5 - x)[None, :]
    t = (xs % BLIND_PITCH_PX) / BLIND_PITCH_PX
    slat = np.where(t < 0.85, 1.0, 0.55) * (0.94 + 0.06 * np.sin(np.pi * t))
    lin = atlas.srgb_to_linear(sub)
    target = atlas.srgb_to_linear(np.asarray(BLIND, np.float32)) * slat[..., None]
    mixed = lin * (1.0 - BLIND_MIX) + target * BLIND_MIX
    out = atlas.linear_to_srgb(mixed)
    sub[msk] = out[msk]
    return rgb


def export(out_dir, ss=atlas.SS):
    """Glazing in the emission map is neutral white, so it reads as glazing
    downstream; the light box and the band's letters carry their own
    colours (EMIT). No occupancy or schedule is baked in."""
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.010)
    c.weather.dust(cav, (ID_BRICK, ID_PLINTH, ID_MORTAR))
    rough = 0.04 * atlas.noise(c, 13, 20.0)
    path = os.path.join(out_dir, ASSET)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS, ID_SIGN_W, ID_SIGN_INK)),
                          path + "_normal.png"),
               atlas.save(glazing.night_rooms(atlas.coverage(c, ID_GLASS) > 0,
                                              atlas.emission_colours(c, EMIT)),
                          path + "_emission.png")]
    glass = atlas.coverage(c, ID_GLASS) >= 0.5
    for v in VARIANTS:
        rgb = glazing.rooms(glass, atlas.albedo(c, lut(v), grime=0.25 * cav))
        rgb = blinds(rgb, glass)
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
