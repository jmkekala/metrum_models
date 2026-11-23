# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
nostokonehuone_brick.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
plan, heights, opening sizes, band rows, region rectangles -- so a change here
cannot leave the UVs pointing at the wrong artwork.

The atlas is a trim sheet. Three bands run the full width and tile in U:

    y    0 ..  376   BRICK   z 0 .. 5.875 m: concrete plinth, facing brick,
                             the cast concrete lintel band at the window heads
    y  384 ..  552   ROOF    standing-seam sheet, V stretched up the slope, the
                             snow guard just inside the wall line
    y  558 ..  574   EAVE    the eave fascia with its gutter
    y  586 .. 1020   unique  the two tall steel windows, the entrance screen,
                             the machinery door, the rope-slot louvre, the vent
                             pipes, the entrance's floor slab and the flat
                             patches

The brick band stops at the wall head. The two gable triangles above Z_GABLE
sample the same band GABLE_SHIFT metres lower, a whole tone period of
courses, so the bond runs on across the line without a second band of brick.
The lintel band's rows stay above anything the triangles sample.

Rasterising is scripts/atlas.py's; dirt, algae, rust and faded paint are
scripts/weathering.py's fields, placed by weather() below.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import brickwork  # noqa: E402
import door_floor as DF  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "nostokonehuone_brick"
ATLAS = 1024
PPM = 64.0
PAD = 2                 # rows each band paints beyond its own edge

# ------------------------------------------------------------------ plan
# Gable end to the front (-Y): the machinery door is in it, and the long walls
# carry the window rhythm. 9.0 x 11.5 m at the outer wall faces, ridge along Y.
HX, HY = 4.5, 5.75

# ------------------------------------------------------------ vertical layout
# Metres above ground. Every height is a whole number of texels at 64 px/m.
Z_PLINTH = 0.5          # 32 px; cast concrete base under every wall
Z_SILL = 1.25           # 80 px; every tall window's sill
WIN_W, WIN_H = 1.625, 3.0
Z_HEAD = Z_SILL + WIN_H                          # 4.25, 272 px: window heads
Z_BAND = 4.5625         # 292 px; top of the concrete lintel band
Z_LEAF = 2.125          # 136 px; the pedestrian door leaf's head
Z_EAVE = 5.75           # 368 px; roof underside at the long walls' face
WALL_INTO_ROOF = 0.125  # walls run this far into the roof slab
Z_WALL_TOP = Z_EAVE + WALL_INTO_ROOF             # 5.875, 376 px
Z_GABLE = 5.5           # 352 px; the gable walls change rows here, a quarter
                        # metre under the soffit line
GABLE_SHIFT = 3.75      # 240 px = 48 courses = one tone period
Z_SLOT = 6.0            # the rope slot's sill, high in the rear gable

# the gable roof
TAN = 0.4               # 21.8 degrees
ROOF_T = 0.25           # slab's vertical thickness = the fascia's height
EAVE_OUT = 0.40         # eave overhang at the long walls, horizontal
RAKE_OUT = 0.30         # rake overhang at the gables
SLOPE_F = float(np.sqrt(1.0 + TAN * TAN))
SLOPE_LEN = (HX + EAVE_OUT) * SLOPE_F           # eave edge to ridge, 5.277 m

# ------------------------------------------------------------------ openings
# kind -> (width, height) of the opening in the brick, metres. The steel
# frames are set back REVEAL metres in the brick.
OPENINGS = {
    "window": (WIN_W, WIN_H),
    "window_b": (WIN_W, WIN_H),
    "screen": (WIN_W, Z_HEAD),          # entrance: door and glazing in one bay
    "bigdoor": (3.375, 3.75),           # the machinery door
    "slot": (1.5, 0.75),                # the rope slot's louvre
}
REVEAL = {"window": 0.20, "window_b": 0.20, "screen": 0.20, "bigdoor": 0.25,
          "slot": 0.15}

