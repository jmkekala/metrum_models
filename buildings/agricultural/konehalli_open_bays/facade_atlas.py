# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM and normal atlas for konehalli_open_bays, and the layout
build.py maps into.

This describes one asset and nothing else, so it lives beside build.py rather
than in scripts/. It is also the single source of the numbers the two files
share: build.py imports the massing heights, opening sizes and region rects
from here instead of writing them a second time, so the pixel layout and the
UVs cannot drift apart. Importing this module only defines those constants;
the painting runs when paint() is called. Rasterising is scripts/atlas.py's.

    python3 facade_atlas.py export      # writes every map into ./export

The shed has no glazing, so there is no emission map: see notes.md, Night
lighting.

The atlas is a trim sheet. The full-width bands tile in U; the roof's top
and its underside are regions of their own:

    y    0 ..  272   S1       outer walls, z 0 .. 4.20: footing, board and batten
    y  274 ..  499   ROOF     x 2 .. 379: the roof's top, the whole slope at
                              33 px/m both ways, the snow guard near its foot
                     CEIL     x 382 .. 759: the roof's underside over the open
                              bays, 33 px/m both ways, V = plan depth
    y  500 ..  712   INT      the bays' back wall: footing, bare boards, girts
    y  716 ..  984   unique   bay side walls, both doors, post and corner
                              strips, flat patches, the concrete floor slabs
                              in both doors' reveals (scripts/door_floor.py)
    y  984 .. 1004   FASC_R   the rear (low) eave's fascia with the gutter
    y 1004 .. 1024   FASCIA   the slab's front and rake edges: white board,
                              sheet flashing

The open bays are outside surface of the closed shell, seen in shade, so their
boards are unpainted and their occlusion is painted: the back wall evenly
dark, the side walls and the ceiling darkening with depth from the front.

The roof sheds its water to the rear, so only the rear eave has a gutter, and
the snow guard runs along the roof above it. The roof and the ceiling are the
two largest surfaces, seen from raised views and through the open front; a
full-width band each stretched them to 14 px a metre in V against 64 in U, so
each is now one isotropic region at the most density the two fit at.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import door_floor as DF  # noqa: E402
import weathering  # noqa: E402

ASSET = "konehalli_open_bays"
ATLAS = 1024
PPM = 64.0

# --------------------------------------------------------------- massing
# Metres. Front faces -Y; the mono-pitch roof falls from the front to the rear.
HX, HY = 5.25, 3.00          # outer wall faces: 10.5 x 6.0 m
Z_FOOT = 0.1875              # concrete footing strip under every wall (12 px)
Z_EAVE_F = 4.00              # roof's underside at the front wall line
Z_EAVE_R = 3.00              # ... and at the rear wall line
TAN = (Z_EAVE_F - Z_EAVE_R) / (2.0 * HY)          # 1:6, about 9.5 degrees
FRONT_OV, REAR_OV, RAKE_OV = 0.40, 0.20, 0.40
ROOF_T = 0.25                # slab's vertical thickness = fascia height (16 px)
WALL_INTO = 0.12             # walls run this far up into the slab
Z_WALL_MAX = 4.15            # the side, post and corner regions reach this high


def z_under(y):
    """Height of the roof's underside over plan y."""
    return Z_EAVE_F - (y + HY) * TAN


SLOPE_F = (1.0 + TAN * TAN) ** 0.5
Y_FRONT, Y_REAR = -HY - FRONT_OV, HY + REAR_OV    # the slab's edges in plan
ROOF_SLOPE_LEN = (Y_REAR - Y_FRONT) * SLOPE_F

# ------------------------------------------------------------- openings
# kind -> (width, height, casing side, casing bottom, casing top), metres.
# Both doors stand on the ground and cut the footing, so they have no bottom
# casing. The pair is a vehicle door; the leaf beside it is the way in.
OPENINGS = {
    "door_pair": (3.00, 3.20, 0.125, 0.0, 0.1875),
    "door": (0.90, 2.10, 0.125, 0.0, 0.1875),
}
REVEAL_DEPTH = {"door_pair": 0.15, "door": 0.12}

# ------------------------------------------------------------ atlas bands
S1_Y0 = 2.0                  # v of z = 0 on the outer walls
FASC_H = ROOF_T * PPM        # 16 rows
# The roof's top and its underside, the bays' ceiling: one region each, side
# by side, at ROOF_PPM pixels a metre both ways. U is plan x from the rake
# edge (x = -ROOF_LEN / 2), so the ribs and rafters fall on whole multiples
# of their spacing as before; the roof's V is up the slope from the low
# (rear) edge, the ceiling's plan depth from the slab's front edge. At 64
# px/m the two would need 850 rows; 33 px/m is the most at which they fit
# between S1 and INT.
ROOF_PPM = 33.0
ROOF_LEN = 2.0 * (HX + RAKE_OV)                   # 11.3 m along x
ROOF = (4.0, 276.0, ROOF_LEN * ROOF_PPM, ROOF_SLOPE_LEN * ROOF_PPM)
CEIL = (384.0, 276.0, ROOF_LEN * ROOF_PPM, (Y_REAR - Y_FRONT) * ROOF_PPM)
CEIL_RPM = ROOF_PPM                               # rows per metre of plan depth
INT_Y0 = 502.0               # v of z = 0 on the bays' back wall
INT_TOP = 3.25               # the back wall band reaches this high
UNI_Y0 = 716.0

