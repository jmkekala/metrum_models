# SPDX-License-Identifier: GPL-3.0-or-later

"""The vehicle contract's numbers, and the per-vertex ids as they ship.

One source of truth for the build (scripts/vehicle_build.py), the sidecar
(scripts/model_facts.py), the validator (scripts/vehicle_checks.py) and the
review sheet (scripts/review_vehicle.py): the body classes and their boxes,
tier ceilings and texture sizes, the part, lamp and glass id tables, the
COLOR_0 encoding, a GLB reader for the accessors the checks need, and the
post-export pass that rewrites COLOR_0 as exact bytes.

The ids (CLAUDE.md, Vehicles): one colour attribute per tier, COLOR_0,

    R  part     0 body; 1.. the wheel parts, in sidecar order (at most 8)
    G  surface  0 plain; 1..15 a lamp (LAMPS); 32..47 glass (GLASS)
    B  paint    1 on painted body panels, 0 elsewhere
    A  unused   1

authored as a FLOAT_COLOR attribute on the face corners, (part / 255,
surface / 255, paint, 1.0) on every corner of a polygon. Blender's exporter
writes it as normalised UNSIGNED_SHORT, id n as exactly n * 257;
convert_color0_to_ubyte() rewrites it as normalised UNSIGNED_BYTE VEC4, id n
as the byte n, B 0 or 255, A 255. That byte form is what ships.

Frames: the build frame is Blender's (metres, Z up, front toward -Y); the
exported frame glTF's (+Y up, nose toward +Z). Blender (x, y, z) is glTF
(x, z, -y). In both, +X is the driver's left.

numpy only at module level; Pillow is imported where a PNG is read or
written. Runs in Blender's Python and in a system Python alike.

    python3 scripts/vehicle_ids.py FILE.glb     # the COLOR_0 accessor and its ids
"""

import json
import math
import struct
import sys

import numpy as np

# ================================================================ classes
# Box (length, width, height) in metres, a hard limit for the straight-ahead
# model; width without mirrors. mirror: what mirrors may add a side.
# ceilings: LOD0..LOD3 triangles. texture: the atlas size.
CLASSES = {
    "car": {"box": (4.50, 1.80, 1.95), "mirror": 0.12, "texture": 512,
            "ceilings": (3000, 900, 220, 40), "bay": (2.5, 5.0)},
    "van": {"box": (6.00, 2.10, 2.70), "mirror": 0.25, "texture": 512,
            "ceilings": (3500, 1000, 260, 40), "bay": (3.0, 8.0)},
    "truck": {"box": (8.00, 2.55, 3.80), "mirror": 0.25, "texture": 1024,
              "ceilings": (4500, 1400, 350, 60), "bay": (3.0, 8.0)},
    "bus": {"box": (12.00, 2.55, 3.20), "mirror": 0.25, "texture": 1024,
            "ceilings": (4500, 1400, 350, 60), "bay": (3.0, 13.0)},
}
LEVELS = (0, 1, 2, 3)
SIZE_TOL = 0.05          # a size's tolerance round its target, metres
WHEEL_SIDES = {0: (16, 20), 1: (8, 10)}   # sides of a wheel part, per tier
MAX_WHEELS = 8
STEER_DEG = 35.0         # front wheels turned either way, for the arch check
CLEARANCE = 0.010        # nearest a turned wheel vertex may come to the body
CYLINDER_TOL = 0.005     # a wheel vertex's reach past its sidecar cylinder
MIRROR_TOL = 0.001       # wheel and lamp pairs mirror in x within this
GROUND_TOL = 0.001

