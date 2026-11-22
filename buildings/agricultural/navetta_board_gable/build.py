# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of navetta_board_gable, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite mid-century Finnish farm barn (navetta): a 16 x 9 m byre under a
30 degree gable roof whose roof space is the hay loft, red-ochre vertical
board-and-batten with white corner boards and casings on a low cast-concrete
plinth. The long front faces the yard with a pair of big braced board doors
on a concrete ramp, a row of small byre windows and a plank door at the east
end; the east gable carries the loft hatch high up.

Construction is a set of closed solids unioned with Blender's exact boolean:
the body (a wall ring capped under the roof), the roof slab, three concrete
ramps and two downpipes from the gutters painted on the eave fascias. The union trims the walls where the soffits meet them and
removes everything that ends up inside, so the result is the boundary of one
empty volume and interior geometry cannot occur.

The walls are textured as a trim sheet (see facade_atlas.py): board-and-batten
tiles, and each opening is a hole in the wall with its own faces mapped to the
region that carries its casing and leaf or glazing. Every number the two files
share is imported from facade_atlas.py.
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
EXPORT_DIR = os.path.join(HERE, "export")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import downpipes as DP  # noqa: E402
import model_facts  # noqa: E402
import shell_build as SB  # noqa: E402
from asset_build import to_object, union  # noqa: E402
from shell_build import InwardFrame as Frame, fill_region, rect_poly  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT)
get_material, export_all = BUILD.material, BUILD.export_all
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants
Builder = functools.partial(SB.Builder, L.ATLAS)
PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ------------------------------------------------------------------ massing
# Front (the yard side) faces -Y. Walls 16.0 x 9.0 m, ridge along X.
HX, HY = 8.0, 4.5
PITCH_DEG = 30.0
TAN = math.tan(math.radians(PITCH_DEG))
ROOF_T = L.FASC_H / PPM          # slab's vertical thickness = fascia height
EAVE_OV = 0.45                   # eave overhang
RAKE_OV = 0.35                   # gable (rake) overhang
Z_APEX = L.Z_WALL_TOP + HY * TAN                 # body apex, inside the slab
Z_RIDGE = L.Z_EAVE + ROOF_T + HY * TAN           # top of the ridge

# Ramps: low concrete wedges up to the thresholds, (x0, x1, wall y, outward,
# run out from the wall). The top meets the wall 2 cm under the threshold, so
# it never lies in the plane of a door recess's floor; its back is buried in
# the wall. Every tier keeps them, so every tier has the same extents.
Z_RAMP = L.Z_FLOOR - 0.02
BIG_RAMP = (-6.60, -2.60, -HY, -1.0, 2.20)
DOOR_RAMP = (5.80, 7.40, -HY, -1.0, 1.40)
REAR_RAMP = (-0.80, 0.80, HY, 1.0, 1.40)
RAMPS = (BIG_RAMP, DOOR_RAMP, REAR_RAMP)

# --------------------------------------------------------------- elevations
# Openings as (kind, s, z): s is the centre along the wall from its start, z
# the sill (windows) or threshold (doors). "window" and "window_b" are the
# same byre window on two atlas regions with different rooms behind the glass,
# alternated along each wall. Each wall runs counter-clockwise
# seen from above, so its outward face is on the right.
GF = 1.30                         # byre window sills, 0.90 m over the floor
Z_HATCH = 4.05                    # the loft hatch's threshold, over the belt board
MAIN_WALLS = {
    # front (-Y), s = x + 8: the big doors toward the west, four byre windows,
    # the plank door at the east end
    "front": ((-HX, -HY), (HX, -HY), None, [
        ("bigdoor", 3.40, L.Z_FLOOR), ("window", 6.90, GF), ("window_b", 8.80, GF),
        ("window", 10.70, GF), ("window_b", 12.60, GF), ("door", 14.60, L.Z_FLOOR)]),
    # +X gable end, s = y + 4.5: one window below, the loft hatch above it
    "east": ((HX, -HY), (HX, HY), Z_APEX, [
        ("window", 4.50, GF), ("hatch", 4.50, Z_HATCH)]),
    # rear (+Y), s = 8 - x: two windows either side of the service door
    "rear": ((HX, HY), (-HX, HY), None, [
        ("window", 2.40, GF), ("window_b", 4.80, GF), ("door", 8.00, L.Z_FLOOR),
        ("window", 11.20, GF), ("window_b", 13.60, GF)]),
    # -X gable end, s = 4.5 - y: one window below, a louvred loft vent above
    "west": ((-HX, HY), (-HX, -HY), Z_APEX, [
        ("window_b", 4.50, GF), ("vent", 4.50, 5.25)]),
}
# Offsets into the tiling board band, so the board tones differ wall to wall.
U_OFF = {"front": 0.0, "east": 3.3, "rear": 6.1, "west": 9.4}

