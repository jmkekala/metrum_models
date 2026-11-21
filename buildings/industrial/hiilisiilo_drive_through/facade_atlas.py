# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas for hiilisiilo_drive_through, and
the layout build.py maps into.

This describes one asset and nothing else, so it lives beside build.py rather
than in scripts/. It is the single source of the numbers the two files share:
build.py imports the massing heights, opening sizes and region rects from
here, so the pixel layout and the UVs cannot drift apart. Importing this
module only defines those constants; the painting runs when paint() is
called. Rasterising is scripts/atlas.py's.

    python3 facade_atlas.py export      # writes every map into ./export

A trim sheet. Rows from the bottom:

    y    0 ..  414   S1      concrete, z 0 .. 6.40 at 64 px/m: plinth,
                             board-formed legs and walls, the deck joint at
                             5.20, the bunker's ring beam, the cladding's base
                             flashing on its top
    y  414 ..  554   C       profiled sheet cladding, one 2.00 m repeat (rows
                             420 .. 548) tiling in V, x 0 .. 960; the concrete
                             frame's column strip beside it at x 972, same rows
    y  558 ..  658   ROOF    profiled roof sheet, V stretched up the slope
    y  660 ..  680   FASCIA  the roof slab's front and rake edges
    y  684 ..  944   unique  the lane's ceiling and side walls (32 px/m), the
                             doors, the window, a hopper side, flat patches
    y  988 .. 1024   EAVE_R  the rear (low) eave: fascia with the gutter, then
                             the roof's lowest 0.40 m with the snow guard

The screen house is taller than any band at 64 px/m, so the cladding band
repeats in V: build.py cuts the walls at 6.40, 8.40, 10.40 and 12.40 m and
maps every strip onto the same rows. Profiled sheet varies only across its
ribs, so the repeat has nothing to show but its noise, which is drawn on the
band's period (noise() below). Weather that follows height (splash, coal
dust thrown up by the trucks) goes only on S1, whose V is height from the
ground.

The lane under the bunker is outside surface of the one closed shell, seen in
shade and open at both ends, so its walls and ceiling darken toward the
middle of its length and its occlusion is painted; coal dust lies thickest
at its foot and round the chutes. Its regions are at 32 px/m, a recorded
deviation: 8 m of wall and ceiling at 64 px/m would need a third of the atlas
for surfaces seen only in shade.
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

ASSET = "hiilisiilo_drive_through"
ATLAS = 1024
PPM = 64.0
LPM = 32.0                   # px/m in the lane's own regions

# --------------------------------------------------------------- massing
# Metres. Front faces -Y. The bunker house is 12.0 x 8.0 m, its long sides to
# the front and the rear; the truck lane runs through it front to rear.
HX, HY = 6.00, 4.00
XL0, XL1 = -4.40, 0.60       # the lane's side walls: 5.00 m clear
LANE_C = (XL0 + XL1) / 2.0
Z_DECK = 5.20                # the lane's ceiling, the bunker's underside
Z_PLINTH = 0.30
Z_CLAD = 6.40                # top of the ring beam, foot of the cladding: S1's top
CLAD_P = 2.00                # the cladding band's repeat
JOINTS = (Z_CLAD, Z_CLAD + CLAD_P, Z_CLAD + 2 * CLAD_P, Z_CLAD + 3 * CLAD_P,
          Z_CLAD + 4 * CLAD_P)
COL_W = 0.40                 # the concrete frame's columns
Z_EAVE_F, Z_EAVE_R = 12.80, 12.00                 # roof underside at the wall lines
TAN = (Z_EAVE_F - Z_EAVE_R) / (2.0 * HY)          # 1:10, falling to the rear
FRONT_OV, REAR_OV, RAKE_OV = 0.30, 0.40, 0.30
ROOF_T = 0.25
WALL_INTO = 0.12             # walls run this far up into the slab
Z_SCREEN = 7.40              # the screen floor: the gallery's floor at the wall
Z_WIN = 8.70                 # sill of the screen house's windows
Z_WIN_LOW = 1.10             # sill of the control room's windows

# Hoppers under the bunker, along the lane's centre line.
HOP_Y = (-2.50, 0.00, 2.50)
HOP_TOP = (1.50, 1.20)       # plan size at their buried top, x by y
HOP_BOT = (0.60, 0.45)       # ... and at the mouth
HOP_BURY = 0.12
Z_HOP = 4.60                 # the mouths: the lowest point over the lane

# The conveyor gallery: 2.0 x 2.0 m, rising at 30 degrees from the intake
# house east of the bunker into the screen house's east wall, the side the
# catalog camera sees, its axis along X. It enters the east wall's rear half,
# clear of the lane (west of the control room) and both of its approaches.
GAL_Y = (0.80, 2.80)         # across the axis
GAL_DEG = 30.0
GAL_TAN = math.tan(math.radians(GAL_DEG))
GAL_COS = math.cos(math.radians(GAL_DEG))
GAL_H = 2.00                 # section height, square to the axis
GAL_X = (HX - 0.50, HX + 7.50)   # upper end inside the house, lower inside the intake

# The intake hopper house: concrete, flat concrete roof slab, its vehicle
# door on its front (-Y) face.
INT_X = (HX + 5.00, HX + 8.20)
INT_Y = (GAL_Y[0] - 0.50, GAL_Y[1] + 0.50)
INT_SLAB = (3.95, 4.20)
INT_OV = 0.15
INT_TOP = 4.07               # its walls' lid, inside the slab


def z_under(y):
    """Height of the bunker roof's underside over plan y."""
    return Z_EAVE_F - (y + HY) * TAN


def gal_bottom(x):
    """The gallery's floor (its bottom face) over plan x."""
    return Z_SCREEN - (x - HX) * GAL_TAN


SLOPE_F = (1.0 + TAN * TAN) ** 0.5
Y_FRONT, Y_REAR = -HY - FRONT_OV, HY + REAR_OV    # the slab's edges in plan
ROOF_SLOPE_LEN = (Y_REAR - Y_FRONT) * SLOPE_F
GAL_LEN = (GAL_X[1] - GAL_X[0]) / GAL_COS          # along its axis

# ------------------------------------------------------------- openings
# kind -> (width, height, casing side, casing bottom, casing top), metres.
# Doors stand on the ground and have no bottom casing.
OPENINGS = {
    "door": (0.95, 2.10, 0.08, 0.0, 0.08),
    "win": (1.20, 0.90, 0.06, 0.06, 0.08),
    "door_v": (2.40, 2.60, 0.10, 0.0, 0.12),
}
REVEAL_DEPTH = {"door": 0.12, "win": 0.12, "door_v": 0.15}