# ------------------------------------------------------------------- bands
BRICK_Y0, BRICK_H = 0, 376        # z 0 .. Z_WALL_TOP
ROOF_Y0, ROOF_H = 384, 168        # the slope, eave edge to ridge
EAVE_Y0, EAVE_H = 558, 16         # the eave fascia, ROOF_T tall
GUTTER_PX = 9                     # the gutter's rows, across the fascia's top
# The downpipes' sides span the middle five of them (scripts/downpipes.py)
PIPE_STRIP = (EAVE_Y0 + EAVE_H - GUTTER_PX + 2, EAVE_Y0 + EAVE_H - 2)
ROOF_RPM = ROOF_H / SLOPE_LEN     # roof rows per metre up the slope
SEAM = 32.0                       # standing seams every 0.5 m, px along U
# The snow guard's lower tube, metres up the slope from the eave's edge: just
# inside the wall line (the 0.40 m eave is 0.43 m of slope), where its
# brackets bear over the wall.
SNOW_GUARD = 0.55

COURSE = brickwork.COURSE      # brick course pitch: 5 px
BRICK_L = brickwork.BRICK_L    # stretcher: 16 px, 64 bricks per atlas width
TONE_COURSES = 48       # brick tone repeats every GABLE_SHIFT

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels, all at 64 px/m. check_regions() asserts they neither
# overlap nor run off the sheet.
UNI_Y = 586
SCREEN = (4, UNI_Y, 104, 272)            # 1.625 x 4.25 m
BIGDOOR = (116, UNI_Y, 216, 240)         # 3.375 x 3.75 m
WINDOW = (340, UNI_Y, 104, 192)          # 1.625 x 3.0 m
WINDOW_B = (452, UNI_Y, 104, 192)
SLOT = (564, UNI_Y, 96, 48)              # 1.5 x 0.75 m
VENT = (668, UNI_Y, 32, 96)              # a pipe's side: across x 1.5 m up
PIPE_TOP = (708, UNI_Y, 24, 24)          # a pipe's open end, planar

# The concrete floor slab in the entrance's reveal (scripts/door_floor.py),
# unfolded at 64 px/m: U across the opening, V up the nosing and back to the
# screen. 1.625 m wide and 0.20 m deep.
FLOORS = {"entrance": DF.Floor(740, UNI_Y, OPENINGS["screen"][0], REVEAL["screen"])}

REGION = {"screen": SCREEN, "bigdoor": BIGDOOR, "window": WINDOW,
          "window_b": WINDOW_B, "slot": SLOT}

PATCH_NAMES = ("blank", "soffit", "sill", "conc", "barge", "pipe")
PATCHES = {n: (4 + 20 * i, 1004, 16, 16) for i, n in enumerate(PATCH_NAMES)}

# The doors' clear leaves, as painted (build.py's facts() reads these)
SCREEN_LEAF = (20, 84)                   # px across the screen region
BIGDOOR_FRAME = 6                        # px of steel frame round the pair

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_FRAME, ID_GLASS, ID_ROOF, ID_FLASH, ID_CONC = 5, 6, 7, 8, 9
ID_DOOR, ID_GUTTER, ID_HANDLE, ID_DARK, ID_PIPE = 10, 11, 12, 13, 14
ID_SOFFIT, ID_SEAL = 15, 16
ID_FLOOR = 17           # the cast concrete floor slab in the entrance's reveal

# (roughness, metallic). Painted or coated steel is dielectric -- the paint is
# what the light sees: the roof sheet, the fascia and barge flashing, the
# frames, the doors and the black vent pipes. The gutter, downpipes and snow
# guard are bare galvanised steel, and metal.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.82, 0.0), ID_MORTAR: (0.94, 0.0), ID_FRAME: (0.44, 0.0),
    ID_GLASS: (glazing.ROUGHNESS, 0.0), ID_ROOF: (0.48, 0.0),
    ID_FLASH: (0.46, 0.0), ID_CONC: (0.90, 0.0), ID_DOOR: (0.52, 0.0),
    ID_GUTTER: (0.48, 0.60), ID_HANDLE: (0.35, 0.80), ID_DARK: (0.96, 0.0),
    ID_PIPE: (0.55, 0.0), ID_SOFFIT: (0.74, 0.0), ID_SEAL: (0.90, 0.0),
    ID_FLOOR: DF.SURFACE,
}

