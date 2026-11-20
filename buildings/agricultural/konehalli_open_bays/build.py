# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of konehalli_open_bays, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, renders preview.png and writes the facts
sidecar:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite Finnish konehalli, the machine shed of a small post-war grain
farm: a low 10.5 x 6.0 m board-and-batten shed under a mono-pitch roof that
falls from the yard side to the rear, three 3.5 m bays along it. Two bays are
open to the yard, the full depth of the shed, with a white post between them
and a white header over them; the third is a closed workshop with a pair of
framed board doors on the front and a pedestrian door in its end wall.

Construction is a set of closed solids unioned with Blender's exact boolean:
the wall ring, the roof slab, the post and the header. The wall ring is not a
rectangle: the open bays are a notch taken out of its plan, so the ring is the
closed bay plus a back wall and an end wall one board-wall thick, and the
notch's faces -- the bays' side walls and back wall -- are ordinary outside
surface of the one closed shell. The roof slab passes over the notch, and its
underside there is the bays' ceiling. The bays have no floor face: the ground
is their floor, so the shell's bottom is the wall ring's own floor cap and
the post's foot, nothing in between.

The roof sheds its water to the rear, so the rear eave carries the gutter,
painted on its fascia, and a downpipe stands at each end of the rear wall
(scripts/downpipes.py), unioned like the rest. The snow guard above that
eave is painted on the roof's lowest strip, which maps onto its own rows of
the atlas (facade_atlas.py).

The shed has no glazing and so no emission map (CLAUDE.md, Output Contract);
UnlitAsset below is asset_build.Asset without the window wiring.
"""

import importlib
import math
import os
import sys

import bmesh
import bpy
from mathutils import Euler, Vector, geometry


HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import facade_atlas as L  # noqa: E402  (layout constants shared with the atlas)
importlib.reload(L)       # an interactive session must not keep a stale layout

ASSET = L.ASSET
EXPORT_DIR = os.path.join(HERE, "export")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import asset_build  # noqa: E402
import downpipes as DP  # noqa: E402
import model_facts  # noqa: E402
from asset_build import bounds as _bounds, pivot_offset, to_object, union  # noqa: E402,F401
from glb_images import strip_embedded_images  # noqa: E402

asset_build.check_toolchain()


class UnlitAsset(asset_build.Asset):
    """asset_build.Asset for a building with no glazing, hence no emission map.

    The shared Asset always wires a window-emission mask into the material,
    exports every tier lit and rewrites the factor to zero, and renders a
    day/night variants.png; all three need the emission PNG this shed does
    not have (CLAUDE.md allows a windowless shed to ship none). This keeps
    the shared material, previews and bookkeeping and leaves out only the
    window wiring: material() builds the shared material with attach()
    disabled, export_all() is the shared export without the emission
    rewrite, and there is no day/night sheet to render. It belongs in
    scripts/asset_build.py as an option once a second unlit asset needs it.
    """

    def material(self, variant=None):
        attach = asset_build.attach
        asset_build.attach = lambda *args, **kwargs: None
        try:
            return super().material(variant)
        finally:
            asset_build.attach = attach

    def export_all(self):
        written = []
        for level in self.levels:
            obj = self.lod(level)
            for other in bpy.data.objects:
                other.select_set(False)
            obj.hide_set(False)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            path = os.path.join(self.export_dir, "{}_lod{}.glb".format(self.name, level))
            bpy.ops.export_scene.gltf(
                filepath=path, export_format='GLB', use_selection=True,
                export_yup=True, export_apply=True, export_keep_originals=True,
                export_cameras=False, export_lights=False)
            obj.select_set(False)
            strip_embedded_images(path)
            written.append(os.path.basename(path))
        self.show_only(0)
        return written

    def render_preview(self):
        self.preview_studio()
        self.show_only(0)
        self.material(self.default_variant)
        path = os.path.join(self.here, "preview.png")
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        return path

    def render_variants(self, tile_w=640):
        return "no variants.png: not night-lit (no glazing)"


BUILD = UnlitAsset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT)
get_material, export_all = BUILD.material, BUILD.export_all
_show_only, preview_studio = BUILD.show_only, BUILD.preview_studio
render_preview = BUILD.render_preview
PPM = L.PPM
EPS = 1e-6
LEVELS = (0, 1, 2, 3)

# ------------------------------------------------------------------ massing
# Front (the yard side) faces -Y. Outer walls 10.5 x 6.0 m.
HX, HY = L.HX, L.HY
T_WALL = 0.20                    # the open bays' back and end walls, one board wall
X_BAYS = -HX + T_WALL            # the end wall's inner face
Y_BACK = HY - T_WALL             # the back wall's inner face
X_PART = 1.55                    # the closed bay's west face: the bays' partition
# The closed bay is 3.70 m (it takes the 3.0 m door pair with its casing and
# room for the corner boards); the open span 6.60 m, split by one post into
# two 3.2 m clear bays.
POST_X = (X_BAYS + X_PART) / 2.0
POST_HALF = L.POST_W / 2.0
POST_Y = (-HY, -HY + L.POST_W)
POST_TOP = 4.10                  # up into the roof slab
# The header over the open span: 5 cm back from the post's face, so no face of
# it is coplanar with a wall's; its ends run into the end wall and the closed
# bay and its top into the slab.
HEADER_X = (-HX + 0.10, X_PART + 0.10)
HEADER_Y = (-HY + 0.05, -HY + 0.25)
HEADER_Z = (3.70, 4.08)
SOFFIT_IN = 0.05                 # rake soffit strips start inside the end walls

Z_FOOT = L.Z_FOOT
TAN = L.TAN


def z_under(y):
    return L.z_under(y)


def z_top(y):
    """The wall ring's lid: WALL_INTO up into the slab, everywhere."""
    return z_under(y) + L.WALL_INTO


