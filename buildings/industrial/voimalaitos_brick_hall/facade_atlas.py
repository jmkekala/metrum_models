# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
voimalaitos_brick_hall.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
plan, heights, the walls and their openings, band rows and region
rectangles -- so a change here cannot leave the UVs pointing at the wrong
artwork.

The atlas is a trim sheet. Five bands run the full width and tile in U:

    y    0 ..  336   BRICK   z 0 .. 5.25 m: the cast concrete plinth and
                             stretcher-bond facing brick. Walls above 5.25 m
                             sample its rows 1.25 .. 5.25 m in 4 m slabs
                             (SLAB): the bond, the tones and every noise
                             repeat every 256 rows, so the slab lines vanish.
    y  336 ..  348           the brick's bond carried on into the gutter, so
                             a coarse mip at a slab's top still averages brick
    y  352 ..  432   BUNKER  1.25 m of brick with a small square window every
                             2 m: the bunker bay's window row, on brick at
                             both edges for the same reason.
    y  440 ..  480   CONC    0.625 m of light precast concrete, U along the
                             wall: the window band's sill, spandrels and head,
                             and the openings' reveals (V the depth).
    y  488 ..  512   COPE    the 0.375 m concrete coping on every parapet.
    y  518 ..  530   PIPE    galvanised steel, round-shaded across V: the
                             roof safety kit (PIPE_STRIP).
    y  536 .. 1020   unique  the steel hall window and the small square one,
                             the doors, the flue stub, the cable bushings, the
                             lettering and the coal-dusted wall under the
                             gallery (both brick in the band's own bond), the
                             gallery's sheeting, the stub stacks, the two
                             roof decks (8 px/m), the LOD3 elevations (6 px/m)
                             and flat patches.

The hall window is painted once, four columns and four pane rows, and
build.py assembles every multi-pane window from its sections: the bottom
row, middle rows with or without the hopper, the top row, and in width the
outer columns and the middle ones (window_sections()).

Two unique regions continue the brick band: the lettering under the turbine
hall's coping and the wall under the coal gallery. Each sits in the atlas
at the U its wall samples the band at (U_OFF is chosen for that) and on rows
a whole number of bond repeats (32 rows, six courses) from the band rows its
heights sample, so its bond runs on into the band's across its edges.

Rasterising is scripts/atlas.py's; dirt, algae, rust, faded paint and coal
dust are scripts/weathering.py's fields, placed by weather() below.
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

ASSET = "voimalaitos_brick_hall"
ATLAS = 1024
PPM = 64.0
LPPM = 6.0              # the LOD3 elevations
DPPM = 8.0              # the roof decks
GPPM = 24.0             # the coal gallery's sheeting
SPPM = 32.0             # the stub stacks
PAD = 2                 # rows each band paints beyond its own edge

# ------------------------------------------------------------------ plan
# Blender build frame, front toward -Y. The boiler house is the west block,
# a little deeper than the turbine hall so its corners stand proud of the
# hall's front and rear walls; the turbine hall abuts its east face.
BH = (-16.0, -2.0, -8.5, 8.5)          # x0, x1, y0, y1: 14 x 17 m
TH = (-2.0, 16.0, -8.0, 8.0)           # 18 x 16 m

# ------------------------------------------------------------ vertical layout
# Metres above ground; every height is a whole or half texel at 64 px/m.
Z_PLINTH = 0.625        # 40 px; cast concrete base under every wall
COPING = 0.375          # the concrete coping on the parapet, foot to top
CO = 0.05               # it oversails the brick outside by this much
CO_IN = 0.05            # and the parapet's inner face by this much
PIN = 0.25              # the parapet's inner face, inside the wall line
WALL_IN = 0.125         # the walls run this far up into the coping
DECK_DOWN = 0.875       # the deck, below the coping's top

Z_BC = 19.5             # boiler house coping top
Z_BS = Z_BC - COPING    # 19.125, the coping's foot
Z_BWT = Z_BS + WALL_IN  # 19.25, its wall tops, inside the coping
Z_BD = Z_BC - DECK_DOWN  # 18.625, its deck
Z_TC = 11.625           # turbine hall coping top
Z_TS = Z_TC - COPING    # 11.25
Z_TWT = Z_TS + WALL_IN  # 11.375
Z_TD = Z_TC - DECK_DOWN  # 10.75
BURY = 0.5              # the turbine hall's coping runs this far into the
                        # boiler house, which hides its open ends

# The brick band holds z 0 .. BAND_TOP. Above that the walls are cut at
# CUTS into 4 m slabs, slab i sampling the band SLAB * i lower.
BAND_TOP = 5.25
SLAB = 4.0
CUTS = (5.25, 9.25, 13.25, 17.25, 21.25)

# ----------------------------------------------------------------- windows
# One steel window design: frame FR, columns CW wide on mullions, pane rows
# RH tall on bars. A window is (cols, rows). The region is four columns
# (outer, two middles, outer) by four rows (bottom, hopper, plain, top).
FR = 0.0625             # 4 px
CW = 0.5                # 32 px
RH = 0.75               # 48 px
MUL = 0.046875          # 3 px
REGION_COLS = 4
REGION_ROWS = 4
SQ = 0.8125             # the small square window, 52 px


def win_size(cols, rows):
    return (2 * FR + cols * CW, 2 * FR + rows * RH)


# Other openings and flush panels: (width, height), metres.
SIZES = {
    "entrance": (2.0, 3.0),
    "bigdoor": (3.5, 4.0),
    "service": (1.1875, 2.375),
    "sq": (SQ, SQ),
    "bushing": (2.5, 1.25),     # flush: painted on the wall at every tier
    "letters": (10.5, 1.25),    # flush: brick with the lettering on it
    "mouth": (3.25, 2.375),     # flush: brick under the coal gallery, dusted
}
REVEAL = {"win": 0.25, "sq": 0.2, "entrance": 0.25, "bigdoor": 0.3,
          "service": 0.25}
FLUSH = ("bushing", "letters", "mouth", "conc")
DOOR_FRAME = 0.09375    # 6 px of steel frame round every door
LEAF_TOP = {"entrance": 2.3, "service": 2.1}

# ------------------------------------------------------------------ walls
# name: (p0, p1, z foot, z top). Walked counter-clockwise from above, so the
# outward face is on the right. The two returns are the boiler house's
# corners where they stand proud of the turbine hall; "step" is the boiler
# house's east face above the turbine hall's roof (it runs on down to the
# hall's deck between the hall's parapets; build.py adds that strip).
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
# the coping foot over each wall, for the ladders
SOFFIT = {"bh_front": Z_BS, "bh_rear": Z_BS, "bh_west": Z_BS, "step": Z_BS,
          "th_front": Z_TS, "th_east": Z_TS, "th_rear": Z_TS}

# The boiler house front's window band: five lights 1.125 m wide on
# 0.3125 m brick piers, in three tiers of 3.875 m on light concrete
# spandrels, a concrete sill under it and a head over it.
LIGHT_X = (-11.875, -10.4375, -9.0, -7.5625, -6.125)
LIGHT = (2, 5)
TIERS = (3.75, 8.25, 12.75)
BAND_W = 6.875
BAND_STRIPS = ((3.5, 0.25), (7.625, 0.625), (12.125, 0.625), (16.625, 0.25))
# Small square windows on the gallery levels, every 3.75 m.
SQ_Z = (4.0, 7.75, 11.5, 15.25)
# The turbine hall's front: four hall windows 1.625 x 6.875 m on equal
# piers, and one over the machinery door, every head at 9.375 m.
TH_WIN_X = (0.5, 3.75, 7.0, 10.25)
TH_WIN = (3, 9)
TH_SILL = 2.5
DOOR_WIN = (3, 6)
DOOR_WIN_SILL = 4.75
LETTERS_Z = 9.625       # the lettering band's foot, under the hall's coping

# The coal gallery on the west wall: an enclosed conveyor stub leaving the
# wall at GAL_ZM (centre line), sloping down away from it at GAL_SLOPE,
# GAL_W wide and GAL_H tall (vertical), GAL_LEN on the plan, its end a
# closed blank face. Its back runs GAL_BURY into the parapet's brick.
GAL_Y = 4.5
GAL_W, GAL_H = 2.6, 2.8
GAL_ZM = 17.625
GAL_SLOPE = 20.0
GAL_LEN = 5.0
GAL_BURY = 0.2
GAL_TAN = math.tan(math.radians(GAL_SLOPE))
GAL_X0 = BH[0]                          # the wall face it leaves
GAL_X1 = BH[0] - GAL_LEN                # its far end
MOUTH_Z = 14.125                        # the dusted brick under it, from here

# Openings: (kind, plan centre along the wall, z of its foot, extra): extra
# is (cols, rows) for a window, (width, height) for a concrete strip.
ITEMS = {
    "bh_front": ([("win", x, z, LIGHT) for z in TIERS for x in LIGHT_X]
                 + [("conc", -9.0, z, (BAND_W, h)) for z, h in BAND_STRIPS]
                 + [("sq", x, z, None) for x in (-14.25, -3.75) for z in SQ_Z]
                 + [("entrance", -9.0, 0.0, None)]),
    "bh_ret_front": [],
    "th_front": ([("win", x, TH_SILL, TH_WIN) for x in TH_WIN_X]
                 + [("bigdoor", 13.5, 0.0, None),
                    ("win", 13.5, DOOR_WIN_SILL, DOOR_WIN),
                    ("letters", 7.0, LETTERS_Z, None)]),
    "th_east": [("sq", -5.0, 7.75, None), ("sq", 5.0, 7.75, None),
                ("bushing", 0.0, 6.25, None)],
    "th_rear": ([("sq", x, 7.75, None) for x in (14.0, 8.5, 5.0, 1.5)]
                + [("sq", x, 2.0, None) for x in (14.0, 8.5, 5.0)]
                + [("service", 0.0, 0.0, None)]),
    "bh_ret_rear": [],
    "bh_rear": ([("sq", x, z, None) for x in (-4.5, -13.5) for z in SQ_Z]
                + [("sq", -9.0, 4.0, None), ("sq", -9.0, 7.75, None)]),
    "bh_west": ([("sq", GAL_Y, z, None) for z in SQ_Z[:3]]
                + [("sq", -GAL_Y, z, None) for z in SQ_Z]
                + [("mouth", GAL_Y, MOUTH_Z, None)]),
    "step": [("sq", -5.0, 15.25, None), ("sq", 5.0, 15.25, None)],
}

# Things outside the walls that build.py makes as solids of their own.
CANOPY = (-10.6, -7.4, 1.25, 3.25, 0.25)        # x0, x1, projection, z, thickness
FLUE = (-10.0, -8.0, 1.0, 12.75, 2.0)           # x0, x1, projection, z, height
# The raised coal bunker bay on the boiler house's roof, its faces 0.1 m
# behind the walls under it: brick, a row of square windows, a coping.
BUNKER = (-15.9, -2.1, 1.9, 8.4)                # plan
BUNKER_TOP = 24.0
BUNKER_WIN = (21.0, 22.25)                      # the window row's band
BUNKER_COPE = BUNKER_TOP - COPING
BUNKER_PITCH = 2.0       # a window centred on every face, 2 m apart
# Two steel stub stacks on the boiler house's deck in front of the bay.
STACKS = [(-12.5, 0.0), (-10.0, 0.0)]
STACK_R = 0.78          # octagon, to its corners: 1.44 m across the flats
STACK_TOP = 24.75
STACK_WALL, STACK_DEPTH = 0.08, 1.0
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
    kind, _c, _z, extra = item
    if kind == "win":
        return win_size(*extra)
    if kind == "conc":
        return extra
    return SIZES[kind]


def item_rect(name, item):
    """(s0, s1, z0, z1) of an opening or panel on its wall."""
    w, h = item_size(item)
    s = wall_s(name, item[1])
    return (s - w / 2.0, s + w / 2.0, item[2], item[2] + h)


def slab_of(z):
    """Index of the brick slab a height lies in, from the cell's foot."""
    for i, c in enumerate(CUTS):
        if z < c - 1e-9:
            return i
    return len(CUTS)


def row_seq(rows):
    """A window's pane rows, region rows: bottom (0), plain (2) with a
    hopper row (1) every third, top (3)."""
    return [0] + [1 if i % 3 == 1 else 2 for i in range(rows - 2)] + [3]


def col_seq(cols):
    return [0] + [1 + (i % 2) for i in range(cols - 2)] + [3]


def window_sections(cols, rows):
    """The window's sections in width and height: lists of (a0, a1, r0),
    metres from the window's corner to metres into the region, consecutive
    sections that are consecutive in the region merged."""
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
    return runs(col_seq(cols), CW, cols), runs(row_seq(rows), RH, rows)


# ------------------------------------------------------------------- bands
BRICK_Y0, BRICK_H = 0, 336            # z 0 .. BAND_TOP
BRICK_PHASE = BRICK_Y0 + 40           # the first course's foot, at the plinth's top
BRICK_RUN = 348                       # the bond runs on into the gutter to here
CONC_Y0, CONC_H = 440, 40             # 0.625 m
COPE_Y0, COPE_H = 488, 24             # 0.375 m
PIPE_Y0, PIPE_H = 518, 12
# The ladders' sides span the band's middle eight rows
PIPE_STRIP = (PIPE_Y0 + 2, PIPE_Y0 + PIPE_H - 2)
BUNK_Y0, BUNK_H = 352, 80             # z BUNKER_WIN

COURSE = 16.0 / 3.0     # brick course pitch in px: 0.0833 m
BRICK_L = 16.0          # stretcher: 0.25 m, 64 bricks per atlas width
TONE_COURSES = 48       # tones repeat every 256 rows, SLAB metres
TILE_Y = 4              # every noise repeats every 256 rows likewise
BOND_ROWS = 32          # six courses: the bond's own repeat

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels. check_regions() asserts they neither overlap nor
# run off the sheet, and that each matches its opening's size.
BIGDOOR = (4, 536, 224, 256)                    # 3.5 x 4.0 m
WINDOW = (236, 536, 136, 200)                   # 2.125 x 3.125 m: 4 x 4 panes
ENTRANCE = (380, 536, 128, 192)                 # 2.0 x 3.0 m
SERVICE = (516, 536, 76, 152)                   # 1.1875 x 2.375 m
STACK = (600, 536, 20, 204)                     # one octagon face, 6.375 m, at SPPM
FLUE_END = (628, 536, 128, 128)                 # 2.0 x 2.0 m
FLUE_SIDE = (628, 672, 128, 64)                 # 2.0 m (U, up) x 1.0 m (V, out)
BUSHING = (764, 536, 160, 80)                   # 2.5 x 1.25 m
SQWIN = (932, 536, 52, 52)                      # 0.8125 m square
MOUTH = (772, 648, 208, 152)                    # 3.25 x 2.375 m, brick
LETTERS = (4, 936, 672, 80)                     # 10.5 x 1.25 m, brick
DECK_T = (604, 744, 148, 132)                   # 18.5 x 16.5 m at DPPM
DECK_B = (756, 806, 116, 140)                   # 14.5 x 17.5 m at DPPM
GAL_SIDE = (876, 806, 128, 67)                  # 5.33 x 2.8 m at GPPM
GAL_TOP = (876, 880, 128, 62)                   # 5.33 x 2.6 m at GPPM
GAL_END = (684, 946, 62, 67)                    # 2.6 x 2.8 m at GPPM
REGION = {"entrance": ENTRANCE, "bigdoor": BIGDOOR, "service": SERVICE,
          "sq": SQWIN, "bushing": BUSHING, "letters": LETTERS, "mouth": MOUTH}
# where each deck's region starts on the plan
DECK_T_O = (-2.55, -8.1)
DECK_B_O = (-16.1, -8.6)

# LOD3 elevations at LPPM: which walls each holds, and where along it.
ELEV = {
    "front": (4, 800, 192, 116),
    "rear": (200, 800, 192, 116),
    "west": (396, 800, 102, 116),
    "east": (502, 800, 96, 69),
    "step": (502, 874, 96, 48),
}
ELEV_WALLS = {"front": (("bh_front", 0.0), ("th_front", 14.0)),
              "rear": (("th_rear", 0.0), ("bh_rear", 18.0)),
              "west": (("bh_west", 0.0),),
              "east": (("th_east", 0.0),),
              "step": (("step", 0.0),)}
ELEV_ZB = {"front": 0.0, "rear": 0.0, "west": 0.0, "east": 0.0, "step": Z_TWT}
WALL_ELEV = {w: (e, off) for e, ws in ELEV_WALLS.items() for w, off in ws}

PATCH_NAMES = ("blank", "soffit", "cope_top", "conc", "duct", "soot", "felt",
               "rim", "gal_under", "dark")
PATCHES = {n: (756 + 20 * (i % 12), 952 + 22 * (i // 12), 16, 16)
           for i, n in enumerate(PATCH_NAMES)}


def _u_offsets():
    """Where each wall samples the brick band in U: end to end round the
    building, except that the two walls with a brick region of their own
    sample the band at the U their region sits at in the atlas."""
    u, out = 0.0, {}
    for n in WALL_ORDER[:-1]:
        out[n] = u
        u += wall_len(n)
    out["step"] = 0.0
    for name, kind in (("th_front", "letters"), ("bh_west", "mouth")):
        it, = [i for i in ITEMS[name] if i[0] == kind]
        s0 = item_rect(name, it)[0]
        out[name] = (REGION[kind][0] / PPM - s0) % (ATLAS / PPM)
    return out


U_OFF = _u_offsets()

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_CONC, ID_FRAME, ID_GLASS, ID_DOOR, ID_GALV = 5, 6, 7, 8, 9
ID_HANDLE, ID_DARK, ID_SEAL, ID_SOFFIT, ID_FELT = 10, 11, 12, 13, 14
ID_COPE, ID_DUCT, ID_SOOT, ID_PORC, ID_SHEET = 15, 16, 17, 18, 19
ID_LETTER, ID_STACK, ID_BALLAST, ID_PANEL = 20, 21, 22, 23

# (roughness, metallic). Painted steel stays mostly dielectric -- the paint
# is what the light sees. The ladders are galvanised.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.82, 0.0), ID_MORTAR: (0.94, 0.0), ID_CONC: (0.86, 0.0),
    ID_FRAME: (0.44, 0.0), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_DOOR: (0.52, 0.0), ID_GALV: (0.48, 0.60), ID_HANDLE: (0.35, 0.80),
    ID_DARK: (0.96, 0.0), ID_SEAL: (0.90, 0.0), ID_SOFFIT: (0.86, 0.0),
    ID_FELT: (0.92, 0.0), ID_COPE: (0.82, 0.0), ID_DUCT: (0.62, 0.15),
    ID_SOOT: (0.98, 0.0), ID_PORC: (0.22, 0.0), ID_SHEET: (0.50, 0.05),
    ID_LETTER: (0.55, 0.0), ID_STACK: (0.70, 0.10), ID_BALLAST: (0.96, 0.0),
    ID_PANEL: (0.74, 0.0),
}

# ---------------------------------------------------------------- palettes
# One coherent brick per instance: the brick changes, and the window steel
# and the doors move with it. Window steel is always lighter than the glass
# it holds. The concrete, the coping, the roofs, the gallery and the kit
# stay the same.
#
# red_brick is shared with the plant's other pieces: each brick-face colour
# c of the earlier palette went to Y + 0.6 * (c - Y) per channel (Y its
# Rec.709 luma), times 0.94, the mortar a further 10 % darker:
# brick (142, 68, 50), brick2 (112, 55, 43), mortar (150, 146, 138) before.
VARIANTS = {
    "red_brick": {"brick": (111, 69, 59), "brick2": (88, 56, 49),
                  "mortar": (126, 124, 120), "frame": (198, 198, 192),
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
    ID_GLASS: glazing.BASE, ID_PLINTH: (148, 146, 140), ID_CONC: (168, 166, 158),
    ID_GALV: (134, 137, 137), ID_HANDLE: (150, 150, 148), ID_DARK: (24, 24, 24),
    ID_SEAL: (34, 34, 34), ID_SOFFIT: (150, 148, 142), ID_BLANK: (52, 52, 52),
    ID_FELT: (58, 58, 60), ID_COPE: (164, 162, 155), ID_DUCT: (74, 74, 76),
    ID_SOOT: (20, 19, 18), ID_PORC: (104, 58, 38), ID_SHEET: (192, 192, 186),
    ID_LETTER: (212, 210, 202), ID_STACK: (62, 62, 63), ID_BALLAST: (82, 80, 76),
    ID_PANEL: (54, 56, 58),
}

# A stray pixel in a tiling band is not a local blemish: every surface that
# samples the band repeats it.
BAND_IDS = {
    "BRICK": ((0, BRICK_RUN), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH}),
    "BUNKER": ((350, 436), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_FRAME, ID_GLASS,
                            ID_CONC}),
    "CONC": ((438, 482), {ID_CONC}),
    "COPE": ((486, 514), {ID_COPE}),
    "PIPE": ((516, 532), {ID_GALV}),
}

# The candidate-glazing mask is the emission map, neutral white.
EMIT = {ID_GLASS: (255, 255, 255)}
# Linear RGB: industrial hall lamps, the value the catalog's works use.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto: only the few
# centimetres the mesh does not model.
BRICK_FACE = 0.006      # brick face proud of the recessed mortar
ARRIS_H = 0.008         # the concrete's arrises
FRAME_H = 0.035         # window frames, proud of the glass
TRAN_H = 0.030          # mullions and bars
SASH_H = 0.045          # the hopper's sash
DOOR_FRAME_H = 0.030    # door frames and stiles
RIB_H = 0.006           # sheet ribs on the machinery door
CORR_H = 0.012          # the gallery's corrugations
SEAM_H = 0.020          # its roof's standing seams
LETTER_H = 0.020        # the letters, proud of the brick
FLANGE_H = 0.012        # the stacks' flanges

# ---------------------------------------------------------------- lettering
# Plain individual sans-serif capitals, CAP tall, strokes STROKE caps wide,
# centred in the brick band under the turbine hall's coping. A generic word,
# no plant's or company's name. Painted, not lit.
TEXT = "VOIMALAITOS"
CAP = 1.0
STROKE = 0.14
TRACK = 0.24
GLYPH_W = {"V": 0.78, "O": 0.92, "I": STROKE, "M": 0.92, "A": 0.84, "L": 0.58,
           "T": 0.74, "S": 0.66}


def m(v):
    """Metres -> pixels at 64 px/m."""
    return v * PPM


# ================================================================== bands
def paint_brick_area(c, x0, x1, y0, y1):
    """Stretcher-bond facing brick over a rect, in the band's own bond: 64
    bricks per width, courses 1/12 m from BRICK_PHASE, two tones, mortar
    recessed. Any rect whose rows are a whole number of BOND_ROWS from the
    band rows it continues, and whose X is the U it continues, matches it."""
    c.paint(x0, x1, y0, y1, ID_BRICK, 1.0, 1.0)
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    r = np.floor((Y - BRICK_PHASE) / COURSE).astype(np.int64)
    off = (r % 2) * BRICK_L * 0.5
    b = np.floor((X - off) / BRICK_L).astype(np.int64) % int(ATLAS / BRICK_L)
    rr = r % TONE_COURSES
    bed = (Y - BRICK_PHASE - r * COURSE) < 1.0
    perp = ((X - off) % BRICK_L) < 1.0
    joint = bed | perp
    tone = 0.90 + 0.20 * atlas.hash_unit(b, rr, 17)
    dark = atlas.hash_unit(atlas.hash_int(b, rr, 29), 7) < 0.17
    c.mid[sy, sx] = np.where(joint, ID_MORTAR, np.where(dark, ID_BRICK2, ID_BRICK))
    c.shade[sy, sx] = np.where(joint, 0.94, tone)
    c.ao[sy, sx] = np.where(joint, 0.80, 1.0)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)


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
    paint_brick_area(c, 0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_RUN)
    paint_plinth(c)


