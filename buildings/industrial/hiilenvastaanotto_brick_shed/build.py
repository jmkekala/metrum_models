# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of hiilenvastaanotto_brick_shed, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, renders preview.png and variants.png, and
writes the facts sidecar:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

The coal reception of a small mid-century Nordic town heat-and-power plant: a
composite, not any real building. Trucks drive straight through a brick
tipping shed and tip their coal through a steel grate in the floor into the
pit, from which a bucket elevator lifts it toward the boiler house's bunkers.

The shed is 14.0 x 6.4 m, red brick on a concrete plinth between the columns
of a concrete frame, under a low 6.8 degree profiled-sheet gable roof whose
ridge runs along X. The truck lane runs through it along X, level and
doorless, 5.60 m between its walls and 14.0 m from the west mouth's wall
plane to the east one's, used one way, in at the west mouth. Each gable is a
concrete portal: two 0.4 m piers and a lintel at 6.00 m, the band that runs
round the shed as its ring beam, brick and the shallow gable above. Inside,
two tie beams cross the lane at 6.20 m under a pitched sheet ceiling, and the
tipping grate lies in the floor 2.5 m west of mid-length, under the tail of a
truck stopped at the lane's centre. Three tall steel windows light the shed
high on its front (-Y) wall.

Behind it (+Y), the side that faces the hall's coal side: a brick lean-to
with the attendant's room (a window onto the lane, its door in the lean-to's
east end) and the drive room, and through it the elevator tower: a slim
brick shaft 2.6 x 4.1 m with its stair's windows stacked up its east face,
under a sheet-clad head house 4.0 x 4.8 x 4.2 m that oversails it on three
sides, a loading hatch and hoist beam on its east face. From the head
house's rear face the inclined conveyor gallery rises at 20 degrees away from
the building, 4.0 m in plan to a closed end, on two raking struts back to
the shaft: nothing of it stands on the ground behind the tower.

Construction. The shed is one closed box with the lane cut out of it by an
exact boolean difference (asset_build.difference): the lane's void, extended
past both gables, and at the close tiers the attendant's window recess, are
the cutters, so the box
keeps a 0.02 m floor slab under the lane, the lane's floor face, and the
void's own faces become the lane's walls, ceiling, the lintels' soffits and
the gables' inner faces over them, with the void's UVs. Then the lean-to and
shaft (one hand-built solid), the head house, the two roof slabs, the head
house's slab, the gallery, its struts, the hoist beam, the tie beams and the
downpipes are unioned in (asset_build.union).
"""

import importlib
import json
import math
import os
import struct
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
from asset_build import difference, to_object, union  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT, tint=L.LIT_FACTOR)
PPM, LPM = L.PPM, L.LPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

HX = L.HX
YL0, YL1, YC = L.YL0, L.YL1, L.YC
X_IN = L.X_IN
FT = L.FLOOR_T


def house_top(y):
    """The shed's wall ring lid: WALL_INTO up into the gable slab."""
    return L.roof_under(y) + L.WALL_INTO


def annex_top(y):
    return L.annex_under(y) + L.WALL_INTO


# ============================================================== mesh builder
class Builder:
    """One closed solid under construction, with UVs set as faces are made.
    Vertices are shared through a position cache, so faces that meet along an
    edge meet on the same vertices; region outlines carry their neighbours'
    breakpoints explicitly (fix_tjunctions) so every edge has a vertex at
    each of its ends."""

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
    out runs away from the wall on the side its outward normal points."""

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

    def s_at(self, plan):
        """s of a plan coordinate along this wall (x for walls along x)."""
        along_x = abs(self.t.x) > 0.5
        return (plan - (self.p0.x if along_x else self.p0.y)) * (
            self.t.x if along_x else self.t.y)

    def xy(self, s):
        q = self.p0 + self.t * s
        return q.x, q.y


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.
def uv_brick(fr, u_off, shift=0.0):
    """The brick band; *shift* lowers the rows sampled, above the band."""
    return lambda co: ((fr.s_of(co) + u_off) * PPM, L.BRICK_Y0 + (co.z - shift) * PPM)


def uv_col(fr, a):
    x0 = L.COL[0]
    return lambda co: (x0 + (fr.s_of(co) - a) * PPM, L.BRICK_Y0 + co.z * PPM)


def uv_patch(name):
    x, y, w, h = L.PATCHES[name]
    c = (x + w / 2.0, y + h / 2.0)
    return lambda co: c


def uv_region(fr, kind, s0, z0):
    x, y, w, h = L.REGION[kind]
    return lambda co: (x + (fr.s_of(co) - s0) * PPM, y + (co.z - z0) * PPM)


def uv_reveal(fr, edge, u_off, shift=0.0):
    """The cheek of an opening, in the wall's own brick, unrolled round the
    corner so the coursing runs on into the cheek (as nostokonehuone_brick)."""
    (s0, z0), (s1, z1) = edge
    ds, dz = s1 - s0, z1 - z0
    ln = math.hypot(ds, dz) or 1.0
    ns, nz = -dz / ln, ds / ln

    def f(co):
        d = -fr.out_of(co)
        return ((fr.s_of(co) + ns * d + u_off) * PPM,
                L.BRICK_Y0 + (co.z + nz * d - shift) * PPM)
    return f


# ================================================================== walls
def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge: collinear
    breakpoints along a region's outline let the triangulator make
    triangles of no area."""
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


def fill_region(B, to3d, outline, holes, uvfn):
    """Triangulate a planar region (an outline and holes, in 2D) and add it."""
    loops = [outline] + list(holes)
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((a, b, 0.0)) for a, b in loop] for loop in loops])
    for i, j, k in _flip_slivers(flat, tris):
        B.face([to3d(*flat[i]), to3d(*flat[j]), to3d(*flat[k])], uvfn)


def _area(poly):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1])) / 2.0


