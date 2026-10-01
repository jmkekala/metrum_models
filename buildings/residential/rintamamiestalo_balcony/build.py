# SPDX-License-Identifier: GPL-2.0-only

"""Deterministic rebuild of rintamamiestalo_balcony, all four LOD tiers.

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
brick chimney on the ridge. This one has the type's porch-and-balcony front:
a wide entrance porch centred on the long wall, its flat roof a balcony behind
a solid sided parapet, and over it a wall dormer (frontespiisi) with a shed
roof, whose front carries the balcony door out of the attic storey.

Construction is a set of closed solids unioned with Blender's exact boolean.
The house is three of them side by side, the west block, the dormer section
and the east block, because the dormer section's front wall runs from the
ground to the dormer eave in one plane: built as a separate part on top of a
whole house, it would overlap the house's front wall in that plane. Then the
porch-and-balcony, the roof slabs (the main roof in three pieces, cut back
over the dormer, and the dormer's shed roof), the chimney, the back-door canopy
and the two flights of steps. The union cuts the dormer roof into the main
roof, trims the walls where the soffits meet them and removes everything that
ends up inside, so the result is the boundary of one empty volume and interior
geometry cannot occur.

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
# Front faces -Y. Main block 10.0 x 8.0 m, ridge along X.
HX, HY = 5.0, 4.0
TAN = 1.0                        # 45 degree roof, the type's defining pitch
ROOF_T = L.FASC_H / PPM          # slab's vertical thickness = fascia height
EAVE_OV = 0.45                   # eave overhang, the catalog default
RAKE_OV = 0.35                   # gable (rake) overhang
Z_APEX = L.Z_WALL_TOP + HY * TAN                 # body apex, inside the slab
Z_RIDGE = L.Z_EAVE + ROOF_T + HY * TAN           # top of the ridge

# Porch, balcony and dormer: three stacked parts on one width, centred on the
# front.
#   - The entrance porch, 2.6 m deep. Its flat roof is the balcony.
#   - The balcony's parapet: the porch walls carried a metre past the deck,
#     solid and sided like the walls, under a cap board. A see-through railing
#     would need alpha, which CLAUDE.md rules out, and a solid sided parapet is
#     the type's own detail anyway.
#   - A wall dormer (frontespiisi) behind it: the front wall carried up
#     through the eave, so the attic storey gets a full-height wall for the
#     balcony door, under a shed roof falling to the front.
# One width means the porch sides, the parapet ends and the dormer corners
# stand on one line each side. CLAUDE.md asks for exact alignment or a real
# setback, and three near-misses stacked up would read as a mistake.
BX0, BX1 = -2.20, 2.20
PY_FRONT = -HY - 2.60
# The deck sits 5 cm under the 3.80 m attic floor, for the door's threshold.
DECK_Z = 3.75
PARAPET_Z = DECK_Z + 1.00
PARAPET_T = L.CW         # = the corner-board width, so cap and board lines meet
DZ_EAVE = 6.30           # dormer front meets its soffit, clear of door and window heads
DZ_TOP = DZ_EAVE + (L.Z_WALL_TOP - L.Z_EAVE)
D_PITCH = 0.30           # the shed roof rises 0.3 m per metre back, about 17 degrees
D_RAKE_OV = 0.30         # past the dormer's side walls; its front eave takes EAVE_OV
# Where the dormer's top meets the main roof, in metres back from the front
# wall. The dormer eave and wall top sit the same 2.0 m over the main ones, so
# the roof surfaces and the solids' lids meet on the same line.
D_JOIN = (DZ_TOP - L.Z_WALL_TOP) / (TAN - D_PITCH)
D_BACK = D_JOIN + 0.35   # the dormer roof runs on this far, buried in the main roof
MAIN_CUT = 2.20          # over the dormer the main slab starts this far back, inside the dormer

CHIMNEY = (0.30, 0.90, -0.42, 0.42, 7.60, Z_RIDGE + 0.95)
# The chimney is open at the top: a half-brick shell round one flue, which
# drops FLUE_DEPTH to a soot floor. The top stands 0.95 m over the ridge, so
# the floor stays clear of the roof slab and nothing reaches into the flue.
FLUE_WALL = 0.12
FLUE_DEPTH = 0.80

# Steps: landing just under the threshold, then three risers of ~0.17 m.
STEP_PROFILE = [(-0.05, 0.0), (-0.05, 0.68), (0.90, 0.68), (0.90, 0.51),
                (1.18, 0.51), (1.18, 0.34), (1.46, 0.34), (1.46, 0.17),
                (1.74, 0.17), (1.74, 0.0)]
# LOD3 keeps the steps' footprint as a ramp, so every tier has the same extents
# and therefore the same pivot.
STEP_PROFILE_LOW = [(-0.05, 0.0), (-0.05, 0.68), (0.90, 0.68), (1.74, 0.0)]
FRONT_DOOR_S = 0.90      # along the porch front from its west corner
BACK_DOOR_X = 1.20       # in the rear wall of the dormer section
FRONT_STEPS = (BX0 + FRONT_DOOR_S - 0.70, BX0 + FRONT_DOOR_S + 0.70)
BACK_STEPS = (BACK_DOOR_X - 0.70, BACK_DOOR_X + 0.70)   # along x, off the rear wall
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
# carried by the cellar plinth. The dormer's windows sit 1.0 m over the attic
# floor, clear of the parapet in front of them.
# The attic storey is lit from the gables, one window per end: the standard
# 1.80 x 1.40 m "wide" unit, centred under the ridge at ATTIC_SILL. It is the
# same sash the living room has, which is how the standardised type worked,
# and it is why no separate attic region is painted in the atlas.
# The dormer front carries only the balcony door: a wide window will not fit
# between the parapet, which sets the lowest sill that reads, and the dormer's
# eave, and two small windows flanking the door read busier than the type is.
GF, ATTIC_SILL = 1.50, 4.65

# Siding regions, stacked from the ground: (z where each starts, atlas band,
# the z that band's first row stands for).
# - The parapet reads the gable band S2 from the deck up, so S2's belt board
#   becomes a trim band round the porch at the balcony floor, and the corner
#   boards stop under it as they do under a gable's belt.
# - The dormer front, to 6.40 m, is taller than S1's painted 4.44 m, so it
#   reads S1 shifted down two metres: whole 0.125 m courses, and S1's
#   under-soffit shadow lands right under the dormer's soffit.
EAVE_BANDS = [(0.0, "S1", 0.0)]
GABLE_BANDS = [(0.0, "S1", 0.0), (L.Z_EAVE, "S2", L.Z_EAVE)]
PORCH_BANDS = [(0.0, "S1", 0.0), (DECK_Z, "S2", DECK_Z)]
DORMER_BANDS = [(0.0, "S1", 2.0)]

# Wall tops as (s, z) profiles; a plain height stands for a level top.
GABLE_TOP = [(0.0, L.Z_WALL_TOP), (HY, Z_APEX), (2 * HY, L.Z_WALL_TOP)]
# the dormer section's east side, s = y + 4: dormer top, then the house's lid
CHEEK_TOP = [(0.0, DZ_TOP), (D_JOIN, L.Z_WALL_TOP + D_JOIN * TAN), (HY, Z_APEX),
             (2 * HY, L.Z_WALL_TOP)]
CHEEK_TOP_W = [(2 * HY - s, z) for s, z in reversed(CHEEK_TOP)]

# Each solid's walls, counter-clockwise seen from above so the outward face is
# on the right: (name, p0, p1, top, openings, corners, bands, board_to).
# Openings are (kind, s, sill z), s measured along the wall from p0. Corners
# are the boards at the start and end: True from the plinth up, False for
# none, or the height a board starts at. board_to is where boards stop under
# a gable's belt board.
# Gable ends carry one window per storey: the wide living-room window below,
# centred under the wide attic window above. Two smaller windows side by side
# read as busier than the type is, and one large one is the catalog's rule for
# short walls (CLAUDE.md, Style Direction).
WEST_WALLS = [
    # s = x + 5
    ("front_w", (-HX, -HY), (BX0, -HY), L.Z_WALL_TOP, [("std", 1.40, GF)],
     (True, False), EAVE_BANDS, None),
    # against the dormer section, merged away
    ("join_w", (BX0, -HY), (BX0, HY), GABLE_TOP, [], (False, False), GABLE_BANDS,
     L.Z_EAVE),
    # s = -2.2 - x
    ("rear_w", (BX0, HY), (-HX, HY), L.Z_WALL_TOP,
     [("std", 1.40, GF), ("cellar", 1.40, 0.25)], (False, True), EAVE_BANDS, None),
    # s = 4 - y
    ("west", (-HX, HY), (-HX, -HY), GABLE_TOP, [
        ("wide", 4.00, GF), ("wide", 4.00, ATTIC_SILL),
        ("vent", 4.00, 7.35), ("cellar", 2.00, 0.25)],
     (True, True), GABLE_BANDS, L.Z_EAVE),
]
EAST_WALLS = [
    # s = x - 2.2
    ("front_e", (BX1, -HY), (HX, -HY), L.Z_WALL_TOP,
     [("std", 1.40, GF), ("cellar", 1.40, 0.25)], (False, True), EAVE_BANDS, None),
    # s = y + 4
    ("east", (HX, -HY), (HX, HY), GABLE_TOP, [
        ("wide", 4.00, GF), ("wide", 4.00, ATTIC_SILL),
        ("vent", 4.00, 7.35), ("cellar", 6.10, 0.25)],
     (True, True), GABLE_BANDS, L.Z_EAVE),
    # s = 5 - x
    ("rear_e", (HX, HY), (BX1, HY), L.Z_WALL_TOP, [("std", 1.40, GF)],
     (True, False), EAVE_BANDS, None),
    ("join_e", (BX1, HY), (BX1, -HY), GABLE_TOP, [], (False, False), GABLE_BANDS,
     L.Z_EAVE),
]
DORMER_WALLS = [
    # s = x + 2.2: the balcony door at the attic floor, its one opening, as a
    # gable carries one per storey; below the deck this wall is merged away
    ("dormer_front", (BX0, -HY), (BX1, -HY), DZ_TOP, [
        ("door_balcony", 2.20, DECK_Z + 0.05)], (PARAPET_Z, PARAPET_Z),
     DORMER_BANDS, None),
    # the dormer's side walls above the main roof; below it, merged away
    ("cheek_e", (BX1, -HY), (BX1, HY), CHEEK_TOP, [], (PARAPET_Z, False),
     GABLE_BANDS, None),
    # s = 2.2 - x: the back door and the bathroom
    ("rear_m", (BX1, HY), (BX0, HY), L.Z_WALL_TOP, [
        ("door_back", BX1 - BACK_DOOR_X, L.Z_FLOOR), ("bath", 3.20, 2.20)],
     (False, False), EAVE_BANDS, None),
    ("cheek_w", (BX0, HY), (BX0, -HY), CHEEK_TOP_W, [], (False, PARAPET_Z),
     GABLE_BANDS, None),
]
PORCH_WALLS = [
    # s = -4 - y
    ("porch_w", (BX0, -HY), (BX0, PY_FRONT), PARAPET_Z, [("std", 1.30, GF)],
     (False, True), PORCH_BANDS, DECK_Z),
    # s = x + 2.2: the entrance beside a wide window
    ("porch_front", (BX0, PY_FRONT), (BX1, PY_FRONT), PARAPET_Z, [
        ("door_front", FRONT_DOOR_S, L.Z_FLOOR), ("wide", 3.00, GF)],
     (True, True), PORCH_BANDS, DECK_Z),
    # s = y + 6.6
    ("porch_e", (BX1, PY_FRONT), (BX1, -HY), PARAPET_Z, [("std", 1.30, GF)],
     (True, False), PORCH_BANDS, DECK_Z),
]
# Offsets into the tiling siding band, so butt joints differ wall to wall. The
# pieces of the rear wall carry on from each other, since they meet in one
# plane; so do the two front pieces, though the porch stands between them.
# Downpipes (scripts/downpipes.py): one from each eave's gutter, at
# diagonally opposite corners, so each gable end shows one: the front's at
# its east end, the rear's at its west. The porch and the dormer take the
# middle of the front, so each eave's gutter drains to its outer end.
DOWNPIPE_SPOTS = [("front_e", HX - BX1 - DP.CORNER), ("rear_w", HX + BX0 - DP.CORNER)]
WALLS = {w[0]: w for w in WEST_WALLS + EAST_WALLS + DORMER_WALLS + PORCH_WALLS}
DOWNPIPES = [DP.eave_pipe(*WALLS[w][1:3], s, L.Z_EAVE, TAN, EAVE_OV)
             for w, s in DOWNPIPE_SPOTS]
U_OFF = {"front_w": 0.0, "front_e": 7.2, "dormer_front": 2.8, "east": 3.3,
         "rear_e": 6.1, "rear_m": 8.9, "rear_w": 13.3, "west": 9.4,
         "join_w": 0.0, "join_e": 0.0, "cheek_e": 4.1, "cheek_w": 11.7,
         "porch_w": 2.2, "porch_front": 0.3, "porch_e": 5.7}

# Roof safety kit (scripts/roof_safety.py), the sweep's way to the chimney.
# The porch and the dormer take the front, and its outer pieces are too short
# for a ladder beside their windows and downpipe, so the kit is on the rear:
# a wall ladder between the bathroom and the west window, the roof ladder
# straight above it up the rear slope, and a level walkway along the slope
# 0.5 m below the ridge, east to stand behind the stack. The rear wall's
# three pieces lie in one plane, so the kit takes the whole of it as its eave.
REAR = ((HX, HY), (-HX, HY))                      # s = 5 - x
KIT_S = HX + 2.15
EAVE_REAR = RS.Eave(*REAR, L.Z_EAVE, EAVE_OV, L.Z_EAVE + ROOF_T - EAVE_OV * TAN, TAN)
WALK_OUT = -HY + 0.50 + RS.WALK_W                 # the walkway's downslope edge
ROOF_KIT = [
    RS.WallLadder(EAVE_REAR, KIT_S),
    RS.RoofLadder(EAVE_REAR, KIT_S, EAVE_REAR.roof_z(WALK_OUT)),
    RS.Walkway(EAVE_REAR, HX - CHIMNEY[1], KIT_S + RS.HALF, WALK_OUT),
]

# Handrails (scripts/handrails.py) on both flights: each climbs 0.68 m in
# three risers to its landing, so each gets a rail on its right going up.
HANDRAILS = [
    HR.Flight(*FRONT_STEPS, PY_FRONT, -1.0, STEP_PROFILE),
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


def build_wall(B, fr, prof, bands, edge_z, corners, items, u_off, level,
               board_to=None):
    """One elevation: corner-board columns, then siding regions with holes.

    *prof* is the wall's top edge as (s, z) points from s = 0 to its full
    length: level for an eave wall, peaked for a gable, stepped for a dormer's
    side. *bands* stacks the siding regions from the ground up (see
    EAVE_BANDS). *edge_z* is the set of heights every panel end of this solid
    carries, so two walls meeting at a corner meet on exactly the same
    vertices. Corner boards stop at *board_to* when a belt board runs over
    them.
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
            if zb <= z_from + EPS or (board_to is not None and za >= board_to - EPS):
                fn = band_at(za)                 # plinth or flush wall below, belt above
            else:
                fn = strip
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
    for name, p0, p1, top, items, corners, bands, board_to in walls:
        fr = Frame(p0, p1)
        build_wall(B, fr, wall_profile(top, fr.L), bands, sorted(set(edge)),
                   corners, items, U_OFF[name], level, board_to)


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


