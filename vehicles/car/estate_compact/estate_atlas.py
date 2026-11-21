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
M = dict(paint=1, lip=2, grille=3, intake=4, pillar=5, sail=35, under=6, liner=7, plate=8,
         plate_rim=9, glass=10, tread=11, tyre=12, rim=13, wheel_inner=14, mirror_glass=15,
         rail=16, seal=17, rim_dark=18, gap=19, handle=20, lens_body=21, chrome=22,
         glass_dark=23, pic_red=24, pic_amber=25, pic_white=26, disc=27, hl_chrome=28)
M_LENS = {lid: 40 + lid for lid in range(1, 16)}
SRGB = {M["paint"]: (228, 228, 228), M["lip"]: (40, 41, 42), M["grille"]: (24, 25, 26),
        M["intake"]: (30, 31, 32), M["pillar"]: (25, 26, 27), M["under"]: (20, 20, 21),
        M["liner"]: (38, 38, 39), M["plate"]: (238, 238, 234), M["plate_rim"]: (40, 42, 44),
        M["glass"]: glazing.BASE, M["tread"]: (40, 40, 40), M["tyre"]: (30, 30, 31),
        M["rim"]: (186, 188, 190), M["wheel_inner"]: (22, 22, 23),
        M["mirror_glass"]: (120, 124, 128), M["rail"]: (52, 53, 55), M["seal"]: (22, 22, 23),
        M["rim_dark"]: (60, 61, 63), M["gap"]: (120, 120, 120), M["handle"]: (205, 205, 205),
        M["lens_body"]: (110, 112, 114), M["chrome"]: (176, 178, 180),
        M["glass_dark"]: (44, 47, 50), M["sail"]: (24, 24, 25), M["pic_red"]: (110, 30, 28), M["pic_amber"]: (150, 90, 30),
        M["pic_white"]: (165, 167, 165), M["disc"]: (24, 24, 26),
        M["hl_chrome"]: (206, 208, 210)}
ROUGH = {M["paint"]: (0.32, 0.0), M["lip"]: (0.86, 0.0), M["grille"]: (0.55, 0.0),
         M["intake"]: (0.62, 0.0), M["pillar"]: (0.42, 0.0), M["under"]: (0.9, 0.0),
         M["liner"]: (0.92, 0.0), M["plate"]: (0.45, 0.0), M["plate_rim"]: (0.5, 0.0),
         M["glass"]: (glazing.ROUGHNESS, 0.0), M["tread"]: (0.9, 0.0), M["tyre"]: (0.88, 0.0),
         M["rim"]: (0.35, 0.85), M["wheel_inner"]: (0.85, 0.0), M["mirror_glass"]: (0.06, 0.9),
         M["rail"]: (0.5, 0.0), M["seal"]: (0.6, 0.0), M["rim_dark"]: (0.5, 0.0),
         M["gap"]: (0.5, 0.0), M["handle"]: (0.32, 0.0), M["lens_body"]: (0.2, 0.0),
         M["chrome"]: (0.25, 0.0), M["sail"]: (0.62, 0.0), M["glass_dark"]: (0.1, 0.0), M["pic_red"]: (0.2, 0.0),
         M["pic_amber"]: (0.2, 0.0), M["pic_white"]: (0.2, 0.0), M["disc"]: (0.9, 0.0),
         M["hl_chrome"]: (0.25, 0.55)}
LENS_UNLIT = {"red": (128, 28, 26), "amber": (196, 112, 30), "white": (172, 175, 174)}
for _lid in range(1, 16):
    SRGB[M_LENS[_lid]] = LENS_UNLIT[vi.lamp_colour(_lid)]
    ROUGH[M_LENS[_lid]] = (0.12, 0.0)          # glossy lenses: the ORM's alone
CABIN_LEVEL = 0.25
KIND_MID = {"paint": M["paint"], "lip": M["lip"], "grille": M["grille"],
            "intake": M["intake"], "pillar": M["pillar"], "sail": M["sail"],
            "under": M["under"], "liner": M["liner"], "reflector": M["pic_red"],
            "seal": M["seal"], "pod": M["lip"]}


