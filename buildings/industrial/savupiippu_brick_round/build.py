# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of savupiippu_brick_round, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the material and previews read it.

The free-standing chimney stack of a small mid-century Nordic coal-fired
heat and power plant: a round, battered shaft of radial brick, 4.1 m across
at its foot and 2.4 m at its top, straight to a pale cast concrete head band
under a steel cap ring, open at the top round a flue sunk 1 m and sooted.
It stands on a massive brick base, 6.8 m square on a concrete footing,
turned to an octagon by sloping brick fillets at its corners and to the
round by a concrete wash. A closed flue inlet, toward the boiler house, is
in the base's front (-Y), a cast iron cleanout hatch low in its east wall.
A steel service platform rings the head 1.5 m under the rim, with a
railing; an iron ladder climbs the back (+Y) along the batter from 2.5 m
above the base to the platform; three obstruction lamps sit on the head
band, their lenses the emission map's only lit regions.

The stack is one closed solid built directly: the base's walls (the inlet
cut into the front at LOD0/1), the trapezoids and fillets above them, the
octagon's coping, the wash holed by the shaft's foot, and a surface of
revolution for the shaft, the head band, the rim and the flue's lining,
closed by the flue's floor. The platform, ladder and lamps are closed
solids unioned into it (asset_build.union).

Every number the mesh and the atlas share is imported from facade_atlas.py.
"""

import importlib
import math
import os
import sys

import bmesh
from mathutils import Vector, geometry


HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import facade_atlas as L  # noqa: E402  (layout constants shared with the atlas)
importlib.reload(L)       # an interactive session must not keep a stale layout

ASSET = L.ASSET
EXPORT_DIR = os.path.join(HERE, "export")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
from asset_build import to_object, union  # noqa: E402

asset_build.check_toolchain()

PPM = L.PPM
LEVELS = (0, 1, 2, 3)


BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT)
get_material, export_all = BUILD.material, BUILD.export_all
_show_only, preview_studio = BUILD.show_only, BUILD.preview_studio
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants


# ----------------------------------------------------------------- tiers
def sides(level):
    """24 sides to 35 m, 16 to 70, 12 to 120, 8 beyond: the polygon's
    sagitta is under three pixels at each switch (notes.md, LOD review)."""
    return L.SIDES[level]


def inlet_mode(level):
    """The inlet's 0.25 m recess through LOD1; painted flush after, where it
    is under two pixels deep."""
    return "cut" if level < 2 else "flush"


def ladder_mode(level):
    """The modelled ladder through LOD1; after that the painted line on the
    back facet (notes.md, LOD review)."""
    return "solid" if level < 2 else "paint"


# What of the platform each tier keeps: the deck is the head's silhouette,
# kept on every tier; the hand rail, posts and brackets through LOD2; the
# knee rail through LOD1.
PLATFORM = ({"deck", "rail", "knee", "posts", "struts"},
            {"deck", "rail", "knee", "posts", "struts"},
            {"deck", "rail", "posts", "struts"},
            {"deck"})


# ============================================================== mesh builder
class Builder:
    """One closed solid, with UVs given per face corner. Vertices are shared
    through a position cache, so faces meet on the same vertices."""

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cache = {}

    def v(self, co):
        key = (round(co[0], 5), round(co[1], 5), round(co[2], 5))
        vert = self.cache.get(key)
        if vert is None:
            vert = self.bm.verts.new(co)
            self.cache[key] = vert
        return vert

    def face(self, cos, uvs, smooth=False):
        verts = [self.v(co) for co in cos]
        if len(set(verts)) != len(verts):
            raise ValueError("degenerate face at %s" % (tuple(cos[0]),))
        f = self.bm.faces.new(verts)
        for loop, (u, w) in zip(f.loops, uvs):
            loop[self.uv].uv = (u / L.ATLAS, w / L.ATLAS)
        f.smooth = smooth
        return f


class Frame:
    """A wall plane: s along the wall from p0, z world height, out along the
    outward normal (on the right of p0 -> p1, walking counter-clockwise)."""

    def __init__(self, p0, p1):
        self.p0 = Vector((p0[0], p0[1], 0.0))
        d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
        self.L = d.length
        self.t = d / self.L
        self.n = Vector((self.t.y, -self.t.x, 0.0))

    def P(self, s, z, out=0.0):
        q = self.p0 + self.t * s + self.n * out
        return (q.x, q.y, z)


BH = L.BH
WALLS = {
    "front": ((-BH, -BH), (BH, -BH)),
    "east": ((BH, -BH), (BH, BH)),
    "rear": ((BH, BH), (-BH, BH)),
    "west": ((-BH, BH), (-BH, -BH)),
}
# the octagon's corners, counter-clockwise from the front's west end
A = L.OCT_A
OCTAGON = [(-A, -BH), (A, -BH), (BH, -A), (BH, A), (A, BH), (-A, BH), (-BH, A), (-BH, -A)]


def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge (see
    nostokonehuone_brick/build.py)."""
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