# ---------------------------------------------------------------- elevations
# Each wall runs counter-clockwise seen from above, so its outward face is on
# the right and s runs along it from p0. kind: "outer" walls carry the board
# band and corner boards; "side" and "back" are the open bays' inner faces;
# "end" is the end wall's 0.2 m face at the open front, a white post.
# Items are (opening kind, s at the centre, z at the threshold).
WALLS = [
    dict(name="end_front", kind="end", p0=(-HX, -HY), p1=(X_BAYS, -HY)),
    dict(name="bay_west", kind="side", p0=(X_BAYS, -HY), p1=(X_BAYS, Y_BACK)),
    dict(name="bay_back", kind="back", p0=(X_BAYS, Y_BACK), p1=(X_PART, Y_BACK),
         u_off=0.0),
    dict(name="bay_east", kind="side", p0=(X_PART, Y_BACK), p1=(X_PART, -HY)),
    dict(name="front", kind="outer", p0=(X_PART, -HY), p1=(HX, -HY),
         items=[("door_pair", (HX - X_PART) / 2.0, 0.0)], u_off=0.0),
    dict(name="east", kind="outer", p0=(HX, -HY), p1=(HX, HY),
         items=[("door", 1.50, 0.0)], u_off=4.3),
    dict(name="rear", kind="outer", p0=(HX, HY), p1=(-HX, HY), items=[], u_off=7.7),
    dict(name="west", kind="outer", p0=(-HX, HY), p1=(-HX, -HY), items=[], u_off=2.9),
]


# ----------------------------------------------------------------- downpipes
# One at each end of the rear wall, DP.CORNER in from the corners: the gutter
# runs the slab's full 11.3 m, the rear wall is blank, and a pipe at each end
# halves the run each one drains and shows from both end walls' oblique views.
#
# The rear eave projects 0.20 m, so the module's swan-neck would leave the
# soffit at DP.outlet(0.20) = 0.11 m and come back to the pipe's axis at
# DP.OUT = 0.08 m: a 0.03 m jog, under two pixels at 20 m, for 32 more
# triangles a pipe. These run straight up into the soffit instead, the
# module's own course under a shallow overhang (outlet None).
#
# The module's shoe kicks its mouth 0.15 m out, which would reach 0.27 m off
# the wall, past the 0.20 m eave: LOD0 and LOD1 would then be deeper than the
# unbent LOD2 and LOD3, and asset_build refuses tiers whose extents differ.
# ShedPipe kicks it SHOE_KICK instead, keeping the whole pipe under the eave.
SHOE_KICK = 0.075
DOWNPIPE_S = (DP.CORNER, 2 * HX - DP.CORNER)


class ShedPipe(DP.Pipe):
    """DP.Pipe with a shorter shoe, so the pipe stays under the 0.20 m eave."""

    def path(self, bent=True):
        p = super().path(bent)
        if bent:
            z0 = DP.SHOE[0]
            p[-1] = (DP.OUT + SHOE_KICK, z0 - SHOE_KICK)
        return p