# Downpipes (scripts/downpipes.py): one from each eave's gutter, at
# diagonally opposite corners, so each gable end shows one: the front's at its
# east end, past the plank door's ramp, the rear's at its west end.
DOWNPIPE_SPOTS = [("front", 2 * HX - DP.CORNER), ("rear", 2 * HX - DP.CORNER)]
DOWNPIPES = [DP.eave_pipe(*MAIN_WALLS[w][:2], s, L.Z_EAVE, TAN, EAVE_OV)
             for w, s in DOWNPIPE_SPOTS]


def item_mode(kind, level):
    """How an opening is built at each tier.

    ring  - LOD0: the casing is a ring of faces on the wall, the opening inside
            it is recessed with reveals and closed by its glass or leaf plane.
    cut   - LOD1: one recess the size of the casing, casing painted on it.
    flush - LOD2/3: the casing rect as a flat quad in the wall.
    None  - dropped: the gable vent below LOD1.
    """
    if kind == "vent":
        return ("flush", "flush", None, None)[level]
    return ("ring", "cut", "flush", "flush")[level]


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position. Walls are
# shell_build.InwardFrame: the third coordinate is depth into the wall.

def uv_band(fr, y0, z_ref, u_off):
    return lambda co: ((fr.s_of(co) + u_off) * PPM, y0 + (co.z - z_ref) * PPM)


def uv_item(fr, kind, s_left, z_bot):
    """Planar, at true scale. Recessed faces sit behind the wall only along
    its normal, so they sample the same texels as if they were flush."""
    x0, y0 = L.ITEM_ORIGIN[kind]
    return SB.uv_region(fr, (x0, y0, 0, 0), s_left, z_bot, PPM)


def uv_strip(fr, rect, a, b, z0, z1):
    x0, y0, w, h = rect
    return lambda co: (x0 + (fr.s_of(co) - a) / (b - a) * w,
                       y0 + min(max((co.z - z0) / (z1 - z0), 0.0), 1.0) * h)


def uv_patch(name):
    return SB.uv_patch(L.PATCHES[name])


# ================================================================== walls
def recess(B, fr, rect, depth, fn, rev):
    """Line opening *rect* (l, r, b, t) with reveals and close it *depth*
    into the wall (shell_build.recess())."""
    SB.recess(B, fr, rect_poly(rect), 0.0, depth, fn, rev)


def item_rects(kind, s, z):
    return SB.item_rects(L.OPENINGS[kind], s, z)


def build_item(B, fr, kind, s, z, level):
    """Faces for one opening; returns the hole it needs in its wall region."""
    mode = item_mode(kind, level)
    (ol, orr, ob, ot), (il, ir, ib, it) = item_rects(kind, s, z)
    fn = uv_item(fr, kind, ol, ob)
    depth = L.REVEAL_DEPTH.get(kind, L.REVEAL_DEFAULT)
    rev = uv_patch("reveal")
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
        # no bottom casing: the threshold edge lies on the hole's bottom edge,
        # so the hole has to carry the leaf's two bottom corners too
        return [(ol, ob), (il, ib), (ir, ib), (orr, ob), (orr, ot), (ol, ot)]
    return o