def _dedupe(poly):
    out = []
    for p in poly:
        p = (round(p[0], 6), round(p[1], 6))
        if not out or abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-6 and abs(out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    return out


def clip_rect(poly, s0, s1, z0, z1):
    """Sutherland-Hodgman: *poly* (s, z) clipped to the rectangle. The
    walls' outlines are clipped by horizontal bands and column strips that
    never split them into two pieces."""
    pts = list(poly)
    for axis, val, ge in ((0, s0, True), (0, s1, False), (1, z0, True), (1, z1, False)):
        if not pts:
            return []
        out = []
        n = len(pts)
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            ip = p[axis] >= val - 1e-9 if ge else p[axis] <= val + 1e-9
            iq = q[axis] >= val - 1e-9 if ge else q[axis] <= val + 1e-9
            if ip:
                out.append(p)
            if ip != iq:
                t = (val - p[axis]) / (q[axis] - p[axis])
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        pts = out
    pts = _dedupe(pts)
    return pts if len(pts) >= 3 and abs(_area(pts)) > 1e-9 else []


def fix_tjunctions(polys):
    """Insert into every polygon's edges the corners of the others that lie
    on them, so regions that share an edge share its vertices."""
    pts = {p for poly in polys for p in poly}
    out = []
    for poly in polys:
        res = []
        for a, b in zip(poly, poly[1:] + poly[:1]):
            res.append(a)
            ex, ez = b[0] - a[0], b[1] - a[1]
            ll = ex * ex + ez * ez
            on = []
            for p in pts:
                t = ((p[0] - a[0]) * ex + (p[1] - a[1]) * ez) / ll
                if 1e-7 < t < 1 - 1e-7:
                    d = abs((p[0] - a[0]) * ez - (p[1] - a[1]) * ex) / math.sqrt(ll)
                    if d < 1e-6:
                        on.append((t, p))
            res += [p for _, p in sorted(on)]
        out.append(res)
    return out


def item_rect(fr, kind, centre, z0):
    """(s0, s1, z0, z1) of an opening centred on plan coordinate *centre*."""
    w, h = L.OPENINGS[kind]
    s = fr.s_at(centre)
    return (s - w / 2.0, s + w / 2.0, z0, z0 + h)


def opening_mode(level):
    """LOD0/1 cut every opening into its wall with reveals; LOD2/3 paint the
    same rectangle flat (CLAUDE.md's default)."""
    return "cut" if level < 2 else "flush"


def build_opening(B, fr, kind, rect, level, u_off, shift):
    """One opening: brick reveals round it and the closing plane set back in
    it while it is cut, the same rectangle flat after. Returns its outline.
    A door on the ground gets no cheek along its threshold: that strip would
    lie on the floor cap; left out, the rim detours round the recess."""
    s0, s1, z0, z1 = rect
    poly = [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]
    closing = uv_region(fr, kind, s0, z0)
    if opening_mode(level) == "flush":
        B.face([fr.P(s, z) for s, z in poly], closing)
        return poly
    depth = L.REVEAL[kind]
    for k, edge in enumerate(zip(poly, poly[1:] + poly[:1])):
        (a0, b0), (a1, b1) = edge
        if k == 0 and z0 < EPS:
            continue
        if k == 0:
            fn = uv_patch("sill")
        elif k == 2 and abs(z1 - L.Z_BAND0) < EPS:
            fn = uv_patch("conc")
        else:
            fn = uv_reveal(fr, edge, u_off, shift)
        B.face([fr.P(a0, b0), fr.P(a1, b1), fr.P(a1, b1, -depth),
                fr.P(a0, b0, -depth)], fn)
    B.face([fr.P(s, z, -depth) for s, z in poly], closing)
    return poly


def band_of(z0, z1):
    """Which of the brick band's three samplings a span of height lies in."""
    sp = L.SPLITS
    for k, (lo, hi) in enumerate(((-1e9, sp[0]), (sp[0], sp[1]), (sp[1], 1e9))):
        if lo - EPS <= z0 and z1 <= hi + EPS:
            return k
    return None


def build_wall(B, spec, level):
    """One wall: its outline (with any door notched into its foot) cut into
    regions by the band splits and, below the first split, by the concrete
    frame's columns; each region filled with its openings as holes, the
    columns mapped onto the column strip, the brick onto the brick band
    (shifted above the splits)."""
    fr = Frame(spec["p0"], spec["p1"])
    items = [(k, item_rect(fr, k, c, z)) for k, c, z in spec["items"]]
    notches = sorted((r[0], r[1], r[3]) for k, r in items if r[2] < EPS)
    foot = [(spec["s_lo"], 0.0)]
    for a, b, top in notches:
        foot += [(a, 0.0), (a, top), (b, top), (b, 0.0)]
    foot.append((spec["s_hi"], 0.0))
    outline = _dedupe(foot + spec["top"])
    cols = spec.get("cols", [])
    splits = (-1.0,) + L.SPLITS + (1e3,)
    regions = []
    for k in range(3):
        band = clip_rect(outline, -1e3, 1e3, splits[k], splits[k + 1])
        if not band:
            continue
        if k == 0 and cols:
            edges = sorted({e for c in cols for e in c})
            xs = [-1e3] + edges + [1e3]
            for a, b in zip(xs, xs[1:]):
                piece = clip_rect(band, a, b, -1e3, 1e3)
                if piece:
                    is_col = any(abs(a - c0) < 1e-6 and abs(b - c1) < 1e-6 for c0, c1 in cols)
                    regions.append((k, is_col, a, piece))
        else:
            regions.append((k, False, None, band))
    polys = fix_tjunctions([r[3] for r in regions])
    placed = set()
    for (k, is_col, a, _), piece in zip(regions, polys):
        shift = L.SHIFTS[k]
        holes = []
        if not is_col:
            xs_, zs_ = [p[0] for p in piece], [p[1] for p in piece]
            for i, (kind, r) in enumerate(items):
                if i in placed:
                    continue
                if min(xs_) - EPS <= r[0] and r[1] <= max(xs_) + EPS and \
                        min(zs_) - EPS <= r[2] and r[3] <= max(zs_) + EPS:
                    poly = build_opening(B, fr, kind, r, level, spec["u_off"], shift)
                    placed.add(i)
                    if r[2] > EPS:
                        holes.append(poly)
        fn = uv_col(fr, a) if is_col else uv_brick(fr, spec["u_off"], shift)
        fill_region(B, fr.P, piece, holes, fn)
    if len(placed) != len(items):
        raise ValueError("%s: an opening straddles a split or a column" % spec["name"])


def close_solid(B, n_loops, split=None):
    """Cap every open rim with an n-gon, walked in edge-index order so the
    caps start on the same vertex every run. A rim that is not planar (the
    shed's gable lid) is cut in two between the *split* vertices."""
    bm = B.bm
    bm.edges.index_update()
    order = [e for e in bm.edges if len(e.link_faces) == 1]
    rim = set(order)
    branch = [v for e in order for v in e.verts
              if sum(1 for x in v.link_edges if x in rim) != 2]
    if branch:
        c = branch[0].co
        raise ValueError("a rim branches at (%.3f, %.3f, %.3f): a T-junction" % (c.x, c.y, c.z))
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
    keys = [B.v(p) for p in split] if split else []
    for loop in loops:
        if keys and all(k in loop for k in keys):
            i, j = sorted(loop.index(k) for k in keys)
            for half in (loop[i:j + 1], loop[j:] + loop[:i + 1]):
                B.set_uv(bm.faces.new(half), blank)
        else:
            B.set_uv(bm.faces.new(loop), blank)


# --------------------------------------------------------------- the shed
# Each wall runs counter-clockwise seen from above, outward face on its
# right. cols: the s spans of the concrete frame's columns. items: (kind,
# centre in plan x or y, sill z). top: the wall's top, from s_hi back to s_lo.
COLS_LONG = [(0.0, L.COL_W)] + [(HX + fx - L.COL_W / 2.0, HX + fx + L.COL_W / 2.0)
                                for fx in L.FRAME_X] + [(2 * HX - L.COL_W, 2 * HX)]
SPAN = L.Y_R - L.Y_F
GABLE_TOP_F = [(SPAN, house_top(L.Y_R)), (SPAN / 2.0, house_top(YC)), (0.0, house_top(L.Y_F))]
WIN_X = (-4.6, 0.0, 4.6)
SHED_WALLS = [
    dict(name="front", p0=(-HX, L.Y_F), p1=(HX, L.Y_F), s_lo=0.0, s_hi=2 * HX,
         top=[(2 * HX, house_top(L.Y_F)), (0.0, house_top(L.Y_F))], cols=COLS_LONG,
         items=[("win", WIN_X[0], L.Z_WIN), ("win_b", WIN_X[1], L.Z_WIN),
                ("win", WIN_X[2], L.Z_WIN)], u_off=0.4),
    dict(name="east", p0=(HX, L.Y_F), p1=(HX, L.Y_R), s_lo=0.0, s_hi=SPAN,
         top=GABLE_TOP_F, cols=[(0.0, L.WALL_T), (SPAN - L.WALL_T, SPAN)],
         items=[], u_off=4.0),
    dict(name="rear", p0=(HX, L.Y_R), p1=(-HX, L.Y_R), s_lo=0.0, s_hi=2 * HX,
         top=[(2 * HX, house_top(L.Y_R)), (0.0, house_top(L.Y_R))], cols=COLS_LONG,
         items=[], u_off=0.7),
    dict(name="west", p0=(-HX, L.Y_R), p1=(-HX, L.Y_F), s_lo=0.0, s_hi=SPAN,
         top=GABLE_TOP_F, cols=[(0.0, L.WALL_T), (SPAN - L.WALL_T, SPAN)],
         items=[], u_off=7.0),
]


def shed_box(level):
    """The shed as one closed box: four walls to the lid inside the roof
    slab, a floor cap and the lid cut along the ridge. The lane is cut out of
    it afterwards (lane_void)."""
    B = Builder()
    for spec in SHED_WALLS:
        build_wall(B, spec, level)
    close_solid(B, 2, split=[(HX, YC, house_top(YC)), (-HX, YC, house_top(YC))])
    return B


# ---------------------------------------------------------------- the lane
def uv_lane_side(co):
    """Both side walls: U along the lane from the west mouth, V up."""
    x0, y0 = L.LANE_SIDE[:2]
    return (x0 + (co.x + HX) * LPM, y0 + co.z * LPM)


def uv_lane_end(co):
    """The gables' inner faces over the lintels: the side walls' rows at a
    short run of U near the west mouth (brick, the band at the lintel)."""
    x0, y0 = L.LANE_SIDE[:2]
    return (x0 + (0.8 + 0.25 * (co.y - YL0)) * LPM, y0 + co.z * LPM)


def uv_lane_ceil(co):
    x0, y0 = L.LANE_CEIL[:2]
    return (x0 + (co.x + HX) * LPM,
            y0 + ((YC - YL0) - abs(co.y - YC)) * L.SLOPE_F * LPM)


def uv_lane_floor(co):
    x0, y0 = L.LANE_FLOOR[:2]
    return (x0 + (co.x + HX) * LPM, y0 + (co.y - YL0) * LPM)


LANE_OVER = 0.5         # the void runs this far past each gable's outer face
LANE_WIN = ("win_s_b", 3.3, 1.3)    # the attendant's window onto the lane: kind, x, sill
LANE_WIN_DEPTH = 0.15


def lane_win_rect():
    kind, x, z = LANE_WIN
    w, h = L.OPENINGS[kind]
    return (x - w / 2.0, x + w / 2.0, z, z + h)


def lane_void(level):
    """The lane's void as one closed solid: the mouths' 6.00 m sections
    through the gables, and between the gables' inner faces the hall up to
    its pitched ceiling, over the floor slab's top. Cut from the shed box, its
    faces become the lane's surfaces with these UVs. At the far tiers the
    attendant's window is a flat quad in the rear side wall."""
    B = Builder()
    x0, x1 = -HX - LANE_OVER, HX + LANE_OVER
    zm = L.Z_MOUTH
    zc0, zc1, zap = L.ceil_z(YL0), L.ceil_z(YL1), L.ceil_z(YC)
    B.face([(x0, YL0, FT), (x1, YL0, FT), (x1, YL1, FT), (x0, YL1, FT)], uv_lane_floor)
    side = [(x0, FT), (x1, FT), (x1, zm), (X_IN, zm), (X_IN, zc0), (-X_IN, zc0),
            (-X_IN, zm), (x0, zm)]
    B.face([(x, YL0, z) for x, z in side], uv_lane_side)
    rear = [(x, z) for x, z in side]
    if opening_mode(level) == "flush":
        s0, s1, z0, z1 = lane_win_rect()
        hole = [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]
        fill_region(B, lambda x, z: (x, YL1, z), rear, [hole], uv_lane_side)
        kind = LANE_WIN[0]
        rx, ry = L.REGION[kind][:2]
        B.face([(x, YL1, z) for x, z in hole],
               lambda co: (rx + (co.x - s0) * PPM, ry + (co.z - z0) * PPM))
    else:
        B.face([(x, YL1, z) for x, z in rear], uv_lane_side)
    for xa, xb in ((x0, -X_IN), (X_IN, x1)):
        B.face([(xa, YL0, zm), (xb, YL0, zm), (xb, YL1, zm), (xa, YL1, zm)],
               uv_patch("lintel"))
    for x in (-X_IN, X_IN):
        B.face([(x, YL0, zm), (x, YL1, zm), (x, YL1, zc1), (x, YC, zap), (x, YL0, zc0)],
               uv_lane_end)
    B.face([(-X_IN, YL0, zc0), (X_IN, YL0, zc0), (X_IN, YC, zap), (-X_IN, YC, zap)],
           uv_lane_ceil)
    B.face([(-X_IN, YC, zap), (X_IN, YC, zap), (X_IN, YL1, zc1), (-X_IN, YL1, zc1)],
           uv_lane_ceil)
    for x in (x0, x1):
        B.face([(x, YL0, FT), (x, YL1, FT), (x, YL1, zm), (x, YL0, zm)], uv_patch("blank"))
    return B


def lane_window_cutter():
    """The attendant's window recess, cut into the lane's rear side wall at
    the close tiers: reveals and the steel window LANE_WIN_DEPTH back."""
    B = Builder()
    s0, s1, z0, z1 = lane_win_rect()
    ya, yb = YL1 - 0.3, YL1 + LANE_WIN_DEPTH
    kind = LANE_WIN[0]
    rx, ry = L.REGION[kind][:2]
    win = lambda co: (rx + (co.x - s0) * PPM, ry + (co.z - z0) * PPM)  # noqa: E731
    rev = uv_patch("reveal")
    B.face([(s0, yb, z0), (s1, yb, z0), (s1, yb, z1), (s0, yb, z1)], win)
    B.face([(s0, ya, z0), (s0, ya, z1), (s1, ya, z1), (s1, ya, z0)], uv_patch("blank"))
    B.face([(s0, ya, z0), (s1, ya, z0), (s1, yb, z0), (s0, yb, z0)], uv_patch("sill"))
    B.face([(s0, ya, z1), (s0, yb, z1), (s1, yb, z1), (s1, ya, z1)], rev)
    B.face([(s0, ya, z0), (s0, yb, z0), (s0, yb, z1), (s0, ya, z1)], rev)
    B.face([(s1, ya, z0), (s1, ya, z1), (s1, yb, z1), (s1, yb, z0)], rev)
    return B


def keeps_beams(level):
    """The tie beams are seen only from inside the lane or straight through
    a mouth; each costs about 30 triangles with its cuts. Past 70 m they are
    under three pixels deep in a dark lane, so LOD2 and LOD3 drop them; the
    rafters painted on the ceiling stay."""
    return level < 2


def tie_beam(xc):
    """A concrete tie beam across the lane at the frame at *xc*: soffit at
    Z_BEAM, its ends run 0.15 m into the side walls and its top 0.10 m up
    into the solid over the ceiling, a pentagon in section."""
    B = Builder()
    ya, yb = YL0 - 0.15, YL1 + 0.15
    zb = L.Z_BEAM
    sec = [(ya, zb), (yb, zb), (yb, L.ceil_z(yb) + 0.10), (YC, L.ceil_z(YC) + 0.10),
           (ya, L.ceil_z(ya) + 0.10)]
    xa, xb = xc - L.BEAM_W / 2.0, xc + L.BEAM_W / 2.0
    fn = uv_patch("beam")
    for k in range(5):
        (y0, z0), (y1, z1) = sec[k], sec[(k + 1) % 5]
        B.face([(xa, y0, z0), (xa, y1, z1), (xb, y1, z1), (xb, y0, z0)], fn)
    B.face([(xa, y, z) for y, z in sec], fn)
    B.face([(xb, y, z) for y, z in reversed(sec)], fn)
    return B


# ------------------------------------------------------- lean-to and tower
AX0, AX1, AY0, AY1 = L.AX0, L.AX1, L.AY0, L.AY1
TX0, TX1, TY1 = L.TX0, L.TX1, L.TY1
ZT = L.Z_TOWER_TOP
AT0, AT1 = annex_top(AY0), annex_top(AY1)
DOOR_Y = 4.0            # the attendant's door, on the lean-to's east end
ANNEX_WALLS = [
    dict(name="a_front", p0=(AX0, AY0), p1=(AX1, AY0), s_lo=0.0, s_hi=AX1 - AX0,
         top=[(AX1 - AX0, AT0), (TX1 - AX0, AT0), (TX1 - AX0, ZT), (TX0 - AX0, ZT),
              (TX0 - AX0, AT0), (0.0, AT0)],
         items=[("win_s", 0.0, 10.2)], u_off=0.3),
    dict(name="a_east", p0=(AX1, AY0), p1=(AX1, AY1), s_lo=0.0, s_hi=AY1 - AY0,
         top=[(AY1 - AY0, AT1), (0.0, AT0)],
         items=[("door", DOOR_Y, 0.0), ("win_s", 5.6, 1.0)], u_off=10.0),
    dict(name="a_rear_e", p0=(AX1, AY1), p1=(TX1, AY1), s_lo=0.0, s_hi=AX1 - TX1,
         top=[(AX1 - TX1, AT1), (0.0, AT1)],
         items=[("win_s_b", 3.0, 1.0)], u_off=2.0),
    # the stair's windows, one a flight, stacked up the shaft's east face
    dict(name="t_east", p0=(TX1, AY1), p1=(TX1, TY1), s_lo=0.0, s_hi=TY1 - AY1,
         top=[(TY1 - AY1, ZT), (AY0 - AY1, ZT), (AY0 - AY1, AT0), (0.0, AT1)],
         items=[("win_s", 4.8, 4.6), ("win_s_b", 4.8, 7.6), ("win_s", 4.8, 10.6)],
         u_off=5.0),
    dict(name="t_rear", p0=(TX1, TY1), p1=(TX0, TY1), s_lo=0.0, s_hi=TX1 - TX0,
         top=[(TX1 - TX0, ZT), (0.0, ZT)],
         items=[("door", 0.0, 0.0)], u_off=9.6),
    dict(name="t_west", p0=(TX0, TY1), p1=(TX0, AY1), s_lo=0.0, s_hi=TY1 - AY1,
         top=[(TY1 - AY1, AT1), (TY1 - AY0, AT0), (TY1 - AY0, ZT), (0.0, ZT)],
         items=[], u_off=0.4),
    dict(name="a_rear_w", p0=(TX0, AY1), p1=(AX0, AY1), s_lo=0.0, s_hi=TX0 - AX0,
         top=[(TX0 - AX0, AT1), (0.0, AT1)],
         items=[("win_s", -3.0, 1.0)], u_off=11.5),
    dict(name="a_west", p0=(AX0, AY1), p1=(AX0, AY0), s_lo=0.0, s_hi=AY1 - AY0,
         top=[(AY1 - AY0, AT0), (0.0, AT1)], items=[], u_off=5.5),
]


def annex_body(level):
    """The lean-to and the tower as one closed solid: the lean-to's walls to
    its sloping lid inside its roof slab, the tower's rising from the ground
    where it stands proud of the lean-to and from the lid elsewhere, to its
    own lid inside its slab. Rims: the floor, the lean-to's two lids either
    side of the tower, the tower's lid."""
    B = Builder()
    for spec in ANNEX_WALLS:
        build_wall(B, spec, level)
    close_solid(B, 4)
    return B


# ================================================================== roofs
XE = HX + L.RAKE_OV
YE0, YE1 = L.Y_F - L.EAVE_OV, L.Y_R + L.EAVE_OV


def uv_roof(co):
    d = (L.HALF_SPAN + L.EAVE_OV - abs(co.y - YC)) * L.SLOPE_F
    return ((co.x + XE) * PPM, L.ROOF_Y0 + d * L.ROOF_RPM)


def uv_eave(z_edge):
    return lambda co: ((co.x + XE) * PPM, L.EAVE_Y0 + (co.z - z_edge) * PPM)


def gable_slab():
    """The main roof as one closed slab: a chevron section across y,
    extruded along the ridge. The part inside the walls disappears in the
    union; outside them it is the eave and rake soffit. The section's
    vertical sides are the eave fascias with the gutter, the chevron ends
    the barge flashing over the gables."""
    B = Builder()
    zu = L.roof_under(YE0)
    zr = L.roof_under(YC)
    T = L.ROOF_T
    sec = [(YE0, zu), (YE0, zu + T), (YC, zr + T), (YE1, zu + T), (YE1, zu), (YC, zr)]
    fns = [uv_eave(zu), uv_roof, uv_roof, uv_eave(zu), uv_patch("soffit"), uv_patch("soffit")]
    for k in range(6):
        (y0, z0), (y1, z1) = sec[k], sec[(k + 1) % 6]
        B.face([(-XE, y0, z0), (-XE, y1, z1), (XE, y1, z1), (XE, y0, z0)], fns[k])
    barge = uv_patch("barge")
    B.face([(-XE, y, z) for y, z in sec], barge)
    B.face([(XE, y, z) for y, z in reversed(sec)], barge)
    return B


AXE0, AXE1 = AX0 - L.A_RAKE_OV, AX1 + L.A_RAKE_OV


def uv_annex_roof(co):
    d = (L.A_SLAB_Y1 - co.y) * L.SLOPE_FA * L.ANNEX_V_K
    return ((co.x + XE) * PPM, L.ROOF_Y0 + d * L.ROOF_RPM)


def lean_to_slab():
    """The lean-to's mono-pitch slab: its high end buried in the shed's rear
    wall, its low edge the rear fascia with the gutter, rakes either end."""
    B = Builder()
    ya, yb = L.A_SLAB_Y0, L.A_SLAB_Y1
    za, zb = L.annex_under(ya), L.annex_under(yb)
    T = L.ROOF_T
    sec = [(ya, za), (ya, za + T), (yb, zb + T), (yb, zb)]
    fns = [uv_patch("blank"), uv_annex_roof, uv_eave(zb), uv_patch("soffit")]
    for k in range(4):
        (y0, z0), (y1, z1) = sec[k], sec[(k + 1) % 4]
        B.face([(AXE0, y0, z0), (AXE0, y1, z1), (AXE1, y1, z1), (AXE1, y0, z0)], fns[k])
    barge = uv_patch("barge")
    B.face([(AXE0, y, z) for y, z in sec], barge)
    B.face([(AXE1, y, z) for y, z in reversed(sec)], barge)
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


def tower_slab():
    """The head house's flat concrete roof slab, overhanging T_OV all round."""
    o = L.T_OV
    return box(L.HX0 - o, L.HX1 + o, L.HY0 - o, L.HY1 + o, L.Z_TSLAB,
               L.Z_TSLAB + L.T_SLAB_T, uv_patch("coping"), uv_patch("felt"),
               uv_patch("slab_under"))


# ------------------------------------------------------------- head house
# Its four walls, walked anticlockwise from above as every wall here is;
# items as the brick walls' (kind, plan centre, sill). u_off places each
# wall's U in the cladding region, inside its 7.0 m.
HH_WALLS = [
    dict(name="h_front", p0=(L.HX0, L.HY0), p1=(L.HX1, L.HY0),
         items=[("win_s", -0.8, 13.5), ("win_s_b", 0.8, 13.5)], u_off=0.2),
    dict(name="h_east", p0=(L.HX1, L.HY0), p1=(L.HX1, L.HY1),
         items=[("win_s", 3.1, 13.5), ("hatch", L.HOIST_Y, 12.6)], u_off=1.0),
    dict(name="h_rear", p0=(L.HX1, L.HY1), p1=(L.HX0, L.HY1), items=[], u_off=2.6),
    dict(name="h_west", p0=(L.HX0, L.HY1), p1=(L.HX0, L.HY0),
         items=[("louvre", L.HOIST_Y, 14.6), ("win_s_b", 3.1, 13.5)], u_off=2.0),
]


def uv_clad(fr, u_off):
    x0, y0 = L.CLAD[:2]
    return lambda co: (x0 + (fr.s_of(co) + u_off) * PPM, y0 + (co.z - L.HH_Z0) * L.CLAD_VPM)


def head_house(level):
    """The head house as one closed box: four sheet-clad walls from its
    floor (the oversail's soffit, which the shaft runs up into) to a lid
    inside the roof slab, each wall's openings recessed at the close tiers
    and flush after, as the brick walls' are."""
    B = Builder()
    z0, z1 = L.HH_Z0, L.Z_HH_TOP
    for spec in HH_WALLS:
        fr = Frame(spec["p0"], spec["p1"])
        holes = []
        for kind, c, zs in spec["items"]:
            s0, s1, a, b = item_rect(fr, kind, c, zs)
            poly = [(s0, a), (s1, a), (s1, b), (s0, b)]
            holes.append(poly)
            closing = uv_region(fr, kind, s0, a)
            if opening_mode(level) == "flush":
                B.face([fr.P(s, z) for s, z in poly], closing)
                continue
            d = L.REVEAL[kind]
            rev = uv_patch("clad_rev")
            for (a0, b0), (a1, b1) in zip(poly, poly[1:] + poly[:1]):
                B.face([fr.P(a0, b0), fr.P(a1, b1), fr.P(a1, b1, -d), fr.P(a0, b0, -d)], rev)
            B.face([fr.P(s, z, -d) for s, z in poly], closing)
        fill_region(B, fr.P, [(0.0, z0), (fr.L, z0), (fr.L, z1), (0.0, z1)], holes,
                    uv_clad(fr, spec["u_off"]))
    ring = [(L.HX0, L.HY0), (L.HX1, L.HY0), (L.HX1, L.HY1), (L.HX0, L.HY1)]
    B.face([(x, y, z0) for x, y in reversed(ring)], uv_patch("hh_soffit"))
    B.face([(x, y, z1) for x, y in ring], uv_patch("blank"))
    return B


def hoist_beam():
    """The steel hoist beam over the loading hatch, out from the head
    house's east face under the slab, its inner end inside the wall."""
    w = L.HOIST_W / 2.0
    return box(L.HX1 - 0.25, L.HX1 + L.HOIST_OUT, L.HOIST_Y - w, L.HOIST_Y + w,
               L.HOIST_Z[0], L.HOIST_Z[1], uv_patch("hoist"), uv_patch("hoist"),
               uv_patch("hoist"))


# ---------------------------------------------------------------- gallery
GAL_YA = TY1 - L.GAL_BURY           # its start, inside the head house
GAL_XW = L.GAL_W / 2.0


def gal_end_recessed(level):
    return level < 2


def uv_gal_side(co):
    x0, y0 = L.GAL_SIDE[:2]
    return (x0 + (co.y - GAL_YA) * PPM, y0 + (co.z - L.gal_floor(co.y)) * L.GAL_VPM)


def uv_gal_roof(co):
    """The gallery's roof on the cladding: ribs across U run down the slope;
    V up the slope, squeezed into the cladding's clean rows."""
    x0, y0, _w, _h = L.CLAD
    run = (L.GAL_Y1 - GAL_YA) / math.cos(math.radians(L.GAL_ANG))
    rows = (L.Z_TSLAB - L.HH_Z0) * L.CLAD_VPM - 8.0
    return (x0 + (co.x + GAL_XW + 0.5) * PPM,
            y0 + 4.0 + (co.y - GAL_YA) / math.cos(math.radians(L.GAL_ANG)) / run * rows)


def uv_gal_end(co):
    x0, y0 = L.GAL_END[:2]
    return (x0 + (co.x + GAL_XW) * LPM, y0 + (co.z - L.gal_floor(L.GAL_Y1)) * LPM)


def gallery(level):
    """The inclined conveyor gallery as one closed box: its vertical section
    GAL_W x GAL_H, centre line at GAL_Z0 on the shaft's rear face plane
    rising at GAL_ANG toward +Y to its closed end at GAL_Y1, started
    GAL_BURY inside the head house so the union cuts its mouth there. The
    end is a rim round a blanking plate, set back at the close tiers."""
    B = Builder()
    ya, yb = GAL_YA, L.GAL_Y1
    xw, H = GAL_XW, L.GAL_H
    za, zb = L.gal_floor(ya), L.gal_floor(yb)
    # sides, floor, roof
    B.face([(xw, ya, za), (xw, yb, zb), (xw, yb, zb + H), (xw, ya, za + H)], uv_gal_side)
    B.face([(-xw, ya, za), (-xw, ya, za + H), (-xw, yb, zb + H), (-xw, yb, zb)], uv_gal_side)
    B.face([(-xw, ya, za), (-xw, yb, zb), (xw, yb, zb), (xw, ya, za)], uv_patch("gal_under"))
    B.face([(-xw, ya, za + H), (xw, ya, za + H), (xw, yb, zb + H), (-xw, yb, zb + H)],
           uv_gal_roof)
    B.face([(-xw, ya, za), (xw, ya, za), (xw, ya, za + H), (-xw, ya, za + H)],
           uv_patch("blank"))
    # the end: in the plane y = yb, (s, z) with s = x
    outline = [(-xw, zb), (xw, zb), (xw, zb + H), (-xw, zb + H)]
    to3d = lambda s, z: (s, yb, z)  # noqa: E731
    flip = lambda s, z: (-s, yb, z)  # noqa: E731  (walked so its normal is +Y)
    if not gal_end_recessed(level):
        B.face([to3d(s, z) for s, z in reversed(outline)], uv_gal_end)
        return B
    r, d = L.GAL_END_RIM, L.GAL_END_RECESS
    inner = [(-xw + r, zb + r), (xw - r, zb + r), (xw - r, zb + H - r), (-xw + r, zb + H - r)]
    # fill_region winds its triangles anticlockwise in (s, z); mirrored in s
    # they face +Y, out of the end
    fill_region(B, flip, [(-s, z) for s, z in reversed(outline)],
                [[(-s, z) for s, z in reversed(inner)]], uv_gal_end)
    rev = uv_patch("clad_rev")
    for (s0, z0), (s1, z1) in zip(inner, inner[1:] + inner[:1]):
        B.face([(s0, yb, z0), (s1, yb, z1), (s1, yb - d, z1), (s0, yb - d, z0)], rev)
    B.face([(s, yb - d, z) for s, z in reversed(inner)], uv_gal_end)
    return B


def strut(x):
    """One raking strut: a square steel member from inside the shaft's rear
    face at STRUT_FOOT up and out to the gallery's floor at STRUT_TOP_Y,
    both ends run on into the solids it joins."""
    (fy, fz), ty = L.STRUT_FOOT, L.STRUT_TOP_Y
    tz = L.gal_floor(ty)
    a = Vector((0.0, ty - fy, tz - fz)).normalized()
    p = Vector((0.0, a.z, -a.y))                    # across the axis, in y-z
    q = Vector((1.0, 0.0, 0.0))
    h = L.STRUT_W / 2.0
    A = Vector((x, fy, fz)) - a * 0.25
    Bp = Vector((x, ty, tz)) + a * 0.20
    ring = [(-h, -h), (h, -h), (h, h), (-h, h)]
    r0 = [tuple(A + q * u + p * v) for u, v in ring]
    r1 = [tuple(Bp + q * u + p * v) for u, v in ring]
    B = Builder()
    fn = uv_patch("strut")
    for k in range(4):
        B.face([r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k]], fn)
    B.face(list(reversed(r0)), fn)
    B.face(list(r1), fn)
    return B


