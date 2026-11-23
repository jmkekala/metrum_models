# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of brick_clocktower_hall, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite late-19th-century Nordic civic hall: a long two-storey front
range in red brick with white trim between projecting end pavilions, a
forward centre entrance bay under a clock attic and pediment, rear wings and
a centre link round a U-shaped court, a low truncated-hip roof of dark
painted steel over one flat deck, a slender clock tower with a balustraded
platform, a round dome, a ball and a flagpole, six open chimney stacks.

Construction: closed solids unioned with Blender's exact boolean
(asset_build.union, snapped to 0.1 mm) -- the body (the wall ring with every
opening, capped with a floor and a lid at Z_TOP, inside the roof), the roof
(soffit, fascia, slopes and deck as one solid, notched in front of the
attic by asset_build.difference so the eave breaks round it), the attic and
its pediment, the dial, the tower's shaft, platform rails and dado, the
dome, ball and pole, the chimneys (asset_build.open_stack), the balcony's
slab and rails, the quoin blocks, the entrance and service steps, the
downpipes and the roof ladder; the caged wall ladder goes in after the weld
as the lean kit (scripts/roof_safety.py).

Every wall samples the atlas in true metres: the tiling wall band (brick,
plinth and the horizontal trim) at the wall's own U, each opening kind's
own item region at its place, and on the far tiers the wall's elevation.
Every number the mesh and the atlas share is imported from facade_atlas.py.
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
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import downpipes as DP  # noqa: E402
import model_facts  # noqa: E402
import roof_safety as RS  # noqa: E402
import shell_build as SB  # noqa: E402
from asset_build import difference, to_object, union  # noqa: E402
from shell_build import Frame  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT, tint=L.LIT_FACTOR,
                          camera_location=(33.8, -63.6, 22.0))
get_material, export_all = BUILD.material, BUILD.export_all
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants
Builder = functools.partial(SB.Builder, L.ATLAS)

PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)
EO = L.EAVE_OUT
SLOPE_K = math.sqrt(1.0 + L.TAN * L.TAN)


# ================================================================ tiers
# What each tier keeps. Nothing but detail goes; massing, roofline, crown,
# attic, chimneys, balcony and the U-plan stay on every tier.
#
#   LOD0  every opening recessed REVEAL into the wall, quoin blocks, the
#         modelled dial, balcony and platform rails over recessed dados,
#         the stone steps, the dome at 16 sides, the ball, bent downpipes,
#         the whole roof safety kit
#   LOD1  the street walls as LOD0; the U-court's seven walls on their
#         elevations; the dial painted; the balustrades plain blocks with
#         the balusters on their faces, the ball a box, the dome at 12
#         sides, straight four-sided pipes, every fourth rung and every
#         sixth hoop of the kit
#   LOD2  every wall one face on its elevation (16 texels a metre: the
#         band, the items, the quoins and the downpipes painted in), the
#         street front's openings still recessed, the entrance on its
#         step; the dome at 8 sides, straight pipes; no quoin blocks, dial
#         or service step (its door is flush); no kit, which stands in the
#         U-court
#   LOD3  as LOD2 with every opening flush and no step (the risers painted
#         under the doors), the dome at 4 sides, no ball, no pipes (painted
#         on the elevations), the balcony one block, the soffit and fascia
#         one face
FRONT_REVEALS = (True, True, True, False)
DOME_SIDES = (16, 12, 8, 4)
DOME_RINGS = ((0, 1, 2, 3, 4), (0, 2, 3, 4), (0, 2, 4), (0, 4))
PIPE_MODES = ((8, True), (4, False), (4, False), (0, False))
KIT_MODES = ((1, True), (4, False), (None, False), (None, False))
CAGE_MODES = (1, 6, None, None)


def wall_mode(name, level):
    """("items", recessed) or ("elev", recessed) for wall *name* at *level*."""
    if level == 0:
        return "items", True
    if level == 1:
        return ("elev", False) if name in L.COURT else ("items", True)
    return "elev", FRONT_REVEALS[level] and name in L.FRONT


def detail(level):
    """Quoin blocks, the modelled dial (the steps follow their doors'
    recesses: steps_kept())."""
    return level < 2


def rails(level):
    """The balustrades' rails over recessed dados, the ball, the dial."""
    return level < 1


# ============================================================== wall frames
def frame_of(name):
    w = L.WALL[name]
    return Frame(w["p0"], w["p1"])


# ------------------------------------------------------------ UV mappings
def uv_patch(name):
    return SB.uv_patch(L.PATCHES[name])


def uv_band(fr, u_off, dz=0.0):
    """The wall band in true metres, at the wall's own U; *dz* lowers the
    face onto band rows lower down (the attic's brick above the eave)."""
    return lambda co: ((fr.s_of(co) + u_off) * PPM, L.WALL_Y0 + (co.z - dz) * PPM)


def uv_item(fr, kind, v, left):
    x, y, _w, _h = L.ITEM_REGION[(kind, v)]
    z0 = L.ITEMS[kind]["z0"]
    return lambda co: (x + (fr.s_of(co) - left) * PPM, y + (co.z - z0) * PPM)


def uv_elev(fr, name):
    x, y, _w, _h = L.ELEV[name]
    return lambda co: (x + fr.s_of(co) * L.EPPM, y + co.z * L.EPPM)


def uv_rect(rect, s_of, z0, ppm=PPM):
    """A face onto a region, s_of(co) metres across it, z0 at its foot."""
    x, y, _w, _h = rect
    return lambda co: (x + s_of(co) * ppm, y + (co.z - z0) * ppm)


# ================================================================== walls
# A hole-free four-point region goes in as one quad (fill_region's quad).
fill_region = functools.partial(SB.fill_region, quad=True)


def opening(B, fr, a0, a1, z0, z1, back):
    """An opening a0..a1 x z0..z1 recessed REVEAL into its wall
    (shell_build.recess()): four reveals (none at its foot when it stands on
    the ground, where the floor cap closes it) and the back face, which
    samples the same texels it would flush, through *back*."""
    fns = [uv_patch("sill_top"), uv_patch("reveal"), uv_patch("reveal"), uv_patch("reveal")]
    SB.recess(B, fr, SB.rect_poly((a0, a1, z0, z1)), 0.0, -L.REVEAL, back, fns,
              skip_z=z0 if z0 < EPS else None)


