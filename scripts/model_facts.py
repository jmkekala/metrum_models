# SPDX-License-Identifier: GPL-3.0-or-later

"""The geometry facts sidecar, export/<asset_name>.model.json.

One JSON file beside an asset's exported tiers that states, in the frame of
those .glb files, what a consumer would otherwise have to measure or guess:
where the outer walls stand, where the doors are, how many storeys and
dwellings the shell stands for, and the hash of every file it describes.
Geometry and files only: it names no consumer concept.

Frame: metres, glTF as exported (right-handed, +Y up, +Z front, origin at the
asset's pivot). A build.py states its facts in its own build frame (Blender,
Z up, front toward -Y, before the pivot is applied) and compose() converts:
a build point (bx, by, bz) with pivot offset (px, py, pz) is
[bx - px, bz - pz, -(by - py)]; a plan point is the [x, z] of that.

A build.py declares:

    def facts():
        return {
            "hero": False,
            "dwellings": 1,
            "footprint": [(x, y), ...],          # outer wall outline, build frame
            "storeys": [(floor_z, area_m2), ...],  # occupied storeys, lowest first
            "doors": [model_facts.wall_door("front", p0, p1, s, z, w, h, main=True)],
        }

and asset_build.Asset.write_facts() adds everything that is read from the
build and the exported files. Triangle counts and bounds are read from the
.glb files themselves, so the sidecar describes what ships.

Pure Python, no bpy: scripts/validate_asset.py runs check() on what is on disk.
"""

import hashlib
import json
import math
import os
import struct
import subprocess

SCHEMA = "metrum-model-facts"
VERSION = 1
LICENSE = "CC-BY-4.0"
DECIMALS = 4                     # 0.1 mm; the build's own weld is 0.01 mm
DOOR_TOL = 0.05                  # a door's distance from a footprint edge, metres
KEYS = ("schema", "version", "name", "path", "source", "license", "bounds",
        "footprint", "storeys", "dwellings", "doors", "lods", "textures",
        "variants", "default_variant", "preview", "hero")
DOOR_KEYS = ("id", "position", "facing", "width_m", "height_m", "main")


def _r(x):
    """Rounded, with no negative zero."""
    return round(float(x), DECIMALS) + 0.0


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def sidecar_path(here, name):
    return os.path.join(here, "export", name + ".model.json")


# ------------------------------------------------------------ build frame
def wall_door(door_id, p0, p1, s, z, width, height, main=False):
    """A door in the wall from plan point *p0* to *p1*, in the build frame.

    The catalog's walls run counter-clockwise seen from above, so the outward
    normal is on the right of p0 -> p1. *s* is the door's centre along the
    wall from p0 and *z* its threshold; the position is on the outer wall
    plane whatever the reveal's depth. *width* and *height* are the leaf's
    (or the pair's) clear opening, without casing, fanlight or transom.
    """
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    tx, ty = dx / length, dy / length
    return {"id": door_id,
            "position": (p0[0] + tx * s, p0[1] + ty * s, z),
            "facing": (ty, -tx),
            "width_m": width, "height_m": height, "main": bool(main)}


def roof_clear_width(span, z_floor, z_eave, tan, headroom=1.6):
    """Width of an attic floor with at least *headroom* under a gable roof.

    *span* is the distance between the two eave walls' outer faces, *z_eave*
    the height at which the roof's underside meets those faces and *tan* its
    pitch. The underside rises from each wall face, so the usable strip ends
    where it reaches z_floor + headroom.
    """
    lost = max(0.0, (z_floor + headroom - z_eave) / tan)
    return max(0.0, span - 2.0 * lost)


# ------------------------------------------------------------- .glb files
def glb_json(path):
    with open(path, "rb") as fh:
        data = fh.read()
    magic, version, _length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67 or version != 2:
        raise ValueError("%s is not a glTF 2 binary" % path)
    length, kind = struct.unpack_from("<II", data, 12)
    if kind != 0x4E4F534A:
        raise ValueError("%s does not start with a JSON chunk" % path)
    return json.loads(data[20:20 + length].decode("utf-8"))


def glb_stats(path):
    """Triangle count, vertex bounds and the image uris of one exported tier.

    The catalog's export applies every transform, so the POSITION accessors'
    own min and max are the bounds; a node that carries a transform is
    refused rather than misread.
    """
    js = glb_json(path)
    for node in js.get("nodes", []):
        if any(k in node for k in ("matrix", "translation", "rotation", "scale")):
            raise ValueError("%s: node %r carries a transform" % (path, node.get("name")))
    acc = js["accessors"]
    tris, lo, hi = 0, [math.inf] * 3, [-math.inf] * 3
    for mesh in js["meshes"]:
        for prim in mesh["primitives"]:
            if prim.get("mode", 4) != 4:
                raise ValueError("%s: a primitive is not a triangle list" % path)
            pos = acc[prim["attributes"]["POSITION"]]
            count = acc[prim["indices"]]["count"] if "indices" in prim else pos["count"]
            tris += count // 3
            lo = [min(a, b) for a, b in zip(lo, pos["min"])]
            hi = [max(a, b) for a, b in zip(hi, pos["max"])]
    return {"triangles": tris, "min": lo, "max": hi,
            "uris": [i.get("uri") for i in js.get("images", [])]}


