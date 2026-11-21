# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of voimalan_konttori_brick, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

The office and control building of a small town's coal-fired heat and power
plant (*voimalan konttori*: the power plant's office), 1950s-60s: two storeys
of red facing brick on a cast concrete plinth, 14 x 9 m, under a low hipped
roof of bitumen felt on battens with a 0.5 m eave all round. A light cast
band marks the first floor right round the building. The plant's main
entrance is on the front, west of the middle: a pair of glazed leaves and a
transom light in a cast surround, under a thin concrete canopy carried out
from the first-floor slab, up three steps with a handrail. East of it the
control room's three larger windows run on as a band, round the east corner
and along the rear; the offices upstairs have one regular row of white
framed windows on every side. Staff go out to the boiler house by a steel
door on the rear, up three steps of their own. A galvanised gutter is painted
round the whole eave with four modelled downpipes, and two plain vent pipes
stand on the rear slope.

Construction is a set of closed solids unioned with Blender's exact boolean:
the wall ring, capped as one solid with the building's whole volume (its lid
a hipped tent inside the roof slab), the hipped roof slab, the canopy, the
two flights of steps, their handrails, the downpipes and the vents. The
union trims the wall tops into the roof and the rest into the walls, and
leaves the boundary of one empty volume, so interior geometry cannot occur.

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
import model_facts  # noqa: E402
from asset_build import bounds as _bounds, to_object, union  # noqa: E402
import downpipes as DP  # noqa: E402
import handrails as HR  # noqa: E402
import roof_safety as RS  # noqa: E402

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
HX, HY = L.HX, L.HY                     # 7 x 4.5: a 14 x 9 m shell
XE = HX + L.EAVE_OUT                    # the roof's own extent
PE = HY + L.EAVE_OUT
RIDGE_X = HX - HY                       # the ridge runs x = -2.5 .. 2.5


def roof_under(x, y):
    """The hipped roof's underside over plan position (x, y): one pitch on
    every side, so its height is set by the nearest wall line."""
    return L.Z_EAVE + min(HY - abs(y), HX - abs(x)) * L.TAN


def roof_top(x, y):
    return roof_under(x, y) + L.ROOF_T


# Openings, per wall, as (kind, centre in plan x or y, sill z). One grid of
# 2.625 m bays on the long walls: upstairs a window in every bay; downstairs
# the office window and the entrance in the two west bays, the control
# room's windows in the three east bays, which on the rear become two and an
# office window, with the staff door in the entrance's bay. On the 9 m ends
# one window to a storey, the control room's at the east.
FL, S1, S2, SC = L.Z_FLOOR, L.Z_SILL, L.Z_SILL2, L.Z_SILL_CTRL
BAYS = (-5.25, -2.625, 0.0, 2.625, 5.25)
ENTRANCE_X = -2.625
SERVICE_X = -2.625
UPPER = [("win", x, S2) for x in BAYS]
FRONT_ITEMS = ([("win", -5.25, S1), ("entrance", ENTRANCE_X, FL)]
               + [("ctrl", x, SC) for x in (0.0, 2.625, 5.25)] + UPPER)
REAR_ITEMS = ([("ctrl", x, SC) for x in (5.25, 2.625)]
              + [("win", 0.0, S1), ("service_door", SERVICE_X, FL), ("win", -5.25, S1)]
              + UPPER[::-1])
EAST_ITEMS = [("ctrl", 0.0, SC), ("win", 0.0, S2)]
WEST_ITEMS = [("win", 0.0, S1), ("win", 0.0, S2)]

# The canopy over the entrance: (centre x, width, projection), sunk into the
# wall CANOPY_BURY.
CANOPY = (ENTRANCE_X, 2.6, 1.5)
CANOPY_BURY = 0.1

# Steps up to the doors, as (out from the wall, z) profiles extruded across
# the door: a landing 3 cm under the threshold, then two steps, so three
# risers of 0.156 m, and a handrail on each flight (scripts/handrails.py).
# The back of each is buried STEP_BURY in the wall under the door.
STEP_BURY = 0.05
Z_LAND = L.Z_FLOOR - 0.03125            # 0.46875
RISER = Z_LAND / 3.0


