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
and power plant: a 16.0 x 12.0 m compound behind a 2.0 m brick wall on brick
piers, closed at the front by a sheet-steel double gate. Inside, two power
transformers stand on concrete plinths either side of a brick fire wall,
their high-voltage bushings toward a galvanised H-section portal on the west
(incoming) side, from whose beam a suspension string over each phase holds a
rigid tubular bus down to its bushing. The small red brick switchgear house
stands in the front-east corner, its front and east walls in the yard wall's
outer planes, its steel door on the street.

Construction is a set of closed solids unioned with Blender's exact boolean
(asset_build.union): the switchgear house (one solid with its openings, slab
edge and roof), the wall's runs, its piers and the gate; per transformer the
plinth, tank, two radiator banks, the conservator and its saddles, three
bushings and the cable box; the fire wall; the gantry's two columns, beam and
foundation pads, six insulator strings and six bus tubes. There is no ground:
every solid stands on z = 0 or on another solid.

The yard has no glazing, so it has no emission map (CLAUDE.md, Output
Contract); BUILD below is asset_build.Asset with night_lit=False.
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
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import model_facts  # noqa: E402
from asset_build import bounds as _bounds, to_object, union  # noqa: E402

asset_build.check_toolchain()


BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT, night_lit=False)
PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ------------------------------------------------------------------ the wall
# Pier centres along each run of the yard wall. The front run stops at the
# gate's west pier; the gate's east pier stands against the house's front
# corner; the east run starts at a pier against the house's north wall.
WCX, WCY = L.WCX, L.WCY
HW = L.WALL_T / 2.0
GATE_W_PIER = L.GATE_OPEN[0] - L.PIER_W / 2.0
GATE_E_PIER = L.GATE_OPEN[1] + L.PIER_W / 2.0
JUNCTION_Y = L.HY1               # the east run's pier against the house


def spaced(a, b, n):
    return [a + (b - a) * i / n for i in range(n + 1)]


PIERS_FRONT = [(x, -WCY) for x in spaced(-WCX, GATE_W_PIER, 3)] + [(GATE_E_PIER, -WCY)]
PIERS_WEST = [(-WCX, y) for y in spaced(-WCY, WCY, 4)[1:-1]]
PIERS_NORTH = [(x, WCY) for x in spaced(-WCX, WCX, 5)]
PIERS_EAST = [(WCX, y) for y in spaced(WCY, JUNCTION_Y, 3)[1:]]
PIERS = PIERS_FRONT + PIERS_WEST + PIERS_NORTH + PIERS_EAST
# The piers LOD3 keeps: the gate's two and the junction pier. Its wall is
# one pier thick (RUNS_THICK), so the other piers' faces fold into the
# wall's and the plan bounds stay the piers' outer faces.
PIERS_KEPT = [(GATE_W_PIER, -WCY), (GATE_E_PIER, -WCY), (WCX, JUNCTION_Y)]

# Wall runs as (x0, x1, y0, y1), each ending inside a pier (or, the east
# run, inside the house) so no end face is left in the open.
RUNS = [
    (-WCX, GATE_W_PIER, -WCY - HW, -WCY + HW),          # front, west of the gate
    (-WCX - HW, -WCX + HW, -WCY, WCY),                  # west
    (-WCX, WCX, WCY - HW, WCY + HW),                    # north
    (WCX - HW, WCX + HW, JUNCTION_Y - 0.10, WCY),       # east
]
FX, FY, PW = L.FX, L.FY, L.PIER_W
RUNS_THICK = [
    (-FX, GATE_W_PIER, -FY, -FY + PW),
    (-FX, -FX + PW, -FY, FY),
    (-FX, FX, FY - PW, FY),
    (FX - PW, FX, JUNCTION_Y, FY),
]

# ----------------------------------------------------------------- the house
HX0, HX1, HY0, HY1 = L.HX0, L.HX1, L.HY0, L.HY1
HI, LO = L.Z_LOUVRE_HI, L.Z_LOUVRE_LO
# Each wall runs counter-clockwise seen from above, outward face on its
# right; s runs along it from p0. items: (kind, s at the centre, z of the
# sill or threshold).
H_WALLS = [
    dict(name="front", p0=(HX0, HY0), p1=(HX1, HY0),
         items=[("door", 1.30, 0.0), ("louvre", 3.55, HI)], u_off=0.0),
    dict(name="east", p0=(HX1, HY0), p1=(HX1, HY1),
         items=[("louvre", 1.20, HI), ("louvre", 2.80, HI)], u_off=5.0),
    dict(name="north", p0=(HX1, HY1), p1=(HX0, HY1),
         items=[("louvre", 1.40, HI)], u_off=9.0),
    dict(name="west", p0=(HX0, HY1), p1=(HX0, HY0),
         items=[("louvre", 2.00, LO)], u_off=14.0),
]

