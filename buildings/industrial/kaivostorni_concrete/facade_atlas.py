# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas for kaivostorni_concrete, and the
layout build.py maps into.

This describes one asset and nothing else, so it lives beside build.py rather
than in scripts/. It is the single source of the numbers the two files share:
build.py imports the z-levels, opening sizes and region rects from here, so
the pixel layout and the UVs cannot drift apart. Importing this module only
defines those constants; the painting runs when paint() is called.
Rasterising is scripts/atlas.py's.

    python3 facade_atlas.py export      # writes every map into ./export

A trim sheet, not one picture per elevation:

    y    0 ..  262   S1      board-marked concrete, z 0 .. 4.00 from the
                             ground: splash, soil and algae at its foot
    y  262 ..  526   W2      the same concrete above 4.00 m, repeating every
                             4.00 m in V (rows 266 .. 522), its opposite
                             ends carried into its gutters
    y  530 ..  550   FASCIA  steel fascia under the roof's edge, a
                             half-round galvanised gutter across its top
    y  554 ..  670   ROOF    profiled steel sheet, V stretched up the slope,
                             a galvanised snow guard 0.5 m up from the eave
    y  674 ..  710   LEDGE   the base's sloped top, trowelled concrete
    y  716 .. 1024   unique  the doors, the window, the louvre, the rope
                             opening, flat patches, the sheave card (32 px/m)
                             and the sheave bay's picture for the flat tier

Every band spans the full width and tiles in U. The tower is 21 m to its
eave, which no band at 64 px/m holds in a 1024 atlas, so W2 tiles in V:
build.py cuts every wall at 4, 8, 12, 16 and 20 m and maps each 4 m strip
onto the same rows. Cast concrete does the same thing: it is poured in
lifts, each leaving a lift line where the next pour starts, so the repeat
sits on a line the eye expects. A lift here is 2 m, two to each repeat, and
S1 is the same pattern from the ground, so the boards and lift lines run on
unbroken through every joint. Every noise over the bands repeats on W2's
256 rows (atlas.noise(tile_y=4)); weather that follows height (splash, soil,
algae) goes only on S1, whose V is height from the ground.
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

ASSET = "kaivostorni_concrete"
ATLAS = 1024
PPM = 64.0

# --------------------------------------------------------- vertical layout
# Metres above ground.
Z_FLOOR = 0.10       # floor slab and both door thresholds
W2_P = 4.0           # W2's repeat, 256 px
JOINTS = (4.0, 8.0, 12.0, 16.0, 20.0)   # where the walls change strips
LIFT = 2.0           # a pour's height, 128 px: two lifts to each repeat
BOARD = 0.125        # formwork board width, 8 px: 16 boards to a lift
TIE_ROWS = (0.5, 1.5)   # form-tie holes, metres above each lift line
TIE_PITCH = 1.0      # along the wall, staggered by half on the upper row

# ------------------------------------------------------------- openings
# kind -> (width, height, surround side, surround bottom, surround top),
# metres. The surround is the smooth concrete a formwork box leaves round an
# opening, painted, never modelled; a window's and a louvre's bottom is a
# precast sill. Doors have no bottom surround.
OPENINGS = {
    "door_vehicle": (3.20, 3.40, 0.10, 0.0, 0.12),
    "door": (0.95, 2.10, 0.10, 0.0, 0.12),
    "win": (0.80, 1.00, 0.10, 0.15, 0.10),
    "louvre": (1.20, 1.00, 0.10, 0.12, 0.10),
    "rope": (1.10, 1.70, 0.10, 0.12, 0.10),     # where the hoist ropes leave
}
REVEAL_DEPTH = {"win": 0.20, "louvre": 0.15, "door": 0.15, "door_vehicle": 0.20,
                "rope": 0.25}

# ------------------------------------------------------------ sheave bay
# The head room's front is open over the sheave deck: a bay BAY_W x BAY_H,
# its sill on the deck, showing two spoked rope sheaves edge-on to the
# hoist, so face-on to the front. Bay-local metres: u along the wall from
# the bay's west jamb, z up from its sill. build.py models the bay and the
# sheaves from these numbers; flat tiers map the bay onto the region below,
# where paint_bay() draws the same sheaves where the geometry has them.
BAY_W, BAY_H = 5.80, 3.25
SHEAVE_R = 1.60              # rim's outside: a 3.2 m sheave
SHEAVE_RI = 1.42             # rim's inside
HUB_R = 0.22
SPOKES = 8
SPOKE_W = 0.10               # in the sheave's plane
SHEAVES = ((1.80, 1.50), (4.05, 1.50))   # (u, z) centres, the front sheave first
ROPE_SET = 0.05              # the rope's axis, inside the rim's outside (the groove)
ROPE_D = 0.05
ROPE_ANGLE = 20.0            # the ropes fall this far below level toward the hoist


