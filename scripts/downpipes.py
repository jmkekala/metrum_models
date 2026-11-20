# SPDX-License-Identifier: GPL-3.0-or-later

"""Downpipes: the rainwater pipe from an eave's gutter down a wall to the
ground, as one closed solid for a build.py to union into its tier.

    import downpipes as DP
    PIPES = [DP.eave_pipe(p0, p1, s, Z_EAVE, TAN, EAVE_OUT), ...]
    for B, name in DP.solids(PIPES, sides, bent, L.PIPE_STRIP, L.ATLAS):
        parts.append(to_object(B, name))
    bad += DP.problems(PIPES[0], "the front downpipe", [("door", s0, s1)])

A pipe hangs on a wall given by its plan end points p0 -> p1, walked
anticlockwise seen from above so the outward face is on the right, as every
build.py walks its walls; *s* is the pipe's centre along the wall from p0.
under(out) is the z of the underside the pipe leaves (a soffit, a slab) at
*out* metres from the wall face, so a sloping soffit and a flat one read alike.

Why modelled. A downpipe is 0.1 m, under the 0.25 m relief threshold, and is
modelled anyway: a wall samples a tiling band, which cannot place a pipe, and
a painted one has neither the shadow nor, at a corner, the edge a downpipe is
seen by. After the union each costs about 80 triangles with its bends at
eight sides, 40 at four, 13-20 straight and 10-15 three-sided, the pipe's
own faces and the hole it leaves in the soffit together.

Shape. The pipe stands GAP clear of the wall, as it does on its clips, and is
joined to nothing but the underside it leaves: buried in the wall, each pipe
cut two long lines through the wall's triangles and cost over 100 more. Under
an eave it leaves the soffit on a swan-neck: up into it at *outlet*, just
inside the fascia the gutter is painted on, down DROP, then back to the wall
at 45 degrees. Under a shallow overhang (outlet None) it runs straight up
into the underside. At the foot a shoe kicks it out from the wall and down,
its mouth clear of the ground. Unbent, the pipe runs straight from the
underside to FOOT: the swan-neck and the shoe are under two pixels past 70 m.
Either way the pipe never reaches the ground plane.

UVs. The sides map along the run onto the middle rows of the half-round
gutter each atlas paints on its eave band, named there as PIPE_STRIP. The pipe
takes the gutter's colour in every variant and its round shading across each
flat, and the gutter's hangers, a metre apart, read as the pipe's clips. So
an atlas that paints a gutter needs no new region for its pipes.

Runs inside Blender only.
"""

import math

import bmesh
from mathutils import Vector

A = 0.05            # half the pipe's width across its flats: a 0.1 m pipe
GAP = 0.03          # clear of the wall behind it
OUT = GAP + A       # its axis off the wall face
DROP = 0.25         # the swan-neck's fall below the soffit before its offset
BURY = 0.10         # how far its top runs up into the underside it leaves;
                    # keep it inside the slab's thickness
SHOE = (0.35, 0.15)  # the shoe starts this high and kicks out and down this far
FOOT = 0.20         # an unbent pipe's open end, without a shoe
CORNER = 0.25       # the least distance from a wall's end to the pipe's axis:
                    # its face 0.2 m in, clear of a corner board or a quoin
CLEAR = A + 0.2     # the least distance from its axis to an opening's side:
                    # 0.2 m of wall between the pipe and a casing

# (sides, bent) per tier, LOD0 to LOD3: eight sides with both bends up close,
# four to 70 m, straight four-sided pipes past it, and past 120 m, where a
# pipe is about a pixel across, three sides, which is all a one-pixel line
# needs. The last tier keeps the pipes because they are light against most
# walls and visibly go at the switch otherwise; a build.py that cannot
# afford them there passes (0, False) and records the vanishing in its notes.
MODES = ((8, True), (4, True), (4, False), (3, False))


def outlet(eave_out):
    """The swan-neck's outlet, off the wall face, under an eave projecting
    *eave_out*: the pipe's face 0.04 m inside the fascia."""
    return eave_out - A - 0.04


class Pipe:
    """One downpipe's place: its wall, where along it, and what it hangs from."""

    def __init__(self, p0, p1, s, under, outlet=None):
        self.p0 = Vector((p0[0], p0[1]))
        d = Vector((p1[0] - p0[0], p1[1] - p0[1]))
        self.length = d.length
        self.t = d / self.length
        self.n = Vector((self.t.y, -self.t.x))
        self.s, self.under, self.outlet = s, under, outlet

    def point(self, a, out, z):
        """World position *a* along the wall from the pipe's axis, *out* off
        the wall face, at height *z*."""
        q = self.p0 + self.t * (self.s + a) + self.n * out
        return Vector((q.x, q.y, z))

    def top(self, out):
        """Where a pipe on axis *out* stops: BURY into the underside, taken
        at whichever of its two faces meets the underside higher."""
        return max(self.under(out - A), self.under(out + A)) + BURY

    def path(self, bent=True):
        """The pipe's axis, top to bottom, as (out, z)."""
        if self.outlet is not None and bent:
            z1 = self.under(self.outlet) - DROP
            top = [(self.outlet, self.top(self.outlet)), (self.outlet, z1),
                   (OUT, z1 - (self.outlet - OUT))]
        else:
            top = [(OUT, self.top(OUT))]
        if not bent:
            return top + [(OUT, FOOT)]
        z0, k = SHOE
        return top + [(OUT, z0), (OUT + k, z0 - k)]


