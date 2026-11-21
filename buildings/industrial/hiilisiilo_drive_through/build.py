# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of hiilisiilo_drive_through, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, renders preview.png and variants.png, and
writes the facts sidecar:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite coal screening and truck-loading bunker of a small mid-century
Nordic mine. A 12.0 x 8.0 m bunker house stands on concrete legs over one
drive-through truck lane, which runs straight through it from the front long
side to the rear: 5.00 m clear between its concrete side walls and 5.20 m to
its ceiling, from which three steel hoppers hang to 4.60 m. West of the lane
is a 1.60 m concrete leg; east of it, under the bunker, the control and
stair room with the operators' steel door. Over the lane, a concrete ring
beam carries the screen house: a concrete frame clad in profiled sheet to a
1:10 mono-pitch roof falling to the rear, 13.1 m at its front fascia, a row
of small steel windows at the screen floor. East of it, on the side the
catalog camera sees, a 2.0 x 2.0 m conveyor gallery rises at 30 degrees from
a low concrete intake hopper house into the screen house's east wall, clear
of the lane and both of its approaches, carried at mid-span on a steel
trestle.

Construction is a set of closed solids unioned with Blender's exact boolean
(asset_build.union): the bunker house, the roof slab, the gallery, the intake
house's walls and roof slab, the trestle's legs, cross-head, bracing and
footings, three hoppers and two downpipes. The bunker
house is one closed solid of genus one: a box with the lane as a tunnel
through it, its front and rear walls U-shaped round the lane's mouths, the
lane's two side walls and ceiling ordinary outside surface. The lane has no
floor face: the ground is its floor, so the shell's bottom is the two floor
caps under the leg and the control room, nothing between them.

The walls are textured as a trim sheet (facade_atlas.py): concrete to the top
of the ring beam at 6.40 m, then profiled sheet in 2.00 m strips that all map
onto the same rows, split by the concrete frame's columns at the corners and
over the lane's side walls.
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
importlib.reload(L)       # an interactive session must not keep a stale layout

ASSET = L.ASSET
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import downpipes as DP  # noqa: E402
import model_facts  # noqa: E402
from asset_build import to_object, union  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT)
PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

HX, HY = L.HX, L.HY
XL0, XL1 = L.XL0, L.XL1
Z_DECK, Z_CLAD = L.Z_DECK, L.Z_CLAD
STRIPS = list(zip(L.JOINTS[:-1], L.JOINTS[1:]))
CW = L.COL_W


def house_top(x, y):
    """The bunker house's wall ring lid: WALL_INTO up into the roof slab."""
    return L.z_under(y) + L.WALL_INTO


def intake_top(x, y):
    return L.INT_TOP


# ---------------------------------------------------------------- elevations
# Each wall runs counter-clockwise seen from above, outward face on its right;
# s runs along it from p0. lane: the s span of the lane's mouth. cols: the s
# spans of the concrete frame's columns above the ring beam. items: (kind, s
# at the centre, z of the sill or threshold). u_off: metres into the bands.
DOOR_S = 1.90 + HX          # the control room's door, x 1.90
WALLS = [
    dict(name="front", p0=(-HX, -HY), p1=(HX, -HY), lane=(XL0 + HX, XL1 + HX),
         cols=[(0.0, CW), (XL0 + HX - CW, XL0 + HX), (XL1 + HX, XL1 + HX + CW),
               (2 * HX - CW, 2 * HX)],
         items=[("door", DOOR_S, 0.0), ("win", 4.30 + HX, L.Z_WIN_LOW),
                ("win", L.LANE_C + HX, L.Z_WIN), ("win", 3.30 + HX, L.Z_WIN)],
         u_off=0.0),
    dict(name="east", p0=(HX, -HY), p1=(HX, HY), lane=None,
         cols=[(0.0, CW), (2 * HY - CW, 2 * HY)],
         items=[("win", 3.00, L.Z_WIN_LOW), ("win", 3.00, L.Z_WIN)], u_off=3.1),
    dict(name="rear", p0=(HX, HY), p1=(-HX, HY), lane=(HX - XL1, HX - XL0),
         cols=[(0.0, CW), (HX - XL1 - CW, HX - XL1), (HX - XL0, HX - XL0 + CW),
               (2 * HX - CW, 2 * HX)],
         items=[("win", HX - L.LANE_C, L.Z_WIN)], u_off=1.7),
    dict(name="west", p0=(-HX, HY), p1=(-HX, -HY), lane=None,
         cols=[(0.0, CW), (2 * HY - CW, 2 * HY)],
         items=[("win", 4.00, L.Z_WIN)], u_off=0.9),
]
(IX0, IX1), (IY0, IY1) = L.INT_X, L.INT_Y
INTAKE_WALLS = [
    dict(name="int_front", p0=(IX0, IY0), p1=(IX1, IY0), lane=None, cols=[],
         items=[("door_v", (IX1 - IX0) / 2.0, 0.0)], u_off=4.0),
    dict(name="int_east", p0=(IX1, IY0), p1=(IX1, IY1), lane=None, cols=[],
         items=[], u_off=7.0),
    dict(name="int_rear", p0=(IX1, IY1), p1=(IX0, IY1), lane=None, cols=[],
         items=[], u_off=9.8),
    dict(name="int_west", p0=(IX0, IY1), p1=(IX0, IY0), lane=None, cols=[],
         items=[], u_off=12.8),
]


def item_mode(kind, level):
    """How an opening is built at each tier.

    ring  - LOD0: the casing is a ring of faces on the wall, the opening
            inside it recessed with reveals and closed by its glass or leaf.
    cut   - LOD1: one recess the size of the casing, the casing painted on it.
    flush - LOD2/3: the casing rect as a flat quad in the wall.
    """
    return ("ring", "cut", "flush", "flush")[level]


