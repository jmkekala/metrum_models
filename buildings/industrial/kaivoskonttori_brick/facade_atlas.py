# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
kaivoskonttori_brick.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
the plan, the floor, sill, door and eave heights, band rows, opening sizes,
region rectangles -- so a change here cannot leave the UVs pointing at the
wrong artwork.

The atlas is a trim sheet. Four bands run the full width and tile in U:

    y    0 ..  232   BRICK   z 0 .. 3.625 m: rendered plinth, then brick
    y  238 ..  548   ROOF    standing-seam sheet, eave edge to ridge, with
                             the snow guard painted near its foot
    y  554 ..  570   EAVE    the eave fascia with its gutter
    y  576 ..  588   CANOPY  the entrance canopy's concrete edge
    y  596 ..  ...   unique  the entrance with its rendered surround, the
                             service door, the two window types, the concrete
                             for the steps and the canopy, the vent pipes,
                             patches

The brick band stops at the wall head. The gable triangles above Z_GABLE
sample the same band GABLE_SHIFT metres lower, a whole tone period of
courses, so the bond runs on across the line.

Every opening here is a single window or door, so each type has a region of
its own at 64 px/m, painted once and sampled by every opening of that type:
the office's ordinary windows, the dry's high windows, the entrance and the
service door.

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

ASSET = "kaivoskonttori_brick"
ATLAS = 1024
PPM = 64.0
PAD = 2                 # rows each band paints beyond its own edge

# ------------------------------------------------------------------ plan
# Front (-Y) is the long side. Walls at x = +-HX, y = +-HY: a 16 x 8 m shell,
# the office at the east (+X) end, the changing rooms and wash room (the dry)
# at the west end.
HX, HY = 8.0, 4.0

# ------------------------------------------------------------ vertical layout
# Metres above ground; every height a whole number of texels at 64 px/m.
Z_PLINTH = 0.375        # 24 px; rendered plinth under the brick
Z_FLOOR = 0.3125        # 20 px; the floor, and every door's threshold
Z_EAVE = 3.5            # 224 px; roof underside at the side-wall face,
                        # 3.1875 m over the floor
WALL_INTO_ROOF = 0.125  # walls run this far into the roof slab
Z_WALL_TOP = Z_EAVE + WALL_INTO_ROOF             # 3.625, 232 px
Z_GABLE = 3.25          # 208 px; the gables change rows a quarter metre
                        # under the soffit, as tehdas_brick_gable found the
                        # exact boolean wants
GABLE_SHIFT = 1.875     # 120 px = 24 courses = one tone period

# windows: the office's at desk height, the dry's above head height
Z_SILL = Z_FLOOR + 0.875                         # 1.1875
Z_SILL_HIGH = Z_FLOOR + 1.6875                   # 2.0
# doors: every leaf 2.125 m; the entrance has a transom light above it
Z_LEAF = 2.125          # leaf height over the threshold
ENTRY_H = 2.4375        # the entrance's opening, threshold to head
SURROUND = 0.1875       # the entrance's rendered surround, each side
SURROUND_TOP = 0.25     # and above the head, its top under the canopy

# the canopy over the entrance: a concrete slab sunk into the wall
Z_CAN0 = Z_FLOOR + ENTRY_H + 0.1875              # 2.9375, underside
Z_CAN1 = Z_CAN0 + 0.1875                         # 3.125, top

# the gable roof
TAN = 0.4375            # 23.6 degrees
ROOF_T = 0.25           # slab's vertical thickness = the fascia's height
EAVE_OUT = 0.45         # eave overhang, horizontal
RAKE_OUT = 0.30         # rake overhang at the gables
SLOPE_F = float(np.sqrt(1.0 + TAN * TAN))
SLOPE_LEN = (HY + EAVE_OUT) * SLOPE_F           # eave edge to ridge, 4.857 m

# ------------------------------------------------------------------ openings
# kind -> (width, height) of the opening in the brick, metres.
OPENINGS = {
    "win": (1.375, 1.3125),         # the office's ordinary windows
    "high": (1.25, 0.625),          # the dry's high windows
    "entrance": (1.125, ENTRY_H),   # half-glazed leaf and transom light
    "service_door": (1.125, 2.1875),
}
REVEAL = {"win": 0.15, "high": 0.15, "entrance": 0.20, "service_door": 0.15}

