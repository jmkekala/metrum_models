# SPDX-License-Identifier: GPL-3.0-or-later

"""Render exported assets in a disposable scene for lighting and LOD review.

Run in a separate background Blender process, never in an authoring session:
    blender -b -t 8 -P scripts/review_asset.py -- ASSET_DIR OUTPUT_DIR --day-cycle
    blender -b -t 8 -P scripts/review_asset.py -- ASSET_DIR OUTPUT_DIR \
        --tiers 0 1 2 --distances 65 75 --views front oblique rear --lights noon dusk

The cycle uses one fitted 50-degree vertical-FOV camera, four sun/moon states,
fixed exposure and physically shaded opaque materials. Distance comparisons
use 1920x1080, with distance measured along the view direction to the centre
of the visible front/rear wall. These are authoring scenarios, not game presets.
Optional --texture-dir substitutes temporary mip PNGs without editing exports.
Renders and settings go to OUTPUT_DIR; no source blend or catalog preview saves.

The tiers reference the default variant's albedo. --variant NAME renders
another colour instead: every image named ASSET_albedo_*.png is swapped for
export/ASSET_albedo_NAME.png, and the shared ASSET_orm.png and
ASSET_normal.png for ASSET_orm_NAME.png and ASSET_normal_NAME.png where those
variant-specific maps exist. The variant name is appended to every render's
file name (..._lod0_NAME.png) and recorded in the settings JSON. With
--texture-dir the substituted names are then looked up there in turn:
    blender -b -t 8 -P scripts/review_asset.py -- ASSET_DIR OUTPUT_DIR \
        --six-views --variant yellow_brick
"""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from window_emission import set_imported_state, LIT_FACTOR


# Elevation/azimuth in degrees, sun strength/colour, environment strength.
# The night source is a moon proxy. --emission controls imported window masks.
LIGHTS = {
    'morning': (15, -65, 2.0, (1.0, 0.72, 0.46), 0.25),
    'noon': (60, -35, 3.0, (1.0, 0.95, 0.86), 0.45),
    'dusk': (6, 110, 1.1, (1.0, 0.40, 0.16), 0.10),
    'night': (35, -55, 0.10, (0.48, 0.62, 1.0), 0.025),
    'reverse': (35, 145, 3.0, (1.0, 0.95, 0.86), 0.45),
    'shade': (60, -35, 0.0, (1.0, 1.0, 1.0), 0.45),
}
VIEWS = {'front': (0, 12), 'oblique': (40, 30), 'rear': (150, 30),
         'grazing': (75, 12), 'back': (180, 0), 'left': (-90, 0),
         'right': (90, 0), 'top': (0, 90), 'aerial': (40, 45)}


def direction(azimuth, elevation):
    a, e = map(math.radians, (azimuth, elevation))
    return Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def setup(args):
    if not bpy.app.background:
        raise RuntimeError('Use a separate background process; this replaces its scene.')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.cycles.seed = 42
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.render.resolution_x, scene.render.resolution_y = args.resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1

    world = bpy.data.worlds.new('Review environment')
    world.use_nodes = True
    scene.world = world
    nodes, links = world.node_tree.nodes, world.node_tree.links
    tex = nodes.new('ShaderNodeTexCoord')
    sep = nodes.new('ShaderNodeSeparateXYZ')
    ramp = nodes.new('ShaderNodeValToRGB')
    # A neutral ground hemisphere and blue sky provide view-dependent glass
    # reflections. Their colours are lighting, never written to the albedo.
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.28, 0.29, 0.31, 1)
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (0.38, 0.55, 0.80, 1)
    links.new(tex.outputs['Normal'], sep.inputs[0])
    links.new(sep.outputs['Z'], ramp.inputs[0])
    links.new(ramp.outputs[0], nodes.get('Background').inputs['Color'])
    sun = bpy.data.objects.new('Review sun or moon', bpy.data.lights.new('Review light', 'SUN'))
    scene.collection.objects.link(sun)
    sun.data.angle = math.radians(1)
    cam = bpy.data.objects.new('Review camera', bpy.data.cameras.new('Review camera'))
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.sensor_fit = 'VERTICAL'
    cam.data.sensor_height = 24
    cam.data.lens = 24 / (2 * math.tan(math.radians(25)))
    cam.data.clip_end = 2000

    bpy.ops.mesh.primitive_plane_add(size=2000)
    ground = bpy.context.object
    ground.name = 'Review ground'
    ground.location.z = -0.015
    mat = bpy.data.materials.new('Neutral ground')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.16, 0.17, 0.18, 1)
    bsdf.inputs['Roughness'].default_value = 0.9
    ground.data.materials.append(mat)
    return scene, cam, sun


