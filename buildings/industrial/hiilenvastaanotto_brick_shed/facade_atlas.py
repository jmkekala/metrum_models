# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
hiilenvastaanotto_brick_shed.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share
(plan, heights, opening sizes, band rows, region rectangles), so a change
here cannot leave the UVs pointing at the wrong artwork. Importing it only
defines those constants; the painting runs when paint() is called.
Rasterising is scripts/atlas.py's; dirt, algae, rust, faded paint and coal
dust are scripts/weathering.py's fields, placed by weather() below.

A trim sheet. Rows from the bottom:

    y    0 ..  422   BRICK   z 0 .. 6.5625 m at 64 px/m, x 0 .. 960: concrete
                             plinth, stretcher-bond facing brick, the cast
                             concrete band (the portal lintels and the ring
                             beam) at 6.0 .. 6.5625; the concrete frame's
                             column strip beside it at x 972, same rows
    y  426 ..  526   ROOF    profiled roof sheet, V stretched up the slope,
                             snow guard near the eave, ridge cap at the top
    y  530 ..  550   EAVE    the eave fascia with its gutter
    y  556 .. 1020   unique  the lane's side walls, ceiling and floor with the
                             tipping grate (32 px/m), the windows, the doors,
                             the loading hatch, the louvre, the head house's
                             cladding (CLAD), the conveyor gallery's sides
                             (GAL_SIDE) and closed end (GAL_END), flat patches

Every wall above the band's top (6.5625 m) samples the brick rows again,
GABLE_SHIFT or twice that lower, a whole tone period of courses, so the bond
runs on across the line: the gable triangles, the main walls' strip under
the eave and the elevator tower's brick shaft to 12.4 m all come from one
band.
Weather that follows height stays below SAMPLE_LO, the lowest row any shifted
wall samples, so the shift never shows as a seam.
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

ASSET = "hiilenvastaanotto_brick_shed"
ATLAS = 1024
PPM = 64.0
LPM = 32.0              # px/m in the lane's own regions
PAD = 2                 # rows each band paints beyond its own edge

# ------------------------------------------------------------------ plan
# Metres, build frame: Z up, front toward -Y. The shed is 14.0 x 6.4 m, its
# long sides to the front and the rear; the truck lane runs straight through
# it along X, from the mouth in the west gable to the mouth in the east one.
HX = 7.0                         # half the shed's length: the mouths' planes
Y_F, Y_R = -3.4, 3.0             # front and rear walls' outer faces
WALL_T = 0.4                     # every wall of the shed, and the portal piers
YL0, YL1 = Y_F + WALL_T, Y_R - WALL_T   # the lane's side walls: 5.60 m clear
YC = (Y_F + Y_R) / 2.0           # the shed's and the lane's centre line, the ridge
X_IN = HX - WALL_T               # the gable walls' inner faces
HALF_SPAN = (Y_R - Y_F) / 2.0
FLOOR_T = 0.02                   # the lane's floor slab, top over the ground

# ------------------------------------------------------------ vertical layout
# Every height is a whole number of texels at 64 px/m.
Z_PLINTH = 0.625        # 40 px: cast concrete base under every wall
Z_BAND0 = 6.0           # 384 px: the band's foot, the mouths' heads
Z_BAND1 = 6.5625        # 420 px: its top, and the top of the brick band
Z_MOUTH = Z_BAND0       # the portal lintels' soffit: the lane's clear height
Z_WIN = 4.25            # 272 px: the shed's high windows' sill ...
WIN_W, WIN_H = 2.8, 1.75  # ... their head under the band at 6.0
Z_EAVE = 7.2            # the main roof's underside at the long walls' faces
TAN = 0.12              # 6.8 degrees, a low working-shed gable, ridge along X
ROOF_T = 0.25
EAVE_OV, RAKE_OV = 0.40, 0.30
WALL_INTO = 0.12        # walls run this far up into a roof slab
CEIL_DROP = 0.30        # the lane's ceiling (sheet and purlins) under the roof
SLOPE_F = math.sqrt(1.0 + TAN * TAN)
MAIN_SLOPE = (HALF_SPAN + EAVE_OV) * SLOPE_F      # eave edge to ridge, 3.711 m

# The concrete frame: columns flush in the brick at the corners and at two
# intermediate frames, whose tie beams cross the lane under its ceiling.
COL_W = 0.40
FRAME_X = (-2.4, 2.4)
Z_BEAM = 6.20           # the tie beams' soffit, over the lintels' 6.00
BEAM_W = 0.30

# The annex behind the shed (+Y, the side that faces the hall's coal side):
# a brick lean-to with the attendant's room and the drive room, and the
# elevator tower rising through it. The annex's front runs ANNEX_BURY into
# the shed's rear wall.
ANNEX_BURY = 0.10
AX0, AX1 = -4.5, 4.7
AY0, AY1 = Y_R - ANNEX_BURY, 6.6
Z_AE = 3.5              # the lean-to roof's underside at the annex's rear face
TAN_A = 0.10            # 1:10, falling to the rear
A_EAVE_OV, A_RAKE_OV = 0.30, 0.30
A_SLAB_Y0 = Y_R - 0.20  # the lean-to slab's high end, buried in the shed's wall
SLOPE_FA = math.sqrt(1.0 + TAN_A * TAN_A)

# The elevator tower, housing the bucket elevator from the pit under the
# grate and its stair: a slim brick shaft 2.6 x 4.1 m in plan, standing 0.4 m
# proud of the annex's rear face, and on it the head house, sheet-clad,
# oversailing the shaft by HH_OV on the front and both sides and flush with
# its rear face, where the inclined conveyor gallery leaves it.
TX0, TX1 = -1.3, 1.3
TY0, TY1 = AY0, 7.0
HH_OV = 0.70
HX0, HX1 = TX0 - HH_OV, TX1 + HH_OV          # the head house: x -2.0 .. 2.0
HY0, HY1 = TY0 - HH_OV, TY1                  # ... y 2.2 .. 7.0
HH_Z0 = 12.30           # its floor: the shaft's top, the oversail's soffit
Z_TSLAB = 16.25         # its flat roof slab, 16.25 .. 16.50
T_SLAB_T = 0.25
T_OV = 0.15
Z_TOWER_TOP = HH_Z0 + WALL_INTO     # the shaft's lid, inside the head house
Z_HH_TOP = Z_TSLAB + WALL_INTO      # the head house walls' lid, inside the slab

# The inclined conveyor gallery: an enclosed box 2.6 m wide and 2.8 m tall
# in vertical section, leaving the head house's rear face (the shaft's rear
# face plane, TY1) with its centre line at GAL_Z0 and rising at GAL_ANG
# degrees away from the building, toward +Y, GAL_LEN metres in plan to a
# closed end. It is carried as a cantilever on two raking steel struts back
# to the shaft's rear face: nothing of it reaches the ground.
GAL_W, GAL_H = 2.6, 2.8
GAL_ANG = 20.0
GAL_TAN = math.tan(math.radians(GAL_ANG))
GAL_Z0 = 14.0
GAL_LEN = 4.0
GAL_Y1 = TY1 + GAL_LEN                       # its end face's plane, 11.0
GAL_Z1 = GAL_Z0 + GAL_LEN * GAL_TAN          # its end's centre, 15.456
GAL_BURY = 0.30                              # it starts this far inside the head house
GAL_END_RIM = 0.15                           # the end face's rim round its panel
GAL_END_RECESS = 0.08                        # the panel's set-back at the close tiers
STRUT_X = (-1.0, 1.0)                        # the two struts, under the gallery
STRUT_W = 0.20
STRUT_FOOT = (TY1, 9.80)                     # (y, z) of their axis at the shaft's face
STRUT_TOP_Y = TY1 + 3.40                     # ... and under the gallery's floor
# The hoist beam over the head house's loading hatch, east face
HOIST_Y = 4.6
HOIST_OUT = 1.10
HOIST_Z = (15.55, 15.80)
HOIST_W = 0.16


def gal_floor(y):
    """The gallery's underside over plan y (its floor's outside)."""
    return GAL_Z0 - GAL_H / 2.0 + (y - TY1) * GAL_TAN