# ---------------------------------------------------------------- downpipes
# The main roof drains to its front and rear eaves, the lean-to to its rear.
# Each pipe stands 0.7 m in from the shed's corners (clear of the corner
# columns and the high windows) or 0.25 m in from the lean-to's, all inside
# the mouths' planes: nothing stands in line with the lane's approaches.
PIPE_S = 0.7
DOWNPIPES = [
    DP.eave_pipe(SHED_WALLS[0]["p0"], SHED_WALLS[0]["p1"], PIPE_S, L.Z_EAVE, L.TAN, L.EAVE_OV),
    DP.eave_pipe(SHED_WALLS[0]["p0"], SHED_WALLS[0]["p1"], 2 * HX - PIPE_S, L.Z_EAVE, L.TAN,
                 L.EAVE_OV),
    DP.eave_pipe(SHED_WALLS[2]["p0"], SHED_WALLS[2]["p1"], PIPE_S, L.Z_EAVE, L.TAN, L.EAVE_OV),
    DP.eave_pipe(SHED_WALLS[2]["p0"], SHED_WALLS[2]["p1"], 2 * HX - PIPE_S, L.Z_EAVE, L.TAN,
                 L.EAVE_OV),
    DP.eave_pipe(ANNEX_WALLS[2]["p0"], ANNEX_WALLS[2]["p1"], DP.CORNER, L.Z_AE, L.TAN_A,
                 L.A_EAVE_OV),
    DP.eave_pipe(ANNEX_WALLS[6]["p0"], ANNEX_WALLS[6]["p1"], TX0 - AX0 - DP.CORNER, L.Z_AE,
                 L.TAN_A, L.A_EAVE_OV),
]
PIPE_WALLS = ["front", "front", "rear", "rear", "a_rear_e", "a_rear_w"]


