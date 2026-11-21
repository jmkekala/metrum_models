# SPDX-License-Identifier: GPL-3.0-or-later

"""rigid_box_18t: a two-axle 18 t cab-over box truck, all four tiers.

    python3 truck_atlas.py export
    blender --background --python build.py

Stations, the atlas layout and the UV mappings are truck_atlas.py's (L).

LOD0/LOD1: the cab is a loft of rounded rings (rounded vertical corners and
roof edge, raked screen) with its arches, step wells, screen, door glass,
grille and side repeaters cut in by exact booleans; each lamp and pane is
the floor of the cutter that makes its recess, so it carries its own id and
UVs. A bumper loft with the headlamp units and the front plate, the step
carriers, the roof deflector and its side flaps, the box (panels set in
behind aluminium rails, corner posts and a rear frame round an inset roller
door, marker lamps in the rails), the chassis rails, subframe and cross
bearers, the fuel tank, battery box and tanks, side guards on brackets,
mudguards with flaps, axle housings, the rear under-run bar with the lamp
housings and plate are unioned into one closed body. Mirrors are separate
closed solids a few millimetres off the cab; wheels are revolved closed
solids, the rear twins one part a side. LOD2: plain massing with lamp cells
on flat faces, the wheels as hexagonal prisms in the body. LOD3: one
extruded side profile.
"""

import importlib
import math
import os
import sys

import bmesh
import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import truck_atlas as L  # noqa: E402
importlib.reload(L)
sys.path.insert(0, L.SCRIPTS)
import asset_build  # noqa: E402
import vehicle_build as VB  # noqa: E402
import model_facts  # noqa: E402

asset_build.check_toolchain()
# preview_paint None: the albedo as shipped. render_variants() multiplies
# every variant by preview_paint, the paint-false livery too, which the
# consumer paints white; a tint here would darken the haulier's sheet.
V = VB.VehicleAsset(L.ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT, "truck",
                    preview_paint=None)

Y = L.Y


def P(x, s, z):
    return (float(x), float(Y(s)), float(z))


def sw(co):
    """(x, s, z) of a build-frame point."""
    return co[0], co[1] + L.HL, co[2]


# ================================================================ kinds
class K:
    """How a face is mapped and tagged: onto a patch (rect) by its own
    planar extent, or through uv(co) -> atlas pixels."""

    def __init__(self, rect=None, uv=None, surface=0, paint=False):
        self.rect = L.REG[rect] if isinstance(rect, str) else rect
        self.uv, self.surface, self.paint = uv, surface, paint


def put(B, cos, k, smooth=True):
    if k.uv is not None:
        return B.face(cos, k.uv, surface=k.surface, paint=k.paint, smooth=smooth)
    return VB.patch_face(B, cos, k.rect, surface=k.surface, paint=k.paint, smooth=smooth)


def put_uv(B, cos, uvs, surface=0, paint=False, smooth=True):
    it = iter(uvs)
    return B.face(cos, lambda co: next(it), surface=surface, paint=paint, smooth=smooth)


def uv_box_side(co):
    _x, s, z = sw(co)
    return L.at("box_side", s - L.BOX_S0, z - L.BOX_Z0)


def uv_box_roof(co):
    x, s, _z = sw(co)
    return L.at("box_roof", s - L.BOX_S0, x + L.BOX_HW)


def uv_box_front(co):
    x, _s, z = sw(co)
    return L.at("box_front", x + L.BOX_HW, z - L.BOX_Z0)


def uv_box_rear(co):
    x, _s, z = sw(co)
    return L.at("box_rear", -x + L.BOX_HW, z - L.BOX_Z0)


def uv_rail(co):
    _x, s, z = sw(co)
    return L.at("rail", s - L.BOX_S0, z - L.BOX_Z0)


def uv_cab_roof(co):
    x, s, _z = sw(co)
    return L.at("cab_roof", x + L.CAB_HW, s - 0.30)


def uv_bumper_front(co):
    x, _s, z = sw(co)
    v = float(np.interp(z, [r[0] for r in L.BUMPER_RINGS], L.BUMPER_V))
    return L.at("bumper", abs(x), v)


def uv_lod3_side(co):
    _x, s, z = sw(co)
    return L.at("lod3_side", s, z, ppm=L.LOD3_PPM)


def uv_lod3_front(co):
    x, _s, z = sw(co)
    return L.at("lod3_front", x + L.BOX_HW, z, ppm=L.LOD3_PPM)


def uv_lod3_rear(co):
    x, _s, z = sw(co)
    return L.at("lod3_rear", -x + L.BOX_HW, z, ppm=L.LOD3_PPM)


PAINT_CAB = K("cabpaint", paint=True) if "cabpaint" in L.REG else None
DARK, LINER, ALU, ALU_LOW, TANK, GUARD, RUBBER, PLASTIC, STEP, HOUSING, SEAL, MBODY, MGLASS = (
    K(n) for n in ("dark", "liner", "alu", "alu_low", "tank", "guard", "rubber", "plastic",
                   "step", "housing", "seal", "mirror_body", "mirror"))


def lamp(lid, colour=None):
    return K(L.lens_kind(lid, colour), surface=lid)


# ================================================================ solids
def new():
    return VB.Builder(L.ATLAS)


def obj(B, name="tmp"):
    VB.conform(B)
    # conform() replaces a face but leaves its old, now faceless edges behind
    loose = [e for e in B.bm.edges if not e.link_faces]
    if loose:
        bmesh.ops.delete(B.bm, geom=loose, context='EDGES')
    return VB._object(name, B)


def box(B, x0, x1, s0, s1, z0, z1, k):
    """An axis-aligned box in (x, s, z); k a K or a dict keyed by face
    ('x0', 'x1', 's0', 's1', 'z0', 'z1') with 'all' as the default."""
    def kk(f):
        if isinstance(k, K):
            return k
        return k.get(f, k.get("all"))
    c = {(i, j, l): P((x0, x1)[i], (s0, s1)[j], (z0, z1)[l])
         for i in (0, 1) for j in (0, 1) for l in (0, 1)}
    put(B, [c[0, 0, 0], c[0, 1, 0], c[0, 1, 1], c[0, 0, 1]], kk("x0"), False)
    put(B, [c[1, 0, 0], c[1, 0, 1], c[1, 1, 1], c[1, 1, 0]], kk("x1"), False)
    put(B, [c[0, 0, 0], c[0, 0, 1], c[1, 0, 1], c[1, 0, 0]], kk("s0"), False)
    put(B, [c[0, 1, 0], c[1, 1, 0], c[1, 1, 1], c[0, 1, 1]], kk("s1"), False)
    put(B, [c[0, 0, 0], c[1, 0, 0], c[1, 1, 0], c[0, 1, 0]], kk("z0"), False)
    put(B, [c[0, 0, 1], c[0, 1, 1], c[1, 1, 1], c[1, 0, 1]], kk("z1"), False)
    return B