def fill_planar(B, outline, holes, to3d, uvfn, smooth=False):
    """Triangulate a planar region given in 2D (an outline and holes) and add
    it; *to3d* lifts a 2D point, *uvfn* gives the 3D point's UV."""
    loops = [outline] + list(holes)
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((a, b, 0.0)) for a, b in loop] for loop in loops])
    for i, j, k in _flip_slivers(flat, tris):
        cos = [to3d(*flat[n]) for n in (i, j, k)]
        B.face(cos, [uvfn(co) for co in cos], smooth)


def uv_patch(name):
    x, y, w, h = L.PATCHES[name]
    return lambda co: (x + w / 2.0, y + h / 2.0)


# ================================================================== the base
def uv_wall(fr, wall, shift=0.0):
    """The base band: U along the wall from its range's start, V height,
    *shift* metres lower (the trapezoids and fillets)."""
    u0 = L.U_OFF[wall]

    def f(co):
        s = (Vector(co) - fr.p0).dot(fr.t)
        return ((u0 + s) * PPM, L.PL_Y0 + (co[2] - shift) * PPM)
    return f


def uv_region(fr, rect, s0, z0):
    x, y, w, h = rect

    def f(co):
        s = (Vector(co) - fr.p0).dot(fr.t)
        return (x + (s - s0) * PPM, y + (co[2] - z0) * PPM)
    return f


def opening(B, fr, wall, spec, rect_px, recess):
    """A rectangle in a base wall: cut with brick reveals, a concrete sill
    and lintel soffit and its closing plane *recess* deep, or painted flush.
    Returns its outline in (s, z), a hole in the wall."""
    sc, z0, w, h = spec
    s0, s1, z1 = sc - w / 2.0, sc + w / 2.0, z0 + h
    poly = [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]
    closing = uv_region(fr, rect_px, s0, z0)
    if not recess:
        cos = [fr.P(s, z) for s, z in poly]
        B.face(cos, [closing(c) for c in cos])
        return poly
    for k, ((a0, b0), (a1, b1)) in enumerate(zip(poly, poly[1:] + poly[:1])):
        cos = [fr.P(a0, b0), fr.P(a1, b1), fr.P(a1, b1, -recess), fr.P(a0, b0, -recess)]
        if k in (0, 2):
            fn = uv_patch("conc")              # the sill, the lintel's soffit
        else:
            # a jamb: the brick that would have been as far along the wall,
            # so the coursing turns into the reveal
            sign = -1.0 if k == 1 else 1.0

            def fn(co, sign=sign):
                q = Vector(co) - fr.p0
                s, d = q.dot(fr.t), -q.dot(fr.n)
                return ((L.U_OFF[wall] + s + sign * d) * PPM, L.PL_Y0 + co[2] * PPM)
        B.face(cos, [fn(c) for c in cos])
    cos = [fr.P(s, z, -recess) for s, z in poly]
    B.face(cos, [closing(c) for c in cos])
    return poly


def ray_octagon(theta):
    """Where a ray from the axis at angle *theta* leaves the octagon."""
    c, s = abs(math.cos(theta)), abs(math.sin(theta))
    t = min(BH / c if c > 1e-12 else 1e9, BH / s if s > 1e-12 else 1e9,
            (BH + A) / (c + s))
    return (t * math.cos(theta), t * math.sin(theta))


