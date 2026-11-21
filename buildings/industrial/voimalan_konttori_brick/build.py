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
of red facing brick on a cast concrete plinth, 14 x 9 m, under a flat roof
behind a low brick parapet with a galvanised coping, drained inside. A light
cast band marks the first floor right round the building. Upstairs one
continuous ribbon of white steel lights runs along each long side, brick only
at its ends, its head at the ceiling tight under the roof edge and a slim
transom across it; downstairs the control room's taller band fills the east
half of front and rear, and the offices have smaller windows in the same
language. The plant's main entrance is on the front, west of the middle: a
pair of glazed leaves and a transom light in a cast surround, under a slab
canopy cantilevered 2.125 m with a deep fascia and a concrete fin at its
west edge, up three steps with a handrail, the plant clock beside it. Staff
go out to the boiler house by a steel door on the rear, up three steps of
their own, a bulkhead lamp over it. On the deck a ventilation housing, the
control room's guyed radio mast and two vent pipes; a caged wall ladder at
the west end's rear corner serves the housing.

Construction is a set of closed solids unioned with Blender's exact boolean:
the wall ring, capped as one solid with the building's whole volume (its lid
the deck sunk inside the parapet), the coping ring, the canopy and its fin,
the two flights of steps, the clock and the lamp, the roof plant. The union
leaves the boundary of one empty volume, so interior geometry cannot occur.
The ladder, its cage and the handrails are roof_safety's lean kit, separate
solids appended after the weld that touch nothing.

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
XI, YI = HX - L.PIN, HY - L.PIN         # the parapet's inner faces: the deck

# Openings, per wall, as (kind, centre in plan x or y, sill z, lights). The
# window bands are n lights long (facade_atlas.BANDS); a door is one.
# Upstairs one ribbon of eight lights on each long side, x = -6 .. 6, brick
# only at its ends. Downstairs the control room's band of four lights fills
# the east half of front and rear, x = 0 .. 6; the offices' two-light window
# is in each long side's west bay, with the entrance (front) or the staff
# door (rear) east of it. On the 9 m ends one two-light window to a storey,
# the control room's at the east.
FL, S1, S2, SC = L.Z_FLOOR, L.Z_SILL, L.Z_SILL2, L.Z_SILL_CTRL
ENTRANCE_X = -2.625
SERVICE_X = -2.625
OFFICE_X = -5.3125                      # -6.25 .. -4.375
RIBBON = ("rib", 0.0, S2, 8)
FRONT_ITEMS = [("gwin", OFFICE_X, S1, 2), ("entrance", ENTRANCE_X, FL, 1),
               ("ctrl", 3.0, SC, 4), RIBBON]
REAR_ITEMS = [("ctrl", 3.0, SC, 4), ("service_door", SERVICE_X, FL, 1),
              ("gwin", OFFICE_X, S1, 2), RIBBON]
EAST_ITEMS = [("ctrl", 0.0, SC, 2), ("rib", 0.0, S2, 2)]
WEST_ITEMS = [("gwin", 0.0, S1, 2), ("rib", 0.0, S2, 2)]

# The canopy over the entrance: (centre x, width, projection), sunk into the
# wall CANOPY_BURY, cantilevered with no posts. Under its west edge, away
# from the control room's band, a cast concrete fin FIN_T thick stands from
# the ground into the slab, out FIN_D from the wall to the landing's edge,
# taking the steps' west cheek: a wing wall framing the entrance, the slab
# carried on past it. A fin the canopy's whole depth hid the offices'
# window beside it from the catalog view.
CANOPY = (ENTRANCE_X, 2.9, 2.125)
CANOPY_BURY = 0.1
FIN_T = 0.2
FIN_D = 1.2

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
    return HR.Flight(cx - w / 2.0, cx + w / 2.0, wall_y, outward, profile, lean=True)


HANDRAILS = [_flight(FRONT_STEPS, -HY, -1.0), _flight(REAR_STEPS, HY, 1.0)]

# On the deck: the ventilation housing over the stair, (centre x, y), its
# side and height facade_atlas's; the control room's radio mast, (x, y,
# height of its tube above the deck), a galvanised tube MAST_R in radius
# with a dipole across its head, a whip on top and two stays down to the
# deck; and two plain vent pipes, (x, y, diameter, height above the deck),
# which are not serviced items.
HOUSING = (-3.25, 1.75)
MAST = (3.0, 2.5, 2.5)
MAST_R = 0.05
WHIP = (0.75, 0.025)                    # length over the tube, and section
DIPOLE = (1.3, 0.03, 0.2)               # length, section, and depth under the top
STAY_Z = 1.6                            # where the stays meet the tube, over the deck
STAYS = [(-0.85, -0.85), (0.85, -0.85)]  # each stay's foot, from the mast's foot
STAY_W = 0.025
VENTS = [(-1.6, 2.3, 0.25, 0.85), (1.2, 2.6, 0.16, 0.60)]

