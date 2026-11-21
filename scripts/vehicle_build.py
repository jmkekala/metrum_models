# SPDX-License-Identifier: GPL-3.0-or-later

"""Everything a vehicle's build.py does that does not describe the vehicle.

The vehicle half of scripts/asset_build.py (CLAUDE.md, Vehicles): pieces
tagged with surface and paint ids as their faces are made, wheels as their
own objects with the origin at the wheel centre, the ids written as the
FLOAT_COLOR corner attribute vehicle_ids.ID_ATTRIBUTE, one joined mesh and
one material per tier, the checks the ids and the frame must pass before
export, the measured facts (wheels, lamp lenses, glass areas, body block)
for the version 2 sidecar, previews painted through the B channel, and
wheels turned for review.

    import vehicle_build as VB
    V = VB.VehicleAsset(ASSET, HERE, [("plain", True)], "plain", "car")

    def build_lod(level):
        body = VB.Builder(L.ATLAS)
        body.face(cos, uvfn, surface=7)          # a low-beam lens
        body.face(cos, uvfn, paint=True)         # a painted panel
        ...
        pieces = [VB.Piece("body", body), VB.Piece("mirror", mirror)]
        if level <= 1:                           # wheels keep their parts
            pieces += [VB.Piece("wheel", VB.wheel_solid(...), part=1,
                                centre=(x, y, r), steer=True), ...]
        else:                                    # merged into the body
            pieces.append(VB.Piece("body", merged_wheels))
        return pieces

    def facts():
        return {"cargo": None}                   # the rest is measured

    if __name__ == "__main__":
        V.main(lambda: V.build_all(check_layout, build_lod), facts)

Runs inside Blender only.
"""

import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Vector

import asset_build
import model_facts
import vehicle_ids as vi
from variant_previews import render_sheet
from window_emission import set_state

SURFACE = "metrum_surface"       # int face layers a Builder writes
PAINT = "metrum_paint"
ROLES = ("body", "mirror", "wheel")
TOL = 1e-3
# Lamps lit in a preview's night row (variants.png): what the game shows on
# a car driving at night. The review sheet lights every group in turn.
NIGHT_LAMPS = (1, 3, 7, 9, 15)
PREVIEW_TINT = (1.0, 1.0, 1.0)   # lamps carry their own colour


# ================================================================ authoring
class Builder:
    """A closed solid (or several) as a bmesh, with UVs in atlas pixels and
    the surface and paint ids set face by face.

        B = Builder(512)
        B.face([(x, y, z), ...], uvfn, surface=0, paint=False)

    *uvfn(co)* returns atlas pixels (u, v) for a corner; *surface* is 0, a
    lamp id (1..15) or a glass id (32..47); *paint* marks a painted panel.
    Vertices are shared by position (rounded to 1e-6 m)."""

    def __init__(self, atlas_size):
        self.size = float(atlas_size)
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.surf = self.bm.faces.layers.int.new(SURFACE)
        self.paint = self.bm.faces.layers.int.new(PAINT)
        self.cache = {}

    def v(self, co):
        key = tuple(round(c, 6) for c in co)
        vert = self.cache.get(key)
        if vert is None:
            vert = self.bm.verts.new(co)
            self.cache[key] = vert
        return vert

    def face(self, cos, uvfn, surface=0, paint=False, smooth=False):
        vi.encode(0, surface, paint)            # refuses a painted lamp or glass
        f = self.bm.faces.new([self.v(co) for co in cos])
        for loop, co in zip(f.loops, cos):
            u, w = uvfn(co)
            loop[self.uv].uv = (u / self.size, w / self.size)
        f[self.surf] = int(surface)
        f[self.paint] = int(bool(paint))
        f.smooth = smooth
        return f


def patch_uv(rect, inset=1.5):
    """A uvfn that maps a face's corners onto atlas rectangle *rect* (x, y,
    w, h px), inset by *inset* px, by the face's own planar extent. Bind it
    per face with patch_face()."""
    x, y, w, h = rect
    return (x + inset, y + inset, w - 2 * inset, h - 2 * inset)


def patch_face(B, cos, rect, surface=0, paint=False, inset=1.5, smooth=False):
    """Add face *cos* to builder *B*, its corners spread over atlas *rect*
    by the face's own planar projection: for a crude or flat-shaded region
    whose texels are uniform (a lens, a pane, a plain panel)."""
    pts = np.array(cos, float)
    n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
    for k in range(2, len(pts) - 1):
        n += np.cross(pts[k] - pts[0], pts[k + 1] - pts[0])
    ax = int(np.argmax(np.abs(n)))
    keep = [i for i in range(3) if i != ax]
    q = pts[:, keep]
    lo, hi = q.min(axis=0), q.max(axis=0)
    span = np.maximum(hi - lo, 1e-9)
    x0, y0, w, h = patch_uv(rect, inset)
    uvs = {tuple(c): (x0 + w * (p[0] - lo[0]) / span[0], y0 + h * (p[1] - lo[1]) / span[1])
           for c, p in zip(map(tuple, cos), q)}
    return B.face(cos, lambda co: uvs[tuple(co)], surface, paint, smooth)