# ------------------------------------------------------------------- bands
BRICK_Y0, BRICK_H = 0, 232        # z 0 .. Z_WALL_TOP, plinth in the bottom 24
ROOF_Y0, ROOF_H = 238, 310        # the slope, eave edge to ridge
EAVE_Y0, EAVE_H = 554, 16         # the eave fascia, ROOF_T tall
GUTTER_PX = 9                     # the gutter's rows, across the fascia's top
# The downpipes' sides span the middle five of them (scripts/downpipes.py)
PIPE_STRIP = (EAVE_Y0 + EAVE_H - GUTTER_PX + 2, EAVE_Y0 + EAVE_H - 2)
CANE_Y0, CANE_H = 576, 12         # the canopy's edge, 0.1875 m
ROOF_RPM = ROOF_H / SLOPE_LEN     # roof rows per metre up the slope (63.8)

COURSE = 0.078125       # brick course pitch: 5 px
BRICK_L = 0.25          # stretcher: 16 px, 64 bricks per atlas width
TONE_COURSES = 24       # brick tone repeats every GABLE_SHIFT
SEAM = 32               # standing seams every 0.5 m, in px
SNOW_GUARD = (0.50, 0.74)   # slope metres from the eave edge: brackets
SNOW_RAILS = (0.58, 0.67)   # its two round rails, up the slope

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels, all at 64 px/m.
UNI_Y = 596
ENTRANCE = (4, UNI_Y, 96, 172)        # surround 1.5 x 2.6875 m round the door
SERVICE_DOOR = (104, UNI_Y, 72, 140)  # 1.125 x 2.1875 m
WIN = (180, UNI_Y, 88, 84)            # 1.375 x 1.3125 m
HIGH = (272, UNI_Y, 80, 40)           # 1.25 x 0.625 m
CONC = (356, UNI_Y, 160, 88)          # 2.5 x 1.375 m of cast concrete
VENT = (520, UNI_Y, 32, 96)           # a pipe's side: across x 1.5 m up
PIPE_TOP = (556, UNI_Y, 24, 24)       # a pipe's open end, planar

REGION = {"entrance": ENTRANCE, "service_door": SERVICE_DOOR, "win": WIN,
          "high": HIGH}
# where each region's opening sits inside it, (dx, dy) in px: the entrance
# region carries its surround round the opening
REGION_OFF = {"entrance": (int(SURROUND * PPM), 0)}

PATCH_NAMES = ("blank", "soffit", "sill", "render", "barge", "pipe")
PATCHES = {n: (4 + 20 * i, 1004, 16, 16) for i, n in enumerate(PATCH_NAMES)}

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_FRAME, ID_GLASS, ID_ROOF, ID_FLASH, ID_SNOW = 5, 6, 7, 8, 9
ID_CONC, ID_DOOR, ID_RENDER, ID_STEEL, ID_PIPE = 10, 11, 12, 13, 14
ID_SOFFIT, ID_GUTTER, ID_HANDLE, ID_DARK, ID_SEAL = 15, 16, 17, 18, 19
ID_SILL, ID_ENTRY = 20, 21

# (roughness, metallic). The roof, fascia and snow guard are painted sheet,
# mostly dielectric; the gutter is bare galvanised steel.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.92, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.82, 0.0), ID_MORTAR: (0.94, 0.0), ID_FRAME: (0.48, 0.0),
    ID_GLASS: (glazing.ROUGHNESS, 0.0), ID_ROOF: (0.46, 0.25),
    ID_FLASH: (0.48, 0.20), ID_SNOW: (0.44, 0.30), ID_CONC: (0.90, 0.0),
    ID_DOOR: (0.50, 0.0), ID_RENDER: (0.90, 0.0), ID_STEEL: (0.38, 0.75),
    ID_PIPE: (0.55, 0.20), ID_SOFFIT: (0.74, 0.0), ID_GUTTER: (0.36, 0.70),
    ID_HANDLE: (0.30, 0.85), ID_DARK: (0.96, 0.0), ID_SEAL: (0.90, 0.0),
    ID_SILL: (0.86, 0.0), ID_ENTRY: (0.44, 0.0),
}

