# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of viljakuivuri_tower, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite Finnish farm grain dryer (viljankuivuri): a 5 x 5 m board tower,
10.5 m to its eave under a 30 degree gable roof, with a low mono-pitch intake
lean-to on its east side holding the tipping-pit door, a steel furnace flue
through the lean-to's roof, and a round galvanised storage bin behind,
fed by a sloping spout from high on the tower's back.

Construction is a set of closed solids unioned with Blender's exact boolean:
the tower body, the lean-to body, the two roof slabs, the bin's wall, its
cone, its fill collar, the spout, the flue and the three downpipes
(scripts/downpipes.py), which hang from the gutter painted on the eave
fascias; the tower's east one spills onto the lean-to's roof. The lean-to
stands against the
tower with its inner wall on the tower's east wall plane, and the union
removes the two coincident walls. The result is the boundary of one empty
volume, so no interior geometry can occur.

The walls are textured as a trim sheet (see facade_atlas.py). The tower is
taller than any band, so its walls are cut at the board joints, 4.80 m and
8.80 m, and each strip above the first maps onto the same band, W2, which
repeats in V. The bin's wall is cut at its 1.00 m rings the same way. Every
number the two files share is imported from facade_atlas.py.
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
importlib.reload(L)

ASSET = L.ASSET
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import downpipes as DP  # noqa: E402
import model_facts  # noqa: E402
from asset_build import bounds as _bounds, to_object, union  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT)
_show_only, preview_studio = BUILD.show_only, BUILD.preview_studio
PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ------------------------------------------------------------------ massing
# Front faces -Y. The tower is centred on the build origin; its ridge runs
# along Y, so the gables face the front and the back.
TX = TY = 2.5                                    # tower half-sizes, 5.0 x 5.0 m
T_TAN = math.tan(math.radians(30.0))
ROOF_T = L.FASC_H / PPM                          # slabs' vertical thickness
T_EAVE_OV = 0.40
T_RAKE_OV = 0.40
Z_T_EAVE = 10.50
Z_T_TOP = Z_T_EAVE + 0.10                        # walls run on into the slab
Z_T_APEX = Z_T_TOP + TX * T_TAN

# Intake lean-to against the tower's east wall, its mono-pitch roof falling
# away from the tower. It is set back 0.40 m from the tower's front and back
# faces, so its rakes stop short of them, and it runs LT_IN into the tower:
# the union then meets no coincident faces (the exact solver keeps two
# coincident opposite walls as a double wall).
LT_IN = 0.15
LX0, LX1 = TX - LT_IN, TX + 3.90
LY = TY - 0.40
LT_L = LX1 - LX0
LT_TAN = math.tan(math.radians(15.0))
Z_LT_EAVE = 3.60
Z_LT_TOP = Z_LT_EAVE + 0.10
Z_LT_HIGH = Z_LT_TOP + LT_L * LT_TAN             # wall top, buried in the tower
Z_LT_VIS = Z_LT_TOP + (LX1 - TX) * LT_TAN        # wall top where it meets the tower
LT_EAVE_OV = 0.40
LT_RAKE_OV = 0.25

# The storage bin: 3.0 m across, 5.5 m to its eave, behind the lean-to.
BX, BY = 4.40, 4.30
BIN_R = 1.50
Z_BIN = 5.50
BIN_EAVE_R = L.BIN_EAVE_R
BIN_LIP = (5.45, 5.50)                           # the cone's rolled eave
BIN_TAN = math.tan(math.radians(25.0))
Z_BIN_APEX = BIN_LIP[1] + BIN_EAVE_R * BIN_TAN
COLLAR_R = L.COLLAR_R
COLLAR_Z = (Z_BIN_APEX - 0.25, Z_BIN_APEX + 0.20)
# Ring cuts: the bin's wall maps one 1.00 m ring onto the BIN band, so it is
# cut at every ring joint; the bottom strip is half a ring.
BIN_CUTS = [0.0, 0.5, 1.5, 2.5, 3.5, 4.5, Z_BIN]

# The spout: from inside the tower, out through its back wall at about 9 m,
# down at 40 degrees into the bin's fill collar.
SPOUT_R = 0.10
SPOUT_A = (1.60, 2.20, 9.60)
SPOUT_B = (BX, BY, COLLAR_Z[1] - 0.15)

