# SPDX-License-Identifier: GPL-3.0-or-later

"""Reproducible variant contact sheets: day/night for any window-emitting
asset, day only for an unlit one (asset_build.Asset.render_variants())."""

from pathlib import Path
import tempfile

import blf
import bpy
from bpy_extras.object_utils import world_to_camera_view
import imbuf
import numpy as np

from window_emission import LIT_FACTOR, set_state


def render_sheet(asset, here, variants, get_material, preview_studio, show_only,
                 tile_w=640, tint=None, with_night=True):
    """Colours in columns; day above night. Fixed camera and exposure.

    *tint* is the asset's reference lit factor; the catalog's warm default is
    used when an asset does not state one of its own. with_night=False is
    for an asset with no emission (night_lit=False): one day row, each panel
    labelled with its variant's name alone, and no emission state touched.
    """
    tint = LIT_FACTOR if tint is None else tint
    scn = bpy.context.scene
    cam = preview_studio()
    show_only(0)
    obj = bpy.data.objects[f'{asset}_LOD0']
    bpy.context.view_layer.update()
    pts = [world_to_camera_view(scn, cam, obj.matrix_world @ v.co)
           for v in obj.data.vertices]
    x0 = max(0.0, min(p.x for p in pts) - 0.06)
    x1 = min(1.0, max(p.x for p in pts) + 0.06)
    w, h = scn.render.resolution_x, scn.render.resolution_y
    scale = tile_w / (w * (x1 - x0))
    rw, rh = round(w * scale), round(h * scale)
    c0 = min(round(rw * x0), rw - tile_w)
    saved = (scn.render.engine, scn.render.filepath, scn.cycles.samples,
             scn.cycles.use_denoising, scn.cycles.seed)
    bg = next(n for n in scn.world.node_tree.nodes if n.type == 'BACKGROUND')
    sun = bpy.data.objects['StudioSun']
    day = (tuple(bg.inputs[0].default_value), bg.inputs[1].default_value,
           sun.data.energy, tuple(sun.data.color))
    scn.render.engine = 'CYCLES'
    scn.cycles.samples = 48
    scn.cycles.use_denoising = True
    scn.cycles.seed = 42
    scn.render.resolution_x, scn.render.resolution_y = rw, rh
    rows = []
    try:
        with tempfile.TemporaryDirectory(prefix=asset + '_variants_') as tmp:
            rows_of = (False, True) if with_night else (False,)
            for night in rows_of:
                bg.inputs[0].default_value = (0.24, 0.32, 0.50, 1) if night else day[0]
                bg.inputs[1].default_value = 0.08 if night else day[1]
                sun.data.energy = 0.12 if night else day[2]
                sun.data.color = (0.48, 0.62, 1.0) if night else day[3]
                tiles = []
                for variant in variants:
                    material = get_material(variant)
                    if with_night:
                        set_state(material, float(night), tint)
                    path = str(Path(tmp) / f'{variant}_{night}.png')
                    scn.render.filepath = path
                    bpy.ops.render.render(write_still=True)
                    ib = imbuf.load(path)
                    with blf.bind_imbuf(0, ib):
                        blf.size(0, max(14, rh // 25))
                        blf.color(0, *((0.86, 0.89, 0.96, 1) if night else (0.08, 0.08, 0.08, 1)))
                        blf.position(0, c0 + 14, rh - rh // 14, 0)
                        label = variant.replace('_', ' ')
                        if with_night:
                            label += ' / NIGHT' if night else ' / DAY'
                        blf.draw_buffer(0, label)
                    imbuf.write(ib, filepath=path)
                    image = bpy.data.images.load(path, check_existing=False)
                    px = np.array(image.pixels[:], np.float32).reshape(rh, rw, 4)
                    bpy.data.images.remove(image)
                    tiles.append(px[:, c0:c0 + tile_w])
                rows.append(np.concatenate(tiles, axis=1))
        # Blender pixel rows start at bottom, so concatenate night before day.
        sheet = np.concatenate(rows[::-1], axis=0)
        out = bpy.data.images.new(asset + '_variants', sheet.shape[1], sheet.shape[0], alpha=False)
        out.pixels.foreach_set(sheet.ravel())
        path = str(Path(here) / 'variants.png')
        out.filepath_raw, out.file_format = path, 'PNG'
        out.save()
        bpy.data.images.remove(out)
        return path
    finally:
        get_material(variants[0])  # reset to default colour and emission off
        bg.inputs[0].default_value, bg.inputs[1].default_value = day[:2]
        sun.data.energy, sun.data.color = day[2:]
        scn.render.resolution_x, scn.render.resolution_y = w, h
        (scn.render.engine, scn.render.filepath, scn.cycles.samples,
         scn.cycles.use_denoising, scn.cycles.seed) = saved
