# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of konepaja_element_monitors, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A Nordic machinery works (*konepaja*: an engineering works, a machine shop)
of the 1970s-80s in precast concrete elements, one building on a 32 x 24 m
plan, its long side to the street. At the back the production hall, 32 x 16
m: exposed-aggregate wall panels with a smooth column cover on every 5.33 m
column line, a dark profiled-sheet fascia from 7.5 to 8.5 m round a flat felt
roof, one high window in every bay, and across the roof three long glazed
rooflight monitors on the column lines with two rows of opal domes between
them, an air handler, three extract fans and a guyed steel flue at the back
west corner. In front of it, toward the street, a two-storey office nose at
the west corner in smooth pale panels with a ribbon of lights to each
storey, its glazed entrance and stair bay under a cantilevered canopy and
KONEPAJA on its fascia, and east of it a single-storey staff and stores
strip in the hall's panels with two windows and a door. The truck door, 3.3 x
3.9 m, is in the hall's east wall close behind the strip, with a personnel
door beyond it: a truck drives in from the street along the east side, stands
beside the door and backs out. Nothing of the building stands on the ground
on that side.

Construction is a set of closed solids unioned with Blender's exact boolean:
three plain bodies (the hall, the office, the strip), each a box from the
ground to its deck with its openings built into its walls, set against one
another face to face; the fascia rings, which stand proud of the walls and
make each roof's upstand; the monitors, the domes, the plant, the canopy and
the landing. The union leaves the boundary of one volume, so interior
geometry cannot occur. The caged wall ladder on the hall's west wall is
roof_safety's lean kit, separate solids appended after the weld.

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
EXPORT_DIR = os.path.join(HERE, "export")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import model_facts  # noqa: E402
from asset_build import to_object, union  # noqa: E402
import roof_safety as RS  # noqa: E402
import shell_build as SB  # noqa: E402
from shell_build import Frame  # noqa: E402

asset_build.check_toolchain()
BUILD = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT,
                          tint=L.LIT_FACTOR)
get_material, export_all = BUILD.material, BUILD.export_all
render_preview, render_variants = BUILD.render_preview, BUILD.render_variants
Builder = functools.partial(SB.Builder, L.ATLAS)

PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)
HX, HY, YH, OX1, BAY = L.HX, L.HY, L.Y_HALL, L.OX1, L.BAY
FO, FI = L.FAS_OUT, L.FAS_IN
SUNK = 0.10             # plant and rooflights run this far into the deck


# ----------------------------------------------------------------- tiers
def ribbon_whole(level):
    """Past 120 m each office ribbon is one face on its own small region
    (facade_atlas RIB7LO, RIB5LO), the lights painted, instead of a face a
    light."""
    return level == 3


def opening_mode(level):
    """LOD0-LOD2 cut every opening into its wall with reveals; LOD3 paints
    the same rectangle flat. The hall's high windows are in the wall band
    itself, so on the flat tier they need no geometry at all. At the
    consumer's LOD1/LOD2 switch (about 132 m) the 0.12-0.2 m reveals'
    shade still darkened every opening, and flattened there they lightened
    at once; LOD2 has the triangles to keep them, but for the hall's band
    windows (band_cut())."""
    return "cut" if level < 3 else "flush"


def band_cut(level):
    """The hall's high windows are recessed to LOD1 and painted in the wall
    band from LOD2: the band carries their frames, sills and the reveal's
    occlusion inside the panel's edge, so flat they keep their shade, and
    the triangles go to the monitors' lights (monitor_split())."""
    return level < 2


def dome_form(level):
    """Kerb and pyramid to LOD2, then painted on the deck. The domes stand
    0.31 m over the felt: dropped at the consumer's LOD1/LOD2 switch (about
    132 m) the eight light squares sank into the deck at once, and as
    flat-topped boxes on LOD1 they lost the pyramid's lit and shaded
    facets at the LOD0/LOD1 switch (about 59 m). A pyramid is 8 triangles
    more than a box. Past LOD3's switch (about 264 m) a 1.3 m dome is
    3 px."""
    return ("pyramid", "pyramid", "pyramid", None)[level]


def monitor_split(level):
    """A monitor's sides are ten lights each, every light its own face, to
    LOD2; on LOD3 one face samples the whole side at DPPM. At night the
    whole-side region's glow is wider and brighter than the ten lit
    lights, and at the consumer's LOD1/LOD2 switch (about 132 m) the three
    strips visibly changed."""
    return level < 3


def stack_sides(level):
    """The flue sets the building's height and stays on every tier, open
    at its top on every tier: eight sides to 70 m, six to 120 m, four
    past it."""
    return (8, 8, 6, 4)[level]


def stack_rings(level):
    """The rolled rim and the guy collar, 3 cm proud: to 70 m."""
    return level < 2


def guys_kept(level):
    """The guys are 2.5 cm rods, seen as fine lines against the deck by
    their shadows: to LOD1, so they do not go at the consumer's LOD0/LOD1
    switch (about 59 m)."""
    return level < 2


def fan_sides(level):
    """The extract fans: eight sides, six, four; past 120 m none (0.8 m,
    under 8 px)."""
    return (8, 6, 4, 0)[level]


def landing_kept(level):
    """The entrance's one step, 16 cm: to 120 m."""
    return level < 3


# ============================================================== mesh kit
def fill_planar(B, loops, to3d, uvfn):
    """shell_build.fill_planar() on the loops with consecutive repeated
    points dropped first (to 1e-7), as _zone_polys() can repeat a breakpoint
    where an opening meets a region's end."""
    SB.fill_planar(B, [SB.dedupe(lp, 1e-7) for lp in loops], to3d, uvfn)


def _patch(name):
    return SB.uv_patch(L.PATCHES[name])


# ============================================================== openings
class Opening:
    """One opening in a wall: its rectangle (s0, s1, a0, a1), the cuts that
    split its closing plane into lights (vcuts, along s) and modules (hcuts,
    up z), its reveal depth, and its UVs. *cell(fr, s_lo, s_hi, z_lo, z_hi)*
    returns the closing-plane mapping of one cell; *sill*, *jamb* and *head*
    the reveals'. *band* openings (the hall's high windows) are painted into
    the wall band: on the flat tiers they are not built at all."""

    def __init__(self, kind, s0, s1, a0, a1, vcuts, hcuts, depth, cell,
                 sill="sill", jamb="reveal", head="reveal", band=False, lo=None):
        self.kind, self.s0, self.s1, self.a0, self.a1 = kind, s0, s1, a0, a1
        self.vcuts = sorted(set([s0, s1] + list(vcuts)))
        self.hcuts = sorted(set([a0, a1] + list(hcuts)))
        self.depth, self.cell = depth, cell
        self.sill, self.jamb, self.head = sill, jamb, head
        self.band, self.lo = band, lo
        self.ground = a0 < EPS
        self.bs = self.jz = None


