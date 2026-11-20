# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of kaivostorni_concrete, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite mid-century Nordic mine headframe (kaivostorni): a 6 x 6 m
board-marked concrete shaft tower on a slightly wider base, a head room
cantilevered 0.8 m east and west at the top for the winding gear, under a
shallow steel gable roof, and a low shaft-collar annex against the east side
with the big steel door. The head room's front stands open on two spoked
rope sheaves, whose ropes leave east toward the hoist. A caged wall ladder
runs up the back to the roof.

Construction is a set of closed solids unioned with Blender's exact boolean:
the tower (shaft and head room as one ring of walls, the cantilevers' soffits
included, the sheave bay recessed into its front), the base, the annex,
the two roof slabs, three downpipes (scripts/downpipes.py), the sheaves
(rims, hubs, spokes, axles, ropes), the wall ladder
(scripts/roof_safety.py) and its cage, which that module does not build.
The base stands round the shaft's foot and the annex runs into the shaft,
so the union removes every buried wall. The result is the boundary of one
empty volume, so no interior geometry can occur.

The walls are textured as a trim sheet (see facade_atlas.py). The tower is
taller than any band, so every wall is cut at the 4 m joints and each strip
above the first maps onto the same band, W2, which repeats in V. Every
number the two files share is imported from facade_atlas.py.
"""

import importlib
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector, geometry


HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import facade_atlas as L  # noqa: E402  (layout constants shared with the atlas)
importlib.reload(L)

ASSET = L.ASSET
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import downpipes as DP  # noqa: E402
import model_facts  # noqa: E402
import roof_safety as RS  # noqa: E402
from asset_build import to_object, union  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT)
PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ------------------------------------------------------------------ massing
# Front faces -Y. The shaft is centred on the build origin.
TX = TY = 3.00                  # shaft half-sizes, 6.0 x 6.0 m
HX = 3.80                       # head room half-length: 0.80 m cantilevers E and W
BX = 3.25                       # base half-size, 6.5 x 6.5 m
Z_SH0 = 1.00                    # the tower solid's foot, buried in the base
Z_BASE = 3.70                   # the base's vertical faces
BASE_IN = 0.35                  # its 45 degree top runs this far in, to
Z_BASE_TOP = Z_BASE + BASE_IN   # 4.05 at 2.90 m, inside the shaft
Z_HEAD = 17.00                  # the head room's underside, the cantilevers' soffit
Z_EAVE = 20.80                  # the head room roof's underside at the eave walls
Z_TOP = Z_EAVE + 0.10           # walls run on into the slab
H_TAN = math.tan(math.radians(15.0))
ROOF_T = L.FASC_H / PPM         # slabs' vertical thickness
EAVE_OV = 0.40                  # front and back eaves
RAKE_OV = 0.30                  # east and west rakes, past the cantilevers
Z_APEX = Z_TOP + TY * H_TAN
Z_EDGE = Z_EAVE + ROOF_T - EAVE_OV * H_TAN      # the sheet's top at the fascia

# The shaft-collar annex against the shaft's east side, its mono-pitch roof
# falling away from the tower. It runs A_IN into the shaft, so the union
# meets no coincident walls, and is set back from the shaft's front and back
# so its rakes stop 0.15 m short of the shaft's face planes.
A_IN = 0.15
AX0, AX1 = TX - A_IN, 7.40
AY = 2.60
A_L = AX1 - AX0
A_TAN = math.tan(math.radians(10.0))
Z_A_EAVE = 4.30
Z_A_TOP = Z_A_EAVE + 0.10
Z_A_HIGH = Z_A_TOP + A_L * A_TAN               # wall top, buried in the shaft
A_EAVE_OV = 0.40
A_RAKE_OV = 0.25

# --------------------------------------------------------------- elevations
# Each wall runs counter-clockwise seen from above, outward face on its
# right: (p0, p1, outline kind, openings). Openings are (kind, s, z): s is
# the centre along the wall from p0, z the sill or threshold.
# Stair landings light the shaft: three windows stacked over the door on the
# front, the other faces staggered between them. The head room's front is the
# sheave bay (below); its back has a strip of three windows, the ladder taking
# the west end. The west gable has two louvred vents; the east gable, toward
# the hoist, the opening the ropes leave by and one vent.
Z_SILL_HEAD = 18.10
TOWER_WALLS = {
    "front": ((-HX, -TY), (HX, -TY), "t_eave", [
        ("win", 2.30, 5.20), ("win", 2.30, 9.20), ("win", 2.30, 13.20)]),
    "e_shaft": ((TX, -TY), (TX, TY), "shaft", [("win", 3.00, 9.20)]),
    "e_head": ((HX, -TY), (HX, TY), "t_gable", [
        ("rope", 0.95, Z_SILL_HEAD), ("louvre", 4.40, Z_SILL_HEAD)]),
    "back": ((HX, TY), (-HX, TY), "t_eave", [
        ("win", 2.80, 10.60),
        ("win", 2.00, Z_SILL_HEAD), ("win", 3.20, Z_SILL_HEAD),
        ("win", 4.40, Z_SILL_HEAD)]),
    "w_shaft": ((-TX, TY), (-TX, -TY), "shaft", [
        ("win", 3.00, 6.60), ("win", 3.00, 14.60)]),
    "w_head": ((-HX, TY), (-HX, -TY), "t_gable", [
        ("louvre", 1.60, Z_SILL_HEAD), ("louvre", 4.40, Z_SILL_HEAD)]),
}
BASE_WALLS = {
    "b_front": ((-BX, -BX), (BX, -BX), "base", [("door", 1.75, L.Z_FLOOR)]),
    "b_east": ((BX, -BX), (BX, BX), "base", []),
    "b_back": ((BX, BX), (-BX, BX), "base", [("win", 2.25, 1.50)]),
    "b_west": ((-BX, BX), (-BX, -BX), "base", [("win", 3.25, 1.50)]),
}
ANNEX_WALLS = {
    "a_front": ((AX0, -AY), (AX1, -AY), "a_down", [("door_vehicle", 2.50, L.Z_FLOOR)]),
    "a_east": ((AX1, -AY), (AX1, AY), "a_eave", [("win", 3.40, 1.50)]),
    "a_back": ((AX1, AY), (AX0, AY), "a_up", [("louvre", 2.10, 2.00)]),
    "a_west": ((AX0, AY), (AX0, -AY), "a_high", []),
}
ALL_WALLS = {**TOWER_WALLS, **BASE_WALLS, **ANNEX_WALLS}
# Offsets into the tiling bands, in metres; each 4 m strip above the first
# shifts by STRIP_SHIFT more, so the band's 4 m repeat does not stack up the
# tower in one column.
U_OFF = {"front": 0.0, "e_shaft": 7.2, "e_head": 6.6, "back": 13.2,
         "w_shaft": 3.1, "w_head": 2.5, "b_front": 0.35, "b_east": 6.85,
         "b_back": 13.35, "b_west": 9.6, "a_front": 4.1, "a_east": 8.9,
         "a_back": 14.1, "a_west": 0.0}
STRIP_SHIFT = 3.30

# The sheave bay: the head room's front stands open over the sheave deck,
# BAY_DEPTH deep to a dark back, and shows the two rope sheaves face-on. The
# hoist house is to the east, beyond the annex: the ropes run off the
# sheaves' tops toward the east gable and leave by its rope opening, so the
# sheaves' planes are parallel to the front. The bay's size, the sheaves'
# centres and the ropes are facade_atlas.py's (bay-local metres); here is
# where it stands. It runs from its sill on the deck up past the joint at
# 20 m to 0.25 m under the eave, so the two strips it crosses are notched
# round it (notch()) rather than holed. East of it the front downpipe runs.
BAY_S0 = 0.35                   # its west jamb, along the front wall (x -3.45)
BAY_Z0 = 17.30                  # the sheave deck, 0.30 m over the soffit
BAY_S1, BAY_Z1 = BAY_S0 + L.BAY_W, BAY_Z0 + L.BAY_H
BAY_REVEAL = 0.25               # the wall's thickness: concrete; dark beyond
BAY_DEPTH = 2.00                # to the dark back
BAYS = {"front": (BAY_S0, BAY_S1, BAY_Z0, BAY_Z1)}
SHEAVE_DEPTH = (0.55, 1.25)     # each sheave's mid-plane behind the wall face
SHEAVE_W = 0.22                 # the rim's width along the axle
SPOKE_T = 0.06                  # a spoke's thickness along the axle
HUB_W = 0.30                    # the hub's length along the axle
AXLE_R = 0.08                   # the axle runs back into the bay's back
# Per tier: how each sheave is built, its rim's sides, its hub's and axle's
# sides, and whether the ropes are. "spoked": rim, hub, spokes and axle;
# "disc": one closed disc whose faces sample the painted sheave card
# (facade_atlas.paint_card); None: the bay is flat and painted with the
# sheaves (facade_atlas.paint_bay).
SHEAVE_MODES = (("spoked", 32, 12, True), ("spoked", 20, 8, False),
                ("disc", 12, 0, False), None)


def bay_mode(level):
    """recess - LOD0-LOD2: the bay open BAY_DEPTH deep, its sheaves modelled.
    flush   - LOD3: one face in the wall, painted with the sheaves."""
    return "flush" if SHEAVE_MODES[level] is None else "recess"


# Downpipes (scripts/downpipes.py). The head room's front and back eave
# walls are flush with the shaft, so a pipe from each gutter runs straight
# down the shaft's face at its east end, clear of the windows, and jogs out
# over the base's sloped top onto the base's face. The annex's runs down its
# outer, east wall at the front end.
PIPE_Z_JOG = 3.95               # the jog's foot, on the base's face
PIPE_STEP = BX - TY             # 0.25 m, the base's projection


class StepPipe(DP.Pipe):
    """A downpipe that jogs out by *step* over a plinth or base whose face
    stands proud of the wall it hangs on, its 45 degree jog ending at
    *z_jog*. The rest of its path, the swan-neck and the shoe included, is
    DP.Pipe's; only the part below the jog stands *step* further out.

    The shoe stays on every tier, unbent ones too: kicked out from a face
    already *step* proud, it is the building's outermost point on its side,
    and every tier keeps LOD0's extents."""

    def __init__(self, pipe, z_jog, step):
        DP.Pipe.__init__(self, tuple(pipe.p0), tuple(pipe.p0 + pipe.t * pipe.length),
                         pipe.s, pipe.under, pipe.outlet)
        self.z_jog, self.step = z_jog, step

    def path(self, bent=True):
        pts = DP.Pipe.path(self, bent)
        k = 3 if (self.outlet is not None and bent) else 1
        upper = pts[:k]
        lower = DP.Pipe.path(self, True)[-2:]                      # the shoe
        if upper[-1][1] < self.z_jog + self.step + 0.05:
            raise ValueError("a stepped downpipe's swan-neck reaches the jog")
        return (upper + [(DP.OUT, self.z_jog + self.step),
                         (DP.OUT + self.step, self.z_jog)]
                + [(o + self.step, z) for o, z in lower])


