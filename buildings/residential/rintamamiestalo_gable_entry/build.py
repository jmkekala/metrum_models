# SPDX-License-Identifier: GPL-2.0-only

"""Deterministic rebuild of rintamamiestalo_gable_entry, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Run without a .blend (blender --background --python build.py) it starts from an
empty scene and writes source.blend itself. Regenerate the textures first
(python3 facade_atlas.py export): the UVs index into the atlas, and the renders
read it.

A composite Finnish rintamamiestalo — the 1940s-50s one-and-a-half-storey
veterans' house: a 10 x 8 m block under a 45 degree gable roof, horizontal lap
siding over a concrete plinth with cellar lights, plain-glass windows and a
brick chimney on the ridge. This one stands with a gable end to the street
and its entrance in that gable:

- a terrace the full width of the house in front of the door;
- over the door, a balcony, reached from the attic storey by a pair of glazed
  doors;
- the back door in the far gable.

Construction is a set of closed solids unioned with Blender's exact boolean:
the house, the roof slab, the chimney, the terrace, the balcony slab, the
railing boards standing on both, the back-door canopy and the two flights of
steps. Wherever two solids meet face to face, the union merges the faces away,
so the result is the boundary of one empty volume and interior geometry cannot
occur.

The walls are textured as a trim sheet (see facade_atlas.py): siding tiles,
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
import handrails as HR  # noqa: E402
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
# Front faces -Y, and the front is a gable end: the siblings' 10.0 x 8.0 m
# block turned so that its ridge runs back from the street along Y. The street
# sees the 8 m gable with the entrance in it.
HX, HY = 4.0, 5.0
TAN = 1.0                        # 45 degree roof, the type's defining pitch
ROOF_T = L.FASC_H / PPM          # slab's vertical thickness = fascia height
EAVE_OV = 0.45                   # eave overhang, the catalog default
RAKE_OV = 0.35                   # gable (rake) overhang
Z_APEX = L.Z_WALL_TOP + HX * TAN                 # body apex, inside the slab
Z_RIDGE = L.Z_EAVE + ROOF_T + HX * TAN           # top of the ridge

# The terrace runs the house's full width, flush with both long walls, and is
# 2.4 m deep. Its deck is 5 cm under the front door's threshold, on a concrete
# base like the house's plinth.
# - The railing is a solid board, as CLAUDE.md asks of a balcony's parapet: a
#   see-through one would need alpha. Its balusters and handrail are painted,
#   and its top face is the cap.
# - The steps come off the front edge through a gap in the railing, centred
#   on the door, so the way in runs straight from the street.
TERRACE_Y = -HY - 2.40
TERRACE_Z = 0.65
TERRACE_RAIL_Z = TERRACE_Z + 0.90
RAIL_T = 0.10                    # railing board thickness
HANDRAIL_H = 0.10                # the painted handrail band along its top
STEPS_X = (-0.70, 0.70)

# The balcony is a slab cantilevered 1.2 m off the front gable at the attic
# floor. It is centred over the front door, so it is the door's canopy too.
# Its deck is at the gables' belt height.
BAL_X = (-1.60, 1.60)
BAL_Y = -HY - 1.20
BAL_T = 0.20
DECK_Z = L.Z_BELT
BAL_RAIL_Z = DECK_Z + 1.00

CHIMNEY = (-0.42, 0.42, 0.40, 1.00, 7.60, Z_RIDGE + 0.95)
# The chimney is open at the top: a half-brick shell round one flue, which
# drops FLUE_DEPTH to a soot floor. The top stands 0.95 m over the ridge, so
# the floor stays clear of the roof slab and nothing reaches into the flue.
FLUE_WALL = 0.12
FLUE_DEPTH = 0.80

# Back steps: landing just under the threshold, then three risers of ~0.17 m.
STEP_PROFILE = [(-0.05, 0.0), (-0.05, 0.68), (0.90, 0.68), (0.90, 0.51),
                (1.18, 0.51), (1.18, 0.34), (1.46, 0.34), (1.46, 0.17),
                (1.74, 0.17), (1.74, 0.0)]
# Terrace steps: three treads down from the terrace, whose own edge is the
# top riser, so four equal risers of 0.1625 m.
TERRACE_STEP_PROFILE = [(-0.05, 0.0), (-0.05, 0.4875), (0.28, 0.4875),
                        (0.28, 0.325), (0.56, 0.325), (0.56, 0.1625),
                        (0.84, 0.1625), (0.84, 0.0)]
# LOD3 keeps each flight's footprint as a ramp, so every tier has the same
# extents and therefore the same pivot.
STEP_PROFILE_LOW = [(-0.05, 0.0), (-0.05, 0.68), (0.90, 0.68), (1.74, 0.0)]
TERRACE_STEP_PROFILE_LOW = [(-0.05, 0.0), (-0.05, 0.4875), (0.28, 0.4875),
                            (0.84, 0.0)]
BACK_DOOR_X = 1.80
BACK_STEPS = (BACK_DOOR_X - 0.70, BACK_DOOR_X + 0.70)   # along x, off the rear gable
# Lean-to canopy over the back door, the type's usual kitchen entrance: 0.8 m
# out from the wall, a shallow fall, sitting clear above the door casing. It
# clears the 0.25 m test as a covered entrance, and is silhouette, so it
# survives to LOD2.
CANOPY_X = (BACK_DOOR_X - 0.75, BACK_DOOR_X + 0.75)
CANOPY_OUT = 0.80
CANOPY_Z = (3.30, 3.14)                           # top at the wall, top at the edge
CANOPY_T = 0.12

# --------------------------------------------------------------- elevations
# Sills sit at 1.5 m: 0.8 m above the 0.7 m floor, the floor itself being
# carried by the cellar plinth. The attic floor is 3.90 m, 5 cm over the
# balcony deck, and the attic window sits 0.75 m above it.
# The attic storey is lit from the gables, one window per end: the standard
# 1.80 x 1.40 m "wide" unit, centred under the ridge at ATTIC_SILL. It is the
# same sash the living room has, which is how the standardised type worked,
# and it is why no separate attic region is painted in the atlas.
# The front gable has the balcony doors at that level instead, so only the
# rear gable carries the window.
GF, ATTIC_SILL = 1.50, 4.65
BAL_DOOR_SILL = DECK_Z + 0.05

# Siding regions, stacked from the ground: (z where each starts, atlas band,
# the z that band's first row stands for). The gables switch to S2, whose
# belt board is at its foot, at the attic floor (see Z_BELT in the atlas).
EAVE_BANDS = [(0.0, "S1", 0.0)]
GABLE_BANDS = [(0.0, "S1", 0.0), (L.Z_BELT, "S2", L.Z_BELT)]
GABLE_TOP = [(0.0, L.Z_WALL_TOP), (HX, Z_APEX), (2 * HX, L.Z_WALL_TOP)]

# Openings as (kind, s, sill z), s being the centre measured along the wall
# from its start.
# The gables carry one window per storey besides their doors, the entrance
# storey of the front gable excepted: two smaller windows side by side read
# busier than the type is, and one large one is the catalog's rule for short
# walls (CLAUDE.md, Style Direction). The long walls keep several.
# Front gable, s = x + 4: the entrance under the balcony between two wide
# windows, the living room's and the kitchen's, mirrored about the door, and
# the balcony doors over it. Two windows on one storey of a gable is what
# CLAUDE.md allows an entrance gable: the door in the middle splits the
# storey, so they flank it rather than stand side by side.
FRONT_ITEMS = [("wide", 1.90, GF), ("door_front", HX, L.Z_FLOOR), ("wide", 6.10, GF),
               ("door_balcony", HX, BAL_DOOR_SILL), ("vent", HX, 7.35)]
# Rear gable, s = 4 - x: the back door and one wide window, and the one wide
# attic window lighting the attic from this end, as on the siblings.
REAR_ITEMS = [("door_back", HX - BACK_DOOR_X, L.Z_FLOOR),
              ("wide", 5.20, GF), ("cellar", 5.20, 0.25),
              ("wide", 4.00, ATTIC_SILL), ("vent", HX, 7.35)]
# east long wall, s = y + 5
EAST_ITEMS = [("std", 1.90, GF), ("wide", 5.30, GF), ("std", 8.30, GF),
              ("cellar", 5.30, 0.25)]
# west long wall, s = 5 - y: the living room's second window at the front
WEST_ITEMS = [("std", 1.80, GF), ("std", 5.00, GF), ("wide", 8.20, GF),
              ("cellar", 1.80, 0.25)]

# The house's walls, counter-clockwise seen from above so the outward face is
# on the right: (name, p0, p1, top, openings, corners, bands). Corners are the
# boards at the start and end. On the gables they run the full height and the
# belt board runs between them.
HOUSE_WALLS = [
    ("front", (-HX, -HY), (HX, -HY), GABLE_TOP, FRONT_ITEMS, (True, True), GABLE_BANDS),
    ("east", (HX, -HY), (HX, HY), L.Z_WALL_TOP, EAST_ITEMS, (True, True), EAVE_BANDS),
    ("rear", (HX, HY), (-HX, HY), GABLE_TOP, REAR_ITEMS, (True, True), GABLE_BANDS),
    ("west", (-HX, HY), (-HX, -HY), L.Z_WALL_TOP, WEST_ITEMS, (True, True), EAVE_BANDS),
]
# Offsets into the tiling siding band, so butt joints differ wall to wall.
U_OFF = {"front": 0.0, "east": 3.3, "rear": 6.1, "west": 9.4}

# Downpipes (scripts/downpipes.py): one from each eave's gutter, at
# diagonally opposite corners: the east eave's at the street end, where it
# stands behind the terrace's railing, the west eave's at the back.
DOWNPIPE_SPOTS = [("east", DP.CORNER), ("west", DP.CORNER)]
DOWNPIPES = [DP.eave_pipe(*{w[0]: w for w in HOUSE_WALLS}[n][1:3], s,
                          L.Z_EAVE, TAN, EAVE_OV) for n, s in DOWNPIPE_SPOTS]

# Roof safety kit (scripts/roof_safety.py), the sweep's way to the chimney,
# at the back, away from the entrance, as such kits usually are. The gables
# take the front door and the back door, and a ladder has to pass an eave, so
# it stands on the west eave wall's rear half, the side away from the
# catalog's view: a wall ladder between the two standard windows, the roof
# ladder straight above it up the west slope, and a level walkway along the
# slope 0.5 m below the ridge, forward to stand beside the stack. The wall
# ladder stands outside the eave, the building's widest point on this side,
# so LOD3 keeps its bare rails and every tier keeps LOD0's extents and pivot.
WEST = next(w for w in HOUSE_WALLS if w[0] == "west")   # s = 5 - y
KIT_S = 3.40                                      # centred between the windows
EAVE_WEST = RS.Eave(*WEST[1:3], L.Z_EAVE, EAVE_OV, L.Z_EAVE + ROOF_T - EAVE_OV * TAN, TAN)
WALK_OUT = -HX + 0.50 + RS.WALK_W                 # the walkway's downslope edge
ROOF_KIT = [
    RS.WallLadder(EAVE_WEST, KIT_S),
    RS.RoofLadder(EAVE_WEST, KIT_S, EAVE_WEST.roof_z(WALK_OUT)),
    RS.Walkway(EAVE_WEST, KIT_S - RS.HALF, HY - CHIMNEY[2], WALK_OUT),
]

# Handrails (scripts/handrails.py) on both flights, each on its right going
# up. The terrace steps fall 0.65 m in four risers from the deck; their rail
# starts on the deck against the end of the east railing board at the gap
# (inset 0), at the board's own height, so railing and handrail read as one.
# The back steps climb 0.68 m in three risers to their landing.
HANDRAILS = [
    HR.Flight(*STEPS_X, TERRACE_Y, -1.0, TERRACE_STEP_PROFILE, top=TERRACE_Z,
              inset=0.0),
    HR.Flight(*BACK_STEPS, HY, 1.0, STEP_PROFILE),
]


def wall_profile(top, length):
    return [(0.0, top), (length, top)] if isinstance(top, float) else top


def profile_z(prof, s):
    """Height of a wall's top edge at *s*, from its (s, z) profile."""
    for (sa, za), (sb, zb) in zip(prof, prof[1:]):
        if s <= sb + EPS:
            return za if sb - sa < EPS else za + (zb - za) * (s - sa) / (sb - sa)
    return prof[-1][1]


