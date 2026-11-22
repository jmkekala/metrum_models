# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of voimalaitos_brick_hall, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

The boiler and turbine hall of a small mid-century Nordic town heat-and-power
plant: one block of two volumes in continuous red facing brick on a concrete
plinth, under flat roofs behind a low parapet with a light concrete coping.
The boiler house, 14 x 17 m and 19.5 m to its coping, is the west block, a
raised coal bunker bay along the rear half of its roof (to 24 m) and two
steel stub stacks in front of it; its front carries one tall central band
of narrow lights in three tiers on light spandrels. The turbine hall,
18 x 16 m and 11.6 m, abuts its east face: four tall hall windows and the
machinery door on the front, the lettering in the brick above them. The
boiler house's rear wall carries a closed flue stub toward the chimney, its
west wall the closed inlet the coal reception's conveyor gallery ends
against (the hall carries no gallery of its own); the turbine hall's east
end, toward the transformer yard, is nearly blank round a cable bushing
panel.

Construction. The walls of both volumes are one closed shell, meshed
directly: each wall is a rectangle less its openings and panels, cut into
3.75 m slabs of brick (facade_atlas.CUTS) whose outlines are traced from a grid
of cells; every face is then given every vertex that lies on its edges
(tjunctions()), so neighbours meet on shared vertices. Recessed openings
add their concrete reveals and the closing plane, the conveyor inlet its
steel frame standing 0.05 m proud on the copings' plane (the face the coal
reception's gallery butts against), steel reveals and blanking panel. On LOD0-LOD1 the
shell also carries both roofs' parapets and sunk decks, so it closes with
its floor alone; on LOD2-LOD3 two flat lids close it. The copings, the
bunker bay (its windows cut to LOD1), the stacks (with their rings), the
ventilators, the flue stub and the entrance canopy are closed solids of
their own, unioned with Blender's exact boolean. The wall ladders with their
cages are scripts/roof_safety.py's lean kit, appended after the cleanup.

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
    6 px/m elevations, every opening and panel painted on them."""
    return ("cut", "cut", "flush", "elevation")[level]


def roof_flat(level):
    """From LOD2 each roof closes with a lid under a coping box: the
    roofline stays; the deck sunk 0.875 m behind the parapet, a pixel or two
    deep past 70 m and hidden from the ground, goes."""
    return level >= 2


def vents_kept(level):
    """The two 0.8 m ventilators are hollow to LOD1 and go from LOD2: they
    stand 0.3 m over the coping, under three pixels past 70 m, and the
    parapet hides the rest from the ground."""
    return level < 2


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


def uv_brick(fr, u_off, shift):
    """The brick band from the wall's foot, *shift* metres lower above it."""
    return lambda co: ((fr.s_of(co) + u_off) * PPM,
                       L.BRICK_Y0 + (co.z - shift) * PPM)


def uv_conc(fr, z0):
    """A concrete panel: the concrete band, V up from the panel's foot."""
    return lambda co: (fr.s_of(co) * PPM, L.CONC_Y0 + (co.z - z0) * PPM)


def uv_jamb(fr):
    """A reveal's side: concrete, U up it, V the depth from the wall face."""
    return lambda co: (co.z * PPM, L.CONC_Y0 + (-fr.out_of(co)) * PPM)


def uv_head(fr):
    """A reveal's head or sill: U along the wall, V the depth."""
    return lambda co: (fr.s_of(co) * PPM, L.CONC_Y0 + (-fr.out_of(co)) * PPM)


def uv_region(fr, rect, s0, z0, ppm=PPM):
    x, y, w, h = rect
    return lambda co: (x + (fr.s_of(co) - s0) * ppm, y + (co.z - z0) * ppm)


def uv_elevation(fr, ename, off, zb):
    ex, ey, ew, eh = L.ELEV[ename]
    return lambda co: (ex + (fr.s_of(co) + off) * L.LPPM, ey + (co.z - zb) * L.LPPM)


def uv_cope(fr, z0):
    """The coping band along an edge, V up from the coping's foot."""
    return lambda co: (fr.s_of(co) * PPM, L.COPE_Y0 + (co.z - z0) * PPM)


def uv_deck(rect, origin):
    x, y, w, h = rect
    ox, oy = origin
    return lambda co: (x + (co.x - ox) * L.DPPM, y + (co.y - oy) * L.DPPM)


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


# where the two 0.5 m returns sample the LOD3 elevations: a blank strip of
# the neighbouring wall's brick at the same corner
RETURN_ELEV = {"bh_ret_front": ("front", 13.5), "bh_ret_rear": ("rear", 18.0)}


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
        if name in RETURN_ELEV:
            ename, off = RETURN_ELEV[name]
            fn = uv_elevation(fr, ename, off, 0.0)
        else:
            ename, off = L.WALL_ELEV[name]
            fn = uv_elevation(fr, ename, off, L.ELEV_ZB[ename])
        return [Poly([P3(loop)], fn)]

    inserts = []
    if name == "step" and not roof_flat(level):
        # between the hall's parapets the boiler house's face runs on down
        # to the hall's deck; behind the parapets' ends it is buried
        zb = L.Z_TD
        inserts += [(0.0, L.PIN, zb, L.Z_TWT), (Lw - L.PIN, Lw, zb, L.Z_TWT)]
    for item in L.ITEMS[name]:
        rect = L.item_rect(name, item)
        inserts.append(rect)
        cuts = [L.item_rect(name, o) for o in L.ITEMS[name] if o[0] == NOTCHED.get(item[0])]
        polys += item_polys(fr, item, rect, mode, cuts)
    for slab, outline, holes in brick_regions(Lw, zb, zt, inserts):
        polys.append(Poly([P3(outline)] + [P3(h) for h in holes],
                          uv_brick(fr, L.U_OFF[name], L.SLAB * slab)))
    return polys