def rope_lines(reach=BAY_W):
    """Each sheave's two ropes, bay-local ((u, z), (u, z)) segments: the
    one down into the shaft off the sheave's west side, to just under the
    deck, and the one leaving its top on the hoist's side, falling
    ROPE_ANGLE, to u = *reach*. Each starts a little inside the rim, where
    the rope lies in its groove."""
    a = math.radians(ROPE_ANGLE)
    du, dz = math.cos(a), -math.sin(a)
    r = SHEAVE_R - ROPE_SET
    out = []
    for u, z in SHEAVES:
        drop = ((u - r, z + 0.15), (u - r, -0.10))
        tu, tz = u + r * math.sin(a), z + r * math.cos(a)        # the tangent point
        t = (reach - tu) / du
        lead = ((tu - 0.15 * du, tz - 0.15 * dz), (tu + t * du, tz + t * dz))
        out.append((drop, lead))
    return out

# ------------------------------------------------------------ atlas bands
S1_Y0 = 2.0                  # v of z = 0
S1_TOP = S1_Y0 + W2_P * PPM  # 258: v of z = 4.00
W2_Y0, W2_H = 266.0, 256.0   # v of a joint; the band repeats every W2_H
FASC_Y0, FASC_H = 532.0, 16.0   # = the roof slabs' 0.25 m vertical thickness
GUTTER_PX = 8.0      # the gutter's rows, 0.125 m, hung across the fascia's top
# The downpipes' and the ladder's sides span the middle five of them
# (scripts/downpipes.py, scripts/roof_safety.py)
PIPE_STRIP = (FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 - 2.5,
              FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 + 2.5)
ROOF_Y0, ROOF_H = 556.0, 112.0
# The annex's slope, from the shaft's wall to its fascia's top, in metres:
# the roof band stretches it over ROOF_H rows, and the head room's shorter
# slopes sample its lower rows at the same scale. build.py asserts it
# against the massing.
ROOF_SLOPE_LEN = 4.8740
LEDGE_Y0, LEDGE_H = 676.0, 32.0  # the base's 45 degree top, 0.50 m of slope
UNI_Y0 = 716.0

ITEM_ORIGIN = {
    "door_vehicle": (4.0, UNI_Y0),
    "door": (232.0, UNI_Y0),
    "win": (316.0, UNI_Y0),
    "louvre": (390.0, UNI_Y0),
    "rope": (316.0, 804.0),
}
PATCHES = {name: (494.0 + 14.0 * i, UNI_Y0, 8.0, 8.0) for i, name in enumerate(
    ("soffit", "csoffit", "reveal", "blank", "barge", "steel", "interior", "rope"))}
BAY_ORIGIN = (608.0, UNI_Y0)     # the bay's sill at its west jamb
# One sheave face-on on dark, at half density, for the tier that builds each
# sheave as a plain disc (build.py): its faces sample this, centred.
CARD_PPM = 32.0
CARD_ORIGIN = (496.0, 740.0)     # lower left; the card is 2 SHEAVE_R square