def xbox(x0, x1, s0, s1, z0, z1, k):
    """box() as its own object."""
    return obj(box(new(), min(x0, x1), max(x0, x1), s0, s1, z0, z1, k))


def mirrored(fn):
    """[fn(+1), fn(-1)]: a part and its mirror image."""
    return [fn(1), fn(-1)]


def prism(B, pts, axis, a0, a1, kside, kcap, smooth=False):
    """A prism along *axis* ('x', 's' or 'z') from a0 to a1 over the 2D
    outline *pts* (the other two coordinates in (x, s, z) order)."""
    def p3(q, a):
        if axis == "x":
            return P(a, q[0], q[1])
        if axis == "s":
            return P(q[0], a, q[1])
        return P(q[0], q[1], a)
    n = len(pts)
    for i in range(n):
        q0, q1 = pts[i], pts[(i + 1) % n]
        put(B, [p3(q0, a0), p3(q1, a0), p3(q1, a1), p3(q0, a1)], kside, smooth)
    put(B, [p3(q, a0) for q in pts], kcap, False)
    put(B, [p3(q, a1) for q in reversed(pts)], kcap, False)
    return B


def polygon(cx, cy, r, n, phase=0.0):
    return [(cx + r * math.cos(phase + 2 * math.pi * k / n),
             cy + r * math.sin(phase + 2 * math.pi * k / n)) for k in range(n)]


def obox(B, c, U, V_, N, hu, hv, d_in, d_out, cells, wall):
    """A cutter box on a host face: centre *c* (x, s, z) on the surface,
    unit axes U, V_ across it and N outward (in x, s, z); its floor, d_in
    under the surface, is split into *cells* [(a0, a1, b0, b1, K)] tiling
    [-hu, hu] x [-hv, hv]; walls and the outer lid are *wall*."""
    c, U, V_, N = (np.asarray(v, float) for v in (c, U, V_, N))

    def p(a, b, t):
        q = c + U * a + V_ * b + N * t
        return P(*q)
    for a0, a1, b0, b1, k in cells:
        put(B, [p(a0, b0, -d_in), p(a1, b0, -d_in), p(a1, b1, -d_in), p(a0, b1, -d_in)], k,
            False)
    corners = [(-hu, -hv), (hu, -hv), (hu, hv), (-hu, hv)]
    walls = wall if isinstance(wall, (list, tuple)) else [wall] * 4   # b0, a1, b1, a0
    put(B, [p(a, b, d_out) for a, b in corners], walls[0], False)
    for i in range(4):
        (a0, b0), (a1, b1) = corners[i], corners[(i + 1) % 4]
        put(B, [p(a0, b0, -d_in), p(a1, b1, -d_in), p(a1, b1, d_out), p(a0, b0, d_out)],
            walls[i], False)
    return B


def pocket(c, U, V_, N, hu, hv, depth, cells, wall, out=0.10):
    return obj(obox(new(), c, U, V_, N, hu, hv, depth, out, cells, wall))


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def loft(B, rings, band_kind, top=None, bottom=None, smooth=True):
    """Quads between closed rings [[(xyz, uv), ...], ...] of equal length;
    band_kind(i, j) -> (surface, paint) for the quad from ring i, point j.
    *top* and *bottom* (K) close the last and first rings."""
    n = len(rings[0])
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        for j in range(n):
            a, b, c, d = r0[j], r0[(j + 1) % n], r1[(j + 1) % n], r1[j]
            kind = band_kind(i, j)
            if isinstance(kind, K):          # mapped onto its own patch
                put(B, [a[0], b[0], c[0], d[0]], kind, False)
                continue
            surf, paint = kind
            put_uv(B, [a[0], b[0], c[0], d[0]], [a[1], b[1], c[1], d[1]], surf, paint, smooth)
    if top is not None:
        put(B, [q[0] for q in rings[-1]], top, False)
    if bottom is not None:
        put(B, [q[0] for q in reversed(rings[0])], bottom, False)
    return B


def full_ring(half):
    """A closed ring from its x >= 0 half (front centre .. back centre)."""
    return half + [(-q[0],) + tuple(q[1:]) for q in reversed(half[1:-1])]


# ================================================================ cab
def front_station(x, z):
    """The cab front's station at (x, z): the corner station from the
    rings, the bow across."""
    zs = [r[0] for r in L.CAB_RINGS]
    sf = float(np.interp(z, zs, [r[1] for r in L.CAB_RINGS]))
    xe = L.CAB_HW - L.CAB_RINGS[0][3]
    return L.bowed(x, sf, xe, L.CAB_BOW)


def bowed_cutter(z0, z1, hw, depth, nseg, rect, surface, wall):
    """A recess cut into the bowed front between z0 and z1, |x| <= hw: its
    floor follows the bow *depth* behind the surface in strips, each mapped
    across *rect* by x and z, tagged *surface*; walls *wall*."""
    xs = [-hw + 2 * hw * k / (2 * nseg) for k in range(2 * nseg + 1)]
    fx, fy, fw, fh = VB.patch_uv(L.REG[rect])

    def uv(co):
        x, _s, z = sw(co)
        return (fx + fw * (x + hw) / (2 * hw), fy + fh * (z - z0) / (z1 - z0))
    floor = K(uv=uv, surface=surface)
    B = new()

    def F(x, z):
        return P(x, front_station(x, z) + depth, z)

    def O(x, z):
        return P(x, front_station(x, z) - 0.10, z)
    for a, b in zip(xs, xs[1:]):
        put(B, [F(a, z0), F(b, z0), F(b, z1), F(a, z1)], floor, False)
        put(B, [O(a, z0), O(a, z1), O(b, z1), O(b, z0)], wall, False)
    for x in (-hw, hw):
        put(B, [F(x, z0), F(x, z1), O(x, z1), O(x, z0)], wall, False)
    for z in (z0, z1):
        put(B, [F(x, z) for x in xs] + [O(x, z) for x in reversed(xs)], wall, False)
    return obj(B, "bowcut")


def cab_rings(level):
    """Rings, front arc segments, rear arc segments, bowed front segments."""
    if level == 0:
        return L.CAB_RINGS, 4, 2, 3
    if level == 1:
        keep = (0.80, 1.10, 1.60, 2.55, 2.75)
        return [r for r in L.CAB_RINGS if r[0] in keep], 2, 1, 1
    keep = (0.80, 1.60, 2.55, 2.75)
    return [r for r in L.CAB_RINGS if r[0] in keep], 1, 0, 1


