# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
voimalan_konttori_brick.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
the plan, the floor, sill, door, band, deck and coping heights, band rows,
light and opening sizes, region rectangles -- so a change here cannot leave
the UVs pointing at the wrong artwork.

The atlas is a trim sheet. Four bands run the full width and tile in U:

    y    0 ..  468   BRICK    z 0 .. 7.3125 m: concrete plinth, brick, the
                              cast floor-slab band at the first floor, brick
                              up the parapet into the coping
    y  480 ..  512   COPING   the galvanised coping: its outer face (8 rows),
                              then its top (24 rows)
    y  528 ..  548   UPSTAND  the parapet's inner face: the felt turned up
                              from the deck
    y  560 ..  576   CANOPY   the entrance canopy's sheet fascia
    y  592 ..  ...   unique   the entrance with its cast surround, the service
                              door, one light of each window band, concrete,
                              the vent pipe, the ventilation housing's side,
                              the roof deck, patches

The brick band is the whole wall's height, so every wall samples it by its
own height from the ground and the plinth, the slab band and the weather at
the foot line up all round. Every band starts on a 16-row boundary, 12 or
more rows clear of the one below, so a mip 4 texel never mixes two of them.

The windows are bands of equal lights in white steel, so each band type has
one region per kind of light (a fixed light, or one with a vent sash), a
light wide at 64 px/m with half a mullion at each side: the build splits a
band's glass plane at every mullion and maps each light onto its region, so
neighbouring lights make up a whole mullion between them.

The deck is a region of its own at 32 px/m (DPPM), seen only from above.

Rasterising is scripts/atlas.py's; weathering is scripts/weathering.py's,
placed by weather() below; glass is scripts/glazing.py's.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "voimalan_konttori_brick"
ATLAS = 1024
PPM = 64.0
DPPM = 32.0             # the roof deck's region
PAD = 2                 # rows each band paints beyond its own edge

# ------------------------------------------------------------------ plan
# Front (-Y) is the long side. Walls at x = +-HX, y = +-HY: a 14 x 9 m shell.
# The lobby and stair are behind the entrance west of the middle, the control
# room in the east half of the ground storey, offices upstairs.
HX, HY = 7.0, 4.5

# ------------------------------------------------------------ vertical layout
# Metres above ground; every height a whole number of texels at 64 px/m.
Z_PLINTH = 0.625        # 40 px; cast concrete plinth under the brick
Z_FLOOR = 0.5           # 32 px; the ground floor and both thresholds
Z_FLOOR2 = 3.75         # 240 px; the first floor: 3.25 m storey
Z_BAND0 = 3.5           # 224 px; the floor slab's cast edge, flush with the
Z_BAND1 = Z_FLOOR2      # brick, from its underside to the floor
Z_DECK = 7.0            # 448 px; the roof deck: 3.25 m over the first floor
# the parapet: brick up from the walls, capped by a galvanised coping that
# oversails both faces
PIN = 0.25              # the parapet's thickness: inner face HX - PIN
COPING_H = 0.125        # 8 px; the coping's face
COPING_OUT = 0.0625     # 4 px; its oversail past either face of the parapet
Z_COP = 7.375           # 472 px; the coping's top, 0.375 m over the deck
Z_COP0 = Z_COP - COPING_H                        # 7.25, the coping's drip
Z_PAR = Z_COP - 0.0625                           # 7.3125, the brick's top,
                                                 # inside the coping

# window bands: sills over each floor, every ground-storey head on one line
# with the entrance's head
Z_SILL = Z_FLOOR + 1.0                           # 1.5, ground-floor offices
Z_SILL_CTRL = Z_FLOOR + 0.75                     # 1.25, the control room
Z_SILL2 = Z_FLOOR2 + 0.875                       # 4.625, the upper ribbon
# doors: every leaf 2.125 m; the entrance has a transom light above its pair
Z_LEAF = 2.125          # leaf height over the threshold
ENTRY_H = 2.6875        # the entrance's opening, threshold to head (3.1875)
SURROUND = 0.1875       # the entrance's cast surround, each side
SURROUND_TOP = 0.375    # and above the head, up into the canopy

# the canopy over the entrance: the first-floor slab carried out, its fascia
# in line with the painted slab band
Z_CAN0 = Z_BAND0                                 # 3.5, underside
Z_CAN1 = Z_BAND1                                 # 3.75, top

# ------------------------------------------------------------------ openings
# Window bands: kind -> (light width, band height) in metres. A band of n
# lights is n light widths long; each light samples one of its kind's
# regions (LIGHTS).
BANDS = {
    "rib": (1.5, 1.4375),           # the upper storey's ribbon
    "ctrl": (1.5, 1.9375),          # the control room's band
    "gwin": (0.9375, 1.6875),       # the ground-floor offices' windows
}
# Doors: kind -> (width, height) of the opening in the brick.
OPENINGS = {
    "entrance": (1.625, ENTRY_H),   # a pair of glazed leaves and a transom light
    "service_door": (1.125, 2.1875),
}
REVEAL = {"rib": 0.15, "ctrl": 0.15, "gwin": 0.15, "entrance": 0.20,
          "service_door": 0.15}

# ------------------------------------------------------------------- bands
BRICK_Y0, BRICK_H = 0, 468        # z 0 .. Z_PAR
COP_Y0, COP_FACE, COP_TOP = 480, 8, 24   # the coping's face, then its top
UPST_Y0, UPST_H = 528, 20         # the parapet's inner face, Z_DECK .. Z_PAR
CANE_Y0, CANE_H = 560, 16         # the canopy's fascia, 0.25 m
# The handrails and the ladder take the coping's galvanised colour: the
# middle rows of its top, where no joint lies along them.
PIPE_STRIP = (COP_Y0 + COP_FACE + 6, COP_Y0 + COP_FACE + COP_TOP - 6)

