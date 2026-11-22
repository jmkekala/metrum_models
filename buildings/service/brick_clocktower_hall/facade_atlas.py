# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
brick_clocktower_hall.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
the plan, the walls and what stands on each, every height, the band rows and
the region rectangles -- so a change here cannot leave the UVs pointing at the
wrong artwork.

The atlas is 2048 square at 64 texels a metre (the documented hero
exception: the building is 49 m long). Four bands run the full width and
tile in U, every wall sampling them in true metres:

    rows    2 ..  752   WALL    z 0 .. 11.72 m: the stone plinth, its cap,
                                stretcher-bond brick (scripts/brickwork.py,
                                the catalog module), the string course, the
                                dentilled frieze, the cornice and the shaded
                                fascia under the soffit
    rows  760 ..  908   ROOF    dark painted standing-seam steel, V up the
                                slope at 32 rows a metre
    rows  914 ..  930   FASCIA  the white fascia board with the dark
                                half-round gutter across its top (PIPE_STRIP)
    rows  936 ..  965   SOFFIT  painted soffit boards, V out from the wall

Above them, the unique regions: every opening kind as its own item (the
windows in three or four room variants each, the arched entrance, the
balcony group, the service door, the pilaster), the quoin strips, the tower,
the chimney, the dome facet, the clock attic, the pediment, the balustrades,
the roof deck in plan (16 texels a metre) and the walls' elevations at 16
texels a metre, which the two far tiers map in place of the band and its
items. The elevations are composed after the maps are resolved from the
band, the items, the quoins and the downpipes at their places on each wall,
and box-filtered down, so the far tiers show what the near ones do.

The brick is the catalog's module: a 0.25 m stretcher on a 0.078125 m
course. Every height the walls share with the coursing falls on a course
line, and every opening's and item's side on a whole or half stretcher of
the wall's bond (build.py's check_layout()).

Rasterising is scripts/atlas.py's (numpy, scipy; Pillow to save);
weathering is scripts/weathering.py's at the catalog's moderate level, and
glass is scripts/glazing.py's room behind the pane.
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import brickwork  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "brick_clocktower_hall"
VARIANTS = ("red_brick",)
DEFAULT_VARIANT = "red_brick"
ATLAS = 2048
PPM = 64.0
EPPM = 16.0             # the walls' elevations, for LOD2 and LOD3
DPPM = 16.0             # the roof deck, in plan
RPM = 32.0              # the roof band, rows per metre of slope
PAD = 2

# --------------------------------------------------------------- brickwork
COURSE = brickwork.COURSE           # 0.078125 m, 5 px
BRICK_L = brickwork.BRICK_L         # 0.25 m, 16 px
HALF = BRICK_L / 2.0                # a half stretcher, 0.125 m
TONE_COURSES = 160


def course(n):
    """Course line *n* above the ground, metres."""
    return n * COURSE


def m(v):
    """Metres -> pixels at 64 px/m."""
    return v * PPM


# --------------------------------------------------------- vertical layout
Z_FLOOR = course(2)             # 0.156: the ground floor, one step up
Z_PLINTH = course(12)           # 0.9375: top of the stone plinth
Z_PLINTH_CAP = course(15)       # 1.171875: top of its moulded cap
Z_GF_SILL = course(16)          # 1.25
Z_DOOR_TRANSOM = course(32)     # 2.50: the doors' leaves end here
Z_DOOR_HEAD = course(33)        # 2.578: the door cuts' head, the arch's springing
Z_GF_HEAD = course(47)          # 3.672
Z_STRING = course(65)           # 5.078: string course foot
Z_UPPER = course(71)            # 5.547: string course top, the upper floor
Z_BAL_SILL = course(72)         # 5.625: the balcony door's threshold
Z_UF_SILL = course(81)          # 6.328
Z_TALL_SILL = course(84)        # 6.5625: the entrance bay's tall windows
Z_BAL_TRANSOM = course(101)     # 7.891: the balcony door's leaves end here
Z_UF_HEAD = course(115)         # 8.984
Z_TALL_HEAD = course(117)       # 9.141: balcony door and tall windows' head
Z_FRIEZE = course(127)          # 9.922: frieze foot
Z_CORNICE = course(134)         # 10.469: cornice foot
Z_CORNICE_TOP = course(143)     # 11.172
Z_EAVE = course(146)            # 11.406: the soffit meets the wall
Z_TOP = course(148)             # 11.5625: the walls run into the roof to here
Z_BAND = course(150)            # 11.71875: the band's painted top
FASC_M = 0.25                   # the fascia's depth
Z_FT = Z_EAVE + FASC_M          # 11.656: the roof's top at the fascia
EAVE_OUT = 0.45                 # the eave's projection, wall face to fascia
ROOF_RUN, ROOF_RISE = 3.5, 3.0  # the slope, fascia to deck
TAN = ROOF_RISE / ROOF_RUN
Z_DECK = Z_FT + ROOF_RISE       # 14.656: the one flat deck
SLOPE_LEN = math.hypot(ROOF_RUN, ROOF_RISE)

# ---------------------------------------------------------------- plan
# The massing as overlapping rectangles (x0, x1, y0, y1), front toward -Y.
# Every edge on a half stretcher.
RECTS = [
    (-17.25, 17.25, -8.0, 6.0),         # main front range
    (-24.375, -16.375, -9.625, 6.0),    # left end pavilion
    (16.375, 24.375, -9.625, 6.0),      # right end pavilion
    (-5.5, 5.5, -10.25, 2.0),           # centre entrance bay
    (-24.375, -13.375, 2.0, 16.5),      # left rear wing
    (13.375, 24.375, 2.0, 16.5),        # right rear wing
    (-6.0, 6.0, 2.0, 11.0),             # centre rear link
]

# The outline of their union, counter-clockwise seen from above, so each
# wall's outward face is on the right of p0 -> p1. build.py checks it is the
# union's outline.
WALLS = [
    dict(name="pav_front_l", p0=(-24.375, -9.625), p1=(-16.375, -9.625)),
    dict(name="pav_ret_l", p0=(-16.375, -9.625), p1=(-16.375, -8.0)),
    dict(name="front_l", p0=(-16.375, -8.0), p1=(-5.5, -8.0)),
    dict(name="ent_ret_l", p0=(-5.5, -8.0), p1=(-5.5, -10.25)),
    dict(name="entrance", p0=(-5.5, -10.25), p1=(5.5, -10.25)),
    dict(name="ent_ret_r", p0=(5.5, -10.25), p1=(5.5, -8.0)),
    dict(name="front_r", p0=(5.5, -8.0), p1=(16.375, -8.0)),
    dict(name="pav_ret_r", p0=(16.375, -8.0), p1=(16.375, -9.625)),
    dict(name="pav_front_r", p0=(16.375, -9.625), p1=(24.375, -9.625)),
    dict(name="side_r", p0=(24.375, -9.625), p1=(24.375, 16.5)),
    dict(name="wing_end_r", p0=(24.375, 16.5), p1=(13.375, 16.5)),
    dict(name="wing_in_r", p0=(13.375, 16.5), p1=(13.375, 6.0)),
    dict(name="rear_r", p0=(13.375, 6.0), p1=(6.0, 6.0)),
    dict(name="link_side_r", p0=(6.0, 6.0), p1=(6.0, 11.0)),
    dict(name="link_end", p0=(6.0, 11.0), p1=(-6.0, 11.0)),
    dict(name="link_side_l", p0=(-6.0, 11.0), p1=(-6.0, 6.0)),
    dict(name="rear_l", p0=(-6.0, 6.0), p1=(-13.375, 6.0)),
    dict(name="wing_in_l", p0=(-13.375, 6.0), p1=(-13.375, 16.5)),
    dict(name="wing_end_l", p0=(-13.375, 16.5), p1=(-24.375, 16.5)),
    dict(name="side_l", p0=(-24.375, 16.5), p1=(-24.375, -9.625)),
]
WALL = {w["name"]: w for w in WALLS}
# The walls a street camera can see; the U-court's seven are the rest.
COURT = ("wing_in_r", "rear_r", "link_side_r", "link_end", "link_side_l", "rear_l",
         "wing_in_l")
# The street front, whose openings LOD2 may keep recessed.
FRONT = ("pav_front_l", "front_l", "entrance", "front_r", "pav_front_r")


def _dir(w):
    (x0, y0), (x1, y1) = w["p0"], w["p1"]
    d = math.hypot(x1 - x0, y1 - y0)
    return (x1 - x0) / d, (y1 - y0) / d, d


for _i, _w in enumerate(WALLS):
    _tx, _ty, _w["L"] = _dir(_w)
for _i, _w in enumerate(WALLS):
    _a = WALLS[_i - 1]
    ax, ay, _ = _dir(_a)
    bx, by, _ = _dir(_w)
    # a left turn, walking counter-clockwise, is a convex corner
    _w["convex0"] = ax * by - ay * bx > 0.0
for _i, _w in enumerate(WALLS):
    _w["convex1"] = WALLS[(_i + 1) % len(WALLS)]["convex0"]

# ------------------------------------------------------- openings (items)
# Every opening kind is an item: a rectangle on its wall, its own region in
# the atlas, fully covered by its artwork (casing, head, sill, the opening),
# so no brick is painted inside one. w is its width; z0 .. z1 its heights;
# openings, (s0, s1, z0, z1) from its left edge, are recessed REVEAL on the
# near tiers. The casing is a quarter metre, so an item's sides and its
# opening's both fall on half stretchers.
CASING = 0.25
REVEAL = 0.28
QUOIN_DEPTH = 0.5               # the quoin block wraps this far along each face
QUOIN_PROUD = course(1)         # and stands this far out of both
QUOIN_TOP = Z_FRIEZE            # the entablature runs on round the corner above
ITEMS = {
    "gf": dict(w=1.875, z0=Z_PLINTH_CAP, z1=course(53),
               openings=[(0.25, 1.625, Z_GF_SILL, Z_GF_HEAD)]),
    "uf": dict(w=1.875, z0=course(79), z1=course(121),
               openings=[(0.25, 1.625, Z_UF_SILL, Z_UF_HEAD)]),
    "gf125": dict(w=1.75, z0=Z_PLINTH_CAP, z1=course(53),
                  openings=[(0.25, 1.5, Z_GF_SILL, Z_GF_HEAD)]),
    "uf125": dict(w=1.75, z0=course(79), z1=course(121),
                  openings=[(0.25, 1.5, Z_UF_SILL, Z_UF_HEAD)]),
    "door": dict(w=2.5, z0=0.0, z1=course(53),
                 openings=[(0.25, 2.25, 0.0, Z_DOOR_HEAD)]),
    "service": dict(w=1.875, z0=0.0, z1=course(39),
                    openings=[(0.25, 1.625, 0.0, Z_DOOR_HEAD)]),
    "group": dict(w=5.5, z0=Z_UPPER, z1=course(123),
                  openings=[(0.25, 1.5, Z_TALL_SILL, Z_TALL_HEAD),
                            (2.125, 3.375, Z_BAL_SILL, Z_TALL_HEAD),
                            (4.0, 5.25, Z_TALL_SILL, Z_TALL_HEAD)]),
    "pilaster": dict(w=0.25, z0=Z_UPPER, z1=Z_FRIEZE, openings=[]),
}
# Room variants per kind: a window's rooms are told apart by where its panes
# lie in the atlas (scripts/glazing.py seeds each pane by its box), so a kind
# painted three or four times gives three or four rooms, and a facade cycles
# through them.
NVAR = {"gf": 4, "uf": 4, "gf125": 2, "uf125": 3, "door": 1, "service": 1,
        "group": 1, "pilaster": 1}
