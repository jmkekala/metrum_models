# SPDX-License-Identifier: GPL-3.0-or-later

"""estate_compact: the car's shape and UV layout, as plain face lists.

numpy only, so the texture generator (estate_atlas.py, system Python) and
build.py (Blender) read one description: every tier's faces with their
kind, surface id, paint flag and atlas UVs, the wheel, mirror and roof-rail
solids, and the wheel-arch cutters build.py subtracts.

Build frame: metres, Z up, front toward -Y, +X the driver's left, origin on
the ground at the centre of the body's plan box. Internally the length is
measured as s from the front bumper (y = s - HL).

The body is a closed shell lofted through stations along the length. Each
station is a loop of rows round the section, the same rows on every
station (SIDE_ROWS from the sill to the belt, TOP_ROWS from the glass
bottom over the roof to the centre line); its points carry their own s, so
a station bends where a pillar leans. The two ends are grids ("caps")
whose rows are the side rows and whose columns are the top rows, laid
round the plan corner, so the bumper faces, the lamps and the corners are
cells of one grid. Each cap row is one smooth plan curve (bowed across the
face, a superellipse round the corner) at its own setback, so the nose
leans back and rounds in plan, and the side rows taper in plan toward
both ends and flare round the arches (hw()). Lamps, panes and plates are whole cells or bilinear
sub-cells of the grid; build.py conforms the T-junctions away.
"""

import math

import numpy as np

ASSET = "estate_compact"
ATLAS = 1024                        # every vehicle class's atlas (owner's decision)
PPM = 128.0
SC = 2                              # the layout below was drawn at 512: scaled to 1024

# ================================================================ dimensions
L = 4.48
HL = L / 2.0
HW = 0.895                          # half the body width (1.79)
WHEEL_R, TYRE_W, TRACK = 0.32, 0.205, 1.54
WHEEL_X = TRACK / 2.0
S_AXLE = (0.86, 3.51)               # from the front bumper: 0.86 / 0.97 overhangs
ARCH_R, ARCH_DZ = 0.37, 0.015       # arch opening, its centre above the axle
LINER_X = 0.465                     # the arch liner's inner wall

# K1..K3 are cap-only columns round the plan corners: the end stations
# carry them, the tube between does not.
ROWS = ("SB", "S1", "S2", "S3", "S4", "S5", "SH", "K1", "GB", "K2", "GT", "K3", "RE", "R1",
        "R2", "R3", "RC")
SIDE_ROWS = ROWS[:7]
TOP_ROWS = ROWS[7:]
CAP_ONLY = ("K1", "K2", "K3")
IDX = {r: i for i, r in enumerate(ROWS)}

# The section amidships: the door skin fullest under the shoulder crease
# (S5), barrelled 0.04 down to the sill and leaning in above the crease to
# the belt (SH). In plan the body tapers toward both ends, the shoulder rows
# most, and the rows at arch height stand proud round the wheels, where the
# body reaches its full width.
W_MID = dict(SB=0.832, S1=0.852, S2=0.871, S3=0.880, S4=0.883, S5=0.876, SH=0.850)
TAPER_F = dict(SB=0.020, S1=0.016, S2=0.004, S3=0.000, S4=0.004, S5=0.020, SH=0.044)
TAPER_R = dict(SB=0.015, S1=0.012, S2=0.006, S3=0.006, S4=0.016, S5=0.030, SH=0.040)
# (S4 runs just over the arches' tops and is not cut away there: it is
# the row that carries the full width)
FLARE = dict(S1=0.006, S2=0.016, S3=0.018, S4=0.018, S5=0.010)
FLARE_LEN = 0.34
Z_MID = dict(SB=0.23, S1=0.30, S2=0.43, S3=0.62, S4=0.77)
SHOULDER = 0.065                    # the crease (S5) under the belt

# The ends, row by row: z on the centre line, z at the side (None: the
# belt's), the setback from the bumper line at the centre, the bow across
# the face, the distance D from the bumper line at which the row reaches
# the body side, and the plan corner's superellipse exponent (2 a
# quarter ellipse, more a squarer corner).
#
# The nose: a lip tucked 0.10 under, the bumper fullest at 0.515 (S3), its
# top rolling back to a shelf (S4 to S5) under the lamps and the grille,
# which lean back about 30 degrees to the bonnet's leading edge (SH), 0.15
# behind the bumper and 0.26 above it. Every row bows across the face and
# sweeps round the corner, the upper ones further, so the lamps lie on a
# surface that turns back along the wing; their foot (S5) climbs toward the
# side, where it runs on as the shoulder crease.
CAP = {
    "front": dict(
        rows=dict(SB=(0.190, 0.190, 0.105, 0.035, 0.40, 3.0),
                  S1=(0.270, 0.270, 0.040, 0.040, 0.39, 3.1),
                  S2=(0.385, 0.400, 0.010, 0.045, 0.38, 3.2),
                  S3=(0.515, 0.530, 0.000, 0.050, 0.38, 3.2),
                  S4=(0.605, 0.665, 0.022, 0.055, 0.40, 3.1),
                  S5=(0.635, 0.715, 0.062, 0.060, 0.42, 3.0),
                  SH=(0.800, None, 0.125, 0.075, 0.48, 2.8)),
        # inner columns: x, the same on every row or row by row (the grille
        # an inverted trapezoid, the lamps' inner edges parallel to it)
        inner=dict(RC=0.0, R3=0.13, R2=0.26,
                   R1=dict(SB=0.34, S1=0.34, S2=0.37, S3=0.36, S4=0.325, S5=0.31, SH=0.385),
                   RE=dict(SB=0.42, S1=0.42, S2=0.50, S3=0.46, S4=0.40, S5=0.37, SH=0.445)),
        # outer columns: degrees, x = xRE + (W - xRE) sin(angle)
        outer=dict(K3=20.0, GT=38.0, K2=54.0, GB=68.0, K1=80.0),
        # how late a row climbs to its side height: the lamps' foot stays
        # level under the inner cells and climbs round the corner
        rise=dict(S4=3.0, S5=3.0), rise_default=2.2),
    "rear": dict(
        rows=dict(SB=(0.250, 0.250, 0.055, 0.030, 0.29, 3.0),
                  S1=(0.330, 0.330, 0.008, 0.040, 0.29, 3.0),
                  S2=(0.520, 0.520, 0.000, 0.045, 0.30, 3.0),
                  S3=(0.640, 0.640, 0.035, 0.045, 0.32, 3.0),
                  S4=(0.800, 0.850, 0.105, 0.045, 0.36, 3.0),
                  S5=(0.975, 1.000, 0.190, 0.040, 0.40, 3.2),
                  SH=(1.050, None, 0.290, 0.030, 0.43, 4.0)),
        inner=dict(RC=0.0, R3=0.12, R2=0.26, R1=0.42,
                   RE=dict(SB=0.575, S1=0.575, S2=0.575, S3=0.575, S4=0.575, S5=0.575, SH=0.60)),
        outer=dict(K3=11.0, GT=21.0, K2=48.0, GB=62.0, K1=77.0),
        rise={}, rise_default=2.0),
}

PLATE_W, PLATE_H = 0.52, 0.11


# ================================================================ helpers
def pchip(xs, ys, x):
    """Monotone cubic interpolation (Fritsch-Carlson), clamped at the ends."""
    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)
    h = np.diff(xs)
    d = np.diff(ys) / h
    m = np.zeros_like(ys)
    m[0], m[-1] = d[0], d[-1]
    for k in range(1, len(xs) - 1):
        if d[k - 1] * d[k] > 0:
            w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
    x = min(max(float(x), xs[0]), xs[-1])
    k = min(int(np.searchsorted(xs, x, side="right")) - 1, len(xs) - 2)
    t = (x - xs[k]) / h[k]
    h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
    h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
    return float(h00 * ys[k] + h10 * h[k] * m[k] + h01 * ys[k + 1] + h11 * h[k] * m[k + 1])


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def P(x, s, z):
    """A build-frame point from (x, s, z)."""
    return (float(x), float(s - HL), float(z))


def s_of(p):
    return p[1] + HL


# ================================================================ profiles
BELT = ((0.30, 0.80), (0.62, 0.818), (0.86, 0.842), (1.08, 0.872), (1.30, 0.903),
        (1.40, 0.92), (3.88, 1.065), (4.00, 1.062), (4.10, 1.05))