def cab_shell(level):
    rings_p, nf, nb, nbow = cab_rings(level)
    rings = []
    for r in rings_p:
        z = r[0]
        v = L.cab_v(z)
        rings.append([(P(x, s, z), L.cab_band_px(u, v)) for x, s, u in
                      full_ring(L.ring_half(r, nf, nb, nbow))])
    zs = [r[0] for r in rings_p]

    def kind(i, j):
        if level == 2 and zs[i] == 1.60 and (j < nbow or j >= len(rings[0]) - nbow):
            return K("glass_ws", surface=32)   # LOD2: the screen is the whole front face
        n = len(rings[0])
        front = max(rings[i][j][0][1], rings[i][(j + 1) % n][0][1]) + L.HL < 0.27
        return 0, zs[i] >= L.Z_DOOR or level == 2 or front
    B = new()
    loft(B, rings, kind, top=K(uv=uv_cab_roof, paint=True), bottom=DARK)
    return obj(B, "cab")


def cab_cutters(level):
    """Arches, step wells, screen, door glass, grille and repeaters."""
    out = []
    sc, zc, ra, xin = L.ARCH
    n = 12 if level == 0 else 4
    arc = [(sc - ra * math.cos(math.pi * k / n), zc + ra * math.sin(math.pi * k / n))
           for k in range(n + 1)]
    prof = arc + [(sc + ra, 0.30), (sc - ra, 0.30)]
    for sgn in (1, -1):
        B = new()
        a0, a1 = sorted((sgn * xin, sgn * 1.40))
        prism(B, prof, "x", a0, a1, LINER, LINER)
        out.append(obj(B, "arch"))
    # screen and grille, recessed into the bowed front
    nseg = 3 if level == 0 else 1
    wh, wz0, wz1 = L.WSCREEN
    out.append(bowed_cutter(wz0, wz1, wh, 0.03, nseg, "glass_ws", 32, SEAL))
    if level == 0:          # LOD1 keeps the grille in the band's texture
        gh, gz0, gz1 = L.GRILLE
        out.append(bowed_cutter(gz0, gz1, gh, 0.035, nseg, "grille", 0, PLASTIC))
    g0, g1, gz0_, gz1_ = L.DOOR_GLASS
    r0, r1, rz0, rz1 = L.REPEATER
    for sgn in (1, -1):
        c = (sgn * L.CAB_HW, (g0 + g1) / 2, (gz0_ + gz1_) / 2)
        hu, hv_ = (g1 - g0) / 2, (gz1_ - gz0_) / 2
        out.append(pocket(c, (0, 1, 0), (0, 0, 1), (sgn, 0, 0), hu, hv_, 0.02,
                          [(-hu, hu, -hv_, hv_, K("glass_side", surface=33))], SEAL))
        c = (sgn * L.CAB_HW, (r0 + r1) / 2, (rz0 + rz1) / 2)
        hu, hv_ = (r1 - r0) / 2, (rz1 - rz0) / 2
        out.append(pocket(c, (0, 1, 0), (0, 0, 1), (sgn, 0, 0), hu, hv_, 0.012,
                          [(-hu, hu, -hv_, hv_, lamp(4 if sgn > 0 else 5))], HOUSING))
        if level == 0:
            s0, s1, z0, z1, d = L.STEP_UP
            c = (sgn * L.CAB_HW, (s0 + s1) / 2, (z0 + z1) / 2)
            hu, hv_ = (s1 - s0) / 2, (z1 - z0) / 2
            out.append(pocket(c, (0, 1, 0), (0, 0, 1), (sgn, 0, 0), hu, hv_, d,
                              [(-hu, hu, -hv_, hv_, PLASTIC)], [STEP, LINER, LINER, LINER]))
    return out


# ================================================================ tiling
def tile_face(B, to3d, u0, u1, v0, v1, cells, base):
    """A planar rectangle u0..u1 x v0..v1 (to3d(u, v) -> point) tiled by
    *cells* [(a0, a1, b0, b1, K or None)], the first that holds a grid cell
    winning, and *base* elsewhere; None leaves a hole. A grid on every cell
    edge, merged along each row where the kind repeats."""
    us = sorted({u0, u1} | {c[0] for c in cells} | {c[1] for c in cells})
    vs = sorted({v0, v1} | {c[2] for c in cells} | {c[3] for c in cells})
    us = [u for u in us if u0 <= u <= u1]
    vs = [v for v in vs if v0 <= v <= v1]

    def emit(run, va, vb):
        if run is not None and run[2] is not None:
            put(B, [to3d(run[0], va), to3d(run[1], va), to3d(run[1], vb), to3d(run[0], vb)],
                run[2], False)
    for va, vb in zip(vs, vs[1:]):
        run = None
        for ua, ub in zip(us, us[1:]):
            k = next((c[4] for c in cells if c[0] <= ua and ub <= c[1] and c[2] <= va
                      and vb <= c[3]), base)
            if run is not None and run[2] is k:
                run[1] = ub
                continue
            emit(run, va, vb)
            run = [ua, ub, k]
        emit(run, va, vb)


def tiled_box(x0, x1, s0, s1, z0, z1, front=(), rear=(), base=DARK, front_base=None,
              rear_base=None):
    """A box whose front (s0) and rear (s1) faces are tiled with cells in
    (x, z)."""
    B = new()
    tile_face(B, lambda u, v: P(u, s0, v), x0, x1, z0, z1, list(front), front_base or base)
    tile_face(B, lambda u, v: P(u, s1, v), x0, x1, z0, z1, list(rear), rear_base or base)
    for x in (x0, x1):
        put(B, [P(x, s0, z0), P(x, s1, z0), P(x, s1, z1), P(x, s0, z1)], base, False)
    put(B, [P(x0, s0, z0), P(x1, s0, z0), P(x1, s1, z0), P(x0, s1, z0)], base, False)
    put(B, [P(x0, s0, z1), P(x1, s0, z1), P(x1, s1, z1), P(x0, s1, z1)], base, False)
    return obj(B, "tiled")


# ================================================================ bumper
def headlamp_cells(sgn):
    """Cells of one headlamp unit in its pocket's (a, b): a outward from
    the unit's centre, b up from its middle. A dark housing frame 20 mm
    wide round the indicator, the low and high beam reflectors and the
    daytime strip under them."""
    xi, xo, z0, z1 = L.HEADLAMP
    xc, zc = (xi + xo) / 2, (z0 + z1) / 2
    ind = 4 if sgn > 0 else 5
    b = 0.02
    zd = 0.645
    A = lambda x: x - xc            # noqa: E731
    Z = lambda z: z - zc            # noqa: E731
    return xc, zc, (xo - xi) / 2, (z1 - z0) / 2, [
        (A(0.90), A(xo - b), Z(z0 + b), Z(z1 - b), lamp(ind)),
        (A(0.76), A(0.90), Z(zd), Z(z1 - b), lamp(7)),
        (A(xi + b), A(0.76), Z(zd), Z(z1 - b), lamp(8)),
        (A(xi + b), A(0.90), Z(z0 + b), Z(zd), lamp(9)),
        (A(xi), A(xo), Z(z0), Z(z0 + b), HOUSING),
        (A(xi), A(xo), Z(z1 - b), Z(z1), HOUSING),
        (A(xi), A(xi + b), Z(z0 + b), Z(z1 - b), HOUSING),
        (A(xo - b), A(xo), Z(z0 + b), Z(z1 - b), HOUSING),
    ]