def paint_conc_band(c):
    """Light precast concrete, 0.625 m across V: smooth, an arris at both
    edges, faint pores and a panel joint every 1.5 m along U."""
    y0, y1 = CONC_Y0, CONC_Y0 + CONC_H
    c.paint(0, ATLAS, y0 - PAD, y1 + PAD, ID_CONC, 1.0, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, y1, ARRIS_H, 1.5, axes="y")
    c.mul(0, ATLAS, y0, y0 + 1, 0.95)
    c.mul(0, ATLAS, y1 - 1, y1, 0.95)
    for i in range(int(ATLAS / 96)):
        x = i * 96.0 + 48.0
        c.mul(x, x + 1, y0, y1, 0.90, ao=0.90)
        c.lift(x, x + 1, y0, y1, -0.002)


def paint_cope_band(c):
    """The parapet's coping, 0.375 m: precast concrete units a metre long,
    a drip groove near the foot whose shadow lies under it, the top arris."""
    y0, y1 = COPE_Y0, COPE_Y0 + COPE_H
    c.paint(0, ATLAS, y0 - PAD, y1 + PAD, ID_COPE, 1.0, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, y1, ARRIS_H, 1.2, axes="y")
    c.mul(0, ATLAS, y0 - PAD, y0 + 1, 0.80, ao=0.80)               # the soffit's edge
    c.mul(0, ATLAS, y0 + 3, y0 + 4, 0.82, ao=0.82)                 # drip groove
    c.lift(0, ATLAS, y0 + 3, y0 + 4, -0.006)
    for i in range(int(ATLAS / 64)):                               # unit joints
        x = i * 64.0 + 32.0
        c.mul(x, x + 1, y0, y1, 0.84, ao=0.86)
        c.lift(x, x + 1, y0, y1, -0.003)