def wheel_solid(size, radius, width, sides, tread_rect, face_rect, outward=1,
                rim=0.62, dish=0.03, smooth=True):
    """One wheel as a closed solid round its own centre, axis along X: a
    tyre of *sides* tread quads, one corner at the very bottom so the tyre
    touches the ground at centre z - radius exactly; an outer sidewall ring
    down to the rim and the rim face sunk *dish* metres; a flat inner face.
    rim=None makes a plain prism (two flat faces), for a tier whose wheels
    merge into the body. *outward* is +1 for a wheel whose outer face looks
    toward +X (the driver's left), -1 for the right. *tread_rect* and
    *face_rect* are atlas rectangles (x, y, w, h px): U runs round the
    tread, both faces map onto the square. Every face plain (surface 0,
    paint 0). Returns a Builder in the wheel's own frame: give it to
    Piece("wheel", ..., centre=...)."""
    B = Builder(size)
    hw = width / 2.0
    xo, xi = hw * outward, -hw * outward
    ang = [-math.pi / 2.0 + 2.0 * math.pi * k / sides for k in range(sides)]
    ring = [(math.cos(a), math.sin(a)) for a in ang]
    tx, ty, tw, th = patch_uv(tread_rect)
    fx, fy, fw, fh = patch_uv(face_rect)

    def fuv(co):
        return (fx + fw * (0.5 + co[1] / (2 * radius)), fy + fh * (0.5 + co[2] / (2 * radius)))

    def add(cos, uvfn):
        B.face(cos if outward > 0 else cos[::-1], uvfn, smooth=False)

    for k in range(sides):
        (c0, s0), (c1, s1) = ring[k], ring[(k + 1) % sides]
        u0, u1 = tx + tw * k / sides, tx + tw * (k + 1) / sides
        quad = [(xi, radius * c0, radius * s0), (xo, radius * c0, radius * s0),
                (xo, radius * c1, radius * s1), (xi, radius * c1, radius * s1)]
        uvs = dict(zip(quad, [(u0, ty), (u0, ty + th), (u1, ty + th), (u1, ty)]))
        q = quad if outward > 0 else quad[::-1]
        B.face(q, lambda co, uvs=uvs: uvs[co], smooth=smooth)
        if rim is not None:
            rr, xr = radius * rim, xo - dish * outward
            add([(xo, radius * c0, radius * s0), (xo, rr * c0, rr * s0),
                 (xo, rr * c1, rr * s1), (xo, radius * c1, radius * s1)], fuv)
            add([(xo, rr * c0, rr * s0), (xr, rr * c0, rr * s0),
                 (xr, rr * c1, rr * s1), (xo, rr * c1, rr * s1)], fuv)
    if rim is not None:
        add([(xo - dish * outward, radius * rim * c, radius * rim * s) for c, s in ring], fuv)
    else:
        add([(xo, radius * c, radius * s) for c, s in ring], fuv)
    add([(xi, radius * c, radius * s) for c, s in reversed(ring)], fuv)
    return B


def conform(B, tol=1e-6):
    """Remove T-junctions from builder *B*: every vertex lying inside
    another face's edge is inserted into that face (UVs interpolated along
    the edge), so faces cut into cells (a lens or a pane inside a panel)
    close against their neighbours. Run before the piece is used.

    A replaced face's old edges that no face uses any more are removed, and
    so is any vertex that loses its last edge, so the piece stays closed for
    Piece's checks; edges and vertices that were loose before are kept."""
    bm = B.bm
    bm.verts.ensure_lookup_table()
    cos = np.array([v.co[:] for v in bm.verts])
    dropped = set()                      # edges of the faces replaced
    changed = True
    while changed:
        changed = False
        for f in list(bm.faces):
            loops = list(f.loops)
            new, uvs = [], []
            for i, lp in enumerate(loops):
                a, b = lp.vert, loops[(i + 1) % len(loops)].vert
                new.append(a)
                uvs.append(Vector(lp[B.uv].uv))
                pa, pb = np.array(a.co[:]), np.array(b.co[:])
                d = pb - pa
                ll = float(d @ d)
                if ll < tol * tol:
                    continue
                t = (cos - pa) @ d / ll
                off = cos - pa - np.outer(t, d)
                hit = np.flatnonzero((t > 1e-6) & (t < 1 - 1e-6)
                                     & (np.einsum("ij,ij->i", off, off) < tol * tol))
                if len(hit):
                    ua, ub = Vector(lp[B.uv].uv), Vector(loops[(i + 1) % len(loops)][B.uv].uv)
                    for j in sorted(hit, key=lambda j: t[j]):
                        new.append(bm.verts[int(j)])
                        uvs.append(ua.lerp(ub, float(t[j])))
            if len(new) == len(loops):
                continue
            s, p, sm = f[B.surf], f[B.paint], f.smooth
            dropped.update(f.edges)
            bm.faces.remove(f)
            g = bm.faces.new(new)
            for lp, uv in zip(g.loops, uvs):
                lp[B.uv].uv = uv
            g[B.surf], g[B.paint], g.smooth = s, p, sm
            changed = True
    loose = [e for e in dropped if e.is_valid and not e.link_faces]
    ends = {v for e in loose for v in e.verts}
    for e in loose:
        bm.edges.remove(e)
    lone = [v for v in ends if v.is_valid and not v.link_edges]
    if lone:
        gone = set(lone)
        B.cache = {k: v for k, v in B.cache.items() if v not in gone}
        for v in lone:
            bm.verts.remove(v)
    return B


