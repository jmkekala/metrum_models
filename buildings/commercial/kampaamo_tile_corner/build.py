# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of kampaamo_tile_corner, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A late-1980s Finnish corner shop of the postmodern kind, let to a hair salon:
one tall storey in small glazed ceramic tile, a flat roof behind a parapet
with a thin painted coping, and a quarter-round corner. The shopfront storey
is tiled in a muted accent colour over a dark tile plinth; above it a white
tile band carries the sign and runs on round the curve. At the corner the
shopfront stands back from the band under its own soffit, glazed in facets
between slim mullions on a smaller arc, and a slim round white column stands
free under the band's middle with a projecting light box above it.

The straight front has two display windows under striped awnings, the
salon's lettering on the band over them, and the one shop door next to the
corner under a thin steel canopy hung on two rods. The left side has two
windows, the back a small window, the staff door under a small steel canopy
and the wall ladder to the roof, and the right side a window, the meter cupboard and an exhaust louvre.
The roof drains inside the parapet, so there are no gutters or downpipes.

Construction is a set of closed solids unioned with Blender's exact boolean:
the shell (walls, the corner recess, the parapet and the deck as one solid
built face by face, with every opening's reveals), the coping, the column
and its steel shoe, the light box, the awnings, the canopy and its rods, and the roof fan and
pipes. The wall ladder is roof_safety's lean kit, appended after the weld.

Every number the mesh and the atlas share is imported from facade_atlas.py.
"""

import importlib
import math
import os
import sys

import bmesh
import bpy
from mathutils import Euler, Vector, geometry


HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import facade_atlas as L  # noqa: E402  (layout constants shared with the atlas)
importlib.reload(L)       # an interactive session must not keep a stale layout

ASSET = L.ASSET
EXPORT_DIR = os.path.join(HERE, "export")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import model_facts  # noqa: E402
import roof_safety as RS  # noqa: E402
from asset_build import bounds as _bounds, to_object, union  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT,
                          tint=L.LIT_FACTOR)
get_material, export_all = BUILD.material, BUILD.export_all
_show_only, preview_studio = BUILD.show_only, BUILD.preview_studio
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants

PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ================================================================== massing
HX, HY = L.HX, L.HY
CX, CY = L.ARC_C
R_OUT, R_IN = L.R_OUT, L.R_IN
FRONT_L = L.FRONT_L
S_EAST = FRONT_L + L.ARC_OUT_LEN            # the wall band's U where each
S_REAR = S_EAST + (HY - CY)                 # straight wall starts, running
S_WEST = S_REAR + 2.0 * HX                  # anticlockwise from the front's
                                            # left end, round the curve

REVEAL_V = 1.0              # sills and heads sample the accent tile from here
SOFFIT_V = 3.125            # the corner soffit samples the white tile from here

# Straight walls, walked anticlockwise seen from above so the outward face is
# on the right, as every build.py walks them. *breaks* are heights where the
# wall's vertical edge meets the corner recess.
WALLS = {
    "front": dict(p0=(-HX, -HY), p1=(CX, -HY), s_off=0.0, right=(L.Z_HEAD,), left=()),
    "east": dict(p0=(HX, CY), p1=(HX, HY), s_off=S_EAST, right=(), left=(L.Z_HEAD,)),
    "rear": dict(p0=(HX, HY), p1=(-HX, HY), s_off=S_REAR, right=(), left=()),
    "west": dict(p0=(-HX, HY), p1=(-HX, -HY), s_off=S_WEST, right=(), left=()),
}
WALL_ORDER = ("front", "east", "rear", "west")


def _span(centre, width):
    return centre - width / 2.0, centre + width / 2.0


SIDE_W, SIDE_H, SIDE_Z = L.SIDE_WIN
REAR_W, REAR_H, REAR_Z = L.REAR_WIN
SERV_W, SERV_H, _ = L.SERVICE_DOOR
MET_W, MET_H, MET_Z = L.METER
LOU_W, LOU_H, LOU_Z = L.LOUVRE

# (kind, s0, s1, z0, z1) on each straight wall, s from its p0.
ITEMS = {
    "front": [("display",) + L.DISPLAYS[0] + (L.Z_SILL, L.Z_HEAD),
              ("display2",) + L.DISPLAYS[1] + (L.Z_SILL, L.Z_HEAD),
              ("door",) + L.DOOR_SPAN + (0.0, L.Z_HEAD),
              ("sign",) + L.SIGN_SPAN + L.SIGN_Z],
    "east": [("side",) + _span(2.25, SIDE_W) + (SIDE_Z, SIDE_Z + SIDE_H),
             ("meter",) + _span(5.25, MET_W) + (MET_Z, MET_Z + MET_H),
             ("louvre",) + _span(4.0, LOU_W) + (LOU_Z, LOU_Z + LOU_H)],
    "rear": [("rear",) + _span(4.5, REAR_W) + (REAR_Z, REAR_Z + REAR_H),
             ("service",) + _span(7.0, SERV_W) + (0.0, SERV_H)],
    "west": [("side",) + _span(3.0, SIDE_W) + (SIDE_Z, SIDE_Z + SIDE_H),
             ("side",) + _span(6.0, SIDE_W) + (SIDE_Z, SIDE_Z + SIDE_H)],
}
REGION = {"display": L.DISPLAY_R, "display2": L.DISPLAY2_R, "door": L.DOOR_R,
          "sign": L.SIGN_R, "side": L.SIDE_R, "meter": L.METER_R,
          "louvre": L.LOUVRE_R, "rear": L.REAR_R, "service": L.SERVICE_R}
DEPTH = {"display": L.SHOP_DEPTH, "display2": L.SHOP_DEPTH, "door": L.SHOP_DEPTH,
         "side": L.WINDOW_DEPTH, "rear": L.WINDOW_DEPTH, "service": L.SERVICE_DEPTH}

# roof plant: (kind, (x, y), radius, height over the deck)
FAN = ((-1.6, 1.6), 0.28, 0.58, 0.36, 0.76)      # drum r, drum top, hood r, hood top
VENTS = [((2.2, 2.4), 0.055, 0.95), ((-3.5, -1.2), 0.045, 0.80)]
SUNK = 0.10                 # roof plant runs this far into the deck

# The wall ladder: on the back wall, toward its east end, clear of the back
# window and the staff door. s along the back wall from its p0 (5, 4.5).
LADDER_S = 2.0


# ---------------------------------------------------------- tier choices
def arc_segments(level):
    """8, 6, 4, 3 facets round the quarter circle, body, band and coping
    alike: 11.25 degrees a facet at LOD0, 30 at LOD3. Every tier that keeps
    the column or the light box has an even count, which puts a vertex at
    the curve's middle where they stand; LOD3 has neither, and its three
    facets keep the corner round at the last switch."""
    return L.ARC_SEGMENTS[level]


def cut(level):
    """Openings are cut, with reveals, to 70 m; flat past it."""
    return level < 2


def coping_modelled(level):
    """The 6 cm coping is under a pixel past 120 m: LOD3 paints it on the
    parapet's top instead (the wall band's top rows are its face)."""
    return level < 3


COLUMN_SIDES = (16, 10, 6, None)
FAN_SIDES = (12, 8, 6, None)
VENT_SIDES = (8, 6, None, None)


def rods_kept(level):
    """The canopy's two 3 cm tie rods are under a pixel past 70 m."""
    return level < 2


