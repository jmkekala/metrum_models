# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
voimalaitos_brick_hall.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
plan, heights, the walls, their concrete columns and openings, band rows and
region rectangles -- so a change here cannot leave the UVs pointing at the
wrong artwork.

The atlas is a trim sheet. Four bands run the full width and tile in U:

    y    0 ..  336   BRICK   z 0 .. 5.25 m: the cast concrete plinth and
                             stretcher-bond facing brick. Walls above 5.25 m
                             sample its rows 1.25 .. 5.25 m in 4 m slabs
                             (SLAB): the bond, the tones and every noise
                             repeat every 256 rows, so the slab lines vanish.
    y  344 ..  376   COLUMN  0.5 m of board-formed concrete across V, U along
                             its length: the frame's columns (U up the
                             column), and the openings' concrete reveals and
                             heads (V across the depth from the wall face).
    y  384 ..  440   FASCIA  the 0.875 m concrete roof edge beam with its
                             galvanised coping flashing.
    y  448 ..  460   PIPE    galvanised steel, round-shaded across V: the
                             downpipes and the roof safety kit (PIPE_STRIP).
    y  468 .. 1020   unique  the tall steel window, the doors, the coal hatch,
                             the flue's blanking plate, the cable bushings,
                             the roof monitor's louvres, the roof deck (8 px/m),
                             the LOD3 elevations (6 px/m) and flat patches.

The tall window is painted once, four 1.5 m periods tall, with heavy
transoms on the period lines and mullions on the column lines. build.py
assembles every window of the building from its sections: the bottom
period, alternating middle periods and the top one, and in width the
outer columns and the middle ones (window_sections()).

Rasterising is scripts/atlas.py's; dirt, algae, rust and faded paint are
scripts/weathering.py's fields, placed by weather() below.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "voimalaitos_brick_hall"
ATLAS = 1024
PPM = 64.0
LPPM = 6.0              # the LOD3 elevations
DPPM = 8.0              # the roof deck
PAD = 2                 # rows each band paints beyond its own edge

# ------------------------------------------------------------------ plan
# Blender build frame, front toward -Y. The boiler house is the west block,
# a little deeper than the turbine hall so its corners stand proud of the
# hall's front and rear walls; the turbine hall abuts its east face.
BH = (-16.0, -2.0, -8.5, 8.5)          # x0, x1, y0, y1: 14 x 17 m
TH = (-2.0, 16.0, -8.0, 8.0)           # 18 x 16 m
COL = 0.5                              # concrete column width on the face

# ------------------------------------------------------------ vertical layout
# Metres above ground; every height is a whole or half texel at 64 px/m.
Z_PLINTH = 0.625        # 40 px; cast concrete base under every wall
FASCIA = 0.875          # the roof edge beam, soffit to coping top
O = 0.25                # the roof slab oversails the walls by this much
PIN = 0.25              # the parapet's inner face, inside the wall line
DECK_DOWN = 0.625       # the deck, below the coping top
WALL_IN = 0.125         # the walls run this far up into the roof slab

Z_BS = 18.625           # boiler house soffit
Z_BC = Z_BS + FASCIA    # 19.5, its coping top
Z_BD = Z_BC - DECK_DOWN  # 18.875, its deck
Z_BWT = Z_BS + WALL_IN  # 18.75, its wall tops, inside the slab
Z_TS = 10.75            # turbine hall soffit
Z_TC = Z_TS + FASCIA    # 11.625
Z_TD = Z_TC - DECK_DOWN  # 11.0
Z_TWT = Z_TS + WALL_IN  # 10.875
BURY = 0.5              # the turbine hall's roof runs this far into the
                        # boiler house, which hides its open end

# The brick band holds z 0 .. BAND_TOP. Above that the walls are cut at
# CUTS into 4 m slabs, slab i sampling the band SLAB * i lower.
BAND_TOP = 5.25
SLAB = 4.0
CUTS = (5.25, 9.25, 13.25, 17.25, 21.25)

# ----------------------------------------------------------------- windows
# One steel window design: frame FR, columns CW wide, periods PER tall, each
# period three pane rows; heavy transoms on the period lines, mullions on the
# column lines. A window is (cols, periods).
FR = 0.125              # 8 px
CW = 0.5625             # 36 px
PER = 1.5               # 96 px
MUL = 0.046875          # 3 px
TRAN = 0.09375          # 6 px
BAR = 0.03125           # 2 px
REGION_PERIODS = 4      # bottom, middle A (hopper), middle B, top
REGION_COLS = 4


def win_size(cols, periods):
    return (2 * FR + cols * CW, 2 * FR + periods * PER)


# Other openings: (width, height) of the hole in the wall, metres.
SIZES = {
    "entrance": (2.0, 3.0),
    "bigdoor": (3.5, 4.0),
    "service": (1.1875, 2.375),
    "hatch": (2.5, 2.0),
    "bushing": (2.5, 1.25),     # flush: painted on the wall at every tier
}
REVEAL = {"win": 0.25, "entrance": 0.25, "bigdoor": 0.3, "service": 0.25,
          "hatch": 0.2, "bushing": 0.0}
DOOR_FRAME = 0.09375    # 6 px of steel frame round every door
LEAF_TOP = {"entrance": 2.3, "service": 2.1}

# ------------------------------------------------------------------ walls
# name: (p0, p1, z foot, z top). Walked counter-clockwise from above, so the
# outward face is on the right. The two returns are the boiler house's
# corner columns where they stand proud of the turbine hall; "step" is the
# boiler house's east face above the turbine hall's roof.
WALLS = {
    "bh_front": ((-16.0, -8.5), (-2.0, -8.5), 0.0, Z_BWT),
    "bh_ret_front": ((-2.0, -8.5), (-2.0, -8.0), 0.0, Z_BWT),
    "th_front": ((-2.0, -8.0), (16.0, -8.0), 0.0, Z_TWT),
    "th_east": ((16.0, -8.0), (16.0, 8.0), 0.0, Z_TWT),
    "th_rear": ((16.0, 8.0), (-2.0, 8.0), 0.0, Z_TWT),
    "bh_ret_rear": ((-2.0, 8.0), (-2.0, 8.5), 0.0, Z_BWT),
    "bh_rear": ((-2.0, 8.5), (-16.0, 8.5), 0.0, Z_BWT),
    "bh_west": ((-16.0, 8.5), (-16.0, -8.5), 0.0, Z_BWT),
    "step": ((-2.0, -8.0), (-2.0, 8.0), Z_TWT, Z_BWT),
}
WALL_ORDER = ("bh_front", "bh_ret_front", "th_front", "th_east", "th_rear",
              "bh_ret_rear", "bh_rear", "bh_west", "step")
# the soffit each wall's roof edge has, for downpipes and ladders
SOFFIT = {"bh_front": Z_BS, "bh_rear": Z_BS, "bh_west": Z_BS, "step": Z_BS,
          "th_front": Z_TS, "th_east": Z_TS, "th_rear": Z_TS}

# Concrete columns: plan coordinate of each column's centre along its wall.
COLUMNS = {
    "bh_front": (-15.75, -11.25, -6.75, -2.25),
    "bh_ret_front": (-8.25,),
    "th_front": (2.25, 6.75, 11.25, 15.75),
    "th_east": (-7.75, -2.5, 2.5, 7.75),
    "th_rear": (15.75, 11.25, 6.75, 2.25),
    "bh_ret_rear": (8.25,),
    "bh_rear": (-2.25, -6.75, -11.25, -15.75),
    "bh_west": (8.25, 2.75, -2.75, -8.25),
    "step": (-2.75, 2.75),
}

