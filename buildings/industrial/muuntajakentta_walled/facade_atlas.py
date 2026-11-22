# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM and normal atlas, and shared layout, for muuntajakentta_walled.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
plan, heights, opening sizes, band rows, region rectangles -- so a change here
cannot leave the UVs pointing at the wrong artwork. Importing it only defines
those constants; painting runs when paint() is called.

The yard has no glazing: the switchgear house is ventilated by steel louvres,
so there is no emission map (notes.md, Night lighting).

The atlas is a trim sheet. Two bands run the full width and tile in U:

    y    0 ..  248   HOUSE   z 0 .. 3.80 m: concrete plinth, then facing
                             brick; the switchgear house's walls and the
                             fire wall between the transformers
    y  252 ..  384   FENCE   z 0 .. 1.5625 m: concrete footing, the yard wall's
                             brick, its thin concrete coping; the piers too
    y  390 .. 1024   unique  tank, radiator, conservator, bushing and
                             insulator regions, the switchgear's breaker
                             poles, disconnector posts and current
                             transformers, the gate, the door, the louvre,
                             the gravel bed on the plinths, the roof, the
                             slab edge, LOD3's painted gantry lattice, the
                             disconnector legs' painted lattice and flat
                             patches

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
import weathering  # noqa: E402

ASSET = "muuntajakentta_walled"
ATLAS = 1024
PPM = 64.0
PAD = 2                 # rows each band paints beyond its own edge

# ------------------------------------------------------------------ plan
# Metres, Blender frame, front toward -Y. The origin is the first build's
# compound centre, kept when the compound grew 4 m west for the switchgear,
# so the house and the transformers keep their numbers; the pivot is the
# plan's centre (asset_build), x -2.0 in this frame. The yard wall's plain
# brick piers stand on the compound's outline; their outer faces are the
# asset's plan bounds, 20.0 x 12.0 m.
FX0, FX1, FY = -12.0, 8.0, 6.0  # the piers' outer faces: west, east, +-Y
PIER_W = 0.36                   # a brick pier, square (one and a half bricks)
WALL_T = 0.24                   # the wall between them (one brick)
WCX0, WCX1 = FX0 + PIER_W / 2.0, FX1 - PIER_W / 2.0   # wall centre lines
WCY = FY - PIER_W / 2.0
# The brick is the catalog module (scripts/brickwork.py): every height the
# brick meets something at is a whole number of COURSE from the ground, and
# every opening side a whole or half stretcher (HALF) in the U its wall
# samples (build.py's brick_problems()).
COURSE = brickwork.COURSE       # 0.078125 m, 5 px
BRICK_L = brickwork.BRICK_L     # 0.25 m, 16 px; 64 bricks per atlas width
HALF = BRICK_L / 2.0
Z_FENCE = 1.5625                # wall top, coping included, 20 courses (the piers PIER_PROUD over it)
Z_FOOT_F = 0.3125               # the wall's concrete footing (20 px, 4 courses)
Z_COPING = Z_FENCE - COURSE     # the thin coping's foot, 1.484375 m (19 courses)
PIER_PROUD = 0.02               # the piers stand this much over the coping
WALL_COAL = 0.55                # coal fines at the yard wall's foot (weather()) ...
WALL_COAL_FALL = 0.45           # ... falling by 1/e every this many metres up

# The gate: an opening in the front wall between two piers, closed by a
# sheet-steel double gate set back in the wall's thickness.
GATE_OPEN = (-0.75, 2.625)      # x of the two piers' inner faces (U = x + 8 m: half stretchers)
GATE_Y = (-WCY - 0.04, -WCY + 0.02)   # the leaves' 0.06 m thickness
GATE_Z = (0.04, Z_FENCE - 0.04)
GATE_INTO = 0.05                # the leaves' box runs this far into the piers

# The switchgear house: in the compound's front-east corner, its front and
# east walls in the yard wall's outer planes, so the wall stops on it.
HX1 = WCX1 + WALL_T / 2.0       # 7.94, the east wall line
HX0 = HX1 - 5.0
HY0 = -(WCY + WALL_T / 2.0)     # -5.94, the front wall line
HY1 = HY0 + 4.0
H_WALL_T = 0.24                 # the house's own walls (for the floor area)
Z_WALL = 3.203125               # brick to the roof slab, 41 courses
Z_TOP = Z_WALL + 0.25           # the flat slab's top, flush with the walls
Z_PLINTH = 0.390625             # 25 px, 5 courses; the house's concrete plinth

# The transformers: two, north and south of a brick fire wall, on concrete
# plinths, their high-voltage bushings at the west end of the cover,
# toward the gantry.
T_X = -2.0
T_Y = (-2.7, 2.7)
PLINTH = (4.4, 3.4, 0.30)       # x, y, height
TANK = (2.6, 1.6)               # x, y
TANK_Z = (0.25, 2.90)           # from inside the plinth to the cover
RAD_X, RAD_D = 2.0, 0.55        # radiator bank's length and depth
RAD_Z = (0.70, 2.55)
CONS_R, CONS_X, CONS_Z = 0.28, 0.85, 3.40     # conservator radius, x offset, axis
BUSH_X = -0.75                  # the bushings' x offset from the tank centre
PHASE = 0.60                    # phase spacing
BUSH_H = 1.10                   # from 0.05 inside the cover to the terminal
CABLE_X = (1.25, 1.62)          # the cable box on the east end
CABLE_Y = 0.45
CABLE_TOP = 2.45
FIRE = (-3.8, -0.2, 0.15, 3.80)  # fire wall x0, x1, half thickness, height
# Cable trenches: precast covers 0.08 m proud, from each plinth's east edge
# (under the cable box) to the switchgear house. The north one turns south
# at TRENCH_TURN_X.
TRENCH_W, TRENCH_H = 0.60, 0.08
TRENCH_X0 = 0.10                # inside the plinths' east edge (0.20)
TRENCH_TURN_X = 4.70            # the north trench's leg toward the house

# The gantry: a galvanised lattice portal on the west side. Two square
# columns of four corner angles, braced on every face, taper from their pads
# to G_TOP; above it each rises as a lattice peak to a capped finial for the
# shield wire. A box truss of four chord angles spans between them, braced
# on its sides, top and bottom; a suspension string hangs from it over each
# switchgear phase. Every bar is its own closed solid, stopping G_GAP short
# of the bars it meets (build.py, lattice()).
G_X = -10.6
G_COL_Y = 4.6
G_W = (0.64, 0.40)              # a column's outer width at the pad's top and at G_TOP
G_TOP = 9.70                    # where the column's legs turn into the peak
G_PEAK_W = 0.22                 # the peak's outer width at its top, G_PEAK_Z
G_PEAK_Z = 10.50                # the legs' tops; the finial's cap over them
G_TIP = 10.90                   # the finial's point, the asset's highest
G_BEAM_Z = (9.00, 9.60)         # the box truss: 0.60 m deep, as wide as the
                                # columns at its mid-height
G_PAD = (0.80, 0.30)            # concrete foundation pad: side, height
G_LEG = 0.08                    # a corner angle's leg (columns), its hull a
G_CHORD = 0.07                  # right triangle; a chord angle's (truss)
G_BRACE = (0.05, 0.035)         # a bracing angle: flange width, toe depth
G_GAP = 0.004                   # between bars that meet
# LOD3: the columns and the truss as slim solids with the lattice
# painted on, this fraction of the lattice's outer width (columns, the
# truss's width) and depth (the truss)
G_SOLID = (0.42, 0.45, 0.35)
STRING_LEN = 0.85               # top hardware to the bottom clamp


def g_half(z):
    """A lattice column's outer half-width at height z: tapering from the
    pad's top to G_TOP, then converging up the peak to G_PEAK_Z."""
    z0 = G_PAD[1]
    if z <= G_TOP:
        return 0.5 * (G_W[0] + (G_W[1] - G_W[0]) * (z - z0) / (G_TOP - z0))
    return 0.5 * (G_W[1] + (G_PEAK_W - G_W[1]) * (z - G_TOP) / (G_PEAK_Z - G_TOP))


# Panel points, metres. A column's shaft: a rail at each point and one
# diagonal per panel on every face (LOD0), the top point level with the
# truss's top chord; the peak: one diagonal up to a rail at G_PEAK_RAIL.
# LOD1 keeps the legs and a zigzag of diagonals between G_SHAFT_PTS1.
G_SHAFT_PTS = tuple(round(0.45 + (9.03 - 0.45) * k / 10, 4) for k in range(11)) + (9.66,)
G_SHAFT_PTS1 = tuple(round(0.45 + (9.66 - 0.45) * k / 6, 4) for k in range(7))
G_PEAK_RAIL = 10.10
BEAM_ZC = 0.5 * (G_BEAM_Z[0] + G_BEAM_Z[1])
BEAM_HW = g_half(BEAM_ZC)                   # the truss's half-width (x)
BEAM_HD = 0.5 * (G_BEAM_Z[1] - G_BEAM_Z[0])  # and half-depth (z)
# the truss's bracing stops this far from its axis' middle, clear of the
# columns' inner faces at its bottom chord
BEAM_YP = G_COL_Y - g_half(G_BEAM_Z[0]) - G_GAP - G_BRACE[0] / 2 - 0.01
# its top and bottom: a rail under each string (y = T_Y +- SW_PHASE * k,
# set below with the switchgear) and at mid-span, a diagonal per panel

# The switchgear: one bay per transformer between the gantry and its plinth,
# phases SW_PHASE apart across Y about the transformer's centre line. From
# west to east: the disconnector, its six posts on a tall steel table; the
# three minimum-oil breaker poles on a steel stand; the three current
# transformers on a concrete table. Each frame runs SW_HALF either side of
# the bay's centre line.
SW_PHASE = 1.0
SW_HALF = 1.35
DIS_X = (-9.3, -8.7)            # the disconnector's two rows of posts
DIS_DECK = (-9.45, -8.55, 4.05, 4.20)   # deck x0, x1, z0, z1
DIS_LEG = (0.24, 0.24, 1.10)    # leg x, y, centre's y offset from the bay's
BRK_X = -7.0                    # breaker poles' axis
BRK_DECK = (0.30, 1.85, 2.00)   # stand deck: x width, z0, z1
BRK_LEG = (0.14, 1.25)          # stand legs: side, y offset
BRK_Z0 = 1.97                   # a pole's foot, inside the deck
CT_X = -5.3
CT_TABLE = (0.50, 1.85, 2.20)   # concrete table: beam x width, z0, z1
CT_LEG = (0.35, 1.05)           # its legs: side, y offset
CT_Z0 = 2.17                    # a current transformer's foot
POST_Z0 = DIS_DECK[3] - 0.03    # a disconnector post's foot
COND_R = 0.025                  # the flexible conductors' radius
STRING_YS = tuple(sorted(ty + k * SW_PHASE for ty in T_Y for k in (-1, 0, 1)))
BEAM_PTS = (-BEAM_YP,) + STRING_YS[:3] + (0.0,) + STRING_YS[3:] + (BEAM_YP,)
BEAM_SIDE_N = 18                # the truss's sides: a Warren zigzag of this many panels