def _region_cell(rect, s_origin, z_origin, ppm=PPM):
    def make(fr, slo, shi, zlo, zhi):
        return SB.uv_region(fr, rect, s_origin, z_origin, ppm)
    return make


def lights(kind, s0, n, light_w, sill, head, rect, depth, lo=None):
    """A band of *n* equal lights, each its own face on its own region; *lo*,
    a region with the whole band, for the tier that draws it as one face."""
    x, y, _w, _h = rect

    def cell(fr, slo, shi, zlo, zhi):
        k = int(math.floor((0.5 * (slo + shi) - s0) / light_w))
        o = s0 + k * light_w
        return lambda co: (x + (fr.s_of(co) - o) * PPM, y + (co.z - sill) * PPM)
    return Opening(kind, s0, s0 + n * light_w, sill, head,
                   [s0 + k * light_w for k in range(n + 1)], [], depth, cell, lo=lo)


def whole(o):
    """Opening *o* as one face on its lo region."""
    x, y, _w, _h = o.lo
    k = L.LPPM

    def cell(fr, slo, shi, zlo, zhi):
        return lambda co: (x + (fr.s_of(co) - o.s0) * k, y + (co.z - o.a0) * k)
    return Opening(o.kind, o.s0, o.s1, o.a0, o.a1, [], [], o.depth, cell, o.sill, o.jamb,
                   o.head, o.band)


def band_window(s0, zone_uv):
    """A hall window: the AGG band's own window, recessed on the cut tiers."""
    def cell(fr, slo, shi, zlo, zhi):
        return zone_uv
    return Opening("hwin", s0, s0 + L.HWIN_W, L.Z_HSILL, L.Z_HHEAD, [], [], 0.15, cell,
                   band=True)


def entrance(s0):
    """The office's entrance and stair bay: four modules up the glazing."""
    def cell(fr, slo, shi, zlo, zhi):
        zm = 0.5 * (zlo + zhi)
        j = max(k for k in range(len(L.E_MODS) - 1) if L.E_MODS[k] <= zm + EPS)
        x, y, _w, _h = L.REGION[L.E_REGIONS[j]]
        z0 = L.E_MODS[j]
        return lambda co: (x + (fr.s_of(co) - s0) * PPM, y + (co.z - z0) * PPM)
    return Opening("entrance", s0, s0 + (L.E_X1 - L.E_X0), L.E_MODS[0], L.E_MODS[-1],
                   [], L.E_MODS, 0.2, cell, sill="conc", jamb="door_reveal",
                   head="door_reveal")


def truck_door(s0):
    """The sectional truck door: six sections, the fifth windowed."""
    x, y, _w, _h = L.TRUCK
    sec = L.TD_SEC

    def cell(fr, slo, shi, zlo, zhi):
        j = int(math.floor(0.5 * (zlo + zhi) / sec))
        off = sec * PPM if j == L.TD_WIN_SEC else 0.0
        return lambda co: (x + (fr.s_of(co) - s0) * PPM, y + off + (co.z - j * sec) * PPM)
    return Opening("truck", s0, s0 + L.TD_W, 0.0, L.TD_H, [],
                   [k * sec for k in range(L.TD_SECS + 1)], 0.2, cell,
                   sill="conc", jamb="door_reveal", head="door_reveal")


def service_door(s0):
    return Opening("service", s0, s0 + L.SD_W, 0.0, L.SD_H, [], [], 0.15,
                   _region_cell(L.SERVICE, s0, 0.0), sill="conc", jamb="door_reveal",
                   head="door_reveal")


# ================================================================== walls
def uv_agg(fr, u_off, v_shift=0.0):
    """The precast band, U along the wall from its bay phase, V the height
    (less *v_shift*)."""
    return lambda co: ((fr.s_of(co) + u_off) * PPM, L.AGG_Y0 + (co.z - v_shift) * PPM)


def uv_off(fr, u_off, v_shift):
    return lambda co: ((fr.s_of(co) + u_off) * PPM, L.OFF_Y0 + (co.z - v_shift) * PPM)


def uv_blank(fr, u_off):
    return _patch("blank")


class Wall:
    """One wall: its plan ends (walked anticlockwise seen from above), its
    zones (z0, z1, uv maker) from the ground up, its openings, and the U
    offset of its band."""

    def __init__(self, name, p0, p1, zones, u_off=0.0, items=None):
        self.name, self.p0, self.p1, self.zones = name, p0, p1, zones
        self.u_off = u_off
        self.fr = Frame(p0, p1)
        self.items = items(self) if callable(items) else (items or [])


def _zone_polys(L_, z0, z1, ops):
    """The wall regions of one zone: (outline, holes) in (s, z), each
    opening that reaches the zone a hole, a notch from its foot or head, or
    a cut right through it, with every breakpoint of the opening's outline
    that lies on the region's."""
    inz = [o for o in ops if o.a1 > z0 + EPS and o.a0 < z1 - EPS]
    full = sorted([o for o in inz if o.a0 <= z0 + EPS and o.a1 >= z1 - EPS],
                  key=lambda o: o.s0)
    pieces, start, left = [], 0.0, None
    for f in full:
        pieces.append((start, f.s0, left, f))
        start, left = f.s1, f
    pieces.append((start, L_, left, None))
    out = []
    for p0, p1, lop, rop in pieces:
        inside = [o for o in inz if o not in full and o.s0 >= p0 - EPS and o.s1 <= p1 + EPS]
        bottom = sorted([o for o in inside if o.a0 <= z0 + EPS], key=lambda o: o.s0)
        top = sorted([o for o in inside if o.a1 >= z1 - EPS], key=lambda o: -o.s0)
        holes = [o for o in inside if o.a0 > z0 + EPS and o.a1 < z1 - EPS]
        pts = [(p0, z0)]
        for o in bottom:
            up = [z for z in o.jz if z0 + EPS < z < o.a1 - EPS]
            pts += [(o.s0, z0)] + [(o.s0, z) for z in up] + [(s, o.a1) for s in o.bs]
            pts += [(o.s1, z) for z in reversed(up)] + [(o.s1, z0)]
        pts.append((p1, z0))
        if rop is not None:
            pts += [(p1, z) for z in rop.jz if z0 + EPS < z < z1 - EPS]
        pts.append((p1, z1))
        for o in top:
            dn = [z for z in o.jz if o.a0 + EPS < z < z1 - EPS]
            pts += [(o.s1, z1)] + [(o.s1, z) for z in reversed(dn)]
            pts += [(s, o.a0) for s in reversed(o.bs)]
            pts += [(o.s0, z) for z in dn] + [(o.s0, z1)]
        pts.append((p0, z1))
        if lop is not None:
            pts += [(p0, z) for z in reversed(lop.jz) if z0 + EPS < z < z1 - EPS]
        hl = []
        for o in holes:
            mid = o.jz[1:-1]
            hl.append([(s, o.a0) for s in o.bs] + [(o.s1, z) for z in mid]
                      + [(s, o.a1) for s in reversed(o.bs)] + [(o.s0, z) for z in reversed(mid)])
        out.append((pts, hl))
    return out