def _profile(land, tread):
    return [(-STEP_BURY, 0.0), (-STEP_BURY, Z_LAND), (land, Z_LAND),
            (land, 2 * RISER), (land + tread, 2 * RISER),
            (land + tread, RISER), (land + 2 * tread, RISER),
            (land + 2 * tread, 0.0)]


FRONT_STEPS = (ENTRANCE_X, 2.6, _profile(1.2, 0.3))
REAR_STEPS = (SERVICE_X, 1.8, _profile(1.0, 0.3))


def _flight(spec, wall_y, outward):
    cx, w, profile = spec
    return HR.Flight(cx - w / 2.0, cx + w / 2.0, wall_y, outward, profile)


HANDRAILS = [_flight(FRONT_STEPS, -HY, -1.0), _flight(REAR_STEPS, HY, 1.0)]

# Vent pipes on the rear slope, over the toilets and the stair: (x, y,
# diameter, height above the felt). Plain vents, not serviced items, so no
# roof safety kit.
VENTS = [(-1.6, 2.3, 0.25, 0.85), (1.2, 2.6, 0.16, 0.60)]


# ----------------------------------------------------------------- tiers
def opening_mode(level):
    """LOD0/1 cut every opening into its wall with brick reveals; LOD2/3 paint
    the same rectangle flat. The 0.15-0.2 m reveals are under two pixels past
    70 m, and the window rhythm is the painted rectangle's to keep."""
    return "cut" if level < 2 else "flush"


def vent_sides(level, dia):
    """Eight sides up close, six to 70 m, four past it; past 120 m only the
    0.25 m exhaust stays, as a four-sided stub over the ridge line."""
    if level == 0:
        return 8
    if level == 1:
        return 6
    if level == 2:
        return 4
    return 4 if dia >= 0.2 else 0


def downpipe_mode(level):
    """(sides, bent) of the downpipes at each tier: scripts/downpipes.py's
    MODES unchanged. Their galvanised line at each corner of the long walls
    is what tells the gutter is there."""
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

def uv_brick(fr, u_off):
    """The brick band, V the height from the ground."""
    return lambda co: ((fr.s_of(co) + u_off) * PPM, L.BRICK_Y0 + co.z * PPM)


def _patch_centre(name):
    x, y, w, h = L.PATCHES[name]
    return (x + w / 2.0, y + h / 2.0)


def uv_patch(name):
    c = _patch_centre(name)
    return lambda co: c


def uv_reveal(fr, edge, u_off):
    """The cheek of an opening, in the wall's own brick, unrolled round the
    corner so the coursing runs on into the cheek instead of restarting."""
    (s0, z0), (s1, z1) = edge
    ds, dz = s1 - s0, z1 - z0
    ln = math.hypot(ds, dz) or 1.0
    ns, nz = -dz / ln, ds / ln

    def f(co):
        d = -fr.out_of(co)
        return ((fr.s_of(co) + ns * d + u_off) * PPM,
                L.BRICK_Y0 + (co.z + nz * d) * PPM)
    return f


def uv_region(fr, rect, s0, z0, ppm=PPM):
    """A unique region, its lower-left corner at (s0, z0) on the wall."""
    x, y, w, h = rect
    return lambda co: (x + (fr.s_of(co) - s0) * ppm, y + (co.z - z0) * ppm)


def uv_conc(a_of, b_of):
    """The concrete region, planar: *a_of* and *b_of* give a vertex's metres
    across and up the region from its corner."""
    x, y, w, h = L.CONC
    return lambda co: (x + a_of(co) * PPM, y + b_of(co) * PPM)


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


def fill_planar(B, loops, to3d, uvfn):
    """Triangulate a planar region -- an outline and any holes, in 2D -- and
    add it, each 2D point placed by *to3d*."""
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((a, b, 0.0)) for a, b in loop] for loop in loops])
    for i, j, k in _flip_slivers(flat, tris):
        B.face([to3d(*flat[i]), to3d(*flat[j]), to3d(*flat[k])], uvfn)


def fill_region(B, fr, outline, holes, uvfn, out=0.0):
    fill_planar(B, [outline] + list(holes), lambda s, z: fr.P(s, z, out), uvfn)


def item_rect(fr, kind, centre, z0):
    """(s0, s1, z0, z1) of an opening centred on plan coordinate *centre*."""
    w, h = L.OPENINGS[kind]
    s = fr.s_at(centre)
    return (s - w / 2.0, s + w / 2.0, z0, z0 + h)


