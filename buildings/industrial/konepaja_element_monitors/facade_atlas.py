# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
konepaja_element_monitors.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
the plan, the bays, every height, light and opening sizes, region rectangles --
so a change here cannot leave the UVs pointing at the wrong artwork.

The atlas is a trim sheet. Three bands run the full width and tile in U:

    y    0 ..  480   AGG      z 0 .. 7.5 m of the precast walls: the cast
                              plinth, then exposed-aggregate panels 2.67 m
                              wide with a smooth column cover over every
                              other joint (one bay, 5.33 m), and in every
                              bay the hall's high window, 4 lights at
                              z 5.0 .. 6.0. Three bays to the 16 m wrap.
    y  496 ..  560   FASCIA   the dark profiled-sheet fascia, 1.0 m, V from
                              its foot to its top flashing; lower fascias
                              sample its upper rows
    y  576 ..  776   OFFICE   the office's smooth panels, one storey band
                              3.125 m tall that both storeys sample
    y  792 ..  ...   unique   the roof plan, the entrance bay's modules, the
                              truck door's sections, the service door, the
                              ribbon and strip lights, the monitor lights, the
                              flue, the fans, the air handler, the lettering,
                              the dome, patches

The hall's windows are painted into the AGG band: every bay of the hall has
one, at the same place in the bay, so the walls of the flat tiers are plain
quads and the cut tiers' recessed glass samples the same pixels.

The roof plan is one region at DPPM over the whole 32 x 24 m plan: every deck
and every monitor top samples it at its own plan position, and the flat tiers'
domes are painted on it.

Rasterising is scripts/atlas.py's; weathering is scripts/weathering.py's,
placed by weather() below; glass is scripts/glazing.py's.
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

ASSET = "konepaja_element_monitors"
ATLAS = 1024
PPM = 64.0
DPPM = 8.0              # the roof plan
SPPM = 32.0             # the flue, the fans and the air handler
OPPM = 24.0             # the dome's top
PAD = 2                 # rows each band paints beyond its own edge

# ------------------------------------------------------------------ plan
# Blender frame, front (street) toward -Y. The production hall fills the back
# 32 x 16 m; in front of it the office nose at the west street corner and
# the single-storey staff and stores strip east of it, both 8 m deep.
HX, HY = 16.0, 12.0
Y_HALL = -4.0           # the hall's front wall; the front band before it
BAY = 16.0 / 3.0        # 5.333 m: the column grid, a column cover per bay
PANEL = BAY / 2.0       # 2.667 m precast panels
OX1 = -HX + 2.5 * BAY   # -2.667: the office's east wall, the strip's west end

# ------------------------------------------------------------ heights (m)
Z_PLINTH = 0.75         # 48 px: the cast plinth under every wall
# the hall: panels to the fascia's soffit, the fascia to its flashing, the
# deck sunk inside it
Z_EAVE, Z_TOP, Z_DECK = 7.5, 8.5, 8.25
# the office nose and the strip, likewise
OZ_EAVE, OZ_TOP, OZ_DECK = 6.375, 7.125, 6.875
SZ_EAVE, SZ_TOP, SZ_DECK = 3.5, 4.125, 3.875
FAS_OUT = 0.09375       # 6 px: the fascia stands proud of the panels
FAS_IN = 0.3125         # and runs this far in over the wall head
FAS_H = 1.0             # the fascia band: the hall's whole fascia

# the hall's high windows, one per bay, painted into the AGG band
Z_HSILL, Z_HHEAD = 5.0, 6.0
HWIN_W = 4.0
HWIN_IN = (BAY - HWIN_W) / 2.0          # from the bay's column line
H_LIGHTS = 4
# the hall's south wall over the strip has no windows: it samples the band
# HALL_SOUTH_V lower, so only plain panel rows reach it
HALL_SOUTH_V = 3.375

# the strip's windows: 4 lights of 1.0 m, centred in their bay
Z_SSILL, Z_SHEAD = 1.25, 2.25
S_LIGHT = 1.0

# the office: two storeys over a 10 cm threshold
O_FLOOR = 0.15625       # 10 px
ZL = 3.3125             # where the wall changes from the lower storey's
                        # band to the upper's, under the first floor
O_FLOOR2 = 3.4375       # 3.28 m storey
O_SILL1, O_SILL2 = 1.0625, 4.34375      # 0.906 m over each floor
O_WIN_H = 1.1875        # 76 px ribbon
O_LIGHT = 1.25          # 80 px lights
# the office band: lower storey V = z - OB_LOWER, upper V = z - ZL
OB_LOWER = 0.1875
OB_H = 3.125

# the entrance bay on the office front: a glazed bay from the threshold to
# under the fascia, split into modules (bottom, top) that each sample one
# region: the doors, the transom and floor spandrel, then stair glazing twice
E_X0, E_X1 = -5.75, -3.25
E_MODS = (O_FLOOR, 2.40625, 3.53125, 4.78125, 6.03125)
E_REGIONS = ("ent_a", "ent_b", "ent_c", "ent_c")
Z_LEAF = 2.1875         # the leaves over the threshold
E_FRAME, E_SIDE, E_MULL = 4, 20, 4      # px across the bay: frame, side light
E_LEAF_PX = (160 - 2 * E_FRAME - 2 * E_SIDE - 2 * E_MULL) / 2.0   # 52 px each
# the canopy over it, cantilevered from the first-floor slab
CANOPY = (-6.25, -2.75, 1.5)            # x0, x1, projection
Z_CAN0, Z_CAN1 = 3.03125, 3.28125

# the truck door: a sectional door of six 0.65 m sections, a row of small
# windows in the fifth, 2.6 .. 3.25 m
TD_W, TD_H = 3.3125, 3.9
TD_SECS = 6
TD_SEC = TD_H / TD_SECS
TD_WIN_SEC = 4
# personnel doors: the opening, and its steel frame each side and over it
SD_W, SD_H = 1.0625, 2.1875
SD_FRAME = 0.0625

# monitors: three rooflights along the hall, on the column lines
MON_X = (-2.0 * BAY, 0.0, 2.0 * BAY)
MON_W = 2.5
MON_Y0 = Y_HALL + 1.75
MON_LIGHT = 1.25
MON_N = 10
MON_H = 1.25            # over the deck
MON_UP = 0.25           # its sheeted upstand, then glazing, then fascia
MON_GLASS_TOP = 1.0625
MON_SLOPE_IN = 0.45     # the glazing leans in this far from the upstand to the top

# domes: two rows between the monitors
DOME_X = (-BAY, BAY)
DOME_Y = (-0.75, 2.25, 5.25, 8.25)
DOME_HALF = 0.65        # the kerb's half side
DOME_TOP = 0.3125       # the kerb, over the deck
DOME_RISE = 0.25        # the dome over the kerb
DOME_CROWN = 0.3        # the crown's half side

# ------------------------------------------------------------------- rows
AGG_Y0, AGG_H = 0, 480
FAS_Y0, FAS_PX = 496, 64
OFF_Y0, OFF_PX = 576, 200
UNI_Y = 792
# The ladder and its cage take the fascia's colour from its top flashing,
# where nothing runs across them.
PIPE_STRIP = (FAS_Y0 + FAS_PX - 6, FAS_Y0 + FAS_PX - 2)
FLASH_PX = 7            # the flashing's folded top, rows

RIB_W = 0.4             # the column cover
RIB_H = 0.03            # its arrises, proud of the panels
JOINT_PX = 1.25         # a sealed panel joint
SHEET_PITCH = 0.2       # the fascia's profile

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels, at PPM unless noted.
PLAN = (4, 796, 256, 192)               # 32 x 24 m at DPPM
MONLO = (4, 994, 100, 10)               # a monitor's side at DPPM, flat tiers
LPPM = 12.0             # the office ribbons on LOD3
RIB7LO = (4, 1008, 105, 14)             # a seven-light ribbon at LPPM
RIB5LO = (944, 942, 75, 14)             # a five-light one
ENT_A = (266, 796, 160, 144)            # 2.5 x 2.25 m: the doors
ENT_B = (266, 946, 160, 72)             # 2.5 x 1.125 m: transom, spandrel
ENT_C = (432, 796, 160, 80)             # 2.5 x 1.25 m: stair glazing
OFF_L = (432, 882, 80, 76)              # one ribbon light, 1.25 x 1.1875 m
MON_L = (516, 882, 80, 80)              # one monitor light, 1.25 x 1.25 m
FAN_S = (432, 968, 92, 24)              # a fan's side round, at SPPM
FAN_T = (530, 968, 32, 32)              # its cowl from above, 1.0 m at SPPM
DOME = (566, 968, 32, 32)               # 1.333 m at OPPM
TRUCK = (602, 796, 212, 84)             # a plain section, then the windowed one
STACK = (602, 886, 224, 64)             # the flue at SPPM: U up it, V round it
STRIP_L = (820, 796, 64, 64)            # one strip light, 1.0 x 1.0 m
AHU_E = (888, 796, 56, 48)              # the air handler's end, at SPPM
SERVICE = (952, 796, 68, 140)           # a personnel door, 1.0625 x 2.1875 m
AHU_S = (832, 886, 104, 48)             # its side, at SPPM
LETTERS = (602, 970, 352, 48)           # 5.5 x 0.75 m of the office fascia

