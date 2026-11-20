# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared trim-sheet rasteriser: a supersampled canvas with a height channel,
and the maps it resolves to (albedo, ORM, normal, emission coverage).

An asset's facade_atlas.py keeps its own layout, palette and artwork; this
module owns how any atlas is rasterised, so every asset gets the same
anti-aliasing, the same normal-map convention and the same cavity shading.

Coordinates are atlas pixels at the final resolution, as floats, with V up
(row 0 at the bottom) and pixel i covering [i, i + 1). The canvas stores SS
samples per pixel along each axis and resolve() box-filters them back down, so
an edge at 60.8 px lands 80 % of the way across its pixel instead of snapping
to 61, and anything drawn per sample is anti-aliased for free.

Four channels are painted, all at sample resolution:

    mid     material id (uint8); a variant's lookup table colours it
    shade   albedo multiplier: tone, wear and occlusion darkening, never
            directional light -- relief that should answer the sun goes in
            height instead (CLAUDE.md, Texture Requirements)
    ao      ambient occlusion, ORM red
    height  surface relief in metres, relative to the face the region maps
            onto. Only micro-relief: a recess the mesh already models is not
            repeated here

Importing needs numpy alone, so build.py can import an atlas's layout inside a
Blender whose Python has no scipy; scipy is imported by the functions that
resolve maps, which run in the standalone texture export.

    import atlas
    c = atlas.Canvas(size=1024, ss=4, ppm=64.0)
    c.paint(x0, x1, y0, y1, mid=ID_TRIM, height=0.02)
    ...                                         # every region
    w = weathering.Weather(c, clean=(ID_GLASS,))  # then weathering (optional)
    ...
    c.pad()                                     # fill the gaps between regions
    rgb = atlas.albedo(c, lut)                  # sRGB floats, 0-255
                                                # (weathered, if c.weather is set)
    rgb = glazing.rooms(atlas.coverage(c, ID_GLASS) >= 0.5, rgb)
    atlas.save(atlas.to_u8(rgb), path)
