# SPDX-License-Identifier: GPL-3.0-or-later

"""rigid_box_18t: a two-axle 18 t cab-over box truck, all four tiers.

    python3 truck_atlas.py export
    blender --background --python build.py

Stations, the atlas layout and the UV mappings are truck_atlas.py's (L).

LOD0/LOD1: the cab and the dark lower module under it (bumper, corner and
step fairings) are one loft of plan rings: a front bowed in plan, rounded
corners, a set-back chin and a ledge at the bumper's top, a brow and the
sides' crown at the belt, sides leaning in above it, a raked screen panel
and a rounded roof edge. Exact booleans cut the arches, the screen inside
its rounded outline, the door glass with its dropped front corner, the
grille, the step wells, the headlamp units, the fog lamps in the chin and
the recess between the lamp pods; each lamp and pane is the floor of the
cutter that makes its recess, so it carries its own id and UVs. The roof
fairing (a second loft, its nose a convex curve, its sides flaring to the
box corners), a sun visor wrapped round the corners, the corner blades
(rooted in the front panel, a slot behind their tails) and the black fender
lips are unioned in. The plate's plinth, cab side collars, the front
mudguards' rear quarters, the box (panels set in behind aluminium rails,
corner posts and a rear frame round an inset roller door, marker lamps in
the rails), the chassis members and cross bearers, the fuel tank, battery
box and tanks, side guards on brackets, mudguards with flaps, axle
housings, the rear under-run bar with the lamp housings and plate are
closed solids that touch nothing. Mirrors are closed solids a few
millimetres apart and off the cab; wheels are revolved closed solids, the
rear twins one part a side. LOD2: plain massing with lamp cells on flat
faces, each axle's wheels one hexagonal prism in the body. LOD3: two
extruded side profiles.
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
(DARK, LINER, ALU, GUARD, RUBBER, PLASTIC, STEP, HOUSING, SEAL, MBODY, MGLASS, BEZEL, MESH,
 REFLECTOR) = (
    K(n) for n in ("dark", "liner", "alu", "guard", "rubber", "plastic", "step", "housing",
                   "seal", "mirror_body", "mirror", "bezel", "mesh", "reflector"))


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


def loft_faces(B, rings, band_kind, top=None, bottom=None, smooth=True):
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


# ================================================================ shell
def poly_pocket(c, U, V_, N, pts, depth, floor, wall, out=0.10):
    """A cutter prism on a host face: outline *pts* [(a, b)] in the face's
    axes U, V_ round *c*, its floor (one face, kind *floor*) *depth* under
    the surface, its lid *out* above it."""
    c, U, V_, N = (np.asarray(v, float) for v in (c, U, V_, N))

    def p(a, b, t):
        return P(*(c + U * a + V_ * b + N * t))
    B = new()
    put(B, [p(a, b, -depth) for a, b in pts], floor, False)
    put(B, [p(a, b, out) for a, b in reversed(pts)], wall, False)
    n = len(pts)
    for i in range(n):
        (a0, b0), (a1, b1) = pts[i], pts[(i + 1) % n]
        put(B, [p(a0, b0, -depth), p(a1, b1, -depth), p(a1, b1, out), p(a0, b0, out)], wall,
            False)
    return obj(B, "pocket")


def split_quads(B):
    """Split every quad of *B* that is not flat into two triangles, the
    diagonal mirrored about x = 0. A twisted quad left whole is cut one way
    by one boolean and the other way by the next, and the cuts made in it
    then stand a fraction of a millimetre off the surface as fins."""
    for method, sign in (('FIXED', 1.0), ('ALTERNATE', -1.0)):
        quads = []
        for f in B.bm.faces:
            if len(f.verts) != 4 or f.calc_center_median().x * sign < 0.0:
                continue
            p = [v.co for v in f.verts]
            n = (p[1] - p[0]).cross(p[2] - p[0])
            if n.length > 0.0 and abs((p[3] - p[0]).dot(n.normalized())) > 1e-7:
                quads.append(f)
        if quads:
            bmesh.ops.triangulate(B.bm, faces=quads, quad_method=method)
    return B


def join(objs, name="joined"):
    """Several closed solids that touch nothing, as one object."""
    bm = bmesh.new()
    for o in objs:
        bm.from_mesh(o.data)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for o in objs:
        d = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.meshes.remove(d)
    return bpy.data.objects.new(name, me)


def level_shell(level):
    """A tier's shell: its loft, the (bow, front arc, rear arc) segments,
    the kind of each band between rings and the ring range of the cab's
    screen panel."""
    R, V = L.SHELL.rings, L.SHELL.v
    if level == 0:
        kinds = ["low"] * (L.N_LOWER - 1) + ["ledge", "foot", "cab", "cab", "screen", "cab",
                                             "cab"]
        return L.SHELL, (3, 4, 1), kinds, (L.I_SCR0, L.I_SCR1)
    face = R[L.I_FACE[0]]
    foot = (L.Z_FOOT,) + face[1:]           # no chin, no tucked valance
    top = (R[L.I_TOP][0],) + face[1:]       # no rolled top edge
    idx = (L.I_LEDGE, L.I_SCR0, L.I_SCR1, L.I_ROOF)
    kinds = ["low", "ledge", "cab", "screen", "cab"]
    rings = [foot, top] + [R[i] for i in idx]
    vs = [V[0], V[L.I_TOP]] + [V[i] for i in idx]
    n = len(rings)
    return L.Loft(rings, "cab_band", vs), ((1, 2, 1) if level == 1 else (1, 1, 0)), kinds, \
        (n - 3, n - 2)


def shell(level):
    loft, (nbow, nf, nb), kinds, _scr = level_shell(level)
    rings = []
    for r, v in zip(loft.rings, loft.v):
        rings.append([(P(x, s, r[0]), loft.px(u, v)) for x, s, u in
                      full_ring(L.plan_half(r, nbow, nf, nb))])
    n = len(rings[0])
    m = n // 2 + 1                             # points in a half ring
    rear = (m - 2, m - 1)                      # the back wall, dark and unpainted

    def kind(i, j):
        k = kinds[i]
        if level == 2 and k == "screen" and (j < nbow or j >= n - nbow):
            return K("glass_ws", surface=32)   # LOD2: the screen is the whole front face
        if k in ("low", "ledge") or rear[0] <= j <= rear[1]:
            return 0, False
        if k == "foot":                        # painted round the front, plastic on the sides
            return 0, j < nbow + nf or j >= n - nbow - nf
        return 0, True
    B = new()
    loft_faces(B, rings, kind, top=K(uv=uv_cab_roof, paint=True), bottom=DARK)
    return obj(split_quads(B), "cab")


def front_cutter(loft, part, half, depth, floor, wall, cuts=(0.5,), lid=0.10):
    """A recess cut into the bowed front inside a symmetric outline, *half*
    its x >= 0 side [(x, z)] from the foot's centre round to the head's.
    The floor follows the front's parabola *depth* behind it in strips
    (floor a K), the lid stands *lid* in front. The strips break at the
    outline's own corners, at the centre line and at *cuts*, which are kept
    away from the shell's facet edges: a strip edge that crossed the
    outline a millimetre from a facet edge would leave a sliver."""
    lo, hi = part
    xmax = max(q[0] for q in half)
    first = next(i for i, q in enumerate(half) if q[0] >= xmax - 1e-9)
    last = max(i for i, q in enumerate(half) if q[0] >= xmax - 1e-9)
    low, upp = half[:first + 1], half[last:][::-1]

    def zlo(x):
        return float(np.interp(abs(x), [q[0] for q in low], [q[1] for q in low]))

    def zhi(x):
        return float(np.interp(abs(x), [q[0] for q in upp], [q[1] for q in upp]))
    xs = {round(q[0], 5) for q in half} | {round(c, 5) for c in cuts} | {0.0}
    xs = sorted(x for x in xs if x <= xmax + 1e-9)
    xs = [-x for x in reversed(xs) if x > 0] + xs

    def F(x, z):
        return P(x, loft.front(x, z, lo, hi) + depth, z)

    def O(x, z):
        return P(x, loft.front(x, z, lo, hi) - lid, z)

    def ring(a, b, fn):
        pts = [fn(a, zlo(a)), fn(b, zlo(b)), fn(b, zhi(b)), fn(a, zhi(a))]
        return [q for k, q in enumerate(pts) if q != pts[k - 1]]
    B = new()
    for a, b in zip(xs, xs[1:]):
        put(B, ring(a, b, F), floor, False)
        put(B, ring(a, b, O)[::-1], wall, False)
        put(B, [F(a, zlo(a)), O(a, zlo(a)), O(b, zlo(b)), F(b, zlo(b))], wall, False)
        put(B, [F(a, zhi(a)), F(b, zhi(b)), O(b, zhi(b)), O(a, zhi(a))], wall, False)
    for x in (xs[0], xs[-1]):
        if zhi(x) - zlo(x) > 1e-6:
            put(B, [F(x, zlo(x)), F(x, zhi(x)), O(x, zhi(x)), O(x, zlo(x))], wall, False)
    return obj(split_quads(B), "frontcut")


def region_floor(rect, hw, z0, z1, surface=0):
    """A floor kind mapped across atlas patch *rect* by x and z."""
    fx, fy, fw, fh = VB.patch_uv(L.REG[rect])

    def uv(co):
        x, _s, z = sw(co)
        return (fx + fw * (x + hw) / (2 * hw), fy + fh * (z - z0) / (z1 - z0))
    return K(uv=uv, surface=surface)


def lamp_frame(sgn):
    """The headlamp unit's place on the lower module's bowed face, the
    same on every tier (LOD0's): centre (x, s, z) on the chord across the
    unit, axes outward along the face, up, and out of it."""
    xc, zc, hu, _hv = L.HEADLAMP
    f0 = L.SHELL.front(xc - hu, zc, *L.I_FACE, nbow=3)
    f1 = L.SHELL.front(xc + hu, zc, *L.I_FACE, nbow=3)
    m = (f1 - f0) / (2 * hu)
    k = math.hypot(1.0, m)
    return (sgn * xc, (f0 + f1) / 2, zc), (sgn / k, m / k, 0.0), (0.0, 0.0, 1.0), \
        (sgn * m / k, -1.0 / k, 0.0)


def fog_frame(sgn):
    """The fog lamp's place on the chin, as lamp_frame()."""
    xc, zc, hu, _hv, _d = L.FOG
    f0 = L.SHELL.front(xc - hu, zc, *L.I_CHIN, nbow=3)
    f1 = L.SHELL.front(xc + hu, zc, *L.I_CHIN, nbow=3)
    m = (f1 - f0) / (2 * hu)
    k = math.hypot(1.0, m)
    return (sgn * xc, (f0 + f1) / 2, zc), (sgn / k, m / k, 0.0), (0.0, 0.0, 1.0), \
        (sgn * m / k, -1.0 / k, 0.0)


def headlamp_cells(sgn, grid=True):
    """Cells of one headlamp unit in its own (a, b): a outward from the
    unit's centre, b up from its middle. The amber indicator at the outer
    end, the low and high beam reflectors, the daytime strip under them.
    Each lens is mapped whole onto its patch. With *grid* the six cells
    share every corner, so the unit's floor stays closed however the
    boolean's grid rounds its turned corners. The light bezel is the
    recess's walls."""
    _xc, _zc, hu, hv = L.HEADLAMP
    a_ind, a_split, b_drl = L.LAMP_SPLIT
    c, U, V_, _N = (np.asarray(v, float) for v in lamp_frame(sgn))

    def lens(lid, a0, a1, b0, b1):
        fx, fy, fw, fh = VB.patch_uv(L.REG[L.lens_kind(lid)])

        def uv(co):
            d = np.asarray(sw(co)) - c
            return (fx + fw * (float(d @ U) - a0) / (a1 - a0),
                    fy + fh * (float(d @ V_) - b0) / (b1 - b0))
        return K(uv=uv, surface=lid)
    ind = lens(4 if sgn > 0 else 5, a_ind, hu, -hv, hv)
    low, high = lens(7, a_split, a_ind, b_drl, hv), lens(8, -hu, a_split, b_drl, hv)
    drl = lens(9, -hu, a_ind, -hv, b_drl)
    if not grid:
        return [(a_ind, hu, -hv, hv, ind), (a_split, a_ind, b_drl, hv, low),
                (-hu, a_split, b_drl, hv, high), (-hu, a_ind, -hv, b_drl, drl)]
    return [
        (a_ind, hu, b_drl, hv, ind), (a_ind, hu, -hv, b_drl, ind),
        (a_split, a_ind, b_drl, hv, low), (-hu, a_split, b_drl, hv, high),
        (-hu, a_split, -hv, b_drl, drl), (a_split, a_ind, -hv, b_drl, drl),
    ]


def shell_cutters(level):
    """Arches, screen, door glass, repeaters and headlamp units; at LOD0
    also the grille, the step wells, the front plate and the centre step."""
    loft, _seg, _kinds, scr = level_shell(level)
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
    # the screen, recessed into the bowed front inside its rounded outline
    w = L.WSCREEN
    if level == 0:
        half, cuts = L.rounded_outline(w, 2), (0.5,)
    else:                   # LOD1: the corners sharp, the dark surround still round them
        half, cuts = [(0.0, w[1]), (w[0], w[1]), (w[2], w[3]), (0.0, w[3])], ()
    out.append(front_cutter(loft, scr, half, 0.03,
                            region_floor("glass_ws", w[0], w[1], w[3], 32), SEAL, cuts=cuts))
    if level == 0:          # LOD1 keeps the grille in the band's texture
        g = L.GRILLE
        out.append(front_cutter(L.SHELL, (L.I_LEDGE, L.I_BELT), L.rounded_outline(g, 1), 0.04,
                                region_floor("grille", g[0], g[1], g[3]), PLASTIC, cuts=(0.45,)))
    # door glass on the leaning side, side repeaters
    (z0, z1) = L.Z_SCREEN
    w0, w1 = L.SHELL.rings[L.I_SCR0][3], L.SHELL.rings[L.I_SCR1][3]
    dxdz = (w1 - w0) / (z1 - z0)
    kk = math.hypot(1.0, dxdz)
    glass = L.DOOR_GLASS if level == 0 else L.DOOR_GLASS_LOD1
    gs = [q[0] for q in L.DOOR_GLASS]
    gz = [q[1] for q in L.DOOR_GLASS]
    s_c, z_c = (min(gs) + max(gs)) / 2, (min(gz) + max(gz)) / 2
    pts = [(q[0] - s_c, (q[1] - z_c) * kk) for q in glass]
    r0, r1, rz0, rz1 = L.REPEATER
    for sgn in (1, -1):
        c = (sgn * (w0 + dxdz * (z_c - z0)), s_c, z_c)
        out.append(poly_pocket(c, (0, 1, 0), (sgn * dxdz / kk, 0, 1 / kk),
                               (sgn / kk, 0, -dxdz / kk), pts, 0.022,
                               K("glass_side", surface=33), SEAL))
        c = (sgn * L.SHELL.side((rz0 + rz1) / 2, L.I_DOOR, L.I_BELT)[0], (r0 + r1) / 2,
             (rz0 + rz1) / 2)
        hu, hv_ = (r1 - r0) / 2, (rz1 - rz0) / 2
        out.append(pocket(c, (0, 1, 0), (0, 0, 1), (sgn, 0, 0), hu, hv_, 0.014,
                          [(-hu, hu, -hv_, hv_, lamp(4 if sgn > 0 else 5))], HOUSING))
        # the headlamp unit, its floor square to the bowed face
        c, U, V_, N = lamp_frame(sgn)
        _xc, _zc, hu, hv_ = L.HEADLAMP
        out.append(obj(obox(new(), c, U, V_, N, hu, hv_, 0.030, 0.14, headlamp_cells(sgn),
                            BEZEL), "lamp"))
        # the fog lamp in the chin's corner, in LOD0's plane on every tier
        c, U, V_, N = fog_frame(sgn)
        _xc, _zc, hu, hv_, fd = L.FOG
        out.append(obj(obox(new(), c, U, V_, N, hu, hv_, fd, 0.14,
                            [(-hu, hu, -hv_, hv_, lamp(10))], BEZEL), "fog"))
        if level == 0:
            for (s0, s1, sz0, sz1, d), floor in ((L.STEP_UP, PLASTIC), (L.STEP_LO, PLASTIC)):
                c = (sgn * L.LOW_HW, (s0 + s1) / 2, (sz0 + sz1) / 2)
                hu, hv_ = (s1 - s0) / 2, (sz1 - sz0) / 2
                out.append(pocket(c, (0, 1, 0), (0, 0, 1), (sgn, 0, 0), hu, hv_, d,
                                  [(-hu, hu, -hv_, hv_, floor)], [STEP, LINER, LINER, LINER]))
    if level == 0:
        ch, cz0, cz1, cd = L.CSTEP
        sf = L.SHELL.rings[L.I_FACE[0]][1]
        hv_ = (cz1 - cz0) / 2
        out.append(pocket((0.0, sf, (cz0 + cz1) / 2), (1, 0, 0), (0, 0, 1), (0, -1, 0), ch, hv_,
                          cd, [(-ch, ch, -hv_, hv_, MESH)], [STEP, PLASTIC, PLASTIC, PLASTIC]))
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


# ================================================================ deflector
def deflector(level):
    """The roof fairing: a loft of plan rings up a convex nose, painted."""
    R, V = L.DEFL.rings, L.DEFL.v
    idx, (nbow, nf) = {0: (range(len(R)), (2, 3)), 1: ((0, 3, 5), (1, 1)),
                       2: ((0, 5), (0, 0))}[level]
    rings = []
    for i in idx:
        if level == 2:      # a wedge: nose, shoulders, back
            _z, sc, _bow, wf, _rf, sb, wb, _rb = R[i]
            se = float(L.plan_frame(*R[i][1:])[5])
            half = [(0.0, sc, 0.0), (wf, se, wf), (wb, sb, wf + sb - se), (0.0, sb, 9.0)]
        else:
            half = L.plan_half(R[i], nbow, nf, 0)
        rings.append([(P(x, s, R[i][0]), L.DEFL.px(u, V[i])) for x, s, u in full_ring(half)])
    m = len(half)                            # points in a half ring

    def kind(i, j):
        return PAINT_CAB if j in (m - 2, m - 1) else (0, True)   # the back wall: a plain patch
    B = new()
    loft_faces(B, rings, kind, top=PAINT_CAB, bottom=PAINT_CAB)
    return obj(split_quads(B), "defl")


def cab_group(level):
    cab = asset_build.difference(shell(level), shell_cutters(level), snap=asset_build.SNAP)
    # No snap here: the fairing, visor and fender lips share no wall with the
    # cab, and moving the difference's cut points onto the grid would fold
    # the slivers beside them.
    return asset_build.union(cab, [deflector(level)] + cab_addons(level))


# The sun visor's section: (reach out of the cab's surface, z), tip then root.
VISOR = [(0.205, 2.535), (0.205, 2.505), (-0.075, 2.605), (-0.075, 2.645)]
VISOR_Z = 2.60                          # the height whose plan ring it follows
VISOR_WRAP = ((0.5, 0.62), (1.0, 0.16))   # round each corner: (arc fraction, share of the reach)


def visor(level):
    """The sun visor over the screen: a plank swept along the cab's plan at
    the screen's head, bowed with the front and wrapped round the corners
    onto the pillars, its reach tapering there (LOD2: a straight wedge)."""
    ring = L.SHELL.ring_at(VISOR_Z, L.I_SCR1, L.I_ROOF)
    _z, sc, bow, _wf, rf, _sb, _wb, _rb = ring
    xe, th0, tau, cx, cs, _se, _ls = (float(v) for v in L.plan_frame(*ring[1:]))
    th1 = math.pi / 2 - tau
    if level == 2:
        prof = [VISOR[0], VISOR[2], VISOR[3]]
        path = [((x, sc + bow * 0.35), (0.0, -1.0), 1.0) for x in (-0.96, 0.96)]
    else:
        prof = VISOR
        half = [((x, sc + bow * (x / xe) ** 2), unit((2 * bow * x / xe ** 2, -1.0)), 1.0)
                for x in ((0.0, 0.5, xe) if level == 0 else (0.0, xe))]
        for f, k in (VISOR_WRAP if level == 0 else ()):
            th = th0 + (th1 - th0) * f
            half.append(((cx + rf * math.sin(th), cs - rf * math.cos(th)),
                         (math.sin(th), -math.cos(th)), k))
        path = [((-p[0], p[1]), (-nrm[0], nrm[1]), k) for p, nrm, k in reversed(half[1:])] + half
    n = len(prof)
    secs = [[P(p[0] + nrm[0] * (o * k if o > 0 else o), p[1] + nrm[1] * (o * k if o > 0 else o), z)
             for o, z in prof] for p, nrm, k in path]
    B = new()
    for a, b in zip(secs, secs[1:]):
        for i in range(n):
            put(B, [a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]], PLASTIC, False)
    put(B, secs[0], PLASTIC, False)
    put(B, secs[-1][::-1], PLASTIC, False)
    return obj(split_quads(B), "visor")


