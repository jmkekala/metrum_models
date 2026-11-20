# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas for viljakuivuri_tower, and the
layout build.py maps into.

This describes one asset and nothing else, so it lives beside build.py rather
than in scripts/. It is the single source of the numbers the two files share:
build.py imports the z-levels, opening sizes and region rects from here, so
the pixel layout and the UVs cannot drift apart. Importing this module only
defines those constants; the painting runs when paint() is called.
Rasterising is scripts/atlas.py's.

    python3 facade_atlas.py export      # writes every map into ./export

A trim sheet, not one picture per elevation:

    y    0 ..  312   S1      lower walls, z 0 .. 4.80: plinth, flashing,
                             board-and-batten, and the drip joint at 4.80
    y  312 ..  576   W2      board-and-batten above 4.80, repeating every
                             4.00 m in V (rows 316 .. 572), a drip joint at
                             the foot of each repeat
    y  578 ..  650   BIN     the bin's corrugated wall, one 1.00 m ring
                             (rows 582 .. 646), repeating in V
    y  652 ..  672   FASCIA  white fascia board under the roof's edge, a
                             half-round galvanised gutter across its top
    y  674 ..  774   ROOF    profiled steel sheet, V stretched up the slope,
                             a galvanised snow guard 0.5 m up from the eave
    y  778 .. 1024   unique  doors, windows, the louvre, the bin roof,
                             the corner-board strip, flat patches

Every band spans the full width and tiles in U. The tower is 12 m to its
apex, which no band at 64 px/m holds in a 1024 atlas, so W2 tiles in V as
well: build.py cuts the tower's walls at 4.80 m and 8.80 m and maps each
4 m strip onto the same rows. Real board-and-batten does the same thing,
boards end and a drip board covers the joint, so the repeat sits on a joint
the eye expects. W2 and BIN each carry their opposite ends into their
gutters and every noise over them repeats on their period
(atlas.noise(tile_y=...)): W2 on 256 rows, BIN on 64. Weather that follows
height (ground splash, a sheltered eave) goes only on S1.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "viljakuivuri_tower"
ATLAS = 1024
PPM = 64.0

# --------------------------------------------------------- vertical layout
# Metres above ground, shared by every wall.
Z_FLOOR = 0.10       # floor slab and both door thresholds
Z_PLINTH = 0.35      # concrete plinth top
Z_FLASH = 0.40       # top of the plinth flashing; boards and corner boards
Z_J1 = 4.80          # first board joint: top of S1, foot of W2's first repeat
W2_P = 4.00          # W2's repeat, 256 px
Z_J2 = Z_J1 + W2_P   # second board joint
CW = 0.125           # corner-board width (8 px)
BATTEN_PITCH = 0.25  # board-and-batten: a batten every 16 px
BATTEN_W = 0.0625    # 4 px batten over each board joint
DRIP_PX = 6.0        # the drip board over a joint, 0.094 m

# ------------------------------------------------------------- openings
# kind -> (width, height, casing side, casing bottom, casing top), metres.
# Casings are painted, never modelled. Doors have no bottom casing.
OPENINGS = {
    "door_vehicle": (3.00, 3.20, 0.125, 0.0, 0.1875),
    "door": (0.90, 2.10, 0.125, 0.0, 0.1875),
    "win": (0.70, 0.80, 0.125, 0.125, 0.1875),
    "louvre": (1.50, 1.20, 0.125, 0.125, 0.1875),
}
REVEAL_DEPTH = {"louvre": 0.12}
REVEAL_DEFAULT = 0.15

# ------------------------------------------------------------ atlas bands
S1_Y0 = 2.0                  # v of z = 0
S1_TOP = 312.0
W2_Y0, W2_H = 316.0, 256.0   # v of a joint; the band repeats every W2_H
BIN_Y0, BIN_H = 582.0, 64.0  # v of a ring's foot; repeats every BIN_H
BIN_RING = BIN_H / PPM       # 1.00 m rings
FASC_Y0, FASC_H = 654.0, 16.0   # = the roof slabs' 0.25 m vertical thickness
GUTTER_PX = 8.0      # the gutter's rows, 0.125 m, hung across the fascia's top
# The downpipes' sides span the middle five of them (scripts/downpipes.py)
PIPE_STRIP = (FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 - 2.5,
              FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 + 2.5)
ROOF_Y0, ROOF_H = 676.0, 96.0
# The lean-to's slope, fascia top to the tower wall, in metres: the roof band
# stretches it over ROOF_H rows, and the tower's shorter slopes sample its
# lower rows at the same scale. build.py asserts it against the massing.
ROOF_SLOPE_LEN = 4.4517
UNI_Y0 = 780.0

ITEM_ORIGIN = {
    "door_vehicle": (4.0, UNI_Y0),
    "door": (218.0, UNI_Y0),
    "win": (298.0, UNI_Y0),
    "louvre": (366.0, UNI_Y0),
}
# The bin's cone roof, projected from above: centre of the region is the
# apex, BINROOF_PPM pixels per metre of plan radius.
BINROOF = (484.0, UNI_Y0, 128.0, 128.0)
BINROOF_PPM = 38.0
BIN_EAVE_R = 1.60            # the cone's eave radius; build.py's too
COLLAR_R = 0.30              # the fill collar round the apex
CORNER = (618.0, UNI_Y0, 8.0, 64.0)          # corner-board strip, V stretched
PATCHES = {name: (632.0 + 14.0 * i, UNI_Y0, 8.0, 8.0) for i, name in enumerate(
    ("trim", "soffit", "reveal", "blank", "galv", "galv_under", "soot",
     "flue", "barge"))}