COURSE = 0.078125       # brick course pitch: 5 px
BRICK_L = 0.25          # stretcher: 16 px, 64 bricks per atlas width
TONE_COURSES = 24       # brick tone repeats every 1.875 m
COP_JOINT = 128         # coping sheet joints every 2 m, in px

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels, at 64 px/m unless noted.
UNI_Y = 592
ENTRANCE = (4, UNI_Y, 128, 196)       # surround 2.0 x 3.0625 m round the door
SERVICE_DOOR = (136, UNI_Y, 72, 140)  # 1.125 x 2.1875 m
CTRL = (212, UNI_Y, 96, 124)          # one control-room light, 1.5 x 1.9375 m
RIB_F = (312, UNI_Y, 96, 92)          # a fixed light of the ribbon
RIB_V = (412, UNI_Y, 96, 92)          # one with a vent sash
GWIN = (512, UNI_Y, 60, 108)          # one light of the offices' windows
CONC = (640, UNI_Y, 168, 128)         # 2.625 x 2.0 m of cast concrete
VENT = (812, UNI_Y, 32, 96)           # a pipe's side: across x 1.5 m up
PIPE_TOP = (848, UNI_Y, 24, 24)       # a pipe's open end, planar
HOUSING = (876, UNI_Y, 96, 60)        # the ventilation housing's side
DECK = (140, 744, 432, 272)           # the roof deck at DPPM: 13.5 x 8.5 m

REGION = {"entrance": ENTRANCE, "service_door": SERVICE_DOOR, "ctrl": CTRL,
          "rib_f": RIB_F, "rib_v": RIB_V, "gwin": GWIN}
# each band's lights, fixed first; a band with one region uses it throughout
LIGHTS = {"rib": ("rib_f", "rib_v"), "ctrl": ("ctrl",), "gwin": ("gwin",)}
# where each region's opening sits inside it, (dx, dy) in px: the entrance
# region carries its surround round the opening
REGION_OFF = {"entrance": (int(SURROUND * PPM), 0)}

# the ventilation housing, a sheet box on the deck: side and height
HOUSING_W, HOUSING_H = 1.5, 0.9375

PATCH_NAMES = ("blank", "soffit", "sill", "render", "pipe", "post", "housing_top",
               "drip", "galv")
PATCHES = {n: (580 + 20 * i, 744, 16, 16) for i, n in enumerate(PATCH_NAMES)}

# internal rainwater outlets on the deck, plan (x, y)
OUTLETS = [(-3.0, -1.5), (3.0, -1.5)]

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_FRAME, ID_GLASS, ID_DECK, ID_COPING, ID_LAP = 5, 6, 7, 8, 9
ID_CONC, ID_DOOR, ID_RENDER, ID_STEEL, ID_PIPE = 10, 11, 12, 13, 14
ID_SOFFIT, ID_FASCIA, ID_HANDLE, ID_DARK, ID_SLAB = 15, 16, 17, 18, 19
ID_SILL, ID_ENTRY, ID_LOUVRE, ID_POST = 20, 21, 22, 23

# (roughness, metallic). The deck is mineral-surfaced felt; the coping,
# the housing and the kit galvanised; the canopy's fascia painted sheet.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.92, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.82, 0.0), ID_MORTAR: (0.94, 0.0), ID_FRAME: (0.46, 0.0),
    ID_GLASS: (glazing.ROUGHNESS, 0.0), ID_DECK: (0.92, 0.0),
    ID_COPING: (0.40, 0.65), ID_LAP: (0.88, 0.0), ID_CONC: (0.90, 0.0),
    ID_DOOR: (0.50, 0.0), ID_RENDER: (0.88, 0.0), ID_STEEL: (0.38, 0.75),
    ID_PIPE: (0.55, 0.20), ID_SOFFIT: (0.74, 0.0), ID_FASCIA: (0.52, 0.0),
    ID_HANDLE: (0.30, 0.85), ID_DARK: (0.96, 0.0), ID_SLAB: (0.90, 0.0),
    ID_SILL: (0.62, 0.30), ID_ENTRY: (0.44, 0.0), ID_LOUVRE: (0.46, 0.55),
    ID_POST: (0.55, 0.10),
}


# ---------------------------------------------------------------- palettes
def plant_brick(rgb, k=0.94):
    """The red brick shared by the plant's five pieces: each sRGB channel
    pulled 40% toward the triplet's Rec.709 luma, then darkened by *k*."""
    y = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    return tuple(int(round((y + 0.6 * (c - y)) * k)) for c in rgb)


# One coherent treatment per instance, matching the plant's other brick
# buildings: the brick changes, the frames stay white, the doors move a
# little with the brick. The deck, coping, kit, fascia, plinth, slab band,
# surround and canopy are fixed. red_brick is plant_brick() of the original
# red (146, 74, 54) / (116, 60, 47), its mortar (150, 145, 136) a further
# 10% darker.
VARIANTS = {
    "red_brick": {"brick": plant_brick((146, 74, 54)),
                  "brick2": plant_brick((116, 60, 47)),
                  "mortar": plant_brick((150, 145, 136), 0.94 * 0.90),
                  "frame": (222, 220, 212),
                  "entry": (98, 70, 50), "door": (86, 94, 90)},
    "yellow_brick": {"brick": (190, 168, 124), "brick2": (166, 144, 104),
                     "mortar": (162, 158, 150), "frame": (226, 224, 216),
                     "entry": (90, 66, 48), "door": (78, 88, 86)},
    "brown_brick": {"brick": (112, 76, 60), "brick2": (90, 62, 50),
                    "mortar": (128, 122, 114), "frame": (214, 210, 198),
                    "entry": (104, 76, 52), "door": (80, 74, 68)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (142, 140, 134), ID_CONC: (176, 174, 168),
    ID_RENDER: (188, 185, 176), ID_STEEL: (150, 152, 150), ID_PIPE: (62, 62, 64),
    ID_SOFFIT: (200, 198, 192), ID_HANDLE: (168, 168, 166), ID_DARK: (24, 24, 24),
    ID_BLANK: (52, 52, 52), ID_SILL: (128, 130, 130), ID_SLAB: (170, 168, 162),
    ID_DECK: (92, 91, 88), ID_LAP: (78, 77, 75), ID_COPING: (150, 152, 150),
    ID_FASCIA: (196, 196, 190), ID_LOUVRE: (140, 142, 141), ID_POST: (70, 72, 72),
}

BAND_IDS = {
    "BRICK": ((0, 470), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH, ID_SLAB}),
    "COPING": ((478, 514), {ID_COPING}),
    "UPSTAND": ((526, 550), {ID_DECK, ID_LAP, ID_COPING}),
    "CANOPY": ((558, 578), {ID_FASCIA}),
}

