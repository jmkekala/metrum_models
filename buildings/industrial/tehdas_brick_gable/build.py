# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of tehdas_brick_gable, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite Finnish light-industrial building of the kind put up on a town's
edge from the 1970s on: workshop below, offices above, in facing brick under a
shallow profiled-steel gable. The main block is 42 x 12 m and two storeys, with
long ribbon windows in white frames on both floors. Two single-storey wings
with dark felt roofs are built onto its long sides: one on the front beside the
main entrance, which is set back into a lobby under a flat canopy, and a larger
one behind.

At the east end the ground storey stops 3 m short of the gable and the upper
storey runs on over four concrete pillars, sheltering the second entrance. At
the west end the gable carries a sectional loading door and a personnel door,
and the front wall a stair lit by one tall strip of glazing, with its own door
under a canopy. Ladders climb from the ground to each wing's roof, and from the
front wing's roof up the main wall past the eave, where a roof ladder carries
on up the slope to the ridge. Vent pipes stand on both slopes.

Construction is a set of closed solids unioned with Blender's exact boolean:
the main block's wall ring, the gable roof slab, each wing's wall ring and its
parapeted roof slab, the pillars, the canopies, the ladders and the vents.
Each is simple on its own; the union trims the wall tops into the roofs, the
wings into the block and the pillars into the upper floor, and leaves the
boundary of one empty volume, so interior geometry cannot occur. The main
ring is capped at the top by two planar faces split at the ridge, since its
rim follows both gables.

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
from asset_build import bounds as _bounds, pivot_offset, to_object, union  # noqa: E402,F401
import downpipes as DP  # noqa: E402
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
HX, HY = L.HX, L.HY                     # 21 x 6: a 42 x 12 m block
PX = L.PORCH_X                          # the ground storey's east wall
XE = HX + L.RAKE_OUT                    # the roof's own extent
PE = HY + L.EAVE_OUT
Z_APEX = L.Z_EAVE + HY * L.TAN + L.WALL_INTO_ROOF      # gable wall top, in the slab


def roof_under(y):
    """The gable roof's underside over plan position *y*."""
    return L.Z_EAVE + (HY - abs(y)) * L.TAN


def gtop(s, span=2.0 * HY):
    """Where a gable wall stops, *s* along it: inside the roof slab."""
    return L.Z_WALL_TOP + min(s, span - s) * L.TAN


# Openings, per wall, as (kind, centre along the wall in plan x or y, sill z).
# The ribbon windows keep one 6 m rhythm on both floors of both long walls;
# ground-storey openings stop where a wing or the porch buries the wall.
UP, GF = L.Z_SILL_UP, L.Z_SILL
FRONT_ITEMS = (
    [("stair", -18.5, L.Z_STAIR), ("glazed_door", -18.5, 0.0)]
    + [("ribbon4", x, UP) for x in (-12.0, -6.0, 0.0, 6.0, 12.0, 18.0)]
    + [("ribbon4", x, GF) for x in (-12.0, -6.0, 0.0)]
    + [("entrance", 6.5, 0.0)])
REAR_ITEMS = (
    [("ribbon4", x, UP) for x in (18.0, 12.0, 6.0, 0.0, -6.0, -12.0, -18.0)]
    + [("ribbon4", x, GF) for x in (0.0, -6.0, -12.0, -18.0)]
    + [("service_door", 3.5, 0.0)])
WEST_ITEMS = [("loading_door", 1.5, 0.0), ("service_door", -3.5, 0.0),
              ("ribbon4", 0.0, UP)]
EAST_ITEMS = [("ribbon4", 0.0, UP)]
PORCH_ITEMS = [("entrance", -1.5, 0.0), ("ribbon2", 3.0, GF)]
LOBBY = "entrance"          # the front entrance's kind; the porch's is shallow

# Pillars under the east end's upper storey: 0.40625 m square, their outer
# faces 0.15 m inside the upper walls, evenly across the gable.
PILLAR_IN = 0.15
PILLAR_X = HX - PILLAR_IN - L.PILLAR_W / 2.0
_py = HY - PILLAR_IN - L.PILLAR_W / 2.0
PILLAR_Y = [-_py + 2.0 * _py * k / 3.0 for k in range(4)]
PILLAR_TOP = L.Z_PORCH + 0.125

# Canopies: (centre x, width, projection) on the front wall.
CANOPIES = [(6.5, 4.0, 1.2), (-18.5, 2.0, 1.0)]
CANOPY_BURY = 0.1

# The wings: each wall as (name, p0, p1, items), walked counter-clockwise from
# above so the outward face is on the right. The side that meets the block is
# a wall like the others, WING_BURY inside it, which the union removes.
FW, BW, WB = L.FRONT_WING, L.BACK_WING, L.WING_BURY
FRONT_WING_WALLS = [
    ("fw_west", (FW[0], FW[3] + WB), (FW[0], FW[2]), []),
    ("fw_front", (FW[0], FW[2]), (FW[1], FW[2]), [("ribbon4", 13.2, GF)]),
    ("fw_east", (FW[1], FW[2]), (FW[1], FW[3] + WB), [("service_door", -9.4, 0.0)]),
    ("fw_back", (FW[1], FW[3] + WB), (FW[0], FW[3] + WB), []),
]
BACK_WING_WALLS = [
    ("bw_south", (BW[0], BW[2] - WB), (BW[1], BW[2] - WB), []),
    ("bw_east", (BW[1], BW[2] - WB), (BW[1], BW[3]),
     [("service_door", 8.2, 0.0), ("ribbon2", 11.8, GF)]),
    ("bw_north", (BW[1], BW[3]), (BW[0], BW[3]),
     [("ribbon4", 14.267, GF), ("ribbon4", 9.133, GF)]),
    ("bw_west", (BW[0], BW[3]), (BW[0], BW[2] - WB), [("ribbon4", 11.5, GF)]),
]

