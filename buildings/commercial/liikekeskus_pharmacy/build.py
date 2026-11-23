# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of liikekeskus_pharmacy, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A free-standing neighbourhood pharmacy in a car park: one shop under one
roof, behind one door. The plan is a 24 x 16 m rectangle and the roof is a single
gable whose ridge runs front to back, so the whole of the front is one wide
gable end. It overhangs 1.2 m at the rakes and 0.9 m at the eaves, in white
boarded soffit behind a white fascia, and that deep white A over coursed stone
is what the type is recognised by.

The front is two 9 m display windows either side of a 2.8 m stone pier that
runs from the pavement to the apex. The shop's one door goes through the foot
of that pier, on the building's centre line, under a lit plaque with the
pharmacy mark; a green sign board over each window carries the name once and
the mark once. Above the boards the gable opens into two raking curtain-wall
panels either side of the pier. A white crest caps the ridge from rake to
rake, and the pharmacy's sign stands on it above the pier, a lit cube on four
steel legs.

The display windows and the door stand 0.18 m back in their openings, on the
ground, and the door 0.43 m back from the pier's face: each set-back stands on
a 0.02 m concrete floor slab (scripts/door_floor.py), the windows' and the
door's in the wall, the portal's in the pier, so no terrain shows inside.

Construction is a set of closed solids unioned with Blender's exact boolean:
the wall ring, the roof, the ridge crest, the middle pier, the plaque over the
door, the sign and its stand, the wall-hung air handler, the roof stacks, the
four downpipes (scripts/downpipes.py) and the roof safety kit
(scripts/roof_safety.py). Each is simple on its own; the union is what trims the wall tops into the roof and leaves the boundary of one empty volume,
so interior geometry cannot occur. The wall ring is capped at the top by two
planar faces rather than one, split at the ridge -- the rim follows the gable
and a single n-gon across it would not be flat.

Every number the mesh and the atlas share is imported from facade_atlas.py
rather than written here a second time.
"""

import functools
import importlib
import math
import os
import sys

import bmesh


HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import facade_atlas as L  # noqa: E402  (layout constants shared with the atlas)
importlib.reload(L)       # an interactive session must not keep a stale layout

ASSET = L.ASSET
EXPORT_DIR = os.path.join(HERE, "export")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import door_floor as DF  # noqa: E402
import downpipes as DP  # noqa: E402
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
HX, HY = L.HX, L.HY                     # 12 x 8: a 24 x 16 m plan
XE, YE = HX + L.EAVE_OUT, HY + L.RAKE_OUT      # the roof's own extent
COS = 1.0 / math.hypot(1.0, L.SLOPE)           # run -> slope length
SLOPE_LEN = (XE / COS)                          # eave edge to ridge, 14.147 m

# The stone band repeats every 4 m, so a gable elevation is cut into courses
# at its multiples and each course indexes the band from its own base.
CUT = L.STONE_WRAP                              # 4.0
Z_CUT = 2.0 * CUT                               # 8.0, the second wrap line


def gunder(s):
    """Roof underside over a gable elevation, in that elevation's own s."""
    return L.Z_EAVE + L.SLOPE * (HX - abs(s - HX))


def gtop(s):
    """Where a gable wall stops: inside the roof slab, never touching it."""
    return gunder(s) + L.WALL_INTO_ROOF


def s_at(z):
    """Distance from the middle of a gable elevation at which gtop is *z*."""
    return HX - (z - L.WALL_INTO_ROOF - L.Z_EAVE) / L.SLOPE


def gglass(s):
    """Head of the gable curtain wall: under the rake, then capped flat."""
    return min(L.GABLE_HEAD_CAP, gunder(s) - L.GABLE_HEAD_DROP)


# The three piers of the front, and which of their vertical edges carry the
# shopfront head as a breakpoint: the two corner piers meet a side wall that
# has no such break, and putting one there would leave a T-junction.
PIER_BREAK = {i: (i > 0, i < len(L.PIERS) - 1) for i in range(len(L.PIERS))}
MID_PIER = next(i for i, (a, b) in enumerate(L.PIERS)
                if a < L.ENTRANCE_S < b)

# The entrance, as a rectangle in the front's (s, z), and the portal through
# the middle pier round it.
DOOR_RECT = (L.ENTRANCE_S - L.ENTRANCE_W / 2.0, L.ENTRANCE_S + L.ENTRANCE_W / 2.0,
             0.0, L.Z_HEAD)
PORTAL_RECT = (L.ENTRANCE_S - L.PORTAL_W / 2.0, L.ENTRANCE_S + L.PORTAL_W / 2.0,
               0.0, L.PORTAL_HEAD)


def opening_mode(level, where):
    """Whether an opening is cut into the wall or painted flat on it.

    Every opening is cut through LOD1 and painted flat from LOD2, the catalog
    default. The side windows, the back door and the louvres once went flat
    a tier early, to keep LOD1 from coming out the same as LOD0; the roof
    safety kit's thinned rungs now make that reduction, and the side
    windows' reveals going flat was the one change seen at the LOD0/LOD1
    switch. *where* is kept for the front, which could differ again.
    """
    return "cut" if level < 2 else "flush"


def floored(level):
    """Whether the shopfront's and the door's set-backs stand on their floor
    slabs at *level*: on every tier that cuts them (opening_mode()); a flush
    opening has no reveal to floor. The portal's slab is the pier's, on every
    tier that keeps the pier."""
    return opening_mode(level, "front") == "cut"


def pier_kept(level):
    """The middle pier stands 0.25 m proud and carries the apex, so it is the
    one piece of relief that shapes the gable rather than decorating it. At
    LOD3 the 0.25 m is well under a pixel and the stone behind it is the same
    colour, so it flattens without changing what the elevation reads as."""
    return level < 3


def ahu_kept(level):
    return level < 3


def buttress_kept(level):
    """The side buttresses are the wall's own stone, so losing them costs no
    colour, only the shadow line of a 0.30 m projection. That is still worth
    having at LOD1; past 70 m it is under a pixel and the elevations are flat
    anyway."""
    return level < 2


def vent_kept(level, kind):
    """Both kinds break the ridge line seen from anywhere raised.

    The pipes are only 0.3 m across, but LOD1 starts at 35 m and there they
    are still two or three pixels of dark against a pale sky: dropping them at
    that switch was the one change visible in the comparison, so they carry to
    LOD1 and go at LOD2. The boxes are three times the size and stay on every
    tier: at the 206 m switch they were still two dark bumps on the roofline
    and a dark square on the right slope, and their going showed. A box is
    four-sided on every tier anyway, about 20 triangles after the union.
    """
    return kind == "box" or level < 2


# ============================================ rainwater goods and roof kit
# The two side walls are the eaves, walked anticlockwise seen from above, as
# scripts/downpipes.py and scripts/roof_safety.py take them: s runs from the
# front along the right (+X) wall and from the back along the left (-X) one.
RIGHT = ((HX, -HY), (HX, HY))
LEFT = ((-HX, HY), (-HX, -HY))
Z_FASCIA_FOOT = L.roof_under(XE)              # 3.595, the soffit at the fascia
Z_EDGE = Z_FASCIA_FOOT + L.ROOF_T             # 3.97, the sheet at the eave edge