def arc_prism(sgn, r0, r1, x0, x1, a0, a1, n, kind, smooth=True):
    """A band round the front axle from angle a0 to a1 (degrees, 0 at the
    front, 90 over the top), radii r0..r1, across |x| x0..x1."""
    sc, zc = L.FRONT_AXLE, L.R_WHEEL
    ang = [math.radians(a0 + (a1 - a0) * k / n) for k in range(n + 1)]
    outer = [(sc - r1 * math.cos(a), zc + r1 * math.sin(a)) for a in ang]
    inner = [(sc - r0 * math.cos(a), zc + r0 * math.sin(a)) for a in reversed(ang)]
    B = new()
    xa, xb = sorted((sgn * x0, sgn * x1))
    prism(B, outer + inner, "x", xa, xb, kind, kind, smooth=smooth)
    return obj(B, "arc")


def cab_addons(level):
    """The sun visor over the screen; at LOD0 the black fender lips round
    the front arches."""
    out = [visor(level)]
    if level == 0:
        r0, r1, x0, x1, a0, a1 = L.FLARE
        out += [arc_prism(sgn, r0, r1, x0, x1, a0, a1, 6, PLASTIC) for sgn in (1, -1)]
        out += blades(L.BLADE)
    return out


def blades(stations, loft=None, part=None):
    """The corner air deflectors: a painted blade a side, following the
    cab's front corner from a root inside the front panel out to a tail that
    stands off the corner, an open slot behind it. LOD0 unions it with the
    shell, so the root is moulded in; LOD1's short tail (BLADE_LOD1) is a
    closed solid that touches nothing; LOD2 shows the slot drawn behind it."""
    z0, z1 = L.BLADE_Z
    ring = (loft or L.SHELL).ring_at((z0 + z1) / 2, *(part or (L.I_DOOR, L.I_BELT)))
    _xe, th0, tau, cx, cs, _se, _ls = (float(v) for v in L.plan_frame(*ring[1:]))
    rf = ring[4]
    th1 = math.pi / 2 - tau

    def pt(sgn, f, e):
        a = th0 + (th1 - th0) * f
        return (sgn * (cx + (rf + e) * math.sin(a)), cs - (rf + e) * math.cos(a))
    out = []
    for sgn in (1, -1):
        outline = [pt(sgn, f, eo) for f, eo, _ei in stations] \
            + [pt(sgn, f, ei) for f, _eo, ei in reversed(stations)]
        B = new()
        prism(B, outline, "z", z0, z1, PAINT_CAB, PAINT_CAB, smooth=True)
        out.append(obj(B, "blade"))
    return out