# ------------------------------------------------------------ atlas bands
S1_Y0 = 2.0                  # v of z = 0
S1_TOP = S1_Y0 + Z_CLAD * PPM                     # 411.6
C_Y0, C_H = 420.0, CLAD_P * PPM                   # one 2.00 m repeat, 128 rows
C_G = 6.0                    # gutter rows each side, periodic
C_W = 960.0                  # the cladding band's width; U stays inside it
COL = (972.0, C_Y0, COL_W * PPM, C_H)             # column strip, same rows
ROOF_Y0, ROOF_H = 560.0, 96.0
ROOF_LEN = 9.60              # metres up the slope ROOF_H rows cover
ROOF_RPM = ROOF_H / ROOF_LEN
FASC_Y0 = 662.0
FASC_H = ROOF_T * PPM        # 16 rows
UNI_Y0 = 686.0

LANE_CEIL = (4.0, UNI_Y0, (XL1 - XL0) * LPM, 2 * HY * LPM)      # 160 x 256
LANE_SIDE = (172.0, UNI_Y0, 2 * HY * LPM, Z_DECK * LPM)         # 256 x 166.4
ITEM_ORIGIN = {
    "door": (436.0, UNI_Y0),
    "win": (516.0, UNI_Y0),
    "door_v": (608.0, UNI_Y0),
}
CHUTE = (782.0, UNI_Y0, 80.0, 48.0)
PATCHES = {name: (870.0 + 14.0 * i, UNI_Y0, 8.0, 8.0) for i, name in enumerate(
    ("blank", "reveal", "soffit", "coal", "gal_under", "coping", "felt",
     "slab_under", "steel"))}

# The rear eave band, as konehalli_open_bays: the rear fascia (V = height over
# the slab's underside) with the gutter across its top, and from its top row
# on, the roof's lowest EAVE_STRIP_LEN up the slope at EAVE_RPM rows a metre.
FASC_R_Y0 = 990.0
EAVE_ROOF_Y0 = FASC_R_Y0 + FASC_H
EAVE_STRIP_LEN = 0.40
EAVE_RPM = 40.0
GUTTER_PX = 9.0
PIPE_STRIP = (EAVE_ROOF_Y0 - 1 - GUTTER_PX / 2.0 - 2.5,
              EAVE_ROOF_Y0 - 1 - GUTTER_PX / 2.0 + 2.5)
SNOW_S = 0.20                # the snow guard's lower tube, up the slope from the edge

RIB_P = 16.0                 # profiled sheet: a rib every 0.25 m, wall and roof
BOARD_H = 0.20               # board-formed concrete: a board every 0.20 m