def op_mode(o, level):
    """opening_mode() for opening *o*: the hall's windows, painted in the
    wall band with their reveal's occlusion, are flat from LOD2 (band_cut)."""
    if o.band and not band_cut(level):
        return "flush"
    return opening_mode(level)


def build_wall(B, wall, level):
    """One wall, ground to its deck, every opening in it built and holed."""
    fr = wall.fr
    zlines = [z0 for z0, _z1, _mk in wall.zones[1:]]
    ops = [whole(o) if o.lo and ribbon_whole(level) else o for o in wall.items
           if not (op_mode(o, level) == "flush" and o.band)]
    for o in ops:
        mode = op_mode(o, level)
        o.jz = sorted(set([o.a0, o.a1] + [z for z in zlines if o.a0 + EPS < z < o.a1 - EPS]
                          + (o.hcuts if mode == "flush" else [])))
        o.bs = o.vcuts if mode == "flush" else [o.s0, o.s1]
    for z0, z1, mk in wall.zones:
        uv = mk(fr, wall.u_off)
        for outline, holes in _zone_polys(fr.L, z0, z1, ops):
            fill_planar(B, [outline] + holes, lambda s, z: fr.P(s, z), uv)
    for o in ops:
        build_opening(B, fr, o, op_mode(o, level))
    return ops


def build_opening(B, fr, o, mode):
    """The opening's closing plane, split into its cells, set back o.depth
    behind reveals on the cut tiers and in the wall's plane on the flat
    ones. Each reveal is one planar face whose outer edge carries the wall's
    breakpoints and its inner edge the closing plane's."""
    if mode == "flush":
        hs, vs, d = o.jz, o.bs, 0.0
    else:
        hs, vs, d = o.hcuts, o.vcuts, o.depth
    for i in range(len(vs) - 1):
        for j in range(len(hs) - 1):
            a, b, z0, z1 = vs[i], vs[i + 1], hs[j], hs[j + 1]
            B.face([fr.P(a, z0, -d), fr.P(b, z0, -d), fr.P(b, z1, -d), fr.P(a, z1, -d)],
                   o.cell(fr, a, b, z0, z1))
    if mode == "flush":
        return
    # sill (unless the opening stands on the ground), head, jambs
    if not o.ground:
        fill_planar(B, [[(o.s0, 0.0), (o.s1, 0.0)] + [(s, -d) for s in reversed(o.vcuts)]],
                    lambda s, w: fr.P(s, o.a0, w), _patch(o.sill))
    fill_planar(B, [[(o.s0, 0.0), (o.s1, 0.0)] + [(s, -d) for s in reversed(o.vcuts)]],
                lambda s, w: fr.P(s, o.a1, w), _patch(o.head))
    for s in (o.s0, o.s1):
        fill_planar(B, [[(z, 0.0) for z in o.jz] + [(z, -d) for z in reversed(o.hcuts)]],
                    lambda z, w, s=s: fr.P(s, z, w), _patch(o.jamb))


def body(walls, z_top, level):
    """A closed box from the ground to its deck: the walls with their
    openings, the deck on the roof plan, and a ground face with a notch for
    every recess that stands on the ground."""
    B = Builder()
    ground = []
    for w in walls:
        ops = build_wall(B, w, level)
        fr = w.fr
        ground.append(fr.P(0.0, 0.0)[:2])
        for o in sorted([o for o in ops if o.ground], key=lambda o: o.s0):
            if op_mode(o, level) == "cut":
                ground += [fr.P(o.s0, 0.0)[:2]] + [fr.P(s, 0.0, -o.depth)[:2] for s in o.vcuts]
                ground.append(fr.P(o.s1, 0.0)[:2])
            else:
                ground += [fr.P(s, 0.0)[:2] for s in o.bs]
    corners = [w.fr.P(0.0, 0.0)[:2] for w in walls]
    fill_planar(B, [list(reversed(corners))], lambda x, y: (x, y, z_top), uv_plan)
    fill_planar(B, [ground], lambda x, y: (x, y, 0.0), _patch("blank"))
    return B


def uv_plan(co):
    px, py = L.plan_px(co.x, co.y)
    return (px, py)


# ------------------------------------------------------------- the bodies
def hall_walls():
    zone = [(0.0, L.Z_DECK, uv_agg)]

    def windows(nb):
        def make(w):
            uv = uv_agg(w.fr, w.u_off)
            return [band_window(k * BAY + L.HWIN_IN, uv) for k in range(nb)]
        return make

    def east(w):
        uv = uv_agg(w.fr, w.u_off)
        return ([truck_door(TRUCK_S - L.TD_W / 2.0), service_door(STAFF_S - L.SD_W / 2.0)]
                + [band_window(k * BAY + L.HWIN_IN, uv) for k in range(3)])
    south = [(0.0, L.Z_DECK, lambda fr, u: uv_agg(fr, u, L.HALL_SOUTH_V))]
    return [Wall("hall_south", (-HX, YH), (HX, YH), south),
            Wall("hall_east", (HX, YH), (HX, HY), zone, items=east),
            Wall("hall_rear", (HX, HY), (-HX, HY), zone, items=windows(6)),
            Wall("hall_west", (-HX, HY), (-HX, YH), zone, items=windows(3))]


# the hall's east wall, s from its front corner: the truck door centred in
# the first bay, the staff door beyond it in the second
TRUCK_S = BAY / 2.0
STAFF_S = BAY + 1.0


def _office_zones(blank=False):
    if blank:
        mk = uv_blank
        return [(0.0, L.Z_PLINTH, mk), (L.Z_PLINTH, L.ZL, mk), (L.ZL, L.OZ_DECK, mk)]
    return [(0.0, L.Z_PLINTH, uv_agg),
            (L.Z_PLINTH, L.ZL, lambda fr, u: uv_off(fr, u, L.OB_LOWER)),
            (L.ZL, L.OZ_DECK, lambda fr, u: uv_off(fr, u, L.ZL))]


