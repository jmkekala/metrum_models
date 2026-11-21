# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of savupiippu_brick_round, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports and renders preview.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the preview reads it.

The free-standing chimney stack of a small mid-century Nordic coal-fired
heat and power plant: a round, battered shaft of radial brick, 4.2 m across
at its foot and 2.4 m under its head, on a square brick plinth with a cast
concrete footing and a sloped coping. The head is corbelled out in three
steps to a 1.3 m head band, a projecting crown course and a cast concrete
cap, open at the top round a flue sunk 1 m and sooted. A closed flue inlet,
toward the boiler house, is in the plinth's front (-Y), a cast iron
cleanout hatch low in its east wall. Steel tension bands every 2 m, the step
irons and the down conductor up the back (+Y), and three obstruction lamps
on the head band are texture.

The mesh is one closed solid built directly, no boolean: the plinth's walls
(the inlet cut into the front at LOD0/1), its coping, the coping's flat top
holed by the shaft's foot, and a surface of revolution for the shaft, the
head, the rim and the flue's lining, closed by the flue's floor.

Every number the mesh and the atlas share is imported from facade_atlas.py.
"""

import importlib
import math
import os
import sys

import bmesh
from mathutils import Vector, geometry


HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import facade_atlas as L  # noqa: E402  (layout constants shared with the atlas)
importlib.reload(L)       # an interactive session must not keep a stale layout

ASSET = L.ASSET
EXPORT_DIR = os.path.join(HERE, "export")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
from asset_build import to_object  # noqa: E402

asset_build.check_toolchain()

PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)


BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT, night_lit=False)
get_material, export_all = BUILD.material, BUILD.export_all
_show_only, preview_studio = BUILD.show_only, BUILD.preview_studio
render_preview = BUILD.render_preview


# ----------------------------------------------------------------- tiers
def sides(level):
    """24 sides to 35 m, 16 to 70, 12 to 120, 8 beyond: the polygon's
    sagitta is under three pixels at each switch (notes.md, LOD review)."""
    return L.SIDES[level]


def head_profile(level):
    """The head's (z, r) points and their atlas rows: the three corbel steps
    while they are a few pixels tall, one flare after 70 m."""
    idx = range(len(L.HEAD)) if level < 2 else L.HEAD_FLARE
    return [L.HEAD[i] for i in idx], [L.HEAD_V[i] for i in idx]


def inlet_mode(level):
    """The inlet's 0.25 m recess through LOD1; painted flush after, where it
    is under two pixels deep."""
    return "cut" if level < 2 else "flush"


# ============================================================== mesh builder
class Builder:
    """One closed solid, with UVs given per face corner. Vertices are shared
    through a position cache, so faces meet on the same vertices."""

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cache = {}

    def v(self, co):
        key = (round(co[0], 5), round(co[1], 5), round(co[2], 5))
        vert = self.cache.get(key)
        if vert is None:
            vert = self.bm.verts.new(co)
            self.cache[key] = vert
        return vert

    def face(self, cos, uvs, smooth=False):
        verts = [self.v(co) for co in cos]
        if len(set(verts)) != len(verts):
            raise ValueError("degenerate face at %s" % (cos[0],))
        f = self.bm.faces.new(verts)
        for loop, (u, w) in zip(f.loops, uvs):
            loop[self.uv].uv = (u / L.ATLAS, w / L.ATLAS)
        f.smooth = smooth
        return f


class Frame:
    """A wall plane: s along the wall from p0, z world height, out along the
    outward normal (on the right of p0 -> p1, walking counter-clockwise)."""

    def __init__(self, p0, p1):
        self.p0 = Vector((p0[0], p0[1], 0.0))
        d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
        self.L = d.length
        self.t = d / self.L
        self.n = Vector((self.t.y, -self.t.x, 0.0))

    def P(self, s, z, out=0.0):
        q = self.p0 + self.t * s + self.n * out
        return (q.x, q.y, z)


PH = L.PH
WALLS = {
    "front": ((-PH, -PH), (PH, -PH)),
    "east": ((PH, -PH), (PH, PH)),
    "rear": ((PH, PH), (-PH, PH)),
    "west": ((-PH, PH), (-PH, -PH)),
}


def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge (see
    nostokonehuone_brick/build.py)."""
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


