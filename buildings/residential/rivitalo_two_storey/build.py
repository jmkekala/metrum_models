# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of rivitalo_two_storey, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite Finnish rivitalo — the terraced row built through the 1960s-80s:
six two-storey dwellings side by side in one straight line under one
continuous shallow gable roof, vertical board cladding over a low concrete
plinth, and a walled private back yard per dwelling with a pedestrian gate set
off centre in its end wall. Each dwelling has one front door, with the type's
small stores shed built on beside it — a stained-board box projecting from the
front wall, its own door in its front — and one canopy over both.

Construction is a set of closed solids unioned with Blender's exact boolean:
the main body, the roof slab, one shed and one canopy per dwelling, the
entrance landings and yard-door steps, the ridge vent housings, and the yard
screen walls. Each solid
is simple to build on its own; the union is what trims the walls where the
soffits meet them and removes everything that ends up inside, so the result is
the boundary of one empty volume and interior geometry cannot occur.

The walls are textured as a trim sheet (see facade_atlas.py): cladding tiles,
and each window or door is a hole in the wall with its own faces mapped to the
region that carries its casing and glazing. Every number the two files share
is imported from facade_atlas.py rather than written here a second time.
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
import downpipes as DP  # noqa: E402
import roof_safety as RS  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT)
get_material, export_all = BUILD.material, BUILD.export_all
_show_only, preview_studio = BUILD.show_only, BUILD.preview_studio
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants
PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ------------------------------------------------------------------ massing
# Front (the entrance side) faces -Y. One straight row, one ridge along X.
UNITS = 6
UNIT_W = 6.0                     # a whole number of 0.5 m cladding boards
HX, HY = UNITS * UNIT_W / 2.0, 4.25
TAN = 0.20                       # 11.3 degrees: the type's shallow gable
ROOF_T = L.FASC_H / PPM          # slab's vertical thickness = fascia height
EAVE_OV = 0.40                   # eave overhang
RAKE_OV = 0.30                   # gable (rake) overhang
Z_APEX = L.Z_WALL_TOP + HY * TAN                 # body apex, inside the slab
Z_RIDGE = L.Z_EAVE + ROOF_T + HY * TAN           # top of the ridge

# The entrance shed: the stores box this type builds on beside each front
# door, clad in stained boarding with its own door. Real massing, kept at
# every tier — it is what gives the entrance side its rhythm of projections.
# It has no roof of its own; it runs up into the canopy, which covers both it
# and the door beside it.
SHED_W, SHED_OUT = L.SHED_FACE_W, 1.80
SHED_BURY = 0.10                 # into the front wall, for the union to trim
SHED_INTO = 0.03                 # into the canopy slab, so the two become one

# Entrance canopies: one shallow pent slab per dwelling, over the front door
# and the shed beside it. It oversails the shed's front and outer side as a
# small eave, and falls at the main roof's pitch, so it reads as a roof
# shedding water rather than a flat slab. Every tier keeps it.
CANOPY_EAVE = (0.25, 0.15)       # past the shed's front, past its outer side
CANOPY_OUT = SHED_OUT + CANOPY_EAVE[0]           # projection from the front wall
CANOPY_Z = (2.95, 2.95 - TAN * CANOPY_OUT)       # top at the wall, top at the edge
CANOPY_T = 0.14
CANOPY_FALL = (CANOPY_Z[0] - CANOPY_Z[1]) / CANOPY_OUT


def shed_top(d):
    """Height of the shed's roof *d* metres out from the front wall.

    The shed has no roof of its own: its top runs up into the canopy slab and
    stops SHED_INTO inside it, so the union leaves one volume and the canopy's
    soffit is what covers the store. A flat shed roof left a gap under the
    canopy that read as a mistake.
    """
    return CANOPY_Z[0] - CANOPY_T + SHED_INTO - CANOPY_FALL * d

# Landings and steps up to the 0.35 m plinth. Both sit inside a projection
# that every tier keeps — the shed in front, the screen walls behind — so
# dropping them at LOD3 cannot move the plan's extents.
FRONT_LANDING = [(-0.05, 0.0), (-0.05, 0.35), (0.50, 0.35), (0.50, 0.175),
                 (0.85, 0.175), (0.85, 0.0)]
REAR_STEP = [(-0.05, 0.0), (-0.05, 0.35), (0.40, 0.35), (0.40, 0.175),
             (0.70, 0.175), (0.70, 0.0)]

# Ridge vent housings, the sheet-metal boxes this type carries over its stacks.
# Each is open at the top, as every chimney is: a sheet-metal rim round one
# flue that drops FLUE_DEPTH to a soot floor. The top stands 0.95 m over the
# ridge, so the floor stays clear of the roof slab and nothing reaches into
# the flue.
VENT_X = (-2.0 * UNIT_W, 0.0, 2.0 * UNIT_W)
VENT = (0.45, 0.30, 0.50, 0.95)  # half x, half y, below the ridge, above it
FLUE_WALL = 0.10
FLUE_DEPTH = 0.80

# Back yards: one per dwelling, screened by rendered block walls. The
# dividing walls run back from the rear wall; the end wall closes each yard
# and carries the pedestrian gate, set off centre towards one side.
YARD_D = 4.50                    # yard depth behind the rear wall
YARD_T = 0.15                    # screen-wall thickness
YARD_Y = HY + YARD_D             # centreline of the end wall
YARD_START = HY - 0.10           # dividers start inside the rear wall
GATE_INSET = 1.60                # gate centre, measured from the +X end
GATE_Z = 0.08                    # the leaf hangs clear of the ground