# ------------------------------------------------------------------ source
def repo_root(here):
    return _git(here, "rev-parse", "--show-toplevel")


def _git(cwd, *args):
    try:
        out = subprocess.run(("git",) + args, cwd=cwd, check=True,
                             capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            "the facts sidecar records the commit it was built from, and "
            "`git %s` failed in %s: %s" % (" ".join(args), cwd,
                                           getattr(exc, "stderr", "") or exc))
    return out.stdout.rstrip("\n")


def source(here, name, blender):
    """The commit the asset was built from, and whether the asset folder or
    scripts/ differed from it. The sidecar itself is left out of that
    question: it is this function's own output."""
    root = repo_root(here)
    rel = os.path.relpath(here, root).replace(os.sep, "/")
    own = "%s/export/%s.model.json" % (rel, name)
    status = _git(root, "status", "--porcelain", "--untracked-files=all",
                  "--", rel, "scripts")
    dirty = any(line[3:].strip('"') != own for line in status.splitlines())
    return rel, {"commit": _git(root, "rev-parse", "HEAD"), "dirty": dirty,
                 "blender": blender}


# ----------------------------------------------------------------- compose
def compose(name, here, variants, default_variant, levels, pivot, facts, blender):
    """The sidecar's document, from the build's facts and the files on disk.

    *pivot* is the build's pivot offset (asset_build.pivot_offset of LOD0,
    before it was applied) and *facts* the build.py's facts() in the build
    frame. Raises on a fact that is missing or malformed; check() then judges
    the finished document.
    """
    px, py, pz = pivot
    edir = os.path.join(here, "export")

    def point(p):
        return [_r(p[0] - px), _r(p[2] - pz), _r(-(p[1] - py))]

    def plan(p):
        return [_r(p[0] - px), _r(-(p[1] - py))]

    def entry(fn, key="file"):
        return {key: fn, "sha256": sha256(os.path.join(edir, fn))}

    unknown = set(facts) - {"hero", "dwellings", "footprint", "storeys", "doors"}
    if unknown:
        raise ValueError("facts() has unknown keys: %s" % sorted(unknown))

    footprint = [plan((x, y, 0.0)) for x, y in facts["footprint"]]
    if _area(footprint) < 0.0:
        footprint.reverse()              # one winding for every asset
    doors = []
    for d in facts["doors"]:
        if set(d) != set(DOOR_KEYS):
            raise ValueError("door %r: keys %s" % (d.get("id"), sorted(d)))
        fx, fy = d["facing"]
        n = math.hypot(fx, fy)
        doors.append({"id": d["id"], "position": point(d["position"]),
                      "facing": [_r(fx / n), 0.0, _r(-fy / n)],
                      "width_m": _r(d["width_m"]), "height_m": _r(d["height_m"]),
                      "main": bool(d["main"])})

    lods = []
    for level in levels:
        fn = "%s_lod%d.glb" % (name, level)
        path = os.path.join(edir, fn)
        lods.append({"file": fn, "triangles": glb_stats(path)["triangles"],
                     "sha256": sha256(path)})
    lod0 = glb_stats(os.path.join(edir, lods[0]["file"]))

    textures = {"orm": entry(name + "_orm.png"), "normal": entry(name + "_normal.png")}
    if os.path.isfile(os.path.join(edir, name + "_emission.png")):
        textures["emission"] = entry(name + "_emission.png")

    rel, src = source(here, name, blender)
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "name": name,
        "path": rel,
        "source": src,
        "license": LICENSE,
        "bounds": {"min": [_r(v) for v in lod0["min"]],
                   "max": [_r(v) for v in lod0["max"]]},
        "footprint": footprint,
        "storeys": [{"floor_y_m": _r(z - pz), "area_m2": round(float(a), 2)}
                    for z, a in facts["storeys"]],
        "dwellings": int(facts["dwellings"]),
        "doors": doors,
        "lods": lods,
        "textures": textures,
        "variants": [{"id": v, "albedo": "%s_albedo_%s.png" % (name, v),
                      "sha256": sha256(os.path.join(
                          edir, "%s_albedo_%s.png" % (name, v)))}
                     for v in variants],
        "default_variant": default_variant,
        "preview": {"file": "../preview.png",
                    "sha256": sha256(os.path.join(here, "preview.png"))},
        "hero": bool(facts["hero"]),
    }