def build_item(B, fr, kind, s, v, recess):
    """One item's faces; returns its outline on the wall, counter-clockwise
    from its bottom left. Flush, one face on its region; recessed, its front
    round its openings, and each opening recessed (opening())."""
    l, r, b, t = L.item_rect(kind, s)
    fn = uv_item(fr, kind, v, l)
    it = L.ITEMS[kind]
    rect = [(l, b), (r, b), (r, t), (l, t)]
    if not recess or not it["openings"]:
        B.face([fr.P(a, z) for a, z in rect], fn)
        return rect
    holes, notch = [], []
    for o0, o1, z0, z1 in it["openings"]:
        a0, a1 = l + o0, l + o1
        if z0 <= b + EPS:
            notch.append((a0, a1, z1))
        else:
            holes.append([(a0, z0), (a1, z0), (a1, z1), (a0, z1)])
        opening(B, fr, a0, a1, z0, z1, fn)
    outline = [(l, b)]
    for a0, a1, z1 in sorted(notch):
        outline += [(a0, b), (a0, z1), (a1, z1), (a1, b)]
    outline += [(r, b), (r, t), (l, t)]
    fill_region(B, fr, SB.dedupe(outline), holes, fn)
    return rect


def build_wall(B, spec, level):
    """One elevation from the ground to Z_TOP, holed for its items (or, on
    the elevation tiers, its recessed openings) and notched at its foot for
    those that stand on the ground."""
    fr = Frame(spec["p0"], spec["p1"])
    mode, recess = wall_mode(spec["name"], level)
    holes, notches = [], []
    if mode == "items":
        wallfn = uv_band(fr, spec["u"])
        for kind, s, v in spec["items"]:
            ring = build_item(B, fr, kind, s, v, recess and kind != "pilaster")
            (notches if ring[0][1] < EPS else holes).append(ring)
    else:
        wallfn = uv_elev(fr, spec["name"])
        if recess:
            for kind, s, v in spec["items"]:
                l = L.item_rect(kind, s)[0]
                for o0, o1, z0, z1 in L.ITEMS[kind]["openings"]:
                    opening(B, fr, l + o0, l + o1, z0, z1, wallfn)
                    ring = [(l + o0, z0), (l + o1, z0), (l + o1, z1), (l + o0, z1)]
                    (notches if z0 < EPS else holes).append(ring)
    # Under each quoin block (detail tiers) the wall is its own cell, so the
    # union cuts the wall along edges it already has; the block buries it.
    # Both faces of a corner are cut, whatever either maps, so the corner's
    # edge is split at the same height on both.
    q, qt, pr = L.QUOIN_DEPTH, L.QUOIN_TOP, L.QUOIN_PROUD
    lq = detail(level)
    q0, q1 = lq and spec["convex0"], lq and spec["convex1"]
    if q0:
        x, y, _w, _h = L.QUOIN["b"]
        B.face([fr.P(0.0, 0.0), fr.P(q, 0.0), fr.P(q, qt), fr.P(0.0, qt)],
               lambda co: (x + (fr.s_of(co) + pr) * PPM, y + co.z * PPM))
    if q1:
        x, y, _w, _h = L.QUOIN["a"]
        B.face([fr.P(fr.L - q, 0.0), fr.P(fr.L, 0.0), fr.P(fr.L, qt), fr.P(fr.L - q, qt)],
               lambda co: (x + (fr.L + pr - fr.s_of(co)) * PPM, y + co.z * PPM))
    outline = [(q, 0.0)] if q0 else [(0.0, 0.0)]
    for ring in sorted(notches, key=lambda r: r[0][0]):
        outline += [ring[0], ring[3], ring[2], ring[1]]
    if q1:
        outline += [(fr.L - q, 0.0), (fr.L - q, qt), (fr.L, qt)]
    else:
        outline += [(fr.L, 0.0)]
    outline += [(fr.L, L.Z_TOP), (0.0, L.Z_TOP)]
    if q0:
        outline += [(0.0, qt), (q, qt)]
    fill_region(B, fr, SB.dedupe(outline), holes, wallfn)


def main_body(level):
    """The wall ring, capped by a floor on the ground and a lid at the wall
    top (shell_build.close_solid())."""
    B = Builder()
    for spec in L.WALLS:
        build_wall(B, spec, level)
    SB.close_solid(B, uv_patch("blank"))
    return B


# ================================================================== boxes
def box(x0, x1, y0, y1, z0, z1, fns):
    """A closed axis-aligned box (shell_build.box()). *fns* maps "front"
    (-Y), "right" (+X), "back" (+Y), "left" (-X), "top" and "bottom" to UV
    functions, each face called with s running left to right as seen from
    outside it."""
    s_ofs = (("front", lambda co: co.x - x0), ("right", lambda co: co.y - y0),
             ("back", lambda co: x1 - co.x), ("left", lambda co: y1 - co.y))
    sides = []
    for name, s_of in s_ofs:
        fn = fns[name]
        sides.append(fn(s_of) if getattr(fn, "wants_s", False) else fn)
    return SB.box(Builder(), x0, x1, y0, y1, z0, z1, sides, fns["top"], fns["bottom"])


def along(rect, z0, ppm=PPM, s0=0.0):
    """A side's mapping onto *rect*: s across it from s0, z up from z0. Passed
    to box(), which hands it the side's own s."""
    def make(s_of):
        return uv_rect(rect, lambda co: s_of(co) - s0, z0, ppm)
    make.wants_s = True
    return make


def plain(name, **extra):
    fns = {k: uv_patch(name) for k in ("front", "right", "back", "left", "top", "bottom")}
    fns.update({k: uv_patch(v) for k, v in extra.items()})
    return fns


# ================================================================== roof
def _normal(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy)
    return dy / d, -dx / d