WINDOW_KINDS = ("gf", "uf", "gf125", "uf125")
# The door leaves' widths and heights, for the facts sidecar.
DOOR_LEAF = {"door": (2.0, Z_DOOR_TRANSOM - Z_FLOOR),
             "service": (1.375, Z_DOOR_TRANSOM - Z_FLOOR),
             "balcony": (1.25, Z_BAL_TRANSOM - Z_BAL_SILL)}


def _row(kind, centres, first=0):
    n = NVAR[kind]
    return [(kind, s, (first + k) % n) for k, s in enumerate(centres)]


def _mirror(items, length):
    """The same placements on the mirrored wall, its s running the other way."""
    return [(k, length - s, v) for k, s, v in items]


_SIDE = [2.125 + 3.125 * k for k in range(8)]
_SIDE_P = [3.6875 + 3.125 * k for k in range(7)]
PLACE = {
    "pav_front_l": (_row("gf", (2.0625, 5.9375), 0) + _row("uf", (2.0625, 5.9375), 2)
                    + _row("pilaster", (4.0,))),
    "front_l": (_row("gf", (1.8125, 5.4375, 9.0625), 1) + _row("uf", (1.8125, 5.4375, 9.0625), 3)
                + _row("pilaster", (3.625, 7.25))),
    "entrance": ([("door", 5.5, 0), ("group", 5.5, 0)] + _row("gf", (2.1875, 8.8125), 2)
                 + _row("uf125", (1.625, 9.375), 0)),
    "side_r": (_row("gf", _SIDE, 0) + _row("uf", _SIDE, 2) + _row("pilaster", _SIDE_P)),
    "wing_end_r": ([("service", 5.5, 0)] + _row("gf", (1.875, 9.125), 3)
                   + _row("uf", (1.875, 5.5, 9.125), 1) + _row("pilaster", (3.6875, 7.3125))),
    "wing_in_r": (_row("gf", (1.8125, 5.4375, 9.0625), 2)
                  + _row("uf", (1.8125, 5.4375, 9.0625), 0)
                  + _row("pilaster", (3.625, 7.25))),
    "rear_r": (_row("gf", (1.8125, 5.4375), 3) + _row("uf", (1.8125, 5.4375), 1)
               + _row("pilaster", (3.625,))),
    "link_side_r": _row("gf125", (1.125, 3.125), 0) + _row("uf125", (1.125, 3.125), 1),
    "link_end": (_row("gf", (1.6875, 4.5625, 7.4375, 10.3125), 1)
                 + _row("uf", (1.6875, 4.5625, 7.4375, 10.3125), 3)
                 + _row("pilaster", (3.125, 6.0, 8.875))),
}
PLACE["pav_front_r"] = _row("gf", (2.0625, 5.9375), 1) + _row("uf", (2.0625, 5.9375), 3) \
    + _row("pilaster", (4.0,))
PLACE["front_r"] = (_row("gf", (1.8125, 5.4375, 9.0625), 2)
                    + _row("uf", (1.8125, 5.4375, 9.0625), 0) + _row("pilaster", (3.625, 7.25)))
PLACE["side_l"] = (_row("gf", _SIDE, 1) + _row("uf", _SIDE, 3) + _row("pilaster", _SIDE_P))
PLACE["wing_end_l"] = (_row("gf", (1.875, 5.5, 9.125), 2) + _row("uf", (1.875, 5.5, 9.125), 0)
                       + _row("pilaster", (3.6875, 7.3125)))
PLACE["wing_in_l"] = _mirror(PLACE["wing_in_r"], 10.5)
PLACE["rear_l"] = _mirror(PLACE["rear_r"], 7.375)
PLACE["link_side_l"] = _mirror(PLACE["link_side_r"], 5.0)
for _w in WALLS:
    _w["items"] = PLACE.get(_w["name"], [])


def item_rect(kind, s):
    """(left, right, bottom, top) of the item centred *s* along its wall."""
    it = ITEMS[kind]
    return s - it["w"] / 2.0, s + it["w"] / 2.0, it["z0"], it["z1"]


# Downpipes, (wall, s): on the four short returns at the front, beside the
# valleys there; two on each side; one on each rear wing's end; two in the
# U-court beside the link.
PIPES = [("pav_ret_l", 1.25), ("ent_ret_l", 0.375), ("ent_ret_r", 1.875),
         ("pav_ret_r", 0.375), ("side_r", 6.5), ("side_r", 19.0),
         ("wing_end_r", 3.125), ("rear_r", 7.0), ("rear_l", 0.375),
         ("wing_end_l", 7.875), ("side_l", 7.125), ("side_l", 19.625)]
PIPE_W = 0.10
# The roof safety kit's wall ladder: in the U-court, on the left wing's inner
# face, in front of the pilaster between its first two bays.
LADDER = ("wing_in_l", 3.25)


def _u_offsets():
    """Where each wall samples the brick band in U, so that every item's
    sides fall on a half stretcher of the wall's bond, and at every concave
    corner the bond turns: the course ending on a whole brick on one face
    ends on a half on the other. Convex corners are under the quoins."""
    u, out = 0.0, {}
    prev = None
    for w in WALLS:
        if prev is None:
            u0 = 0.0
        elif w["convex0"]:
            u0 = math.floor(out[prev["name"]] + prev["L"]) + 3.0
        else:
            u0 = out[prev["name"]] + prev["L"] + HALF
        need = 0.0
        if w["items"]:
            k, s, _v = w["items"][0]
            need = (-item_rect(k, s)[0]) % HALF
        if w["convex0"]:
            u0 = math.floor(u0 / HALF) * HALF + need
        out[w["name"]] = u0 % (ATLAS / PPM)
        prev = w
    return out


U_OFF = _u_offsets()
for _w in WALLS:
    _w["u"] = U_OFF[_w["name"]]

# ------------------------------------------------------------ the tower etc.
TOWER_W, TOWER_YC = 1.5, -2.3           # half-width, centre in y
TOWER_FOOT = 14.5                       # inside the roof, under the deck
TOWER_TOP = 20.2
TOWER_PLAT = (17.3, 18.0)
DOME_Z = (20.2, 20.55, 20.9, 21.3, 21.6)
DOME_R = (1.45, 1.36, 1.12, 0.80, 0.45)
TOWER_BALL = (21.6, 22.1)
TOWER_POLE = 24.6
CHIM_TOP = course(209)                  # 16.328
CHIM_FOOT = 14.35
CHIMNEYS = [(-8.125, -6.875, -1.625, -0.375), (6.875, 8.125, -1.625, -0.375),
            (-19.375, -18.125, 6.625, 7.875), (18.125, 19.375, 6.625, 7.875),
            (-19.375, -18.125, 11.625, 12.875), (18.125, 19.375, 11.625, 12.875)]
ATTIC = (-4.0, 4.0, -10.25, -8.375)     # plan of the clock attic
Z_ATTIC = course(187)                   # 14.609: the attic's top
Z_APEX = course(210)                    # 16.406: the pediment's apex
PED_OVER = 0.125                        # the pediment oversails the attic
DIAL_C, DIAL_R = (0.0, 13.1875), 0.9375
BALC_X = 2.4
BALC_Y = -11.4                          # the balcony's front
BALC_SLAB = (course(68), Z_UPPER)       # 5.3125 .. 5.547
# bottom rail's top, dado's top, top rail's top: a course under the tall
# windows' sills, so the parapets run into the wall clear of their recesses
BALC_RAIL = (course(73), course(81), course(83))
BALC_T = 0.2

# --------------------------------------------------------------- the atlas
WALL_Y0 = 2
ROOF_Y0 = 760
ROOF_H = SLOPE_LEN * RPM
FASC_Y0, FASC_H = 914, FASC_M * PPM
GUTTER_PX = 9.0
PIPE_STRIP = (FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 - 2.5,
              FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 + 2.5)
SOF_Y0, SOF_H = 936, EAVE_OUT * PPM
BANDS_TOP = SOF_Y0 + SOF_H + PAD

ELEV_Y = (972, 1163)
ELEV_H = int(round(Z_TOP * EPPM))       # 185 rows: z 0 .. Z_TOP
ELEV_MAX_X = 1568


def _elev_regions():
    out, x, row = {}, 4, 0
    for w in WALLS:
        wpx = int(round(w["L"] * EPPM))
        if x + wpx > ELEV_MAX_X:
            row, x = row + 1, 4
        out[w["name"]] = (x, ELEV_Y[row], wpx, ELEV_H)
        x += wpx + 4
    return out


ELEV = _elev_regions()


def _item_regions():
    out = {}
    places = (("gf", 700, 1354), ("uf", 700, 1550))
    for kind, x, y in places:
        for v in range(NVAR[kind]):
            out[(kind, v)] = (x + 124 * v, y)
    for v in range(NVAR["gf125"]):
        out[("gf125", v)] = (1196 + 116 * v, 1354)
    for v in range(NVAR["uf125"]):
        out[("uf125", v)] = (1196 + 116 * v, 1550)
    out[("door", 0)] = (1548, 1354)
    out[("service", 0)] = (1716, 1354)
    out[("pilaster", 0)] = (1844, 1354)
    out[("group", 0)] = (1548, 1640)
    rects = {}
    for (kind, v), (x, y) in out.items():
        it = ITEMS[kind]
        rects[(kind, v)] = (x, y, m(it["w"]), m(it["z1"] - it["z0"]))
    return rects