def paint_pipe_band(c):
    """Galvanised steel, round-shaded across V, a clip every metre."""
    y0, y1 = PIPE_Y0, PIPE_Y0 + PIPE_H
    c.paint(0, ATLAS, y0 - PAD, y1 + PAD, ID_GALV, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y1 + PAD)
    u = np.clip(2.0 * (Y - y0) / (y1 - y0) - 1.0, -1.0, 1.0)
    clip = (X % 64.0) < 2.0
    c.shade[sy, sx] = (0.86 + 0.14 * np.cos(0.5 * np.pi * u)) * np.where(clip, 0.82, 1.0)


def paint_bunker_band(c):
    """The bunker bay's window row: the band's brick, and a small square
    window every BUNKER_PITCH, flush on the face, a concrete sill under
    each and the recess's occlusion round it."""
    y0, y1 = BUNK_Y0, BUNK_Y0 + BUNK_H
    paint_brick_area(c, 0, ATLAS, y0 - PAD, y1 + 2 * PAD)
    p = m(BUNKER_PITCH)
    wy = y0 + m(0.21875)
    for k in range(int(round(ATLAS / p))):
        cx = p / 2.0 + k * p
        x0 = cx - m(SQ) / 2.0
        c.mul(x0 - 3, x0 + m(SQ) + 3, wy - 3, wy + m(SQ) + 3, 0.72, ao=0.70)
        c.paint(x0 - 4, x0 + m(SQ) + 4, wy - 5, wy - 1, ID_CONC, 0.96, 0.9, height=0.0)
        paint_sq(c, x0, wy, PPM, pad=0)


