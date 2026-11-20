# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas for navetta_board_gable, and the
layout build.py maps into.

This describes one asset and nothing else, so it lives beside build.py rather
than in scripts/. It is also the single source of the numbers the two files
share: build.py imports the z-levels, opening sizes and region rects from here
instead of writing them a second time, so the pixel layout and the UVs cannot
drift apart. Importing this module only defines those constants; the painting
runs when paint() is called. Rasterising is scripts/atlas.py's.

    python3 facade_atlas.py export      # writes every map into ./export

The atlas is a trim sheet: the walls sample tiling bands and every opening
samples a region of its own, which carries its casing as well as its leaf or
glazing.

    y    0 ..  256   S1      lower walls, z 0 .. 3.97: concrete plinth,
                             drip flashing, vertical board-and-batten
    y  258 ..  448   S2      gable triangles, z 3.80 .. 6.70: belt board,
                             board-and-batten
    y  452 ..  772   ROOF    trapezoidal profiled steel, V stretched up the slope,
                             with the snow guard a short way up from the eave
    y  774 ..  798   FASCIA  fascia board with its half-round gutter
    y  802 .. 1010   unique  the big door pair, the plank door, the loft hatch,
                             the byre window, the gable vent, the corner-board
                             strip, flat patches

S1, S2, ROOF and FASCIA span the full width and tile in U. Board-and-batten
varies along U only (battens every 0.25 m), so it tiles at any wall length,
and V stays height above the ground: plinth splash and the sheltered eave
land the same on every wall.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "navetta_board_gable"
ATLAS = 1024
PPM = 64.0

# --------------------------------------------------------- vertical layout
# Metres above ground, shared by every wall.
Z_FLOOR = 0.40       # cast-concrete plinth top = byre floor; door thresholds
Z_FLASH = 0.45       # top of the drip flashing; boards and corner boards begin
Z_EAVE = 3.80        # long walls meet the soffit; gable boarding begins
Z_WALL_TOP = 3.90    # walls run on up into the roof slab, which trims them
BELT_H = 0.1875      # belt board across the foot of each gable (12 px)
CW = 0.15625         # corner-board width (10 px)
S2_TOP = 6.70        # gable band reaches this high; build.py asserts the apex fits

BATTEN_PITCH = 0.25  # one board and its batten (16 px, divides the atlas)
BATTEN_PX = 3.0      # batten width, ~47 mm
RIB_PITCH = 16.0     # roof sheet's trapezoidal ribs, px along U (0.25 m)

# ------------------------------------------------------------- openings
# kind -> (width, height, casing side, casing bottom, casing top), metres.
# Width and height are the clear opening: the door leaf or the glazed sash.
# Casings are painted, never modelled. Doors and the hatch have no bottom
# casing: the leaf runs down to the threshold.
OPENINGS = {
    "bigdoor": (3.20, 3.00, 0.15625, 0.0, 0.1875),
    "door": (0.95, 2.10, 0.125, 0.0, 0.1875),
    "hatch": (1.20, 1.40, 0.125, 0.0, 0.1875),
    "window": (1.00, 0.70, 0.125, 0.125, 0.1875),
    "window_b": (1.00, 0.70, 0.125, 0.125, 0.1875),
    "vent": (0.60, 0.40, 0.0625, 0.0625, 0.0625),
}
# Leaves per door-like opening; the leaves are painted board doors.
LEAVES = {"bigdoor": 2, "door": 1, "hatch": 2}
# Recess from the wall face to the glass or leaf. A board wall sets its
# frames near the outside face; see notes.md.
REVEAL_DEPTH = {"vent": 0.08}
REVEAL_DEFAULT = 0.12