def load_tiers(args):
    tiers = {}
    for tier in args.tiers:
        path = args.asset / 'export' / f'{args.asset.name}_lod{tier}.glb'
        old = set(bpy.data.objects)
        # Blender 5.2's importer packs images by default, and a packed image
        # ignores a new filepath: --texture-dir would then render the original
        # textures without a word. Keep them external so substitution works.
        kw = {}
        if 'import_pack_images' in bpy.ops.import_scene.gltf.get_rna_type().properties:
            kw['import_pack_images'] = False
        bpy.ops.import_scene.gltf(filepath=str(path), **kw)
        tiers[tier] = [o for o in set(bpy.data.objects) - old if o.type == 'MESH']
        if not tiers[tier]:
            raise RuntimeError(f'No mesh in {path}')
    if args.variant:
        substitute_variant(args.asset, args.variant)
    if args.texture_dir:
        for im in bpy.data.images:
            if im.source == 'FILE':
                replacement = args.texture_dir / Path(bpy.path.abspath(im.filepath)).name
                if not replacement.is_file():
                    raise RuntimeError(f'Missing substitute {replacement}')
                if im.packed_file:
                    raise RuntimeError(f'{im.name} is packed; a substitute would be ignored')
                im.filepath = str(replacement)
                im.reload()
    return tiers


def substitute_variant(asset, variant):
    """Point the imported images at *variant*'s textures in asset/export."""
    name, export = asset.name, asset / 'export'
    albedo = export / f'{name}_albedo_{variant}.png'
    if not albedo.is_file():
        known = sorted(p.name[len(name) + 8:-4] for p in export.glob(f'{name}_albedo_*.png'))
        raise RuntimeError(f'No {albedo.name}; variants here: {", ".join(known)}')
    for im in bpy.data.images:
        if im.source != 'FILE':
            continue
        if im.packed_file:
            raise RuntimeError(f'{im.name} is packed; a substitute would be ignored')
        current = Path(bpy.path.abspath(im.filepath)).name
        if current.startswith(f'{name}_albedo_'):
            replacement = albedo
        elif current in (f'{name}_orm.png', f'{name}_normal.png'):
            replacement = export / current.replace('.png', f'_{variant}.png')
            if not replacement.is_file():
                continue                    # shared by every variant
        else:
            continue
        im.filepath = str(replacement)
        im.reload()


