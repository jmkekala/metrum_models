# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of voimalaitos_brick_hall, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

The boiler and turbine hall of a small mid-century Nordic town heat-and-power
plant: one block of two volumes in red facing brick infilling an exposed
concrete frame, on a concrete plinth, under flat roofs behind a concrete
roof-edge beam and parapet. The boiler house, 14 x 17 m and 19.5 m to its
coping, is the west block, with a louvred roof monitor; the turbine hall,
18 x 16 m and 11.6 m, abuts its east face. Tall steel multi-pane hall windows
fill the front bays of both. The boiler house's rear wall carries a closed
flue stub toward the chimney, its west end the coal intake hatch high up;
the turbine hall's east end, toward the transformer yard, is nearly blank
round a cable bushing panel.

Construction. The walls of both volumes are one closed shell, meshed
directly: each wall is a rectangle less its columns and openings, cut into
4 m slabs of brick (facade_atlas.CUTS) whose outlines are traced from a grid
of cells; every face is then given every vertex that lies on its edges
(tjunctions()), so neighbours meet on shared vertices. Recessed openings
add their concrete reveals and the closing plane, made of the window
region's sections. The shell is capped by a floor and two lids, which the
roof slabs bury. The roof slabs (edge beam, parapet and sunk deck), the
roof monitor, the ventilators, the flue stub, the entrance canopy, the
downpipes and the ladders are closed solids of their own, unioned with
Blender's exact boolean.

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
import downpipes as DP  # noqa: E402
import model_facts  # noqa: E402
import roof_safety as RS  # noqa: E402
from asset_build import bounds as _bounds, open_stack, to_object, union  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT,
                          tint=L.LIT_FACTOR)
get_material, export_all = BUILD.material, BUILD.export_all
_show_only, preview_studio = BUILD.show_only, BUILD.preview_studio
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants

PPM = L.PPM
EPS = 1e-6
ND = 4                  # vertex positions are compared at 0.1 mm
LEVELS = (0, 1, 2, 3)
LADDER_HANG = 0.30      # the upper wall ladder's foot, above the hall's deck


# ----------------------------------------------------------------- tiers
def opening_mode(level):
    """Recessed with concrete reveals to 70 m; flush, the same rectangles
    painted, at LOD2; at LOD3 the walls are single faces carrying the
    6 px/m elevations, every opening and column painted on them."""
    return ("cut", "cut", "flush", "elevation")[level]


def roof_flat(level):
    """LOD3 draws each roof as a box to the coping: the parapet's profile
    stays, the sunk deck behind it, invisible from the ground, goes."""
    return level >= 3


def vents_kept(level):
    """The two 0.8 m ventilators are hollow to LOD2 and go at LOD3, where
    they are about seven pixels over a roof seen from below its edge."""
    return level < 3


# ============================================================== mesh builder
def _key(co):
    return (round(co[0], ND) + 0.0, round(co[1], ND) + 0.0, round(co[2], ND) + 0.0)


class Builder:
    """One closed solid under construction, with UVs set as faces are made.

    Vertices are shared through a position cache, so faces that meet along an
    edge meet on the same vertices when every vertex on the edge is a corner
    of both faces.
    """

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cache = {}

    def v(self, co):
        key = _key(co)
        vert = self.cache.get(key)
        if vert is None:
            vert = self.bm.verts.new(key)
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


def wall_frame(name):
    return Frame(*L.WALLS[name][:2])


# ------------------------------------------------------------ UV mappings
def _patch_centre(name):
    x, y, w, h = L.PATCHES[name]
    return (x + w / 2.0, y + h / 2.0)


def uv_patch(name):
    c = _patch_centre(name)
    return lambda co: c


U_OFF = {}
_u = 0.0
for _n in L.WALL_ORDER[:-1]:
    U_OFF[_n] = _u
    _u += L.wall_len(_n)
U_OFF["step"] = 0.0


def uv_brick(fr, u_off, shift):
    """The brick band from the wall's foot, *shift* metres lower above it."""
    return lambda co: ((fr.s_of(co) + u_off) * PPM,
                       L.BRICK_Y0 + (co.z - shift) * PPM)


def uv_column(fr, s0, u0):
    """A column: the concrete band with U up the column and V across it."""
    return lambda co: ((co.z + u0) * PPM, L.COL_Y0 + (fr.s_of(co) - s0) * PPM)