# ================================================================ raster
def polygon(c, pts, mid=None, shade=None, ao=None, height=None, grow=0.0):
    """Fill a polygon given in atlas pixels (even-odd, per sample), grown
    by *grow* pixels all round its outline (a true offset: a thin sliver
    grows across its width too)."""
    pts = np.asarray(pts, float)
    x0, y0 = pts.min(axis=0) - 1 - grow
    x1, y1 = pts.max(axis=0) + 1 + grow

    def test(X, Y):
        inside = np.zeros(X.shape, bool)
        n = len(pts)
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            cond = (ay > Y) != (by > Y)
            with np.errstate(divide="ignore", invalid="ignore"):
                xc = ax + (Y - ay) * (bx - ax) / (by - ay)
            inside ^= cond & (X < xc)
            if grow > 0:
                dx, dy = bx - ax, by - ay
                ll = max(dx * dx + dy * dy, 1e-12)
                t = np.clip(((X - ax) * dx + (Y - ay) * dy) / ll, 0.0, 1.0)
                inside |= np.hypot(X - ax - t * dx, Y - ay - t * dy) <= grow
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
                polygon(c, f.uv, mid=KIND_MID[f.kind], grow=1.3)
    lod3_gaps(c, T)
    # glass: the union of every tier's panes, a pixel wide
    for lv in order:
        for f in T[lv]["body"]:
            if f.kind == "glass":
                polygon(c, f.uv, mid=M["glass"], grow=1.2)
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
                       ("pic_red", S.R_REFLECTOR), ("sail", S.R_SAIL)):
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

    def groove(self, m, depth=0.004, shade=0.10, on=None, lip=None):
        """A panel gap: dark (sRGB about 70 on the field), grooved, and
        optionally a slightly raised lip on one side that catches light."""
        self.put(m, shade=shade, add_h=-depth, ao=0.7, on=on)
        if lip is not None:
            self.put(lip & ~m, add_h=0.0015, on=on)


SEAM = 0.0135                   # a panel gap's painted width: 1.7 texels, to read at 30 m
ARCH_TRIM = 0.008               # the dark trim edge round each wheel arch
DOOR_FOOT = S.Z_MID["S1"] + 0.012   # the doors' lower edge, over the sill cover
STRIP_Z = (0.462, 0.500)        # the side mouldings and the bumpers' rub strips
STRIP_FRONT_S, STRIP_REAR_S = 0.47, 3.90      # where the strips end short of the arches
STRIP_X = 0.50                  # and where they start on the bumpers' faces
# the front bumper cover's joint on the wing: s from under the headlamp's
# tip to the arch's edge, and its height
_JZ = S.cap_ze("front", "S5") - 0.020
BUMPER_JOINT = (S.cap_d("front", "S5") - 0.01,
                S.S_AXLE[0] - math.sqrt(S.ARCH_R ** 2 - (_JZ - S.WHEEL_R - S.ARCH_DZ) ** 2), _JZ)
