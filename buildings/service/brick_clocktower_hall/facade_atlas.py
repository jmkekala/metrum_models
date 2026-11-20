# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas for brick_clocktower_hall.

This builds one asset and nothing else: every region constant, colour and painted
feature below describes this building, so it lives beside build.py rather than in
scripts/, which is for tooling a second asset could call unmodified.

    python3 facade_atlas.py export      # writes every map into ./export

The atlas is laid out in three horizontal bands whose pixel coordinates must stay
in lockstep with the UV assignment in build.py beside it:

    y    0 ..  730   facade   - tiles horizontally, 11.4 m of wall at 64 px/m
    y  730 ..  986   roof     - tiles horizontally, V stretched across each slope
    y  986 .. 2048   unique   - entrance / tower / clock attic / chimney / patches

Everything is authored at 64 px/m so that storey bands, string course and cornice
line up across every wall of the building without per-wall tweaking.

Rasterising is scripts/atlas.py's: a canvas supersampled SS x SS per pixel, so
the arched doorway, the clock dial and the belfry arch come out anti-aliased
without hand-computed coverage. Painting produces a material id, a shade, an AO
and a height per sample; this being a single-variant landmark, each colour is an
id and a shade factor on it (WALL_LT is the wall at 1.08). Relief that should
answer the sun -- brick faces, the string course, cornice and dentils, the
window surrounds and pediments, quoins, balusters, standing seams -- is height,
and reaches the renderer through the normal map. atlas.pad() fills every sample
no region claims from the nearest region's own edge. Dirt, algae, rust and
faded paint are scripts/weathering.py's fields, placed by weather() below.
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

ASSET = "brick_clocktower_hall"
VARIANT = "red_brick"
ATLAS = 2048
PPM = 64.0

ROOF_Y0, ROOF_H = 730, 256
UNI = 986
ENT = (0, 704, UNI, UNI + 730)
TOW = (704, 896, UNI, UNI + 563)     # 3.0 m x 8.8 m
ATT = (986, 1498, UNI, UNI + 333)
CHM = (1498, 1588, UNI, UNI + 314)   # 1.4 m x 4.9 m
BLANK = (1600, 1660, UNI, UNI + 60)
# flat trim patch for returns and raking cornices, which must not sample the
# stretched clock artwork
TRIMPATCH = (1660, 1720, UNI, UNI + 60)
# 0.5 m x 11.4 m toothed quoin strip, wrapped onto the corner blocks
QUOIN = (1720, 1752, UNI, UNI + 730)
# 4.8 m x 1.0 m balcony parapet, solid with the balusters painted on
BALUS = (0, 308, 1750, 1814)
# shadowed plaster for window and door reveals; bright trim there reads as a
# pale frame rather than as depth
REVEALP = (1752, 1812, UNI, UNI + 60)
# soot for the chimney flues' lining and floor, above the blank patch and
# clear of every region edge, so its padding touches nothing sampled
SOOT = (1600, 1660, UNI + 72, UNI + 132)

# ------------------------------------------------------- materials, colours
# Material ids, each with its base colour. The other colours the elevations
# use are shades of these: see SHADE.
ID_WALL, ID_TRIM, ID_PLINTH, ID_GLASS, ID_FRAME = 0, 1, 2, 3, 4
ID_DOOR, ID_ROOF, ID_DARK, ID_CLOCK, ID_CHIM = 5, 6, 7, 8, 9
COLOUR = {
    ID_WALL: (158, 96, 72), ID_TRIM: (226, 222, 211), ID_PLINTH: (163, 158, 149),
    # Glass is neutral and DARK: from outside a window is mostly the unlit room
    # behind it, and the sky reflection is the renderer's job, not the base
    # colour's. glazing.rooms() repaints every pane at the end.
    ID_GLASS: glazing.BASE, ID_FRAME: (150, 146, 140), ID_DOOR: (60, 50, 42),
    ID_ROOF: (47, 51, 59), ID_DARK: (58, 52, 47), ID_CLOCK: (232, 229, 220),
    # Dark rendered stacks rather than exposed brick: the chimneys read as
    # near-black against the roof, not as red brick rising out of it.
    ID_CHIM: (70, 73, 78),
}
WALL_LT, WALL_DK, TRIM_SH, PLINTH_DK = 1.08, 0.905, 0.86, 0.82
ROOF_DK, CHIM_DK, CHIM_CAP = 0.80, 0.83, 1.40
SPANDREL, REVEAL = 0.555, 0.58          # shadowed plaster, as shades of trim
# (roughness, metallic)
SURFACE = {ID_WALL: (0.80, 0.0), ID_TRIM: (0.62, 0.0), ID_PLINTH: (0.71, 0.0),
           ID_GLASS: (0.10, 0.0), ID_FRAME: (0.45, 0.15), ID_DOOR: (0.56, 0.0),
           ID_ROOF: (0.38, 0.25), ID_DARK: (0.88, 0.0), ID_CLOCK: (0.34, 0.0),
           ID_CHIM: (0.71, 0.0)}

# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto: only the few
# centimetres the mesh does not model. The walls' openings, the eave, the
# balcony, the dial and the quoin blocks are geometry at the near tiers.
BRICK_FACE = 0.006
TRIM_H = 0.040       # string course, plinth cap, window surrounds, pilasters
CORNICE_H = 0.060    # cornice and pediments, the deepest painted mouldings
DENTIL_H = 0.030
SEAM_H = 0.025       # the roof's standing seams
REVEAL_D = -0.020    # the dark reveal ring round each window, set back


# ---------------------------------------------------------------- vertical
# Vertical architecture, in metres above ground.
Z_PLINTH_TOP = 0.95
Z_PLINTH_CAP = 1.15
Z_GF_SILL = 1.25
Z_GF_HEAD = 3.70
Z_GF_SPRING = 3.85
Z_STRING_BOT = 5.10
Z_STRING_TOP = 5.55
Z_UF_SILL = 6.35
Z_UF_HEAD = 8.95
Z_FRIEZE_BOT = 9.95
Z_CORNICE_BOT = 10.45
Z_CORNICE_TOP = 11.15
Z_TOP = 11.40


def m(v):
    """Metres -> pixels."""
    return v * PPM


# ================================================================ painting
def arch(c, cx, r, y_sill, y_spring, mid, shade=1.0, ao=None, height=None):
    """An opening with straight jambs up to y_spring, then a semicircular head."""
    def test(X, Y):
        jamb = (np.abs(X - cx) <= r) & (Y >= y_sill) & (Y <= y_spring)
        head = ((X - cx) ** 2 + (Y - y_spring) ** 2 <= r * r) & (Y > y_spring)
        return jamb | head
    c.shape(cx - r - 1, cx + r + 1, y_sill, y_spring + r + 1, test, mid, shade, ao,
            height)