ITEM_REGION = _item_regions()
QUOIN = {"a": (1964, 1354, 38, m(QUOIN_TOP)), "b": (2006, 1354, 38, m(QUOIN_TOP))}
TOWER = (1572, 972, m(2 * TOWER_W), m(TOWER_TOP - TOWER_FOOT))
CHIMNEY = (1772, 972, 80, m(CHIM_TOP - CHIM_FOOT))
DOME = (1860, 972, 64, m(1.625))
DECK = (4, 1354, 688, 336)
DECK_O = (-21.5, -7.375)                # the plan point at the deck region's corner
ATTIC_F = (4, 1700, m(8.0), m(Z_ATTIC - Z_TOP))
PEDIMENT = (4, 1906, m(8.0 + 2 * PED_OVER), m(Z_APEX - Z_ATTIC))
BALUS = (548, 1786, m(2 * BALC_X), m(BALC_RAIL[1] - BALC_RAIL[0]))
PLAT_BALUS = (548, 1840, m(3.6), m(0.45))
PATCH_NAMES = ("blank", "reveal", "trim", "trim_shade", "sill_top", "roof", "soot",
               "step", "rim", "gutter", "frame", "cutter", "lid", "rail")
PATCHES = {n: (870 + 20 * i, 1790, 16, 16) for i, n in enumerate(PATCH_NAMES)}

# ----------------------------------------------------------- material ids
ID_BLANK, ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH = 0, 1, 2, 3, 4
ID_TRIM, ID_GLASS, ID_FRAME, ID_DOOR, ID_ROOF = 5, 6, 7, 8, 9
ID_GUTTER, ID_DARK, ID_CLOCK, ID_CHIM, ID_METAL, ID_SOOT = 10, 11, 12, 13, 14, 15
BRICK_IDS = (ID_BRICK, ID_BRICK2, ID_MORTAR)

# sRGB. A late-19th-century civic red brick, deep and a little brown rather
# than orange, with about one brick in six darker; a lime mortar; trim painted
# a weathered off-white; grey granite at the plinth; the roof, its gutter and
# downpipes and the roof safety kit one dark painted steel.
COLOUR = {
    ID_BLANK: (52, 52, 52), ID_BRICK: (134, 74, 60), ID_BRICK2: (104, 55, 46),
    ID_MORTAR: (158, 152, 140), ID_PLINTH: (146, 143, 136), ID_TRIM: (210, 204, 190),
    ID_GLASS: glazing.BASE, ID_FRAME: (178, 172, 160), ID_DOOR: (64, 54, 45),
    ID_ROOF: (54, 58, 66), ID_GUTTER: (58, 62, 68), ID_DARK: (44, 41, 38),
    ID_CLOCK: (230, 226, 214), ID_CHIM: (80, 82, 86), ID_METAL: (150, 128, 92),
    ID_SOOT: (22, 21, 20),
}
# (roughness, metallic). The roof, gutter, pipes and kit are painted steel,
# and the windows and doors painted timber: none of them metallic.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_BRICK: (0.84, 0.0), ID_BRICK2: (0.82, 0.0),
    ID_MORTAR: (0.93, 0.0), ID_PLINTH: (0.78, 0.0), ID_TRIM: (0.64, 0.0),
    ID_GLASS: (glazing.ROUGHNESS, 0.0), ID_FRAME: (0.50, 0.0), ID_DOOR: (0.52, 0.0),
    ID_ROOF: (0.55, 0.0), ID_GUTTER: (0.50, 0.0), ID_DARK: (0.92, 0.0),
    ID_CLOCK: (0.32, 0.0), ID_CHIM: (0.86, 0.0), ID_METAL: (0.36, 0.75),
    ID_SOOT: (0.98, 0.0),
}
# The emission: glass in neutral white (glazing.night_rooms() then makes each
# pane a room), and the clock's dial in its own warm light, which is how the
# validator tells a fixture from glazing. Both share the mask's one control.
EMIT = {ID_GLASS: (255, 255, 255), ID_CLOCK: (255, 208, 146)}
# Linear RGB: the catalog's warm interior lamps.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
BRICK_FACE = brickwork.BRICK_FACE
TRIM_H = 0.035          # string course, casings, quoin stones, pilasters
CORNICE_H = 0.06        # cornices and heads, the deepest painted mouldings
DENTIL_H = 0.03
FRAME_H = 0.025         # window frames proud of the glass
SEAM_H = 0.025          # standing seams
TRIM_SH = 0.88          # trim in its own shade

BAND_IDS = {
    "WALL": ((0, WALL_Y0 + m(Z_BAND) + PAD), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH,
                                              ID_TRIM}),
    "ROOF": ((ROOF_Y0 - PAD, ROOF_Y0 + ROOF_H + PAD), {ID_ROOF}),
    "FASCIA": ((FASC_Y0 - PAD, FASC_Y0 + FASC_H + PAD), {ID_TRIM, ID_GUTTER}),
    "SOFFIT": ((SOF_Y0 - PAD, SOF_Y0 + SOF_H + PAD), {ID_TRIM}),
}


# ================================================================ bands
def paint_wall_band(c):
    """The wall: plinth, brick and the horizontal trim every wall shares, at
    the heights build.py's walls are cut to."""
    y0 = WALL_Y0
    top = y0 + m(Z_BAND)
    brickwork.paint(c, 0, ATLAS, y0, top + PAD, BRICK_IDS, TONE_COURSES, seed=17)
    Y = lambda z: y0 + m(z)                                    # noqa: E731
    # the plinth: three courses of dressed granite, staggered metre blocks,
    # the ground course a little darker
    c.paint(0, ATLAS, y0 - PAD, Y(Z_PLINTH), ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, YY, XX = c.field(0, ATLAS, y0 - PAD, Y(Z_PLINTH))
    k = np.floor((YY - y0) / m(0.3125)).astype(np.int64)
    bed = ((YY - y0) % m(0.3125)) < 1.0
    perp = ((XX + (k % 2) * 32.0) % 64.0) < 1.0
    joint = (bed & (YY > y0 + 1)) | perp
    tone = 0.94 + 0.10 * atlas.hash_unit(np.floor((XX + (k % 2) * 32.0) / 64.0)
                                         .astype(np.int64) % 32, k, 5)
    c.shade[sy, sx] = np.where(joint, 0.72, tone * np.where(k <= 0, 0.92, 1.0))
    c.ao[sy, sx] = np.where(joint, 0.78, 1.0)
    c.height[sy, sx] = np.where(joint, -0.004, 0.0)
    # the plinth cap: a moulded trim course, its drip's shadow on the granite
    c.paint(0, ATLAS, Y(Z_PLINTH), Y(Z_PLINTH_CAP), ID_TRIM, 1.0, 1.0)
    c.bevel(0, ATLAS, Y(Z_PLINTH), Y(Z_PLINTH_CAP), TRIM_H, 2.0, axes="y")
    c.mul(0, ATLAS, Y(Z_PLINTH), Y(Z_PLINTH) + 3, 0.80, ao=0.80)
    c.mul(0, ATLAS, Y(Z_PLINTH) - 2, Y(Z_PLINTH), 0.84, ao=0.78)
    c.mul(0, ATLAS, Y(Z_PLINTH_CAP), Y(Z_PLINTH_CAP) + 2, 0.88, ao=0.86)
    # the string course: a flat fascia under a projecting moulding
    zs, zm = Y(Z_STRING), Y(Z_STRING + course(2))
    c.paint(0, ATLAS, zs, Y(Z_UPPER), ID_TRIM, 1.0, 1.0)
    c.bevel(0, ATLAS, zs, zm, TRIM_H * 0.6, 1.5, axes="y")
    c.bevel(0, ATLAS, zm, Y(Z_UPPER), CORNICE_H, 2.5, base=TRIM_H * 0.6, axes="y")
    c.mul(0, ATLAS, zm - 1, zm + 1, 0.86, ao=0.80)
    c.mul(0, ATLAS, zs - 3, zs, 0.84, ao=0.76)                  # drip on the brick
    c.mul(0, ATLAS, Y(Z_UPPER), Y(Z_UPPER) + 2, 0.90, ao=0.86)
    # the frieze, its dentils, the cornice and the fascia under the soffit
    zf, zc = Y(Z_FRIEZE), Y(Z_CORNICE)
    c.paint(0, ATLAS, zf, Y(Z_BAND) + PAD, ID_TRIM, 1.0, 1.0, height=0.008)
    c.mul(0, ATLAS, zf - 3, zf, 0.88, ao=0.82)
    c.mul(0, ATLAS, zf, zf + 2, 0.86, ao=0.80)
    d0, d1 = Y(Z_FRIEZE + course(3)), zc - 3
    sy, sx, _YY, XX = c.field(0, ATLAS, d0, d1)
    tooth = (XX % 20.0) < 10.0
    c.shade[sy, sx] = np.where(tooth, 1.0, 0.70)
    c.ao[sy, sx] = np.where(tooth, 1.0, 0.62)
    c.height[sy, sx] = np.where(tooth, DENTIL_H, 0.0)
    c.mul(0, ATLAS, d0 - 2, d0, 0.82, ao=0.78)
    c.mul(0, ATLAS, d1, zc, 0.78, ao=0.70)
    zt = Y(Z_CORNICE_TOP)
    c.bevel(0, ATLAS, zc, zc + 10, TRIM_H, 1.5, axes="y")
    c.bevel(0, ATLAS, zc + 10, zt - 12, CORNICE_H, 2.0, base=TRIM_H, axes="y")
    c.bevel(0, ATLAS, zt - 12, zt, CORNICE_H * 0.8, 2.0, base=CORNICE_H * 0.4, axes="y")
    c.mul(0, ATLAS, zc + 9, zc + 11, 0.84, ao=0.80)
    c.mul(0, ATLAS, zt - 13, zt - 11, 0.80, ao=0.76)
    c.paint(0, ATLAS, zt, Y(Z_EAVE), ID_TRIM, 0.84, 0.74, height=0.0)
    c.paint(0, ATLAS, Y(Z_EAVE), Y(Z_BAND) + PAD, ID_TRIM, 0.94, 0.90, height=0.0)


def paint_roof(c):
    """Standing-seam steel, V up the slope at RPM rows a metre: seams every
    half metre along U, a snow guard a little up from the eave, a drip edge
    at the foot and the deck's flashing at the top."""
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_ROOF, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    xm = X % 32.0
    v = Y - y0
    k = RPM / PPM
    rib = xm < 2.0
    height = np.where(rib, SEAM_H * np.clip(np.sin(np.pi * xm / 2.0), 0.0, 1.0), 0.0)
    shade = np.where((xm >= 2.0) & (xm < 3.0), 0.90, 1.0)
    ao = np.where((xm >= 2.0) & (xm < 3.0), 0.84, 1.0)
    shade = np.where(v < 2, shade * 0.84, shade)
    g = round(0.6 * RPM)
    tube = (v >= g) & (v < g + 2.5)
    height = np.where(tube, np.maximum(height, 0.03 * k), height)
    shade = np.where((v >= g - 2) & (v < g), shade * 0.82, shade)
    ao = np.where((v >= g - 2) & (v < g + 2.5), np.minimum(ao, 0.86), ao)
    shade = np.where(v > h - 3, shade * 0.9, shade)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao


def paint_fascia(c):
    """The white fascia board, the dark half-round gutter hung across its top
    (PIPE_STRIP is its middle rows: the downpipes and the kit sample them)."""
    y0, top = FASC_Y0, FASC_Y0 + FASC_H
    c.paint(0, ATLAS, y0 - PAD, top + PAD, ID_TRIM, 1.0, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 - PAD, y0 + 1, ID_TRIM, 0.80, 0.80)
    g0 = top - 1 - GUTTER_PX
    c.paint(0, ATLAS, g0, top - 1, ID_GUTTER, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top - 1)
    u = 2.0 * (Y - g0) / GUTTER_PX - 1.0
    c.height[sy, sx] = 0.06 * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_GUTTER, 0.80)
    c.paint(0, ATLAS, top - 1, top + PAD, ID_GUTTER, 0.78, height=0.0)
    for i, f in enumerate((0.86, 0.80, 0.76)):
        c.mul(0, ATLAS, g0 - 3 + i, g0 - 2 + i, f, ao=0.8)
    sy, sx, _, X = c.field(0, ATLAS, g0 + 2, top - 1)
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.80, c.shade[sy, sx])


