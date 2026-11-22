# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of kaivoskonttori_brick, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

The staff building of a small mid-century mine (*kaivoskonttori*: mine
office): one storey of red facing brick on a rendered plinth under a low
standing-seam gable, 16 x 8 m. The office is at the east end, behind three
ordinary windows on each long wall and one in the gable; the changing rooms
and the wash room (the dry) are at the west end, lit by rows of small high
windows. The main entrance is on the front, just east of the middle: a
half-glazed door with a transom light in a rendered surround, under a flat
concrete canopy, up two concrete steps. The shift comes in off the site by a
steel door on the rear, into the dry, up two steps of its own. A galvanised
gutter is painted along both eaves with four modelled downpipes, a snow
guard is painted above each eave, and three vent pipes stand on the rear
slope over the wash room.

Construction is a set of closed solids unioned with Blender's exact boolean:
the wall ring, capped as one solid with the building's whole volume, the
gable roof slab, the canopy, the two flights of steps, the downpipes and the
vents. The union trims the wall tops into the roof and the rest into the
walls, and leaves the boundary of one empty volume, so interior geometry
cannot occur.

Every number the mesh and the atlas share is imported from facade_atlas.py
rather than written here a second time.
"""

import functools
import importlib
import math
import os
import sys

import bmesh


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
import shell_build as SB  # noqa: E402
from asset_build import to_object, union  # noqa: E402
from shell_build import Frame, fill_region, rect_poly  # noqa: E402
import downpipes as DP  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT,
                          tint=L.LIT_FACTOR)
get_material, export_all = BUILD.material, BUILD.export_all
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants
Builder = functools.partial(SB.Builder, L.ATLAS)

PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ================================================================== massing
HX, HY = L.HX, L.HY                     # 8 x 4: a 16 x 8 m shell
XE = HX + L.RAKE_OUT                    # the roof's own extent
PE = HY + L.EAVE_OUT
Z_APEX = L.Z_EAVE + HY * L.TAN + L.WALL_INTO_ROOF      # gable wall top, in the slab


def roof_under(y):
    """The gable roof's underside over plan position *y*."""
    return L.Z_EAVE + (HY - abs(y)) * L.TAN


def roof_top(y):
    return roof_under(y) + L.ROOF_T


def gtop(s, span=2.0 * HY):
    """Where a gable wall stops, *s* along it: inside the roof slab."""
    return L.Z_WALL_TOP + min(s, span - s) * L.TAN


# Openings, per wall, as (kind, centre in plan x or y, sill z). The dry's
# high windows keep a 1.75 m pitch west of the middle and the office's
# windows a 1.875 m pitch east of it, on both long walls; the entrance stands
# between them on the front, just east of the middle, with a metre of plain
# brick each side of its surround so it reads on its own.
FL, SH, SW = L.Z_FLOOR, L.Z_SILL_HIGH, L.Z_SILL
ENTRANCE_X = 0.9
SERVICE_X = -1.5
FRONT_ITEMS = ([("high", x, SH) for x in (-6.75, -5.0, -3.25, -1.5)]
               + [("entrance", ENTRANCE_X, FL)]
               + [("win", x, SW) for x in (3.0, 4.875, 6.75)])
REAR_ITEMS = ([("win", x, SW) for x in (6.75, 4.875, 3.0)]
              + [("service_door", SERVICE_X, FL)]
              + [("high", x, SH) for x in (-3.25, -5.0, -6.75)])
EAST_ITEMS = [("win", 0.0, SW)]         # the office's gable
WEST_ITEMS = [("high", 0.0, SH)]        # the wash room's gable

# The canopy over the entrance: (centre x, width, projection), sunk into the
# wall CANOPY_BURY.
CANOPY = (ENTRANCE_X, 2.4, 1.2)
CANOPY_BURY = 0.1

