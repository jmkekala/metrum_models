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
railing; an iron ladder in a hooped safety cage climbs the back (+Y) along
the batter from 2.5 m above the base to the platform, a copper down
conductor beside it; three obstruction lamps sit on the head band, their
lenses the emission map's only lit regions, painted red.

The stack is one closed solid built directly: the base's walls (the inlet
cut into the front at LOD0/1), the trapezoids and fillets above them, the
octagon's coping, the wash holed by the shaft's foot, and a surface of
revolution for the shaft, the head band, the platform's deck, the rim and
the flue's lining, closed by the flue's floor. The railing, ladder, cage,
conductor and lamps are separate closed solids, each held GAP clear of the
stack and of each other, so no boolean cuts any face; build_lod() checks
that no two intersect.

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
from asset_build import to_object  # noqa: E402

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


# What of the platform's steel each tier keeps (the deck is the lathe's, the
# head's silhouette on every tier): the hand rail, posts and brackets
# through LOD2, the knee rail on LOD0 alone.
PLATFORM = ({"rail", "knee", "posts", "struts"},
            {"rail", "posts", "struts"},
            {"rail", "posts", "struts"},
            set())


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


def strip_x():
    """The conductor's painted strip down the base's rear: its x range."""
    s0 = L.COND_S0
    return BH - s0 - L.COND_SW / PPM, BH - s0


def outer_loop(n):
    """The octagon's top edge as the wash meets it: a point where each ray
    to a shaft vertex leaves it, its eight corners, and the conductor strip's
    two edges on the rear flat, counter-clockwise from the first ray.
    Returns [(x, y, corner index or None)] and, per shaft vertex, its point's
    index in the loop."""
    tau = 2 * math.pi
    th = vertex_angles(n)
    a0 = th[0] % tau
    corners = [(math.atan2(y, x) % tau, k) for k, (x, y) in enumerate(OCTAGON)]
    pts = []
    for j in range(n):
        a = th[j] % tau
        hit = next((k for ang, k in corners
                    if abs((ang - a + math.pi) % tau - math.pi) < 1e-9), None)
        pt = OCTAGON[hit] + (hit,) if hit is not None else ray_octagon(th[j]) + (None,)
        pts.append(((a - a0) % tau, pt, j))
    for ang, k in corners:
        if all(abs(p[1][0] - OCTAGON[k][0]) + abs(p[1][1] - OCTAGON[k][1]) > 1e-9 for p in pts):
            pts.append(((ang - a0) % tau, OCTAGON[k] + (k,), None))
    for x in strip_x():
        if all(abs(p[1][0] - x) + abs(p[1][1] - BH) > 1e-6 for p in pts):
            pts.append(((math.atan2(BH, x) - a0) % tau, (x, BH, None), None))
    pts.sort(key=lambda p: p[0])
    loop = [p[1] for p in pts]
    ray_idx = [0] * n
    for i, p in enumerate(pts):
        if p[2] is not None:
            ray_idx[p[2]] = i
    return loop, ray_idx


def clip_s(poly, a, b):
    """The part of a convex polygon in (s, z) with a <= s <= b."""
    def cut(pts, keep, edge):
        out = []
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            if keep(p):
                out.append(p)
            if keep(p) != keep(q):
                t = (edge - p[0]) / (q[0] - p[0])
                out.append((edge, p[1] + t * (q[1] - p[1])))
        return out
    pts = cut(list(poly), lambda p: p[0] >= a - 1e-6, a) if a is not None else list(poly)
    pts = cut(pts, lambda p: p[0] <= b + 1e-6, b) if b is not None and pts else pts
    clean = []
    for p in pts:
        if not clean or abs(p[0] - clean[-1][0]) + abs(p[1] - clean[-1][1]) > 1e-6:
            clean.append(p)
    if len(clean) > 1 and abs(clean[0][0] - clean[-1][0]) + abs(clean[0][1] - clean[-1][1]) < 1e-6:
        clean.pop()
    return clean