# Downpipes: one at each end of each eave's gutter, 0.5 m in from the corner,
# where both ends are clear of the windows, the buttresses and the air
# handler. The rakes carry no gutter, so the gables carry no pipes.
DOWNPIPE_SPOTS = (("right front", RIGHT, 0.5), ("right rear", RIGHT, 15.5),
                  ("left rear", LEFT, 0.5), ("left front", LEFT, 15.5))
DOWNPIPES = [DP.eave_pipe(p0, p1, s, L.Z_EAVE, L.SLOPE, L.EAVE_OUT)
             for _n, (p0, p1), s in DOWNPIPE_SPOTS]

# Roof safety kit, the way to the two ventilation housings and the sign on
# the ridge. The entrance is in the front gable and the catalog view looks at
# the right side, so the wall ladder stands on the left eave wall's rear
# half, between the rear downpipe and the first window, and passes outside
# the eave. The roof ladder runs up the left slope above it to 0.75 m short
# of the ridge, where a walkway along the slope just under the crest takes it
# forward to behind the sign. A second walkway leaves the roof ladder at the
# left housing's level and stops beside it. The right housing is on the
# other slope: a short roof ladder runs down beside it from the crest,
# reached over the crest from the ridge walkway. The eave's z_wall is the
# soffit at the fascia, not at the wall: the soffit falls 0.45 m per metre
# outward, and the wall ladder's brackets run out under all of it.
PAINT = RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)
EAVE_LEFT = RS.Eave(*LEFT, Z_FASCIA_FOOT, L.EAVE_OUT, Z_EDGE, L.SLOPE)
KIT_S = 1.8                                   # left wall, s = HY - y: y = 6.2
RIDGE_OUT = -(HX - 0.75)                      # 0.75 m from the ridge line
WALL_LADDER = RS.WallLadder(EAVE_LEFT, KIT_S)
ROOF_LADDER = RS.RoofLadder(EAVE_LEFT, KIT_S, EAVE_LEFT.roof_z(RIDGE_OUT))
SIGN_BACK = L.SIGN["y"] + L.SIGN["d"] / 2.0 + 0.2         # y, behind the sign
RIDGE_WALK = RS.Walkway(EAVE_LEFT, KIT_S - RS.HALF, HY - SIGN_BACK,
                        ROOF_LADDER.top_out())
_kind, (BOX_LX, BOX_LY), BOX_LW, _h = L.VENTS[0]
BOX_WALK = RS.Walkway(EAVE_LEFT, KIT_S + RS.HALF + 0.03,
                      HY - (BOX_LY + BOX_LW / 2.0 + 0.2),
                      -HX - BOX_LX + RS.WALK_W / 2.0)      # centred on the box
_kind, (BOX_RX, BOX_RY), BOX_RW, _h = L.VENTS[1]
BOX_LADDER_S = HY + BOX_RY + BOX_RW / 2.0 + 0.2 + RS.HALF  # right wall, s = y + HY
# the ladder's own eave: an edge on the slope 0.15 m below the housing's
# downslope side, which the module takes the ladder's foot from
_foot = BOX_RX + BOX_RW / 2.0 + 0.15 - HX
EAVE_BOX = RS.Eave(*RIGHT, Z_FASCIA_FOOT, _foot + RS.ROOF_START * COS,
                   L.roof_under(HX + _foot + RS.ROOF_START * COS) + L.ROOF_T,
                   L.SLOPE)
# it climbs to 0.45 m from the ridge line, 0.15 m short of the crest's side,
# where the climber steps over the crest to the ridge walkway
BOX_LADDER = RS.RoofLadder(EAVE_BOX, BOX_LADDER_S, EAVE_BOX.roof_z(-(HX - 0.45)))
KIT = [WALL_LADDER, ROOF_LADDER, RIDGE_WALK, BOX_WALK, BOX_LADDER]

# The kit's tiers, LOD0 to LOD3, (rungs, fittings): roof_safety.MODES but
# thinner past LOD0, since 13 m of roof ladder and 15 m of walkway are a lot
# of kit for a one-storey shop. Brackets and walkway posts are 4 cm, under a
# pixel at the 46 m switch, so LOD1 keeps every other rung without them;
# LOD2 keeps every eighth rung, the rails' outline being what reads at 103 m,
# where a rung is a fifth of a pixel. LOD3 drops the rungs and the fittings
# and keeps bare rails and the ridge plank (kit()).
KIT_MODES = ((1, True), (2, False), (8, False), (None, False))


def kit(level, extents=False):
    """The roof safety kit's solids for this tier, thinned by KIT_MODES.

    With *extents*, for the tier that drops the kit: the wall ladder's bare
    rails, which set the building's -X extent, and, because at the 206 m
    switch the white rails of the two roof ladders and the ridge walkway's
    plank still read against the dark roof and their going showed, those
    too, as bare three-sided rails and the plank alone. None of them touches
    anything, so they are appended after the weld rather than unioned. The
    short housing walkway, behind the ridge from every street view, goes."""
    if extents:
        return (RS.solids([WALL_LADDER], level, PAINT, extents=True,
                          modes=KIT_MODES)
                + [(ROOF_LADDER.solid(PAINT, None, False), "tmp_far_ladder"),
                   (BOX_LADDER.solid(PAINT, None, False), "tmp_far_box_ladder"),
                   (RIDGE_WALK.solid(PAINT, None, False)[0], "tmp_far_walk")])
    return RS.solids(KIT, level, PAINT, modes=KIT_MODES)


def kit_plan():
    """(name, x0, x1, y0, y1) plan rectangle of each piece on the roof."""
    def ladder(eave, lad, sign):
        top = lad.top_out()
        foot = eave.eave_out - RS.ROOF_START * COS
        y = (HY - lad.s) if sign < 0 else (lad.s - HY)
        xs = sorted((sign * (HX + foot), sign * (HX + top)))
        return xs + [y - RS.HALF, y + RS.HALF]

    def walk(w):
        xs = sorted((-HX - w.out_lo, -HX - w.out_hi))
        return xs + sorted((HY - w.s0, HY - w.s1))
    return [("roof ladder", *ladder(EAVE_LEFT, ROOF_LADDER, -1)),
            ("ridge walkway", *walk(RIDGE_WALK)),
            ("housing walkway", *walk(BOX_WALK)),
            ("housing ladder", *ladder(EAVE_BOX, BOX_LADDER, 1))]


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.

def uv_stone(fr, zbase=0.0):
    return lambda co: (fr.s_of(co) * PPM, L.STONE_Y0 + (co.z - zbase) * PPM)


def uv_patch(name):
    return SB.uv_patch(L.PATCHES[name])


def uv_shop(fr, s0, s1=None, flip=False):
    """A glazed run. *flip* measures the lights back from s1 instead, which
    is how the part light in a run that does not divide evenly is kept at the
    pier end rather than left beside a door."""
    if flip:
        return lambda co: ((s1 - fr.s_of(co)) * PPM, L.SHOP_Y0 + co.z * PPM)
    return lambda co: ((fr.s_of(co) - s0) * PPM, L.SHOP_Y0 + co.z * PPM)


def uv_door(fr, s0):
    x, y, w, h = L.DOOR_DOUBLE
    return lambda co: (x + (fr.s_of(co) - s0) * PPM, y + co.z * PPM)


def uv_fascia(fr, key, s0):
    x, y, w, h = L.FASCIA[key]
    return lambda co: (x + (fr.s_of(co) - s0) * PPM,
                       y + (co.z - L.Z_HEAD) * PPM)


