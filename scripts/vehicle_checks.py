# SPDX-License-Identifier: GPL-3.0-or-later

"""The vehicle checks of CLAUDE.md's Vehicles section, on the exported files.

scripts/validate_asset.py runs these for the classes vehicle_car,
vehicle_van, vehicle_truck and vehicle_bus, beside its generic tier checks
(GLB container, external images, manifold, hidden surface, triangle
ceilings, notes). Everything here reads the files directly: the tiers'
accessors (positions, triangles, COLOR_0 bytes, UVs) through
scripts/vehicle_ids.py, the sidecar, the PNGs and glass_texels.png. Blender's
own importer is not used, because it reads COLOR_0 as an sRGB byte colour.

    1  class box, ground contact, wheels resting, plan box kept by every tier
    2  wheel and lamp pairs mirror in x
    3  ids: COLOR_0 as normalised UNSIGNED_BYTE VEC4, A = 255, whole ids from
       the allowed sets, one R, G and B per triangle, R = B = 0 on lamps
       and glass, B 0 or 1
    4  per tier: wheel parts, required and listed lamp and glass ids
    5  wheel vertices inside their sidecar cylinders, no body vertex inside
    6  steer clearance: wheels turned +-35 degrees (and straight, for every
       wheel) keep 10 mm from every body triangle
    7  lamp faces inside the nearest lens rectangle of their id, no lens
       without a face, lit lens texels
    8  glass ids against the glass texels both ways, lit cabin texels, the
       glass albedo and roughness band
    9  emission black off the lamps and the glass; painted faces neutral
    10 one material, the sidecar (hashes, clean source, lists against the
       mesh), texture sizes

A texel set of a triangle is the texels whose centres lie at least half a
texel inside it in UV, or, for a triangle too small to hold one, the texel
under its centroid.

    python3 scripts/vehicle_checks.py ASSET_DIR car     # these checks only
"""

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_facts  # noqa: E402
import vehicle_ids as vi  # noqa: E402

LENS_TOL = 0.002         # a lamp face's reach past its lens rectangle, metres
LENS_DEPTH = 0.05        # and along the lens's facing
BLACK = 3                # an 8-bit texel at or under this in every channel is black
NEUTRAL_CHROMA = 10.0    # mean sRGB max - min over a painted face
PAINT_LEVEL = (0.60, 0.90)   # linear grey of the painted panels, WARN outside
GLASS_SRGB = (40.0, 78.0)    # mean over the glass texels, as validate_asset's glazing
GLASS_ROUGH = (0.05, 0.12)


# ================================================================ geometry
def closest_distance(points, tris):
    """Distance from each of *points* (n, 3) to the nearest of triangles
    *tris* (m, 3, 3), exactly (Ericson's closest point on a triangle), with
    an AABB prefilter at the running best distance. Returns (n,) distances
    and the index of the nearest triangle (-1 where none is near)."""
    points = np.asarray(points, float)
    n = len(points)
    best = np.full(n, np.inf)
    which = np.full(n, -1)
    if len(tris) == 0 or n == 0:
        return best, which
    lo, hi = tris.min(axis=1), tris.max(axis=1)
    # a first bound: the nearest triangle corner
    corners = tris.reshape(-1, 3)
    for s in range(0, n, 512):
        d = np.linalg.norm(points[s:s + 512, None, :] - corners[None], axis=2)
        best[s:s + 512] = d.min(axis=1)
    reach = best[:, None]
    gap = np.maximum(np.maximum(lo[None] - points[:, None], points[:, None] - hi[None]), 0.0)
    near = np.einsum("ptk,ptk->pt", gap, gap) <= reach * reach + 1e-12
    pi, ti = np.nonzero(near)
    for s in range(0, len(pi), 200000):
        p, t = pi[s:s + 200000], ti[s:s + 200000]
        d = _point_triangle(points[p], tris[t])
        order = np.lexsort((d, p))
        p, t, d = p[order], t[order], d[order]
        first = np.ones(len(p), bool)
        first[1:] = p[1:] != p[:-1]
        p, t, d = p[first], t[first], d[first]
        better = d < best[p]
        best[p[better]] = d[better]
        which[p[better]] = t[better]
    return best, which