# The bays' side walls: U is depth from the front wall line, V is height,
# both at true scale. One region serves both walls.
BAY_DEPTH = 5.80             # front wall line to the back wall's inner face
SIDE = (4.0, UNI_Y0, BAY_DEPTH * PPM, Z_WALL_MAX * PPM)
POST_STRIP = 0.15            # white post side at the front of each side wall

# Region origins: the bottom-left of each opening's casing, in pixels.
ITEM_ORIGIN = {
    "door_pair": (384.0, UNI_Y0),
    "door": (600.0, UNI_Y0),
}
POST_W = 0.20                # post section and wall-end width
POST = (682.0, UNI_Y0, POST_W * PPM, Z_WALL_MAX * PPM)
CW = 0.125                   # corner-board width (8 px)
CORNER = (704.0, UNI_Y0, CW * PPM, Z_WALL_MAX * PPM)
PATCHES = {name: (722.0 + 14.0 * i, UNI_Y0, 8.0, 8.0) for i, name in enumerate(
    ("header", "soffit", "reveal", "blank"))}

# The concrete floor slabs in the two doors' reveals (scripts/door_floor.py),
# one region an opening kind, unfolded at 64 px/m: U across the casing from
# its left side, V up the 0.02 m nosing and back across the reveal to the
# leaf. LOD1's recess is the casing's width; LOD0's, inside the casing ring,
# samples the leaf's middle stretch of it. The workshop door's (1.15 x 0.12 m)
# lies in the free rows over the door's region, with a worn path to the leaf;
# the machine door's (3.25 x 0.15 m), a vehicle door that no one walks in on
# a path, lies right of the flat patches and has none.
def _floor(kind, x, y, **kw):
    return DF.Floor(x, y, OPENINGS[kind][0] + 2 * OPENINGS[kind][2], REVEAL_DEPTH[kind], **kw)


FLOORS = {"door": _floor("door", 600, 872),
          "door_pair": _floor("door_pair", 790, 720, tread=-1e3)}

# The two fascia bands, above the unique regions, V = height over the slab's
# underside: the rear (low) edge's with the gutter across its top (FASC_R),
# then the front and rake edges' (FASCIA).
FASC_R_Y0 = 986.0            # v of the rear fascia's bottom edge
FASC_R_TOP = FASC_R_Y0 + FASC_H                   # v of the roof's low edge
FASC_Y0 = 1006.0             # v of the front fascia's bottom edge
GUTTER_PX = 9.0              # the gutter's rows, under the fascia's top row
# The downpipes' sides span the gutter's middle five rows (scripts/downpipes.py)
PIPE_STRIP = (FASC_R_TOP - 1 - GUTTER_PX / 2.0 - 2.5,
              FASC_R_TOP - 1 - GUTTER_PX / 2.0 + 2.5)
SNOW_S = 0.20                # the snow guard's lower tube, up the slope from the
                             # edge: over the rear wall's line
# Its two tubes, metres up the slope from SNOW_S: 50 and 37 mm.
GUARD_TUBES = ((0.0, 0.050), (0.075, 0.1125))

# Board-and-batten: battens over the board joints every 0.2 m. 12.8 px divides
# the atlas width 80 times, so the bands still wrap.
BATTEN_PITCH = 0.20 * PPM
BATTEN_W = 0.05 * PPM