def surround_rect(rect):
    """The entrance's cast surround round its opening *rect*."""
    s0, s1, z0, z1 = rect
    return (s0 - L.SURROUND, s1 + L.SURROUND, z0, z1 + L.SURROUND_TOP)


def build_opening(B, fr, kind, rect, level, u_off):
    """One opening: reveals round it and the closing plane set back in it
    while it is cut, the same rectangle painted flat after. Returns the
    outline in (s, z) the wall region takes as a hole.

    The entrance carries its cast surround: a U of concrete on the wall face
    round three sides of the opening, which is the hole the wall takes, and
    its reveals are concrete too. Its region holds the surround and the door
    together, so the flush tiers draw both as one quad.
    """
    s0, s1, z0, z1 = rect
    poly = [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]
    dx, _dy = L.REGION_OFF.get(kind, (0, 0))
    rs0 = s0 - dx / PPM
    closing = uv_region(fr, L.REGION[kind], rs0, z0)
    entrance = kind == "entrance"
    if entrance:
        S0, S1, _z0, Z1 = surround_rect(rect)
    if opening_mode(level) == "flush":
        if entrance:
            poly = [(S0, z0), (S1, z0), (S1, Z1), (S0, Z1)]
        B.face([fr.P(s, z) for s, z in poly], closing)
        return poly
    depth = L.REVEAL[kind]
    for k, edge in enumerate(zip(poly, poly[1:] + poly[:1])):
        (a0, b0), (a1, b1) = edge
        if k == 0:
            fn = uv_patch("sill")
        elif entrance:
            fn = uv_patch("render")
        else:
            fn = uv_reveal(fr, edge, u_off)
        B.face([fr.P(a0, b0), fr.P(a1, b1), fr.P(a1, b1, -depth),
                fr.P(a0, b0, -depth)], fn)
    B.face([fr.P(s, z, -depth) for s, z in poly], closing)
    if not entrance:
        return poly
    ring = [(S0, z0), (s0, z0), (s0, z1), (s1, z1), (s1, z0), (S1, z0),
            (S1, Z1), (S0, Z1)]
    fill_region(B, fr, ring, [], closing)
    # the wall's hole: the surround's outline, with the opening's foot
    # corners on it, which the threshold shares
    return [(S0, z0), (s0, z0), (s1, z0), (S1, z0), (S1, Z1), (S0, Z1)]


def rects_for(fr, items):
    return [(kind, item_rect(fr, kind, c, z)) for kind, c, z in items]


# ------------------------------------------------------------- the shell
MAIN_WALLS = {
    # name: (p0, p1), walked counter-clockwise from above
    "front": ((-HX, -HY), (HX, -HY)),
    "east": ((HX, -HY), (HX, HY)),
    "rear": ((HX, HY), (-HX, HY)),
    "west": ((-HX, HY), (-HX, -HY)),
}
# u offsets run on round the corners so the bond continues
U_OFF = {"front": 0.0, "east": 2 * HX, "rear": 2 * HX + 2 * HY,
         "west": 4 * HX + 2 * HY}
ITEMS = {"front": FRONT_ITEMS, "east": EAST_ITEMS, "rear": REAR_ITEMS,
         "west": WEST_ITEMS}


def build_wall(B, name, level):
    """One wall, ground to its head inside the roof slab, every opening in
    it built and holed. The hip roof leaves all four walls level-headed."""
    fr = Frame(*MAIN_WALLS[name])
    uo = U_OFF[name]
    L_ = fr.L
    outline = [(0.0, 0.0), (L_, 0.0), (L_, L.Z_WALL_TOP), (0.0, L.Z_WALL_TOP)]
    holes = [build_opening(B, fr, kind, rect, level, uo)
             for kind, rect in rects_for(fr, ITEMS[name])]
    fill_region(B, fr, outline, holes, uv_brick(fr, uo))