# Steps up to the doors, as (out from the wall, z) profiles extruded across
# the door: a landing 3 cm under the threshold, then one step, so two risers
# of 0.14 m and no handrail (CLAUDE.md asks for one from three risers). The
# back of each is buried STEP_BURY in the wall under the door.
STEP_BURY = 0.05
Z_LAND = L.Z_FLOOR - 0.03125            # 0.28125
Z_STEP = Z_LAND / 2.0
FRONT_STEPS = (ENTRANCE_X, 2.0, [(-STEP_BURY, 0.0), (-STEP_BURY, Z_LAND), (1.0, Z_LAND),
                                 (1.0, Z_STEP), (1.3, Z_STEP), (1.3, 0.0)])
REAR_STEPS = (SERVICE_X, 1.6, [(-STEP_BURY, 0.0), (-STEP_BURY, Z_LAND), (0.9, Z_LAND),
                               (0.9, Z_STEP), (1.2, Z_STEP), (1.2, 0.0)])

# Vent pipes on the rear slope over the wash room: (x, y, diameter, height
# above the sheet). Plain vents, not serviced items, so no roof safety kit.
VENTS = [(-6.0, 1.5, 0.25, 0.85), (-4.4, 1.8, 0.16, 0.60),
         (-2.8, 1.5, 0.16, 0.60)]


# ----------------------------------------------------------------- tiers
def opening_mode(level):
    """LOD0/1 cut every opening into its wall with brick reveals; LOD2/3 paint
    the same rectangle flat. The 0.15-0.2 m reveals are under two pixels past
    70 m, and the window rhythm is the painted rectangle's to keep."""
    return "cut" if level < 2 else "flush"


def vent_sides(level, dia):
    """Eight sides up close, six to 70 m, four past it. Dropping the two
    0.16 m pipes at LOD2 showed at 65 m as two ticks over the ridge going, so
    they stay to 120 m; past it they are a pixel wide and go, and only the
    wash room's 0.25 m exhaust still breaks the ridge line."""
    if level == 0:
        return 8
    if level == 1:
        return 6
    if level == 2:
        return 4
    return 4 if dia >= 0.2 else 0


def downpipe_mode(level):
    """(sides, bent) of the downpipes at each tier: scripts/downpipes.py's
    MODES unchanged. Four pipes are cheap enough to keep on every tier, and
    their galvanised line at each corner of the long walls is what tells
    the gutter is there."""
    return DP.MODES[level]


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.

def uv_brick(fr, u_off, shift=0.0):
    """The brick band. *shift* lowers the rows sampled, for the gables."""
    return lambda co: ((fr.s_of(co) + u_off) * PPM,
                       L.BRICK_Y0 + (co.z - shift) * PPM)


def uv_patch(name):
    return SB.uv_patch(L.PATCHES[name])


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


def uv_conc(a_of, b_of):
    """The concrete region, planar: *a_of* and *b_of* give a vertex's metres
    across and up the region from its corner."""
    x, y, w, h = L.CONC
    return lambda co: (x + a_of(co) * PPM, y + b_of(co) * PPM)


# ================================================================== walls
def item_rect(fr, kind, centre, z0):
    """(s0, s1, z0, z1) of an opening centred on plan coordinate *centre*."""
    w, h = L.OPENINGS[kind]
    s = fr.s_at(centre)
    return (s - w / 2.0, s + w / 2.0, z0, z0 + h)


def surround_rect(rect):
    """The entrance's rendered surround round its opening *rect*."""
    s0, s1, z0, z1 = rect
    return (s0 - L.SURROUND, s1 + L.SURROUND, z0, z1 + L.SURROUND_TOP)