# A flush panel cut round another item on its wall: the dusted brick round
# and under the conveyor inlet runs up either side of the inlet's frame.
NOTCHED = {"mouth": "inlet"}


def panel_outlines(rect, cuts):
    """The panel *rect* less the rects *cuts*, as [(outline, holes)] in
    (s, z), traced from a grid of cells as the brick is."""
    s0, s1, z0, z1 = rect
    ss = sorted({s0, s1} | {v for r in cuts for v in r[:2] if s0 < v < s1})
    zs = sorted({z0, z1} | {v for r in cuts for v in r[2:] if z0 < v < z1})
    cells = set()
    for i in range(len(ss) - 1):
        sm = (ss[i] + ss[i + 1]) / 2.0
        for j in range(len(zs) - 1):
            zm = (zs[j] + zs[j + 1]) / 2.0
            if not any(r[0] < sm < r[1] and r[2] < zm < r[3] for r in cuts):
                cells.add((i, j))
    return trace_cells(cells, ss, zs)


def item_polys(fr, item, rect, mode, cuts=()):
    """One opening or flush panel's faces."""
    kind = item[0]
    s0, s1, z0, z1 = rect
    if kind == "inlet":
        return inlet_polys(fr, rect, mode)
    if kind in L.FLUSH:
        fn = (uv_conc(fr, z0) if kind == "conc" else
              uv_region(fr, L.REGION[kind], s0, z0, L.REGION_PPM.get(kind, PPM)))
        if cuts:
            return [Poly([[fr.P(s, z) for s, z in lp] for lp in [outline] + holes], fn)
                    for outline, holes in panel_outlines(rect, cuts)]
        quad = [fr.P(s0, z0), fr.P(s1, z0), fr.P(s1, z1), fr.P(s0, z1)]
        return [Poly([quad], fn)]
    return opening_polys(fr, item, rect, mode)


def inlet_polys(fr, rect, mode):
    """The closed conveyor inlet, *rect* its flashing frame's outline. The
    frame is a steel ring INLET_FRAME wide standing INLET_PROUD off the
    brick, part of the shell: its face, flat, on the copings' outer plane
    (the hall's bounds), which the coal reception's gallery's end butts
    against, and its four outer returns down to the wall. While openings
    are cut (LOD0/LOD1) the opening's steel reveals run from the frame's
    face INLET_DEPTH behind the brick to the blanking panel closing it;
    flush (LOD2), the reveals stop at the brick and the panel lies in the
    wall's plane. Frame face and panel sample the inlet's region where they
    stand on the wall, the returns and the reveals the galvanised lining."""
    s0, s1, z0, z1 = rect
    fn = uv_region(fr, L.INLET, s0, z0, L.IPPM)
    f, p = L.INLET_FRAME, L.INLET_PROUD
    d = -L.INLET_DEPTH if mode == "cut" else 0.0
    a0, a1, b0, b1 = s0 + f, s1 - f, z0 + f, z1 - f
    lining = uv_patch("lining")
    return [
        # the frame's face, round the opening
        Poly([[fr.P(s0, z0, p), fr.P(s1, z0, p), fr.P(s1, z1, p), fr.P(s0, z1, p)],
              [fr.P(a0, b0, p), fr.P(a0, b1, p), fr.P(a1, b1, p), fr.P(a1, b0, p)]], fn),
        # its outer returns, down to the brick
        Poly([[fr.P(s0, z0), fr.P(s0, z0, p), fr.P(s1, z0, p), fr.P(s1, z0)]], lining),
        Poly([[fr.P(s0, z1), fr.P(s1, z1), fr.P(s1, z1, p), fr.P(s0, z1, p)]], lining),
        Poly([[fr.P(s0, z0), fr.P(s0, z1), fr.P(s0, z1, p), fr.P(s0, z0, p)]], lining),
        Poly([[fr.P(s1, z0), fr.P(s1, z0, p), fr.P(s1, z1, p), fr.P(s1, z1)]], lining),
        # the opening's reveals, from the frame's face to the panel
        Poly([[fr.P(a0, b0, p), fr.P(a0, b0, d), fr.P(a1, b0, d), fr.P(a1, b0, p)]], lining),
        Poly([[fr.P(a0, b1, p), fr.P(a1, b1, p), fr.P(a1, b1, d), fr.P(a0, b1, d)]], lining),
        Poly([[fr.P(a0, b0, p), fr.P(a0, b1, p), fr.P(a0, b1, d), fr.P(a0, b0, d)]], lining),
        Poly([[fr.P(a1, b0, p), fr.P(a1, b0, d), fr.P(a1, b1, d), fr.P(a1, b1, p)]], lining),
        # the blanking panel
        Poly([[fr.P(a0, b0, d), fr.P(a1, b0, d), fr.P(a1, b1, d), fr.P(a0, b1, d)]], fn),
    ]


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
    cols, rows = item[3]
    wx, wy = L.WINDOW[:2]
    sec_s, sec_z = L.window_sections(cols, rows)
    # the opening is whole courses tall; the pane rows stretch to it
    k = L.win_k(rows)
    for a0, a1, ru in sec_s:
        for b0, b1, rv in sec_z:
            def fn(co, a0=a0, b0=b0, ru=ru, rv=rv):
                return (wx + (ru + fr.s_of(co) - s0 - a0) * PPM,
                        wy + (rv + (co.z - z0) / k - b0) * PPM)
            polys.append(Poly([[fr.P(s0 + a0, z0 + k * b0, out),
                                fr.P(s0 + a1, z0 + k * b0, out),
                                fr.P(s0 + a1, z0 + k * b1, out),
                                fr.P(s0 + a0, z0 + k * b1, out)]], fn))
    return polys


