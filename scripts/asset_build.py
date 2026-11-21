# SPDX-License-Identifier: GPL-3.0-or-later

"""Everything a building's build.py does that does not describe the building.

Each build.py keeps its massing, UVs and layout checks; this module owns the
parts that must be the same for every asset: the toolchain check, the one
material slot and its bindings, the export and its image/emission repairs,
the catalog's fixed preview setup, the day/night sheet, the tier bookkeeping
in build_all(), the facts sidecar and the headless entry point. A change to any of those is made
here once instead of in every asset.

    import asset_build
    asset_build.check_toolchain()
    A = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT)
    get_material, export_all = A.material, A.export_all
    ...
    def build_all():
        return A.build_all(check_layout, build_lod)

    def facts():
        return {...}                # scripts/model_facts.py says what

    if __name__ == "__main__":
        A.main(build_all, facts)

Runs inside Blender only.
"""

import math
import os
import sys

import bmesh
import bpy
from mathutils import Euler, Vector

import model_facts
from glb_images import strip_embedded_images
from variant_previews import render_sheet
from window_emission import LIT_FACTOR, attach, rewrite_glb_emission, set_state
from vehicle_ids import convert_color0_to_ubyte

# ------------------------------------------------------------ toolchain
# Too old: the newest of the catalog's source.blend files are saved by Blender
# 5.3, which an older Blender cannot open, and running a build script on 4.x fails as a bare
# AttributeError deep in the build. Too new: export_all() passes glTF exporter
# flags by keyword, the part most exposed to an upgrade, so each is checked to
# still exist. A flag that keeps its name while changing its default is no
# error at all, which is why notes.md records the export settings too.
BLENDER_MIN = (5, 3)
GLTF_EXPORT_FLAGS = (
    "export_format", "use_selection", "export_yup", "export_apply",
    "export_keep_originals", "export_cameras", "export_lights",
    # an asset that declares an id attribute (Asset.id_attribute, the
    # vehicles) exports it as COLOR_0 and nothing else as a colour, with
    # mesh compression held off: the ids must reach the bytes exactly
    "export_vertex_color", "export_vertex_color_name",
    "export_all_vertex_colors", "export_draco_mesh_compression_enable",
    "export_meshopt_compression_enable",
)
LEVELS = (0, 1, 2, 3)

# ---------------------------------------------------- the catalog preview
# One fixed camera orientation, lens, sun and backdrop for every preview.png,
# so assets compare fairly at a glance. Only the distance is fitted, to the
# asset's LOD0 bounds, with PREVIEW_MARGIN on the frame's tightest side. The
# flat grey world rather than a studio HDRI is recorded as an open question in
# brick_clocktower_hall/notes.md.
PREVIEW_RES = (1600, 1000)
PREVIEW_ROT = (81.316, 0.0, 27.988)
PREVIEW_LENS = 40.0
PREVIEW_MARGIN = 0.08
PREVIEW_SUN = {"rot_deg": (55.0, 0.0, 35.0), "energy": 3.0}
PREVIEW_BG = (0.45, 0.45, 0.47, 1.0)


def check_toolchain():
    """Fail early and legibly on a Blender these scripts cannot drive."""
    if bpy.app.version < BLENDER_MIN:
        raise RuntimeError(
            "Blender %s is below the %s floor, the newest version the catalog's "
            "source.blend files are saved in — see CLAUDE.md's Tech Stack. "
            "Nothing above that floor is pinned."
            % (bpy.app.version_string, ".".join(str(v) for v in BLENDER_MIN)))
    props = bpy.ops.export_scene.gltf.get_rna_type().properties
    missing = [f for f in GLTF_EXPORT_FLAGS if f not in props]
    if missing:
        raise RuntimeError(
            "Blender %s's glTF exporter no longer takes: %s. export_all() sets "
            "these deliberately — export_keep_originals above all, since it is "
            "what keeps the textures referenced instead of embedded in all four "
            "tiers. Re-check CLAUDE.md's Texture Requirements against the "
            "current exporter before dropping an argument to make this pass."
            % (bpy.app.version_string, ", ".join(missing)))