# ------------------------------------------------------------ the transformers
TX = L.T_X
PH = (-1, 0, 1)                  # phases, as multiples of L.PHASE across Y


def bushing_xy(ty, k):
    return TX + L.BUSH_X, ty + k * L.PHASE


def string_top():
    """Inside the beam's bottom flange."""
    return L.G_BEAM_Z[0] + 0.02


def bus_ends(ty, k):
    """The tubular bus from the foot of a string to its bushing's terminal:
    each end 0.05 m inside the clamp or the terminal, on its axis."""
    bx, by = bushing_xy(ty, k)
    z_term = L.TANK_Z[1] - 0.05 + L.BUSH_H - 0.05
    z_clamp = string_top() - L.STRING_LEN + 0.04
    return Vector((L.G_X, by, z_clamp)), Vector((bx, by, z_term))


# ------------------------------------------------------------------ tiers
def mode(level):
    """What each tier builds; notes.md, Per-tier triangle counts, says why.

    item    house openings: ring (casing ring, recessed leaf), cut (one
            recess the size of the casing), flush (a painted rect)
    runs    the wall one brick thick between piers, or one pier thick
    louvres the house walls whose louvres are kept (None: all)
    piers   all, or only the gate's and the junction's
    h       the gantry's members as H-sections, or as boxes
    bush    sides of a bushing, and whether its full profile is turned
    string  "discs" (turned profile), sides of a plain prism, or 0 (none)
    bus     sides of the tubular bus, 0 for none
    cons    sides of the conservator; saddles kept or not
    trench  the cable trench covers, or none
    """
    return [
        dict(item="ring", runs=RUNS, louvres=None, piers=PIERS, h=True, bush=(8, True), string=("discs", 6),
             bus=4, cons=(8, True), cable=True, pads=True, rad=True, trench=True),
        dict(item="cut", runs=RUNS, louvres=None, piers=PIERS, h=True, bush=(6, True), string=("prism", 6),
             bus=4, cons=(6, True), cable=True, pads=True, rad=True, trench=True),
        dict(item="flush", runs=RUNS, louvres=None, piers=PIERS, h=False, bush=(4, False),
             string=("prism", 4), bus=3, cons=(4, False), cable=True, pads=True, rad=True,
             trench=True),
        dict(item="flush", runs=RUNS_THICK, louvres=("front", "east"),
             piers=PIERS_KEPT, h=False, bush=(3, None), string=(None, 0),
             bus=0, cons=(4, False), cable=False, pads=False, rad="one",
             trench=False),
    ][level]


# ============================================================== mesh builder
class Builder:
    """One closed solid under construction, with UVs set as faces are made.
    Vertices are shared through a position cache, so faces that meet along an
    edge meet on the same vertices."""

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

    def xy(self, s):
        q = self.p0 + self.t * s
        return q.x, q.y

    def s_of(self, co):
        return (co.x - self.p0.x) * self.t.x + (co.y - self.p0.y) * self.t.y


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.
def uv_patch(name):
    x0, y0, w, h = L.PATCHES[name]
    c = (x0 + w / 2.0, y0 + h / 2.0)
    return lambda co: c


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
    """A closed box; *side(a, b)* returns the uv function of the side face
    from plan point a to b (walked counter-clockwise, outward on the right)."""
    B = Builder()
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for k in range(4):
        a, b = ring[k], ring[(k + 1) % 4]
        B.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)],
               side(a, b))
    B.face([(x, y, z1) for x, y in ring], top)
    B.face([(x, y, z0) for x, y in reversed(ring)], bottom)
    return B


