# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of rivitalo_brick_gable, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite Finnish rivitalo of the brick-and-timber kind built from the late
1960s on: four two-storey dwellings in one straight line, brick gables at the
ends and brick piers on every party line, with stained timber between them —
horizontal lap siding across the window bands and vertical board-and-batten
round the doors. The roof is an asymmetric shallow gable whose ridge sits near
the street, so the long slope runs back over the yard and cantilevers out past
the rear wall to roof the balcony under it.

Street side, per dwelling: the front door recessed into the boarded panel in
the middle of the bay, with one large window each side of it on each storey —
four windows to the front.

Yard side, per dwelling: a recessed balcony on the upper floor behind a solid
boarded parapet, glazed along its whole back wall; under it a covered terrace
on steel posts; a large window in the terrace's back wall, and beside that
window an alcove whose side wall — at a right angle to the wall the window is
in — carries the door into the house. Behind that, a private yard closed by a
boarded fence with a gate.

Construction is a set of closed solids unioned with Blender's exact boolean:
the main body, the roof slab, the balcony slab and its parapet, the screens
between balconies, the posts, the terrace paving, the entrance and alcove
steps, the ridge vents, and the yard fences. Each solid is simple to build on
its own; the union is what trims the walls where the soffits meet them and
removes everything that ends up inside, so the result is the boundary of one
empty volume and interior geometry cannot occur.

The walls are textured as a trim sheet (see facade_atlas.py): the cladding
bands tile, and each window or door is a hole in the wall with its own faces
mapped to the region that carries its casing and glazing. Every number the two
files share is imported from facade_atlas.py rather than written here a second
time.
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
# Front (the street side) faces -Y. One straight row, one ridge along X.
UNITS = 4
UNIT_W = L.BAY_W                 # 7.5 m; a whole number of 0.125 m boards
HX = UNITS * UNIT_W / 2.0
Y_FRONT, Y_REAR = -4.0, 4.0      # the heated block's wall faces
Y_RIDGE = -1.6                   # the ridge sits near the street
Y_ROOF_F, Y_ROOF_R = -4.6, 6.2   # the roof slab's two edges
TAN_F, TAN_R = 0.40, 0.19        # 21.8 deg to the street, 10.8 deg to the yard
ROOF_T = L.FASC_H / PPM          # slab's vertical thickness = fascia height
RAKE_OV = 0.60                   # the roof's overhang past each gable

Y_BALC = 5.8                     # the balcony's outer face
Y_SCREEN = 5.95                  # the screens between balconies end here
Y_POST = 5.85                    # the posts' centreline
BALC_T = 0.0625                  # the balcony floor slab
PARAPET_T = 0.18
PARAPET_Z = 4.5375               # top of the parapet: 1.04 m over the deck
SCREEN_T = 0.12
POST = 0.09                      # half the section of a galvanised post
POST_S = (1.875, 5.625)          # posts, twice in each bay

# The yard: a boarded fence on every party line and across the back, built as a
# whole number of L.FENCE_W bays so the boards keep their pitch.
YARD_FRONT = 5.80                # the fences start inside the terrace screens
YARD_BACK = 10.80                # 5.0 m of yard: two fence bays
YARD_T = 0.08
GATE_BAY = 0                     # which fence bay of a dwelling's back run

# Steps up to the 0.3125 m floor level. Both sit inside a projection every tier
# keeps — the roof in front, the balcony behind — so dropping them at LOD3
# cannot move the plan's extents.
FRONT_STEP = [(-0.05, 0.0), (-0.05, L.Z_FLOOR), (0.30, L.Z_FLOOR),
              (0.30, 0.16), (0.55, 0.16), (0.55, 0.0)]
STEP_W = 1.70                    # across the front door

# Ridge vents, the sheet-metal stacks this type carries over its flues. Each
# is open at the top, as every chimney is: a sheet-metal rim round one flue
# that drops FLUE_DEPTH to a soot floor. The top stands 0.95 m over the ridge,
# so the floor stays clear of the roof slab and nothing reaches into the flue.
VENT_X = (-UNIT_W, UNIT_W)
VENT = (0.42, 0.34, 0.45, 0.95)  # half x, half y, below the ridge, above it
FLUE_WALL = 0.10
FLUE_DEPTH = 0.80


def roof_under(y):
    """Height of the roof slab's underside at *y*, the asymmetric gable."""
    apex = L.Z_EAVE + (Y_RIDGE - Y_FRONT) * TAN_F
    return apex - ((Y_RIDGE - y) * TAN_F if y <= Y_RIDGE else (y - Y_RIDGE) * TAN_R)


# Downpipes (scripts/downpipes.py). The street eave's gutter drains to three
# pipes, one down the middle of the brick pier on each party line. The yard
# eave oversails the wall by 2.2 m, so each dwelling's pipe drops straight
# from its gutter down the outer face of the balcony post nearer its east
# party line, and goes with the posts at LOD2.
FRONT_PIPES = [DP.eave_pipe((-HX, Y_FRONT), (HX, Y_FRONT), k * UNIT_W, L.Z_EAVE,
                            TAN_F, Y_FRONT - Y_ROOF_F) for k in range(1, UNITS)]
REAR_PIPES = [DP.Pipe((x + POST, Y_POST + POST), (x - POST, Y_POST + POST), POST,
                      lambda out: roof_under(Y_POST + POST + out))
              for x in (-HX + k * UNIT_W + POST_S[1] for k in range(UNITS))]
DOWNPIPES = FRONT_PIPES + REAR_PIPES

# Roof safety kit (scripts/roof_safety.py): the way up to the ridge vents.
# The yard slope oversails its wall by 2.2 m over the balconies, too far for a
# wall ladder to pass outside it, the street side is the front, and the end
# gables are blank brick, so the wall ladder stands on the west gable next to
# its rear corner and passes outside the rake. That is at the back, away from
# the front doors, and the side away from the catalog view. The roof ladder
# runs up the long yard slope from its eave, just inside the rake, and a level
# walkway along the slope just behind the ridge serves both vents.
KIT_GABLE_S = 0.80                                # west gable, s = 4 - y
KIT_ROOF_S = 2.0 * HX - 0.70                      # rear wall, s = HX - x
GABLE_WEST = RS.Eave((-HX, Y_REAR), (-HX, Y_FRONT),
                     roof_under(Y_REAR - KIT_GABLE_S + RS.HALF), RAKE_OV,
                     roof_under(Y_REAR - KIT_GABLE_S) + ROOF_T, 0.0)
EAVE_REAR = RS.Eave((HX, Y_REAR), (-HX, Y_REAR), roof_under(Y_REAR),
                    Y_ROOF_R - Y_REAR, roof_under(Y_ROOF_R) + ROOF_T, TAN_R)