def house_part(level, walls, pairs, extra=()):
    """One of the house's three side-by-side solids."""
    B = Builder()
    edge = [0.0, L.Z_EAVE, L.Z_WALL_TOP, L.Z_FLASH] + list(extra)
    ring(B, walls, edge, level)
    close_solid(B, pairs)
    return B


def west_block(level):
    return house_part(level, WEST_WALLS, [[(-HX, 0.0, Z_APEX), (BX0, 0.0, Z_APEX)]])


def east_block(level):
    return house_part(level, EAST_WALLS, [[(BX1, 0.0, Z_APEX), (HX, 0.0, Z_APEX)]])


def dormer_section(level):
    """The middle third of the house, with its front wall carried up into the
    dormer. Its lid is split at the ridge and where the dormer top meets the
    house's roof line."""
    y_j, z_j = -HY + D_JOIN, L.Z_WALL_TOP + D_JOIN * TAN
    return house_part(level, DORMER_WALLS,
                      [[(BX0, 0.0, Z_APEX), (BX1, 0.0, Z_APEX)],
                       [(BX0, y_j, z_j), (BX1, y_j, z_j)]], extra=[PARAPET_Z])


def porch_and_balcony(level):
    """The porch with the balcony on its roof, as one closed solid: sided walls
    carried up past the deck as a solid parapet, a cap board round the top,
    the parapet's inner faces and the deck. Its back face lies on the dormer
    section's front wall, and the union merges the two away."""
    B = Builder()
    edge = [0.0, DECK_Z, PARAPET_Z, L.Z_FLASH]
    ring(B, PORCH_WALLS, edge, level)
    t = PARAPET_T
    x0, x1, yf, yb = BX0, BX1, PY_FRONT, -HY
    xi0, xi1, yi = x0 + t, x1 - t, yf + t
    zt, zd = PARAPET_Z, DECK_Z

    # Cap board: one U-shaped face. Its outer edge carries every vertex the
    # wall tops have, the corner-board columns' included, and those sit
    # exactly on the parapet's inner lines because it is one board thick.
    outer = [(x0, yb), (x0, yi), (x0, yf), (xi0, yf), (xi1, yf), (x1, yf),
             (x1, yi), (x1, yb)]
    inner = [(xi1, yb), (xi1, yi), (xi0, yi), (xi0, yb)]
    B.face([(x, y, zt) for x, y in outer + inner], uv_patch("trim"))

    # the parapet's inner faces, sided like its outer ones, the belt at their
    # foot making a skirting round the deck
    for p0, p1 in (((xi1, yi), (xi0, yi)), ((xi0, yi), (xi0, yb)),
                   ((xi1, yb), (xi1, yi))):
        fr = Frame(p0, p1)
        B.face([fr.P(0.0, zd), fr.P(fr.L, zd), fr.P(fr.L, zt), fr.P(0.0, zt)],
               uv_band(fr, L.S2_Y0, DECK_Z, 0.0))
    B.face([(xi0, yi, zd), (xi1, yi, zd), (xi1, yb, zd), (xi0, yb, zd)],
           uv_patch("deck"))

    # the back, on the house wall: the porch's full width up to the deck and
    # the two parapet ends above it, through every height the side walls carry
    side = sorted({e for e in edge if e < zt - EPS} | {zt})
    back = ([(x0, 0.0), (x1, 0.0)] + [(x1, z) for z in side if z > EPS]
            + [(xi1, zt), (xi1, zd), (xi0, zd), (xi0, zt)]
            + [(x0, z) for z in reversed(side) if z > EPS])
    B.face([(x, yb, z) for x, z in back], uv_patch("blank"))
    close_solid(B, [], loops=1)
    return B


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