# the bonnet's centre line: rolling up from its leading edge, then about 10
# degrees to the cowl
BONNET_C = ((0.125, 0.800), (0.21, 0.832), (0.34, 0.856), (0.70, 0.916), (1.00, 0.965),
            (1.27, 1.010))
BONNET_CROWN = 0.100                # z falls by this times x squared
ROOF_C = ((2.05, 1.400), (2.40, 1.432), (2.80, 1.446), (3.20, 1.446), (3.60, 1.432),
          (3.99, 1.395))
GLASS_TOP = ((1.99, 1.345), (2.40, 1.360), (3.00, 1.362), (3.80, 1.335))
ROOF_CROWN = dict(RE=-0.048, R1=-0.022, R2=-0.010, R3=-0.003, RC=0.0)
ROOF_X = dict(R1=0.52, R2=0.35, R3=0.17, RC=0.0)
# behind the windscreen's header the roof keeps its edge, the row under the
# rails and the centre line: its crown is 22 mm over half a metre
ROOF_SPARE = ("R2", "R3")
ROOF_STATIONS = ("B1", "B2", "M1", "C1", "C2", "X1", "D1", "RF", "RL", "RG")


def _tab(t, s):
    return pchip([a for a, _ in t], [b for _, b in t], s)


def belt(s):
    return _tab(BELT, s)


def bonnet_z(s, x):
    """The bonnet: crowned across, with a soft raised centre."""
    return _tab(BONNET_C, s) - BONNET_CROWN * x * x + 0.010 * math.exp(-(x / 0.28) ** 2)


def roof_z(s, row):
    return _tab(ROOF_C, s) + ROOF_CROWN[row]


def roof_edge_x(s):
    return pchip([2.05, 3.0, 3.99], [0.655, 0.645, 0.632], s)


def hw(row, s):
    """A side row's half-width at s: the section amidships, tapered in plan
    toward the ends and flared round the arches, never past HW."""
    w = W_MID[row] - TAPER_F[row] * (1.0 - smoothstep(0.45, 1.80, s)) \
        - TAPER_R[row] * smoothstep(3.00, 4.30, s)
    fl = FLARE.get(row, 0.0)
    if fl:
        w += fl * max(math.exp(-((s - S_AXLE[0]) / FLARE_LEN) ** 2),
                      math.exp(-((s - S_AXLE[1]) / FLARE_LEN) ** 2))
    return min(w, HW)


def z_side(row, s):
    """A side row's height at a straight-side station s."""
    if row == "SH":
        return belt(s)
    zm = belt(s) - SHOULDER if row == "S5" else Z_MID[row]
    zf, zr = cap_ze("front", row), cap_ze("rear", row)
    # (the crease leaves the lamp's foot for its place under the belt by
    # the front axle, clear of the row over the arch)
    z = zf + (zm - zf) * smoothstep(0.38, 0.90 if row == "S5" else 1.25, s)
    return z + (zr - z) * smoothstep(3.80, 4.12, s)


def gb_x(s):
    """The side glass's foot: a narrow painted shoulder inside the belt."""
    return min(0.828, hw("SH", s) - 0.022)


# ================================================================ caps
# A tier whose cap keeps no row on the bumper's foremost line stands one of
# its rows there instead, so every tier has the plan box: (level, end) ->
# that row, which takes the plan of the end's foremost row (FLUSH_AS).
FLUSH = {}
FLUSH_AS = {"front": "S3", "rear": "S2"}


def _cap_row(end, row, level=0):
    return CAP[end]["rows"][FLUSH_AS[end] if FLUSH.get((level, end)) == row else row]


def cap_d(end, row, level=0):
    """Distance from the bumper line at which the row reaches the side."""
    return _cap_row(end, row, level)[4]


def cap_s_side(end, row, level=0):
    d = cap_d(end, row, level)
    return d if end == "front" else L - d


def cap_w(end, row, level=0):
    """The row's half-width where it reaches the body side."""
    return hw(row, cap_s_side(end, row, level))


def cap_ze(end, row):
    ze = CAP[end]["rows"][row][1]
    return belt(cap_s_side(end, row)) if ze is None else ze


def cap_s(end, row, x, level=0):
    """s of the row's plan outline at x: bowed across the face, a
    superellipse round the corner, tangent to the side at x = W."""
    _zc, _ze, sb, bow, d, n = _cap_row(end, row, level)
    r = min(abs(x) / cap_w(end, row, level), 1.0)
    ds = sb + bow * r * r + (d - sb - bow) * (1.0 - (1.0 - r ** n) ** (1.0 / n))
    return ds if end == "front" else L - ds


def cap_z(end, row, x):
    """A cap row's height at x: level across the face, climbing (or
    falling) to its side height round the corner."""
    zc = CAP[end]["rows"][row][0]
    r = min(abs(x) / cap_w(end, row), 1.0)
    return zc + (cap_ze(end, row) - zc) * r ** CAP[end]["rise"].get(row, CAP[end]["rise_default"])


def cap_x(end, row, col, level=0):
    """x of column *col* on row *row*."""
    w = cap_w(end, row, level)
    if col == "SIDE":
        return w
    spec = CAP[end]
    if col in spec["inner"]:
        v = spec["inner"][col]
        return v[row] if isinstance(v, dict) else v
    xre = spec["inner"]["RE"][row]
    return xre + (w - xre) * math.sin(math.radians(spec["outer"][col]))


def cap_point(end, row, col, sign=1, level=0):
    x = cap_x(end, row, col, level)
    return P(sign * x, cap_s(end, row, x, level), cap_z(end, row, x))


# ================================================================ stations
def side_part(s, rows=SIDE_ROWS, shift=None):
    shift = shift or {}
    return {r: (hw(r, s + shift.get(r, 0.0)), s + shift.get(r, 0.0),
                z_side(r, s + shift.get(r, 0.0)))
            for r in rows}


def roof_part(s, rows=("RE", "R1", "R2", "R3", "RC")):
    out = {}
    for r in rows:
        x = roof_edge_x(s) if r == "RE" else ROOF_X[r]
        out[r] = (x, s, roof_z(s, r))
    return out


def gb(s):
    return (gb_x(s), s, belt(s) + 0.012)


def gt(s, x=0.683):
    return (x, s, _tab(GLASS_TOP, s))


BONNET_F = (0.14, 0.47, 0.70, 0.962)      # the bonnet stations, leading edge to cowl


