# SPDX-License-Identifier: GPL-3.0-or-later

"""The catalog's default exterior glazing: the room behind the pane.

Shared by every asset, so windows match across the catalog. An atlas paints
its glass id as usual and then calls rooms() on the finished albedo:

    import glazing
    rgb = glazing.rooms(c.mid == ID_GLASS, rgb)

Why this and not a flat fill. Seen from outside in daylight a window is mostly
the unlit room behind it, which is dark; the bright part is a specular
reflection of the sky. In a metallic/roughness renderer that reflection is
generated at shading time from roughness and the dielectric F0, so base colour
must not supply it as well. A near-white pane double-counts the sky: half of
everything reflected diffusely in all directions, plus a sharp highlight on
top, which is exactly how glossy white paint behaves. The reliable symptom is
a pane measuring brighter than the casing around it.

What it paints, per pane: one overall level, because rooms differ; a vertical
falloff, because a room is darker toward its floor and brighter where light
from the window catches the ceiling; a lit patch of far wall on rather more
than half of them; and a little pane-scale dirt. All of it is the room, not a
reflection, so it belongs in base colour -- unlike a fixed sill-to-head sky
gradient, which CLAUDE.md's Texture Requirements rule out.

By night the same panes are the lit room: night_rooms() multiplies each
pane of the emission mask by its own level, a soft lamp glow and a falloff
toward the floor, so a lit window reads as a room behind glass rather than a
flat panel. It stays neutral grey and every pane stays lit: which buildings
are lit, how brightly and in what colour is still the consumer's, and nothing
here says whether a room is occupied. Curtains and blinds were tried and read
as dark bars, not fabric, so there are none.

    emit = glazing.night_rooms(atlas.coverage(c, ID_GLASS) > 0, emit)

Panes are found from the glass mask itself, so an atlas needs to say nothing
about where its windows are. Lights separated by glazing bars thinner than
`merge` are treated as one window, which is what they are: bars divide a pane,
they do not divide the room.

numpy only -- this runs inside Blender as well as standalone.
"""

import numpy as np

# sRGB. The catalog default; CLAUDE.md's Style Direction owns the band.
BASE = (50, 54, 57)
WARM = (78, 70, 60)          # a far wall with daylight on it
ROUGHNESS = 0.08             # ORM green over glass; band is 0.05 - 0.12

LEVEL = (0.72, 1.34)         # room-to-room variation
FALLOFF = (0.80, 1.12)       # sill -> head, within one room
LIT_WALL_CHANCE = 0.55
GRAIN = 0.05

# night_rooms(): multipliers on the emission mask, per pane
NIGHT_LEVEL = (0.62, 1.0)    # room-to-room brightness
NIGHT_FLOOR = 0.78           # light at the sill, relative to the head
LAMP_GAIN = 0.45             # how much brighter the lamp's glow is
NIGHT_MIN = 0.22             # no pane reads as switched off


# ------------------------------------------------------------------ labelling
def _runs(row):
    d = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


def _dilate(mask, n):
    """Square dilation by n, so glazing bars do not split one window."""
    out = mask
    for _ in range(n):
        m = out.copy()
        m[1:, :] |= out[:-1, :]
        m[:-1, :] |= out[1:, :]
        m[:, 1:] |= out[:, :-1]
        m[:, :-1] |= out[:, 1:]
        out = m
    return out


def components(mask):
    """Connected components as (y0, y1, x0, x1) boxes. Run-length union-find:
    exact, and fast enough to run per variant inside Blender."""
    parent = []

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    runs, prev = [], []
    for y in range(mask.shape[0]):
        row = mask[y]
        if not row.any():
            prev = []
            continue
        cur = []
        for s, e in _runs(row):
            i = len(parent)
            parent.append(i)
            cur.append((s, e, i))
            runs.append((y, s, e, i))
            for ps, pe, pi in prev:
                if ps < e and s < pe:
                    union(i, pi)
        prev = cur

    boxes = {}
    for y, s, e, i in runs:
        r = find(i)
        if r in boxes:
            b = boxes[r]
            boxes[r] = (min(b[0], y), max(b[1], y + 1),
                        min(b[2], s), max(b[3], e))
        else:
            boxes[r] = (y, y + 1, s, e)
    return sorted(boxes.values())


def _seed(box):
    y0, y1, x0, x1 = box
    v = ((x0 * 73856093) ^ (y0 * 19349663)
         ^ ((x1 - x0) * 83492791) ^ ((y1 - y0) * 2654435761))
    return int(v % 2147483647)