def build_wall(B, fr, top, apex, split, edge_z, items, u_off, level):
    """One elevation: corner-board columns at both ends, then board regions
    with holes. *edge_z* is the set of heights every panel end carries, so
    two walls meeting at a corner meet on exactly the same vertices. *split*
    is the height where boarding hands over from S1 to the gable band S2."""
    Lw = fr.L
    s0, s1 = L.CW, Lw - L.CW

    def rake(s):
        return top if apex is None else top + min(s, Lw - s) * TAN

    def ez(s):
        return sorted({e for e in edge_z if e < top - EPS} | {rake(s)})

    s1band = uv_band(fr, L.S1_Y0, 0.0, u_off)
    s2band = uv_band(fr, L.S2_Y0, L.Z_EAVE, u_off)

    lo = [e for e in edge_z if e < top - EPS]
    for a, b in ((0.0, L.CW), (Lw - L.CW, Lw)):
        strip = uv_strip(fr, L.CORNER, a, b, L.Z_FLASH, rake(L.CW))
        for k, za in enumerate(lo):
            if k + 1 < len(lo):
                zb = lo[k + 1]
                poly = [(a, za), (b, za), (b, zb), (a, zb)]
            else:
                zb = top
                poly = [(a, za), (b, za), (b, rake(b)), (a, rake(a))]
            if zb <= L.Z_FLASH + EPS:
                fn = s1band                      # plinth under the board
            elif split is not None and za >= split - EPS:
                fn = s2band                      # gable belt over the board
            else:
                fn = strip
            B.face([fr.P(s, z) for s, z in poly], fn)

    rect = {}
    for kind, s, z in items:
        if item_mode(kind, level):
            rect[(kind, s, z)] = item_rects(kind, s, z)[0]

    def holes_between(z0, z1):
        return [(kind, s, z) for (kind, s, z), r in rect.items()
                if r[2] > z0 - EPS and r[3] < z1 + EPS]

    if split is None:
        outline = [(s0, 0.0), (s1, 0.0)] + [(s1, z) for z in ez(s1) if z > EPS]
        outline += [(s0, z) for z in reversed(ez(s0)) if z > EPS]
        regions = [(outline, s1band, holes_between(0.0, 99.0))]
    else:
        lower = ([(s0, 0.0), (s1, 0.0)]
                 + [(s1, z) for z in ez(s1) if EPS < z < split - EPS]
                 + [(s1, split), (s0, split)]
                 + [(s0, z) for z in reversed(ez(s0)) if EPS < z < split - EPS])
        upper = ([(s0, split), (s1, split)]
                 + [(s1, z) for z in ez(s1) if z > split + EPS]
                 + [(Lw / 2.0, apex)]
                 + [(s0, z) for z in reversed(ez(s0)) if z > split + EPS])
        regions = [(lower, s1band, holes_between(0.0, split)),
                   (upper, s2band, holes_between(split, 99.0))]

    placed = 0
    for outline, fn, its in regions:
        holes = [build_item(B, fr, kind, s, z, level) for kind, s, z in its]
        placed += len(its)
        fill_region(B, fr, outline, holes, fn)
    if placed != len(rect):
        raise ValueError("an opening straddles a region boundary on a %.1f m wall" % Lw)


def main_body(level):
    """The wall ring, capped by an n-gon floor and a roof-shaped lid split at
    the ridge (shell_build.close_solid()), both buried once unioned: the
    floor on the ground, the lid inside the roof slab."""
    B = Builder()
    edge = [0.0, L.Z_FLASH, L.Z_EAVE, L.Z_WALL_TOP]
    for name, (p0, p1, apex, items) in MAIN_WALLS.items():
        build_wall(B, Frame(p0, p1), L.Z_WALL_TOP, apex, L.Z_EAVE if apex else None,
                   sorted(edge), items, U_OFF[name], level)
    SB.close_solid(B, uv_patch("blank"), ridges=[[(HX, 0.0, Z_APEX), (-HX, 0.0, Z_APEX)]])
    return B


# ================================================================== roof
SLOPE_F = math.sqrt(1.0 + TAN * TAN)            # slope length per horizontal metre
ROOF_RPM = L.ROOF_H / L.ROOF_SLOPE_LEN           # atlas px per metre up the slope