WALK_OUT = Y_RIDGE + VENT[1] + 0.08 + RS.WALK_W - Y_REAR   # its downslope edge
ROOF_KIT = [
    RS.WallLadder(GABLE_WEST, KIT_GABLE_S),
    RS.RoofLadder(EAVE_REAR, KIT_ROOF_S, EAVE_REAR.roof_z(WALK_OUT)),
    RS.Walkway(EAVE_REAR, HX - VENT_X[1] - VENT[0], KIT_ROOF_S + RS.HALF, WALK_OUT),
]


def kit_modes():
    """The kit's tiers: roof_safety.MODES without the brackets and posts at
    LOD1, which are under a pixel past 35 m and would take the tier past its
    ceiling along a 22 m walkway. From LOD2 the vents the walkway serves are
    gone, and the kit goes with them but for the wall ladder's bare rails,
    which stand outside the rake, the building's west extreme, so every tier
    keeps LOD0's bounds and pivot."""
    return ((1, True), (2, False), (None, False), (None, False))


Z_APEX = roof_under(Y_RIDGE) + L.WALL_INTO_ROOF     # body's lid, inside the slab
Z_RIDGE = roof_under(Y_RIDGE) + ROOF_T              # top of the ridge
Z_TOP_FRONT = L.Z_EAVE + L.WALL_INTO_ROOF
Z_TOP_REAR = roof_under(Y_REAR) + L.WALL_INTO_ROOF
Z_DECK = L.Z_STOREY + BALC_T                        # the balcony's walking level


# --------------------------------------------------------------- elevations
def row_panels(unit_panels):
    """Repeat one bay's cladding panels along the row, merging abutting piers."""
    out = []
    for k in range(UNITS):
        base = k * UNIT_W
        for s0, s1, band in unit_panels:
            if out and out[-1][2] == band and abs(out[-1][1] - (base + s0)) < 1e-9:
                out[-1] = (out[-1][0], base + s1, band)
            else:
                out.append((base + s0, base + s1, band))
    return out


def row_items(unit_layout):
    return [(kind, k * UNIT_W + s, z) for k in range(UNITS)
            for kind, s, z in unit_layout]


def plinth_panels(panels):
    """The plinth wears concrete whatever the storey above it wears, but keeps
    that storey's vertical breakpoints so the two meet on shared vertices."""
    return [(s0, s1, "plinth") for s0, s1, _ in panels]


FRONT_GF = row_panels(L.FRONT_PANELS)
REAR_GF = row_panels(L.REAR_GF_PANELS)
REAR_UP = row_panels(L.REAR_UP_PANELS)
END_P = list(L.END_PANELS)

# (p0, p1, panels per storey, items per storey, the wall's top).
# Each wall runs counter-clockwise seen from above, so its outward face is on
# the right and s runs along it from p0.
GF_ITEMS_FRONT = [(k, s, z) for k, s, z in row_items(L.FRONT_UNIT) if z < L.Z_STOREY]
UP_ITEMS_FRONT = [(k, s, z) for k, s, z in row_items(L.FRONT_UNIT) if z >= L.Z_STOREY]
MAIN_WALLS = {
    "front": dict(p0=(-HX, Y_FRONT), p1=(HX, Y_FRONT),
                  panels=(FRONT_GF, FRONT_GF),
                  items=(GF_ITEMS_FRONT, UP_ITEMS_FRONT),
                  top=lambda s: Z_TOP_FRONT, alcoves=()),
    "east": dict(p0=(HX, Y_FRONT), p1=(HX, Y_REAR), panels=(END_P, END_P),
                 items=((), ()),
                 top=lambda s: roof_under(Y_FRONT + s) + L.WALL_INTO_ROOF,
                 alcoves=()),
    "rear": dict(p0=(HX, Y_REAR), p1=(-HX, Y_REAR), panels=(REAR_GF, REAR_UP),
                 items=(row_items(L.REAR_GF_UNIT), row_items(L.REAR_UP_UNIT)),
                 top=lambda s: Z_TOP_REAR,
                 alcoves=tuple(k * UNIT_W for k in range(UNITS))),
    "west": dict(p0=(-HX, Y_REAR), p1=(-HX, Y_FRONT), panels=(END_P, END_P),
                 items=((), ()),
                 top=lambda s: roof_under(Y_REAR - s) + L.WALL_INTO_ROOF,
                 alcoves=()),
}
BAY_REGION = {"front": ("LOD3_FRONT", L.BAY_H_FRONT),
              "rear": ("LOD3_REAR", L.BAY_H_REAR)}
# Storey feet; the top of the last one is the wall's own top function.
STOREY_Z = (0.0, L.Z_FLOOR, L.Z_STOREY)


def item_mode(kind, level):
    """How an opening is built at each tier.

    ring  - LOD0: the casing is a ring of faces on the wall, the opening inside
            it is recessed with reveals and closed by its glass or door plane.
    cut   - LOD1: one recess the size of the casing; the casing is painted on
            the recessed plane. Half the wall breakpoints for the same shadow.
    flush - LOD2/3: the casing rect as a flat quad in the wall.
    """
    if kind == "door_front":
        # The one opening that clears the 0.25 m relief test on its own: the
        # entrance is set 0.30 m back into the boarded panel, and that shadow is
        # what tells the row apart from a flat-fronted terrace. Kept recessed
        # through LOD1 for that reason.
        return ("ring", "cut", "flush", "flush")[level]
    return ("ring", "cut", "flush", "flush")[level]


def alcove_kept(level):
    """The yard-door alcove: real massing at 1.4 m deep, painted at LOD3."""
    return level < 3


# ============================================================== mesh builder
class Builder:
    """One closed solid under construction, with UVs set as faces are made.

    Vertices are shared through a position cache, so faces that meet along an
    edge meet on the same vertices. That only works if every vertex lying on an
    edge is a corner of both faces — which is why region outlines carry their
    neighbours' breakpoints explicitly.
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
        # Area vector (Newell) from coordinates relative to the first vertex, in
        # double precision. Summed from absolute positions in mathutils' 32-bit
        # floats, a zero-area face keeps enough rounding to pass as real and
        # lands a third face on its edges.
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
    """A wall plane: s runs along the wall from p0, z is world height, and depth
    runs inward, away from the outward normal."""

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

def uv_band(fr, y0, z_ref):
    return lambda co: (fr.s_of(co) * PPM, y0 + (co.z - z_ref) * PPM)


def uv_vboard(fr, z0, z1):
    """Vertical boarding: true scale across the boards, stretched along them."""
    span = max(z1 - z0, 1e-6)
    return lambda co: (fr.s_of(co) * PPM,
                       L.VB_Y0 + (co.z - z0) / span * L.VB_H)


def uv_item(fr, kind, s_left, z_bot):
    """Planar, at true scale. Recessed faces sit behind the wall only along its
    normal, so they sample the same texels as if they were flush."""
    x0, y0 = L.ITEM_ORIGIN[kind]
    return lambda co: (x0 + (fr.s_of(co) - s_left) * PPM, y0 + (co.z - z_bot) * PPM)


def uv_patch(name):
    x0, y0, w, h = L.PATCHES[name]
    c = (x0 + w / 2.0, y0 + h / 2.0)
    return lambda co: c


def uv_ceiling(y_out):
    """A boarded ceiling read from the siding band, running out from *y_out*."""
    return lambda co: ((co.x + 16.0) * PPM, L.WOOD_Y0 + (y_out - co.y) * PPM)


def uv_deck(y0):
    """The balcony's boards, running out from the wall at *y0*."""
    return lambda co: ((co.x + 16.0) * PPM, L.WOOD_Y0 + (co.y - y0) * PPM)


