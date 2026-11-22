# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of parturi_brick_pyramid, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A late-1980s suburban barber's pavilion: one storey of buff facing brick,
10 x 8 m, under a brown standing-seam hipped roof of one pitch on all four
sides, so steep and short-ridged it reads as a pyramid. It stands at the back
of a 20 x 20 m lot with the forecourt in front.

The street elevation (-Y) carries the shop: an entrance lobby set 0.88 m into
the brick, left of centre, its glazed screen (the door leaf and a sidelight
under a transom light) at the back, and two windows to its right, all under
soldier courses on one head line. A brown sheet band under the eave carries
PARTURI in cut cream letters over the windows, and a square light box on a
bracket stands out from the pier beside the lobby; a wall lamp under a lit
house number, an opening-hours board and a lobby ceiling light are the small
things round the door. The east wall has the side window and a small staff
window, the rear the service door under a small canopy with a wall lamp and
a high window, the west the meter cupboard, a small WC window and an air
louvre. A louvred sheet-metal ventilation housing sits on the ridge; the
roof safety kit reaches it from the back. Gutters run round all four eaves,
with two downpipes at diagonally opposite corners.

Construction: closed solids unioned with Blender's exact boolean
(asset_build.union, snapped to 0.1 mm) -- the body (the wall ring with its
recesses, capped with a floor and a lid), the roof (hip slopes, fascia,
soffit and underside as one solid), the hip and ridge flashings (to LOD2),
the housing with its louvre blades, skirt and lid (to LOD2), the hood with its blades and
cap, the fittings, the sign band, the light box and its arms, the canopy,
the downpipes and the roof safety kit.

Every number the mesh and the atlas share is imported from facade_atlas.py.
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
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import downpipes as DP  # noqa: E402
import model_facts  # noqa: E402
import roof_safety as RS  # noqa: E402
import shell_build as SB  # noqa: E402
from asset_build import to_object, union  # noqa: E402
from shell_build import Frame, fill_region, rect_poly  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT, tint=L.LIT_FACTOR)
get_material, export_all = BUILD.material, BUILD.export_all
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants
Builder = functools.partial(SB.Builder, L.ATLAS)

PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ================================================================== massing
HX, HY = L.HX, L.HY
EO = L.EAVE_OUT
EX, EY = HX + EO, HY + EO                    # the eave's outline, half
RX = HX - HY                                 # half the ridge: equal pitches
SLOPE_K = math.sqrt(1.0 + L.TAN * L.TAN)     # slope length per metre of plan

# ------------------------------------------------------------------ elevations
# Each wall runs counter-clockwise seen from above, so its outward face is on
# the right and s runs along it from p0. items are (kind, s at the centre);
# every kind sits at its own fixed heights (facade_atlas.ITEMS). u is the
# wall's offset into the tiling brick band, so the bond does not repeat in
# step from wall to wall. Every u, and every item's sides, fall on a half
# stretcher, so each course ends on a whole or a half brick; the u's
# alternate by a half stretcher at each corner, so the course that ends on
# a whole brick on one face ends on a half on the other, as a stretcher
# bond's quoin does (check_layout()).
WALLS = [
    dict(name="front", p0=(-HX, -HY), p1=(HX, -HY), u=0.0,
         items=[("screen", 2.125), ("window", 5.25), ("window", 8.125)]),
    dict(name="east", p0=(HX, -HY), p1=(HX, HY), u=3.125,
         items=[("side_window", 2.4375), ("small_window", 5.5625)]),
    dict(name="rear", p0=(HX, HY), p1=(-HX, HY), u=6.25,
         items=[("small_window", 2.3125), ("service_door", 7.0)]),
    dict(name="west", p0=(-HX, HY), p1=(-HX, -HY), u=9.625,
         items=[("meter", 2.0625), ("small_window", 3.5625), ("louvre", 5.0)]),
]
# the lobby cheeks' offset into the brick band, past the wall's own u: the
# left cheek's, and the right's CHEEK_U[1] on; each turns its corner a half
# stretcher out of step with the front, like the building's corners
CHEEK_U = (1.375, 2.0)
WALL = {w["name"]: w for w in WALLS}

# The projecting light box, on the pier right of the lobby: its face is
# square, it stands BOX_OUT off the brick so it clears the sign band, and it
# hangs from two arms let into the pier below the band.
BOX_S = 3.8
BOX_T = 0.15                                 # its thickness, along the wall
BOX_OUT = (0.15, 0.15 + L.SIGN_BOX_M)        # its inner and outer edges, off the wall
BOX_Z = (2.25, 2.25 + L.SIGN_BOX_M)
ARMS = ((2.33, 2.37), (2.65, 2.69))          # z of the two arms
ARM_W = 0.04
ARM_OUT = (-0.05, BOX_OUT[0] + 0.15)         # from inside the pier into the box

BAND_OUT = 0.10                              # the sign band, proud of the brick

# the rear door's canopy: a flat steel tray on the wall over the door
CANOPY_S = (6.25, 7.75)
CANOPY_OUT = 0.60
CANOPY_Z = (2.46, 2.56)

# The louvred attic vent on the front slope: a small hood whose vertical
# front carries the louvre and whose nearly level top runs back into the
# slope, under a cap plate that oversails its front and sides. HOOD_Y is
# its front's y, L.HOOD_FACE the front's height over the sheet there,
# HOOD_FALL the top's fall toward the front.
HOOD_X = L.HOOD_W / 2.0
HOOD_Y = -2.6
HOOD_FACE = L.HOOD_FACE
HOOD_FALL = 0.052
HOOD_CAP = (0.06, 0.03, 0.020, 0.035)   # cap: oversail front, sides; above, below the top

# The small fittings, each a box on its wall (facade_atlas.LAMP_M etc. give
# their sizes): s at the centre along the wall, z of the foot. The wall lamp
# and the lit house number stand one over the other on the pier left of the
# lobby, the opening-hours board on the pier right of it under the light
# box's arms, a ceiling light in the lobby's soffit, and the same wall lamp
# again by the service door.
FRONT_LAMP = (0.55, 1.98)
NUMBER_AT = (0.55, 2.38)
HOURS_AT = (3.80, 1.25)
REAR_LAMP = (8.00, 1.98)
LOBBY_LAMP_OUT = -0.45                  # the ceiling light's centre, off the front wall
FIT_BURY = 0.02                         # every fitting's back, into the brick
# a plain soil vent pipe on the rear slope (LOD0/LOD1): (x, y), radius, height
VENT = ((-2.0, 2.2), 0.06, 0.55)

# Hip and ridge flashings: a five-sided section in a vertical plane across
# the line it caps, (across, up) from the line, buried at the foot.
CAP_SECTION = [(-0.09, -0.10), (0.09, -0.10), (0.09, -0.012), (0.0, 0.035),
               (-0.09, -0.012)]
CAP_CORNER = 0.14            # a hip cap stops this far (in plan) short of the corner