def item_mode(kind, level):
    """How an opening is built at each tier.

    ring  - LOD0: the casing is a ring of faces on the wall, the opening inside
            it is recessed with reveals and closed by its glass or door plane.
    cut   - LOD1: one recess the size of the casing; the casing is painted on
            the recessed plane. Half the wall breakpoints for the same shadow.
    flush - LOD2/3: the casing rect as a flat quad in the wall.
    None  - dropped: cellar lights and the vent below LOD1, the two smallest
            windows at LOD3.
    """
    if kind == "cellar":
        return ("ring", "flush", None, None)[level]
    if kind == "vent":
        return ("flush", "flush", None, None)[level]
    if kind in ("bath", "porch"):
        # under a metre across: about 5 px at LOD3's 120 m, so it goes
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


def uv_strip(fr, rect, a, b, z0, z1):
    x0, y0, w, h = rect
    return lambda co: (x0 + (fr.s_of(co) - a) / (b - a) * w,
                       y0 + min(max((co.z - z0) / (z1 - z0), 0.0), 1.0) * h)


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


def fill_region(B, fr, outline, holes, uvfn):
    """Triangulate a wall region with rectangular holes and add it."""
    loops = [outline] + holes
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((s, z, 0.0)) for s, z in loop] for loop in loops])
    for a, b, c in _flip_slivers(flat, tris):
        B.face([fr.P(*flat[a]), fr.P(*flat[b]), fr.P(*flat[c])], uvfn)


