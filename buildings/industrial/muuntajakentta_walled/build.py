# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of muuntajakentta_walled, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, renders preview.png and writes the facts
sidecar:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

The walled transformer yard of a small mid-century Nordic coal-fired heat
and power plant: a 20.0 x 12.0 m compound behind a plain 1.56 m brick
perimeter wall with plain piers every 4-6 m, closed at the front by a
sheet-steel double gate. Inside, two power transformers stand on concrete
plinths either side of a concrete fire wall, their high-voltage bushings
toward the west (incoming) side. There, a galvanised lattice portal with
shield-wire peaks carries a suspension string over each phase, and between
it and each transformer stands that transformer's switchgear bay: a
disconnector on a tall steel table, three minimum-oil breaker poles on a
steel stand and three current transformers on a concrete table, joined by
slack flexible conductors. The small red brick switchgear house stands in
the front-east corner, its front and east walls in the yard wall's outer
planes, its steel door on the street.

Construction is a set of closed solids unioned with Blender's exact boolean
(asset_build.union): the switchgear house (one solid with its openings, slab
edge and roof), the wall's lengths between piers, its piers and the gate; per
transformer the plinth, tank, two radiator banks, the conservator and its
saddles, three bushings and the cable box; the fire wall; the gantry's
foundation pads, its columns' corner angles and six insulator strings; per
bay the switchgear's frames, posts, poles and current transformers and
twelve conductors. There is no ground: every solid stands on z = 0 or on
another solid. The lattice's bracing, chords and finials are closed solids
that touch nothing; they join the mesh after the union (build_lod()).

The yard has no glazing, so it has no emission map (CLAUDE.md, Output
Contract); BUILD below is asset_build.Asset with night_lit=False.
"""

import functools
import importlib
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector


HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import facade_atlas as L  # noqa: E402  (layout constants shared with the atlas)
importlib.reload(L)       # an interactive session must not keep a stale layout

ASSET = L.ASSET
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import model_facts  # noqa: E402
import shell_build as SB  # noqa: E402
from asset_build import to_object, union  # noqa: E402
from shell_build import InwardFrame as Frame  # noqa: E402  (P's third coordinate is depth)

asset_build.check_toolchain()
Builder = functools.partial(SB.Builder, L.ATLAS)


BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT, night_lit=False)
PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ------------------------------------------------------------------ the wall
# Plain pier centres along each run of the yard wall, at the corners, the
# gate and every 4-6 m between. The front run stops at the gate's west
# pier; the gate's east pier stands against the house's front corner; the
# east run starts at a pier against the house's north wall.
WCX0, WCX1, WCY = L.WCX0, L.WCX1, L.WCY
HW = L.WALL_T / 2.0
GATE_W_PIER = L.GATE_OPEN[0] - L.PIER_W / 2.0
GATE_E_PIER = L.GATE_OPEN[1] + L.PIER_W / 2.0
JUNCTION_Y = L.HY1               # the east run's pier against the house


def spaced(a, b, n):
    return [a + (b - a) * i / n for i in range(n + 1)]


PIERS_FRONT = [(x, -WCY) for x in spaced(WCX0, GATE_W_PIER, 2)] + [(GATE_E_PIER, -WCY)]
PIERS_WEST = [(WCX0, y) for y in spaced(-WCY, WCY, 2)[1:-1]]
PIERS_NORTH = [(x, WCY) for x in spaced(WCX0, WCX1, 4)]
PIERS_EAST = [(WCX1, y) for y in spaced(WCY, JUNCTION_Y, 2)[1:]]
PIERS = PIERS_FRONT + PIERS_WEST + PIERS_NORTH + PIERS_EAST

# Wall runs as (x0, x1, y0, y1), each ending inside a pier (or, the east
# run, inside the house) so no end face is left in the open.
RUNS = [
    (WCX0, GATE_W_PIER, -WCY - HW, -WCY + HW),          # front, west of the gate
    (WCX0 - HW, WCX0 + HW, -WCY, WCY),                  # west
    (WCX0, WCX1, WCY - HW, WCY + HW),                   # north
    (WCX1 - HW, WCX1 + HW, JUNCTION_Y - 0.10, WCY),     # east
]


def between_piers(runs, piers, into, lift):
    """Each run as the lengths between the piers on its centre line, each
    running *into* into the pier at either end and standing *lift* off the
    ground, (x0, x1, y0, y1, z0). With the piers PIER_PROUD over the wall's
    top, each length's end is buried in its pier with no face coplanar with
    the pier's, so the union cuts one clean hole in the pier's side; threading
    every pier onto one long run, flush top and bottom, cost 240 more
    triangles."""
    out = []
    for x0, x1, y0, y1 in runs:
        if x1 - x0 > y1 - y0:
            c = (y0 + y1) / 2.0
            on = sorted(x for x, y in piers if abs(y - c) < EPS and x0 - EPS <= x <= x1 + EPS)
            out += [(a + PW / 2 - into, b - PW / 2 + into, y0, y1, lift)
                    for a, b in zip(on, on[1:])]
        else:
            c = (x0 + x1) / 2.0
            on = sorted(y for x, y in piers if abs(x - c) < EPS and y0 - EPS <= y <= y1 + EPS)
            out += [(x0, x1, a + PW / 2 - into, b - PW / 2 + into, lift)
                    for a, b in zip(on, on[1:])]
    return out


# LOD3's wall is one pier thick, its outer faces the piers', so the piers
# fold into it and the plan bounds stay theirs; the gate's east pier and the
# junction pier become the short run into the house and the east run's foot.
FX0, FX1, FY, PW = L.FX0, L.FX1, L.FY, L.PIER_W
RUNS_THICK = [
    (FX0, L.GATE_OPEN[0], -FY, -FY + PW),
    (L.GATE_OPEN[1], L.HX0 + 0.04, -FY, -FY + PW),
    (FX0, FX0 + PW, -FY, FY),
    (FX0, FX1, FY - PW, FY),
    (FX1 - PW, FX1, JUNCTION_Y - PW / 2.0, FY),
]
RUN_SEGS = between_piers(RUNS, PIERS, 0.05, 0.001)

# ----------------------------------------------------------------- the house
HX0, HX1, HY0, HY1 = L.HX0, L.HX1, L.HY0, L.HY1
HI, LO = L.Z_LOUVRE_HI, L.Z_LOUVRE_LO
# Each wall runs counter-clockwise seen from above, outward face on its
# right; s runs along it from p0. items: (kind, s at the centre, z of the
# sill or threshold).
# Every opening's casing sides on whole or half stretchers in the U its wall
# samples, u_off from facade_atlas.HOUSE_U_OFF (brick_problems()).
H_WALLS = [
    dict(name="front", p0=(HX0, HY0), p1=(HX1, HY0),
         items=[("door", 1.3125, 0.0), ("louvre", 3.50, HI)]),
    dict(name="east", p0=(HX1, HY0), p1=(HX1, HY1),
         items=[("louvre", 1.25, HI), ("louvre", 2.75, HI)]),
    dict(name="north", p0=(HX1, HY1), p1=(HX0, HY1),
         items=[("louvre", 1.375, HI)]),
    dict(name="west", p0=(HX0, HY1), p1=(HX0, HY0),
         items=[("louvre", 2.00, LO)]),
]
for _spec in H_WALLS:
    _spec["u_off"] = L.HOUSE_U_OFF[_spec["name"]]

# ------------------------------------------------------------ the transformers
TX = L.T_X
PH = (-1, 0, 1)                  # phases: multiples of L.PHASE (bushings) or
                                 # L.SW_PHASE (switchgear) across Y


def bushing_xy(ty, k):
    return TX + L.BUSH_X, ty + k * L.PHASE


def string_top():
    """GAP under the truss's bottom rail (or the slim truss's bottom)."""
    return L.G_BEAM_Z[0] - L.G_GAP


# Terminal heights the conductors join, each inside its part on every tier.
Z_CLAMP = string_top() - L.STRING_LEN + 0.04
Z_POST_TOP = L.POST_Z0 + L.POST_H - 0.05
Z_BRK_TOP = L.BRK_Z0 + (L.Z_BRK[2] + L.Z_BRK[3]) / 2.0
Z_BRK_MID = L.BRK_Z0 + (L.Z_BRK[0] + L.Z_BRK[1]) / 2.0
Z_CT_HEAD = L.CT_Z0 + (L.Z_CT[1] + L.Z_CT[2]) / 2.0
Z_TERM = L.TANK_Z[1] - 0.05 + L.BUSH_H - 0.05


def spans(ty, k):
    """One phase's conductors, (p0, p1, sag, kind): the slack drop from the
    string's clamp to the disconnector's incoming post, then near-level
    spans from its outgoing post to the breaker's top head, from the
    breaker's mid head to the current transformer's head, and from there to
    the transformer's bushing. Each end is buried in the part it joins."""
    ys = ty + k * L.SW_PHASE
    bx, by = bushing_xy(ty, k)
    return [
        (Vector((L.G_X, ys, Z_CLAMP)), Vector((L.DIS_X[0], ys, Z_POST_TOP)), 0.35, "drop"),
        (Vector((L.DIS_X[1], ys, Z_POST_TOP)), Vector((L.BRK_X - 0.04, ys, Z_BRK_TOP)),
         0.14, "span"),
        (Vector((L.BRK_X + 0.04, ys, Z_BRK_MID)), Vector((L.CT_X - 0.06, ys, Z_CT_HEAD)),
         0.12, "span"),
        (Vector((L.CT_X + 0.06, ys, Z_CT_HEAD + 0.08)), Vector((bx, by, Z_TERM)), 0.18, "span"),
    ]


