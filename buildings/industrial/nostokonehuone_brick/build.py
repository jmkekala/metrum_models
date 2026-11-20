# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of nostokonehuone_brick, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite mid-century Nordic mine's hoist house: the engine hall that
stands beside a headframe and houses the winding engine and compressors. One
tall hall, 9.0 x 11.5 m, in facing brick on a concrete plinth under a low
standing-seam gable, with a cast concrete lintel band round the building at
the window heads. Gable end to the front: a steel machinery door between two
tall windows, a ventilation louvre high in the gable above. Each long wall carries four tall steel multi-pane windows in a
2.75 m rhythm; on the east wall the front bay is the entrance, the window's
frame brought down to the ground round a steel leaf. The rear gable has one
tall window and, high up under the apex, the louvred slot the winding ropes
would pass through toward the headframe. Gutters are painted on both eave
fascias, with a downpipe from each and a snow guard above; two plain vent
pipes stand on the slopes.

Construction is a set of closed solids unioned with Blender's exact boolean:
the wall ring (capped by a floor and a lid split at the ridge, both buried),
the gable roof slab, the downpipes and the vents. The union trims the wall
tops into the roof and leaves the boundary of one empty volume, so interior
geometry cannot occur.

Every number the mesh and the atlas share is imported from facade_atlas.py
rather than written here a second time.
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
HX, HY = L.HX, L.HY                     # 4.5 x 5.75: a 9.0 x 11.5 m hall
XE = HX + L.EAVE_OUT                    # the eave edges, in x
YE = HY + L.RAKE_OUT                    # the rake edges, in y
Z_APEX = L.Z_WALL_TOP + HX * L.TAN      # gable wall top, in the slab


def roof_under(x):
    """The gable roof's underside over plan position *x*."""
    return L.Z_EAVE + (HX - abs(x)) * L.TAN


def roof_top(x):
    return roof_under(x) + L.ROOF_T


def gtop(s, span=2.0 * HX):
    """Where a gable wall stops, *s* along it: inside the roof slab."""
    return L.Z_WALL_TOP + min(s, span - s) * L.TAN


# Openings, per wall, as (kind, centre in plan x or y, sill z). The long walls
# keep one 2.75 m bay rhythm, the two window regions alternating so that
# neighbouring windows show different rooms behind the glass.
SILL = L.Z_SILL
BAYS = (-4.125, -1.375, 1.375, 4.125)           # plan y of the long walls' bays
FRONT_ITEMS = [("window", -3.125, SILL), ("bigdoor", 0.0, 0.0),
               ("window_b", 3.125, SILL), ("slot", 0.0, L.Z_SLOT)]
EAST_ITEMS = [("screen", BAYS[0], 0.0), ("window_b", BAYS[1], SILL),
              ("window", BAYS[2], SILL), ("window_b", BAYS[3], SILL)]
REAR_ITEMS = [("window", 0.0, SILL), ("slot", 0.0, L.Z_SLOT)]
WEST_ITEMS = [("window", BAYS[3], SILL), ("window_b", BAYS[2], SILL),
              ("window", BAYS[1], SILL), ("window_b", BAYS[0], SILL)]

# Vent pipes on the slopes: (x, y, diameter, height above the sheet). Plain
# vents, not serviced plant, so no roof safety kit (CLAUDE.md).
VENTS = [(2.0, 1.6, 0.30, 0.90), (-1.9, -2.4, 0.16, 0.55)]


# ----------------------------------------------------------------- tiers
def opening_mode(level):
    """LOD0/1 cut every opening into its wall with brick reveals; LOD2/3 paint
    the same rectangle flat. The 0.15-0.25 m reveals are under two pixels past
    70 m, and the window rhythm is the painted rectangle's to keep."""
    return "cut" if level < 2 else "flush"


def vent_sides(level, dia):
    """Eight sides up close, six to 70 m, four after; the 0.16 m pipe goes
    past 70 m, where it is under two pixels across, and the 0.3 m one stays
    to the last tier as a four-sided stack: about 3 px over the ridge line."""
    if level == 0:
        return 8
    if level == 1:
        return 6
    return 4 if dia >= 0.25 else 0