def recess(B, fr, rect, depth, fn, rev):
    l, r, b, t = rect
    c = [(l, b), (r, b), (r, t), (l, t)]
    for k in range(4):
        (s0, z0), (s1, z1) = c[k], c[(k + 1) % 4]
        B.face([fr.P(s0, z0), fr.P(s1, z1), fr.P(s1, z1, depth), fr.P(s0, z0, depth)], rev)
    B.face([fr.P(s, z, depth) for s, z in c], fn)


def item_rects(kind, s, z):
    w, h, cs, cb, ct = L.OPENINGS[kind]
    outer = (s - w / 2 - cs, s + w / 2 + cs, z - cb, z + h + ct)
    inner = (s - w / 2, s + w / 2, z, z + h)
    return outer, inner


def build_item(B, fr, kind, s, z, level):
    """Faces for one opening; returns the hole it needs in its wall region."""
    mode = item_mode(kind, level)
    (ol, orr, ob, ot), (il, ir, ib, it) = item_rects(kind, s, z)
    fn = uv_item(fr, kind, ol, ob)
    depth = L.REVEAL_DEPTH.get(kind, L.REVEAL_DEFAULT)
    rev = uv_patch("tread" if kind == "cellar" else "reveal")
    o = [(ol, ob), (orr, ob), (orr, ot), (ol, ot)]
    if mode == "flush":
        B.face([fr.P(*p) for p in o], fn)
        return o
    if mode == "cut":
        recess(B, fr, (ol, orr, ob, ot), depth, fn, rev)
        return o
    i = [(il, ib), (ir, ib), (ir, it), (il, it)]
    for k in range(4):
        B.face([fr.P(*o[k]), fr.P(*o[(k + 1) % 4]),
                fr.P(*i[(k + 1) % 4]), fr.P(*i[k])], fn)
    recess(B, fr, (il, ir, ib, it), depth, fn, rev)
    if abs(ob - ib) < EPS:
        # A door has no bottom casing, so the threshold edge lies on the hole's
        # own bottom edge; the hole has to carry those two corners too.
        return [(ol, ob), (il, ib), (ir, ib), (orr, ob), (orr, ot), (ol, ot)]
    return o