def roof_polys(level):
    """Both roofs' parapets and sunk decks as part of the shell: the
    parapet's top at the wall tops (inside the coping), its inner faces in
    brick down to the deck, and the deck. The turbine hall's parapet is a U
    open to the boiler house, its deck running to the step face."""
    if roof_flat(level):
        return []
    polys = []
    blank = uv_patch("blank")
    x0, x1, y0, y1 = L.BH
    p = L.PIN
    outer = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    inner = [(x0 + p, y0 + p), (x1 - p, y0 + p), (x1 - p, y1 - p), (x0 + p, y1 - p)]
    zt, zd = L.Z_BWT, L.Z_BD
    polys.append(Poly([[q + (zt,) for q in outer], [q + (zt,) for q in inner]], blank))
    # the inner faces turn the bond at their corners too: every other face
    # a half stretcher along
    for k in range(4):
        a, b = inner[k], inner[(k + 1) % 4]
        fr = Frame(b, a)                        # out faces into the deck
        polys.append(Poly([[a + (zd,), b + (zd,), b + (zt,), a + (zt,)]],
                          uv_brick(fr, (k % 2) * L.HALF, L.SLAB * L.slab_of(zd))))
    polys.append(Poly([[q + (zd,) for q in inner]], uv_deck(L.DECK_B, L.DECK_B_O)))

    x0, x1, y0, y1 = L.TH
    zt, zd = L.Z_TWT, L.Z_TD
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y1 - p), (x1 - p, y1 - p),
            (x1 - p, y0 + p), (x0, y0 + p)]
    polys.append(Poly([[q + (zt,) for q in ring]], blank))
    for k, (a, b) in enumerate(((ring[7], ring[6]), (ring[6], ring[5]), (ring[5], ring[4]))):
        fr = Frame(b, a)
        polys.append(Poly([[a + (zd,), b + (zd,), b + (zt,), a + (zt,)]],
                          uv_brick(fr, (k % 2) * L.HALF, L.SLAB * L.slab_of(zd))))
    deck = [ring[7], ring[6], ring[5], ring[4]]
    polys.append(Poly([[q + (zd,) for q in deck]], uv_deck(L.DECK_T, L.DECK_T_O)))
    return polys


def cap_loops(B, expect):
    """Close the shell: the floor, and on a flat-roofed tier the two lids,
    one n-gon per rim loop, every one of them buried by the ground or a
    coping."""
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
    if len(loops) != expect:
        c = loops[-1][0].co if loops else Vector()
        raise ValueError("expected %d rim loops, got %d: a T-junction somewhere, "
                         "e.g. near (%.3f, %.3f, %.3f)" % (expect, len(loops), c.x, c.y, c.z))
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
    polys += roof_polys(level)
    tjunctions(polys)
    B = Builder()
    for p in polys:
        emit(B, p)
    cap_loops(B, 3 if roof_flat(level) else 1)
    return B


# ================================================================ copings
def prism(B, ring, z0, z1, side_fns, top, bottom):
    """A closed prism over plan polygon *ring* (outer loop, optional holes
    as further loops) from z0 to z1; *side_fns* maps each loop's edge index
    to a UV function."""
    for li, lp in enumerate(ring):
        for k in range(len(lp)):
            a, b = lp[k], lp[(k + 1) % len(lp)]
            B.face([a + (z0,), b + (z0,), b + (z1,), a + (z1,)], side_fns(li, k, a, b))
    emit(B, Poly([[q + (z1,) for q in lp] for lp in ring], top))
    emit(B, Poly([[q + (z0,) for q in reversed(lp)] for lp in ring], bottom))
    return B


def coping_side(z0, blank_edges=()):
    def fn(li, k, a, b):
        if (li, k) in blank_edges:
            return uv_patch("blank")
        return uv_cope(Frame(a, b), z0)
    return fn


def copings(level):
    """The parapets' copings: a ring 0.375 m tall over each parapet, CO
    proud of the brick outside and CO_IN inside, the walls running WALL_IN
    up into it; on LOD3 a box over the whole roof, its top the deck. The
    turbine hall's runs BURY into the boiler house at both ends."""
    co, ci, p = L.CO, L.CO_IN, L.PIN
    out = []
    x0, x1, y0, y1 = L.BH
    # the west face is cut over the conveyor inlet: its middle samples the
    # dusted coping (COPE_DUST), the rest the band, all along one frame
    ya, yb = L.INLET_Y + L.COPE_DUST_HALF, L.INLET_Y - L.COPE_DUST_HALF
    o = [(x0 - co, y0 - co), (x1 + co, y0 - co), (x1 + co, y1 + co), (x0 - co, y1 + co),
         (x0 - co, ya), (x0 - co, yb)]
    zs, zc = L.Z_BS, L.Z_BC
    west = Frame((x0 - co, y1 + co), (x0 - co, y0 - co))
    dx, dy = L.COPE_DUST[:2]
    dust = (lambda co_: (dx + (west.s_of(co_) - L.cope_dust_s0()) * PPM,
                         dy + (co_.z - zs) * PPM))
    plain = coping_side(zs)

    def bh_side(li, k, a, b):
        if li == 0 and k == 4:
            return dust
        if li == 0 and k in (3, 5):
            return uv_cope(west, zs)
        return plain(li, k, a, b)
    if roof_flat(level):
        B = prism(Builder(), [o], zs, zc, bh_side,
                  uv_deck(L.DECK_B, L.DECK_B_O), uv_patch("soffit"))
    else:
        i = [(x0 + p + ci, y0 + p + ci), (x0 + p + ci, y1 - p - ci),
             (x1 - p - ci, y1 - p - ci), (x1 - p - ci, y0 + p + ci)]
        B = prism(Builder(), [o, i], zs, zc, bh_side, uv_patch("cope_top"),
                  uv_patch("soffit"))
    out.append((B, "tmp_bh_coping"))

    x0, x1, y0, y1 = L.TH
    xb = x0 - L.BURY
    zs, zc = L.Z_TS, L.Z_TC
    if roof_flat(level):
        o = [(xb, y0 - co), (x1 + co, y0 - co), (x1 + co, y1 + co), (xb, y1 + co)]
        B = prism(Builder(), [o], zs, zc, coping_side(zs, ((0, 3),)),
                  uv_deck(L.DECK_T, L.DECK_T_O), uv_patch("soffit"))
    else:
        q = p + ci
        u = [(xb, y0 - co), (x1 + co, y0 - co), (x1 + co, y1 + co), (xb, y1 + co),
             (xb, y1 - q), (x1 - q, y1 - q), (x1 - q, y0 + q), (xb, y0 + q)]
        B = prism(Builder(), [u], zs, zc, coping_side(zs, ((0, 3), (0, 7))),
                  uv_patch("cope_top"), uv_patch("soffit"))
    out.append((B, "tmp_th_coping"))
    return out


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