# The plant clock on the entrance wall, between the entrance's surround and
# the control room's band: (centre x, centre z), a dial facade_atlas's CLOCK
# wide on a drum CLOCK_D proud of the brick. The staff door's bulkhead lamp
# over it on the rear: (width, height, depth) and the gap over the opening.
CLOCK_AT = (-0.8125, 2.5625)
CLOCK_R = L.CLOCK[2] / PPM / 2.0
CLOCK_D = 0.06
LAMP_SIZE = (L.LAMP[2] / PPM, L.LAMP[3] / PPM, 0.14)
LAMP_GAP = 0.1875

# The wall ladder up to the deck, which the housing is serviced from: at the
# back, and the rear wall's ribbon leaves it no run clear of openings, so on
# the blank west end next to its rear corner, LADDER_S along that wall from
# the corner. Over CAGE_LADDER long, so it carries a cage.
PAINT = RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)
LADDER_S = 1.2


# ----------------------------------------------------------------- tiers
def opening_mode(level):
    """LOD0/1 cut every opening into its wall with brick reveals; LOD2/3 paint
    the same rectangle flat. The 0.15-0.2 m reveals are under two pixels past
    70 m, and the window rhythm is the painted lights' to keep."""
    return "cut" if level < 2 else "flush"


def vent_sides(level, dia):
    """Eight sides up close, six to 70 m, four past it; past 120 m only the
    0.25 m exhaust stays, as a four-sided stub."""
    if level == 0:
        return 8
    if level == 1:
        return 6
    if level == 2:
        return 4
    return 4 if dia >= 0.2 else 0


def mast_sides(level):
    """The mast's tube sets the building's height, so it stays on every
    tier: eight sides up close, six to 70 m, four past it."""
    return (8, 6, 4, 4)[level]


def mast_parts(level):
    """(dipole, stays) per tier: the stays, 2.5 cm bars, to 70 m; the
    1.3 m dipole, which gives the mast its aerial's outline, to 120 m. The
    whip stays on every tier: it sets the height."""
    return (level < 3, level < 2)


def clock_sides(level):
    """The 0.625 m clock: twelve sides to 70 m, eight to 120 m, then gone
    (3 px)."""
    return (12, 12, 8, 0)[level]


def lamp_kept(level):
    """The staff door's 0.25 m lamp: LOD0 and LOD1."""
    return level < 2


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


def item_width(kind, n):
    """Width of an opening: a band of *n* lights, or a door."""
    if kind in L.BANDS:
        return L.BANDS[kind][0] * n
    return L.OPENINGS[kind][0]


def item_height(kind):
    return L.BANDS[kind][1] if kind in L.BANDS else L.OPENINGS[kind][1]


def item_rect(fr, kind, centre, z0, n=1):
    """(s0, s1, z0, z1) of an opening centred on plan coordinate *centre*."""
    w = item_width(kind, n)
    s = fr.s_at(centre)
    return (s - w / 2.0, s + w / 2.0, z0, z0 + item_height(kind))


def surround_rect(rect):
    """The entrance's cast surround round its opening *rect*."""
    s0, s1, z0, z1 = rect
    return (s0 - L.SURROUND, s1 + L.SURROUND, z0, z1 + L.SURROUND_TOP)