def item_size_px(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    return (w + 2.0 * cs) * PPM, (h + cb + ct) * PPM


# ----------------------------------------------------------- material ids
ID_WALL, ID_TRIM, ID_FOOT, ID_ROOF, ID_DOOR, ID_INNER, ID_SHEET, ID_BLANK, ID_HW = (
    0, 1, 2, 3, 4, 5, 6, 7, 8)
ID_GUTTER = 9                # gutter, downpipes and snow guard: galvanised steel
ID_FLOOR = 10                # the cast concrete floor slabs in the doors' reveals
# (roughness, metallic). Red ochre (punamulta) is a very matte paint; the
# sheet's underside is bare galvanised steel gone dull under dust and
# condensation, kept nearly dielectric: a brighter metallic underside reflected
# the sky into the open bays and lit their ceiling like a skylight. The
# rainwater goods and the snow guard are the farm buildings' one galvanised
# steel, the same in every variant and on navetta_board_gable and
# viljakuivuri_tower: sRGB (134, 137, 137), part metallic, dulled by its zinc
# patina. The roof sheet's top and its folded flashings are coil-coated,
# painted steel: dielectric, as on the farm's other two.
SURFACE = {
    ID_WALL: (0.84, 0.0), ID_TRIM: (0.62, 0.0), ID_FOOT: (0.90, 0.0),
    ID_ROOF: (0.50, 0.0), ID_DOOR: (0.80, 0.0), ID_INNER: (0.88, 0.0),
    ID_SHEET: (0.72, 0.15), ID_BLANK: (0.95, 0.0), ID_HW: (0.55, 0.60),
    ID_GUTTER: (0.48, 0.60), ID_FLOOR: DF.SURFACE,
}

# ---------------------------------------------------------------- palettes
# Colour only: every variant is the same ids and shading. The door leaves'
# planks take the door colour, a shade darker than the wall, their frames and
# braces the trim's. The farmstead's three buildings (this one,
# navetta_board_gable, viljakuivuri_tower) share these numbers exactly, so
# one variant name dresses the set; grey_weathered is unpainted boards gone
# silver with weathered grey trim, lighter than the boards but no white.
VARIANTS = {
    "red_ochre": {"wall": (122, 52, 42), "trim": (221, 217, 205),
                  "roof": (54, 56, 58), "door": (112, 48, 39)},
    "grey_weathered": {"wall": (110, 106, 98), "trim": (150, 146, 137),
                       "roof": (62, 62, 60), "door": (101, 98, 90)},
    "yellow_ochre": {"wall": (184, 148, 86), "trim": (222, 218, 206),
                     "roof": (75, 51, 45), "door": (169, 136, 79)},
}
DEFAULT_VARIANT = "red_ochre"
FIXED = {
    ID_FOOT: (146, 144, 138), ID_INNER: (104, 90, 72), ID_SHEET: (88, 90, 90),
    ID_BLANK: (52, 52, 52), ID_HW: (44, 44, 44), ID_GUTTER: (134, 137, 137),
    ID_FLOOR: DF.COLOUR,
}

# Which ids each tiling band may contain.
BAND_IDS = {
    "S1": ((0, 272), {ID_FOOT, ID_WALL}),
    "INT": ((500, 712), {ID_FOOT, ID_INNER}),
    "FASC_R": ((FASC_R_Y0 - 2, FASC_R_TOP + 2), {ID_TRIM, ID_ROOF, ID_GUTTER}),
    "FASCIA": ((FASC_Y0 - 2, ATLAS), {ID_TRIM, ID_ROOF}),
}

# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto: only what the
# mesh does not model.
BATTEN_H = 0.020     # batten over a board joint
CASING_H = 0.020     # door casings, corner boards, posts' arrises
FRAME_H = 0.020      # a door's frame and brace boards over its planks
RIB_H = 0.030        # profiled sheet's trapezoid ribs
GIRT_H = 0.040       # girts across the inside of the walls (kept shallow)
RAFTER_H = 0.040     # rafters under the sheet (kept shallow; see notes.md)
GUTTER_R = 0.070     # half-round gutter's radius, proud of the rear fascia
SNOW_TUBE_H = 0.035  # the snow guard's tubes over the sheet
SNOW_BRACKET_H = 0.030

# Occlusion in the open bays: what the deepest surfaces keep of the shade and
# AO a surface in the open would have.
BACK_SHADE, BACK_AO = 0.64, 0.42
CEIL_SHADE, CEIL_AO = 0.52, 0.35


def m(v):
    """Metres -> pixels."""
    return v * PPM


def depth_fall(d):
    """0 at the bay's open front, 1 at the back wall, d in metres."""
    return atlas.smoothstep(0.1, BAY_DEPTH - 0.6, d)


# ============================================================ painting
def paint_boards(c, x0, x1, y0, y1, mid, seed, battens):
    """Vertical boards over a rect, 0.2 m wide from x = 0 so every band and
    region shares one rhythm. With *battens* a batten covers each joint;
    without, the joint is a dark line (the inside of the same wall)."""
    sy, sx, Y, X = c.field(x0, x1, y0, y1)
    xm = X % BATTEN_PITCH
    b = np.floor(X / BATTEN_PITCH).astype(np.int64) % int(ATLAS / BATTEN_PITCH)
    tone = 1.0 + 0.06 * (atlas.hash_unit(seed, b) - 0.5)
    c.mid[sy, sx] = mid
    if battens:
        on = xm < BATTEN_W
        d = np.minimum(xm, BATTEN_W - xm)
        height = np.where(on, BATTEN_H * np.clip(d / 0.9, 0.0, 1.0), 0.0)
        # the board faces beside a batten sit in its lee whatever the sun does
        lee = (xm >= BATTEN_W) & (xm < BATTEN_W + 1.0) | (xm > BATTEN_PITCH - 1.0)
        shade = np.where(on, 1.0 + 0.04 * (atlas.hash_unit(seed + 1, b) - 0.5), tone)
        c.shade[sy, sx] = np.where(lee, shade * 0.90, shade)
        c.ao[sy, sx] = np.where(lee, 0.82, 1.0)
        c.height[sy, sx] = height
    else:
        joint = xm < 1.0
        c.shade[sy, sx] = np.where(joint, tone * 0.72, tone)
        c.ao[sy, sx] = np.where(joint, 0.80, 1.0)
        c.height[sy, sx] = np.where(joint, -0.004, 0.0)


def paint_footing(c, x0, x1, y_ground, top):
    """The concrete footing strip, with the bleed rows under the ground."""
    c.paint(x0, x1, y_ground - 2, top, ID_FOOT, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(x0, x1, y_ground - 2, top)
    z = (Y - y_ground) / PPM
    c.shade[sy, sx] *= 0.86 + 0.14 * np.clip(z / 0.15, 0.0, 1.0)
    # the boards stop a little above it: a dark drip line, shaded always
    c.mul(x0, x1, top - 1.0, top, 0.80, ao=0.80)


def paint_s1(c):
    y0 = S1_Y0
    ft = y0 + m(Z_FOOT)
    paint_footing(c, 0, ATLAS, y0, ft)
    paint_boards(c, 0, ATLAS, ft, 272, ID_WALL, seed=11, battens=True)
    # board ends over the footing: end grain, a little darker
    c.mul(0, ATLAS, ft, ft + 1.0, 0.86)


def region_x(rect, X):
    """Plan x of samples X in the ROOF or CEIL region."""
    return (X - rect[0]) / ROOF_PPM - ROOF_LEN / 2.0


def rail_bracket(x):
    """The snow guard's brackets, every metre over the rafters."""
    xm = np.mod(x, 1.0)
    return (xm >= 0.009) & (xm < 0.040)


def paint_roof(c):
    """Profiled steel at ROOF_PPM both ways: ribs every 0.2 m down the slope,
    the snow guard SNOW_S up from the low (rear) edge, over the rear wall's
    line, and the folded flashing along the high (front) edge. The guard is
    two round tubes on brackets every metre, as rintamamiestalo_porch paints
    its own. Every height is scaled by ROOF_PPM / PPM, so the slopes the
    normal map derives at PPM stay physical."""
    x0, y0, w, h = ROOF
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_ROOF, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2)
    k = ROOF_PPM / PPM
    xm = np.mod(region_x(ROOF, X), 0.20)
    s = (Y - y0) / ROOF_PPM                               # metres up the slope
    # trapezoid rib: 19 mm slopes either side of a 31 mm crown
    up = np.clip(xm / 0.01875, 0.0, 1.0)
    down = np.clip((0.06875 - xm) / 0.01875, 0.0, 1.0)
    height = np.where(xm < 0.06875, RIB_H * k * np.minimum(up, down), 0.0)
    foot = (xm >= 0.06875) & (xm < 0.084375)
    shade = np.where(foot, 0.92, 1.0)                           # foot of a rib
    ao = np.where(foot, 0.86, 1.0)
    shade = np.where(s < 0.06, shade * 0.85, shade)             # low edge's drip
    shade = np.where(s > ROOF_SLOPE_LEN - 0.10, shade * 0.96, shade)   # edge flashing
    g = SNOW_S
    rail = np.zeros(s.shape, bool)
    for t0, t1 in GUARD_TUBES:
        inside = (s >= g + t0) & (s < g + t1)
        tube = SNOW_TUBE_H * k * np.sqrt(np.clip(
            1.0 - (2.0 * (s - g - t0) / (t1 - t0) - 1.0) ** 2, 0, 1))
        height = np.where(inside, tube, height)
        shade = np.where(inside, 1.0, shade)
        rail |= inside
    lo, hi = g - 0.075, g + GUARD_TUBES[-1][1]
    shade = np.where((s >= lo) & (s < g - 0.025), shade * 0.80, shade)   # under the tubes
    gap = (s >= g + GUARD_TUBES[0][1]) & (s < g + GUARD_TUBES[1][0])
    shade = np.where(gap, shade * 0.85, shade)                           # between them
    ao = np.where((s >= lo) & (s < hi), np.minimum(ao, 0.85), ao)
    bracket = rail_bracket(region_x(ROOF, X)) & (s >= lo) & (s < hi)
    height = np.where(bracket, SNOW_BRACKET_H * k, height)
    shade = np.where(bracket, 0.75, shade)
    rail |= bracket
    c.mid[sy, sx] = np.where(rail, ID_GUTTER, ID_ROOF)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao


def paint_fascia(c):
    """The slab's front and rake edges: a white board under the sheet's
    folded flashing, which takes the roof's colour. The rear edge, where the
    water leaves the roof, is paint_rear_fascia()'s."""
    y0 = FASC_Y0
    top = y0 + FASC_H
    c.paint(0, ATLAS, y0 - 2, top + 2, ID_TRIM, 1.0, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, top - 4.0, CASING_H, 1.0, axes="y")
    c.mul(0, ATLAS, y0 - 2, y0 + 1, 0.86)                       # board's lower edge
    c.paint(0, ATLAS, top - 4.0, top + 2, ID_ROOF, 1.0, 1.0, height=0.012)
    c.mul(0, ATLAS, top - 5.0, top - 4.0, 0.78, ao=0.80)        # under the flashing


def paint_rear_fascia(c):
    """The rear (low) edge: the white fascia board with a half-round steel
    gutter hung across its top, under the sheet's drip edge, as in
    rintamamiestalo_porch. The band's top row is the roof's edge, where the
    water leaves it; the two rows over it continue the sheet's drip edge."""
    y0 = FASC_R_Y0
    top = FASC_R_TOP
    c.paint(0, ATLAS, y0 - 2, top, ID_TRIM, 1.0, 1.0, height=0.0)
    c.paint(0, ATLAS, top, top + 2, ID_ROOF, 0.80, height=0.0)
    c.bevel(0, ATLAS, y0, top - 1.0, CASING_H, 1.0, axes="y")
    c.mul(0, ATLAS, y0 - 2, y0 + 1, 0.86)                       # board's lower edge
    # half-round gutter: belly at the bottom, rolled lip at the top. Its roll
    # is height; only the belly's underside is darker.
    gh = GUTTER_PX
    g0 = top - 1 - gh
    c.paint(0, ATLAS, g0, top - 1, ID_GUTTER, 1.0, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top - 1)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_GUTTER, 0.80)
    c.paint(0, ATLAS, top - 1, top, ID_ROOF, 0.80, height=0.0)  # the sheet's drip edge
    sy, sx = c.sl(0, ATLAS, g0 - 3, top)
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.9)
    for k, f in enumerate((0.92, 0.86, 0.80)):            # occluded under the gutter
        c.mul(0, ATLAS, g0 - 3 + k, g0 - 2 + k, f)
    # hangers every 1.0 m, a spacing that divides the atlas width
    sy, sx, _, X = c.field(0, ATLAS, g0 + 2, top - 1)
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.80, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_ceiling(c):
    """The roof's underside, its own region at ROOF_PPM both ways: U plan x,
    V plan depth from the slab's front edge. Bare sheet with its ribs,
    rafters every metre across it (U), purlins under the sheet every 1.1 m
    (V). Light under the front overhang, darkening into the bays, light again
    under the rear overhang, which is outside the back wall. Heights are
    scaled by ROOF_PPM / PPM, as on the roof."""
    x0, y0, w, h = CEIL
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_SHEET, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2)
    kh = ROOF_PPM / PPM
    y = Y_FRONT + (Y - y0) / CEIL_RPM                # plan y of each sample
    x = region_x(CEIL, X)                            # plan x
    xm = np.mod(x, 0.20)
    height = np.where(xm < 0.06875, -0.6 * RIB_H * kh * np.minimum(
        np.clip(xm / 0.01875, 0, 1), np.clip((0.06875 - xm) / 0.01875, 0, 1)), 0.0)
    # The ribs, purlins and rafters are kept low in tone: the ceiling slopes
    # down to the back, so the front elevation sees it face-on through the
    # opening, and at full contrast the grid they make read as glazing bars.
    shade = np.where(xm < 0.06875, 0.97, 1.0)
    mid = np.full(Y.shape, ID_SHEET, np.uint8)
    # purlins, across the rafters just under the sheet
    purl = np.zeros(Y.shape, bool)
    for yp in (-3.25, -2.15, -1.05, 0.05, 1.15, 2.25, 3.10):
        purl |= np.abs(y - yp) < 0.05
    mid = np.where(purl, ID_INNER, mid)
    height = np.where(purl, 0.5 * RAFTER_H * kh, height)
    shade = np.where(purl, 0.92, shade)
    # rafters every metre, a 50 mm face
    rm = np.mod(x, 1.0)
    raf = rm < 0.05
    mid = np.where(raf, ID_INNER, mid)
    height = np.where(raf, RAFTER_H * kh * np.clip(np.minimum(rm, 0.05 - rm) / 0.0125, 0, 1),
                      height)
    shade = np.where(raf, 0.92, shade)
    beside = (rm >= 0.05) & (rm < 0.0656)
    shade = np.where(beside, shade * 0.92, shade)                    # beside a rafter
    ao = np.where(beside | (rm > 1.0 - 0.0156), 0.80, 1.0)
    # occlusion: depth into the bay from the front wall line. The ceiling
    # faces the floor, so it darkens sooner and further than the walls.
    d = y + HY
    k = atlas.smoothstep(-0.3, 3.0, d)
    back = np.clip((y - (HY - 0.12)) / 0.10, 0.0, 1.0)            # rear overhang
    k = k * (1.0 - back)
    fs = 1.0 - (1.0 - CEIL_SHADE) * k
    fa = 1.0 - (1.0 - CEIL_AO) * k
    soff = (y < -HY) | (y > HY)
    fs = np.where(soff, 0.92, fs)                                  # overhangs
    c.mid[sy, sx] = mid
    c.height[sy, sx] = height
    c.shade[sy, sx] = shade * fs
    c.ao[sy, sx] = ao * fa