def fill_planar(B, outline, holes, to3d, uvfn):
    """Triangulate a planar region given in 2D (an outline and holes) and add
    it; *to3d* lifts a 2D point, *uvfn* gives the 3D point's UV."""
    loops = [outline] + list(holes)
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((a, b, 0.0)) for a, b in loop] for loop in loops])
    for i, j, k in _flip_slivers(flat, tris):
        cos = [to3d(*flat[n]) for n in (i, j, k)]
        B.face(cos, [uvfn(co) for co in cos])


# ================================================================= plinth
def uv_wall(fr, wall):
    """The plinth band: U along the wall, run on round the corners, V height."""
    u0 = L.U_OFF[wall]

    def f(co):
        s = (Vector(co) - fr.p0).dot(fr.t)
        return ((u0 + s) * PPM, L.PL_Y0 + co[2] * PPM)
    return f


def uv_region(fr, rect, s0, z0):
    x, y, w, h = rect

    def f(co):
        s = (Vector(co) - fr.p0).dot(fr.t)
        return (x + (s - s0) * PPM, y + (co[2] - z0) * PPM)
    return f


def uv_patch(name):
    x, y, w, h = L.PATCHES[name]
    return lambda co: (x + w / 2.0, y + h / 2.0)


def opening(B, fr, wall, spec, rect_px, level, recess):
    """A rectangle in a plinth wall: cut with brick reveals, a concrete sill
    and lintel soffit and its closing plane *recess* deep, or painted flush.
    Returns its outline in (s, z), a hole in the wall."""
    sc, z0, w, h = spec
    s0, s1, z1 = sc - w / 2.0, sc + w / 2.0, z0 + h
    poly = [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]
    closing = uv_region(fr, rect_px, s0, z0)
    if not recess:
        cos = [fr.P(s, z) for s, z in poly]
        B.face(cos, [closing(c) for c in cos])
        return poly
    band = uv_wall(fr, wall)
    for k, ((a0, b0), (a1, b1)) in enumerate(zip(poly, poly[1:] + poly[:1])):
        cos = [fr.P(a0, b0), fr.P(a1, b1), fr.P(a1, b1, -recess), fr.P(a0, b0, -recess)]
        if k == 0:
            fn = uv_patch("conc")              # the sill
        elif k == 2:
            fn = uv_patch("conc")              # the lintel's soffit
        else:
            # a jamb: the brick that would have been as far along the wall,
            # so the coursing turns into the reveal
            sign = -1.0 if k == 1 else 1.0

            def fn(co, sign=sign):
                q = Vector(co) - fr.p0
                s, d = q.dot(fr.t), -q.dot(fr.n)
                return ((L.U_OFF[wall] + s + sign * d) * PPM, L.PL_Y0 + co[2] * PPM)
        B.face(cos, [fn(c) for c in cos])
    cos = [fr.P(s, z, -recess) for s, z in poly]
    B.face(cos, [closing(c) for c in cos])
    return poly


def plinth(B, level, shaft_foot):
    """Walls, coping, the coping's flat top round the shaft, the floor."""
    for wall, (p0, p1) in WALLS.items():
        fr = Frame(p0, p1)
        holes = []
        if wall == "front":
            depth = L.INLET_REVEAL if inlet_mode(level) == "cut" else 0.0
            holes.append(opening(B, fr, wall, L.INLET, L.INLET_R, level, depth))
        if wall == "east":
            holes.append(opening(B, fr, wall, L.HATCH, L.HATCH_R, level, 0.0))
        outline = [(0.0, 0.0), (fr.L, 0.0), (fr.L, L.Z_PLINTH), (0.0, L.Z_PLINTH)]
        fill_planar(B, outline, holes, fr.P, uv_wall(fr, wall))
        # the coping: from the wall head 0.25 in and up, U by projection onto
        # the wall, V on along the slope
        a, b = fr.P(0.0, L.Z_PLINTH), fr.P(fr.L, L.Z_PLINTH)
        c = fr.P(fr.L - L.WASH_IN, L.Z_SHAFT0, -L.WASH_IN)
        d = fr.P(L.WASH_IN, L.Z_SHAFT0, -L.WASH_IN)
        u0 = L.U_OFF[wall] * PPM
        B.face([a, b, c, d],
               [(u0, L.PL_WALL_PX), (u0 + fr.L * PPM, L.PL_WALL_PX),
                (u0 + (fr.L - L.WASH_IN) * PPM, L.PL_TOP_PX),
                (u0 + L.WASH_IN * PPM, L.PL_TOP_PX)])
    # the flat top, holed by the shaft's foot, mapped from above at 16 px/m
    t = L.PH_TOP
    x, y, w, h = L.PLTOP_R

    def top_uv(co):
        return (x + (co[0] + t) * L.PLTOP_PPM, y + (co[1] + t) * L.PLTOP_PPM)
    fill_planar(B, [(-t, -t), (t, -t), (t, t), (-t, t)],
                [[(p[0], p[1]) for p in shaft_foot]],
                lambda a, b: (a, b, L.Z_SHAFT0), top_uv)
    floor = [(-PH, -PH, 0.0), (-PH, PH, 0.0), (PH, PH, 0.0), (PH, -PH, 0.0)]
    B.face(floor, [uv_patch("blank")(c) for c in floor])


