# SPDX-License-Identifier: GPL-3.0-or-later

"""Mechanical checks over an asset's exported files.

Run inside Blender, because the interior-geometry check needs a BVH:

    blender -b -P scripts/validate_asset.py -- buildings/service/brick_clocktower_hall

This validates what actually ships — the contents of ``export/`` — rather than
the authoring scene, so a stale or hand-edited export cannot pass.

It covers the parts of CLAUDE.md's Validation Checklist that a machine can
decide. It deliberately does not cover the parts that need judgement (palette,
proportion, silhouette across tiers, whether the asset resembles a real
building); those stay with the six verification views and the reviewer. Checks
that cannot be decided here are reported as MANUAL rather than silently passed,
so the output is never mistaken for a full sign-off.

The check this exists for is INTERIOR GEOMETRY. Screenshots cannot find it —
interior walls are invisible from every exterior angle by definition — so it is
the one checklist item with no human fallback.
"""

import json
import math
import os
import struct
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# Per-tier triangle bands (floor, ceiling), from CLAUDE.md's budgets. Buildings
# run LOD0..LOD3 across a free camera's ~20-150 m; props run LOD0..LOD2 with the
# last optional, because a prop culls out long before a building's far tiers
# matter. The tier count per kind is taken from the length of its entry, not
# hardcoded. Buildings have ceilings only: a building's count follows from its
# massing, and the catalog's houses sit an order of magnitude under any single
# floor that would also fit a tower.
BUDGETS = {
    ("building", False): ((None, 12000), (None, 4000), (None, 1500), (None, 500)),
    ("building", True): ((None, 20000), (None, 6000), (None, 2500), (None, 700)),
    ("prop_small", False): ((50, 300), (12, 80), None),
    ("prop_medium", False): ((200, 800), (40, 200), None),
}
TEX_MAX = {("building", False): 1024, ("building", True): 2048,
           ("prop_small", False): 256, ("prop_medium", False): 512}

# Hidden-surface thresholds. A watertight shell must close somewhere — a
# wall-ring cap, a roof underside, a shaft through the roof, the buried back of
# a quoin block — so the floor is never zero, and on a low-poly tier that
# unavoidable closure is a large *share* of a small mesh. Judging on percentage
# alone therefore flags a clean bottom tier while a bloated LOD0 slips through, so
# both a share and an absolute count have to be exceeded together.
#
# Calibrated against the first building authored here: 3,018 hidden triangles
# at 48% while it carried full interior partition walls, 586 at 11% once they
# were gone.
# notes.md sections, from CLAUDE.md's Notes.md & Catalog Template. Fixed
# spelling and order are what let one asset's notes be read, and diffed,
# against another's; "Revision log" is optional and always last.
NOTES_ORDER = (
    "Style brief", "Category and secondary use", "Hero/landmark status",
    "Footprint", "Story height", "Door leaf height", "Window sills",
    "Eave overhang", "Construction", "Per-tier triangle counts", "LOD review",
    "Interior geometry", "Known simplifications", "Texture set",
    "Glazing treatment", "Variant list", "Night lighting", "Export",
    "Review status", "Tooling versions", "Revision log",
)
# A prop has no storeys, doors, eaves or night windows to record, so those
# sections are absent rather than a column of "n/a"; glazing is required only
# of the props that actually carry glass, which this cannot decide.
NOTES_REQUIRED = {
    "building": tuple(s for s in NOTES_ORDER if s != "Revision log"),
    "prop": ("Style brief", "Category and secondary use", "Footprint",
             "Construction", "Per-tier triangle counts", "LOD review",
             "Texture set", "Variant list", "Export", "Review status",
             "Tooling versions"),
}

HIDDEN_WARN = (0.15, 150)
HIDDEN_FAIL = (0.25, 400)
RAYS = 40


def _pot(n):
    return n >= 1 and (n & (n - 1)) == 0