def build_opening(B, fr, kind, rect, level, u_off, n=1):
    """One opening: reveals round it and the closing plane set back in it
    while it is cut, the same rectangle painted flat after. Returns the
    outline in (s, z) the wall region takes as a hole.

    A window band's closing plane is split at every mullion into its lights,
    each mapped onto its own light's region (facade_atlas.light_kind), and
    the band's outline carries those split points along its sill and head,
    so the sill and head reveals and the wall around meet the lights on
    shared vertices.

    The entrance carries its cast surround: a U of concrete on the wall face
    round three sides of the opening, which is the hole the wall takes, and
    its reveals are concrete too. Its region holds the surround and the door
    together, so the flush tiers draw both as one quad.
    """
    s0, s1, z0, z1 = rect
    band = kind in L.BANDS
    if band:
        pitch = L.BANDS[kind][0]
        cuts = [s0 + k * pitch for k in range(n + 1)]
        lights = [(cuts[k], cuts[k + 1], uv_region(
            fr, L.REGION[L.light_kind(kind, k, n)], cuts[k], z0)) for k in range(n)]
        poly = [(s, z0) for s in cuts] + [(s, z1) for s in reversed(cuts)]
    else:
        dx, _dy = L.REGION_OFF.get(kind, (0, 0))
        lights = [(s0, s1, uv_region(fr, L.REGION[kind], s0 - dx / PPM, z0))]
        poly = [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]
    entrance = kind == "entrance"
    if entrance:
        S0, S1, _z0, Z1 = surround_rect(rect)
    if opening_mode(level) == "flush":
        if entrance:
            poly = [(S0, z0), (S1, z0), (S1, Z1), (S0, Z1)]
            B.face([fr.P(s, z) for s, z in poly], lights[0][2])
            return poly
        for a, b, fn in lights:
            B.face([fr.P(a, z0), fr.P(b, z0), fr.P(b, z1), fr.P(a, z1)], fn)
        return poly
    depth = L.REVEAL[kind]
    for (a0, b0), (a1, b1) in zip(poly, poly[1:] + poly[:1]):
        if abs(b0 - z0) < EPS and abs(b1 - z0) < EPS:
            fn = uv_patch("sill")
        elif entrance:
            fn = uv_patch("render")
        else:
            fn = uv_reveal(fr, ((a0, b0), (a1, b1)), u_off)
        B.face([fr.P(a0, b0), fr.P(a1, b1), fr.P(a1, b1, -depth),
                fr.P(a0, b0, -depth)], fn)
    for a, b, fn in lights:
        B.face([fr.P(a, z0, -depth), fr.P(b, z0, -depth), fr.P(b, z1, -depth),
                fr.P(a, z1, -depth)], fn)
    if not entrance:
        return poly
    ring = [(S0, z0), (s0, z0), (s0, z1), (s1, z1), (s1, z0), (S1, z0),
            (S1, Z1), (S0, Z1)]
    fill_region(B, fr, ring, [], lights[0][2])
    # the wall's hole: the surround's outline, with the opening's foot
    # corners on it, which the threshold shares
    return [(S0, z0), (s0, z0), (s1, z0), (S1, z0), (S1, Z1), (S0, Z1)]


def rects_for(fr, items):
    return [(kind, item_rect(fr, kind, c, z, n), n) for kind, c, z, n in items]


# ------------------------------------------------------------- the shell
MAIN_WALLS = {
    # name: (p0, p1), walked counter-clockwise from above
    "front": ((-HX, -HY), (HX, -HY)),
    "east": ((HX, -HY), (HX, HY)),
    "rear": ((HX, HY), (-HX, HY)),
    "west": ((-HX, HY), (-HX, -HY)),
}
ORDER = ("front", "east", "rear", "west")
# u offsets run on round the corners so the bond continues
U_OFF = {"front": 0.0, "east": 2 * HX, "rear": 2 * HX + 2 * HY,
         "west": 4 * HX + 2 * HY}
ITEMS = {"front": FRONT_ITEMS, "east": EAST_ITEMS, "rear": REAR_ITEMS,
         "west": WEST_ITEMS}


def build_wall(B, name, level):
    """One wall, ground to the parapet's top inside the coping, every
    opening in it built and holed."""
    fr = Frame(*MAIN_WALLS[name])
    uo = U_OFF[name]
    L_ = fr.L
    outline = [(0.0, 0.0), (L_, 0.0), (L_, L.Z_PAR), (0.0, L.Z_PAR)]
    holes = [build_opening(B, fr, kind, rect, level, uo, n)
             for kind, rect, n in rects_for(fr, ITEMS[name])]
    fill_region(B, fr, outline, holes, uv_brick(fr, uo))


def _ring(x, y):
    return [(-x, -y), (x, -y), (x, y), (-x, y)]


def _along(p, q, u0):
    """Metres along the edge p -> q from p, plus *u0*, for a vertex."""
    ln = math.hypot(q[0] - p[0], q[1] - p[1])
    tx, ty = (q[0] - p[0]) / ln, (q[1] - p[1]) / ln
    return lambda co: u0 + (co.x - p[0]) * tx + (co.y - p[1]) * ty