def item_size_px(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    return (w + 2.0 * cs) * PPM, (h + cb + ct) * PPM


def hop_at_deck():
    """A hopper's plan size where its sides cross the lane's ceiling."""
    f = (Z_DECK - Z_HOP) / (Z_DECK + HOP_BURY - Z_HOP)
    return tuple(b + (t - b) * f for t, b in zip(HOP_TOP, HOP_BOT))


# ----------------------------------------------------------- material ids
(ID_CONC, ID_CLAD, ID_METAL, ID_ROOF, ID_SASH, ID_GLASS, ID_DOOR, ID_STEEL,
 ID_COAL, ID_FELT, ID_BLANK, ID_HW, ID_GUTTER) = range(13)
# (roughness, metallic). One ORM for both variants, so the cladding is a
# painted sheet in both: grey paint (or galvanising long since dulled under
# coal dust) and red oxide alike, all but dielectric. The gutter, downpipes
# and snow guard are the catalog's galvanised rainwater steel.
SURFACE = {
    ID_CONC: (0.90, 0.0), ID_CLAD: (0.58, 0.10), ID_METAL: (0.52, 0.20),
    ID_ROOF: (0.52, 0.12), ID_SASH: (0.50, 0.15), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_DOOR: (0.56, 0.12), ID_STEEL: (0.62, 0.30), ID_COAL: (0.92, 0.0),
    ID_FELT: (0.90, 0.0), ID_BLANK: (0.95, 0.0), ID_HW: (0.45, 0.55),
    ID_GUTTER: (0.48, 0.60),
}

# ---------------------------------------------------------------- palettes
# Restrained, one coherent treatment per instance: the concrete, the coal and
# the galvanised rainwater steel are the same in both.
VARIANTS = {
    "grey_sheet": {"clad": (114, 118, 117), "roof": (70, 72, 74),
                   "door": (66, 78, 74), "sash": (92, 98, 96)},
    "red_sheet": {"clad": (104, 56, 46), "roof": (62, 60, 58),
                  "door": (64, 64, 62), "sash": (94, 94, 92)},
}
DEFAULT_VARIANT = "grey_sheet"
FIXED = {
    ID_CONC: (134, 132, 126), ID_GLASS: glazing.BASE, ID_STEEL: (72, 72, 70),
    ID_COAL: (30, 30, 30), ID_FELT: (54, 54, 56), ID_BLANK: (52, 52, 52),
    ID_HW: (46, 46, 46), ID_GUTTER: (134, 137, 137),
}
GLASS_BASE = glazing.BASE

BAND_IDS = {
    "S1": ((0, 414), {ID_CONC, ID_METAL}),
    "C": ((C_Y0 - C_G, C_Y0 + C_H + C_G), {ID_CLAD, ID_CONC}),
    "ROOF": ((ROOF_Y0 - 2, ROOF_Y0 + ROOF_H + 2), {ID_ROOF}),
    "FASCIA": ((FASC_Y0 - 2, FASC_Y0 + FASC_H + 2), {ID_METAL}),
    "EAVE_R": ((988, 1024), {ID_METAL, ID_ROOF, ID_GUTTER}),
}
TILE_C = int(ATLAS // C_H)   # 8: noise over C's rows repeats every 128 rows

# ---------------------------------------------------------------- relief
# Metres, relative to the face each region maps onto: only what the mesh
# does not model. Regions painted at LPM scale theirs by LPM / PPM, so the
# slope the normal map derives from stays physical.
RIB_H = 0.025        # profiled sheet's trapezoid ribs
BOARD_LINE_H = 0.002 # the step between formwork boards
CASING_H = 0.015     # steel flashings round the openings
FRAME_H = 0.012      # a steel window's frame over its glass
BAR_H = 0.008        # its glazing bars
GUTTER_R = 0.070
SNOW_TUBE_H = 0.035
SNOW_BRACKET_H = 0.030
BEAM_H = 0.040       # downstand beams painted on the lane's ceiling (kept low)
RAIL_H = 0.050       # the steel wheel guard along the lane's walls

# Occlusion in the lane: what its middle keeps of the shade and AO a surface
# in the open has.
SIDE_SHADE, SIDE_AO = 0.66, 0.50
CEIL_SHADE, CEIL_AO = 0.55, 0.40


def m(v):
    """Metres -> pixels."""
    return v * PPM


# ================================================================== noise
def noise(c, seed, sx, sy=None):
    """atlas.noise() over the whole canvas, but on the cladding band's
    period over its rows, so the band stays seamless where it repeats."""
    n = atlas.noise(c, seed, sx, sy)
    nt = atlas.noise(c, seed + 1000, sx, sy, tile_y=TILE_C)
    rows, _ = c.sl(0, 1, C_Y0 - C_G, C_Y0 + C_H + C_G)
    n[rows] = nt[rows]
    return n


# Coal dust: weathering.py's K field, laid by Weather.coal()
COAL_DUST = (46, 45, 44)     # sRGB: settled coal fines, a matte blue-black grey
FOOT_COAL = 1.00             # coal dust at the concrete's foot (S1, z = 0) ...
FOOT_FALL = 1.50             # ... falling by 1/e every this many metres up
LANE_COAL = 0.35             # everywhere in the lane, before its foot and the hoppers


class Weather(weathering.Weather):
    """weathering.Weather whose named noise is noise() above: periodic over
    the cladding band's rows, free everywhere else."""

    def noise(self, name):
        if name not in self._noise:
            seed, sx, sy, kind = weathering.NOISE[name]
            n = noise(self.c, seed, sx, sy)
            if kind == "unit":
                n = atlas.smoothstep(-1.5, 1.5, n)
            elif kind == "speck":
                n = atlas.smoothstep(1.3, 2.2, n)
            self._noise[name] = n.astype(np.float32)
        return self._noise[name]


# ============================================================ painting
def paint_concrete(c, x0, x1, y_ground, y0, y1, ppm, seed, ties=True):
    """Board-formed concrete over a rect: boards BOARD_H high from the
    ground row, each a little different in tone, staggered butt joints every
    2 m, form-tie holes on a 1.0 x 0.6 m grid."""
    k = ppm / PPM
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    z = (Y - y_ground) / ppm
    u = X / ppm
    row = np.floor(z / BOARD_H).astype(np.int64)
    zm = z - row * BOARD_H
    seg = np.floor(u / 2.0 + 0.5 * (row % 2)).astype(np.int64) % 64
    tone = 1.0 + 0.05 * (atlas.hash_unit(seed, row % 97, seg) - 0.5)
    line = zm * ppm < 0.8
    butt = np.abs(np.mod(u + 1.0 * (row % 2), 2.0)) * ppm < 0.7
    shade = np.where(line | butt, tone * 0.90, tone)
    height = np.where(line | butt, -BOARD_LINE_H * k, 0.0)
    ao = np.where(line | butt, 0.88, 1.0)
    if ties:
        tu = np.mod(u, 1.0) - 0.5
        tz = np.mod(z, 0.6) - 0.3
        tie = np.hypot(tu * ppm, tz * ppm) < 0.9 * k + 0.35
        shade = np.where(tie, shade * 0.72, shade)
        height = np.where(tie, -0.006 * k, height)
        ao = np.where(tie, 0.75, ao)
    c.mid[sy, sx] = ID_CONC
    c.shade[sy, sx], c.height[sy, sx], c.ao[sy, sx] = shade, height, ao


def paint_s1(c):
    """The concrete band: plinth, board-formed walls and legs to the deck
    joint at Z_DECK, the bunker's ring beam above it, and the cladding's
    steel base flashing along the top."""
    y0 = S1_Y0
    paint_concrete(c, 0, ATLAS, y0, 0, y0 + m(Z_DECK), PPM, seed=11)
    # plinth: smoother, a little darker, a chamfer line on its top
    yp = y0 + m(Z_PLINTH)
    c.paint(0, ATLAS, 0, yp, ID_CONC, 0.95, 1.0, height=0.0)
    c.mul(0, ATLAS, yp - 1.0, yp, 0.82, ao=0.85)
    c.lift(0, ATLAS, yp - 1.0, yp, -0.004)
    # the deck joint where the ring beam starts: a groove in shadow
    yd = y0 + m(Z_DECK)
    # ring beam: smoother plywood-formed concrete, panels 1.0 m wide
    sy, sx, Y, X = c.field(0, ATLAS, yd, S1_TOP + 2)
    pan = np.floor(X / PPM).astype(np.int64) % 16
    tone = 1.04 * (1.0 + 0.04 * (atlas.hash_unit(17, pan) - 0.5))
    joint = np.mod(X, PPM) < 0.7
    c.mid[sy, sx] = ID_CONC
    c.shade[sy, sx] = np.where(joint, tone * 0.92, tone)
    c.height[sy, sx] = np.where(joint, -0.002, 0.0)
    c.ao[sy, sx] = np.where(joint, 0.9, 1.0)
    # tie holes in one row along the beam's middle
    zt = yd + m(0.55)
    tie = (np.hypot(np.mod(X, PPM) - 32.0, Y - zt) < 1.2)
    c.shade[sy, sx] = np.where(tie, c.shade[sy, sx] * 0.72, c.shade[sy, sx])
    c.height[sy, sx] = np.where(tie, -0.006, c.height[sy, sx])
    c.paint(0, ATLAS, yd - 0.5, yd + 1.0, ID_CONC, 0.70, 0.7, height=-0.008)
    c.mul(0, ATLAS, yd - 1.5, yd - 0.5, 0.90)
    # the cladding's base flashing: sloped steel over the beam's top edge,
    # its drip casting a line of shadow on the concrete
    f0 = S1_TOP - m(0.15)
    c.paint(0, ATLAS, f0, S1_TOP + 2, ID_METAL, 1.0, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, f0, S1_TOP + 2)
    c.height[sy, sx] = 0.030 - 0.018 * np.clip((Y - f0) / m(0.15), 0.0, 1.0)
    c.paint(0, ATLAS, f0, f0 + 1.0, ID_METAL, 0.80)
    for k, f in enumerate((0.72, 0.84, 0.93)):
        c.mul(0, ATLAS, f0 - 1.0 - k, f0 - k, f, ao=0.75 + 0.08 * k)


def paint_sheet(c, x0, x1, y0, y1, mid, seed, rib_h=RIB_H, k=1.0):
    """Profiled sheet over a rect, ribs across U every RIB_P px: a 3 px
    crown on 1.5 px slopes, the pan between in the rib's lee, a darker
    side-lap every fourth rib where two sheets overlap, tone per sheet.
    Nothing varies in V."""
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    xm = np.mod(X, RIB_P)
    up = np.clip(xm / 1.5, 0.0, 1.0)
    down = np.clip((6.0 - xm) / 1.5, 0.0, 1.0)
    rib = np.where(xm < 6.0, np.minimum(up, down), 0.0)
    sheet = np.floor(X / (4 * RIB_P)).astype(np.int64) % int(ATLAS // (4 * RIB_P))
    tone = 1.0 + 0.05 * (atlas.hash_unit(seed, sheet) - 0.5)
    foot = (xm >= 6.0) & (xm < 7.0)
    lap = (np.mod(X, 4 * RIB_P) < 7.0) & (xm >= 4.5) & (xm < 6.0)
    shade = np.where(foot, tone * 0.90, tone)
    shade = np.where(lap, shade * 0.86, shade)
    ao = np.where(foot | lap, 0.84, 1.0)
    c.mid[sy, sx] = mid
    c.shade[sy, sx], c.ao[sy, sx] = shade, ao
    c.height[sy, sx] = rib_h * k * rib


def paint_c(c):
    """The cladding band over its rows and both gutters: one periodic
    pattern, so each strip's neighbour on the wall is what it finds in the
    gutter. And the column strip beside it, on the same period."""
    paint_sheet(c, 0, C_W, C_Y0 - C_G, C_Y0 + C_H + C_G, ID_CLAD, seed=29)
    x0, y0, w, h = COL
    sy, sx, Y, X = c.field(x0 - 2, x0 + w + 2, C_Y0 - C_G, C_Y0 + C_H + C_G)
    v = np.mod(Y - C_Y0, C_H) / PPM
    row = np.floor(v / BOARD_H).astype(np.int64)
    line = (v - row * BOARD_H) * PPM < 0.8
    tone = 1.0 + 0.05 * (atlas.hash_unit(37, row) - 0.5)
    c.mid[sy, sx] = ID_CONC
    c.shade[sy, sx] = np.where(line, tone * 0.90, tone)
    c.ao[sy, sx] = np.where(line, 0.88, 1.0)
    d = np.minimum(X - x0, x0 + w - X)
    c.height[sy, sx] = (np.where(line, -BOARD_LINE_H, 0.0)
                        + 0.012 * np.clip(d / 1.5, 0.0, 1.0))
    # the cladding meets the column in a steel closer: a shadow line each side
    c.mul(x0 - 2, x0, C_Y0 - C_G, C_Y0 + C_H + C_G, 0.70, ao=0.7)
    c.mul(x0 + w, x0 + w + 2, C_Y0 - C_G, C_Y0 + C_H + C_G, 0.70, ao=0.7)


def paint_roof(c):
    """Profiled roof sheet, V stretched up the slope (ROOF_H rows over
    ROOF_LEN). The ribs vary in U only, so the stretch does not show."""
    y0, h = ROOF_Y0, ROOF_H
    paint_sheet(c, 0, ATLAS, y0 - 2, y0 + h + 2, ID_ROOF, seed=41, rib_h=0.030)
    sy, sx, Y, _ = c.field(0, ATLAS, y0 - 2, y0 + h + 2)
    v = Y - y0
    c.shade[sy, sx] = np.where(v < 1.5, c.shade[sy, sx] * 0.85, c.shade[sy, sx])


def paint_fascia(c):
    """The slab's front and rake edges: a folded steel flashing in the
    roof's trim colour, a drip along its foot and the roof's edge on top."""
    y0, top = FASC_Y0, FASC_Y0 + FASC_H
    c.paint(0, ATLAS, y0 - 2, top + 2, ID_METAL, 1.0, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, top - 2.0, CASING_H, 1.0, axes="y")
    c.paint(0, ATLAS, y0 - 2, y0 + 1, ID_METAL, 0.80)
    c.mul(0, ATLAS, top - 3.0, top - 2.0, 0.82, ao=0.85)


def paint_rear_fascia(c):
    """The rear (low) edge: the steel fascia with a half-round galvanised
    gutter across its top, under the sheet's drip edge, as on
    konehalli_open_bays."""
    y0 = FASC_R_Y0
    top = EAVE_ROOF_Y0
    c.paint(0, ATLAS, y0 - 2, top, ID_METAL, 1.0, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, top - 1.0, CASING_H, 1.0, axes="y")
    c.mul(0, ATLAS, y0 - 2, y0 + 1, 0.82)
    gh = GUTTER_PX
    g0 = top - 1 - gh
    c.paint(0, ATLAS, g0, top - 1, ID_GUTTER, 1.0, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top - 1)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_GUTTER, 0.80)
    c.paint(0, ATLAS, top - 1, top, ID_ROOF, 0.80, height=0.0)
    sy, sx = c.sl(0, ATLAS, g0 - 3, top)
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.9)
    for k, f in enumerate((0.92, 0.86, 0.80)):
        c.mul(0, ATLAS, g0 - 3 + k, g0 - 2 + k, f)
    sy, sx, _, X = c.field(0, ATLAS, g0 + 2, top - 1)
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.80, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_eave_roof(c):
    """The roof's lowest EAVE_STRIP_LEN at EAVE_RPM rows a metre, resampled
    from the finished ROOF band's rows (paint, weather and all) so the slab's
    top changes band without a seam, and the snow guard on it: two tubes on
    brackets every metre, heights scaled by EAVE_RPM / PPM. As
    konehalli_open_bays paints its own."""
    ss = c.ss
    r0 = c._idx(EAVE_ROOF_Y0)
    rows = np.arange(r0, ATLAS * ss)
    Y = (rows + 0.5) / ss
    s = (Y - EAVE_ROOF_Y0) / EAVE_RPM
    src = (ROOF_Y0 + s * ROOF_RPM) * ss - 0.5
    i0 = np.floor(src).astype(np.int64)
    f = (src - i0).astype(np.float32)[:, None]
    i1 = i0 + 1
    near = np.where(f[:, 0] < 0.5, i0, i1)
    c.mid[r0:] = c.mid[near]
    for a in (c.shade, c.ao, c.height):
        a[r0:] = a[i0] * (1.0 - f) + a[i1] * f
    w = c.weather
    for k in w.f:                   # coal dust's K among them
        w.f[k][r0:] = w.f[k][i0] * (1.0 - f) + w.f[k][i1] * f

    rpm = EAVE_RPM
    k = rpm / PPM
    y0 = EAVE_ROOF_Y0
    g = round(SNOW_S * rpm)
    sy, sx, Y, X = c.field(0, ATLAS, y0, ATLAS)
    v = Y - y0
    mid, height = c.mid[sy, sx], c.height[sy, sx]
    shade, ao = c.shade[sy, sx], c.ao[sy, sx]
    rail = np.zeros(Y.shape, bool)
    for t0, t1 in ((g, g + 2.0), (g + 3.0, g + 4.5)):
        inside = (v >= t0) & (v < t1)
        tube = SNOW_TUBE_H * k * np.sqrt(np.clip(
            1.0 - (2.0 * (v - t0) / (t1 - t0) - 1.0) ** 2, 0, 1))
        height = np.where(inside, tube, height)
        shade = np.where(inside, 1.0, shade)
        rail |= inside
    shade = np.where((v >= g - 3) & (v < g - 1), shade * 0.80, shade)
    shade = np.where((v >= g + 2.0) & (v < g + 3.0), shade * 0.85, shade)
    ao = np.where((v >= g - 3) & (v < g + 4.5), np.minimum(ao, 0.85), ao)
    xm = X % PPM
    bracket = (xm >= 0.6) & (xm < 2.6) & (v >= g - 3) & (v < g + 4.5)
    height = np.where(bracket, SNOW_BRACKET_H * k, height)
    shade = np.where(bracket, 0.75, shade)
    rail |= bracket
    c.mid[sy, sx] = np.where(rail, ID_GUTTER, mid)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao
    for key in w.f:
        w.f[key][sy, sx] = np.where(rail, 0.0, w.f[key][sy, sx])
    w.add("D", 0, ATLAS, y0 + g - 3, y0 + g + 4.5,
          lambda Y, X, nz: 0.08 + 0.10 * nz("blotch"), (ID_GUTTER,))
    w.add("R", 0, ATLAS, y0 + g - 3, y0 + g + 4.5, lambda Y, X, nz: 0.15 * (
        ((X % PPM) >= 0.6) & ((X % PPM) < 2.6)), (ID_GUTTER,))
    w.add("D", 0, ATLAS, y0 + g + 4.5, y0 + g + 10.0, lambda Y, X, nz: 0.22
          * nz("blotch") * (1.0 - (Y - y0 - g - 4.5) / 5.5), (ID_ROOF,))


def lane_fall(e, start=0.2, end=3.2):
    """0 at the lane's mouth, 1 in its middle; *e* metres from the nearer end."""
    return atlas.smoothstep(start, end, e)


def paint_lane_side(c):
    """The lane's two side walls, U along the lane from its front mouth and V
    up from the ground, at LPM: board-formed concrete, a low kerb, a steel
    wheel guard, and occlusion deepening toward the middle of the lane's
    length and into both of its corners."""
    x0, y0, w, h = LANE_SIDE
    k = LPM / PPM
    paint_concrete(c, x0 - 2, x0 + w + 2, y0, y0 - 2, y0 + h + 2, LPM, seed=53)
    # kerb: smoother concrete, its top edge chamfered
    yk = y0 + 0.25 * LPM
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, yk, ID_CONC, 0.93, 1.0, height=0.0)
    c.mul(x0 - 2, x0 + w + 2, yk - 0.6, yk, 0.80, ao=0.8)
    # the wheel guard: a steel channel at 0.45 .. 0.60 m on brackets
    r0, r1 = y0 + 0.45 * LPM, y0 + 0.60 * LPM
    c.paint(x0 - 2, x0 + w + 2, r0, r1, ID_STEEL, 1.0, 1.0)
    c.bevel(x0 - 2, x0 + w + 2, r0, r1, RAIL_H * k, 0.8, axes="y")
    c.mul(x0 - 2, x0 + w + 2, r0 - 1.5, r0, 0.70, ao=0.6)
    sy, sx, Y, X = c.field(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2)
    e = np.minimum(X - x0, x0 + w - X) / LPM
    z = (Y - y0) / LPM
    f = lane_fall(e)
    corner = 0.14 * np.exp(-np.clip(z, 0, None) / 0.30) + 0.16 * np.exp(
        -np.clip(Z_DECK - z, 0, None) / 0.35)
    c.shade[sy, sx] *= (1.0 - (1.0 - SIDE_SHADE) * f) * (1.0 - corner)
    c.ao[sy, sx] *= (1.0 - (1.0 - SIDE_AO) * f) * (1.0 - 1.5 * corner)