class Piece:
    """One piece of a tier: *role* body, mirror or wheel; *part* the wheel's
    part id (1.., in sidecar order: the front axle first, left before
    right); a wheel's *centre* (build frame) is its object's origin and its
    builder is in that local frame; *steer* and *twin* as the sidecar's.
    *src* is a Builder, a bmesh or an unlinked mesh object."""

    def __init__(self, role, src, part=0, centre=None, steer=False, twin=False):
        if role not in ROLES:
            raise ValueError("role %r is not one of %s" % (role, ROLES))
        if (role == "wheel") != (part > 0):
            raise ValueError("a wheel piece has a part id 1..8, and only a wheel")
        if role == "wheel" and centre is None:
            raise ValueError("a wheel piece needs its centre")
        self.role, self.src, self.part = role, src, int(part)
        self.centre = tuple(centre) if centre is not None else (0.0, 0.0, 0.0)
        self.steer, self.twin = bool(steer), bool(twin)


# ================================================================ ids
def write_ids(me, part):
    """Write the id attribute on *me*'s corners from its SURFACE and PAINT
    face attributes (absent: 0), every corner of a polygon the same, part
    *part* throughout; then drop the face attributes."""
    n = len(me.polygons)
    surf = np.zeros(n, np.int32)
    paint = np.zeros(n, np.int32)
    for name, arr in ((SURFACE, surf), (PAINT, paint)):
        a = me.attributes.get(name)
        if a is not None:
            a.data.foreach_get("value", arr)
    for i in range(n):
        vi.encode(part, int(surf[i]), int(paint[i]))  # refuses a bad combination
    per_poly = np.stack([np.full(n, part / 255.0), surf / 255.0,
                         (paint > 0).astype(np.float64), np.ones(n)], axis=1)
    totals = np.zeros(n, np.int32)
    me.polygons.foreach_get("loop_total", totals)
    corner = np.repeat(per_poly, totals, axis=0).astype(np.float32)
    old = me.color_attributes.get(vi.ID_ATTRIBUTE)
    if old is not None:
        me.color_attributes.remove(old)
    attr = me.color_attributes.new(vi.ID_ATTRIBUTE, 'FLOAT_COLOR', 'CORNER')
    attr.data.foreach_set("color", corner.ravel())
    me.color_attributes.active_color = attr
    me.color_attributes.render_color_index = me.color_attributes.find(vi.ID_ATTRIBUTE)
    for name in (SURFACE, PAINT):
        a = me.attributes.get(name)
        if a is not None:
            me.attributes.remove(a)


def read_ids(me):
    """Per-polygon (part, surface, paint) and the per-corner float array."""
    attr = me.color_attributes.get(vi.ID_ATTRIBUTE)
    if attr is None or attr.domain != 'CORNER' or attr.data_type != 'FLOAT_COLOR':
        raise ValueError("%s has no FLOAT_COLOR corner attribute %r"
                         % (me.name, vi.ID_ATTRIBUTE))
    c = np.zeros(len(me.loops) * 4, np.float32)
    attr.data.foreach_get("color", c)
    c = c.reshape(-1, 4).astype(np.float64)
    starts = np.zeros(len(me.polygons), np.int32)
    me.polygons.foreach_get("loop_start", starts)
    first = c[starts]
    return (np.round(first[:, 0] * 255).astype(int), np.round(first[:, 1] * 255).astype(int),
            np.round(first[:, 2]).astype(int), c)


