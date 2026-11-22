# SPDX-License-Identifier: GPL-3.0-or-later

"""The mesh kit every building's build.py builds its closed solids with.

A build.py describes its building: massing, UV mappings onto its atlas,
layout checks and facts(). The way a face is made, a wall region filled or
an opening lined is the same in every asset, and lives here:

    Builder         a bmesh under construction: vertices shared through a
                    position cache, faces with their UVs set as they are made
    Frame           a wall plane: s along the wall, z up, out from its face
                    (InwardFrame: the third coordinate is depth into the wall)
    fill_planar()   a planar region with holes, triangulated, slivers repaired
    fill_region()   the same on a wall Frame
    recess()        an opening's cheeks and its closing face, set back
    prism(), box()  vertical prisms over a plan ring; circle() for a round one
    rim_loops(), cap(), close_solid()
                    a wall ring's open rims walked and capped, so the ring is a
                    closed solid the exact boolean can take
    uv_patch(), uv_region()
                    the two UV mappings every atlas has: a flat patch, and a
                    region laid on a wall at its own texel density
    render_views()  the six working views CLAUDE.md asks for, and any more

UVs are atlas pixels throughout; the Builder divides by the atlas size.

    import functools
    import shell_build as SB
    Builder = functools.partial(SB.Builder, L.ATLAS)

    def uv_patch(name):
        return SB.uv_patch(L.PATCHES[name])

    def main_body(level):
        B = Builder()
        fr = SB.Frame((-HX, -HY), (HX, -HY))
        SB.fill_region(B, fr, SB.rect_poly((0.0, 2 * HX, 0.0, Z_TOP)),
                       [SB.rect_poly(r) for r in windows], uv_wall(fr))
        for r in windows:
            SB.recess(B, fr, SB.rect_poly(r), 0.0, -DEPTH, uv_glass(fr, r),
                      uv_patch("reveal"))
        ...
        SB.close_solid(B, uv_patch("blank"))
        return B

Every function reproduces, number for number, the copy it replaces in the
assets that had one; where copies differed, the one that is correct in more
cases is kept (the area test in Builder.face, the sliver repair's bound) and
what varied is a parameter. Runs inside Blender only.
"""

import math
import os

import bmesh
import bpy
from mathutils import Euler, Vector, geometry

import asset_build

EPS = 1e-6


# ============================================================ the builder
class Builder:
    """One closed solid under construction, with UVs set as faces are made.

    Vertices are shared through a position cache, so faces that meet along
    an edge meet on the same vertices. That only works if every vertex lying
    on an edge is a corner of both faces, which is why region outlines carry
    their neighbours' breakpoints explicitly.

    *atlas* is the atlas size in pixels; UVs are given in atlas pixels.
    *digits* is the cache's rounding (4: 0.1 mm). With *snap* a vertex is
    made at its rounded position rather than at the first position that
    reached it. *uv_point*, when given, makes a UV function see
    uv_point(co) of each corner as passed to face() (e.g. mathutils.Vector)
    rather than the cached vertex's stored position.
    """

    def __init__(self, atlas, digits=4, snap=False, uv_point=None):
        self.atlas = atlas
        self.digits = digits
        self.snap = snap
        self.uv_point = uv_point
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cache = {}

    def key(self, co):
        d = self.digits
        return (round(co[0], d) + 0.0, round(co[1], d) + 0.0, round(co[2], d) + 0.0)

    def v(self, co):
        key = self.key(co)
        vert = self.cache.get(key)
        if vert is None:
            vert = self.bm.verts.new(key if self.snap else co)
            self.cache[key] = vert
        return vert

    def face(self, cos, uvs, smooth=False):
        """A face through *cos*, or None when it has no area or exists.

        *uvs* is a function of a vertex position returning atlas pixels
        (u, v), or a list of them, one per corner. Repeated consecutive
        corners are dropped. The area test is Newell's, on coordinates
        relative to the first vertex, in double precision: summed from
        absolute positions in mathutils' 32-bit floats, a zero-area face keeps
        enough rounding to pass as real and lands a third face on its edges.
        """
        fn = None
        if callable(uvs):
            fn, uvs = uvs, None
            if self.uv_point is not None:
                uvs = [fn(self.uv_point(co)) for co in cos]
        verts, keep = [], []
        for i, co in enumerate(cos):
            vv = self.v(co)
            if not verts or verts[-1] is not vv:
                verts.append(vv)
                if uvs is not None:
                    keep.append(uvs[i])
        if len(verts) > 2 and verts[0] is verts[-1]:
            verts.pop()
            if uvs is not None:
                keep.pop()
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
        if uvs is None:
            self.set_uv(f, fn)
        else:
            for loop, (u, w) in zip(f.loops, keep):
                loop[self.uv].uv = (u / self.atlas, w / self.atlas)
        if smooth:
            f.smooth = True
        return f

    def set_uv(self, f, uvfn):
        """UVs for an existing face, *uvfn* called at each vertex's position."""
        for loop in f.loops:
            u, w = uvfn(loop.vert.co)
            loop[self.uv].uv = (u / self.atlas, w / self.atlas)