def fill_split(B, outline, to3d, uvfn, s0, s1, uv_strip):
    """fill_planar a convex outline in three pieces split at s0 and s1, the
    middle one mapped by *uv_strip*."""
    for a, b, fn in ((None, s0, uvfn), (s0, s1, uv_strip), (s1, None, uvfn)):
        piece = clip_s(outline, a, b)
        if len(piece) >= 3:
            fill_planar(B, piece, [], to3d, fn)


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
        # the wall runs on up as a trapezoid between the corner fillets; it
        # samples range A, lower, where the brick is plain
        trap = [(0.0, L.Z_SQ), (fr.L, L.Z_SQ), (BH + A, L.Z_OCT), (BH - A, L.Z_OCT)]
        f = uv_wall(fr, "east", L.FILLET_SHIFT)
        if wall == "rear":
            # the conductor's strip: the wall and the trapezoid over it
            # sample their own copy of the brick with the strap painted on
            s0, s1 = L.COND_S0, L.COND_S0 + L.COND_SW / PPM
            cx, cy = L.COND_BASE_R[:2]
            fill_split(B, outline, fr.P, uv_wall(fr, wall), s0, s1,
                       uv_region(fr, (cx, cy, 0, 0), s0, 0.0))
            fill_split(B, trap, fr.P, f, s0, s1,
                       uv_region(fr, (cx, cy, 0, 0), s0, L.FILLET_SHIFT))
            continue
        fill_planar(B, outline, holes, fr.P, uv_wall(fr, wall))
        cos = [fr.P(s, z) for s, z in trap]
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
        if k == 4:
            # the rear side, from (A, BH) running west: the conductor's strip
            sc = A - strip_x()[1]
            qx, qy = L.COND_COPING_R[:2]

            def uvs(co, p0=p0, t=t, sc=sc):
                s = (Vector((co[0], co[1], 0.0)) - p0).dot(t)
                return (qx + (s - sc) * PPM, qy + (co[2] - L.Z_OCT) * PPM)
            fill_split(B, outline, to3d, uvc, sc, sc + L.COND_SW / PPM, uvs)
            continue
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
        chain = [P[i0]] + between + [P[i1]]
        # a fan from the foot's first vertex over the chain's first half, from
        # its second over the rest
        mid = (len(chain) - 1) // 2
        tris = [(chain[i], chain[i + 1], a) for i in range(mid)]
        tris.append((chain[mid], b, a))
        tris += [(chain[i], chain[i + 1], b) for i in range(mid, len(chain) - 1)]
        for tri in tris:
            B.face(list(tri), [uvw(p) for p in tri], smooth=True)
    # the rear wall's foot carries the conductor strip's two corners
    xs = strip_x()
    floor = [(-BH, -BH, 0.0), (-BH, BH, 0.0), (xs[0], BH, 0.0), (xs[1], BH, 0.0),
             (BH, BH, 0.0), (BH, -BH, 0.0)]
    B.face(floor, [uv_patch("blank")(c) for c in floor])


# ================================================================== the lathe
def ring_points(r, z, n):
    """A ring of *n* vertices at radius r * k(n), the back facet (facet 0)
    centred on +Y and the facets running counter-clockwise from above."""
    rv = r * L.k_sides(n)
    return [(rv * math.cos(a), rv * math.sin(a), z) for a in vertex_angles(n)]


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
    """The shaft's lifts, the head band's foot, the band in two parts round
    the platform's deck (its underside, outer edge and top are the profile's
    own), the rim, the flue's lining and floor."""
    n = sides(level)
    for z0, z1, name, v0, v1, ladder in L.LIFTS:
        lift(B, z0, z1, name, v0, v1, ladder, level)
    band(B, (L.Z_HEAD0, L.R1), (L.Z_HEAD0, L.R_HEAD), n, "under")
    hx, hy, hw, hh = L.HEAD_R
    w = L.chord(L.R_HEAD, n) * PPM
    zl, zd = L.Z_DECK - L.DECK_T, L.Z_DECK
    for z0, z1 in ((L.Z_HEAD0, zl), (zd, L.Z_TOP)):
        p0 = ring_points(L.R_HEAD, z0, n)
        p1 = ring_points(L.R_HEAD, z1, n)
        v0, v1 = hy + (z0 - L.Z_HEAD0) * PPM, hy + (z1 - L.Z_HEAD0) * PPM
        for j in range(n):
            k = (j + 1) % n
            u = hx + j * w
            B.face([p0[j], p0[k], p1[k], p1[j]],
                   [(u, v0), (u + w, v0), (u + w, v1), (u, v1)], smooth=True)
    band(B, (zl, L.R_HEAD), (zl, L.R_DECK), n, "deck")
    band(B, (zl, L.R_DECK), (zd, L.R_DECK), n, "deck")
    band(B, (zd, L.R_DECK), (zd, L.R_HEAD), n, "deck")
    band(B, (L.Z_TOP, L.R_HEAD), (L.Z_TOP, L.R_FLUE), n, "rim")
    zt, zf = L.Z_TOP, L.Z_TOP - L.FLUE_DEPTH
    band(B, (zt, L.R_FLUE), (zf, L.R_FLUE), n, "soot")
    floor = ring_points(L.R_FLUE, zf, n)
    B.face(floor, [uv_patch("soot")(c) for c in floor])