def bumper_front_cells(drl=True):
    """(x0, x1, z0, z1, K) cells on the bumper's front face, both lamps."""
    out = []
    for sgn in (1, -1):
        xc, zc, hu, hv, cells = headlamp_cells(sgn)
        for a0, a1, b0, b1, k in cells:
            if k.surface == 0 or (not drl and k.surface == 9):
                continue
            xs = sorted((sgn * (xc + a0), sgn * (xc + a1)))
            out.append((xs[0], xs[1], zc + b0, zc + b1, k))
    return out


def bumper(level):
    z1 = L.BUMPER_RINGS[-1][0]
    if level >= 1:
        cells = bumper_front_cells(drl=True)
        if level == 1:
            ph, pz0, pz1 = L.PLATE_F
            cells.append((-ph, ph, pz0, pz1, K("plate")))
        return tiled_box(-L.BUMPER_HW, L.BUMPER_HW, 0.0, L.BUMPER_D, 0.40, z1, front=cells,
                         base=PLASTIC, front_base=K(uv=uv_bumper_front))
    rings = []
    for z, sf in L.BUMPER_RINGS:
        v = float(np.interp(z, [r[0] for r in L.BUMPER_RINGS], L.BUMPER_V))
        rings.append([(P(x, s, z), L.at("bumper", u, v)) for x, s, u in
                      full_ring(L.bumper_half(sf, 3))])
    B = new()
    loft(B, rings, lambda i, j: (0, False), top=PLASTIC, bottom=PLASTIC)
    cut = []
    for sgn in (1, -1):
        xc, zc, hu, hv, cells = headlamp_cells(sgn)
        sc = L.bowed(xc, L.BUMPER_RINGS[1][1], L.BUMPER_HW - L.BUMPER_R, L.BUMPER_BOW)
        cut.append(pocket((sgn * xc, sc, zc), (sgn, 0, 0), (0, 0, 1), (0, -1, 0), hu, hv,
                          0.026, cells, HOUSING))
    ph, pz0, pz1 = L.PLATE_F
    hv = (pz1 - pz0) / 2
    cut.append(pocket((0.0, 0.0, (pz0 + pz1) / 2), (1, 0, 0), (0, 0, 1), (0, -1, 0), ph, hv,
                      0.006, [(-ph, ph, -hv, hv, K("plate"))], PLASTIC))
    return asset_build.difference(obj(B, "bumper"), cut, snap=asset_build.SNAP)


def carriers(level):
    s0, s1, x0, x1, z0, z1 = L.CARRIER
    out = []
    for sgn in (1, -1):
        o = xbox(sgn * x0, sgn * x1, s0, s1, z0, z1, PLASTIC)
        if level == 0:
            a0, a1, b0, b1, d = L.STEP_LO
            c = (sgn * x1, (a0 + a1) / 2, (b0 + b1) / 2)
            hu, hv = (a1 - a0) / 2, (b1 - b0) / 2
            o = asset_build.difference(o, [pocket(c, (0, 1, 0), (0, 0, 1), (sgn, 0, 0), hu, hv,
                                                  d, [(-hu, hu, -hv, hv, STEP)], STEP)],
                                       snap=asset_build.SNAP)
        out.append(o)
    return out


# ================================================================ deflector
def deflector(level):
    if level == 2:
        st, vs = [L.DEFL[0], L.DEFL[-1]], [L.DEFL_V[0], L.DEFL_V[-1]]
        rings = []
        for (s, h, wb, wt), v in zip(st, vs):
            half = [(0.0, h, 0.0), (wt, h, wt), (wb, L.DEFL_Z0, wt + h - L.DEFL_Z0),
                    (0.0, L.DEFL_Z0, wt + wb + h - L.DEFL_Z0)]
            rings.append([(P(x, s, z), L.at("defl", u, v)) for x, z, u in full_ring(half)])
        B = new()
        loft(B, rings, lambda i, j: (0, True), top=PAINT_CAB, bottom=PAINT_CAB)
        return [obj(B, "defl")]
    st = L.DEFL if level == 0 else [L.DEFL[0], L.DEFL[2], L.DEFL[4]]
    nc = 3 if level == 0 else 1
    vs = L.DEFL_V if level == 0 else [L.DEFL_V[0], L.DEFL_V[2], L.DEFL_V[4]]
    rings = []
    for (s, h, wb, wt), v in zip(st, vs):
        half = L.defl_half((s, h, wb, wt), nc)
        rings.append([(P(x, s, z), L.at("defl", u, v)) for x, z, u in full_ring(half)])
    B = new()
    loft(B, rings, lambda i, j: (0, True), top=PAINT_CAB, bottom=PAINT_CAB)
    out = [obj(B, "defl")]
    s0, s1, x0, x1, z0, z1 = L.FLAP
    for sgn in (1, -1):
        out.append(xbox(sgn * x0, sgn * x1, s0, s1, z0, z1, PAINT_CAB))
    return out


def cab_group(level):
    cab = asset_build.difference(cab_shell(level), cab_cutters(level), snap=asset_build.SNAP)
    return asset_build.union(cab, deflector(level) + cab_addons(level), snap=asset_build.SNAP)


def cab_addons(level):
    """The sun visor over the screen; at LOD0 the black fender lips round
    the front arches."""
    out = []
    B = new()
    prism(B, [(0.30, 2.665), (0.03, 2.59), (0.03, 2.56), (0.30, 2.635)], "x", -1.0, 1.0,
          PLASTIC, PLASTIC)
    out.append(obj(B, "visor"))
    if level == 0:
        sc, zc, ra, _xin = L.ARCH
        r0, r1, n = 0.615, 0.71, 8
        t0, t1 = math.radians(25.0), math.radians(122.0)
        ang = [t0 + (t1 - t0) * k / n for k in range(n + 1)]
        outer = [(sc - r1 * math.cos(a), zc + r1 * math.sin(a)) for a in ang]
        inner = [(sc - r0 * math.cos(a), zc + r0 * math.sin(a)) for a in reversed(ang)]
        for sgn in (1, -1):
            B = new()
            a0, a1 = sorted((sgn * 1.12, sgn * 1.175))
            prism(B, outer + inner, "x", a0, a1, PLASTIC, PLASTIC, smooth=True)
            out.append(obj(B, "flare"))
    return out