def paint_inner_wall(c, x0, x1, y_ground, y_top, fall):
    """Bare boards on the inside of a wall, two girts across them, standing on
    the footing; *fall(Y, X)* is the occlusion, 0 open .. 1 deepest."""
    ft = y_ground + m(Z_FOOT)
    paint_footing(c, x0, x1, y_ground, ft)
    paint_boards(c, x0, x1, ft, y_top, ID_INNER, seed=23, battens=False)
    for zg in (1.05, 2.15):                       # girts, 0.1 m faces
        g0, g1 = y_ground + m(zg), y_ground + m(zg + 0.10)
        c.paint(x0, x1, g0, g1, ID_INNER, 1.02, 1.0)
        c.bevel(x0, x1, g0, g1, GIRT_H, 1.0, axes="y")
        c.mul(x0, x1, g0 - 1.0, g0, 0.70, ao=0.6)   # under the girt
        c.mul(x0, x1, g1, g1 + 1.0, 0.90)
    sy, sx, Y, X = c.field(x0, x1, y_ground - 2, y_top)
    k = fall(Y, X)
    z = (Y - y_ground) / PPM
    # where the wall meets the ground, and the ceiling over the back
    corner = 0.10 * np.exp(-np.clip(z, 0, None) / 0.25)
    c.shade[sy, sx] *= (1.0 - (1.0 - BACK_SHADE) * k) * (1.0 - corner)
    c.ao[sy, sx] *= (1.0 - (1.0 - BACK_AO) * k) * (1.0 - 1.5 * corner)


