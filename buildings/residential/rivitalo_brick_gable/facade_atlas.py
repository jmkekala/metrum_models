# SPDX-License-Identifier: GPL-2.0-only

"""Albedo, ORM, normal and emission atlas for rivitalo_brick_gable, and the
layout build.py maps into.

This describes one asset and nothing else, so it lives beside build.py rather
than in scripts/. It is also the single source of the numbers the two files
share: build.py imports the z-levels, panel layout, opening sizes and region
rects from here instead of writing them a second time, so the pixel layout and
the UVs cannot drift apart. Importing this module only defines those constants; the painting
runs when paint() is called. Rasterising is scripts/atlas.py's: a canvas
supersampled SS x SS per pixel, with a height channel the normal map is
derived from (numpy and scipy; Pillow to save).

    python3 facade_atlas.py export      # writes every map into ./export

The atlas is a trim sheet rather than one picture per elevation. This row of
four dwellings is 30 m long, so the walls sample tiling bands and every opening
samples a region of its own:

    y    2 ..   34   PLINTH  cast concrete base, z 0 .. 0.5
    y   38 ..  238   WOOD    horizontal lap siding, one storey tall (3.125 m)
    y  242 ..  514   BRICK   facing brick, 4.25 m tall, stretcher bond
    y  518 ..  582   VBOARD  vertical board-and-batten, V stretched per panel
    y  586 ..  682   ROOF    bitumen felt, V stretched up the shallow slope
    y  686 ..  710   FASCIA  the roof slab's edge, with its gutter
    y  714 ..  754   SOFFIT  eave underside with exposed rafter ends
    y  758 ..  910   unique  doors, windows, the yard fence panel and its gate
    y  914 .. 1018   unique  the small balcony window, LOD3 bays, patches

PLINTH, WOOD, BRICK, VBOARD, ROOF, FASCIA and SOFFIT span the full width and
tile in U. WOOD and BRICK are one storey tall and are sampled from each
storey's own foot, so every wall hands over from the ground storey's run to the
upper storey's run at Z_STOREY. Both Z_STOREY - Z_FLOOR and Z_EAVE - Z_STOREY
are whole numbers of courses and of siding boards, so that handover is
seamless: 3.125 m is 40 brick courses and 25 siding boards exactly.

Every opening's region carries its casing as well as its glazing, because the
casing is the one part of a window a tiling band cannot place. build.py cuts a
ring of faces round each opening for it to land on.

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

ASSET = "rivitalo_brick_gable"
ATLAS = 1024
PPM = 64.0

# --------------------------------------------------------- vertical layout
# Metres above ground, shared by every wall so storey lines agree all round.
COURSE = 0.078125    # brick course pitch: 5 px, 64 courses per atlas height
LAP = 0.125          # lap siding exposure: 8 px, 25 boards per storey
BOARD = 0.125        # vertical board-and-batten pitch: 8 px, 128 per atlas
Z_FLOOR = 0.3125     # plinth top = ground-floor level; door thresholds
Z_STOREY = 3.4375    # upper floor: 40 courses above Z_FLOOR
Z_EAVE = 6.5625      # front wall top, where the roof soffit meets it
WALL_INTO_ROOF = 0.12  # walls run this far into the roof slab, which trims them

# ------------------------------------------------------------- openings
# kind -> (width, height, casing side, casing bottom, casing top), metres.
# Casing is painted, never modelled: a 20-40 mm proud casing fails the 0.25 m
# relief test by an order of magnitude. Doors have no bottom casing — the leaf
# runs down to its threshold. The front door's casing is the wide dark surround
# the type sets its entrance in.
OPENINGS = {
    "door_front": (1.00, 2.10, 0.20, 0.0, 0.20),
    "door_glazed": (1.00, 2.10, 0.10, 0.0, 0.15),
    "win_gf": (2.00, 1.55, 0.10, 0.10, 0.10),
    "win_up": (2.00, 1.35, 0.10, 0.10, 0.10),
    "win_bw": (2.60, 1.45, 0.10, 0.10, 0.10),
    "win_bs": (1.40, 1.30, 0.10, 0.10, 0.10),
}
# Recess from the wall face to the glass or leaf. The front door is deliberately
# deeper than the windows: the type sets its entrance back into the boarding,
# and at 0.30 m it is the one opening that clears the 0.25 m relief test on its
# own rather than on the shadow line alone.
REVEAL_DEPTH = {"door_front": 0.30}
REVEAL_DEFAULT = 0.14

# ------------------------------------------------------------ atlas bands
PLINTH_Y0, PLINTH_H = 2.0, 32.0      # v of z = 0 on any wall foot
WOOD_Y0, WOOD_H = 38.0, 200.0        # v of the foot of a storey's siding run
BRICK_Y0, BRICK_H = 242.0, 272.0     # v of the foot of a storey's brickwork
VB_Y0, VB_H = 518.0, 64.0            # V normalised over each boarded panel
ROOF_Y0, ROOF_H = 586.0, 96.0
ROOF_SLOPE_LEN = 8.0                 # metres of slope the band is stretched over
FASC_Y0, FASC_H = 686.0, 24.0        # = the roof slab's 0.375 m thickness
GUTTER_PX = 8.0      # the gutter's rows, hung across the fascia's top
# The downpipes' sides span the middle five of them (scripts/downpipes.py)
PIPE_STRIP = (FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 - 2.5,
              FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 + 2.5)
SOF_Y0, SOF_H = 714.0, 40.0          # v of the wall face; 0.625 m of overhang
UNI_A, UNI_A_H = 758.0, 152.0
UNI_B, UNI_B_H = 914.0, 104.0

# Region origins: the bottom-left of each opening's casing, in pixels.
ITEM_ORIGIN = {
    "door_front": (4.0, UNI_A),
    "door_glazed": (100.0, UNI_A),
    "win_gf": (183.0, UNI_A),
    "win_up": (330.0, UNI_A),
    "win_bw": (477.0, UNI_A),
    "win_bs": (4.0, UNI_B),
}
# One 2.5 m bay of the yard fence: a post, then vertical boards on two rails —
# and the same bay again with the gate hung in it. Every fence run is built as a
# whole number of these, so the boards keep their pitch instead of stretching
# with the run's length, and the gate needs no hole cut for it: at a few
# centimetres proud of the boards a leaf is far under the 0.25 m relief test.
FENCE = (662.0, UNI_A, 160.0, 112.0)
GATE = (828.0, UNI_A, 160.0, 112.0)
FENCE_W, FENCE_H = 2.5, 1.75
GATE_LEAF = (0.72, 1.77, 1.55)       # s0, s1 within the bay, and leaf height

PATCHES = {name: (800.0 + 16.0 * i, UNI_B, 8.0, 8.0) for i, name in enumerate(
    ("reveal", "blank", "pave", "post", "cap", "tread", "barge", "deck", "flue"))}

# ---------------------------------------------------- LOD3 painted elevations
# At LOD3 the front and rear walls are not cut at all: each dwelling bay is one
# quad mapped to a painted elevation of that bay. Cutting them instead costs
# more than the rest of the tier put together — a wall region has to be
# retriangulated round every hole — and the triangles it frees are what let the
# balcony, its dividers and every yard fence survive to the last tier. This is
# CLAUDE.md's "flatten geometry into suitable shared-atlas regions".
#
# 14 px/m is ample here: at the tier's 120 m a 7.5 m bay is about 72 px on
# screen, and the region is 105.
PPM3 = 14.0
BAY_W = 7.5                       # one dwelling; build.py asserts it
BAY_H_FRONT = Z_EAVE              # front wall, ground to soffit
BAY_H_REAR = 6.4585               # rear wall top; build.py asserts it
LOD3_FRONT = (120.0, UNI_B, BAY_W * PPM3, BAY_H_FRONT * PPM3)
LOD3_REAR = (232.0, UNI_B, BAY_W * PPM3, BAY_H_REAR * PPM3)

# ------------------------------------------------------------- elevations
# Which openings sit where in one dwelling bay, as (kind, s along the bay,
# sill z), and which cladding each vertical panel of the bay wears, as
# (s0, s1, band). build.py cuts these at LOD0-LOD2 and paints them into the bay
# regions above at LOD3, so both files read them from one place or a window
# would move across the LOD2/LOD3 switch.
#
# The front is the street elevation: a brick pier on each party line, a
# vertically boarded panel in the middle of the bay with the dwelling's own
# front door recessed into it, and a large window each side of it on both
# storeys. That is the four front windows the type shows per dwelling.
PIER = 0.30                       # half a 0.6 m brick pier, each side of a line
GF_SILL, UP_SILL = 0.90, 4.30
DOOR_S = 3.75                     # front door, centred in the bay

FRONT_PANELS = [(0.00, 0.30, "brick"), (0.30, 2.85, "wood"),
                (2.85, 4.65, "vboard"), (4.65, 7.20, "wood"),
                (7.20, 7.50, "brick")]
FRONT_UNIT = [
    ("win_gf", 1.575, GF_SILL),
    ("door_front", DOOR_S, Z_FLOOR),
    ("win_gf", 5.925, GF_SILL),
    ("win_up", 1.575, UP_SILL),
    ("win_up", 5.925, UP_SILL),
]

# The yard elevation. The ground storey sits under the balcony: one large
# window, and beside it the alcove whose side wall carries the door into the
# house — the door is not in the wall the window is in, but at a right angle to
# it in the opening next to it. The upper storey stands inside the balcony and
# is nearly all glass: the balcony door and two windows.
ALCOVE = (4.10, 5.40, Z_FLOOR, 2.70, 1.40)  # s0, s1, z0, z1, depth
ALCOVE_DOOR_S = 0.70                     # along the alcove's side wall
REAR_GF_PANELS = [(0.00, 0.30, "brick"), (0.30, 3.60, "wood"),
                  (3.60, 5.60, "vboard"), (5.60, 7.20, "wood"),
                  (7.20, 7.50, "brick")]
REAR_UP_PANELS = [(0.00, 0.30, "brick"), (0.30, 7.20, "wood"),
                  (7.20, 7.50, "brick")]
REAR_GF_UNIT = [("win_gf", 1.70, GF_SILL)]
REAR_UP_UNIT = [
    ("door_glazed", 1.20, Z_STOREY),
    ("win_bw", 4.00, UP_SILL),
    ("win_bs", 6.30, UP_SILL),
]
# The end walls are solid brick, as the type's gables are; a terrace's ends
# carry no rooms that want a view.
END_PANELS = [(0.00, 8.00, "brick")]


def item_size_px(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    return (w + 2.0 * cs) * PPM, (h + cb + ct) * PPM


# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_WOOD, ID_VBOARD, ID_BRICK, ID_ROOF = 0, 1, 2, 3, 4, 5
ID_TRIM, ID_SASH, ID_GLASS, ID_DOOR, ID_METAL, ID_POST = 6, 7, 8, 9, 10, 11
ID_SOFFIT, ID_FENCE, ID_RAIL, ID_PAVE, ID_HANDLE = 12, 13, 14, 15, 16
# (roughness, metallic). Galvanised posts and the gutter are the only real
# metals; painted steel stays mostly dielectric, because the paint is what the
# light sees.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_WOOD: (0.72, 0.0),
    ID_VBOARD: (0.74, 0.0), ID_BRICK: (0.82, 0.0), ID_ROOF: (0.86, 0.0),
    ID_TRIM: (0.48, 0.0), ID_SASH: (0.46, 0.0), ID_GLASS: (0.08, 0.0),
    ID_DOOR: (0.50, 0.0), ID_METAL: (0.38, 0.35), ID_POST: (0.42, 0.65),
    ID_SOFFIT: (0.76, 0.0), ID_FENCE: (0.78, 0.0), ID_RAIL: (0.70, 0.0),
    ID_PAVE: (0.88, 0.0), ID_HANDLE: (0.32, 0.80),
}

# ---------------------------------------------------------------- palettes
# The type wears stained timber against facing brick, and the stain is what a
# street of these varies. Brick moves with it — red brick under the dark stains,
# the pale yellow brick Finnish suburbs are full of under the ochre — but never
# within one building: this is the low-rise case in CLAUDE.md, one coherent
# treatment per instance, repeated along the row.
VARIANTS = {
    "brown": {"wood": (122, 68, 46), "brick": (148, 88, 66),
              "roof": (54, 54, 56), "trim": (44, 44, 42),
              "door": (94, 52, 36), "fence": (128, 66, 48)},
    "red": {"wood": (124, 62, 50), "brick": (144, 86, 66),
            "roof": (58, 56, 54), "trim": (48, 44, 40),
            "door": (74, 50, 42), "fence": (130, 64, 52)},
    "ochre": {"wood": (168, 124, 74), "brick": (198, 180, 138),
              "roof": (62, 60, 56), "trim": (58, 50, 42),
              "door": (96, 62, 40), "fence": (150, 110, 66)},
    "grey": {"wood": (106, 102, 96), "brick": (138, 124, 110),
             "roof": (56, 58, 60), "trim": (46, 48, 48),
             "door": (68, 70, 70), "fence": (96, 93, 88)},
    "green": {"wood": (86, 96, 76), "brick": (148, 88, 66),
              "roof": (54, 56, 56), "trim": (44, 48, 44),
              "door": (66, 76, 62), "fence": (92, 100, 80)},
}
DEFAULT_VARIANT = "brown"
# Opaque glass, a neutral dark grey — darker than the catalog's timber houses
# and darker again than rivitalo_two_storey. This type's windows are large and
# its balcony is nearly all glass, and at a paler value those openings read as
# white panels in direct sun rather than as glass. Neutral and low-saturation,
# with the separation carried by roughness in the ORM; nothing is reflected into
# the albedo.
FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (150, 148, 142),
    ID_POST: (128, 130, 132), ID_PAVE: (158, 156, 150),
    ID_HANDLE: (152, 148, 140), ID_BLANK: (52, 52, 52),
}

# Which ids each tiling band may contain. A stray pixel in a band is not a
# local blemish: every surface sampling that band repeats it.
BAND_IDS = {
    "PLINTH": ((0, 36), {ID_PLINTH}),
    "WOOD": ((36, 240), {ID_WOOD}),
    "BRICK": ((240, 516), {ID_BRICK}),
    "VBOARD": ((516, 584), {ID_VBOARD}),
    "ROOF": ((584, 684), {ID_ROOF, ID_METAL}),
    "FASCIA": ((684, 712), {ID_METAL, ID_TRIM}),
    "SOFFIT": ((712, 756), {ID_SOFFIT}),
}


# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto. The mesh
# already models every recess over 0.25 m; these are the few centimetres of
# board, brick and sheet that only a normal map can show. The LOD3 bays are
# painted at PPM3, not PPM, and seen only beyond ~120 m, so they stay flat.
LAP_BUTT = 0.018     # lap siding: thickness at a board's butt
LAP_TOP = 0.004      # ... and at its top, under the next board's butt
BRICK_FACE = 0.006   # brick face proud of the recessed mortar
BATTEN_H = 0.018     # battens over the board joints
CASING_H = 0.020     # window and door casings
SILL_H = 0.035       # sill boards
SASH_H = 0.012       # sash frames, proud of the glass
GUTTER_R = 0.070     # half-round gutter's radius
RAFTER_H = 0.050     # rafter ends below the soffit boarding
RAIL_H = 0.022       # fence rails and ledgers, proud of the boards


# ============================================================ painting
def m(v):
    """Metres -> pixels."""
    return v * PPM


# ------------------------------------------------------------------ bands
def paint_plinth(c):
    """Cast concrete, the 0.3125 m base every wall stands on."""
    y0, h = PLINTH_Y0, PLINTH_H
    c.paint(0, ATLAS, y0 - 2, y0 + h + 2, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, 0, y0 + h + 2)
    z = (Y - y0) / PPM
    splash = 0.80 + 0.20 * np.clip(z / 0.22, 0.0, 1.0) ** 0.7   # rain splash-back
    c.shade[sy, sx] *= splash
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.22, 0, 1))
    # board-formed pour lines, and the occluded strip under the cladding's drip
    for zz in (0.14, 0.26):
        yy = y0 + m(zz)
        c.mul(0, ATLAS, yy, yy + 1, 0.94, ao=0.94)
        c.lift(0, ATLAS, yy, yy + 1, -0.002)
    top = y0 + m(Z_FLOOR)
    c.mul(0, ATLAS, top - 3, top + 2, 0.80, ao=0.74)


def paint_wood(c):
    """One storey of horizontal lap siding, 0.125 m to the weather.

    The band is exactly 25 boards tall and a storey is exactly 25 boards, so a
    wall hands over from the ground storey's run to the upper storey's at
    Z_STOREY without a part board. Each board is a wedge, thick at its butt, so
    the normal map tilts it towards the sky and puts a downward step under
    every butt; the lap line at its foot is occlusion as well. A lengthwise
    grain is added later with the rest of the weathering.
    """
    y0, h = WOOD_Y0, WOOD_H
    p = m(LAP)
    assert int(h) % int(p) == 0, "the siding band is not a whole number of boards"
    c.paint(0, ATLAS, y0 - 2, y0 + h + 2, ID_WOOD, 1.0, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, y0 - 2, y0 + h + 2)
    t = (Y - y0) / p
    board = np.floor(t).astype(np.int64)
    r = t - board                               # 0 at a board's butt, 1 at its top
    tone = 1.0 + 0.05 * (atlas.hash_unit(7, board % int(h // p)) - 0.5)
    butt = r < 1.0 / p
    c.shade[sy, sx] = tone * np.where(butt, 0.80, 1.0 - 0.06 * atlas.smoothstep(0.75, 1.0, r))
    c.ao[sy, sx] = np.where(butt, 0.78, 1.0)
    c.height[sy, sx] = LAP_TOP + (LAP_BUTT - LAP_TOP) * (1.0 - r)


def paint_brick(c):
    """Facing brick in stretcher bond: 0.25 m bricks on a 0.078125 m course.

    Both divide the atlas width and a storey's height exactly, so the bond
    repeats at the atlas wrap and across the storey handover rather than
    shifting by part of a brick. Per-brick tone is hashed from the brick's
    position modulo those periods, so the same is true of the colour variation.
    The mortar is recessed: the brick faces stand BRICK_FACE proud of it.
    """
    y0, h = BRICK_Y0, BRICK_H
    cp, bl = m(COURSE), m(0.25)
    assert ATLAS % int(bl) == 0 and int(m(Z_STOREY - Z_FLOOR)) % int(2 * cp) == 0
    c.paint(0, ATLAS, y0 - 2, y0 + h + 4, ID_BRICK, 1.0, 1.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - 2, y0 + h + 4)
    yy = Y - y0
    course = np.floor(yy / cp).astype(np.int64)
    off = np.where(course % 2 == 0, 0.0, bl / 2.0)
    brick = np.floor((X + off) / bl).astype(np.int64)
    shade = 1.0 + 0.11 * (atlas.hash_unit(3, course % 40, brick % 64) - 0.5)
    joint = ((yy - course * cp) < 1.0) | (((X + off) % bl) < 1.0)
    c.shade[sy, sx] = np.where(joint, 0.80, shade)
    c.ao[sy, sx] = np.where(joint, 0.80, 1.0)
    c.height[sy, sx] = np.where(joint, 0.0, BRICK_FACE)


def paint_vboard(c):
    """Vertical board-and-batten, 0.125 m pitch.

    Detail runs across the boards and nothing changes along them, so V is
    stretched to whatever the panel it clads is tall; see notes.md. The relief
    varies across U only, so the stretch does not distort it.
    """
    y0, h = VB_Y0, VB_H
    c.paint(0, ATLAS, y0 - 2, y0 + h + 2, ID_VBOARD, 1.0, 1.0)
    p = m(BOARD)
    sy, sx, _, X = c.field(0, ATLAS, y0 - 2, y0 + h + 2)
    board = np.floor(X / p).astype(np.int64)
    col = X - board * p
    tone = 1.0 + 0.05 * (atlas.hash_unit(11, board) - 0.5)
    gap = col < 1.0                              # the shadow beside each batten
    batten = (col >= 1.0) & (col < 3.0)
    c.shade[sy, sx] = tone * np.where(gap, 0.76, np.where(col >= p - 1.0, 0.90, 1.0))
    c.ao[sy, sx] = np.where(gap, 0.78, 1.0)
    c.height[sy, sx] = np.where(
        batten, BATTEN_H * np.clip(np.sin(np.pi * (col - 1.0) / 2.0), 0, 1) ** 0.5, 0.0)


def paint_roof(c):
    """Bitumen felt on a shallow slope: sheet laps across, a granular surface.

    The band is stretched up the slope — 12 px per metre rather than 64 — which
    is the axis a felt roof has no detail on except the laps. Recorded in
    notes.md rather than treated as free. The laps vary in V, so their height
    is scaled by the band's px/m over PPM to keep their slope physical.
    """
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0 - 2, y0 + h + 2, ID_ROOF, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - 2, y0 + h + 2)
    rpm = ROOF_H / ROOF_SLOPE_LEN
    k = rpm / PPM
    v = Y - y0
    lap = max(round(1.0 * rpm), 1)                 # sheet laps every metre
    s = v % lap
    shade = np.where(s < 1.0, 0.88, 1.0)
    height = 0.004 * k * (1.0 - s / lap)
    shade = np.where(v < 2, shade * 0.85, shade)   # drip edge at the eave
    # welted seams down the slope every 1.0 m, and the ridge capping
    seam = (X % 64.0) < 1.0
    shade = np.where(seam, shade * 0.94, shade)
    height = np.where(seam, height + 0.008, height)
    ridge = v >= h - 8
    shade = np.where(ridge, 0.96, shade)
    c.shade[sy, sx], c.height[sy, sx] = shade, height
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], np.where(s < 1.0, 0.9, 1.0))
    c.paint(0, ATLAS, y0 + h - 4, y0 + h + 2, ID_METAL, 0.92, 0.9, height=0.010 * k)


def paint_fascia(c):
    """The roof slab's edge: a painted board with a half-round gutter on it."""
    y0, h = FASC_Y0, FASC_H
    top = y0 + h
    c.paint(0, ATLAS, y0 - 2, top + 2, ID_TRIM, 1.0, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 - 2, y0 + 1, ID_TRIM, 0.86, 0.85)      # lower edge
    gh = GUTTER_PX
    g0 = top - 1 - gh
    c.paint(0, ATLAS, g0, top - 1, ID_METAL, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top - 1)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_METAL, 0.80)
    c.paint(0, ATLAS, top - 1, top + 2, ID_METAL, 0.80, height=0.0)
    c.ao[c.sl(0, ATLAS, g0 - 3, top + 2)] = 0.9
    for k, f in enumerate((0.92, 0.86, 0.80)):                   # occluded under the gutter
        c.mul(0, ATLAS, g0 - 3 + k, g0 - 2 + k, f)
    sy, sx, _, X = c.field(0, ATLAS, g0 + 2, top - 1)            # hangers every 1 m
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.80, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_soffit(c):
    """The eave underside: boarding crossed by the rafter ends the type shows.

    V runs out from the wall face, U along the wall, so the rafters land on
    their real 0.60 m spacing and the boarding between them runs out with them.
    The rafters hang below the boarding; the strip beside each is occluded.
    """
    y0, h = SOF_Y0, SOF_H
    c.paint(0, ATLAS, y0 - 2, y0 + h + 2, ID_SOFFIT, 0.92, 0.80, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - 2, y0 + h + 2)
    x = X % int(m(0.60))
    rafter = x < int(m(0.11))
    beside = (x >= int(m(0.11))) & (x < int(m(0.11)) + 1)
    v = Y - y0
    inboard = 0.80 + 0.20 * np.clip(v / (h * 0.8), 0.0, 1.0)     # darker inboard
    c.shade[sy, sx] = np.where(rafter, 0.86, np.where(beside, 0.72, 0.92)) * inboard
    c.ao[sy, sx] = np.minimum(0.62 + 0.30 * np.clip(v / (h * 0.8), 0, 1),
                              np.where(rafter, 0.72, 1.0))
    c.height[sy, sx] = np.where(
        rafter, RAFTER_H * np.clip(np.minimum(x, int(m(0.11)) - x) / 1.0, 0, 1), 0.0)