def bunker_windows(length):
    """Where along a bunker bay face of *length* its windows are centred: one
    in the middle, the rest every BUNKER_PITCH, as the band paints them."""
    n = int((length / 2.0 - L.SQ_W / 2.0 - 0.3) // L.BUNKER_PITCH)
    return [length / 2.0 + L.BUNKER_PITCH * k for k in range(-n, n + 1)]


def bunker_u(length):
    """Where a bunker bay face of *length* samples the brick band in U: as
    the window row's band does (a window on the face's middle, at
    BUNKER_PITCH / 2 in the band), so the bond runs on across the row's
    edges, and its corners turn the bond (check_layout())."""
    return (L.BUNKER_PITCH / 2.0 - length / 2.0) % (L.ATLAS / PPM)


def split_at_cuts(z0, z1):
    """z0 .. z1 cut at the brick's slab lines, as (z0, z1) pieces."""
    zs = [z0] + [c for c in L.CUTS if z0 + EPS < c < z1 - EPS] + [z1]
    return list(zip(zs, zs[1:]))


# Where the bay's buried west foot steps back behind the conveyor inlet.
BUNKER_STEP = 0.05
BUNKER_STEP_Z = 19.0


def bunker(level):
    """The raised coal bunker bay: one box on the boiler house's roof, its
    foot buried in the deck, each face four bands: brick, the window row
    (a window centred on the face, the rest every BUNKER_PITCH), brick, the
    coping. While openings are cut (LOD0/LOD1) each window is cut into the
    row with its reveals, the closing plane the small square window's
    region; from LOD2 the band's painted windows stand flush.

    The west face stands 0.125 m behind the wall under it, inside the
    parapet, but the conveyor inlet below is recessed further (INLET_DEPTH)
    and its head is above the deck: so below BUNKER_STEP_Z, where the
    parapet hides it, the bay's west face steps back BUNKER_STEP, behind
    the inlet's blanking panel, and the recess stays open. Nothing of the
    step shows."""
    x0, x1, y0, y1 = L.BUNKER
    zb = L.Z_BD - 0.2
    w0, w1 = L.BUNKER_WIN
    d, zs = BUNKER_STEP, BUNKER_STEP_Z
    blank = uv_patch("blank")
    cut = opening_mode(level) == "cut"
    # the brick bands cut at the slab lines, each piece sampling its slab
    bands = ([(a, b, "brick") for a, b in split_at_cuts(zb, w0)] + [(w0, w1, "band")]
             + [(a, b, "brick") for a, b in split_at_cuts(w1, L.BUNKER_COPE)]
             + [(L.BUNKER_COPE, L.BUNKER_TOP, "cope")])
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    polys = []
    for k in range(4):
        a, b = ring[k], ring[(k + 1) % 4]
        fr = Frame(a, b)
        half = fr.L / 2.0
        for z0, z1, what in bands:
            holes = []
            if what == "brick":
                fn = uv_brick(fr, bunker_u(fr.L), L.SLAB * L.slab_of(z0))
            elif what == "band":
                fn = (lambda co, fr=fr: (
                    (fr.s_of(co) + bunker_u(fr.L)) * PPM,
                    L.BUNK_Y0 + (co.z - w0) * PPM))
                if cut:
                    for sc in bunker_windows(fr.L):
                        rect = (sc - L.SQ_W / 2.0, sc + L.SQ_W / 2.0, L.BUNKER_SILL,
                                L.BUNKER_SILL + L.SQ_H)
                        holes.append([fr.P(rect[0], rect[2]), fr.P(rect[0], rect[3]),
                                      fr.P(rect[1], rect[3]), fr.P(rect[1], rect[2])])
                        polys += opening_polys(fr, ("sq", sc, rect[2], None), rect, "cut")
            else:
                fn = uv_cope(fr, z0)
            outline = [(0.0, z0), (fr.L, z0), (fr.L, z1), (0.0, z1)]
            if z0 == zb and k == 0:             # front: its west end steps back
                outline = [(d, zb), (fr.L, zb), (fr.L, z1), (0.0, z1), (0.0, zs), (d, zs)]
            elif z0 == zb and k == 2:           # rear: likewise
                outline = [(0.0, zb), (fr.L - d, zb), (fr.L - d, zs), (fr.L, zs),
                           (fr.L, z1), (0.0, z1)]
            elif z0 == zb and k == 3:           # west: from the step up
                outline = [(0.0, zs), (fr.L, zs), (fr.L, z1), (0.0, z1)]
            polys.append(Poly([[fr.P(s_, z_) for s_, z_ in outline]] + holes, fn))
    lo = Frame((x0 + d, y1), (x0 + d, y0))
    polys.append(Poly([[lo.P(0.0, zb), lo.P(lo.L, zb), lo.P(lo.L, zs), lo.P(0.0, zs)]], blank))
    polys.append(Poly([[(x0, y0, zs), (x0, y1, zs), (x0 + d, y1, zs), (x0 + d, y0, zs)]], blank))
    foot = [(x0 + d, y0), (x1, y0), (x1, y1), (x0 + d, y1)]
    polys.append(Poly([[q + (L.BUNKER_TOP,) for q in ring]], uv_deck(L.DECK_B, L.DECK_B_O)))
    polys.append(Poly([[q + (zb,) for q in reversed(foot)]], blank))
    B = Builder()
    for p in polys:
        emit(B, p)
    return B


def stack_rings(level):
    """The stacks' rings modelled at *level*, (z0, z1, proud): the rolled cap
    ring, which shapes the mouth's outline, to 70 m; the two stiffening
    rings to 35 m. Every ring is painted at every tier, so a tier without
    its geometry keeps it in the texture."""
    return ((L.STACK_STIFF if level == 0 else ()) + ((L.STACK_CAP,) if level <= 1 else ()))


def stub_stack(cx, cy, level):
    """A steel stub stack on the boiler house's deck: an octagon STACK_R to
    its corners, open at the top round a flue sunk STACK_DEPTH and sooted,
    its foot buried in the deck; its rings (stack_rings()) stand proud of
    the plate. Face STACK_LADDER_FACE samples the ladder's region (STACK_L,
    turned a quarter), the others the plain face (STACK)."""
    n = 8
    r = L.STACK_R
    ri = r - L.STACK_WALL / math.cos(math.pi / n)
    zb, zt = L.Z_BD - 0.2, L.STACK_TOP
    zf = zt - L.STACK_DEPTH
    ang = [2.0 * math.pi * (k + 0.5) / n for k in range(n)]
    prof = [(zb, r)]
    rings = stack_rings(level)
    for z0, z1, d in sorted(rings):
        rr = r + d / math.cos(math.pi / n)          # d proud across the flats
        if z1 >= zt - 1e-9:
            prof += [(z0, r), (z0, rr), (zt, rr)]
        else:
            prof += [(z0, r), (z0, rr), (z1, rr), (z1, r)]
    if prof[-1][0] < zt - 1e-9:
        prof.append((zt, r))
    r_top = prof[-1][1]

    def ring_at(rad):
        return [(cx + rad * math.cos(a), cy + rad * math.sin(a)) for a in ang]
    base = ring_at(r)
    flue = ring_at(ri)
    top = ring_at(r_top)
    sx, sy, sw, sh = L.STACK
    lx, ly, lw, lh = L.STACK_L
    B = Builder()
    rim, soot = uv_patch("rim"), uv_patch("soot")
    for k in range(n):
        fr = Frame(base[k], base[(k + 1) % n])
        if k == L.STACK_LADDER_FACE:
            fn = (lambda co, fr=fr: (lx + (co.z - L.Z_BD) * L.SPPM, ly + fr.s_of(co) * L.SPPM))
        else:
            fn = (lambda co, fr=fr: (sx + fr.s_of(co) * L.SPPM, sy + (co.z - L.Z_BD) * L.SPPM))
        for (za, ra), (zc, rc) in zip(prof, prof[1:]):
            a0, b0 = ring_at(ra)[k], ring_at(ra)[(k + 1) % n]
            a1, b1 = ring_at(rc)[k], ring_at(rc)[(k + 1) % n]
            B.face([a0 + (za,), b0 + (za,), b1 + (zc,), a1 + (zc,)], fn)
        a, b = top[k], top[(k + 1) % n]
        B.face([a + (zt,), b + (zt,), flue[(k + 1) % n] + (zt,), flue[k] + (zt,)], rim)
        fa, fb = flue[(k + 1) % n], flue[k]
        B.face([fa + (zf,), fb + (zf,), fb + (zt,), fa + (zt,)], soot)
    B.face([q + (zf,) for q in flue], soot)
    B.face([q + (zb,) for q in reversed(base)], uv_patch("blank"))
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
    sx, sy, sw, sh = L.FLUE_SIDE

    def end(co):
        return (fx + (x1 - co.x) * PPM, fy + (co.z - z0) * PPM)

    def side(co):
        return (sx + (co.z - z0) * L.FPPM, sy + max(0.0, co.y - L.BH[3]) * L.FPPM)
    return box(x0, x1, y0, y1, z0, z0 + hgt, [uv_patch("blank"), side, end, side],
               uv_patch("conc"), uv_patch("soffit"))


def canopy():
    """The entrance canopy: a cast concrete slab, sunk into the wall."""
    x0, x1, proj, z0, t = L.CANOPY
    y1 = L.BH[2] + 0.15
    y0 = L.BH[2] - proj

    def edge(axis):
        return lambda co: ((co.x if axis == "x" else co.y) * PPM,
                           L.CONC_Y0 + (co.z - z0) * PPM)
    return box(x0, x1, y0, y1, z0, z0 + t,
               [edge("x"), edge("y"), uv_patch("blank"), edge("y")],
               uv_patch("conc"), uv_patch("soffit"))


# ---------------------------------------------------------------- ladders
# The roofs are flat decks, so CLAUDE.md asks only for a wall ladder up to
# each, and the two make one route: from the ground up the turbine hall's
# rear wall, across the hall's deck, and up the boiler house's east face to
# its deck, where the stacks stand. Nothing serviced stands on the bunker
# bay's roof, so no third ladder. Both run more than 8 m and carry a cage.
PAINT = RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)
LADDER1_X = 11.25
LADDER2_Y = 0.0
BRACKET_PITCH = 2.4     # the most between two wall brackets