def uv_reveal(fr, edge, zbase=0.0):
    """The cheek of an opening, in the wall's own stone.

    The surface is unrolled round the corner: a point *d* deep in the reveal
    takes the artwork that would have been *d* further along the wall in the
    direction the opening lies, so the coursing runs on into the cheek instead
    of restarting. Offsetting perpendicular to the edge handles a jamb, a head
    and a sill with one expression, and a raking head as well.
    """
    (s0, z0), (s1, z1) = edge
    ds, dz = s1 - s0, z1 - z0
    ln = math.hypot(ds, dz) or 1.0
    ns, nz = -dz / ln, ds / ln

    def f(co):
        d = -fr.out_of(co)                  # 0 at the wall face, + into it
        return ((fr.s_of(co) + ns * d) * PPM,
                L.STONE_Y0 + (co.z + nz * d - zbase) * PPM)
    return f


def uv_return(fr, s_edge, sign, zbase=0.0):
    """The side of something standing proud of the wall - a buttress, the
    middle pier - with the coursing carried on round its corner."""
    return lambda co: ((s_edge + sign * fr.out_of(co)) * PPM,
                       L.STONE_Y0 + (co.z - zbase) * PPM)


def uv_region(fr, rect, s0, z0, ppm=PPM, flip=False):
    return SB.uv_region(fr, rect, s0, z0, ppm, flip)


def uv_roof(left):
    x, y, w, h = L.ROOF
    def f(co):
        u = (co.y + YE) if left else (YE - co.y)
        return (x + u * L.ROOF_PPM,
                y + (XE - abs(co.x)) / COS * L.ROOF_PPM)
    return f


def uv_soffit_x(co):
    """The eave soffit: v runs out from the side wall."""
    return (co.y * PPM,
            L.SOF_Y0 + L.SOF_FASCIA + (abs(co.x) - HX) * PPM)


def uv_soffit_y(co):
    """The rake soffit: v runs out from the gable wall."""
    return (co.x * PPM,
            L.SOF_Y0 + L.SOF_FASCIA + (abs(co.y) - HY) * PPM)


def uv_eave_fascia(x):
    z0 = L.roof_under(x)
    return lambda co: (co.y * PPM, L.SOF_Y0 + (co.z - z0) * PPM)


def uv_rake_board(co):
    """The rake board: the fascia rows under the gutter, which the rakes do
    not carry, stretched over the board's depth."""
    return (co.x / COS * PPM, L.SOF_Y0 + (co.z - L.roof_under(co.x))
            / L.ROOF_T * L.RAKE_ROWS)


def uv_plaque(x0, z0):
    """The plaque over the door: LOGO squeezed onto DOOR_SIGN's square."""
    x, y, w, h = L.LOGO
    sx, sz = w / L.DOOR_SIGN["w"], h / L.DOOR_SIGN["h"]
    return lambda co: (x + (co.x - x0) * sx, y + (co.z - z0) * sz)


def uv_logo(axis, origin):
    """One face of the ridge sign. All four take the same square region; the
    mark is symmetric about its upright, so the two faces that run along y
    need no mirroring to read the right way round."""
    x, y, w, h = L.LOGO
    def f(co):
        along = co.x if axis == "x" else co.y
        return (x + (along - origin) * PPM, y + (co.z - L.SIGN["z0"]) * PPM)
    return f


# The crest is white board like the rake boards, so it takes the same fascia
# rows under the gutter (RAKE_ROWS). Its sides and ends run the whole height
# of the solid, foot included, onto those rows: the drip edge along the bottom
# rows then shows only where the end cap stands clear of the rake board, and
# the shingles cut the long sides off above it.
def crest_foot(x):
    """Where the crest's solid stops, inside the roof slab."""
    return L.roof_under(x) + 0.15


CREST_LO = crest_foot(L.CREST["w"] / 2.0)


def uv_crest_face(axis):
    def f(co):
        along = co.y if axis == "y" else co.x
        return (along * PPM, L.SOF_Y0 + (co.z - CREST_LO)
                / (L.Z_CREST - CREST_LO) * L.RAKE_ROWS)
    return f


def uv_crest_top(co):
    """The top and the foot, across the plain far rows of the soffit
    (CREST_TOP_ROWS), clear of the eave's shadow ramp and of every line."""
    v0, v1 = L.CREST_TOP_ROWS
    return (co.y * PPM, v0 + (co.x / L.CREST["w"] + 0.5) * (v1 - v0))


# ============================================================ wall regions
def reveal(B, fr, poly, depth, zbase=0.0, skip_z=None):
    """Line the sides of the hole *poly* back by *depth* in the wall's own
    coursing (uv_reveal); the closing face is the caller's. A threshold on
    z = *skip_z* gets no cheek (shell_build.recess())."""
    SB.recess(B, fr, poly, 0.0, -depth, None,
              [uv_reveal(fr, edge, zbase) for edge in SB.edges(poly)], skip_z)


def item_rects(kind, s, z):
    return SB.item_rects(L.OPENINGS[kind], s, z)


def place_item(B, fr, kind, rect, region, level, skip_z=None):
    """A cut opening while it reads, the same rectangle painted flat after."""
    poly = rect_poly(rect)
    out = 0.0
    if opening_mode(level, "side") == "cut":
        reveal(B, fr, poly, L.REVEAL_DEPTH[kind], skip_z=skip_z)
        out = -L.REVEAL_DEPTH[kind]
    B.face([fr.P(s, z, out) for s, z in poly],
           uv_region(fr, region, rect[0], rect[2]))


# ----------------------------------------------------------- gable outlines
def gable_top_line(s_hi, s_lo, cap=None):
    """Points along the rake from *s_hi* to *s_lo*, flattened at *cap*."""
    stops = {s_hi, s_lo, HX}
    if cap is not None:
        off = s_at(cap)
        if 0.0 < off < HX:
            stops.update((HX - off, HX + off))
    lo, hi = min(s_lo, s_hi), max(s_lo, s_hi)
    xs = sorted(x for x in stops if lo - EPS <= x <= hi + EPS)
    pts = [(x, gtop(x) if cap is None else min(cap, gtop(x))) for x in xs]
    return pts[::-1] if s_hi > s_lo else pts


def panel_points(a, b):
    """The head of one curtain-wall panel, left to right, then back down."""
    off = HX - (L.GABLE_HEAD_CAP + L.GABLE_HEAD_DROP - L.Z_EAVE) / L.SLOPE
    xs = sorted({a, b} | {x for x in (HX - off, HX + off) if a < x < b})
    return [(x, gglass(x)) for x in xs] + [(b, L.GABLE_SILL)]


def panel_poly(a, b):
    return [(a, L.GABLE_SILL)] + panel_points(a, b)


def gable_band(B, fr, lo, cap, notches=(), holes=(), breaks=()):
    """The stone of a gable elevation between two of the band's wrap lines.

    *lo* is both the region's foot and the row the band is indexed from, which
    is what keeps the coursing continuous across a wrap: each course of wall
    starts the band again from its own base.
    """
    span = 2.0 * HX
    notch = {round(a, 4): (a, b) for a, b in notches}
    stops = sorted(set([0.0, span] + list(breaks)
                       + [v for n in notches for v in n]))
    pts = [(0.0, lo)]
    for a, b in zip(stops, stops[1:]):
        n = notch.get(round(a, 4))
        if n and abs(n[1] - b) < EPS:
            pts += panel_points(a, b)
        else:
            pts.append((b, lo))
    pts += gable_top_line(span, 0.0, cap)
    fill_region(B, fr, pts, holes, uv_stone(fr, lo))