BODY = (M["paint"],)
BONNET_GAP = 0.006              # the bonnet's shut lines: a deeper groove, to catch the light


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
            # the arch lip: a slim dark trim edge round the opening (it also
            # rounds the cut's facets), then the body's raised, rolled lip
            R.put((r >= S.ARCH_R) & (r < S.ARCH_R + ARCH_TRIM), mid=M["lip"], height=0.002,
                  on=BODY)
            R.put((r >= S.ARCH_R + ARCH_TRIM) & (r < S.ARCH_R + 0.026), shade=0.93, add_h=0.004,
                  on=BODY)
            R.put((r >= S.ARCH_R + 0.026) & (r < S.ARCH_R + 0.034), shade=0.96, add_h=0.002,
                  on=BODY)
        # door cut lines
        R.groove(near(s, 1.305) & (z > DOOR_FOOT) & (z < bz - 0.004), on=BODY)
        R.groove(near(s, 2.44) & (z > DOOR_FOOT) & (z < bz - 0.004), on=BODY)
        R.groove(near(s, 3.20) & (z > 0.585) & (z < bz - 0.004), on=BODY)
        ra = np.hypot(s - 3.51, z - 0.335)
        R.groove(near(ra, 0.40) & (s < 3.205) & (z > DOOR_FOOT + 0.035) & (z < 0.59), on=BODY)
        R.groove(near(s, 3.11) & (z > DOOR_FOOT) & (z < DOOR_FOOT + 0.04), on=BODY)
        R.groove(near(z, DOOR_FOOT) & (s > 1.305) & (s < 3.11), on=BODY)
        # bumper breaks: the front cover's joint, level from under the lamp's
        # swept tip back to the arch (along the texel rows, so it stays crisp)
        R.groove(near(z, BUMPER_JOINT[2]) & (s > BUMPER_JOINT[0]) & (s < BUMPER_JOINT[1]), on=BODY)
        R.groove(near(z, 0.63) & (s > 3.70) & (s < 4.45), on=BODY)
        # the wing's top edge to the A-pillar, and the tailgate's edge
        R.groove(near(s, 4.115) & (z > 0.995) & (z < bz - 0.004), on=BODY)
        # handles: each a grip across a scallop dished into the door, just
        # under the shoulder crease
        zcr = np.array([S.z_side("S5", v) for v in s[0]])[None, :]
        for s0, s1 in ((2.040, 2.220), (3.000, 3.170)):
            sm, hs, hz = (s0 + s1) / 2.0, (s1 - s0) / 2.0, 0.038
            zc = zcr - 0.100
            rr = ((s - sm) / hs) ** 2 + ((z - zc) / hz) ** 2
            dish = rr < 1.0
            hh = c.height[R.sy, R.sx]
            mm = dish & np.isin(R.mid(), BODY)
            hh[mm] -= (0.012 * (1.0 - rr))[mm]
            c.height[R.sy, R.sx] = hh
            R.put(dish, shade=1.0, ao=0.65, on=BODY)
            sha = c.shade[R.sy, R.sx]
            sha[mm] *= np.clip(0.72 + 0.30 * (zc + hz - z) / (2 * hz), 0.70, 1.0)[mm]
            c.shade[R.sy, R.sx] = sha
            R.put(rrect(s, z, sm - hs * 0.84, sm + hs * 0.84, zc + 0.000, zc + 0.020, 0.010),
                  mid=M["handle"], height=0.008)
        # the doors' lower break, pressed a little deeper than the mesh has
        # it: below the line the skin sits 4 mm in, over a 3 cm turn; it
        # fades out at the doors' ends, short of the arches
        zb = np.array([S.z_side("S3", v) for v in s[0]])[None, :]
        fade = np.clip((s - 1.32) / 0.10, 0, 1) * np.clip((3.08 - s) / 0.10, 0, 1)
        turn = np.clip((zb + 0.015 - z) / 0.030, 0, 1)
        hh = c.height[R.sy, R.sx]
        mm = np.isin(R.mid(), BODY) & (z > DOOR_FOOT + 0.01)
        hh[mm] -= (0.004 * fade * turn * turn * (3 - 2 * turn))[mm]
        c.height[R.sy, R.sx] = hh
        # the doors' frames: the shut line to the roof above the window seal,
        # and the door gaps carried up the B- and C-pillars' black-outs
        zgt0 = np.interp(s, [a for a, _ in S.GLASS_TOP], [b for _, b in S.GLASS_TOP])
        R.groove(near(z, zgt0 + 0.034, 0.010) & (s > S.A_GT_TOP + 0.04) & (s < 3.215), depth=0.003,
                 on=BODY)
        for sg in (2.44, 3.205):
            R.put(near(s, sg, 0.009) & (z > bz) & (z < zgt0 + 0.034), mid=M["rim_dark"],
                  on=(M["pillar"],))
        # side moulding along the doors, and the bumpers' rub strips at its
        # height: one dark line round the car, broken by the arches
        R.put(rrect(s, z, 1.37, 3.08, STRIP_Z[0], STRIP_Z[1], 0.018), mid=M["lip"], height=0.006,
              on=BODY + (M["gap"],))
        R.put(rrect(s, z, -1.0, STRIP_FRONT_S, STRIP_Z[0], STRIP_Z[1], 0.015), mid=M["lip"],
              height=0.005, on=BODY)
        R.put(rrect(s, z, STRIP_REAR_S, 6.0, STRIP_Z[0], STRIP_Z[1], 0.015), mid=M["lip"],
              height=0.005, on=BODY)
        # the belt moulding under the side glass
        # (the door's painted skin runs up to the glass; the waist seal is on
        # the shoulder, in the top island)
        # (the flank's character line is the mesh's own crease, row S5)
        # window surround: black rubber above the glass and up the A-pillar
        zgt = np.interp(s, [a for a, _ in S.GLASS_TOP], [b for _, b in S.GLASS_TOP])
        R.put((z > zgt - 0.01) & (z < zgt + 0.018) & (s > S.A_GT_TOP - 0.02) & (s < 3.875),
              mid=M["seal"], on=BODY)
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
    # bonnet shut lines. The bonnet spans nearly the car's width: its front
    # edge runs just behind the leading edge, over the grille and along the
    # lamps' tops to the middle of the low beam; from there each side line
    # runs back along the wing's top, nearly parallel to the car's length,
    # and curves in to the windscreen's base corner just inboard of the
    # A-pillar's foot, where it meets the bonnet's rear edge. Only a narrow
    # strip of wing shows outboard of it.
    x_f = 0.705
    s_f = S.cap_s("front", "SH", x_f) + 0.012
    x_r, s_r = 0.705, float(cowl_s(0.705)) - 0.046
    # (about 0.09-0.10 inboard of the wing's crest along the bonnet, curving
    # in over the last 0.15 to the windscreen's corner)
    ks, kx = [s_f, 0.90, 1.10, 1.20, s_r], [x_f, 0.722, 0.730, 0.723, x_r]
    shut = np.array([S.pchip(ks, kx, v) for v in s[0]])[None, :]
    run = (s > s_f - SEAM / 2) & (s < s_r + SEAM / 2)
    R.groove(near(x, shut) & run, depth=BONNET_GAP, on=BODY,
             lip=(x - shut > SEAM / 2) & (x - shut < SEAM / 2 + 0.006) & run)
    xs = np.linspace(0.0, x_f, 32)
    edge = np.interp(x, xs, [S.cap_s("front", "SH", v) for v in xs]) + 0.012
    R.groove(near(s, edge) & (x < x_f + SEAM / 2), depth=BONNET_GAP, on=BODY,
             lip=(s - edge > SEAM / 2) & (s - edge < SEAM / 2 + 0.006) & (x < x_f))
    sc = cowl_s(x)
    cowl = (s > sc - 0.046) & (s < sc + 0.01) & (x < 0.69)
    R.groove(near(s, sc - 0.046) & (x < 0.71), depth=BONNET_GAP, on=BODY)
    R.put(cowl, mid=M["lip"], on=BODY)
    R.put(cowl & (np.mod(x, 0.05) < 0.012) & (s > sc - 0.036) & (s < sc - 0.012), shade=0.6,
          add_h=-0.003)
    # wipers parked along the cowl: arm and blade
    R.put((seg_dist(s, x, (1.252, 0.05), (1.29, 0.64)) < 0.007) & (x < 0.66), mid=M["seal"],
          height=0.008)
    # belt moulding on the shoulder, the roof side's window surround
    # the waist seal at the glass foot: 18 mm of rubber on the painted shoulder
    ss_ = np.linspace(1.30, 3.92, 80)
    gx = np.interp(s, ss_, [S.gb_x(v) for v in ss_])
    R.put((x > gx - 0.010) & (x < gx + 0.008) & (s > 1.335) & (s < 3.89), mid=M["seal"],
          add_h=0.002, on=BODY)
    R.put((x > 0.668) & (x < 0.686) & (s > S.A_GT_TOP - 0.02) & (s < 3.875), mid=M["seal"],
          on=BODY)
    # the tailgate's hinge line across the roof end
    R.groove(near(s, 3.965) & (x < 0.60), on=BODY)
    # the roof's drip channel either side of the rails
    R.groove(near(x, 0.632, 0.008) & (s > 2.1) & (s < 3.9), depth=0.0015, shade=0.8, on=BODY)