# Ladders. Their shape is scripts/roof_safety.py's; the places are this
# building's. Wall ladders stand off on brackets; the roof ladder's rails are
# bedded into the sheet, as they were before the shared kit stood roof ladders
# off on brackets.
WALL_LADDER_X = 15.0        # the front wing's roof to the main eave, between
                            # the upper windows at 12 and 18
FW_LADDER_Y = -7.3          # ground to the front wing's roof
BW_LADDER_Y = 15.4          # ground to the back wing's roof
LADDER_TOP = RS.LADDER_TOP  # rails run on this far above what they reach
LADDER_HANG = 0.15          # the wall ladder ends this far above the deck
EAVE_CLEAR = RS.EAVE_CLEAR  # the wall ladder passes this far outside the eave

# Vent pipes on the slopes: (x, y, diameter, height above the sheet).
VENTS = [(-15.0, -1.4, 0.30, 0.90), (-4.5, -1.1, 0.16, 0.50),
         (8.0, -1.6, 0.50, 1.10), (-9.0, 1.3, 0.50, 1.10),
         (1.5, 1.5, 0.30, 0.90), (12.5, 1.2, 0.16, 0.50),
         (-18.0, 1.0, 0.16, 0.50)]


# ----------------------------------------------------------------- tiers
def opening_mode(level):
    """LOD0/1 cut every opening into its wall with brick reveals; LOD2/3 paint
    the same rectangle flat. The 0.15-0.25 m reveals are under a pixel past
    70 m, and the window rhythm is the painted rectangle's to keep."""
    return "cut" if level < 2 else "flush"


def lobby_kept(level):
    """The entrance lobby is 1.5 m deep and 3 m wide: a real hole in the front
    at every distance, and three faces, so it stays on every tier."""
    return True


def canopy_kept(level, i):
    """The canopies are 0.19 m slabs projecting 1-1.2 m, light against the
    brick. They are the only light marks on the front's ground storey and
    say where the ways in are; at 120 m the stair door's is still a 15 px
    mark, and dropping it was the one change left at that switch. Both stay
    on every tier, at 16 triangles each."""
    return True


def ladder_mode(level):
    """How many of LOD0's rungs a tier keeps: every one, every other, every
    fourth, then no ladder at all.

    Rungs are 3 cm, under a pixel past 35 m, but their rhythm and their
    shadows on the sheet still read at 35 m, and from above at 70 m the roof
    ladder is still a hatched strip and the wall ladder a line standing over
    the eave. Each time a tier dropped them outright the ladders visibly
    vanished at the switch, so each tier thins them instead, keeping rungs
    only where the tier before has them. Past 120 m the rails are under half
    a pixel and the ladders go. These are roof_safety.MODES, which took them
    from here.
    """
    return RS.MODES[level][0]


def vent_sides(level, dia):
    """Pipes break the ridge line from any raised view: eight sides up close,
    six to 70 m. At 70 m the 0.3 m pipes still stand 3.5 x 10 px over the
    ridge in a front view and dropping them was visible, so they carry to
    LOD2 as four-sided stacks with the 0.5 m exhausts; the 0.16 m ones are
    under two pixels wide and go. Past 120 m only the exhausts remain, 3 x 7
    px of black over the ridge, and what says this roof is ventilated."""
    if level == 0:
        return 8
    if level == 1:
        return 6
    if level == 2:
        return 4 if dia >= 0.25 else 0
    return 4 if dia >= 0.45 else 0


def downpipe_mode(level):
    """(sides, bent) of the downpipes at each tier: scripts/downpipes.py's
    MODES, except that LOD3 drops them. It has 12 triangles to spare and the
    eight straight pipes would cost about 70, so past 120 m, where a pipe is
    under a pixel, they go.
    """
    return DP.MODES[level] if level < 3 else (0, False)


def bays_merged(level):
    """LOD3 paints what stands one above the other on the front and rear as
    one quad over a region that carries both and the brick between: each
    bay's two ribbon windows (L.LOD3_BAY), and the stair's door and glazing
    (L.LOD3_STAIR). Eight pairs at about eight triangles each are what pay
    for keeping the exhausts and both canopies on the last tier."""
    return level >= 3


def storey_pairs(items, level):
    """*items* with each such pair on one centre line replaced by its single
    LOD3 quad, when bays_merged(level)."""
    if not bays_merged(level):
        return items
    gf = {c for k, c, z in items if k == "ribbon4" and z == GF}
    up = {c for k, c, z in items if k == "ribbon4" and z == UP}
    both = gf & up
    stair = ({c for k, c, z in items if k == "stair"}
             & {c for k, c, z in items if k == "glazed_door"})
    out = [(k, c, z) for k, c, z in items
           if not (k == "ribbon4" and c in both)
           and not (k in ("stair", "glazed_door") and c in stair)]
    return (out + [("lod3_bay", c, GF) for c in sorted(both)]
            + [("lod3_stair", c, 0.0) for c in sorted(stair)])


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
        # Area vector (Newell) from coordinates relative to the first vertex, in
        # double precision; summed from absolute positions in 32-bit floats a
        # zero-area face keeps enough rounding to pass as real.
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


def uv_reveal(fr, edge, u_off):
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
                L.BRICK_Y0 + (co.z + nz * d) * PPM)
    return f


def uv_window(fr, s0, z0):
    """The ribbon-window band, its first cell at the window's left jamb."""
    return lambda co: ((fr.s_of(co) - s0) * PPM, L.WIN_Y0 + (co.z - z0) * PPM)


def uv_region(fr, rect, s0, z0, ppm=PPM):
    x, y, w, h = rect
    return lambda co: (x + (fr.s_of(co) - s0) * ppm, y + (co.z - z0) * ppm)


