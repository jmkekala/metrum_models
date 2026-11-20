# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of liikekeskus_pharmacy, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A small suburban shopping centre of three units under one roof: a pharmacy
with the middle half of the frontage, a beauty salon in the left quarter and a
barber in the right. The plan is a 24 x 16 m rectangle and the roof is a single
gable whose ridge runs front to back, so the whole of the front is one wide
gable end. It overhangs 1.2 m at the rakes and 0.9 m at the eaves, in white
boarded soffit behind a white fascia, and that deep white A over coursed stone
is what the type is recognised by.

The front is four 4 m shopfront bays between stone piers. The pharmacy's pair
of doors is in the second quarter rather than on the centre line, the other two
units' doors are centred in their own bays, and above the
sign boards the gable opens into two raking curtain-wall panels either side of
a 2.8 m stone pier that runs unbroken from the pavement to the apex. A white
crest caps the ridge from rake to rake, and the centre's own sign stands on it
above the pier, a lit cube on four steel legs.

Construction is a set of closed solids unioned with Blender's exact boolean:
the wall ring, the roof, the ridge crest, the middle pier, the sign and its
stand, the wall-hung air handler and the roof stacks. Each is simple on its
own; the union is what
trims the wall tops into the roof and leaves the boundary of one empty volume,
so interior geometry cannot occur. The wall ring is capped at the top by two
planar faces rather than one, split at the ridge -- the rim follows the gable
and a single n-gon across it would not be flat.

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
from asset_build import bounds as _bounds, pivot_offset, to_object, union  # noqa: E402,F401

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
HX, HY = L.HX, L.HY                     # 12 x 8: a 24 x 16 m plan
XE, YE = HX + L.EAVE_OUT, HY + L.RAKE_OUT      # the roof's own extent
COS = 1.0 / math.hypot(1.0, L.SLOPE)           # run -> slope length
SLOPE_LEN = (XE / COS)                          # eave edge to ridge, 14.147 m

# The stone band repeats every 4 m, so a gable elevation is cut into courses
# at its multiples and each course indexes the band from its own base.
CUT = L.STONE_WRAP                              # 4.0
Z_CUT = 2.0 * CUT                               # 8.0, the second wrap line


def gunder(s):
    """Roof underside over a gable elevation, in that elevation's own s."""
    return L.Z_EAVE + L.SLOPE * (HX - abs(s - HX))


def gtop(s):
    """Where a gable wall stops: inside the roof slab, never touching it."""
    return gunder(s) + L.WALL_INTO_ROOF


def s_at(z):
    """Distance from the middle of a gable elevation at which gtop is *z*."""
    return HX - (z - L.WALL_INTO_ROOF - L.Z_EAVE) / L.SLOPE


def gglass(s):
    """Head of the gable curtain wall: under the rake, then capped flat."""
    return min(L.GABLE_HEAD_CAP, gunder(s) - L.GABLE_HEAD_DROP)


# The five piers of the front, and which of their vertical edges carry the
# shopfront head as a breakpoint: the two corner piers meet a side wall that
# has no such break, and putting one there would leave a T-junction.
PIER_BREAK = {0: (False, True), 1: (True, True), 2: (True, True),
              3: (True, True), 4: (True, False)}

BAY_OF = {name: (a, b) for name, a, b in L.BAYS}
DOOR_AT = {}
for _name, _s, _n in L.DOORS:
    DOOR_AT.setdefault(_name, []).append((_s, _n))


def opening_mode(level, where):
    """Whether an opening is cut into the wall or painted flat on it.

    The front is what this building is read by: the shopfront's 0.18 m reveal
    and the gable panels' are its depth, so both are cut until 70 m. The side
    windows and the back door are 0.14 m deep on elevations that are oblique
    or behind the building from any street camera, and they go flat one tier
    earlier. That is a deliberate departure from the catalog default of
    cutting through LOD1, and it is what makes LOD1 an intermediate tier at
    all: with the openings on every elevation cut, LOD1 came out the same
    triangle for triangle as LOD0, and a switch that saves nothing is worse
    than a reveal that goes flat at 35 m.
    """
    return "cut" if level < (2 if where == "front" else 1) else "flush"


def pier_kept(level):
    """The middle pier stands 0.25 m proud and carries the apex, so it is the
    one piece of relief that shapes the gable rather than decorating it. At
    LOD3 the 0.25 m is well under a pixel and the stone behind it is the same
    colour, so it flattens without changing what the elevation reads as."""
    return level < 3


def ahu_kept(level):
    return level < 3


def buttress_kept(level):
    """The side buttresses are the wall's own stone, so losing them costs no
    colour, only the shadow line of a 0.30 m projection. That is still worth
    having at LOD1; past 70 m it is under a pixel and the elevations are flat
    anyway."""
    return level < 2


def vent_kept(level, kind):
    """Both kinds break the ridge line seen from anywhere raised.

    The pipes are only 0.3 m across, but LOD1 starts at 35 m and there they
    are still two or three pixels of dark against a pale sky: dropping them at
    that switch was the one change visible in the comparison, so they carry to
    LOD1 and go at 70 m. The boxes are three times the size and hold to LOD2.
    """
    return level < (3 if kind == "box" else 2)


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
        # Area vector (Newell) from coordinates relative to the first vertex,
        # in double precision. Summed from absolute positions in mathutils'
        # 32-bit floats, a zero-area face keeps enough rounding to pass as
        # real and lands a third face on its edges.
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


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.