# ================================================================ assembly
def keeps_downpipes(level):
    """LOD3 drops the six downpipes to pay for the gallery and the head
    house: past 120 m a pipe is under two pixels wide against its wall."""
    return level < 3


def keeps_fittings(level):
    """The hoist beam and the gallery's two struts, 0.16-0.20 m steel, go at
    LOD3 with the downpipes: past 120 m they are under two pixels across."""
    return level < 3


def build_lod(level):
    house = to_object(shed_box(level), "tmp_shed")
    cutters = [to_object(lane_void(level), "tmp_lane")]
    if opening_mode(level) == "cut":
        cutters.append(to_object(lane_window_cutter(), "tmp_lane_win"))
    house = difference(house, cutters)
    parts = [to_object(annex_body(level), "tmp_annex"),
             to_object(gable_slab(), "tmp_roof"),
             to_object(lean_to_slab(), "tmp_lean_to"),
             to_object(tower_slab(), "tmp_tower_slab"),
             to_object(head_house(level), "tmp_head_house"),
             to_object(gallery(level), "tmp_gallery")]
    if keeps_fittings(level):
        parts.append(to_object(hoist_beam(), "tmp_hoist"))
        parts += [to_object(strut(x), "tmp_strut%d" % i) for i, x in enumerate(L.STRUT_X)]
    if keeps_beams(level):
        parts += [to_object(tie_beam(x), "tmp_beam%d" % i) for i, x in enumerate(L.FRAME_X)]
    if keeps_downpipes(level):
        parts += [to_object(B, name) for B, name in
                  DP.solids(DOWNPIPES, *DP.MODES[level], L.PIPE_STRIP, L.ATLAS)]
    obj = union(house, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
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
        bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges[:])
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY',
                              ngon_method='BEAUTY')
        flat = [f for f in bm.faces if f.calc_area() < 1e-8]
    if flat:
        raise ValueError("LOD%d keeps %d zero-area triangles, e.g. at %s"
                         % (level, len(flat), tuple(flat[0].calc_center_median())))
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# ================================================================== checks
LANE_BAND = 1.0         # nothing beyond a mouth's plane within this of the lane
UNDER_GALLERY_MIN = 4.6     # nothing lower than this over the strip behind the tower