def vertex_angles(n):
    return [math.pi / 2 - math.pi / n + 2 * math.pi * j / n for j in range(n)]


def outer_loop(n):
    """The octagon's top edge as the wash meets it: a point where each ray
    to a shaft vertex leaves it, and its eight corners, counter-clockwise.
    Returns [(x, y, corner index or None)] and, per shaft vertex, its point's
    index in the loop."""
    corners = [(math.atan2(y, x) % (2 * math.pi), k) for k, (x, y) in enumerate(OCTAGON)]
    th = vertex_angles(n)
    loop, ray_idx = [], []
    for j in range(n):
        a0 = th[j] % (2 * math.pi)
        hit = next((k for ang, k in corners
                    if abs((ang - a0 + math.pi) % (2 * math.pi) - math.pi) < 1e-9), None)
        ray_idx.append(len(loop))
        if hit is not None:
            loop.append(OCTAGON[hit] + (hit,))
        else:
            loop.append(ray_octagon(th[j]) + (None,))
        span = (2 * math.pi / n)
        inside = sorted(((ang - a0) % (2 * math.pi), k) for ang, k in corners
                        if 1e-9 < (ang - a0) % (2 * math.pi) < span - 1e-9)
        for _d, k in inside:
            loop.append(OCTAGON[k] + (k,))
    return loop, ray_idx


def base(B, level, foot):
    """Walls, trapezoids, corner fillets, the octagon's coping, the wash
    round the shaft's foot ring *foot*, and the floor."""
    n = sides(level)
    for wall, (p0, p1) in WALLS.items():
        fr = Frame(p0, p1)
        holes = []
        if wall == "front":
            depth = L.INLET_REVEAL if inlet_mode(level) == "cut" else 0.0
            holes.append(opening(B, fr, wall, L.INLET, L.INLET_R, depth))
        if wall == "east":
            holes.append(opening(B, fr, wall, L.HATCH, L.HATCH_R, 0.0))
        outline = [(0.0, 0.0), (fr.L, 0.0), (fr.L, L.Z_SQ), (0.0, L.Z_SQ)]
        fill_planar(B, outline, holes, fr.P, uv_wall(fr, wall))
        # the wall runs on up as a trapezoid between the corner fillets; it
        # samples range A, lower, where the brick is plain
        cos = [fr.P(0.0, L.Z_SQ), fr.P(fr.L, L.Z_SQ), fr.P(BH + A, L.Z_OCT),
               fr.P(BH - A, L.Z_OCT)]
        f = uv_wall(fr, "east", L.FILLET_SHIFT)
        B.face(cos, [f(c) for c in cos])
    # the fillets: a sloping brick triangle at each corner, its coursing
    # level, U along its head
    keys = list(WALLS)
    for k, wall in enumerate(keys):
        nxt = keys[(k + 1) % 4]
        f0, f1 = Frame(*WALLS[wall]), Frame(*WALLS[nxt])
        corner = f0.P(f0.L, L.Z_SQ)
        a, b = f0.P(BH + A, L.Z_OCT), f1.P(BH - A, L.Z_OCT)
        mid = (Vector(a) + Vector(b)) / 2.0
        d = (Vector(b) - Vector(a))
        d.z = 0.0
        d.normalize()

        def uvf(co, mid=mid, d=d):
            q = Vector(co) - mid
            q.z = 0.0
            return ((BH + q.dot(d)) * PPM, L.PL_Y0 + (co[2] - L.FILLET_SHIFT) * PPM)
        B.face([corner, a, b], [uvf(c) for c in (corner, a, b)])
    # the coping: the octagon's eight vertical sides, their heads carrying
    # the wash's points
    loop, ray_idx = outer_loop(n)
    cx, cy, cw, ch = L.COPING_R
    cidx = {c[2]: i for i, c in enumerate(loop) if c[2] is not None}
    for k in range(8):
        i0, i1 = cidx[k], cidx[(k + 1) % 8]
        pts = [loop[i % len(loop)] for i in range(i0, i1 + (len(loop) if i1 <= i0 else 0) + 1)]
        p0 = Vector((pts[0][0], pts[0][1], 0.0))
        t = Vector((pts[-1][0], pts[-1][1], 0.0)) - p0
        side = t.length
        t.normalize()
        ss = [(Vector((p[0], p[1], 0.0)) - p0).dot(t) for p in pts]
        outline = ([(0.0, L.Z_OCT), (side, L.Z_OCT)]
                   + [(s, L.Z_CAP) for s in reversed(ss)])
        # the head's first and last points are the corners themselves
        outline[2] = (side, L.Z_CAP)
        outline[-1] = (0.0, L.Z_CAP)

        def to3d(s, z, p0=p0, t=t):
            q = p0 + t * s
            return (q.x, q.y, z)

        def uvc(co, p0=p0, t=t):
            s = (Vector((co[0], co[1], 0.0)) - p0).dot(t)
            return (cx + s * PPM, cy + (co[2] - L.Z_OCT) * PPM)
        fill_planar(B, outline, [], to3d, uvc)
    # the wash: from the coping's head up to the shaft's foot, mapped from
    # above
    wx, wy, ww, wh = L.WASH_R

    def uvw(co):
        return (wx + ww / 2.0 + co[0] * L.WASH_PPM, wy + wh / 2.0 + co[1] * L.WASH_PPM)
    P = [(x, y, L.Z_CAP) for x, y, _c in loop]
    for j in range(n):
        i0 = ray_idx[j]
        i1 = ray_idx[(j + 1) % n]
        between = [P[i] for i in range(i0 + 1, i1 if i1 > i0 else len(P))]
        a, b = foot[j], foot[(j + 1) % n]
        o0, o1 = P[i0], P[i1]
        if between:
            c = between[0]
            for tri in ((o0, c, a), (c, b, a), (c, o1, b)):
                B.face(list(tri), [uvw(p) for p in tri], smooth=True)
        else:
            for tri in ((o0, o1, b), (o0, b, a)):
                B.face(list(tri), [uvw(p) for p in tri], smooth=True)
    floor = [(-BH, -BH, 0.0), (-BH, BH, 0.0), (BH, BH, 0.0), (BH, -BH, 0.0)]
    B.face(floor, [uv_patch("blank")(c) for c in floor])