# ========================================================= the attachments
# Every attachment is a closed solid of its own, held GAP off the stack and
# off every other part, so no boolean cuts the shaft's faces or the rails'
# and the whole kit costs only its own triangles. A part is a section swept
# along a polyline (sweep): a rung, a rail, a hoop, a ring rail.
GAP = L.GAP
X_AXIS, Z_AXIS = Vector((1.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0))


def plane_hit(c, d, plane):
    """Where the line through *c* along *d* meets *plane* (point, normal)."""
    q, nrm = plane
    return c + d * ((q - c).dot(nrm) / d.dot(nrm))


def sweep(B, pts, section, uvfn, side_hint=None, closed=False, ends=(None, None)):
    """A closed solid: *section*, a polygon of (side, up) offsets, swept
    along the polyline *pts* and mitred at its bends, its ends square or cut
    by the planes in *ends*, or a closed ring. side is *side_hint* made
    square to each segment, or the segment's right in plan (outward round a
    loop walked counter-clockwise); up is side x direction."""
    P = [Vector(p) for p in pts]
    m = len(P)
    segs = m if closed else m - 1
    D = [(P[(i + 1) % m] - P[i]).normalized() for i in range(segs)]

    def frame(d):
        if side_hint is None:
            sv = d.cross(Z_AXIS)
        else:
            h = Vector(side_hint)
            sv = h - d * h.dot(d)
        sv.normalize()
        return sv, sv.cross(d)
    F = [frame(d) for d in D]
    rings = []
    for k in range(m):
        if closed:
            fa, fb = F[k - 1], F[k]
        else:
            fa, fb = F[max(k - 1, 0)], F[min(k, segs - 1)]
        S = (fa[0] + fb[0]) / (1.0 + fa[0].dot(fb[0]))
        U = (fa[1] + fb[1]) / (1.0 + fa[1].dot(fb[1]))
        rings.append([P[k] + S * a + U * b for a, b in section])
    if not closed:
        for idx, d, plane in ((0, D[0], ends[0]), (-1, D[-1], ends[1])):
            if plane is not None:
                rings[idx] = [plane_hit(c, d, plane) for c in rings[idx]]
    ns = len(section)
    for i in range(segs):
        r0, r1 = rings[i], rings[(i + 1) % m]
        for j in range(ns):
            q = [r0[j], r0[(j + 1) % ns], r1[(j + 1) % ns], r1[j]]
            B.face(q, [uvfn(co) for co in q])
    if not closed:
        for r in (rings[0], rings[-1]):
            B.face(r, [uvfn(co) for co in r])
    return B


def tri(w, d):
    """A triangular section w wide (along side) with its flat face at
    up = 0 and its apex d out along -up."""
    return [(-w / 2.0, 0.0), (w / 2.0, 0.0), (0.0, -d)]


def rect(w, d):
    return [(-w / 2.0, -d / 2.0), (w / 2.0, -d / 2.0), (w / 2.0, d / 2.0), (-w / 2.0, d / 2.0)]


def facet_normals(n):
    """The outward normals of an n-sided ring's facets, in plan."""
    return [Vector((math.cos(a), math.sin(a), 0.0))
            for a in (math.pi / 2 + 2 * math.pi * j / n for j in range(n))]