def item_size_px(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    return (w + 2.0 * cs) * PPM, (h + cb + ct) * PPM


# ----------------------------------------------------------- material ids
ID_WALL, ID_SURR, ID_SILL, ID_FRAME, ID_GLASS, ID_DOOR = 0, 1, 2, 3, 4, 5
ID_ROOF, ID_METAL, ID_GUTTER, ID_BLANK, ID_HANDLE, ID_DARK = 6, 7, 8, 9, 10, 11
# (roughness, metallic). The steel doors, window frames and louvres are
# painted, so the light sees paint, not metal; the gutter, downpipes, ladder
# and snow guard are galvanised.
SURFACE = {
    ID_WALL: (0.90, 0.0), ID_SURR: (0.86, 0.0), ID_SILL: (0.84, 0.0),
    ID_FRAME: (0.50, 0.0), ID_GLASS: (glazing.ROUGHNESS, 0.0),
    ID_DOOR: (0.55, 0.0), ID_ROOF: (0.46, 0.25), ID_METAL: (0.44, 0.25),
    ID_GUTTER: (0.48, 0.60), ID_BLANK: (0.95, 0.0), ID_HANDLE: (0.40, 0.70),
    ID_DARK: (0.95, 0.0),
}

# ---------------------------------------------------------------- palettes
# A restrained landmark: one coherent treatment per instance. Bare grey
# concrete with grey-green steelwork, or the same concrete under an ochre
# lime wash with oxide-red doors and a red-brown roof.
VARIANTS = {
    "grey_concrete": {"wall": (138, 136, 130), "frame": (92, 100, 96),
                      "door": (78, 88, 84), "roof": (66, 68, 70)},
    "ochre_render": {"wall": (176, 146, 100), "frame": (86, 82, 76),
                     "door": (110, 62, 50), "roof": (84, 62, 54)},
}
DEFAULT_VARIANT = "grey_concrete"
# The atlas has one window region, so the whole building is one pane to
# glazing.rooms(), and its room level is drawn once; GLASS_BASE scales the
# base so that one draw lands mid-band (measured in notes.md).
GLASS_BASE = tuple(int(round(v * 1.35)) for v in glazing.BASE)
FIXED = {
    ID_GLASS: glazing.BASE, ID_GUTTER: (134, 137, 137), ID_BLANK: (52, 52, 52),
    ID_HANDLE: (150, 148, 142), ID_DARK: (30, 30, 30),
}

BAND_IDS = {
    "S1": ((0, S1_TOP + 4), {ID_WALL}),
    "W2": ((W2_Y0 - 4, W2_Y0 + W2_H + 4), {ID_WALL}),
    "FASCIA": ((FASC_Y0 - 2, FASC_Y0 + FASC_H + 2), {ID_METAL, ID_GUTTER}),
    "ROOF": ((ROOF_Y0 - 2, ROOF_Y0 + ROOF_H + 2), {ID_ROOF, ID_METAL, ID_GUTTER}),
    "LEDGE": ((LEDGE_Y0 - 2, LEDGE_Y0 + LEDGE_H + 2), {ID_SURR}),
}
TILE = int(ATLAS // W2_H)            # 4: every noise repeats every 256 rows

# ---------------------------------------------------------------- relief
FIN_H = 0.0015       # the grout fin a board joint leaves
GRAIN_H = 0.0005     # the boards' grain printed in the concrete
LIFT_D = 0.004       # a lift line's recess
TIE_D = 0.010        # a form-tie hole, plugged short of the face
SURR_H = 0.0         # the smooth surround is flush with the boards
SILL_H = 0.035       # precast sill's nose
FRAME_H = 0.025      # steel window frames, proud of the glass
BAR_H = 0.015        # glazing bars
LEAF_H = 0.020       # door frames and rails
RIB_H = 0.020        # the roof sheet's trapezoidal ribs
GUTTER_R = 0.0625    # the half-round gutter's radius, 125 mm across
SNOW_TUBE_H = 0.035  # the snow guard's tubes, proud of the sheet
SNOW_BRACKET_H = 0.030
SNOW_GUARD_M = 0.50  # the snow guard's lower tube, up the slope from the eave


def m(v):
    """Metres -> pixels."""
    return v * PPM


def noise(c, seed, sx, sy=None):
    """atlas.noise() on W2's period, so every band stays seamless in V."""
    return atlas.noise(c, seed, sx, sy, tile_y=TILE)


# ============================================================ painting
def paint_concrete(c, y_lo, y_hi, y_ref, seed=11):
    """Board-marked concrete across the full width, rows y_lo..y_hi, phased
    so that y_ref is a lift line. Everything is periodic in W2_H rows and in
    the atlas width, so S1 and W2 are one pattern and both wrap.

    Each 0.125 m board row has its own tone and its own butt joints, the
    joint between two boards leaves a small grout fin, every 2 m lift starts
    on a dark recessed lift line with a grout leak over the top of the lift
    below, and the plugged form-tie holes sit in two staggered rows a lift."""
    sy, sx, Y, X = c.field(0, ATLAS, y_lo, y_hi)
    lp, bp = m(LIFT), m(BOARD)
    v = np.mod(Y - y_ref, W2_H)
    lift = np.floor(v / lp).astype(np.int64)
    vl = v - lift * lp                                    # up from the lift line
    b = np.floor(v / bp).astype(np.int64) % int(W2_H // bp)
    vb = v - np.floor(v / bp) * bp
    tone = (1.0 + 0.09 * (atlas.hash_unit(seed, b) - 0.5)
            + 0.07 * (atlas.hash_unit(seed + 3, lift) - 0.5))
    # butt joints: boards 2 m long, each row's joints at its own offset
    off = atlas.hash_unit(seed + 5, b) * m(2.0)
    xb = np.mod(X - off, m(2.0))
    butt = xb < 0.8
    fin = vb < 0.9
    shade = np.where(fin, tone * 0.95, tone)
    shade = np.where(butt, shade * 0.90, shade)
    height = np.where(fin, FIN_H, 0.0) + np.where(butt, -0.001, 0.0)
    ao = np.where(fin | butt, 0.93, 1.0)
    # the lift line, and the grout that leaked over the lower lift's top
    line = vl < 2.2
    shade = np.where(line, shade * 0.72, shade)
    ao = np.where(line, np.minimum(ao, 0.82), ao)
    height = np.where(line, -LIFT_D, height)
    leak = vl > lp - 4.0
    shade = np.where(leak, shade * 0.94, shade)
    # form-tie holes
    for k, zr in enumerate(TIE_ROWS):
        px = m(TIE_PITCH)
        xo = np.mod(X - k * px / 2.0, px) - px / 2.0
        hole = np.hypot(xo, vl - m(zr)) < 1.3
        shade = np.where(hole, shade * 0.60, shade)
        ao = np.where(hole, np.minimum(ao, 0.65), ao)
        height = np.where(hole, -TIE_D, height)
    c.mid[sy, sx] = ID_WALL
    c.shade[sy, sx], c.ao[sy, sx], c.height[sy, sx] = shade, ao, height


def paint_fascia(c):
    """The eave's vertical edge: a steel fascia in the roof's metal, with a
    half-round galvanised gutter hung across its top, right under the roof's
    edge; the fascia shows below it. Only eave fascias sample this band
    (rakes take the barge patch)."""
    y0, top = FASC_Y0, FASC_Y0 + FASC_H
    gh = GUTTER_PX
    g0 = top - 1 - gh
    c.paint(0, ATLAS, y0 - 2, top + 2, ID_METAL, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, g0, 0.008, 1.0, axes="y")
    c.paint(0, ATLAS, y0 - 2, y0 + 1, ID_METAL, 0.86)              # drip edge
    c.paint(0, ATLAS, g0, top - 1, ID_GUTTER, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top - 1)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_GUTTER, 0.80)
    c.paint(0, ATLAS, top - 1, top + 2, ID_METAL, 0.80, height=0.0)  # sheet's drip edge
    c.ao[c.sl(0, ATLAS, g0 - 3, top + 2)] = 0.9
    for k, f in enumerate((0.92, 0.86, 0.80)):            # occluded under the gutter
        c.mul(0, ATLAS, g0 - 3 + k, g0 - 2 + k, f)
    # hangers every 1.0 m; on the downpipes and the ladder they read as clips
    sy, sx, _, X = c.field(0, ATLAS, g0 + 2, top - 1)
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.80, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_roof(c):
    """Profiled steel sheet, V stretched up the slope (ROOF_H rows over
    ROOF_SLOPE_LEN metres). Ribs vary in U only; the snow guard and the
    flashing at the top, where the annex meets the shaft, vary in V, so
    their heights are scaled by the band's px/m over PPM. Every slope's V
    starts at its eave (build.py's slab()), so the snow guard lands
    SNOW_GUARD_M up from the eave on every slope."""
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
    g = round(SNOW_GUARD_M * h / ROOF_SLOPE_LEN)
    guard = np.zeros(v.shape, bool)
    for t0, t1 in ((g, g + 2.0), (g + 3.0, g + 4.5)):
        inside = (v >= t0) & (v < t1)
        tube = SNOW_TUBE_H * k * np.sqrt(np.clip(
            1.0 - (2.0 * (v - t0) / (t1 - t0) - 1.0) ** 2, 0.0, 1.0))
        height = np.where(inside, np.maximum(height, tube), height)
        shade = np.where(inside, 1.0, shade)
        guard |= inside
    shade = np.where((v >= g - 3) & (v < g - 1), shade * 0.80, shade)
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


def paint_ledge(c):
    """The base's sloped top: trowelled concrete, a little darker where it
    holds the wet, with an arris at its foot."""
    y0, h = LEDGE_Y0, LEDGE_H
    c.paint(0, ATLAS, y0 - 2, y0 + h + 2, ID_SURR, 0.97, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 - 2, y0 + 1.5, ID_SURR, 0.92, 0.92)
    c.paint(0, ATLAS, y0 + h - 2, y0 + h + 2, ID_SURR, 0.88, 0.80)   # into the shaft


def _frame(c, x0, x1, y0, y1, w, mid=ID_FRAME, h=FRAME_H, shade=1.0):
    """A rectangular frame w px wide, bevelled on both edges."""
    for a0, a1, b0, b1, ax in ((x0, x0 + w, y0, y1, "x"), (x1 - w, x1, y0, y1, "x"),
                               (x0, x1, y0, y0 + w, "y"), (x0, x1, y1 - w, y1, "y")):
        c.paint(a0, a1, b0, b1, mid, shade, 0.92)
        c.bevel(a0, a1, b0, b1, h, 0.8, axes=ax)


def paint_opening(c, kind):
    """One opening's region: the smooth surround, the precast sill, then the
    window, door or louvre inside it."""
    x0, y0 = ITEM_ORIGIN[kind]
    w, h, cs, cb, ct = OPENINGS[kind]
    rw, rh = item_size_px(kind)
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0 + m(cb), y0 + m(cb + h)
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, ID_SURR, 1.03, 1.0, height=SURR_H)
    # the formwork box's edge: a faint line round the surround
    for a0, a1, b0, b1 in ((x0, x0 + 1, y0, y0 + rh), (x0 + rw - 1, x0 + rw, y0, y0 + rh),
                           (x0, x0 + rw, y0 + rh - 1, y0 + rh)):
        c.mul(a0, a1, b0, b1, 0.90, ao=0.92)
    c.mul(ox0 - 1, ox1 + 1, oy1, oy1 + 2, 0.88, ao=0.84)          # under the head
    if cb > 0:                                                     # precast sill
        c.paint(x0 - 2, x0 + rw + 2, y0 - 2, oy0, ID_SILL, 1.0, 1.0)
        c.bevel(x0, x0 + rw, y0, oy0, SILL_H, 1.5, axes="y")
        c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + 1.5, ID_SILL, 0.78, 0.8)   # drip
        c.mul(ox0, ox1, oy0 - 2, oy0, 0.90, ao=0.86)               # sill's back
    if kind == "door_vehicle":
        paint_vehicle_door(c, ox0, ox1, oy0, oy1)
    elif kind == "door":
        paint_door(c, ox0, ox1, oy0, oy1)
    elif kind == "louvre":
        paint_louvre(c, ox0, ox1, oy0, oy1)
    elif kind == "rope":
        paint_rope_opening(c, ox0, ox1, oy0, oy1)
    else:
        paint_window(c, ox0, ox1, oy0, oy1)