def wipers():
    """Two parked wiper arms lying 2 mm off the recessed, bowed screen
    (LOD0): straight bars along a chord of the bow, set forward by its
    sagitta."""
    nrm = unit((0.0, -(L.CAB_RINGS[4][0] - L.CAB_RINGS[3][0]),
                L.CAB_RINGS[4][1] - L.CAB_RINGS[3][1]))
    xe = L.CAB_HW - L.CAB_RINGS[0][3]
    out = []
    for a0, a1, z0, z1 in ((-0.84, -0.12, 1.70, 1.76), (0.04, 0.76, 1.70, 1.76)):
        f0 = np.array((a0, front_station(a0, z0) + 0.03, z0))
        f1 = np.array((a1, front_station(a1, z1) + 0.03, z1))
        sag = L.CAB_BOW / xe ** 2 * ((a1 - a0) / 2) ** 2
        U = unit(f1 - f0)
        V_ = unit(np.cross(nrm, U))
        ctr = (f0 + f1) / 2 + np.asarray(nrm) * (sag + 0.008)
        hu = float(np.linalg.norm(f1 - f0)) / 2
        B = new()
        obox(B, ctr, U, V_, nrm, hu, 0.011, 0.006, 0.006, [(-hu, hu, -0.011, 0.011, MBODY)],
             MBODY)
        out.append(obj(B, "wiper"))
    return out


# ================================================================ box
def box_shell(level):
    """The box as one closed solid: aluminium rails and corner posts
    proud of side panels set in 12 mm (LOD0), marker lamps as cells on the
    rails, the roller door set in behind the rear frame (LOD0)."""
    hw, pw = L.BOX_HW, L.PANEL_HW
    s0, s1, z0, z1 = L.BOX_S0, L.BOX_S1, L.BOX_Z0, L.BOX_Z1
    r0, r1 = L.RAIL_LO[1], L.RAIL_HI[0]
    p0, p1 = s0 + L.POST_F, s1 - L.REAR_FRAME
    rail, panel = K(uv=uv_rail), K(uv=uv_box_side, paint=True)
    w, mz0, mz1 = L.MARK_SIDE
    B = new()
    for sgn in (1, -1):
        X = sgn * hw

        def f(u, v, X=X):
            return P(X, u, v)
        marks = [(s - w / 2, s + w / 2, mz0, mz1, lamp(15, "amber")) for s in L.MARK_SIDE_S]
        frame = marks + [(s0, s1, z0, r0, rail), (s0, s1, r1, z1, ALU)]
        if level == 0:
            frame += [(s0, p0, r0, r1, ALU), (p1, s1, r0, r1, ALU)]
        if level == 0:
            frame.append((p0, p1, r0, r1, None))
            tile_face(B, f, s0, s1, z0, z1, frame, panel)
            Xi = sgn * pw
            ring = [(p0, r0), (p1, r0), (p1, r1), (p0, r1)]
            for i in range(4):
                (a0, b0), (a1, b1) = ring[i], ring[(i + 1) % 4]
                put(B, [P(X, a0, b0), P(X, a1, b1), P(Xi, a1, b1), P(Xi, a0, b0)], ALU, False)
            put(B, [P(Xi, a, b) for a, b in ring], panel, False)
        else:
            tile_face(B, f, s0, s1, z0, z1, frame, panel)
    x0, x1 = L.MARK_END
    fz, rz = L.MARK_FRONT_Z, L.MARK_REAR_Z
    tile_face(B, lambda u, v: P(u, s0, v), -hw, hw, z0, z1,
              [(x0, x1, fz[0], fz[1], lamp(15, "white")),
               (-x1, -x0, fz[0], fz[1], lamp(15, "white"))], K(uv=uv_box_front, paint=True))
    rcells = [(x0, x1, rz[0], rz[1], lamp(15, "red")), (-x1, -x0, rz[0], rz[1], lamp(15, "red"))]
    rp, d0, d1 = L.REAR_POST_HW, L.SILL_Z, L.HEADER_Z
    if level == 0:
        rcells.append((-rp, rp, d0, d1, None))
    tile_face(B, lambda u, v: P(u, s1, v), -hw, hw, z0, z1, rcells, K(uv=uv_box_rear))
    if level == 0:
        ring = [(-rp, d0), (rp, d0), (rp, d1), (-rp, d1)]
        sd = L.DOOR_FACE
        for i in range(4):
            (a0, b0), (a1, b1) = ring[i], ring[(i + 1) % 4]
            put(B, [P(a0, s1, b0), P(a1, s1, b1), P(a1, sd, b1), P(a0, sd, b0)], ALU, False)
        put(B, [P(a, sd, b) for a, b in ring], K(uv=uv_box_rear), False)
    put(B, [P(-hw, s0, z1), P(-hw, s1, z1), P(hw, s1, z1), P(hw, s0, z1)], K(uv=uv_box_roof),
        False)
    put(B, [P(-hw, s0, z0), P(hw, s0, z0), P(hw, s1, z0), P(-hw, s1, z0)], DARK, False)
    return obj(B, "box")


# ================================================================ chassis
G = 0.002                                 # the gap that keeps solids apart