def build_opening(B, fr, kind, rect, level, u_off):
    """One opening: reveals round it and the closing plane set back in it
    while it is cut, the same rectangle painted flat after. Returns the
    outline in (s, z) the wall region takes as a hole.

    The entrance carries its rendered surround: a U of render on the wall
    face round three sides of the opening, which is the hole the wall takes,
    and its reveals are render too. Its region holds the surround and the
    door together, so the flush tiers draw both as one quad.
    """
    s0, s1, z0, z1 = rect
    poly = rect_poly(rect)
    dx, _dy = L.REGION_OFF.get(kind, (0, 0))
    rs0 = s0 - dx / PPM
    closing = SB.uv_region(fr, L.REGION[kind], rs0, z0, PPM)
    entrance = kind == "entrance"
    if entrance:
        S0, S1, _z0, Z1 = surround_rect(rect)
    if opening_mode(level) == "flush":
        if entrance:
            poly = [(S0, z0), (S1, z0), (S1, Z1), (S0, Z1)]
        B.face([fr.P(s, z) for s, z in poly], closing)
        return poly
    cheeks = [uv_patch("sill") if k == 0 else
              uv_patch("render") if entrance else uv_reveal(fr, edge, u_off)
              for k, edge in enumerate(SB.edges(poly))]
    SB.recess(B, fr, poly, 0.0, -L.REVEAL[kind], closing, cheeks)
    if not entrance:
        return poly
    ring = [(S0, z0), (s0, z0), (s0, z1), (s1, z1), (s1, z0), (S1, z0),
            (S1, Z1), (S0, Z1)]
    fill_region(B, fr, ring, [], closing)
    # the wall's hole: the surround's outline, with the opening's foot
    # corners on it, which the threshold shares
    return [(S0, z0), (s0, z0), (s1, z0), (S1, z0), (S1, Z1), (S0, Z1)]


def wall_region(B, fr, outline, items, level, u_off, uvfn):
    """One planar region of wall: every opening inside it built and holed."""
    holes = [build_opening(B, fr, kind, rect, level, u_off) for kind, rect in items]
    fill_region(B, fr, outline, holes, uvfn)


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


def build_long(B, name, level):
    """A long wall, ground to its head inside the roof slab; its corners
    carry the gables' Z_GABLE breakpoint."""
    fr = Frame(*MAIN_WALLS[name])
    uo = U_OFF[name]
    L_ = fr.L
    outline = [(0.0, 0.0), (L_, 0.0), (L_, L.Z_GABLE), (L_, L.Z_WALL_TOP),
               (0.0, L.Z_WALL_TOP), (0.0, L.Z_GABLE)]
    wall_region(B, fr, outline, rects_for(fr, ITEMS[name]), level, uo, uv_brick(fr, uo))


def build_gable(B, name, level):
    """A gable end: the wall up to Z_GABLE with its opening, then the
    triangle above, which samples the brick band GABLE_SHIFT lower down."""
    fr = Frame(*MAIN_WALLS[name])
    uo = U_OFF[name]
    L_ = fr.L
    outline = [(0.0, 0.0), (L_, 0.0), (L_, L.Z_GABLE), (0.0, L.Z_GABLE)]
    wall_region(B, fr, outline, rects_for(fr, ITEMS[name]), level, uo, uv_brick(fr, uo))
    tri = [(0.0, L.Z_GABLE), (L_, L.Z_GABLE), (L_, L.Z_WALL_TOP),
           (L_ / 2.0, gtop(L_ / 2.0)), (0.0, L.Z_WALL_TOP)]
    fill_region(B, fr, tri, [], uv_brick(fr, uo, L.GABLE_SHIFT))


def cap_ring(B, split):
    """Cap the wall ring: a floor on the ground and a lid at the wall top,
    both buried (the floor on the ground, the lid inside the roof), so the
    solid is closed for the exact boolean. The lid is cut between the two
    *split* rim positions, the gable apexes, since its rim is not planar
    (shell_build.rim_loops() and cap(); the floor is capped first)."""
    loops = SB.rim_loops(B, 2)
    blank = uv_patch("blank")
    floor = min(loops, key=lambda lp: max(v.co.z for v in lp))
    top = next(lp for lp in loops if lp is not floor)
    SB.cap(B, floor, blank)
    SB.cap(B, top, blank, split=[B.v(p) for p in split])