def dumps(doc):
    """The file's text: one key per line, short arrays on one line."""
    def flat(v):
        return json.dumps(v, ensure_ascii=False)

    out = ["{"]
    items = list(doc.items())
    for i, (k, v) in enumerate(items):
        comma = "," if i + 1 < len(items) else ""
        if k in ("footprint", "storeys", "doors", "lods", "variants"):
            out.append("  %s: [" % flat(k))
            out += ["    %s%s" % (flat(e), "," if j + 1 < len(v) else "")
                    for j, e in enumerate(v)]
            out.append("  ]" + comma)
        elif k == "textures":
            out.append("  %s: {" % flat(k))
            sub = list(v.items())
            out += ["    %s: %s%s" % (flat(a), flat(b), "," if j + 1 < len(sub) else "")
                    for j, (a, b) in enumerate(sub)]
            out.append("  }" + comma)
        else:
            out.append("  %s: %s%s" % (flat(k), flat(v), comma))
    out.append("}")
    return "\n".join(out) + "\n"


def write(path, doc):
    problems = check(doc, os.path.dirname(path))
    if problems:
        raise ValueError("the facts sidecar would be wrong:\n  " + "\n  ".join(problems))
    text = dumps(doc)
    if json.loads(text) != doc:
        raise ValueError("the facts sidecar does not survive its own formatting")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


# ------------------------------------------------------------------- check
def _area(poly):
    return sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(poly, poly[1:] + poly[:1])) / 2.0


def _edge_distance(p, a, b):
    ex, ey = b[0] - a[0], b[1] - a[1]
    t = ((p[0] - a[0]) * ex + (p[1] - a[1]) * ey) / (ex * ex + ey * ey)
    t = min(1.0, max(0.0, t))
    return math.hypot(p[0] - a[0] - t * ex, p[1] - a[1] - t * ey)


def _inside(p, poly):
    inside = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > p[1]) != (b[1] > p[1]) and \
                p[0] < a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            inside = not inside
    return inside


def _crosses(a, b, c, d):
    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return side(a, b, c) * side(a, b, d) < -1e-12 and side(c, d, a) * side(c, d, b) < -1e-12