class Frame:
    """A wall plane: s runs along the wall from p0, z is world height, and out
    runs away from the wall on the side the outward normal points (on the
    right of p0 -> p1: walls are walked counter-clockwise seen from above)."""

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

    def xy(self, s):
        q = self.p0 + self.t * s
        return q.x, q.y


class InwardFrame(Frame):
    """A Frame whose third coordinate is depth into the wall, away from the
    outward normal: P(s, z, d) is Frame's P(s, z, -d)."""

    def P(self, s, z, depth=0.0):
        q = self.p0 + self.t * s - self.n * depth
        return (q.x, q.y, z)


# ============================================================ small helpers
def rect_poly(r):
    """(s0, s1, z0, z1) as its four corners, counter-clockwise from (s0, z0)."""
    s0, s1, z0, z1 = r
    return [(s0, z0), (s1, z0), (s1, z1), (s0, z1)]


def edges(poly):
    """The closed polygon's edges, (poly[k], poly[k + 1])."""
    return list(zip(poly, poly[1:] + poly[:1]))


def circle(cx, cy, r, n, phase=0.5):
    """n points round (cx, cy) at radius r, counter-clockwise, the first at
    angle phase * 2 pi / n (0.5: a flat side faces each axis when n % 4 == 0)."""
    return [(cx + r * math.cos(a), cy + r * math.sin(a))
            for a in [(i + phase) * 2.0 * math.pi / n for i in range(n)]]


def dedupe(pts, eps=EPS):
    """*pts* without consecutive repeats, the closing repeat included."""
    out = []
    for p in pts:
        if not out or abs(out[-1][0] - p[0]) > eps or abs(out[-1][1] - p[1]) > eps:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < eps \
            and abs(out[0][1] - out[-1][1]) < eps:
        out.pop()
    return out


def overlap(a, b, gap=0.0):
    """Whether rectangles (s0, s1, z0, z1) come within *gap* of each other."""
    return a[0] < b[1] + gap and b[0] < a[1] + gap and a[2] < b[3] + gap and b[2] < a[3] + gap


def item_rects(spec, s, z):
    """An opening and its casing: *spec* is (width, height, casing at the
    sides, below and above); the opening stands at sill z, centred on s.
    Returns (outer, inner) rectangles, each (s0, s1, z0, z1)."""
    w, h, cs, cb, ct = spec
    outer = (s - w / 2 - cs, s + w / 2 + cs, z - cb, z + h + ct)
    inner = (s - w / 2, s + w / 2, z, z + h)
    return outer, inner


# ============================================================ UV mappings
def patch_centre(rect):
    x, y, w, h = rect
    return (x + w / 2.0, y + h / 2.0)