def build_wall(B, fr, prof, bands, edge_z, corners, items, u_off, level):
    """One elevation: corner-board columns, then siding regions with holes.

    *prof* is the wall's top edge as (s, z) points from s = 0 to its full
    length: level for an eave wall, peaked for a gable. *bands* stacks the
    siding regions from the ground up (see EAVE_BANDS). *edge_z* is the set of
    heights every panel end of this solid carries, so two walls meeting at a
    corner meet on exactly the same vertices. Corner boards run from their
    start to the top of the wall, a gable's belt board running between them.
    """
    Lw = fr.L
    # Contrasting paint survives every tier; these are flush UV strips.
    c0, c1 = corners
    s0 = L.CW if c0 else 0.0
    s1 = Lw - L.CW if c1 else Lw

    def rake(s):
        return profile_z(prof, s)

    def ez(s, end):
        # every level under this end of the wall's top, then the top at s
        return sorted({e for e in edge_z if e < rake(end) - EPS} | {rake(s)})

    regions = [(z0, uv_band(fr, L.S1_Y0 if band == "S1" else L.S2_Y0, zref, u_off))
               for z0, band, zref in bands]

    def band_at(z):
        fn = regions[0][1]
        for z0, f in regions:
            if z >= z0 - EPS:
                fn = f
        return fn

    for a, b, end, has in ((0.0, L.CW, 0.0, c0), (Lw - L.CW, Lw, Lw, c1)):
        if not has:
            continue
        # True: a board from the plinth up; a height: the board starts there
        z_from = L.Z_FLASH if has is True else has
        strip = uv_strip(fr, L.CORNER, a, b, L.Z_FLASH, max(rake(a), rake(b)))
        lo = [e for e in edge_z if e < rake(end) - EPS]
        for k, za in enumerate(lo):
            if k + 1 < len(lo):
                zb = lo[k + 1]
                poly = [(a, za), (b, za), (b, zb), (a, zb)]
            else:
                zb = rake(end)
                poly = [(a, za), (b, za), (b, rake(b)), (a, rake(a))]
            fn = band_at(za) if zb <= z_from + EPS else strip   # plinth below
            B.face([fr.P(s, z) for s, z in poly], fn)

    rect = {}
    for kind, s, z in items:
        if item_mode(kind, level):
            rect[(kind, s, z)] = item_rects(kind, s, z)[0]

    splits = [z0 for z0, _, _ in bands[1:]]
    bounds = [0.0] + splits + [None]
    peaks = [(s, z) for s, z in reversed(prof) if s0 + EPS < s < s1 - EPS]
    if splits and any(z < splits[-1] for _, z in peaks):
        raise ValueError("a %.1f m wall's top dips under its last band change" % Lw)
    left, right = ez(s0, 0.0), ez(s1, Lw)
    placed = 0
    for i in range(len(bounds) - 1):
        zlo, zhi = bounds[i], bounds[i + 1]
        last = zhi is None

        def within(z):
            return z > zlo + EPS and (last or z < zhi - EPS)

        outline = [(s0, zlo), (s1, zlo)] + [(s1, z) for z in right if within(z)]
        outline += peaks if last else [(s1, zhi), (s0, zhi)]
        outline += [(s0, z) for z in reversed(left) if within(z)]
        its = [(kind, s, z) for (kind, s, z), r in rect.items()
               if r[2] > zlo - EPS and (last or r[3] < zhi + EPS)]
        holes = [build_item(B, fr, kind, s, z, level) for kind, s, z in its]
        placed += len(its)
        fill_region(B, fr, outline, holes, regions[i][1])
    if placed != len(rect):
        raise ValueError("an opening straddles a band change on a %.1f m wall" % Lw)


def ring(B, walls, edge, level):
    """Build a solid's walls from one of the *_WALLS tables."""
    for name, p0, p1, top, items, corners, bands in walls:
        fr = Frame(p0, p1)
        build_wall(B, fr, wall_profile(top, fr.L), bands, sorted(set(edge)),
                   corners, items, U_OFF[name], level)