def gable_apex(B, fr):
    """The triangle above the band's second wrap line.

    Its base carries the middle of the elevation as a breakpoint, because the
    band below it does: gable_top_line puts a vertex under the ridge whether
    the rake is flattened there or not, and a base without one would leave
    that vertex in the middle of an edge.
    """
    off = s_at(Z_CUT)
    fill_region(B, fr, [(HX - off, Z_CUT), (HX, Z_CUT), (HX + off, Z_CUT),
                        (HX, gtop(HX))], [], uv_stone(fr, Z_CUT))


# --------------------------------------------------------------- elevations
def build_front(B, fr, level):
    """The street front. While the openings are cut, the door and the two
    display windows stand GLAZE_DEPTH back on concrete floor slabs
    (door_floor.recess()): a nosing on the wall plane from the ground to the
    slab's top, the reveal starting on that top. The piers' edges beside
    them carry the nosings' top corners (door_floor.notch() round the door),
    so wall, nosing, slab and cheeks meet on shared vertices and the floor
    cap's rim runs straight along the wall line."""
    mode = opening_mode(level, "front")
    slab = floored(level)
    d0, d1, _dz0, dz1 = DOOR_RECT
    for i, (a, b) in enumerate(L.PIERS):
        lb, rb = PIER_BREAK[i]
        poly = [(a, 0.0)]
        if i == MID_PIER:
            # the entrance stands on the ground, so it is a notch in the
            # pier's outline rather than a hole in it
            poly += (DF.notch(DOOR_RECT) if slab else
                     [(d0, 0.0), (d0, dz1), (d1, dz1), (d1, 0.0)])
        poly.append((b, 0.0))
        if rb:
            if slab:
                poly.append((b, DF.T))      # the window slab's nosing corner
            poly.append((b, L.Z_HEAD))
        poly += [(b, L.Z_FASCIA), (a, L.Z_FASCIA)]
        if lb:
            poly.append((a, L.Z_HEAD))
            if slab:
                poly.append((a, DF.T))
        fill_region(B, fr, poly, [], uv_stone(fr, 0.0))

    # The door unit, recessed like the display windows while they are. Its
    # slab samples the portal's floor region where the door's reveal
    # continues it (facade_atlas.DOOR_FLOOR); its nosing is buried in the
    # pier's slab in front of it.
    door = rect_poly(DOOR_RECT)
    if slab:
        DF.recess(B, fr, DOOR_RECT, 0.0, -L.GLAZE_DEPTH, uv_door(fr, d0),
                  [uv_reveal(fr, edge) for edge in SB.edges(door)], L.DOOR_FLOOR)
    else:
        B.face([fr.P(s, z) for s, z in door], uv_door(fr, d0))

    # The gable panels' outer jambs stand over the display windows' sign
    # boards, so the board's top edge carries them as breakpoints.
    panel_edges = [v for p in L.GABLE_PANELS for v in p]
    for name, a, b in L.BAYS:
        tops = sorted(v for v in panel_edges if a + EPS < v < b - EPS)
        B.face([fr.P(s, z) for s, z in
                [(a, L.Z_HEAD), (b, L.Z_HEAD), (b, L.Z_FASCIA)]
                + [(v, L.Z_FASCIA) for v in reversed(tops)]
                + [(a, L.Z_FASCIA)]],
               uv_fascia(fr, name, a))
        rect = (a, b, 0.0, L.Z_HEAD)
        poly = rect_poly(rect)
        # Each window's lights are counted from its pier end, so the two
        # mirror each other about the entrance.
        glass = uv_shop(fr, a, b, flip=b <= L.ENTRANCE_S)
        if slab:
            DF.recess(B, fr, rect, 0.0, -L.GLAZE_DEPTH, glass,
                      [uv_reveal(fr, edge) for edge in SB.edges(poly)],
                      L.FLOORS["shop"])
        else:
            B.face([fr.P(s, z) for s, z in poly], glass)

    breaks = [v for a, b in L.PIERS for v in (a, b)]
    gable_band(B, fr, L.GABLE_SILL, Z_CUT, notches=L.GABLE_PANELS,
               breaks=breaks)
    gable_apex(B, fr)
    for i, (a, b) in enumerate(L.GABLE_PANELS):
        poly = panel_poly(a, b)
        out = 0.0
        if mode == "cut":
            reveal(B, fr, poly, L.GLAZE_DEPTH, zbase=L.GABLE_SILL)
            out = -L.GLAZE_DEPTH
        fill_region(B, fr, poly, [],
                    uv_region(fr, L.GABLE_GLAZE, a, L.GABLE_SILL,
                              L.GABLE_PPM, flip=(i == 1)), out=out)


def build_rear(B, fr, level):
    door, _ = item_rects("maint_door", L.MAINT_DOOR_S, 0.0)
    d0, d1, _, dz1 = door
    span = 2.0 * HX
    fill_region(B, fr, [(0.0, 0.0), (d0, 0.0), (d0, dz1), (d1, dz1), (d1, 0.0),
                        (span, 0.0), (span, CUT), (0.0, CUT)], [],
                uv_stone(fr, 0.0))
    place_item(B, fr, "maint_door", door, L.MAINT_DOOR, level, skip_z=0.0)

    vents = [(s - L.LOUVRE_WH[0] / 2.0, s + L.LOUVRE_WH[0] / 2.0,
              z, z + L.LOUVRE_WH[1]) for s, z in L.LOUVRES]
    gable_band(B, fr, CUT, Z_CUT, holes=[rect_poly(v) for v in vents])
    gable_apex(B, fr)
    for v in vents:
        poly = rect_poly(v)
        out = 0.0
        if opening_mode(level, "side") == "cut":
            reveal(B, fr, poly, 0.10, zbase=CUT)
            out = -0.10
        B.face([fr.P(s, z, out) for s, z in poly],
               uv_region(fr, L.LOUVRE, v[0], v[2]))


def build_side(B, fr, level):
    holes = [rect_poly(item_rects("side_window", s, L.Z_WIN)[0])
             for s in L.SIDE_WINDOWS]
    fill_region(B, fr, rect_poly((0.0, fr.L, 0.0, CUT)), holes,
                uv_stone(fr, 0.0))
    for s in L.SIDE_WINDOWS:
        outer, _ = item_rects("side_window", s, L.Z_WIN)
        place_item(B, fr, "side_window", outer, L.SIDE_WINDOW, level)
    # the strip that runs on into the roof slab, where the union removes it
    top = L.Z_EAVE + L.WALL_INTO_ROOF
    B.face([fr.P(0.0, CUT), fr.P(fr.L, CUT), fr.P(fr.L, top), fr.P(0.0, top)],
           uv_patch("blank"))


def close_solid(B):
    """Cap the wall ring: a floor on the ground, a lid under the roof.

    Both end up buried, but the solid must be closed for the boolean to be
    exact. The lid is two faces rather than one: the rim follows the gable, so
    a single n-gon across it would not be planar. Split at the two ridge
    vertices, each half lies in one roof plane.
    """
    loops = SB.rim_loops(B, 2)
    blank = uv_patch("blank")
    floor = min(loops, key=lambda lp: max(v.co.z for v in lp))
    top = next(lp for lp in loops if lp is not floor)
    SB.cap(B, floor, blank)
    ridge = [v for v in top if abs(v.co.x) < 1e-4 and abs(abs(v.co.y) - HY) < 1e-4]
    if len(ridge) != 2:
        raise ValueError("expected two ridge vertices on the lid's rim, got %d"
                         % len(ridge))
    SB.cap(B, top, blank, split=ridge)