# ---------------------------------------------------------------- palettes
# One coherent treatment per instance: the brick changes, and the frames,
# roof and doors move with it. The roof stays dark in every variant, the
# gutter and pipes galvanised; the render, canopy and steps are fixed.
VARIANTS = {
    "red_brick": {"brick": (146, 74, 54), "brick2": (116, 60, 47),
                  "mortar": (150, 145, 136), "frame": (222, 220, 212),
                  "roof": (58, 60, 62), "flash": (62, 64, 66),
                  "entry": (98, 70, 50), "door": (86, 94, 90)},
    "yellow_brick": {"brick": (190, 168, 124), "brick2": (166, 144, 104),
                     "mortar": (162, 158, 150), "frame": (66, 76, 72),
                     "roof": (54, 56, 58), "flash": (58, 60, 62),
                     "entry": (62, 84, 74), "door": (82, 88, 92)},
    "brown_brick": {"brick": (112, 76, 60), "brick2": (90, 62, 50),
                    "mortar": (128, 122, 114), "frame": (214, 210, 198),
                    "roof": (52, 50, 48), "flash": (56, 54, 52),
                    "entry": (112, 80, 54), "door": (80, 74, 68)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (140, 138, 132), ID_CONC: (178, 176, 170),
    ID_RENDER: (196, 192, 182), ID_STEEL: (150, 152, 150), ID_PIPE: (62, 62, 64),
    ID_SOFFIT: (200, 198, 192), ID_HANDLE: (168, 168, 166), ID_DARK: (24, 24, 24),
    ID_SEAL: (34, 34, 34), ID_BLANK: (52, 52, 52), ID_SILL: (168, 166, 160),
    ID_GUTTER: (150, 152, 150),
}

BAND_IDS = {
    "BRICK": ((0, 234), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH}),
    "ROOF": ((236, 550), {ID_ROOF, ID_SNOW}),
    "EAVE": ((552, 572), {ID_FLASH, ID_GUTTER}),
    "CANOPY": ((574, 590), {ID_CONC}),
}

# The candidate-glazing mask is the emission map, neutral white.
EMIT = {ID_GLASS: (255, 255, 255)}
# Linear RGB. Offices and a changing room are lit by fluorescent tubes, as
# tehdas_brick_gable's are; the same reference factor.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
BRICK_FACE = 0.006      # brick face proud of the recessed mortar
FRAME_H = 0.030         # window and door frames, proud of the glass
SASH_H = 0.045          # an opening sash, proud of the frame
DOOR_FRAME_H = 0.020    # steel door frames
SEAM_H = 0.025          # standing seam
GUTTER_R = 0.070        # half-round gutter
RAIL_H = 0.035          # the snow guard's rails over the sheet
RENDER_H = 0.012        # the entrance surround, proud of the brick


def m(v):
    """Metres -> pixels."""
    return v * PPM


# ================================================================== bands
def paint_plinth(c, y0):
    """Rendered plinth, the base every wall stands on: cement render with a
    trowelled texture, darker at its foot, a shadow line under the brick."""
    h = m(Z_PLINTH)
    c.paint(0, ATLAS, y0 - PAD, y0 + h, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, y0 - PAD, y0 + h)
    z = (Y - y0) / PPM
    c.shade[sy, sx] *= 0.84 + 0.16 * np.clip(z / 0.20, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.20, 0, 1))
    c.mul(0, ATLAS, y0 + h - 2, y0 + h, 0.86, ao=0.84)


def paint_brick(c):
    """Stretcher-bond facing brick, 0.25 x 0.078125 m, in two tones; the
    mortar recessed and its own id. Tone and bond repeat at the atlas wrap in
    U and every TONE_COURSES in V, which lets the gables sample these rows
    again higher up."""
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