REGION = {"ent_a": ENT_A, "ent_b": ENT_B, "ent_c": ENT_C, "off_l": OFF_L,
          "mon_l": MON_L, "strip_l": STRIP_L, "truck": TRUCK, "service": SERVICE}

PATCH_NAMES = ("blank", "reveal", "sill", "soffit", "cap", "upstand", "kerb",
               "monend", "rim", "soot", "galv", "conc", "felt", "fasend",
               "door_reveal", "duct", "stack")
_PATCH_SLOTS = ([(114 + 20 * i, 994) for i in range(7)]
                + [(432 + 20 * i, 1004) for i in range(8)]
                + [(832 + 20 * i, 944) for i in range(5)]
                + [(958 + 20 * i, 974) for i in range(3)]
                + [(958 + 20 * i, 998) for i in range(3)])
PATCHES = {n: _PATCH_SLOTS[i] + (16, 16) for i, n in enumerate(PATCH_NAMES)}

# the plant on the hall's deck
STACK_AT = (-13.8, 9.25)
STACK_R = 0.3           # across the flats / 2
STACK_TOP = Z_DECK + 7.0                # 15.25: 6.75 m over the fascia
STACK_WALL = 0.04
STACK_DEPTH = 1.0
STACK_GUY = 12.75       # the guy collar
STACK_CAP = 0.12        # the rolled ring at the rim
GUY_R = 1.6             # the guys' feet, out from the axis
GUY_ANGLES = (90.0, 210.0, 330.0)
FANS = [(-13.75, 1.5), (13.75, 8.5), (BAY, 10.75)]
FAN_R, FAN_H = 0.4, 0.6                 # the body, across the flats / 2
FAN_CAP_R, FAN_CAP_H = 0.5, 0.15        # the cowl over it
AHU = (13.0, 14.75, 1.0, 4.25)          # x0, x1, y0, y1
AHU_H = 1.5
# internal rainwater outlets, plan (x, y)
OUTLETS = [(-BAY * 1.5, 3.0), (BAY * 1.5, 3.0), (-BAY * 0.5, 10.5),
           (BAY * 0.5, -2.5), (-9.0, -8.0), (7.0, -8.0)]

# the lettering on the office's front fascia: its left edge on a sheet rib
TEXT = "KONEPAJA"
LET_X0 = -13.25 - ((-13.25 + HX + FAS_OUT) % SHEET_PITCH)
LET_X1 = LET_X0 + LETTERS[2] / PPM
CAP = 0.5               # cap height
STROKE = 0.15           # in cap heights
TRACK = 0.26
GLYPH_W = {"K": 0.72, "O": 0.9, "N": 0.78, "E": 0.62, "P": 0.68, "A": 0.84,
           "J": 0.56}

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_AGG, ID_STONE_D, ID_STONE_L, ID_SEAL = 0, 1, 2, 3, 4, 5
ID_RIB, ID_FRAME, ID_GLASS, ID_SILL, ID_FASCIA, ID_OPANEL = 6, 7, 8, 9, 10, 11
ID_DECK, ID_LAP, ID_DOOR, ID_SDOOR, ID_HANDLE, ID_DARK = 12, 13, 14, 15, 16, 17
ID_DOME, ID_KERB, ID_STACK, ID_SOOT, ID_GALV, ID_LOUVRE = 18, 19, 20, 21, 22, 23
ID_LETTER, ID_CONC, ID_GROUT, ID_SOFFIT, ID_RUBBER, ID_SPANDREL = 24, 25, 26, 27, 28, 29
ID_LADDER, ID_MONTOP, ID_ALU = 30, 31, 32

# (roughness, metallic)
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_AGG: (0.93, 0.0),
    ID_STONE_D: (0.80, 0.0), ID_STONE_L: (0.78, 0.0), ID_SEAL: (0.88, 0.0),
    ID_RIB: (0.86, 0.0), ID_FRAME: (0.45, 0.0), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_SILL: (0.48, 0.0), ID_FASCIA: (0.52, 0.0), ID_OPANEL: (0.80, 0.0),
    ID_DECK: (0.93, 0.0), ID_LAP: (0.90, 0.0), ID_DOOR: (0.50, 0.0),
    ID_SDOOR: (0.50, 0.0), ID_HANDLE: (0.32, 0.85), ID_DARK: (0.96, 0.0),
    ID_DOME: (0.30, 0.0), ID_KERB: (0.55, 0.0), ID_STACK: (0.62, 0.15),
    ID_SOOT: (0.97, 0.0), ID_GALV: (0.42, 0.65), ID_LOUVRE: (0.48, 0.55),
    ID_LETTER: (0.40, 0.0), ID_CONC: (0.90, 0.0), ID_GROUT: (0.92, 0.0),
    ID_SOFFIT: (0.70, 0.0), ID_RUBBER: (0.90, 0.0), ID_SPANDREL: (0.55, 0.0),
    ID_LADDER: (0.55, 0.0), ID_MONTOP: (0.90, 0.0), ID_ALU: (0.38, 0.70),
}

# ---------------------------------------------------------------- palettes
# Three cladding schemes, each one coherent treatment of the whole works:
# the aggregate (matrix, dark and light stones), its smooth column covers,
# the fascia (with the monitors' and kit's sheet), the window and door
# frames, the office's smooth panels and the doors. The plinth, the felt,
# the glass, the flue and the plant are fixed. All three share the ORM and
# normal maps: only colour changes, never the surface.
VARIANTS = {
    "grey_aggregate": {"agg": (150, 148, 142), "stone_d": (104, 102, 98),
                       "stone_l": (192, 190, 184), "rib": (164, 162, 156),
                       "fascia": (74, 56, 45), "frame": (66, 52, 43),
                       "opanel": (206, 204, 196), "door": (88, 70, 56),
                       "sdoor": (78, 62, 50)},
    "beige_aggregate": {"agg": (172, 162, 142), "stone_d": (134, 118, 98),
                        "stone_l": (202, 194, 174), "rib": (180, 172, 156),
                        "fascia": (108, 62, 48), "frame": (136, 76, 52),
                        "opanel": (208, 204, 192), "door": (112, 68, 50),
                        "sdoor": (102, 62, 48)},
    "red_aggregate": {"agg": (136, 114, 104), "stone_d": (96, 74, 66),
                      "stone_l": (168, 150, 140), "rib": (150, 136, 128),
                      "fascia": (60, 62, 64), "frame": (176, 176, 172),
                      "opanel": (196, 194, 188), "door": (74, 78, 80),
                      "sdoor": (66, 70, 72)},
}
DEFAULT_VARIANT = "grey_aggregate"

FIXED = {
    ID_BLANK: (52, 52, 52), ID_PLINTH: (128, 127, 122), ID_SEAL: (70, 70, 70),
    ID_GLASS: glazing.BASE, ID_SILL: (120, 122, 122), ID_DECK: (96, 95, 91),
    ID_LAP: (88, 87, 84), ID_HANDLE: (168, 168, 166), ID_DARK: (24, 24, 24),
    ID_DOME: (204, 204, 198), ID_KERB: (128, 130, 130), ID_STACK: (58, 58, 60),
    ID_SOOT: (22, 21, 20), ID_GALV: (148, 150, 148), ID_LOUVRE: (128, 130, 129),
    ID_LETTER: (222, 220, 212), ID_CONC: (160, 158, 152), ID_GROUT: (176, 174, 168),
    ID_SOFFIT: (176, 174, 168), ID_RUBBER: (30, 30, 30), ID_SPANDREL: (46, 46, 48),
    ID_LADDER: (150, 152, 150), ID_ALU: (168, 170, 170),
}

BAND_IDS = {
    "AGG": ((0, AGG_H + PAD), {ID_PLINTH, ID_AGG, ID_STONE_D, ID_STONE_L, ID_SEAL,
                               ID_RIB, ID_FRAME, ID_GLASS, ID_SILL, ID_GROUT}),
    "FASCIA": ((FAS_Y0 - PAD, FAS_Y0 + FAS_PX + PAD), {ID_FASCIA}),
    "OFFICE": ((OFF_Y0 - PAD, OFF_Y0 + OFF_PX + PAD), {ID_OPANEL, ID_SEAL}),
}

# The candidate-glazing mask is the emission map, neutral white. The domes'
# opal shells glow at a third of the glazing's level, neutral too.
EMIT = {ID_GLASS: (255, 255, 255), ID_DOME: (150, 150, 150)}
# Linear RGB: a workshop under fluorescent and high-bay lamps, a little
# cooler than the catalog's offices.
LIT_FACTOR = (1.0, 0.92, 0.80)

# ---------------------------------------------------------------- relief
STONE_H = 0.003         # the exposed stones, proud of the matrix
SEAL_H = -0.008         # a sealed joint's recess
FRAME_H = 0.030         # window frames and mullions, proud of the glass
SASH_H = 0.042
DOOR_FRAME_H = 0.025
SHEET_H = 0.028         # the fascia's trapezoidal ribs
LETTER_H = 0.015
SILL_H = 0.03


def m(v):
    """Metres -> pixels."""
    return v * PPM


def wrap_spans(x0, x1, shifts=False):
    """[x0, x1) in atlas pixels split at the U wrap, for features that
    straddle it in a tiling band; with *shifts*, each span's offset too."""
    out = []
    for k in (-1, 0, 1):
        a, b = x0 + k * ATLAS, x1 + k * ATLAS
        a, b = max(a, 0.0), min(b, float(ATLAS))
        if b > a:
            out.append((a, b, k * ATLAS) if shifts else (a, b))
    return out