def paint_lane_ceil(c):
    """The bunker's underside over the lane, U across the lane from its west
    wall and V along it from the front mouth, at LPM: concrete cast on boards
    running along the lane, two downstand beams painted across it between
    the hoppers, a steel flange round each hopper's throat, and occlusion
    that falls further than the walls'."""
    x0, y0, w, h = LANE_CEIL
    k = LPM / PPM
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_CONC, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2)
    u = (X - x0) / LPM
    yy = (Y - y0) / LPM - HY                     # plan y
    col = np.floor(u / BOARD_H).astype(np.int64)
    line = (u - col * BOARD_H) * LPM < 0.6
    tone = 1.0 + 0.05 * (atlas.hash_unit(61, col) - 0.5)
    shade = np.where(line, tone * 0.90, tone)
    height = np.where(line, -BOARD_LINE_H * k, 0.0)
    ao = np.where(line, 0.88, 1.0)
    mid = np.full(Y.shape, ID_CONC, np.uint8)
    # downstand beams across the lane, 0.30 m faces, between the hoppers
    for yb in (-1.25, 1.25):
        d = np.abs(yy - yb)
        on = d < 0.15
        height = np.where(on, BEAM_H * k * np.clip((0.15 - d) * LPM / 1.0, 0, 1), height)
        shade = np.where(on, tone * 1.02, shade)
        side = (d >= 0.15) & (d < 0.15 + 1.5 / LPM)
        shade = np.where(side, shade * 0.80, shade)
        ao = np.where(side, 0.7, ao)
    # the hoppers' flanges: 0.08 m of steel round each throat
    hx, hy = hop_at_deck()
    xc = LANE_C - XL0
    for yc in HOP_Y:
        dx = np.abs(u - xc) - hx / 2.0
        dy = np.abs(yy - yc) - hy / 2.0
        ring = (np.maximum(dx, dy) < 0.08) & (np.maximum(dx, dy) > -0.05)
        mid = np.where(ring, ID_STEEL, mid)
        height = np.where(ring, 0.010 * k, height)
        shade = np.where(ring, 0.95, shade)
        bolt = ring & ((np.mod((u - xc) * LPM, 6.0) < 1.0) | (np.mod((yy - yc) * LPM, 6.0) < 1.0))
        shade = np.where(bolt, shade * 0.85, shade)
    e = HY - np.abs(yy)
    f = lane_fall(e, 0.0, 3.0)
    edge = 0.14 * np.exp(-np.clip(np.minimum(u, (XL1 - XL0) - u), 0, None) / 0.35)
    fs = (1.0 - (1.0 - CEIL_SHADE) * f) * (1.0 - edge)
    fa = (1.0 - (1.0 - CEIL_AO) * f) * (1.0 - 1.5 * edge)
    c.mid[sy, sx] = mid
    c.shade[sy, sx], c.ao[sy, sx], c.height[sy, sx] = shade * fs, ao * fa, height


