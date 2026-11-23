# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of lahikauppa_corner, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite Finnish neighbourhood shop of the kind built beside housing estates
from the 1980s on: one tall retail storey in facing brick, banded and panelled
with white render, under a flat roof whose long white eave runs right round the
building and falls outward as it goes, so the deck is the high side and snow
pushed off it goes over the edge rather than piling behind a parapet. Because
the eave falls to head height at its outer edge it shelters the shopfront
itself, and there is no separate canopy.

The street elevation carries the whole public side of the shop. Its right-hand
corner is cut off at 45 degrees and glazed, with a pair of sliding glass doors
in the middle of the cut, set back into a lobby on a 0.02 m concrete floor
slab, and a lit sign standing on the eave above them. At the
other end of the same wall the walls step back under the roof to make a covered
loading bay deep enough to take all but the nose of a delivery van, with the
goods door in its back wall and a column at the open corner.

The roof plant is serviced from the deck, so a wall ladder (scripts/
roof_safety.py) climbs the rear wall to it, at the back, away from the street
and the entrance: off the wall on long brackets, passing outside the 1.5 m
eave and running a metre above its edge. It is the building's rearmost point,
so every tier keeps at least its bare rails and the plan bounds hold.

Construction is a set of closed solids unioned with Blender's exact boolean:
the wall ring, the roof, the sign, the column, the render panels and the roof
plant. Each is simple on its own; the union is what trims the wall tops into
the roof, trims the render panels flush against the soffit, and leaves the
boundary of one empty volume, so interior geometry cannot occur. The roof is
one solid rather than a slab plus a swept eave: the deck and the skirt are a
single surface folding at the wall line, and two solids meeting along that fold
touch tangentially, which is the case the boolean handles worst.

Every number the mesh and the atlas share is imported from facade_atlas.py
rather than written here a second time.
"""

import functools
import importlib
import math
import os
import sys

import bmesh
from mathutils import Vector


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
import roof_safety as RS  # noqa: E402
import shell_build as SB  # noqa: E402
from asset_build import pivot_offset, to_object, union  # noqa: E402,F401
from shell_build import Frame, fill_region, rect_poly  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT,
                          tint=L.LIT_FACTOR)
get_material, export_all = BUILD.material, BUILD.export_all
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants
Builder = functools.partial(SB.Builder, L.ATLAS)

PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ================================================================== massing
# Front (the street side) faces -Y. The plan is a 32 x 18 m rectangle with the
# street corner cut off at 45 degrees for the entrance; the loading bay is a
# notch taken out of the walls at the other end of the same wall, which the
# roof passes straight over.
HX, HY = 16.0, 9.0
CHAMFER = 4.5                       # cut back this far along each wall
BAY_X, BAY_Y = -9.0, -4.0           # inner corner of the loading-bay notch

Z_TOP = L.Z_WALL + L.WALL_INTO_ROOF          # wall top, buried in the roof slab
FALL = L.EAVE_FALL / L.EAVE_OUT     # the eave's fall, per metre out from the wall

# The roof outline: the wall line, with the two breakpoints the slab's underside
# needs where the loading bay's ceiling is a face of its own.
OUTLINE = [(-HX, -HY), (HX - CHAMFER, -HY), (HX, -HY + CHAMFER), (HX, HY),
           (-HX, HY)]
CHAMFER_EDGE = 1                    # OUTLINE edge index the entrance is under:
                                    # OUTLINE[1] -> OUTLINE[2] is the 45 degree cut
CHAMFER_LEN = CHAMFER * math.sqrt(2.0)

# The column at the loading bay's open corner, and the plant on the deck.
COLUMN = 0.32
PLANT = [
    ("box", (-10.5, 2.0), (2.2, 1.5), 0.95),
    ("box", (-7.0, 1.2), (1.8, 1.3), 0.85),
    ("cowl", (-12.2, 5.4), 0.45, 0.75),
    ("cowl", (-4.6, 4.2), 0.38, 0.65),
    ("pipe", (-1.2, 6.0), 0.14, 0.55),
    ("pipe", (2.2, 3.2), 0.12, 0.45),
]

# ------------------------------------------------------------------ elevations
# Each wall runs counter-clockwise seen from above, so its outward face is on
# the right and s runs along it from p0. panels are (s0, s1, band); items are
# (kind, s at the centre, z at the sill); glazing is (s0, s1) shopfront bays.
WALLS = [
    dict(name="bay_rear", p0=(-HX, BAY_Y), p1=(BAY_X, BAY_Y),
         panels=[(0.0, 7.0, "brick")],
         items=[("goods_door", 3.5, 0.0)], glazing=[]),
    dict(name="bay_east", p0=(BAY_X, BAY_Y), p1=(BAY_X, -HY),
         panels=[(0.0, 5.0, "brick")],
         items=[("service_door", 1.6, 0.0)], glazing=[]),
    dict(name="front", p0=(BAY_X, -HY), p1=(HX - CHAMFER, -HY),
         panels=[(0.0, 12.4, "brick"), (12.4, 20.5, "stucco")],
         piers=[(2.4, 3.4), (6.0, 7.0), (9.6, 10.6)],
         items=[], glazing=[(13.4, 19.4)]),
    dict(name="chamfer", p0=(HX - CHAMFER, -HY), p1=(HX, -HY + CHAMFER),
         panels=[(0.0, CHAMFER_LEN, "stucco")],
         items=[], glazing=[(0.6, CHAMFER_LEN - 0.6)], entrance=True),
    dict(name="east", p0=(HX, -HY + CHAMFER), p1=(HX, HY),
         panels=[(0.0, 5.0, "stucco"), (5.0, 13.5, "brick")],
         piers=[(7.2, 8.2), (11.2, 12.2)],
         items=[], glazing=[(0.6, 4.6)]),
    dict(name="rear", p0=(HX, HY), p1=(-HX, HY),
         panels=[(0.0, 32.0, "brick")],
         piers=[(3.4, 4.4), (12.2, 13.2), (21.0, 22.0), (28.2, 29.2)],
         items=[("staff_window", 6.0, 1.0), ("staff_window", 9.0, 1.0),
                ("service_door", 17.0, 0.0)],
         glazing=[]),
    dict(name="west", p0=(-HX, HY), p1=(-HX, BAY_Y),
         panels=[(0.0, 13.0, "brick")],
         piers=[(4.2, 5.2), (9.2, 10.2)],
         items=[], glazing=[]),
]

# The white ornament walls: rendered strips standing proud of the brick, which
# is what breaks a thirty-metre brick elevation up. At 0.25 m they are exactly
# at Geometry and Construction's default relief threshold and earn their
# triangles in shadow rather than colour alone; the render band along the top
# of every wall stays flat, in the texture.
PIER_OUT = 0.25
# The eave falls as it comes out, so a pilaster that stopped at the wall head
# would touch the soffit along one line and push through it everywhere beyond:
# tangential contact, which is the case an exact boolean handles worst, and it
# leaves a centimetre-high slot under the eave that reads as hidden surface.
# The pilaster runs up *into* the eave instead, so the union trims it flush
# against the soffit and the top face is properly buried. check_layout() keeps
# it strictly inside the eave's own thickness.
PIER_TOP = 4.40625

# ------------------------------------------------------------- roof safety
# The air handlers and fans on the deck are serviced from it, and a flat deck
# needs only a wall ladder up to it (CLAUDE.md, Geometry and Construction). It
# stands on the rear wall, between the two render panels west of the staff
# door, behind the plant it serves. The lean kit: separate solids that cut
# nothing, appended after the weld, so the wall keeps its triangles.
#
# This eave falls outward, so its soffit is lowest at the fascia, not at the
# wall, and the ladder's brackets run out under the whole slope to reach the
# rails outside it. The Eave's z_wall -- where roof_safety keeps the top
# bracket SOFFIT_CLEAR below, and problems() checks it -- is therefore the
# soffit's outer bottom edge, the lowest point any bracket passes under; tan
# is the skirt's fall. The ladder runs to the fascia top plus LADDER_TOP, 5.06
# m, under CAGE_LADDER, so it has no cage.
LADDER_S = 25.0
REAR = next(w for w in WALLS if w["name"] == "rear")
KIT_PAINT = RS.Paint(L.ATLAS, strip=L.LADDER_STRIP)
KIT_EAVE = RS.Eave(REAR["p0"], REAR["p1"], L.Z_EAVE_B, L.EAVE_OUT, L.Z_EAVE_T, FALL)
WALL_LADDER = RS.WallLadder(KIT_EAVE, LADDER_S, lean=True)
KIT = [WALL_LADDER]


def kit(level):
    """The wall ladder, roof_safety's MODES unchanged, with extents: it stands
    furthest out at the back, so LOD3 keeps its bare rails."""
    return RS.solids(KIT, level, KIT_PAINT, extents=True)


def item_mode(level):
    """LOD0/1 cut every opening into the wall; LOD2/3 paint it flat.

    The shopfront's 0.20 m reveal and the entrance's further 0.50 m are what
    give the street elevation its depth, so both survive LOD1; past 70 m the
    reveal is under a pixel and the painted rectangle keeps the rhythm.
    """
    return ("ring", "cut", "flush", "flush")[level]


def lobby_kept(level):
    """The entrance's own recess: 0.50 m of real shadow, kept while it reads."""
    return level < 2