def keeps_hoppers(level):
    """The hoppers say "loading lane" from any height that sees under the
    bunker; they cost about 18 triangles each. Dropped at LOD3 they left a
    visible step in the lintel's dark underside at the 120 m switch, so
    every tier keeps them."""
    return True


# ----------------------------------------------------------------- downpipes
# The roof falls to the rear, so the rear eave carries the gutter, and a
# downpipe stands at each end of the rear wall, DP.CORNER in from the
# corners: on the control room's back wall and on the west leg's. The rear
# wall's middle is the lane's mouth, so nothing hangs there.
_REAR = WALLS[2]
DOWNPIPE_S = (DP.CORNER, 2 * HX - DP.CORNER)
DOWNPIPES = [DP.eave_pipe(_REAR["p0"], _REAR["p1"], s, L.Z_EAVE_R, L.TAN, L.REAR_OV)
             for s in DOWNPIPE_S]


# ============================================================== mesh builder
class Builder:
    """One closed solid under construction, with UVs set as faces are made.
    Vertices are shared through a position cache, so faces that meet along an
    edge meet on the same vertices; region outlines carry their neighbours'
    breakpoints explicitly so every edge has a vertex at each of its ends."""

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

    def xy(self, s):
        q = self.p0 + self.t * s
        return q.x, q.y

    def s_of(self, co):
        return (co.x - self.p0.x) * self.t.x + (co.y - self.p0.y) * self.t.y


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.
def uv_s1(fr, u_off):
    return lambda co: ((fr.s_of(co) + u_off) * PPM, L.S1_Y0 + co.z * PPM)


def uv_clad(fr, a, z0, u_off):
    """A cladding panel from s = a, in the strip from z0: U from the panel's
    start (C is not full width), V from the strip's foot."""
    return lambda co: (8.0 + (fr.s_of(co) - a + u_off) * PPM,
                       L.C_Y0 + (co.z - z0) * PPM)


def uv_col(fr, a, z0):
    x0 = L.COL[0]
    return lambda co: (x0 + (fr.s_of(co) - a) * PPM, L.C_Y0 + (co.z - z0) * PPM)


def uv_item(fr, kind, s_left, z_bot):
    x0, y0 = L.ITEM_ORIGIN[kind]
    return lambda co: (x0 + (fr.s_of(co) - s_left) * PPM, y0 + (co.z - z_bot) * PPM)


def uv_patch(name):
    x0, y0, w, h = L.PATCHES[name]
    c = (x0 + w / 2.0, y0 + h / 2.0)
    return lambda co: c


def uv_lane_side(co):
    """Both of the lane's side walls: U along the lane from its front mouth,
    V up from the ground, at LPM; the occlusion is symmetric about the
    lane's middle, so one region serves both."""
    x0, y0 = L.LANE_SIDE[:2]
    return (x0 + (co.y + HY) * L.LPM, y0 + co.z * L.LPM)


def uv_lane_ceil(co):
    x0, y0 = L.LANE_CEIL[:2]
    return (x0 + (co.x - XL0) * L.LPM, y0 + (co.y + HY) * L.LPM)


def uv_roof(co):
    """Profiled sheet: U along x, V up the slope from the low (rear) edge."""
    return ((co.x + 16.0) * PPM,
            L.ROOF_Y0 + (L.Y_REAR - co.y) * L.SLOPE_F * L.ROOF_RPM)


def uv_eave(co):
    return ((co.x + 16.0) * PPM,
            L.EAVE_ROOF_Y0 + (L.Y_REAR - co.y) * L.SLOPE_F * L.EAVE_RPM)


def uv_fascia_x(co):
    return ((co.x + 16.0) * PPM, L.FASC_Y0 + (co.z - L.z_under(co.y)) * PPM)


def uv_fascia_rear(co):
    return ((co.x + 16.0) * PPM, L.FASC_R_Y0 + (co.z - L.z_under(co.y)) * PPM)


def uv_fascia_y(co):
    return ((co.y + 16.0) * PPM, L.FASC_Y0 + (co.z - L.z_under(co.y)) * PPM)


# ================================================================== walls
def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge: collinear
    corners in a region's outline (the column breakpoints along the ring
    beam's top) let the triangulator make triangles of no area."""
    tris = [list(t) for t in tris]

    def area2(t):
        (ax, ay), (bx, by), (cx, cy) = (pts[i] for i in t)
        return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

    for _ in range(4 * len(tris) + 8):
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


def fill_region(B, fr, outline, holes, uvfn):
    """Triangulate a wall region (s, z) with rectangular holes and add it."""
    loops = [outline] + holes
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((s, z, 0.0)) for s, z in loop] for loop in loops])
    for a, b, c in _flip_slivers(flat, tris):
        B.face([fr.P(*flat[a]), fr.P(*flat[b]), fr.P(*flat[c])], uvfn)