# ================================================================ id tables
PART_BODY = 0
LAMPS = {    # id: (group, lit colour, where)
    1: ("tail", "red", "rear, both sides"),
    2: ("brake", "red", "rear, both sides, and a car's high-mounted lamp"),
    3: ("tail_brake", "red", "a rear lens that is both"),
    4: ("indicator_left", "amber", "front, rear and side repeater, left"),
    5: ("indicator_right", "amber", "front, rear and side repeater, right"),
    6: ("reverse", "white", "rear"),
    7: ("low_beam", "white", "front, both sides"),
    8: ("high_beam", "white", "front, both sides"),
    9: ("daytime", "white", "front, both sides"),
    10: ("fog_front", "white", "optional"),
    11: ("fog_rear", "red", "optional"),
    12: ("plate", "white", "rear plate lamp, optional"),
    13: ("beacon", "livery", "roof; reserved"),
    14: ("sign", "livery", "taxi sign, bus destination board; reserved"),
    15: ("marker", "amber, white, red", "truck and bus outline lamps"),
}
GLASS = {    # id: group
    32: "glass_windscreen", 33: "glass_front_side", 34: "glass_rear_side",
    35: "glass_rear", 36: "glass_roof", 37: "glass_cab_rear",
    38: "glass_saloon", 39: "glass_door",
}
GLASS_RESERVED = range(40, 48)
LAMP_IDS = range(1, 16)
GLASS_IDS = range(32, 48)
LAMP_GROUP = {g: i for i, (g, _, _) in LAMPS.items()}
GLASS_GROUP = {g: i for i, g in GLASS.items()}
# The lamp whose mirror image is another group (the indicators); every
# other group mirrors onto itself.
MIRROR_GROUP = {4: 5, 5: 4}
# Groups a vehicle may carry as a single lens off the centre line (a rear
# fog lamp on the driver's side, one reverse lamp); every other lens off the
# centre line has a mirrored partner.
SINGLE_OK = (6, 11, 12, 13, 14)

# Required lamp ids: every class has these, and tail plus brake either as
# tail_brake (3) or as separate tail (1) and brake (2) lenses.
LAMPS_ALL = (4, 5, 6, 7, 8, 9)
LAMPS_CLASS = {"car": (2,), "van": (), "truck": (15,), "bus": ()}
# Required glass ids. car and truck are the contract's; van and bus are this
# repository's reading of it (a cab has a windscreen and side glass).
GLASS_CLASS = {"car": (32, 33, 34, 35), "van": (32, 33), "truck": (32, 33),
               "bus": (32,)}
POSITIONS = ("front", "rear", "side", "roof")
SIDES = ("left", "right", "centre")
SIDE_X = 0.01            # |x| under this is a centre lamp

# Suggested lens colours for an atlas, sRGB: unlit in the albedo, lit in
# the emission. An asset may tune them; the validator only asks that a lit
# lens is not black.
LENS_UNLIT = {"red": (92, 24, 22), "amber": (120, 70, 18), "white": (150, 152, 150)}
LENS_LIT = {"red": (255, 34, 22), "amber": (255, 132, 10), "white": (255, 248, 236)}


def lamp_colour(lamp_id):
    """The lit colour word of a lamp id: red, amber or white (livery and
    marker lamps fall back to white; their colour is the asset's)."""
    word = LAMPS[lamp_id][1]
    return word if word in LENS_LIT else "white"


def required_lamps(body_class, present):
    """The required lamp ids missing from *present* (a set of ids)."""
    need = set(LAMPS_ALL) | set(LAMPS_CLASS[body_class])
    missing = sorted(need - set(present))
    if 3 not in present and not {1, 2} <= set(present):
        missing.append("3 (or 1 and 2)")
    return missing


def required_glass(body_class, present):
    return sorted(set(GLASS_CLASS[body_class]) - set(present))


# ================================================================ encoding
ID_ATTRIBUTE = "metrum_ids"          # the authored FLOAT_COLOR, exported as COLOR_0


def encode(part, surface, paint):
    """The authored float colour of one polygon's corners."""
    if not 0 <= part <= MAX_WHEELS:
        raise ValueError("part %r is not 0..%d" % (part, MAX_WHEELS))
    if not (surface == 0 or surface in LAMP_IDS or surface in GLASS_IDS):
        raise ValueError("surface %r is not 0, 1..15 or 32..47" % surface)
    if surface and (part or paint):
        raise ValueError("a lamp or glass face is body with paint 0 "
                         "(part %r, surface %r, paint %r)" % (part, surface, paint))
    return (part / 255.0, surface / 255.0, 1.0 if paint else 0.0, 1.0)


def surface_kind(g):
    if g == 0:
        return "plain"
    if g in LAMP_IDS:
        return "lamp"
    if g in GLASS_IDS:
        return "glass"
    return "unused"


# ================================================================ GLB
GLB_MAGIC = 0x46546C67
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942
ARRAY_BUFFER = 34962
UBYTE, USHORT, UINT, FLOAT = 5121, 5123, 5125, 5126
_DTYPE = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16,
          5125: np.uint32, 5126: np.float32}
_NORM = {5120: 127.0, 5121: 255.0, 5122: 32767.0, 5123: 65535.0}
_NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
CT_NAME = {5120: "BYTE", 5121: "UNSIGNED_BYTE", 5122: "SHORT",
           5123: "UNSIGNED_SHORT", 5125: "UNSIGNED_INT", 5126: "FLOAT"}