BAND_UV = {
    "plinth": lambda fr, z0, z1: uv_band(fr, L.PLINTH_Y0, 0.0),
    "wood": lambda fr, z0, z1: uv_band(fr, L.WOOD_Y0, z0),
    "brick": lambda fr, z0, z1: uv_band(fr, L.BRICK_Y0, z0),
    "vboard": lambda fr, z0, z1: uv_vboard(fr, z0, z1),
}


# ================================================================== walls
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


def build_alcove(B, fr, base_s, level):
    """The yard entrance: a pocket in the wall whose side wall carries the door.

    The door is deliberately not in the wall the window is in. It stands at a
    right angle to it, in the opening beside it, which is how this type keeps a
    sheltered entrance on a terrace whose whole yard elevation is glazed.
    Returns the hole the pocket needs in the wall region.
    """
    ls0, ls1, z0, z1, d = L.ALCOVE
    s0, s1 = base_s + ls0, base_s + ls1
    vb_ceiling = lambda co: ((co.x + 16.0) * PPM, L.SOF_Y0 + 4.0)   # noqa: E731

    # the two side walls; the far one (at s1, facing back along the wall) takes
    # the door, so it is seen from the yard rather than from inside the pocket
    near = Frame(fr.P(s0, 0.0, 0.0)[:2], fr.P(s0, 0.0, d)[:2])
    far = Frame(fr.P(s1, 0.0, d)[:2], fr.P(s1, 0.0, 0.0)[:2])
    fill_region(B, near, [(0.0, z0), (d, z0), (d, z1), (0.0, z1)], [],
                uv_vboard(near, z0, z1))

    # The door stands on the alcove's own floor, so it is a notch in the side
    # wall's bottom edge rather than a hole in it, and the floor has to carry
    # every vertex the door's faces put on that line.
    (ol, orr, _ob, ot), (il, ir, _ib, _it) = item_rects(
        "door_glazed", d - L.ALCOVE_DOOR_S, L.Z_FLOOR)
    build_item(B, far, "door_glazed", d - L.ALCOVE_DOOR_S, L.Z_FLOOR, level)
    fill_region(B, far, [(0.0, z0), (ol, z0), (ol, ot), (orr, ot), (orr, z0),
                         (d, z0), (d, z1), (0.0, z1)], [],
                uv_vboard(far, z0, z1))
    on_far = [ol, orr] + ([il, ir] if item_mode("door_glazed", level) == "ring"
                          else [])

    back = Frame(fr.P(s1, 0.0, d)[:2], fr.P(s0, 0.0, d)[:2])
    fill_region(B, back, [(0.0, z0), (s1 - s0, z0), (s1 - s0, z1), (0.0, z1)],
                [], uv_vboard(back, z0, z1))
    B.face([fr.P(s0, z1, 0.0), fr.P(s1, z1, 0.0), fr.P(s1, z1, d), fr.P(s0, z1, d)],
           vb_ceiling)
    floor = [(s1, 0.0), (s0, 0.0), (s0, d), (s1, d)]
    floor += [(s1, d - v) for v in sorted(on_far)]   # depths descending to 0
    B.face([fr.P(s, z0, dep) for s, dep in floor], uv_patch("pave"))
    return [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]


def build_wall(B, fr, spec, level):
    """One elevation: cladding panels, storey by storey, holed for every opening.

    Panels are vertical strips of one cladding each — a brick pier on every
    party line, lap siding across the window bands, vertical boarding round the
    doors — so the wall is a grid of panel-by-storey regions. Regions carry
    their neighbours' breakpoints on every shared edge, so two that meet do so
    on the same vertices and the solid stays closed.
    """
    panels_gf, panels_up = spec["panels"]
    items_gf, items_up = spec["items"]
    top = spec["top"]
    alc_s = spec["alcoves"] if alcove_kept(level) else ()
    layers = [(STOREY_Z[0], STOREY_Z[1], plinth_panels(panels_gf), (), ()),
              (STOREY_Z[1], STOREY_Z[2], panels_gf, items_gf, alc_s),
              (STOREY_Z[2], None, panels_up, items_up, ())]

    apex_s = None
    if top(0.0) != top(fr.L / 2.0) or top(fr.L) != top(fr.L / 2.0):
        apex_s = (Y_RIDGE - Y_FRONT) if fr.t.y > 0 else (Y_REAR - Y_RIDGE)

    # Doors and the alcove stand on their storey's floor line, which is also the
    # line where one cladding band hands over to the next. They are therefore
    # notches in the region's bottom edge rather than holes inside it, and the
    # region below has to carry every vertex the faces above put on that line.
    standing = [_standing(items, alcoves, zlo, level)
                for zlo, _zhi, _p, items, alcoves in layers]

    for idx, (zlo, zhi, panels, items, alcoves) in enumerate(layers):
        below = layers[idx - 1][2] if idx else None
        above = layers[idx + 1][2] if idx + 1 < len(layers) else None
        cuts_above = _breaks(above, 0.0, fr.L)
        for l, r, mids, _what in (standing[idx + 1] if idx + 1 < len(layers) else []):
            cuts_above += [l, r] + mids
        for s0, s1, band in panels:
            zt = (lambda s: zhi) if zhi is not None else top
            cuts_b = _breaks(below, s0, s1)
            cuts_t = sorted(s for s in cuts_above if s0 + EPS < s < s1 - EPS)
            if zhi is None and apex_s is not None and s0 < apex_s < s1:
                cuts_t = sorted(cuts_t + [apex_s])
            stand = [x for x in standing[idx] if s0 - EPS < x[0] and x[1] < s1 + EPS]
            stand.sort()
            outline = [(s0, zlo)]
            cursor = s0
            for l, r, _mids, what in stand:
                if l < cursor + 0.02:
                    raise ValueError("a floor-standing opening touches a cladding "
                                     "panel's edge at s %.2f" % l)
                outline += [(s, zlo) for s in cuts_b if cursor < s < l]
                outline += [(l, zlo), (l, what[-1]), (r, what[-1]), (r, zlo)]
                cursor = r
            outline += [(s, zlo) for s in cuts_b if s > cursor]
            outline += ([(s1, zlo), (s1, zt(s1))]
                        + [(s, zt(s)) for s in reversed(cuts_t)]
                        + [(s0, zt(s0))])
            for l, r, _mids, what in stand:
                if what[0] == "item":
                    build_item(B, fr, what[1], what[2], what[3], level)
                else:
                    build_alcove(B, fr, what[1], level)
            holes = []
            for kind, s, z in items:
                rr = item_rects(kind, s, z)[0]
                if rr[0] > s0 - EPS and rr[1] < s1 + EPS and rr[2] > zlo + EPS \
                        and rr[3] < min(zt(rr[0]), zt(rr[1])) + EPS:
                    holes.append(build_item(B, fr, kind, s, z, level))
            for base in alcoves:
                a0, a1, az0, az1, _d = L.ALCOVE
                if base + a0 > s0 - EPS and base + a1 < s1 + EPS and az0 > zlo + EPS:
                    holes.append(build_alcove(B, fr, base, level))
            fill_region(B, fr, outline, holes,
                        BAND_UV[band](fr, zlo, zt(s0)))