# ---------------------------------------------------------------- front
def _eroded(m, px):
    """A sample mask shrunk by px atlas pixels at its top and its foot only:
    a frame's rails. The slanted sides stay the mesh's own edges, crisp at
    any distance."""
    from scipy import ndimage
    n = max(1, int(round(px * atlas.SS)))
    return ndimage.binary_erosion(m, structure=np.ones((3, 1), bool), iterations=n)


def paint_front(c):
    R = Region(c, S.R_FRONT)
    x, z = R.U, R.V + 0.15
    R.put(z < 0.274, mid=M["lip"])                # the lip, and under it
    # the grille, whatever its cells' outline: a dark grey frame, horizontal
    # slats over darkness (the cells were rastered a texel past their
    # outline, so the frame's edge finds frame, never paint)
    g = R.mid() == M["grille"]
    gin = _eroded(g, 2.6)
    R.put(g, mid=M["rim_dark"], height=0.002)
    R.put(gin, mid=M["grille"], height=-0.006)
    R.put(gin & (np.mod(z - 0.634, 0.028) < 0.011), mid=M["rim_dark"], height=0.004)
    # the lower intake: its frame and mesh
    g = R.mid() == M["intake"]
    iin = _eroded(g, 2.2)
    R.put(g, mid=M["rim_dark"], height=0.004)
    R.put(iin, mid=M["intake"], height=-0.006)
    mesh = iin & ((np.mod(x, 0.034) < 0.008) | (np.mod(z - 0.2865, 0.034) < 0.008))
    R.put(mesh, mid=M["rim_dark"], height=-0.002)
    # (the fog lamps' pods beside it are faces of their own kind, and the
    # lamps faces on their own patch, R_FOGLAMP)
    # the plate's holder: a black plinth a little larger than the plate
    # (the plate's own faces map to their rect; the light patch inside the
    # holder is what LOD2's bumper face shows there)
    pz0, pz1 = S.PLATE_Z["front"]
    R.put(rrect(x, z, -1.0, S.PLATE_W / 2 + 0.020, pz0 - 0.012, pz1 + 0.012, 0.012),
          mid=M["lip"], height=0.004, on=BODY)
    R.put(rrect(x, z, -1.0, S.PLATE_W / 2, pz0, pz1, 0.004), mid=M["paint"], height=0.006)
    # the lip's upper edge: a lighter chamfer, the break between bumper and splitter
    R.put((z > 0.256) & (z < 0.274), mid=M["rim_dark"], height=0.004, on=(M["lip"],))
    # the bumper's rub strips on its corners, at the side mouldings' height
    R.put(rrect(x, z, STRIP_X, 2.0, STRIP_Z[0], STRIP_Z[1], 0.015), mid=M["lip"], height=0.005,
          on=BODY)