# Walls above the band sample the brick rows lower by these, in bands split
# at these heights. A shift is a whole tone period (48 courses, 3.75 m).
SPLITS = (Z_BAND1, Z_BAND1 + 3.0)            # 6.5625, 9.5625
SHIFTS = (0.0, 3.75, 7.5)
SAMPLE_LO = 2.0         # the lowest z any shifted wall samples (checked)
SAMPLE_HI = 5.88        # ... and the highest

# The lane is used one way, in at the west (-X) mouth and out at the east.
# A truck stops with its centre at the lane's centre (STOP_X); a rear-tipping
# truck's tail is then toward the entry, so the tipping grate lies on the
# centre line 2.5 m toward the west mouth, 3.0 m along the lane.
STOP_X = 0.0
GRATE_C = -2.5
GRATE_X = (GRATE_C - 1.5, GRATE_C + 1.5)
GRATE_Y = (YC - 2.0, YC + 2.0)


def roof_under(y):
    """The main gable roof's underside over plan y."""
    return Z_EAVE + (HALF_SPAN - abs(y - YC)) * TAN


def ceil_z(y):
    """The lane's ceiling over plan y."""
    return roof_under(y) - CEIL_DROP


def annex_under(y):
    """The lean-to roof's underside over plan y."""
    return Z_AE + (AY1 - y) * TAN_A


CEIL_LEN = (YC - YL0) * SLOPE_F                    # wall edge to apex, 2.886 m
A_SLAB_Y1 = AY1 + A_EAVE_OV                        # 6.9: the lean-to's eave edge
ANNEX_SLOPE = (A_SLAB_Y1 - A_SLAB_Y0) * SLOPE_FA   # its slab, buried end to edge
# The lean-to samples the roof band scaled by this, so its buried end stays
# under the ridge cap the main roof's top rows carry.
ANNEX_V_K = (MAIN_SLOPE - 0.25) / ANNEX_SLOPE

# ------------------------------------------------------------------ openings
# kind -> (width, height) of the opening in the brick, metres; the region it
# maps onto is the same size. Steel frames are set back REVEAL metres.
OPENINGS = {
    "win": (WIN_W, WIN_H), "win_b": (WIN_W, WIN_H),
    "win_s": (0.9, 1.2), "win_s_b": (0.9, 1.2),
    "door": (1.05, 2.15),       # a 0.95 x 2.10 leaf in a 0.05 m steel frame
    "hatch": (1.2, 1.2),        # the head house's loading hatch, under the hoist beam
    "louvre": (1.0, 0.6),
}
REVEAL = {"win": 0.20, "win_b": 0.20, "win_s": 0.15, "win_s_b": 0.15,
          "door": 0.20, "hatch": 0.12, "louvre": 0.12}
DOOR_FRAME = 0.05
LEAF_W, LEAF_H = OPENINGS["door"][0] - 2 * DOOR_FRAME, OPENINGS["door"][1] - DOOR_FRAME

# ------------------------------------------------------------------- bands
BRICK_Y0 = 0
BRICK_H = 420                    # z 0 .. Z_BAND1
BRICK_W = 960.0                  # the brick band's width; U stays inside it
COL = (972.0, 0.0, COL_W * PPM, BRICK_H)      # the column strip, same rows
ROOF_Y0, ROOF_H = 428, 96
ROOF_LEN = MAIN_SLOPE + 0.10     # metres up the slope ROOF_H rows cover
ROOF_RPM = ROOF_H / ROOF_LEN
EAVE_Y0, EAVE_H = 532, 16        # the eave fascia, ROOF_T tall
GUTTER_PX = 9
PIPE_STRIP = (EAVE_Y0 + EAVE_H - GUTTER_PX + 2, EAVE_Y0 + EAVE_H - 2)
SNOW_GUARD = 0.55                # the snow guard's lower tube, up the slope
RIB_P = 16.0                     # profiled sheet: a rib every 0.25 m

COURSE = 0.078125                # brick course pitch: 5 px
BRICK_L = 0.25                   # stretcher: 16 px
TONE_COURSES = 48                # brick tone repeats every 3.75 m

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels. The lane's at LPM, the rest at 64 px/m.
UNI_Y = 556
LANE_SIDE = (4.0, 558.0, 2 * HX * LPM, 7.7 * LPM)            # 448 x 246.4
LANE_CEIL = (4.0, 812.0, 2 * HX * LPM, CEIL_LEN * LPM)       # 448 x 92.4
LANE_FLOOR = (460.0, 558.0, 2 * HX * LPM, (YL1 - YL0) * LPM)  # 448 x 179.2
REGION = {
    "win": (460.0, 746.0, WIN_W * PPM, WIN_H * PPM),
    "win_b": (460.0, 866.0, WIN_W * PPM, WIN_H * PPM),
    "win_s": (648.0, 746.0, 0.9 * PPM, 1.2 * PPM),
    "win_s_b": (648.0, 830.0, 0.9 * PPM, 1.2 * PPM),
    "door": (714.0, 746.0, 1.05 * PPM, 2.15 * PPM),
    "hatch": (790.0, 746.0, 1.2 * PPM, 1.2 * PPM),
    "louvre": (790.0, 830.0, 1.0 * PPM, 0.6 * PPM),
}
# The light profiled sheet the head house is clad in and the gallery's roof:
# ribs every RIB_P px across U at 64 px/m, uniform up V, so V is stretched
# (CLAD_VPM) to fit: U along a wall, V up it from the head house's floor.
CLAD = (4.0, 908.0, 448.0, 88.0)
CLAD_H = Z_HH_TOP - HH_Z0 + 0.10                 # metres V covers
CLAD_VPM = CLAD[3] / CLAD_H
# The gallery's two sides: U along the gallery in plan from inside the head
# house (GAL_BURY) at 64 px/m, V up from its floor across its 2.8 m section.
GAL_SIDE = (716.0, 912.0, (GAL_LEN + GAL_BURY) * PPM, 106.0)
GAL_VPM = GAL_SIDE[3] / GAL_H
# The gallery's closed end, at LPM: U across from its west side, V up.
GAL_END = (914.0, 560.0, GAL_W * LPM, GAL_H * LPM)
PATCH_NAMES = ("blank", "soffit", "sill", "conc", "barge", "lintel", "beam",
               "felt", "coping", "slab_under", "reveal", "hh_soffit", "gal_under",
               "strut", "clad_rev", "hoist")
PATCHES = {n: (4.0 + 20.0 * i, 1000.0, 16.0, 16.0) for i, n in enumerate(PATCH_NAMES)}

# ----------------------------------------------------------- material ids
(ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR, ID_CONC, ID_FRAME,
 ID_GLASS, ID_ROOF, ID_FLASH, ID_DOOR, ID_GUTTER, ID_HANDLE, ID_DARK,
 ID_SOFFIT, ID_SEAL, ID_STEEL, ID_COAL, ID_FLOOR, ID_SHEET, ID_FELT,
 ID_CLAD) = range(22)

# (roughness, metallic). Painted steel stays mostly dielectric; the gutter,
# downpipes, snow guard and ridge are the catalog's galvanised steel.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.82, 0.0), ID_MORTAR: (0.94, 0.0), ID_CONC: (0.90, 0.0),
    ID_FRAME: (0.44, 0.0), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_ROOF: (0.52, 0.12), ID_FLASH: (0.46, 0.25), ID_DOOR: (0.52, 0.05),
    ID_GUTTER: (0.48, 0.60), ID_HANDLE: (0.35, 0.80), ID_DARK: (0.96, 0.0),
    ID_SOFFIT: (0.74, 0.0), ID_SEAL: (0.90, 0.0), ID_STEEL: (0.62, 0.30),
    ID_COAL: (0.92, 0.0), ID_FLOOR: (0.88, 0.0), ID_SHEET: (0.58, 0.25),
    ID_FELT: (0.90, 0.0), ID_CLAD: (0.56, 0.10),
}