def _standing(items, alcoves, zlo, level):
    """Openings whose threshold is this storey's floor line.

    Returns (left, right, extra vertices the storey below must carry, what) per
    opening; *what* ends with the height the region's bottom edge detours to.
    """
    out = []
    for kind, s, z in items:
        outer, inner = item_rects(kind, s, z)
        if abs(outer[2] - zlo) > EPS:
            continue
        # a ring puts the casing's two jambs and the recess's floor on the line,
        # so three faces meet it; a recess or a flush quad puts only one
        mids = [inner[0], inner[1]] if item_mode(kind, level) == "ring" else []
        out.append((outer[0], outer[1], mids, ("item", kind, s, z, outer[3])))
    for base in alcoves:
        a0, a1, az0, az1, _d = L.ALCOVE
        if abs(az0 - zlo) < EPS:
            out.append((base + a0, base + a1, [], ("alcove", base, az1)))
    return out


def _breaks(panels, s0, s1):
    if not panels:
        return []
    out = set()
    for a, b, _ in panels:
        for s in (a, b):
            if s0 + EPS < s < s1 - EPS:
                out.add(round(s, 6))
    return sorted(out)


def build_bay_wall(B, fr, spec, name):
    """LOD3's front or rear wall: one quad per dwelling bay, nothing cut.

    Every bay is identical, so all four sample the same painted region; the UV
    runs from each bay's own start, which makes the bay boundaries UV seams and
    lets four faces do the work of a wall with twenty holes in it.
    """
    region, bay_h = BAY_REGION[name]
    x0, y0, w, h = getattr(L, region)
    top = spec["top"](0.0)
    for k in range(UNITS):
        a, b = k * UNIT_W, (k + 1) * UNIT_W
        lo = [z for z in STOREY_Z[1:] if EPS < z < top - EPS]
        pts = [(a, 0.0), (b, 0.0)]
        pts += [(b, z) for z in (lo if k == UNITS - 1 else [])]
        pts += [(b, top), (a, top)]
        pts += [(a, z) for z in reversed(lo if k == 0 else [])]

        def fn(co, a=a):
            return (x0 + (fr.s_of(co) - a) / L.BAY_W * w, y0 + co.z / bay_h * h)

        B.face([fr.P(s, z) for s, z in pts], fn)


def close_solid(B, apexes):
    """Cap a wall ring: an n-gon floor, and a roof-shaped lid split at the ridge.

    Both end up buried — the floor on the ground, the lid inside the roof slab —
    but the solid must be closed for the boolean to be exact.

    The rim is walked and capped by hand rather than with bmesh's holes_fill,
    which silently skips a loop whose vertices already carry a face.
    """
    bm = B.bm
    bm.edges.index_update()
    # walked in edge-index order, never set order: a set of BMEdges iterates by
    # memory address, so the caps would start on a different vertex each run and
    # the boolean would triangulate differently every time
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


def main_body(level):
    B = Builder()
    for name, spec in MAIN_WALLS.items():
        fr = Frame(spec["p0"], spec["p1"])
        if level >= 3 and name in BAY_REGION:
            build_bay_wall(B, fr, spec, name)
        else:
            build_wall(B, fr, spec, level)
    close_solid(B, [(HX, Y_RIDGE, Z_APEX), (-HX, Y_RIDGE, Z_APEX)])
    return B


# ================================================================== roof
def roof_slab():
    """The asymmetric gable as one closed slab: a section extruded along X.

    The section carries a vertex where each wall face meets the underside, so
    the balcony's ceiling, the street eave's soffit and the parts that end up
    buried inside the building are separate faces with UVs of their own rather
    than one plane the boolean has to interpolate across.
    """
    B = Builder()
    uF, uR, uB = roof_under(Y_ROOF_F), roof_under(Y_RIDGE), roof_under(Y_ROOF_R)
    uFW, uRW = roof_under(Y_FRONT), roof_under(Y_REAR)
    # roof_under() is the SOFFIT line — where the underside meets each wall —
    # so the slab sits on it and its top surface is ROOF_T above. Building it
    # the other way round leaves every wall top, screen and post standing proud
    # of the roof and the body's own lid exposed over it; check_roof() below
    # now fails the build if that ever comes back.
    sec = [(Y_ROOF_F, uF), (Y_ROOF_F, uF + ROOF_T), (Y_RIDGE, uR + ROOF_T),
           (Y_ROOF_R, uB + ROOF_T), (Y_ROOF_R, uB), (Y_REAR, uRW),
           (Y_RIDGE, uR), (Y_FRONT, uFW)]
    stations = [-HX - RAKE_OV, -HX, HX, HX + RAKE_OV]
    slope_f = math.sqrt(1.0 + TAN_F * TAN_F)
    slope_r = math.sqrt(1.0 + TAN_R * TAN_R)
    rpm = L.ROOF_H / L.ROOF_SLOPE_LEN

    def fascia(z_bot):
        return lambda co: ((co.x + 16.0) * PPM, L.FASC_Y0 + (co.z - z_bot) * PPM)

    def slope_front(co):
        return ((co.x + 16.0) * PPM, L.ROOF_Y0 + (co.y - Y_ROOF_F) * slope_f * rpm)

    def slope_rear(co):
        return ((co.x + 16.0) * PPM, L.ROOF_Y0 + (Y_ROOF_R - co.y) * slope_r * rpm)

    def eave_soffit(co):
        return ((co.x + 16.0) * PPM, L.SOF_Y0 + (Y_FRONT - co.y) * PPM)

    def deep_soffit(co):
        # the rake's underside over the middle of the roof: the boarding's
        # inboard tone, with its rafters still landing on their own spacing
        return ((co.x + 16.0) * PPM, L.SOF_Y0 + 3.0)

    fns = [fascia(uF), slope_front, slope_rear, fascia(uB),
           uv_ceiling(Y_ROOF_R), deep_soffit, deep_soffit, eave_soffit]
    for k in range(len(sec)):
        (y0, z0), (y1, z1) = sec[k], sec[(k + 1) % len(sec)]
        for a, b in zip(stations, stations[1:]):
            B.face([(b, y0, z0), (b, y1, z1), (a, y1, z1), (a, y0, z0)], fns[k])
    barge = uv_patch("barge")
    B.face([(stations[0], y, z) for y, z in sec], barge)
    B.face([(stations[-1], y, z) for y, z in reversed(sec)], barge)
    return B