def clip_below(poly, top):
    """A convex (s, z) polygon clipped to z <= top(s), top linear in s."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = p[1] - top(p[0]), q[1] - top(q[0])
        if fp <= EPS:
            out.append(p)
        if (fp < -EPS and fq > EPS) or (fp > EPS and fq < -EPS):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    res = []
    for p in out:
        p = (round(p[0], 6), round(p[1], 6))
        if not res or abs(p[0] - res[-1][0]) > 1e-6 or abs(p[1] - res[-1][1]) > 1e-6:
            res.append(p)
    if len(res) > 1 and abs(res[0][0] - res[-1][0]) < 1e-6 and abs(res[0][1] - res[-1][1]) < 1e-6:
        res.pop()
    return res


def recess(B, fr, rect, depth, fn, rev, floor=True):
    """Push a rectangle *depth* back from the wall and close it. An opening
    that stands on the ground gets no floor of its own (floor=False): the
    strip it would lay at z = 0 would sit on the floor cap, and left out, the
    rim detours round the recess and the cap covers it."""
    l, r, b, t = rect
    c = [(l, b), (r, b), (r, t), (l, t)]
    for k in range(4):
        if k == 0 and not floor:
            continue
        (s0, z0), (s1, z1) = c[k], c[(k + 1) % 4]
        B.face([fr.P(s0, z0), fr.P(s1, z1), fr.P(s1, z1, depth), fr.P(s0, z0, depth)], rev)
    B.face([fr.P(s, z, depth) for s, z in c], fn)


def item_rects(kind, s, z):
    w, h, cs, cb, ct = L.OPENINGS[kind]
    outer = (s - w / 2 - cs, s + w / 2 + cs, z - cb, z + h + ct)
    inner = (s - w / 2, s + w / 2, z, z + h)
    return outer, inner


def build_item(B, fr, kind, s, z, level):
    """Faces for one opening. A door on the ground returns the notch it cuts
    in its region's bottom edge, left to right; a window returns its hole."""
    mode = item_mode(kind, level)
    (ol, orr, ob, ot), (il, ir, ib, it) = item_rects(kind, s, z)
    fn = uv_item(fr, kind, ol, ob)
    depth = L.REVEAL_DEPTH[kind]
    rev = uv_patch("reveal")
    on_ground = z < EPS
    o = [(ol, ob), (orr, ob), (orr, ot), (ol, ot)]
    hole = [(ol, ob), (ol, ot), (orr, ot), (orr, ob)] if on_ground else o
    if mode == "flush":
        B.face([fr.P(*p) for p in o], fn)
        return hole
    if mode == "cut":
        recess(B, fr, (ol, orr, ob, ot), depth, fn, rev, floor=not on_ground)
        return hole
    i = [(il, ib), (ir, ib), (ir, it), (il, it)]
    for k in range(4):          # a door's bottom quad has no area and is skipped
        B.face([fr.P(*o[k]), fr.P(*o[(k + 1) % 4]),
                fr.P(*i[(k + 1) % 4]), fr.P(*i[k])], fn)
    recess(B, fr, (il, ir, ib, it), depth, fn, rev, floor=not on_ground)
    return hole


def partition(spec, length):
    """The wall's s breakpoints above the ring beam: (a, b, is_column)."""
    edges = sorted({0.0, length} | {e for c in spec["cols"] for e in c})
    cols = {(round(a, 6), round(b, 6)) for a, b in spec["cols"]}
    return [(a, b, (round(a, 6), round(b, 6)) in cols) for a, b in zip(edges, edges[1:])]


def build_wall(B, spec, level, top_at):
    """One wall: the concrete region from the ground to Z_CLAD (or to the
    wall's top, if lower), notched by the lane's mouth and any door, holed by
    any low window; then, above Z_CLAD, one region per cladding strip and
    column or panel, clipped to the wall's top, holed by its windows.

    Every wall carries vertices at z = 0, Z_CLAD and each strip joint at both
    ends, so walls meeting at a corner meet on exactly the same vertices."""
    fr = Frame(spec["p0"], spec["p1"])
    Lw = fr.L

    def top(s):
        return top_at(*fr.xy(s))

    parts = partition(spec, Lw)
    s1_top = min(Z_CLAD, top(0.0), top(Lw))
    notches, holes1, upper = [], [], []
    for kind, s, z in spec["items"]:
        (l, r, b, t), _ = item_rects(kind, s, z)
        if z < EPS:
            notches.append((l, build_item(B, fr, kind, s, z, level)))
        elif t < s1_top:
            holes1.append(build_item(B, fr, kind, s, z, level))
        else:
            upper.append((kind, s, z))
    if spec["lane"] is not None:
        a, b = spec["lane"]
        notches.append((a, [(a, 0.0), (a, Z_DECK), (b, Z_DECK), (b, 0.0)]))
    outline = [(0.0, 0.0)]
    for _, pts in sorted(notches, key=lambda n: n[0]):
        outline += pts
    outline.append((Lw, 0.0))
    if s1_top < Z_CLAD - EPS:                       # the intake: no strips over it
        outline += [(Lw, top(Lw)), (0.0, top(0.0))]
    else:
        outline += [(Lw, Z_CLAD)] + [(a, Z_CLAD) for a, _, _ in reversed(parts[1:])] \
            + [(0.0, Z_CLAD)]
    fill_region(B, fr, outline, holes1, uv_s1(fr, spec["u_off"]))
    if s1_top < Z_CLAD - EPS:
        return

    placed = 0
    for z0, z1 in STRIPS:
        for a, b, is_col in parts:
            poly = clip_below([(a, z0), (b, z0), (b, z1), (a, z1)], top)
            if len(poly) < 3:
                continue
            holes = []
            if not is_col:
                for kind, s, z in upper:
                    (l, r, bb, t), _ = item_rects(kind, s, z)
                    if a < l and r < b and z0 < bb and t < z1:
                        holes.append(build_item(B, fr, kind, s, z, level))
                        placed += 1
            fn = uv_col(fr, a, z0) if is_col else uv_clad(fr, a, z0, spec["u_off"])
            fill_region(B, fr, poly, holes, fn)
    if placed != len(upper):
        raise ValueError("%s: a window straddles a strip joint or a column" % spec["name"])


def close_solid(B, n_loops):
    """Cap every open rim with an n-gon: the floors on the ground and the lid
    inside the roof slab, all buried or underneath, but the solid must be
    closed for the boolean. The rims are walked in edge-index order, so the
    caps start on the same vertex every run."""
    bm = B.bm
    bm.edges.index_update()
    order = [e for e in bm.edges if len(e.link_faces) == 1]
    rim = set(order)
    if any(sum(1 for e in v.link_edges if e in rim) != 2
           for e in order for v in e.verts):
        raise ValueError("a rim branches: a T-junction somewhere")
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
    if len(loops) != n_loops:
        raise ValueError("expected %d rims, got %d: a T-junction somewhere"
                         % (n_loops, len(loops)))
    blank = uv_patch("blank")
    for loop in loops:
        B.set_uv(bm.faces.new(loop), blank)