def paint_window(c, x0, x1, y0, y1):
    """A small steel-framed window: a heavy outer frame and glazing bars
    into two lights across and three up, the middle row a bottom-hung
    hopper with its own frame. glazing.rooms() owns the glass's colour; this
    sets its id, its AO and a flat height."""
    F, bar = m(0.05), m(0.03)
    c.paint(x0, x1, y0, y1, ID_GLASS, 1.0, 0.9, height=0.0)
    _frame(c, x0, x1, y0, y1, F)
    xm = (x0 + x1) / 2.0
    c.paint(xm - bar / 2, xm + bar / 2, y0, y1, ID_FRAME, 1.0, 0.92)
    c.bevel(xm - bar / 2, xm + bar / 2, y0, y1, BAR_H, 0.6, axes="x")
    ys = [y0 + F + (y1 - y0 - 2 * F) * k / 3.0 for k in (1, 2)]
    for yy in ys:
        c.paint(x0, x1, yy - bar / 2, yy + bar / 2, ID_FRAME, 1.0, 0.92)
        c.bevel(x0, x1, yy - bar / 2, yy + bar / 2, BAR_H, 0.6, axes="y")
    # the hopper: a second frame inside the middle row, a little proud
    hy0, hy1 = ys[0] + bar / 2, ys[1] - bar / 2
    for a0, a1 in ((x0 + F, xm - bar / 2), (xm + bar / 2, x1 - F)):
        c.mul(a0, a1, hy1 - 1.2, hy1, 0.86, ao=0.84)
    c.mul(x0 + F, x1 - F, y1 - F - 1.5, y1 - F, 0.84, ao=0.82)    # head frame's shadow
    c.paint(xm - 3, xm + 3, hy1 - 2, hy1 - 0.8, ID_HANDLE, 0.9, height=0.02)