def ids_problems(me):
    """What the export would carry wrong: A = 1 everywhere, one R and one G
    (and B) per polygon, whole ids from the allowed sets, R = 0 and B = 0
    where G is not 0, B 0 or 1. A join with an object that lacked the
    attribute shows as A = 0 there."""
    part, surf, paint, c = read_ids(me)
    problems = []
    if np.any(np.abs(c[:, 3] - 1.0) > 1e-6):
        problems.append("%d corners have A != 1 (a piece without the id attribute "
                        "joined in?)" % int(np.sum(np.abs(c[:, 3] - 1.0) > 1e-6)))
    for ch in (0, 1):
        s = c[:, ch] * 255.0
        if np.any(np.abs(s - np.round(s)) > 1e-3):
            problems.append("channel %s is not whole ids" % "RG"[ch])
    if np.any((np.abs(c[:, 2]) > 1e-6) & (np.abs(c[:, 2] - 1.0) > 1e-6)):
        problems.append("B is not 0 or 1 everywhere")
    totals = np.zeros(len(me.polygons), np.int32)
    me.polygons.foreach_get("loop_total", totals)
    poly_of = np.repeat(np.arange(len(totals)), totals)
    first = c[np.repeat(np.cumsum(totals) - totals, totals)]
    mixed = np.unique(poly_of[np.any(np.abs(c[:, :3] - first[:, :3]) > 1e-6, axis=1)])
    if len(mixed):
        problems.append("%d polygons have corners with different ids" % len(mixed))
    bad_g = sorted(set(surf.tolist()) - {0} - set(vi.LAMP_IDS) - set(vi.GLASS_IDS))
    if bad_g:
        problems.append("surface ids outside 0, 1..15, 32..47: %s" % bad_g)
    if np.any((surf != 0) & ((part != 0) | (paint != 0))):
        problems.append("lamp or glass faces with a part or paint")
    if part.max(initial=0) > vi.MAX_WHEELS:
        problems.append("part ids over %d" % vi.MAX_WHEELS)
    return problems


# ================================================================ nodes
def id_sockets(nt, attribute):
    """(R*255, G*255, B) sockets from a geometry attribute in a material."""
    a = nt.nodes.new("ShaderNodeAttribute")
    a.attribute_type = 'GEOMETRY'
    a.attribute_name = attribute
    a.location = (-900, -900)
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    sep.location = (-700, -900)
    nt.links.new(a.outputs["Color"], sep.inputs["Color"])
    out = []
    for ch in ("Red", "Green"):
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = 'MULTIPLY'
        m.inputs[1].default_value = 255.0
        nt.links.new(sep.outputs[ch], m.inputs[0])
        out.append(m.outputs[0])
    return out[0], out[1], sep.outputs["Blue"]


def gate(nt, g255, ids):
    """A 0/1 socket: 1 where the surface id is one of *ids*."""
    total = None
    for k in sorted(set(ids)):
        cmp_ = nt.nodes.new("ShaderNodeMath")
        cmp_.operation = 'COMPARE'
        cmp_.inputs[1].default_value = float(k)
        cmp_.inputs[2].default_value = 0.5
        nt.links.new(g255, cmp_.inputs[0])
        if total is None:
            total = cmp_.outputs[0]
        else:
            add = nt.nodes.new("ShaderNodeMath")
            add.operation = 'ADD'
            nt.links.new(total, add.inputs[0])
            nt.links.new(cmp_.outputs[0], add.inputs[1])
            total = add.outputs[0]
    if total is None:
        v = nt.nodes.new("ShaderNodeValue")
        v.outputs[0].default_value = 0.0
        total = v.outputs[0]
    return total


def paint_base(nt, albedo, b, rgb):
    """albedo multiplied by *rgb* where B = 1: the game's paint."""
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = 'RGBA'
    mul.blend_type = 'MULTIPLY'
    mul.inputs["Factor"].default_value = 1.0
    nt.links.new(albedo, mul.inputs[6])
    mul.inputs[7].default_value = (*rgb, 1.0)
    pick = nt.nodes.new("ShaderNodeMix")
    pick.data_type = 'RGBA'
    nt.links.new(b, pick.inputs["Factor"])
    nt.links.new(albedo, pick.inputs[6])
    nt.links.new(mul.outputs[2], pick.inputs[7])
    return pick.outputs[2]


def gate_emission(nt, colour_socket_input, g255, ids):
    """Insert a multiply by gate(ids) in front of the socket feeding
    *colour_socket_input* (the BSDF's Emission Color)."""
    src = colour_socket_input.links[0].from_socket
    m = nt.nodes.new("ShaderNodeMix")
    m.data_type = 'RGBA'
    m.blend_type = 'MULTIPLY'
    m.inputs["Factor"].default_value = 1.0
    nt.links.new(src, m.inputs[6])
    g = gate(nt, g255, ids)
    comb = nt.nodes.new("ShaderNodeCombineColor")
    for k in range(3):
        nt.links.new(g, comb.inputs[k])
    nt.links.new(comb.outputs[0], m.inputs[7])
    nt.links.new(m.outputs[2], colour_socket_input)