def main_body(level):
    B = Builder()
    build_long(B, "front", level)
    build_gable(B, "east", level)
    build_long(B, "rear", level)
    build_gable(B, "west", level)
    cap_ring(B, split=[(HX, 0.0, Z_APEX), (-HX, 0.0, Z_APEX)])
    return B


# ================================================================== roof
def uv_roof(co):
    d = (PE - abs(co.y)) * L.SLOPE_F
    return ((co.x + XE) * PPM, L.ROOF_Y0 + d * L.ROOF_RPM)


def uv_eave(co):
    zt = roof_under(PE)
    return ((co.x + XE) * PPM, L.EAVE_Y0 + (co.z - zt) * PPM)


def gable_slab():
    """The roof as one closed slab: a chevron section extruded along the
    ridge. Its underside meets the long walls' faces at Z_EAVE, so once it is
    unioned with the shell the part outside the walls is the eave and rake
    soffit and the part inside disappears. The vertical ends of the section
    are the eave fascias with the gutter; the chevron end caps are the barge
    flashing over the gables."""
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


# ============================================================ other solids
def uv_cane(axis, z0):
    """The canopy's edge band, U along the edge, V from its underside."""
    return lambda co: ((co.x if axis == "x" else co.y) * PPM,
                       L.CANE_Y0 + (co.z - z0) * PPM)


