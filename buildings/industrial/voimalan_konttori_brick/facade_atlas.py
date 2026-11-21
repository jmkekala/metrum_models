# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
voimalan_konttori_brick.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
the plan, the floor, sill, door, band and eave heights, band rows, opening
sizes, region rectangles -- so a change here cannot leave the UVs pointing at
the wrong artwork.

The atlas is a trim sheet. Four bands run the full width and tile in U:

    y    0 ..  448   BRICK   z 0 .. 7.0 m: concrete plinth, brick, the cast
                             floor-slab band at the first floor, brick to the
                             wall head
    y  464 ..  560   ROOF    batten-seamed bitumen felt, eave edge to ridge,
                             V stretched up the slope
    y  568 ..  584   EAVE    the eave fascia with its gutter
    y  592 ..  608   CANOPY  the entrance canopy's concrete edge
    y  616 ..  ...   unique  the entrance with its cast surround, the service
                             door, the office window, the control-room
                             window, the concrete for the steps and the
                             canopy, the vent pipes, patches

The brick band is the whole wall's height, so every wall samples it by its
own height from the ground and the plinth, the slab band and the weather at
the foot line up all round. The battens on the felt run down the slope, so
the roof band only varies across U and is stretched up the slope in V, the
way tehdas_brick_gable stretches its profiled sheet.

The roof and canopy bands start on 16-row boundaries, the roof 16 rows clear
of the brick: at mip 4 (16 x 16 texels to a texel) a roof band sharing a
block with the brick's top rows came out with a red rim along every eave.

Every opening is a single window or door, so each type has a region of its
own at 64 px/m, painted once and sampled by every opening of that type.

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
Z_EAVE = 6.875          # 440 px; roof underside at the wall face, 3.125 m
                        # over the first floor
WALL_INTO_ROOF = 0.125  # walls run this far into the roof slab
Z_WALL_TOP = Z_EAVE + WALL_INTO_ROOF             # 7.0, 448 px

# windows: the offices' at desk height on both floors, the control room's a
# quarter metre lower and taller, every ground-floor head at one line
Z_SILL = Z_FLOOR + 1.0                           # 1.5
Z_SILL2 = Z_FLOOR2 + 1.0                         # 4.75
Z_SILL_CTRL = Z_FLOOR + 0.75                     # 1.25
# doors: every leaf 2.125 m; the entrance has a transom light above its pair
Z_LEAF = 2.125          # leaf height over the threshold
ENTRY_H = 2.6875        # the entrance's opening, threshold to head (3.1875)
SURROUND = 0.1875       # the entrance's cast surround, each side
SURROUND_TOP = 0.375    # and above the head, up into the canopy

# the canopy over the entrance: the first-floor slab carried out, its edge
# in line with the painted slab band
Z_CAN0 = Z_BAND0                                 # 3.5, underside
Z_CAN1 = Z_BAND1                                 # 3.75, top

# the hipped roof: one pitch on all four sides, one overhang all round
TAN = 0.3125            # 17.4 degrees
ROOF_T = 0.25           # slab's vertical thickness = the fascia's height
EAVE_OUT = 0.5          # eave overhang, horizontal, all four sides
SLOPE_F = float(np.sqrt(1.0 + TAN * TAN))
SLOPE_LEN = (HY + EAVE_OUT) * SLOPE_F           # eave edge to ridge, 5.238 m

# ------------------------------------------------------------------ openings
# kind -> (width, height) of the opening in the brick, metres.
OPENINGS = {
    "win": (1.5, 1.6875),           # the offices' windows, both floors
    "ctrl": (2.0, 1.9375),          # the control room's
    "entrance": (1.625, ENTRY_H),   # a pair of glazed leaves and a transom light
    "service_door": (1.125, 2.1875),
}
REVEAL = {"win": 0.15, "ctrl": 0.15, "entrance": 0.20, "service_door": 0.15}