def lightbox_kept(level):
    """The 0.12 m light box is 0.8 m tall and reads at LOD2's distance; at
    LOD3 it is a pixel or two and goes."""
    return level < 3


# ============================================================== mesh builder
class Builder:
    """One closed solid under construction, with UVs set as faces are made.
    Vertices are shared through a position cache, so faces that meet along
    an edge meet on the same vertices."""

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
    """A wall plane: s runs along the wall from p0, z is world height, and out
    runs away from the wall on the side the outward normal points."""

    def __init__(self, p0, p1):
        self.p0 = Vector((p0[0], p0[1], 0.0))
        d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
        self.L = d.length
        self.t = d / self.L
        self.n = Vector((self.t.y, -self.t.x, 0.0))

    def P(self, s, z, out=0.0):
        q = self.p0 + self.t * s + self.n * out
        return (q.x, q.y, z)

    def s_of(self, co):
        return (co.x - self.p0.x) * self.t.x + (co.y - self.p0.y) * self.t.y

    def out_of(self, co):
        return (co.x - self.p0.x) * self.n.x + (co.y - self.p0.y) * self.n.y


# ------------------------------------------------------------- plan rings
def arc_pts(r, n):
    """The quarter circle round ARC_C at radius *r*, from the front (-90
    degrees) to the east side (0), as n facets: n + 1 points."""
    out = []
    for i in range(n + 1):
        a = math.radians(-90.0 + 90.0 * i / n)
        out.append((CX + r * math.cos(a), CY + r * math.sin(a)))
    return out


def ring(offset, n):
    """The wall outline offset *offset* outward (negative inward), anticlockwise
    from the front-left corner, its curve in n facets."""
    hx, hy = HX + offset, HY + offset
    return [(-hx, -hy)] + arc_pts(R_OUT + offset, n) + [(hx, hy), (-hx, hy)]


def ground_outline(n):
    """The wall outline at ground level: the curved shopfront stands RECESS
    behind the band, with a return at each end of the curve."""
    return [(-HX, -HY), (CX, -HY)] + arc_pts(R_IN, n) + [(HX, CY), (HX, HY), (-HX, HY)]


def _theta(co):
    """Angle along the curve, 0 at its front end, pi/2 at its east end."""
    return math.atan2(co[1] - CY, co[0] - CX) + math.pi / 2.0


def _radius(co):
    return math.hypot(co[0] - CX, co[1] - CY)


# ------------------------------------------------------------ UV mappings
def uv_patch(name):
    x, y, w, h = L.PATCHES[name]
    c = (x + w / 2.0, y + h / 2.0)
    return lambda co: c


def uv_band(fr, s_off):
    """The wall band: U the running length round the building, V height."""
    return lambda co: ((s_off + fr.s_of(co)) * PPM, L.WALL_Y0 + co.z * PPM)


def uv_region(fr, rect, s0, s1, z0, z1):
    x, y, w, h = rect
    return lambda co: (x + (fr.s_of(co) - s0) / (s1 - s0) * w,
                       y + (co.z - z0) / (z1 - z0) * h)


def uv_jamb(fr, s_off, sj):
    """A reveal's side: the band, running on into the reveal from the wall's
    own U, so the tile courses turn the corner."""
    return lambda co: ((s_off + sj + max(0.0, -fr.out_of(co))) * PPM,
                       L.WALL_Y0 + co.z * PPM)


