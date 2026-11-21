# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of puistopenkki_slatted, both LOD tiers.

A plain Nordic municipal park bench: two cast end frames carrying four seat
slats and three back slats. Dimensions, atlas layout and textures live in
bench_atlas.py beside this file. Rebuild from the repository root, textures
first (system Python with scipy and Pillow), then the tiers in Blender:

    python3 props/street_furniture/puistopenkki_slatted/bench_atlas.py export
    blender --background --python props/street_furniture/puistopenkki_slatted/build.py

The Blender step builds both tiers, exports them, renders preview.png and
saves source.blend. A small prop ships no facts sidecar, no emission map and
no variants.png (asset_build.Asset with night_lit=False).

Every tier is a set of disjoint closed solids in one mesh, not a union:

    LOD0  two end frames, each one extruded 11-point casting profile (40
          triangles), four seat slats and three back slats, each a box (12):
          164 triangles. The slats rest on the frames' rail and stay faces;
          the gaps between them are real.
    LOD1  the frames as 9-point profiles (32), the seat and the back each one
          right-triangle wedge (8) mapped onto composites of the slats with
          the gaps painted dark: 80 triangles.

Pivot: on the ground at the centre of the four feet (asset_build.Asset's
pivot=, authored at the build origin). Front: the seat's front toward -Y.
"""

import importlib
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import bench_atlas as L  # noqa: E402  (the dimensions and the atlas layout)
importlib.reload(L)       # an interactive session must not keep a stale layout

sys.path.insert(0, L.SCRIPTS)
import asset_build  # noqa: E402

asset_build.check_toolchain()
ASSET = L.ASSET
LEVELS = (0, 1)
A = asset_build.Asset(ASSET, HERE, L.VARIANTS, L.DEFAULT_VARIANT,
                      levels=LEVELS, night_lit=False, pivot=(0.0, 0.0, 0.0))


# ================================================================ builder
class Builder:
    """One closed solid, UVs set as faces are made (atlas pixels)."""

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cache = {}

    def v(self, co):
        key = tuple(round(c, 6) for c in co)
        vert = self.cache.get(key)
        if vert is None:
            vert = self.bm.verts.new(co)
            self.cache[key] = vert
        return vert

    def face(self, cos, uvfn):
        f = self.bm.faces.new([self.v(co) for co in cos])
        for loop, co in zip(f.loops, cos):
            u, w = uvfn(co)
            loop[self.uv].uv = (u / L.ATLAS, w / L.ATLAS)
        return f


def patch(rect):
    x, y, w, h = rect
    return lambda co: (x + w / 2.0, y + h / 2.0)


def along(x0):
    """U along a slat, from its -X end."""
    return lambda co: x0 + L.m(co[0] + L.HL)


# ================================================================ solids
def seat_slat(i):
    y0, y1 = L.SEAT_SLATS[i]
    z0, z1 = L.Z_RAIL, L.Z_SEAT
    x0, rows = L.seat_faces(i)
    U = along(x0)
    fr, top, bk, un = (L.face_rows(rows, f)[0] for f in ("front", "top", "back", "under"))
    B = Builder()
    xa, xb = -L.HL, L.HL
    B.face([(xa, y0, z0), (xb, y0, z0), (xb, y0, z1), (xa, y0, z1)],
           lambda co: (U(co), fr + L.m(co[2] - z0)))
    B.face([(xa, y0, z1), (xb, y0, z1), (xb, y1, z1), (xa, y1, z1)],
           lambda co: (U(co), top + L.m(co[1] - y0)))
    B.face([(xa, y1, z1), (xb, y1, z1), (xb, y1, z0), (xa, y1, z0)],
           lambda co: (U(co), bk + L.m(z1 - co[2])))
    B.face([(xa, y1, z0), (xb, y1, z0), (xb, y0, z0), (xa, y0, z0)],
           lambda co: (U(co), un + L.m(y1 - co[1])))
    for x in (xa, xb):
        B.face([(x, y0, z0), (x, y0, z1), (x, y1, z1), (x, y1, z0)], patch(L.END_R))
    return B


def back_slat(i):
    s0, s1 = L.BACK_SLATS[i]
    t0, t1 = 0.0, L.BACK_T
    x0, rows = L.back_faces(i)
    U = along(x0)
    fr, top, rr, ft = (L.face_rows(rows, f)[0] for f in ("front", "top", "rear", "foot"))

    def P(x, s, t):
        y, z = L.stay_point(s, t)
        return (x, y, z)

    def st(co):
        return L.stay_coords(co[1], co[2])
    B = Builder()
    xa, xb = -L.HL, L.HL
    B.face([P(xa, s0, t1), P(xb, s0, t1), P(xb, s1, t1), P(xa, s1, t1)],
           lambda co: (U(co), fr + L.m(st(co)[0] - s0)))
    B.face([P(xa, s1, t1), P(xb, s1, t1), P(xb, s1, t0), P(xa, s1, t0)],
           lambda co: (U(co), top + L.m(t1 - st(co)[1])))
    B.face([P(xa, s1, t0), P(xb, s1, t0), P(xb, s0, t0), P(xa, s0, t0)],
           lambda co: (U(co), rr + L.m(s1 - st(co)[0])))
    B.face([P(xa, s0, t0), P(xb, s0, t0), P(xb, s0, t1), P(xa, s0, t1)],
           lambda co: (U(co), ft + L.m(st(co)[1])))
    for x in (xa, xb):
        B.face([P(x, s0, t0), P(x, s0, t1), P(x, s1, t1), P(x, s1, t0)], patch(L.END_R))
    return B


def frame(side, outline):
    """One end frame: *outline* [(name, (y, z), perimeter in, perimeter
    out)] counter-clockwise seen from +X, extruded across the casting's
    thickness. Faces on the frame region by (y, z); edges on the edge
    strip, U the LOD0 perimeter distance, V across the casting."""
    xin, xout = side * L.FX0, side * L.FX1
    B = Builder()

    def face_uv(co):
        return L.frame_uv(co[1], co[2])
    pts = [p for _, p, _, _ in outline]
    outer = [(xout, y, z) for y, z in pts]
    inner = [(xin, y, z) for y, z in pts]
    B.face(outer if side > 0 else list(reversed(outer)), face_uv)
    B.face(list(reversed(inner)) if side > 0 else inner, face_uv)
    ex, ev = L.EDGE_R
    n = len(outline)
    for k in range(n):
        (_, a, _, sa), (_, b, sb, _) = outline[k], outline[(k + 1) % n]
        quad = [(xin, a[0], a[1]), (xin, b[0], b[1]), (xout, b[0], b[1]),
                (xout, a[0], a[1])]
        uvs = {}
        for co, s in zip(quad, (sa, sb, sb, sa)):
            uvs[co] = (ex + L.m(s), ev + L.m(abs(co[0]) - L.FX0))
        B.face(quad, lambda co, uvs=uvs: uvs[co])
    return B


def outline0():
    out = []
    for name, p in L.PROFILE0:
        s = L.PERIM[name]
        out.append((name, p, s, s))
    out[0] = (out[0][0], out[0][1], L.PERIM_LEN, 0.0)
    return out


def seat_wedge():
    """LOD1's seat: a right-triangle prism, the top and the front face where
    the slats' are, the underside sloping from the front's foot up to the
    stay along the frame's raised rail top."""
    yf, yt = L.SEAT_WEDGE
    z0, z1 = L.Z_RAIL, L.Z_SEAT
    xs, vs = L.SEAT_COMP
    x0, rows = L.seat_faces(0)
    fr = L.face_rows(rows, "front")[0]
    B = Builder()
    xa, xb = -L.HL, L.HL
    B.face([(xa, yf, z0), (xb, yf, z0), (xb, yf, z1), (xa, yf, z1)],
           lambda co: (x0 + L.m(co[0] + L.HL), fr + L.m(co[2] - z0)))
    B.face([(xa, yf, z1), (xb, yf, z1), (xb, yt, z1), (xa, yt, z1)],
           lambda co: (xs + L.m(co[0] + L.HL), vs + L.m(co[1] - yf)))
    B.face([(xa, yt, z1), (xb, yt, z1), (xb, yf, z0), (xa, yf, z0)], patch(L.UNDER_R))
    B.face([(xa, yf, z0), (xa, yf, z1), (xa, yt, z1)], patch(L.END_R))
    B.face([(xb, yf, z0), (xb, yt, z1), (xb, yf, z1)], patch(L.END_R))
    return B