def close_solid(B, pairs, loops=2):
    """Cap a solid's open rim loops: normally a floor and a roof-shaped lid,
    the lid split along each pair of vertices in *pairs* (a ridge, a kink).
    Both caps end up buried — the floor on the ground, the lid inside a roof
    slab — but the solid must be closed for the boolean to be exact.

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
    found = []
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
        found.append(loop)
    if len(found) != loops:
        raise ValueError("expected %d open loops, got %d: a T-junction somewhere"
                         % (loops, len(found)))
    blank = uv_patch("blank")
    for loop in found:
        B.set_uv(bm.faces.new(loop), blank)
    for pair in pairs:
        a, b = (B.cache[(round(p[0], 4), round(p[1], 4), round(p[2], 4))] for p in pair)
        bmesh.ops.connect_verts(bm, verts=[a, b])


def house(level):
    """The house: four walls round one plan, closed by a floor and a lid split
    along the ridge."""
    B = Builder()
    edge = [0.0, L.Z_BELT, L.Z_EAVE, L.Z_WALL_TOP, L.Z_FLASH]
    ring(B, HOUSE_WALLS, edge, level)
    close_solid(B, [[(0.0, -HY, Z_APEX), (0.0, HY, Z_APEX)]])
    return B


def uv_deck(co):
    """Deck boards running along X: Y walks across the strip's boards, and
    every point samples the strip at the same V."""
    return ((co.y + 16.0) * PPM, L.DECK_Y0 + L.DECK_H / 2.0)


def uv_rail(fr, z0, z1):
    """The baluster strip. U runs along the railing in world metres, so the
    balusters on a board's two faces line up; V squeezes z0..z1 into the
    strip's rows, texel centre to texel centre."""
    along_x = abs(fr.t.x) > 0.5

    def fn(co):
        t = min(max((co.z - z0) / (z1 - z0), 0.0), 1.0)
        return (((co.x if along_x else co.y) + 16.0) * PPM,
                L.RAIL_Y0 + 0.5 + t * (L.RAIL_H - 1.0))
    return fn


def box(x0, x1, y0, y1, zs, side_uv, top_uv, bottom_uv):
    """A closed box on a plan rectangle. Its sides are split at every height
    in *zs* (ascending, the first and last being its bottom and top), so each
    band of a side can take its own mapping: side_uv(frame, k) for band k."""
    B = Builder()
    rim = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for i in range(4):
        fr = Frame(rim[i], rim[(i + 1) % 4])
        for k in range(len(zs) - 1):
            B.face([fr.P(0.0, zs[k]), fr.P(fr.L, zs[k]), fr.P(fr.L, zs[k + 1]),
                    fr.P(0.0, zs[k + 1])], side_uv(fr, k))
    B.face([(x, y, zs[-1]) for x, y in rim], top_uv)
    B.face([(x, y, zs[0]) for x, y in reversed(rim)], bottom_uv)
    return B


def railing(x0, x1, y0, y1, zb, zt):
    """One railing board standing on a deck. Balusters are painted up to the
    handrail band. The handrail, the cap and the board's 0.1 m ends are
    plain trim, and the ends read as posts."""
    zs = (zb, zt - HANDRAIL_H, zt)
    trim = uv_patch("trim")

    def side(fr, k):
        return uv_rail(fr, zb, zs[1]) if k == 0 and fr.L > RAIL_T + EPS else trim
    return box(x0, x1, y0, y1, zs, side, trim, uv_patch("blank"))


def terrace():
    """The terrace's concrete base with the deck on top, and its railing.
    The railing is a board along the front on each side of the steps, and
    one down each side to the house. The side boards start behind the front
    ones, so no two boards overlap, and the union merges away every face
    they share with the base, each other and the house."""
    t, z0, z1 = RAIL_T, TERRACE_Z, TERRACE_RAIL_Z
    yf, yb = TERRACE_Y, -HY
    base = box(-HX, HX, yf, yb, (0.0, z0),
               lambda fr, k: uv_band(fr, L.S1_Y0, 0.0, 0.0), uv_deck, uv_patch("blank"))
    return [("terrace", base),
            ("rail_fw", railing(-HX, STEPS_X[0], yf, yf + t, z0, z1)),
            ("rail_fe", railing(STEPS_X[1], HX, yf, yf + t, z0, z1)),
            ("rail_w", railing(-HX, -HX + t, yf + t, yb, z0, z1)),
            ("rail_e", railing(HX - t, HX, yf + t, yb, z0, z1))]


def balcony():
    """The balcony: a slab with trim-faced edges, a soffit under it and the
    deck on top, and three railing boards on it."""
    x0, x1 = BAL_X
    t, yf, yb = RAIL_T, BAL_Y, -HY
    deck = box(x0, x1, yf, yb, (DECK_Z - BAL_T, DECK_Z),
               lambda fr, k: uv_patch("trim"), uv_deck, uv_patch("soffit"))
    return [("balcony", deck),
            ("rail_bf", railing(x0, x1, yf, yf + t, DECK_Z, BAL_RAIL_Z)),
            ("rail_bw", railing(x0, x0 + t, yf + t, yb, DECK_Z, BAL_RAIL_Z)),
            ("rail_be", railing(x1 - t, x1, yf + t, yb, DECK_Z, BAL_RAIL_Z))]


# ================================================================== roofs
SLOPE_F = math.sqrt(1.0 + TAN * TAN)            # slope length per horizontal metre
ROOF_RPM = L.ROOF_H / L.ROOF_SLOPE_LEN           # atlas px per metre up a slope