PIPE_SPOTS = [("front", 6.45), ("back", 1.15), ("a_east", 0.30)]
DOWNPIPES = [
    StepPipe(DP.eave_pipe(*TOWER_WALLS["front"][:2], PIPE_SPOTS[0][1], Z_EAVE, H_TAN,
                          EAVE_OV), PIPE_Z_JOG, PIPE_STEP),
    StepPipe(DP.eave_pipe(*TOWER_WALLS["back"][:2], PIPE_SPOTS[1][1], Z_EAVE, H_TAN,
                          EAVE_OV), PIPE_Z_JOG, PIPE_STEP),
    DP.eave_pipe(*ANNEX_WALLS["a_east"][:2], PIPE_SPOTS[2][1], Z_A_EAVE, A_TAN,
                 A_EAVE_OV),
]

# The wall ladder (scripts/roof_safety.py) up the back eave wall, west of
# the head room's windows, from the ground to a metre over the roof's edge.
LADDER_S = 6.00                 # along the back wall from its east end: x -2.20
BACK_EAVE = RS.Eave(*TOWER_WALLS["back"][:2], Z_EAVE, EAVE_OV, Z_EDGE, H_TAN)
LADDER = RS.WallLadder(BACK_EAVE, LADDER_S)
PAINT = RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)

# The ladder's safety cage, which scripts/roof_safety.py does not build: flat
# hoops round the climber's back from CAGE_FOOT to CAGE_TOP, fixed to the
# rails' outsides, and three vertical straps on the hoops' outsides. Across
# (a) and out (o) are the ladder's own: a along the wall from its axis, o
# from the wall face. A hoop leaves each rail, flares out to CAGE_R either
# side of the axis at CAGE_O, and rounds the back on CAGE_ARC chords.
CAGE_FOOT, CAGE_TOP = 2.50, 21.80
CAGE_PITCH = 1.65               # the most between two hoops
CAGE_O = LADDER.standoff + 0.28     # the hoops' arc centre, out from the wall
CAGE_R = 0.36
CAGE_ARC = 4
HOOP_T, HOOP_H = 0.016, 0.05    # flat bar: thickness, height
STRAP_T, STRAP_W = 0.020, 0.05
STRAP_ANGLES = (135.0, 90.0, 45.0)  # round the arc, 90 at the back
STRAP_END = 0.04                # past the first and last hoops
_n = int(math.ceil((CAGE_TOP - CAGE_FOOT) / CAGE_PITCH - 1e-9))
CAGE_HOOPS = [CAGE_FOOT + (CAGE_TOP - CAGE_FOOT) * k / _n for k in range(_n + 1)]
# per tier: which hoops (every n-th, the top one always), or None for the
# back strap alone, which sets the +Y extent every tier keeps
CAGE_MODES = (1, 2, 6, None)