def check(doc, export_dir):
    """Every problem with a sidecar document against the files beside it.

    Covers what a reader relies on: the schema's keys and nothing else, each
    hash against its file, triangle counts and bounds against the tiers, one
    simple footprint inside the bounds, exactly one main door, and every door
    on a footprint edge (within DOOR_TOL) or inside the outline, facing out
    along a unit horizontal normal.
    """
    problems = []
    if tuple(doc) != KEYS:
        problems.append("keys are %s, not the schema's %s" % (list(doc), list(KEYS)))
        return problems
    if doc["schema"] != SCHEMA or doc["version"] != VERSION:
        problems.append("schema %r version %r" % (doc["schema"], doc["version"]))
    name = doc["name"]
    if os.path.basename(doc["path"]) != name:
        problems.append("path %r does not end in the name %r" % (doc["path"], name))
    src = doc["source"]
    if tuple(src) != ("commit", "dirty", "blender"):
        problems.append("source keys are %s" % list(src))
    elif len(src["commit"]) != 40 or set(src["commit"]) - set("0123456789abcdef"):
        problems.append("source.commit is not a 40-hex commit")
    if doc["license"] != LICENSE:
        problems.append("license is %r" % doc["license"])

    def hashed(what, fn, digest):
        path = os.path.normpath(os.path.join(export_dir, fn))
        if not os.path.isfile(path):
            problems.append("%s: %s is missing" % (what, fn))
        elif sha256(path) != digest:
            problems.append("%s: %s does not match its recorded sha256" % (what, fn))

    for i, lod in enumerate(doc["lods"]):
        fn = lod["file"]
        if fn != "%s_lod%d.glb" % (name, i):
            problems.append("lods[%d] is %r" % (i, fn))
        hashed("lods", fn, lod["sha256"])
        path = os.path.join(export_dir, fn)
        if os.path.isfile(path):
            stats = glb_stats(path)
            if stats["triangles"] != lod["triangles"]:
                problems.append("%s has %d triangles, the sidecar says %d"
                                % (fn, stats["triangles"], lod["triangles"]))
            if i == 0:
                for key in ("min", "max"):
                    if any(abs(a - b) > 1e-3 for a, b in zip(stats[key], doc["bounds"][key])):
                        problems.append("bounds.%s %s is not %s's %s"
                                        % (key, doc["bounds"][key], fn, stats[key]))
                albedo = "%s_albedo_%s.png" % (name, doc["default_variant"])
                if albedo not in stats["uris"]:
                    problems.append("%s references %s, not the default variant's %s"
                                    % (fn, stats["uris"], albedo))
    if not doc["lods"]:
        problems.append("no lods")
    if abs(doc["bounds"]["min"][1]) > 1e-3:
        problems.append("bounds.min.y is %s, not 0" % doc["bounds"]["min"][1])

    for key, tex in doc["textures"].items():
        if key not in ("orm", "normal", "emission") or tex["file"] != "%s_%s.png" % (name, key):
            problems.append("textures.%s is %r" % (key, tex.get("file")))
        hashed("textures." + key, tex["file"], tex["sha256"])
    for key in ("orm", "normal"):
        if key not in doc["textures"]:
            problems.append("textures.%s is missing" % key)
    if ("emission" in doc["textures"]) != os.path.isfile(
            os.path.join(export_dir, name + "_emission.png")):
        problems.append("textures.emission disagrees with the emission PNG's presence")
    ids = [v["id"] for v in doc["variants"]]
    for v in doc["variants"]:
        if v["albedo"] != "%s_albedo_%s.png" % (name, v["id"]):
            problems.append("variant %r names %r" % (v["id"], v["albedo"]))
        hashed("variants", v["albedo"], v["sha256"])
    on_disk = sorted(f[len(name) + 8:-4] for f in os.listdir(export_dir)
                     if f.startswith(name + "_albedo_") and f.endswith(".png"))
    if sorted(ids) != on_disk or len(set(ids)) != len(ids):
        problems.append("variants %s are not the albedo files %s" % (ids, on_disk))
    if doc["default_variant"] not in ids:
        problems.append("default_variant %r is not a variant" % doc["default_variant"])
    if doc["preview"]["file"] != "../preview.png":
        problems.append("preview.file is %r" % doc["preview"]["file"])
    hashed("preview", doc["preview"]["file"], doc["preview"]["sha256"])

    fp = doc["footprint"]
    lo, hi = doc["bounds"]["min"], doc["bounds"]["max"]
    if len(fp) < 3 or fp[0] == fp[-1]:
        problems.append("footprint needs three or more points and no repeated end point")
    else:
        edges = list(zip(fp, fp[1:] + fp[:1]))
        if _area(fp) <= 0.0:
            problems.append("footprint has no positive area in [x, z]")
        if any(_crosses(a, b, c, d) for i, (a, b) in enumerate(edges)
               for c, d in edges[i + 1:]):
            problems.append("footprint crosses itself")
        if any(not (lo[0] - 1e-3 <= x <= hi[0] + 1e-3 and lo[2] - 1e-3 <= z <= hi[2] + 1e-3)
               for x, z in fp):
            problems.append("footprint leaves the LOD0 bounds")
        for d in doc["doors"]:
            p = (d["position"][0], d["position"][2])
            near = min(_edge_distance(p, a, b) for a, b in edges)
            if near > DOOR_TOL and not _inside(p, fp):
                problems.append("door %r is %.3f m outside the footprint" % (d["id"], near))

    floors = [s["floor_y_m"] for s in doc["storeys"]]
    if not floors or floors != sorted(floors) or any(s["area_m2"] <= 0 for s in doc["storeys"]):
        problems.append("storeys must be one or more, lowest first, each with an area")
    if doc["dwellings"] < 0:
        problems.append("dwellings is negative")

    door_ids = [d["id"] for d in doc["doors"]]
    if len(set(door_ids)) != len(door_ids):
        problems.append("door ids repeat: %s" % door_ids)
    if sum(1 for d in doc["doors"] if d["main"]) != 1:
        problems.append("exactly one door must be main, not %d"
                        % sum(1 for d in doc["doors"] if d["main"]))
    for d in doc["doors"]:
        if tuple(d) != DOOR_KEYS:
            problems.append("door %r: keys %s" % (d.get("id"), list(d)))
            continue
        fx, fy, fz = d["facing"]
        if fy != 0 or abs(math.hypot(fx, fz) - 1.0) > 1e-3:
            problems.append("door %r: facing %s is not a unit horizontal vector"
                            % (d["id"], d["facing"]))
        if not (d["width_m"] > 0 and d["height_m"] > 0 and d["position"][1] >= 0):
            problems.append("door %r: size or threshold height is not positive" % d["id"])
    return problems


def check_file(path):
    """check() on a sidecar on disk; a missing or unparsable file is a problem."""
    if not os.path.isfile(path):
        return ["%s is missing" % os.path.basename(path)]
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except ValueError as exc:
        return ["%s does not parse: %s" % (os.path.basename(path), exc)]
    return check(doc, os.path.dirname(path))