def uv_stone(fr, zbase=0.0):
    return lambda co: (fr.s_of(co) * PPM, L.STONE_Y0 + (co.z - zbase) * PPM)


def uv_patch(name):
    x, y, w, h = L.PATCHES[name]
    return lambda co: (x + w / 2.0, y + h / 2.0)


def uv_shop(fr, s0, s1=None, flip=False):
    """A glazed run. *flip* measures the lights back from s1 instead, which
    is how the part light in a run that does not divide evenly is kept at the
    pier end rather than left beside a door."""
    if flip:
        return lambda co: ((s1 - fr.s_of(co)) * PPM, L.SHOP_Y0 + co.z * PPM)
    return lambda co: ((fr.s_of(co) - s0) * PPM, L.SHOP_Y0 + co.z * PPM)


def uv_door(fr, s0, leaves):
    x, y, w, h = L.DOOR_DOUBLE if leaves == 2 else L.DOOR_SINGLE
    return lambda co: (x + (fr.s_of(co) - s0) * PPM, y + co.z * PPM)


def uv_fascia(fr, key, s0):
    x, y, w, h = L.FASCIA[key]
    return lambda co: (x + (fr.s_of(co) - s0) * PPM,
                       y + (co.z - L.Z_HEAD) * PPM)


def uv_reveal(fr, edge, zbase=0.0):
    """The cheek of an opening, in the wall's own stone.

    The surface is unrolled round the corner: a point *d* deep in the reveal
    takes the artwork that would have been *d* further along the wall in the
    direction the opening lies, so the coursing runs on into the cheek instead
    of restarting. Offsetting perpendicular to the edge handles a jamb, a head
    and a sill with one expression, and a raking head as well.
    """
    (s0, z0), (s1, z1) = edge
    ds, dz = s1 - s0, z1 - z0
    ln = math.hypot(ds, dz) or 1.0
    ns, nz = -dz / ln, ds / ln

    def f(co):
        d = -fr.out_of(co)                  # 0 at the wall face, + into it
        return ((fr.s_of(co) + ns * d) * PPM,
                L.STONE_Y0 + (co.z + nz * d - zbase) * PPM)
    return f


def uv_return(fr, s_edge, sign, zbase=0.0):
    """The side of something standing proud of the wall - a buttress, the
    middle pier - with the coursing carried on round its corner."""
    return lambda co: ((s_edge + sign * fr.out_of(co)) * PPM,
                       L.STONE_Y0 + (co.z - zbase) * PPM)


def uv_region(fr, rect, s0, z0, ppm=PPM, flip=False):
    x, y, w, h = rect
    def f(co):
        u = (fr.s_of(co) - s0) * ppm
        return (x + (w - u if flip else u), y + (co.z - z0) * ppm)
    return f


def uv_roof(left):
    x, y, w, h = L.ROOF
    def f(co):
        u = (co.y + YE) if left else (YE - co.y)
        return (x + u * L.ROOF_PPM,
                y + (XE - abs(co.x)) / COS * L.ROOF_PPM)
    return f


def uv_soffit_x(co):
    """The eave soffit: v runs out from the side wall."""
    return (co.y * PPM,
            L.SOF_Y0 + L.SOF_FASCIA + (abs(co.x) - HX) * PPM)


def uv_soffit_y(co):
    """The rake soffit: v runs out from the gable wall."""
    return (co.x * PPM,
            L.SOF_Y0 + L.SOF_FASCIA + (abs(co.y) - HY) * PPM)


def uv_eave_fascia(x):
    z0 = L.roof_under(x)
    return lambda co: (co.y * PPM, L.SOF_Y0 + (co.z - z0) * PPM)


def uv_rake_board(co):
    return (co.x / COS * PPM, L.SOF_Y0 + (co.z - L.roof_under(co.x)) * PPM)


def uv_logo(axis, origin):
    """One face of the ridge sign. All four take the same square region; the
    mark is symmetric about its upright, so the two faces that run along y
    need no mirroring to read the right way round."""
    x, y, w, h = L.LOGO
    def f(co):
        along = co.x if axis == "x" else co.y
        return (x + (along - origin) * PPM, y + (co.z - L.SIGN["z0"]) * PPM)
    return f


# The crest is white board like the fascia, so it takes the soffit band's
# fascia rows. Its sides and ends run the whole height of the solid, foot
# included, onto those 24 rows: the drip edge along the bottom rows then shows
# only where the end cap stands clear of the rake board, and the shingles cut
# the long sides off above it.
def crest_foot(x):
    """Where the crest's solid stops, inside the roof slab."""
    return L.roof_under(x) + 0.15


CREST_LO = crest_foot(L.CREST["w"] / 2.0)


def uv_crest_face(axis):
    def f(co):
        along = co.y if axis == "y" else co.x
        return (along * PPM, L.SOF_Y0 + (co.z - CREST_LO)
                / (L.Z_CREST - CREST_LO) * L.SOF_FASCIA)
    return f


def uv_crest_top(co):
    """The top and the foot, across the middle of the fascia rows, clear of
    the lines along both edges."""
    return (co.y * PPM, L.SOF_Y0 + 4.0 + (co.x / L.CREST["w"] + 0.5)
            * (L.SOF_FASCIA - 8.0))