def downpipe_mode(level):
    """(sides, bent) of the downpipes at each tier: scripts/downpipes.py's
    MODES unchanged; the last tier can afford its two three-sided pipes."""
    return DP.MODES[level]


# ============================================================== mesh builder
class Builder:
    """One closed solid under construction, with UVs set as faces are made.

    Vertices are shared through a position cache, so faces that meet along an
    edge meet on the same vertices. That only works if every vertex lying on
    an edge is a corner of both faces - which is why region outlines carry
    their neighbours' breakpoints explicitly.
    """

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
        # Newell area in double precision, relative to the first vertex, so a
        # zero-area face is reliably skipped.
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

    def s_at(self, plan):
        """s of a plan coordinate along this wall (x for walls along x)."""
        along_x = abs(self.t.x) > 0.5
        return (plan - (self.p0.x if along_x else self.p0.y)) * (
            self.t.x if along_x else self.t.y)


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.

def uv_brick(fr, u_off, shift=0.0):
    """The brick band. *shift* lowers the rows sampled, for the gables."""
    return lambda co: ((fr.s_of(co) + u_off) * PPM,
                       L.BRICK_Y0 + (co.z - shift) * PPM)


def _patch_centre(name):
    x, y, w, h = L.PATCHES[name]
    return (x + w / 2.0, y + h / 2.0)


def uv_patch(name):
    c = _patch_centre(name)
    return lambda co: c


def uv_reveal(fr, edge, u_off, shift=0.0):
    """The cheek of an opening, in the wall's own brick.

    Unrolled round the corner: a point *d* deep in the reveal takes the brick
    that would have been *d* further along the wall in the direction the
    opening lies, so the coursing runs on into the cheek instead of
    restarting, and the plinth runs on round a door's jamb.
    """
    (s0, z0), (s1, z1) = edge
    ds, dz = s1 - s0, z1 - z0
    ln = math.hypot(ds, dz) or 1.0
    ns, nz = -dz / ln, ds / ln

    def f(co):
        d = -fr.out_of(co)
        return ((fr.s_of(co) + ns * d + u_off) * PPM,
                L.BRICK_Y0 + (co.z + nz * d - shift) * PPM)
    return f


def uv_region(fr, rect, s0, z0):
    x, y, w, h = rect
    return lambda co: (x + (fr.s_of(co) - s0) * PPM, y + (co.z - z0) * PPM)