def ground_parts():
    """(name, x0, x1, y0, y1, z_low) in plan for everything outside the
    shed's walls: what could stand in a truck's way at a mouth."""
    out = [("lean-to", AX0, AX1, AY0, AY1, 0.0),
           ("tower", TX0, TX1, L.TY0, TY1, 0.0),
           ("lean-to slab", AXE0, AXE1, L.A_SLAB_Y0, L.A_SLAB_Y1, L.annex_under(L.A_SLAB_Y1)),
           ("head house", L.HX0, L.HX1, L.HY0, L.HY1, L.HH_Z0),
           ("head house slab", L.HX0 - L.T_OV, L.HX1 + L.T_OV, L.HY0 - L.T_OV,
            L.HY1 + L.T_OV, L.Z_TSLAB),
           ("hoist beam", L.HX1, L.HX1 + L.HOIST_OUT, L.HOIST_Y - L.HOIST_W / 2.0,
            L.HOIST_Y + L.HOIST_W / 2.0, L.HOIST_Z[0]),
           ("gallery", -GAL_XW, GAL_XW, TY1, L.GAL_Y1, L.gal_floor(TY1)),
           ("struts", L.STRUT_X[0] - L.STRUT_W / 2.0, L.STRUT_X[1] + L.STRUT_W / 2.0, TY1,
            L.STRUT_TOP_Y + 0.15, L.STRUT_FOOT[1] - 0.2),
           ("main roof's rakes", -XE, XE, YE0, YE1, L.roof_under(YE0))]
    for p, w in zip(DOWNPIPES, PIPE_WALLS):
        pts = [p.point(a, out, z) for out, z in p.path(True) for a in (-DP.A, DP.A)]
        out.append(("downpipe on %s at s %.2f" % (w, p.s), min(q.x for q in pts),
                    max(q.x for q in pts), min(q.y for q in pts), max(q.y for q in pts),
                    min(q.z for q in pts)))
    return out