# ------------------------------------------------------------ atlas bands
S1_Y0 = 2.0          # v of z = 0
S2_Y0 = 262.0        # v of z = Z_EAVE
ROOF_Y0, ROOF_H = 454.0, 316.0
# Roof slope, fascia top to ridge, in metres; build.py asserts it.
ROOF_SLOPE_LEN = 5.716
FASC_Y0 = 776.0      # v of the fascia's bottom edge
FASC_H = 20.0        # = the roof slab's 0.3125 m vertical thickness
GUTTER_PX = 9.0      # the gutter's rows, hung across the fascia's top
# The downpipes' sides span the middle five of them (scripts/downpipes.py)
PIPE_STRIP = (FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 - 2.5,
              FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 + 2.5)
# The snow guard's lower tube, in metres up the slope from the eave's edge:
# just inside the wall line (the 0.45 m eave is 0.52 m of slope), where its
# brackets bear on the rafters over the wall.
SNOW_GUARD = 0.60
UNI_Y0 = 804.0

# Region origins: the bottom-left of each opening's casing, in pixels.
ITEM_ORIGIN = {
    "bigdoor": (4.0, UNI_Y0),
    "door": (238.0, UNI_Y0),
    "hatch": (324.0, UNI_Y0),
    "window": (430.0, UNI_Y0),
    "window_b": (515.0, UNI_Y0),
    "vent": (426.0, UNI_Y0 + 76.0),
}
# Two regions for the one byre window, so neighbouring windows show two
# different rooms. glazing.rooms() seeds each pane from its box in the atlas;
# these two origins were picked so both rooms land mid-band (levels 1.09 and
# 1.06 of glazing.BASE), where the first single region drew 0.75 and measured
# under the 45-70 band. See notes.md, Glazing treatment.
CORNER = (604.0, UNI_Y0, 10.0, 64.0)        # corner-board strip, V stretched
PATCHES = {name: (624.0 + 14.0 * i, UNI_Y0, 8.0, 8.0) for i, name in enumerate(
    ("trim", "soffit", "reveal", "blank", "tread", "barge"))}


def item_size_px(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    return (w + 2.0 * cs) * PPM, (h + cb + ct) * PPM


# ----------------------------------------------------------- material ids
ID_WALL, ID_TRIM, ID_SASH, ID_GLASS, ID_PLINTH, ID_METAL = 0, 1, 2, 3, 4, 5
ID_ROOF, ID_DOOR, ID_BLANK, ID_IRON = 6, 7, 8, 9
ID_GUTTER = 10       # gutter, downpipes and snow guard: galvanised steel
# (roughness, metallic). The rainwater goods and the snow guard are the farm
# buildings' one galvanised steel, the same in every variant and on
# viljakuivuri_tower and konehalli_open_bays: sRGB (134, 137, 137), dulled by
# its zinc patina, part metallic.
SURFACE = {
    ID_WALL: (0.82, 0.0), ID_TRIM: (0.62, 0.0), ID_SASH: (0.52, 0.0),
    ID_GLASS: (glazing.ROUGHNESS, 0.0), ID_PLINTH: (0.90, 0.0),
    ID_METAL: (0.42, 0.30), ID_ROOF: (0.46, 0.25), ID_DOOR: (0.78, 0.0),
    ID_BLANK: (0.95, 0.0), ID_IRON: (0.55, 0.45), ID_GUTTER: (0.48, 0.60),
}

# ---------------------------------------------------------------- palettes
# Muted farm paints. Red ochre (punamulta) and yellow ochre with white trim,
# and unpainted boards gone silver-grey with darker weathered trim. The doors
# are boarded like the walls and painted with them, a shade darker; the roof
# is dark steel and shifts a little with the body colour; the drip flashing
# and drip caps follow it. The gutter, downpipes and snow guard do not: they
# are galvanised in every variant (ID_GUTTER).
VARIANTS = {
    "red_ochre": {"wall": (120, 52, 42), "trim": (220, 216, 204),
                  "roof": (54, 56, 58), "door": (108, 47, 39)},
    "grey_weathered": {"wall": (106, 102, 95), "trim": (74, 69, 62),
                       "roof": (60, 60, 59), "door": (94, 89, 82)},
    "yellow_ochre": {"wall": (178, 142, 84), "trim": (220, 216, 202),
                     "roof": (74, 50, 44), "door": (162, 128, 76)},
}
DEFAULT_VARIANT = "red_ochre"
FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (146, 144, 138),
    ID_BLANK: (52, 52, 52), ID_IRON: (60, 58, 56), ID_GUTTER: (134, 137, 137),
}