def back_wedge():
    """LOD1's back: a right-triangle prism on the stays, its rear face the
    slats' rear faces, full thickness at the top edge, its sloping front
    face the slats' front faces."""
    s0, s1, t1 = L.BACK_S0, L.BACK_S1, L.BACK_T
    xf, vf = L.BACK_COMP_F
    xr, vr = L.BACK_COMP_R
    x2, rows = L.back_faces(L.BACK_N - 1)
    top = L.face_rows(rows, "top")[0]

    def P(x, s, t):
        y, z = L.stay_point(s, t)
        return (x, y, z)

    def st(co):
        return L.stay_coords(co[1], co[2])
    B = Builder()
    xa, xb = -L.HL, L.HL
    B.face([P(xa, s0, 0.0), P(xb, s0, 0.0), P(xb, s1, t1), P(xa, s1, t1)],
           lambda co: (xf + L.m(co[0] + L.HL), vf + L.m(st(co)[0] - s0)))
    B.face([P(xa, s1, t1), P(xb, s1, t1), P(xb, s1, 0.0), P(xa, s1, 0.0)],
           lambda co: (x2 + L.m(co[0] + L.HL), top + L.m(t1 - st(co)[1])))
    B.face([P(xa, s1, 0.0), P(xb, s1, 0.0), P(xb, s0, 0.0), P(xa, s0, 0.0)],
           lambda co: (xr + L.m(co[0] + L.HL), vr + L.m(s1 - st(co)[0])))
    B.face([P(xa, s0, 0.0), P(xa, s1, t1), P(xa, s1, 0.0)], patch(L.END_R))
    B.face([P(xb, s0, 0.0), P(xb, s1, 0.0), P(xb, s1, t1)], patch(L.END_R))
    return B