def sag_point(p0, p1, sag, t):
    return p0.lerp(p1, t) - Vector((0.0, 0.0, 4.0 * sag * t * (1.0 - t)))


# ------------------------------------------------------------------ tiers
def mode(level):
    """What each tier builds; notes.md, Per-tier triangle counts, says why.

    item    house openings: ring (casing ring, recessed leaf), cut (one
            recess the size of the casing), flush (a painted rect)
    runs    the wall one brick thick between piers, or one pier thick
    louvres the house walls whose louvres are kept (None: all)
    piers   the plain piers, or none (LOD3's pier-thick wall)
    lat     the gantry: "full" lattice (every face braced, rails and
            diagonals), "coarse" lattice (legs, a zigzag of diagonals, the
            truss's sides and string rails), "legs" (the corner angles and
            chords alone, a plain spike for the finial) or "painted" (slim
            solids with the lattice painted on)
    bush    sides of a bushing, and whether its full profile is turned (True),
            one turret and taper (False), one taper (None), or a pyramid
            standing GAP over the cover, touching nothing ("pyramid")
    string  "discs" (turned profile), "prism", "pyramid" (sides converging
            to the clamp, GAP under the truss, touching nothing) or None,
            and the sides
    cons    sides of the conservator; saddles kept or not
    trench  the cable trench covers, or none
    sw      the switchgear, or None: (sides, profile) of the breaker poles,
            the disconnector posts and the current transformers, and
            whether the disconnector's blades and the breaker's operating
            cabinet are kept
    cond    the conductors, or None: (segments, sides) of the drop and of
            the spans; a kind left out is not built
    poles3  LOD3's stand-in for the switchgear: the breaker poles alone,
            one prism each from the ground (poles3())
    dis3    LOD3's disconnector tables: the deck as a box on two 3-sided
            legs that stop GAP under it (dis3())
    gate_gap the gate as a plate GAP short of its piers or runs, touching
            nothing, instead of running into them (LOD3: no union cuts)
    """
    return [
        dict(item="ring", runs=RUN_SEGS, louvres=None, piers=PIERS, lat="full",
             bush=(8, True), string=("discs", 6), cons=(8, True), cable=True, pads=True,
             rad=True, trench=True,
             sw=dict(pole=(8, True), post=(6, True), ct=(8, True), blades=True, cab=True),
             cond=dict(drop=(6, 4), span=(4, 4)), poles3=False, dis3=False, gate_gap=False),
        dict(item="cut", runs=RUN_SEGS, louvres=None, piers=PIERS, lat="coarse",
             bush=(5, False), string=("prism", 4), cons=(6, True), cable=True, pads=True,
             rad=True, trench=True,
             sw=dict(pole=(5, True), post=(3, False), ct=(5, "mid"), blades=False, cab=True),
             cond=dict(drop=(3, 3), span=(2, 3)), poles3=False, dis3=False, gate_gap=False),
        dict(item="flush", runs=RUNS_THICK, louvres=None, piers=[], lat="legs",
             bush=(4, None), string=("prism", 3), cons=(4, False), cable=True, pads=True,
             rad=True, trench=True,
             sw=dict(pole=(4, False), post=(3, False), ct=(4, False), blades=False, cab=False),
             cond=dict(drop=(1, 3)), poles3=False, dis3=False, gate_gap=False),
        dict(item="flush", runs=RUNS_THICK, louvres=("front", "east"),
             piers=[], lat="painted", bush=(3, "pyramid"), string=("pyramid", 3),
             cons=(4, False), cable=False, pads=False, rad="one",
             trench=False, sw=None, cond=None, poles3=True, dis3=True, gate_gap=True),
    ][level]


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.
def uv_patch(name):
    return SB.uv_patch(L.PATCHES[name])