def uv_closing(fr, kind, s0, z0):
    if kind.startswith("ribbon"):
        return uv_window(fr, s0, z0)
    return uv_region(fr, L.REGION[kind], s0, z0, L.REGION_PPM.get(kind, PPM))


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


def build_opening(B, fr, kind, rect, level, u_off, depth):
    """One opening: brick reveals round it and the closing plane set back in
    it while it is cut, the same rectangle painted flat after. Returns its
    outline in (s, z), which the wall region takes as a hole or a notch.

    An opening on the ground gets no cheek along its threshold: the strip
    would lie at z = 0 inside the building's footprint, on top of the floor
    the wall ring is capped with, and the two coplanar faces would leave the
    export non-manifold at the doorway. Left out, the rim detours round the
    recess and the floor cap covers it.
    """
    s0, s1, z0, z1 = rect
    poly = [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]
    closing = uv_closing(fr, kind, s0, z0)
    if opening_mode(level) == "flush" and not (kind == LOBBY and depth > 1.0
                                               and lobby_kept(level)):
        B.face([fr.P(s, z) for s, z in poly], closing)
        return poly
    for k, edge in enumerate(zip(poly, poly[1:] + poly[:1])):
        (a0, b0), (a1, b1) = edge
        if k == 0 and z0 < EPS:
            continue
        if k == 0:
            fn = uv_patch("sill")
        elif k == 2 and depth > 1.0:
            fn = uv_patch("ceiling")
        else:
            fn = uv_reveal(fr, edge, u_off)
        B.face([fr.P(a0, b0), fr.P(a1, b1), fr.P(a1, b1, -depth),
                fr.P(a0, b0, -depth)], fn)
    B.face([fr.P(s, z, -depth) for s, z in poly], closing)
    return poly


def wall_region(B, fr, outline, items, level, u_off, uvfn, lobby=None):
    """One planar region of wall: every opening inside it built and holed.

    Openings standing on the region's foot are notches in *outline* already
    (see outline_with_notches); the rest are holes.
    """
    holes = []
    for kind, rect in items:
        depth = L.LOBBY_DEPTH if (lobby is not None and kind == lobby) else L.REVEAL[kind]
        poly = build_opening(B, fr, kind, rect, level, u_off, depth)
        if rect[2] > EPS:
            holes.append(poly)
    fill_region(B, fr, outline, holes, uvfn)


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


# ------------------------------------------------------------- main block
MAIN_WALLS = {
    # name: (p0, p1); u offsets run on round the corners so the bond continues
    "front": ((-HX, -HY), (HX, -HY)),
    "east": ((HX, -HY), (HX, HY)),
    "rear": ((HX, HY), (-HX, HY)),
    "west": ((-HX, HY), (-HX, -HY)),
    "porch": ((PX, -HY), (PX, HY)),
}
U_OFF = {"front": 0.0, "east": 2 * HX, "rear": 2 * HX + 2 * HY,
         "west": 4 * HX + 2 * HY, "porch": 2 * HX - 3.0}


def build_front(B, level):
    fr = Frame(*MAIN_WALLS["front"])
    items = rects_for(fr, storey_pairs(FRONT_ITEMS, level))
    uo = U_OFF["front"]
    L_ = fr.L
    sp = fr.s_at(PX)                                # 39: the porch's corner
    notches = [(r[0], r[1], r[3]) for k, r in items if r[2] < EPS]
    foot = outline_with_notches(0.0, sp, 0.0, notches)
    outline = foot + [(sp, L.Z_PORCH), (L_, L.Z_PORCH), (L_, L.Z_GABLE),
                      (L_, L.Z_WALL_TOP), (0.0, L.Z_WALL_TOP), (0.0, L.Z_GABLE)]
    wall_region(B, fr, outline, items, level, uo, uv_brick(fr, uo), lobby=LOBBY)


def build_rear(B, level):
    fr = Frame(*MAIN_WALLS["rear"])
    items = rects_for(fr, storey_pairs(REAR_ITEMS, level))
    uo = U_OFF["rear"]
    L_ = fr.L
    sp = fr.s_at(PX)                                # 3
    notches = [(r[0], r[1], r[3]) for k, r in items if r[2] < EPS]
    foot = outline_with_notches(sp, L_, 0.0, notches)
    outline = foot + [(L_, L.Z_GABLE), (L_, L.Z_WALL_TOP), (0.0, L.Z_WALL_TOP),
                      (0.0, L.Z_GABLE), (0.0, L.Z_PORCH), (sp, L.Z_PORCH)]
    wall_region(B, fr, outline, items, level, uo, uv_brick(fr, uo))


def build_gable(B, name, z_foot, items_spec, level):
    """A gable end: the wall up to Z_GABLE with its openings, then the
    triangle above, which samples the brick band GABLE_SHIFT lower down."""
    fr = Frame(*MAIN_WALLS[name])
    items = rects_for(fr, items_spec)
    uo = U_OFF[name]
    L_ = fr.L
    notches = [(r[0], r[1], r[3]) for k, r in items if r[2] < z_foot + EPS]
    foot = outline_with_notches(0.0, L_, z_foot, notches)
    outline = foot + [(L_, L.Z_GABLE), (0.0, L.Z_GABLE)]
    wall_region(B, fr, outline, items, level, uo, uv_brick(fr, uo))
    tri = [(0.0, L.Z_GABLE), (L_, L.Z_GABLE), (L_, L.Z_WALL_TOP),
           (L_ / 2.0, gtop(L_ / 2.0)), (0.0, L.Z_WALL_TOP)]
    fill_region(B, fr, tri, [], uv_brick(fr, uo, L.GABLE_SHIFT))