# ------------------------------------------------------------------ openings
# kind -> (width, height, casing side, casing bottom, casing top), metres.
# The casings' outer edges are the brick's: the door's 1.125 x 2.1875 m (9
# half stretchers, 28 courses), a louvre's 1.0 x 0.625 m (8 x 8).
OPENINGS = {
    "door": (1.00, 2.125, 0.0625, 0.0, 0.0625),
    "louvre": (0.875, 0.50, 0.0625, 0.0625, 0.0625),
}
REVEAL_DEPTH = {"door": 0.12, "louvre": 0.10}
Z_LOUVRE_HI = 2.328125          # high louvres' sill: casing 2.265625 .. 2.890625 (29 .. 37 courses)
Z_LOUVRE_LO = 0.53125           # low louvre's sill: casing 0.46875 .. 1.09375 (6 .. 14 courses)

# ------------------------------------------------------------------- bands
H_Y0 = 2.0                      # v of z = 0 on the house band
H_TOP = 3.80                    # the band reaches the fire wall's top
F_Y0 = 254.0                    # v of z = 0 on the fence band
BAND_IDS_ROWS = {"HOUSE": (0, 248), "FENCE": (252, 384)}

TONE_COURSES = 48

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels. check_regions() asserts they neither overlap nor
# run off the sheet.
UNI_Y = 390
TANK_R = (4, UNI_Y, 168, 168)            # tank side: U along, V = z - plinth top
GATE_R = (180, UNI_Y, 226, 130)          # the gate's face, 3.52 x 1.62 m
RAD_R = (526, UNI_Y, 128, 120)           # radiator bank's outer face
RAD_END_R = (662, UNI_Y, 36, 120)        # its end
CONS_R_ = (706, UNI_Y, 104, 122)         # conservator: U along, V round
GRAVEL_R = (818, UNI_Y, 178, 138)        # plinth top at GRAVEL_PPM
GRAVEL_PPM = 40.0
ROW_B = 566
TANK_TOP_R = (4, ROW_B, 168, 104)
ROOF_R = (180, ROW_B, 162, 130)          # the house roof at ROOF_PPM
ROOF_PPM = 32.0
FASCIA_R = (350, ROW_B, 322, 18)         # the slab's edge: 0.25 m tall
RAD_TOP_R = (350, 592, 130, 36)
BUSH_R = (560, 592, 48, 72)              # U round, V up the bushing
STRING_R = (616, 592, 40, 56)            # U round, V down the string
CABLE_R = (712, 592, 60, 142)
CONS_END_R = (780, 592, 40, 40)
FIRE_R = (256, 770, 232, 246)            # the fire wall's face, board-marked
TRENCH_R = (500, 770, 336, 40)           # trench covers: U along, V across
BREAKER_R = (4, 770, 48, 216)            # a breaker pole: U round, V up
POST_R = (60, 770, 32, 66)               # a disconnector post: U round, V up
CT_R = (100, 770, 48, 116)               # a current transformer: U round, V up
POLE3_R = (500, 820, 16, 172)            # LOD3's breaker pole from the ground, V at POLE3_PPM
POLE3_PPM = 32.0
# LOD3's slim gantry, the lattice painted on: a column's faces (U across
# the face whatever its width, V = z), the truss's sides (U = y, V across its
# depth) and its top and bottom (U = y, V across its width)
COL_LAT_R = (524, 822, 40, 196)
COL_LAT_PPM = 17.9
BEAM_LAT_R = (572, 822, 400, 40)
BEAM_TOP_R = (572, 870, 400, 26)
BEAM_LAT_PPM = 40.0
# the disconnector table's two legs: square lattice posts painted on solid
# stand-ins, every face alike (U across the face, V = z)
DIS_LAT_R = (984, 850, 24, 136)
DIS_LAT_PPM = 32.0

ITEM_ORIGIN = {"door": (414.0, float(UNI_Y)), "louvre": (488.0, 592.0)}

PATCH_NAMES = ("blank", "coping", "conc", "reveal", "alu", "tank_paint", "galv_paint",
               "porcelain", "steel_dark", "gate", "felt", "pad_top", "head")
PATCHES = {n: (4 + 20 * i, 740, 12, 12) for i, n in enumerate(PATCH_NAMES)}

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_CONC, ID_PAINT, ID_HW, ID_SIGN_Y, ID_SIGN_K = 5, 6, 7, 8, 9
ID_TANK, ID_TANK_DK, ID_GALV, ID_PORC, ID_ALU = 10, 11, 12, 13, 14
ID_GRAVEL, ID_FELT, ID_FLASH, ID_DARK, ID_LOUVRE = 15, 16, 17, 18, 19
ID_PLATE, ID_HEAD, ID_LAT_GAP, ID_ENAMEL, ID_ENAMEL_W = 20, 21, 22, 23, 24

# (roughness, metallic). Painted steel is dielectric to the light: the
# paint is what it sees. The gantry is hot-dip galvanised, as the catalog's
# rainwater goods are; porcelain is glazed and smooth; the bus is aluminium.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.82, 0.0), ID_MORTAR: (0.94, 0.0), ID_CONC: (0.90, 0.0),
    ID_PAINT: (0.55, 0.0), ID_HW: (0.45, 0.55), ID_SIGN_Y: (0.45, 0.0),
    ID_SIGN_K: (0.45, 0.0), ID_TANK: (0.52, 0.0), ID_TANK_DK: (0.60, 0.0),
    ID_GALV: (0.48, 0.60), ID_PORC: (0.16, 0.0), ID_ALU: (0.42, 0.75),
    ID_GRAVEL: (0.96, 0.0), ID_FELT: (0.90, 0.0), ID_FLASH: (0.50, 0.25),
    ID_DARK: (0.92, 0.0), ID_LOUVRE: (0.55, 0.0), ID_PLATE: (0.40, 0.50),
    ID_HEAD: (0.50, 0.0), ID_LAT_GAP: (0.72, 0.0), ID_ENAMEL: (0.25, 0.0),
    ID_ENAMEL_W: (0.25, 0.0),
}