def house_body(level):
    """The bunker house: four walls, the lane's two side walls and its
    ceiling, two floor caps and the lid."""
    B = Builder()
    for spec in WALLS:
        build_wall(B, spec, level, house_top)
    for x in (XL0, XL1):
        B.face([(x, -HY, 0.0), (x, HY, 0.0), (x, HY, Z_DECK), (x, -HY, Z_DECK)],
               uv_lane_side)
    B.face([(XL0, -HY, Z_DECK), (XL1, -HY, Z_DECK), (XL1, HY, Z_DECK),
            (XL0, HY, Z_DECK)], uv_lane_ceil)
    close_solid(B, 3)
    return B


def intake_body(level):
    B = Builder()
    for spec in INTAKE_WALLS:
        build_wall(B, spec, level, intake_top)
    close_solid(B, 2)
    return B


# ================================================================== roof
def roof_slab():
    """The mono-pitch roof as one closed slab, ROOF_T thick vertically, over
    the bunker house. Its underside is one face, the soffit; the part over
    the walls is inside the house and the union removes it. Its top is two
    strips across y: the roof's lowest EAVE_STRIP_LEN, with the snow guard,
    maps onto the rear eave band, the rest onto ROOF. The rake edges carry
    that breakpoint."""
    B = Builder()
    xr = HX + L.RAKE_OV
    y0, y1 = L.Y_FRONT, L.Y_REAR
    t = L.ROOF_T
    zu = L.z_under
    B.face([(-xr, y0, zu(y0)), (-xr, y1, zu(y1)), (xr, y1, zu(y1)), (xr, y0, zu(y0))],
           uv_patch("soffit"))
    ys = y1 - L.EAVE_STRIP_LEN / L.SLOPE_F
    B.face([(-xr, y0, zu(y0) + t), (xr, y0, zu(y0) + t), (xr, ys, zu(ys) + t),
            (-xr, ys, zu(ys) + t)], uv_roof)
    B.face([(-xr, ys, zu(ys) + t), (xr, ys, zu(ys) + t), (xr, y1, zu(y1) + t),
            (-xr, y1, zu(y1) + t)], uv_eave)
    B.face([(-xr, y0, zu(y0)), (xr, y0, zu(y0)), (xr, y0, zu(y0) + t),
            (-xr, y0, zu(y0) + t)], uv_fascia_x)
    B.face([(xr, y1, zu(y1)), (-xr, y1, zu(y1)), (-xr, y1, zu(y1) + t),
            (xr, y1, zu(y1) + t)], uv_fascia_rear)
    for x, ya, yb in ((-xr, y1, y0), (xr, y0, y1)):
        B.face([(x, ya, zu(ya)), (x, yb, zu(yb)), (x, yb, zu(yb) + t),
                (x, ys, zu(ys) + t), (x, ya, zu(ya) + t)], uv_fascia_y)
    return B


def box(x0, x1, y0, y1, z0, z1, side, top, bottom):
    B = Builder()
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for k in range(4):
        (ax, ay), (bx, by) = ring[k], ring[(k + 1) % 4]
        B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], side)
    B.face([(x, y, z1) for x, y in ring], top)
    B.face([(x, y, z0) for x, y in reversed(ring)], bottom)
    return B


def uv_int_roof(co):
    """The intake roof's felt, planar from the slab's south-west corner."""
    x0, y0 = L.INT_ROOF[:2]
    return (x0 + (co.x - (IX0 - L.INT_OV)) * L.LPM, y0 + (co.y - (IY0 - L.INT_OV)) * L.LPM)


def intake_slab():
    """The intake house's flat concrete roof, overhanging its walls by
    INT_OV: a coping edge, a coal-dusted felt top, a concrete soffit."""
    o = L.INT_OV
    z0, z1 = L.INT_SLAB
    return box(IX0 - o, IX1 + o, IY0 - o, IY1 + o, z0, z1, uv_patch("coping"),
               uv_int_roof, uv_patch("slab_under"))


# ============================================================== the gallery
def gallery():
    """The conveyor gallery: a 2.0 x 2.0 m box whose axis runs along X and
    falls at GAL_DEG from inside the screen house's east wall to inside the
    intake house. Its sides take the cladding band with U along the axis and
    V square to it, so the sheets' ribs stand square to the gallery as they
    are fixed; its top takes the roof band up the slope from its lower end;
    its floor a dark steel patch. Both ends are buried except the lower
    end's top, which stands up out of the intake's roof and takes the
    cladding."""
    B = Builder()
    (x0, x1), (y0, y1) = L.GAL_X, L.GAL_Y
    hv = L.GAL_H / L.GAL_COS
    b0, b1 = L.gal_bottom(x0), L.gal_bottom(x1)

    def t_of(co):
        return (co.x - x0) / L.GAL_COS

    def side(co):
        d = (co.z - L.gal_bottom(co.x)) * L.GAL_COS
        return (8.0 + (t_of(co) + 1.0) * PPM, L.C_Y0 + d * PPM)

    def top(co):
        return ((co.y + 16.0) * PPM, L.ROOF_Y0 + (L.GAL_LEN - t_of(co)) * L.ROOF_RPM)

    def end(co):
        return (8.0 + (co.y - y0) * PPM, L.C_Y0 + (co.z - b1) / hv * L.C_H)

    B.face([(x0, y0, b0), (x1, y0, b1), (x1, y0, b1 + hv), (x0, y0, b0 + hv)], side)
    B.face([(x1, y1, b1), (x0, y1, b0), (x0, y1, b0 + hv), (x1, y1, b1 + hv)], side)
    B.face([(x0, y0, b0 + hv), (x1, y0, b1 + hv), (x1, y1, b1 + hv), (x0, y1, b0 + hv)], top)
    B.face([(x0, y0, b0), (x0, y1, b0), (x1, y1, b1), (x1, y0, b1)], uv_patch("gal_under"))
    B.face([(x0, y0, b0), (x0, y0, b0 + hv), (x0, y1, b0 + hv), (x0, y1, b0)],
           uv_patch("blank"))
    B.face([(x1, y1, b1), (x1, y1, b1 + hv), (x1, y0, b1 + hv), (x1, y0, b1)], end)
    return B