def paint_int(c):
    """The bays' back wall: evenly deep, so evenly occluded."""
    paint_inner_wall(c, 0, ATLAS, INT_Y0, INT_Y0 + m(INT_TOP) + 2,
                     lambda Y, X: np.ones(Y.shape, np.float32))


def paint_side(c):
    """The bays' side walls: occlusion grows with depth from the front, and
    the first POST_STRIP is the white post's side the wall ends in."""
    x0, y0, w, h = SIDE
    paint_inner_wall(c, x0 - 2, x0 + w + 2, y0, y0 + h + 2,
                     lambda Y, X: depth_fall((X - x0) / PPM))
    ps = x0 + m(POST_STRIP)
    c.paint(x0 - 2, ps, y0 + m(Z_FOOT), y0 + h + 2, ID_TRIM, 1.0, 1.0, height=0.0)
    c.bevel(x0 - 2, ps, y0 + m(Z_FOOT), y0 + h + 2, CASING_H, 1.0, axes="x")
    c.mul(ps, ps + 1.0, y0 + m(Z_FOOT), y0 + h + 2, 0.80, ao=0.75)


def paint_post(c):
    """A white post's face, or a wall's end: the footing pad, then the
    board, its arrises rounded."""
    x0, y0, w, h = POST
    paint_footing(c, x0 - 2, x0 + w + 2, y0, y0 + m(Z_FOOT))
    c.paint(x0 - 2, x0 + w + 2, y0 + m(Z_FOOT), y0 + h + 2, ID_TRIM, 1.0, 1.0, height=0.0)
    c.bevel(x0, x0 + w, y0 + m(Z_FOOT), y0 + h + 2, CASING_H, 1.0, axes="x")