def shoe_reach():
    """How far the shoe's mouth reaches off the wall: its axis, plus the
    ring's half-width A along the mouth's normal, which is 45 degrees off
    horizontal."""
    return DP.OUT + SHOE_KICK + DP.A * math.sqrt(0.5)


_REAR = next(w for w in WALLS if w["name"] == "rear")
DOWNPIPES = [ShedPipe(_REAR["p0"], _REAR["p1"], s,
                      lambda out: L.Z_EAVE_R - out * TAN) for s in DOWNPIPE_S]


def pipe_mode(level):
    """DP.MODES on every tier: the pipes cost little and LOD3 keeps them, as
    the module does by default."""
    return DP.MODES[level]


def item_mode(kind, level):
    """How a door is built at each tier.

    ring  - LOD0: the casing is a ring of faces on the wall, the leaf inside it
            is recessed with reveals.
    cut   - LOD1: one recess the size of the casing, the casing painted on the
            recessed plane.
    flush - LOD2/3: the casing rect as a flat quad in the wall.
    """
    return ("ring", "cut", "flush", "flush")[level]


def keeps_post(level):
    return True


def keeps_header(level):
    """The header sets the bays' opening height and frames them in white; it
    goes at LOD3, where its 0.29 m face is under three pixels and the roof's
    own fascia line carries the top of the opening."""
    return level < 3


# ============================================================== mesh builder
class Builder:
    """One closed solid under construction, with UVs set as faces are made.

    Vertices are shared through a position cache, so faces that meet along an
    edge meet on the same vertices. That only works if every vertex lying on
    an edge is a corner of both faces -- which is why region outlines carry
    their neighbours' breakpoints explicitly.
    """

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cache = {}

    def v(self, co):
        key = (round(co[0], 4), round(co[1], 4), round(co[2], 4))
        vert = self.cache.get(key)
        if vert is None:
            vert = self.bm.verts.new(co)
            self.cache[key] = vert
        return vert

    def face(self, cos, uvfn):
        verts = []
        for co in cos:
            vv = self.v(co)
            if not verts or verts[-1] is not vv:
                verts.append(vv)
        if len(verts) > 2 and verts[0] is verts[-1]:
            verts.pop()
        if len(verts) < 3:
            return None
        # Area vector (Newell) relative to the first vertex, in double
        # precision, so a door's missing sill (zero area) is reliably skipped.
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
        self.set_uv(f, uvfn)
        return f

    def set_uv(self, f, uvfn):
        for loop in f.loops:
            u, w = uvfn(loop.vert.co)
            loop[self.uv].uv = (u / L.ATLAS, w / L.ATLAS)


class Frame:
    """A wall plane: s runs along the wall from p0, z is world height, and
    depth runs inward, away from the outward normal."""

    def __init__(self, p0, p1):
        self.p0 = Vector((p0[0], p0[1], 0.0))
        d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
        self.L = d.length
        self.t = d / self.L
        self.n = Vector((self.t.y, -self.t.x, 0.0))

    def P(self, s, z, depth=0.0):
        q = self.p0 + self.t * s - self.n * depth
        return (q.x, q.y, z)

    def s_of(self, co):
        return (co.x - self.p0.x) * self.t.x + (co.y - self.p0.y) * self.t.y

    def top(self, s):
        """The wall ring's lid height at s: linear along any straight wall."""
        return z_top(self.p0.y + self.t.y * s)


# ------------------------------------------------------------ UV mappings
# Each returns (u, v) in atlas pixels for a vertex position.

def uv_band(fr, y0, u_off):
    return lambda co: ((fr.s_of(co) + u_off) * PPM, y0 + co.z * PPM)


def uv_side(co):
    """The bays' side walls: U is depth from the front wall line, so both
    walls get the same occlusion at the same depth."""
    x0, y0 = L.SIDE[:2]
    return (x0 + (co.y + HY) * PPM, y0 + co.z * PPM)


def uv_strip(rect, across):
    """A true-scale vertical strip (post or corner board); *across(co)* is the
    distance across it in metres."""
    x0, y0, w, _h = rect
    return lambda co: (x0 + across(co) * PPM, y0 + co.z * PPM)