def paint_chute(c):
    """One side of a hopper: steel plate with a flange along its top, two
    stiffeners down it and the gate's frame along its foot."""
    x0, y0, w, h = CHUTE
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_STEEL, 1.0, 1.0, height=0.0)
    c.paint(x0 - 2, x0 + w + 2, y0 + h - 5, y0 + h + 2, ID_STEEL, 1.05, 1.0)
    c.bevel(x0 - 2, x0 + w + 2, y0 + h - 5, y0 + h + 2, 0.010, 1.0, axes="y")
    c.mul(x0 - 2, x0 + w + 2, y0 + h - 6, y0 + h - 5, 0.75, ao=0.75)
    for xs in (x0 + w / 3.0, x0 + 2.0 * w / 3.0):
        c.paint(xs - 1.0, xs + 1.0, y0 + 6, y0 + h - 5, ID_STEEL, 1.04, 1.0)
        c.bevel(xs - 1.0, xs + 1.0, y0 + 6, y0 + h - 5, 0.012, 0.6, axes="x")
        c.mul(xs + 1.0, xs + 2.0, y0 + 6, y0 + h - 5, 0.82, ao=0.8)
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + 6, ID_STEEL, 0.80, 0.85)
    c.bevel(x0 - 2, x0 + w + 2, y0, y0 + 6, 0.012, 1.0, axes="y")