# ------------------------------------------------------------------- bands
BRICK_Y0, BRICK_H = 0, 448        # z 0 .. Z_WALL_TOP
ROOF_Y0, ROOF_H = 464, 96         # the slope, eave edge to ridge
EAVE_Y0, EAVE_H = 568, 16         # the eave fascia, ROOF_T tall
GUTTER_PX = 9                     # the gutter's rows, across the fascia's top
# The downpipes' and handrails' sides span the middle five of them
PIPE_STRIP = (EAVE_Y0 + EAVE_H - GUTTER_PX + 2, EAVE_Y0 + EAVE_H - 2)
CANE_Y0, CANE_H = 592, 16         # the canopy's edge, 0.25 m
ROOF_RPM = ROOF_H / SLOPE_LEN     # roof rows per metre up the slope (18.3)

COURSE = 0.078125       # brick course pitch: 5 px
BRICK_L = 0.25          # stretcher: 16 px, 64 bricks per atlas width
TONE_COURSES = 24       # brick tone repeats every 1.875 m
BATTEN = 32             # felt battens every 0.5 m, in px

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels, all at 64 px/m.
UNI_Y = 616
ENTRANCE = (4, UNI_Y, 128, 196)       # surround 2.0 x 3.0625 m round the door
SERVICE_DOOR = (136, UNI_Y, 72, 140)  # 1.125 x 2.1875 m
WIN = (212, UNI_Y, 96, 108)           # 1.5 x 1.6875 m
CTRL = (312, UNI_Y, 128, 124)         # 2.0 x 1.9375 m
CONC = (444, UNI_Y, 160, 88)          # 2.5 x 1.375 m of cast concrete
VENT = (608, UNI_Y, 32, 96)           # a pipe's side: across x 1.5 m up
PIPE_TOP = (644, UNI_Y, 24, 24)       # a pipe's open end, planar

REGION = {"entrance": ENTRANCE, "service_door": SERVICE_DOOR, "win": WIN,
          "ctrl": CTRL}
# where each region's opening sits inside it, (dx, dy) in px: the entrance
# region carries its surround round the opening
REGION_OFF = {"entrance": (int(SURROUND * PPM), 0)}

PATCH_NAMES = ("blank", "soffit", "sill", "render", "pipe")
PATCHES = {n: (4 + 20 * i, 1004, 16, 16) for i, n in enumerate(PATCH_NAMES)}

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_FRAME, ID_GLASS, ID_ROOF, ID_FLASH, ID_BATTEN = 5, 6, 7, 8, 9
ID_CONC, ID_DOOR, ID_RENDER, ID_STEEL, ID_PIPE = 10, 11, 12, 13, 14
ID_SOFFIT, ID_GUTTER, ID_HANDLE, ID_DARK, ID_SLAB = 15, 16, 17, 18, 19
ID_SILL, ID_ENTRY = 20, 21

# (roughness, metallic). The felt and its battens are matt bitumen with a
# mineral surface; the fascia is painted sheet; the gutter bare galvanised.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.92, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.82, 0.0), ID_MORTAR: (0.94, 0.0), ID_FRAME: (0.48, 0.0),
    ID_GLASS: (glazing.ROUGHNESS, 0.0), ID_ROOF: (0.86, 0.0),
    ID_FLASH: (0.50, 0.20), ID_BATTEN: (0.80, 0.0), ID_CONC: (0.90, 0.0),
    ID_DOOR: (0.50, 0.0), ID_RENDER: (0.88, 0.0), ID_STEEL: (0.38, 0.75),
    ID_PIPE: (0.55, 0.20), ID_SOFFIT: (0.74, 0.0), ID_GUTTER: (0.36, 0.70),
    ID_HANDLE: (0.30, 0.85), ID_DARK: (0.96, 0.0), ID_SLAB: (0.90, 0.0),
    ID_SILL: (0.62, 0.30), ID_ENTRY: (0.44, 0.0),
}