# ================================================================ regions
def _bar(c, a0, a1, b0, b1, mid=ID_FRAME, h=FRAME_H, ao=0.88, shade=1.0,
         axes="xy", w=1.0):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, w, axes=axes)


def paint_window(c, x0, y0, ppm, cols, seq, pad=PAD):
    """A steel multi-pane window at *ppm*, corner at pixel (x0, y0): a
    frame, *cols* columns on mullions, one pane row per entry of *seq* (0
    bottom, 1 with the hopper, 2 plain, 3 top) on bars. The region paints
    seq (0, 1, 2, 3) and four columns; the LOD3 elevations paint each
    window whole."""
    def P(v):
        return v * ppm

    def B(v):
        # a bar never thinner than one sample: at the elevations' 6 px/m it
        # would vanish, leaving the window darker than the region
        return max(v * ppm, 1.0 / c.ss)
    n = len(seq)
    W, H = win_size(cols, n)
    k = ppm / PPM
    bw = max(0.25, k)
    _bar(c, x0 - pad, x0 + P(W) + pad, y0 - pad, y0 + P(H) + pad, h=FRAME_H, w=bw)
    ix0, ix1 = x0 + P(FR), x0 + P(W - FR)
    c.paint(ix0, ix1, y0 + P(FR), y0 + P(H - FR), ID_FRAME, 1.0, 0.9, height=TRAN_H)
    for j, kind in enumerate(seq):
        b0 = y0 + P(FR + j * RH) + (B(MUL) / 2.0 if j > 0 else 0.0)
        b1 = y0 + P(FR + (j + 1) * RH) - (B(MUL) / 2.0 if j < n - 1 else 0.0)
        for i in range(cols):
            a0 = x0 + P(FR + i * CW) + (B(MUL) / 2.0 if i > 0 else 0.0)
            a1 = x0 + P(FR + (i + 1) * CW) - (B(MUL) / 2.0 if i < cols - 1 else 0.0)
            if kind == 1:                       # the hopper's sash in the pane
                s = B(0.03125)
                _bar(c, a0, a1, b0, b1, h=SASH_H, w=bw)
                c.mul(a0, a1, b0, b0 + 1.5 * k, 0.86, ao=0.84)
                a0, a1, g0, g1 = a0 + s, a1 - s, b0 + s, b1 - s
            else:
                g0, g1 = b0, b1
            c.paint(a0, a1, g0, g1, ID_GLASS, 1.0, 0.92, height=0.0)
            c.mul(a0, a1, g1 - 2.0 * k, g1, 0.92, ao=0.86)
        if j > 0:                                   # the bar under it
            t = y0 + P(FR + j * RH)
            c.mul(ix0, ix1, t - B(MUL) / 2.0 - 1.5 * k, t - B(MUL) / 2.0, 0.90, ao=0.86)
    c.mul(x0, x0 + P(W), y0, y0 + P(FR), 0.92, ao=0.86)  # bottom rail holds water


def paint_sq(c, x0, y0, ppm, pad=PAD):
    """The small square steel window: a frame round four panes on a cross."""
    k = ppm / PPM
    bw = max(0.25, k)
    s = SQ * ppm
    f = max(FR * ppm, 1.0 / c.ss)
    b = max(MUL * ppm, 1.0 / c.ss)
    _bar(c, x0 - pad, x0 + s + pad, y0 - pad, y0 + s + pad, h=FRAME_H, w=bw)
    mx, my = x0 + s / 2.0, y0 + s / 2.0
    for a0, a1 in ((x0 + f, mx - b / 2.0), (mx + b / 2.0, x0 + s - f)):
        for g0, g1 in ((y0 + f, my - b / 2.0), (my + b / 2.0, y0 + s - f)):
            c.paint(a0, a1, g0, g1, ID_GLASS, 1.0, 0.92, height=0.0)
            c.mul(a0, a1, g1 - 2.0 * k, g1, 0.92, ao=0.86)
    c.mul(x0, x0 + s, y0, y0 + f, 0.92, ao=0.86)


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
    c.paint(a0, a1, b0, b1, mid, 1.0, 0.9, height=0.02)
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
    a0 = l0 + lw + 10 * k
    a1 = a0 + 0.8 * ppm
    b0, b1 = y0 + 12 * k, y0 + 2.05 * ppm
    c.paint(a0, a0 + 1.0 * k, b0, b1, ID_DARK, 1.0, 0.6, height=-0.003)
    c.paint(a1 - 1.0 * k, a1, b0, b1, ID_DARK, 1.0, 0.6, height=-0.003)
    c.paint(a0, a1, b1 - 1.0 * k, b1, ID_DARK, 1.0, 0.6, height=-0.003)
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


def paint_flue_side(c):
    """The flue stub's sides: its concrete casing, U up the side (2 m) and V
    out from the wall (1 m), arrises on the outer edges."""
    x, y, w, h = FLUE_SIDE
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CONC, 1.0, 1.0, height=0.0)
    c.bevel(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ARRIS_H, 1.5)


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
            ID_COPE, 1.0, 0.9, height=0.005)


