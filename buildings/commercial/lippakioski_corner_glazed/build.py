# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of lippakioski_corner_glazed, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png
(the first run, without source.blend, creates it):

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A Helsinki-type straight-front canopy kiosk, freshly built: a 4.8 x 3.4 m
box of narrow vertical ribbed boarding on a low concrete plinth, its
front-right (serving) corner rounded at R 0.6 m, under a thin flat canopy
slab -- the "lippa" -- 0.30 m thick with rounded plan corners, projecting
1.6 m over the front and the serving side and 0.35 m at the rear and the
left. A glazing band runs from a stainless counter at 1.05 m up to the
soffit along the right half of the front, round the corner in facets and
along the front of the serving side, with folding shutter leaves stacked open
at each end. The customer door is at the left end of the front, a glazed
leaf with a transom light over it; the staff door is at the rear under a wall
lamp. Each door's reveal stands on a 0.02 m concrete floor slab
(scripts/door_floor.py). A lit KIOSKI board stands on two short posts over
the canopy's front edge; three drum downlights hang under the soffit. A
newspaper rack, two poster cases, a wall bench and a litter bin on a post
dress it, all under the canopy.

Construction is closed solids and one exact union, snapped to
asset_build.SNAP: the wall ring (built on one shared grid of rows, openings
recessed into it or painted flush, capped at the floor and buried in the
canopy at the top), the canopy slab with its hidden deck modelled directly,
and the sign, counter, shutters and furniture as closed solids.

Every number the mesh and the atlas share is imported from facade_atlas.py.
"""

import functools
import importlib
import math
import os
import sys

import bmesh
from mathutils import Vector


HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import facade_atlas as L  # noqa: E402  (layout constants shared with the atlas)
importlib.reload(L)       # an interactive session must not keep a stale layout

ASSET = L.ASSET
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import door_floor as DF  # noqa: E402
import model_facts  # noqa: E402
import shell_build as SB  # noqa: E402
from asset_build import to_object, union  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT,
                          tint=L.LIT_FACTOR)
get_material, export_all = BUILD.material, BUILD.export_all
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants

PPM = L.PPM
EPS = 1e-6
SNAP = asset_build.SNAP

# ================================================================ layout
DOOR_X = -1.65            # customer door's leaf centre, front wall
STAFF_X = 0.90            # staff door's leaf centre, rear wall
POSTER_Y = (0.55, -0.45)  # poster cases' centres, left wall
SHUTTER_FRONT_X1 = L.BAND_X0 - 0.02      # the front stack ends at the band's frame
SHUTTER_SIDE_Y0 = L.BAND_Y1 + 0.02       # the side stack starts at the band's frame
RACK_Y = (0.85, 1.45)                    # the rack along the serving side
BENCH_Y = (-1.1, 0.9)                    # the bench along the left wall
BENCH_LEGS = (-0.95, 0.75)
BIN_AT, BIN_R, BIN_Z = (-0.35, -2.55), 0.17, (0.50, 1.00)
POST_R = 0.035
LAMP = (STAFF_X - 0.08, STAFF_X + 0.08, 2.38, 2.52, 0.14)   # x0, x1, z0, z1, out
SIGN_X = 0.5 * ((L.CX0 + L.R_CANOPY["fl"]) + (L.CX1 - L.R_CANOPY["fr"]))
SIGN_SET, SIGN_T = 0.01, 0.07           # the board's face behind the canopy's edge; depth
SIGN_POST = 0.04                         # the stand-offs' square section
SIGN_POST_IN = 0.40                      # each post's centre in from the board's end
SIGN_POST_Y = 0.04                       # the posts' centre behind the edge, on the rim
SIGN_BURY = 0.04                         # the posts' foot into the canopy's rim
SHELF_OUT, SHELF_IN, SHELF_T, SHELF_EAR = 0.30, 0.05, 0.04, 0.05
SHELF_TOP = L.Z_COUNTER - 0.01
DOOR_CLEAR = (2.0, 2.0)   # depth, width kept clear in front of the customer door


# ================================================================= tiers
def wall_facets(level):
    return L.WALL_FACETS[level]


def recessed(level, what="band"):
    """LOD0/LOD1 set the glass and both doors back in their openings; LOD2
    keeps the doors' recesses (what="door"), each on its floor slab: the
    customer door's sunlit jamb and the staff door's slab nosing, a light
    line across its foot, pop at 25 m when they go. LOD2 paints the band
    flat on the wall plane, as LOD3 paints all three."""
    return level < (3 if what == "door" else 2)


def canopy_segs(level, corner):
    return L.CANOPY_SEGS["small" if corner == "rl" else "big"][level]


def kept(level, what):
    """Which attached pieces each tier keeps (notes.md, Per-tier triangle
    counts). A consumer switching by screen size shows LOD2 from about 25 m
    and LOD3 from about 52 m (notes.md, LOD review), so LOD2 keeps the
    counter, the rack, the bench, the bin, the wall lamp and the drums,
    which pop when they go there, and drops only what is under a pixel at
    25 m; LOD3 keeps what pops at 52 m: the counter, the shutter blocks, the
    rack, the bench, the bin and the drums, each at its fewest sides. The
    wall lamp goes at LOD3, under a pixel there by day and by night."""
    return level <= {"counter": 3, "shutters": 3, "shutter_leaves": 1, "rack": 3,
                     "bench": 3, "bench_legs": 0, "bin": 3, "lamp": 2, "well": 2,
                     "sign": 3, "downlights": 3}[what]


# ============================================================== mesh builder
# Vertices are made on the cache's 0.1 mm grid, and a UV function sees each
# corner's own coordinates rather than the snapped vertex.
Builder = functools.partial(SB.Builder, L.ATLAS, snap=True, uv_point=Vector)


def patch(name):
    return SB.uv_patch(L.PATCHES[name])


def uv_plan(rect, ppm):
    return lambda co: L.plan_px(rect, co.x, co.y, ppm)


# ================================================================= the plan
def wall_outline(level):
    """The wall outline at ground level, counter-clockwise from the front's
    left corner, with the serving corner as *n* chords of its arc. Each
    point carries its s round the outline as LOD0 measures it (the corner's
    chords at LOD0), so U agrees between tiers at every shared point."""
    n = wall_facets(level)
    cx, cy = L.WALL_C
    pts = [((L.WX0, L.WY0), 0.0)]
    front = cx - L.WX0
    for k in range(n + 1):
        a = math.radians(-90.0 + 90.0 * k / n)
        k0 = k * L.WALL_FACETS[0] // n
        pts.append(((cx + L.R_WALL * math.cos(a), cy + L.R_WALL * math.sin(a)),
                    front + k0 * L.CHORD))
    side0 = front + L.CORNER_RUN
    pts.append(((L.WX1, L.WY1), side0 + (L.WY1 - cy)))
    rear0 = side0 + (L.WY1 - cy) + (L.WX1 - L.WX0)
    pts.append(((L.WX0, L.WY1), rear0))
    return pts, rear0 + (L.WY1 - L.WY0)


def band_s(seg_kind, k0=None, x=None, y=None):
    """s along the glazing band of a point on its run."""
    if seg_kind == "front":
        return x - L.BAND_X0
    if seg_kind == "corner":
        return L.FRONT_RUN + k0 * L.CHORD
    return L.FRONT_RUN + L.CORNER_RUN + (y - L.WALL_C[1])


# ================================================================= walls
class Seg(SB.Frame):
    """A wall segment from p0 to p1, a Frame (s along it, z height, out along
    the outward normal) that also knows its U round the outline and carries
    its openings."""

    def __init__(self, p0, p1, u0, u1, kind):
        super().__init__(p0, p1)
        self.u0, self.u1, self.kind, self.items = u0, u1, kind, []

    def u(self, s):
        """s round the outline as LOD0 measures it, at s along this segment."""
        return self.u0 + (self.u1 - self.u0) * s / self.L


class Item:
    """A rectangle on a wall segment, s0..s1 x z0..z1: recessed *depth*
    with its own UV, or flush (depth 0). cont0/cont1: it runs on into the
    previous/next segment, so no jamb closes it there. *floor*, a
    door_floor.Floor, stands a recess that is on the ground on a concrete
    slab (build_ring())."""

    def __init__(self, s0, s1, z0, z1, depth, uv, cont0=False, cont1=False, floor=None):
        self.s0, self.s1, self.z0, self.z1 = s0, s1, z0, z1
        self.depth, self.uv, self.cont0, self.cont1 = depth, uv, cont0, cont1
        self.floor = floor if depth > 0.0 else None


def door_rect():
    """The customer door's casing on the front wall, (s0, s1, z0, z1)."""
    s0 = DOOR_X - L.DOOR_SIZE[0] / 2.0 - L.WX0
    return (s0, s0 + L.DOOR_SIZE[0], 0.0, L.Z_HEAD)