def apothem(r, n):
    return r * L.k_sides(n) * math.cos(math.pi / n)


def back_y(x, r, n):
    """Where the line at *x* (parallel to y) leaves the n-sided ring of
    radius *r* on its +Y side."""
    ap = apothem(r, n)
    return min((ap - x * f.x) / f.y for f in facet_normals(n) if f.y > 0.2)


def facet_plane(theta, rfun, n, za, zb):
    """The facet of the battered n-sided surface of radius rfun(z) at angle
    *theta*, as (point, outward normal), between heights za and zb."""
    step = 2 * math.pi / n
    th0 = vertex_angles(n)[0]
    j = int(math.floor(((theta - th0) % (2 * math.pi)) / step))
    a0, a1 = th0 + j * step, th0 + (j + 1) * step
    k = L.k_sides(n)

    def p(a, z):
        return Vector((rfun(z) * k * math.cos(a), rfun(z) * k * math.sin(a), z))
    A, Bv, C = p(a0, za), p(a1, za), p(a0, zb)
    nrm = (Bv - A).cross(C - A).normalized()
    mid = (a0 + a1) / 2.0
    if nrm.dot(Vector((math.cos(mid), math.sin(mid), 0.0))) < 0:
        nrm = -nrm
    return A, nrm


def offset(plane, d):
    return plane[0] + plane[1] * d, plane[1]


def flat_back(z):
    """The back facet's distance from the axis at height *z*, on LOD0's 24
    sides: the ladder's line is the same on every tier."""
    return apothem(L.r_shaft(z), L.SIDES[0])


def rail_y(z):
    """The ladder rails' centre line: STANDOFF off the back facet, along the
    batter."""
    return flat_back(z) + L.STANDOFF


def rail_frame():
    """A rail's direction, and its section's up (toward the shaft)."""
    d = Vector((0.0, rail_y(L.Z_DECK) - rail_y(L.Z_LADDER0), L.Z_DECK - L.Z_LADDER0)).normalized()
    return d, X_AXIS.cross(d)


def rail_point(x, z):
    return Vector((x, rail_y(z), z))


def ladder(B, level):
    """The iron ladder up the back: two rails along the batter from the
    ladder's foot to under the deck and on above it as grab handles, a rung
    every third of a metre (every third rung on LOD1) between them, each a
    triangular bar stopping GAP short of the rails, and pairs of brackets
    from the shaft to the rails' inner faces, stopping GAP short of both."""
    steel = uv_patch("steel")
    n = sides(level)
    za, zb = L.Z_LADDER0, L.Z_LADDER1
    zl, zd = L.Z_DECK - L.DECK_T, L.Z_DECK
    d, up = rail_frame()
    for x in (-L.LADDER_HALF, L.LADDER_HALF):
        for z0, z1 in ((za, zl - GAP), (zd + GAP, zb)):
            sweep(B, [rail_point(x, za), rail_point(x, zb)], rect(L.RAIL_W, L.RAIL_D), steel,
                  side_hint=X_AXIS, ends=((Vector((0, 0, z0)), Z_AXIS), (Vector((0, 0, z1)), Z_AXIS)))
    inner = L.LADDER_HALF - L.RAIL_W / 2.0 - GAP
    every = L.RUNG_EVERY[level]
    i = 0
    while True:
        z = za + L.RUNG_PITCH * (i + 0.5)
        if z > zl - 0.1:
            break
        if i % every == every // 2:
            # a flat top, the apex under it
            c = rail_point(0.0, z) + Vector((0.0, 0.0, L.RUNG / 3.0))
            sweep(B, [c - X_AXIS * inner, c + X_AXIS * inner],
                  [(-L.RUNG / 2.0, 0.0), (L.RUNG / 2.0, 0.0), (0.0, -L.RUNG * 0.85)],
                  steel, side_hint=Vector((0.0, 1.0, 0.0)))
        i += 1
    for i, z in enumerate(L.LADDER_BRACKETS):
        if L.BRACKET_EVERY[level] is None or i % L.BRACKET_EVERY[level]:
            continue
        for x in (-L.LADDER_HALF, L.LADDER_HALF):
            ax = abs(x) - L.BRACKET_W / 2.0
            y_end = back_y(ax, L.r_shaft(z - L.BRACKET_W), n) + GAP
            face = rail_point(x, z) + up * (L.RAIL_D / 2.0 + GAP)
            c = Vector((x, y_end, z))
            sweep(B, [c, Vector((x, rail_y(z), z))], tri(L.BRACKET_W, L.BRACKET_W * 0.8), steel,
                  side_hint=X_AXIS,
                  ends=((Vector((0.0, y_end, 0.0)), Vector((0.0, 1.0, 0.0))), (face, up)))