def read_glb(path):
    """(json dict, BIN chunk bytes) of a glTF 2 binary."""
    with open(path, "rb") as fh:
        data = fh.read()
    magic, version, total = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC or version != 2 or total != len(data):
        raise ValueError("%s: not a glTF 2.0 binary" % path)
    off, js, bin_ = 12, None, b""
    while off < total:
        clen, ctype = struct.unpack_from("<II", data, off)
        payload = data[off + 8:off + 8 + clen]
        if ctype == JSON_CHUNK:
            js = json.loads(payload.decode("utf-8"))
        elif ctype == BIN_CHUNK:
            bin_ = payload
        off += 8 + clen
    return js, bin_


def write_glb(path, js, bin_):
    jb = json.dumps(js, separators=(",", ":")).encode("utf-8")
    jb += b" " * (-len(jb) % 4)
    out = struct.pack("<II", len(jb), JSON_CHUNK) + jb
    if bin_:
        bb = bytes(bin_) + b"\x00" * (-len(bin_) % 4)
        out += struct.pack("<II", len(bb), BIN_CHUNK) + bb
    with open(path, "wb") as fh:
        fh.write(struct.pack("<III", GLB_MAGIC, 2, 12 + len(out)) + out)


def accessor(js, bin_, index, normalise=True):
    """An accessor as a (count, components) numpy array; normalised integer
    accessors become floats when *normalise*, otherwise their raw integers."""
    acc = js["accessors"][index]
    if "sparse" in acc or "bufferView" not in acc:
        raise ValueError("accessor %d: sparse or absent data is not read here" % index)
    dt = np.dtype(_DTYPE[acc["componentType"]]).newbyteorder("<")
    n = _NCOMP[acc["type"]]
    bv = js["bufferViews"][acc["bufferView"]]
    size = dt.itemsize * n
    stride = bv.get("byteStride", size)
    base = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    if stride == size:
        a = np.frombuffer(bin_, dt, count * n, base).reshape(count, n)
    else:
        rows = np.frombuffer(bin_, np.uint8, stride * (count - 1) + size, base)
        a = np.lib.stride_tricks.as_strided(rows, (count, size), (stride, 1))
        a = np.ascontiguousarray(a).view(dt).reshape(count, n)
    if normalise and acc.get("normalized"):
        return np.maximum(a.astype(np.float64) / _NORM[acc["componentType"]], -1.0)
    return a.copy()


def tier(path):
    """Everything the checks read from one exported tier, concatenated over
    its primitives in file order: positions and normals (glTF frame),
    triangles as vertex indices, COLOR_0 as decoded floats, its accessor's
    encoding, the first UV set, and the JSON. Raises on a file the contract excludes (no
    COLOR_0, a node transform, a primitive that is not a triangle list)."""
    js, bin_ = read_glb(path)
    for node in js.get("nodes", []):
        if any(k in node for k in ("matrix", "translation", "rotation", "scale")):
            raise ValueError("%s: node %r carries a transform" % (path, node.get("name")))
    pos, tri, col, uv, nrm, enc, base = [], [], [], [], [], [], 0
    for mesh in js.get("meshes", []):
        for prim in mesh["primitives"]:
            if prim.get("mode", 4) != 4:
                raise ValueError("%s: a primitive is not a triangle list" % path)
            attrs = prim["attributes"]
            p = accessor(js, bin_, attrs["POSITION"]).astype(np.float64)
            if "indices" in prim:
                ix = accessor(js, bin_, prim["indices"], False).reshape(-1)
            else:
                ix = np.arange(len(p))
            if "COLOR_0" not in attrs:
                raise ValueError("%s: a primitive has no COLOR_0" % path)
            acc = js["accessors"][attrs["COLOR_0"]]
            c = accessor(js, bin_, attrs["COLOR_0"])
            if c.shape[1] == 3:
                c = np.concatenate([c, np.ones((len(c), 1))], axis=1)
            enc.append((CT_NAME[acc["componentType"]], bool(acc.get("normalized")),
                        acc["type"]))
            t = accessor(js, bin_, attrs["TEXCOORD_0"]) if "TEXCOORD_0" in attrs \
                else np.zeros((len(p), 2))
            nrm.append(accessor(js, bin_, attrs["NORMAL"]).astype(np.float64)
                       if "NORMAL" in attrs else np.zeros_like(p))
            pos.append(p)
            col.append(np.asarray(c, np.float64))
            uv.append(np.asarray(t, np.float64))
            tri.append(ix.reshape(-1, 3).astype(np.int64) + base)
            base += len(p)
    if not pos:
        raise ValueError("%s: no mesh" % path)
    return {"positions": np.concatenate(pos), "triangles": np.concatenate(tri),
            "color": np.concatenate(col), "uv": np.concatenate(uv),
            "normals": np.concatenate(nrm), "encoding": sorted(set(enc)), "json": js}