def _point_triangle(p, tri):
    """Row-wise distance from points p (k, 3) to triangles tri (k, 3, 3)."""
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    ab, ac, ap = b - a, c - a, p - a

    def dot(x, y):
        return np.einsum("ij,ij->i", x, y)
    d1, d2 = dot(ab, ap), dot(ac, ap)
    bp, cp = p - b, p - c
    d3, d4 = dot(ab, bp), dot(ac, bp)
    d5, d6 = dot(ab, cp), dot(ac, cp)
    va = d3 * d6 - d5 * d4
    vb = d5 * d2 - d1 * d6
    vc = d1 * d4 - d3 * d2
    q = np.empty_like(p)
    done = np.zeros(len(p), bool)

    def put(mask, val):
        m = mask & ~done
        q[m] = val[m] if val.ndim == 2 else val
        done[:] |= m
    put((d1 <= 0) & (d2 <= 0), a)
    put((d3 >= 0) & (d4 <= d3), b)
    put((d6 >= 0) & (d5 <= d6), c)
    with np.errstate(divide="ignore", invalid="ignore"):
        v = d1 / (d1 - d3)
        put((vc <= 0) & (d1 >= 0) & (d3 <= 0), a + v[:, None] * ab)
        w = d2 / (d2 - d6)
        put((vb <= 0) & (d2 >= 0) & (d6 <= 0), a + w[:, None] * ac)
        w2 = (d4 - d3) / ((d4 - d3) + (d5 - d6))
        put((va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0), b + w2[:, None] * (c - b))
        den = 1.0 / (va + vb + vc)
        v3, w3 = vb * den, vc * den
        put(np.ones(len(p), bool), a + v3[:, None] * ab + w3[:, None] * ac)
    return np.linalg.norm(p - q, axis=1)


def edge_samples(pts, tris, k=3):
    """Vertices of *tris* plus *k* points inside each of their edges."""
    out = [pts[np.unique(tris)]]
    for i, j in ((0, 1), (1, 2), (2, 0)):
        a, b = pts[tris[:, i]], pts[tris[:, j]]
        for s in range(1, k + 1):
            t = s / (k + 1.0)
            out.append(a + (b - a) * t)
    return np.concatenate(out)


def wheel_sides(pts, centre, radius):
    """Distinct angles round the axis of the vertices on the tread's rim."""
    d = pts - np.asarray(centre)
    r = np.hypot(d[:, 1], d[:, 2])
    ang = np.round(np.degrees(np.arctan2(d[r > 0.9 * radius, 2], d[r > 0.9 * radius, 1])), 1)
    return len(np.unique(np.mod(ang, 360.0)))


# ================================================================ texels
def texel_sets(uv, tris, size):
    """For each triangle, the flat indices of its texel set in a
    *size* x *size* image (rows top-down, as glTF UVs address it)."""
    px = np.asarray(uv, float) * size
    out = []
    for t in tris:
        a, b, c = px[t[0]], px[t[1]], px[t[2]]
        x0, y0 = np.floor(np.minimum(np.minimum(a, b), c)).astype(int)
        x1, y1 = np.ceil(np.maximum(np.maximum(a, b), c)).astype(int)
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        P = np.stack([xs.ravel(), ys.ravel()], axis=1)
        area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        inside = np.ones(len(P), bool)
        if abs(area) > 1e-12:
            sgn = 1.0 if area > 0 else -1.0
            for p, q in ((a, b), (b, c), (c, a)):
                e = q - p
                ln = math.hypot(*e)
                if ln < 1e-12:
                    continue
                dist = sgn * (e[0] * (P[:, 1] - p[1]) - e[1] * (P[:, 0] - p[0])) / ln
                inside &= dist >= 0.5
        else:
            inside[:] = False
        P = P[inside]
        if not len(P):
            P = ((a + b + c) / 3.0)[None]
        ix = np.mod(np.floor(P[:, 0]).astype(int), size)
        iy = np.mod(np.floor(P[:, 1]).astype(int), size)
        out.append(np.unique(iy * size + ix))
    return out


def _png(path):
    from PIL import Image
    return np.asarray(Image.open(path).convert("RGB"))


def _srgb_to_linear(v):
    v = np.asarray(v, float) / 255.0
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


# ================================================================ checks
class Report:
    def __init__(self, results):
        self.results = results

    def __call__(self, status, tag, msg):
        self.results.append((status, tag, msg))


def _fmt(p):
    return "[%s]" % ", ".join("%.3f" % c for c in p)


