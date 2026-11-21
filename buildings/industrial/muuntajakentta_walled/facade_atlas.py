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
    y  252 ..  384   FENCE   z 0 .. 2.00 m: concrete footing, the yard wall's
                             brick, its concrete coping
    y  390 .. 1024   unique  tank, radiator, conservator, bushing and
                             insulator regions, the gate, the door, the
                             louvre, a pier face, the gravel bed on the
                             plinths, the roof, the slab edge, the gantry's
                             galvanised steel and flat patches

Rasterising is scripts/atlas.py's; dirt, algae, rust and faded paint are
scripts/weathering.py's fields, placed by weather() below.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import weathering  # noqa: E402

ASSET = "muuntajakentta_walled"
ATLAS = 1024
PPM = 64.0
PAD = 2                 # rows each band paints beyond its own edge

# ------------------------------------------------------------------ plan
# Metres, Blender frame, front toward -Y, origin at the compound's centre.
# The yard wall's brick piers stand on the compound's outline; their outer
# faces are the asset's plan bounds, 16.0 x 12.0 m.
FX, FY = 8.0, 6.0               # the piers' outer faces
PIER_W = 0.36                   # a brick pier, square (one and a half bricks)
WALL_T = 0.24                   # the wall between them (one brick)
WCX, WCY = FX - PIER_W / 2.0, FY - PIER_W / 2.0      # wall centre lines
Z_FENCE = 2.0                   # wall top, coping included
Z_PIER = 2.2                    # pier top, cap included
Z_FOOT_F = 0.3125               # the wall's concrete footing (20 px)
Z_COPING = Z_FENCE - 6.0 / PPM  # the coping's foot, 1.906 m
Z_CAP = Z_PIER - 6.0 / PPM      # the pier cap's foot

# The gate: an opening in the front wall between two piers, closed by a
# sheet-steel double gate set back in the wall's thickness.
GATE_OPEN = (-0.80, 2.62)       # x of the two piers' inner faces
GATE_Y = (-WCY - 0.04, -WCY + 0.02)   # the leaves' 0.06 m thickness
GATE_Z = (0.04, 2.04)
GATE_INTO = 0.05                # the leaves' box runs this far into the piers

# The switchgear house: in the compound's front-east corner, its front and
# east walls in the yard wall's outer planes, so the wall stops on it.
HX1 = WCX + WALL_T / 2.0        # 7.94, the east wall line
HX0 = HX1 - 5.0
HY0 = -(WCY + WALL_T / 2.0)     # -5.94, the front wall line
HY1 = HY0 + 4.0
H_WALL_T = 0.24                 # the house's own walls (for the floor area)
Z_WALL = 3.20                   # brick to the roof slab
Z_TOP = 3.45                    # the flat slab's top, flush with the walls
Z_PLINTH = 0.375                # 24 px; the house's concrete plinth

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

# The gantry: a portal of H-section steel on the west side, its beam along
# Y, with a suspension string over each phase and a rigid tubular bus down
# to each bushing.
G_X = -6.5
G_COL_Y = 4.6
G_H = 0.30                      # H-section depth and width
G_TF, G_TW = 0.03, 0.02         # flange and web thickness
G_TOP = 7.45                    # column tops
G_BEAM_Z = (7.00, 7.30)
G_BEAM_W = 0.24
G_BEAM_Y = 4.90
G_PAD = (0.70, 0.30)            # concrete foundation pad: side, height
STRING_LEN = 0.85               # top hardware to the bottom clamp
BUS_R = 0.03                    # the tubular bus's radius

# ------------------------------------------------------------------ openings
# kind -> (width, height, casing side, casing bottom, casing top), metres.
OPENINGS = {
    "door": (1.00, 2.10, 0.0625, 0.0, 0.0625),
    "louvre": (0.875, 0.50, 0.0625, 0.0625, 0.0625),
}
REVEAL_DEPTH = {"door": 0.12, "louvre": 0.10}
Z_LOUVRE_HI = 2.30              # high louvres' sill
Z_LOUVRE_LO = 0.55              # low louvre's sill

# ------------------------------------------------------------------- bands
H_Y0 = 2.0                      # v of z = 0 on the house band
H_TOP = 3.80                    # the band reaches the fire wall's top
F_Y0 = 254.0                    # v of z = 0 on the fence band
BAND_IDS_ROWS = {"HOUSE": (0, 248), "FENCE": (252, 384)}