# Downpipes (scripts/downpipes.py): two, at diagonally opposite corners, on
# the side walls, so the street front stays clear and each side shows one.
DOWNPIPES = [DP.eave_pipe(WALL[w]["p0"], WALL[w]["p1"], s, L.Z_EAVE, 0.0, EO)
             for w, s in (("west", 7.7), ("east", 7.7))]

# Roof safety kit (scripts/roof_safety.py), the way to the ventilation
# housing on the ridge: a wall ladder up the middle of the rear wall and the
# roof ladder straight above it up the rear slope to just short of the
# housing's back. The roof ladder reaches the housing, so no walkway.
KIT_S = 5.0                                   # rear wall, s = 5 - x: at x = 0
PAINT = RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)
EAVE_REAR = RS.Eave(WALL["rear"]["p0"], WALL["rear"]["p1"], L.Z_EAVE, EO, L.Z_FT, L.TAN)
ROOF_TOP_OUT = -(HY - L.HOUSING_HALF[1] - 0.30)      # 0.30 m short of the housing
WALL_LADDER = RS.WallLadder(EAVE_REAR, KIT_S)
ROOF_LADDER = RS.RoofLadder(EAVE_REAR, KIT_S, EAVE_REAR.roof_z(ROOF_TOP_OUT))


def item_mode(kind, level):
    """Openings: recessed with their reveals to LOD2, painted flush at LOD3.
    The consumer switches by screen size, LOD1 to LOD2 at about 44 m, where a
    0.12 m reveal's shadow is still two pixels and flush windows popped; at
    LOD3's 87 m it is under one. The entrance lobby is massing, 0.88 m deep
    and 2.25 m wide, and stays cut on every tier: painted flush at LOD3 it
    read lighter than the dark recess. The meter cupboard and the louvre are
    flush on every tier."""
    if kind in ("meter", "louvre"):
        return "flush"
    if kind == "screen":
        return "recess"
    return "recess" if level < 3 else "flush"


def caps_kept(level):
    """The hip and ridge flashings: 0.18 m wide, kept to LOD2, whose 44 m
    switch still shows their highlight lines; at LOD3's 87 m they are about
    1.5 px and the change of light between two slopes draws the hip."""
    return level < 3


def band_modelled(level):
    """The sign band stands 0.10 m off the brick; modelled to LOD2, so its
    letters stay as lit and as proud at the 44 m switch as on LOD1. LOD3
    paints its artwork on the wall's top course instead."""
    return level < 3


def arms(level):
    return ARMS if level < 2 else ARMS[1:]


def canopy_kept(level):
    return level < 3


def housing_mode(level):
    """The ridge housing: "full" to LOD2 (modelled louvre blades, the
    flashing skirt, the hipped lid with its drip edge), since the blades'
    shadows still read at the 44 m switch; "lid" at LOD3, a box under a
    plain overhanging slab, the louvres painted: the oversailing lid is the
    housing's outline at 87 m, and the bare box ("box", unused) lost it."""
    return ("full", "full", "full", "lid")[level]


def hood_mode(level):
    """The front hood: its louvre blades and cap plate to LOD2; at LOD3 the
    bare wedge, its louvres painted."""
    return level < 3


def fittings(level):
    """Which small fittings a tier keeps: everything to LOD2, so the lobby
    light and the rear lamp stay lit and the opening-hours board stays at
    the 44 m switch; at LOD3 the four that light at night (the three lamps
    and the house number), points of light that would go out at 87 m. The
    unlit opening-hours board goes."""
    if level < 3:
        return ("front_lamp", "number", "hours", "lobby_lamp", "rear_lamp")
    return ("front_lamp", "number", "lobby_lamp", "rear_lamp")


def vent_kept(level):
    """The soil vent: 0.12 m across, about 2 px at 70 m, behind the ridge
    from the street; LOD0/LOD1, as plain vent pipes are elsewhere."""
    return level < 2


# ============================================================== wall frames
def frame_of(name):
    w = WALL[name]
    return Frame(w["p0"], w["p1"])


# ------------------------------------------------------------ UV mappings
def uv_patch(name):
    return SB.uv_patch(L.PATCHES[name])


def uv_brick(fr, u_off):
    return lambda co: ((fr.s_of(co) + u_off) * PPM, L.BRICK_Y0 + co.z * PPM)


def uv_band(fr):
    x, y, _w, _h = L.SIGN_BAND
    s0 = L.SIGN_BAND_S[0]
    return lambda co: (x + (fr.s_of(co) - s0) * PPM, y + (co.z - L.Z_BAND0) * PPM)


def uv_item(fr, kind, l, b):
    x, y, _w, _h = L.ITEM_REGION[kind]
    return lambda co: (x + (fr.s_of(co) - l) * PPM, y + (co.z - b) * PPM)


def uv_cheek(fr, u_off):
    """A lobby cheek: the brick band, U running back from the wall face."""
    return lambda co: ((-fr.out_of(co) + u_off) * PPM, L.BRICK_Y0 + co.z * PPM)


def uv_lobby_soffit(fr, depth):
    return lambda co: (fr.s_of(co) * PPM,
                       L.SOF_Y0 + (depth + fr.out_of(co)) / depth * L.SOF_H)


# ================================================================== walls
def item_rect(kind, s):
    """(left, right, bottom, top) of the rectangle an item takes on its wall,
    and its opening's (bottom, top)."""
    it = L.ITEMS[kind]
    b, t = L.item_box(kind)
    return (s - it["w"] / 2.0, s + it["w"] / 2.0, b, t), (it["z0"], it["z1"])


def build_item(B, fr, wall, kind, s, level):
    """Faces for one item; returns its outline on the wall, counter-clockwise
    from its bottom left, with every vertex its faces put on that outline."""
    (l, r, ob, ot), (zb, zt) = item_rect(kind, s)
    fn = uv_item(fr, kind, l, ob)
    if item_mode(kind, level) == "flush":
        B.face([fr.P(l, ob), fr.P(r, ob), fr.P(r, ot), fr.P(l, ot)], fn)
        return [(l, ob), (r, ob), (r, ot), (l, ot)]
    d = L.ITEMS[kind]["depth"]
    if zb > ob + EPS:                                   # the sheet sill
        B.face([fr.P(l, ob), fr.P(r, ob), fr.P(r, zb), fr.P(l, zb)], fn)
    if ot > zt + EPS:                                   # the soldier course
        B.face([fr.P(l, zt), fr.P(r, zt), fr.P(r, ot), fr.P(l, ot)], fn)
    if kind == "screen":
        u0 = wall["u"] + CHEEK_U[0]
        side = (uv_cheek(fr, u0), uv_cheek(fr, u0 + CHEEK_U[1]))
        head, sill = uv_lobby_soffit(fr, d), uv_patch("blank")
    else:
        side = (uv_patch("reveal"), uv_patch("reveal"))
        head, sill = uv_patch("reveal"), uv_patch("sill_top")
    # standing on the ground, it has no sill: the floor cap closes it
    SB.recess(B, fr, rect_poly((l, r, zb, zt)), 0.0, -d, fn, [sill, side[1], head, side[0]],
              skip_z=zb if zb < EPS else None)
    ring = [(l, ob), (r, ob)]
    if zb > ob + EPS:
        ring.append((r, zb))
    ring.append((r, zt))
    if ot > zt + EPS:
        ring += [(r, ot), (l, ot)]
    ring.append((l, zt))
    if zb > ob + EPS:
        ring.append((l, zb))
    return SB.dedupe(ring)