# The furnace flue: plain black steel up through the lean-to's roof, open at
# the top round a sooted mouth.
FLUE_XY = (3.20, -1.00)
FLUE_R = 0.15
FLUE_WALL = 0.03
FLUE_Z = (3.90, 7.00)
FLUE_DEPTH = 0.50

# Sides per round part and tier.
SIDES = {"bin": (16, 12, 8, 6), "spout": (8, 6, 4, 4), "flue": (8, 6, 4, 4),
         "collar": (8, 8, 6, 4)}

# --------------------------------------------------------------- elevations
# Each wall runs counter-clockwise seen from above, outward face on its
# right. (p0, p1, top profile, openings, corner board at start, at end).
# Openings are (kind, s, sill z): s is the centre along the wall from p0.
# The front's stair-landing windows stand one above the other, 4.0 m apart,
# each half a metre over a board joint. The furnace room at the foot has a
# window to the west and one to the back, and a landing window lights the
# west face between the joints, so no face is a blank 10 m board wall.
TOWER_WALLS = {
    "front": ((-TX, -TY), (TX, -TY), "gable", [
        ("door", 1.30, L.Z_FLOOR), ("win", 3.55, 1.30), ("win", 3.55, 5.30),
        ("win", 3.55, 9.30)], (True, True)),
    "east": ((TX, -TY), (TX, TY), "eave", [], (True, True)),
    "rear": ((TX, TY), (-TX, TY), "gable", [
        ("louvre", 2.50, 9.20), ("win", 3.40, 1.30)], (True, True)),
    "west": ((-TX, TY), (-TX, -TY), "eave", [
        ("win", 2.50, 1.30), ("win", 2.50, 7.30)], (True, True)),
}
LT_WALLS = {
    "lt_front": ((LX0, -LY), (LX1, -LY), "down", [
        ("door_vehicle", 2.05 + LT_IN, L.Z_FLOOR)], (False, True)),
    "lt_east": ((LX1, -LY), (LX1, LY), "lt_eave", [], (True, True)),
    "lt_rear": ((LX1, LY), (LX0, LY), "up", [], (True, False)),
    "lt_west": ((LX0, LY), (LX0, -LY), "high", [], (False, False)),
}
# Offsets into the tiling bands, in metres. The lean-to's front and rear
# continue the tower's boards across the joint between them.
U_OFF = {"front": 0.0, "east": 5.3, "rear": 10.6, "west": 2.9,
         "lt_front": 5.0, "lt_east": 7.7, "lt_rear": 13.1, "lt_west": 0.0}

# Downpipes (scripts/downpipes.py), from the gutters painted on the eave
# fascias, each near the front end of its eave so the front and the catalog's
# oblique see it. The tower's west pipe and the lean-to's run to the ground.
# The tower's east eave stands over the lean-to, whose roof covers that wall
# all but 0.40 m at each end, too little for a pipe CORNER from the corner and
# clear of the 0.25 m rake. So the east pipe comes down the tower's wall above
# the lean-to and spills onto its slope, which carries the water to the
# lean-to's own gutter and pipe: RoofPipe below lifts its foot, the shoe or
# the straight pipe's open end, to ON_ROOF over the slope at the wall. It
# stands EAST_PIPE_S from the front corner, ON_ROOF_IN inside the lean-to's
# front wall plane, so the shoe lands on the roof and not on the rake.
EAST_PIPE_S = 0.75
ON_ROOF = 0.10                   # the straight foot's height over the slope
ON_ROOF_IN = 0.30


def lt_roof_top(x):
    """The lean-to's slope surface at x."""
    return Z_LT_EAVE + (LX1 - x) * LT_TAN + ROOF_T


class RoofPipe(DP.Pipe):
    """A downpipe that ends on a lower roof instead of the ground: DP.Pipe's
    path, with the part below the swan-neck's offset (the shoe, or a
    straight pipe's foot) raised by *lift*."""

    def __init__(self, pipe, lift):
        super().__init__(pipe.p0, pipe.p0 + pipe.t * pipe.length, pipe.s,
                         pipe.under, pipe.outlet)
        self.lift = lift

    def path(self, bent=True):
        pts = super().path(bent)
        k = 2 if bent else 1                     # DP.Pipe.path's foot points
        return pts[:-k] + [(out, z + self.lift) for out, z in pts[-k:]]