def paint_soffit(c):
    """Painted soffit boards along the eave, darker toward the wall."""
    y0, h = SOF_Y0, SOF_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_TRIM, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    groove = ((Y - y0) % (h / 3.0)) < 0.7
    t = np.clip((Y - y0) / float(h), 0.0, 1.0)
    c.shade[sy, sx] = np.where(groove, 0.78, 1.0) * (0.74 + 0.20 * t)
    c.ao[sy, sx] = np.minimum(np.where(groove, 0.80, 1.0), 0.76 + 0.24 * t)
    c.height[sy, sx] = np.where(groove, -0.003, 0.0)


# ================================================================ items
def _xz(kind, v):
    """Pixel mappers for an item's region: s (from its left edge) and z."""
    x, y, _w, _h = ITEM_REGION[(kind, v)]
    z0 = ITEMS[kind]["z0"]
    return (lambda s: x + m(s)), (lambda z: y + m(z - z0))


def bar(c, a0, a1, b0, b1, mid=ID_FRAME, shade=1.0, ao=0.86, h=FRAME_H, axes="xy",
        base=0.0):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, 1.0, base=base, axes=axes)


def casing(c, X, Z, s0, s1, z0, z1, w=CASING):
    """An architrave round the opening (s0..s1, z0..z1): a raised band *w*
    wide, bevelled at its outer edge, with a bead next to the opening."""
    a0, a1, b0, b1 = X(s0 - w), X(s1 + w), Z(z0), Z(z1 + course(3))
    c.paint(a0, a1, b0, b1, ID_TRIM, 1.0, 1.0)
    c.bevel(a0, a1, b0, b1, TRIM_H, 2.0)
    for e0, e1, f0, f1 in ((X(s0) - 3, X(s0), Z(z0), Z(z1) + 3), (X(s1), X(s1) + 3, Z(z0),
                                                                   Z(z1) + 3),
                           (X(s0) - 3, X(s1) + 3, Z(z1), Z(z1) + 3)):
        c.mul(e0, e1, f0, f1, 0.90, ao=0.86)
        c.lift(e0, e1, f0, f1, 0.010)


def head_cap(c, X, Z, s0, s1, z0, z1):
    """A cornice cap over a head, from z0 to z1 across s0..s1: a fillet, the
    projecting corona and its drip's shadow on the casing below."""
    a0, a1 = X(s0), X(s1)
    c.paint(a0, a1, Z(z0), Z(z1), ID_TRIM, 1.0, 1.0)
    c.bevel(a0, a1, Z(z0), Z(z0) + 5, TRIM_H, 1.5)
    c.bevel(a0, a1, Z(z0) + 5, Z(z1), CORNICE_H, 2.0, base=TRIM_H)
    c.mul(a0, a1, Z(z0), Z(z0) + 2, 0.80, ao=0.74)
    c.mul(a0, a1, Z(z0) + 4, Z(z0) + 6, 0.86, ao=0.80)
    c.mul(a0, a1, Z(z1) - 2, Z(z1), 1.04)


def sill(c, X, Z, s0, s1, z0, z1):
    """The sill under an opening, its nose catching the light."""
    a0, a1 = X(s0), X(s1)
    c.paint(a0, a1, Z(z0), Z(z1), ID_TRIM, 1.0, 1.0)
    c.bevel(a0, a1, Z(z0), Z(z1), CORNICE_H * 0.8, 1.5, axes="y")
    c.mul(a0, a1, Z(z0), Z(z0) + 1.5, 0.72, ao=0.70)


def sash_window(c, X, Z, s0, s1, z0, z1, transom=0.70):
    """Glass in a painted timber frame: a meeting mullion, a transom light
    over the casements, one bar across each casement."""
    a0, a1, b0, b1 = X(s0), X(s1), Z(z0), Z(z1)
    c.paint(a0, a1, b0, b1, ID_GLASS, 1.0, 1.0, height=0.0)
    f = 4.5
    bar(c, a0, a1, b0, b0 + f, axes="y")
    bar(c, a0, a1, b1 - f, b1, axes="y")
    bar(c, a0, a0 + f, b0, b1, axes="x")
    bar(c, a1 - f, a1, b0, b1, axes="x")
    mx = (a0 + a1) / 2.0
    bar(c, mx - 2.0, mx + 2.0, b0, b1, axes="x")
    bt = b0 + (b1 - b0) * transom
    bar(c, a0, a1, bt - 2.5, bt + 2.5, axes="y", h=FRAME_H * 1.2)
    c.mul(a0, a1, bt - 4.5, bt - 2.5, 0.92, ao=0.84)
    bm = b0 + (bt - b0) * 0.5
    bar(c, a0, a1, bm - 1.3, bm + 1.3, axes="y", h=FRAME_H * 0.8)
    # the dark gap where the frame meets the reveal, so a flush opening
    # still reads as set back
    for e in ((a0 - 1.5, a0, b0, b1), (a1, a1 + 1.5, b0, b1), (a0 - 1.5, a1 + 1.5, b1, b1 + 1.5),
              (a0 - 1.5, a1 + 1.5, b0 - 1.5, b0)):
        c.paint(*e, mid=ID_DARK, shade=1.0, ao=0.5, height=-0.01)


def paint_window(c, kind, v):
    """A window item: the sill, the architrave, the cornice cap over the
    head, and the sash in the opening. Every variant is painted alike; the
    rooms behind the glass differ by where each lies in the atlas."""
    it = ITEMS[kind]
    X, Z = _xz(kind, v)
    s0, s1, z0, z1 = it["openings"][0]
    x, y, w, h = ITEM_REGION[(kind, v)]
    c.paint(x, x + w, y, y + h, ID_TRIM, 1.0, 1.0, height=0.0)
    sill(c, X, Z, 0.0, it["w"], it["z0"], z0)
    casing(c, X, Z, s0, s1, z0, z1)
    head_cap(c, X, Z, 0.0, it["w"], z1 + course(3), it["z1"])
    sash_window(c, X, Z, s0, s1, z0, z1)


def leaf_panels(c, a0, a1, b0, b1, mid=ID_DOOR):
    """A panelled timber leaf from a0..a1, b0..b1 (px): stiles and rails
    round two raised fields."""
    c.paint(a0, a1, b0, b1, mid, 1.0, 0.95, height=0.0)
    st = m(0.11)
    hgt = b1 - b0
    for f0, f1 in ((b0 + m(0.20), b0 + hgt * 0.42), (b0 + hgt * 0.42 + m(0.12), b1 - st)):
        c.paint(a0 + st, a1 - st, f0, f1, mid, 1.06, 1.0)
        c.bevel(a0 + st, a1 - st, f0, f1, 0.012, 2.0)
        c.mul(a0 + st, a1 - st, f0, f0 + 1.0, 0.82, ao=0.80)
    c.mul(a0, a1, b0, b0 + 1.0, 0.80, ao=0.80)