def main_body(level):
    """The wall ring capped as one solid: a floor on the ground and a lid
    that is a hipped tent WALL_INTO_ROOF above the roof's underside, so both
    caps are buried (the floor in the ground plane, the lid in the slab) and
    the union removes them."""
    B = Builder()
    for name in ("front", "east", "rear", "west"):
        build_wall(B, name, level)
    blank = uv_patch("blank")
    zt = L.Z_WALL_TOP
    zr = zt + HY * L.TAN
    a, b, c, d = (-HX, -HY, zt), (HX, -HY, zt), (HX, HY, zt), (-HX, HY, zt)
    r0, r1 = (-RIDGE_X, 0.0, zr), (RIDGE_X, 0.0, zr)
    B.face([a, b, r1, r0], blank)
    B.face([b, c, r1], blank)
    B.face([c, d, r0, r1], blank)
    B.face([d, a, r0], blank)
    B.face([(-HX, -HY, 0.0), (-HX, HY, 0.0), (HX, HY, 0.0), (HX, -HY, 0.0)], blank)
    return B


# ================================================================== roof
def uv_slope(axis, sign):
    """A roof slope: U along its eave at 64 px/m, V up the slope from the
    eave edge, stretched to the band (the battens run down the slope)."""
    k = L.SLOPE_F * L.ROOF_RPM
    if axis == "y":         # front (sign -1) or rear (+1) slope
        return lambda co: ((sign * -co.x + XE) * PPM,
                           L.ROOF_Y0 + (PE - sign * co.y) * k)
    return lambda co: ((sign * co.y + PE) * PPM, L.ROOF_Y0 + (XE - sign * co.x) * k)


def uv_eave(z0, along):
    return lambda co: (along(co) * PPM, L.EAVE_Y0 + (co.z - z0) * PPM)


def hip_slab():
    """The roof as one closed slab: the hipped underside, the same surface
    ROOF_T higher as the felt, and the four vertical eave edges as fascias
    with the gutter. Its underside meets the walls' faces at Z_EAVE, so once
    it is unioned with the shell the part outside the walls is the soffit and
    the part inside disappears."""
    B = Builder()
    T = L.ROOF_T
    zu = L.Z_EAVE - L.EAVE_OUT * L.TAN
    zr = zu + PE * L.TAN
    corners = [(-XE, -PE), (XE, -PE), (XE, PE), (-XE, PE)]
    ridge = [(-RIDGE_X, 0.0), (RIDGE_X, 0.0)]

    def top(p, z):
        return (p[0], p[1], z + T)

    def bot(p, z):
        return (p[0], p[1], z)
    a, b, c, d = corners
    r0, r1 = ridge
    slopes = [([a, b], [r1, r0], uv_slope("y", -1)),
              ([b, c], [r1], uv_slope("x", 1)),
              ([c, d], [r0, r1], uv_slope("y", 1)),
              ([d, a], [r0], uv_slope("x", -1))]
    soffit = uv_patch("soffit")
    for eave, rid, fn in slopes:
        B.face([top(p, zu) for p in eave] + [top(p, zr) for p in rid], fn)
        B.face(list(reversed([bot(p, zu) for p in eave] + [bot(p, zr) for p in rid])),
               soffit)
    # fascias, U running on round the perimeter
    run = 0.0
    for k in range(4):
        p, q = corners[k], corners[(k + 1) % 4]
        ln = math.hypot(q[0] - p[0], q[1] - p[1])
        u0 = run

        def along(co, p=p, q=q, ln=ln, u0=u0):
            return u0 + ((co.x - p[0]) * (q[0] - p[0]) + (co.y - p[1]) * (q[1] - p[1])) / ln
        B.face([bot(p, zu), bot(q, zu), top(q, zu), top(p, zu)], uv_eave(zu, along))
        run += ln
    return B


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


def uv_cane(axis, z0):
    """The canopy's edge band, U along the edge, V from its underside."""
    return lambda co: ((co.x if axis == "x" else co.y) * PPM,
                       L.CANE_Y0 + (co.z - z0) * PPM)


def canopy():
    """The flat concrete canopy over the entrance, the first-floor slab
    carried out through the wall: its edges the cast-edge band, its top the
    concrete region, its underside the soffit."""
    cx, w, proj = CANOPY
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y0, y1 = -HY - proj, -HY + CANOPY_BURY
    fx, fy = uv_cane("x", L.Z_CAN0), uv_cane("y", L.Z_CAN0)
    top = uv_conc(lambda co: co.x - x0, lambda co: co.y - y0)
    return box(x0, x1, y0, y1, L.Z_CAN0, L.Z_CAN1, [fx, fy, uv_patch("blank"), fy],
               top, uv_patch("soffit"))