def uv_jamb(fr):
    """A reveal's side: concrete, U up it, V the depth from the wall face."""
    return lambda co: (co.z * PPM, L.COL_Y0 + (-fr.out_of(co)) * PPM)


def uv_head(fr):
    """A reveal's head or sill: U along the wall, V the depth."""
    return lambda co: (fr.s_of(co) * PPM, L.COL_Y0 + (-fr.out_of(co)) * PPM)


def uv_region(fr, rect, s0, z0):
    x, y, w, h = rect
    return lambda co: (x + (fr.s_of(co) - s0) * PPM, y + (co.z - z0) * PPM)


def uv_elevation(fr, name):
    ename, off = L.WALL_ELEV[name]
    ex, ey, ew, eh = L.ELEV[ename]
    zb = L.ELEV_ZB[ename]
    return lambda co: (ex + (fr.s_of(co) + off) * L.LPPM,
                       ey + (co.z - zb) * L.LPPM)


# ========================================================== polygon faces
class Poly:
    """A planar face before triangulation: an outline and any holes, as 3D
    points, and the UV mapping its vertices take."""

    def __init__(self, loops, uvfn):
        self.loops = [[_key(p) for p in lp] for lp in loops]
        self.uvfn = uvfn


def tjunctions(polys):
    """Give every face every vertex that lies on one of its edges.

    Every shell face is axis-aligned, so a point lies on an edge when it
    shares the edge's two fixed coordinates and falls between its ends on
    the third. Indexed by those lines, the pass is linear in practice.
    """
    lines = ({}, {}, {})
    pts = {p for poly in polys for lp in poly.loops for p in lp}
    for p in pts:
        for ax in range(3):
            k = tuple(p[i] for i in range(3) if i != ax)
            lines[ax].setdefault(k, []).append(p[ax])
    for ax in range(3):
        for k in lines[ax]:
            lines[ax][k].sort()
    for poly in polys:
        new_loops = []
        for lp in poly.loops:
            out = []
            for a, b in zip(lp, lp[1:] + lp[:1]):
                out.append(a)
                diff = [i for i in range(3) if abs(a[i] - b[i]) > 1e-9]
                if len(diff) != 1:
                    continue
                ax = diff[0]
                k = tuple(a[i] for i in range(3) if i != ax)
                lo, hi = sorted((a[ax], b[ax]))
                mids = [v for v in lines[ax].get(k, ()) if lo + 1e-6 < v < hi - 1e-6]
                if a[ax] > b[ax]:
                    mids.reverse()
                for v in mids:
                    q = list(a)
                    q[ax] = v
                    out.append(tuple(q))
            new_loops.append(out)
        poly.loops = new_loops
    return polys