# ================================================================== lathe
def ring_points(r, z, n):
    """A ring of *n* vertices at radius r * k(n), the back facet (facet 0)
    centred on +Y and the facets running counter-clockwise from above."""
    rv = r * L.k_sides(n)
    return [(rv * math.cos(a), rv * math.sin(a), z)
            for a in (math.pi / 2 - math.pi / n + 2 * math.pi * j / n for j in range(n))]


def facet_u(r, n, j, right):
    """U of facet *j*'s left (right=False) or right corner at radius *r*:
    chord length at 64 px/m. The back facet takes the strip, centred on
    STRIP_C; the rest run on from STRIP_W, unwrapped, so seen from outside
    the bricks read left to right and true size on every tier."""
    w = 2.0 * r * L.k_sides(n) * math.sin(math.pi / n) * PPM
    if j == 0:
        return L.STRIP_C + (0.5 if right else -0.5) * w
    return L.STRIP_W + (j - 1 + (1 if right else 0)) * w


def band(B, lo, hi, v_lo, v_hi, n, patch=None):
    """One band of *n* facets from ring (z, r) *lo* up (or across, or down)
    to *hi*, V from v_lo to v_hi. The winding faces out for a profile
    walked upward and across the rim, and into the flue down its lining.
    *patch* maps the whole band onto one flat patch instead."""
    (z0, r0), (z1, r1) = lo, hi
    p0, p1 = ring_points(r0, z0, n), ring_points(r1, z1, n)
    for j in range(n):
        k = (j + 1) % n
        cos = [p0[j], p0[k], p1[k], p1[j]]
        uvs = [(facet_u(r0, n, j, False), v_lo), (facet_u(r0, n, j, True), v_lo),
               (facet_u(r1, n, j, True), v_hi), (facet_u(r1, n, j, False), v_hi)]
        if patch:
            uvs = [uv_patch(patch)(c) for c in cos]
        B.face(cos, uvs, smooth=True)


def stack(B, level):
    """The shaft's ten lifts, the head, the rim, the lining and the floor."""
    n = sides(level)
    # the shaft: nine lifts on MID, the top lift on TOPHEAD
    for i in range(L.NSEG):
        z0 = L.Z_SHAFT0 + i * L.SEG
        z1 = z0 + L.SEG
        if i < L.NSEG - 1:
            v0, v1 = L.MID_Y0, L.MID_Y0 + L.MID_H
        else:
            v0, v1 = L.TH_Y0, L.TH_Y0 + L.MID_H
        band(B, (z0, L.r_shaft(z0)), (z1, L.r_shaft(z1)), v0, v1, n)
    prof, rows = head_profile(level)
    for (a, b), (va, vb) in zip(zip(prof, prof[1:]), zip(rows, rows[1:])):
        band(B, a, b, va, vb, n)
    # the flue: lining straight down from the rim's inner edge, then a floor
    zt, zf = L.Z_TOP, L.Z_TOP - L.FLUE_DEPTH
    band(B, (zt, L.R_FLUE), (zf, L.R_FLUE), 0, 0, n, patch="soot")
    floor = ring_points(L.R_FLUE, zf, n)
    B.face(floor, [uv_patch("soot")(c) for c in floor])
    return ring_points(L.r_shaft(L.Z_SHAFT0), L.Z_SHAFT0, n)