def uv_item(fr, kind, s_left, z_bot):
    """Planar, at true scale. Recessed faces sit behind the wall only along
    its normal, so they sample the same texels as if they were flush."""
    x0, y0 = L.ITEM_ORIGIN[kind]
    return lambda co: (x0 + (fr.s_of(co) - s_left) * PPM, y0 + (co.z - z_bot) * PPM)


def uv_patch(name):
    x0, y0, w, h = L.PATCHES[name]
    c = (x0 + w / 2.0, y0 + h / 2.0)
    return lambda co: c


ROOF_RPM = L.ROOF_H / L.ROOF_SLOPE_LEN           # atlas rows per metre up the slope


def uv_roof(co):
    """Profiled sheet: U along the ridge-less length, V up the slope from the
    low (rear) edge."""
    return ((co.x + 16.0) * PPM, L.ROOF_Y0 + (L.Y_REAR - co.y) * L.SLOPE_F * ROOF_RPM)


def uv_ceiling(co):
    return ((co.x + 16.0) * PPM, L.CEIL_Y0 + (co.y - L.Y_FRONT) * L.CEIL_RPM)


def uv_fascia_x(co):
    """Front and rear edges: U along x, V up from the slab's underside."""
    return ((co.x + 16.0) * PPM, L.FASC_Y0 + (co.z - z_under(co.y)) * PPM)


def uv_fascia_rear(co):
    """The rear (low) edge, where the gutter is: its own rows, U along x."""
    return ((co.x + 16.0) * PPM, L.FASC_R_Y0 + (co.z - z_under(co.y)) * PPM)


def uv_eave(co):
    """The roof's lowest strip, carrying the snow guard: V up the slope from
    the low edge at EAVE_RPM, continuing the rear fascia's rows past its top."""
    return ((co.x + 16.0) * PPM,
            L.EAVE_ROOF_Y0 + (L.Y_REAR - co.y) * L.SLOPE_F * L.EAVE_RPM)


def uv_fascia_y(co):
    """The rake edges: U along y."""
    return ((co.y + 16.0) * PPM, L.FASC_Y0 + (co.z - z_under(co.y)) * PPM)


# ================================================================== walls
def _flip_slivers(pts, tris):
    """Replace zero-area triangles by flipping their long edge (see
    rintamamiestalo_porch/build.py: collinear corners in a region's outline
    let the triangulator make a triangle of no area)."""
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


def fill_region(B, fr, outline, uvfn):
    """Triangulate a wall region (s, z) outline and add it."""
    tris = geometry.tessellate_polygon([[Vector((s, z, 0.0)) for s, z in outline]])
    for a, b, c in _flip_slivers(outline, tris):
        B.face([fr.P(*outline[a]), fr.P(*outline[b]), fr.P(*outline[c])], uvfn)


def recess(B, fr, rect, depth, fn, rev, floor=True):
    """Push a rectangle *depth* back from the wall and close it.

    An opening that stands on the ground gets no floor of its own, as in
    lahikauppa_corner: the strip it would lay at z = 0 would sit on top of the
    floor the wall ring is capped with. Left out, the ring's rim detours
    round the recess and the floor cap covers it.
    """
    l, r, b, t = rect
    c = [(l, b), (r, b), (r, t), (l, t)]
    for k in range(4):
        if k == 0 and not floor:
            continue
        (s0, z0), (s1, z1) = c[k], c[(k + 1) % 4]
        B.face([fr.P(s0, z0), fr.P(s1, z1), fr.P(s1, z1, depth), fr.P(s0, z0, depth)], rev)
    B.face([fr.P(s, z, depth) for s, z in c], fn)


def item_rects(kind, s, z):
    w, h, cs, cb, ct = L.OPENINGS[kind]
    outer = (s - w / 2 - cs, s + w / 2 + cs, z - cb, z + h + ct)
    inner = (s - w / 2, s + w / 2, z, z + h)
    return outer, inner