def side_frames():
    return (Frame((HX, -HY), (HX, HY)), Frame((-HX, HY), (-HX, -HY)))


def main_body(level):
    B = Builder()
    build_front(B, Frame((-HX, -HY), (HX, -HY)), level)
    build_rear(B, Frame((HX, HY), (-HX, HY)), level)
    for fr in side_frames():
        build_side(B, fr, level)
    close_solid(B)
    return B


# ==================================================================== roof
def roof():
    """One gable slab: deck, soffit, fascia and rake board in a single solid.

    A slab plus a separately swept eave would meet along the wall line
    tangentially, which is the case an exact boolean handles worst. Folded at
    the ridge and carried right out to the eave edge, it is one surface.
    """
    B = Builder()
    xs = [-XE, -HX, 0.0, HX, XE]
    ys = [-YE, -HY, HY, YE]
    zb = L.roof_under

    def zt(x):
        return L.roof_under(x) + L.ROOF_T

    for i in range(4):
        x0, x1 = xs[i], xs[i + 1]
        left = (x0 + x1) < 0.0
        for j in range(3):
            y0, y1 = ys[j], ys[j + 1]
            if i in (0, 3):
                soffit = uv_soffit_x
            elif j in (0, 2):
                soffit = uv_soffit_y
            else:
                soffit = uv_patch("blank")
            B.face([(x0, y0, zb(x0)), (x1, y0, zb(x1)),
                    (x1, y1, zb(x1)), (x0, y1, zb(x0))], soffit)
            B.face([(x0, y0, zt(x0)), (x0, y1, zt(x0)),
                    (x1, y1, zt(x1)), (x1, y0, zt(x1))], uv_roof(left))
    for x in (-XE, XE):
        for j in range(3):
            y0, y1 = ys[j], ys[j + 1]
            B.face([(x, y0, zb(x)), (x, y0, zt(x)),
                    (x, y1, zt(x)), (x, y1, zb(x))], uv_eave_fascia(x))
    for y in (-YE, YE):
        for i in range(4):
            x0, x1 = xs[i], xs[i + 1]
            B.face([(x0, y, zb(x0)), (x1, y, zb(x1)),
                    (x1, y, zt(x1)), (x0, y, zt(x0))], uv_rake_board)
    return B


# ============================================================ other solids
PIER_OUT = L.PIER_OUT       # how far the middle pier stands off the gable
PIER_IN = 0.10              # and how far it sinks into it, so no face is
                            # coplanar with the wall it is unioned into


def mid_pier():
    """The stone pier under the apex, 2.8 m wide, from the pavement to the
    top, with the shop's entrance through its foot.

    Its face is three courses, cut where the stone band wraps, so the coursing
    runs on from the wall it stands against instead of restarting. Every other
    face of the solid carries the same two breakpoints, or the face edges meet
    the front's in their middles.

    The portal is an opening through the whole depth of the solid, lined in
    the pier's own coursing turned round its corners, PORTAL_REBATE clear of
    the door's reveal on every side so no face of the pier lies in the plane
    of one of the wall's. It stands on a concrete floor slab
    (door_floor.recess()), its nosing on the pier's face and its top 0.02 m
    over the ground through the whole depth of the solid, where the door's
    own slab in the wall (build_front()) continues it to the door on the
    same atlas region. The slab's top is the one face the pier shares with
    the wall's plane: both are z = 0.02 over the door's reveal, and the exact
    union merges them. Under it the solid's foot runs straight across the
    portal, and its back face closes over the slab's 0.02 m at y_in, inside
    the door's slab.
    """
    B = Builder()
    a, b = L.PIERS[MID_PIER]
    x0, x1 = a - HX, b - HX
    p0, p1, _pz0, pz1 = PORTAL_RECT
    xp0, xp1 = p0 - HX, p1 - HX
    y_out, y_in = -HY - PIER_OUT, -HY + PIER_IN
    fr = Frame((-HX, -HY), (HX, -HY))          # so the coursing lines up
    face = Frame((-HX, y_out), (HX, y_out))    # the pier's own face

    def top(x):
        return L.roof_under(x) + L.WALL_INTO_ROOF

    portal = DF.notch(PORTAL_RECT)             # with the slab's top corners
    fill_region(B, fr, [(a, 0.0)] + portal + [(b, 0.0), (b, CUT), (a, CUT)],
                [], uv_stone(fr, 0.0), out=PIER_OUT)
    fill_region(B, fr, rect_poly((a, b, CUT, Z_CUT)), [], uv_stone(fr, CUT),
                out=PIER_OUT)
    fill_region(B, fr, [(a, Z_CUT), (b, Z_CUT), (b, top(x1)), (HX, top(0.0)),
                        (a, top(x0))], [], uv_stone(fr, Z_CUT), out=PIER_OUT)
    DF.recess(B, face, PORTAL_RECT, 0.0, -(PIER_OUT + PIER_IN), None,
              [uv_reveal(face, edge) for edge in SB.edges(rect_poly(PORTAL_RECT))],
              L.FLOORS["portal"])

    blank = uv_patch("blank")
    fill_region(B, fr, [(a, 0.0)] + portal
                + [(b, 0.0), (b, CUT), (b, Z_CUT), (b, top(x1)), (HX, top(0.0)),
                   (a, top(x0)), (a, Z_CUT), (a, CUT)], [], blank,
                out=-PIER_IN)
    for x, s_edge, sign in ((x0, a, -1.0), (x1, b, 1.0)):
        for lo, hi, base in ((0.0, CUT, 0.0), (CUT, Z_CUT, CUT),
                             (Z_CUT, top(x), Z_CUT)):
            B.face([(x, y_in, lo), (x, y_out, lo), (x, y_out, hi),
                    (x, y_in, hi)], uv_return(fr, s_edge, sign, base))
    for xa, xb in ((x0, 0.0), (0.0, x1)):
        B.face([(xa, y_in, top(xa)), (xb, y_in, top(xb)),
                (xb, y_out, top(xb)), (xa, y_out, top(xa))], blank)
    # the back of the slab under the portal, inside the door's own slab
    B.face([fr.P(p1, 0.0, -PIER_IN), fr.P(p0, 0.0, -PIER_IN),
            fr.P(p0, DF.T, -PIER_IN), fr.P(p1, DF.T, -PIER_IN)], blank)
    for xa, xb in ((x0, xp0), (xp0, xp1), (xp1, x1)):   # the foot, under the slab
        B.face([(xa, y_in, 0.0), (xa, y_out, 0.0), (xb, y_out, 0.0),
                (xb, y_in, 0.0)], blank)
    return B