# ================================================================ geometry
def to_object(name, src):
    """An unlinked mesh object named *name* from *src*: a Builder or a
    bmesh (face normals recalculated outward first), or an object, which is
    returned as it is. For a build.py that works on a piece as an object
    (an exact boolean, edge creases) before handing it to Piece."""
    if isinstance(src, Builder):
        src = src.bm
    if isinstance(src, bmesh.types.BMesh):
        bmesh.ops.recalc_face_normals(src, faces=src.faces[:])
        me = bpy.data.meshes.new(name)
        src.to_mesh(me)
        return bpy.data.objects.new(name, me)
    return src


_object = to_object     # the earlier private name, which committed build.py files call


def lens_texel_colour(me, polys, emit):
    """The lit colour (vehicle_ids.lit_colour()) of the emission texels
    *emit* (8-bit sRGB, rows top-down) that polygons *polys* of mesh *me*
    sample through its active UV map; None where they are not white, amber
    or red."""
    uvl = me.uv_layers.active.data
    uv, tris = [], []
    for p in polys:
        loops = list(me.polygons[p].loop_indices)
        base = len(uv)
        uv += [(uvl[i].uv[0], 1.0 - uvl[i].uv[1]) for i in loops]
        tris += [(base, base + k, base + k + 1) for k in range(1, len(loops) - 1)]
    size = emit.shape[0]
    sets = vi.texel_sets(np.array(uv), np.array(tris), size)
    word, _share = vi.lit_colour(emit.reshape(-1, 3)[np.unique(np.concatenate(sets))])
    return word if word in vi.LENS_COLOURS else None


