# SPDX-License-Identifier: GPL-3.0-or-later

"""The vehicle review sheet (CLAUDE.md, Vehicles), as one command.

Run in a separate background Blender, never in an authoring session:

    blender -b -P scripts/review_vehicle.py -- ASSET_DIR OUTPUT_DIR [--variant NAME]
    blender -b -P scripts/review_vehicle.py -- ASSET_DIR OUTPUT_DIR --cycles \
        [--samples N] [--device cpu]

The sheet renders in EEVEE; --cycles renders it in Cycles instead, on the AMD
HIP device unless --device cpu asks for the CPU (review_asset.use_device():
this process only, and an error where there is no HIP device).

OUTPUT_DIR belongs under the git-ignored review/ folder: the sheet is for the
owner's look and is never committed. It receives every frame as a PNG,
<asset>_review_sheet.png (the contact sheet) and <asset>_review.json (the
settings and the frame list):

    views     side, front, rear and top (orthographic) and a three-quarter
    steer     the front wheels turned +35 and -35 degrees, top and three-quarter
    lamps     each lamp group lit alone at night, from the front and the rear
    night     tail, low beam and brake together; the cabin (glass ids) lit
    ids       a false-colour view of the surface ids and wheel parts
    paint     white, dark grey and red through the B channel
    tiers     LOD0..LOD3 side by side at 30, 100 and 400 m (75 degree vertical
              field of view at 1080p, the contract's band assumption), each
              crop enlarged to the tile with the true pixel size labelled

Every scene has a 1.8 m standing figure and the class's parking bay outline
(car 2.5 x 5.0 m, van and truck 3.0 x 8.0 m, bus 3.0 x 13.0 m).

The tiers are built from the exported files' accessors (scripts/vehicle_ids.py),
not through Blender's glTF importer, which reads COLOR_0 as an sRGB byte
colour and multiplies it into the base colour. The material is made from the
files the GLB names: albedo times the paint where B = 1, ORM, the normal map
when there is one, and the emission gated per surface id by the review.
"""

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path

import blf
import bpy
import imbuf
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vehicle_ids as vi  # noqa: E402
from review_asset import use_device  # noqa: E402

RES = (960, 540)
TILE = (480, 270)
PAINTS = {"white": (0.80, 0.80, 0.80), "dark_grey": (0.035, 0.037, 0.040),
          "red": (0.45, 0.02, 0.02)}
LAMP_GAIN = 6.0
CABIN_GAIN = 3.0
NIGHT_SET = (1, 2, 3, 7)
DISTANCES = (30.0, 100.0, 400.0)
TIER_FOV = 75.0
FALSE = {"plain": (0.30, 0.30, 0.30), "paint": (0.75, 0.75, 0.72),
         "wheel": (0.10, 0.12, 0.35), "glass": (0.05, 0.55, 0.75)}
FALSE_LAMP = {"red": (0.9, 0.05, 0.05), "amber": (1.0, 0.45, 0.0), "white": (1.0, 1.0, 0.85)}


# ================================================================ scene
def setup(engine, samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.render.engine = engine
    if engine == 'CYCLES':
        scn.cycles.samples = samples
        scn.cycles.use_denoising = True
        scn.cycles.seed = 42
    scn.render.resolution_x, scn.render.resolution_y = RES
    scn.render.resolution_percentage = 100
    scn.render.image_settings.file_format = 'PNG'
    scn.render.image_settings.color_mode = 'RGB'
    scn.view_settings.view_transform = 'AgX'
    scn.view_settings.look = 'None'
    world = bpy.data.worlds.new("review")
    scn.world = world
    if world.node_tree is None:
        world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", 'SUN'))
    scn.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), 0.0, math.radians(35))
    sun.data.angle = math.radians(2)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scn.collection.objects.link(cam)
    scn.camera = cam
    cam.data.clip_end = 5000.0
    return scn, bg, sun, cam


def day(bg, sun):
    bg.inputs[0].default_value = (0.50, 0.52, 0.56, 1.0)
    bg.inputs[1].default_value = 1.0
    sun.data.energy = 3.0
    sun.data.color = (1.0, 0.96, 0.9)