# The candidate-glazing mask is the emission map, neutral white.
EMIT = {ID_GLASS: (255, 255, 255)}
# Linear RGB. Offices and a control room lit by fluorescent tubes, the same
# reference factor as the catalog's other offices.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
BRICK_FACE = 0.006      # brick face proud of the recessed mortar
FRAME_H = 0.030         # steel window frames and mullions, proud of the glass
SASH_H = 0.045          # a vent sash, proud of the frame
DOOR_FRAME_H = 0.020    # steel door frames
RENDER_H = 0.015        # the cast surround, proud of the brick
LAP_H = 0.004           # a felt lap's step
SEAM_H = 0.006          # the coping's joint straps
LOUVRE_H = 0.020        # a louvre blade's lip


def m(v):
    """Metres -> pixels."""
    return v * PPM


# ================================================================== bands
def paint_plinth(c, y0):
    """Cast concrete plinth: board-float texture, darker at its foot, a drip
    line where the brick starts."""
    h = m(Z_PLINTH)
    c.paint(0, ATLAS, y0 - PAD, y0 + h, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h)
    z = (Y - y0) / PPM
    c.shade[sy, sx] *= 0.84 + 0.16 * np.clip(z / 0.25, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.25, 0, 1))
    # formwork board joints, 0.15 m apart
    for k in range(1, 4):
        yy = y0 + k * m(0.15)
        c.mul(0, ATLAS, yy, yy + 0.8, 0.94, ao=0.92)
    c.bevel(0, ATLAS, y0 + h - 3, y0 + h, 0.010, 1.5, axes="y")
    c.mul(0, ATLAS, y0 + h - 1, y0 + h, 0.86, ao=0.84)


def paint_brick(c):
    """Stretcher-bond facing brick, 0.25 x 0.078125 m, in two tones; the
    mortar recessed and its own id. Tone and bond repeat at the atlas wrap in
    U, so the bond runs on round every corner. The top course runs on up
    into the coping, which hides it."""
    y0 = BRICK_Y0 + m(Z_PLINTH)
    top = BRICK_Y0 + BRICK_H + PAD
    c.paint(0, ATLAS, y0, top, ID_BRICK, 1.0, 1.0)
    course, blen = m(COURSE), m(BRICK_L)
    sy, sx, Y, X = c.field(0, ATLAS, y0, top)
    r = np.floor((Y - y0) / course).astype(np.int64)
    off = (r % 2) * blen * 0.5
    b = np.floor((X - off) / blen).astype(np.int64) % int(ATLAS / blen)
    rr = r % TONE_COURSES
    bed = (Y - y0 - r * course) < 1.0
    perp = ((X - off) % blen) < 1.0
    joint = bed | perp
    tone = 0.90 + 0.20 * atlas.hash_unit(b, rr, 17)
    dark = atlas.hash_unit(b, rr, 29) < 0.17
    c.mid[sy, sx] = np.where(joint, ID_MORTAR, np.where(dark, ID_BRICK2, ID_BRICK))
    c.shade[sy, sx] = np.where(joint, 0.94, tone)
    c.ao[sy, sx] = np.where(joint, 0.80, 1.0)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)
    paint_plinth(c, BRICK_Y0)
    paint_slab(c)
    # the coping's shadow line on the brick under its drip
    yd = BRICK_Y0 + m(Z_COP0)
    c.mul(0, ATLAS, yd - 3, yd, 0.86, ao=0.80)
    c.mul(0, ATLAS, yd - 6, yd - 3, 0.95, ao=0.92)


def paint_slab(c):
    """The first floor slab's cast edge, flush with the brick face: a light
    concrete band right round the building, its arrises lit, a shadow line
    in the mortar bed under it, and the form-tie holes every metre."""
    y0, y1 = BRICK_Y0 + m(Z_BAND0), BRICK_Y0 + m(Z_BAND1)
    c.paint(0, ATLAS, y0, y1, ID_SLAB, 1.0, 1.0)
    c.bevel(0, ATLAS, y0, y1, BRICK_FACE + 0.004, 1.2, base=BRICK_FACE, axes="y")
    sy, sx, Y, X = c.field(0, ATLAS, y0, y1)
    c.shade[sy, sx] *= 0.97 + 0.03 * np.cos(2.0 * np.pi * X / 96.0) ** 2
    c.mul(0, ATLAS, y0 - 1, y0, 0.84, ao=0.82)        # bed joint under it
    for i in range(int(ATLAS / 64)):
        x = i * 64.0 + 16.0
        c.disc(x, (y0 + y1) / 2.0, 0.9, ID_SLAB, 0.80, 0.85, height=BRICK_FACE - 0.004)