def lathe(c, axis, e1, rings, sides, uvf, cap0, cap1, phase=0.0):
    """A turned solid: *rings* (radius, h) along unit *axis* from point *c*,
    *sides* facets starting at angle *phase* from unit *e1*. uvf(h, frac)
    gives a side vertex's (u, v), frac running 0..1 round; cap0 and cap1
    the first and last rings' caps' uv functions."""
    B = Builder()
    c, axis, e1 = Vector(c), Vector(axis).normalized(), Vector(e1).normalized()
    e2 = axis.cross(e1)

    def P(r, h, k):
        th = phase + 2.0 * math.pi * k / sides
        return tuple(c + axis * h + (e1 * math.cos(th) + e2 * math.sin(th)) * r)

    for i in range(len(rings) - 1):
        (r0, h0), (r1, h1) = rings[i], rings[i + 1]
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
            B.face([P(r0, h0, k), P(r0, h0, k + 1), P(r1, h1, k + 1), P(r1, h1, k)], fn)
    r, h = rings[0]
    B.face([P(r, h, k) for k in reversed(range(sides))], cap0)
    r, h = rings[-1]
    B.face([P(r, h, k) for k in range(sides)], cap1)
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


def h_profile(w, h, tf, tw):
    """An H-section's outline, flanges at u = +-w/2, web along u = 0."""
    a, b = w / 2.0, h / 2.0
    return [(-a, -b), (-a + tf, -b), (-a + tf, -tw / 2), (a - tf, -tw / 2), (a - tf, -b),
            (a, -b), (a, b), (a - tf, b), (a - tf, tw / 2), (-a + tf, tw / 2),
            (-a + tf, b), (-a, b)]


def rect_profile(w, h):
    a, b = w / 2.0, h / 2.0
    return [(-a, -b), (a, -b), (a, b), (-a, b)]


# ================================================================== the wall
def wall_run(x0, x1, y0, y1):
    return box(x0, x1, y0, y1, 0.0, L.Z_FENCE, band(L.F_Y0), uv_patch("coping"),
               uv_patch("blank"))


def pier(x, y):
    h = L.PIER_W / 2.0
    return box(x - h, x + h, y - h, y + h, 0.0, L.Z_PIER, region(L.PIER_R, 0.0),
               uv_patch("coping"), uv_patch("blank"))


