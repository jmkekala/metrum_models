# SPDX-License-Identifier: GPL-2.0-only

"""Keep a GLB's images external: one `uri` each, never a `bufferView` too.

Blender's glTF exporter, asked to keep original texture files, writes each
image with *both* a `uri` and a `bufferView`, and the embedded data is a 1x1
placeholder rather than the real texture. glTF allows exactly one source per
image: strict loaders may take the placeholder and render a flat colour, and
Godot warns and drops the image. Dropping the bufferView keeps the external
reference, so every tier shares one copy of the PNGs in export/.

Run it over each file an asset's export_all() writes:

    from glb_images import strip_embedded_images
    strip_embedded_images(path)

Standard library only; changes the JSON chunk and never touches mesh buffers.
"""

import json
import struct

GLB_MAGIC = 0x46546C67
JSON_CHUNK = 0x4E4F534A


def strip_embedded_images(path):
    """Remove `bufferView`/`mimeType` from images that also carry a `uri`.

    Returns True if the file was rewritten, False if it was already clean.
    """
    with open(path, "rb") as fh:
        data = fh.read()
    magic, version, total = struct.unpack("<III", data[:12])
    if magic != GLB_MAGIC or version != 2 or total != len(data):
        raise ValueError("%s: not a glTF 2.0 binary" % path)
    off, chunks = 12, []
    while off < total:
        clen, ctype = struct.unpack("<II", data[off:off + 8])
        chunks.append([ctype, data[off + 8:off + 8 + clen]])
        off += 8 + clen

    changed = False
    for chunk in chunks:
        if chunk[0] != JSON_CHUNK:
            continue
        js = json.loads(chunk[1].decode("utf-8"))
        for img in js.get("images", []):
            if "uri" in img and "bufferView" in img:
                del img["bufferView"]
                img.pop("mimeType", None)      # only required with bufferView
                changed = True
        if changed:
            chunk[1] = json.dumps(js, separators=(",", ":")).encode("utf-8")
    if not changed:
        return False

    out = b""
    for ctype, payload in chunks:
        pad = (4 - len(payload) % 4) % 4
        payload += (b" " if ctype == JSON_CHUNK else b"\x00") * pad
        out += struct.pack("<II", len(payload), ctype) + payload
    with open(path, "wb") as fh:
        fh.write(struct.pack("<III", GLB_MAGIC, 2, 12 + len(out)) + out)
    return True