def key_stations():
    """Every LOD0 station as (name, {row: (x, s, z)}) for the x >= 0 half,
    front to rear."""
    st = []
    # F0: the front cap's boundary
    f0 = {r: _xsz(cap_point("front", r, "SIDE")) for r in SIDE_ROWS}
    f0.update({r: _xsz(cap_point("front", "SH", r)) for r in TOP_ROWS})
    cw = side_part(1.30)
    cw.update(GB=(min(0.832, hw("SH", 1.34) - 0.012), 1.34, belt(1.34) + 0.010),
              GT=(0.815, A_GT_BASE, 0.94),
              RE=(0.70, 1.315, 0.975), R1=(0.525, 1.29, 0.993), R2=(0.35, 1.277, 1.004),
              R3=(0.175, 1.271, 1.009), RC=(0.0, 1.27, 1.010))
    hd = side_part(2.00)
    hd.update(GB=gb(2.00), GT=(0.685, A_GT_TOP, 1.345), RE=(0.655, 2.085, 1.368),
              R1=(0.51, 2.07, 1.383), R2=(0.34, 2.06, 1.392), R3=(0.17, 2.052, 1.398),
              RC=(0.0, 2.05, 1.400))
    st.append(("F0", f0))
    for k, f in enumerate(BONNET_F):
        st.append(("F%d" % (k + 1), _bonnet(f0, cw, f)))
    st.append(("CW", cw))
    for name, f, fg, s in (("A1", 1.0 / 3.0, 0.18, 1.53), ("A2", 2.0 / 3.0, 0.59, 1.81)):
        st.append((name, _screen(cw, hd, f, s, fg)))
    st.append(("HD", hd))
    for name, sg, st_ in (("B1", 2.39, 2.39), ("B2", 2.49, 2.49), ("M1", 2.80, 2.80),
                          ("C1", 3.12, 3.15), ("C2", 3.28, 3.25), ("X1", S_AXLE[1], 3.51)):
        d = side_part(sg)
        d.update(GB=gb(sg), GT=gt(st_))
        d.update(roof_part(st_))
        st.append((name, d))
    d1 = side_part(3.88)
    d1.update(GB=gb(3.88), GT=gt(3.865, 0.678))
    d1.update(roof_part(3.875))
    st.append(("D1", d1))
    rf = side_part(3.92)
    rf.update(GB=(gb_x(3.92) - 0.002, 3.92, belt(3.92) + 0.011), GT=(0.676, 3.95, 1.322),
              RE=(0.632, 3.98, 1.350))
    rf.update({r: (ROOF_X[r], 3.99, roof_z(3.99, r)) for r in ("R1", "R2", "R3", "RC")})
    rl = side_part(3.96)
    rl.update(GB=(gb_x(3.95) - 0.004, 3.95, belt(3.95) + 0.011), GT=(0.672, 3.975, 1.308),
              RE=(0.618, 4.012, 1.343))
    rl.update({r: (ROOF_X[r] * 0.97, 4.032, 1.376 + 0.85 * ROOF_CROWN[r])
               for r in ("R1", "R2", "R3", "RC")})
    rg = side_part(4.00)
    rg.update(GB=(gb_x(3.98) - 0.006, 3.98, belt(3.98) + 0.011), GT=(0.668, 3.995, 1.292),
              RE=(0.600, 4.016, 1.322))
    rg.update({r: (ROOF_X[r] * 0.94, 4.022, 1.346 + 0.7 * ROOF_CROWN[r])
               for r in ("R1", "R2", "R3", "RC")})
    st += [("RF", rf), ("RL", rl), ("RG", rg)]
    r0 = {r: _xsz(cap_point("rear", r, "SIDE")) for r in SIDE_ROWS}
    r0.update({r: _xsz(cap_point("rear", "SH", r)) for r in TOP_ROWS})
    st.append(("R0", r0))
    for name, d in st:
        if name in ROOF_STATIONS:
            for r in ROOF_SPARE:
                d.pop(r, None)
    return st


def _xsz(p):
    return (p[0], s_of(p), p[2])


def _bonnet(f0, cw, f):
    """A station across the bonnet at fraction f from the leading edge (F0)
    to the cowl (CW)."""
    d = {}
    for r in SIDE_ROWS:
        s = f0[r][1] + (cw[r][1] - f0[r][1]) * f
        d[r] = (hw(r, s), s, z_side(r, s))
    for r in TOP_ROWS:
        if r not in cw:
            continue
        (x0, s0, z0), (x1, s1, z1) = f0[r], cw[r]
        x, s = x0 + (x1 - x0) * f, s0 + (s1 - s0) * f
        if r == "GB":
            # the wing top: the bonnet's edge, rolling down to the belt
            z = bonnet_z(s, x) + (z0 - bonnet_z(s0, x0)) * (1 - f) + (z1 - bonnet_z(s1, x1)) * f
        else:
            z = bonnet_z(s, x) + (z0 - bonnet_z(s0, x0)) * (1 - f) ** 2 \
                + (z1 - bonnet_z(s1, x1)) * f ** 2
        d[r] = (x, s, z)
    return d


# The A-pillar: a band of constant width beside the windscreen's side edge
# (RE from the cowl to the header, about 27 degrees in side view); the side
# glass's front edge (GT) runs parallel to it, A_PILLAR behind, from the
# mirror patch at its foot to the glass top.
A_PILLAR = 0.08
_RE0, _RE1 = (1.315, 0.975), (2.085, 1.368)
_SLOPE = (_RE1[1] - _RE0[1]) / (_RE1[0] - _RE0[0])
_DROP = A_PILLAR * math.hypot(1.0, _SLOPE)


def _a_gt_s(z):
    return _RE0[0] + (z - _RE0[1] + _DROP) / _SLOPE


A_GT_BASE = _a_gt_s(0.94)
A_GT_TOP = _a_gt_s(1.345)


def _screen(cw, hd, f, s_side, f_gt=None):
    """A station across the windscreen at fraction f from the cowl to the
    header; the A-pillar rows (GT, RE) climb with it, the belt and the side
    rows stay at s_side."""
    d = side_part(s_side)
    d["GB"] = gb(s_side)
    bulge = 0.014 * math.sin(math.pi * f)
    for r in ("GT", "RE", "R1", "R2", "R3", "RC"):
        (x0, s0, z0), (x1, s1, z1) = cw[r], hd[r]
        g = f_gt if (r == "GT" and f_gt is not None) else f
        x, s, z = x0 + (x1 - x0) * g, s0 + (s1 - s0) * g, z0 + (z1 - z0) * g
        k = {"GT": 0.0, "RE": 0.0, "R1": 0.75, "R2": 0.95, "R3": 1.0, "RC": 1.0}[r]
        # the screen bows outward, along its normal (-0.447, 0.894) in (s, z)
        s -= 0.447 * bulge * k
        z += 0.894 * bulge * k
        if r in ("GT", "RE"):
            x += 0.010 * math.sin(math.pi * g)
        d[r] = (x, s, z)
    return d


# ================================================================ tiers
class Tier:
    """What a tier keeps: its stations, its tube rows, and per end the cap's
    rows and columns (supersets of the tube's; the end station carries the
    extra points, so the cap meets the tube without a T-junction)."""

    def __init__(self, level, stations, rows, cap):
        self.level = level
        self.stations = stations
        self.rows = [r for r in ROWS if r in rows]
        self.cap = {end: ([r for r in SIDE_ROWS if r in cr], [c for c in TOP_ROWS if c in cc])
                    for end, (cr, cc) in cap.items()}

    def loop_rows(self, station):
        extra = ()
        if station in ("F0", "R0"):
            cr, cc = self.cap["front" if station == "F0" else "rear"]
            extra = tuple(cr) + tuple(cc)
        return [r for r in ROWS if r in self.rows or r in extra]


ALL_STATIONS = [n for n, _ in key_stations()]
_CAP0 = (SIDE_ROWS, TOP_ROWS)
_CAP_K = ("K1", "K2", "K3")
TIERS = {
    0: Tier(0, ALL_STATIONS, [r for r in ROWS if r not in CAP_ONLY],
            {"front": _CAP0, "rear": _CAP0}),
    1: Tier(1, ["F0", "F2", "CW", "HD", "B1", "B2", "C1", "C2", "D1", "RL", "RG", "R0"],
            ("S1", "S3", "S4", "SH", "GT", "RE", "RC"),
            {"front": (("S1", "S3", "S4", "S5", "SH"), ("GB", "GT", "RE", "R2", "RC")),
             "rear": (("S1", "S3", "S4", "S5", "SH"), ("GB", "GT", "RE", "RC"))}),
    # LOD2's sides start at the sill's top (S1): its painted faces never
    # sample the black sill, and the wheel prisms show more under them
    2: Tier(2, ["F0", "CW", "HD", "RG", "R0"], ("S1", "SH", "GT", "RC"),
            {"front": (("S1", "S5", "SH"), ("GB", "GT", "RE", "RC")),
             "rear": (("S1", "S4", "S5", "SH"), ("GB", "GT", "RE", "RC"))}),
}
# a cap strip that keeps fewer columns than the tier's (its cells become
# polygons over the row points the neighbouring strips need)
STRIP_COLS = {(2, "front", "S1"): ("RC", "SIDE"), (2, "rear", "S1"): ("RC", "RE", "SIDE")}
LOD2_SB_X = HW            # LOD2 keeps no widest row: its sill carries the width
FLUSH.update({(2, "front"): "S1", (2, "rear"): "S1", (1, "rear"): "S3"})


# ================================================================ faces
class Face:
    __slots__ = ("pts", "kind", "surface", "paint", "smooth", "island", "uv", "lens", "part")

    def __init__(self, pts, kind, surface=0, paint=False, smooth=True, island=None):
        self.pts = [tuple(float(c) for c in p) for p in pts]
        self.kind, self.surface, self.paint = kind, int(surface), bool(paint)
        self.smooth, self.island = smooth, island
        self.uv, self.lens, self.part = None, None, None

    def normal(self):
        p = np.array(self.pts)
        n = np.zeros(3)
        for k in range(1, len(p) - 1):
            n += np.cross(p[k] - p[0], p[k + 1] - p[0])
        ln = np.linalg.norm(n)
        return n / ln if ln > 0 else n

    def centre(self):
        return tuple(np.mean(np.array(self.pts), axis=0))