# =============================================================== balcony
def box(x0, x1, y0, y1, z0, z1, side, top, bottom="blank"):
    """A closed rectangular box; every face takes a flat patch."""
    B = Builder()
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    fn = uv_patch(side) if isinstance(side, str) else side
    for k in range(4):
        (ax, ay), (bx, by) = ring[k], ring[(k + 1) % 4]
        B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], fn)
    B.face([(x, y, z1) for x, y in ring],
           uv_patch(top) if isinstance(top, str) else top)
    B.face([(x, y, z0) for x, y in reversed(ring)],
           uv_patch(bottom) if isinstance(bottom, str) else bottom)
    return B


def screen_faces():
    """Both faces of every balcony screen, as x stations.

    The row-long slabs are subdivided on these, so the boolean's cut where a
    screen passes through one lands on an edge that is already there instead of
    retriangulating a thirty-metre n-gon round five small rectangles.
    """
    xs = []
    for i in range(UNITS + 1):
        x = -HX + i * UNIT_W
        a, b = x - SCREEN_T / 2.0, x + SCREEN_T / 2.0
        if abs(x) > HX - EPS:
            a, b = (x, x + SCREEN_T) if x < 0 else (x - SCREEN_T, x)
        xs += [a, b]
    return sorted(v for v in xs if -HX + EPS < v < HX - EPS)


def xslab(y0, y1, z0, z1, side, top, bottom):
    """A box spanning the row, subdivided in x on the screens' faces."""
    B = Builder()
    xs = [-HX] + screen_faces() + [HX]
    fns = [side if callable(side) else uv_patch(side),
           top if callable(top) else uv_patch(top),
           bottom if callable(bottom) else uv_patch(bottom)]
    for a, b in zip(xs, xs[1:]):
        B.face([(a, y0, z0), (b, y0, z0), (b, y0, z1), (a, y0, z1)], fns[0])
        B.face([(b, y1, z0), (a, y1, z0), (a, y1, z1), (b, y1, z1)], fns[0])
        B.face([(a, y0, z1), (b, y0, z1), (b, y1, z1), (a, y1, z1)], fns[1])
        B.face([(a, y1, z0), (b, y1, z0), (b, y0, z0), (a, y0, z0)], fns[2])
    for x, flip in ((xs[0], True), (xs[-1], False)):
        ring = [(y0, z0), (y1, z0), (y1, z1), (y0, z1)]
        B.face([(x, y, z) for y, z in (ring if flip else reversed(ring))], fns[0])
    return B


def balcony_slab():
    """The balcony floor: boards over the terrace, buried into the rear wall."""
    edge = uv_band(Frame((-HX, Y_BALC), (HX, Y_BALC)), L.WOOD_Y0, L.Z_STOREY)
    return xslab(Y_REAR - 0.10, Y_BALC, L.Z_STOREY, Z_DECK, edge,
                 uv_deck(Y_REAR), uv_ceiling(Y_BALC))


def parapet():
    """The balcony's solid boarded front, with a sheet-metal coping."""
    face = uv_band(Frame((-HX, Y_BALC), (HX, Y_BALC)), L.WOOD_Y0, L.Z_STOREY)
    return xslab(Y_BALC - PARAPET_T, Y_BALC, Z_DECK, PARAPET_Z,
                 face, "cap", "blank")


def screen(x, level=0):
    """One privacy screen between balconies, ground to roof.

    Its top runs above the roof's underside at both ends but stays inside the
    slab, so the union trims it to the soffit exactly; check_layout() asserts
    both, because a screen poking through the roof is only visible from above.
    """
    B = Builder()
    xl, xr = x - SCREEN_T / 2.0, x + SCREEN_T / 2.0
    if abs(x) > HX - EPS:                       # the end screens sit inside the
        xl, xr = (x, x + SCREEN_T) if x < 0 else (x - SCREEN_T, x)   # gable line
    y0, y1 = Y_REAR - 0.10, Y_SCREEN
    if level >= 2:
        # a 0.05 m gap under the soffit is invisible past 70 m, and keeping the
        # five screens out of the roof saves more than the gap costs
        zt0, zt1 = roof_under(y0) - 0.05, roof_under(y1) - 0.05
    else:
        zt0, zt1 = roof_under(y0) + 0.30, roof_under(y1) + 0.14
    prof = [(y0, 0.0), (y1, 0.0), (y1, zt1), (y0, zt0)]
    board = uv_vboard(Frame((xl, y0), (xl, y1)), 0.0, zt1)
    for xx, flip in ((xl, False), (xr, True)):
        pts = prof if flip else list(reversed(prof))
        B.face([(xx, y, z) for y, z in pts], board)
    B.face([(xl, y1, 0.0), (xr, y1, 0.0), (xr, y1, zt1), (xl, y1, zt1)], board)
    B.face([(xr, y0, 0.0), (xl, y0, 0.0), (xl, y0, zt0), (xr, y0, zt0)],
           uv_patch("blank"))
    B.face([(xl, y0, zt0), (xl, y1, zt1), (xr, y1, zt1), (xr, y0, zt0)],
           uv_patch("blank"))
    B.face([(xl, y1, 0.0), (xl, y0, 0.0), (xr, y0, 0.0), (xr, y1, 0.0)],
           uv_patch("blank"))
    return B


def post(x):
    """A galvanised post under the balcony's outer edge, up into the roof."""
    return box(x - POST, x + POST, Y_POST - POST, Y_POST + POST,
               0.0, roof_under(Y_POST) + 0.12, "post", "blank")