# the office front: a ribbon of seven lights to each storey from the west
# corner, the entrance bay at its east end
O_RIB_S0 = 0.625
O_RIB_N = 7
O_END_S0 = 0.875        # the end walls' ribbons, five lights
O_END_N = 5


def _ribbon(s0, n, sill):
    return lights("olight", s0, n, L.O_LIGHT, sill, sill + L.O_WIN_H, L.OFF_L, 0.12,
                  L.RIB7LO if n == 7 else L.RIB5LO)


def office_walls():
    front_items = [_ribbon(O_RIB_S0, O_RIB_N, L.O_SILL1), _ribbon(O_RIB_S0, O_RIB_N, L.O_SILL2),
                   entrance(L.E_X0 + HX)]
    end = [_ribbon(O_END_S0, O_END_N, L.O_SILL1), _ribbon(O_END_S0, O_END_N, L.O_SILL2)]
    east = [_ribbon(O_END_S0, O_END_N, L.O_SILL2)]
    z = _office_zones()
    return [Wall("office_front", (-HX, -HY), (OX1, -HY), z, 0.0, front_items),
            Wall("office_east", (OX1, -HY), (OX1, YH), z, 3.0, east),
            Wall("office_north", (OX1, YH), (-HX, YH), _office_zones(True)),
            Wall("office_west", (-HX, YH), (-HX, -HY), z, 9.0, end)]


# the strip's front: a window in each of its two whole bays, the stores door
# between them; s from its west end, where the band's phase is mid-bay
STRIP_U = BAY - (OX1 + HX) % BAY
STRIP_WIN_S = [k * BAY + L.HWIN_IN - OX1 for k in (0, 2)]
STORES_S = 8.0 - OX1


def strip_walls():
    """The strip's walls. Its fascia runs flush with the east wall, the
    truck side, so the east wall's head above the eave samples the fascia
    band exactly as the ring's east face over it does; the other walls
    carry the same zone line so the corners share their vertices."""
    zone = [(0.0, L.SZ_EAVE, uv_agg), (L.SZ_EAVE, L.SZ_DECK, uv_agg)]
    fz = lambda fr, u: (lambda co: ((fr.s_of(co) + u) * PPM,                   # noqa: E731
                                    L.FAS_Y0 + (co.z - (L.SZ_TOP - L.FAS_H)) * PPM))
    east = [(0.0, L.SZ_EAVE, uv_agg), (L.SZ_EAVE, L.SZ_DECK, fz)]
    front = ([lights("slight", s, 4, L.S_LIGHT, L.Z_SSILL, L.Z_SHEAD, L.STRIP_L, 0.12)
              for s in STRIP_WIN_S] + [service_door(STORES_S - L.SD_W / 2.0)])
    blank = [(0.0, L.SZ_EAVE, uv_blank), (L.SZ_EAVE, L.SZ_DECK, uv_blank)]
    return [Wall("strip_front", (OX1, -HY), (HX, -HY), zone, STRIP_U, front),
            Wall("strip_east", (HX, -HY), (HX, YH), east, (HX - OX1) + FO),
            Wall("strip_north", (HX, YH), (OX1, YH), blank),
            Wall("strip_west", (OX1, YH), (OX1, -HY), blank)]


# ================================================================ fascias
def prism(B, loops, z0, z1, side, top, bottom):
    """Extrude the plan *loops* (an outline and any holes) from z0 to z1:
    side(loop, edge, p, q) gives each side face's mapping."""
    for li, loop in enumerate(loops):
        n = len(loop)
        for k in range(n):
            p, q = loop[k], loop[(k + 1) % n]
            B.face([(p[0], p[1], z0), (q[0], q[1], z0), (q[0], q[1], z1),
                    (p[0], p[1], z1)], side(li, k, p, q))
    fill_planar(B, loops, lambda x, y: (x, y, z1), top)
    fill_planar(B, loops, lambda x, y: (x, y, z0), bottom)
    return B


def _fascia_uv(z_top, u0, p, q):
    """The fascia band along edge p -> q, U from *u0* metres at p, V from the
    band's foot FAS_H under *z_top*."""
    ln = math.hypot(q[0] - p[0], q[1] - p[1])
    tx, ty = (q[0] - p[0]) / ln, (q[1] - p[1]) / ln
    return lambda co: ((u0 + (co.x - p[0]) * tx + (co.y - p[1]) * ty) * PPM,
                       L.FAS_Y0 + (co.z - (z_top - L.FAS_H)) * PPM)