# Openings: (kind, plan centre along the wall, z of its foot, (cols,
# periods) for a window). The boiler house's three front bays carry the
# full-height hall windows over a lower window or the entrance; the turbine
# hall's front its tall windows and, in the east bay, the machinery door.
ITEMS = {
    "bh_front": [("win", -13.5, 4.75, (4, 8)), ("win", -9.0, 4.75, (4, 8)),
                 ("win", -4.5, 4.75, (4, 8)), ("win", -13.5, 0.875, (4, 2)),
                 ("win", -4.5, 0.875, (4, 2)), ("entrance", -9.0, 0.0, None)],
    "bh_ret_front": [],
    "th_front": [("win", 0.0, 1.75, (4, 5)), ("win", 4.5, 1.75, (4, 5)),
                 ("win", 9.0, 1.75, (4, 5)), ("bigdoor", 13.5, 0.0, None),
                 ("win", 13.5, 4.75, (4, 3))],
    "th_east": [("win", -5.125, 5.5, (4, 2)), ("win", 5.125, 5.5, (4, 2)),
                ("bushing", 0.0, 6.25, None)],
    "th_rear": [("win", 13.5, 4.75, (4, 3)), ("win", 9.0, 4.75, (4, 3)),
                ("win", 4.5, 4.75, (4, 3)), ("win", 0.0, 4.75, (4, 3)),
                ("service", 0.0, 0.0, None)],
    "bh_ret_rear": [],
    "bh_rear": [("win", -4.5, 9.75, (4, 3)), ("win", -13.5, 9.75, (4, 3)),
                ("win", -9.0, 5.5, (4, 3)), ("win", -4.5, 1.0, (2, 2)),
                ("win", -13.5, 1.0, (2, 2))],
    "bh_west": [("win", 5.5, 6.0, (4, 3)), ("win", -5.5, 6.0, (4, 3)),
                ("hatch", 0.0, 13.0, None)],
    "step": [("win", -5.5, 13.5, (4, 2)), ("win", 0.0, 13.5, (4, 2))],
}

# Things outside the walls that build.py makes as solids of their own:
# the entrance canopy, the flue stub on the boiler house's rear wall toward
# the chimney, the boiler house's roof monitor and the turbine hall's two
# roof ventilators.
CANOPY = (-10.6, -7.4, 1.25, 3.25, 0.25)        # x0, x1, projection, z, thickness
FLUE = (-10.0, -8.0, 1.0, 12.75, 2.0)           # x0, x1, projection, z, height
MONITOR = (-11.0, -7.0, -4.0, 4.0)              # plan of the roof monitor
MON_H = 1.75                                     # its height above the deck
MOD = 2.0                                        # its louvre modules
VENTS = [(5.0, 2.5), (11.0, -2.0)]               # plan centres on the hall roof
VENT_W, VENT_H = 0.8, 1.2


def wall_len(name):
    (x0, y0), (x1, y1) = WALLS[name][:2]
    return abs(x1 - x0) + abs(y1 - y0)


def wall_s(name, plan):
    """s along *name* of a plan coordinate (x for walls along x)."""
    (x0, y0), (x1, y1) = WALLS[name][:2]
    if abs(y1 - y0) < 1e-9:
        return (plan - x0) * (1.0 if x1 > x0 else -1.0)
    return (plan - y0) * (1.0 if y1 > y0 else -1.0)


def item_size(item):
    kind, _c, _z, wp = item
    return win_size(*wp) if kind == "win" else SIZES[kind]


def item_rect(name, item):
    """(s0, s1, z0, z1) of an opening on its wall."""
    w, h = item_size(item)
    s = wall_s(name, item[1])
    return (s - w / 2.0, s + w / 2.0, item[2], item[2] + h)


def column_rects(name):
    zb, zt = WALLS[name][2:4]
    return [(wall_s(name, c) - COL / 2.0, wall_s(name, c) + COL / 2.0,
             max(zb, Z_PLINTH), zt) for c in COLUMNS[name]]


def slab_of(z):
    """Index of the brick slab a height lies in, from the cell's foot."""
    for i, c in enumerate(CUTS):
        if z < c - 1e-9:
            return i
    return len(CUTS)


def window_sections(cols, periods):
    """The window's sections in width and height: lists of (a0, a1, r0),
    metres from the window's corner to metres into the region, consecutive
    sections that are consecutive in the region merged. The region's period
    order is bottom (0), A (1), B (2), top (3); a window's middles alternate
    A and B. Its columns likewise: outer left (0), 1, 2, outer right (3)."""
    def seq(n, last):
        return [0] + [1 + (i % 2) for i in range(n - 2)] + [last]

    def runs(order, pitch, n):
        out = []
        for i, r in enumerate(order):
            a0 = 0.0 if i == 0 else FR + i * pitch
            a1 = 2 * FR + n * pitch if i == n - 1 else FR + (i + 1) * pitch
            r0 = 0.0 if r == 0 else FR + r * pitch
            if out and order[i - 1] + 1 == r:
                out[-1] = (out[-1][0], a1, out[-1][2])
            else:
                out.append((a0, a1, r0))
        return out
    return (runs(seq(cols, REGION_COLS - 1), CW, cols),
            runs(seq(periods, REGION_PERIODS - 1), PER, periods))


# ------------------------------------------------------------------- bands
BRICK_Y0, BRICK_H = 0, 336            # z 0 .. BAND_TOP
COL_Y0, COL_H = 344, 32               # 0.5 m across
FASCIA_Y0, FASCIA_H = 384, 56         # 0.875 m
PIPE_Y0, PIPE_H = 448, 12
# The downpipes' and the ladders' sides span the band's middle eight rows
PIPE_STRIP = (PIPE_Y0 + 2, PIPE_Y0 + PIPE_H - 2)
COPING_PX = 8                         # the coping flashing at the fascia's top

COURSE = 16.0 / 3.0     # brick course pitch in px: 0.0833 m
BRICK_L = 16.0          # stretcher: 0.25 m, 64 bricks per atlas width
TONE_COURSES = 48       # tones repeat every 256 rows, SLAB metres
TILE_Y = 4              # every noise repeats every 256 rows likewise

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels. check_regions() asserts they neither overlap nor
# run off the sheet, and that each opening's region matches its size.
UNI_Y = 470
WINDOW = (4, UNI_Y, 160, 400)                   # 2.5 x 6.25 m: four periods
BIGDOOR = (172, UNI_Y, 224, 256)                # 3.5 x 4.0 m
ENTRANCE = (404, UNI_Y, 128, 192)               # 2.0 x 3.0 m
SERVICE = (540, UNI_Y, 76, 152)                 # 1.1875 x 2.375 m
HATCH = (624, UNI_Y, 160, 128)                  # 2.5 x 2.0 m
FLUE_END = (792, UNI_Y, 128, 128)               # 2.0 x 2.0 m
LOUVRE = (624, 606, 128, 112)                   # 2.0 x 1.75 m module
BUSHING = (760, 606, 160, 80)                   # 2.5 x 1.25 m
DECK = (172, 734, 148, 136)                     # 18.5 x 17 m at 8 px/m
REGION = {"entrance": ENTRANCE, "bigdoor": BIGDOOR, "service": SERVICE,
          "hatch": HATCH, "bushing": BUSHING}

# LOD3 elevations at LPPM: which walls each holds, and where along it.
ELEV = {
    "front": (404, 734, 192, 114),
    "rear": (604, 734, 192, 114),
    "west": (804, 734, 102, 114),
    "east": (914, 734, 96, 66),
    "step": (914, 808, 96, 48),
}
ELEV_WALLS = {"front": (("bh_front", 0.0), ("th_front", 14.0)),
              "rear": (("th_rear", 0.0), ("bh_rear", 18.0)),
              "west": (("bh_west", 0.0),),
              "east": (("th_east", 0.0),),
              "step": (("step", 0.0),)}
ELEV_ZB = {"front": 0.0, "rear": 0.0, "west": 0.0, "east": 0.0, "step": Z_TWT}
WALL_ELEV = {w: (e, off) for e, ws in ELEV_WALLS.items() for w, off in ws}