def paint_coping(c):
    """The parapet's galvanised coping: its outer face with a folded drip at
    the foot, then its top falling slightly inward. Sheets two metres long,
    joined by a lapped strap across face and top."""
    y0 = COP_Y0
    y1 = y0 + COP_FACE + COP_TOP
    c.paint(0, ATLAS, y0 - PAD, y1 + PAD, ID_COPING, 1.0, 1.0, height=0.0)
    # the face: the drip fold at its foot, the arris at its top
    c.paint(0, ATLAS, y0 - PAD, y0 + 1, ID_COPING, 0.84, 0.86)
    c.bevel(0, ATLAS, y0 + 1, y0 + COP_FACE, 0.006, 1.0, axes="y")
    # the top: lighter, as a horizontal sheet weathers, a crease at the arris
    c.paint(0, ATLAS, y0 + COP_FACE, y1 + PAD, ID_COPING, 1.06, 1.0, height=0.0)
    c.mul(0, ATLAS, y0 + COP_FACE, y0 + COP_FACE + 1, 0.92)
    # joint straps every two metres, across face and top
    sy, sx, _, X = c.field(0, ATLAS, y0 - PAD, y1 + PAD)
    d = np.abs(((X % COP_JOINT) + COP_JOINT / 2.0) % COP_JOINT - COP_JOINT / 2.0)
    strap = d < 2.0
    c.height[sy, sx] = np.where(strap, c.height[sy, sx] + SEAM_H, c.height[sy, sx])
    c.shade[sy, sx] = np.where(strap, c.shade[sy, sx] * 0.95, c.shade[sy, sx])
    edge = (d >= 2.0) & (d < 3.0)
    c.ao[sy, sx] = np.where(edge, np.minimum(c.ao[sy, sx], 0.86), c.ao[sy, sx])


def paint_upstand(c):
    """The parapet's inner face from the deck up: the deck's felt turned up
    over a cant at the foot, dressed to a metal termination bar under the
    coping."""
    y0, h = UPST_Y0, UPST_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_DECK, 0.96, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    z = np.clip((Y - y0) / PPM, 0.0, None)
    c.shade[sy, sx] *= 0.82 + 0.18 * np.clip(z / 0.10, 0.0, 1.0)     # the cant
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.72 + 0.28 * np.clip(z / 0.12, 0, 1))
    yb = y0 + m(Z_COP0 - Z_DECK) - 4                    # the termination bar
    c.paint(0, ATLAS, yb, yb + 2, ID_COPING, 0.9, 0.9, height=0.006)
    c.mul(0, ATLAS, yb - 1, yb, 0.85, ao=0.85)
    c.paint(0, ATLAS, yb + 2, y0 + h + PAD, ID_COPING, 0.7, 0.7, height=0.0)
    # vertical laps of the upstand strips, a metre apart
    sy, sx, _, X = c.field(0, ATLAS, y0, yb)
    lap = (X % 64.0) < 1.0
    c.mid[sy, sx] = np.where(lap, ID_LAP, c.mid[sy, sx])
    c.height[sy, sx] = np.where((X % 64.0) < 4.0, LAP_H, c.height[sy, sx])


def paint_canopy_edge(c):
    """The canopy slab's fascia: a painted sheet edge, a lighter fold at its
    top, a drip at its foot."""
    y0, h = CANE_Y0, CANE_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_FASCIA, 1.0, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0 + 1, y0 + h - 1, 0.006, 1.0, axes="y")
    c.paint(0, ATLAS, y0 - PAD, y0 + 1, ID_FASCIA, 0.80, 0.84)
    c.paint(0, ATLAS, y0 + h - 1, y0 + h + PAD, ID_FASCIA, 1.04, 1.0)
    sy, sx, _, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    joint = (X % 128.0) < 1.0
    c.shade[sy, sx] = np.where(joint, c.shade[sy, sx] * 0.86, c.shade[sy, sx])


# ================================================================= regions
def _bar(c, a0, a1, b0, b1, mid=ID_FRAME, h=FRAME_H, ao=0.86, shade=1.0, axes="xy"):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, 1.0, axes=axes)


def _handle(c, x, y0, y1):
    """A stainless pull bar standing off the leaf."""
    c.paint(x - 1.2, x + 1.2, y0, y1, ID_HANDLE, 1.0, 0.9)
    sy, sx, _, X = c.field(x - 1.2, x + 1.2, y0, y1)
    u = (X - x) / 1.2
    c.height[sy, sx] = 0.05 * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))


def _light(c, a0, a1, b0, b1):
    """A pane in its frame, the frame's head rail shading its top."""
    c.paint(a0, a1, b0, b1, ID_GLASS, 1.0, 0.92, height=0.0)
    c.mul(a0, a1, b1 - 4, b1, 0.90, ao=0.84)


def _sash(c, a0, a1, b0, b1, inset=3):
    """A vent sash, proud of the frame, glazed inside its rails."""
    c.paint(a0, a1, b0, b1, ID_FRAME, 0.88)
    c.bevel(a0, a1, b0, b1, SASH_H, 1.0, base=FRAME_H)
    _light(c, a0 + inset, a1 - inset, b0 + inset + 1, b1 - inset)


MULL = 3                # half a mullion at each side of a light, px
HEAD, FOOT = 4, 6       # the band's head and bottom rails, px


def paint_band_light(c, rect, vent=None, vent_w=0.0):
    """One light of a window band: white steel, half a mullion either side so
    two neighbours make a whole one, a head rail and a heavier bottom rail,
    the glass between. *vent* "side" adds a side-hung vent sash *vent_w*
    metres wide at the light's left; "top" a top-hung one *vent_w* tall
    across its head, so a band of them reads as one line of vents."""
    x, y, w, h = rect
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 1.0, height=FRAME_H)
    c.bevel(x - 2, x + w + 2, y, y + h, FRAME_H, 1.0, axes="y")
    for a in (x, x + w):                                 # mullion arrises
        c.mul(a - 0.5, a + 0.5, y + FOOT, y + h - HEAD, 0.92, ao=0.9)
    a0, a1, b0, b1 = x + MULL, x + w - MULL, y + FOOT, y + h - HEAD
    if vent == "side":
        s1 = a0 + m(vent_w)
        _sash(c, a0, s1, b0, b1)
        _bar(c, s1, s1 + 3, b0, b1, axes="x")
        _light(c, s1 + 3, a1, b0, b1)
    elif vent == "top":
        yt = b1 - m(vent_w)
        _light(c, a0, a1, b0, yt)
        _bar(c, a0 - MULL, a1 + MULL, yt, yt + 3, axes="y")
        _sash(c, a0, a1, yt + 3, b1)
    else:
        _light(c, a0, a1, b0, b1)
    c.mul(x, x + w, y, y + 2, 0.90, ao=0.86)