def chassis(level):
    """The running gear and everything under the box, as closed solids
    that touch nothing (2 mm gaps where they would meet)."""
    out = []
    rx0, rx1 = L.RAIL_X
    zt = L.RAIL_Z[1]
    for sgn in (1, -1):
        if level >= 1:                    # rail and subframe as one member
            out.append(xbox(sgn * rx0, sgn * rx1, 1.83, 7.80, L.RAIL_Z[0], 1.072, DARK))
            continue
        out.append(xbox(sgn * rx0, sgn * rx1, 1.83, 7.80, *L.RAIL_Z, DARK))
        out.append(xbox(sgn * L.SUB_X[0], sgn * L.SUB_X[1], 1.92, 7.80, zt + G, 1.072, DARK))
    out.append(xbox(-0.34, 0.34, 0.40, 2.40, 0.48, 0.80 - 0.005, DARK))     # engine, gearbox
    if level == 0:
        out.append(xbox(-0.72, 0.72, 1.36, 1.44, 0.40, 0.47, DARK))         # front axle beam
    if level == 0:
        for s in (2.45, 3.15, 3.85, 4.55, 5.05, 6.75, 7.40):
            out.append(xbox(-1.20, 1.20, s - 0.03, s + 0.03, 1.075, L.BOX_Z0 - G, DARK))
    # fuel tank, left, on straps from the rail
    s0, s1, xc, zc, r = L.TANK
    n = 12 if level == 0 else 6
    B = new()
    prism(B, polygon(xc, zc, r, n, math.pi / n), "s", s0, s1, TANK, TANK)
    out.append(obj(B, "tank"))
    flat = xc - r * math.cos(math.pi / n)
    for a, b in ((2.20, 2.27), (2.73, 2.80)) if level == 0 else ((2.45, 2.55),):
        out.append(xbox(rx1 + G, flat - G, a, b, 0.78, 0.90, DARK))
    # battery box, right
    s0, s1, x0, x1, z0, z1 = L.BATTERY
    out.append(xbox(-x1, -x0, s0, s1, z0, z1, {"all": DARK, "z1": PLASTIC}))
    out.append(xbox(-(x0 - G), -(rx1 + G), 2.30, 2.40, 0.80, 0.90, DARK))
    if level == 0:
        # AdBlue tank left; an air tank and a silencer right
        out.append(xbox(0.48, 0.82, 3.05, 3.40, 0.55, 0.92, PLASTIC))
        out.append(xbox(rx1 + G, 0.48 - G, 3.18, 3.26, 0.80, 0.90, DARK))
        B = new()
        prism(B, polygon(-0.62, 0.80, 0.11, 6, math.pi / 6), "s", 3.00, 3.90, DARK, DARK)
        out.append(obj(B, "air"))
        out.append(xbox(-(0.62 - 0.11 * math.cos(math.pi / 6) - G), -(rx1 + G), 3.40, 3.46,
                        0.76, 0.84, DARK))
        out.append(xbox(-0.95, -0.50, 4.10, 4.75, 0.62, 0.92, DARK))
        out.append(xbox(-(0.50 - G), -(rx1 + G), 4.40, 4.48, 0.82, 0.90, DARK))
    # side guards on brackets
    g0, g1 = L.GUARD_S
    gx0, gx1 = L.GUARD_X
    for sgn in (1, -1):
        for z0, z1 in L.GUARD_Z:
            out.append(xbox(sgn * gx0, sgn * gx1, g0, g1, z0, z1, GUARD))
        for s in (L.GUARD_BRACKETS if level == 0 else L.GUARD_BRACKETS[::2]):
            out.append(xbox(sgn * 1.13, sgn * (gx0 - G), s - 0.03, s + 0.03,
                            L.GUARD_Z[0][0], L.BOX_Z0 - G, DARK))
    # rear under-run bar, its brackets, the lamp housings
    b0, b1, bh, bz0, bz1 = L.BAR
    ph, pz0, pz1 = L.PLATE_R
    if level == 0:
        bar = xbox(-bh, bh, b0, b1, bz0, bz1, GUARD)
        hv = (pz1 - pz0) / 2
        bar = asset_build.difference(bar, [pocket((0.0, b1, (pz0 + pz1) / 2), (-1, 0, 0),
                                                  (0, 0, 1), (0, 1, 0), ph, hv, 0.006,
                                                  [(-ph, ph, -hv, hv, K("plate"))], GUARD)],
                                     snap=asset_build.SNAP)
    else:
        bar = tiled_box(-bh, bh, b0, b1, bz0, bz1, rear=[(-ph, ph, pz0, pz1, K("plate"))],
                        base=GUARD)
    out.append(bar)
    for sgn in (1, -1):
        out.append(xbox(sgn * 0.36, sgn * 0.44, 7.68, 7.76, bz1 + G, L.RAIL_Z[0] - G, DARK))
        out.append(rear_lamp(sgn, level))
    # mudguards and flaps over the twins
    m0, m1, mx0, mx1, mz0, mz1 = L.MUDGUARD
    prof = [(m0, 0.86), (m0, mz1), (m1, mz1), (m1, 0.50), (m1 - 0.04, 0.50),
            (m1 - 0.04, mz0), (m0 + 0.04, mz0), (m0 + 0.04, 0.86)]
    for sgn in (1, -1):
        if level >= 1:
            # a flat guard and one rubber lip and flap behind it
            out.append(xbox(sgn * mx0, sgn * mx1, m0, m1 - 0.04 - G, mz0, mz1, PLASTIC))
            out.append(xbox(sgn * mx0, sgn * mx1, m1 - 0.04, m1, 0.25, mz1, RUBBER))
            continue
        B = new()
        a0, a1 = sorted((sgn * mx0, sgn * mx1))
        prism(B, prof, "x", a0, a1, PLASTIC, PLASTIC)
        out.append(obj(B, "mudguard"))
        out.append(xbox(sgn * 0.62, sgn * 1.24, m1 + G, m1 + 0.02, 0.25, 0.62, RUBBER))
        out.append(xbox(sgn * (L.SUB_X[1] + G), sgn * (mx0 - G), 5.88, 5.94, 1.075, 1.105,
                        DARK))
    # rear axle housings and differential
    zc = L.R_WHEEL
    if level == 0:
        for sgn in (1, -1):
            B = new()
            a0, a1 = sorted((sgn * 0.172, sgn * 0.585))
            prism(B, polygon(5.90, zc, 0.085, 8, math.pi / 8), "x", a0, a1, DARK, DARK)
            out.append(obj(B, "axle"))
        out.append(xbox(-0.17, 0.17, 5.74, 6.06, 0.38, 0.66, DARK))
    else:
        B = new()
        prism(B, polygon(5.90, zc, 0.085, 6, math.pi / 6), "x", -0.585, 0.585, DARK, DARK)
        out.append(obj(B, "axle"))
    return out


def rear_lamp(sgn, level):
    s0, s1, x0, x1, z0, z1 = L.REAR_LAMP
    lz0, lz1 = L.REAR_LENS_Z
    z0 += G
    if level >= 1:
        cells = []
        for xo, xi, kind in (L.REAR_CELLS_L if sgn > 0 else L.REAR_CELLS_R):
            if kind == "housing":
                continue
            xs = sorted((sgn * xo, sgn * xi))
            cells.append((xs[0], xs[1], lz0, lz1, lamp(kind)))
        a, b = sorted((sgn * x0, sgn * x1))
        return tiled_box(a, b, s0, s1, z0, z1, rear=cells, base=HOUSING)
    o = xbox(sgn * x0, sgn * x1, s0, s1, z0, z1, HOUSING)
    xc, zc = (x0 + x1) / 2, (lz0 + lz1) / 2
    hu, hv = (x1 - x0) / 2, (lz1 - lz0) / 2
    cells = []
    for xo, xi, kind in (L.REAR_CELLS_L if sgn > 0 else L.REAR_CELLS_R):
        k = HOUSING if kind == "housing" else lamp(kind)
        cells.append((xi - xc, xo - xc, -hv, hv, k))
    cut = pocket((sgn * xc, s1, zc), (sgn, 0, 0), (0, 0, 1), (0, 1, 0), hu, hv, 0.02, cells,
                 HOUSING)
    return asset_build.difference(o, [cut], snap=asset_build.SNAP)