# ================================================================ assembly
def build_lod(level):
    B = Builder()
    foot = ring_points(L.r_shaft(L.Z_SHAFT0), L.Z_SHAFT0, sides(level))
    plinth(B, level, foot)
    stack(B, level)
    bm = B.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # smooth round the stack, sharp where its profile turns
    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        fa, fb = e.link_faces
        if not (fa.smooth and fb.smooth):
            continue
        a, b = e.verts
        if abs(a.co.z - b.co.z) < 1e-6 and fa.normal.angle(fb.normal, 0.0) > math.radians(25):
            e.smooth = False
    obj = to_object(B, "{}_LOD{}".format(ASSET, level))
    obj.data.name = obj.name + "_mesh"
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4],
                          quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# ================================================================== checks
def check_layout():
    bad = []
    # the inlet and the hatch inside their walls, the inlet under its lintel
    sc, z0, w, h = L.INLET
    if sc - w / 2 < 0.6 or sc + w / 2 > 2 * PH - 0.6:
        bad.append("the inlet is within 0.6 m of a corner")
    if abs(z0 + h - L.Z_LINTEL[0]) > 1e-6:
        bad.append("the inlet's head is not the lintel's soffit")
    if sc - L.LINTEL_HALF < 0.4 or sc + L.LINTEL_HALF > 2 * PH - 0.4:
        bad.append("the lintel runs into a corner")
    if L.Z_LINTEL[1] > L.Z_PLINTH - 0.2:
        bad.append("the lintel crowds the coping")
    sc, z0, w, h = L.HATCH
    if z0 < L.Z_FOOT + 0.1 or z0 + h > L.INLET[1] + L.INLET[3]:
        bad.append("the hatch is not low in the plinth, above the footing")
    # the shaft's foot inside the coping's top on every tier
    for n in L.SIDES:
        rv = L.r_shaft(L.Z_SHAFT0) * L.k_sides(n)
        if rv > L.PH_TOP - 0.05:
            bad.append("%d sides: the shaft's foot (%.3f) overruns the coping" % (n, rv))
        # the back facet inside its strip, the rest inside its region
        w = 2 * rv * math.sin(math.pi / n) * PPM
        if L.STRIP_C + w / 2 > L.STRIP_W or L.STRIP_C - w / 2 < 0:
            bad.append("%d sides: the back facet (%.1f px) overruns the strip" % (n, w))
        if L.STRIP_W + (n - 1) * w > L.ATLAS:
            bad.append("%d sides: the shaft wraps the atlas" % n)
        rh = max(r for z, r in L.HEAD) * L.k_sides(n)
        wh = 2 * rh * math.sin(math.pi / n) * PPM
        if L.STRIP_W + (n - 1) * wh > L.TH_W:
            bad.append("%d sides: the head overruns TOPHEAD" % n)
        if L.STRIP_C + wh / 2 > L.STRIP_W:
            bad.append("%d sides: the head's back facet overruns the strip" % n)
    # the profile: a closed walk up, across the rim, the flue's floor inside
    # the head band
    zs = [z for z, r in L.HEAD]
    if zs != sorted(zs) or abs(L.HEAD[0][1] - L.R1) > 1e-9 or abs(L.HEAD[0][0] - L.Z_HEAD0) > 1e-9:
        bad.append("the head profile does not start on the shaft's top")
    zf = L.Z_TOP - L.FLUE_DEPTH
    if zf < L.HEAD[5][0] + 0.2:
        bad.append("the flue's floor is below the head band")
    if L.R_FLUE > min(r for z, r in L.HEAD[5:9]) - 0.3:
        bad.append("the rim is under 0.3 m wide")
    return bad


def build_all():
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The plinth is the footprint; nothing stands outside it. A chimney has
    no door (the hatch and the inlet are not doors) and no occupied storey,
    so it lists neither, and the sidecar has no main door."""
    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-PH, -PH), (PH, -PH), (PH, PH), (-PH, PH)],
        "storeys": [],
        "doors": [],
    }


if __name__ == "__main__":
    BUILD.main(build_all, facts)
