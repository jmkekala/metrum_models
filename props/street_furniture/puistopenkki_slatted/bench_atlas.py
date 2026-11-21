# SPDX-License-Identifier: GPL-3.0-or-later

"""puistopenkki_slatted: the bench's dimensions, atlas layout and textures.

The numbers build.py builds from and the pixels the atlas paints them into
live here together, so a change to one is made beside the other. Importing
needs numpy alone (Blender's Python reads the layout); painting needs scipy
and Pillow, imported where used. Write the textures, from the repository
root, before the Blender build reads them:

    python3 props/street_furniture/puistopenkki_slatted/bench_atlas.py export

Build frame: metres, Z up, the seat's front (the side you sit on) toward
-Y, the origin on the ground at the centre of the four feet. Blender
(x, y, z) is glTF (x, z, -y).

The bench: two cast end frames, each one flat casting (front leg, seat
rail, rear leg and back stay in one profile), carrying four seat slats and
three back slats. Every slat is its own closed box with real gaps between,
so the frames and the ground show through them.
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "scripts"))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import atlas  # noqa: E402
import weathering  # noqa: E402

ASSET = "puistopenkki_slatted"
ATLAS = 256
PPM = 64.0

# ================================================================ geometry
LENGTH = 1.80                 # slats, end to end
HL = LENGTH / 2.0
FRAME_X = 0.70                # end frames' centre planes, x = +-0.70
FRAME_T = 0.045               # casting thickness
FX0, FX1 = FRAME_X - FRAME_T / 2.0, FRAME_X + FRAME_T / 2.0

Z_RAIL = 0.41                 # the seat rail's top; slats sit on it
Z_RAIL_BOT = 0.355
SLAT_T = 0.04                 # seat slats, 0.095 x 0.04
Z_SEAT = Z_RAIL + SLAT_T      # 0.45, the seat's top
SEAT_W, SEAT_GAP, SEAT_N = 0.095, 0.02, 4
BACK_W, BACK_GAP, BACK_N = 0.085, 0.0275, 3
BACK_T = 0.025
BACK_S0 = 0.11                # the lowest back slat's foot, along the stay
STAY_TOP = 0.425              # the stay's top, along it
STAY_W = 0.045                # the stay's width across it
TILT = math.radians(14.0)     # the back's lean from vertical

# The profile is drawn with the seat's front at y' = 0, then moved back by
# Y_SHIFT so that the origin is the centre of the feet (the pivot).
_U = (math.sin(TILT), math.cos(TILT))         # up the stay, (y, z)
_NF = (-math.cos(TILT), math.sin(TILT))       # out of the stay's front face
_RB = (math.cos(TILT), -math.sin(TILT))       # out of its back face
_J = (0.45, Z_RAIL)                           # stay front at the rail's top


def _add(p, d, k):
    return (p[0] + d[0] * k, p[1] + d[1] * k)


def _profile0():
    """LOD0's end-frame outline, (y', z), counter-clockwise seen from +X."""
    A, B = (0.0, 0.0), (0.055, 0.0)               # front foot
    C = (0.06, Z_RAIL_BOT)                        # front leg's inner top
    splay = 0.2                                   # rear leg: dy per dz
    E, F = (0.525, 0.0), (0.58, 0.0)              # rear foot
    D = (E[0] - splay * Z_RAIL_BOT, Z_RAIL_BOT)   # rear leg's inner top
    I = _add(_J, _U, STAY_TOP)                    # stay top, front
    H = _add(I, _RB, STAY_W)                      # stay top, back
    # G: the rear leg's outer edge meets the stay's back edge
    t = math.tan(TILT)
    z = (F[0] - H[0] + H[1] * t) / (splay + t)
    G = (F[0] - splay * z, z)
    K = (0.005, Z_RAIL)                           # the rail's front top
    return {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G,
            "H": H, "I": I, "J": _J, "K": K}


_P0 = _profile0()
ORDER0 = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K")
Y_SHIFT = (_P0["A"][0] + _P0["B"][0] + _P0["E"][0] + _P0["F"][0]) / 4.0


def _mv(p):
    return (p[0] - Y_SHIFT, p[1])


PROFILE0 = [(k, _mv(_P0[k])) for k in ORDER0]
J = _mv(_J)
U_STAY, N_FRONT = _U, _NF


def _perimeter():
    """Distance along LOD0's outline to each point, from A: U on the
    frame's edge strip."""
    s, out = 0.0, {}
    pts = PROFILE0 + [PROFILE0[0]]
    for (k, a), (_, b) in zip(pts, pts[1:]):
        out[k] = s
        s += math.hypot(b[0] - a[0], b[1] - a[1])
    return out, s