PATCH_NAMES = ("blank", "soffit", "coping", "conc", "parapet_in", "duct",
               "soot", "lid", "felt", "rim")
PATCHES = {n: (4 + 20 * i, 1002, 16, 16) for i, n in enumerate(PATCH_NAMES)}

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_CONC, ID_FRAME, ID_GLASS, ID_DOOR, ID_GALV = 5, 6, 7, 8, 9
ID_HANDLE, ID_DARK, ID_SEAL, ID_SOFFIT, ID_FELT = 10, 11, 12, 13, 14
ID_COPING, ID_DUCT, ID_SOOT, ID_PORC, ID_LOUVRE = 15, 16, 17, 18, 19

# (roughness, metallic). Painted steel stays mostly dielectric -- the paint
# is what the light sees. The coping, downpipes and ladders are galvanised.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.82, 0.0), ID_MORTAR: (0.94, 0.0), ID_CONC: (0.88, 0.0),
    ID_FRAME: (0.44, 0.0), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_DOOR: (0.52, 0.0), ID_GALV: (0.48, 0.60), ID_HANDLE: (0.35, 0.80),
    ID_DARK: (0.96, 0.0), ID_SEAL: (0.90, 0.0), ID_SOFFIT: (0.86, 0.0),
    ID_FELT: (0.92, 0.0), ID_COPING: (0.46, 0.55), ID_DUCT: (0.62, 0.15),
    ID_SOOT: (0.98, 0.0), ID_PORC: (0.22, 0.0), ID_LOUVRE: (0.50, 0.10),
}

# ---------------------------------------------------------------- palettes
# One coherent brick per instance: the brick changes, and the window steel
# and the doors move with it. Window steel is always lighter than the glass
# it holds. The concrete frame, the coping and the roof stay the same.
VARIANTS = {
    "red_brick": {"brick": (142, 68, 50), "brick2": (112, 55, 43),
                  "mortar": (150, 146, 138), "frame": (198, 198, 192),
                  "door": (64, 80, 76)},
    "yellow_brick": {"brick": (186, 164, 120), "brick2": (162, 140, 102),
                     "mortar": (160, 156, 148), "frame": (98, 110, 104),
                     "door": (104, 56, 44)},
    "brown_brick": {"brick": (96, 67, 53), "brick2": (77, 54, 44),
                    "mortar": (126, 120, 112), "frame": (184, 180, 170),
                    "door": (58, 66, 76)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (148, 146, 140), ID_CONC: (166, 164, 156),
    ID_GALV: (134, 137, 137), ID_HANDLE: (150, 150, 148), ID_DARK: (24, 24, 24),
    ID_SEAL: (34, 34, 34), ID_SOFFIT: (160, 158, 152), ID_BLANK: (52, 52, 52),
    ID_FELT: (58, 58, 60), ID_COPING: (128, 131, 131), ID_DUCT: (74, 74, 76),
    ID_SOOT: (20, 19, 18), ID_PORC: (104, 58, 38), ID_LOUVRE: (96, 98, 100),
}

# A stray pixel in a tiling band is not a local blemish: every surface that
# samples the band repeats it.
BAND_IDS = {
    "BRICK": ((0, 338), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH}),
    "COLUMN": ((342, 378), {ID_CONC}),
    "FASCIA": ((382, 442), {ID_CONC, ID_COPING}),
    "PIPE": ((446, 462), {ID_GALV}),
}

# The candidate-glazing mask is the emission map, neutral white.
EMIT = {ID_GLASS: (255, 255, 255)}
# Linear RGB: industrial hall lamps, the value the catalog's works use.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto: only the few
# centimetres the mesh does not model.
BRICK_FACE = 0.006      # brick face proud of the recessed mortar
ARRIS_H = 0.008         # the concrete's arrises at a column's or reveal's edge
FRAME_H = 0.035         # window frames, proud of the glass
TRAN_H = 0.030          # transoms and mullions
BAR_H = 0.020           # glazing bars
SASH_H = 0.045          # the hopper's sash
DOOR_FRAME_H = 0.030    # door frames and stiles
RIB_H = 0.006           # sheet ribs on the machinery door and hatch
COPING_H = 0.030        # the coping's lip
BLADE_H = 0.030         # louvre blades


def m(v):
    """Metres -> pixels at 64 px/m."""
    return v * PPM


# ================================================================== bands
def paint_plinth(c):
    """Cast concrete, the base every wall stands on: a little darker at the
    foot, a drip shadow under the brick's first course."""
    y0, h = BRICK_Y0, m(Z_PLINTH)
    c.paint(0, ATLAS, y0 - PAD, y0 + h, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, y0 - PAD, y0 + h)
    z = (Y - y0) / PPM
    c.shade[sy, sx] *= 0.84 + 0.16 * np.clip(z / 0.25, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.25, 0, 1))
    c.mul(0, ATLAS, y0 + m(0.3), y0 + m(0.3) + 1, 0.94, ao=0.94)   # pour line
    c.lift(0, ATLAS, y0 + m(0.3), y0 + m(0.3) + 1, -0.002)
    c.mul(0, ATLAS, y0 + h - 2, y0 + h, 0.86, ao=0.84)


def paint_brick(c):
    """Stretcher-bond facing brick, 64 bricks per width, courses 1/12 m, two
    tones, mortar recessed and its own id. Bond and tones repeat every 256
    rows (TONE_COURSES), the slab period, from the plinth's top."""
    y0 = BRICK_Y0 + m(Z_PLINTH)
    top = BRICK_Y0 + BRICK_H + PAD
    c.paint(0, ATLAS, y0, top, ID_BRICK, 1.0, 1.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0, top)
    r = np.floor((Y - y0) / COURSE).astype(np.int64)
    off = (r % 2) * BRICK_L * 0.5
    b = np.floor((X - off) / BRICK_L).astype(np.int64) % int(ATLAS / BRICK_L)
    rr = r % TONE_COURSES
    bed = (Y - y0 - r * COURSE) < 1.0
    perp = ((X - off) % BRICK_L) < 1.0
    joint = bed | perp
    tone = 0.90 + 0.20 * atlas.hash_unit(b, rr, 17)
    dark = atlas.hash_unit(atlas.hash_int(b, rr, 29), 7) < 0.17
    c.mid[sy, sx] = np.where(joint, ID_MORTAR, np.where(dark, ID_BRICK2, ID_BRICK))
    c.shade[sy, sx] = np.where(joint, 0.94, tone)
    c.ao[sy, sx] = np.where(joint, 0.80, 1.0)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)
    paint_plinth(c)


def paint_column_band(c):
    """Board-formed concrete, 0.5 m across V: arrises at both edges, the
    plank joints running along U, tie-hole plugs every 0.75 m."""
    y0, y1 = COL_Y0, COL_Y0 + COL_H
    c.paint(0, ATLAS, y0 - PAD, y1 + PAD, ID_CONC, 1.0, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, y1, ARRIS_H, 1.5, axes="y")
    for k in (1, 2, 3):
        yy = y0 + 8.0 * k
        c.mul(0, ATLAS, yy - 0.3, yy + 0.3, 0.94, ao=0.94)
        c.lift(0, ATLAS, yy - 0.3, yy + 0.3, -0.0015)
    for i in range(int(ATLAS / 48)):
        x = i * 48.0 + 24.0
        for yy in (y0 + 8.0, y0 + 24.0):
            c.disc(x, yy, 1.2, ID_CONC, 0.88, 0.9)
    c.mul(0, ATLAS, y0, y0 + 1, 0.96)
    c.mul(0, ATLAS, y1 - 1, y1, 0.96)