DOWNPIPE_SPOTS = [("west", 2 * TY - DP.CORNER), ("lt_east", DP.CORNER),
                  ("east", EAST_PIPE_S)]
_ALL_WALLS = {**TOWER_WALLS, **LT_WALLS}
DOWNPIPES = [
    DP.eave_pipe(*TOWER_WALLS["west"][:2], DOWNPIPE_SPOTS[0][1], Z_T_EAVE, T_TAN,
                 T_EAVE_OV),
    DP.eave_pipe(*LT_WALLS["lt_east"][:2], DOWNPIPE_SPOTS[1][1], Z_LT_EAVE, LT_TAN,
                 LT_EAVE_OV),
    RoofPipe(DP.eave_pipe(*TOWER_WALLS["east"][:2], DOWNPIPE_SPOTS[2][1], Z_T_EAVE,
                          T_TAN, T_EAVE_OV),
             lt_roof_top(TX + DP.GAP) + ON_ROOF - DP.FOOT),
]


def top_fn(profile, length):
    """The wall's top edge as z(s), and the s of its interior kinks."""
    if profile == "gable":
        return (lambda s: Z_T_TOP + min(s, length - s) * T_TAN), [length / 2.0]
    if profile == "eave":                        # the tower's eave walls
        return (lambda s: Z_T_TOP), []
    if profile == "lt_eave":                     # the lean-to's outer wall
        return (lambda s: Z_LT_TOP), []
    if profile == "down":                        # high at s = 0, the tower
        return (lambda s: Z_LT_TOP + (length - s) * LT_TAN), []
    if profile == "up":                          # high at s = length
        return (lambda s: Z_LT_TOP + s * LT_TAN), []
    if profile == "high":
        return (lambda s: Z_LT_HIGH), []
    raise ValueError(profile)


def item_mode(kind, level):
    """How an opening is built at each tier.

    ring  - LOD0: the casing is a ring of faces on the wall, the opening inside
            it recessed with reveals and closed by its glass, leaf or louvre.
    cut   - LOD1: one recess the size of the casing, casing painted on it.
    flush - LOD2/3: the casing rect as a flat quad in the wall.
    """
    return ("ring", "cut", "flush", "flush")[level]


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
        # zero-area test in double precision, relative to the first vertex
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

    def s_of(self, co):
        return (co.x - self.p0.x) * self.t.x + (co.y - self.p0.y) * self.t.y


# ------------------------------------------------------------ UV mappings
def uv_band(fr, y0, z_ref, u_off):
    return lambda co: ((fr.s_of(co) + u_off) * PPM, y0 + (co.z - z_ref) * PPM)


def uv_item(fr, kind, s_left, z_bot):
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


def wall_bands(fr, u_off):
    """(z_lo, z_hi, uv) for the band each height range of a wall samples:
    S1 from the ground to the first joint, then W2 per 4 m strip, each strip
    mapped from its own joint."""
    return [(0.0, L.Z_J1, uv_band(fr, L.S1_Y0, 0.0, u_off)),
            (L.Z_J1, L.Z_J2, uv_band(fr, L.W2_Y0, L.Z_J1, u_off)),
            (L.Z_J2, L.Z_J2 + L.W2_P, uv_band(fr, L.W2_Y0, L.Z_J2, u_off))]