def build_porch(B, level):
    """The ground storey's east wall, 3 m in from the gable, and the soffit
    of the upper storey that runs on over it to the pillars."""
    fr = Frame(*MAIN_WALLS["porch"])
    items = rects_for(fr, PORCH_ITEMS)
    uo = U_OFF["porch"]
    notches = [(r[0], r[1], r[3]) for k, r in items if r[2] < EPS]
    foot = outline_with_notches(0.0, fr.L, 0.0, notches)
    outline = foot + [(fr.L, L.Z_PORCH), (0.0, L.Z_PORCH)]
    wall_region(B, fr, outline, items, level, uo, uv_brick(fr, uo))
    z = L.Z_PORCH
    B.face([(PX, -HY, z), (PX, HY, z), (HX, HY, z), (HX, -HY, z)],
           uv_patch("soffit"))


def cap_ring(B, split=None, lid=None):
    """Cap a wall ring: a floor on the ground and a lid at the wall top.

    Both end up buried - the floor on the ground, the lid inside the roof -
    but the solid must be closed for the boolean to be exact. *split* is a
    pair of rim positions the lid is cut between, for a rim that follows a
    gable and so is not planar; *lid* maps a lid that is seen, not buried. The rim is walked by hand rather than with
    bmesh's holes_fill, which silently skips a loop whose vertices already
    carry a face; walked in edge-index order, so the caps start on the same
    vertex every run.
    """
    bm = B.bm
    bm.edges.index_update()
    order = [e for e in bm.edges if len(e.link_faces) == 1]
    rim = set(order)
    branch = [v for e in order for v in e.verts
              if sum(1 for x in v.link_edges if x in rim) != 2]
    if branch:
        c = branch[0].co
        raise ValueError("a wall ring's rim branches at %d vertices, e.g. "
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
        raise ValueError("expected a floor and a lid, got %d holes: a wall "
                         "ring has a T-junction somewhere" % len(loops))
    blank = uv_patch("blank")
    floor = min(loops, key=lambda lp: max(v.co.z for v in lp))
    top = next(lp for lp in loops if lp is not floor)
    B.set_uv(bm.faces.new(floor), blank)
    if split is None:
        B.set_uv(bm.faces.new(top), lid or blank)
        return
    keys = [B.v(p) for p in split]
    i, j = sorted(top.index(v) for v in keys)
    for half in (top[i:j + 1], top[j:] + top[:i + 1]):
        B.set_uv(bm.faces.new(half), blank)


def main_body(level):
    B = Builder()
    build_front(B, level)
    build_gable(B, "east", L.Z_PORCH, EAST_ITEMS, level)
    build_rear(B, level)
    build_gable(B, "west", 0.0, WEST_ITEMS, level)
    build_porch(B, level)
    cap_ring(B, split=[(HX, 0.0, Z_APEX), (-HX, 0.0, Z_APEX)])
    return B


# ------------------------------------------------------------------ wings
def wing_box(level):
    """LOD3 draws each wing as one box: brick to the slab's underside, the
    fascia's flashing on the wall above it to the coping's height, and a lid
    painted with the coping's light edge. The parapet and the 0.125 m
    oversail are about a pixel at 120 m and cost more than the rest of the
    wing put together."""
    return level >= 3


def wing_body(walls, level, lid=None):
    """A single-storey wing's wall ring, capped flat inside its roof slab, or
    at LOD3 (wing_box) capped by its own painted lid *lid*."""
    B = Builder()
    uo = 0.0
    boxed = wing_box(level)
    top = L.Z_COPE if boxed else L.Z_WING_WALL
    for name, p0, p1, spec in walls:
        fr = Frame(p0, p1)
        items = rects_for(fr, spec)
        notches = [(r[0], r[1], r[3]) for k, r in items if r[2] < EPS]
        foot = outline_with_notches(0.0, fr.L, 0.0, notches)
        zb = L.Z_WING_SOF if boxed else top
        outline = foot + [(fr.L, zb), (0.0, zb)]
        wall_region(B, fr, outline, items, level, uo, uv_brick(fr, uo))
        if boxed:
            fill_region(B, fr, [(0.0, zb), (fr.L, zb), (fr.L, top), (0.0, top)],
                        [], lambda co, fr=fr: (fr.s_of(co) * PPM,
                                               L.FLASH_Y0 + (co.z - zb) * PPM))
        uo += fr.L
    cap_ring(B, lid=lid if boxed else None)
    return B


def uv_lod3_lid(wing, rect, side):
    """The whole wing, wall face to wall face and on into the block, at
    LOD3_PPM from its plan's lower-left corner."""
    x0, x1, y0, y1 = wing
    ylo = y0 if side < 0 else y0 - L.WING_BURY
    x, y, w, h = rect
    return lambda co: (x + (co.x - x0) * L.LOD3_PPM, y + (co.y - ylo) * L.LOD3_PPM)


def uv_flash(axis, z0):
    """The flashing band, U along the edge, V from the fascia's foot."""
    return lambda co: ((co.x if axis == "x" else co.y) * PPM,
                       L.FLASH_Y0 + (co.z - z0) * PPM)


def uv_deck(x0, y0):
    x, y, w, h = L.DECK
    return lambda co: (x + (co.x - x0) * L.DECK_PPM, y + (co.y - y0) * L.DECK_PPM)


def wing_roof(wing, side):
    """A wing's flat roof as one closed solid: the felt deck inside a low
    parapet, its coping, and the fascia and soffit where it oversails the
    walls. *side* is -1 for a wing on the front, +1 behind: its open end runs
    WING_BURY into the block, where the union trims it at the wall.

    Built in plan as a U of coping round the deck, so the deck and the
    parapet's inner faces meet the coping on shared vertices.
    """
    x0, x1, y0, y1 = wing
    o, p = L.WING_OVER, L.PARAPET
    zb, zd, zc = L.Z_WING_SOF, L.Z_DECK, L.Z_COPE
    if side < 0:                        # front wing: open end at y1 (the block)
        yo_far, yi_far, y_end = y0 - o, y0 + p, y1 + L.WING_BURY
    else:                               # back wing: open end at y0
        yo_far, yi_far, y_end = y1 + o, y1 - p, y0 - L.WING_BURY
    xo0, xo1, xi0, xi1 = x0 - o, x1 + o, x0 + p, x1 - p
    B = Builder()
    # ring corners in plan, counter-clockwise from above for the front wing
    outer = [(xo0, y_end), (xo0, yo_far), (xo1, yo_far), (xo1, y_end)]
    inner = [(xi0, y_end), (xi0, yi_far), (xi1, yi_far), (xi1, y_end)]
    if side > 0:
        outer, inner = outer[::-1], inner[::-1]
    coping, blank = uv_patch("coping"), uv_patch("blank")
    # coping: three quads round the deck, split at the inner corners' lines
    far_o = [outer[1], outer[2]]
    far_i = [inner[1], inner[2]]
    B.face([(outer[0][0], outer[0][1], zc), (inner[0][0], inner[0][1], zc),
            (far_i[0][0], far_i[0][1], zc), (far_o[0][0], far_o[0][1], zc)], coping)
    B.face([(far_o[0][0], far_o[0][1], zc), (far_i[0][0], far_i[0][1], zc),
            (far_i[1][0], far_i[1][1], zc), (far_o[1][0], far_o[1][1], zc)], coping)
    B.face([(far_o[1][0], far_o[1][1], zc), (far_i[1][0], far_i[1][1], zc),
            (inner[3][0], inner[3][1], zc), (outer[3][0], outer[3][1], zc)], coping)
    # the parapet's inner faces and the deck
    for a, b in zip(inner, inner[1:]):
        axis = "y" if abs(a[0] - b[0]) < EPS else "x"
        B.face([(a[0], a[1], zc), (a[0], a[1], zd), (b[0], b[1], zd),
                (b[0], b[1], zc)], uv_patch("parapet_in"))
    B.face([(x, y, zd) for x, y in inner], uv_deck(xi0, min(y_end, yi_far)))
    # the fascia round the three oversailing sides, and the soffit
    for a, b in zip(outer, outer[1:]):
        axis = "y" if abs(a[0] - b[0]) < EPS else "x"
        B.face([(a[0], a[1], zb), (a[0], a[1], zc), (b[0], b[1], zc),
                (b[0], b[1], zb)], uv_flash(axis, zb))
    B.face([(x, y, zb) for x, y in outer], uv_patch("soffit"))
    # the open end, inside the block: an eight-sided section through it
    end = [(outer[0][0], zb), (outer[0][0], zc), (inner[0][0], zc),
           (inner[0][0], zd), (inner[3][0], zd), (inner[3][0], zc),
           (outer[3][0], zc), (outer[3][0], zb)]
    B.face([(x, y_end, z) for x, z in end], blank)
    return B


# ================================================================== roof
def uv_roof(co):
    d = (PE - abs(co.y)) * L.SLOPE_F
    return ((co.x + XE) * PPM, L.ROOF_Y0 + d * L.ROOF_RPM)


def uv_eave(co):
    zt = roof_under(PE)
    return ((co.x + XE) * PPM, L.EAVE_Y0 + (co.z - zt) * PPM)


def gable_slab():
    """The main roof as one closed slab: a chevron section extruded along the
    ridge. Its underside meets the side walls' faces at Z_EAVE, so once it is
    unioned with the block the part outside the walls is the eave and rake
    soffit and the part inside disappears. The vertical ends of the section
    are the eave fascias with the gutter; the chevron end caps are the barge
    flashing over the gables.
    """
    B = Builder()
    zu = roof_under(PE)
    zr = roof_under(0.0)
    T = L.ROOF_T
    sec = [(-PE, zu), (-PE, zu + T), (0.0, zr + T), (PE, zu + T), (PE, zu),
           (0.0, zr)]
    kinds = ("fascia", "slope", "slope", "fascia", "soffit", "soffit")
    fns = {"fascia": uv_eave, "slope": uv_roof, "soffit": uv_patch("soffit")}
    for k, kind in enumerate(kinds):
        (p0, z0), (p1, z1) = sec[k], sec[(k + 1) % 6]
        B.face([(-XE, p0, z0), (-XE, p1, z1), (XE, p1, z1), (XE, p0, z0)], fns[kind])
    barge = uv_patch("barge")
    B.face([(-XE, p, z) for p, z in sec], barge)
    B.face([(XE, p, z) for p, z in reversed(sec)], barge)
    return B


def roof_top(y):
    return roof_under(y) + L.ROOF_T


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


def pillar(py):
    """A cast concrete pillar, ground to the upper storey, into which it is
    sunk: every face takes the pillar region, across its own width."""
    h = L.PILLAR_W / 2.0
    x0, x1, y0, y1 = PILLAR_X - h, PILLAR_X + h, py - h, py + h
    rx, ry, rw, rh = L.PILLAR

    def side(a0, b0, a1, b1):
        def f(co):
            ax, ay = a1 - a0, b1 - b0
            t = ((co.x - a0) * ax + (co.y - b0) * ay) / (ax * ax + ay * ay)
            return (rx + t * rw, ry + co.z * PPM)
        return f
    sides = [side(x0, y0, x1, y0), side(x1, y0, x1, y1),
             side(x1, y1, x0, y1), side(x0, y1, x0, y0)]
    return box(x0, x1, y0, y1, 0.0, PILLAR_TOP, sides, uv_patch("blank"),
               uv_patch("conc"))


def canopy(cx, w, proj):
    """A flat steel canopy on the front wall, sunk into the brick."""
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y0, y1 = -HY - proj, -HY + CANOPY_BURY
    fx, fy = uv_flash("x", L.Z_CAN0), uv_flash("y", L.Z_CAN0)
    return box(x0, x1, y0, y1, L.Z_CAN0, L.Z_CAN1, [fx, fy, uv_patch("blank"), fy],
               uv_patch("coping"), uv_patch("soffit"))


# ------------------------------------------------------------------ ladders
def ladders(level):
    mode = ladder_mode(level)
    if mode is None:
        return []
    out = []
    zc = L.Z_COPE
    keep = RS.brackets_kept(level)
    paint = RS.Paint(L.ATLAS, patch=_patch_centre("steel"))
    # ground to each wing's roof, on the wings' east faces
    for name, x, y in (("fw", FW[1], FW_LADDER_Y), ("bw", BW[1], BW_LADDER_Y)):
        out.append((RS.ladder((x, y, 0.0), (0, 0, 1), (0, 1, 0), (1, 0, 0),
                           zc + LADDER_TOP, 0.20, [1.0, 3.0] if keep else [], mode, paint),
                    "tmp_ladder_" + name))
    # the front wing's roof up the main wall and past the eave
    so = L.EAVE_OUT + EAVE_CLEAR
    top = roof_top(PE) + LADDER_TOP
    # It hangs on its brackets and ends LADDER_HANG above the deck, above the
    # coping, as such ladders do: rails driven through the felt put long thin
    # triangles across the deck, whose crossings the weld then collapsed.
    z0 = L.Z_DECK + LADDER_HANG
    out.append((RS.ladder((WALL_LADDER_X, -HY, z0), (0, 0, 1), (1, 0, 0),
                       (0, -1, 0), top - z0, so, [0.55, 2.45] if keep else [], mode, paint),
                "tmp_ladder_wall"))
    # and on up the front slope to the ridge, bedded into the sheet
    ang = math.atan(L.TAN)
    up = (0.0, math.cos(ang), math.sin(ang))
    nrm = (0.0, -math.sin(ang), math.cos(ang))
    start = 0.25                                    # up the slope from the edge
    foot = (WALL_LADDER_X, -PE + start * math.cos(ang), roof_top(PE) + start * math.sin(ang))
    out.append((RS.ladder(foot, up, (1, 0, 0), nrm, L.SLOPE_LEN - start - 0.45,
                       -0.03, [], mode, paint, rail_d=0.12),
                "tmp_ladder_roof"))
    return out


# -------------------------------------------------------------------- vents
def vent(px, py, dia, height, sides):
    """A vent pipe on the roof: its foot is a slice of the roof plane inside
    the slab, so it is buried everywhere rather than only at its middle. The
    open end is painted as a bore."""
    B = Builder()
    r = dia / 2.0

    def foot(y):
        return roof_under(y) + 0.10

    base = foot(abs(py) + r)
    z1 = roof_top(py) + height
    ring = [(px + r * math.cos(a), py + r * math.sin(a))
            for a in [(i + 0.5) * 2.0 * math.pi / sides for i in range(sides)]]
    rx, ry, rw, rh = L.VENT
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        def fn(co, ax=ax, ay=ay, bx=bx, by=by):
            t = ((co.x - ax) * (bx - ax) + (co.y - ay) * (by - ay)) / \
                ((bx - ax) ** 2 + (by - ay) ** 2)
            return (rx + t * rw, ry + (co.z - base) * PPM)
        B.face([(ax, ay, foot(ay)), (bx, by, foot(by)), (bx, by, z1),
                (ax, ay, z1)], fn)
    tx, ty, tw, th = L.PIPE_TOP
    B.face([(x, y, z1) for x, y in ring],
           lambda co: (tx + tw * (0.5 + (co.x - px) / dia),
                       ty + th * (0.5 + (co.y - py) / dia)))
    B.face([(x, y, foot(y)) for x, y in reversed(ring)], uv_patch("blank"))
    return B


# ---------------------------------------------------------------- downpipes
# (wall, plan coordinate along it, kind). "eave" pipes leave the painted
# gutter under the main eave on a swan-neck; "wing" pipes run straight up into
# a wing's oversailing slab, fed through its parapet. The shape, the UVs and
# the placing rules are scripts/downpipes.py's. Three to each long wall,
# between window bays and at the west corners, and one on each wing's west
# face; none at the east end, where the porch leaves nothing for a pipe to
# come down.
DOWNPIPE_SPOTS = [
    (MAIN_WALLS["front"], -20.6, "eave"), (MAIN_WALLS["front"], -9.0, "eave"),
    (MAIN_WALLS["front"], 3.0, "eave"),
    (MAIN_WALLS["rear"], 2.5, "eave"), (MAIN_WALLS["rear"], -9.0, "eave"),
    (MAIN_WALLS["rear"], -20.6, "eave"),
    (FRONT_WING_WALLS[0][1:3], FW[2] + 0.4, "wing"),
    (BACK_WING_WALLS[3][1:3], BW[3] - 0.4, "wing"),
]


def _pipe(wall, c, kind):
    s = Frame(*wall).s_at(c)
    if kind == "wing":
        return DP.slab_pipe(*wall, s, L.Z_WING_SOF)
    return DP.eave_pipe(*wall, s, L.Z_EAVE, L.TAN, L.EAVE_OUT)


DOWNPIPES = [_pipe(*spot) for spot in DOWNPIPE_SPOTS]


def downpipes(level):
    return DP.solids(DOWNPIPES, *downpipe_mode(level), L.PIPE_STRIP, L.ATLAS)


# ================================================================ assembly
def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    parts = [to_object(gable_slab(), "tmp_roof"),
             to_object(wing_body(FRONT_WING_WALLS, level,
                                 uv_lod3_lid(FW, L.LOD3_FW_DECK, -1)), "tmp_fw"),
             to_object(wing_body(BACK_WING_WALLS, level,
                                 uv_lod3_lid(BW, L.LOD3_BW_DECK, +1)), "tmp_bw")]
    if not wing_box(level):
        parts += [to_object(wing_roof(FW, -1), "tmp_fw_roof"),
                  to_object(wing_roof(BW, +1), "tmp_bw_roof")]
    for i, py in enumerate(PILLAR_Y):
        parts.append(to_object(pillar(py), "tmp_pillar%d" % i))
    for i, (cx, w, proj) in enumerate(CANOPIES):
        if canopy_kept(level, i):
            parts.append(to_object(canopy(cx, w, proj), "tmp_canopy%d" % i))
    for B, name in ladders(level) + downpipes(level):
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
    # 1e-4: the exact boolean resolves 42 m eave lines in 32-bit floats and
    # leaves the odd corner vertex a hundredth of a millimetre off its
    # neighbour. The smallest authored feature is the ladder rung's 0.03 m, so
    # a 0.1 mm weld cannot reach it.
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
    walls = {
        "front": (MAIN_WALLS["front"], FRONT_ITEMS, 0.0, L.Z_WALL_TOP),
        "rear": (MAIN_WALLS["rear"], REAR_ITEMS, 0.0, L.Z_WALL_TOP),
        "west": (MAIN_WALLS["west"], WEST_ITEMS, 0.0, L.Z_GABLE),
        "east": (MAIN_WALLS["east"], EAST_ITEMS, L.Z_PORCH, L.Z_GABLE),
        "porch": (MAIN_WALLS["porch"], PORCH_ITEMS, 0.0, L.Z_PORCH),
    }
    for name, p0, p1, spec in FRONT_WING_WALLS + BACK_WING_WALLS:
        walls[name] = ((p0, p1), spec, 0.0, L.Z_WING_WALL)
    for name, ((p0, p1), spec, zlo, zhi) in walls.items():
        fr = Frame(p0, p1)
        rects = [item_rect(fr, k, c, z) for k, c, z in spec]
        for (k, c, z), r in zip(spec, rects):
            if r[0] < 0.4 or r[1] > fr.L - 0.4:
                bad.append("%s: %s at %.2f is within 0.4 m of a corner" % (name, k, c))
            if r[2] < zlo - EPS or r[3] > zhi - 0.3:
                bad.append("%s: %s at %.2f runs outside its wall's height" % (name, k, c))
            if EPS < r[2] - zlo < 0.3:
                bad.append("%s: %s at %.2f leaves a sliver of wall below it" % (name, k, c))
        for i, a in enumerate(rects):
            for b in rects[i + 1:]:
                if _overlap(a, b, 0.3):
                    bad.append("%s: two openings within 0.3 m of each other" % name)
    # the ground storey of the long walls is buried where a wing stands
    for name, wing, items in (("front", FW, FRONT_ITEMS), ("rear", BW, REAR_ITEMS)):
        for k, c, z in items:
            w = L.OPENINGS[k][0] / 2.0
            if z < L.Z_COPE and c + w > wing[0] - 0.3 and c - w < wing[1] + 0.3:
                bad.append("%s: %s at %.2f is behind the wing" % (name, k, c))
            if z < L.Z_PORCH and c + w > PX - 0.3:
                bad.append("%s: %s at %.2f is in the porch" % (name, k, c))
    for kind in ("glazed_door", "entrance"):
        if L.Z_DOOR <= L.Z_LEAF:
            bad.append("the %s has no transom above its leaves" % kind)
    if not 2.0 <= L.Z_LEAF <= 2.4:
        bad.append("door leaf %.3f m is outside 2.0-2.4" % L.Z_LEAF)
    if not 2.0 <= L.OPENINGS["service_door"][1] - 0.0625 <= 2.4:
        bad.append("the service door's leaf is outside 2.0-2.4")
    # canopies clear of what they shelter, and of the windows above
    if L.Z_CAN0 < L.Z_DOOR + 0.1:
        bad.append("the canopies sit on the door heads")
    if L.Z_CAN1 > L.Z_SILL_UP - 0.5:
        bad.append("the canopies crowd the upper windows")
    # the wings stay clear of the upper windows and of the porch line
    if L.Z_COPE > L.Z_SILL_UP - 0.3:
        bad.append("the wings' coping reaches the upper sills")
    for wing in (FW, BW):
        if wing[1] > PX - 0.3:
            bad.append("a wing's east face is within 0.3 m of the porch wall, "
                       "which a coplanar union would not survive")
    # pillars stand under the upper storey, clear of the porch wall
    if PILLAR_X - L.PILLAR_W / 2.0 < PX + 1.0:
        bad.append("the pillars crowd the porch wall")
    if PILLAR_TOP > L.Z_SILL_UP - 0.2:
        bad.append("the pillars run up into the upper windows")
    # ladders: the wall ladder lands on the deck, clear of the parapet and of
    # the windows; the wing ladders clear of their doors and windows
    half = RS.HALF
    lx0, lx1 = WALL_LADDER_X - half, WALL_LADDER_X + half
    if lx0 < FW[0] + L.PARAPET + 0.2 or lx1 > FW[1] - L.PARAPET - 0.2:
        bad.append("the wall ladder does not land on the front wing's deck")
    for k, c, z in FRONT_ITEMS:
        w = L.OPENINGS[k][0] / 2.0
        if z > L.Z_COPE and c - w < lx1 + 0.2 and c + w > lx0 - 0.2:
            bad.append("the wall ladder crosses the %s at %.2f" % (k, c))
    for y, spec in ((FW_LADDER_Y, FRONT_WING_WALLS[2][3]), (BW_LADDER_Y, BACK_WING_WALLS[1][3])):
        for k, c, z in spec:
            w = L.OPENINGS[k][0] / 2.0
            if abs(c - y) < w + RS.HALF + 0.2:
                bad.append("a wing ladder crosses the %s at %.2f" % (k, c))
    # vents clear of the ridge, the eave and the roof ladder
    for px, py, dia, h in VENTS:
        if abs(py) < dia / 2.0 + 0.2 or abs(py) > HY - 1.0:
            bad.append("the vent at (%.1f, %.1f) is on the ridge or the eave" % (px, py))
        if py < 0 and abs(px - WALL_LADDER_X) < RS.LADDER_W + dia:
            bad.append("the vent at (%.1f, %.1f) is on the roof ladder" % (px, py))
        if abs(px) > HX - 1.0:
            bad.append("the vent at (%.1f, %.1f) is over a gable" % (px, py))
    # downpipes clear of corners, openings, canopies and the wall ladder, and
    # the eave ones clear of the wings and the porch they would run into
    specs = {tuple(map(tuple, pp)): spec for pp, spec, _lo, _hi in walls.values()}
    for (wall, c, kind), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        fr = Frame(*wall)

        def span(what, a, b):
            return (what, min(fr.s_at(a), fr.s_at(b)), max(fr.s_at(a), fr.s_at(b)))
        avoid = [span(k, oc - L.OPENINGS[k][0] / 2.0, oc + L.OPENINGS[k][0] / 2.0)
                 for k, oc, z in specs[tuple(map(tuple, wall))]]
        if wall == MAIN_WALLS["front"]:
            avoid += [span("canopy", cx - w / 2.0, cx + w / 2.0)
                      for cx, w, _proj in CANOPIES]
            avoid.append(span("wall ladder", WALL_LADDER_X - half, WALL_LADDER_X + half))
        if kind == "eave":
            wing = FW if wall[0][1] < 0 else BW
            avoid += [span("wing", wing[0], wing[1]), span("porch", PX, HX)]
        bad += DP.problems(pipe, "the %s downpipe at %.2f" % (kind, c), avoid)
    return bad


# ================================================================== build
def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
# Clear leaf widths, as facade_atlas.py paints them inside each door region's
# frame: paint_entrance()'s pair of leaves between the side lights (122 px),
# paint_glazed_door()'s and paint_service_door()'s one leaf inside a 4 px
# frame. The loading door is its whole sectional opening.
LEAF_W = {"entrance": 122 / PPM,
          "glazed_door": (L.GLAZED_DOOR[2] - 8) / PPM,
          "service_door": (L.SERVICE_DOOR[2] - 8) / PPM,
          "loading_door": L.OPENINGS["loading_door"][0]}
LEAF_H = {"loading_door": L.OPENINGS["loading_door"][1]}      # the rest: L.Z_LEAF


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the walls that stand on the ground:
    the ground storey, which stops at the porch wall PX under the oversailing
    east end (the pillars are open), and both wings; the entrance lobby is a
    recess in the front wall and leaves the outline straight. Two storeys:
    the ground floor with its wings, and the whole 42 x 12 m upper floor,
    which has 3.69 m to the eave."""
    wings = {n: (p0, p1, items) for n, p0, p1, items
             in FRONT_WING_WALLS + BACK_WING_WALLS}
    walls = {"front": MAIN_WALLS["front"] + (FRONT_ITEMS,),
             "rear": MAIN_WALLS["rear"] + (REAR_ITEMS,),
             "west": MAIN_WALLS["west"] + (WEST_ITEMS,),
             "porch": MAIN_WALLS["porch"] + (PORCH_ITEMS,)}
    walls.update(wings)

    def door(door_id, wall, kind, main=False):
        p0, p1, items = walls[wall]
        (c, z), = [(c, z) for k, c, z in items if k == kind]
        return model_facts.wall_door(door_id, p0, p1, Frame(p0, p1).s_at(c), z,
                                     LEAF_W[kind], LEAF_H.get(kind, L.Z_LEAF), main)

    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-HX, -HY), (FW[0], -HY), (FW[0], FW[2]), (FW[1], FW[2]),
                      (FW[1], -HY), (PX, -HY), (PX, HY), (BW[1], HY),
                      (BW[1], BW[3]), (BW[0], BW[3]), (BW[0], HY), (-HX, HY)],
        "storeys": [
            (0.0, (PX + HX) * 2 * HY + (FW[1] - FW[0]) * (FW[3] - FW[2])
             + (BW[1] - BW[0]) * (BW[3] - BW[2])),
            (L.Z_STOREY, 2 * HX * 2 * HY),
        ],
        "doors": [door("front", "front", "entrance", main=True),
                  door("stair", "front", "glazed_door"),
                  door("east_porch", "porch", "entrance"),
                  door("rear", "rear", "service_door"),
                  door("west", "west", "service_door"),
                  door("loading", "west", "loading_door"),
                  door("front_wing", "fw_east", "service_door"),
                  door("back_wing", "bw_east", "service_door")],
    }


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four
    orthographic elevations, a plan from above, and a raised three-quarter
    aerial off the front corner; plus aerials off the other corners and eye
    views at the two entrances. Working views only - not committed."""
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
    persp = [("aerial", centre, Vector((1.0, -1.0, math.sqrt(2.0))), 3.0),
             ("aerial_rear", centre, Vector((-1.0, 1.0, math.sqrt(2.0))), 3.0),
             ("aerial_west", centre, Vector((-1.0, -1.0, math.sqrt(2.0))), 3.0),
             ("aerial_east", centre, Vector((1.0, 1.0, math.sqrt(2.0))), 3.0),
             ("eye_entrance", Vector((8.0, -8.0, 3.0)), Vector((-0.2, -1.0, 0.12)), 0.75),
             ("eye_porch", Vector((18.0, -2.0, 2.5)), Vector((1.0, -0.45, 0.12)), 0.55),
             ("eye_west", Vector((-21.0, -2.0, 3.0)), Vector((-1.0, -0.6, 0.15)), 0.75),
             ("near_ladders", Vector((15.0, -8.0, 5.5)), Vector((1.0, -1.0, 0.55)), 0.55),
             ("near_roof", Vector((6.0, -2.0, 9.0)), Vector((0.3, -1.0, 0.9)), 0.6)]
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