def outline(kind, length):
    """The wall's outline as (s, z) corners, and how far its visible top
    stands below the outline's (the part run on into a roof slab)."""
    a = HX - TX
    if kind == "t_eave":                         # front and back: shaft and head room
        return [(a, Z_SH0), (length - a, Z_SH0), (length - a, Z_HEAD),
                (length, Z_HEAD), (length, Z_TOP), (0.0, Z_TOP), (0.0, Z_HEAD),
                (a, Z_HEAD)], 0.10
    if kind == "shaft":
        return [(0.0, Z_SH0), (length, Z_SH0), (length, Z_HEAD), (0.0, Z_HEAD)], 0.0
    if kind == "t_gable":
        return [(0.0, Z_HEAD), (length, Z_HEAD), (length, Z_TOP),
                (length / 2.0, Z_TOP + length / 2.0 * H_TAN), (0.0, Z_TOP)], 0.10
    if kind == "base":
        return [(0.0, 0.0), (length, 0.0), (length, Z_BASE), (0.0, Z_BASE)], 0.0
    if kind == "a_down":                         # high at s = 0, the shaft
        return [(0.0, 0.0), (length, 0.0), (length, Z_A_TOP), (0.0, Z_A_HIGH)], 0.10
    if kind == "a_up":                           # high at s = length
        return [(0.0, 0.0), (length, 0.0), (length, Z_A_HIGH), (0.0, Z_A_TOP)], 0.10
    if kind == "a_eave":
        return [(0.0, 0.0), (length, 0.0), (length, Z_A_TOP), (0.0, Z_A_TOP)], 0.10
    if kind == "a_high":
        return [(0.0, 0.0), (length, 0.0), (length, Z_A_HIGH), (0.0, Z_A_HIGH)], 0.10
    raise ValueError(kind)


def item_mode(kind, level):
    """How an opening is built at each tier.

    ring  - LOD0: the surround is a ring of faces on the wall, the opening
            inside it recessed with reveals and closed by its glass, leaf or
            louvre.
    cut   - LOD1: one recess the size of the surround, the surround painted.
    flush - LOD2/3: the surround rect as a flat quad in the wall.
    """
    return ("ring", "cut", "flush", "flush")[level]


# ============================================================== mesh builder
class Builder:
    """One closed solid under construction, with UVs set as faces are made.
    Vertices are shared through a position cache, so faces that meet along an
    edge meet on the same vertices."""

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cache = {}

    def v(self, co):
        key = (round(co[0], 4), round(co[1], 4), round(co[2], 4))
        vert = self.cache.get(key)
        if vert is None:
            vert = self.bm.verts.new(co)
            self.cache[key] = vert
        return vert

    def face(self, cos, uvfn):
        verts = []
        for co in cos:
            vv = self.v(co)
            if not verts or verts[-1] is not vv:
                verts.append(vv)
        if len(verts) > 2 and verts[0] is verts[-1]:
            verts.pop()
        if len(verts) < 3:
            return None
        o = verts[0].co
        pts = [(v.co.x - o.x, v.co.y - o.y, v.co.z - o.z) for v in verts]
        nx = ny = nz = 0.0
        for i in range(len(pts)):
            (ax, ay, az), (bx, by, bz) = pts[i], pts[(i + 1) % len(pts)]
            nx += ay * bz - az * by
            ny += az * bx - ax * bz
            nz += ax * by - ay * bx
        if nx * nx + ny * ny + nz * nz < 1e-18:
            return None
        try:
            f = self.bm.faces.new(verts)
        except ValueError:
            return None
        self.set_uv(f, uvfn)
        return f

    def set_uv(self, f, uvfn):
        for loop in f.loops:
            u, w = uvfn(loop.vert.co)
            loop[self.uv].uv = (u / L.ATLAS, w / L.ATLAS)


class Frame:
    """A wall plane: s runs along the wall from p0, z is world height, and
    depth runs inward, away from the outward normal."""

    def __init__(self, p0, p1):
        self.p0 = Vector((p0[0], p0[1], 0.0))
        d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
        self.L = d.length
        self.t = d / self.L
        self.n = Vector((self.t.y, -self.t.x, 0.0))

    def P(self, s, z, depth=0.0):
        q = self.p0 + self.t * s - self.n * depth
        return (q.x, q.y, z)

    def s_of(self, co):
        return (co.x - self.p0.x) * self.t.x + (co.y - self.p0.y) * self.t.y


# ------------------------------------------------------------ UV mappings
def uv_band(fr, y0, z_ref, u_off):
    return lambda co: ((fr.s_of(co) + u_off) * PPM, y0 + (co.z - z_ref) * PPM)


def uv_item(fr, kind, s_left, z_bot):
    x0, y0 = L.ITEM_ORIGIN[kind]
    return lambda co: (x0 + (fr.s_of(co) - s_left) * PPM, y0 + (co.z - z_bot) * PPM)


def uv_patch(name):
    x0, y0, w, h = L.PATCHES[name]
    c = (x0 + w / 2.0, y0 + h / 2.0)
    return lambda co: c


def wall_bands(fr, u_off):
    """(z_lo, z_hi, uv) for the band each height range of a wall samples:
    S1 from the ground to the first joint, then W2 per 4 m strip, each strip
    mapped from its own joint and shifted along U."""
    out = [(-1.0, L.JOINTS[0], uv_band(fr, L.S1_Y0, 0.0, u_off))]
    for k, zj in enumerate(L.JOINTS):
        hi = L.JOINTS[k + 1] if k + 1 < len(L.JOINTS) else zj + L.W2_P
        out.append((zj, hi, uv_band(fr, L.W2_Y0, zj, u_off + (k + 1) * STRIP_SHIFT)))
    return out