def bay_window(k):
    """(u0, u1) in metres along the band of bay *k*'s window."""
    u0 = k * BAY + HWIN_IN
    return u0, u0 + HWIN_W


# ================================================================== bands
def paint_agg(c):
    """The precast wall band: the cast plinth, then exposed-aggregate panels
    -- a pale matrix full of dark and light stones, each a little proud --
    with a sealed joint every PANEL, a smooth column cover over every other
    joint, lifting-anchor patches at each panel's head, and the hall's high
    window in every bay."""
    y0, top = AGG_Y0, AGG_Y0 + AGG_H + PAD
    yp = y0 + m(Z_PLINTH)
    c.paint(0, ATLAS, y0 - PAD, top, ID_AGG, 1.0, 1.0, height=0.0)
    # the aggregate: two fine fields pick the stones and their colour
    sy, sx, Y, X = c.field(0, ATLAS, yp, top)
    pick = atlas.noise(c, 21, 0.42)[sy, sx]
    tone = atlas.noise(c, 22, 0.55)[sy, sx]
    size = atlas.noise(c, 23, 1.6)[sy, sx]
    stone = pick > 0.55 - 0.25 * size
    dark = stone & (tone > 0.15)
    light = stone & (tone < -0.55)
    c.mid[sy, sx] = np.where(dark, ID_STONE_D, np.where(light, ID_STONE_L, ID_AGG))
    c.shade[sy, sx] = np.where(stone, 0.92 + 0.16 * atlas.smoothstep(-1.5, 1.5, tone),
                               0.97 + 0.06 * atlas.smoothstep(-2, 2, size))
    c.height[sy, sx] = np.where(stone, STONE_H * atlas.smoothstep(0.55, 1.6, pick), 0.0)
    c.ao[sy, sx] = np.where(stone, 1.0, 0.90)
    # each element cast on its own day: a slightly different tone
    n_pan = int(round(16.0 / PANEL))
    k_pan = np.floor(((X / PPM) % 16.0) / PANEL).astype(np.int64) % n_pan
    c.shade[sy, sx] *= 1.0 + 0.05 * (atlas.hash_unit(k_pan, 7) - 0.5)
    paint_plinth(c)
    # panel joints, sealed, the panels' arrises a little darker either side
    for k in range(int(round(16.0 / PANEL))):
        u = m(k * PANEL)
        for a, b in wrap_spans(u - 3.0, u + 3.0):
            c.mul(a, b, yp, top, 0.97, ao=0.92)
        for a, b in wrap_spans(u - JOINT_PX / 2.0, u + JOINT_PX / 2.0):
            c.paint(a, b, yp, top, ID_SEAL, 1.0, 0.70, height=SEAL_H)
    # column covers over every other joint: smooth cast strips, arrises lit
    w = m(RIB_W)
    for k in range(3):
        u = m(k * BAY)
        for a, b, k_ in wrap_spans(u - w / 2.0, u + w / 2.0, shifts=True):
            c.paint(a, b, yp, top, ID_RIB, 1.0, 1.0)
            _bevel_x(c, a, b, u - w / 2.0 + k_, u + w / 2.0 + k_, yp, top, RIB_H, 2.0)
        sy, sx, Y, X = c.field(0, ATLAS, yp, top)
        d = np.abs(((X - u + ATLAS / 2.0) % ATLAS) - ATLAS / 2.0)
        cover = d < w / 2.0
        form = atlas.noise(c, 24, 30.0, 2.0)[sy, sx]
        c.shade[sy, sx] = np.where(cover, c.shade[sy, sx] * (1.0 + 0.02 * form),
                                   c.shade[sy, sx])
        for e in (u - w / 2.0, u + w / 2.0):         # its own sealed joints
            for a, b in wrap_spans(e - 0.6, e + 0.6):
                c.paint(a, b, yp, top, ID_SEAL, 1.0, 0.72, height=0.0)
    # lifting anchors near each panel's head, filled with grout
    for k in range(int(round(16.0 / PANEL))):
        for du in (0.45, PANEL - 0.45):
            u = m(k * PANEL + du)
            if _near_rib(u, w / 2.0 + 4):
                continue
            yy = y0 + m(7.05)
            c.paint(u - 2.5, u + 2.5, yy - 2.0, yy + 2.0, ID_GROUT, 1.0, 0.9,
                    height=-0.002)
    # the hall's window in every bay
    for k in range(3):
        paint_hall_window(c, k)
    # the fascia's shadow line under its drip, and the wall head
    yd = y0 + m(Z_EAVE)
    c.mul(0, ATLAS, yd - 3, yd + PAD, 0.84, ao=0.78)
    c.mul(0, ATLAS, yd - 7, yd - 3, 0.95, ao=0.90)


def _near_rib(u, half):
    for k in range(4):
        if abs(u - m(k * BAY)) < half:
            return True
    return False


def _bevel_x(c, a, b, e0, e1, y0, y1, h, w):
    """Height *h* over [a, b) ramping from 0 over *w* px at e0 and e1."""
    sy, sx, Y, X = c.field(a, b, y0, y1)
    d = np.minimum(X - e0, e1 - X)
    c.height[sy, sx] = h * np.clip(d / w, 0.0, 1.0)


def paint_plinth(c):
    """The cast plinth: smooth grey concrete, darker toward the ground,
    formwork tie holes, a chamfered top with a drip line over it."""
    y0, h = AGG_Y0, m(Z_PLINTH)
    c.paint(0, ATLAS, y0 - PAD, y0 + h, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h)
    z = np.clip((Y - y0) / PPM, 0.0, None)
    c.shade[sy, sx] *= 0.86 + 0.14 * np.clip(z / 0.3, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.25, 0, 1))
    form = atlas.noise(c, 25, 40.0, 1.5)[sy, sx]
    c.shade[sy, sx] *= 1.0 + 0.025 * form
    for k in range(int(round(16.0 / PANEL))):
        u = m(k * PANEL)
        for a, b in wrap_spans(u - 0.6, u + 0.6):
            c.paint(a, b, y0, y0 + h, ID_PLINTH, 0.86, 0.80, height=-0.004)
        for du in (0.6, PANEL / 2.0, PANEL - 0.6):
            x = m(k * PANEL + du)
            c.disc(x, y0 + m(0.42), 0.9, ID_PLINTH, 0.78, 0.8, height=-0.004)
    c.bevel(0, ATLAS, y0 + h - 4, y0 + h, 0.012, 2.0, axes="y")
    c.mul(0, ATLAS, y0 + h - 1, y0 + h + 1, 0.84, ao=0.80)


MULL = 1.5              # half a mullion each side of a light, px
HEAD, FOOT = 4, 5       # head and bottom rails, px


def _bar(c, a0, a1, b0, b1, mid=ID_FRAME, h=FRAME_H, ao=0.86, shade=1.0, axes="xy"):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, 1.0, axes=axes)


def _light(c, a0, a1, b0, b1):
    """A pane in its frame, the head rail occluding its top."""
    c.paint(a0, a1, b0, b1, ID_GLASS, 1.0, 0.92, height=0.0)
    c.mul(a0, a1, b1 - 3, b1, 0.92, ao=0.86)


def _sash(c, a0, a1, b0, b1, inset=3):
    c.paint(a0, a1, b0, b1, ID_FRAME, 0.9)
    c.bevel(a0, a1, b0, b1, SASH_H, 1.0, base=FRAME_H)
    _light(c, a0 + inset, a1 - inset, b0 + inset, b1 - inset)


def paint_hall_window(c, k):
    """Bay *k*'s high window in the AGG band: four lights in one frame, a
    top-hung vent over the second, a pressed sill flashing under it and the
    panel's arris shading round it."""
    u0, u1 = bay_window(k)
    x0, x1 = m(u0), m(u1)
    y0, y1 = AGG_Y0 + m(Z_HSILL), AGG_Y0 + m(Z_HHEAD)
    c.paint(x0, x1, y0, y1, ID_FRAME, 1.0, 1.0, height=FRAME_H)
    c.bevel(x0, x1, y0, y1, FRAME_H, 1.0)
    pitch = (x1 - x0) / H_LIGHTS
    for i in range(H_LIGHTS):
        a0 = x0 + i * pitch + (3 if i == 0 else MULL)
        a1 = x0 + (i + 1) * pitch - (3 if i == H_LIGHTS - 1 else MULL)
        b0, b1 = y0 + FOOT, y1 - HEAD
        if i == 1:
            yt = b1 - 22
            _light(c, a0, a1, b0, yt)
            _bar(c, a0, a1, yt, yt + 2, axes="y")
            _sash(c, a0, a1, yt + 2, b1)
        else:
            _light(c, a0, a1, b0, b1)
    # the sill flashing, a little wider than the frame, and its shadow
    c.paint(x0 - 3, x1 + 3, y0 - 4, y0, ID_SILL, 1.0, 1.0, height=SILL_H)
    c.bevel(x0 - 3, x1 + 3, y0 - 4, y0, SILL_H, 1.0, axes="y")
    c.mul(x0 - 3, x1 + 3, y0 - 6, y0 - 4, 0.82, ao=0.76)
    # the reveal's occlusion just inside the panel's edge
    c.mul(x0, x1, y1 - 3, y1, 0.84, ao=0.78)
    c.mul(x0, x0 + 2, y0, y1, 0.90, ao=0.84)
    c.mul(x1 - 2, x1, y0, y1, 0.90, ao=0.84)