def main_body(level):
    """The wall ring capped as one solid: a floor on the ground, the
    parapet's top (inside the coping, which the union removes), the
    parapet's inner faces down to the deck, and the deck. The deck is the
    flat roof's felt, sunk Z_COP - Z_DECK below the coping."""
    B = Builder()
    for name in ORDER:
        build_wall(B, name, level)
    blank = uv_patch("blank")
    zp, zd = L.Z_PAR, L.Z_DECK
    outer, inner = _ring(HX, HY), _ring(XI, YI)
    run = 0.0
    for k in range(4):
        o0, o1 = outer[k], outer[(k + 1) % 4]
        i0, i1 = inner[k], inner[(k + 1) % 4]
        B.face([o0 + (zp,), o1 + (zp,), i1 + (zp,), i0 + (zp,)], blank)
        along = _along(i0, i1, run)
        B.face([i1 + (zd,), i0 + (zd,), i0 + (zp,), i1 + (zp,)],
               lambda co, along=along: (along(co) * PPM,
                                        L.UPST_Y0 + (co.z - zd) * PPM))
        run += math.hypot(i1[0] - i0[0], i1[1] - i0[1])
    dx, dy, _dw, _dh = L.DECK
    B.face([p + (zd,) for p in inner],
           lambda co: (dx + (co.x + XI) * L.DPPM, dy + (co.y + YI) * L.DPPM))
    B.face([(x, y, 0.0) for x, y in reversed(outer)], blank)
    return B


# ================================================================ coping
def coping():
    """The parapet's galvanised coping as one closed ring: COPING_H deep,
    oversailing both faces of the parapet by COPING_OUT, its faces and top
    on the coping band, its underside the drip patch."""
    B = Builder()
    co, z0, z1 = L.COPING_OUT, L.Z_COP0, L.Z_COP
    outer = _ring(HX + co, HY + co)
    inner = _ring(XI - co, YI - co)
    y_top = L.COP_Y0 + L.COP_FACE
    drip = uv_patch("drip")
    run = 0.0
    for k in range(4):
        o0, o1 = outer[k], outer[(k + 1) % 4]
        i0, i1 = inner[k], inner[(k + 1) % 4]
        along = _along(o0, o1, run)
        # inward normal of this edge, to measure the top across from o0-o1
        ln = math.hypot(o1[0] - o0[0], o1[1] - o0[1])
        nx, ny = -(o1[1] - o0[1]) / ln, (o1[0] - o0[0]) / ln

        def face_uv(c, along=along):
            return (along(c) * PPM, L.COP_Y0 + (c.z - z0) * PPM)

        def top_uv(c, along=along, o0=o0, nx=nx, ny=ny):
            return (along(c) * PPM,
                    y_top + ((c.x - o0[0]) * nx + (c.y - o0[1]) * ny) * PPM)
        B.face([o0 + (z0,), o1 + (z0,), o1 + (z1,), o0 + (z1,)], face_uv)
        B.face([i1 + (z0,), i0 + (z0,), i0 + (z1,), i1 + (z1,)], face_uv)
        B.face([o0 + (z1,), o1 + (z1,), i1 + (z1,), i0 + (z1,)], top_uv)
        B.face([i0 + (z0,), i1 + (z0,), o1 + (z0,), o0 + (z0,)], drip)
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
    """The canopy's fascia band, U along the edge, V from its underside."""
    return lambda co: ((co.x if axis == "x" else co.y) * PPM,
                       L.CANE_Y0 + (co.z - z0) * PPM)


def canopy():
    """The thin concrete canopy over the entrance, the first-floor slab
    carried out through the wall, edged with a painted sheet fascia: its
    edges the fascia band, its top the concrete region, its underside the
    soffit."""
    cx, w, proj = CANOPY
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y0, y1 = -HY - proj, -HY + CANOPY_BURY
    fx, fy = uv_cane("x", L.Z_CAN0), uv_cane("y", L.Z_CAN0)
    # the concrete region is 2.625 x 2.0 m: the 2.9 x 2.225 m top samples
    # it shrunk, which its board-float texture does not show
    top = uv_conc(lambda co: (co.x - x0) * 0.88, lambda co: (co.y - y0) * 0.88)
    return box(x0, x1, y0, y1, L.Z_CAN0, L.Z_CAN1, [fx, fy, uv_patch("blank"), fy],
               top, uv_patch("soffit"))


FIN_K = 2.0 / (L.Z_CAN0 + 0.05)       # the fin's 3.55 m on the 2.0 m region