def build_item(B, fr, kind, s, z, level):
    """Faces for one door standing on the ground; returns the notch it cuts
    in the bottom edge of its wall region, as outline points left to right."""
    mode = item_mode(kind, level)
    (ol, orr, ob, ot), (il, ir, ib, it) = item_rects(kind, s, z)
    fn = uv_item(fr, kind, ol, ob)
    depth = L.REVEAL_DEPTH[kind]
    rev = uv_patch("reveal")
    notch = [(ol, ob), (ol, ot), (orr, ot), (orr, ob)]
    if mode == "flush":
        B.face([fr.P(ol, ob), fr.P(orr, ob), fr.P(orr, ot), fr.P(ol, ot)], fn)
        return notch
    if mode == "cut":
        recess(B, fr, (ol, orr, ob, ot), depth, fn, rev, floor=False)
        return notch
    o = [(ol, ob), (orr, ob), (orr, ot), (ol, ot)]
    i = [(il, ib), (ir, ib), (ir, it), (il, it)]
    for k in range(4):          # the bottom quad has no area and is skipped
        B.face([fr.P(*o[k]), fr.P(*o[(k + 1) % 4]),
                fr.P(*i[(k + 1) % 4]), fr.P(*i[k])], fn)
    recess(B, fr, (il, ir, ib, it), depth, fn, rev, floor=False)
    return notch


def build_wall(B, spec, level):
    """One wall face of the ring. Every wall carries vertices at z = 0,
    Z_FOOT and its top at both ends, so walls meeting at a corner meet on
    exactly the same vertices."""
    fr = Frame(spec["p0"], spec["p1"])
    Lw, kind = fr.L, spec["kind"]

    def column(a, b):
        return [(a, 0.0), (b, 0.0), (b, Z_FOOT), (b, fr.top(b)), (a, fr.top(a)),
                (a, Z_FOOT)]

    if kind == "end":
        B.face([fr.P(*p) for p in column(0.0, Lw)],
               uv_strip(L.POST, lambda co: fr.s_of(co)))
        return
    if kind == "side":
        fill_region(B, fr, column(0.0, Lw), uv_side)
        return
    band_y0 = L.INT_Y0 if kind == "back" else L.S1_Y0
    band = uv_band(fr, band_y0, spec.get("u_off", 0.0))
    if kind == "back":
        fill_region(B, fr, column(0.0, Lw), band)
        return

    # outer wall: a white corner board at each end, the footing under it
    # sampling the band, then the boarded region between, notched by doors
    cw = L.CW
    for a, b in ((0.0, cw), (Lw - cw, Lw)):
        B.face([fr.P(a, 0.0), fr.P(b, 0.0), fr.P(b, Z_FOOT), fr.P(a, Z_FOOT)], band)
        B.face([fr.P(a, Z_FOOT), fr.P(b, Z_FOOT), fr.P(b, fr.top(b)), fr.P(a, fr.top(a))],
               uv_strip(L.CORNER, lambda co, a=a: fr.s_of(co) - a))
    s0, s1 = cw, Lw - cw
    outline = [(s0, 0.0)]
    for k, s, z in sorted(spec.get("items", []), key=lambda it: it[1]):
        outline += build_item(B, fr, k, s, z, level)
    outline += [(s1, 0.0), (s1, Z_FOOT), (s1, fr.top(s1)), (s0, fr.top(s0)), (s0, Z_FOOT)]
    fill_region(B, fr, outline, band)


def close_solid(B):
    """Cap the wall ring: an n-gon floor on the ground and a lid in the roof
    slab's plane. Both end up buried or underneath -- the lid inside the slab,
    the floor on the ground -- but the solid must be closed for the boolean.

    The rim is walked in edge-index order and capped by hand, as in
    rintamamiestalo_porch/build.py, so the caps start on the same vertex
    every run and the boolean triangulates the same way every time.
    """
    bm = B.bm
    bm.edges.index_update()
    order = [e for e in bm.edges if len(e.link_faces) == 1]
    rim = set(order)
    if any(sum(1 for e in v.link_edges if e in rim) != 2
           for e in order for v in e.verts):
        raise ValueError("the wall ring's rim branches: a T-junction somewhere")
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
    if len(loops) != 2:
        raise ValueError("expected a floor and a lid, got %d holes: the wall ring "
                         "has a T-junction somewhere" % len(loops))
    blank = uv_patch("blank")
    for loop in loops:
        B.set_uv(bm.faces.new(loop), blank)


def wall_ring(level):
    B = Builder()
    for spec in WALLS:
        build_wall(B, spec, level)
    close_solid(B)
    return B