def decode(color, tol=0.002):
    """Per-vertex ids from COLOR_0 floats: (part, surface, paint) integer
    arrays, and the largest distance of R or G * 255 from a whole number.
    paint is 1 where B rounds to 1."""
    r, g = color[:, 0] * 255.0, color[:, 1] * 255.0
    off = float(max(np.abs(r - np.round(r)).max(initial=0.0),
                    np.abs(g - np.round(g)).max(initial=0.0)))
    return (np.round(r).astype(int), np.round(g).astype(int),
            np.round(color[:, 2]).astype(int), off)


# ============================================================ COLOR_0 bytes
def convert_color0_to_ubyte(src, dst=None, attribute="COLOR_0", tol=1e-3):
    """Rewrite *attribute* on every primitive as normalised UNSIGNED_BYTE
    VEC4, exactly: each component times 255 must lie within *tol* of a whole
    byte (an id bent on its way, by a BYTE_COLOR attribute's sRGB round trip
    or an interpolating modifier, fails here instead of rounding silently).
    The BIN chunk is repacked: the old views dropped, every kept view on a
    4-byte boundary. Returns a report dict; raises ValueError.

    Blender 5.3's exporter writes the FLOAT_COLOR ids as normalised
    UNSIGNED_SHORT VEC4, id n as n * 257, so the conversion is lossless."""
    dst = dst or src
    js, bin_ = read_glb(src)
    for ext in ("KHR_draco_mesh_compression", "EXT_meshopt_compression",
                "KHR_meshopt_compression"):
        if ext in js.get("extensionsUsed", []):
            raise ValueError("%s: %s is not supported" % (src, ext))
    targets = sorted({p["attributes"][attribute] for m in js.get("meshes", [])
                      for p in m["primitives"] if attribute in p["attributes"]})
    report = {"accessors": [], "worst_offgrid": 0.0}
    new = {}
    for ai in targets:
        acc = js["accessors"][ai]
        if acc["type"] not in ("VEC3", "VEC4"):
            raise ValueError("accessor %d: %s is not a colour" % (ai, acc["type"]))
        if acc["componentType"] == UBYTE and acc.get("normalized") and acc["type"] == "VEC4":
            continue
        if acc["componentType"] != FLOAT and not acc.get("normalized"):
            raise ValueError("accessor %d: an integer COLOR_0 must be normalised" % ai)
        v = accessor(js, bin_, ai)
        if v.shape[1] == 3:
            v = np.concatenate([v, np.ones((len(v), 1))], axis=1)
        s = np.clip(v, 0.0, 1.0) * 255.0
        q = np.floor(s + 0.5)
        off = np.abs(s - q)
        worst = float(off.max(initial=0.0))
        report["worst_offgrid"] = max(report["worst_offgrid"], worst)
        if worst > tol:
            i, ch = np.unravel_index(int(np.argmax(off)), off.shape)
            raise ValueError("accessor %d: vertex %d component %d is %.6f, %.4f off "
                             "a whole byte" % (ai, i, ch, v[i, ch], worst))
        new[ai] = q.astype(np.uint8).tobytes()
        report["accessors"].append({"index": ai, "was": [CT_NAME[acc["componentType"]],
                                                         acc["type"]],
                                    "count": acc["count"]})
    if not new:
        return report
    views = js["bufferViews"]
    for ai, data in new.items():
        acc = js["accessors"][ai]
        views.append({"buffer": 0, "byteLength": len(data), "target": ARRAY_BUFFER,
                      "_data": data})
        acc["bufferView"] = len(views) - 1
        acc.pop("byteOffset", None)
        acc.update(componentType=UBYTE, normalized=True, type="VEC4")
        acc.pop("min", None)
        acc.pop("max", None)
    refs = {a["bufferView"] for a in js.get("accessors", []) if "bufferView" in a}
    refs |= {i["bufferView"] for i in js.get("images", []) if "bufferView" in i}
    if any("sparse" in a for a in js.get("accessors", [])):
        raise ValueError("%s: sparse accessors are not supported" % src)
    remap, kept, blob = {}, [], bytearray()
    for i, bv in enumerate(views):
        if i not in refs:
            continue
        if bv.get("buffer", 0) != 0:
            raise ValueError("%s: more than one buffer" % src)
        data = bv.pop("_data", None)
        if data is None:
            start = bv.get("byteOffset", 0)
            data = bin_[start:start + bv["byteLength"]]
        blob += b"\x00" * (-len(blob) % 4)
        bv["byteOffset"] = len(blob)
        blob += data
        remap[i] = len(kept)
        kept.append(bv)
    blob += b"\x00" * (-len(blob) % 4)
    for a in js.get("accessors", []):
        if "bufferView" in a:
            a["bufferView"] = remap[a["bufferView"]]
    for im in js.get("images", []):
        if "bufferView" in im:
            im["bufferView"] = remap[im["bufferView"]]
    js["bufferViews"] = kept
    js["buffers"][0]["byteLength"] = len(blob)
    write_glb(dst, js, blob)
    report["bin_bytes"] = [len(bin_), len(blob)]
    return report