def check_layout():
    """Numbers that have to agree before any geometry is worth looking at:
    openings on their walls, clear of corners, columns, splits and each
    other; the lane at least the consumer's 5.0 m wide and 4.6 m clear, its
    length in the brief's 12-16 m; nothing beyond a mouth's plane in line
    with the lane or within LANE_BAND of it below the lintel; downpipes clear
    of corners and openings; the roofs."""
    bad = []
    walls = SHED_WALLS + ANNEX_WALLS
    for spec in walls:
        fr = Frame(spec["p0"], spec["p1"])
        rects = [(k, item_rect(fr, k, c, z)) for k, c, z in spec["items"]]
        lo = min(spec["s_lo"], min(p[0] for p in spec["top"]))
        hi = max(spec["s_hi"], max(p[0] for p in spec["top"]))
        for k, r in rects:
            if r[0] < lo + 0.3 or r[1] > hi - 0.3:
                bad.append("%s: %s within 0.3 m of the wall's end" % (spec["name"], k))
            if band_of(r[2], r[3]) is None:
                bad.append("%s: %s straddles a band split" % (spec["name"], k))
            for c0, c1 in spec.get("cols", []):
                if r[0] < c1 + 0.2 and c0 - 0.2 < r[1]:
                    bad.append("%s: %s crowds a column" % (spec["name"], k))
            if EPS < r[2] < 0.3:
                bad.append("%s: %s leaves a sliver of wall under it" % (spec["name"], k))
            if r[3] > L.Z_BAND0 + EPS and r[2] < L.Z_BAND1:
                bad.append("%s: %s runs up into the band" % (spec["name"], k))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b = rects[i][1], rects[j][1]
                if a[0] < b[1] + 0.3 and b[0] < a[1] + 0.3 and a[2] < b[3] + 0.3 and b[2] < a[3] + 0.3:
                    bad.append("%s: two openings within 0.3 m" % spec["name"])
    # the lean-to's openings stand under its roof, the tower's above it
    for spec in ANNEX_WALLS:
        fr = Frame(spec["p0"], spec["p1"])
        for k, c, z in spec["items"]:
            r = item_rect(fr, k, c, z)
            ground = spec["name"] in ("a_east", "a_rear_e", "a_rear_w", "a_west") or z < 3.0
            if ground and r[3] > AT1 - L.WALL_INTO - 0.4:
                bad.append("%s: %s runs up under the lean-to's roof" % (spec["name"], k))
            if not ground and r[2] < AT0 + 0.5:
                bad.append("%s: %s is not clear above the lean-to's roof" % (spec["name"], k))
            if not ground and r[3] > L.HH_Z0 - 0.4:
                bad.append("%s: %s runs up under the head house" % (spec["name"], k))
    # the head house's openings: on their walls, clear of its ends, its floor,
    # its slab and each other; the hoist beam over the hatch
    for spec in HH_WALLS:
        fr = Frame(spec["p0"], spec["p1"])
        rects = [(k, item_rect(fr, k, c, z)) for k, c, z in spec["items"]]
        for k, r in rects:
            if r[0] < 0.3 or r[1] > fr.L - 0.3:
                bad.append("%s: %s within 0.3 m of the wall's end" % (spec["name"], k))
            if r[2] < L.HH_Z0 + 0.2 or r[3] > L.Z_TSLAB - 0.3:
                bad.append("%s: %s crowds the floor or the slab" % (spec["name"], k))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b = rects[i][1], rects[j][1]
                if a[0] < b[1] + 0.3 and b[0] < a[1] + 0.3 and a[2] < b[3] + 0.3 \
                        and b[2] < a[3] + 0.3:
                    bad.append("%s: two openings within 0.3 m" % spec["name"])
    hatch_top = next(z + L.OPENINGS[k][1] for k, c, z in HH_WALLS[1]["items"] if k == "hatch")
    if L.HOIST_Z[0] < hatch_top + 0.5 or L.HOIST_Z[1] > L.Z_TSLAB - 0.2:
        bad.append("the hoist beam is not between the hatch and the slab")
    # the gallery: its mouth inside the head house's rear face, its end
    # centre where the plant hall's stub expects it
    za, zt = L.gal_floor(TY1), L.gal_floor(TY1) + L.GAL_H
    if za < L.HH_Z0 + 0.2 or zt > L.Z_TSLAB - 0.3:
        bad.append("the gallery's mouth is not inside the head house's rear face")
    if GAL_XW > L.HX1 - 0.3:
        bad.append("the gallery's mouth crowds the head house's corners")
    if abs(L.GAL_Z1 - 15.456) > 0.001:
        bad.append("the gallery's end centre is at %.3f m, not 15.456" % L.GAL_Z1)
    for x in L.STRUT_X:
        if abs(x) + L.STRUT_W / 2.0 > TX1 - 0.15 or abs(x) + L.STRUT_W / 2.0 > GAL_XW - 0.1:
            bad.append("a strut is not on the shaft's rear face under the gallery")
    if L.STRUT_FOOT[1] < L.OPENINGS["door"][1] + 2.0:
        bad.append("the struts' feet crowd the elevator door")
    # the tower front's window, above the shed's roof
    if 10.2 < L.roof_under(L.TY0) + L.ROOF_T + 1.0:
        bad.append("the tower's front window is not clear of the shed's roof")
    # the attendant's window onto the lane: inside the room's walls
    s0, s1, z0, z1 = lane_win_rect()
    if not (TX1 + 0.3 + 0.3 < s0 and s1 < AX1 - 0.3 - 0.3):
        bad.append("the lane window is not inside the attendant's room")
    for fx in L.FRAME_X:
        if s0 - 0.3 < fx + L.BEAM_W / 2.0 and fx - L.BEAM_W / 2.0 < s1 + 0.3:
            bad.append("the lane window crowds a frame")
    # the lane: the consumer's hard numbers
    if YL1 - YL0 < 5.0:
        bad.append("the lane is %.2f m wide, under 5.0" % (YL1 - YL0))
    if min(L.Z_MOUTH, L.Z_BEAM) - FT < 4.6 or L.Z_BEAM < L.Z_MOUTH:
        bad.append("the lane's clear height is under 4.6 m, or a beam under the lintels")
    if L.ceil_z(YL0) < L.Z_BEAM + 0.5:
        bad.append("the ceiling meets the side walls under the beams")
    if not 12.0 <= 2 * HX <= 16.0:
        bad.append("the lane is %.1f m long, outside 12-16" % (2 * HX))
    for name, x0, x1, y0, y1, zlo in ground_parts():
        beyond = x0 < -HX - EPS or x1 > HX + EPS
        beside = y0 < YL1 + LANE_BAND and YL0 - LANE_BAND < y1
        if beyond and beside and zlo < L.Z_MOUTH:
            bad.append("%s stands beyond a mouth's plane beside the lane" % name)
        # the strip under the gallery, behind the tower's rear face, is clear
        # ground: nothing there under UNDER_GALLERY_MIN
        if y1 > TY1 + EPS and zlo < UNDER_GALLERY_MIN:
            bad.append("%s reaches into the strip under the gallery" % name)
    if AX0 - L.A_RAKE_OV < -HX or AX1 + L.A_RAKE_OV > HX:
        bad.append("the lean-to runs past the shed's gables")
    # the void and the floor slab, the window recesses inside the walls
    if L.REVEAL["win"] > L.WALL_T - 0.15 or LANE_WIN_DEPTH > L.WALL_T - 0.15:
        bad.append("a recess comes within 0.15 m of the lane or the wall's face")
    # downpipes: clear of corners and openings
    for p, w in zip(DOWNPIPES, PIPE_WALLS):
        spec = next(s for s in walls if s["name"] == w)
        fr = Frame(spec["p0"], spec["p1"])
        avoid = [(k, *item_rect(fr, k, c, z)[:2]) for k, c, z in spec["items"]]
        if w == "rear":
            avoid.append(("lean-to", fr.s_at(AX1) - 0.3, fr.s_at(AX0) + 0.3))
        bad += DP.problems(p, "the downpipe on %s at s %.2f" % (w, p.s), avoid)
    # the roofs: the lean-to no steeper than 1:8 and nothing serviced on the
    # main roof (CLAUDE.md's roof safety rules)
    if L.TAN_A > 1.0 / 8.0:
        bad.append("the lean-to is steeper than 1:8")
    # the atlas: brick U inside its band, shifted rows inside clean brick
    for spec in walls:
        ss = [p[0] for p in spec["top"]] + [spec["s_lo"], spec["s_hi"]]
        if (min(ss) + spec["u_off"]) * PPM < 2 or (max(ss) + spec["u_off"]) * PPM > L.BRICK_W - 2:
            bad.append("%s: its brick runs off the band" % spec["name"])
        zt = max(p[1] for p in spec["top"])
        for k, (lo, sh) in enumerate(zip(L.SPLITS, L.SHIFTS[1:])):
            if zt > lo:
                hi = min(zt, L.SPLITS[k + 1] if k + 1 < len(L.SPLITS) else zt)
                if lo - sh < L.SAMPLE_LO - EPS or hi - sh > L.SAMPLE_HI + EPS:
                    bad.append("%s samples brick outside the clean rows" % spec["name"])
    return bad


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def glb_triangles(path):
    """Every triangle of an exported tier, in the glTF frame, read from the
    file itself (no import)."""
    with open(path, "rb") as fh:
        data = fh.read()
    jlen = struct.unpack_from("<I", data, 12)[0]
    js = json.loads(data[20:20 + jlen].decode("utf-8"))
    off = 20 + jlen
    blen = struct.unpack_from("<I", data, off)[0]
    binc = data[off + 8:off + 8 + blen]
    comp = {5126: ("f", 4), 5125: ("I", 4), 5123: ("H", 2), 5121: ("B", 1)}
    width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}

    def accessor(i):
        a = js["accessors"][i]
        bv = js["bufferViews"][a["bufferView"]]
        fmt, size = comp[a["componentType"]]
        n = width[a["type"]]
        stride = bv.get("byteStride", size * n)
        start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        return [struct.unpack_from("<" + fmt * n, binc, start + k * stride)
                for k in range(a["count"])]

    tris = []
    for mesh in js["meshes"]:
        for prim in mesh["primitives"]:
            pos = accessor(prim["attributes"]["POSITION"])
            idx = [i[0] for i in accessor(prim["indices"])]
            tris += [(pos[idx[k]], pos[idx[k + 1]], pos[idx[k + 2]])
                     for k in range(0, len(idx), 3)]
    return tris