def offset_ring(pts, k):
    """The rectilinear counter-clockwise ring *pts* offset *k* outward (inward
    for negative k), each corner moved along the sum of its two edges'
    outward normals, which is exact for right-angled corners."""
    out = []
    n = len(pts)
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        n1, n2 = _normal(a, b), _normal(b, c)
        out.append((b[0] + k * (n1[0] + n2[0]), b[1] + k * (n1[1] + n2[1])))
    return out


W_RING = [tuple(w["p0"]) for w in L.WALLS]
F_RING = offset_ring(W_RING, EO)
D_RING = offset_ring(F_RING, -L.ROOF_RUN)


def _roof_u():
    u, out = 0.0, []
    for i in range(len(F_RING)):
        out.append(u % (L.ATLAS / PPM))
        a, b = F_RING[i], F_RING[(i + 1) % len(F_RING)]
        u += math.hypot(b[0] - a[0], b[1] - a[1]) + 0.25
    return out


ROOF_U = _roof_u()


def uv_deck():
    x, y, _w, _h = L.DECK
    ox, oy = L.DECK_O
    return lambda co: (x + (co.x - ox) * L.DPPM, y + (co.y - oy) * L.DPPM)


def roof_solid(level=0):
    """The roof as one closed solid over the wall outline: a level soffit
    EAVE_OUT wide all round, the fascia, the slopes rising ROOF_RISE over
    ROOF_RUN to the one flat deck, and the underside inside the wall line,
    which the union buries in the body (its walls run up to Z_TOP). On LOD3
    the soffit and the fascia are one face, from the wall's head to the
    fascia's top: the eave's outline stays where it is."""
    B = Builder()
    ze, zf, zd = L.Z_EAVE, L.Z_FT, L.Z_DECK
    n = len(W_RING)
    B.face([(x, y, ze) for x, y in reversed(W_RING)], uv_patch("blank"))
    for i in range(n):
        j = (i + 1) % n
        w0, w1, f0, f1, d0, d1 = W_RING[i], W_RING[j], F_RING[i], F_RING[j], D_RING[i], D_RING[j]
        u = ROOF_U[i]
        fw, ff = Frame(w0, w1), Frame(f0, f1)
        soffit = (lambda co, fw=fw, u=u: ((fw.s_of(co) + u) * PPM,
                                          L.SOF_Y0 + min(EO, max(0.0, fw.out_of(co))) * PPM))
        if level == 3:
            B.face([(w1[0], w1[1], ze), (w0[0], w0[1], ze), (f0[0], f0[1], zf),
                    (f1[0], f1[1], zf)], soffit)
        else:
            B.face([(w1[0], w1[1], ze), (w0[0], w0[1], ze), (f0[0], f0[1], ze),
                    (f1[0], f1[1], ze)], soffit)
            B.face([(f0[0], f0[1], ze), (f1[0], f1[1], ze), (f1[0], f1[1], zf),
                    (f0[0], f0[1], zf)],
                   lambda co, ff=ff, u=u: ((ff.s_of(co) + u) * PPM,
                                           L.FASC_Y0 + (co.z - ze) * PPM))
        B.face([(f0[0], f0[1], zf), (f1[0], f1[1], zf), (d1[0], d1[1], zd), (d0[0], d0[1], zd)],
               lambda co, ff=ff, u=u: ((ff.s_of(co) + u) * PPM,
                                       L.ROOF_Y0 + max(0.0, -ff.out_of(co)) * SLOPE_K * L.RPM))
    B.face([(x, y, zd) for x, y in D_RING], uv_deck())
    return B


def roof_object(level):
    """The roof, notched in front of the clock attic: the eave breaks round
    the attic, whose front rises straight from the wall's cornice, and the
    cut's faces are the eave's white returns either side of it."""
    x0, x1, y0, _y1 = L.ATTIC
    cut = box(x0, x1, y0 - 1.25, y0 + 0.125, L.Z_EAVE - 0.5, 13.5, plain("cutter"))
    return difference(to_object(roof_solid(level), "tmp_roof"), [to_object(cut, "tmp_notch")],
                      snap=asset_build.SNAP)


# =========================================================== attic, crown
def attic():
    """The clock attic: its front the attic region (brick, framed panel,
    dial), its sides and back brick from the wall band's upper storey."""
    x0, x1, y0, y1 = L.ATTIC
    band = lambda s_of: (lambda co: ((s_of(co) + 3.0) * PPM,  # noqa: E731
                                     L.WALL_Y0 + (co.z - 5.0) * PPM))
    band.wants_s = True
    fns = {"front": uv_rect(L.ATTIC_F, lambda co: co.x - x0, L.Z_TOP),
           "right": band, "back": band, "left": band,
           "top": uv_patch("trim"), "bottom": uv_patch("blank")}
    return box(x0, x1, y0, y1, L.Z_TOP, L.Z_ATTIC, fns)


def pediment():
    """The pediment over the attic, PED_OVER proud of its front and sides
    (its back flush with the attic's, where an oversail would only shade
    the roof behind): its front the tympanum and raking cornice, its back
    brick, its slopes the roof sheet, its underside the white cornice
    soffit."""
    B = Builder()
    o = L.PED_OVER
    x0, x1, y0, y1 = L.ATTIC
    x0, x1, y0 = x0 - o, x1 + o, y0 - o
    zb, za = L.Z_ATTIC, L.Z_APEX
    half = (x1 - x0) / 2.0
    k = math.hypot(half, za - zb) / half
    front = uv_rect(L.PEDIMENT, lambda co: co.x - x0, zb)
    B.face([(x0, y0, zb), (x1, y0, zb), (0.0, y0, za)], front)
    B.face([(x1, y1, zb), (x0, y1, zb), (0.0, y1, za)],
           lambda co: ((x1 - co.x + 5.0) * PPM, L.WALL_Y0 + (co.z - 7.0) * PPM))
    slope = lambda co: ((co.y - y0 + 1.0) * PPM,                # noqa: E731
                        L.ROOF_Y0 + (half - abs(co.x)) * k * L.RPM)
    B.face([(x1, y0, zb), (x1, y1, zb), (0.0, y1, za), (0.0, y0, za)], slope)
    B.face([(x0, y1, zb), (x0, y0, zb), (0.0, y0, za), (0.0, y1, za)], slope)
    B.face([(x0, y1, zb), (x1, y1, zb), (x1, y0, zb), (x0, y0, zb)], uv_patch("trim_shade"))
    return B