def wall_cells(spec, fr):
    """The wall's rectangles of cladding, (s0, s1, z0, z1, uv): brick from
    the ground to the sign band's foot, and above it brick -- or on the
    front, between SIGN_BAND_S, the band's artwork, which LOD0/LOD1 hide
    under the modelled band and LOD2/LOD3 show."""
    brick = uv_brick(fr, spec["u"])
    cells = [(0.0, fr.L, 0.0, L.Z_BAND0, brick)]
    if spec["name"] == "front":
        a, b = L.SIGN_BAND_S
        cells += [(0.0, a, L.Z_BAND0, L.Z_TOP, brick), (a, b, L.Z_BAND0, L.Z_TOP, uv_band(fr)),
                  (b, fr.L, L.Z_BAND0, L.Z_TOP, brick)]
    else:
        cells.append((0.0, fr.L, L.Z_BAND0, L.Z_TOP, brick))
    return cells


def _on_edge(p, a, b):
    """p strictly inside the axis-aligned segment a-b."""
    if abs(a[0] - b[0]) < EPS:
        return abs(p[0] - a[0]) < EPS and min(a[1], b[1]) + EPS < p[1] < max(a[1], b[1]) - EPS
    return abs(p[1] - a[1]) < EPS and min(a[0], b[0]) + EPS < p[0] < max(a[0], b[0]) - EPS


def build_wall(B, spec, level):
    """One elevation: its cells, each holed for the items inside it, or
    notched at its foot for an item that stands on the ground. Every cell
    corner that lies on another cell's edge is put on that edge too, so the
    cells meet vertex to vertex."""
    fr = Frame(spec["p0"], spec["p1"])
    cells = wall_cells(spec, fr)
    corners = {(round(s, 6), round(z, 6)) for s0, s1, z0, z1, _ in cells
               for s, z in ((s0, z0), (s1, z0), (s1, z1), (s0, z1))}
    feats = []
    for kind, s in spec["items"]:
        (l, r, b, t), _ = item_rect(kind, s)
        feats.append(dict(kind=kind, s=s, l=l, r=r, b=b, t=t))
    for s0, s1, z0, z1, uvfn in cells:
        mine = [f for f in feats if f["l"] > s0 - EPS and f["r"] < s1 + EPS
                and f["b"] > z0 - EPS and f["t"] < z1 + EPS]
        for f in feats:
            if f not in mine and f["l"] < s1 - EPS and s0 + EPS < f["r"] \
                    and f["b"] < z1 - EPS and z0 + EPS < f["t"]:
                raise ValueError("%s: the %s crosses a cell edge" % (spec["name"], f["kind"]))
        holes, notches = [], []
        for f in mine:
            ring = build_item(B, fr, spec, f["kind"], f["s"], level)
            if f["b"] < z0 + EPS:
                notches.append((f["l"], ring))
            else:
                holes.append(ring)
        edges = [((s0, z0), (s1, z0)), ((s1, z0), (s1, z1)), ((s1, z1), (s0, z1)),
                 ((s0, z1), (s0, z0))]
        outline = []
        for k, (a, b) in enumerate(edges):
            outline.append(a)
            marks = [("pt", p) for p in corners if _on_edge(p, a, b)]
            if k == 0:
                marks += [("notch", n) for n in notches]

            def key(mk, a=a, b=b):
                q = mk[1] if mk[0] == "pt" else (mk[1][0], z0)
                return (q[0] - a[0]) * (b[0] - a[0]) + (q[1] - a[1]) * (b[1] - a[1])
            for what, val in sorted(marks, key=key):
                if what == "pt":
                    outline.append(val)
                else:
                    outline += _notch_path(val[1])
        fill_region(B, fr, SB.dedupe(outline), holes, uvfn)


def _notch_path(ring):
    """A ground-standing item's outline as the cell's foot walks round it:
    from its bottom left up its left side, over its top, down its right."""
    return [ring[0]] + list(reversed(ring[1:]))


def main_body(level):
    """The wall ring, capped by a floor on the ground and a lid at the wall
    top (shell_build.close_solid())."""
    B = Builder()
    for spec in WALLS:
        build_wall(B, spec, level)
    SB.close_solid(B, uv_patch("blank"))
    return B


# ================================================================== roof
EAVES = [  # (eave line start, end) on the eave outline, counter-clockwise, and its wall
    ((-EX, -EY), (EX, -EY), "front"), ((EX, -EY), (EX, EY), "east"),
    ((EX, EY), (-EX, EY), "rear"), ((-EX, EY), (-EX, -EY), "west")]
U_ROOF = {"front": 0.0, "east": 4.0, "rear": 8.0, "west": 12.0}


def _eave_frame(a, b):
    fr = Frame(a, b)
    return fr


def uv_slope(fr, u_off):
    """The roof band: U along the eave, V up the slope from the fascia."""
    return lambda co: ((fr.s_of(co) + u_off) * PPM,
                       L.ROOF_Y0 + max(0.0, -fr.out_of(co)) * SLOPE_K * L.ROOF_RPM)


def uv_fascia(fr, u_off):
    return lambda co: ((fr.s_of(co) + u_off) * PPM, L.FASC_Y0 + (co.z - L.Z_EAVE) * PPM)


def uv_soffit(fr, u_off):
    """*fr* is the wall's line; v is the distance out from its face."""
    return lambda co: ((fr.s_of(co) + u_off) * PPM,
                       L.SOF_Y0 + min(EO, max(0.0, fr.out_of(co))) * PPM)


def roof():
    """The hipped roof as one closed solid: four slopes rising from the
    fascia's top to a ridge RX each side of the centre (two trapezoids and
    two triangles, every hip in plan at 45 degrees since the pitches are
    equal), the fascia all round, the level soffit back to the wall line and
    the underside inside it, which the union buries in the body."""
    B = Builder()
    F = [(-EX, -EY), (EX, -EY), (EX, EY), (-EX, EY)]
    W = [(-HX, -HY), (HX, -HY), (HX, HY), (-HX, HY)]
    R0, R1 = (-RX, 0.0, L.Z_RIDGE), (RX, 0.0, L.Z_RIDGE)
    zt, zb = L.Z_FT, L.Z_EAVE
    top = {"front": [F[0], F[1], R1, R0], "east": [F[1], F[2], R1],
           "rear": [F[2], F[3], R0, R1], "west": [F[3], F[0], R0]}
    for k, (a, b, name) in enumerate(EAVES):
        fr = _eave_frame(a, b)
        u0 = U_ROOF[name]
        pts = [p if len(p) == 3 else (p[0], p[1], zt) for p in top[name]]
        B.face(pts, uv_slope(fr, u0))
        fa, fb = F[k], F[(k + 1) % 4]
        B.face([(fa[0], fa[1], zb), (fb[0], fb[1], zb), (fb[0], fb[1], zt),
                (fa[0], fa[1], zt)], uv_fascia(fr, u0))
        wa, wb = W[k], W[(k + 1) % 4]
        B.face([(fa[0], fa[1], zb), (wa[0], wa[1], zb), (wb[0], wb[1], zb),
                (fb[0], fb[1], zb)], uv_soffit(Frame(wa, wb), u0 + 0.0))
    B.face([(x, y, zb) for x, y in W], uv_patch("blank"))
    return B