# ---------------------------------------------------------------- palettes
# One coherent brick per instance: the brick changes, and the window steel,
# the doors and the roof move with it. Window steel is always lighter than
# the glass it holds.
VARIANTS = {
    "red_brick": {"brick": (144, 72, 52), "brick2": (114, 58, 45),
                  "mortar": (150, 145, 136), "frame": (206, 204, 196),
                  "door": (66, 82, 76), "roof": (58, 60, 62)},
    "yellow_brick": {"brick": (188, 166, 122), "brick2": (164, 142, 104),
                     "mortar": (160, 156, 148), "frame": (104, 116, 108),
                     "door": (104, 56, 44), "roof": (62, 64, 66)},
    "brown_brick": {"brick": (98, 68, 54), "brick2": (78, 54, 44),
                    "mortar": (124, 118, 110), "frame": (186, 182, 172),
                    "door": (60, 68, 76), "roof": (52, 52, 54)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (150, 148, 142), ID_CONC: (170, 168, 160),
    ID_GUTTER: (134, 137, 137), ID_HANDLE: (150, 150, 148), ID_DARK: (24, 24, 24),
    ID_PIPE: (62, 62, 64), ID_SOFFIT: (176, 174, 168), ID_SEAL: (34, 34, 34),
    ID_BLANK: (52, 52, 52), ID_FLOOR: DF.COLOUR,
}

# A stray pixel in a tiling band is not a local blemish: every surface that
# samples the band repeats it.
BAND_IDS = {
    "BRICK": ((0, 378), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH, ID_CONC}),
    "ROOF": ((382, 554), {ID_ROOF, ID_GUTTER}),
    "EAVE": ((556, 576), {ID_FLASH, ID_GUTTER}),
}

# The candidate-glazing mask is the emission map, neutral white.
EMIT = {ID_GLASS: (255, 255, 255)}
# Linear RGB. An engine hall is lit by industrial lamps, not a living-room
# bulb; the value is the one tehdas_brick_gable uses for its workshop.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto: only the few
# centimetres the mesh does not model. The roof band is painted at ROOF_RPM
# rows a metre up the slope, so relief that varies in V there is scaled by
# ROOF_RPM / PPM to keep its slope physical.
BRICK_FACE = brickwork.BRICK_FACE   # brick face proud of the recessed mortar
BAND_H = 0.010          # the lintel band, proud of the brick
FRAME_H = 0.035         # window and screen outer frames, proud of the glass
BAR_H = 0.022           # glazing bars
SASH_H = 0.045          # the hopper's sash, proud of the frame
DOOR_FRAME_H = 0.030    # door frames and stiles
RIB_H = 0.006           # the machinery door's sheet ribs
SEAM_H = 0.040          # standing seams
GUTTER_R = 0.070        # half-round gutter
TUBE_H = 0.045          # snow-guard tubes
GUARD_BRACKET_H = 0.040


def m(v):
    """Metres -> pixels."""
    return v * PPM


def region_size_m(kind):
    x, y, w, h = REGION[kind]
    return w / PPM, h / PPM


# ================================================================== bands
def paint_plinth(c, y0):
    """Cast concrete, the 0.5 m base every wall stands on."""
    h = m(Z_PLINTH)
    c.paint(0, ATLAS, y0 - PAD, y0 + h, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, y0 - PAD, y0 + h)
    z = (Y - y0) / PPM
    c.shade[sy, sx] *= 0.82 + 0.18 * np.clip(z / 0.20, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.20, 0, 1))
    # board-formed pour line, and the occluded strip under the brick's drip
    for zz in (0.25,):
        c.mul(0, ATLAS, y0 + m(zz), y0 + m(zz) + 1, 0.94, ao=0.94)
        c.lift(0, ATLAS, y0 + m(zz), y0 + m(zz) + 1, -0.002)
    c.mul(0, ATLAS, y0 + h - 2, y0 + h, 0.88, ao=0.86)


def paint_band(c):
    """The cast concrete lintel band the window heads stand under, running
    round the whole building: arrises catching the light, a drip shadow on
    the brick under it, and dirt where the brick above sheds onto its top."""
    b0, b1 = BRICK_Y0 + m(Z_HEAD), BRICK_Y0 + m(Z_BAND)
    c.paint(0, ATLAS, b0, b1, ID_CONC, 1.0, 1.0)
    c.bevel(0, ATLAS, b0, b1, BAND_H, 1.0, axes="y")
    c.mul(0, ATLAS, b0, b0 + 1, 0.86, ao=0.86)            # its soffit edge
    c.mul(0, ATLAS, b0 - 2, b0, 0.88, ao=0.84)            # shadow on the brick
    c.mul(0, ATLAS, b1 - 1, b1, 0.96)
    # formwork joints every 2 m, a period that divides the atlas width
    for i in range(int(ATLAS / 128)):
        x = i * 128.0
        c.mul(x, x + 1, b0, b1, 0.90, ao=0.90)
        c.lift(x, x + 1, b0, b1, -0.003)