# ---------------------------------------------------------------- palettes
# The plant's brick trio: one coherent brick per instance, the window steel,
# the doors and the roof moving with it. Window steel is always lighter than
# the glass it holds.
def plant_brick(c, k=0.94):
    """The plant's shared red-brick tone: each sRGB channel pulled 40 % of
    the way to the triplet's Rec. 709 luma, then darkened by *k*. All five
    of the plant's pieces derive their red brick from the same originals by
    this formula, so they match side by side."""
    y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    return tuple(int((y + 0.6 * (v - y)) * k + 0.5) for v in c)


VARIANTS = {
    # from (144, 72, 52), (114, 58, 45) and (150, 145, 136); the mortar a
    # further 10 % darker than the brick's 0.94
    "red_brick": {"brick": plant_brick((144, 72, 52)), "brick2": plant_brick((114, 58, 45)),
                  "mortar": plant_brick((150, 145, 136), 0.94 * 0.90),
                  "frame": (206, 204, 196),
                  "door": (66, 82, 76), "roof": (58, 60, 62)},
    "yellow_brick": {"brick": (188, 166, 122), "brick2": (164, 142, 104),
                     "mortar": (160, 156, 148), "frame": (104, 116, 108),
                     "door": (104, 56, 44), "roof": (62, 64, 66)},
    # a dark purple-brown clinker, the same constants in all five pieces
    "brown_brick": {"brick": (80, 59, 57), "brick2": (62, 46, 45),
                    "mortar": (108, 106, 102), "frame": (186, 182, 172),
                    "door": (60, 68, 76), "roof": (52, 52, 54)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_BLANK: (52, 52, 52), ID_PLINTH: (150, 148, 142), ID_CONC: (166, 164, 156),
    ID_GLASS: glazing.BASE, ID_GUTTER: (134, 137, 137), ID_HANDLE: (150, 150, 148),
    ID_DARK: (24, 24, 24), ID_SOFFIT: (150, 150, 146), ID_SEAL: (34, 34, 34),
    ID_STEEL: (72, 72, 70), ID_COAL: (28, 28, 28), ID_FLOOR: (132, 130, 124),
    ID_SHEET: (124, 126, 126), ID_FELT: (54, 54, 56),
    ID_CLAD: (184, 186, 180),   # pale grey painted sheet: head house and gallery
}

# A stray pixel in a tiling band repeats under every surface sampling it.
BAND_IDS = {
    "BRICK": ((0, BRICK_H + PAD), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH, ID_CONC}),
    "ROOF": ((ROOF_Y0 - PAD, ROOF_Y0 + ROOF_H + PAD), {ID_ROOF, ID_GUTTER, ID_FLASH}),
    "EAVE": ((EAVE_Y0 - PAD, EAVE_Y0 + EAVE_H + PAD), {ID_FLASH, ID_GUTTER}),
}

# The candidate-glazing mask is the emission map, neutral white.
EMIT = {ID_GLASS: (255, 255, 255)}
# Linear RGB: industrial lamps, as the catalog's other works buildings.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
# Metres, relative to the face each region maps onto: only what the mesh
# does not model. Regions painted at LPM or ROOF_RPM scale relief that varies
# along their stretched axis, so the normal map's slopes stay physical.
BRICK_FACE = 0.006
BAND_H = 0.010
FRAME_H = 0.035
BAR_H = 0.022
SASH_H = 0.040
DOOR_FRAME_H = 0.030
RIB_H = 0.030
GUTTER_R = 0.070
TUBE_H = 0.045
GUARD_BRACKET_H = 0.040
BOARD_LINE_H = 0.002
GRATE_BAR_H = 0.040     # the grate's bars over the coal between them

# Occlusion in the lane: what its middle keeps of the shade and AO a surface
# in the open has. Open at both ends, so symmetric about mid-length.
SIDE_SHADE, SIDE_AO = 0.52, 0.44
CEIL_SHADE, CEIL_AO = 0.42, 0.34
FLOOR_SHADE, FLOOR_AO = 0.70, 0.55

# Coal dust: weathering.py's K field, laid by Weather.coal()
COAL_DUST = (44, 43, 42)    # sRGB: settled coal fines
FOOT_COAL = 1.30            # at the walls' foot ...
FOOT_FALL = 1.10            # ... falling by 1/e every this many metres ...
FOOT_TOP = 1.90             # ... and gone by here, under SAMPLE_LO
LANE_COAL = 0.55


def m(v):
    """Metres -> pixels at 64 px/m."""
    return v * PPM


# ================================================================== bands
def paint_plinth(c, x0, x1):
    """Cast concrete, the base every wall and column stands on."""
    y0 = BRICK_Y0
    h = m(Z_PLINTH)
    c.paint(x0, x1, y0 - PAD, y0 + h, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(x0, x1, y0 - PAD, y0 + h)
    z = (Y - y0) / PPM
    c.shade[sy, sx] *= 0.82 + 0.18 * np.clip(z / 0.20, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.20, 0, 1))
    c.mul(x0, x1, y0 + m(0.3125), y0 + m(0.3125) + 1, 0.94, ao=0.94)
    c.lift(x0, x1, y0 + m(0.3125), y0 + m(0.3125) + 1, -0.002)
    c.mul(x0, x1, y0 + h - 2, y0 + h, 0.88, ao=0.86)


def paint_band(c, x0, x1):
    """The cast concrete band: the portal lintels over the mouths and the
    ring beam round the shed at the same height, arrises catching the light,
    a drip shadow on the brick under it, formwork joints every 2 m."""
    b0, b1 = BRICK_Y0 + m(Z_BAND0), BRICK_Y0 + m(Z_BAND1)
    c.paint(x0, x1, b0, b1 + PAD, ID_CONC, 1.0, 1.0)
    c.bevel(x0, x1, b0, b1, BAND_H, 1.0, axes="y")
    sy, sx, Y, _ = c.field(x0, x1, b1, b1 + PAD)
    c.height[sy, sx] = 0.0
    c.mul(x0, x1, b0, b0 + 1, 0.86, ao=0.86)
    c.mul(x0, x1, b0 - 2, b0, 0.88, ao=0.84)
    c.mul(x0, x1, b1 - 1, b1, 0.96)
    for i in range(int(BRICK_W / 128) + 1):
        x = i * 128.0
        if x0 <= x < x1:
            c.mul(x, x + 1, b0, b1, 0.90, ao=0.90)
            c.lift(x, x + 1, b0, b1, -0.003)


def paint_brick(c):
    """Stretcher-bond facing brick, 0.25 x 0.078125 m, in two tones, mortar
    recessed and its own id; tone and bond repeat every TONE_COURSES."""
    x0, x1 = -PAD, BRICK_W + PAD
    y0 = BRICK_Y0 + m(Z_PLINTH)
    top = BRICK_Y0 + m(Z_BAND0)
    c.paint(x0, x1, y0, top, ID_BRICK, 1.0, 1.0)
    course, blen = m(COURSE), m(BRICK_L)
    sy, sx, Y, X = c.field(x0, x1, y0, top)
    r = np.floor((Y - y0) / course).astype(np.int64)
    off = (r % 2) * blen * 0.5
    b = np.floor((X - off) / blen).astype(np.int64) % 64
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
    paint_plinth(c, x0, x1)
    paint_band(c, x0, x1)


def paint_col(c):
    """The concrete frame's column strip: smooth cast concrete from the
    plinth to the band, the plinth and the band painted as on the brick so
    their lines run on across, its arrises a little raised."""
    x0, _, w, _ = COL
    a, b = x0 - PAD, x0 + w + PAD
    c.paint(a, b, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(Z_BAND0), ID_CONC, 1.0, 1.0,
            height=0.0)
    sy, sx, Y, X = c.field(a, b, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(Z_BAND0))
    z = (Y - BRICK_Y0) / PPM
    lift = np.floor(z / 1.2).astype(np.int64)
    line = ((z - lift * 1.2) * PPM) < 0.8
    tone = 1.0 + 0.04 * (atlas.hash_unit(37, lift) - 0.5)
    c.shade[sy, sx] = np.where(line, tone * 0.90, tone)
    c.ao[sy, sx] = np.where(line, 0.88, 1.0)
    d = np.minimum(X - x0, x0 + w - X)
    c.height[sy, sx] = (np.where(line, -BOARD_LINE_H, 0.0)
                        + 0.008 * np.clip(d / 1.5, 0.0, 1.0))
    paint_plinth(c, a, b)
    paint_band(c, a, b)