def paint_corner(c):
    x0, y0, w, h = CORNER
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_TRIM, 1.0, 1.0, height=0.0)
    c.bevel(x0, x0 + w, y0 - 2, y0 + h + 2, CASING_H, 1.0, axes="x")


def paint_leaf(c, x0, x1, y0, y1, hinge_left, seed):
    """One ledged, braced and framed board leaf: planks with V-grooves, a
    white frame and a white diagonal brace in each panel rising away from the
    hinges, black strap hinges, kicked dirt at the foot."""
    c.paint(x0, x1, y0, y1, ID_DOOR, 1.0, 1.0, height=0.0)
    for xx in np.arange(x0 + m(0.1), x1 - 0.5, m(0.1)):
        c.mul(xx, xx + 1, y0, y1, 0.80, ao=0.80)
        c.lift(xx, xx + 1, y0, y1, -0.003)
    fw = m(0.10)
    mid_y = y0 + (y1 - y0) * 0.48
    # the brace first, so the frame's rails lie over its ends
    for p0, p1 in ((y0 + fw, mid_y), (mid_y + fw, y1 - fw)):
        a = (x0 + fw * 0.7, p0) if hinge_left else (x1 - fw * 0.7, p0)
        b = (x1 - fw * 0.7, p1) if hinge_left else (x0 + fw * 0.7, p1)
        c.stroke(a, b, fw, ID_TRIM, 1.0, 1.0, clip=(x0, y0, x1 - x0, y1 - y0),
                 height=FRAME_H)
    for rx0, rx1, ry0, ry1 in ((x0, x0 + fw, y0, y1), (x1 - fw, x1, y0, y1),
                               (x0, x1, y0, y0 + fw * 1.2), (x0, x1, y1 - fw, y1),
                               (x0, x1, mid_y, mid_y + fw)):
        c.paint(rx0, rx1, ry0, ry1, ID_TRIM, 1.0, 1.0)
        c.bevel(rx0, rx1, ry0, ry1, FRAME_H, 0.8)
    # strap hinges over the hinge stile
    hx0, hx1 = (x0 - 1, x0 + m(0.45)) if hinge_left else (x1 - m(0.45), x1 + 1)
    for hy in (y0 + m(0.35), y1 - m(0.45)):
        c.paint(hx0, hx1, hy, hy + 2.5, ID_HW, 1.0, 0.9, height=FRAME_H + 0.006)
    c.mul(x0, x1, y0, y0 + 2, 0.80, ao=0.75)                      # foot
    return c