def paint_brick(c):
    """Stretcher-bond facing brick, 0.25 x 0.078125 m, 64 bricks per width,
    in two tones, mortar recessed and its own id. Tone and bond repeat at the
    atlas wrap in U and every TONE_COURSES in V, which is what lets the gables
    sample these rows again higher up."""
    brickwork.paint(c, 0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + BRICK_H + PAD,
                    (ID_BRICK, ID_BRICK2, ID_MORTAR), TONE_COURSES, seed=17)
    paint_plinth(c, BRICK_Y0)
    paint_band(c)


def paint_roof(c):
    """Standing-seam steel: a seam down the slope every 0.5 m, flat pans
    between with a little oil-canning, a drip at the eave and the ridge cap at
    the top. The snow guard is two round tubes across the band on brackets
    clamped to every second seam, galvanised like the gutter (ID_GUTTER).

    V is stretched (ROOF_H rows over SLOPE_LEN); the seams vary in U only, at
    64 px/m, and what varies in V is scaled by ROOF_RPM over PPM."""
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_ROOF, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    d = np.abs(((X % SEAM) + SEAM / 2.0) % SEAM - SEAM / 2.0)   # to the seam
    height = SEAM_H * np.sqrt(np.clip(1.0 - (d / 1.6) ** 2, 0.0, 1.0))
    foot = (d >= 1.6) & (d < 2.8)
    shade = np.where(foot, 0.90, 1.0)
    ao = np.where(foot, 0.84, 1.0)
    k = ROOF_RPM / PPM
    v = Y - y0
    shade = np.where(v < 2, shade * 0.84, shade)                     # eave drip
    # snow guard
    g = round(SNOW_GUARD * ROOF_RPM)
    guard = np.zeros(v.shape, bool)
    for t0, t1 in ((g, g + 2.0), (g + 3.0, g + 4.5)):
        inside = (v >= t0) & (v < t1)
        tube = TUBE_H * k * np.sqrt(np.clip(
            1.0 - (2.0 * (v - t0) / (t1 - t0) - 1.0) ** 2, 0.0, 1.0))
        height = np.where(inside, np.maximum(height, tube), height)
        shade = np.where(inside, 1.0, shade)
        guard |= inside
    shade = np.where((v >= g - 3) & (v < g - 1), shade * 0.80, shade)   # under the tubes
    ao = np.where((v >= g - 3) & (v < g + 4.5), np.minimum(ao, 0.85), ao)
    xb = X % (2.0 * SEAM)
    bracket = (xb >= 2.0) & (xb < 5.0) & (v >= g - 3) & (v < g + 4.5)
    height = np.where(bracket, GUARD_BRACKET_H * k, height)
    shade = np.where(bracket, 0.75, shade)
    guard |= bracket
    ridge = v >= h - 8                                               # ridge cap
    height = np.where(ridge, 0.012 * k, height)
    shade = np.where(ridge, 0.97, shade)
    ao = np.where(ridge, 1.0, ao)
    shade = np.where((v >= h - 9) & (v < h - 8), shade * 0.80, shade)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao
    c.mid[sy, sx] = np.where(guard, ID_GUTTER, ID_ROOF)


def paint_eave(c):
    """The eave's vertical edge: a fascia of folded sheet in the roof's
    colour with a half-round galvanised gutter hung across its top, hangers
    every metre."""
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
    for k, f in enumerate((0.84, 0.90, 0.95)):             # under the gutter
        c.mul(0, ATLAS, g0 - 1 - k, g0 - k, f, ao=0.86)
    sy, sx, _, X = c.field(0, ATLAS, g0 + 1, top)           # hangers, 1 m
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.84, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


# ================================================================= regions
def _bar(c, a0, a1, b0, b1, mid=ID_FRAME, h=FRAME_H, ao=0.88, shade=1.0, axes="xy"):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, 1.0, axes=axes)