def gate():
    """The double gate as one closed plate between the gate piers, its ends
    in them: the front takes the gate region, the back the same leaves
    mirrored, the edges the gate's paint."""
    x0, x1 = L.GATE_OPEN[0] - L.GATE_INTO, L.GATE_OPEN[1] + L.GATE_INTO
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
def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge."""
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


def fill_region(B, fr, outline, holes, uvfn):
    loops = [outline] + holes
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((s, z, 0.0)) for s, z in loop] for loop in loops])
    for a, b, c in _flip_slivers(flat, tris):
        B.face([fr.P(*flat[a]), fr.P(*flat[b]), fr.P(*flat[c])], uvfn)


def recess(B, fr, rect, depth, fn, rev, floor=True):
    l, r, b, t = rect
    c = [(l, b), (r, b), (r, t), (l, t)]
    for k in range(4):
        if k == 0 and not floor:
            continue
        (s0, z0), (s1, z1) = c[k], c[(k + 1) % 4]
        B.face([fr.P(s0, z0), fr.P(s1, z1), fr.P(s1, z1, depth), fr.P(s0, z0, depth)], rev)
    B.face([fr.P(s, z, depth) for s, z in c], fn)


def item_rects(kind, s, z):
    w, h, cs, cb, ct = L.OPENINGS[kind]
    outer = (s - w / 2 - cs, s + w / 2 + cs, z - cb, z + h + ct)
    inner = (s - w / 2, s + w / 2, z, z + h)
    return outer, inner


def uv_item(fr, kind, s_left, z_bot):
    x0, y0 = L.ITEM_ORIGIN[kind]
    return lambda co: (x0 + (fr.s_of(co) - s_left) * PPM, y0 + (co.z - z_bot) * PPM)


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
    """Cap the house's two open rims: the floor on the ground and the roof's
    top. The rims are walked in edge-index order, so the caps start on the
    same vertex every run."""
    bm = B.bm
    bm.edges.index_update()
    order = [e for e in bm.edges if len(e.link_faces) == 1]
    rim = set(order)
    if any(sum(1 for e in v.link_edges if e in rim) != 2
           for e in order for v in e.verts):
        raise ValueError("a rim branches: a T-junction somewhere")
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
        raise ValueError("expected a floor and a roof rim, got %d" % len(loops))
    for loop in loops:
        up = loop[0].co.z > 1.0
        B.set_uv(bm.faces.new(loop), top_uv if up else uv_patch("blank"))


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
        fill_region(B, fr, outline, holes,
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
    out.append(lathe((cx, ty - td / 2, cz), (0, 1, 0), (0, 0, 1), [(r, 0.0), (r, td)],
                     sides, cons_uv, cons_end, cons_end, phase=math.pi / sides))
    if saddles:
        for dy in (-0.55, 0.55):
            out.append(box(cx - 0.06, cx + 0.06, ty + dy - 0.06, ty + dy + 0.06,
                           z1 - 0.05, cz, lambda a, b: uv_patch("steel_dark"),
                           uv_patch("steel_dark"), uv_patch("steel_dark")))
    # bushings
    bs, full = md["bush"]
    if full:
        prof = L.bushing_profile()
    elif full is None:          # LOD3: one tapered prism, turret and porcelain
        prof = [(0.14, 0.0), (0.06, L.BUSH_H)]
    else:
        prof = [(0.15, 0.0), (0.15, 0.27), (0.10, 0.27), (0.06, L.BUSH_H)]
    br = L.BUSH_R
    for k in PH:
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
def gantry(level):
    """The portal: two columns on concrete pads, the beam across their tops,
    a suspension string over each phase and the tubular bus from each string
    down to its bushing."""
    md = mode(level)
    out = []
    g = L.GALV_R
    col_len = L.G_TOP - L.G_PAD[1] + 0.05
    beam_len = 2.0 * L.G_BEAM_Y

    def col_uv(a, b, x0, y0):
        tx, ty = _along(a, b)
        return lambda co: (g[0] + 2.0 + ((co.x - x0 - a[0]) * tx + (co.y - y0 - a[1]) * ty) * PPM,
                           g[1] + (co.z - L.G_PAD[1]) / col_len * g[3])

    for sy in (-1, 1):
        y = sy * L.G_COL_Y
        if md["pads"]:
            p = L.G_PAD[0] / 2.0
            out.append(box(L.G_X - p, L.G_X + p, y - p, y + p, 0.0, L.G_PAD[1],
                           band(L.F_Y0, 2.0), uv_patch("pad_top"), uv_patch("blank")))
        prof = h_profile(L.G_H, L.G_H, L.G_TF, L.G_TW) if md["h"] else \
            rect_profile(L.G_H, L.G_H)
        foot = L.G_PAD[1] - 0.05 if md["pads"] else 0.0
        out.append(extrude(prof, lambda u, v, d, y=y: (L.G_X + u, y + v, d),
                           foot, L.G_TOP,
                           lambda a, b, y=y: col_uv(a, b, L.G_X, y),
                           uv_patch("galv_paint")))
    # the beam: an H on its side, swept along Y
    b0, b1 = L.G_BEAM_Z
    zc = (b0 + b1) / 2.0
    prof = h_profile(b1 - b0, L.G_BEAM_W, L.G_TF, L.G_TW) if md["h"] else \
        rect_profile(b1 - b0, L.G_BEAM_W)

    def beam_side(a, b):
        # a, b are (u, v) with u vertical, v across X
        da = math.hypot(b[0] - a[0], b[1] - a[1])
        tu, tv = (b[0] - a[0]) / da, (b[1] - a[1]) / da
        return lambda co: (g[0] + 2.0 + ((co.z - zc - a[0]) * tu + (co.x - L.G_X - a[1]) * tv) * PPM,
                           g[1] + (co.y + L.G_BEAM_Y) / beam_len * g[3])
    out.append(extrude(prof, lambda u, v, d: (L.G_X + v, d, zc + u),
                       -L.G_BEAM_Y, L.G_BEAM_Y, beam_side, uv_patch("galv_paint")))
    # strings and bus
    kind, sides = md["string"]
    st = L.STRING_R
    top = string_top()
    for ty in L.T_Y:
        for k in PH:
            by = ty + k * L.PHASE
            if kind is not None:
                rings = L.string_profile() if kind == "discs" else \
                    [(0.10, 0.0), (0.10, L.STRING_LEN)]
                out.append(lathe((L.G_X, by, top), (0, 0, -1), (1, 0, 0), rings, sides,
                                 lambda h, frac: (st[0] + frac * st[2], st[1] + h * PPM),
                                 uv_patch("galv_paint"), uv_patch("galv_paint"),
                                 phase=math.pi / sides))
            if md["bus"]:
                p0, p1 = bus_ends(ty, k)
                ax = p1 - p0
                e1 = Vector((0, 1, 0))
                out.append(lathe(p0, ax, e1, [(L.BUS_R, 0.0), (L.BUS_R, ax.length)],
                                 md["bus"], lambda h, frac: L.PATCHES["alu"][:2],
                                 uv_patch("alu"), uv_patch("alu"), phase=math.pi / md["bus"]))
    return out


# ================================================================ assembly
def build_lod(level):
    md = mode(level)
    base = to_object(house(level), "tmp_house")
    solids = [wall_run(*r) for r in md["runs"]]
    solids += [pier(x, y) for x, y in md["piers"]]
    solids.append(gate())
    solids.append(fire_wall())
    if md["trench"]:
        solids += trenches()
    for ty in L.T_Y:
        solids += transformer(ty, level)
    solids += gantry(level)
    parts = [to_object(B, "tmp_%d" % i) for i, B in enumerate(solids)]
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
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


def check_layout():
    """Assert what the numbers hide and a render would show."""
    problems = []
    gap = 0.05
    # house openings: on the wall, clear of corners, piers and each other,
    # under the slab
    blocked = {"front": [(0.0, GATE_E_PIER + L.PIER_W / 2 - HX0 + 0.10)],
               "east": [(JUNCTION_Y - L.PIER_W / 2 - HY0 - 0.10, 4.0)],
               "north": [(0.0, HX1 - (WCX - L.PIER_W / 2) + 0.10)],
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
    if abs(HX1 - (WCX + HW)) > EPS or abs(HY0 + WCY + HW) > EPS:
        problems.append("the house's front and east walls are not in the wall's planes")
    inner_x, inner_y = WCX - HW, WCY - HW
    px, py, _ = L.PLINTH
    for ty in L.T_Y:
        if TX - px / 2 < -inner_x + 0.8 or abs(ty) + py / 2 > inner_y - 0.6:
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
            if abs(by) > L.G_COL_Y - 0.5:
                problems.append("a string is within 0.5 m of a gantry column")
    if L.FIRE[0] > TX - L.TANK[0] / 2 - 0.5 + EPS or L.FIRE[1] < TX + L.TANK[0] / 2 + 0.5 - EPS:
        problems.append("the fire wall does not run 0.5 m past both tank ends")
    top_cons = L.CONS_Z + L.CONS_R
    if L.FIRE[3] < top_cons:
        problems.append("the fire wall is lower than the conservators")
    if abs(L.CONS_X) + L.CONS_R > L.TANK[0] / 2 or L.CONS_X - L.CONS_R < L.BUSH_X + 0.3:
        problems.append("the conservator overhangs the cover or crowds the bushings")
    p = L.G_PAD[0] / 2
    if L.G_X - p < -inner_x + 0.3 or L.G_COL_Y + p > inner_y - 0.3:
        problems.append("a gantry pad crowds the yard wall")
    if L.G_BEAM_Y > inner_y - 0.3:
        problems.append("the beam reaches the yard wall")
    if L.G_TOP <= L.G_BEAM_Z[1] + 0.05:
        problems.append("the columns do not rise above the beam")
    # the bus: its ends inside the clamp and the terminal, clear of every
    # cover, radiator and conservator in between
    for ty in L.T_Y:
        for k in PH:
            p0, p1 = bus_ends(ty, k)
            for x in (TX - L.TANK[0] / 2, TX - L.TANK[0] / 2 + 0.3):
                f = (x - p0.x) / (p1.x - p0.x)
                z = p0.z + f * (p1.z - p0.z)
                if z < L.TANK_Z[1] + 0.4:
                    problems.append("the bus passes within 0.4 m of a cover")
            slope = math.degrees(math.atan2(p0.z - p1.z, p1.x - p0.x))
            if not 15.0 < slope < 50.0:
                problems.append("the bus slopes at %.0f degrees" % slope)
    if string_top() - L.STRING_LEN < L.TANK_Z[1] + L.BUSH_H + 1.5:
        problems.append("the strings hang within 1.5 m of the bushings' tips")
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
    aerial off the front corner. Working views only -- not committed."""
    BUILD.preview_studio()
    BUILD.show_only(level)
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
