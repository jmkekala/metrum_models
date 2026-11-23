# SPDX-License-Identifier: GPL-3.0-or-later

"""The concrete floor slab of an opening recessed at grade: the layout, the
atlas painting, the geometry and the layout check, in one place.

An opening that stands on the ground in a recess has no upward face under
it, so a consumer's terrain shows inside: grass between the paving and the
door. CLAUDE.md (Geometry and Construction, Openings) gives every opening
recessed at grade, whatever its depth, a slab filling its plan: a door of
any kind, a lobby or set-back doorway, set-back glazing or a portal. Its
top is T over the ground (a face at grade fights the terrain), a nosing on
the wall plane, nothing past it, on its own atlas region, on every tier
that keeps the recess. Bounds, footprint and the door's threshold stay as
they are: the slab is a floor finish, not a step. scripts/validate_asset.py
probes every sidecar door for it on every tier.

Geometry. The nosing is a quad on the wall plane from the ground to T across
the opening; the recess starts on its top, and the recess's foot cheek is
the slab's top, back to the closing face. The wall's foot detours round the
opening with a corner at T on each side (notch()), so the wall, the nosing,
the slab top and the cheeks all meet on shared vertices, and the open rim the
floor cap closes runs straight along the wall line under the nosing instead
of round the reveal. Four triangles a slab over a recess that stood on the
ground (skip_z), and none at grade inside the reveal.

UVs. One region per slab, unfolded: U along the wall from the opening's left
side, V up the nosing from the ground (T) and then back across the top from
the wall plane to the closing face (depth), at the atlas's texel density.

Painting. Float-finished cast concrete in one fixed colour (COLOUR, SURFACE)
whatever the variant, flat, its occlusion deepening toward the jambs and the
door, where the floor sees least sky, a paler worn path toward the leaf, pores
in its shade and trodden-in dirt over it: the three slabs built before this
module (the salon's, the barber's and the grocery's), which look alike, in one
copy.

    import door_floor as DF

    # facade_atlas.py (numpy only)
    ID_FLOOR = 20
    FLOORS = {"front": DF.Floor(820, 690, 3.0, LOBBY_DEPTH)}   # x, y px; m
    FIXED[ID_FLOOR], SURFACE[ID_FLOOR] = DF.COLOUR, DF.SURFACE
    rects.update({"floor_" + k: f.rect for k, f in FLOORS.items()})
    for f in FLOORS.values():                       # paint(), with the regions
        DF.paint(c, f, ID_FLOOR, bleed=PAD)
    DF.grain(c, ID_FLOOR, pores)                    # with the other pores
    for f in FLOORS.values():                       # weather()
        DF.weather(w, f, ID_FLOOR, bleed=PAD)

    # build.py, wherever the opening is cut
    foot += DF.notch(rect)                          # the wall's detour
    DF.recess(B, fr, rect, 0.0, -depth, back, cheeks, L.FLOORS["front"])
    bad += DF.problems(L.FLOORS["front"], "the front entrance", rect, depth)

Importing needs numpy alone, so a texture generator runs it in system Python
and build.py in Blender; recess() imports shell_build when it is called.
"""

import numpy as np

T = 0.02                    # the slab's top over the ground, metres
COLOUR = (132, 130, 124)    # sRGB: cast concrete, one colour in every variant
SURFACE = (0.88, 0.0)       # (roughness, metallic)
EPS = 1e-6


class Floor:
    """One slab's layout: its atlas region and the reveal it fills.

    (x, y) is the region's lower-left corner in atlas pixels; *width* is the
    opening's width and *depth* the reveal's, in metres, at *ppm* texels a
    metre. *tread* is the centre of the worn path across the slab, metres
    from the opening's left side (the leaf's centre; by default the
    opening's), and *spread* its width; *falloff* is how far the occlusion
    at the jambs and the door reaches. The defaults suit a single leaf in a
    shallow reveal and a pair in a lobby alike.
    """

    def __init__(self, x, y, width, depth, ppm=64.0, tread=None, spread=None,
                 falloff=None):
        self.x, self.y = x, y
        self.width, self.depth, self.ppm = width, depth, float(ppm)
        self.tread = width / 2.0 if tread is None else tread
        self.spread = min(0.6, 0.3 * width) if spread is None else spread
        self.falloff = min(0.12, 0.4 * depth) if falloff is None else falloff
        self.rect = (x, y, width * self.ppm, (T + depth) * self.ppm)


