# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas for rivitalo_two_storey, and the
layout build.py maps into.

This describes one asset and nothing else, so it lives beside build.py rather
than in scripts/. It is also the single source of the numbers the two files
share: build.py imports the z-levels, opening sizes and region rects from here
instead of writing them a second time, so the pixel layout and the UVs cannot
drift apart. Importing this module only defines those constants; the painting
runs when paint() is called. Rasterising is scripts/atlas.py's: a canvas
supersampled SS x SS per pixel, with a height channel the normal map is
derived from (numpy and scipy; Pillow to save).

    python3 facade_atlas.py export      # writes every map into ./export

The atlas is a trim sheet rather than one picture per elevation. This row of
four dwellings is 24 m long, and painting even one elevation at the catalog's
64 px/m would need 1536 px, so the walls sample tiling bands and every opening
samples a region of its own:

    y    0 ..  236   S1      ground storey, z 0 .. 3.65: plinth, board cladding
    y  238 ..  548   S2      upper storey, z 3.35 .. 8.13: storey band, cladding
    y  550 ..  664   ROOF    profiled sheet, V stretched up the shallow slope
    y  668 ..  692   FASCIA  eave fascia with its gutter
    y  696 ..  827   YARD    rendered block screen wall of the back yards
    y  832 .. 1022   unique  doors, windows, yard gate, the entrance shed's
                             boarding, the LOD3 painted elevations, patches

S1, S2, ROOF, FASCIA and YARD span the full width and tile in U. Every
opening's region carries its casing as well as its glazing, because the casing
is the one part of a window a tiling cladding band cannot place. build.py cuts
a ring of faces round each opening for it to land on.

The cladding is vertical boarding on a 0.5 m pitch, which is what the type
wears and what the 6.0 m dwelling module is a whole number of. Board tone and
joints therefore repeat exactly every 1024 px, so a wall whose U crosses the
atlas wrap sees a board continue rather than change tone with no joint to
explain it.