def lobby_floor_top(spec, level):
    """The height the entrance's recess starts at: the top of the lobby's
    floor slab on the tiers that keep the lobby, the ground elsewhere (a flat
    entrance, a bay without one)."""
    if spec.get("entrance") and item_mode(level) != "flush" and lobby_kept(level):
        return L.LOBBY_FLOOR_T
    return 0.0


def plant_kept(level, kind):
    """Roof plant.

    The two air handlers are 1.8 and 2.2 m boxes about 0.9 m tall on the
    deck, so they break the roof line seen from above and are kept to LOD2.
    The cowls and pipes are under 0.5 m across -- a pixel or two at LOD1's
    distance, small on the dark deck, which the falling eave leaves open to
    any raised view -- so they stop at LOD0. None of it changes the plan,
    which the eave's outer edge and the wall ladder define.
    """
    if level >= 3:
        return False
    return kind == "box" or level < 1


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.

def uv_band(fr, y0, z_ref):
    return lambda co: (fr.s_of(co) * PPM, y0 + (co.z - z_ref) * PPM)


BAND_UV = {
    "brick": lambda fr: uv_band(fr, L.BRICK_Y0, 0.0),
    "stucco": lambda fr: uv_band(fr, L.STUCCO_Y0, 0.0),
}


def uv_patch(name):
    return SB.uv_patch(L.PATCHES[name])


def uv_rect(rect, umin, uspan, vmin, vspan, coord):
    """Map a region onto a rectangle of wall, in whatever coordinates *coord*
    reads off a vertex."""
    x, y, w, h = rect
    return lambda co: (x + (coord(co)[0] - umin) / uspan * w,
                       y + (coord(co)[1] - vmin) / vspan * h)


def uv_shop(fr, s0):
    """The tiling shopfront band, starting a structural mullion at s0."""
    return lambda co: ((fr.s_of(co) - s0) * PPM,
                       L.SHOP_Y0 + (co.z - L.Z_SILL) * PPM)


def uv_item(fr, kind, ol, ob):
    ow, oh = L.item_size_m(kind)
    x, y, w, h = L.ITEM_REGION[kind]
    return lambda co: (x + (fr.s_of(co) - ol) / ow * w,
                       y + (co.z - ob) / oh * h)


def uv_door_unit(fr, d0):
    x, y, w, h = L.DOOR_UNIT
    return lambda co: (x + (fr.s_of(co) - d0) / L.DOOR_UNIT_W * w,
                       y + co.z / L.Z_HEAD * h)


def uv_lobby_floor(fr, d0):
    """The entrance lobby's floor slab, unfolded: up its nosing on the wall
    plane, then back across its top to the doors (facade_atlas.LOBBY_FLOOR)."""
    x, y, _w, _h = L.LOBBY_FLOOR
    return lambda co: (x + (fr.s_of(co) - d0) * PPM,
                       y + (co.z + max(0.0, -fr.out_of(co))) * PPM)


def uv_soffit(fr):
    """The white eave and the canopy share one band; v is how far out the
    surface has reached, as a fraction of the eave's own slope length."""
    return lambda co: (fr.s_of(co) * PPM,
                       L.SOF_Y0 + max(0.0, fr.out_of(co)) / L.EAVE_OUT * L.SOF_H)