# ================================================================= ground
def steps(a0, a1, wall, outward, profile, axis="y"):
    """A flight of steps: *profile* is (distance out from the wall, z), extruded
    across a0..a1. Its back is buried in the wall it serves."""
    B = Builder()

    def W(a, d, z):
        return (a, wall + outward * d, z) if axis == "y" else (wall + outward * d, a, z)

    def across(co):
        return co.x if axis == "y" else co.y

    def out(co):
        return ((co.y if axis == "y" else co.x) - wall) * outward

    def riser_uv(co):
        return ((across(co) + 11.0) * PPM, L.PLINTH_Y0 + co.z * PPM)

    def cheek_uv(co):
        return ((out(co) + 11.0) * PPM, L.PLINTH_Y0 + co.z * PPM)

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


def terrace():
    """The paved strip under the balcony, buried into the rear wall."""
    return xslab(Y_REAR - 0.10, Y_SCREEN, 0.0, 0.08, "pave", "pave", "blank")


def fence_run(p0, p1, gates, level):
    """A yard fence: a whole number of L.FENCE_W bays of boards between posts.

    Every bay is a quad mapped to the fence region at true scale, so the boards
    keep their pitch however long the run is. The gate is the same: one bay
    mapped to its own region, since a leaf a few centimetres proud of the boards
    is far under the 0.25 m relief test.
    """
    B = Builder()
    fr = Frame(p0, p1)
    n = max(1, int(round(fr.L / L.FENCE_W)))
    if not gates and level >= 2:
        # a plain run carries nothing but boards at 0.125 m, which is about one
        # pixel past 70 m, so one stretched bay says the same thing
        n = 1
    if level >= 3:
        n, gates = 1, ()            # and at the last tier so does a gated one
    bw = fr.L / n
    h, do, di = L.FENCE_H, -YARD_T / 2.0, YARD_T / 2.0
    fx, fy, fw, fh = L.FENCE

    def panel_uv(k):
        rx, ry, rw, rh = L.GATE if k in gates else (fx, fy, fw, fh)
        return lambda co: (rx + (fr.s_of(co) - k * bw) / bw * rw,
                           ry + co.z / h * rh)

    for k in range(n):
        a, b = k * bw, (k + 1) * bw
        out = panel_uv(k)
        B.face([fr.P(a, 0.0, do), fr.P(b, 0.0, do), fr.P(b, h, do),
                fr.P(a, h, do)], out)
        B.face([fr.P(b, 0.0, di), fr.P(a, 0.0, di), fr.P(a, h, di),
                fr.P(b, h, di)], out)
        B.face([fr.P(a, h, do), fr.P(a, h, di), fr.P(b, h, di), fr.P(b, h, do)],
               uv_patch("cap"))
        B.face([fr.P(a, 0.0, di), fr.P(a, 0.0, do), fr.P(b, 0.0, do),
                fr.P(b, 0.0, di)], uv_patch("blank"))
    rail = uv_patch("cap")
    B.face([fr.P(0.0, 0.0, do), fr.P(0.0, 0.0, di), fr.P(0.0, h, di),
            fr.P(0.0, h, do)], rail)
    B.face([fr.P(fr.L, 0.0, di), fr.P(fr.L, 0.0, do), fr.P(fr.L, h, do),
            fr.P(fr.L, h, di)], rail)
    return B


def yard_fences(level):
    """One fence on every party line, and a gated run across the back of each
    dwelling's yard."""
    out = []
    for i in range(UNITS + 1):
        x = -HX + i * UNIT_W
        out.append((fence_run((x, YARD_FRONT), (x, YARD_BACK), (), level),
                    "tmp_fence_div%d" % i))
    # One run across the whole back rather than one per dwelling: four runs
    # would abut end to end, and a pair of coincident end caps is the one thing
    # an exact boolean resolves expensively. The gates sit in it, one per
    # dwelling, in the same bay of each. Runs -X so its outward normal faces
    # +Y, away from the dwellings.
    per = int(round(UNIT_W / L.FENCE_W))
    gates = tuple(k * per + GATE_BAY for k in range(UNITS))
    out.append((fence_run((HX, YARD_BACK), (-HX, YARD_BACK), gates, level),
                "tmp_fence_back"))
    return out


# ================================================================ assembly


def front_door_x():
    """X of each dwelling's front door. The front wall runs +X, so x = s - HX."""
    return [-HX + k * UNIT_W + L.DOOR_S for k in range(UNITS)]


def alcove_x():
    """X span of each yard alcove. The rear wall runs -X, so x = HX - s."""
    ls0, ls1 = L.ALCOVE[0], L.ALCOVE[1]
    return [(HX - (k * UNIT_W + ls1), HX - (k * UNIT_W + ls0)) for k in range(UNITS)]


def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    parts = [to_object(roof_slab(), "tmp_roof"),
             to_object(balcony_slab(), "tmp_balcony"),
             to_object(parapet(), "tmp_parapet"),
             to_object(terrace(), "tmp_terrace")]
    for i in range(UNITS + 1):
        parts.append(to_object(screen(-HX + i * UNIT_W, level),
                               "tmp_screen%d" % i))
    if level < 2:
        # A 0.18 m post is about 2.6 px across at LOD2's distance and 1.5 at
        # LOD3's, and it stands inside the roof's own projection, so dropping it
        # cannot move the plan. The parapet and the screens keep the balcony
        # reading once it is gone.
        for k in range(UNITS):
            for j, s in enumerate(POST_S):
                parts.append(to_object(post(-HX + k * UNIT_W + s),
                                       "tmp_post%d_%d" % (k, j)))
    if level < 2:
        for i, vx in enumerate(VENT_X):
            hx_, hy_, below, above = VENT
            parts.append(to_object(asset_build.open_stack(
                Builder(), vx - hx_, vx + hx_, Y_RIDGE - hy_, Y_RIDGE + hy_,
                Z_RIDGE - below, Z_RIDGE + above, FLUE_WALL, FLUE_DEPTH,
                uv_patch("cap"), uv_patch("cap"), uv_patch("flue"),
                uv_patch("blank")), "tmp_vent%d" % i))
    if level < 2:
        # A 0.31 m step is about 2 px at LOD2's distance and both flights sit
        # inside a projection every tier keeps — the roof in front, the balcony
        # behind — so dropping them cannot move the plan's extents.
        for i, xc in enumerate(front_door_x()):
            parts.append(to_object(steps(xc - STEP_W / 2.0, xc + STEP_W / 2.0,
                                         Y_FRONT, -1.0, FRONT_STEP),
                                   "tmp_step_f%d" % i))
        for i, (x0, x1) in enumerate(alcove_x()):
            parts.append(to_object(box(x0, x1, Y_REAR, Y_REAR + 0.45, 0.0,
                                       L.Z_FLOOR, "tread", "tread"),
                                   "tmp_step_r%d" % i))
    # the yard pipes hang on the posts, and go with them
    pipes = DOWNPIPES if level < 2 else FRONT_PIPES
    kit = RS.solids(ROOF_KIT, level, RS.Paint(L.ATLAS, strip=L.PIPE_STRIP),
                    extents=True, modes=kit_modes())
    bare = kit_modes()[level][0] is None             # the rails alone, clear of all
    for B, name in yard_fences(level) + DP.solids(
            pipes, *DP.MODES[level], L.PIPE_STRIP, L.ATLAS) + ([] if bare else kit):
        parts.append(to_object(B, name))
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # 1e-4 rather than 1e-5. The exact boolean resolves this row's 30 m eave
    # lines in 32-bit floats and leaves the odd corner vertex a hundredth of a
    # millimetre off its neighbour: enough to export as two vertices and read as
    # a non-manifold seam downstream. The smallest authored feature here is the
    # window casing's 0.10 m, so a 0.1 mm weld cannot reach anything real.
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # Recover the cost of coplanar boolean subdivisions. Keep UV and material
        # seams and every architectural edge. 0.001 radians tolerates float noise
        # on nominally planar faces.
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