def paint_door(c, x0, x1, y0, y1):
    """The pedestrian door: a steel leaf in a steel frame, two pressed
    panels, a lever and a kick plate."""
    F = m(0.05)
    c.paint(x0, x1, y0, y1, ID_DOOR, 1.0, 1.0, height=0.0)
    _frame(c, x0, x1, y0 - 2, y1, F, ID_DOOR, LEAF_H, 0.88)
    lx0, lx1, ly1 = x0 + F, x1 - F, y1 - F
    c.mul(lx0, lx1, ly1 - 2, ly1, 0.86, ao=0.84)
    for p0, p1 in ((y0 + m(0.25), y0 + m(1.00)), (y0 + m(1.20), ly1 - m(0.20))):
        a0, a1 = lx0 + m(0.10), lx1 - m(0.10)
        c.bevel(a0, a1, p0, p1, 0.006, 2.0)
        c.mul(a0, a1, p0, p0 + 1, 0.86)
        c.mul(a0, a0 + 1, p0, p1, 0.90)
    c.paint(lx0 + 1, lx1 - 1, y0, y0 + m(0.22), ID_HANDLE, 0.80, 0.92, height=0.003)
    hx, hy = lx1 - m(0.10), y0 + m(1.05)
    c.paint(hx - 1.5, hx + 1.5, hy - 5, hy + 5, ID_HANDLE, 1.0, 0.9, height=0.01)
    c.stroke((hx, hy + 2), (hx - 8, hy + 2), 2.2, ID_HANDLE, 1.0, 0.9, height=0.04)


def paint_vehicle_door(c, x0, x1, y0, y1):
    """The big steel door: a pair of hinged leaves of pressed steel sheet,
    vertical ribs every 0.2 m, on an angle frame with a mid rail and a
    diagonal brace in each panel rising from the hinge to the meeting
    stiles, three hinges on each outer edge and a drop bolt and hasp at the
    meeting stiles."""
    mid = (x0 + x1) / 2.0
    st = m(0.10)
    ym0, ym1 = y0 + m(1.60), y0 + m(1.72)
    c.paint(x0, x1, y0, y1, ID_DOOR, 1.0, 1.0, height=0.0)
    sy, sx, _, X = c.field(x0, x1, y0, y1)
    xr = np.mod(X - x0, m(0.20))
    rib = np.clip(1.5 - np.abs(xr - m(0.10)), 0.0, 1.0)
    c.height[sy, sx] = 0.006 * rib
    c.shade[sy, sx] = np.where(np.abs(xr - m(0.10) - 1.8) < 0.8, 0.92, 1.0)
    for a, b, hinge_left in ((x0, mid, True), (mid, x1, False)):
        _frame(c, a, b, y0, y1, st, ID_DOOR, LEAF_H, 0.94)
        c.paint(a + st, b - st, ym0, ym1, ID_DOOR, 0.94, 0.92)
        c.bevel(a + st, b - st, ym0, ym1, LEAF_H, 0.8, axes="y")
        c.mul(a + st, b - st, ym0 - 1, ym0, 0.86, ao=0.82)
        for p, q in ((y0 + st, ym0), (ym1, y1 - st)):
            lo_x, hi_x = (a + st, b - st) if hinge_left else (b - st, a + st)
            c.stroke((lo_x, p), (hi_x, q), st * 0.8, mid=ID_DOOR, shade=0.94,
                     clip=(a + st, p, b - a - 2 * st, q - p), height=LEAF_H)
        hx = a + 1 if hinge_left else b - 7
        for hy in (y0 + m(0.35), (y0 + y1) / 2.0, y1 - m(0.45)):
            c.paint(hx, hx + 6, hy - 2, hy + 2, ID_DARK, 1.0, 0.85, height=0.03)
        # rivets along the stiles every 0.25 m
        for yy in np.arange(y0 + m(0.15), y1 - m(0.1), m(0.25)):
            for xx in (a + st / 2, b - st / 2):
                c.disc(xx, yy, 0.9, shade=0.86, height=LEAF_H + 0.004)
    c.paint(mid - 0.75, mid + 0.75, y0, y1, ID_DARK, 1.0, 0.5, height=0.0)   # meeting gap
    for xx in (mid - m(0.12), mid + m(0.06)):
        c.paint(xx, xx + m(0.05), y0 + m(1.15), y0 + m(1.35), ID_HANDLE, 0.9, height=0.03)
    c.paint(mid + m(0.10), mid + m(0.14), y0, y0 + m(0.60), ID_HANDLE, 0.8, height=0.02)
    c.paint(x0, x1, y0, y0 + 2, ID_DOOR, 0.8, 0.7)                    # kick wear