# --------------------------------------------------------------- openings
def paint_opening(c, kind):
    """One window, door or gate: casing, sill, sash frames, glass."""
    x0, y0 = ITEM_ORIGIN[kind]
    w, h, cs, cb, ct = OPENINGS[kind]
    rw, rh = item_size_px(kind)
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0 + m(cb), y0 + m(cb + h)
    # casing, bled 2 px outward so filtering at the region edge stays casing;
    # it stands proud of the wall with rounded arrises
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, ID_TRIM, 1.0, 1.0, height=0.0)
    c.bevel(x0, x0 + rw, y0, y0 + rh, CASING_H, 1.0)

    top = y0 + rh
    c.paint(x0 - 2, x0 + rw + 2, top - 3, top + 2, ID_METAL, 1.0)      # drip cap
    sy, sx, Y, _ = c.field(x0 - 2, x0 + rw + 2, top - 3, top + 2)
    c.height[sy, sx] = 0.032 - 0.012 * np.clip((Y - (top - 3)) / 3.0, 0.0, 1.0)
    c.paint(x0 - 2, x0 + rw + 2, top - 4, top - 3, ID_TRIM, 0.85, 0.8)
    c.mul(ox0 - 1, ox1 + 1, oy1, oy1 + 1, 0.82, ao=0.78)               # head shadow
    c.mul(ox0 - 1, ox0, oy0, oy1, 0.93)
    if cb > 0:                                                          # sill board
        c.paint(x0 - 2, x0 + rw + 2, y0 - 2, oy0, ID_TRIM, 1.0)
        c.bevel(x0, x0 + rw, y0, oy0, SILL_H, 1.0)
        c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + 1, ID_TRIM, 0.80, 0.8)

    if kind.startswith("door_"):
        paint_door(c, ox0, ox1, oy0, oy1, kind)
        return

    # Glass: this sets the id and the AO, and albedo then hands every pane to
    # glazing.rooms(), which owns the colour. The glass keeps a flat normal.
    f = m(0.055)                        # the dark frame round the glass
    c.paint(ox0, ox1, oy0, oy1, ID_SASH, 1.0, 1.0)
    c.bevel(ox0, ox1, oy0, oy1, SASH_H, 1.0)
    c.paint(ox0 + f, ox1 - f, oy0 + f, oy1 - f, ID_GLASS, ao=0.9, height=0.0)
    if w > 2.2:
        # the wide balcony window is a two-light unit; the mullion is a real
        # part of the frame, not a painted glazing bar
        mx = (ox0 + ox1) / 2.0
        c.paint(mx - f, mx + f, oy0, oy1, ID_SASH, 1.0, 1.0)
        c.bevel(mx - f, mx + f, oy0 + f, oy1 - f, SASH_H, 1.0, axes="x")
    c.mul(ox0 + f, ox1 - f, oy1 - f - 1, oy1 - f, 0.82, ao=0.8)
    c.mul(ox0 + f, ox0 + f + 1, oy0 + f, oy1 - f, 0.88)