# ------------------------------------------------------------- lettering
def _glyph(ch, w, sw):
    """test(u, v) for capital *ch* in cap-height units: u from its left,
    v up from the baseline; strokes *sw* wide."""
    def seg(ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        ll = math.hypot(dx, dy)
        ext = sw / ll

        def t(u, v):
            tt = ((u - ax) * dx + (v - ay) * dy) / (ll * ll)
            d = np.abs((u - ax) * dy - (v - ay) * dx) / ll
            return (d <= sw / 2.0) & (tt >= -ext) & (tt <= 1.0 + ext)
        return t

    def ring(cx, cy, rx, ry, cut=None):
        def t(u, v):
            a, b = (u - cx) / rx, (v - cy) / ry
            ai, bi = (u - cx) / (rx - sw), (v - cy) / (ry - sw)
            hit = (a * a + b * b <= 1.0) & (ai * ai + bi * bi >= 1.0)
            if cut is not None:
                th = np.degrees(np.arctan2(b, a))
                lo, hi = cut
                hit &= ~((th > lo) & (th < hi))
            return hit
        return t

    if ch == "V":
        parts = [seg(sw * 0.55, 1.0, w / 2.0, 0.0), seg(w / 2.0, 0.0, w - sw * 0.55, 1.0)]
    elif ch == "O":
        parts = [ring(w / 2.0, 0.5, w / 2.0, 0.5)]
    elif ch == "I":
        parts = [lambda u, v: u <= sw]
    elif ch == "M":
        parts = [lambda u, v: (u <= sw) | (u >= w - sw),
                 seg(sw / 2.0, 1.0, w / 2.0, 0.22), seg(w / 2.0, 0.22, w - sw / 2.0, 1.0)]
    elif ch == "A":
        parts = [seg(sw * 0.55, 0.0, w / 2.0, 1.0), seg(w / 2.0, 1.0, w - sw * 0.55, 0.0),
                 lambda u, v: (v >= 0.24) & (v <= 0.24 + sw * 0.85)
                 & (u >= 0.2 * w) & (u <= 0.8 * w)]
    elif ch == "L":
        parts = [lambda u, v: (u <= sw) | (v <= sw)]
    elif ch == "T":
        parts = [lambda u, v: (v >= 1.0 - sw) | (np.abs(u - w / 2.0) <= sw / 2.0)]
    elif ch == "S":
        a = (1.0 + sw) / 4.0
        parts = [ring(w / 2.0, 1.0 - a, w / 2.0, a, cut=(-90.0, 28.0)),
                 ring(w / 2.0, a, w / 2.0, a, cut=(90.0, 180.0)),
                 ring(w / 2.0, a, w / 2.0, a, cut=(-180.0, -152.0))]
        # the lower bowl keeps its right side and its foot round to the
        # left: cut its upper left quarter and the last of its lower left
        parts = [parts[0], lambda u, v, r=parts[1], q=parts[2]: r(u, v) & q(u, v)]
    else:
        raise ValueError("no glyph for %r" % ch)

    def test(u, v):
        hit = np.zeros(np.shape(u), bool)
        for p in parts:
            hit |= p(u, v)
        return hit & (v >= 0.0) & (v <= 1.0) & (u >= 0.0) & (u <= w)
    return test


def text_width(sw=STROKE):
    return sum(GLYPH_W[ch] if ch != "I" else sw for ch in TEXT) + TRACK * (len(TEXT) - 1)


def paint_letters(c, x0, y0, w_px, h_px, ppm):
    """TEXT, CAP tall, centred in the rect at (x0, y0): each capital a
    painted metal letter a little proud of the brick, a soft occlusion
    round it."""
    cap = CAP * ppm
    sw = max(STROKE, 1.2 / cap)
    tw = text_width(sw) * cap
    u0 = x0 + (w_px - tw) / 2.0
    vb = y0 + (h_px - cap) / 2.0
    halo = 1.5 / cap if ppm >= PPM else 0.0
    for ch in TEXT:
        gw = GLYPH_W[ch] if ch != "I" else sw
        test = _glyph(ch, gw, sw)
        if halo:
            big = _glyph(ch, gw + 2 * halo, sw + 2 * halo)
            gx = u0 - halo * cap
            c.shape(gx - 2, gx + (gw + 2 * halo) * cap + 2, vb - halo * cap - 2,
                    vb + cap + halo * cap + 2,
                    lambda X, Y, gx=gx, big=big: big((X - gx) / cap,
                                                     (Y - vb) / cap + halo),
                    ao=0.78)
            sy, sx, Y, X = c.field(gx - 2, gx + (gw + 2 * halo) * cap + 2,
                                   vb - halo * cap - 2, vb + cap + halo * cap + 2)
            hit = big((X - gx) / cap, (Y - vb) / cap + halo)
            c.shade[sy, sx] = np.where(hit, c.shade[sy, sx] * 0.86, c.shade[sy, sx])
        c.shape(u0 - 1, u0 + gw * cap + 1, vb - 1, vb + cap + 1,
                lambda X, Y, u0=u0, test=test: test((X - u0) / cap, (Y - vb) / cap),
                mid=ID_LETTER, shade=1.0, ao=1.0, height=LETTER_H)
        u0 += (gw + TRACK) * cap


def paint_letters_region(c):
    x, y, w, h = LETTERS
    paint_brick_area(c, x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    paint_letters(c, x, y, w, h, PPM)


def paint_mouth(c):
    """The brick under the coal gallery: the band's bond; weather() dusts it."""
    x, y, w, h = MOUTH
    paint_brick_area(c, x - PAD, x + w + PAD, y - PAD, y + h + PAD)


# --------------------------------------------------------------- gallery
def gal_slope_len():
    return (GAL_LEN + GAL_BURY) / math.cos(math.radians(GAL_SLOPE))


def paint_gallery(c):
    """The coal gallery's light sheeting at GPPM. Sides: vertical
    corrugations, U along the slope from the far end, V up from the floor
    line, a flashing at the top and the floor rail at the foot. Roof:
    standing seams down the slope. End: a sheet frame round the dark
    blanking panel, set back."""
    k = GPPM / PPM
    x, y, w, h = GAL_SIDE
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_SHEET, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    ph = 2.0 * np.pi * (X - x) / (0.1875 * GPPM)
    c.shade[sy, sx] = 0.96 + 0.05 * np.cos(ph)
    c.height[sy, sx] = CORR_H * (0.5 + 0.5 * np.cos(ph))
    for b0, b1 in ((y - PAD, y + 0.12 * GPPM), (y + h - 0.12 * GPPM, y + h + PAD)):
        c.paint(x - PAD, x + w + PAD, b0, b1, ID_SHEET, 0.90, 0.92, height=0.0)
    c.mul(x - PAD, x + w + PAD, y + h - 0.12 * GPPM - 1, y + h - 0.12 * GPPM, 0.84, ao=0.84)
    c.mul(x - PAD, x + w + PAD, y + 0.12 * GPPM, y + 0.12 * GPPM + 1, 0.88, ao=0.88)
    for i in range(1, 4):                               # sheet laps every 1.33 m
        xx = x + i * w / 4.0
        c.mul(xx, xx + 1, y, y + h, 0.88, ao=0.88)

    x, y, w, h = GAL_TOP
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_SHEET, 0.94, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    r = (Y - y) % (0.52 * GPPM)
    c.height[sy, sx] = np.where(r < 1.0, SEAM_H, 0.0)
    c.shade[sy, sx] = np.where(r < 1.0, 1.0, np.where(r < 2.0, 0.92, 0.95))
    c.mul(x - PAD, x + w + PAD, y - PAD, y + 1.5, 0.86, ao=0.86)
    c.mul(x - PAD, x + w + PAD, y + h - 1.5, y + h + PAD, 0.86, ao=0.86)

    x, y, w, h = GAL_END
    f = 0.16 * GPPM
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_SHEET, 0.92, 1.0, height=0.0)
    c.bevel(x - PAD, x + w + PAD, y - PAD, y + h + PAD, 0.01, 1.0)
    c.paint(x + f, x + w - f, y + f, y + h - f, ID_PANEL, 1.0, 0.8, height=-0.02)
    c.mul(x + f, x + w - f, y + h - f - 2 * k * 4, y + h - f, 0.82, ao=0.75)
    c.mul(x + f, x + f + 2, y + f, y + h - f, 0.86, ao=0.8)
    c.mul(x + w - f - 2, x + w - f, y + f, y + h - f, 0.86, ao=0.8)
    for i in range(1, 3):                               # the panel's joints
        yy = y + f + i * (h - 2 * f) / 3.0
        c.paint(x + f, x + w - f, yy - 0.5, yy + 0.5, ID_DARK, 1.0, 0.7, height=-0.025)


def paint_stack(c):
    """One face of a steel stub stack at SPPM, V up from the deck: painted
    plate with a flange ring every 2 m, the top sooted."""
    x, y, w, h = STACK
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_STACK, 1.0, 1.0, height=0.0)
    for zz in (0.25, 2.25, 4.25):
        yy = y + zz * SPPM
        c.paint(x - PAD, x + w + PAD, yy, yy + 2.5, ID_STACK, 1.08, 1.0, height=FLANGE_H)
        c.mul(x - PAD, x + w + PAD, yy - 1.5, yy, 0.84, ao=0.84)
    top = y + (STACK_TOP - Z_BD) * SPPM
    c.paint(x - PAD, x + w + PAD, top - 0.18 * SPPM, top + PAD, ID_STACK, 1.06, 1.0,
            height=FLANGE_H)
    c.mul(x - PAD, x + w + PAD, top - 0.18 * SPPM - 1.5, top - 0.18 * SPPM, 0.84, ao=0.84)