def paint_louvre(c, x0, x1, y0, y1):
    """A steel louvred vent: blades sloping out and down in the frame
    colour, dark between, in a steel frame with a bird mesh behind."""
    F = m(0.05)
    c.paint(x0, x1, y0, y1, ID_DARK, 1.0, 0.5, height=-0.010)
    pitch = m(0.08)
    for yy in np.arange(y0 + F, y1 - F, pitch):
        b = min(yy + pitch - 1.8, y1 - F)
        c.paint(x0, x1, yy, b, ID_FRAME, 0.96, 0.9)
        sy, sx, Y, _ = c.field(x0, x1, yy, b)
        c.height[sy, sx] = 0.022 * (1.0 - (Y - yy) / max(b - yy, 1e-3))
        c.paint(x0, x1, yy, yy + 1, ID_FRAME, 0.80, 0.8)
    _frame(c, x0, x1, y0, y1, F)
    c.mul(x0 + F, x1 - F, y1 - F - 2, y1 - F, 0.78, ao=0.72)


def paint_rope_opening(c, x0, x1, y0, y1):
    """The opening the hoist ropes leave the head room by: open to the dark
    machinery space, in a steel angle frame, with a rope guide roller
    across its foot."""
    F = m(0.05)
    c.paint(x0, x1, y0, y1, ID_DARK, 1.0, 0.45, height=-0.010)
    c.paint(x0 + F, x1 - F, y0 + F, y0 + F + m(0.08), ID_FRAME, 0.80, 0.7)   # roller
    c.bevel(x0 + F, x1 - F, y0 + F, y0 + F + m(0.08), 0.02, 1.0, axes="y")
    _frame(c, x0, x1, y0, y1, F)
    c.mul(x0 + F, x1 - F, y1 - F - 2, y1 - F, 0.78, ao=0.72)


def paint_sheave(c, cx, cy, ppm, shade, ao, rect):
    """One sheave face-on, centred at pixel (cx, cy), *ppm* pixels a metre,
    within *rect* (x0, x1, y0, y1): rim, SPOKES spokes and hub in the
    painted steel, a darker groove round the rim, the hub's boss."""
    x0, x1, y0, y1 = rect
    k = ppm

    def inside(X, Y):
        d = np.hypot(X - cx, Y - cy)
        ang = np.arctan2(Y - cy, X - cx)
        step = 2.0 * np.pi / SPOKES
        off = (np.mod(ang + step / 2.0, step) - step / 2.0) * d   # off the nearest spoke
        rim = (d <= k * SHEAVE_R) & (d >= k * SHEAVE_RI)
        spoke = (np.abs(off) <= k * SPOKE_W / 2.0) & (d < k * SHEAVE_RI)
        return rim | spoke | (d <= k * HUB_R)
    c.shape(x0, x1, y0, y1, inside, ID_DOOR, shade, ao, height=0.02)
    c.shape(x0, x1, y0, y1, lambda X, Y: np.abs(
        np.hypot(X - cx, Y - cy) - k * (SHEAVE_R - ROPE_SET)) < max(1.2, k * 0.02),
        shade=shade * 0.75)
    c.disc(cx, cy, k * 0.08, shade=shade * 0.7, height=0.04)


def paint_card(c):
    """The sheave card: one sheave on the dark of the machinery space."""
    x0, y0 = CARD_ORIGIN
    sz = 2.0 * SHEAVE_R * CARD_PPM
    c.paint(x0 - 2, x0 + sz + 2, y0 - 2, y0 + sz + 2, ID_DARK, 1.0, 0.45, height=0.0)
    paint_sheave(c, x0 + sz / 2.0, y0 + sz / 2.0, CARD_PPM, 0.95, 0.75,
                 (x0, x0 + sz, y0, y0 + sz))