# ================================================================== the lathe
def ring_points(r, z, n):
    """A ring of *n* vertices at radius r * k(n), the back facet (facet 0)
    centred on +Y and the facets running counter-clockwise from above."""
    rv = r * L.k_sides(n)
    return [(rv * math.cos(a), rv * math.sin(a), z) for a in vertex_angles(n)]


def poly_radius(theta, r, n):
    """The n-gon's radius at angle *theta*: its apothem over the cosine of
    the angle from the nearest facet centre (facet centres at 90 + 360 j / n
    degrees)."""
    ap = r * L.k_sides(n) * math.cos(math.pi / n)
    step = 2 * math.pi / n
    d = (theta - math.pi / 2) % step
    d = min(d, step - d)
    return ap / math.cos(d)


def band(B, lo, hi, n, patch):
    """One ring of *n* facets from (z, r) *lo* to *hi*, mapped onto a patch."""
    (z0, r0), (z1, r1) = lo, hi
    p0, p1 = ring_points(r0, z0, n), ring_points(r1, z1, n)
    for j in range(n):
        k = (j + 1) % n
        cos = [p0[j], p0[k], p1[k], p1[j]]
        B.face(cos, [uv_patch(patch)(c) for c in cos], smooth=True)


def lift(B, z0, z1, name, v0, v1, ladder, level):
    """One lift of the shaft on band *name*, rows v0..v1 of it. U is chord
    length at 64 px/m, reduced by whole periods of the band (L.SHAFT_P) per
    facet, the same for the facet's foot and head, so the brick runs on
    across every facet and the taper never folds a facet over a wrap. The
    back facet of LOD2/LOD3 samples the band's strip, the painted ladder,
    where the lift carries it."""
    n = sides(level)
    x0, y0, ov, sx, sw = L.BANDS[name]
    r0, r1 = L.r_shaft(z0), L.r_shaft(z1)
    w0, w1 = L.chord(r0, n) * PPM, L.chord(r1, n) * PPM
    p0, p1 = ring_points(r0, z0, n), ring_points(r1, z1, n)
    for j in range(n):
        k = (j + 1) % n
        if j == 0 and ladder and level >= 2:
            c = sx + sw / 2.0
            ub, ut = c - w0 / 2.0, c - w1 / 2.0
        else:
            wrap = math.floor(j * w0 / L.SHAFT_P) * L.SHAFT_P
            ub, ut = x0 + j * w0 - wrap, x0 + j * w1 - wrap
        cos = [p0[j], p0[k], p1[k], p1[j]]
        uvs = [(ub, y0 + v0), (ub + w0, y0 + v0), (ut + w1, y0 + v1), (ut, y0 + v1)]
        B.face(cos, uvs, smooth=True)