# ---------------------------------------------------------------- rear
def paint_rear(c):
    R = Region(c, S.R_REAR)
    x, z = R.U, R.V + 0.18
    R.put(z < 0.334, mid=M["lip"])
    xs = np.linspace(0.0, 0.89, 40)
    zs4 = np.interp(x, xs, [S.cap_z("rear", "S4", v) for v in xs])
    zs5 = np.interp(x, xs, [S.cap_z("rear", "S5", v) for v in xs])
    re4, re5, reh = (S.cap_x("rear", r, "RE") for r in ("S4", "S5", "SH"))
    z4, z5 = S.CAP["rear"]["rows"]["S4"][0], S.CAP["rear"]["rows"]["S5"][0]
    zh = S.CAP["rear"]["rows"]["SH"][0]
    # the tailgate's cut lines: along the bumper, up beside the clusters'
    # inner edges (the clusters sit on the quarters) and on to the glass's
    # lower corners; the bumper's joint to the quarter outboard of it
    R.groove(near(x, re4) & (z > 0.64) & (z < z4 - 0.004), on=BODY)
    R.groove(seg_dist(x, z, (re5, z5 + 0.012), (reh, zh + 0.004)) < SEAM / 2.0, on=BODY)
    R.groove(near(z, 0.642) & (x < re4), on=BODY)
    R.groove(near(z, 0.628) & (x > re4), on=BODY)
    # the handle: a dark recess under a raised garnish, above the plate
    R.put(rrect(x, z, -1.0, 0.24, 0.790, 0.812, 0.008), mid=M["lip"], height=-0.006, ao=0.6,
          on=BODY)
    R.put(rrect(x, z, -1.0, 0.30, 0.812, 0.838, 0.008), mid=M["handle"], height=0.006, on=BODY)
    # the plate's holder
    pz0, pz1 = S.PLATE_Z["rear"]
    R.put(rrect(x, z, -1.0, S.PLATE_W / 2 + 0.020, pz0 - 0.012, pz1 + 0.012, 0.012),
          mid=M["lip"], height=0.004, on=BODY)
    R.put(rrect(x, z, -1.0, S.PLATE_W / 2, pz0, pz1, 0.004), mid=M["paint"], height=0.006)
    # the clusters' housing edge on the body: inner edge, top and foot
    R.put(seg_dist(x, z, (re4, z4), (re5, z5)) < 0.006, mid=M["seal"], on=BODY)
    R.put((x > re5 - 0.004) & (z > zs5) & (z < zs5 + 0.010), mid=M["seal"], on=BODY)
    R.put((x > re4 - 0.004) & (z > zs4 - 0.010) & (z < zs4), mid=M["seal"], on=BODY)
    # (the right-hand red reflector mirroring the fog lamp is its own face)
    # the bumper's rub strips on its corners, and its lower diffuser line
    R.put(rrect(x, z, 0.60, 2.0, STRIP_Z[0], STRIP_Z[1], 0.015), mid=M["lip"], height=0.005,
          on=BODY)
    R.groove(near(z, 0.345) & (x < 0.8), on=BODY)