def paint_fascia(c):
    """The fascia: dark profiled steel sheet, trapezoidal ribs every
    SHEET_PITCH, a drip at its foot and a folded flashing over its top,
    which the ladder samples."""
    y0, h = FAS_Y0, FAS_PX
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_FASCIA, 1.0, 1.0, height=0.0)
    _sheet(c, 0, ATLAS, y0, y0 + h - FLASH_PX, 0.0)
    _flashing(c, 0, ATLAS, y0 + h - FLASH_PX, y0 + h + PAD)
    c.paint(0, ATLAS, y0 - PAD, y0 + 1.5, ID_FASCIA, 0.80, 0.82, height=0.0)


def _sheet(c, x0, x1, y0, y1, phase):
    """Trapezoidal sheet ribs across [x0, x1), the first crest *phase* px
    from x0."""
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    p = m(SHEET_PITCH)
    t = ((X - x0 - phase) % p) / p
    crest = np.clip(1.0 - np.abs(t - 0.5) / 0.16, 0.0, 1.0)
    prof = np.clip((0.34 - np.abs(t - 0.5)) / 0.10, 0.0, 1.0)
    c.height[sy, sx] = SHEET_H * prof
    c.shade[sy, sx] *= 0.96 + 0.06 * crest
    flank = (np.abs(t - 0.5) > 0.24) & (np.abs(t - 0.5) < 0.34)
    c.ao[sy, sx] = np.where(np.abs(t - 0.5) > 0.34, 0.88,
                            np.where(flank, 0.94, 1.0))


def _flashing(c, x0, x1, y0, y1):
    c.paint(x0, x1, y0, y1, ID_FASCIA, 1.04, 1.0, height=0.008)
    c.mul(x0, x1, y0, y0 + 1, 0.80, ao=0.80)


def paint_office_band(c):
    """The office's smooth panels: one storey band, a sealed floor joint at
    its foot, vertical joints every 2 m, a faint formwork float."""
    y0, h = OFF_Y0, OFF_PX
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_OPANEL, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    float_ = atlas.noise(c, 31, 50.0, 6.0)[sy, sx]
    pores = atlas.noise(c, 32, 0.7)[sy, sx]
    c.shade[sy, sx] *= 1.0 + 0.015 * float_ + 0.012 * pores
    c.height[sy, sx] += 0.0003 * pores
    for k in range(8):
        u = m(2.0 * k)
        for a, b in wrap_spans(u - 0.7, u + 0.7):
            c.paint(a, b, y0 - PAD, y0 + h + PAD, ID_SEAL, 1.0, 0.72, height=SEAL_H)
        for a, b in wrap_spans(u - 2.5, u + 2.5):
            c.mul(a, b, y0 - PAD, y0 + h + PAD, 0.985)
    c.paint(0, ATLAS, y0 - PAD, y0 + 1.0, ID_SEAL, 1.0, 0.72, height=SEAL_H)
    c.mul(0, ATLAS, y0 + 1.0, y0 + 3.0, 0.97, ao=0.92)


# ================================================================= regions
def paint_ribbon_light(c, rect, vent=0.375):
    """One ribbon light of the office: a fixed pane and a side-hung vent
    *vent* m wide at its left, in the variant's frames."""
    x, y, w, h = rect
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 1.0, height=FRAME_H)
    c.bevel(x - 2, x + w + 2, y, y + h, FRAME_H, 1.0, axes="y")
    a0, a1, b0, b1 = x + 2, x + w - 2, y + FOOT, y + h - HEAD
    s1 = a0 + m(vent)
    _sash(c, a0, s1, b0, b1)
    _bar(c, s1, s1 + 2, b0, b1, axes="x")
    _light(c, s1 + 2, a1, b0, b1)
    for a in (x, x + w):
        c.mul(a - 0.5, a + 0.5, y + FOOT, y + h - HEAD, 0.9, ao=0.88)
    c.mul(x, x + w, y, y + 2, 0.9, ao=0.86)


def paint_strip_light(c):
    """One light of the strip's windows: a fixed pane in the frame."""
    x, y, w, h = STRIP_L
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 1.0, height=FRAME_H)
    c.bevel(x - 2, x + w + 2, y, y + h, FRAME_H, 1.0, axes="y")
    _light(c, x + 2, x + w - 2, y + FOOT, y + h - HEAD)
    for a in (x, x + w):
        c.mul(a - 0.5, a + 0.5, y + FOOT, y + h - HEAD, 0.9, ao=0.88)


def paint_monitor_light(c):
    """One light of a monitor's side, 1.25 m square: the sheeted upstand,
    the glazing in aluminium frames, the fascia over it."""
    x, y, w, h = MON_L
    up, gt = m(MON_UP), m(MON_GLASS_TOP)
    c.paint(x, x + w, y, y + up, ID_KERB, 1.0, 1.0, height=0.0)
    _sheet(c, x, x + w, y, y + up - 2, 0.0)
    c.paint(x, x + w, y + up - 2, y + up, ID_SILL, 1.0, 1.0, height=0.01)
    c.paint(x, x + w, y + up, y + gt, ID_ALU, 1.0, 1.0, height=FRAME_H)
    c.bevel(x - 2, x + w + 2, y + up, y + gt, FRAME_H, 1.0, axes="y")
    _light(c, x + 2.5, x + w - 2.5, y + up + 4, y + gt - 4)
    for a in (x, x + w):
        c.mul(a - 0.5, a + 0.5, y + up + 4, y + gt - 4, 0.9, ao=0.88)
    c.paint(x, x + w, y + gt, y + h, ID_FASCIA, 1.0, 1.0, height=0.0)
    c.mul(x, x + w, y + gt, y + gt + 1.5, 0.80, ao=0.80)
    c.paint(x, x + w, y + h - 2, y + h, ID_FASCIA, 1.06, 1.0, height=0.006)


def paint_monlo(c):
    """A monitor's whole side for the flat tiers, at DPPM: the same bands,
    a mullion every light."""
    x, y, w, h = MONLO
    k = DPPM
    c.paint(x - PAD, x + w + PAD, y - PAD, y + MON_UP * k, ID_KERB, 1.0, 1.0, height=0.0)
    c.paint(x - PAD, x + w + PAD, y + MON_UP * k, y + MON_GLASS_TOP * k, ID_GLASS, 1.0,
            0.92, height=0.0)
    c.paint(x - PAD, x + w + PAD, y + MON_GLASS_TOP * k, y + h + PAD, ID_FASCIA, 1.0, 1.0,
            height=0.0)
    for i in range(MON_N + 1):
        a = x + i * MON_LIGHT * k
        c.paint(a - 0.6, a + 0.6, y + MON_UP * k, y + MON_GLASS_TOP * k, ID_ALU, 1.0, 1.0)


def paint_riblo(c):
    """The office's ribbons for LOD3, whole, at LPPM: frame, glass, a mullion
    every light."""
    for rect, n in ((RIB7LO, 7), (RIB5LO, 5)):
        x, y, w, h = rect
        c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_FRAME, 1.0, 1.0, height=0.0)
        c.paint(x + 0.5, x + w - 0.5, y + 1.0, y + h - 1.0, ID_GLASS, 1.0, 0.92, height=0.0)
        for i in range(1, n):
            a = x + i * O_LIGHT * LPPM
            c.paint(a - 0.5, a + 0.5, y, y + h, ID_FRAME, 1.0, 1.0)