# Which ids each tiling band may contain.
BAND_IDS = {
    "S1": ((0, 256), {ID_PLINTH, ID_METAL, ID_WALL}),
    "S2": ((258, 448), {ID_TRIM, ID_WALL}),
    "ROOF": ((452, 772), {ID_ROOF, ID_GUTTER}),
    "FASCIA": ((774, 798), {ID_METAL, ID_TRIM, ID_GUTTER}),
}

# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto.
BATTEN_H = 0.020     # battens proud of the boards
CASING_H = 0.020     # casings, frames and the corner board
SILL_H = 0.035       # sill board, proud of the casing
SASH_H = 0.012       # sash frame, proud of the glass
FRAME_H = 0.022      # the door leaves' frame and brace boards
HINGE_H = 0.028      # strap hinges on the frame
RIB_H = 0.022        # the roof sheet's trapezoidal ribs
GUTTER_R = 0.070     # half-round gutter's radius
TUBE_H = 0.045       # snow-guard tubes, over the sheet's pans
GUARD_BRACKET_H = 0.040  # snow-guard brackets, on the rib crests


# ============================================================ painting
def m(v):
    """Metres -> pixels."""
    return v * PPM


def paint_boards(c, y_lo, y_hi, seed):
    """Vertical board-and-batten across the full width.

    Every BATTEN_PITCH a batten BATTEN_PX wide stands BATTEN_H proud over the
    joint between two boards, its arrises rounded over a pixel so they catch
    the sun; the inside corner either side of it is an occlusion line. Each
    board and each batten has its own tone, hashed from its column, and the
    columns repeat every 1024 px, so the band wraps.
    """
    p = m(BATTEN_PITCH)
    assert ATLAS % int(p) == 0
    cols = int(ATLAS // p)
    sy, sx, Y, X = c.field(0, ATLAS, y_lo, y_hi)
    col = np.floor(X / p).astype(np.int64)
    xm = X - col * p
    batten = xm < BATTEN_PX
    board_tone = 1.0 + 0.07 * (atlas.hash_unit(seed, col % cols) - 0.5)
    batten_tone = 1.0 + 0.05 * (atlas.hash_unit(seed + 1, col % cols) - 0.5)
    d = np.minimum(xm, BATTEN_PX - xm)
    height = np.where(batten, BATTEN_H * np.clip(d / 0.9, 0.0, 1.0), 0.0)
    corner = (~batten) & ((xm < BATTEN_PX + 1.0) | (xm > p - 1.0))
    shade = np.where(batten, batten_tone, board_tone)
    shade = np.where(corner, shade * 0.88, shade)
    c.mid[sy, sx] = ID_WALL
    c.shade[sy, sx] = shade
    c.ao[sy, sx] = np.where(corner, 0.84, 1.0)
    c.height[sy, sx] = height


def paint_s1(c):
    y0 = S1_Y0
    # cast-concrete plinth, with the bleed rows under z = 0 painted the same
    c.paint(0, ATLAS, 0, y0 + m(Z_FLOOR), ID_PLINTH, 1.0, height=0.0)
    zz = y0 + m(0.20)                                   # one formwork lift line
    c.mul(0, ATLAS, zz, zz + 1, 0.93)
    c.lift(0, ATLAS, zz, zz + 1, -0.002)
    sy, sx, Y, _ = c.field(0, ATLAS, 0, y0 + m(Z_FLOOR))
    z = (Y - y0) / PPM
    c.shade[sy, sx] *= 0.82 + 0.18 * np.clip(z / 0.30, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.86 + 0.14 * np.clip(z / 0.30, 0, 1))
    c.mul(0, ATLAS, y0 + m(Z_FLOOR) - 2, y0 + m(Z_FLOOR), 0.86, ao=0.80)
    # drip flashing: a folded sheet over the plinth's top, its lip shadowed
    fy0, fy1 = y0 + m(Z_FLOOR), y0 + m(Z_FLASH)
    c.paint(0, ATLAS, fy0, fy1, ID_METAL, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, fy0, fy1)
    c.height[sy, sx] = 0.022 - 0.010 * (Y - fy0) / (fy1 - fy0)
    c.paint(0, ATLAS, fy0, fy0 + 1, ID_METAL, 0.80)
    paint_boards(c, fy1, 256, seed=11)
    # the boards' sawn feet, just over the flashing
    c.mul(0, ATLAS, fy1, fy1 + 1, 0.86, ao=0.85)
    # shade under the soffit / the gable belt board
    for k, f in enumerate((0.84, 0.90, 0.95)):
        yy = y0 + m(Z_EAVE) - 1 - k
        c.mul(0, ATLAS, yy, yy + 1, f, ao=0.8 + 0.06 * k)


def paint_s2(c):
    y0 = S2_Y0
    bt = y0 + m(BELT_H)
    c.paint(0, ATLAS, y0 - 4, bt, ID_TRIM, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, bt, CASING_H, 1.0, axes="y")
    c.mul(0, ATLAS, y0 - 4, y0 + 1, 0.85)
    paint_boards(c, bt, 448, seed=29)
    c.mul(0, ATLAS, bt, bt + 2, 0.86, ao=0.82)          # under the belt's drip


def paint_roof(c):
    """Trapezoidal profiled steel, ribs every RIB_PITCH px running down the
    slope, V stretched (ROOF_H rows over ROOF_SLOPE_LEN metres). Ribs vary in
    U only; relief that varies in V is scaled by the band's px/m over PPM so
    the slope the normal map derives from stays physical.

    The snow guard is two round tubes across the whole band, on brackets
    through every second rib's crest (0.5 m apart, a period that divides the
    atlas), in the gutter's galvanised steel (ID_GUTTER) as a matched
    system."""
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0 - 2, y0 + h + 2, ID_ROOF, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - 2, y0 + h + 2)
    xm = X % RIB_PITCH
    rib = np.clip(np.minimum(xm / 1.5, (5.0 - xm) / 1.5), 0.0, 1.0)
    height = RIB_H * rib
    foot = ((xm >= 5.0) & (xm < 6.0)) | (xm >= RIB_PITCH - 0.5)
    shade = np.where(foot, 0.93, 1.0)
    ao = np.where(foot, 0.86, 1.0)
    # a shallow stiffening flute mid-pan
    flute = (xm >= 10.0) & (xm < 11.0)
    height = np.where(flute, height - 0.002, height)
    k = (ROOF_H / ROOF_SLOPE_LEN) / PPM
    v = Y - y0
    shade = np.where(v < 3, shade * 0.85, shade)                    # eave drip edge
    # snow guard
    g = round(SNOW_GUARD * ROOF_H / ROOF_SLOPE_LEN)
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
    xb = X % (2.0 * RIB_PITCH)
    bracket = (xb >= 1.5) & (xb < 3.5) & (v >= g - 3) & (v < g + 4.5)
    height = np.where(bracket, GUARD_BRACKET_H * k, height)
    shade = np.where(bracket, 0.75, shade)
    guard |= bracket
    ridge = v >= h - 12
    height = np.where(ridge, 0.010 * k + 0.4 * height, height)      # ridge flashing
    shade = np.where(ridge, 0.97, shade)
    shade = np.where((v >= h - 12) & (v < h - 11), shade * 0.85, shade)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao
    c.mid[sy, sx] = np.where(guard, ID_GUTTER, ID_ROOF)