def stack(B, level):
    """The shaft's lifts, the head band's foot, the band, the rim, the
    flue's lining and floor."""
    n = sides(level)
    for z0, z1, name, v0, v1, ladder in L.LIFTS:
        lift(B, z0, z1, name, v0, v1, ladder, level)
    band(B, (L.Z_HEAD0, L.R1), (L.Z_HEAD0, L.R_HEAD), n, "under")
    hx, hy, hw, hh = L.HEAD_R
    w = L.chord(L.R_HEAD, n) * PPM
    p0 = ring_points(L.R_HEAD, L.Z_HEAD0, n)
    p1 = ring_points(L.R_HEAD, L.Z_TOP, n)
    for j in range(n):
        k = (j + 1) % n
        u = hx + j * w
        B.face([p0[j], p0[k], p1[k], p1[j]],
               [(u, hy), (u + w, hy), (u + w, hy + hh), (u, hy + hh)], smooth=True)
    band(B, (L.Z_TOP, L.R_HEAD), (L.Z_TOP, L.R_FLUE), n, "rim")
    zt, zf = L.Z_TOP, L.Z_TOP - L.FLUE_DEPTH
    band(B, (zt, L.R_FLUE), (zf, L.R_FLUE), n, "soot")
    floor = ring_points(L.R_FLUE, zf, n)
    B.face(floor, [uv_patch("soot")(c) for c in floor])


# ========================================================= the attachments
def box(B, c, ax, ay, az, h, uvfn):
    """A closed box centred on *c*, axes ax, ay, az, half sizes *h*."""
    c = Vector(c)

    def P(i, j, k):
        q = c + ax * (i * h[0]) + ay * (j * h[1]) + az * (k * h[2])
        return (q.x, q.y, q.z)
    quads = []
    for s in (-1, 1):
        quads.append([P(s, -1, -1), P(s, 1, -1), P(s, 1, 1), P(s, -1, 1)])
        quads.append([P(-1, s, -1), P(1, s, -1), P(1, s, 1), P(-1, s, 1)])
        quads.append([P(-1, -1, s), P(1, -1, s), P(1, 1, s), P(-1, 1, s)])
    for q in quads:
        B.face(q, [uvfn(co) for co in q])
    return B


def seg_box(p0, p1, side, w, d, uvfn):
    """A bar of section w (along *side*) by d from p0 to p1, as a Builder."""
    p0, p1 = Vector(p0), Vector(p1)
    az = (p1 - p0)
    length = az.length
    az.normalize()
    ax = Vector(side)
    ax = (ax - az * ax.dot(az)).normalized()
    ay = az.cross(ax).normalized()
    return box(Builder(), (p0 + p1) / 2.0, ax, ay, az, (w / 2.0, d / 2.0, length / 2.0), uvfn)