def cap(p0, p1, uvfn):
    """A flashing along the roof line p0 -> p1 (3D), its five-sided section
    in vertical planes across the line's plan direction."""
    B = Builder()
    d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0)).normalized()
    lat = Vector((-d.y, d.x, 0.0))
    rings = []
    for p in (p0, p1):
        rings.append([(p[0] + lat.x * a, p[1] + lat.y * a, p[2] + z) for a, z in CAP_SECTION])
    n = len(CAP_SECTION)
    for k in range(n):
        B.face([rings[0][k], rings[0][(k + 1) % n], rings[1][(k + 1) % n], rings[1][k]], uvfn)
    B.face(list(reversed(rings[0])), uvfn)
    B.face(rings[1], uvfn)
    return B


def caps():
    """The ridge flashing and the four hip flashings, each stopping short of
    its eave corner so nothing reaches past the fascia's outline."""
    fn = uv_patch("flashing")
    out = [(cap((-RX - 0.05, 0.0, L.Z_RIDGE), (RX + 0.05, 0.0, L.Z_RIDGE), fn), "tmp_ridge")]
    for i, (cx, cy) in enumerate(((-EX, -EY), (EX, -EY), (EX, EY), (-EX, EY))):
        rx = RX if cx > 0 else -RX
        run = math.hypot(cx - rx, cy)
        k = 1.0 - CAP_CORNER * math.sqrt(2.0) / run
        end = (rx + (cx - rx) * k, cy * k, L.Z_RIDGE + (L.Z_FT - L.Z_RIDGE) * k)
        out.append((cap((rx, 0.0, L.Z_RIDGE), end, fn), "tmp_hip%d" % i))
    return out


def blades(fr, s0, s1, tops, name):
    """Sawtooth louvre blades on the face of frame *fr*, from s0 to s1 along
    it: under each top edge in *tops* a solid whose sloping face runs from
    the face down and out LOUV_D to its drip, LOUV_T below, and whose level
    underside runs back into the face; its back is buried 10 mm."""
    T, D = L.LOUV_T, L.LOUV_D
    blade, shadow = uv_patch("blade"), uv_patch("shadow")
    out = []
    for i, zt in enumerate(tops):
        B = Builder()
        sec = [(-0.01, zt + 0.01 * T / D), (D, zt - T), (-0.01, zt - T)]
        a = [fr.P(s0, z, o) for o, z in sec]
        b = [fr.P(s1, z, o) for o, z in sec]
        B.face([a[0], a[1], b[1], b[0]], blade)
        B.face([a[1], a[2], b[2], b[1]], shadow)
        B.face([a[2], a[0], b[0], b[2]], shadow)
        B.face([a[2], a[1], a[0]], blade)
        B.face([b[0], b[1], b[2]], blade)
        out.append((B, "tmp_%s%d" % (name, i)))
    return out


def hip_lid(x0, x1, y0, y1, zb, zd, rise):
    """A lid: a slab from zb to its drip edge's top zd, under a hipped top
    rising *rise* to a ridge along X (equal pitches)."""
    B = Builder()
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    half = max((x1 - x0) - (y1 - y0), 0.0) / 2.0
    r0, r1 = (cx - half, cy, zd + rise), (cx + half, cy, zd + rise)
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    drip, top, under = uv_patch("lid"), uv_patch("canopy_top"), uv_patch("shadow")
    for k in range(4):
        (ax, ay), (bx, by) = ring[k], ring[(k + 1) % 4]
        B.face([(ax, ay, zb), (bx, by, zb), (bx, by, zd), (ax, ay, zd)], drip)
    B.face([(x0, y0, zd), (x1, y0, zd), r1, r0], top)
    B.face([(x1, y0, zd), (x1, y1, zd), r1], top)
    B.face([(x1, y1, zd), (x0, y1, zd), r0, r1], top)
    B.face([(x0, y1, zd), (x0, y0, zd), r0], top)
    B.face([(x, y, zb) for x, y in reversed(ring)], under)
    return B