PERIM, PERIM_LEN = _perimeter()

# LOD1's outline (80 triangles in all): each foot a point midway across
# it, and the rail's top raised at the back to meet the seat wedge's sloping
# underside (build.py). The stay's top keeps both corners and the rear leg
# its kink, so the plan bounds and the side outline hold. Each point carries
# the LOD0 perimeter distances its incoming and outgoing edges start and end
# at, so LOD1's edges sample the same strip.
_SEAT_FRONT = -Y_SHIFT                       # y of the seat's front
_Q1 = _add(J, _U, SLAT_T / math.cos(TILT))   # stay front at the seat's top


def seat_wedge_z(y):
    """LOD1's seat underside: from (front, Z_RAIL) up to the stay at Z_SEAT."""
    return Z_RAIL + SLAT_T * (y - _SEAT_FRONT) / (_Q1[0] - _SEAT_FRONT)


def _profile1():
    p = dict(PROFILE0)
    P = PERIM
    S = ((p["A"][0] + p["B"][0]) / 2.0, 0.0)
    R = ((p["E"][0] + p["F"][0]) / 2.0, 0.0)
    K1 = (p["K"][0], seat_wedge_z(p["K"][0]))
    # (name, point, perimeter distance in, perimeter distance out)
    return [("S", S, PERIM_LEN, P["B"]), ("C", p["C"], P["C"], P["C"]),
            ("D", p["D"], P["D"], P["D"]), ("R", R, P["E"], P["F"]),
            ("G", p["G"], P["G"], P["G"]), ("H", p["H"], P["H"], P["H"]),
            ("I", p["I"], P["I"], P["I"]), ("J", _Q1, P["J"], P["J"]),
            ("K", K1, P["K"], P["K"])]


PROFILE1 = _profile1()
SEAT_WEDGE = (_SEAT_FRONT, _Q1[0])           # LOD1 seat: y front .. tip


def seat_slats():
    """(y front, y back) of each seat slat, front first."""
    out = []
    for i in range(SEAT_N):
        y0 = _SEAT_FRONT + i * (SEAT_W + SEAT_GAP)
        out.append((y0, y0 + SEAT_W))
    return out


def back_slats():
    """(s foot, s top) of each back slat along the stay, lowest first."""
    return [(BACK_S0 + i * (BACK_W + BACK_GAP),
             BACK_S0 + i * (BACK_W + BACK_GAP) + BACK_W) for i in range(BACK_N)]


def stay_point(s, t):
    """(y, z) at s up the stay's front face and t in front of it."""
    return (J[0] + _U[0] * s + _NF[0] * t, J[1] + _U[1] * s + _NF[1] * t)


def stay_coords(y, z):
    """(s, t) of a point: inverse of stay_point."""
    dy, dz = y - J[0], z - J[1]
    return dy * _U[0] + dz * _U[1], dy * _NF[0] + dz * _NF[1]


SEAT_SLATS = seat_slats()
BACK_SLATS = back_slats()
BACK_S1 = BACK_SLATS[-1][1]