def paint_entrance(c):
    """The entrance bay's three modules, 2.5 m wide in a dark frame.

    A: the doors -- a pair of glazed leaves between narrow side lights, a
    deep kick rail, long pull bars. B: the transom light over the doors,
    then the floor's spandrel panel behind the canopy. C: a storey's stair
    glazing, a transom a third of the way up."""
    x, y, w, h = ENT_A
    F, S, M = E_FRAME, E_SIDE, E_MULL
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 1.0, height=DOOR_FRAME_H)
    for a0, a1 in ((x + F, x + F + S), (x + w - F - S, x + w - F)):
        _light(c, a0, a1, y + m(0.30), y + h - F)
        _bar(c, a0, a1, y, y + m(0.30), axes="y")
    l0 = x + F + S + M
    yl = y + m(Z_LEAF)
    for i in range(2):
        a0 = l0 + i * E_LEAF_PX
        a1 = a0 + E_LEAF_PX
        c.paint(a0, a1, y, yl, ID_FRAME, 0.94, 0.95, height=DOOR_FRAME_H + 0.01)
        c.bevel(a0, a1, y, yl, DOOR_FRAME_H + 0.01, 1.0)
        _light(c, a0 + 6, a1 - 6, y + m(0.40), yl - 6)
        c.paint(a0 + 2, a1 - 2, y + 2, y + 10, ID_ALU, 0.9, 0.9, height=0.04)
        hx = a1 - 4 if i == 0 else a0 + 4
        c.paint(hx - 1.2, hx + 1.2, y + m(0.85), y + m(1.45), ID_HANDLE, 1.0, 0.9,
                height=0.05)
    c.mul(l0 + E_LEAF_PX - 0.5, l0 + E_LEAF_PX + 0.5, y, yl, 0.6, ao=0.6)
    _bar(c, l0, l0 + 2 * E_LEAF_PX, yl, yl + 4, axes="y")
    _light(c, l0, l0 + 2 * E_LEAF_PX, yl + 4, y + h - F)
    _bar(c, x, x + w, y + h - F, y + h, axes="y")
    c.paint(x, x + w, y, y + 2, ID_ALU, 1.0, 0.9, height=0.01)     # threshold
    # B: the transom light, then the spandrel
    x, y, w, h = ENT_B
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 1.0, height=DOOR_FRAME_H)
    ys = y + m(3.0 - E_MODS[1])
    _light(c, x + F, x + w - F, y, ys - F)
    c.paint(x + F, x + w - F, ys, y + h, ID_SPANDREL, 1.0, 1.0, height=0.0)
    _bar(c, x, x + w, ys - F, ys, axes="y")
    for a in (x + F + S + M / 2.0, x + w - F - S - M / 2.0):
        _bar(c, a - M / 2.0, a + M / 2.0, y, ys - F, axes="x")
    # C: stair glazing
    x, y, w, h = ENT_C
    c.paint(x, x + w, y, y + h, ID_FRAME, 1.0, 1.0, height=DOOR_FRAME_H)
    yt = y + m(0.42)
    _light(c, x + F, x + w - F, y + F, yt)
    _bar(c, x, x + w, yt, yt + F, axes="y")
    _light(c, x + F, x + w - F, yt + F, y + h - F / 2.0)
    for a in (x + F + S + M / 2.0, x + w - F - S - M / 2.0):
        _bar(c, a - M / 2.0, a + M / 2.0, y, y + h, axes="x")
    _bar(c, x, x + w, y, y + F / 2.0, axes="y")
    _bar(c, x, x + w, y + h - F / 2.0, y + h, axes="y")


def paint_truck(c):
    """The truck door's two kinds of section, 3.3125 x 0.65 m each: steel,
    pressed with fine horizontal ribs, a rubber seal at the joint; the
    windowed one carries five small lights."""
    x, y, w, h = TRUCK
    sec = m(TD_SEC)
    for j in range(2):
        b0 = y + j * sec
        c.paint(x - PAD, x + w + PAD, b0, b0 + sec, ID_DOOR, 1.0, 1.0, height=0.0)
        sy, sx, Y, X = c.field(x - PAD, x + w + PAD, b0, b0 + sec)
        t = ((Y - b0) % m(0.1083)) / m(0.1083)
        c.height[sy, sx] = 0.004 * np.sin(np.pi * t)
        c.shade[sy, sx] *= 0.98 + 0.03 * np.sin(np.pi * t)
        c.paint(x - PAD, x + w + PAD, b0, b0 + 1.5, ID_RUBBER, 1.0, 0.7, height=-0.004)
        c.mul(x - PAD, x + w + PAD, b0 + 1.5, b0 + 3, 0.9, ao=0.85)
        for e in (x + 6, x + w - 6):                    # end stiles
            c.paint(e - 3, e + 3, b0 + 2, b0 + sec, ID_DOOR, 0.94, 0.95, height=0.006)
        if j == 1:
            n = 5
            pitch = (w - 40) / n
            for i in range(n):
                a0 = x + 20 + i * pitch + pitch * 0.18
                a1 = a0 + pitch * 0.64
                _bar(c, a0 - 2, a1 + 2, b0 + 9, b0 + sec - 8, ID_RUBBER, 0.01, 0.8)
                _light(c, a0, a1, b0 + 11, b0 + sec - 10)
    c.paint(x - PAD, x + w + PAD, y + 2 * sec, y + h + PAD, ID_DOOR, 1.0, 1.0, height=0.0)


def paint_service(c):
    """A personnel door: a plain steel leaf in a steel frame, a wired
    vision panel, a kick plate, a lever handle."""
    x, y, w, h = SERVICE
    F = m(SD_FRAME)
    c.paint(x, x + w, y, y + h, ID_SDOOR, 0.88, 0.9, height=0.0)
    _bar(c, x, x + F, y, y + h, ID_SDOOR, DOOR_FRAME_H, 0.84, 0.86, "x")
    _bar(c, x + w - F, x + w, y, y + h, ID_SDOOR, DOOR_FRAME_H, 0.84, 0.86, "x")
    _bar(c, x, x + w, y + h - F, y + h, ID_SDOOR, DOOR_FRAME_H, 0.84, 0.86, "y")
    l0, l1, t = x + F, x + w - F, y + h - F
    c.paint(l0, l1, y, t, ID_SDOOR, 1.0, 0.96, height=0.0)
    c.mul(l0, l1, t - 3, t, 0.88, ao=0.84)
    v0, v1 = y + m(1.35), y + m(1.85)
    c.paint(l0 + 16, l1 - 16, v0, v1, ID_GLASS, 1.0, 1.0, height=0.0)
    for a0, a1, b0, b1, ax in ((l0 + 15, l0 + 16, v0, v1, "x"), (l1 - 16, l1 - 15, v0, v1, "x"),
                               (l0 + 15, l1 - 15, v0 - 1, v0, "y"),
                               (l0 + 15, l1 - 15, v1, v1 + 1, "y")):
        _bar(c, a0, a1, b0, b1, ID_SDOOR, 0.012, 0.86, 0.9, ax)
    c.paint(l0 + 2, l1 - 2, y + 2, y + m(0.25), ID_ALU, 0.9, 0.9, height=0.003)
    hx, hy = l1 - 8, y + m(1.0)
    c.paint(hx - 1.5, hx + 1.5, hy - 5, hy + 5, ID_HANDLE, 1.0, 0.9, height=0.01)
    c.stroke((hx, hy + 2), (hx - 8, hy + 2), 2.2, ID_HANDLE, 1.0, 0.9, height=0.04)


def paint_dome(c):
    """A rooflight dome from above, at OPPM: the sheeted kerb's top edge,
    the opal acrylic shell rising to its crown."""
    x, y, w, h = DOME
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_KERB, 1.0, 1.0, height=0.0)
    cx, cy = x + w / 2.0, y + h / 2.0
    half = DOME_HALF * OPPM
    shell = (DOME_HALF - 0.08) * OPPM
    c.paint(cx - shell, cx + shell, cy - shell, cy + shell, ID_DOME, 1.0, 1.0)
    sy, sx, Y, X = c.field(cx - shell, cx + shell, cy - shell, cy + shell)
    d = np.maximum(np.abs(X - cx), np.abs(Y - cy)) / shell
    c.height[sy, sx] = 0.012 * (1.0 - d ** 2)
    c.ao[sy, sx] = 0.88 + 0.12 * (1.0 - d)
    c.mul(cx - half, cx + half, cy - half, cy - half + 1.0, 0.9, ao=0.86)
    c.mul(cx - shell, cx + shell, cy - shell, cy - shell + 1.5, 0.86, ao=0.8)


def paint_stack(c):
    """The steel flue at SPPM, U up it from the deck and V round it: black
    heat-resisting paint over welded plate, a circumferential seam every
    1.5 m, the guy collar and the rolled rim, the foot's flashing, and a
    painted iron ladder up three of its faces."""
    x, y, w, h = STACK
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_STACK, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    c.shade[sy, sx] *= 1.0 + 0.04 * atlas.noise(c, 41, 10.0, 2.0)[sy, sx]

    def U(z):
        return x + (z - Z_DECK) * SPPM
    z = Z_DECK + 1.0
    while z < STACK_TOP - 0.4:
        c.paint(U(z) - 0.4, U(z) + 0.4, y - PAD, y + h + PAD, ID_STACK, 0.86, 0.9,
                height=0.002)
        z += 1.5
    for z0, z1 in ((Z_DECK, Z_DECK + 0.25), (STACK_GUY, STACK_GUY + 0.12),
                   (STACK_TOP - STACK_CAP, STACK_TOP)):
        c.paint(U(z0), U(z1), y - PAD, y + h + PAD, ID_STACK, 1.06, 1.0, height=0.0)
        c.bevel(U(z0), U(z1), y - PAD, y + h + PAD, 0.010, 0.8, axes="x")
        c.mul(U(z0) - 1.5, U(z0), y - PAD, y + h + PAD, 0.82, ao=0.82)
    c.paint(U(Z_DECK), U(Z_DECK + 0.25), y - PAD, y + h + PAD, ID_GALV, 0.9, 0.9)
    # the ladder: rails and rungs across the middle three of eight faces
    face = h / 8.0
    vm = y + 4.0 * face
    for side in (-1, 1):
        v = vm + side * m(0.2) * SPPM / PPM
        c.paint(U(Z_DECK + 0.3), U(STACK_TOP - 0.1), v - 1.0, v + 1.0, ID_LADDER, 1.0, 0.95,
                height=0.03)
        c.mul(U(Z_DECK + 0.3), U(STACK_TOP - 0.1), v + 1.0, v + 2.0, 0.85, ao=0.82)
    z = Z_DECK + 0.6
    while z < STACK_TOP - 0.3:
        c.paint(U(z), U(z) + 0.9, vm - m(0.2) * SPPM / PPM, vm + m(0.2) * SPPM / PPM,
                ID_LADDER, 1.0, 0.95, height=0.025)
        c.mul(U(z) - 1.0, U(z), vm - m(0.2) * SPPM / PPM, vm + m(0.2) * SPPM / PPM, 0.86,
              ao=0.84)
        z += 0.3