def paint_fascia(c):
    """The eave's vertical edge: a fascia board in the trim colour, with a
    half-round steel gutter hung across its top, under the roof sheet's drip
    edge, as on rintamamiestalo_porch.

    The band's top row is the roof's edge, where the water leaves the roof,
    so the gutter sits right under it and the board shows below. The gutter
    is ID_GUTTER, galvanised in every variant, and so are the downpipes that
    sample its rows and the snow guard: a matched rainwater system. The drip
    edge above it is the roof's flashing (ID_METAL).
    """
    y0 = FASC_Y0
    top = y0 + FASC_H                       # the roof's edge
    c.paint(0, ATLAS, y0 - 2, top + 2, ID_TRIM, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 - 2, y0 + 1, ID_TRIM, 0.88)      # board's lower edge
    # half-round gutter: belly at the bottom, rolled lip at the top. Its roll
    # is height; only the belly's underside is darker.
    gh = GUTTER_PX
    g0 = top - 1 - gh
    c.paint(0, ATLAS, g0, top - 1, ID_GUTTER, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top - 1)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_GUTTER, 0.80)
    c.paint(0, ATLAS, top - 1, top + 2, ID_METAL, 0.80, height=0.0)  # roof sheet's drip edge
    c.ao[c.sl(0, ATLAS, g0 - 3, top + 2)] = 0.9
    for k, f in enumerate((0.92, 0.86, 0.80)):            # occluded under the gutter
        c.mul(0, ATLAS, g0 - 3 + k, g0 - 2 + k, f)
    # hangers every 1.0 m, a spacing that divides the atlas width
    sy, sx, _, X = c.field(0, ATLAS, g0 + 2, top - 1)
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.80, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_leaves(c, x0, x1, y0, y1, n):
    """Board door leaves: vertical planks with V-grooves, a frame and a
    diagonal brace in the trim colour, black strap hinges on the hinge stile
    and an iron handle on the latch side. A leaf over 2.5 m tall gets a mid
    rail and a brace in each half."""
    c.paint(x0, x1, y0, y1, ID_DOOR, 1.0, 1.0, height=0.0)
    lw = (x1 - x0) / n
    fr = m(0.11)
    tall = (y1 - y0) > m(2.5)
    for i in range(n):
        a0, a1 = x0 + i * lw, x0 + (i + 1) * lw
        hinge_left = (i == 0)
        for xx in np.arange(a0 + m(0.13), a1 - 2, m(0.13)):
            c.mul(xx, xx + 1, y0, y1, 0.82, ao=0.8)
            c.lift(xx, xx + 1, y0, y1, -0.003)
        rails = [(y0, y0 + fr), (y1 - fr, y1)]
        bays = [(y0 + fr, y1 - fr)]
        if tall:
            ym = (y0 + y1) / 2.0
            rails.append((ym - fr / 2.0, ym + fr / 2.0))
            bays = [(y0 + fr, ym - fr / 2.0), (ym + fr / 2.0, y1 - fr)]
        # brace up from the hinge side's foot to the latch side's head
        for b0, b1 in bays:
            p0 = (a0 + fr, b0) if hinge_left else (a1 - fr, b0)
            p1 = (a1 - fr, b1) if hinge_left else (a0 + fr, b1)
            c.stroke(p0, p1, fr * 0.9, mid=ID_TRIM, shade=1.0, height=FRAME_H)
        for r0, r1 in rails:
            c.paint(a0, a1, r0, r1, ID_TRIM, 1.0, 1.0)
            c.bevel(a0, a1, r0, r1, FRAME_H, 1.0)
            c.mul(a0, a1, r0 - 1, r0, 0.86, ao=0.8)                 # under a rail
        for s0, s1 in ((a0, a0 + fr), (a1 - fr, a1)):
            c.paint(s0, s1, y0, y1, ID_TRIM, 1.0, 1.0)
            c.bevel(s0, s1, y0, y1, FRAME_H, 1.0)
        # strap hinges, iron, on the hinge stile and out across the rails
        hx0 = a0 if hinge_left else a1 - m(0.50)
        hx1 = hx0 + m(0.50)
        for r0, r1 in rails:
            yc = (r0 + r1) / 2.0
            c.paint(hx0, hx1, yc - 2.0, yc + 2.0, ID_IRON, 1.0, 0.9, height=HINGE_H)
            c.mul(hx0, hx1, yc - 3.0, yc - 2.0, 0.85, ao=0.8)
    if n == 2:                                    # the meeting stiles' joint
        xc = (x0 + x1) / 2.0
        c.paint(xc - 0.5, xc + 0.5, y0, y1, ID_DOOR, 0.45, 0.5, height=-0.004)
    # handle: an iron grip on the latch stile at hand height
    hx = (x0 + x1) / 2.0 - m(0.06) if n == 2 else x1 - m(0.06)
    hy = y0 + m(1.0) if (y1 - y0) > m(1.8) else y0 + m(0.55)
    c.paint(hx - 1.0, hx + 1.0, hy, hy + m(0.28), ID_IRON, 1.0, 0.9, height=FRAME_H + 0.025)
    c.mul(x0, x1, y0, y0 + 2, 0.8, ao=0.7)                          # kick wear