# ================================================================== atlas
# V up, in pixels. Every slat has its own strip at 64 texels/m: U along the
# slat from its -X end, V walking round its section (seat: front face, top,
# back face, underside; back: front face, top edge, rear face, foot edge),
# so each slat's wear and grain are its own. Below them the composites that
# LOD1's two wedges map onto, copied sample by sample from the strips with
# the gaps painted dark between; then the frame's face, U and V its y and z,
# and the frame's edge strip, U the distance round LOD0's outline.
SEAT_PER = 2 * (SEAT_W + SLAT_T)                 # 0.27 m: 17.3 px
BACK_PER = 2 * (BACK_W + BACK_T)                 # 0.22 m: 14.1 px
COL_X = (4.0, 132.0)
SEAT_STRIP = [(COL_X[0], 4.0), (COL_X[1], 4.0), (COL_X[0], 27.0), (COL_X[1], 27.0)]
BACK_STRIP = [(COL_X[0], 50.0), (COL_X[1], 50.0), (COL_X[0], 70.0)]
END_R = (132, 70, 14, 14)                       # slat end grain, a patch
UNDER_R = (152, 70, 14, 14)                     # LOD1 seat's underside
SEAT_COMP = (COL_X[0], 92.0)                    # LOD1 seat top, V = y
BACK_COMP_F = (COL_X[1], 92.0)                  # LOD1 back front, V = s
BACK_COMP_R = (COL_X[1], 118.0)                 # LOD1 back rear, V = s1 - s
FRAME_R = (4.0, 144.0)                          # frame face: U from y', V z
EDGE_R = (4.0, 204.0)                           # frame edges

ID_PAINT, ID_WORN, ID_END, ID_GAP, ID_IRON, ID_BOLT = 0, 1, 2, 3, 4, 5

SURFACE = {ID_PAINT: (0.58, 0.0), ID_WORN: (0.82, 0.0), ID_END: (0.78, 0.0),
           ID_GAP: (0.95, 0.0), ID_IRON: (0.55, 0.0), ID_BOLT: (0.45, 0.6)}

# Municipal green on the timber and black on the iron; or oiled timber on
# dark grey steel. Wear shows grey weathered wood under the green paint,
# bleached wood where the oil has gone.
VARIANTS = {
    "green_painted": {ID_PAINT: (50, 72, 56), ID_WORN: (112, 104, 90),
                      ID_END: (44, 60, 48), ID_IRON: (46, 47, 48)},
    "brown_oiled": {ID_PAINT: (112, 82, 58), ID_WORN: (140, 126, 106),
                    ID_END: (86, 62, 44), ID_IRON: (64, 66, 68)},
}
DEFAULT_VARIANT = "green_painted"
# a gap on LOD1 is a see-through line at ~1 px: whatever lies behind the
# bench, so a neutral mid-dark rather than black
FIXED = {ID_GAP: (70, 70, 68), ID_BOLT: (74, 74, 72)}

ARRIS_H = 0.004               # rounded slat arrises, metres
FRAME_RIM_H = 0.005           # the casting's raised rim
BOLT_R = 0.011                # carriage bolt heads, metres


def m(v):
    return v * PPM


def seat_faces(i):
    """Seat slat i's strip: [(face, v0, v1)] in V order, and its x0."""
    x0, v0 = SEAT_STRIP[i]
    rows, v = [], v0
    for face, h in (("front", SLAT_T), ("top", SEAT_W), ("back", SLAT_T),
                    ("under", SEAT_W)):
        rows.append((face, v, v + m(h)))
        v += m(h)
    return x0, rows


def back_faces(i):
    x0, v0 = BACK_STRIP[i]
    rows, v = [], v0
    for face, h in (("front", BACK_W), ("top", BACK_T), ("rear", BACK_W),
                    ("foot", BACK_T)):
        rows.append((face, v, v + m(h)))
        v += m(h)
    return x0, rows


def face_rows(rows, name):
    return next((a, b) for f, a, b in rows if f == name)


def frame_uv(y, z):
    return FRAME_R[0] + m(y + Y_SHIFT), FRAME_R[1] + m(z)


# ================================================================ painting
def _poly_inside(X, Y, poly):
    """Even-odd point-in-polygon over sample grids."""
    inside = np.zeros(X.shape, bool)
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        cross = ((y1 > Y) != (y2 > Y))
        xi = x1 + (Y - y1) * (x2 - x1) / ((y2 - y1) if y2 != y1 else 1e-12)
        inside ^= cross & (X < xi)
    return inside