def gable_slab(axis, c, half_w, z_eave, over, a0, a1, cut=None):
    """A gable roof as one closed slab: a chevron section extruded along the
    ridge.

    The section's underside meets the wall face at *z_eave*, so once the slab
    is unioned with the walls the part outside them is the soffit and the part
    inside disappears. The vertical ends of the section are the fascias; the
    two chevron end caps are the barge boards over the gables. With *cut*, the
    front slope stops at that distance across from the ridge (negative, on the
    front) in a vertical face that has to end up buried, as it does inside the
    dormer.
    """
    pe = half_w + over
    z0 = z_eave + ROOF_T + half_w * TAN
    zt = z0 - pe * TAN
    if cut is None:
        sec = [(-pe, zt - ROOF_T), (-pe, zt), (0.0, z0), (pe, zt),
               (pe, zt - ROOF_T), (0.0, z0 - ROOF_T)]
        kinds = ("fascia", "slope", "slope", "fascia", "soffit", "soffit")
    else:
        zc = z0 + cut * TAN
        sec = [(cut, zc - ROOF_T), (cut, zc), (0.0, z0), (pe, zt),
               (pe, zt - ROOF_T), (0.0, z0 - ROOF_T)]
        kinds = ("cut", "slope", "slope", "fascia", "soffit", "soffit")

    def along(co):
        return co.x if axis == "x" else co.y

    def across(co):
        return (co.y if axis == "x" else co.x) - c

    def slope_uv(co):
        d = (pe - abs(across(co))) * SLOPE_F
        return ((along(co) + 16.0) * PPM, L.ROOF_Y0 + d * ROOF_RPM)

    def fascia_uv(co):
        return ((along(co) + 16.0) * PPM, L.FASC_Y0 + (co.z - (zt - ROOF_T)) * PPM)

    fns = {"fascia": fascia_uv, "slope": slope_uv, "soffit": uv_patch("soffit"),
           "cut": uv_patch("blank")}
    return slab(axis, c, sec, kinds, a0, a1, fns)