def fin_span():
    """(x0, x1) of the fin: flush with the canopy's west edge."""
    cx, w, _proj = CANOPY
    return (cx - w / 2.0, cx - w / 2.0 + FIN_T)


def fin():
    """The cast concrete fin under the canopy's west edge: a wing wall from
    the ground up into the slab and from the front wall out to the slab's
    edge, its back sunk into the wall. Its faces sample the concrete region
    across its depth and up its height, the height squeezed onto the
    region's 2.0 m."""
    x0, x1 = fin_span()
    y0, y1 = -HY - FIN_D, -HY + CANOPY_BURY
    z1 = L.Z_CAN0 + 0.05
    out = lambda co: -HY - co.y                                # noqa: E731
    up = lambda co: co.z * FIN_K                               # noqa: E731
    side = uv_conc(lambda co: out(co) + 0.2, up)
    end = uv_conc(lambda co: co.x - x0 + 2.3, up)
    return box(x0, x1, y0, y1, 0.0, z1, [end, side, uv_patch("blank"), side],
               uv_patch("blank"), uv_patch("blank"))


def prism(px, py, r, z0, z1, sides, side_uv, top_uv, bottom_uv):
    """An upright round bar of *sides* sides, centre (px, py)."""
    B = Builder()
    ring = [(px + r * math.cos(a), py + r * math.sin(a))
            for a in [(i + 0.5) * 2.0 * math.pi / sides for i in range(sides)]]
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], side_uv)
    B.face([(x, y, z1) for x, y in ring], top_uv)
    B.face([(x, y, z0) for x, y in reversed(ring)], bottom_uv)
    return B




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


# -------------------------------------------------------------- roof plant
SUNK = 0.10                             # roof plant runs this far into the deck


def vent(px, py, dia, height, sides):
    """A vent pipe on the deck, its foot sunk into it. The open end is
    painted as a bore."""
    B = Builder()
    r = dia / 2.0
    base, z1 = L.Z_DECK - SUNK, L.Z_DECK + height
    ring = [(px + r * math.cos(a), py + r * math.sin(a))
            for a in [(i + 0.5) * 2.0 * math.pi / sides for i in range(sides)]]
    rx, ry, rw, rh = L.VENT
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        def fn(co, ax=ax, ay=ay, bx=bx, by=by):
            t = ((co.x - ax) * (bx - ax) + (co.y - ay) * (by - ay)) / \
                ((bx - ax) ** 2 + (by - ay) ** 2)
            return (rx + t * rw, ry + (co.z - L.Z_DECK) * PPM)
        B.face([(ax, ay, base), (bx, by, base), (bx, by, z1), (ax, ay, z1)], fn)
    tx, ty, tw, th = L.PIPE_TOP
    B.face([(x, y, z1) for x, y in ring],
           lambda co: (tx + tw * (0.5 + (co.x - px) / dia),
                       ty + th * (0.5 + (co.y - py) / dia)))
    B.face([(x, y, base) for x, y in reversed(ring)], uv_patch("blank"))
    return B


def housing():
    """The ventilation housing: a galvanised box on the deck, louvred on
    every side, a sheet lid."""
    hx, hy = HOUSING
    h = L.HOUSING_W / 2.0
    x0, x1, y0, y1 = hx - h, hx + h, hy - h, hy + h
    rx, ry, _rw, _rh = L.HOUSING
    z0 = L.Z_DECK

    def side(axis, start, sign):
        return lambda co: (rx + sign * ((co.x if axis == "x" else co.y) - start) * PPM,
                           ry + (co.z - z0) * PPM)
    sides = [side("x", x0, 1), side("y", y0, 1), side("x", x1, -1), side("y", y1, -1)]
    return box(x0, x1, y0, y1, z0 - SUNK, z0 + L.HOUSING_H, sides,
               uv_patch("housing_top"), uv_patch("blank"))


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
    ring = [side * h + up * h, -side * h + up * h, -side * h - up * h, side * h - up * h]
    B = Builder()
    r0, r1 = [tuple(a + q) for q in ring], [tuple(b + q) for q in ring]
    for k in range(4):
        B.face([r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k]], uv)
    B.face(list(reversed(r1)), uv)
    B.face(list(r0), uv)
    return B


