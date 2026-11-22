# SPDX-License-Identifier: GPL-3.0-or-later

"""Roof safety equipment: the wall ladder, its safety cage, the roof ladder
and the walkway that take a sweep or a fitter from the ground to whatever on
a roof is serviced from it, as closed solids for a build.py to union into
its tier.

    import roof_safety as RS
    PAINT = RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)
    EAVE = RS.Eave(p0, p1, z_wall, eave_out, z_edge, tan)
    WALL = RS.WallLadder(EAVE, s)
    ROOF = RS.RoofLadder(EAVE, s, z_top)
    WALK = RS.Walkway(EAVE, s0, s1, ROOF.top_out())
    for B, name in RS.solids([WALL, ROOF, WALK], level, PAINT):
        parts.append(to_object(B, name))
    bad += RS.problems(WALL, "the wall ladder", [("door", s0, s1)])

A wall ladder longer than CAGE_LADDER (8 m) carries a safety cage. Give it
the ladder and list it after it; problems() checks its place as wide as its
hoops, against the same spans:

    CAGE = RS.Cage(WALL)            # hoops from 2.5 m over the foot to the top
    for B, name in RS.solids([WALL, CAGE, ROOF, WALK], level, PAINT):
        parts.append(to_object(B, name))
    bad += RS.problems(CAGE, "the ladder's cage", [("door", s0, s1)])

and where the ladder sets the building's extents, on the tier that drops
the kit (after the weld, as below):

    RS.append(obj, RS.solids([WALL, CAGE], level, PAINT, extents=True))

The lean kit. WallLadder(..., lean=True), and the Cage given that ladder,
build the same rails, rungs, brackets, hoops and straps, in the same places
and with the same UVs, as separate closed solids that touch nothing:
rungs stop LEAN_GAP (1.5 mm) short of the rails, brackets as short of the
wall and the rails, hoops of the rails and straps of the hoops. Nothing is
cut, so nothing is split: a 22 m caged ladder costs about 1,380 triangles at
LOD0 and 740 at LOD1, against 3,500 and 2,100 unioned. It goes into every
tier through append(), after the build's union, weld and dissolve, never
through the union; check=True raises if any part meets the building or
another part (clashes()). Brackets stop short of the eave wall's face; where
something stands proud of it behind the ladder, *behind* says how far:

    WALL = RS.WallLadder(EAVE, s, lean=True,
                         behind=lambda z: 0.25 if z < 3.7 else 0.0)  # a plinth
    CAGE = RS.Cage(WALL)                                    # lean with it
    KIT = [WALL, CAGE]
    ...
    obj = union(base, parts)            # the kit is not in parts
    ...weld, dissolve...
    RS.append(obj, RS.solids(KIT, level, PAINT, extents=True), check=True)

extents=True there gives the full kit on tiers that keep it and the bare
rails and back strap on the tier that drops it, so one call serves every
tier. A lean ladder's rungs are three-sided prisms (8 triangles) to LOD1
and tetrahedra (4) from LOD2, its brackets prisms at LOD0 and tetrahedra
from LOD1 (LEAN_FORMS; solids(forms=...) replaces it); hoops and straps are
three-sided throughout. Only the wall ladder and its cage have a
lean form; the roof ladder and walkway stand on the sheet and still go
through the union.

The eave is given by its wall's plan end points p0 -> p1, walked
anticlockwise seen from above so the outward face is on the right, as every
build.py walks its walls and as scripts/downpipes.py takes them. *s* runs
along that wall from p0 and *out* away from its face, negative inside it.
*z_wall* is where the soffit meets the wall face, *eave_out* the overhang to
the fascia's outer face, *z_edge* the roof's top surface at that edge, and
*tan* the slope's rise per metre inward (0 for a level deck).

Where a building's eave walls have no run clear of openings from the ground
to the eave -- a terrace's bays, one after another -- the wall ladder stands
on a blank gable and passes outside the rake instead: give WallLadder an Eave
on the gable wall whose *z_wall* is the rake's soffit at the ladder's lower
side, *eave_out* the rake overhang, *z_edge* the roof's top over the ladder,
and *tan* 0, and put the roof ladder on the eave beside it, just inside the
rake.

Why modelled. Finnish building rules want a fixed route from the ground to
anything on a roof steeper than 1:8 that is serviced from it -- chimneys,
ventilation housings, plant -- and the kit is part of how a Finnish roof
reads. Its parts are 3-6 cm, far under the 0.25 m relief threshold, but they
are placement-specific, so no tiling band can paint them, and they are seen
by their outline standing over the eave and the rungs' shadows on the sheet.

Shape.
  * The wall ladder stands on the ground, off the wall on brackets, passes
    EAVE_CLEAR outside the fascia and runs LADDER_TOP above the roof edge,
    the handhold for stepping onto the roof ladder.
  * Its cage, on a ladder over CAGE_LADDER: flat-bar hoops from CAGE_FOOT
    over the ladder's foot to CAGE_TOP_GAP under its top, at most
    CAGE_PITCH apart, each running from inside one rail out to a half
    circle CAGE_R round an axis CAGE_OUT beyond the rails' backs and into
    the other rail; three straps on the hoops' outsides, at the back and
    either side of it. Hoops and straps are closed solids of their own,
    overlapping the rails and each other, so the build's union joins them.
  * The roof ladder starts ROOF_START up the slope from the edge, straight
    above the wall ladder, and stands ROOF_STANDOFF off the sheet on
    brackets that run down into the roof slab, so it cuts only a few small
    squares in the sheet rather than two lines along it.
  * The walkway is a level plank WALK_W wide along the slope, parallel to the
    eave, its upslope edge WALK_GAP clear of the sheet, on posts running down
    into the slab. It starts at the roof ladder's top and runs to the
    serviced item.
Every ladder is one closed solid built without a boolean: each rung's faces
meet the square holes it leaves in the rails' inner faces. A row of holes
the triangulator leaves slivers in is filled with quads and fans instead,
which keep the rail's own edges whole. The walkway's plank and posts overlap
one another and the roof, so the build's union joins them.

UVs. The kit takes the gutter's colour, as a matched rainwater and roof
safety system does: every face maps along its length onto the middle rows of
the painted gutter the atlas names PIPE_STRIP (Paint(strip=...)), the same
rows the downpipes use, so the parts carry the gutter's colour in every
variant and its hangers, a metre apart, read as joints. An atlas without a
gutter passes a fixed patch instead (Paint(patch=...)).

Tiers. MODES gives each tier's rung thinning: every rung up close, every
other one to 70 m, every fourth to 120 m, where the rungs' rhythm still
reads, and past that no kit, whose rails are then under half a pixel. The
brackets and posts go at LOD2. A building that cannot afford that passes its
own modes to solids(). A wall ladder standing outside the eave or the rake
can be the building's widest point, and every tier shares LOD0's bounds and
pivot, so solids(extents=True) keeps its bare rails, three-sided, on a tier
that drops the kit; they touch nothing, and go into the tier through
append(), after the build's weld and dissolve. A cage thins by CAGE_MODES
(its own *modes*): every hoop, every other one, every sixth with the top
one always, and on the tier that drops the kit, with extents, its back
strap alone, three-sided, which stands furthest out of all.

Runs inside Blender only.
"""