def item_size_px(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    return (w + 2.0 * cs) * PPM, (h + cb + ct) * PPM


# ----------------------------------------------------------- material ids
ID_WALL, ID_TRIM, ID_SASH, ID_GLASS, ID_PLINTH, ID_METAL = 0, 1, 2, 3, 4, 5
ID_ROOF, ID_DOOR, ID_GALV, ID_FLUE, ID_BLANK, ID_HANDLE = 6, 7, 8, 9, 11, 12
ID_GUTTER = 13       # gutter, downpipes and snow guard: galvanised steel
# (roughness, metallic). Galvanised steel is metal, dulled by its zinc
# oxide. The gutter, downpipes and snow guard are the farm buildings' one
# rainwater steel, the same in every variant and on navetta_board_gable and
# konehalli_open_bays: sRGB (134, 137, 137), older zinc than the bin's, darker
# and duller. The furnace flue is black-painted steel.
SURFACE = {
    ID_WALL: (0.78, 0.0), ID_TRIM: (0.60, 0.0), ID_SASH: (0.50, 0.0),
    ID_GLASS: (glazing.ROUGHNESS, 0.0), ID_PLINTH: (0.90, 0.0),
    ID_METAL: (0.42, 0.30), ID_ROOF: (0.46, 0.25), ID_DOOR: (0.70, 0.0),
    ID_GALV: (0.40, 0.85), ID_FLUE: (0.62, 0.30), ID_BLANK: (0.95, 0.0),
    ID_HANDLE: (0.40, 0.70), ID_GUTTER: (0.48, 0.60),
}

# ---------------------------------------------------------------- palettes
# Farm paints, kept muted: punamulta red ochre and yellow ochre with white
# trim, and unpainted boards gone silver. The bin is galvanised in all three.
VARIANTS = {
    "red_ochre": {"wall": (124, 54, 44), "trim": (222, 219, 208),
                  "roof": (58, 60, 62), "door": (116, 51, 42)},
    "grey_weathered": {"wall": (110, 106, 98), "trim": (138, 134, 125),
                       "roof": (62, 62, 60), "door": (102, 98, 91)},
    "yellow_ochre": {"wall": (190, 152, 88), "trim": (224, 220, 208),
                     "roof": (76, 52, 46), "door": (178, 142, 82)},
}
DEFAULT_VARIANT = "red_ochre"
# The atlas has one window region, so the whole building is one pane to
# glazing.rooms(), and that pane's room level is drawn once, at 0.82 of the
# mean. Its base is raised by the inverse so the glass measures mid-band
# (sRGB ~55) rather than under the 45-70 band; the room treatment, falloff
# and lit wall are rooms()' own.
GLASS_BASE = tuple(int(round(v * 1.25)) for v in glazing.BASE)
FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (148, 146, 140), ID_GALV: (164, 167, 168),
    ID_FLUE: (46, 46, 46), ID_BLANK: (52, 52, 52), ID_HANDLE: (150, 146, 138),
    ID_GUTTER: (134, 137, 137),
}