def check(results, asset, adir, body_class):
    """Append (status, tag, message) results for one vehicle asset."""
    R = Report(results)
    edir = os.path.join(adir, "export")
    spec = vi.CLASSES[body_class]
    path = model_facts.sidecar_path(adir, asset)
    problems = model_facts.check_file(path)
    for p in problems:
        R("FAIL", "facts", p)
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        assert tuple(doc) == model_facts.VEHICLE_KEYS
    except (OSError, ValueError, AssertionError):
        R("FAIL", "facts", "no readable version 2 vehicle sidecar: the vehicle checks need it")
        return
    if not problems:
        R("PASS", "facts", "%s: schema, hashes, tiers and id flags, %d wheels, %d lenses, "
                           "%d glass groups, lists match LOD0's ids both ways"
          % (os.path.basename(path), len(doc["wheels"]), len(doc["lamps"]), len(doc["glass"])))
    if doc["source"].get("dirty"):
        R("WARN", "facts", "source.dirty is true: rewrite the sidecar from a committed tree "
                           "(build.py -- facts)")
    if doc["body"].get("class") != body_class:
        R("FAIL", "facts", "body.class is %r, the validator was run for %r"
          % (doc["body"].get("class"), body_class))
    want = "vehicles/%s/%s" % (body_class, asset)
    if doc["path"] != want:
        R("WARN", "facts", "path is %r, not %r: not in the catalog's vehicles/ tree"
          % (doc["path"], want))

    tiers = {}
    for level in vi.LEVELS:
        fp = os.path.join(edir, "%s_lod%d.glb" % (asset, level))
        if not os.path.isfile(fp):
            continue                  # validate_asset's tier check reports it
        try:
            tiers[level] = vi.tier(fp)
        except (ValueError, KeyError) as exc:
            R("FAIL", "LOD%d" % level, "cannot read the tier's accessors: %s" % exc)
    if 0 not in tiers:
        return
    ids = {}
    for level, t in tiers.items():
        ids[level] = check_ids(R, level, t, doc)
    if any(v is None for v in ids.values()):
        R("FAIL", "ids", "the id encoding is wrong; the geometric and texel checks that "
                         "read the ids are skipped")
        return
    check_box(R, tiers, ids, doc, spec)
    check_pairs(R, doc)
    check_presence(R, tiers, ids, doc, body_class)
    check_wheels(R, tiers, ids, doc)
    check_steer(R, tiers, ids, doc)
    check_lamps(R, tiers, ids, doc)
    check_texels(R, asset, adir, tiers, ids, doc, spec)


def check_ids(R, level, t, doc):
    """Check 3 (and the consumer's encoding): returns per-vertex
    (part, surface, paint) and per-triangle (part, surface, paint-all), or
    None when the encoding itself is wrong."""
    tag = "LOD%d" % level
    enc = t["encoding"]
    if enc != [("UNSIGNED_BYTE", True, "VEC4")]:
        R("FAIL", tag, "COLOR_0 is %s, not normalised UNSIGNED_BYTE VEC4 (the consumer "
                       "truncates other forms; run vehicle_ids.convert_color0_to_ubyte)" % enc)
        return None
    raw = np.round(t["color"] * 255.0).astype(int)
    bad = []
    if np.any(raw[:, 3] != 255):
        bad.append("%d vertices have A != 255" % int(np.sum(raw[:, 3] != 255)))
    part, surf, paint = raw[:, 0], raw[:, 1], raw[:, 2]
    if np.any((paint != 0) & (paint != 255)):
        bad.append("B is not 0 or 255 at %d vertices" % int(np.sum((paint != 0) & (paint != 255))))
    nw = len(doc["wheels"])
    if np.any((part < 0) | (part > nw)):
        bad.append("R holds parts %s; the sidecar lists %d wheels"
                   % (sorted(set(part[(part > nw)].tolist())), nw))
    allowed = {0} | set(vi.LAMP_IDS) | set(vi.GLASS_IDS)
    stray = sorted(set(surf.tolist()) - allowed)
    if stray:
        bad.append("G holds ids outside 0, 1..15, 32..47: %s" % stray)
    tri = t["triangles"]
    for ch, name in ((part, "R"), (surf, "G"), (paint, "B")):
        c = ch[tri]
        mixed = np.flatnonzero((c[:, 0] != c[:, 1]) | (c[:, 0] != c[:, 2]))
        if len(mixed):
            centre = t["positions"][tri[mixed[0]]].mean(axis=0)
            bad.append("%d triangles mix %s ids, e.g. at %s (ids %s)"
                       % (len(mixed), name, _fmt(centre), c[mixed[0]].tolist()))
    wrong = (surf != 0) & ((part != 0) | (paint != 0))
    if np.any(wrong):
        bad.append("%d lamp or glass vertices carry a part or paint" % int(wrong.sum()))
    if bad:
        for b in bad:
            R("FAIL", tag, "ids: " + b)
    else:
        R("PASS", tag, "ids: COLOR_0 normalised UNSIGNED_BYTE VEC4, A 255, whole ids, one R, "
                       "G and B per triangle, lamps and glass unpainted body")
    tp = part[tri[:, 0]]
    ts = surf[tri[:, 0]]
    tpaint = np.all(paint[tri] == 255, axis=1)
    return {"part": part, "surface": surf, "paint": paint, "tpart": tp, "tsurf": ts,
            "tpaint": tpaint, "encoding_ok": not bad}