def eave_pipe(p0, p1, s, z_eave, tan, eave_out):
    """A pipe from the gutter of a pitched eave projecting *eave_out*, whose
    soffit meets the wall face at *z_eave* and falls *tan* per metre outward
    (0 for a level soffit): up into the soffit on a swan-neck."""
    return Pipe(p0, p1, s, lambda out: z_eave - out * tan, outlet=outlet(eave_out))


def slab_pipe(p0, p1, s, z_under):
    """A pipe running straight up into a level underside at *z_under* that
    oversails the wall too little for a swan-neck, such as a flat roof's
    slab fed through its parapet."""
    return Pipe(p0, p1, s, lambda out: z_under)


class Solid:
    """A closed bmesh with its UV layer, as asset_build.to_object takes it."""

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    def face(self, verts, uvs, atlas):
        f = self.bm.faces.new(verts)
        for loop, (u, v) in zip(f.loops, uvs):
            loop[self.uv].uv = (u / atlas, v / atlas)
        return f


def solid(pipe, sides, bent, strip, atlas, ppm=64.0, cap_uv=None):
    """*pipe* swept along its path as one closed solid, mitred at each bend.

    One flat always faces the wall, so no corner of an odd-sided ring
    reaches across the GAP into it; a ring that would raises. *strip* is
    (v0, v1), the atlas rows every flat spans across; along the run each flat
    takes *ppm* texels a metre. The top, buried in the underside, and the
    shoe's mouth take *cap_uv*, the strip's middle unless given, in atlas
    pixels.
    """
    S = Solid()
    path = [Vector(p) for p in pipe.path(bent)]
    n = len(path)
    dirs = [(path[i + 1] - path[i]).normalized() for i in range(n - 1)]
    norms = [Vector((-d.y, d.x)) for d in dirs]
    mits = [norms[0]]
    for n1, n2 in zip(norms, norms[1:]):
        mits.append((n1 + n2) / (1.0 + n1.dot(n2)))
    mits.append(norms[-1])
    r = A / math.cos(math.pi / sides)
    ab = [(r * math.cos(t), r * math.sin(t))
          for t in [-math.pi / 2.0 + (2 * k + 1) * math.pi / sides
                    for k in range(sides)]]
    rings = []
    for i in range(n):
        ring = []
        for a, b in ab:
            q = path[i] + mits[i] * b
            if q.x < GAP / 2.0:
                raise ValueError("a downpipe at s %.2f reaches into its wall"
                                 % pipe.s)
            ring.append(S.bm.verts.new(pipe.point(a, q.x, q.y)))
        rings.append(ring)
    run = [0.0]
    for i in range(n - 1):
        run.append(run[-1] + (path[i + 1] - path[i]).length)
    v0, v1 = strip
    for i in range(n - 1):
        u0, u1 = run[i] * ppm, run[i + 1] * ppm
        for k in range(sides):
            k1 = (k + 1) % sides
            S.face([rings[i][k], rings[i][k1], rings[i + 1][k1], rings[i + 1][k]],
                   [(u0, v0), (u0, v1), (u1, v1), (u1, v0)], atlas)
    cap = cap_uv or (0.0, (v0 + v1) / 2.0)
    S.face(rings[0], [cap] * sides, atlas)
    S.face(list(reversed(rings[-1])), [cap] * sides, atlas)
    return S


def solids(pipes, sides, bent, strip, atlas, **kw):
    """(solid, object name) for each of *pipes* at one tier's (sides, bent);
    none when *sides* is 0."""
    if not sides:
        return []
    return [(solid(p, sides, bent, strip, atlas, **kw), "tmp_downpipe%d" % i)
            for i, p in enumerate(pipes)]


def problems(pipe, name, avoid, clear=CLEAR, corners=True):
    """What is wrong with *pipe*'s place on its wall: its axis within CORNER
    of either end, or within *clear* of any (what, s0, s1) span along the
    wall it has to miss, such as an opening, a canopy or a ladder. A span
    may carry its own clearance as a fourth item, for something the pipe
    may stand closer to than a window, such as a garden wall. *corners*
    False skips the ends, for a pipe on a post or a pier's face."""
    bad = []
    if corners and not CORNER - 1e-6 <= pipe.s <= pipe.length - CORNER + 1e-6:
        bad.append("%s is within %.2f m of a corner" % (name, CORNER))
    for what, s0, s1, *own in avoid:
        c = own[0] if own else clear
        if s0 - c < pipe.s < s1 + c:
            bad.append("%s crowds the %s" % (name, what))
    return bad