# ============================================================ wall regions
def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge.

    Openings on one wall share head and sill heights, so a region's holes line
    up and the triangulator is free to join three collinear corners into a
    triangle of no area. Dropping it leaves a hole in the wall; keeping it
    leaves a face with no normal. Flipping the long edge it shares with its
    neighbour turns the pair into two real triangles meeting at the middle
    vertex, which is the standard repair.
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
        e0, e1, mid = max(pairs, key=lambda p: (pts[p[0]][0] - pts[p[1]][0]) ** 2
                          + (pts[p[0]][1] - pts[p[1]][1]) ** 2)
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
    """Triangulate a wall region with polygonal holes and add it."""
    loops = [outline] + list(holes)
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((s, z, 0.0)) for s, z in loop] for loop in loops])
    for a, b, c in _flip_slivers(flat, tris):
        B.face([fr.P(*flat[a], out), fr.P(*flat[b], out),
                fr.P(*flat[c], out)], uvfn)


def reveal(B, fr, poly, depth, zbase=0.0, skip_z=None):
    """Push *poly* back by *depth* and line the sides of the hole.

    An opening that stands on the ground gets no cheek along its threshold:
    the strip it would lay at z = 0 is inside the building's own footprint, so
    it would sit on top of the floor the wall ring is capped with, and the two
    coplanar faces leave the export non-manifold at the doorway.
    """
    for edge in zip(poly, poly[1:] + poly[:1]):
        (s0, z0), (s1, z1) = edge
        if skip_z is not None and abs(z0 - skip_z) < EPS and abs(z1 - skip_z) < EPS:
            continue
        B.face([fr.P(s0, z0), fr.P(s1, z1),
                fr.P(s1, z1, -depth), fr.P(s0, z0, -depth)],
               uv_reveal(fr, edge, zbase))


def rect_poly(r):
    s0, s1, z0, z1 = r
    return [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]


def item_rects(kind, s, z):
    w, h, cs, cb, ct = L.OPENINGS[kind]
    return ((s - w / 2 - cs, s + w / 2 + cs, z - cb, z + h + ct),
            (s - w / 2, s + w / 2, z, z + h))


def place_item(B, fr, kind, rect, region, level, skip_z=None):
    """A cut opening while it reads, the same rectangle painted flat after."""
    poly = rect_poly(rect)
    out = 0.0
    if opening_mode(level, "side") == "cut":
        reveal(B, fr, poly, L.REVEAL_DEPTH[kind], skip_z=skip_z)
        out = -L.REVEAL_DEPTH[kind]
    B.face([fr.P(s, z, out) for s, z in poly],
           uv_region(fr, region, rect[0], rect[2]))


# ----------------------------------------------------------- gable outlines
def gable_top_line(s_hi, s_lo, cap=None):
    """Points along the rake from *s_hi* to *s_lo*, flattened at *cap*."""
    stops = {s_hi, s_lo, HX}
    if cap is not None:
        off = s_at(cap)
        if 0.0 < off < HX:
            stops.update((HX - off, HX + off))
    lo, hi = min(s_lo, s_hi), max(s_lo, s_hi)
    xs = sorted(x for x in stops if lo - EPS <= x <= hi + EPS)
    pts = [(x, gtop(x) if cap is None else min(cap, gtop(x))) for x in xs]
    return pts[::-1] if s_hi > s_lo else pts


def panel_points(a, b):
    """The head of one curtain-wall panel, left to right, then back down."""
    off = HX - (L.GABLE_HEAD_CAP + L.GABLE_HEAD_DROP - L.Z_EAVE) / L.SLOPE
    xs = sorted({a, b} | {x for x in (HX - off, HX + off) if a < x < b})
    return [(x, gglass(x)) for x in xs] + [(b, L.GABLE_SILL)]


def panel_poly(a, b):
    return [(a, L.GABLE_SILL)] + panel_points(a, b)


def gable_band(B, fr, lo, cap, notches=(), holes=(), breaks=()):
    """The stone of a gable elevation between two of the band's wrap lines.

    *lo* is both the region's foot and the row the band is indexed from, which
    is what keeps the coursing continuous across a wrap: each course of wall
    starts the band again from its own base.
    """
    span = 2.0 * HX
    notch = {round(a, 4): (a, b) for a, b in notches}
    stops = sorted(set([0.0, span] + list(breaks)
                       + [v for n in notches for v in n]))
    pts = [(0.0, lo)]
    for a, b in zip(stops, stops[1:]):
        n = notch.get(round(a, 4))
        if n and abs(n[1] - b) < EPS:
            pts += panel_points(a, b)
        else:
            pts.append((b, lo))
    pts += gable_top_line(span, 0.0, cap)
    fill_region(B, fr, pts, holes, uv_stone(fr, lo))


def gable_apex(B, fr):
    """The triangle above the band's second wrap line.

    Its base carries the middle of the elevation as a breakpoint, because the
    band below it does: gable_top_line puts a vertex under the ridge whether
    the rake is flattened there or not, and a base without one would leave
    that vertex in the middle of an edge.
    """
    off = s_at(Z_CUT)
    fill_region(B, fr, [(HX - off, Z_CUT), (HX, Z_CUT), (HX + off, Z_CUT),
                        (HX, gtop(HX))], [], uv_stone(fr, Z_CUT))