def _mirror_zone(P, doc):
    """Vertices beyond the body's half width: the mirrors."""
    return np.abs(P[:, 0]) > doc["body"]["width_m"] / 2.0 + vi.GROUND_TOL


def check_box(R, tiers, ids, doc, spec):
    """Check 1."""
    Lb, Wb, Hb = spec["box"]
    lowest_wheel = min((w["centre"][1] for w in doc["wheels"]), default=0.0)
    ref = None
    for level, t in sorted(tiers.items()):
        tag = "LOD%d" % level
        P = t["positions"]
        zone = _mirror_zone(P, doc)
        body = P[~zone]
        lo, hi = P.min(axis=0), P.max(axis=0)
        blo, bhi = body.min(axis=0), body.max(axis=0)
        length, width, height = bhi[2] - blo[2], bhi[0] - blo[0], hi[1]
        reach = float(np.abs(P[:, 0]).max())
        bad = []
        if length > Lb + 1e-4:
            bad.append("length %.4f over the box's %.2f" % (length, Lb))
        if width > Wb + 1e-4:
            bad.append("width %.4f (without mirrors) over the box's %.2f" % (width, Wb))
        if height > Hb + 1e-4:
            bad.append("height %.4f over the box's %.2f" % (height, Hb))
        if reach > Wb / 2.0 + spec["mirror"] + 1e-4:
            bad.append("mirrors reach x %.4f, over %.2f + %.2f" % (reach, Wb / 2.0, spec["mirror"]))
        if zone.any():
            Z = P[zone]
            if np.any(Z[:, 1] < lowest_wheel) or np.any(Z[:, 2] < 0.0):
                bad.append("%d vertices outside the body's width are not mirrors (below the "
                           "wheel centres or in the rear half)"
                           % int(np.sum((Z[:, 1] < lowest_wheel) | (Z[:, 2] < 0.0))))
        if abs(lo[1]) > vi.GROUND_TOL:
            bad.append("lowest point y %.4f, not 0" % lo[1])
        cx, cz = (blo[0] + bhi[0]) / 2.0, (blo[2] + bhi[2]) / 2.0
        if abs(cx) > vi.GROUND_TOL or abs(cz) > vi.GROUND_TOL:
            bad.append("origin is not the body's plan centre (centre x %.4f, z %.4f)" % (cx, cz))
        box = (blo[0], bhi[0], blo[2], bhi[2])
        if ref is None:
            ref = box
            if abs(width - doc["body"]["width_m"]) > vi.GROUND_TOL:
                bad.append("body width %.4f is not the sidecar's width_m %s"
                           % (width, doc["body"]["width_m"]))
        elif max(abs(a - b) for a, b in zip(box, ref)) > vi.GROUND_TOL:
            bad.append("plan box x %.3f..%.3f z %.3f..%.3f is not LOD0's" % box)
        if level <= 1 and level in ids:
            for w in doc["wheels"]:
                sel = ids[level]["part"] == w["part"]
                if sel.any() and abs(P[sel, 1].min()) > vi.GROUND_TOL:
                    bad.append("wheel %s's lowest point is y %.4f, not 0"
                               % (w["id"], P[sel, 1].min()))
        for b in bad:
            R("FAIL", tag, "box: " + b)
        if not bad:
            R("PASS", tag, "box: %.3f x %.3f x %.3f in the %s box %.2f x %.2f x %.2f; mirrors "
                           "to x %.3f; on the ground; plan box %s"
              % (length, width, height, doc["body"]["class"], Lb, Wb, Hb, reach,
                 "LOD0's" if level else "centred"))