"""

import numpy as np

SS = 4               # samples per pixel per axis: the catalog default
UNPAINTED = 255      # material id of samples no region has claimed; pad() fills them


# ================================================================== canvas
class Canvas:
    def __init__(self, size=1024, ss=SS, ppm=64.0):
        self.size, self.ss, self.ppm = size, ss, float(ppm)
        n = size * ss
        self.mid = np.full((n, n), UNPAINTED, np.uint8)
        self.shade = np.ones((n, n), np.float32)
        self.ao = np.ones((n, n), np.float32)
        self.height = np.zeros((n, n), np.float32)
        self.padded = np.zeros((n, n), bool)     # set by pad()
        self.weather = None                      # a weathering.Weather sets itself here

    # ---------------------------------------------------------- addressing
    def _idx(self, a):
        """Pixel coordinate -> index of the first sample whose centre is >= a."""
        n = self.size * self.ss
        return min(max(int(np.ceil(a * self.ss - 0.5)), 0), n)

    def sl(self, x0, x1, y0, y1):
        """Samples whose centres fall in [x0, x1) x [y0, y1), as (rows, cols)."""
        a0, a1 = self._idx(x0), self._idx(x1)
        b0, b1 = self._idx(y0), self._idx(y1)
        return slice(b0, max(b0, b1)), slice(a0, max(a0, a1))

    def coords(self, sy, sx):
        """Pixel coordinates of the sample centres in a slice, as (Y, X) grids.

        At ss = 1 these are i + 0.5, so floor() gives back the pixel index an
        unsupersampled atlas would have used.
        """
        s = self.ss
        ys = ((np.arange(sy.start, sy.stop) + 0.5) / s).astype(np.float32)
        xs = ((np.arange(sx.start, sx.stop) + 0.5) / s).astype(np.float32)
        return np.meshgrid(ys, xs, indexing="ij")

    def field(self, x0, x1, y0, y1):
        """(rows, cols, Y, X) for per-sample expressions over a rect."""
        sy, sx = self.sl(x0, x1, y0, y1)
        Y, X = self.coords(sy, sx)
        return sy, sx, Y, X

    # ------------------------------------------------------------ painting
    def paint(self, x0, x1, y0, y1, mid=None, shade=None, ao=None, height=None):
        """Set any of the four channels over a rect."""
        sy, sx = self.sl(x0, x1, y0, y1)
        if mid is not None:
            self.mid[sy, sx] = mid
        if shade is not None:
            self.shade[sy, sx] = shade
        if ao is not None:
            self.ao[sy, sx] = ao
        if height is not None:
            self.height[sy, sx] = height

    def mul(self, x0, x1, y0, y1, f, ao=None):
        """Darken (or tint) shade over a rect; AO only ever goes down."""
        sy, sx = self.sl(x0, x1, y0, y1)
        self.shade[sy, sx] *= f
        if ao is not None:
            self.ao[sy, sx] = np.minimum(self.ao[sy, sx], ao)

    def lift(self, x0, x1, y0, y1, dh):
        """Add dh metres of height over a rect (negative for a groove)."""
        sy, sx = self.sl(x0, x1, y0, y1)
        self.height[sy, sx] += dh

    def bevel(self, x0, x1, y0, y1, h, w, base=0.0, axes="xy"):
        """A raised board: height h over the rect, ramping up from base over
        w px at its edges, so the arrises catch light instead of
        stair-stepping. axes="y" bevels only the top and bottom edges, for a
        board that runs the full width of a band that wraps in U."""
        sy, sx, Y, X = self.field(x0, x1, y0, y1)
        d = np.full(Y.shape, np.inf, np.float32)
        if "x" in axes:
            d = np.minimum(d, np.minimum(X - x0, x1 - X))
        if "y" in axes:
            d = np.minimum(d, np.minimum(Y - y0, y1 - Y))
        self.height[sy, sx] = base + (h - base) * np.clip(d / max(w, 1e-6), 0.0, 1.0)

    def pad(self):
        """Fill every unpainted sample from the nearest painted one.

        Each region's own edge is extended outward across all the empty atlas
        space around it, in every channel, so the maps derived from them agree
        and a mip level's wider footprint at a region's edge finds more of that
        region instead of background. The border between two regions falls
        halfway across the gap. Call it last, after weathering. The filled
        samples are remembered, and normal_map() keeps them flat: two
        neighbours' edge heights meeting at the midline would otherwise draw a
        crease there. Weathering fields are filled the same way.
        """
        from scipy.ndimage import distance_transform_edt
        empty = self.mid == UNPAINTED
        self.padded = empty
        if not empty.any():
            return
        iy, ix = distance_transform_edt(empty, return_distances=False,
                                        return_indices=True)
        for a in (self.mid, self.shade, self.ao, self.height):
            a[...] = a[iy, ix]
        if self.weather is not None:
            self.weather.carry(iy, ix)

    # -------------------------------------------------------------- shapes
    # Evaluated per sample, so their edges come out anti-aliased by the box
    # filter; nothing here computes coverage by hand. AO only ever goes down.
    def shape(self, x0, x1, y0, y1, test, mid=None, shade=None, ao=None,
              height=None):
        """Any shape: *test(X, Y)* says which samples in the bounding rect are
        inside it."""
        sy, sx, Y, X = self.field(x0, x1, y0, y1)
        if Y.size == 0:
            return
        hit = test(X, Y)
        if mid is not None:
            self.mid[sy, sx][hit] = mid
        if shade is not None:
            self.shade[sy, sx][hit] = shade
        if ao is not None:
            self.ao[sy, sx][hit] = np.minimum(self.ao[sy, sx][hit], ao)
        if height is not None:
            self.height[sy, sx][hit] = height

    def stroke(self, p0, p1, w, mid=None, shade=None, ao=None, clip=None,
               height=None):
        """A line segment *w* pixels thick with round caps."""
        (ax, ay), (bx, by) = p0, p1
        x0, x1 = min(ax, bx) - w, max(ax, bx) + w
        y0, y1 = min(ay, by) - w, max(ay, by) + w
        if clip:
            cx, cy, cw, ch = clip
            x0, x1 = max(x0, cx), min(x1, cx + cw)
            y0, y1 = max(y0, cy), min(y1, cy + ch)
        dx, dy = bx - ax, by - ay
        ll = max(dx * dx + dy * dy, 1e-9)

        def test(X, Y):
            t = np.clip(((X - ax) * dx + (Y - ay) * dy) / ll, 0.0, 1.0)
            return np.hypot(X - (ax + t * dx), Y - (ay + t * dy)) <= w * 0.5
        self.shape(x0, x1, y0, y1, test, mid, shade, ao, height)

    def disc(self, cx, cy, r, mid=None, shade=None, ao=None, inner=0.0,
             height=None):
        """A filled circle, or a ring when *inner* > 0."""
        def test(X, Y):
            d = np.hypot(X - cx, Y - cy)
            return (d <= r) & (d >= inner)
        self.shape(cx - r - 1, cx + r + 1, cy - r - 1, cy + r + 1, test,
                    mid, shade, ao, height)

    def rounded_rect(self, x0, y0, w, h, r, mid=None, shade=None, ao=None,
                     height=None):
        """A rectangle with corners of radius *r*."""
        def test(X, Y):
            dx = np.clip(np.abs(X - (x0 + w / 2.0)) - (w / 2.0 - r), 0, None)
            dy = np.clip(np.abs(Y - (y0 + h / 2.0)) - (h / 2.0 - r), 0, None)
            return np.hypot(dx, dy) <= r
        self.shape(x0, x0 + w, y0, y0 + h, test, mid, shade, ao, height)

    def check_bands(self, bands):
        """Fail the bake if a tiling band holds an id it should not.

        bands: name -> ((row0, row1), allowed ids), rows in pixels. A stray
        sample in a tiling band repeats under every surface sampling it.
        """
        for name, ((r0, r1), ok) in bands.items():
            sy, _ = self.sl(0, 1, r0, r1)
            found = set(np.unique(self.mid[sy]).tolist())
            # unpainted samples are allowed: pad() fills them from the band's
            # own edge; only another region's id is a slip
            stray = found - set(ok) - {UNPAINTED}
            if stray:
                raise ValueError("%s band rows %d..%d contain ids %s"
                                 % (name, r0, r1, sorted(stray)))


# ================================================================== noise
def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def hash_int(*ints):
    """Integer hash, elementwise over numpy arrays or on plain ints."""
    h = np.int64(0x9E3779B1)
    for i in ints:
        h = (h ^ np.asarray(i, np.int64)) * np.int64(0x85EBCA6B) & np.int64(0x7FFFFFFF)
        h ^= h >> np.int64(13)
    return h


def hash_unit(*ints):
    """hash_int mapped to [0, 1)."""
    return (hash_int(*ints) % 100003) / 100003.0


def noise(c, seed, sx_px, sy_px=None, tile_y=1):
    """Smooth random field over the whole canvas, unit variance, zero mean.

    White noise blurred by a Gaussian of sx_px x sy_px (in pixels) through the
    FFT, so it is periodic: it tiles exactly in both axes, and a band that
    wraps in U stays seamless. Unequal sigmas give streaks: a large sx_px runs
    them along U (wood grain), a large sy_px along V (rain streaks). tile_y > 1
    repeats the field that many times up the canvas, for a band that also
    wraps in V with a period of size / tile_y rows.
    """
    sy_px = sx_px if sy_px is None else sy_px
    n = c.size * c.ss
    rows = n // tile_y
    rs = np.random.RandomState(seed)
    white = rs.standard_normal((rows, n)).astype(np.float32)
    fy = np.fft.fftfreq(rows)[:, None]
    fx = np.fft.rfftfreq(n)[None, :]
    sx_s, sy_s = sx_px * c.ss, sy_px * c.ss
    g = np.exp(-2.0 * np.pi ** 2 * ((fx * sx_s) ** 2 + (fy * sy_s) ** 2))
    out = np.fft.irfft2(np.fft.rfft2(white) * g, s=(rows, n)).astype(np.float32)
    out -= out.mean()
    out /= max(float(out.std()), 1e-12)
    return np.tile(out, (tile_y, 1)) if tile_y > 1 else out


# =============================================================== resolving
def box(a, ss):
    """Mean over each ss x ss block: samples back to pixels."""
    if ss == 1:
        return a.astype(np.float32)
    h, w = a.shape[:2]
    rest = a.shape[2:]
    return a.reshape(h // ss, ss, w // ss, ss, *rest).mean(axis=(1, 3)).astype(np.float32)


def srgb_to_linear(v):
    v = np.asarray(v, np.float32) / 255.0
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(v):
    v = np.clip(v, 0.0, 1.0)
    return 255.0 * np.where(v <= 0.0031308, v * 12.92, 1.055 * v ** (1 / 2.4) - 0.055)


def lookup(c, table, default=0.0):
    """Per-sample value from an id -> value dict (scalars or tuples)."""
    first = next(iter(table.values()))
    depth = np.shape(first)
    lut = np.full((256,) + depth, default, np.float32)
    for i, v in table.items():
        lut[i] = v
    return lut[c.mid]


def coverage(c, ids):
    """Fraction of each pixel covered by the given id(s)."""
    return box(np.isin(c.mid, np.atleast_1d(ids)).astype(np.float32), c.ss)


def cavity(c, radius_px=2.0, depth_m=0.01):
    """How far each sample sits below its surroundings, 0 (flat) .. 1 (deep).

    Height minus its Gaussian blur, over depth_m: grooves, laps and joints
    read as cavities, raised boards as not. Wraps in U like the bands.
    Only relief within a region counts, so paint each region's bleed at its
    own edge height or the region border reads as a groove.
    """
    from scipy.ndimage import gaussian_filter
    sigma = radius_px * c.ss
    blur = gaussian_filter(c.height, sigma=sigma, mode=("nearest", "wrap"))
    return np.clip((blur - c.height) / depth_m, 0.0, 1.0)


def albedo(c, lut, grime=None):
    """Colour the ids, apply shade, and box-filter in linear light.

    lut: 256 x 3 sRGB table. grime: optional per-sample 0..1 darkening, e.g.
    from cavity(). The canvas's weathering, if any, is applied to the colours
    first (scripts/weathering.py). Returns sRGB floats 0-255 at pixel
    resolution, ready for glazing.rooms() and to_u8().
    """
    base = srgb_to_linear(lut).astype(np.float32)[c.mid]
    shade = c.shade
    if c.weather is not None:
        shade = c.weather.albedo(base, shade)
    if grime is not None:
        shade = shade * (1.0 - grime)
    return linear_to_srgb(box(base * shade[..., None], c.ss))


def orm(c, surface, rough_var=None, cavity_ao=None):
    """ORM at pixel resolution from an id -> (roughness, metallic) table.

    rough_var: optional per-sample roughness offset (e.g. 0.04 * noise(...)).
    cavity_ao: optional per-sample 0..1 cavity, deepened into the AO.
    The canvas's weathering, if any, roughens dirt and strips its metallic.
    """
    rough = lookup(c, {i: r for i, (r, _) in surface.items()})
    metal = lookup(c, {i: m for i, (_, m) in surface.items()})
    if rough_var is not None:
        rough = rough + rough_var
    if c.weather is not None:
        rough, metal = c.weather.orm(rough, metal)
    ao = c.ao if cavity_ao is None else c.ao * (1.0 - cavity_ao)
    out = np.stack([box(np.clip(ao, 0, 1), c.ss),
                    box(np.clip(rough, 0.04, 1), c.ss),
                    box(np.clip(metal, 0, 1), c.ss)], axis=-1)
    return out * 255.0


def normal_map(c, flat_ids=(), soften_px=0.35, strength=1.0):
    """Tangent-space normals from the height channel, OpenGL convention.

    +X follows U and +Y follows V (green up), as glTF and Blender's Normal
    Map node expect. Slopes come from height in metres over sample spacing in
    metres, so relief keeps its physical proportions at any SS. soften_px
    rounds arrises slightly (real boards are not knife-edged) and keeps steps
    from aliasing. Normals are averaged per pixel and renormalised, so a
    one-pixel lap still tilts its pixel. flat_ids (glass) stay flat, and so
    does the padding between regions.
    """
    from scipy.ndimage import gaussian_filter
    h = c.height
    if soften_px > 0:
        h = gaussian_filter(h, sigma=soften_px * c.ss, mode=("nearest", "wrap"))
    step = 1.0 / (c.ppm * c.ss)                       # metres per sample
    dx = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) / (2.0 * step)   # U wraps
    dy = np.empty_like(h)
    dy[1:-1] = (h[2:] - h[:-2]) / (2.0 * step)
    dy[0], dy[-1] = dy[1], dy[-2]
    n = np.stack([-dx * strength, -dy * strength, np.ones_like(h)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    flat = c.padded.copy()
    if len(flat_ids):
        flat |= np.isin(c.mid, flat_ids)
    n[flat] = (0.0, 0.0, 1.0)
    n = box(n, c.ss)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
    return (n * 0.5 + 0.5) * 255.0


def emission(c, ids):
    """Neutral candidate-glazing mask: coverage as grey, nothing else."""
    return np.repeat(coverage(c, ids)[..., None] * 255.0, 3, axis=-1)


def emission_colours(c, table):
    """An emission map from an id -> sRGB table (glazing white, a sign in its
    own colours), box-filtered in linear light; ids not listed are black."""
    lut = np.zeros((256, 3), np.float32)
    for i, col in table.items():
        lut[i] = col
    return linear_to_srgb(box(srgb_to_linear(lut).astype(np.float32)[c.mid], c.ss))


def to_u8(a):
    return np.clip(np.round(a), 0, 255).astype(np.uint8)


def save(arr, path):
    """Write an RGB atlas authored with V = 0 at the bottom (PNG rows run
    top-down, so it is flipped on the way out)."""
    from PIL import Image
    Image.fromarray(np.flipud(to_u8(arr)), mode="RGB").save(path, optimize=True)
    return path