def paint_fan(c):
    """An extract fan: its galvanised body round, a flange at its foot and
    one under the cowl, a bolted service hatch; the cowl from above, a grille
    over the outlet."""
    x, y, w, h = FAN_S
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_GALV, 1.0, 1.0, height=0.0)
    for b0 in (y, y + h - 3):
        c.paint(x - PAD, x + w + PAD, b0, b0 + 3, ID_GALV, 1.05, 0.95, height=0.006)
    c.paint(x + w * 0.3, x + w * 0.5, y + 6, y + h - 6, ID_GALV, 0.94, 0.95, height=0.004)
    c.mul(x + w * 0.3, x + w * 0.5, y + 5, y + 6, 0.85, ao=0.85)
    x, y, w, h = FAN_T
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_GALV, 1.02, 1.0, height=0.0)
    cx, cy = x + w / 2.0, y + h / 2.0
    c.disc(cx, cy, w * 0.34, ID_DARK, 0.6, 0.5, height=-0.01)
    for k in range(-4, 5):
        c.paint(cx - w * 0.33, cx + w * 0.33, cy + k * 2.4 - 0.5, cy + k * 2.4 + 0.5,
                ID_GALV, 0.9, 0.9, height=0.004)
    c.disc(cx, cy, w * 0.36, ID_GALV, 1.0, 0.9, inner=w * 0.33, height=0.006)


def paint_ahu(c):
    """The air handler's casing at SPPM: galvanised panels on a frame, a
    louvred intake on its end, hinged access doors along its side."""
    for rect, louvre in ((AHU_S, False), (AHU_E, True)):
        x, y, w, h = rect
        c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_GALV, 0.96, 1.0, height=0.0)
        c.paint(x - PAD, x + w + PAD, y, y + 3, ID_GALV, 0.82, 0.85, height=0.0)
        c.paint(x - PAD, x + w + PAD, y + h - 2, y + h + PAD, ID_GALV, 1.04, 1.0, height=0.004)
        n = int(round(w / 26.0))
        for i in range(1, n):
            a = x + i * w / n
            c.paint(a - 0.6, a + 0.6, y + 3, y + h - 2, ID_GALV, 0.86, 0.85, height=-0.002)
        if louvre:
            p0, p1, q0, q1 = x + 6, x + w - 6, y + 8, y + h - 8
            c.paint(p0, p1, q0, q1, ID_DARK, 0.5, 0.5, height=-0.01)
            sy, sx, Y, X = c.field(p0, p1, q0, q1)
            t = ((Y - q0) % 2.5) / 2.5
            blade = t > 0.35
            c.mid[sy, sx] = np.where(blade, ID_LOUVRE, ID_DARK)
            c.shade[sy, sx] = np.where(blade, 0.80 + 0.25 * t, 0.5)
            c.height[sy, sx] = np.where(blade, 0.015 * t, -0.01)
        else:
            for i in range(n):
                a0, a1 = x + i * w / n + 3, x + (i + 1) * w / n - 3
                c.paint(a1 - 3, a1 - 1.5, y + h * 0.45, y + h * 0.55, ID_HANDLE, 1.0, 0.9,
                        height=0.01)
                c.mul(a0, a1, y + 4, y + 5, 0.9, ao=0.9)


# ------------------------------------------------------------- lettering
def _glyph(ch, w, sw):
    """test(u, v) for capital *ch* in cap-height units: u from its left,
    v up from the baseline; strokes *sw* wide."""
    def seg(ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        ll = math.hypot(dx, dy)

        def t(u, v):
            tt = ((u - ax) * dx + (v - ay) * dy) / (ll * ll)
            d = np.abs((u - ax) * dy - (v - ay) * dx) / ll
            return (d <= sw / 2.0) & (tt >= 0.0) & (tt <= 1.0)
        return t

    def ring(cx, cy, rx, ry, keep=None):
        def t(u, v):
            a, b = (u - cx) / rx, (v - cy) / ry
            ai, bi = (u - cx) / (rx - sw), (v - cy) / (ry - sw)
            hit = (a * a + b * b <= 1.0) & (ai * ai + bi * bi >= 1.0)
            if keep is not None:
                hit &= keep(u, v)
            return hit
        return t

    def box(u0, u1, v0, v1):
        return lambda u, v: (u >= u0) & (u <= u1) & (v >= v0) & (v <= v1)

    if ch == "K":
        parts = [box(0, sw, 0, 1), seg(sw * 0.8, 0.40, w - sw * 0.45, 1.0),
                 seg(w * 0.36, 0.62, w - sw * 0.45, 0.0)]
    elif ch == "O":
        parts = [ring(w / 2.0, 0.5, w / 2.0, 0.5)]
    elif ch == "N":
        parts = [box(0, sw, 0, 1), box(w - sw, w, 0, 1),
                 seg(sw * 0.5, 1.0, w - sw * 0.5, 0.0)]
    elif ch == "E":
        parts = [box(0, sw, 0, 1), box(0, w, 1 - sw, 1), box(0, w * 0.86, 0.5 - sw / 2,
                                                              0.5 + sw / 2), box(0, w, 0, sw)]
    elif ch == "P":
        ry = (1.0 - 0.42) / 2.0
        cy = 0.42 + ry
        bx = w - ry
        parts = [box(0, sw, 0, 1), box(0, bx, 1 - sw, 1), box(0, bx, 0.42, 0.42 + sw),
                 ring(bx, cy, ry, ry, keep=lambda u, v, bx=bx: u >= bx)]
    elif ch == "A":
        parts = [seg(sw * 0.5, 0.0, w / 2.0, 1.0), seg(w / 2.0, 1.0, w - sw * 0.5, 0.0),
                 box(0.22 * w, 0.78 * w, 0.26, 0.26 + sw * 0.9)]
    elif ch == "J":
        r = w / 2.0
        parts = [box(w - sw, w, 0.30, 1), ring(r, 0.32, r, 0.32,
                                                keep=lambda u, v: v <= 0.32)]
    else:
        raise ValueError("no glyph for %r" % ch)

    def test(u, v):
        hit = np.zeros(np.shape(u), bool)
        for p in parts:
            hit |= p(u, v)
        return hit & (v >= 0.0) & (v <= 1.0) & (u >= 0.0) & (u <= w)
    return test


def text_width():
    return sum(GLYPH_W[ch] for ch in TEXT) + TRACK * (len(TEXT) - 1)


def paint_letters(c):
    """KONEPAJA in plain capitals on the office's front fascia: each letter a
    pale enamelled plate a little proud of the sheet, its occlusion round
    it. The background is the fascia band's sheet, rib for rib: the region
    starts on a rib, as LET_X0 does on the ring."""
    x, y, w, h = LETTERS
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_FASCIA, 1.0, 1.0, height=0.0)
    _sheet(c, x - PAD, x + w + PAD, y - PAD, y + h - FLASH_PX, PAD)
    _flashing(c, x - PAD, x + w + PAD, y + h - FLASH_PX, y + h + PAD)
    cap = m(CAP)
    tw = text_width() * cap
    u0 = x + (w - tw) / 2.0
    vb = y + (h - FLASH_PX - cap) / 2.0
    for ch in TEXT:
        gw = GLYPH_W[ch]
        test = _glyph(ch, gw, STROKE)
        big = _glyph(ch, gw, STROKE + 0.05)
        c.shape(u0 - 2, u0 + gw * cap + 2, vb - 2, vb + cap + 2,
                lambda X, Y, u0=u0, big=big: big((X - u0) / cap, (Y - vb) / cap + 0.01),
                ao=0.80)
        c.shape(u0 - 1, u0 + gw * cap + 1, vb - 1, vb + cap + 1,
                lambda X, Y, u0=u0, test=test: test((X - u0) / cap, (Y - vb) / cap),
                mid=ID_LETTER, shade=1.0, ao=1.0, height=LETTER_H)
        u0 += (gw + TRACK) * cap


# ----------------------------------------------------------------- the plan
def plan_px(x, y):
    """Atlas pixel of plan point (x, y) in the roof plan region."""
    px, py, _w, _h = PLAN
    return px + (x + HX) * DPPM, py + (y + HY) * DPPM


