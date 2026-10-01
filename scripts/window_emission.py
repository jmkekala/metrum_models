# SPDX-License-Identifier: GPL-2.0-only

"""Shared window emission wiring and GLB emission state; no asset artwork.

scripts/asset_build.py exports every tier lit and then calls
rewrite_glb_emission() to ship it with its lights off.
"""

import json
from pathlib import Path
import struct

import bpy


LIT_FACTOR = (1.0, 0.55, 0.23)  # linear RGB, warm reference; game may replace


def attach(material, export_dir, asset, tint=LIT_FACTOR):
    """Wire a linked, neutral glazing mask; authoring starts with lights off.

    *tint* is the asset's reference lit factor, for previews only: the export
    rewrites the glTF factor to zero either way. A shop's fluorescent interior
    is far cooler than a living-room bulb, so a type whose windows are a lit
    sales floor passes its own factor rather than the residential default.
    """
    nt = material.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    path = str(Path(export_dir) / f'{asset}_emission.png')
    image = bpy.data.images.load(path, check_existing=True)
    image.colorspace_settings.name = 'sRGB'
    image.filepath = bpy.path.relpath(path) if bpy.data.filepath else path
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.name = 'Window emission mask'
    tex.label = 'Candidate glazing; shared by every colour and LOD'
    tex.location = (-650, -550)
    tex.image = image
    tex.interpolation = 'Linear'
    tex.extension = 'REPEAT'
    tint_rgb = tint
    tint = nt.nodes.new('ShaderNodeMixRGB')
    tint.name = 'Window emission tint'
    tint.blend_type = 'MULTIPLY'
    tint.inputs[0].default_value = 1.0
    tint.inputs[2].default_value = (*tint_rgb, 1.0)
    tint.location = (-280, -550)
    nt.links.new(tex.outputs['Color'], tint.inputs[1])
    nt.links.new(tint.outputs[0], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 0.0


def set_state(material, strength, tint=LIT_FACTOR):
    nt = material.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Emission Strength'].default_value = strength
    nt.nodes['Window emission tint'].inputs[2].default_value = (*tint, 1.0)


def set_imported_state(material, strength):
    """Simulate a runtime RGB-factor change on a reimported default-off GLB.

    Preserve the imported texture and UV binding; do not attach a replacement.
    Blender imports a zero RGB factor as zero Principled emission strength.
    """
    nt = material.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    socket = bsdf.inputs['Emission Color']
    tint = nt.nodes.get('Review runtime emission factor')
    if tint is None:
        if len(socket.links) != 1:
            raise RuntimeError(f'Missing imported emission binding: {material.name}')
        source = socket.links[0].from_socket
        if source.node.type != 'TEX_IMAGE' or not source.node.image.name.endswith('_emission.png'):
            raise RuntimeError(f'Unexpected imported emission input: {material.name}')
        tint = nt.nodes.new('ShaderNodeMixRGB')
        tint.name = 'Review runtime emission factor'
        tint.blend_type = 'MULTIPLY'
        tint.inputs[0].default_value = 1.0
        nt.links.new(source, tint.inputs[1])
        nt.links.new(tint.outputs[0], socket)
    tint.inputs[2].default_value = (*LIT_FACTOR, 1.0)
    bsdf.inputs['Emission Strength'].default_value = strength


def rewrite_glb_emission(path, factor):
    """Keep the exported texture while setting the core glTF RGB factor.

    Exporting a positive reference state prevents exporter optimizations
    dropping unused textures. Changing JSON here never touches mesh buffers.
    Also used by validation to emulate a consumer's material state change.
    """
    path = Path(path)
    raw = path.read_bytes()
    magic, version, total = struct.unpack_from('<III', raw)
    assert magic == 0x46546C67 and version == 2 and total == len(raw)
    chunks, offset, found = [], 12, False
    while offset < total:
        size, kind = struct.unpack_from('<II', raw, offset)
        payload = raw[offset + 8:offset + 8 + size]
        if kind == 0x4E4F534A:
            doc = json.loads(payload)
            for material in doc.get('materials', []):
                if 'emissiveTexture' in material:
                    material['emissiveFactor'] = list(factor)
                    assert 'KHR_materials_emissive_strength' not in material.get('extensions', {})
                    found = True
            payload = json.dumps(doc, separators=(',', ':')).encode()
            payload += b' ' * (-len(payload) % 4)
        chunks.append(struct.pack('<II', len(payload), kind) + payload)
        offset += size + 8
    if not found:
        raise RuntimeError(f'Exporter lost emissiveTexture: {path}')
    body = b''.join(chunks)
    path.write_bytes(struct.pack('<III', magic, version, len(body) + 12) + body)