def _clip_poly3(poly, axis, val, keep_ge):
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        ip = p[axis] >= val if keep_ge else p[axis] <= val
        iq = q[axis] >= val if keep_ge else q[axis] <= val
        if ip:
            out.append(p)
        if ip != iq:
            t = (val - p[axis]) / (q[axis] - p[axis])
            out.append(tuple(p[j] + t * (q[j] - p[j]) for j in range(3)))
    return out


def measure_lane(path=None, inset=1e-3):
    """The lane as the exported LOD0 mesh has it, in the build frame: every
    triangle clipped to the lane's plan (inset a millimetre, so the side
    walls on its edges drop out), the floor's height (the highest point of
    the triangles lying at the floor slab's top) and the lowest point of
    everything else over it."""
    path = path or os.path.join(BUILD.export_dir, "%s_lod0.glb" % ASSET)
    px, py, pz = BUILD.pivot
    floor, low, low_at = -1e9, 1e9, None
    for tri in glb_triangles(path):
        pts = [(gx + px, -gz + py, gy + pz) for gx, gy, gz in tri]
        poly = pts
        for axis, val, ge in ((0, -HX + inset, True), (0, HX - inset, False),
                              (1, YL0 + inset, True), (1, YL1 - inset, False)):
            if poly:
                poly = _clip_poly3(poly, axis, val, ge)
        if len(poly) < 3:
            continue
        zs = [p[2] for p in poly]
        if max(zs) <= FT + 1e-3:
            floor = max(floor, max(zs))
            continue
        if min(zs) < low:
            low = min(zs)
            low_at = min(poly, key=lambda p: p[2])
    return {"floor": floor, "lowest": low, "lowest_at": low_at}