# --------------------------------------------------------------- elevations
# Openings as (kind, s, sill z): s is the centre, measured along the wall from
# its start, and each wall runs counter-clockwise seen from above so its
# outward face is on the right. Per-dwelling layouts are given in local s
# across one UNIT_W bay and repeated along the row.
# Front: a large living-room window, then the dwelling's own front door with
# its stores shed built on beside it, and two large bedroom windows above,
# 3 m apart, the second over the shed. Every dwelling is laid out the same
# way, so the row reads as one door and one shed per house. Rear: the glazed
# yard door and a large window onto the private yard, with three windows
# above. The end walls of a terrace are blank.
#
# All three live in facade_atlas.py, because LOD3 paints them into its bay
# regions while the upper tiers cut them, and the two must not drift.
DOOR_S, SHED_S = L.DOOR_S, L.SHED_S
FRONT_UNIT, REAR_UNIT, END_WALL = L.FRONT_UNIT, L.REAR_UNIT, L.END_WALL


def row_items(layout, mirror_alternate):
    items = []
    for k in range(UNITS):
        base = k * UNIT_W
        flip = mirror_alternate and k % 2 == 1
        for kind, ls, z in layout:
            items.append((kind, base + (UNIT_W - ls if flip else ls), z))
    return items


MAIN_WALLS = {
    # front (-Y), s = x + HX
    "front": ((-HX, -HY), (HX, -HY), None, row_items(FRONT_UNIT, False)),
    # +X end wall, s = y + HY
    "east": ((HX, -HY), (HX, HY), Z_APEX, END_WALL),
    # rear (+Y), s = HX - x
    "rear": ((HX, HY), (-HX, HY), None, row_items(REAR_UNIT, False)),
    # -X end wall, s = HY - y
    "west": ((-HX, HY), (-HX, -HY), Z_APEX, END_WALL),
}
# The cladding band tiles every 0.5 m and its tone repeats every 16 m, so
# leaving every wall at offset zero lines the board joints up with the 6 m
# dwelling module and with each other where two walls meet at a corner.
U_OFF = {name: 0.0 for name in MAIN_WALLS}

# Downpipes (scripts/downpipes.py): three to each eave, each draining two
# dwellings' 12 m of gutter. On the front each stands just past a stores
# shed's canopy, on the rear just inside the next yard, beside its
# dividing wall.
DOWNPIPE_SPOTS = ([("front", UNIT_W + 0.15 + 2 * UNIT_W * k) for k in range(3)]
                  + [("rear", UNIT_W + 0.25 + 2 * UNIT_W * k) for k in range(3)])
DOWNPIPES = [DP.eave_pipe(*MAIN_WALLS[w][:2], s, L.Z_EAVE, TAN, EAVE_OV)
             for w, s in DOWNPIPE_SPOTS]

# Roof safety kit (scripts/roof_safety.py): the way up to the ridge vent
# housings. The rear wall has no run clear of openings from the ground to the
# eave, the front none either, and a terrace's end gables are blank, so the
# wall ladder stands on the west gable, next to its rear corner, and passes
# outside the rake; that is at the back, away from the front doors, and the
# side away from the catalog view. The roof ladder runs up the rear slope just
# inside the rake, and a level walkway along the slope just behind the ridge
# serves all three housings.
KIT_GABLE_S = 0.80                                # west gable, s = HY - y
KIT_ROOF_S = 2.0 * HX - 0.70                      # rear wall, s = HX - x


def _rake_z(s):
    """The west gable's rake at *s* along it: the soffit and the roof's top."""
    rise = min(s, 2.0 * HY - s) * TAN
    return L.Z_EAVE + rise, L.Z_EAVE + ROOF_T + rise


GABLE_WEST = RS.Eave(*MAIN_WALLS["west"][:2],
                     _rake_z(KIT_GABLE_S - RS.HALF)[0], RAKE_OV,
                     _rake_z(KIT_GABLE_S)[1], 0.0)
EAVE_REAR = RS.Eave(*MAIN_WALLS["rear"][:2], L.Z_EAVE, EAVE_OV,
                    L.Z_EAVE + ROOF_T - EAVE_OV * TAN, TAN)
WALK_OUT = -HY + VENT[1] + 0.08 + RS.WALK_W       # the walkway's downslope edge
ROOF_KIT = [
    RS.WallLadder(GABLE_WEST, KIT_GABLE_S, foot=0.03),
    RS.RoofLadder(EAVE_REAR, KIT_ROOF_S, EAVE_REAR.roof_z(WALK_OUT)),
    RS.Walkway(EAVE_REAR, HX - VENT_X[2] - VENT[0], KIT_ROOF_S + RS.HALF, WALK_OUT),
]


def kit_modes():
    """The kit's tiers: roof_safety.MODES but thinner, since the row has only
    about 500 triangles to spare at LOD1 and 70 at LOD2. LOD1 keeps every
    fourth rung and no brackets or posts, which are under a pixel past 35 m.
    From LOD2 the housings the walkway serves are gone, and the kit goes with
    them but for the wall ladder's bare rails, which stand outside the rake,
    the building's west extreme, so every tier keeps LOD0's bounds and pivot."""
    return ((1, True), (4, False), (None, False), (None, False))


def front_door_x():
    """X of each dwelling's front door. The front wall runs +X, so x = s - HX."""
    return [-HX + k * UNIT_W + DOOR_S for k in range(UNITS)]


def shed_x():
    """X of each dwelling's stores shed, centred."""
    return [-HX + k * UNIT_W + SHED_S for k in range(UNITS)]


def canopy_span(k):
    """The canopy over dwelling *k*: from outside the door's casing to the
    shed's far side, so one slab shelters both."""
    half = L.OPENINGS["door_front"][0] / 2.0 + L.OPENINGS["door_front"][2]
    return (-HX + k * UNIT_W + DOOR_S - half - 0.12,
            -HX + k * UNIT_W + SHED_S + SHED_W / 2.0 + CANOPY_EAVE[1])