# ------------------------------------------------------------- geometry
def bounds(obj):
    """Centre and bounding radius of *obj*'s vertices."""
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    lo = Vector((min(xs), min(ys), min(zs)))
    hi = Vector((max(xs), max(ys), max(zs)))
    return (lo + hi) / 2.0, (hi - lo).length / 2.0


def pivot_offset(obj):
    """Ground level, centred on the plan's bounding box.

    The box is the whole plan, overhangs and steps included, which is the
    footprint scripts/validate_asset.py checks. Taken from LOD0 and applied to
    every tier, so a LOD switch never moves the building; build_all() asserts
    that every tier then has the same extents.
    """
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    return Vector(((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, min(zs)))


def to_object(B, name):
    """A closed bmesh (B.bm) as a new, unlinked object; raises if it is open."""
    bm = B.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bad = [e for e in bm.edges if len(e.link_faces) != 2]
    if bad:
        c = bad[0].verts[0].co
        raise ValueError("%s is not closed: %d edges without exactly two faces, "
                         "e.g. near (%.3f, %.3f, %.3f)" % (name, len(bad), c.x, c.y, c.z))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return bpy.data.objects.new(name, me)


def open_stack(B, x0, x1, y0, y1, zb, zt, wall, depth, side, rim, soot, bottom):
    """A rectangular stack open at the top, as CLAUDE.md wants every chimney:
    four sides from *zb* to *zt*, a rim *wall* wide round one flue sunk
    *depth* to a floor, and the flue lined and floored in *soot*. Added to
    builder *B* (any build.py's Builder: B.face(cos, uvfn)); *side*, *rim*,
    *soot* and *bottom* are its UV functions. The caller keeps the floor,
    zt - depth, clear of whatever the stack is unioned into, or the union
    fills the flue up to it."""
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    flue = [(x0 + wall, y0 + wall), (x1 - wall, y0 + wall),
            (x1 - wall, y1 - wall), (x0 + wall, y1 - wall)]
    zf = zt - depth
    for k in range(4):
        (ax, ay), (bx, by) = ring[k], ring[(k + 1) % 4]
        B.face([(ax, ay, zb), (bx, by, zb), (bx, by, zt), (ax, ay, zt)], side)
        B.face([ring[k] + (zt,), ring[(k + 1) % 4] + (zt,),
                flue[(k + 1) % 4] + (zt,), flue[k] + (zt,)], rim)
        # walked the other way round, so the lining faces into the flue
        (ax, ay), (bx, by) = flue[(k + 1) % 4], flue[k]
        B.face([(ax, ay, zf), (bx, by, zf), (bx, by, zt), (ax, ay, zt)], soot)
    B.face([(x, y, zf) for x, y in flue], soot)
    B.face([(x, y, zb) for x, y in reversed(ring)], bottom)
    return B


KEYHOLE_TOL = 1e-4


def _open_keyholes(me):
    """Triangulate every face of *me* that passes one point twice.

    The exact solver returns a face with a hole in it, such as a soffit a
    downpipe runs up into, as one polygon that runs out to the hole and back
    along a bridge whose two sides are distinct but coincident vertices. The
    weld every build.py runs next merges them, and bmesh keeps the outline and
    the hole as two faces that overlap: manifold in the build, folded once the
    exporter triangulates it. Triangulated while the bridge is still open, the
    bridge's triangles have no area and the weld removes them. A point
    repeated only in consecutive corners is a short edge, not a bridge, and is
    left alone. Points count as one within KEYHOLE_TOL, the widest weld any
    build.py runs.
    """
    bm = bmesh.new()
    bm.from_mesh(me)
    keyholes = []
    for f in bm.faces:
        cos = [v.co for v in f.verts]
        run = [c for k, c in enumerate(cos) if (c - cos[k - 1]).length > KEYHOLE_TOL]
        n = len(run)
        if any((run[i] - run[j]).length <= KEYHOLE_TOL
               for i in range(n) for j in range(i + 2, n) if (i, j) != (0, n - 1)):
            keyholes.append(f)
    if keyholes:
        bmesh.ops.triangulate(bm, faces=keyholes)
        bm.to_mesh(me)
    bm.free()


SNAP = 1e-4


def snap_vertices(obj, grid=SNAP):
    """Move every vertex of *obj* onto a *grid* metres lattice, in place.

    The exact boolean merges two faces only when they are exactly coplanar.
    Two solids built to share a wall at a non-round coordinate (x = -8/3 m,
    say) reach it by different arithmetic, land an ulp or two apart, and the
    union keeps both faces as an internal double wall. Snapped, both solids
    carry the same float. A power-of-ten grid rounds to decimal places
    (Python's round(), as a build.py's vertex cache keys do), so the snap
    reproduces a vertex already put on that grid by its builder exactly;
    -0.0 is folded into 0.0. The grid must be finer than the smallest
    authored feature, or distinct vertices fold onto one lattice point.
    """
    digits = round(-math.log10(grid))
    if abs(10.0 ** -digits - grid) <= 1e-12 * grid:
        def snap(c):
            return round(c, digits) + 0.0
    else:
        def snap(c):
            return round(c / grid) * grid + 0.0
    for v in obj.data.vertices:
        v.co = (snap(v.co.x), snap(v.co.y), snap(v.co.z))
    return obj


def union(base, others, snap=None):
    """Exact boolean union of *others* into *base*, applied, with any face the
    solver returns as a keyhole triangulated (see _open_keyholes).

    snap=SNAP (0.1 mm) first puts every operand's vertices, *base*'s too, on
    that grid (snap_vertices()), so faces two solids share by design are
    exactly coplanar for the solver however each solid's arithmetic rounded:
    without it a shared wall at a non-round coordinate can survive as an
    internal double wall. Off by default, which leaves every catalog asset's
    build as it was: on, it moves the off-grid vertices of round pipes,
    rails and sloped planes by up to 0.05 mm, which changes where the
    boolean cuts and so the triangle counts of most existing buildings. A
    new build.py should pass it:

        obj = union(base, parts, snap=asset_build.SNAP)
    """
    return _boolean(base, others, 'UNION', snap)


def difference(base, cutters, snap=None):
    """Exact boolean difference of *cutters* from *base*, applied, as union()
    applies its union: keyholes opened, the cutters removed, *base* returned
    unlinked, and *snap* as union() takes it. Each cutter is a closed solid,
    such as a drive-through lane's void cut out of a hand-built box before
    the rest is unioned in:

        house = difference(to_object(shed_box(level), "tmp_shed"),
                           [to_object(lane_void(level), "tmp_lane")])
        obj = union(house, parts)
    """
    return _boolean(base, cutters, 'DIFFERENCE', snap)


def _boolean(base, others, operation, snap=None):
    """union()'s and difference()'s shared body: the operands snapped when
    *snap* is a grid, *others* as one operand collection on a BOOLEAN
    modifier of *base*, evaluated with the exact solver, keyholes opened,
    *others* deleted, *base* returned unlinked."""
    if snap:
        for o in [base] + list(others):
            snap_vertices(o, snap)
    scn = bpy.context.scene
    scn.collection.objects.link(base)
    col = bpy.data.collections.new(base.name + "_operands")
    scn.collection.children.link(col)
    for o in others:
        col.objects.link(o)
    mod = base.modifiers.new(operation.lower(), 'BOOLEAN')
    mod.operation, mod.solver = operation, 'EXACT'
    mod.operand_type, mod.collection = 'COLLECTION', col
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(base.evaluated_get(dg))
    _open_keyholes(me)
    old = base.data
    base.modifiers.clear()
    base.data = me
    bpy.data.meshes.remove(old)
    for o in others:
        d = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.meshes.remove(d)
    bpy.data.collections.remove(col)
    scn.collection.objects.unlink(base)
    return base


def fit_camera(cam, obj, margin, res=PREVIEW_RES):
    """Place *cam*, orientation fixed, so *obj*'s bounding box is centred in
    frame and fills it to within *margin* on its tightest side."""
    from bpy_extras.object_utils import world_to_camera_view
    scn = bpy.context.scene
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    corners = [Vector((x, y, z)) for x in (min(xs), max(xs))
               for y in (min(ys), max(ys)) for z in (min(zs), max(zs))]
    rot = cam.rotation_euler.to_matrix()
    fwd, right, up = rot @ Vector((0, 0, -1)), rot @ Vector((1, 0, 0)), rot @ Vector((0, 1, 0))
    centre, radius = bounds(obj)
    dist, shift = radius * 3.0, Vector((0.0, 0.0))
    for _ in range(40):
        cam.location = centre - fwd * dist + right * shift.x + up * shift.y
        bpy.context.view_layer.update()
        pts = [world_to_camera_view(scn, cam, c) for c in corners]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts)))
        span = max(hi.x - lo.x, hi.y - lo.y)
        mid = (lo + hi) / 2.0 - Vector((0.5, 0.5))
        # frame half-width at this distance, in metres, per unit of view space
        k = dist * 36.0 / cam.data.lens
        shift += Vector((mid.x * k, mid.y * k * res[1] / res[0]))
        dist *= span / (1.0 - 2.0 * margin)
    return cam