BAND_IDS = {
    "S1": ((0, S1_TOP), {ID_PLINTH, ID_METAL, ID_WALL}),
    "W2": ((S1_TOP, W2_Y0 + W2_H + 4), {ID_WALL}),
    "BIN": ((BIN_Y0 - 4, BIN_Y0 + BIN_H + 4), {ID_GALV}),
    "FASCIA": ((FASC_Y0 - 2, FASC_Y0 + FASC_H + 2), {ID_METAL, ID_TRIM, ID_GUTTER}),
    "ROOF": ((ROOF_Y0 - 2, ROOF_Y0 + ROOF_H + 2), {ID_ROOF, ID_METAL, ID_GUTTER}),
}
TILE_W2 = int(ATLAS // W2_H)          # 4: noise over W2 repeats every 256 rows
TILE_BIN = int(ATLAS // BIN_H)        # 16: noise over BIN repeats every 64 rows

# ---------------------------------------------------------------- relief
BATTEN_H = 0.018     # batten proud of the boards
DRIP_H = 0.030       # drip board's lip, proud of the boards
CASING_H = 0.020
SILL_H = 0.035
SASH_H = 0.012
RIB_H = 0.020        # the roof sheet's trapezoidal ribs
CORR_H = 0.013       # the bin's corrugation, crest to valley
LAP_H = 0.003        # a bin sheet's lapped edge
GUTTER_R = 0.0625    # the half-round gutter's radius, 125 mm across
SNOW_TUBE_H = 0.035  # the snow guard's tubes, proud of the sheet
SNOW_BRACKET_H = 0.030
SNOW_GUARD_M = 0.50  # the snow guard's lower tube, up the slope from the eave


def m(v):
    """Metres -> pixels."""
    return v * PPM


def noise(c, seed, sx, sy=None):
    """atlas.noise() on W2's period, and on BIN's over the BIN band's rows,
    so every band that repeats in V stays seamless."""
    n = atlas.noise(c, seed, sx, sy, tile_y=TILE_W2)
    nb = atlas.noise(c, seed + 1000, sx, sy, tile_y=TILE_BIN)
    sy_, _ = c.sl(0, 1, BIN_Y0 - 4, BIN_Y0 + BIN_H + 4)
    n[sy_] = nb[sy_]
    return n


# ============================================================ painting
def paint_boards(c, y_lo, y_hi, seed):
    """Vertical board-and-batten across the full width: boards BATTEN_PITCH
    wide, a batten proud over every joint with its arrises rounded over a
    pixel, and occlusion in the angle beside each batten. Tone varies per
    board, hashed on a period that divides the atlas, so the band wraps in U;
    nothing varies in V, so it wraps in V too."""
    p = m(BATTEN_PITCH)
    bw = m(BATTEN_W)
    sy, sx, Y, X = c.field(0, ATLAS, y_lo, y_hi)
    xm = np.mod(X, p)
    d = np.minimum(xm, p - xm)                      # distance from a joint
    board = np.floor(X / p).astype(np.int64) % int(ATLAS // p)
    bat_i = np.floor(X / p + 0.5).astype(np.int64) % int(ATLAS // p)
    tone = 1.0 + 0.07 * (atlas.hash_unit(seed, board) - 0.5)
    bat = d < bw / 2.0
    btone = 1.0 + 0.05 * (atlas.hash_unit(seed + 7, bat_i) - 0.5)
    side = (~bat) & (d < bw / 2.0 + 1.0)
    c.mid[sy, sx] = ID_WALL
    shade = np.where(bat, btone, tone)
    c.shade[sy, sx] = np.where(side, shade * 0.86, shade)
    c.ao[sy, sx] = np.where(side, 0.80, 1.0)
    c.height[sy, sx] = BATTEN_H * np.clip((bw / 2.0 - d) / 1.0 + 0.5, 0.0, 1.0)


def paint_drip(c, yj, y_max=None):
    """A drip board over a board joint at row yj: sloped top, its lip
    proudest at the bottom, and the shadow it casts on the boards below."""
    y1 = yj + DRIP_PX if y_max is None else min(yj + DRIP_PX, y_max)
    c.paint(0, ATLAS, yj, y1, ID_WALL, 1.0, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, yj, y1)
    c.height[sy, sx] = DRIP_H - 0.016 * np.clip((Y - yj) / DRIP_PX, 0.0, 1.0)
    c.paint(0, ATLAS, yj, yj + 1, ID_WALL, 0.80, 0.8)        # lip's underside
    for k, f in enumerate((0.78, 0.88, 0.95)):              # shadow under it
        c.mul(0, ATLAS, yj - 1 - k, yj - k, f, ao=0.78 + 0.07 * k)


def paint_s1(c):
    y0 = S1_Y0
    c.paint(0, ATLAS, 0, y0 + m(Z_PLINTH), ID_PLINTH, 1.0, height=0.0)
    for k in range(1, 3):                                   # formwork lines
        zz = y0 + m(0.12 * k)
        c.mul(0, ATLAS, zz, zz + 1, 0.94)
        c.lift(0, ATLAS, zz, zz + 1, -0.002)
    c.mul(0, ATLAS, y0 + m(Z_PLINTH) - 2, y0 + m(Z_PLINTH), 0.86, ao=0.80)
    fy0, fy1 = y0 + m(Z_PLINTH), y0 + m(Z_FLASH)
    c.paint(0, ATLAS, fy0, fy1, ID_METAL, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, fy0, fy1)
    c.height[sy, sx] = 0.022 - 0.010 * (Y - fy0) / (fy1 - fy0)
    c.paint(0, ATLAS, fy0, fy0 + 1, ID_METAL, 0.80)
    paint_boards(c, fy1, S1_TOP, seed=11)
    paint_drip(c, y0 + m(Z_J1), y_max=S1_TOP)


def paint_w2(c):
    """W2 over its band and both gutters, as one periodic pattern: the
    gutter under the band holds the band's top rows and the gutter over it
    its foot, which is what each strip's neighbour on the wall is."""
    lo, hi = S1_TOP, W2_Y0 + W2_H + 4
    paint_boards(c, lo, hi, seed=29)
    paint_drip(c, W2_Y0)
    paint_drip(c, W2_Y0 + W2_H, y_max=hi)


def paint_bin(c):
    """One 1.00 m ring of the bin's corrugated galvanised wall, repeating in
    V with its opposite ends in the gutters. U runs once round the bin over
    the full width, so four sheets a ring are 256 px apart."""
    lo, hi = BIN_Y0 - 4, BIN_Y0 + BIN_H + 4
    sy, sx, Y, X = c.field(0, ATLAS, lo, hi)
    v = np.mod(Y - BIN_Y0, BIN_H)
    period = BIN_H / 15.0                       # 15 corrugations a ring, 67 mm
    phase = 2.0 * np.pi * v / period
    h = CORR_H * 0.5 * (1.0 - np.cos(phase))
    sheet = np.floor(X / 256.0).astype(np.int64) % 4
    tone = 1.0 + 0.06 * (atlas.hash_unit(31, sheet) - 0.5)
    shade = tone * (0.96 + 0.04 * 0.5 * (1.0 - np.cos(phase)))
    ao = 0.94 + 0.06 * 0.5 * (1.0 - np.cos(phase))
    # the ring joint: the upper ring's sheet laps outside the lower one, so
    # its edge is a small downward step at the ring's foot, bolted every 8 px
    lap = v < 3.0
    h = np.where(lap, h + LAP_H, h)
    shade = np.where(v < 1.0, shade * 0.80, shade)
    ao = np.where(v < 1.0, np.minimum(ao, 0.75), ao)
    bolt = lap & (np.hypot(np.mod(X, 8.0) - 4.0, v - 1.6) < 0.9)
    h = np.where(bolt, h + 0.006, h)
    shade = np.where(bolt, shade * 0.88, shade)
    # the vertical seam between sheets: a lap and a bolt every corrugation
    xs = np.mod(X, 256.0)
    seam = xs < 3.0
    h = np.where(seam, np.maximum(h, CORR_H * 0.5) + LAP_H, h)
    shade = np.where(xs < 1.0, shade * 0.82, shade)
    ao = np.where(xs < 1.0, np.minimum(ao, 0.75), ao)
    sbolt = seam & (np.hypot(xs - 1.6, np.mod(v, period) - period / 2.0) < 0.8)
    h = np.where(sbolt, h + 0.006, h)
    c.mid[sy, sx] = ID_GALV
    c.shade[sy, sx], c.ao[sy, sx], c.height[sy, sx] = shade, ao, h


def paint_fascia(c):
    """The eave's vertical edge: a white fascia board, with a half-round
    galvanised gutter hung across its top, right under the roof's edge where
    the water leaves the sheet; the board shows below it. Only eave fascias
    sample this band (rakes take the barge patch), so the gutter runs along
    the tower's two eaves and the lean-to's low eave and nowhere else."""
    y0, top = FASC_Y0, FASC_Y0 + FASC_H                 # top: the roof's edge
    gh = GUTTER_PX
    g0 = top - 1 - gh
    c.paint(0, ATLAS, y0 - 2, top + 2, ID_TRIM, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, g0, 0.012, 1.0, axes="y")
    c.paint(0, ATLAS, y0 - 2, y0 + 1, ID_TRIM, 0.86)              # lower edge
    # half-round gutter: belly at the bottom, rolled lip at the top. Its roll
    # is height; only the belly's underside is darker.
    c.paint(0, ATLAS, g0, top - 1, ID_GUTTER, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top - 1)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_GUTTER, 0.80)
    c.paint(0, ATLAS, top - 1, top + 2, ID_METAL, 0.80, height=0.0)  # sheet's drip edge
    c.ao[c.sl(0, ATLAS, g0 - 3, top + 2)] = 0.9
    for k, f in enumerate((0.92, 0.86, 0.80)):            # occluded under the gutter
        c.mul(0, ATLAS, g0 - 3 + k, g0 - 2 + k, f)
    # hangers every 1.0 m, a spacing that divides the atlas width; on the
    # downpipes, which sample the gutter's middle rows, they read as clips
    sy, sx, _, X = c.field(0, ATLAS, g0 + 2, top - 1)
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.80, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_roof(c):
    """Profiled steel sheet, V stretched up the slope (ROOF_H rows over
    ROOF_SLOPE_LEN metres). Ribs vary in U only; the snow guard and the
    flashing at the top, where the lean-to meets the tower wall, vary in V,
    so their heights are scaled by the band's px/m over PPM to keep their
    slopes physical. Every slope's V starts at its eave (build.py's slab()),
    so the snow guard lands SNOW_GUARD_M up from the eave on the tower's two
    slopes and the lean-to's alike."""
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0 - 2, y0 + h + 2, ID_ROOF, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - 2, y0 + h + 2)
    xm = np.mod(X, 16.0)
    v = Y - y0
    k = (h / ROOF_SLOPE_LEN) / PPM
    rib = np.clip(np.minimum(xm, 4.0 - xm) / 1.0, 0.0, 1.0) * (xm < 4.0)
    height = RIB_H * rib
    shade = np.where((xm >= 4.0) & (xm < 5.0), 0.92, 1.0)
    ao = np.where((xm >= 4.0) & (xm < 5.0), 0.86, 1.0)
    shade = np.where(v < 2, shade * 0.85, shade)                 # eave drip edge
    # snow guard: two round tubes on brackets, standard on Finnish metal
    # roofs, in the gutter's galvanised steel (ID_GUTTER) as a matched
    # system; the brackets sit on every second rib
    g = round(SNOW_GUARD_M * h / ROOF_SLOPE_LEN)
    guard = np.zeros(v.shape, bool)
    for t0, t1 in ((g, g + 2.0), (g + 3.0, g + 4.5)):
        inside = (v >= t0) & (v < t1)
        tube = SNOW_TUBE_H * k * np.sqrt(np.clip(
            1.0 - (2.0 * (v - t0) / (t1 - t0) - 1.0) ** 2, 0.0, 1.0))
        height = np.where(inside, np.maximum(height, tube), height)
        shade = np.where(inside, 1.0, shade)
        guard |= inside
    shade = np.where((v >= g - 3) & (v < g - 1), shade * 0.80, shade)   # under the tubes
    ao = np.where((v >= g - 3) & (v < g + 4.5), np.minimum(ao, 0.85), ao)
    xb = np.mod(X, 32.0)
    bracket = (xb >= 1.0) & (xb < 3.0) & (v >= g - 3) & (v < g + 4.5)
    height = np.where(bracket, np.maximum(height, SNOW_BRACKET_H * k), height)
    shade = np.where(bracket, 0.75, shade)
    guard |= bracket
    top = v >= h - 8
    height = np.where(top, 0.010 * k, height)
    shade = np.where(top, 0.97, shade)
    shade = np.where((v >= h - 8) & (v < h - 7), shade * 0.82, shade)
    ao = np.where((v >= h - 10) & (v < h - 8), np.minimum(ao, 0.85), ao)
    c.mid[sy, sx] = np.where(top, ID_METAL, np.where(guard, ID_GUTTER, ID_ROOF))
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao


def paint_opening(c, kind):
    x0, y0 = ITEM_ORIGIN[kind]
    w, h, cs, cb, ct = OPENINGS[kind]
    rw, rh = item_size_px(kind)
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0 + m(cb), y0 + m(cb + h)
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, ID_TRIM, 1.0, 1.0, height=0.0)
    c.bevel(x0, x0 + rw, y0, y0 + rh, CASING_H, 1.0)
    top = y0 + rh
    if kind != "louvre":
        # drip cap: sheet steel over the head casing, sloping out
        c.paint(x0 - 2, x0 + rw + 2, top - 3, top + 2, ID_METAL, 1.0)
        sy, sx, Y, _ = c.field(x0 - 2, x0 + rw + 2, top - 3, top + 2)
        c.height[sy, sx] = 0.032 - 0.012 * np.clip((Y - (top - 3)) / 3.0, 0.0, 1.0)
        c.paint(x0 - 2, x0 + rw + 2, top - 4, top - 3, ID_TRIM, 0.85, 0.8)
    c.mul(ox0 - 1, ox1 + 1, oy1, oy1 + 1, 0.84, ao=0.8)          # head shadow
    if cb > 0:                                                   # sill board
        c.paint(x0 - 2, x0 + rw + 2, y0 - 2, oy0, ID_TRIM, 1.0)
        c.bevel(x0, x0 + rw, y0, oy0, SILL_H, 1.0)
        c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + 1, ID_TRIM, 0.80, 0.8)
    if kind == "door_vehicle":
        paint_vehicle_door(c, ox0, ox1, oy0, oy1)
    elif kind == "door":
        paint_door(c, ox0, ox1, oy0, oy1)
    elif kind == "louvre":
        paint_louvre(c, ox0, ox1, oy0, oy1)
    else:
        paint_window(c, ox0, ox1, oy0, oy1)