def hoop_plan():
    """A hoop's polyline in plan, (x, out from the rails' centre line), from
    the east rail round behind the ladder to the west one; its two ends lie
    inside the rails and are cut GAP off their outer faces."""
    (bx, by), (cx, cy) = L.HOOP
    e = L.LADDER_HALF + 0.02
    return [(e, 0.0), (bx, by), (cx, cy), (-bx, by), (-e, 0.0)]


def cage_levels(level):
    every = L.CAGE_EVERY[level]
    ks = [k for k in range(L.CAGE_N) if k % every == 0]
    if ks[-1] != L.CAGE_N - 1:
        ks.append(L.CAGE_N - 1)
    return [L.CAGE_Z0 + k * L.CAGE_PITCH for k in ks]


def cage(B, level):
    """The safety cage: level flat-bar hoops along the batter, each a
    triangular bar of four chords, its broad face outward, cut GAP off the
    rails' outer faces; three straps outside them, at the hoops' corners
    and their back, GAP off the hoops' outer arrises."""
    steel = uv_patch("steel")
    plan = hoop_plan()
    outer = L.LADDER_HALF + L.RAIL_W / 2.0 + GAP
    # broad face outward, the apex in
    section = [(L.HOOP_T / 2.0, -L.HOOP_H / 2.0), (L.HOOP_T / 2.0, L.HOOP_H / 2.0),
               (-L.HOOP_T / 2.0, 0.0)]
    zs = cage_levels(level)
    for z in zs:
        y0 = rail_y(z)
        pts = [(x, y0 + o, z) for x, o in plan]
        sweep(B, pts, section, steel,
              ends=((Vector((outer, 0, 0)), X_AXIS), (Vector((-outer, 0, 0)), X_AXIS)))
    # the straps: at each corner, along the bisector of the hoop's turn
    d, _up = rail_frame()
    for i in (1, 2, 3):
        p = Vector((plan[i][0], plan[i][1], 0.0))
        a = (p - Vector((plan[i - 1][0], plan[i - 1][1], 0.0))).normalized()
        b = (Vector((plan[i + 1][0], plan[i + 1][1], 0.0)) - p).normalized()
        sa, sb = a.cross(Z_AXIS), b.cross(Z_AXIS)
        nb = (sa + sb).normalized()
        reach = (L.HOOP_T / 2.0) / math.cos(sa.angle(sb) / 2.0) + 2 * GAP
        base = p + nb * reach
        z0, z1 = zs[0] - 0.04, zs[-1] + 0.04
        c0 = Vector((base.x, rail_y(z0) + base.y, z0))
        c1 = Vector((base.x, rail_y(z1) + base.y, z1))
        # the flat face against the hoops, the apex out
        sweep(B, [c0, c1], [(0.0, -L.STRAP_W / 2.0), (L.STRAP_T, 0.0), (0.0, L.STRAP_W / 2.0)],
              steel, side_hint=nb)


def conductor_line(rfun, n, z0, z1):
    """The conductor's inner face line at COND_X, COND_OFF off the n-sided
    surface of radius rfun(z) between z0 and z1: straight, raised wherever
    the surface between its ends would come closer (a facet's edge)."""
    xa = L.COND_X - L.COND_W / 2.0

    def need(z):
        return back_y(xa, rfun(z), n) + L.COND_OFF
    ya, yb = need(z0), need(z1)
    lift = max(need(z0 + (z1 - z0) * t / 64.0) - (ya + (yb - ya) * t / 64.0)
               for t in range(65))
    return (Vector((L.COND_X, ya + lift, z0)), Vector((L.COND_X, yb + lift, z1)))