# ================================================================== walls
def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge (openings that
    share head and sill heights line up, and the triangulator then joins
    three collinear corners)."""
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


def clip_z(poly, zlo, zhi):
    """A convex wall outline (s, z) clipped to zlo <= z <= zhi."""
    def clip(pts, inside, cut):
        out = []
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            if inside(p):
                out.append(p)
                if not inside(q):
                    out.append(cut(p, q))
            elif inside(q):
                out.append(cut(p, q))
        return out

    def at(z):
        def cut(p, q):
            t = (z - p[1]) / (q[1] - p[1])
            return (p[0] + t * (q[0] - p[0]), z)
        return cut

    pts = clip(poly, lambda p: p[1] >= zlo - EPS, at(zlo))
    pts = clip(pts, lambda p: p[1] <= zhi + EPS, at(zhi))
    out = []
    for p in pts:
        p = (round(p[0], 6), round(p[1], 6))
        if not out or abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-6 and abs(out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    return out


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
        # a door has no bottom casing: the hole carries the leaf's corners too
        return [(ol, ob), (il, ib), (ir, ib), (orr, ob), (orr, ot), (ol, ot)]
    return o


def build_wall(B, fr, profile, edge_z, corners, items, u_off, level):
    """One elevation: corner-board columns, then board regions with holes,
    one region per band the wall's height crosses.

    *edge_z* is the set of heights every corner of this solid carries, so two
    walls meeting at a corner meet on exactly the same vertices.
    """
    Lw = fr.L
    top, kinks = top_fn(profile, Lw)
    c0, c1 = corners
    s0 = L.CW if c0 else 0.0
    s1 = Lw - L.CW if c1 else Lw

    def ez(s):
        return sorted({e for e in edge_z if EPS < e < top(s) - EPS} | {top(s)})

    bands = wall_bands(fr, u_off)
    s1band = bands[0][2]
    for a, b, has in ((0.0, L.CW, c0), (Lw - L.CW, Lw, c1)):
        if not has:
            continue
        zt = max(top(a), top(b))
        strip = uv_strip(fr, L.CORNER, a, b, L.Z_FLASH, zt)
        lo = [0.0] + [e for e in edge_z if EPS < e < min(top(a), top(b)) - EPS]
        for k, za in enumerate(lo):
            if k + 1 < len(lo):
                zb = lo[k + 1]
                poly = [(a, za), (b, za), (b, zb), (a, zb)]
            else:
                zb = zt
                poly = [(a, za), (b, za), (b, top(b)), (a, top(a))]
            fn = s1band if zb <= L.Z_FLASH + EPS else strip
            B.face([fr.P(s, z) for s, z in poly], fn)

    outline = ([(s0, 0.0), (s1, 0.0)] + [(s1, z) for z in ez(s1)]
               + [(k, top(k)) for k in sorted(kinks, reverse=True) if s0 < k < s1]
               + [(s0, z) for z in reversed(ez(s0))])
    rects = {(kind, s, z): item_rects(kind, s, z)[0] for kind, s, z in items}
    placed = 0
    zmax = max(z for _, z in outline)
    for zlo, zhi, fn in bands:
        if zlo >= zmax - EPS:
            continue
        region = clip_z(outline, zlo, zhi)
        its = [k for k, r in rects.items() if r[2] > zlo - EPS and r[3] < zhi + EPS]
        holes = [build_item(B, fr, kind, s, z, level) for kind, s, z in its]
        placed += len(its)
        fill_region(B, fr, region, holes, fn)
    if placed != len(rects):
        raise ValueError("an opening straddles a board joint on a %.1f m wall" % Lw)


def close_solid(B, apexes=()):
    """Cap a wall ring with an n-gon floor and a lid, both buried (the floor
    on the ground, the lid inside the roof slab); the solid must be closed
    for the boolean to be exact. The rim is walked in edge-index order, so
    the caps start on the same vertex every run. A gable lid is split at its
    ridge between *apexes*."""
    bm = B.bm
    bm.edges.index_update()
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
        raise ValueError("expected a floor and a lid, got %d holes" % len(loops))
    blank = uv_patch("blank")
    for loop in loops:
        B.set_uv(bm.faces.new(loop), blank)
    if apexes:
        a, b = (B.cache[(round(p[0], 4), round(p[1], 4), round(p[2], 4))] for p in apexes)
        bmesh.ops.connect_verts(bm, verts=[a, b])


def tower_body(level):
    B = Builder()
    edge = [0.0, L.Z_FLASH, L.Z_J1, L.Z_J2]
    for name, (p0, p1, prof, items, corners) in TOWER_WALLS.items():
        build_wall(B, Frame(p0, p1), prof, edge, corners, items, U_OFF[name], level)
    close_solid(B, [(0.0, -TY, Z_T_APEX), (0.0, TY, Z_T_APEX)])
    return B


def leanto_body(level):
    B = Builder()
    edge = [0.0, L.Z_FLASH]
    for name, (p0, p1, prof, items, corners) in LT_WALLS.items():
        build_wall(B, Frame(p0, p1), prof, edge, corners, items, U_OFF[name], level)
    close_solid(B)
    return B


# ================================================================== roofs
ROOF_RPM = L.ROOF_H / L.ROOF_SLOPE_LEN           # atlas px per metre up a slope


def slab(section, kinds, axis, a0, a1, slope_v):
    """A roof slab: a closed *section* (across, z) extruded along *axis*
    from a0 to a1. *kinds* names each section edge: slope, fascia, soffit or
    end (a barge). *slope_v(across)* is the distance up the slope from the
    eave edge, for the roof band's V."""
    B = Builder()

    def W(a, p, z):
        return (a, p, z) if axis == "x" else (p, a, z)

    def along(co):
        return co.x if axis == "x" else co.y

    def across(co):
        return co.y if axis == "x" else co.x

    def slope_uv(co):
        return ((along(co) + 16.0) * PPM, L.ROOF_Y0 + slope_v(across(co)) * ROOF_RPM)

    def fascia_uv(z_bot):
        return lambda co: ((along(co) + 16.0) * PPM, L.FASC_Y0 + (co.z - z_bot) * PPM)

    n = len(section)
    for k, kind in enumerate(kinds):
        (p0, z0), (p1, z1) = section[k], section[(k + 1) % n]
        if kind == "slope":
            fn = slope_uv
        elif kind == "fascia":
            fn = fascia_uv(min(z0, z1))
        elif kind == "soffit":
            fn = uv_patch("soffit")
        else:
            fn = uv_patch("barge")
        B.face([W(a0, p0, z0), W(a0, p1, z1), W(a1, p1, z1), W(a1, p0, z0)], fn)
    barge = uv_patch("barge")
    B.face([W(a0, p, z) for p, z in section], barge)
    B.face([W(a1, p, z) for p, z in reversed(section)], barge)
    return B


