# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of rintamamiestalo_porch, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite Finnish rintamamiestalo — the 1940s-50s one-and-a-half-storey
veterans' house: a 10 x 8 m block under a 45 degree gable roof, horizontal lap
siding over a concrete plinth with cellar lights, plain-glass windows, a
brick chimney on the ridge, and an enclosed entrance porch whose own gable
runs into the main eave.

Construction is a set of closed solids unioned with Blender's exact boolean:
the main body, the porch body, one roof slab per roof, the chimney, the
back-door canopy and the two flights of steps. Each solid is simple to build
on its own; the union is what cuts the porch roof's valleys, trims the walls
where the soffits meet them and removes everything that ends up inside, so the
result is the boundary of one empty volume and interior geometry cannot occur.

The walls are textured as a trim sheet (see facade_atlas.py): siding tiles,
and each window or door is a hole in the wall with its own faces mapped to the
region that carries its casing and glazing. Every number the two files share
is imported from facade_atlas.py rather than written here a second time.
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
from asset_build import pivot_offset, to_object, union  # noqa: E402,F401
import downpipes as DP  # noqa: E402
import handrails as HR  # noqa: E402
import roof_safety as RS  # noqa: E402
import shell_build as SB  # noqa: E402
from shell_build import InwardFrame, fill_region, overlap, rect_poly  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT)
get_material, export_all = BUILD.material, BUILD.export_all
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants
Builder = functools.partial(SB.Builder, L.ATLAS)
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

# Entrance porch: an enclosed kuisti on the front, off centre, its gable facing
# the street. It is a separate solid reaching 0.2 m into the main body; the
# union removes the overlap.
PX0, PX1 = -2.70, 0.30
PXC, PHW = (PX0 + PX1) / 2.0, (PX1 - PX0) / 2.0
PY_FRONT, PY_BACK = -6.20, -HY + 0.20
PZ_EAVE = 2.75
PZ_TOP = PZ_EAVE + (L.Z_WALL_TOP - L.Z_EAVE)
PORCH_OV = 0.30                  # both eave and rake: a smaller roof, a smaller overhang
PORCH_SLAB_BACK = -3.40          # well inside the main block, so its end is buried

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
FRONT_STEPS = (PXC - 0.70, PXC + 0.70)           # along x, off the porch front
BACK_STEPS = (0.80, 2.20)                         # along x, off the rear wall
# Lean-to canopy over the back door, the type's usual kitchen entrance: 0.8 m
# out from the wall, a shallow fall, sitting clear above the door casing. It
# clears the 0.25 m test as a covered entrance, and is silhouette, so it
# survives to LOD2.
CANOPY_X = (0.75, 2.25)
CANOPY_OUT = 0.80
CANOPY_Z = (3.30, 3.14)                           # top at the wall, top at the edge
CANOPY_T = 0.12

# --------------------------------------------------------------- elevations
# Openings as (kind, s, sill z): s is the centre, measured along the wall from
# its start, and each wall runs counter-clockwise seen from above so its outward
# face is on the right. Sills sit at 1.5 m: 0.8 m above the 0.7 m floor, the
# floor itself being carried by the cellar plinth.
# The attic storey is lit from the gables, one window per end: the standard
# 1.80 x 1.40 m "wide" unit, centred under the ridge at ATTIC_SILL. It is the
# same sash the living room has, which is how the standardised type worked,
# and it is why no separate attic region is painted in the atlas.
GF, ATTIC_SILL = 1.50, 4.65
# Gable ends carry one window per storey: the wide living-room window below,
# centred under the wide attic window above. Two smaller windows side by side
# read as busier than the type is, and one large one is the catalog's rule for
# short walls (CLAUDE.md, Style Direction). The porch splits the front wall
# into two such runs, and each carries one window centred between the porch
# and its corner: a standard one west, the wide living-room window east, with
# the cellar light under it.
MAIN_WALLS = {
    # front (-Y), s = x + 5; the porch covers s 2.3 .. 5.3
    "front": ((-HX, -HY), (HX, -HY), None, [
        ("std", 1.15, GF), ("wide", 7.65, GF), ("cellar", 7.65, 0.25)]),
    # +X gable end, s = y + 4
    "east": ((HX, -HY), (HX, HY), Z_APEX, [
        ("wide", 4.00, GF), ("wide", 4.00, ATTIC_SILL),
        ("vent", 4.00, 7.35), ("cellar", 6.10, 0.25)]),
    # rear (+Y), s = 5 - x
    "rear": ((HX, HY), (-HX, HY), None, [
        ("std", 1.50, GF), ("door_back", 3.50, L.Z_FLOOR), ("bath", 5.30, 2.20),
        ("std", 8.40, GF), ("cellar", 1.50, 0.25)]),
    # -X gable end, s = 4 - y
    "west": ((-HX, HY), (-HX, -HY), Z_APEX, [
        ("wide", 4.00, GF), ("wide", 4.00, ATTIC_SILL),
        ("vent", 4.00, 7.35), ("cellar", 2.00, 0.25)]),
}
PORCH_APEX = PZ_TOP + PHW * TAN
PORCH_WALLS = {
    # (p0, p1, apex, items, corner at start, corner at end)
    "left": ((PX0, PY_BACK), (PX0, PY_FRONT), None, [("porch", 1.30, 1.55)],
             False, True),
    "front": ((PX0, PY_FRONT), (PX1, PY_FRONT), PORCH_APEX,
              [("door_front", 1.50, L.Z_FLOOR)], True, True),
    "right": ((PX1, PY_FRONT), (PX1, PY_BACK), None, [("porch", 1.10, 1.55)],
              True, False),
    "back": ((PX1, PY_BACK), (PX0, PY_BACK), PORCH_APEX, [], False, False),
}
# Offsets into the tiling siding band, so butt joints differ wall to wall.
U_OFF = {"front": 0.0, "east": 3.3, "rear": 6.1, "west": 9.4,
         "left": 2.2, "right": 5.7, "back": 0.0}