def mast(level):
    """The control room's radio mast: a galvanised tube on the deck, a
    horizontal dipole across its head, a whip on top, and two stays down to
    the deck on its yard side."""
    mx, my, mh = MAST
    galv = uv_patch("galv")
    zt = L.Z_DECK + mh
    out = [prism(mx, my, MAST_R, L.Z_DECK - SUNK, zt, mast_sides(level), galv, galv,
                 uv_patch("blank"))]
    wl, ww = WHIP
    out.append(box(mx - ww / 2, mx + ww / 2, my - ww / 2, my + ww / 2, zt - 0.05,
                   zt + wl, galv, galv, galv))
    dipole, stays = mast_parts(level)
    if dipole:
        dl, dw, dd = DIPOLE
        out.append(box(mx - dl / 2, mx + dl / 2, my - MAST_R - dw, my - MAST_R + 0.02,
                       zt - dd - dw, zt - dd, galv, galv, galv))
    if stays:
        top = (mx, my, L.Z_DECK + STAY_Z)
        for dx, dy in STAYS:
            # from under the deck's surface to the tube's axis
            foot = Vector((mx + dx, my + dy, L.Z_DECK - SUNK))
            out.append(bar(tuple(foot), top, STAY_W, galv))
    return out


def clock(sides):
    """The plant clock: a drum on the front wall, its face the dial."""
    cx, cz = CLOCK_AT
    x, y, w, h = L.CLOCK
    B = Builder()
    y_face, y_back = -HY - CLOCK_D, -HY + 0.05
    ring = [(cx + CLOCK_R * math.cos(a), cz + CLOCK_R * math.sin(a))
            for a in [(i + 0.5) * 2.0 * math.pi / sides for i in range(sides)]]
    rim = uv_patch("post")
    for (ax, az), (bx, bz) in zip(ring, ring[1:] + ring[:1]):
        B.face([(ax, y_back, az), (bx, y_back, bz), (bx, y_face, bz),
                (ax, y_face, az)][::-1], rim)
    B.face([(px, y_face, pz) for px, pz in ring],
           lambda co: (x + w / 2.0 + (co.x - cx) * PPM, y + h / 2.0 + (co.z - cz) * PPM))
    B.face([(px, y_back, pz) for px, pz in reversed(ring)], uv_patch("blank"))
    return B


def lamp():
    """The staff door's bulkhead lamp, centred over the door: a cast box on
    the rear wall, its frosted glass to the front and underneath. Painted,
    not emissive."""
    lw, lh, ld = LAMP_SIZE
    z0 = L.Z_FLOOR + L.OPENINGS["service_door"][1] + LAMP_GAP
    x0, x1 = SERVICE_X - lw / 2.0, SERVICE_X + lw / 2.0
    lx, ly, _w, _h = L.LAMP
    front = lambda co: (lx + (x1 - co.x) * PPM, ly + (co.z - z0) * PPM)  # noqa: E731
    body = uv_patch("post")
    return box(x0, x1, HY - 0.05, HY + ld, z0, z0 + lh, [uv_patch("blank"), body, front, body],
               body, uv_patch("frosted"))


# ----------------------------------------------------------------- the kit
# The lean kit (scripts/roof_safety.py): the ladder, its cage and the two
# handrails as separate solids that touch nothing, appended after the weld
# on every tier rather than unioned. The plinth is painted flush with the
# brick, so nothing stands proud behind the ladder's brackets.
WEST = MAIN_WALLS["west"]
EAVE = RS.Eave(*WEST, L.Z_COP0, L.COPING_OUT, L.Z_COP, 0.0)
WALL_LADDER = RS.WallLadder(EAVE, LADDER_S, lean=True)
CAGE = RS.Cage(WALL_LADDER) if WALL_LADDER.length > RS.CAGE_LADDER else None
KIT = [WALL_LADDER] + ([CAGE] if CAGE else [])


def kit(level):
    """The ladder and its cage, roof_safety's MODES and CAGE_MODES
    unchanged, with extents: LOD3 keeps the bare rails and the cage's back
    strap, which set the plan's west extent; and the handrails, handrails'
    MODES unchanged."""
    return (RS.solids(KIT, level, PAINT, extents=True)
            + HR.solids(HANDRAILS, level, PAINT))