def uv_skirt_top(fr):
    """The skirt's top face: U along the run at 64 px/m from the start of its
    straight side, so the seams fall every 0.5 m and meet across a breakpoint
    in that side; V how far out, across SKIRT_STRIP."""
    v0, v1 = L.SKIRT_STRIP
    return lambda co: (fr.s_of(co) * PPM,
                       v0 + min(1.0, max(0.0, fr.out_of(co) / L.EAVE_OUT)) * (v1 - v0))


def uv_fascia(fr):
    """The fascia: the same seamed strip, U as the skirt's top, V its height."""
    v0, v1 = L.SKIRT_STRIP
    return lambda co: (fr.s_of(co) * PPM,
                       v0 + (co.z - L.Z_EAVE_B) / (L.Z_EAVE_T - L.Z_EAVE_B) * (v1 - v0))


def uv_deck(co):
    x, y, w, h = L.ROOF_DECK
    return (x + (co.x + HX) / (2 * HX) * w, y + (co.y + HY) / (2 * HY) * h)


def uv_bay_ceiling(co):
    x, y, w, h = L.BAY_CEILING
    return (x + (co.x + HX) / (BAY_X + HX) * w,
            y + (co.y + HY) / (BAY_Y + HY) * h)


# ================================================================== walls
def recess(B, fr, rect, depth, fn, rev):
    """Push a rectangle *depth* back from the wall and close it.

    A shallow opening that stands on the ground (a door's reveal) gets no
    floor of its own: the strip it would lay at z = 0 is inside the building's
    own footprint, so it would sit on top of the floor the wall ring is capped
    with, and the two coplanar faces leave the export non-manifold at the
    threshold. Left out, the rim simply detours round the recess and the floor
    cap covers it. The entrance lobby is deep enough to see into and is
    floored with a slab instead (build_glazing()).
    """
    SB.recess(B, fr, rect_poly(rect), 0.0, -depth, fn, rev,
              skip_z=None if rect[2] > EPS else rect[2])


def item_rects(kind, s, z):
    return SB.item_rects(L.OPENINGS[kind], s, z)


def build_item(B, fr, kind, s, z, level):
    """Faces for one repeated opening; returns the hole it needs in its wall."""
    mode = item_mode(level)
    (ol, orr, ob, ot), (il, ir, ib, it) = item_rects(kind, s, z)
    fn = uv_item(fr, kind, ol, ob)
    depth = L.REVEAL_DEPTH[kind]
    rev = uv_patch("reveal_dark" if kind != "staff_window" else "reveal_light")
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
        # A door has no bottom casing, so the threshold edge lies on the hole's
        # own bottom edge; the hole has to carry those two corners too.
        return [(ol, ob), (il, ib), (ir, ib), (orr, ob), (orr, ot), (ol, ot)]
    return o


def entrance_span(s0, s1):
    """The entrance unit's two edges, centred in its bay s0..s1."""
    d0 = (s0 + s1) / 2.0 - L.DOOR_UNIT_W / 2.0
    return d0, d0 + L.DOOR_UNIT_W