def _grid(c, x0, x1, y0, y1, cols, rows, bar=2.0):
    """Glass from x0..x1, y0..y1 in cols x rows small panes, divided by steel
    glazing bars *bar* px wide; each pane's head shaded by its bar."""
    c.paint(x0, x1, y0, y1, ID_FRAME, 1.0, 0.9, height=BAR_H)
    pw, ph = (x1 - x0) / cols, (y1 - y0) / rows
    for i in range(cols):
        for j in range(rows):
            a0 = x0 + i * pw + (bar / 2.0 if i else 0.0)
            a1 = x0 + (i + 1) * pw - (bar / 2.0 if i < cols - 1 else 0.0)
            b0 = y0 + j * ph + (bar / 2.0 if j else 0.0)
            b1 = y0 + (j + 1) * ph - (bar / 2.0 if j < rows - 1 else 0.0)
            c.paint(a0, a1, b0, b1, ID_GLASS, 1.0, 0.92, height=0.0)
            c.mul(a0, a1, b1 - 2, b1, 0.92, ao=0.86)


def paint_window(c, rect):
    """A tall steel industrial window: a heavy frame round 4 x 8 small panes
    on slim glazing bars, and a bottom-hung hopper two panes high across the
    middle, its sash standing proud. scripts/glazing.py paints one room per
    window, the bars being thinner than its merge."""
    x, y, w, h = rect
    F = 5
    _bar(c, x - PAD, x + w + PAD, y - PAD, y + h + PAD, h=FRAME_H, axes="xy")
    gx0, gx1, gy0, gy1 = x + F, x + w - F, y + F + 1, y + h - F
    _grid(c, gx0, gx1, gy0, gy1, 4, 8)
    ph = (gy1 - gy0) / 8.0
    s0, s1 = gy0 + 4 * ph - 1.5, gy0 + 6 * ph + 1.5               # the hopper
    for a0, a1, b0, b1, axes in ((gx0, gx1, s0, s0 + 3, "y"), (gx0, gx1, s1 - 3, s1, "y"),
                                 (gx0, gx0 + 3, s0, s1, "x"), (gx1 - 3, gx1, s0, s1, "x")):
        _bar(c, a0, a1, b0, b1, h=SASH_H, axes=axes)
    c.mul(gx0, gx1, s0 - 2, s0, 0.88, ao=0.84)                     # under the sash
    # the bottom rail is heavier and holds water
    c.mul(x, x + w, y, y + F + 1, 0.92, ao=0.86)
    c.mul(gx0, gx1, gy1 - 3, gy1, 0.90, ao=0.84)                   # under the head


def paint_screen(c):
    """The entrance bay: the window's frame brought down to the ground, a
    plain steel leaf in it between two solid side panels, a transom at the
    leaf's head and the window's small panes above to the band."""
    x, y, w, h = SCREEN
    F = 5
    _bar(c, x - PAD, x + w + PAD, y - PAD, y + h + PAD, h=FRAME_H)
    lx0, lx1 = x + SCREEN_LEAF[0], x + SCREEN_LEAF[1]
    yt = y + m(Z_LEAF)
    # side panels: steel sheet in a frame, the threshold under the lot
    for a0, a1 in ((x + F, lx0 - 3), (lx1 + 3, x + w - F)):
        c.paint(a0, a1, y + 4, yt, ID_FRAME, 0.90, 0.9, height=0.012)
        c.mul(a0, a1, yt - 3, yt, 0.88, ao=0.84)
    _bar(c, x, x + w, yt, yt + 6, h=FRAME_H, axes="y")            # transom
    # the door frame and the leaf
    _bar(c, lx0 - 3, lx0, y, yt, h=DOOR_FRAME_H, axes="x")
    _bar(c, lx1, lx1 + 3, y, yt, h=DOOR_FRAME_H, axes="x")
    c.paint(lx0, lx1, y, yt, ID_DOOR, 1.0, 0.95, height=0.0)
    c.mul(lx0, lx1, yt - 3, yt, 0.86, ao=0.82)
    c.paint(lx0 + 2, lx1 - 2, y + 2, y + m(0.25), ID_DOOR, 0.86, 0.9, height=0.003)
    hx, hy = lx1 - 8, y + m(1.0)
    c.paint(hx - 1.5, hx + 1.5, hy - 5, hy + 5, ID_HANDLE, 1.0, 0.9, height=0.01)
    c.stroke((hx, hy + 2), (hx - 8, hy + 2), 2.2, ID_HANDLE, 1.0, 0.9, height=0.04)
    c.paint(lx0, lx1, y, y + 2, ID_SEAL, 1.0, 0.8)
    _grid(c, x + F, x + w - F, yt + 6, y + h - F, 4, 5)
    c.mul(x + F, x + w - F, y + h - F - 3, y + h - F, 0.90, ao=0.84)