def ring(outline, kinds, z0, z1, holes=()):
    """A fascia ring over *outline*: each edge's kind 'f' (fascia face, U
    running on round the corners), 'u' (the upstand inside), 'e' (an end
    against a taller neighbour), 'L' (the lettering)."""
    B = Builder()
    run = [0.0]
    for k in range(len(outline)):
        p, q = outline[k], outline[(k + 1) % len(outline)]
        run.append(run[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
    lx, ly, _lw, _lh = L.LETTERS

    def side(li, k, p, q):
        kind = kinds[li][k]
        if kind == "f":
            return _fascia_uv(z1, run[k] if li == 0 else 0.0, p, q)
        if kind == "L":
            return lambda co: (lx + (co.x - L.LET_X0) * PPM, ly + (co.z - z0) * PPM)
        if kind == "u":
            return _patch("upstand")
        return _patch("fasend")
    return prism(B, [outline] + list(holes), z0, z1, side, _patch("cap"), _patch("soffit"))


def hall_ring():
    o = [(-HX - FO, YH - FO), (HX + FO, YH - FO), (HX + FO, HY + FO), (-HX - FO, HY + FO)]
    i = [(-HX + FI, HY - FI), (HX - FI, HY - FI), (HX - FI, YH + FI), (-HX + FI, YH + FI)]
    return ring(o, ["ffff", "uuuu"], L.Z_EAVE, L.Z_TOP, holes=[i])


def office_ring():
    y0, yo, yi = YH, -HY - FO, -HY + FI
    o = [(-HX - FO, yo), (L.LET_X0, yo), (L.LET_X1, yo), (OX1 + FO, yo), (OX1 + FO, y0),
         (OX1 - FI, y0), (OX1 - FI, yi), (-HX + FI, yi), (-HX + FI, y0), (-HX - FO, y0)]
    return ring(o, ["fLffeuuuef"], L.OZ_EAVE, L.OZ_TOP)


def strip_ring():
    yo, yi = -HY - FO, -HY + FI
    # flush with the east wall: nothing oversails the truck lane
    o = [(OX1, yo), (HX, yo), (HX, YH), (HX - FI, YH), (HX - FI, yi), (OX1, yi)]
    return ring(o, ["ffeuue"], L.SZ_EAVE, L.SZ_TOP)


# ============================================================== rooflights
def box(x0, x1, y0, y1, z0, z1, sides, top, bottom):
    """A closed box in its own Builder (shell_build.box()); *sides* is one
    mapping or four, south/east/north/west."""
    return SB.box(Builder(), x0, x1, y0, y1, z0, z1, sides, top, bottom)


def monitor(mx, level):
    """A rooflight monitor along the hall, on a column line: a sheeted
    upstand, then glazing leaning in MON_SLOPE_IN to a flat dark top, so
    the glass reads from above and glows there at night; sheet ends. Its
    sides are ten lights each, every light its own face, to 70 m; past it
    one face samples the whole side at DPPM."""
    h0 = L.MON_W / 2.0
    h1 = h0 - L.MON_SLOPE_IN
    y0 = L.MON_Y0
    y1 = y0 + L.MON_N * L.MON_LIGHT
    zb, zu, zt = L.Z_DECK - SUNK, L.Z_DECK + L.MON_UP, L.Z_DECK + L.MON_H
    B = Builder()
    end = _patch("monend")
    if monitor_split(level):
        ys = [y0 + k * L.MON_LIGHT for k in range(L.MON_N + 1)]
        rx, ry, _w, _h = L.MON_L
        k = PPM

        def fn(sign):
            if sign > 0:
                return lambda co, o: (rx + (co.y - o) * k, ry + (co.z - L.Z_DECK) * k)
            return lambda co, o: (rx + (o + L.MON_LIGHT - co.y) * k, ry + (co.z - L.Z_DECK) * k)
    else:
        ys = [y0, y1]
        rx, ry, _w, _h = L.MONLO
        k = L.DPPM

        def fn(sign):
            if sign > 0:
                return lambda co, o: (rx + (co.y - y0) * k, ry + (co.z - L.Z_DECK) * k)
            return lambda co, o: (rx + (y1 - co.y) * k, ry + (co.z - L.Z_DECK) * k)
    for sign in (1, -1):
        f = fn(sign)
        xa, xb = mx + sign * h0, mx + sign * h1
        for a, b in zip(ys, ys[1:]):
            uv = (lambda co, f=f, a=a: f(co, a))
            B.face([(xa, a, zb), (xa, b, zb), (xa, b, zu), (xa, a, zu)], uv)
            B.face([(xa, a, zu), (xa, b, zu), (xb, b, zt), (xb, a, zt)], uv)
    for a, b in zip(ys, ys[1:]):
        B.face([(mx - h1, a, zt), (mx + h1, a, zt), (mx + h1, b, zt), (mx - h1, b, zt)], uv_plan)
        B.face([(mx - h0, a, zb), (mx + h0, a, zb), (mx + h0, b, zb), (mx - h0, b, zb)],
               _patch("blank"))
    for y in (y0, y1):
        B.face([(mx - h0, y, zb), (mx + h0, y, zb), (mx + h0, y, zu), (mx + h1, y, zt),
                (mx - h1, y, zt), (mx - h0, y, zu)], end)
    return B


def dome(cx, cy, form):
    """A rooflight dome: a sheeted kerb and the opal shell, a low pyramid up
    close, a flat top further out."""
    h, c = L.DOME_HALF, L.DOME_CROWN
    zb, zk = L.Z_DECK - SUNK, L.Z_DECK + L.DOME_TOP
    dx, dy, dw, dh = L.DOME

    def plan(co):
        return (dx + dw / 2.0 + (co.x - cx) * L.OPPM, dy + dh / 2.0 + (co.y - cy) * L.OPPM)
    if form == "box":
        return box(cx - h, cx + h, cy - h, cy + h, zb, zk + 0.08, _patch("kerb"), plan,
                   _patch("blank"))
    B = Builder()
    sq = lambda r: [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)]  # noqa: E731
    base, crown = sq(h), sq(c)
    zc = zk + L.DOME_RISE
    for k in range(4):
        a, b = base[k], base[(k + 1) % 4]
        B.face([a + (zb,), b + (zb,), b + (zk,), a + (zk,)], _patch("kerb"))
        p, q = crown[k], crown[(k + 1) % 4]
        B.face([a + (zk,), b + (zk,), q + (zc,), p + (zc,)], plan)
    B.face([p + (zc,) for p in crown], plan)
    B.face([p + (zb,) for p in reversed(base)], _patch("blank"))
    return B


# ================================================================== plant
def ngon(cx, cy, r_flat, n):
    """Corners of an n-gon round (cx, cy), r_flat to its flats, a flat
    toward -Y."""
    rc = r_flat / math.cos(math.pi / n)
    return [(cx + rc * math.cos(a), cy + rc * math.sin(a))
            for a in [-math.pi / 2.0 + (k + 0.5) * 2.0 * math.pi / n for k in range(n)]]


def stack(level):
    """The guyed steel flue: an n-gon STACK_R to its flats, its foot in the
    deck, open at the top round a flue sunk STACK_DEPTH and sooted, the
    rolled rim and the guy collar proud of it up close. Its faces sample
    STACK by height and by the way round, so the painted ladder keeps its
    place on any number of sides."""
    n = stack_sides(level)
    cx, cy = L.STACK_AT
    zb, zt = L.Z_DECK - SUNK, L.STACK_TOP
    zf = zt - L.STACK_DEPTH
    r = L.STACK_R
    prof = [(zb, r)]
    if stack_rings(level):
        for z0, z1 in ((L.STACK_GUY, L.STACK_GUY + 0.12),):
            prof += [(z0, r), (z0, r + 0.03), (z1, r + 0.03), (z1, r)]
        prof += [(zt - L.STACK_CAP, r), (zt - L.STACK_CAP, r + 0.03), (zt, r + 0.03)]
    else:
        prof.append((zt, r))
    sx, sy, sw, sh = L.STACK
    B = Builder()
    rings = [ngon(cx, cy, rr, n) for _z, rr in prof]
    flue = ngon(cx, cy, r - L.STACK_WALL, n)
    for k in range(n):
        def fn(co, k=k):
            return (sx + (co.z - L.Z_DECK) * L.SPPM, sy + around(co, cx, cy, n, k) * sh)
        for (za, _ra), (zc, _rc), ra, rc in zip(prof, prof[1:], rings, rings[1:]):
            a0, b0 = ra[k], ra[(k + 1) % n]
            a1, b1 = rc[k], rc[(k + 1) % n]
            B.face([a0 + (za,), b0 + (za,), b1 + (zc,), a1 + (zc,)], fn)
        top = rings[-1]
        B.face([top[k] + (zt,), top[(k + 1) % n] + (zt,), flue[(k + 1) % n] + (zt,),
                flue[k] + (zt,)], _patch("rim"))
        fa, fb = flue[(k + 1) % n], flue[k]
        B.face([fa + (zf,), fb + (zf,), fb + (zt,), fa + (zt,)], _patch("soot"))
    B.face([q + (zf,) for q in flue], _patch("soot"))
    B.face([q + (zb,) for q in reversed(rings[0])], _patch("blank"))
    return B


def around(co, cx, cy, n, k):
    """How far round an n-gon centred (cx, cy) point *co* on face *k* lies,
    0 at face 0's first corner to 1 at the last face's end, so a face never
    wraps."""
    a = math.atan2(co.y - cy, co.x - cx)
    a0 = -math.pi / 2.0 + (k + 0.5) * 2.0 * math.pi / n
    d = ((a - a0 + math.pi) % (2.0 * math.pi)) - math.pi
    return k / float(n) + d / (2.0 * math.pi)


def guy_feet():
    cx, cy = L.STACK_AT
    return [(cx + L.GUY_R * math.cos(math.radians(a)), cy + L.GUY_R * math.sin(math.radians(a)))
            for a in L.GUY_ANGLES]


def bar(p0, p1, w, uv):
    """A straight square bar *w* across from *p0* to *p1*, a closed solid."""
    a, b = Vector(p0), Vector(p1)
    d = (b - a).normalized()
    side = d.cross(Vector((0.0, 0.0, 1.0)))
    if side.length < 1e-6:
        side = Vector((1.0, 0.0, 0.0))
    side.normalize()
    up = side.cross(d).normalized()
    h = w / 2.0
    rr = [side * h + up * h, -side * h + up * h, -side * h - up * h, side * h - up * h]
    B = Builder()
    r0, r1 = [tuple(a + q) for q in rr], [tuple(b + q) for q in rr]
    for k in range(4):
        B.face([r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k]], uv)
    B.face(list(reversed(r1)), uv)
    B.face(list(r0), uv)
    return B


