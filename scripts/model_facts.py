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
            "doors": [model_facts.wall_door("front", "entrance", p0, p1, s, z,
                                            w, h, main=True)],
            "passages": [model_facts.lane_passage("lane", (x, y), (0.0, 1.0),
                                                  w, l, h)],   # optional
        }

Every door names its kind, one of DOOR_KINDS, and exactly one door, an
entrance, is main. A structure with no door (a chimney stack) lists none and
so has no main door; one with no occupied floor lists no storeys. A building
with a drivable lane through it lists it under passages; without one, it
leaves the key out, and so does the sidecar.
asset_build.Asset.write_facts() adds everything that is
read from the build and the exported files. Triangle counts and bounds are
read from the .glb files themselves, so the sidecar describes what ships.

Pure Python, no bpy: scripts/validate_asset.py runs check() on what is on disk.

Vehicles write version 2 with "kind": "vehicle" (compose_vehicle(), the
helpers under "vehicles" below); buildings and boundary props stay version
1, unchanged. dumps(), write() and check() take either version. A vehicle
build.py's facts() is completed by scripts/vehicle_build.py's VehicleAsset,
which measures the wheels, lamps, glass and body from the LOD0 build.
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
DOOR_KEYS = ("id", "kind", "position", "facing", "width_m", "height_m", "main")
# entrance: a pedestrian door people use to enter the occupied space from the
# ground. service: a staff or back pedestrian door at ground level. vehicle:
# loading and goods doors. balcony: any door not reachable from the ground,
# upper-floor doors included. store: doors of sheds and unheated stores.
DOOR_KINDS = ("entrance", "service", "vehicle", "balcony", "store")
# Optional: present only when the build.py's facts() lists passages, and then
# right after doors. A drivable lane through the building, from one mouth.
PASSAGES_AFTER = "doors"
PASSAGE_KEYS = ("id", "position", "forward", "width_m", "length_m",
                "clear_height_m", "through")
PASSAGE_TOL = 1e-3               # a mouth's distance outside the LOD0 plan bounds


def schema_keys(doc):
    """KEYS in order, with passages after doors when *doc* has them."""
    keys = list(KEYS)
    if "passages" in doc:
        keys.insert(keys.index(PASSAGES_AFTER) + 1, "passages")
    return tuple(keys)


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
def wall_door(door_id, kind, p0, p1, s, z, width, height, main=False):
    """A door of *kind* (DOOR_KINDS) in the wall from plan point *p0* to *p1*,
    in the build frame. The one *main* door is the entrance a visitor uses,
    tagged by the build.py; in a row of equal units, the unit just to the +X
    side of the centre (the middle one in an odd row).

    The catalog's walls run counter-clockwise seen from above, so the outward
    normal is on the right of p0 -> p1. *s* is the door's centre along the
    wall from p0 and *z* its threshold; the position is on the outer wall
    plane whatever the reveal's depth. *width* and *height* are the leaf's
    (or the pair's) clear opening, without casing, fanlight or transom.
    """
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    tx, ty = dx / length, dy / length
    return {"id": door_id, "kind": kind,
            "position": (p0[0] + tx * s, p0[1] + ty * s, z),
            "facing": (ty, -tx),
            "width_m": width, "height_m": height, "main": bool(main)}