def check_pairs(R, doc):
    """Check 2."""
    bad, n = [], 0
    wheels = doc["wheels"]
    for a in wheels:
        if a["side"] != "left":
            continue
        b = next((w for w in wheels if w["axle"] == a["axle"] and w["side"] == "right"), None)
        n += 1
        if b is None:
            bad.append("wheel %s has no right partner" % a["id"])
            continue
        ca, cb = a["centre"], b["centre"]
        if abs(ca[0] + cb[0]) > vi.MIRROR_TOL or abs(ca[1] - cb[1]) > vi.MIRROR_TOL or \
                abs(ca[2] - cb[2]) > vi.MIRROR_TOL or \
                abs(a["radius_m"] - b["radius_m"]) > vi.MIRROR_TOL or \
                abs(a["width_m"] - b["width_m"]) > vi.MIRROR_TOL:
            bad.append("wheels %s and %s do not mirror in x" % (a["id"], b["id"]))
    lamps = doc["lamps"]
    singles = []
    for i, a in enumerate(lamps):
        if a["side"] == "centre":
            if abs(a["centre"][0]) > vi.MIRROR_TOL or abs(a["facing"][0]) > 1e-3:
                bad.append("centre lamp %s at x %.4f is not on the centre line"
                           % (a["group"], a["centre"][0]))
            continue
        mate = vi.MIRROR_GROUP.get(a["lamp"], a["lamp"])
        other = "right" if a["side"] == "left" else "left"
        cands = [b for b in lamps if b["lamp"] == mate and b["side"] == other
                 and b["position"] == a["position"]]
        ok = [b for b in cands
              if abs(a["centre"][0] + b["centre"][0]) <= vi.MIRROR_TOL
              and all(abs(a["centre"][k] - b["centre"][k]) <= vi.MIRROR_TOL for k in (1, 2))
              and abs(a["facing"][0] + b["facing"][0]) <= 1e-3
              and all(abs(a["facing"][k] - b["facing"][k]) <= 1e-3 for k in (1, 2))
              and abs(a["width_m"] - b["width_m"]) <= vi.MIRROR_TOL
              and abs(a["height_m"] - b["height_m"]) <= vi.MIRROR_TOL]
        if ok:
            n += a["side"] == "left"
        elif not cands and a["lamp"] in vi.SINGLE_OK:
            singles.append("%s %s %s" % (a["group"], a["position"], a["side"]))
        else:
            bad.append("lens %s %s %s at %s has no mirrored %s partner (%s)"
                       % (a["group"], a["position"], a["side"], _fmt(a["centre"]), other,
                          "none of its group and position on the %s" % other if not cands
                          else "nearest at %s" % _fmt(cands[0]["centre"])))
    for b in bad:
        R("FAIL", "pairs", b)
    if not bad:
        R("PASS", "pairs", "%d wheel and lens pairs mirror in x within %.0f mm; centre "
                           "lenses on x = 0%s" % (n, vi.MIRROR_TOL * 1000,
                                                  "; single lenses: %s" % ", ".join(singles)
                                                  if singles else ""))


def check_presence(R, tiers, ids, doc, body_class):
    """Check 4, and the lists against every tier's ids."""
    nw = len(doc["wheels"])
    lamps = {ln["lamp"] for ln in doc["lamps"]}
    glass = {g["id"] for g in doc["glass"]}
    for level, t in sorted(tiers.items()):
        tag = "LOD%d" % level
        parts = set(ids[level]["tpart"].tolist())
        surfs = set(ids[level]["tsurf"].tolist()) - {0}
        bad, warn = [], []
        if surfs - lamps - glass:
            bad.append("surface ids no sidecar list names: %s" % sorted(surfs - lamps - glass))
        if level <= 1:
            if parts != set(range(nw + 1)):
                bad.append("wheel parts %s, not 1..%d" % (sorted(parts - {0}), nw))
            missing = vi.required_lamps(body_class, surfs)
            if missing:
                bad.append("required lamp ids missing: %s" % missing)
            if (lamps | glass) - surfs:
                bad.append("listed ids missing: %s" % sorted((lamps | glass) - surfs))
            lo, hi = vi.WHEEL_SIDES[level]
            for w in doc["wheels"]:
                sel = ids[level]["part"] == w["part"]
                n = wheel_sides(t["positions"][sel], w["centre"], w["radius_m"])
                if not lo <= n <= hi:
                    bad.append("wheel %s has %d sides, not %d to %d" % (w["id"], n, lo, hi))
        elif level == 2:
            if parts != {0}:
                bad.append("wheel parts %s: from LOD2 the wheels are body (part 0)"
                           % sorted(parts - {0}))
            if lamps - surfs:
                warn.append("lamp ids %s are not kept on flat faces" % sorted(lamps - surfs))
        else:
            if parts != {0} or surfs:
                bad.append("LOD3 carries parts %s and surface ids %s; it has R = 0, G = 0"
                           % (sorted(parts - {0}), sorted(surfs)))
        for b in bad:
            R("FAIL", tag, "presence: " + b)
        for w in warn:
            R("WARN", tag, "presence: " + w)
        if not bad and not warn:
            R("PASS", tag, "presence: parts %s, lamps %s, glass %s"
              % (sorted(parts), sorted(s for s in surfs if s < 32),
                 sorted(s for s in surfs if s >= 32)))