def staff_rect():
    """The staff door's casing on the rear wall, (s0, s1, z0, z1)."""
    s0 = L.WX1 - STAFF_X - L.STAFF_SIZE[0] / 2.0
    return (s0, s0 + L.STAFF_SIZE[0], 0.0, L.Z_MID)


def segments(level):
    """The wall ring's segments with their openings, posters and band."""
    pts, total = wall_outline(level)
    segs = []
    n = wall_facets(level)
    for i in range(len(pts)):
        (a, ua), (b, ub) = pts[i], pts[(i + 1) % len(pts)]
        kind = ("front" if i == 0 else "corner" if i <= n else
                ("side", "rear", "left")[i - n - 1])
        segs.append(Seg(a, b, ua, ub if i + 1 < len(pts) else total, kind))
    rec = recessed(level)
    bz0, bz1 = L.Z_COUNTER, L.Z_HEAD
    bx, by = L.BAND[0], L.BAND[1]

    def band_uv(sb0, scale=1.0):
        """Band U from sb0 at the segment's s = 0, *scale* band metres per
        metre of segment (a coarse tier's facet spans LOD0's chords)."""
        return lambda s, z: (bx + (sb0 + s * scale) * PPM, by + (z - bz0) * PPM)

    def region_uv(rect, s0, z0):
        return lambda s, z: (rect[0] + (s - s0) * PPM, rect[1] + (z - z0) * PPM)

    d_band = L.BAND_DEPTH if rec else 0.0
    # front: the customer door at its left end, on its floor slab while it
    # is recessed, the band from BAND_X0 on
    front = segs[0]
    ds0, ds1, dz0, dz1 = door_rect()
    front.items.append(Item(ds0, ds1, dz0, dz1,
                            L.DOOR_DEPTH if recessed(level, "door") else 0.0,
                            region_uv(L.DOOR, ds0, 0.0), floor=L.FLOORS["kiosk"]))
    s0 = L.BAND_X0 - L.WX0
    front.items.append(Item(s0, front.L, bz0, bz1, d_band, band_uv(-s0), cont1=True))
    # the corner's facets: wholly glazed above the counter
    for k in range(n):
        seg = segs[1 + k]
        sb = band_s("corner", k0=k * L.WALL_FACETS[0] // n)
        span = L.CHORD * L.WALL_FACETS[0] / n
        seg.items.append(Item(0.0, seg.L, bz0, bz1, d_band, band_uv(sb, span / seg.L),
                              True, True))
    # the serving side: the band's last panes from the corner
    side = segs[n + 1]
    sb = band_s("side", y=L.WALL_C[1])
    side.items.append(Item(0.0, L.SIDE_RUN, bz0, bz1, d_band, band_uv(sb), cont0=True))
    # rear: the staff door, on its floor slab while it is recessed
    rear = segs[n + 2]
    ss0, ss1, sz0, sz1 = staff_rect()
    rear.items.append(Item(ss0, ss1, sz0, sz1,
                           L.STAFF_DEPTH if recessed(level, "door") else 0.0,
                           region_uv(L.STAFF, ss0, 0.0), floor=L.FLOORS["staff"]))
    # left: two poster cases, flat on the wall on every tier
    left = segs[n + 3]
    pw = L.POSTER_SIZE[0]
    for yc, rect in zip(POSTER_Y, (L.POSTER_A, L.POSTER_B)):
        ps0 = L.WY1 - yc - pw / 2.0
        left.items.append(Item(ps0, ps0 + pw, L.Z_COUNTER, L.Z_MID, 0.0,
                               region_uv(rect, ps0, L.Z_COUNTER)))
    return segs


def _mitre(segs, i, depth):
    """The back-plane point *depth* behind corner i (the start of segment
    i), on the bisector of the two segments' normals."""
    a, b = segs[i - 1], segs[i]
    m = (a.n + b.n).normalized()
    p = b.p0 - m * (depth / m.dot(b.n))
    return p


def build_ring(B, segs):
    """Every segment on one grid: its s at its own corners and items, z at
    L.WALL_Z, shared by every segment so the vertical edges at the corners
    carry the same vertices from both sides.

    A recess on the ground with a *floor* (either door's) stands on a
    concrete slab (scripts/door_floor.py): a nosing on the wall plane from
    the ground to T across the opening, and the slab's top at T from the
    wall plane back to the closing face, where the threshold cheek would be.
    The recess (its back, its jambs) starts at T, and the wall cell on
    either side of the opening carries a corner at (s, T), so wall, nosing,
    slab and jambs meet on shared vertices and the open rim the floor cap
    closes runs straight along the wall line under the nosing."""
    zs = L.WALL_Z
    T = DF.T
    for i, seg in enumerate(segs):
        floored = {round(v, 6) for it in seg.items if it.floor is not None
                   for v in (it.s0, it.s1)}
        for it in seg.items:
            if it.z0 not in zs or it.z1 not in zs:
                raise ValueError("an opening on the %s wall is off the shared rows"
                                 % seg.kind)
        cuts = sorted({0.0, seg.L} | {round(v, 6) for it in seg.items
                                     for v in (it.s0, it.s1)})
        nxt = (i + 1) % len(segs)

        def Q(s, z, it, seg=seg, i=i, nxt=nxt):
            """A point on an item's back plane."""
            if it.cont0 and s < EPS:
                p = _mitre(segs, i, it.depth)
                return (p.x, p.y, z)
            if it.cont1 and s > seg.L - EPS:
                p = _mitre(segs, nxt, it.depth)
                return (p.x, p.y, z)
            return seg.P(s, z, -it.depth)

        def wall_uv(s, z, seg=seg):
            return (seg.u(s) * PPM, L.WALL_Y0 + z * PPM)

        rev = patch("reveal")(None)
        for sa, sb in zip(cuts, cuts[1:]):
            for za, zb in zip(zs, zs[1:]):
                sc, zc = (sa + sb) / 2.0, (za + zb) / 2.0
                it = next((it for it in seg.items
                           if it.s0 < sc < it.s1 and it.z0 < zc < it.z1), None)
                corners = [(sa, za), (sb, za), (sb, zb), (sa, zb)]
                if it is None:
                    if za < EPS:                # the nosing's corners on the jambs' lines
                        corners = ([(sa, za), (sb, za)]
                                   + ([(sb, za + T)] if round(sb, 6) in floored else [])
                                   + [(sb, zb), (sa, zb)]
                                   + ([(sa, za + T)] if round(sa, 6) in floored else []))
                    B.face([seg.P(s, z) for s, z in corners],
                           [wall_uv(s, z) for s, z in corners])
                    continue
                if it.depth <= 0.0:
                    B.face([seg.P(s, z) for s, z in corners],
                           [it.uv(s, z) for s, z in corners])
                    continue
                if it.floor is not None and abs(za - it.z0) < EPS:
                    # the slab: the nosing on the wall plane, its top back to
                    # the closing face; the recess starts on it
                    fuv = DF.uv(seg, it.floor, it.s0, it.z0)
                    B.face([seg.P(sa, za), seg.P(sb, za), seg.P(sb, za + T),
                            seg.P(sa, za + T)], fuv)
                    za += T
                    corners = [(sa, za), (sb, za), (sb, zb), (sa, zb)]
                    B.face([seg.P(sa, za), Q(sa, za, it), Q(sb, za, it), seg.P(sb, za)], fuv)
                B.face([Q(s, z, it) for s, z in corners], [it.uv(s, z) for s, z in corners])
                if abs(sa - it.s0) < EPS and not (it.cont0 and sa < EPS):
                    B.face([seg.P(sa, za), seg.P(sa, zb), Q(sa, zb, it), Q(sa, za, it)],
                           [rev] * 4)
                if abs(sb - it.s1) < EPS and not (it.cont1 and sb > seg.L - EPS):
                    B.face([seg.P(sb, za), Q(sb, za, it), Q(sb, zb, it), seg.P(sb, zb)],
                           [rev] * 4)
                if abs(za - it.z0) < EPS and za > EPS:
                    B.face([seg.P(sa, za), Q(sa, za, it), Q(sb, za, it), seg.P(sb, za)],
                           [rev] * 4)
                if abs(zb - it.z1) < EPS:
                    B.face([seg.P(sa, zb), seg.P(sb, zb), Q(sb, zb, it), Q(sa, zb, it)],
                           [rev] * 4)


def main_body(level):
    """The wall ring, capped by a floor on the ground (straight under the
    doors' slabs) and a lid at Z_BODY, buried in the canopy. Each cap is
    triangulated, collinear corners and all, its slivers repaired."""
    B = Builder()
    build_ring(B, segments(level))
    for loop in SB.rim_loops(B, 2):
        SB.cap(B, loop, patch("blank"), triangulate=True)
    return B


# ================================================================ canopy
def rounded_outline(x0, y0, x1, y1, radii, level):
    """Counter-clockwise plan outline of a rectangle with rounded corners,
    from the front-right corner's start; returns points and, per edge, which
    straight side ("front", "right", "rear", "left") or "arc" it is."""
    spec = (("fr", x1 - radii["fr"], y0 + radii["fr"], -90.0, "right"),
            ("rr", x1 - radii["rr"], y1 - radii["rr"], 0.0, "rear"),
            ("rl", x0 + radii["rl"], y1 - radii["rl"], 90.0, "left"),
            ("fl", x0 + radii["fl"], y0 + radii["fl"], 180.0, "front"))
    pts, kinds = [], []
    for key, cx, cy, a0, after in spec:
        n = canopy_segs(level, key)
        r = radii[key]
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            kinds.append("arc" if k < n else after)
    return pts, kinds


def canopy(level):
    """The canopy slab, z Z_SOFFIT..Z_TOP over its rounded plan, built
    directly as a closed solid: the fascia round it, the soffit under it,
    and on top the galvanised rim round the felt deck sunk to Z_DECK behind
    it (LOD3: one flat top). The fascia's straight run on the serving side
    samples the fascia band like every other edge, U running round the
    outline."""
    outer, kinds = rounded_outline(L.CX0, L.CY0, L.CX1, L.CY1, L.R_CANOPY, level)
    B = Builder()
    n = len(outer)
    z0, z1 = L.Z_SOFFIT, L.Z_TOP
    # the fascia; U starts where the rear-left corner's arc does, so the
    # band's one seam in U hides at the back
    start = [i for i in range(n) if kinds[i - 1] == "rear"][0]
    u = 0.0
    for i in [(start + k) % n for k in range(n)]:
        a, b = outer[i], outer[(i + 1) % n]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        cos = [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]
        uvs = [(u * PPM, L.FASCIA_Y0),
               ((u + ln) * PPM, L.FASCIA_Y0),
               ((u + ln) * PPM, L.FASCIA_Y0 + L.FASCIA_H),
               (u * PPM, L.FASCIA_Y0 + L.FASCIA_H)]
        B.face(cos, uvs)
        u += ln
    B.face([(x, y, z0) for x, y in reversed(outer)], uv_plan(L.SOFFIT, PPM))
    deck_uv = uv_plan(L.DECK, L.DECK_PPM)
    if not kept(level, "well"):
        B.face([(x, y, z1) for x, y in outer], deck_uv)
        return B
    r_in = {k: v - L.RIM for k, v in L.R_CANOPY.items()}
    inner, _ = rounded_outline(L.CX0 + L.RIM, L.CY0 + L.RIM, L.CX1 - L.RIM,
                               L.CY1 - L.RIM, r_in, level)
    up = patch("flash")
    for i in range(n):
        j = (i + 1) % n
        B.face([(outer[i][0], outer[i][1], z1), (outer[j][0], outer[j][1], z1),
                (inner[j][0], inner[j][1], z1), (inner[i][0], inner[i][1], z1)], deck_uv)
        B.face([(inner[i][0], inner[i][1], z1), (inner[j][0], inner[j][1], z1),
                (inner[j][0], inner[j][1], L.Z_DECK), (inner[i][0], inner[i][1], L.Z_DECK)],
               up)
    B.face([(x, y, L.Z_DECK) for x, y in inner], deck_uv)
    return B


# ================================================================== solids
def box(x0, x1, y0, y1, z0, z1, uv):
    """A closed box; *uv* maps a side ("-y", "+x", "+y", "-x", "top",
    "bottom") to a UV function, "*" for any side not named."""
    rest = uv.get("*")
    return SB.box(Builder(), x0, x1, y0, y1, z0, z1,
                  [uv.get(k, rest) for k in ("-y", "+x", "+y", "-x")],
                  uv.get("top", rest), uv.get("bottom", rest))


def face_uv(rect, axis, a0, z0, ppm=PPM, flip=False):
    """A vertical face mapped onto a region: U along *axis* from a0 (or back
    from it when *flip*), V up from z0."""
    def fn(co):
        a = getattr(co, axis) - a0
        return rect[0] + (-a if flip else a) * ppm, rect[1] + (co.z - z0) * ppm
    return fn


def sign_z():
    """The board's foot and top."""
    z0 = L.Z_TOP + L.SIGN_GAP
    return z0, z0 + L.SIGN_H


def sign():
    """The lit board over the canopy's front edge: a slim box SIGN_W x
    SIGN_H, galvanised round its edges, its face SIGN_SET behind the
    canopy's edge, standing SIGN_GAP clear of the flashing on two short
    square posts whose feet are sunk into the canopy's rim."""
    hw = L.SIGN_W / 2.0
    y0 = L.CY0 + SIGN_SET
    z0, z1 = sign_z()
    face = face_uv(L.SIGN, "x", SIGN_X - hw, z0, L.SIGN_PPM)
    parts = [box(SIGN_X - hw, SIGN_X + hw, y0, y0 + SIGN_T, z0, z1,
                 {"*": patch("flash"), "+y": patch("sign_edge"), "-y": face})]
    p = SIGN_POST / 2.0
    yc = L.CY0 + SIGN_POST_Y
    for xc in (SIGN_X - hw + SIGN_POST_IN, SIGN_X + hw - SIGN_POST_IN):
        parts.append(box(xc - p, xc + p, yc - p, yc + p, L.Z_TOP - SIGN_BURY, z0 + 0.02,
                         {"*": patch("flash")}))
    return parts


def downlights(level):
    """The soffit's three surface-mounted drum lamps: a white housing over
    an opal band and an opal base, the housing's top sunk 0.02 m into the
    slab so the union seats it."""
    n = (12, 8, 6, 4)[level]
    zb, zl = L.DOWNLIGHT_Z
    zt = L.Z_SOFFIT + 0.02
    r = L.DOWNLIGHT_R
    out = []
    for x, y in L.DOWNLIGHTS:
        B = Builder()
        ring = [(x + r * math.cos(2 * math.pi * (k + 0.5) / n),
                 y + r * math.sin(2 * math.pi * (k + 0.5) / n)) for k in range(n)]
        for k in range(n):
            (ax, ay), (bx, by) = ring[k], ring[(k + 1) % n]
            B.face([(ax, ay, zb), (bx, by, zb), (bx, by, zl), (ax, ay, zl)], patch("light"))
            B.face([(ax, ay, zl), (bx, by, zl), (bx, by, zt), (ax, ay, zt)], patch("fitting"))
        B.face([(px, py, zt) for px, py in ring], patch("fitting"))
        B.face([(px, py, zb) for px, py in reversed(ring)], patch("light"))
        out.append(B)
    return out


def counter(level):
    """The stainless counter shelf under the whole band, following the
    corner: SHELF_OUT proud of the wall, SHELF_IN into it so the union seats
    it, with ears SHELF_EAR past the band's ends."""
    n = wall_facets(level)
    cx, cy = L.WALL_C
    path = [((L.BAND_X0 - SHELF_EAR, L.WY0), (0.0, -1.0))]
    for k in range(n + 1):
        a = math.radians(-90.0 + 90.0 * k / n)
        path.append(((cx + L.R_WALL * math.cos(a), cy + L.R_WALL * math.sin(a)),
                     (math.cos(a), math.sin(a))))
    path.append(((L.WX1, L.BAND_Y1 + SHELF_EAR), (1.0, 0.0)))
    B = Builder()
    steel = patch("steel")

    def off(p, d, r, arc):
        if arc:
            return (cx + (L.R_WALL + r) * d[0], cy + (L.R_WALL + r) * d[1])
        return (p[0] + d[0] * r, p[1] + d[1] * r)
    outer = [off(p, d, SHELF_OUT, 0 < i < len(path) - 1) for i, (p, d) in enumerate(path)]
    inner = [off(p, d, -SHELF_IN, 0 < i < len(path) - 1) for i, (p, d) in enumerate(path)]
    z0, z1 = SHELF_TOP - SHELF_T, SHELF_TOP
    for i in range(len(path) - 1):
        o0, o1, i0, i1 = outer[i], outer[i + 1], inner[i], inner[i + 1]
        B.face([(o0[0], o0[1], z1), (o1[0], o1[1], z1), (i1[0], i1[1], z1), (i0[0], i0[1], z1)],
               steel)
        B.face([(i0[0], i0[1], z0), (i1[0], i1[1], z0), (o1[0], o1[1], z0), (o0[0], o0[1], z0)],
               steel)
        B.face([(o0[0], o0[1], z0), (o1[0], o1[1], z0), (o1[0], o1[1], z1), (o0[0], o0[1], z1)],
               steel)
        B.face([(i1[0], i1[1], z0), (i0[0], i0[1], z0), (i0[0], i0[1], z1), (i1[0], i1[1], z1)],
               steel)
    for o, i_ in ((outer[0], inner[0]), (outer[-1], inner[-1])):
        B.face([(o[0], o[1], z0), (i_[0], i_[1], z0), (i_[0], i_[1], z1), (o[0], o[1], z1)],
               steel)
    return B


def shutter_stack(p0, along, out, level):
    """One stack of folded shutter leaves on a wall: *p0* the stack's end on
    the wall plane, *along* the wall, *out* its outward normal (plan unit
    vectors). At LOD0/LOD1 the stack is stepped (L.SHUTTER_LAYERS): a hinge
    rail set back from both edges, so a shadow gap shows between the leaves
    and the wall, then three leaves, each a little narrower; from LOD2 it is
    one block. One closed prism over the stepped plan outline. Faces facing
    out sample the stack's front elevation, faces facing along the wall its
    side, faces facing the wall and the ends a dark patch."""
    w, _t, z0, z1 = L.SHUTTER
    layers = L.SHUTTER_LAYERS if kept(level, "shutter_leaves") else ((0.0, -0.02, 0.10),)
    # the stepped outline in (a along, t out), going round one way
    right = []
    for inset, t0, t1 in layers:
        right += [(w - inset, t0), (w - inset, t1)]
    left = [(w - a, t) for a, t in reversed(right)]
    loop = right + left
    P = lambda a, t: (p0[0] + along[0] * a + out[0] * t,  # noqa: E731
                      p0[1] + along[1] * a + out[1] * t)
    ring = [P(a, t) for a, t in loop]
    # the loop runs counter-clockwise in (a, t): a stretch of constant t
    # faces out where a falls along it. Reversed to run counter-clockwise
    # in plan, that becomes where a rises.
    area = sum(ax * by - bx * ay for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]))
    out_sign = -1.0
    if area < 0.0:
        ring.reverse()
        loop.reverse()
        out_sign = 1.0

    face, edge = L.SHUTTER_FACE, L.SHUTTER_EDGE

    def local(co):
        dx, dy = co.x - p0[0], co.y - p0[1]
        return dx * along[0] + dy * along[1], dx * out[0] + dy * out[1]

    def uv_face(co):
        a, _ = local(co)
        return face[0] + a * PPM, face[1] + (co.z - z0) * PPM

    def uv_edge(co):
        _, t = local(co)
        return edge[0] + (t + 0.02) * PPM, edge[1] + (co.z - z0) * PPM

    B = Builder()
    n = len(ring)
    for k in range(n):
        (a0, t0), (a1, t1) = loop[k], loop[(k + 1) % n]
        (ax, ay), (bx, by) = ring[k], ring[(k + 1) % n]
        if abs(t1 - t0) < EPS:                   # faces out, or toward the wall
            uv = uv_face if (a1 - a0) * out_sign > 0 else patch("shutter_top")
        else:
            uv = uv_edge
        B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], uv)
    B.face([(x, y, z1) for x, y in ring], patch("shutter_top"))
    B.face([(x, y, z0) for x, y in reversed(ring)], patch("shutter_top"))
    return B