def patio_door_x():
    """X of each yard door. The rear wall runs -X, so s = HX - x."""
    return [HX - (j * UNIT_W + REAR_UNIT[0][1]) for j in range(UNITS)]


def downpipe_mode(level):
    """(sides, bent) of the downpipes at each tier: scripts/downpipes.py's
    MODES, except that LOD3 drops them. It has 6 triangles to spare and the
    six straight pipes would cost about 70, so past 120 m, where a pipe is
    under a pixel, they go."""
    return DP.MODES[level] if level < 3 else (0, False)


def item_mode(kind, level):
    """How an opening is built at each tier.

    ring  - LOD0: the casing is a ring of faces on the wall, the opening inside
            it is recessed with reveals and closed by its glass or door plane.
    cut   - LOD1: one recess the size of the casing; the casing is painted on
            the recessed plane. Half the wall breakpoints for the same shadow.
    flush - LOD2/3: the casing rect as a flat quad in the wall.
    None  - dropped: the small windows and the yard gates below LOD2/LOD3.
    """
    if kind == "gate":
        # always flush: a gate leaf is a few centimetres proud of the render
        return "flush"
    if kind == "door_shed":
        # shallow by nature — a store door is nearly flush with its boarding.
        # At LOD3 the shed's front is a painted elevation, so nothing is cut.
        return ("cut", "cut", "flush", None)[level]
    if kind == "small":
        # Only the rear has small windows, and at LOD3 they are painted into
        # its bay region, so dropping the cut there costs nothing.
        return ("ring", "cut", "flush", None)[level]
    return ("ring", "cut", "flush", "flush")[level]


# ============================================================== mesh builder
class Builder:
    """One closed solid under construction, with UVs set as faces are made.

    Vertices are shared through a position cache, so faces that meet along an
    edge meet on the same vertices. That only works if every vertex lying on
    an edge is a corner of both faces — which is why region outlines carry
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
        # 32-bit floats, a zero-area face (a door's missing sill) keeps enough
        # rounding to pass as real and lands a third face on its edges.
        o = verts[0].co
        pts = [(v.co.x - o.x, v.co.y - o.y, v.co.z - o.z) for v in verts]
        nx = ny = nz = 0.0
        for i in range(len(pts)):
            (ax, ay, az), (bx, by, bz) = pts[i], pts[(i + 1) % len(pts)]
            nx += ay * bz - az * by
            ny += az * bx - ax * bz
            nz += ax * by - ay * bx
        if nx * nx + ny * ny + nz * nz < 1e-18:
            return None                       # zero area: a door's missing sill
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
    depth runs inward, away from the outward normal."""

    def __init__(self, p0, p1):
        self.p0 = Vector((p0[0], p0[1], 0.0))
        d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
        self.L = d.length
        self.t = d / self.L
        self.n = Vector((self.t.y, -self.t.x, 0.0))

    def P(self, s, z, depth=0.0):
        q = self.p0 + self.t * s - self.n * depth
        return (q.x, q.y, z)

    def s_of(self, co):
        return (co.x - self.p0.x) * self.t.x + (co.y - self.p0.y) * self.t.y


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.

def uv_band(fr, y0, z_ref, u_off):
    return lambda co: ((fr.s_of(co) + u_off) * PPM, y0 + (co.z - z_ref) * PPM)


def uv_item(fr, kind, s_left, z_bot):
    """Planar, at true scale. Recessed faces sit behind the wall only along
    its normal, so they sample the same texels as if they were flush."""
    x0, y0 = L.ITEM_ORIGIN[kind]
    return lambda co: (x0 + (fr.s_of(co) - s_left) * PPM, y0 + (co.z - z_bot) * PPM)


def uv_patch(name):
    x0, y0, w, h = L.PATCHES[name]
    c = (x0 + w / 2.0, y0 + h / 2.0)
    return lambda co: c