def paint_door(c, x0, x1, y0, y1, kind):
    c.paint(x0, x1, y0, y1, ID_DOOR, 1.0, 1.0, height=0.0)
    if kind == "door_front":
        # a flush hardwood leaf with a tall narrow light beside the lock stile
        for xx in np.arange(x0, x1, m(0.10)):
            c.mul(xx, xx + 1, y0, y1, 0.92, ao=0.94)
            c.lift(xx, xx + 1, y0, y1, -0.002)
        gx0, gx1 = x0 + m(0.16), x0 + m(0.34)
        gy0, gy1 = y0 + m(0.82), y0 + m(1.86)
        c.paint(gx0 - 2, gx1 + 2, gy0 - 2, gy1 + 2, ID_SASH, 1.0, 0.9)
        c.bevel(gx0 - 2, gx1 + 2, gy0 - 2, gy1 + 2, SASH_H, 1.0)
        c.paint(gx0, gx1, gy0, gy1, ID_GLASS, 0.86, 0.85, height=0.0)
        c.mul(gx0, gx1, gy1 - 1, gy1, 0.80)
    else:
        # the balcony and yard doors: one big pane in a frame, solid at the foot
        f = m(0.085)
        c.paint(x0, x1, y0, y1, height=SASH_H)
        c.paint(x0 + f, x1 - f, y0 + f, y1 - f, ID_GLASS, 0.90, 0.9, height=0.0)
        c.mul(x0 + f, x1 - f, y1 - f - 1, y1 - f, 0.82, ao=0.8)
        c.mul(x0 + f, x0 + f + 1, y0 + f, y1 - f, 0.88)
        c.paint(x0, x1, y0, y0 + m(0.34), ID_DOOR, 1.0, 1.0)
        c.bevel(x0, x1, y0, y0 + m(0.34), SASH_H, 1.0)
    hx = x1 - m(0.10)
    c.paint(hx - 1, hx, y0 + m(0.92), y0 + m(1.10), ID_HANDLE, 0.9, height=0.015)
    c.paint(hx - 2, hx + 1, y0 + m(1.00), y0 + m(1.06), ID_HANDLE, 1.0, height=0.030)
    c.paint(x0, x1, y0, y0 + 2, ID_DOOR, 0.80, 0.7)                  # kick wear