# ---------------------------------------------------------------- palettes
# The plant's brick, as nostokonehuone_brick and the hall: the house, the
# wall and the fire wall change with it, and the painted steel of the gate
# and the door moves with the brick. The electrical plant is the same in
# every variant: grey-green tank paint, galvanised gantry, brown porcelain,
# the breakers' red-brown heads. red_brick is the plant's shared, muted red:
# each brick face colour c of the earlier red goes to Y + 0.6 (c - Y), Y its
# Rec. 709 luma, then times 0.94, and the mortar 10% darker again, from
# the catalog red (144, 72, 52), (114, 58, 45), mortar (150, 145, 136).
# brown_brick is a dark purple-brown clinker; both are the same constants
# in all five of the plant's pieces.
VARIANTS = {
    "red_brick": {"brick": (114, 73, 62), "brick2": (90, 59, 51),
                  "mortar": (125, 123, 118), "paint": (66, 82, 76)},
    "yellow_brick": {"brick": (188, 166, 122), "brick2": (164, 142, 104),
                     "mortar": (160, 156, 148), "paint": (104, 56, 44)},
    "brown_brick": {"brick": (80, 59, 57), "brick2": (62, 46, 45),
                    "mortar": (108, 106, 102), "paint": (60, 68, 76)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_BLANK: (52, 52, 52), ID_PLINTH: (150, 148, 142), ID_CONC: (166, 164, 156),
    ID_HW: (120, 120, 118), ID_SIGN_Y: (196, 160, 54), ID_SIGN_K: (30, 30, 30),
    ID_TANK: (104, 114, 104), ID_TANK_DK: (70, 76, 70), ID_GALV: (134, 137, 137),
    ID_PORC: (98, 54, 36), ID_ALU: (150, 152, 150), ID_GRAVEL: (128, 124, 116),
    ID_FELT: (56, 56, 58), ID_FLASH: (96, 98, 100), ID_DARK: (26, 26, 26),
    ID_LOUVRE: (112, 114, 110), ID_PLATE: (170, 170, 166), ID_HEAD: (144, 66, 44),
    # what shows between a lattice's members from 70 m on: the far face's
    # bars, the shade inside, the background, averaged into one opaque grey
    ID_LAT_GAP: (150, 153, 153),
    # a vitreous enamel plate: deep blue ground, off-white numeral and border
    ID_ENAMEL: (44, 60, 92), ID_ENAMEL_W: (196, 194, 186),
}

BAND_IDS = {
    "HOUSE": (BAND_IDS_ROWS["HOUSE"], {ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR,
                                       # the yard walls' fittings, at their own U
                                       ID_GALV, ID_HW, ID_DARK, ID_PAINT, ID_ENAMEL,
                                       ID_ENAMEL_W}),
    "FENCE": (BAND_IDS_ROWS["FENCE"], {ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR,
                                       ID_CONC}),
}

# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto: only the
# few centimetres the mesh does not model.
BRICK_FACE = brickwork.BRICK_FACE
COPING_H = 0.020
FRAME_H = 0.025         # door and gate frames
RIB_H = 0.008           # pressed ribs in the gate's sheet
STIFF_H = 0.030         # stiffeners welded round the tank
FIN_H = 0.060           # radiator fins: their edges stand proud of the gaps
SHED_H = 0.030          # porcelain sheds on a bushing
DISC_H = 0.025          # insulator discs, where the prism carries them in paint
BLADE_H = 0.030         # louvre blades
SEAM_H = 0.006          # felt laps


def m(v):
    """Metres -> pixels."""
    return v * PPM


def item_size_px(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    return (w + 2.0 * cs) * PPM, (h + cb + ct) * PPM


# ================================================================== bands
def paint_brick(c, x0, x1, y_z0, z_from, z_to, seed=17):
    """Stretcher-bond facing brick, 0.25 x 0.078 m, two tones, the mortar
    recessed and its own id, courses counted from z_from up. Tone and bond
    repeat at the atlas wrap in U."""
    brickwork.paint(c, x0, x1, y_z0 + m(z_from), y_z0 + m(z_to),
                    (ID_BRICK, ID_BRICK2, ID_MORTAR), TONE_COURSES, seed=seed)


def paint_footing(c, x0, x1, y_z0, ztop, mid=ID_PLINTH):
    """Cast concrete from the ground to ztop, darker at the foot, with the
    occluded strip under the brick's drip."""
    h = m(ztop)
    c.paint(x0, x1, y_z0 - PAD, y_z0 + h, mid, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(x0, x1, y_z0 - PAD, y_z0 + h)
    z = (Y - y_z0) / PPM
    c.shade[sy, sx] *= 0.84 + 0.16 * np.clip(z / 0.20, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.86 + 0.14 * np.clip(z / 0.20, 0, 1))
    c.mul(x0, x1, y_z0 + h - 2, y_z0 + h, 0.88, ao=0.86)


def paint_house_band(c):
    paint_brick(c, 0, ATLAS, H_Y0, Z_PLINTH, H_TOP + PAD / PPM)
    paint_footing(c, 0, ATLAS, H_Y0, Z_PLINTH)


# The house's yard walls carry fittings painted on its band, where U is
# unique to one wall: U = (s + HOUSE_U_OFF[wall]) * PPM, s along the wall
# from its start corner (build.py's H_WALLS); the north wall's whole length
# and the west wall's first 1.5 m map nowhere else. The trench covers meet
# the walls at s = TRENCH_S.
# Each a half stretcher, chosen so the bond turns a half stretcher at the
# house's four corners (build.py's brick_problems()).
HOUSE_U_OFF = {"front": 0.0, "east": 5.125, "north": 9.0, "west": 14.125}
TRENCH_S = {"west": -1.94 - T_Y[0], "north": 7.94 - TRENCH_TURN_X}
LAMP_S, LAMP_Z = 1.05, 2.70     # the yard lamp on the west wall: centre, shade's rim
PLATE_S, PLATE_Z = 2.30, 1.62   # the enamel number plate on the north wall: centre, foot


def paint_house_fittings(c):
    """On the yard walls: a galvanised cover plate sealing each cable trench
    where its covers meet the wall; a wall-mounted yard lamp (painted dark
    paint outside, white enamel inside, unlit) on the west wall over the
    south trench; a small blue enamel number plate at eye height on the
    north wall, a plain white numeral, no words."""
    def U(wall, s):
        return (s + HOUSE_U_OFF[wall]) * PPM

    def V(z):
        return H_Y0 + z * PPM
    for wall, s in TRENCH_S.items():
        a, b = U(wall, s - 0.34), U(wall, s + 0.34)
        z0, z1 = V(TRENCH_H), V(0.50)
        c.paint(a, b, z0, z1, ID_GALV, 0.92, 0.95, height=0.006)
        c.bevel(a, b, z0, z1, 0.006, 1.0)
        c.mul(a, b, z0 - 1.5, z0, 0.70, ao=0.7)
        c.mul(a - 1, a, z0, z1, 0.86, ao=0.85)
        for bx in (a + 2.5, (a + b) / 2.0, b - 2.5):
            for by in (z0 + 2.5, z1 - 2.5):
                c.disc(bx, by, 0.9, ID_HW, 0.8, 0.85, height=0.012)
        for gx in (a + (b - a) * 0.3, a + (b - a) * 0.7):       # two cable glands
            c.disc(gx, z0 + 9.0, 3.0, ID_HW, 0.85, 0.85, height=0.02)
            c.disc(gx, z0 + 9.0, 1.6, ID_DARK, 1.0, 0.7, height=0.012)
    # the yard lamp: wall plate, a short arm, the conical shade, its rim
    # and the white enamel reflector seen under it
    x = U("west", LAMP_S)
    z = V(LAMP_Z)
    c.paint(x - 3.2, x + 3.2, z + m(0.24), z + m(0.38), ID_PAINT, 0.85, 0.9, height=0.015)
    c.paint(x - 1.0, x + 1.0, z + m(0.16), z + m(0.25), ID_PAINT, 0.80, 0.85, height=0.03)
    shade = [(x - m(0.18), z), (x + m(0.18), z), (x + m(0.05), z + m(0.16)),
             (x - m(0.05), z + m(0.16))]
    box = (x - m(0.19), x + m(0.19), z - 2, z + m(0.17))
    c.shape(*box, lambda X, Y: _in_poly(X, Y, shade), ID_PAINT, 0.95, 0.9, height=0.05)
    c.paint(x - m(0.18), x + m(0.18), z, z + 1.0, ID_PAINT, 1.12, 0.9, height=0.055)
    c.paint(x - m(0.16), x + m(0.16), z - 1.4, z, ID_ENAMEL_W, 0.80, 0.7, height=0.04)
    c.mul(x - m(0.14), x + m(0.14), z - 2.6, z - 1.4, 0.75, ao=0.75)
    # the number plate: white border, blue ground, a white numeral 1
    px, pz = U("north", PLATE_S), V(PLATE_Z)
    w, h = m(0.22), m(0.16)
    c.paint(px - w / 2, px + w / 2, pz, pz + h, ID_ENAMEL_W, 1.0, 1.0, height=0.004)
    c.bevel(px - w / 2, px + w / 2, pz, pz + h, 0.004, 0.8)
    c.paint(px - w / 2 + 0.9, px + w / 2 - 0.9, pz + 0.9, pz + h - 0.9, ID_ENAMEL, 1.0, 1.0)
    c.paint(px - 0.55, px + 0.75, pz + 2.2, pz + h - 2.0, ID_ENAMEL_W, 1.0, 1.0)
    c.stroke((px - 0.2, pz + h - 2.2), (px - 2.0, pz + h - 3.6), 1.1, ID_ENAMEL_W, 1.0)
    c.paint(px - 1.6, px + 1.8, pz + 2.0, pz + 3.0, ID_ENAMEL_W, 1.0, 1.0)
    c.mul(px - w / 2, px + w / 2, pz - 1.0, pz, 0.85, ao=0.85)


def paint_coping(c, x0, x1, y0, y1, axes="y"):
    """A precast concrete coping or cap: arrises catching the light, a drip
    shadow on the brick under it."""
    c.paint(x0, x1, y0, y1, ID_CONC, 1.0, 1.0)
    c.bevel(x0, x1, y0, y1, COPING_H, 1.0, axes=axes)
    c.mul(x0, x1, y0, y0 + 1, 0.86, ao=0.86)
    c.mul(x0, x1, y0 - 2, y0, 0.86, ao=0.84)


def paint_fence_band(c):
    top = F_Y0 + m(Z_FENCE)
    paint_brick(c, 0, ATLAS, F_Y0, Z_FOOT_F, Z_COPING, seed=41)
    paint_footing(c, 0, ATLAS, F_Y0, Z_FOOT_F)
    paint_coping(c, 0, ATLAS, F_Y0 + m(Z_COPING), top + PAD)


# ================================================================= regions
def _bar(c, a0, a1, b0, b1, mid, h, shade=1.0, ao=0.9, axes="xy"):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, 1.0, axes=axes)


def _in_poly(X, Y, pts):
    """Even-odd point-in-polygon over sample grids."""
    inside = np.zeros(X.shape, bool)
    n = len(pts)
    for i in range(n):
        (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
        cond = (ay > Y) != (by > Y)
        xint = ax + (Y - ay) * (bx - ax) / ((by - ay) if by != ay else 1e-9)
        inside ^= cond & (X < xint)
    return inside


def paint_warning(c, cx, cy, side):
    """A generic high-voltage warning plate: a yellow equilateral triangle
    with a black border and a black lightning arrow, no lettering. *side*
    in pixels, (cx, cy) its centroid."""
    hgt = side * np.sqrt(3.0) / 2.0
    tri = [(cx - side / 2, cy - hgt / 3), (cx + side / 2, cy - hgt / 3), (cx, cy + 2 * hgt / 3)]
    box = (cx - side / 2 - 1, cx + side / 2 + 1, cy - hgt / 3 - 1, cy + 2 * hgt / 3 + 1)

    def shrink(k):
        return [(cx + (px - cx) * k, cy + (py - cy) * k) for px, py in tri]

    c.shape(*box, lambda X, Y: _in_poly(X, Y, tri), ID_SIGN_K, 1.0, height=0.004)
    c.shape(*box, lambda X, Y: _in_poly(X, Y, shrink(0.80)), ID_SIGN_Y, 1.0,
            height=0.004)
    s = side / 24.0
    bolt = [(cx + 1.0 * s, cy + 6.5 * s), (cx - 2.6 * s, cy - 0.2 * s),
            (cx + 0.2 * s, cy - 0.2 * s), (cx - 1.6 * s, cy - 5.6 * s),
            (cx + 2.8 * s, cy + 1.2 * s), (cx + 0.0 * s, cy + 1.2 * s),
            (cx + 2.2 * s, cy + 6.5 * s)]
    c.shape(*box, lambda X, Y: _in_poly(X, Y, bolt), ID_SIGN_K, 1.0, height=0.004)


def gate_u(x):
    """The gate region's U, in pixels, of plan x along the gate's face."""
    return GATE_R[0] + (x - (GATE_OPEN[0] - GATE_INTO)) * PPM


def paint_gate(c):
    """A sheet-steel double gate: each leaf a frame of square tube round a
    sheet with pressed vertical ribs, a mid rail, heavy hinges on the outer
    stiles, a drop bolt and a padlocked hasp where the leaves meet, and a
    high-voltage warning plate on the left leaf."""
    x, y, w, h = GATE_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_PAINT, 1.0, 1.0, height=0.0)
    l0, l1 = gate_u(GATE_OPEN[0]), gate_u(GATE_OPEN[1])
    mid = (l0 + l1) / 2.0
    F = m(0.06)
    gh = GATE_Z[1] - GATE_Z[0]                    # the leaves' height
    top = y + m(gh)
    for a0, a1, hinge in ((l0, mid - 0.6, l0), (mid + 0.6, l1, l1)):
        sy, sx, _, X = c.field(a0, a1, y, top)
        r = (X - a0) % m(0.15)
        c.height[sy, sx] = np.where(r < 3.0, RIB_H * np.sin(np.pi * np.clip(r / 3.0, 0, 1)), 0.0)
        c.shade[sy, sx] = np.where((r >= 3.0) & (r < 4.0), 0.92, 1.0)
        for b0, b1 in ((y, y + F), (y + m(0.49 * gh), y + m(0.49 * gh) + F), (top - F, top)):
            _bar(c, a0, a1, b0, b1, ID_PAINT, FRAME_H, 1.0, 0.9, "y")
            c.mul(a0, a1, b0 - 2, b0, 0.88, ao=0.84)
        _bar(c, a0, a0 + F, y, top, ID_PAINT, FRAME_H, 1.0, 0.9, "x")
        _bar(c, a1 - F, a1, y, top, ID_PAINT, FRAME_H, 1.0, 0.9, "x")
        for zz in (0.28, gh - 0.24):
            hy = y + m(zz)
            hx0 = hinge - 2 if hinge == l0 else hinge - 12
            c.paint(hx0, hx0 + 14, hy - 3, hy + 3, ID_HW, 0.80, 0.86, height=0.040)
            c.mul(hx0, hx0 + 14, hy - 5, hy - 3, 0.82, ao=0.8)
    # meeting stiles, drop bolt, hasp and padlock
    c.paint(mid - 0.6, mid + 0.6, y, top, ID_DARK, 1.0, 0.5, height=-0.004)
    c.paint(mid + 2, mid + 4, y + 2, y + m(0.55), ID_HW, 0.85, 0.85, height=0.03)
    hasp = 0.62 * gh
    c.paint(mid - 7, mid + 7, y + m(hasp), y + m(hasp + 0.06), ID_HW, 0.9, 0.85, height=0.035)
    c.paint(mid - 3, mid + 1, y + m(hasp - 0.08), y + m(hasp), ID_DARK, 1.0, 0.8, height=0.045)
    # the warning plate, 0.38 m, high on the left leaf
    paint_warning(c, (l0 + mid) / 2.0, y + m(gh - 0.38), m(0.38))
    # the leaves' foot is just off the ground: dark under the bottom rail
    c.mul(l0, l1, y, y + 1.5, 0.80, ao=0.8)


def paint_door(c):
    """The switchgear room's steel door: a pressed steel frame round a flush
    leaf with a lever handle and lock, a kick plate, a warning plate at eye
    height."""
    x0, y0 = ITEM_ORIGIN["door"]
    w, h, cs, cb, ct = OPENINGS["door"]
    rw, rh = item_size_px("door")
    c.paint(x0 - PAD, x0 + rw + PAD, y0 - PAD, y0 + rh + PAD, ID_PAINT, 0.86, 0.9,
            height=FRAME_H)
    c.bevel(x0 - PAD, x0 + rw + PAD, y0 - PAD, y0 + rh + PAD, FRAME_H, 1.0)
    lx0, lx1 = x0 + m(cs), x0 + m(cs + w)
    yt = y0 + m(h)
    c.paint(lx0, lx1, y0, yt, ID_PAINT, 1.0, 0.95, height=0.0)
    c.mul(lx0, lx1, yt - 2, yt, 0.84, ao=0.8)                   # under the head
    c.mul(lx0 - 1, lx0, y0, yt, 0.80, ao=0.8)
    c.mul(lx1, lx1 + 1, y0, yt, 0.80, ao=0.8)
    c.paint(lx0 + 2, lx1 - 2, y0 + 1, y0 + m(0.22), ID_HW, 0.85, 0.9, height=0.003)
    hx, hy = lx1 - 7, y0 + m(1.05)
    c.paint(hx - 1.5, hx + 1.5, hy - 6, hy + 5, ID_HW, 1.0, 0.9, height=0.01)
    c.stroke((hx, hy + 2), (hx - 8, hy + 2), 2.2, ID_HW, 1.0, 0.9, height=0.04)
    c.disc(hx, hy - 4, 1.2, ID_DARK, 1.0, 0.8, height=0.0)
    paint_warning(c, (lx0 + lx1) / 2.0, y0 + m(1.55), m(0.30))
    c.paint(lx0, lx1, y0, y0 + 1.5, ID_DARK, 1.0, 0.8)


def paint_louvre(c):
    """A steel louvre in a pressed frame: blades sloping out and down, dark
    between, insect mesh behind."""
    x0, y0 = ITEM_ORIGIN["louvre"]
    rw, rh = item_size_px("louvre")
    F = 4
    c.paint(x0 - PAD, x0 + rw + PAD, y0 - PAD, y0 + rh + PAD, ID_LOUVRE, 1.0, 1.0)
    c.bevel(x0 - PAD, x0 + rw + PAD, y0 - PAD, y0 + rh + PAD, 0.02, 1.5)
    c.paint(x0 + F, x0 + rw - F, y0 + F, y0 + rh - F, ID_DARK, 1.0, 0.5, height=-0.02)
    for yy in np.arange(y0 + F, y0 + rh - F - 1, 4.0):
        c.paint(x0 + F, x0 + rw - F, yy, yy + 3, ID_LOUVRE, 0.92, 0.85)
        sy, sx, Y, _ = c.field(x0 + F, x0 + rw - F, yy, yy + 3)
        c.height[sy, sx] = BLADE_H * (1.0 - (Y - yy) / 3.0)
        c.paint(x0 + F, x0 + rw - F, yy, yy + 1, ID_LOUVRE, 0.78, 0.8)
    c.mul(x0 + F, x0 + rw - F, y0 + rh - F - 3, y0 + rh - F, 0.80, ao=0.7)


def paint_fascia(c):
    """The roof slab's edge: cast concrete, a drip groove under it, the
    felt's dressed-down edge and a steel trim strip along the top."""
    x, y, w, h = FASCIA_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CONC, 1.0, 1.0, height=0.0)
    c.mul(x - PAD, x + w + PAD, y - PAD, y + 1, 0.82, ao=0.86)
    top = y + m(Z_TOP - Z_WALL)
    c.paint(x - PAD, x + w + PAD, top - 3, top + PAD, ID_FLASH, 1.0, 1.0, height=0.008)
    c.mul(x - PAD, x + w + PAD, top - 4, top - 3, 0.80, ao=0.80)


def paint_roof(c):
    """The house's flat roof at ROOF_PPM: bitumen felt in 1 m laps along X,
    a steel edge trim round it, a rainwater outlet near the north edge."""
    x, y, w, h = ROOF_R
    k = ROOF_PPM
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_FELT, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x, x + w, y, y + h)
    lap = ((X - x) % k) < 1.0
    c.shade[sy, sx] = np.where(lap, 0.88, 1.0)
    c.height[sy, sx] = np.where(lap, SEAM_H * k / PPM, 0.0)
    e = 0.06 * k
    for a0, a1, b0, b1 in ((x - PAD, x + w + PAD, y - PAD, y + e),
                           (x - PAD, x + w + PAD, y + h - e, y + h + PAD),
                           (x - PAD, x + e, y - PAD, y + h + PAD),
                           (x + w - e, x + w + PAD, y - PAD, y + h + PAD)):
        c.paint(a0, a1, b0, b1, ID_FLASH, 1.0, 1.0, height=0.0)
    ox, oy = x + 3.5 * k, y + h - 0.4 * k
    c.disc(ox, oy, 0.12 * k, ID_DARK, 0.8, 0.6, height=-0.01)