# ----------------------------------------------------------------- decks
def paint_deck(c, rect, origin, inner, drains, hatches, kerbs, paths, soot=(),
               bunker=None):
    """A flat roof deck at DPPM, its region's corner at plan point *origin*:
    mineral-surfaced felt, lap seams a metre apart, patches of gravel and of
    a later repair; the felt's upstand along the parapet round *inner*
    (x0, x1, y0, y1); drain outlets, hatches on kerbs, low skylight kerbs and
    a line of paving slabs where people walk; *soot* rings round the stacks
    for weather(); *bunker*, the bay's roof in the part of the region the bay
    covers."""
    x, y, w, h = rect
    ox, oy = origin

    def P(px, py):
        return x + (px - ox) * DPPM, y + (py - oy) * DPPM
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_FELT, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    lap = ((Y - y) % DPPM) < 0.7
    grain = atlas.noise(c, 31, 0.7, tile_y=TILE_Y)[sy, sx]
    tone = atlas.noise(c, 32, 14.0, tile_y=TILE_Y)[sy, sx]
    # mineral-surfaced felt: a fine stone grain, a few grains of the
    # lighter ballast, broad tone where rolls were laid at different times
    c.mid[sy, sx] = np.where(grain > 2.3, ID_BALLAST, ID_FELT)
    c.shade[sy, sx] = np.where(lap, 1.10, 1.0) * (1.0 + 0.05 * np.clip(grain, -2, 2)
                                                  + 0.035 * tone)
    c.height[sy, sx] = np.where(lap, 0.004, 0.0)
    for (px, py, pw, ph) in ((0.25, 0.3, 0.18, 0.1), (0.6, 0.65, 0.12, 0.16)):
        c.mul(x + px * w, x + (px + pw) * w, y + py * h, y + (py + ph) * h, 0.93)
    # the upstand: a lighter felt fillet along the parapet's foot
    x0, y0 = P(inner[0], inner[2])
    x1, y1 = P(inner[1], inner[3])
    for a0, a1, b0, b1 in ((x0, x1, y0, y0 + 2), (x0, x1, y1 - 2, y1),
                           (x0, x0 + 2, y0, y1), (x1 - 2, x1, y0, y1)):
        c.paint(a0, a1, b0, b1, ID_FELT, 1.14, 0.80, height=0.0)
    for px, py in drains:
        cx, cy = P(px, py)
        c.disc(cx, cy, 2.4, ID_FELT, 0.80, 0.70)
        c.disc(cx, cy, 1.3, ID_DARK, 1.0, 0.5, height=-0.01)
    for px, py, s in hatches:
        cx, cy = P(px, py)
        r = s * DPPM / 2.0
        c.paint(cx - r - 1, cx + r + 1, cy - r - 1, cy + r + 1, ID_FELT, 0.70, 0.7)
        c.paint(cx - r, cx + r, cy - r, cy + r, ID_GALV, 1.0, 1.0, height=0.02)
        c.paint(cx - r + 1, cx + r - 1, cy - r + 1, cy + r - 1, ID_DUCT, 1.0, 1.0,
                height=0.03)
    for px, py, kw, kh in kerbs:
        cx, cy = P(px, py)
        a, b = kw * DPPM / 2.0, kh * DPPM / 2.0
        c.paint(cx - a - 1, cx + a + 1, cy - b - 1, cy + b + 1, ID_FELT, 0.70, 0.7)
        c.paint(cx - a, cx + a, cy - b, cy + b, ID_CONC, 0.92, 1.0, height=0.03)
        c.paint(cx - a + 1.5, cx + a - 1.5, cy - b + 1.5, cy + b - 1.5, ID_DARK, 1.0,
                0.9, height=0.02)
    for pts in paths:
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            (ax, ay), (bx, by) = P(ax, ay), P(bx, by)
            c.stroke((ax, ay), (bx, by), 0.4 * DPPM, ID_CONC, 0.62, 0.95, height=0.01)
    if bunker is not None:
        bx0, by0 = P(bunker[0], bunker[2])
        bx1, by1 = P(bunker[1], bunker[3])
        c.paint(bx0, bx1, by0, by1, ID_FELT, 1.0, 1.0, height=0.0)
        sy, sx, Y, X = c.field(bx0, bx1, by0, by1)
        c.shade[sy, sx] = np.where(((Y - by0) % DPPM) < 0.7, 1.10, 1.0)
        for a0, a1, b0, b1 in ((bx0, bx1, by0, by0 + 1.2), (bx0, bx1, by1 - 1.2, by1),
                               (bx0, bx0 + 1.2, by0, by1), (bx1 - 1.2, bx1, by0, by1)):
            c.paint(a0, a1, b0, b1, ID_COPE, 1.0, 1.0, height=0.0)
        cx, cy = P((bunker[0] + bunker[1]) / 2.0, (bunker[2] + bunker[3]) / 2.0)
        c.disc(cx, cy, 2.0, ID_DARK, 1.0, 0.5, height=-0.01)
        hx, hy = P(bunker[0] + 1.6, bunker[2] + 1.4)
        c.paint(hx - 4, hx + 4, hy - 4, hy + 4, ID_GALV, 1.0, 1.0, height=0.02)
        c.paint(hx - 3, hx + 3, hy - 3, hy + 3, ID_DUCT, 1.0, 1.0, height=0.03)


DECK_T_INNER = (TH[0], TH[1] - PIN, TH[2] + PIN, TH[3] - PIN)
DECK_B_INNER = (BH[0] + PIN, BH[1] - PIN, BH[2] + PIN, BH[3] - PIN)


def paint_decks(c):
    paint_deck(c, DECK_T, DECK_T_O, DECK_T_INNER,
               drains=((2.5, -4.5), (2.5, 4.5), (13.0, -4.5), (13.0, 4.5)),
               hatches=((1.5, -5.5, 1.0),),
               kerbs=((8.0, -3.0, 1.4, 2.6), (8.0, 3.5, 1.4, 2.6)),
               paths=(((11.25, 7.7), (11.25, 6.2), (-1.2, 6.2), (-1.2, 0.0)),))
    paint_deck(c, DECK_B, DECK_B_O, DECK_B_INNER,
               drains=((-14.0, -6.5), (-4.0, -6.5)),
               hatches=((-6.0, -4.5, 1.0),),
               kerbs=(),
               paths=(((-2.4, 0.0), (-2.4, -1.3), (-11.25, -1.3)),),
               bunker=BUNKER)


# ------------------------------------------------------------- elevations
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
            "service": paint_service, "bushing": paint_bushing, "sq": paint_sq}