def paint_fascia(c):
    """The roof edge beam: cast concrete with a drip groove near its foot
    and formwork joints every 2 m, the galvanised coping flashing over its
    top with a lip whose shadow falls on the concrete."""
    y0, y1 = FASCIA_Y0, FASCIA_Y0 + FASCIA_H
    yc = y1 - COPING_PX
    c.paint(0, ATLAS, y0 - PAD, yc, ID_CONC, 1.0, 1.0, height=0.0)
    c.mul(0, ATLAS, y0 - PAD, y0 + 1, 0.86, ao=0.86)               # soffit arris
    c.mul(0, ATLAS, y0 + 3, y0 + 4, 0.82, ao=0.82)                 # drip groove
    c.lift(0, ATLAS, y0 + 3, y0 + 4, -0.008)
    for i in range(int(ATLAS / 128)):
        x = i * 128.0
        c.mul(x, x + 1, y0, yc, 0.90, ao=0.90)
        c.lift(x, x + 1, y0, yc, -0.003)
    c.paint(0, ATLAS, yc, y1 + PAD, ID_COPING, 1.0, 1.0, height=0.0)
    c.bevel(0, ATLAS, yc, yc + 3, COPING_H, 1.0, axes="y")         # the lip
    c.paint(0, ATLAS, yc + 3, y1 + PAD, ID_COPING, 0.96, 1.0, height=0.0)
    for k, f in enumerate((0.78, 0.86, 0.94)):                     # its shadow
        c.mul(0, ATLAS, yc - 1 - k, yc - k, f, ao=0.84)
    for i in range(int(ATLAS / 128)):                              # its joints
        x = i * 128.0 + 64.0
        c.mul(x, x + 1.5, yc, y1, 0.86)
        c.lift(x, x + 1.5, yc + 3, y1, 0.003)


def paint_pipe_band(c):
    """Galvanised steel, round-shaded across V, a clip every metre."""
    y0, y1 = PIPE_Y0, PIPE_Y0 + PIPE_H
    c.paint(0, ATLAS, y0 - PAD, y1 + PAD, ID_GALV, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y1 + PAD)
    u = np.clip(2.0 * (Y - y0) / (y1 - y0) - 1.0, -1.0, 1.0)
    clip = (X % 64.0) < 2.0
    c.shade[sy, sx] = (0.86 + 0.14 * np.cos(0.5 * np.pi * u)) * np.where(clip, 0.82, 1.0)


# ================================================================ regions
def _bar(c, a0, a1, b0, b1, mid=ID_FRAME, h=FRAME_H, ao=0.88, shade=1.0,
         axes="xy", w=1.0):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, w, axes=axes)


def paint_window(c, x0, y0, ppm, cols, seq, pad=PAD):
    """A steel hall window at *ppm*, corner at pixel (x0, y0): a heavy frame,
    *cols* columns on mullions, one period per entry of *seq* (0 bottom,
    1 middle with the hopper, 2 middle, 3 top) on heavy transoms, three
    pane rows to a period. The region paints seq (0, 1, 2, 3) and four
    columns; the LOD3 elevations paint each window whole."""
    def P(v):
        return v * ppm

    def B(v):
        # a bar never thinner than one sample: at the elevations' 6 px/m a
        # glazing bar is a fifth of a pixel and would vanish, leaving the
        # window darker than the region it stands for
        return max(v * ppm, 1.0 / c.ss)
    n = len(seq)
    W, H = win_size(cols, n)
    k = ppm / PPM
    bw = max(0.25, k)
    _bar(c, x0 - pad, x0 + P(W) + pad, y0 - pad, y0 + P(H) + pad, h=FRAME_H, w=bw)
    ix0, ix1 = x0 + P(FR), x0 + P(W - FR)
    c.paint(ix0, ix1, y0 + P(FR), y0 + P(H - FR), ID_FRAME, 1.0, 0.9, height=BAR_H)
    for j, kind in enumerate(seq):
        b0 = y0 + P(FR + j * PER) + (B(TRAN) / 2.0 if j > 0 else 0.0)
        b1 = y0 + P(FR + (j + 1) * PER) - (B(TRAN) / 2.0 if j < n - 1 else 0.0)
        rh = (b1 - b0) / 3.0
        for i in range(cols):
            a0 = x0 + P(FR + i * CW) + (B(MUL) / 2.0 if i > 0 else 0.0)
            a1 = x0 + P(FR + (i + 1) * CW) - (B(MUL) / 2.0 if i < cols - 1 else 0.0)
            for r in range(3):
                g0 = b0 + r * rh + (B(BAR) / 2.0 if r > 0 else 0.0)
                g1 = b0 + (r + 1) * rh - (B(BAR) / 2.0 if r < 2 else 0.0)
                c.paint(a0, a1, g0, g1, ID_GLASS, 1.0, 0.92, height=0.0)
                c.mul(a0, a1, g1 - 2.0 * k, g1, 0.92, ao=0.86)
        if j > 0:                                       # transom under it
            t = y0 + P(FR + j * PER)
            _bar(c, ix0, ix1, t - B(TRAN) / 2.0, t + B(TRAN) / 2.0, h=TRAN_H,
                 axes="y", w=bw)
            c.mul(ix0, ix1, t - B(TRAN) / 2.0 - 2.0 * k, t - B(TRAN) / 2.0, 0.90, ao=0.84)
        if kind == 1:                                   # the hopper, middle row
            s0, s1 = b0 + rh - 1.5 * k, b0 + 2.0 * rh + 1.5 * k
            sw = 3.0 * k
            for a, bb, cc, d, ax in ((ix0, ix1, s0, s0 + sw, "y"),
                                     (ix0, ix1, s1 - sw, s1, "y"),
                                     (ix0, ix0 + sw, s0, s1, "x"),
                                     (ix1 - sw, ix1, s0, s1, "x")):
                _bar(c, a, bb, cc, d, h=SASH_H, axes=ax, w=bw)
            c.mul(ix0, ix1, s0 - 2.0 * k, s0, 0.88, ao=0.84)
    for i in range(1, cols):                            # mullions over all
        mx = x0 + P(FR + i * CW)
        _bar(c, mx - B(MUL) / 2.0, mx + B(MUL) / 2.0, y0 + P(FR), y0 + P(H - FR),
             h=TRAN_H, axes="x", w=bw)
    c.mul(x0, x0 + P(W), y0, y0 + P(FR), 0.92, ao=0.86)  # bottom rail holds water


def _door_frame(c, x0, y0, ppm, w, h, pad):
    F = DOOR_FRAME * ppm
    c.paint(x0 - pad, x0 + w * ppm + pad, y0 - pad, y0 + h * ppm + pad, ID_FRAME,
            0.92, 0.88, height=DOOR_FRAME_H)
    c.bevel(x0 - pad, x0 + w * ppm + pad, y0 - pad, y0 + h * ppm + pad,
            DOOR_FRAME_H, max(0.25, ppm / PPM))
    return F


def _lights(c, a0, a1, b0, b1, n, k, mid=ID_FRAME):
    """n glass lights across a0..a1 in b0..b1 on 2 px bars."""
    pw = (a1 - a0) / n
    c.paint(a0, a1, b0, b1, mid, 1.0, 0.9, height=BAR_H)
    for i in range(n):
        p0 = a0 + i * pw + (1.0 * k if i else 0.0)
        p1 = a0 + (i + 1) * pw - (1.0 * k if i < n - 1 else 0.0)
        c.paint(p0, p1, b0 + 1.5 * k, b1 - 1.5 * k, ID_GLASS, 1.0, 0.92, height=0.0)
        c.mul(p0, p1, b1 - 3.5 * k, b1 - 1.5 * k, 0.92, ao=0.86)