# ================================================================ assembly
def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    parts = [to_object(coping(), "tmp_coping"),
             to_object(canopy(), "tmp_canopy"),
             to_object(fin(), "tmp_fin"),
             to_object(steps(FRONT_STEPS, -HY, -1), "tmp_steps_front"),
             to_object(steps(REAR_STEPS, HY, +1), "tmp_steps_rear"),
             to_object(housing(), "tmp_housing")]
    for i, B in enumerate(mast(level)):
        parts.append(to_object(B, "tmp_mast%d" % i))
    if clock_sides(level):
        parts.append(to_object(clock(clock_sides(level)), "tmp_clock"))
    if lamp_kept(level):
        parts.append(to_object(lamp(), "tmp_lamp"))
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
    RS.append(obj, kit(level), check=True)
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
        for k, c, z, n in ITEMS[name]:
            r = item_rect(fr, k, c, z, n)
            if k == "entrance":
                r = surround_rect(r)
            rects.append(r)
            if r[0] < 0.4 or r[1] > fr.L - 0.4:
                bad.append("%s: %s at %.2f is within 0.4 m of a corner" % (name, k, c))
            # the roof slab and a lintel over every upper head
            if r[3] > L.Z_DECK - 0.4:
                bad.append("%s: %s at %.2f runs into the roof slab" % (name, k, c))
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
    # every band's lights 1.2-1.5 m apart on the long walls' ribbons
    for kind, (lw, lh) in L.BANDS.items():
        if kind != "gwin" and not 1.2 <= lw <= 1.5:
            bad.append("the %s band's mullions are not 1.2-1.5 m apart" % kind)
    # the ribbon's head at the upper rooms' ceiling, tight under the roof
    # edge, its sill at desk height; a transom keeps it horizontal
    if abs(L.Z_SILL2 + L.BANDS["rib"][1] - L.Z_HEAD2) > EPS:
        bad.append("the upper ribbon's head is not at Z_HEAD2")
    if not 2.6 <= L.Z_HEAD2 - L.Z_FLOOR2 <= 2.8:
        bad.append("the upper ribbon's head is not at a 2.6-2.8 m ceiling")
    if L.Z_COP0 - L.Z_HEAD2 > 0.75:
        bad.append("more than 0.75 m of brick over the upper ribbon")
    if not 0.4 <= L.TRANSOM2 <= 0.6 or L.TRANSOM2 > L.BANDS["rib"][1] / 3.0:
        bad.append("the ribbon's fixed upper light is not a slim 0.4-0.6 m")
    if L.BANDS["ctrl"][1] <= L.BANDS["gwin"][1]:
        bad.append("the control room's band is not taller than the offices' windows")
    # the human scale: door leaves, the transom, sills against both floors
    if not 2.0 <= L.Z_LEAF <= 2.4:
        bad.append("door leaf %.3f m is outside 2.0-2.4" % L.Z_LEAF)
    if L.ENTRY_H <= L.Z_LEAF + 0.15:
        bad.append("the entrance has no transom light above its leaves")
    if not 2.0 <= L.OPENINGS["service_door"][1] - 0.0625 <= 2.4:
        bad.append("the service door's leaf is outside 2.0-2.4")
    for z, floor, what in ((L.Z_SILL, L.Z_FLOOR, "ground office"),
                           (L.Z_SILL2, L.Z_FLOOR2, "upper ribbon"),
                           (L.Z_SILL_CTRL, L.Z_FLOOR, "control room")):
        if not 0.7 <= z - floor <= 1.05:
            bad.append("the %s sills are not at desk height" % what)
    if not 3.0 <= L.Z_FLOOR2 - L.Z_FLOOR <= 3.3:
        bad.append("the ground storey is outside 3.0-3.3 m")
    if not 3.0 <= L.Z_DECK - L.Z_FLOOR2 <= 3.3:
        bad.append("the upper storey is outside 3.0-3.3 m to the deck")
    # the parapet: 0.3-0.5 m over the deck, on every tier
    if not 0.3 <= L.Z_COP - L.Z_DECK <= 0.5:
        bad.append("the parapet is not 0.3-0.5 m over the deck")
    # the canopy: on the surround, wider than it, clear of the windows,
    # cantilevered 2.0-2.2 m, covering the landing
    if abs(L.Z_CAN0 - (L.Z_FLOOR + L.ENTRY_H + L.SURROUND_TOP)) > 0.0626:
        bad.append("the canopy does not sit on the entrance surround")
    cx, w, proj = CANOPY
    fr = Frame(*MAIN_WALLS["front"])
    srd = surround_rect(item_rect(fr, "entrance", ENTRANCE_X, L.Z_FLOOR))
    if w < srd[1] - srd[0] + 0.4:
        bad.append("the canopy is not wider than the entrance surround")
    if not 2.0 <= proj <= 2.2:
        bad.append("the cantilevered canopy is not 2.0-2.2 m out")
    for k, c, z, n in FRONT_ITEMS:
        if k != "entrance" and z < L.Z_FLOOR2:
            hw = item_width(k, n) / 2.0
            if c + hw > cx - w / 2.0 - 0.25 and c - hw < cx + w / 2.0 + 0.25:
                bad.append("the canopy runs within 0.25 m of the %s at %.2f" % (k, c))
    # the fin: under the canopy's west edge, away from the control room,
    # beside the steps (it takes their west cheek), as deep as the landing
    fx0, fx1 = fin_span()
    if fx1 > ENTRANCE_X - L.OPENINGS["entrance"][0] / 2.0 - L.SURROUND:
        bad.append("the fin runs into the entrance's surround")
    if fx0 > FRONT_STEPS[0] - FRONT_STEPS[1] / 2.0 or fx1 < FRONT_STEPS[0] - FRONT_STEPS[1] / 2.0:
        bad.append("the fin does not take the steps' west cheek")
    if not FRONT_STEPS[2][2][0] <= FIN_D < proj:
        bad.append("the fin does not reach the landing's edge or outruns the slab")
    # the clock: clear of the surround, the control band and the canopy
    cx, cz = CLOCK_AT
    clock_r = (cx - CLOCK_R, cx + CLOCK_R, cz - CLOCK_R, cz + CLOCK_R)
    for k, r in [(k, item_rect(fr, k, c, z, n)) for k, c, z, n in FRONT_ITEMS]:
        if k == "entrance":
            r = surround_rect(r)
        r = (r[0] - HX, r[1] - HX, r[2], r[3])
        if _overlap(clock_r, r, 0.3):
            bad.append("the clock is within 0.3 m of the %s" % k)
    if clock_r[3] > L.Z_CAN0 - 0.3:
        bad.append("the clock is within 0.3 m of the canopy's height")
    # the lamp: over the staff door, under the slab band
    z_lamp = L.Z_FLOOR + L.OPENINGS["service_door"][1] + LAMP_GAP + LAMP_SIZE[1]
    if z_lamp > L.Z_BAND0 - 0.2:
        bad.append("the staff door's lamp runs into the slab band")
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
    # the roof plant on the deck, clear of the parapet and of one another
    # (x, y, radius, item): the mast's stays' feet are part of the mast
    plant = [(HOUSING[0], HOUSING[1], L.HOUSING_W / 2.0, "housing"),
             (MAST[0], MAST[1], DIPOLE[0] / 2.0, "mast")]
    plant += [(MAST[0] + dx, MAST[1] + dy, 0.05, "mast") for dx, dy in STAYS]
    plant += [(px, py, dia / 2.0, "vent%d" % i) for i, (px, py, dia, h) in enumerate(VENTS)]
    for i, (px, py, r, what) in enumerate(plant):
        if abs(px) + r > XI - 0.4 or abs(py) + r > YI - 0.4:
            bad.append("roof plant at (%.1f, %.1f) crowds the parapet" % (px, py))
        for qx, qy, q, other in plant[i + 1:]:
            if other != what and abs(px - qx) < r + q + 0.3 and abs(py - qy) < r + q + 0.3:
                bad.append("roof plant at (%.1f, %.1f) crowds another" % (px, py))
        for ox, oy in L.OUTLETS:
            if abs(px - ox) < r + 0.4 and abs(py - oy) < r + 0.4:
                bad.append("roof plant at (%.1f, %.1f) stands on an outlet" % (px, py))
    # the wall ladder and its cage clear of the west end's corners and
    # windows; only a ladder this long has a cage
    fr = Frame(*WEST)
    avoid = []
    for k, c, z, n in WEST_ITEMS:
        r = item_rect(fr, k, c, z, n)
        avoid.append((k, r[0], r[1]))
    bad += RS.problems(WALL_LADDER, "the wall ladder", avoid)
    if CAGE:
        bad += RS.problems(CAGE, "the ladder's cage", avoid)
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
    coping's 6 cm oversail, the canopy and its fin, the clock, the lamp, the
    two flights of steps with their rails and the caged ladder stand outside
    it. Two
    storeys, at 0.5 and 3.75 m, each the whole plate inside the outer wall
    faces (the upper one under the flat roof, 3.25 m to the deck). The main
    door is the front entrance; the rear door is the staff's, a service
    door."""
    def door(door_id, kind, wall, item, main=False):
        p0, p1 = MAIN_WALLS[wall]
        (c, z), = [(c, z) for k, c, z, n in ITEMS[wall] if k == item]
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