Painting produces a material-id map, a shade multiplier, an AO map and a
height map once; each variant is those coloured by its own palette, so the
variants cannot differ in anything but colour. Relief that should answer the
sun is height, and reaches the renderer through the normal map; shade only
carries tone, wear and occlusion, which do not depend on where the sun is.
Dirt, algae, rust and faded paint are scripts/weathering.py's fields: weather()
below says where they go on this layout, and each variant resolves them
against its own colours.
"""

import os
import sys

import numpy as np

# Windows are painted the same way across the whole catalog, and every atlas is
# rasterised the same way, so both live in scripts/ and not here; see
# CLAUDE.md's Style Direction and Texture Requirements.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "rivitalo_two_storey"
ATLAS = 1024
PPM = 64.0

# --------------------------------------------------------- vertical layout
# Metres above ground, shared by every wall so storey lines agree all round.
Z_FLOOR = 0.35       # plinth top = ground-floor level; door thresholds
Z_FLASH = 0.35       # cladding and the S1 board run start here
Z_STOREY = 3.35      # upper floor: the horizontal panel seam on every wall
Z_EAVE = 6.35        # walls meet the soffit
Z_WALL_TOP = 6.50    # walls run on up into the roof slab, which trims them
BAND_H = 0.1875      # storey seam board across every wall at Z_STOREY (12 px)
BOARD = 0.5          # vertical board pitch (32 px); 1024/32 = 32 boards
S1_TOP = 3.65        # S1 band reaches this high above ground
S2_TOP = 8.13        # S2 band top; build.py asserts the gable apex fits

# ------------------------------------------------------------- openings
# kind -> (width, height, casing side, casing bottom, casing top), metres.
# Casing is painted, never modelled: at 20-40 mm proud it fails the 0.25 m
# test by an order of magnitude. Doors have no bottom casing — the leaf
# runs down to the threshold. The front door's "casing" is the wide board
# surround the type sets its entrance in, stained a contrasting colour.
OPENINGS = {
    "door_front": (0.95, 2.10, 0.15, 0.0, 0.1875),
    "door_shed": (0.85, 1.95, 0.09, 0.0, 0.06),
    "door_patio": (1.00, 2.10, 0.125, 0.0, 0.1875),
    "wide": (1.80, 1.50, 0.125, 0.125, 0.1875),
    "std": (1.20, 1.30, 0.125, 0.125, 0.1875),
    "small": (0.50, 0.70, 0.125, 0.125, 0.1875),
    "gate": (1.00, 1.55, 0.06, 0.0, 0.06),
}
# Recess from the wall face to the glass or leaf. A boarded timber wall sets
# its windows near the outside face, so this is shallower than the masonry
# reveals the 0.25 m test was written around; see notes.md.
REVEAL_DEPTH = {"door_shed": 0.08}   # a store door is nearly flush with its boarding
REVEAL_DEFAULT = 0.15

# ------------------------------------------------------------ atlas bands
S1_Y0 = 2.0          # v of z = 0
S2_Y0 = 240.0        # v of z = Z_STOREY
ROOF_Y0, ROOF_H = 552.0, 110.0
# Main roof slope, fascia top to ridge, in metres. The roof band stretches
# this over ROOF_H rows; build.py asserts it against the massing.
ROOF_SLOPE_LEN = 4.742
FASC_Y0 = 670.0      # v of the fascia's bottom edge
FASC_H = 20.0        # = the roof slab's 0.3125 m vertical thickness
GUTTER_PX = 9.0      # the gutter's rows, hung across the fascia's top
# The downpipes' sides span the middle five of them (scripts/downpipes.py)
PIPE_STRIP = (FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 - 2.5,
              FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 + 2.5)
YARD_Y0 = 698.0      # v of z = 0 on a back-yard screen wall
YARD_H = 1.90        # screen wall height; the band carries 1.95 m
UNI_Y0 = 832.0

# Region origins: the bottom-left of each opening's casing, in pixels.
ITEM_ORIGIN = {
    "door_front": (4.0, UNI_Y0),
    "door_shed": (92.0, UNI_Y0),
    "door_patio": (166.0, UNI_Y0),
    "wide": (254.0, UNI_Y0),
    "std": (393.0, UNI_Y0),
    "small": (494.0, UNI_Y0),
    "gate": (550.0, UNI_Y0),
}
# The entrance shed's stained boarding: a strip mapped from the face's own
# along-coordinate and from world z, so the boards stand upright on its front
# and on both returns. 2.0 m wide by SHED_V m tall covers every face it has.
SHED = (630.0, UNI_Y0, 128.0, 188.0)
SHED_V = 188.0 / PPM
PATCHES = {name: (772.0 + 16.0 * i, UNI_Y0, 8.0, 8.0) for i, name in enumerate(
    ("trim", "soffit", "reveal", "blank", "tread", "cap", "barge", "render",
     "flue"))}

# ---------------------------------------------------- LOD3 painted elevations
# At LOD3 the front and rear walls are not cut at all: each dwelling bay is one
# quad mapped to a painted elevation of that bay, and the entrance shed's front
# is one quad mapped to a painted elevation of its own. Cutting them instead
# cost more than the rest of the tier put together — a wall region has to be
# retriangulated round every hole — and the triangles it freed are what let
# every yard dividing wall, every gate and every canopy survive to the last
# tier. This is CLAUDE.md's "flatten geometry into suitable shared-atlas
# regions", and it is why LOD3 still reads as six separate dwellings.
#
# 14 px/m is ample here: at the tier's 120 m a 6 m bay is about 58 px on
# screen, and the region is 84.
PPM3 = 14.0
BAY_W, BAY_H = 6.00, 6.50        # one bay; build.py asserts both against it
LOD3_FRONT = (896.0, UNI_Y0, BAY_W * PPM3, BAY_H * PPM3)
LOD3_REAR = (896.0, UNI_Y0 + BAY_H * PPM3 + 6.0, BAY_W * PPM3, BAY_H * PPM3)
LOD3_SHED = (988.0, UNI_Y0, 21.0, 41.0)
SHED_FACE_W = 1.50               # the entrance shed's width; build.py asserts it

# ------------------------------------------------------------- elevations
# Which openings sit where in one dwelling bay, as (kind, s along the bay,
# sill z). build.py cuts these at LOD0-LOD2 and paints them into the bay
# regions above at LOD3, so both files must read them from one place or a
# window would move across the LOD2/LOD3 switch.
GF_SILL, UP_SILL, SMALL_SILL = 0.95, 4.20, 4.75
DOOR_S, SHED_S = 3.30, 4.95      # the front door and the shed's centre
# Upstairs, two bedroom windows on a 3 m rhythm, so the row's upper storey
# reads as one even run of large windows across every dwelling.
FRONT_UNIT = [
    ("wide", 1.50, GF_SILL),
    ("door_front", DOOR_S, Z_FLOOR),
    ("wide", 1.50, UP_SILL),
    ("wide", 4.50, UP_SILL),
]
REAR_UNIT = [
    ("door_patio", 1.30, Z_FLOOR),
    ("wide", 3.60, GF_SILL),
    ("wide", 1.60, UP_SILL),
    ("std", 3.80, UP_SILL),
    ("small", 5.20, SMALL_SILL),
]
END_WALL = []           # both end gables are blank


def item_size_px(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    return (w + 2.0 * cs) * PPM, (h + cb + ct) * PPM


# ----------------------------------------------------------- material ids
ID_WALL, ID_TRIM, ID_SASH, ID_GLASS, ID_PLINTH, ID_METAL = 0, 1, 2, 3, 4, 5
ID_ROOF, ID_DOOR, ID_ENTRY, ID_BAND, ID_CAP, ID_BLANK, ID_HANDLE = (
    6, 7, 8, 9, 10, 11, 12)
ID_RENDER, ID_GATE = 13, 14
# (roughness, metallic). Painted steel stays mostly dielectric — the paint is
# what the light sees — but gets a little metallic so it separates from the
# timber beside it.
SURFACE = {
    ID_WALL: (0.76, 0.0), ID_TRIM: (0.56, 0.0), ID_SASH: (0.50, 0.0),
    ID_GLASS: (0.08, 0.0), ID_PLINTH: (0.90, 0.0), ID_METAL: (0.40, 0.30),
    ID_ROOF: (0.44, 0.25), ID_DOOR: (0.52, 0.0), ID_ENTRY: (0.68, 0.0),
    ID_BAND: (0.58, 0.0), ID_CAP: (0.48, 0.35), ID_BLANK: (0.95, 0.0),
    ID_HANDLE: (0.35, 0.80), ID_RENDER: (0.88, 0.0), ID_GATE: (0.72, 0.0),
}

# ---------------------------------------------------------------- palettes
# Muted Finnish suburban paints. Yellow is the default: the pale ochre body
# with dark red window casings and red entrance boarding that the type is
# usually seen in. Colour only — each variant is the same set of ids and
# shading. Casings, the fascia/storey band, roof and door vary with the body
# colour the way they would on a real street; glass, plinth, the yards'
# rendered walls and their timber gates never do.
VARIANTS = {
    "yellow": {"wall": (216, 200, 148), "trim": (128, 52, 46),
               "band": (222, 218, 206), "roof": (62, 66, 70),
               "door": (158, 60, 48), "entry": (140, 50, 42)},
    "green": {"wall": (146, 156, 124), "trim": (72, 78, 68),
              "band": (224, 221, 210), "roof": (62, 64, 66),
              "door": (128, 52, 44), "entry": (96, 74, 56)},
    "white": {"wall": (226, 223, 214), "trim": (96, 78, 62),
              "band": (206, 202, 192), "roof": (70, 64, 60),
              "door": (132, 58, 48), "entry": (98, 72, 54)},
    "brown": {"wall": (136, 106, 78), "trim": (220, 215, 202),
              "band": (224, 220, 208), "roof": (56, 54, 52),
              "door": (78, 68, 58), "entry": (92, 72, 56)},
    "red": {"wall": (140, 68, 54), "trim": (222, 219, 208),
            "band": (226, 223, 212), "roof": (60, 62, 64),
            "door": (74, 82, 68), "entry": (96, 74, 56)},
}
DEFAULT_VARIANT = "yellow"
# Opaque glass, calibrated darker than the catalog's first houses. Those are
# small-windowed timber houses; this row is largely glazed, and at their pale
# value the openings read as white panels in direct sun rather than as glass.
# Neutral and low-saturation either way, with the separation carried by
# roughness in the ORM; nothing is reflected into the albedo.
FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (146, 144, 138),
    ID_CAP: (64, 66, 68), ID_BLANK: (52, 52, 52), ID_HANDLE: (150, 146, 138),
    ID_RENDER: (196, 192, 182), ID_GATE: (92, 78, 62),
}

# Which ids each tiling band may contain. A stray pixel in a band is not a
# local blemish: every surface sampling that band repeats it.
BAND_IDS = {
    "S1": ((0, 236), {ID_PLINTH, ID_WALL}),
    "S2": ((238, 548), {ID_BAND, ID_WALL}),
    "ROOF": ((550, 664), {ID_ROOF}),
    "FASCIA": ((668, 692), {ID_METAL, ID_BAND}),
    "YARD": ((696, 827), {ID_RENDER, ID_CAP}),
}


# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto. The mesh
# already models every recess over 0.25 m; these are the few centimetres of
# board and sheet that only a normal map can show. The LOD3 bay elevations are
# painted at PPM3, not PPM, and seen only beyond ~120 m, so they stay flat.
CLAD_H = 0.015       # boarding, proud of the concrete plinth below it
JOINT_D = 0.006      # the V-joint between boards
BAND_RELIEF = 0.028  # storey band and fascia boards
CASING_H = 0.020     # window and door casings, proud of the wall
SILL_H = 0.035       # sill boards
SASH_H = 0.012       # sash frames, proud of the glass
RIB_H = 0.030        # the roof sheet's trapezoid ribs
STEP_H = 0.010       # the sheet's transverse steps
GUTTER_R = 0.070     # half-round gutter's radius
COPING_H = 0.030     # the yard wall's sheet-metal coping


# ============================================================ painting
def m(v):
    """Metres -> pixels."""
    return v * PPM


def paint_boarding(c, y_lo, y_hi, seed):
    """Vertical board cladding across the full width, boards BOARD wide.

    The board pitch is 32 px, so 32 boards span the atlas and both the joints
    and the per-board tone repeat exactly at the wrap. Each board is a slightly
    crowned face with a V-joint on its left; the joint is height, so the
    normal map lets it catch the light, and occlusion, so it stays a dark line
    whatever the sun does. A faint lengthwise grain is added later, with the
    rest of the weathering.
    """
    p = m(BOARD)
    assert ATLAS % p == 0
    sy, sx, _, X = c.field(0, ATLAS, y_lo, y_hi)
    board = np.floor(X / p).astype(np.int64)
    col = X - board * p                          # 0 .. p, joint at 0
    tone = 1.0 + 0.045 * (atlas.hash_unit(seed, board) - 0.5)
    # a V-joint about 3 px across: its floor and both shoulders are occluded,
    # which is what keeps the boarding legible at 20 m and beyond
    d = np.minimum(col, p - col)                 # distance to the joint line
    v = np.clip(1.0 - d / 1.5, 0.0, 1.0)
    c.mid[sy, sx] = ID_WALL
    c.shade[sy, sx] = tone * (1.0 - 0.24 * v)
    c.ao[sy, sx] = 1.0 - 0.22 * v
    crown = CLAD_H + 0.002 * np.sin(np.pi * col / p)
    c.height[sy, sx] = crown - JOINT_D * v


def paint_s1(c):
    """Ground storey: a low concrete plinth, then vertical boarding."""
    y0 = S1_Y0
    top = min(int(np.ceil(y0 + m(S1_TOP))), 236)
    fy = y0 + m(Z_FLASH)
    paint_boarding(c, 0, top, seed=11)
    # concrete plinth, with the bleed rows under z = 0 painted the same
    c.paint(0, ATLAS, 0, fy, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, 0, fy)
    z = (Y - y0) / PPM
    splash = 0.80 + 0.20 * np.clip(z / 0.30, 0.0, 1.0) ** 0.7   # rain splash-back
    c.shade[sy, sx] *= splash
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.30, 0, 1))
    # the boards' drip edge overhangs the plinth: occluded concrete under it
    c.mul(0, ATLAS, fy - 3, fy, 0.82, ao=0.78)
    # a faint panel seam halfway up the storey, as the boarding is delivered
    mid = y0 + m(1.85)
    c.mul(0, ATLAS, mid, mid + 1, 0.90, ao=0.9)
    c.lift(0, ATLAS, mid, mid + 1, -0.003)
    # occluded just under the upper storey's band board
    for k, f in enumerate((0.86, 0.92, 0.96)):
        yy = y0 + m(Z_STOREY) - 1 - k
        c.mul(0, ATLAS, yy, yy + 1, f, ao=0.82 + 0.05 * k)


def paint_s2(c):
    """Upper storey: the storey band board at its foot, then boarding."""
    y0 = S2_Y0
    bt = y0 + m(BAND_H)
    paint_boarding(c, bt, 548, seed=29)
    c.paint(0, ATLAS, y0 - 2, bt, ID_BAND, 1.0, 1.0, height=CLAD_H)
    c.bevel(0, ATLAS, y0, bt, BAND_RELIEF, 1.0, base=CLAD_H, axes="y")
    c.paint(0, ATLAS, y0 - 2, y0 + 1, ID_BAND, 0.85, 0.8)        # its lower edge
    c.mul(0, ATLAS, bt, bt + 2, 0.86, ao=0.82)                    # under its drip
    mid = y0 + m(1.85)
    c.mul(0, ATLAS, mid, mid + 1, 0.90, ao=0.9)                   # panel seam
    c.lift(0, ATLAS, mid, mid + 1, -0.003)


def paint_roof(c):
    """Profiled steel sheet: trapezoid ribs down the slope, steps across it.

    V is stretched up the shallow slope (ROOF_H rows over ROOF_SLOPE_LEN
    metres). The ribs vary in U only; the steps vary in V, so their heights
    are scaled by the band's px/m over PPM to keep their slope physical.
    """
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0 - 2, y0 + h + 2, ID_ROOF, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - 2, y0 + h + 2)
    dx = np.abs(((X % 32.0) - 1.0 + 16.0) % 32.0 - 16.0)    # from the rib's centre
    height = RIB_H * np.clip((2.8 - dx) / 1.3, 0.0, 1.0)
    foot = (dx >= 2.8) & (dx < 3.6)
    shade = np.where(foot, 0.92, 1.0)
    ao = np.where(foot, 0.86, 1.0)
    v = Y - y0
    rpm = ROOF_H / ROOF_SLOPE_LEN              # px per metre up the slope
    k = rpm / PPM
    step = max(round(0.40 * rpm), 1)           # transverse step of the profile
    s = v % step
    height = height + STEP_H * k * (1.0 - s / step)
    shade = np.where(s < 1.0, shade * 0.86, shade)
    shade = np.where(v < 3, shade * 0.85, shade)               # eave drip edge
    ridge = v >= h - 10                                         # ridge flashing
    height = np.where(ridge, 0.008 * k, height)
    shade = np.where(ridge, 0.97, shade)
    shade = np.where((v >= h - 10) & (v < h - 9), shade * 0.85, shade)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao


def paint_fascia(c):
    """The eave's vertical edge: a fascia board in the band colour, with a
    half-round steel gutter hung across its top, where the water leaves."""
    y0 = FASC_Y0
    top = y0 + FASC_H                       # the roof's edge
    c.paint(0, ATLAS, y0 - 2, top + 2, ID_BAND, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 - 2, y0 + 1, ID_BAND, 0.88)      # board's lower edge
    gh = GUTTER_PX
    g0 = top - 1 - gh
    c.paint(0, ATLAS, g0, top - 1, ID_METAL, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top - 1)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_METAL, 0.80)
    c.paint(0, ATLAS, top - 1, top + 2, ID_METAL, 0.80, height=0.0)  # roof sheet's drip edge
    c.ao[c.sl(0, ATLAS, g0 - 3, top + 2)] = 0.9
    for k, f in enumerate((0.92, 0.86, 0.80)):            # occluded under the gutter
        c.mul(0, ATLAS, g0 - 3 + k, g0 - 2 + k, f)
    sy, sx, _, X = c.field(0, ATLAS, g0 + 2, top - 1)     # hangers every 1.0 m
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.80, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_yard(c):
    """The back yards' screen wall: rendered blockwork with a flat coping."""
    y0 = YARD_Y0
    ct = y0 + m(YARD_H)
    c.paint(0, ATLAS, y0 - 2, ct + m(0.11), ID_RENDER, 1.0, 1.0, height=0.0)
    # block courses, 0.25 m high and 0.5 m long: both divide the atlas width;
    # the render follows them as shallow grooves
    bh = m(0.25)
    for k in range(1, 8):
        yy = y0 + bh * k
        if yy >= ct:
            break
        c.mul(0, ATLAS, yy, yy + 1, 0.94, ao=0.9)
        c.lift(0, ATLAS, yy, yy + 1, -0.002)
    sy, sx, Y, X = c.field(0, ATLAS, y0, ct)
    seam = (X % 32.0) < 1.0
    c.shade[sy, sx] = np.where(seam, c.shade[sy, sx] * 0.95, c.shade[sy, sx])
    c.height[sy, sx] = np.where(seam, c.height[sy, sx] - 0.002, c.height[sy, sx])
    sy, sx, Y, _ = c.field(0, ATLAS, y0 - 2, ct)
    z = (Y - y0) / PPM
    c.shade[sy, sx] *= 0.82 + 0.18 * np.clip(z / 0.45, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.86 + 0.14 * np.clip(z / 0.45, 0, 1))
    # coping: a sheet-metal cap standing proud, occluded under its lip
    c.paint(0, ATLAS, ct - m(0.06), ct + m(0.11), ID_CAP, 1.0, 1.0)
    c.bevel(0, ATLAS, ct - m(0.06), ct + m(0.11) + 2, COPING_H, 1.0, axes="y")
    c.paint(0, ATLAS, ct - m(0.06), ct - m(0.06) + 1, ID_CAP, 0.80, 0.7)