def dial(sides=16):
    """The clock's dial, a disc DIAL_R across standing 0.10 m off the attic
    and let 0.02 m into it, its face on the painted dial."""
    B = Builder()
    (cx, cz), r = L.DIAL_C, L.DIAL_R
    y_in, y_out = L.ATTIC[2] + 0.02, L.ATTIC[2] - 0.10
    ring = [(cx + r * math.cos(2 * math.pi * (k + 0.5) / sides),
             cz + r * math.sin(2 * math.pi * (k + 0.5) / sides)) for k in range(sides)]
    face = uv_rect(L.ATTIC_F, lambda co: co.x - L.ATTIC[0], L.Z_TOP)
    rim = uv_patch("trim_shade")
    for k in range(sides):
        (ax, az), (bx, bz) = ring[k], ring[(k + 1) % sides]
        B.face([(ax, y_out, az), (bx, y_out, bz), (bx, y_in, bz), (ax, y_in, az)], rim)
    B.face([(x, y_out, z) for x, z in reversed(ring)], face)
    B.face([(x, y_in, z) for x, z in ring], uv_patch("blank"))
    return B


def tower_parts(level):
    """The shaft from inside the roof to TOWER_TOP, its platform, the dome,
    the ball and the flagpole, as (solid, name)."""
    w, yc = L.TOWER_W, L.TOWER_YC
    out = []
    fns = {k: along(L.TOWER, L.TOWER_FOOT) for k in ("front", "right", "back", "left")}
    fns.update(top=uv_patch("lid"), bottom=uv_patch("blank"))
    out.append((box(-w, w, yc - w, yc + w, L.TOWER_FOOT, L.TOWER_TOP, fns), "tmp_shaft"))
    p0, p1 = L.TOWER_PLAT
    if rails(level):
        z_d0, z_d1 = p0 + 0.15, p1 - 0.10
        r, rd = w + 0.35, w + 0.30
        out.append((box(-r, r, yc - r, yc + r, p0, z_d0, plain("rail", top="sill_top",
                                                               bottom="trim_shade")), "tmp_plat0"))
        dado = {k: along(L.PLAT_BALUS, z_d0, s0=0.0) for k in ("front", "right", "back", "left")}
        dado.update(top=uv_patch("rail"), bottom=uv_patch("blank"))
        out.append((box(-rd, rd, yc - rd, yc + rd, z_d0, z_d1, dado), "tmp_plat1"))
        out.append((box(-r, r, yc - r, yc + r, z_d1, p1, plain("rail", bottom="trim_shade")),
                    "tmp_plat2"))
    else:
        r = w + 0.35
        dado = {k: along(L.PLAT_BALUS, p0 + 0.15) for k in ("front", "right", "back", "left")}
        dado.update(top=uv_patch("rail"), bottom=uv_patch("trim_shade"))
        out.append((box(-r, r, yc - r, yc + r, p0, p1, dado), "tmp_plat"))
    out.append((dome(level), "tmp_dome"))
    top = L.DOME_Z[-1]
    if rails(level):
        out.append((ball(), "tmp_ball"))
    elif level < 3:
        b0, b1 = L.TOWER_BALL
        out.append((box(-0.2, 0.2, yc - 0.2, yc + 0.2, b0, b1, plain("rail")), "tmp_ball"))
    q = 0.09
    out.append((box(-q, q, yc - q, yc + q, top - 0.05, L.TOWER_POLE, plain("rail")), "tmp_pole"))
    return out