def tower_roof():
    """A chevron across X, ridge along Y. Its underside meets the east and
    west walls at Z_T_EAVE; the part inside the walls is removed by the
    union, the rest is the soffit."""
    pe = TX + T_EAVE_OV
    z0 = Z_T_EAVE + ROOF_T + TX * T_TAN
    zt = z0 - pe * T_TAN
    sec = [(-pe, zt - ROOF_T), (-pe, zt), (0.0, z0), (pe, zt),
           (pe, zt - ROOF_T), (0.0, z0 - ROOF_T)]
    kinds = ("fascia", "slope", "slope", "fascia", "soffit", "soffit")
    slope_f = math.sqrt(1.0 + T_TAN * T_TAN)
    return slab(sec, kinds, "y", -TY - T_RAKE_OV, TY + T_RAKE_OV,
                lambda p: (pe - abs(p)) * slope_f)


def leanto_roof():
    """The lean-to's mono-pitch slab, from the tower's wall plane out over
    the east eave. Its inner end lies on the tower's wall, which the union
    removes; only the rake overhangs' ends show, as barge."""
    xo = LX1 + LT_EAVE_OV

    def under(x):
        return Z_LT_EAVE + (LX1 - x) * LT_TAN

    sec = [(LX0, under(LX0)), (LX0, under(LX0) + ROOF_T), (xo, under(xo) + ROOF_T),
           (xo, under(xo))]
    # section walked inner end, slope, fascia, underside
    kinds = ("end", "slope", "fascia", "soffit")
    slope_f = math.sqrt(1.0 + LT_TAN * LT_TAN)
    return slab(sec, kinds, "y", -LY - LT_RAKE_OV, LY + LT_RAKE_OV,
                lambda x: (xo - x) * slope_f)


# ============================================================ round parts
def ring_pts(cx, cy, r, n, phase=0.0):
    """n points round a circle. The bin's start at +Y (phase pi/2): its
    eave sets the asset's +Y extent, and every tier's n has a corner there,
    so every tier keeps LOD0's bounds and pivot."""
    return [(cx + r * math.cos(phase + 2 * math.pi * k / n),
             cy + r * math.sin(phase + 2 * math.pi * k / n)) for k in range(n)]