def door_sign(level):
    """The lit plaque with the pharmacy mark, over the entrance.

    It stands DOOR_SIGN["out"] proud of the pier's face, or of the wall's
    where the pier has gone flat, and runs back to PIER_IN behind the wall
    line either way, so the union always meets a solid overlap.
    """
    B = Builder()
    w, h = L.DOOR_SIGN["w"], L.DOOR_SIGN["h"]
    x0, x1 = L.ENTRANCE_S - HX - w / 2.0, L.ENTRANCE_S - HX + w / 2.0
    z0, z1 = L.DOOR_SIGN["z0"], L.DOOR_SIGN["z0"] + h
    face = -HY - (PIER_OUT if pier_kept(level) else 0.0)
    y0, y1 = face - L.DOOR_SIGN["out"], -HY + PIER_IN
    side, blank = uv_patch("sign_side"), uv_patch("blank")
    B.face([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
           uv_plaque(x0, z0))
    B.face([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], blank)
    B.face([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], side)
    B.face([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], side)
    B.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], side)
    B.face([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)], side)
    return B


def side_buttress(fr, s):
    """One stone buttress on a side wall, the same width and the same
    projection the whole way up: it is applied decoration, not a raking prop,
    so it has no batter.

    It stops at the same height as the wall behind it, inside the roof slab
    rather than under it: the soffit falls 0.45 m per metre as it comes out,
    so a buttress that stopped at the wall head would touch it along one line
    and push through it everywhere further out. Run up into the slab, the
    union trims it flush against the falling soffit instead, and no sliver of
    hidden surface is left under the eave. Its face is cut at the stone band's
    wrap line for the same reason the walls are.
    """
    B = Builder()
    s0, s1 = s - L.BUTTRESS_W / 2.0, s + L.BUTTRESS_W / 2.0
    z_top = L.Z_EAVE + L.WALL_INTO_ROOF
    out, o_in = L.BUTTRESS_OUT, -PIER_IN
    blank = uv_patch("blank")
    for lo, hi, base in ((0.0, CUT, 0.0), (CUT, z_top, None)):
        fn = blank if base is None else uv_stone(fr, base)
        B.face([fr.P(s0, lo, out), fr.P(s1, lo, out),
                fr.P(s1, hi, out), fr.P(s0, hi, out)], fn)
        B.face([fr.P(s0, lo, o_in), fr.P(s0, hi, o_in),
                fr.P(s1, hi, o_in), fr.P(s1, lo, o_in)], blank)
        for x, sign in ((s0, -1.0), (s1, 1.0)):
            side = blank if base is None else uv_return(fr, x, sign, base)
            B.face([fr.P(x, lo, o_in), fr.P(x, lo, out),
                    fr.P(x, hi, out), fr.P(x, hi, o_in)], side)
    B.face([fr.P(s0, z_top, o_in), fr.P(s1, z_top, o_in),
            fr.P(s1, z_top, out), fr.P(s0, z_top, out)], blank)
    B.face([fr.P(s0, 0.0, o_in), fr.P(s0, 0.0, out),
            fr.P(s1, 0.0, out), fr.P(s1, 0.0, o_in)], blank)
    return B


def crest():
    """The white crest along the ridge, rake to rake.

    Its foot is a slice of the two roof planes, like the stacks', so it lies
    inside the slab along its whole length: a flat foot across the ridge would
    be inside the slab only over a 15 mm band of height, which is not a solid
    intersection to hand a boolean. The union trims it to the shingles and
    leaves two vertical sides and a flat top. Its ends stand CREST["end"] past
    the rake boards, clear of their faces, so they cap the apex instead of
    lying coplanar with it.
    """
    B = Builder()
    hw = L.CREST["w"] / 2.0
    y0, y1 = -YE - L.CREST["end"], YE + L.CREST["end"]
    z1 = L.Z_CREST
    foot = crest_foot
    B.face([(-hw, y0, foot(-hw)), (0.0, y0, foot(0.0)), (hw, y0, foot(hw)),
            (hw, y0, z1), (-hw, y0, z1)], uv_crest_face("x"))
    B.face([(-hw, y1, z1), (hw, y1, z1), (hw, y1, foot(hw)),
            (0.0, y1, foot(0.0)), (-hw, y1, foot(-hw))], uv_crest_face("x"))
    for x in (-hw, hw):
        B.face([(x, y0, foot(x)), (x, y1, foot(x)), (x, y1, z1), (x, y0, z1)],
               uv_crest_face("y"))
    B.face([(-hw, y0, z1), (hw, y0, z1), (hw, y1, z1), (-hw, y1, z1)],
           uv_crest_top)
    for xa, xb in ((-hw, 0.0), (0.0, hw)):
        B.face([(xa, y0, foot(xa)), (xa, y1, foot(xa)),
                (xb, y1, foot(xb)), (xb, y0, foot(xb))], uv_crest_top)
    return B