def paint_bay(c):
    """The sheave bay for the tiers that build it flat: the dark machinery
    space, the two sheaves face-on where build.py puts them (the rear one
    first, half hidden by the front one, both occluded as in the bay), and
    their ropes. Only light that holds whatever the sun does is here: the
    rear sheave's AO, never a sunlit rim."""
    x0, y0 = BAY_ORIGIN
    w, h = m(BAY_W), m(BAY_H)
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_DARK, 1.0, 0.45, height=0.0)
    c.mul(x0, x0 + w, y0, y0 + m(0.06), 0.85, ao=0.40)            # the deck's edge
    lines = rope_lines()
    for k in reversed(range(len(SHEAVES))):
        u, z = SHEAVES[k]
        cx, cy = x0 + m(u), y0 + m(z)
        # flat on the facade, they would read lighter than the modelled
        # sheaves deep under the bay's head: darkened as the occlusion
        # there, which holds whatever the sun does
        shade, ao = (0.82, 0.72) if k == 0 else (0.68, 0.55)
        paint_sheave(c, cx, cy, PPM, shade, ao, (x0, x0 + w, y0, y0 + h))
        for (pa, pb) in lines[k]:
            c.stroke((x0 + m(pa[0]), y0 + m(max(pa[1], 0.0))),
                     (x0 + min(m(pb[0]), w), y0 + m(max(pb[1], 0.0))),
                     m(ROPE_D), ID_GUTTER, 0.72 * shade, ao, height=0.025,
                     clip=(x0, y0, w, h))


def paint_patches(c):
    spec = {"soffit": (ID_METAL, 0.86, 0.82), "csoffit": (ID_SURR, 0.94, 0.86),
            "reveal": (ID_SURR, 0.92, 0.75), "blank": (ID_BLANK, 1.0, 0.5),
            "barge": (ID_METAL, 1.0, 1.0), "steel": (ID_DOOR, 1.0, 1.0),
            "interior": (ID_DARK, 1.0, 0.45), "rope": (ID_GUTTER, 0.72, 0.9)}
    atlas.paint_patches(c, PATCHES, spec)