# ================================================================== walls
def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge (openings that
    share head and sill heights line up, and the triangulator then joins
    three collinear corners)."""
    tris = [list(t) for t in tris]

    def area2(t):
        (ax, ay), (bx, by), (cx, cy) = (pts[i] for i in t)
        return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

    for _ in range(4 * len(tris)):
        bad = next((i for i, t in enumerate(tris) if abs(area2(t)) < 1e-10), None)
        if bad is None:
            return tris
        t = tris[bad]
        pairs = [(t[0], t[1], t[2]), (t[1], t[2], t[0]), (t[2], t[0], t[1])]
        e0, e1, mid = max(pairs, key=lambda p: (pts[p[0]][0] - pts[p[1]][0]) ** 2 +
                          (pts[p[0]][1] - pts[p[1]][1]) ** 2)
        for j, u in enumerate(tris):
            if j == bad or e0 not in u or e1 not in u:
                continue
            k = next(k for k in range(3) if {u[k], u[(k + 1) % 3]} == {e0, e1})
            x, y, d = u[k], u[(k + 1) % 3], u[(k + 2) % 3]
            tris[bad], tris[j] = [x, mid, d], [mid, y, d]
            break
        else:
            raise ValueError("zero-area triangle with no neighbour to flip against")
    raise ValueError("sliver repair did not converge")


def fill_region(B, fr, outline_pts, holes, uvfn):
    """Triangulate a wall region with rectangular holes and add it."""
    loops = [outline_pts] + holes
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((s, z, 0.0)) for s, z in loop] for loop in loops])
    for a, b, c in _flip_slivers(flat, tris):
        B.face([fr.P(*flat[a]), fr.P(*flat[b]), fr.P(*flat[c])], uvfn)


def clip_z(poly, zlo, zhi):
    """A wall outline (s, z) clipped to zlo <= z <= zhi. The outlines here
    are convex or a T, which a horizontal slab cuts into one piece, so the
    half-plane clip is exact."""
    def clip(pts, inside, cut):
        out = []
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            if inside(p):
                out.append(p)
                if not inside(q):
                    out.append(cut(p, q))
            elif inside(q):
                out.append(cut(p, q))
        return out

    def at(z):
        def cut(p, q):
            t = (z - p[1]) / (q[1] - p[1])
            return (p[0] + t * (q[0] - p[0]), z)
        return cut

    pts = clip(poly, lambda p: p[1] >= zlo - EPS, at(zlo))
    if pts:
        pts = clip(pts, lambda p: p[1] <= zhi + EPS, at(zhi))
    out = []
    for p in pts:
        p = (round(p[0], 6), round(p[1], 6))
        if not out or abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-6 and abs(out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    return out


def notch(region, rect, zlo, zhi):
    """*region*, a strip zlo..zhi of a wall's outline (anticlockwise in s, z),
    with an opening *rect* (l, r, b, t) that crosses the strip's top or its
    bottom cut out of that edge: the strip's outline runs round it rather
    than holing it, so the strips either side of the joint meet the
    opening's jambs on the same vertices."""
    l, r, b, t = rect
    if t <= zlo + EPS or b >= zhi - EPS:
        return region
    top, bottom = t >= zhi - EPS, b <= zlo + EPS
    if top == bottom:
        raise ValueError("an opening inside or across a whole strip needs a hole")
    zc = zhi if top else zlo
    n = len(region)
    for i in range(n):
        p, q = region[i], region[(i + 1) % n]
        if abs(p[1] - zc) > EPS or abs(q[1] - zc) > EPS:
            continue
        if top and p[0] > r and q[0] < l:
            cut = [(r, zc), (r, b), (l, b), (l, zc)]
        elif bottom and p[0] < l and q[0] > r:
            cut = [(l, zc), (l, t), (r, t), (r, zc)]
        else:
            continue
        return region[:i + 1] + cut + region[i + 1:]
    raise ValueError("no strip edge at %.2f spans the opening" % zc)


def uv_bay(fr):
    x0, y0 = L.BAY_ORIGIN
    return lambda co: (x0 + (fr.s_of(co) - BAY_S0) * PPM, y0 + (co.z - BAY_Z0) * PPM)


def build_bay(B, fr, level):
    """The sheave bay's faces, its jambs carrying the joint's vertices: flush,
    one face painted with the sheaves; or open, a concrete reveal the wall's
    thickness deep, then dark sides, deck, head and back."""
    l, r, b, t = BAYS["front"]
    mids = [z for z in L.JOINTS if b + EPS < z < t - EPS]
    edges = [[(l, b), (r, b)], [(r, b)] + [(r, z) for z in mids] + [(r, t)],
             [(r, t), (l, t)], [(l, t)] + [(l, z) for z in reversed(mids)] + [(l, b)]]
    if bay_mode(level) == "flush":
        B.face([fr.P(*p) for e in edges for p in e[:-1]], uv_bay(fr))
        return
    rev, dark = uv_patch("reveal"), uv_patch("interior")
    for e in edges:
        (s0, z0), (s1, z1) = e[0], e[-1]
        B.face([fr.P(s, z) for s, z in e] +
               [fr.P(s1, z1, BAY_REVEAL), fr.P(s0, z0, BAY_REVEAL)], rev)
        B.face([fr.P(s0, z0, BAY_REVEAL), fr.P(s1, z1, BAY_REVEAL),
                fr.P(s1, z1, BAY_DEPTH), fr.P(s0, z0, BAY_DEPTH)], dark)
    B.face([fr.P(s, z, BAY_DEPTH) for s, z in ((l, b), (r, b), (r, t), (l, t))], dark)


def recess(B, fr, rect, depth, fn, rev):
    l, r, b, t = rect
    c = [(l, b), (r, b), (r, t), (l, t)]
    for k in range(4):
        (s0, z0), (s1, z1) = c[k], c[(k + 1) % 4]
        B.face([fr.P(s0, z0), fr.P(s1, z1), fr.P(s1, z1, depth), fr.P(s0, z0, depth)], rev)
    B.face([fr.P(s, z, depth) for s, z in c], fn)


def item_rects(kind, s, z):
    w, h, cs, cb, ct = L.OPENINGS[kind]
    outer = (s - w / 2 - cs, s + w / 2 + cs, z - cb, z + h + ct)
    inner = (s - w / 2, s + w / 2, z, z + h)
    return outer, inner


def build_item(B, fr, kind, s, z, level):
    """Faces for one opening; returns the hole it needs in its wall region."""
    mode = item_mode(kind, level)
    (ol, orr, ob, ot), (il, ir, ib, it) = item_rects(kind, s, z)
    fn = uv_item(fr, kind, ol, ob)
    depth = L.REVEAL_DEPTH[kind]
    rev = uv_patch("reveal")
    o = [(ol, ob), (orr, ob), (orr, ot), (ol, ot)]
    if mode == "flush":
        B.face([fr.P(*p) for p in o], fn)
        return o
    if mode == "cut":
        recess(B, fr, (ol, orr, ob, ot), depth, fn, rev)
        return o
    i = [(il, ib), (ir, ib), (ir, it), (il, it)]
    for k in range(4):
        B.face([fr.P(*o[k]), fr.P(*o[(k + 1) % 4]),
                fr.P(*i[(k + 1) % 4]), fr.P(*i[k])], fn)
    recess(B, fr, (il, ir, ib, it), depth, fn, rev)
    if abs(ob - ib) < EPS:
        # a door has no bottom surround: the hole carries the leaf's corners too
        return [(ol, ob), (il, ib), (ir, ib), (orr, ob), (orr, ot), (ol, ot)]
    return o