def _along(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    return dx / n, dy / n


def band(y_z0, u_off=0.0):
    """A side face from plan a to b on a tiling band: U the world coordinate
    along the face (so runs continue across piers), V height."""
    def side(a, b):
        tx, ty = _along(a, b)
        return lambda co: ((co.x * tx + co.y * ty + u_off) * PPM + 512.0,
                           y_z0 + co.z * PPM)
    return side


def region(rect, z0, vppm=PPM, uppm=PPM):
    """A side face from plan a to b on a unique region: U from a, true
    scale; V from height z0."""
    def side(a, b):
        tx, ty = _along(a, b)
        x0, y0 = rect[:2]
        return lambda co: (x0 + ((co.x - a[0]) * tx + (co.y - a[1]) * ty) * uppm,
                           y0 + (co.z - z0) * vppm)
    return side


def plan_uv(rect, ox, oy, ppm):
    x0, y0 = rect[:2]
    return lambda co: (x0 + (co.x - ox) * ppm, y0 + (co.y - oy) * ppm)


# ================================================================== solids
def box(x0, x1, y0, y1, z0, z1, side, top, bottom):
    """A closed box (shell_build.box()); *side(a, b)* returns the uv function
    of the side face from plan point a to b (walked counter-clockwise,
    outward on the right)."""
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    sides = [side(ring[k], ring[(k + 1) % 4]) for k in range(4)]
    return SB.box(Builder(), x0, x1, y0, y1, z0, z1, sides, top, bottom)


SMOOTH_SIDES = 4        # turned parts of this many facets or more shade smooth


def lathe(c, axis, e1, rings, sides, uvf, cap0, cap1, phase=0.0):
    """A turned solid: *rings* (radius, h) along unit *axis* from point *c*,
    *sides* facets starting at angle *phase* from unit *e1*. uvf(h, frac)
    gives a side vertex's (u, v), frac running 0..1 round; cap0 and cap1
    the first and last rings' caps' uv functions.

    With SMOOTH_SIDES facets or more, every side band steeper than 45
    degrees shades smooth, so a 5- or 8-sided porcelain column reads round
    instead of as flat glossy facets each catching its own highlight; the
    caps and the flat steps (a head's top, a shed's underside) stay flat,
    and Blender treats an edge between a smooth and a flat face as sharp."""
    B = Builder()
    c, axis, e1 = Vector(c), Vector(axis).normalized(), Vector(e1).normalized()
    e2 = axis.cross(e1)

    def P(r, h, k):
        th = phase + 2.0 * math.pi * k / sides
        return tuple(c + axis * h + (e1 * math.cos(th) + e2 * math.sin(th)) * r)

    for i in range(len(rings) - 1):
        (r0, h0), (r1, h1) = rings[i], rings[i + 1]
        smooth = sides >= SMOOTH_SIDES and abs(h1 - h0) > abs(r1 - r0)
        for k in range(sides):
            def fn(co, k=k, h0=h0, h1=h1, r0=r0, r1=r1):
                d = Vector(co) - c
                h = d.dot(axis)
                q = d - axis * h
                th = math.atan2(q.dot(e2), q.dot(e1)) - phase - 2.0 * math.pi * k / sides
                th = th % (2.0 * math.pi)
                if th > math.pi * 1.5:
                    th -= 2.0 * math.pi
                return uvf(h, (k + th / (2.0 * math.pi / sides)) / sides)
            B.face([P(r0, h0, k), P(r0, h0, k + 1), P(r1, h1, k + 1), P(r1, h1, k)], fn,
                   smooth=smooth)
    r, h = rings[0]
    B.face([P(r, h, k) for k in reversed(range(sides))], cap0)
    r, h = rings[-1]
    B.face([P(r, h, k) for k in range(sides)], cap1)
    return B


def pyramid(c, axis, e1, r, length, sides, uvf, cap, phase=0.0):
    """A *sides*-sided pyramid: its base of circumradius *r* at point *c*,
    square to unit *axis*, its apex *length* along it; uvf(h, frac) as for
    lathe(), cap the base's uv function. sides + 1 faces, sides * 2 - 2
    triangles fewer than a prism of the same base."""
    B = Builder()
    c, axis, e1 = Vector(c), Vector(axis).normalized(), Vector(e1).normalized()
    e2 = axis.cross(e1)
    ring = [tuple(c + (e1 * math.cos(th) + e2 * math.sin(th)) * r)
            for th in (phase + 2.0 * math.pi * k / sides for k in range(sides))]
    apex = tuple(c + axis * length)
    for k in range(sides):
        def fn(co, k=k):
            h = (Vector(co) - c).dot(axis)
            # the apex takes the face's middle, the base corners its edges
            if h > length - 1e-6:
                return uvf(h, (k + 0.5) / sides)
            th = (math.atan2((Vector(co) - c).dot(e2), (Vector(co) - c).dot(e1)) - phase) \
                % (2.0 * math.pi)
            j = th / (2.0 * math.pi / sides)
            if j < k - 0.5:
                j += sides
            return uvf(h, j / sides)
        B.face([ring[k], ring[(k + 1) % sides], apex], fn)
    B.face(list(reversed(ring)), cap)
    return B


def extrude(poly, P, d0, d1, side_uv, cap_uv):
    """A prism: plan polygon *poly* (u, v), counter-clockwise, swept from d0
    to d1 by P(u, v, d) -> (x, y, z). side_uv(a, b) gives each side's uv."""
    B = Builder()
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        B.face([P(*a, d0), P(*b, d0), P(*b, d1), P(*a, d1)], side_uv(a, b))
    B.face([P(u, v, d1) for u, v in poly], cap_uv)
    B.face([P(u, v, d0) for u, v in reversed(poly)], cap_uv)
    return B


# ================================================================== the wall
def wall_run(x0, x1, y0, y1, z0=0.0):
    return box(x0, x1, y0, y1, z0, L.Z_FENCE, band(L.F_Y0), uv_patch("coping"),
               uv_patch("blank"))


def pier(x, y):
    """A plain pier, PIER_PROUD over the wall's coping, its faces on the
    wall's band so the footing, brick and thin coping run round it."""
    h = L.PIER_W / 2.0
    return box(x - h, x + h, y - h, y + h, 0.0, L.Z_FENCE + L.PIER_PROUD, band(L.F_Y0),
               uv_patch("coping"), uv_patch("blank"))


def gate(gap=None):
    """The double gate as one closed plate between the gate piers, its ends
    in them: the front takes the gate region, the back the same leaves
    mirrored, the edges the gate's paint. With *gap* its ends stop that far
    short of the opening's sides instead, touching nothing (LOD3, whose
    union then cuts no holes in the runs' ends)."""
    if gap is None:
        x0, x1 = L.GATE_OPEN[0] - L.GATE_INTO, L.GATE_OPEN[1] + L.GATE_INTO
    else:
        x0, x1 = L.GATE_OPEN[0] + gap, L.GATE_OPEN[1] - gap
    y0, y1 = L.GATE_Y
    z0, z1 = L.GATE_Z
    gx, gy = L.GATE_R[:2]
    mirror = L.GATE_OPEN[0] + L.GATE_OPEN[1]

    def front(co):
        return (L.gate_u(co.x), gy + (co.z - z0) * PPM)

    def back(co):
        return (L.gate_u(mirror - co.x), gy + (co.z - z0) * PPM)

    def side(a, b):
        if a[1] == b[1] == y0:
            return front
        if a[1] == b[1] == y1:
            return back
        return uv_patch("gate")
    return box(x0, x1, y0, y1, z0, z1, side, uv_patch("gate"), uv_patch("gate"))


# ================================================================= the house
def recess(B, fr, rect, depth, fn, rev, floor=True):
    """shell_build.recess() of rectangle *rect* (l, r, b, t), *depth* in;
    without *floor* the bottom edge has no cheek (a door on the ground)."""
    SB.recess(B, fr, SB.rect_poly(rect), 0.0, depth, fn, rev,
              skip_z=None if floor else rect[2])


def item_rects(kind, s, z):
    return SB.item_rects(L.OPENINGS[kind], s, z)


def uv_item(fr, kind, s_left, z_bot):
    x0, y0 = L.ITEM_ORIGIN[kind]
    return SB.uv_region(fr, (x0, y0, 0, 0), s_left, z_bot, PPM)


def build_item(B, fr, kind, s, z, level):
    """Faces for one opening. A door on the ground returns the notch it cuts
    in the wall's bottom edge, left to right; a louvre returns its hole."""
    m = mode(level)["item"]
    (ol, orr, ob, ot), (il, ir, ib, it) = item_rects(kind, s, z)
    fn = uv_item(fr, kind, ol, ob)
    depth = L.REVEAL_DEPTH[kind]
    rev = uv_patch("reveal")
    on_ground = z < EPS
    o = [(ol, ob), (orr, ob), (orr, ot), (ol, ot)]
    hole = [(ol, ob), (ol, ot), (orr, ot), (orr, ob)] if on_ground else o
    if m == "flush":
        B.face([fr.P(*p) for p in o], fn)
        return hole
    if m == "cut":
        recess(B, fr, (ol, orr, ob, ot), depth, fn, rev, floor=not on_ground)
        return hole
    i = [(il, ib), (ir, ib), (ir, it), (il, it)]
    for k in range(4):          # a door's bottom quad has no area and is skipped
        B.face([fr.P(*o[k]), fr.P(*o[(k + 1) % 4]),
                fr.P(*i[(k + 1) % 4]), fr.P(*i[k])], fn)
    recess(B, fr, (il, ir, ib, it), depth, fn, rev, floor=not on_ground)
    return hole


def close_solid(B, top_uv):
    """Cap the house's two open rims (shell_build.rim_loops()): the floor on
    the ground, blank, and the roof's top, mapped by *top_uv*."""
    for loop in SB.rim_loops(B, 2):
        up = loop[0].co.z > 1.0
        SB.cap(B, loop, top_uv if up else uv_patch("blank"))


def house(level):
    """The switchgear house: four brick walls with their openings, the
    concrete slab's flush edge above them, the flat felt roof and the floor
    cap, as one closed solid."""
    B = Builder()
    fascia = L.FASCIA_R
    for spec in H_WALLS:
        fr = Frame(spec["p0"], spec["p1"])
        Lw = fr.L
        notches, holes = [], []
        keep = mode(level)["louvres"]
        for kind, s, z in spec["items"]:
            if kind == "louvre" and keep is not None and spec["name"] not in keep:
                continue
            if z < EPS:
                notches.append((s, build_item(B, fr, kind, s, z, level)))
            else:
                holes.append(build_item(B, fr, kind, s, z, level))
        outline = [(0.0, 0.0)]
        for _, pts in sorted(notches, key=lambda n: n[0]):
            outline += pts
        outline += [(Lw, 0.0), (Lw, L.Z_WALL), (0.0, L.Z_WALL)]
        u_off = spec["u_off"]
        SB.fill_region(B, fr, outline, holes,
                       lambda co, fr=fr, u_off=u_off: ((fr.s_of(co) + u_off) * PPM,
                                                       L.H_Y0 + co.z * PPM))
        B.face([fr.P(0.0, L.Z_WALL), fr.P(Lw, L.Z_WALL), fr.P(Lw, L.Z_TOP),
                fr.P(0.0, L.Z_TOP)],
               lambda co, fr=fr: (fascia[0] + fr.s_of(co) * PPM,
                                  fascia[1] + (co.z - L.Z_WALL) * PPM))
    close_solid(B, plan_uv(L.ROOF_R, HX0, HY0, L.ROOF_PPM))
    return B


def fire_wall():
    """Board-marked concrete between the transformers, its own region."""
    x0, x1, hw, h = L.FIRE
    return box(x0, x1, -hw, hw, 0.0, h, region(L.FIRE_R, 0.0), uv_patch("conc"),
               uv_patch("blank"))


def trenches():
    """The cable trenches' precast covers, TRENCH_H proud: the south one
    straight from its plinth into the house's west wall, the north one east
    from its plinth and south at TRENCH_TURN_X into the house's north wall.
    Each starts inside its plinth and ends inside the house. The north one
    is one closed L: its top three quads (the east run, the corner square,
    the south run), its outline split where they meet."""
    w, h = L.TRENCH_W / 2.0, L.TRENCH_H
    tr = L.TRENCH_R
    side = uv_patch("conc")
    out = []
    ys = L.T_Y[0]
    x0, x1 = L.TRENCH_X0, HX0 + 0.05
    out.append(box(x0, x1, ys - w, ys + w, 0.0, h, lambda a, b: side,
                   lambda co: (tr[0] + (co.x - x0) * PPM, tr[1] + (co.y - (ys - w)) * PPM),
                   uv_patch("blank")))
    yn = L.T_Y[1]
    xa, xb = L.TRENCH_TURN_X - w, L.TRENCH_TURN_X + w
    yend = HY1 - 0.05
    B = Builder()

    def along_x(co):
        return (tr[0] + (co.x - x0) * PPM, tr[1] + (co.y - (yn - w)) * PPM)

    def along_y(co):
        return (tr[0] + (yn - w - co.y) * PPM, tr[1] + (co.x - xa) * PPM)
    for quad, fn in (([(x0, yn - w), (xa, yn - w), (xa, yn + w), (x0, yn + w)], along_x),
                     ([(xa, yn - w), (xb, yn - w), (xb, yn + w), (xa, yn + w)], along_x),
                     ([(xa, yend), (xb, yend), (xb, yn - w), (xa, yn - w)], along_y)):
        B.face([(x, y, h) for x, y in quad], fn)
    outline = [(x0, yn - w), (xa, yn - w), (xa, yend), (xb, yend), (xb, yn - w),
               (xb, yn + w), (xa, yn + w), (x0, yn + w)]
    for k in range(len(outline)):
        a, b = outline[k], outline[(k + 1) % len(outline)]
        B.face([(a[0], a[1], 0.0), (b[0], b[1], 0.0), (b[0], b[1], h), (a[0], a[1], h)], side)
    B.face([(x, y, 0.0) for x, y in reversed(outline)], uv_patch("blank"))
    out.append(B)
    return out


# ========================================================== the transformers
def transformer(ty, level):
    """One transformer's solids, standing on its plinth."""
    md = mode(level)
    px, py, ph = L.PLINTH
    tw, td = L.TANK
    z0, z1 = L.TANK_Z
    out = []
    out.append(box(TX - px / 2, TX + px / 2, ty - py / 2, ty + py / 2, 0.0, ph,
                   band(L.F_Y0, 1.0), plan_uv(L.GRAVEL_R, TX - px / 2, ty - py / 2,
                                              L.GRAVEL_PPM), uv_patch("blank")))
    out.append(box(TX - tw / 2, TX + tw / 2, ty - td / 2, ty + td / 2, z0, z1,
                   region(L.TANK_R, ph), plan_uv(L.TANK_TOP_R, TX - tw / 2, ty - td / 2, PPM),
                   uv_patch("steel_dark")))
    if md["rad"] == "one":
        # LOD3: both banks as one box through the tank, their outer faces
        # where the banks' are, their fins painted as before
        y0, y1 = ty - td / 2 - L.RAD_D + 0.05, ty + td / 2 + L.RAD_D - 0.05

        def side(a, b, ty=ty):
            if abs(a[0] - b[0]) < EPS:
                return region(L.RAD_END_R, L.RAD_Z[0])(a, b)
            return region(L.RAD_R, L.RAD_Z[0])(a, b)

        def fins_uv(co, ty=ty):
            d = abs(co.y - ty) - (td / 2 - 0.05)
            return (L.RAD_TOP_R[0] + (co.x - (TX - L.RAD_X / 2)) * PPM,
                    L.RAD_TOP_R[1] + d * PPM)
        out.append(box(TX - L.RAD_X / 2, TX + L.RAD_X / 2, y0, y1, *L.RAD_Z,
                       side, fins_uv, fins_uv))
    elif md["rad"]:
        for sgn in (-1, 1):
            ya = ty + sgn * (td / 2 - 0.05)
            yb = ty + sgn * (td / 2 + L.RAD_D - 0.05)
            y0, y1 = min(ya, yb), max(ya, yb)

            def side(a, b, sgn=sgn, ty=ty):
                if abs(a[0] - b[0]) < EPS:                  # an end, normal +-x
                    return region(L.RAD_END_R, L.RAD_Z[0])(a, b)
                outer = (a[1] - ty) * sgn > td / 2
                if outer:
                    return region(L.RAD_R, L.RAD_Z[0])(a, b)
                return uv_patch("steel_dark")
            def fins_uv(co, sgn=sgn, ty=ty):
                d = abs(co.y - ty) - (td / 2 - 0.05)
                return (L.RAD_TOP_R[0] + (co.x - (TX - L.RAD_X / 2)) * PPM,
                        L.RAD_TOP_R[1] + d * PPM)
            out.append(box(TX - L.RAD_X / 2, TX + L.RAD_X / 2, y0, y1, *L.RAD_Z,
                           side, fins_uv, fins_uv))
    # conservator, its axis along Y over the east end of the cover
    sides, saddles = md["cons"]
    cx, cz, r = TX + L.CONS_X, L.CONS_Z, L.CONS_R
    cr = L.CONS_R_
    ce = L.CONS_END_R

    def cons_uv(h, frac):
        return (cr[0] + h * PPM, cr[1] + frac * cr[3])

    def cons_end(co):
        return (ce[0] + ce[2] / 2 + (co.x - cx) * PPM, ce[1] + ce[3] / 2 + (co.z - cz) * PPM)
    if saddles:
        out.append(lathe((cx, ty - td / 2, cz), (0, 1, 0), (0, 0, 1), [(r, 0.0), (r, td)],
                         sides, cons_uv, cons_end, cons_end, phase=math.pi / sides))
    else:
        # without saddles the drum comes down into the cover as a box of
        # the square drum's width, so it does not float over the tank
        h = r * math.cos(math.pi / 4)
        y0 = ty - td / 2

        def drum_side(a, b, y0=y0):
            if abs(a[0] - b[0]) < EPS:
                return lambda co: cons_uv(co.y - y0, 0.25)
            return cons_end
        out.append(box(cx - h, cx + h, y0, ty + td / 2, z1 - 0.05, cz + h, drum_side,
                       lambda co, y0=y0: cons_uv(co.y - y0, 0.0), uv_patch("steel_dark")))
    if saddles:
        for dy in (-0.55, 0.55):
            out.append(box(cx - 0.06, cx + 0.06, ty + dy - 0.06, ty + dy + 0.06,
                           z1 - 0.05, cz, lambda a, b: uv_patch("steel_dark"),
                           uv_patch("steel_dark"), uv_patch("steel_dark")))
    # bushings
    bs, full = md["bush"]
    br = L.BUSH_R
    if full == "pyramid":
        # LOD3: each bushing a 3-sided pyramid standing GAP over the cover,
        # its tip at the terminal, touching nothing (4 triangles; tapers
        # cut into the cover cost 76 for the six)
        for k in PH:
            bx, by = bushing_xy(ty, k)
            out.append(pyramid((bx, by, z1 + GAP), (0, 0, 1), (1, 0, 0), 0.14,
                               L.BUSH_H - 0.05 - GAP, bs,
                               lambda h, frac: (br[0] + frac * br[2],
                                                br[1] + (h + 0.05 + GAP) * PPM),
                               uv_patch("steel_dark"), phase=math.pi / bs))
        bs = 0
    if bs == 0:
        prof = None
    elif full:
        prof = L.bushing_profile()
    elif full is None:          # LOD3: one tapered prism, turret and porcelain
        prof = [(0.14, 0.0), (0.06, L.BUSH_H)]
    else:
        prof = [(0.15, 0.0), (0.15, 0.27), (0.10, 0.27), (0.06, L.BUSH_H)]
    for k in (PH if prof else ()):
        bx, by = bushing_xy(ty, k)
        out.append(lathe((bx, by, z1 - 0.05), (0, 0, 1), (1, 0, 0), prof, bs,
                         lambda h, frac: (br[0] + frac * br[2], br[1] + h * PPM),
                         uv_patch("steel_dark"), uv_patch("alu"),
                         phase=math.pi / bs))
    if md["cable"]:
        c0, c1 = L.CABLE_X
        out.append(box(TX + c0, TX + c1, ty - L.CABLE_Y, ty + L.CABLE_Y, z0, L.CABLE_TOP,
                       region(L.CABLE_R, ph), uv_patch("tank_paint"), uv_patch("steel_dark")))
    return out


# ============================================================== the gantry
# A lattice portal, built LEAN: every corner angle, chord and bracing bar is
# its own closed solid, stopping GAP short of whatever it meets, so the
# union never cuts one bar with another. Only the columns' legs go into the
# union, into their pads; the bracing, the chords and the finials join the
# mesh after it, and build_lod() asserts they touch nothing.
GAP = L.G_GAP


class Face:
    """One braced face of a lattice member, as an affine map from face
    coordinates: a across the face (0 on its centre line), t along the
    member, d inward from the face's outer plane. The outer plane lies
    hn(t) out from the member's axis along unit e_n, its edges (the corner
    angles' heels) at a = +-ha(t); hn and ha are linear in t, given at t0
    and t1. *edge* is the corner angles' leg: the bracing stops GAP inside
    it."""

    def __init__(self, origin, e_t, e_a, e_n, t0, t1, hn, ha, edge):
        self.o, self.e_t, self.e_a, self.e_n = (Vector(v) for v in (origin, e_t, e_a, e_n))
        self.t0, self.t1, self.hn, self.ha, self.edge = t0, t1, hn, ha, edge

    def lin(self, pair, t):
        return pair[0] + (pair[1] - pair[0]) * (t - self.t0) / (self.t1 - self.t0)

    def P(self, a, t, d):
        return tuple(self.o + self.e_t * t + self.e_a * a
                     + self.e_n * (self.lin(self.hn, t) - d))

    def inner(self, t):
        """Half the clear width between the corner angles at t, GAP inside."""
        return self.lin(self.ha, t) - self.edge - GAP

    def clip(self, p, D, side):
        """s where p + s D (face coordinates) meets a = side * inner(t)."""
        k = (self.ha[1] - self.ha[0]) / (self.t1 - self.t0)
        c0 = self.inner(0.0)
        return (side * (c0 + k * p[1]) - p[0]) / (D[0] - side * k * D[1])


def brace(B, face, p0, p1, uv, w=L.G_BRACE[0], d=L.G_BRACE[1]):
    """A bracing angle across *face* along the line from p0 to p1 (face
    coordinates, p0 on the side a < 0), as its hull, a triangular prism:
    the flange w wide in the face's outer plane, the toe d deep on its centre
    line. Both ends are cut along the clip lines, GAP inside the corner
    angles, so the bar touches nothing."""
    D = Vector((p1[0] - p0[0], p1[1] - p0[1])).normalized()
    n = Vector((-D.y, D.x))
    pts = []
    for off, depth in ((0.5 * w, 0.0), (-0.5 * w, 0.0), (0.0, d)):
        q = Vector(p0) + n * off
        pts.append([face.P(*(q + D * face.clip(q, D, sd)), depth) for sd in (-1, 1)])
    (aL, aR), (bL, bR), (cL, cR) = pts
    for f in ([aL, aR, bR, bL], [aL, cL, cR, aR], [bL, bR, cR, cL], [aL, bL, cL],
              [aR, cR, bR]):
        B.face(f, uv)


def bracing(B, face, pts, rails, dirs, uv, railed=None):
    """One face's bracing between panel points *pts* (t, increasing): a
    rail across the face at each t in *rails*, and a diagonal in each panel,
    dirs[k] True running from a < 0 at pts[k] to a > 0 at pts[k + 1]. A
    diagonal stands off each panel point by half its own width measured
    along t, plus the rail's half-width where the point is *railed* (rails
    by default; a rail another section draws counts too), plus a clearance,
    so it clears the rail or the diagonal meeting it there."""
    w = L.G_BRACE[0]
    railed = set(rails if railed is None else railed)
    for t in rails:
        brace(B, face, (-face.inner(t), t), (face.inner(t), t), uv)
    for k, up in enumerate(dirs):
        if up is None:
            continue
        ta, tb = pts[k], pts[k + 1]
        th = math.atan2(tb - ta, face.inner(ta) + face.inner(tb))
        ht = 0.5 * w / math.cos(th)

        def off(t):
            return ht + GAP + 0.003 + (0.5 * w if t in railed else 0.0)
        a, b = ta + off(ta), tb - off(tb)
        if up:
            brace(B, face, (-face.inner(a), a), (face.inner(b), b), uv)
        else:
            brace(B, face, (-face.inner(b), b), (face.inner(a), a), uv)


def prism(B, rings, uv):
    """A closed prism through polygon *rings* (each a list of points, all the
    same length, in order along the member), capped at both ends."""
    n = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            B.face([r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]], uv)
    B.face(list(rings[0]), uv)
    B.face(list(rings[-1]), uv)
    return B