def lane_passage(passage_id, mouth, direction, width, length, clear_height,
                 through=True):
    """A drivable lane through the building, in the build frame, stated from
    one of its mouths: the one vehicles enter by, for a lane used one way.

    *mouth* is the plan point (x, y) where the lane's centre line crosses
    that mouth's outer wall plane, on the ground the pivot stands on.
    *direction* is the plan vector along the lane from the mouth into the
    building; it is normalised here. *width* is the clear width between the
    lane's walls, *length* the run from this mouth to the far one (or to the
    lane's closed end), and *clear_height* the lowest geometry over the
    lane's whole width and length, hung hoppers and beams included. *through*
    is true when the lane is open at the far end.
    """
    dx, dy = direction
    n = math.hypot(dx, dy)
    return {"id": passage_id, "position": (mouth[0], mouth[1], 0.0),
            "forward": (dx / n, dy / n), "width_m": width, "length_m": length,
            "clear_height_m": clear_height, "through": bool(through)}


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

    unknown = set(facts) - {"hero", "dwellings", "footprint", "storeys", "doors",
                            "passages"}
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
        doors.append({"id": d["id"], "kind": d["kind"],
                      "position": point(d["position"]),
                      "facing": [_r(fx / n), 0.0, _r(-fy / n)],
                      "width_m": _r(d["width_m"]), "height_m": _r(d["height_m"]),
                      "main": bool(d["main"])})
    passages = []
    for p in facts.get("passages") or ():
        if set(p) != set(PASSAGE_KEYS):
            raise ValueError("passage %r: keys %s" % (p.get("id"), sorted(p)))
        fx, fy = p["forward"]
        n = math.hypot(fx, fy)
        passages.append({"id": p["id"], "position": point(p["position"]),
                         "forward": [_r(fx / n), 0.0, _r(-fy / n)],
                         "width_m": _r(p["width_m"]), "length_m": _r(p["length_m"]),
                         "clear_height_m": _r(p["clear_height_m"]),
                         "through": bool(p["through"])})

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
    doc = {
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
    if passages:
        doc["passages"] = passages
    return {k: doc[k] for k in schema_keys(doc)}


def dumps(doc):
    """The file's text: one key per line, short arrays on one line, and an
    empty list (no doors, no storeys) as [] on its key's line."""
    if doc.get("kind") == VEHICLE_KIND:
        return _dumps_vehicle(doc)

    def flat(v):
        return json.dumps(v, ensure_ascii=False)

    out = ["{"]
    items = list(doc.items())
    for i, (k, v) in enumerate(items):
        comma = "," if i + 1 < len(items) else ""
        if k in ("footprint", "storeys", "doors", "passages", "lods", "variants") and v:
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
    simple footprint inside the bounds, storeys (if any) lowest first, exactly
    one main door and that one an entrance where there are doors at all, and
    every door of a DOOR_KINDS kind, on a footprint edge
    (within DOOR_TOL) or inside the outline, facing out along a unit
    horizontal normal. Passages, when present, are checked by _passages().
    A version 2 vehicle document is checked by check_vehicle().
    """
    if isinstance(doc, dict) and (doc.get("kind") == VEHICLE_KIND
                                  or doc.get("version") == VEHICLE_VERSION):
        return check_vehicle(doc, export_dir)
    problems = []
    if tuple(doc) != schema_keys(doc):
        problems.append("keys are %s, not the schema's %s"
                        % (list(doc), list(schema_keys(doc))))
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
    if floors != sorted(floors) or any(s["area_m2"] <= 0 for s in doc["storeys"]):
        problems.append("storeys must be lowest first, each with an area")
    if doc["dwellings"] < 0:
        problems.append("dwellings is negative")

    door_ids = [d["id"] for d in doc["doors"]]
    if len(set(door_ids)) != len(door_ids):
        problems.append("door ids repeat: %s" % door_ids)
    if doc["doors"] and sum(1 for d in doc["doors"] if d["main"]) != 1:
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
        if d["kind"] not in DOOR_KINDS:
            problems.append("door %r: kind %r is not one of %s"
                            % (d["id"], d["kind"], list(DOOR_KINDS)))
        if d["main"] and d["kind"] != "entrance":
            problems.append("door %r: the main door must be an entrance, not %r"
                            % (d["id"], d["kind"]))
        if not (d["width_m"] > 0 and d["height_m"] > 0 and d["position"][1] >= 0):
            problems.append("door %r: size or threshold height is not positive" % d["id"])
    if "passages" in doc:
        problems += _passages(doc["passages"], lo, hi)
    return problems


def _number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _passages(passages, lo, hi):
    """Problems with the optional passages: a non-empty list of PASSAGE_KEYS
    records with unique non-empty ids, each mouth on the ground (y within
    1 mm of 0) and on or within the LOD0 plan bounds, a unit horizontal
    forward, positive sizes, a boolean through, and the lane's far end,
    position + forward * length, on or within the bounds as well."""
    if not isinstance(passages, list) or not passages:
        return ["passages must be a non-empty list, or left out"]
    problems = []
    ids = [p.get("id") if isinstance(p, dict) else None for p in passages]
    if len(set(map(repr, ids))) != len(ids):
        problems.append("passage ids repeat: %s" % ids)

    def within(x, z):
        return (lo[0] - PASSAGE_TOL <= x <= hi[0] + PASSAGE_TOL
                and lo[2] - PASSAGE_TOL <= z <= hi[2] + PASSAGE_TOL)

    for p in passages:
        if not isinstance(p, dict) or tuple(p) != PASSAGE_KEYS:
            problems.append("passage %r: keys %s, not %s"
                            % (p.get("id") if isinstance(p, dict) else p,
                               list(p) if isinstance(p, dict) else type(p).__name__,
                               list(PASSAGE_KEYS)))
            continue
        pid = p["id"]
        if not isinstance(pid, str) or not pid:
            problems.append("passage id %r is not a non-empty string" % (pid,))
        pos, fwd = p["position"], p["forward"]
        if not (isinstance(pos, list) and len(pos) == 3 and all(map(_number, pos))):
            problems.append("passage %r: position %r is not [x, y, z]" % (pid, pos))
            continue
        if not (isinstance(fwd, list) and len(fwd) == 3 and all(map(_number, fwd))):
            problems.append("passage %r: forward %r is not [x, y, z]" % (pid, fwd))
            continue
        if abs(pos[1]) > 1e-3:
            problems.append("passage %r: position y is %s, not 0" % (pid, pos[1]))
        if fwd[1] != 0 or abs(math.hypot(fwd[0], fwd[2]) - 1.0) > 1e-3:
            problems.append("passage %r: forward %s is not a unit horizontal vector"
                            % (pid, fwd))
        sizes = [p[k] for k in ("width_m", "length_m", "clear_height_m")]
        if not all(_number(v) and v > 0 for v in sizes):
            problems.append("passage %r: width, length and clear height %s must "
                            "be positive numbers" % (pid, sizes))
            continue
        if not isinstance(p["through"], bool):
            problems.append("passage %r: through %r is not a boolean"
                            % (pid, p["through"]))
        if not within(pos[0], pos[2]):
            problems.append("passage %r: the mouth %s leaves the LOD0 plan bounds"
                            % (pid, pos))
        end = (pos[0] + fwd[0] * p["length_m"], pos[2] + fwd[2] * p["length_m"])
        if not within(*end):
            problems.append("passage %r: the %s [%.4f, %.4f] leaves the LOD0 plan "
                            "bounds" % (pid, "far mouth" if p["through"] else "end",
                                        end[0], end[1]))
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


# ================================================================= vehicles
# Version 2, "kind": "vehicle" (CLAUDE.md, Vehicles). The field order is the
# contract's example's. numpy and scripts/vehicle_ids.py are imported inside
# the functions that need them, so the version 1 path stays standard-library.
VEHICLE_VERSION = 2
VEHICLE_KIND = "vehicle"
VEHICLE_KEYS = ("schema", "version", "kind", "name", "path", "source", "license",
                "bounds", "body", "axles", "wheels", "attributes", "lamps", "glass",
                "cargo", "coupling", "interior", "lods", "textures", "variants",
                "default_variant", "preview")
BODY_KEYS = ("class", "length_m", "width_m", "width_mirrors_m", "height_m",
             "wheelbase_m", "front_overhang_m", "rear_overhang_m",
             "ground_clearance_m")
AXLE_KEYS = ("z", "track_m", "steer", "twin")
WHEEL_KEYS = ("id", "part", "axle", "side", "centre", "radius_m", "width_m", "steer")
ATTRIBUTES = {"set": "COLOR_0", "r": "part", "g": "surface", "b": "paint", "version": 1}
LAMP_KEYS = ("group", "lamp", "side", "position", "colour", "centre", "facing",
             "width_m", "height_m")
GLASS_KEYS = ("group", "id", "area_m2")
CARGO_KEYS = ("min", "max", "door")
CARGO_DOORS = ("rear", "side", "top")
INTERIOR_KEYS = ("file", "triangles", "sha256")
VEHICLE_LOD_KEYS = ("file", "triangles", "sha256", "wheel_parts", "lamp_ids", "glass_ids")
VARIANT_KEYS = ("name", "albedo", "paint")
AXLE_TOL = 0.01          # wheels whose centres lie this close in z share an axle
GEOM_TOL = 1e-3


# ---------------------------------------------------------- build frame
def wheel_part(part, centre, radius, width, steer, twin=False):
    """One wheel part, in the build frame: *centre* the wheel's centre
    (its object's origin), *radius* and *width* the tyre's (both tyres of a
    twin pair), *steer* whether the game turns it."""
    return {"part": int(part), "centre": tuple(centre), "radius": float(radius),
            "width": float(width), "steer": bool(steer), "twin": bool(twin)}


def lamp_lens(lamp, points, facing, colour=None):
    """One lens of lamp id *lamp* from its faces' vertices *points* and
    their outward *facing* (the area-weighted normal), in the build frame.
    *colour* is its lit colour, white, amber or red: None takes the group's
    one colour (vehicle_ids.lens_colours); a marker, beacon or sign lens
    states its own (VehicleAsset.lamp_lenses() reads it from the emission).

    The rectangle is the faces' bounding rectangle in the plane across the
    facing: width along up x facing (horizontal), height along facing x
    width; a lens facing straight up takes width along X. Its centre is the
    rectangle's centre, on the plane through the points' mean depth."""
    import numpy as np
    import vehicle_ids as vi
    f = np.asarray(vi.to_gltf(facing), float)
    f /= np.linalg.norm(f)
    p = np.array([vi.to_gltf(q) for q in points], float)
    u, v = vi.lens_axes(f)
    pu, pv, pf = p @ u, p @ v, p @ f
    cu, cv = (pu.min() + pu.max()) / 2.0, (pv.min() + pv.max()) / 2.0
    c = u * cu + v * cv + f * pf.mean()
    out = {"lamp": int(lamp), "centre": vi.to_build(c), "facing": vi.to_build(f),
           "width": float(pu.max() - pu.min()), "height": float(pv.max() - pv.min())}
    if colour is not None:
        out["colour"] = colour
    return out


def glass_group(glass_id, area):
    """One glass group present: its id and its area in square metres."""
    return {"id": int(glass_id), "area": float(area)}


def cargo_box(lo, hi, door="rear"):
    """The load box of a van or truck, build-frame corners, and its door."""
    return {"lo": tuple(lo), "hi": tuple(hi), "door": door}


def interior_file(here, name):
    """The optional interior mesh, export/<name>_interior.glb, once one is
    built: its file, triangle count and hash. None until then."""
    fn = name + "_interior.glb"
    path = os.path.join(here, "export", fn)
    if not os.path.isfile(path):
        return None
    return {"file": fn, "triangles": glb_stats(path)["triangles"], "sha256": sha256(path)}


def wheel_name(axle, axles, side):
    where = "front" if axle == 0 else "rear" if axle == axles - 1 else "axle%d" % axle
    return "%s_%s" % (where, side)


# --------------------------------------------------------------- compose
def tier_ids(path):
    """(parts, surfaces) present in one exported tier, read from COLOR_0."""
    import vehicle_ids as vi
    part, surf, _paint, _off = vi.decode(vi.tier(path)["color"])
    return set(part.tolist()), set(surf.tolist())


def compose_vehicle(name, here, variants, default_variant, levels, facts, blender):
    """The version 2 document, from the vehicle facts and the files on disk.

    *variants* is [(name, paint), ...]: paint false for a livery that paints
    its panels in full colour. *facts* (build frame) holds "class", "body"
    (measured: "lo"/"hi" the plan-and-height box without mirrors,
    "width_mirrors", "ground_clearance"), "wheels" (wheel_part()), "lamps"
    (lamp_lens()), "glass" (glass_group()), "cargo" (cargo_box() or None),
    "coupling" (None) and "interior" (interior_file()). Bounds, triangle
    counts, per-tier id flags and hashes are read from the exported files.
    """
    import vehicle_ids as vi
    edir = os.path.join(here, "export")
    unknown = set(facts) - {"class", "body", "wheels", "lamps", "glass", "cargo",
                            "coupling", "interior"}
    if unknown:
        raise ValueError("vehicle facts have unknown keys: %s" % sorted(unknown))
    cls = facts["class"]
    if cls not in vi.CLASSES:
        raise ValueError("class %r is not one of %s" % (cls, list(vi.CLASSES)))

    def g(p):
        return [_r(c) for c in vi.to_gltf(p)]

    def entry(fn):
        return {"file": fn, "sha256": sha256(os.path.join(edir, fn))}

    # wheels and axles, front axle first, left before right
    wheels = sorted(facts["wheels"], key=lambda w: w["part"])
    if [w["part"] for w in wheels] != list(range(1, len(wheels) + 1)):
        raise ValueError("wheel parts are %s, not 1..n" % [w["part"] for w in wheels])
    zs = []
    for w in wheels:
        z = vi.to_gltf(w["centre"])[2]
        if not any(abs(z - a) < AXLE_TOL for a in zs):
            zs.append(z)
    zs.sort(reverse=True)

    def axle_of(w):
        z = vi.to_gltf(w["centre"])[2]
        return next(i for i, a in enumerate(zs) if abs(z - a) < AXLE_TOL)

    axles = []
    for i, z in enumerate(zs):
        on = [w for w in wheels if axle_of(w) == i]
        left = [w["centre"][0] for w in on if w["centre"][0] > 0]
        right = [w["centre"][0] for w in on if w["centre"][0] < 0]
        if len(left) != 1 or len(right) != 1:
            raise ValueError("axle %d has %d left and %d right wheel parts"
                             % (i, len(left), len(right)))
        zz = sum(vi.to_gltf(w["centre"])[2] for w in on) / len(on)
        axles.append({"z": _r(zz), "track_m": _r(left[0] - right[0]),
                      "steer": any(w["steer"] for w in on),
                      "twin": any(w["twin"] for w in on)})
    wheel_docs = []
    for w in wheels:
        a = axle_of(w)
        side = "left" if w["centre"][0] > 0 else "right"
        wheel_docs.append({"id": wheel_name(a, len(axles), side), "part": w["part"],
                           "axle": a, "side": side, "centre": g(w["centre"]),
                           "radius_m": _r(w["radius"]), "width_m": _r(w["width"]),
                           "steer": bool(w["steer"])})

    b = facts["body"]
    lo, hi = vi.to_gltf(b["lo"]), vi.to_gltf(b["hi"])
    zmin, zmax = min(lo[2], hi[2]), max(lo[2], hi[2])
    body = {"class": cls, "length_m": _r(zmax - zmin),
            "width_m": _r(abs(hi[0] - lo[0])),
            "width_mirrors_m": _r(b["width_mirrors"]),
            "height_m": _r(max(lo[1], hi[1])),
            "wheelbase_m": _r(axles[0]["z"] - axles[-1]["z"]) if axles else 0.0,
            "front_overhang_m": _r(zmax - axles[0]["z"]) if axles else 0.0,
            "rear_overhang_m": _r(axles[-1]["z"] - zmin) if axles else 0.0,
            "ground_clearance_m": _r(b["ground_clearance"])}

    order = {p: i for i, p in enumerate(vi.POSITIONS)}
    sides = {s: i for i, s in enumerate(vi.SIDES)}
    lamps = []
    for ln in facts["lamps"]:
        c, f = vi.to_gltf(ln["centre"]), vi.to_gltf(ln["facing"])
        n = math.sqrt(sum(x * x for x in f))
        f = [x / n for x in f]
        allowed = vi.lens_colours(ln["lamp"])
        colour = ln.get("colour") or (allowed[0] if len(allowed) == 1 else None)
        if colour not in allowed:
            raise ValueError("a %s lens at %s needs its colour, one of %s, not %r "
                             "(lamp_lens(..., colour=))"
                             % (vi.LAMPS[ln["lamp"]][0], [_r(x) for x in c], list(allowed),
                                colour))
        lamps.append({"group": vi.LAMPS[ln["lamp"]][0], "lamp": int(ln["lamp"]),
                      "side": vi.lens_side(c[0]), "position": vi.lens_position(f),
                      "colour": colour,
                      "centre": [_r(x) for x in c], "facing": [_r(x) for x in f],
                      "width_m": _r(ln["width"]), "height_m": _r(ln["height"])})
    lamps.sort(key=lambda d: (d["lamp"], order[d["position"]], sides[d["side"]],
                              -d["centre"][2], -d["centre"][1], -d["centre"][0]))
    glass = [{"group": vi.GLASS.get(gl["id"], "glass_reserved_%d" % gl["id"]),
              "id": int(gl["id"]), "area_m2": round(float(gl["area"]), 3)}
             for gl in sorted(facts["glass"], key=lambda d: d["id"])]
    cargo = facts.get("cargo")
    if cargo is not None:
        a, bb = vi.to_gltf(cargo["lo"]), vi.to_gltf(cargo["hi"])
        cargo = {"min": [_r(min(p, q)) for p, q in zip(a, bb)],
                 "max": [_r(max(p, q)) for p, q in zip(a, bb)],
                 "door": cargo["door"]}

    lods = []
    for level in levels:
        fn = "%s_lod%d.glb" % (name, level)
        path = os.path.join(edir, fn)
        parts, surfs = tier_ids(path)
        lods.append({"file": fn, "triangles": glb_stats(path)["triangles"],
                     "sha256": sha256(path),
                     "wheel_parts": any(p > 0 for p in parts),
                     "lamp_ids": any(s in vi.LAMP_IDS for s in surfs),
                     "glass_ids": any(s in vi.GLASS_IDS for s in surfs)})
    lod0 = glb_stats(os.path.join(edir, lods[0]["file"]))
    normal = name + "_normal.png"
    textures = {"orm": entry(name + "_orm.png"),
                "emission": entry(name + "_emission.png"),
                "normal": entry(normal) if os.path.isfile(os.path.join(edir, normal))
                else None}
    rel, src = source(here, name, blender)
    doc = {
        "schema": SCHEMA, "version": VEHICLE_VERSION, "kind": VEHICLE_KIND,
        "name": name, "path": rel, "source": src, "license": LICENSE,
        "bounds": {"min": [_r(v) for v in lod0["min"]],
                   "max": [_r(v) for v in lod0["max"]]},
        "body": body, "axles": axles, "wheels": wheel_docs,
        "attributes": dict(ATTRIBUTES), "lamps": lamps, "glass": glass,
        "cargo": cargo, "coupling": facts.get("coupling"),
        "interior": facts.get("interior"),
        "lods": lods, "textures": textures,
        "variants": [{"name": v, "albedo": entry("%s_albedo_%s.png" % (name, v)),
                      "paint": bool(p)} for v, p in variants],
        "default_variant": default_variant,
        "preview": {"file": "preview.png",
                    "sha256": sha256(os.path.join(here, "preview.png"))},
    }
    return {k: doc[k] for k in VEHICLE_KEYS}


def _dumps_vehicle(doc):
    """One key per line; each entry of a list on its own line; body,
    attributes and textures one member per line."""
    def flat(v):
        return json.dumps(v, ensure_ascii=False)

    out = ["{"]
    items = list(doc.items())
    for i, (k, v) in enumerate(items):
        comma = "," if i + 1 < len(items) else ""
        if isinstance(v, list) and v and k in ("axles", "wheels", "lamps", "glass",
                                               "lods", "variants"):
            out.append("  %s: [" % flat(k))
            out += ["    %s%s" % (flat(e), "," if j + 1 < len(v) else "")
                    for j, e in enumerate(v)]
            out.append("  ]" + comma)
        elif isinstance(v, dict) and k in ("body", "textures"):
            out.append("  %s: {" % flat(k))
            sub = list(v.items())
            out += ["    %s: %s%s" % (flat(a), flat(b), "," if j + 1 < len(sub) else "")
                    for j, (a, b) in enumerate(sub)]
            out.append("  }" + comma)
        else:
            out.append("  %s: %s%s" % (flat(k), flat(v), comma))
    out.append("}")
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------- check
def _vec(v, n=3):
    return isinstance(v, list) and len(v) == n and all(map(_number, v))


def check_vehicle(doc, export_dir):
    """Every problem with a version 2 vehicle document against the files
    beside it: the schema's keys in order, each record's keys, ids and
    names against the tables in scripts/vehicle_ids.py, the body block
    against the bounds and the axles, wheels resting on the ground, the
    hashes, triangle counts and id flags of the tiers, the variants against
    the albedo files, and the lamp and glass lists against LOD0's ids both
    ways. Whether a lens lies on its faces is scripts/vehicle_checks.py's."""
    import vehicle_ids as vi
    problems = []
    if not isinstance(doc, dict) or tuple(doc) != VEHICLE_KEYS:
        return ["keys are %s, not the vehicle schema's %s"
                % (list(doc) if isinstance(doc, dict) else doc, list(VEHICLE_KEYS))]
    if (doc["schema"], doc["version"], doc["kind"]) != (SCHEMA, VEHICLE_VERSION,
                                                        VEHICLE_KIND):
        problems.append("schema %r version %r kind %r"
                        % (doc["schema"], doc["version"], doc["kind"]))
    name = doc["name"]
    if os.path.basename(doc["path"]) != name:
        problems.append("path %r does not end in the name %r" % (doc["path"], name))
    src = doc["source"]
    if not isinstance(src, dict) or tuple(src) != ("commit", "dirty", "blender"):
        problems.append("source keys are %s" % list(src))
    elif len(src["commit"]) != 40 or set(src["commit"]) - set("0123456789abcdef"):
        problems.append("source.commit is not a 40-hex commit")
    if doc["license"] != LICENSE:
        problems.append("license is %r" % doc["license"])

    def hashed(what, fn, digest, base=export_dir):
        path = os.path.normpath(os.path.join(base, fn))
        if not os.path.isfile(path):
            problems.append("%s: %s is missing" % (what, fn))
        elif sha256(path) != digest:
            problems.append("%s: %s does not match its recorded sha256" % (what, fn))

    def keyed(what, rec, keys):
        if not isinstance(rec, dict) or tuple(rec) != keys:
            problems.append("%s: keys %s, not %s" % (
                what, list(rec) if isinstance(rec, dict) else rec, list(keys)))
            return False
        return True

    lo, hi = doc["bounds"]["min"], doc["bounds"]["max"]
    if abs(lo[1]) > GEOM_TOL:
        problems.append("bounds.min.y is %s, not 0" % lo[1])

    body = doc["body"]
    cls = None
    if keyed("body", body, BODY_KEYS):
        cls = body["class"]
        if cls not in vi.CLASSES:
            problems.append("body.class %r is not one of %s" % (cls, list(vi.CLASSES)))
            cls = None
        nums = [body[k] for k in BODY_KEYS[1:]]
        if not all(_number(x) and x >= 0 for x in nums):
            problems.append("body sizes must be numbers, not negative: %s" % nums)
        else:
            if abs(body["height_m"] - hi[1]) > GEOM_TOL:
                problems.append("body.height_m %s is not bounds.max.y %s"
                                % (body["height_m"], hi[1]))
            if body["width_mirrors_m"] + GEOM_TOL < body["width_m"]:
                problems.append("width_mirrors_m is under width_m")
            if abs(body["width_mirrors_m"] - (hi[0] - lo[0])) > GEOM_TOL:
                problems.append("width_mirrors_m %s is not the bounds' x extent %.4f"
                                % (body["width_mirrors_m"], hi[0] - lo[0]))
            if abs(body["length_m"] - (hi[2] - lo[2])) > GEOM_TOL:
                problems.append("length_m %s is not the bounds' z extent %.4f"
                                % (body["length_m"], hi[2] - lo[2]))
            total = body["front_overhang_m"] + body["wheelbase_m"] + body["rear_overhang_m"]
            if abs(total - body["length_m"]) > 2 * GEOM_TOL:
                problems.append("overhangs and wheelbase add up to %.4f, not length_m %s"
                                % (total, body["length_m"]))

    axles = doc["axles"]
    if not isinstance(axles, list) or not axles:
        problems.append("axles must be a non-empty list")
        axles = []
    for i, a in enumerate(axles):
        if not keyed("axles[%d]" % i, a, AXLE_KEYS):
            continue
        if not (_number(a["z"]) and _number(a["track_m"]) and a["track_m"] > 0
                and isinstance(a["steer"], bool) and isinstance(a["twin"], bool)):
            problems.append("axles[%d] is malformed: %s" % (i, a))
    zs = [a.get("z") for a in axles if isinstance(a, dict)]
    if zs != sorted(zs, reverse=True):
        problems.append("axles are not front first: z %s" % zs)
    if axles and body.get("wheelbase_m") is not None and _number(zs[0]) and \
            abs(zs[0] - zs[-1] - body["wheelbase_m"]) > GEOM_TOL:
        problems.append("wheelbase_m %s is not the first to the last axle, %.4f"
                        % (body["wheelbase_m"], zs[0] - zs[-1]))

    wheels = doc["wheels"]
    if not isinstance(wheels, list) or not 4 <= len(wheels) <= vi.MAX_WHEELS:
        problems.append("wheels must list 4..%d wheel parts" % vi.MAX_WHEELS)
        wheels = wheels if isinstance(wheels, list) else []
    for i, w in enumerate(wheels):
        if not keyed("wheels[%d]" % i, w, WHEEL_KEYS):
            continue
        if w["part"] != i + 1:
            problems.append("wheels[%d] is part %r, not %d (part order)" % (i, w["part"], i + 1))
        if not (isinstance(w["axle"], int) and 0 <= w["axle"] < len(axles)):
            problems.append("wheel %r: axle %r" % (w["id"], w["axle"]))
            continue
        if w["side"] not in ("left", "right") or not _vec(w["centre"]):
            problems.append("wheel %r: side %r, centre %r" % (w["id"], w["side"], w["centre"]))
            continue
        if w["id"] != wheel_name(w["axle"], len(axles), w["side"]):
            problems.append("wheel id %r is not %r" % (
                w["id"], wheel_name(w["axle"], len(axles), w["side"])))
        if (w["centre"][0] > 0) != (w["side"] == "left"):
            problems.append("wheel %r: side %s but x %s (+x is the driver's left)"
                            % (w["id"], w["side"], w["centre"][0]))
        if abs(w["centre"][1] - w["radius_m"]) > GEOM_TOL:
            problems.append("wheel %r: centre.y %s is not radius_m %s"
                            % (w["id"], w["centre"][1], w["radius_m"]))
        if not (w["radius_m"] > 0 and w["width_m"] > 0):
            problems.append("wheel %r: radius and width must be positive" % w["id"])
        ax = axles[w["axle"]]
        if isinstance(ax, dict) and _number(ax.get("z")) and \
                abs(w["centre"][2] - ax["z"]) > AXLE_TOL:
            problems.append("wheel %r is not on axle %d's z" % (w["id"], w["axle"]))
        if isinstance(ax, dict) and w["steer"] and not ax.get("steer"):
            problems.append("wheel %r steers on an axle that does not" % w["id"])
    if wheels and not any(isinstance(w, dict) and w.get("steer") for w in wheels):
        problems.append("no wheel steers")

    if doc["attributes"] != ATTRIBUTES:
        problems.append("attributes are %s, not %s" % (doc["attributes"], ATTRIBUTES))

    lamp_ids, uncoloured = set(), []
    for i, ln in enumerate(doc["lamps"]):
        if isinstance(ln, dict) and "colour" not in ln and \
                tuple(ln) == tuple(k for k in LAMP_KEYS if k != "colour"):
            uncoloured.append(i)          # one summary below; the rest is checked
            ln = dict(ln, colour=None)
        elif not keyed("lamps[%d]" % i, ln, LAMP_KEYS):
            continue
        lid = ln["lamp"]
        if lid not in vi.LAMPS or ln["group"] != vi.LAMPS[lid][0]:
            problems.append("lamps[%d]: group %r lamp %r" % (i, ln["group"], lid))
            continue
        lamp_ids.add(lid)
        if ln["side"] not in vi.SIDES or ln["position"] not in vi.POSITIONS:
            problems.append("lamps[%d]: side %r position %r" % (i, ln["side"], ln["position"]))
        if ln["colour"] not in vi.lens_colours(lid) and i not in uncoloured:
            problems.append("lamps[%d] (%s): colour %r, not one of %s"
                            % (i, ln["group"], ln["colour"], list(vi.lens_colours(lid))))
        if not (_vec(ln["centre"]) and _vec(ln["facing"])):
            problems.append("lamps[%d]: centre or facing is not [x, y, z]" % i)
            continue
        if abs(math.sqrt(sum(x * x for x in ln["facing"])) - 1.0) > GEOM_TOL:
            problems.append("lamps[%d]: facing %s is not a unit vector" % (i, ln["facing"]))
        if ln["side"] in vi.SIDES and vi.lens_side(ln["centre"][0]) != ln["side"]:
            problems.append("lamps[%d] (%s): side %s but x %s"
                            % (i, ln["group"], ln["side"], ln["centre"][0]))
        if not (_number(ln["width_m"]) and _number(ln["height_m"])
                and ln["width_m"] >= 0 and ln["height_m"] >= 0):
            problems.append("lamps[%d]: width and height must be numbers" % i)
    if uncoloured:
        problems.append("lamps%s: %d lens entries have no colour (a sidecar written before "
                        "the field: rewrite it with build.py -- facts)"
                        % (uncoloured if len(uncoloured) < 6 else "", len(uncoloured)))
    if cls:
        missing = vi.required_lamps(cls, lamp_ids)
        if missing:
            problems.append("lamps: required lamp ids missing: %s" % missing)
        if cls == "car" and not any(isinstance(ln, dict) and ln.get("lamp") == 2
                                    and ln.get("side") == "centre" for ln in doc["lamps"]):
            problems.append("lamps: a car has a high-mounted brake lamp (2, centre)")

    glass_ids = []
    for i, gl in enumerate(doc["glass"]):
        if not keyed("glass[%d]" % i, gl, GLASS_KEYS):
            continue
        gid = gl["id"]
        if gid not in vi.GLASS_IDS or gl["group"] != vi.GLASS.get(
                gid, "glass_reserved_%d" % gid):
            problems.append("glass[%d]: group %r id %r" % (i, gl["group"], gid))
        if not (_number(gl["area_m2"]) and gl["area_m2"] > 0):
            problems.append("glass[%d]: area %r" % (i, gl["area_m2"]))
        glass_ids.append(gid)
    if len(set(glass_ids)) != len(glass_ids) or glass_ids != sorted(glass_ids):
        problems.append("glass groups repeat or are out of id order: %s" % glass_ids)
    if cls:
        missing = vi.required_glass(cls, set(glass_ids))
        if missing:
            problems.append("glass: required glass ids missing: %s" % missing)

    cargo = doc["cargo"]
    if cargo is not None:
        if keyed("cargo", cargo, CARGO_KEYS):
            if not (_vec(cargo["min"]) and _vec(cargo["max"]) and
                    all(a < b for a, b in zip(cargo["min"], cargo["max"]))):
                problems.append("cargo min/max are not a box")
            if cargo["door"] not in CARGO_DOORS:
                problems.append("cargo door %r is not one of %s" % (cargo["door"], CARGO_DOORS))
    elif cls in ("van", "truck"):
        problems.append("cargo is null; a %s states its load box" % cls)
    if doc["coupling"] is not None:
        problems.append("coupling must be null (reserved for trailers)")
    interior = doc["interior"]
    if interior is not None and keyed("interior", interior, INTERIOR_KEYS):
        hashed("interior", interior["file"], interior["sha256"])

    lods = doc["lods"]
    if not isinstance(lods, list) or len(lods) != len(vi.LEVELS):
        problems.append("lods must list all four tiers")
        lods = lods if isinstance(lods, list) else []
    lod0_ids = None
    for i, lod in enumerate(lods):
        if not keyed("lods[%d]" % i, lod, VEHICLE_LOD_KEYS):
            continue
        fn = lod["file"]
        if fn != "%s_lod%d.glb" % (name, i):
            problems.append("lods[%d] is %r" % (i, fn))
        hashed("lods", fn, lod["sha256"])
        path = os.path.join(export_dir, fn)
        if not os.path.isfile(path):
            continue
        stats = glb_stats(path)
        if stats["triangles"] != lod["triangles"]:
            problems.append("%s has %d triangles, the sidecar says %d"
                            % (fn, stats["triangles"], lod["triangles"]))
        try:
            parts, surfs = tier_ids(path)
        except ValueError as exc:
            problems.append("%s: %s" % (fn, exc))
            continue
        flags = {"wheel_parts": any(p > 0 for p in parts),
                 "lamp_ids": any(s in vi.LAMP_IDS for s in surfs),
                 "glass_ids": any(s in vi.GLASS_IDS for s in surfs)}
        for k, v in flags.items():
            if lod[k] is not v:
                problems.append("lods[%d].%s is %r, the tier says %r" % (i, k, lod[k], v))
        if i == 0:
            lod0_ids = (parts, surfs)
            for key in ("min", "max"):
                if any(abs(a - b) > GEOM_TOL for a, b in zip(stats[key], doc["bounds"][key])):
                    problems.append("bounds.%s %s is not %s's %s"
                                    % (key, doc["bounds"][key], fn, stats[key]))
            albedo = "%s_albedo_%s.png" % (name, doc["default_variant"])
            if albedo not in stats["uris"]:
                problems.append("%s references %s, not the default variant's %s"
                                % (fn, stats["uris"], albedo))
    if lod0_ids is not None:
        parts, surfs = lod0_ids
        listed = lamp_ids | set(glass_ids)
        in_mesh = {s for s in surfs if s}
        if in_mesh - listed:
            problems.append("LOD0 carries surface ids no list names: %s"
                            % sorted(in_mesh - listed))
        if listed - in_mesh:
            problems.append("listed lamp or glass ids missing from LOD0: %s"
                            % sorted(listed - in_mesh))
        want = set(range(len(wheels) + 1))
        if parts != want:
            problems.append("LOD0 parts are %s, the wheels list says %s"
                            % (sorted(parts), sorted(want)))

    tex = doc["textures"]
    if not isinstance(tex, dict) or tuple(tex) != ("orm", "emission", "normal"):
        problems.append("textures keys are %s, not orm, emission, normal"
                        % (list(tex) if isinstance(tex, dict) else tex))
    else:
        for key, t in tex.items():
            if t is None:
                if key != "normal":
                    problems.append("textures.%s is required" % key)
                elif os.path.isfile(os.path.join(export_dir, "%s_normal.png" % name)):
                    problems.append("textures.normal is null but %s_normal.png exists" % name)
                continue
            if tuple(t) != ("file", "sha256") or t["file"] != "%s_%s.png" % (name, key):
                problems.append("textures.%s is %r" % (key, t))
                continue
            hashed("textures." + key, t["file"], t["sha256"])

    names = []
    for i, v in enumerate(doc["variants"]):
        if not keyed("variants[%d]" % i, v, VARIANT_KEYS):
            continue
        names.append(v["name"])
        a = v["albedo"]
        if not isinstance(a, dict) or tuple(a) != ("file", "sha256") or \
                a["file"] != "%s_albedo_%s.png" % (name, v["name"]):
            problems.append("variant %r albedo is %r" % (v["name"], a))
        else:
            hashed("variants", a["file"], a["sha256"])
        if not isinstance(v["paint"], bool):
            problems.append("variant %r: paint %r is not a boolean" % (v["name"], v["paint"]))
    on_disk = sorted(f[len(name) + 8:-4] for f in os.listdir(export_dir)
                     if f.startswith(name + "_albedo_") and f.endswith(".png"))
    if sorted(names) != on_disk or len(set(names)) != len(names):
        problems.append("variants %s are not the albedo files %s" % (names, on_disk))
    if doc["default_variant"] not in names:
        problems.append("default_variant %r is not a variant" % doc["default_variant"])
    pv = doc["preview"]
    if not isinstance(pv, dict) or tuple(pv) != ("file", "sha256") or pv["file"] != "preview.png":
        problems.append("preview is %r" % pv)
    else:
        hashed("preview", pv["file"], pv["sha256"], os.path.dirname(os.path.normpath(export_dir)))
    return problems