def paint_opening(c, kind):
    """One window, door or gate: casing, sill, sash frames, glass."""
    x0, y0 = ITEM_ORIGIN[kind]
    w, h, cs, cb, ct = OPENINGS[kind]
    rw, rh = item_size_px(kind)
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0 + m(cb), y0 + m(cb + h)
    if kind == "gate":
        paint_gate(c, x0, y0, rw, rh, ox0, ox1, oy0, oy1)
        return
    # the shed door is cut straight through its stained boarding; every other
    # opening carries a painted casing, standing proud with rounded arrises
    cas_id = ID_ENTRY if kind == "door_shed" else ID_TRIM
    # casing, bled 2 px outward so filtering at the region edge stays casing
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, cas_id, 1.0, 1.0, height=0.0)

    if kind == "door_shed":
        for xx in np.arange(x0 - 2, x0 + rw + 2, m(0.25)):
            c.mul(xx, xx + 1, y0 - 2, y0 + rh + 2, 0.85, ao=0.85)
            c.lift(xx, xx + 1, y0 - 2, y0 + rh + 2, -0.005)
        c.mul(ox0 - 1, ox1 + 1, oy1, oy1 + 2, 0.80, ao=0.78)
    else:
        c.bevel(x0, x0 + rw, y0, y0 + rh, CASING_H, 1.0)
        top = y0 + rh
        c.paint(x0 - 2, x0 + rw + 2, top - 3, top + 2, ID_METAL, 1.0)   # drip cap
        sy, sx, Y, _ = c.field(x0 - 2, x0 + rw + 2, top - 3, top + 2)
        c.height[sy, sx] = 0.032 - 0.012 * np.clip((Y - (top - 3)) / 3.0, 0.0, 1.0)
        c.paint(x0 - 2, x0 + rw + 2, top - 4, top - 3, ID_TRIM, 0.85, 0.8)
        c.mul(ox0 - 1, ox1 + 1, oy1, oy1 + 1, 0.84, ao=0.8)             # head shadow
        c.mul(ox0 - 1, ox0, oy0, oy1, 0.93)
        if cb > 0:                                                       # sill board
            c.paint(x0 - 2, x0 + rw + 2, y0 - 2, oy0, ID_TRIM, 1.0)
            c.bevel(x0, x0 + rw, y0, oy0, SILL_H, 1.0)
            c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + 1, ID_TRIM, 0.80, 0.8)

    if kind.startswith("door_"):
        paint_door(c, ox0, ox1, oy0, oy1, kind)
        return

    # Glass: this sets the id and the AO, and albedo then hands every pane to
    # glazing.rooms(), which owns the colour. The glass keeps a flat normal.
    f = m(0.0625)                       # frame round the glass
    c.paint(ox0, ox1, oy0, oy1, ID_SASH, 1.0, 1.0)
    c.bevel(ox0, ox1, oy0, oy1, SASH_H, 1.0)
    c.paint(ox0 + f, ox1 - f, oy0 + f, oy1 - f, ID_GLASS, ao=0.9, height=0.0)
    # Plain glass: one clear pane inside the frame, with no crossbars and no
    # mullions, as the type's windows are.
    c.mul(ox0 + f, ox1 - f, oy1 - f - 1, oy1 - f, 0.82, ao=0.8)
    c.mul(ox0 + f, ox0 + f + 1, oy0 + f, oy1 - f, 0.88)