def ring_prism(r_in, r_out, z0, z1, n, uvfn):
    """An n-sided annular prism, as a Builder: a deck, a ring rail."""
    B = Builder()
    i0, i1 = ring_points(r_in, z0, n), ring_points(r_in, z1, n)
    o0, o1 = ring_points(r_out, z0, n), ring_points(r_out, z1, n)
    for j in range(n):
        k = (j + 1) % n
        for q in ([o0[j], o0[k], o1[k], o1[j]], [i0[k], i0[j], i1[j], i1[k]],
                  [i1[j], o1[j], o1[k], i1[k]], [i0[k], o0[k], o0[j], i0[j]]):
            B.face(q, [uvfn(co) for co in q])
    return B


def flat_back(z):
    """The back facet's distance from the axis at height *z*, on LOD0's 24
    sides (LOD1's is 10 mm less at the foot; the brackets reach 50 mm in)."""
    n = L.SIDES[0]
    return L.r_shaft(z) * L.k_sides(n) * math.cos(math.pi / n)


def rail_y(z):
    """The ladder rails' centre line: STANDOFF off the back facet, along the
    batter."""
    return flat_back(z) + L.STANDOFF


def ladder(level):
    """The iron ladder up the back: two rails along the batter from the
    ladder's foot to grab handles over the deck, a rung every third of a
    metre (every third rung on LOD1), the rails held off the shaft on
    brackets."""
    steel = uv_patch("steel")
    parts = []
    za, zb = L.Z_LADDER0, L.Z_LADDER1
    for x in (-L.LADDER_HALF, L.LADDER_HALF):
        parts.append(seg_box((x, rail_y(za), za), (x, rail_y(zb), zb), (1, 0, 0),
                             L.RAIL_W, L.RAIL_D, steel))
    every = L.RUNG_EVERY[level]
    i = 0
    while True:
        z = za + L.RUNG_PITCH * (i + 0.5)
        if z > L.Z_DECK - L.DECK_T - 0.1:
            break
        if i % every == every // 2:
            y = rail_y(z)
            dz = (rail_y(z + 0.5) - rail_y(z - 0.5))
            az = Vector((0.0, dz, 1.0)).normalized()
            ay = az.cross(Vector((1.0, 0.0, 0.0))).normalized()
            parts.append(box(Builder(), (0.0, y, z), Vector((1.0, 0.0, 0.0)), ay, az,
                             (L.LADDER_HALF + 0.01, L.RUNG / 2.0, L.RUNG / 2.0), steel))
        i += 1
    for z in L.LADDER_BRACKETS:
        for x in (-L.LADDER_HALF, L.LADDER_HALF):
            y0, y1 = flat_back(z) - 0.05, rail_y(z)
            parts.append(box(Builder(), (x, (y0 + y1) / 2.0, z), Vector((1.0, 0.0, 0.0)),
                             Vector((0.0, 1.0, 0.0)), Vector((0.0, 0.0, 1.0)),
                             (L.BRACKET_W / 2.0, (y1 - y0) / 2.0, L.BRACKET_W / 2.0), steel))
    return parts


def platform(level):
    """The service platform: a steel deck ringing the head band, a ring hand
    rail and knee rail on six posts, six brackets from the shaft under it,
    as far as PLATFORM keeps them for the tier."""
    n = sides(level)
    keep = PLATFORM[level]
    steel, deck = uv_patch("steel"), uv_patch("deck")
    parts = [ring_prism(L.R_HEAD - 0.04, L.R_DECK, L.Z_DECK - L.DECK_T, L.Z_DECK, n, deck)]
    for zt, part in zip(L.RAIL_Z, ("rail", "knee")):
        if part in keep:
            parts.append(ring_prism(L.RAIL_R[0], L.RAIL_R[1], zt - L.RAIL_H, zt, n, steel))
    rm = (L.RAIL_R[0] + L.RAIL_R[1]) / 2.0
    for deg in (L.POSTS if "posts" in keep else ()):
        th = math.radians(deg)
        radial = Vector((math.cos(th), math.sin(th), 0.0))
        tang = Vector((-math.sin(th), math.cos(th), 0.0))
        rp = poly_radius(th, rm, n)
        z0, z1 = L.Z_DECK - 0.02, L.RAIL_Z[0] - 0.01
        parts.append(box(Builder(), radial * rp + Vector((0, 0, (z0 + z1) / 2.0)),
                         radial, tang, Vector((0.0, 0.0, 1.0)),
                         (0.02, L.POST_W / 2.0, (z1 - z0) / 2.0), steel))
        rs = poly_radius(th, L.r_shaft(L.STRUT_Z), n) - 0.05
        p0 = radial * rs + Vector((0.0, 0.0, L.STRUT_Z))
        p1 = radial * L.STRUT_R + Vector((0.0, 0.0, L.Z_DECK - L.DECK_T + 0.03))
        parts.append(seg_box(p0, p1, tang, L.STRUT_W, L.STRUT_W, steel))
    return parts