# ------------------------------------------------------------------- painting
def _grain(shape, rs, amp):
    """Bilinear-upsampled noise; numpy only, so no scipy inside Blender."""
    h, w = shape
    sh, sw = max(2, h // 12), max(2, w // 12)
    small = rs.normal(0.0, 1.0, (sh, sw)).astype(np.float32)
    yi = np.linspace(0.0, sh - 1.0, h)
    xi = np.linspace(0.0, sw - 1.0, w)
    y0 = np.floor(yi).astype(int)
    x0 = np.floor(xi).astype(int)
    y1 = np.minimum(y0 + 1, sh - 1)
    x1 = np.minimum(x0 + 1, sw - 1)
    fy = (yi - y0)[:, None].astype(np.float32)
    fx = (xi - x0)[None, :].astype(np.float32)
    top = small[y0][:, x0] * (1 - fx) + small[y0][:, x1] * fx
    bot = small[y1][:, x0] * (1 - fx) + small[y1][:, x1] * fx
    return 1.0 + amp * np.clip(top * (1 - fy) + bot * fy, -2.5, 2.5)


def pane(h, w, rs, base=BASE):
    """One pane, h x w pixels, row 0 at the sill and row h-1 at the head."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = yy / max(1.0, h - 1.0)
    u = xx / max(1.0, w - 1.0)

    lvl = rs.uniform(*LEVEL)
    rgb = (np.asarray(base, np.float32)
           * (FALLOFF[0] + (FALLOFF[1] - FALLOFF[0]) * t)[..., None] * lvl)
    if rs.rand() < LIT_WALL_CHANCE:
        a0, a1 = sorted(rs.uniform(0.05, 0.95, 2))
        band = (np.clip((t - 0.42) / 0.30, 0, 1)
                * ((u > a0) & (u < min(a1, a0 + 0.55))))[..., None] * 0.6
        rgb = rgb * (1.0 - band) + np.asarray(WARM, np.float32) * band
    return rgb * _grain((h, w), rs, GRAIN)[..., None]


def rooms(mask, rgb, base=BASE, merge=3):
    """Repaint every pane of `mask` in `rgb` (H, W, 3 float, sRGB 0-255).

    The atlas keeps ownership of everything else: the sash, the casing, the
    reveal and the AO are untouched, and the emission mask is unaffected
    because the glass ids do not move.
    """
    if not mask.any():
        return rgb
    for box in components(_dilate(mask, merge)):
        y0, y1, x0, x1 = box
        sub = mask[y0:y1, x0:x1]
        if not sub.any():
            continue
        tile = pane(y1 - y0, x1 - x0, np.random.RandomState(_seed(box)), base)
        rgb[y0:y1, x0:x1][sub] = tile[sub]
    return rgb


def night_pane(h, w, rs):
    """h x w emission multipliers for one pane, row 0 at the sill."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = yy / max(1.0, h - 1.0)
    u = xx / max(1.0, w - 1.0)
    level = rs.uniform(*NIGHT_LEVEL)
    # a lamp somewhere in the room, seen through the glass as a soft glow
    lu, lt = rs.uniform(0.2, 0.8), rs.uniform(0.3, 0.75)
    r = rs.uniform(0.28, 0.5)
    aspect = w / max(1.0, float(h))
    lamp = np.exp(-(((u - lu) * aspect) ** 2 + (t - lt) ** 2) / (2 * r * r))
    # A pane much wider than it is tall -- a shopfront, a curtain wall, whose
    # thin mullions the merge bridges -- is a row of bays, each with its own
    # light; one glow for the lot left most of it in the falloff. Extra lamps
    # are drawn only after the first, so ordinary panes are unchanged.
    bays = int(round(aspect))
    if bays > 1:
        for k in range(bays):
            bu = (k + rs.uniform(0.3, 0.7)) / bays
            bt = rs.uniform(0.3, 0.75)
            lamp = np.maximum(lamp, np.exp(-(((u - bu) * aspect) ** 2 + (t - bt) ** 2)
                                           / (2 * r * r)))
    light = (level * (NIGHT_FLOOR + (1.0 - NIGHT_FLOOR) * t)
             * (1.0 - LAMP_GAIN + LAMP_GAIN * lamp))
    return np.clip(light, NIGHT_MIN, 1.0)


def night_rooms(mask, emission, merge=3):
    """Multiply every pane of `mask` in `emission` (H, W, 3, 0-255) by its room.

    `mask` is the glass the pane covers, including partly covered edge pixels,
    in the same V-up orientation as the atlas. Other luminous regions (a sign,
    a clock face) are left as they are, because they are not in the mask.
    Seeded from each pane's box like rooms(), but on a different stream, so a
    pane's night does not follow from its day.
    """
    emission = np.asarray(emission, np.float32).copy()
    if not mask.any():
        return emission
    for box in components(_dilate(mask, merge)):
        y0, y1, x0, x1 = box
        sub = mask[y0:y1, x0:x1]
        if not sub.any():
            continue
        rs = np.random.RandomState((_seed(box) ^ 0x5BD1E995) % 2147483647)
        pat = night_pane(y1 - y0, x1 - x0, rs)
        region = emission[y0:y1, x0:x1]
        region[sub] *= pat[sub][:, None]
    return emission


def mean_linear(mask, rgb):
    """Mean linear reflectance over the glass, for checks and notes."""
    v = np.asarray(rgb, np.float32)[mask].mean() / 255.0
    return float(v ** 2.2)