def paint_window(c, ox0, ox1, oy0, oy1):
    """One plain pane in a thin sash. glazing.rooms() owns the glass's
    colour; this sets its id, its AO and a flat height."""
    f = m(0.0625)
    c.paint(ox0, ox1, oy0, oy1, ID_SASH, 1.0, 1.0)
    c.bevel(ox0, ox1, oy0, oy1, SASH_H, 1.0)
    c.paint(ox0 + f, ox1 - f, oy0 + f, oy1 - f, ID_GLASS, ao=0.9, height=0.0)
    c.mul(ox0 + f, ox1 - f, oy1 - f - 1, oy1 - f, 0.82, ao=0.8)
    c.mul(ox0 + f, ox0 + f + 1, oy0 + f, oy1 - f, 0.88)


def paint_planks(c, x0, x1, y0, y1, pitch):
    c.paint(x0, x1, y0, y1, ID_DOOR, 1.0, 1.0, height=0.0)
    for xx in np.arange(x0 + pitch, x1 - 1, pitch):
        c.mul(xx, xx + 1, y0, y1, 0.80, ao=0.78)
        c.lift(xx, xx + 1, y0, y1, -0.003)


def brace(c, a, b, w, clip):
    """A white brace board from a to b, w px wide, clipped to a panel."""
    c.stroke(a, b, w, mid=ID_TRIM, shade=1.0, clip=clip, height=0.020)