def paint_plan(c):
    """The roof plan at DPPM: mineral-felt decks in one-metre strips, the
    monitors' dark tops with their seams, the domes the flat tiers show,
    rainwater outlets with ponding round them, and the flue's flashing."""
    x, y, w, h = PLAN
    p = DPPM
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_DECK, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    v = (X - x) / p
    f = v - np.floor(v)
    c.height[sy, sx] = np.where(f < 0.12, 0.004 * (1.0 - f / 0.12), 0.0)
    c.mid[sy, sx] = np.where(f < 1.0 / p, ID_LAP, ID_DECK)
    row = np.floor(v).astype(np.int64)
    u = (Y - y) / p + 5.0 * (row % 2)
    endlap = ((u % 10.0) < 1.0 / p) & (c.mid[sy, sx] == ID_DECK)
    c.mid[sy, sx] = np.where(endlap, ID_LAP, c.mid[sy, sx])
    # the office's and the strip's decks, laid later, a shade apart
    x0, y0 = plan_px(-HX, -HY)
    x1, y1 = plan_px(HX, Y_HALL)
    c.mul(x0 - PAD, x1 + PAD, y0 - PAD, y1, 1.06)
    xo, _ = plan_px(OX1, 0.0)
    c.mul(x0 - PAD, xo, y0 - PAD, y1, 0.95)
    # the edges: felt dressed up the fascia's upstand and the walls
    for (ax, ay, bx, by) in ((-HX, Y_HALL, HX, HY), (-HX, -HY, OX1, Y_HALL),
                             (OX1, -HY, HX, Y_HALL)):
        p0, p1 = plan_px(ax, ay), plan_px(bx, by)
        sy, sx, Y, X = c.field(p0[0], p1[0], p0[1], p1[1])
        d = np.minimum(np.minimum(X - p0[0], p1[0] - X), np.minimum(Y - p0[1], p1[1] - Y)) / p
        edge = np.clip((d - FAS_IN) / 0.3, 0.0, 1.0)
        c.shade[sy, sx] *= 0.80 + 0.20 * edge
        c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.66 + 0.34 * edge)
    # the monitors' tops: dark felt on a sheet edge, a lap every 2.5 m
    for mx in MON_X:
        a0, b0 = plan_px(mx - MON_W / 2.0, MON_Y0)
        a1, b1 = plan_px(mx + MON_W / 2.0, MON_Y0 + MON_N * MON_LIGHT)
        c.mul(a0 - 3, a1 + 3, b0 - 3, b1 + 3, 0.78, ao=0.70)       # its foot's AO
        a0, _ = plan_px(mx - MON_W / 2.0 + MON_SLOPE_IN, 0.0)
        a1, _ = plan_px(mx + MON_W / 2.0 - MON_SLOPE_IN, 0.0)
        c.paint(a0, a1, b0, b1, ID_MONTOP, 1.0, 1.0, height=0.0)
        c.paint(a0, a0 + 1.2, b0, b1, ID_FASCIA, 1.0, 1.0, height=0.006)
        c.paint(a1 - 1.2, a1, b0, b1, ID_FASCIA, 1.0, 1.0, height=0.006)
        k = MON_Y0
        while k < MON_Y0 + MON_N * MON_LIGHT + 1e-6:
            _, bb = plan_px(0, k)
            c.paint(a0 + 1.2, a1 - 1.2, bb - 0.5, bb + 0.5, ID_MONTOP, 0.85, 0.9,
                    height=0.003)
            k += 2.5
    # the domes, for the tiers that paint them
    for dx in DOME_X:
        for dy in DOME_Y:
            cx, cy = plan_px(dx, dy)
            hh = DOME_HALF * p
            c.mul(cx - hh - 1.5, cx + hh + 1.5, cy - hh - 1.5, cy + hh + 1.5, 0.80, ao=0.72)
            c.paint(cx - hh, cx + hh, cy - hh, cy + hh, ID_KERB, 1.0, 1.0, height=0.0)
            s = (DOME_HALF - 0.08) * p
            c.paint(cx - s, cx + s, cy - s, cy + s, ID_DOME, 1.0, 1.0, height=0.004)
    # the outlets
    for ox, oy in OUTLETS:
        cx, cy = plan_px(ox, oy)
        c.disc(cx, cy, 0.30 * p, ID_LAP, 0.8, 0.8, height=-0.004)
        c.disc(cx, cy, 0.14 * p, ID_DARK, 1.0, 0.5, height=-0.012)
    # the flue's flashing collar and the plant's feet
    cx, cy = plan_px(*STACK_AT)
    c.disc(cx, cy, (STACK_R + 0.25) * p, ID_GALV, 0.85, 0.75, height=0.004)
    for fx, fy in FANS:
        cx, cy = plan_px(fx, fy)
        c.disc(cx, cy, (FAN_R + 0.2) * p, ID_GALV, 0.85, 0.75, height=0.004)
    a0, b0 = plan_px(AHU[0], AHU[2])
    a1, b1 = plan_px(AHU[1], AHU[3])
    c.mul(a0 - 2, a1 + 2, b0 - 2, b1 + 2, 0.85, ao=0.72)


def paint_patches(c):
    """Flat cells for surfaces a whole face takes one colour from."""
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0), "reveal": (ID_RIB, 0.94, 0.86),
        "sill": (ID_SILL, 1.0, 0.95), "soffit": (ID_FASCIA, 0.80, 0.80),
        "cap": (ID_FASCIA, 1.05, 1.0), "upstand": (ID_DECK, 0.90, 0.85),
        "kerb": (ID_KERB, 1.0, 1.0), "monend": (ID_FASCIA, 0.94, 1.0),
        "rim": (ID_STACK, 1.05, 1.0), "soot": (ID_SOOT, 1.0, 0.6),
        "galv": (ID_GALV, 1.0, 1.0), "conc": (ID_CONC, 1.0, 1.0),
        "felt": (ID_DECK, 1.0, 1.0), "fasend": (ID_FASCIA, 0.86, 0.9),
        "door_reveal": (ID_SDOOR, 0.9, 0.85), "duct": (ID_GALV, 0.92, 0.95),
        "stack": (ID_STACK, 1.0, 1.0),
    }
    atlas.paint_patches(c, PATCHES, spec)