def uv_reveal_flat(fr, s_off):
    """A sill or head: accent tile, U along the wall, V the depth in."""
    return lambda co: ((s_off + fr.s_of(co)) * PPM,
                       L.WALL_Y0 + (REVEAL_V + max(0.0, -fr.out_of(co))) * PPM)


def uv_arc_band(co):
    return ((FRONT_L + R_OUT * _theta(co)) * PPM, L.WALL_Y0 + co.z * PPM)


def uv_curve(co):
    x, y, _w, _h = L.CURVE_R
    return (x + R_IN * _theta(co) * PPM, y + co.z * PPM)


def uv_soffit(co):
    return ((FRONT_L + R_OUT * _theta(co)) * PPM,
            L.WALL_Y0 + (SOFFIT_V + (R_OUT - _radius(co))) * PPM)


def uv_deck(co):
    x, y, _w, _h = L.DECK_R
    return (x + (co.x + HX - L.PARAPET_T) * L.DECK_PPM,
            y + (co.y + HY - L.PARAPET_T) * L.DECK_PPM)


def uv_ring_face(cum, a, t, y0, z0):
    """A face along a ring segment from plan point *a* in direction *t*, U the
    ring's running length *cum* at a, V from *z0* up into rows from *y0*."""
    return lambda co: ((cum + (co.x - a[0]) * t[0] + (co.y - a[1]) * t[1]) * PPM,
                       y0 + (co.z - z0) * PPM)


def uv_ring_top(cum, a, t, nrm, y0):
    """A ring's top: U along the segment, V inward from its outer edge."""
    return lambda co: ((cum + (co.x - a[0]) * t[0] + (co.y - a[1]) * t[1]) * PPM,
                       y0 + max(0.0, (a[0] - co.x) * nrm[0] + (a[1] - co.y) * nrm[1]) * PPM)


def _segments(pts):
    """(a, b, unit tangent, outward normal, running length at a) for each
    edge of a closed anticlockwise ring."""
    out, cum = [], 0.0
    for k in range(len(pts)):
        a, b = pts[k], pts[(k + 1) % len(pts)]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        t = ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)
        out.append((a, b, t, (t[1], -t[0]), cum))
        cum += ln
    return out