def collars():
    """The cab's side collars: a painted flap from each rear edge of the
    cab out to the box's corner, closing the gap in side view. Closed
    solids that touch nothing: the foot follows the cab's leaning side 4 mm
    off it, the outer edge stands upright by the box corner."""
    s0, s1, x1, z0, z1, t = L.COLLAR
    out = []
    for sgn in (1, -1):
        secs = []
        for z in (z0, z1):
            x0 = L.SHELL.side(min(z, L.Z_SCREEN[1]), L.I_BELT, L.I_SCR1)[0] + 0.004
            if z > L.Z_SCREEN[1]:                # over the roof's rounding the foot stays put
                x0 = L.SHELL.side(L.Z_SCREEN[1], L.I_BELT, L.I_SCR1)[0] + 0.004
            d = unit((x1 - x0, s1 - s0, 0.0))
            n = np.array((-d[1], d[0], 0.0)) * t
            a, b = np.array((x0, s0, z)), np.array((x1, s1, z))
            secs.append([P(sgn * q[0], q[1], q[2]) for q in (a, b, b + n, a + n)])
        B = new()
        lo, hi = secs
        for k in range(4):
            put(B, [lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]], PAINT_CAB, False)
        put(B, lo, PAINT_CAB, False)
        put(B, hi[::-1], PAINT_CAB, False)
        out.append(obj(split_quads(B), "collar"))
    return out