# ================================================================== roof
def roof_slab():
    """The mono-pitch roof as one closed slab, ROOF_T thick vertically.

    Its underside is in three strips across x -- the two rake soffits and the
    middle -- so the rakes can take the plain soffit patch while the middle
    samples the ceiling band, which is the open bays' ceiling and the front
    and rear soffits. The front and rear edges carry the strips' breakpoints.
    Once unioned, the part of the underside over the closed bay and the walls
    is inside the wall ring and disappears.

    The top is two strips across y: the roof's lowest EAVE_STRIP_LEN up the
    slope, with the snow guard, maps onto the rear eave band, the rest onto
    the ROOF band. The rake edges carry that breakpoint.

    The breakpoints sit SOFFIT_IN inside the end walls' outer faces, not on
    them: an underside edge lying in a wall's plane left the exact boolean a
    sliver triangle of wall inside the slab at each end.
    """
    B = Builder()
    xr = HX + L.RAKE_OV
    xi = HX - SOFFIT_IN
    xs = [-xr, -xi, xi, xr]
    y0, y1 = L.Y_FRONT, L.Y_REAR
    t = L.ROOF_T

    def zu(y):
        return z_under(y)

    for i in range(3):
        a, b = xs[i], xs[i + 1]
        fn = uv_ceiling if i == 1 else uv_patch("soffit")
        B.face([(a, y0, zu(y0)), (a, y1, zu(y1)), (b, y1, zu(y1)), (b, y0, zu(y0))], fn)
    ys = y1 - L.EAVE_STRIP_LEN / L.SLOPE_F
    B.face([(-xr, y0, zu(y0) + t), (xr, y0, zu(y0) + t), (xr, ys, zu(ys) + t),
            (-xr, ys, zu(ys) + t)], uv_roof)
    B.face([(-xr, ys, zu(ys) + t), (xr, ys, zu(ys) + t), (xr, y1, zu(y1) + t),
            (-xr, y1, zu(y1) + t)], uv_eave)
    # front edge, walked +x along the bottom, back along the top
    B.face([(x, y0, zu(y0)) for x in xs] + [(xr, y0, zu(y0) + t), (-xr, y0, zu(y0) + t)],
           uv_fascia_x)
    B.face([(x, y1, zu(y1)) for x in reversed(xs)]
           + [(-xr, y1, zu(y1) + t), (xr, y1, zu(y1) + t)], uv_fascia_rear)
    for x, ya, yb in ((-xr, y1, y0), (xr, y0, y1)):
        B.face([(x, ya, zu(ya)), (x, yb, zu(yb)), (x, yb, zu(yb) + t),
                (x, ys, zu(ys) + t), (x, ya, zu(ya) + t)], uv_fascia_y)
    return B


def box(x0, x1, y0, y1, z0, z1, sides, top, bottom):
    """A closed box; *sides* is a uv function, or a callable taking the face's
    start and end plan points and returning one."""
    B = Builder()
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for k in range(4):
        (ax, ay), (bx, by) = ring[k], ring[(k + 1) % 4]
        B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)],
               sides((ax, ay), (bx, by)))
    B.face([(x, y, z1) for x, y in ring], top)
    B.face([(x, y, z0) for x, y in reversed(ring)], bottom)
    return B


def post():
    """The white post between the two open bays, on its footing pad, up into
    the roof slab."""
    def side(a, b):
        return uv_strip(L.POST, lambda co, a=a: math.hypot(co.x - a[0], co.y - a[1]))
    return box(POST_X - POST_HALF, POST_X + POST_HALF, POST_Y[0], POST_Y[1],
               0.0, POST_TOP, side, uv_patch("blank"), uv_patch("blank"))


def header():
    """The beam over the open span: white faces front, back and under."""
    return box(HEADER_X[0], HEADER_X[1], HEADER_Y[0], HEADER_Y[1], HEADER_Z[0],
               HEADER_Z[1], lambda a, b: uv_patch("header"), uv_patch("blank"),
               uv_patch("header"))