def build_glazing(B, fr, spec, s0, s1, level):
    """One shopfront bay: a recess in the wall, glazed across, with the sliding
    entrance set back again in the middle of it where the wall is the chamfer.

    The glazing stands on the plinth; the entrance unit breaks through it and
    stands on the ground, so its leaves are a door's height from the pavement.
    Every face of the unit is split at the sill line, where the plinth's
    return and the glazing beside it meet its edge.

    Where the lobby is kept, the way in is deep enough to see into, so it is
    floored: a concrete slab L.LOBBY_FLOOR_T over the ground (clear of the
    consumer's terrain at z = 0) from the wall plane back to the doors, its
    nosing on the wall plane between the plinth's cut ends. The recess starts
    on its top; the unit's art keeps its place.
    """
    mode = item_mode(level)
    entrance = spec.get("entrance", False)
    d0, d1 = entrance_span(s0, s1)
    door_uv = uv_door_unit(fr, d0)
    zf = lobby_floor_top(spec, level)

    def door_plane(out):
        for za, zb in ((zf, L.Z_SILL), (L.Z_SILL, L.Z_HEAD)):
            B.face([fr.P(d0, za, out), fr.P(d1, za, out),
                    fr.P(d1, zb, out), fr.P(d0, zb, out)], door_uv)
    # The entrance breaks the bay's sill and head lines whether it is a recess
    # or a painted rectangle, so the hole this bay needs in its wall carries
    # those two vertices either way.
    brk = [s0] + ([d0, d1] if entrance else []) + [s1]
    outline = ([(x, L.Z_SILL) for x in brk]
               + [(x, L.Z_HEAD) for x in reversed(brk)])

    if mode == "flush":
        if entrance:
            B.face([fr.P(s0, L.Z_SILL), fr.P(d0, L.Z_SILL),
                    fr.P(d0, L.Z_HEAD), fr.P(s0, L.Z_HEAD)], uv_shop(fr, s0))
            door_plane(0.0)
            B.face([fr.P(d1, L.Z_SILL), fr.P(s1, L.Z_SILL),
                    fr.P(s1, L.Z_HEAD), fr.P(d1, L.Z_HEAD)], uv_shop(fr, d1))
        else:
            B.face([fr.P(*p) for p in outline], uv_shop(fr, s0))
        return outline

    rev = uv_patch("reveal_light")
    lobby = entrance and lobby_kept(level)
    # The jambs are one quad each; the sill and the head are broken at the
    # lobby's own jambs, because that is where the recess steps back again and
    # the deeper opening's side faces have to meet them on shared vertices.
    for sj in (s0, s1):
        B.face([fr.P(sj, L.Z_SILL), fr.P(sj, L.Z_HEAD),
                fr.P(sj, L.Z_HEAD, -L.GLAZE_DEPTH),
                fr.P(sj, L.Z_SILL, -L.GLAZE_DEPTH)], rev)
    for zz in (L.Z_SILL, L.Z_HEAD):
        for a, b in zip(brk, brk[1:]):
            if entrance and zz == L.Z_SILL and a == d0:
                continue                  # no sill under the entrance unit
            B.face([fr.P(a, zz), fr.P(b, zz),
                    fr.P(b, zz, -L.GLAZE_DEPTH),
                    fr.P(a, zz, -L.GLAZE_DEPTH)], rev)
    if entrance:
        # the plinth's cut ends, each side of the way in
        for dj in (d0, d1):
            B.face([fr.P(dj, zf), fr.P(dj, L.Z_SILL),
                    fr.P(dj, L.Z_SILL, -L.GLAZE_DEPTH),
                    fr.P(dj, zf, -L.GLAZE_DEPTH)], uv_patch("plinth_top"))
    if not lobby:
        if entrance:
            for a, b, fn in ((s0, d0, uv_shop(fr, s0)), (d1, s1, uv_shop(fr, d1))):
                B.face([fr.P(a, L.Z_SILL, -L.GLAZE_DEPTH),
                        fr.P(b, L.Z_SILL, -L.GLAZE_DEPTH),
                        fr.P(b, L.Z_HEAD, -L.GLAZE_DEPTH),
                        fr.P(a, L.Z_HEAD, -L.GLAZE_DEPTH)], fn)
            door_plane(-L.GLAZE_DEPTH)
        else:
            B.face([fr.P(s0, L.Z_SILL, -L.GLAZE_DEPTH),
                    fr.P(s1, L.Z_SILL, -L.GLAZE_DEPTH),
                    fr.P(s1, L.Z_HEAD, -L.GLAZE_DEPTH),
                    fr.P(s0, L.Z_HEAD, -L.GLAZE_DEPTH)], uv_shop(fr, s0))
        return outline

    # the lobby: the glazing each side stays on the shopfront plane and the
    # doors step back again, so the entrance reads as a way in from across a
    # car park rather than as more window
    for a, b, fn in ((s0, d0, uv_shop(fr, s0)), (d1, s1, uv_shop(fr, d1))):
        B.face([fr.P(a, L.Z_SILL, -L.GLAZE_DEPTH),
                fr.P(b, L.Z_SILL, -L.GLAZE_DEPTH),
                fr.P(b, L.Z_HEAD, -L.GLAZE_DEPTH),
                fr.P(a, L.Z_HEAD, -L.GLAZE_DEPTH)], fn)
    # the lobby's sides, split at the sill line like the unit itself: below it
    # the plinth carries on from its cut end back to the doors, above it the
    # light reveal; then its head.
    for dj in (d0, d1):
        for za, zb, fn in ((zf, L.Z_SILL, uv_patch("plinth_top")),
                           (L.Z_SILL, L.Z_HEAD, rev)):
            B.face([fr.P(dj, za, -L.GLAZE_DEPTH), fr.P(dj, zb, -L.GLAZE_DEPTH),
                    fr.P(dj, zb, -L.DOOR_DEPTH), fr.P(dj, za, -L.DOOR_DEPTH)], fn)
    B.face([fr.P(d0, L.Z_HEAD, -L.GLAZE_DEPTH), fr.P(d1, L.Z_HEAD, -L.GLAZE_DEPTH),
            fr.P(d1, L.Z_HEAD, -L.DOOR_DEPTH), fr.P(d0, L.Z_HEAD, -L.DOOR_DEPTH)], rev)
    # its floor slab: the nosing on the wall plane, then the top in two
    # strips, split where the plinth's cut ends stop and the lobby's own
    # sides begin, so each side face meets it on shared vertices (as one
    # face it would carry those two as collinear corners and triangulate
    # with a zero-area triangle)
    floor = uv_lobby_floor(fr, d0)
    B.face([fr.P(d0, 0.0), fr.P(d1, 0.0), fr.P(d1, zf), fr.P(d0, zf)], floor)
    for near, far in ((0.0, -L.GLAZE_DEPTH), (-L.GLAZE_DEPTH, -L.DOOR_DEPTH)):
        B.face([fr.P(d0, zf, near), fr.P(d1, zf, near),
                fr.P(d1, zf, far), fr.P(d0, zf, far)], floor)
    door_plane(-L.DOOR_DEPTH)
    return outline


def wall_layers(band):
    """Two courses: the cladding up to the top of the brickwork, and the band
    of white render that runs along the top of every wall under the eave.

    Both bands start at the ground and carry the plinth themselves, so there
    is exactly one line across a wall, at Z_BRICK. check_layout() keeps every
    opening clear of it: an opening straddling the line would need its casing,
    its reveal and its closure all split there to stay welded to the wall.
    Every panel is cut at that same line whatever it wears, so a brick panel
    and a rendered one meet on shared vertices at the corners.
    """
    return [(0.0, L.Z_BRICK, band), (L.Z_BRICK, Z_TOP, "stucco")]


def uv_return(fr, s, sign):
    """A projecting panel's side: the render band wrapped round the corner from
    its face, U running on from the face's own s (*sign* -1 at its left edge,
    +1 at its right) and V world height, so the concrete plinth in the band's
    foot carries round the corner instead of stopping at it."""
    d = PIER_OUT
    return lambda co: ((s + sign * (d - fr.out_of(co))) * PPM, L.STUCCO_Y0 + co.z * PPM)


def build_pier(B, fr, s0, s1):
    """One projecting render panel, standing on the ground and stopping under
    the eave. Its face samples the render band from the same s as the wall
    does, so its panel joints line up with the band along the top, and its
    sides wrap the band round its corners. A flat reveal patch there put white
    render down to the ground beside the plinth."""
    face = BAND_UV["stucco"](fr)
    top, blank = uv_patch("plinth_top"), uv_patch("blank")
    z0, z1, d = 0.0, PIER_TOP, PIER_OUT
    B.face([fr.P(s0, z0, d), fr.P(s1, z0, d), fr.P(s1, z1, d),
            fr.P(s0, z1, d)], face)
    B.face([fr.P(s1, z0, 0.0), fr.P(s0, z0, 0.0), fr.P(s0, z1, 0.0),
            fr.P(s1, z1, 0.0)], blank)
    B.face([fr.P(s0, z0, 0.0), fr.P(s0, z0, d), fr.P(s0, z1, d),
            fr.P(s0, z1, 0.0)], uv_return(fr, s0, -1.0))
    B.face([fr.P(s1, z0, d), fr.P(s1, z0, 0.0), fr.P(s1, z1, 0.0),
            fr.P(s1, z1, d)], uv_return(fr, s1, 1.0))
    B.face([fr.P(s0, z1, 0.0), fr.P(s0, z1, d), fr.P(s1, z1, d),
            fr.P(s1, z1, 0.0)], top)
    B.face([fr.P(s0, z0, d), fr.P(s0, z0, 0.0), fr.P(s1, z0, 0.0),
            fr.P(s1, z0, d)], blank)
    return B