def check_wheels(R, tiers, ids, doc):
    """Check 5."""
    for level in (0, 1):
        if level not in tiers:
            continue
        P, part = tiers[level]["positions"], ids[level]["part"]
        bad = []
        for w in doc["wheels"]:
            c, r, hw = np.asarray(w["centre"]), w["radius_m"], w["width_m"] / 2.0
            d = P - c
            rad, ax = np.hypot(d[:, 1], d[:, 2]), np.abs(d[:, 0])
            mine = part == w["part"]
            out = mine & ((rad > r + vi.CYLINDER_TOL) | (ax > hw + vi.CYLINDER_TOL))
            if out.any():
                k = np.flatnonzero(out)[0]
                bad.append("%d vertices of wheel %s lie outside its cylinder, e.g. %s "
                           "(radius %.4f, offset %.4f)"
                           % (int(out.sum()), w["id"], _fmt(P[k]), rad[k], ax[k]))
            intr = (part == 0) & (rad < r - vi.GROUND_TOL) & (ax < hw - vi.GROUND_TOL)
            if intr.any():
                k = np.flatnonzero(intr)[0]
                bad.append("%d body vertices lie inside wheel %s's cylinder, e.g. %s"
                           % (int(intr.sum()), w["id"], _fmt(P[k])))
        for b in bad:
            R("FAIL", "LOD%d" % level, "wheels: " + b)
        if not bad:
            R("PASS", "LOD%d" % level, "wheels: every wheel vertex inside its sidecar cylinder "
                                       "(+%.0f mm), no body vertex inside one"
              % (vi.CYLINDER_TOL * 1000))


def check_steer(R, tiers, ids, doc):
    """Check 6: every steering wheel turned +-STEER_DEG, and every wheel
    straight ahead (the arch clears the spinning wheel), keeps CLEARANCE
    from every body triangle. The wheel is sampled at its vertices and at
    three points inside each of its edges."""
    for level in (0, 1):
        if level not in tiers:
            continue
        t = tiers[level]
        P, tri = t["positions"], t["triangles"]
        tp = ids[level]["tpart"]
        body = P[tri[tp == 0]]
        worst, bad = [], []
        for w in doc["wheels"]:
            wt = tri[tp == w["part"]]
            if not len(wt):
                continue
            pts = edge_samples(P, wt)
            angles = (0.0, vi.STEER_DEG, -vi.STEER_DEG) if w["steer"] else (0.0,)
            reach = math.hypot(w["radius_m"], w["width_m"] / 2.0) + vi.CLEARANCE + 0.05
            c = np.asarray(w["centre"])
            near = body[np.any(np.linalg.norm(body - c, axis=2) < reach, axis=1)
                        | (np.linalg.norm(body.mean(axis=1) - c, axis=1) < reach)]
            for a in angles:
                q = vi.steer(pts, c, a)
                d, k = closest_distance(q, near)
                i = int(np.argmin(d))
                worst.append((float(d[i]), w["id"], a))
                if d[i] < vi.CLEARANCE:
                    bad.append("wheel %s turned %+.0f deg comes %.1f mm from the body at %s "
                               "(%d sample points under %.0f mm)"
                               % (w["id"], a, d[i] * 1000, _fmt(q[i]),
                                  int(np.sum(d < vi.CLEARANCE)), vi.CLEARANCE * 1000))
        for b in bad:
            R("FAIL", "LOD%d" % level, "steer: " + b)
        if not bad and worst:
            d, wid, a = min(worst)
            R("PASS", "LOD%d" % level, "steer: wheels straight and steering wheels at +-%.0f "
                                       "deg keep %.1f mm or more from the body (nearest: %s at "
                                       "%+.0f deg)" % (vi.STEER_DEG, d * 1000, wid, a))