# Downpipes (scripts/downpipes.py): one from each eave's gutter, at
# diagonally opposite corners, so each gable end shows one. The front's is at
# its east end, since a window crowds the west corner.
DOWNPIPE_SPOTS = [("front", 2 * HX - DP.CORNER), ("rear", 2 * HX - DP.CORNER)]
DOWNPIPES = [DP.eave_pipe(*MAIN_WALLS[w][:2], s, L.Z_EAVE, TAN, EAVE_OV)
             for w, s in DOWNPIPE_SPOTS]

# Roof safety kit (scripts/roof_safety.py), the sweep's way to the chimney,
# at the back, away from the entrance, as such kits usually are: a wall
# ladder up the rear wall between the bathroom and the west window, the roof ladder
# straight above it up the rear slope, and a level walkway along the slope
# 0.5 m below the ridge, east to stand behind the stack.
KIT_S = 6.70                                      # rear wall, s = 5 - x
EAVE_REAR = RS.Eave(*MAIN_WALLS["rear"][:2], L.Z_EAVE, EAVE_OV,
                    L.Z_EAVE + ROOF_T - EAVE_OV * TAN, TAN)
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
def item_rects(kind, s, z):
    return SB.item_rects(L.OPENINGS[kind], s, z)


def build_item(B, fr, kind, s, z, level):
    """Faces for one opening; returns the hole it needs in its wall region."""
    mode = item_mode(kind, level)
    (ol, orr, ob, ot), (il, ir, ib, it) = item_rects(kind, s, z)
    fn = uv_item(fr, kind, ol, ob)
    depth = L.REVEAL_DEPTH.get(kind, L.REVEAL_DEFAULT)
    rev = uv_patch("tread" if kind == "cellar" else "reveal")
    o = rect_poly((ol, orr, ob, ot))
    if mode == "flush":
        B.face([fr.P(*p) for p in o], fn)
        return o
    if mode == "cut":
        SB.recess(B, fr, o, 0.0, depth, fn, rev)
        return o
    i = rect_poly((il, ir, ib, it))
    for k in range(4):
        B.face([fr.P(*o[k]), fr.P(*o[(k + 1) % 4]),
                fr.P(*i[(k + 1) % 4]), fr.P(*i[k])], fn)
    SB.recess(B, fr, i, 0.0, depth, fn, rev)
    if abs(ob - ib) < EPS:
        # A door has no bottom casing, so the threshold edge lies on the hole's
        # own bottom edge; the hole has to carry those two corners too.
        return [(ol, ob), (il, ib), (ir, ib), (orr, ob), (orr, ot), (ol, ot)]
    return o


def build_wall(B, fr, top, apex, split, edge_z, corners, items, u_off, level):
    """One elevation: corner-board columns, then siding regions with holes.

    *edge_z* is the set of heights every panel end of this solid carries, so
    two walls meeting at a corner meet on exactly the same vertices. *split*
    is the height where siding hands over from S1 to the gable band S2.
    """
    Lw = fr.L
    # Contrasting paint survives every tier; these are flush UV strips.
    c0, c1 = corners
    s0 = L.CW if c0 else 0.0
    s1 = Lw - L.CW if c1 else Lw

    def rake(s):
        return top if apex is None else top + min(s, Lw - s) * TAN

    def ez(s):
        return sorted({e for e in edge_z if e < top - EPS} | {rake(s)})

    s1band = uv_band(fr, L.S1_Y0, 0.0, u_off)
    s2band = uv_band(fr, L.S2_Y0, L.Z_EAVE, u_off)

    lo = [e for e in edge_z if e < top - EPS]
    for a, b, has in ((0.0, L.CW, c0), (Lw - L.CW, Lw, c1)):
        if not has:
            continue
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
        if apex is not None:
            outline.append((Lw / 2.0, apex))
        outline += [(s0, z) for z in reversed(ez(s0)) if z > EPS]
        regions = [(outline, s1band, holes_between(0.0, 99.0))]
    else:
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
        raise ValueError("an opening straddles a region boundary on a %.1f m wall"
                         % Lw)