def paint_window(c, kind="win"):
    """A small steel window: a sheet-steel flashing round it with a sloped
    sill and a drip head, a steel frame, and glazing bars dividing it four
    lights wide and three high. glazing.rooms() owns the glass's colour."""
    x0, y0 = ITEM_ORIGIN[kind]
    w, h, cs, cb, ct = OPENINGS[kind]
    rw, rh = item_size_px(kind)
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0 + m(cb), y0 + m(cb + h)
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, ID_METAL, 1.0, 1.0, height=0.0)
    c.bevel(x0, x0 + rw, y0, y0 + rh, CASING_H, 1.0)
    sy, sx, Y, _ = c.field(x0 - 2, x0 + rw + 2, y0 - 2, oy0)
    c.height[sy, sx] = 0.030 - 0.020 * np.clip((Y - y0) / m(cb), 0.0, 1.0)
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + 1, ID_METAL, 0.78, 0.8)
    c.mul(ox0 - 1, ox1 + 1, oy1, oy1 + 1.5, 0.80, ao=0.8)
    f = m(0.05)
    c.paint(ox0, ox1, oy0, oy1, ID_SASH, 1.0, 1.0)
    c.bevel(ox0, ox1, oy0, oy1, FRAME_H, 1.0)
    gx0, gx1, gy0, gy1 = ox0 + f, ox1 - f, oy0 + f, oy1 - f
    c.paint(gx0, gx1, gy0, gy1, ID_GLASS, ao=0.9, height=0.0)
    bar = m(0.03)
    for i in (1, 2, 3):
        xb = gx0 + (gx1 - gx0) * i / 4.0
        c.paint(xb - bar / 2, xb + bar / 2, gy0, gy1, ID_SASH, 1.0, 1.0, height=BAR_H)
    for j in (1, 2):
        yb = gy0 + (gy1 - gy0) * j / 3.0
        c.paint(gx0, gx1, yb - bar / 2, yb + bar / 2, ID_SASH, 1.0, 1.0, height=BAR_H)
    c.mul(gx0, gx1, gy1 - 1.5, gy1, 0.82, ao=0.8)
    c.mul(gx0, gx0 + 1.0, gy0, gy1, 0.88)


def paint_door(c):
    """The control room's door: a painted steel leaf with two pressed
    panels in a steel frame, a lever handle on the right (hinges left), a
    kick plate along its foot."""
    x0, y0 = ITEM_ORIGIN["door"]
    w, h, cs, cb, ct = OPENINGS["door"]
    rw, rh = item_size_px("door")
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0, y0 + m(h)
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, ID_SASH, 1.0, 1.0, height=0.0)
    c.bevel(x0, x0 + rw, y0 - 3, y0 + rh, CASING_H, 1.0)
    c.paint(ox0, ox1, oy0, oy1, ID_DOOR, 1.0, 1.0, height=0.0)
    c.mul(ox0, ox1, oy1 - 1.5, oy1, 0.80, ao=0.8)                  # head shadow
    for p0, p1 in ((0.30, 0.95), (1.15, 1.95)):
        a, b = oy0 + m(p0), oy0 + m(p1)
        px0, px1 = ox0 + m(0.12), ox1 - m(0.12)
        c.bevel(px0, px1, a, b, -0.006, 1.2, base=0.0)
        c.mul(px0, px1, b - 1.0, b, 0.84, ao=0.85)
        c.mul(px0, px0 + 1.0, a, b, 0.90)
    c.paint(ox0, ox1, oy0, oy0 + m(0.22), ID_STEEL, 1.0, 0.9, height=0.003)
    hx = ox1 - m(0.09)
    hy = oy0 + m(1.02)
    c.paint(hx - m(0.13), hx + 1.0, hy - 1.0, hy + 1.0, ID_HW, 1.0, 0.9, height=0.030)
    c.paint(hx - 1.5, hx + 1.5, hy - 5.0, hy + 3.0, ID_HW, 0.9, 0.9, height=0.012)
    c.mul(ox0, ox0 + 1.0, oy0, oy1, 0.80, ao=0.8)                   # hinge-side gap
    c.mul(ox1 - 1.0, ox1, oy0, oy1, 0.80, ao=0.8)


