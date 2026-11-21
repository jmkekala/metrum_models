# SPDX-License-Identifier: GPL-3.0-or-later

"""estate_compact: the 512 atlas, painted from the shape's own faces.

    python3 estate_atlas.py export

writes export/estate_compact_albedo_plain.png, _orm.png, _normal.png and
_emission.png, and glass_texels.png beside this file. The layout is
estate_shape.py's: every body face of every tier is rasterised into its
projected island in its kind's material, LOD0 last, so the atlas and the
mesh cannot drift apart; panel gaps, handles, the grille, lamp graphics,
plates, wheels and wear are painted over that from 3D positions mapped
through the same projections.
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def _scripts(d):
    while not os.path.isfile(os.path.join(d, "scripts", "asset_build.py")):
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError("no scripts/ above %s" % HERE)
        d = parent
    return os.path.join(d, "scripts")


SCRIPTS = _scripts(HERE)
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import atlas  # noqa: E402
import estate_shape as S  # noqa: E402
import glazing  # noqa: E402
import vehicle_ids as vi  # noqa: E402

ASSET = S.ASSET
ATLAS = S.ATLAS
VARIANTS = [("plain", True)]
DEFAULT_VARIANT = "plain"

# ================================================================ materials
M = dict(paint=1, lip=2, grille=3, intake=4, pillar=5, sail=5, under=6, liner=7, plate=8,
         plate_rim=9, glass=10, tread=11, tyre=12, rim=13, wheel_inner=14, mirror_glass=15,
         rail=16, seal=17, rim_dark=18, gap=19, handle=20, lens_body=21, chrome=22,
         glass_dark=23, pic_red=24, pic_amber=25, pic_white=26, disc=27)
M_LENS = {lid: 40 + lid for lid in range(1, 16)}
SRGB = {M["paint"]: (228, 228, 228), M["lip"]: (40, 41, 42), M["grille"]: (24, 25, 26),
        M["intake"]: (30, 31, 32), M["pillar"]: (16, 17, 18), M["under"]: (20, 20, 21),
        M["liner"]: (38, 38, 39), M["plate"]: (238, 238, 234), M["plate_rim"]: (40, 42, 44),
        M["glass"]: glazing.BASE, M["tread"]: (40, 40, 40), M["tyre"]: (30, 30, 31),
        M["rim"]: (186, 188, 190), M["wheel_inner"]: (22, 22, 23),
        M["mirror_glass"]: (120, 124, 128), M["rail"]: (52, 53, 55), M["seal"]: (22, 22, 23),
        M["rim_dark"]: (60, 61, 63), M["gap"]: (120, 120, 120), M["handle"]: (205, 205, 205),
        M["lens_body"]: (110, 112, 114), M["chrome"]: (176, 178, 180),
        M["glass_dark"]: (44, 47, 50), M["pic_red"]: (110, 30, 28), M["pic_amber"]: (150, 90, 30),
        M["pic_white"]: (165, 167, 165), M["disc"]: (24, 24, 26)}
ROUGH = {M["paint"]: (0.32, 0.0), M["lip"]: (0.86, 0.0), M["grille"]: (0.55, 0.0),
         M["intake"]: (0.62, 0.0), M["pillar"]: (0.18, 0.0), M["under"]: (0.9, 0.0),
         M["liner"]: (0.92, 0.0), M["plate"]: (0.45, 0.0), M["plate_rim"]: (0.5, 0.0),
         M["glass"]: (glazing.ROUGHNESS, 0.0), M["tread"]: (0.9, 0.0), M["tyre"]: (0.88, 0.0),
         M["rim"]: (0.35, 0.85), M["wheel_inner"]: (0.85, 0.0), M["mirror_glass"]: (0.06, 0.9),
         M["rail"]: (0.5, 0.0), M["seal"]: (0.6, 0.0), M["rim_dark"]: (0.5, 0.0),
         M["gap"]: (0.5, 0.0), M["handle"]: (0.32, 0.0), M["lens_body"]: (0.2, 0.0),
         M["chrome"]: (0.25, 0.0), M["glass_dark"]: (0.1, 0.0), M["pic_red"]: (0.2, 0.0),
         M["pic_amber"]: (0.2, 0.0), M["pic_white"]: (0.2, 0.0), M["disc"]: (0.9, 0.0)}
LENS_UNLIT = {"red": (128, 28, 26), "amber": (196, 112, 30), "white": (172, 175, 174)}
for _lid in range(1, 16):
    SRGB[M_LENS[_lid]] = LENS_UNLIT[vi.lamp_colour(_lid)]
    ROUGH[M_LENS[_lid]] = (0.12, 0.0)          # glossy lenses: the ORM's alone
CABIN_LEVEL = 0.25
KIND_MID = {"paint": M["paint"], "lip": M["lip"], "grille": M["grille"],
            "intake": M["intake"], "pillar": M["pillar"], "sail": M["sail"],
            "under": M["under"], "liner": M["liner"], "reflector": M["pic_red"],
            "seal": M["seal"]}


# ================================================================ raster
def polygon(c, pts, mid=None, shade=None, ao=None, height=None):
    """Fill a polygon given in atlas pixels (even-odd, per sample)."""
    pts = np.asarray(pts, float)
    x0, y0 = pts.min(axis=0) - 1
    x1, y1 = pts.max(axis=0) + 1

    def test(X, Y):
        inside = np.zeros(X.shape, bool)
        n = len(pts)
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            cond = (ay > Y) != (by > Y)
            with np.errstate(divide="ignore", invalid="ignore"):
                xc = ax + (Y - ay) * (bx - ax) / (by - ay)
            inside ^= cond & (X < xc)
        return inside
    c.shape(x0, x1, y0, y1, test, mid, shade, ao, height)


def dilated(pts, r):
    """A polygon grown by r pixels about its centroid (enough for the
    convex cells used here)."""
    pts = np.asarray(pts, float)
    cen = pts.mean(axis=0)
    d = pts - cen
    ln = np.linalg.norm(d, axis=1, keepdims=True)
    return cen + d * (1 + r / np.maximum(ln, 1e-6))


def tiers():
    return {lv: S.tier(lv) for lv in S.LEVELS_BUILT}


# ================================================================ paint
def paint():
    c = atlas.Canvas(size=ATLAS, ss=atlas.SS, ppm=S.PPM)
    T = tiers()
    order = sorted(T, reverse=True)          # LOD0 last: it owns the texels
    # the projected islands start as paint, so a face sampling past its own
    # outline (a pillar's edge by the windscreen) finds body colour there
    for rect in (S.R_SIDE_L, S.R_SIDE_R, S.R_TOP, S.R_FRONT, S.R_REAR):
        x, y, w, h = rect
        c.paint(x, x + w, y, y + h, mid=M["paint"])
    # body islands, by face kind
    for lv in order:
        for f in T[lv]["body"]:
            if f.island in ("side_l", "side_r", "top", "front", "rear", "under"):
                polygon(c, dilated(f.uv, 0.6), mid=KIND_MID.get(f.kind, M["paint"]))
        for cut in T[lv]["cutters"]:
            for f in cut:
                polygon(c, f.uv, mid=M["liner"])
    # unpainted trim (lips, grille, intake, pillars, cowl) a texel past its
    # outline: a face filters a texel beyond its edge, and a trim face must
    # find trim there, never paint (a light fringe); paint finding trim
    # reads as a thin dark gap line
    for lv in (1, 0):
        for f in T[lv]["body"]:
            if f.island in ("side_l", "side_r", "top", "front", "rear") and not f.paint \
                    and f.kind in KIND_MID:
                polygon(c, dilated(f.uv, 1.1), mid=KIND_MID[f.kind])
    lod3_gaps(c, T)
    # glass: the union of every tier's panes, a pixel wide
    for lv in order:
        for f in T[lv]["body"]:
            if f.kind == "glass":
                polygon(c, dilated(f.uv, 1.2), mid=M["glass"])
    paint_side(c)
    paint_top(c)
    paint_front(c)
    paint_rear(c)
    paint_lenses(c)
    paint_plate(c)
    paint_wheels(c)
    # LOD3's uniform blocks: light paint at about the tiers' painted level,
    # dark glass, dark under-body
    for rect, mid, sh in ((S.R_L3_PAINT, M["paint"], 0.93), (S.R_L3_GLASS, M["glass_dark"], 1.0),
                          (S.R_L3_UNDER, M["under"], 1.0)):
        x, y, w, h = rect
        c.paint(x, x + w, y, y + h, mid=mid, shade=sh, height=0.0)
    for name, rect in (("paint", S.R_FLAT_PAINT), ("mirror_glass", S.R_MIRROR_GLASS),
                       ("rail", S.R_RAIL), ("under", S.R_UNDER),
                       ("pic_red", S.R_REFLECTOR)):
        x, y, w, h = rect
        c.paint(x, x + w, y, y + h, mid=M[name])
    return c


# ---------------------------------------------------------------- fields
def field(c, rect):
    """(rows, cols, U, V): a rect's samples, U and V in metres from the
    rect's mapped origin (the projections' one-pixel offset)."""
    x, y, w, h = rect
    sy, sx, Y_, X_ = c.field(x, x + w, y, y + h)
    return sy, sx, (X_ - x - 1.0) / S.PPM, (Y_ - y - 1.0) / S.PPM


class Region:
    """Masks over one island in world terms, painted in place."""

    def __init__(self, c, rect):
        self.c = c
        self.sy, self.sx, self.U, self.V = field(c, rect)

    def mid(self):
        return self.c.mid[self.sy, self.sx]

    def put(self, m, mid=None, shade=None, add_h=None, ao=None, height=None, on=None):
        if on is not None:
            m = m & np.isin(self.mid(), on)
        if not np.any(m):
            return
        c, sy, sx = self.c, self.sy, self.sx
        if mid is not None:
            a = c.mid[sy, sx]
            a[m] = mid
            c.mid[sy, sx] = a
        if shade is not None:
            a = c.shade[sy, sx]
            a[m] *= shade
            c.shade[sy, sx] = a
        if height is not None:
            a = c.height[sy, sx]
            a[m] = height
            c.height[sy, sx] = a
        if add_h is not None:
            a = c.height[sy, sx]
            a[m] += add_h
            c.height[sy, sx] = a
        if ao is not None:
            a = c.ao[sy, sx]
            a[m] = np.minimum(a[m], ao)
            c.ao[sy, sx] = a

    def groove(self, m, depth=0.0025, shade=0.55, on=None):
        self.put(m, shade=shade, add_h=-depth, ao=0.7, on=on)


SEAM = 0.0085                   # a panel gap's painted width: one texel
BODY = (M["paint"],)


def near(a, b, w=SEAM):
    return np.abs(a - b) <= w / 2.0


def seg_dist(s, z, p0, p1):
    (a0, b0), (a1, b1) = p0, p1
    ds, dz = a1 - a0, b1 - b0
    t = np.clip(((s - a0) * ds + (z - b0) * dz) / (ds * ds + dz * dz), 0.0, 1.0)
    return np.hypot(s - (a0 + t * ds), z - (b0 + t * dz))


def belt_z(s):
    return np.interp(s, [a for a, _ in S.BELT], [b for _, b in S.BELT])


def rrect(u, v, u0, u1, v0, v1, r):
    """A rounded rectangle mask."""
    du = np.clip(np.maximum(u0 + r - u, u - (u1 - r)), 0, None)
    dv = np.clip(np.maximum(v0 + r - v, v - (v1 - r)), 0, None)
    return np.hypot(du, dv) <= r


# ---------------------------------------------------------------- LOD3 gaps
def lod3_gaps(c, T):
    """Texels no LOD0 or LOD1 face samples, painted for the flat LOD3 sides
    (and LOD2's): the side glass dark, the lamps as unlit colour, the
    wheels in their arches, the shadow under the sills."""
    for f in T[0]["body"]:
        if f.kind == "glass" and f.surface in (33, 34):
            for isl in ("side_l", "side_r"):
                polygon(c, [S.project(isl, (x if isl == "side_l" else -abs(x), y, z))
                            for x, y, z in ((abs(p[0]), p[1], p[2]) for p in f.pts)],
                        mid=M["glass_dark"])
        if f.kind == "lamp" and abs(f.normal()[0]) > 0.5:
            # neutral: coarser tiers' painted faces may sample these texels
            mid = M["paint"] if f.surface in (1, 2, 3, 4, 5, 11) else M["pic_white"]
            isl = "side_l" if f.centre()[0] > 0 else "side_r"
            polygon(c, dilated([S.project(isl, p) for p in f.pts], 0.6), mid=mid)


# ---------------------------------------------------------------- side
def paint_side(c):
    for isl, rect in (("side_l", S.R_SIDE_L), ("side_r", S.R_SIDE_R)):
        R = Region(c, rect)
        s = R.U if isl == "side_l" else S.L - R.U
        z = R.V
        bz = belt_z(s)
        # the black sill and lips up to the S1 row, so their thin faces find
        # black on both sides of their outline; under the sills, shadow
        z1 = np.array([S.z_side("S1", v) for v in s[0]])[None, :]
        R.put(z < z1 + 0.004, mid=M["lip"])
        R.put(z < 0.185, mid=M["under"])
        # the wheels in their arches, for LOD2/LOD3; liners round them
        for sa in S.S_AXLE:
            r = np.hypot(s - sa, z - (S.WHEEL_R + S.ARCH_DZ))
            rw = np.hypot(s - sa, z - S.WHEEL_R)
            # (only LOD2's painted sides sample these: a light rim in a thin
            # dark tyre, the arch gap left as paint, so they keep the paint's
            # brightness at the tier switch)
            hole = r < S.ARCH_R
            R.put(hole & (rw < S.WHEEL_R), mid=M["tyre"])
            R.put(hole & (rw < 0.26), mid=M["rim"])
            R.put(hole & (rw < 0.05), mid=M["rim_dark"])
            # the arch lip: a raised, slightly shaded rim on the body
            lip = (r >= S.ARCH_R) & (r < S.ARCH_R + 0.016)
            R.put(lip, shade=0.86, add_h=0.003, on=BODY)
            R.put((r >= S.ARCH_R + 0.016) & (r < S.ARCH_R + 0.022), shade=0.9, add_h=0.0015,
                  on=BODY)
        # door cut lines
        R.groove(near(s, 1.305) & (z > 0.30) & (z < bz - 0.004), on=BODY)
        R.groove(near(s, 2.44) & (z > 0.30) & (z < bz - 0.004), on=BODY)
        R.groove(near(s, 3.20) & (z > 0.585) & (z < bz - 0.004), on=BODY)
        ra = np.hypot(s - 3.51, z - 0.335)
        R.groove(near(ra, 0.40) & (s < 3.205) & (z > 0.335) & (z < 0.59), on=BODY)
        R.groove(near(s, 3.11) & (z > 0.30) & (z < 0.34), on=BODY)
        R.groove(near(z, 0.305) & (s > 1.305) & (s < 3.11), on=BODY)
        # bumper breaks
        R.groove(near(z, 0.645) & (s > 0.20) & (s < 0.58), on=BODY)
        R.groove(near(s, 0.58) & (z > 0.30) & (z < 0.645), on=BODY)
        R.groove(near(z, 0.63) & (s > 3.75) & (s < 4.45), on=BODY)
        R.groove(near(s, 3.86) & (z > 0.30) & (z < 0.63), on=BODY)
        # the wing's top edge to the A-pillar, and the tailgate's edge
        R.groove(near(s, 4.115) & (z > 0.995) & (z < bz - 0.004), on=BODY)
        # handles: a raised grip over a dark recess
        for s0, s1, zh in ((2.06, 2.20, 0.905), (3.02, 3.15, 0.945)):
            R.put(rrect(s, z, s0 - 0.01, s1 + 0.01, zh - 0.026, zh - 0.004, 0.01),
                  shade=0.45, add_h=-0.004, ao=0.6, on=BODY)
            R.put(rrect(s, z, s0, s1, zh - 0.012, zh + 0.018, 0.012), mid=M["handle"],
                  height=0.006)
        # side moulding along the doors
        R.put(rrect(s, z, 1.37, 3.08, 0.462, 0.500, 0.018), mid=M["lip"], height=0.006,
              on=BODY + (M["gap"],))
        # the belt moulding under the side glass
        # (the door's painted skin runs up to the glass; the waist seal is on
        # the shoulder, in the top island)
        # a soft character line along the flank, catching the light
        zc = bz - 0.085
        R.put((np.abs(z - zc) < 0.012) & (s > 0.45) & (s < 4.12),
              add_h=0.0, on=BODY)
        ridge = np.clip(1.0 - np.abs(z - zc) / 0.012, 0.0, 1.0)
        hh = c.height[R.sy, R.sx]
        mm = np.isin(R.mid(), BODY) & (s > 0.45) & (s < 4.12)
        hh[mm] += 0.003 * ridge[mm]
        c.height[R.sy, R.sx] = hh
        # window surround: black rubber above the glass and up the A-pillar
        zgt = np.interp(s, [a for a, _ in S.GLASS_TOP], [b for _, b in S.GLASS_TOP])
        R.put((z > zgt - 0.01) & (z < zgt + 0.018) & (s > S.A_GT_TOP - 0.02) & (s < 3.875),
              mid=M["seal"], on=BODY)
        R.put(seg_dist(s, z, (S.A_GT_BASE, 0.94), (S.A_GT_TOP, 1.345)) < 0.012, mid=M["seal"],
              on=BODY)
        R.put(seg_dist(s, z, (3.88, 1.075), (3.865, 1.335)) < 0.010, mid=M["seal"], on=BODY)
        # fuel flap on the right rear quarter
        if isl == "side_r":
            ff = rrect(s, z, 3.73, 3.89, 0.83, 0.94, 0.02)
            inner = rrect(s, z, 3.73 + SEAM, 3.89 - SEAM, 0.83 + SEAM, 0.94 - SEAM, 0.012)
            R.groove(ff & ~inner, on=BODY)


# ---------------------------------------------------------------- top
def cowl_s(x):
    return 1.27 + 0.045 * (np.asarray(x) / 0.70) ** 2


def paint_top(c):
    R = Region(c, S.R_TOP)
    s, x = R.U, R.V
    # bonnet shut lines along the wings, and its rear edge at the cowl
    # from the headlamps' inner top corners back along the wings
    shut = np.interp(s, [0.15, 0.45, 0.85, 1.20], [0.50, 0.625, 0.705, 0.745])
    R.groove(near(x, shut, 0.012) & (s > 0.15) & (s < cowl_s(0.745) - 0.046), depth=0.003,
             shade=0.5, on=BODY)
    sc = cowl_s(x)
    cowl = (s > sc - 0.046) & (s < sc + 0.01) & (x < 0.72)
    R.groove(near(s, sc - 0.046) & (x < 0.79), on=BODY)
    R.put(cowl, mid=M["lip"], on=BODY)
    R.put(cowl & (np.mod(x, 0.05) < 0.012) & (s > sc - 0.036) & (s < sc - 0.012), shade=0.6,
          add_h=-0.003)
    # wipers parked along the cowl: arm and blade
    R.put((seg_dist(s, x, (1.252, 0.05), (1.29, 0.64)) < 0.007) & (x < 0.66), mid=M["seal"],
          height=0.008)
    # belt moulding on the shoulder, the roof side's window surround
    # the waist seal at the glass foot: 18 mm of rubber on the painted shoulder
    R.put((x > 0.818) & (x < 0.836) & (s > 1.335) & (s < 3.89), mid=M["seal"], add_h=0.002,
          on=BODY)
    R.put((x > 0.668) & (x < 0.686) & (s > S.A_GT_TOP - 0.02) & (s < 3.875), mid=M["seal"],
          on=BODY)
    # the tailgate's hinge line across the roof end
    R.groove(near(s, 3.965) & (x < 0.60), on=BODY)
    # the roof's drip channel either side of the rails
    R.groove(near(x, 0.632, 0.008) & (s > 2.1) & (s < 3.9), depth=0.0015, shade=0.8, on=BODY)


# ---------------------------------------------------------------- front
def paint_front(c):
    R = Region(c, S.R_FRONT)
    x, z = R.U, R.V + 0.15
    R.put(z < 0.274, mid=M["lip"])                # the lip, and under it
    # grille: a dark grey frame, horizontal slats over darkness
    # (the frame reaches a texel past the grille's cells, so their edges
    # find dark frame, never paint)
    zs5 = 0.695 + 0.03 * (x / S.W_SIDE["S5"]) ** 2
    gfr = (x < 0.392) & (z > zs5 - 0.016) & (z < 0.83)
    R.put(gfr, mid=M["rim_dark"], height=0.002)
    gin = (x < 0.356) & (z > zs5 + 0.010) & (z < 0.795)
    R.put(gin, mid=M["grille"], height=-0.006)
    slat = gin & (np.mod(z - 0.704 - 0.008, 0.029) < 0.012)
    R.put(slat, mid=M["rim_dark"], height=0.004)
    # the lamp housings' dark edge on the body round them (the lamps' lower
    # edge rises toward the wing with the S4 row)
    zl = 0.655 + 0.03 * (x / S.W_SIDE["S4"]) ** 2
    R.put((x > 0.493) & (x < 0.505) & (z > zl - 0.008) & (z < 0.81), mid=M["seal"])
    R.put((x > 0.50) & (z > zl - 0.010) & (z < zl + 0.002), mid=M["seal"])
    # bumper: a break line under grille and lamps, a second, softer one
    # where the face turns under
    R.groove(near(z, zl - 0.03, 0.013) & (x < 0.80), depth=0.004, shade=0.45, on=BODY)
    R.groove(near(z, 0.425, 0.009) & (x > 0.56) & (x < 0.80), depth=0.002, shade=0.7, on=BODY)
    # the lower intake, 1.10 wide, its frame, mesh and the fog lamps' pods at
    # its outer ends
    ifr = (x < 0.555) & (z > 0.262) & (z < 0.405)
    R.put(ifr, mid=M["rim_dark"], height=0.004)
    iin = (x < 0.540) & (z > 0.278) & (z < 0.392)
    R.put(iin, mid=M["intake"], height=-0.006)
    mesh = iin & ((np.mod(x, 0.034) < 0.008) | (np.mod(z - 0.278, 0.034) < 0.008))
    R.put(mesh, mid=M["rim_dark"], height=-0.002)
    pod = rrect(x, z, 0.54, 0.735, 0.272, 0.398, 0.03)
    R.put(pod, mid=M["lip"], height=-0.003)
    # (the fog lamps themselves are faces of their own, R_FOGLAMP)


# ---------------------------------------------------------------- rear
def paint_rear(c):
    R = Region(c, S.R_REAR)
    x, z = R.U, R.V + 0.18
    R.put(z < 0.334, mid=M["lip"])
    # the tailgate's cut lines down beside the lamps and along the bumper
    R.groove(near(x, 0.622) & (z > 0.64) & (z < 1.06), on=BODY)
    R.groove(near(z, 0.642) & (x < 0.622), on=BODY)
    R.groove(near(z, 0.628) & (x > 0.622), on=BODY)
    # plate recess and the tailgate's handle trim above it
    R.put((x < 0.30) & (z > 0.782) & (z < 0.806), mid=M["chrome"], height=0.005)
    # the lamps' housing edge
    zs4, zs5 = 0.80, 0.985
    R.put((x > 0.624) & (x < 0.636) & (z > zs4 - 0.01) & (z < zs5 + 0.01), mid=M["seal"])
    R.put((x > 0.62) & (z > zs5) & (z < zs5 + 0.010), mid=M["seal"])
    R.put((x > 0.62) & (z > zs4 - 0.010) & (z < zs4), mid=M["seal"])
    # (the right-hand red reflector mirroring the fog lamp is its own face)
    # the bumper's lower diffuser line
    R.groove(near(z, 0.345) & (x < 0.8), on=BODY)


# ---------------------------------------------------------------- lenses
# The hand-in lamp pictures (pale lenses with soft reflector shading, the
# amber end cell, ribbed red clusters), painted at LENS_PPM so their edges
# are crisper; pixel sizes below are in body texels (F scales them).
F = S.LENS_PPM / 64.0
LENS_STYLE = {(7, "front"): "projector", (8, "front"): "reflector", (9, "front"): "strip",
              (4, "front"): "ribs", (1, "rear"): "bars", (3, "rear"): "guide",
              (4, "rear"): "ribs", (6, "rear"): "clear", (2, "rear"): "dots",
              (11, "rear"): "ribs", (4, "mirror"): "plain"}


def paint_lenses(c):
    for key, ref in S.lens_refs().items():
        x, y, w, h = ref["rect"]
        c.paint(x, x + w, y, y + h, mid=M_LENS[key[0]], shade=1.0, height=0.0)
        sy, sx, Y_, X_ = c.field(x, x + w, y, y + h)
        u, v = X_ - x, Y_ - y
        sh = np.ones(u.shape, np.float32)
        hh = np.zeros(u.shape, np.float32)
        style = LENS_STYLE.get(key, "plain")
        cx, cy = w / 2.0, h / 2.0
        if style == "projector":
            # a chrome bowl round a projector lens, the cut-off shield dark
            r = np.hypot(u - w * 0.62, v - cy)
            sh *= 1.15
            sh[r < h * 0.36] = 0.55
            sh[r < h * 0.26] = 1.25
            sh[(r < h * 0.26) & (v < cy - h * 0.06)] = 0.75
            hh[r < h * 0.36] = -0.006
        elif style == "reflector":
            r = np.hypot(u - cx, v - cy)
            sh *= 0.85 + 0.35 * np.clip(1 - r / (h * 0.5), 0, 1)
            sh[np.abs(r - h * 0.18) < 0.6 * F] *= 0.7
        elif style == "strip":
            sh[np.abs(v - cy) < max(1.0 * F, h * 0.18)] = 1.3
        elif style == "ribs":
            sh[np.mod(v, 2.0 * F) < 0.8 * F] *= 0.82
        elif style == "guide":
            # a lighter light guide across a ribbed red field
            sh[np.mod(v, 1.6 * F) < 0.6 * F] *= 0.85
            sh[np.abs(v - h * 0.62) < max(1.2 * F, h * 0.09)] *= 1.45
            sh[(np.abs(v - h * 0.62) < h * 0.2) & (u > w * 0.1) & (u < w * 0.9)] *= 1.1
        elif style == "bars":
            sh[np.mod(v, 1.6 * F) < 0.6 * F] *= 0.85
            sh[np.abs(v - h * 0.62) < max(1.2 * F, h * 0.09)] *= 1.45
        elif style == "dots":
            sh[(np.mod(u, 2.5 * F) < 1.2 * F) & (np.abs(v - cy) < 1.5 * F)] *= 1.3
        elif style == "clear":
            sh *= 1.1
            sh[np.mod(u, 2.0 * F) < 0.6 * F] *= 0.88
        # a thin dark outline, the first texel inside the faces' mapping
        # (they map to the rect inset 3 texels)
        e = 3.0 + S.LENS_PPM / 112.0
        edge = (u < e) | (u > w - e) | (v < e) | (v > h - e)
        sh[edge] *= 0.45
        hh[edge] = -0.003
        c.shade[sy, sx] = sh
        c.height[sy, sx] = hh
    # the front fog lamps, as at hand-in: a dark bezel round a pale lens
    x, y, w, h = S.R_FOGLAMP
    sy, sx, Y_, X_ = c.field(x, x + w, y, y + h)
    rr = np.hypot(X_ - x - w / 2.0, Y_ - y - h / 2.0) / (w / 2.0)
    mid = np.full(rr.shape, M["seal"], np.uint8)
    mid[rr < 0.72] = M["chrome"]
    sh = np.ones(rr.shape, np.float32)
    sh[rr < 0.32] = 0.82
    c.mid[sy, sx] = mid
    c.shade[sy, sx] = sh
    c.height[sy, sx] = np.where(rr < 0.72, 0.004, 0.002).astype(np.float32)


def paint_plate(c):
    x, y, w, h = S.R_PLATE
    # white round the plate's rect to a 32-texel block, so its coarse mips
    # stay white; the faces map to the rect inset a texel: the border is the
    # next texel
    c.paint(x - 16, x + w + 32, y - 16, y + h + 24, mid=M["plate"], height=0.0)
    c.paint(x, x + w, y, y + h, mid=M["plate_rim"], height=0.0)
    b = 1.0 + S.SC                                   # the inset texel and the border
    c.paint(x + b, x + w - b, y + b, y + h - b, mid=M["plate"], height=0.0)


# ---------------------------------------------------------------- wheels
def paint_wheels(c):
    """The wheel face, shared by all four wheels and every tier, at 147
    texels per metre: a dark sidewall, a dark gap at the bead, a bright rim
    lip, five silver spokes over near-black openings, a hub with its cap and
    nuts. Crisp edges; relief a few millimetres at the edges only."""
    x, y, w, h = S.R_WHEEL_FACE
    k = (w / 2.0 - 1.0) / S.WHEEL_R
    sy, sx, Y_, X_ = c.field(x, x + w, y, y + h)
    r = np.hypot(X_ - x - w / 2.0, Y_ - y - h / 2.0) / k
    a = np.arctan2(Y_ - y - h / 2.0, X_ - x - w / 2.0)
    mid = np.full(r.shape, M["tyre"], np.uint8)
    hgt = np.zeros(r.shape, np.float32)
    sh = np.ones(r.shape, np.float32)
    sh[r > 0.300] *= 0.9                             # the shoulder's roll
    hgt[np.abs(r - 0.268) < 0.004] = 0.001           # a sidewall rib, no lettering
    mid[(r > 0.226) & (r < 0.234)] = M["seal"]       # the gap at the bead
    lip = (r >= 0.212) & (r <= 0.226)
    mid[lip] = M["rim"]
    hgt[lip] = 0.003
    face = r < 0.212
    mid[face] = M["rim"]
    sh[(r > 0.200) & (r < 0.212)] *= 0.85            # the dish wall
    pitch = 2 * np.pi / 5
    dist = np.abs(np.mod(a + pitch / 2, pitch) - pitch / 2) * r
    window = (r < 0.192) & (r > 0.072) & (dist > 0.022 + 0.045 * (r - 0.072) / 0.12)
    mid[window] = M["disc"]
    hgt[window] = -0.004
    hub = r < 0.062
    mid[hub] = M["rim"]
    hgt[hub] = 0.003
    mid[r < 0.034] = M["rim_dark"]
    nut = (np.hypot(r * np.cos(a) - 0.046 * np.cos(np.round(a / pitch) * pitch),
                    r * np.sin(a) - 0.046 * np.sin(np.round(a / pitch) * pitch)) < 0.007)
    mid[nut & (r < 0.06)] = M["rim_dark"]
    c.mid[sy, sx] = mid
    c.height[sy, sx] = hgt
    c.shade[sy, sx] = sh
    # tread: crown and shoulders, circumferential grooves, shoulder sipes
    x, y, w, h = S.R_TREAD
    c.paint(x, x + w, y, y + h, mid=M["tread"], height=0.0, shade=1.0)
    sy, sx, Y_, X_ = c.field(x, x + w, y, y + h)
    v = (Y_ - y) / h
    m = np.zeros(v.shape, bool)
    for g in (0.36, 0.5, 0.64):
        m |= np.abs(v - g) < 0.03
    hh = np.zeros(v.shape, np.float32)
    ss = np.ones(v.shape, np.float32)
    hh[m] = -0.006
    ss[m] = 0.7
    sip = ((v < 0.28) | (v > 0.72)) & (np.mod(X_ - x, 3.0 * S.SC) < 0.9 * S.SC)
    hh[sip] = -0.004
    ss[sip] *= 0.8
    ss[(v < 0.15) | (v > 0.85)] *= 0.9
    ss[(v > 0.30) & (v < 0.70)] *= 1.12              # the crown worn lighter
    c.height[sy, sx] = hh
    c.shade[sy, sx] = ss
    x, y, w, h = S.R_WHEEL_INNER
    c.paint(x, x + w, y, y + h, mid=M["wheel_inner"])


# ================================================================ weather
def weather(c):
    import weathering
    clean = (M["glass"], M["glass_dark"], M["mirror_glass"], M["plate"]) + tuple(M_LENS.values())
    w = weathering.Weather(c, clean=clean,
                           steel=(M["paint"], M["rim"], M["handle"], M["chrome"], M["lip"],
                                  M["seal"], M["rim_dark"], M["intake"], M["grille"],
                                  M["plate_rim"], M["tyre"], M["tread"], M["liner"],
                                  M["under"], M["disc"]))
    w.grime(0.025)
    dirty = (M["paint"], M["lip"], M["seal"], M["handle"])
    for isl, rect in (("side_l", S.R_SIDE_L), ("side_r", S.R_SIDE_R)):
        x, y, wd, h = rect
        oy = y + 1.0
        # road film from the ground up, densest on the sills
        w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.16 * np.exp(
            -((Y_ - oy) / S.PPM - 0.22) .clip(0) / 0.20) * (0.6 + 0.4 * nz("blotch")), dirty)
        w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz: 0.14 * nz("speck") * np.exp(
            -((Y_ - oy) / S.PPM) / 0.35), dirty)
        # spray fanned behind each wheel
        for sa in S.S_AXLE:
            def fan(Y_, X_, nz, sa=sa, isl=isl):
                u = (X_ - x - 1.0) / S.PPM
                s = u if isl == "side_l" else S.L - u
                zz = (Y_ - oy) / S.PPM
                d = s - (sa + 0.30)
                return 0.12 * np.exp(-(d / 0.35) ** 2) * np.exp(-zz / 0.32) * (d > -0.3) \
                    * (0.5 + 0.5 * nz("blotch"))
            w.add("D", x, x + wd, y, y + h, fan, dirty)
    # front and rear: the bumpers' lower edge, the tailgate in the wake
    for rect, z0, amt, fall in ((S.R_FRONT, 0.15, 0.14, 0.18), (S.R_REAR, 0.18, 0.12, 0.40)):
        x, y, wd, h = rect
        w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz, z0=z0, amt=amt, fall=fall: amt * np.exp(
            -(((Y_ - y - 1.0) / S.PPM + z0) - 0.25).clip(0) / fall) * (0.6 + 0.4 * nz("blotch")),
            dirty)
    # the liners, under-body, tyres: road dirt
    for rect, amt in ((S.R_UNDER, 0.3), (S.R_TREAD, 0.22), (S.R_WHEEL_FACE, 0.14)):
        x, y, wd, h = rect
        w.add("D", x, x + wd, y, y + h, lambda Y_, X_, nz, amt=amt: amt * (0.5 + 0.5 * nz("blotch")))
    return w


# ================================================================ export
GLASS_BASE = (52, 56, 60)       # neutral dark, a touch cool: inside the band


def vehicle_glass(mask, rgb):
    """The panes neutral dark with a gentle falloff toward their foot and a
    little grain, per pane (glazing's components): a car's glass, without
    rooms()' lit far wall, which reads as a stain on a windscreen."""
    out = np.asarray(rgb, np.float32).copy()
    for y0, y1, x0, x1 in glazing.components(glazing._dilate(mask, 2)):
        sub = mask[y0:y1, x0:x1]
        if not sub.any():
            continue
        hgt = max(1, y1 - y0 - 1)
        t = (np.arange(y1 - y0, dtype=np.float32) / hgt)[:, None]
        rs = np.random.RandomState(glazing._seed((y0, y1, x0, x1)))
        lvl = rs.uniform(0.92, 1.06)
        tile = (np.asarray(GLASS_BASE, np.float32) * lvl
                * (0.86 + 0.22 * t)[..., None]
                * glazing._grain((y1 - y0, x1 - x0), rs, 0.03)[..., None])
        region = out[y0:y1, x0:x1]
        region[sub] = np.broadcast_to(tile, region.shape)[sub]
    return out


def export(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    c = paint()
    w = weather(c)
    c.pad()
    cav = atlas.cavity(c, radius_px=1.5 * S.SC, depth_m=0.006)
    lut = np.zeros((256, 3), np.float32)
    for mid, col in SRGB.items():
        lut[mid] = col
    cov = atlas.coverage(c, M["glass"])
    glass = cov >= 0.5
    rgb = atlas.albedo(c, lut, grime=0.25 * cav)
    rgb = vehicle_glass(glass, rgb)
    out = [atlas.save(rgb, os.path.join(out_dir, "%s_albedo_plain.png" % ASSET))]
    rough = 0.03 * atlas.noise(c, 31, 12.0 * S.SC)
    out.append(atlas.save(atlas.orm(c, ROUGH, rough, 0.5 * cav),
                          os.path.join(out_dir, "%s_orm.png" % ASSET)))
    out.append(atlas.save(atlas.normal_map(c, flat_ids=(M["glass"],)),
                          os.path.join(out_dir, "%s_normal.png" % ASSET)))
    # emission: every lens rect lit in its lamp's colour, the cabin dim on
    # the glass texels, black everywhere else (partly glass texels too)
    emit = np.zeros((ATLAS, ATLAS, 3), np.float32)
    for key, ref in S.lens_refs().items():
        x, y, wd, h = ref["rect"]
        emit[y:y + h, x:x + wd] = vi.LENS_LIT[vi.lamp_colour(key[0])]
    cabin = glazing.night_rooms(glass, np.where(glass[..., None], 255.0, 0.0)) * CABIN_LEVEL
    emit = np.where(glass[..., None], cabin, emit)
    out.append(atlas.save(emit, os.path.join(out_dir, "%s_emission.png" % ASSET)))
    out.append(vi.save_glass_texels(glass, os.path.join(HERE, vi.GLASS_TEXELS)))
    del w
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["export"]:
        for p in export(os.path.join(HERE, "export")):
            print(p)
    else:
        print(__doc__)