def paint_entrance(c, x0, y0, ppm, pad=PAD):
    """The main entrance: a pair of framed steel leaves, each with a tall
    light, under a transom and a four-light fanlight."""
    w, h = SIZES["entrance"]
    k = ppm / PPM
    F = _door_frame(c, x0, y0, ppm, w, h, pad)
    top = y0 + LEAF_TOP["entrance"] * ppm
    l0, l1 = x0 + F, x0 + w * ppm - F
    mid = (l0 + l1) / 2.0
    _bar(c, x0, x0 + w * ppm, top, top + F, h=DOOR_FRAME_H, axes="y", w=max(0.25, k))
    _lights(c, l0, l1, top + F, y0 + (h - DOOR_FRAME) * ppm, 4, k)
    for a0, a1, hx in ((l0, mid - 0.5 * k, mid - 6 * k), (mid + 0.5 * k, l1, mid + 6 * k)):
        c.paint(a0, a1, y0, top, ID_DOOR, 1.0, 0.95, height=0.0)
        S = 7 * k
        for b0, b1 in ((y0, y0 + 14 * k), (top - S, top)):
            _bar(c, a0, a1, b0, b1, ID_DOOR, DOOR_FRAME_H, 0.88, 1.0, "y", max(0.25, k))
        _bar(c, a0, a0 + S, y0, top, ID_DOOR, DOOR_FRAME_H, 0.88, 1.0, "x", max(0.25, k))
        _bar(c, a1 - S, a1, y0, top, ID_DOOR, DOOR_FRAME_H, 0.88, 1.0, "x", max(0.25, k))
        g0, g1 = a0 + 12 * k, a1 - 12 * k
        _bar(c, g0 - 2 * k, g1 + 2 * k, y0 + 0.95 * ppm - 2 * k, y0 + 2.05 * ppm + 2 * k,
             ID_DOOR, DOOR_FRAME_H, 0.9, 0.95, "xy", max(0.25, k))
        c.paint(g0, g1, y0 + 0.95 * ppm, y0 + 2.05 * ppm, ID_GLASS, 1.0, 0.92, height=0.0)
        c.mul(g0, g1, y0 + 2.05 * ppm - 2 * k, y0 + 2.05 * ppm, 0.9, ao=0.85)
        hy = y0 + 1.05 * ppm
        c.paint(hx - 1.5 * k, hx + 1.5 * k, hy - 6 * k, hy + 6 * k, ID_HANDLE, 1.0, 0.9,
                height=0.04)
    c.paint(mid - 0.5 * k, mid + 0.5 * k, y0, top, ID_DARK, 1.0, 0.5, height=-0.004)
    c.paint(l0, l1, y0, y0 + 2 * k, ID_SEAL, 1.0, 0.8)


def paint_bigdoor(c, x0, y0, ppm, pad=PAD):
    """The machinery door: four folding steel leaves with fine vertical ribs,
    a mid rail, a row of lights near the head and a wicket door in the
    second leaf; dark joints where the leaves fold."""
    w, h = SIZES["bigdoor"]
    k = ppm / PPM
    F = _door_frame(c, x0, y0, ppm, w, h, pad)
    l0, l1, top = x0 + F, x0 + w * ppm - F, y0 + (h - DOOR_FRAME) * ppm
    lw = (l1 - l0) / 4.0
    bw = max(0.25, k)
    for i in range(4):
        a0, a1 = l0 + i * lw + 0.5 * k, l0 + (i + 1) * lw - 0.5 * k
        c.paint(a0, a1, y0, top, ID_DOOR, 1.0, 1.0, height=0.0)
        sy, sx, _, X = c.field(a0, a1, y0, top)
        r = (X - a0) % (8.0 * k)
        c.height[sy, sx] = np.where(r < 1.5 * k, RIB_H, 0.0)
        c.shade[sy, sx] = np.where(r < 1.5 * k, 1.0, np.where(r < 2.5 * k, 0.93, 1.0))
        S = 6 * k
        for b0, b1 in ((y0, y0 + 12 * k), (y0 + 1.0 * ppm - 4 * k, y0 + 1.0 * ppm + 4 * k),
                       (top - 0.7 * ppm - 4 * k, top - 0.7 * ppm + 4 * k), (top - S, top)):
            _bar(c, a0, a1, b0, b1, ID_DOOR, DOOR_FRAME_H, 0.86, 1.0, "y", bw)
            c.mul(a0, a1, b0 - 2 * k, b0, 0.88, ao=0.84)
        _bar(c, a0, a0 + S, y0, top, ID_DOOR, DOOR_FRAME_H, 0.86, 1.0, "x", bw)
        _bar(c, a1 - S, a1, y0, top, ID_DOOR, DOOR_FRAME_H, 0.86, 1.0, "x", bw)
        _lights(c, a0 + S, a1 - S, top - 0.7 * ppm + 4 * k, top - S, 2, k, ID_DOOR)
        if i:
            c.paint(a0 - 1.0 * k, a0, y0, top, ID_DARK, 1.0, 0.5, height=-0.004)
    # the wicket door in the second leaf, and the handles
    a0 = l0 + lw + 10 * k
    a1 = a0 + 0.8 * ppm
    for b0, b1, ax in ((y0 + 12 * k, y0 + 2.05 * ppm, "x"),):
        c.paint(a0, a0 + 1.0 * k, b0, b1, ID_DARK, 1.0, 0.6, height=-0.003)
        c.paint(a1 - 1.0 * k, a1, b0, b1, ID_DARK, 1.0, 0.6, height=-0.003)
    c.paint(a0, a1, y0 + 2.05 * ppm - 1.0 * k, y0 + 2.05 * ppm, ID_DARK, 1.0, 0.6,
            height=-0.003)
    c.paint(a1 - 8 * k, a1 - 5 * k, y0 + 1.0 * ppm, y0 + 1.2 * ppm, ID_HANDLE, 0.9,
            0.85, height=0.04)
    mid = l0 + 2 * lw
    c.paint(mid - 6 * k, mid - 2 * k, y0 + 0.9 * ppm, y0 + 1.4 * ppm, ID_HANDLE,
            0.9, 0.85, height=0.04)
    c.paint(l0, l1, y0, y0 + 2 * k, ID_SEAL, 1.0, 0.8)


def paint_service(c, x0, y0, ppm, pad=PAD):
    """The back door: a plain steel leaf under a louvred vent panel."""
    w, h = SIZES["service"]
    k = ppm / PPM
    F = _door_frame(c, x0, y0, ppm, w, h, pad)
    l0, l1 = x0 + F, x0 + w * ppm - F
    top = y0 + LEAF_TOP["service"] * ppm
    c.paint(l0, l1, y0, top, ID_DOOR, 1.0, 0.95, height=0.0)
    c.paint(l0 + 3 * k, l1 - 3 * k, y0 + 3 * k, top - 3 * k, ID_DOOR, 0.97, 0.95,
            height=0.004)
    c.mul(l0, l1, top - 3 * k, top, 0.86, ao=0.82)
    _bar(c, x0, x0 + w * ppm, top, top + F, h=DOOR_FRAME_H, axes="y", w=max(0.25, k))
    v0, v1 = top + F, y0 + (h - DOOR_FRAME) * ppm
    c.paint(l0, l1, v0, v1, ID_DARK, 1.0, 0.5, height=-0.01)
    yy = v0
    while yy + 3 * k <= v1:
        c.paint(l0, l1, yy, yy + 2.5 * k, ID_DOOR, 0.92, 0.85, height=0.02)
        yy += 3.5 * k
    hx, hy = l1 - 8 * k, y0 + 1.05 * ppm
    c.paint(hx - 1.5 * k, hx + 1.5 * k, hy - 5 * k, hy + 5 * k, ID_HANDLE, 1.0, 0.9,
            height=0.01)
    c.stroke((hx, hy + 2 * k), (hx - 8 * k, hy + 2 * k), 2.2 * k, ID_HANDLE, 1.0, 0.9,
             height=0.04)
    c.paint(l0, l1, y0, y0 + 2 * k, ID_SEAL, 1.0, 0.8)