# ================================================================== walls
def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge: openings on
    one wall share head and sill heights, so the triangulator may join three
    collinear corners."""
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


def fill_region(B, fr, outline, holes, uvfn, out=0.0):
    """Triangulate a wall region with holes and add it."""
    loops = [outline] + holes
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((s, z, 0.0)) for s, z in loop] for loop in loops])
    for a, b, c in _flip_slivers(flat, tris):
        B.face([fr.P(*flat[a], out), fr.P(*flat[b], out), fr.P(*flat[c], out)], uvfn)


def build_item(B, fr, s_off, item, level):
    """One opening or painted panel; returns its outline on the wall.

    Cut: four reveals (no sill under a door that stands on the ground: the
    floor cap covers its footprint) and the closing face DEPTH back. Flush:
    the closing face on the wall plane. Either way it samples its region.
    """
    kind, s0, s1, z0, z1 = item
    fn = uv_region(fr, REGION[kind], s0, s1, z0, z1)
    o = [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]
    depth = DEPTH.get(kind)
    if depth is None or not cut(level):
        B.face([fr.P(s, z) for s, z in o], fn)
        return o
    flat = uv_reveal_flat(fr, s_off)
    edges = [(o[0], o[1], flat), (o[1], o[2], uv_jamb(fr, s_off, s1)),
             (o[2], o[3], flat), (o[3], o[0], uv_jamb(fr, s_off, s0))]
    for k, (a, b, f) in enumerate(edges):
        if k == 0 and z0 <= EPS:
            continue
        B.face([fr.P(*a), fr.P(*b), fr.P(*b, -depth), fr.P(*a, -depth)], f)
    B.face([fr.P(s, z, -depth) for s, z in o], fn)
    return o


def build_wall(B, name, level, z_top):
    """One straight elevation, holed and notched for its items."""
    spec = WALLS[name]
    fr = Frame(spec["p0"], spec["p1"])
    ln = fr.L
    items = ITEMS[name]
    outline = [(0.0, 0.0)]
    for kind, s0, s1, z0, z1 in sorted((i for i in items if i[3] <= EPS),
                                       key=lambda i: i[1]):
        outline += [(s0, 0.0), (s0, z1), (s1, z1), (s1, 0.0)]
    outline += [(ln, 0.0)] + [(ln, z) for z in sorted(spec["right"])]
    outline += [(ln, z_top), (0.0, z_top)]
    outline += [(0.0, z) for z in sorted(spec["left"], reverse=True)]
    holes = []
    for item in items:
        poly = build_item(B, fr, spec["s_off"], item, level)
        if item[3] > EPS:
            holes.append(poly)
    fill_region(B, fr, outline, holes, uv_band(fr, spec["s_off"]))


def build_corner(B, n, z_top):
    """The curved corner: the band on the outer arc from the shopfront head
    up, its soffit back to the inner arc, the faceted shopfront on the inner
    arc down to the ground, and a tiled return at each end of the recess."""
    outer, inner = arc_pts(R_OUT, n), arc_pts(R_IN, n)
    zh = L.Z_HEAD
    for i in range(n):
        (a, b), (c, d) = (outer[i], outer[i + 1]), (inner[i], inner[i + 1])
        B.face([a + (zh,), b + (zh,), b + (z_top,), a + (z_top,)], uv_arc_band)
        B.face([a + (zh,), b + (zh,), d + (zh,), c + (zh,)], uv_soffit)
        B.face([c + (0.0,), d + (0.0,), d + (zh,), c + (zh,)], uv_curve)
    front_ret = Frame((CX, -HY), (CX, -HY + L.RECESS))
    east_ret = Frame((HX - L.RECESS, CY), (HX, CY))
    for fr, s_off in ((front_ret, FRONT_L), (east_ret, S_EAST - L.RECESS)):
        B.face([fr.P(0.0, 0.0), fr.P(fr.L, 0.0), fr.P(fr.L, zh), fr.P(0.0, zh)],
               uv_band(fr, s_off))


def build_top(B, n, z_top, coping):
    """The parapet's top (inside the coping, which the union then removes; or,
    where the coping is not modelled, painted as it), the parapet's inner
    face down to the deck, and the deck."""
    outer, inner = ring(0.0, n), ring(-L.PARAPET_T, n)
    so, si = _segments(outer), _segments(inner)
    blank = uv_patch("blank")
    top_y0 = L.COP_Y0 + L.COP_FACE
    for k in range(len(outer)):
        a, b, t, nrm, cum = so[k]
        ia, ib, it, _n, icum = si[k]
        top = blank if coping else uv_ring_top(cum, a, t, nrm, top_y0)
        B.face([a + (z_top,), b + (z_top,), ib + (z_top,), ia + (z_top,)], top)
        B.face([ib + (L.Z_DECK,), ia + (L.Z_DECK,), ia + (z_top,), ib + (z_top,)],
               uv_ring_face(icum, ia, it, L.UPST_Y0, L.Z_DECK))
    B.face([p + (L.Z_DECK,) for p in inner], uv_deck)


def close_floor(B):
    """Cap the shell's open rim on the ground with one face, triangulated in
    plan (it is not convex: the recess bites into it)."""
    bm = B.bm
    bm.edges.index_update()
    rim = {e for e in bm.edges if len(e.link_faces) == 1}
    if any(sum(1 for e in v.link_edges if e in rim) != 2 for e in rim for v in e.verts):
        raise ValueError("the shell's rim branches: a T-junction somewhere")
    first = min(rim, key=lambda e: e.index)
    start, cur = first.verts
    loop = [start]
    rim.discard(first)
    while cur is not start:
        loop.append(cur)
        e = min((x for x in cur.link_edges if x in rim), key=lambda x: x.index)
        rim.discard(e)
        cur = e.other_vert(cur)
    if rim:
        raise ValueError("the shell has %d open edges besides its floor: a "
                         "T-junction somewhere" % len(rim))
    if any(abs(v.co.z) > 1e-6 for v in loop):
        raise ValueError("the shell's open rim is not on the ground")
    pts = [Vector((v.co.x, v.co.y, 0.0)) for v in loop]
    blank = uv_patch("blank")
    for a, b, c in geometry.tessellate_polygon([pts]):
        f = bm.faces.new((loop[a], loop[b], loop[c]))
        B.set_uv(f, blank)


def main_body(level):
    n = arc_segments(level)
    z_top = L.Z_PAR if coping_modelled(level) else L.Z_COP
    B = Builder()
    for name in WALL_ORDER:
        build_wall(B, name, level, z_top)
    build_corner(B, n, z_top)
    build_top(B, n, z_top, coping_modelled(level))
    close_floor(B)
    return B


# ================================================================ the rest
def coping(level):
    """The parapet's painted sheet coping as one closed ring, oversailing
    both faces by COPING_OUT: its faces on the coping band's face rows, its
    top on the top rows, its underside the drip patch."""
    n = arc_segments(level)
    co = L.COPING_OUT
    outer, inner = ring(co, n), ring(-(L.PARAPET_T + co), n)
    so, si = _segments(outer), _segments(inner)
    z0, z1 = L.Z_COP0, L.Z_COP
    B = Builder()
    drip = uv_patch("drip")
    for k in range(len(outer)):
        a, b, t, nrm, cum = so[k]
        ia, ib, it, _n, icum = si[k]
        B.face([a + (z0,), b + (z0,), b + (z1,), a + (z1,)],
               uv_ring_face(cum, a, t, L.COP_Y0, z0))
        B.face([ib + (z0,), ia + (z0,), ia + (z1,), ib + (z1,)],
               uv_ring_face(icum, ia, it, L.COP_Y0, z0))
        B.face([a + (z1,), b + (z1,), ib + (z1,), ia + (z1,)],
               uv_ring_top(cum, a, t, nrm, L.COP_Y0 + L.COP_FACE))
        B.face([ia + (z0,), ib + (z0,), b + (z0,), a + (z0,)], drip)
    return B


def prism(px, py, r, z0, z1, sides, side_uv, top_uv, bottom_uv, phase=0.5):
    """An upright round bar of *sides* sides, centre (px, py)."""
    B = Builder()
    pts = [(px + r * math.cos(a), py + r * math.sin(a))
           for a in [(i + phase) * 2.0 * math.pi / sides for i in range(sides)]]
    for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
        B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], side_uv)
    B.face([(x, y, z1) for x, y in pts], top_uv)
    B.face([(x, y, z0) for x, y in reversed(pts)], bottom_uv)
    return B


def box(x0, x1, y0, y1, z0, z1, sides, top, bottom):
    """A closed box; *sides* is one mapping or four, south/east/north/west."""
    B = Builder()
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    fns = sides if isinstance(sides, (list, tuple)) else [sides] * 4
    for k in range(4):
        (ax, ay), (bx, by) = pts[k], pts[(k + 1) % 4]
        B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], fns[k])
    B.face([(x, y, z1) for x, y in pts], top)
    B.face([(x, y, z0) for x, y in reversed(pts)], bottom)
    return B


def _mid_dir():
    a = math.radians(-45.0)
    return math.cos(a), math.sin(a)


def column(level):
    """The slim round column under the band at the curve's middle, white,
    from the pavement up into the band over the soffit."""
    er = _mid_dir()
    px, py = CX + L.COLUMN_AT * er[0], CY + L.COLUMN_AT * er[1]
    c = uv_patch("column")
    return prism(px, py, L.COLUMN_R, 0.0, L.Z_HEAD + 0.10, COLUMN_SIDES[level], c, c,
                 uv_patch("blank"))


def column_shoe(level):
    """The column's steel shoe at the pavement: a short wider collar in the
    coping's dark paint, which grounds the slim column and takes the kicks."""
    er = _mid_dir()
    px, py = CX + L.COLUMN_AT * er[0], CY + L.COLUMN_AT * er[1]
    r, h = L.SHOE
    d = uv_patch("drip")
    return prism(px, py, r, 0.0, h, COLUMN_SIDES[level], d, uv_patch("metal_edge"),
                 uv_patch("blank"))