def shutters(level):
    """The folding shutter leaves, stacked open against the wall at each end
    of the band, their hinge rails 0.02 m into the wall."""
    w = L.SHUTTER[0]
    front = shutter_stack((SHUTTER_FRONT_X1 - w, L.WY0), (1.0, 0.0), (0.0, -1.0), level)
    side = shutter_stack((L.WX1, SHUTTER_SIDE_Y0 + w), (0.0, -1.0), (1.0, 0.0), level)
    return [front, side]


def rack():
    """The wall-fixed magazine rack on the serving side, past the shutters."""
    w, d, z0, z1 = L.RACK
    y0, y1 = RACK_Y
    return box(L.WX1 - 0.02, L.WX1 + d, y0, y1, z0, z1,
               {"*": patch("post"), "+x": face_uv(L.RACK_FACE, "y", y1, z0, flip=True)})


def bench(level):
    """The wall-fixed bench along the left wall: a timber seat and, at LOD0,
    two slim front legs."""
    ln, d, z0, z1 = L.BENCH
    y0, y1 = BENCH_Y
    x0 = L.WX0 - d
    top = lambda co: (L.BENCH_TOP[0] + (co.y - y0) * PPM,  # noqa: E731
                      L.BENCH_TOP[1] + (co.x - x0) * PPM)
    parts = [box(x0, L.WX0 + 0.02, y0, y1, z0, z1, {"*": patch("timber"), "top": top})]
    if kept(level, "bench_legs"):
        for yl in BENCH_LEGS:
            parts.append(box(x0 + 0.03, x0 + 0.08, yl - 0.025, yl + 0.025, 0.0, z0 + 0.01,
                             {"*": patch("post")}))
    return parts