def plinth():
    """The front plate on its plinth (LOD0): a block standing off the
    chin, a closed solid that touches nothing; its face is the plate."""
    ph, pz0, pz1 = L.PLATE_F
    sf = L.SHELL.rings[L.I_CHIN[0]][1]
    return xbox(-ph, ph, sf - G - L.PLINTH, sf - G, pz0, pz1, {"all": PLASTIC, "s0": K("plate")})


def wings(level):
    """The front mudguards' rear quarters behind the cab, with their
    flaps: closed solids that touch nothing."""
    r0, r1, x0, x1, a0, a1 = L.WING
    out = []
    for sgn in (1, -1):
        s1 = L.FRONT_AXLE + r1
        if level == 1:       # one plate: the wing's foot and its flap
            out.append(xbox(sgn * x0, sgn * x1, s1 - 0.025, s1, L.WING_FLAP, 0.95, RUBBER))
            continue
        out.append(arc_prism(sgn, r0, r1, x0, x1, a0, a1, 4, PLASTIC))
        out.append(xbox(sgn * x0, sgn * x1, s1 - 0.025, s1, L.WING_FLAP,
                        L.R_WHEEL - r1 * math.sin(math.radians(a1 - 180.0)) - G, RUBBER))
    return out


def wipers():
    """Two parked wiper arms lying a few millimetres off the recessed,
    bowed screen (LOD0): straight bars along a chord of the bow, set forward
    by its sagitta."""
    r3, r4 = L.SHELL.rings[L.I_SCR0], L.SHELL.rings[L.I_SCR1]
    nrm = unit((0.0, -(r4[0] - r3[0]), r4[1] - r3[1]))
    xe = L.SHELL.xe(1.75)
    out = []
    for a0, a1, z0, z1 in ((-0.86, -0.14, 1.71, 1.78), (0.04, 0.76, 1.71, 1.78)):
        f0 = np.array((a0, L.SHELL.front(a0, z0, L.I_SCR0, L.I_SCR1) + 0.03, z0))
        f1 = np.array((a1, L.SHELL.front(a1, z1, L.I_SCR0, L.I_SCR1) + 0.03, z1))
        sag = L.BOW / xe ** 2 * ((a1 - a0) / 2) ** 2
        U = unit(f1 - f0)
        V_ = unit(np.cross(nrm, U))
        ctr = (f0 + f1) / 2 + np.asarray(nrm) * (sag + 0.010)
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
    for sgn in (1, -1):
        # rail and subframe as one member: dark on dark, the joint never showed
        out.append(xbox(sgn * rx0, sgn * rx1, 1.83, 7.80, L.RAIL_Z[0], 1.072, DARK))
    if level == 0:
        for s in (2.45, 3.30, 4.15, 5.05, 6.75, 7.40):
            out.append(xbox(-1.20, 1.20, s - 0.03, s + 0.03, 1.075, L.BOX_Z0 - G, DARK))
    # fuel tank, left, on straps from the rail
    s0, s1, xc, zc, r = L.TANK
    n = 12 if level == 0 else 6
    out.append(tank(s0, s1, xc, zc, r, n))
    # battery box, right
    s0, s1, x0, x1, z0, z1 = L.BATTERY
    out.append(xbox(-x1, -x0, s0, s1, z0, z1, {"all": DARK, "z1": PLASTIC}))
    if level == 0:
        # AdBlue tank left; an air tank and a silencer right
        # each hangs 2 mm off the rail's side, so none needs a bracket
        out.append(xbox(rx1 + G, 0.82, 3.16, 3.51, 0.55, 0.92, PLASTIC))
        B = new()
        xa = rx1 + G + 0.11 * math.cos(math.pi / 6)
        prism(B, polygon(-xa, 0.80, 0.11, 6, math.pi / 6), "s", 3.00, 3.90, DARK, DARK)
        out.append(obj(B, "air"))
        out.append(xbox(-0.95, -(rx1 + G), 4.10, 4.75, 0.62, 0.92, DARK))
    # side guards on brackets
    g0, g1 = L.GUARD_S
    gx0, gx1 = L.GUARD_X
    for sgn in (1, -1):
        for z0, z1 in L.GUARD_Z:
            out.append(xbox(sgn * gx0, sgn * gx1, g0, g1, z0, z1, GUARD))
        for s in (L.GUARD_BRACKETS if level == 0 else ()):     # LOD1: the rails alone
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
    # rear axle housings and differential
    zc = L.R_WHEEL
    if level == 0:
        for sgn in (1, -1):
            B = new()
            a0, a1 = sorted((sgn * 0.172, sgn * 0.585))
            prism(B, polygon(5.90, zc, 0.085, 6, math.pi / 6), "x", a0, a1, DARK, DARK)
            out.append(obj(B, "axle"))
        out.append(xbox(-0.17, 0.17, 5.74, 6.06, 0.38, 0.66, DARK))
    else:
        B = new()
        prism(B, polygon(5.90, zc, 0.085, 6, math.pi / 6), "x", -0.585, 0.585, DARK, DARK)
        out.append(obj(B, "axle"))
    return out