def brackets(eave, foot):
    top = eave.z_wall - RS.SOFFIT_CLEAR - foot
    n = max(1, int(math.ceil((top - 0.6) / BRACKET_PITCH - 1e-9)))
    return [0.6 + (top - 0.6) * k / n for k in range(n + 1)]


# The lean kit (scripts/roof_safety.py): rails, rungs, brackets, hoops and
# straps as separate closed solids that touch nothing, appended after the
# union and the cleanup on every tier but LOD3, so nothing is cut. The walls
# are flush (the plinth too) and the copings oversail 0.05 m, 0.12 m inside
# the rails, so no bracket needs *behind*.
EAVE1 = RS.Eave(*L.WALLS["th_rear"][:2], L.Z_TS, L.CO, L.Z_TC, 0.0)
WALL1 = RS.WallLadder(EAVE1, L.wall_s("th_rear", LADDER1_X), brackets=brackets(EAVE1, 0.0),
                      lean=True)
EAVE2 = RS.Eave(*L.WALLS["step"][:2], L.Z_BS, L.CO, L.Z_BC, 0.0)
FOOT2 = L.Z_TD + LADDER_HANG
WALL2 = RS.WallLadder(EAVE2, L.wall_s("step", LADDER2_Y), foot=FOOT2,
                      brackets=brackets(EAVE2, FOOT2), lean=True)