def paint_opening(c, kind):
    x0, y0 = ITEM_ORIGIN[kind]
    w, h, cs, cb, ct = OPENINGS[kind]
    rw, rh = item_size_px(kind)
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0 + m(cb), y0 + m(cb + h)
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, ID_TRIM, 1.0, 1.0, height=0.0)
    c.bevel(x0, x0 + rw, y0 - 3, y0 + rh, CASING_H, 1.0)
    # drip flashing over the head casing, in the roof's steel
    top = y0 + rh
    c.paint(x0 - 2, x0 + rw + 2, top - 2.5, top + 2, ID_HW, 1.0)
    sy, sx, Y, _ = c.field(x0 - 2, x0 + rw + 2, top - 2.5, top + 2)
    c.height[sy, sx] = 0.030 - 0.010 * np.clip((Y - (top - 2.5)) / 2.5, 0.0, 1.0)
    c.mul(x0 - 2, x0 + rw + 2, top - 3.5, top - 2.5, 0.85, ao=0.8)
    c.mul(ox0 - 1, ox1 + 1, oy1, oy1 + 1, 0.84, ao=0.8)          # head shadow
    if kind == "door_pair":
        mx = (ox0 + ox1) / 2.0
        paint_leaf(c, ox0, mx - 0.5, oy0, oy1, True, 3)
        paint_leaf(c, mx + 0.5, ox1, oy0, oy1, False, 4)
        c.paint(mx - 0.5, mx + 0.5, oy0, oy1, ID_BLANK, 0.6, 0.5, height=-0.01)
        # the drop bar and its keeper across the meeting stiles
        c.paint(mx - m(0.35), mx + m(0.35), oy0 + m(1.15), oy0 + m(1.21), ID_HW,
                1.0, 0.9, height=FRAME_H + 0.012)
        c.paint(mx - 1.5, mx + 1.5, oy0 + m(1.05), oy0 + m(1.30), ID_HW, 0.9,
                0.9, height=FRAME_H + 0.008)
    else:
        paint_leaf(c, ox0, ox1, oy0, oy1, True, 5)
        hx = ox1 - m(0.10)
        c.paint(hx - 2, hx, oy0 + m(0.95), oy0 + m(1.12), ID_HW, 1.0, 0.9,
                height=FRAME_H + 0.015)
        c.paint(hx - 3, hx + 0.5, oy0 + m(1.02), oy0 + m(1.06), ID_HW, 1.0, 0.9,
                height=FRAME_H + 0.028)