def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge."""
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


def emit(B, poly):
    """Triangulate *poly* in its own plane and add it to builder *B*."""
    o = poly.loops[0]
    n = [0.0, 0.0, 0.0]
    for (ax, ay, az), (bx, by, bz) in zip(o, o[1:] + o[:1]):
        n[0] += ay * bz - az * by
        n[1] += az * bx - ax * bz
        n[2] += ax * by - ay * bx
    drop = max(range(3), key=lambda i: abs(n[i]))
    d0, d1 = [i for i in range(3) if i != drop]
    flat3 = [p for lp in poly.loops for p in lp]
    flat2 = [(p[d0], p[d1]) for p in flat3]
    if len(poly.loops) == 1 and len(o) == 4:
        B.face(o, poly.uvfn)
        return
    tris = geometry.tessellate_polygon(
        [[Vector((p[d0], p[d1], 0.0)) for p in lp] for lp in poly.loops])
    for i, j, k in _flip_slivers(flat2, tris):
        B.face([flat3[i], flat3[j], flat3[k]], poly.uvfn)


# ================================================================== walls
def trace_cells(cells, ss, zs):
    """Outlines of a union of grid cells (i, j) over s-lines *ss* and z-lines
    *zs*: [(outer, [holes])], each loop as (s, z) points, collinear points
    dropped. Where two cells touch only at a corner the walk turns right,
    keeping the pieces apart."""
    edges = {}
    for i, j in cells:
        loop = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
        for a, b in zip(loop, loop[1:] + loop[:1]):
            if (b, a) in edges:
                del edges[(b, a)]
            else:
                edges[(a, b)] = True
    out = {}
    for a, b in edges:
        out.setdefault(a, []).append(b)
    loops = []
    while out:
        start = next(iter(out))
        loop = [start]
        cur = out[start].pop()
        prev = start
        if not out[start]:
            del out[start]
        while cur != start:
            loop.append(cur)
            nxt = out[cur]
            if len(nxt) > 1:
                dx, dy = cur[0] - prev[0], cur[1] - prev[1]

                def turn(q):
                    ex, ey = q[0] - cur[0], q[1] - cur[1]
                    return dx * ey - dy * ex       # > 0 is a left turn
                nxt.sort(key=turn)
            prev, cur = cur, nxt.pop(0)
            if not out[prev]:
                del out[prev]
        loops.append(loop)
    polys = []
    for lp in loops:
        pts = [(ss[i], zs[j]) for i, j in lp]
        simple = []
        n = len(pts)
        for k in range(n):
            a, b, c = pts[k - 1], pts[k], pts[(k + 1) % n]
            if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > 1e-12:
                simple.append(b)
        area = sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(simple, simple[1:] + simple[:1])) / 2.0
        polys.append((area, simple))
    outers = [(a, p) for a, p in polys if a > 0]
    holes = [p for a, p in polys if a < 0]
    result = [(p, []) for a, p in outers]

    def inside(pt, poly):
        x, y = pt
        c = False
        for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                c = not c
        return c
    for h in holes:
        probe = ((h[0][0] + h[1][0]) / 2.0 + 1e-4, (h[0][1] + h[1][1]) / 2.0 + 1e-4)
        owners = [r for r in result if inside(probe, r[0])]
        if not owners:
            raise ValueError("a hole in the brick has no outline round it")
        min(owners, key=lambda r: abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in
                                          zip(r[0], r[0][1:] + r[0][:1]))))[1].append(h)
    return result


def brick_regions(L_, zb, zt, inserts):
    """The brick of a wall from s 0..L_ and z zb..zt less *inserts* (s0, s1,
    z0, z1), as [(slab index, outline, holes)] in (s, z)."""
    ss = sorted({0.0, L_} | {v for r in inserts for v in r[:2] if 0.0 < v < L_})
    cuts = [c for c in L.CUTS if zb < c < zt]
    zs = sorted({zb, zt} | set(cuts) |
                {v for r in inserts for v in r[2:] if zb < v < zt})
    by_slab = {}
    for i in range(len(ss) - 1):
        sm = (ss[i] + ss[i + 1]) / 2.0
        for j in range(len(zs) - 1):
            zm = (zs[j] + zs[j + 1]) / 2.0
            if any(r[0] < sm < r[1] and r[2] < zm < r[3] for r in inserts):
                continue
            by_slab.setdefault(L.slab_of(zs[j]), set()).add((i, j))
    out = []
    for slab, cells in sorted(by_slab.items()):
        for outline, holes in trace_cells(cells, ss, zs):
            out.append((slab, outline, holes))
    return out


def wall_polys(name, level):
    """Every face of wall *name* at *level*, as Polys."""
    fr = wall_frame(name)
    Lw = fr.L
    zb, zt = L.WALLS[name][2:4]
    polys = []

    def P3(loop, out=0.0):
        return [fr.P(s, z, out) for s, z in loop]

    mode = opening_mode(level)
    if mode == "elevation":
        loop = [(0.0, zb), (Lw, zb), (Lw, zt), (0.0, zt)]
        fn = (uv_column(fr, 0.0, 0.0) if name.startswith("bh_ret")
              else uv_elevation(fr, name))
        return [Poly([P3(loop)], fn)]

    inserts = []
    for k, (s0, s1, z0, z1) in enumerate(L.column_rects(name)):
        inserts.append((s0, s1, z0, z1))
        polys.append(Poly([P3([(s0, z0), (s1, z0), (s1, z1), (s0, z1)])],
                          uv_column(fr, s0, 0.37 * k + 0.11 * len(name))))
    for item in L.ITEMS[name]:
        rect = L.item_rect(name, item)
        inserts.append(rect)
        polys += opening_polys(fr, item, rect, mode)
    for slab, outline, holes in brick_regions(Lw, zb, zt, inserts):
        polys.append(Poly([P3(outline)] + [P3(h) for h in holes],
                          uv_brick(fr, U_OFF[name], L.SLAB * slab)))
    return polys


def opening_polys(fr, item, rect, mode):
    """One opening: its closing plane, set back REVEAL with concrete reveals
    round it while cut, in the wall's plane when flush. A door has no
    threshold cheek: the floor cap covers its recess."""
    kind = item[0]
    s0, s1, z0, z1 = rect
    depth = L.REVEAL[kind] if mode == "cut" else 0.0
    polys = []
    if depth > 0.0:
        out = -depth
        if z0 > EPS:
            polys.append(Poly([[fr.P(s0, z0), fr.P(s0, z0, out), fr.P(s1, z0, out),
                                fr.P(s1, z0)]], uv_head(fr)))
        polys.append(Poly([[fr.P(s0, z1), fr.P(s1, z1), fr.P(s1, z1, out),
                            fr.P(s0, z1, out)]], uv_head(fr)))
        polys.append(Poly([[fr.P(s0, z0), fr.P(s0, z1), fr.P(s0, z1, out),
                            fr.P(s0, z0, out)]], uv_jamb(fr)))
        polys.append(Poly([[fr.P(s1, z0), fr.P(s1, z0, out), fr.P(s1, z1, out),
                            fr.P(s1, z1)]], uv_jamb(fr)))
    out = -depth
    if kind != "win":
        polys.append(Poly([[fr.P(s0, z0, out), fr.P(s1, z0, out), fr.P(s1, z1, out),
                            fr.P(s0, z1, out)]], uv_region(fr, L.REGION[kind], s0, z0)))
        return polys
    cols, periods = item[3]
    wx, wy = L.WINDOW[:2]
    sec_s, sec_z = L.window_sections(cols, periods)
    for a0, a1, ru in sec_s:
        for b0, b1, rv in sec_z:
            def fn(co, a0=a0, b0=b0, ru=ru, rv=rv):
                return (wx + (ru + fr.s_of(co) - s0 - a0) * PPM,
                        wy + (rv + co.z - z0 - b0) * PPM)
            polys.append(Poly([[fr.P(s0 + a0, z0 + b0, out), fr.P(s0 + a1, z0 + b0, out),
                                fr.P(s0 + a1, z0 + b1, out), fr.P(s0 + a0, z0 + b1, out)]],
                              fn))
    return polys


def cap_loops(B):
    """Close the shell: a floor and the two lids, one n-gon per rim loop,
    every one of them buried by the ground or a roof slab."""
    bm = B.bm
    bm.edges.index_update()
    order = [e for e in bm.edges if len(e.link_faces) == 1]
    rim = set(order)
    branch = [v for e in order for v in e.verts
              if sum(1 for x in v.link_edges if x in rim) != 2]
    if branch:
        c = branch[0].co
        raise ValueError("the shell's rim branches at %d vertices, e.g. "
                         "(%.3f, %.3f, %.3f): a T-junction there"
                         % (len(set(branch)), c.x, c.y, c.z))
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
    if len(loops) != 3:
        raise ValueError("expected a floor and two lids, got %d rim loops: a "
                         "T-junction somewhere" % len(loops))
    blank = uv_patch("blank")
    for lp in loops:
        zs = {round(v.co.z, 4) for v in lp}
        if len(zs) != 1:
            raise ValueError("a rim loop is not level: %s" % sorted(zs))
        B.set_uv(bm.faces.new(lp), blank)


def shell(level):
    polys = []
    for name in L.WALL_ORDER:
        polys += wall_polys(name, level)
    tjunctions(polys)
    B = Builder()
    for p in polys:
        emit(B, p)
    cap_loops(B)
    return B


# ================================================================== roofs
def uv_fascia(axis, zs):
    return lambda co: ((co.x if axis == "x" else co.y) * PPM,
                       L.FASCIA_Y0 + (co.z - zs) * PPM)


def uv_deck(x0, y0):
    x, y, w, h = L.DECK
    return lambda co: (x + (co.x - x0) * L.DPPM, y + (co.y - y0) * L.DPPM)


def parapet_roof(box, zs, zc, zd, open_west=False, flat=False):
    """A flat roof as one closed solid: the concrete edge beam oversailing
    the walls by O, from the soffit zs to the coping zc, and inside the
    parapet the deck sunk to zd. *open_west* leaves the west side without a
    parapet and runs the roof BURY into the boiler house, which trims it;
    *flat* draws the whole roof as a box to the coping."""
    x0, x1, y0, y1 = box
    xo0 = x0 - (L.BURY if open_west else L.O)
    xo1, yo0, yo1 = x1 + L.O, y0 - L.O, y1 + L.O
    B = Builder()
    outer = [(xo0, yo0), (xo1, yo0), (xo1, yo1), (xo0, yo1)]
    for k in range(4):
        (ax, ay), (bx, by) = outer[k], outer[(k + 1) % 4]
        if open_west and k == 3:
            continue
        axis = "x" if abs(ay - by) < EPS else "y"
        B.face([(ax, ay, zs), (bx, by, zs), (bx, by, zc), (ax, ay, zc)],
               uv_fascia(axis, zs))
    B.face([(x, y, zs) for x, y in reversed(outer)], uv_patch("soffit"))
    if flat:
        B.face([(x, y, zc) for x, y in outer], uv_patch("felt"))
        if open_west:
            B.face([(xo0, yo1, zs), (xo0, yo0, zs), (xo0, yo0, zc), (xo0, yo1, zc)],
                   uv_patch("blank"))
        return B
    xi0 = xo0 if open_west else x0 + L.PIN
    xi1, yi0, yi1 = x1 - L.PIN, y0 + L.PIN, y1 - L.PIN
    inner = [(xi0, yi0), (xi1, yi0), (xi1, yi1), (xi0, yi1)]
    for k in range(4):
        if open_west and k == 3:
            continue
        o0, o1 = outer[k], outer[(k + 1) % 4]
        i0, i1 = inner[k], inner[(k + 1) % 4]
        B.face([o0 + (zc,), o1 + (zc,), i1 + (zc,), i0 + (zc,)], uv_patch("coping"))
        B.face([i0 + (zc,), i1 + (zc,), i1 + (zd,), i0 + (zd,)], uv_patch("parapet_in"))
    B.face([(x, y, zd) for x, y in inner], uv_deck(xi0, yi0))
    if open_west:
        sec = [(yo0, zs), (yo0, zc), (yi0, zc), (yi0, zd), (yi1, zd), (yi1, zc),
               (yo1, zc), (yo1, zs)]
        B.face([(xo0, y, z) for y, z in reversed(sec)], uv_patch("blank"))
    return B


def roofs(level):
    flat = roof_flat(level)
    return [(parapet_roof(L.BH, L.Z_BS, L.Z_BC, L.Z_BD, flat=flat), "tmp_bh_roof"),
            (parapet_roof(L.TH, L.Z_TS, L.Z_TC, L.Z_TD, open_west=True, flat=flat),
             "tmp_th_roof")]


# ============================================================ other solids
def box(x0, x1, y0, y1, z0, z1, sides, top, bottom):
    """A closed box; *sides* is one mapping or four, south/east/north/west."""
    B = Builder()
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    fns = sides if isinstance(sides, (list, tuple)) else [sides] * 4
    for k in range(4):
        (ax, ay), (bx, by) = ring[k], ring[(k + 1) % 4]
        B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], fns[k])
    B.face([(x, y, z1) for x, y in ring], top)
    B.face([(x, y, z0) for x, y in reversed(ring)], bottom)
    return B


def monitor():
    """The boiler house's roof monitor: a box standing MON_H above the deck,
    its foot buried in the roof slab, every side a row of 2 m louvre
    modules under a sheet lid."""
    x0, x1, y0, y1 = L.MONITOR
    zb, zt = L.Z_BD - 0.2, L.Z_BD + L.MON_H
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    rx, ry, rw, rh = L.LOUVRE
    pts = []
    B = Builder()
    for k in range(4):
        (ax, ay), (bx, by) = ring[k], ring[(k + 1) % 4]
        length = math.hypot(bx - ax, by - ay)
        n = int(round(length / L.MOD))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            p = (ax + (bx - ax) * t0, ay + (by - ay) * t0)
            q = (ax + (bx - ax) * t1, ay + (by - ay) * t1)
            pts.append(p)

            def fn(co, p=p, d=((bx - ax) / length, (by - ay) / length)):
                t = (co.x - p[0]) * d[0] + (co.y - p[1]) * d[1]
                return (rx + t * PPM, ry + (co.z - L.Z_BD) * PPM)
            B.face([p + (zb,), q + (zb,), q + (zt,), p + (zt,)], fn)
    B.face([p + (zt,) for p in pts], uv_patch("lid"))
    B.face([p + (zb,) for p in reversed(pts)], uv_patch("blank"))
    return B


def ventilator(px, py):
    """A roof ventilator on the turbine hall: hollow, its flue sooted."""
    h = L.VENT_W / 2.0
    zb, zt = L.Z_TD - 0.2, L.Z_TD + L.VENT_H
    B = Builder()
    return open_stack(B, px - h, px + h, py - h, py + h, zb, zt, 0.06, 0.9,
                      uv_patch("duct"), uv_patch("rim"), uv_patch("soot"), uv_patch("blank"))


def flue_stub():
    """The flue's stub on the boiler house's rear wall, toward the chimney: a
    concrete casing projecting FLUE[2], its end closed by the steel blanking
    plate, its back buried in the wall."""
    x0, x1, proj, z0, hgt = L.FLUE
    y0, y1 = L.BH[3] - 0.2, L.BH[3] + proj
    fx, fy, fw, fh = L.FLUE_END

    def end(co):
        return (fx + (x1 - co.x) * PPM, fy + (co.z - z0) * PPM)
    conc = uv_patch("conc")
    return box(x0, x1, y0, y1, z0, z0 + hgt, [uv_patch("blank"), conc, end, conc],
               conc, uv_patch("soffit"))


def canopy():
    """The entrance canopy: a cast concrete slab, sunk into the wall."""
    x0, x1, proj, z0, t = L.CANOPY
    y1 = L.BH[2] + 0.15
    y0 = L.BH[2] - proj

    def edge(axis):
        return lambda co: ((co.x if axis == "x" else co.y) * PPM,
                           L.COL_Y0 + (co.z - z0) * PPM)
    return box(x0, x1, y0, y1, z0, z0 + t,
               [edge("x"), edge("y"), uv_patch("blank"), edge("y")],
               uv_patch("conc"), uv_patch("soffit"))


# ---------------------------------------------------------------- downpipes
# Two from each roof: on a column between bays on the front and the rear,
# running straight up into the edge beam's soffit, fed through the parapet.
DOWNPIPE_SPOTS = [("bh_front", -6.75), ("bh_rear", -11.25),
                  ("th_front", 11.25), ("th_rear", 2.25)]
DOWNPIPES = [DP.slab_pipe(*L.WALLS[w][:2], L.wall_s(w, c), L.SOFFIT[w])
             for w, c in DOWNPIPE_SPOTS]


def downpipes(level):
    return DP.solids(DOWNPIPES, *DP.MODES[level], L.PIPE_STRIP, L.ATLAS)


# ---------------------------------------------------------------- ladders
# A flat roof needs only the wall ladder up to it (CLAUDE.md): one from the
# ground up the turbine hall's rear wall, on a column, and one from the
# hall's deck up the boiler house's east face, in its rear bay.
PAINT = RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)
LADDER1_X = 11.25
LADDER2_Y = 5.5
EAVE1 = RS.Eave(*L.WALLS["th_rear"][:2], L.Z_TS, L.O, L.Z_TC, 0.0)
WALL1 = RS.WallLadder(EAVE1, L.wall_s("th_rear", LADDER1_X))
EAVE2 = RS.Eave(*L.WALLS["step"][:2], L.Z_BS, L.O, L.Z_BC, 0.0)
WALL2 = RS.WallLadder(EAVE2, L.wall_s("step", LADDER2_Y), foot=L.Z_TD + LADDER_HANG)


# Rungs every 0.28 m to 35 m, every other one to 70 m, as roof_safety's
# MODES; past 70 m the two ladders cost 430 triangles for rungs under half a
# pixel, so LOD2 keeps only their bare rails, touching nothing, appended
# after the cleanup, and LOD3 has no kit.
LADDER_MODES = (RS.MODES[0], RS.MODES[1], (None, False), (None, False))


def ladders(level):
    return RS.solids([WALL1, WALL2], level, PAINT, modes=LADDER_MODES)


def ladder_rails(level):
    return (RS.solids([WALL1, WALL2], level, PAINT, extents=True, modes=LADDER_MODES)
            if level == 2 else [])


# ================================================================ assembly
def build_lod(level):
    base = to_object(shell(level), "tmp_shell")
    parts = [to_object(B, n) for B, n in roofs(level)]
    parts.append(to_object(monitor(), "tmp_monitor"))
    parts.append(to_object(flue_stub(), "tmp_flue"))
    parts.append(to_object(canopy(), "tmp_canopy"))
    if vents_kept(level):
        for i, (px, py) in enumerate(L.VENTS):
            parts.append(to_object(ventilator(px, py), "tmp_vent%d" % i))
    for M, name in downpipes(level) + ladders(level):
        parts.append(to_object(M, name))
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # Recover the cost of coplanar subdivisions; keep UV and material
        # seams and every architectural edge.
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4],
                          quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.to_mesh(obj.data)
    bm.free()
    RS.append(obj, ladder_rails(level))
    return obj


# ================================================================== checks
def _overlap(a, b, gap=0.0):
    return a[0] < b[1] + gap and b[0] < a[1] + gap and a[2] < b[3] + gap and b[2] < a[3] + gap


def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    for name in L.WALL_ORDER:
        Lw = L.wall_len(name)
        zb, zt = L.WALLS[name][2:4]
        cols = L.column_rects(name)
        rects = [(it, L.item_rect(name, it)) for it in L.ITEMS[name]]
        for it, r in rects:
            tag = "%s: %s at %.2f" % (name, it[0], it[1])
            if r[0] < 0.3 or r[1] > Lw - 0.3:
                bad.append(tag + " is within 0.3 m of a corner")
            if r[2] < zb - EPS or r[3] > L.SOFFIT[name] - 0.3:
                bad.append(tag + " leaves the wall")
            if EPS < r[2] < 0.5:
                bad.append(tag + " leaves a sliver of plinth under it")
            if any(abs(z - c) < 0.1 for z in r[2:] for c in L.CUTS):
                bad.append(tag + " has an edge within 0.1 m of a slab line")
            for c in cols:
                if _overlap(r, c, 0.2):
                    bad.append(tag + " crowds a column")
        for i, (a, ra) in enumerate(rects):
            for b, rb in rects[i + 1:]:
                if _overlap(ra, rb, 0.3):
                    bad.append("%s: %s and %s within 0.3 m" % (name, a[0], b[0]))
    for kind, top in L.LEAF_TOP.items():
        if not 2.0 <= top <= 2.4:
            bad.append("the %s leaf is %.3f m" % (kind, top))
    # downpipes clear of the corners, the openings and the ladders
    for (w, c), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        avoid = [(it[0], *L.item_rect(w, it)[:2]) for it in L.ITEMS[w]]
        for wall, ladder, x in (("th_rear", WALL1, LADDER1_X), ("step", WALL2, LADDER2_Y)):
            if wall == w:
                avoid.append(("ladder", *ladder.span()))
        if w == "bh_front":
            avoid.append(("canopy", L.wall_s(w, L.CANOPY[0]), L.wall_s(w, L.CANOPY[1])))
        bad += DP.problems(pipe, "the %s downpipe" % w, avoid)
    for wall, ladder in (("th_rear", WALL1), ("step", WALL2)):
        avoid = [(it[0], *L.item_rect(wall, it)[:2]) for it in L.ITEMS[wall]]
        avoid += [("downpipe", p.s - DP.A, p.s + DP.A)
                  for (w, c), p in zip(DOWNPIPE_SPOTS, DOWNPIPES) if w == wall]
        bad += RS.problems(ladder, "the %s wall ladder" % wall, avoid)
    # roof things clear of each other and the parapets
    mx0, mx1, my0, my1 = L.MONITOR
    if mx0 < L.BH[0] + 1.0 or mx1 > L.BH[1] - 1.0 or my0 < L.BH[2] + 1.0 or my1 > L.BH[3] - 1.0:
        bad.append("the roof monitor crowds the boiler house's parapet")
    for px, py in L.VENTS:
        h = L.VENT_W / 2.0
        if px - h < L.TH[0] + 0.8 or px + h > L.TH[1] - 0.8 or abs(py) + h > L.TH[3] - 0.8:
            bad.append("the ventilator at (%.1f, %.1f) crowds a parapet" % (px, py))
        if abs(px - LADDER1_X) < 1.0 and py > L.TH[3] - 2.0:
            bad.append("the ventilator at (%.1f, %.1f) blocks the ladder" % (px, py))
    if L.Z_BD + L.MON_H < WALL2.eave.z_edge + RS.LADDER_TOP + 0.05:
        bad.append("the upper ladder, not the monitor, would set the height")
    return bad


# ================================================================== build
def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
# Clear leaf widths and heights, as facade_atlas.py paints them inside each
# door's 6 px steel frame.
LEAF = {
    "entrance": (L.SIZES["entrance"][0] - 2 * L.DOOR_FRAME, L.LEAF_TOP["entrance"]),
    "bigdoor": (L.SIZES["bigdoor"][0] - 2 * L.DOOR_FRAME,
                L.SIZES["bigdoor"][1] - L.DOOR_FRAME),
    "service": (L.SIZES["service"][0] - 2 * L.DOOR_FRAME, L.LEAF_TOP["service"]),
}


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the outer wall outline at the
    ground: the boiler house's 14 x 17 m and the turbine hall's 18 x 16 m,
    without the roof edges, the canopy, the flue stub, the pipes and the
    ladders. One storey: both halls' floors at the ground, which every door
    opens onto level; its area is inside the outer wall faces. The coal
    hatch high in the west wall is not a door."""
    def door(door_id, kind, wall, item, main=False):
        p0, p1 = L.WALLS[wall][:2]
        it, = [i for i in L.ITEMS[wall] if i[0] == item]
        w, h = LEAF[item]
        return model_facts.wall_door(door_id, kind, p0, p1, L.wall_s(wall, it[1]),
                                     it[2], w, h, main)

    bh = (L.BH[1] - L.BH[0]) * (L.BH[3] - L.BH[2])
    th = (L.TH[1] - L.TH[0]) * (L.TH[3] - L.TH[2])
    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [L.WALLS[n][0] for n in L.WALL_ORDER[:-1]],
        "storeys": [(0.0, bh + th)],
        "doors": [door("entrance", "entrance", "bh_front", "entrance", main=True),
                  door("machinery", "vehicle", "th_front", "bigdoor"),
                  door("service", "service", "th_rear", "service")],
    }


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four
    orthographic elevations, a plan from above, and a raised three-quarter
    aerial off the front corner; plus aerials off the other corners and eye
    views at the doors, the flue and the coal side. Working views only, not
    committed."""
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
    os.makedirs(out_dir, exist_ok=True)
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
    persp = [("aerial", centre, Vector((1.0, -1.0, math.sqrt(2.0))), 2.6),
             ("aerial_rear", centre, Vector((-1.0, 1.0, math.sqrt(2.0))), 2.6),
             ("aerial_west", centre, Vector((-1.0, -1.0, math.sqrt(2.0))), 2.6),
             ("aerial_east_rear", centre, Vector((1.0, 1.0, math.sqrt(2.0))), 2.6),
             ("eye_entrance", Vector((-9.0, -8.5, 3.0)), Vector((0.3, -1.0, 0.05)), 0.9),
             ("eye_bigdoor", Vector((13.5, -8.0, 3.5)), Vector((0.2, -1.0, 0.05)), 1.0),
             ("eye_flue", Vector((-9.0, 8.5, 12.0)), Vector((-0.6, 1.0, 0.1)), 1.0),
             ("eye_coal", Vector((-16.0, 0.0, 12.0)), Vector((-1.0, -0.4, -0.1)), 1.0),
             ("eye_step", Vector((-2.0, 3.0, 15.0)), Vector((1.0, 0.6, 0.35)), 0.8)]
    for name, target, d, k in persp:
        cam.data.type = 'PERSP'
        cam.data.lens = 35.0
        cam.location = target + d.normalized() * radius * k
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scn.render.filepath = os.path.join(out_dir, "L%d_%s.png" % (level, name))
        bpy.ops.render.render(write_still=True)
        written.append(scn.render.filepath)
    scn.camera, scn.render.resolution_x, scn.render.resolution_y = saved
    return written


if __name__ == "__main__":
    BUILD.main(build_all, facts)