# Rungs and brackets: every one to 35 m, every other one to 70 m; past that
# bare rails and the cages' back straps (LOD2); LOD3 has no kit. Cage hoops:
# every one, then every other one, the top one always.
LADDER_MODES = ((1, True), (2, True), (None, False), (None, False))
CAGE_MODES = (1, 2, None, None)
CAGE1 = RS.Cage(WALL1, modes=CAGE_MODES)
CAGE2 = RS.Cage(WALL2, modes=CAGE_MODES)
# From LOD2 the hall's roof is its coping box, its top 0.875 m over the deck
# the upper ladder hangs above, so there its bare rails start just on the
# box (hidden behind the parapet from the ground either way) and its back
# strap keeps the cage's hoops' heights.
WALL2_FLAT = RS.WallLadder(EAVE2, L.wall_s("step", LADDER2_Y), foot=L.Z_TC + 0.01,
                           lean=True)
CAGE2_FLAT = RS.Cage(WALL2_FLAT, foot=CAGE2.hoops[0], top=CAGE2.hoops[-1],
                     modes=CAGE_MODES)


def kit(level):
    """The roof safety kit's parts at *level*, for one RS.append()."""
    upper = [WALL2_FLAT, CAGE2_FLAT] if roof_flat(level) else [WALL2, CAGE2]
    return [WALL1, CAGE1] + upper


# ================================================================ assembly
def build_lod(level):
    base = to_object(shell(level), "tmp_shell")
    parts = [to_object(B, n) for B, n in copings(level)]
    parts.append(to_object(bunker(level), "tmp_bunker"))
    for i, (px, py) in enumerate(L.STACKS):
        parts.append(to_object(stub_stack(px, py, level), "tmp_stack%d" % i))
    parts.append(to_object(flue_stub(), "tmp_flue"))
    parts.append(to_object(canopy(), "tmp_canopy"))
    if vents_kept(level):
        for i, (px, py) in enumerate(L.VENTS):
            parts.append(to_object(ventilator(px, py), "tmp_vent%d" % i))
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
    if level < 3:
        RS.append(obj, RS.solids(kit(level), level, PAINT, extents=True, modes=LADDER_MODES),
                  check=True)
    return obj


# ================================================================== checks
def _overlap(a, b, gap=0.0):
    return a[0] < b[1] + gap and b[0] < a[1] + gap and a[2] < b[3] + gap and b[2] < a[3] + gap


def _avoid(wall):
    return [(it[0], *L.item_rect(wall, it)[:2]) for it in L.ITEMS[wall]
            if it[0] not in ("conc",)]


def _on(v, step):
    return abs(v / step - round(v / step)) < 1e-6