# ---------------------------------------------------------------- lenses
# The hand-in lamp pictures (pale lenses with soft reflector shading, the
# amber end cell, ribbed red clusters), painted at LENS_PPM so their edges
# are crisper; pixel sizes below are in body texels (F scales them).
F = S.LENS_PPM / 64.0
LENS_STYLE = {(7, "front"): "projector", (8, "front"): "reflector", (9, "front"): "strip",
              (4, "front"): "indicator", (1, "rear"): "bars", (3, "rear"): "guide",
              (4, "rear"): "ribs", (6, "rear"): "clear", (2, "rear"): "dots",
              (11, "rear"): "ribs", (4, "mirror"): "plain"}


UNITS = {"front": (4, 7, 8, 9), "rear": (1, 3, 4, 6)}     # ids of one lamp unit (5 maps as 4)


def unit_faces(end):
    """The left unit's LOD0 faces at one end: cap cells and the tip on the side."""
    return [f for f in S.tier(0)["body"]
            if f.kind == "lamp" and f.centre()[0] > 0 and S.lens_key(f)[1] == end
            and S.lens_key(f)[0] in UNITS[end]]


def unit_edges(faces):
    """(outline, joints): the edges of *faces* no other of them shares,
    whole or in part (a cell cut in two meets its neighbour's uncut edge),
    and the edges where two of them with different lamp ids meet; each as
    (face, corner index) pairs."""
    outline, joints = [], []
    segs = [(g, np.array(g.pts[k]), np.array(g.pts[(k + 1) % len(g.pts)]))
            for g in faces for k in range(len(g.pts))]
    for f in faces:
        n = len(f.pts)
        for k in range(n):
            m = (np.array(f.pts[k]) + np.array(f.pts[(k + 1) % n])) / 2.0
            other = None
            for g, a, b in segs:
                if g is f:
                    continue
                d = b - a
                t = min(max(float((m - a) @ d) / max(float(d @ d), 1e-12), 0.0), 1.0)
                if np.linalg.norm(m - a - t * d) < 2e-4:
                    other = g
                    break
            if other is None:
                outline.append((f, k))
            elif S.lens_key(other) != S.lens_key(f):
                joints.append((f, k))
    return outline, joints