def parts(level):
    if level == 0:
        return ([frame(s, outline0()) for s in (-1, 1)]
                + [seat_slat(i) for i in range(L.SEAT_N)]
                + [back_slat(i) for i in range(L.BACK_N)])
    return [frame(s, L.PROFILE1) for s in (-1, 1)] + [seat_wedge(), back_wedge()]


# ================================================================ tiers
def check_layout():
    """The atlas fits, and the parts stack as a bench should."""
    problems = list(L.check_layout())
    if L.SEAT_SLATS[-1][1] >= L.J[0]:
        problems.append("the rear seat slat runs into the stay")
    lowest = L.stay_point(L.BACK_S0, L.BACK_T)[1]
    if lowest <= L.Z_SEAT + 0.03:
        problems.append("the lowest back slat sits on the seat (z %.3f)" % lowest)
    if L.STAY_TOP < L.BACK_S1:
        problems.append("the top back slat stands above the stay")
    if not (L.FX0 < L.FRAME_X < L.FX1 < L.HL):
        problems.append("the frames are not under the slats")
    return problems


def build_lod(level):
    """One tier as an unlinked object: every part a closed solid, joined
    into one mesh, triangulated, checked closed."""
    bm = bmesh.new()
    for B in parts(level):
        bmesh.ops.recalc_face_normals(B.bm, faces=B.bm.faces[:])
        me = bpy.data.meshes.new("tmp")
        B.bm.to_mesh(me)
        B.bm.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY',
                          ngon_method='EAR_CLIP')
    flat = [f for f in bm.faces if f.calc_area() < 1e-8]
    open_ = [e for e in bm.edges if len(e.link_faces) != 2]
    if flat or open_:
        raise ValueError("%s LOD%d: %d zero-area faces, %d edges not on two faces"
                         % (ASSET, level, len(flat), len(open_)))
    name = "{}_LOD{}".format(ASSET, level)
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    return bpy.data.objects.new(name, me)


def build_all():
    return A.build_all(check_layout, build_lod)


if __name__ == "__main__":
    A.main(build_all)