# ------------------------------------------------------------------ checks
def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands or
    run off the sheet, or if a region does not fit what samples it."""
    rects = {"plan": PLAN, "monlo": MONLO, "rib7lo": RIB7LO, "rib5lo": RIB5LO, "ent_a": ENT_A, "ent_b": ENT_B,
             "ent_c": ENT_C, "off_l": OFF_L, "mon_l": MON_L, "fan_s": FAN_S,
             "fan_t": FAN_T, "dome": DOME, "truck": TRUCK, "stack": STACK,
             "strip_l": STRIP_L, "ahu_e": AHU_E, "service": SERVICE, "ahu_s": AHU_S,
             "letters": LETTERS}
    rects.update({"patch_" + k: r for k, r in PATCHES.items()})   # "stack" is both
    problems = atlas.region_problems(rects, ATLAS, bands_top=UNI_Y, band_gap=0)
    if AGG_H != m(Z_EAVE):
        problems.append("the AGG band is not the hall's wall to the fascia")
    if OFF_PX != m(OB_H):
        problems.append("the office band is not OB_H tall")
    if FAS_PX != m(FAS_H):
        problems.append("the fascia band is not FAS_H tall")
    checks = [(PLAN, (2 * HX * DPPM, 2 * HY * DPPM)), (MONLO, (MON_N * MON_LIGHT * DPPM,
                                                               MON_H * DPPM)),
              (ENT_A, (m(E_X1 - E_X0), m(E_MODS[1] - E_MODS[0]))),
              (ENT_B, (m(E_X1 - E_X0), m(E_MODS[2] - E_MODS[1]))),
              (ENT_C, (m(E_X1 - E_X0), m(E_MODS[3] - E_MODS[2]))),
              (OFF_L, (m(O_LIGHT), m(O_WIN_H))),
              (RIB7LO, (7 * O_LIGHT * LPPM, O_WIN_H * LPPM)),
              (RIB5LO, (5 * O_LIGHT * LPPM, O_WIN_H * LPPM)), (MON_L, (m(MON_LIGHT), m(MON_H))),
              (STRIP_L, (m(S_LIGHT), m(Z_SHEAD - Z_SSILL))),
              (SERVICE, (m(SD_W), m(SD_H))), (LETTERS, (m(LET_X1 - LET_X0),
                                                         m(OZ_TOP - OZ_EAVE))),
              (STACK, ((STACK_TOP - Z_DECK) * SPPM, 8 * 2 * STACK_R * math.tan(
                  math.pi / 8) * SPPM)),
              (AHU_S, ((AHU[3] - AHU[2]) * SPPM, AHU_H * SPPM)),
              (AHU_E, ((AHU[1] - AHU[0]) * SPPM, AHU_H * SPPM))]
    for rect, (w, h) in checks:
        if abs(rect[2] - w) > 1.01 or abs(rect[3] - h) > 1.01:
            problems.append("region %s is not %.1f x %.1f px" % (rect, w, h))
    if abs(TRUCK[2] - m(TD_W)) > 1.01 or TRUCK[3] < 2 * m(TD_SEC):
        problems.append("the truck door's region does not fit two sections")
    if E_LEAF_PX * 2 + 2 * (E_FRAME + E_SIDE + E_MULL) != m(E_X1 - E_X0):
        problems.append("the entrance's leaves do not fill the bay")
    if text_width() * CAP > LETTERS[2] / PPM - 0.3:
        problems.append("the lettering does not fit its region")
    for z in (Z_PLINTH, Z_EAVE, Z_TOP, Z_DECK, OZ_EAVE, OZ_TOP, OZ_DECK, SZ_EAVE, SZ_TOP,
              SZ_DECK, Z_HSILL, Z_HHEAD, Z_SSILL, Z_SHEAD, O_FLOOR, ZL, O_FLOOR2, O_SILL1,
              O_SILL2, O_WIN_H, Z_LEAF) + E_MODS:
        if abs(m(z) - round(m(z))) > 1e-6:
            problems.append("height %.5f is not a whole texel" % z)
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    The AGG band's V is height from the ground on every wall but the hall's
    south wall, which never reaches its window or plinth rows, so the
    plinth's soil and splash, the runs under the fascia's drip and the
    streaks from the window sills land the same all round. The panel joints
    and column covers carry their own runs, being in the band too.
    """
    agg = (ID_AGG, ID_STONE_D, ID_STONE_L, ID_RIB, ID_SEAL, ID_GROUT)
    steel = (ID_FASCIA, ID_DOOR, ID_SDOOR, ID_HANDLE, ID_GALV, ID_LOUVRE, ID_STACK,
             ID_KERB, ID_ALU, ID_SILL, ID_LADDER)
    w = weathering.Weather(c, clean=(ID_GLASS, ID_DOME), steel=steel)
    w.grime()
    w.fade((ID_FRAME, ID_DOOR, ID_SDOOR, ID_FASCIA, ID_DECK, ID_LAP, ID_KERB))
    w.wash(agg + (ID_OPANEL,))
    yp = AGG_Y0 + m(Z_PLINTH)
    w.plinth(0, ATLAS, AGG_Y0, yp, (ID_PLINTH,))
    w.splash(0, ATLAS, yp, AGG_Y0 + AGG_H + PAD, agg, amount=0.16)
    # under the fascia's drip: sheltered dust, then runs
    yd = AGG_Y0 + m(Z_EAVE)
    w.shelter(0, ATLAS, yd - 20, yd, agg, amount=0.06, top=AGG_Y0 + AGG_H + PAD)
    w.runs(0, ATLAS, yd - 90, yd, agg, 0.09, fall=40.0)
    # the joints: the sealant lines catch dirt, and water runs down them
    for k in range(int(round(16.0 / PANEL))):
        u = m(k * PANEL)
        for a, b in wrap_spans(u - 5.0, u + 5.0):
            w.add("D", a, b, yp, yd, lambda Y, X, nz, u=u: 0.07 * atlas.smoothstep(
                0.2, 1.4, nz("runs")) * np.exp(-((((X - u + 512.0) % 1024.0) - 512.0) / 3.0)
                                               ** 2), agg)
    # under each window's sill flashing: streaks, heaviest under its ends
    for k in range(3):
        u0, u1 = bay_window(k)
        y0 = AGG_Y0 + m(Z_HSILL) - 6
        w.runs(m(u0) - 4, m(u1) + 4, y0 - 44, y0, agg, 0.10, fall=16.0)
        for e in (m(u0) - 2, m(u1) + 2):
            w.add("R", e - 1.5, e + 1.5, y0 - 18, y0, lambda Y, X, nz, y0=y0: 0.12
                  * np.exp(-(y0 - Y) / 8.0), agg)
    # the lifting anchors' faint rust
    for k in range(int(round(16.0 / PANEL))):
        for du in (0.45, PANEL - 0.45):
            u = m(k * PANEL + du)
            yy = AGG_Y0 + m(7.05)
            w.add("R", u - 2, u + 2, yy - 14, yy - 1, lambda Y, X, nz, yy=yy: 0.10
                  * np.exp(-(yy - Y) / 5.0) * atlas.smoothstep(0.0, 1.2, nz("runs")), agg)
    # the fascia: chalked, dust in the pans, short runs from the flashing
    w.runs(0, ATLAS, FAS_Y0, FAS_Y0 + FAS_PX - FLASH_PX, (ID_FASCIA,), 0.08, fall=10.0,
           noise="short")
    x, y, rw, rh = LETTERS
    w.runs(x, x + rw, y, y + rh - FLASH_PX, (ID_FASCIA, ID_LETTER), 0.06, fall=10.0,
           noise="short")
    # the office: dust under the floor joint, faint runs
    w.runs(0, ATLAS, OFF_Y0, OFF_Y0 + OFF_PX, (ID_OPANEL,), 0.04, fall=80.0)
    w.add("D", 0, ATLAS, OFF_Y0, OFF_Y0 + 12, lambda Y, X, nz: 0.05 * nz("blotch"),
          (ID_OPANEL,))
    # the plan: blotchy felt, ponding round the outlets and at the upstands
    x, y, rw, rh = PLAN
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.04 + 0.06 * nz("big")
          + 0.04 * nz("blotch"), (ID_DECK, ID_LAP, ID_MONTOP))
    for ox, oy in OUTLETS:
        cx, cy = plan_px(ox, oy)
        r = 2.0 * DPPM
        w.add("D", cx - r, cx + r, cy - r, cy + r, lambda Y, X, nz, cx=cx, cy=cy, r=r:
              0.22 * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (0.45 * r) ** 2)
              * (0.6 + 0.4 * nz("blotch")), (ID_DECK, ID_LAP))
    cx, cy = plan_px(*STACK_AT)
    r = 1.5 * DPPM
    w.add("D", cx - r, cx + r, cy - r, cy + r, lambda Y, X, nz: 0.25 * np.exp(
        -((X - cx) ** 2 + (Y - cy) ** 2) / (0.5 * r) ** 2), (ID_DECK, ID_LAP, ID_GALV))
    # the doors
    x, y, rw, rh = SERVICE
    w.door(x + 4, x + rw - 4, y, y + rh - 4, (ID_SDOOR,), handle=(x + rw - 12, y + m(1.0)))
    x, y, rw, rh = TRUCK
    w.splash(x, x + rw, y, y + m(TD_SEC), (ID_DOOR,), amount=0.16, fall=0.2)
    x, y, rw, rh = ENT_A
    w.door(x + 30, x + rw - 30, y, y + m(Z_LEAF), (ID_FRAME, ID_ALU),
           handle=(x + rw / 2.0, y + m(1.15)))
    # windows: dirt on their bottom rails
    for rect in (OFF_L, STRIP_L):
        x, y, rw, rh = rect
        w.add("D", x, x + rw, y, y + FOOT + 1, lambda Y, X, nz: 0.10
              + 0.12 * atlas.smoothstep(0.2, 1.4, nz("short")), (ID_FRAME,))
    # the monitors' upstands and the domes' kerbs
    x, y, rw, rh = MON_L
    w.splash(x, x + rw, y, y + m(MON_UP), (ID_KERB, ID_SILL), amount=0.14, fall=0.1)
    # the flue: soot down from the rim, rust runs from the collar
    x, y, rw, rh = STACK
    w.add("D", x + rw - 40, x + rw + PAD, y - PAD, y + rh + PAD, lambda Y, X, nz:
          0.25 * atlas.smoothstep(x + rw - 40, x + rw, X), (ID_STACK, ID_LADDER))
    w.add("R", x, x + rw, y, y + rh, lambda Y, X, nz: 0.08 * atlas.smoothstep(
        0.6, 1.8, nz("runs")), (ID_STACK, ID_LADDER))
    # the plant: dust at its feet
    for rect in (FAN_S, AHU_S, AHU_E):
        x, y, rw, rh = rect
        w.splash(x, x + rw, y, y + rh, (ID_GALV, ID_LOUVRE), amount=0.12, fall=0.15,
                 ppm=SPPM)
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_agg(c)
    paint_fascia(c)
    paint_office_band(c)
    c.check_bands(BAND_IDS)
    paint_ribbon_light(c, OFF_L)
    paint_strip_light(c)
    paint_monitor_light(c)
    paint_monlo(c)
    paint_riblo(c)
    paint_entrance(c)
    paint_truck(c)
    paint_service(c)
    paint_dome(c)
    paint_stack(c)
    paint_fan(c)
    paint_ahu(c)
    paint_letters(c)
    paint_plan(c)
    paint_patches(c)

    wear = 0.02 * atlas.noise(c, 3, 40.0) + 0.012 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    sheet = np.isin(c.mid, (ID_FASCIA, ID_DOOR, ID_SDOOR, ID_KERB))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    c.shade[sheet] *= 1.0 + 0.015 * grain[sheet]
    deck = np.isin(c.mid, (ID_DECK, ID_LAP, ID_MONTOP))
    mottle = atlas.noise(c, 6, 6.0, 6.0)
    gravel = atlas.noise(c, 11, 0.6)
    c.shade[deck] *= 1.0 + 0.035 * mottle[deck] + 0.08 * gravel[deck]
    c.height[deck] += 0.0008 * gravel[deck]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_CONC, ID_RIB, ID_GROUT))
    pores = atlas.noise(c, 9, 0.8)
    c.shade[mineral] *= 1.0 + 0.03 * pores[mineral]
    c.height[mineral] += 0.0005 * pores[mineral]
    weather(c)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    for key, i in (("agg", ID_AGG), ("stone_d", ID_STONE_D), ("stone_l", ID_STONE_L),
                   ("rib", ID_RIB), ("fascia", ID_FASCIA), ("frame", ID_FRAME),
                   ("opanel", ID_OPANEL), ("door", ID_DOOR), ("sdoor", ID_SDOOR)):
        t[i] = pal[key]
    # the monitors' tops: the fascia's sheet, laid flat and a little darker
    t[ID_MONTOP] = [0.86 * v for v in pal["fascia"]]
    return t


def export(out_dir, ss=atlas.SS):
    """Candidate glazing in the emission map is neutral grey, each light the
    lit room behind it; the domes glow evenly at a third of that; nothing
    else on the building glows, and no occupancy or schedule is baked in."""
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.008)
    c.weather.dust(cav, (ID_AGG, ID_STONE_D, ID_STONE_L, ID_FASCIA, ID_SEAL))
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