def paint_door_v(c):
    """The intake's sliding door: profiled steel in the door's paint, framed
    in steel, under a track hood, with two pull handles."""
    x0, y0 = ITEM_ORIGIN["door_v"]
    w, h, cs, cb, ct = OPENINGS["door_v"]
    rw, rh = item_size_px("door_v")
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0, y0 + m(h)
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, ID_STEEL, 1.0, 1.0, height=0.0)
    c.bevel(x0, x0 + rw, y0 - 3, y0 + rh, CASING_H, 1.0)
    paint_sheet(c, ox0, ox1, oy0, oy1, ID_DOOR, seed=71, rib_h=0.020)
    fr = m(0.08)
    for rx0, rx1, ry0, ry1 in ((ox0, ox0 + fr, oy0, oy1), (ox1 - fr, ox1, oy0, oy1),
                               (ox0, ox1, oy0, oy0 + fr), (ox0, ox1, oy1 - fr, oy1),
                               (ox0, ox1, oy0 + m(1.25), oy0 + m(1.25) + fr)):
        c.paint(rx0, rx1, ry0, ry1, ID_DOOR, 1.04, 1.0)
        c.bevel(rx0, rx1, ry0, ry1, 0.012, 0.8)
    top = y0 + rh
    c.paint(x0 - 2, x0 + rw + 2, top - m(0.12), top + 2, ID_STEEL, 0.95, 1.0)
    sy, sx, Y, _ = c.field(x0 - 2, x0 + rw + 2, top - m(0.12), top + 2)
    c.height[sy, sx] = 0.040 - 0.020 * np.clip((Y - (top - m(0.12))) / m(0.12), 0, 1)
    c.mul(x0 - 2, x0 + rw + 2, top - m(0.12) - 2, top - m(0.12), 0.72, ao=0.7)
    for hx in (ox0 + m(0.20), ox1 - m(0.20)):
        c.paint(hx - 1.0, hx + 1.0, oy0 + m(0.85), oy0 + m(1.15), ID_HW, 1.0, 0.9,
                height=0.030)