# ================================================================== walls
def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge.

    Openings on one wall share head and sill heights, so a region's holes
    line up and the triangulator is free to join three collinear corners into
    a triangle of no area. Dropping it leaves a hole in the wall; keeping it
    leaves a face with no normal. Flipping the long edge it shares with its
    neighbour turns the pair into two real triangles meeting at the middle
    vertex, which is the standard repair.
    """
    tris = [list(t) for t in tris]

    def area2(t):
        (ax, ay), (bx, by), (cx, cy) = (pts[i] for i in t)
        return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

    for _ in range(4 * len(tris)):
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


def fill_region(B, fr, outline, holes, uvfn, depth=0.0):
    """Triangulate a wall region with rectangular holes and add it."""
    loops = [outline] + holes
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((s, z, 0.0)) for s, z in loop] for loop in loops])
    for a, b, c in _flip_slivers(flat, tris):
        B.face([fr.P(*flat[a], depth), fr.P(*flat[b], depth),
                fr.P(*flat[c], depth)], uvfn)


def recess(B, fr, rect, depth, base, fn, rev):
    l, r, b, t = rect
    c = [(l, b), (r, b), (r, t), (l, t)]
    for k in range(4):
        (s0, z0), (s1, z1) = c[k], c[(k + 1) % 4]
        B.face([fr.P(s0, z0, base), fr.P(s1, z1, base),
                fr.P(s1, z1, base + depth), fr.P(s0, z0, base + depth)], rev)
    B.face([fr.P(s, z, base + depth) for s, z in c], fn)


def item_rects(kind, s, z):
    w, h, cs, cb, ct = L.OPENINGS[kind]
    outer = (s - w / 2 - cs, s + w / 2 + cs, z - cb, z + h + ct)
    inner = (s - w / 2, s + w / 2, z, z + h)
    return outer, inner


def build_item(B, fr, kind, s, z, level, base=0.0):
    """Faces for one opening; returns the hole it needs in its wall region."""
    mode = item_mode(kind, level)
    (ol, orr, ob, ot), (il, ir, ib, it) = item_rects(kind, s, z)
    fn = uv_item(fr, kind, ol, ob)
    depth = L.REVEAL_DEPTH.get(kind, L.REVEAL_DEFAULT)
    rev = uv_patch("reveal")
    o = [(ol, ob), (orr, ob), (orr, ot), (ol, ot)]
    if mode == "flush":
        B.face([fr.P(*p, base) for p in o], fn)
        return o
    if mode == "cut":
        recess(B, fr, (ol, orr, ob, ot), depth, base, fn, rev)
        return o
    i = [(il, ib), (ir, ib), (ir, it), (il, it)]
    for k in range(4):
        B.face([fr.P(*o[k], base), fr.P(*o[(k + 1) % 4], base),
                fr.P(*i[(k + 1) % 4], base), fr.P(*i[k], base)], fn)
    recess(B, fr, (il, ir, ib, it), depth, base, fn, rev)
    if abs(ob - ib) < EPS:
        # A door has no bottom casing, so the threshold edge lies on the hole's
        # own bottom edge; the hole has to carry those two corners too.
        return [(ol, ob), (il, ib), (ir, ib), (orr, ob), (orr, ot), (ol, ot)]
    return o


def build_wall(B, fr, top, apex, split, edge_z, items, u_off, level):
    """One elevation: cladding regions with a hole for every opening.

    *edge_z* is the set of heights every panel end of this solid carries, so
    two walls meeting at a corner meet on exactly the same vertices. *split*
    is the height where the cladding hands over from the ground-storey band
    S1 to the upper-storey band S2, which is the storey seam board.
    """
    Lw = fr.L

    def rake(s):
        return top if apex is None else top + min(s, Lw - s) * TAN

    def ez(s):
        return sorted({e for e in edge_z if e < top - EPS} | {rake(s)})

    s1band = uv_band(fr, L.S1_Y0, 0.0, u_off)
    s2band = uv_band(fr, L.S2_Y0, L.Z_STOREY, u_off)
    s0, s1 = 0.0, Lw

    rect = {}
    for kind, s, z in items:
        if item_mode(kind, level):
            rect[(kind, s, z)] = item_rects(kind, s, z)[0]

    def holes_between(z0, z1):
        return [(kind, s, z) for (kind, s, z), r in rect.items()
                if r[2] > z0 - EPS and r[3] < z1 + EPS]

    lower = ([(s0, 0.0), (s1, 0.0)]
             + [(s1, z) for z in ez(s1) if EPS < z < split - EPS]
             + [(s1, split), (s0, split)]
             + [(s0, z) for z in reversed(ez(s0)) if EPS < z < split - EPS])
    upper = ([(s0, split), (s1, split)]
             + [(s1, z) for z in ez(s1) if z > split + EPS]
             + ([(Lw / 2.0, apex)] if apex is not None else [])
             + [(s0, z) for z in reversed(ez(s0)) if z > split + EPS])
    regions = [(lower, s1band, holes_between(0.0, split)),
               (upper, s2band, holes_between(split, 99.0))]

    placed = 0
    for outline, fn, its in regions:
        holes = [build_item(B, fr, kind, s, z, level) for kind, s, z in its]
        placed += len(its)
        fill_region(B, fr, outline, holes, fn)
    if placed != len(rect):
        raise ValueError("an opening straddles the storey seam on a %.1f m wall"
                         % Lw)


def build_bay_wall(B, fr, top, edge_z, region, items):
    """LOD3's front or rear wall: one quad per dwelling bay, nothing cut.

    Every bay is identical, so all six sample the same painted region; the UV
    runs from each bay's own start, which makes the bay boundaries UV seams
    and lets six faces do the work of a wall with thirty holes in it. The two
    outermost bays carry the neighbouring end wall's breakpoints on their far
    edges, or the wall ring's rim would branch at the corner.
    """
    x0, y0, w, h = region
    lo = sorted(e for e in edge_z if EPS < e < top - EPS)
    for k in range(UNITS):
        a, b = k * UNIT_W, (k + 1) * UNIT_W
        pts = [(a, 0.0), (b, 0.0)]
        pts += [(b, z) for z in (lo if k == UNITS - 1 else [])]
        pts += [(b, top), (a, top)]
        pts += [(a, z) for z in reversed(lo if k == 0 else [])]

        def fn(co, a=a):
            return (x0 + (fr.s_of(co) - a) / L.BAY_W * w, y0 + co.z / L.BAY_H * h)

        B.face([fr.P(s, z) for s, z in pts], fn)


def close_solid(B, apexes):
    """Cap a wall ring: an n-gon floor, and a roof-shaped lid split at the
    ridge. Both end up buried — the floor on the ground, the lid inside the
    roof slab — but the solid must be closed for the boolean to be exact.

    The rim is walked and capped by hand rather than with bmesh's holes_fill,
    which silently skips a loop whose vertices already carry a face.
    """
    bm = B.bm
    bm.edges.index_update()
    # walked in edge-index order, never set order: a set of BMEdges iterates
    # by memory address, so the caps would start on a different vertex each
    # run and the boolean would triangulate differently every time
    order = [e for e in bm.edges if len(e.link_faces) == 1]
    rim = set(order)
    if any(sum(1 for e in v.link_edges if e in rim) != 2
           for e in order for v in e.verts):
        raise ValueError("the wall ring's rim branches: a T-junction somewhere")
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
        raise ValueError("expected a floor and a lid, got %d holes: the wall ring "
                         "has a T-junction somewhere" % len(loops))
    blank = uv_patch("blank")
    for loop in loops:
        B.set_uv(bm.faces.new(loop), blank)
    a, b = (B.cache[(round(p[0], 4), round(p[1], 4), round(p[2], 4))] for p in apexes)
    bmesh.ops.connect_verts(bm, verts=[a, b])


BAY_REGION = {"front": "LOD3_FRONT", "rear": "LOD3_REAR"}


def main_body(level):
    B = Builder()
    edge = sorted([0.0, L.Z_FLASH, L.Z_STOREY, L.Z_EAVE, L.Z_WALL_TOP])
    for name, (p0, p1, apex, items) in MAIN_WALLS.items():
        fr = Frame(p0, p1)
        if level >= 3 and name in BAY_REGION:
            build_bay_wall(B, fr, L.Z_WALL_TOP, edge,
                           getattr(L, BAY_REGION[name]), items)
        else:
            build_wall(B, fr, L.Z_WALL_TOP, apex, L.Z_STOREY, edge, items,
                       U_OFF[name], level)
    close_solid(B, [(HX, 0.0, Z_APEX), (-HX, 0.0, Z_APEX)])
    return B


# ================================================================== roofs
SLOPE_F = math.sqrt(1.0 + TAN * TAN)            # slope length per horizontal metre
ROOF_RPM = L.ROOF_H / L.ROOF_SLOPE_LEN           # atlas px per metre up a slope


def gable_slab(axis, c, half_w, z_eave, over, a0, a1):
    """A roof as one closed slab: a chevron section extruded along the ridge.

    The section's underside meets the wall face at *z_eave*, so once the slab
    is unioned with the walls the part outside them is the soffit and the part
    inside disappears. The vertical ends of the section are the fascias; the
    two chevron end caps are the barge boards over the gables.
    """
    B = Builder()
    pe = half_w + over
    z0 = z_eave + ROOF_T + half_w * TAN
    zt = z0 - pe * TAN
    sec = [(-pe, zt - ROOF_T), (-pe, zt), (0.0, z0), (pe, zt),
           (pe, zt - ROOF_T), (0.0, z0 - ROOF_T)]
    kinds = ("fascia", "slope", "slope", "fascia", "soffit", "soffit")

    def W(a, p, z):
        return (a, c + p, z) if axis == "x" else (c + p, a, z)

    def along(co):
        return co.x if axis == "x" else co.y

    def across(co):
        return (co.y if axis == "x" else co.x) - c

    def slope_uv(co):
        d = (pe - abs(across(co))) * SLOPE_F
        return ((along(co) + 16.0) * PPM, L.ROOF_Y0 + d * ROOF_RPM)

    def fascia_uv(co):
        return ((along(co) + 16.0) * PPM, L.FASC_Y0 + (co.z - (zt - ROOF_T)) * PPM)

    fns = {"fascia": fascia_uv, "slope": slope_uv, "soffit": uv_patch("soffit")}
    for k, kind in enumerate(kinds):
        (p0, z0_), (p1, z1_) = sec[k], sec[(k + 1) % 6]
        B.face([W(a0, p0, z0_), W(a0, p1, z1_), W(a1, p1, z1_), W(a1, p0, z0_)], fns[kind])
    barge = uv_patch("barge")
    B.face([W(a0, p, z) for p, z in sec], barge)
    B.face([W(a1, p, z) for p, z in reversed(sec)], barge)
    return B


def canopy(x0, x1):
    """An entrance canopy over one front door and its shed: a thin sloped slab
    with its back buried in the front wall."""
    B = Builder()
    zw, ze = CANOPY_Z
    fall = (zw - ze) / CANOPY_OUT
    back = -0.10                                   # into the wall
    sec = [(back, zw - fall * back), (CANOPY_OUT, ze), (CANOPY_OUT, ze - CANOPY_T),
           (back, zw - fall * back - CANOPY_T)]
    slope_len = math.hypot(CANOPY_OUT, zw - ze)

    def W(x, d, z):
        return (x, -HY - d, z)

    def top_uv(co):
        d = (CANOPY_OUT - (-HY - co.y)) * slope_len / CANOPY_OUT
        return ((co.x + 16.0) * PPM, L.ROOF_Y0 + d * ROOF_RPM)

    fns = (top_uv, uv_patch("barge"), uv_patch("soffit"), uv_patch("blank"))
    for k in range(4):
        (d0, z0), (d1, z1) = sec[k], sec[(k + 1) % 4]
        B.face([W(x1, d0, z0), W(x1, d1, z1), W(x0, d1, z1), W(x0, d0, z0)], fns[k])
    B.face([W(x1, d, z) for d, z in sec], uv_patch("barge"))
    B.face([W(x0, d, z) for d, z in reversed(sec)], uv_patch("barge"))
    return B


def shed(xc, level):
    """The stores shed beside a front door: a boarded box on the front wall.

    Its three exposed faces sample one strip in the atlas, mapped from each
    face's own along-coordinate and from world z, so the boards stand upright
    and the plinth line turns the corner. Its back is buried in the front
    wall, which the union removes.
    """
    B = Builder()
    x0, x1 = xc - SHED_W / 2.0, xc + SHED_W / 2.0
    yf, yb = -HY - SHED_OUT, -HY + SHED_BURY
    zf, zb = shed_top(SHED_OUT), shed_top(-SHED_BURY)
    rx, ry, rw, rh = L.SHED
    if rh / PPM < zb + 0.02:
        raise ValueError("the shed strip is shorter than the shed")

    def strip(along0, along_of):
        return lambda co: (rx + abs(along_of(co) - along0) * PPM, ry + co.z * PPM)

    front = Frame((x0, yf), (x1, yf))
    face = [(0.0, 0.0), (SHED_W, 0.0), (SHED_W, zf), (0.0, zf)]
    if item_mode("door_shed", level):
        fill_region(B, front, face,
                    [build_item(B, front, "door_shed", SHED_W / 2.0, L.Z_FLOOR,
                                level)],
                    strip(x0, lambda co: co.x))
    else:
        # LOD3: the door is painted into the shed's own elevation region, so
        # the front is one quad rather than a region with a hole in it
        bx, by, bw, bh = L.LOD3_SHED
        B.face([front.P(s, z) for s, z in face],
               lambda co: (bx + front.s_of(co) / SHED_W * bw,
                           by + co.z / (bh / L.PPM3) * bh))
    side = strip(yf, lambda co: co.y)
    B.face([(x1, yf, 0.0), (x1, yb, 0.0), (x1, yb, zb), (x1, yf, zf)], side)
    B.face([(x0, yb, 0.0), (x0, yf, 0.0), (x0, yf, zf), (x0, yb, zb)], side)
    B.face([(x1, yb, 0.0), (x0, yb, 0.0), (x0, yb, zb), (x1, yb, zb)],
           uv_patch("blank"))
    # the top is buried in the canopy, so it never shows; the canopy's own
    # soffit is what a viewer sees over the store door
    B.face([(x0, yf, zf), (x1, yf, zf), (x1, yb, zb), (x0, yb, zb)],
           uv_patch("blank"))
    B.face([(x1, yf, 0.0), (x1, yb, 0.0), (x0, yb, 0.0), (x0, yf, 0.0)],
           uv_patch("blank"))
    return B


def steps(a0, a1, wall, outward, profile, axis="y"):
    """A flight of steps: *profile* is (distance out from the wall, z),
    extruded across a0..a1. Its back is buried in the wall it serves."""
    B = Builder()

    def W(a, d, z):
        return (a, wall + outward * d, z) if axis == "y" else (wall + outward * d, a, z)

    def across(co):
        return co.x if axis == "y" else co.y

    def out(co):
        return ((co.y if axis == "y" else co.x) - wall) * outward

    # risers and cheeks read the plinth's concrete in S1: risers along the
    # flight's width, cheeks along its run
    def riser_uv(co):
        return ((across(co) + 11.0) * PPM, L.S1_Y0 + co.z * PPM)

    def cheek_uv(co):
        return ((out(co) + 11.0) * PPM, L.S1_Y0 + co.z * PPM)

    n = len(profile)
    for k in range(n):
        (d0, z0), (d1, z1) = profile[k], profile[(k + 1) % n]
        flat = abs(z1 - z0) < EPS
        fn = uv_patch("tread") if flat and z0 > EPS else (
            uv_patch("blank") if flat else riser_uv)
        B.face([W(a0, d0, z0), W(a1, d0, z0), W(a1, d1, z1), W(a0, d1, z1)], fn)
    B.face([W(a0, d, z) for d, z in profile], cheek_uv)
    B.face([W(a1, d, z) for d, z in reversed(profile)], cheek_uv)
    return B


def screen_wall(p0, p1, gates, level):
    """A back-yard screen wall: one closed rendered slab, centred on p0..p1.

    The outer face samples the tiling YARD band and carries each gate as a
    flush quad in its own atlas region — a gate leaf stands a few centimetres
    proud of the render, far below the 0.25 m relief test, so it is painted.
    """
    B = Builder()
    fr = Frame(p0, p1)
    Lw, h, do, di = fr.L, L.YARD_H, -YARD_T / 2.0, YARD_T / 2.0
    band = uv_band(fr, L.YARD_Y0, 0.0, 0.0)
    holes = [build_item(B, fr, "gate", s, GATE_Z, level, do)
             for s in gates if item_mode("gate", level)]
    fill_region(B, fr, [(0.0, 0.0), (Lw, 0.0), (Lw, h), (0.0, h)], holes, band, do)
    B.face([fr.P(s, z, di) for s, z in ((Lw, 0.0), (0.0, 0.0), (0.0, h), (Lw, h))],
           band)
    render = uv_patch("render")
    B.face([fr.P(0.0, 0.0, do), fr.P(0.0, 0.0, di), fr.P(0.0, h, di),
            fr.P(0.0, h, do)], render)
    B.face([fr.P(Lw, 0.0, di), fr.P(Lw, 0.0, do), fr.P(Lw, h, do),
            fr.P(Lw, h, di)], render)
    B.face([fr.P(0.0, h, do), fr.P(0.0, h, di), fr.P(Lw, h, di), fr.P(Lw, h, do)],
           uv_patch("cap"))
    B.face([fr.P(0.0, 0.0, di), fr.P(0.0, 0.0, do), fr.P(Lw, 0.0, do),
            fr.P(Lw, 0.0, di)], uv_patch("blank"))
    return B


def yard_walls(level):
    """The dividing walls between yards, and each yard's gated end wall.

    Every divider runs into the rear wall, and the boolean has to subdivide
    that wall around each one. That is what made these expensive at LOD3 while
    the rear wall was still cut for its windows; with that wall painted
    instead, all six yards stay separate at every tier.
    """
    out = []
    for i in range(UNITS + 1):
        x = -HX + i * UNIT_W
        out.append((screen_wall((x, YARD_START), (x, YARD_Y + YARD_T / 2.0), [],
                                level), "tmp_yard_div%d" % i))
    if level >= 3:
        # The six end walls are collinear and abut, so one span is the same
        # wall; only the gates are lost, and a 1 m gate is about 9 px at this
        # tier's distance. The dividing walls all stay, which is what makes
        # six private yards read as six rather than one.
        out.append((screen_wall((HX + YARD_T / 2.0, YARD_Y),
                                (-HX - YARD_T / 2.0, YARD_Y), [], level),
                    "tmp_yard_end"))
        return out
    for k in range(UNITS):
        xl, xr = -HX + k * UNIT_W, -HX + (k + 1) * UNIT_W
        # runs -X so its outward normal faces +Y, away from the dwelling
        out.append((screen_wall((xr + YARD_T / 2.0, YARD_Y),
                                (xl - YARD_T / 2.0, YARD_Y), [GATE_INSET], level),
                    "tmp_yard_end%d" % k))
    return out


# ================================================================ assembly


def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    parts = [to_object(gable_slab("x", 0.0, HY, L.Z_EAVE, EAVE_OV,
                                  -HX - RAKE_OV, HX + RAKE_OV), "tmp_roof")]
    if level < 2:
        for i, vx in enumerate(VENT_X):
            hx_, hy_, below, above = VENT
            parts.append(to_object(asset_build.open_stack(
                Builder(), vx - hx_, vx + hx_, -hy_, hy_, Z_RIDGE - below,
                Z_RIDGE + above, FLUE_WALL, FLUE_DEPTH, uv_patch("cap"),
                uv_patch("cap"), uv_patch("flue"), uv_patch("blank")),
                "tmp_vent%d" % i))
    for i, xc in enumerate(shed_x()):
        parts.append(to_object(shed(xc, level), "tmp_shed%d" % i))
    for k in range(UNITS):
        parts.append(to_object(canopy(*canopy_span(k)), "tmp_canopy%d" % k))
    if level < 3:
        # A 0.35 m landing is a couple of pixels at LOD3's distance, and it
        # sits inside the shed's projection, so dropping it there cannot move
        # the plan's front edge.
        for i, xc in enumerate(front_door_x()):
            parts.append(to_object(steps(xc - 0.85, xc + 0.85, -HY, -1.0,
                                         FRONT_LANDING), "tmp_steps_f%d" % i))
    rear_prof = REAR_STEP
    if level < 3:
        # A 0.7 m step slab inside a walled yard is sub-pixel at LOD3's
        # distance and never breaks the plan's extents, so it goes there.
        for i, xc in enumerate(patio_door_x()):
            parts.append(to_object(steps(xc - 0.85, xc + 0.85, HY, 1.0, rear_prof),
                                   "tmp_steps_r%d" % i))
    kit = RS.solids(ROOF_KIT, level, RS.Paint(L.ATLAS, strip=L.PIPE_STRIP),
                    extents=True, modes=kit_modes())
    bare = kit_modes()[level][0] is None             # the rails alone, clear of all
    for B, name in yard_walls(level) + DP.solids(
            DOWNPIPES, *downpipe_mode(level), L.PIPE_STRIP, L.ATLAS) + (
            [] if bare else kit):
        parts.append(to_object(B, name))
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # 1e-4 rather than the 1e-5 the earlier houses weld at. The exact boolean
    # resolves this row's 24 m eave lines in 32-bit floats, and it leaves the
    # odd corner vertex a hundredth of a millimetre off its neighbour: enough
    # to export as two vertices and read as a non-manifold seam downstream.
    # The smallest authored feature here is the gate's 0.06 m casing, so a
    # 0.1 mm weld cannot reach anything real.
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # Recover the cost of coplanar boolean subdivisions. Keep UV and
        # material seams and every architectural edge. 0.001 radians
        # tolerates float noise on nominally planar faces.
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    if bare:
        # after the weld and the dissolve, whose greedy passes the extra faces
        # would otherwise reorder: they took eight more triangles
        RS.append(obj, kit)
    return obj


def check_layout():
    """Assert the constraints that are invisible in the numbers and obvious
    once rendered: openings colliding, clipping the rake or the wall ends, or
    straddling the storey seam; the gable outgrowing its atlas band; the
    canopies missing the door pairs they cover."""
    problems = []
    if Z_APEX > L.S2_TOP:
        problems.append("gable apex %.2f is above the S2 band's %.2f" % (Z_APEX, L.S2_TOP))
    if L.Z_STOREY + (L.S1_TOP - L.Z_STOREY) < L.Z_STOREY:
        problems.append("S1 band does not reach the storey seam")
    if L.S1_TOP < L.Z_STOREY:
        problems.append("S1 band stops below the storey seam at %.2f" % L.Z_STOREY)
    slope = (HY + EAVE_OV) * SLOPE_F
    if abs(slope - L.ROOF_SLOPE_LEN) > 1e-3:
        problems.append("main slope is %.3f m, atlas assumes %.3f" % (slope, L.ROOF_SLOPE_LEN))
    gate_top = item_rects("gate", 0.0, GATE_Z)[0][3]
    if YARD_D <= 0.0 or L.YARD_H <= gate_top + 0.05:
        problems.append("the yard's screen wall is not taller than its gate")
    if GATE_Z <= 0.02:
        problems.append("the yard gate's foot is coincident with the wall's")
    gap = 0.05
    for name, (p0, p1, apex, items) in MAIN_WALLS.items():
        fr = Frame(p0, p1)
        rects = [(k, item_rects(k, s, z)[0]) for k, s, z in items]
        for k, (l, r, b, t) in rects:
            if l < gap or r > fr.L - gap:
                problems.append("%s: %s at s %.2f..%.2f runs off the wall" % (name, k, l, r))
            eave = L.Z_EAVE            # visible top, under the soffit
            for s in (l, r):
                vis = eave + (min(s, fr.L - s) * TAN if apex is not None else 0.0)
                if t > vis - gap:
                    problems.append("%s: %s top %.2f is under the roof (%.2f)"
                                    % (name, k, t, vis))
            if b < L.Z_STOREY < t:
                problems.append("%s: %s straddles the storey seam" % (name, k))
            if b < L.Z_FLASH < t and not k.startswith("door"):
                problems.append("%s: %s straddles the plinth top" % (name, k))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b_ = rects[i][1], rects[j][1]
                if a[0] < b_[1] + gap and b_[0] < a[1] + gap and \
                        a[2] < b_[3] + gap and b_[2] < a[3] + gap:
                    problems.append("%s: %s at %.2f and %s at %.2f overlap"
                                    % (name, rects[i][0], a[0], rects[j][0], b_[0]))
    front = MAIN_WALLS["front"][3]
    doors = sorted(item_rects(k, s, z)[0] for k, s, z in front if k == "door_front")
    if len(doors) != UNITS:
        problems.append("%d front doors for %d dwellings" % (len(doors), UNITS))
    for k in range(UNITS):
        c0, c1 = canopy_span(k)
        dl, dr = doors[k][0] - HX, doors[k][1] - HX      # front wall: s = x + HX
        sl, sr = shed_x()[k] - SHED_W / 2.0, shed_x()[k] + SHED_W / 2.0
        if not (c0 <= dl and dr <= c1 and c0 <= sl and sr <= c1):
            problems.append("canopy %d does not cover its door and shed" % k)
        if dr > sl - 0.02:
            problems.append("dwelling %d's shed runs into its door casing" % k)
        if sr > -HX + (k + 1) * UNIT_W + 0.01:
            problems.append("dwelling %d's shed crosses into the next bay" % k)
        if CANOPY_Z[0] - CANOPY_T < doors[k][3] + 0.10:
            problems.append("canopy %d meets the wall on the door casing" % k)
    landing = max(d for d, _ in FRONT_LANDING)
    if CANOPY_Z[0] - CANOPY_FALL * landing - CANOPY_T - L.Z_FLOOR < 2.2:
        problems.append("canopy is below head height over the landing")
    if CANOPY_Z[1] - CANOPY_T < 2.2:
        problems.append("canopy edge is below head height over the ground")
    if SHED_INTO <= 0.0 or SHED_INTO >= CANOPY_T - 0.02:
        problems.append("the shed does not meet the canopy as one volume")
    if max(d for d, _ in FRONT_LANDING) > SHED_OUT - 0.02:
        problems.append("the entrance landing reaches past the shed, so "
                        "dropping it at LOD3 would move the plan's front edge")
    if min(CANOPY_EAVE) <= 0.0:
        problems.append("the canopy does not oversail its shed as an eave")
    if item_rects("door_shed", 0.0, L.Z_FLOOR)[0][3] > shed_top(SHED_OUT) - 0.05:
        problems.append("the shed door runs into the canopy over it")
    gw = L.OPENINGS["gate"][0] / 2.0 + L.OPENINGS["gate"][2]
    if not (gap < GATE_INSET - gw and GATE_INSET + gw < UNIT_W + YARD_T - gap):
        problems.append("the yard gate runs into a dividing wall")
    if abs(GATE_INSET - (UNIT_W + YARD_T) / 2.0) < 0.5:
        problems.append("the yard gate is too near the middle of the end wall")
    # downpipes clear of the corners and the openings; of the sheds, canopies
    # and landings on the front; of the yard walls and steps on the rear
    near = DP.A + 0.1
    for (w, s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        avoid = [(k,) + item_rects(k, c, z)[0][:2] for k, c, z in MAIN_WALLS[w][3]]
        if w == "front":                                    # s = x + HX
            avoid += [("canopy", a + HX, b + HX)
                      for a, b in (canopy_span(k) for k in range(UNITS))]
            avoid += [("shed", x + HX - SHED_W / 2.0, x + HX + SHED_W / 2.0)
                      for x in shed_x()]
            avoid += [("landing", x + HX - 0.85, x + HX + 0.85, near)
                      for x in front_door_x()]
        else:                                               # s = HX - x
            avoid += [("yard wall", i * UNIT_W - YARD_T / 2.0,
                       i * UNIT_W + YARD_T / 2.0, near) for i in range(UNITS + 1)]
            avoid += [("yard step", HX - x - 0.85, HX - x + 0.85, near)
                      for x in patio_door_x()]
        problems += DP.problems(pipe, "the %s downpipe at s %.2f" % (w, s), avoid)
    # the roof kit: the wall ladder on the blank gable clear of its corners
    # and under the rake; the roof ladder inside the rake; the walkway just
    # behind the housings and running past the last one
    wall, roof, walk = ROOF_KIT
    problems += RS.problems(wall, "the gable ladder", [])
    if roof.s + RS.HALF > 2.0 * HX - 0.20:
        problems.append("the roof ladder is not inside the west rake")
    if any(abs(HX - roof.s - vx) < VENT[0] + RS.HALF + 0.3 for vx in VENT_X):
        problems.append("the roof ladder runs into a vent housing")
    y_hi = HY + walk.out_hi                          # its upslope edge, in y
    if not VENT[1] + 0.02 < y_hi < VENT[1] + 0.30:
        problems.append("the walkway's edge is not just behind the housings")
    if walk.s0 > HX - VENT_X[2] - VENT[0]:
        problems.append("the walkway stops short of the east housing")
    if VENT[3] - FLUE_DEPTH < 0.05:
        problems.append("a housing's flue floor is down in the roof slab")
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# ================================================================ previews


def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four
    orthographic elevations, a plan from above, and a raised three-quarter
    aerial off the front corner. Working views only — not committed."""
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
    # raised three-quarter: 45 degrees up, off the front-right corner
    cam.data.type = 'PERSP'
    cam.data.lens = 35.0
    d = Vector((1.0, -1.0, math.sqrt(2.0))).normalized()
    cam.location = centre + d * radius * 3.0
    cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scn.render.filepath = os.path.join(out_dir, "L%d_aerial.png" % level)
    bpy.ops.render.render(write_still=True)
    written.append(scn.render.filepath)
    scn.camera, scn.render.resolution_x, scn.render.resolution_y = saved
    return written


if __name__ == "__main__":
    BUILD.main(build_all)