def paint_windows(c):
    paint_band_light(c, RIB_F)
    paint_band_light(c, RIB_V, "side", 0.4375)
    paint_band_light(c, CTRL, "top", 0.375)
    paint_band_light(c, GWIN, "top", 0.375)


def paint_entrance(c):
    """The plant's main entrance: a cast concrete surround round three sides
    of the opening, and in it a pair of glazed teak leaves in a white frame
    with a transom light over them. Each leaf is glazed from a deep bottom
    rail to its top rail, with a long pull bar at the meeting stiles."""
    x, y, w, h = ENTRANCE
    s = m(SURROUND)
    # the surround: concrete, proud of the brick, its arrises bevelled
    c.paint(x, x + w, y, y + h, ID_RENDER, 1.0, 1.0)
    c.bevel(x, x + w, y - 4, y + h, RENDER_H, 1.5, axes="xy")
    ox0, ox1, oy1 = x + s, x + w - s, y + m(ENTRY_H)
    c.mul(ox0 - 2, ox0, y, oy1 + 2, 0.90, ao=0.86)      # shadow into the reveal
    c.mul(ox1, ox1 + 2, y, oy1 + 2, 0.94, ao=0.90)
    c.mul(ox0 - 2, ox1 + 2, oy1, oy1 + 2, 0.92, ao=0.88)
    # the opening: frame, transom light, two leaves
    c.paint(ox0, ox1, y, oy1, ID_GLASS, 1.0, 1.0, height=0.0)
    F = 4
    yl = y + m(Z_LEAF)
    _bar(c, ox0, ox1, y, y + 2, axes="y")                   # threshold
    _bar(c, ox0, ox1, oy1 - F, oy1, axes="y")               # head
    _bar(c, ox0, ox0 + F, y, oy1, axes="x")
    _bar(c, ox1 - F, ox1, y, oy1, axes="x")
    _bar(c, ox0, ox1, yl, yl + 5, axes="y")                 # transom bar
    xm = (ox0 + ox1) / 2.0
    _bar(c, xm - 1.5, xm + 1.5, yl + 5, oy1 - F, axes="x")  # transom mullion
    c.mul(ox0 + F, ox1 - F, oy1 - F - 3, oy1 - F, 0.90, ao=0.84)
    st, gb, gt = 6, y + m(0.40), yl - 7
    for l0, l1 in ((ox0 + F, xm), (xm, ox1 - F)):
        _bar(c, l0, l1, y + 2, yl, ID_ENTRY, 0.04, 0.9, 1.0)
        c.paint(l0 + st, l1 - st, gb, gt, ID_GLASS, 1.0, 1.0, height=0.0)
        c.mul(l0 + st, l1 - st, gt - 4, gt, 0.90, ao=0.84)     # under the top rail
        for a0, a1, b0, b1, ax in ((l0 + st - 1, l0 + st, gb, gt, "x"),
                                   (l1 - st, l1 - st + 1, gb, gt, "x"),
                                   (l0 + st, l1 - st, gb - 1, gb, "y")):
            _bar(c, a0, a1, b0, b1, ID_ENTRY, 0.05, 0.86, 0.9, ax)
        c.paint(l0 + 2, l1 - 2, y + 2, y + 12, ID_STEEL, 0.9, 0.9, height=0.043)
    c.mul(xm - 0.5, xm + 0.5, y + 2, yl, 0.70, ao=0.70)       # meeting stiles
    _handle(c, xm - 4, y + m(0.80), y + m(1.40))
    _handle(c, xm + 4, y + m(0.80), y + m(1.40))


def paint_service_door(c):
    """A plain steel leaf in a steel frame: the staff's back door toward the
    boiler house."""
    x, y, w, h = SERVICE_DOOR
    c.paint(x, x + w, y, y + h, ID_DOOR, 0.86, 0.9, height=0.0)
    F = 4
    _bar(c, x, x + F, y, y + h, ID_DOOR, DOOR_FRAME_H, 0.84, 0.86, "x")
    _bar(c, x + w - F, x + w, y, y + h, ID_DOOR, DOOR_FRAME_H, 0.84, 0.86, "x")
    _bar(c, x, x + w, y + h - F, y + h, ID_DOOR, DOOR_FRAME_H, 0.84, 0.86, "y")
    l0, l1, t = x + F, x + w - F, y + h - F
    c.paint(l0, l1, y, t, ID_DOOR, 1.0, 0.96, height=0.0)
    c.mul(l0, l1, t - 3, t, 0.88, ao=0.84)
    # a small wired vision panel, then a kick plate
    c.paint(l0 + 18, l1 - 18, y + m(1.35), y + m(1.85), ID_GLASS, 1.0, 1.0, height=0.0)
    for a0, a1, b0, b1, ax in ((l0 + 17, l0 + 18, y + m(1.35), y + m(1.85), "x"),
                               (l1 - 18, l1 - 17, y + m(1.35), y + m(1.85), "x"),
                               (l0 + 17, l1 - 17, y + m(1.35) - 1, y + m(1.35), "y"),
                               (l0 + 17, l1 - 17, y + m(1.85), y + m(1.85) + 1, "y")):
        _bar(c, a0, a1, b0, b1, ID_DOOR, 0.012, 0.86, 0.9, ax)
    c.paint(l0 + 2, l1 - 2, y + 2, y + m(0.25), ID_STEEL, 0.9, 0.9, height=0.003)
    hx, hy = l1 - 8, y + m(1.0)
    c.paint(hx - 1.5, hx + 1.5, hy - 5, hy + 5, ID_HANDLE, 1.0, 0.9, height=0.01)
    c.stroke((hx, hy + 2), (hx - 8, hy + 2), 2.2, ID_HANDLE, 1.0, 0.9, height=0.04)