# ================================================================ mirrors
def mirror(sgn, level):
    def X(a, b):
        return sorted((sgn * a, sgn * b))
    parts = []
    if level >= 1:
        # one arm into the head, one head holding both mirrors
        a, b = X(1.153, 1.385)
        parts.append(xbox(a, b, 0.40, 0.43, 2.385, 2.415, MBODY))
        a, b = X(1.30, 1.48)
        parts.append(xbox(a, b, 0.425, 0.495, 1.80, 2.36, {"all": MBODY, "s1": MGLASS}))
        return asset_build.union(parts[0], parts[1:], snap=asset_build.SNAP)
    a, b = X(1.153, 1.385)
    parts.append(xbox(a, b, 0.40, 0.43, 2.385, 2.415, MBODY))
    parts.append(xbox(a, b, 0.402, 0.438, 1.83, 1.86, MBODY))
    a, b = X(1.37, 1.40)
    parts.append(xbox(a, b, 0.40, 0.44, 1.83, 2.415, MBODY))
    for x0, x1, s0, s1, z0, z1 in ((1.29, 1.49, 0.425, 0.50, 1.98, 2.36),
                                   (1.31, 1.47, 0.425, 0.49, 1.80, 1.95)):
        a, b = X(x0, x1)
        parts.append(head(a, b, s0, s1, z0, z1))
    return asset_build.union(parts[0], parts[1:], snap=asset_build.SNAP)


def head(x0, x1, s0, s1, z0, z1, c=0.02):
    """A mirror head: a box chamfered round its front, the glass at the back."""
    B = new()
    rear = [P(x0, s1, z0), P(x1, s1, z0), P(x1, s1, z1), P(x0, s1, z1)]
    mid = [P(x0, s0 + c, z0), P(x1, s0 + c, z0), P(x1, s0 + c, z1), P(x0, s0 + c, z1)]
    front = [P(x0 + c, s0, z0 + c), P(x1 - c, s0, z0 + c), P(x1 - c, s0, z1 - c),
             P(x0 + c, s0, z1 - c)]
    put(B, rear, MGLASS, False)
    put(B, list(reversed(front)), MBODY, False)
    for i in range(4):
        j = (i + 1) % 4
        put(B, [rear[i], mid[i], mid[j], rear[j]], MBODY, False)
        put(B, [mid[i], front[i], front[j], mid[j]], MBODY, True)
    return obj(B, "head")


# ================================================================ wheels
def wheel(level, front, outward, half=None):
    """A revolved closed wheel about its own centre, axis along X: a profile
    of (x outward, r) from the inner cap to the outer cap; the tyre's tread
    rows map round the tread strip, everything else onto the face disc."""
    R = L.R_WHEEL
    if level == 0:
        sides = 20
        prof = ([(-0.15, 0.49), (-0.12, R), (0.12, R), (0.15, 0.49), (0.15, 0.30),
                 (0.125, 0.285), (0.125, 0.15), (0.15, 0.10)] if front else
                [(-0.32, 0.49), (-0.29, R), (-0.025, R), (0.0, 0.49), (0.025, R), (0.29, R),
                 (0.32, 0.49), (0.32, 0.30), (0.25, 0.285), (0.25, 0.15), (0.30, 0.11)])
    elif level == 1:
        sides = 10
        prof = ([(-0.15, R), (0.15, R), (0.15, 0.29), (0.125, 0.12)] if front else
                [(-0.32, R), (0.32, R), (0.32, 0.29), (0.26, 0.12)])
    else:
        sides = 6
        hw = half or (L.FRONT_W if front else L.REAR_W) / 2
        prof = [(-hw, R), (hw, R)]
    tread = L.REG["tread_f" if front else "tread_r"]
    disc = L.REG["wheel_f" if front else "wheel_r"]
    hw = max(abs(p[0]) for p in prof)
    tx, ty, tw, th = VB.patch_uv(tread)
    dx, dy, dw, dh = disc
    dppm = (dw - 2 * L.PAD) / (2 * R)
    dcx, dcy = dx + dw / 2.0, dy + dh / 2.0
    ang = [-math.pi / 2 + 2 * math.pi * k / sides for k in range(sides)]

    def pt(i, k):
        x, r = prof[i]
        return (x * outward, r * math.cos(ang[k]), r * math.sin(ang[k]))

    def duv(co):
        return (dcx + co[1] * dppm * outward, dcy + co[2] * dppm)
    B = new()
    for i in range(len(prof) - 1):
        is_tread = prof[i][1] >= 0.485 and prof[i + 1][1] >= 0.485
        for k in range(sides):
            k1 = (k + 1) % sides
            cos = [pt(i, k), pt(i + 1, k), pt(i + 1, k1), pt(i, k1)]
            if is_tread:
                def tv(i_):
                    return ty + th * (prof[i_][0] + hw) / (2 * hw)
                u0, u1 = tx + tw * k / sides, tx + tw * (k + 1) / sides
                put_uv(B, cos, [(u0, tv(i)), (u0, tv(i + 1)), (u1, tv(i + 1)), (u1, tv(i))])
            else:
                B.face(cos, duv, smooth=True)
    B.face([pt(0, k) for k in reversed(range(sides))], duv)
    B.face([pt(len(prof) - 1, k) for k in range(sides)], duv)
    return B


def wheel_pieces(level):
    out = []
    for part, x, s, wdt, steer, twin in L.WHEELS:
        o = finish(obj(wheel(level, not twin, 1 if x > 0 else -1), "wheel"),
                   40.0 if level == 0 else 50.0)
        out.append(VB.Piece("wheel", o, part=part, centre=P(x, s, L.R_WHEEL), steer=steer,
                            twin=twin))
    return out


def wheel_body(x, s, twin, half=None):
    o = obj(wheel(2, not twin, 1 if x >= 0 else -1, half), "wheel")
    for v in o.data.vertices:
        v.co.x += x
        v.co.y += Y(s)
        v.co.z += L.R_WHEEL
    return o


# ================================================================ finishing
def finish(o, angle):
    """Every face smooth; edges over *angle* degrees sharp; normals weighted
    toward the big faces, so flat panels shade flat and the rounded corners
    blend into them."""
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges[:])
    lim = math.radians(angle)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        e.smooth = not (len(e.link_faces) == 2 and e.calc_face_angle(0.0) > lim)
    bm.to_mesh(me)
    bm.free()
    scn = bpy.context.scene
    scn.collection.objects.link(o)
    mod = o.modifiers.new("wn", 'WEIGHTED_NORMAL')
    mod.mode = 'FACE_AREA'
    mod.weight = 50
    mod.keep_sharp = True
    dg = bpy.context.evaluated_depsgraph_get()
    new_me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    o.modifiers.clear()
    old = o.data
    o.data = new_me
    bpy.data.meshes.remove(old)
    scn.collection.objects.unlink(o)
    return o