# ============================================================= the trestle
def trestle_mode(level):
    """How the trestle under the gallery's span is built at each tier.

    full   - LOD0/1: H-section legs on concrete pad footings, an H-section
             cross-head, the X of two bars.
    portal - LOD2/3: the legs and the cross-head as one plain solid, an
             upturned U of the legs' plan width standing on the ground; no
             footings. As separate boxes the leg tops' holes in the head
             cost LOD3 its last triangles under the ceiling.
    """
    return ("full", "full", "portal", "portal")[level]


def keeps_bracing(level):
    """The X reads as two faint lines at the 70 m switch, so LOD2 keeps it
    for about 30 triangles; LOD3 cannot afford it under its ceiling, and at
    120 m its bars are under a pixel."""
    return level <= 2


def _normal(cos):
    nx = ny = nz = 0.0
    for i in range(len(cos)):
        (ax, ay, az), (bx, by, bz) = cos[i], cos[(i + 1) % len(cos)]
        nx += ay * bz - az * by
        ny += az * bx - ax * bz
        nz += ax * by - ay * bx
    return nx, ny, nz


def steel_face(B, cos):
    """One face of the trestle's steel on the TRESTLE region: V is height
    from the ground; U runs along Y, or along X on a face square to Y."""
    nx, ny, _ = _normal(cos)
    x0, y0 = L.TRESTLE[:2]
    if abs(nx) >= abs(ny):
        fn = lambda co: (x0 + (co.y - L.TR_U0) * L.TPM, y0 + co.z * L.TPM)   # noqa: E731
    else:
        fn = lambda co: (x0 + (co.x - L.TR_UX0) * L.TPM, y0 + co.z * L.TPM)  # noqa: E731
    B.face(cos, fn)


def prism(profile, place, t0, t1):
    """A closed prism of the trestle's steel: the 2D *profile* swept from t0
    to t1, place(p, t) giving the 3D point."""
    B = Builder()
    n = len(profile)
    for k in range(n):
        p, q = profile[k], profile[(k + 1) % n]
        steel_face(B, [place(p, t0), place(q, t0), place(q, t1), place(p, t1)])
    steel_face(B, [place(p, t0) for p in reversed(profile)])
    steel_face(B, [place(p, t1) for p in profile])
    return B


def h_profile(a0, a1, b0, b1, tf, tw):
    """An H in (a, b): flanges tf thick at a0 and a1, each spanning b0..b1;
    the web, tw thick, along a at b's middle."""
    m0, m1 = (b0 + b1 - tw) / 2.0, (b0 + b1 + tw) / 2.0
    return [(a0, b0), (a0 + tf, b0), (a0 + tf, m0), (a1 - tf, m0), (a1 - tf, b0),
            (a1, b0), (a1, b1), (a1 - tf, b1), (a1 - tf, m1), (a0 + tf, m1),
            (a0 + tf, b1), (a0, b1)]


def pad_uv(z_top=None):
    """A footing on S1's foot: U round its sides, V the height, or one row
    at z_top for its top."""
    def fn(co):
        return ((co.x + co.y + 3.0) * PPM, L.S1_Y0 + (co.z if z_top is None else z_top) * PPM)
    return fn


def portal(x0, x1, y0, y1, w, zb):
    """The bent at LOD2/3 as one closed solid: an upturned U in (y, z), legs
    *w* wide in Y from the ground to the head, the head from zb to the
    cross-head's top, swept along X from x0 to x1. The top follows the
    gallery's floor, so the U's outline differs at its two ends."""
    top = L.tr_head_top

    def u_at(x):
        return [(x, y0, 0.0), (x, y0 + w, 0.0), (x, y0 + w, zb), (x, y1 - w, zb),
                (x, y1 - w, 0.0), (x, y1, 0.0), (x, y1, top(x)), (x, y0, top(x))]
    B = Builder()
    a, b = u_at(x0), u_at(x1)
    n = len(a)
    for k in range(n):
        steel_face(B, [a[k], b[k], b[(k + 1) % n], a[(k + 1) % n]])
    steel_face(B, a)
    steel_face(B, list(reversed(b)))
    return B