# ================================================================== atlas
def paint(c, floor, mid, bleed=2):
    """Paint *floor*'s region on canvas *c* as material id *mid*, and *bleed*
    px beyond it. Its first rows are the nosing on the wall plane, which
    takes the shading of the slab's front edge."""
    x, y, w, h = floor.rect
    c.paint(x - bleed, x + w + bleed, y - bleed, y + h + bleed, mid, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(x - bleed, x + w + bleed, y - bleed, y + h + bleed)
    u = np.clip((X - x) / floor.ppm, 0.0, floor.width)
    v = np.clip((Y - y) / floor.ppm - T, 0.0, floor.depth)
    side = np.minimum(u, floor.width - u)
    edge = np.minimum(side, floor.depth - v)
    corner = np.exp(-edge / floor.falloff)
    tread = np.exp(-((u - floor.tread) / floor.spread) ** 2)
    c.shade[sy, sx] = (1.0 - 0.14 * corner) * (1.0 + 0.05 * tread)
    c.ao[sy, sx] = 1.0 - 0.30 * corner


def grain(c, mid, pores):
    """The concrete's pores on every sample of id *mid*: *pores* is the
    generator's own unit-variance pore noise (atlas.noise(c, seed, 0.7-0.8)),
    in the shade and a fraction of a millimetre of height."""
    cast = c.mid == mid
    c.shade[cast] *= 1.0 + 0.05 * pores[cast]
    c.height[cast] += 0.0004 * pores[cast]


def weather(w, floor, mid, bleed=2):
    """Trodden-in dirt, blotchy, over *floor*'s region (a weathering.Weather)."""
    x, y, rw, rh = floor.rect
    w.add("D", x - bleed, x + rw + bleed, y - bleed, y + rh + bleed,
          lambda Y, X, nz: 0.08 + 0.10 * nz("blotch"), (mid,))


# =============================================================== geometry
def uv(fr, floor, s0, z0=0.0):
    """The slab unfolded onto its region: U along wall frame *fr* from *s0*,
    V up the nosing from *z0* and then back across the top."""
    x, y, _w, _h = floor.rect
    return lambda co: (x + (fr.s_of(co) - s0) * floor.ppm,
                       y + (co.z - z0 + max(0.0, -fr.out_of(co))) * floor.ppm)


def notch(rect):
    """The wall foot's detour round floored opening *rect* (s0, s1, z0, z1),
    from (s0, z0) to (s1, z0), with the nosing's top as a corner each side."""
    s0, s1, z0, z1 = rect
    zf = z0 + T
    return [(s0, z0), (s0, zf), (s0, z1), (s1, z1), (s1, zf), (s1, z0)]


def recess(B, fr, rect, near, far, back, cheeks, floor, u0=None):
    """Line opening *rect* (s0, s1, z0, z1), standing at z0 on the ground,
    and close it set back, on a slab: shell_build.recess() with its foot
    raised to the slab's top.

    *near*, *far*, *back* and *cheeks* are shell_build.recess()'s: fr.P's
    third coordinate at the wall face and at the closing face (on a Frame
    far = -depth, on an InwardFrame +depth), the closing face's UVs, and
    one UV function for every side or four, counter-clockwise from the foot,
    whose first (the foot's) is replaced by the slab's top. The nosing is
    made when *near* is the wall plane; the inner step of a cased opening
    (near != 0) only continues the top, and *u0*, the outer step's s0, keeps
    it on the same stretch of the region. Returns the opening's outline on
    the wall, counter-clockwise from its foot, with the nosing's corners.
    """
    import shell_build as SB
    s0, s1, z0, z1 = rect
    zf = z0 + T
    fn = uv(fr, floor, s0 if u0 is None else u0, z0)
    if abs(near) < EPS:
        B.face([fr.P(s0, z0), fr.P(s1, z0), fr.P(s1, zf), fr.P(s0, zf)], fn)
    sides = list(cheeks) if isinstance(cheeks, (list, tuple)) else [cheeks] * 4
    SB.recess(B, fr, SB.rect_poly((s0, s1, zf, z1)), near, far, back, [fn] + sides[1:])
    return [(s0, z0), (s1, z0), (s1, zf), (s1, z1), (s0, z1), (s0, zf)]


def problems(floor, name, rect, depth):
    """What is wrong with *floor* under opening *rect* (s0, s1, z0, z1) in a
    reveal *depth* deep, as messages for check_layout(): the opening not on
    the ground, or the region not the slab's width and depth."""
    s0, s1, z0, z1 = rect
    bad = []
    if abs(z0) > EPS:
        bad.append("%s stands %.3f m off the ground: its slab expects it at grade"
                   % (name, z0))
    if z1 - z0 <= T:
        bad.append("%s is lower than its slab" % name)
    if abs(floor.width - (s1 - s0)) > EPS:
        bad.append("%s's floor slab is %.3f m wide for a %.3f m opening"
                   % (name, floor.width, s1 - s0))
    if abs(floor.depth - depth) > EPS:
        bad.append("%s's floor slab is %.3f m deep for a %.3f m reveal"
                   % (name, floor.depth, depth))
    return bad