import math

import bmesh
import bpy
from mathutils import Vector, geometry

LADDER_W = 0.45             # rail centre to rail centre
RAIL_W, RAIL_D = 0.05, 0.06
RUNG = 0.03
RUNG_PITCH = 0.28
BRACKET = 0.04
BRACKET_BURY = 0.06         # how far a bracket runs into the wall or slab
LADDER_TOP = 1.0            # the wall ladder runs on this far above the edge
EAVE_CLEAR = 0.12           # the wall ladder's rails pass this far outside it
WALL_BRACKET_PITCH = 1.6    # the wall ladder's brackets, from 0.6 m up
SOFFIT_CLEAR = 0.25         # the top bracket stays this far under the soffit
ROOF_START = 0.25           # the roof ladder's foot, up the slope from the edge
ROOF_STANDOFF = 0.08        # its rails' undersides off the sheet
ROOF_BRACKET_PITCH = 1.2    # its brackets, along the slope
WALK_W = 0.30               # the walkway plank, across the slope
WALK_T = 0.05               # its thickness
WALK_GAP = 0.05             # its underside above the sheet at its upslope edge
POST = 0.04                 # the walkway's posts, square
POST_PITCH = 1.2            # the most between two of them
SLAB_BURY = 0.10            # how far a post runs into the roof below the sheet
HALF = LADDER_W / 2.0 + RAIL_W / 2.0    # a ladder's half-width to its rails' outsides
CORNER = 0.30               # the least from a wall's end to the ladder's outside
CLEAR = 0.20                # the least from its outside to an opening or a pipe

# (rungs, fittings) per tier, LOD0 to LOD3: every rung, every other one,
# every fourth, then no kit at all; and whether the tier keeps the brackets
# and the walkway's posts. A building that cannot afford that passes its own
# modes to solids().
MODES = ((1, True), (2, True), (4, False), (None, False))

# The safety cage round a tall wall ladder's climber (Cage): flat-bar hoops
# fixed into the rails, flaring out and round the climber's back, and
# vertical straps on the hoops' outsides. Across (a) and out (o) are the
# ladder's own: a along the wall from its axis, o out from the wall face.
CAGE_LADDER = 8.0           # a wall ladder longer than this carries a cage
CAGE_FOOT = 2.50            # the lowest hoop, over the ladder's foot
CAGE_TOP_GAP = 0.15         # the top hoop, under the ladder's top, by default
CAGE_PITCH = 1.65           # the most between two hoops
CAGE_OUT = 0.28             # the hoops' arc centre, out beyond the rails' backs
CAGE_R = 0.36               # the arc's radius
CAGE_ARC = 4                # chords round the half circle
HOOP_T, HOOP_H = 0.016, 0.05        # flat bar: thickness, height
STRAP_T, STRAP_W = 0.020, 0.05
STRAP_ANGLES = (135.0, 90.0, 45.0)  # round the arc, 90 at the back
STRAP_END = 0.04            # past the first and last hoops
# Per tier, LOD0 to LOD3: every hoop, every other one, every sixth (the top
# one always), then the back strap alone, three-sided, which holds the
# cage's outward extent on the tier that drops the kit (solids(extents=True)).
CAGE_MODES = (1, 2, 6, None)


def brackets_kept(level):
    """Brackets and posts are 4 cm bars, under a pixel past 70 m, and each
    costs about twenty triangles -- its box, its hole in the rail and its cut
    in what it runs into."""
    return MODES[level][1]


# ================================================================= mesh
class Paint:
    """Where the kit's faces sample the atlas: along a strip, or at a point."""

    def __init__(self, atlas, strip=None, patch=None, ppm=64.0):
        if (strip is None) == (patch is None):
            raise ValueError("give a strip or a patch")
        self.atlas, self.strip, self.patch, self.ppm = atlas, strip, patch, ppm


class Mesh:
    """One closed solid under construction, vertices shared through a
    position cache so faces meeting along an edge meet on its vertices."""

    def __init__(self, paint):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cache = {}
        self.paint = paint

    def v(self, co):
        key = (round(co[0], 4), round(co[1], 4), round(co[2], 4))
        vert = self.cache.get(key)
        if vert is None:
            vert = self.bm.verts.new(co)
            self.cache[key] = vert
        return vert

    def face(self, cos, along, frame=None):
        """A face through *cos*, mapped with its length along *along*. Faces
        of one planar region pass one *frame* (origin, side, half) so their
        mapping agrees across their shared edges."""
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
        pts = [v.co - o for v in verts]
        nrm = Vector((0.0, 0.0, 0.0))
        for a, b in zip(pts, pts[1:] + pts[:1]):
            nrm += a.cross(b)
        if nrm.length_squared < 1e-18:
            return None
        try:
            f = self.bm.faces.new(verts)
        except ValueError:
            return None
        self._uv(f, nrm.normalized(), Vector(along), frame)
        return f

    def _uv(self, f, nrm, along, frame):
        p = self.paint
        if p.patch is not None:
            for loop in f.loops:
                loop[self.uv].uv = (p.patch[0] / p.atlas, p.patch[1] / p.atlas)
            return
        a = along - nrm * along.dot(nrm)
        if a.length < 0.3:
            # the face lies across the hint: map it along its longest edge
            es = [(l.link_loop_next.vert.co - l.vert.co) for l in f.loops]
            a = max(es, key=lambda e: e.length)
        a.normalize()
        side = nrm.cross(a)
        if frame is None:
            cos = [l.vert.co for l in f.loops]
            origin = sum(cos, Vector()) / len(cos)
            half = max(abs((c - origin).dot(side)) for c in cos)
        else:
            origin, half = Vector(frame[0]), frame[1]
        v0, v1 = p.strip
        vm, hv = (v0 + v1) / 2.0, (v1 - v0) / 2.0
        k = min(1.0, hv / (half * p.ppm)) if half > 1e-9 else 0.0
        for loop in f.loops:
            d = loop.vert.co - origin
            loop[self.uv].uv = ((512.0 + d.dot(a) * p.ppm) / p.atlas,
                                (vm + d.dot(side) * p.ppm * k) / p.atlas)