def paint_roof(c):
    """Standing-seam sheet: a seam down the slope every 0.5 m, the pans
    between faintly oil-canned, a drip at the eave and the ridge cap at the
    top, and the snow guard painted across the foot of the slope: two round
    rails on a bracket every metre, about a metre up from the eave edge,
    over the wall line."""
    y0, h = ROOF_Y0, ROOF_H
    k = ROOF_RPM / PPM                     # V relief scales by rows per metre
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_ROOF, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    d = np.abs(((X % SEAM) + SEAM / 2.0) % SEAM - SEAM / 2.0)   # to the seam
    height = SEAM_H * np.clip((1.6 - d) / 1.0, 0.0, 1.0)
    shade = np.where((d >= 1.6) & (d < 3.0), 0.90, 1.0)
    ao = np.where((d >= 1.6) & (d < 3.0), 0.86, 1.0)
    pan = 0.003 * np.cos(np.pi * (X % SEAM) / SEAM * 2.0)       # oil canning
    height = height + np.where(d >= 1.6, pan, 0.0)
    v = Y - y0
    shade = np.where(v < 2, shade * 0.82, shade)                  # eave drip
    ridge = v >= h - 4
    height = np.where(ridge, 0.012 * k, height)
    shade = np.where(ridge, 0.97, shade)
    ao = np.where(ridge, 1.0, ao)
    shade = np.where((v >= h - 5) & (v < h - 4), shade * 0.80, shade)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao
    # the snow guard: brackets on the seams' clamps, then the two rails
    b0, b1 = y0 + SNOW_GUARD[0] * ROOF_RPM, y0 + SNOW_GUARD[1] * ROOF_RPM
    for i in range(int(ATLAS / 64)):
        x = i * 64.0 + SEAM / 2.0           # on a seam
        c.paint(x - 1.0, x + 1.0, b0, b1, ID_SNOW, 0.92, 0.9, height=0.03 * k)
        c.mul(x + 1.0, x + 2.5, b0, b1, 0.86, ao=0.84)       # its shadow
    for zr in SNOW_RAILS:
        yc = y0 + zr * ROOF_RPM
        r = 1.4
        c.paint(0, ATLAS, yc - r, yc + r, ID_SNOW, 1.0, 1.0)
        sy, sx, Y, _ = c.field(0, ATLAS, yc - r, yc + r)
        u = (Y - yc) / r
        c.height[sy, sx] = RAIL_H * k * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
        c.mul(0, ATLAS, yc - r - 1.5, yc - r, 0.80, ao=0.80)  # shadow below


def paint_eave(c):
    """The eave's vertical edge: a sheet fascia in the roof's colour with a
    half-round galvanised gutter hung across its top, hangers every metre."""
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


def paint_entrance(c):
    """The entrance: a rendered surround round three sides of the opening,
    and in it a half-glazed leaf in a painted frame with a transom light over
    it. The leaf is the variant's entrance colour, its upper two thirds
    glazed; the lower a fielded panel with a kick plate."""
    x, y, w, h = ENTRANCE
    s = m(SURROUND)
    # the surround: render, proud of the brick, its arrises bevelled
    c.paint(x, x + w, y, y + h, ID_RENDER, 1.0, 1.0)
    c.bevel(x, x + w, y - 4, y + h, RENDER_H, 1.5, axes="xy")
    ox0, ox1, oy1 = x + s, x + w - s, y + m(ENTRY_H)
    c.mul(ox0 - 2, ox0, y, oy1 + 2, 0.90, ao=0.86)      # shadow into the reveal
    c.mul(ox1, ox1 + 2, y, oy1 + 2, 0.94, ao=0.90)
    c.mul(ox0 - 2, ox1 + 2, oy1, oy1 + 2, 0.92, ao=0.88)
    # the opening: frame, transom light, leaf
    c.paint(ox0, ox1, y, oy1, ID_GLASS, 1.0, 1.0, height=0.0)
    F = 4
    yl = y + m(Z_LEAF)
    _bar(c, ox0, ox1, y, y + 2, axes="y")                   # threshold
    _bar(c, ox0, ox1, oy1 - F, oy1, axes="y")               # head
    _bar(c, ox0, ox0 + F, y, oy1, axes="x")
    _bar(c, ox1 - F, ox1, y, oy1, axes="x")
    _bar(c, ox0, ox1, yl, yl + 4, axes="y")                 # transom bar
    c.mul(ox0 + F, ox1 - F, oy1 - F - 3, oy1 - F, 0.90, ao=0.84)
    l0, l1 = ox0 + F, ox1 - F                               # the leaf, 1.0 m
    st, gb, gt = 7, y + m(0.95), yl - 8
    _bar(c, l0, l1, y + 2, yl, ID_ENTRY, 0.04, 0.9, 1.0)
    c.paint(l0 + st, l1 - st, gb, gt, ID_GLASS, 1.0, 1.0, height=0.0)
    c.mul(l0 + st, l1 - st, gt - 4, gt, 0.90, ao=0.84)     # under the top rail
    # glazing bead round the light
    for a0, a1, b0, b1, ax in ((l0 + st - 1, l0 + st, gb, gt, "x"),
                               (l1 - st, l1 - st + 1, gb, gt, "x"),
                               (l0 + st, l1 - st, gb - 1, gb, "y")):
        _bar(c, a0, a1, b0, b1, ID_ENTRY, 0.05, 0.86, 0.9, ax)
    # the fielded panel below, and a kick plate
    p0, p1 = y + 16, gb - 8
    c.bevel(l0 + st + 2, l1 - st - 2, p0, p1, 0.046, 3.0, base=0.04)
    c.mul(l0 + st, l1 - st, p1, p1 + 1, 0.88, ao=0.86)
    c.paint(l0 + 2, l1 - 2, y + 2, y + 13, ID_STEEL, 0.9, 0.9, height=0.043)
    _handle(c, l1 - 9, y + m(0.85), y + m(1.30))