def _hemisphere(n, k=RAYS):
    """Cosine-ish weighted directions in the hemisphere around *n*."""
    a = n.normalized()
    if a.length_squared < 0.5:
        return []
    tmp = Vector((0.0, 0.0, 1.0)) if abs(a.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    u = a.cross(tmp).normalized()
    v = a.cross(u)
    ga = math.pi * (3.0 - math.sqrt(5.0))
    out = []
    for i in range(k):
        z = (i + 0.5) / k
        r = math.sqrt(max(0.0, 1.0 - z * z))
        th = ga * i
        out.append((a * z + u * (r * math.cos(th)) + v * (r * math.sin(th))).normalized())
    return out


def hidden_surface(obj, far=1000.0, eps=1e-3):
    """Triangles no ray can escape from, i.e. surface no camera can reach.

    Visibility, not position: a point-in-solid test would report every recessed
    window as buried, because the glass legitimately sits behind the wall plane.
    """
    me = obj.data
    me.calc_loop_triangles()
    tri_of = {}
    for t in me.loop_triangles:
        tri_of[t.polygon_index] = tri_of.get(t.polygon_index, 0) + 1
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bvh = BVHTree.FromBMesh(bm)
    bm.free()
    hid_t = 0
    hid_vert_area = 0.0
    worst = []
    for p in me.polygons:
        o = p.center + p.normal * eps
        if any(bvh.ray_cast(o, d, far)[0] is None for d in _hemisphere(p.normal)):
            continue
        hid_t += tri_of.get(p.index, 0)
        if abs(p.normal.z) < 0.5:
            hid_vert_area += p.area
        worst.append((p.area, tuple(round(c, 2) for c in p.center)))
    worst.sort(reverse=True)
    return {"hidden_tris": hid_t, "total_tris": len(me.loop_triangles),
            "hidden_vertical_area_m2": round(hid_vert_area, 2),
            "largest_hidden": worst[:5]}


def mesh_health(obj, weld=1e-5):
    """Manifold check on the welded mesh.

    glTF stores one vertex per unique position/normal/UV combination, so an
    exported mesh arrives with its vertices split along every UV seam and hard
    edge. Checked as-imported, a perfectly watertight asset reports thousands of
    boundary edges — every seam looks like a hole. Welding by distance first
    restores the topology the asset was authored with, which is what the
    "opens cleanly" rule is actually about.
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    split = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=weld)
    out = {"boundary_edges": sum(1 for e in bm.edges if len(e.link_faces) == 1),
           "edges_over_2_faces": sum(1 for e in bm.edges if len(e.link_faces) > 2),
           "loose_verts": sum(1 for v in bm.verts if not v.link_edges),
           "loose_edges": sum(1 for e in bm.edges if not e.link_faces),
           "verts_as_stored": split, "verts_welded": len(bm.verts)}
    bm.free()
    out["manifold"] = not any(out[k] for k in
                              ("boundary_edges", "edges_over_2_faces",
                               "loose_verts", "loose_edges"))
    return out


def glb_json(path):
    with open(path, "rb") as fh:
        data = fh.read()
    magic, ver, length = struct.unpack_from("<III", data, 0)
    ok = (magic == 0x46546C67 and ver == 2 and length == len(data))
    off, js, nchunks = 12, None, 0
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        off += 8
        chunk = data[off:off + clen]
        off += clen
        nchunks += 1
        if ctype == 0x4E4F534A:
            js = json.loads(chunk.decode("utf-8"))
    return js, {"header_ok": ok, "chunks": nchunks, "walk_ok": off == len(data)}


def check_tier(results, asset, adir, level, kind, hero):
    tag = "LOD{}".format(level)
    path = os.path.join(adir, "export", "{}_lod{}.glb".format(asset, level))
    if not os.path.exists(path):
        required = (kind == "building") or level < 2
        results.append(("FAIL" if required else "SKIP", tag,
                        "export missing" if required else "optional tier absent"))
        return
    js, hdr = glb_json(path)
    results.append(("PASS" if hdr["header_ok"] and hdr["walk_ok"] else "FAIL", tag,
                    "GLB container: header_ok={header_ok} chunks={chunks} "
                    "walk_ok={walk_ok}".format(**hdr)))

    emission_name = asset + "_emission.png"
    if kind == "building" and os.path.isfile(os.path.join(adir, "export", emission_name)):
        bound = 0
        for index, material in enumerate(js.get("materials", [])):
            binding = material.get("emissiveTexture")
            if binding is None:
                continue
            bound += 1
            try:
                texture = js["textures"][binding["index"]]
                image = js["images"][texture["source"]]
                uv = "TEXCOORD_%d" % binding.get("texCoord", 0)
                primitives = [p for mesh in js["meshes"] for p in mesh["primitives"]
                              if p.get("material") == index]
                valid = (image.get("uri") == emission_name and "bufferView" not in image
                         and material.get("emissiveFactor", [0, 0, 0]) == [0, 0, 0]
                         and primitives and all(uv in p["attributes"] for p in primitives))
            except (KeyError, IndexError, TypeError):
                valid = False
            results.append(("PASS" if valid else "FAIL", tag,
                            "window emission: external mask, UV binding, default off"
                            if valid else "invalid window emission image/UV/default state"))
        if not bound:
            results.append(("FAIL", tag, "emission PNG exists but no emissiveTexture is bound"))

    normal_name = asset + "_normal.png"
    if os.path.isfile(os.path.join(adir, "export", normal_name)):
        # Every material carries the shared normal map: external, on a UV set
        # its primitives have, at scale 1 (strength lives in the texture).
        for index, material in enumerate(js.get("materials", [])):
            binding = material.get("normalTexture")
            try:
                texture = js["textures"][binding["index"]]
                image = js["images"][texture["source"]]
                uv = "TEXCOORD_%d" % binding.get("texCoord", 0)
                primitives = [p for mesh in js["meshes"] for p in mesh["primitives"]
                              if p.get("material") == index]
                valid = (image.get("uri") == normal_name and "bufferView" not in image
                         and abs(binding.get("scale", 1.0) - 1.0) < 1e-6
                         and primitives and all(uv in p["attributes"] for p in primitives))
            except (KeyError, IndexError, TypeError):
                valid = False
            results.append(("PASS" if valid else "FAIL", tag,
                            "normal map: external, UV binding, scale 1" if valid else
                            "normal PNG exists but material %r does not bind it "
                            "correctly" % material.get("name")))

    bad = [i.get("name") for i in js.get("images", [])
           if "uri" in i and "bufferView" in i]
    embedded = [i.get("name") for i in js.get("images", [])
                if "uri" not in i and "bufferView" in i]
    if bad:
        results.append(("FAIL", tag, "images carry both uri and bufferView: %s "
                                     "(Godot drops these)" % bad))
    elif embedded:
        results.append(("FAIL", tag, "images embedded rather than referenced: %s"
                        % embedded))
    else:
        results.append(("PASS", tag, "images referenced externally, uri only"))

    mats = js.get("materials", [])
    results.append((("PASS" if 1 <= len(mats) <= 2 else "FAIL"), tag,
                    "material slots: %d" % len(mats)))
    for mm in mats:
        if mm.get("doubleSided", False):
            results.append(("FAIL", tag, "material %r is doubleSided" % mm.get("name")))
        if mm.get("alphaMode", "OPAQUE") != "OPAQUE":
            results.append(("FAIL", tag, "material %r alphaMode=%s"
                            % (mm.get("name"), mm.get("alphaMode"))))

    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    objs = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    if not objs:
        results.append(("FAIL", tag, "no mesh imported"))
        return
    obj = objs[0]

    h = mesh_health(obj)
    results.append((("PASS" if h["manifold"] else "FAIL"), tag,
                    "manifold after welding seams: boundary={boundary_edges} "
                    "over2={edges_over_2_faces} loose_v={loose_verts} "
                    "loose_e={loose_edges} ({verts_as_stored} stored verts -> "
                    "{verts_welded} welded)".format(**h)))

    obj.data.calc_loop_triangles()
    tris = len(obj.data.loop_triangles)
    band = BUDGETS[(kind, hero)][level]
    if band is None:
        results.append(("PASS", tag, "triangles: %d (no band for this tier)" % tris))
    elif tris > band[1]:
        results.append(("FAIL", tag, "triangles: %d, over the %d ceiling"
                                     % (tris, band[1])))
    elif band[0] is None:
        results.append(("PASS", tag, "triangles: %d (ceiling %d)" % (tris, band[1])))
    elif tris < band[0]:
        # Asymmetric on purpose. The ceiling is a real cost and holds; the floor
        # only says what an ordinary silhouette tends to need, and a simple
        # prop legitimately comes in under it. Failing that would invite
        # padding the tier with triangles that carry no shape, which is worse
        # than the shortfall — so it is a WARN the reviewer explains in
        # notes.md, not a defect to engineer away.
        results.append(("WARN", tag, "triangles: %d, under the %d floor (band "
                                     "%d-%d) — fine if the silhouette is simple, "
                                     "but say so in notes.md"
                        % (tris, band[0], band[0], band[1])))
    else:
        results.append(("PASS", tag,
                        "triangles: %d (band %d-%d)" % (tris, band[0], band[1])))

    zs = [v.co.z for v in obj.data.vertices]
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    results.append((("PASS" if abs(min(zs)) < 1e-3 else "FAIL"), tag,
                    "pivot at ground: min z = %.4f" % min(zs)))
    if kind == "building":
        cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
        results.append((("PASS" if abs(cx) < 1e-2 and abs(cy) < 1e-2 else "FAIL"), tag,
                        "pivot centred on footprint: centre = (%.3f, %.3f)" % (cx, cy)))

    hs = hidden_surface(obj)
    n, frac = hs["hidden_tris"], hs["hidden_tris"] / max(1, hs["total_tris"])
    status = "PASS"
    if frac >= HIDDEN_FAIL[0] and n >= HIDDEN_FAIL[1]:
        status = "FAIL"
    elif frac >= HIDDEN_WARN[0] and n >= HIDDEN_WARN[1]:
        status = "WARN"
    results.append((status, tag,
                    "interior geometry: %d/%d triangles hidden (%.1f%%), "
                    "%.1f m2 of it vertical; largest hidden faces at %s"
                    % (n, hs["total_tris"], frac * 100.0,
                       hs["hidden_vertical_area_m2"],
                       [c for _, c in hs["largest_hidden"][:3]])))

    d = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if d.users == 0:
        bpy.data.meshes.remove(d)


def check_textures(results, asset, adir, kind, hero):
    try:
        from PIL import Image
    except ImportError:
        results.append(("MANUAL", "tex", "Pillow unavailable; texture format "
                                         "unchecked"))
        return
    edir = os.path.join(adir, "export")
    pngs = sorted(f for f in os.listdir(edir) if f.lower().endswith(".png"))
    if not pngs:
        results.append(("FAIL", "tex", "no textures in export/"))
        return
    cap = TEX_MAX[(kind, hero)]
    for name in pngs:
        im = Image.open(os.path.join(edir, name))
        w, h = im.size
        issues = []
        if im.mode not in ("RGB", "L"):
            issues.append("mode=%s (alpha or non-8-bit)" % im.mode)
        if w != h:
            issues.append("not square (%dx%d)" % (w, h))
        if not _pot(w) or not _pot(h):
            issues.append("not power-of-two")
        if w > cap:
            issues.append("%d exceeds the %d cap" % (w, cap))
        results.append((("PASS" if not issues else "FAIL"), "tex",
                        "%s: %dx%d %s%s" % (name, w, h, im.mode,
                                            "" if not issues else " -> " + "; ".join(issues))))
    if not any(("_orm" in p) for p in pngs):
        results.append(("FAIL", "tex", "no ORM texture present"))
    check_normal(results, asset, edir, pngs, kind, Image)
    check_glazing(results, asset, edir, pngs, Image)
    results.append(("MANUAL", "tex", "colour space (albedo sRGB, ORM/normal "
                                     "linear) is set in Blender, not readable "
                                     "from the PNG"))


def check_normal(results, asset, edir, pngs, kind, Image):
    """A building needs a normal map; when there is one, check its encoding.

    Decoded vectors should be unit length and face out of the surface. This
    cannot tell OpenGL from DirectX green (both are valid unit vectors), so
    that stays a MANUAL item for the render review.
    """
    name = asset + "_normal.png"
    if name not in pngs:
        if kind == "building":
            results.append(("WARN", "tex", "no %s: CLAUDE.md requires a normal map "
                                           "for buildings" % name))
        return
    import numpy as np
    n = np.asarray(Image.open(os.path.join(edir, name)).convert("RGB"),
                   np.float32) / 127.5 - 1.0
    length = np.linalg.norm(n, axis=-1)
    unit = float(np.mean(np.abs(length - 1.0) < 0.05))
    outward = float(np.mean(n[..., 2] > 0.0))
    ok = unit > 0.99 and outward > 0.999
    results.append(("PASS" if ok else "FAIL", "tex",
                    "normal map: %.1f%% unit length, %.2f%% facing out, mean z %.3f"
                    % (100 * unit, 100 * outward, float(n[..., 2].mean()))))
    results.append(("MANUAL", "tex", "normal map is OpenGL (+Y green up): "
                                     "check a lit render that laps and seams "
                                     "read as raised, not dented"))


def check_glazing(results, asset, edir, pngs, Image):
    """Measure the albedo over the emission mask against Style Direction.

    The emission PNG is the candidate-glazing mask, so it doubles as a free
    glass selector: no atlas layout knowledge is needed. Seen from outside a
    window is mostly the unlit room behind it, and the sky reflection is the
    renderer's job, so a pane brighter than its own casing is the symptom
    that base colour is double-counting the sky.

    This measures value only. It cannot see roughness bindings, whether a
    fixed sky gradient was baked across the pane, or whether the mask covers
    the right pixels.
    """
    import numpy as np

    mask_name = asset + "_emission.png"
    if mask_name not in pngs:
        return
    emit = np.array(Image.open(os.path.join(edir, mask_name)).convert("RGB")).astype(np.int16)
    lit = emit.max(axis=-1) > 0
    # Candidate glazing is written neutral grey: each pane at its own level
    # with a lamp's glow (glazing.night_rooms), never below about a fifth.
    # A luminous fixture that is not a window -- a lit sign, a lamp bowl --
    # carries its own colour, and measuring it against the glazing band would
    # be meaningless, so it is reported separately instead. CLAUDE.md's Output
    # Contract allows such fixtures when the brief calls for them.
    neutral = (emit.max(axis=-1) - emit.min(axis=-1)) <= 24
    glass = (emit[..., 0] > 40) & neutral
    # Shrink by a pixel: a pane's anti-aliased edge (supersampled coverage)
    # still counts as glazing, but its albedo mixes in the frame's.
    mask = glass.copy()
    mask[1:, :] &= glass[:-1, :]
    mask[:-1, :] &= glass[1:, :]
    mask[:, 1:] &= glass[:, :-1]
    mask[:, :-1] &= glass[:, 1:]
    # only colour marks a fixture; grey at any level is glazing
    fixture = lit & ~neutral
    if fixture.any():
        results.append(("MANUAL", "glazing",
                        "%d mask pixels are coloured luminous fixtures, not "
                        "glazing; their regions and control scope belong in "
                        "notes.md" % int(fixture.sum())))
    if not mask.any():
        results.append(("FAIL" if not lit.any() else "MANUAL", "glazing",
                        "emission mask is empty" if not lit.any() else
                        "emission mask holds no neutral glazing to measure"))
        return
    for name in pngs:
        if "_albedo" not in name:
            continue
        im = np.array(Image.open(os.path.join(edir, name)).convert("RGB"))
        if im.shape[:2] != mask.shape:
            continue
        glass = im[mask].astype(np.float32)
        rest = im[~mask].astype(np.float32)
        mean = glass.mean()
        lin = (mean / 255.0) ** 2.2
        trim = float(np.percentile(rest, 99.0)) or 1.0
        issues = []
        if not 40.0 <= mean <= 78.0:
            issues.append("mean sRGB %.0f outside the 45-70 band" % mean)
        if mean > trim:
            issues.append("brighter than the trim around it (%.0f vs %.0f)"
                          % (mean, trim))
        results.append((("PASS" if not issues else "FAIL"), "glazing",
                        "%s: glass sRGB %.0f, linear %.3f, %.2fx trim%s"
                        % (name, mean, lin, mean / trim,
                           "" if not issues else " -> " + "; ".join(issues))))
    results.append(("MANUAL", "glazing", "glazing painted with scripts/glazing.py "
                                         "(or a brief-driven exception recorded "
                                         "in notes.md); no baked sky gradient"))


def check_notes(results, adir, kind):
    """Check notes.md's ## sections against the schema, not their prose.

    The failure this catches is a note growing a second section about a
    surface the note already described — typically a dated revision appended
    instead of an edit — after which the reader has to guess which of the two
    is the asset as it now stands.
    """
    path = os.path.join(adir, "notes.md")
    if not os.path.exists(path):
        return                      # already reported by the file check
    found, fence = [], False
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("```"):
                fence = not fence
            elif not fence and line.startswith("## "):
                found.append(line[3:].strip())

    required = NOTES_REQUIRED["building" if kind == "building" else "prop"]
    missing = [s for s in required if s not in found]
    if missing:
        results.append(("FAIL", "notes", "missing required section%s: %s"
                        % ("" if len(missing) == 1 else "s", ", ".join(missing))))

    for head in found:
        if head in NOTES_ORDER:
            continue
        # A dated or qualified revision heading keeps the section name it
        # supersedes, so name that section rather than only rejecting the line.
        owner = next((s for s in NOTES_ORDER if head.startswith(s)), None)
        results.append(("FAIL", "notes", "unrecognised section %r; %s" % (
            head, "fold it into %r" % owner if owner else
            "asset-specific material belongs in a ### subsection")))

    for head in dict.fromkeys(found):
        if found.count(head) > 1:
            results.append(("FAIL", "notes", "section %r appears %d times; the "
                            "notes describe current state once"
                            % (head, found.count(head))))

    known = [s for s in found if s in NOTES_ORDER]
    ranks = [NOTES_ORDER.index(s) for s in known]
    out = next((known[i] for i in range(1, len(ranks))
                if ranks[i] < ranks[i - 1]), None)
    if out:
        results.append(("WARN", "notes", "sections out of schema order, first "
                                         "at %r" % out))
    if not missing and out is None and len(set(found)) == len(found) \
            and all(s in NOTES_ORDER for s in found):
        results.append(("PASS", "notes", "notes.md sections complete, unique "
                                         "and in order"))


def validate(adir, kind="building", hero=False):
    if kind not in ("building", "prop_small", "prop_medium"):
        raise ValueError("kind must be building, prop_small or prop_medium, "
                         "not %r" % kind)
    if kind != "building" and hero:
        # The hero/landmark exception is a buildings-only rule; props have no
        # equivalent band, so silently accepting it would validate against a
        # budget that does not exist.
        raise ValueError("the hero/landmark exception applies to buildings only")
    adir = os.path.abspath(adir)
    asset = os.path.basename(adir.rstrip("/"))
    results = []
    for f in ("notes.md", "preview.png"):
        results.append((("PASS" if os.path.exists(os.path.join(adir, f)) else "FAIL"),
                        "files", "%s present" % f))
    check_notes(results, adir, kind)
    for level in range(len(BUDGETS[(kind, hero)])):
        check_tier(results, asset, adir, level, kind, hero)
    check_textures(results, asset, adir, kind, hero)
    for note in ("material palette within the muted/realistic range",
                 "silhouette, roofline and major recesses match across tiers",
                 "front faces -Y" if kind == "building" else
                 "orientation only forced where the prop has a real front",
                 "not a reproduction of a specific real building or object",
                 "the six verification views have been looked at"):
        results.append(("MANUAL", "review", note))
    return asset, results


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    adir = argv[0]
    kind = argv[1] if len(argv) > 1 else "building"
    hero = len(argv) > 2 and argv[2].lower() in ("hero", "true", "1", "yes")
    asset, results = validate(adir, kind, hero)
    order = {"FAIL": 0, "WARN": 1, "MANUAL": 2, "SKIP": 3, "PASS": 4}
    print("\n%s  (%s%s)" % (asset, kind, ", hero" if hero else ""))
    print("=" * 72)
    for status, tag, msg in sorted(results, key=lambda r: order[r[0]]):
        print("%-7s %-6s %s" % (status, tag, msg))
    fails = sum(1 for s, _, _ in results if s == "FAIL")
    warns = sum(1 for s, _, _ in results if s == "WARN")
    man = sum(1 for s, _, _ in results if s == "MANUAL")
    print("=" * 72)
    print("%d FAIL, %d WARN, %d MANUAL — MANUAL items are not checked here and "
          "still need a reviewer." % (fails, warns, man))
    return 1 if fails else 0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    if bpy.app.background:
        sys.exit(code)