def _boards(c, x0, x1, y0, y1):
    """Upright fence boards on BOARD pitch: a groove and occlusion at each gap."""
    for xx in np.arange(x0, x1, m(BOARD)):
        c.mul(xx, xx + 1, y0, y1, 0.78, ao=0.82)
        c.lift(xx, xx + 1, y0, y1, -0.005)


def _fence_bay(c, x0, y0, w, h, skip=None):
    """Boards on two rails, a post at the left edge, over the bay's full width.

    *skip* is the (s0, s1) the gate leaf occupies, left for paint_gate to fill.
    """
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_FENCE, 1.0, 1.0, height=0.0)
    _boards(c, x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2)
    for zz in (y0 + m(0.30), y0 + m(FENCE_H - 0.42)):                 # rails
        c.paint(x0 - 2, x0 + w + 2, zz, zz + m(0.11), ID_RAIL, 1.0, 1.0)
        c.bevel(x0 - 2, x0 + w + 2, zz, zz + m(0.11), RAIL_H, 1.0, axes="y")
        c.mul(x0 - 2, x0 + w + 2, zz, zz + 1, 0.86, ao=0.85)
    c.paint(x0 - 2, x0 + m(0.10), y0 - 2, y0 + h + 2, ID_RAIL, 1.0, 1.0,  # post
            height=0.030)
    c.mul(x0 + m(0.10), x0 + m(0.10) + 2, y0 - 2, y0 + h + 2, 0.80, ao=0.8)
    c.paint(x0 - 2, x0 + w + 2, y0 + h - m(0.05), y0 + h + 2, ID_RAIL, 0.94, 0.86,
            height=0.025)
    c.mul(x0 - 2, x0 + w + 2, y0 - 2, y0 + m(0.10), 0.72, ao=0.74)    # ground dirt