def build_wall(B, name, level):
    """One elevation: its outline cut into the bands its height crosses, each
    region holed for the openings inside it. Two walls meeting at a corner
    are cut at the same heights, so they meet on the same vertices."""
    p0, p1, kind, items = ALL_WALLS[name]
    fr = Frame(p0, p1)
    poly, _ = outline(kind, fr.L)
    rects = {(k, s, z): item_rects(k, s, z)[0] for k, s, z in items}
    bay = BAYS.get(name)
    placed = 0
    for zlo, zhi, fn in wall_bands(fr, U_OFF[name]):
        region = clip_z(poly, zlo, zhi)
        if len(region) < 3:
            continue
        if bay:
            region = notch(region, bay, zlo, zhi)
        its = [key for key, r in rects.items() if r[2] > zlo - EPS and r[3] < zhi + EPS]
        holes = [build_item(B, fr, k, s, z, level) for k, s, z in its]
        placed += len(its)
        fill_region(B, fr, region, holes, fn)
    if placed != len(rects):
        raise ValueError("an opening on %s straddles a joint" % name)
    if bay:
        build_bay(B, fr, level)


def close_solid(B, apexes=()):
    """Cap a wall ring with an n-gon floor and a lid, both buried (the floor
    in the base or the ground, the lid inside the roof slab); the solid must
    be closed for the boolean to be exact. The rim is walked in edge-index
    order, so the caps start on the same vertex every run. A gable lid is
    split at its ridge between *apexes*."""
    bm = B.bm
    bm.edges.index_update()
    order = [e for e in bm.edges if len(e.link_faces) == 1]
    rim = set(order)
    if any(sum(1 for e in v.link_edges if e in rim) != 2
           for e in order for v in e.verts):
        raise ValueError("the wall ring's rim branches: a T-junction somewhere")
    loops = []
    for first in order:
        if first not in rim:
            continue
        rim.discard(first)
        start, cur = first.verts
        loop = [start]
        while cur is not start:
            loop.append(cur)
            e = min((x for x in cur.link_edges if x in rim), key=lambda x: x.index)
            rim.discard(e)
            cur = e.other_vert(cur)
        loops.append(loop)
    if len(loops) != 2:
        raise ValueError("expected a floor and a lid, got %d holes" % len(loops))
    blank = uv_patch("blank")
    for loop in loops:
        B.set_uv(bm.faces.new(loop), blank)
    if apexes:
        a, b = (B.cache[(round(p[0], 4), round(p[1], 4), round(p[2], 4))] for p in apexes)
        bmesh.ops.connect_verts(bm, verts=[a, b])


def tower_body(level):
    """The shaft and the head room as one ring of walls. The front and back
    walls are a T: the shaft's width up to the head room, its full length
    above. Under each cantilever a soffit closes the step between the
    shaft's side wall and the head room's gable wall."""
    B = Builder()
    for name in TOWER_WALLS:
        build_wall(B, name, level)
    soffit = uv_patch("csoffit")
    for sx in (1.0, -1.0):
        B.face([(sx * TX, -TY, Z_HEAD), (sx * HX, -TY, Z_HEAD),
                (sx * HX, TY, Z_HEAD), (sx * TX, TY, Z_HEAD)], soffit)
    close_solid(B, [(HX, 0.0, Z_APEX), (-HX, 0.0, Z_APEX)])
    return B


def base_body(level):
    """The base: four walls to Z_BASE, a 45 degree sloped top running in and
    up into the shaft, and buried caps."""
    B = Builder()
    for name in BASE_WALLS:
        build_wall(B, name, level)
    r = BX - BASE_IN
    out = [(-BX, -BX), (BX, -BX), (BX, BX), (-BX, BX)]
    inn = [(-r, -r), (r, -r), (r, r), (-r, r)]
    k_slope = math.sqrt(2.0) * PPM
    for k in range(4):
        a, b = out[k], out[(k + 1) % 4]
        ai, bi = inn[k], inn[(k + 1) % 4]
        fr = Frame(a, b)
        name = list(BASE_WALLS)[k]

        def fn(co, fr=fr, u=U_OFF[name]):
            return ((fr.s_of(co) + u) * PPM, L.LEDGE_Y0 + (co.z - Z_BASE) * k_slope)
        B.face([(a[0], a[1], Z_BASE), (b[0], b[1], Z_BASE),
                (bi[0], bi[1], Z_BASE_TOP), (ai[0], ai[1], Z_BASE_TOP)], fn)
    blank = uv_patch("blank")
    B.face([(x, y, Z_BASE_TOP) for x, y in inn], blank)
    B.face([(x, y, 0.0) for x, y in reversed(out)], blank)
    return B


def annex_body(level):
    B = Builder()
    for name in ANNEX_WALLS:
        build_wall(B, name, level)
    close_solid(B)
    return B


# ================================================================== roofs
ROOF_RPM = L.ROOF_H / L.ROOF_SLOPE_LEN           # atlas px per metre up a slope


def slab(section, kinds, axis, a0, a1, slope_v):
    """A roof slab: a closed *section* (across, z) extruded along *axis*
    from a0 to a1. *kinds* names each section edge: slope, fascia, soffit or
    end (a barge). *slope_v(across)* is the distance up the slope from the
    eave edge, for the roof band's V."""
    B = Builder()

    def W(a, p, z):
        return (a, p, z) if axis == "x" else (p, a, z)

    def along(co):
        return co.x if axis == "x" else co.y

    def across(co):
        return co.y if axis == "x" else co.x

    def slope_uv(co):
        return ((along(co) + 16.0) * PPM, L.ROOF_Y0 + slope_v(across(co)) * ROOF_RPM)

    def fascia_uv(z_bot):
        return lambda co: ((along(co) + 16.0) * PPM, L.FASC_Y0 + (co.z - z_bot) * PPM)

    n = len(section)
    for k, kind in enumerate(kinds):
        (p0, z0), (p1, z1) = section[k], section[(k + 1) % n]
        if kind == "slope":
            fn = slope_uv
        elif kind == "fascia":
            fn = fascia_uv(min(z0, z1))
        elif kind == "soffit":
            fn = uv_patch("soffit")
        else:
            fn = uv_patch("barge")
        B.face([W(a0, p0, z0), W(a0, p1, z1), W(a1, p1, z1), W(a1, p0, z0)], fn)
    barge = uv_patch("barge")
    B.face([W(a0, p, z) for p, z in section], barge)
    B.face([W(a1, p, z) for p, z in reversed(section)], barge)
    return B


def head_roof():
    """A chevron across Y, ridge along X. Its underside meets the front and
    back walls at Z_EAVE; the part inside the walls is removed by the union,
    the rest is the soffit."""
    pe = TY + EAVE_OV
    z0 = Z_EAVE + ROOF_T + TY * H_TAN
    zt = z0 - pe * H_TAN
    sec = [(-pe, zt - ROOF_T), (-pe, zt), (0.0, z0), (pe, zt),
           (pe, zt - ROOF_T), (0.0, z0 - ROOF_T)]
    kinds = ("fascia", "slope", "slope", "fascia", "soffit", "soffit")
    slope_f = math.sqrt(1.0 + H_TAN * H_TAN)
    return slab(sec, kinds, "x", -HX - RAKE_OV, HX + RAKE_OV,
                lambda p: (pe - abs(p)) * slope_f)