def bricks(c, x0, x1, y0, y1, yb, mid=ID_WALL, tones=(1.0, WALL_LT, WALL_DK, 1.0),
           joints=True):
    """Running-bond brick over a rect: per-brick tone hashed so there is no
    diagonal banding, periodic in X so the facade band still tiles; recessed
    bed and perpend joints."""
    bl, bh = int(round(m(0.25))), int(round(m(0.075)))
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    by = np.floor((Y - yb) / bh).astype(np.int64)
    shift = (by % 2) * (bl // 2)
    bx = np.floor((X + shift) / bl).astype(np.int64) % (ATLAS // bl)
    h = bx * 374761393 + by * 668265263
    h = (h ^ (h >> 13)) * 1274126177
    shade = np.asarray(tones, np.float32)[(h >> 16) % len(tones)]
    c.mid[sy, sx] = mid
    if not joints:
        c.shade[sy, sx] = shade
        return
    bed = (Y - yb - by * bh) < 1.0
    perp = ((X + shift) % bl) < 1.0
    c.shade[sy, sx] = np.where(bed, WALL_DK * 0.90, np.where(perp, WALL_DK * 0.94, shade))
    c.ao[sy, sx] = np.where(bed | perp, 0.86, 1.0)
    c.height[sy, sx] = np.where(bed | perp, 0.0, BRICK_FACE)


def moulding(c, x0, x1, y0, y1, h, shade=1.0, ao=None, axes="y"):
    """A trim band standing *h* proud, with rounded arrises."""
    c.paint(x0, x1, y0, y1, ID_TRIM, shade, ao)
    c.bevel(x0, x1, y0, y1, h, 1.0, axes=axes)


def draw_wall_bands(c, x0, x1, yb):
    """Horizontal storey architecture shared by every wall."""
    c.paint(x0, x1, yb, yb + m(Z_TOP), ID_WALL, 1.0, 1.0, height=0.0)
    bricks(c, x0, x1, yb + m(Z_PLINTH_CAP), yb + m(Z_TOP), yb)

    # plinth: dressed stone courses, the ground course darker
    c.paint(x0, x1, yb, yb + m(Z_PLINTH_TOP), ID_PLINTH, 1.0, height=0.0)
    for j in range(1, 4):
        c.paint(x0, x1, yb + m(0.24 * j), yb + m(0.24 * j) + 1, ID_PLINTH, PLINTH_DK,
                height=-0.004)
    c.paint(x0, x1, yb, yb + m(0.18), ID_PLINTH, PLINTH_DK, 0.72)
    moulding(c, x0, x1, yb + m(Z_PLINTH_TOP), yb + m(Z_PLINTH_CAP), TRIM_H)
    c.paint(x0, x1, yb + m(Z_PLINTH_CAP), yb + m(Z_PLINTH_CAP) + 2, ID_TRIM, TRIM_SH, 0.78)

    # string course between storeys, occluded under its drip
    moulding(c, x0, x1, yb + m(Z_STRING_BOT), yb + m(Z_STRING_TOP), CORNICE_H)
    c.paint(x0, x1, yb + m(Z_STRING_BOT) - 3, yb + m(Z_STRING_BOT), ID_TRIM, TRIM_SH, 0.70)
    c.paint(x0, x1, yb + m(Z_STRING_TOP), yb + m(Z_STRING_TOP) + 2, ID_TRIM, TRIM_SH, 0.80)

    # frieze, cornice with dentils, top fascia
    c.paint(x0, x1, yb + m(Z_FRIEZE_BOT), yb + m(Z_CORNICE_BOT), ID_TRIM, TRIM_SH,
            height=0.010)
    sy, sx, _, X = c.field(x0, x1, yb + m(Z_FRIEZE_BOT), yb + m(Z_CORNICE_BOT))
    pitch, width = round(m(0.32)), round(m(0.14))
    dent = (X % pitch) < width
    c.shade[sy, sx] = np.where(dent, 1.0, c.shade[sy, sx])
    c.height[sy, sx] = np.where(dent, DENTIL_H, c.height[sy, sx])
    c.paint(x0, x1, yb + m(Z_FRIEZE_BOT) - 4, yb + m(Z_FRIEZE_BOT), ID_DARK, 1.0, 0.45,
            height=0.0)
    moulding(c, x0, x1, yb + m(Z_CORNICE_BOT), yb + m(Z_CORNICE_TOP), CORNICE_H)
    c.paint(x0, x1, yb + m(Z_CORNICE_TOP), yb + m(Z_TOP), ID_TRIM, TRIM_SH, 0.72,
            height=0.020)


def sill_grime(c, n01, cx, w, ys, fall=0.75, strength=0.075):
    """Weathering below a sill, as a falloff rather than a rectangle.

    This was a hard-edged box the width of the window, darkening it a flat 10%.
    It read as a painted shadow rather than as dirt, because it had a crisp
    bottom edge and crisp sides that nothing on the wall explains — worst on
    the ground floor, where it lands on the flat grey plinth and the edges have
    nothing to hide behind. It only became obvious once the windows were
    resized smaller: the band stayed the same size and moved down onto the
    plinth, where it had previously sat on brick and been partly lost in the
    coursing.

    Run-off is strongest right under the sill and fades downwards and sideways,
    so that is what fades here. It is also weaker, and broken up with noise so
    it does not read as a clean gradient ramp, which is the other way a painted
    effect gives itself away.
    """
    top = ys - m(0.30)
    depth = max(1.0, m(fall))
    half = w + m(0.10)
    sy, sx, Y, X = c.field(cx - half, cx + half, max(0.0, top - depth), max(0.0, top))
    if Y.size == 0:
        return
    t = np.clip((top - Y) / depth, 0.0, 1.0)
    vert = (1.0 - t) ** 1.6
    edge = atlas.smoothstep(0.0, 1.0, (half - np.abs(X - cx)) / max(1.0, m(0.22)))
    amt = np.clip(vert * edge * (0.70 + 0.6 * n01[sy, sx]), 0.0, 1.0) * strength
    c.shade[sy, sx] *= 1.0 - amt
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 1.0 - amt * 0.55)


def draw_rect_window(c, n01, cx, half_w, yb, sill=Z_UF_SILL, head=Z_UF_HEAD, bars=3):
    w, ys, yh = m(half_w), yb + m(sill), yb + m(head)
    # architrave, then a small pediment over the head
    moulding(c, cx - w - m(0.26), cx + w + m(0.26), ys - m(0.26), yh + m(0.26), TRIM_H,
             axes="xy")
    moulding(c, cx - w - m(0.42), cx + w + m(0.42), yh + m(0.26), yh + m(0.52), CORNICE_H,
             axes="xy")
    c.paint(cx - w - m(0.42), cx + w + m(0.42), yh + m(0.52), yh + m(0.58), ID_TRIM,
            TRIM_SH, 0.74)
    # the dark reveal ring, set back, then the glass and its bars
    c.paint(cx - w - m(0.10), cx + w + m(0.10), ys - m(0.08), yh + m(0.10), ID_DARK,
            1.0, 0.42, height=REVEAL_D)
    c.paint(cx - w, cx + w, ys, yh, ID_GLASS, 1.0, 0.55, height=REVEAL_D)
    c.paint(cx - 2, cx + 2, ys, yh, ID_FRAME, 1.0, 0.50, height=REVEAL_D + 0.015)
    for b in range(1, bars + 1):
        yy = ys + (yh - ys) * b / (bars + 1)
        c.paint(cx - w, cx + w, yy - 2, yy + 2, ID_FRAME, 1.0, 0.50,
                height=REVEAL_D + 0.015)
    # sill, with soft weathering below it
    moulding(c, cx - w - m(0.34), cx + w + m(0.34), ys - m(0.30), ys - m(0.14), CORNICE_H,
             axes="xy")
    sill_grime(c, n01, cx, w, ys)


def paint_facade(c, n01):
    draw_wall_bands(c, 0, ATLAS, 0)
    bays = 10
    edges = [int(round(ATLAS * i / bays)) for i in range(bays + 1)]
    for i in range(bays):
        cx = (edges[i] + edges[i + 1]) / 2.0
        draw_rect_window(c, n01, cx, 0.70, 0, sill=Z_GF_SILL, head=Z_GF_HEAD)
        draw_rect_window(c, n01, cx, 0.70, 0)
        # slender pilaster on the bay joint, upper storey only
        moulding(c, edges[i] - m(0.10), edges[i] + m(0.10), m(Z_STRING_TOP),
                 m(Z_FRIEZE_BOT), TRIM_H, TRIM_SH, axes="x")
    # the pilaster on the joint at u = 0 is split across the wrap: its other half
    moulding(c, ATLAS - m(0.10), ATLAS, m(Z_STRING_TOP), m(Z_FRIEZE_BOT), TRIM_H,
             TRIM_SH, axes="x")


def paint_roof(c):
    """Standing-seam steel, V stretched across each slope. The seams vary in
    U only; the transverse joints vary in V and are scaled for the stretch."""
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0, y0 + h, ID_ROOF, 1.0, 1.0, height=0.0)
    seam = round(m(0.5))
    sy, sx, Y, X = c.field(0, ATLAS, y0, y0 + h)
    xs = X % seam
    rib = xs < 3.0
    height = np.where(rib, SEAM_H * np.clip(np.sin(np.pi * xs / 3.0), 0, 1), 0.0)
    shade = np.where((xs >= 3.0) & (xs < 5.0), ROOF_DK, 1.0)
    ao = np.where((xs >= 3.0) & (xs < 4.0), 0.82, np.where((xs >= 4.0) & (xs < 5.0), 0.86, 1.0))
    for k in range(1, 4):
        yk = y0 + h * k / 4.0
        joint = np.abs(Y - yk) < 1.0
        shade = np.where(joint, ROOF_DK, shade)
        height = np.where(joint, height - 0.004, height)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao


def paint_entrance(c, n01):
    ex0, ex1, ey0, ey1 = ENT
    draw_wall_bands(c, ex0, ex1, ey0)
    ec = (ex0 + ex1) / 2.0
    # central arched doorway: surround, dark reveal, door, fanlight
    tr = ey0 + m(2.50)
    arch(c, ec, m(1.26), ey0 + m(0.05), ey0 + m(2.60), ID_TRIM, 1.0, height=TRIM_H)
    arch(c, ec, m(1.10), ey0 + m(0.10), ey0 + m(2.60), ID_DARK, 1.0, 0.38, height=REVEAL_D)
    arch(c, ec, m(1.00), ey0 + m(0.15), ey0 + m(2.60), ID_GLASS, 1.0, 0.50, height=REVEAL_D)
    c.paint(ec - m(1.00), ec + m(1.00), ey0 + m(0.15), tr, ID_DOOR, 1.0, 0.52,
            height=REVEAL_D)
    c.paint(ec - m(1.00), ec + m(1.00), tr - m(0.08), tr, ID_FRAME, 1.0,
            height=REVEAL_D + 0.015)
    c.paint(ec - 2, ec + 2, ey0 + m(0.15), tr - m(0.08), ID_FRAME, 1.0,
            height=REVEAL_D + 0.010)
    # Entrance threshold, drawn up from the panel's baseline instead of down
    # from the door sill. ey0 is z = 0 -- the ENT region is mapped from the
    # ground up, so there is no such thing as artwork below that line. The
    # three stacked steps that used to be here ran downwards from the sill,
    # which put all of them up to 0.21 m underground and into the roof band
    # underneath, where every slope's UVs read them back as a pale patch.
    c.paint(ec - m(1.9), ec + m(1.9), ey0, ey0 + m(0.15), ID_PLINTH, 1.0, 0.74, height=0.0)
    c.paint(ec - m(1.9), ec + m(1.9), ey0, ey0 + m(0.04), ID_PLINTH, PLINTH_DK, 0.66)
    # flanking windows on the ground floor
    for off in (-3.30, 3.30):
        draw_rect_window(c, n01, ec + m(off), 0.70, ey0, sill=Z_GF_SILL, head=Z_GF_HEAD)
    # Wall behind the balcony only. The balcony itself is modelled geometry, so
    # painting a balustrade here would show through beside the real one.
    c.paint(ec - m(2.4), ec + m(2.4), ey0 + m(Z_STRING_BOT) - 4,
            ey0 + m(Z_STRING_TOP) + m(0.05), ID_TRIM, 1.0, height=0.0)
    # upper storey: the balcony door, runs down to the slab and carries more
    # glazing bars so it reads as a door leaf, between two tall windows
    draw_rect_window(c, n01, ec, 0.62, ey0, sill=5.60, head=9.10, bars=5)
    for off in (-1.85, 1.85):
        draw_rect_window(c, n01, ec + m(off), 0.62, ey0, sill=6.60, head=9.10, bars=3)
    for off in (-2.85, -0.92, 0.92, 2.85):
        moulding(c, ec + m(off) - m(0.16), ec + m(off) + m(0.16), ey0 + m(Z_STRING_TOP),
                 ey0 + m(Z_FRIEZE_BOT), TRIM_H, TRIM_SH, axes="x")
    for off in (-4.05, 4.05):
        draw_rect_window(c, n01, ec + m(off), 0.68, ey0)