def build_wall(B, fr, spec, level):
    """One elevation: cladding panels in three courses, holed for every opening.

    A feature's faces are built once, in the layer that owns its sill; each
    layer then takes the feature's rectangle clipped to its own height as a
    hole, a notch in one of its edges, or - where a door runs clean through a
    course - a break that splits the course in two.
    """
    features = []
    for kind, s, z in spec["items"]:
        (ol, orr, ob, ot), _ = item_rects(kind, s, z)
        features.append(dict(l=ol, r=orr, b=ob, t=ot,
                             build=lambda f=(kind, s, z): build_item(
                                 B, fr, f[0], f[1], f[2], level)))
    for s0, s1 in spec["glazing"]:
        f = dict(l=s0, r=s1, b=L.Z_SILL, t=L.Z_HEAD,
                 build=lambda a=s0, b=s1: build_glazing(B, fr, spec, a, b, level))
        if spec.get("entrance"):
            # The entrance unit stands on the ground while the glazing each
            # side stands on the plinth, so the bay is a notch in the wall's
            # foot whose outline steps up from the door to the sill; it
            # carries every vertex the bay's own faces put on it.
            d0, d1 = entrance_span(s0, s1)
            f["b"] = 0.0
            f["notch"] = [(d0, 0.0), (d0, L.Z_SILL), (s0, L.Z_SILL), (s0, L.Z_HEAD),
                          (d0, L.Z_HEAD), (d1, L.Z_HEAD), (s1, L.Z_HEAD),
                          (s1, L.Z_SILL), (d1, L.Z_SILL), (d1, 0.0)]
            zf = lobby_floor_top(spec, level)
            if zf > EPS:
                # the floor slab's nosing puts a corner on each side of the
                # notch's foot
                f["notch"][1:1] = [(d0, zf)]
                f["notch"][-1:-1] = [(d1, zf)]
        features.append(f)
    built = {}

    for s0, s1, band in spec["panels"]:
        mine = [f for f in features if f["l"] > s0 - EPS and f["r"] < s1 + EPS]
        for f in features:
            if (f["l"] < s1 - EPS and s0 + EPS < f["r"]) and f not in mine:
                raise ValueError("%s: an opening crosses a cladding panel edge "
                                 "at s %.2f" % (spec["name"], f["l"]))
        for z0, z1, lband in wall_layers(band):
            uvfn = BAND_UV[lband](fr)
            # what this course must carry on its own bottom and top edges so
            # the course below and above meet it on the same vertices
            cuts_b = sorted({v for f in features for v in (f["l"], f["r"])
                             if f["b"] < z0 - EPS < f["t"] and s0 < v < s1})
            cuts_t = sorted({v for f in features for v in (f["l"], f["r"])
                             if f["b"] < z1 + EPS and f["t"] > z1 - EPS
                             and s0 < v < s1})
            breaks, notch_b, notch_t, holes = [], [], [], []
            for f in mine:
                if f["t"] <= z0 + EPS or f["b"] >= z1 - EPS:
                    continue                      # not in this course at all
                if id(f) not in built:
                    built[id(f)] = f["build"]()
                if f["b"] <= z0 + EPS and f["t"] >= z1 - EPS:
                    breaks.append(f)
                elif f["b"] <= z0 + EPS:
                    notch_b.append(f)
                elif f["t"] >= z1 - EPS:
                    notch_t.append(f)
                else:
                    holes.append(f)
            breaks.sort(key=lambda f: f["l"])
            spans, cursor = [], s0
            for f in breaks:
                spans.append((cursor, f["l"]))
                cursor = f["r"]
            spans.append((cursor, s1))
            for a, b in spans:
                if b - a < 1e-4:
                    continue
                nb = sorted([f for f in notch_b if a - EPS < f["l"]
                             and f["r"] < b + EPS], key=lambda f: f["l"])
                nt = sorted([f for f in notch_t if a - EPS < f["l"]
                             and f["r"] < b + EPS], key=lambda f: f["l"])
                # a course below or above may put vertices on this course's
                # edges; only the ones inside this span belong to it
                cb = [s for s in cuts_b if a + EPS < s < b - EPS]
                ct = [s for s in cuts_t if a + EPS < s < b - EPS]
                outline = [(a, z0)]
                cur = a
                for f in nb:
                    outline += [(s, z0) for s in cb if cur < s < f["l"] - EPS]
                    outline += f.get("notch") or [
                        (f["l"], z0), (f["l"], min(f["t"], z1)),
                        (f["r"], min(f["t"], z1)), (f["r"], z0)]
                    cur = f["r"]
                outline += [(s, z0) for s in cb if s > cur + EPS]
                outline += [(b, z0), (b, z1)]
                cur = b
                for f in reversed(nt):
                    outline += [(s, z1) for s in ct if f["r"] + EPS < s < cur]
                    outline += [(f["r"], z1), (f["r"], max(f["b"], z0)),
                                (f["l"], max(f["b"], z0)), (f["l"], z1)]
                    cur = f["l"]
                outline += [(s, z1) for s in reversed(ct) if s < cur - EPS]
                outline += [(a, z1)]
                hl = []
                for f in holes:
                    if a - EPS < f["l"] and f["r"] < b + EPS:
                        hl.append(built[id(f)] if id(f) in built else
                                  [(f["l"], f["b"]), (f["r"], f["b"]),
                                   (f["r"], f["t"]), (f["l"], f["t"])])
                fill_region(B, fr, SB.dedupe(outline), hl, uvfn)


def main_body(level):
    """The wall ring, capped by a floor on the ground and a lid at the wall
    top: both end up buried, the floor under the slab and the lid inside the
    roof, but the solid must be closed for the boolean to be exact."""
    B = Builder()
    for spec in WALLS:
        build_wall(B, Frame(spec["p0"], spec["p1"]), spec, level)
    SB.close_solid(B, uv_patch("blank"))
    return B


def piers():
    """Every wall's ornament panels, as separate solids for the union."""
    out = []
    for spec in WALLS:
        fr = Frame(spec["p0"], spec["p1"])
        for i, (s0, s1) in enumerate(spec.get("piers", ())):
            out.append((build_pier(Builder(), fr, s0, s1),
                        "tmp_pier_%s%d" % (spec["name"], i)))
    return out