def paint_patches(c):
    spec = {"header": (ID_TRIM, 0.96, 1.0), "soffit": (ID_SHEET, 0.86, 0.85),
            "reveal": (ID_TRIM, 0.72, 0.6), "blank": (ID_BLANK, 1.0, 0.5)}
    atlas.paint_patches(c, PATCHES, spec)


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    The outer wall band's V is height from the ground, the roof band's is
    slope from the low edge, so splash and the dirtier eave land the same on
    every face. Inside the bays nothing washes the dust off."""
    w = weathering.Weather(c, steel=(ID_ROOF, ID_SHEET, ID_HW, ID_GUTTER))
    w.grime()
    w.fade((ID_WALL, ID_TRIM, ID_DOOR))
    w.wash((ID_WALL,))
    # outer walls: the footing and the boards' splashed foot
    w.plinth(0, ATLAS, S1_Y0, S1_Y0 + m(Z_FOOT), (ID_FOOT,))
    w.splash(0, ATLAS, S1_Y0 + m(Z_FOOT), 272, (ID_WALL,))
    # roof: runs down the slope, dirt toward the low edge, chalk up the slope
    x0, y0, rw, rh = ROOF
    xa, xb = x0 - 2, x0 + rw + 2
    w.roof(xa, xb, y0, rh, ROOF_SLOPE_LEN, (ID_ROOF,))
    w.add("R", xa, xb, y0 - 2, y0 + 0.15 * ROOF_PPM, lambda Y, X, nz: 0.12 * nz("speck"),
          (ID_ROOF,))
    # the snow guard: light dust on it (with grime(), 0.06 + 0.08 blotch, as
    # on the farm's other two), rust at its brackets; debris held on the
    # sheet just above it
    g = y0 + SNOW_S * ROOF_PPM
    lo, hi = g - 0.075 * ROOF_PPM, g + GUARD_TUBES[-1][1] * ROOF_PPM
    w.add("D", xa, xb, lo, hi, lambda Y, X, nz: 0.06 + 0.045 * nz("blotch"),
          (ID_GUTTER,))
    w.add("R", xa, xb, lo, hi, lambda Y, X, nz: 0.15 * rail_bracket(region_x(ROOF, X)),
          (ID_GUTTER,))
    w.add("D", xa, xb, hi, hi + 0.17 * ROOF_PPM, lambda Y, X, nz: 0.22 * nz("blotch")
          * (1.0 - (Y - hi) / (0.17 * ROOF_PPM)), (ID_ROOF,))
    # fascia: runs down the board from the flashing
    w.runs(0, ATLAS, FASC_Y0 - 2, FASC_Y0 + FASC_H - 4, (ID_TRIM,), 0.18, fall=6.0,
           lo=0.4, hi=1.6)
    # rear fascia: runs down the board from the gutter; the gutter's dirty
    # belly and light runs down its face from the lip, the same treatment as
    # the farm's other two gutters
    top = FASC_R_TOP
    g0 = top - 1 - GUTTER_PX
    w.add("D", 0, ATLAS, FASC_R_Y0 - 2, g0, 0.06, (ID_TRIM,))
    w.runs(0, ATLAS, FASC_R_Y0 - 2, g0, (ID_TRIM,), 0.22, fall=6.0, lo=0.4, hi=1.6)
    w.add("D", 0, ATLAS, g0, g0 + 4, lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"),
          (ID_GUTTER,))
    w.runs(0, ATLAS, g0, top - 1, (ID_GUTTER,), 0.08, fall=4.0, lo=0.4, hi=1.6)
    # inside the bays: dust settled on everything, thicker toward the floor
    for x0, x1, yg, yt in ((0, ATLAS, INT_Y0, INT_Y0 + m(INT_TOP) + 2),
                           (SIDE[0] - 2, SIDE[0] + SIDE[2] + 2, SIDE[1],
                            SIDE[1] + SIDE[3] + 2)):
        w.add("D", x0, x1, yg - 2, yt, lambda Y, X, nz, yg=yg: 0.08 * nz("blotch")
              + 0.28 * np.exp(-np.clip((Y - yg) / PPM, 0, None) / 0.35),
              (ID_INNER, ID_FOOT, ID_TRIM))
    w.add("D", CEIL[0] - 2, CEIL[0] + CEIL[2] + 2, CEIL[1] - 2, CEIL[1] + CEIL[3] + 2,
          lambda Y, X, nz: 0.10 * nz("blotch"), (ID_SHEET, ID_INNER))
    # posts, corner boards and door feet: splashed like the walls
    for x0, y0, wd, _h in (POST, CORNER):
        w.splash(x0 - 2, x0 + wd + 2, y0 + m(Z_FOOT), y0 + m(1.0), (ID_TRIM,))
    w.plinth(POST[0] - 2, POST[0] + POST[2] + 2, POST[1], POST[1] + m(Z_FOOT), (ID_FOOT,))
    for kind, (wd, h, cs, cb, ct) in OPENINGS.items():
        x0, yb = ITEM_ORIGIN[kind]
        ox0, ox1 = x0 + m(cs), x0 + m(cs + wd)
        oy0, oy1 = yb + m(cb), yb + m(cb + h)
        hx = (ox0 + ox1) / 2.0 if kind == "door_pair" else ox1 - m(0.10)
        w.door(ox0, ox1, oy0, oy1, (ID_DOOR, ID_TRIM), handle=(hx, oy0 + m(1.10)))
        w.splash(x0 - 2, x0 + item_size_px(kind)[0] + 2, yb, yb + m(0.8), (ID_TRIM,))
    # the floor slabs in the doors' reveals: trodden-in dirt
    for f in FLOORS.values():
        DF.weather(w, f, ID_FLOOR)
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_s1(c)
    paint_roof(c)
    paint_fascia(c)
    paint_rear_fascia(c)
    paint_ceiling(c)
    paint_int(c)
    paint_side(c)
    for kind in OPENINGS:
        paint_opening(c, kind)
    paint_post(c)
    paint_corner(c)
    for f in FLOORS.values():
        DF.paint(c, f, ID_FLOOR)
    paint_patches(c)

    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    wood = np.isin(c.mid, (ID_WALL, ID_TRIM, ID_DOOR, ID_INNER))
    grain = atlas.noise(c, 5, 0.35, 60.0)            # streaks along vertical boards
    c.shade[wood] *= 1.0 + 0.03 * grain[wood]
    c.height[wood] += 0.0003 * grain[wood]
    roof = c.mid == ID_ROOF
    streak = atlas.noise(c, 7, 0.8, 40.0)            # rain runs down the slope
    c.shade[roof] *= 1.0 + 0.035 * streak[roof]
    concrete = c.mid == ID_FOOT
    pores = atlas.noise(c, 9, 0.8)
    c.shade[concrete] *= 1.0 + 0.03 * pores[concrete]
    c.height[concrete] += 0.0006 * pores[concrete]
    DF.grain(c, ID_FLOOR, pores)
    weather(c)
    c.check_bands(BAND_IDS)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    t[ID_WALL] = pal["wall"]
    t[ID_DOOR] = pal["door"]
    t[ID_TRIM] = pal["trim"]
    t[ID_ROOF] = pal["roof"]
    return t


def export(out_dir, ss=atlas.SS):
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.012)
    c.weather.dust(cav, (ID_WALL, ID_INNER))
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
        os.makedirs(os.path.join(here, "export"), exist_ok=True)
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