def paint_door(c, x0, x1, y0, y1, kind):
    c.paint(x0, x1, y0, y1, ID_DOOR, 1.0, 1.0, height=0.0)
    wpx = x1 - x0
    if kind == "door_shed":
        # The store's leaf: boarded like the shed it is set in, but in the
        # door colour rather than the boarding's, with a shadow gap round it.
        # Painted in the boarding colour it vanished, and the shed then read
        # as one blank red panel across the whole entrance.
        for xx in np.arange(x0, x1, m(0.12)):
            c.mul(xx, xx + 1, y0, y1, 0.82, ao=0.82)
            c.lift(xx, xx + 1, y0, y1, -0.004)
        for zz in (y0 + m(0.30), y1 - m(0.36)):                  # ledger rails
            c.bevel(x0, x1, zz, zz + m(0.09), 0.012, 1.0, axes="y")
            c.mul(x0, x1, zz, zz + 1, 0.88, ao=0.85)
        hx = x1 - m(0.12)
        c.paint(hx - 1, hx + 1, y0 + m(0.94), y0 + m(1.06), ID_HANDLE, 1.0, height=0.025)
        for a0, a1, b0, b1, f in ((x0, x0 + 2, y0, y1, 0.70), (x1 - 2, x1, y0, y1, 0.76),
                                  (x0, x1, y1 - 2, y1, 0.66)):
            c.mul(a0, a1, b0, b1, f, ao=0.7)                     # shadow gap round it
            c.lift(a0, a1, b0, b1, -0.006)
        c.paint(x0, x1, y0, y0 + 2, ID_DOOR, 0.80, 0.7)
        return
    if kind == "door_front":
        # boarded leaf with a small glazed light near the head, stiles proud
        for xx in np.arange(x0, x1, m(0.12)):
            c.mul(xx, xx + 1, y0, y1, 0.82, ao=0.82)
            c.lift(xx, xx + 1, y0, y1, -0.004)
        st = m(0.08)
        c.paint(x0, x0 + st, y0, y1, height=0.008)
        c.paint(x1 - st, x1, y0, y1, height=0.008)
        gx0, gx1 = x0 + wpx * 0.28, x1 - wpx * 0.28
        gy0, gy1 = y0 + m(1.42), y0 + m(1.86)
        c.paint(gx0 - 2, gx1 + 2, gy0 - 2, gy1 + 2, ID_SASH, 1.0, 0.9)
        c.bevel(gx0 - 2, gx1 + 2, gy0 - 2, gy1 + 2, SASH_H, 1.0)
        c.paint(gx0, gx1, gy0, gy1, ID_GLASS, 0.86, 0.85, height=0.0)
        c.mul(gx0, gx1, gy1 - 1, gy1, 0.8)
    else:
        # the yard door: a glazed terrace door, a frame round one big pane
        f = m(0.09)
        c.paint(x0, x1, y0, y1, height=SASH_H)
        c.paint(x0 + f, x1 - f, y0 + f, y1 - f, ID_GLASS, 0.90, 0.9, height=0.0)
        c.mul(x0 + f, x1 - f, y1 - f - 1, y1 - f, 0.82, ao=0.8)
        c.mul(x0 + f, x0 + f + 1, y0 + f, y1 - f, 0.88)
        c.paint(x0, x1, y0, y0 + m(0.28), ID_DOOR, 1.0, 1.0)   # solid foot panel
        c.bevel(x0, x1, y0, y0 + m(0.28), SASH_H, 1.0)
    hx = x1 - m(0.11)
    c.paint(hx - 1, hx, y0 + m(0.92), y0 + m(1.10), ID_HANDLE, 0.9, height=0.015)
    c.paint(hx - 2, hx + 1, y0 + m(1.00), y0 + m(1.06), ID_HANDLE, 1.0, height=0.030)
    c.paint(x0, x1, y0, y0 + 2, ID_DOOR, 0.80, 0.7)                  # kick wear