def bil(q, a, b):
    """Bilinear point of quad q = (p00, p10, p11, p01) at (a, b)."""
    p00, p10, p11, p01 = (np.array(c) for c in q)
    return tuple((1 - a) * (1 - b) * p00 + a * (1 - b) * p10 + a * b * p11 + (1 - a) * b * p01)


def sub(q, a0, a1, b0, b1):
    return [bil(q, a0, b0), bil(q, a1, b0), bil(q, a1, b1), bil(q, a0, b1)]


def inset(q, a0, a1, b0, b1, kind, rest="paint"):
    """q with one sub-rectangle [a0, a1] x [b0, b1] of another kind: full
    height strips either side of it, and the column through it cut in
    three (five faces at most)."""
    out = []
    if a0 > 1e-6:
        out.append((sub(q, 0.0, a0, 0.0, 1.0), rest))
    if b0 > 1e-6:
        out.append((sub(q, a0, a1, 0.0, b0), rest))
    out.append((sub(q, a0, a1, b0, b1), kind))
    if b1 < 1 - 1e-6:
        out.append((sub(q, a0, a1, b1, 1.0), rest))
    if a1 < 1 - 1e-6:
        out.append((sub(q, a1, 1.0, 0.0, 1.0), rest))
    return out


def kind_args(k):
    """A kind -> Face kwargs. Kinds: "paint", a trim word, ("lamp", id),
    ("glass", id)."""
    if isinstance(k, tuple):
        what, ident = k
        return dict(kind=what, surface=ident, paint=False)
    return dict(kind=k, surface=0, paint=(k == "paint"))


# --------------------------------------------------------------- body
def station_points(level):
    tier = TIERS[level]
    names = dict(key_stations())
    out = []
    for n in tier.stations:
        half = dict(names[n])
        low = tier.rows[0]
        if level == 2 and n not in ("F0", "R0"):
            x, s, z = half[low]
            half[low] = (LOD2_SB_X, s, z)
        if n in ("F0", "R0"):
            end = "front" if n == "F0" else "rear"
            r = FLUSH.get((level, end))
            if r:
                half[r] = _xsz(cap_point(end, r, "SIDE", level=level))
        rows = tier.loop_rows(n)
        out.append((n, {r: half[r] for r in rows if r in half}))
    return out


def body_faces(level):
    tier = TIERS[level]
    stations = station_points(level)
    faces = []
    for (na, ha), (nb, hb) in zip(stations[:-1], stations[1:]):
        # the rows both stations carry: a row one of them lacks (the cap's
        # corner columns, the roof's spare rows) ends there as a point of
        # the cell's polygon
        major = [r for r in tier.rows if r in ha and r in hb]
        for sign in (-1, 1):
            for lo, hi in zip(major[:-1], major[1:]):
                def pts(h, rows):
                    return [P(sign * h[r][0] if r != "RC" else 0.0, h[r][1], h[r][2])
                            for r in rows]
                ra = [r for r in ROWS if r in ha and IDX[lo] <= IDX[r] <= IDX[hi]]
                rb = [r for r in ROWS if r in hb and IDX[lo] <= IDX[r] <= IDX[hi]]
                poly = pts(ha, ra) + pts(hb, rb)[::-1]
                q = None
                if len(ra) == 2 and len(rb) == 2:
                    q = (poly[0], poly[3], poly[2], poly[1])   # a along, b up
                for p, kd in tube_cell(level, (na, nb), (lo, hi), sign, q, poly):
                    f = Face(p, **kind_args(kd))
                    if (lo, hi) == ("GT", "RE") and f.kind == "paint" \
                            and na not in ("F0", "F1", "F2", "F3", "F4"):
                        # the pillars and the roof's side (not the bonnet's
                        # strip ahead of the cowl): always the side island,
                        # whatever their slope
                        f.island = "side_l" if sign > 0 else "side_r"
                    faces.append(f)
        # the underside strip, sill to sill
        a, b = ha[major[0]], hb[major[0]]
        faces.append(Face([P(-a[0], a[1], a[2]), P(a[0], a[1], a[2]), P(b[0], b[1], b[2]),
                           P(-b[0], b[1], b[2])], "under", smooth=False, island="under"))
    for end in ("front", "rear"):
        faces += cap_faces(end, tier)
    return faces


def tube_cell(level, seg, pair, sign, q, poly):
    """Faces of one tube cell. q is the quad (a along the length, b from the
    lower row up) when the cell has four corners, else None (a polygon at
    an end station with the cap's extra points)."""
    lo, hi = pair
    k = "paint"
    if lo == "SB" and hi == "S1":
        k = "lip"                       # the black sill trim and bumper lips
    if (lo, hi) == ("S4", "S5") and seg == ("RG", "R0") and q is not None:
        # the tail lamp's wrap runs out to a point on the shoulder crease
        return [([q[1], q[2], q[3]], ("lamp", 1)), ([q[0], q[1], q[3]], "paint")]
    if hi == "SH" and seg[0] == "F0" and level < 2:
        # the headlamp's swept tip on the wing: the indicator runs out to a
        # point on the shoulder line, TIP_S behind the bumper
        return lamp_tip(poly, sign)
    if seg == ("F4", "CW") and IDX[lo] >= IDX["RE"]:
        k = "lip"                       # the cowl panel under the wipers
    side_glass = (lo, hi) == ("GB", "GT") or (level >= 1 and (lo, hi) == ("SH", "GT"))
    if side_glass:
        k = {("CW", "A1"): "sail", ("A1", "A2"): ("glass", 33), ("A2", "HD"): ("glass", 33),
             ("HD", "B1"): ("glass", 33), ("B1", "B2"): "pillar", ("B2", "M1"): ("glass", 34),
             ("B2", "C1"): ("glass", 34),
             ("M1", "C1"): ("glass", 34), ("C1", "C2"): "pillar",
             ("C2", "D1"): ("glass", 34), ("C2", "X1"): ("glass", 34),
             ("X1", "D1"): ("glass", 34)}.get(seg, "paint")
        if level == 1 and seg == ("CW", "HD"):
            k = ("glass", 33)
        if level == 2:
            k = ("glass", 33) if seg in (("CW", "HD"), ("HD", "RG")) else "paint"
    top = IDX[lo] >= IDX["RE" if level < 2 else "GT"]
    if top:
        if seg in (("CW", "A1"), ("A1", "A2"), ("A2", "HD"), ("CW", "HD")):
            k = ("glass", 32)
        elif seg == ("RG", "R0"):
            k = ("glass", 35)
        elif seg == ("RL", "RG") and hi == "RC":
            if lo == "R3":
                k = ("lamp", 2)
            elif q is not None:
                # the high-mounted stop lamp: the inner part of a wider cell,
                # kept inside the LOD0 lens
                b0 = 1.0 - 0.150 / max(abs(q[0][0]), abs(q[1][0]), 1e-6)
                a0, a1 = 0.12, 0.88
                return inset(q, a0, a1, b0, 1.0, ("lamp", 2))
    return [(poly, k)]


TIP_S = 0.57


def lamp_tip(poly, sign):
    """The first side cell under the belt, cut for the headlamp's tip:
    *poly* runs up the front station (lower row, any cap rows, SH) and back
    down the next one. The lamp is the triangle from the lamp's foot (S5)
    and the bonnet's edge (SH) on the front station to a point on the
    shoulder line."""
    n_a = len(poly) - 2                 # points on the front station
    a_pts, b_hi, b_lo = poly[:n_a], poly[n_a], poly[n_a + 1]
    a_hi, a_foot = a_pts[-1], a_pts[-2]
    s0, s1 = s_of(a_hi), s_of(b_hi)
    f = min(max((TIP_S - s0) / (s1 - s0), 0.05), 1.0)
    tip = tuple(np.array(a_hi) + (np.array(b_hi) - np.array(a_hi)) * f)
    rest = a_pts[:-1][::-1] + [b_lo, b_hi] + ([tip] if f < 1.0 - 1e-6 else [])
    return [([a_foot, tip, a_hi], ("lamp", 4 if sign > 0 else 5)), (rest, "paint")]