def paint_tank(c):
    """A tank side in grey-green: the cover's bolted flange along the top,
    the base frame along the foot, stiffeners, lifting lugs at the corners,
    a blank rating plate and a drain valve. U from the face's left edge, V
    from the plinth's top."""
    x, y, w, h = TANK_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_TANK, 1.0, 1.0, height=0.0)
    top = y + m(TANK_Z[1] - PLINTH[2])
    # base frame, 0.12 m, darker paint
    c.paint(x - PAD, x + w + PAD, y - PAD, y + m(0.12), ID_TANK_DK, 1.0, 0.9, height=0.02)
    c.mul(x - PAD, x + w + PAD, y + m(0.12), y + m(0.12) + 2, 0.86, ao=0.84)
    # cover flange, 0.10 m, its bolts every 0.15 m
    f0 = top - m(0.10)
    c.paint(x - PAD, x + w + PAD, f0, top + PAD, ID_TANK, 0.94, 1.0, height=0.025)
    c.mul(x - PAD, x + w + PAD, f0 - 2, f0, 0.82, ao=0.80)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, f0 + 2, top - 2)
    bolt = (np.abs((X - x) % m(0.15) - m(0.075)) < 1.2) & (np.abs(Y - (f0 + top) / 2) < 1.4)
    c.height[sy, sx] = np.where(bolt, 0.04, c.height[sy, sx])
    c.shade[sy, sx] = np.where(bolt, 0.85, c.shade[sy, sx])
    # horizontal stiffeners at a third and two thirds of the height
    for zz in (0.85, 1.70):
        b0 = y + m(zz)
        _bar(c, x - PAD, x + w + PAD, b0, b0 + 4, ID_TANK, STIFF_H, 1.0, 0.95, "y")
        c.mul(x - PAD, x + w + PAD, b0 - 2, b0, 0.86, ao=0.86)
    # lifting lugs near the top corners
    for lx in (x + 6, x + w - 14):
        c.paint(lx, lx + 8, f0 - 10, f0, ID_TANK, 0.92, 0.9, height=0.04)
        c.disc(lx + 4, f0 - 5, 2.0, ID_DARK, 0.6, 0.6, height=0.0)
    # rating plate (blank) and the drain valve
    c.paint(x + 18, x + 34, y + m(1.25), y + m(1.45), ID_PLATE, 1.0, 1.0, height=0.004)
    c.mul(x + 18, x + 34, y + m(1.25) - 1, y + m(1.25), 0.8)
    c.disc(x + w - 24, y + m(0.30), 3.5, ID_HW, 0.9, 0.85, height=0.04)
    c.disc(x + w - 24, y + m(0.30), 1.5, ID_DARK, 1.0, 0.7, height=0.05)


def paint_tank_top(c):
    """The cover: a bolt ring round its edge and an inspection cover."""
    x, y, w, h = TANK_TOP_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_TANK, 0.96, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x, x + w, y, y + h)
    d = np.minimum(np.minimum(X - x, x + w - X), np.minimum(Y - y, y + h - Y))
    ring = (d > 2.0) & (d < 4.5)
    c.shade[sy, sx] = np.where(ring, 0.90, c.shade[sy, sx])
    along = np.where(np.minimum(X - x, x + w - X) < np.minimum(Y - y, y + h - Y), Y, X)
    bolt = ring & (np.abs(along % m(0.15) - m(0.075)) < 1.2)
    c.height[sy, sx] = np.where(bolt, 0.03, 0.0)
    c.shade[sy, sx] = np.where(bolt, 0.80, c.shade[sy, sx])
    c.disc(x + w * 0.62, y + h * 0.5, m(0.22), ID_TANK, 0.92, 0.9, height=0.02)
    c.disc(x + w * 0.62, y + h * 0.5, m(0.22), ID_TANK, 0.80, 0.8, inner=m(0.20))