def paint_attic(c):
    """The clock attic: a framed panel with the dial, under a pediment."""
    ax0, ax1, ay0, ay1 = ATT
    c.paint(ax0, ax1, ay0, ay1, ID_WALL, 1.0, 1.0, height=0.0)
    moulding(c, ax0 + m(0.4), ax1 - m(0.4), ay0 + m(0.25), ay0 + m(3.05), TRIM_H, axes="xy")
    c.paint(ax0 + m(0.7), ax1 - m(0.7), ay0 + m(0.50), ay0 + m(2.80), ID_WALL, WALL_DK,
            height=0.0)
    cx, cy, r = (ax0 + ax1) / 2.0, ay0 + m(1.85), m(0.98)
    # the dial is modelled on the near tiers; this paint is what LOD2 shows
    c.disc(cx, cy, r, ID_TRIM, 1.0, height=0.0)
    c.disc(cx, cy, r * 0.84, ID_CLOCK, 1.0)
    for k in range(12):
        a = 2 * np.pi * k / 12.0
        tx, ty = cx + np.sin(a) * r * 0.70, cy + np.cos(a) * r * 0.70
        c.paint(tx - 2, tx + 3, ty - 2, ty + 3, ID_DARK, 1.0)
    c.paint(cx - 1, cx + 2, cy, cy + r * 0.60, ID_DARK, 1.0)
    c.paint(cx - r * 0.40, cx + 2, cy - 1, cy + 2, ID_DARK, 1.0)
    # No plaque below the dial. A painted one used to sit here, 2.2 m wide
    # against the dial's 1.96 m and reaching from 0.25 m below the dial's foot
    # up behind it. The dial is modelled, so the painted disc is hidden under it
    # and the only part of the plaque left showing was the strip poking out
    # underneath -- it read as a white tab hanging off the clock, not as a
    # plaque. There is 0.37 m of clear wall between the dial's foot and the
    # framed panel's bottom rail, which is not enough for anything legible.
    # Pediment: white raking cornice over a wall tympanum.
    ped0, ped1 = ay0 + m(3.2), ay0 + m(5.0)
    apex = (ax0 + ax1) / 2.0
    halfw = (ax1 - ax0) / 2.0

    def inside(X, Y):
        t = np.clip((Y - ped0) / max(1.0, ped1 - ped0), 0, 1)
        return (np.abs(X - apex) <= halfw * (1.0 - t)) & (Y >= ped0) & (Y <= ped1)

    def rake(X, Y):
        t = np.clip((Y - ped0) / max(1.0, ped1 - ped0), 0, 1)
        return inside(X, Y) & (np.abs(X - apex) >= halfw * (1.0 - t) - m(0.38))
    c.paint(ax0, ax1, ped0 + m(0.34), ay1, ID_ROOF, 1.0, height=0.0)
    c.shape(ax0, ax1, ped0, ped1, inside, ID_WALL, 1.0, height=0.0)
    c.shape(ax0, ax1, ped0, ped1, rake, ID_TRIM, 1.0, height=CORNICE_H)
    moulding(c, ax0, ax1, ped0, ped0 + m(0.34), CORNICE_H)
    c.paint(ax0, ax1, ay0 + m(3.05), ped0, ID_TRIM, TRIM_SH, 0.70, height=0.0)