def paint_fence(c):
    """One 2.5 m bay of the yard fence."""
    _fence_bay(c, *FENCE)


def paint_gate(c):
    """The same bay with the gate hung in it, between two stouter posts."""
    x0, y0, w, h = GATE
    _fence_bay(c, x0, y0, w, h)
    ls, le, lh = GATE_LEAF
    gx0, gx1 = x0 + m(ls), x0 + m(le)
    gy0, gy1 = y0 + m(0.10), y0 + m(0.10 + lh)
    c.paint(gx0 - m(0.10), gx0, y0 - 2, y0 + h + 2, ID_RAIL, 1.0, 1.0, height=0.035)
    c.paint(gx1, gx1 + m(0.10), y0 - 2, y0 + h + 2, ID_RAIL, 1.0, 1.0, height=0.035)
    c.paint(gx0, gx1, y0 - 2, y0 + h + 2, ID_BLANK, 0.55, 0.5, height=-0.02)  # the gap
    c.paint(gx0, gx1, gy0, gy1, ID_FENCE, 1.0, 1.0, height=0.0)
    _boards(c, gx0, gx1, gy0, gy1)
    for zz in (gy0 + m(0.22), gy1 - m(0.34)):                            # ledgers
        c.paint(gx0, gx1, zz, zz + m(0.11), ID_RAIL, 1.0, 1.0)
        c.bevel(gx0, gx1, zz, zz + m(0.11), RAIL_H, 1.0, axes="y")
        c.mul(gx0, gx1, zz, zz + 1, 0.86, ao=0.85)
    c.mul(gx0, gx0 + 2, gy0, gy1, 0.74, ao=0.74)                         # shadow gaps
    c.mul(gx1 - 2, gx1, gy0, gy1, 0.78, ao=0.78)
    c.mul(gx0, gx1, gy1 - 2, gy1, 0.74, ao=0.76)
    hx = gx1 - m(0.12)
    c.paint(hx - 1, hx + 1, gy0 + m(0.92), gy0 + m(1.04), ID_HANDLE, 1.0, height=0.025)