def gable_slab(half_w, z_eave, over, a0, a1):
    """The roof as one closed slab: a chevron section extruded along X.

    The section's underside meets the wall face at *z_eave*, so once unioned
    the part outside the walls is the soffit and the part inside disappears.
    The vertical ends are the fascias; the chevron end caps are the barge
    boards over the gables.
    """
    B = Builder()
    pe = half_w + over
    z0 = z_eave + ROOF_T + half_w * TAN
    zt = z0 - pe * TAN
    sec = [(-pe, zt - ROOF_T), (-pe, zt), (0.0, z0), (pe, zt),
           (pe, zt - ROOF_T), (0.0, z0 - ROOF_T)]
    kinds = ("fascia", "slope", "slope", "fascia", "soffit", "soffit")

    def W(a, p, z):
        return (a, p, z)

    def slope_uv(co):
        d = (pe - abs(co.y)) * SLOPE_F
        return ((co.x + 16.0) * PPM, L.ROOF_Y0 + d * ROOF_RPM)

    def fascia_uv(co):
        return ((co.x + 16.0) * PPM, L.FASC_Y0 + (co.z - (zt - ROOF_T)) * PPM)

    fns = {"fascia": fascia_uv, "slope": slope_uv, "soffit": uv_patch("soffit")}
    for k, kind in enumerate(kinds):
        (p0, z0_), (p1, z1_) = sec[k], sec[(k + 1) % 6]
        B.face([W(a0, p0, z0_), W(a0, p1, z1_), W(a1, p1, z1_), W(a1, p0, z0_)], fns[kind])
    barge = uv_patch("barge")
    B.face([W(a0, p, z) for p, z in sec], barge)
    B.face([W(a1, p, z) for p, z in reversed(sec)], barge)
    return B


def ramp(x0, x1, wall, outward, run):
    """A concrete ramp: a wedge from Z_RAMP at the wall down to the ground
    *run* metres out, across x0..x1, its back 5 cm into the wall. The slope
    and cheeks sample the plinth's concrete in S1 by height, so its foot
    carries the plinth's soil and splash; the bottom is the blank patch."""
    B = Builder()
    profile = [(-0.05, 0.0), (-0.05, Z_RAMP), (0.0, Z_RAMP), (run, 0.0)]

    def W(a, d, z):
        return (a, wall + outward * d, z)

    def slope_uv(co):
        return ((co.x + 11.0) * PPM, L.S1_Y0 + co.z * PPM)

    def cheek_uv(co):
        return (((co.y - wall) * outward + 11.0) * PPM, L.S1_Y0 + co.z * PPM)

    n = len(profile)
    for k in range(n):
        (d0, z0), (d1, z1) = profile[k], profile[(k + 1) % n]
        fn = uv_patch("blank") if abs(z0) < EPS and abs(z1) < EPS else slope_uv
        B.face([W(x0, d0, z0), W(x1, d0, z0), W(x1, d1, z1), W(x0, d1, z1)], fn)
    B.face([W(x0, d, z) for d, z in profile], cheek_uv)
    B.face([W(x1, d, z) for d, z in reversed(profile)], cheek_uv)
    return B