def cap_faces(end, tier):
    rows, cols = tier.cap[end]
    half = cols[::-1] + ["SIDE"]                      # RC .. SIDE
    across = [(c, -1) for c in half[::-1] if c != "RC"] + [("RC", 0)] \
        + [(c, 1) for c in half[1:]]

    def strip_cols(i):
        keep = STRIP_COLS.get((tier.level, end, rows[i]))
        return [j for j, (c, _s) in enumerate(across) if keep is None or c in keep]

    # the points each row needs: the columns of the strips below and above
    need = []
    for i in range(len(rows)):
        js = set()
        for k in (i - 1, i):
            if 0 <= k < len(rows) - 1:
                js |= set(strip_cols(k))
        need.append(sorted(js))
    grid = {}
    for i, r in enumerate(rows):
        for j in need[i]:
            c, sg = across[j]
            grid[i, j] = cap_point(end, r, c, sg if sg else 1, tier.level) if c != "RC" else \
                _centre(cap_point(end, r, "RC", level=tier.level))
    faces = []
    for i in range(len(rows) - 1):
        js = strip_cols(i)
        for j0, j1 in zip(js[:-1], js[1:]):
            (c0, s0), (c1, s1) = across[j0], across[j1]
            sign = s0 if s0 else s1
            col = (c0, c1) if sign > 0 else (c1, c0)      # inner column first
            low = [grid[i, j] for j in need[i] if j0 <= j <= j1]
            up = [grid[i + 1, j] for j in need[i + 1] if j0 <= j <= j1]
            if len(low) == 2 and len(up) == 2:
                q = [low[0], low[1], up[1], up[0]]
                if sign < 0:
                    q = [q[1], q[0], q[3], q[2]]          # a from the inner column out
                for pts, kd in cap_cell(end, tier.level, (rows[i], rows[i + 1]), col, sign, q):
                    faces.append(Face(pts, **kind_args(kd)))
            else:
                kd = cap_cell(end, tier.level, (rows[i], rows[i + 1]), col, sign, None)
                poly = low + up[::-1]
                faces.append(Face(poly, **kind_args(kd)))
    faces.append(Face([grid[0, j] for j in need[0]][::-1], "under", smooth=False,
                      island="under"))
    return faces


def _centre(p):
    return (0.0, p[1], p[2])


PLATE_Z = {"front": (0.395, 0.505), "rear": (0.665, 0.775)}
DRL_B = 0.26              # the daytime strip's share of the lamp's height, from its foot
GRILLE_A = 0.56           # LOD1: the grille's outer edge inside its wider cell
FOG = (0.445, 0.555, 0.381, 0.452)      # the rear fog lamp: x0, x1, z0, z1 (LOD0)


def _fractions(end, q, lo, hi, x0, x1, z0, z1):
    """a, b fractions of a cap cell for an x and z range (rows are level)."""
    zl, zh = cap_z(end, lo, abs(q[0][0])), cap_z(end, hi, abs(q[3][0]))
    xa, xb = abs(q[0][0]), abs(q[1][0])
    return ((x0 - xa) / (xb - xa), (x1 - xa) / (xb - xa),
            (z0 - zl) / (zh - zl), (z1 - zl) / (zh - zl))


def cap_cell(end, level, rowpair, col, sign, q):
    """q = (inner-lower, outer-lower, outer-upper, inner-upper)."""
    lo, hi = rowpair
    ci, co = col
    left = sign > 0
    ind = ("lamp", 4 if left else 5)
    front = end == "front"
    if (lo, hi) == ("SB", "S1"):
        return [(q, "lip")] if q is not None else "lip"
    if q is None:
        return "paint"
    pz0, pz1 = PLATE_Z[end]
    zl, zh = CAP[end]["rows"][lo][0], CAP[end]["rows"][hi][0]
    xa, xb = abs(q[0][0]), abs(q[1][0])
    if level < 2 and zl <= pz0 + 1e-6 and zh >= pz1 - 1e-6 and xa < PLATE_W / 2 - 1e-3:
        a1 = min(1.0, (PLATE_W / 2 - xa) / (xb - xa))
        if a1 > 0.995:
            a1 = 1.0
        b0, b1 = (pz0 - zl) / (zh - zl), (pz1 - zl) / (zh - zl)
        return inset(q, 0.0, a1, max(b0, 0.0), min(b1, 1.0), "plate")
    if front:
        if (lo, hi) == ("S1", "S2"):
            inner = co in ("R3", "R2", "R1", "RE")
            if (ci, co) == ("K3", "GT"):
                # a round fog lamp in the bumper's pod, its own atlas patch
                return inset(q, 0.10, 0.90, 0.14, 0.86, "foglamp")
            return [(q, "intake" if inner else "paint")]
        if hi == "SH":
            # the band under the bonnet's edge: the grille between the
            # lamps, a painted post either side of it, then each lamp from
            # its inner end out: high beam, low beam, the indicator in the
            # swept tip; the daytime strip along the foot of the high beam
            if co in ("R3", "R2", "R1") or (level == 2 and co == "RE"):
                return [(q, "grille")]
            if (ci, co) == ("R2", "RE"):
                return [(sub(q, 0, GRILLE_A, 0, 1), "grille"), (sub(q, GRILLE_A, 1, 0, 1), "paint")]
            if co == "RE":
                return [(q, "paint")]
            if co in ("K3", "GT"):
                return [(sub(q, 0, 1, 0, DRL_B), ("lamp", 9)), (sub(q, 0, 1, DRL_B, 1), ("lamp", 8))]
            if co in ("K2", "GB"):
                return [(q, ("lamp", 7))]
            if co in ("K1", "SIDE"):
                return [(q, ind)]
        return [(q, "paint")]
    # rear
    if zl <= FOG[2] and zh >= FOG[3] and xa <= FOG[0] and xb >= 0.5 * (FOG[0] + FOG[1]) \
            and (left or level == 0):
        # the rear fog lamp on the left; a red reflector in its place on the
        # right (LOD0 only: the coarser tiers leave it to the texture)
        a0, a1, b0, b1 = _fractions(end, q, lo, hi, *FOG)
        if level:
            m = 0.18 * (a1 - a0)
            a0, a1 = a0 + m, a1 - m
            m = 0.18 * (b1 - b0)
            b0, b1 = b0 + m, b1 - m
        return inset(q, a0, a1, b0, b1, ("lamp", 11) if left else "reflector")
    if (lo, hi) == ("S4", "S5"):
        if co in ("K3", "GT"):
            return [(sub(q, 0, 1, 0, 0.46), ("lamp", 6)), (sub(q, 0, 1, 0.46, 1), ind)]
        if co in ("K2", "GB"):
            return [(q, ("lamp", 3))]
        if co in ("K1", "SIDE"):
            return [(q, ("lamp", 1))]
    return [(q, "paint")]