def bounds(objects):
    points = [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
    lo = Vector([min(v[i] for v in points) for i in range(3)])
    hi = Vector([max(v[i] for v in points) for i in range(3)])
    return lo, hi


def main(args):
    args.asset = args.asset.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    scene, cam, sun = setup(args)
    tiers = load_tiers(args)
    lo, hi = bounds(tiers[min(tiers)])
    centre = (lo + hi) / 2
    if args.cycle:
        args.lights = ['morning', 'noon', 'dusk', 'night']
        args.views = ['oblique']
        radius = (hi - lo).length / 2
        args.distances = [radius / math.sin(math.radians(25)) * 1.08]
    if args.six_views:
        args.views = ['front', 'back', 'left', 'right', 'top', 'aerial']
        args.distances = [(hi - lo).length * 2]
        args.lights = ['noon']
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = (hi - lo).length * 1.05
    records = []
    for view in args.views:
        azimuth, elevation = VIEWS[view]
        if args.six_views and view == 'front':
            elevation = 0
        ray = direction(azimuth, elevation)
        # Feature-centred distances avoid conflating orbit-to-pivot with depth.
        target = centre.copy()
        if not args.cycle and not args.six_views:
            target.y = lo.y if ray.y <= 0 else hi.y
        for distance in args.distances:
            cam.location = target + ray * distance
            aim(cam, target)
            bpy.context.view_layer.update()
            crop = None
            if not args.cycle and not args.six_views:
                # Render only the assessed feature area, preserving the full
                # 1080p camera projection and native pixel size in the crop.
                points = [world_to_camera_view(scene, cam, Vector((x, y, z)))
                          for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
                width, height = args.resolution
                crop = [max(0, math.floor(min(p.x for p in points) * width) - 32),
                        max(0, math.floor(min(p.y for p in points) * height) - 32),
                        min(width, math.ceil(max(p.x for p in points) * width) + 32),
                        min(height, math.ceil(max(p.y for p in points) * height) + 32)]
                scene.render.use_border = True
                scene.render.use_crop_to_border = True
                scene.render.border_min_x, scene.render.border_min_y = crop[0] / width, crop[1] / height
                scene.render.border_max_x, scene.render.border_max_y = crop[2] / width, crop[3] / height
            for light in args.lights:
                lit = args.emission == 'on' or (args.emission == 'auto' and light == 'night')
                materials = {m for objects in tiers.values() for obj in objects
                             for m in obj.data.materials if m}
                for material in materials:
                    if any(n.type == 'TEX_IMAGE' and n.image and
                           n.image.name.endswith('_emission.png')
                           for n in material.node_tree.nodes):
                        set_imported_state(material, float(lit))
                elev, az, power, colour, ambient = LIGHTS[light]
                sun.location = direction(az, elev) * 100
                aim(sun, (0, 0, 0))
                sun.data.energy = power
                sun.data.color = colour
                scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value = ambient
                for level in args.tiers:
                    for lv, objects in tiers.items():
                        for obj in objects:
                            obj.hide_render = lv != level
                    state = 'on' if lit else 'off'
                    name = f'{args.asset.name}_{view}_{distance:.1f}m_{light}_emission_{state}_lod{level}'
                    name += f'_{args.variant}.png' if args.variant else '.png'
                    scene.render.filepath = str(args.output / name)
                    if not getattr(args, 'resume', False) or not (args.output / name).exists():
                        bpy.ops.render.render(write_still=True)
                    records.append({'file': name, 'tier': level, 'view': view, 'light': light,
                                    'emission_factor': list(LIT_FACTOR) if lit else [0, 0, 0],
                                    'distance_m': distance, 'target': list(target),
                                    'camera': list(cam.location), 'crop_px_bottom_left': crop})
                    print('REVIEW', name, flush=True)
    settings = {'asset': str(args.asset), 'blender': bpy.app.version_string,
                'renderer': 'Cycles CPU', 'samples': args.samples, 'denoising': True,
                'vertical_fov_degrees': 50, 'resolution': args.resolution,
                'exposure': 0, 'view_transform': 'AgX', 'lights': LIGHTS,
                'projection': cam.data.type, 'orthographic_size': cam.data.ortho_scale,
                'texture_dir': str(args.texture_dir) if args.texture_dir else None,
                'variant': args.variant,
                'renders': records}
    (args.output / f'{args.asset.name}_settings.json').write_text(json.dumps(settings, indent=2) + '\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('asset', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--day-cycle', dest='cycle', action='store_true')
    p.add_argument('--six-views', action='store_true')
    p.add_argument('--resume', action='store_true', help='Reuse matching filenames; only use with identical settings.')
    p.add_argument('--tiers', type=int, nargs='+', default=[0])
    p.add_argument('--distances', type=float, nargs='+', default=[65, 75])
    p.add_argument('--views', nargs='+', choices=VIEWS, default=['front', 'oblique'])
    p.add_argument('--lights', nargs='+', choices=LIGHTS, default=['noon', 'reverse'])
    p.add_argument('--resolution', type=int, nargs=2, default=[1920, 1080])
    p.add_argument('--samples', type=int, default=24)
    p.add_argument('--texture-dir', type=Path)
    p.add_argument('--variant', help='Render this colour variant (export/ASSET_albedo_VARIANT.png) '
                                     'instead of the default the tiers reference.')
    p.add_argument('--emission', choices=['auto', 'on', 'off'], default='auto',
                   help='Default: light candidate windows at night only; game timing stays external.')
    main(p.parse_args(sys.argv[sys.argv.index('--') + 1:]))