def paint_radiator(c):
    """A radiator bank's outer face: the edges of pressed-steel fins every
    0.05 m, dark gaps between them, three elements to the bank with a wider
    gap between, header pipes along the top and bottom."""
    x, y, w, h = RAD_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_TANK, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    pitch = m(0.05)
    r = (X - x) % pitch
    fin = r < 1.2
    elem = np.abs(((X - x) % m(RAD_X / 3.0)) - 0.0) < 2.5
    gap = ~fin
    c.shade[sy, sx] = np.where(fin, 1.04, 0.42)
    c.ao[sy, sx] = np.where(fin, 0.92, 0.38)
    c.height[sy, sx] = np.where(fin, FIN_H, 0.0)
    c.shade[sy, sx] = np.where(elem & gap, 0.25, c.shade[sy, sx])
    c.mid[sy, sx] = np.where(gap, ID_TANK_DK, ID_TANK)
    for b0, b1 in ((y - PAD, y + 7), (y + h - 7, y + h + PAD)):
        c.paint(x - PAD, x + w + PAD, b0, b1, ID_TANK, 1.0, 0.95)
        sy2, sx2, Y2, _ = c.field(x - PAD, x + w + PAD, b0, b1)
        u = 2.0 * (Y2 - b0) / (b1 - b0) - 1.0
        c.height[sy2, sx2] = 0.08 * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.mul(x - PAD, x + w + PAD, y + 7, y + 9, 0.80, ao=0.8)
    c.mul(x - PAD, x + w + PAD, y + h - 9, y + h - 7, 0.86, ao=0.85)


def paint_radiator_end(c):
    """The outermost fin seen flat: pressed vertical channels, the header
    pipes' ends top and bottom."""
    x, y, w, h = RAD_END_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_TANK, 1.0, 1.0, height=0.0)
    sy, sx, _, X = c.field(x, x + w, y + 7, y + h - 7)
    r = (X - x) % m(0.09)
    c.height[sy, sx] = np.where(r < 3.5, 0.012 * np.sin(np.pi * r / 3.5), 0.0)
    c.shade[sy, sx] = np.where((r >= 3.5) & (r < 4.5), 0.90, 1.0)
    for b0 in (y + 1, y + h - 7):
        c.disc(x + w / 2.0, b0 + 3, 3.2, ID_TANK, 0.94, 0.95, height=0.03)


def paint_radiator_top(c):
    """The fins' top edges seen from above: stripes across the bank."""
    x, y, w, h = RAD_TOP_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_TANK, 1.0, 1.0, height=0.0)
    sy, sx, _, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    fin = ((X - x) % m(0.05)) < 1.2
    c.shade[sy, sx] = np.where(fin, 1.04, 0.40)
    c.ao[sy, sx] = np.where(fin, 0.92, 0.38)
    c.mid[sy, sx] = np.where(fin, ID_TANK, ID_TANK_DK)
    c.height[sy, sx] = np.where(fin, FIN_H, 0.0)


def paint_conservator(c):
    """The conservator's barrel: tank paint, a girth seam at each end, the
    pipe flange on its underside. U along the axis, V round from the top."""
    x, y, w, h = CONS_R_
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_TANK, 1.0, 1.0, height=0.0)
    for sx0 in (x + 3, x + w - 5):
        c.paint(sx0, sx0 + 2, y - PAD, y + h + PAD, ID_TANK, 0.86, 0.9, height=0.006)
    sy, sx, Y, _ = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    ang = (Y - y) / h * 2.0 * np.pi          # 0 at the top, round and back
    c.shade[sy, sx] *= 0.94 + 0.06 * np.cos(ang)    # dust settles on top: AO below
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.85 + 0.15 * np.cos(ang))
    x2, y2, w2, h2 = CONS_END_R
    c.paint(x2 - PAD, x2 + w2 + PAD, y2 - PAD, y2 + h2 + PAD, ID_TANK, 0.96, 1.0, height=0.0)
    cx, cy = x2 + w2 / 2.0, y2 + h2 / 2.0
    c.disc(cx, cy, 7.0, ID_HW, 0.9, 0.9, height=0.02)       # the level gauge
    c.disc(cx, cy, 5.0, ID_PLATE, 1.0, 0.9, height=0.025)
    c.stroke((cx, cy), (cx + 3.0, cy + 2.5), 1.0, ID_DARK, 1.0, height=0.026)


def bushing_profile():
    """(radius, z) rings of a bushing from 0.05 under the cover up, metres:
    the steel turret, the porcelain body tapering to the head, the
    terminal. build.py turns it; paint_bushing() reads its z breaks."""
    return [(0.15, 0.0), (0.15, 0.27), (0.115, 0.27), (0.075, 1.00),
            (0.05, 1.00), (0.05, BUSH_H)]


Z_PORC = (0.27, 1.00)


def paint_bushing(c):
    """A bushing wrapped once round: steel turret, brown glazed porcelain
    with a shed every 0.07 m, an aluminium terminal. V = metres up from the
    turret's foot."""
    x, y, w, h = BUSH_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_TANK, 1.0, 1.0, height=0.0)
    p0, p1 = y + m(Z_PORC[0]), y + m(Z_PORC[1])
    c.paint(x - PAD, x + w + PAD, p0, p1, ID_PORC, 1.0, 1.0)
    sy, sx, Y, _ = c.field(x - PAD, x + w + PAD, p0, p1)
    t = ((Y - p0) % m(0.07)) / m(0.07)
    c.height[sy, sx] = SHED_H * np.where(t < 0.55, np.sin(np.pi * t / 0.55), 0.0)
    c.shade[sy, sx] = np.where(t >= 0.80, 0.55, np.where(t < 0.12, 1.10, 1.0))
    c.ao[sy, sx] = np.where(t >= 0.80, 0.55, 1.0)
    c.paint(x - PAD, x + w + PAD, p1, y + h + PAD, ID_ALU, 1.0, 1.0, height=0.0)
    c.mul(x - PAD, x + w + PAD, p0 - 2, p0, 0.82, ao=0.8)      # turret flange
    c.mul(x - PAD, x + w + PAD, p1, p1 + 1.5, 0.86, ao=0.85)


def porcelain(c, x0, x1, a, b, pitch=0.07):
    """Brown glazed porcelain from row a to b: a shed every *pitch* m, the
    deep shadow under each shed a third of the pitch, so a column of sheds
    reads darker than the bushings' short ones and its cast heads stand
    out. The light on the sheds' upper faces is the normal map's."""
    c.paint(x0, x1, a, b, ID_PORC, 0.86, 1.0)
    sy, sx, Y, _ = c.field(x0, x1, a, b)
    t = ((Y - a) % m(pitch)) / m(pitch)
    c.height[sy, sx] = SHED_H * np.where(t < 0.55, np.sin(np.pi * t / 0.55), 0.0)
    c.shade[sy, sx] = np.where(t >= 0.66, 0.42, 0.86)
    c.ao[sy, sx] = np.where(t >= 0.66, 0.50, 1.0)


# (radius, h) rings of the switchgear's turned parts, h up from each foot in
# metres; build.py turns them and the paint below reads their breaks.
Z_BRK = (1.25, 1.60, 2.95, 3.30)        # mid head foot, top; top head foot, top


def breaker_profile(full=True):
    """A minimum-oil breaker pole: the support porcelain, the red-brown mid
    head (the interrupter's lower terminal), the chamber's porcelain and
    the red-brown top head. *full* steps the heads out; otherwise one
    taper carries them in paint."""
    a, b, c_, d = Z_BRK
    if not full:
        return [(0.14, 0.0), (0.12, d)]
    return [(0.12, 0.0), (0.12, a), (0.17, a), (0.17, b), (0.12, b), (0.11, c_),
            (0.16, c_), (0.16, d)]


Z_POST = 0.88                           # a disconnector post's cap foot
POST_H = 0.98                           # and its top


def post_profile(full=True):
    if not full:
        return [(0.09, 0.0), (0.075, POST_H)]
    return [(0.09, 0.0), (0.075, Z_POST), (0.10, Z_POST), (0.10, POST_H)]


Z_CT = (0.21, 1.35, 1.75)               # base top, head foot, head top


def ct_profile(full=True):
    """A current transformer: steel base, porcelain, the oil head. *full*
    True turns them all; "mid" folds the base into the porcelain's taper;
    False is one taper carrying all three in paint."""
    a, b, t = Z_CT
    if full is True:
        return [(0.15, 0.0), (0.15, a), (0.12, a), (0.10, b), (0.19, b), (0.19, t)]
    if full == "mid":
        return [(0.15, 0.0), (0.11, b), (0.19, b), (0.19, t)]
    return [(0.14, 0.0), (0.17, t)]


def paint_breaker(c):
    """A breaker pole wrapped once round, V = metres up from its foot:
    porcelain with its sheds, the two red-brown cast heads with a bolted
    flange at each end, a darker vent cap on the top."""
    x, y, w, h = BREAKER_R
    a, b, c_, d = (y + m(v) for v in Z_BRK)
    porcelain(c, x - PAD, x + w + PAD, y - PAD, a)
    porcelain(c, x - PAD, x + w + PAD, b, c_)
    for h0, h1 in ((a, b), (c_, y + h + PAD)):
        c.paint(x - PAD, x + w + PAD, h0 - 1, h1, ID_HEAD, 1.0, 1.0, height=0.0)
        c.paint(x - PAD, x + w + PAD, h0 - 1, h0 + 3, ID_HEAD, 0.86, 0.9, height=0.012)
        c.mul(x - PAD, x + w + PAD, h0 - 3, h0 - 1, 0.70, ao=0.7)
    c.paint(x - PAD, x + w + PAD, b - 3, b, ID_HEAD, 0.86, 0.9, height=0.012)
    c.paint(x - PAD, x + w + PAD, d - 4, y + h + PAD, ID_HW, 0.80, 0.9, height=0.01)
    c.paint(x + 4, x + 12, a + 6, a + 14, ID_PLATE, 1.0, 1.0, height=0.004)


def paint_pole3(c):
    """LOD3's breaker pole, one prism from the ground at POLE3_PPM: the
    galvanised stand, then the pole's porcelain and red-brown heads with
    the sheds averaged into a darker brown, as they read from 120 m on."""
    x, y, w, h = POLE3_R
    k = POLE3_PPM
    z = lambda v: y + (BRK_Z0 + v) * k
    c.paint(x - PAD, x + w + PAD, y - PAD, y + BRK_Z0 * k, ID_GALV, 0.95, 1.0, height=0.0)
    c.paint(x - PAD, x + w + PAD, y + BRK_Z0 * k, y + h + PAD, ID_PORC, 0.68, 0.8, height=0.0)
    for h0, h1 in ((Z_BRK[0], Z_BRK[1]), (Z_BRK[2], Z_BRK[3] + 1.0)):
        c.paint(x - PAD, x + w + PAD, z(h0), z(h1), ID_HEAD, 1.0, 1.0, height=0.0)