def dome(level):
    """The round dome on the drum: DOME_SIDES[level] facets (flats toward
    the four fronts), on the rings DOME_RINGS[level] of the profile DOME_Z /
    DOME_R, its foot on the shaft's top and a flat cap at its crown. Every
    facet maps the dome region, U across it, V up its meridian."""
    B = Builder()
    n = DOME_SIDES[level]
    yc = L.TOWER_YC
    idx = DOME_RINGS[level]
    zs = [L.DOME_Z[i] for i in idx]
    rs = [L.DOME_R[i] / math.cos(math.pi / n) for i in idx]
    ang = [2.0 * math.pi * (k + 0.5) / n for k in range(n)]
    rings = [[(r * math.cos(a), yc + r * math.sin(a), z) for a in ang] for r, z in zip(rs, zs)]
    mer = [0.0]
    for j in range(1, len(zs)):
        mer.append(mer[-1] + math.hypot(L.DOME_R[idx[j]] - L.DOME_R[idx[j - 1]], zs[j] - zs[j - 1]))
    x, y, w, _h = L.DOME
    for j in range(len(zs) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            cos = [rings[j][k], rings[j][k1], rings[j + 1][k1], rings[j + 1][k]]
            uvs = [(x, y + mer[j] * PPM), (x + w, y + mer[j] * PPM),
                   (x + w, y + mer[j + 1] * PPM), (x, y + mer[j + 1] * PPM)]
            B.face(cos, uvs)
    B.face(list(rings[-1]), uv_patch("lid"))
    B.face(list(reversed(rings[0])), uv_patch("blank"))
    return B


def ball():
    """The gilt-less ball on the crown, an octagonal sphere 0.5 m across."""
    B = Builder()
    yc = L.TOWER_YC
    b0, b1 = L.TOWER_BALL
    prof = [(0.12, b0), (0.25, b0 + 0.18), (0.23, b0 + 0.35), (0.10, b1)]
    n = 8
    ang = [2.0 * math.pi * (k + 0.5) / n for k in range(n)]
    rings = [[(r * math.cos(a), yc + r * math.sin(a), z) for a in ang] for r, z in prof]
    fn = uv_patch("rail")
    for j in range(len(prof) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            B.face([rings[j][k], rings[j][k1], rings[j + 1][k1], rings[j + 1][k]], fn)
    B.face(list(rings[-1]), fn)
    B.face(list(reversed(rings[0])), fn)
    return B


def chimneys():
    """The six stacks, each open at the top round one flue sunk 1.0 m to a
    soot floor (asset_build.open_stack), from inside the roof. A stack's four
    sides share one mapping, mirrored about each side's middle, so the
    corners agree."""
    out = []
    x, y, w, _h = L.CHIMNEY
    for i, (x0, x1, y0, y1) in enumerate(L.CHIMNEYS):
        xc, yc, h = (x0 + x1) / 2.0, (y0 + y1) / 2.0, (x1 - x0) / 2.0
        side = (lambda co, xc=xc, yc=yc, h=h:
                (x + w / 2.0 + (abs(co.x - xc) + abs(co.y - yc) - h) * PPM,
                 y + (co.z - L.CHIM_FOOT) * PPM))
        B = Builder()
        asset_build.open_stack(B, x0, x1, y0, y1, L.CHIM_FOOT, L.CHIM_TOP, 0.25, 1.0,
                               side, uv_patch("rim"), uv_patch("soot"), uv_patch("blank"))
        out.append((B, "tmp_chimney%d" % i))
    return out


# ======================================================== balcony, steps
def balcony(level):
    """The balcony over the entrance: a slab let into the wall under the
    upper floor, and three parapets, each a bottom rail, a recessed dado
    with the balusters painted on and a top rail (to LOD1), or one block
    with the balusters on its faces."""
    out = []
    X, yf = L.BALC_X, L.BALC_Y
    yw = L.ATTIC[2] + 0.10                 # into the wall, past its face
    z0, z1 = L.BALC_SLAB
    rb, rd, rt = L.BALC_RAIL
    t = L.BALC_T
    if level == 3:
        # one block: the slab and the parapet's outline, the balusters on
        # its faces, as far out as the near tiers' top rail
        o = 0.02
        fns = {k: along(L.BALUS, rb) for k in ("front", "right", "back", "left")}
        fns.update(top=uv_patch("rail"), bottom=uv_patch("trim_shade"))
        return [(box(-X - o, X + o, yf - o, yw, z0, rt, fns), "tmp_balcony")]
    out.append((box(-X, X, yf, yw, z0, z1, plain("trim", top="sill_top", bottom="trim_shade")),
                "tmp_slab"))
    spans = [("front", -X, X, yf, yf + t), ("left", -X, -X + t, yf, yw), ("right", X - t, X, yf, yw)]
    for name, a0, a1, b0, b1 in spans:
        along_x = name == "front"

        def dado_map(s_of, along_x=along_x):
            s = (lambda co: co.x + X) if along_x else (lambda co: co.y - yf)
            return uv_rect(L.BALUS, s, rb)
        dado_map.wants_s = True
        fns = {k: dado_map for k in ("front", "right", "back", "left")}
        if rails(level):
            # the side parapets run on into the wall; the front one's ends
            # are inside the side ones
            g, o = 0.03, 0.02
            back = b1 if not along_x else b1 - g
            fns.update(top=uv_patch("rail"), bottom=uv_patch("blank"))
            out.append((box(a0, a1, b0, b1, z1, rb, plain("rail", bottom="trim_shade")),
                        "tmp_rail_%s0" % name))
            out.append((box(a0 + g, a1 - g, b0 + g, back, rb, rd, fns), "tmp_rail_%s1" % name))
            out.append((box(a0 - o, a1 + o, b0 - o, b1 + o if along_x else b1, rd, rt,
                            plain("rail", bottom="trim_shade")), "tmp_rail_%s2" % name))
        else:
            # as far out as the near tiers' top rail, so the bounds hold
            o = 0.02
            fns.update(top=uv_patch("rail"), bottom=uv_patch("trim_shade"))
            out.append((box(a0 - o, a1 + o, b0 - o, b1 + o if along_x else b1, z1, rt, fns),
                        "tmp_parapet_%s" % name))
    return out


def steps(level):
    """A stone step under each door whose recess *level* keeps, one riser to
    the ground floor, filling the door's recess and running into the wall
    behind it: the door's floor, so no recess stands open to the ground. The
    entrance's goes with the street front's reveals (to LOD2), the service
    door's with the near tiers' items (to LOD1); a flush door has none."""
    out = []
    if steps_kept("entrance", level):
        fr = frame_of("entrance")
        y = fr.p0.y
        out.append((box(-1.75, 1.75, y - 0.45, y + L.REVEAL + 0.12, 0.0, L.Z_FLOOR,
                        plain("step")), "tmp_step_entrance"))
    if steps_kept("wing_end_r", level):
        w = L.WALL["wing_end_r"]
        xs = w["p0"][0] - dict((k, s) for k, s, _v in w["items"])["service"]
        yr = w["p0"][1]
        out.append((box(xs - 1.0, xs + 1.0, yr - L.REVEAL - 0.12, yr + 0.40, 0.0, L.Z_FLOOR,
                        plain("step")), "tmp_step_service"))
    return out


def steps_kept(wall, level):
    """Whether *level* recesses the openings of *wall*, and so keeps the
    step its door stands on (wall_mode(), the predicate that cuts them)."""
    return wall_mode(wall, level)[1]


# ================================================================== quoins
def corners():
    """(wall ending, wall starting) at every convex corner."""
    return [(L.WALLS[i - 1], w) for i, w in enumerate(L.WALLS) if w["convex0"]]


def quoin_block(A, B_):
    """The block at the convex corner where wall A ends and B_ starts: it
    stands QUOIN_PROUD out of both faces and wraps QUOIN_DEPTH back along
    each, from the ground to QUOIN_TOP. Its face along A samples quoin strip
    "a" and its face along B_ strip "b", U measured from the block's outer
    corner, so the long and short stones alternate round the corner."""
    fr = Frame(A["p0"], A["p1"])
    d, pr, top = L.QUOIN_DEPTH, L.QUOIN_PROUD, L.QUOIN_TOP
    la = fr.L
    s0, s1, o0, o1 = la - d, la + pr, -d, pr
    qa, qb = L.QUOIN["a"], L.QUOIN["b"]
    fa = lambda co: (qa[0] + (s1 - fr.s_of(co)) * PPM, qa[1] + co.z * PPM)   # noqa: E731
    fb = lambda co: (qb[0] + (o1 - fr.out_of(co)) * PPM, qb[1] + co.z * PPM)  # noqa: E731
    side = uv_patch("trim_shade")
    ring = [fr.P(s, 0.0, o)[:2] for s, o in ((s0, o1), (s1, o1), (s1, o0), (s0, o0))]
    return SB.prism(Builder(), ring, 0.0, top, [fa, fb, side, side], uv_patch("sill_top"),
                    uv_patch("blank"))


# ========================================================= pipes and kit
PIPES = [DP.eave_pipe(L.WALL[n]["p0"], L.WALL[n]["p1"], s, L.Z_EAVE, 0.0, EO)
         for n, s in L.PIPES]
PAINT = RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)
_KW = L.WALL[L.LADDER[0]]
KIT_EAVE = RS.Eave(_KW["p0"], _KW["p1"], L.Z_EAVE, EO, L.Z_FT, L.TAN)
WALL_LADDER = RS.WallLadder(KIT_EAVE, L.LADDER[1], lean=True)
CAGE = RS.Cage(WALL_LADDER, modes=CAGE_MODES)
ROOF_LADDER = RS.RoofLadder(KIT_EAVE, L.LADDER[1], L.Z_DECK)


# ================================================================ assembly
def build_lod(level):
    base = to_object(main_body(level), "tmp_body")
    parts = [roof_object(level), to_object(attic(), "tmp_attic"),
             to_object(pediment(), "tmp_pediment")]
    parts += [to_object(B, n) for B, n in tower_parts(level)]
    parts += [to_object(B, n) for B, n in chimneys()]
    parts += [to_object(B, n) for B, n in balcony(level)]
    if rails(level):
        parts.append(to_object(dial(), "tmp_dial"))
    if detail(level):
        parts += [to_object(quoin_block(A, B_), "tmp_quoin%d" % i)
                  for i, (A, B_) in enumerate(corners())]
    parts += [to_object(B, n) for B, n in steps(level)]
    parts += [to_object(B, n) for B, n in DP.solids(PIPES, *PIPE_MODES[level], L.PIPE_STRIP,
                                                     L.ATLAS)]
    kit = KIT_MODES[level][0] is not None
    if kit:
        parts += [to_object(B, n) for B, n in RS.solids([ROOF_LADDER], level, PAINT,
                                                         modes=KIT_MODES)]
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
                                 edges=bm.edges[:], delimit={'UV'})
    bm.to_mesh(obj.data)
    bm.free()
    if kit:
        RS.append(obj, RS.solids([WALL_LADDER, CAGE], level, PAINT, modes=KIT_MODES),
                  check=True)
    # faces in an order of their own corners, so a rebuild writes the same file
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    order = sorted(bm.faces, key=lambda f: [tuple(round(c, 4) for c in lp.vert.co)
                                            for lp in f.loops])
    rank = {f: i for i, f in enumerate(order)}
    bm.faces.sort(key=lambda f: rank[f])
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# ================================================================== checks
def union_outline(rects):
    """Ordered plan polygon of the union of axis-aligned *rects*, CCW from
    above, collinear points dropped: the rects laid out as cells on the grid
    of their own edges, the cells inside any rect dissolved into one n-gon."""
    xs = sorted({v for r in rects for v in (r[0], r[1])})
    ys = sorted({v for r in rects for v in (r[2], r[3])})
    bm = bmesh.new()
    cache = {}

    def dv(co):
        key = (round(co[0], 6), round(co[1], 6))
        if key not in cache:
            cache[key] = bm.verts.new((co[0], co[1], 0.0))
        return cache[key]
    cells = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2.0, (ys[j] + ys[j + 1]) / 2.0
            if any(r[0] < cx < r[1] and r[2] < cy < r[3] for r in rects):
                cells.append(bm.faces.new([dv((xs[i], ys[j])), dv((xs[i + 1], ys[j])),
                                           dv((xs[i + 1], ys[j + 1])), dv((xs[i], ys[j + 1]))]))
    region = bmesh.ops.dissolve_faces(bm, faces=cells, use_verts=False)["region"]
    if len(region) != 1:
        bm.free()
        raise ValueError("the massing does not dissolve to one outline")
    poly = [(lp.vert.co.x, lp.vert.co.y) for lp in region[0].loops]
    bm.free()
    out = []
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by), (cx, cy) = poly[i - 1], poly[i], poly[(i + 1) % n]
        if abs((bx - ax) * (cy - by) - (by - ay) * (cx - bx)) > 1e-9:
            out.append((bx, by))
    m = len(out)
    area = sum(out[i][0] * out[(i + 1) % m][1] - out[(i + 1) % m][0] * out[i][1]
               for i in range(m))
    if area < 0.0:
        out.reverse()
    return out