def paint_lenses(c):
    units = {end: unit_faces(end) for end in UNITS}
    cent = {}
    for faces in units.values():
        for f in faces:
            q = np.array(S.lens_uv(f))
            px = 0.5 * abs(sum(q[k][0] * q[(k + 1) % len(q)][1]
                               - q[(k + 1) % len(q)][0] * q[k][1] for k in range(len(q))))
            cent.setdefault(S.lens_key(f), []).append((px, q.mean(axis=0)))
    for key, ref in S.lens_refs().items():
        x, y, w, h = ref["rect"]
        c.paint(x, x + w, y, y + h, mid=M_LENS[key[0]], shade=1.0, height=0.0)
        sy, sx, Y_, X_ = c.field(x, x + w, y, y + h)
        u, v = X_ - x, Y_ - y
        sh = np.ones(u.shape, np.float32)
        hh = np.zeros(u.shape, np.float32)
        style = LENS_STYLE.get(key, "plain")
        cx, cy = w / 2.0, h / 2.0
        tall = h - 6.0
        if key in cent:
            # a unit's cell is no rectangle: its picture sits on the cell's
            # own centre of area and is sized from its mean height
            ar = np.array([a for a, _ in cent[key]])
            pc = np.array([p for _, p in cent[key]])
            cx, cy = (pc * ar[:, None]).sum(axis=0) / ar.sum() - (x, y)
            tall = ar.sum() / (w - 6.0)
        md = np.full(u.shape, M_LENS[key[0]], np.uint8)
        if style in ("projector", "reflector"):
            # the headlamp's inside behind a clear lens: a bright metallic
            # housing, darker under its roof; no glints (the lens's gloss is
            # the ORM's) and no ring round a dot
            md[:] = M["hl_chrome"]
            sh *= 0.94
            sh *= 0.80 + 0.20 * np.clip((h - v) / (h * 0.32), 0, 1)
        if style == "reflector":
            # the high beam: a fluted reflector bowl, wider than tall, the
            # flutes upright, lighter toward its foot; a small bulb shield
            bw, bh = 0.86 * tall, 0.37 * tall
            bowl = rrect(u, v, cx - bw, cx + bw, cy - bh, cy + bh, 0.8 * bh)
            edge = rrect(u, v, cx - bw - 1.1, cx + bw + 1.1, cy - bh - 1.1, cy + bh + 1.1,
                         0.8 * bh + 1.1) & ~bowl
            t = np.clip((v - (cy - bh)) / (2 * bh), 0, 1)
            flute = np.where(np.mod(u - cx, 3.4) < 1.7, 1.07, 0.93)
            sh[bowl] = ((1.10 - 0.20 * t) * flute)[bowl]
            sh[edge] = 0.70
            hh[bowl] = (-0.005 * (1 - ((v - cy) / bh) ** 2).clip(0, 1))[bowl]
            shield = rrect(u, v, cx - 3.0, cx + 3.0, cy - 1.5, cy + 1.5, 1.5)
            sh[shield] = 0.66
        elif style == "projector":
            # the low beam: a projector's glass lens in a square shroud, the
            # lens glossy and darker, its lower half shaded by the cut-off
            hs = 0.42 * tall
            shroud = rrect(u, v, cx - hs, cx + hs, cy - hs, cy + hs, 0.35 * hs)
            edge = rrect(u, v, cx - hs - 1.1, cx + hs + 1.1, cy - hs - 1.1, cy + hs + 1.1,
                         0.35 * hs + 1.1) & ~shroud
            sh[shroud] = 1.10
            sh[edge] = 0.70
            r = np.hypot(u - cx, v - cy)
            lens = r < 0.72 * hs
            md[lens] = M_LENS[key[0]]
            sh[lens] = np.where(v < cy - 0.1 * hs, 0.60, 0.74)[lens]
            hh[lens] = (0.004 * (1 - (r / (0.72 * hs)) ** 2))[lens]
        elif style == "strip":
            sh *= 0.96
        elif style == "ribs":
            sh[np.mod(v, 2.0 * F) < 0.8 * F] *= 0.78
        elif style == "guide":
            # a lighter light guide across a ribbed red field
            sh[np.mod(v, 1.6 * F) < 0.6 * F] *= 0.80
            sh[np.abs(v - cy) < max(1.2 * F, tall * 0.10)] *= 1.50
        elif style == "bars":
            sh[np.mod(v, 1.6 * F) < 0.6 * F] *= 0.80
            sh[np.abs(v - cy) < max(1.2 * F, tall * 0.10)] *= 1.50
        elif style == "indicator":
            # a ribbed amber cell behind the clear lens, out to the end
            sh[np.mod(u, 1.8 * F) < 0.7 * F] *= 0.84
        elif style == "dots":
            sh[(np.mod(u, 2.5 * F) < 1.2 * F) & (np.abs(v - cy) < 1.5 * F)] *= 1.3
        elif style == "clear":
            sh *= 1.12
            sh[np.mod(u, 2.0 * F) < 0.6 * F] *= 0.84
        if key not in cent:
            # a thin dark outline, the first texel inside the faces' mapping
            # (they map to the rect inset 3 texels)
            e = 3.0 + S.LENS_PPM / 112.0
            edge = (u < e) | (u > w - e) | (v < e) | (v > h - e)
            sh[edge] *= 0.45
            hh[edge] = -0.003
        c.mid[sy, sx] = md
        c.shade[sy, sx] = sh
        c.height[sy, sx] = hh
    # the daytime strip: a slim, lighter light guide along the middle of
    # each of its cells (they follow the lamp's foot)
    for f in units["front"]:
        if f.surface != 9:
            continue
        q = np.array(S.lens_uv(f))
        a, b = (q[0] + q[3]) / 2.0, (q[1] + q[2]) / 2.0
        wd = 0.42 * np.linalg.norm(q[3] - q[0])
        d = (b - a) / np.linalg.norm(b - a)
        c.stroke(tuple(a - d * 2.0), tuple(b + d * 2.0), wd, shade=1.16)
    # each unit's joints (a fine dark line where two of its cells meet) and
    # its outline, drawn just inside its own edge, whatever its shape: the
    # dark line where the lens meets the body
    ow = 2.0 * S.LENS_PPM / 112.0
    for faces in units.values():
        outline, joints = unit_edges(faces)
        for f, k in joints:
            q = S.lens_uv(f)
            c.stroke(q[k], q[(k + 1) % len(q)], 0.6 * ow, shade=0.62)
        for f, k in outline:
            q = S.lens_uv(f)
            c.stroke(q[k], q[(k + 1) % len(q)], ow, shade=0.45, height=-0.003)
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
    hgt[window] = -0.012
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
    clean = (M["glass"], M["glass_dark"], M["mirror_glass"], M["plate"],
             M["hl_chrome"]) + tuple(M_LENS.values())
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