def paint_door(c):
    """The main entrance: a pair of panelled leaves 2.0 x 2.34 m under a
    transom bar at 2.50 m, cut to the 2.58 m springing; over it a flush
    arched fanlight with radial bars, in a rusticated stone surround with
    voussoirs and a keystone, under a cornice cap. Below the threshold, the
    step's riser (the step is modelled up close)."""
    it = ITEMS["door"]
    X, Z = _xz("door", 0)
    x, y, w, h = ITEM_REGION[("door", 0)]
    c.paint(x, x + w, y, y + h, ID_TRIM, 1.0, 1.0, height=0.0)
    cx = X(1.25)
    # rusticated jambs: stone courses with sunk joints
    for a0, a1 in ((X(0.0), X(0.25)), (X(2.25), X(2.5))):
        c.bevel(a0, a1, y, Z(Z_DOOR_HEAD), TRIM_H, 1.5)
        for k in range(1, 9):
            zz = Z(k * course(4))
            c.paint(a0, a1, zz - 0.6, zz + 0.6, ID_TRIM, 0.70, 0.70, height=0.0)
    # the arch: voussoirs round the fanlight, a keystone at the crown
    zs, r0, r1 = Z(Z_DOOR_HEAD), m(1.0), m(1.25)

    def ring(X_, Y_):
        d = np.hypot(X_ - cx, Y_ - zs)
        return (d >= r0) & (d <= r1) & (Y_ >= zs)
    c.shape(cx - r1, cx + r1, zs, zs + r1, ring, ID_TRIM, 1.0, 1.0, height=TRIM_H)
    sy, sx, YY, XX = c.field(cx - r1, cx + r1, zs, zs + r1)
    ang = np.degrees(np.arctan2(YY - zs, XX - cx))
    d = np.hypot(XX - cx, YY - zs)
    joint = ((ang % 15.0) < 0.9) & (d >= r0) & (d <= r1)
    c.shade[sy, sx] = np.where(joint, 0.74, c.shade[sy, sx])
    c.height[sy, sx] = np.where(joint, 0.0, c.height[sy, sx])
    c.paint(cx - m(0.16), cx + m(0.16), zs + r0 - 2, zs + r1 + 3, ID_TRIM, 1.04, 1.0)
    c.bevel(cx - m(0.16), cx + m(0.16), zs + r0 - 2, zs + r1 + 3, CORNICE_H, 1.5)
    # the fanlight: glass in a radial frame, flush on the wall plane

    def fan(X_, Y_):
        return (np.hypot(X_ - cx, Y_ - zs) < r0 - 1.0) & (Y_ >= zs)
    c.shape(cx - r0, cx + r0, zs, zs + r0, fan, ID_GLASS, 1.0, 1.0, height=-0.02)
    for a in (30.0, 60.0, 90.0, 120.0, 150.0):
        t = math.radians(a)
        c.stroke((cx, zs), (cx + math.cos(t) * (r0 - 1), zs + math.sin(t) * (r0 - 1)), 2.2,
                 ID_FRAME, 1.0, 0.9, height=-0.005)

    def rim(X_, Y_):
        dd = np.hypot(X_ - cx, Y_ - zs)
        return (dd >= r0 - 3.5) & (dd < r0) & (Y_ >= zs)
    c.shape(cx - r0, cx + r0, zs, zs + r0, rim, ID_FRAME, 1.0, 0.86, height=-0.005)
    c.disc(cx, zs, m(0.18), ID_FRAME, 1.0, 0.9, height=-0.005)
    # the opening, behind the wall plane on the near tiers
    a0, a1 = X(0.25), X(2.25)
    c.paint(a0, a1, y, Z(Z_FLOOR), ID_PLINTH, 0.96, 0.80, height=0.0)
    c.mul(a0, a1, Z(Z_FLOOR) - 1, Z(Z_FLOOR), 0.8, ao=0.8)
    leaf_panels(c, a0 + 2, cx - 0.5, Z(Z_FLOOR), Z(Z_DOOR_TRANSOM))
    leaf_panels(c, cx + 0.5, a1 - 2, Z(Z_FLOOR), Z(Z_DOOR_TRANSOM))
    c.paint(cx - 0.5, cx + 0.5, Z(Z_FLOOR), Z(Z_DOOR_TRANSOM), ID_DARK, 1.0, 0.5, height=-0.01)
    bar(c, a0, a1, Z(Z_DOOR_TRANSOM), Z(Z_DOOR_HEAD), mid=ID_DOOR, shade=0.9, h=0.02)
    c.mul(a0, a1, Z(Z_DOOR_TRANSOM) - 1.5, Z(Z_DOOR_TRANSOM), 0.7, ao=0.7)
    for side in (-1, 1):
        hx = cx + side * 4.0
        c.paint(hx - 1.0, hx + 1.0, Z(Z_FLOOR + 0.95), Z(Z_FLOOR + 1.25), ID_METAL, 1.0,
                height=0.02)
    for e in ((a0 - 1.5, a0, y, Z(Z_DOOR_HEAD)), (a1, a1 + 1.5, y, Z(Z_DOOR_HEAD))):
        c.paint(*e, mid=ID_DARK, shade=1.0, ao=0.5, height=-0.01)
    # the cornice cap over the whole surround
    head_cap(c, X, Z, 0.0, 2.5, it["z1"] - course(3), it["z1"])


def paint_service(c):
    """The rear service door: a pair of panelled timber leaves 1.375 x 2.34 m
    on the ground floor's threshold, a head rail to the cut's head, a plain
    architrave and a cornice cap; the step's riser below the threshold."""
    it = ITEMS["service"]
    X, Z = _xz("service", 0)
    x, y, w, h = ITEM_REGION[("service", 0)]
    c.paint(x, x + w, y, y + h, ID_TRIM, 1.0, 1.0, height=0.0)
    s0, s1 = 0.25, 1.625
    casing(c, X, Z, s0, s1, 0.0, Z_DOOR_HEAD)
    head_cap(c, X, Z, 0.0, it["w"], it["z1"] - course(3), it["z1"])
    a0, a1 = X(s0), X(s1)
    cx = (a0 + a1) / 2.0
    c.paint(a0, a1, y, Z(Z_FLOOR), ID_PLINTH, 0.96, 0.80, height=0.0)
    leaf_panels(c, a0 + 2, cx - 0.5, Z(Z_FLOOR), Z(Z_DOOR_TRANSOM))
    leaf_panels(c, cx + 0.5, a1 - 2, Z(Z_FLOOR), Z(Z_DOOR_TRANSOM))
    c.paint(cx - 0.5, cx + 0.5, Z(Z_FLOOR), Z(Z_DOOR_TRANSOM), ID_DARK, 1.0, 0.5, height=-0.01)
    bar(c, a0, a1, Z(Z_DOOR_TRANSOM), Z(Z_DOOR_HEAD), mid=ID_DOOR, shade=0.88, h=0.02)
    c.mul(a0, a1, Z(Z_DOOR_TRANSOM) - 1.5, Z(Z_DOOR_TRANSOM), 0.7, ao=0.7)
    for side in (-1, 1):
        hx = cx + side * 3.5
        c.paint(hx - 1.0, hx + 1.0, Z(Z_FLOOR + 0.95), Z(Z_FLOOR + 1.15), ID_METAL, 1.0,
                height=0.02)
    for e in ((a0 - 1.5, a0, y, Z(Z_DOOR_HEAD)), (a1, a1 + 1.5, y, Z(Z_DOOR_HEAD))):
        c.paint(*e, mid=ID_DARK, shade=1.0, ao=0.5, height=-0.01)


def paint_group(c):
    """The entrance bay's upper storey: the balcony door (a glazed pair
    2.27 m tall under a heavy transom, a fanlight over it) between two tall
    windows, panelled pilasters between them, aprons under the windows behind
    the balustrade, all under one entablature."""
    it = ITEMS["group"]
    X, Z = _xz("group", 0)
    x, y, w, h = ITEM_REGION[("group", 0)]
    c.paint(x, x + w, y, y + h, ID_TRIM, 1.0, 1.0, height=0.0)
    c.bevel(x, x + w, y, y + h, TRIM_H, 2.0)
    zh = Z_TALL_HEAD
    # panelled pilasters between the openings and aprons under the windows
    for a, b in ((1.5, 2.125), (3.375, 4.0)):
        c.paint(X(a) + 4, X(b) - 4, Z(Z_UPPER) + 6, Z(zh) - 6, ID_TRIM, 0.92, 0.92)
        c.bevel(X(a) + 4, X(b) - 4, Z(Z_UPPER) + 6, Z(zh) - 6, TRIM_H * 0.5, 1.5,
                base=TRIM_H)
    for a, b in ((0.25, 1.5), (4.0, 5.25)):
        c.paint(X(a) + 3, X(b) - 3, Z(Z_UPPER) + 6, Z(Z_TALL_SILL) - 6, ID_TRIM, 0.90, 0.90)
        c.bevel(X(a) + 3, X(b) - 3, Z(Z_UPPER) + 6, Z(Z_TALL_SILL) - 6, TRIM_H * 0.5,
                1.5, base=TRIM_H)
        sill(c, X, Z, a - 0.1, b + 0.1, Z_TALL_SILL - course(1), Z_TALL_SILL)
        sash_window(c, X, Z, a, b, Z_TALL_SILL, zh, transom=0.68)
    # the balcony door: two glazed leaves to the transom, a fanlight above
    a0, a1, b0 = X(2.125), X(3.375), Z(Z_BAL_SILL)
    bt = Z(Z_BAL_TRANSOM)
    c.paint(a0, a1, b0, Z(zh), ID_GLASS, 1.0, 1.0, height=0.0)
    f = 4.5
    bar(c, a0, a1, b0, b0 + m(0.14), axes="y")
    bar(c, a0, a0 + f, b0, Z(zh), axes="x")
    bar(c, a1 - f, a1, b0, Z(zh), axes="x")
    bar(c, a0, a1, Z(zh) - f, Z(zh), axes="y")
    mx = (a0 + a1) / 2.0
    bar(c, mx - 2.5, mx + 2.5, b0, bt, axes="x")
    bar(c, mx - 1.5, mx + 1.5, bt, Z(zh), axes="x")
    for k in (1, 2):
        yy = b0 + m(0.14) + (bt - b0 - m(0.14)) * k / 3.0
        bar(c, a0, a1, yy - 1.3, yy + 1.3, axes="y", h=FRAME_H * 0.8)
    bar(c, a0, a1, bt, bt + m(0.12), axes="y", h=FRAME_H * 1.6)
    c.mul(a0, a1, bt - 2.0, bt, 0.84, ao=0.76)
    for e in ((a0 - 1.5, a0, b0, Z(zh)), (a1, a1 + 1.5, b0, Z(zh)),
              (a0 - 1.5, a1 + 1.5, Z(zh), Z(zh) + 1.5)):
        c.paint(*e, mid=ID_DARK, shade=1.0, ao=0.5, height=-0.01)
    # the entablature over the group
    c.paint(x, x + w, Z(zh), Z(zh + course(3)), ID_TRIM, 0.96, 1.0)
    c.bevel(x, x + w, Z(zh), Z(zh + course(3)), TRIM_H, 1.5, axes="y")
    head_cap(c, X, Z, 0.0, it["w"], zh + course(3), it["z1"])