def paint_door(c, x0, x1, y0, y1):
    """Ledged-and-braced plank door: two white ledges and a white brace
    rising from the hinge side (left) to the latch side."""
    paint_planks(c, x0, x1, y0, y1, m(0.10))
    lw = m(0.12)
    l0 = (y0 + m(0.20), y0 + m(0.20) + lw)
    l1 = (y1 - m(0.25) - lw, y1 - m(0.25))
    for a, b in (l0, l1):
        c.paint(x0, x1, a, b, ID_TRIM, 1.0, 1.0)
        c.bevel(x0, x1, a, b, 0.020, 1.0)
        c.mul(x0, x1, a - 1, a, 0.85, ao=0.8)
    brace(c, (x0 + lw * 0.6, l0[1]), (x1 - lw * 0.6, l1[0]), lw,
          (x0, l0[1], x1 - x0, l1[0] - l0[1]))
    hx = x1 - m(0.10)
    c.paint(hx - 1, hx + 1, y0 + m(0.98), y0 + m(1.12), ID_HANDLE, 0.9, height=0.030)
    c.paint(x0, x1, y0, y0 + 2, ID_DOOR, 0.8, 0.7)                    # kick wear


def paint_vehicle_door(c, x0, x1, y0, y1):
    """The tipping-pit door: a pair of hinged leaves of vertical boards in a
    white frame, a mid rail and a white diagonal brace in each panel rising
    from the hinge to the meeting stiles."""
    mid = (x0 + x1) / 2.0
    st, rl = m(0.12), m(0.15)
    ym0, ym1 = y0 + m(1.55), y0 + m(1.70)
    for a, b, hinge_left in ((x0, mid, True), (mid, x1, False)):
        paint_planks(c, a, b, y0, y1, m(0.12))
        for r in ((a, a + st, y0, y1), (b - st, b, y0, y1)):
            c.paint(r[0], r[1], r[2], r[3], ID_TRIM, 1.0, 1.0)
            c.bevel(r[0], r[1], r[2], r[3], 0.022, 1.0)
        for p, q in ((y0, y0 + rl), (y1 - rl, y1), (ym0, ym1)):
            c.paint(a + st, b - st, p, q, ID_TRIM, 1.0, 1.0)
            c.bevel(a + st, b - st, p, q, 0.022, 1.0)
            c.mul(a + st, b - st, p - 1, p, 0.86, ao=0.8)
        for p, q in ((y0 + rl, ym0), (ym1, y1 - rl)):
            lo_x, hi_x = (a + st, b - st) if hinge_left else (b - st, a + st)
            brace(c, (lo_x, p), (hi_x, q), st, (a + st, p, b - a - 2 * st, q - p))
    c.paint(mid - 0.75, mid + 0.75, y0, y1, ID_BLANK, 0.5, 0.5, height=0.0)   # meeting gap
    for xx in (mid - m(0.10), mid + m(0.06)):                                 # hasp
        c.paint(xx, xx + m(0.04), y0 + m(1.10), y0 + m(1.30), ID_HANDLE, 0.9, height=0.030)
    c.paint(x0, x1, y0, y0 + 2, ID_DOOR, 0.8, 0.7)