def paint_bigdoor(c):
    """The machinery door: a pair of side-hung steel leaves in a steel frame,
    each a framed sheet with fine vertical ribs, a mid rail at hand height and
    a row of three small lights near the head; heavy hinges on the outer
    stiles, a lock bar and a drop bolt where the leaves meet."""
    x, y, w, h = BIGDOOR
    F = BIGDOOR_FRAME
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_DOOR, 0.80, 0.84,
            height=DOOR_FRAME_H)
    c.bevel(x - PAD, x + w + PAD, y - PAD, y + h + PAD, DOOR_FRAME_H, 1.0)
    l0, l1, top = x + F, x + w - F, y + h - F
    mid = (l0 + l1) / 2.0
    for a0, a1, hinge in ((l0, mid - 0.5, l0), (mid + 0.5, l1, l1)):
        c.paint(a0, a1, y, top, ID_DOOR, 1.0, 1.0, height=0.0)
        sy, sx, _, X = c.field(a0, a1, y, top)
        r = (X - a0) % 8.0
        c.height[sy, sx] = np.where(r < 1.5, RIB_H, 0.0)
        c.shade[sy, sx] = np.where(r < 1.5, 1.0, np.where(r < 2.5, 0.92, 1.0))
        S = 6
        for b0, b1 in ((y, y + 10), (y + m(1.5) - 4, y + m(1.5) + 4),
                       (top - m(0.75) - 4, top - m(0.75) + 4), (top - S, top)):
            _bar(c, a0, a1, b0, b1, ID_DOOR, DOOR_FRAME_H, 0.86, 1.0, "y")
            c.mul(a0, a1, b0 - 2, b0, 0.88, ao=0.84)
        _bar(c, a0, a0 + S, y, top, ID_DOOR, DOOR_FRAME_H, 0.86, 1.0, "x")
        _bar(c, a1 - S, a1, y, top, ID_DOOR, DOOR_FRAME_H, 0.86, 1.0, "x")
        # three small lights between the upper rail and the head
        gy0, gy1 = top - m(0.75) + 4, top - S
        pw = (a1 - a0 - 2 * S) / 3.0
        for i in range(3):
            p0 = a0 + S + i * pw + (2 if i else 0)
            p1 = a0 + S + (i + 1) * pw - (2 if i < 2 else 0)
            c.paint(p0, p1, gy0, gy1, ID_GLASS, 1.0, 0.9, height=0.0)
            c.mul(p0, p1, gy1 - 2, gy1, 0.92, ao=0.86)
        # hinges, three to a leaf, on the outer stile
        for zz in (0.35, 1.9, 3.2):
            hy = y + m(zz)
            hx0 = hinge - 3 if hinge == l0 else hinge - 14
            c.paint(hx0, hx0 + 17, hy - 3, hy + 3, ID_DOOR, 0.78, 0.86, height=0.045)
            c.mul(hx0, hx0 + 17, hy - 5, hy - 3, 0.82, ao=0.8)
    # the meeting stiles, the lock bar and the drop bolt
    c.paint(mid - 0.5, mid + 0.5, y, top, ID_DARK, 1.0, 0.5, height=-0.004)
    c.paint(mid - 6, mid - 2, y + m(0.9), y + m(1.3), ID_HANDLE, 0.9, 0.85, height=0.04)
    c.paint(mid + 2, mid + 4, y + 4, y + m(0.6), ID_HANDLE, 0.85, 0.85, height=0.03)
    c.paint(l0, l1, y, y + 2, ID_SEAL, 1.0, 0.8)


