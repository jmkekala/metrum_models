# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of brick_clocktower_hall, all four LOD tiers.

Run headless against the authoring file, which it rebuilds, exports, renders
and saves:

    blender --background source.blend --python build.py

Massing is a composite Nordic-civic town hall: a long front range with
projecting end pavilions and a forward centre entrance bay, rear wings forming
a U-shaped court, a low truncated-hip roof over one continuous flat deck, and a
centred clock tower.

The masses below are written as overlapping rectangles because that is how the
building is actually shaped, but they are never built as separate boxes — see
union_outline. Both walls and roof are raised from the union's outline, so the
mesh is the boundary of one empty shell and carries no interior geometry.

Facade ornament (arches, trim, string course, cornice, clock face) is carried
by the texture atlas, per the LOD0 rule in CLAUDE.md. Geometry carries
silhouette plus the openings CLAUDE.md makes an explicit exception for: massing,
roofline, cut window and door reveals at LOD0, quoined corners, the balcony,
the pedimented clock attic, the tower's stepped profile, chimneys.

Region names below index into the atlas produced by facade_atlas.py beside this
file; the pixel constants in the two files must stay in step.
"""

import math
import os
import sys

import bmesh
import bpy
from mathutils import Euler, Vector


ASSET = "brick_clocktower_hall"
HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(HERE, "export")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import model_facts  # noqa: E402
from asset_build import bounds as _bounds, pivot_offset, to_object, union  # noqa: E402,F401

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, ["red_brick"], "red_brick",
                          camera_location=(33.8, -63.6, 22.0))
get_material, export_all = BUILD.material, BUILD.export_all
_show_only, preview_studio = BUILD.show_only, BUILD.preview_studio
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants
LEVELS = (0, 1, 2, 3)

ATLAS, PPM = 2048.0, 64.0
BAY_M = 3.2                      # nominal facade bay pitch
BAY_U = 204.8 / ATLAS
ROOF_Y0, ROOF_H = 730.0, 256.0
UNI = 986.0
ENT = (0.0, 704.0, UNI, UNI + 730.0)
TOW = (704.0, 896.0, UNI, UNI + 563.0)   # 3.0 m x 8.8 m at 64 px/m
ATT = (986.0, 1498.0, UNI, UNI + 333.0)
CHM = (1498.0, 1588.0, UNI, UNI + 314.0)   # 1.4 m x 4.9 m at 64 px/m
BLANK = (1600.0, 1660.0, UNI, UNI + 60.0)
TRIMP = (1660.0, 1720.0, UNI, UNI + 60.0)
QUOIN = (1720.0, 1752.0, UNI, UNI + 730.0)
BALUS = (0.0, 308.0, 1750.0, 1814.0)
REVEALP = (1752.0, 1812.0, UNI, UNI + 60.0)
SOOT = (1600.0, 1660.0, UNI + 72.0, UNI + 132.0)

Z_EAVE = 11.4                    # single continuous cornice height
EAVE_OVER = 0.45                 # projection, within the 0.3-0.6 m convention
FASCIA_H = 0.25                  # fascia depth; matches the atlas' top trim band
# Walls run this far past the eave, up inside the roof solid. Without it their
# top caps sit exactly on the roof's floor outline, the rings weld, and every
# perimeter edge ends up with four faces. The sliver is inside the roof volume.
WALL_TUCK = 0.10

# Window and door openings. The reveal depth clears the 0.25 m test on its own
# merits; both storeys share one half-width so the two rows' column
# breakpoints coincide, which roughly halves the wall subdivision.
WIN_HW = 0.70
WIN_DEPTH = 0.28
GF_OPEN = (1.25, 3.70)           # ground floor: 2.45 m tall, 1.25 m sill
UF_OPEN = (6.35, 8.95)           # upper floor: 2.6 m tall
# The entrance elevation reads the unique ENT artwork rather than the tiling
# band, so its openings are listed explicitly. s is measured from the panel's
# left end, i.e. s = x + 5.5.
ENTRANCE_OPENINGS = [
    (5.50, 1.00, 0.15, 2.60, "door"),   # cut to the springing; fanlight is flush
    (2.20, WIN_HW, GF_OPEN[0], GF_OPEN[1], "gfl"),
    (8.80, WIN_HW, GF_OPEN[0], GF_OPEN[1], "gfr"),
    (3.65, 0.62, 6.60, 9.10, "ual"),
    (5.50, 0.62, 5.60, 9.10, "bal"),           # balcony door, down to the slab
    (7.35, 0.62, 6.60, 9.10, "uar"),
    (1.45, WIN_HW, UF_OPEN[0], UF_OPEN[1], "url"),
    (9.55, WIN_HW, UF_OPEN[0], UF_OPEN[1], "urr"),
]
# Balcony pieces. The parapets sink 0.10 m into the slab and are held a few
# centimetres inside its faces, so no two boxes share a ring or a plane —
# stacking them flush over-connects the shared edges instead.
BALC_SLAB = (-2.40, 2.40, -11.40, -9.90, 5.35, 5.55)
BALC_FRONT = (-2.36, 2.36, -11.36, -11.16, 5.45, 6.55)
BALC_SIDES = [(-2.34, -2.14, -11.30, -10.00, 5.45, 6.55),
              (2.14, 2.34, -11.30, -10.00, 5.45, 6.55)]
BALC_RAIL_Z = (5.55, 1.0)        # visible parapet height, for the UV band

# Quoined corners are derived from the plan outline, never listed by hand.
# Hand-maintaining them went wrong twice in opposite directions: flattening a
# jog left two blocks stranded mid-wall where they read as seams, and the fix
# for that left the whole rear of the building unquoined while the front was.
# Both are the same bug — a corner list that does not follow the massing it
# describes. Deriving them makes the two agree by construction.
QUOIN_PROUD = 0.08               # stands this far out of both wall planes
QUOIN_DEPTH = 0.50               # and wraps this far back along each
Z_UP = Vector((0.0, 0.0, 1.0))

# walls: x0, x1, y0, y1   (front faces -Y)
#
# The rear wings' outer faces are flush with the end pavilions' at x = +-24.4,
# not set back. An earlier version had the wings 0.8 m narrower, which put a
# 0.8 m jog in each side elevation at y = 6.0 — and because the roof is raised
# from these same rects, the eave and hip stepped there too. At that size it
# reads as two walls that failed to meet rather than as articulation: the side
# looked like two misaligned buildings. Either commit to a real setback or make
# it flush; 0.8 m is the one thing it must not be.
WALLS = [
    (-17.2, 17.2, -8.0, 6.0),      # main front range
    (-24.4, -16.4, -9.6, 6.0),     # left end pavilion
    (16.4, 24.4, -9.6, 6.0),       # right end pavilion
    (-5.5, 5.5, -10.2, 2.0),       # centre entrance bay
    (-24.4, -13.4, 2.0, 16.5),     # left rear wing, flush with the pavilion
    (13.4, 24.4, 2.0, 16.5),       # right rear wing, flush with the pavilion
    (-6.0, 6.0, 2.0, 11.0),        # centre rear link
]

# Truncated hip: a short sloped band up from the eave to one broad flat deck,
# not steep hips meeting at a ridge. That is what the reference does, and it is
# why its roofline sits so low over a building this wide. Built over the union
# footprint by roof_solid, so the slopes exist only on the outer perimeter.
ROOF_RUN, ROOF_RISE = 3.50, 3.00         # slope run and rise; deck at 14.65

# Tower, bottom up, scaled off the orthographic dusk elevation: platform at
# 18.0, a short 2.2 m drum, a 1.4 m dome, then a thin flagpole to 24.6. The
# earlier version had a drum and dome each about twice this tall and a shaft
# 4.4 m wide, which read as a campanile bolted onto a low building.
TOWER_W, TOWER_YC = 1.50, -2.30          # half-width, and centre in Y
TOWER_TOP = 20.20
TOWER_PLAT = (17.30, 18.00)
TOWER_DOME = (20.20, 20.90, 21.60)
DOME_MID_W, DOME_TOP_W = 1.10, 0.45       # half-widths at the dome's break and top
TOWER_BALL = (21.60, 22.10)
TOWER_POLE = 24.60
# Dark rendered stacks, slimmer and shorter than a ridged roof would carry,
# which is how the reference's read against the roof.
CHIM_TOP = 16.30                         # ~1.65 m proud of the 14.65 deck
CHIMNEYS = [
    (-8.1, -6.9, -1.6, -0.4, CHIM_TOP), (6.9, 8.1, -1.6, -0.4, CHIM_TOP),
    (-19.3, -18.1, 6.6, 7.8, CHIM_TOP), (18.1, 19.3, 6.6, 7.8, CHIM_TOP),
    (-19.3, -18.1, 11.6, 12.8, CHIM_TOP), (18.1, 19.3, 11.6, 12.8, CHIM_TOP),
]
# Each stack is open at the top: a one-brick shell round one flue, which drops
# FLUE_DEPTH to a soot floor, still 0.65 m over the deck.
FLUE_WALL = 0.25
FLUE_DEPTH = 1.00

# The U-court: between the rear wings' inner faces and behind the front range.
# Its seven walls are the one part of the building a street camera does not
# see, so LOD1 bakes their windows flat while every other elevation keeps its
# reveals.
COURT_X, COURT_Y = 13.4, 6.0

# What each tier keeps. Every tier is raised from the same WALLS outline: an
# earlier LOD2 collapsed the 1.6-2.2 m facade projections flush, which were
# taken as sub-pixel at its range but are 16-37 px at the 70-120 m it covers,
# and it dropped the balcony, so its bounds and therefore its pivot sat 0.98 m
# off LOD0's. Now only detail goes, never massing:
#
#   LOD0   reveals on every elevation, quoin blocks, clock dial, full crown
#   LOD1   as LOD0, with the U-court's seven walls baked flat
#   LOD2   windows flat, quoins painted on flat corner strips, dial painted;
#          balcony, chimneys and the whole crown stay
#   LOD3   as LOD2, with the dome's two stages merged and the ball into the
#          pole, both changes of about a pixel beyond 120 m
#
# LOD2 and LOD3 end up close together. That is the silhouette's actual cost:
# everything left is massing or roofline, and what a tier drops beyond this
# shows as a change at the switch.
#
# The crown — balustraded platform, two-stage dome, ball and flagpole — is
# what the tower is recognised by on the skyline, so it goes through LOD2
# unchanged. It was already four-sided, the least a dome can have and still
# read as one, so there is no coarser version to fall back to; an earlier
# LOD1 dropped the platform and pole and LOD2 swapped the lot for a plain
# pyramid, which changed the skyline at the first two switches.


# --------------------------------------------------------------------- UVs

def _face_htan(face):
    """In-plane horizontal direction, taken from the face's own vertex spread.

    Derived from geometry rather than the normal on purpose: a freshly created
    bmesh face reports a stale normal, and a normal-derived tangent silently
    degenerates to the X axis, which collapses every x-constant wall onto a
    single texel column.
    """
    co = [l.vert.co for l in face.loops]
    best, tan = -1.0, Vector((1.0, 0.0, 0.0))
    for i in range(len(co)):
        for j in range(i + 1, len(co)):
            d = Vector((co[j].x - co[i].x, co[j].y - co[i].y, 0.0))
            if d.length_squared > best:
                best, tan = d.length_squared, d
    if tan.length < 1e-6:
        return Vector((1.0, 0.0, 0.0))
    tan.normalize()
    return tan


def _uv_facade(face, uvl, z_shift=0.0):
    """World-Z for V so storey bands line up on every wall; U snapped to a
    whole number of bays so windows stay centred and never cut at a corner."""
    t = _face_htan(face)
    ss = [l.vert.co.x * t.x + l.vert.co.y * t.y for l in face.loops]
    s0, s1 = min(ss), max(ss)
    length = s1 - s0
    nbay = max(1, int(round(length / BAY_M)))
    for loop in face.loops:
        co = loop.vert.co
        s = co.x * t.x + co.y * t.y
        u = 0.0 if length < 1e-6 else (s - s0) / length * nbay * BAY_U
        loop[uvl].uv = (u, (co.z - z_shift) * PPM / ATLAS)


def _bay_openings(length):
    """Two window rows per bay, derived from the panel's bay rhythm.

    Each opening is one rectangle. Stepping the arched row to follow its curve
    was tried and reverted: it cost about 7,000 extra triangles, because the
    extra column breakpoints multiply across every band, and it read worse —
    a chunky staircase ledge instead of a clean niche head.
    """
    nbay = max(1, int(round(length / BAY_M)))
    w = length / nbay
    out = []
    for i in range(nbay):
        c = (i + 0.5) * w
        out.append((c, WIN_HW, GF_OPEN[0], GF_OPEN[1], ("gf", i)))
        out.append((c, WIN_HW, UF_OPEN[0], UF_OPEN[1], ("uf", i)))
    return out, nbay


def _uv_panel_facade(face, uvl, p0, t, length, nbay):
    """Facade band, mapped from the panel's own run rather than each face's.

    Every quad in a gridded wall has to share one mapping; letting each small
    pier snap its own bay count would scramble the artwork. Recessed faces are
    offset only along the wall normal, so they sample the same texels as if
    they were flush.
    """
    for loop in face.loops:
        co = loop.vert.co
        s = (co - p0).dot(t)
        loop[uvl].uv = (s / length * nbay * BAY_U, co.z * PPM / ATLAS)


def _inset(rect, half=0.5):
    """Pull a region rect in by half a texel on every side.

    A rect's bounds are the seams *between* texels, not texel centres, so a UV
    that lands on one puts the bilinear filter half onto the neighbouring
    region. At the roof band's edges that is the white cornice course below and
    whatever the unique band starts with above, drawn as a hairline along every
    eave and deck edge; beside the entrance panel it is the atlas' unpainted
    black. Half a texel in keeps the filter inside the artwork it is reading.
    """
    x0, x1, y0, y1 = rect
    return (x0 + half, x1 - half, y0 + half, y1 - half)


def _uv_panel_rect(face, uvl, p0, t, length, rect, z0, zspan):
    x0, x1, y0, y1 = _inset(rect)
    for loop in face.loops:
        co = loop.vert.co
        fu = (co - p0).dot(t) / length
        fv = min(max((co.z - z0) / zspan, 0.0), 1.0)
        loop[uvl].uv = ((x0 + fu * (x1 - x0)) / ATLAS,
                        (y0 + fv * (y1 - y0)) / ATLAS)


def _uv_roof(face, uvl):
    t = _face_htan(face)
    slope = face.normal.cross(t)
    if slope.length < 1e-6:
        slope = Vector((t.y, -t.x, 0.0))
    slope.normalize()
    ds = [l.vert.co.dot(slope) for l in face.loops]
    d0, d1 = min(ds), max(ds)
    span = d1 - d0
    for loop in face.loops:
        co = loop.vert.co
        u = (co.x * t.x + co.y * t.y) * PPM / ATLAS
        f = 0.5 if span < 1e-6 else (co.dot(slope) - d0) / span
        # half a texel in at each end, for the reason _inset gives
        loop[uvl].uv = (u, (ROOF_Y0 + 0.5 + f * (ROOF_H - 1.0)) / ATLAS)


def _uv_rect(face, uvl, rect, z0, zspan):
    x0, x1, y0, y1 = _inset(rect)
    t = _face_htan(face)
    ss = [l.vert.co.x * t.x + l.vert.co.y * t.y for l in face.loops]
    s0, s1 = min(ss), max(ss)
    length = s1 - s0
    for loop in face.loops:
        co = loop.vert.co
        fu = 0.5 if length < 1e-6 else ((co.x * t.x + co.y * t.y) - s0) / length
        fv = min(max((co.z - z0) / zspan, 0.0), 1.0)
        loop[uvl].uv = ((x0 + fu * (x1 - x0)) / ATLAS,
                        (y0 + fv * (y1 - y0)) / ATLAS)


def _uv_patch(face, uvl, rect):
    x0, x1, y0, y1 = rect
    uv = ((x0 + x1) / 2.0 / ATLAS, (y0 + y1) / 2.0 / ATLAS)
    for loop in face.loops:
        loop[uvl].uv = uv


def apply_region(faces, region, uvl):
    for f in faces:
        f.normal_update()
        if region == "facade":
            _uv_facade(f, uvl)
        elif region == "fascia":
            # The fascia stands above the wall top, so shift it down onto the
            # band the atlas already draws as the topmost trim course.
            _uv_facade(f, uvl, z_shift=FASCIA_H)
        elif region == "quoin":
            _uv_rect(f, uvl, QUOIN, 0.0, Z_EAVE)
        elif region == "balus":
            _uv_rect(f, uvl, BALUS, BALC_RAIL_Z[0], BALC_RAIL_Z[1])
        elif region == "balus_side":
            # take a slice of the rail artwork as wide as the return is deep,
            # so the balusters keep the same pitch as on the front
            front_w = BALC_FRONT[1] - BALC_FRONT[0]
            side_d = BALC_SIDES[0][3] - BALC_SIDES[0][2]
            span = (BALUS[1] - BALUS[0]) * side_d / front_w
            _uv_rect(f, uvl, (BALUS[0], BALUS[0] + span, BALUS[2], BALUS[3]),
                     BALC_RAIL_Z[0], BALC_RAIL_Z[1])
        elif region == "roof":
            _uv_roof(f, uvl)
        elif region == "entrance":
            _uv_rect(f, uvl, ENT, 0.0, 11.4)
        elif region == "tower":
            _uv_rect(f, uvl, TOW, Z_EAVE, TOWER_TOP - Z_EAVE)
        elif region == "attic":
            _uv_rect(f, uvl, ATT, Z_EAVE, 5.2)
        elif region == "clock":
            # mapped from world position, not the face's own extents, so the
            # dial lands on the painted clock rather than stretching the whole
            # attic artwork across itself
            x0r, x1r, y0r, y1r = ATT
            for loop in f.loops:
                co = loop.vert.co
                fu = min(max((co.x + 4.0) / 8.0, 0.0), 1.0)
                fv = min(max((co.z - Z_EAVE) / 5.2, 0.0), 1.0)
                loop[uvl].uv = ((x0r + fu * (x1r - x0r)) / ATLAS,
                                (y0r + fv * (y1r - y0r)) / ATLAS)
        elif region == "chimney":
            _uv_rect(f, uvl, CHM, Z_EAVE, CHIM_TOP - Z_EAVE)
        elif region == "trim":
            _uv_patch(f, uvl, TRIMP)
        elif region == "reveal":
            _uv_patch(f, uvl, REVEALP)
        elif region == "soot":
            _uv_patch(f, uvl, SOOT)
        else:
            _uv_patch(f, uvl, BLANK)


# -------------------------------------------------------------- primitives

def _vcache(bm):
    cache = {}

    def dv(co):
        key = (round(co[0], 4), round(co[1], 4), round(co[2], 4))
        if key not in cache:
            cache[key] = bm.verts.new(co)
        return cache[key]
    return dv


def _mkface(bm, verts):
    uniq = []
    for v in verts:
        if not uniq or uniq[-1] is not v:
            uniq.append(v)
    if len(uniq) > 2 and uniq[0] is uniq[-1]:
        uniq.pop()
    if len(uniq) < 3:
        return None
    try:
        return bm.faces.new(uniq)
    except ValueError:
        return None


def box(bm, x0, x1, y0, y1, z0, z1, top=False, bottom=True):
    """Returns (sides, caps). Sides are ordered -Y, +X, +Y, -X."""
    dv = _vcache(bm)
    a, b, c, d = dv((x0, y0, z0)), dv((x1, y0, z0)), dv((x1, y1, z0)), dv((x0, y1, z0))
    e, f, g, h = dv((x0, y0, z1)), dv((x1, y0, z1)), dv((x1, y1, z1)), dv((x0, y1, z1))
    sides = [_mkface(bm, [a, b, f, e]), _mkface(bm, [b, c, g, f]),
             _mkface(bm, [c, d, h, g]), _mkface(bm, [d, a, e, h])]
    caps = []
    if bottom:
        caps.append(_mkface(bm, [d, c, b, a]))
    if top:
        caps.append(_mkface(bm, [e, f, g, h]))
    return [s for s in sides if s], [c for c in caps if c]


def chimney(bm, uvl, x0, x1, y0, y1, z0, z1):
    """A stack open at the top: its capped rim round one flue, which is sunk
    FLUE_DEPTH and lined and floored in soot. Every tier keeps the recess:
    painted flush, the soot lies in the sun and reads as dark grey, barely
    apart from the cap, where the shaded shaft reads black."""
    dv = _vcache(bm)
    w, zf = FLUE_WALL, z1 - FLUE_DEPTH
    out = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    inn = [(x0 + w, y0 + w), (x1 - w, y0 + w), (x1 - w, y1 - w), (x0 + w, y1 - w)]
    stack, soot = [], []
    for k in range(4):
        (ax, ay), (bx, by) = out[k], out[(k + 1) % 4]
        (cx, cy), (dx, dy) = inn[k], inn[(k + 1) % 4]
        stack.append(_mkface(bm, [dv((ax, ay, z0)), dv((bx, by, z0)),
                                  dv((bx, by, z1)), dv((ax, ay, z1))]))
        stack.append(_mkface(bm, [dv((ax, ay, z1)), dv((bx, by, z1)),
                                  dv((dx, dy, z1)), dv((cx, cy, z1))]))
        # walked the other way round, so the lining faces into the flue
        soot.append(_mkface(bm, [dv((dx, dy, zf)), dv((cx, cy, zf)),
                                 dv((cx, cy, z1)), dv((dx, dy, z1))]))
    stack.append(_mkface(bm, [dv((x, y, z0)) for x, y in reversed(out)]))
    soot.append(_mkface(bm, [dv((x, y, zf)) for x, y in inn]))
    apply_region([f for f in stack if f], "chimney", uvl)
    apply_region([f for f in soot if f], "soot", uvl)


def union_outline(rects, grow=0.0):
    """Ordered plan polygon of the union of axis-aligned *rects*, CCW from above.

    The massing is described as overlapping rectangles because that is the
    natural way to think about wings and pavilions, but building each one as
    its own closed box leaves every overlap as a pair of walls buried inside
    the shell — a set of complete interior partitions, windows and all, that
    nothing can ever see. Walls are built from this outline instead, so the
    mesh is the boundary of the union and interior geometry cannot occur by
    construction rather than having to be cleaned up afterwards.

    Same construction roof_solid uses for the roof: lay the rects out as
    non-overlapping cells on the grid of their own edges, keep the cells that
    fall inside any rect, and dissolve them into one n-gon. *grow* expands each
    rect first, which is how the roof gets its overhang.

    Collinear vertices are dropped here rather than by dissolve_verts: for the
    roof they were harmless, but a wall split at one would become two panels
    that each pick their own bay count, which scrambles the facade rhythm
    across a join that is not actually a corner.
    """
    ex = [(x0 - grow, x1 + grow, y0 - grow, y1 + grow) for x0, x1, y0, y1 in rects]
    xs = sorted({v for r in ex for v in (r[0], r[1])})
    ys = sorted({v for r in ex for v in (r[2], r[3])})
    bm = bmesh.new()
    dv = _vcache(bm)
    cells = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2.0, (ys[j] + ys[j + 1]) / 2.0
            if not any(r[0] < cx < r[1] and r[2] < cy < r[3] for r in ex):
                continue
            f = _mkface(bm, [dv((xs[i], ys[j], 0.0)), dv((xs[i + 1], ys[j], 0.0)),
                             dv((xs[i + 1], ys[j + 1], 0.0)),
                             dv((xs[i], ys[j + 1], 0.0))])
            if f:
                cells.append(f)
    region = bmesh.ops.dissolve_faces(bm, faces=cells, use_verts=False)["region"]
    if len(region) != 1:
        bm.free()
        raise ValueError(
            "massing does not dissolve to one outline (%d regions) — the rects "
            "must form a single connected, hole-free footprint" % len(region))
    poly = [(l.vert.co.x, l.vert.co.y) for l in region[0].loops]
    bm.free()

    out = []
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by), (cx, cy) = poly[i - 1], poly[i], poly[(i + 1) % n]
        if abs((bx - ax) * (cy - by) - (by - ay) * (cx - bx)) > 1e-9:
            out.append((bx, by))
    # CCW, so wall_panel's outward normal really points out of the building.
    m = len(out)
    area = sum(out[i][0] * out[(i + 1) % m][1] - out[(i + 1) % m][0] * out[i][1]
               for i in range(m))
    if area < 0.0:
        out.reverse()
    return out


def is_convex(poly, i):
    """True if corner *i* of the CCW outline *poly* turns outwards."""
    n = len(poly)
    (ax, ay), (bx, by), (cx, cy) = poly[i - 1], poly[i], poly[(i + 1) % n]
    return (bx - ax) * (cy - by) - (by - ay) * (cx - bx) > 0.0


def quoin_blocks(poly, proud=QUOIN_PROUD, depth=QUOIN_DEPTH):
    """One quoin block per convex corner of *poly*, as (x0, x1, y0, y1).

    Every convex corner gets one and no concave corner does, so the front and
    rear of the building are treated alike — which is the whole point of
    deriving them. A concave corner is an internal angle where two walls meet
    going inwards; there is no arris there to dress, and a block would simply
    fill the reentrant.

    The block straddles the corner, standing *proud* of both wall planes and
    wrapping *depth* back along each, which is what makes it read as a dressed
    stone corner rather than a pilaster stuck on one face.
    """
    n = len(poly)
    out = []
    for i in range(n):
        if not is_convex(poly, i):
            continue
        (ax, ay), (bx, by), (cx, cy) = poly[i - 1], poly[i], poly[(i + 1) % n]
        nx = ny = 0.0
        for (px, py), (qx, qy) in (((ax, ay), (bx, by)), ((bx, by), (cx, cy))):
            tx, ty = qx - px, qy - py
            length = math.hypot(tx, ty)
            if length < 1e-9:
                continue
            ex, ey = ty / length, -tx / length     # outward normal, CCW winding
            if abs(ex) > abs(ey):
                nx = ex
            else:
                ny = ey
        xs = sorted((bx + proud * nx, bx - depth * nx))
        ys = sorted((by + proud * ny, by - depth * ny))
        out.append((xs[0], xs[1], ys[0], ys[1]))
    return out


def roof_solid(bm, rects, z, over, fascia_h, run, rise):
    """One continuous roof over the union of *rects*.

    Built as a single solid so the slopes exist only on the building's outer
    perimeter and the top is one flat deck. Per-mass hips cannot do this: where
    two masses abut, each slopes down to its own eave and back up again, which
    cuts a deep valley through what should be continuous deck.

    Profile outward from the wall face: soffit horizontal at *z*, fascia up
    *fascia_h* at the outer edge, then the slope rising *rise* over *run* to
    the deck. Returns (soffit, fascia, slopes, deck, floor) face lists.
    """
    # Union outline of the rects already grown by the overhang, as
    # non-overlapping cells on the grid of their edges, dissolved into one
    # n-gon. Growing the rects up front avoids needing an outward inset, which
    # inset_region does not perform reliably. The resulting face is both the
    # soffit — the visible underside of the overhang — and the attic floor;
    # they are coplanar, so one face serves for both.
    ex = [(x0 - over, x1 + over, y0 - over, y1 + over) for x0, x1, y0, y1 in rects]
    xs = sorted({v for r in ex for v in (r[0], r[1])})
    ys = sorted({v for r in ex for v in (r[2], r[3])})
    dv = _vcache(bm)
    cells = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx = (xs[i] + xs[i + 1]) / 2.0
            cy = (ys[j] + ys[j + 1]) / 2.0
            if not any(r[0] < cx < r[1] and r[2] < cy < r[3] for r in ex):
                continue
            f = _mkface(bm, [dv((xs[i], ys[j], z)), dv((xs[i + 1], ys[j], z)),
                             dv((xs[i + 1], ys[j + 1], z)), dv((xs[i], ys[j + 1], z))])
            if f:
                cells.append(f)
    # use_verts must stay off: it dissolves any vertex left with two edges,
    # which includes the outline's genuine right-angle corners, not just
    # collinear ones. That turns each step into a diagonal and sends the roof
    # cantilevering across the courtyard. The collinear verts it would have
    # removed are harmless — a few extra quads in the slope ring.
    floor = bmesh.ops.dissolve_faces(bm, faces=cells, use_verts=False)["region"]
    # Now drop only the vertices that are genuinely collinear, testing each
    # one, rather than letting dissolve_faces take every 2-edge vertex.
    flat = []
    # Sorted, because a set of BMVerts iterates in memory-address order, and
    # the order they are dissolved in decides where the deck n-gon's loop
    # starts — and so how it triangulates on export, run to run.
    for v in sorted({v for f in floor for v in f.verts},
                    key=lambda v: (v.co.x, v.co.y, v.co.z)):
        if len(v.link_edges) != 2:
            continue
        a, b = (e.other_vert(v) for e in v.link_edges)
        d1, d2 = v.co - a.co, b.co - v.co
        if d1.length < 1e-9 or d2.length < 1e-9:
            continue
        if d1.normalized().cross(d2.normalized()).length < 1e-6:
            flat.append(v)
    if flat:
        bmesh.ops.dissolve_verts(bm, verts=flat)
        floor = [f for f in bm.faces if f.is_valid and
                 all(abs(l.vert.co.z - z) < 1e-6 for l in f.loops) and
                 len(f.verts) > 4]

    def outer_edges(faces):
        seen = {}
        for f in faces:
            for e in f.edges:
                seen[e] = seen.get(e, 0) + 1
        return [e for e, n in seen.items() if n == 1]

    ring = outer_edges(list(floor))
    ext = bmesh.ops.extrude_edge_only(bm, edges=ring)["geom"]
    new_v = [g for g in ext if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_v, vec=(0.0, 0.0, fascia_h))
    fascia = [g for g in ext if isinstance(g, bmesh.types.BMFace)]
    top_edges = [g for g in ext if isinstance(g, bmesh.types.BMEdge)
                 and all(v in new_v for v in g.verts)]
    deck = bmesh.ops.contextual_create(bm, geom=top_edges)["faces"]
    # inset_region applies depth along the face normal, and a face built from a
    # loop can come back pointing down — which would drive the whole roof
    # inwards and 3 m below the eave instead of up to a deck.
    for f in deck:
        f.normal_update()
        if f.normal.z < 0.0:
            f.normal_flip()
    slopes = bmesh.ops.inset_region(bm, faces=deck, thickness=run, depth=rise,
                                    use_even_offset=True)["faces"]
    return fascia, slopes, deck, list(floor)


def frustum(bm, x0, x1, y0, y1, z0, tx0, tx1, ty0, ty1, z1, cap=False):
    dv = _vcache(bm)
    b1, b2 = dv((x0, y0, z0)), dv((x1, y0, z0))
    b3, b4 = dv((x1, y1, z0)), dv((x0, y1, z0))
    d1, d2 = dv((tx0, ty0, z1)), dv((tx1, ty0, z1))
    d3, d4 = dv((tx1, ty1, z1)), dv((tx0, ty1, z1))
    out = [_mkface(bm, [b1, b2, d2, d1]), _mkface(bm, [b2, b3, d3, d2]),
           _mkface(bm, [b3, b4, d4, d3]), _mkface(bm, [b4, b1, d1, d4])]
    if cap:
        out.append(_mkface(bm, [d1, d2, d3, d4]))
    return [f for f in out if f]


def gable(bm, x0, x1, y0, y1, zb, apex_z):
    """Pediment prism, open at the base. Returns (front, back, rakes)."""
    dv = _vcache(bm)
    xm = (x0 + x1) / 2.0
    a, b, c = dv((x0, y0, zb)), dv((x1, y0, zb)), dv((xm, y0, apex_z))
    d, e, f = dv((x0, y1, zb)), dv((x1, y1, zb)), dv((xm, y1, apex_z))
    front = _mkface(bm, [a, b, c])
    back = _mkface(bm, [e, d, f])
    rakes = [_mkface(bm, [b, e, f, c]), _mkface(bm, [d, a, c, f])]
    return front, back, [r for r in rakes if r]


# ------------------------------------------------------------------- build

def clock_dial(bm, cx, cz, y_face, depth, radius, segs=16):
    """The clock dial as a shallow faceted cylinder standing proud of the wall.

    A singular fixture rather than repeated trim: a painted circle only reads
    as a dial head-on, where a real disc keeps its round silhouette and catches
    light on its rim from any angle. One per building, so there is no
    multiplication risk in modelling it.
    """
    import math
    dv = _vcache(bm)
    front, back = [], []
    for i in range(segs):
        a = 2.0 * math.pi * i / segs
        x = cx + math.cos(a) * radius
        z = cz + math.sin(a) * radius
        front.append(dv((x, y_face - depth, z)))
        back.append(dv((x, y_face, z)))
    rim = []
    for i in range(segs):
        j = (i + 1) % segs
        f = _mkface(bm, [back[i], back[j], front[j], front[i]])
        if f:
            rim.append(f)
    face = _mkface(bm, list(reversed(front)))
    cap = _mkface(bm, back)
    return [f for f in (face,) if f], [f for f in rim + [cap] if f]


def wall_panel(bm, p0, p1, z_cuts, openings, breaks=()):
    """One wall elevation, banded so openings can be cut without gridding the
    whole face. Returns (wall, glass, reveal, bottom_ring, top_ring).

    *openings* is a list of (centre_s, half_width, z0, z1) in panel-local
    coordinates, s measured along the panel from p0. *breaks* are further s
    positions to split the wall at without cutting anything, so a stretch of
    it can take its own mapping.

    Every band is split at the same s breakpoints, and every column at the
    same z breakpoints, so the quads above and below an opening share its
    vertices. A T-junction there would leave the opening's edge carrying one
    face instead of two.
    """
    span = p1 - p0
    length = span.length
    t = span / length
    n = Vector((t.y, -t.x, 0.0))            # outward from the wall
    dv = _vcache(bm)

    def P(s, z, d=0.0):
        q = p0 + t * s - n * d
        return (q.x, q.y, z)

    def quad(sa, sb, za, zb, d=0.0):
        return _mkface(bm, [dv(P(sa, za, d)), dv(P(sb, za, d)),
                            dv(P(sb, zb, d)), dv(P(sa, zb, d))])

    cuts = sorted({0.0, length} | set(breaks) |
                  {min(max(c + k * hw, 0.0), length)
                   for c, hw, _, _, _ in openings for k in (-1, 1)})
    zs = list(z_cuts)

    # Which opening owns each cell, or -1. An opening wider than its
    # neighbours' breakpoints spans several cells, so reveals must be emitted
    # on its outer perimeter only — putting them on the internal seams too is
    # what over-connects those edges.
    grid = []
    for zi in range(len(zs) - 1):
        zm = (zs[zi] + zs[zi + 1]) / 2.0
        row = []
        for si in range(len(cuts) - 1):
            sm = (cuts[si] + cuts[si + 1]) / 2.0
            own = -1
            for c, hw, z0, z1, gid in openings:
                if abs(c - sm) < hw - 1e-6 and z0 - 1e-6 < zm < z1 + 1e-6:
                    own = gid
                    break
            row.append(own)
        grid.append(row)

    wall, glass, reveal = [], [], []
    for zi in range(len(zs) - 1):
        za, zb = zs[zi], zs[zi + 1]
        for si in range(len(cuts) - 1):
            sa, sb = cuts[si], cuts[si + 1]
            own = grid[zi][si]
            if own == -1:
                f = quad(sa, sb, za, zb)
                if f:
                    wall.append(f)
                continue
            f = quad(sa, sb, za, zb, WIN_DEPTH)
            if f:
                glass.append(f)
            nb = [grid[zi][si - 1] if si > 0 else -1,                      # left
                  grid[zi][si + 1] if si + 1 < len(grid[zi]) else -1,      # right
                  grid[zi - 1][si] if zi > 0 else -1,                      # below
                  grid[zi + 1][si] if zi + 1 < len(grid) else -1]          # above
            # same group id means an internal seam of a stepped opening
            ring = [(sa, za), (sb, za), (sb, zb), (sa, zb)]
            for k, side in enumerate((2, 1, 3, 0)):    # bottom, right, top, left
                if nb[side] == own:
                    continue
                s0, t0 = ring[k]
                s1, t1 = ring[(k + 1) % 4]
                rf = _mkface(bm, [dv(P(s0, t0)), dv(P(s1, t1)),
                                  dv(P(s1, t1, WIN_DEPTH)), dv(P(s0, t0, WIN_DEPTH))])
                if rf:
                    reveal.append(rf)

    bottom = [dv(P(s, zs[0])) for s in cuts[:-1]]
    top = [dv(P(s, zs[-1])) for s in cuts[:-1]]
    return wall, glass, reveal, bottom, top, t, length


def wall_with_openings(bm, plan, z_top, uvl, opening_fn):
    """One closed wall ring following *plan*, its elevations carrying openings.

    *plan* is the building's whole plan outline as a list of Vectors, counter-
    clockwise seen from above so each panel's outward normal points out of the
    building. It comes from union_outline, so every panel is exterior surface
    and the ring encloses one empty volume — there is nothing inside it.

    *opening_fn(index, p0, p1, length)* returns the opening list for that
    elevation, a callable that maps its faces into the atlas, and any extra
    breakpoints for wall_panel. It gets the
    segment's endpoints, not just its index, because which elevation is which
    is a question about where a wall is, and an outline's segment order is an
    accident of where the tracing started.
    """
    panels = []
    for i in range(len(plan)):
        p0, p1 = plan[i], plan[(i + 1) % len(plan)]
        openings, uvfn, breaks = opening_fn(i, p0, p1, (p1 - p0).length)
        panels.append((p0, p1, openings, uvfn, breaks))

    # One z-breakpoint set for the whole ring. Per-panel breakpoints leave the
    # shared corner edge with vertices on one side only, and every one of those
    # is a T-junction carrying a single face.
    z_cuts = sorted({0.0, z_top} | {z for _, _, ops, _, _ in panels
                                    for _, _, z0, z1, _ in ops for z in (z0, z1)})

    bottom_ring, top_ring = [], []
    for p0, p1, openings, uvfn, breaks in panels:
        wall, glass, reveal, bot, top, t, length = wall_panel(
            bm, p0, p1, z_cuts, openings, breaks)
        for f in wall + glass:
            f.normal_update()
            uvfn(f, p0, t, length)
        apply_region(reveal, "reveal", uvl)
        bottom_ring += bot
        top_ring += top
    # Caps follow the full perimeter rings, so the panels' intermediate
    # vertices are shared rather than left as T-junctions.
    caps = [f for f in (_mkface(bm, list(reversed(bottom_ring))),
                        _mkface(bm, top_ring)) if f]
    apply_region(caps, "blank", uvl)


def is_court_wall(p0, p1):
    """True for the seven walls inside the U-court, which LOD1 bakes flat."""
    return all(abs(p.x) < COURT_X + 1e-6 and p.y > COURT_Y - 1e-6
               for p in (p0, p1))


def cuts_openings(level, p0, p1):
    """Whether this tier cuts the openings of the wall from *p0* to *p1*.

    Reveals are LOD0 and LOD1 detail, per CLAUDE.md. LOD0 cuts them on every
    elevation, the courtyard included, because a town hall is placed once per
    district and seen from all round. LOD1, from 35 m out, keeps them wherever
    a street camera can see and bakes the U-court, which it can only look into
    from behind and past the wings. That court is about 1,220 of LOD0's
    triangles, and baking it is what separates the two tiers.
    """
    if level == 0:
        return True
    return level == 1 and not is_court_wall(p0, p1)


def tower_crown(bm, uvl, level):
    """Balustraded platform, dome, ball and flagpole, on the tower shaft.

    Kept whole through LOD2: this is how the building is recognised from a
    distance. At LOD3, beyond 120 m, the dome's two stages merge into one,
    which moves its profile by 0.13 m at the break, about a pixel there,
    and the ball goes into the pole. Its outline and the flagpole's tip
    stay where they are at every tier.
    """
    w, yc = TOWER_W, TOWER_YC
    d0, d1, d2 = TOWER_DOME
    m, t = DOME_MID_W, DOME_TOP_W
    # Balustraded platform: it breaks the shaft against the sky, so it is
    # silhouette rather than applied trim.
    p = w + 0.35
    psides, pcaps = box(bm, -p, p, yc - p, yc + p,
                        TOWER_PLAT[0], TOWER_PLAT[1], top=True)
    apply_region(psides, "tower", uvl)
    apply_region(pcaps, "trim", uvl)
    # Each stage is capped where nothing wider sits on it, so no ring is left
    # open; an open ring is 4 non-manifold edges.
    if level < 3:
        apply_region(frustum(bm, -w, w, yc - w, yc + w, d0,
                             -m, m, yc - m, yc + m, d1), "roof", uvl)
        apply_region(frustum(bm, -m, m, yc - m, yc + m, d1,
                             -t, t, yc - t, yc + t, d2, cap=True), "roof", uvl)
        # Ball and pole sink into what they stand on, so no coincident planes.
        bsides, bcaps = box(bm, -0.20, 0.20, yc - 0.20, yc + 0.20,
                            TOWER_BALL[0] - 0.10, TOWER_BALL[1], top=True)
        apply_region(bsides + bcaps, "trim", uvl)
        pole_foot = TOWER_BALL[1] - 0.10
    else:
        apply_region(frustum(bm, -w, w, yc - w, yc + w, d0,
                             -t, t, yc - t, yc + t, d2, cap=True), "roof", uvl)
        pole_foot = d2 - 0.10
    # A thin flagpole rather than a solid spire. At 0.18 m it is under two
    # pixels wide beyond 120 m, but it sets the tip of the skyline, so it
    # stays at every tier.
    fsides, fcaps = box(bm, -0.09, 0.09, yc - 0.09, yc + 0.09,
                        pole_foot, TOWER_POLE, top=True)
    apply_region(fsides + fcaps, "trim", uvl)


def build_lod(level):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")

    # One wall ring on the union outline, at every tier. The masses overlap by
    # design, so building each as its own box left both sides of every overlap
    # standing inside the shell: complete interior partition walls, carrying
    # their own cut windows, reveals and glass. Taking the outline first means
    # only surfaces that are actually outside the building get built.
    outline = union_outline(WALLS)
    plan = [Vector((x, y, 0.0)) for x, y in outline]

    # Below LOD1 the quoin blocks go, but the white corners are the facade's
    # strongest vertical line, and losing them at the 70 m switch reads as
    # the building changing. So from LOD2 each wall is split QUOIN_DEPTH in
    # from every convex corner and that strip maps the same atlas region the
    # blocks do — CLAUDE.md's other allowed form of a quoin.
    strips = [] if level < 2 else \
        [is_convex(outline, i) for i in range(len(outline))]

    def opening_fn(i, p0, p1, length):
        cut = cuts_openings(level, p0, p1)
        ends = []
        if strips and strips[i]:
            ends.append((0.0, QUOIN_DEPTH))
        if strips and strips[(i + 1) % len(outline)]:
            ends.append((length - QUOIN_DEPTH, length))
        breaks = [b for e in ends for b in e]

        def in_strip(f, q0, t):
            ss = [(l.vert.co - q0).dot(t) for l in f.loops]
            return any(a - 1e-6 <= min(ss) and max(ss) <= b + 1e-6
                       for a, b in ends)

        if abs(p0.y + 10.2) < 1e-6 and abs(p1.y + 10.2) < 1e-6 \
                and abs(p0.x + 5.5) < 1e-6 and abs(p1.x - 5.5) < 1e-6:
            # The entrance frontage reads the unique ENT artwork at every
            # tier, cut or flat. Matched on its actual position rather than a
            # segment index; the outline yields it as one 11.0 m run, so
            # ENTRANCE_OPENINGS' s = x + 5.5 still holds.
            def uvfn(f, q0, t, L):
                if in_strip(f, q0, t):
                    apply_region([f], "quoin", uvl)
                else:
                    _uv_panel_rect(f, uvl, q0, t, L, ENT, 0.0, 11.4)
            return (ENTRANCE_OPENINGS if cut else []), uvfn, breaks
        openings, nbay = _bay_openings(length)

        def uvfn(f, q0, t, L, nbay=nbay):
            if in_strip(f, q0, t):
                apply_region([f], "quoin", uvl)
            else:
                _uv_panel_facade(f, uvl, q0, t, L, nbay)
        return (openings if cut else []), uvfn, breaks

    wall_with_openings(bm, plan, Z_EAVE + WALL_TUCK, uvl, opening_fn)

    # One roof over the whole union: slopes only on the outer perimeter, a
    # single flat deck on top. The overhang is kept at every tier — the rules
    # allow dropping it at LOD3, but one construction path is worth more than
    # the handful of faces it would save.
    fascia, slopes, deck, floor = roof_solid(
        bm, WALLS, Z_EAVE, EAVE_OVER, FASCIA_H, ROOF_RUN, ROOF_RISE)
    apply_region(fascia, "fascia", uvl)
    apply_region(slopes, "roof", uvl)
    apply_region(deck, "roof", uvl)
    apply_region(floor, "trim", uvl)   # soffit underside; also the attic floor

    # Pedimented clock attic, at every tier: the pediment breaks the roofline.
    # Only the front reads the clock; returns and rakes are trim.
    sides, caps = box(bm, -4.0, 4.0, -10.2, -8.4, Z_EAVE, 14.6, top=False)
    apply_region([sides[0]], "attic", uvl)
    apply_region(sides[1:], "trim", uvl)
    apply_region(caps, "blank", uvl)
    front, back, rakes = gable(bm, -4.0, 4.0, -10.2, -8.4, 14.6, 16.4)
    apply_region([front], "attic", uvl)
    apply_region([back] + rakes, "trim", uvl)
    # The modelled dial stands 0.10 m proud, well under the 0.25 m test, and
    # is allowed as a singular fixture for its round outline. That outline is
    # detail rather than silhouette, so from LOD2 the painted dial beneath it
    # carries the clock alone.
    if level < 2:
        dial, rim = clock_dial(bm, 0.0, 13.25, -10.2, 0.10, 0.98)
        apply_region(dial, "clock", uvl)
        apply_region(rim, "trim", uvl)

    # Balcony over the main entrance: slab, solid parapet, soffit. The
    # balusters stay in the texture — cutting between them would need the
    # masked transparency Texture Requirements rules out. Its back face is
    # buried in the bay wall rather than coplanar with it, so nothing z-fights.
    # Kept at every tier, LOD3 included, where the rules would let it go: it
    # is the frontmost thing on the building, so dropping it moves the
    # bounds, and with them the pivot every tier is placed by.
    s_sides, s_caps = box(bm, *BALC_SLAB, top=True)
    apply_region(s_sides + s_caps, "trim", uvl)
    f_sides, f_caps = box(bm, *BALC_FRONT, top=True)
    apply_region([f_sides[0]], "balus", uvl)
    apply_region(f_sides[1:] + f_caps, "trim", uvl)
    for rect in BALC_SIDES:
        p_sides, p_caps = box(bm, *rect, top=True)
        apply_region(p_sides, "balus_side", uvl)
        apply_region(p_caps, "trim", uvl)

    # Quoined corner blocks on every convex corner of the outline, front and
    # rear alike. Fine detail rather than silhouette: they survive LOD1 and
    # collapse below it, as CLAUDE.md has quoins do.
    if level < 2:
        for qx0, qx1, qy0, qy1 in quoin_blocks(outline):
            q_sides, q_caps = box(bm, qx0, qx1, qy0, qy1, 0.0, Z_EAVE, top=True)
            apply_region(q_sides, "quoin", uvl)
            apply_region(q_caps, "blank", uvl)

    # tower shaft, then its crown
    w, yc = TOWER_W, TOWER_YC
    sides, caps = box(bm, -w, w, yc - w, yc + w, Z_EAVE, TOWER_TOP, top=False)
    apply_region(sides, "tower", uvl)
    apply_region(caps, "blank", uvl)
    tower_crown(bm, uvl, level)

    # Chimneys stand 1.65 m clear of the deck and show above the roof slope
    # from the street, so they are roofline rather than rooftop clutter, and
    # stay at every tier, open flues included. Dropped at LOD3 they left six
    # gaps in the skyline at the 120 m switch, each still about 12 x 16 px
    # there.
    for cx0, cx1, cy0, cy1, ctop in CHIMNEYS:
        chimney(bm, uvl, cx0, cx1, cy0, cy1, Z_EAVE, ctop)

    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # The roof's extrude and inset emit faces in memory-address order, so the
    # same mesh came out in a different face order every run. Sort by each
    # face's own corners, so a rebuild writes byte-identical files and a real
    # change shows up as a changed file.
    order = sorted(bm.faces, key=lambda f: [tuple(round(c, 4) for c in l.vert.co)
                                            for l in f.loops])
    rank = {f: i for i, f in enumerate(order)}
    bm.faces.sort(key=lambda f: rank[f])

    name = "{}_LOD{}".format(ASSET, level)
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(mesh)
    bm.free()
    return bpy.data.objects.new(name, mesh)


def check_massing(min_seg=1.0):
    """Guards against the massing errors this asset has actually hit.

    Both are invisible in the rect list and obvious only once rendered, which
    is the worst combination, so they are asserted at build time instead.

    A very short outline segment means two masses were meant to line up and
    missed. The wings once sat 0.8 m inside the end pavilions, which put a jog
    in each side elevation and stepped the eave and hip above it; it read as
    two misaligned buildings rather than as articulation. Anything below about
    a metre is far more likely to be that than a deliberate setback.

    Quoins no longer need checking for placement — quoin_blocks derives them
    from this same outline, so a stranded or missing one cannot occur. What can
    still occur is two convex corners close enough that their blocks collide,
    which min_seg also catches, since the blocks only overlap when the segment
    between them is shorter than they are.

    It also keeps each chimney's open flue inside its stack and clear of the
    roof deck below, and every door's threshold on the floor it opens onto:
    the sidecar once stated a ground floor 0.80 m above the entrance.
    """
    problems = []
    poly = union_outline(WALLS)
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        length = math.hypot(bx - ax, by - ay)
        if length < min_seg:
            problems.append(
                "outline segment (%.2f, %.2f)-(%.2f, %.2f) is only %.2f m; "
                "two masses probably missed alignment" % (ax, ay, bx, by, length))
    span = QUOIN_PROUD + QUOIN_DEPTH
    blocks = quoin_blocks(poly)
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            a, b = blocks[i], blocks[j]
            if (a[0] < b[1] and b[0] < a[1]) and (a[2] < b[3] and b[2] < a[3]):
                problems.append(
                    "quoin blocks at (%.2f, %.2f) and (%.2f, %.2f) overlap; "
                    "corners closer than %.2f m cannot both be dressed"
                    % ((a[0]+a[1])/2, (a[2]+a[3])/2,
                       (b[0]+b[1])/2, (b[2]+b[3])/2, span))
    deck = Z_EAVE + FASCIA_H + ROOF_RISE
    for cx0, cx1, cy0, cy1, ctop in CHIMNEYS:
        if ctop - FLUE_DEPTH < deck + 0.10:
            problems.append("the flue at (%.2f, %.2f) sinks to the roof deck"
                            % ((cx0 + cx1) / 2, (cy0 + cy1) / 2))
        if min(cx1 - cx0, cy1 - cy0) < 2 * FLUE_WALL + 0.30:
            problems.append("the stack at (%.2f, %.2f) is too slim for its flue"
                            % ((cx0 + cx1) / 2, (cy0 + cy1) / 2))
    # Every door opens onto a floor: its threshold on a storey's floor or at
    # most a sill's 0.10 m above it, never a flight of steps away from it.
    for _s, _hw, z0, _z1, tag in ENTRANCE_OPENINGS:
        if tag in DOOR_TAGS and not any(0.0 <= z0 - f <= 0.10 + 1e-6
                                        for f in (Z_GROUND_FLOOR, Z_UPPER_FLOOR)):
            problems.append("the %s door's threshold at %.2f m meets no floor"
                            % (tag, z0))
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_massing, build_lod)


# =================================================================== facts
# The two storeys' floors are where the doors open onto them. The ground
# floor is the entrance's threshold, 0.15 m up: the door is cut down to it
# through the plinth, over a painted threshold step, and the ground-floor
# sills stand 1.10 m above it. The 0.95 m plinth is the stone base course of
# the wall, not a floor level. The upper floor is the balcony's deck, on the
# string course's top (facade_atlas.py's Z_STRING_TOP): the balcony door's
# threshold stands 0.05 m above it and the upper sills 0.80 m. The entrance's
# pair of leaves ends at the transom, where facade_atlas.paint_entrance()
# draws it; the fanlight above is not part of the leaf.
Z_GROUND_FLOOR, Z_UPPER_FLOOR = 0.15, 5.55
DOOR_TRANSOM = 2.50
DOOR_TAGS = ("door", "bal")      # the ENTRANCE_OPENINGS that are doors


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the wall ring's own outline, without
    the quoin blocks that stand 0.08 m proud of it. Both storeys fill that
    outline: the upper one ends under the cornice, below the roof. The tower
    and the clock attic are not floors. The one door at ground level is the
    arched entrance in the centre bay, its threshold on the ground floor; the
    balcony door above it is in the same outer wall, onto the upper floor.
    The hall has no other outer door."""
    outline = union_outline(WALLS)
    n = len(outline)
    area = sum(outline[i][0] * outline[(i + 1) % n][1]
               - outline[(i + 1) % n][0] * outline[i][1] for i in range(n)) / 2.0
    x0, x1, y0, _y1 = WALLS[3]                      # the centre entrance bay
    p0, p1 = (x0, y0), (x1, y0)                     # its front, s = x + 5.5

    def door(door_id, kind, tag, top=None, main=False):
        s, hw, z0, z1, _ = next(o for o in ENTRANCE_OPENINGS if o[4] == tag)
        return model_facts.wall_door(door_id, kind, p0, p1, s, z0, 2.0 * hw,
                                     (top or z1) - z0, main)

    return {
        "hero": True,
        "dwellings": 0,
        "footprint": outline,
        "storeys": [(Z_GROUND_FLOOR, area), (Z_UPPER_FLOOR, area)],
        "doors": [door("front", "entrance", "door", DOOR_TRANSOM, main=True),
                  door("balcony", "balcony", "bal")],
    }


def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four
    orthographic elevations, a plan from above, and a raised three-quarter
    aerial off the front corner. Working views only — not committed."""
    preview_studio()
    _show_only(level)
    scn = bpy.context.scene
    saved = (scn.camera, scn.render.resolution_x, scn.render.resolution_y)
    scn.render.resolution_x, scn.render.resolution_y = res
    obj = bpy.data.objects["{}_LOD{}".format(ASSET, level)]
    lo = Vector([min(v.co[i] for v in obj.data.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in obj.data.vertices) for i in range(3)])
    centre, radius = (lo + hi) / 2.0, (hi - lo).length / 2.0
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
        cam.location = centre + Vector(d) * 150.0
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
    BUILD.main(build_all, facts)