def tank(s0, s1, xc, zc, r, n):
    """The fuel tank: a prism mapped along and round the tank patch, so its
    two straps are rings; plain aluminium ends."""
    tx, ty, tw, th = VB.patch_uv(L.REG["tank"])
    pts = polygon(xc, zc, r, n, math.pi / n)
    B = new()
    for k in range(n):
        q0, q1 = pts[k], pts[(k + 1) % n]
        cos = [P(q0[0], s0, q0[1]), P(q1[0], s0, q1[1]), P(q1[0], s1, q1[1]), P(q0[0], s1, q0[1])]
        v0, v1 = ty + th * k / n, ty + th * (k + 1) / n
        put_uv(B, cos, [(tx, v0), (tx, v1), (tx + tw, v1), (tx + tw, v0)])
    put(B, [P(q[0], s0, q[1]) for q in pts], ALU, False)
    put(B, [P(q[0], s1, q[1]) for q in reversed(pts)], ALU, False)
    return obj(B, "tank")


def rear_lamp(sgn, level):
    s0, s1, x0, x1, z0, z1 = L.REAR_LAMP
    lz0, lz1 = L.REAR_LENS_Z
    z0 += G
    if level >= 1:
        cells = []
        for xo, xi, kind in (L.REAR_CELLS_L if sgn > 0 else L.REAR_CELLS_R):
            xs = sorted((sgn * xo, sgn * xi))
            cells.append((xs[0], xs[1], lz0, lz1,
                          REFLECTOR if kind == "reflector" else lamp(kind)))
        a, b = sorted((sgn * x0, sgn * x1))
        return tiled_box(a, b, s0, s1, z0, z1, rear=cells, base=HOUSING)
    o = xbox(sgn * x0, sgn * x1, s0, s1, z0, z1, HOUSING)
    xc, zc = (x0 + x1) / 2, (lz0 + lz1) / 2
    hu, hv = (x1 - x0) / 2, (lz1 - lz0) / 2
    cells = []
    for xo, xi, kind in (L.REAR_CELLS_L if sgn > 0 else L.REAR_CELLS_R):
        k = REFLECTOR if kind == "reflector" else lamp(kind)
        cells.append((xi - xc, xo - xc, -hv, hv, k))
    cut = pocket((sgn * xc, s1, zc), (sgn, 0, 0), (0, 0, 1), (0, 1, 0), hu, hv, 0.02, cells,
                 HOUSING)
    return asset_build.difference(o, [cut], snap=asset_build.SNAP)