def _on(v, step):
    return abs(v / step - round(v / step)) < 1e-6


def _inside(poly, x, y):
    c = False
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    # the walls are the massing's outline, every corner on a half stretcher
    ring = union_outline(L.RECTS)
    k0 = min(range(len(ring)), key=lambda i: (ring[i][0] - W_RING[0][0]) ** 2
             + (ring[i][1] - W_RING[0][1]) ** 2)
    ring = ring[k0:] + ring[:k0]
    if len(ring) != len(W_RING) or any(abs(a[0] - b[0]) > 1e-6 or abs(a[1] - b[1]) > 1e-6
                                       for a, b in zip(ring, W_RING)):
        bad.append("the WALLS ring is not the outline of RECTS")
    for a, b in zip(L.WALLS, L.WALLS[1:] + L.WALLS[:1]):
        if tuple(a["p1"]) != tuple(b["p0"]):
            bad.append("the wall ring breaks between %s and %s" % (a["name"], b["name"]))
    for x, y in W_RING:
        if not (_on(x, L.HALF) and _on(y, L.HALF)):
            bad.append("the corner (%.4f, %.4f) is off the half stretcher" % (x, y))
    for w in L.WALLS:
        if w["L"] < 1.0:
            bad.append("%s is only %.2f m: two masses probably missed alignment"
                       % (w["name"], w["L"]))
    # heights on course lines
    for what in ("Z_FLOOR", "Z_PLINTH", "Z_PLINTH_CAP", "Z_GF_SILL", "Z_DOOR_TRANSOM",
                 "Z_DOOR_HEAD", "Z_GF_HEAD", "Z_STRING", "Z_UPPER", "Z_BAL_SILL",
                 "Z_UF_SILL", "Z_TALL_SILL", "Z_BAL_TRANSOM", "Z_UF_HEAD", "Z_TALL_HEAD",
                 "Z_FRIEZE", "Z_CORNICE", "Z_CORNICE_TOP", "Z_EAVE", "Z_TOP", "Z_ATTIC",
                 "Z_APEX", "CHIM_TOP", "QUOIN_TOP", "QUOIN_PROUD"):
        if not _on(getattr(L, what), L.COURSE):
            bad.append("%s at %.5f m is off the coursing" % (what, getattr(L, what)))
    for v in L.BALC_RAIL + L.BALC_SLAB:
        if not _on(v, L.COURSE):
            bad.append("a balcony height %.5f is off the coursing" % v)
    # items: widths and openings on half stretchers, heights on courses
    for kind, it in L.ITEMS.items():
        if not _on(it["w"], L.HALF):
            bad.append("the %s is not a whole number of half stretchers wide" % kind)
        zs = [it["z0"], it["z1"]] + [z for o in it["openings"] for z in o[2:]]
        if not all(_on(z, L.COURSE) for z in zs):
            bad.append("the %s's heights are off the coursing" % kind)
        if not all(_on(s, L.HALF) for o in it["openings"] for s in o[:2]):
            bad.append("the %s's openings are off the half stretcher" % kind)
    # each wall's items: inside the wall, clear of its quoins and each other,
    # every side on a half stretcher of the wall's bond
    q = L.QUOIN_DEPTH + 0.25
    for w in L.WALLS:
        rs = []
        if w["items"] and w["L"] < 2.5:
            bad.append("%s is %.2f m, too short for an opening" % (w["name"], w["L"]))
        for kind, s, v in w["items"]:
            l, r, b, t = L.item_rect(kind, s)
            lo = q if w["convex0"] else 0.25
            hi = w["L"] - (q if w["convex1"] else 0.25)
            if l < lo - EPS or r > hi + EPS:
                bad.append("%s: the %s at %.4f is within a quoin or 0.25 m of a corner"
                           % (w["name"], kind, s))
            if not (_on(w["u"] + l, L.HALF) and _on(w["u"] + r, L.HALF)):
                bad.append("%s: the %s at %.4f cuts the bond off a half stretcher"
                           % (w["name"], kind, s))
            if v >= L.NVAR[kind]:
                bad.append("%s: the %s has no variant %d" % (w["name"], kind, v))
            rs.append((kind, l, r, b, t))
        for i, a in enumerate(rs):
            for b_ in rs[i + 1:]:
                if a[1] < b_[2] + 0.25 - EPS and b_[1] < a[2] + 0.25 - EPS \
                        and a[3] < b_[4] - EPS and b_[3] < a[4] - EPS:
                    bad.append("%s: the %s and the %s are under 0.25 m apart"
                               % (w["name"], a[0], b_[0]))
        # neighbouring windows of a kind show different rooms
        for kind in L.WINDOW_KINDS:
            row = sorted((s, v) for k, s, v in w["items"] if k == kind)
            if any(a[1] == b_[1] for a, b_ in zip(row, row[1:])):
                bad.append("%s: two neighbouring %s windows share a room" % (w["name"], kind))
    # the bond turns at every concave corner
    for a, b in zip(L.WALLS, L.WALLS[1:] + L.WALLS[:1]):
        if b["convex0"]:
            continue
        end = a["u"] + a["L"]
        if not (_on(b["u"], L.HALF) and _on(end - b["u"] - L.HALF, L.BRICK_L)):
            bad.append("the %s/%s corner does not turn the bond" % (a["name"], b["name"]))
    # human scale
    for name, (wd, ht) in L.DOOR_LEAF.items():
        if not 2.0 <= ht <= 2.4:
            bad.append("the %s leaf is %.3f m, outside 2.0-2.4" % (name, ht))
    if L.Z_DOOR_HEAD - L.Z_DOOR_TRANSOM < 0.05 or L.Z_TALL_HEAD - L.Z_BAL_TRANSOM < 0.5:
        bad.append("a door has no transom between its leaf and its head")
    for what, sill, floor in (("ground", L.Z_GF_SILL, L.Z_FLOOR),
                              ("upper", L.Z_UF_SILL, L.Z_UPPER)):
        if not 0.6 <= sill - floor <= 1.4:
            bad.append("the %s floor's sills are %.2f m over it" % (what, sill - floor))
    if L.Z_BAL_SILL - L.Z_UPPER > 0.10 + EPS or L.Z_FLOOR > 0.25:
        bad.append("a door's threshold is not on its floor")
    if not 0.3 <= EO <= 0.6:
        bad.append("the eave projects %.3f m, outside 0.3-0.6" % EO)
    if L.TAN <= 1.0 / 8.0:
        bad.append("the roof is not steeper than 1:8: the kit's rule would not apply")
    if L.BALC_RAIL[2] > L.Z_TALL_SILL - L.COURSE + EPS:
        bad.append("the balcony's top rail reaches the tall windows' sills")
    # the roof: every deck edge parallel to its eave and positive
    n = len(W_RING)
    for i in range(n):
        j = (i + 1) % n
        wa, wb = W_RING[i], W_RING[j]
        da, db = D_RING[i], D_RING[j]
        if (db[0] - da[0]) * (wb[0] - wa[0]) + (db[1] - da[1]) * (wb[1] - wa[1]) <= 1e-6:
            bad.append("the deck collapses over %s" % L.WALLS[i]["name"])
    # the stacks and the tower on the deck, their flues clear of it
    for x0, x1, y0, y1 in L.CHIMNEYS + [(-L.TOWER_W, L.TOWER_W, L.TOWER_YC - L.TOWER_W,
                                          L.TOWER_YC + L.TOWER_W)]:
        if not all(_inside(D_RING, x, y) for x in (x0 - 0.2, x1 + 0.2) for y in (y0 - 0.2,
                                                                                  y1 + 0.2)):
            bad.append("the stack or tower at (%.2f, %.2f) is not on the deck" % (x0, y0))
    if L.CHIM_TOP - 1.0 < L.Z_DECK + 0.1:
        bad.append("a flue sinks to the deck")
    if L.Z_ATTIC <= max(L.Z_FT + (L.ATTIC[3] - L.ATTIC[2] + EO) * L.TAN, L.Z_TOP):
        bad.append("the attic does not stand clear of the roof slope behind it")
    # the dial inside the attic's framed panel
    (_cx, cz), r = L.DIAL_C, L.DIAL_R
    if cz - r < 11.875 + 0.125 or cz + r > 14.3125 - 0.125:
        bad.append("the dial does not fit its panel")
    # downpipes clear of corners, quoins, items and the ladder
    for (name, s), pipe in zip(L.PIPES, PIPES):
        w = L.WALL[name]
        # a pilaster is painted trim, not an opening: a pipe may stand
        # beside one, its face a few centimetres off it
        avoid = [(k, L.item_rect(k, si)[0], L.item_rect(k, si)[1])
                 + ((0.15,) if k == "pilaster" else ()) for k, si, _v in w["items"]]
        if w["convex0"]:
            avoid.append(("quoin", 0.0, L.QUOIN_DEPTH, 0.15))
        if w["convex1"]:
            avoid.append(("quoin", w["L"] - L.QUOIN_DEPTH, w["L"], 0.15))
        if name == L.LADDER[0]:
            avoid.append(("ladder",) + CAGE.span())
        bad += DP.problems(pipe, "the %s downpipe at %.2f" % (name, s), avoid)
    # the roof safety kit, in the U-court on the left wing's inner face
    w = L.WALL[L.LADDER[0]]
    avoid = [(k, L.item_rect(k, si)[0], L.item_rect(k, si)[1]) for k, si, _v in w["items"]
             if k != "pilaster"]
    avoid += [("downpipe", s - DP.A, s + DP.A) for n_, s in L.PIPES if n_ == L.LADDER[0]]
    if w["convex1"]:
        avoid.append(("quoin", w["L"] - L.QUOIN_DEPTH - L.QUOIN_PROUD, w["L"]))
    bad += RS.problems(WALL_LADDER, "the wall ladder", avoid)
    bad += RS.problems(CAGE, "the ladder's cage", avoid)
    if L.LADDER[0] not in L.COURT:
        bad.append("the wall ladder is not at the back of the building")
    if abs(ROOF_LADDER.top_out() - (EO - L.ROOF_RUN)) > 0.05:
        bad.append("the roof ladder does not reach the deck's edge")
    return bad