def conductor(B, level):
    """The lightning down conductor beside the ladder: a copper strap from
    the shaft's foot to under the head band, then up the band, under and
    over the deck, to its air terminal level with the rim."""
    copper = uv_patch("copper")
    n = sides(level)
    zl, zd = L.Z_DECK - L.DECK_T, L.Z_DECK
    runs = ((L.r_shaft, L.Z_SHAFT0 + 0.03, L.Z_HEAD0 - GAP),
            (lambda z: L.R_HEAD, L.Z_HEAD0 + GAP, zl - GAP),
            (lambda z: L.R_HEAD, zd + GAP, L.COND_TIP))
    for rfun, z0, z1 in runs:
        a, b = conductor_line(rfun, n, z0, z1)
        # the flat face toward the shaft (up is -Y here), the apex out
        sweep(B, [a, b], [(-L.COND_W / 2.0, 0.0), (0.0, -L.COND_T), (L.COND_W / 2.0, 0.0)],
              copper, side_hint=X_AXIS)


def ring_rail(B, rc, zc, n, uvfn):
    """A railing's ring rail: a triangular bar round a polygon of radius rc,
    its flat underside at zc - 0.0125, apex up."""
    pts = ring_points(rc, zc, n)
    sweep(B, pts, [(-0.022, -0.0125), (0.022, -0.0125), (0.0, 0.025)], uvfn, closed=True)
    return apothem(rc, n) - 0.022


def platform(B, level):
    """The service platform's steel: a ring hand rail and knee rail, six
    posts just inside them from GAP over the deck, and six brackets from the
    shaft to GAP under the deck, as far as PLATFORM keeps them."""
    n = sides(level)
    keep = PLATFORM[level]
    steel = uv_patch("steel")
    # square posts and brackets close up, triangular bars beyond
    bar = rect if level == 0 else (lambda w, d: [(-w / 2.0, d / 2.0), (w / 2.0, d / 2.0),
                                                  (0.0, -d / 2.0)])
    rc = (L.RAIL_R[0] + L.RAIL_R[1]) / 2.0
    inner = None
    for zt, part in zip(L.RAIL_Z, ("rail", "knee")):
        if part in keep:
            inner = ring_rail(B, rc, zt - 0.025, n, steel)
    zl, zd = L.Z_DECK - L.DECK_T, L.Z_DECK
    for deg in L.POSTS:
        th = math.radians(deg)
        radial = Vector((math.cos(th), math.sin(th), 0.0))
        tang = Vector((-math.sin(th), math.cos(th), 0.0))
        if "posts" in keep and inner is not None:
            # the post's outer corners GAP inside every facet of the rings
            hw, pd = L.POST_W / 2.0, 0.04
            rp = min((inner - GAP - abs(hw * tang.dot(f))) / radial.dot(f)
                     for f in facet_normals(n) if radial.dot(f) > 0.3) - pd / 2.0
            c = radial * rp
            sweep(B, [c + Vector((0, 0, zd + GAP)), c + Vector((0, 0, L.RAIL_Z[0]))],
                  bar(L.POST_W, pd), steel, side_hint=tang)
        if "struts" in keep:
            p0 = radial * (L.r_shaft(L.STRUT_Z) - 0.1) + Vector((0.0, 0.0, L.STRUT_Z))
            p1 = radial * L.STRUT_R + Vector((0.0, 0.0, zl))
            shaft = offset(facet_plane(th, L.r_shaft, n, L.STRUT_Z - 0.1, L.STRUT_Z + 0.1), GAP)
            sweep(B, [p0, p1], bar(L.STRUT_W, L.STRUT_W), steel, side_hint=tang,
                  ends=(shaft, (Vector((0, 0, zl - GAP)), Z_AXIS)))