# ================================================================ mirrors
MIRROR_POST = (1.385, 0.445)              # the post's |x| and station
MIRROR_ARMS = ((2.40, 0.545), (1.735, 0.45))   # arm heights and their stations on the cab


def tube(p0, p1, r, n, kind=None):
    """A closed tube of n sides from p0 to p1, points in (x, s, z)."""
    kind = kind or MBODY
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    ax = unit(p1 - p0)
    u = unit(np.cross(ax, (0.0, 0.0, 1.0) if abs(ax[2]) < 0.9 else (1.0, 0.0, 0.0)))
    v = np.cross(ax, u)
    ring = [u * math.cos(2 * math.pi * k / n) + v * math.sin(2 * math.pi * k / n)
            for k in range(n)]
    B = new()
    a = [P(*(p0 + q * r)) for q in ring]
    b = [P(*(p1 + q * r)) for q in ring]
    for k in range(n):
        put(B, [a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]], kind, True)
    put(B, a[::-1], kind, False)
    put(B, b, kind, False)
    return obj(B, "tube")


def mirror(sgn, level):
    """A mirror per side, as closed solids a few millimetres apart: at LOD0
    two rounded heads (the tall main mirror and the squarer wide-angle one
    under it) behind a tube post, the post between two tube arms from the
    door frame; at LOD1 one arm and one block holding both glasses."""
    px, ps = MIRROR_POST
    (zu, su), (zl, sl) = MIRROR_ARMS

    def root(z, s_):
        return (sgn * (L.SHELL.side(z, L.I_DOOR, L.I_SCR1)[0] + 0.003), s_, z)
    if level >= 1:
        a = tube(root(zu, su), (sgn * (px + 0.01), ps, zu), 0.016, 4)
        x0, x1 = sorted((sgn * 1.30, sgn * 1.49))
        b = xbox(x0, x1, ps + 0.018, ps + 0.10, 1.78, 2.35, {"all": MBODY, "s1": MGLASS})
        return join([a, b], "mirror")
    r = 0.015
    parts = [tube(root(zu, su), (sgn * (px + 0.015), ps, zu), r, 4),
             tube(root(zl, sl), (sgn * (px + 0.015), ps, zl), r, 4),
             tube((sgn * px, ps, zl + r + 0.002), (sgn * px, ps, zu - r - 0.002), r + 0.002, 4),
             head(sgn, 1.395, 0.098, ps + 0.018, ps + 0.125, 2.14, 0.205, 3),       # main
             head(sgn, 1.395, 0.088, ps + 0.018, ps + 0.105, 1.84, 0.082, 2)]      # wide angle
    return join(parts, "mirror")