def litter_bin(level):
    """A litter bin on a short post under the canopy, clear of the door."""
    n, np_ = ((10, 6), (6, 4), (6, 4), (4, 4))[level]
    bx, by = BIN_AT
    B = Builder()
    ring = [(bx + BIN_R * math.cos(2 * math.pi * (k + 0.5) / n),
             by + BIN_R * math.sin(2 * math.pi * (k + 0.5) / n)) for k in range(n)]
    SB.prism(B, ring, BIN_Z[0], BIN_Z[1], patch("bin"), patch("bin"), patch("bin"))
    P = Builder()
    ring = [(bx + POST_R * math.cos(2 * math.pi * (k + 0.5) / np_),
             by + POST_R * math.sin(2 * math.pi * (k + 0.5) / np_)) for k in range(np_)]
    SB.prism(P, ring, 0.0, BIN_Z[0] + 0.02, patch("post"), patch("post"), patch("post"))
    return [B, P]


def lamp():
    """The wall lamp over the staff door: a small graphite bulkhead, its
    opal lens in the lower part of its face and on its underside."""
    x0, x1, z0, z1, out = LAMP
    return box(x0, x1, L.WY1 - 0.02, L.WY1 + out, z0, z1,
               {"*": patch("lamp"), "bottom": patch("lens"),
                "+y": face_uv(L.LAMP_FACE, "x", x1, z0, flip=True)})