def bin_wall(n):
    """The bin's wall: an n-sided prism cut at every ring joint. U runs once
    round over the full atlas width (the BIN band wraps in U); V maps each
    strip onto the band from its ring's foot."""
    B = Builder()
    pts = ring_pts(BX, BY, BIN_R, n, math.pi / 2.0)
    for j in range(len(BIN_CUTS) - 1):
        za, zb = BIN_CUTS[j], BIN_CUTS[j + 1]
        base = zb - L.BIN_RING                  # the ring's foot, for V
        for k in range(n):
            (ax, ay), (bx, by) = pts[k], pts[(k + 1) % n]
            u0, u1 = k / n * L.ATLAS, (k + 1) / n * L.ATLAS

            def fn(co, ax=ax, ay=ay, u0=u0, u1=u1, base=base):
                u = u0 if abs(co.x - ax) < 1e-6 and abs(co.y - ay) < 1e-6 else u1
                return u, L.BIN_Y0 + (co.z - base) * PPM
            B.face([(ax, ay, za), (bx, by, za), (bx, by, zb), (ax, ay, zb)], fn)
    blank = uv_patch("blank")
    B.face([(x, y, 0.0) for x, y in reversed(pts)], blank)
    B.face([(x, y, Z_BIN) for x, y in pts], blank)
    return B


def bin_roof(n):
    """The cone: a short rolled lip at the eave, then n triangles to the
    apex. The cone samples the BINROOF disc projected from above; the lip
    and the eave's underside sample flat galvanised patches."""
    B = Builder()
    x0, y0, w, h = L.BINROOF
    cx, cy = x0 + w / 2.0, y0 + h / 2.0

    def plan(co):
        return (cx + (co.x - BX) * L.BINROOF_PPM, cy + (co.y - BY) * L.BINROOF_PPM)

    pts = ring_pts(BX, BY, BIN_EAVE_R, n, math.pi / 2.0)
    za, zb = BIN_LIP
    apex = (BX, BY, Z_BIN_APEX)
    galv = uv_patch("galv")
    for k in range(n):
        (ax, ay), (bx, by) = pts[k], pts[(k + 1) % n]
        B.face([(ax, ay, za), (bx, by, za), (bx, by, zb), (ax, ay, zb)], galv)
        B.face([(ax, ay, zb), (bx, by, zb), apex], plan)
    B.face([(x, y, za) for x, y in reversed(pts)], uv_patch("galv_under"))
    return B, plan


def collar(n, plan):
    """The fill collar round the apex, which the spout runs into."""
    B = Builder()
    pts = ring_pts(BX, BY, COLLAR_R, n, math.pi / n)
    za, zb = COLLAR_Z
    galv = uv_patch("galv")
    for k in range(n):
        (ax, ay), (bx, by) = pts[k], pts[(k + 1) % n]
        B.face([(ax, ay, za), (bx, by, za), (bx, by, zb), (ax, ay, zb)], galv)
    B.face([(x, y, zb) for x, y in pts], plan)
    B.face([(x, y, za) for x, y in reversed(pts)], uv_patch("blank"))
    return B