# ================================================================== roof
# The deck and the eave are one surface, not two: the deck is the high side and
# the skirt folds down from it at the wall line. Built as two solids they would
# meet tangentially along that fold, which is the case an exact boolean handles
# worst -- it left the fold non-manifold and, in one configuration, silently
# dropped other operands. Built as one closed solid they simply share vertices.
def _mitres(loop, closed=True):
    """Per-vertex offset directions, so a profile swept along *loop* mitres at
    its corners and every point still lies the intended distance out from each
    edge it belongs to. A vertex between two collinear edges gets the plain
    edge normal, which is what a breakpoint in a straight run needs."""
    n = len(loop)
    norms = []
    for k in range(n if closed else n - 1):
        a, b = loop[k], loop[(k + 1) % n]
        t = Vector((b[0] - a[0], b[1] - a[1])).normalized()
        norms.append(Vector((t.y, -t.x)))
    out = []
    for k in range(n):
        if not closed and k == 0:
            out.append(norms[0])
        elif not closed and k == n - 1:
            out.append(norms[-1])
        else:
            n1, n2 = norms[k - 1], norms[k % len(norms)]
            out.append((n1 + n2) / (1.0 + n1.dot(n2)))
    return out


def _roof_loop():
    """The wall outline, carrying the loading bay's two corners, where the
    roof's underside is broken into separate faces."""
    return [(-HX, -HY), (BAY_X, -HY), (HX - CHAMFER, -HY),
            (HX, -HY + CHAMFER), (HX, HY), (BAY_X, HY), (-HX, HY),
            (-HX, BAY_Y)]


def roof():
    """The flat roof and its eave as one closed solid.

    Top: the deck, then the skirt folding down and out from the wall line to
    the fascia. Outer: the fascia. Bottom: the soffit back to the wall line,
    then the underside, whose face over the loading bay is that bay's ceiling.
    The skirt is sheeted the whole way round, the entrance included: its top
    face and the fascia sample the eave band's seamed strip along the run,
    measured from the start of each straight side, so a side broken at the
    loading bay's corner carries one run of seams, and the soffit the whole
    band from its own edge's start, as before.
    """
    B = Builder()
    loop = _roof_loop()
    md = _mitres(loop, closed=True)
    n = len(loop)
    out = [(Vector(loop[k]) + md[k] * L.EAVE_OUT) for k in range(n)]

    def side_start(k):
        """The first vertex of the straight side edge *k* belongs to."""
        while True:
            a, b, c = loop[(k - 1) % n], loop[k], loop[(k + 1) % n]
            if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > EPS:
                return b
            k -= 1

    B.face([(x, y, L.Z_DECK) for x, y in loop], uv_deck)
    for k in range(n):
        p0, p1 = loop[k], loop[(k + 1) % n]
        q0, q1 = out[k], out[(k + 1) % n]
        fr = Frame(p0, p1)
        run = Frame(side_start(k), p1)
        top, under, edge = uv_skirt_top(run), uv_soffit(fr), uv_fascia(run)
        B.face([(p0[0], p0[1], L.Z_DECK), (p1[0], p1[1], L.Z_DECK),
                (q1.x, q1.y, L.Z_EAVE_T), (q0.x, q0.y, L.Z_EAVE_T)], top)
        B.face([(q0.x, q0.y, L.Z_EAVE_T), (q1.x, q1.y, L.Z_EAVE_T),
                (q1.x, q1.y, L.Z_EAVE_B), (q0.x, q0.y, L.Z_EAVE_B)], edge)
        B.face([(q0.x, q0.y, L.Z_EAVE_B), (q1.x, q1.y, L.Z_EAVE_B),
                (p1[0], p1[1], L.Z_WALL), (p0[0], p0[1], L.Z_WALL)], under)

    # the underside, in three pieces so the loading bay's ceiling is its own
    # face; every piece carries the breakpoints its neighbours put on it
    z = L.Z_WALL
    bay = [(-HX, -HY), (BAY_X, -HY), (BAY_X, BAY_Y), (-HX, BAY_Y)]
    west = [(-HX, BAY_Y), (BAY_X, BAY_Y), (BAY_X, HY), (-HX, HY)]
    main = [(BAY_X, -HY)] + loop[2:6] + [(BAY_X, BAY_Y)]
    blank = uv_patch("blank")
    B.face([(x, y, z) for x, y in reversed(bay)], uv_bay_ceiling)
    B.face([(x, y, z) for x, y in reversed(west)], blank)
    B.face([(x, y, z) for x, y in reversed(main)], blank)
    return B


def placard():
    """The lit sign standing on the eave over the entrance."""
    B = Builder()
    fr = Frame(OUTLINE[CHAMFER_EDGE], OUTLINE[CHAMFER_EDGE + 1])
    s0 = (CHAMFER_LEN - L.SIGN_W) / 2.0
    s1 = s0 + L.SIGN_W
    z0, z1 = L.Z_SIGN, L.Z_SIGN + L.SIGN_H
    # planted on the eave's slope, its foot a little below the surface so the
    # union buries it and the sign reads as standing on the roof
    out1 = L.EAVE_OUT - 0.12
    out0 = out1 - L.SIGN_T
    edge = uv_patch("sign_edge")
    x, y, w, h = L.PLACARD
    face = lambda co: (x + (fr.s_of(co) - s0) / L.SIGN_W * w,  # noqa: E731
                       y + (co.z - z0) / L.SIGN_H * h)
    B.face([fr.P(s0, z0, out1), fr.P(s1, z0, out1),
            fr.P(s1, z1, out1), fr.P(s0, z1, out1)], face)
    B.face([fr.P(s1, z0, out0), fr.P(s0, z0, out0),
            fr.P(s0, z1, out0), fr.P(s1, z1, out0)], edge)
    for a, b, o0, o1 in ((s0, s0, out0, out1), (s1, s1, out1, out0)):
        B.face([fr.P(a, z0, o0), fr.P(b, z0, o1),
                fr.P(b, z1, o1), fr.P(a, z1, o0)], edge)
    B.face([fr.P(s0, z1, out0), fr.P(s0, z1, out1),
            fr.P(s1, z1, out1), fr.P(s1, z1, out0)], edge)
    B.face([fr.P(s0, z0, out1), fr.P(s0, z0, out0),
            fr.P(s1, z0, out0), fr.P(s1, z0, out1)], edge)
    return B