def steps(spec, wall_y, outward):
    """A flight of concrete steps on the long wall at *wall_y*: *spec* is
    (centre x, width, profile), the profile (distance out from the wall, z)
    extruded across the width. Treads, risers and cheeks all sample the
    concrete region in plan or elevation."""
    cx, w, profile = spec
    a0, a1 = cx - w / 2.0, cx + w / 2.0
    B = Builder()

    def W(a, d, z):
        return (a, wall_y + outward * d, z)

    def out(co):
        return (co.y - wall_y) * outward + STEP_BURY

    across = uv_conc(lambda co: co.x - a0, lambda co: co.z)
    tread = uv_conc(lambda co: co.x - a0, out)
    cheek = uv_conc(out, lambda co: co.z)
    n = len(profile)
    for k in range(n):
        (d0, z0), (d1, z1) = profile[k], profile[(k + 1) % n]
        flat = abs(z1 - z0) < EPS
        fn = (tread if z0 > EPS else uv_patch("blank")) if flat else across
        quad = [W(a0, d0, z0), W(a1, d0, z0), W(a1, d1, z1), W(a0, d1, z1)]
        B.face(quad if outward < 0 else quad[::-1], fn)
    side0 = [W(a0, d, z) for d, z in profile]
    side1 = [W(a1, d, z) for d, z in reversed(profile)]
    B.face(side0 if outward < 0 else side0[::-1], cheek)
    B.face(side1 if outward < 0 else side1[::-1], cheek)
    return B


# -------------------------------------------------------------------- vents
def vent(px, py, dia, height, sides):
    """A vent pipe on the roof: its foot is a slice of the roof plane inside
    the slab, so it is buried everywhere rather than only at its middle. The
    open end is painted as a bore."""
    B = Builder()
    r = dia / 2.0

    def foot(x, y):
        return roof_under(x, y) + 0.10

    z1 = roof_top(px, py) + height
    ring = [(px + r * math.cos(a), py + r * math.sin(a))
            for a in [(i + 0.5) * 2.0 * math.pi / sides for i in range(sides)]]
    base = min(foot(x, y) for x, y in ring)
    rx, ry, rw, rh = L.VENT
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        def fn(co, ax=ax, ay=ay, bx=bx, by=by):
            t = ((co.x - ax) * (bx - ax) + (co.y - ay) * (by - ay)) / \
                ((bx - ax) ** 2 + (by - ay) ** 2)
            return (rx + t * rw, ry + (co.z - base) * PPM)
        B.face([(ax, ay, foot(ax, ay)), (bx, by, foot(bx, by)), (bx, by, z1),
                (ax, ay, z1)], fn)
    tx, ty, tw, th = L.PIPE_TOP
    B.face([(x, y, z1) for x, y in ring],
           lambda co: (tx + tw * (0.5 + (co.x - px) / dia),
                       ty + th * (0.5 + (co.y - py) / dia)))
    B.face([(x, y, foot(x, y)) for x, y in reversed(ring)], uv_patch("blank"))
    return B


# ---------------------------------------------------------------- downpipes
# (wall, plan x along it). Two to each long wall, 0.25 m in from the
# corners, where the hip's gutters meet; the shape, the UVs and the placing
# rules are scripts/downpipes.py's.
DOWNPIPE_SPOTS = [("front", -6.75), ("front", 6.75), ("rear", 6.75), ("rear", -6.75)]


def _pipe(name, x):
    wall = MAIN_WALLS[name]
    s = Frame(*wall).s_at(x)
    return DP.eave_pipe(*wall, s, L.Z_EAVE, L.TAN, L.EAVE_OUT)


DOWNPIPES = [_pipe(*spot) for spot in DOWNPIPE_SPOTS]


def downpipes(level):
    return DP.solids(DOWNPIPES, *downpipe_mode(level), L.PIPE_STRIP, L.ATLAS)