def slab(axis, c, section, kinds, a0, a1, fns):
    """A closed slab: *section*, (across, z) points, extruded along *axis*
    from a0 to a1. Each section edge takes the UV function its kind names;
    the two end caps are the barge boards."""
    B = Builder()

    def W(a, p, z):
        return (a, c + p, z) if axis == "x" else (c + p, a, z)

    n = len(section)
    for k in range(n):
        (p0, z0_), (p1, z1_) = section[k], section[(k + 1) % n]
        B.face([W(a0, p0, z0_), W(a0, p1, z1_), W(a1, p1, z1_), W(a1, p0, z0_)],
               fns[kinds[k]])
    barge = uv_patch("barge")
    B.face([W(a0, p, z) for p, z in section], barge)
    B.face([W(a1, p, z) for p, z in reversed(section)], barge)
    return B


def gable_slab(axis, c, half_w, z_eave, over, a0, a1):
    """A gable roof as one closed slab: a chevron section extruded along the
    ridge.

    The section's underside meets the wall face at *z_eave*, so once the slab
    is unioned with the walls the part outside them is the soffit and the part
    inside disappears. The vertical ends of the section are the fascias; the
    two chevron end caps are the barge boards over the gables.
    """
    pe = half_w + over
    z0 = z_eave + ROOF_T + half_w * TAN
    zt = z0 - pe * TAN
    sec = [(-pe, zt - ROOF_T), (-pe, zt), (0.0, z0), (pe, zt),
           (pe, zt - ROOF_T), (0.0, z0 - ROOF_T)]
    kinds = ("fascia", "slope", "slope", "fascia", "soffit", "soffit")

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
    return slab(axis, c, sec, kinds, a0, a1, fns)


def chimney():
    """The stack: brick sides from inside the roof slab up to a capped rim
    round one open flue, sunk FLUE_DEPTH and lined and floored in soot. Every
    tier keeps the recess: painted flush, the soot lies in the sun and reads
    as dark grey, barely apart from the cap, where the shaded shaft reads
    black."""
    x0, x1, y0, y1, zb, zt = CHIMNEY
    B = Builder()
    cx0, cy0, cw, ch = L.CHIMNEY

    def side(a, b, z0, z1, fn=None):
        # a -> b along the face, left to right seen from the side it faces
        ax, ay = a
        bx, by = b
        length = math.hypot(bx - ax, by - ay)

        def brick(co):
            s = math.hypot(co.x - ax, co.y - ay)
            return (cx0 + (cw - length * PPM) / 2.0 + s * PPM, cy0 + ch - (zt - co.z) * PPM)
        B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], fn or brick)

    w = FLUE_WALL
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    flue = [(x0 + w, y0 + w), (x1 - w, y0 + w), (x1 - w, y1 - w), (x0 + w, y1 - w)]
    cap, soot = uv_patch("cap"), uv_patch("flue")
    for k in range(4):
        side(ring[k], ring[(k + 1) % 4], zb, zt)
        B.face([ring[k] + (zt,), ring[(k + 1) % 4] + (zt,),
                flue[(k + 1) % 4] + (zt,), flue[k] + (zt,)], cap)
    zf = zt - FLUE_DEPTH
    # walked the other way round, so the lining faces into the flue
    for k in range(4):
        side(flue[(k + 1) % 4], flue[k], zf, zt, soot)
    B.face([(x, y, zf) for x, y in flue], soot)
    B.face([(x, y, zb) for x, y in reversed(ring)], uv_patch("blank"))
    return B


def canopy():
    """The back-door canopy: a thin sloped slab with its back buried in the
    rear wall. Top samples the roof band, underside the soffit patch, edges
    the barge patch."""
    B = Builder()
    x0, x1 = CANOPY_X
    zw, ze = CANOPY_Z
    fall = (zw - ze) / CANOPY_OUT
    back = -0.10                                   # into the wall

    def top(d):
        return zw - fall * d

    sec = [(back, top(back)), (CANOPY_OUT, ze), (CANOPY_OUT, ze - CANOPY_T),
           (back, top(back) - CANOPY_T)]
    slope_len = math.hypot(CANOPY_OUT, zw - ze)

    def W(x, d, z):
        return (x, HY + d, z)

    def top_uv(co):
        d = (CANOPY_OUT - (co.y - HY)) * slope_len / CANOPY_OUT
        return ((co.x + 16.0) * PPM, L.ROOF_Y0 + d * ROOF_RPM)

    fns = (top_uv, uv_patch("barge"), uv_patch("soffit"), uv_patch("blank"))
    for k in range(4):
        (d0, z0), (d1, z1) = sec[k], sec[(k + 1) % 4]
        B.face([W(x0, d0, z0), W(x0, d1, z1), W(x1, d1, z1), W(x1, d0, z0)], fns[k])
    B.face([W(x0, d, z) for d, z in sec], uv_patch("barge"))
    B.face([W(x1, d, z) for d, z in reversed(sec)], uv_patch("barge"))
    return B


def steps(a0, a1, wall, outward, profile, axis="y"):
    """A flight of steps: *profile* is (distance out from the wall, z),
    extruded across a0..a1. *axis* is the way the flight runs: "y" off a
    front or rear wall at y = *wall*, "x" off a side wall at x = *wall*. Its
    back is buried in the wall it serves."""
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


# ================================================================ assembly