def canopy():
    """The flat concrete canopy over the entrance, sunk into the wall: its
    edges the cast-edge band, its top the concrete region, its underside the
    soffit."""
    cx, w, proj = CANOPY
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y0, y1 = -HY - proj, -HY + CANOPY_BURY
    fx, fy = uv_cane("x", L.Z_CAN0), uv_cane("y", L.Z_CAN0)
    top = uv_conc(lambda co: co.x - x0, lambda co: co.y - y0)
    return SB.box(Builder(), x0, x1, y0, y1, L.Z_CAN0, L.Z_CAN1,
                  [fx, fy, uv_patch("blank"), fy], top, uv_patch("soffit"))


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
# (wall, plan x along it). Two to each eave, 0.3 m in from the corners, clear
# of the end windows; the shape, the UVs and the placing rules are
# scripts/downpipes.py's.
DOWNPIPE_SPOTS = [("front", -7.7), ("front", 7.7), ("rear", 7.7), ("rear", -7.7)]


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
    parts = [to_object(gable_slab(), "tmp_roof"),
             to_object(canopy(), "tmp_canopy"),
             to_object(steps(FRONT_STEPS, -HY, -1), "tmp_steps_front"),
             to_object(steps(REAR_STEPS, HY, +1), "tmp_steps_rear")]
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
def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    tops = {"front": L.Z_EAVE, "rear": L.Z_EAVE, "east": L.Z_GABLE,
            "west": L.Z_GABLE}
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
            if r[3] > tops[name] - 0.3:
                bad.append("%s: %s at %.2f runs too close to the wall head" % (name, k, c))
            if r[2] < L.Z_FLOOR - EPS:
                bad.append("%s: %s at %.2f is below the floor" % (name, k, c))
        for i, a in enumerate(rects):
            for b in rects[i + 1:]:
                if SB.overlap(a, b, 0.3):
                    bad.append("%s: two openings within 0.3 m of each other" % name)
    # the human scale: door leaves, the transom, sills against both
    if not 2.0 <= L.Z_LEAF <= 2.4:
        bad.append("door leaf %.3f m is outside 2.0-2.4" % L.Z_LEAF)
    if L.ENTRY_H <= L.Z_LEAF + 0.15:
        bad.append("the entrance has no transom light above its leaf")
    if not 2.0 <= L.OPENINGS["service_door"][1] - 0.0625 <= 2.4:
        bad.append("the service door's leaf is outside 2.0-2.4")
    if not 0.8 <= L.Z_SILL - L.Z_FLOOR <= 1.0:
        bad.append("the office sills are not at desk height")
    if L.Z_SILL_HIGH - L.Z_FLOOR < 1.6:
        bad.append("the high windows' sills are not above head height")
    # the canopy: over the surround, clear of the eave's soffit and gutter,
    # wider than the surround and clear of the windows beside it
    if abs(L.Z_CAN0 - (L.Z_FLOOR + L.ENTRY_H + L.SURROUND_TOP)) > 0.0626:
        bad.append("the canopy does not sit on the entrance surround")
    clear = roof_under(-PE) - L.Z_CAN1
    if clear < 0.15:
        bad.append("the canopy is %.2f m under the eave's soffit" % clear)
    cx, w, proj = CANOPY
    fr = Frame(*MAIN_WALLS["front"])
    srd = surround_rect(item_rect(fr, "entrance", ENTRANCE_X, L.Z_FLOOR))
    if w < srd[1] - srd[0] + 0.4:
        bad.append("the canopy is not wider than the entrance surround")
    for k, c, z in FRONT_ITEMS:
        if k != "entrance":
            hw = L.OPENINGS[k][0] / 2.0
            if c + hw > cx - w / 2.0 and c - hw < cx + w / 2.0:
                bad.append("the canopy runs over the %s at %.2f" % (k, c))
    # the steps: under the canopy, as wide as the surround, and two risers
    if FRONT_STEPS[1] < srd[1] - srd[0] + 0.3:
        bad.append("the entrance steps are narrower than the surround")
    if Z_LAND / 2.0 > 0.18:
        bad.append("the steps' risers are over 0.18 m")
    # vents clear of the ridge, the eave and the gables, over the wash room
    for px, py, dia, h in VENTS:
        if abs(py) < dia / 2.0 + 0.3 or abs(py) > HY - 1.0:
            bad.append("the vent at (%.1f, %.1f) is on the ridge or the eave" % (px, py))
        if abs(px) > HX - 1.0 or px > 0.0:
            bad.append("the vent at (%.1f, %.1f) is not over the wash room" % (px, py))
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
# Clear leaf widths, as facade_atlas.py paints them: one 1.0 m leaf inside a
# 4 px frame in both door regions.
LEAF_W = {"entrance": 1.0, "service_door": (L.SERVICE_DOOR[2] - 8) / PPM}


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the outer wall faces, 16 x 8 m; the
    eaves, the canopy and the two flights of steps stand outside it. One
    storey, at the floor level 0.3125 m above the ground the thresholds
    stand on, the whole plate inside the outer wall faces. The main door is
    the front entrance; the rear door is the shift's, a service door."""
    def door(door_id, kind, wall, item, main=False):
        p0, p1 = MAIN_WALLS[wall]
        (c, z), = [(c, z) for k, c, z in ITEMS[wall] if k == item]
        return model_facts.wall_door(door_id, kind, p0, p1, Frame(p0, p1).s_at(c), z,
                                     LEAF_W[item], L.Z_LEAF, main)

    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-HX, -HY), (HX, -HY), (HX, HY), (-HX, HY)],
        "storeys": [(L.Z_FLOOR, 2 * HX * 2 * HY)],
        "doors": [door("entrance", "entrance", "front", "entrance", main=True),
                  door("shift", "service", "rear", "service_door")],
    }


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views (shell_build.render_views()), plus an aerial off
    the rear corner and eye views at the two doors. Working views only - not
    committed."""
    return SB.render_views(BUILD, out_dir, level, res, distance=60.0, views=(
        SB.AERIAL, SB.AERIAL_REAR,
        SB.orbit("eye_entrance", (0.35, -1.0, 0.10), 0.75, target=(ENTRANCE_X, -HY, 1.6)),
        SB.orbit("eye_service", (-0.35, 1.0, 0.10), 0.75, target=(SERVICE_X, HY, 1.6)),
        SB.orbit("eye_front", (-0.6, -1.0, 0.05), 1.6, target=(0.0, -HY, 2.0))))


if __name__ == "__main__":
    BUILD.main(build_all, facts)