def paint_post(c):
    """A disconnector post insulator: porcelain, a galvanised cap."""
    x, y, w, h = POST_R
    porcelain(c, x - PAD, x + w + PAD, y - PAD, y + m(Z_POST), pitch=0.08)
    c.paint(x - PAD, x + w + PAD, y + m(Z_POST), y + h + PAD, ID_GALV, 0.92, 0.9, height=0.0)
    c.mul(x - PAD, x + w + PAD, y + m(Z_POST), y + m(Z_POST) + 2, 0.80, ao=0.8)
    c.paint(x - PAD, x + w + PAD, y - PAD, y + 3, ID_GALV, 0.85, 0.9, height=0.01)


def paint_ct(c):
    """A current transformer: its steel base in tank paint, porcelain, the
    oil head with a sight glass and a bolted flange."""
    x, y, w, h = CT_R
    a, b, t = (y + m(v) for v in Z_CT)
    c.paint(x - PAD, x + w + PAD, y - PAD, a, ID_TANK_DK, 1.0, 0.9, height=0.0)
    c.paint(x - PAD, x + w + PAD, a - 3, a, ID_TANK_DK, 0.9, 0.9, height=0.012)
    porcelain(c, x - PAD, x + w + PAD, a, b)
    c.paint(x - PAD, x + w + PAD, b, y + h + PAD, ID_TANK, 1.0, 1.0, height=0.0)
    c.paint(x - PAD, x + w + PAD, b, b + 4, ID_TANK, 0.88, 0.9, height=0.015)
    c.mul(x - PAD, x + w + PAD, b - 2, b, 0.75, ao=0.7)
    c.disc(x + w * 0.5, b + m(0.22), 3.0, ID_DARK, 0.9, 0.8, height=0.0)
    c.paint(x - PAD, x + w + PAD, t - 3, y + h + PAD, ID_TANK, 0.90, 0.9, height=0.01)


def string_profile():
    """(radius, z) rings of a suspension string, z downward from its top in
    metres: the cap and pin, four discs at 0.146 m, the clamp."""
    rings = [(0.035, 0.0), (0.035, 0.12)]
    z = 0.12
    for _ in range(4):
        rings += [(0.125, z + 0.03), (0.125, z + 0.05), (0.035, z + 0.10)]
        z += 0.146
    rings += [(0.035, STRING_LEN - 0.08), (0.05, STRING_LEN - 0.08), (0.05, STRING_LEN)]
    return rings


def paint_string(c):
    """An insulator string wrapped once round, V down from its top: the
    discs' brown porcelain rims light, the caps and pins dark galvanised;
    on a tier that turns the string as a plain prism this paint is all
    there is of the discs."""
    x, y, w, h = STRING_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_GALV, 0.80, 0.9, height=0.0)
    for i in range(4):
        z0 = 0.12 + 0.146 * i
        a, b = y + m(z0), y + m(z0 + 0.10)
        c.paint(x - PAD, x + w + PAD, a, b, ID_PORC, 1.0, 1.0)
        sy, sx, Y, _ = c.field(x - PAD, x + w + PAD, a, b)
        t = (Y - a) / (b - a)
        c.height[sy, sx] = DISC_H * np.sin(np.pi * t)
        c.shade[sy, sx] = np.where(t > 0.7, 0.60, 1.0)


def paint_lattice(c):
    """LOD3's slim gantry: the lattice painted on, galvanised members
    over the ID_LAT_GAP grey that stands for the openings. The column region
    has a corner angle at each edge, the rails and N-truss diagonals at
    G_SHAFT_PTS, the peak's diagonal and rail, the finial solid; the truss's
    sides have their chords top and bottom, end rails and the Warren zigzag;
    its top and bottom their chords at the edges, rails at BEAM_PTS and a
    zigzag between them. Member widths are the lattice's, at least a pixel."""
    lw = 0.9                                        # a bar's painted width, px

    def member(p0, p1):
        c.stroke(p0, p1, lw, ID_GALV, 1.0, 0.95, height=0.0)

    x, y, w, h = COL_LAT_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_LAT_GAP, 1.0, 1.0, height=0.0)
    edge = 0.16 * w
    zr = lambda z: y + z * COL_LAT_PPM
    c.paint(x - PAD, x + edge, y - PAD, y + h + PAD, ID_GALV, 1.0, 1.0)
    c.paint(x + w - edge, x + w + PAD, y - PAD, y + h + PAD, ID_GALV, 1.0, 1.0)
    c.paint(x - PAD, x + w + PAD, y - PAD, zr(G_PAD[1]), ID_GALV, 0.92, 0.9)
    c.paint(x - PAD, x + w + PAD, zr(G_PEAK_Z), y + h + PAD, ID_GALV, 1.0, 1.0)
    l, r = x + edge, x + w - edge
    for z in G_SHAFT_PTS + (G_PEAK_RAIL,):
        member((l, zr(z)), (r, zr(z)))
    pts = G_SHAFT_PTS + (G_PEAK_RAIL,)
    for za, zb in zip(pts, pts[1:]):
        member((l, zr(za)), (r, zr(zb)))
    # the truss's sides: U = y from the region's middle, V across the depth
    x, y, w, h = BEAM_LAT_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_LAT_GAP, 1.0, 1.0, height=0.0)
    u = lambda t: x + w / 2.0 + t * BEAM_LAT_PPM
    ch = G_CHORD / (2.0 * BEAM_HD * G_SOLID[2]) * h
    c.paint(x - PAD, x + w + PAD, y - PAD, y + ch, ID_GALV, 1.0, 1.0)
    c.paint(x - PAD, x + w + PAD, y + h - ch, y + h + PAD, ID_GALV, 1.0, 1.0)
    for t in (-BEAM_YP, BEAM_YP):
        member((u(t), y + ch), (u(t), y + h - ch))
    c.paint(x - PAD, u(-BEAM_YP) - 1, y - PAD, y + h + PAD, ID_GALV, 1.0, 1.0)
    c.paint(u(BEAM_YP) + 1, x + w + PAD, y - PAD, y + h + PAD, ID_GALV, 1.0, 1.0)
    n = BEAM_SIDE_N
    for k in range(n):
        ta, tb = (-BEAM_YP + 2 * BEAM_YP * j / n for j in (k, k + 1))
        lo, hi = (y + ch, y + h - ch) if k % 2 == 0 else (y + h - ch, y + ch)
        member((u(ta), lo), (u(tb), hi))
    # its top and bottom
    x, y, w, h = BEAM_TOP_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_LAT_GAP, 1.0, 1.0, height=0.0)
    u = lambda t: x + w / 2.0 + t * BEAM_LAT_PPM
    ch = G_CHORD / (2.0 * BEAM_HW * G_SOLID[1]) * h
    c.paint(x - PAD, x + w + PAD, y - PAD, y + ch, ID_GALV, 1.0, 1.0)
    c.paint(x - PAD, x + w + PAD, y + h - ch, y + h + PAD, ID_GALV, 1.0, 1.0)
    c.paint(x - PAD, u(-BEAM_YP) - 1, y - PAD, y + h + PAD, ID_GALV, 1.0, 1.0)
    c.paint(u(BEAM_YP) + 1, x + w + PAD, y - PAD, y + h + PAD, ID_GALV, 1.0, 1.0)
    for t in BEAM_PTS:
        member((u(t), y + ch), (u(t), y + h - ch))
    for k, (ta, tb) in enumerate(zip(BEAM_PTS, BEAM_PTS[1:])):
        lo, hi = (y + ch, y + h - ch) if k % 2 == 0 else (y + h - ch, y + ch)
        member((u(ta), lo), (u(tb), hi))


def paint_dis_leg(c):
    """The disconnector table's legs: a corner angle down each edge of the
    face, a rail at each panel point and a zigzag of diagonals between, over
    a darker grey for the shade inside the leg and the yard seen through
    it; a solid base plate at the foot and a cap plate under the deck."""
    x, y, w, h = DIS_LAT_R
    z1 = DIS_DECK[2]                                # the deck's underside
    zr = lambda z: y + z * DIS_LAT_PPM
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_LAT_GAP, 0.32, 0.5, height=0.0)
    edge = w * 0.05 / DIS_LEG[0]
    c.paint(x - PAD, x + edge, y - PAD, y + h + PAD, ID_GALV, 1.0, 1.0, height=0.0)
    c.paint(x + w - edge, x + w + PAD, y - PAD, y + h + PAD, ID_GALV, 1.0, 1.0, height=0.0)
    c.paint(x - PAD, x + w + PAD, y - PAD, zr(0.12), ID_GALV, 0.95, 0.9, height=0.0)
    c.paint(x - PAD, x + w + PAD, zr(z1 - 0.10), y + h + PAD, ID_GALV, 1.0, 1.0, height=0.0)
    c.mul(x + edge, x + w - edge, zr(z1 - 0.10) - 1.0, zr(z1 - 0.10), 0.8, ao=0.8)
    l, r = x + edge, x + w - edge
    pts = [0.12 + (z1 - 0.22) * k / 9 for k in range(10)]
    for z in pts:
        c.stroke((l, zr(z)), (r, zr(z)), 2.6, ID_GALV, 1.0, 1.0, height=0.0)
    for k, (za, zb) in enumerate(zip(pts, pts[1:])):
        a, b = (l, r) if k % 2 == 0 else (r, l)
        c.stroke((a, zr(za)), (b, zr(zb)), 2.6, ID_GALV, 1.0, 1.0, height=0.0)


def paint_cable_box(c):
    """The cable end box: tank paint, a bolted lid near the top, the
    cable gland's collar at the foot."""
    x, y, w, h = CABLE_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_TANK, 1.0, 1.0, height=0.0)
    c.paint(x - PAD, x + w + PAD, y - PAD, y + m(0.12), ID_TANK_DK, 1.0, 0.9, height=0.02)
    l0 = y + m(1.30)
    for a0, a1, b0, b1 in ((x + 3, x + w - 3, l0, l0 + 2), (x + 3, x + w - 3, h + y - 6, h + y - 4),
                           (x + 3, x + 5, l0, y + h - 4), (x + w - 5, x + w - 3, l0, y + h - 4)):
        c.paint(a0, a1, b0, b1, ID_TANK, 0.84, 0.9, height=0.01)
    c.mul(x - PAD, x + w + PAD, y + m(0.12), y + m(0.12) + 2, 0.86, ao=0.84)