def _poly_dist(X, Y, poly):
    d = np.full(X.shape, np.inf, np.float32)
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / max(dx * dx + dy * dy, 1e-12), 0, 1)
        d = np.minimum(d, np.hypot(X - (ax + t * dx), Y - (ay + t * dy)))
    return d


def paint_slat_strip(c, x0, rows, seed):
    """One slat: every face its own bevelled board, grain along U."""
    x1 = x0 + m(LENGTH)
    for _, a, b in rows:
        c.paint(x0, x1, a, b, mid=ID_PAINT, shade=1.0, ao=1.0)
        c.bevel(x0, x1, a, b, ARRIS_H, 0.7)
    sy, sx = c.sl(x0, x1, rows[0][1], rows[-1][2])
    grain = atlas.noise(c, seed, 14.0, 0.25)[sy, sx]
    c.shade[sy, sx] *= 1.0 + 0.035 * grain
    c.height[sy, sx] += 0.0003 * grain


def paint_wear(c, x0, rows, front_slat, kind, seed):
    """Paint worn through to the wood in flecks along the arrises that
    hands and calves rub: the front seat slat's front arris and the top
    back slat's top edge most, the middle 1.2 m where people sit more than
    the ends. At 64 texels/m a fleck is a texel or two; the broad wear of
    the seat is chalking (weather()), not bare wood. Moderate: never a
    bare board."""
    x1 = x0 + m(LENGTH)
    nz = atlas.noise(c, seed, 0.7)
    for face, a, b in rows:
        sy, sx, Y, X = c.field(x0, x1, a, b)
        xm = (X - x0) / PPM - HL                       # metres from the middle
        seat = np.exp(-(np.abs(xm) / 0.6) ** 4)        # where people sit
        if kind == "seat" and face == "top" and front_slat:
            score = 0.75 * np.exp(-(Y - a) / 0.8) * (0.4 + 0.6 * seat)
        elif kind == "seat" and face == "front" and front_slat:
            score = 0.75 * np.exp(-(b - Y) / 0.8) * (0.4 + 0.6 * seat)
        elif kind == "seat" and face == "top":
            score = 0.45 * np.exp(-np.minimum(Y - a, b - Y) / 0.6) * seat
        elif kind == "back" and face == "top":
            score = 0.60 * (0.5 + 0.5 * seat) + np.zeros_like(Y)
        elif kind == "back" and face == "front":
            score = 0.45 * np.exp(-(b - Y) / 0.6) * (0.5 + 0.5 * seat)
        else:
            continue
        worn = score + 0.22 * nz[sy, sx] > 0.80
        c.mid[sy, sx][worn & (c.mid[sy, sx] == ID_PAINT)] = ID_WORN
        # worn wood lies a hair below the paint film
        c.height[sy, sx][worn] -= 0.0004


def paint_bolts(c):
    """Carriage bolt heads over the frames: one per slat per frame, on the
    seat slats' tops and the back slats' front faces."""
    for i in range(SEAT_N):
        x0, rows = seat_faces(i)
        a, b = face_rows(rows, "top")
        for xf in (-FRAME_X, FRAME_X):
            c.disc(x0 + m(xf + HL), (a + b) / 2.0, m(BOLT_R), mid=ID_BOLT,
                   ao=0.8, height=ARRIS_H + 0.003)
    for i in range(BACK_N):
        x0, rows = back_faces(i)
        a, b = face_rows(rows, "front")
        for xf in (-FRAME_X, FRAME_X):
            c.disc(x0 + m(xf + HL), (a + b) / 2.0, m(BOLT_R), mid=ID_BOLT,
                   ao=0.8, height=ARRIS_H + 0.003)


def frame_poly_px():
    return [frame_uv(y, z) for _, (y, z) in PROFILE0]