def paint_hatch(c, x0, y0, ppm, pad=PAD):
    """The coal intake: a pair of heavy steel hatches, closed, in an angle
    frame with bolted hinges and a cross-brace each, coal dust settled on
    every ledge."""
    w, h = SIZES["hatch"]
    k = ppm / PPM
    bw = max(0.25, k)
    F = 8 * k
    c.paint(x0 - pad, x0 + w * ppm + pad, y0 - pad, y0 + h * ppm + pad, ID_DUCT,
            0.9, 0.86, height=DOOR_FRAME_H)
    c.bevel(x0 - pad, x0 + w * ppm + pad, y0 - pad, y0 + h * ppm + pad, DOOR_FRAME_H, bw)
    l0, l1, b0, b1 = x0 + F, x0 + w * ppm - F, y0 + F, y0 + h * ppm - F
    mid = (l0 + l1) / 2.0
    for a0, a1 in ((l0, mid - 0.5 * k), (mid + 0.5 * k, l1)):
        c.paint(a0, a1, b0, b1, ID_DOOR, 0.82, 0.95, height=0.0)
        sy, sx, Y, _ = c.field(a0, a1, b0, b1)
        r = (Y - b0) % (10.0 * k)
        c.height[sy, sx] = np.where(r < 1.5 * k, RIB_H, 0.0)
        _bar(c, a0, a1, b0, b0 + 6 * k, ID_DOOR, DOOR_FRAME_H, 0.86, 0.8, "y", bw)
        _bar(c, a0, a1, b1 - 6 * k, b1, ID_DOOR, DOOR_FRAME_H, 0.86, 0.8, "y", bw)
        _bar(c, a0, a0 + 6 * k, b0, b1, ID_DOOR, DOOR_FRAME_H, 0.86, 0.8, "x", bw)
        _bar(c, a1 - 6 * k, a1, b0, b1, ID_DOOR, DOOR_FRAME_H, 0.86, 0.8, "x", bw)
        c.stroke((a0 + 6 * k, b0 + 6 * k), (a1 - 6 * k, b1 - 6 * k), 5 * k, ID_DOOR,
                 0.8, 0.86, height=DOOR_FRAME_H)
        for yy in (b0 + 0.35 * ppm, b1 - 0.35 * ppm):
            hx = a0 if a0 == l0 else a1 - 18 * k
            c.paint(hx, hx + 18 * k, yy - 3.5 * k, yy + 3.5 * k, ID_DUCT, 0.8, 0.86,
                    height=0.045)
    c.paint(mid - 0.5 * k, mid + 0.5 * k, b0, b1, ID_DARK, 1.0, 0.5, height=-0.004)
    c.paint(mid - 3 * k, mid + 3 * k, y0 + 0.9 * ppm, y0 + 1.1 * ppm, ID_HANDLE, 0.8,
            0.85, height=0.04)


def paint_flue_end(c, x0, y0, ppm, pad=PAD):
    """The flue stub's end: a concrete casing round a bolted steel flange
    whose blanking plate closes the duct, sooted where the flue gas left."""
    w, h = 2.0, 2.0
    k = ppm / PPM
    c.paint(x0 - pad, x0 + w * ppm + pad, y0 - pad, y0 + h * ppm + pad, ID_CONC,
            1.0, 1.0, height=0.0)
    c.bevel(x0 - pad, x0 + w * ppm + pad, y0 - pad, y0 + h * ppm + pad, ARRIS_H,
            1.5 * k)
    cx, cy = x0 + w * ppm / 2.0, y0 + h * ppm / 2.0
    c.disc(cx, cy, 0.86 * ppm, ID_DARK, 0.7, 0.6, height=-0.01)
    c.disc(cx, cy, 0.80 * ppm, ID_DUCT, 1.0, 0.9, height=0.03)
    c.disc(cx, cy, 0.66 * ppm, ID_DUCT, 0.86, 0.9, height=0.0)
    c.disc(cx, cy, 0.66 * ppm, ID_DUCT, 0.80, 0.86, inner=0.64 * ppm, height=0.015)
    for i in range(16):
        a = 2.0 * np.pi * (i + 0.5) / 16.0
        bx, by = cx + 0.73 * ppm * np.cos(a), cy + 0.73 * ppm * np.sin(a)
        c.disc(bx, by, 2.2 * k, ID_HANDLE, 0.8, 0.85, height=0.045)
    c.stroke((cx - 0.5 * ppm, cy), (cx + 0.5 * ppm, cy), 6 * k, ID_DUCT, 0.9, 0.9,
             height=0.02)
    c.stroke((cx, cy - 0.5 * ppm), (cx, cy + 0.5 * ppm), 6 * k, ID_DUCT, 0.9, 0.9,
             height=0.02)


def paint_louvre(c, x0, y0, ppm=PPM, pad=PAD):
    """A 2 m module of the roof monitor's side: a sheet upstand, a louvre of
    sloping blades in a steel frame, the flashing at the top; cover strips at
    both ends where modules meet."""
    k = ppm / PPM
    w = MOD * ppm
    c.paint(x0 - pad, x0 + w + pad, y0 - pad, y0 + 0.25 * ppm, ID_DUCT, 1.0, 1.0,
            height=0.0)
    c.mul(x0 - pad, x0 + w + pad, y0 - pad, y0 + 3 * k, 0.86, ao=0.86)
    b0, b1 = y0 + 0.25 * ppm, y0 + 1.5 * ppm
    c.paint(x0 - pad, x0 + w + pad, b0, b1, ID_DARK, 1.0, 0.45, height=-0.02)
    yy = b0 + 2 * k
    while yy + 4 * k <= b1 - 2 * k:
        c.paint(x0 - pad, x0 + w + pad, yy, yy + 4 * k, ID_LOUVRE, 0.96, 0.85)
        sy, sx, Y, _ = c.field(x0 - pad, x0 + w + pad, yy, yy + 4 * k)
        c.height[sy, sx] = BLADE_H * (1.0 - (Y - yy) / (4 * k))
        c.mul(x0 - pad, x0 + w + pad, yy, yy + 1 * k, 0.80, ao=0.8)
        yy += 5 * k
    _bar(c, x0 - pad, x0 + w + pad, b0 - 2 * k, b0 + 2 * k, ID_LOUVRE, DOOR_FRAME_H,
         0.86, 1.0, "y")
    _bar(c, x0 - pad, x0 + w + pad, b1 - 2 * k, b1 + 2 * k, ID_LOUVRE, DOOR_FRAME_H,
         0.86, 1.0, "y")
    c.paint(x0 - pad, x0 + w + pad, b1 + 2 * k, y0 + 1.75 * ppm + pad, ID_COPING,
            1.0, 1.0, height=0.0)
    c.mul(x0 - pad, x0 + w + pad, b1 + 2 * k, b1 + 4 * k, 0.86, ao=0.86)
    for a in (x0 - pad, x0 + w - 3 * k):
        _bar(c, a, a + 3 * k + pad, y0 - pad, y0 + 1.75 * ppm + pad, ID_LOUVRE,
             DOOR_FRAME_H, 0.86, 0.96, "x")