SIDES = ((-1, 0), (0, -1), (1, 0), (0, 1))     # a column's faces' outward normals


def column(cx, cy, md, legs, bars):
    """A lattice column on axis (cx, cy): four corner angles from inside the
    pad up the shaft and the peak (into *legs*, for the union), each face's
    bracing and the finial (into *bars*)."""
    g = uv_patch("galv_paint")
    a = L.G_LEG
    zs = (L.G_PAD[1] - 0.05, L.G_TOP, L.G_PEAK_Z)
    for sx in (-1, 1):
        for sy in (-1, 1):
            rings = []
            for z in zs:
                h = L.g_half(z)
                x, y = cx + sx * h, cy + sy * h
                rings.append([(x, y, z), (x - sx * a, y, z), (x, y - sy * a, z)])
            legs.append(prism(Builder(), rings, g))
    z0 = L.G_PAD[1]
    for i, (nx, ny) in enumerate(SIDES):
        e_n, e_a = (nx, ny, 0.0), (-ny, nx, 0.0)
        hs = (L.g_half(z0), L.g_half(L.G_TOP))
        shaft = Face((cx, cy, 0.0), (0, 0, 1), e_a, e_n, z0, L.G_TOP, hs, hs, a)
        if md["lat"] == "legs":
            continue
        if md["lat"] == "full":
            pts = L.G_SHAFT_PTS
            bracing(bars, shaft, pts, pts, [i % 2 == 0] * (len(pts) - 1), g)
            hp = (L.g_half(L.G_TOP), L.g_half(L.G_PEAK_Z))
            peak = Face((cx, cy, 0.0), (0, 0, 1), e_a, e_n, L.G_TOP, L.G_PEAK_Z, hp, hp, a)
            bracing(bars, peak, (pts[-1], L.G_PEAK_RAIL), (L.G_PEAK_RAIL,), [i % 2 == 0], g,
                    railed=(pts[-1], L.G_PEAK_RAIL))
        else:
            pts = L.G_SHAFT_PTS1
            bracing(bars, shaft, pts, (), [(k + i) % 2 == 0 for k in range(len(pts) - 1)], g)
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    if md["lat"] == "legs":
        # LOD2: the finial as one plain spike GAP over the legs' tops
        h, z1 = L.g_half(L.G_PEAK_Z) + 0.01, L.G_PEAK_Z + GAP
        ring = [(cx + p * h, cy + q * h, z1) for p, q in sq]
        bars.face(list(reversed(ring)), g)
        for j in range(4):
            bars.face([ring[j], ring[(j + 1) % 4], (cx, cy, L.G_TIP)], g)
        return
    # the finial: a cap plate over the legs' tops, the shield-wire spike on it
    h, r = L.g_half(L.G_PEAK_Z) + 0.01, 0.035
    z1, z2 = L.G_PEAK_Z + GAP, L.G_PEAK_Z + GAP + 0.04
    outer = [(cx + p * h, cy + q * h) for p, q in sq]
    inner = [(cx + p * r, cy + q * r) for p, q in sq]
    bars.face([(x, y, z1) for x, y in reversed(outer)], g)
    for k in range(4):
        (ax, ay), (bx, by) = outer[k], outer[(k + 1) % 4]
        (ix, iy), (jx, jy) = inner[k], inner[(k + 1) % 4]
        bars.face([(ax, ay, z1), (bx, by, z1), (bx, by, z2), (ax, ay, z2)], g)
        bars.face([(ax, ay, z2), (bx, by, z2), (jx, jy, z2), (ix, iy, z2)], g)
        bars.face([(ix, iy, z2), (jx, jy, z2), (cx, cy, L.G_TIP)], g)