def build_lod(level):
    base = to_object(house(level), "tmp_house")
    low = level == 3
    parts = [
        to_object(gable_slab("y", 0.0, HX, L.Z_EAVE, EAVE_OV,
                             -HY - RAKE_OV, HY + RAKE_OV), "tmp_roof"),
        to_object(chimney(), "tmp_chimney"),
    ]
    parts += [to_object(B, "tmp_" + name) for name, B in terrace() + balcony()]
    if level < 3:
        parts.append(to_object(canopy(), "tmp_canopy"))
    parts.append(to_object(steps(*STEPS_X, TERRACE_Y, -1.0, TERRACE_STEP_PROFILE_LOW
                                 if low else TERRACE_STEP_PROFILE), "tmp_steps_f"))
    parts.append(to_object(steps(*BACK_STEPS, HY, 1.0, STEP_PROFILE_LOW
                                 if low else STEP_PROFILE), "tmp_steps_r"))
    parts += [to_object(B, name) for B, name in
              DP.solids(DOWNPIPES, *DP.MODES[level], L.PIPE_STRIP, L.ATLAS)]
    kit = RS.solids(ROOF_KIT, level, RS.Paint(L.ATLAS, strip=L.PIPE_STRIP),
                    extents=True)
    bare = RS.MODES[level][0] is None                # the rails alone, clear of all
    parts += [] if bare else [to_object(B, name) for B, name in kit]
    parts += [to_object(B, name) for B, name in
              HR.solids(HANDRAILS, level, RS.Paint(L.ATLAS, strip=L.PIPE_STRIP))]
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # Recover the cost of persistent corner paint from coplanar boolean
        # subdivisions. Keep UV/material seams and every architectural edge.
        # 0.001 radians tolerates float noise on nominally planar faces.
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    if bare:
        # after the weld and the dissolve, whose greedy passes the extra faces
        # would otherwise reorder
        RS.append(obj, kit)
    return obj


def all_walls():
    """Every wall of the house, as (name, frame, profile, openings, corners,
    bands)."""
    for name, p0, p1, top, items, corners, bands in HOUSE_WALLS:
        fr = Frame(p0, p1)
        yield name, fr, wall_profile(top, fr.L), items, corners, bands