def paint_pilaster(c):
    """A slender pilaster on the upper storey between two bays: a base, a
    plain shaft standing proud, a moulded capital under the frieze."""
    x, y, w, h = ITEM_REGION[("pilaster", 0)]
    c.paint(x, x + w, y, y + h, ID_TRIM, TRIM_SH, 1.0, height=0.0)
    c.bevel(x, x + w, y, y + h, TRIM_H, 2.0, axes="x")
    c.bevel(x, x + w, y, y + 10, CORNICE_H * 0.7, 1.5)
    c.mul(x, x + w, y + 10, y + 11, 0.84, ao=0.82)
    c.bevel(x, x + w, y + h - 13, y + h, CORNICE_H * 0.7, 1.5)
    c.mul(x, x + w, y + h - 14, y + h - 13, 0.80, ao=0.78)


# ================================================================ unique
def quoin_course(k, side):
    """Whether stone course *k* of a quoin strip is a long one: the two faces
    of a corner alternate, so a long stone on one is a short one on the
    other, as dressed quoins are laid."""
    return (k + (0 if side == "a" else 1)) % 2 == 0


def paint_quoins(c):
    """Toothed quoin strips, V up the corner from the ground to the frieze,
    U along the face from the block's outer corner: stone courses 0.3125 m
    high, the long ones the block's full face, the short ones 0.34 m, brick
    in the bond between."""
    long_px, short_px = m(QUOIN_DEPTH + QUOIN_PROUD), m(0.34375)
    for side, (x, y, w, h) in QUOIN.items():
        brickwork.paint(c, x - PAD, x + w + PAD, y - PAD, y + h + PAD, BRICK_IDS,
                        TONE_COURSES, seed=23)
        ch = m(0.3125)
        for k in range(int(math.ceil(h / ch))):
            b0, b1 = y + k * ch, min(y + h, y + (k + 1) * ch)
            a1 = x + (long_px if quoin_course(k, side) else short_px)
            c.paint(x - PAD, a1, b0, b1, ID_TRIM, 1.0, 1.0)
            c.bevel(x - PAD, a1, b0 + 0.6, b1 - 0.6, TRIM_H, 1.5, axes="xy")
            c.paint(x - PAD, a1, b0, b0 + 0.8, ID_TRIM, 0.72, 0.72, height=0.0)
            c.mul(a1, a1 + 1.5, b0, b1, 0.80, ao=0.76)


def paint_tower(c):
    """One face of the tower above the deck, z TOWER_FOOT .. TOWER_TOP: a
    stone band at the deck, brick between corner pilasters, a belt under the
    platform, the drum with its arched louvred belfry opening, the dentilled
    cornice under the dome."""
    x, y, w, h = TOWER
    Z = lambda z: y + m(z - TOWER_FOOT)                         # noqa: E731
    brickwork.paint(c, x - PAD, x + w + PAD, y - PAD, y + h + PAD, BRICK_IDS,
                    TONE_COURSES, seed=29)
    c.paint(x - PAD, x + w + PAD, y - PAD, Z(14.95), ID_PLINTH, 1.0, 1.0, height=0.0)
    c.paint(x - PAD, x + w + PAD, Z(14.95), Z(15.10), ID_TRIM, 1.0, 1.0)
    c.bevel(x - PAD, x + w + PAD, Z(14.95), Z(15.10), TRIM_H, 1.5, axes="y")
    c.mul(x - PAD, x + w + PAD, Z(15.10), Z(15.10) + 2, 0.86, ao=0.84)
    for a0, a1 in ((x - PAD, x + m(0.30)), (x + w - m(0.30), x + w + PAD)):
        c.paint(a0, a1, Z(15.10), Z(19.66), ID_TRIM, TRIM_SH, 1.0)
        c.bevel(a0, a1, Z(15.10), Z(19.66), TRIM_H, 1.5, axes="x")
    c.paint(x - PAD, x + w + PAD, Z(17.05), Z(17.3), ID_TRIM, 1.0, 1.0)
    c.bevel(x - PAD, x + w + PAD, Z(17.05), Z(17.3), TRIM_H, 1.5, axes="y")
    cx = x + w / 2.0
    zs = Z(19.25)

    def arch(r, sill_z):
        def test(X, Y):
            return (((np.abs(X - cx) <= r) & (Y >= Z(sill_z)) & (Y <= zs))
                    | (((X - cx) ** 2 + (Y - zs) ** 2 <= r * r) & (Y > zs)))
        return test
    c.shape(cx - m(0.64), cx + m(0.64), Z(18.30), zs + m(0.64), arch(m(0.62), 18.30),
            ID_TRIM, 1.0, 1.0, height=TRIM_H)
    c.shape(cx - m(0.5), cx + m(0.5), Z(18.42), zs + m(0.5), arch(m(0.48), 18.42),
            ID_DARK, 1.0, 0.40, height=-0.02)
    slat = m(0.16)

    def louvre(X, Y):
        return arch(m(0.42), 18.48)(X, Y) & (((Y - Z(18.48)) % slat) < slat * 0.62)
    c.shape(cx - m(0.44), cx + m(0.44), Z(18.48), zs + m(0.44), louvre, ID_FRAME, 0.62,
            0.55, height=-0.012)
    zc = Z(19.66)
    c.paint(x - PAD, x + w + PAD, zc, y + h + PAD, ID_TRIM, 1.0, 1.0, height=0.008)
    c.mul(x - PAD, x + w + PAD, zc - 2, zc, 0.84, ao=0.80)
    sy, sx, _YY, XX = c.field(x - PAD, x + w + PAD, zc + 4, zc + 14)
    tooth = ((XX - x) % 16.0) < 8.0
    c.shade[sy, sx] = np.where(tooth, 1.0, 0.70)
    c.height[sy, sx] = np.where(tooth, DENTIL_H, 0.0)
    c.bevel(x - PAD, x + w + PAD, zc + 16, y + h, CORNICE_H, 2.0, axes="y")
    c.mul(x - PAD, x + w + PAD, zc + 15, zc + 17, 0.80, ao=0.76)


def paint_chimney(c):
    """A rendered stack in a dark render, from under the deck to its top:
    the roof's flashing at its foot, render joints, a cap band."""
    x, y, w, h = CHIMNEY
    Z = lambda z: y + m(z - CHIM_FOOT)                          # noqa: E731
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_CHIM, 1.0, 0.94, height=0.0)
    for k in range(1, 7):
        zz = Z(Z_DECK + 0.25 * k)
        c.paint(x - PAD, x + w + PAD, zz - 0.5, zz + 0.5, ID_CHIM, 0.86, 0.86, height=-0.002)
    c.paint(x - PAD, x + w + PAD, y - PAD, Z(Z_DECK + 0.12), ID_GUTTER, 1.0, 0.9, height=0.0)
    c.mul(x - PAD, x + w + PAD, Z(Z_DECK + 0.12), Z(Z_DECK + 0.12) + 2, 0.82, ao=0.80)
    c.paint(x - PAD, x + w + PAD, Z(CHIM_TOP - 0.30), y + h + PAD, ID_CHIM, 1.25, 1.0)
    c.bevel(x - PAD, x + w + PAD, Z(CHIM_TOP - 0.30), y + h, 0.03, 1.5, axes="y")
    c.mul(x - PAD, x + w + PAD, Z(CHIM_TOP - 0.30) - 2, Z(CHIM_TOP - 0.30), 0.78, ao=0.74)


def paint_dome(c):
    """One facet of the dome, U across it, V up its meridian: painted steel
    with a seam down each edge and the middle."""
    x, y, w, h = DOME
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_ROOF, 1.0, 1.0, height=0.0)
    for xx in (x, x + w / 2.0, x + w):
        c.bevel(xx - 1.5, xx + 1.5, y - PAD, y + h + PAD, SEAM_H, 1.0, axes="x")
    c.mul(x - PAD, x + w + PAD, y - PAD, y + 2, 0.84, ao=0.84)


def paint_deck(c):
    """The flat deck in plan, DPPM texels a metre: painted steel sheet, seams
    every half metre along Y, cross seams every two metres."""
    x, y, w, h = DECK
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_ROOF, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    seam = ((X - x) % (0.5 * DPPM)) < 1.0
    cross = ((Y - y) % (2.0 * DPPM)) < 0.8
    c.height[sy, sx] = np.where(seam, SEAM_H * 0.6, np.where(cross, 0.004, 0.0))
    c.shade[sy, sx] = np.where(seam, 1.06, np.where(cross, 0.92, 1.0))


def paint_attic(c):
    """The clock attic's front, x -4 .. 4, from the wall top to the attic's
    top: brick on a trim base course, a framed panel round the dial (white
    ring, enamel face, hour marks, hands at three), a cornice under the
    pediment."""
    x, y, w, h = ATTIC_F
    Z = lambda z: y + m(z - Z_TOP)                              # noqa: E731
    X = lambda xx: x + m(xx + 4.0)                              # noqa: E731
    brickwork.paint(c, x - PAD, x + w + PAD, y - PAD, y + h + PAD, BRICK_IDS,
                    TONE_COURSES, seed=31)
    c.paint(x - PAD, x + w + PAD, y - PAD, Z(Z_TOP + course(3)), ID_TRIM, 1.0, 1.0)
    c.bevel(x - PAD, x + w + PAD, y, Z(Z_TOP + course(3)), TRIM_H, 1.5, axes="y")
    c.mul(x - PAD, x + w + PAD, Z(Z_TOP + course(3)), Z(Z_TOP + course(3)) + 2, 0.86, ao=0.84)
    f0, f1, g0, g1 = X(-3.25), X(3.25), Z(11.875), Z(14.3125)
    c.paint(f0, f1, g0, g1, ID_TRIM, 1.0, 1.0)
    c.bevel(f0, f1, g0, g1, TRIM_H, 2.0)
    fw = m(0.125)
    brickwork.paint(c, f0 + fw, f1 - fw, g0 + fw, g1 - fw, BRICK_IDS, TONE_COURSES, seed=37)
    c.mul(f0 + fw, f1 - fw, g0 + fw, g1 - fw, 0.92)
    c.mul(f0 + fw, f1 - fw, g1 - fw - 2, g1 - fw, 0.82, ao=0.80)
    cx, cy, r = X(DIAL_C[0]), Z(DIAL_C[1]), m(DIAL_R)
    c.disc(cx, cy, r, ID_TRIM, 1.0, 1.0, height=0.0)
    c.disc(cx, cy, r, ID_TRIM, 0.92, inner=r - 2.0)
    c.disc(cx, cy, r * 0.84, ID_CLOCK, 1.0, 1.0)
    for k in range(12):
        a = 2 * math.pi * k / 12.0
        tx, ty = cx + math.sin(a) * r * 0.72, cy + math.cos(a) * r * 0.72
        ln = 3.5 if k % 3 == 0 else 2.0
        c.stroke((tx, ty), (tx + math.sin(a) * ln, ty + math.cos(a) * ln), 1.6, ID_DARK, 1.0)
    c.stroke((cx, cy), (cx, cy + r * 0.62), 1.6, ID_DARK, 1.0)
    c.stroke((cx, cy), (cx + r * 0.42, cy), 2.4, ID_DARK, 1.0)
    c.disc(cx, cy, 2.0, ID_DARK, 1.0)
    c.paint(x - PAD, x + w + PAD, Z(14.375), y + h + PAD, ID_TRIM, 1.0, 1.0)
    c.bevel(x - PAD, x + w + PAD, Z(14.375), y + h, CORNICE_H, 2.0, axes="y")
    c.mul(x - PAD, x + w + PAD, Z(14.375) - 2, Z(14.375), 0.82, ao=0.78)