def main_body(level):
    """The wall ring, capped by a floor and a roof-shaped lid split at the
    ridge (shell_build.close_solid())."""
    B = Builder()
    edge = [0.0, L.Z_EAVE, L.Z_WALL_TOP, L.Z_FLASH]
    for name, (p0, p1, apex, items) in MAIN_WALLS.items():
        fr = InwardFrame(p0, p1)
        build_wall(B, fr, L.Z_WALL_TOP, apex, L.Z_EAVE if apex else None,
                   sorted(edge), (True, True), items, U_OFF[name], level)
    SB.close_solid(B, uv_patch("blank"), ridges=[[(HX, 0.0, Z_APEX), (-HX, 0.0, Z_APEX)]])
    return B


def porch_body(level):
    B = Builder()
    edge = [0.0, PZ_TOP, L.Z_FLASH]
    for name, (p0, p1, apex, items, c0, c1) in PORCH_WALLS.items():
        fr = InwardFrame(p0, p1)
        build_wall(B, fr, PZ_TOP, apex, None, sorted(edge), (c0, c1), items,
                   U_OFF[name], level)
    SB.close_solid(B, uv_patch("blank"),
                   ridges=[[(PXC, PY_FRONT, PORCH_APEX), (PXC, PY_BACK, PORCH_APEX)]])
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
    base = to_object(main_body(level), "tmp_body")
    parts = [
        to_object(porch_body(level), "tmp_porch"),
        to_object(gable_slab("x", 0.0, HY, L.Z_EAVE, EAVE_OV,
                             -HX - RAKE_OV, HX + RAKE_OV), "tmp_roof"),
        to_object(gable_slab("y", PXC, PHW, PZ_EAVE, PORCH_OV,
                             PY_FRONT - PORCH_OV, PORCH_SLAB_BACK), "tmp_porch_roof"),
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


def check_layout():
    """Assert the constraints that are invisible in the numbers and obvious
    once rendered: openings colliding, clipping the rake or a corner board,
    or straddling the band change; the gable outgrowing its atlas band; the
    porch roof missing the main roof it is meant to run into."""
    problems = []
    if Z_APEX > L.S2_TOP:
        problems.append("gable apex %.2f is above the S2 band's %.2f" % (Z_APEX, L.S2_TOP))
    slope = (HY + EAVE_OV) * SLOPE_F
    if abs(slope - L.ROOF_SLOPE_LEN) > 1e-3:
        problems.append("main slope is %.3f m, atlas assumes %.3f" % (slope, L.ROOF_SLOPE_LEN))
    walls = [(n, InwardFrame(p0, p1), apex, items, L.Z_WALL_TOP, (True, True), L.Z_EAVE)
             for n, (p0, p1, apex, items) in MAIN_WALLS.items()]
    walls += [(n, InwardFrame(p0, p1), apex, items, PZ_TOP, (c0, c1), None)
              for n, (p0, p1, apex, items, c0, c1) in PORCH_WALLS.items()]
    gap = 0.05
    for name, fr, apex, items, top, (c0, c1), split in walls:
        rects = [(k, item_rects(k, s, z)[0]) for k, s, z in items]
        for k, (l, r, b, t) in rects:
            lo = (L.CW if c0 else 0.0) + gap
            hi = fr.L - (L.CW if c1 else 0.0) - gap
            if l < lo or r > hi:
                problems.append("%s: %s at s %.2f..%.2f runs into a corner" % (name, k, l, r))
            eave = top - (L.Z_WALL_TOP - L.Z_EAVE)       # visible top, under the soffit
            for s in (l, r):
                if apex is not None:
                    vis = eave + min(s, fr.L - s) * TAN
                else:
                    vis = eave
                if t > vis - gap:
                    problems.append("%s: %s top %.2f is under the roof (%.2f)" % (name, k, t, vis))
            if split is not None and b < split < t:
                problems.append("%s: %s straddles the gable band change" % (name, k))
            if b < L.Z_FLASH < t and k != "door_front" and k != "door_back":
                problems.append("%s: %s straddles the plinth top" % (name, k))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if overlap(rects[i][1], rects[j][1], gap):
                    problems.append("%s: %s and %s overlap" % (name, rects[i][0], rects[j][0]))
    door = next(item_rects(k, x, z)[0] for k, x, z in MAIN_WALLS["rear"][3]
                if k == "door_back")
    cx = sorted(HX - v for v in door[:2])            # rear wall: s = 5 - x
    if not (CANOPY_X[0] < cx[0] and cx[1] < CANOPY_X[1]):
        problems.append("back canopy does not cover the door casing")
    if CANOPY_Z[0] - CANOPY_T < door[3] + 0.10:
        problems.append("back canopy meets the wall on top of the door casing")
    if CANOPY_Z[1] - CANOPY_T - STEP_PROFILE[2][1] < 2.2:
        problems.append("back canopy's edge is below head height over the landing")
    porch_ridge = PZ_EAVE + ROOF_T + PHW * TAN
    if not (Z_RIDGE - HY - EAVE_OV < porch_ridge < Z_RIDGE - HY + 0.5):
        problems.append("porch ridge %.2f does not run into the main eave" % porch_ridge)
    if CHIMNEY[5] - FLUE_DEPTH < Z_RIDGE + 0.05:
        problems.append("the flue's floor is down in the roof slab")
    # downpipes clear of the corners, the openings, the back steps and canopy
    back = [("back steps", HX - BACK_STEPS[1], HX - BACK_STEPS[0]),
            ("back canopy", HX - CANOPY_X[1], HX - CANOPY_X[0])]
    wall = ROOF_KIT[0]
    for (w, _s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        avoid = [(k,) + item_rects(k, c, z)[0][:2] for k, c, z in MAIN_WALLS[w][3]]
        kit = [("wall ladder",) + wall.span()] if w == "rear" else []
        problems += DP.problems(pipe, "the %s downpipe" % w,
                                avoid + (back if w == "rear" else []) + kit)
    # the roof kit: the wall ladder clear of the rear's corners, openings,
    # back steps, canopy and downpipe; the walkway behind the stack, clear of
    # it and of the ridge
    avoid = [(k,) + item_rects(k, c, z)[0][:2] for k, c, z in MAIN_WALLS["rear"][3]]
    avoid += back
    avoid += [("downpipe", p.s - DP.A, p.s + DP.A)
              for (w, _s), p in zip(DOWNPIPE_SPOTS, DOWNPIPES) if w == "rear"]
    problems += RS.problems(wall, "the wall ladder", avoid)
    door_w = L.OPENINGS["door_front"][0]
    problems += HR.problems(HANDRAILS[0], "the front handrail", door_w)
    problems += HR.problems(HANDRAILS[1], "the back handrail",
                            L.OPENINGS["door_back"][0], (cx[0] + cx[1]) / 2.0)
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


# =================================================================== facts
# Storeys: the ground floor on the plinth and the attic 3.10 m above it.
Z_ATTIC = L.Z_FLOOR + 3.10


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the main block with the enclosed
    porch, whose walls stand on the ground like the block's own. The attic
    counts where the roof's underside is 1.6 m or more over its floor."""
    def door(door_id, kind, wall, item, main=False):
        p0, p1, items = wall[0], wall[1], wall[3]
        s, z = next((s, z) for k, s, z in items if k == item)
        w, h = L.OPENINGS[item][:2]
        return model_facts.wall_door(door_id, kind, p0, p1, s, z, w, h, main)

    attic_w = model_facts.roof_clear_width(2 * HY, Z_ATTIC, L.Z_EAVE, TAN)
    return {
        "hero": False,
        "dwellings": 1,
        "footprint": [(-HX, HY), (-HX, -HY), (PX0, -HY), (PX0, PY_FRONT),
                      (PX1, PY_FRONT), (PX1, -HY), (HX, -HY), (HX, HY)],
        "storeys": [
            (L.Z_FLOOR, 2 * HX * 2 * HY + (PX1 - PX0) * (-HY - PY_FRONT)),
            (Z_ATTIC, 2 * HX * attic_w),
        ],
        "doors": [door("front", "entrance", PORCH_WALLS["front"], "door_front", main=True),
                  door("back", "service", MAIN_WALLS["rear"], "door_back")],
    }


# ================================================================ previews


def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export
    (shell_build.render_views()): four orthographic elevations, a plan from
    above, and a raised three-quarter aerial off the front corner. Working
    views only — not committed."""
    return SB.render_views(BUILD, out_dir, level, res, distance=60.0)


if __name__ == "__main__":
    BUILD.main(build_all, facts)