# ================================================================ assembly
def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    parts = [to_object(hip_slab(), "tmp_roof"),
             to_object(canopy(), "tmp_canopy"),
             to_object(steps(FRONT_STEPS, -HY, -1), "tmp_steps_front"),
             to_object(steps(REAR_STEPS, HY, +1), "tmp_steps_rear")]
    for B, name in downpipes(level):
        parts.append(to_object(B, name))
    for B, name in HR.solids(HANDRAILS, level, RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)):
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
    # larger than a 0.1 mm weld can reach.
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # Recover the cost of coplanar boolean subdivisions. Keep UV and
        # material seams and every architectural edge.
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# ================================================================== checks
def _overlap(a, b, gap=0.0):
    return a[0] < b[1] + gap and b[0] < a[1] + gap and a[2] < b[3] + gap and b[2] < a[3] + gap


def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    for name, (p0, p1) in MAIN_WALLS.items():
        fr = Frame(p0, p1)
        rects = []
        for k, c, z in ITEMS[name]:
            r = item_rect(fr, k, c, z)
            if k == "entrance":
                r = surround_rect(r)
            rects.append(r)
            if r[0] < 0.4 or r[1] > fr.L - 0.4:
                bad.append("%s: %s at %.2f is within 0.4 m of a corner" % (name, k, c))
            if r[3] > L.Z_EAVE - 0.3:
                bad.append("%s: %s at %.2f runs too close to the wall head" % (name, k, c))
            if r[2] < L.Z_FLOOR - EPS:
                bad.append("%s: %s at %.2f is below the floor" % (name, k, c))
            # the slab band: ground-storey heads under it, upper sills over
            # it; the entrance's surround runs up into the canopy instead
            if k != "entrance" and r[2] < L.Z_BAND1 + 0.3 and r[3] > L.Z_BAND0 - 0.2:
                bad.append("%s: %s at %.2f runs into the slab band" % (name, k, c))
        for i, a in enumerate(rects):
            for b in rects[i + 1:]:
                if _overlap(a, b, 0.3):
                    bad.append("%s: two openings within 0.3 m of each other" % name)
    # the human scale: door leaves, the transom, sills against both
    if not 2.0 <= L.Z_LEAF <= 2.4:
        bad.append("door leaf %.3f m is outside 2.0-2.4" % L.Z_LEAF)
    if L.ENTRY_H <= L.Z_LEAF + 0.15:
        bad.append("the entrance has no transom light above its leaves")
    if not 2.0 <= L.OPENINGS["service_door"][1] - 0.0625 <= 2.4:
        bad.append("the service door's leaf is outside 2.0-2.4")
    for z, floor, what in ((L.Z_SILL, L.Z_FLOOR, "ground office"),
                           (L.Z_SILL2, L.Z_FLOOR2, "upper office"),
                           (L.Z_SILL_CTRL, L.Z_FLOOR, "control room")):
        if not 0.7 <= z - floor <= 1.05:
            bad.append("the %s sills are not at desk height" % what)
    if not 3.0 <= L.Z_FLOOR2 - L.Z_FLOOR <= 3.3:
        bad.append("the ground storey is outside 3.0-3.3 m")
    if not 3.0 <= L.Z_EAVE - L.Z_FLOOR2 <= 3.3:
        bad.append("the upper storey is outside 3.0-3.3 m to the eave")
    # the canopy: on the surround, wider than it, clear of the windows
    if abs(L.Z_CAN0 - (L.Z_FLOOR + L.ENTRY_H + L.SURROUND_TOP)) > 0.0626:
        bad.append("the canopy does not sit on the entrance surround")
    cx, w, proj = CANOPY
    fr = Frame(*MAIN_WALLS["front"])
    srd = surround_rect(item_rect(fr, "entrance", ENTRANCE_X, L.Z_FLOOR))
    if w < srd[1] - srd[0] + 0.4:
        bad.append("the canopy is not wider than the entrance surround")
    for k, c, z in FRONT_ITEMS:
        if k != "entrance" and z < L.Z_FLOOR2:
            hw = L.OPENINGS[k][0] / 2.0
            if c + hw > cx - w / 2.0 - 0.25 and c - hw < cx + w / 2.0 + 0.25:
                bad.append("the canopy runs within 0.25 m of the %s at %.2f" % (k, c))
    if proj < FRONT_STEPS[2][2][0] + 0.2:
        bad.append("the canopy does not cover the landing")
    # the steps: as wide as the surround, risers of a stair
    if FRONT_STEPS[1] < srd[1] - srd[0] + 0.3:
        bad.append("the entrance steps are narrower than the surround")
    if RISER > 0.18:
        bad.append("the steps' risers are over 0.18 m")
    # handrails clear of the doors and on their treads
    bad += HR.problems(HANDRAILS[0], "the front handrail", door_w=L.OPENINGS["entrance"][0],
                       door_c=ENTRANCE_X)
    bad += HR.problems(HANDRAILS[1], "the rear handrail",
                       door_w=L.OPENINGS["service_door"][0], door_c=SERVICE_X)
    # vents on the rear slope, clear of the ridge, the eave and the hips
    for px, py, dia, h in VENTS:
        if py < dia / 2.0 + 0.3 or py > HY - 1.0:
            bad.append("the vent at (%.1f, %.1f) is on the ridge or the eave" % (px, py))
        if HY - abs(py) > HX - abs(px) - 0.5:
            bad.append("the vent at (%.1f, %.1f) is on or near a hip" % (px, py))
    # downpipes clear of corners, openings, the canopy and the steps
    for (name, x), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        fr = Frame(*MAIN_WALLS[name])

        def span(what, a, b):
            return (what, min(fr.s_at(a), fr.s_at(b)), max(fr.s_at(a), fr.s_at(b)))
        avoid = [span(k, oc - L.OPENINGS[k][0] / 2.0, oc + L.OPENINGS[k][0] / 2.0)
                 for k, oc, z in ITEMS[name]]
        if name == "front":
            avoid.append(span("canopy", cx - w / 2.0, cx + w / 2.0))
            st = FRONT_STEPS
        else:
            st = REAR_STEPS
        avoid.append(span("steps", st[0] - st[1] / 2.0, st[0] + st[1] / 2.0))
        bad += DP.problems(pipe, "the %s downpipe at %.2f" % (name, x), avoid)
    return bad