def _box(B, x0, x1, y0, y1, z0, z1, uvfn):
    """A leg: a closed box in this asset's own face order (front, back,
    left, right, top, bottom), which shell_build.box()'s ring order would
    renumber, moving every exported tier."""
    for f in ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
              [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
              [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
              [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
              [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
              [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)]):
        B.face(f, uvfn)


def sign_stand():
    """The four steel legs under the sign, in two pairs along the crest.

    Each runs 0.05 m into the crest below and the box above, so the union
    meets solid overlaps rather than faces lying on faces.
    """
    B = Builder()
    r = L.STAND["leg"] / 2.0
    z0, z1 = L.Z_CREST - 0.05, L.SIGN["z0"] + 0.05
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            x, y = sx * L.STAND["x"], L.SIGN["y"] + sy * L.STAND["y"]
            _box(B, x - r, x + r, y - r, y + r, z0, z1, uv_patch("steel"))
    return B


def sign_box():
    """The centre's illuminated sign, a closed cube on its stand, clear of
    the roof on every side: the four faces carry the mark, the lid is the
    lit field's colour and the underside is the steel of the stand."""
    B = Builder()
    w, h, d = L.SIGN["w"], L.SIGN["h"], L.SIGN["d"]
    x0, x1 = -w / 2.0, w / 2.0
    y0, y1 = L.SIGN["y"] - d / 2.0, L.SIGN["y"] + d / 2.0
    z0, z1 = L.SIGN["z0"], L.SIGN["z0"] + h
    for y in (y0, y1):
        B.face([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)],
               uv_logo("x", x0))
    for x in (x0, x1):
        B.face([(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)],
               uv_logo("y", y0))
    B.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
           uv_patch("sign_side"))
    B.face([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
           uv_patch("steel"))
    return B


def ahu_box():
    """The air handler hung on the right-hand wall."""
    B = Builder()
    y = L.AHU["s"] - HY
    y0, y1 = y - L.AHU["w"] / 2.0, y + L.AHU["w"] / 2.0
    x0, x1 = HX - 0.10, HX + L.AHU["d"]
    z0, z1 = L.AHU["z"], L.AHU["z"] + L.AHU["h"]
    fr = Frame((HX, -HY), (HX, HY))
    steel, blank = uv_patch("steel"), uv_patch("blank")
    B.face([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
           uv_region(fr, L.AHU_SIDE, y0 + HY, z0))
    B.face([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], blank)
    for y_ in (y0, y1):
        B.face([(x0, y_, z0), (x1, y_, z0), (x1, y_, z1), (x0, y_, z1)], steel)
    top = Frame((x0, y1), (x1, y1))
    B.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
           uv_region(top, L.AHU_TOP, 0.0, z1))
    B.face([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], steel)
    return B


def vent(kind, px, py, size, height, sides=8):
    """A stack on the roof: its foot is a slice of the roof plane, so it is
    inside the slab everywhere rather than only at its middle."""
    B = Builder()
    r = size / 2.0

    def foot(x):
        return L.roof_under(x) + 0.15

    base = L.roof_under(abs(px) + r) + 0.15
    z1 = L.roof_under(px) + L.ROOF_T + height
    steel, blank = uv_patch("steel"), uv_patch("blank")
    if kind == "box":
        ring = [(px - r, py - r), (px + r, py - r), (px + r, py + r),
                (px - r, py + r)]
        rect = L.VENT_BOX
    else:
        ring = [(px + r * math.cos(a), py + r * math.sin(a))
                for a in [i * 2.0 * math.pi / sides for i in range(sides)]]
        rect = L.VENT_PIPE
    rx, ry, rw, rh = rect
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        # every side gets the whole casing region across it rather than a run
        # along a shared perimeter: a stack is small, and a perimeter that did
        # not divide the region would wrap the artwork in the middle of a face
        def fn(co, ax=ax, ay=ay, bx=bx, by=by):
            t = 0.0 if abs(bx - ax) + abs(by - ay) < EPS else \
                ((co.x - ax) * (bx - ax) + (co.y - ay) * (by - ay)) / \
                ((bx - ax) ** 2 + (by - ay) ** 2)
            return (rx + t * rw, ry + (co.z - base) * PPM)
        B.face([(ax, ay, foot(ax)), (bx, by, foot(bx)), (bx, by, z1),
                (ax, ay, z1)], fn)
    B.face([(x, y, z1) for x, y in ring], steel)
    B.face([(x, y, foot(x)) for x, y in reversed(ring)], blank)
    return B


# ================================================================ assembly


def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    # The crest and the stand stay on every tier: the crest is the white line
    # along the roofline, and without its legs the sign would float.
    parts = [to_object(roof(), "tmp_roof"), to_object(crest(), "tmp_crest"),
             to_object(sign_stand(), "tmp_stand"),
             to_object(sign_box(), "tmp_sign"),
             to_object(door_sign(level), "tmp_door_sign")]
    if pier_kept(level):
        parts.append(to_object(mid_pier(), "tmp_pier"))
    if ahu_kept(level):
        parts.append(to_object(ahu_box(), "tmp_ahu"))
    if buttress_kept(level):
        for w, fr in enumerate(side_frames()):
            for i, s in enumerate(L.BUTTRESSES):
                parts.append(to_object(side_buttress(fr, s),
                                       "tmp_buttress%d%d" % (w, i)))
    for i, (kind, (px, py), size, height) in enumerate(L.VENTS):
        if vent_kept(level, kind):
            parts.append(to_object(
                vent(kind, px, py, size, height, 8 if level == 0 else 4),
                "tmp_vent%d" % i))
    parts += [to_object(B, n) for B, n in
              DP.solids(DOWNPIPES, *DP.MODES[level], L.PIPE_STRIP, L.ATLAS)]
    drop_kit = KIT_MODES[level][0] is None
    if not drop_kit:
        parts += [to_object(B, n) for B, n in kit(level)]
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # 1e-4 rather than 1e-5: the exact boolean resolves this building's 24 m
    # rake lines in 32-bit floats and leaves the odd corner vertex a hundredth
    # of a millimetre off its neighbour, which exports as two vertices and
    # reads as a non-manifold seam downstream. The smallest authored feature
    # here is the shopfront mullion's 0.05 m, so a 0.1 mm weld cannot reach it.
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
    if drop_kit:
        # the wall ladder's bare rails, clear of everything, after the weld
        RS.append(obj, kit(level, extents=True), check=True)
    return obj


# ================================================================== checks
def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    spans = sorted([(a, b) for a, b in L.PIERS]
                   + [(a, b) for _n, a, b in L.BAYS])
    if abs(spans[0][0]) > EPS or abs(spans[-1][1] - 2 * HX) > EPS:
        bad.append("the front's bays and piers do not span 0 .. %.1f m" % (2 * HX))
    for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
        if abs(a1 - b0) > EPS:
            bad.append("gap or overlap on the front at %.3f m" % a1)
    a, b = L.PIERS[MID_PIER]
    p0, p1, _z0, pz1 = PORTAL_RECT
    if p0 - a < 0.3 - EPS or b - p1 < 0.3 - EPS:
        bad.append("the portal leaves the middle pier less than 0.3 m of stone "
                   "either side")
    # the set-backs' floor slabs (scripts/door_floor.py): each region the
    # opening's width and the set-back's depth, under an opening at grade;
    # the portal's runs from the pier's face to the door, and the pier's
    # solid ends inside the door's reveal, on the door's slab
    for name, a_, b_ in L.BAYS:
        bad += DF.problems(L.FLOORS["shop"], "the %s display window" % name,
                           (a_, b_, 0.0, L.Z_HEAD), L.GLAZE_DEPTH)
    bad += DF.problems(L.DOOR_FLOOR, "the entrance", DOOR_RECT, L.GLAZE_DEPTH)
    bad += DF.problems(L.FLOORS["portal"], "the portal", PORTAL_RECT,
                       PIER_OUT + L.GLAZE_DEPTH)
    if not 0.0 < PIER_IN < L.GLAZE_DEPTH:
        bad.append("the pier's portal slab does not end inside the door's reveal")
    portal_floor = L.FLOORS["portal"]
    if (abs(L.DOOR_FLOOR.x - portal_floor.x - (DOOR_RECT[0] - p0) * PPM) > EPS
            or abs(L.DOOR_FLOOR.y - portal_floor.y - PIER_OUT * PPM) > EPS):
        bad.append("the door's floor does not continue the portal's on its region")
    if abs(L.ENTRANCE_S - HX) > EPS:
        bad.append("the entrance is %.2f m off the front's centre"
                   % (L.ENTRANCE_S - HX))
    sw = L.DOOR_SIGN["w"]
    if (L.DOOR_SIGN["z0"] < pz1 + 0.1 or L.ENTRANCE_S - sw / 2.0 < a + 0.2
            or L.ENTRANCE_S + sw / 2.0 > b - 0.2):
        bad.append("the plaque over the door is not on the pier above the "
                   "portal")
    if abs(L.DOOR_SIGN["w"] - L.DOOR_SIGN["h"]) > EPS:
        bad.append("the plaque is not square; it takes the square LOGO region")
    if not 2.0 <= L.Z_LEAF <= 2.4:
        bad.append("door leaf %.2f m is outside the 2.0 - 2.4 m band"
                   % L.Z_LEAF)
    if L.Z_HEAD > L.Z_FASCIA or L.Z_FASCIA != L.Z_EAVE:
        bad.append("the sign fascia does not sit between the shopfront head "
                   "and the eave")
    for a, b in L.GABLE_PANELS:
        if gglass(a) > gunder(a) - EPS or gglass(b) > gunder(b) - EPS:
            bad.append("a gable panel's head is through the roof")
        if max(gglass(a), gglass(b)) > Z_CUT - EPS:
            bad.append("a gable panel crosses the stone band's wrap line, "
                       "which its region cannot straddle")
    # region pixel sizes against the metres they are stretched over
    for rect, size, ppm, what in (
            (L.DOOR_DOUBLE, (L.ENTRANCE_W, L.Z_HEAD), PPM, "double door"),
            (L.SIDE_WINDOW, L.item_size_m("side_window"), PPM, "side window"),
            (L.MAINT_DOOR, L.item_size_m("maint_door"), PPM, "maintenance door"),
            (L.LOUVRE, L.LOUVRE_WH, PPM, "gable louvre"),
            (L.GABLE_GLAZE, (L.BAY_W, L.GABLE_HEAD_CAP - L.GABLE_SILL),
             L.GABLE_PPM, "gable curtain wall"),
            (L.AHU_SIDE, (L.AHU["w"], L.AHU["h"]), PPM, "air handler"),
            (L.LOGO, (L.SIGN["w"], L.SIGN["h"]), PPM, "ridge sign"),
            (L.ROOF, (2.0 * YE, SLOPE_LEN), L.ROOF_PPM, "roof slope")):
        for got, want, axis in ((rect[2], size[0] * ppm, "width"),
                                (rect[3], size[1] * ppm, "height")):
            if abs(got - want) > 1.0:
                bad.append("the %s region's %s is %d px for %.1f px of "
                           "artwork" % (what, axis, got, want))
    for name, a, b in L.BAYS:
        if abs(L.FASCIA[name][2] - (b - a) * PPM) > 1.0:
            bad.append("the %s sign board does not match its bay" % name)
    if abs(L.SIGN["d"] - L.SIGN["w"]) > EPS:
        bad.append("the ridge sign is %.2f x %.2f m in plan; its four faces "
                   "share one square region and cannot be stretched"
                   % (L.SIGN["w"], L.SIGN["d"]))
    if L.SIGN["y"] - L.SIGN["d"] / 2.0 < -YE or L.SIGN["y"] + L.SIGN["d"] / 2.0 > YE:
        bad.append("the ridge sign overhangs the roof it stands on")
    reach = L.STAND["x"] + L.STAND["leg"] / 2.0
    if reach > L.CREST["w"] / 2.0 - 0.02:
        bad.append("the sign's legs stand off the %.2f m crest" % L.CREST["w"])
    if (reach > L.SIGN["w"] / 2.0
            or L.STAND["y"] + L.STAND["leg"] / 2.0 > L.SIGN["d"] / 2.0):
        bad.append("the sign's legs stand outside the box they carry")
    if not 0.0 < crest_foot(0.0) - L.roof_under(0.0) < L.ROOF_T:
        bad.append("the crest's foot is not inside the roof slab")
    for kind, (px, _py), size, _h in L.VENTS:
        if abs(px) - size / 2.0 < L.CREST["w"] / 2.0 + 0.1:
            bad.append("a roof %s stands against the ridge crest" % kind)
    if L.SOF_FASCIA + L.RAKE_OUT * PPM > L.SOF_H:
        bad.append("the soffit band is too short for a %.2f m rake overhang"
                   % L.RAKE_OUT)
    if L.ROOF_T * PPM > L.SOF_FASCIA + 1.0:
        bad.append("the fascia rows cannot cover a %.3f m board" % L.ROOF_T)
    if not L.SOF_Y0 + L.RAKE_ROWS < L.GUT_Y0 - 1 < L.PIPE_STRIP[0]:
        bad.append("the rake boards' rows reach the gutter, or PIPE_STRIP is off it")
    bad += rainwater_and_kit_problems()
    return bad


def rainwater_and_kit_problems():
    """The downpipes and the wall ladder against everything on the side walls
    and each other; the kit's pieces on the roof against the stacks, the
    crest and the sign, and reaching what they serve."""
    bad = []
    wall = [("window", *item_rects("side_window", s, L.Z_WIN)[0][:2])
            for s in L.SIDE_WINDOWS]
    wall += [("buttress", s - L.BUTTRESS_W / 2.0, s + L.BUTTRESS_W / 2.0)
             for s in L.BUTTRESSES]
    avoid = {"right": wall + [("air handler", L.AHU["s"] - L.AHU["w"] / 2.0,
                               L.AHU["s"] + L.AHU["w"] / 2.0)],
             "left": wall + [("wall ladder", *WALL_LADDER.span())]}
    pipes = {"right": [], "left": []}
    for (name, _ends, s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        side = name.split()[0]
        bad += DP.problems(pipe, "the %s downpipe" % name, avoid[side])
        pipes[side].append(("downpipe", s - DP.A, s + DP.A))
    bad += RS.problems(WALL_LADDER, "the wall ladder", wall + pipes["left"])
    # on the roof: nothing within 0.1 m of a stack, the crest or the sign,
    # except the housing each piece serves, which it must come within 0.4 m of
    hw = L.CREST["w"] / 2.0
    things = [("%s %d" % (kind, i), px - sz / 2.0, px + sz / 2.0,
               py - sz / 2.0, py + sz / 2.0)
              for i, (kind, (px, py), sz, _h) in enumerate(L.VENTS)]
    things.append(("crest", -hw, hw, -YE, YE))
    things.append(("sign", -L.SIGN["w"] / 2.0, L.SIGN["w"] / 2.0,
                   L.SIGN["y"] - L.SIGN["d"] / 2.0, L.SIGN["y"] + L.SIGN["d"] / 2.0))
    serves = {"housing walkway": "box 0", "housing ladder": "box 1",
              "ridge walkway": "sign"}

    def gap(a, b):
        return math.hypot(max(a[0] - b[1], b[0] - a[1], 0.0),
                          max(a[2] - b[3], b[2] - a[3], 0.0))
    for name, *r in kit_plan():
        for what, *t in things:
            g = gap(r, t)
            if serves.get(name) == what:
                if g > 0.4:
                    bad.append("the %s stops %.2f m short of the %s it serves"
                               % (name, g, what))
            elif g < 0.1:
                bad.append("the %s runs into the %s" % (name, what))
    return bad


def check_roof(obj):
    """Nothing may stand higher than the sign, and nothing wider than the
    eaves: both are what the catalog row and notes.md quote."""
    xs = [v.co.x for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    return (round(max(xs) - min(xs), 3), round(max(zs), 3))


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame.

    The footprint is the 24 x 16 m wall ring; the middle pier and the side
    buttresses are relief applied to it, and the air handler hangs on it.
    The shop's one door, its main entrance, is given on the front wall's
    plane, though the door stands GLAZE_DEPTH back in the portal through the
    middle pier. Its pair of leaves runs from the pavement to Z_LEAF, under a
    transom light. One storey; the gable is roof space.
    """
    front = ((-HX, -HY), (HX, -HY))
    rear = ((HX, HY), (-HX, HY))
    doors = [model_facts.wall_door("pharmacy", "entrance", *front, L.ENTRANCE_S,
                                   0.0, L.ENTRANCE_W, L.Z_LEAF, main=True)]
    w, h = L.OPENINGS["maint_door"][:2]
    doors.append(model_facts.wall_door("maintenance", "service", *rear, L.MAINT_DOOR_S,
                                       0.0, w, h))
    return {"hero": False, "dwellings": 0,
            "footprint": [(-HX, -HY), (HX, -HY), (HX, HY), (-HX, HY)],
            "storeys": [(0.0, 2 * HX * 2 * HY)], "doors": doors}

# ================================================================ previews


def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views (shell_build.render_views()), plus the same
    aerial from behind, where the maintenance door and the air handler are,
    and a low view of the front. Working views only - not committed."""
    return SB.render_views(BUILD, out_dir, level, res, views=(
        SB.AERIAL, SB.AERIAL_REAR, SB.orbit("eye_front", (0.35, -1.0, 0.22))))


if __name__ == "__main__":
    BUILD.main(build_all, facts)