def head(sgn, xc, hx, s0, s1, zc, hz, bands):
    """A mirror head round (xc, zc), half sizes hx across and hz up: a
    housing with a rounded back, small at its front (s0) and swelling to
    its full outline at the rear face (s1), which is the dark glass. The
    tall main head (three bands) has its corners rounded in two steps, the
    small one in one."""
    nc = 2 if bands == 3 else 1

    def ring(s, k):
        ax, az = hx * k, hz * k + (hz - hx) * (1.0 - k) * 0.6
        r = min(ax, az) * 0.62
        pts = []
        for qx, qz, a0 in ((1, 1, 0.0), (1, -1, 0.5), (-1, -1, 1.0), (-1, 1, 1.5)):
            for i in range(nc + 1):
                a = math.pi * (a0 + 0.5 * i / nc)
                pts.append((qx * (ax - r) + r * math.sin(a), qz * (az - r) + r * math.cos(a)))
        return [P(sgn * xc + px, s, zc + pz) for px, pz in pts]
    d = s1 - s0
    rings = ([ring(s0, 0.50), ring(s0 + 0.22 * d, 0.84), ring(s0 + 0.60 * d, 1.0), ring(s1, 1.0)]
             if bands == 3 else [ring(s0, 0.55), ring(s0 + 0.40 * d, 0.96), ring(s1, 1.0)])
    n = len(rings[0])
    B = new()
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            put(B, [r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]], MBODY, True)
    put(B, list(reversed(rings[0])), MBODY, False)
    put(B, rings[-1], MGLASS, False)
    return obj(B, "head")


# ================================================================ wheels
def wheel(level, front, outward, half=None):
    """A revolved closed wheel about its own centre, axis along X: a profile
    of (x outward, r) from the inner cap to the outer cap; the tyre's tread
    rows map round the tread strip, everything else onto the face disc."""
    R = L.R_WHEEL
    if level == 0:
        sides = 20
        # the inner sidewalls, which nothing shows at any use distance, have no shoulder
        prof = ([(-0.15, R), (0.12, R), (0.15, 0.49), (0.15, 0.30),
                 (0.10, 0.285), (0.10, 0.155), (0.15, 0.105)] if front else
                [(-0.32, R), (-0.025, R), (0.0, 0.49), (0.025, R), (0.29, R),
                 (0.32, 0.49), (0.32, 0.30), (0.25, 0.285), (0.25, 0.145), (0.305, 0.11)])
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
        # the top rail too is unpainted aluminium, as LOD0's: under a dark
        # paint the box keeps its light frame lines
        tile_face(B, lambda u, v, sgn=sgn: P(sgn * hw, u, v), s0, s1, z0, z1,
                  [(s0, s1, z0, L.RAIL_LO[1], rail), (s0, s1, L.RAIL_HI[0], z1, ALU)], panel)
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
    parts = [shell(2), visor(2), deflector(2), box_lod2()]
    # the headlamp units: plaques in LOD0's lens planes, a few millimetres
    # proud of this tier's flatter face, the lenses their outer faces
    _xc, _zc, hu, hv = L.HEADLAMP
    for sgn in (1, -1):
        c, U, V_, N = lamp_frame(sgn)
        parts.append(obj(obox(new(), c, U, V_, tuple(-v for v in N), hu, hv, 0.008,
                              0.0, headlamp_cells(sgn, grid=False), BEZEL), "lamp"))
    parts.append(xbox(-0.95, 0.95, 1.83, 7.64, 0.48, L.BOX_Z0 - G,
                      {"all": DARK, "x0": K(uv=uv_lod3_side), "x1": K(uv=uv_lod3_side)}))
    # the under-run bar and the two lamp housings above its ends
    b0, b1, bh, bz0, bz1 = L.BAR
    parts.append(xbox(-bh, bh, b0, b1, bz0, bz1, GUARD))
    s0, s1, x0, x1, z0, z1 = L.REAR_LAMP
    lz0, lz1 = L.REAR_LENS_Z
    for sgn, row in ((1, L.REAR_CELLS_L), (-1, L.REAR_CELLS_R)):
        cells = []
        for xo, xi, kind in row:
            if kind != "reflector" and not (sgn < 0 and kind == 6):   # one reverse lens
                xs = sorted((sgn * xo, sgn * xi))
                cells.append((xs[0], xs[1], lz0, lz1, lamp(kind)))
        a, b = sorted((sgn * x0, sgn * x1))
        parts.append(tiled_box(a, b, s0, s1, z0 + G, z1, rear=cells, base=HOUSING))
    # the left fog lamp: a tetrahedron whose face is the lens, parallel to
    # LOD0's and 3 mm proud of this tier's flatter face
    loft = level_shell(2)[0]
    c, U, V_, N = (np.asarray(v, float) for v in fog_frame(1))
    _xc, _zc, hu, hv, fd = L.FOG
    tri = [(-hu, -hv), (hu, -hv), (0.0, hv)]
    t = max((c[1] + U[1] * a_ - loft.front(c[0] + U[0] * a_, c[2] + b_, 0, 1, nbow=1) + 0.003)
            / -N[1] for a_, b_ in tri)
    if t + fd > 0.048:
        raise ValueError("LOD2's fog lens stands %.3f m off LOD0's" % (t + fd))
    q = [c + U * a_ + V_ * b_ + N * t for a_, b_ in tri]
    apex = c - N * 0.10
    B = new()
    put(B, [P(*v) for v in q], lamp(10), False)
    for k in range(3):
        put(B, [P(*q[k]), P(*apex), P(*q[(k + 1) % 3])], BEZEL, False)
    parts.append(obj(B, "fog"))
    # Each axle's wheels one prism across it, the middle inside the body. The
    # front one stands 6 mm proud of the lower module's sides, which this
    # tier does not cut for arches, so the discs show.
    parts.append(wheel_body(0.0, L.FRONT_AXLE, False, half=L.LOW_HW + 0.006))
    parts.append(wheel_body(0.0, L.REAR_AXLE, True, half=L.REAR_X + L.REAR_W / 2))
    return parts