def paint_conc(c):
    """Cast concrete for the steps and the canopy's top: board-float
    texture, pores."""
    x, y, w, h = CONC
    c.paint(x, x + w, y, y + h, ID_CONC, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x, x + w, y, y + h)
    c.shade[sy, sx] *= 0.97 + 0.03 * np.cos(2.0 * np.pi * (X - x) / 24.0) ** 2


def paint_vent(c):
    """A black steel vent pipe's side, wrapped once round, with a collar
    near the top and a welded seam; its open end, the bore dark."""
    x, y, w, h = VENT
    c.paint(x, x + w, y, y + h, ID_PIPE, 1.0, 1.0, height=0.0)
    sy, sx, _, X = c.field(x, x + w, y, y + h)
    u = 2.0 * (X - x) / w - 1.0
    c.shade[sy, sx] *= 0.96 + 0.04 * np.cos(np.pi * u)
    c.mul(x + w / 2 - 0.5, x + w / 2 + 0.5, y, y + h, 0.88, ao=0.9)
    for yy in (y + m(0.45), y + m(0.9)):
        c.paint(x, x + w, yy - 2, yy + 2, ID_PIPE, 0.90, 0.9, height=0.006)
    x, y, w, h = PIPE_TOP
    c.paint(x, x + w, y, y + h, ID_PIPE, 1.0, 1.0, height=0.0)
    cx, cy = x + w / 2.0, y + h / 2.0
    c.disc(cx, cy, w / 2.0 - 1.5, ID_DARK, 1.0, 0.5, height=-0.02)
    c.disc(cx, cy, w / 2.0 - 4.0, ID_DARK, 0.6, 0.3, height=-0.04)


def paint_housing(c):
    """The ventilation housing's side: galvanised sheet with folded corners,
    and a louvred intake panel, its blades 6 cm apart, dark between."""
    x, y, w, h = HOUSING
    c.paint(x, x + w, y, y + h, ID_COPING, 0.96, 1.0, height=0.0)
    c.bevel(x, x + w, y, y + h, 0.004, 2.0, axes="x")       # folded corners
    c.paint(x, x + w, y, y + 3, ID_COPING, 0.80, 0.80)      # the foot, flashed
    c.paint(x, x + w, y + h - 3, y + h, ID_COPING, 1.04, 1.0, height=0.006)
    p0, p1, q0, q1 = x + 10, x + w - 10, y + 10, y + h - 12
    _bar(c, p0 - 2, p1 + 2, q0 - 2, q1 + 2, ID_COPING, 0.012, 0.88, 0.9)
    c.paint(p0, p1, q0, q1, ID_DARK, 0.5, 0.5, height=-0.01)
    sy, sx, Y, X = c.field(p0, p1, q0, q1)
    t = ((Y - q0) % 4.0) / 4.0                              # blade profile
    blade = t > 0.35
    c.mid[sy, sx] = np.where(blade, ID_LOUVRE, ID_DARK)
    c.shade[sy, sx] = np.where(blade, 0.80 + 0.25 * t, 0.5)
    c.height[sy, sx] = np.where(blade, LOUVRE_H * t, -0.01)
    c.ao[sy, sx] = np.where(blade, 0.85, 0.45)


def paint_deck(c):
    """The roof deck at DPPM: mineral-surfaced bitumen felt in one-metre
    strips laid across the fall, each lapped over the next, their end laps
    staggered; the felt dressed up a cant at the parapet all round; two
    internal rainwater outlets with ponding stains round them."""
    x, y, w, h = DECK
    p = DPPM
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_DECK, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    # strips across the fall: a lap every metre, a short step up over it
    v = (Y - y) / p
    f = v - np.floor(v)
    lap = f < 1.0 / p
    c.height[sy, sx] = np.where(f < 0.10, LAP_H * (1.0 - f / 0.10), 0.0)
    c.mid[sy, sx] = np.where(lap, ID_LAP, ID_DECK)
    row = np.floor(v).astype(np.int64)
    u = (X - x) / p + 2.5 * (row % 2)
    endlap = ((u % 5.0) < 1.0 / p) & ~lap
    c.mid[sy, sx] = np.where(endlap, ID_LAP, c.mid[sy, sx])
    # the cant and the upstand's foot at the parapet, all round
    d = np.minimum(np.minimum(X - x, x + w - X), np.minimum(Y - y, y + h - Y)) / p
    edge = np.clip(d / 0.18, 0.0, 1.0)
    c.shade[sy, sx] *= 0.84 + 0.16 * edge
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.70 + 0.30 * edge)
    c.height[sy, sx] += 0.02 * (1.0 - edge)
    # the outlets: a dark bowl and a grating
    for ox, oy in OUTLETS:
        cx, cy = x + (ox + HX - PIN) * p, y + (oy + HY - PIN) * p
        c.disc(cx, cy, 0.22 * p, ID_LAP, 0.8, 0.8, height=-0.006)
        c.disc(cx, cy, 0.12 * p, ID_DARK, 1.0, 0.5, height=-0.02)
        c.disc(cx, cy, 0.12 * p, ID_COPING, 0.7, 0.7, inner=0.09 * p, height=-0.01)


def paint_patches(c):
    """Flat cells for surfaces a whole face takes one colour from."""
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0),
        "soffit": (ID_SOFFIT, 0.92, 0.80),
        "sill": (ID_SILL, 0.96, 0.92),
        "render": (ID_RENDER, 0.94, 0.88),
        "pipe": (ID_PIPE, 1.0, 0.95),
        "post": (ID_POST, 1.0, 0.95),
        "housing_top": (ID_COPING, 1.02, 1.0),
        "drip": (ID_COPING, 0.62, 0.70),
        "galv": (ID_COPING, 1.0, 1.0),
    }
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x - 2, x + w + 2, y - 2, y + h + 2, mid, sh, ao, height=0.0)