def annex_roof():
    """The annex's mono-pitch slab, from inside the shaft out over the east
    eave. Its inner end is buried in the shaft; only the rakes' ends show,
    as barge."""
    xo = AX1 + A_EAVE_OV

    def under(x):
        return Z_A_EAVE + (AX1 - x) * A_TAN

    sec = [(AX0, under(AX0)), (AX0, under(AX0) + ROOF_T), (xo, under(xo) + ROOF_T),
           (xo, under(xo))]
    kinds = ("end", "slope", "fascia", "soffit")
    slope_f = math.sqrt(1.0 + A_TAN * A_TAN)
    return slab(sec, kinds, "y", -AY - A_RAKE_OV, AY + A_RAKE_OV,
                lambda x: (xo - x) * slope_f)


# ================================================================ sheaves
def bay_point(u, z, depth):
    """A bay-local point (facade_atlas: u from the west jamb, z from the
    sill) *depth* behind the front wall's face, in the build frame."""
    return (-HX + BAY_S0 + u, -TY + depth, BAY_Z0 + z)


def _prism(B, ring0, ring1, fn, caps=True):
    """Quads between two matching rings of points, and the two rings as caps."""
    n = len(ring0)
    for k in range(n):
        B.face([ring0[k], ring0[(k + 1) % n], ring1[(k + 1) % n], ring1[k]], fn)
    if caps:
        B.face(list(reversed(ring0)), fn)
        B.face(list(ring1), fn)
    return B


def _disc_ring(c, r, y, n, phase=0.5):
    return [(c[0] + r * math.cos(2.0 * math.pi * (k + phase) / n), y,
             c[2] + r * math.sin(2.0 * math.pi * (k + phase) / n)) for k in range(n)]


def sheave_disc(c, y0, y1, sides, side_uv):
    """A sheave as one closed disc: its rim's outside in the steel, its two
    faces mapped onto the painted sheave card, centred, so the spokes and
    the dark between them are texture."""
    x0, v0 = L.CARD_ORIGIN
    half = L.SHEAVE_R * L.CARD_PPM

    def card(co):
        return (x0 + half + (co.x - c[0]) * L.CARD_PPM, v0 + half + (co.z - c[2]) * L.CARD_PPM)
    B = Builder()
    r0, r1 = _disc_ring(c, L.SHEAVE_R, y0, sides), _disc_ring(c, L.SHEAVE_R, y1, sides)
    _prism(B, r0, r1, side_uv, caps=False)
    B.face(list(reversed(r0)), card)
    B.face(list(r1), card)
    return B


def sheave_solids(level):
    """Each sheave as closed solids for the union: the rim (an annulus), the
    hub, SPOKES spokes running into both, and the axle back into the bay's
    back; the rims' feet run below the deck, as a sheave's do. On LOD0 the
    ropes too: square strands from inside each rim's groove down into the
    deck and across to the east jamb, toward the rope opening."""
    kind, sides, hub_n, ropes = SHEAVE_MODES[level]
    steel = uv_patch("steel")
    out = []
    for (u, z), depth in zip(L.SHEAVES, SHEAVE_DEPTH):
        c = bay_point(u, z, depth)
        y0, y1 = c[1] - SHEAVE_W / 2.0, c[1] + SHEAVE_W / 2.0
        if kind == "disc":
            out.append(sheave_disc(c, y0, y1, sides, steel))
            continue
        B = Builder()
        o0, o1 = (_disc_ring(c, L.SHEAVE_R, y, sides) for y in (y0, y1))
        i0, i1 = (_disc_ring(c, L.SHEAVE_RI, y, sides) for y in (y0, y1))
        for k in range(sides):
            j = (k + 1) % sides
            B.face([o0[k], o0[j], o1[j], o1[k]], steel)
            B.face([i0[k], i1[k], i1[j], i0[j]], steel)
            B.face([i0[k], i0[j], o0[j], o0[k]], steel)
            B.face([i1[k], o1[k], o1[j], i1[j]], steel)
        out.append(B)
        out.append(_prism(Builder(), _disc_ring(c, L.HUB_R, c[1] - HUB_W / 2.0, hub_n),
                          _disc_ring(c, L.HUB_R, c[1] + HUB_W / 2.0, hub_n), steel))
        out.append(_prism(Builder(), _disc_ring(c, AXLE_R, c[1], hub_n),
                          _disc_ring(c, AXLE_R, -TY + BAY_DEPTH + 0.10, hub_n), steel))
        r0, r1 = L.HUB_R * 0.6, (L.SHEAVE_RI + L.SHEAVE_R) / 2.0
        for k in range(L.SPOKES):
            a = 2.0 * math.pi * k / L.SPOKES
            d = Vector((math.cos(a), 0.0, math.sin(a)))
            p = Vector((-math.sin(a), 0.0, math.cos(a))) * (L.SPOKE_W / 2.0)
            ty = Vector((0.0, SPOKE_T / 2.0, 0.0))
            ring = [p + ty, -p + ty, -p - ty, p - ty]
            out.append(_prism(Builder(), [tuple(Vector(c) + d * r0 + q) for q in ring],
                              [tuple(Vector(c) + d * r1 + q) for q in ring], steel))
    if ropes:
        rope = uv_patch("rope")
        h = L.ROPE_D / 2.0
        for (seg_drop, seg_lead), depth in zip(L.rope_lines(L.BAY_W + 0.10), SHEAVE_DEPTH):
            for (pa, pb) in (seg_drop, seg_lead):
                a = Vector(bay_point(pa[0], pa[1], depth))
                b = Vector(bay_point(pb[0], pb[1], depth))
                d = (b - a).normalized()
                s1 = Vector((0.0, h, 0.0))
                s2 = d.cross(Vector((0.0, 1.0, 0.0))).normalized() * h
                ring = [s1 + s2, -s1 + s2, -s1 - s2, s1 - s2]
                out.append(_prism(Builder(), [tuple(a + q) for q in ring],
                                  [tuple(b + q) for q in ring], rope))
    return out


# =================================================================== cage
def cage_point(a, o, z):
    return tuple(BACK_EAVE.point(LADDER_S + a, o, z))


def hoop_path():
    """A hoop's centre line in (a, o): from inside one rail, flaring out to
    the arc, round the back, and into the other rail."""
    rail_o = LADDER.standoff + RS.RAIL_D / 2.0
    a_in = RS.LADDER_W / 2.0 + RS.RAIL_W / 2.0 - 0.02      # 2 cm inside the rail
    arc = [(CAGE_R * math.cos(math.pi * (1.0 - k / CAGE_ARC)),
            CAGE_O + CAGE_R * math.sin(math.pi * (1.0 - k / CAGE_ARC)))
           for k in range(CAGE_ARC + 1)]
    return [(-a_in, rail_o)] + arc + [(a_in, rail_o)]