def paint_elevation(c, ename):
    """One LOD3 elevation at LPPM: every wall it holds, with its plinth, its
    openings and panels, drawn by the same painters as the regions."""
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
        for item in ITEMS[wname]:
            s0, s1, z0, z1 = item_rect(wname, item)
            kind = item[0]
            if kind == "win":
                paint_window(c, X(s0), Y(z0), LPPM, item[3][0], row_seq(item[3][1]),
                             pad=0)
            elif kind == "conc":
                c.paint(X(s0), X(s1), Y(z0), Y(z1), ID_CONC, 0.98, 0.95, height=0.0)
            elif kind == "letters":
                paint_letters(c, X(s0), Y(z0), (s1 - s0) * LPPM, (z1 - z0) * LPPM, LPPM)
            elif kind == "mouth":
                continue                    # weather() dusts it
            else:
                PAINTERS[kind](c, X(s0), Y(z0), LPPM, pad=0)


def paint_patches(c):
    """Flat cells for surfaces a whole face takes one colour from."""
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0),
        "soffit": (ID_SOFFIT, 0.90, 0.80),
        "cope_top": (ID_COPE, 1.02, 1.0),
        "conc": (ID_CONC, 0.96, 0.95),
        "duct": (ID_DUCT, 1.0, 0.95),
        "soot": (ID_SOOT, 1.0, 0.5),
        "felt": (ID_FELT, 1.0, 1.0),
        "rim": (ID_STACK, 0.9, 0.95),
        "gal_under": (ID_SHEET, 0.80, 0.85),
        "dark": (ID_DARK, 1.0, 0.8),
    }
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x - 2, x + w + 2, y - 2, y + h + 2, mid, sh, ao, height=0.0)


# ------------------------------------------------------------------ checks
def _brick_row(z):
    """The brick band row height *z* samples."""
    return BRICK_Y0 + (z - SLAB * slab_of(z)) * PPM