COURSE = 0.078125               # brick course pitch: 5 px
BRICK_L = 0.25                  # stretcher: 16 px, 64 bricks per atlas width
TONE_COURSES = 48

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels. check_regions() asserts they neither overlap nor
# run off the sheet.
UNI_Y = 390
TANK_R = (4, UNI_Y, 168, 168)            # tank side: U along, V = z - plinth top
GATE_R = (180, UNI_Y, 226, 130)          # the gate's face, 3.52 x 2.0 m
PIER_R = (494, UNI_Y, 24, 142)           # a pier face, 0.36 x 2.2 m
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
GALV_R = (664, 592, 40, 128)             # gantry steel: U across, V stretched
CABLE_R = (712, 592, 60, 142)
CONS_END_R = (780, 592, 40, 40)
FIRE_R = (256, 770, 232, 246)            # the fire wall's face, board-marked
TRENCH_R = (500, 770, 336, 40)           # trench covers: U along, V across

ITEM_ORIGIN = {"door": (414.0, float(UNI_Y)), "louvre": (488.0, 592.0)}

PATCH_NAMES = ("blank", "coping", "conc", "reveal", "alu", "tank_paint", "galv_paint",
               "porcelain", "steel_dark", "gate", "felt", "pad_top")
PATCHES = {n: (4 + 20 * i, 740, 12, 12) for i, n in enumerate(PATCH_NAMES)}

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_CONC, ID_PAINT, ID_HW, ID_SIGN_Y, ID_SIGN_K = 5, 6, 7, 8, 9
ID_TANK, ID_TANK_DK, ID_GALV, ID_PORC, ID_ALU = 10, 11, 12, 13, 14
ID_GRAVEL, ID_FELT, ID_FLASH, ID_DARK, ID_LOUVRE = 15, 16, 17, 18, 19
ID_PLATE = 20

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
}