def truss(md, bars):
    """The box truss between the columns: four chord angles along Y, each
    stopping GAP short of the columns' inner faces, and the bracing of its
    sides, top and bottom; a rail under each string."""
    g = uv_patch("galv_paint")
    c = L.G_CHORD
    hw, hd, zc = L.BEAM_HW, L.BEAM_HD, L.BEAM_ZC
    for sx in (-1, 1):
        for sz in (-1, 1):
            zmin = L.G_BEAM_Z[0] if sz < 0 else L.G_BEAM_Z[1] - c
            ye = L.G_COL_Y - L.g_half(zmin) - GAP
            x, z = L.G_X + sx * hw, zc + sz * hd
            tri = [(x, z), (x - sx * c, z), (x, z - sz * c)]
            prism(bars, [[(px, y, pz) for px, pz in tri] for y in (-ye, ye)], g)
    o = (L.G_X, 0.0, zc)
    side = [Face(o, (0, 1, 0), (0, 0, 1), (s, 0, 0), -1.0, 1.0, (hw, hw), (hd, hd), c)
            for s in (-1, 1)]
    top, bottom = (Face(o, (0, 1, 0), (1, 0, 0), (0, 0, s), -1.0, 1.0, (hd, hd), (hw, hw), c)
                   for s in (1, -1))
    yp = L.BEAM_YP
    if md["lat"] == "legs":
        return
    if md["lat"] == "full":
        n = L.BEAM_SIDE_N
        pts = [-yp + 2 * yp * k / n for k in range(n + 1)]
        for f in side:
            bracing(bars, f, pts, (-yp, yp), [k % 2 == 0 for k in range(n)], g)
        bp = L.BEAM_PTS
        half = (len(bp) - 1) // 2
        bracing(bars, bottom, bp, bp, [k < half for k in range(len(bp) - 1)], g)
        bracing(bars, top, bp, (-yp, yp), [k % 2 == 0 for k in range(len(bp) - 1)], g)
    else:
        n = 10
        pts = [-yp + 2 * yp * k / n for k in range(n + 1)]
        for f in side:
            bracing(bars, f, pts, (), [k % 2 == 0 for k in range(n)], g)
        for t in L.STRING_YS:
            brace(bars, bottom, (-bottom.inner(t), t), (bottom.inner(t), t), g)


def painted_column(cx, cy, foot):
    """LOD3: a column as one slim tapered solid, G_SOLID[0] of the lattice's
    width, its peak a pyramid from G_TOP to the finial's tip, the lattice
    painted on (COL_LAT_R)."""
    k = L.G_SOLID[0]
    R = L.COL_LAT_R
    zs = (foot, L.G_TOP)
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    B = Builder()

    def uv(t2):
        def fn(co):
            if co.z > L.G_TOP + EPS:    # the peak: to a point at G_TIP
                hz = k * L.g_half(L.G_TOP) * (L.G_TIP - co.z) / (L.G_TIP - L.G_TOP)
            else:
                hz = k * L.g_half(co.z)
            across = (co.x - cx) * t2[0] + (co.y - cy) * t2[1]
            f = 0.5 if hz < 1e-6 else 0.5 + across / (2.0 * hz)
            return (R[0] + f * R[2], R[1] + co.z * L.COL_LAT_PPM)
        return fn
    rings = [[(cx + p * k * L.g_half(z), cy + q * k * L.g_half(z), z) for p, q in sq] for z in zs]
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(4):
            a, b = sq[j], sq[(j + 1) % 4]
            t2 = ((b[0] - a[0]) / 2.0, (b[1] - a[1]) / 2.0)
            B.face([r0[j], r0[(j + 1) % 4], r1[(j + 1) % 4], r1[j]], uv(t2))
    for j in range(4):
        a, b = sq[j], sq[(j + 1) % 4]
        t2 = ((b[0] - a[0]) / 2.0, (b[1] - a[1]) / 2.0)
        B.face([rings[-1][j], rings[-1][(j + 1) % 4], (cx, cy, L.G_TIP)], uv(t2))
    B.face(list(reversed(rings[0])), uv_patch("blank"))
    return B