def paint_slot(c):
    """The rope slot high in the rear gable, closed by a steel louvre in a
    cast concrete surround: blades sloping out and down, dark between."""
    x, y, w, h = SLOT
    F = 5
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CONC, 1.0, 1.0)
    c.bevel(x - PAD, x + w + PAD, y - PAD, y + h + PAD, 0.02, 1.5)
    c.paint(x + F, x + w - F, y + F, y + h - F, ID_DARK, 1.0, 0.5, height=-0.02)
    for yy in np.arange(y + F, y + h - F - 1, 4.0):
        c.paint(x + F, x + w - F, yy, yy + 3, ID_FRAME, 0.92, 0.85)
        sy, sx, Y, _ = c.field(x + F, x + w - F, yy, yy + 3)
        c.height[sy, sx] = 0.03 * (1.0 - (Y - yy) / 3.0)
        c.paint(x + F, x + w - F, yy, yy + 1, ID_FRAME, 0.80, 0.8)
    c.mul(x + F, x + w - F, y + h - F - 3, y + h - F, 0.80, ao=0.7)
    c.paint(x + F, x + w - F, y + F - 1, y + F + 1, ID_CONC, 0.86, 0.9)   # its sill


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
        "sill": (ID_CONC, 0.94, 0.90),
        "conc": (ID_CONC, 0.84, 0.80),
        "barge": (ID_FLASH, 0.94, 0.94),
        "pipe": (ID_PIPE, 1.0, 0.95),
    }
    atlas.paint_patches(c, PATCHES, spec)