# ---------------------------------------------------------------- palettes
# The plant's brick, as nostokonehuone_brick and the hall: the house, the
# wall and the fire wall change with it, and the painted steel of the gate
# and the door moves with the brick. The electrical plant is the same in
# every variant: grey-green tank paint, galvanised gantry, brown porcelain.
VARIANTS = {
    "red_brick": {"brick": (144, 72, 52), "brick2": (114, 58, 45),
                  "mortar": (150, 145, 136), "paint": (66, 82, 76)},
    "yellow_brick": {"brick": (188, 166, 122), "brick2": (164, 142, 104),
                     "mortar": (160, 156, 148), "paint": (104, 56, 44)},
    "brown_brick": {"brick": (98, 68, 54), "brick2": (78, 54, 44),
                    "mortar": (124, 118, 110), "paint": (60, 68, 76)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_BLANK: (52, 52, 52), ID_PLINTH: (150, 148, 142), ID_CONC: (166, 164, 156),
    ID_HW: (120, 120, 118), ID_SIGN_Y: (196, 160, 54), ID_SIGN_K: (30, 30, 30),
    ID_TANK: (104, 114, 104), ID_TANK_DK: (70, 76, 70), ID_GALV: (134, 137, 137),
    ID_PORC: (98, 54, 36), ID_ALU: (150, 152, 150), ID_GRAVEL: (128, 124, 116),
    ID_FELT: (56, 56, 58), ID_FLASH: (96, 98, 100), ID_DARK: (26, 26, 26),
    ID_LOUVRE: (112, 114, 110), ID_PLATE: (170, 170, 166),
}

BAND_IDS = {
    "HOUSE": (BAND_IDS_ROWS["HOUSE"], {ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR}),
    "FENCE": (BAND_IDS_ROWS["FENCE"], {ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR,
                                       ID_CONC}),
}

# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto: only the
# few centimetres the mesh does not model.
BRICK_FACE = 0.006
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
    y0, top = y_z0 + m(z_from), y_z0 + m(z_to)
    course, blen = m(COURSE), m(BRICK_L)
    c.paint(x0, x1, y0, top, ID_BRICK, 1.0, 1.0)
    sy, sx, Y, X = c.field(x0, x1, y0, top)
    r = np.floor((Y - y0) / course).astype(np.int64)
    off = (r % 2) * blen * 0.5
    b = np.floor((X - off) / blen).astype(np.int64) % int(ATLAS / blen)
    rr = r % TONE_COURSES
    bed = (Y - y0 - r * course) < 1.0
    perp = ((X - off) % blen) < 1.0
    joint = bed | perp
    tone = 0.90 + 0.20 * atlas.hash_unit(b, rr, seed)
    dark = atlas.hash_unit(b, rr, seed + 12) < 0.17
    c.mid[sy, sx] = np.where(joint, ID_MORTAR, np.where(dark, ID_BRICK2, ID_BRICK))
    c.shade[sy, sx] = np.where(joint, 0.94, tone)
    c.ao[sy, sx] = np.where(joint, 0.80, 1.0)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)


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
def paint_pier(c):
    """A pier face, 0.36 m across, the wall's footing and brick run on up
    to the precast cap."""
    x, y, w, h = PIER_R
    paint_brick(c, x - PAD, x + w + PAD, y, Z_FOOT_F, Z_CAP, seed=53)
    paint_footing(c, x - PAD, x + w + PAD, y, Z_FOOT_F)
    paint_coping(c, x - PAD, x + w + PAD, y + m(Z_CAP), y + m(Z_PIER) + PAD, axes="xy")
    # the pier's arrises: a touch lighter brick at its edges, a shadow line
    # where the wall runs into it is the mesh's
    c.mul(x, x + 1, y + m(Z_FOOT_F), y + m(Z_CAP), 0.94)
    c.mul(x + w - 1, x + w, y + m(Z_FOOT_F), y + m(Z_CAP), 0.94)


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
    top = y + m(GATE_Z[1] - GATE_Z[0])
    for a0, a1, hinge in ((l0, mid - 0.6, l0), (mid + 0.6, l1, l1)):
        sy, sx, _, X = c.field(a0, a1, y, top)
        r = (X - a0) % m(0.15)
        c.height[sy, sx] = np.where(r < 3.0, RIB_H * np.sin(np.pi * np.clip(r / 3.0, 0, 1)), 0.0)
        c.shade[sy, sx] = np.where((r >= 3.0) & (r < 4.0), 0.92, 1.0)
        for b0, b1 in ((y, y + F), (y + m(0.95), y + m(0.95) + F), (top - F, top)):
            _bar(c, a0, a1, b0, b1, ID_PAINT, FRAME_H, 1.0, 0.9, "y")
            c.mul(a0, a1, b0 - 2, b0, 0.88, ao=0.84)
        _bar(c, a0, a0 + F, y, top, ID_PAINT, FRAME_H, 1.0, 0.9, "x")
        _bar(c, a1 - F, a1, y, top, ID_PAINT, FRAME_H, 1.0, 0.9, "x")
        for zz in (0.30, 1.65):
            hy = y + m(zz)
            hx0 = hinge - 2 if hinge == l0 else hinge - 12
            c.paint(hx0, hx0 + 14, hy - 3, hy + 3, ID_HW, 0.80, 0.86, height=0.040)
            c.mul(hx0, hx0 + 14, hy - 5, hy - 3, 0.82, ao=0.8)
    # meeting stiles, drop bolt, hasp and padlock
    c.paint(mid - 0.6, mid + 0.6, y, top, ID_DARK, 1.0, 0.5, height=-0.004)
    c.paint(mid + 2, mid + 4, y + 2, y + m(0.55), ID_HW, 0.85, 0.85, height=0.03)
    c.paint(mid - 7, mid + 7, y + m(1.10), y + m(1.16), ID_HW, 0.9, 0.85, height=0.035)
    c.paint(mid - 3, mid + 1, y + m(1.02), y + m(1.10), ID_DARK, 1.0, 0.8, height=0.045)
    # the warning plate, 0.42 m, at eye height on the left leaf
    paint_warning(c, (l0 + mid) / 2.0, y + m(1.45), m(0.42))
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


def paint_galv(c):
    """Hot-dip galvanised steel: spangle mottling, nothing that would show
    stretched along V."""
    x, y, w, h = GALV_R
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_GALV, 1.0, 1.0, height=0.0)


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
    }
    for name, (mid, sh, ao) in spec.items():
        x, y, w, h = PATCHES[name]
        c.paint(x - 2, x + w + 2, y - 2, y + h + 2, mid, sh, ao, height=0.0)