def lamps(level):
    """Three obstruction lamps on the head band: a box of housing and lens,
    sampling the lamp region by height, on every tier."""
    n = sides(level)
    lx, ly, lw, lh = L.LAMP_R
    parts = []
    for deg in L.LAMP_ANGLES:
        th = math.radians(deg)
        radial = Vector((math.cos(th), math.sin(th), 0.0))
        tang = Vector((-math.sin(th), math.cos(th), 0.0))
        rh = poly_radius(th, L.R_HEAD, n)
        r0, r1 = rh - 0.03, rh + L.LAMP_OUT
        z0, z1 = L.LAMP_Z[0], L.LAMP_Z[2]
        c = radial * ((r0 + r1) / 2.0) + Vector((0.0, 0.0, (z0 + z1) / 2.0))

        def uvl(co, c=c, tang=tang):
            t = (Vector(co) - c).dot(tang)
            return (lx + lw / 2.0 + t * PPM, ly + (co[2] - z0) * PPM)
        parts.append(box(Builder(), c, radial, tang, Vector((0.0, 0.0, 1.0)),
                         ((r1 - r0) / 2.0, L.LAMP_HALF, (z1 - z0) / 2.0), uvl))
    return parts


# ================================================================ assembly
def build_lod(level):
    B = Builder()
    foot = ring_points(L.r_shaft(L.Z_SHAFT0), L.Z_SHAFT0, sides(level))
    base(B, level, foot)
    stack(B, level)
    bm = B.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # smooth round the stack, sharp where its profile turns
    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        fa, fb = e.link_faces
        if not (fa.smooth and fb.smooth):
            continue
        a, b = e.verts
        if abs(a.co.z - b.co.z) < 1e-6 and fa.normal.angle(fb.normal, 0.0) > math.radians(25):
            e.smooth = False
    obj = to_object(B, "tmp_stack_LOD%d" % level)
    parts = lamps(level) + platform(level)
    if ladder_mode(level) == "solid":
        parts += ladder(level)
    obj = union(obj, [to_object(P, "tmp_part_%d_%d" % (level, i))
                      for i, P in enumerate(parts)])
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4],
                          quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# ================================================================== checks