def paint_frame(c):
    """The casting's face: a flat web inside a raised rim round the
    outline, the rim's outer arris rounded; light pitting."""
    poly = frame_poly_px()
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    sy, sx, Y, X = c.field(min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1)
    inside = _poly_inside(X, Y, poly)
    d = _poly_dist(X, Y, poly)
    rim = FRAME_RIM_H * atlas.smoothstep(2.9, 2.1, d) * atlas.smoothstep(0.0, 0.6, d)
    c.mid[sy, sx][inside] = ID_IRON
    c.shade[sy, sx][inside] = 1.0
    c.ao[sy, sx][inside] = np.minimum(1.0, 0.92 + 0.08 * np.clip(d / 4.0, 0, 1))[inside]
    c.height[sy, sx][inside] = rim[inside]
    # the edge strip: U round the outline, V across the casting
    x0, v0 = EDGE_R
    c.paint(x0, x0 + m(PERIM_LEN), v0, v0 + m(FRAME_T), mid=ID_IRON, shade=1.0, ao=1.0)
    c.bevel(x0, x0 + m(PERIM_LEN), v0, v0 + m(FRAME_T), 0.003, 0.6, axes="y")
    iron = c.mid == ID_IRON
    pit = atlas.noise(c, 21, 0.7)
    c.height[iron] += 0.0004 * pit[iron]
    c.shade[iron] *= 1.0 + 0.04 * atlas.noise(c, 22, 6.0)[iron]


def paint_patches(c):
    x, y, w, h = END_R
    c.paint(x, x + w, y, y + h, mid=ID_END, shade=1.0, ao=0.9, height=0.0)
    sy, sx = c.sl(x, x + w, y, y + h)
    c.shade[sy, sx] *= 1.0 + 0.06 * atlas.noise(c, 31, 0.6, 3.0)[sy, sx]
    x, y, w, h = UNDER_R
    c.paint(x, x + w, y, y + h, mid=ID_PAINT, shade=0.9, ao=0.85, height=0.0)


def edge_z(U):
    """Height above the ground of the frame edge strip's column U (pixels)."""
    s = (U - EDGE_R[0]) / PPM
    ss = [PERIM[k] for k in ORDER0] + [PERIM_LEN]
    zs = [p[1] for _, p in PROFILE0] + [PROFILE0[0][1][1]]
    return np.interp(s, ss, zs)


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it is.
    The timber chalks and greys on its upward faces; dirt and a little
    rust at the frames' feet; rust round the bolt heads; road dust."""
    w = weathering.Weather(c, clean=(ID_GAP,), steel=(ID_IRON, ID_BOLT))
    w.grime(0.03)
    w.fade((ID_PAINT, ID_IRON), amount=0.08, base=0.02)
    timber = (ID_PAINT, ID_WORN)
    for i in range(SEAT_N):
        x0, rows = seat_faces(i)
        a, b = face_rows(rows, "top")
        w.add("F", x0 - 1, x0 + m(LENGTH) + 1, a, b, lambda Y, X, nz, x0=x0:
              0.05 + 0.12 * np.exp(-((X - x0) / PPM - HL) ** 4 / 0.6 ** 4)
              * (0.7 + 0.3 * nz("blotch")), (ID_PAINT,))
        a, b = face_rows(rows, "under")
        w.add("D", x0 - 1, x0 + m(LENGTH) + 1, a, b, 0.06, timber)
    for i in range(BACK_N):
        x0, rows = back_faces(i)
        a, b = face_rows(rows, "front")
        w.add("F", x0 - 1, x0 + m(LENGTH) + 1, a, b, 0.04, (ID_PAINT,))
        a, b = face_rows(rows, "top")
        w.add("D", x0 - 1, x0 + m(LENGTH) + 1, a, b, 0.10, timber)
    # the frame's feet: soil splash up the face, the strip by its height
    fx, fy = FRAME_R
    w.splash(fx - 2, fx + 44, fy - 2, fy + m(0.5), (ID_IRON,), amount=0.30,
             fall=0.10, specks=0.15, speck_fall=0.20)
    w.add("R", fx - 2, fx + 44, fy - 2, fy + m(0.06), lambda Y, X, nz:
          0.14 * nz("blotch") * np.exp(-(Y - fy) / 2.5), (ID_IRON,))
    ex, ey = EDGE_R
    ex1 = ex + m(PERIM_LEN)
    w.add("D", ex - 2, ex1 + 2, ey - 2, ey + m(FRAME_T) + 2, lambda Y, X, nz:
          0.32 * np.exp(-edge_z(X) / 0.10) * (0.6 + 0.4 * nz("blotch")), (ID_IRON,))
    w.add("R", ex - 2, ex1 + 2, ey - 2, ey + m(FRAME_T) + 2, lambda Y, X, nz:
          0.16 * np.exp(-edge_z(X) / 0.04), (ID_IRON,))
    # faint rust bleeding round the bolt heads
    for i in range(SEAT_N + BACK_N):
        if i < SEAT_N:
            x0, rows = seat_faces(i)
            a, b = face_rows(rows, "top")
        else:
            x0, rows = back_faces(i - SEAT_N)
            a, b = face_rows(rows, "front")
        for xf in (-FRAME_X, FRAME_X):
            cx, cy = x0 + m(xf + HL), (a + b) / 2.0
            r = m(BOLT_R)
            w.add("R", cx - 4 * r, cx + 4 * r, a, b, lambda Y, X, nz, cx=cx, cy=cy, r=r:
                  0.30 * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (1.6 * r) ** 2),
                  timber + (ID_BOLT,))
    return w