def paint_sheet(c, x0, x1, y0, y1, mid, seed, rib_h=RIB_H, k=1.0):
    """Profiled sheet over a rect, ribs across U every RIB_P px (as
    hiilisiilo_drive_through paints its own): a crown on short slopes, the
    pan between in the rib's lee, a darker side-lap every fourth rib."""
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


def paint_roof(c):
    """Profiled steel roof sheet, V stretched up the slope (ROOF_H rows over
    ROOF_LEN). The ribs vary in U only. The snow guard is two tubes across
    the band on brackets every metre near the eave, galvanised; the ridge cap
    over the main roof's last 0.15 m, which the lean-to's mapping stops
    short of."""
    y0, h = ROOF_Y0, ROOF_H
    paint_sheet(c, 0, ATLAS, y0 - PAD, y0 + h + PAD, ID_ROOF, seed=41)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    k = ROOF_RPM / PPM
    v = Y - y0
    shade, ao, height = c.shade[sy, sx], c.ao[sy, sx], c.height[sy, sx]
    mid = c.mid[sy, sx]
    shade = np.where(v < 1.5, shade * 0.85, shade)                     # eave drip
    g = round(SNOW_GUARD * ROOF_RPM)
    guard = np.zeros(v.shape, bool)
    for t0, t1 in ((g, g + 2.0), (g + 3.0, g + 4.5)):
        inside = (v >= t0) & (v < t1)
        tube = TUBE_H * k * np.sqrt(np.clip(
            1.0 - (2.0 * (v - t0) / (t1 - t0) - 1.0) ** 2, 0.0, 1.0))
        height = np.where(inside, tube, height)
        shade = np.where(inside, 1.0, shade)
        guard |= inside
    shade = np.where((v >= g - 3) & (v < g - 1), shade * 0.80, shade)
    ao = np.where((v >= g - 3) & (v < g + 4.5), np.minimum(ao, 0.85), ao)
    xb = X % PPM
    bracket = (xb >= 0.6) & (xb < 2.6) & (v >= g - 3) & (v < g + 4.5)
    height = np.where(bracket, GUARD_BRACKET_H * k, height)
    shade = np.where(bracket, 0.75, shade)
    guard |= bracket
    r0 = (MAIN_SLOPE - 0.15) * ROOF_RPM                              # ridge cap
    ridge = v >= r0
    height = np.where(ridge, 0.020 * k, height)
    shade = np.where(ridge, 0.97, shade)
    ao = np.where(ridge, 1.0, ao)
    shade = np.where((v >= r0 - 1.0) & (v < r0), shade * 0.80, shade)
    mid = np.where(guard, ID_GUTTER, np.where(ridge, ID_FLASH, mid))
    c.mid[sy, sx], c.shade[sy, sx], c.ao[sy, sx], c.height[sy, sx] = mid, shade, ao, height


def paint_eave(c):
    """The eave's vertical edge: a fascia of folded sheet in the roof's trim
    colour with a half-round galvanised gutter hung across its top, hangers
    every metre."""
    y0 = EAVE_Y0
    top = y0 + EAVE_H
    c.paint(0, ATLAS, y0 - PAD, top + PAD, ID_FLASH, 1.0, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 - PAD, y0 + 1, ID_FLASH, 0.86, 0.9)
    gh = float(GUTTER_PX)
    g0 = top - gh
    c.paint(0, ATLAS, g0, top + PAD, ID_GUTTER, 1.0, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_GUTTER, 0.82, 0.86)
    for k, f in enumerate((0.84, 0.90, 0.95)):
        c.mul(0, ATLAS, g0 - 1 - k, g0 - k, f, ao=0.86)
    sy, sx, _, X = c.field(0, ATLAS, g0 + 1, top)
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.84, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


# ================================================================== lane
def lane_fall(e, start=0.2, end=3.5):
    """0 at a mouth, 1 deep in the lane; *e* metres from the nearer mouth."""
    return atlas.smoothstep(start, end, e)


def paint_lane_side(c):
    """Both of the lane's side walls, U along the lane from the west mouth
    and V up from the ground, at LPM: a board-formed concrete impact wall to
    1.2 m, facing brick above, the frame's columns and the mouths' piers in
    concrete, the band at the lintels' height, and occlusion deepening toward
    mid-length and into the corners. The rows above 6.0 also serve the
    gables' inner faces over the lintels."""
    x0, y0, w, h = LANE_SIDE
    k = LPM / PPM
    a, b = x0 - PAD, x0 + w + PAD
    sy, sx, Y, X = c.field(a, b, y0 - PAD, y0 + h + PAD)
    u = (X - x0) / LPM                      # metres from the west mouth
    z = (Y - y0) / LPM
    xp = u - HX                             # plan x
    # brick everywhere first
    course, blen = COURSE * LPM, BRICK_L * LPM
    r = np.floor((Y - y0) / course).astype(np.int64)
    off = (r % 2) * blen * 0.5
    bi = np.floor((X - off) / blen).astype(np.int64) % 97
    joint = ((Y - y0 - r * course) < 0.5) | (((X - off) % blen) < 0.5)
    tone = 0.90 + 0.20 * atlas.hash_unit(bi, r % TONE_COURSES, 17)
    dark = atlas.hash_unit(bi, r % TONE_COURSES, 29) < 0.17
    mid = np.where(joint, ID_MORTAR, np.where(dark, ID_BRICK2, ID_BRICK)).astype(np.uint8)
    shade = np.where(joint, 0.94, tone)
    ao = np.where(joint, 0.85, 1.0)
    height = np.where(joint, 0.0, BRICK_FACE * k)
    # concrete: the impact wall, the columns and piers, the band
    conc = (z < 1.2) | ((z >= Z_BAND0) & (z < Z_BAND1))
    conc |= np.abs(xp) > X_IN
    for fx in FRAME_X:
        conc |= np.abs(xp - fx) < COL_W / 2.0
    lift = np.floor(z / 0.4).astype(np.int64)
    ctone = 1.0 + 0.05 * (atlas.hash_unit(53, lift, np.floor(u / 2.0).astype(np.int64)) - 0.5)
    cline = ((z - lift * 0.4) * LPM) < 0.5
    mid = np.where(conc, ID_CONC, mid)
    shade = np.where(conc, np.where(cline & (z < 1.2), ctone * 0.92, ctone), shade)
    ao = np.where(conc, 1.0, ao)
    height = np.where(conc, 0.0, height)
    # the impact wall's top chamfer and the band's arrises
    shade = np.where((z >= 1.17) & (z < 1.2), shade * 0.80, shade)
    shade = np.where((z >= Z_BAND0 - 0.04) & (z < Z_BAND0), shade * 0.82, shade)
    # occlusion
    e = np.minimum(u, 2 * HX - u)
    f = lane_fall(e)
    corner = 0.16 * np.exp(-np.clip(z, 0, None) / 0.30) + 0.18 * np.exp(
        -np.clip(ceil_z(YL0) - z, 0, None) / 0.40)
    shade = shade * (1.0 - (1.0 - SIDE_SHADE) * f) * (1.0 - corner)
    ao = ao * (1.0 - (1.0 - SIDE_AO) * f) * (1.0 - 1.4 * corner)
    c.mid[sy, sx], c.shade[sy, sx], c.ao[sy, sx], c.height[sy, sx] = mid, shade, ao, height