def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands, or
    run off the sheet, or the layout's numbers disagree."""
    rects = {"window": WINDOW, "bigdoor": BIGDOOR, "entrance": ENTRANCE,
             "service": SERVICE, "stack": STACK, "flue_end": FLUE_END,
             "flue_side": FLUE_SIDE, "bushing": BUSHING, "sq": SQWIN,
             "mouth": MOUTH, "letters": LETTERS, "deck_t": DECK_T, "deck_b": DECK_B,
             "gal_side": GAL_SIDE, "gal_top": GAL_TOP, "gal_end": GAL_END}
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
    W, H = win_size(REGION_COLS, REGION_ROWS)
    if (WINDOW[2], WINDOW[3]) != (m(W), m(H)):
        problems.append("the window region is not %s x %s m" % (W, H))
    for kind, (w, h) in SIZES.items():
        rx, ry, rw, rh = REGION[kind]
        if abs(rw - m(w)) > 1.0 or abs(rh - m(h)) > 1.0:
            problems.append("%s region is %d x %d px for a %.3f x %.3f m opening"
                            % (kind, rw, rh, w, h))
    if (FLUE_END[2], FLUE_END[3]) != (m(2.0), m(2.0)) or FLUE[1] - FLUE[0] != 2.0 \
            or FLUE[4] != 2.0 or (FLUE_SIDE[2], FLUE_SIDE[3]) != (m(FLUE[4]), m(FLUE[2])):
        problems.append("the flue's regions are not its faces")
    if abs(m(BAND_TOP) - BRICK_H) > 1e-6:
        problems.append("the brick band does not hold z 0 .. BAND_TOP")
    if abs(TONE_COURSES * COURSE - m(SLAB)) > 1e-6 or (ATLAS / TILE_Y) != m(SLAB):
        problems.append("the bond and the noise do not repeat every SLAB")
    if abs(BOND_ROWS / COURSE - round(BOND_ROWS / COURSE)) > 1e-9 or \
            round(BOND_ROWS / COURSE) % 2:
        problems.append("BOND_ROWS is not an even number of courses")
    if BAND_TOP - SLAB < Z_PLINTH + 0.6:
        problems.append("the upper slabs would sample the plinth's splash")
    if CONC_H != m(0.625) or COPE_H != m(COPING) or BUNK_H != m(BUNKER_WIN[1] - BUNKER_WIN[0]):
        problems.append("a band is not its element's size")
    # the brick regions continue the band's bond across their edges
    for name, kind, z0 in (("th_front", "letters", LETTERS_Z), ("bh_west", "mouth", MOUTH_Z),
                           ("bunker", "bunker", BUNKER_WIN[0])):
        rect = BUNK_Y0 if kind == "bunker" else REGION[kind][1]
        if (rect - _brick_row(z0)) % BOND_ROWS:
            problems.append("the %s region's rows are off the band's bond" % kind)
        if kind != "bunker" and slab_of(z0) != slab_of(z0 + SIZES[kind][1] - 1e-6):
            problems.append("the %s panel crosses a slab line" % kind)
    if (BUNK_Y0 + BUNK_H - _brick_row(BUNKER_WIN[1])) % BOND_ROWS:
        problems.append("the bunker band's top is off the bond above it")
    if m(BUNKER_PITCH) * round(ATLAS / m(BUNKER_PITCH)) != ATLAS:
        problems.append("the bunker's window pitch does not divide the band")
    if STACK[2] < 2 * STACK_R * math.sin(math.pi / 8) * SPPM or \
            STACK[3] < (STACK_TOP - Z_BD) * SPPM:
        problems.append("the stack region cannot hold a face")
    if GAL_SIDE[2] < (GAL_LEN / math.cos(math.radians(GAL_SLOPE))) * GPPM - 1 or \
            GAL_SIDE[3] < GAL_H * GPPM - 1 or GAL_TOP[3] < GAL_W * GPPM - 1 or \
            (GAL_END[2], GAL_END[3]) != (round(GAL_W * GPPM), round(GAL_H * GPPM)):
        problems.append("a gallery region cannot hold its face")
    if text_width() * CAP > SIZES["letters"][0] - 0.3:
        problems.append("the lettering does not fit its panel")
    for ename, (ex, ey, ew, eh) in ELEV.items():
        for wname, off in ELEV_WALLS[ename]:
            zb, zt = WALLS[wname][2:4]
            if (off + wall_len(wname)) * LPPM > ew + 1e-6 or \
                    (zt - ELEV_ZB[ename]) * LPPM > eh + 1e-6:
                problems.append("elevation %s cannot hold %s" % (ename, wname))
    for rect, o, box in ((DECK_T, DECK_T_O, (TH[0] - BURY, TH[1] + CO, TH[2] - CO, TH[3] + CO)),
                         (DECK_B, DECK_B_O, (BH[0] - CO, BH[1] + CO, BH[2] - CO, BH[3] + CO))):
        if box[0] < o[0] - 0.6 or box[2] < o[1] - 1e-6 or \
                (box[1] - o[0]) * DPPM > rect[2] + 1.0 or (box[3] - o[1]) * DPPM > rect[3]:
            problems.append("a deck region cannot hold its roof")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    Only the brick band's first 1.25 m is height from the ground for every
    wall; above it each 4 m slab samples the same rows again, so nothing
    that follows height goes there, only noise on the slab period (TILE_Y).
    The plant burns coal: a light film of coal dust lies on the coping and
    the gallery, heavier on the gallery's roof and on the wall under it, and
    soot on the stacks, the flue stub and the deck round them.
    """
    brick = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    steel = (ID_GALV, ID_DUCT, ID_DOOR, ID_HANDLE, ID_SHEET, ID_STACK, ID_PANEL)
    w = weathering.Weather(c, clean=(ID_GLASS, ID_PORC), steel=steel, tile_y=TILE_Y,
                           coal_dust=weathering.COAL_DUST)
    w.grime()
    w.fade((ID_FRAME, ID_DOOR, ID_SHEET, ID_LETTER, ID_STACK))
    w.wash(brick)
    w.plinth(0, ATLAS, BRICK_Y0, BRICK_Y0 + m(Z_PLINTH), (ID_PLINTH,))
    w.splash(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(1.25), brick,
             fall=0.14, speck_fall=0.16)
    w.bloom(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(1.2), brick,
            amount=0.10, fade=m(0.5))
    # the precast concrete: patchy dirt
    w.add("D", 0, ATLAS, CONC_Y0, CONC_Y0 + CONC_H, lambda Y, X, nz: 0.06 * nz("blotch"),
          (ID_CONC,))
    # the coping: runs down its face from the top arris, a film of coal dust
    y0, y1 = COPE_Y0, COPE_Y0 + COPE_H
    w.runs(0, ATLAS, y0, y1, (ID_COPE,), 0.14, fall=14.0)
    w.coal(0, ATLAS, y0 - PAD, y1 + PAD, lambda Y, X, nz: 0.06 + 0.10 * nz("big"),
           (ID_COPE,))
    # the windows: dirt standing on the bottom rails
    for x, y, rw, _ in (WINDOW, SQWIN):
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
    # the flue's blanking plate and casing: soot and rust, and soot runs
    # down the casing's sides from its top (U is up the side there)
    x, y, rw, rh = FLUE_END
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.22 * nz("blotch"),
          (ID_DUCT, ID_DARK, ID_HANDLE))
    w.add("R", x, x + rw, y, y + rh, lambda Y, X, nz: 0.14 * atlas.smoothstep(
        0.4, 1.6, nz("runs")), (ID_DUCT, ID_HANDLE))
    w.coal(x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, lambda Y, X, nz: (
        0.10 + 0.25 * np.exp(-(y + rh - Y) / 20.0)) * (0.6 + 0.4 * nz("blotch")), (ID_CONC,))
    x, y, rw, rh = FLUE_SIDE
    w.coal(x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, lambda Y, X, nz: (
        0.08 + 0.30 * np.exp(-(x + rw - X) / 26.0) * np.exp(-(y + rh - Y) / 40.0))
        * (0.6 + 0.4 * nz("blotch")), (ID_CONC,))
    # the gallery: a coal-plant's film of fines, thick on its roof, on the
    # sides' floor rail and toward the wall, where the conveyor's dust leaks
    x, y, rw, rh = GAL_SIDE
    w.coal(x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, lambda Y, X, nz: (
        0.08 + 0.10 * nz("big") + 0.30 * np.exp(-(Y - y) / 6.0)
        + 0.12 * np.clip((X - x) / rw, 0.0, 1.0)), (ID_SHEET,))
    w.runs(x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, (ID_SHEET,), 0.18, fall=30.0)
    x, y, rw, rh = GAL_TOP
    w.coal(x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, lambda Y, X, nz: (
        0.22 + 0.16 * nz("big") + 0.14 * np.clip((X - x) / rw, 0.0, 1.0)), (ID_SHEET,))
    x, y, rw, rh = GAL_END
    w.coal(x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, lambda Y, X, nz: (
        0.10 + 0.10 * nz("big") + 0.25 * np.exp(-(Y - y) / 8.0)), (ID_SHEET, ID_PANEL))
    # the wall under the gallery: dust falls from its floor, thickest under
    # it and fading to nothing at the panel's edges, so the band runs on
    x, y, rw, rh = MOUTH
    g0 = x + (wall_s("bh_west", GAL_Y + GAL_W / 2.0) - (wall_s("bh_west", GAL_Y)
                                                     - SIZES["mouth"][0] / 2.0)) * PPM
    g1 = g0 + GAL_W * PPM
    zg = y + (GAL_ZM - GAL_H / 2.0 - MOUTH_Z) * PPM      # the gallery's floor line

    def mouth(Y, X, nz):
        across = atlas.smoothstep(g0 - 18.0, g0 + 6.0, X) * atlas.smoothstep(g1 + 18.0, g1 - 6.0, X)
        edge = (atlas.smoothstep(x, x + 22.0, X) * atlas.smoothstep(x + rw, x + rw - 22.0, X)
                * atlas.smoothstep(y, y + 30.0, Y))
        fall = np.exp(-np.clip(zg - Y, 0.0, None) / 80.0)
        runs = 0.45 + 0.55 * atlas.smoothstep(-0.6, 1.2, nz("runs"))
        return np.clip(1.25 * across * edge * fall * runs, 0.0, 1.0)
    w.coal(x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, mouth, brick, dark=0.40)
    # the stacks: soot down from the mouth, rust under the flanges
    x, y, rw, rh = STACK
    top = y + (STACK_TOP - Z_BD) * SPPM
    w.coal(x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, lambda Y, X, nz: (
        0.10 + 0.55 * np.exp(-np.clip(top - Y, 0.0, None) / 22.0)
        * (0.6 + 0.4 * atlas.smoothstep(-0.5, 1.5, nz("runs")))), (ID_STACK,))
    w.add("R", x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, lambda Y, X, nz: 0.16
          * atlas.smoothstep(0.3, 1.6, nz("runs")), (ID_STACK,))
    # the decks: dirt in patches, soot round the stacks
    for rect in (DECK_T, DECK_B):
        x, y, rw, rh = rect
        w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.12 * nz("blotch"),
              (ID_FELT, ID_BALLAST))
    x, y, rw, rh = DECK_B
    for sx_, sy_ in STACKS:
        cx = x + (sx_ - DECK_B_O[0]) * DPPM
        cy = y + (sy_ - DECK_B_O[1]) * DPPM
        w.coal(cx - 20, cx + 20, cy - 20, cy + 20, lambda Y, X, nz, cx=cx, cy=cy: 0.45
               * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / 120.0), (ID_FELT, ID_BALLAST))
    w.coal(x, x + rw, y, y + rh, lambda Y, X, nz: 0.06 + 0.06 * nz("big"),
           (ID_FELT, ID_BALLAST, ID_COPE))
    # the LOD3 west elevation: the same dust under the gallery
    ex, ey, ew, eh = ELEV["west"]
    gx = ex + wall_s("bh_west", GAL_Y + GAL_W / 2.0) * LPPM
    gz = ey + (GAL_ZM - GAL_H / 2.0) * LPPM
    w.coal(gx - 1, gx + GAL_W * LPPM + 1, gz - 14, gz, lambda Y, X, nz: 0.7 * np.exp(
        -(gz - Y) / 4.5), brick)
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_brick(c)
    paint_conc_band(c)
    paint_cope_band(c)
    paint_pipe_band(c)
    paint_bunker_band(c)
    c.check_bands(BAND_IDS)
    paint_window(c, WINDOW[0], WINDOW[1], PPM, REGION_COLS, [0, 1, 2, 3])
    paint_sq(c, SQWIN[0], SQWIN[1], PPM)
    paint_bigdoor(c, BIGDOOR[0], BIGDOOR[1], PPM)
    paint_entrance(c, ENTRANCE[0], ENTRANCE[1], PPM)
    paint_service(c, SERVICE[0], SERVICE[1], PPM)
    paint_flue_end(c, FLUE_END[0], FLUE_END[1], PPM)
    paint_flue_side(c)
    paint_bushing(c, BUSHING[0], BUSHING[1], PPM)
    paint_letters_region(c)
    paint_mouth(c)
    paint_gallery(c)
    paint_stack(c)
    paint_decks(c)
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
    sheet = np.isin(c.mid, (ID_DOOR, ID_FRAME, ID_DUCT, ID_SHEET, ID_STACK))
    grain = nz(5, 60.0, 0.35)
    c.shade[sheet] *= 1.0 + 0.016 * grain[sheet]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_CONC, ID_MORTAR, ID_SOFFIT, ID_COPE))
    pores = nz(9, 0.8)
    c.shade[mineral] *= 1.0 + 0.03 * pores[mineral]
    c.height[mineral] += 0.0006 * pores[mineral]
    conc = np.isin(c.mid, (ID_CONC, ID_COPE))
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


# Whether the LOD3 elevations keep their glass at glazing.BASE, box-filtered
# with its bars, instead of glazing.rooms() (Texture set, notes.md).
ELEV_BASE_GLASS = True


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
        # In the 6 px/m elevations a pane is a few pixels and most pixels
        # are part glass, part bar, so rooms() would repaint whole pixels and
        # drop the bars mixed into them. There the glass keeps glazing.BASE,
        # box-filtered with its frame and bars.
        if ELEV_BASE_GLASS:
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