def tube(a, b, r, n, uv):
    """A closed n-sided pipe from point a to point b."""
    B = Builder()
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(d.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    u = d.cross(ref).normalized()
    v = d.cross(u)
    ring = [u * (r * math.cos(2 * math.pi * k / n)) + v * (r * math.sin(2 * math.pi * k / n))
            for k in range(n)]
    for k in range(n):
        p, q = ring[k], ring[(k + 1) % n]
        B.face([tuple(a + p), tuple(a + q), tuple(b + q), tuple(b + p)], uv)
    B.face([tuple(a + p) for p in reversed(ring)], uv)
    B.face([tuple(b + p) for p in ring], uv)
    return B


def flue(n):
    """The furnace flue: an n-sided steel pipe whose top is a thin rim round
    the open mouth, the inside lined and floored with soot FLUE_DEPTH down,
    as CLAUDE.md asks of a chimney. The floor stays clear of the lean-to's
    slab, so the union leaves the mouth empty."""
    B = Builder()
    cx, cy = FLUE_XY
    zb, zt = FLUE_Z
    zf = zt - FLUE_DEPTH
    phase = math.pi / n
    out = ring_pts(cx, cy, FLUE_R, n, phase)
    inn = ring_pts(cx, cy, FLUE_R - FLUE_WALL, n, phase)
    side, soot = uv_patch("flue"), uv_patch("soot")
    for k in range(n):
        j = (k + 1) % n
        B.face([out[k] + (zb,), out[j] + (zb,), out[j] + (zt,), out[k] + (zt,)], side)
        B.face([out[k] + (zt,), out[j] + (zt,), inn[j] + (zt,), inn[k] + (zt,)], side)
        B.face([inn[j] + (zf,), inn[k] + (zf,), inn[k] + (zt,), inn[j] + (zt,)], soot)
    B.face([p + (zf,) for p in inn], soot)
    B.face([p + (zb,) for p in reversed(out)], uv_patch("blank"))
    return B


# ================================================================ assembly
def build_lod(level):
    base = to_object(tower_body(level), "tmp_tower")
    roof, plan = bin_roof(SIDES["bin"][level])
    parts = [
        to_object(leanto_body(level), "tmp_leanto"),
        to_object(tower_roof(), "tmp_tower_roof"),
        to_object(leanto_roof(), "tmp_leanto_roof"),
        to_object(bin_wall(SIDES["bin"][level]), "tmp_bin"),
        to_object(roof, "tmp_bin_roof"),
        to_object(collar(SIDES["collar"][level], plan), "tmp_collar"),
        to_object(tube(SPOUT_A, SPOUT_B, SPOUT_R, SIDES["spout"][level],
                       uv_patch("galv")), "tmp_spout"),
        to_object(flue(SIDES["flue"][level]), "tmp_flue"),
    ]
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
        # coplanar boolean subdivisions, keeping UV seams and every real edge
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def check_layout():
    """Assert what the numbers hide and a render would show: openings
    colliding, clipping a corner board or the roof, straddling a board
    joint or the plinth; the lean-to outgrowing S1; the slopes disagreeing
    with the roof band; the bin, spout and flue fouling the building."""
    problems = []
    gap = 0.05
    walls = [(n, Frame(p0, p1), prof, items, corners)
             for n, (p0, p1, prof, items, corners) in list(TOWER_WALLS.items())
             + list(LT_WALLS.items())]
    for name, fr, prof, items, (c0, c1) in walls:
        top, _ = top_fn(prof, fr.L)
        rects = [(k, item_rects(k, s, z)[0]) for k, s, z in items]
        for k, (l, r, b, t) in rects:
            lo = (L.CW if c0 else 0.0) + gap
            hi = fr.L - (L.CW if c1 else 0.0) - gap
            if l < lo or r > hi:
                problems.append("%s: %s at s %.2f..%.2f runs into a corner" % (name, k, l, r))
            for s in (l, r):
                if t > top(s) - 0.10 - gap:              # visible top, under the soffit
                    problems.append("%s: %s top %.2f is under the roof" % (name, k, t))
            for zj in (L.Z_J1, L.Z_J2):
                if b - gap < zj < t + gap:
                    problems.append("%s: %s crosses the board joint at %.2f" % (name, k, zj))
            if b < L.Z_FLASH + gap and not k.startswith("door"):
                problems.append("%s: %s reaches the plinth" % (name, k))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b_ = rects[i][1], rects[j][1]
                if a[0] < b_[1] + gap and b_[0] < a[1] + gap and \
                        a[2] < b_[3] + gap and b_[2] < a[3] + gap:
                    problems.append("%s: %s and %s overlap" % (name, rects[i][0], rects[j][0]))
    if Z_LT_HIGH > L.Z_J1 - 0.01:
        problems.append("the lean-to's walls (%.2f) outgrow the S1 band (%.2f)"
                        % (Z_LT_HIGH, L.Z_J1))
    if LT_RAKE_OV > TY - LY - 0.10:
        problems.append("the lean-to's rakes reach the tower's face plane")
    if Z_T_APEX > L.Z_J2 + L.W2_P:
        problems.append("the tower's apex is above W2's second repeat")
    lt_slope = (LX1 - TX + LT_EAVE_OV) * math.sqrt(1.0 + LT_TAN ** 2)
    if abs(lt_slope - L.ROOF_SLOPE_LEN) > 1e-3:
        problems.append("lean-to slope is %.4f m, the atlas assumes %.4f"
                        % (lt_slope, L.ROOF_SLOPE_LEN))
    if (TX + T_EAVE_OV) * math.sqrt(1.0 + T_TAN ** 2) > L.ROOF_SLOPE_LEN:
        problems.append("the tower's slope is longer than the roof band")
    # the bin: clear of the lean-to's rake and the tower, its eave over the
    # lean-to's roof
    if BY - BIN_R < LY + LT_RAKE_OV + 0.20:
        problems.append("the bin stands within 0.2 m of the lean-to's rake")
    if BIN_LIP[0] < Z_LT_HIGH + ROOF_T + 0.3:
        problems.append("the bin's eave is not clear above the lean-to")
    if math.hypot(BX - min(max(BX, -TX), TX), BY - TY) < BIN_EAVE_R + 0.3:
        problems.append("the bin stands within 0.3 m of the tower")
    # the spout: steep enough for grain to run, through the tower's back wall
    # clear of its corners and the louvre
    a, b = Vector(SPOUT_A), Vector(SPOUT_B)
    d = b - a
    angle = math.degrees(math.atan2(-d.z, math.hypot(d.x, d.y)))
    if angle < 35.0:
        problems.append("the spout falls at %.1f degrees, under 35" % angle)
    t = (TY - a.y) / d.y
    hit = a + d * t
    if not (L.CW + 0.25 < TX - hit.x < 2.5 - 0.875 - 0.25):
        problems.append("the spout leaves the back wall at x %.2f, near a corner or "
                        "the louvre" % hit.x)
    if abs(hit.z - L.Z_J2) < 0.25:
        problems.append("the spout leaves the back wall on the board joint")
    # the flue: clear of the tower wall, its mouth's floor above the slab
    fx, fy = FLUE_XY
    under = Z_LT_EAVE + (LX1 - fx) * LT_TAN
    if fx - FLUE_R - TX < 0.4:
        problems.append("the flue is within 0.4 m of the tower")
    if FLUE_Z[1] - FLUE_DEPTH < under + ROOF_T + 0.3:
        problems.append("the flue's sooted floor is down in the lean-to's roof")
    if FLUE_Z[0] > under - 0.1:
        problems.append("the flue's foot is not inside the lean-to")
    # downpipes clear of their walls' corners and openings, and of the bin
    for (w, _s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        avoid = [(k,) + item_rects(k, s, z)[0][:2] for k, s, z in _ALL_WALLS[w][3]]
        problems += DP.problems(pipe, "the %s downpipe" % w, avoid)
        foot = pipe.point(0.0, DP.OUT, 0.0)
        if math.hypot(foot.x - BX, foot.y - BY) < BIN_EAVE_R + DP.A + 0.3:
            problems.append("the %s downpipe is within 0.3 m of the bin" % w)
    # the east pipe spills onto the lean-to's slope: over the roof, clear of
    # its rakes, and its foot just above the sheet at every tier's path
    east = DOWNPIPES[2]
    y = -TY + east.s
    if not -LY + ON_ROOF_IN - EPS <= y <= LY - ON_ROOF_IN + EPS:
        problems.append("the east downpipe is not %.2f m inside the lean-to's "
                        "walls" % ON_ROOF_IN)
    for bent in (True, False):
        out, z = east.path(bent)[-1]
        r = DP.A / math.cos(math.pi / 8)
        gap = z - r - lt_roof_top(TX + out + r)
        if not 0.03 < gap < 0.25:
            problems.append("the east downpipe's %s foot is %.2f m over the lean-to's "
                            "roof" % ("bent" if bent else "straight", gap))
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the tower and the lean-to's wall
    outline; the bin is equipment standing apart and is left out. The one
    storey is the ground floor of the tower base and the lean-to: the tower
    above it is machinery space, not an occupied storey."""
    def door(door_id, kind, wall, item, main=False):
        p0, p1, items = wall[0], wall[1], wall[3]
        s, z = next((s, z) for k, s, z in items if k == item)
        w, h = L.OPENINGS[item][:2]
        return model_facts.wall_door(door_id, kind, p0, p1, s, z, w, h, main)

    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-TX, -TY), (TX, -TY), (TX, -LY), (LX1, -LY), (LX1, LY),
                      (TX, LY), (TX, TY), (-TX, TY)],
        "storeys": [(L.Z_FLOOR, 2 * TX * 2 * TY + (LX1 - TX) * 2 * LY)],
        "doors": [door("front", "entrance", TOWER_WALLS["front"], "door", main=True),
                  door("intake", "vehicle", LT_WALLS["lt_front"], "door_vehicle")],
    }


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four
    orthographic elevations, a plan from above, and a raised three-quarter
    aerial off the front corner. Working views only, not committed."""
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