def painted_truss_z():
    """The slim truss's bottom and top: G_SOLID[2] of the lattice's depth,
    on its mid-height."""
    hd = L.G_SOLID[2] * L.BEAM_HD
    return L.BEAM_ZC - hd, L.BEAM_ZC + hd


def painted_truss():
    """LOD3: the truss as one slim box, G_SOLID[1] of its width and
    G_SOLID[2] of its depth, on its mid-height, GAP short of the slim
    columns; the lattice painted on its sides (BEAM_LAT_R) and its top and
    bottom (BEAM_TOP_R)."""
    hw = L.G_SOLID[1] * L.BEAM_HW
    z0, z1 = painted_truss_z()
    ye = L.G_COL_Y - L.G_SOLID[0] * L.g_half(z0) - GAP
    S, T = L.BEAM_LAT_R, L.BEAM_TOP_R

    def u(co, R):
        return R[0] + R[2] / 2.0 + co.y * L.BEAM_LAT_PPM

    def side(a, b):
        if abs(a[0] - b[0]) < EPS:          # a long side, normal +-x
            return lambda co: (u(co, S), S[1] + (co.z - z0) / (z1 - z0) * S[3])
        return uv_patch("galv_paint")

    def flat(co):
        return (u(co, T), T[1] + (co.x - (L.G_X - hw)) / (2.0 * hw) * T[3])
    # box() walks the plan; its x is the truss's x, y along the truss
    return box(L.G_X - hw, L.G_X + hw, -ye, ye, z0, z1, side, flat, flat)


def gantry(level):
    """The portal and its strings: (solids for the union, bars to join after
    it). Lattice tiers put the legs, pads and strings in the union and every
    bar after it; painted tiers put the pads, the slim columns' feet and the
    strings in the union and the slim truss after it."""
    md = mode(level)
    union_parts, bars = [], Builder()
    for sy in (-1, 1):
        y = sy * L.G_COL_Y
        if md["pads"]:
            p = L.G_PAD[0] / 2.0
            union_parts.append(box(L.G_X - p, L.G_X + p, y - p, y + p, 0.0, L.G_PAD[1],
                                   band(L.F_Y0, 2.0), uv_patch("pad_top"), uv_patch("blank")))
        if md["lat"] == "painted":
            foot = L.G_PAD[1] - 0.05 if md["pads"] else 0.0
            union_parts.append(painted_column(L.G_X, y, foot))
        else:
            column(L.G_X, y, md, union_parts, bars)
    after = [bars]
    if md["lat"] == "painted":
        after.append(painted_truss())
    else:
        truss(md, bars)
    # strings
    kind, sides = md["string"]
    st = L.STRING_R
    top = string_top()
    if md["lat"] == "painted":      # from GAP under the slim truss to the same clamp
        top = painted_truss_z()[0] - GAP
    length = L.STRING_LEN + top - string_top()
    if kind == "pyramid":
        # LOD3: each string a 3-sided pyramid from GAP under the slim truss
        # to the clamp's height, touching nothing (4 triangles)
        for ys in L.STRING_YS:
            union_parts.append(pyramid((L.G_X, ys, top), (0, 0, -1), (1, 0, 0), 0.10,
                                       length, sides,
                                       lambda h, frac: (st[0] + frac * st[2],
                                                        st[1] + (h - length + L.STRING_LEN)
                                                        * PPM),
                                       uv_patch("galv_paint"), phase=math.pi / sides))
    elif kind is not None:
        for ys in L.STRING_YS:
            rings = L.string_profile() if kind == "discs" else \
                [(0.10, 0.0), (0.10, length)]
            union_parts.append(lathe((L.G_X, ys, top), (0, 0, -1), (1, 0, 0), rings, sides,
                                     # the extra length over the painted string
                                     # samples the cap's paint above it
                                     lambda h, frac: (st[0] + frac * st[2],
                                                      st[1] + (h - length + L.STRING_LEN) * PPM),
                                     uv_patch("galv_paint"), uv_patch("galv_paint"),
                                     phase=math.pi / sides))
    return union_parts, [B for B in after if B.bm.faces]


# ============================================================ the switchgear
def wrapped(rect):
    """uv for a turned part wrapped once round its region, V metres up."""
    return lambda h, frac: (rect[0] + frac * rect[2], rect[1] + h * PPM)


def galv_box(x0, x1, y0, y1, z0, z1):
    return box(x0, x1, y0, y1, z0, z1, lambda a, b: uv_patch("galv_paint"),
               uv_patch("galv_paint"), uv_patch("blank"))


def lattice_leg(x0, x1, y0, y1, z0, z1):
    """A disconnector table's leg: a solid post with the lattice painted on
    each face (DIS_LAT_R), U across the face, V up it."""
    R = L.DIS_LAT_R

    def side(a, b):
        ln2 = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
        return lambda co: (R[0] + ((co.x - a[0]) * (b[0] - a[0]) + (co.y - a[1]) * (b[1] - a[1]))
                           / ln2 * R[2], R[1] + co.z * L.DIS_LAT_PPM)
    return box(x0, x1, y0, y1, z0, z1, side, uv_patch("galv_paint"), uv_patch("blank"))


def switchgear(ty, level):
    """One transformer's switchgear bay, west to east: the disconnector on
    its tall steel table, the breaker poles on their stand, the current
    transformers on their concrete table."""
    sw = mode(level)["sw"]
    if sw is None:
        return []
    out = []
    H = L.SW_HALF
    ys = [ty + k * L.SW_PHASE for k in PH]
    # the disconnector: deck, two plate legs, six posts, three closed blades
    x0, x1, z0, z1 = L.DIS_DECK
    xc = (x0 + x1) / 2.0
    out.append(galv_box(x0, x1, ty - H, ty + H, z0, z1))
    lx, ly, lo = L.DIS_LEG
    for sgn in (-1, 1):
        yl = ty + sgn * lo
        out.append(lattice_leg(xc - lx / 2, xc + lx / 2, yl - ly / 2, yl + ly / 2, 0.0, z0 + 0.05))
    sides, full = sw["post"]
    prof = L.post_profile(full)
    for y in ys:
        for px in L.DIS_X:
            out.append(lathe((px, y, L.POST_Z0), (0, 0, 1), (1, 0, 0), prof, sides,
                             wrapped(L.POST_R), uv_patch("blank"), uv_patch("galv_paint"),
                             phase=math.pi / sides))
        if sw["blades"]:
            zt = L.POST_Z0 + L.POST_H
            out.append(galv_box(L.DIS_X[0], L.DIS_X[1], y - 0.03, y + 0.03, zt - 0.06, zt + 0.01))
    # the breaker: stand deck and legs, the operating cabinet, three poles
    w, z0, z1 = L.BRK_DECK
    out.append(galv_box(L.BRK_X - w / 2, L.BRK_X + w / 2, ty - H, ty + H, z0, z1))
    side, lo = L.BRK_LEG
    for sgn in (-1, 1):
        yl = ty + sgn * lo
        out.append(galv_box(L.BRK_X - side / 2, L.BRK_X + side / 2, yl - side / 2, yl + side / 2,
                            0.0, z0 + 0.05))
    if sw["cab"]:
        out.append(box(L.BRK_X - 0.20, L.BRK_X + 0.20, ty - 0.30, ty + 0.30, 1.15, z0 + 0.05,
                       region(L.CABLE_R, -0.10), uv_patch("tank_paint"), uv_patch("steel_dark")))
    sides, full = sw["pole"]
    prof = L.breaker_profile(full)
    for y in ys:
        out.append(lathe((L.BRK_X, y, L.BRK_Z0), (0, 0, 1), (1, 0, 0), prof, sides,
                         wrapped(L.BREAKER_R), uv_patch("blank"), uv_patch("head"),
                         phase=math.pi / sides))
    # the current transformers: concrete table, three on it
    w, z0, z1 = L.CT_TABLE
    conc = region(L.FIRE_R, 0.0)
    out.append(box(L.CT_X - w / 2, L.CT_X + w / 2, ty - H, ty + H, z0, z1, conc,
                   uv_patch("conc"), uv_patch("blank")))
    side, lo = L.CT_LEG
    for sgn in (-1, 1):
        yl = ty + sgn * lo
        out.append(box(L.CT_X - side / 2, L.CT_X + side / 2, yl - side / 2, yl + side / 2,
                       0.0, z0 + 0.05, conc, uv_patch("conc"), uv_patch("blank")))
    sides, full = sw["ct"]
    prof = L.ct_profile(full)
    for y in ys:
        out.append(lathe((L.CT_X, y, L.CT_Z0), (0, 0, 1), (1, 0, 0), prof, sides,
                         wrapped(L.CT_R), uv_patch("blank"), uv_patch("tank_paint"),
                         phase=math.pi / sides))
    return out