def guys():
    """Three guy rods from the collar down to anchor plates in the deck."""
    cx, cy = L.STACK_AT
    top = (cx, cy, L.STACK_GUY + 0.06)
    return [bar((fx, fy, L.Z_DECK - SUNK), top, 0.025, _patch("galv"))
            for fx, fy in guy_feet()]


def fan(fx, fy, n):
    """An extract fan: an n-sided galvanised body and a wider cowl over it,
    its grille seen from above."""
    zb, z1 = L.Z_DECK - SUNK, L.Z_DECK + L.FAN_H
    z2 = z1 + L.FAN_CAP_H
    sx, sy, sw, sh = L.FAN_S
    tx, ty, tw, th = L.FAN_T

    def side(k):
        return lambda co: (sx + around(co, fx, fy, n, k) * sw, sy + (co.z - L.Z_DECK) * L.SPPM)

    def cowl(x, y):
        return (tx + tw / 2.0 + (x - fx) * L.SPPM, ty + th / 2.0 + (y - fy) * L.SPPM)
    body_ = ngon(fx, fy, L.FAN_R, n)
    cap = ngon(fx, fy, L.FAN_CAP_R, n)
    out = []
    B = Builder()
    for k in range(n):
        a, b = body_[k], body_[(k + 1) % n]
        B.face([a + (zb,), b + (zb,), b + (z1,), a + (z1,)], side(k))
    B.face([p + (z1,) for p in body_], _patch("duct"))
    B.face([p + (zb,) for p in reversed(body_)], _patch("blank"))
    out.append(B)
    C = Builder()
    for k in range(n):
        a, b = cap[k], cap[(k + 1) % n]
        C.face([a + (z1 - 0.02,), b + (z1 - 0.02,), b + (z2,), a + (z2,)], _patch("galv"))
    C.face([p + (z2,) for p in cap], lambda co: cowl(co.x, co.y))
    C.face([p + (z1 - 0.02,) for p in reversed(cap)], _patch("duct"))
    out.append(C)
    return out


def ahu():
    """The air handler: a galvanised box on the deck, louvred at its ends,
    access doors along its sides."""
    x0, x1, y0, y1 = L.AHU
    zb, zt = L.Z_DECK - SUNK, L.Z_DECK + L.AHU_H
    sx, sy, _sw, _sh = L.AHU_S
    ex, ey, _ew, _eh = L.AHU_E
    k = L.SPPM

    def long_(sign, start):
        return lambda co: (sx + sign * (co.y - start) * k, sy + (co.z - L.Z_DECK) * k)

    def end_(sign, start):
        return lambda co: (ex + sign * (co.x - start) * k, ey + (co.z - L.Z_DECK) * k)
    sides = [end_(1, x0), long_(1, y0), end_(-1, x1), long_(-1, y1)]
    return box(x0, x1, y0, y1, zb, zt, sides, _patch("galv"), _patch("blank"))


# =============================================================== entrance
def canopy():
    """The entrance canopy: a thin cantilevered slab from the first floor,
    its edge the fascia's sheet, felt on top, a pale soffit under it. Its
    back runs CANOPY_BURY into the wall and through the bay's glazing."""
    x0, x1, proj = L.CANOPY
    y0, y1 = -HY - proj, -HY + CANOPY_BURY
    z0, z1 = L.Z_CAN0, L.Z_CAN1
    fx = _fascia_uv(z1, 0.0, (x0, y0), (x1, y0))
    fy = _fascia_uv(z1, 0.0, (x0, y0), (x0, y1))
    return box(x0, x1, y0, y1, z0, z1, [fx, fy, _patch("blank"), fy], _patch("felt"),
               _patch("soffit"))


CANOPY_BURY = 0.25
LANDING = (-6.0, -3.0, 1.2)             # x0, x1, out from the wall


def landing():
    """One concrete step up to the entrance's threshold, its back against
    the plinth."""
    x0, x1, out = LANDING
    return box(x0, x1, -HY - out, -HY, 0.0, L.O_FLOOR, _patch("conc"), _patch("conc"),
               _patch("blank"))