def check_regions():
    """Fail on unique regions that overlap, leave the atlas or start below
    the unique row."""
    rects = {k: ITEM_ORIGIN[k] + item_size_px(k) for k in OPENINGS}
    rects.update({"patch_" + k: r for k, r in PATCHES.items()})   # "rope" is both
    rects["bay"] = BAY_ORIGIN + (m(BAY_W), m(BAY_H))
    rects["card"] = CARD_ORIGIN + (2 * SHEAVE_R * CARD_PPM,) * 2
    problems = atlas.region_problems(rects, ATLAS, bands_top=UNI_Y0, band_gap=0)
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks
    like. Height-following weather goes on S1 only, whose V is height from
    the ground; W2 repeats in V, so it gets only noise on its own period,
    and its runs hang from its own lift lines."""
    w = weathering.Weather(c, clean=(ID_GLASS,),
                           steel=(ID_ROOF, ID_METAL, ID_GUTTER, ID_FRAME, ID_DOOR),
                           tile_y=TILE)
    w.grime()
    w.fade((ID_WALL, ID_SURR, ID_SILL, ID_FRAME, ID_DOOR), amount=0.08)
    w.wash((ID_WALL, ID_SURR), amount=0.05)
    walls = ((0, S1_TOP + 4), (W2_Y0 - 4, W2_Y0 + W2_H + 4))
    # rain streaks down the concrete, long and patchy, on the band period
    for y0, y1 in walls:
        w.add("D", 0, ATLAS, y0, y1, lambda Y, X, nz: 0.26 * atlas.smoothstep(
            0.0, 1.6, nz("long")) + 0.06 * nz("big"), (ID_WALL,))
    # runs hanging under every lift line, where water leaves the cold joint
    lines = [S1_Y0 + m(LIFT), S1_TOP, W2_Y0 + m(LIFT), W2_Y0 + W2_H]
    for yl in lines:
        w.runs(0, ATLAS, yl - 60, yl, (ID_WALL,), 0.28, fall=22.0)
        w.add("F", 0, ATLAS, yl - 6, yl + 2, lambda Y, X, nz: 0.18 * atlas.smoothstep(
            0.5, 1.6, nz("bloom")), (ID_WALL,))                   # lime bloom
    # the W2 gutter under the band holds the runs of the line at its top
    w.runs(0, ATLAS, W2_Y0 - 4, W2_Y0, (ID_WALL,), 0.28, fall=22.0)
    # S1: soil and algae at the foot, splash above it
    w.plinth(0, ATLAS, S1_Y0, S1_Y0 + m(0.30), (ID_WALL,))
    w.splash(0, ATLAS, S1_Y0 + m(0.30), S1_TOP, (ID_WALL,), amount=0.16)
    # the base's ledge: dirt and a green film where it holds the wet
    w.add("D", 0, ATLAS, LEDGE_Y0 - 2, LEDGE_Y0 + LEDGE_H + 2,
          lambda Y, X, nz: 0.12 + 0.12 * nz("blotch"), (ID_SURR,))
    w.add("G", 0, ATLAS, LEDGE_Y0 - 2, LEDGE_Y0 + LEDGE_H + 2,
          lambda Y, X, nz: 0.18 * nz("blotch") * np.exp(-(Y - LEDGE_Y0) / 14.0), (ID_SURR,))
    # the roof band, up the slope from the eave
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, ROOF_SLOPE_LEN, (ID_ROOF,))
    w.add("D", 0, ATLAS, ROOF_Y0 - 2, ROOF_Y0 + ROOF_H + 2, lambda Y, X, nz: 0.10 * (
        (np.mod(X, 16.0) >= 4.0) & (np.mod(X, 16.0) < 6.0)), (ID_ROOF,))
    w.add("R", 0, ATLAS, ROOF_Y0 - 2, ROOF_Y0 + 3, lambda Y, X, nz: 0.12 * nz("speck"),
          (ID_ROOF,))
    # the snow guard: dust on it, rust at its brackets, debris held above it
    g = ROOF_Y0 + round(SNOW_GUARD_M * ROOF_H / ROOF_SLOPE_LEN)
    w.add("D", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.06 + 0.045 * nz("blotch"),
          (ID_GUTTER,))
    w.add("R", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.15 * (
        (np.mod(X, 32.0) >= 1.0) & (np.mod(X, 32.0) < 3.0)), (ID_GUTTER,))
    w.add("D", 0, ATLAS, g + 4.5, g + 14.0, lambda Y, X, nz: 0.22 * nz("blotch")
          * (1.0 - (Y - g - 4.5) / 9.5), (ID_ROOF,))
    w.add("R", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.16 * (
        np.mod(X, 32.0) < 4.0), (ID_ROOF,))
    # the fascia and its gutter, as the catalog's other gutters
    top = FASC_Y0 + FASC_H
    g0 = top - 1 - GUTTER_PX
    w.add("D", 0, ATLAS, FASC_Y0 - 2, g0, 0.05, (ID_METAL,))
    w.runs(0, ATLAS, FASC_Y0 - 2, g0, (ID_METAL,), 0.18, fall=5.0, lo=0.4, hi=1.6)
    w.add("D", 0, ATLAS, g0, g0 + 4, lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"),
          (ID_GUTTER,))
    w.runs(0, ATLAS, g0, top - 1, (ID_GUTTER,), 0.08, fall=4.0, lo=0.4, hi=1.6)
    # openings: sills, heads, door feet and handles, rust on the steel
    for kind, (wd, h, cs, cb, ct) in OPENINGS.items():
        x0, yb = ITEM_ORIGIN[kind]
        rw, rh = item_size_px(kind)
        ox0, ox1 = x0 + m(cs), x0 + m(cs + wd)
        oy0, oy1 = yb + m(cb), yb + m(cb + h)
        if kind == "door":
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR,), handle=(ox1 - m(0.15), oy0 + m(1.05)))
        elif kind == "door_vehicle":
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR,), handle=((ox0 + ox1) / 2.0, oy0 + m(1.25)))
            w.splash(ox0, ox1, oy0, oy0 + m(0.8), (ID_DOOR,), amount=0.25, fall=0.25)
        else:
            w.window(x0, yb, rw, rh, oy0, oy1, m(0.05), (ID_SILL, ID_SURR), (ID_FRAME,))
        w.add("R", ox0, ox1, oy0, oy1, lambda Y, X, nz: 0.10 * nz("speck")
              + 0.05 * nz("blotch"), (ID_FRAME, ID_DOOR))
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_concrete(c, 0, S1_TOP + 4, S1_Y0)
    paint_concrete(c, W2_Y0 - 4, W2_Y0 + W2_H + 4, W2_Y0)
    paint_fascia(c)
    paint_roof(c)
    paint_ledge(c)
    for kind in OPENINGS:
        paint_opening(c, kind)
    paint_patches(c)
    paint_bay(c)
    paint_card(c)
    c.check_bands(BAND_IDS)

    wear = 0.025 * noise(c, 3, 40.0) + 0.015 * noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    conc = c.mid == ID_WALL
    grain = noise(c, 5, 30.0, 0.45)                    # the boards' grain, along U
    c.shade[conc] *= 1.0 + 0.035 * grain[conc]
    c.height[conc] += GRAIN_H * grain[conc]
    mottle = noise(c, 6, 50.0)                         # pour-to-pour mottling
    c.shade[conc] *= 1.0 + 0.04 * mottle[conc]
    pores = noise(c, 9, 0.7)
    smooth = np.isin(c.mid, (ID_SURR, ID_SILL))
    c.shade[smooth] *= 1.0 + 0.025 * pores[smooth]
    c.height[smooth] += 0.0004 * pores[smooth]
    c.height[conc] += 0.0004 * pores[conc]
    roof = c.mid == ID_ROOF
    streak = noise(c, 7, 0.8, 40.0)
    c.shade[roof] *= 1.0 + 0.035 * streak[roof]
    weather(c)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    wall = np.array(pal["wall"], np.float32)
    t[ID_WALL] = wall
    t[ID_SURR] = np.minimum(wall * 1.02, 255)
    t[ID_SILL] = np.minimum(wall * 1.06 + 4, 255)
    t[ID_FRAME] = pal["frame"]
    t[ID_DOOR] = pal["door"]
    t[ID_ROOF] = pal["roof"]
    t[ID_METAL] = np.minimum(np.array(pal["roof"], np.float32) * 1.18 + 6, 255)
    return t


def export(out_dir, ss=atlas.SS):
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.006)
    c.weather.dust(cav, (ID_WALL,), amount=0.12)
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