def _copy_rows(c, src_x0, src_v, dst_x0, dst_v):
    """Copy one sample row (pixel coordinate src_v) across a slat's length
    to the composite row dst_v, every channel and weather field."""
    s = c.ss
    n = int(round(m(LENGTH) * s))
    rs, rd = int(src_v * s), int(dst_v * s)
    cs, cd = int(round(src_x0 * s)), int(round(dst_x0 * s))
    for a in (c.mid, c.shade, c.ao, c.height):
        a[rd, cd:cd + n] = a[rs, cs:cs + n]
    for a in c.weather.f.values():
        a[rd, cd:cd + n] = a[rs, cs:cs + n]


def paint_composites(c):
    """LOD1's wedges: the slats' faces side by side with the gaps dark,
    copied from the strips row by row so the wear and grain match LOD0."""
    s = c.ss

    def fill(dst_x0, dst_v0, span, lookup):
        rows = int(math.ceil(m(span) * s))
        n = int(round(m(LENGTH) * s))
        cd = int(round(dst_x0 * s))
        for k in range(rows):
            v = dst_v0 + (k + 0.5) / s                  # pixel coordinate
            q = (k + 0.5) / s / PPM                     # metres into the span
            src = lookup(q)
            rd = int(dst_v0 * s) + k
            if src is None:
                c.mid[rd, cd:cd + n] = ID_GAP
                c.shade[rd, cd:cd + n] = 1.0
                c.ao[rd, cd:cd + n] = 0.8
                c.height[rd, cd:cd + n] = -0.002
                for a in c.weather.f.values():
                    a[rd, cd:cd + n] = 0.0
            else:
                _copy_rows(c, src[0], src[1], dst_x0, v)

    def seat_top(q):
        y = SEAT_WEDGE[0] + q
        for i, (y0, y1) in enumerate(SEAT_SLATS):
            if y0 <= y < y1:
                x0, rows = seat_faces(i)
                a, _ = face_rows(rows, "top")
                return x0, a + m(y - y0)
        return None

    def back(face):
        def look(q):
            s_ = BACK_S0 + q if face == "front" else BACK_S1 - q
            for i, (s0, s1) in enumerate(BACK_SLATS):
                if s0 <= s_ < s1:
                    x0, rows = back_faces(i)
                    a, _ = face_rows(rows, face)
                    return x0, a + m(s_ - s0 if face == "front" else s1 - s_)
            return None
        return look
    fill(SEAT_COMP[0], SEAT_COMP[1], SEAT_WEDGE[1] - SEAT_WEDGE[0], seat_top)
    fill(BACK_COMP_F[0], BACK_COMP_F[1], BACK_S1 - BACK_S0, back("front"))
    fill(BACK_COMP_R[0], BACK_COMP_R[1], BACK_S1 - BACK_S0, back("rear"))