def paint_tower(c):
    """Laid out against the orthographic elevation, in metres above the eave:

        0.00-3.25  base, buried below the 14.65 roof deck
        3.25-3.55  plinth band breaking out at deck level
        3.55-5.90  brick base, largely hidden behind the clock attic
        5.90-6.60  balustraded platform
        6.60-8.30  drum, arched louvred openings between corner pilasters
        8.30-8.80  drum cornice
    """
    tx0, tx1, ty0, ty1 = TOW
    tcx = (tx0 + tx1) / 2.0
    c.paint(tx0, tx1, ty0, ty0 + m(5.90), ID_WALL, 1.0, 1.0, height=0.0)
    bricks(c, tx0, tx1, ty0, ty0 + m(5.90), ty0)
    moulding(c, tx0, tx1, ty0 + m(3.25), ty0 + m(3.55), CORNICE_H)
    c.paint(tx0, tx1, ty0 + m(3.55), ty0 + m(3.63), ID_TRIM, TRIM_SH, 0.76)
    for a0, a1 in ((tx0, tx0 + m(0.34)), (tx1 - m(0.34), tx1)):
        moulding(c, a0, a1, ty0 + m(3.63), ty0 + m(5.90), TRIM_H, TRIM_SH, axes="x")

    moulding(c, tx0, tx1, ty0 + m(5.75), ty0 + m(5.90), TRIM_H)
    c.paint(tx0, tx1, ty0 + m(5.90), ty0 + m(6.50), ID_TRIM, 1.0, height=0.0)
    sy, sx, _, X = c.field(tx0, tx1, ty0 + m(5.90), ty0 + m(6.50))
    gap = (X % round(m(0.22))) < round(m(0.11))
    c.shade[sy, sx] = np.where(gap, TRIM_SH, 1.0)
    c.ao[sy, sx] = np.where(gap, 0.80, c.ao[sy, sx])
    c.height[sy, sx] = np.where(gap, -0.010, 0.020)            # balusters proud
    moulding(c, tx0, tx1, ty0 + m(6.50), ty0 + m(6.60), TRIM_H)

    c.paint(tx0, tx1, ty0 + m(6.60), ty0 + m(8.30), ID_WALL, 1.0, height=0.0)
    for a0, a1 in ((tx0, tx0 + m(0.38)), (tx1 - m(0.38), tx1)):
        moulding(c, a0, a1, ty0 + m(6.60), ty0 + m(8.30), TRIM_H, TRIM_SH, axes="x")
    arch(c, tcx, m(0.62), ty0 + m(6.95), ty0 + m(7.85), ID_TRIM, 1.0, height=TRIM_H)
    arch(c, tcx, m(0.48), ty0 + m(7.05), ty0 + m(7.85), ID_DARK, 1.0, 0.36, height=REVEAL_D)
    arch(c, tcx, m(0.41), ty0 + m(7.11), ty0 + m(7.85), ID_FRAME, 1.0, 0.42, height=REVEAL_D)
    # louvre slats, with dark gaps between them; the belfry emits through the
    # gaps (see emission_mask)
    slat, gapw = round(m(0.18)), round(m(0.08))

    def slot(X, Y):
        r, ys, yp = m(0.41), ty0 + m(7.11), ty0 + m(7.85)
        inside = (((np.abs(X - tcx) <= r) & (Y >= ys) & (Y <= yp))
                  | (((X - tcx) ** 2 + (Y - yp) ** 2 <= r * r) & (Y > yp)))
        return inside & (((Y - ty0) % slat) < gapw)
    c.shape(tcx - m(0.42), tcx + m(0.42), ty0 + m(7.11), ty0 + m(8.27), slot, ID_DARK,
            1.0, 0.36, height=REVEAL_D - 0.010)

    c.paint(tx0, tx1, ty0 + m(8.26), ty0 + m(8.34), ID_DARK, 1.0, 0.48, height=0.0)
    moulding(c, tx0, tx1, ty0 + m(8.34), ty1, CORNICE_H)
    sy, sx, _, X = c.field(tx0, tx1, ty0 + m(8.34), ty0 + m(8.58))
    tooth = (X % round(m(0.24))) < round(m(0.11))
    c.shade[sy, sx] = np.where(tooth, TRIM_SH, c.shade[sy, sx])
    c.height[sy, sx] = np.where(tooth, c.height[sy, sx] + DENTIL_H, c.height[sy, sx])


def paint_chimney(c):
    cx0, cx1, cy0, cy1 = CHM
    c.paint(cx0, cx1, cy0, cy1, ID_CHIM, 1.0, 0.92, height=0.0)
    bricks(c, cx0, cx1, cy0, cy1, cy0, mid=ID_CHIM, tones=(1.0, 1.0, CHIM_DK, 1.0),
           joints=False)
    sy, sx, Y, _ = c.field(cx0, cx1, cy0, cy1)
    course = ((Y - cy0) % round(m(0.075))) < 1.0
    c.shade[sy, sx] = np.where(course, CHIM_DK, c.shade[sy, sx])
    c.height[sy, sx] = np.where(course, -0.003, 0.0)
    c.paint(cx0, cx1, cy1 - m(0.46), cy1 - m(0.34), ID_CHIM, CHIM_CAP, 0.88, height=0.030)
    c.paint(cx0, cx1, cy1 - m(0.34), cy1, ID_ROOF, 0.73, 0.70, height=0.0)


def paint_quoins(c):
    """Toothed corner strip: alternating courses run the full width or stop
    short, which is what reads as interlocking corner stones once wrapped on
    the block. The stones stand proud of the brick behind them."""
    qx0, qx1, qy0, qy1 = QUOIN
    c.paint(qx0, qx1, qy0, qy1, ID_WALL, 1.0, height=0.0)
    bricks(c, qx0, qx1, qy0, qy1, qy0)
    course_h = m(0.46)
    for k in range(int((qy1 - qy0) / course_h) + 1):
        cy = qy0 + k * course_h
        bx1 = qx1 if k % 2 == 0 else qx0 + (qx1 - qx0) * 0.62
        c.paint(qx0, bx1, cy + 1, cy + course_h - 1, ID_TRIM, 1.0)
        c.bevel(qx0, bx1, cy + 1, cy + course_h - 1, TRIM_H, 1.0,
                axes="y" if k % 2 == 0 else "xy")
        c.paint(qx0, bx1, cy + course_h - 3, cy + course_h - 1, ID_TRIM, TRIM_SH, 0.82)