def paint_gravel(c):
    """A transformer plinth's top at GRAVEL_PPM: a cast concrete curb round
    a bed of crushed stone that holds spilt oil, darker toward the middle
    under the tank."""
    x, y, w, h = GRAVEL_R
    k = GRAVEL_PPM
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CONC, 0.96, 1.0, height=0.0)
    e = 0.15 * k
    c.paint(x + e, x + w - e, y + e, y + h - e, ID_GRAVEL, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x + e, x + w - e, y + e, y + h - e)
    gx = np.floor((X - x) / 1.3).astype(np.int64)
    gy = np.floor((Y - y) / 1.3).astype(np.int64)
    stone = atlas.hash_unit(gx, gy, 71)
    c.shade[sy, sx] = 0.80 + 0.36 * stone
    c.height[sy, sx] = 0.006 * stone
    c.ao[sy, sx] = 0.80 + 0.2 * stone
    # oil and dust under the tank: darker toward the plinth's middle
    dx = np.abs(X - (x + w / 2.0)) / (w / 2.0)
    dy = np.abs(Y - (y + h / 2.0)) / (h / 2.0)
    d = np.maximum(dx, dy)
    c.shade[sy, sx] *= 0.80 + 0.20 * atlas.smoothstep(0.3, 0.9, d)
    c.mul(x + e, x + w - e, y + e, y + e + 1.0, 0.80, ao=0.85)
    c.mul(x + e, x + e + 1.0, y + e, y + h - e, 0.80, ao=0.85)


def paint_fire(c):
    """The fire wall: board-marked cast concrete, the boards 0.15 m tall
    with faint joints and their grain, form-tie holes on a 0.6 m grid, a
    pour line every 1.2 m, splash at the foot. U along the face, V = z."""
    x, y, w, h = FIRE_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CONC, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    board = np.floor((Y - y) / m(0.15)).astype(np.int64)
    tone = 0.95 + 0.08 * atlas.hash_unit(board, np.floor((X - x) / m(1.2)).astype(np.int64), 61)
    joint = ((Y - y) % m(0.15)) < 0.8
    c.shade[sy, sx] = np.where(joint, 0.90, tone)
    c.height[sy, sx] = np.where(joint, -0.002, 0.0)
    pour = ((Y - y) % m(1.2)) < 1.0
    c.shade[sy, sx] = np.where(pour, c.shade[sy, sx] * 0.92, c.shade[sy, sx])
    tie = (np.abs((X - x) % m(0.6) - m(0.3)) < 1.0) & (np.abs((Y - y) % m(0.6) - m(0.3)) < 1.0)
    c.shade[sy, sx] = np.where(tie, 0.55, c.shade[sy, sx])
    c.height[sy, sx] = np.where(tie, -0.01, c.height[sy, sx])
    c.ao[sy, sx] = np.where(tie, 0.6, 1.0)
    c.mul(x - PAD, x + w + PAD, y + h - 2, y + h + PAD, 0.94)     # its top arris
    sy, sx, Y, _ = c.field(x - PAD, x + w + PAD, y - PAD, y + m(0.3))
    z = (Y - y) / PPM
    c.shade[sy, sx] *= 0.84 + 0.16 * np.clip(z / 0.25, 0.0, 1.0)


def paint_trench(c):
    """Cable trench covers: precast slabs 0.6 m long across the trench,
    joints between them, two lifting holes in each."""
    x, y, w, h = TRENCH_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CONC, 0.96, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    slab = np.floor((X - x) / m(0.6)).astype(np.int64)
    c.shade[sy, sx] = 0.92 + 0.10 * atlas.hash_unit(slab, 83)
    r = (X - x) % m(0.6)
    joint = r < 1.0
    c.shade[sy, sx] = np.where(joint, 0.62, c.shade[sy, sx])
    c.ao[sy, sx] = np.where(joint, 0.6, 1.0)
    c.height[sy, sx] = np.where(joint, -0.01, 0.0)
    hole = (np.abs(r - m(0.3)) < 1.2) & ((np.abs(Y - (y + h * 0.25)) < 1.2) |
                                          (np.abs(Y - (y + h * 0.75)) < 1.2))
    c.shade[sy, sx] = np.where(hole, 0.40, c.shade[sy, sx])
    c.mul(x - PAD, x + w + PAD, y - PAD, y + 1.0, 0.86)
    c.mul(x - PAD, x + w + PAD, y + h - 1.0, y + h + PAD, 0.86)


def paint_patches(c):
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0), "coping": (ID_CONC, 1.0, 1.0),
        "conc": (ID_CONC, 0.92, 0.92), "reveal": (ID_PLINTH, 0.80, 0.70),
        "alu": (ID_ALU, 1.0, 1.0), "tank_paint": (ID_TANK, 1.0, 1.0),
        "galv_paint": (ID_GALV, 1.0, 1.0), "porcelain": (ID_PORC, 1.0, 1.0),
        "steel_dark": (ID_TANK_DK, 1.0, 0.9), "gate": (ID_PAINT, 0.94, 0.95),
        "felt": (ID_FELT, 1.0, 1.0), "pad_top": (ID_CONC, 0.96, 1.0),
        "head": (ID_HEAD, 0.94, 1.0),
    }
    atlas.paint_patches(c, PATCHES, spec)


# ------------------------------------------------------------------ checks
def regions():
    r = {"tank": TANK_R, "gate": GATE_R, "rad": RAD_R,
         "rad_end": RAD_END_R, "cons": CONS_R_, "gravel": GRAVEL_R,
         "tank_top": TANK_TOP_R, "roof": ROOF_R, "fascia": FASCIA_R,
         "rad_top": RAD_TOP_R, "bush": BUSH_R, "string": STRING_R,
         "col_lat": COL_LAT_R, "beam_lat": BEAM_LAT_R, "beam_top": BEAM_TOP_R,
         "dis_lat": DIS_LAT_R,
         "cable": CABLE_R, "cons_end": CONS_END_R,
         "fire": FIRE_R, "trench": TRENCH_R, "breaker": BREAKER_R, "post": POST_R,
         "ct": CT_R, "pole3": POLE3_R}
    for kind, (x, y) in ITEM_ORIGIN.items():
        w, h = item_size_px(kind)
        r[kind] = (x, y, w, h)
    r.update(PATCHES)
    return r