def dormer_roof():
    """The dormer's shed roof: a slab falling to the front at D_PITCH, from its
    eave over the balcony back into the main roof, which buries its back end.
    Mapped like the main roof: fascia band on the front edge, roof band up the
    slope from the eave, barge boards at the sides."""
    yf, yb = -HY - EAVE_OV, -HY + D_BACK

    def under(y):
        return DZ_EAVE + D_PITCH * (y + HY)

    sec = [(yf, under(yf)), (yf, under(yf) + ROOF_T), (yb, under(yb) + ROOF_T),
           (yb, under(yb))]
    kinds = ("fascia", "slope", "back", "soffit")
    sf = math.sqrt(1.0 + D_PITCH * D_PITCH)

    def slope_uv(co):
        return ((co.x + 16.0) * PPM, L.ROOF_Y0 + (co.y - yf) * sf * ROOF_RPM)

    def fascia_uv(co):
        return ((co.x + 16.0) * PPM, L.FASC_Y0 + (co.z - under(yf)) * PPM)

    fns = {"fascia": fascia_uv, "slope": slope_uv, "soffit": uv_patch("soffit"),
           "back": uv_patch("blank")}
    return slab("x", 0.0, sec, kinds, BX0 - D_RAKE_OV, BX1 + D_RAKE_OV, fns)


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
    base = to_object(west_block(level), "tmp_west")
    roof = lambda a0, a1, cut=None: gable_slab("x", 0.0, HY, L.Z_EAVE, EAVE_OV,
                                              a0, a1, cut)
    parts = [
        to_object(east_block(level), "tmp_east"),
        to_object(dormer_section(level), "tmp_dormer"),
        to_object(porch_and_balcony(level), "tmp_porch"),
        to_object(roof(-HX - RAKE_OV, BX0), "tmp_roof_w"),
        to_object(roof(BX0, BX1, cut=-HY + MAIN_CUT), "tmp_roof_m"),
        to_object(roof(BX1, HX + RAKE_OV), "tmp_roof_e"),
        to_object(dormer_roof(), "tmp_dormer_roof"),
        to_object(chimney(), "tmp_chimney"),
    ]
    if level < 3:
        parts.append(to_object(canopy(), "tmp_canopy"))
    prof = STEP_PROFILE if level < 3 else STEP_PROFILE_LOW
    parts.append(to_object(steps(*FRONT_STEPS, PY_FRONT, -1.0, prof), "tmp_steps_f"))
    parts.append(to_object(steps(*BACK_STEPS, HY, 1.0, prof), "tmp_steps_r"))
    parts += [to_object(B, name) for B, name in
              DP.solids(DOWNPIPES, *DP.MODES[level], L.PIPE_STRIP, L.ATLAS)]
    parts += [to_object(B, name) for B, name in
              RS.solids(ROOF_KIT, level, RS.Paint(L.ATLAS, strip=L.PIPE_STRIP))]
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
    return obj