def poles3(ty):
    """LOD3's switchgear: each breaker pole one 3-sided prism from the
    ground to its top head, its stand painted at its foot, standing alone."""
    r = L.POLE3_R
    return [lathe((L.BRK_X, ty + k * L.SW_PHASE, 0.0), (0, 0, 1), (1, 0, 0),
                  [(0.13, 0.0), (0.12, L.BRK_Z0 + L.Z_BRK[3])], 3,
                  lambda h, frac: (r[0] + frac * r[2], r[1] + h * L.POLE3_PPM),
                  uv_patch("blank"), uv_patch("head"), phase=math.pi / 3)
            for k in PH]


def dis3(ty):
    """LOD3's disconnector table: the galvanised deck as a 3-sided prism
    along the bay, its top the deck's top, its two sloping undersides
    meeting on the deck's centre line at its underside's height, on its two
    legs, each a 3-sided prism with the painted lattice (DIS_LAT_R), flat
    face toward the bay's centre line, stopping GAP under the deck, so
    nothing touches and the union cuts nothing: 24 triangles a bay."""
    x0, x1, z0, z1 = L.DIS_DECK
    xc = (x0 + x1) / 2.0
    H = L.SW_HALF
    g = uv_patch("galv_paint")
    deck = extrude([(x0, z1), (xc, z0), (x1, z1)], lambda u, v, d: (u, d, v),
                   ty - H, ty + H, lambda a, b: g, g)
    bmesh.ops.recalc_face_normals(deck.bm, faces=deck.bm.faces[:])
    out = [deck]
    lx, ly, lo = L.DIS_LEG
    R = L.DIS_LAT_R

    def side(a, b):
        ln2 = (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2
        return lambda co: (R[0] + ((co.x - a[0]) * (b[0] - a[0]) + (co.y - a[1]) * (b[1] - a[1]))
                           / ln2 * R[2], R[1] + co.z * L.DIS_LAT_PPM)
    for sgn in (-1, 1):
        yl = ty + sgn * lo
        yi, yo = yl - sgn * ly / 2.0, yl + sgn * ly / 2.0      # inner (flat) and outer
        tri = [(xc - lx / 2.0, yi), (xc + lx / 2.0, yi), (xc, yo)]
        if sgn < 0:
            tri = [tri[1], tri[0], tri[2]]
        if (tri[1][0] - tri[0][0]) * (tri[2][1] - tri[0][1]) \
                - (tri[1][1] - tri[0][1]) * (tri[2][0] - tri[0][0]) < 0:
            tri.reverse()                                        # counter-clockwise
        out.append(extrude(tri, lambda u, v, d: (u, v, d), 0.0, z0 - GAP, side,
                           uv_patch("galv_paint")))
    return out


def tube(points, r, sides):
    """A closed tube through *points* (all in one vertical plane), rings
    square to the local tangent, the aluminium patch all over."""
    B = Builder()
    pts = [Vector(p) for p in points]
    chord = pts[-1] - pts[0]
    s = Vector((chord.y, -chord.x, 0.0))
    s = s.normalized() if s.length > 1e-6 else Vector((1.0, 0.0, 0.0))
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        e2 = t.cross(s).normalized()
        rings.append([tuple(p + (s * math.cos(th) + e2 * math.sin(th)) * r)
                      for th in (math.pi / sides + 2.0 * math.pi * k / sides
                                 for k in range(sides))])
    fn = uv_patch("alu")
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            B.face([a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k]], fn)
    B.face(list(reversed(rings[0])), fn)
    B.face(rings[-1], fn)
    return B


def conductors(ty, level):
    cond = mode(level)["cond"]
    if cond is None:
        return []
    out = []
    for k in PH:
        for p0, p1, sag, kind in spans(ty, k):
            if kind not in cond:
                continue
            n, sides = cond[kind]
            pts = [sag_point(p0, p1, sag, i / n) for i in range(n + 1)]
            out.append(tube(pts, L.COND_R, sides))
    return out


# ================================================================ assembly
def touching(bm, me):
    """Why the closed shells of mesh *me* do not stand clear of each other
    and of *bm*, or "" when they do: any two of its shells, or one of them
    and bm, whose triangles intersect or come within GAP / 4 of each other
    (probed by intersecting each shell, grown by that much, with the rest)."""
    from mathutils.bvhtree import BVHTree
    other = bm.copy()
    bmesh.ops.triangulate(other, faces=other.faces[:])
    tree = BVHTree.FromBMesh(other)
    other.free()
    mine = bmesh.new()
    mine.from_mesh(me)
    bmesh.ops.triangulate(mine, faces=mine.faces[:])
    mine.faces.index_update()
    shells, seen = [], set()
    for f in mine.faces:
        if f.index in seen:
            continue
        stack, shell = [f], []
        seen.add(f.index)
        while stack:
            g = stack.pop()
            shell.append(g.index)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index)
                        stack.append(h)
        shells.append(shell)
    tri = [[tuple(v.co) for v in f.verts] for f in mine.faces]
    whole = BVHTree.FromPolygons([v for t in tri for v in t],
                                 [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(tri))],
                                 epsilon=GAP / 4.0)
    owner = {i: k for k, sh in enumerate(shells) for i in sh}
    mine.free()
    for k, sh in enumerate(shells):
        idx = sh
        part = BVHTree.FromPolygons([v for i in idx for v in tri[i]],
                                    [(3 * j, 3 * j + 1, 3 * j + 2) for j in range(len(idx))],
                                    epsilon=GAP / 4.0)
        if part.overlap(tree):
            c = tri[idx[0]][0]
            return "a bar near (%.3f, %.3f, %.3f) meets the union" % c
        for _, j in part.overlap(whole):
            if owner[j] != k:
                c = tri[idx[0]][0]
                return "two bars meet near (%.3f, %.3f, %.3f)" % c
    return ""


def build_lod(level):
    md = mode(level)
    base = to_object(house(level), "tmp_house")
    solids = [wall_run(*r) for r in md["runs"]]
    solids += [pier(x, y) for x, y in md["piers"]]
    solids.append(gate(GAP if md["gate_gap"] else None))
    solids.append(fire_wall())
    if md["trench"]:
        solids += trenches()
    for ty in L.T_Y:
        solids += transformer(ty, level)
        solids += switchgear(ty, level)
        solids += conductors(ty, level)
        if md["poles3"]:
            solids += poles3(ty)
        if md["dis3"]:
            solids += dis3(ty)
    gparts, after = gantry(level)
    solids += gparts
    parts = [to_object(B, "tmp_%d" % i) for i, B in enumerate(solids)]
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    # the lattice's bars join after the union: closed solids that touch
    # nothing, so it would only cost time; asserted here
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for i, B in enumerate(after):
        extra = to_object(B, "tmp_bars_%d" % i)
        clash = touching(bm, extra.data)
        if clash:
            raise ValueError("LOD%d: %s" % (level, clash))
        bm.from_mesh(extra.data)
        bpy.data.meshes.remove(extra.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY',
                          ngon_method='BEAUTY')
    flat = [f for f in bm.faces if f.calc_area() < 1e-8]
    if flat:
        bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges[:])
        flat = [f for f in bm.faces if f.calc_area() < 1e-8]
    if flat:
        raise ValueError("LOD%d keeps %d zero-area triangles, e.g. at %s"
                         % (level, len(flat), tuple(flat[0].calc_center_median())))
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def _on(v, step):
    return abs(v / step - round(v / step)) < 1e-6


def brick_problems():
    """The brickwork, on the catalog module (scripts/brickwork.py), as the
    plant hall's: every height the brick meets something at on a course
    line (the house's plinth, slab and every opening casing's head and foot;
    the yard wall's footing and coping); every opening casing's sides, and
    the gate opening's, on a whole or half stretcher in the U its wall
    samples; the bond turning a half stretcher at the house's four corners.
    The yard wall's 0.36 m piers and 0.24 m wall are left as they are: a
    pier is one and a half bricks as the period built them, and the brick
    runs on round it in the wall's band."""
    bad = []
    c, h = L.COURSE, L.HALF
    for what, z in (("house plinth", L.Z_PLINTH), ("house slab's underside", L.Z_WALL),
                    ("yard wall's footing", L.Z_FOOT_F), ("coping's foot", L.Z_COPING),
                    ("yard wall's top", L.Z_FENCE)):
        if not _on(z, c):
            bad.append("the %s at %.6f m is off the coursing" % (what, z))
    for spec in H_WALLS:
        u = spec["u_off"]
        if not _on(u, h):
            bad.append("%s: its U offset is off a half stretcher" % spec["name"])
        for kind, s, z in spec["items"]:
            (l, r, b, t), _ = item_rects(kind, s, z)
            tag = "%s: %s at %.4f" % (spec["name"], kind, s)
            if not ((b < EPS or _on(b, c)) and _on(t, c)):
                bad.append(tag + " is off the coursing")
            if not (_on(u + l, h) and _on(u + r, h)):
                bad.append(tag + " cuts the bond off a half stretcher")
    # the yard wall's band samples U = x (+ 8 m) along the front run
    if not all(_on(x, h) for x in L.GATE_OPEN):
        bad.append("the gate opening's sides are off a half stretcher")
    ring = [s["name"] for s in H_WALLS]
    lens = {s["name"]: Frame(s["p0"], s["p1"]).L for s in H_WALLS}
    for a, b in zip(ring, ring[1:] + ring[:1]):
        ua = L.HOUSE_U_OFF[a] + lens[a]
        ub = L.HOUSE_U_OFF[b]
        if not _on(ua - ub - h, L.BRICK_L):
            bad.append("the house's %s/%s corner does not turn the bond" % (a, b))
    return bad