def _closed(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bad = [e for e in bm.edges if len(e.link_faces) != 2]
    flat = [f for f in bm.faces if f.calc_area() < 1e-9]
    bm.free()
    return len(bad), len(flat)


def _triangulate(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.to_mesh(obj.data)
    bm.free()


def _verts(obj):
    a = np.zeros(len(obj.data.vertices) * 3)
    obj.data.vertices.foreach_get("co", a)
    a = a.reshape(-1, 3)
    m = np.array(obj.matrix_world)
    return a @ m[:3, :3].T + m[:3, 3]


def _components(me, polys):
    """Connected components (by shared vertices) of polygon indices *polys*."""
    parent = {p: p for p in polys}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    by_vert = {}
    for p in polys:
        for v in me.polygons[p].vertices:
            by_vert.setdefault(v, []).append(p)
    for ps in by_vert.values():
        for q in ps[1:]:
            ra, rb = find(ps[0]), find(q)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    groups = {}
    for p in polys:
        groups.setdefault(find(p), []).append(p)
    return sorted(groups.values())


# ================================================================ asset
class VehicleAsset(asset_build.Asset):
    """One vehicle: its name, folder, body class and variants.

    *variants* is [(name, paint), ...]: paint False for a livery that paints
    its panels in full colour (CLAUDE.md, Vehicles). Authored in the
    exported frame's origin: the build frame's origin is on the ground at
    the centre of the body's plan box, mirrors excluded, and build_all()
    refuses a tier that is not. *preview_paint* is the linear colour
    preview.png and variants.png multiply the painted panels of a paint-true
    variant by (None: white, the albedo as shipped); a paint-false livery is
    always shown white, as the consumer paints it.
    """

    id_attribute = vi.ID_ATTRIBUTE

    def __init__(self, name, here, variants, default_variant, body_class,
                 preview_paint=None):
        if body_class not in vi.CLASSES:
            raise ValueError("body class %r is not one of %s" % (body_class, list(vi.CLASSES)))
        self.paint_flags = [(v, bool(p)) for v, p in variants]
        super().__init__(name, here, [v for v, _ in self.paint_flags], default_variant,
                         tint=PREVIEW_TINT, levels=vi.LEVELS, night_lit=True,
                         pivot=(0.0, 0.0, 0.0))
        self.body_class = body_class
        self.spec = vi.CLASSES[body_class]
        self.preview_paint = preview_paint
        self.measured = None            # set by build_all() from LOD0
        self.wheels = []                # wheel_part() records, LOD0

    # ---------------------------------------------------------------- tiers
    def parts_collection(self):
        name = self.name + "_parts"
        col = bpy.data.collections.get(name)
        if col is None:
            col = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(col)
        col.hide_render = True
        return col

    def build_all(self, check, build_lod):
        """Run the layout check, build every tier from its pieces, write the
        ids, join each tier into one mesh with one material, check the ids
        and the frame, and measure LOD0's facts. Returns per-tier triangle
        counts, the class ceilings and the measured body block.

        In the saved scene each tier's pieces stay in <name>_parts, a wheel
        as its own object with its origin at the wheel centre; the tier
        <name>_LOD<n> is their join, which is what exports."""
        problems = check()
        if problems:
            raise ValueError("layout check failed:\n  " + "\n  ".join(problems))
        scn = bpy.context.scene
        parts_col = self.parts_collection()
        for o in list(parts_col.objects):
            m = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if m.users == 0:
                bpy.data.meshes.remove(m)
        for level in self.levels:
            old = bpy.data.objects.get("{}_LOD{}".format(self.name, level))
            if old:
                m = old.data
                bpy.data.objects.remove(old, do_unlink=True)
                bpy.data.meshes.remove(m)
        col = bpy.data.collections.get(self.name)
        if col is None:
            col = bpy.data.collections.new(self.name)
            scn.collection.children.link(col)
        mat = self.material()
        stats, ref = {}, None
        for level in self.levels:
            pieces = build_lod(level)
            obj, info = self._tier(level, pieces, parts_col, mat)
            col.objects.link(obj)
            box = info["box"]
            if level == 0:
                ref = box
                cx, cy = (box[0][0] + box[1][0]) / 2.0, (box[0][1] + box[1][1]) / 2.0
                if abs(cx) > TOL or abs(cy) > TOL or abs(info["zmin"]) > TOL:
                    raise ValueError(
                        "LOD0's origin is not on the ground at the centre of the body's "
                        "plan box: centre (%.4f, %.4f), lowest z %.4f"
                        % (cx, cy, info["zmin"]))
                self.measured = info
                size = (box[1][1] - box[0][1], box[1][0] - box[0][0], box[1][2])
                for what, v, lim in zip(("length", "width", "height"), size,
                                        self.spec["box"]):
                    if v > lim + 1e-4:
                        print("WARNING: %s is %.4f m %s, over the %s box's %.2f; the "
                              "validator fails it" % (self.name, v, what, self.body_class, lim))
            elif abs(info["zmin"]) > TOL:
                raise ValueError("LOD%d's lowest point is z %.4f: every tier stands on the "
                                 "ground" % (level, info["zmin"]))
            elif any(abs(a - b) > TOL for i in (0, 1) for a, b in zip(box[i][:2], ref[i][:2])):
                raise ValueError("LOD%d's plan box %s is not LOD0's %s"
                                 % (level, [list(map(lambda c: round(c, 4), b[:2])) for b in box],
                                    [list(map(lambda c: round(c, 4), b[:2])) for b in ref]))
            obj.data.calc_loop_triangles()
            n = len(obj.data.loop_triangles)
            stats["LOD%d" % level] = n
            ceiling = self.spec["ceilings"][level]
            if n > ceiling:
                print("WARNING: %s LOD%d has %d triangles, over the %s ceiling %d"
                      % (self.name, level, n, self.body_class, ceiling))
            obj.hide_set(level != 0)
            obj.hide_render = (level != 0)
        self.pivot = (0.0, 0.0, 0.0)
        stats["ceilings"] = self.spec["ceilings"]
        b = self.body_block()
        stats["body"] = {k: round(v, 4) if isinstance(v, float) else v for k, v in b.items()}
        return stats

    def _tier(self, level, pieces, parts_col, mat):
        """The pieces of one tier as objects in *parts_col*, ids written,
        and their join as the unlinked tier object."""
        if not pieces:
            raise ValueError("LOD%d has no pieces" % level)
        parts = [p.part for p in pieces if p.role == "wheel"]
        if len(parts) != len(set(parts)):
            raise ValueError("LOD%d repeats wheel parts %s" % (level, parts))
        if parts and sorted(parts) != list(range(1, len(parts) + 1)):
            raise ValueError("LOD%d's wheel parts %s are not 1..n" % (level, sorted(parts)))
        if level >= 2 and parts:
            raise ValueError("LOD%d keeps wheel parts; from LOD2 the wheels are body" % level)
        objs, info = [], {"wheels": []}
        lo, hi, zmin, body_z = [np.inf] * 3, [-np.inf] * 3, np.inf, np.inf
        mirror_x = 0.0
        for k, p in enumerate(pieces):
            name = "%s_LOD%d_%s%s" % (self.name, level, p.role,
                                      p.part if p.role == "wheel" else k)
            obj = to_object(name, p.src)
            obj.name = obj.data.name = name
            open_, flat = _closed(obj)
            if open_ or flat:
                raise ValueError("%s: %d edges not on two faces, %d zero-area faces"
                                 % (name, open_, flat))
            _triangulate(obj)
            if _closed(obj)[1]:
                raise ValueError("%s triangulates into zero-area faces" % name)
            obj.location = Vector(p.centre)
            parts_col.objects.link(obj)
            bpy.context.view_layer.update()
            write_ids(obj.data, p.part)
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            v = _verts(obj)
            zmin = min(zmin, float(v[:, 2].min()))
            if p.role == "mirror":
                mirror_x = max(mirror_x, float(np.abs(v[:, 0]).max()))
            else:
                lo = np.minimum(lo, v.min(axis=0))
                hi = np.maximum(hi, v.max(axis=0))
            if p.role == "body":
                body_z = min(body_z, float(v[:, 2].min()))
            if p.role == "wheel":
                local = v - np.asarray(p.centre)
                info["wheels"].append(model_facts.wheel_part(
                    p.part, p.centre, float(np.hypot(local[:, 1], local[:, 2]).max()),
                    float(local[:, 0].max() - local[:, 0].min()), p.steer, p.twin))
            objs.append(obj)
            obj.hide_set(True)
        # the tier: a join of copies, so the parts keep their own objects
        copies = []
        for o in objs:
            c = o.copy()
            c.data = o.data.copy()
            bpy.context.scene.collection.objects.link(c)
            copies.append(c)
        target = copies[0]
        for c in copies:
            c.hide_set(False)
            c.select_set(True)
        with bpy.context.temp_override(active_object=target, object=target,
                                       selected_objects=copies,
                                       selected_editable_objects=copies):
            bpy.ops.object.join()
        bpy.context.view_layer.update()
        me = target.data
        # the join keeps the first object's transform; bake it so the tier
        # is in the build frame with an identity transform
        me.transform(target.matrix_world)
        target.matrix_world.identity()
        bpy.context.scene.collection.objects.unlink(target)
        target.name = "{}_LOD{}".format(self.name, level)
        me.name = target.name + "_mesh"
        problems = ids_problems(me)
        if problems:
            raise ValueError("LOD%d ids:\n  %s" % (level, "\n  ".join(problems)))
        if len(me.color_attributes) != 1:
            raise ValueError("LOD%d has colour attributes %s; only %r may export"
                             % (level, [a.name for a in me.color_attributes], vi.ID_ATTRIBUTE))
        me.materials.clear()
        me.materials.append(mat)
        info.update(box=(tuple(map(float, lo)), tuple(map(float, hi))), zmin=zmin,
                    body_zmin=body_z,
                    width_mirrors=2.0 * max(mirror_x, abs(lo[0]), abs(hi[0])))
        return target, info

    # ---------------------------------------------------------------- facts
    def body_block(self):
        m = self.measured
        return {"lo": m["box"][0], "hi": m["box"][1], "width_mirrors": m["width_mirrors"],
                "ground_clearance": m["body_zmin"]}

    def lamp_lenses(self, level=0):
        """One lamp_lens() per connected group of same-id lamp faces of the
        tier: a lens. A lens of a group with one colour takes it; a marker
        (or beacon, or sign) lens takes the lit colour of the emission
        texels its faces sample (vehicle_ids.lit_colour()), so the texture
        generator's lens colours are the record. Where that is not white,
        amber or red, compose_vehicle() refuses the lens: the build.py then
        states the lenses itself, facts()["lamps"], with
        model_facts.lamp_lens(..., colour=)."""
        me = self.lod(level).data
        _part, surf, _paint, _c = read_ids(me)
        emit, out = None, []
        for lamp in sorted(set(surf.tolist()) & set(vi.LAMP_IDS)):
            for comp in _components(me, [int(i) for i in np.flatnonzero(surf == lamp)]):
                pts, n = [], Vector()
                for p in comp:
                    poly = me.polygons[p]
                    pts += [tuple(me.vertices[v].co) for v in poly.vertices]
                    n += poly.normal * poly.area
                colour = None
                if len(vi.lens_colours(lamp)) > 1:
                    if emit is None:
                        emit = self.emission_texels()
                    colour = lens_texel_colour(me, comp, emit)
                out.append(model_facts.lamp_lens(lamp, pts, tuple(n.normalized()),
                                                 colour=colour))
        return out

    def emission_texels(self):
        """export/<name>_emission.png as 8-bit sRGB (size, size, 3), rows
        top-down as the PNG stores them."""
        path = os.path.join(self.export_dir, self.name + "_emission.png")
        im = bpy.data.images.load(path, check_existing=False)
        try:
            w, h = im.size
            px = np.zeros(w * h * 4, np.float32)
            im.pixels.foreach_get(px)
        finally:
            bpy.data.images.remove(im)
        return np.round(np.flipud(px.reshape(h, w, 4)[:, :, :3]) * 255.0).astype(np.uint8)

    def glass_areas(self, level=0):
        me = self.lod(level).data
        _part, surf, _paint, _c = read_ids(me)
        areas = np.zeros(len(me.polygons))
        me.polygons.foreach_get("area", areas)
        return [model_facts.glass_group(g, float(areas[surf == g].sum()))
                for g in sorted(set(surf.tolist()) & set(vi.GLASS_IDS))]

    def vehicle_facts(self, facts):
        """The build.py's facts() completed with what LOD0 measures.

        The build.py states "cargo" (model_facts.cargo_box(), or None for a
        car) and may override "lamps", "glass", "coupling" or "interior";
        the body block, the wheels, the lenses and the glass areas are
        measured here."""
        user = dict(facts() if callable(facts) else (facts or {}))
        unknown = set(user) - {"cargo", "coupling", "interior", "lamps", "glass"}
        if unknown:
            raise ValueError("facts() has unknown keys: %s" % sorted(unknown))
        return {"class": self.body_class, "body": self.body_block(),
                "wheels": list(self.measured["wheels"]),
                "lamps": user.get("lamps") or self.lamp_lenses(),
                "glass": user.get("glass") or self.glass_areas(),
                "cargo": user.get("cargo"), "coupling": user.get("coupling"),
                "interior": user.get("interior",
                                     model_facts.interior_file(self.here, self.name))}

    def write_facts(self, facts):
        if self.measured is None:
            raise RuntimeError("write_facts() needs build_all() first")
        problems = self.check_export()
        if problems:
            raise ValueError("the build does not match export/:\n  " + "\n  ".join(problems))
        doc = model_facts.compose_vehicle(
            self.name, self.here, self.paint_flags, self.default_variant, self.levels,
            self.vehicle_facts(facts), bpy.app.version_string)
        return model_facts.write(model_facts.sidecar_path(self.here, self.name), doc)

    # ------------------------------------------------------------- material
    def material(self, variant=None, paint=None, lamps=None):
        """The one export material (asset_build's: albedo, ORM, optional
        normal, the emission bound default-off), which never reads the ids.
        For previews only, *paint* multiplies the painted panels (B = 1) by
        a linear colour as the game does, and *lamps* gates the emission to
        those surface ids; the export rebuilds the plain material first."""
        mat = super().material(variant)
        if paint is None and lamps is None:
            return mat
        nt = mat.node_tree
        bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        _r255, g255, b = id_sockets(nt, vi.ID_ATTRIBUTE)
        if paint is not None:
            albedo = bsdf.inputs["Base Color"].links[0].from_socket
            nt.links.new(paint_base(nt, albedo, b, paint), bsdf.inputs["Base Color"])
        if lamps is not None:
            gate_emission(nt, bsdf.inputs["Emission Color"], g255, lamps)
        return mat

    def export_all(self):
        """Re-check every tier's ids, put the plain material back, then
        asset_build's export with the id attribute as exact COLOR_0 bytes."""
        for level in self.levels:
            problems = ids_problems(self.lod(level).data)
            if problems:
                raise ValueError("LOD%d ids:\n  %s" % (level, "\n  ".join(problems)))
        self.material()
        return super().export_all()

    # -------------------------------------------------------------- previews
    def paint_for(self, variant):
        """The linear colour a preview multiplies *variant*'s painted panels
        by: preview_paint for a paint-true variant; None (white, the albedo
        as shipped) for a paint-false livery, which the consumer paints
        white."""
        return self.preview_paint if dict(self.paint_flags)[variant] else None

    def render_preview(self):
        self.preview_studio()
        self.show_only(0)
        mat = self.material(self.default_variant, paint=self.paint_for(self.default_variant))
        set_state(mat, 0.0, self.tint)
        path = os.path.join(self.here, "preview.png")
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        self.material()
        return path

    def render_variants(self, tile_w=640):
        """variants.png: each variant by day and at night with the night
        driving lamps (NIGHT_LAMPS) lit; paint-true variants painted with
        preview_paint, a paint-false livery white (paint_for())."""
        path = render_sheet(self.name, self.here, self.variants,
                            lambda v: self.material(v, paint=self.paint_for(v),
                                                    lamps=NIGHT_LAMPS),
                            self.preview_studio, self.show_only, tile_w, self.tint,
                            with_night=True)
        self.material()
        return path

    # ------------------------------------------------------------ steering
    def steer(self, level, angle_deg):
        """Turn the steering wheel parts of tier *level* by *angle_deg*
        (positive: a left turn) about the vertical axis through each wheel's
        centre, in place; returns a function that puts them back. For
        review renders only."""
        me = self.lod(level).data
        part, _s, _p, _c = read_ids(me)
        co = np.zeros(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        saved = co.copy()
        co = co.reshape(-1, 3)
        for w in self.measured["wheels"]:
            if not w["steer"]:
                continue
            verts = sorted({v for i in np.flatnonzero(part == w["part"])
                            for v in me.polygons[int(i)].vertices})
            pts = np.array([vi.to_gltf(c) for c in co[verts]])
            turned = vi.steer(pts, vi.to_gltf(w["centre"]), angle_deg)
            co[verts] = [vi.to_build(p) for p in turned]
        me.vertices.foreach_set("co", co.ravel())
        me.update()

        def restore():
            me.vertices.foreach_set("co", saved)
            me.update()
        return restore
