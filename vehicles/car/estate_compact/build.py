# SPDX-License-Identifier: GPL-3.0-or-later

"""estate_compact: a generic Nordic family estate car, all four tiers.

    python3 estate_atlas.py export
    blender --background --python build.py

The shape, the tiers and the UVs are estate_shape.py's; this file turns its
face lists into vehicle_build pieces: the body shell (conformed, its wheel
arches cut by exact booleans whose cutter faces become the dark liners,
creases marked sharp), the mirrors and roof rails as their own closed
solids, and the wheels as parts with their origins at the wheel centres.
"""

import importlib
import math
import os
import sys

import bmesh
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import estate_shape as S  # noqa: E402
importlib.reload(S)
import estate_atlas as A  # noqa: E402
importlib.reload(A)
sys.path.insert(0, A.SCRIPTS)
import asset_build  # noqa: E402
import model_facts  # noqa: E402
import vehicle_build as VB  # noqa: E402
import vehicle_ids as vi  # noqa: E402

asset_build.check_toolchain()
V = VB.VehicleAsset(S.ASSET, HERE, A.VARIANTS, A.DEFAULT_VARIANT, "car",
                    preview_paint=(0.22, 0.30, 0.40))

CREASE_DEG = 50.0           # an edge sharper than this shades as a crease


def builder(faces, conform=True):
    """A vehicle_build.Builder holding *faces*, T-junctions conformed away
    and any edge left without a face removed."""
    B = VB.Builder(S.ATLAS)
    for f in faces:
        uvs = dict(zip(f.pts, f.uv))
        B.face(f.pts, lambda co, d=uvs: d[tuple(co)], surface=f.surface, paint=f.paint,
               smooth=f.smooth)
    if conform:
        VB.conform(B)
        loose = [e for e in B.bm.edges if not e.link_faces]
        if loose:
            bmesh.ops.delete(B.bm, geom=loose, context='EDGES')
    return B


def crease(obj, lines=()):
    """Mark the creases sharp: edges past CREASE_DEG, every edge where
    glass meets something else, where unpainted trim meets paint, and the
    edges along *lines* (pairs of points: the shape's own crease lines)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    key = lambda co: tuple(round(v, 3) for v in co)  # noqa: E731
    marked = {frozenset((key(p), key(q))) for p, q in lines}
    surf = bm.faces.layers.int.get(VB.SURFACE)
    paint = bm.faces.layers.int.get(VB.PAINT)
    lim = math.radians(CREASE_DEG)
    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        a, b = e.link_faces
        glass = [f[surf] >= 32 if surf else False for f in (a, b)]
        # a trim part meeting the paint (a bumper lip, the grille) is its
        # own part: its edge shades crisp
        trim = (paint is not None and surf is not None and a[surf] == 0 and b[surf] == 0
                and a[paint] != b[paint])
        line = frozenset(key(v.co) for v in e.verts) in marked
        e.smooth = not (e.calc_face_angle() > lim or glass[0] != glass[1] or trim or line)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def body(level, t):
    obj = VB._object("tmp_body", builder(t["body"]))
    if t["cutters"]:
        cutters = [VB._object("tmp_cut", builder(f, conform=False)) for f in t["cutters"]]
        obj = asset_build.difference(obj, cutters, snap=asset_build.SNAP)
    return crease(obj, S.crease_edges(level))


def build_lod(level):
    t = S.tier(level)
    pieces = [VB.Piece("body", body(level, t))]
    for faces in t["mirrors"]:
        pieces.append(VB.Piece("mirror", crease(VB._object("tmp_mirror", builder(faces)))))
    for faces in t["rails"]:
        pieces.append(VB.Piece("body", builder(faces, conform=False)))
    for faces in t.get("axles", []):
        pieces.append(VB.Piece("body", builder(faces, conform=False)))
    for part, centre, steer, faces in t["wheels"]:
        w = crease(VB._object("tmp_wheel", builder(faces, conform=False)))
        pieces.append(VB.Piece("wheel", w, part=part, centre=centre, steer=steer))
    return pieces


def check_layout():
    """What the tiers would get wrong before any is built: the class box,
    the wheels in their arches, the mirrors' reach, the lens depths."""
    problems = []
    spec = vi.CLASSES["car"]
    if S.L > spec["box"][0] or 2 * S.HW > spec["box"][1]:
        problems.append("body %.3f x %.3f is over the car box" % (S.L, 2 * S.HW))
    reach = max(abs(p[0]) for f in S.mirror_faces(0, 1) for p in f.pts) - S.HW
    if reach > spec["mirror"]:
        problems.append("mirrors reach %.3f past the body, over %.2f" % (reach, spec["mirror"]))
    # a front wheel turned 35 degrees: its innermost point against the liner
    a = math.radians(vi.STEER_DEG)
    inner = S.WHEEL_X - (S.WHEEL_R * math.sin(a) + S.TYRE_W / 2 * math.cos(a))
    if inner - S.LINER_X < vi.CLEARANCE + 0.005:
        problems.append("a turned wheel comes within %.3f of the liner" % (inner - S.LINER_X))
    if S.ARCH_R - math.hypot(S.WHEEL_R, S.TYRE_W / 2 * math.sin(a)) - S.ARCH_DZ < 0.02:
        problems.append("arch radius %.3f leaves under 20 mm round a turned tyre" % S.ARCH_R)
    # every LOD0 lens no deeper than the validator's lens rectangle allows
    faces = [f for f in S.tier(0)["body"] + S.mirror_faces(0, 1) if f.kind == "lamp"]
    for lid in sorted({f.surface for f in faces}):
        for grp in S._components([f for f in faces if f.surface == lid]):
            pts = np.array([p for f in grp for p in f.pts])
            n = sum((S.outward(f) * S._area(f) for f in grp), np.zeros(3))
            n /= np.linalg.norm(n)
            d = pts @ n
            if d.max() - d.mean() > 0.045 or d.mean() - d.min() > 0.045:
                problems.append("lamp %d lens at %s is %.3f m deep along its facing"
                                % (lid, np.round(pts.mean(axis=0), 2), d.max() - d.min()))
    return problems


def build_all():
    return V.build_all(check_layout, build_lod)


def facts():
    """No load box. The doors from the shut lines the atlas draws: two a
    side on the door skin, which is the plan box's side, and the tailgate
    between its cut lines at the bumper, on the plan box's rear."""
    s0, s1, s2 = A.DOOR_S
    gate = S.cap_x("rear", "S4", "RE")
    return {"cargo": None,
            "doors": model_facts.side_doors("front", s0 - S.HL, s1 - S.HL)
            + model_facts.side_doors("rear", s1 - S.HL, s2 - S.HL)
            + [model_facts.rear_door(-gate, gate)]}


if __name__ == "__main__":
    V.main(build_all, facts)