def _outward(M, faces):
    """Turn *faces*, one closed solid just added to *M*, outward if they
    enclose a negative volume. A solid laid out in a fixed order on the
    caller's axes comes out inside out wherever those axes are left-handed,
    as an eave's (along, out, up) are, or where its section is mirrored, as
    a ladder's two rails are. Reversing keeps every vertex, loop start and
    UV, so the solid is the one a later recalc_face_normals() would have
    made: the union's operands, recalculated by to_object(), are unchanged,
    and what append() takes needs no recalculating."""
    faces = [f for f in faces if f is not None]
    if not faces:
        return M
    o = faces[0].verts[0].co.copy()
    vol = 0.0
    for f in faces:
        cos = [l.vert.co - o for l in f.loops]
        for b, c in zip(cos[1:], cos[2:]):
            vol += cos[0].dot(b.cross(c))
    if vol < 0.0:
        bmesh.ops.reverse_faces(M.bm, faces=faces)
    return M


def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge: rung holes
    share their depth, so the triangulator may join three collinear corners."""
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


def _fill_planar(M, loops, to3d, along, frame):
    """A rail face -- a rectangle and the square holes in it -- as triangles,
    or, where the triangulator's slivers cannot be flipped away, as quads."""
    flat = [p for loop in loops for p in loop]
    tris = geometry.tessellate_polygon(
        [[Vector((a, b, 0.0)) for a, b in loop] for loop in loops])
    try:
        tris = _flip_slivers(flat, tris)
    except ValueError:
        _fill_columns(M, loops, to3d, along, frame)
        return
    for i, j, k in tris:
        M.face([to3d(*flat[i]), to3d(*flat[j]), to3d(*flat[k])], along, frame)


def _fill_columns(M, loops, to3d, along, frame):
    """The same face without the triangulator: a rectangle holed by squares
    stacked along its length, all spanning the same range across it, as on
    every rail. A quad below the first hole, one between each two and one
    above the last; either side, a fan from the rectangle's lower corner up
    the holes' side edges. The rectangle's own edges stay whole, so they
    still meet the rail's other faces on their corners alone."""
    xs = [p[0] for p in loops[0]]
    ys = [p[1] for p in loops[0]]
    X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)
    hs = [(min(p[0] for p in h), max(p[0] for p in h),
           min(p[1] for p in h), max(p[1] for p in h)) for h in loops[1:]]
    swap = (X1 - X0) > (Y1 - Y0)            # run along the longer axis
    if swap:
        X0, X1, Y0, Y1 = Y0, Y1, X0, X1
        hs = [(b0, b1, a0, a1) for a0, a1, b0, b1 in hs]
        put = lambda x, y: to3d(y, x)       # noqa: E731
    else:
        put = lambda x, y: to3d(x, y)       # noqa: E731
    hs.sort(key=lambda h: h[2])
    p, q = hs[0][0], hs[0][1]
    if any(abs(h[0] - p) > 1e-9 or abs(h[1] - q) > 1e-9 for h in hs):
        raise ValueError("rail holes must share one range across the rail")

    def F(pts):
        M.face([put(*pt) for pt in pts], along, frame)

    F([(X0, Y0), (X1, Y0), (q, hs[0][2]), (p, hs[0][2])])
    for h, g in zip(hs, hs[1:]):
        F([(p, h[3]), (q, h[3]), (q, g[2]), (p, g[2])])
    F([(p, hs[-1][3]), (q, hs[-1][3]), (X1, Y1), (X0, Y1)])
    left = [pt for h in hs for pt in ((p, h[2]), (p, h[3]))]
    right = [pt for h in hs for pt in ((q, h[2]), (q, h[3]))]
    for c, d in zip(left, left[1:]):
        F([(X0, Y0), d, c])
    F([(X0, Y0), (X0, Y1), left[-1]])
    for c, d in zip(right, right[1:]):
        F([(X1, Y0), c, d])
    F([(X1, Y0), right[-1], (X1, Y1)])