def paint_lane_ceil(c):
    """The lane's ceiling, both slopes alike: U along the lane from the west
    mouth, V up the slope from the side wall to the apex, at LPM. Profiled
    sheet underside on steel purlins running along the lane, the frames'
    concrete rafters over the tie beams, and occlusion falling further than
    the walls'."""
    x0, y0, w, h = LANE_CEIL
    k = LPM / PPM
    a, b = x0 - PAD, x0 + w + PAD
    sy, sx, Y, X = c.field(a, b, y0 - PAD, y0 + h + PAD)
    u = (X - x0) / LPM
    v = (Y - y0) / LPM
    xp = u - HX
    xm = np.mod(X - x0, RIB_P * k)
    rib = xm < 3.0 * k
    mid = np.full(Y.shape, ID_SHEET, np.uint8)
    shade = np.where(rib, 1.0, 0.90)
    ao = np.where(rib, 1.0, 0.88)
    height = np.where(rib, RIB_H * k, 0.0)
    for vp in (0.25, 1.15, 2.05, CEIL_LEN - 0.12):           # purlins
        on = np.abs(v - vp) < 0.08
        mid = np.where(on, ID_STEEL, mid)
        shade = np.where(on, 0.95, shade)
        height = np.where(on, 0.06 * k, height)
        lee = (v >= vp + 0.08) & (v < vp + 0.16)
        shade = np.where(lee, shade * 0.75, shade)
        ao = np.where(lee, 0.7, ao)
    for fx in FRAME_X:                                         # rafters
        on = np.abs(xp - fx) < BEAM_W / 2.0
        mid = np.where(on, ID_CONC, mid)
        shade = np.where(on, 0.92, shade)
        height = np.where(on, 0.0, height)
        side = (np.abs(xp - fx) >= BEAM_W / 2.0) & (np.abs(xp - fx) < BEAM_W / 2.0 + 0.08)
        shade = np.where(side, shade * 0.78, shade)
        ao = np.where(side, 0.7, ao)
    e = np.minimum(u, 2 * HX - u)
    f = lane_fall(e, 0.0, 3.5)
    edge = 0.16 * np.exp(-np.clip(v, 0, None) / 0.35)
    shade = shade * (1.0 - (1.0 - CEIL_SHADE) * f) * (1.0 - edge)
    ao = ao * (1.0 - (1.0 - CEIL_AO) * f) * (1.0 - 1.4 * edge)
    c.mid[sy, sx], c.shade[sy, sx], c.ao[sy, sx], c.height[sy, sx] = mid, shade, ao, height


def grate_d(u, v):
    """Metres from the grate's edge (0 inside it), for the floor region's
    (u, v): u along the lane from the west mouth, v across from YL0."""
    gx0, gx1 = GRATE_X[0] + HX, GRATE_X[1] + HX
    gy0, gy1 = GRATE_Y[0] - YL0, GRATE_Y[1] - YL0
    dx = np.clip(np.maximum(gx0 - u, u - gx1), 0, None)
    dy = np.clip(np.maximum(gy0 - v, v - gy1), 0, None)
    return np.hypot(dx, dy)


def paint_lane_floor(c):
    """The lane's floor slab, U along the lane from the west mouth and V
    across it from the front wall, at LPM: broom-finished concrete in bays
    with sawn joints, two worn wheel tracks, and at mid-length the tipping
    grate: a steel frame round bars across the traffic, coal in the pit
    under them, a cross bearer down the middle."""
    x0, y0, w, h = LANE_FLOOR
    k = LPM / PPM
    a, b = x0 - PAD, x0 + w + PAD
    sy, sx, Y, X = c.field(a, b, y0 - PAD, y0 + h + PAD)
    u = (X - x0) / LPM
    v = (Y - y0) / LPM
    bay = np.floor(u / 3.5).astype(np.int64)
    tone = 1.0 + 0.05 * (atlas.hash_unit(71, bay) - 0.5)
    mid = np.full(Y.shape, ID_FLOOR, np.uint8)
    shade = tone.astype(np.float32)
    ao = np.ones(Y.shape, np.float32)
    height = np.zeros(Y.shape, np.float32)
    joint = (np.abs(np.mod(u + 1.75, 3.5) - 1.75) < 0.6 / LPM) | (
        np.abs(v - (YC - YL0)) < 0.6 / LPM)
    shade = np.where(joint, shade * 0.80, shade)
    height = np.where(joint, -0.004 * k, height)
    ao = np.where(joint, 0.85, ao)
    # two wheel tracks, polished darker by the tyres
    vc = YC - YL0
    for t in (vc - 0.95, vc + 0.95):
        tr = np.exp(-((v - t) / 0.35) ** 2)
        shade = shade * (1.0 - 0.10 * tr)
    # the grate
    gx0, gx1 = GRATE_X[0] + HX, GRATE_X[1] + HX
    gy0, gy1 = GRATE_Y[0] - YL0, GRATE_Y[1] - YL0
    inside = (u >= gx0) & (u < gx1) & (v >= gy0) & (v < gy1)
    fr = 0.12
    frame = inside & ((u < gx0 + fr) | (u >= gx1 - fr) | (v < gy0 + fr) | (v >= gy1 - fr))
    bearer = inside & (np.abs(v - vc) < 0.06)
    bars = inside & (np.mod(u - gx0, 0.15) < 0.04)
    pit = inside & ~(frame | bearer | bars)
    steel = frame | bearer | bars
    mid = np.where(pit, ID_COAL, np.where(steel, ID_STEEL, mid))
    shade = np.where(pit, 0.85, np.where(steel, 1.0, shade))
    ao = np.where(pit, 0.45, np.where(steel, 0.95, ao))
    height = np.where(pit, -GRATE_BAR_H * k, np.where(steel, 0.0, height))
    rim = (~inside) & (grate_d(u, v) < 0.05)
    shade = np.where(rim, shade * 0.75, shade)
    # occlusion: toward mid-length and along the walls
    e = np.minimum(u, 2 * HX - u)
    f = lane_fall(e, 0.3, 4.0)
    wall = 0.20 * np.exp(-np.minimum(v, (YL1 - YL0) - v) / 0.35)
    shade = shade * (1.0 - (1.0 - FLOOR_SHADE) * f) * (1.0 - wall)
    ao = ao * (1.0 - (1.0 - FLOOR_AO) * f) * (1.0 - 1.2 * wall)
    c.mid[sy, sx], c.shade[sy, sx], c.ao[sy, sx], c.height[sy, sx] = mid, shade, ao, height


# ================================================================= regions
def _bar(c, a0, a1, b0, b1, mid=ID_FRAME, h=FRAME_H, ao=0.88, shade=1.0, axes="xy"):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, 1.0, axes=axes)


def _grid(c, x0, x1, y0, y1, cols, rows, bar=2.0):
    """Glass in cols x rows small panes on steel glazing bars *bar* px wide,
    each pane's head shaded by its bar."""
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


def paint_window(c, rect, cols, rows, hop, F=5):
    """A steel industrial window: a heavy frame round cols x rows small panes
    on slim glazing bars, and a bottom-hung hopper across row *hop*, its
    sash standing proud. glazing.rooms() paints one room per window."""
    x, y, w, h = rect
    _bar(c, x - PAD, x + w + PAD, y - PAD, y + h + PAD, h=FRAME_H)
    gx0, gx1, gy0, gy1 = x + F, x + w - F, y + F + 1, y + h - F
    _grid(c, gx0, gx1, gy0, gy1, cols, rows)
    ph = (gy1 - gy0) / float(rows)
    s0, s1 = gy0 + hop * ph - 1.5, gy0 + (hop + 1) * ph + 1.5
    for a0, a1, b0, b1, axes in ((gx0, gx1, s0, s0 + 3, "y"), (gx0, gx1, s1 - 3, s1, "y"),
                                 (gx0, gx0 + 3, s0, s1, "x"), (gx1 - 3, gx1, s0, s1, "x")):
        _bar(c, a0, a1, b0, b1, h=SASH_H, axes=axes)
    c.mul(gx0, gx1, s0 - 2, s0, 0.88, ao=0.84)
    c.mul(x, x + w, y, y + F + 1, 0.92, ao=0.86)
    c.mul(gx0, gx1, gy1 - 3, gy1, 0.90, ao=0.84)