# ================================================================== walls
def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge.

    Openings on one wall share head and sill heights, so a region's holes line
    up and the triangulator is free to join three collinear corners into a
    triangle of no area. Flipping the long edge it shares with its neighbour
    turns the pair into two real triangles meeting at the middle vertex.
    """
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
    """Triangulate a planar wall region -- an outline and any holes, in
    (s, z) -- and add it."""
    loops = [outline] + list(holes)
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((a, b, 0.0)) for a, b in loop] for loop in loops])
    for i, j, k in _flip_slivers(flat, tris):
        B.face([fr.P(*flat[i]), fr.P(*flat[j]), fr.P(*flat[k])], uvfn)


def item_rect(fr, kind, centre, z0):
    """(s0, s1, z0, z1) of an opening centred on plan coordinate *centre*."""
    w, h = L.OPENINGS[kind]
    s = fr.s_at(centre)
    return (s - w / 2.0, s + w / 2.0, z0, z0 + h)


def build_opening(B, fr, kind, rect, level, u_off, shift=0.0):
    """One opening: brick reveals round it and the closing plane set back in
    it while it is cut, the same rectangle painted flat after. Returns its
    outline in (s, z), which the wall region takes as a hole or a notch.

    The sill is a concrete patch; a head that stands under the lintel band
    is the band's soffit. An opening on the ground gets no cheek along its
    threshold: the strip would lie at z = 0 on top of the floor the wall ring
    is capped with, and the two coplanar faces would leave the export
    non-manifold at the doorway. Left out, the rim detours round the recess
    and the floor cap covers it.
    """
    s0, s1, z0, z1 = rect
    poly = [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]
    closing = uv_region(fr, L.REGION[kind], s0, z0)
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
        elif k == 2 and abs(z1 - L.Z_HEAD) < EPS:
            fn = uv_patch("conc")
        else:
            fn = uv_reveal(fr, edge, u_off, shift)
        B.face([fr.P(a0, b0), fr.P(a1, b1), fr.P(a1, b1, -depth),
                fr.P(a0, b0, -depth)], fn)
    B.face([fr.P(s, z, -depth) for s, z in poly], closing)
    return poly


def wall_region(B, fr, outline, items, level, u_off, shift=0.0):
    """One planar region of wall: every opening inside it built and holed.

    Openings standing on the region's foot are notches in *outline* already
    (see outline_with_notches); the rest are holes.
    """
    holes = []
    for kind, rect in items:
        poly = build_opening(B, fr, kind, rect, level, u_off, shift)
        if rect[2] > outline[0][1] + EPS:
            holes.append(poly)
    fill_region(B, fr, outline, holes, uv_brick(fr, u_off, shift))


def outline_with_notches(s0, s1, z0, notches):
    """The foot of a region from s0 to s1 at z0, detouring up round every
    door that stands on it; returns the points from (s0, z0) to (s1, z0)."""
    pts = [(s0, z0)]
    for a, b, top in sorted(notches):
        pts += [(a, z0), (a, top), (b, top), (b, z0)]
    pts.append((s1, z0))
    out = []
    for p in pts:
        if not out or abs(out[-1][0] - p[0]) > EPS or abs(out[-1][1] - p[1]) > EPS:
            out.append(p)
    return out


def rects_for(fr, items):
    return [(kind, item_rect(fr, kind, c, z)) for kind, c, z in items]


MAIN_WALLS = {
    # name: (p0, p1), walked counter-clockwise from above so the outward face
    # is on the right; u offsets run on round the corners so the bond continues
    "front": ((-HX, -HY), (HX, -HY)),
    "east": ((HX, -HY), (HX, HY)),
    "rear": ((HX, HY), (-HX, HY)),
    "west": ((-HX, HY), (-HX, -HY)),
}
WALL_ITEMS = {"front": FRONT_ITEMS, "east": EAST_ITEMS, "rear": REAR_ITEMS,
              "west": WEST_ITEMS}
U_OFF = {"front": 0.0, "east": 2 * HX, "rear": 2 * HX + 2 * HY,
         "west": 4 * HX + 2 * HY}


def build_long(B, name, level):
    """An eave wall: one region from the ground to the wall head, which runs
    into the roof slab. Its ends carry Z_GABLE, where the gables meet it."""
    fr = Frame(*MAIN_WALLS[name])
    items = rects_for(fr, WALL_ITEMS[name])
    notches = [(r[0], r[1], r[3]) for k, r in items if r[2] < EPS]
    foot = outline_with_notches(0.0, fr.L, 0.0, notches)
    outline = foot + [(fr.L, L.Z_GABLE), (fr.L, L.Z_WALL_TOP),
                      (0.0, L.Z_WALL_TOP), (0.0, L.Z_GABLE)]
    wall_region(B, fr, outline, items, level, U_OFF[name])


def build_gable(B, name, level):
    """A gable end: the wall up to Z_GABLE with its openings, then the
    triangle above with any of its own, which samples the brick band
    GABLE_SHIFT lower down."""
    fr = Frame(*MAIN_WALLS[name])
    items = rects_for(fr, WALL_ITEMS[name])
    lower = [(k, r) for k, r in items if r[3] < L.Z_GABLE]
    upper = [(k, r) for k, r in items if r[2] > L.Z_GABLE]
    notches = [(r[0], r[1], r[3]) for k, r in lower if r[2] < EPS]
    Lw = fr.L
    foot = outline_with_notches(0.0, Lw, 0.0, notches)
    wall_region(B, fr, foot + [(Lw, L.Z_GABLE), (0.0, L.Z_GABLE)], lower, level,
                U_OFF[name])
    tri = [(0.0, L.Z_GABLE), (Lw, L.Z_GABLE), (Lw, L.Z_WALL_TOP),
           (Lw / 2.0, gtop(Lw / 2.0)), (0.0, L.Z_WALL_TOP)]
    wall_region(B, fr, tri, upper, level, U_OFF[name], L.GABLE_SHIFT)


def cap_ring(B, split):
    """Cap the wall ring: a floor on the ground and a lid at the wall top.

    Both end up buried - the floor on the ground, the lid inside the roof -
    but the solid must be closed for the boolean to be exact. *split* is the
    pair of rim positions at the gable apexes the lid is cut between, since
    the rim follows both gables and is not planar. The rim is walked by hand
    in edge-index order, so the caps start on the same vertex every run.
    """
    bm = B.bm
    bm.edges.index_update()
    order = [e for e in bm.edges if len(e.link_faces) == 1]
    rim = set(order)
    branch = [v for e in order for v in e.verts
              if sum(1 for x in v.link_edges if x in rim) != 2]
    if branch:
        c = branch[0].co
        raise ValueError("the wall ring's rim branches at %d vertices, e.g. "
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
    if len(loops) != 2:
        raise ValueError("expected a floor and a lid, got %d holes: the wall "
                         "ring has a T-junction somewhere" % len(loops))
    blank = uv_patch("blank")
    floor = min(loops, key=lambda lp: max(v.co.z for v in lp))
    top = next(lp for lp in loops if lp is not floor)
    B.set_uv(bm.faces.new(floor), blank)
    keys = [B.v(p) for p in split]
    i, j = sorted(top.index(v) for v in keys)
    for half in (top[i:j + 1], top[j:] + top[:i + 1]):
        B.set_uv(bm.faces.new(half), blank)


def main_body(level):
    B = Builder()
    build_gable(B, "front", level)
    build_long(B, "east", level)
    build_gable(B, "rear", level)
    build_long(B, "west", level)
    cap_ring(B, split=[(0.0, -HY, Z_APEX), (0.0, HY, Z_APEX)])
    return B


# ================================================================== roof
def uv_roof(co):
    d = (XE - abs(co.x)) * L.SLOPE_F
    return ((co.y + YE) * PPM, L.ROOF_Y0 + d * L.ROOF_RPM)


def uv_eave(co):
    return ((co.y + YE) * PPM, L.EAVE_Y0 + (co.z - roof_under(XE)) * PPM)


def gable_slab():
    """The roof as one closed slab: a chevron section across x, extruded
    along the ridge. Its underside meets the long walls' faces at Z_EAVE, so
    once it is unioned with the walls the part outside them is the eave and
    rake soffit and the part inside disappears. The vertical sides of the
    section are the eave fascias with the gutter; the chevron end caps are
    the barge flashing over the gables.
    """
    B = Builder()
    zu = roof_under(XE)
    zr = roof_under(0.0)
    T = L.ROOF_T
    sec = [(-XE, zu), (-XE, zu + T), (0.0, zr + T), (XE, zu + T), (XE, zu),
           (0.0, zr)]
    kinds = ("fascia", "slope", "slope", "fascia", "soffit", "soffit")
    fns = {"fascia": uv_eave, "slope": uv_roof, "soffit": uv_patch("soffit")}
    for k, kind in enumerate(kinds):
        (p0, z0), (p1, z1) = sec[k], sec[(k + 1) % 6]
        B.face([(p0, -YE, z0), (p1, -YE, z1), (p1, YE, z1), (p0, YE, z0)], fns[kind])
    barge = uv_patch("barge")
    B.face([(p, -YE, z) for p, z in sec], barge)
    B.face([(p, YE, z) for p, z in reversed(sec)], barge)
    return B


# -------------------------------------------------------------------- vents
def vent(px, py, dia, height, sides):
    """A vent pipe on the roof: its foot is a slice of the roof plane inside
    the slab, so it is buried everywhere rather than only at its middle. The
    open end is painted as a bore."""
    B = Builder()
    r = dia / 2.0

    def foot(x):
        return roof_under(x) + 0.10

    base = foot(abs(px) + r)
    z1 = roof_top(px) + height
    ring = [(px + r * math.cos(a), py + r * math.sin(a))
            for a in [(i + 0.5) * 2.0 * math.pi / sides for i in range(sides)]]
    rx, ry, rw, rh = L.VENT
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        def fn(co, ax=ax, ay=ay, bx=bx, by=by):
            t = ((co.x - ax) * (bx - ax) + (co.y - ay) * (by - ay)) / \
                ((bx - ax) ** 2 + (by - ay) ** 2)
            return (rx + t * rw, ry + (co.z - base) * PPM)
        B.face([(ax, ay, foot(ax)), (bx, by, foot(bx)), (bx, by, z1),
                (ax, ay, z1)], fn)
    tx, ty, tw, th = L.PIPE_TOP
    B.face([(x, y, z1) for x, y in ring],
           lambda co: (tx + tw * (0.5 + (co.x - px) / dia),
                       ty + th * (0.5 + (co.y - py) / dia)))
    B.face([(x, y, foot(x)) for x, y in reversed(ring)], uv_patch("blank"))
    return B


# ---------------------------------------------------------------- downpipes
# One from each eave's gutter, at diagonally opposite corners: the east one
# at the rear, clear of the entrance bay, the west one at the front, so each
# gable shows one. The shape, the UVs and the placing rules are
# scripts/downpipes.py's.
PIPE_S = 2 * HY - 0.4
DOWNPIPE_SPOTS = [("east", PIPE_S), ("west", PIPE_S)]
DOWNPIPES = [DP.eave_pipe(*MAIN_WALLS[w], s, L.Z_EAVE, L.TAN, L.EAVE_OUT)
             for w, s in DOWNPIPE_SPOTS]


def downpipes(level):
    return DP.solids(DOWNPIPES, *downpipe_mode(level), L.PIPE_STRIP, L.ATLAS)


# ================================================================ assembly
def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    parts = [to_object(gable_slab(), "tmp_roof")]
    for B, name in downpipes(level):
        parts.append(to_object(B, name))
    for i, (px, py, dia, h) in enumerate(VENTS):
        n = vent_sides(level, dia)
        if n:
            parts.append(to_object(vent(px, py, dia, h, n), "tmp_vent%d" % i))
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # 1e-4: the exact boolean leaves the odd corner vertex a hundredth of a
    # millimetre off its neighbour; the smallest authored feature is far
    # larger than a 0.1 mm weld.
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # Recover the cost of coplanar boolean subdivisions. Keep UV and
        # material seams and every architectural edge.
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    # The union returns each gable's brick as an n-gon that keeps, in a
    # straight line along its top, the vertices where the rake soffit meets
    # it; the exporter's own triangulation joined three of them into a
    # zero-area triangle on every tier. Ear clipping with the beauty rule
    # never does, at the same count.
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4],
                          quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# ================================================================== checks
def _overlap(a, b, gap=0.0):
    return a[0] < b[1] + gap and b[0] < a[1] + gap and a[2] < b[3] + gap and b[2] < a[3] + gap


def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    gable = {"front", "rear"}
    for name, (p0, p1) in MAIN_WALLS.items():
        fr = Frame(p0, p1)
        spec = WALL_ITEMS[name]
        rects = [item_rect(fr, k, c, z) for k, c, z in spec]
        for (k, c, z), r in zip(spec, rects):
            if r[0] < 0.4 or r[1] > fr.L - 0.4:
                bad.append("%s: %s at %.2f is within 0.4 m of a corner" % (name, k, c))
            if EPS < r[2] < 0.3:
                bad.append("%s: %s at %.2f leaves a sliver of wall below it" % (name, k, c))
            if r[2] > L.Z_GABLE:
                # in a gable's triangle: clear of the split and of the rake
                if name not in gable:
                    bad.append("%s: %s at %.2f is above an eave wall's head" % (name, k, c))
                elif r[2] < L.Z_GABLE + 0.3:
                    bad.append("%s: %s at %.2f crowds the gable split" % (name, k, c))
                elif r[3] > min(roof_under(fr.P(s, 0)[0]) for s in r[:2]) - 0.4:
                    bad.append("%s: %s at %.2f runs up under the rake" % (name, k, c))
            elif r[3] > L.Z_HEAD + EPS:
                bad.append("%s: %s at %.2f runs up into the lintel band" % (name, k, c))
        for i, a in enumerate(rects):
            for b in rects[i + 1:]:
                if _overlap(a, b, 0.3):
                    bad.append("%s: two openings within 0.3 m of each other" % name)
    if not 2.0 <= L.Z_LEAF <= 2.4:
        bad.append("door leaf %.3f m is outside 2.0-2.4" % L.Z_LEAF)
    if not 0.9 <= LEAF_W["screen"] <= 1.0:
        bad.append("the entrance leaf is %.3f m wide" % LEAF_W["screen"])
    # the roof the atlas was painted for
    slope = (HX + L.EAVE_OUT) * L.SLOPE_F
    if abs(slope - L.SLOPE_LEN) > 1e-6:
        bad.append("slope is %.3f m, the atlas assumes %.3f" % (slope, L.SLOPE_LEN))
    # vents clear of the ridge, the eave and the gables
    for px, py, dia, h in VENTS:
        if abs(px) < dia / 2.0 + 0.4 or abs(px) > HX - 1.0:
            bad.append("the vent at (%.1f, %.1f) is on the ridge or the eave" % (px, py))
        if abs(py) > HY - 1.0:
            bad.append("the vent at (%.1f, %.1f) is over a gable" % (px, py))
    # downpipes clear of the corners and the openings
    for (w, s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        fr = Frame(*MAIN_WALLS[w])
        avoid = [(k, r[0], r[1]) for k, r in rects_for(fr, WALL_ITEMS[w])]
        bad += DP.problems(pipe, "the %s downpipe" % w, avoid)
    return bad


# ================================================================== build
def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
# Clear leaf widths and heights, as facade_atlas.py paints them: the
# entrance's one steel leaf inside the screen's door frame, the machinery
# door's pair inside its steel frame.
LEAF_W = {"screen": (L.SCREEN_LEAF[1] - L.SCREEN_LEAF[0]) / PPM,
          "bigdoor": (L.BIGDOOR[2] - 2 * L.BIGDOOR_FRAME) / PPM}
LEAF_H = {"screen": L.Z_LEAF,
          "bigdoor": (L.BIGDOOR[3] - L.BIGDOOR_FRAME) / PPM}


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the wall outline, without the
    overhangs and the downpipes. One storey: the hall floor at the ground,
    which the doors open onto level; its area is inside the outer wall
    faces. The louvres high in the gables are not doors."""
    def door(door_id, kind, wall, item, main=False):
        p0, p1 = MAIN_WALLS[wall]
        (c, z), = [(c, z) for k, c, z in WALL_ITEMS[wall] if k == item]
        return model_facts.wall_door(door_id, kind, p0, p1, Frame(p0, p1).s_at(c), z,
                                     LEAF_W[item], LEAF_H[item], main)

    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-HX, -HY), (HX, -HY), (HX, HY), (-HX, HY)],
        "storeys": [(0.0, 2 * HX * 2 * HY)],
        "doors": [door("entrance", "entrance", "east", "screen", main=True),
                  door("machinery", "vehicle", "front", "bigdoor")],
    }


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four
    orthographic elevations, a plan from above, and a raised three-quarter
    aerial off the front corner; plus aerials off the other corners and eye
    views at the doors and the rear gable. Working views only, not
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
        cam.location = centre + Vector(d) * 60.0
        scn.render.filepath = os.path.join(out_dir, "L%d_%s.png" % (level, name))
        bpy.ops.render.render(write_still=True)
        written.append(scn.render.filepath)
    persp = [("aerial", centre, Vector((1.0, -1.0, math.sqrt(2.0))), 3.0),
             ("aerial_rear", centre, Vector((-1.0, 1.0, math.sqrt(2.0))), 3.0),
             ("aerial_west", centre, Vector((-1.0, -1.0, math.sqrt(2.0))), 3.0),
             ("eye_front", Vector((0.0, -HY, 2.5)), Vector((0.35, -1.0, 0.1)), 1.6),
             ("eye_entrance", Vector((HX, -3.0, 2.2)), Vector((1.0, -0.5, 0.1)), 1.2),
             ("eye_rear", Vector((0.0, HY, 4.5)), Vector((-0.4, 1.0, 0.1)), 1.6),
             ("near_eave", Vector((HX, 4.5, 5.0)), Vector((1.0, 0.6, 0.25)), 0.45)]
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