# --------------------------------------------------------------- elevations
def bay_runs(name):
    """One shopfront bay, split into glazed runs and door units."""
    s0, s1 = BAY_OF[name]
    runs, cur = [], s0
    for ds, n in sorted(DOOR_AT.get(name, [])):
        a, b = ds - L.DOOR_W[n] / 2.0, ds + L.DOOR_W[n] / 2.0
        if a - cur > EPS:
            runs.append((cur, a, 0))
        runs.append((a, b, n))
        cur = b
    if s1 - cur > EPS:
        runs.append((cur, s1, 0))
    return runs


def build_front(B, fr, level):
    mode = opening_mode(level, "front")
    for i, (a, b) in enumerate(L.PIERS):
        lb, rb = PIER_BREAK[i]
        poly = [(a, 0.0), (b, 0.0)]
        if rb:
            poly.append((b, L.Z_HEAD))
        poly += [(b, L.Z_FASCIA), (a, L.Z_FASCIA)]
        if lb:
            poly.append((a, L.Z_HEAD))
        fill_region(B, fr, poly, [], uv_stone(fr, 0.0))

    for name, a, b in L.BAYS:
        runs = bay_runs(name)
        # The shopfront head is one line shared by three things: the sign
        # board above it, the opening's head reveal, and the tops of the
        # glazed runs and door units below. They all have to break at the same
        # places or the run boundaries land in the middle of somebody's edge.
        joints = [r[0] for r in runs[1:]]
        B.face([fr.P(s, z) for s, z in
                [(a, L.Z_HEAD)] + [(j, L.Z_HEAD) for j in joints]
                + [(b, L.Z_HEAD), (b, L.Z_FASCIA), (a, L.Z_FASCIA)]],
               uv_fascia(fr, name, a))
        poly = ([(a, 0.0), (b, 0.0), (b, L.Z_HEAD)]
                + [(j, L.Z_HEAD) for j in reversed(joints)] + [(a, L.Z_HEAD)])
        out = 0.0
        if mode == "cut":
            reveal(B, fr, poly, L.GLAZE_DEPTH, skip_z=0.0)
            out = -L.GLAZE_DEPTH
        for i, (r0, r1, leaves) in enumerate(runs):
            after_door = any(r[2] for r in runs[i + 1:])
            fn = (uv_door(fr, r0, leaves) if leaves
                  else uv_shop(fr, r0, r1, flip=after_door))
            B.face([fr.P(s, z, out)
                    for s, z in rect_poly((r0, r1, 0.0, L.Z_HEAD))], fn)

    breaks = [v for a, b in L.PIERS for v in (a, b)]
    gable_band(B, fr, L.GABLE_SILL, Z_CUT, notches=L.GABLE_PANELS,
               breaks=breaks)
    gable_apex(B, fr)
    for i, (a, b) in enumerate(L.GABLE_PANELS):
        poly = panel_poly(a, b)
        out = 0.0
        if mode == "cut":
            reveal(B, fr, poly, L.GLAZE_DEPTH, zbase=L.GABLE_SILL)
            out = -L.GLAZE_DEPTH
        fill_region(B, fr, poly, [],
                    uv_region(fr, L.GABLE_GLAZE, a, L.GABLE_SILL,
                              L.GABLE_PPM, flip=(i == 1)), out=out)


def build_rear(B, fr, level):
    door, _ = item_rects("maint_door", L.MAINT_DOOR_S, 0.0)
    d0, d1, _, dz1 = door
    span = 2.0 * HX
    fill_region(B, fr, [(0.0, 0.0), (d0, 0.0), (d0, dz1), (d1, dz1), (d1, 0.0),
                        (span, 0.0), (span, CUT), (0.0, CUT)], [],
                uv_stone(fr, 0.0))
    place_item(B, fr, "maint_door", door, L.MAINT_DOOR, level, skip_z=0.0)

    vents = [(s - L.LOUVRE_WH[0] / 2.0, s + L.LOUVRE_WH[0] / 2.0,
              z, z + L.LOUVRE_WH[1]) for s, z in L.LOUVRES]
    gable_band(B, fr, CUT, Z_CUT, holes=[rect_poly(v) for v in vents])
    gable_apex(B, fr)
    for v in vents:
        poly = rect_poly(v)
        out = 0.0
        if opening_mode(level, "side") == "cut":
            reveal(B, fr, poly, 0.10, zbase=CUT)
            out = -0.10
        B.face([fr.P(s, z, out) for s, z in poly],
               uv_region(fr, L.LOUVRE, v[0], v[2]))


def build_side(B, fr, level):
    holes = [rect_poly(item_rects("side_window", s, L.Z_WIN)[0])
             for s in L.SIDE_WINDOWS]
    fill_region(B, fr, rect_poly((0.0, fr.L, 0.0, CUT)), holes,
                uv_stone(fr, 0.0))
    for s in L.SIDE_WINDOWS:
        outer, _ = item_rects("side_window", s, L.Z_WIN)
        place_item(B, fr, "side_window", outer, L.SIDE_WINDOW, level)
    # the strip that runs on into the roof slab, where the union removes it
    top = L.Z_EAVE + L.WALL_INTO_ROOF
    B.face([fr.P(0.0, CUT), fr.P(fr.L, CUT), fr.P(fr.L, top), fr.P(0.0, top)],
           uv_patch("blank"))