# ================================================================== checks
def check_layout():
    """Assert the constraints that are invisible in the numbers and obvious once
    rendered: openings colliding, leaving their cladding panel or straddling a
    storey; the gable outgrowing its atlas band; the roof missing the balcony it
    is supposed to cover; a screen poking through the roof."""
    p = []
    if abs(L.BAY_H_REAR - roof_under(Y_REAR)) > 1e-4:
        p.append("facade_atlas.BAY_H_REAR is %.4f, the rear wall tops out at %.4f"
                 % (L.BAY_H_REAR, roof_under(Y_REAR)))
    for name, run in (("front", (Y_RIDGE - Y_ROOF_F) * math.sqrt(1 + TAN_F ** 2)),
                      ("rear", (Y_ROOF_R - Y_RIDGE) * math.sqrt(1 + TAN_R ** 2))):
        if run > L.ROOF_SLOPE_LEN:
            p.append("the %s slope is %.3f m, past the roof band's %.3f"
                     % (name, run, L.ROOF_SLOPE_LEN))
    if roof_under(Y_REAR) - L.Z_STOREY > L.WOOD_H / PPM:
        p.append("the upper storey outgrows the siding band")
    if Z_APEX - L.Z_STOREY > L.BRICK_H / PPM:
        p.append("the gable apex outgrows the brick band")
    if (Y_ROOF_R - Y_REAR) * PPM > L.WOOD_H:
        p.append("the balcony ceiling outgrows the siding band")
    if (Y_FRONT - Y_ROOF_F) * PPM > L.SOF_H:
        p.append("the street eave outgrows the soffit band")
    if Y_ROOF_R < Y_BALC + 0.2:
        p.append("the roof does not reach past the balcony's parapet")
    if roof_under(Y_BALC) - Z_DECK < 2.2:
        p.append("headroom over the balcony is under 2.2 m")
    if L.Z_STOREY - 0.08 < 2.4:
        p.append("headroom on the covered terrace is under 2.4 m")
    if max(d for d, _ in FRONT_STEP) > Y_FRONT - Y_ROOF_F:
        p.append("the entrance step reaches past the eave, so dropping it at "
                 "LOD3 would move the plan's front edge")
    # Everything that runs up into the roof has to stop inside the slab: above
    # its soffit, so the union trims it there, and below its top surface, so it
    # does not stand proud of the roof. Checked for every such solid rather
    # than for the screens alone.
    for label, y, zt in (
            ("the front wall", Y_FRONT, Z_TOP_FRONT),
            ("the rear wall", Y_REAR, Z_TOP_REAR),
            ("the body's lid", Y_RIDGE, Z_APEX),
            ("a gable wall", Y_FRONT + 2.0,
             roof_under(Y_FRONT + 2.0) + L.WALL_INTO_ROOF),
            ("a balcony screen", Y_REAR - 0.10, roof_under(Y_REAR - 0.10) + 0.30),
            ("a balcony screen", Y_SCREEN, roof_under(Y_SCREEN) + 0.14),
            ("a terrace post", Y_POST, roof_under(Y_POST) + 0.12)):
        if not roof_under(y) < zt < roof_under(y) + ROOF_T:
            p.append("%s tops out at %.3f, outside the roof slab's %.3f..%.3f "
                     "at y=%.2f" % (label, zt, roof_under(y),
                                    roof_under(y) + ROOF_T, y))
    if YARD_FRONT > Y_SCREEN - 0.05:
        p.append("a party fence meets the terrace screen face to face instead "
                 "of running into it")
    for run, label in (((YARD_BACK - YARD_FRONT), "a yard's party fence"),
                       ((UNIT_W), "a yard's back fence")):
        if abs(run / L.FENCE_W - round(run / L.FENCE_W)) > 1e-6:
            p.append("%s is %.3f m, not a whole number of %.2f m bays"
                     % (label, run, L.FENCE_W))
    if not 0 <= GATE_BAY < round(UNIT_W / L.FENCE_W):
        p.append("the yard gate is not in one of the back fence's bays")
    if abs(GATE_BAY + 0.5 - round(UNIT_W / L.FENCE_W) / 2.0) < 0.4:
        p.append("the yard gate is in the middle of the back fence")

    lw, lh = L.OPENINGS["door_front"][0], L.OPENINGS["door_front"][1]
    if not 2.0 <= lh <= 2.4:
        p.append("the front door's leaf is %.2f m, outside 2.0-2.4 m" % lh)
    if L.GF_SILL - L.Z_FLOOR > 1.4 or L.UP_SILL - L.Z_STOREY > 1.4:
        p.append("a window sill sits above chest height over its own floor")

    # every opening inside its cladding panel and its storey, and clear of its
    # neighbours; the alcove likewise
    for name, spec in MAIN_WALLS.items():
        fr = Frame(spec["p0"], spec["p1"])
        for idx, (panels, items) in enumerate(zip(spec["panels"], spec["items"])):
            zlo, zhi = STOREY_Z[idx + 1], (STOREY_Z[2] if idx == 0 else None)
            rects = [(k, item_rects(k, s, z)[0]) for k, s, z in items]
            for base in (spec["alcoves"] if idx == 0 else ()):
                a0, a1, az0, az1, _d = L.ALCOVE
                rects.append(("alcove", (base + a0, base + a1, az0, az1)))
            for kind, r in rects:
                top = spec["top"](r[0]) if zhi is None else zhi
                if r[2] < zlo - EPS or r[3] > top - 0.05:
                    p.append("%s: %s at s %.2f leaves its storey (%.2f..%.2f)"
                             % (name, kind, r[0], r[2], r[3]))
                if not any(s0 - EPS < r[0] and r[1] < s1 + EPS
                           for s0, s1, _ in panels):
                    p.append("%s: %s at s %.2f..%.2f crosses a cladding panel "
                             "boundary" % (name, kind, r[0], r[1]))
                if r[0] < 0.05 or r[1] > fr.L - 0.05:
                    p.append("%s: %s runs off the wall" % (name, kind))
            for i in range(len(rects)):
                for j in range(i + 1, len(rects)):
                    a, b = rects[i][1], rects[j][1]
                    if a[0] < b[1] + 0.03 and b[0] < a[1] + 0.03 and \
                            a[2] < b[3] + 0.03 and b[2] < a[3] + 0.03:
                        p.append("%s: %s at %.2f and %s at %.2f overlap"
                                 % (name, rects[i][0], a[0], rects[j][0], b[0]))
    front_win = [k for k, _s, _z in L.FRONT_UNIT if k.startswith("win")]
    if len(front_win) != 4:
        p.append("%d front windows per dwelling, not four" % len(front_win))
    d = L.ALCOVE[4]
    dw = L.OPENINGS["door_glazed"][0] + 2 * L.OPENINGS["door_glazed"][2]
    if not 0.05 < L.ALCOVE_DOOR_S - dw / 2.0 and L.ALCOVE_DOOR_S + dw / 2.0 < d - 0.05:
        p.append("the yard door does not fit the alcove's side wall")
    # downpipes: the street ones on their piers, clear of the windows and the
    # doors' steps; the yard ones clear of the parapet and under the eave
    front = [(k,) + item_rects(k, c, z)[0][:2] for k, c, z in row_items(L.FRONT_UNIT)]
    front += [("step", x + HX - STEP_W / 2.0, x + HX + STEP_W / 2.0)
              for x in front_door_x()]
    for pipe in FRONT_PIPES:
        name = "the street downpipe at s %.2f" % pipe.s
        p += DP.problems(pipe, name, front)
        if not any(s0 + DP.A < pipe.s < s1 - DP.A for s0, s1, band in FRONT_GF
                   if band == "brick"):
            p.append("%s is off its brick pier" % name)
    if Y_POST + POST + DP.GAP < Y_BALC + 0.1:
        p.append("the yard downpipes crowd the balcony's parapet")
    if Y_POST + POST + DP.OUT + DP.A > Y_ROOF_R - 0.04:
        p.append("the yard downpipes stand out past the gutter")
    # the roof kit: the wall ladder on the blank gable clear of its corners
    # and under the rake; the roof ladder inside the rake and clear of the
    # vents; the walkway just behind the vents and running past the last one
    wall, roof, walk = ROOF_KIT
    p += RS.problems(wall, "the gable ladder", [])
    if roof.s + RS.HALF > 2.0 * HX - 0.20:
        p.append("the roof ladder is not inside the west rake")
    if any(abs(HX - roof.s - vx) < VENT[0] + RS.HALF + 0.3 for vx in VENT_X):
        p.append("the roof ladder runs into a vent")
    y_hi = Y_REAR + walk.out_hi                      # its upslope edge, in y
    if not Y_RIDGE + VENT[1] + 0.02 < y_hi < Y_RIDGE + VENT[1] + 0.30:
        p.append("the walkway's edge is not just behind the vents")
    if walk.s0 > HX - VENT_X[1] - VENT[0]:
        p.append("the walkway stops short of the east vent")
    if VENT[3] - FLUE_DEPTH < 0.05:
        p.append("a vent's flue floor is down in the roof slab")
    return p


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame.

    The footprint is the heated block's outer wall at ground level, so it
    turns in round each yard alcove: the pocket is open to the yard from the
    floor up, and its side wall, which carries the yard door, is outer wall.
    That door is given where it stands, facing along the row into its pocket.
    The roof, the balconies and their posts, the terrace paving, the steps,
    the yard fences and the gable ladder are left out; a fence gate is not a
    door. The ground storey is the plate less the alcoves, the upper storey
    the whole plate: the roof's underside is 3.0 m or more over it at both
    walls. The balcony doors are doors in an outer wall and are listed, at
    the upper floor's level.
    """
    front, rear = MAIN_WALLS["front"], MAIN_WALLS["rear"]
    fr = Frame(rear["p0"], rear["p1"])
    ls0, ls1, _z0, _z1, depth = L.ALCOVE
    glazed = L.OPENINGS["door_glazed"][:2]

    def unit(k):
        """The dwelling, counted from the west, of the rear wall's bay *k*,
        which that wall counts from its start at the east end."""
        return UNITS - k

    footprint = [(-HX, Y_FRONT), (HX, Y_FRONT), (HX, Y_REAR)]
    for k in range(UNITS):
        s0, s1 = k * UNIT_W + ls0, k * UNIT_W + ls1
        footprint += [fr.P(s0, 0.0)[:2], fr.P(s0, 0.0, depth)[:2],
                      fr.P(s1, 0.0, depth)[:2], fr.P(s1, 0.0)[:2]]
    footprint.append((-HX, Y_REAR))

    doors = []
    for k in range(UNITS):
        doors.append(model_facts.wall_door(
            "unit_%d" % (k + 1), "entrance", front["p0"], front["p1"],
            k * UNIT_W + L.DOOR_S,
            L.Z_FLOOR, *L.OPENINGS["door_front"][:2]))
    # the entrance a visitor uses: the unit just to the +X side of the centre
    doors[UNITS // 2]["main"] = True
    for k in reversed(range(UNITS)):
        # the alcove's far side wall, as build_alcove() frames it
        s1 = k * UNIT_W + ls1
        doors.append(model_facts.wall_door(
            "unit_%d_back" % unit(k), "service", fr.P(s1, 0.0, depth)[:2],
            fr.P(s1, 0.0)[:2],
            depth - L.ALCOVE_DOOR_S, L.Z_FLOOR, *glazed))
    for k in reversed(range(UNITS)):
        for kind, s, z in L.REAR_UP_UNIT:
            if kind == "door_glazed":
                doors.append(model_facts.wall_door(
                    "unit_%d_balcony" % unit(k), "balcony", rear["p0"], rear["p1"],
                    k * UNIT_W + s, z, *glazed))
    plate = 2 * HX * (Y_REAR - Y_FRONT)
    return {
        "hero": False,
        "dwellings": UNITS,
        "footprint": footprint,
        "storeys": [(L.Z_FLOOR, plate - UNITS * (ls1 - ls0) * depth),
                    (L.Z_STOREY, plate)],
        "doors": doors,
    }


# ================================================================ previews


def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four orthographic
    elevations, a plan from above, and a raised three-quarter aerial off the
    front corner. Working views only — not committed."""
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
    # raised three-quarter, 45 degrees up, off the front-right corner, and the
    # same from behind: this type's yard elevation is the one with the balcony
    for name, d in (("aerial", Vector((1.0, -1.0, math.sqrt(2.0)))),
                    ("aerial_rear", Vector((-1.0, 1.0, math.sqrt(2.0))))):
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
    BUILD.main(build_all, facts)