def paint_gate(c, x0, y0, rw, rh, ox0, ox1, oy0, oy1):
    """The back yard's timber gate, in a rendered opening with a concrete head."""
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, ID_RENDER, 0.84, 0.8, height=0.0)
    c.paint(x0 - 2, x0 + rw + 2, y0 + rh - m(0.06), y0 + rh + 2, ID_CAP, 0.92, 0.8,
            height=0.015)
    c.paint(ox0, ox1, oy0, oy1, ID_GATE, 1.0, 1.0)
    for xx in np.arange(ox0, ox1, m(0.14)):                  # vertical boards
        c.mul(xx, xx + 1, oy0, oy1, 0.78, ao=0.8)
        c.lift(xx, xx + 1, oy0, oy1, -0.005)
    for zz in (oy0 + m(0.22), oy1 - m(0.28)):                # two ledger rails
        c.bevel(ox0, ox1, zz, zz + m(0.10), 0.014, 1.0, axes="y")
        c.mul(ox0, ox1, zz, zz + 1, 0.88, ao=0.85)
    c.mul(ox0, ox1, oy1 - 1, oy1, 0.78, ao=0.75)
    c.paint(ox0, ox1, oy0, oy0 + 2, ID_GATE, 0.80, 0.7)
    hx = ox1 - m(0.10)
    c.paint(hx - 1, hx + 1, oy0 + m(0.90), oy0 + m(1.02), ID_HANDLE, 1.0, height=0.025)