def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands,
    run off the sheet, or are too small for what maps onto them."""
    rects = regions()
    problems = atlas.region_problems(rects, ATLAS, bands_top=BAND_IDS_ROWS["FENCE"][1])
    need = {"tank": (TANK[0], TANK_Z[1] - PLINTH[2]),
            "rad": (RAD_X, RAD_Z[1] - RAD_Z[0]), "rad_end": (RAD_D, RAD_Z[1] - RAD_Z[0]),
            "tank_top": TANK, "fascia": (HX1 - HX0, Z_TOP - Z_WALL),
            "rad_top": (RAD_X, RAD_D), "bush": (0.0, BUSH_H), "string": (0.0, STRING_LEN),
            "cable": (2 * CABLE_Y, CABLE_TOP - PLINTH[2]),
            "cons": (TANK[1], 0.0), "fire": (FIRE[1] - FIRE[0], FIRE[3]),
            "trench": (HX0 + TRENCH_W / 2 + 0.05 - TRENCH_X0, TRENCH_W),
            "breaker": (0.0, Z_BRK[3] + 0.03), "post": (0.0, POST_H + 0.02),
            "ct": (0.0, Z_CT[2] + 0.03)}
    if G_TIP * COL_LAT_PPM > COL_LAT_R[3] + 0.01:
        problems.append("the painted column overruns its region")
    if 2 * (G_COL_Y - G_SOLID[0] * g_half(G_BEAM_Z[0])) * BEAM_LAT_PPM > BEAM_LAT_R[2] + 0.01:
        problems.append("the painted truss overruns its region")
    if (DIS_DECK[2] + 0.05) * DIS_LAT_PPM > DIS_LAT_R[3] + 0.01:
        problems.append("the painted disconnector leg overruns its region")
    if (BRK_Z0 + Z_BRK[3]) * POLE3_PPM > POLE3_R[3] + 0.01:
        problems.append("the LOD3 pole overruns its region")
    for k, (wm, hm) in need.items():
        x, y, w, h = rects[k]
        if wm * PPM > w + 0.01 or hm * PPM > h + 0.01:
            problems.append("%s region %dx%d is smaller than its %.2f x %.2f m"
                            % (k, w, h, wm, hm))
    if 2 * np.pi * CONS_R * PPM > CONS_R_[3] + 0.01:
        problems.append("the conservator's girth overruns its region")
    gw = (GATE_OPEN[1] - GATE_OPEN[0] + 2 * GATE_INTO) * PPM
    if gw > GATE_R[2] or (GATE_Z[1] - GATE_Z[0]) * PPM > GATE_R[3]:
        problems.append("the gate overruns its region")
    if PLINTH[0] * GRAVEL_PPM > GRAVEL_R[2] or PLINTH[1] * GRAVEL_PPM > GRAVEL_R[3]:
        problems.append("the plinth top overruns the gravel region")
    if 5.0 * ROOF_PPM > ROOF_R[2] or 4.0 * ROOF_PPM > ROOF_R[3]:
        problems.append("the roof overruns its region")
    if H_Y0 + m(H_TOP) > BAND_IDS_ROWS["HOUSE"][1] - 1:
        problems.append("the house band runs into the fence band")
    if F_Y0 + m(Z_FENCE) + PAD > BAND_IDS_ROWS["FENCE"][1]:
        problems.append("the fence band runs off its rows")
    if Z_WALL > H_TOP:
        problems.append("the house rises above the house band")
    if (TRENCH_TURN_X + TRENCH_W / 2 - TRENCH_X0) * PPM > TRENCH_R[2] or \
            (T_Y[1] + TRENCH_W / 2 - HY1) * PPM > TRENCH_R[2]:
        problems.append("a trench overruns its region")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    Both bands' V is height from the ground, so the plinth's soil, the
    splash-back and salt bloom land the same on the house, the fire wall and
    the yard wall. The tank and its radiators gather dust on their upper
    surfaces and runs from the cover; the gravel and the plinth curbs take
    oil and dust; the gantry's zinc takes light dust only.
    """
    brick = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    steel = (ID_PAINT, ID_HW, ID_TANK, ID_TANK_DK, ID_GALV, ID_ALU, ID_FLASH,
             ID_LOUVRE, ID_PLATE, ID_HEAD)
    w = weathering.Weather(c, steel=steel)
    w.grime()
    w.fade((ID_PAINT, ID_TANK, ID_LOUVRE, ID_FLASH, ID_HEAD))
    w.wash(brick)
    # house band and fire wall
    w.plinth(0, ATLAS, H_Y0, H_Y0 + m(Z_PLINTH), (ID_PLINTH,))
    w.splash(0, ATLAS, H_Y0 + m(Z_PLINTH), BAND_IDS_ROWS["HOUSE"][1], brick)
    w.bloom(0, ATLAS, H_Y0 + m(Z_PLINTH), H_Y0 + m(1.3), brick, amount=0.10, fade=m(0.7))
    # fence band: footing, splash, coping dust and runs from under it
    w.plinth(0, ATLAS, F_Y0, F_Y0 + m(Z_FOOT_F), (ID_PLINTH,))
    w.splash(0, ATLAS, F_Y0 + m(Z_FOOT_F), F_Y0 + m(Z_COPING), brick)
    w.bloom(0, ATLAS, F_Y0 + m(Z_FOOT_F), F_Y0 + m(1.2), brick, amount=0.10, fade=m(0.6))
    cop = F_Y0 + m(Z_COPING)
    w.add("D", 0, ATLAS, cop, F_Y0 + m(Z_FENCE) + PAD,
          lambda Y, X, nz: 0.08 + 0.10 * nz("blotch"), (ID_CONC,))
    # the plant's coal fines: a grey-black film thrown up along the wall's
    # foot, fading by half a metre, and a light patchy film above it and on
    # the coping, so the wall sits back behind the plant it encloses
    w.coal(0, ATLAS, F_Y0 - PAD, F_Y0 + m(Z_FENCE) + PAD, lambda Y, X, nz: (
        WALL_COAL * np.exp(-np.clip(Y - F_Y0, 0.0, None) / m(WALL_COAL_FALL))
        * (0.65 + 0.35 * nz("blotch")) + 0.05 + 0.06 * nz("big")),
        (ID_PLINTH, ID_CONC) + brick)
    w.runs(0, ATLAS, cop - m(0.45), cop, brick, 0.12, fall=10.0)
    # the gate and the door: kicked dirt at the foot, grime at the hasp
    x, y, wd, hd = GATE_R
    w.door(gate_u(GATE_OPEN[0]), gate_u(GATE_OPEN[1]), y, y + hd, (ID_PAINT,),
           handle=((gate_u(GATE_OPEN[0]) + gate_u(GATE_OPEN[1])) / 2.0,
                   y + m(0.68 * (GATE_Z[1] - GATE_Z[0]))))
    w.add("R", x, x + wd, y, y + 10, lambda Y, X, nz: 0.10 * nz("blotch"), (ID_PAINT, ID_HW))
    x0, y0 = ITEM_ORIGIN["door"]
    rw, rh = item_size_px("door")
    cs = OPENINGS["door"][2]
    w.door(x0 + m(cs), x0 + rw - m(cs), y0, y0 + m(OPENINGS["door"][1]), (ID_PAINT, ID_HW),
           handle=(x0 + rw - m(cs) - 7, y0 + m(1.05)))
    # the louvre: dirt from the room's air on its blades
    x0, y0 = ITEM_ORIGIN["louvre"]
    rw, rh = item_size_px("louvre")
    w.runs(x0, x0 + rw, y0, y0 + rh, (ID_LOUVRE,), 0.12, fall=rh / 2.0)
    # the slab edge: runs down from the felt's edge
    x, y, wd, hd = FASCIA_R
    w.runs(x - PAD, x + wd + PAD, y - PAD, y + hd - 3, (ID_CONC,), 0.16, fall=8.0,
           noise="short")
    # the roof: dirt pooled round the outlet and along the laps
    x, y, wd, hd = ROOF_R
    w.add("D", x, x + wd, y, y + hd, lambda Y, X, nz: 0.10 * nz("big"), (ID_FELT,))
    # the tank: dust on the cover, runs down the sides from the flange,
    # a little rust at the base frame and on the radiators' lower headers
    x, y, wd, hd = TANK_R
    top = y + m(TANK_Z[1] - PLINTH[2])
    w.runs(x - PAD, x + wd + PAD, y, top - m(0.10), (ID_TANK,), 0.10, fall=40.0)
    w.splash(x - PAD, x + wd + PAD, y + m(0.12), y + m(0.8), (ID_TANK,), amount=0.12)
    w.add("R", x - PAD, x + wd + PAD, y - PAD, y + m(0.14),
          lambda Y, X, nz: 0.12 * nz("blotch"), (ID_TANK_DK,))
    x, y, wd, hd = TANK_TOP_R
    w.add("D", x - PAD, x + wd + PAD, y - PAD, y + hd + PAD,
          lambda Y, X, nz: 0.12 + 0.10 * nz("blotch"), (ID_TANK,))
    x, y, wd, hd = RAD_R
    w.add("R", x - PAD, x + wd + PAD, y - PAD, y + 8, lambda Y, X, nz: 0.12 * nz("blotch"),
          (ID_TANK, ID_TANK_DK))
    w.runs(x - PAD, x + wd + PAD, y, y + hd, (ID_TANK,), 0.06, fall=30.0)
    for r in (RAD_TOP_R, CONS_R_, CABLE_R):
        x, y, wd, hd = r
        w.add("D", x - PAD, x + wd + PAD, y - PAD, y + hd + PAD,
              lambda Y, X, nz: 0.06 + 0.06 * nz("blotch"), (ID_TANK, ID_TANK_DK))
    # porcelain stays nearly clean (rain washes the glaze); a little dust
    # under the sheds
    for r in (BUSH_R, BREAKER_R, POST_R, CT_R):
        x, y, wd, hd = r
        w.add("D", x - PAD, x + wd + PAD, y - PAD, y + hd + PAD,
              lambda Y, X, nz: 0.03 * nz("blotch"), (ID_PORC,))
    # the breakers' cast heads and the current transformers' oil heads:
    # dust on the heads, a little oil and rust at the flanges
    for r in (BREAKER_R, CT_R):
        x, y, wd, hd = r
        w.add("D", x - PAD, x + wd + PAD, y - PAD, y + hd + PAD,
              lambda Y, X, nz: 0.06 + 0.06 * nz("blotch"), (ID_HEAD, ID_TANK, ID_TANK_DK))
    w.runs(BREAKER_R[0] - PAD, BREAKER_R[0] + BREAKER_R[2] + PAD, BREAKER_R[1] + m(Z_BRK[0]),
           BREAKER_R[1] + m(Z_BRK[1]), (ID_HEAD,), 0.10, fall=12.0)
    # the gravel bed and curb: dust and oil
    x, y, wd, hd = GRAVEL_R
    w.add("D", x - PAD, x + wd + PAD, y - PAD, y + hd + PAD,
          lambda Y, X, nz: 0.10 + 0.14 * nz("blotch"), (ID_GRAVEL, ID_CONC))
    # the fire wall: soil and splash at its foot, runs from its top, a
    # little salt; the trench covers: dust and tyre dirt
    x, y, wd, hd = FIRE_R
    w.splash(x - PAD, x + wd + PAD, y, y + m(1.0), (ID_CONC,), amount=0.18)
    w.runs(x - PAD, x + wd + PAD, y + hd - m(0.8), y + hd, (ID_CONC,), 0.14, fall=14.0)
    w.bloom(x - PAD, x + wd + PAD, y, y + m(0.9), (ID_CONC,), amount=0.06, fade=m(0.5))
    x, y, wd, hd = TRENCH_R
    w.add("D", x - PAD, x + wd + PAD, y - PAD, y + hd + PAD,
          lambda Y, X, nz: 0.12 + 0.12 * nz("blotch"), (ID_CONC,))
    # galvanised steel: light dust, on the patch the lattice's bars take
    # and on the slim gantry's painted members
    for x, y, wd, hd in (PATCHES["galv_paint"], COL_LAT_R, BEAM_LAT_R, BEAM_TOP_R,
                         DIS_LAT_R):
        w.add("D", x - PAD, x + wd + PAD, y - PAD, y + hd + PAD,
              lambda Y, X, nz: 0.04 + 0.05 * nz("big"), (ID_GALV,))
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_house_band(c)
    paint_house_fittings(c)
    paint_fence_band(c)
    c.check_bands(BAND_IDS)
    paint_gate(c)
    paint_door(c)
    paint_louvre(c)
    paint_fascia(c)
    paint_roof(c)
    paint_tank(c)
    paint_tank_top(c)
    paint_radiator(c)
    paint_radiator_end(c)
    paint_radiator_top(c)
    paint_conservator(c)
    paint_bushing(c)
    paint_breaker(c)
    paint_post(c)
    paint_ct(c)
    paint_pole3(c)
    paint_string(c)
    paint_lattice(c)
    paint_dis_leg(c)
    paint_cable_box(c)
    paint_gravel(c)
    paint_fire(c)
    paint_trench(c)
    paint_patches(c)

    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH))
    streak = atlas.noise(c, 7, 0.8, 40.0)
    c.shade[walls] *= 1.0 + 0.03 * streak[walls]
    sheet = np.isin(c.mid, (ID_PAINT, ID_TANK, ID_LOUVRE, ID_HEAD))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    c.shade[sheet] *= 1.0 + 0.016 * grain[sheet]
    galv = c.mid == ID_GALV
    spangle = atlas.noise(c, 11, 3.0)
    c.shade[galv] *= 1.0 + 0.05 * spangle[galv]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_CONC, ID_MORTAR))
    pores = atlas.noise(c, 9, 0.8)
    c.shade[mineral] *= 1.0 + 0.03 * pores[mineral]
    c.height[mineral] += 0.0006 * pores[mineral]
    felt = c.mid == ID_FELT
    c.shade[felt] *= 1.0 + 0.05 * atlas.noise(c, 12, 2.0)[felt]
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
    t[ID_PAINT] = pal["paint"]
    return t


def export(out_dir, ss=atlas.SS):
    """Albedo per variant, one ORM and one normal map. No emission map: the
    yard has no glazing."""
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.010)
    c.weather.dust(cav, (ID_BRICK, ID_BRICK2, ID_MORTAR))
    rough = 0.04 * atlas.noise(c, 13, 20.0)
    path = os.path.join(out_dir, ASSET)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c), path + "_normal.png")]
    for v in VARIANTS:
        rgb = atlas.albedo(c, lut(v), grime=0.25 * cav)
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