def housing(level):
    """The ventilation housing on the ridge, a sheet-steel box whose foot is
    buried in both slopes. Up close (housing_mode "full") its four sides
    carry modelled louvre blades over their painted slots, a flashing skirt
    follows the slopes round its foot 0.10 m up, and a hipped lid oversails
    it with a drip edge; at LOD2 the lid is a plain slab; at LOD3 the box
    stands bare. Each side maps onto the housing art of its width."""
    mode = housing_mode(level)
    hx, hy = L.HOUSING_HALF
    z0 = L.Z_RIDGE - L.HOUSING_BURY
    z1 = L.Z_RIDGE + L.HOUSING_UP
    k = L.HOUSING_PPM
    corners = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
    frames = [Frame(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    rects = [L.HOUSING_X, L.HOUSING_Y, L.HOUSING_X, L.HOUSING_Y]
    B = Builder()
    for fr, rect in zip(frames, rects):
        B.face([fr.P(0.0, z0), fr.P(fr.L, z0), fr.P(fr.L, z1), fr.P(0.0, z1)],
               SB.uv_region(fr, rect, 0.0, z0, k))
    lid = uv_patch("lid")
    B.face([(x, y, z1) for x, y in corners], lid)
    B.face([(x, y, z0) for x, y in reversed(corners)], lid)
    out = [(B, "tmp_housing")]
    if mode == "box":
        return out
    d, o = L.HOUSING_LID
    if mode == "lid":
        out.append((SB.box(Builder(), -hx - o, hx + o, -hy - o, hy + o, z1 - 0.02, z1 + d,
                           lid, lid, uv_patch("shadow")), "tmp_lid"))
        return out
    out.append((hip_lid(-hx - o, hx + o, -hy - o, hy + o, z1 - 0.02, z1 - 0.02 + d,
                        L.HOUSING_LID_RISE), "tmp_lid"))
    tops = L.blade_tops(L.Z_RIDGE + L.LOUV_Z[0], L.Z_RIDGE + L.LOUV_Z[1])
    for i, fr in enumerate(frames):
        out += blades(fr, L.LOUV_INSET, fr.L - L.LOUV_INSET, tops, "blade%d_" % i)
    # the skirt: a prism along X whose top follows both slopes SKIRT[1] up
    e, up = L.SKIRT
    ye = hy + e
    zs = L.Z_RIDGE - L.TAN * ye + up
    sec = [(-ye, z0 + 0.05), (ye, z0 + 0.05), (ye, zs), (0.0, L.Z_RIDGE + up), (-ye, zs)]
    S = Builder()
    fl = uv_patch("flashing")
    xa, xb = -hx - e, hx + e
    n = len(sec)
    for i in range(n):
        (ya, za), (yb, zb) = sec[i], sec[(i + 1) % n]
        S.face([(xa, ya, za), (xa, yb, zb), (xb, yb, zb), (xb, ya, za)], fl)
    S.face([(xa, yy, zz) for yy, zz in reversed(sec)], fl)
    S.face([(xb, yy, zz) for yy, zz in sec], fl)
    out.append((S, "tmp_skirt"))
    return out


def roof_z(x, y):
    """The roof's top surface over plan point (x, y): the lowest of the four
    slopes' planes, as a hipped roof is."""
    return L.Z_FT + L.TAN * min(EY + y, EY - y, EX + x, EX - x)


def _prism_x(x0, x1, sec, fns, end):
    """A closed prism along X from x0 to x1 over the (y, z) section *sec*;
    fns[k] maps the face over the section's edge k, *end* both ends."""
    B = Builder()
    n = len(sec)
    for k in range(n):
        (y0, z0), (y1, z1) = sec[k], sec[(k + 1) % n]
        B.face([(x0, y0, z0), (x1, y0, z0), (x1, y1, z1), (x0, y1, z1)], fns[k])
    B.face([(x0, yy, zz) for yy, zz in sec], end)
    B.face([(x1, yy, zz) for yy, zz in reversed(sec)], end)
    return B


def hood(level):
    """The louvred attic vent on the front slope: a closed solid whose
    section across X is its vertical louvred front, its top falling
    HOOD_FALL a metre toward the front, and a back and a foot buried in the
    roof; the union keeps what stands above the sheet. Up close
    (hood_mode()) the front carries modelled blades over its painted slots
    and a cap plate oversails the top, front and sides, its front edge a
    drip; farther, the wedge alone with the louvre painted."""
    zf = roof_z(0.0, HOOD_Y)
    top_f = zf + HOOD_FACE
    foot = zf - L.HOOD_FOOT
    yb = HOOD_Y + HOOD_FACE / (L.TAN - HOOD_FALL) + 0.15
    sec = [(HOOD_Y, foot), (HOOD_Y, top_f),
           (yb, top_f + (yb - HOOD_Y) * HOOD_FALL), (yb, foot)]
    front = Frame((-HOOD_X, HOOD_Y), (HOOD_X, HOOD_Y))
    louvre = SB.uv_region(front, L.HOOD, 0.0, foot, L.HOUSING_PPM)
    fns = (louvre, uv_patch("canopy_top"), uv_patch("blank"), uv_patch("blank"))
    out = [(_prism_x(-HOOD_X, HOOD_X, sec, fns, uv_patch("lid")), "tmp_hood")]
    if not hood_mode(level):
        return out
    tops = L.blade_tops(zf + L.HOOD_LOUV_Z[0], zf + L.HOOD_LOUV_Z[1])
    out += blades(front, L.LOUV_INSET, L.HOOD_W - L.LOUV_INSET, tops, "hood_blade")
    f, s, above, below = HOOD_CAP
    ya = HOOD_Y - f

    def top(yy, dz):
        return top_f + (yy - HOOD_Y) * HOOD_FALL + dz
    cap_sec = [(ya, top(ya, -below)), (yb, top(yb, -below)), (yb, top(yb, above)),
               (ya, top(ya, above))]
    lid = uv_patch("lid")
    out.append((_prism_x(-HOOD_X - s, HOOD_X + s, cap_sec,
                         (uv_patch("shadow"), uv_patch("blank"), uv_patch("canopy_top"), lid),
                         lid), "tmp_hood_cap"))
    return out


def fitting_solids(level):
    """The small fittings this tier keeps (fittings()), each a box let
    FIT_BURY into its wall, its faces on the atlas's fitting art."""
    k = L.FIT_PPM
    fr, rear = frame_of("front"), frame_of("rear")
    out = []
    lamp_top, opal, rim = uv_patch("lamp_body"), uv_patch("opal"), uv_patch("sign_rim")

    def lamp(fr, at, name):
        w, h, d = L.LAMP_M
        s0, z0 = at[0] - w / 2.0, at[1]
        x, y, _w, _h = L.LAMP_SIDE
        ends = lambda co: (x + fr.out_of(co) * k, y + (co.z - z0) * k)  # noqa: E731
        out.append((wall_box(fr, s0, s0 + w, -FIT_BURY, d, z0, z0 + h,
                             SB.uv_region(fr, L.LAMP_FRONT, s0, z0, k), lamp_top, opal, ends),
                    name))
    for what in fittings(level):
        if what == "front_lamp":
            lamp(fr, FRONT_LAMP, "tmp_front_lamp")
        elif what == "rear_lamp":
            lamp(rear, REAR_LAMP, "tmp_rear_lamp")
        elif what == "number":
            w, h, d = L.NUMBER_M
            s0, z0 = NUMBER_AT[0] - w / 2.0, NUMBER_AT[1]
            out.append((wall_box(fr, s0, s0 + w, -FIT_BURY, d, z0, z0 + h,
                                 SB.uv_region(fr, L.NUMBER, s0, z0, k), rim, rim, rim),
                        "tmp_number"))
        elif what == "hours":
            w, h, d = L.HOURS_M
            s0, z0 = HOURS_AT[0] - w / 2.0, HOURS_AT[1]
            edge = uv_patch("lamp_body")
            out.append((wall_box(fr, s0, s0 + w, -FIT_BURY, d, z0, z0 + h,
                                 SB.uv_region(fr, L.HOURS, s0, z0, k), edge, edge, edge),
                        "tmp_hours"))
        elif what == "lobby_lamp":
            w, d, h = L.LOBBY_LAMP_M
            sc = dict(WALL["front"]["items"])["screen"]
            zt = L.ITEMS["screen"]["z1"]
            out.append((wall_box(fr, sc - w / 2.0, sc + w / 2.0, LOBBY_LAMP_OUT - d / 2.0,
                                 LOBBY_LAMP_OUT + d / 2.0, zt - h, zt + 0.03,
                                 lamp_top, uv_patch("blank"), opal, lamp_top),
                        "tmp_lobby_lamp"))
    return out


def vent_pipe():
    """A soil vent pipe through the rear slope, octagonal, its foot buried."""
    (px, py), r, h = VENT
    z0 = roof_z(px, py) - 0.20
    z1 = roof_z(px, py) + h
    ring = [(px + r * math.cos(math.pi / 8 + k * math.pi / 4),
             py + r * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    cap_ = uv_patch("lid")
    return SB.prism(Builder(), ring, z0, z1, uv_patch("flashing"), cap_, cap_)


def wall_box(fr, s0, s1, o0, o1, z0, z1, side, top=None, bottom=None, ends=None):
    """A closed box in a wall's frame: s along it, out away from it. *side*
    maps the faces parallel to the wall, *ends* the faces across it."""
    B = Builder()
    ring = [(s0, o1), (s1, o1), (s1, o0), (s0, o0)]
    fns = [side, ends or side, side, ends or side]
    for k in range(4):
        (sa, oa), (sb, ob) = ring[k], ring[(k + 1) % 4]
        B.face([fr.P(sa, z0, oa), fr.P(sb, z0, ob), fr.P(sb, z1, ob), fr.P(sa, z1, oa)], fns[k])
    B.face([fr.P(s, z1, o) for s, o in ring], top or side)
    B.face([fr.P(s, z0, o) for s, o in reversed(ring)], bottom or side)
    return B


def sign_band():
    """The brown sheet band across the front under the eave, BAND_OUT proud
    of the brick, its back in the wall and its top in the roof slab."""
    fr = frame_of("front")
    a, b = L.SIGN_BAND_S
    edge = uv_patch("band_edge")
    B = Builder()
    o0, o1 = -0.05, BAND_OUT
    z0, z1 = L.Z_BAND0, L.Z_EAVE + 0.05
    face = uv_band(fr)
    B.face([fr.P(a, z0, o1), fr.P(b, z0, o1), fr.P(b, z1, o1), fr.P(a, z1, o1)], face)
    B.face([fr.P(b, z0, o0), fr.P(a, z0, o0), fr.P(a, z1, o0), fr.P(b, z1, o0)], edge)
    B.face([fr.P(a, z0, o0), fr.P(a, z0, o1), fr.P(a, z1, o1), fr.P(a, z1, o0)], edge)
    B.face([fr.P(b, z0, o1), fr.P(b, z0, o0), fr.P(b, z1, o0), fr.P(b, z1, o1)], edge)
    B.face([fr.P(a, z1, o0), fr.P(a, z1, o1), fr.P(b, z1, o1), fr.P(b, z1, o0)], edge)
    B.face([fr.P(a, z0, o1), fr.P(a, z0, o0), fr.P(b, z0, o0), fr.P(b, z0, o1)], edge)
    return B


def light_box(level):
    """The projecting light box and its arms. Both faces carry the same art,
    each mapped to read left to right from its own side; the rims are the
    dark aluminium frame."""
    fr = frame_of("front")
    s0, s1 = BOX_S - BOX_T / 2.0, BOX_S + BOX_T / 2.0
    o0, o1 = BOX_OUT
    z0, z1 = BOX_Z
    x, y, w, h = L.SIGN_BOX
    rim = uv_patch("sign_rim")
    span = L.SIGN_BOX_M

    def face(sign):
        # seen from +s the face's right is toward the wall (out falling)
        if sign > 0:
            return lambda co: (x + (o1 - fr.out_of(co)) / span * w, y + (co.z - z0) / span * h)
        return lambda co: (x + (fr.out_of(co) - o0) / span * w, y + (co.z - z0) / span * h)
    B = Builder()
    B.face([fr.P(s1, z0, o0), fr.P(s1, z0, o1), fr.P(s1, z1, o1), fr.P(s1, z1, o0)], face(1))
    B.face([fr.P(s0, z0, o1), fr.P(s0, z0, o0), fr.P(s0, z1, o0), fr.P(s0, z1, o1)], face(-1))
    B.face([fr.P(s0, z0, o0), fr.P(s1, z0, o0), fr.P(s1, z1, o0), fr.P(s0, z1, o0)], rim)
    B.face([fr.P(s1, z0, o1), fr.P(s0, z0, o1), fr.P(s0, z1, o1), fr.P(s1, z1, o1)], rim)
    B.face([fr.P(s0, z1, o0), fr.P(s1, z1, o0), fr.P(s1, z1, o1), fr.P(s0, z1, o1)], rim)
    B.face([fr.P(s0, z0, o1), fr.P(s1, z0, o1), fr.P(s1, z0, o0), fr.P(s0, z0, o0)], rim)
    out = [(B, "tmp_box")]
    br = uv_patch("bracket")
    for i, (za, zb) in enumerate(arms(level)):
        out.append((wall_box(fr, BOX_S - ARM_W / 2.0, BOX_S + ARM_W / 2.0, ARM_OUT[0],
                             ARM_OUT[1], za, zb, br), "tmp_arm%d" % i))
    return out


def canopy():
    """The service door's canopy: a flat steel tray let into the rear wall."""
    fr = frame_of("rear")
    return wall_box(fr, CANOPY_S[0], CANOPY_S[1], -0.05, CANOPY_OUT, CANOPY_Z[0], CANOPY_Z[1],
                    uv_patch("canopy_edge"), uv_patch("canopy_top"), uv_patch("canopy_under"))


# ================================================================== assembly
def kit(level, extents=False):
    """The roof safety kit's solids for this tier. The wall ladder sets the
    rear of the plan bounds, so the tier that drops the kit keeps its bare
    rails (extents=True), appended after the weld."""
    if extents:
        return RS.solids([WALL_LADDER], level, PAINT, extents=True)
    return RS.solids([WALL_LADDER, ROOF_LADDER], level, PAINT)


def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    parts = [to_object(roof(), "tmp_roof")]
    if caps_kept(level):
        parts += [to_object(B, n) for B, n in caps()]
    parts += [to_object(B, n) for B, n in housing(level)]
    parts += [to_object(B, n) for B, n in hood(level)]
    parts += [to_object(B, n) for B, n in fitting_solids(level)]
    if vent_kept(level):
        parts.append(to_object(vent_pipe(), "tmp_vent"))
    if band_modelled(level):
        parts.append(to_object(sign_band(), "tmp_band"))
    parts += [to_object(B, n) for B, n in light_box(level)]
    if canopy_kept(level):
        parts.append(to_object(canopy(), "tmp_canopy"))
    parts += [to_object(B, n) for B, n in
              DP.solids(DOWNPIPES, *DP.MODES[level], L.PIPE_STRIP, L.ATLAS)]
    drop_kit = RS.MODES[level][0] is None
    if not drop_kit:
        parts += [to_object(B, n) for B, n in kit(level)]
    obj = union(base, parts, snap=asset_build.SNAP)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # 0.1 mm: the snap grid; the smallest authored feature is the kit's 3 cm rung
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # recover coplanar boolean subdivisions; keep UV seams and every
        # architectural edge
        bmesh.ops.dissolve_limit(bm, angle_limit=0.001, verts=bm.verts[:],
                                 edges=bm.edges[:], delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    if drop_kit:
        RS.append(obj, kit(level, extents=True), check=True)
    return obj


# ================================================================== checks
def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    rects = {}
    for spec in WALLS:
        fr = Frame(spec["p0"], spec["p1"])
        rs = []
        for kind, s in spec["items"]:
            (l, r, b, t), (zb, zt) = item_rect(kind, s)
            rs.append((kind, l, r, b, t))
            if l < 0.4 or r > fr.L - 0.4:
                bad.append("%s: the %s is within 0.4 m of a corner" % (spec["name"], kind))
            if t > L.Z_BAND0 - L.COURSE + EPS:
                bad.append("%s: the %s reaches the sign band's course" % (spec["name"], kind))
        for i, a in enumerate(rs):
            for b in rs[i + 1:]:
                if a[1] < b[2] + 0.4 and b[1] < a[2] + 0.4:
                    bad.append("%s: the %s and the %s are under 0.4 m apart"
                               % (spec["name"], a[0], b[0]))
        rects[spec["name"]] = rs
    for a, b in zip(WALLS, WALLS[1:] + WALLS[:1]):
        if tuple(a["p1"]) != tuple(b["p0"]):
            bad.append("the wall ring breaks between %s and %s" % (a["name"], b["name"]))
    # human scale
    if not 2.0 <= L.Z_LEAF <= 2.4:
        bad.append("the entrance leaf is %.3f m, outside 2.0-2.4" % L.Z_LEAF)
    if L.Z_HEAD < L.Z_LEAF + 0.15:
        bad.append("no transom light over the entrance leaf")
    if not 2.0 <= L.SERVICE_LEAF[1] <= 2.4:
        bad.append("the service leaf is %.3f m, outside 2.0-2.4" % L.SERVICE_LEAF[1])
    if L.SERVICE_LEAF[1] > L.Z_SERVICE_HEAD - 0.03 or \
            L.SERVICE_LEAF[0] > L.ITEMS["service_door"]["w"] - 0.06 + EPS:
        bad.append("the service leaf does not fit inside its frame")
    # the brickwork: every height the walls share with the coursing on a
    # course line; every corner, opening side and lobby cheek on a whole or
    # half stretcher; corners and cheeks turning a half stretcher out of step
    half = L.BRICK_L / 2.0

    def on(v, step):
        return abs(v / step - round(v / step)) < 1e-6
    for what, z in (("plinth", L.Z_PLINTH), ("sign band", L.Z_BAND0),
                    ("wall top", L.Z_TOP)):
        if not on(z, L.COURSE):
            bad.append("the %s at %.4f m is off the coursing" % (what, z))
    for kind, it in L.ITEMS.items():
        if not all(on(z, L.COURSE) for z in L.item_box(kind) + (it["z0"], it["z1"])):
            bad.append("the %s's heights are off the coursing" % kind)
        if not on(it["w"], half):
            bad.append("the %s is not a whole number of half stretchers wide" % kind)
    for spec in WALLS:
        for kind, s in spec["items"]:
            (l, r, _b, _t), _ = item_rect(kind, s)
            if not (on(spec["u"] + l, half) and on(spec["u"] + r, half)):
                bad.append("%s: the %s cuts the bond off a half stretcher"
                           % (spec["name"], kind))
    for a, b in zip(WALLS, WALLS[1:] + WALLS[:1]):
        end = a["u"] + Frame(a["p0"], a["p1"]).L
        if not (on(b["u"], half) and on(end - b["u"] - half, L.BRICK_L)):
            bad.append("the %s/%s corner does not turn the bond" % (a["name"], b["name"]))
    (sl, sr, _b, _t), _ = item_rect("screen", dict(WALL["front"]["items"])["screen"])
    for edge, cu in ((sl, CHEEK_U[0]), (sr, CHEEK_U[0] + CHEEK_U[1])):
        if not on(edge - cu - half, L.BRICK_L):
            bad.append("a lobby cheek does not turn the bond at the lobby's mouth")
    if not (on(L.ATLAS, L.BRICK_PX) and on(L.BRICK_PX, 1.0) and on(L.COURSE_PX, 1.0)
            and on(L.BRICK_H, L.COURSE_PX)):
        bad.append("the brick band does not tile on whole pixels")
    wins = [s for k, s in WALL["front"]["items"] if k == "window"]
    if abs(sum(wins) / len(wins) - L.LETTERS_S) > EPS:
        bad.append("the band's letters are not centred over the two windows")
    for kind in ("window", "side_window", "small_window"):
        z0 = L.ITEMS[kind]["z0"]
        if not 0.8 <= z0 <= 1.4:
            bad.append("the %s's sill is %.3f m, outside 0.8-1.4" % (kind, z0))
        if abs(L.ITEMS[kind]["z1"] - L.ITEMS["screen"]["z1"]) > EPS:
            bad.append("the %s's head is off the entrance's head line" % kind)
    # the lobby
    scr = L.ITEMS["screen"]
    if not (0.8 <= scr["depth"] <= 1.0 and 2.0 <= scr["w"] <= 2.4):
        bad.append("the lobby is not a 0.8-1.0 m deep, ~2.2 m wide recess")
    if L.DOOR_S0 + L.DOOR_LEAF_W + 2 * L.SCREEN_FRAME > scr["w"] - 0.5:
        bad.append("the screen has no room for its sidelight")
    # the eave and the roof
    if not 0.3 <= EO <= 0.6:
        bad.append("the eave projects %.3f m, outside 0.3-0.6" % EO)
    pitch = math.degrees(math.atan(L.TAN))
    if not 20.0 <= pitch <= 25.0:
        bad.append("the roof pitch is %.1f degrees, outside 20-25" % pitch)
    if L.TAN <= 1.0 / 8.0:
        bad.append("the roof is not steeper than 1:8: the kit's rule would not apply")
    if abs(L.SLOPE_LEN * L.ROOF_RPM - L.ROOF_H) > 1e-6:
        bad.append("the roof band's height is not the slope's")
    if not 3.0 <= L.Z_EAVE <= 3.35:
        bad.append("the eave is at %.3f m, outside about 3.0-3.3" % L.Z_EAVE)
    band = L.Z_EAVE - L.Z_BAND0
    if not 0.5 <= band <= 0.6:
        bad.append("the sign band is %.3f m tall, outside 0.5-0.6" % band)
    # the housing on the ridge, inside the slopes and clear of the hips
    hx, hy = L.HOUSING_HALF
    t, o = L.HOUSING_LID
    if hx + o > RX + hy - 0.05:
        bad.append("the housing reaches a hip")
    if L.Z_RIDGE - hy * L.TAN < L.Z_RIDGE - L.HOUSING_BURY + 0.1:
        bad.append("the housing's foot is not buried in the slopes")
    # the light box: clear of the band, the lobby and the window, arms in brick
    if BOX_OUT[0] <= BAND_OUT + 0.03 and BOX_Z[1] > L.Z_BAND0:
        bad.append("the light box touches the sign band")
    front = {k: (l, r) for k, l, r, b, t in rects["front"]}
    if not (front["screen"][1] + 0.3 < BOX_S - BOX_T / 2 and
            BOX_S + BOX_T / 2 + 0.3 < min(l for k, l, r, b, t in rects["front"]
                                          if k == "window")):
        bad.append("the light box crowds the lobby or a window")
    for za, zb in ARMS:
        if not (BOX_Z[0] + 0.05 < za < zb < min(BOX_Z[1] - 0.05, L.Z_BAND0 - 0.02)):
            bad.append("a light box arm is not inside the box and under the band")
    if not (BOX_Z[0] >= 2.2 and BOX_Z[1] <= L.Z_EAVE - 0.2):
        bad.append("the light box is not clear over a head and under the soffit")
    # the canopy over the service door
    rear = {k: (l, r, b, t) for k, l, r, b, t in rects["rear"]}
    sd = rear["service_door"]
    if not (CANOPY_S[0] < sd[0] and sd[1] < CANOPY_S[1] and CANOPY_Z[0] > sd[3] + 0.03):
        bad.append("the canopy does not cover the service door clear of its soldiers")
    # downpipes and the roof safety kit
    for pipe, name in zip(DOWNPIPES, ("west", "east")):
        avoid = [(k, l, r) for k, l, r, b, t in rects[name]]
        bad += DP.problems(pipe, "the %s downpipe" % name, avoid)
    avoid = [(k, l, r) for k, l, r, b, t in rects["rear"]]
    avoid.append(("canopy", CANOPY_S[0], CANOPY_S[1]))
    bad += RS.problems(WALL_LADDER, "the wall ladder", avoid)
    if (HY - hy - max(o, L.SKIRT[0])) - abs(ROOF_TOP_OUT) < 0.2:
        bad.append("the roof ladder runs into the housing, its skirt or its lid")
    # the louvre blades: a whole blade fits each band, and they stay clear
    # of the skirt below and the lid above
    tops = L.blade_tops(L.Z_RIDGE + L.LOUV_Z[0], L.Z_RIDGE + L.LOUV_Z[1])
    if len(tops) < 3:
        bad.append("the housing's louvre has fewer than three blades")
    if tops[-1] - L.LOUV_T < L.Z_RIDGE + L.SKIRT[1] + 0.02:
        bad.append("the housing's lowest blade sits on the skirt")
    if tops[0] > L.Z_RIDGE + L.HOUSING_UP - 0.04:
        bad.append("the housing's top blade runs under the lid")
    if len(L.blade_tops(L.HOOD_LOUV_Z[0], L.HOOD_LOUV_Z[1])) < 3 or \
            L.HOOD_LOUV_Z[1] > HOOD_FACE - HOOD_CAP[3]:
        bad.append("the hood's louvre does not fit under its cap")
    # the fittings: on their piers, clear of openings, corners and each other
    front = {k: (l, r, b, t) for k, l, r, b, t in rects["front"]}
    lw, lh, _ = L.LAMP_M
    nw, nh, _ = L.NUMBER_M
    hw, hh, _ = L.HOURS_M
    lamp_r = FRONT_LAMP[0] + lw / 2.0
    if FRONT_LAMP[0] - nw / 2.0 < 0.3 or max(lamp_r, NUMBER_AT[0] + nw / 2.0) > \
            front["screen"][0] - 0.2:
        bad.append("the front lamp or the house number crowds the corner or the lobby")
    if FRONT_LAMP[1] + lh > NUMBER_AT[1] - 0.08 or NUMBER_AT[1] + nh > L.Z_BAND0 - 0.08:
        bad.append("the front lamp, the house number and the band overlap")
    if FRONT_LAMP[1] < 1.9:
        bad.append("the front lamp hangs below head height")
    win = min(l for k, l, r, b, t in rects["front"] if k == "window")
    if not (front["screen"][1] + 0.15 < HOURS_AT[0] - hw / 2.0 and
            HOURS_AT[0] + hw / 2.0 < win - 0.15 and HOURS_AT[1] + hh < BOX_Z[0] - 0.3):
        bad.append("the opening-hours board crowds the lobby, a window or the light box")
    if abs(LOBBY_LAMP_OUT) + L.LOBBY_LAMP_M[1] / 2.0 > L.ITEMS["screen"]["depth"] - 0.1:
        bad.append("the lobby light reaches the screen")
    rear_d = rear["service_door"]
    if not (CANOPY_S[1] + 0.1 < REAR_LAMP[0] - lw / 2.0 and REAR_LAMP[0] + lw / 2.0 < 9.6):
        bad.append("the rear lamp crowds the canopy or the corner (door at %.2f-%.2f)"
                   % (rear_d[0], rear_d[1]))
    # plan bounds within the brief's 11.5 x 9.5 m
    front_y = HY + BOX_OUT[1]
    rear_y = HY + WALL_LADDER.standoff + RS.RAIL_D
    if 2 * EX > 11.5 or front_y + rear_y > 9.5:
        bad.append("the plan bounds %.2f x %.2f m exceed 11.5 x 9.5"
                   % (2 * EX, front_y + rear_y))
    return bad


# ================================================================== build
def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the wall ring at ground level; the
    entrance lobby is a recess in the front wall and leaves the outline
    straight, so the entrance stands on the front wall plane, at the leaf's
    centre, though the leaf itself is 0.88 m back in the lobby. One storey,
    the ring's area less the lobby's; no dwellings."""
    ring = [w["p0"] for w in WALLS]
    area = abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(ring, ring[1:] + ring[:1]))) / 2.0
    scr = L.ITEMS["screen"]
    area -= scr["w"] * scr["depth"]
    fs = dict(WALL["front"]["items"])["screen"]
    leaf_s = fs - scr["w"] / 2.0 + L.DOOR_S0 + L.DOOR_LEAF_W / 2.0
    rs = dict(WALL["rear"]["items"])["service_door"]
    doors = [
        model_facts.wall_door("barber", "entrance", WALL["front"]["p0"], WALL["front"]["p1"],
                              leaf_s, 0.0, L.DOOR_LEAF_W, L.Z_LEAF, main=True),
        model_facts.wall_door("staff", "service", WALL["rear"]["p0"], WALL["rear"]["p1"],
                              rs, 0.0, L.SERVICE_LEAF[0], L.SERVICE_LEAF[1]),
    ]
    return {"hero": False, "dwellings": 0, "footprint": ring,
            "storeys": [(0.0, area)], "doors": doors}


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views (shell_build.render_views()), plus a rear
    aerial, an eye-level street view and an entrance view, with a 1.8 m
    figure by the lobby's mouth. Working views only."""
    return SB.render_views(BUILD, out_dir, level, res, views=(
        SB.AERIAL, SB.AERIAL_REAR,
        SB.look("street", (6.0, -17.0, 1.7), (0.0, -4.0, 2.4)),
        SB.look("entrance", (1.5, -10.0, 1.7), (-2.2, -4.0, 1.9))),
        figures=[(-1.4, -HY - 1.6)])


if __name__ == "__main__":
    BUILD.main(build_all, facts)