def check_layout():
    bad = []
    # the inlet and the hatch inside their walls, the inlet under its lintel
    sc, z0, w, h = L.INLET
    if sc - w / 2 < 0.6 or sc + w / 2 > 2 * BH - 0.6:
        bad.append("the inlet is within 0.6 m of a corner")
    if abs(z0 + h - L.Z_LINTEL[0]) > 1e-6:
        bad.append("the inlet's head is not the lintel's soffit")
    sc, z0, w, h = L.HATCH
    if z0 < L.Z_FOOT + 0.1 or z0 + h > L.INLET[1] + L.INLET[3]:
        bad.append("the hatch is not low in the base, above the footing")
    # the base: fillets rising, the shaft's foot well inside the octagon
    if not (L.Z_FOOT < L.Z_SQ < L.Z_OCT < L.Z_CAP < L.Z_SHAFT0):
        bad.append("the base's heights are out of order")
    for n in L.SIDES:
        if L.r_shaft(L.Z_SHAFT0) * L.k_sides(n) > BH - 0.8:
            bad.append("%d sides: the wash is under 0.8 m wide" % n)
    # every lift's facets inside their band, the far tiers' back facet
    # inside its strip, the head inside its region
    for level, n in enumerate(L.SIDES):
        for z0, z1, name, v0, v1, lad in L.LIFTS:
            x0, y0, ov, sx, sw = L.BANDS[name]
            w0, w1 = L.chord(L.r_shaft(z0), n) * PPM, L.chord(L.r_shaft(z1), n) * PPM
            if w0 > ov:
                bad.append("%d sides, lift at %.1f m: a facet (%.1f px) overruns %s"
                           % (n, z0, w0, name))
            if (n - 1) * (w0 - w1) > L.SHAFT_ML:
                bad.append("%d sides, lift at %.1f m: the taper overruns %s's margin"
                           % (n, z0, name))
            if lad and level >= 2 and w0 > sw:
                bad.append("%d sides, lift at %.1f m: the back facet overruns %s's strip"
                           % (n, z0, name))
        if L.chord(L.R_HEAD, n) * PPM * n > L.HEAD_R[2]:
            bad.append("%d sides: the head band overruns its region" % n)
    if abs(L.LIFTS[-1][1] - L.Z_HEAD0) > 1e-9 or abs(L.LIFTS[0][0] - L.Z_SHAFT0) > 1e-9:
        bad.append("the lifts do not run from the shaft's foot to the head")
    # the head: the rim, the flue's floor, the cap ring over the lamps
    if L.R_HEAD - L.R_FLUE < 0.25:
        bad.append("the rim is under 0.25 m wide")
    if L.Z_TOP - L.FLUE_DEPTH < L.Z_HEAD0 + 0.2:
        bad.append("the flue's floor is below the head band")
    if L.LAMP_Z[2] > L.Z_TOP - L.CAP_RING - 0.05:
        bad.append("the lamps reach the cap ring")
    # the platform: under the rim, its railing outside the lamps and ladder
    if L.RAIL_Z[0] > L.Z_TOP - 0.3:
        bad.append("the railing crowds the rim")
    if abs(L.Z_TOP - L.Z_DECK - 1.5) > 0.2:
        bad.append("the deck is not about 1.5 m under the rim")
    if L.R_HEAD * 1.05 + L.LAMP_OUT > L.RAIL_R[0] - 0.15:
        bad.append("the lamps crowd the railing")
    for deg in L.POSTS:
        if abs((deg - 90.0 + 180.0) % 360.0 - 180.0) < 20.0:
            bad.append("a railing post stands at the ladder")
    # the ladder: on the shaft's batter, clear of the head band and the
    # railing, under the deck's rungs, inside the plan
    if L.Z_LADDER0 < L.Z_SHAFT0 + 2.4:
        bad.append("the ladder's foot is within reach of the base's top")
    head = L.R_HEAD * L.k_sides(L.SIDES[0]) * math.cos(math.pi / L.SIDES[0])
    if rail_y(L.Z_LADDER1) - L.RAIL_D / 2 < head + 0.05:
        bad.append("the ladder's rails run into the head band")
    if rail_y(L.Z_DECK) + L.RAIL_D / 2 > L.RAIL_R[0] - 0.2:
        bad.append("the ladder runs into the railing")
    if rail_y(L.Z_LADDER0) + L.RAIL_D / 2 > BH - 0.5:
        bad.append("the ladder stands outside the base's plan")
    if L.LADDER_BRACKETS[-1] > L.Z_HEAD0 - 0.1 or L.LADDER_BRACKETS[0] < L.Z_LADDER0:
        bad.append("a ladder bracket is off the shaft")
    if L.Z_LADDER1 > L.RAIL_Z[0] + 0.05:
        bad.append("the ladder's grab handles stand over the railing")
    return bad


def build_all():
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The base's square is the footprint; nothing stands outside it (the
    platform reaches 2.0 m from the axis, the ladder 1.6 m). A chimney has no
    door (the hatch and the inlet are not doors) and no occupied storey, so
    it lists neither, and the sidecar has no main door."""
    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-BH, -BH), (BH, -BH), (BH, BH), (-BH, BH)],
        "storeys": [],
        "doors": [],
    }


if __name__ == "__main__":
    BUILD.main(build_all, facts)