# ---------------------------------------------------------------- palettes
# One coherent treatment per instance, matching the plant's other brick
# buildings: the brick changes, the frames stay white, the doors move a
# little with the brick. The felt roof stays near-black, the gutter, pipes
# and rails galvanised; the plinth, slab band, surround and canopy are
# fixed concrete.
VARIANTS = {
    "red_brick": {"brick": (146, 74, 54), "brick2": (116, 60, 47),
                  "mortar": (150, 145, 136), "frame": (222, 220, 212),
                  "roof": (46, 46, 47), "flash": (60, 62, 64),
                  "entry": (98, 70, 50), "door": (86, 94, 90)},
    "yellow_brick": {"brick": (190, 168, 124), "brick2": (166, 144, 104),
                     "mortar": (162, 158, 150), "frame": (226, 224, 216),
                     "roof": (46, 46, 47), "flash": (58, 60, 62),
                     "entry": (90, 66, 48), "door": (78, 88, 86)},
    "brown_brick": {"brick": (112, 76, 60), "brick2": (90, 62, 50),
                    "mortar": (128, 122, 114), "frame": (214, 210, 198),
                    "roof": (44, 43, 42), "flash": (56, 54, 52),
                    "entry": (104, 76, 52), "door": (80, 74, 68)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (142, 140, 134), ID_CONC: (176, 174, 168),
    ID_RENDER: (188, 185, 176), ID_STEEL: (150, 152, 150), ID_PIPE: (62, 62, 64),
    ID_SOFFIT: (200, 198, 192), ID_HANDLE: (168, 168, 166), ID_DARK: (24, 24, 24),
    ID_BLANK: (52, 52, 52), ID_SILL: (128, 130, 130), ID_SLAB: (170, 168, 162),
    ID_GUTTER: (150, 152, 150),
}

BAND_IDS = {
    "BRICK": ((0, 450), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH, ID_SLAB}),
    "ROOF": ((462, 562), {ID_ROOF, ID_BATTEN}),
    "EAVE": ((566, 586), {ID_FLASH, ID_GUTTER}),
    "CANOPY": ((590, 610), {ID_CONC}),
}

# The candidate-glazing mask is the emission map, neutral white.
EMIT = {ID_GLASS: (255, 255, 255)}
# Linear RGB. Offices and a control room lit by fluorescent tubes, the same
# reference factor as the catalog's other offices.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
BRICK_FACE = 0.006      # brick face proud of the recessed mortar
FRAME_H = 0.030         # window and door frames, proud of the glass
SASH_H = 0.045          # an opening sash, proud of the frame
DOOR_FRAME_H = 0.020    # steel door frames
BATTEN_H = 0.045        # felt-covered batten over the sheet
GUTTER_R = 0.070        # half-round gutter
RENDER_H = 0.015        # the cast surround, proud of the brick


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
    U, so the bond runs on round every corner."""
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


def paint_roof(c):
    """Bitumen felt on battens, the Nordic low-pitch roof of the period:
    felt strips laid down the slope between battens every 0.5 m, each batten
    capped by its own strip, so the roof reads as fine ribs from eave to
    ridge. A darker drip strip at the eave. No ridge or hip cap is painted:
    the band's top is a ridge on two slopes and a point on the hip ends."""
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_ROOF, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    d = np.abs(((X % BATTEN) + BATTEN / 2.0) % BATTEN - BATTEN / 2.0)   # to batten
    w = 2.4                                           # batten half-width, px
    prof = np.clip((w - d) / 1.2, 0.0, 1.0)
    height = BATTEN_H * np.sqrt(prof)
    batten = d < w
    mid = np.where(batten, ID_BATTEN, ID_ROOF)
    shade = np.where(batten, 1.04, 1.0)
    # the cap strip's lapped edge either side of the batten, and the felt
    # sagging a little into the bay between
    lap = (d >= w) & (d < w + 1.6)
    shade = np.where(lap, 0.88, shade)
    ao = np.where(lap, 0.84, 1.0)
    bay = np.clip((d - w) / (BATTEN / 2.0 - w), 0.0, 1.0)
    height = height - np.where(batten, 0.0, 0.004 * np.sin(np.pi * bay))
    v = Y - y0
    shade = np.where(v < 1.5, shade * 0.80, shade)    # eave drip strip
    c.mid[sy, sx], c.height[sy, sx] = mid, height
    c.shade[sy, sx], c.ao[sy, sx] = shade, ao