def check_layout():
    """Assert the constraints that are invisible in the numbers and obvious
    once rendered:
    - openings colliding, clipping a roof or a corner board, or straddling a
      band change;
    - the gable outgrowing its atlas band, or its belt missing the fascia line;
    - something standing against the front gable across an opening;
    - the balcony missing the doors it serves;
    - the terrace's steps off the door's centre line or crowding a corner;
    - the back canopy missing its door."""
    problems = []
    if Z_APEX - L.Z_BELT > L.S2_SPAN:
        problems.append("gable apex %.2f is above the S2 band's %.2f"
                        % (Z_APEX, L.Z_BELT + L.S2_SPAN))
    slope = (HX + EAVE_OV) * SLOPE_F
    if abs(slope - L.ROOF_SLOPE_LEN) > 1e-3:
        problems.append("main slope is %.3f m, atlas assumes %.3f" % (slope, L.ROOF_SLOPE_LEN))
    fascia_foot = L.Z_EAVE - EAVE_OV * TAN
    if abs(L.Z_BELT - fascia_foot) > EPS:
        problems.append("the gables' belt at %.2f is off the fascia's lower edge at %.2f"
                        % (L.Z_BELT, fascia_foot))

    gap = 0.05
    for name, fr, prof, items, (c0, c1), bands in all_walls():
        splits = [z0 for z0, _, _ in bands[1:]]
        rects = [(k, item_rects(k, s, z)[0]) for k, s, z in items]
        for k, (l, r, b, t) in rects:
            lo = (L.CW if c0 else 0.0) + gap
            hi = fr.L - (L.CW if c1 else 0.0) - gap
            if l < lo or r > hi:
                problems.append("%s: %s at s %.2f..%.2f runs into a corner" % (name, k, l, r))
            for s in (l, r):
                vis = profile_z(prof, s) - (L.Z_WALL_TOP - L.Z_EAVE)
                if t > vis - gap:
                    problems.append("%s: %s top %.2f is under the roof (%.2f)" % (name, k, t, vis))
            for sp in splits:
                if b < sp < t:
                    problems.append("%s: %s straddles the band change at %.2f" % (name, k, sp))
            if b < L.Z_FLASH < t and not k.startswith("door"):
                problems.append("%s: %s straddles the plinth top" % (name, k))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b_ = rects[i][1], rects[j][1]
                if a[0] < b_[1] + gap and b_[0] < a[1] + gap and \
                        a[2] < b_[3] + gap and b_[2] < a[3] + gap:
                    problems.append("%s: %s and %s overlap" % (name, rects[i][0], rects[j][0]))

    # What stands against the front gable, as (x0, x1, z0, z1). It may not
    # cover any part of an opening's casing.
    contacts = {
        "terrace": (-HX, HX, 0.0, TERRACE_Z),
        "terrace's west railing": (-HX, -HX + RAIL_T, TERRACE_Z, TERRACE_RAIL_Z),
        "terrace's east railing": (HX - RAIL_T, HX, TERRACE_Z, TERRACE_RAIL_Z),
        "balcony slab": (BAL_X[0], BAL_X[1], DECK_Z - BAL_T, DECK_Z),
        "balcony's west railing": (BAL_X[0], BAL_X[0] + RAIL_T, DECK_Z, BAL_RAIL_Z),
        "balcony's east railing": (BAL_X[1] - RAIL_T, BAL_X[1], DECK_Z, BAL_RAIL_Z),
    }
    for k, s, z in FRONT_ITEMS:
        l, r, b, t = item_rects(k, s, z)[0]
        for what, (x0, x1, z0, z1) in contacts.items():
            if l - HX < x1 and x0 < r - HX and b < z1 and z0 < t:
                problems.append("front: the %s stands across the %s" % (what, k))

    # The balcony roofs the front door, and holds the balcony doors between
    # its railings with room to step out.
    l, r, b, t = item_rects("door_front", HX, L.Z_FLOOR)[0]
    if not (BAL_X[0] < l - HX and r - HX < BAL_X[1]):
        problems.append("the balcony does not cover the front door")
    if DECK_Z - BAL_T < t + 0.30:
        problems.append("the balcony slab sits on the front door's casing")
    if abs(sum(STEPS_X) / 2.0 - ((l + r) / 2.0 - HX)) > EPS:
        problems.append("the terrace steps are not centred on the front door")
    if STEPS_X[1] - STEPS_X[0] < r - l:
        problems.append("the terrace steps are narrower than the front door's casing")
    if DECK_Z - BAL_T - TERRACE_Z < 2.2:
        problems.append("the balcony is below head height over the terrace")
    l, r, b, t = item_rects("door_balcony", HX, BAL_DOOR_SILL)[0]
    if not (BAL_X[0] + RAIL_T + 0.30 < l - HX and r - HX < BAL_X[1] - RAIL_T - 0.30):
        problems.append("the balcony doors are not well inside its railings")
    if TERRACE_Z > L.Z_FLOOR - 0.02:
        problems.append("the terrace deck is not under the front door's threshold")
    if STEPS_X[0] < -HX + RAIL_T + 0.30 or STEPS_X[1] > HX - RAIL_T - 0.30:
        problems.append("the terrace steps crowd a corner of the railing")
    top = TERRACE_STEP_PROFILE[1][1]
    risers = [TERRACE_Z - top] + [TERRACE_STEP_PROFILE[k][1] - TERRACE_STEP_PROFILE[k + 1][1]
                                  for k in (2, 4, 6)]
    if max(risers) - min(risers) > 1e-6:
        problems.append("the terrace steps' risers differ: %s" % risers)

    l, r, b, t = next(item_rects(k, s, z)[0] for k, s, z in REAR_ITEMS if k == "door_back")
    cx = sorted(HX - v for v in (l, r))              # rear gable: s = 4 - x
    if not (CANOPY_X[0] < cx[0] and cx[1] < CANOPY_X[1]):
        problems.append("back canopy does not cover the door casing")
    if CANOPY_Z[0] - CANOPY_T < t + 0.10:
        problems.append("back canopy meets the wall on top of the door casing")
    if CANOPY_Z[1] - CANOPY_T - STEP_PROFILE[2][1] < 2.2:
        problems.append("back canopy's edge is below head height over the landing")
    if CANOPY_Z[0] > L.Z_BELT - 0.20:
        problems.append("back canopy runs into the gable's belt")
    if CHIMNEY[5] - FLUE_DEPTH < Z_RIDGE + 0.05:
        problems.append("the flue's floor is down in the roof slab")
    # downpipes clear of the corners and the openings, and behind the terrace
    walls = {w[0]: w for w in HOUSE_WALLS}
    for (w, _s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        avoid = [(k,) + item_rects(k, c, z)[0][:2] for k, c, z in walls[w][4]]
        problems += DP.problems(pipe, "the %s downpipe" % w, avoid)
        if pipe.point(0.0, 0.0, 0.0).y - DP.A < -HY + EPS:
            problems.append("the %s downpipe stands in the terrace" % w)
    # the roof kit: the wall ladder clear of the west wall's corners,
    # openings and downpipe; the walkway beside the stack, clear of it and of
    # the ridge
    wall = ROOF_KIT[0]
    avoid = [(k,) + item_rects(k, c, z)[0][:2] for k, c, z in WEST[4]]
    avoid += [("downpipe", p.s - DP.A, p.s + DP.A)
              for (w, _s), p in zip(DOWNPIPE_SPOTS, DOWNPIPES) if w == "west"]
    problems += RS.problems(wall, "the wall ladder", avoid)
    problems += HR.problems(HANDRAILS[0], "the terrace handrail",
                            L.OPENINGS["door_front"][0])
    problems += HR.problems(HANDRAILS[1], "the back handrail",
                            L.OPENINGS["door_back"][0])
    if abs(TERRACE_RAIL_Z - (TERRACE_Z + HR.HEIGHT)) > 1e-6:
        problems.append("the terrace handrail does not meet the railing's top")
    walk = ROOF_KIT[2]
    if walk.s0 > HY - CHIMNEY[3] or walk.s1 < HY - CHIMNEY[2]:
        problems.append("the walkway does not run the stack's length")
    x_hi = -HX - walk.out_hi                         # its upslope edge, in x
    if not CHIMNEY[0] - 0.30 < x_hi < CHIMNEY[0] - 0.02:
        problems.append("the walkway's edge is not just beside the stack")
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
        cam.location = centre + Vector(d) * 60.0
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