def paint_louvre(c, x0, x1, y0, y1):
    """The dryer's exhaust: timber louvre blades in the trim colour,
    sloping out and down, dark between."""
    c.paint(x0, x1, y0, y1, ID_BLANK, 0.55, 0.5, height=-0.010)
    pitch = m(0.075)
    for yy in np.arange(y0 + 1, y1 - 1, pitch):
        b = min(yy + pitch - 1.6, y1)
        c.paint(x0, x1, yy, b, ID_TRIM, 1.0, 0.9)
        sy, sx, Y, _ = c.field(x0, x1, yy, b)
        c.height[sy, sx] = 0.022 * (1.0 - (Y - yy) / max(b - yy, 1e-3))
        c.paint(x0, x1, yy, yy + 1, ID_TRIM, 0.82, 0.8)
    c.mul(x0, x1, y1 - 2, y1, 0.75, ao=0.7)
    c.mul(x0, x0 + 1, y0, y1, 0.85, ao=0.8)


def paint_bin_roof(c):
    """The bin's cone, seen from above: 24 radial ribs from the fill collar
    to the eave, a rolled edge, and the collar's lid at the centre."""
    x0, y0, w, h = BINROOF
    cx, cy = x0 + w / 2.0, y0 + h / 2.0
    R, rc = BIN_EAVE_R * BINROOF_PPM, COLLAR_R * BINROOF_PPM
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_GALV, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2)
    dx, dy = X - cx, Y - cy
    r = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    step = 2.0 * np.pi / 24.0
    a = th / step
    d = np.abs(a - np.round(a)) * step * r            # arc distance to a rib, px
    rib = (d < 1.1) & (r > rc + 2.0) & (r < R - 2.0)
    sheet = np.floor(a).astype(np.int64) % 24
    tone = 1.0 + 0.05 * (atlas.hash_unit(41, sheet) - 0.5)
    shade = np.where(rib, tone * 1.0, tone)
    height = np.where(rib, 0.016 * np.clip(1.1 - d, 0.0, 1.0) + 0.006, 0.0)
    edge = (r >= R - 2.0)
    shade = np.where(edge, shade * 0.86, shade)
    height = np.where(edge, 0.010, height)
    collar = r < rc
    shade = np.where(collar, 0.94, shade)
    height = np.where(collar, 0.0, height)
    ring = (r >= rc - 1.5) & (r < rc + 1.0)
    shade = np.where(ring, shade * 0.80, shade)
    c.shade[sy, sx], c.height[sy, sx] = shade, height
    c.ao[sy, sx] = np.where(ring | (rib & (d > 0.7)), 0.85, 1.0)


def paint_corner(c):
    x0, y0, w, h = CORNER
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_TRIM, 1.0, height=0.0)
    c.bevel(x0, x0 + w, y0 - 2, y0 + h + 2, CASING_H, 1.0, axes="x")