def lightbox():
    """The projecting light box over the column: a slab standing radially out
    of the curved band, lit on both faces. Each face maps so its artwork
    reads the right way round from its own side."""
    proj, h, t, z0 = L.LIGHTBOX
    z1 = z0 + h
    er = Vector(_mid_dir() + (0.0,))
    et = Vector((-er.y, er.x, 0.0))
    o = Vector((CX, CY, 0.0))
    r0, r1 = R_OUT - 0.10, R_OUT + proj

    def P(r, s, z):
        q = o + er * r + et * s
        return (q.x, q.y, z)
    x, y, w, hh = L.LIGHTBOX_R

    def face_uv(sign):
        def fn(co):
            r = (Vector((co.x, co.y, 0.0)) - o).dot(er)
            f = (r - R_OUT) / proj if sign < 0 else (R_OUT + proj - r) / proj
            return (x + f * w, y + (co.z - z0) / h * hh)
        return fn
    side, blank = uv_patch("box_side"), uv_patch("blank")
    B = Builder()
    for sgn in (1.0, -1.0):
        s = sgn * t / 2.0
        B.face([P(r0, s, z0), P(r1, s, z0), P(r1, s, z1), P(r0, s, z1)], face_uv(sgn))
    B.face([P(r1, -t / 2, z0), P(r1, t / 2, z0), P(r1, t / 2, z1), P(r1, -t / 2, z1)], side)
    B.face([P(r0, -t / 2, z0), P(r0, t / 2, z0), P(r0, t / 2, z1), P(r0, -t / 2, z1)], blank)
    B.face([P(r0, -t / 2, z1), P(r1, -t / 2, z1), P(r1, t / 2, z1), P(r0, t / 2, z1)], side)
    B.face([P(r0, -t / 2, z0), P(r1, -t / 2, z0), P(r1, t / 2, z0), P(r0, t / 2, z0)], side)
    return B


def awning(s0, s1):
    """A fabric awning over a display window, as a closed wedge along the
    front wall: the sloping cloth, the valance, the underside and the two
    cheeks, its back buried in the band."""
    fr = Frame(*[WALLS["front"][k] for k in ("p0", "p1")])
    sa, sb = s0 - L.AWN_OVER, s1 + L.AWN_OVER
    prof = L.AWN_PROFILE
    tx, ty, tw, th = L.AWN_TOP_R
    vx, vy, vw, vh = L.AWN_VAL_R
    front_out = prof[1][0]
    top = lambda co: (tx + (fr.s_of(co) - sa) / (sb - sa) * tw,  # noqa: E731
                      ty + (1.0 - max(0.0, fr.out_of(co)) / front_out) * th)
    val = lambda co: (vx + (fr.s_of(co) - sa) / (sb - sa) * vw,  # noqa: E731
                      vy + (co.z - prof[2][1]) / (prof[1][1] - prof[2][1]) * vh)
    fns = [top, val, uv_patch("fabric_under"), uv_patch("blank")]
    B = Builder()
    for k in range(4):
        (oa, za), (ob, zb) = prof[k], prof[(k + 1) % 4]
        B.face([fr.P(sa, za, oa), fr.P(sb, za, oa), fr.P(sb, zb, ob), fr.P(sa, zb, ob)],
               fns[k])
    cheek = uv_patch("awn_cheek")
    B.face([fr.P(sa, z, o) for o, z in prof], cheek)
    B.face([fr.P(sb, z, o) for o, z in reversed(prof)], cheek)
    return B


def canopy(spec=L.CANOPY, rear=False):
    """A thin steel canopy over a door: top and edges painted sheet,
    underside the white soffit, back buried in the wall. The shop door's on
    the front, the staff door's at the back."""
    cx, w, proj, z0, z1 = spec
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    edge, blank = uv_patch("metal_edge"), uv_patch("blank")
    if rear:
        y0, y1 = HY - 0.10, HY + proj
        sides = [blank, edge, edge, edge]
    else:
        y0, y1 = -HY - proj, -HY + 0.10
        sides = [edge, edge, blank, edge]
    return box(x0, x1, y0, y1, z0, z1, sides, uv_patch("metal"), uv_patch("soffit"))