# ------------------------------------------------------------------ checks
def regions():
    r = {"tank": TANK_R, "gate": GATE_R, "pier": PIER_R, "rad": RAD_R,
         "rad_end": RAD_END_R, "cons": CONS_R_, "gravel": GRAVEL_R,
         "tank_top": TANK_TOP_R, "roof": ROOF_R, "fascia": FASCIA_R,
         "rad_top": RAD_TOP_R, "bush": BUSH_R, "string": STRING_R,
         "galv": GALV_R, "cable": CABLE_R, "cons_end": CONS_END_R,
         "fire": FIRE_R, "trench": TRENCH_R}
    for kind, (x, y) in ITEM_ORIGIN.items():
        w, h = item_size_px(kind)
        r[kind] = (x, y, w, h)
    r.update(PATCHES)
    return r


def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands,
    run off the sheet, or are too small for what maps onto them."""
    rects = regions()
    names = sorted(rects)
    problems = []
    for i, a in enumerate(names):
        ax, ay, aw, ah = rects[a]
        if ax - 2 < 0 or ay - 2 < 0 or ax + aw + 2 > ATLAS or ay + ah + 2 > ATLAS:
            problems.append("%s runs off the atlas" % a)
        if ay - 4 < BAND_IDS_ROWS["FENCE"][1]:
            problems.append("%s overlaps the tiling bands" % a)
        for b in names[i + 1:]:
            bx, by, bw, bh = rects[b]
            if (ax - 4 < bx + bw and bx - 4 < ax + aw
                    and ay - 4 < by + bh and by - 4 < ay + ah):
                problems.append("%s and %s overlap" % (a, b))
    need = {"tank": (TANK[0], TANK_Z[1] - PLINTH[2]), "pier": (PIER_W, Z_PIER),
            "rad": (RAD_X, RAD_Z[1] - RAD_Z[0]), "rad_end": (RAD_D, RAD_Z[1] - RAD_Z[0]),
            "tank_top": TANK, "fascia": (HX1 - HX0, Z_TOP - Z_WALL),
            "rad_top": (RAD_X, RAD_D), "bush": (0.0, BUSH_H), "string": (0.0, STRING_LEN),
            "cable": (2 * CABLE_Y, CABLE_TOP - PLINTH[2]),
            "cons": (TANK[1], 0.0), "fire": (FIRE[1] - FIRE[0], FIRE[3]),
            "trench": (HX0 + TRENCH_W / 2 + 0.05 - TRENCH_X0, TRENCH_W)}
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
             ID_LOUVRE, ID_PLATE)
    w = weathering.Weather(c, steel=steel)
    w.grime()
    w.fade((ID_PAINT, ID_TANK, ID_LOUVRE, ID_FLASH))
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
    w.runs(0, ATLAS, cop - m(0.45), cop, brick, 0.12, fall=10.0)
    # piers: as the wall
    x, y, wd, hd = PIER_R
    w.plinth(x - PAD, x + wd + PAD, y, y + m(Z_FOOT_F), (ID_PLINTH,))
    w.splash(x - PAD, x + wd + PAD, y + m(Z_FOOT_F), y + m(Z_CAP), brick)
    w.runs(x - PAD, x + wd + PAD, y + m(Z_CAP) - m(0.45), y + m(Z_CAP), brick, 0.12, fall=10.0)
    w.add("D", x - PAD, x + wd + PAD, y + m(Z_CAP), y + hd + PAD,
          lambda Y, X, nz: 0.08 + 0.10 * nz("blotch"), (ID_CONC,))
    # the gate and the door: kicked dirt at the foot, grime at the hasp
    x, y, wd, hd = GATE_R
    w.door(gate_u(GATE_OPEN[0]), gate_u(GATE_OPEN[1]), y, y + hd, (ID_PAINT,),
           handle=((gate_u(GATE_OPEN[0]) + gate_u(GATE_OPEN[1])) / 2.0, y + m(1.1)))
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
    x, y, wd, hd = BUSH_R
    w.add("D", x - PAD, x + wd + PAD, y - PAD, y + hd + PAD,
          lambda Y, X, nz: 0.03 * nz("blotch"), (ID_PORC,))
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
    # galvanised steel: light dust
    x, y, wd, hd = GALV_R
    w.add("D", x - PAD, x + wd + PAD, y - PAD, y + hd + PAD,
          lambda Y, X, nz: 0.04 + 0.05 * nz("big"), (ID_GALV,))
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_house_band(c)
    paint_fence_band(c)
    c.check_bands(BAND_IDS)
    paint_pier(c)
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
    paint_string(c)
    paint_galv(c)
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
    sheet = np.isin(c.mid, (ID_PAINT, ID_TANK, ID_LOUVRE))
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