# ================================================================ assembly
def build_lod(level):
    body = to_object(main_body(level), "tmp_body")
    parts = [to_object(canopy(level), "tmp_canopy")]
    if kept(level, "sign"):
        parts += [to_object(b, "tmp_sign") for b in sign()]
    if kept(level, "downlights"):
        parts += [to_object(b, "tmp_downlight") for b in downlights(level)]
    if kept(level, "counter"):
        parts.append(to_object(counter(level), "tmp_counter"))
    if kept(level, "shutters"):
        parts += [to_object(b, "tmp_shutter") for b in shutters(level)]
    if kept(level, "rack"):
        parts.append(to_object(rack(), "tmp_rack"))
    if kept(level, "bench"):
        parts += [to_object(b, "tmp_bench") for b in bench(level)]
    if kept(level, "bin"):
        parts += [to_object(b, "tmp_bin") for b in litter_bin(level)]
    if kept(level, "lamp"):
        parts.append(to_object(lamp(), "tmp_lamp"))
    obj = union(body, parts, snap=SNAP)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # recover the grid's and the boolean's coplanar subdivisions, keeping
        # UV seams
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
    if not 2.0 <= L.DOOR_LEAF_H <= 2.4 or not 2.0 <= L.STAFF_LEAF_H <= 2.4:
        bad.append("a door leaf is outside 2.0-2.4 m")
    if L.Z_HEAD >= L.Z_SOFFIT or L.Z_SOFFIT >= L.Z_BODY or L.Z_BODY >= L.Z_DECK:
        bad.append("head, soffit, wall top and deck are out of order")
    # corner margins on the front and the rear
    dl = DOOR_X - L.DOOR_SIZE[0] / 2.0
    if dl - L.WX0 < 0.15:
        bad.append("the customer door is within 0.15 m of the front's corner")
    if DOOR_X + L.DOOR_SIZE[0] / 2.0 > SHUTTER_FRONT_X1 - L.SHUTTER[0] - 0.2:
        bad.append("the customer door crowds the front shutter stack")
    sx0, sx1 = STAFF_X - L.STAFF_SIZE[0] / 2.0, STAFF_X + L.STAFF_SIZE[0] / 2.0
    if sx0 < L.WX0 + 0.3 or sx1 > L.WX1 - 0.3:
        bad.append("the staff door is within 0.3 m of a rear corner")
    # the serving side: band, shutters, rack in order, clear of the corner
    if SHUTTER_SIDE_Y0 + L.SHUTTER[0] > RACK_Y[0] - 0.1:
        bad.append("the side shutter stack runs into the rack")
    if RACK_Y[1] > L.WY1 - 0.2:
        bad.append("the rack is within 0.2 m of the rear corner")
    # the left wall: posters inside it, bench under them
    for yc in POSTER_Y:
        if yc + L.POSTER_SIZE[0] / 2.0 > L.WY1 - 0.3 or yc - L.POSTER_SIZE[0] / 2.0 < L.WY0 + 0.3:
            bad.append("a poster case is within 0.3 m of a corner")
    if BENCH_Y[0] < L.WY0 + 0.2 or BENCH_Y[1] > L.WY1 - 0.2:
        bad.append("the bench runs past the left wall")
    # everything attached stays inside the canopy's plan
    reach = {"bench": L.WX0 - L.BENCH[1] - L.CX0,
             "rack": L.CX1 - (L.WX1 + L.RACK[1]),
             "lamp": L.CY1 - (L.WY1 + LAMP[4]),
             "bin": min(BIN_AT[1] - BIN_R - L.CY0, BIN_AT[0] - BIN_R - L.CX0)}
    for what, gap in reach.items():
        if gap < 0.02:
            bad.append("the %s reaches past the canopy's plan" % what)
    # the customer door's approach: nothing modelled 2 m out over 2 m width
    cx0, cx1 = DOOR_X - DOOR_CLEAR[1] / 2.0, DOOR_X + DOOR_CLEAR[1] / 2.0
    cy0 = L.WY0 - DOOR_CLEAR[0]
    if BIN_AT[0] - BIN_R < cx1 and BIN_AT[1] + BIN_R > cy0:
        bad.append("the litter bin stands in front of the customer door")
    if SHUTTER_FRONT_X1 - L.SHUTTER[0] < cx1:
        bad.append("the front shutter stack stands in front of the customer door")
    if L.BAND_X0 - SHELF_EAR < cx1:
        bad.append("the counter reaches in front of the customer door")
    # canopy and sign
    if L.Z_TOP - L.Z_SOFFIT < 0.25:
        bad.append("the canopy is under 0.25 m thick")
    for key, r in L.R_CANOPY.items():
        if r - L.RIM < 0.05:
            bad.append("the %s corner's radius leaves no rounded deck" % key)
    hw = L.SIGN_W / 2.0
    if SIGN_X - hw < L.CX0 + L.R_CANOPY["fl"] or SIGN_X + hw > L.CX1 - L.R_CANOPY["fr"]:
        bad.append("the sign board runs onto the canopy's rounded corners")
    p = SIGN_POST / 2.0
    if SIGN_POST_Y - p < 0.005 or SIGN_POST_Y + p > L.RIM - 0.005:
        bad.append("the sign's posts do not stand on the canopy's rim")
    if SIGN_POST_Y - p < SIGN_SET or SIGN_POST_Y + p > SIGN_SET + SIGN_T:
        bad.append("the sign's posts are not under the board")
    if L.SIGN_GAP < 0.06:
        bad.append("the gap under the sign board is too thin to show")
    if L.SIGN_CAP + 0.04 > L.SIGN_H - 2 * L.SIGN_FRAME:
        bad.append("the sign's capitals crowd its frame")
    if (max(t1 for _i, _t0, t1 in L.SHUTTER_LAYERS) != L.SHUTTER[1]
            or min(t0 for _i, t0, _t1 in L.SHUTTER_LAYERS) != -0.02
            or max(i for i, _t0, _t1 in L.SHUTTER_LAYERS) * 2 >= L.SHUTTER[0]):
        bad.append("the shutter leaves' layers leave the stack's box")
    # each door's reveal on its floor slab (scripts/door_floor.py): the
    # slab's region the casing's width and the reveal's depth, at grade
    bad += DF.problems(L.FLOORS["kiosk"], "the customer door", door_rect(), L.DOOR_DEPTH)
    bad += DF.problems(L.FLOORS["staff"], "the staff door", staff_rect(), L.STAFF_DEPTH)
    zb, zl = L.DOWNLIGHT_Z
    if not zb < zl < L.Z_SOFFIT or zb < L.Z_HEAD - 0.10:
        bad.append("the downlights' heights are out of order")
    for x, y in L.DOWNLIGHTS:
        dx = max(L.WX0 - x, x - L.WX1, 0.0)
        dy = max(L.WY0 - y, y - L.WY1, 0.0)
        if math.hypot(dx, dy) < L.DOWNLIGHT_R + 0.10:
            bad.append("a downlight is too near the wall")
    if SHELF_TOP >= L.Z_COUNTER:
        bad.append("the counter does not sit under the band's sill")
    w, d = L.CX1 - L.CX0, L.CY1 - L.CY0
    if w > 7.0 + EPS or d > 5.5 + EPS:
        bad.append("plan bounds %.2f x %.2f m exceed 7.0 x 5.5" % (w, d))
    # region sizes against the metres they stand for
    for rect, (wm, hm), ppm, what in (
            (L.SOFFIT, (w, d), PPM, "soffit"), (L.DECK, (w, d), L.DECK_PPM, "deck"),
            (L.BAND, (L.BAND_LEN, L.Z_HEAD - L.Z_COUNTER), PPM, "band"),
            (L.DOOR, L.DOOR_SIZE, PPM, "door"), (L.STAFF, L.STAFF_SIZE, PPM, "staff"),
            (L.SIGN, (L.SIGN_W, L.SIGN_H), L.SIGN_PPM, "sign"),
            (L.SHUTTER_FACE, (L.SHUTTER[0], L.SHUTTER[3] - L.SHUTTER[2]), PPM, "shutter face"),
            (L.SHUTTER_EDGE, (L.SHUTTER[1] + 0.02, L.SHUTTER[3] - L.SHUTTER[2]), PPM,
             "shutter edge"),
            (L.LAMP_FACE, (LAMP[1] - LAMP[0], LAMP[3] - LAMP[2]), PPM, "lamp face")):
        if abs(rect[2] - wm * ppm) > 0.5 or abs(rect[3] - hm * ppm) > 0.5:
            bad.append("the %s region is %.1f x %.1f px for %.2f x %.2f m"
                       % (what, rect[2], rect[3], wm, hm))
    return bad


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def footprint():
    """The wall outline at ground level, LOD0's corner chords included."""
    pts, _ = wall_outline(0)
    return [p for p, _s in pts]


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the wall outline at ground level;
    the canopy, the counter and the furniture are not walls. The serving
    counter is a window, not a door. One storey; nobody lives here."""
    front = ((L.WX0, L.WY0), (L.WALL_C[0], L.WY0))
    rear = ((L.WX1, L.WY1), (L.WX0, L.WY1))
    doors = [model_facts.wall_door("kiosk", "entrance", *front, DOOR_X - L.WX0, 0.0,
                                   L.DOOR_LEAF_W, L.DOOR_LEAF_H, main=True),
             model_facts.wall_door("staff", "service", *rear, L.WX1 - STAFF_X, 0.0,
                                   L.STAFF_LEAF_W, L.STAFF_LEAF_H)]
    fp = footprint()
    area = 0.5 * abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(fp, fp[1:] + fp[:1])))
    return {"hero": False, "dwellings": 0, "footprint": fp,
            "storeys": [(0.0, round(area, 3))], "doors": doors}


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000), figure=True):
    """The six working views (shell_build.render_views()), plus one aerial
    from behind, one at eye level off the front and one at eye level off the
    serving corner, with 1.8 m figures 1 m in front of the customer door and
    at the serving corner's counter. Working views only."""
    return SB.render_views(BUILD, out_dir, level, res, views=(
        SB.AERIAL, SB.AERIAL_REAR,
        SB.orbit("eye_front", (-0.30, -1.0, 0.0), 3.2, z=1.6, aim_z=1.9),
        SB.orbit("eye_corner", (1.0, -0.8, 0.0), 2.6, lens=28.0, z=1.6, aim_z=1.9)),
        figures=[(DOOR_X, L.WY0 - 1.0), (2.75, -2.15)] if figure else ())


if __name__ == "__main__":
    BUILD.main(build_all, facts)