def trestle(level):
    """The bent under the gallery's span, as closed solids for the union:
    two legs, the cross-head under the gallery's floor, at the full tiers
    two footings, and through LOD2 the X of two bars. The cross-head's top
    follows the gallery's floor TR_BURY up into it; its bottom is level at
    TR_HEAD_ZB, and the legs stop half-way up its bottom flange. Beyond the
    gallery's sides its top flange stands TR_BURY proud of the floor, a
    bearing seat."""
    xc, s, hw = L.TR_X, L.TR_LEG / 2.0, L.TR_HEAD_W / 2.0
    zb, top = L.TR_HEAD_ZB, L.tr_head_top
    solids = bracing(level, xc, zb)
    if trestle_mode(level) == "portal":
        return solids + [(portal(xc - s, xc + s, L.TR_LEG_Y[0] - s, L.TR_LEG_Y[1] + s,
                                 s, zb), "tmp_tr_portal")]
    (hy0, hy1) = L.TR_HEAD_Y
    # cross-head: an H turned on its side, a profile in (x, z) swept along Y:
    # flanges along X at the bottom (level) and the top (sloped), the web
    # upright between them
    xs = (xc - hw, xc + hw)
    tf, tw = L.TR_HEAD_TF, L.TR_HEAD_TW
    prof = [(xs[0], zb), (xs[1], zb), (xs[1], zb + tf), (xc + tw / 2, zb + tf),
            (xc + tw / 2, top(xc + tw / 2) - tf), (xs[1], top(xs[1]) - tf),
            (xs[1], top(xs[1])), (xs[0], top(xs[0])), (xs[0], top(xs[0]) - tf),
            (xc - tw / 2, top(xc - tw / 2) - tf), (xc - tw / 2, zb + tf),
            (xs[0], zb + tf)]
    solids.append((prism(prof, lambda p, t: (p[0], t, p[1]), hy0, hy1), "tmp_tr_head"))
    # legs: in plan, flanges square to X, the web along X at the leg's centre,
    # from inside their footings to half-way up the head's bottom flange
    for i, yc in enumerate(L.TR_LEG_Y):
        prof = h_profile(xc - s, xc + s, yc - s, yc + s, L.TR_LEG_TF, L.TR_LEG_TW)
        solids.append((prism(prof, lambda p, t: (p[0], p[1], t),
                             L.TR_PAD[1] - L.TR_PAD_INTO, zb + tf / 2.0), "tmp_tr_leg%d" % i))
        p = L.TR_PAD[0] / 2.0
        solids.append((box(xc - p, xc + p, yc - p, yc + p, 0.0, L.TR_PAD[1],
                           pad_uv(), pad_uv(L.TR_PAD[1]), uv_patch("blank")),
                       "tmp_tr_pad%d" % i))
    return solids


def bracing(level, xc, zb):
    """The X: each bar ends cut along the plane y of a leg's centre, inside
    its web (or the portal's solid leg), one bar each side of the bent's
    centre plane so the two never touch."""
    if not keeps_bracing(level):
        return []
    solids = []
    ya, yb = L.TR_LEG_Y
    z0, z1 = L.TR_BRACE_LO, zb - L.TR_BRACE_TOP
    t = L.TR_BRACE
    hv = t * math.hypot(yb - ya, z1 - z0) / (yb - ya)
    for i, ((y0, za), (y1, zz), side) in enumerate((((ya, z0), (yb, z1), -1),
                                                     ((ya, z1), (yb, z0), 1))):
        x0 = xc + side * 0.005
        x1 = xc + side * (0.005 + t)
        prof = [(min(x0, x1), -hv / 2), (max(x0, x1), -hv / 2),
                (max(x0, x1), hv / 2), (min(x0, x1), hv / 2)]

        def place(p, u, y0=y0, y1=y1, za=za, zz=zz):
            f = (u - y0) / (y1 - y0)
            return (p[0], u, za + (zz - za) * f + p[1])
        solids.append((prism(prof, place, y0, y1), "tmp_tr_brace%d" % i))
    return solids


# ================================================================ hoppers
def hopper(yc):
    """One loading hopper under the bunker: a frustum from HOP_BURY inside
    the lane's ceiling down to its mouth at Z_HOP. Each side maps onto the
    chute region, its top edge along the region's top; the mouth is coal."""
    B = Builder()
    xc = L.LANE_C
    (tx, ty), (bx, by) = L.HOP_TOP, L.HOP_BOT
    zt, zb = Z_DECK + L.HOP_BURY, L.Z_HOP
    top = [(xc - tx / 2, yc - ty / 2), (xc + tx / 2, yc - ty / 2),
           (xc + tx / 2, yc + ty / 2), (xc - tx / 2, yc + ty / 2)]
    bot = [(xc - bx / 2, yc - by / 2), (xc + bx / 2, yc - by / 2),
           (xc + bx / 2, yc + by / 2), (xc - bx / 2, yc + by / 2)]
    cx0, cy0, cw, ch = L.CHUTE
    for k in range(4):
        j = (k + 1) % 4
        d = Vector((top[j][0] - top[k][0], top[j][1] - top[k][1])).normalized()
        half = abs(Vector((top[j][0] - top[k][0], top[j][1] - top[k][1])).length) / 2.0

        def fn(co, d=d, half=half):
            along = (co.x - xc) * d.x + (co.y - yc) * d.y
            return (cx0 + cw / 2.0 + along / half * (cw / 2.0),
                    cy0 + (co.z - zb) / (zt - zb) * ch)
        B.face([top[k] + (zt,), bot[k] + (zb,), bot[j] + (zb,), top[j] + (zt,)], fn)
    B.face([p + (zt,) for p in top], uv_patch("blank"))
    B.face([p + (zb,) for p in reversed(bot)], uv_patch("coal"))
    return B