def paint_patches(c):
    spec = {"reveal": (ID_TRIM, 0.68, 0.58), "blank": (ID_BLANK, 1.0, 0.5),
            "pave": (ID_PAVE, 0.96, 0.92), "post": (ID_POST, 1.0, 1.0),
            "cap": (ID_METAL, 0.94, 0.9), "tread": (ID_PLINTH, 0.98, 1.0),
            "barge": (ID_TRIM, 0.97, 1.0), "deck": (ID_WOOD, 0.9, 0.9),
            # soot inside the vents' flues: blank darkened to about sRGB 34,
            # and occluded, as a narrow shaft is whatever the sun does
            "flue": (ID_BLANK, 0.45, 0.35)}
    for name, (x0, y0, w, h) in PATCHES.items():
        mid, sh, ao = spec[name]
        c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, mid, sh, ao, height=0.0)


# ---------------------------------------------------- LOD3 painted bays
def _lod3_panel(c, x0, y0, h, s0, s1, band):
    """One vertical panel of a painted bay, at the LOD3 density."""
    l, r = x0 + s0 * PPM3, x0 + s1 * PPM3
    if band == "brick":
        c.paint(l, r, y0 - 2, y0 + h + 2, ID_BRICK, 1.0, 1.0, height=0.0)
        for k in range(1, int((h / PPM3) / (COURSE * 4)) + 1):
            zz = y0 + k * COURSE * 4 * PPM3
            c.mul(l, r, zz, zz + 1, 0.90, ao=0.92)
    elif band == "vboard":
        c.paint(l, r, y0 - 2, y0 + h + 2, ID_VBOARD, 1.0, 1.0, height=0.0)
        for s in np.arange(s0, s1 + BOARD * 0.5, BOARD * 2):
            xx = x0 + s * PPM3
            c.mul(xx, xx + 1, y0 - 2, y0 + h + 2, 0.82, ao=0.86)
    else:
        c.paint(l, r, y0 - 2, y0 + h + 2, ID_WOOD, 1.0, 1.0, height=0.0)
        for k in range(1, int((h / PPM3) / (LAP * 2)) + 1):
            zz = y0 + k * LAP * 2 * PPM3
            c.mul(l, r, zz, zz + 1, 0.86, ao=0.88)
    c.paint(l, r, y0 - 2, y0 + Z_FLOOR * PPM3, ID_PLINTH, 0.94, 0.88)