def bar(p0, p1, w, uv):
    """A straight square bar *w* across from *p0* to *p1*, a closed solid."""
    a, b = Vector(p0), Vector(p1)
    d = (b - a).normalized()
    side = d.cross(Vector((0.0, 0.0, 1.0)))
    if side.length < 1e-6:
        side = Vector((1.0, 0.0, 0.0))
    side.normalize()
    up = side.cross(d).normalized()
    h = w / 2.0
    sq = [side * h + up * h, -side * h + up * h, -side * h - up * h, side * h - up * h]
    B = Builder()
    r0, r1 = [tuple(a + q) for q in sq], [tuple(b + q) for q in sq]
    for k in range(4):
        B.face([r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k]], uv)
    B.face(list(reversed(r1)), uv)
    B.face(list(r0), uv)
    return B


ROD_X = (L.CANOPY[0] - L.CANOPY[1] / 2.0 + 0.12, L.CANOPY[0] + L.CANOPY[1] / 2.0 - 0.12)
ROD_TOP = 3.55


def rods():
    """The canopy's two tie rods, from near its front edge up to the band."""
    _cx, _w, proj, _z0, z1 = L.CANOPY
    out = []
    for x in ROD_X:
        out.append(bar((x, -HY - proj + 0.08, z1 - 0.025), (x, -HY + 0.05, ROD_TOP),
                       0.03, uv_patch("metal_edge")))
    return out


def fan(level):
    """The roof extract fan: a galvanised drum on the deck under a wider
    hood, standing just over the parapet's line."""
    (px, py), r, top, hr, htop = FAN
    sides = FAN_SIDES[level]
    x, y, w, h = L.COWL_R
    z0 = L.Z_DECK - SUNK

    def side(co):
        a = (math.atan2(co.y - py, co.x - px) / (2.0 * math.pi)) % 1.0
        return (x + w * a, y + h * (co.z - z0) / (L.Z_DECK + htop - z0))
    galv = uv_patch("galv")
    drum = prism(px, py, r, z0, L.Z_DECK + top, sides, side, galv, uv_patch("blank"))
    hood = prism(px, py, hr, L.Z_DECK + top - 0.03, L.Z_DECK + htop, sides, side, galv, galv)
    return [drum, hood]


def vents(level):
    out = []
    sides = VENT_SIDES[level]
    if not sides:
        return out
    x, y, w, h = L.PIPE_R
    for (px, py), r, ht in VENTS:
        z0 = L.Z_DECK - SUNK

        def side(co, px=px, py=py, z0=z0, ht=ht):
            a = (math.atan2(co.y - py, co.x - px) / (2.0 * math.pi)) % 1.0
            return (x + w * a, y + h * (co.z - z0) / (L.Z_DECK + ht - z0))
        out.append(prism(px, py, r, z0, L.Z_DECK + ht, sides, side, uv_patch("galv"),
                         uv_patch("blank")))
    return out


# ------------------------------------------------------------- the kit
PAINT = RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)
EAVE = RS.Eave(WALLS["rear"]["p0"], WALLS["rear"]["p1"], L.Z_COP0, L.COPING_OUT,
               L.Z_COP, 0.0)
WALL_LADDER = RS.WallLadder(EAVE, LADDER_S, lean=True)
KIT = [WALL_LADDER]


def kit(level):
    """The wall ladder, roof_safety's MODES unchanged, with extents: it stands
    furthest out at the back, so LOD3 keeps its bare rails."""
    return RS.solids(KIT, level, PAINT, extents=True)


# ================================================================ assembly
def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    solids = []
    if coping_modelled(level):
        solids.append(coping(level))
    if COLUMN_SIDES[level]:
        solids.append(column(level))
        solids.append(column_shoe(level))
    if lightbox_kept(level):
        solids.append(lightbox())
    for s0, s1 in L.DISPLAYS:
        solids.append(awning(s0, s1))
    solids.append(canopy())
    solids.append(canopy(L.REAR_CANOPY, rear=True))
    if rods_kept(level):
        solids += rods()
    if FAN_SIDES[level]:
        solids += fan(level)
    solids += vents(level)
    parts = [to_object(B, "tmp_part%d" % i) for i, B in enumerate(solids)]
    obj = union(base, parts, snap=asset_build.SNAP)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # recover the cost of coplanar boolean subdivisions, keeping UV seams
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    RS.append(obj, kit(level), check=True)
    return obj


# ================================================================== checks
def _overlap(a, b, gap=0.0):
    return a[0] < b[1] + gap and b[0] < a[1] + gap and a[2] < b[3] + gap and b[2] < a[3] + gap