def paint_pediment(c):
    """The pediment's front: a brick tympanum inside a white raking cornice
    and a horizontal cornice along its foot."""
    x, y, w, h = PEDIMENT
    cx = x + w / 2.0
    brickwork.paint(c, x - PAD, x + w + PAD, y - PAD, y + h + PAD, BRICK_IDS,
                    TONE_COURSES, seed=41)
    half = w / 2.0
    rake = m(0.28)
    slope = h / half

    def outer(X, Y):
        return (Y >= y - PAD) & (np.abs(X - cx) <= half * (1.0 - (Y - y) / h) + PAD)

    def band(X, Y):
        d = (half * (1.0 - (Y - y) / h) - np.abs(X - cx)) / math.sqrt(1.0 + 1.0 / slope ** 2)
        return (d < rake) | (Y < y + m(course(3)))
    sy, sx, YY, XX = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    inside = outer(XX, YY)
    cornice = inside & band(XX, YY)
    c.mid[sy, sx] = np.where(cornice, ID_TRIM, c.mid[sy, sx])
    c.shade[sy, sx] = np.where(cornice, 1.0, c.shade[sy, sx])
    c.ao[sy, sx] = np.where(cornice, 1.0, c.ao[sy, sx])
    c.height[sy, sx] = np.where(cornice, CORNICE_H, c.height[sy, sx])
    d = (half * (1.0 - (YY - y) / h) - np.abs(XX - cx)) / math.sqrt(1.0 + 1.0 / slope ** 2)
    edge = inside & (np.abs(d - rake) < 1.2) & (YY >= y + m(course(3)))
    c.shade[sy, sx] = np.where(edge, 0.80, c.shade[sy, sx])
    c.ao[sy, sx] = np.where(edge, 0.78, c.ao[sy, sx])
    c.mul(x - PAD, x + w + PAD, y + m(course(3)), y + m(course(3)) + 2, 0.86, ao=0.82)


def paint_balusters(c, rect, pitch=0.22):
    """A balustrade's dado, solid: turned balusters standing proud of the
    dark recess between them, as relief."""
    x, y, w, h = rect
    c.paint(x - PAD, x + w + PAD, y - PAD, y + h + PAD, ID_TRIM, 0.52, 0.62, height=-0.01)
    sy, sx, Y, X = c.field(x - PAD, x + w + PAD, y - PAD, y + h + PAD)
    t = np.clip((Y - y) / h, 0.0, 1.0)
    rad = m(0.045) * (1.0 + 0.55 * np.exp(-((t - 0.30) / 0.14) ** 2)
                      - 0.25 * np.exp(-((t - 0.78) / 0.08) ** 2))
    p = m(pitch)
    dx = np.abs(((X - x) % p) - p / 2.0)
    post = dx <= rad
    c.mid[sy, sx] = ID_TRIM
    c.shade[sy, sx] = np.where(post, 1.0 - 0.10 * (dx / np.maximum(rad, 1e-3)) ** 2, 0.52)
    c.ao[sy, sx] = np.where(post, 1.0, 0.62)
    c.height[sy, sx] = np.where(post, 0.03 * np.sqrt(np.clip(1.0 - (dx / np.maximum(rad, 1e-3))
                                                             ** 2, 0.0, 1.0)), -0.01)


def paint_patches(c):
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0),
        "reveal": (ID_TRIM, 0.62, 0.55),
        "trim": (ID_TRIM, 1.0, 1.0),
        "trim_shade": (ID_TRIM, 0.80, 0.80),
        "sill_top": (ID_TRIM, 0.94, 0.90),
        "roof": (ID_ROOF, 1.0, 1.0),
        "soot": (ID_SOOT, 1.0, 0.35),
        "step": (ID_PLINTH, 1.0, 0.95),
        "rim": (ID_CHIM, 1.25, 1.0),
        "gutter": (ID_GUTTER, 1.0, 1.0),
        "frame": (ID_FRAME, 0.9, 0.9),
        "cutter": (ID_TRIM, 0.90, 0.88),
        "lid": (ID_ROOF, 0.92, 0.95),
        "rail": (ID_TRIM, 0.96, 1.0),
    }
    atlas.paint_patches(c, PATCHES, spec)


# ================================================================ checks
def all_regions():
    rects = {"%s_%d" % k: r for k, r in ITEM_REGION.items()}
    rects.update({"elev_" + n: r for n, r in ELEV.items()})
    rects.update({"quoin_a": QUOIN["a"], "quoin_b": QUOIN["b"], "tower": TOWER,
                  "chimney": CHIMNEY, "dome": DOME, "deck": DECK, "attic": ATTIC_F,
                  "pediment": PEDIMENT, "balusters": BALUS, "plat_balusters": PLAT_BALUS})
    rects.update(PATCHES)
    return rects


def check_regions():
    """Fail the bake if two regions overlap, run off the sheet or into the
    bands, or if a band runs into the next."""
    problems = atlas.region_problems(all_regions(), ATLAS, bands_top=BANDS_TOP, band_gap=4)
    for a, b, what in ((WALL_Y0 + m(Z_BAND) + PAD, ROOF_Y0 - PAD, "wall into roof"),
                       (ROOF_Y0 + ROOF_H + PAD, FASC_Y0 - PAD, "roof into fascia"),
                       (FASC_Y0 + FASC_H + PAD, SOF_Y0 - PAD, "fascia into soffit")):
        if a > b:
            problems.append("band %s" % what)
    xd, yd, wd, hd = DECK
    for x0, x1, y0, y1 in ((-21.4, 21.4, -7.3, 13.5),):
        if (x0 - DECK_O[0]) * DPPM < 0 or (x1 - DECK_O[0]) * DPPM > wd or \
                (y0 - DECK_O[1]) * DPPM < 0 or (y1 - DECK_O[1]) * DPPM > hd:
            problems.append("the deck region does not cover the deck")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    The wall band's V is height from the ground, so the plinth's soil, the
    splash and bloom above it and the dust under the cornice land the same on
    every wall. Glass and the clock's face stay clean."""
    steel = (ID_ROOF, ID_GUTTER)
    w = weathering.Weather(c, clean=(ID_GLASS, ID_CLOCK), steel=steel)
    w.grime()
    w.fade((ID_TRIM, ID_FRAME, ID_DOOR), amount=0.08, base=0.03)
    w.wash((ID_BRICK, ID_BRICK2, ID_MORTAR))
    y0 = WALL_Y0
    top = y0 + m(Z_BAND) + PAD
    masonry = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    w.plinth(0, ATLAS, y0, y0 + m(Z_PLINTH), (ID_PLINTH,))
    w.splash(0, ATLAS, y0 + m(Z_PLINTH_CAP), y0 + m(Z_PLINTH_CAP + 1.0), masonry,
             amount=0.10, fall=0.25)
    w.bloom(0, ATLAS, y0 + m(Z_PLINTH_CAP), y0 + m(Z_PLINTH_CAP + 1.2), masonry,
            amount=0.10, fade=m(0.8))
    w.runs(0, ATLAS, y0 + m(Z_STRING - 0.8), y0 + m(Z_STRING), masonry, 0.10, fall=m(0.35))
    w.runs(0, ATLAS, y0 + m(Z_PLINTH_CAP - 0.6), y0 + m(Z_PLINTH), (ID_PLINTH,), 0.10,
           fall=m(0.3))
    w.shelter(0, ATLAS, y0 + m(Z_FRIEZE), y0 + m(Z_CORNICE), (ID_TRIM,), amount=0.08,
              top=y0 + m(Z_CORNICE))
    w.runs(0, ATLAS, y0 + m(Z_FRIEZE - 0.6), y0 + m(Z_FRIEZE), masonry, 0.08, fall=m(0.3))
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, SLOPE_LEN, (ID_ROOF,))
    g0 = FASC_Y0 + FASC_H - 10.0
    w.runs(0, ATLAS, FASC_Y0 - PAD, g0, (ID_TRIM,), 0.16, fall=6.0, lo=0.4, hi=1.6)
    w.shelter(0, ATLAS, SOF_Y0, SOF_Y0 + 6, (ID_TRIM,), amount=0.06)
    # windows: dirt on the sill, runs down the casing under the cap, water on
    # the sash's bottom rail
    for (kind, v), (x, y, rw, rh) in ITEM_REGION.items():
        it = ITEMS[kind]
        if kind in WINDOW_KINDS:
            s0, s1, oz0, oz1 = it["openings"][0]
            w.window(x, y, rw, rh, y + m(oz0 - it["z0"]), y + m(oz1 - it["z0"]), 4.5,
                     (ID_TRIM,), (ID_FRAME,))
        elif kind in ("door", "service"):
            s0, s1, _z0, _z1 = it["openings"][0]
            a0, a1 = x + m(s0), x + m(s1)
            w.door(a0, a1, y + m(Z_FLOOR), y + m(Z_DOOR_TRANSOM), (ID_DOOR,),
                   handle=((a0 + a1) / 2.0 + 4.0, y + m(Z_FLOOR + 1.1)))
            w.splash(x, x + rw, y, y + m(1.0), (ID_TRIM, ID_PLINTH), amount=0.14)
        elif kind == "group":
            for s0, s1, oz0, oz1 in it["openings"]:
                w.add("D", x + m(s0), x + m(s1), y + m(oz0 - it["z0"]),
                      y + m(oz0 - it["z0"]) + 5, 0.10, (ID_FRAME,))
            w.runs(x, x + rw, y + rh - 40, y + rh - 15, (ID_TRIM,), 0.08, fall=12.0)
    for x, y, rw, rh in QUOIN.values():
        w.splash(x - PAD, x + rw + PAD, y, y + m(1.0), (ID_TRIM,) + masonry)
    x, y, rw, rh = TOWER
    w.runs(x, x + rw, y + m(16.4 - TOWER_FOOT), y + m(17.05 - TOWER_FOOT), masonry, 0.10,
           fall=m(0.4))
    w.runs(x, x + rw, y + m(18.9 - TOWER_FOOT), y + m(19.66 - TOWER_FOOT), masonry, 0.10,
           fall=m(0.4))
    w.splash(x, x + rw, y + m(Z_DECK - TOWER_FOOT), y + m(Z_DECK - TOWER_FOOT + 0.8),
             (ID_PLINTH, ID_TRIM) + masonry, amount=0.12)
    x, y, rw, rh = CHIMNEY
    w.runs(x, x + rw, y, y + rh - m(0.30), (ID_CHIM,), 0.16, fall=m(0.5))
    w.splash(x, x + rw, y + m(Z_DECK - CHIM_FOOT), y + m(Z_DECK - CHIM_FOOT + 0.6),
             (ID_CHIM,), amount=0.12)
    x, y, rw, rh = ATTIC_F
    w.runs(x, x + rw, y + m(13.6 - Z_TOP), y + m(14.375 - Z_TOP), masonry, 0.08, fall=m(0.4))
    for x, y, rw, rh in (BALUS, PLAT_BALUS):
        w.runs(x, x + rw, y, y + rh, (ID_TRIM,), 0.10, fall=rh * 0.6)
    # the deck: dust in broad patches where it lies flat, light chalking
    x, y, rw, rh = DECK
    w.add("D", x - PAD, x + rw + PAD, y - PAD, y + rh + PAD,
          lambda Y, X, nz: 0.05 + 0.08 * nz("big"), (ID_ROOF,))
    w.add("F", x - PAD, x + rw + PAD, y - PAD, y + rh + PAD,
          lambda Y, X, nz: 0.03 + 0.04 * nz("big"), (ID_ROOF,))
    x, y, rw, rh = DOME
    w.runs(x, x + rw, y, y + rh, (ID_ROOF,), 0.10, fall=rh * 0.5)
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO, height and weather, then padding."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_wall_band(c)
    paint_roof(c)
    paint_fascia(c)
    paint_soffit(c)
    c.check_bands(BAND_IDS)
    for (kind, v) in ITEM_REGION:
        if kind in WINDOW_KINDS:
            paint_window(c, kind, v)
    paint_door(c)
    paint_service(c)
    paint_group(c)
    paint_pilaster(c)
    paint_quoins(c)
    paint_tower(c)
    paint_chimney(c)
    paint_dome(c)
    paint_deck(c)
    paint_attic(c)
    paint_pediment(c)
    paint_balusters(c, BALUS)
    paint_balusters(c, PLAT_BALUS, pitch=0.20)
    paint_patches(c)
    # the materials' own grain: pores in masonry and render, a faint sheen
    # variation in painted steel; periodic, so the bands still wrap
    wear = 0.02 * atlas.noise(c, 3, 40.0) + 0.01 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    masonry = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH, ID_TRIM, ID_CHIM))
    pores = atlas.noise(c, 9, 0.7)
    c.shade[masonry] *= 1.0 + 0.035 * pores[masonry]
    c.height[masonry] += 0.0005 * pores[masonry]
    del pores
    sheet = np.isin(c.mid, (ID_ROOF, ID_GUTTER))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    c.shade[sheet] *= 1.0 + 0.016 * grain[sheet]
    del grain, masonry, sheet
    weather(c)
    c.pad()
    return c