# ================================================================== build
def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
# Clear leaf widths, as facade_atlas.py paints them: the entrance's pair of
# 0.75 m leaves inside a 4 px frame, the service door's one leaf likewise.
LEAF_W = {"entrance": (L.ENTRANCE[2] - 2 * L.REGION_OFF["entrance"][0] - 8) / PPM,
          "service_door": (L.SERVICE_DOOR[2] - 8) / PPM}


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the outer wall faces, 14 x 9 m; the
    eaves, the canopy, the two flights of steps with their rails and the
    downpipes stand outside it. Two storeys, at 0.5 and 3.75 m, each the
    whole plate inside the outer wall faces (the upper one under a flat
    ceiling, 3.125 m to the eave). The main door is the front entrance; the
    rear door is the staff's, a service door."""
    def door(door_id, kind, wall, item, main=False):
        p0, p1 = MAIN_WALLS[wall]
        (c, z), = [(c, z) for k, c, z in ITEMS[wall] if k == item]
        return model_facts.wall_door(door_id, kind, p0, p1, Frame(p0, p1).s_at(c), z,
                                     LEAF_W[item], L.Z_LEAF, main)

    area = 2 * HX * 2 * HY
    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-HX, -HY), (HX, -HY), (HX, HY), (-HX, HY)],
        "storeys": [(L.Z_FLOOR, area), (L.Z_FLOOR2, area)],
        "doors": [door("entrance", "entrance", "front", "entrance", main=True),
                  door("staff", "service", "rear", "service_door")],
    }


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four
    orthographic elevations, a plan from above, and a raised three-quarter
    aerial off the front corner; plus an aerial off the rear corner and eye
    views at the two doors. Working views only - not committed."""
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
    off = Vector(BUILD.pivot) if BUILD.pivot else Vector()
    persp = [("aerial", centre, Vector((1.0, -1.0, math.sqrt(2.0))), 3.0),
             ("aerial_rear", centre, Vector((-1.0, 1.0, math.sqrt(2.0))), 3.0),
             ("eye_entrance", Vector((ENTRANCE_X, -HY, 1.6)) - off,
              Vector((0.35, -1.0, 0.10)), 0.85),
             ("eye_service", Vector((SERVICE_X, HY, 1.6)) - off,
              Vector((-0.35, 1.0, 0.10)), 0.85),
             ("eye_front", Vector((0.0, -HY, 2.5)) - off, Vector((-0.6, -1.0, 0.05)), 1.8)]
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