def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    for name in WALL_ORDER:
        fr = Frame(WALLS[name]["p0"], WALLS[name]["p1"])
        rects = [i[1:] for i in ITEMS[name]]
        for kind, s0, s1, z0, z1 in ITEMS[name]:
            if s0 < 0.25 - EPS or s1 > fr.L - 0.25 + EPS:
                bad.append("%s: %s at s %.2f is within 0.25 m of a corner" % (name, kind, s0))
            if z1 > L.Z_COP0 - 0.2:
                bad.append("%s: %s runs into the coping" % (name, kind))
            if z0 < L.Z_HEAD < z1:
                bad.append("%s: %s straddles the shopfront head" % (name, kind))
        for i, a in enumerate(rects):
            for b in rects[i + 1:]:
                if _overlap(a, b, 0.2):
                    bad.append("%s: two items within 0.2 m of each other" % name)
    a, b = WALLS["front"]["p0"], WALLS["front"]["p1"]
    if abs(math.hypot(b[0] - a[0], b[1] - a[1]) - FRONT_L) > 1e-9:
        bad.append("the front wall is not FRONT_L long")
    # door and transom
    if not 2.0 <= L.Z_LEAF <= 2.4:
        bad.append("the shop door's leaf is %.2f m, outside 2.0-2.4" % L.Z_LEAF)
    if not 2.0 <= L.SERVICE_LEAF[1] <= 2.4:
        bad.append("the staff door's leaf is outside 2.0-2.4 m")
    if L.Z_HEAD - L.Z_LEAF < 0.3:
        bad.append("no room for the shop door's transom light")
    # the awnings: over the windows, under the lettering, clear of the canopy
    prof = L.AWN_PROFILE
    z_wall_top = prof[0][1] + (prof[1][1] - prof[0][1]) * (-prof[0][0]) / (prof[1][0] - prof[0][0])
    z_wall_bot = prof[3][1] + (prof[2][1] - prof[3][1]) * (-prof[3][0]) / (prof[2][0] - prof[3][0])
    if z_wall_top > L.SIGN_Z[0] - 0.02:
        bad.append("the awnings meet the wall at %.3f m, into the lettering" % z_wall_top)
    if z_wall_bot < L.Z_HEAD + 0.03:
        bad.append("the awnings meet the wall at %.3f m, into the shopfront head"
                   % z_wall_bot)
    cx, cw, proj, cz0, cz1 = L.CANOPY
    cs0, cs1 = cx - cw / 2.0 + HX, cx + cw / 2.0 + HX
    for s0, s1 in L.DISPLAYS:
        if s1 + L.AWN_OVER > cs0 - 0.1:
            bad.append("an awning comes within 0.1 m of the canopy")
    if cs1 > FRONT_L - 0.02 or cs0 > L.DOOR_SPAN[0] or cs1 < L.DOOR_SPAN[1]:
        bad.append("the canopy does not cover the door inside the straight front")
    if cz0 < L.Z_HEAD + 0.05:
        bad.append("the canopy sits on the door head")
    # the staff door's canopy: over its door, above its head, clear of the
    # back window and the ladder (s along the back wall is HX - x)
    rx, rw, _rp, rz0, _rz1 = L.REAR_CANOPY
    rs0, rs1 = HX - (rx + rw / 2.0), HX - (rx - rw / 2.0)
    staff = next(i for i in ITEMS["rear"] if i[0] == "service")
    if rs0 > staff[1] or rs1 < staff[2] or rz0 < staff[4] + 0.1:
        bad.append("the staff door's canopy does not cover its door")
    for k, s0, s1, _z0, _z1 in ITEMS["rear"]:
        if k != "service" and s0 < rs1 + 0.2 and rs0 < s1 + 0.2:
            bad.append("the staff door's canopy crowds the %s" % k)
    ls0, ls1 = WALL_LADDER.span()
    if ls0 < rs1 + 0.3 and rs0 < ls1 + 0.3:
        bad.append("the staff door's canopy crowds the wall ladder")
    if ROD_TOP > L.Z_DECK + 0.2 or any(x + HX < L.SIGN_SPAN[1] + 0.2 for x in ROD_X):
        bad.append("a canopy rod lands in the lettering or above the parapet's solid")
    # the corner: the column under the soffit, the light box in the band
    if not R_IN + 0.05 < L.COLUMN_AT - L.COLUMN_R or L.COLUMN_AT + L.COLUMN_R > R_OUT - 0.01:
        bad.append("the column does not stand under the soffit")
    pr, ph, pt, pz0 = L.LIGHTBOX
    if pz0 < L.Z_HEAD + 0.1 or pz0 + ph > L.Z_COP0 - 0.15:
        bad.append("the light box does not sit on the band")
    if 0.10 > L.PARAPET_T or pz0 + ph > L.Z_PAR:
        bad.append("the light box's back is not buried in the parapet's solid")
    for lv, n in enumerate(L.ARC_SEGMENTS):
        if n % 2 and (COLUMN_SIDES[lv] or lightbox_kept(lv)):
            bad.append("LOD%d's %d arc facets put no vertex at the curve's middle, "
                       "where its column and light box stand" % (lv, n))
    if not R_IN + 0.05 < L.COLUMN_AT - L.SHOE[0]:
        bad.append("the column's shoe does not stand clear of the shopfront")
    # the roof: the parapet hides the deck and stands over the plant's base
    if L.Z_COP - L.Z_DECK < 0.5:
        bad.append("the parapet stands only %.2f m over the deck" % (L.Z_COP - L.Z_DECK))
    for (px, py), r in [(FAN[0], FAN[3])] + [(p, r) for p, r, _h in VENTS]:
        if not (-HX + L.PARAPET_T + 0.5 < px - r and px + r < HX - L.PARAPET_T - 0.5
                and -HY + L.PARAPET_T + 0.5 < py - r and py + r < HY - L.PARAPET_T - 0.5):
            bad.append("roof plant at (%.1f, %.1f) crowds the parapet" % (px, py))
        if _radius((px, py)) < R_OUT and px > CX and py < CY:
            bad.append("roof plant at (%.1f, %.1f) is in the curve" % (px, py))
    # the ladder: on the back wall, clear of its corners and openings
    avoid = [(k, s0, s1) for k, s0, s1, _z0, _z1 in ITEMS["rear"]]
    bad += RS.problems(WALL_LADDER, "the wall ladder", avoid)
    return bad