def hoop(z):
    """One flat-bar hoop at height *z*, swept along hoop_path() with mitred
    corners, its ends capped inside the rails."""
    pts = [Vector(p) for p in hoop_path()]
    segs = [(q - p).normalized() for p, q in zip(pts, pts[1:])]
    left = [Vector((-d.y, d.x)) for d in segs]
    offs = []
    for i in range(len(pts)):
        if i == 0 or i == len(pts) - 1:
            offs.append(left[0] if i == 0 else left[-1])
            continue
        m = (left[i - 1] + left[i]).normalized()
        offs.append(m / m.dot(left[i - 1]))
    t, h = HOOP_T / 2.0, HOOP_H / 2.0
    rings = [[cage_point(*(p + n * sa * t), z + sz * h)
              for sa, sz in ((1, -1), (-1, -1), (-1, 1), (1, 1))]
             for p, n in zip(pts, offs)]
    M = RS.Mesh(PAINT)
    for i, d in enumerate(segs):
        along = Vector(cage_point(*pts[i + 1], 0.0)) - Vector(cage_point(*pts[i], 0.0))
        for k in range(4):
            M.face([rings[i][k], rings[i][(k + 1) % 4], rings[i + 1][(k + 1) % 4],
                    rings[i + 1][k]], along)
    M.face(list(reversed(rings[0])), (0, 0, 1))
    M.face(list(rings[-1]), (0, 0, 1))
    return M


def strap(angle, tri=False):
    """A vertical strap on the hoops' outsides at *angle* round the arc;
    *tri*, a three-sided prism within it whose outer edge keeps its extent."""
    a = math.radians(angle)
    rad, tan = Vector((math.cos(a), math.sin(a))), Vector((-math.sin(a), math.cos(a)))
    c = Vector((0.0, CAGE_O)) + rad * CAGE_R
    w = STRAP_W / 2.0
    sec = [c + tan * w, c - tan * w, c - tan * w + rad * STRAP_T, c + tan * w + rad * STRAP_T]
    if tri:
        sec = [c + tan * w, c - tan * w, c + rad * STRAP_T]
    z0, z1 = CAGE_HOOPS[0] - STRAP_END, CAGE_HOOPS[-1] + STRAP_END
    return _prism(RS.Mesh(PAINT), [cage_point(*p, z0) for p in sec],
                  [cage_point(*p, z1) for p in sec], (0, 0, 1))


def cage_solids(level):
    """The cage's hoops and straps for the union, or (on a tier without
    hoops) the back strap alone, three-sided, for append()."""
    every = CAGE_MODES[level]
    if every is None:
        return [strap(90.0, tri=True)]
    zs = [z for k, z in enumerate(CAGE_HOOPS) if k % every == 0 or k == len(CAGE_HOOPS) - 1]
    return [hoop(z) for z in zs] + [strap(a) for a in STRAP_ANGLES]


# ================================================================ assembly
def build_lod(level):
    base = to_object(tower_body(level), "tmp_tower")
    parts = [
        to_object(base_body(level), "tmp_base"),
        to_object(annex_body(level), "tmp_annex"),
        to_object(head_roof(), "tmp_head_roof"),
        to_object(annex_roof(), "tmp_annex_roof"),
    ]
    # The stepped pipes' shoes set the front and back extents, and a
    # three-sided ring's corner stands out past the flats every other tier
    # shows there, so they keep four sides at LOD3.
    sides, bent = DP.MODES[level]
    parts += [to_object(B, "tmp_downpipe_t%d" % i) for i, (B, _n) in enumerate(
        DP.solids(DOWNPIPES[:2], max(sides, 4), bent, L.PIPE_STRIP, L.ATLAS))]
    parts += [to_object(B, "tmp_downpipe_a%d" % i) for i, (B, _n) in enumerate(
        DP.solids(DOWNPIPES[2:], sides, bent, L.PIPE_STRIP, L.ATLAS))]
    if RS.MODES[level][0] is not None:
        parts += [to_object(M, name) for M, name in RS.solids([LADDER], level, PAINT)]
        parts += [to_object(M, "tmp_cage%d" % i) for i, M in enumerate(cage_solids(level))]
    if bay_mode(level) == "recess":
        parts += [to_object(B, "tmp_sheave%d" % i) for i, B in enumerate(sheave_solids(level))]
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # coplanar boolean subdivisions, keeping UV seams and every real edge
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    if RS.MODES[level][0] is None:
        # the ladder sets the top and the cage's back strap the +Y extent:
        # the bare rails and that strap stay
        RS.append(obj, RS.solids([LADDER], level, PAINT, extents=True)
                  + [(M, "tmp_cage") for M in cage_solids(level)])
    return obj


def _inside(p, poly):
    inside = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > p[1]) != (b[1] > p[1]) and \
                p[0] < a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            inside = not inside
    return inside