def paint_service_door(c):
    """A plain steel leaf in a steel frame: the back door the shift comes in
    by."""
    x, y, w, h = SERVICE_DOOR
    c.paint(x, x + w, y, y + h, ID_DOOR, 0.86, 0.9, height=0.0)
    F = 4
    _bar(c, x, x + F, y, y + h, ID_DOOR, DOOR_FRAME_H, 0.84, 0.86, "x")
    _bar(c, x + w - F, x + w, y, y + h, ID_DOOR, DOOR_FRAME_H, 0.84, 0.86, "x")
    _bar(c, x, x + w, y + h - F, y + h, ID_DOOR, DOOR_FRAME_H, 0.84, 0.86, "y")
    l0, l1, t = x + F, x + w - F, y + h - F
    c.paint(l0, l1, y, t, ID_DOOR, 1.0, 0.96, height=0.0)
    c.mul(l0, l1, t - 3, t, 0.88, ao=0.84)
    c.paint(l0 + 2, l1 - 2, y + 2, y + m(0.25), ID_STEEL, 0.9, 0.9, height=0.003)
    hx, hy = l1 - 8, y + m(1.0)
    c.paint(hx - 1.5, hx + 1.5, hy - 5, hy + 5, ID_HANDLE, 1.0, 0.9, height=0.01)
    c.stroke((hx, hy + 2), (hx - 8, hy + 2), 2.2, ID_HANDLE, 1.0, 0.9, height=0.04)


def _light(c, a0, a1, b0, b1):
    """A pane in its frame, the frame's head rail shading its top."""
    c.paint(a0, a1, b0, b1, ID_GLASS, 1.0, 0.92, height=0.0)
    c.mul(a0, a1, b1 - 4, b1, 0.90, ao=0.84)


def _sash(c, a0, a1, b0, b1, inset=3):
    """An opening sash, proud of the frame, glazed inside its rails."""
    c.paint(a0, a1, b0, b1, ID_FRAME, 0.88)
    c.bevel(a0, a1, b0, b1, SASH_H, 1.0, base=FRAME_H)
    _light(c, a0 + inset, a1 - inset, b0 + inset + 1, b1 - inset)


def paint_window(c):
    """The office's ordinary window: a narrow opening casement beside a wide
    fixed light, under one frame, the bottom rail a little heavier."""
    x, y, w, h = WIN
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 1.0, height=FRAME_H)
    c.bevel(x, x + w, y, y + h, FRAME_H, 1.0)
    F, B, mx = 5, 6, x + 31
    _sash(c, x + F, mx, y + B, y + h - F)
    _bar(c, mx, mx + 5, y + B, y + h - F, axes="x")         # the mullion
    _light(c, mx + 5, x + w - F, y + B, y + h - F)
    c.mul(x, x + w, y, y + 2, 0.90, ao=0.86)