def paint_bay(c, rect, panels, items, alcove=None):
    """One dwelling bay's elevation, painted for LOD3.

    The openings are the same rectangles build.py cuts at the upper tiers, drawn
    at this region's scale, so a window does not move across the LOD2/LOD3
    switch — only its reveal goes. Flat: see the relief note above.
    """
    x0, y0, w, h = rect
    for s0, s1, band in panels:
        _lod3_panel(c, x0, y0, h, s0, s1, band)
    if alcove is not None:
        s0, s1, z0, z1, _d = alcove
        c.paint(x0 + s0 * PPM3, x0 + s1 * PPM3, y0 + z0 * PPM3, y0 + z1 * PPM3,
                ID_BLANK, 0.55, 0.42)
    for kind, s, z in items:
        ow, oh, cs, cb, ct = OPENINGS[kind]
        l, r = x0 + (s - ow / 2 - cs) * PPM3, x0 + (s + ow / 2 + cs) * PPM3
        b, t = y0 + (z - cb) * PPM3, y0 + (z + oh + ct) * PPM3
        il, ir = x0 + (s - ow / 2) * PPM3, x0 + (s + ow / 2) * PPM3
        ib, it = y0 + z * PPM3, y0 + (z + oh) * PPM3
        c.paint(l, r, b, t, ID_TRIM, 1.0, 1.0)
        c.mul(l, r, t - 1, t, 0.78, ao=0.8)
        if kind == "door_front":
            c.paint(il, ir, ib, it, ID_DOOR, 0.86, 0.8)
        elif kind == "door_glazed":
            c.paint(il, ir, ib, it, ID_SASH, 1.0, 1.0)
            c.paint(il + 1, ir - 1, y0 + (z + 0.34) * PPM3, it - 1, ID_GLASS, 0.90, 0.9)
        else:
            c.paint(il, ir, ib, it, ID_SASH, 1.0, 1.0)
            c.paint(il + 1, ir - 1, ib + 1, it - 1, ID_GLASS, 0.92, 0.9)
            c.mul(il + 1, ir - 1, it - 2, it - 1, 0.84, ao=0.8)