# ------------------------------------------------------------------ checks
def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands, or
    run off the sheet, or the layout's numbers disagree."""
    rects = {"screen": SCREEN, "bigdoor": BIGDOOR, "window": WINDOW,
             "window_b": WINDOW_B, "slot": SLOT, "vent": VENT,
             "pipe_top": PIPE_TOP}
    rects.update({"floor_" + k: f.rect for k, f in FLOORS.items()})
    rects.update(PATCHES)
    problems = atlas.region_problems(rects, ATLAS, bands_top=EAVE_Y0 + EAVE_H + PAD)
    for kind, (w, h) in OPENINGS.items():
        rw, rh = region_size_m(kind)
        if abs(rw - w) > 0.02 or abs(rh - h) > 0.02:
            problems.append("%s region is %.3f x %.3f m for a %.3f x %.3f m "
                            "opening" % (kind, rw, rh, w, h))
    if abs(m(Z_WALL_TOP) - BRICK_H) > 1e-6:
        problems.append("the brick band does not reach the wall head")
    if (m(GABLE_SHIFT) / m(COURSE)) % TONE_COURSES:
        problems.append("GABLE_SHIFT is not a whole tone period of courses")
    # what the gable triangles sample: brick only, above the plinth's
    # splash and below the lintel band
    lo = Z_GABLE - GABLE_SHIFT
    hi = Z_WALL_TOP + HX * TAN - GABLE_SHIFT
    if lo < Z_PLINTH + 1.0 or hi > Z_HEAD - 0.1:
        problems.append("the gables sample z %.2f .. %.2f, not clear brick" % (lo, hi))
    if ATLAS % SEAM or ATLAS % 64:
        problems.append("the roof's seam period does not divide the atlas")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    The brick band's V is height from the ground, so splash-back, the
    plinth's soil and salt bloom land the same on every wall. Nothing that
    follows height goes near the band's top: the gable triangles sample the
    rows 3.75 m lower, and would show the seam.
    """
    brick = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    steel = (ID_ROOF, ID_FLASH, ID_GUTTER, ID_PIPE, ID_DOOR, ID_HANDLE)
    w = weathering.Weather(c, clean=(ID_GLASS,), steel=steel)
    w.grime()
    w.fade((ID_FRAME, ID_DOOR, ID_FLASH))
    w.wash(brick)
    w.plinth(0, ATLAS, BRICK_Y0, BRICK_Y0 + m(Z_PLINTH), (ID_PLINTH,))
    w.splash(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + BRICK_H + PAD, brick)
    w.bloom(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(1.4), brick,
            amount=0.10, fade=m(0.7))
    # the lintel band: dust on its top, runs down the brick piers under it
    b0, b1 = BRICK_Y0 + m(Z_HEAD), BRICK_Y0 + m(Z_BAND)
    w.add("D", 0, ATLAS, b1 - 4, b1, lambda Y, X, nz: 0.10 + 0.10 * nz("blotch"),
          (ID_CONC,))
    w.runs(0, ATLAS, b0 - m(0.5), b0, brick, 0.10, fall=12.0)
    w.add("D", 0, ATLAS, b0, b1, lambda Y, X, nz: 0.05 * nz("big"), (ID_CONC,))
    # the roof: runs down the slope, dirt toward the gutter, chalking up top;
    # debris held above the snow guard and rust at its brackets
    roof = (ID_ROOF,)
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, SLOPE_LEN, roof)
    g = ROOF_Y0 + round(SNOW_GUARD * ROOF_RPM)
    w.add("D", 0, ATLAS, g + 4.5, g + 14.0, lambda Y, X, nz: 0.22 * nz("blotch")
          * (1.0 - (Y - g - 4.5) / 9.5), roof)
    w.add("D", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.06 + 0.045 * nz("blotch"),
          (ID_GUTTER,))
    w.add("R", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.15 * (
        ((X % (2.0 * SEAM)) >= 2.0) & ((X % (2.0 * SEAM)) < 5.0)), (ID_GUTTER,))
    # the gutter and the fascia: dirty belly, runs from the top edges
    top = EAVE_Y0 + EAVE_H
    w.add("D", 0, ATLAS, top - GUTTER_PX, top - GUTTER_PX + 4,
          lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"), (ID_GUTTER,))
    w.runs(0, ATLAS, top - GUTTER_PX, top, (ID_GUTTER,), 0.08, fall=4.0, lo=0.4, hi=1.6)
    w.runs(0, ATLAS, EAVE_Y0 - PAD, top - GUTTER_PX, (ID_FLASH,), 0.12,
           fall=6.0, noise="short")
    # the windows: dirt standing on the bottom rail and the hopper's sill
    for x, y, rw, rh in (WINDOW, WINDOW_B):
        w.add("D", x, x + rw, y - PAD, y + 7, lambda Y, X, nz: 0.12
              + 0.12 * atlas.smoothstep(0.2, 1.4, nz("short")), (ID_FRAME,))
    # the doors: kicked-up dirt at the foot, grime round the handles
    x, y, rw, rh = SCREEN
    hx = x + SCREEN_LEAF[1] - 8
    w.door(x + SCREEN_LEAF[0], x + SCREEN_LEAF[1], y, y + m(Z_LEAF), (ID_DOOR,),
           handle=(hx, y + m(1.0)))
    w.add("D", x, x + rw, y, y + m(0.4), lambda Y, X, nz: 0.12 * nz("blotch"),
          (ID_FRAME,))
    x, y, rw, rh = BIGDOOR
    w.door(x + BIGDOOR_FRAME, x + rw - BIGDOOR_FRAME, y, y + rh, (ID_DOOR,),
           handle=(x + rw / 2.0, y + m(1.1)))
    w.add("R", x, x + rw, y, y + 12, lambda Y, X, nz: 0.12 * nz("blotch"), (ID_DOOR,))
    # the louvre: soot and dirt from the hall's air on its blades
    x, y, rw, rh = SLOT
    w.runs(x, x + rw, y, y + rh, (ID_FRAME, ID_CONC), 0.16, fall=rh / 2.0)
    # the entrance's floor slab: trodden-in dirt
    for f in FLOORS.values():
        DF.weather(w, f, ID_FLOOR, bleed=PAD)
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
    c.check_bands(BAND_IDS)
    paint_window(c, WINDOW)
    paint_window(c, WINDOW_B)
    paint_screen(c)
    paint_bigdoor(c)
    paint_slot(c)
    paint_vent(c)
    for f in FLOORS.values():
        DF.paint(c, f, ID_FLOOR, bleed=PAD)
    paint_patches(c)

    # Tone wear, grain and pores. Every field is periodic, so the bands wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH))
    streak = atlas.noise(c, 7, 0.8, 40.0)
    c.shade[walls] *= 1.0 + 0.03 * streak[walls]
    sheet = np.isin(c.mid, (ID_FLASH, ID_DOOR, ID_FRAME))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    c.shade[sheet] *= 1.0 + 0.016 * grain[sheet]
    roof = c.mid == ID_ROOF
    runs = atlas.noise(c, 6, 0.6, 20.0)
    c.shade[roof] *= 1.0 + 0.025 * runs[roof]
    can = atlas.noise(c, 8, 10.0, 30.0)                  # oil-canning in the pans
    c.shade[roof] *= 1.0 + 0.02 * can[roof]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_CONC, ID_MORTAR))
    pores = atlas.noise(c, 9, 0.8)
    c.shade[mineral] *= 1.0 + 0.03 * pores[mineral]
    c.height[mineral] += 0.0006 * pores[mineral]
    DF.grain(c, ID_FLOOR, pores)
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
    t[ID_FLASH] = np.minimum(np.array(pal["roof"], np.float32) * 1.15 + 6, 255)
    t[ID_DOOR] = pal["door"]
    return t


def export(out_dir, ss=atlas.SS):
    """Candidate glazing in the emission map is neutral grey, each window the
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