def uv_patch(rect):
    """Every corner at the middle of an atlas patch (x, y, w, h): a flat
    colour, for faces that are buried or too small for artwork."""
    c = patch_centre(rect)
    return lambda co: c


def uv_region(fr, rect, s0, z0, ppm, flip=False):
    """A region (x, y, w, h) laid on wall frame *fr* at *ppm* texels a metre,
    its lower-left corner at (s0, z0); *flip* runs U back from its right edge."""
    x, y, w, h = rect

    def f(co):
        u = (fr.s_of(co) - s0) * ppm
        return (x + (w - u if flip else u), y + (co.z - z0) * ppm)
    return f


# ============================================================ regions
def flip_slivers(pts, tris):
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


def fill_planar(B, loops, to3d, uvfn):
    """Triangulate a planar region, an outline and any holes in 2D, and add
    it, each 2D point placed by *to3d*."""
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((a, b, 0.0)) for a, b in loop] for loop in loops])
    for i, j, k in flip_slivers(flat, tris):
        B.face([to3d(*flat[i]), to3d(*flat[j]), to3d(*flat[k])], uvfn)


def fill_region(B, fr, outline, holes, uvfn, out=0.0, quad=False):
    """Triangulate a wall region, an (s, z) outline with polygonal holes, and
    add it on frame *fr* at *out* (passed on as fr.P's third coordinate).
    With *quad* a hole-free four-point outline goes in as one quad instead."""
    if quad and not holes and len(outline) == 4:
        B.face([fr.P(s, z, out) for s, z in outline], uvfn)
        return
    fill_planar(B, [outline] + list(holes), lambda s, z: fr.P(s, z, out), uvfn)


def recess(B, fr, poly, near, far, back, cheeks, skip_z=None):
    """Line an opening and close it set back.

    *poly* is the opening's (s, z) outline, counter-clockwise seen from
    outside; *near* and *far* are fr.P's third coordinate at the wall face
    and at the closing face (on a Frame, far = near - depth). *cheeks* is one
    UV function for every side, or a list with one per edge (edge k runs
    poly[k] -> poly[k + 1]); *back* maps the closing face, or is None to leave
    it to the caller. An edge lying along z = *skip_z* gets no cheek: an
    opening that stands on the ground has no sill of its own, since that
    strip would lie on the floor the wall ring is capped with.
    """
    n = len(poly)
    fns = cheeks if isinstance(cheeks, (list, tuple)) else [cheeks] * n
    for k in range(n):
        (s0, z0), (s1, z1) = poly[k], poly[(k + 1) % n]
        if skip_z is not None and abs(z0 - skip_z) < EPS and abs(z1 - skip_z) < EPS:
            continue
        B.face([fr.P(s0, z0, near), fr.P(s1, z1, near),
                fr.P(s1, z1, far), fr.P(s0, z0, far)], fns[k])
    if back is not None:
        B.face([fr.P(s, z, far) for s, z in poly], back)


# ============================================================ solids
def prism(B, ring, z0, z1, sides, top, bottom):
    """A vertical prism over the plan *ring* (counter-clockwise, convex or
    not), from z0 to z1, added to *B* and returned: the sides first, edge by
    edge, then the top and the bottom. *sides* is one UV function or a list
    with one per edge."""
    n = len(ring)
    fns = sides if isinstance(sides, (list, tuple)) else [sides] * n
    for k in range(n):
        (ax, ay), (bx, by) = ring[k], ring[(k + 1) % n]
        B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], fns[k])
    B.face([(x, y, z1) for x, y in ring], top)
    B.face([(x, y, z0) for x, y in reversed(ring)], bottom)
    return B


def box(B, x0, x1, y0, y1, z0, z1, sides, top, bottom):
    """An axis-aligned box as a prism(): *sides* is one UV function or four,
    facing -Y, +X, +Y, -X in that order."""
    return prism(B, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, sides, top, bottom)