def check_layout():
    """Assert what the numbers hide and a render would show: openings
    colliding, leaving their wall's visible outline (a corner, the roof, the
    cantilever's step), straddling a joint; the annex outgrowing its bands;
    the slopes disagreeing with the roof band; the pipes and the ladder
    crowding openings, corners or each other."""
    problems = []
    gap = 0.05
    for name, (p0, p1, kind, items) in ALL_WALLS.items():
        fr = Frame(p0, p1)
        poly, drop = outline(kind, fr.L)
        # the visible outline: the part run on into a slab is not wall
        vis = [(s, z - drop) if z > Z_HEAD + 0.5 or (kind.startswith("a_") and z > 0.0)
               else (s, z) for s, z in poly]
        rects = [(k, item_rects(k, s, z)[0]) for k, s, z in items]
        if name in BAYS:
            l, r, b, t = BAYS[name]
            if not all(_inside(c, vis) for c in ((l - gap, b - gap), (r + gap, b - gap),
                                                 (r + gap, t + gap), (l - gap, t + gap))):
                problems.append("%s: the sheave bay leaves the wall" % name)
            if any(l < s < r and b < z < t for s, z in vis):
                problems.append("%s: the sheave bay takes in a corner of the wall" % name)
            if b < Z_HEAD + 0.25:
                problems.append("%s: the sheave deck is within 0.25 m of the soffit" % name)
            rects.append(("sheave bay", BAYS[name]))
        for k, (l, r, b, t) in rects:
            if k == "sheave bay":
                continue
            corners = [(l - gap, b - gap), (r + gap, b - gap), (r + gap, t + gap),
                       (l - gap, t + gap)]
            if not all(_inside(c, vis) for c in corners):
                problems.append("%s: %s at s %.2f..%.2f z %.2f..%.2f leaves the wall"
                                % (name, k, l, r, b, t))
            if any(l < s < r and b < z < t for s, z in vis):
                problems.append("%s: %s takes in a corner of the wall" % (name, k))
            for zj in L.JOINTS:
                if b - gap < zj < t + gap:
                    problems.append("%s: %s crosses the joint at %.2f" % (name, k, zj))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b_ = rects[i][1], rects[j][1]
                if a[0] < b_[1] + gap and b_[0] < a[1] + gap and \
                        a[2] < b_[3] + gap and b_[2] < a[3] + gap:
                    problems.append("%s: %s and %s overlap" % (name, rects[i][0], rects[j][0]))
    if Z_A_HIGH > L.JOINTS[1] - 0.01:
        problems.append("the annex's walls (%.2f) outgrow the first W2 strip" % Z_A_HIGH)
    if A_RAKE_OV > TY - AY - 0.10:
        problems.append("the annex's rakes reach the shaft's face planes")
    if Z_APEX > L.JOINTS[-1] + L.W2_P:
        problems.append("the head room's apex is above the last W2 strip")
    if Z_HEAD in L.JOINTS:
        problems.append("the cantilevers' soffit sits on a joint")
    a_slope = (AX1 - TX + A_EAVE_OV) * math.sqrt(1.0 + A_TAN ** 2)
    if abs(a_slope - L.ROOF_SLOPE_LEN) > 1e-3:
        problems.append("annex slope is %.4f m, the atlas assumes %.4f"
                        % (a_slope, L.ROOF_SLOPE_LEN))
    if (TY + EAVE_OV) * math.sqrt(1.0 + H_TAN ** 2) > L.ROOF_SLOPE_LEN:
        problems.append("the head room's slope is longer than the roof band")
    if Z_A_HIGH + ROOF_T > Z_HEAD - 1.0:
        problems.append("the annex roof reaches the head room")
    # downpipes clear of their walls' ends and openings, and of the ladder;
    # the tower's two also clear of the shaft's corners below the head room
    lad = LADDER.span()
    for (w, s), pipe in zip(PIPE_SPOTS, DOWNPIPES):
        avoid = [(k,) + item_rects(k, s_, z)[0][:2] for k, s_, z in ALL_WALLS[w][3]]
        if w in BAYS:
            avoid.append(("sheave bay",) + BAYS[w][:2])
        if w == "back":
            avoid.append(("ladder",) + lad)
        if w in ("front", "back"):
            a = HX - TX
            if not a + DP.CORNER - 1e-6 <= s <= 2 * HX - a - DP.CORNER + 1e-6:
                problems.append("the %s downpipe is within %.2f m of the shaft's corner"
                                % (w, DP.CORNER))
        problems += DP.problems(pipe, "the %s downpipe" % w, avoid)
    # the ladder: clear of the back's openings at every height, the base's
    # included, of the downpipe, and of the shaft's corners
    # (the base's back wall starts HX - BX further along than the eave's)
    avoid = [(k,) + item_rects(k, s, z)[0][:2] for k, s, z in TOWER_WALLS["back"][3]]
    avoid += [(k,) + tuple(e + HX - BX for e in item_rects(k, s, z)[0][:2])
              for k, s, z in BASE_WALLS["b_back"][3]]
    pipe_s = PIPE_SPOTS[1][1]
    avoid.append(("back downpipe", pipe_s - DP.A, pipe_s + DP.A))
    problems += RS.problems(LADDER, "the wall ladder", avoid)
    s0, s1 = LADDER.span()
    if s0 < HX - TX + RS.CORNER or s1 > HX + TX - RS.CORNER:
        problems.append("the wall ladder is within %.2f m of the shaft's corner" % RS.CORNER)
    # the cage: as wide as its hoops, clear of the same corners and openings
    half = CAGE_R + HOOP_T
    c0, c1 = LADDER_S - half, LADDER_S + half
    if c0 < HX - TX + RS.CORNER or c1 > HX + TX - RS.CORNER:
        problems.append("the ladder's cage is within %.2f m of the shaft's corner" % RS.CORNER)
    for what, a0, a1 in avoid:
        if a0 - RS.CLEAR < c1 and c0 < a1 + RS.CLEAR:
            problems.append("the ladder's cage crowds the %s" % what)
    if min(o for _a, o in hoop_path()) < BACK_EAVE.eave_out + 0.10:
        problems.append("the cage's hoops reach the back eave")
    if CAGE_HOOPS[-1] + HOOP_H > LADDER.foot + LADDER.length:
        problems.append("the cage's top hoop is above the ladder")
    # the sheaves: inside the bay with their feet below the deck, clear of
    # each other, and their ropes leaving by the east gable's rope opening
    R, gap = L.SHEAVE_R, 0.10
    for (u, z), d in zip(L.SHEAVES, SHEAVE_DEPTH):
        if u - R < gap or u + R > L.BAY_W - gap or z + R > L.BAY_H - gap:
            problems.append("a sheave at u %.2f leaves the sheave bay" % u)
        if not z - L.SHEAVE_RI > 0.0 > z - R:
            problems.append("a sheave at u %.2f does not stand in the deck" % u)
        if d - SHEAVE_W / 2.0 < BAY_REVEAL or d + HUB_W / 2.0 > BAY_DEPTH - gap:
            problems.append("a sheave at u %.2f leaves the bay's depth" % u)
    (ua, _za), (ub, _zb) = L.SHEAVES[:2]
    if abs(SHEAVE_DEPTH[0] - SHEAVE_DEPTH[1]) < HUB_W + 0.10 and abs(ua - ub) < 2 * R + gap:
        problems.append("the sheaves collide")
    k, s_rope, z_rope = next(i for i in TOWER_WALLS["e_head"][3] if i[0] == "rope")
    w, h = L.OPENINGS[k][:2]
    for (_drop, (_pa, pb)), d in zip(L.rope_lines(2.0 * HX - BAY_S0), SHEAVE_DEPTH):
        sr, zr = d, BAY_Z0 + pb[1]          # the gable's s runs from the front corner
        if not (s_rope - w / 2.0 + L.ROPE_D < sr < s_rope + w / 2.0 - L.ROPE_D
                and z_rope + L.ROPE_D < zr < z_rope + h - L.ROPE_D):
            problems.append("a rope meets the east gable at s %.2f z %.2f, outside "
                            "the rope opening" % (sr, zr))
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the base and the annex's wall
    outline; the head room's cantilevers, the overhangs, the downpipes'
    feet and the wall ladder stand outside it. The one storey is the ground
    floor of the tower base and the annex: the shaft and the head room above
    it are machinery space, not occupied storeys."""
    def door(door_id, kind, name, item, main=False):
        p0, p1, _kind, items = ALL_WALLS[name]
        s, z = next((s, z) for k, s, z in items if k == item)
        w, h = L.OPENINGS[item][:2]
        return model_facts.wall_door(door_id, kind, p0, p1, s, z, w, h, main)

    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-BX, -BX), (BX, -BX), (BX, -AY), (AX1, -AY), (AX1, AY),
                      (BX, AY), (BX, BX), (-BX, BX)],
        "storeys": [(L.Z_FLOOR, (2 * BX) ** 2 + (AX1 - BX) * 2 * AY)],
        "doors": [door("tower", "entrance", "b_front", "door", main=True),
                  door("collar", "vehicle", "a_front", "door_vehicle")],
    }


if __name__ == "__main__":
    BUILD.main(build_all, facts)