# ================================================================== extras
def column():
    """The steel column at the loading bay's open corner, which is what carries
    the roof where two walls have been taken away."""
    steel = uv_patch("column")
    return SB.box(Builder(), -HX, -HX + COLUMN, -HY, -HY + COLUMN, 0.0, Z_TOP,
                  steel, steel, steel)


def _region_uv(rect, u0, uw, v0, vh, axis):
    x, y, w, h = rect
    return lambda co: (x + (getattr(co, axis) - u0) / uw * w,
                       y + (co.z - v0) / vh * h)


def drum(cx, cy, r, z0, z1, sides=8):
    """A roof fan or a vent pipe: a prism, closed top and bottom."""
    x, y, w, h = L.COWL if r > 0.25 else L.PIPE
    side = lambda co: (x + w * ((math.atan2(co.y - cy, co.x - cx)  # noqa: E731
                                / (2 * math.pi)) % 1.0),
                       y + h * (co.z - z0) / (z1 - z0))
    top = uv_patch("cap") if r <= 0.25 else None
    x2, y2, w2, h2 = L.AHU_TOP
    lid = (lambda co: (x2 + w2 * 0.5, y2 + h2 * 0.5)) if top is None else top
    return SB.prism(Builder(), SB.circle(cx, cy, r, sides, 0.0), z0, z1, side, lid,
                    uv_patch("blank"))


def plant_parts(level):
    """Air handlers, fan cowls and vent pipes on the deck."""
    out = []
    deck = L.Z_DECK - 0.09          # sunk a little, so the boolean has depth
    for i, item in enumerate(PLANT):
        kind = item[0]
        if not plant_kept(level, kind):
            continue
        if kind == "box":
            (cx, cy), (w, d), h = item[1], item[2], item[3]
            xs, ys, zs = L.AHU_SIDE, L.AHU_TOP, None
            side = _region_uv(xs, cx - w / 2, w, deck, h + 0.09, "x")
            top = lambda co, r=ys, cx=cx, cy=cy, w=w, d=d: (  # noqa: E731
                r[0] + (co.x - (cx - w / 2)) / w * r[2],
                r[1] + (co.y - (cy - d / 2)) / d * r[3])
            out.append((SB.box(Builder(), cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2,
                               deck, deck + h + 0.09, side, top, uv_patch("blank")),
                        "tmp_ahu%d" % i))
        else:
            (cx, cy), r, h = item[1], item[2], item[3]
            out.append((drum(cx, cy, r, deck, deck + h + 0.09,
                             8 if r > 0.25 else 6), "tmp_%s%d" % (kind, i)))
    return out


# ================================================================== assembly


def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    # The column is kept on every tier: a consumer switching by screen size
    # shows LOD3 from about 280 m, where the eave corner over the loading bay
    # left standing on nothing read at eye level as a missing support.
    parts = [to_object(roof(), "tmp_roof"),
             to_object(placard(), "tmp_sign"),
             to_object(column(), "tmp_column")]
    for B, name in piers():
        parts.append(to_object(B, name))
    for B, name in plant_parts(level):
        parts.append(to_object(B, name))
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # 1e-4 rather than 1e-5: the exact boolean resolves this building's 32 m
    # eave lines in 32-bit floats and leaves the odd corner vertex a hundredth
    # of a millimetre off its neighbour, which exports as two vertices and
    # reads as a non-manifold seam downstream. The smallest authored feature
    # here is the shopfront mullion's 0.09 m, so a 0.1 mm weld cannot reach it.
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # Recover the cost of coplanar boolean subdivisions. Keep UV and
        # material seams and every architectural edge; 0.001 radians tolerates
        # float noise on nominally planar faces.
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    RS.append(obj, kit(level), check=True)
    return obj