def all_walls():
    """Every wall of every solid, as (name, frame, profile, openings, corners,
    bands, open_top). A porch wall's top is its parapet, not a roof."""
    for walls in (WEST_WALLS, EAST_WALLS, DORMER_WALLS, PORCH_WALLS):
        for name, p0, p1, top, items, corners, bands, _ in walls:
            fr = Frame(p0, p1)
            yield (name, fr, wall_profile(top, fr.L), items, corners, bands,
                   walls is PORCH_WALLS)


def check_layout():
    """Assert the constraints that are invisible in the numbers and obvious
    once rendered: openings colliding, clipping a roof or a corner board, or
    straddling a band change; a band read past its painted rows; the gable
    outgrowing its atlas band; the dormer's roof and the main roof failing to
    bury each other's cut ends; the balcony short of headroom; the back canopy
    missing its door."""
    problems = []
    if Z_APEX > L.S2_TOP:
        problems.append("gable apex %.2f is above the S2 band's %.2f" % (Z_APEX, L.S2_TOP))
    slope = (HY + EAVE_OV) * SLOPE_F
    if abs(slope - L.ROOF_SLOPE_LEN) > 1e-3:
        problems.append("main slope is %.3f m, atlas assumes %.3f" % (slope, L.ROOF_SLOPE_LEN))

    # S1 is painted from the flashing to 4.44 m. The dormer front reads it
    # shifted, and must stay inside that, above the plinth where it shows, and
    # in board phase. The parapet reads S2 from its belt up.
    s1_top = (286.0 - L.S1_Y0) / PPM
    zref = DORMER_BANDS[0][2]
    if DZ_TOP - zref > s1_top + EPS:
        problems.append("dormer front reads S1 up to %.2f m, painted to %.2f"
                        % (DZ_TOP - zref, s1_top))
    if DECK_Z - zref < L.Z_FLASH - EPS:
        problems.append("dormer front shows S1's plinth above the deck")
    if abs(zref / L.BOARD - round(zref / L.BOARD)) > 1e-6:
        problems.append("dormer front's shift is not whole siding courses")
    if PARAPET_Z - DECK_Z > L.S2_TOP - L.Z_EAVE:
        problems.append("parapet is taller than the S2 band")

    gap = 0.05
    doors = {}
    for name, fr, prof, items, (c0, c1), bands, open_top in all_walls():
        splits = [z0 for z0, _, _ in bands[1:]]
        rects = [(k, item_rects(k, s, z)[0]) for k, s, z in items]
        doors.update({k: (name, r) for k, r in rects if k.startswith("door")})
        for k, (l, r, b, t) in rects:
            lo = (L.CW if c0 else 0.0) + gap
            hi = fr.L - (L.CW if c1 else 0.0) - gap
            if l < lo or r > hi:
                problems.append("%s: %s at s %.2f..%.2f runs into a corner" % (name, k, l, r))
            for s in (l, r):
                vis = profile_z(prof, s) - (0.0 if open_top else L.Z_WALL_TOP - L.Z_EAVE)
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

    # the roofs' cut and back ends have to finish buried
    if not MAIN_CUT < D_JOIN < HY:
        problems.append("the main slab's cut (%.2f) must fall inside the dormer, "
                        "before it meets the roof (%.2f)" % (MAIN_CUT, D_JOIN))
    if L.Z_EAVE + ROOF_T + MAIN_CUT * TAN > DZ_TOP + D_PITCH * MAIN_CUT - 0.05:
        problems.append("the main slab's cut end pokes out of the dormer")
    if DZ_EAVE + ROOF_T + D_PITCH * D_BACK > L.Z_WALL_TOP + D_BACK * TAN - 0.02:
        problems.append("the dormer roof's back end pokes out of the main roof")
    # the main eave dies into the parapet's side, so the parapet must be taller
    if L.Z_EAVE + ROOF_T > PARAPET_Z - 0.05:
        problems.append("the main eave rises past the balcony parapet")
    head = DZ_EAVE - D_PITCH * EAVE_OV - DECK_Z
    if head < 2.2:
        problems.append("dormer fascia is %.2f m over the balcony deck" % head)

    wall, door = doors["door_back"]
    cx = sorted(BX1 - v for v in door[:2])            # rear_m: s = 2.2 - x
    if not (CANOPY_X[0] < cx[0] and cx[1] < CANOPY_X[1]):
        problems.append("back canopy does not cover the door casing")
    if CANOPY_Z[0] - CANOPY_T < door[3] + 0.10:
        problems.append("back canopy meets the wall on top of the door casing")
    if CANOPY_Z[1] - CANOPY_T - STEP_PROFILE[2][1] < 2.2:
        problems.append("back canopy's edge is below head height over the landing")
    if CHIMNEY[5] - FLUE_DEPTH < Z_RIDGE + 0.05:
        problems.append("the flue's floor is down in the roof slab")
    # downpipes clear of the corners and the openings
    for (w, _s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        items = WALLS[w][4]
        avoid = [(k,) + item_rects(k, c, z)[0][:2] for k, c, z in items]
        problems += DP.problems(pipe, "the %s downpipe" % w, avoid)
    # the roof kit: the wall ladder clear of the rear's corners, openings,
    # back steps, canopy and downpipe, in the rear line's s = 5 - x; the
    # walkway behind the stack, clear of it and of the ridge
    wall = ROOF_KIT[0]
    avoid = []
    for w in ("rear_e", "rear_m", "rear_w"):
        _n, (x0, _y0), _p1, _top, items = WALLS[w][:5]
        avoid += [(k, HX - x0 + a, HX - x0 + b)
                  for k, c, z in items for a, b in [item_rects(k, c, z)[0][:2]]]
    avoid += [("back steps", HX - BACK_STEPS[1], HX - BACK_STEPS[0]),
              ("back canopy", HX - CANOPY_X[1], HX - CANOPY_X[0])]
    for (w, _s), p in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        c = p.point(0.0, 0.0, 0.0)
        if abs(c.y - HY) < 0.2:
            avoid.append(("downpipe", HX - c.x - DP.A, HX - c.x + DP.A))
    problems += RS.problems(wall, "the wall ladder", avoid)
    problems += HR.problems(HANDRAILS[0], "the front handrail",
                            L.OPENINGS["door_front"][0])
    problems += HR.problems(HANDRAILS[1], "the back handrail",
                            L.OPENINGS["door_back"][0])
    walk = ROOF_KIT[2]
    if walk.s0 > HX - CHIMNEY[1] or walk.s1 < HX - CHIMNEY[0]:
        problems.append("the walkway does not run the stack's width")
    y_hi = HY + walk.out_hi                          # its upslope edge, in y
    if not CHIMNEY[3] + 0.02 < y_hi < CHIMNEY[3] + 0.30:
        problems.append("the walkway's edge is not just behind the stack")
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