def paint_door(c):
    """A steel door: the leaf in a steel frame, two pressed panels, a kick
    plate along its foot, a lever handle on the right (hinges left)."""
    x0, y0, w, h = REGION["door"]
    f = m(DOOR_FRAME)
    ox0, ox1, oy1 = x0 + f, x0 + w - f, y0 + m(LEAF_H)
    c.paint(x0 - PAD, x0 + w + PAD, y0 - PAD, y0 + h + PAD, ID_DOOR, 0.82, 0.9, height=0.0)
    c.bevel(x0, x0 + w, y0 - 3, y0 + h, DOOR_FRAME_H, 1.0)
    c.paint(ox0, ox1, y0, oy1, ID_DOOR, 1.0, 1.0, height=0.0)
    c.mul(ox0, ox1, oy1 - 1.5, oy1, 0.80, ao=0.8)
    for p0, p1 in ((0.30, 0.95), (1.15, 1.95)):
        a, b = y0 + m(p0), y0 + m(p1)
        px0, px1 = ox0 + m(0.12), ox1 - m(0.12)
        c.bevel(px0, px1, a, b, -0.006, 1.2, base=0.0)
        c.mul(px0, px1, b - 1.0, b, 0.84, ao=0.85)
        c.mul(px0, px0 + 1.0, a, b, 0.90)
    c.paint(ox0, ox1, y0, y0 + m(0.22), ID_STEEL, 1.0, 0.9, height=0.003)
    hx, hy = ox1 - m(0.09), y0 + m(1.02)
    c.paint(hx - m(0.13), hx + 1.0, hy - 1.0, hy + 1.0, ID_HANDLE, 1.0, 0.9, height=0.030)
    c.paint(hx - 1.5, hx + 1.5, hy - 5.0, hy + 3.0, ID_HANDLE, 0.9, 0.9, height=0.012)
    c.mul(ox0, ox0 + 1.0, y0, oy1, 0.80, ao=0.8)
    c.mul(ox1 - 1.0, ox1, y0, oy1, 0.80, ao=0.8)
    c.paint(ox0, ox1, y0, y0 + 1.5, ID_SEAL, 1.0, 0.8)


def paint_hatch(c):
    """The head house's loading hatch under the hoist beam: a top-hung
    steel plate in an angle frame, stiffened by a cross of flats, two strap
    hinges along its head and a lock bar at its foot. Closed and opaque."""
    x, y, w, h = REGION["hatch"]
    F = 5
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_STEEL, 0.9, 0.9, height=0.0)
    c.bevel(x - PAD, x + w + PAD, y - PAD, y + h + PAD, 0.02, 1.5)
    px0, px1, py0, py1 = x + F, x + w - F, y + F, y + h - F
    c.paint(px0, px1, py0, py1, ID_DOOR, 1.0, 1.0, height=0.0)
    c.paint(px0 - 1, px1 + 1, py0 - 1, py0, ID_SEAL, 1.0, 0.7)
    c.paint(px0 - 1, px1 + 1, py1, py1 + 1, ID_SEAL, 1.0, 0.7)
    cx, cy = (px0 + px1) / 2.0, (py0 + py1) / 2.0
    for a0, a1, b0, b1, axes in ((cx - 1.5, cx + 1.5, py0, py1, "x"),
                                 (px0, px1, cy - 1.5, cy + 1.5, "y")):
        c.paint(a0, a1, b0, b1, ID_DOOR, 1.03, 1.0)
        c.bevel(a0, a1, b0, b1, 0.012, 0.8, axes=axes)
    for hx in (px0 + m(0.18), px1 - m(0.18)):
        c.paint(hx - 2, hx + 2, py1 - m(0.35), py1 + 2, ID_STEEL, 0.85, 0.85, height=0.02)
    c.paint(cx - m(0.25), cx + m(0.25), py0 + 3, py0 + 6, ID_HANDLE, 0.9, 0.85, height=0.03)
    c.mul(px0, px1, py1 - 2, py1, 0.85, ao=0.82)


def paint_louvre(c):
    """A ventilation louvre: steel blades sloping out and down in a cast
    concrete surround, dark between."""
    x, y, w, h = REGION["louvre"]
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


def paint_clad(c):
    """The head house's cladding: pale painted profiled sheet, ribs upright
    across U, a horizontal end lap 2.0 m up, a drip flashing along the foot
    and the shadow line under the roof slab's edge along the top."""
    x0, y0, w, h = CLAD
    paint_sheet(c, x0 - PAD, x0 + w + PAD, y0 - PAD, y0 + h + PAD, ID_CLAD, seed=61)
    lap = y0 + 2.0 * CLAD_VPM
    c.mul(x0 - PAD, x0 + w + PAD, lap, lap + 1, 0.86, ao=0.86)
    c.paint(x0 - PAD, x0 + w + PAD, y0 - PAD, y0 + 2, ID_FLASH, 0.92, 0.9, height=0.012)
    top = y0 + (Z_TSLAB - HH_Z0) * CLAD_VPM
    c.mul(x0 - PAD, x0 + w + PAD, top - 2, y0 + h + PAD, 0.84, ao=0.80)


def paint_gal_side(c):
    """A side of the conveyor gallery, U along it in plan, V up from its
    floor (GAL_VPM): pale profiled sheet with upright ribs between a steel
    bottom chord and a flashing along the top, and a row of small steel
    windows lighting the belt walkway, one every metre."""
    x0, y0, w, h = GAL_SIDE
    paint_sheet(c, x0 - PAD, x0 + w + PAD, y0 - PAD, y0 + h + PAD, ID_CLAD, seed=67)
    v = GAL_VPM
    c.paint(x0 - PAD, x0 + w + PAD, y0 - PAD, y0 + 0.18 * v, ID_STEEL, 1.0, 0.9, height=0.02)
    c.mul(x0 - PAD, x0 + w + PAD, y0 + 0.18 * v, y0 + 0.18 * v + 1.5, 0.82, ao=0.84)
    c.paint(x0 - PAD, x0 + w + PAD, y0 + h - 0.14 * v, y0 + h + PAD, ID_FLASH, 0.95, 0.95,
            height=0.015)
    c.mul(x0 - PAD, x0 + w + PAD, y0 + h - 0.14 * v - 1.5, y0 + h - 0.14 * v, 0.85, ao=0.86)
    for d in (0.55, 1.55, 2.55, 3.55):
        a = x0 + (GAL_BURY + d - 0.30) * PPM
        b = a + 0.60 * PPM
        s0, s1 = y0 + 1.30 * v, y0 + 1.85 * v
        _bar(c, a, b, s0, s1, h=FRAME_H)
        _grid(c, a + 3, b - 3, s0 + 3, s1 - 3, 2, 1)
        c.mul(a, b, s0 - 2, s0, 0.85, ao=0.84)


def paint_gal_end(c):
    """The gallery's closed end: a rim of the side sheet round a dark steel
    blanking plate, the plate set back at the close tiers."""
    x0, y0, w, h = GAL_END
    r = GAL_END_RIM * LPM
    c.paint(x0 - PAD, x0 + w + PAD, y0 - PAD, y0 + h + PAD, ID_CLAD, 0.95, 1.0, height=0.0)
    c.paint(x0 + r, x0 + w - r, y0 + r, y0 + h - r, ID_STEEL, 0.62, 0.70, height=0.0)
    c.mul(x0 + r, x0 + w - r, y0 + h - r - 2, y0 + h - r, 0.80, ao=0.75)
    for k in range(1, 4):
        yy = y0 + r + k * (h - 2 * r) / 4.0
        c.paint(x0 + r, x0 + w - r, yy, yy + 1, ID_STEEL, 0.70, 0.8, height=0.006)


def paint_patches(c):
    """Flat cells for surfaces a whole face takes one colour from."""
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0), "soffit": (ID_SOFFIT, 0.92, 0.80),
        "sill": (ID_CONC, 0.94, 0.90), "conc": (ID_CONC, 0.84, 0.80),
        "barge": (ID_FLASH, 0.94, 0.94), "lintel": (ID_CONC, 0.62, 0.60),
        "beam": (ID_CONC, 0.60, 0.55), "felt": (ID_FELT, 1.0, 1.0),
        "coping": (ID_CONC, 1.0, 1.0), "slab_under": (ID_CONC, 0.78, 0.75),
        "reveal": (ID_CONC, 0.72, 0.70), "hh_soffit": (ID_CLAD, 0.78, 0.72),
        "gal_under": (ID_STEEL, 0.85, 0.75), "strut": (ID_STEEL, 0.95, 0.90),
        "clad_rev": (ID_CLAD, 0.84, 0.80), "hoist": (ID_STEEL, 1.0, 0.95),
    }
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x - 2, x + w + 2, y - 2, y + h + 2, mid, sh, ao, height=0.0)