def paint_balcony(c):
    """The balcony parapet: solid, with the balusters as relief."""
    bx0, bx1, by0, by1 = BALUS
    c.paint(bx0, bx1, by0, by1, ID_TRIM, 1.0, height=0.0)
    moulding(c, bx0, bx1, by0, by0 + m(0.14), TRIM_H, TRIM_SH, 0.78)
    sy, sx, _, X = c.field(bx0, bx1, by0 + m(0.14), by1 - m(0.16))
    gap = (X % round(m(0.22))) < round(m(0.10))
    c.shade[sy, sx] = np.where(gap, TRIM_SH, 1.0)
    c.ao[sy, sx] = np.where(gap, 0.72, 1.0)
    c.height[sy, sx] = np.where(gap, -0.015, 0.020)
    moulding(c, bx0, bx1, by1 - m(0.16), by1, TRIM_H)


def paint_patches(c):
    c.paint(BLANK[0], BLANK[1], BLANK[2], BLANK[3], ID_WALL, WALL_DK, 0.60, height=0.0)
    c.paint(TRIMPATCH[0], TRIMPATCH[1], TRIMPATCH[2], TRIMPATCH[3], ID_TRIM, 1.0,
            height=0.0)
    c.paint(REVEALP[0], REVEALP[1], REVEALP[2], REVEALP[3], ID_TRIM, REVEAL, 0.50,
            height=0.0)
    # Soot inside the flues: the dark id taken down to about sRGB 30, and
    # occluded, as a narrow shaft is whatever the sun does.
    c.paint(SOOT[0], SOOT[1], SOOT[2], SOOT[3], ID_DARK, 0.36, 0.35, height=0.0)


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    The facade band and the entrance panel both start at the ground and run
    the full wall height with their windows in them, so the plinth's soil, the
    salt bloom above it and the runs under every sill and the string course
    land where they belong. The roof band's V runs across each slope in
    whichever direction the face happens to give, so the roof's weather is
    the same either way up: runs down the slope and silt at the seams, no
    darker eave."""
    w = weathering.Weather(c, clean=(ID_GLASS, ID_CLOCK), steel=(ID_ROOF,))
    w.grime()
    w.fade((ID_TRIM,), amount=0.06, base=0.02)
    w.wash((ID_WALL,))

    def window(cx, half_w, yb, sill):
        """Dirt on the sill moulding, runs down the wall under it."""
        wd, ys = m(half_w), yb + m(sill)
        x0, x1 = cx - wd - m(0.34), cx + wd + m(0.34)
        w.add("D", x0, x1, ys - m(0.30), ys - m(0.14), 0.10, (ID_TRIM,))
        w.runs(x0, x1, ys - m(1.10), ys - m(0.30), (ID_WALL, ID_PLINTH), 0.12, fall=m(0.35))

    for x0, x1, yb in ((0, ATLAS, 0), (ENT[0], ENT[1], ENT[2])):
        w.plinth(x0, x1, yb, yb + m(Z_PLINTH_TOP), (ID_PLINTH,))
        w.bloom(x0, x1, yb + m(Z_PLINTH_CAP), yb + m(Z_PLINTH_CAP + 1.2), (ID_WALL,),
                amount=0.12, fade=m(0.8))
        w.runs(x0, x1, yb + m(Z_STRING_BOT - 0.8), yb + m(Z_STRING_BOT) - 3, (ID_WALL,),
               0.12, fall=m(0.35))
    edges = [int(round(ATLAS * i / 10)) for i in range(11)]
    for i in range(10):
        cx = (edges[i] + edges[i + 1]) / 2.0
        window(cx, 0.70, 0, Z_GF_SILL)
        window(cx, 0.70, 0, Z_UF_SILL)
    ec, ey0 = (ENT[0] + ENT[1]) / 2.0, ENT[2]
    for off in (-3.30, 3.30):
        window(ec + m(off), 0.70, ey0, Z_GF_SILL)
    for off in (-1.85, 1.85):
        window(ec + m(off), 0.62, ey0, 6.60)
    for off in (-4.05, 4.05):
        window(ec + m(off), 0.68, ey0, Z_UF_SILL)
    w.door(ec - m(1.00), ec + m(1.00), ey0 + m(0.15), ey0 + m(2.50), (ID_DOOR,))
    # the roof band, the same whichever way up a slope samples it
    y0, y1 = ROOF_Y0, ROOF_Y0 + ROOF_H
    roof = (ID_ROOF,)
    w.add("D", 0, ATLAS, y0, y1, lambda Y, X, nz: 0.10 * atlas.smoothstep(
        0.0, 1.5, nz("long")) + 0.12 * (((X % round(m(0.5))) >= 3.0)
                                        & ((X % round(m(0.5))) < 6.0)), roof)
    w.add("F", 0, ATLAS, y0, y1, lambda Y, X, nz: 0.05 + 0.04 * nz("big"), roof)
    # the tower: runs under its balustrade and under the drum's cornice
    tx0, tx1, ty0, ty1 = TOW
    w.runs(tx0, tx1, ty0 + m(4.95), ty0 + m(5.75), (ID_WALL,), 0.12, fall=m(0.4))
    w.runs(tx0, tx1, ty0 + m(7.00), ty0 + m(8.26), (ID_WALL,), 0.12, fall=m(0.4))
    # the stacks: runs under the cap
    cx0, cx1, cy0, cy1 = CHM
    w.runs(cx0, cx1, cy0, cy1 - m(0.46), (ID_CHIM,), 0.18, fall=m(0.5))
    # the quoin strip starts at the ground: splashed at the foot
    qx0, qx1, qy0, qy1 = QUOIN
    w.splash(qx0, qx1, qy0, qy0 + m(1.5), (ID_TRIM, ID_WALL))
    # the balcony parapet: runs under its top rail
    bx0, bx1, by0, by1 = BALUS
    w.runs(bx0, bx1, by0 + m(0.14), by1 - m(0.16), (ID_TRIM,), 0.10, fall=m(0.3))
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height."""
    c = atlas.Canvas(ATLAS, ss, PPM)
    n01 = atlas.noise(c, 23, 30.0)
    n01 = (n01 - n01.min()) / max(1e-6, float(n01.max() - n01.min()))
    paint_facade(c, n01)
    paint_roof(c)
    paint_entrance(c, n01)
    paint_attic(c)
    paint_tower(c)
    paint_chimney(c)
    paint_quoins(c)
    paint_balcony(c)
    paint_patches(c)
    # The roof band is the one region tiled under every slope on the building,
    # so a stray sample in it is not a local blemish -- it is repeated across
    # the whole roof. That is not hypothetical: the entrance steps were once
    # painted below their own panel's baseline, landed here, and came back as
    # a pale cap on each slope. The check fails the bake on the next slip.
    c.check_bands({"ROOF": ((ROOF_Y0, ROOF_Y0 + ROOF_H), {ID_ROOF})})

    # Weathering: broad soiling, and a soft darkening toward the ground on the
    # facade band only. Every field is periodic, so the bands still wrap.
    grime = 0.045 * atlas.noise(c, 11, 120.0) + 0.025 * atlas.noise(c, 12, 30.0) \
        + 0.015 * atlas.noise(c, 13, 8.0)
    c.shade *= 1.0 + grime
    c.ao *= np.clip(1.0 + grime * 0.5, 0.7, 1.05)
    sy, sx, Y, _ = c.field(0, ATLAS, 0, m(Z_TOP))
    depth = np.clip(1.0 - Y / m(Z_TOP), 0, 1) ** 2
    c.shade[sy, sx] *= 1.0 - 0.10 * depth
    c.rough_var = 0.12 * grime
    weather(c)
    c.pad()
    return c