# ================================================================ assembly
def build_lod(level):
    base = to_object(house_body(level), "tmp_house")
    parts = [to_object(roof_slab(), "tmp_roof"),
             to_object(gallery(), "tmp_gallery"),
             to_object(intake_body(level), "tmp_intake"),
             to_object(intake_slab(), "tmp_intake_slab")]
    if keeps_hoppers(level):
        parts += [to_object(hopper(y), "tmp_hopper%d" % i) for i, y in enumerate(L.HOP_Y)]
    parts += [to_object(B, name) for B, name in trestle(level)]
    parts += [to_object(B, name) for B, name in
              DP.solids(DOWNPIPES, *DP.MODES[level], L.PIPE_STRIP, L.ATLAS)]
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
    # Triangulated here by the beauty method, so the exporter never joins
    # collinear rim vertices into triangles of no area.
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY',
                          ngon_method='BEAUTY')
    flat = [f for f in bm.faces if f.calc_area() < 1e-8]
    if flat:
        raise ValueError("LOD%d keeps %d zero-area triangles, e.g. at %s"
                         % (level, len(flat), tuple(flat[0].calc_center_median())))
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def check_layout():
    """Assert what the numbers hide and a render would show: openings
    straddling a joint, a column or the roof; the lane narrower or lower than
    the brief's truck; the gallery missing the intake or fouling a downpipe;
    the trestle near the lane or off its gallery; the bands overrunning the
    atlas."""
    problems = []
    gap = 0.05
    for spec in WALLS + INTAKE_WALLS:
        fr = Frame(spec["p0"], spec["p1"])
        top_at = house_top if spec in WALLS else intake_top
        rects = []
        for kind, s, z in spec["items"]:
            (l, r, b, t), _ = item_rects(kind, s, z)
            rects.append((kind, l, r, b, t))
            if l < gap or r > fr.L - gap:
                problems.append("%s: %s runs off the wall" % (spec["name"], kind))
            for e in (l, r):
                if t > top_at(*fr.xy(e)) - L.WALL_INTO - 0.15:
                    problems.append("%s: %s top %.2f is under the roof" % (spec["name"], kind, t))
            if spec["lane"] is not None:
                a, bb = spec["lane"]
                if b < Z_DECK + gap and l < bb + gap and a - gap < r:
                    problems.append("%s: %s is in the lane's mouth" % (spec["name"], kind))
            if b > Z_CLAD - gap:
                for z0, _z1 in STRIPS:
                    if b - gap < z0 < t + gap:
                        problems.append("%s: %s crosses the joint at %.2f"
                                        % (spec["name"], kind, z0))
                for a, bb in spec["cols"]:
                    if l < bb + gap and a - gap < r:
                        problems.append("%s: %s runs into a column" % (spec["name"], kind))
            elif t > Z_CLAD - 0.30:
                problems.append("%s: %s reaches the ring beam" % (spec["name"], kind))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b_ = rects[i], rects[j]
                if a[1] < b_[2] + gap and b_[1] < a[2] + gap and \
                        a[3] < b_[4] + gap and b_[3] < a[4] + gap:
                    problems.append("%s: %s and %s overlap" % (spec["name"], a[0], b_[0]))
    # the lane: the brief's truck is 3.5 m wide and 4.0 m high; the lane is
    # to be at least 4.5 m both ways, under the hoppers' mouths too
    if XL1 - XL0 < 4.5:
        problems.append("the lane is %.2f m wide, under 4.5" % (XL1 - XL0))
    if L.Z_HOP < 4.5:
        problems.append("the hoppers' mouths leave %.2f m clear, under 4.5" % L.Z_HOP)
    hx, hy = L.HOP_TOP
    if abs(L.LANE_C - (XL0 + XL1) / 2) > EPS or hx > XL1 - XL0 - 1.0:
        problems.append("the hoppers are not centred clear of the lane's walls")
    if max(L.HOP_Y) + hy / 2 > HY - 0.6 or min(L.HOP_Y) - hy / 2 < -HY + 0.6:
        problems.append("a hopper reaches the lane's mouth")
    # the roof
    slope = (L.Y_REAR - L.Y_FRONT) * L.SLOPE_F
    if slope > L.ROOF_LEN or L.GAL_LEN > L.ROOF_LEN:
        problems.append("a slope is longer than the roof band's %.2f m" % L.ROOF_LEN)
    if L.WALL_INTO >= L.ROOF_T:
        problems.append("the wall ring's lid is above the roof slab")
    if L.TAN > 1.0 / 8.0:
        problems.append("the roof is steeper than 1:8: roof safety kit rules apply")
    # the gallery: its upper end buried in the house's east wall above the
    # ring beam and below the roof, its floor crossing the intake's roof
    # inside the slab's plan, its lower end inside the intake under the slab
    (gx0, gx1), (gy0, gy1) = L.GAL_X, L.GAL_Y
    hv = L.GAL_H / L.GAL_COS
    roof_low = min(L.z_under(gy0), L.z_under(gy1))
    if not (gx0 < HX - 0.2 and L.gal_bottom(HX) > Z_CLAD + 0.5
            and L.gal_bottom(gx0) + hv < roof_low - 1.0):
        problems.append("the gallery's upper end is not buried in the screen house")
    xc = HX + (L.Z_SCREEN - L.INT_SLAB[1]) / L.GAL_TAN
    if not IX0 - L.INT_OV + 0.3 < xc < IX1 - 0.5:
        problems.append("the gallery's floor meets the intake's roof at x %.2f" % xc)
    if not (IX0 + 0.5 < gx1 < IX1 - 0.1 and 0.3 < L.gal_bottom(gx1) < L.INT_SLAB[0] - 0.3):
        problems.append("the gallery's lower end is not inside the intake house")
    if not (IY0 + 0.3 < gy0 and gy1 < IY1 - 0.3):
        problems.append("the gallery is not inside the intake's walls in y")
    if not (-HY + CW + 0.1 < gy0 and gy1 < HY - CW - 0.1):
        problems.append("the gallery's mouth crowds a corner column")
    # its mouth in the east wall clear of that wall's windows
    east = WALLS[1]
    ga, gb = gy0 + HY, gy1 + HY
    gz0, gz1 = L.gal_bottom(HX), L.gal_bottom(HX) + hv
    for kind, s, z in east["items"]:
        (l, r, b, t), _ = item_rects(kind, s, z)
        if l < gb + 0.3 and ga - 0.3 < r and b < gz1 + 0.3 and gz0 - 0.3 < t:
            problems.append("east: %s crowds the gallery's mouth" % kind)
    # the lane and its approaches: a straight corridor x XL0 .. XL1 for every
    # y; the gallery, the intake and its slab stand east of the house
    if min(gx0, IX0 - L.INT_OV) < XL1 + 1.5:
        problems.append("the gallery or the intake reaches within 1.5 m of the lane's line")
    if gx0 < HX - 0.6 or IX0 - L.INT_OV < HX + 1.0:
        problems.append("the gallery or the intake is not east of the house")
    # the trestle: its footings 1.5 m or more off the lane's line too, in the
    # open between the house and the intake's slab, clear of the intake
    # door's approach; its legs outside the gallery's sides, its cross-head
    # across the whole width under the floor, the legs and bars inside it
    p, s, hw = L.TR_PAD[0] / 2.0, L.TR_LEG / 2.0, L.TR_HEAD_W / 2.0
    tx0, tx1 = L.TR_X - max(p, hw), L.TR_X + max(p, hw)
    (ly0, ly1), (hy0, hy1) = L.TR_LEG_Y, L.TR_HEAD_Y
    if tx0 < XL1 + 1.5:
        problems.append("the trestle reaches within 1.5 m of the lane's line")
    if not (HX + 1.0 < tx0 and tx1 < IX0 - L.INT_OV - 1.0):
        problems.append("the trestle is not in the open between the house and the intake")
    (dl, dr, _b, _t), _ = item_rects("door_v", *INTAKE_WALLS[0]["items"][0][1:])
    if tx1 > IX0 + dl - 1.0:
        problems.append("the trestle crowds the intake door's approach")
    if not (ly0 + s < gy0 - 0.03 and gy1 + 0.03 < ly1 - s):
        problems.append("a trestle leg is under the gallery, not beside it")
    if not (hy0 < ly0 - s - 0.01 and ly1 + s + 0.01 < hy1 and hy0 < gy0 and gy1 < hy1):
        problems.append("the cross-head does not span the legs and the gallery")
    zb = L.TR_HEAD_ZB
    if not (L.TR_HEAD_D - 0.05 < L.gal_bottom(L.TR_X + hw) - zb
            and L.TR_BURY + 0.005 < L.TR_HEAD_TF):
        problems.append("the cross-head's top flange is not just under the gallery's floor")
    if zb - L.TR_BRACE_TOP < L.TR_BRACE_LO + 2.0 or L.TR_BRACE_LO < L.TR_PAD[1] + 0.3:
        problems.append("the trestle's bracing does not fit between its feet and head")
    if s - L.TR_LEG_TF < 0.075 + 0.003:
        problems.append("the bracing bars do not fit between the legs' flanges")
    if (hy1 - L.TR_U0) * L.TPM > L.TRESTLE[2] - 1 or \
            L.tr_head_top(L.TR_X - hw) * L.TPM > L.TRESTLE[3] - 1:
        problems.append("the trestle runs off its atlas region")
    # downpipes: clear of the lane's mouth, which passes through the rear wall
    avoid = [("lane", HX - XL1, HX - XL0)]
    for pipe in DOWNPIPES:
        problems += DP.problems(pipe, "the rear downpipe at s %.2f" % pipe.s, avoid)
    # atlas: the cladding's U stays inside C, the snow guard inside its strip
    for spec in WALLS:
        for a, b, is_col in partition(spec, Frame(spec["p0"], spec["p1"]).L):
            if not is_col and 8.0 + (b - a + spec["u_off"]) * PPM > L.C_W - 2:
                problems.append("%s: a panel runs off the cladding band" % spec["name"])
    if 8.0 + (L.GAL_LEN + 1.0) * PPM > L.C_W - 2:
        problems.append("the gallery's sides run off the cladding band")
    if not 0.0 < L.SNOW_S < L.EAVE_STRIP_LEN - 5.0 / L.EAVE_RPM:
        problems.append("the snow guard is not inside the eave strip")
    if L.EAVE_ROOF_Y0 + L.EAVE_STRIP_LEN * L.EAVE_RPM > L.ATLAS:
        problems.append("the eave strip runs off the atlas")
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame.

    The footprint is the ground outline of the bunker house's legs and walls
    with the lane inside it (the 12.0 x 8.0 m rectangle), the intake house
    east of it, and between them the strip under the gallery, the gallery's
    own width, which joins the two into one simple polygon. The one storey
    is the two ground-level rooms, the control and stair room east of the
    lane and the intake house, inside walls 0.30 and 0.25 m thick. The lane
    is open and the bunker and screen house above it are plant, so neither
    counts; the west leg is a solid concrete pier. The lane's mouths have no
    door leaf and are not doors.

    The lane is the one passage, stated from the front mouth trucks enter
    by: its centre on the front wall's plane, running +Y to the rear mouth
    2 * HY on, XL1 - XL0 between its side walls, open at the far end. Its
    clear height is the hoppers' mouths at Z_HOP, the lowest geometry over
    the lane (check_layout() keeps them clear of its walls and mouths), or
    the ceiling at Z_DECK on a tier without them."""
    walls = {spec["name"]: spec for spec in WALLS + INTAKE_WALLS}

    def door(door_id, kind, wall, main=False):
        spec = walls[wall]
        k, s, z = next(i for i in spec["items"] if i[0].startswith("door"))
        w, h = L.OPENINGS[k][:2]
        return model_facts.wall_door(door_id, kind, spec["p0"], spec["p1"], s, z,
                                     w, h, main)

    (gy0, gy1) = L.GAL_Y
    control = (HX - XL1 - 2 * 0.30) * (2 * HY - 2 * 0.30)
    intake = (IX1 - IX0 - 2 * 0.25) * (IY1 - IY0 - 2 * 0.25)
    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-HX, -HY), (HX, -HY), (HX, gy0), (IX0, gy0), (IX0, IY0),
                      (IX1, IY0), (IX1, IY1), (IX0, IY1), (IX0, gy1), (HX, gy1),
                      (HX, HY), (-HX, HY)],
        "storeys": [(0.0, control + intake)],
        "doors": [door("control", "entrance", "front", main=True),
                  door("intake", "vehicle", "int_front")],
        "passages": [model_facts.lane_passage(
            "truck_lane", (L.LANE_C, -HY), (0.0, 1.0), XL1 - XL0, 2 * HY,
            min(L.Z_HOP, Z_DECK) if keeps_hoppers(0) else Z_DECK, through=True)],
    }


if __name__ == "__main__":
    BUILD.main(build_all, facts)