def lamps(B, level):
    """Three obstruction lamps on the head band: a body of nb sides (six on
    LOD0, four after), its foot the cast housing and its upper part the red
    lens, under a low pointed dome, on an arm from the band (LOD0). The
    body's faces sample LAMP_R by height."""
    n = sides(level)
    nb = 6 if level == 0 else 4
    lx, ly, lw, lh = L.LAMP_R
    z0, zl, z1, zt = L.LAMP_Z
    steel = uv_patch("steel")
    for deg in L.LAMP_ANGLES:
        th = math.radians(deg)
        radial = Vector((math.cos(th), math.sin(th), 0.0))
        tang = Vector((-math.sin(th), math.cos(th), 0.0))
        face = apothem(L.R_HEAD, n)                 # lamps stand on facet centres
        axis = radial * (face + L.LAMP_OUT)
        ring = []
        for i in range(nb):
            a = 2 * math.pi * (i + 0.5) / nb
            ring.append(axis + (radial * math.cos(a) + tang * math.sin(a)) * L.LAMP_RAD)
        side = (ring[1] - ring[0]).length
        foot = [Vector((p.x, p.y, z0)) for p in ring]
        head = [Vector((p.x, p.y, z1)) for p in ring]
        cu = lx + lw / 2.0
        for i in range(nb):
            k = (i + 1) % nb
            B.face([foot[i], foot[k], head[k], head[i]],
                   [(cu - side / 2 * PPM, ly), (cu + side / 2 * PPM, ly),
                    (cu + side / 2 * PPM, ly + lh), (cu - side / 2 * PPM, ly + lh)])
        tip = Vector((axis.x, axis.y, zt))
        for i in range(nb):
            k = (i + 1) % nb
            B.face([head[i], head[k], tip],
                   [(cu - side / 2 * PPM, ly + lh - 1.5), (cu + side / 2 * PPM, ly + lh - 1.5),
                    (cu, ly + lh - 0.5)])
        B.face(list(reversed(foot)), [(cu, ly + 1.0)] * nb)
        if level == 0:
            aw, ad = L.LAMP_ARM
            band = offset(facet_plane(th, lambda z: L.R_HEAD, n, z0 - 0.1, z0), GAP)
            ztop = z0 - GAP
            sweep(B, [radial * (face - 0.05) + Vector((0, 0, ztop)),
                      axis + Vector((0, 0, ztop))],
                  [(-aw / 2.0, 0.0), (aw / 2.0, 0.0), (0.0, ad)], steel, side_hint=tang,
                  ends=(band, None))


# ================================================================ assembly
def overlaps(bm, parts):
    """Pairs of parts (face index ranges of *bm*) whose triangles intersect;
    part 0 is the stack."""
    from mathutils.bvhtree import BVHTree
    bm.faces.ensure_lookup_table()
    trees, boxes = [], []
    for f0, f1 in parts:
        faces = [bm.faces[i] for i in range(f0, f1)]
        remap = {}
        for f in faces:
            for v in f.verts:
                remap.setdefault(v, len(remap))
        co = [v.co.copy() for v in remap]
        trees.append(BVHTree.FromPolygons(co, [[remap[v] for v in f.verts] for f in faces]))
        boxes.append((Vector([min(c[i] for c in co) for i in range(3)]),
                      Vector([max(c[i] for c in co) for i in range(3)])))
    bad = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            (a0, a1), (b0, b1) = boxes[i], boxes[j]
            if any(a1[k] < b0[k] - 1e-4 or b1[k] < a0[k] - 1e-4 for k in range(3)):
                continue
            if trees[i].overlap(trees[j]):
                bad.append((i, j))
    return bad


def build_lod(level):
    """The stack and every attachment in one bmesh, each a separate closed
    shell: no boolean, so the kit's triangles are its own."""
    B = Builder()
    foot = ring_points(L.r_shaft(L.Z_SHAFT0), L.Z_SHAFT0, sides(level))
    base(B, level, foot)
    stack(B, level)
    parts = [(0, len(B.bm.faces))]
    adders = [lambda B: lamps(B, level), lambda B: platform(B, level)]
    if ladder_mode(level) == "solid":
        adders += [lambda B: ladder(B, level), lambda B: cage(B, level),
                   lambda B: conductor(B, level)]
    for add in adders:
        # one range per closed shell, so overlaps() can test each
        before = len(B.bm.faces)
        add(B)
        parts.extend(_shells(B.bm, before))
    bad = overlaps(B.bm, parts)
    if bad:
        raise ValueError("LOD%d: %d intersecting part pairs, e.g. faces %s and %s"
                         % (level, len(bad), parts[bad[0][0]], parts[bad[0][1]]))
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
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4],
                          quad_method='BEAUTY', ngon_method='BEAUTY')
    obj = to_object(B, "{}_LOD{}".format(ASSET, level))
    obj.data.name = obj.name + "_mesh"
    return obj