# ================================================================ assembly
def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    parts = [to_object(gable_slab(HY, L.Z_EAVE, EAVE_OV, -HX - RAKE_OV, HX + RAKE_OV),
                       "tmp_roof")]
    parts += [to_object(ramp(*r), "tmp_ramp%d" % i) for i, r in enumerate(RAMPS)]
    parts += [to_object(B, name) for B, name in
              DP.solids(DOWNPIPES, *DP.MODES[level], L.PIPE_STRIP, L.ATLAS)]
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # coplanar boolean subdivisions, keeping every UV seam and edge
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def check_layout():
    """Assert what is invisible in the numbers and obvious once rendered:
    openings colliding, running into a corner board or under the roof, or
    straddling the plinth or the gable band change; the gable outgrowing its
    atlas band; the roof slope disagreeing with the atlas; a ramp that does
    not cover its door; a downpipe crowding a corner, an opening or a ramp."""
    problems = []
    if Z_APEX > L.S2_TOP:
        problems.append("gable apex %.2f is above the S2 band's %.2f" % (Z_APEX, L.S2_TOP))
    slope = (HY + EAVE_OV) * SLOPE_F
    if abs(slope - L.ROOF_SLOPE_LEN) > 2e-3:
        problems.append("slope is %.3f m, atlas assumes %.3f" % (slope, L.ROOF_SLOPE_LEN))
    gap = 0.05
    for name, (p0, p1, apex, items) in MAIN_WALLS.items():
        fr = Frame(p0, p1)
        rects = [(k, item_rects(k, s, z)[0]) for k, s, z in items]
        for k, (l, r, b, t) in rects:
            if l < L.CW + gap or r > fr.L - L.CW - gap:
                problems.append("%s: %s at s %.2f..%.2f runs into a corner" % (name, k, l, r))
            for s in (l, r):
                vis = L.Z_EAVE + (min(s, fr.L - s) * TAN if apex is not None else 0.0)
                if t > vis - gap:
                    problems.append("%s: %s top %.2f is under the roof (%.2f)" % (name, k, t, vis))
            if apex is not None and b < L.Z_EAVE + L.BELT_H + gap and t > L.Z_EAVE:
                problems.append("%s: %s meets the gable belt board" % (name, k))
            if b < L.Z_FLASH < t and k not in L.LEAVES:
                problems.append("%s: %s straddles the plinth top" % (name, k))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b_ = rects[i][1], rects[j][1]
                if SB.overlap(a, b_, gap):
                    problems.append("%s: %s and %s overlap" % (name, rects[i][0], rects[j][0]))
    # each ramp runs wider than the casing of the door it serves
    for (x0, x1, wall, _o, _r), (wname, kind, s) in zip(
            RAMPS, (("front", "bigdoor", 3.40), ("front", "door", 14.60),
                    ("rear", "door", 8.00))):
        fr = Frame(*MAIN_WALLS[wname][:2])
        l, r = item_rects(kind, s, L.Z_FLOOR)[0][:2]
        xs = sorted(fr.P(v, 0.0)[0] for v in (l, r))
        if not (x0 < xs[0] - 0.1 and xs[1] + 0.1 < x1):
            problems.append("the ramp at x %.2f..%.2f does not cover the %s" % (x0, x1, kind))
    # downpipes clear of the corners, the openings' casings and the ramps
    for (w, _s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        fr = Frame(*MAIN_WALLS[w][:2])
        avoid = [(k,) + item_rects(k, c, z)[0][:2] for k, c, z in MAIN_WALLS[w][3]]
        for i, (x0, x1, wall, _o, _r) in enumerate(RAMPS):
            if abs(fr.P(0.0, 0.0)[1] - wall) < EPS:
                ss = sorted(fr.s_of(Vector((x, wall, 0.0))) for x in (x0, x1))
                avoid.append(("ramp %d" % i, ss[0], ss[1]))
        problems += DP.problems(pipe, "the %s downpipe" % w, avoid)
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the wall outline, without the ramps
    and the overhangs. One storey: the byre floor on the plinth. The loft in
    the roof space is hay storage, not an occupied storey, and its hatch is
    a door no one reaches from the ground."""
    def door(door_id, kind, wall, item, main=False):
        p0, p1, items = MAIN_WALLS[wall][0], MAIN_WALLS[wall][1], MAIN_WALLS[wall][3]
        s, z = next((s, z) for k, s, z in items if k == item)
        w, h = L.OPENINGS[item][:2]
        return model_facts.wall_door(door_id, kind, p0, p1, s, z, w, h, main)

    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-HX, -HY), (HX, -HY), (HX, HY), (-HX, HY)],
        "storeys": [(L.Z_FLOOR, 2 * HX * 2 * HY)],
        "doors": [door("front", "entrance", "front", "door", main=True),
                  door("big_doors", "vehicle", "front", "bigdoor"),
                  door("rear", "service", "rear", "door"),
                  door("loft_hatch", "balcony", "east", "hatch")],
    }


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export
    (shell_build.render_views()). Working views only, not committed."""
    return SB.render_views(BUILD, out_dir, level, res, distance=60.0)


if __name__ == "__main__":
    BUILD.main(build_all, facts)