# ------------------------------------------------------------------ checks
def light_kind(band, k, n):
    """The region light *k* of an *n*-light band of kind *band* samples. A
    band with one region (its vents a row across every light's head) uses
    it throughout; the ribbon has a side vent in every other light, and its
    two-light end windows are two fixed lights: a vent between them made a
    house's casement and fixed light of them."""
    names = LIGHTS[band]
    if len(names) == 1 or n == 2:
        return names[0]
    return names[k % 2]


def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands, or
    run off the sheet, or if a region does not fit its light or opening."""
    rects = {"entrance": ENTRANCE, "service_door": SERVICE_DOOR, "ctrl": CTRL,
             "rib_f": RIB_F, "rib_v": RIB_V, "gwin": GWIN,
             "conc": CONC, "vent": VENT, "pipe_top": PIPE_TOP, "housing": HOUSING,
             "deck": DECK}
    rects.update(PATCHES)
    bands_top = CANE_Y0 + CANE_H + PAD
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
    for band, (lw, lh) in BANDS.items():
        for name in LIGHTS[band]:
            _x, _y, w, h = REGION[name]
            if abs(w / PPM - lw) > 1e-6 or abs(h / PPM - lh) > 1e-6:
                problems.append("%s region is not one %s light" % (name, band))
    for kind, (w, h) in OPENINGS.items():
        x, y, rw, rh = REGION[kind]
        dx, _dy = REGION_OFF.get(kind, (0, 0))
        top = SURROUND_TOP if kind == "entrance" else 0.0
        if abs((rw - 2 * dx) / PPM - w) > 0.02 or abs(rh / PPM - top - h) > 0.02:
            problems.append("%s region does not fit its opening" % kind)
    dx, dy, dw, dh = DECK
    if abs(dw / DPPM - 2 * (HX - PIN)) > 1e-6 or abs(dh / DPPM - 2 * (HY - PIN)) > 1e-6:
        problems.append("the deck region is not the deck inside the parapet")
    if abs(HOUSING[2] / PPM - HOUSING_W) > 1e-6 or abs(HOUSING[3] / PPM - HOUSING_H) > 1e-6:
        problems.append("the housing region does not fit the housing")
    if abs(m(Z_PAR) - BRICK_H) > 1e-6:
        problems.append("the brick band does not reach the parapet's top")
    if abs(m(Z_PAR - Z_DECK) - UPST_H) > 1e-6:
        problems.append("the upstand band is not the parapet's inner face")
    if abs(m(COPING_H) - COP_FACE) > 1e-6 or abs(m(PIN + 2 * COPING_OUT) - COP_TOP) > 1e-6:
        problems.append("the coping band does not fit the coping")
    for z in (Z_PLINTH, Z_FLOOR, Z_FLOOR2, Z_BAND0, Z_DECK, Z_COP, Z_COP0, Z_PAR,
              Z_SILL, Z_SILL2, Z_SILL_CTRL, Z_LEAF, ENTRY_H):
        if abs(m(z) - round(m(z))) > 1e-6:
            problems.append("height %.4f is not a whole texel" % z)
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    The brick band's V is height from the ground on every wall, so the
    plinth's soil, the splash-back and the salt bloom land the same all
    round, and so do the runs from the slab band's top arris.
    """
    brick = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    steel = (ID_COPING, ID_STEEL, ID_PIPE, ID_DOOR, ID_HANDLE, ID_LOUVRE, ID_POST)
    w = weathering.Weather(c, clean=(ID_GLASS,), steel=steel)
    w.grime()
    w.fade((ID_FRAME, ID_DOOR, ID_ENTRY, ID_FASCIA, ID_DECK, ID_LAP, ID_POST))
    w.wash(brick)
    w.plinth(0, ATLAS, BRICK_Y0, BRICK_Y0 + m(Z_PLINTH), (ID_PLINTH,))
    w.splash(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + BRICK_H + PAD, brick)
    w.bloom(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(1.4), brick,
            amount=0.10, fade=m(0.6))
    # the slab band: dirt on its top arris, faint runs onto the brick below
    yb0, yb1 = BRICK_Y0 + m(Z_BAND0), BRICK_Y0 + m(Z_BAND1)
    w.add("D", 0, ATLAS, yb0, yb1, lambda Y, X, nz: 0.05 + 0.08 * nz("blotch")
          + 0.10 * atlas.smoothstep(yb1 - 4, yb1, Y), (ID_SLAB,))
    w.runs(0, ATLAS, yb0 - 24, yb0, brick, 0.06, fall=10.0)
    # the parapet: sheltered under the coping's drip, faint runs from it
    yd = BRICK_Y0 + m(Z_COP0)
    w.shelter(0, ATLAS, yd - 24, yd, brick, amount=0.06, top=BRICK_Y0 + BRICK_H + PAD)
    w.runs(0, ATLAS, yd - 40, yd, brick, 0.05, fall=14.0)
    # the coping: dust on its top, runs down its face
    w.add("D", 0, ATLAS, COP_Y0 + COP_FACE, COP_Y0 + COP_FACE + COP_TOP + PAD,
          lambda Y, X, nz: 0.06 + 0.08 * nz("blotch"), (ID_COPING,))
    w.runs(0, ATLAS, COP_Y0 - PAD, COP_Y0 + COP_FACE, (ID_COPING,), 0.08, fall=5.0,
           noise="short")
    # the upstand: dirt at its foot where water stands
    w.add("D", 0, ATLAS, UPST_Y0 - PAD, UPST_Y0 + UPST_H, lambda Y, X, nz: 0.14
          * np.exp(-np.clip(Y - UPST_Y0, 0, None) / 4.0) * (0.6 + 0.4 * nz("blotch")),
          (ID_DECK, ID_LAP))
    # the canopy's fascia: runs from its top
    w.runs(0, ATLAS, CANE_Y0, CANE_Y0 + CANE_H, (ID_FASCIA,), 0.10, fall=8.0,
           noise="short")
    # the deck: blotchy dirt, darker in the hollows round each outlet and
    # along the parapet's foot, where water stands longest
    x, y, rw, rh = DECK
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.06 + 0.10 * nz("big")
          + 0.06 * nz("blotch"), (ID_DECK, ID_LAP))
    for ox, oy in OUTLETS:
        cx, cy = x + (ox + HX - PIN) * DPPM, y + (oy + HY - PIN) * DPPM
        r = 1.4 * DPPM
        w.add("D", cx - r, cx + r, cy - r, cy + r, lambda Y, X, nz, cx=cx, cy=cy, r=r:
              0.20 * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (0.45 * r) ** 2)
              * (0.6 + 0.4 * nz("blotch")), (ID_DECK, ID_LAP))
    # the windows: dirt standing on the bottom rails
    for rect in (RIB_F, RIB_V, CTRL, GWIN):
        x, y, rw, rh = rect
        w.add("D", x, x + rw, y, y + FOOT + 1, lambda Y, X, nz: 0.10
              + 0.12 * atlas.smoothstep(0.2, 1.4, nz("short")), (ID_FRAME,))
    # the doors: their feet and handles; the surround's foot splashed
    x, y, rw, rh = ENTRANCE
    s = m(SURROUND)
    xm = x + rw / 2.0
    w.door(x + s + 4, x + rw - s - 4, y, y + m(Z_LEAF), (ID_ENTRY, ID_STEEL),
           handle=(xm, y + m(1.10)))
    w.splash(x, x + rw, y, y + rh, (ID_RENDER,), amount=0.16, fall=0.25)
    w.add("D", x, x + rw, y + rh - 20, y + rh, lambda Y, X, nz: 0.08
          * atlas.smoothstep(0.3, 1.5, nz("runs")), (ID_RENDER,))
    x, y, rw, rh = SERVICE_DOOR
    w.door(x + 4, x + rw - 4, y, y + rh - 4, (ID_DOOR,),
           handle=(x + rw - 12, y + m(1.0)))
    # the concrete: worn and dirty, more so at the foot of each face
    x, y, rw, rh = CONC
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.10 * nz("big")
          + 0.06 * nz("blotch") + 0.10 * nz("speck"), (ID_CONC,))
    w.splash(x, x + rw, y, y + rh, (ID_CONC,), amount=0.14, fall=0.12)
    # the vent pipes: soot and rust runs down from the open end
    x, y, rw, rh = VENT
    w.runs(x, x + rw, y, y + rh, (ID_PIPE,), 0.14, fall=rh / 2.0)
    w.add("R", x, x + rw, y, y + rh, lambda Y, X, nz: 0.10 * atlas.smoothstep(
        0.4, 1.6, nz("runs")), (ID_PIPE,))
    # the housing: dirt at its foot, runs under its lid
    x, y, rw, rh = HOUSING
    w.splash(x, x + rw, y, y + rh, (ID_COPING, ID_LOUVRE), amount=0.12, fall=0.15)
    w.runs(x, x + rw, y, y + rh - 3, (ID_COPING,), 0.08, fall=8.0, noise="short")
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_brick(c)
    paint_coping(c)
    paint_upstand(c)
    paint_canopy_edge(c)
    c.check_bands(BAND_IDS)
    paint_entrance(c)
    paint_service_door(c)
    paint_windows(c)
    paint_conc(c)
    paint_vent(c)
    paint_housing(c)
    paint_deck(c)
    paint_patches(c)

    # Tone wear, grain and pores. Every field is periodic, so the bands wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH, ID_SLAB))
    streak = atlas.noise(c, 7, 0.8, 40.0)
    c.shade[walls] *= 1.0 + 0.03 * streak[walls]
    sheet = np.isin(c.mid, (ID_FASCIA, ID_DOOR, ID_ENTRY, ID_COPING))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    c.shade[sheet] *= 1.0 + 0.016 * grain[sheet]
    deck = np.isin(c.mid, (ID_DECK, ID_LAP))
    mottle = atlas.noise(c, 6, 6.0, 6.0)
    gravel = atlas.noise(c, 11, 0.6)
    c.shade[deck] *= 1.0 + 0.05 * mottle[deck] + 0.07 * gravel[deck]
    c.height[deck] += 0.0008 * gravel[deck]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_CONC, ID_MORTAR, ID_RENDER, ID_SLAB))
    pores = atlas.noise(c, 9, 0.8)
    c.shade[mineral] *= 1.0 + 0.035 * pores[mineral]
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
    t[ID_FRAME] = pal["frame"]
    t[ID_DOOR] = pal["door"]
    t[ID_ENTRY] = pal["entry"]
    return t


def export(out_dir, ss=atlas.SS):
    """Candidate glazing in the emission map is neutral grey, each light the
    lit room behind it; nothing else on the building glows, and no occupancy
    or schedule is baked in."""
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.010)
    c.weather.dust(cav, (ID_BRICK, ID_BRICK2, ID_MORTAR))
    rough = 0.04 * atlas.noise(c, 13, 20.0)
    path = os.path.join(out_dir, ASSET)
    glass = atlas.coverage(c, ID_GLASS)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS,)), path + "_normal.png"),
               atlas.save(glazing.night_rooms(glass > 0, atlas.emission_colours(c, EMIT)),
                          path + "_emission.png")]
    for v in VARIANTS:
        rgb = glazing.rooms(glass >= 0.5, atlas.albedo(c, lut(v), grime=0.25 * cav))
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