# ----------------------------------------------------------------- the kit
# The lean kit (scripts/roof_safety.py): the wall ladder and its cage on the
# hall's west wall, on the column line at the back bay's end, as separate
# solids appended after the weld. The plinth and the column covers are
# painted flush, so nothing stands proud behind the brackets.
WEST = ((-HX, HY), (-HX, YH))
EAVE = RS.Eave(*WEST, L.Z_EAVE, FO, L.Z_TOP, 0.0)
LADDER_S = BAY
WALL_LADDER = RS.WallLadder(EAVE, LADDER_S, lean=True)
CAGE = RS.Cage(WALL_LADDER) if WALL_LADDER.length > RS.CAGE_LADDER else None
KIT = [WALL_LADDER] + ([CAGE] if CAGE else [])
PAINT = RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)


def kit(level):
    """The ladder and its cage, roof_safety's MODES and CAGE_MODES
    unchanged, with extents: LOD3 keeps the bare rails and the cage's back
    strap, which set the plan's west extent."""
    return RS.solids(KIT, level, PAINT, extents=True)


# ================================================================ assembly
def build_lod(level):
    base = to_object(body(hall_walls(), L.Z_DECK, level), "tmp_hall")
    parts = [to_object(body(office_walls(), L.OZ_DECK, level), "tmp_office"),
             to_object(body(strip_walls(), L.SZ_DECK, level), "tmp_strip"),
             to_object(hall_ring(), "tmp_hall_ring"),
             to_object(office_ring(), "tmp_office_ring"),
             to_object(strip_ring(), "tmp_strip_ring"),
             to_object(canopy(), "tmp_canopy"),
             to_object(stack(level), "tmp_stack"),
             to_object(ahu(), "tmp_ahu")]
    if landing_kept(level):
        parts.append(to_object(landing(), "tmp_landing"))
    for i, mx in enumerate(L.MON_X):
        parts.append(to_object(monitor(mx, level), "tmp_monitor%d" % i))
    form = dome_form(level)
    if form:
        for i, (dx, dy) in enumerate([(x, y) for x in L.DOME_X for y in L.DOME_Y]):
            parts.append(to_object(dome(dx, dy, form), "tmp_dome%d" % i))
    if guys_kept(level):
        for i, B in enumerate(guys()):
            parts.append(to_object(B, "tmp_guy%d" % i))
    n = fan_sides(level)
    if n:
        for i, (fx, fy) in enumerate(L.FANS):
            for j, B in enumerate(fan(fx, fy, n)):
                parts.append(to_object(B, "tmp_fan%d_%d" % (i, j)))
    # snapped to 0.1 mm first: the office's east wall and the strip's west
    # end share x = -2.667 m, which each solid's arithmetic reaches a hair
    # apart, and only exactly coplanar faces merge in the exact boolean
    obj = union(base, parts, snap=asset_build.SNAP)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # 1e-4: the exact boolean leaves the odd corner vertex a hundredth of a
    # millimetre off its neighbour; the smallest authored feature is far
    # larger than a 0.1 mm weld can reach.
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # Recover the cost of coplanar boolean subdivisions. Keep UV and
    # material seams and every architectural edge.
    bmesh.ops.dissolve_limit(bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
                             delimit={'UV', 'MATERIAL'})
    bm.to_mesh(obj.data)
    bm.free()
    east_side_clear(obj, level)
    RS.append(obj, kit(level), check=True)
    return obj


def east_side_clear(obj, level):
    """The truck lane: nothing of the building outside the east wall's plane
    below the strip's fascia, the lowest thing that may oversail it."""
    bad = [v.co for v in obj.data.vertices if v.co.x > HX + 1e-4 and v.co.z < L.SZ_EAVE - 1e-4]
    if bad:
        raise ValueError("LOD%d: %d vertices stand outside the east wall under %.2f m, e.g. %s"
                         % (level, len(bad), L.SZ_EAVE, tuple(round(c, 3) for c in bad[0])))