# ================================================================== build
def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the wall ring at ground level,
    without the quoin blocks that stand QUOIN_PROUD off it. Both storeys
    fill it: the ground floor on the doors' thresholds, one step over the
    ground, the upper floor on the string course's top, where the balcony
    opens. The tower and the attic are not floors. Three doors: the arched
    entrance in the centre bay (main), the balcony door over it, and the
    service door in the right rear wing's end; each height is its leaf's,
    to its transom."""
    ring = W_RING
    area = abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(ring, ring[1:] + ring[:1]))) / 2.0
    ent = L.WALL["entrance"]
    s_door = dict((k, s) for k, s, _v in ent["items"])["door"]
    rear = L.WALL["wing_end_r"]
    s_rear = dict((k, s) for k, s, _v in rear["items"])["service"]
    lw, lh = L.DOOR_LEAF["door"]
    bw, bh = L.DOOR_LEAF["balcony"]
    sw, sh = L.DOOR_LEAF["service"]
    doors = [
        model_facts.wall_door("front", "entrance", ent["p0"], ent["p1"], s_door, L.Z_FLOOR,
                              lw, lh, main=True),
        model_facts.wall_door("balcony", "balcony", ent["p0"], ent["p1"], s_door, L.Z_BAL_SILL,
                              bw, bh),
        model_facts.wall_door("rear", "service", rear["p0"], rear["p1"], s_rear, L.Z_FLOOR,
                              sw, sh),
    ]
    return {"hero": True, "dwellings": 0, "footprint": ring,
            "storeys": [(L.Z_FLOOR, area), (L.Z_UPPER, area)], "doors": doors}


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000), extra=True):
    """The six working views (shell_build.render_views()), plus a rear
    aerial and, with *extra*, an eye-level view of the entrance with a 1.8 m
    figure, the U-court, the tower's crown, the attic and pediment, a
    pavilion's corner, the side, the service door, the ladder and the deck.
    Working views only."""
    views = (SB.AERIAL, SB.AERIAL_REAR)
    if extra:
        views += (SB.look("entrance", (4.0, -24.0, 1.7), (0.0, -10.25, 4.5)),
                  SB.look("court", (0.0, 42.0, 14.0), (0.0, 8.0, 5.0)),
                  SB.look("crown", (12.0, -20.0, 24.0), (0.0, -2.3, 18.5)),
                  SB.look("attic", (6.0, -22.0, 12.0), (0.0, -10.25, 13.5), lens=50.0),
                  SB.look("pavilion", (-9.0, -24.0, 4.0), (-18.0, -9.6, 5.0)),
                  SB.look("side", (42.0, -18.0, 6.0), (24.4, 4.0, 5.0)),
                  SB.look("service", (26.0, 30.0, 3.0), (18.9, 16.5, 3.0)),
                  SB.look("ladder", (-3.0, 15.0, 9.0), (-13.4, 9.25, 9.0)),
                  SB.look("deck", (26.0, -8.0, 34.0), (10.0, 4.0, 14.6)))
    return SB.render_views(BUILD, out_dir, level, res, distance=150.0, views=views,
                           figures=[(2.6, -11.2)])


if __name__ == "__main__":
    BUILD.main(build_all, facts)