def paint_patches(c):
    spec = {"blank": (ID_BLANK, 1.0, 0.5), "reveal": (ID_STEEL, 0.75, 0.6),
            "soffit": (ID_ROOF, 0.72, 0.75), "coal": (ID_COAL, 1.0, 0.5),
            "gal_under": (ID_STEEL, 0.70, 0.65), "coping": (ID_CONC, 1.02, 1.0),
            "felt": (ID_FELT, 1.0, 1.0), "slab_under": (ID_CONC, 0.75, 0.75),
            "steel": (ID_STEEL, 1.0, 1.0)}
    for name, (x0, y0, w, h) in PATCHES.items():
        mid, sh, ao = spec[name]
        c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, mid, sh, ao, height=0.0)


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    Dirt resolves to the neutral dust weathering.py keeps for steel on every
    id, not to soil. w.coal() lays the coal itself (weathering's K field): heavy
    on the legs' feet, in the lane, round and on the hoppers, on the
    gallery's floor and the intake's roof under it; light on the cladding
    above, a working plant's dust, not neglect."""
    w = Weather(c, clean=(ID_GLASS,),
                steel=tuple(i for i in SURFACE if i != ID_GLASS), coal_dust=COAL_DUST)
    w.grime(0.045)
    w.fade((ID_CLAD, ID_DOOR, ID_SASH, ID_METAL, ID_ROOF))
    w.wash((ID_CLAD, ID_CONC))
    # S1: plinth, splash, coal dust thrown up by the wheels, runs down the
    # ring beam from the flashing above it
    w.plinth(0, ATLAS, S1_Y0, S1_Y0 + m(Z_PLINTH), (ID_CONC,))
    w.splash(0, ATLAS, S1_Y0 + m(Z_PLINTH), S1_TOP, (ID_CONC,))
    # S1's V is height from the ground on every wall, so the coal the wheels
    # throw up can follow it: heavy at the legs' feet, fading by 2 m
    w.coal(0, ATLAS, 0, S1_TOP, lambda Y, X, nz: (FOOT_COAL * np.exp(
        -np.clip(Y - S1_Y0, 0, None) / m(FOOT_FALL)) * (0.65 + 0.35 * nz("blotch"))
        + 0.06 + 0.08 * nz("big")
        + 0.14 * atlas.smoothstep(0.3, 1.8, nz("long"))), (ID_CONC,))
    f0 = S1_TOP - m(0.15)
    w.runs(0, ATLAS, S1_Y0 + m(Z_DECK) + 2, f0 - 1, (ID_CONC,), 0.20, fall=18.0)
    w.runs(0, ATLAS, S1_Y0 + m(1.0), S1_Y0 + m(Z_DECK) - 1, (ID_CONC,), 0.06,
           fall=60.0, noise="long")
    # the cladding band and the columns: dust in broad periodic patches and
    # streaks, nothing that follows height
    rows = (C_Y0 - C_G, C_Y0 + C_H + C_G)
    w.add("D", 0, ATLAS, rows[0], rows[1], lambda Y, X, nz: 0.08 * nz("big")
          + 0.10 * atlas.smoothstep(0.4, 1.8, nz("long")), (ID_CLAD, ID_CONC))
    w.coal(0, ATLAS, rows[0], rows[1], lambda Y, X, nz: 0.05 + 0.07 * nz("big")
           + 0.14 * atlas.smoothstep(0.2, 1.8, nz("long"))
           + 0.05 * atlas.smoothstep(0.5, 1.6, nz("runs")), (ID_CLAD, ID_CONC))
    # roof, fascia, rear fascia and gutter
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, ROOF_LEN, (ID_ROOF,))
    w.add("D", 0, ATLAS, ROOF_Y0 - 2, ROOF_Y0 + ROOF_H + 2,
          lambda Y, X, nz: 0.12 * nz("blotch") + 0.08, (ID_ROOF,))
    w.runs(0, ATLAS, FASC_Y0 - 2, FASC_Y0 + FASC_H - 2, (ID_METAL,), 0.18, fall=6.0,
           lo=0.4, hi=1.6)
    top = EAVE_ROOF_Y0
    g0 = top - 1 - GUTTER_PX
    w.add("D", 0, ATLAS, FASC_R_Y0 - 2, g0, 0.06, (ID_METAL,))
    w.runs(0, ATLAS, FASC_R_Y0 - 2, g0, (ID_METAL,), 0.22, fall=6.0, lo=0.4, hi=1.6)
    w.add("D", 0, ATLAS, g0, g0 + 4, lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"),
          (ID_GUTTER,))
    w.runs(0, ATLAS, g0, top - 1, (ID_GUTTER,), 0.08, fall=4.0, lo=0.4, hi=1.6)
    # the lane: coal dust on everything, thickest at the foot of the walls
    # and round the hoppers' throats
    x0, y0, lw, lh = LANE_SIDE
    w.add("D", x0 - 2, x0 + lw + 2, y0 - 2, y0 + lh + 2, lambda Y, X, nz: 0.10
          + 0.08 * nz("blotch"))
    w.coal(x0 - 2, x0 + lw + 2, y0 - 2, y0 + lh + 2, lambda Y, X, nz: LANE_COAL
           + 0.10 * nz("blotch") + 0.60 * np.exp(
               -np.clip(Y - y0, 0, None) / (1.0 * LPM)))
    x0, y0, cw, ch = LANE_CEIL
    hx, hy = hop_at_deck()

    def round_hoppers(Y, X, nz):
        u = (X - x0) / LPM - (LANE_C - XL0)
        yy = (Y - y0) / LPM - HY
        d = np.min([np.hypot(np.clip(np.abs(u) - hx / 2, 0, None),
                             np.clip(np.abs(yy - yc) - hy / 2, 0, None)) for yc in HOP_Y],
                   axis=0)
        return LANE_COAL + 0.08 * nz("blotch") + 0.55 * np.exp(-d / 0.7)
    w.add("D", x0 - 2, x0 + cw + 2, y0 - 2, y0 + ch + 2, lambda Y, X, nz: 0.10
          + 0.10 * nz("blotch"))
    w.coal(x0 - 2, x0 + cw + 2, y0 - 2, y0 + ch + 2, round_hoppers)
    # the hoppers: dusted all over, caked toward the mouth
    x0, y0, hw_, hh = CHUTE
    w.coal(x0 - 2, x0 + hw_ + 2, y0 - 2, y0 + hh + 2,
           lambda Y, X, nz: 0.35 + 0.45 * np.clip(1.0 - (Y - y0) / hh, 0, 1))
    w.add("R", x0 - 2, x0 + hw_ + 2, y0 - 2, y0 + hh + 2,
          lambda Y, X, nz: 0.12 * nz("speck") + 0.06 * nz("blotch"))
    # flat patches: the gallery's floor and the intake's roof under it take
    # the spill; the reveals and the slab's soffit less
    for name, k in (("gal_under", 0.55), ("felt", 0.60), ("slab_under", 0.30),
                    ("steel", 0.30), ("reveal", 0.25)):
        px, py, pw, ph = PATCHES[name]
        w.coal(px - 2, px + pw + 2, py - 2, py + ph + 2, k)
    # the column strip and the openings
    for kind, (wd, h, cs, cb, ct) in OPENINGS.items():
        ix, iy = ITEM_ORIGIN[kind]
        rw, rh = item_size_px(kind)
        ox0, ox1 = ix + m(cs), ix + m(cs + wd)
        oy0, oy1 = iy + m(cb), iy + m(cb + h)
        if kind == "win":
            w.window(ix, iy, rw, rh, oy0, oy1, m(0.05), (ID_METAL,), (ID_SASH,))
        else:
            hx_ = ox1 - m(0.09) if kind == "door" else (ox0 + ox1) / 2.0
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR, ID_STEEL), handle=(hx_, oy0 + m(1.02)))
            w.coal(ix - 2, ix + rw + 2, iy - 2, iy + m(0.8),
                   lambda Y, X, nz, iy=iy: 0.45 * np.exp(-np.clip(Y - iy, 0, None) / m(0.35)))
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_s1(c)
    paint_c(c)
    paint_roof(c)
    paint_fascia(c)
    paint_rear_fascia(c)
    paint_lane_side(c)
    paint_lane_ceil(c)
    paint_chute(c)
    paint_window(c)
    paint_door(c)
    paint_door_v(c)
    paint_patches(c)

    wear = 0.025 * noise(c, 3, 40.0) + 0.015 * noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    concrete = c.mid == ID_CONC
    pores = noise(c, 9, 0.8)
    c.shade[concrete] *= 1.0 + 0.035 * pores[concrete]
    c.height[concrete] += 0.0006 * pores[concrete]
    sheet = np.isin(c.mid, (ID_CLAD, ID_ROOF))
    streak = noise(c, 7, 0.8, 40.0)
    c.shade[sheet] *= 1.0 + 0.035 * streak[sheet]
    weather(c)
    paint_eave_roof(c)              # resamples the finished ROOF band
    c.check_bands(BAND_IDS)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    t[ID_CLAD] = pal["clad"]
    t[ID_ROOF] = pal["roof"]
    t[ID_METAL] = np.minimum(np.array(pal["roof"], np.float32) * 1.25 + 8, 255)
    t[ID_DOOR] = pal["door"]
    t[ID_SASH] = pal["sash"]
    return t


def export(out_dir, ss=atlas.SS):
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.012)
    c.weather.dust(cav, (ID_CLAD, ID_CONC))
    rough = 0.04 * noise(c, 13, 20.0)
    path = os.path.join(out_dir, ASSET)
    glass_any = atlas.coverage(c, ID_GLASS) > 0
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS,)), path + "_normal.png"),
               atlas.save(glazing.night_rooms(glass_any, atlas.emission(c, ID_GLASS)),
                          path + "_emission.png")]
    glass = atlas.coverage(c, ID_GLASS) >= 0.5
    for v in VARIANTS:
        rgb = glazing.rooms(glass, atlas.albedo(c, lut(v), grime=0.25 * cav),
                            base=GLASS_BASE)
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        os.makedirs(os.path.join(here, "export"), exist_ok=True)
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