# ------------------------------------------------------------------ checks
def check_regions():
    """Fail the bake if two unique regions overlap or run off the atlas."""
    rects = {k: (ITEM_ORIGIN[k][0], ITEM_ORIGIN[k][1]) + item_size_px(k)
             for k in OPENINGS}
    rects["fence"] = FENCE
    rects["gate"] = GATE
    rects["lod3_front"] = LOD3_FRONT
    rects["lod3_rear"] = LOD3_REAR
    rects.update(PATCHES)
    names = sorted(rects)
    problems = []
    for i, a in enumerate(names):
        ax, ay, aw, ah = rects[a]
        if ax - 2 < 0 or ay - 2 < 0 or ax + aw + 2 > ATLAS or ay + ah + 2 > ATLAS:
            problems.append("%s runs off the atlas" % a)
        for b in names[i + 1:]:
            bx, by, bw, bh = rects[b]
            if (ax - 4 < bx + bw and bx - 4 < ax + aw
                    and ay - 4 < by + bh and by - 4 < ay + ah):
                problems.append("%s and %s overlap" % (a, b))
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    WOOD and BRICK are sampled from each storey's own foot, so anything that
    follows height there would repeat at the upper floor: ground splash stays
    on the plinth band, whose V is height from the ground on every wall."""
    w = weathering.Weather(c, clean=(ID_GLASS,), steel=(ID_ROOF, ID_METAL, ID_POST))
    w.grime()
    w.fade((ID_WOOD, ID_VBOARD, ID_TRIM, ID_SASH, ID_DOOR, ID_FENCE, ID_RAIL, ID_SOFFIT))
    w.wash((ID_WOOD, ID_VBOARD, ID_BRICK))
    w.plinth(0, ATLAS, PLINTH_Y0, PLINTH_Y0 + m(Z_FLOOR), (ID_PLINTH,))
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, ROOF_SLOPE_LEN, (ID_ROOF,))
    # the fascia: runs down the board from the gutter, a dirty belly
    g0 = FASC_Y0 + FASC_H - 9.0
    w.add("D", 0, ATLAS, FASC_Y0 - 2, g0, 0.06, (ID_TRIM,))
    w.runs(0, ATLAS, FASC_Y0 - 2, g0, (ID_TRIM,), 0.22, fall=6.0, lo=0.4, hi=1.6)
    w.add("D", 0, ATLAS, g0, g0 + 4, lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"), (ID_METAL,))
    # dust on the soffit boarding next to the wall, where no wind clears it
    w.add("D", 0, ATLAS, SOF_Y0 - 2, SOF_Y0 + SOF_H + 2, lambda Y, X, nz: 0.08 * np.exp(
        -np.clip(Y - SOF_Y0, 0.0, None) / 12.0) * (0.6 + 0.4 * nz("blotch")), (ID_SOFFIT,))
    # openings: sills, heads and bottom rails; doors' handles and feet
    for kind, (wd, h, cs, cb, ct) in OPENINGS.items():
        x0, yb = ITEM_ORIGIN[kind]
        rw, rh = item_size_px(kind)
        ox0, ox1 = x0 + m(cs), x0 + m(cs + wd)
        oy0, oy1 = yb + m(cb), yb + m(cb + h)
        if kind.startswith("door"):
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR,), handle=(ox1 - m(0.10), oy0 + m(1.03)))
        else:
            w.window(x0, yb, rw, rh, oy0, oy1, m(0.055), (ID_TRIM,), (ID_SASH,))
    # the fence bays: splashed at the foot; the gate leaf's handle
    for x0, y0, fw, fh in (FENCE, GATE):
        w.splash(x0 - 2, x0 + fw + 2, y0, y0 + fh + 2, (ID_FENCE, ID_RAIL))
    ls, le, lh = GATE_LEAF
    w.spot(GATE[0] + m(le) - m(0.12), GATE[1] + m(0.10 + 0.98), m(0.08), (ID_FENCE, ID_RAIL))
    # the LOD3 bays' plinths, at their own 14 px/m
    for x0, y0, bw, bh in (LOD3_FRONT, LOD3_REAR):
        w.plinth(x0 - 2, x0 + bw + 2, y0, y0 + Z_FLOOR * PPM3, (ID_PLINTH,), ppm=PPM3)
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_plinth(c)
    paint_wood(c)
    paint_brick(c)
    paint_vboard(c)
    paint_roof(c)
    paint_fascia(c)
    paint_soffit(c)
    for kind in OPENINGS:
        paint_opening(c, kind)
    paint_fence(c)
    paint_gate(c)
    paint_bay(c, LOD3_FRONT, FRONT_PANELS, FRONT_UNIT)
    paint_bay(c, LOD3_REAR, REAR_GF_PANELS,
              REAR_GF_UNIT + REAR_UP_UNIT, alcove=ALCOVE)
    paint_patches(c)
    c.check_bands(BAND_IDS)

    # Weathering. Every field is periodic, so the bands still wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    lapped = np.isin(c.mid, (ID_WOOD, ID_SOFFIT, ID_DOOR))
    grain = atlas.noise(c, 5, 60.0, 0.35)            # along the laps
    c.shade[lapped] *= 1.0 + 0.02 * grain[lapped]
    c.height[lapped] += 0.0003 * grain[lapped]
    upright = np.isin(c.mid, (ID_VBOARD, ID_FENCE, ID_RAIL))
    vgrain = atlas.noise(c, 10, 0.35, 60.0)          # along the upright boards
    c.shade[upright] *= 1.0 + 0.018 * vgrain[upright]
    c.height[upright] += 0.0003 * vgrain[upright]
    weathered = np.isin(c.mid, (ID_ROOF, ID_BRICK, ID_PLINTH, ID_PAVE))
    streak = atlas.noise(c, 7, 0.8, 40.0)            # rain runs down
    c.shade[weathered] *= 1.0 + 0.028 * streak[weathered]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_PAVE))
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
    wood = np.array(pal["wood"], np.float32)
    t[ID_WOOD] = wood
    t[ID_VBOARD] = np.clip(wood * 1.06, 0, 255)
    t[ID_SOFFIT] = np.clip(wood * 0.94 + 10, 0, 255)
    t[ID_BRICK] = pal["brick"]
    t[ID_ROOF] = pal["roof"]
    t[ID_TRIM] = t[ID_SASH] = pal["trim"]
    t[ID_METAL] = np.clip(np.array(pal["trim"], np.float32) * 1.30 + 22, 0, 255)
    t[ID_DOOR] = pal["door"]
    t[ID_FENCE] = pal["fence"]
    t[ID_RAIL] = np.clip(np.array(pal["fence"], np.float32) * 0.62, 0, 255)
    return t


def export(out_dir, ss=atlas.SS):
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.012)
    c.weather.dust(cav, (ID_WOOD, ID_VBOARD, ID_BRICK, ID_FENCE))  # laps, joints
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