# ================================================================ tiers
def box_lod2():
    hw = L.BOX_HW
    s0, s1, z0, z1 = L.BOX_S0, L.BOX_S1, L.BOX_Z0, L.BOX_Z1
    B = new()
    rail, panel = K(uv=uv_rail), K(uv=uv_box_side, paint=True)
    for sgn in (1, -1):
        tile_face(B, lambda u, v, sgn=sgn: P(sgn * hw, u, v), s0, s1, z0, z1,
                  [(s0, s1, z0, L.RAIL_LO[1], rail)], panel)
    x0, x1 = L.MARK_END
    rz = L.MARK_REAR_Z
    put(B, [P(-hw, s0, z0), P(-hw, s0, z1), P(hw, s0, z1), P(hw, s0, z0)],
        K(uv=uv_box_front, paint=True), False)
    tile_face(B, lambda u, v: P(u, s1, v), -hw, hw, z0, z1,
              [(x0, x1, rz[0], rz[1], lamp(15, "red")),
               (-x1, -x0, rz[0], rz[1], lamp(15, "red"))], K(uv=uv_box_rear))
    put(B, [P(-hw, s0, z1), P(-hw, s1, z1), P(hw, s1, z1), P(hw, s0, z1)], K(uv=uv_box_roof),
        False)
    put(B, [P(-hw, s0, z0), P(hw, s0, z0), P(hw, s1, z0), P(-hw, s1, z0)], DARK, False)
    return obj(B, "box2")


def lod2_parts():
    B = new()
    prism(B, [(0.30, 2.665), (0.03, 2.59), (0.03, 2.56), (0.30, 2.635)], "x", -1.0, 1.0,
          PLASTIC, PLASTIC)
    parts = [cab_shell(2), bumper(2), obj(B, "visor")] + deflector(2) + [box_lod2()]
    parts.append(xbox(-0.95, 0.95, 1.83, 7.64, 0.48, L.BOX_Z0 - G, DARK))
    # the under-run bar and the two lamp housings above its ends
    b0, b1, bh, bz0, bz1 = L.BAR
    parts.append(xbox(-bh, bh, b0, b1, bz0, bz1, GUARD))
    s0, s1, x0, x1, z0, z1 = L.REAR_LAMP
    lz0, lz1 = L.REAR_LENS_Z
    for sgn, row in ((1, L.REAR_CELLS_L), (-1, L.REAR_CELLS_R)):
        cells = []
        for xo, xi, kind in row:
            if kind != "housing" and not (sgn < 0 and kind == 6):   # one reverse lens
                xs = sorted((sgn * xo, sgn * xi))
                cells.append((xs[0], xs[1], lz0, lz1, lamp(kind)))
        a, b = sorted((sgn * x0, sgn * x1))
        parts.append(tiled_box(a, b, s0, s1, z0 + G, z1, rear=cells, base=HOUSING))
    # front wheels apart; the rear twins one prism across the axle, its
    # middle inside the dark under-box mass
    for part, x, s, wdt, steer, twin in L.WHEELS:
        if not twin:
            parts.append(wheel_body(x, s, twin))
    parts.append(wheel_body(0.0, L.REAR_AXLE, True, half=L.REAR_X + L.REAR_W / 2))
    return parts


def body_lod3():
    """Two extruded side profiles: the painted cab and box (a chamfered
    nose, the deflector and box front as one slope, the roof) and, a little
    narrower, the dark unpainted under-body on four wheel feet. 28 + 32
    triangles."""
    hw = L.BOX_HW
    upper = [(0.0, 0.80), (0.05, 2.45), (0.30, 2.75), (0.75, 2.75), (1.90, 3.70),
             (7.90, 3.70), (7.90, 1.15), (1.90, 1.15)]
    lower = [(0.0, 0.79), (1.05, 0.0), (1.75, 0.0), (1.95, 0.45), (5.30, 0.45),
             (5.50, 0.0), (6.30, 0.0), (7.84, 0.45), (7.84, 1.13)]
    out = []
    for prof, w, kinds, side in (
            (upper, hw, [K(uv=uv_lod3_front, paint=True)] * 4
             + [K(uv=uv_box_roof), K(uv=uv_lod3_rear), DARK, DARK],
             K(uv=uv_lod3_side, paint=True)),
            (lower, 1.24, [DARK] * len(lower), K(uv=uv_lod3_side))):
        B = new()
        n = len(prof)
        for i in range(n):
            (s0, z0), (s1, z1) = prof[i], prof[(i + 1) % n]
            put(B, [P(-w, s0, z0), P(w, s0, z0), P(w, s1, z1), P(-w, s1, z1)], kinds[i], False)
        put(B, [P(w, s, z) for s, z in prof], side, False)
        put(B, [P(-w, s, z) for s, z in reversed(prof)], side, False)
        out.append(obj(B, "lod3"))
    return out


def build_lod(level):
    ang = (40.0, 50.0, 30.0, 30.0)[level]
    if level <= 1:
        bodies = [cab_group(level), bumper(level)] + carriers(level) + [box_shell(level)] \
            + chassis(level) + (wipers() if level == 0 else [])
        pieces = [VB.Piece("body", finish(o, ang)) for o in bodies]
        for sgn in (1, -1):
            pieces.append(VB.Piece("mirror", finish(mirror(sgn, level), ang)))
        return pieces + wheel_pieces(level)
    if level == 2:
        return [VB.Piece("body", finish(o, ang)) for o in lod2_parts()]
    return [VB.Piece("body", finish(o, ang)) for o in body_lod3()]


# ================================================================ checks
def check_layout():
    problems = []
    for part, x, s, wdt, steer, twin in L.WHEELS:
        if abs(x) + wdt / 2 > L.BOX_HW:
            problems.append("wheel %d reaches past the box's side" % part)
    # a turned front wheel's inner reach against the arch's inner wall
    hw = L.FRONT_W / 2
    a = math.radians(35.0)
    reach = L.FRONT_X - (hw * math.cos(a) + 0.49 * math.sin(a))
    if reach - L.ARCH[3] < 0.02:
        problems.append("arch inner wall at %.3f too near the turned wheel (%.3f)"
                        % (L.ARCH[3], reach))
    if L.ARCH[2] < math.hypot(L.R_WHEEL, hw) + 0.02:
        problems.append("arch radius too small for a turned wheel")
    if L.MUDGUARD[4] < 2 * L.R_WHEEL + 0.015:
        problems.append("mudguard too low over the twins")
    s = L.MARK_SIDE_S
    if s[0] > 3.0 or L.LENGTH - s[-1] > 1.0 + 0.05 or max(b - a for a, b in zip(s, s[1:])) > 3.0:
        problems.append("side marker spacing outside UN R48")
    if L.MUDGUARD[0] < L.GUARD_S[1]:
        problems.append("side guard runs into the mudguard")
    return problems


def build_all():
    return V.build_all(check_layout, build_lod)


def facts():
    inner = L.BOX_HW - 0.045
    return {"cargo": model_facts.cargo_box((-inner, Y(L.BOX_S0 + 0.05), L.BOX_Z0 + 0.10),
                                           (inner, Y(L.DOOR_FACE), L.HEADER_Z), door="rear")}


if __name__ == "__main__":
    V.main(build_all, facts)