def emission_mask(c):
    """Glazing, the clock face, and the belfry's louvre gaps, as coverage.

    Final ownership ids keep clock hands, hour marks, window frames and trim
    dark. The belfry emits through the painted gaps between its louvre slats,
    retaining the opaque shell; ID_DARK also labels unrelated cornice shadows
    and reveals, so only the gaps inside the louvre arch count.
    """
    lit = np.isin(c.mid, (ID_GLASS, ID_CLOCK)).astype(np.float32)
    tx0, tx1, ty0, ty1 = TOW
    tcx, r = (tx0 + tx1) / 2.0, m(0.41)
    ys, yp = ty0 + m(7.11), ty0 + m(7.85)
    sy, sx, Y, X = c.field(tcx - r - 1, tcx + r + 1, ys, yp + r + 1)
    arch_in = (((np.abs(X - tcx) <= r) & (Y >= ys) & (Y <= yp))
               | (((X - tcx) ** 2 + (Y - yp) ** 2 <= r * r) & (Y > yp)))
    lit[sy, sx] = np.maximum(lit[sy, sx], (arch_in & (c.mid[sy, sx] == ID_DARK)))
    return np.repeat(atlas.box(lit, c.ss)[..., None] * 255.0, 3, axis=-1)


def export(out_dir, ss=atlas.SS):
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.012)
    c.weather.dust(cav, (ID_WALL, ID_CHIM))          # in the mortar joints
    path = os.path.join(out_dir, ASSET)
    lut = np.zeros((256, 3), np.float32)
    for i, col in COLOUR.items():
        lut[i] = col
    written = [atlas.save(atlas.orm(c, SURFACE, c.rough_var, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS, ID_CLOCK)),
                          path + "_normal.png"),
               atlas.save(glazing.night_rooms(atlas.coverage(c, ID_GLASS) > 0, emission_mask(c)),
                          path + "_emission.png")]
    glass = atlas.coverage(c, ID_GLASS) >= 0.5
    rgb = glazing.rooms(glass, atlas.albedo(c, lut, grime=0.25 * cav))
    written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, VARIANT)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