def paint_eave(c):
    """The eave's vertical edge: a sheet fascia with a half-round galvanised
    gutter hung across its top, hangers every metre."""
    y0 = EAVE_Y0
    top = y0 + EAVE_H
    c.paint(0, ATLAS, y0 - PAD, top + PAD, ID_FLASH, 1.0, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 - PAD, y0 + 1, ID_FLASH, 0.86, 0.9)       # drip edge
    gh = float(GUTTER_PX)
    g0 = top - gh
    c.paint(0, ATLAS, g0, top + PAD, ID_GUTTER, 1.0, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_GUTTER, 0.82, 0.86)
    for k, f in enumerate((0.80, 0.88, 0.95)):             # under the gutter
        c.mul(0, ATLAS, g0 - 1 - k, g0 - k, f, ao=0.84)
    sy, sx, _, X = c.field(0, ATLAS, g0 + 1, top)           # hangers, 1 m
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.84, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_canopy_edge(c):
    """The canopy slab's cast edge: concrete, an arris at the top, a drip
    groove near the foot."""
    y0, h = CANE_Y0, CANE_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_CONC, 1.0, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0 - PAD, y0 + h, 0.006, 1.5, axes="y")
    c.mul(0, ATLAS, y0 + 2, y0 + 3, 0.84, ao=0.82)
    c.lift(0, ATLAS, y0 + 2, y0 + 3, -0.004)
    c.mul(0, ATLAS, y0 - PAD, y0 + 2, 0.92)


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
    """An opening sash, proud of the frame, glazed inside its rails."""
    c.paint(a0, a1, b0, b1, ID_FRAME, 0.88)
    c.bevel(a0, a1, b0, b1, SASH_H, 1.0, base=FRAME_H)
    _light(c, a0 + inset, a1 - inset, b0 + inset + 1, b1 - inset)


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


def paint_window(c):
    """The offices' window: a top-hung vent light over the full width, and
    below a transom a narrow opening casement beside a wide fixed light, all
    in one white frame with a heavier bottom rail."""
    x, y, w, h = WIN
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 1.0, height=FRAME_H)
    c.bevel(x, x + w, y, y + h, FRAME_H, 1.0)
    F, B = 5, 6
    yt = y + h - F - m(0.45)                                # transom
    mx = x + F + 30
    _sash(c, x + F, mx, y + B, yt)
    _bar(c, mx, mx + 5, y + B, yt, axes="x")                # the mullion
    _light(c, mx + 5, x + w - F, y + B, yt)
    _bar(c, x + F, x + w - F, yt, yt + 5, axes="y")         # the transom
    _sash(c, x + F, x + w - F, yt + 5, y + h - F)
    c.mul(x, x + w, y, y + 2, 0.90, ao=0.86)


def paint_ctrl(c):
    """The control room's window: wider and taller, three fixed lights over
    a sill-high rail with a row of top-hung vent sashes above a transom, so
    the room reads as a band of glass from the yard."""
    x, y, w, h = CTRL
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 1.0, height=FRAME_H)
    c.bevel(x, x + w, y, y + h, FRAME_H, 1.0)
    F, B, M = 5, 6, 5
    yt = y + h - F - m(0.4375)
    inner = (w - 2 * F - 2 * M) / 3.0
    xs = [x + F + k * (inner + M) for k in range(3)]
    for k, a0 in enumerate(xs):
        _light(c, a0, a0 + inner, y + B, yt)
        _sash(c, a0, a0 + inner, yt + 4, y + h - F)
        if k < 2:
            _bar(c, a0 + inner, a0 + inner + M, y + B, y + h - F, axes="x")
    _bar(c, x + F, x + w - F, yt, yt + 4, axes="y")
    c.mul(x, x + w, y, y + 2, 0.90, ao=0.86)


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


def paint_patches(c):
    """Flat cells for surfaces a whole face takes one colour from."""
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0),
        "soffit": (ID_SOFFIT, 0.92, 0.80),
        "sill": (ID_SILL, 0.96, 0.92),
        "render": (ID_RENDER, 0.94, 0.88),
        "pipe": (ID_PIPE, 1.0, 0.95),
    }
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x - 2, x + w + 2, y - 2, y + h + 2, mid, sh, ao, height=0.0)


# ------------------------------------------------------------------ checks
def region_size_m(kind):
    x, y, w, h = REGION[kind]
    dx, dy = REGION_OFF.get(kind, (0, 0))
    return (w - 2 * dx) / PPM, (h - dy) / PPM