def check_layout():
    """Assert what the numbers hide and a render would show."""
    problems = brick_problems()
    gap = 0.05
    # house openings: on the wall, clear of corners, piers and each other,
    # under the slab
    blocked = {"front": [(0.0, GATE_E_PIER + L.PIER_W / 2 - HX0 + 0.10)],
               "east": [(JUNCTION_Y - L.PIER_W / 2 - HY0 - 0.10, 4.0)],
               "north": [(0.0, HX1 - (WCX1 - L.PIER_W / 2) + 0.10)],
               "west": [(HY1 - (-WCY + L.PIER_W / 2) - 0.10, 4.0)]}
    for spec in H_WALLS:
        fr = Frame(spec["p0"], spec["p1"])
        rects = []
        for kind, s, z in spec["items"]:
            (l, r, b, t), _ = item_rects(kind, s, z)
            rects.append((kind, l, r, b, t))
            if l < 0.30 or r > fr.L - 0.30:
                problems.append("%s: %s within 0.30 m of a corner" % (spec["name"], kind))
            if t > L.Z_WALL - 0.15:
                problems.append("%s: %s top %.2f is under the slab" % (spec["name"], kind, t))
            for a, bb in blocked[spec["name"]]:
                if l < bb and a < r:
                    problems.append("%s: %s runs into a pier" % (spec["name"], kind))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b_ = rects[i], rects[j]
                if a[1] < b_[2] + gap and b_[1] < a[2] + gap and \
                        a[3] < b_[4] + gap and b_[3] < a[4] + gap:
                    problems.append("%s: %s and %s overlap" % (spec["name"], a[0], b_[0]))
    w, h = L.OPENINGS["door"][:2]
    if not 2.0 <= h <= 2.4:
        problems.append("the door leaf is %.2f m, outside 2.0-2.4" % h)
    # plan: everything inside the piers' outline, the gate between its piers
    half = L.PIER_W / 2.0
    if abs(GATE_W_PIER + half - L.GATE_OPEN[0]) > EPS or \
            abs(GATE_E_PIER - half - L.GATE_OPEN[1]) > EPS:
        problems.append("the gate piers do not frame the opening")
    if not (HX0 < GATE_E_PIER + half < HX0 + 0.10):
        problems.append("the gate's east pier does not stand against the house")
    if L.GATE_Y[0] < -WCY - HW or L.GATE_Y[1] > -WCY + HW:
        problems.append("the gate leaves stand outside the wall's thickness")
    if abs(HX1 - (WCX1 + HW)) > EPS or abs(HY0 + WCY + HW) > EPS:
        problems.append("the house's front and east walls are not in the wall's planes")
    west, inner_y = WCX0 + HW, WCY - HW
    px, py, _ = L.PLINTH
    for ty in L.T_Y:
        if abs(ty) + py / 2 > inner_y - 0.6:
            problems.append("a plinth crowds the yard wall")
        if abs(ty) - py / 2 < L.FIRE[2] + 0.5:
            problems.append("a plinth crowds the fire wall")
        if abs(ty) - L.TANK[1] / 2 - L.RAD_D + 0.05 < L.FIRE[2] + 0.8:
            problems.append("a radiator bank is within 0.8 m of the fire wall")
        if TX + px / 2 > HX0 - 2.0:
            problems.append("a plinth leaves under 2.0 m to the house")
        for k in PH:
            bx, by = bushing_xy(ty, k)
            if abs(by - ty) + 0.15 > L.TANK[1] / 2 or bx - 0.15 < TX - L.TANK[0] / 2:
                problems.append("a bushing's turret overhangs the cover")
            if abs(ty + k * L.SW_PHASE) > L.G_COL_Y - 0.5:
                problems.append("a string is within 0.5 m of a gantry column")
    if L.FIRE[0] > TX - L.TANK[0] / 2 - 0.5 + EPS or L.FIRE[1] < TX + L.TANK[0] / 2 + 0.5 - EPS:
        problems.append("the fire wall does not run 0.5 m past both tank ends")
    top_cons = L.CONS_Z + L.CONS_R
    if L.FIRE[3] < top_cons:
        problems.append("the fire wall is lower than the conservators")
    if abs(L.CONS_X) + L.CONS_R > L.TANK[0] / 2 or L.CONS_X - L.CONS_R < L.BUSH_X + 0.3:
        problems.append("the conservator overhangs the cover or crowds the bushings")
    p = L.G_PAD[0] / 2
    if L.G_X - p < west + 0.3 or L.G_COL_Y + p > inner_y - 0.3:
        problems.append("a gantry pad crowds the yard wall")
    if L.G_TOP <= L.G_BEAM_Z[1] + 0.05:
        problems.append("the columns do not rise above the beam")
    # the switchgear bays: west to east with a walkway between each part,
    # clear of the yard wall and the fire wall, phases apart
    order = [("gantry pad", L.G_X + p), ("disconnector", L.DIS_DECK[0]),
             ("disconnector", L.DIS_DECK[1]), ("breaker stand", L.BRK_X - L.BRK_DECK[0] / 2),
             ("breaker stand", L.BRK_X + L.BRK_DECK[0] / 2),
             ("current transformers", L.CT_X - L.CT_TABLE[0] / 2),
             ("current transformers", L.CT_X + L.CT_TABLE[0] / 2), ("plinth", TX - px / 2)]
    for (na, xa), (nb, xb) in zip(order[0::2], order[1::2]):
        if xb - xa < 0.6:
            problems.append("%s and %s are %.2f m apart, under 0.6" % (na, nb, xb - xa))
    for ty in L.T_Y:
        if abs(ty) + L.SW_HALF > inner_y - 0.5:
            problems.append("a switchgear frame crowds the yard wall")
        if abs(ty) - L.SW_HALF < 1.0:
            problems.append("the two bays' frames are under 2 m apart")
    if L.SW_PHASE - 2 * 0.17 < 0.6:
        problems.append("the breaker heads are under 0.6 m apart")
    if abs(L.DIS_LEG[2]) + L.DIS_LEG[1] / 2 > L.SW_HALF or L.BRK_LEG[1] > L.SW_HALF or \
            L.CT_LEG[1] + L.CT_LEG[0] / 2 > L.SW_HALF:
        problems.append("a leg stands outside its frame")
    if L.POST_Z0 + L.POST_H > L.BRK_Z0 + L.Z_BRK[3] + 0.2:
        problems.append("the disconnector stands over the breakers' tops")
    # the conductors: the spans near level, clear of the covers; the drop
    # well under the strings
    for ty in L.T_Y:
        for k in PH:
            for p0, p1, sag, kind in spans(ty, k):
                if kind == "span":
                    run = math.hypot(p1.x - p0.x, p1.y - p0.y)
                    slope = math.degrees(math.atan2(abs(p1.z - p0.z), run))
                    if slope > 15.0:
                        problems.append("a span slopes at %.0f degrees" % slope)
                low = min(sag_point(p0, p1, sag, i / 20.0).z for i in range(21))
                if low < min(p0.z, p1.z) - 0.25:
                    problems.append("a conductor sags %.2f m under its lower end"
                                    % (min(p0.z, p1.z) - low))
            p0, p1, sag, _ = spans(ty, k)[-1]
            for i in range(21):
                q = sag_point(p0, p1, sag, i / 20.0)
                if TX - L.TANK[0] / 2 - 0.1 < q.x and q.z < L.TANK_Z[1] + 0.6:
                    problems.append("a conductor passes within 0.6 m of a cover")
                    break
    if Z_CLAMP - Z_POST_TOP < 2.0:
        problems.append("the strings hang within 2 m of the disconnector")
    # the house band and fire wall
    if L.FIRE[3] > L.H_TOP:
        problems.append("the fire wall rises above the house band")
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame.

    The footprint is the switchgear house's outer wall outline at ground
    level, the 5.0 x 4.0 m rectangle: CLAUDE.md's footprint leaves out
    fences, and the yard wall, its piers and gate, the plinths, the fire wall
    and the gantry are not the building's walls. One storey, its floor on the
    ground, inside walls 0.24 m thick. The house door is the one door, an
    entrance, main. The gate is not a door in the schema's sense (it leads
    into an open yard, not an occupied space) and is reported in notes.md.
    """
    spec = H_WALLS[0]
    k, s, z = spec["items"][0]
    w, h = L.OPENINGS[k][:2]
    t = L.H_WALL_T
    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(HX0, HY0), (HX1, HY0), (HX1, HY1), (HX0, HY1)],
        "storeys": [(0.0, (HX1 - HX0 - 2 * t) * (HY1 - HY0 - 2 * t))],
        "doors": [model_facts.wall_door("switchgear", "entrance", spec["p0"], spec["p1"],
                                        s, z, w, h, main=True)],
    }


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four
    orthographic elevations, a plan from above, and a raised three-quarter
    aerial off the front corner (shell_build.render_views()). Working views
    only -- not committed."""
    return SB.render_views(BUILD, out_dir, level, res, distance=60.0)


if __name__ == "__main__":
    BUILD.main(build_all, facts)