def brick_problems():
    """The brickwork, on the catalog module (scripts/brickwork.py): every
    height brick meets something at on a course line; every opening's
    side, and so every pier, on a whole or half stretcher in the U its wall
    samples; the bond turning a half stretcher at every corner. The
    conveyor inlet is the exception, sized and placed by the coal
    reception's gallery (its proud frame covers the cut); the lettering and
    the dusted panel are brick continuing brick, held to the band's rows
    and U by facade_atlas.check_regions()."""
    bad = []
    c, h = L.COURSE, L.HALF
    heights = [("plinth", L.Z_PLINTH), ("boiler house coping's foot", L.Z_BS),
               ("hall coping's foot", L.Z_TS), ("boiler house deck", L.Z_BD),
               ("hall deck", L.Z_TD), ("brick band's top", L.BAND_TOP),
               ("bunker window row", L.BUNKER_WIN[0]), ("bunker window row's top", L.BUNKER_WIN[1]),
               ("bunker coping's foot", L.BUNKER_COPE), ("bunker windows' sill", L.BUNKER_SILL),
               ("bunker windows' head", L.BUNKER_SILL + L.SQ_H),
               ("canopy", L.CANOPY[3]), ("canopy's top", L.CANOPY[3] + L.CANOPY[4]),
               ("flue stub", L.FLUE[3]), ("flue stub's top", L.FLUE[3] + L.FLUE[4])]
    heights += [("slab line", z) for z in L.CUTS + (L.SLAB,)]
    for what, z in heights:
        if not _on(z, c):
            bad.append("the %s at %.6f m is off the coursing" % (what, z))
    for name in L.WALL_ORDER:
        u = L.U_OFF[name]
        for it in L.ITEMS[name]:
            if it[0] == "inlet":
                continue
            s0, s1, z0, z1 = L.item_rect(name, it)
            tag = "%s: %s at %.4f, %.4f" % (name, it[0], it[1], it[2])
            if not (_on(z0, c) and _on(z1, c)):
                bad.append(tag + " is off the coursing")
            if it[0] in ("letters", "mouth"):
                continue
            if not (_on(u + s0, h) and _on(u + s1, h)):
                bad.append(tag + " cuts the bond off a half stretcher")
    for wall, xa, xb in (("bh_front", L.CANOPY[0], L.CANOPY[1]),
                         ("bh_rear", L.FLUE[0], L.FLUE[1])):
        u = L.U_OFF[wall]
        if not (_on(u + L.wall_s(wall, xa), h) and _on(u + L.wall_s(wall, xb), h)):
            bad.append("the %s's sides on %s are off a half stretcher" % (
                "canopy" if wall == "bh_front" else "flue stub", wall))
    ring = L.WALL_ORDER[:-1]
    for a, b in zip(ring, ring[1:] + ring[:1]):
        end = L.U_OFF[a] + L.wall_len(a)
        if not (_on(L.U_OFF[b], h) and _on(end - L.U_OFF[b] - h, L.BRICK_L)):
            bad.append("the %s/%s corner does not turn the bond" % (a, b))
    # the boiler house's east face above the hall: the front return, the
    # step face and the rear return in one plane, on one bond
    if not (_on(L.U_OFF["step"] - L.U_OFF["bh_ret_front"] - L.wall_len("bh_ret_front"),
                L.BRICK_L) and
            _on(L.U_OFF["step"] + L.wall_len("step") - L.U_OFF["bh_ret_rear"], L.BRICK_L)):
        bad.append("the step face does not run on the returns' bond")
    # the bunker bay: its plan, corners and windows on the grid
    x0, x1, y0, y1 = L.BUNKER
    lens = [x1 - x0, y1 - y0, x1 - x0, y1 - y0]
    if not all(_on(v, h) for v in (x0, x1, y0, y1)):
        bad.append("the bunker bay's faces are off the half-stretcher grid")
    for k in range(4):
        la, lb = lens[k], lens[(k + 1) % 4]
        if not _on(bunker_u(la) + la - bunker_u(lb) - h, L.BRICK_L):
            bad.append("a bunker bay corner does not turn the bond")
        for sc in bunker_windows(la):
            if not (_on(bunker_u(la) + sc - L.SQ_W / 2.0, h)
                    and _on(bunker_u(la) + sc + L.SQ_W / 2.0, h)):
                bad.append("a bunker bay window cuts the bond off a half stretcher")
    return bad