# ============================================================ closing a ring
def rim_loops(B, count=None):
    """The open rims of *B*: every loop of edges with one face, as vertex
    lists, walked in edge-index order so the caps start on the same vertex
    every run (a set of BMEdges iterates by memory address, and the boolean
    would triangulate differently each time). Raises on a rim that branches
    or, given *count*, on another number of rims: either is a T-junction."""
    bm = B.bm
    bm.edges.index_update()
    order = [e for e in bm.edges if len(e.link_faces) == 1]
    rim = set(order)
    branch = [v for e in order for v in e.verts
              if sum(1 for x in v.link_edges if x in rim) != 2]
    if branch:
        c = branch[0].co
        raise ValueError("an open rim branches at %d vertices, e.g. "
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
    if count is not None and len(loops) != count:
        raise ValueError("expected %d open rims, got %d: a T-junction somewhere"
                         % (count, len(loops)))
    return loops


def cap(B, loop, uvfn, split=None, triangulate=False, repair=True):
    """Close one rim *loop* (from rim_loops()) with a face mapped by *uvfn*.

    *split*, two vertices of the loop, caps it with two faces meeting
    between them instead (a lid that follows a gable is not planar, but each
    half lies in one roof plane). *triangulate* caps it with triangles in
    plan, for a horizontal rim that is not convex, their slivers repaired
    (flip_slivers()); repair=False keeps the triangulator's output as it is,
    zero-area triangles and all, which only reproduces an asset built that
    way. The rim is capped by hand rather than with bmesh's holes_fill,
    which silently skips a loop whose vertices already carry a face.
    """
    bm = B.bm
    if triangulate:
        pts = [(v.co.x, v.co.y) for v in loop]
        tris = geometry.tessellate_polygon([[Vector((x, y, 0.0)) for x, y in pts]])
        for a, b, c in (flip_slivers(pts, tris) if repair else tris):
            B.set_uv(bm.faces.new((loop[a], loop[b], loop[c])), uvfn)
        return
    if split is None:
        B.set_uv(bm.faces.new(loop), uvfn)
        return
    i, j = sorted(loop.index(v) for v in split)
    for half in (loop[i:j + 1], loop[j:] + loop[:i + 1]):
        B.set_uv(bm.faces.new(half), uvfn)


def close_solid(B, uvfn, count=2, ridges=()):
    """Cap a wall ring: one n-gon per open rim (normally a floor on the
    ground and a lid buried in the roof), then each lid split along the
    (point, point) pairs in *ridges* (a gable's ridge). Both caps end up
    buried, but the solid must be closed for the boolean to be exact."""
    for loop in rim_loops(B, count):
        cap(B, loop, uvfn)
    for a, b in ridges:
        bmesh.ops.connect_verts(B.bm, verts=[B.cache[B.key(a)], B.cache[B.key(b)]])


# ============================================================ working views
SQRT2 = math.sqrt(2.0)


def orbit(name, direction, k=3.0, target=None, lens=35.0, z=None, aim_z=None):
    """A perspective view for render_views(): *k* bounding radii from *target*
    (a build-frame point; None, the tier's centre) along *direction*, looking
    at it. *z* puts the camera at that height and *aim_z* the aim, for an eye
    level view."""
    def place(centre, radius, pivot):
        t = centre.copy() if target is None else Vector(target) - pivot
        loc = t + Vector(direction).normalized() * radius * k
        if z is not None:
            loc.z = z
        if aim_z is not None:
            t.z = aim_z
        return loc, t, lens
    return name, place


def look(name, loc, aim, lens=35.0):
    """A perspective view for render_views() from build-frame point *loc*
    toward *aim*."""
    def place(centre, radius, pivot):
        return Vector(loc) - pivot, Vector(aim) - pivot, lens
    return name, place


AERIAL = orbit("aerial", (1.0, -1.0, SQRT2))           # off the front-right corner
AERIAL_REAR = orbit("aerial_rear", (-1.0, 1.0, SQRT2))


def figure(A, at, name="_figure"):
    """A 1.8 m standing figure, body and head, on the ground at build-frame
    point *at*, for scale in the working views; never part of a tier."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for (w, d), (z0, z1) in (((0.44, 0.26), (0.0, 1.55)), ((0.20, 0.20), (1.58, 1.80))):
        geom = bmesh.ops.create_cube(bm, size=1.0)
        for v in geom["verts"]:
            v.co.x *= w
            v.co.y *= d
            v.co.z = z0 + (v.co.z + 0.5) * (z1 - z0)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = Vector((at[0], at[1], 0.0)) - Vector(A.pivot or (0.0, 0.0, 0.0))
    mat = bpy.data.materials.get("_figure") or bpy.data.materials.new("_figure")
    if mat.node_tree is None:           # use_nodes is deprecated in 5.x, gone in 6.0
        mat.use_nodes = True
    dark = (0.25, 0.22, 0.20, 1.0)
    mat.diffuse_color = dark
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs["Base Color"].default_value = dark
    me.materials.append(mat)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def render_views(A, out_dir, level=0, res=(1400, 1000), distance=80.0,
                 views=(AERIAL,), figures=()):
    """The six working views CLAUDE.md asks for before export, for asset_build
    Asset *A*'s tier *level*: four orthographic elevations and a plan from
    above, *distance* metres out, then the perspective *views* (orbit() or
    look(); by default the raised three-quarter aerial off the front corner).
    *figures* are build-frame ground points where a 1.8 m figure stands
    while they render. Working views only, into the git-ignored review/
    folder; returns the files written."""
    os.makedirs(out_dir, exist_ok=True)
    A.preview_studio()
    A.show_only(level)
    scn = bpy.context.scene
    saved = (scn.camera, scn.render.resolution_x, scn.render.resolution_y)
    scn.render.resolution_x, scn.render.resolution_y = res
    centre, radius = asset_build.bounds(A.lod(level))
    pivot = Vector(A.pivot) if A.pivot else Vector()
    cam = bpy.data.objects.get("_view_cam")
    if cam is None:
        cam = bpy.data.objects.new("_view_cam", bpy.data.cameras.new("_view_cam"))
        scn.collection.objects.link(cam)
    scn.camera = cam
    cam.data.clip_end = 1000.0
    figs = [figure(A, at, "_figure%d" % i) for i, at in enumerate(figures)]
    ortho = {
        "front": ((0, -1, 0), (90, 0, 0)), "rear": ((0, 1, 0), (90, 0, 180)),
        "east": ((1, 0, 0), (90, 0, 90)), "west": ((-1, 0, 0), (90, 0, -90)),
        "top": ((0, 0, 1), (0, 0, 0)),
    }
    written = []
    try:
        for name, (d, rot) in ortho.items():
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = radius * 2.1
            cam.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
            cam.location = centre + Vector(d) * distance
            scn.render.filepath = os.path.join(out_dir, "L%d_%s.png" % (level, name))
            bpy.ops.render.render(write_still=True)
            written.append(scn.render.filepath)
        for name, place in views:
            loc, aim, lens = place(centre, radius, pivot)
            cam.data.type = 'PERSP'
            cam.data.lens = lens
            cam.location = loc
            cam.rotation_euler = (aim - loc).to_track_quat('-Z', 'Y').to_euler()
            scn.render.filepath = os.path.join(out_dir, "L%d_%s.png" % (level, name))
            bpy.ops.render.render(write_still=True)
            written.append(scn.render.filepath)
    finally:
        for o in figs:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.meshes.remove(me)
        scn.camera, scn.render.resolution_x, scn.render.resolution_y = saved
    return written