def color0_report(path):
    """The COLOR_0 accessor of a tier as shipped: encoding, vertex count and
    bytes, and the ids it holds."""
    t = tier(path)
    part, surf, paint, off = decode(t["color"])
    acc = [t["json"]["accessors"][p["attributes"]["COLOR_0"]]
           for m in t["json"]["meshes"] for p in m["primitives"]]
    nbytes = sum(a["count"] * _NCOMP[a["type"]] * np.dtype(_DTYPE[a["componentType"]]).itemsize
                 for a in acc)
    return {"encoding": t["encoding"], "vertices": len(t["positions"]),
            "triangles": len(t["triangles"]), "color0_bytes": int(nbytes),
            "worst_offgrid": off, "parts": sorted(set(part.tolist())),
            "surfaces": sorted(set(surf.tolist())), "paint": sorted(set(paint.tolist()))}


# ================================================================ geometry
def to_gltf(p):
    """Build-frame point (Blender) to the exported frame."""
    return (p[0], p[2], -p[1])


def to_build(p):
    return (p[0], -p[2], p[1])


def steer(points, centre, angle_deg):
    """*points* (n, 3, glTF frame) turned *angle_deg* about the vertical
    axis through *centre*. Positive turns the nose (+Z) toward +X, the
    driver's left: a left turn."""
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    d = np.asarray(points, np.float64) - np.asarray(centre, np.float64)
    out = np.empty_like(d)
    out[:, 0] = c * d[:, 0] + s * d[:, 2]
    out[:, 1] = d[:, 1]
    out[:, 2] = -s * d[:, 0] + c * d[:, 2]
    return out + np.asarray(centre, np.float64)


def lens_axes(facing):
    """The lens rectangle's (width, height) axes in the glTF frame for a
    unit outward *facing*: width horizontal (up x facing), height the third
    axis (facing x width). A lens facing straight up or down takes width
    along +X."""
    f = np.asarray(facing, np.float64)
    f = f / np.linalg.norm(f)
    u = np.cross((0.0, 1.0, 0.0), f)
    if np.linalg.norm(u) < 1e-6:
        u = np.array((1.0, 0.0, 0.0))
    u /= np.linalg.norm(u)
    v = np.cross(f, u)
    return u, v / np.linalg.norm(v)


def lens_position(facing):
    """front, rear, side or roof from an outward facing (glTF frame)."""
    fx, fy, fz = facing
    k = int(np.argmax(np.abs((fx, fy, fz))))
    if k == 2:
        return "front" if fz > 0 else "rear"
    if k == 0:
        return "side"
    if fy > 0:
        return "roof"
    raise ValueError("a lamp faces down: %s" % (facing,))


def lens_side(x):
    return "left" if x > SIDE_X else "right" if x < -SIDE_X else "centre"


# ================================================================ glass texels
GLASS_TEXELS = "glass_texels.png"    # beside notes.md, never in export/


def save_glass_texels(mask, path):
    """Write the atlas's glass texels: *mask* is (size, size) bool, V up as
    an atlas is painted (row 0 at the bottom); stored as an 8-bit grey PNG,
    255 on glass, rows top-down like every atlas PNG."""
    from PIL import Image
    a = np.flipud(np.asarray(mask, bool)).astype(np.uint8) * 255
    Image.fromarray(a, mode="L").save(path, optimize=True)
    return path


def load_glass_texels(path):
    """The glass texel mask, rows top-down as the PNG (and an image's
    pixel rows) are stored; True on glass."""
    from PIL import Image
    a = np.asarray(Image.open(path).convert("L"))
    if set(np.unique(a).tolist()) - {0, 255}:
        raise ValueError("%s holds values other than 0 and 255" % path)
    return a == 255


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(p, json.dumps(color0_report(p)))