def measure_strip(path=None, inset=1e-3):
    """The strip under the gallery as the exported LOD0 mesh has it, in the
    build frame: the LOD0 plan bounds, and the lowest point of every
    triangle clipped to the strip's plan -- from the shaft's rear face, the
    rearmost thing that stands on the ground, to the gallery's far end,
    across the whole width of the bounds -- inset a millimetre so the
    shaft's face and the gallery's end plane drop out."""
    path = path or os.path.join(BUILD.export_dir, "%s_lod0.glb" % ASSET)
    px, py, pz = BUILD.pivot
    tris = [[(gx + px, -gz + py, gy + pz) for gx, gy, gz in t] for t in glb_triangles(path)]
    xs = [p[0] for t in tris for p in t]
    ys = [p[1] for t in tris for p in t]
    lo_x, hi_x = min(xs), max(xs)
    low, low_at = 1e9, None
    for pts in tris:
        poly = pts
        for axis, val, ge in ((1, TY1 + inset, True), (1, L.GAL_Y1 - inset, False)):
            if poly:
                poly = _clip_poly3(poly, axis, val, ge)
        if len(poly) < 3:
            continue
        p = min(poly, key=lambda q: q[2])
        if p[2] < low:
            low, low_at = p[2], p
    return {"x": (lo_x, hi_x), "y": (min(ys), max(ys)), "lowest": low, "lowest_at": low_at}


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame.

    The footprint is the outer wall outline at the ground: the shed's 14.0 x
    6.4 m rectangle with the lane inside it (the mouths' openings closed
    across their wall planes, as hiilisiilo_drive_through states its lane),
    the lean-to behind it and the tower's 0.4 m step proud of the lean-to.
    The one storey is the ground-level rooms of the lean-to and the tower
    (the attendant's room, the drive room and the elevator's boot room)
    inside 0.3 m walls; the lane is open and not a storey. The lane's mouths
    have no leaf and are not doors.

    The lane is the first passage, used one way and stated from its entry,
    the west mouth (glTF -X): its centre on the west gable's outer plane,
    forward +X, width between the side walls, length gable plane to gable
    plane, open at the far end. Its clear height is measured on the exported
    LOD0 mesh (measure_lane): the lowest geometry over the lane, from the
    floor slab's top the trucks run on. A truck stops with its centre at the
    lane's centre, its tail over the grate (GRATE_C).

    The second passage is the clear ground under the gallery: the strip from
    the shaft's rear face to the gallery's far end, across the LOD0 plan
    bounds' whole width, stated from their -X edge along +X; nothing stands
    on it, and its clear height is the lowest geometry over it, measured on
    the exported LOD0 mesh (measure_strip)."""
    def door(door_id, kind, wall, main=False):
        spec = next(s for s in ANNEX_WALLS if s["name"] == wall)
        fr = Frame(spec["p0"], spec["p1"])
        k, c, z = next(i for i in spec["items"] if i[0] == "door")
        return model_facts.wall_door(door_id, kind, spec["p0"], spec["p1"], fr.s_at(c), z,
                                     L.LEAF_W, L.LEAF_H, main)

    lane = measure_lane()
    clear = lane["lowest"] - lane["floor"]
    strip = measure_strip()
    sx0, sx1 = strip["x"]
    rooms = ((AX1 - 0.3) - (AX0 + 0.3)) * ((AY1 - 0.3) - L.Y_R) \
        + ((TX1 - 0.3) - (TX0 + 0.3)) * ((TY1 - 0.3) - (AY1 - 0.3))
    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-HX, L.Y_F), (HX, L.Y_F), (HX, L.Y_R), (AX1, L.Y_R), (AX1, AY1),
                      (TX1, AY1), (TX1, TY1), (TX0, TY1), (TX0, AY1), (AX0, AY1),
                      (AX0, L.Y_R), (-HX, L.Y_R)],
        "storeys": [(0.0, rooms)],
        "doors": [door("attendant", "entrance", "a_east", main=True),
                  door("elevator", "service", "t_rear")],
        "passages": [model_facts.lane_passage(
            "truck_lane", (-HX, YC), (1.0, 0.0), YL1 - YL0, 2 * HX, round(clear, 3),
            through=True),
            model_facts.lane_passage(
            "under_gallery", (sx0, (TY1 + L.GAL_Y1) / 2.0), (1.0, 0.0),
            round(L.GAL_Y1 - TY1, 3), round(sx1 - sx0, 3), round(strip["lowest"], 3),
            through=True)],
    }


if __name__ == "__main__":
    BUILD.main(build_all, facts)