def paint_opening(c, kind):
    """One opening's region: casing, drip cap and sill, then its leaves,
    louvres or sash and glass."""
    x0, y0 = ITEM_ORIGIN[kind]
    w, h, cs, cb, ct = OPENINGS[kind]
    rw, rh = item_size_px(kind)
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0 + m(cb), y0 + m(cb + h)
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, ID_TRIM, 1.0, 1.0, height=0.0)
    c.bevel(x0, x0 + rw, y0, y0 + rh, CASING_H, 1.0)
    if kind != "vent":
        top = y0 + rh
        # drip cap: sheet steel over the head casing, sloping out
        c.paint(x0 - 2, x0 + rw + 2, top - 3, top + 2, ID_METAL, 1.0)
        sy, sx, Y, _ = c.field(x0 - 2, x0 + rw + 2, top - 3, top + 2)
        c.height[sy, sx] = 0.032 - 0.012 * np.clip((Y - (top - 3)) / 3.0, 0.0, 1.0)
        c.paint(x0 - 2, x0 + rw + 2, top - 4, top - 3, ID_TRIM, 0.85, 0.8)
        c.mul(ox0 - 1, ox1 + 1, oy1, oy1 + 1, 0.84, ao=0.8)             # head shadow
        c.mul(ox0 - 1, ox0, oy0, oy1, 0.93)
        if cb > 0:                                                       # sill board
            c.paint(x0 - 2, x0 + rw + 2, y0 - 2, oy0, ID_TRIM, 1.0)
            c.bevel(x0, x0 + rw, y0, oy0, SILL_H, 1.0)
            c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + 1, ID_TRIM, 0.80, 0.8)

    if kind in LEAVES:
        paint_leaves(c, ox0, ox1, oy0, oy1, LEAVES[kind])
        return
    if kind == "vent":
        c.paint(ox0, ox1, oy0, oy1, ID_TRIM, 0.62, 0.6, height=-0.010)
        for yy in np.arange(oy0, oy1, 3.0):
            # louvre blades, sloping out and down to shed rain
            c.paint(ox0, ox1, yy, yy + 2, ID_TRIM, 1.0, 0.9)
            sy, sx, Y, _ = c.field(ox0, ox1, yy, yy + 2)
            c.height[sy, sx] = 0.020 * (1.0 - (Y - yy) / 2.0)
            c.paint(ox0, ox1, yy, yy + 1, ID_TRIM, 0.85, 0.8)
        return

    # The byre window: one plain pane in a sash frame. Glass sets the id and
    # the AO; glazing.rooms() owns its colour.
    f = m(0.0625)
    c.paint(ox0, ox1, oy0, oy1, ID_SASH, 1.0, 1.0)
    c.bevel(ox0, ox1, oy0, oy1, SASH_H, 1.0)
    c.paint(ox0 + f, ox1 - f, oy0 + f, oy1 - f, ID_GLASS, ao=0.9, height=0.0)
    c.mul(ox0 + f, ox1 - f, oy1 - f - 1, oy1 - f, 0.82, ao=0.8)
    c.mul(ox0 + f, ox0 + f + 1, oy0 + f, oy1 - f, 0.88)