def body_lod3():
    """Two extruded side profiles: the painted cab and box (the raked nose,
    the deflector and box front as one slope, the roof) and, a little
    narrower, the dark unpainted lower module and under-body on four wheel
    feet. 24 + 36 triangles."""
    hw = L.BOX_HW
    upper, lower = L.LOD3_UPPER, L.LOD3_LOWER
    out = []
    for prof, w, kinds, side in (
            (upper, hw, [K(uv=uv_lod3_front, paint=True)] * 3
             + [K(uv=uv_box_roof), K(uv=uv_lod3_rear), DARK, DARK],
             K(uv=uv_lod3_side, paint=True)),
            (lower, 1.24, [K(uv=uv_lod3_front)] + [DARK] * (len(lower) - 1),
             K(uv=uv_lod3_side))):
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
        bodies = [cab_group(level), box_shell(level)] + chassis(level) \
            + collars() + wings(level) \
            + (wipers() + [plinth()] if level == 0
               else blades(L.BLADE_LOD1, level_shell(1)[0], (2, 3)))
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
    # the front wing behind the cab: clear of a turned wheel, the cab's back,
    # the tank, the battery box and the side guards
    r0, r1, _x0, wx1, a0, _a1 = L.WING
    if r0 < math.hypot(L.R_WHEEL, hw) + 0.02:
        problems.append("front wing too near a turned wheel")
    if L.FRONT_AXLE - r0 * math.cos(math.radians(a0)) < L.CAB_BACK + 0.002:
        problems.append("front wing runs into the cab's back")
    back = L.FRONT_AXLE + r1
    if min(L.TANK[0], L.BATTERY[0]) < back + 0.02 or (L.GUARD_S[0] < back + 0.02
                                                      and L.GUARD_X[0] < wx1 + 0.002):
        problems.append("front wing runs into the tank, the battery box or a side guard")
    # the headlamp unit inside the bumper face's bowed part, over the chin
    xc, zc, hu, hv = L.HEADLAMP
    if xc + hu > L.SHELL.xe(zc, *L.I_FACE) - 0.02 or zc - hv < L.Z_CHIN + 0.02 \
            or zc + hv > L.SHELL.rings[L.I_FACE[1]][0] - 0.02:
        problems.append("headlamp unit leaves the bumper's face")
    # screen and grille inside the bowed front, clear of the corner arcs
    for name, t, part in (("screen", L.WSCREEN, (L.I_SCR0, L.I_SCR1)),
                          ("grille", L.GRILLE, (L.I_LEDGE, L.I_BELT))):
        for hw_, z in ((t[0], t[1]), (t[2], t[3])):
            if hw_ > L.SHELL.xe(z, *part) - 0.02:
                problems.append("%s reaches the corner arc at z %.2f" % (name, z))
    if L.COLLAR[2] > L.BOX_HW or L.COLLAR[1] > L.BOX_S0 - 0.01:
        problems.append("cab collar reaches past the box's side or into its front")
    # the fog lamps inside the chin's bowed part, between its rings, clear of
    # the intake slots; the plinth behind the bumper's face
    fx, fz, fhu, fhv, _fd = L.FOG
    chin = [L.SHELL.rings[i][0] for i in L.I_CHIN]
    if fx + fhu > L.SHELL.xe(fz, *L.I_CHIN) - 0.02 or fz - fhv < chin[0] + 0.015 \
            or fz + fhv > chin[1] - 0.015 or fx - fhu < L.INTAKE[1] + 0.04:
        problems.append("fog lamp leaves the chin or meets an intake slot")
    if L.SHELL.rings[L.I_CHIN[0]][1] - G - L.PLINTH < 0.0:
        problems.append("the plate's plinth stands past the bumper's face")
    if max(L.DEFL_W) > L.BOX_HW or L.DEFL_BACK > L.BOX_S0 - 0.02 or L.DEFL_TOP > L.BOX_Z1:
        problems.append("fairing reaches past the box")
    return problems


def build_all():
    return V.build_all(check_layout, build_lod)


def facts():
    inner = L.BOX_HW - 0.045
    return {"cargo": model_facts.cargo_box((-inner, Y(L.BOX_S0 + 0.05), L.BOX_Z0 + 0.10),
                                           (inner, Y(L.DOOR_FACE), L.HEADER_Z), door="rear")}


if __name__ == "__main__":
    V.main(build_all, facts)