def paint_bushing(c, x0, y0, ppm, pad=PAD):
    """The cable outlet toward the transformer yard, flush on the wall: a
    cast concrete panel in a steel frame through which three porcelain
    bushings stand, cable glands under them, a hazard plate beside."""
    w, h = SIZES["bushing"]
    k = ppm / PPM
    bw = max(0.25, k)
    c.paint(x0 - pad, x0 + w * ppm + pad, y0 - pad, y0 + h * ppm + pad, ID_DUCT,
            0.9, 0.9, height=DOOR_FRAME_H)
    c.bevel(x0 - pad, x0 + w * ppm + pad, y0 - pad, y0 + h * ppm + pad, DOOR_FRAME_H, bw)
    F = 6 * k
    c.paint(x0 + F, x0 + w * ppm - F, y0 + F, y0 + h * ppm - F, ID_CONC, 0.94, 0.95,
            height=0.0)
    for i in range(3):
        bx = x0 + (0.55 + 0.55 * i) * ppm
        c.paint(bx - 0.14 * ppm, bx + 0.14 * ppm, y0 + 0.30 * ppm, y0 + 0.40 * ppm,
                ID_DUCT, 0.9, 0.9, height=0.03)
        yy = y0 + 0.40 * ppm
        n = 0
        while yy < y0 + 1.02 * ppm:
            r = (0.10 if n % 2 == 0 else 0.07) * ppm
            c.rounded_rect(bx - r, yy, 2 * r, 0.05 * ppm, 0.02 * ppm, ID_PORC,
                           1.0 if n % 2 == 0 else 0.86, 0.9, height=0.04)
            yy += 0.06 * ppm
            n += 1
        c.paint(bx - 0.03 * ppm, bx + 0.03 * ppm, yy, yy + 0.08 * ppm, ID_HANDLE,
                0.9, 0.9, height=0.05)
        c.disc(bx, y0 + 0.18 * ppm, 0.07 * ppm, ID_DARK, 0.8, 0.7, height=0.02)
    c.paint(x0 + 2.05 * ppm, x0 + 2.3 * ppm, y0 + 0.6 * ppm, y0 + 0.85 * ppm,
            ID_COPING, 1.0, 0.9, height=0.005)


def paint_deck(c):
    """The roof deck: bitumen felt at 8 px/m, a lap seam every metre and
    patches of a later repair, mineral grain."""
    x, y, w, h = DECK
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_FELT, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    lap = ((X - x) % DPPM) < 0.6
    c.shade[sy, sx] = np.where(lap, 1.08, 1.0)
    c.height[sy, sx] = np.where(lap, 0.004, 0.0)
    for (px, py, pw, ph) in ((30, 40, 22, 14), (96, 90, 16, 24), (60, 112, 30, 10)):
        c.mul(x + px, x + px + pw, y + py, y + py + ph, 0.92)


def paint_brick_lo(c, x0, x1, y0, y1):
    """Brick at LOD3 scale: the bond is far under a pixel, so each sample is
    brick, darker brick or mortar in their proportions; the box filter turns
    that into the wall's average colour with a trace of grain."""
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    if Y.size == 0:
        return
    iy = np.floor(Y * c.ss).astype(np.int64)
    ix = np.floor(X * c.ss).astype(np.int64)
    u = atlas.hash_unit(ix, iy, 41)
    c.mid[sy, sx] = np.where(u < 0.24, ID_MORTAR, np.where(u < 0.37, ID_BRICK2, ID_BRICK))
    c.shade[sy, sx] = np.where(u < 0.24, 0.94, 0.90 + 0.2 * atlas.hash_unit(ix, iy, 43))
    c.ao[sy, sx] = 0.95
    c.height[sy, sx] = 0.0


PAINTERS = {"entrance": paint_entrance, "bigdoor": paint_bigdoor,
            "service": paint_service, "hatch": paint_hatch,
            "bushing": paint_bushing}


def window_seq(periods):
    return [0] + [1 + (i % 2) for i in range(periods - 2)] + [3]


def paint_elevation(c, ename):
    """One LOD3 elevation at LPPM: every wall it holds, with its plinth, its
    columns and its openings, drawn by the same painters as the regions."""
    ex, ey, ew, eh = ELEV[ename]
    zb0 = ELEV_ZB[ename]
    for wname, off in ELEV_WALLS[ename]:
        zb, zt = WALLS[wname][2:4]
        L = wall_len(wname)

        def X(s):
            return ex + (s + off) * LPPM

        def Y(z):
            return ey + (z - zb0) * LPPM
        paint_brick_lo(c, X(0), X(L), Y(zb), Y(zt))
        if zb < Z_PLINTH:
            c.paint(X(0), X(L), Y(zb), Y(Z_PLINTH), ID_PLINTH, 0.92, 0.9, height=0.0)
        for s0, s1, z0, z1 in column_rects(wname):
            c.paint(X(s0), X(s1), Y(z0), Y(z1), ID_CONC, 0.97, 0.95, height=0.0)
        for item in ITEMS[wname]:
            s0, s1, z0, z1 = item_rect(wname, item)
            if item[0] == "win":
                paint_window(c, X(s0), Y(z0), LPPM, item[3][0],
                             window_seq(item[3][1]), pad=0)
            else:
                PAINTERS[item[0]](c, X(s0), Y(z0), LPPM, pad=0)


def paint_patches(c):
    """Flat cells for surfaces a whole face takes one colour from."""
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0),
        "soffit": (ID_SOFFIT, 0.96, 0.84),
        "coping": (ID_COPING, 1.0, 1.0),
        "conc": (ID_CONC, 0.96, 0.95),
        "parapet_in": (ID_FELT, 0.96, 0.86),
        "duct": (ID_DUCT, 1.0, 0.95),
        "soot": (ID_SOOT, 1.0, 0.5),
        "lid": (ID_DUCT, 0.92, 1.0),
        "felt": (ID_FELT, 1.0, 1.0),
        "rim": (ID_DUCT, 0.9, 0.95),
    }
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x - 2, x + w + 2, y - 2, y + h + 2, mid, sh, ao, height=0.0)