def paint_shed(c):
    """The entrance shed's stained boarding, plinth to flat roof.

    One strip serves the shed's front and both returns: U is that face's own
    along-coordinate, V is world height, so the boards stand upright on all
    three and the plinth line runs round the corner without a break.
    """
    x0, y0, w, h = SHED
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_ENTRY, 1.0, 1.0, height=CLAD_H)
    for xx in np.arange(x0 - 2, x0 + w + 2, m(0.25)):
        c.mul(xx, xx + 1, y0 - 2, y0 + h + 2, 0.84, ao=0.84)
        c.lift(xx, xx + 1, y0 - 2, y0 + h + 2, -JOINT_D)
    fy = y0 + m(Z_FLASH)
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, fy, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(x0 - 2, x0 + w + 2, y0 - 2, fy)
    z = (Y - y0) / PPM
    c.shade[sy, sx] *= 0.80 + 0.20 * np.clip(z / 0.30, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.30, 0, 1))
    c.mul(x0 - 2, x0 + w + 2, fy - 3, fy, 0.82, ao=0.78)
    # sheet-metal cap along the top of the boarding, under the flat roof
    ct = y0 + m(SHED_V - 0.08)
    c.paint(x0 - 2, x0 + w + 2, ct, y0 + h + 2, ID_CAP, 1.0, 1.0, height=0.030)
    c.paint(x0 - 2, x0 + w + 2, ct, ct + 1, ID_CAP, 0.80, 0.72)


def _bay_cladding(c, rect, width):
    """Plinth, vertical boarding and the storey seam, at the LOD3 density."""
    x0, y0, w, h = rect
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_WALL, 1.0, 1.0, height=0.0)
    for s in np.arange(0.0, width + BOARD * 0.5, BOARD):
        xx = x0 + s * PPM3
        c.mul(xx, xx + 1, y0 - 2, y0 + h + 2, 0.82, ao=0.85)
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + Z_FLASH * PPM3, ID_PLINTH, 0.94, 0.88)