# ================================================================== checks
def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    for spec in WALLS:
        fr = Frame(spec["p0"], spec["p1"])
        if abs(spec["panels"][-1][1] - fr.L) > 1e-6:
            bad.append("%s: panels cover %.4f m of a %.4f m wall"
                       % (spec["name"], spec["panels"][-1][1], fr.L))
        for a, b in zip(spec["panels"], spec["panels"][1:]):
            if abs(a[1] - b[0]) > 1e-9:
                bad.append("%s: a gap between panels at s %.3f"
                           % (spec["name"], a[1]))
        for s0, s1 in spec["glazing"]:
            if not any(p[0] - EPS < s0 and s1 < p[1] + EPS
                       for p in spec["panels"]):
                bad.append("%s: a shopfront bay crosses a panel edge"
                           % spec["name"])
        for ps0, ps1 in spec.get("piers", ()):
            if ps0 < 0.3 or ps1 > fr.L - 0.3:
                bad.append("%s: an ornament panel reaches a wall corner"
                           % spec["name"])
            for k, s, z in spec["items"]:
                o = item_rects(k, s, z)[0]
                if ps0 < o[1] and o[0] < ps1:
                    bad.append("%s: an ornament panel covers an opening"
                               % spec["name"])
            for gs0, gs1 in spec["glazing"]:
                if ps0 < gs1 and gs0 < ps1:
                    bad.append("%s: an ornament panel covers a shopfront bay"
                               % spec["name"])
        rects = [item_rects(k, s, z)[0] for k, s, z in spec["items"]]
        rects += [(a, b, L.Z_SILL, L.Z_HEAD) for a, b in spec["glazing"]]
        for _l, _r, ob, ot in rects:
            if ob < L.Z_BRICK - EPS < ot:
                bad.append("%s: an opening straddles the cladding line at "
                           "z %.4f; see wall_layers()" % (spec["name"], L.Z_BRICK))
        if spec.get("entrance") and s1 - s0 < L.DOOR_UNIT_W + 0.4:
            bad.append("%s: no room for the entrance in its bay" % spec["name"])
    ring = [tuple(round(v, 6) for v in w["p0"]) for w in WALLS]
    for a, b in zip(WALLS, WALLS[1:] + WALLS[:1]):
        fr = Frame(a["p0"], a["p1"])
        if tuple(round(v, 6) for v in a["p1"]) != tuple(round(v, 6) for v in b["p0"]):
            bad.append("the wall ring breaks between %s and %s"
                       % (a["name"], b["name"]))
    if len(set(ring)) != len(ring):
        bad.append("the wall ring visits a corner twice")
    door = L.OPENINGS["service_door"][1]
    if not 2.0 <= door <= 2.4:
        bad.append("the service door's leaf is %.2f m, outside 2.0-2.4" % door)
    if not 2.0 <= L.Z_TRANSOM <= 2.4:
        bad.append("the entrance leaf is %.2f m, outside 2.0-2.4" % L.Z_TRANSOM)
    if L.Z_HEAD <= L.Z_TRANSOM:
        bad.append("the entrance has no transom above its leaves")
    # the lobby's floor slab: over the terrain but no step, on its own atlas
    # region, on every tier that keeps the lobby and no other
    if not 0.01 <= L.LOBBY_FLOOR_T <= 0.03:
        bad.append("the lobby's floor is %.3f m over the ground, outside 0.01-0.03"
                   % L.LOBBY_FLOOR_T)
    for lv in LEVELS:
        if lobby_kept(lv) != (item_mode(lv) != "flush"):
            bad.append("LOD%d keeps the entrance's recess without its lobby, "
                       "or the other way round: the floor slab expects both" % lv)
    if abs(L.LOBBY_FLOOR[2] - L.DOOR_UNIT_W * PPM) > 1e-6 or \
            abs(L.LOBBY_FLOOR[3] - (L.LOBBY_FLOOR_T + L.DOOR_DEPTH) * PPM) > 1e-6:
        bad.append("the lobby floor's atlas region is not the slab's nosing and top")
    if L.Z_EAVE_B >= L.Z_WALL:
        bad.append("the eave rises outward instead of falling; snow pushed off "
                   "the deck would have nowhere to go")
    if L.Z_EAVE_B <= L.Z_HEAD + 0.4:
        bad.append("the eave's outer edge comes down to %.3f m, into the "
                   "shopfront head at %.3f m" % (L.Z_EAVE_B, L.Z_HEAD))
    if L.Z_SIGN + L.SIGN_H <= L.Z_DECK:
        bad.append("the sign does not stand above the roof deck")
    if not L.Z_WALL < PIER_TOP < L.Z_DECK - PIER_OUT * FALL:
        bad.append("the ornament panels reach %.4f m, which is not strictly "
                   "inside the eave between its soffit at %.4f m and its top "
                   "at %.4f m, so the union cannot trim them cleanly"
                   % (PIER_TOP, L.Z_WALL, L.Z_DECK - PIER_OUT * FALL))
    a, b = OUTLINE[CHAMFER_EDGE], OUTLINE[CHAMFER_EDGE + 1]
    if abs(abs(b[0] - a[0]) - abs(b[1] - a[1])) > 1e-9:
        bad.append("CHAMFER_EDGE %d is not the 45 degree cut, so the entrance's "
                   "sign would land on a straight wall instead"
                   % CHAMFER_EDGE)
    for item in PLANT:
        (cx, cy) = item[1]
        if not (-HX + 1.5 < cx < HX - 1.5 and -HY + 1.5 < cy < HY - 1.5):
            bad.append("plant at %s stands over the eave" % (item[1],))
    # the wall ladder: clear of the rear wall's corners, openings and render
    # panels; under the eave's lowest edge; short enough to need no cage
    avoid = [(k,) + tuple(item_rects(k, s, z)[0][:2]) for k, s, z in REAR["items"]]
    avoid += [("render panel", s0, s1) for s0, s1 in REAR["piers"]]
    bad += RS.problems(WALL_LADDER, "the wall ladder", avoid)
    if WALL_LADDER.length > RS.CAGE_LADDER:
        bad.append("the wall ladder is %.2f m long and needs a cage" % WALL_LADDER.length)
    return bad


def check_roof(obj):
    """Nothing but the plant, the sign and the wall ladder's top stands above
    the roof deck."""
    over = [v.co for v in obj.data.vertices if v.co.z > L.Z_DECK + 1e-4]
    return len(over)


# ================================================================== build
def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame.

    The footprint is the wall ring itself, so the loading bay's notch is out
    of it: the roof passes over the bay, but its two walls are outer walls and
    the column at its open corner is a post, not a wall. The entrance is given
    on the chamfer's wall plane, though the shopfront stands GLAZE_DEPTH back
    in it and the doors DOOR_DEPTH. Its threshold is the pavement (the
    lobby's 0.02 m floor slab is a floor finish, not a step) and its
    height runs from there to the transom bar; the pair is the two sliding
    leaves without the fixed screens at their sides.
    One retail storey, floored at the ground the service and goods doors
    open onto.
    """
    ring = [w["p0"] for w in WALLS]
    area = abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(ring, ring[1:] + ring[:1]))) / 2.0
    names = {("chamfer", 0): ("main", "entrance"), ("bay_rear", 0): ("loading", "vehicle"),
             ("bay_east", 0): ("loading_staff", "service"),
             ("rear", 0): ("staff", "service")}
    doors = []
    for spec in WALLS:
        found = [(k, s, z) + L.OPENINGS[k][:2] for k, s, z in spec["items"]
                 if k.endswith("_door")]
        if spec.get("entrance"):
            s0, s1 = spec["glazing"][0]
            found.append(("entrance", (s0 + s1) / 2.0, 0.0,
                          2 * ENTRANCE_LEAF, L.Z_TRANSOM))
        for i, (kind, s, z, w, h) in enumerate(found):
            doors.append(model_facts.wall_door(
                *names[(spec["name"], i)], spec["p0"], spec["p1"], s, z, w, h,
                main=kind == "entrance"))
    return {"hero": False, "dwellings": 0, "footprint": ring,
            "storeys": [(0.0, area)], "doors": doors}


# One sliding leaf of the entrance, as facade_atlas.paint_door_unit() draws
# the pair: meeting on the centre line, a 0.35 m fixed screen outside each.
ENTRANCE_LEAF = 1.2

# ================================================================ previews


def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views (shell_build.render_views()), plus the same
    aerial from behind and one low off the loading bay's corner: this type's
    bay is on the elevation the first misses. Working views only - not
    committed."""
    return SB.render_views(BUILD, out_dir, level, res, views=(
        SB.AERIAL, SB.AERIAL_REAR, SB.orbit("aerial_bay", (-1.2, -1.0, 0.9))))


if __name__ == "__main__":
    BUILD.main(build_all, facts)