def box(M, origin, ax, ay, az, xr, yr, zr):
    """A box on axes *ax*, *ay*, *az* from *origin*, spanning *xr*, *yr*,
    *zr* along them; each face mapped along its longer side, and wound
    outward whichever way the axes turn (an eave's are left-handed)."""
    o, ax, ay, az = Vector(origin), Vector(ax), Vector(ay), Vector(az)

    def P(i, j, k):
        return tuple(o + ax * xr[i] + ay * yr[j] + az * zr[k])

    ext = [(xr[1] - xr[0], ax), (yr[1] - yr[0], ay), (zr[1] - zr[0], az)]
    longest = max(ext, key=lambda e: e[0])[1]
    faces = []
    for f in ([(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)],
              [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
              [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
              [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)],
              [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],
              [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]):
        faces.append(M.face([P(*c) for c in f], longest))
    return _outward(M, faces)


# =============================================================== ladder
def ladder(foot, up, across, out, length, standoff, brackets, mode, paint,
           bury=0.0, rail_d=RAIL_D):
    """One ladder as a single closed solid, without a boolean.

    Two rails, each a box; every *mode*-th rung runs between them, each rung's
    four faces meeting the square hole it leaves in each rail's inner face,
    and brackets run back from the rails' rear faces BRACKET_BURY into what
    the ladder stands off, the same way. *foot* is the ladder's centre on
    that surface at the bottom; *up*, *across* and *out* its axes; *standoff*
    the gap behind the rails (negative to bed them into a roof, with deeper
    rails so the rungs still clear it); *brackets* the distances up the
    rails they stand at; *mode* None leaves bare rails. The rails start
    *bury* below the foot.
    """
    M = Mesh(paint)
    up, across, out = Vector(up), Vector(across), Vector(out)
    foot = Vector(foot)

    def P(a, b, c):
        q = foot + across * a + up * b + out * c
        return (q.x, q.y, q.z)

    b0, b1 = -bury, length
    if mode is None and not brackets:
        # bare rails, each a three-sided prism in its box: its back face
        # full width and its front edge on the box's front, so the ladder
        # keeps its extents at 16 triangles for the pair. The two sections
        # mirror each other, so one rail's faces wind inward as laid out;
        # _outward() turns that one, keeping its vertices, UVs and order.
        for side in (-1, 1):
            a_out = side * (LADDER_W / 2.0 + RAIL_W / 2.0)
            a_in = side * (LADDER_W / 2.0 - RAIL_W / 2.0)
            am = side * LADDER_W / 2.0
            tri = [(a_out, standoff), (a_in, standoff), (am, standoff + rail_d)]
            faces = [M.face([P(pa, b0, pc), P(qa, b0, qc), P(qa, b1, qc), P(pa, b1, pc)], up)
                     for (pa, pc), (qa, qc) in zip(tri, tri[1:] + tri[:1])]
            faces.append(M.face([P(a, b0, c) for a, c in reversed(tri)], up))
            faces.append(M.face([P(a, b1, c) for a, c in tri], up))
            _outward(M, faces)
        return M
    c0, c1 = standoff, standoff + rail_d
    cm = (c0 + c1) / 2.0
    half = LADDER_W / 2.0
    n = int((length - 0.25) / RUNG_PITCH)
    rungs = [RUNG_PITCH * (k + 1) for k in range(n) if mode and k % mode == 0]
    r2 = RUNG / 2.0
    k2 = BRACKET / 2.0
    for side in (-1, 1):
        a_out = side * (half + RAIL_W / 2.0)
        a_in = side * (half - RAIL_W / 2.0)
        am = side * half
        # outer face, front face, top and bottom: plain quads
        M.face([P(a_out, b0, c0), P(a_out, b1, c0), P(a_out, b1, c1),
                P(a_out, b0, c1)], up)
        M.face([P(a_out, b0, c1), P(a_out, b1, c1), P(a_in, b1, c1),
                P(a_in, b0, c1)], up)
        M.face([P(a_out, b1, c0), P(a_in, b1, c0), P(a_in, b1, c1),
                P(a_out, b1, c1)], up)
        M.face([P(a_out, b0, c0), P(a_out, b0, c1), P(a_in, b0, c1),
                P(a_in, b0, c0)], up)
        # inner face (b, c), holed for every rung
        holes = [[(b - r2, cm - r2), (b + r2, cm - r2), (b + r2, cm + r2),
                  (b - r2, cm + r2)] for b in rungs]
        _fill_planar(M, [[(b0, c0), (b1, c0), (b1, c1), (b0, c1)]] + holes,
                     lambda b, c, a=a_in: P(a, b, c), up,
                     (P(a_in, 0.0, cm), rail_d / 2.0))
        # rear face (a, b), holed for every bracket
        holes = [[(am - k2, bb - k2), (am + k2, bb - k2), (am + k2, bb + k2),
                  (am - k2, bb + k2)] for bb in brackets]
        _fill_planar(M, [[(a_out, b0), (a_in, b0), (a_in, b1), (a_out, b1)]] + holes,
                     lambda a, b: P(a, b, c0), up, (P(am, 0.0, c0), RAIL_W / 2.0))
        for bb in brackets:
            sq = [(am - k2, bb - k2), (am + k2, bb - k2), (am + k2, bb + k2),
                  (am - k2, bb + k2)]
            for (pa, pb), (qa, qb) in zip(sq, sq[1:] + sq[:1]):
                M.face([P(pa, pb, c0), P(qa, qb, c0), P(qa, qb, -BRACKET_BURY),
                        P(pa, pb, -BRACKET_BURY)], out)
            M.face([P(a, b, -BRACKET_BURY) for a, b in sq], out)
    for b in rungs:
        sq = [(b - r2, cm - r2), (b + r2, cm - r2), (b + r2, cm + r2),
              (b - r2, cm + r2)]
        lo, hi = -(half - RAIL_W / 2.0), half - RAIL_W / 2.0
        for (pb, pc), (qb, qc) in zip(sq, sq[1:] + sq[:1]):
            M.face([P(lo, pb, pc), P(lo, qb, qc), P(hi, qb, qc), P(hi, pb, pc)],
                   across)
    return M


# ============================================================= lean kit
# The lean kit (WallLadder(lean=True) and its Cage): every part a closed
# solid of its own that cuts nothing, LEAN_GAP clear of its neighbours and of
# the wall, so no part is split by another and nothing goes through the
# boolean. Per tier, LOD0 to LOD3, the form of its (rungs, brackets):
# "prism", three-sided with full faces up and out, or down (8 triangles), or
# "tetra", a tetrahedron on two skew diagonals of the same box (4), whose
# outline along each of the box's three axes is the box's own. Tetrahedral
# rungs read fainter than prisms at 35-70 m (reviewed on the headframe), so
# they wait for LOD2; brackets, seen by their shadows, go at LOD1.
LEAN_GAP = 0.0015
LEAN_FORMS = (("prism", "prism"), ("prism", "tetra"), ("tetra", "tetra"),
              ("tetra", "tetra"))


def _finish(M):
    """Outward normals on every shell of *M*: lean parts reach their tier
    through append(), which recalculates nothing."""
    bmesh.ops.recalc_face_normals(M.bm, faces=M.bm.faces[:])
    return M


def bar(M, Q, t0, t1, u0, u1, v0, v1, form, along):
    """A bar from *t0* to *t1* in the box *u0*..*u1*, *v0*..*v1* of the frame
    Q(t, u, v) -> point, added to *M*: a "prism", three-sided, with full
    faces on v1 and on u1 and its third face across the box's diagonal, so
    seen from beyond that corner -- or lit from there -- its outline is the
    box's (swap a pair of bounds to turn it); a "tetra" on the box's
    diagonals; or a "box"."""
    if form == "tetra":
        p, q, r, s = Q(t0, u0, v1), Q(t0, u1, v0), Q(t1, u0, v0), Q(t1, u1, v1)
        for f in ((p, q, r), (q, p, s), (r, s, p), (s, r, q)):
            M.face(list(f), along)
        return M
    if form == "prism":
        sec = [(u0, v1), (u1, v1), (u1, v0)]
    elif form == "box":
        sec = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    else:
        raise ValueError("a lean bar is a 'prism', a 'tetra' or a 'box', not %r" % form)
    return _prism(M, [Q(t0, u, v) for u, v in sec], [Q(t1, u, v) for u, v in sec], along)


def lean_ladder(foot, up, across, out, length, standoff, brackets, mode, paint,
                form=("prism", "prism"), backs=None, rail_d=RAIL_D):
    """ladder()'s lean twin: the same rails, rungs and brackets in the same
    places, as separate closed solids in one mesh. *form* is the (rungs,
    brackets) bar form, or one form for both. Each rail one box mapped as
    ladder() maps it; every *mode*-th rung a bar between the rails' inner
    faces, LEAN_GAP short of each; each bracket a bar from LEAN_GAP off the
    surface behind it -- *backs*, its distance out
    from the ladder's foot plane at each bracket, 0 by default -- to
    LEAN_GAP short of the rail. Nothing is buried, so nothing is cut."""
    M = Mesh(paint)
    up, across, out = Vector(up), Vector(across), Vector(out)
    foot = Vector(foot)
    rung_form, bracket_form = (form, form) if isinstance(form, str) else form

    def P(a, b, c):
        q = foot + across * a + up * b + out * c
        return (q.x, q.y, q.z)

    g = LEAN_GAP
    b0, b1 = 0.0, length
    c0, c1 = standoff, standoff + rail_d
    cm = (c0 + c1) / 2.0
    half = LADDER_W / 2.0
    r2, k2 = RUNG / 2.0, BRACKET / 2.0
    backs = [0.0] * len(brackets) if backs is None else list(backs)
    for side in (-1, 1):
        a_out = side * (half + RAIL_W / 2.0)
        a_in = side * (half - RAIL_W / 2.0)
        am = side * half
        M.face([P(a_out, b0, c0), P(a_out, b1, c0), P(a_out, b1, c1),
                P(a_out, b0, c1)], up)
        M.face([P(a_out, b0, c1), P(a_out, b1, c1), P(a_in, b1, c1),
                P(a_in, b0, c1)], up)
        M.face([P(a_out, b1, c0), P(a_in, b1, c0), P(a_in, b1, c1),
                P(a_out, b1, c1)], up)
        M.face([P(a_out, b0, c0), P(a_out, b0, c1), P(a_in, b0, c1),
                P(a_in, b0, c0)], up)
        M.face([P(a_in, b0, c0), P(a_in, b0, c1), P(a_in, b1, c1), P(a_in, b1, c0)],
               up, (P(a_in, 0.0, cm), rail_d / 2.0))
        M.face([P(a_out, b0, c0), P(a_in, b0, c0), P(a_in, b1, c0), P(a_out, b1, c0)],
               up, (P(am, 0.0, c0), RAIL_W / 2.0))
        for bb, back in zip(brackets, backs):
            # full faces down and toward the ladder's middle
            bar(M, lambda t, u, v, am=am: P(u, v, t), back + g, c0 - g,
                am + side * k2, am - side * k2, bb + k2, bb - k2, bracket_form, out)
    n = int((length - 0.25) / RUNG_PITCH)
    lo = half - RAIL_W / 2.0 - g
    for k in range(n):
        if mode and k % mode == 0:
            b = RUNG_PITCH * (k + 1)
            # full faces up and out: from above and in front, and in a sun
            # from there, its outline is the old square bar's
            bar(M, P, -lo, lo, b - r2, b + r2, cm - r2, cm + r2, rung_form, across)
    return M


# ============================================================ placement
class Eave:
    """One eave: its wall, its overhang and the slope above it."""

    def __init__(self, p0, p1, z_wall, eave_out, z_edge, tan):
        self.p0 = Vector((p0[0], p0[1], 0.0))
        d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
        self.length = d.length
        self.t = d / self.length
        self.n = Vector((self.t.y, -self.t.x, 0.0))
        self.z_wall, self.eave_out, self.z_edge, self.tan = z_wall, eave_out, z_edge, tan
        ang = math.atan(tan)
        self.cos, self.sin = math.cos(ang), math.sin(ang)
        # up the slope, and off the sheet
        self.up = -self.n * self.cos + Vector((0.0, 0.0, self.sin))
        self.off = self.n * self.sin + Vector((0.0, 0.0, self.cos))

    def point(self, s, out, z):
        return self.p0 + self.t * s + self.n * out + Vector((0.0, 0.0, z))

    def roof_z(self, out):
        """The sheet's top at *out* from the wall face, on the slope."""
        return self.z_edge + (self.eave_out - out) * self.tan

    def out_at(self, z):
        """Where on the slope the sheet's top is at height *z*."""
        return self.eave_out - (z - self.z_edge) / self.tan


class WallLadder:
    """The ladder from the ground up the eave's wall, centred *s* along it.

    *lean* builds it, and its Cage, as the lean kit (module docstring):
    separate solids that touch nothing, for append() after the weld rather
    than the union. Its brackets then stop short of the wall instead of
    running into it, so where something stands proud of the wall behind
    them -- a plinth, a base -- *behind* gives that: a function of height
    (build-frame z) returning how far the surface behind the ladder stands
    out from the eave wall's face there, 0 by default."""

    def __init__(self, eave, s, foot=0.0, brackets=None, lean=False, behind=None):
        self.eave, self.s, self.foot = eave, s, foot
        self.lean, self.behind = lean, behind
        self.standoff = eave.eave_out + EAVE_CLEAR
        self.length = eave.z_edge + LADDER_TOP - foot
        if brackets is None:
            top = eave.z_wall - SOFFIT_CLEAR - foot
            n = max(1, int((top - 0.6) / WALL_BRACKET_PITCH) + 1)
            brackets = [0.6 + (top - 0.6) * k / max(1, n) for k in range(n + 1)]
        self.brackets = brackets

    def span(self):
        return (self.s - HALF, self.s + HALF)

    def backs(self):
        """How far out from the wall face the surface behind each bracket
        stands: *behind* at its foot, middle and top, the furthest."""
        if self.behind is None:
            return [0.0] * len(self.brackets)
        k2 = BRACKET / 2.0
        return [max(self.behind(self.foot + b + dz) for dz in (-k2, 0.0, k2))
                for b in self.brackets]

    def solid(self, paint, mode, fittings, form=("prism", "prism")):
        """The ladder at rung *mode*, with its brackets if *fittings*; a lean
        ladder's (rungs, brackets) in *form* (a LEAN_FORMS entry), its bare
        rails the same as any ladder's."""
        e = self.eave
        if not self.lean or mode is None:
            return ladder(e.point(self.s, 0.0, self.foot), (0, 0, 1), e.t, e.n,
                          self.length, self.standoff,
                          self.brackets if fittings and mode else [], mode, paint)
        keep = fittings and mode
        return _finish(lean_ladder(
            e.point(self.s, 0.0, self.foot), (0, 0, 1), e.t, e.n, self.length,
            self.standoff, self.brackets if keep else [], mode, paint, form,
            self.backs() if keep else []))


def _prism(M, ring0, ring1, along):
    """Quads between two matching rings of points, and the rings as caps."""
    n = len(ring0)
    for k in range(n):
        M.face([ring0[k], ring0[(k + 1) % n], ring1[(k + 1) % n], ring1[k]], along)
    M.face(list(reversed(ring0)), along)
    M.face(list(ring1), along)
    return M


class Cage:
    """The safety cage round wall ladder *wall*'s climber, its lowest hoop
    at height *foot* and its top hoop at *top* (build-frame z): by default
    CAGE_FOOT over the ladder's foot and CAGE_TOP_GAP under its top. Hoops
    at most CAGE_PITCH apart, evenly spaced; *modes* per tier, as
    CAGE_MODES. Every hoop is a closed solid whose ends run into the rails,
    and every strap one that runs through the hoops, so the build's union
    joins them to the ladder."""

    def __init__(self, wall, foot=None, top=None, modes=CAGE_MODES):
        self.wall, self.eave, self.s, self.modes = wall, wall.eave, wall.s, modes
        self.lean = getattr(wall, "lean", False)     # lean with its ladder
        self.foot = wall.foot + CAGE_FOOT if foot is None else foot
        self.top = wall.foot + wall.length - CAGE_TOP_GAP if top is None else top
        if self.top - self.foot < CAGE_PITCH / 2.0:
            raise ValueError("a cage from %.2f to %.2f m is too short for its ladder"
                             % (self.foot, self.top))
        self.o = wall.standoff + CAGE_OUT
        n = int(math.ceil((self.top - self.foot) / CAGE_PITCH - 1e-9))
        self.hoops = [self.foot + (self.top - self.foot) * k / n for k in range(n + 1)]

    def span(self):
        half = CAGE_R + HOOP_T
        return (self.s - half, self.s + half)

    def point(self, a, o, z):
        return tuple(self.eave.point(self.s + a, o, z))

    def hoop_path(self):
        """A hoop's centre line in (a, o): from inside one rail, flaring out
        to the arc, round the back, and into the other rail."""
        rail_o = self.wall.standoff + RAIL_D / 2.0
        a_in = LADDER_W / 2.0 + RAIL_W / 2.0 - 0.02      # 2 cm inside the rail
        arc = [(CAGE_R * math.cos(math.pi * (1.0 - k / CAGE_ARC)),
                self.o + CAGE_R * math.sin(math.pi * (1.0 - k / CAGE_ARC)))
               for k in range(CAGE_ARC + 1)]
        return [(-a_in, rail_o)] + arc + [(a_in, rail_o)]

    def hoop(self, z, paint):
        """One flat-bar hoop at height *z*, swept along hoop_path() with
        mitred corners, its ends capped inside the rails."""
        pts = [Vector(p) for p in self.hoop_path()]
        segs = [(q - p).normalized() for p, q in zip(pts, pts[1:])]
        left = [Vector((-d.y, d.x)) for d in segs]
        offs = []
        for i in range(len(pts)):
            if i == 0 or i == len(pts) - 1:
                offs.append(left[0] if i == 0 else left[-1])
                continue
            m = (left[i - 1] + left[i]).normalized()
            offs.append(m / m.dot(left[i - 1]))
        t, h = HOOP_T / 2.0, HOOP_H / 2.0
        rings = [[self.point(*(p + n * sa * t), z + sz * h)
                  for sa, sz in ((1, -1), (-1, -1), (-1, 1), (1, 1))]
                 for p, n in zip(pts, offs)]
        M = Mesh(paint)
        for i, d in enumerate(segs):
            along = Vector(self.point(*pts[i + 1], 0.0)) - Vector(self.point(*pts[i], 0.0))
            for k in range(4):
                M.face([rings[i][k], rings[i][(k + 1) % 4], rings[i + 1][(k + 1) % 4],
                        rings[i + 1][k]], along)
        M.face(list(reversed(rings[0])), (0, 0, 1))
        M.face(list(rings[-1]), (0, 0, 1))
        return M

    def strap(self, angle, paint, tri=False):
        """A vertical strap on the hoops' outsides at *angle* round the arc;
        *tri*, a three-sided prism within it whose outer edge keeps its
        extent. Its section is laid out in the eave's left-handed (along,
        out) plane, so _outward() turns it."""
        a = math.radians(angle)
        rad, tan = Vector((math.cos(a), math.sin(a))), Vector((-math.sin(a), math.cos(a)))
        c = Vector((0.0, self.o)) + rad * CAGE_R
        w = STRAP_W / 2.0
        sec = [c + tan * w, c - tan * w, c - tan * w + rad * STRAP_T,
               c + tan * w + rad * STRAP_T]
        if tri:
            sec = [c + tan * w, c - tan * w, c + rad * STRAP_T]
        z0, z1 = self.hoops[0] - STRAP_END, self.hoops[-1] + STRAP_END
        M = _prism(Mesh(paint), [self.point(*p, z0) for p in sec],
                   [self.point(*p, z1) for p in sec], (0, 0, 1))
        return _outward(M, M.bm.faces[:])

    def lean_hoop(self, z, M):
        """hoop()'s lean twin, added to *M*: the same centre line and outer
        face, three-sided (its inner face a ridge), and ending LEAN_GAP
        outside the rail where the centre line leaves it rather than inside
        it, its cap in that face's plane."""
        pts = [Vector(p) for p in self.hoop_path()]
        segs = [(q - p).normalized() for p, q in zip(pts, pts[1:])]
        left = [Vector((-d.y, d.x)) for d in segs]
        offs = [left[0]]
        for i in range(1, len(pts) - 1):
            m = (left[i - 1] + left[i]).normalized()
            offs.append(m / m.dot(left[i - 1]))
        offs.append(left[-1])
        t, h, g = HOOP_T / 2.0, HOOP_H / 2.0, LEAN_GAP
        sec = ((1, -1), (1, 1), (-1, 0))        # outer face full, inner ridge
        rings = [[(p + n * sa * t, sz) for sa, sz in sec] for p, n in zip(pts, offs)]
        front = self.wall.standoff + RAIL_D
        for idx, d, side in ((0, segs[0], -1.0), (-1, -segs[-1], 1.0)):
            p = pts[idx]                        # inside the rail; d leads out
            planes = [(Vector((0.0, 1.0)), front + g),
                      (Vector((side, 0.0)), HALF + g)]
            n2, val = min(((n2, val) for n2, val in planes if d.dot(n2) > 1e-9),
                          key=lambda pl: (pl[1] - p.dot(pl[0])) / d.dot(pl[0]))
            rings[idx] = [(q + d * ((val - q.dot(n2)) / d.dot(n2)), sz)
                          for q, sz in rings[idx]]
        rings = [[self.point(q.x, q.y, z + sz * h) for q, sz in r] for r in rings]
        for i, d in enumerate(segs):
            along = Vector(self.point(*pts[i + 1], 0.0)) - Vector(self.point(*pts[i], 0.0))
            for k in range(3):
                M.face([rings[i][k], rings[i][(k + 1) % 3], rings[i + 1][(k + 1) % 3],
                        rings[i + 1][k]], along)
        M.face(list(reversed(rings[0])), (0, 0, 1))
        M.face(list(rings[-1]), (0, 0, 1))
        return M

    def lean_strap(self, angle, M):
        """strap()'s lean twin, added to *M*: the same outer face, three-sided,
        its inner edge LEAN_GAP off the hoops' outermost corners."""
        a = math.radians(angle)
        rad, tan = Vector((math.cos(a), math.sin(a))), Vector((-math.sin(a), math.cos(a)))
        c = Vector((0.0, self.o)) + rad * CAGE_R
        w = STRAP_W / 2.0
        r_in = HOOP_T / 2.0 / math.cos(math.pi / (2.0 * CAGE_ARC)) + LEAN_GAP
        sec = [c + tan * w + rad * STRAP_T, c - tan * w + rad * STRAP_T, c + rad * r_in]
        z0, z1 = self.hoops[0] - STRAP_END, self.hoops[-1] + STRAP_END
        return _prism(M, [self.point(*p, z0) for p in sec],
                      [self.point(*p, z1) for p in sec], (0, 0, 1))

    def solid(self, paint, level, kit=True):
        """The hoops this tier keeps and the straps, for the union; or, on a
        tier without hoops or without the kit, the back strap alone,
        three-sided, for append(). A lean cage's hoops and straps are one
        mesh of separate solids, for append()."""
        every = self.modes[level] if kit else None
        if every is None:
            return [self.strap(90.0, paint, tri=True)]
        zs = [z for k, z in enumerate(self.hoops)
              if k % every == 0 or k == len(self.hoops) - 1]
        if self.lean:
            M = Mesh(paint)
            for z in zs:
                self.lean_hoop(z, M)
            for a in STRAP_ANGLES:
                self.lean_strap(a, M)
            return [_finish(M)]
        return [self.hoop(z, paint) for z in zs] + [self.strap(a, paint)
                                                     for a in STRAP_ANGLES]

    def problems(self, name):
        """What only a cage can get wrong; problems() adds its place."""
        bad = []
        if min(o for _a, o in self.hoop_path()) < self.eave.eave_out + 0.10:
            bad.append("%s's hoops reach the eave" % name)
        if self.hoops[-1] + HOOP_H > self.wall.foot + self.wall.length:
            bad.append("%s's top hoop is above the ladder" % name)
        if self.hoops[0] < self.wall.foot + 2.0:
            bad.append("%s starts under 2.0 m, in the climber's way at the foot" % name)
        return bad


class RoofLadder:
    """The ladder up the slope from the eave, centred *s* along it, to where
    the sheet reaches *z_top*."""

    def __init__(self, eave, s, z_top):
        self.eave, self.s, self.z_top = eave, s, z_top
        self.length = (z_top - eave.z_edge) / eave.sin - ROOF_START
        n = max(1, int(round(self.length / ROOF_BRACKET_PITCH)))
        self.brackets = [0.3 + (self.length - 0.6) * k / n for k in range(n + 1)]

    def top_out(self):
        """The *out* of the ladder's top, on the plan."""
        return self.eave.out_at(self.z_top)

    def solid(self, paint, mode, fittings):
        e = self.eave
        out = e.eave_out - ROOF_START * e.cos
        foot = e.point(self.s, out, e.roof_z(out))
        return ladder(foot, e.up, e.t, e.off, self.length, ROOF_STANDOFF,
                      self.brackets if fittings else [], mode, paint)


class Walkway:
    """The level walkway along the slope from *s0* to *s1*, its downslope
    edge at *out* from the wall face -- a roof ladder's top_out() when it
    starts from one."""

    def __init__(self, eave, s0, s1, out):
        self.eave, self.s0, self.s1 = eave, min(s0, s1), max(s0, s1)
        self.out_lo = out                   # downslope edge
        self.out_hi = out - WALK_W          # upslope edge, higher on the sheet
        self.z_top = eave.roof_z(self.out_hi) + WALK_GAP + WALK_T

    def solid(self, paint, mode, fittings):
        """The plank and each post as solids of their own: they overlap, and
        the exact boolean resolves overlaps between operands, not inside one.
        Without *fittings* the plank alone, its posts under a pixel."""
        e = self.eave
        z = self.z_top
        out = [box(Mesh(paint), e.point(0.0, 0.0, 0.0), e.t, e.n, (0, 0, 1),
                   (self.s0, self.s1), (self.out_hi, self.out_lo), (z - WALK_T, z))]
        if not fittings:
            return out
        n = max(1, int(math.ceil((self.s1 - self.s0 - 0.2) / POST_PITCH)))
        om = (self.out_hi + self.out_lo) / 2.0
        zb = e.roof_z(om + POST) - SLAB_BURY
        for k in range(n + 1):
            s = self.s0 + 0.1 + (self.s1 - self.s0 - 0.2) * k / n
            out.append(box(Mesh(paint), e.point(s, om, 0.0), e.t, e.n, (0, 0, 1),
                           (-POST / 2.0, POST / 2.0), (-POST / 2.0, POST / 2.0),
                           (zb, z - WALK_T / 2.0)))
        return out


def clashes(obj, pieces):
    """What in *pieces*, (solid, name) pairs, touches or cuts *obj*'s mesh,
    or one of its own solids another: append() joins nothing, so a lean part
    that reaches the wall or a neighbour would leave both whole, buried in
    each other. Faces that share a vertex belong to one solid and are not
    compared."""
    from mathutils.bvhtree import BVHTree
    verts, polys, owner = [], [], []
    for M, name in pieces:
        base = len(verts)
        index = {v: base + i for i, v in enumerate(M.bm.verts)}
        verts += [v.co.copy() for v in M.bm.verts]
        for f in M.bm.faces:
            polys.append([index[v] for v in f.verts])
            owner.append(name)
    if not polys:
        return []
    kit = BVHTree.FromPolygons(verts, polys)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    building = BVHTree.FromBMesh(bm)
    bm.free()
    bad = []
    hit = building.overlap(kit)
    if hit:
        c = Vector(verts[polys[hit[0][1]][0]])
        bad.append("%d faces of the kit meet the building, e.g. %s's near (%.3f, %.3f, %.3f)"
                   % (len({j for _i, j in hit}), owner[hit[0][1]], c.x, c.y, c.z))
    pairs = [(i, j) for i, j in kit.overlap(kit)
             if i < j and not set(polys[i]) & set(polys[j])]
    if pairs:
        c = Vector(verts[polys[pairs[0][0]][0]])
        bad.append("%d pairs of the kit's faces from different solids meet, e.g. "
                   "near (%.3f, %.3f, %.3f)" % (len(pairs), c.x, c.y, c.z))
    return bad


def append(obj, pieces, check=False):
    """Add *pieces*, (solid, name) pairs touching nothing, to *obj*'s mesh
    after its union and its cleanup. A wall ladder's bare rails stand clear
    of the building, so there is nothing to join, and in the mesh before a
    build's weld and dissolve they changed what those greedy passes merged
    elsewhere, for eight more triangles on a tier with none to spare. The
    lean kit goes in this way on every tier. append() recalculates no
    normals: every solid this module hands it (bare rails, the back strap,
    a walkway's plank, the lean parts) is wound outward as it is built.
    *check* raises if a piece meets the mesh or another piece (clashes())."""
    if check:
        bad = clashes(obj, pieces)
        if bad:
            raise ValueError("the appended kit is not clear:\n  " + "\n  ".join(bad))
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for M, _name in pieces:
        me = bpy.data.meshes.new("tmp_append")
        M.bm.to_mesh(me)
        M.bm.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def solids(parts, level, paint, extents=False, modes=MODES, forms=LEAN_FORMS):
    """(solid, object name) for each of *parts* at *level*; none past the
    tiers that keep the kit. *modes* replaces MODES for a building that
    cannot afford the kit as far out; a Cage thins its hoops by its own
    modes. With *extents*, a tier that drops the kit still keeps each wall
    ladder's bare rails, 16 triangles, and each cage's back strap, 8, for a
    building whose extents a wall ladder or its cage sets: every tier shares
    LOD0's bounds and pivot. *forms* replaces LEAN_FORMS for a lean ladder's
    rungs and brackets."""
    mode, fittings = modes[level]
    out = []
    for p in parts:
        if mode is None and not (extents and isinstance(p, (WallLadder, Cage))):
            continue
        if isinstance(p, Cage):
            got = p.solid(paint, level, kit=mode is not None)
        elif isinstance(p, WallLadder):
            got = p.solid(paint, mode, fittings, forms[level])
        else:
            got = p.solid(paint, mode, fittings)
        for M in (got if isinstance(got, list) else [got]):
            out.append((M, "tmp_roof_safety%d" % len(out)))
    return out


def problems(wall, name, avoid, clear=CLEAR):
    """What is wrong with wall ladder *wall*'s place on its wall, or a
    Cage's: its outside within CORNER of either end, or within *clear* of
    any (what, s0, s1) span it has to miss, such as an opening, a canopy or
    a downpipe (give a pipe's span as its axis +- downpipes.A); a span may
    carry its own clearance as a fourth item. Also a ladder's bracket that
    would meet the soffit, and a cage's hoops reaching the eave, rising
    above the ladder or starting under 2 m."""
    bad = []
    s0, s1 = wall.span()
    if s0 < CORNER - 1e-6 or s1 > wall.eave.length - CORNER + 1e-6:
        bad.append("%s is within %.2f m of a corner" % (name, CORNER))
    for what, a0, a1, *own in avoid:
        c = own[0] if own else clear
        if a0 - c < s1 and s0 < a1 + c:
            bad.append("%s crowds the %s" % (name, what))
    if isinstance(wall, Cage):
        return bad + wall.problems(name)
    if wall.brackets and wall.foot + max(wall.brackets) + BRACKET / 2.0 > \
            wall.eave.z_wall - 0.05:
        bad.append("%s has a bracket in the soffit" % name)
    if getattr(wall, "lean", False) and any(wall.standoff - back < 0.05
                                            for back in wall.backs()):
        bad.append("%s has a bracket with under 5 cm between its rail and the "
                   "surface behind it" % name)
    return bad