def paint_bay(c, rect, items):
    """One dwelling bay's elevation: cladding, storey band and every opening.

    The openings are the same rectangles build.py cuts at the upper tiers,
    drawn at this region's scale, so a window does not move across the
    LOD2/LOD3 switch — only its reveal goes. Flat: see the relief note above.
    """
    x0, y0, w, h = rect
    _bay_cladding(c, rect, BAY_W)
    bt = y0 + Z_STOREY * PPM3
    c.paint(x0 - 2, x0 + w + 2, bt, bt + BAND_H * PPM3, ID_BAND, 1.0, 1.0)
    c.mul(x0 - 2, x0 + w + 2, bt - 1, bt, 0.84, ao=0.82)
    for kind, s, z in items:
        ow, oh, cs, cb, ct = OPENINGS[kind]
        l, r = x0 + (s - ow / 2 - cs) * PPM3, x0 + (s + ow / 2 + cs) * PPM3
        b, t = y0 + (z - cb) * PPM3, y0 + (z + oh + ct) * PPM3
        il, ir = x0 + (s - ow / 2) * PPM3, x0 + (s + ow / 2) * PPM3
        ib, it = y0 + z * PPM3, y0 + (z + oh) * PPM3
        c.paint(l, r, b, t, ID_TRIM, 1.0, 1.0)
        c.mul(l, r, t - 1, t, 0.80, ao=0.8)
        if kind == "door_front":
            c.paint(il, ir, ib, it, ID_DOOR, 1.0, 1.0)
            c.paint(il + 1, ir - 1, y0 + (z + 1.42) * PPM3,
                    y0 + (z + 1.86) * PPM3, ID_GLASS, 0.86, 0.85)
        elif kind == "door_patio":
            c.paint(il, ir, ib, it, ID_SASH, 1.0, 1.0)
            c.paint(il + 1, ir - 1, y0 + (z + 0.28) * PPM3, it - 1,
                    ID_GLASS, 0.90, 0.9)
        else:
            c.paint(il, ir, ib, it, ID_SASH, 1.0, 1.0)
            c.paint(il + 1, ir - 1, ib + 1, it - 1, ID_GLASS, 0.92, 0.9)
            c.mul(il + 1, ir - 1, it - 2, it - 1, 0.84, ao=0.8)


def paint_lod3_shed(c, width, door):
    """The entrance shed's front at LOD3: boarding with its door painted in."""
    rect = LOD3_SHED
    x0, y0, w, h = rect
    _bay_cladding(c, rect, width)
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_ENTRY, 1.0, 1.0)
    for s in np.arange(0.0, width + 0.125, 0.25):
        xx = x0 + s * PPM3
        c.mul(xx, xx + 1, y0 - 2, y0 + h + 2, 0.80, ao=0.84)
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + Z_FLASH * PPM3, ID_PLINTH, 0.94, 0.88)
    dw, dh, cs, cb, ct = OPENINGS["door_shed"]
    l = x0 + (width - dw) / 2.0 * PPM3
    c.paint(l, l + dw * PPM3, y0 + door * PPM3, y0 + (door + dh) * PPM3,
            ID_DOOR, 1.0, 1.0)
    c.mul(l, l + dw * PPM3, y0 + (door + dh) * PPM3 - 1,
          y0 + (door + dh) * PPM3, 0.68, ao=0.72)