def check_layout():
    """The regions fit the atlas and keep clear of one another."""
    problems = []
    rects = []
    for i in range(SEAT_N):
        x0, rows = seat_faces(i)
        rects.append(("seat%d" % i, x0, x0 + m(LENGTH), rows[0][1], rows[-1][2]))
    for i in range(BACK_N):
        x0, rows = back_faces(i)
        rects.append(("back%d" % i, x0, x0 + m(LENGTH), rows[0][1], rows[-1][2]))
    for name, (x, y, w, h) in (("end", END_R), ("under", UNDER_R)):
        rects.append((name, x, x + w, y, y + h))
    rects.append(("seat_comp", SEAT_COMP[0], SEAT_COMP[0] + m(LENGTH), SEAT_COMP[1],
                  SEAT_COMP[1] + m(SEAT_WEDGE[1] - SEAT_WEDGE[0])))
    for name, (x, y) in (("back_comp_f", BACK_COMP_F), ("back_comp_r", BACK_COMP_R)):
        rects.append((name, x, x + m(LENGTH), y, y + m(BACK_S1 - BACK_S0)))
    poly = frame_poly_px()
    rects.append(("frame", min(p[0] for p in poly), max(p[0] for p in poly),
                  min(p[1] for p in poly), max(p[1] for p in poly)))
    rects.append(("edge", EDGE_R[0], EDGE_R[0] + m(PERIM_LEN), EDGE_R[1],
                  EDGE_R[1] + m(FRAME_T)))
    for name, x0, x1, y0, y1 in rects:
        if x0 < 2 or y0 < 2 or x1 > ATLAS - 2 or y1 > ATLAS - 2:
            problems.append("%s leaves the atlas" % name)
    for i, (n1, a0, a1, b0, b1) in enumerate(rects):
        for n2, c0, c1, d0, d1 in rects[i + 1:]:
            if a0 < c1 + 3 and c0 < a1 + 3 and b0 < d1 + 3 and d0 < b1 + 3:
                problems.append("%s and %s are closer than 3 px" % (n1, n2))
    return problems


def paint(ss=atlas.SS):
    problems = check_layout()
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))
    c = atlas.Canvas(ATLAS, ss, PPM)
    for i in range(SEAT_N):
        x0, rows = seat_faces(i)
        paint_slat_strip(c, x0, rows, 40 + i)
        paint_wear(c, x0, rows, i == 0, "seat", 60 + 2 * i)
    for i in range(BACK_N):
        x0, rows = back_faces(i)
        paint_slat_strip(c, x0, rows, 50 + i)
        paint_wear(c, x0, rows, False, "back", 80 + 2 * i)
    paint_bolts(c)
    paint_frame(c)
    paint_patches(c)
    weather(c)
    paint_composites(c)
    c.pad()
    return c


def lut(variant):
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    for i, col in VARIANTS[variant].items():
        t[i] = col
    return t


def export(out_dir, ss=atlas.SS):
    """Albedo per variant, one ORM and one normal map; no emission."""
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.0, depth_m=0.004)
    c.weather.dust(cav, (ID_PAINT, ID_WORN, ID_IRON), amount=0.12)
    rough = 0.03 * atlas.noise(c, 13, 6.0)
    maps = {"orm": atlas.orm(c, SURFACE, rough, 0.4 * cav),
            "normal": atlas.normal_map(c, flat_ids=(ID_GAP,))}
    for v in VARIANTS:
        maps["albedo_" + v] = atlas.albedo(c, lut(v), grime=0.15 * cav)
    os.makedirs(out_dir, exist_ok=True)
    return [atlas.save(arr, os.path.join(out_dir, "%s_%s.png" % (ASSET, key)))
            for key, arr in maps.items()]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(HERE, "export")):
            print(p)
    else:
        print(__doc__)