def paint_high(c):
    """The dry's high window: two bottom-hung lights side by side, each a
    sash in the frame."""
    x, y, w, h = HIGH
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 1.0, height=FRAME_H)
    c.bevel(x, x + w, y, y + h, FRAME_H, 1.0)
    F, B, mx = 4, 5, x + w / 2.0
    _sash(c, x + F, mx - 2, y + B, y + h - F)
    _sash(c, mx + 2, x + w - F, y + B, y + h - F)
    c.mul(x, x + w, y, y + 2, 0.90, ao=0.86)


def paint_conc(c):
    """Cast concrete for the steps and the canopy's top: board-float
    texture, pores, the arrises a little lighter."""
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
        "barge": (ID_FLASH, 0.92, 0.94),
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
             "high": HIGH, "conc": CONC, "vent": VENT, "pipe_top": PIPE_TOP}
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
    if (m(GABLE_SHIFT) / m(COURSE)) % TONE_COURSES:
        problems.append("GABLE_SHIFT is not a whole tone period of courses")
    if ATLAS % SEAM or ATLAS % 64:
        problems.append("the roof's seams do not divide the atlas width")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    The brick band's V is height from the ground, so the plinth's soil, the
    splash-back and the salt bloom land the same on every wall. The gable
    triangles sample the band from 1.375 m up, above the bloom.
    """
    brick = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    steel = (ID_ROOF, ID_FLASH, ID_GUTTER, ID_STEEL, ID_PIPE, ID_SNOW,
             ID_DOOR, ID_HANDLE)
    w = weathering.Weather(c, clean=(ID_GLASS,), steel=steel)
    w.grime()
    w.fade((ID_FRAME, ID_DOOR, ID_ENTRY, ID_FLASH, ID_ROOF))
    w.wash(brick)
    w.plinth(0, ATLAS, BRICK_Y0, BRICK_Y0 + m(Z_PLINTH), (ID_PLINTH,))
    w.splash(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + BRICK_H + PAD, brick)
    w.bloom(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(1.2), brick,
            amount=0.10, fade=m(0.6))
    # the roof: runs down the slope, dirt toward the gutter, chalking up top
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, SLOPE_LEN, (ID_ROOF, ID_SNOW))
    # the gutter and the fascia under it
    w.add("D", 0, ATLAS, EAVE_Y0 + EAVE_H - 9, EAVE_Y0 + EAVE_H,
          lambda Y, X, nz: 0.08 + 0.10 * nz("blotch"), (ID_GUTTER,))
    w.runs(0, ATLAS, EAVE_Y0 - PAD, EAVE_Y0 + EAVE_H - 9, (ID_FLASH,), 0.12,
           fall=6.0, noise="short")
    # the canopy's edge: runs from its top
    w.runs(0, ATLAS, CANE_Y0, CANE_Y0 + CANE_H, (ID_CONC,), 0.12, fall=8.0,
           noise="short")
    # the windows: dirt standing on the bottom rails
    for rect in (WIN, HIGH):
        x, y, rw, rh = rect
        w.add("D", x, x + rw, y, y + 7, lambda Y, X, nz: 0.10
              + 0.12 * atlas.smoothstep(0.2, 1.4, nz("short")), (ID_FRAME,))
    # the doors: their feet and handles; the surround's foot splashed
    x, y, rw, rh = ENTRANCE
    s = m(SURROUND)
    w.door(x + s + 4, x + rw - s - 4, y, y + m(Z_LEAF), (ID_ENTRY, ID_STEEL),
           handle=(x + rw - s - 13, y + m(1.05)))
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
    paint_high(c)
    paint_conc(c)
    paint_vent(c)
    paint_patches(c)

    # Tone wear, grain and pores. Every field is periodic, so the bands wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH))
    streak = atlas.noise(c, 7, 0.8, 40.0)
    c.shade[walls] *= 1.0 + 0.03 * streak[walls]
    sheet = np.isin(c.mid, (ID_FLASH, ID_DOOR, ID_ENTRY))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    c.shade[sheet] *= 1.0 + 0.016 * grain[sheet]
    roof = c.mid == ID_ROOF
    runs = atlas.noise(c, 6, 0.6, 20.0)
    c.shade[roof] *= 1.0 + 0.025 * runs[roof]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_CONC, ID_MORTAR, ID_RENDER, ID_SILL))
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
    t[ID_SNOW] = pal["roof"]
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