def paint_patches(c):
    spec = {"trim": (ID_TRIM, 1.0, 1.0), "soffit": (ID_BAND, 0.86, 0.82),
            "reveal": (ID_TRIM, 0.70, 0.6), "blank": (ID_BLANK, 1.0, 0.5),
            "tread": (ID_PLINTH, 0.96, 1.0), "cap": (ID_CAP, 1.0, 1.0),
            "barge": (ID_BAND, 0.97, 1.0), "render": (ID_RENDER, 0.94, 0.9),
            # soot inside the vents' flues: blank darkened to about sRGB 34,
            # and occluded, as a narrow shaft is whatever the sun does
            "flue": (ID_BLANK, 0.45, 0.35)}
    atlas.paint_patches(c, PATCHES, spec)


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    The wall bands' V is height and the roof band's is slope, so ground
    splash, the sheltered eaves and the dirtier eave land the same on every
    wall and every roof face. The LOD3 bays get the same, at their scale."""
    w = weathering.Weather(c, clean=(ID_GLASS,), steel=(ID_ROOF, ID_METAL, ID_CAP))
    w.grime()
    w.fade((ID_WALL, ID_TRIM, ID_SASH, ID_DOOR, ID_ENTRY, ID_BAND))
    w.wash((ID_WALL, ID_ENTRY))
    # S1: the plinth and the boarding's splashed foot; S2: its top sheltered
    # under the soffit
    fy = S1_Y0 + m(Z_FLASH)
    w.plinth(0, ATLAS, S1_Y0, fy, (ID_PLINTH,))
    w.splash(0, ATLAS, fy, 236, (ID_WALL,))
    w.shelter(0, ATLAS, S2_Y0 + m(Z_EAVE - 0.5 - Z_STOREY), S2_Y0 + m(Z_EAVE - Z_STOREY),
              (ID_WALL,), top=548)
    # the roof, silt along the ribs' feet, a few rust specks on the drip edge
    roof = (ID_ROOF,)
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, ROOF_SLOPE_LEN, roof)

    def silt(Y, X, nz):
        dx = np.abs(((X % 32.0) - 1.0 + 16.0) % 32.0 - 16.0)
        return 0.12 * ((dx >= 2.8) & (dx < 4.5))
    w.add("D", 0, ATLAS, ROOF_Y0 - 2, ROOF_Y0 + ROOF_H + 2, silt, roof)
    w.add("R", 0, ATLAS, ROOF_Y0 - 2, ROOF_Y0 + 3, lambda Y, X, nz: 0.12 * nz("speck"), roof)
    # the fascia: runs down the board from the gutter, a dirty belly
    g0 = FASC_Y0 + FASC_H - 10.0
    w.add("D", 0, ATLAS, FASC_Y0 - 2, g0, 0.06, (ID_BAND,))
    w.runs(0, ATLAS, FASC_Y0 - 2, g0, (ID_BAND,), 0.22, fall=6.0, lo=0.4, hi=1.6)
    w.add("D", 0, ATLAS, g0, g0 + 4, lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"), (ID_METAL,))
    # the yards' rendered screen walls: soil at the foot, runs from the coping
    w.plinth(0, ATLAS, YARD_Y0, YARD_Y0 + m(YARD_H - 0.06), (ID_RENDER,))
    # the entrance shed: its plinth, the boarding's foot, runs under its cap
    x0, y0, sw, sh = SHED
    fy = y0 + m(Z_FLASH)
    ct = y0 + m(SHED_V - 0.08)
    w.plinth(x0 - 2, x0 + sw + 2, y0, fy, (ID_PLINTH,))
    w.splash(x0 - 2, x0 + sw + 2, fy, ct, (ID_ENTRY,))
    w.runs(x0 - 2, x0 + sw + 2, fy, ct, (ID_ENTRY,), 0.15, fall=m(0.3))
    # openings: sills, heads and bottom rails; doors' and the gate's handles
    # and feet
    for kind, (wd, h, cs, cb, ct) in OPENINGS.items():
        x0, yb = ITEM_ORIGIN[kind]
        rw, rh = item_size_px(kind)
        ox0, ox1 = x0 + m(cs), x0 + m(cs + wd)
        oy0, oy1 = yb + m(cb), yb + m(cb + h)
        if kind == "gate":
            w.door(ox0, ox1, oy0, oy1, (ID_GATE,), handle=(ox1 - m(0.10), oy0 + m(0.96)))
        elif kind == "door_shed":
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR,), handle=(ox1 - m(0.12), oy0 + m(1.00)))
        elif kind.startswith("door"):
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR,), handle=(ox1 - m(0.11), oy0 + m(1.03)))
        else:
            w.window(x0, yb, rw, rh, oy0, oy1, m(0.0625), (ID_TRIM,), (ID_SASH,))
    # the LOD3 painted elevations, at their own 14 px/m
    for x0, y0, bw, bh in (LOD3_FRONT, LOD3_REAR, LOD3_SHED):
        fy = y0 + Z_FLASH * PPM3
        w.plinth(x0 - 2, x0 + bw + 2, y0, fy, (ID_PLINTH,), ppm=PPM3)
        w.splash(x0 - 2, x0 + bw + 2, fy, y0 + bh + 2, (ID_WALL, ID_ENTRY), ppm=PPM3)
        w.shelter(x0 - 2, x0 + bw + 2, y0 + (Z_EAVE - 0.5) * PPM3, y0 + Z_EAVE * PPM3,
                  (ID_WALL,), top=y0 + bh + 2)
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_s1(c)
    paint_s2(c)
    paint_roof(c)
    paint_fascia(c)
    paint_yard(c)
    paint_shed(c)
    paint_bay(c, LOD3_FRONT, FRONT_UNIT)
    paint_bay(c, LOD3_REAR, REAR_UNIT)
    paint_lod3_shed(c, SHED_FACE_W, Z_FLOOR)
    for kind in OPENINGS:
        paint_opening(c, kind)
    paint_patches(c)
    c.check_bands(BAND_IDS)

    # Weathering. Every field is periodic, so the bands still wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    boarded = np.isin(c.mid, (ID_WALL, ID_BAND, ID_DOOR, ID_ENTRY, ID_GATE))
    grain = atlas.noise(c, 5, 0.35, 60.0)            # streaks along the upright boards
    c.shade[boarded] *= 1.0 + 0.02 * grain[boarded]
    c.height[boarded] += 0.0003 * grain[boarded]
    weathered = np.isin(c.mid, (ID_ROOF, ID_RENDER))
    streak = atlas.noise(c, 7, 0.8, 40.0)            # rain runs down
    c.shade[weathered] *= 1.0 + 0.03 * streak[weathered]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_RENDER))
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
    t[ID_WALL] = pal["wall"]
    t[ID_TRIM] = t[ID_SASH] = pal["trim"]
    t[ID_BAND] = pal["band"]
    t[ID_ROOF] = pal["roof"]
    t[ID_METAL] = np.minimum(np.array(pal["roof"], np.float32) * 1.18 + 6, 255)
    t[ID_DOOR] = pal["door"]
    t[ID_ENTRY] = pal["entry"]
    return t


def export(out_dir, ss=atlas.SS):
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.012)
    c.weather.dust(cav, (ID_WALL, ID_ENTRY))         # in the board joints
    rough = 0.04 * atlas.noise(c, 13, 20.0)
    path = os.path.join(out_dir, ASSET)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS,)), path + "_normal.png"),
               atlas.save(glazing.night_rooms(atlas.coverage(c, ID_GLASS) > 0,
                                          atlas.emission(c, ID_GLASS)),
                          path + "_emission.png")]
    glass = atlas.coverage(c, ID_GLASS) >= 0.5
    for v in VARIANTS:
        rgb = glazing.rooms(glass, atlas.albedo(c, lut(v), grime=0.25 * cav))
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