def paint_patches(c):
    spec = {"trim": (ID_TRIM, 1.0, 1.0), "soffit": (ID_TRIM, 0.86, 0.82),
            "reveal": (ID_TRIM, 0.72, 0.6), "blank": (ID_BLANK, 1.0, 0.5),
            "galv": (ID_GALV, 1.0, 1.0), "galv_under": (ID_GALV, 0.70, 0.6),
            "soot": (ID_BLANK, 0.45, 0.35), "flue": (ID_FLUE, 1.0, 1.0),
            "barge": (ID_TRIM, 0.97, 1.0)}
    for name, (x0, y0, w, h) in PATCHES.items():
        mid, sh, ao = spec[name]
        c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, mid, sh, ao, height=0.0)


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    Height-following weather goes on S1 only, whose V is height from the
    ground; W2 and the bin's band repeat in V, so they get only noise on
    their own period, written here on the bin's from its own noise."""
    w = weathering.Weather(c, clean=(ID_GLASS,),
                           steel=(ID_ROOF, ID_METAL, ID_GALV, ID_FLUE, ID_GUTTER),
                           tile_y=TILE_W2)
    b0, b1 = BIN_Y0 - 4, BIN_Y0 + BIN_H + 4
    for y0, y1 in ((0, b0), (b1, ATLAS)):                    # grime, bin excepted
        w.add("D", 0, ATLAS, y0, y1, lambda Y, X, nz: 0.035 * nz("blotch"))
    w.fade((ID_WALL, ID_TRIM, ID_SASH, ID_DOOR))
    w.wash((ID_WALL,))
    # S1: the plinth, its flashing, the boards' splashed foot
    w.plinth(0, ATLAS, S1_Y0, S1_Y0 + m(Z_PLINTH), (ID_PLINTH,))
    w.add("D", 0, ATLAS, S1_Y0 + m(Z_PLINTH), S1_Y0 + m(Z_FLASH),
          lambda Y, X, nz: 0.10 * nz("blotch"), (ID_METAL,))
    w.splash(0, ATLAS, S1_Y0 + m(Z_FLASH), S1_TOP, (ID_WALL,))
    # the drip boards: dirt on their sloped tops, short runs under the lips
    for yj, y1 in ((S1_Y0 + m(Z_J1), S1_TOP), (W2_Y0, W2_Y0 + DRIP_PX),
                   (W2_Y0 + W2_H, W2_Y0 + W2_H + 4)):
        w.add("D", 0, ATLAS, yj + 1, y1, 0.06, (ID_WALL,))
        w.runs(0, ATLAS, yj - 12, yj, (ID_WALL,), 0.10, fall=5.0, noise="short")
    w.runs(0, ATLAS, S1_TOP, S1_TOP + 2, (ID_WALL,), 0.10, fall=5.0, noise="short")
    # the roof band, up the slope from the eave
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, ROOF_SLOPE_LEN, (ID_ROOF,))
    w.add("D", 0, ATLAS, ROOF_Y0 - 2, ROOF_Y0 + ROOF_H + 2, lambda Y, X, nz: 0.10 * (
        (np.mod(X, 16.0) >= 4.0) & (np.mod(X, 16.0) < 6.0)), (ID_ROOF,))
    w.add("R", 0, ATLAS, ROOF_Y0 - 2, ROOF_Y0 + 3, lambda Y, X, nz: 0.12 * nz("speck"),
          (ID_ROOF,))
    # the snow guard: light dust on it (with the grime above, 0.06 + 0.08
    # blotch, as on the farm's other two), rust at its brackets, debris held
    # above it, rust on the sheet round the brackets and in short runs under
    # them
    g = ROOF_Y0 + round(SNOW_GUARD_M * ROOF_H / ROOF_SLOPE_LEN)
    w.add("D", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.06 + 0.045 * nz("blotch"),
          (ID_GUTTER,))
    w.add("R", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.15 * (
        (np.mod(X, 32.0) >= 1.0) & (np.mod(X, 32.0) < 3.0)), (ID_GUTTER,))
    w.add("D", 0, ATLAS, g + 4.5, g + 14.0, lambda Y, X, nz: 0.22 * nz("blotch")
          * (1.0 - (Y - g - 4.5) / 9.5), (ID_ROOF,))
    w.add("R", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.16 * (
        np.mod(X, 32.0) < 4.0), (ID_ROOF,))
    w.add("R", 0, ATLAS, g - 10, g - 3, lambda Y, X, nz: 0.12 * (
        (np.mod(X, 32.0) >= 1.2) & (np.mod(X, 32.0) < 2.8)) * (1.0 - (g - 3 - Y) / 7.0)
        * atlas.smoothstep(-0.5, 0.8, nz("runs")), (ID_ROOF,))
    # the fascia: dirt and runs down the board from the gutter; the gutter's
    # dirty belly and light runs down its face from the lip, the same
    # treatment as the farm's other two gutters
    top = FASC_Y0 + FASC_H
    g0 = top - 1 - GUTTER_PX
    w.add("D", 0, ATLAS, FASC_Y0 - 2, g0, 0.05, (ID_TRIM,))
    w.runs(0, ATLAS, FASC_Y0 - 2, g0, (ID_TRIM,), 0.18, fall=5.0, lo=0.4, hi=1.6)
    w.add("D", 0, ATLAS, g0, g0 + 4, lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"),
          (ID_GUTTER,))
    w.runs(0, ATLAS, g0, top - 1, (ID_GUTTER,), 0.08, fall=4.0, lo=0.4, hi=1.6)
    # openings: sills and heads; door handles and feet
    for kind, (wd, h, cs, cb, ct) in OPENINGS.items():
        x0, yb = ITEM_ORIGIN[kind]
        rw, rh = item_size_px(kind)
        ox0, ox1 = x0 + m(cs), x0 + m(cs + wd)
        oy0, oy1 = yb + m(cb), yb + m(cb + h)
        if kind == "door":
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR,), handle=(ox1 - m(0.10), oy0 + m(1.05)))
        elif kind == "door_vehicle":
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR, ID_TRIM),
                   handle=((ox0 + ox1) / 2.0, oy0 + m(1.20)))
            w.splash(ox0, ox1, oy0, oy0 + m(0.8), (ID_DOOR, ID_TRIM), amount=0.25,
                     fall=0.25)
        elif kind == "win":
            w.window(x0, yb, rw, rh, oy0, oy1, m(0.0625), (ID_TRIM,), (ID_SASH,))
        else:
            w.window(x0, yb, rw, rh, oy0, oy1, 0.0, (ID_TRIM,), (ID_TRIM,))
            w.add("D", ox0, ox1, oy0, oy1, lambda Y, X, nz: 0.14 + 0.10 * nz("blotch"),
                  (ID_TRIM,))                       # dust blown out of the dryer
    # corner boards: splashed at the foot (the strip's V starts at Z_FLASH)
    kx0, ky0, kw, kh = CORNER
    w.add("D", kx0 - 2, kx0 + kw + 2, ky0 - 2, ky0 + kh + 2, lambda Y, X, nz: 0.22
          * np.exp(-np.clip(Y - ky0, 0.0, None) / 3.0), (ID_TRIM,))
    # the bin's roof: dust toward the eave and round the collar, rust specks
    x0, y0, bw, bh = BINROOF
    cx, cy = x0 + bw / 2.0, y0 + bh / 2.0
    R = BIN_EAVE_R * BINROOF_PPM
    w.add("D", x0 - 2, x0 + bw + 2, y0 - 2, y0 + bh + 2, lambda Y, X, nz: (
        0.06 + 0.10 * nz("blotch") + 0.12 * np.exp(-(R - np.hypot(X - cx, Y - cy)) / 6.0)),
        (ID_GALV,))
    w.add("F", x0 - 2, x0 + bw + 2, y0 - 2, y0 + bh + 2,
          lambda Y, X, nz: 0.12 * nz("big"), (ID_GALV,))
    w.add("R", x0 - 2, x0 + bw + 2, y0 - 2, y0 + bh + 2,
          lambda Y, X, nz: 0.10 * nz("speck"), (ID_GALV,))
    # the flue: rust, and soot round its mouth's patch
    fx0, fy0, fw, fh = PATCHES["flue"]
    w.add("R", fx0 - 2, fx0 + fw + 2, fy0 - 2, fy0 + fh + 2, 0.12, (ID_FLUE,))
    # the bin's wall, on its own 64-row period: dull white bloom on the zinc,
    # a film of dust, and short runs hanging under each ring's lapped edge
    sy, sx, Y, _ = c.field(0, ATLAS, b0, b1)
    v = np.mod(Y - BIN_Y0, BIN_H)
    blotch = atlas.smoothstep(-1.5, 1.5, atlas.noise(c, 201, 24.0, tile_y=TILE_BIN)[sy, sx])
    big = atlas.smoothstep(-1.5, 1.5, atlas.noise(c, 202, 60.0, tile_y=TILE_BIN)[sy, sx])
    runs = atlas.noise(c, 203, 0.8, 14.0, tile_y=TILE_BIN)[sy, sx]
    w.f["D"][sy, sx] += 0.05 * blotch + 0.14 * atlas.smoothstep(0.3, 1.5, runs) * np.exp(
        -(BIN_H - v) / 10.0)
    w.f["F"][sy, sx] += 0.05 + 0.12 * big
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_s1(c)
    paint_w2(c)
    paint_bin(c)
    paint_fascia(c)
    paint_roof(c)
    for kind in OPENINGS:
        paint_opening(c, kind)
    paint_bin_roof(c)
    paint_corner(c)
    paint_patches(c)
    c.check_bands(BAND_IDS)

    wear = 0.025 * noise(c, 3, 40.0) + 0.015 * noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    wood = np.isin(c.mid, (ID_WALL, ID_TRIM, ID_DOOR))
    grain = noise(c, 5, 0.35, 60.0)                   # streaks along the boards
    c.shade[wood] *= 1.0 + 0.03 * grain[wood]
    c.height[wood] += 0.0003 * grain[wood]
    roof = c.mid == ID_ROOF
    streak = noise(c, 7, 0.8, 40.0)                   # rain runs down the slope
    c.shade[roof] *= 1.0 + 0.035 * streak[roof]
    galv = c.mid == ID_GALV
    spangle = noise(c, 8, 1.5)                        # the zinc's spangle
    c.shade[galv] *= 1.0 + 0.03 * spangle[galv]
    concrete = c.mid == ID_PLINTH
    pores = noise(c, 9, 0.8)
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
    c.weather.dust(cav, (ID_WALL,))
    rough = 0.04 * noise(c, 13, 20.0)
    path = os.path.join(out_dir, ASSET)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS,)), path + "_normal.png"),
               atlas.save(glazing.night_rooms(atlas.coverage(c, ID_GLASS) > 0,
                                              atlas.emission(c, ID_GLASS)),
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