# --------------------------------------------------------------- cutters
def arch_cutter(axle, sign, level):
    """The closed prism a wheel arch is cut with: the opening's arc (in s, z)
    from just under the body round over the top, closed below the ground,
    from the liner wall at |x| = LINER_X to outside the body."""
    sc = S_AXLE[axle]
    zc = WHEEL_R + ARCH_DZ
    n = {0: 16, 1: 5}.get(level, 5)
    a0, a1 = math.radians(-36.0), math.radians(216.0)
    arc = [(sc + ARCH_R * math.cos(a0 + (a1 - a0) * k / n),
            zc + ARCH_R * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
    poly = arc + [(arc[-1][0], -0.05), (arc[0][0], -0.05)]
    xi, xo = sign * LINER_X, sign * 1.10
    faces = []
    m = len(poly)
    for k in range(m):
        (s0, z0), (s1, z1) = poly[k], poly[(k + 1) % m]
        faces.append(Face([P(xi, s0, z0), P(xo, s0, z0), P(xo, s1, z1), P(xi, s1, z1)],
                          "liner", smooth=False, island="under"))
    faces.append(Face([P(xi, s, z) for s, z in poly], "liner", smooth=False, island="under"))
    faces.append(Face([P(xo, s, z) for s, z in poly[::-1]], "liner", smooth=False,
                      island="under"))
    return faces


# ================================================================ atlas layout
# rects (x, y, w, h) in atlas pixels, V up
R_SIDE_L = (32, 32, 580, 192)
R_SIDE_R = (32, 232, 580, 192)
R_TOP = (32, 448, 580, 120)
R_GLASS_SIDE = (32, 608, 364, 72)
R_GLASS_BAND = (32, 704, 364, 72)
R_GLASS_WS = (416, 608, 192, 120)
R_GLASS_TG = (416, 768, 168, 52)
R_FRONT = (640, 32, 124, 96)
R_REAR = (640, 160, 124, 164)
R_UNDER = (128, 832, 56, 56)
R_PLATE = (880, 304, 80, 24)


def island_of(face):
    if face.island:
        return face.island
    if face.kind == "glass":
        return {32: "glass_ws", 33: "glass_side", 34: "glass_side", 35: "glass_tg"}[face.surface]
    if face.kind == "lamp":
        return "lens"
    if face.kind == "plate":
        return "plate"
    n = outward(face)
    k = int(np.argmax(np.abs(n)))
    if k == 0:
        return "side_l" if n[0] > 0 else "side_r"
    if k == 1:
        return "front" if n[1] < 0 else "rear"
    return "top" if n[2] > 0 else "under"


def outward(face):
    """The face's unit normal, turned away from the body's core line: the
    faces are wound as built, and build.py lets Blender orient them."""
    n = face.normal()
    c = np.array(face.centre())
    core = np.array((0.0, min(max(c[1], -1.2), 1.2), 0.70))
    return n if n @ (c - core) >= 0 else -n


def project(island, p):
    """Atlas pixel (u, v) of build-frame point p in a projected island."""
    x, y, z = p
    s = y + HL
    if island in ("side_l", "side_r"):
        r = R_SIDE_L if island == "side_l" else R_SIDE_R
        u = s * PPM if island == "side_l" else (L - s) * PPM
        return (r[0] + 1 + u, r[1] + 1 + z * PPM)
    if island == "top":
        return (R_TOP[0] + 1 + s * PPM, R_TOP[1] + 1 + abs(x) * PPM)
    if island == "front":
        return (R_FRONT[0] + 1 + abs(x) * PPM, R_FRONT[1] + 1 + (z - 0.15) * PPM)
    if island == "rear":
        return (R_REAR[0] + 1 + abs(x) * PPM, R_REAR[1] + 1 + (z - 0.18) * PPM)
    if island == "under":
        return (R_UNDER[0] + 2 + (x + 1.1) / 2.2 * (R_UNDER[2] - 4),
                R_UNDER[1] + 2 + s / L * (R_UNDER[3] - 4))
    if island == "glass_side":
        return (R_GLASS_SIDE[0] + 2 + (s - 1.25) * PPM, R_GLASS_SIDE[1] + 2 + (z - 0.88) * PPM)
    if island == "glass_band":
        return (R_GLASS_BAND[0] + 2 + (s - 1.25) * PPM, R_GLASS_BAND[1] + 2 + (z - 0.88) * PPM)
    if island == "glass_ws":
        v = (s - 1.27) * 0.894 + (z - 1.01) * 0.447
        return (R_GLASS_WS[0] + R_GLASS_WS[2] / 2.0 + x * PPM, R_GLASS_WS[1] + 2 + v * PPM)
    if island == "glass_tg":
        v = (s - 4.20) * -0.499 + (z - 1.05) * 0.866
        return (R_GLASS_TG[0] + R_GLASS_TG[2] / 2.0 + x * PPM, R_GLASS_TG[1] + 2 + v * PPM)
    raise KeyError(island)


def _group_uvs(faces, island, pick, rect_of):
    """Planar-map each connected group of picked faces onto its rect, by
    the group's own mean plane: a plate, a lens."""
    sel = [f for f in faces if pick(f)]
    for grp in _components(sel):
        pts = np.array([p for f in grp for p in f.pts])
        n = sum((outward(f) * _area(f) for f in grp), np.zeros(3))
        n /= np.linalg.norm(n)
        u = np.cross((0, 0, 1.0), n)
        if np.linalg.norm(u) < 1e-6:
            u = np.array((1.0, 0.0, 0.0))
        u /= np.linalg.norm(u)
        v = np.cross(n, u)
        pu, pv = pts @ u, pts @ v
        rx, ry, rw, rh = rect_of(grp)
        for f in grp:
            q = np.array(f.pts)
            f.uv = [(rx + 1 + (a - pu.min()) / (pu.max() - pu.min()) * (rw - 2),
                     ry + 1 + (b - pv.min()) / (pv.max() - pv.min()) * (rh - 2))
                    for a, b in zip(q @ u, q @ v)]


def _area(f):
    p = np.array(f.pts)
    n = np.zeros(3)
    for k in range(1, len(p) - 1):
        n += np.cross(p[k] - p[0], p[k + 1] - p[0])
    return np.linalg.norm(n) / 2.0


def _components(faces):
    key = lambda p: tuple(round(c, 5) for c in p)  # noqa: E731
    parent = list(range(len(faces)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    by = {}
    for i, f in enumerate(faces):
        for p in f.pts:
            by.setdefault(key(p), []).append(i)
    for ids in by.values():
        for j in ids[1:]:
            a, b = find(ids[0]), find(j)
            if a != b:
                parent[max(a, b)] = min(a, b)
    groups = {}
    for i in range(len(faces)):
        groups.setdefault(find(i), []).append(faces[i])
    return list(groups.values())


# ================================================================ more rects
R_WHEEL_FACE = (800, 32, 192, 192)
R_WHEEL_INNER = (384, 832, 48, 48)
R_FLAT_PAINT = (288, 832, 32, 32)
R_MIRROR_GLASS = (256, 832, 24, 24)
R_RAIL = (192, 832, 32, 32)
R_REFLECTOR = (352, 832, 24, 24)
R_TREAD = (772, 240, 248, 40)
# lenses, each in its own 64 x 32 cell of a coarse grid, so that a
# minified atlas does not bleed one lens into another or into paint (the
# paint islands end on 32-texel boundaries, with a free block before any
# dark or coloured patch)
# The lamps carry the car's face in a small area: their rects are painted at
# LENS_PPM, 1.75 times the body's density, in 192 x 96 cells.
LENS_PPM = 224.0
LENS_CELLS = [(640 + 192 * i, 384 + 96 * j) for j in range(6) for i in range(2)]
R_FOGLAMP = LENS_CELLS[-1][0] + 64, LENS_CELLS[-1][1] + 16, 64, 64


# ================================================================ wheels
# profile (x outward from the wheel's centre plane, radius), inner side first
WHEEL_PROFILE = {
    # tread from the inner face, the outer shoulder, the sidewall down to a
    # rim lip standing 2 mm proud, the lip, and the spoke face dished 38 mm
    0: [(-TYRE_W / 2, WHEEL_R), (0.080, WHEEL_R), (TYRE_W / 2, 0.292), (0.1045, 0.226),
        (0.096, 0.214), (0.066, 0.208)],
    1: [(-TYRE_W / 2, WHEEL_R), (TYRE_W / 2, WHEEL_R)],
}
WHEEL_SIDES = {0: 16, 1: 8}
TREAD_SEGS = {0: (0, 2), 1: (0, 1)}       # profile segments mapped to the tread strip


def wheel_faces(level, outward):
    """One wheel in its own frame (centre at the origin, axis along X), as
    faces with UVs: the tyre's crown and shoulders on the tread strip, the
    sidewall and rim on the wheel-face square, the inner face on its patch.
    *outward* +1 for a left wheel, -1 for a right one. A corner of the tread
    sits at the very bottom."""
    n = WHEEL_SIDES[level]
    prof = [(x * outward, r) for x, r in WHEEL_PROFILE[level]]
    ang = [-math.pi / 2 + 2 * math.pi * k / n for k in range(n)]
    ring = [(math.cos(a), math.sin(a)) for a in ang]
    t0, t1 = TREAD_SEGS[level]
    arc = [0.0]
    for (x0, r0), (x1, r1) in zip(prof[t0:t1], prof[t0 + 1:t1 + 1]):
        arc.append(arc[-1] + math.hypot(x1 - x0, r1 - r0))
    tx, ty, tw, th = R_TREAD
    fx, fy, fw, fh = R_WHEEL_FACE
    k_face = (fw / 2.0 - 1.0) / WHEEL_R

    def face_uv(p, rect=R_WHEEL_FACE):
        x, y, w, h = rect
        k = (w / 2.0 - 1.0) / WHEEL_R
        return (x + w / 2.0 + p[1] * k, y + h / 2.0 + p[2] * k)
    faces = []
    for j in range(len(prof) - 1):
        (x0, r0), (x1, r1) = prof[j], prof[j + 1]
        tread = t0 <= j < t1
        for k in range(n):
            (c0, s0), (c1, s1) = ring[k], ring[(k + 1) % n]
            q = [(x0, r0 * c0, r0 * s0), (x0, r0 * c1, r0 * s1),
                 (x1, r1 * c1, r1 * s1), (x1, r1 * c0, r1 * s0)]
            f = Face(q, "tyre" if j < len(prof) - 2 or level else "rim", smooth=True,
                     island="wheel")
            if tread:
                va = ty + 1 + (th - 2) * arc[j - t0] / arc[-1]
                vb = ty + 1 + (th - 2) * arc[j - t0 + 1] / arc[-1]
                ua, ub = tx + 2 + (tw - 4) * k / n, tx + 2 + (tw - 4) * (k + 1) / n
                f.uv = [(ua, va), (ub, va), (ub, vb), (ua, vb)]
                f.kind = "tread"
            else:
                f.uv = [face_uv(p) for p in q]
                f.kind = "tyre" if j < len(prof) - 2 else "rim"
            faces.append(f)
    # the outer face (rim, or a LOD1 prism's whole side) and the inner face
    xo, ro = prof[-1]
    xi, ri = prof[0]
    outer = [(xo, ro * c, ro * s) for c, s in ring]
    f = Face(outer, "rim", smooth=False, island="wheel")
    f.uv = [face_uv(p) for p in outer]
    faces.append(f)
    inner = [(xi, ri * c, ri * s) for c, s in ring][::-1]
    f = Face(inner, "wheel_inner", smooth=False, island="wheel")
    f.uv = [face_uv(p, R_WHEEL_INNER) for p in inner]
    faces.append(f)
    del k_face, fx, fy, fh
    return faces


WHEELS = [  # part, x, s, steer
    (1, WHEEL_X, S_AXLE[0], True), (2, -WHEEL_X, S_AXLE[0], True),
    (3, WHEEL_X, S_AXLE[1], False), (4, -WHEEL_X, S_AXLE[1], False),
]


# ================================================================ mirrors
MIRROR_C = (1.465, 1.025)                  # housing centre (s, z)
MIRROR_SECTION = [(0.052, -0.056), (-0.015, -0.064), (-0.056, -0.030), (-0.060, 0.016),
                  (-0.026, 0.056), (0.052, 0.060)]
MIRROR_LOFT = {   # x, scale, centre (s, z)
    0: [(0.800, 0.42, (1.48, 0.990)), (0.842, 0.42, (1.48, 0.990)), (0.853, 0.80, MIRROR_C),
        (0.870, 0.97, MIRROR_C), (0.945, 1.0, MIRROR_C), (0.990, 0.92, MIRROR_C),
        (1.010, 0.70, MIRROR_C)],
    1: [(0.800, 0.85, MIRROR_C), (0.990, 0.92, MIRROR_C), (1.010, 0.70, MIRROR_C)],
}
MIRROR_GLASS_SEG = {0: (3, 4), 1: (0, 1)}            # the loft segment whose rear face is glass


def mirror_faces(level, sign):
    loft = MIRROR_LOFT[level]
    secs = [[P(sign * x, c[0] + k * ds, c[1] + k * dz) for ds, dz in MIRROR_SECTION]
            for x, k, c in loft]
    n = len(MIRROR_SECTION)
    faces = []
    for j in range(len(secs) - 1):
        a, b = secs[j], secs[j + 1]
        for k in range(n):
            q = [a[k], b[k], b[(k + 1) % n], a[(k + 1) % n]]
            glass = (k == n - 1 and j in MIRROR_GLASS_SEG[level])
            faces.append(Face(q, "mirror_glass" if glass else "paint", paint=not glass,
                              smooth=not glass, island="mirror"))
    faces.append(Face(secs[0][::-1], "paint", paint=True, smooth=False, island="mirror"))
    # the outer end: the side repeater across its front
    e = secs[-1]
    m1 = tuple((np.array(e[1]) + np.array(e[2])) / 2)
    m2 = tuple((np.array(e[3]) + np.array(e[4])) / 2)
    ind = 4 if sign > 0 else 5
    faces.append(Face([m1, e[2], e[3], m2], "lamp", surface=ind, smooth=False))
    faces.append(Face([e[0], e[1], m1, m2, e[4], e[5]], "paint", paint=True, smooth=False,
                      island="mirror"))
    return faces


# ================================================================ roof rails
RAIL_X = 0.525
RAIL_SECTION = {0: [(0.017, 0.0), (0.012, 0.032), (-0.012, 0.032), (-0.017, 0.0)],
                1: [(0.017, 0.0), (0.0, 0.032), (-0.017, 0.0)]}
RAIL_STATIONS = {0: [(2.26, -0.014), (2.34, 0.010), (2.70, 0.012), (3.10, 0.012),
                     (3.50, 0.012), (3.86, 0.010), (3.94, -0.014)],
                 1: [(2.26, -0.014), (3.10, 0.012), (3.94, -0.014)]}


def rail_faces(level, sign):
    secs = []
    for s, lift in RAIL_STATIONS[level]:
        zb = roof_z(s, "R1") + lift        # R1 runs at x 0.52, under the rail
        secs.append([P(sign * (RAIL_X + dx), s, zb + dz) for dx, dz in RAIL_SECTION[level]])
    n = len(RAIL_SECTION[level])
    faces = []
    for a, b in zip(secs[:-1], secs[1:]):
        for k in range(n):
            faces.append(Face([a[k], b[k], b[(k + 1) % n], a[(k + 1) % n]], "rail",
                              smooth=False, island="rail"))
    faces.append(Face(secs[0][::-1], "rail", smooth=False, island="rail"))
    faces.append(Face(secs[-1], "rail", smooth=False, island="rail"))
    return faces


# ================================================================ lenses
def lens_key(f):
    """Which lens rect a lamp face maps to: its id (right indicators as the
    left ones), its end, and the mirror's repeater apart."""
    lid = 4 if f.surface == 5 else f.surface
    c = f.centre()
    if f.island == "mirror_lens" or abs(c[0]) > HW + 0.01:
        return (lid, "mirror")
    return (lid, "front" if c[1] < 0 else "rear")


_LENS_REF = {}


def lens_refs():
    """Per lens key, the LOD0 left (or centre) lens: its projection axes and
    extents, and its atlas rect, centred in its LENS_CELLS cell."""
    if _LENS_REF:
        return _LENS_REF
    faces = [f for f in body_faces(0) + mirror_faces(0, 1) if f.kind == "lamp"]
    groups = {}
    comps = [g for lid in sorted({f.surface for f in faces})
             for g in _components([f for f in faces if f.surface == lid])]
    for grp in comps:
        c = np.mean([f.centre() for f in grp], axis=0)
        if c[0] < -0.01:
            continue
        groups.setdefault(lens_key(grp[0]), grp)
    for key, cell in zip(sorted(groups), LENS_CELLS):
        grp = groups[key]
        pts = np.array([p for f in grp for p in f.pts])
        n = sum((outward(f) * _area(f) for f in grp), np.zeros(3))
        n /= np.linalg.norm(n)
        u = np.cross((0, 0, 1.0), n)
        if np.linalg.norm(u) < 1e-6:
            u = np.array((1.0, 0.0, 0.0))
        u /= np.linalg.norm(u)
        v = np.cross(n, u)
        pu, pv = pts @ u, pts @ v
        w = int(math.ceil((pu.max() - pu.min()) * LENS_PPM)) + 6
        h = int(math.ceil((pv.max() - pv.min()) * LENS_PPM)) + 6
        if w > 176 or h > 84:
            raise ValueError("lens %s (%d x %d px) overflows its cell" % (key, w, h))
        cx, cy = cell[0] + (192 - w) // 2, cell[1] + (96 - h) // 2
        _LENS_REF[key] = dict(u=u, v=v, lo=(pu.min(), pv.min()), hi=(pu.max(), pv.max()),
                              rect=(cx, cy, w, h))
    if len(groups) > len(LENS_CELLS) - 1:
        raise ValueError("more lenses than lens cells")
    return _LENS_REF


def lens_uv(f):
    ref = lens_refs()[lens_key(f)]
    rx, ry, rw, rh = ref["rect"]
    (ulo, vlo), (uhi, vhi) = ref["lo"], ref["hi"]
    out = []
    for p in f.pts:
        q = np.array((abs(p[0]), p[1], p[2]))
        a, b = q @ ref["u"], q @ ref["v"]
        out.append((rx + 3 + (a - ulo) / (uhi - ulo) * (rw - 6),
                    ry + 3 + (b - vlo) / (vhi - vlo) * (rh - 6)))
    return out


def small_uv(rect, f, axes=(1, 2)):
    """A face squeezed onto a small uniform patch: a flat colour."""
    x, y, w, h = rect
    out = []
    for p in f.pts:
        a, b = p[axes[0]], p[axes[1]]
        out.append((x + 2 + (w - 4) * (0.5 + 0.5 * math.sin(a * 7.0)),
                    y + 2 + (h - 4) * (0.5 + 0.5 * math.sin(b * 7.0))))
    return out


# ================================================================ pieces
def level_of_faces(faces):
    """2 for a LOD2 body list (it has no tube row GB), else 0."""
    return getattr(faces, "level", 0)


class Faces(list):
    level = 0


def assign_all(faces):
    """UVs for any face list (body, mirror, rail, cutter)."""
    for f in faces:
        if f.uv is not None and f.island in ("wheel", "lod3"):
            continue
        if f.kind == "lamp":
            f.uv = lens_uv(f)
            continue
        if f.island == "mirror":
            f.uv = small_uv(R_MIRROR_GLASS if f.kind == "mirror_glass" else R_FLAT_PAINT, f)
            continue
        if f.island == "rail":
            f.uv = small_uv(R_RAIL, f, (1, 0))
            continue
        if f.kind == "reflector":
            f.island = "reflector"
            f.uv = small_uv(R_REFLECTOR, f, (0, 2))
            continue
        isl = island_of(f)
        if isl == "glass_side" and level_of_faces(faces) == 2:
            isl = "glass_band"
        f.island = isl
        if isl == "plate" or f.kind == "foglamp":
            f.island = f.kind
            continue
        f.uv = [project(isl, p) for p in f.pts]
    _group_uvs(faces, "plate", lambda f: f.kind == "plate", lambda key: R_PLATE)
    _group_uvs(faces, "foglamp", lambda f: f.kind == "foglamp", lambda key: R_FOGLAMP)
    return faces


def tier(level):
    """Everything build.py needs for one tier: body faces, arch cutters,
    mirrors, rails and wheels, every face with its UVs."""
    if level == 3:
        return {"body": assign_all(Faces(lod3_faces())), "cutters": [], "mirrors": [], "rails": [],
                "wheels": []}
    body = Faces(body_faces(level))
    body.level = level
    out = {"body": assign_all(body), "cutters": [], "mirrors": [], "rails": [],
           "wheels": []}
    if level <= 1:
        for ax in (0, 1):
            for sg in (1, -1):
                out["cutters"].append(assign_all(arch_cutter(ax, sg, level)))
        for sg in (1, -1):
            out["mirrors"].append(assign_all(mirror_faces(level, sg)))
            out["rails"].append(assign_all(rail_faces(level, sg)))
        for part, x, s, steer in WHEELS:
            out["wheels"].append((part, P(x, s, WHEEL_R), steer,
                                  wheel_faces(level, 1 if x > 0 else -1)))
    else:
        out["axles"] = [axle_faces(s) for s in S_AXLE]
    return out


AXLE_SIDES = 5


def axle_faces(s):
    """LOD2: an axle's two wheels as one prism through the body, a corner
    on the ground; the tread on the tread strip, the ends on the wheel face."""
    n = AXLE_SIDES
    ring = [(math.cos(-math.pi / 2 + 2 * math.pi * k / n),
             math.sin(-math.pi / 2 + 2 * math.pi * k / n)) for k in range(n)]
    xo = WHEEL_X + TYRE_W / 2
    tx, ty, tw, th = R_TREAD
    faces = []
    for k in range(n):
        (c0, s0), (c1, s1) = ring[k], ring[(k + 1) % n]
        q = [P(-xo, s + WHEEL_R * c0, WHEEL_R * (1 + s0)), P(xo, s + WHEEL_R * c0, WHEEL_R * (1 + s0)),
             P(xo, s + WHEEL_R * c1, WHEEL_R * (1 + s1)), P(-xo, s + WHEEL_R * c1, WHEEL_R * (1 + s1))]
        f = Face(q, "tread", smooth=False, island="wheel")
        u0, u1 = tx + 2 + (tw - 4) * k / n, tx + 2 + (tw - 4) * (k + 1) / n
        f.uv = [(u0, ty + 1), (u0, ty + th - 1), (u1, ty + th - 1), (u1, ty + 1)]
        faces.append(f)
    fx, fy, fw, fh = R_WHEEL_FACE
    kf = (fw / 2.0 - 1.0) / WHEEL_R
    for sg in (1, -1):
        pts = [P(sg * xo, s + WHEEL_R * c, WHEEL_R * (1 + si)) for c, si in ring]
        f = Face(pts if sg > 0 else pts[::-1], "rim", smooth=False, island="wheel")
        f.uv = [(fx + fw / 2.0 + (p[1] + HL - s) * kf, fy + fh / 2.0 + (p[2] - WHEEL_R) * kf)
                for p in f.pts]
        faces.append(f)
    return faces


# LOD3: the side profile, extruded across the width (s, z, kind of the
# perimeter face that starts at the point). Each side is three polygons cut
# along existing profile points: the glasshouse (cowl, header, roof end,
# glass foot), the lower strip (chin, the wheel contacts, the tail's foot)
# and the painted body between, so the triangle count is the plain
# extrusion's. Every face samples one uniform 64-texel block, so no mip
# mixes paint with glass or under-body.
LOD3_PROFILE = [(0.0, 0.515, "paint"), (0.125, 0.80, "paint"), (1.27, 1.01, "lod3_glass"),
                (2.05, 1.40, "paint"), (3.99, 1.395, "lod3_glass"), (4.19, 1.05, "paint"),
                (4.48, 0.52, "paint"), (4.43, 0.25, "lod3_under"), (3.51, 0.0, "lod3_under"),
                (0.86, 0.0, "lod3_under"), (0.06, 0.20, "paint")]
LOD3_SIDES = [((2, 3, 4, 5), "lod3_glass"), ((7, 8, 9, 10), "lod3_under"),
              ((0, 1, 2, 5, 6, 7, 10), "paint")]
R_L3_PAINT = (448, 896, 64, 64)
R_L3_GLASS = (512, 896, 64, 64)
R_L3_UNDER = (576, 896, 64, 64)
L3_BLOCK = {"paint": R_L3_PAINT, "lod3_glass": R_L3_GLASS, "lod3_under": R_L3_UNDER}


def _block_uv(kind, pts):
    """Every corner well inside the kind's uniform block."""
    x, y, w, h = L3_BLOCK[kind]
    return [(x + w / 2.0 + 6.0 * math.sin(7.0 * (p[1] + p[2])),
             y + h / 2.0 + 6.0 * math.cos(7.0 * (p[0] + p[2]))) for p in pts]


def lod3_faces():
    prof = LOD3_PROFILE
    n = len(prof)
    faces = []
    for sg in (1, -1):
        for idx, kind in LOD3_SIDES:
            pts = [P(sg * HW, prof[i][0], prof[i][1]) for i in idx]
            f = Face(pts if sg > 0 else pts[::-1], kind, paint=(kind == "paint"),
                     smooth=False, island="lod3")
            f.uv = _block_uv(kind, f.pts)
            faces.append(f)
    for k in range(n):
        (s0, z0, kind), (s1, z1, _) = prof[k], prof[(k + 1) % n]
        q = [P(-HW, s0, z0), P(HW, s0, z0), P(HW, s1, z1), P(-HW, s1, z1)]
        f = Face(q, kind, paint=(kind == "paint"), smooth=False, island="lod3")
        f.uv = _block_uv(kind, q)
        faces.append(f)
    return faces


LEVELS_BUILT = (0, 1, 2, 3)