def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    for name in L.WALL_ORDER:
        Lw = L.wall_len(name)
        zb, zt = L.WALLS[name][2:4]
        rects = [(it, L.item_rect(name, it)) for it in L.ITEMS[name]]
        for it, r in rects:
            tag = "%s: %s at %.2f, %.2f" % (name, it[0], it[1], it[2])
            if r[0] < 0.3 or r[1] > Lw - 0.3:
                bad.append(tag + " is within 0.3 m of a corner")
            top = L.SOFFIT[name] - (0.25 if it[0] in L.FLUSH else 0.3)
            if it[0] == "inlet":
                # its height is the coal reception's gallery's; its flashing
                # need only clear the coping's foot
                top = L.SOFFIT[name] - L.INLET_COPE_CLEAR
            if r[2] < zb - EPS or r[3] > top:
                bad.append(tag + " leaves the wall")
            if EPS < r[2] < 0.5:
                bad.append(tag + " leaves a sliver of plinth under it")
            if any(abs(z - c) < 0.1 for z in r[2:] for c in L.CUTS):
                bad.append(tag + " has an edge within 0.1 m of a slab line")
        for i, (a, ra) in enumerate(rects):
            for b, rb in rects[i + 1:]:
                # the window band's lights stand on its concrete strips by
                # design; the lettering may come 0.25 m over a window head
                kinds = {a[0], b[0]}
                if any(NOTCHED.get(k) in kinds for k in kinds):
                    continue                # a panel cut round the item it wraps
                if kinds == {"win", "conc"} or kinds == {"conc"}:
                    gap = -EPS
                elif "letters" in kinds:
                    gap = 0.2
                else:
                    gap = 0.3
                if _overlap(ra, rb, gap):
                    bad.append("%s: %s at %.2f and %s at %.2f within %.2f m"
                               % (name, a[0], a[1], b[0], b[1], gap))
    for kind, top in L.LEAF_TOP.items():
        if not 2.0 <= top <= 2.4:
            bad.append("the %s leaf is %.3f m" % (kind, top))
        if top > L.SIZES[kind][1] - 2 * L.DOOR_FRAME - 0.05:
            bad.append("no transom or vent panel over the %s leaf" % kind)
    bad += brick_problems()
    # the ladders and their cages clear of the corners and the openings
    for wall, ladder, cage in (("th_rear", WALL1, CAGE1), ("step", WALL2, CAGE2)):
        avoid = _avoid(wall)
        bad += RS.problems(ladder, "the %s wall ladder" % wall, avoid)
        bad += RS.problems(cage, "the %s ladder's cage" % wall, avoid)
    # the upper ladder lands on the boiler house's deck clear of the bay
    c0, c1 = CAGE2.span()
    if L.wall_s("step", L.BUNKER[2]) < c1 + 0.8:
        bad.append("the upper ladder lands against the bunker bay")
    # the conveyor inlet: the coal reception's gallery's section at its
    # height, its frame wide enough for the gallery's 0.05 m collar and its
    # face on the copings' outer plane, its recess inside the wall, and the
    # dusted panel wrapping its foot
    (inlet,) = [L.item_rect("bh_west", it) for it in L.ITEMS["bh_west"] if it[0] == "inlet"]
    (mouth,) = [L.item_rect("bh_west", it) for it in L.ITEMS["bh_west"] if it[0] == "mouth"]
    zc = 13.0 + 12.0 * math.tan(math.radians(20.0))
    if abs((inlet[2] + inlet[3]) / 2.0 - zc) > 1e-6 or \
            abs(inlet[3] - inlet[2] - L.INLET_H - 2 * L.INLET_FRAME) > 1e-6 or \
            abs(inlet[1] - inlet[0] - L.INLET_W - 2 * L.INLET_FRAME) > 1e-6:
        bad.append("the inlet is not the gallery's section at its height")
    if L.INLET_FRAME < 0.05 + 0.05:
        bad.append("the inlet's frame is too narrow for the gallery's collar")
    if abs(L.INLET_PROUD - L.CO) > EPS:
        bad.append("the inlet's frame does not stand on the copings' outer plane")
    if not 0.10 <= L.INLET_DEPTH <= 0.15 or L.INLET_DEPTH >= L.PIN:
        bad.append("the inlet's recess is not a shallow one inside the wall")
    bx = L.BUNKER[0] + BUNKER_STEP - L.BH[0]
    if not (L.INLET_DEPTH < bx < L.PIN and inlet[3] < BUNKER_STEP_Z < L.Z_BWT):
        bad.append("the bunker bay's buried foot does not clear the inlet's recess")
    if not (mouth[0] < inlet[0] and inlet[1] < mouth[1]
            and mouth[2] < inlet[2] < mouth[3] < inlet[3]):
        bad.append("the dusted panel does not wrap the inlet's foot")
    # roof things clear of each other and the parapets
    bx0, bx1, by0, by1 = L.BUNKER
    if not (L.BH[0] < bx0 < L.BH[0] + L.PIN - 0.05 and L.BH[1] - L.PIN + 0.05 < bx1 < L.BH[1]
            and L.BH[3] - L.PIN + 0.05 < by1 < L.BH[3]):
        bad.append("the bunker bay's faces do not stand within the parapets")
    for px, py in L.STACKS:
        r = L.STACK_R
        if py + r > by0 - 0.5 or py - r < L.BH[2] + 1.0 or px - r < L.BH[0] + 1.0 \
                or px + r > L.BH[1] - 1.0:
            bad.append("the stack at (%.1f, %.1f) crowds the bay or a parapet" % (px, py))
        if L.STACK_TOP - L.STACK_DEPTH < L.Z_BD + 0.3:
            bad.append("a stack's flue floor is in the deck")
    if abs(L.STACKS[0][0] - L.STACKS[1][0]) < 2 * L.STACK_R + 0.5:
        bad.append("the stacks crowd each other")
    for px, py in L.VENTS:
        h = L.VENT_W / 2.0
        if px - h < L.TH[0] + 0.8 or px + h > L.TH[1] - 0.8 or abs(py) + h > L.TH[3] - 0.8:
            bad.append("the ventilator at (%.1f, %.1f) crowds a parapet" % (px, py))
        if abs(px - LADDER1_X) < 1.0 and py > L.TH[3] - 2.0:
            bad.append("the ventilator at (%.1f, %.1f) blocks the ladder" % (px, py))
        if px - h < L.TH[0] + 1.5 and abs(py - LADDER2_Y) < 1.5:
            bad.append("the ventilator at (%.1f, %.1f) blocks the upper ladder" % (px, py))
    if L.STACK_TOP < WALL2.eave.z_edge + RS.LADDER_TOP + 0.05:
        bad.append("the upper ladder, not the stacks, would set the height")
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
    without the copings, the canopy, the flue stub, the stacks and the
    ladders. One storey: both halls' floors at the ground, which every door
    opens onto level, inside the outer wall faces. The bunker bay on the
    boiler house's deck holds coal, not an occupied floor, so it is no
    storey. Nothing stands over the ground outside the walls but the
    copings' oversail, the conveyor inlet's frame, the canopy, the flue
    stub and the lower ladder, so there is no passage."""
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
    views at the doors, the flue, the conveyor inlet and the boiler house's
    east face. Working views only, not committed."""
    preview_studio()
    _show_only(level)
    scn = bpy.context.scene
    saved = (scn.camera, scn.render.resolution_x, scn.render.resolution_y)
    scn.render.resolution_x, scn.render.resolution_y = res
    obj = bpy.data.objects["{}_LOD{}".format(ASSET, level)]
    centre, radius = _bounds(obj)
    off = Vector(BUILD.pivot) if BUILD.pivot else Vector()
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

    def B(x, y, z):                     # a build-frame point in the pivoted scene
        return Vector((x, y, z)) - off
    persp = [("aerial", centre, Vector((1.0, -1.0, math.sqrt(2.0))), 2.6),
             ("aerial_rear", centre, Vector((-1.0, 1.0, math.sqrt(2.0))), 2.6),
             ("aerial_west", centre, Vector((-1.0, -1.0, math.sqrt(2.0))), 2.6),
             ("aerial_east_rear", centre, Vector((1.0, 1.0, math.sqrt(2.0))), 2.6),
             ("eye_entrance", B(-9.0, -8.5, 3.0), Vector((0.3, -1.0, 0.05)), 0.9),
             ("eye_bigdoor", B(13.5, -8.0, 3.5), Vector((0.2, -1.0, 0.05)), 1.0),
             ("eye_flue", B(-9.0, 8.5, 12.0), Vector((-0.6, 1.0, 0.1)), 1.0),
             ("eye_inlet", B(-16.0, 4.5, 16.5), Vector((-1.0, -0.6, -0.2)), 0.7),
             ("eye_roof", B(-7.0, 0.0, 20.0), Vector((1.0, -0.8, 0.6)), 0.9),
             ("eye_step", B(-2.0, 3.0, 15.0), Vector((1.0, 0.6, 0.35)), 0.8)]
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