# ================================================================ asset
class Asset:
    """One building: its name, folder, colour variants and reference lit tint.

    tint is the asset's reference lit factor for previews (a shop's cool
    fluorescent interior, say); None means the catalog's warm default. The
    export writes the glTF emission factor as zero either way. camera_location
    pins the preview camera instead of fitting it: the first asset's preview
    was framed by hand, and keeping its camera keeps its preview unchanged.

    night_lit=False is for a building with no glazing and so no emission map
    (a windowless shed, a chimney stack; CLAUDE.md, Output Contract), and
    for a prop without a lamp: the material has no emission mask wired in,
    the export leaves out the lit state and the factor rewrite, and
    variants.png is a day-only row, written only when there is more than one
    variant to show.

    pivot is for a prop pivoted on its attachment point (CLAUDE.md, Props)
    rather than its plan's centre: a build-frame point every tier is moved
    by instead of LOD0's pivot_offset(). Every tier must then still have
    LOD0's plan centre, wherever that lies. None (buildings) keeps the
    plan-centred pivot.

    id_attribute names a FLOAT_COLOR corner attribute that the export
    writes as COLOR_0 (and no other colour), with Draco and meshopt held
    off; COLOR_0 is then rewritten as exact normalised bytes
    (vehicle_ids.convert_color0_to_ubyte()), which a consumer that
    truncates floats to bytes needs. None, the default and every
    building's and prop's, exports exactly as before: a subclass sets it
    (scripts/vehicle_build.py's VehicleAsset).
    """

    id_attribute = None

    def __init__(self, name, here, variants, default_variant, tint=None,
                 levels=LEVELS, camera_location=None, night_lit=True, pivot=None):
        self.name, self.here = name, here
        self.export_dir = os.path.join(here, "export")
        self.variants = list(variants)
        self.default_variant = default_variant
        self.tint = LIT_FACTOR if tint is None else tuple(tint)
        self.levels = tuple(levels)
        self.camera_location = camera_location
        self.night_lit = bool(night_lit)
        self.pivot = None               # set by build_all(): LOD0's pivot offset
        self.authored_pivot = None if pivot is None else tuple(pivot)

    def lod(self, level):
        return bpy.data.objects["{}_LOD{}".format(self.name, level)]

    # ------------------------------------------------------------ material
    def _image(self, node, fn, colorspace):
        img = bpy.data.images.get(fn)
        path = os.path.join(self.export_dir, fn)
        if bpy.data.filepath:
            # linked, not packed, and relative, so source.blend still finds
            # export/ wherever the repository is checked out
            path = bpy.path.relpath(path)
        if img is None:
            img = bpy.data.images.load(path, check_existing=True)
            img.name = fn
        else:
            img.filepath = path
            img.reload()
        img.colorspace_settings.name = colorspace
        node.image = img
        node.extension = 'REPEAT'
        node.interpolation = 'Linear'

    def material(self, variant=None):
        """Single slot, external textures, shared by all four tiers.

        Albedo to Base Color; the ORM's green and blue to roughness and
        metallic, and its red to a glTF Material Output group's Occlusion
        input, which is what makes the exporter write an occlusionTexture.
        The normal map goes through a tangent-space Normal Map node at
        strength 1, written as normalTexture at scale 1; tangents are left to
        the consumer's MikkTSpace, as glTF specifies when none are exported.
        A prop may ship without a normal map (CLAUDE.md, Props): when
        export/<name>_normal.png does not exist the material has no normal
        nodes, so the export writes no normalTexture. Buildings always have
        one (validate_asset.py warns if a building's is missing). The
        emission mask is attached default-off (window_emission) when the
        asset is night-lit.
        """
        variant = variant or self.default_variant
        normal_fn = "{}_normal.png".format(self.name)
        has_normal = os.path.isfile(os.path.join(self.export_dir, normal_fn))
        mat = bpy.data.materials.get(self.name) or bpy.data.materials.new(self.name)
        if mat.node_tree is None:        # use_nodes is deprecated in 5.x, gone in 6.0
            mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (620, 0)
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (300, 0)
        t_alb = nt.nodes.new("ShaderNodeTexImage"); t_alb.location = (-380, 160)
        t_orm = nt.nodes.new("ShaderNodeTexImage"); t_orm.location = (-380, -200)
        if has_normal:
            t_nrm = nt.nodes.new("ShaderNodeTexImage"); t_nrm.location = (-380, -560)
        sep = nt.nodes.new("ShaderNodeSeparateColor"); sep.location = (-70, -200)
        if has_normal:
            nmap = nt.nodes.new("ShaderNodeNormalMap"); nmap.location = (-70, -560)
            nmap.space = 'TANGENT'
            nmap.inputs["Strength"].default_value = 1.0
        self._image(t_alb, "{}_albedo_{}.png".format(self.name, variant), 'sRGB')
        self._image(t_orm, "{}_orm.png".format(self.name), 'Non-Color')
        if has_normal:
            self._image(t_nrm, normal_fn, 'Non-Color')
        nt.links.new(t_alb.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(t_orm.outputs["Color"], sep.inputs["Color"])
        nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
        nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
        if has_normal:
            nt.links.new(t_nrm.outputs["Color"], nmap.inputs["Color"])
            nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

        grp = bpy.data.node_groups.get("glTF Material Output")
        if grp is None:
            grp = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
        if "Occlusion" not in [s.name for s in grp.interface.items_tree]:
            grp.interface.new_socket("Occlusion", in_out='INPUT',
                                     socket_type='NodeSocketFloat')
        gnode = nt.nodes.new("ShaderNodeGroup"); gnode.location = (300, -380)
        gnode.node_tree = grp
        nt.links.new(sep.outputs["Red"], gnode.inputs["Occlusion"])
        if self.night_lit:
            attach(mat, self.export_dir, self.name, self.tint)
        mat.use_backface_culling = True               # closed opaque shell
        return mat

    # --------------------------------------------------------------- tiers
    def show_only(self, level):
        for lv in self.levels:
            o = self.lod(lv)
            o.hide_set(lv != level)
            o.hide_render = (lv != level)

    def build_all(self, check, build_lod):
        """Run the asset's layout check, build every tier, give them one
        pivot and one material, and return per-tier triangle counts.

        One pivot for every tier, taken from LOD0, and every tier must then be
        centred on it. Pivoting each tier on its own bounds hides a tier that
        lost or gained something at its edge: the engine swaps tiers in place,
        so the building would jump at the switch while each file looked right.
        """
        problems = check()
        if problems:
            raise ValueError("layout check failed:\n  " + "\n  ".join(problems))
        for level in self.levels:
            old = bpy.data.objects.get("{}_LOD{}".format(self.name, level))
            if old:
                m = old.data
                bpy.data.objects.remove(old, do_unlink=True)
                bpy.data.meshes.remove(m)
        col = bpy.data.collections.get(self.name)
        if col is None:
            col = bpy.data.collections.new(self.name)
            bpy.context.scene.collection.children.link(col)

        mat = self.material()
        objs = [build_lod(level) for level in self.levels]
        off = pivot_offset(objs[0])
        if self.authored_pivot is not None:
            off = Vector(self.authored_pivot)
        ref = pivot_offset(objs[0]) - off       # zero unless the pivot is authored
        self.pivot = tuple(off)
        stats = {}
        for level, obj in zip(self.levels, objs):
            for v in obj.data.vertices:
                v.co -= off
            centre = pivot_offset(obj) - ref
            if centre.length > 1e-3:
                raise ValueError("LOD%d's extents differ from LOD0's (centre off "
                                 "by %s)" % (level, tuple(round(c, 4) for c in centre)))
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            col.objects.link(obj)
            obj.data.calc_loop_triangles()
            stats["LOD{}".format(level)] = len(obj.data.loop_triangles)
            obj.hide_set(level != 0)
            obj.hide_render = (level != 0)
        stats["pivot_offset"] = tuple(round(c, 4) for c in off)
        lo, hi = Vector(), Vector()
        vs = [v.co for v in self.lod(0).data.vertices]
        for i in range(3):
            lo[i], hi[i] = min(v[i] for v in vs), max(v[i] for v in vs)
        stats["bounds"] = tuple(round(h - lw, 3) for lw, h in zip(lo, hi))
        return stats

    # --------------------------------------------------------------- export
    def export_all(self):
        """Export every tier, then repair the image and emission entries.

        yup for the target's glTF import path, selection-only so the studio
        camera, sun and ground never leak in, keep-originals so the tiers
        reference one texture set instead of embedding it four times. Every
        tier references the default variant's albedo; the other variants are
        the same mesh with that one file swapped.

        The material is exported lit (strength 1), because the exporter drops
        an emissive texture whose factor is zero, and each file's glTF factor
        is then rewritten to zero so the asset ships with its lights off; an
        asset that is not night-lit has no emission to set or rewrite.
        strip_embedded_images() removes the placeholder bufferView that
        keep-originals leaves beside each image's uri.
        """
        mat, saved = bpy.data.materials[self.name], None
        if self.night_lit:
            bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            saved = (bsdf.inputs['Emission Strength'].default_value,
                     tuple(mat.node_tree.nodes['Window emission tint']
                           .inputs[2].default_value[:3]))
        written = []
        try:
            if saved is not None:
                set_state(mat, 1.0, self.tint)
            for level in self.levels:
                obj = self.lod(level)
                for other in bpy.data.objects:
                    other.select_set(False)
                obj.hide_set(False)
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                path = os.path.join(self.export_dir, "{}_lod{}.glb".format(self.name, level))
                ids = {}
                if self.id_attribute:
                    ids = dict(export_vertex_color='NAME',
                               export_vertex_color_name=self.id_attribute,
                               export_all_vertex_colors=False,
                               export_draco_mesh_compression_enable=False,
                               export_meshopt_compression_enable=False)
                bpy.ops.export_scene.gltf(
                    filepath=path, export_format='GLB', use_selection=True,
                    export_yup=True, export_apply=True, export_keep_originals=True,
                    export_cameras=False, export_lights=False, **ids)
                obj.select_set(False)
                strip_embedded_images(path)
                if saved is not None:
                    rewrite_glb_emission(path, (0, 0, 0))
                if self.id_attribute:
                    convert_color0_to_ubyte(path)
                written.append(os.path.basename(path))
        finally:
            if saved is not None:
                set_state(mat, *saved)
        self.show_only(0)
        return written

    # ------------------------------------------------------------- previews
    def preview_studio(self):
        """The catalog's fixed preview camera, sun and backdrop."""
        scn = bpy.context.scene
        scn.render.engine = 'BLENDER_EEVEE'
        scn.render.resolution_x, scn.render.resolution_y = PREVIEW_RES
        scn.render.resolution_percentage = 100
        scn.render.film_transparent = False
        scn.render.image_settings.file_format = 'PNG'
        scn.render.image_settings.color_mode = 'RGB'
        scn.view_settings.view_transform = 'AgX'
        scn.view_settings.look = 'None'
        scn.view_settings.exposure = 0.0

        world = scn.world or bpy.data.worlds.new("World")
        scn.world = world
        if world.node_tree is None:     # use_nodes is deprecated in 5.x, gone in 6.0
            world.use_nodes = True
        bg = next((n for n in world.node_tree.nodes if n.type == 'BACKGROUND'), None)
        if bg:
            bg.inputs[0].default_value = PREVIEW_BG
            bg.inputs[1].default_value = 1.0

        cam = bpy.data.objects.get("PreviewCam")
        if cam is None:
            cam = bpy.data.objects.new("PreviewCam", bpy.data.cameras.new("PreviewCam"))
            scn.collection.objects.link(cam)
        cam.data.type = 'PERSP'
        cam.data.lens = PREVIEW_LENS
        cam.rotation_euler = Euler([math.radians(a) for a in PREVIEW_ROT], 'XYZ')
        cam.data.clip_end = 1000.0
        scn.camera = cam
        if self.camera_location is not None:
            cam.location = Vector(self.camera_location)
        else:
            fit_camera(cam, self.lod(0), PREVIEW_MARGIN)

        sun = bpy.data.objects.get("StudioSun")
        if sun is None:
            sun = bpy.data.objects.new("StudioSun", bpy.data.lights.new("StudioSun", 'SUN'))
            scn.collection.objects.link(sun)
        sun.data.energy = PREVIEW_SUN["energy"]
        sun.rotation_euler = Euler([math.radians(a) for a in PREVIEW_SUN["rot_deg"]], 'XYZ')

        gnd = bpy.data.objects.get("_studio_ground")
        if gnd is None:
            me = bpy.data.meshes.new("_studio_ground_mesh")
            bm = bmesh.new()
            bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=140.0)
            bm.to_mesh(me)
            bm.free()
            gnd = bpy.data.objects.new("_studio_ground", me)
            scn.collection.objects.link(gnd)
        gnd.hide_render = False
        return cam

    def render_preview(self):
        """LOD0, default variant, lights off, from the fixed setup, to preview.png."""
        self.preview_studio()
        self.show_only(0)
        mat = self.material(self.default_variant)
        if self.night_lit:
            set_state(mat, 0.0, self.tint)
        path = os.path.join(self.here, "preview.png")
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        return path

    def render_variants(self, tile_w=640):
        """variants.png: one column per colour, day above night when the
        asset is night-lit; for an unlit asset a single day row, and none at
        all when it has only one variant (preview.png already shows it)."""
        if not self.night_lit and len(self.variants) < 2:
            return "no variants.png: not night-lit, one variant"
        return render_sheet(self.name, self.here, self.variants, self.material,
                            self.preview_studio, self.show_only, tile_w, self.tint,
                            with_night=self.night_lit)

    # ---------------------------------------------------------------- facts
    def check_export(self, tol=1e-3):
        """Problems that say the tiers in the scene are not the exported ones:
        a triangle count or LOD0 bounds that differ from the .glb on disk."""
        problems = []
        for level in self.levels:
            me = self.lod(level).data
            me.calc_loop_triangles()
            fn = "{}_lod{}.glb".format(self.name, level)
            on_disk = model_facts.glb_stats(os.path.join(self.export_dir, fn))
            if len(me.loop_triangles) != on_disk["triangles"]:
                problems.append("%s has %d triangles, the build %d"
                                % (fn, on_disk["triangles"], len(me.loop_triangles)))
            if level == self.levels[0]:
                # Blender (x, y, z) is glTF (x, z, -y)
                pts = [(v.co.x, v.co.z, -v.co.y) for v in me.vertices]
                for key, pick in (("min", min), ("max", max)):
                    here = [pick(p[i] for p in pts) for i in range(3)]
                    if any(abs(a - b) > tol for a, b in zip(here, on_disk[key])):
                        problems.append("%s bounds.%s is %s, the build's %s"
                                        % (fn, key, on_disk[key],
                                           [round(c, 4) for c in here]))
        return problems

    def write_facts(self, facts):
        """Write export/<name>.model.json (scripts/model_facts.py) for the
        tiers build_all() left in the scene and the files in export/.

        *facts* is the build.py's facts(), in the build frame; the pivot is
        applied here. Refuses when the scene's tiers are not the exported
        ones, since the doors and footprint would then describe other files.
        """
        if self.pivot is None:
            raise RuntimeError("write_facts() needs build_all() first: the "
                               "pivot offset comes from that build")
        problems = self.check_export()
        if problems:
            raise ValueError("the build does not match export/:\n  "
                             + "\n  ".join(problems))
        doc = model_facts.compose(
            self.name, self.here, self.variants, self.default_variant,
            self.levels, self.pivot, facts() if callable(facts) else facts,
            bpy.app.version_string)
        return model_facts.write(model_facts.sidecar_path(self.here, self.name), doc)

    # ---------------------------------------------------------------- main
    def _clear_factory_scene(self):
        """Started from the factory scene rather than source.blend: its cube,
        light and camera would sit in the renders, so remove every object
        but the tiers."""
        keep = {"{}_LOD{}".format(self.name, lv) for lv in self.levels}
        for o in list(bpy.data.objects):
            if o.name not in keep:
                bpy.data.objects.remove(o, do_unlink=True)

    def main(self, build_all, facts=None):
        """The headless rebuild: build, export, preview, variants, save, and
        the facts sidecar when the build.py declares *facts*.

            blender --background source.blend --python build.py

        With the word `facts` after `--` it builds the tiers in memory, checks
        them against the files already in export/ and writes only the sidecar;
        nothing else is exported, rendered or saved:

            blender --background --python build.py -- facts

        With `variants` it builds the tiers in memory, refuses if they are not
        the exported ones (check_export(), as facts does), and renders only
        variants.png (render_variants()) from the textures in export/;
        nothing is exported or saved, so a new colour or a changed sheet
        needs no rebuild:

            blender --background --python build.py -- variants
        """
        argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
        if argv == ["facts"]:
            if facts is None:
                raise RuntimeError("%s declares no facts()" % self.name)
            print(build_all())
            print(self.write_facts(facts))
            return
        if argv == ["variants"]:
            print(build_all())
            problems = self.check_export()
            if problems:
                raise ValueError("the build does not match export/:\n  "
                                 + "\n  ".join(problems))
            if not bpy.data.filepath:
                self._clear_factory_scene()
            print(self.render_variants())
            return
        if argv:
            raise RuntimeError("unknown arguments %s; the only ones are `facts` "
                               "and `variants`" % argv)
        if not bpy.data.filepath:
            # save straight away so the texture paths are written relative
            self._clear_factory_scene()
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(self.here, "source.blend"))
        print(build_all())
        print(self.export_all())
        print(self.render_preview())
        print(self.render_variants())
        bpy.ops.wm.save_mainfile()
        if facts is not None:
            print(self.write_facts(facts))