# ================================================================ assembly
def build_lod(level):
    base = to_object(wall_ring(level), "tmp_ring")
    parts = [to_object(roof_slab(), "tmp_roof")]
    if keeps_post(level):
        parts.append(to_object(post(), "tmp_post"))
    if keeps_header(level):
        parts.append(to_object(header(), "tmp_header"))
    parts += [to_object(B, name) for B, name in
              DP.solids(DOWNPIPES, *pipe_mode(level), L.PIPE_STRIP, L.ATLAS)]
    obj = union(base, parts)
    obj.name = "{}_LOD{}".format(ASSET, level)
    obj.data.name = obj.name + "_mesh"

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if level >= 2:
        # Coplanar boolean subdivisions, keeping UV/material seams and every
        # architectural edge; 0.001 rad tolerates float noise.
        bmesh.ops.dissolve_limit(
            bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
            delimit={'UV', 'MATERIAL'})
    # The end walls' top edges run along the slab's underside and carry the
    # underside's vertices, several in a straight line. Left as n-gons, the
    # exporter's triangulation joined three of them into triangles of no area
    # (hidden-surface candidates with no normal); triangulated here with
    # edge rotation, they make real triangles. The count does not change.
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY',
                          ngon_method='BEAUTY')
    flat = [f for f in bm.faces if f.calc_area() < 1e-8]
    if flat:
        raise ValueError("LOD%d keeps %d zero-area triangles, e.g. at %s"
                         % (level, len(flat), tuple(flat[0].calc_center_median())))
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def check_layout():
    """Assert the constraints that are invisible in the numbers and obvious
    once rendered: doors running into a corner board or under the roof, the
    massing outgrowing its atlas bands, the post off the bays' centre, and a
    solid that should be buried in the roof slab poking out of it."""
    problems = []
    gap = 0.05
    for spec in WALLS:
        fr = Frame(spec["p0"], spec["p1"])
        for kind, s, z in spec.get("items", []):
            (l, r, b, t), _ = item_rects(kind, s, z)
            if z != 0.0:
                problems.append("%s: %s must stand on the ground" % (spec["name"], kind))
            if l < L.CW + gap or r > fr.L - L.CW - gap:
                problems.append("%s: %s at s %.2f..%.2f runs into a corner board"
                                % (spec["name"], kind, l, r))
            for e in (l, r):
                vis = z_under(spec["p0"][1] + fr.t.y * e)
                if t > vis - 0.15:
                    problems.append("%s: %s top %.2f is under the roof (%.2f)"
                                    % (spec["name"], kind, t, vis))
    slope = (L.Y_REAR - L.Y_FRONT) * L.SLOPE_F
    if abs(slope - L.ROOF_SLOPE_LEN) > 1e-6:
        problems.append("roof slope is %.3f m, atlas assumes %.3f" % (slope, L.ROOF_SLOPE_LEN))
    if z_top(-HY) > L.Z_WALL_MAX:
        problems.append("front wall top %.2f is above the S1 band and side region"
                        % z_top(-HY))
    if z_top(Y_BACK) > L.INT_TOP:
        problems.append("back wall top %.2f is above the INT band" % z_top(Y_BACK))
    if abs((Y_BACK + HY) - L.BAY_DEPTH) > 1e-6:
        problems.append("bay depth %.2f differs from the atlas's %.2f"
                        % (Y_BACK + HY, L.BAY_DEPTH))
    if not 0.0 < SOFFIT_IN < T_WALL:
        problems.append("the rake soffit breakpoint is not buried in the end walls")
    if L.WALL_INTO >= L.ROOF_T:
        problems.append("the wall ring's lid is above the roof slab")
    # the header and the post must end inside the slab, and the header's ends
    # inside the end wall and the closed bay
    for what, top, ys in (("header", HEADER_Z[1], HEADER_Y),
                          ("post", POST_TOP, POST_Y)):
        for y in ys:
            if not z_under(y) + 0.03 < top < z_under(y) + L.ROOF_T - 0.03:
                problems.append("the %s's top is not inside the roof slab" % what)
    if not (-HX < HEADER_X[0] < X_BAYS and X_PART < HEADER_X[1] < HX):
        problems.append("the header's ends are not buried in the walls")
    if HEADER_Z[0] < max(item_rects(*WALLS[4]["items"][0])[0][3], 3.4):
        problems.append("the header comes down below the door pair's head")
    if abs(POST_X - (X_BAYS + X_PART) / 2.0) > 1e-6:
        problems.append("the post is off the open span's centre")
    if abs(L.POST_W - T_WALL) > 1e-6:
        problems.append("the end wall's face and the post strip differ in width")
    # downpipes: clear of the rear wall's corners (it has no openings), their
    # tops inside the slab, their shoes under the eave so no tier's extents
    # move; the snow guard inside its strip, and the strip on the roof and
    # on the atlas
    for pipe in DOWNPIPES:
        name = "the rear downpipe at s %.2f" % pipe.s
        problems += DP.problems(pipe, name, [])
        if not pipe.top(DP.OUT) < pipe.under(DP.OUT + DP.A) + L.ROOF_T - 0.03:
            problems.append("%s's top is not inside the roof slab" % name)
    if shoe_reach() > L.REAR_OV - 0.002:
        problems.append("the downpipes' shoes reach %.3f m off the wall, past the "
                        "%.2f m rear eave" % (shoe_reach(), L.REAR_OV))
    if not 0.0 < L.SNOW_S < L.EAVE_STRIP_LEN - 5.0 / L.EAVE_RPM:
        problems.append("the snow guard is not inside the eave strip")
    if L.Y_REAR - L.EAVE_STRIP_LEN / L.SLOPE_F <= L.Y_FRONT:
        problems.append("the eave strip is longer than the roof")
    if L.EAVE_ROOF_Y0 + L.EAVE_STRIP_LEN * L.EAVE_RPM > L.ATLAS:
        problems.append("the eave strip runs off the atlas")
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame.

    The footprint is the outer wall outline closed along the front by the
    post line: the open bays are under the roof and belong to the building,
    so it is the 10.5 x 6.0 m rectangle. One storey, its floor on the ground.
    Its area is the open bays' clear floor, from the end wall's and the
    partition's inner faces and from the front post line to the back wall
    (6.60 x 5.80 m), plus the closed bay inside walls 0.20 m thick like the
    open bays' own (3.30 x 5.60 m); the post's 0.04 m2 is not taken off.
    The open bays have no door leaf and are not doors.
    """
    def door(door_id, kind, spec, main=False):
        k, s, z = spec["items"][0]
        w, h = L.OPENINGS[k][:2]
        return model_facts.wall_door(door_id, kind, spec["p0"], spec["p1"], s, z,
                                     w, h, main)

    walls = {spec["name"]: spec for spec in WALLS}
    open_bays = (X_PART - X_BAYS) * (Y_BACK + HY)
    closed_bay = (HX - X_PART - 2 * T_WALL) * (2 * HY - 2 * T_WALL)
    return {
        "hero": False,
        "dwellings": 0,
        "footprint": [(-HX, -HY), (HX, -HY), (HX, HY), (-HX, HY)],
        "storeys": [(0.0, open_bays + closed_bay)],
        "doors": [door("workshop", "entrance", walls["east"], main=True),
                  door("machine", "vehicle", walls["front"])],
    }


# ================================================================ previews
def render_views(out_dir, level=0, res=(1400, 1000)):
    """The six working views CLAUDE.md asks for before export: four
    orthographic elevations, a plan from above, and a raised three-quarter
    aerial off the front corner. Working views only -- not committed."""
    preview_studio()
    _show_only(level)
    scn = bpy.context.scene
    saved = (scn.camera, scn.render.resolution_x, scn.render.resolution_y)
    scn.render.resolution_x, scn.render.resolution_y = res
    centre, radius = _bounds(bpy.data.objects["{}_LOD{}".format(ASSET, level)])
    cam = bpy.data.objects.get("_view_cam")
    if cam is None:
        cam = bpy.data.objects.new("_view_cam", bpy.data.cameras.new("_view_cam"))
        scn.collection.objects.link(cam)
    scn.camera = cam
    cam.data.clip_end = 1000.0
    views = {
        "front": ((0, -1, 0), (90, 0, 0)), "rear": ((0, 1, 0), (90, 0, 180)),
        "east": ((1, 0, 0), (90, 0, 90)), "west": ((-1, 0, 0), (90, 0, -90)),
        "top": ((0, 0, 1), (0, 0, 0)),
    }
    written = []
    for name, (d, rot) in views.items():
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = radius * 2.1
        cam.rotation_euler = Euler([math.radians(a) for a in rot], 'XYZ')
        cam.location = centre + Vector(d) * 60.0
        scn.render.filepath = os.path.join(out_dir, "L%d_%s.png" % (level, name))
        bpy.ops.render.render(write_still=True)
        written.append(scn.render.filepath)
    # raised three-quarter: 45 degrees up, off the front-right corner
    cam.data.type = 'PERSP'
    cam.data.lens = 35.0
    d = Vector((1.0, -1.0, math.sqrt(2.0))).normalized()
    cam.location = centre + d * radius * 3.0
    cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scn.render.filepath = os.path.join(out_dir, "L%d_aerial.png" % level)
    bpy.ops.render.render(write_still=True)
    written.append(scn.render.filepath)
    scn.camera, scn.render.resolution_x, scn.render.resolution_y = saved
    return written


if __name__ == "__main__":
    BUILD.main(build_all, facts)