def check_lamps(R, tiers, ids, doc):
    """Check 7, geometry: each lamp face inside the nearest lens rectangle of
    its id (LOD0..LOD2), and no lens without a face (LOD0, LOD1)."""
    lenses = doc["lamps"]
    geo = []
    for ln in lenses:
        u, v = vi.lens_axes(ln["facing"])
        geo.append((np.asarray(ln["centre"]), u, v, np.asarray(ln["facing"])))
    for level in (0, 1, 2):
        if level not in tiers:
            continue
        t, tag = tiers[level], "LOD%d" % level
        P, tri, ts = t["positions"], t["triangles"], ids[level]["tsurf"]
        hits = np.zeros(len(lenses), int)
        bad = []
        lamp_tris = np.flatnonzero((ts >= 1) & (ts <= 15))
        for k in lamp_tris:
            lid = int(ts[k])
            cand = [i for i, ln in enumerate(lenses) if ln["lamp"] == lid]
            pts = P[tri[k]]
            if not cand:
                bad.append("a face of lamp %d at %s has no lens entry"
                           % (lid, _fmt(pts.mean(axis=0))))
                continue
            i = min(cand, key=lambda i: np.linalg.norm(pts.mean(axis=0) - geo[i][0]))
            c, u, v, f = geo[i]
            d = pts - c
            ln = lenses[i]
            if np.any(np.abs(d @ u) > ln["width_m"] / 2 + LENS_TOL) or \
                    np.any(np.abs(d @ v) > ln["height_m"] / 2 + LENS_TOL) or \
                    np.any(np.abs(d @ f) > LENS_DEPTH):
                bad.append("a face of lamp %d (%s) at %s lies outside the nearest lens "
                           "rectangle, %s %s at %s (%.3f x %.3f)"
                           % (lid, ln["group"], _fmt(pts.mean(axis=0)), ln["side"],
                              ln["position"], _fmt(c), ln["width_m"], ln["height_m"]))
                continue
            hits[i] += 1
        if level <= 1:
            for i in np.flatnonzero(hits == 0):
                ln = lenses[i]
                bad.append("lens entry %s %s %s at %s has no face"
                           % (ln["group"], ln["side"], ln["position"], _fmt(ln["centre"])))
        shown = bad[:12] + (["... and %d more" % (len(bad) - 12)] if len(bad) > 12 else [])
        for b in shown:
            R("FAIL", tag, "lamps: " + b)
        if not bad:
            R("PASS", tag, "lamps: %d lamp faces inside their lens rectangles%s"
              % (len(lamp_tris), ", every lens has a face" if level <= 1 else ""))