def close_solid(B):
    """Cap the wall ring: a floor on the ground, a lid under the roof.

    Both end up buried, but the solid must be closed for the boolean to be
    exact. The lid is two faces rather than one: the rim follows the gable, so
    a single n-gon across it would not be planar. Split at the two ridge
    vertices, each half lies in one roof plane. The rim is walked by hand
    rather than with bmesh's holes_fill, which silently skips a loop whose
    vertices already carry a face.
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
    ridge = [i for i, v in enumerate(top)
             if abs(v.co.x) < 1e-4 and abs(abs(v.co.y) - HY) < 1e-4]
    if len(ridge) != 2:
        raise ValueError("expected two ridge vertices on the lid's rim, got %d"
                         % len(ridge))
    i, j = ridge
    for half in (top[i:j + 1], top[j:] + top[:i + 1]):
        B.set_uv(bm.faces.new(half), blank)


def side_frames():
    return (Frame((HX, -HY), (HX, HY)), Frame((-HX, HY), (-HX, -HY)))


def main_body(level):
    B = Builder()
    build_front(B, Frame((-HX, -HY), (HX, -HY)), level)
    build_rear(B, Frame((HX, HY), (-HX, HY)), level)
    for fr in side_frames():
        build_side(B, fr, level)
    close_solid(B)
    return B


# ==================================================================== roof
def roof():
    """One gable slab: deck, soffit, fascia and rake board in a single solid.

    A slab plus a separately swept eave would meet along the wall line
    tangentially, which is the case an exact boolean handles worst. Folded at
    the ridge and carried right out to the eave edge, it is one surface.
    """
    B = Builder()
    xs = [-XE, -HX, 0.0, HX, XE]
    ys = [-YE, -HY, HY, YE]
    zb = L.roof_under

    def zt(x):
        return L.roof_under(x) + L.ROOF_T

    for i in range(4):
        x0, x1 = xs[i], xs[i + 1]
        left = (x0 + x1) < 0.0
        for j in range(3):
            y0, y1 = ys[j], ys[j + 1]
            if i in (0, 3):
                soffit = uv_soffit_x
            elif j in (0, 2):
                soffit = uv_soffit_y
            else:
                soffit = uv_patch("blank")
            B.face([(x0, y0, zb(x0)), (x1, y0, zb(x1)),
                    (x1, y1, zb(x1)), (x0, y1, zb(x0))], soffit)
            B.face([(x0, y0, zt(x0)), (x0, y1, zt(x0)),
                    (x1, y1, zt(x1)), (x1, y0, zt(x1))], uv_roof(left))
    for x in (-XE, XE):
        for j in range(3):
            y0, y1 = ys[j], ys[j + 1]
            B.face([(x, y0, zb(x)), (x, y0, zt(x)),
                    (x, y1, zt(x)), (x, y1, zb(x))], uv_eave_fascia(x))
    for y in (-YE, YE):
        for i in range(4):
            x0, x1 = xs[i], xs[i + 1]
            B.face([(x0, y, zb(x0)), (x1, y, zb(x1)),
                    (x1, y, zt(x1)), (x0, y, zt(x0))], uv_rake_board)
    return B


# ============================================================ other solids
PIER_OUT = 0.25             # how far the middle pier stands off the gable
PIER_IN = 0.10              # and how far it sinks into it, so no face is
                            # coplanar with the wall it is unioned into


def mid_pier():
    """The stone pier under the apex, 2.8 m wide and unbroken to the top.

    Its face is three courses, cut where the stone band wraps, so the coursing
    runs on from the wall it stands against instead of restarting. Every other
    face of the solid carries the same two breakpoints, or the face edges meet
    the front's in their middles.
    """
    B = Builder()
    a, b = L.PIERS[2]
    x0, x1 = a - HX, b - HX
    y_out, y_in = -HY - PIER_OUT, -HY + PIER_IN
    fr = Frame((-HX, -HY), (HX, -HY))          # so the coursing lines up

    def top(x):
        return L.roof_under(x) + L.WALL_INTO_ROOF

    for lo, hi in ((0.0, CUT), (CUT, Z_CUT)):
        fill_region(B, fr, rect_poly((a, b, lo, hi)), [], uv_stone(fr, lo),
                    out=PIER_OUT)
    fill_region(B, fr, [(a, Z_CUT), (b, Z_CUT), (b, top(x1)), (HX, top(0.0)),
                        (a, top(x0))], [], uv_stone(fr, Z_CUT), out=PIER_OUT)

    blank = uv_patch("blank")
    B.face([(x0, y_in, 0.0), (x1, y_in, 0.0), (x1, y_in, CUT),
            (x1, y_in, Z_CUT), (x1, y_in, top(x1)), (0.0, y_in, top(0.0)),
            (x0, y_in, top(x0)), (x0, y_in, Z_CUT), (x0, y_in, CUT)], blank)
    for x, s_edge, sign in ((x0, a, -1.0), (x1, b, 1.0)):
        for lo, hi, base in ((0.0, CUT, 0.0), (CUT, Z_CUT, CUT),
                             (Z_CUT, top(x), Z_CUT)):
            B.face([(x, y_in, lo), (x, y_out, lo), (x, y_out, hi),
                    (x, y_in, hi)], uv_return(fr, s_edge, sign, base))
    for xa, xb in ((x0, 0.0), (0.0, x1)):
        B.face([(xa, y_in, top(xa)), (xb, y_in, top(xb)),
                (xb, y_out, top(xb)), (xa, y_out, top(xa))], blank)
    B.face([(x0, y_in, 0.0), (x0, y_out, 0.0), (x1, y_out, 0.0),
            (x1, y_in, 0.0)], blank)
    return B


def side_buttress(fr, s):
    """One stone buttress on a side wall, the same width and the same
    projection the whole way up: it is applied decoration, not a raking prop,
    so it has no batter.

    It stops at the same height as the wall behind it, inside the roof slab
    rather than under it: the soffit falls 0.45 m per metre as it comes out,
    so a buttress that stopped at the wall head would touch it along one line
    and push through it everywhere further out. Run up into the slab, the
    union trims it flush against the falling soffit instead, and no sliver of
    hidden surface is left under the eave. Its face is cut at the stone band's
    wrap line for the same reason the walls are.
    """
    B = Builder()
    s0, s1 = s - L.BUTTRESS_W / 2.0, s + L.BUTTRESS_W / 2.0
    z_top = L.Z_EAVE + L.WALL_INTO_ROOF
    out, o_in = L.BUTTRESS_OUT, -PIER_IN
    blank = uv_patch("blank")
    for lo, hi, base in ((0.0, CUT, 0.0), (CUT, z_top, None)):
        fn = blank if base is None else uv_stone(fr, base)
        B.face([fr.P(s0, lo, out), fr.P(s1, lo, out),
                fr.P(s1, hi, out), fr.P(s0, hi, out)], fn)
        B.face([fr.P(s0, lo, o_in), fr.P(s0, hi, o_in),
                fr.P(s1, hi, o_in), fr.P(s1, lo, o_in)], blank)
        for x, sign in ((s0, -1.0), (s1, 1.0)):
            side = blank if base is None else uv_return(fr, x, sign, base)
            B.face([fr.P(x, lo, o_in), fr.P(x, lo, out),
                    fr.P(x, hi, out), fr.P(x, hi, o_in)], side)
    B.face([fr.P(s0, z_top, o_in), fr.P(s1, z_top, o_in),
            fr.P(s1, z_top, out), fr.P(s0, z_top, out)], blank)
    B.face([fr.P(s0, 0.0, o_in), fr.P(s0, 0.0, out),
            fr.P(s1, 0.0, out), fr.P(s1, 0.0, o_in)], blank)
    return B


def crest():
    """The white crest along the ridge, rake to rake.

    Its foot is a slice of the two roof planes, like the stacks', so it lies
    inside the slab along its whole length: a flat foot across the ridge would
    be inside the slab only over a 15 mm band of height, which is not a solid
    intersection to hand a boolean. The union trims it to the shingles and
    leaves two vertical sides and a flat top. Its ends stand CREST["end"] past
    the rake boards, clear of their faces, so they cap the apex instead of
    lying coplanar with it.
    """
    B = Builder()
    hw = L.CREST["w"] / 2.0
    y0, y1 = -YE - L.CREST["end"], YE + L.CREST["end"]
    z1 = L.Z_CREST
    foot = crest_foot
    B.face([(-hw, y0, foot(-hw)), (0.0, y0, foot(0.0)), (hw, y0, foot(hw)),
            (hw, y0, z1), (-hw, y0, z1)], uv_crest_face("x"))
    B.face([(-hw, y1, z1), (hw, y1, z1), (hw, y1, foot(hw)),
            (0.0, y1, foot(0.0)), (-hw, y1, foot(-hw))], uv_crest_face("x"))
    for x in (-hw, hw):
        B.face([(x, y0, foot(x)), (x, y1, foot(x)), (x, y1, z1), (x, y0, z1)],
               uv_crest_face("y"))
    B.face([(-hw, y0, z1), (hw, y0, z1), (hw, y1, z1), (-hw, y1, z1)],
           uv_crest_top)
    for xa, xb in ((-hw, 0.0), (0.0, hw)):
        B.face([(xa, y0, foot(xa)), (xa, y1, foot(xa)),
                (xb, y1, foot(xb)), (xb, y0, foot(xb))], uv_crest_top)
    return B


def _box(B, x0, x1, y0, y1, z0, z1, uvfn):
    for f in ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
              [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
              [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
              [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
              [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
              [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)]):
        B.face(f, uvfn)


def sign_stand():
    """The four steel legs under the sign, in two pairs along the crest.

    Each runs 0.05 m into the crest below and the box above, so the union
    meets solid overlaps rather than faces lying on faces.
    """
    B = Builder()
    r = L.STAND["leg"] / 2.0
    z0, z1 = L.Z_CREST - 0.05, L.SIGN["z0"] + 0.05
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            x, y = sx * L.STAND["x"], L.SIGN["y"] + sy * L.STAND["y"]
            _box(B, x - r, x + r, y - r, y + r, z0, z1, uv_patch("steel"))
    return B


def sign_box():
    """The centre's illuminated sign, a closed cube on its stand, clear of
    the roof on every side: the four faces carry the mark, the lid is the
    lit field's colour and the underside is the steel of the stand."""
    B = Builder()
    w, h, d = L.SIGN["w"], L.SIGN["h"], L.SIGN["d"]
    x0, x1 = -w / 2.0, w / 2.0
    y0, y1 = L.SIGN["y"] - d / 2.0, L.SIGN["y"] + d / 2.0
    z0, z1 = L.SIGN["z0"], L.SIGN["z0"] + h
    for y in (y0, y1):
        B.face([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)],
               uv_logo("x", x0))
    for x in (x0, x1):
        B.face([(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)],
               uv_logo("y", y0))
    B.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
           uv_patch("sign_side"))
    B.face([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
           uv_patch("steel"))
    return B


def ahu_box():
    """The air handler hung on the right-hand wall."""
    B = Builder()
    y = L.AHU["s"] - HY
    y0, y1 = y - L.AHU["w"] / 2.0, y + L.AHU["w"] / 2.0
    x0, x1 = HX - 0.10, HX + L.AHU["d"]
    z0, z1 = L.AHU["z"], L.AHU["z"] + L.AHU["h"]
    fr = Frame((HX, -HY), (HX, HY))
    steel, blank = uv_patch("steel"), uv_patch("blank")
    B.face([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
           uv_region(fr, L.AHU_SIDE, y0 + HY, z0))
    B.face([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], blank)
    for y_ in (y0, y1):
        B.face([(x0, y_, z0), (x1, y_, z0), (x1, y_, z1), (x0, y_, z1)], steel)
    top = Frame((x0, y1), (x1, y1))
    B.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
           uv_region(top, L.AHU_TOP, 0.0, z1))
    B.face([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], steel)
    return B


def vent(kind, px, py, size, height, sides=8):
    """A stack on the roof: its foot is a slice of the roof plane, so it is
    inside the slab everywhere rather than only at its middle."""
    B = Builder()
    r = size / 2.0

    def foot(x):
        return L.roof_under(x) + 0.15

    base = L.roof_under(abs(px) + r) + 0.15
    z1 = L.roof_under(px) + L.ROOF_T + height
    steel, blank = uv_patch("steel"), uv_patch("blank")
    if kind == "box":
        ring = [(px - r, py - r), (px + r, py - r), (px + r, py + r),
                (px - r, py + r)]
        rect = L.VENT_BOX
    else:
        ring = [(px + r * math.cos(a), py + r * math.sin(a))
                for a in [i * 2.0 * math.pi / sides for i in range(sides)]]
        rect = L.VENT_PIPE
    rx, ry, rw, rh = rect
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        # every side gets the whole casing region across it rather than a run
        # along a shared perimeter: a stack is small, and a perimeter that did
        # not divide the region would wrap the artwork in the middle of a face
        def fn(co, ax=ax, ay=ay, bx=bx, by=by):
            t = 0.0 if abs(bx - ax) + abs(by - ay) < EPS else \
                ((co.x - ax) * (bx - ax) + (co.y - ay) * (by - ay)) / \
                ((bx - ax) ** 2 + (by - ay) ** 2)
            return (rx + t * rw, ry + (co.z - base) * PPM)
        B.face([(ax, ay, foot(ax)), (bx, by, foot(bx)), (bx, by, z1),
                (ax, ay, z1)], fn)
    B.face([(x, y, z1) for x, y in ring], steel)
    B.face([(x, y, foot(x)) for x, y in reversed(ring)], blank)
    return B


# ================================================================ assembly


def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    # The crest and the stand stay on every tier: the crest is the white line
    # along the roofline, and without its legs the sign would float.
    parts = [to_object(roof(), "tmp_roof"), to_object(crest(), "tmp_crest"),
             to_object(sign_stand(), "tmp_stand"),
             to_object(sign_box(), "tmp_sign")]
    if pier_kept(level):
        parts.append(to_object(mid_pier(), "tmp_pier"))
    if ahu_kept(level):
        parts.append(to_object(ahu_box(), "tmp_ahu"))
    if buttress_kept(level):
        for w, fr in enumerate(side_frames()):
            for i, s in enumerate(L.BUTTRESSES):
                parts.append(to_object(side_buttress(fr, s),
                                       "tmp_buttress%d%d" % (w, i)))
    for i, (kind, (px, py), size, height) in enumerate(L.VENTS):
        if vent_kept(level, kind):
            parts.append(to_object(
                vent(kind, px, py, size, height, 8 if level == 0 else 4),
                "tmp_vent%d" % i))
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # 1e-4 rather than 1e-5: the exact boolean resolves this building's 24 m
    # rake lines in 32-bit floats and leaves the odd corner vertex a hundredth
    # of a millimetre off its neighbour, which exports as two vertices and
    # reads as a non-manifold seam downstream. The smallest authored feature
    # here is the shopfront mullion's 0.05 m, so a 0.1 mm weld cannot reach it.
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # Recover the cost of coplanar boolean subdivisions. Keep UV and
        # material seams and every architectural edge; 0.001 radians tolerates
        # float noise on nominally planar faces.
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# ================================================================== checks
def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    spans = sorted([(a, b) for a, b in L.PIERS]
                   + [(a, b) for _n, a, b in L.BAYS])
    if abs(spans[0][0]) > EPS or abs(spans[-1][1] - 2 * HX) > EPS:
        bad.append("the front's bays and piers do not span 0 .. %.1f m" % (2 * HX))
    for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
        if abs(a1 - b0) > EPS:
            bad.append("gap or overlap on the front at %.3f m" % a1)
    for name, s, n in L.DOORS:
        a, b = BAY_OF[name]
        w = L.DOOR_W[n]
        if s - w / 2.0 < a - EPS or s + w / 2.0 > b + EPS:
            bad.append("the %s door runs outside its bay" % name)
    if not 2.0 <= L.Z_LEAF <= 2.4:
        bad.append("door leaf %.2f m is outside the 2.0 - 2.4 m band"
                   % L.Z_LEAF)
    if L.Z_HEAD > L.Z_FASCIA or L.Z_FASCIA != L.Z_EAVE:
        bad.append("the sign fascia does not sit between the shopfront head "
                   "and the eave")
    for a, b in L.GABLE_PANELS:
        if gglass(a) > gunder(a) - EPS or gglass(b) > gunder(b) - EPS:
            bad.append("a gable panel's head is through the roof")
        if max(gglass(a), gglass(b)) > Z_CUT - EPS:
            bad.append("a gable panel crosses the stone band's wrap line, "
                       "which its region cannot straddle")
    # region pixel sizes against the metres they are stretched over
    for rect, size, ppm, what in (
            (L.DOOR_DOUBLE, (L.DOOR_W[2], L.Z_HEAD), PPM, "double door"),
            (L.DOOR_SINGLE, (L.DOOR_W[1], L.Z_HEAD), PPM, "single door"),
            (L.SIDE_WINDOW, L.item_size_m("side_window"), PPM, "side window"),
            (L.MAINT_DOOR, L.item_size_m("maint_door"), PPM, "maintenance door"),
            (L.LOUVRE, L.LOUVRE_WH, PPM, "gable louvre"),
            (L.GABLE_GLAZE, (L.BAY_W, L.GABLE_HEAD_CAP - L.GABLE_SILL),
             L.GABLE_PPM, "gable curtain wall"),
            (L.AHU_SIDE, (L.AHU["w"], L.AHU["h"]), PPM, "air handler"),
            (L.LOGO, (L.SIGN["w"], L.SIGN["h"]), PPM, "ridge sign"),
            (L.ROOF, (2.0 * YE, SLOPE_LEN), L.ROOF_PPM, "roof slope")):
        for got, want, axis in ((rect[2], size[0] * ppm, "width"),
                                (rect[3], size[1] * ppm, "height")):
            if abs(got - want) > 1.0:
                bad.append("the %s region's %s is %d px for %.1f px of "
                           "artwork" % (what, axis, got, want))
    for name, a, b in L.BAYS:
        if abs(L.FASCIA[name][2] - (b - a) * PPM) > 1.0:
            bad.append("the %s sign board does not match its bay" % name)
    if abs(L.SIGN["d"] - L.SIGN["w"]) > EPS:
        bad.append("the ridge sign is %.2f x %.2f m in plan; its four faces "
                   "share one square region and cannot be stretched"
                   % (L.SIGN["w"], L.SIGN["d"]))
    if L.SIGN["y"] - L.SIGN["d"] / 2.0 < -YE or L.SIGN["y"] + L.SIGN["d"] / 2.0 > YE:
        bad.append("the ridge sign overhangs the roof it stands on")
    reach = L.STAND["x"] + L.STAND["leg"] / 2.0
    if reach > L.CREST["w"] / 2.0 - 0.02:
        bad.append("the sign's legs stand off the %.2f m crest" % L.CREST["w"])
    if (reach > L.SIGN["w"] / 2.0
            or L.STAND["y"] + L.STAND["leg"] / 2.0 > L.SIGN["d"] / 2.0):
        bad.append("the sign's legs stand outside the box they carry")
    if not 0.0 < crest_foot(0.0) - L.roof_under(0.0) < L.ROOF_T:
        bad.append("the crest's foot is not inside the roof slab")
    for kind, (px, _py), size, _h in L.VENTS:
        if abs(px) - size / 2.0 < L.CREST["w"] / 2.0 + 0.1:
            bad.append("a roof %s stands against the ridge crest" % kind)
    if L.SOF_FASCIA + L.RAKE_OUT * PPM > L.SOF_H:
        bad.append("the soffit band is too short for a %.2f m rake overhang"
                   % L.RAKE_OUT)
    if L.ROOF_T * PPM > L.SOF_FASCIA + 1.0:
        bad.append("the fascia rows cannot cover a %.3f m board" % L.ROOF_T)
    return bad


def check_roof(obj):
    """Nothing may stand higher than the sign, and nothing wider than the
    eaves: both are what the catalog row and notes.md quote."""
    xs = [v.co.x for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    return (round(max(xs) - min(xs), 3), round(max(zs), 3))


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# ================================================================ previews


def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four
    orthographic elevations, a plan from above, and a raised three-quarter
    aerial off the front corner. Working views only - not committed."""
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
    # raised three-quarter, 45 degrees up, off the entrance corner, and the
    # same from behind: the maintenance door and the air handler are on the
    # elevations the first misses
    for name, d in (("aerial", Vector((1.0, -1.0, math.sqrt(2.0)))),
                    ("aerial_rear", Vector((-1.0, 1.0, math.sqrt(2.0)))),
                    ("eye_front", Vector((0.35, -1.0, 0.22)))):
        cam.data.type = 'PERSP'
        cam.data.lens = 35.0
        dn = d.normalized()
        cam.location = centre + dn * radius * 3.0
        cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scn.render.filepath = os.path.join(out_dir, "L%d_%s.png" % (level, name))
        bpy.ops.render.render(write_still=True)
        written.append(scn.render.filepath)
    scn.camera, scn.render.resolution_x, scn.render.resolution_y = saved
    return written


if __name__ == "__main__":
    BUILD.main(build_all)