# ============================================================ elevations
def compose_elevations(maps):
    """The far tiers' walls: each wall's elevation at EPPM, composed from the
    resolved maps -- the band at the wall's U, its items at their places, the
    quoins at its convex corners, its downpipes -- at 64 texels a metre, then
    box-filtered to EPPM (colours in linear light, normals renormalised) and
    written into its ELEV region with a two-texel gutter."""
    f = int(round(PPM / EPPM))
    H = int(round(Z_TOP * PPM))
    lin = {"albedo", "emission"}
    pipe_rgb = np.asarray(COLOUR[ID_GUTTER], np.float32) * 0.92
    pipe_orm = np.asarray((255.0, SURFACE[ID_GUTTER][0] * 255.0, 0.0), np.float32)
    pipes = {}
    for name, s in PIPES:
        pipes.setdefault(name, []).append(s)
    for wall in WALLS:
        L = wall["L"]
        W = int(round(L * PPM))
        cols = (np.round((wall["u"] * PPM)) + np.arange(W)).astype(np.int64) % ATLAS
        rows = np.arange(H) + WALL_Y0
        out = {}
        for key, a in maps.items():
            e = a[rows][:, cols].astype(np.float32)
            for kind, s, v in wall["items"]:
                x, y, rw, rh = ITEM_REGION[(kind, v)]
                l, _r, z0, _z1 = item_rect(kind, s)
                c0, r0 = int(round(m(l))), int(round(m(z0)))
                rw, rh = int(round(rw)), int(round(rh))
                e[r0:r0 + rh, c0:c0 + rw] = a[int(y):int(y) + rh, int(x):int(x) + rw]
            for at_start, convex in ((True, wall["convex0"]), (False, wall["convex1"])):
                if not convex:
                    continue
                side = "b" if at_start else "a"
                qx, qy, _qw, qh = QUOIN[side]
                n = int(round(m(QUOIN_DEPTH)))
                off = int(round(m(QUOIN_PROUD)))
                strip = a[int(qy):int(qy) + int(qh), int(qx) + off:int(qx) + off + n]
                if at_start:
                    e[:int(qh), :n] = strip
                else:
                    e[:int(qh), W - n:] = strip[:, ::-1]
            for s in pipes.get(wall["name"], ()):
                p0, p1 = int(round(m(s - PIPE_W / 2.0))), int(round(m(s + PIPE_W / 2.0)))
                z0, z1 = int(round(m(0.2))), int(round(m(Z_EAVE)))
                if key == "albedo":
                    across = 0.80 + 0.30 * np.sin(np.linspace(0.3, 2.8, p1 - p0))
                    e[z0:z1, p0:p1] = pipe_rgb[None, None, :] * across[None, :, None]
                elif key == "orm":
                    e[z0:z1, p0:p1] = pipe_orm
                elif key == "normal":
                    e[z0:z1, p0:p1] = (127.5, 127.5, 255.0)
                else:
                    e[z0:z1, p0:p1] = 0.0
            if key in lin:
                e = atlas.srgb_to_linear(e)
            e = e.reshape(H // f, f, W // f, f, 3).mean(axis=(1, 3))
            if key in lin:
                e = atlas.linear_to_srgb(e)
            if key == "normal":
                n = e / 127.5 - 1.0
                n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
                e = (n * 0.5 + 0.5) * 255.0
            out[key] = e
        x, y, ew, eh = ELEV[wall["name"]]
        for key, e in out.items():
            a = maps[key]
            g = 2
            padded = np.pad(e, ((g, g), (g, g), (0, 0)), mode="edge")
            a[y - g:y + eh + g, x - g:x + ew + g] = padded
    return maps


# ================================================================ export
CURTAIN = (150, 140, 124)     # sRGB: pale drawn-back curtains, in the room's shade
CURTAIN_MIX = 0.32
CURTAINED = (("gf", 1), ("uf", 2), ("gf125", 1), ("uf125", 2))


def curtains(rgb, glass):
    """Curtains drawn back to either side behind some windows' lower lights:
    part of the room, so albedo only (the night's panes are untouched).
    Painted after glazing.rooms(), on the glass pixels of a few variants."""
    for kind, v in CURTAINED:
        x, y, w, h = ITEM_REGION[(kind, v)]
        it = ITEMS[kind]
        s0, s1, z0, z1 = it["openings"][0]
        a0, a1 = int(math.floor(x + m(s0))), int(math.ceil(x + m(s1)))
        b0 = int(math.floor(y + m(z0 - it["z0"])))
        b1 = int(math.ceil(y + m(z0 - it["z0"] + (z1 - z0) * 0.70)))
        sub, msk = rgb[b0:b1, a0:a1], glass[b0:b1, a0:a1]
        u = (np.arange(a0, a1) + 0.5 - (a0 + a1) / 2.0) / ((a1 - a0) / 2.0)
        cover = np.clip((np.abs(u) - 0.62) / 0.12, 0.0, 1.0)
        fold = 0.90 + 0.10 * np.sin(np.arange(a0, a1) * 1.9)
        mix = (cover * CURTAIN_MIX)[None, :, None]
        lin = atlas.srgb_to_linear(sub)
        tgt = atlas.srgb_to_linear(np.asarray(CURTAIN, np.float32))[None, None, :] \
            * fold[None, :, None]
        out = atlas.linear_to_srgb(lin * (1.0 - mix) + tgt * mix)
        sub[msk] = out[msk]
    return rgb


def export(out_dir, ss=atlas.SS):
    """Paint, resolve every map, compose the elevations into all four, save.
    No occupancy or schedule is baked in."""
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.010)
    c.weather.dust(cav, BRICK_IDS)
    rough = 0.04 * atlas.noise(c, 13, 20.0)
    lut = np.zeros((256, 3), np.float32)
    for i, col in COLOUR.items():
        lut[i] = col
    maps = {"orm": atlas.orm(c, SURFACE, rough, 0.5 * cav)}
    del rough
    maps["normal"] = atlas.normal_map(c, flat_ids=(ID_GLASS, ID_CLOCK))
    maps["emission"] = glazing.night_rooms(atlas.coverage(c, ID_GLASS) > 0,
                                           atlas.emission_colours(c, EMIT))
    glass = atlas.coverage(c, ID_GLASS) >= 0.5
    rgb = glazing.rooms(glass, atlas.albedo(c, lut, grime=0.25 * cav))
    maps["albedo"] = curtains(rgb, glass)
    del c, cav
    maps = compose_elevations(maps)
    path = os.path.join(out_dir, ASSET)
    return [atlas.save(maps["orm"], path + "_orm.png"),
            atlas.save(maps["normal"], path + "_normal.png"),
            atlas.save(maps["emission"], path + "_emission.png"),
            atlas.save(maps["albedo"], "%s_albedo_%s.png" % (path, DEFAULT_VARIANT))]


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