def check_texels(R, asset, adir, tiers, ids, doc, spec):
    """Checks 7 (lit lenses), 8 and 9, and the glass band."""
    try:
        import PIL  # noqa: F401
    except ImportError:
        R("FAIL", "tex", "Pillow unavailable: the vehicle texel checks cannot run")
        return
    edir = os.path.join(adir, "export")
    emit = _png(os.path.join(edir, "%s_emission.png" % asset))
    size = emit.shape[0]
    gpath = os.path.join(adir, vi.GLASS_TEXELS)
    if not os.path.isfile(gpath):
        R("FAIL", "glass", "%s is missing: the texture generator records the glass texels "
                           "there (vehicle_ids.save_glass_texels)" % vi.GLASS_TEXELS)
        return
    glass = vi.load_glass_texels(gpath).ravel()
    if glass.size != size * size:
        R("FAIL", "glass", "%s is not the atlas's size %d" % (vi.GLASS_TEXELS, size))
        return
    if size > spec["texture"]:
        R("FAIL", "tex", "atlas %d over the class's %d" % (size, spec["texture"]))
    lit = emit.reshape(-1, 3).max(axis=1) > BLACK
    if not glass.any():
        R("FAIL", "glass", "%s marks no glass texels" % vi.GLASS_TEXELS)
    elif np.any(glass & ~lit):
        R("FAIL", "glass", "%d glass texels are black in the emission: the lit cabin "
                           "covers every glass texel" % int(np.sum(glass & ~lit)))
    else:
        R("PASS", "glass", "%d glass texels recorded, every one lit in the emission"
          % int(glass.sum()))

    sets = {lv: texel_sets(t["uv"], t["triangles"], size) for lv, t in tiers.items()}
    lamp_texels = np.zeros(size * size, bool)
    for lv in (0, 1):
        if lv not in tiers:
            continue
        ts = ids[lv]["tsurf"]
        for k in np.flatnonzero((ts >= 1) & (ts <= 15)):
            lamp_texels[sets[lv][k]] = True
    grid = lamp_texels.reshape(size, size)
    grow = grid.copy()
    grow[1:] |= grid[:-1]
    grow[:-1] |= grid[1:]
    grow[:, 1:] |= grid[:, :-1]
    grow[:, :-1] |= grid[:, 1:]
    lamp_texels = grow.ravel()

    for lv, t in sorted(tiers.items()):
        tag = "LOD%d" % lv
        ts = ids[lv]["tsurf"]
        cen = t["positions"][t["triangles"]].mean(axis=1)
        dark_lens, glass_off, glass_dark, unmarked, glow = [], [], [], [], []
        for k, s in enumerate(sets[lv]):
            g = int(ts[k])
            if 1 <= g <= 15:
                if np.any(~lit[s]):
                    dark_lens.append((g, cen[k]))
            elif g >= 32:
                if np.any(~glass[s]):
                    glass_off.append((g, cen[k], int(np.sum(~glass[s]))))
                if np.any(~lit[s]):
                    glass_dark.append((g, cen[k]))
            else:
                if lv <= 1 and np.any(glass[s]):
                    unmarked.append((cen[k], int(np.sum(glass[s]))))
                stray = lit[s] & ~glass[s] & ~lamp_texels[s]
                if np.any(stray):
                    glow.append((cen[k], int(stray.sum())))
        for what, rows, fmt in (
                ("lamps", dark_lens, lambda r: "a face of lamp %d at %s samples black emission "
                                               "texels" % (r[0], _fmt(r[1]))),
                ("glass", glass_off, lambda r: "a glass face (%d) at %s samples %d non-glass "
                                               "texels" % (r[0], _fmt(r[1]), r[2])),
                ("glass", glass_dark, lambda r: "a glass face (%d) at %s samples black emission"
                                                % (r[0], _fmt(r[1]))),
                ("glass", unmarked, lambda r: "a face without a glass id at %s samples %d glass "
                                              "texels" % (_fmt(r[0]), r[1])),
                ("emission", glow, lambda r: "a plain face at %s samples %d lit emission "
                                             "texels that are neither lamp nor glass"
                                             % (_fmt(r[0]), r[1]))):
            for r in rows[:6]:
                R("FAIL", tag, "%s: %s" % (what, fmt(r)))
            if len(rows) > 6:
                R("FAIL", tag, "%s: ... and %d more faces" % (what, len(rows) - 6))
        if not (dark_lens or glass_off or glass_dark or unmarked or glow):
            R("PASS", tag, "texels: lenses lit, glass faces on glass texels and lit%s, "
                           "plain faces dark in the emission"
              % (", no unmarked glass" if lv <= 1 else ""))

    orm = _png(os.path.join(edir, "%s_orm.png" % asset)).reshape(-1, 3)
    rough = orm[glass, 1].mean() / 255.0 if glass.any() else 0.0
    metal = orm[glass, 2].mean() / 255.0 if glass.any() else 0.0
    for v in doc["variants"]:
        alb = _png(os.path.join(edir, v["albedo"]["file"])).reshape(-1, 3).astype(float)
        name = v["albedo"]["file"]
        if glass.any():
            mean = alb[glass].mean()
            ok = GLASS_SRGB[0] <= mean <= GLASS_SRGB[1] and \
                GLASS_ROUGH[0] <= rough <= GLASS_ROUGH[1] and metal < 0.02
            R("PASS" if ok else "FAIL", "glass",
              "%s: glass sRGB %.0f (band %.0f-%.0f), roughness %.3f, metallic %.2f"
              % (name, mean, GLASS_SRGB[0], GLASS_SRGB[1], rough, metal))
        if not v["paint"]:
            R("PASS", "paint", "%s: a full-colour livery (paint false), not held to neutral"
              % name)
            continue
        chroma, level, faces, bad = [], [], 0, []
        for lv, t in sorted(tiers.items()):
            cen = t["positions"][t["triangles"]].mean(axis=1)
            for k in np.flatnonzero(ids[lv]["tpaint"]):
                px = alb[sets[lv][k]]
                ch = float((px.max(axis=1) - px.min(axis=1)).mean())
                faces += 1
                chroma.append(ch)
                level.append(float(_srgb_to_linear(px).mean()))
                if ch > NEUTRAL_CHROMA:
                    bad.append((lv, cen[k], ch))
        for lv, c, ch in bad[:6]:
            R("FAIL", "paint", "%s LOD%d: a painted face at %s has mean chroma %.1f (over %.0f): "
                               "painted panels are neutral grey" % (name, lv, _fmt(c), ch,
                                                                    NEUTRAL_CHROMA))
        if len(bad) > 6:
            R("FAIL", "paint", "... and %d more painted faces" % (len(bad) - 6))
        if faces and not bad:
            lvl = float(np.mean(level))
            status = "PASS" if PAINT_LEVEL[0] <= lvl <= PAINT_LEVEL[1] else "WARN"
            R(status, "paint", "%s: %d painted faces neutral (mean chroma %.1f), grey %.2f "
                               "linear (about 0.75 wanted)"
              % (name, faces, float(np.mean(chroma)), lvl))
        elif not faces:
            R("WARN", "paint", "no painted faces (B = 1) on any tier")


if __name__ == "__main__":
    results = []
    adir = os.path.abspath(sys.argv[1])
    check(results, os.path.basename(adir.rstrip("/")), adir, sys.argv[2])
    order = {"FAIL": 0, "WARN": 1, "MANUAL": 2, "SKIP": 3, "PASS": 4}
    for status, tag, msg in sorted(results, key=lambda r: order[r[0]]):
        print("%-7s %-8s %s" % (status, tag, msg))
    sys.exit(1 if any(r[0] == "FAIL" for r in results) else 0)