def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands, or
    run off the sheet, or if a region does not fit its opening."""
    rects = {"entrance": ENTRANCE, "service_door": SERVICE_DOOR, "win": WIN,
             "ctrl": CTRL, "conc": CONC, "vent": VENT, "pipe_top": PIPE_TOP}
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
    for kind, (w, h) in OPENINGS.items():
        rw, rh = region_size_m(kind)
        top = SURROUND_TOP if kind == "entrance" else 0.0
        if abs(rw - w) > 0.02 or abs(rh - top - h) > 0.02:
            problems.append("%s region is %.3f x %.3f m for a %.3f x %.3f m "
                            "opening" % (kind, rw, rh, w, h))
    if abs(m(Z_WALL_TOP) - BRICK_H) > 1e-6:
        problems.append("the brick band does not reach the wall head")
    if ATLAS % BATTEN or ATLAS % 64:
        problems.append("the roof's battens do not divide the atlas width")
    for z in (Z_PLINTH, Z_FLOOR, Z_FLOOR2, Z_BAND0, Z_EAVE, Z_SILL, Z_SILL2,
              Z_SILL_CTRL, Z_LEAF, ENTRY_H):
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
    steel = (ID_ROOF, ID_BATTEN, ID_FLASH, ID_GUTTER, ID_STEEL, ID_PIPE,
             ID_DOOR, ID_HANDLE)
    w = weathering.Weather(c, clean=(ID_GLASS,), steel=steel)
    w.grime()
    w.fade((ID_FRAME, ID_DOOR, ID_ENTRY, ID_FLASH, ID_ROOF, ID_BATTEN))
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
    # under the eave: the wall's head sheltered from rain
    w.shelter(0, ATLAS, BRICK_Y0 + m(Z_EAVE) - 40, BRICK_Y0 + BRICK_H + PAD, brick)
    # the roof: runs down the slope, dirt toward the gutter, chalking up top
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, SLOPE_LEN, (ID_ROOF, ID_BATTEN))
    # the gutter and the fascia under it
    w.add("D", 0, ATLAS, EAVE_Y0 + EAVE_H - 9, EAVE_Y0 + EAVE_H,
          lambda Y, X, nz: 0.08 + 0.10 * nz("blotch"), (ID_GUTTER,))
    w.runs(0, ATLAS, EAVE_Y0 - PAD, EAVE_Y0 + EAVE_H - 9, (ID_FLASH,), 0.12,
           fall=6.0, noise="short")
    # the canopy's edge: runs from its top
    w.runs(0, ATLAS, CANE_Y0, CANE_Y0 + CANE_H, (ID_CONC,), 0.12, fall=8.0,
           noise="short")
    # the windows: dirt standing on the bottom rails
    for rect in (WIN, CTRL):
        x, y, rw, rh = rect
        w.add("D", x, x + rw, y, y + 7, lambda Y, X, nz: 0.10
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
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_brick(c)
    paint_roof(c)
    paint_eave(c)
    paint_canopy_edge(c)
    c.check_bands(BAND_IDS)
    paint_entrance(c)
    paint_service_door(c)
    paint_window(c)
    paint_ctrl(c)
    paint_conc(c)
    paint_vent(c)
    paint_patches(c)

    # Tone wear, grain and pores. Every field is periodic, so the bands wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH, ID_SLAB))
    streak = atlas.noise(c, 7, 0.8, 40.0)
    c.shade[walls] *= 1.0 + 0.03 * streak[walls]
    sheet = np.isin(c.mid, (ID_FLASH, ID_DOOR, ID_ENTRY))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    c.shade[sheet] *= 1.0 + 0.016 * grain[sheet]
    roof = np.isin(c.mid, (ID_ROOF, ID_BATTEN))
    mottle = atlas.noise(c, 6, 3.0, 12.0)
    c.shade[roof] *= 1.0 + 0.05 * mottle[roof]
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
    t[ID_ROOF] = pal["roof"]
    t[ID_BATTEN] = pal["roof"]
    t[ID_FLASH] = pal["flash"]
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