# ------------------------------------------------------------------ checks
def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands or
    run off the sheet, or the layout's numbers disagree."""
    rects = dict(REGION)
    rects.update(PATCHES)
    rects.update({"lane_side": LANE_SIDE, "lane_ceil": LANE_CEIL,
                  "lane_floor": LANE_FLOOR, "clad": CLAD, "gal_side": GAL_SIDE,
                  "gal_end": GAL_END})
    bands_top = EAVE_Y0 + EAVE_H + PAD
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
        _, _, rw, rh = REGION[kind]
        if abs(rw / PPM - w) > 1e-6 or abs(rh / PPM - h) > 1e-6:
            problems.append("%s region is not its opening's size" % kind)
    if abs(m(Z_BAND1) - BRICK_H) > 1e-6:
        problems.append("the brick band does not end at the band's top")
    for s in SHIFTS:
        if abs((m(s) / m(COURSE)) % TONE_COURSES) > 1e-6:
            problems.append("shift %.3f is not a whole tone period" % s)
    if COL[0] < BRICK_W + 8 or COL[0] + COL[2] + 4 > ATLAS:
        problems.append("the column strip crowds the brick band")
    if ANNEX_SLOPE * ANNEX_V_K > MAIN_SLOPE - 0.15 - 0.05:
        problems.append("the lean-to reaches the ridge cap's rows")
    if ROOF_Y0 - PAD < BRICK_H + PAD + 2 or EAVE_Y0 - PAD < ROOF_Y0 + ROOF_H + PAD + 2:
        problems.append("the bands overlap")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    The brick band's V is height from the ground, so splash-back, the
    plinth's soil and the coal the trucks throw up land the same on every
    wall; all of it is gone by FOOT_TOP, under the rows the walls above the
    band sample again (SAMPLE_LO), so no shift shows a seam. Coal dust is
    weathering's K field (w.coal()): heavy in the lane, on its floor round
    the grate and at the mouths' jambs, at the walls' feet; light and patchy
    everywhere above, a working plant's dust, not neglect."""
    brick = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    steel = (ID_ROOF, ID_FLASH, ID_GUTTER, ID_DOOR, ID_HANDLE, ID_STEEL, ID_SHEET)
    w = weathering.Weather(c, clean=(ID_GLASS,), steel=steel, coal_dust=COAL_DUST)
    w.grime()
    w.fade((ID_FRAME, ID_DOOR, ID_FLASH))
    w.wash(brick)
    xb1 = ATLAS
    band_top = BRICK_Y0 + BRICK_H + PAD
    w.plinth(0, xb1, BRICK_Y0, BRICK_Y0 + m(Z_PLINTH), (ID_PLINTH,))
    w.splash(0, xb1, BRICK_Y0 + m(Z_PLINTH), band_top, brick + (ID_CONC,))
    w.bloom(0, xb1, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(1.4), brick,
            amount=0.10, fade=m(0.7))
    # the band: dust on its top, short runs on the brick just under it
    b0, b1 = BRICK_Y0 + m(Z_BAND0), BRICK_Y0 + m(Z_BAND1)
    w.add("D", 0, xb1, b1 - 4, b1, lambda Y, X, nz: 0.10 + 0.10 * nz("blotch"), (ID_CONC,))
    w.runs(0, xb1, BRICK_Y0 + m(SAMPLE_HI + 0.02), b0, brick, 0.10, fall=3.0)
    w.add("D", 0, xb1, b0, b1, lambda Y, X, nz: 0.05 * nz("big"), (ID_CONC,))
    # coal the trucks throw up, at every wall's foot; gone by FOOT_TOP
    def foot(Y, X, nz):
        z = np.clip((Y - BRICK_Y0) / PPM, 0.0, None)
        return (FOOT_COAL * np.exp(-z / FOOT_FALL) * (0.7 + 0.3 * nz("blotch"))
                * atlas.smoothstep(FOOT_TOP, FOOT_TOP - 0.7, z)
                + 0.10 + 0.06 * nz("big")
                + 0.10 * atlas.smoothstep(0.4, 1.8, nz("runs")))
    w.coal(0, xb1, BRICK_Y0, band_top, foot, (ID_PLINTH, ID_CONC) + brick)
    # the plinth: a dull grey-black film all along, the dust it catches
    w.coal(0, xb1, BRICK_Y0 - PAD, BRICK_Y0 + m(Z_PLINTH), lambda Y, X, nz: 0.45
           + 0.15 * nz("blotch"), (ID_PLINTH,))
    # the concrete frame, band and lintels: cast concrete takes the dust
    # harder than the fired brick face, patchy, nothing that follows height
    w.coal(0, xb1, BRICK_Y0, band_top, lambda Y, X, nz: 0.30 + 0.12 * nz("blotch"),
           (ID_CONC,))
    # the roof, its ridge, snow guard, fascia and gutter
    roof = (ID_ROOF,)
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, ROOF_LEN, roof)
    w.coal(0, ATLAS, ROOF_Y0 - PAD, ROOF_Y0 + ROOF_H + PAD, lambda Y, X, nz: 0.05
           + 0.08 * nz("blotch"), roof + (ID_FLASH,))
    g = ROOF_Y0 + round(SNOW_GUARD * ROOF_RPM)
    w.add("D", 0, ATLAS, g + 4.5, g + 12.0, lambda Y, X, nz: 0.20 * nz("blotch")
          * (1.0 - (Y - g - 4.5) / 7.5), roof)
    w.add("D", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.06 + 0.045 * nz("blotch"),
          (ID_GUTTER,))
    top = EAVE_Y0 + EAVE_H
    w.add("D", 0, ATLAS, top - GUTTER_PX, top - GUTTER_PX + 4,
          lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"), (ID_GUTTER,))
    w.runs(0, ATLAS, top - GUTTER_PX, top, (ID_GUTTER,), 0.08, fall=4.0, lo=0.4, hi=1.6)
    w.runs(0, ATLAS, EAVE_Y0 - PAD, top - GUTTER_PX, (ID_FLASH,), 0.12, fall=6.0,
           noise="short")
    # the lane's side walls: dusted all over, heavy at the foot and at the
    # mouths' jambs, where every truck's spray and draught passes
    x0, y0, lw, lh = LANE_SIDE
    w.add("D", x0 - PAD, x0 + lw + PAD, y0 - PAD, y0 + lh + PAD,
          lambda Y, X, nz: 0.08 + 0.08 * nz("blotch"))

    def side(Y, X, nz):
        z = np.clip((Y - y0) / LPM, 0, None)
        u = (X - x0) / LPM
        jamb = np.clip(1.0 - (np.minimum(u, 2 * HX - u) - WALL_T) / 0.8, 0, 1)
        return (LANE_COAL + 0.10 * nz("blotch")
                + 0.45 * np.exp(-z / 1.2) + 0.40 * jamb * np.exp(-z / 4.0))
    w.coal(x0 - PAD, x0 + lw + PAD, y0 - PAD, y0 + lh + PAD, side)
    # the ceiling: dust thickest over the grate, where it rises when a load
    # is tipped
    x0, y0, cw, ch = LANE_CEIL
    w.add("D", x0 - PAD, x0 + cw + PAD, y0 - PAD, y0 + ch + PAD,
          lambda Y, X, nz: 0.10 + 0.10 * nz("blotch"))
    w.coal(x0 - PAD, x0 + cw + PAD, y0 - PAD, y0 + ch + PAD, lambda Y, X, nz: LANE_COAL
           + 0.08 * nz("blotch")
           + 0.35 * np.exp(-np.abs((X - x0) / LPM - (HX + GRATE_C)) / 3.0))
    # the floor: spill round the grate, along the tracks and the walls;
    # rain keeps the mouths cleaner
    x0, y0, fw, fh = LANE_FLOOR
    def floor(Y, X, nz):
        u = (X - x0) / LPM
        v = (Y - y0) / LPM
        e = np.minimum(u, 2 * HX - u)
        d = grate_d(u, v)
        dw = np.minimum(v, (YL1 - YL0) - v)
        vc = YC - YL0
        tracks = sum(np.exp(-((v - t) / 0.40) ** 2) for t in (vc - 0.95, vc + 0.95))
        return ((0.38 + 0.12 * tracks + 0.65 * np.exp(-d / 1.1)
                 + 0.30 * np.exp(-dw / 0.5)) * (0.75 + 0.25 * lane_fall(e, 0.0, 3.0))
                + 0.10 * nz("blotch"))
    w.add("D", x0 - PAD, x0 + fw + PAD, y0 - PAD, y0 + fh + PAD,
          lambda Y, X, nz: 0.10 + 0.10 * nz("blotch"), (ID_FLOOR, ID_STEEL))
    w.coal(x0 - PAD, x0 + fw + PAD, y0 - PAD, y0 + fh + PAD, floor,
           (ID_FLOOR, ID_STEEL))
    # the windows: dirt standing on the bottom rail
    for kind in ("win", "win_b", "win_s", "win_s_b"):
        x, y, rw, rh = REGION[kind]
        w.add("D", x, x + rw, y - PAD, y + 7, lambda Y, X, nz: 0.12
              + 0.12 * atlas.smoothstep(0.2, 1.4, nz("short")), (ID_FRAME,))
        w.coal(x, x + rw, y - PAD, y + rh + PAD, 0.10, (ID_FRAME,))
    # the door: kicked-up dirt and coal at the foot, grime round the handle
    x, y, rw, rh = REGION["door"]
    f = m(DOOR_FRAME)
    w.door(x + f, x + rw - f, y, y + m(LEAF_H), (ID_DOOR,),
           handle=(x + rw - f - m(0.09), y + m(1.02)))
    w.coal(x - PAD, x + rw + PAD, y - PAD, y + m(0.8),
           lambda Y, X, nz: 0.40 * np.exp(-np.clip(Y - y, 0, None) / m(0.35)))
    # the loading hatch: dust settled on its foot, rust at the hinges; the
    # louvre: runs down its blades
    x, y, rw, rh = REGION["hatch"]
    w.coal(x - PAD, x + rw + PAD, y - PAD, y + rh + PAD, lambda Y, X, nz: 0.12
           + 0.20 * np.exp(-np.clip(Y - y, 0, None) / m(0.3)))
    w.add("R", x, x + rw, y + rh - m(0.4), y + rh, lambda Y, X, nz: 0.12 * nz("blotch"),
          (ID_STEEL, ID_DOOR))
    x, y, rw, rh = REGION["louvre"]
    w.runs(x, x + rw, y, y + rh, (ID_FRAME, ID_CONC), 0.16, fall=rh / 2.0)
    w.coal(x, x + rw, y, y + rh, 0.20, (ID_FRAME,))
    # the head house's cladding: the plant's film, heavier toward its foot
    # (V is height up its walls), runs from under the slab's edge
    x0, y0, cw, ch = CLAD
    w.add("D", x0 - PAD, x0 + cw + PAD, y0 - PAD, y0 + ch + PAD,
          lambda Y, X, nz: 0.06 + 0.06 * nz("blotch"), (ID_CLAD,))
    w.runs(x0 - PAD, x0 + cw + PAD, y0, y0 + (Z_TSLAB - HH_Z0) * CLAD_VPM, (ID_CLAD,),
           0.16, fall=0.9 * CLAD_VPM)
    w.coal(x0 - PAD, x0 + cw + PAD, y0 - PAD, y0 + ch + PAD, lambda Y, X, nz: 0.12
           + 0.06 * nz("blotch") + 0.25 * np.exp(-np.clip(Y - y0, 0, None)
                                                 / (0.6 * CLAD_VPM)))
    # the gallery's sides: the dust the belt throws out of its joints, thick
    # along the bottom chord and running down from the top flashing and
    # from every window's sill in dark streaks
    x0, y0, gw, gh = GAL_SIDE
    v = GAL_VPM
    w.add("D", x0 - PAD, x0 + gw + PAD, y0 - PAD, y0 + gh + PAD,
          lambda Y, X, nz: 0.08 + 0.06 * nz("blotch"), (ID_CLAD, ID_STEEL, ID_FLASH))

    def gal(Y, X, nz):
        z = np.clip((Y - y0) / v, 0.0, None)
        streak = atlas.smoothstep(0.3, 1.4, nz("runs"))
        return (0.20 + 0.06 * nz("blotch") + 0.60 * np.exp(-z / 0.45)
                + 0.55 * streak * np.exp(-(GAL_H - z) / 1.6))
    w.coal(x0 - PAD, x0 + gw + PAD, y0 - PAD, y0 + gh + PAD, gal,
           (ID_CLAD, ID_STEEL, ID_FLASH))
    for d in (0.55, 1.55, 2.55, 3.55):
        a = x0 + (GAL_BURY + d - 0.30) * PPM
        w.add("D", a, a + 0.60 * PPM, y0 + 0.25 * v, y0 + 1.30 * v,
              lambda Y, X, nz: 0.45 * atlas.smoothstep(0.2, 1.2, nz("runs"))
              * np.exp(-(y0 + 1.30 * v - Y) / (0.5 * v)), (ID_CLAD,))
    w.coal(GAL_END[0] - PAD, GAL_END[0] + GAL_END[2] + PAD, GAL_END[1] - PAD,
           GAL_END[1] + GAL_END[3] + PAD, lambda Y, X, nz: 0.20 + 0.10 * nz("blotch"))
    # patches: the lintels' soffits and the beams deep in dust, the gallery's
    # underside and its struts under the belt's spill
    for name, k in (("lintel", 0.75), ("beam", 0.70), ("felt", 0.15),
                    ("sill", 0.15), ("reveal", 0.35), ("soffit", 0.15),
                    ("gal_under", 0.75), ("strut", 0.45), ("hoist", 0.25),
                    ("hh_soffit", 0.30), ("clad_rev", 0.25)):
        px, py, pw, ph = PATCHES[name]
        w.coal(px - 2, px + pw + 2, py - 2, py + ph + 2, k)
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_brick(c)
    paint_col(c)
    paint_roof(c)
    paint_eave(c)
    c.check_bands(BAND_IDS)
    paint_lane_side(c)
    paint_lane_ceil(c)
    paint_lane_floor(c)
    paint_window(c, REGION["win"], 7, 4, 2)
    paint_window(c, REGION["win_b"], 7, 4, 2)
    paint_window(c, REGION["win_s"], 3, 4, 2, F=4)
    paint_window(c, REGION["win_s_b"], 3, 4, 2, F=4)
    paint_door(c)
    paint_hatch(c)
    paint_louvre(c)
    paint_clad(c)
    paint_gal_side(c)
    paint_gal_end(c)
    paint_patches(c)

    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH))
    streak = atlas.noise(c, 7, 0.8, 40.0)
    c.shade[walls] *= 1.0 + 0.03 * streak[walls]
    sheet = np.isin(c.mid, (ID_FLASH, ID_DOOR, ID_FRAME, ID_ROOF, ID_SHEET, ID_CLAD))
    grain = atlas.noise(c, 5, 0.8, 40.0)
    c.shade[sheet] *= 1.0 + 0.025 * grain[sheet]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_CONC, ID_MORTAR, ID_FLOOR))
    pores = atlas.noise(c, 9, 0.8)
    c.shade[mineral] *= 1.0 + 0.03 * pores[mineral]
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
    t[ID_FLASH] = np.minimum(np.array(pal["roof"], np.float32) * 1.15 + 6, 255)
    t[ID_DOOR] = pal["door"]
    return t


def export(out_dir, ss=atlas.SS):
    """Candidate glazing in the emission map is neutral grey, each window the
    lit room behind it; nothing else glows, and no occupancy is baked in."""
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