# ================================================================== build
def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame.

    The footprint is the wall outline at ground level, LOD0's facets: at the
    corner that is the curved shopfront on its inner arc, RECESS behind the
    band, with a return at each end. The shop door is on the straight front
    beside the corner, at grade; its height is the leaf's, without the
    transom light. One storey, floored at the pavement.
    """
    ring0 = ground_outline(arc_segments(0))
    area = abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(ring0, ring0[1:] + ring0[:1]))) / 2.0
    door = next(i for i in ITEMS["front"] if i[0] == "door")
    staff = next(i for i in ITEMS["rear"] if i[0] == "service")
    doors = [model_facts.wall_door("salon", "entrance", WALLS["front"]["p0"],
                                   WALLS["front"]["p1"], (door[1] + door[2]) / 2.0,
                                   0.0, L.LEAF_W, L.Z_LEAF, main=True),
             model_facts.wall_door("staff", "service", WALLS["rear"]["p0"],
                                   WALLS["rear"]["p1"], (staff[1] + staff[2]) / 2.0,
                                   0.0, L.SERVICE_LEAF[0], L.SERVICE_LEAF[1])]
    return {"hero": False, "dwellings": 0, "footprint": ring0,
            "storeys": [(0.0, area)], "doors": doors}


# ================================================================ previews
def _figure():
    """A 1.8 m standing figure for the working views: body, head."""
    grey = uv_patch("blank")
    out = [box(-0.22, 0.22, -0.13, 0.13, 0.0, 1.55, grey, grey, grey),
           box(-0.10, 0.10, -0.10, 0.10, 1.58, 1.80, grey, grey, grey)]
    objs = []
    for i, B in enumerate(out):
        o = to_object(B, "_figure%d" % i)
        bpy.context.scene.collection.objects.link(o)
        objs.append(o)
    mat = bpy.data.materials.get("_figure") or bpy.data.materials.new("_figure")
    mat.diffuse_color = (0.25, 0.22, 0.20, 1.0)
    for o in objs:
        o.data.materials.append(mat)
    return objs


def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export -- four
    orthographic elevations, a plan from above, a raised three-quarter aerial
    off the front corner -- plus an aerial off the back, and eye-level views
    at the corner and the front with a 1.8 m figure by the door. Working
    views only - not committed."""
    os.makedirs(out_dir, exist_ok=True)
    preview_studio()
    _show_only(level)
    scn = bpy.context.scene
    saved = (scn.camera, scn.render.resolution_x, scn.render.resolution_y)
    scn.render.resolution_x, scn.render.resolution_y = res
    centre, radius = _bounds(bpy.data.objects["{}_LOD{}".format(ASSET, level)])
    cam = bpy.data.objects.get("_view_cam")
    if cam is None:
        cam = bpy.data.objects.new("_view_cam", bpy.data.cameras.new("_view_cam"))
        scn.collection.objects.link(cam)
    scn.camera = cam
    cam.data.clip_end = 1000.0
    views = {
        "front": ((0, -1, 0), (90, 0, 0)), "rear": ((0, 1, 0), (90, 0, 180)),
        "east": ((1, 0, 0), (90, 0, 90)), "west": ((-1, 0, 0), (90, 0, -90)),
        "top": ((0, 0, 1), (0, 0, 0)),
    }
    written = []
    for name, (d, rot) in views.items():
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = radius * 2.1
        cam.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
        cam.location = centre + Vector(d) * 80.0
        scn.render.filepath = os.path.join(out_dir, "L%d_%s.png" % (level, name))
        bpy.ops.render.render(write_still=True)
        written.append(scn.render.filepath)
    for name, d in (("aerial", Vector((1.0, -1.0, math.sqrt(2.0)))),
                    ("aerial_rear", Vector((-1.0, 1.0, math.sqrt(2.0))))):
        cam.data.type = 'PERSP'
        cam.data.lens = 35.0
        cam.location = centre + d.normalized() * radius * 3.0
        cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scn.render.filepath = os.path.join(out_dir, "L%d_%s.png" % (level, name))
        bpy.ops.render.render(write_still=True)
        written.append(scn.render.filepath)
    pivot = Vector(BUILD.pivot) if BUILD.pivot else Vector()
    figs = _figure()
    for o in figs:
        o.location = Vector((0.9, -HY - 1.2, 0.0)) - pivot
    for name, loc, aim in (("eye_corner", (9.0, -14.5, 1.6), (2.0, -3.2, 2.0)),
                           ("eye_front", (-1.0, -15.5, 1.6), (-0.5, -4.5, 2.1)),
                           ("eye_door", (4.2, -8.6, 1.6), (1.5, -4.5, 1.9))):
        cam.data.type = 'PERSP'
        cam.data.lens = 30.0
        cam.location = Vector(loc) - pivot
        cam.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        scn.render.filepath = os.path.join(out_dir, "L%d_%s.png" % (level, name))
        bpy.ops.render.render(write_still=True)
        written.append(scn.render.filepath)
    for o in figs:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.meshes.remove(me)
    scn.camera, scn.render.resolution_x, scn.render.resolution_y = saved
    return written


if __name__ == "__main__":
    BUILD.main(build_all, facts)