def _shells(bm, first):
    """Face index ranges of the connected shells among faces from *first* on
    (each part's faces are added together, so a shell is a contiguous
    range)."""
    bm.faces.ensure_lookup_table()
    if first >= len(bm.faces):
        return []
    out, start = [], first
    verts = set()
    for i in range(first, len(bm.faces)):
        f = bm.faces[i]
        fv = set(f.verts)
        if i > start and not (fv & verts):
            # a face sharing nothing with the current shell starts a new one,
            # unless it joins it later; parts are swept ring by ring, so a
            # face of the same part always shares a vertex with an earlier one
            out.append((start, i))
            start, verts = i, set()
        verts |= fv
    out.append((start, len(bm.faces)))
    return out


def kit_triangles(level):
    """Triangles of everything but the stack, for notes.md."""
    B = Builder()
    adders = [lamps, platform] + ([ladder, cage, conductor]
                                  if ladder_mode(level) == "solid" else [])
    out = {}
    for add in adders:
        b0 = sum(len(f.verts) - 2 for f in B.bm.faces)
        add(B, level)
        out[add.__name__] = sum(len(f.verts) - 2 for f in B.bm.faces) - b0
    B.bm.free()
    return out


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
    if L.LAMP_Z[3] > L.Z_TOP - L.CAP_RING - 0.05:
        bad.append("the lamps reach the cap ring")
    if not (L.LAMP_Z[0] < L.LAMP_Z[1] < L.LAMP_Z[2] < L.LAMP_Z[3]):
        bad.append("the lamps' heights are out of order")
    # the platform: under the rim, its railing outside the lamps and ladder
    if L.RAIL_Z[0] > L.Z_TOP - 0.3:
        bad.append("the railing crowds the rim")
    if abs(L.Z_TOP - L.Z_DECK - 1.5) > 0.2:
        bad.append("the deck is not about 1.5 m under the rim")
    if L.R_HEAD * 1.05 + L.LAMP_OUT + L.LAMP_RAD > L.RAIL_R[0] - 0.15:
        bad.append("the lamps crowd the railing")
    if L.LAMP_OUT - L.LAMP_RAD < 0.04:
        bad.append("a lamp's body touches the band")
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
    # the cage: from about 2.5 m over the ladder's foot to under the deck,
    # hoops no further apart than 1.8 m, inside the base's plan
    zs = cage_levels(0)
    if not 2.2 <= L.CAGE_Z0 - L.Z_LADDER0 <= 3.0:
        bad.append("the cage does not start about 2.5 m above the ladder's foot")
    if L.CAGE_PITCH > 1.8:
        bad.append("the hoops are more than 1.8 m apart")
    if zs[-1] + L.HOOP_H / 2 + 0.04 > L.Z_DECK - L.DECK_T - 0.1:
        bad.append("the cage runs into the deck")
    if L.Z_DECK - L.DECK_T - zs[-1] > L.CAGE_PITCH + 0.2:
        bad.append("the cage stops short of the deck")
    reach = rail_y(zs[0]) + L.HOOP[1][1] + L.HOOP_T + 2 * GAP + L.STRAP_T
    if reach > BH - 0.3:
        bad.append("the cage reaches outside the base's plan (%.2f m)" % reach)
    if L.HOOP[0][0] < L.LADDER_HALF + 0.1:
        bad.append("the hoops are no wider than the ladder")
    # the conductor: beside the ladder, clear of its brackets, its terminal
    # no higher than the rim (the bounds)
    if L.COND_X - L.COND_W / 2 < L.LADDER_HALF + L.BRACKET_W / 2 + 0.01:
        bad.append("the conductor runs into the ladder's brackets")
    if L.COND_TIP > L.Z_TOP:
        bad.append("the air terminal stands over the rim")
    return bad


def build_all():
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The base's square is the footprint; nothing stands outside it (the
    platform reaches 2.0 m from the axis, the ladder's cage 2.9 m). A chimney has no
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