FRIT = 0.42               # the printed band's albedo, as a share of the glass's
FRIT_PX = {32: (4.0, 8.0), 35: (5.5, 12.0)}    # glass id -> band width, inner corner radius (texels)


def frit():
    """The printed black band round the windscreen and the tailgate glass,
    with rounded inner corners: its coverage per texel, in the atlas's own
    rows (V up). It is still glass (same ids, texels and gloss), only
    darker."""
    from PIL import Image, ImageDraw
    from scipy import ndimage
    k = atlas.SS                       # drawn at the canvas's sample density, then box-filtered
    n = ATLAS * k
    out = np.zeros((n, n), bool)
    for gid, (wd, rad) in FRIT_PX.items():
        m = Image.new("L", (n, n), 0)
        d = ImageDraw.Draw(m)
        for f in S.tier(0)["body"]:
            if f.kind == "glass" and f.surface == gid:
                d.polygon([(a * k, b * k) for a, b in f.uv], fill=1, outline=1)
        pane = np.asarray(m, bool)
        inner = ndimage.distance_transform_edt(pane) > wd * k
        core = ndimage.distance_transform_edt(inner) > rad * k
        opened = ndimage.distance_transform_edt(~core) <= rad * k
        out |= pane & ~(opened & inner)
        if gid == 35:
            # the rear wiper's arm and pivot, as dark as the band: from the
            # glass's foot on the centre line up to the blade (a solid of its own)
            st = dict(S.key_stations())
            a = np.array((0.0, st["R0"]["RC"][1], st["R0"]["RC"][2]))
            b = np.array((0.0, st["RG"]["RC"][1], st["RG"]["RC"][2]))
            piv = a + (b - a) * 0.035
            tip = a + (b - a) * 0.13 + np.array((0.17, 0.0, 0.0))
            pa = np.array(S.project("glass_tg", S.P(*piv))) * k
            pb = np.array(S.project("glass_tg", S.P(*tip))) * k
            arm = Image.new("L", (n, n), 0)
            da = ImageDraw.Draw(arm)
            da.line([tuple(pa), tuple(pb)], fill=1, width=int(round(2.4 * k)))
            r_ = 3.2 * k
            da.ellipse([pa[0] - r_, pa[1] - r_, pa[0] + r_, pa[1] + r_], fill=1)
            out |= pane & np.asarray(arm, bool)
    return atlas.box(out.astype(np.float32), k)


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
    fr = (frit() * glass)[..., None]
    rgb = rgb * (1.0 - fr * (1.0 - FRIT))
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