# ------------------------------------------------------------------ checks
def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands, or
    run off the sheet, or the layout's numbers disagree."""
    rects = {"window": WINDOW, "bigdoor": BIGDOOR, "entrance": ENTRANCE,
             "service": SERVICE, "hatch": HATCH, "flue_end": FLUE_END,
             "louvre": LOUVRE, "bushing": BUSHING, "deck": DECK}
    rects.update({"elev_" + k: v for k, v in ELEV.items()})
    rects.update(PATCHES)
    bands_top = PIPE_Y0 + PIPE_H + PAD
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
    W, H = win_size(REGION_COLS, REGION_PERIODS)
    if (WINDOW[2], WINDOW[3]) != (m(W), m(H)):
        problems.append("the window region is not %s x %s m" % (W, H))
    for kind, (w, h) in SIZES.items():
        rx, ry, rw, rh = REGION[kind]
        if abs(rw - m(w)) > 1.0 or abs(rh - m(h)) > 1.0:
            problems.append("%s region is %d x %d px for a %.3f x %.3f m opening"
                            % (kind, rw, rh, w, h))
    if (FLUE_END[2], FLUE_END[3]) != (m(2.0), m(2.0)) or FLUE[1] - FLUE[0] != 2.0 \
            or FLUE[4] != 2.0:
        problems.append("the flue's end region is not its 2 x 2 m face")
    if (LOUVRE[2], LOUVRE[3]) != (m(MOD), m(MON_H)):
        problems.append("the louvre region is not one module")
    if abs(m(BAND_TOP) - BRICK_H) > 1e-6:
        problems.append("the brick band does not hold z 0 .. BAND_TOP")
    if abs(TONE_COURSES * COURSE - m(SLAB)) > 1e-6 or (ATLAS / TILE_Y) != m(SLAB):
        problems.append("the bond and the noise do not repeat every SLAB")
    if BAND_TOP - SLAB < Z_PLINTH + 0.6:
        problems.append("the upper slabs would sample the plinth's splash")
    if COL_H != m(COL) or FASCIA_H != m(FASCIA):
        problems.append("the column or fascia band is not its element's size")
    for ename, (ex, ey, ew, eh) in ELEV.items():
        for wname, off in ELEV_WALLS[ename]:
            zb, zt = WALLS[wname][2:4]
            if (off + wall_len(wname)) * LPPM > ew + 1e-6 or \
                    (zt - ELEV_ZB[ename]) * LPPM > eh + 1e-6:
                problems.append("elevation %s cannot hold %s" % (ename, wname))
    for box in (TH, BH):
        dw = (box[1] - box[0] + BURY) * DPPM
        dh = (box[3] - box[2]) * DPPM
        if dw > DECK[2] or dh > DECK[3]:
            problems.append("the deck region cannot hold a %.1f x %.1f m deck"
                            % (dw / DPPM, dh / DPPM))
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    Only the brick band's first 1.25 m is height from the ground for every
    wall; above it each 4 m slab samples the same rows again, so nothing
    that follows height goes there, only noise on the slab period (TILE_Y).
    """
    brick = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    steel = (ID_COPING, ID_GALV, ID_DUCT, ID_DOOR, ID_HANDLE, ID_LOUVRE)
    w = weathering.Weather(c, clean=(ID_GLASS, ID_PORC), steel=steel, tile_y=TILE_Y)
    w.grime()
    w.fade((ID_FRAME, ID_DOOR, ID_LOUVRE))
    w.wash(brick)
    w.plinth(0, ATLAS, BRICK_Y0, BRICK_Y0 + m(Z_PLINTH), (ID_PLINTH,))
    w.splash(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(1.25), brick,
             fall=0.14, speck_fall=0.16)
    w.bloom(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(1.2), brick,
            amount=0.10, fade=m(0.5))
    # the frame's concrete: patchy dirt, a little bloom
    w.add("D", 0, ATLAS, COL_Y0, COL_Y0 + COL_H, lambda Y, X, nz: 0.06 * nz("blotch"),
          (ID_CONC,))
    # the roof edge: runs down the concrete from under the coping's lip,
    # dust on the coping
    yc = FASCIA_Y0 + FASCIA_H - COPING_PX
    w.runs(0, ATLAS, FASCIA_Y0, yc, (ID_CONC,), 0.16, fall=26.0)
    w.add("D", 0, ATLAS, yc, FASCIA_Y0 + FASCIA_H, lambda Y, X, nz: 0.08
          * nz("blotch"), (ID_COPING,))
    # the window: dirt standing on the bottom rail
    x, y, rw, rh = WINDOW
    w.add("D", x, x + rw, y - PAD, y + m(FR) + 1, lambda Y, X, nz: 0.12
          + 0.12 * atlas.smoothstep(0.2, 1.4, nz("short")), (ID_FRAME,))
    # the doors: kicked-up dirt at the foot, grime round the handles
    x, y, rw, rh = ENTRANCE
    w.door(x + m(DOOR_FRAME), x + rw - m(DOOR_FRAME), y, y + m(LEAF_TOP["entrance"]),
           (ID_DOOR,), handle=(x + rw / 2.0, y + m(1.05)))
    x, y, rw, rh = BIGDOOR
    w.door(x + m(DOOR_FRAME), x + rw - m(DOOR_FRAME), y, y + rh, (ID_DOOR,),
           handle=(x + rw / 2.0, y + m(1.1)))
    w.add("R", x, x + rw, y, y + 14, lambda Y, X, nz: 0.12 * nz("blotch"), (ID_DOOR,))
    x, y, rw, rh = SERVICE
    w.door(x + m(DOOR_FRAME), x + rw - m(DOOR_FRAME), y, y + m(LEAF_TOP["service"]),
           (ID_DOOR,), handle=(x + rw - m(DOOR_FRAME) - 8, y + m(1.05)))
    # the coal hatch: coal dust on every ledge, rust at the hinges
    x, y, rw, rh = HATCH
    w.add("D", x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, lambda Y, X, nz: 0.18
          + 0.18 * nz("blotch"), (ID_DOOR, ID_DUCT))
    w.runs(x, x + rw, y, y + rh, (ID_DOOR, ID_DUCT), 0.20, fall=rh / 2.0)
    w.add("R", x, x + rw, y, y + rh, lambda Y, X, nz: 0.12 * atlas.smoothstep(
        0.4, 1.6, nz("runs")), (ID_DOOR, ID_DUCT))
    # the flue's blanking plate: soot and rust
    x, y, rw, rh = FLUE_END
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.22 * nz("blotch"),
          (ID_DUCT, ID_DARK, ID_HANDLE))
    w.add("R", x, x + rw, y, y + rh, lambda Y, X, nz: 0.14 * atlas.smoothstep(
        0.4, 1.6, nz("runs")), (ID_DUCT, ID_HANDLE))
    w.runs(x, x + rw, y, y + rh, (ID_CONC,), 0.18, fall=rh / 3.0)
    # the monitor's louvres and the ventilators: soot from the hall's air
    x, y, rw, rh = LOUVRE
    w.runs(x, x + rw, y, y + rh, (ID_LOUVRE, ID_DUCT), 0.12, fall=rh / 2.0)
    # the deck: dirt in patches, ponding marks
    x, y, rw, rh = DECK
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.12 * nz("blotch"), (ID_FELT,))
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_brick(c)
    paint_column_band(c)
    paint_fascia(c)
    paint_pipe_band(c)
    c.check_bands(BAND_IDS)
    paint_window(c, WINDOW[0], WINDOW[1], PPM, REGION_COLS, [0, 1, 2, 3])
    paint_bigdoor(c, BIGDOOR[0], BIGDOOR[1], PPM)
    paint_entrance(c, ENTRANCE[0], ENTRANCE[1], PPM)
    paint_service(c, SERVICE[0], SERVICE[1], PPM)
    paint_hatch(c, HATCH[0], HATCH[1], PPM)
    paint_flue_end(c, FLUE_END[0], FLUE_END[1], PPM)
    paint_louvre(c, LOUVRE[0], LOUVRE[1])
    paint_bushing(c, BUSHING[0], BUSHING[1], PPM)
    paint_deck(c)
    for ename in ELEV:
        paint_elevation(c, ename)
    paint_patches(c)

    # Tone wear, grain and pores. Every field repeats every 256 rows, so the
    # brick band's slabs and the U wrap stay seamless.
    def nz(seed, sx, sy=None):
        return atlas.noise(c, seed, sx, sy, tile_y=TILE_Y)
    wear = 0.025 * nz(3, 40.0) + 0.015 * nz(4, 8.0)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH))
    streak = nz(7, 0.8, 40.0)
    c.shade[walls] *= 1.0 + 0.03 * streak[walls]
    sheet = np.isin(c.mid, (ID_DOOR, ID_FRAME, ID_DUCT, ID_COPING, ID_LOUVRE))
    grain = nz(5, 60.0, 0.35)
    c.shade[sheet] *= 1.0 + 0.016 * grain[sheet]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_CONC, ID_MORTAR, ID_SOFFIT))
    pores = nz(9, 0.8)
    c.shade[mineral] *= 1.0 + 0.03 * pores[mineral]
    c.height[mineral] += 0.0006 * pores[mineral]
    conc = c.mid == ID_CONC
    mottle = nz(11, 6.0)
    c.shade[conc] *= 1.0 + 0.035 * mottle[conc]
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
    return t


def export(out_dir, ss=atlas.SS):
    """Candidate glazing in the emission map is neutral grey, each window the
    lit room behind it; nothing else on the building glows, and no occupancy
    or schedule is baked in."""
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.010)
    c.weather.dust(cav, (ID_BRICK, ID_BRICK2, ID_MORTAR))
    rough = 0.04 * atlas.noise(c, 13, 20.0, tile_y=TILE_Y)
    path = os.path.join(out_dir, ASSET)
    glass = atlas.coverage(c, ID_GLASS)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS,)), path + "_normal.png"),
               atlas.save(glazing.night_rooms(glass > 0, atlas.emission_colours(c, EMIT)),
                          path + "_emission.png")]
    for v in VARIANTS:
        base = atlas.albedo(c, lut(v), grime=0.25 * cav)
        rgb = glazing.rooms(glass >= 0.5, base.copy())
        # In the 6 px/m elevations a pane is a pixel or two and nearly every
        # pixel is mostly glass, so rooms() would repaint whole pixels and
        # drop the bars mixed into them, leaving the LOD3 windows far darker
        # than the LOD2 ones. There the glass keeps glazing.BASE, box-filtered
        # with its frame and bars.
        for ex, ey, ew, eh in ELEV.values():
            rgb[ey:ey + eh, ex:ex + ew] = base[ey:ey + eh, ex:ex + ew]
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