# ================================================================== checks
def check_layout():
    """Numbers that have to agree before any geometry is worth looking at."""
    bad = []
    walls = hall_walls() + office_walls() + strip_walls()
    for w in walls:
        L_ = w.fr.L
        rects = [(o.kind, o.s0, o.s1, o.a0, o.a1) for o in w.items]
        for k, s0, s1, a0, a1 in rects:
            if s0 < 0.4 or s1 > L_ - 0.4:
                bad.append("%s: %s at %.2f is within 0.4 m of a corner" % (w.name, k, s0))
            for z0, z1, _mk in w.zones:
                for z in (z0, z1):
                    if abs(a0 - z) < 0.05 and a0 > EPS or abs(a1 - z) < 0.05:
                        bad.append("%s: %s's edge lies on a zone line" % (w.name, k))
        for i, a in enumerate(rects):
            for b in rects[i + 1:]:
                if SB.overlap(a[1:], b[1:], 0.3):
                    bad.append("%s: the %s and the %s are within 0.3 m" % (w.name, a[0], b[0]))
    # storeys, doors and sills: the human scale
    if not 3.0 <= L.O_FLOOR2 - L.O_FLOOR <= 3.3:
        bad.append("the office's storey is outside 3.0-3.3 m")
    if not 2.0 <= L.Z_LEAF <= 2.4:
        bad.append("the entrance's leaves are outside 2.0-2.4 m")
    if L.E_MODS[1] - L.O_FLOOR <= L.Z_LEAF + 0.05:
        bad.append("the entrance's transom is not over its leaves")
    if not 2.0 <= L.SD_H - L.SD_FRAME <= 2.4:
        bad.append("the personnel doors' leaves are outside 2.0-2.4 m")
    for z, floor, what in ((L.O_SILL1, L.O_FLOOR, "ground ribbon"),
                           (L.O_SILL2, L.O_FLOOR2, "upper ribbon")):
        if not 0.8 <= z - floor <= 1.0:
            bad.append("the %s's sills are not at desk height" % what)
    if L.O_SILL2 + L.O_WIN_H > L.OZ_EAVE - 0.5:
        bad.append("the upper ribbon runs into the fascia")
    if L.O_SILL1 + L.O_WIN_H > L.ZL - 0.3 or L.O_SILL2 < L.ZL + 0.3:
        bad.append("a ribbon is within 0.3 m of the storey band's change")
    # the hall's windows over the strip's fascia; the monitors on the column
    # lines, 11 m apart, clear of the fascia; the domes between them
    if L.Z_HSILL < L.SZ_TOP + 0.4:
        bad.append("the hall's windows are within 0.4 m of the strip's fascia")
    for mx in L.MON_X:
        if abs(mx / BAY - round(mx / BAY)) > 1e-6:
            bad.append("a monitor is off the column lines")
    y_end = L.MON_Y0 + L.MON_N * L.MON_LIGHT
    if L.MON_Y0 - (YH + FI) < 1.2 or (HY - FI) - y_end < 1.2:
        bad.append("a monitor's end is within 1.2 m of the fascia")
    plant = [(mx, (L.MON_Y0 + y_end) / 2.0, L.MON_W / 2.0, (y_end - L.MON_Y0) / 2.0,
              "monitor") for mx in L.MON_X]
    plant += [(dx, dy, L.DOME_HALF, L.DOME_HALF, "dome") for dx in L.DOME_X for dy in L.DOME_Y]
    plant += [(fx, fy, L.FAN_CAP_R, L.FAN_CAP_R, "fan") for fx, fy in L.FANS]
    x0, x1, y0, y1 = L.AHU
    plant.append(((x0 + x1) / 2.0, (y0 + y1) / 2.0, (x1 - x0) / 2.0, (y1 - y0) / 2.0, "ahu"))
    plant.append(L.STACK_AT + (L.STACK_R + 0.03, L.STACK_R + 0.03, "stack"))
    plant += [(fx, fy, 0.05, 0.05, "guy") for fx, fy in guy_feet()]
    for i, (px, py, rx, ry, what) in enumerate(plant):
        if px - rx < -HX + FI + 0.3 or px + rx > HX - FI - 0.3 or \
                py - ry < YH + FI + 0.3 or py + ry > HY - FI - 0.3:
            bad.append("the %s at (%.1f, %.1f) crowds the fascia" % (what, px, py))
        for qx, qy, qrx, qry, other in plant[i + 1:]:
            if abs(px - qx) < rx + qrx + 0.4 and abs(py - qy) < ry + qry + 0.4:
                bad.append("the %s at (%.1f, %.1f) crowds the %s" % (what, px, py, other))
        for ox, oy in L.OUTLETS:
            if abs(px - ox) < rx + 0.4 and abs(py - oy) < ry + 0.4:
                bad.append("the %s at (%.1f, %.1f) stands on an outlet" % (what, px, py))
    if L.STACK_TOP - L.Z_TOP < 6.0 or L.STACK_TOP - L.Z_TOP > 8.0:
        bad.append("the flue is not 6-8 m over the fascia")
    # the flue in the back west corner, clear of the truck side
    if L.STACK_AT[0] > -HX / 2.0 or L.STACK_AT[1] < HY / 2.0:
        bad.append("the flue is not in the back west corner")
    # the canopy over the entrance, wider than the bay, clear of the ribbons
    cx0, cx1, proj = L.CANOPY
    if cx0 > L.E_X0 - 0.3 or cx1 < L.E_X1 + 0.3 or cx1 > OX1 - 0.05:
        bad.append("the canopy does not cover the entrance bay within the office")
    if cx0 < -HX + O_RIB_S0 + O_RIB_N * L.O_LIGHT + 0.2:
        bad.append("the canopy runs within 0.2 m of the ribbons")
    if not L.E_MODS[1] < L.Z_CAN0 < L.Z_CAN1 < L.E_MODS[2]:
        bad.append("the canopy is not over the spandrel")
    if LANDING[2] > proj - 0.2:
        bad.append("the canopy does not cover the landing")
    # the east side: the truck door near the street front, nothing on the
    # ground on that side
    if TRUCK_S - L.TD_W / 2.0 < 0.6:
        bad.append("the truck door is within 0.6 m of the hall's corner")
    # the ladder and its cage clear of the west wall's windows and corners
    avoid = [("window", k * BAY + L.HWIN_IN, k * BAY + L.HWIN_IN + L.HWIN_W) for k in range(3)]
    bad += RS.problems(WALL_LADDER, "the wall ladder", avoid)
    if CAGE:
        bad += RS.problems(CAGE, "the ladder's cage", avoid)
    return bad


# ================================================================== build
def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
ENT_LEAF_W = 2 * L.E_LEAF_PX / PPM
SD_LEAF = (L.SD_W - 2 * L.SD_FRAME, L.SD_H - L.SD_FRAME)


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the outer wall faces, 32 x 24 m;
    the fascias' 9 cm oversail, the canopy, the landing step and the caged
    ladder on the west wall stand outside it. One storey over the whole
    plan at the ground, the office's upper floor over its 13.3 x 8 m. The
    main door is the office's entrance; the truck door and the staff door
    are on the hall's east wall, the stores door on the strip's front."""
    hall_east = ((HX, YH), (HX, HY))
    office_front = ((-HX, -HY), (OX1, -HY))
    strip_front = ((OX1, -HY), (HX, -HY))
    s_ent = L.E_X0 + HX + (L.E_X1 - L.E_X0) / 2.0
    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-HX, -HY), (HX, -HY), (HX, HY), (-HX, HY)],
        "storeys": [(0.0, 2 * HX * 2 * HY), (L.O_FLOOR2, (OX1 + HX) * (YH + HY))],
        "doors": [
            model_facts.wall_door("entrance", "entrance", *office_front, s_ent, L.O_FLOOR,
                                  ENT_LEAF_W, L.Z_LEAF, main=True),
            model_facts.wall_door("loading", "vehicle", *hall_east, TRUCK_S, 0.0,
                                  L.TD_W, L.TD_H),
            model_facts.wall_door("staff", "service", *hall_east, STAFF_S, 0.0, *SD_LEAF),
            model_facts.wall_door("stores", "service", *strip_front, STORES_S, 0.0, *SD_LEAF),
        ],
    }


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000), night=False):
    """The six working views (shell_build.render_views()), plus an aerial
    off the rear corner, eye views at the entrance, along the truck lane and
    at the truck door. Working views only -- not committed."""
    r2 = math.sqrt(2.0)
    return SB.render_views(BUILD, out_dir, level, res, distance=60.0, views=(
        SB.orbit("aerial", (1.0, -1.0, r2), 2.6),
        SB.orbit("aerial_rear", (-1.0, 1.0, r2), 2.6),
        SB.orbit("eye_entrance", (0.5, -1.0, 0.08), 0.45,
                 target=((L.E_X0 + L.E_X1) / 2.0, -HY, 2.5)),
        SB.orbit("eye_lane", (0.35, -1.0, 0.05), 0.75, target=(HX, YH, 2.5)),
        SB.orbit("eye_truck", (1.0, -0.25, 0.08), 0.45, target=(HX, YH + TRUCK_S, 2.0))))


if __name__ == "__main__":
    BUILD.main(build_all, facts)