def paint_corner(c):
    x0, y0, w, h = CORNER
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_TRIM, 1.0, height=0.0)
    c.bevel(x0, x0 + w, y0 - 2, y0 + h + 2, CASING_H, 1.0, axes="x")
    c.mul(x0 - 2, x0 + w + 2, y0 - 2, y0 + 3, 0.92)


def paint_patches(c):
    spec = {"trim": (ID_TRIM, 1.0, 1.0), "soffit": (ID_TRIM, 0.86, 0.85),
            "reveal": (ID_TRIM, 0.70, 0.6), "blank": (ID_BLANK, 1.0, 0.5),
            "tread": (ID_PLINTH, 0.96, 1.0), "barge": (ID_TRIM, 0.97, 1.0)}
    for name, (x0, y0, w, h) in PATCHES.items():
        mid, sh, ao = spec[name]
        c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, mid, sh, ao, height=0.0)


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    S1's and S2's V is height above the ground and the roof band's is slope,
    so splash, the sheltered eave and the dirtier eave land the same on every
    wall and both roof faces."""
    w = weathering.Weather(c, clean=(ID_GLASS,),
                           steel=(ID_ROOF, ID_METAL, ID_IRON, ID_GUTTER))
    w.grime()
    w.fade((ID_WALL, ID_TRIM, ID_SASH, ID_DOOR))
    w.wash((ID_WALL,))
    w.plinth(0, ATLAS, S1_Y0, S1_Y0 + m(Z_FLOOR), (ID_PLINTH,))
    w.add("D", 0, ATLAS, S1_Y0 + m(Z_FLOOR), S1_Y0 + m(Z_FLASH),
          lambda Y, X, nz: 0.10 * nz("blotch"), (ID_METAL,))
    w.splash(0, ATLAS, S1_Y0 + m(Z_FLASH), 257, (ID_WALL,))
    w.shelter(0, ATLAS, S1_Y0 + m(3.3), S1_Y0 + m(Z_EAVE), (ID_WALL,), top=257)
    roof = (ID_ROOF,)
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, ROOF_SLOPE_LEN, roof)
    w.add("D", 0, ATLAS, ROOF_Y0 - 2, ROOF_Y0 + ROOF_H + 2, lambda Y, X, nz: 0.10 * (
        ((X % RIB_PITCH) >= 5.0) & ((X % RIB_PITCH) < 7.0)), roof)
    w.add("R", 0, ATLAS, ROOF_Y0 - 2, ROOF_Y0 + 3, lambda Y, X, nz: 0.12 * nz("speck"), roof)
    # the snow guard: light dust on it (with grime(), 0.06 + 0.08 blotch, as on
    # the farm's other two), rust at its brackets, debris held above it and
    # short rust runs on the sheet under the brackets
    g = ROOF_Y0 + round(SNOW_GUARD * ROOF_H / ROOF_SLOPE_LEN)

    def bk(X):
        return ((X % (2.0 * RIB_PITCH)) >= 1.0) & ((X % (2.0 * RIB_PITCH)) < 4.0)

    w.add("D", 0, ATLAS, g + 4.5, g + 16.0, lambda Y, X, nz: 0.25 * nz("blotch")
          * (1.0 - (Y - g - 4.5) / 11.5), roof)
    w.add("D", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.06 + 0.045 * nz("blotch"),
          (ID_GUTTER,))
    w.add("R", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.15 * (
        ((X % (2.0 * RIB_PITCH)) >= 1.5) & ((X % (2.0 * RIB_PITCH)) < 3.5)), (ID_GUTTER,))
    w.add("R", 0, ATLAS, g - 14, g - 3, lambda Y, X, nz: 0.15 * bk(X)
          * (1.0 - (g - 3 - Y) / 11.0) * atlas.smoothstep(-0.5, 0.8, nz("runs")), roof)
    # the fascia: runs down the board from the gutter; the gutter's dirty
    # belly and light runs down its face from the lip, the same treatment as
    # the farm's other two gutters
    top = FASC_Y0 + FASC_H
    g0 = top - 1 - GUTTER_PX
    w.add("D", 0, ATLAS, FASC_Y0 - 2, g0, 0.06, (ID_TRIM,))
    w.runs(0, ATLAS, FASC_Y0 - 2, g0, (ID_TRIM,), 0.22, fall=6.0, lo=0.4, hi=1.6)
    w.add("D", 0, ATLAS, g0, g0 + 4, lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"),
          (ID_GUTTER,))
    w.runs(0, ATLAS, g0, top - 1, (ID_GUTTER,), 0.08, fall=4.0, lo=0.4, hi=1.6)
    for kind, (wd, h, cs, cb, ct) in OPENINGS.items():
        if kind == "vent":
            continue
        x0, yb = ITEM_ORIGIN[kind]
        rw, rh = item_size_px(kind)
        ox0, ox1 = x0 + m(cs), x0 + m(cs + wd)
        oy0, oy1 = yb + m(cb), yb + m(cb + h)
        if kind in LEAVES:
            hx = (ox0 + ox1) / 2.0 if LEAVES[kind] == 2 else ox1 - m(0.06)
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR, ID_TRIM), handle=(hx, oy0 + m(1.1)))
        else:
            w.window(x0, yb, rw, rh, oy0, oy1, m(0.0625), (ID_TRIM,), (ID_SASH,))
    kx0, ky0, kw, kh = CORNER
    w.add("D", kx0 - 2, kx0 + kw + 2, ky0 - 2, ky0 + kh + 2, lambda Y, X, nz: 0.22
          * np.exp(-np.clip(Y - ky0, 0.0, None) / 4.0), (ID_TRIM,))
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_s1(c)
    paint_s2(c)
    paint_roof(c)
    paint_fascia(c)
    for kind in OPENINGS:
        paint_opening(c, kind)
    paint_corner(c)
    paint_patches(c)
    c.check_bands(BAND_IDS)

    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    wall = c.mid == ID_WALL
    grain = atlas.noise(c, 5, 0.35, 50.0)            # grain along the vertical boards
    c.shade[wall] *= 1.0 + 0.03 * grain[wall]
    c.height[wall] += 0.0003 * grain[wall]
    trim = np.isin(c.mid, (ID_TRIM, ID_DOOR))
    tgrain = atlas.noise(c, 6, 40.0, 0.35)
    c.shade[trim] *= 1.0 + 0.015 * tgrain[trim]
    roof = c.mid == ID_ROOF
    streak = atlas.noise(c, 7, 0.8, 40.0)            # rain runs down the slope
    c.shade[roof] *= 1.0 + 0.035 * streak[roof]
    concrete = c.mid == ID_PLINTH
    pores = atlas.noise(c, 9, 0.8)
    c.shade[concrete] *= 1.0 + 0.03 * pores[concrete]
    c.height[concrete] += 0.0006 * pores[concrete]
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
    t[ID_ROOF] = pal["roof"]
    t[ID_METAL] = np.minimum(np.array(pal["roof"], np.float32) * 1.18 + 6, 255)
    t[ID_DOOR] = pal["door"]
    return t


def export(out_dir, ss=atlas.SS):
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.012)
    c.weather.dust(cav, (ID_WALL,))                  # beside the battens
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