def night(bg, sun):
    bg.inputs[0].default_value = (0.10, 0.13, 0.22, 1.0)
    bg.inputs[1].default_value = 0.08
    sun.data.energy = 0.06
    sun.data.color = (0.5, 0.6, 1.0)


def flat_material(name, rgb, emit=0.0):
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = 0.9
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1.0)
        b.inputs["Emission Strength"].default_value = emit
    return m


def box_object(name, lo, hi, mat):
    me = bpy.data.meshes.new(name)
    c = [(x, y, z) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    faces = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    me.from_pydata(c, [], faces)
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(o)
    return o


def props(body_class):
    """Ground, the bay outline and the 1.8 m figure (Blender frame)."""
    ground = box_object("ground", (-3000, -3000, -0.02), (3000, 3000, -0.001),
                        flat_material("ground", (0.14, 0.145, 0.15)))
    line = flat_material("bay line", (0.85, 0.85, 0.80))
    bw, bl = vi.CLASSES[body_class]["bay"]
    t = 0.10
    for x0, x1, y0, y1 in ((-bw / 2 - t, -bw / 2, -bl / 2, bl / 2), (bw / 2, bw / 2 + t, -bl / 2, bl / 2),
                           (-bw / 2 - t, bw / 2 + t, -bl / 2 - t, -bl / 2),
                           (-bw / 2 - t, bw / 2 + t, bl / 2, bl / 2 + t)):
        box_object("bay", (x0, y0, -0.001), (x1, y1, 0.002), line)
    skin = flat_material("figure", (0.45, 0.40, 0.36))
    fx, fy = bw / 2 + 0.6, bl / 2 + 0.5        # beside the bay's rear corner
    box_object("figure_body", (fx - 0.2, fy - 0.12, 0.0), (fx + 0.2, fy + 0.12, 1.55), skin)
    box_object("figure_head", (fx - 0.1, fy - 0.1, 1.58), (fx + 0.1, fy + 0.1, 1.80), skin)
    return ground, (bw, bl, fx)


# ================================================================ tiers
def gltf_to_blender(a):
    a = np.asarray(a, float)
    return np.stack([a[:, 0], -a[:, 2], a[:, 1]], axis=1)


def tier_object(name, t):
    """A mesh from one tier's accessors, with the ids as a FLOAT_COLOR corner
    attribute 'ids' (bytes / 255), UVs and the file's normals."""
    P = gltf_to_blender(t["positions"])
    tri = t["triangles"]
    me = bpy.data.meshes.new(name)
    me.from_pydata(P.tolist(), [], tri.tolist())
    me.update()
    uv = me.uv_layers.new(name="UVMap")
    corner_v = tri.ravel()
    uvs = t["uv"][corner_v].copy()
    uvs[:, 1] = 1.0 - uvs[:, 1]
    uv.data.foreach_set("uv", uvs.astype(np.float32).ravel())
    ids = me.color_attributes.new("ids", 'FLOAT_COLOR', 'CORNER')
    ids.data.foreach_set("color", t["color"][corner_v].astype(np.float32).ravel())
    n = gltf_to_blender(t["normals"])[corner_v]
    me.shade_smooth()
    me.normals_split_custom_set(n.tolist())
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def image(path, colorspace):
    im = bpy.data.images.load(str(path), check_existing=True)
    im.colorspace_settings.name = colorspace
    return im


def tier_material(edir, js, surfaces, variant_file):
    """The review material: albedo x paint (B), ORM, normal map, emission
    gated per surface id by Value nodes named gain_<id>."""
    gm = js["materials"][0]

    def uri(binding):
        return js["images"][js["textures"][binding["index"]]["source"]]["uri"]
    m = bpy.data.materials.new("review")
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    pbr = gm["pbrMetallicRoughness"]
    alb = nt.nodes.new("ShaderNodeTexImage")
    alb.image = image(Path(edir) / (variant_file or uri(pbr["baseColorTexture"])), 'sRGB')
    orm = nt.nodes.new("ShaderNodeTexImage")
    orm.image = image(Path(edir) / uri(pbr["metallicRoughnessTexture"]), 'Non-Color')
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(orm.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
    if "normalTexture" in gm:
        nrm = nt.nodes.new("ShaderNodeTexImage")
        nrm.image = image(Path(edir) / uri(gm["normalTexture"]), 'Non-Color')
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(nrm.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_type = 'GEOMETRY'
    attr.attribute_name = "ids"
    ids = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], ids.inputs["Color"])
    paint = nt.nodes.new("ShaderNodeRGB")
    paint.name = "paint"
    paint.outputs[0].default_value = (1, 1, 1, 1)
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type, mul.blend_type = 'RGBA', 'MULTIPLY'
    mul.inputs["Factor"].default_value = 1.0
    nt.links.new(alb.outputs["Color"], mul.inputs[6])
    nt.links.new(paint.outputs[0], mul.inputs[7])
    pick = nt.nodes.new("ShaderNodeMix")
    pick.data_type = 'RGBA'
    nt.links.new(ids.outputs["Blue"], pick.inputs["Factor"])
    nt.links.new(alb.outputs["Color"], pick.inputs[6])
    nt.links.new(mul.outputs[2], pick.inputs[7])
    nt.links.new(pick.outputs[2], bsdf.inputs["Base Color"])
    g255 = nt.nodes.new("ShaderNodeMath")
    g255.operation = 'MULTIPLY'
    g255.inputs[1].default_value = 255.0
    nt.links.new(ids.outputs["Green"], g255.inputs[0])
    total = None
    for k in sorted(surfaces):
        cmp_ = nt.nodes.new("ShaderNodeMath")
        cmp_.operation = 'COMPARE'
        cmp_.inputs[1].default_value = float(k)
        cmp_.inputs[2].default_value = 0.5
        nt.links.new(g255.outputs[0], cmp_.inputs[0])
        gain = nt.nodes.new("ShaderNodeValue")
        gain.name = "gain_%d" % k
        gain.outputs[0].default_value = 0.0
        g = nt.nodes.new("ShaderNodeMath")
        g.operation = 'MULTIPLY'
        nt.links.new(cmp_.outputs[0], g.inputs[0])
        nt.links.new(gain.outputs[0], g.inputs[1])
        if total is None:
            total = g.outputs[0]
        else:
            add = nt.nodes.new("ShaderNodeMath")
            add.operation = 'ADD'
            nt.links.new(total, add.inputs[0])
            nt.links.new(g.outputs[0], add.inputs[1])
            total = add.outputs[0]
    emit = nt.nodes.new("ShaderNodeTexImage")
    emit.image = image(Path(edir) / uri(gm["emissiveTexture"]), 'sRGB')
    nt.links.new(emit.outputs["Color"], bsdf.inputs["Emission Color"])
    if total is not None:
        nt.links.new(total, bsdf.inputs["Emission Strength"])
    else:
        bsdf.inputs["Emission Strength"].default_value = 0.0
    m.use_backface_culling = True
    return m


def false_material(lamp_ids, glass_ids, parts):
    """Flat colours from the ids: wheels, lamps in their colours, glass,
    painted and plain body."""
    m = bpy.data.materials.new("false colour")
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_type = 'GEOMETRY'
    attr.attribute_name = "ids"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], sep.inputs["Color"])

    def scaled(sock):
        mm = nt.nodes.new("ShaderNodeMath")
        mm.operation = 'MULTIPLY'
        mm.inputs[1].default_value = 255.0
        nt.links.new(sock, mm.inputs[0])
        return mm.outputs[0]
    r255, g255 = scaled(sep.outputs["Red"]), scaled(sep.outputs["Green"])
    base = nt.nodes.new("ShaderNodeMix")
    base.data_type = 'RGBA'
    nt.links.new(sep.outputs["Blue"], base.inputs["Factor"])
    base.inputs[6].default_value = (*FALSE["plain"], 1)
    base.inputs[7].default_value = (*FALSE["paint"], 1)
    col = base.outputs[2]

    def layer(col, sock, k, rgb):
        cmp_ = nt.nodes.new("ShaderNodeMath")
        cmp_.operation = 'COMPARE'
        cmp_.inputs[1].default_value = float(k)
        cmp_.inputs[2].default_value = 0.5
        nt.links.new(sock, cmp_.inputs[0])
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = 'RGBA'
        nt.links.new(cmp_.outputs[0], mx.inputs["Factor"])
        nt.links.new(col, mx.inputs[6])
        mx.inputs[7].default_value = (*rgb, 1)
        return mx.outputs[2]
    for p in parts:
        shade = 0.6 + 0.4 * (p % 2)
        col = layer(col, r255, p, tuple(c * shade for c in FALSE["wheel"]))
    for k in lamp_ids:
        base_rgb = FALSE_LAMP[vi.lamp_colour(k)]
        f = 0.55 + 0.45 * ((k * 37) % 7) / 6.0
        col = layer(col, g255, k, tuple(c * f for c in base_rgb))
    for k in glass_ids:
        f = 0.5 + 0.5 * (k - 32) / 7.0
        col = layer(col, g255, k, (FALSE["glass"][0], FALSE["glass"][1] * f, FALSE["glass"][2]))
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(col, em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


# ================================================================ cameras
def aim(cam, target):
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()


def ortho_fit(across, up, margin=1.15):
    """Ortho scale (the frame's width in metres) that holds *across* metres
    across and *up* metres up the frame, with a margin."""
    return max(across, up * RES[0] / RES[1]) * margin


def view(cam, kind, centre, span, az=0.0, el=0.0, dist=None):
    """ortho side/front/rear/top (*span* the ortho scale), or a perspective
    three-quarter (*span* sets the distance). The top view turns the
    vehicle's length across the frame."""
    c = Vector(centre)
    if kind == "persp":
        cam.data.type = 'PERSP'
        cam.data.sensor_fit = 'VERTICAL'
        cam.data.sensor_height = 24.0
        cam.data.lens = 24.0 / (2 * math.tan(math.radians(40.0) / 2))
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
        cam.location = c + d * (dist or span * 1.6)
        aim(cam, c)
        return
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = span
    d = {"side": Vector((1, 0, 0)), "front": Vector((0, -1, 0)), "rear": Vector((0, 1, 0)),
         "top": Vector((0, 0, 1))}[kind]
    cam.location = c + d * 60.0
    if kind == "top":
        cam.rotation_euler = (0.0, 0.0, math.radians(90.0))
    else:
        aim(cam, c)


# ================================================================ frames
def label(path, text, dark=False):
    ib = imbuf.load(str(path))
    w, h = ib.size
    with blf.bind_imbuf(0, ib):
        blf.size(0, max(14, h // 22))
        blf.color(0, *((0.92, 0.92, 0.95, 1) if dark else (0.05, 0.05, 0.05, 1)))
        blf.position(0, 10, h - h // 14, 0)
        blf.draw_buffer(0, text)
    imbuf.write(ib, filepath=str(path))


def pixels(path):
    im = bpy.data.images.load(str(path), check_existing=False)
    w, h = im.size
    a = np.array(im.pixels[:], np.float32).reshape(h, w, 4)
    bpy.data.images.remove(im)
    return a


def fit_tile(a, tile=TILE, nearest=False):
    h, w = a.shape[:2]
    if nearest:
        k = max(1, min(tile[0] // w, tile[1] // h))
        a = np.repeat(np.repeat(a, k, axis=0), k, axis=1)
    else:
        while a.shape[1] >= 2 * tile[0] and a.shape[0] >= 2 * tile[1]:
            a = a.reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2, 4).mean(axis=(1, 3))
    out = np.zeros((tile[1], tile[0], 4), np.float32)
    out[..., 3] = 1.0
    out[..., :3] = 0.08
    h, w = a.shape[:2]
    h2, w2 = min(h, tile[1]), min(w, tile[0])
    y0, x0 = (tile[1] - h2) // 2, (tile[0] - w2) // 2
    out[y0:y0 + h2, x0:x0 + w2] = a[(h - h2) // 2:(h - h2) // 2 + h2, (w - w2) // 2:(w - w2) // 2 + w2]
    return out


def main(args):
    adir = Path(args.asset).resolve()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    name = adir.name
    edir = adir / "export"
    with open(edir / ("%s.model.json" % name)) as fh:
        doc = json.load(fh)
    cls = doc["body"]["class"]
    variant_file = None
    if args.variant:
        variant_file = "%s_albedo_%s.png" % (name, args.variant)
        if not (edir / variant_file).is_file():
            raise RuntimeError("no %s" % variant_file)
    engine = 'CYCLES' if args.cycles else 'BLENDER_EEVEE'
    if args.device and not args.cycles:
        raise RuntimeError("--device applies to --cycles; EEVEE has no device choice")
    scn, bg, sun, cam = setup(engine, args.samples)
    # After setup(): read_factory_settings() resets the preferences.
    renderer = use_device(scn, args.device or "gpu") if args.cycles else None
    tiers, mats, objs = {}, {}, {}
    for lv in vi.LEVELS:
        t = vi.tier(edir / ("%s_lod%d.glb" % (name, lv)))
        tiers[lv] = t
        surf = set(np.round(t["color"][:, 1] * 255).astype(int).tolist()) - {0}
        o = tier_object("%s_LOD%d" % (name, lv), t)
        m = tier_material(edir, t["json"], surf, variant_file)
        o.data.materials.append(m)
        objs[lv], mats[lv] = o, m
    lamp_ids = sorted({ln["lamp"] for ln in doc["lamps"]})
    glass_ids = sorted({g["id"] for g in doc["glass"]})
    fmat = false_material(lamp_ids, glass_ids, [w["part"] for w in doc["wheels"]])
    _ground, (bw, bl, fx) = props(cls)
    lo, hi = Vector(doc["bounds"]["min"]), Vector(doc["bounds"]["max"])
    length, height = hi.z - lo.z, hi.y
    centre = (0.0, 0.0, height / 2)
    span = max(bl, length) * 1.25
    # orthographic frames fitted to the plan box, the bay and the figure
    reach_x = max(bw / 2 + 0.1, fx + 0.25)            # the figure stands at +x
    reach_y = max(bl / 2 + 0.1, length / 2, bl / 2 + 0.75)
    tall = max(height, 1.8) + 0.2
    fit = {"side": ortho_fit(2 * reach_y, tall), "front": ortho_fit(2 * reach_x, tall),
           "rear": ortho_fit(2 * reach_x, tall), "top": ortho_fit(2 * reach_y, 2 * reach_x)}
    mid = {"side": (0, 0, tall / 2), "front": (0, 0, tall / 2), "rear": (0, 0, tall / 2),
           "top": (0, 0, 0)}

    def show(level):
        for lv, o in objs.items():
            o.hide_render = lv != level

    def set_paint(level, rgb):
        mats[level].node_tree.nodes["paint"].outputs[0].default_value = (*rgb, 1)

    def gains(level, ids, g=LAMP_GAIN):
        for n in mats[level].node_tree.nodes:
            if n.name.startswith("gain_"):
                k = int(n.name[5:])
                n.outputs[0].default_value = (CABIN_GAIN if k >= 32 else g) if k in ids else 0.0

    frames = []

    def shot(fname, text, dark=False, level=0):
        path = out / fname
        scn.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        label(path, text, dark)
        frames.append({"file": fname, "label": text, "tier": level})
        print("REVIEW", fname, flush=True)
        return path

    me0 = objs[0].data
    co0 = np.zeros(len(me0.vertices) * 3)
    me0.vertices.foreach_get("co", co0)

    def steer(angle):
        co = co0.reshape(-1, 3).copy()
        part = np.round(tiers[0]["color"][:, 0] * 255).astype(int)
        for w in doc["wheels"]:
            if not w["steer"]:
                continue
            sel = part == w["part"]
            g = np.stack([co[sel, 0], co[sel, 2], -co[sel, 1]], axis=1)
            r = vi.steer(g, w["centre"], angle)
            co[sel] = np.stack([r[:, 0], -r[:, 2], r[:, 1]], axis=1)
        me0.vertices.foreach_set("co", co.ravel())
        me0.update()

    # ---- views, day, plain paint (white: the albedo as shipped)
    show(0)
    day(bg, sun)
    set_paint(0, (1, 1, 1))
    gains(0, ())
    for kind, text in (("side", "side (driver's left)"), ("front", "front"), ("rear", "rear"),
                       ("top", "top")):
        view(cam, kind, mid[kind], fit[kind])
        shot("view_%s.png" % kind, text)
    view(cam, "persp", centre, span, az=-35, el=18)
    shot("view_three_quarter.png", "three-quarter, front left")
    # ---- steering
    for angle in (35.0, -35.0):
        steer(angle)
        view(cam, "top", mid["top"], fit["top"])
        shot("steer_%+d_top.png" % angle, "front wheels %+d deg (left turn +), top" % angle)
        view(cam, "persp", (0, -length / 4, height / 3), span, az=-30, el=12, dist=length * 1.2)
        shot("steer_%+d_three_quarter.png" % angle, "front wheels %+d deg" % angle)
    steer(0.0)
    # ---- lamps, one group at a time, at night
    night(bg, sun)
    for k in lamp_ids:
        group = vi.LAMPS[k][0]
        gains(0, (k,))
        where = {ln["position"] for ln in doc["lamps"] if ln["lamp"] == k}
        for face, az in (("front", -35), ("rear", 145)):
            if face == "front" and not where & {"front", "side", "roof"}:
                continue
            if face == "rear" and not where & {"rear", "side", "roof"}:
                continue
            view(cam, "persp", centre, span, az=az, el=15)
            shot("lamp_%02d_%s_%s.png" % (k, group, face), "%d %s, %s" % (k, group, face), True)
    gains(0, NIGHT_SET)
    for face, az in (("front", -35), ("rear", 145)):
        view(cam, "persp", centre, span, az=az, el=15)
        shot("night_%s.png" % face, "night: tail, low beam, brake (%s)" % face, True)
    gains(0, tuple(glass_ids))
    view(cam, "persp", centre, span, az=-60, el=20)
    shot("cabin_lit.png", "cabin lit (glass ids)", True)
    gains(0, ())
    # ---- false colour
    day(bg, sun)
    orig = objs[0].data.materials[0]
    objs[0].data.materials[0] = fmat
    for face, az in (("front", -35), ("rear", 145)):
        view(cam, "persp", centre, span, az=az, el=20)
        shot("ids_%s.png" % face, "ids: wheels blue, lamps in colour, glass cyan, paint light (%s)"
             % face)
    objs[0].data.materials[0] = orig
    # ---- paint
    for pname, rgb in PAINTS.items():
        set_paint(0, rgb)
        view(cam, "persp", centre, span, az=-35, el=18)
        shot("paint_%s.png" % pname, "paint %s via B" % pname.replace("_", " "))
    set_paint(0, (1, 1, 1))
    # ---- tiers at distance
    scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
    cam.data.type = 'PERSP'
    cam.data.sensor_fit = 'VERTICAL'
    cam.data.sensor_height = 24.0
    cam.data.lens = 24.0 / (2 * math.tan(math.radians(TIER_FOV) / 2))
    tier_tiles = []
    for d in DISTANCES:
        row = []
        for lv in vi.LEVELS:
            show(lv)
            set_paint(lv, PAINTS["red"])
            gains(lv, ())
            a = math.radians(-60)
            cam.location = Vector((math.sin(a) * d, -math.cos(a) * d, 1.6 + d * 0.06))
            aim(cam, (0, 0, height / 2))
            bpy.context.view_layer.update()
            pts = [world_to_camera_view(scn, cam, Vector((x, y, z)))
                   for x in (lo.x, hi.x) for y in (-hi.z, -lo.z) for z in (0.0, hi.y)]
            px = [p.x * 1920 for p in pts]
            py = [p.y * 1080 for p in pts]
            long_px = max(px) - min(px)
            m = max(3, int(long_px * 0.12))
            box = (max(0, int(min(px)) - m), max(0, int(min(py)) - m),
                   min(1920, int(max(px)) + m), min(1080, int(max(py)) + m))
            scn.render.use_border = scn.render.use_crop_to_border = True
            scn.render.border_min_x, scn.render.border_min_y = box[0] / 1920, box[1] / 1080
            scn.render.border_max_x, scn.render.border_max_y = box[2] / 1920, box[3] / 1080
            fname = "tier_lod%d_%03dm.png" % (lv, d)
            scn.render.filepath = str(out / fname)
            bpy.ops.render.render(write_still=True)
            frames.append({"file": fname, "label": "LOD%d at %d m, %.0f px across"
                           % (lv, d, long_px), "tier": lv, "distance_m": d,
                           "crop_px": box})
            row.append((out / fname, "LOD%d %d m: %.0f px long, shown x%%d" % (lv, d, long_px)))
            print("REVIEW", fname, flush=True)
        tier_tiles.append(row)
        show(0)
    scn.render.use_border = False
    set_paint(0, (1, 1, 1))

    # ---- contact sheet: 4 columns
    tiles = []
    for f in frames:
        if f["file"].startswith("tier_"):
            continue
        tiles.append(fit_tile(pixels(out / f["file"])))
    with tempfile.TemporaryDirectory() as tmp:
        for row in tier_tiles:
            for path, text in row:
                src = pixels(path)
                k = max(1, min(TILE[0] // src.shape[1], TILE[1] // src.shape[0]))
                text = text % k
                a = fit_tile(src, nearest=True)
                p = Path(tmp) / "t.png"
                img = bpy.data.images.new("t", TILE[0], TILE[1], alpha=False)
                img.pixels.foreach_set(a.ravel())
                img.filepath_raw, img.file_format = str(p), 'PNG'
                img.save()
                bpy.data.images.remove(img)
                label(p, text, True)
                tiles.append(pixels(p))
    cols = 4
    while len(tiles) % cols:
        tiles.append(fit_tile(np.zeros((2, 2, 4), np.float32)))
    rows = [np.concatenate(tiles[i:i + cols], axis=1) for i in range(0, len(tiles), cols)]
    sheet = np.concatenate(rows[::-1], axis=0)
    img = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=False)
    img.pixels.foreach_set(sheet.ravel())
    spath = out / ("%s_review_sheet.png" % name)
    img.filepath_raw, img.file_format = str(spath), 'PNG'
    img.save()
    settings = {"asset": str(adir), "class": cls, "blender": bpy.app.version_string,
                "engine": engine, "variant": args.variant, "paints": PAINTS,
                "lamp_gain": LAMP_GAIN, "cabin_gain": CABIN_GAIN, "night_set": NIGHT_SET,
                "tier_fov_deg": TIER_FOV, "tier_resolution": [1920, 1080],
                "bay_m": [bw, bl], "figure_m": 1.8, "frames": frames, "sheet": spath.name}
    if renderer:
        settings["renderer"] = renderer
    (out / ("%s_review.json" % name)).write_text(json.dumps(settings, indent=1) + "\n")
    print("SHEET", spath)


if __name__ == "__main__":
    if not bpy.app.background:
        raise RuntimeError("run in a separate background Blender; this replaces its scene")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("asset")
    p.add_argument("output")
    p.add_argument("--variant")
    p.add_argument("--cycles", action="store_true", help="Cycles instead of EEVEE")
    p.add_argument("--samples", type=int, default=32)
    p.add_argument("--device", choices=["cpu", "gpu"],
                   help="with --cycles: gpu (the default) renders on the AMD HIP "
                        "device and fails where there is none; cpu on the CPU")
    main(p.parse_args(sys.argv[sys.argv.index("--") + 1:]))
