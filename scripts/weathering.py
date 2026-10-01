# SPDX-License-Identifier: GPL-2.0-only

"""Weathering for any atlas: dirt, algae, rust, faded paint and rain runs, as
per-sample fields that scripts/atlas.py resolves per variant.

An asset's facade_atlas.py says where the weather goes, because only it knows
its layout; this module owns what each kind of weather looks like, so a
plinth or a sill weathers the same way across the catalog. The fields are
amounts, not colours, and are resolved against each variant's own palette:

    D  dirt   lerp toward soil, a warm grey-brown; on steel ids toward a
              neutral dust, as soil's brown turns a dark roof orange
    G  algae  lerp toward the dark green-grey film at the foot of a plinth
    R  rust   lerp toward a dulled iron oxide
    F  fade   lerp toward the surface's own chalky grey: paint chalking, and
              on brick the pale bloom of efflorescence
    W  wash   a shade offset: faint rain runs down a wall

Dirt, algae and rust roughen the ORM and strip the metallic; fade roughens a
little. None of them touches height or the normal map, and clean ids (glass)
never weather: glazing.rooms() owns every pane.

The tiling bands map height (a wall band) or slope (a roof band) to V and wrap
in U. Weather that follows height -- ground splash, a sheltered eave, dirt
toward the gutter -- is exact on every wall that samples a band whose V is
height from the ground. A band sampled from each storey's own foot, or one
that wraps in V, would repeat it up the wall, so there only noise goes, on
the band's period (tile_y). Everything else is periodic noise, so the bands
still wrap. What follows one window or one corner on the facade cannot live
in a shared band; it stays inside the openings' own regions.

    import weathering
    w = weathering.Weather(c, clean=(ID_GLASS,), steel=(ID_ROOF, ID_METAL))
    w.grime()
    w.plinth(0, ATLAS, S1_Y0, S1_Y0 + m(Z_FLOOR), (ID_PLINTH,))
    ...
    c.pad()                          # carries the fields with the channels
    cav = atlas.cavity(c, ...)
    w.dust(cav, (ID_WALL,))          # after pad(): cavity needs the padding
    atlas.albedo(c, lut, grime)      # applies c.weather; so does atlas.orm()

Amounts are the catalog's "moderate" level, chosen on rintamamiestalo_porch
against a stronger level that read as neglect (CLAUDE.md, Style Direction:
believable wear, nothing that suggests abandonment).
"""

import numpy as np

import atlas

DIRT = (98, 88, 74)        # sRGB: road dust and soil
STEEL_DIRT = (86, 84, 78)  # dust on sheet steel and felt
ALGAE = (70, 78, 60)
RUST = (100, 60, 40)
FIELDS = "DGRFW"

# name -> (seed, sigma x, sigma y, kind); see noise()
NOISE = {
    "blotch": (101, 24.0, 24.0, "unit"),   # ~0.4 m patches
    "big": (102, 60.0, 60.0, "unit"),      # ~1 m patches
    "speck": (103, 1.2, 1.2, "speck"),     # sparse ~2 cm specks
    "runs": (104, 0.8, 30.0, "raw"),       # thin runs, ~0.5 m long
    "long": (105, 1.0, 80.0, "raw"),       # long runs down a roof
    "short": (106, 0.6, 8.0, "raw"),       # short runs on a sill
    "wash": (107, 1.5, 40.0, "raw"),
    "bloom": (108, 10.0, 10.0, "raw"),
}


class Weather:
    def __init__(self, c, clean=(), steel=(), tile_y=1):
        """Attach empty fields to canvas *c*: c.pad() carries them and
        atlas.albedo()/orm() resolve them. tile_y > 1 makes every noise
        repeat that many times up the canvas, for an atlas with a band that
        wraps in V (atlas.noise)."""
        n = c.size * c.ss
        self.c = c
        self.tile_y = tile_y
        self.clean, self.steel = tuple(clean), tuple(steel)
        self.f = {k: np.zeros((n, n), np.float32) for k in FIELDS}
        self._noise = {}
        c.weather = self

    # ------------------------------------------------------------ plumbing
    def noise(self, name):
        """A named field over the whole canvas, made once. "unit" is mapped
        to 0..1, "speck" to sparse specks, "raw" left at unit variance."""
        if name not in self._noise:
            seed, sx, sy, kind = NOISE[name]
            n = atlas.noise(self.c, seed, sx, sy, tile_y=self.tile_y)
            if kind == "unit":
                n = atlas.smoothstep(-1.5, 1.5, n)
            elif kind == "speck":
                n = atlas.smoothstep(1.3, 2.2, n)
            self._noise[name] = n.astype(np.float32)
        return self._noise[name]

    def add(self, field, x0, x1, y0, y1, value, ids=None):
        """Add *value* to one field over a rect, on *ids* only if given.

        value is a number or value(Y, X, nz): Y and X are the samples' pixel
        coordinates and nz(name) the named noise over the same samples.
        """
        sy, sx, Y, X = self.c.field(x0, x1, y0, y1)
        if Y.size == 0:
            return
        if callable(value):
            value = value(Y, X, lambda name: self.noise(name)[sy, sx])
        v = np.broadcast_to(np.asarray(value, np.float32), Y.shape)
        if ids is not None:
            v = np.where(np.isin(self.c.mid[sy, sx], ids), v, 0.0)
        self.f[field][sy, sx] += v

    def carry(self, iy, ix):
        """Canvas.pad()'s nearest-sample fill, applied to every field."""
        for k in FIELDS:
            self.f[k][...] = self.f[k][iy, ix]
        self._noise.clear()

    # -------------------------------------------------------- the weather
    def grime(self, amount=0.035):
        """A light, patchy film of dirt over everything."""
        n = self.c.size
        self.add("D", 0, n, 0, n, lambda Y, X, nz: amount * nz("blotch"))

    def fade(self, ids, amount=0.10, base=0.03):
        """Paint chalking toward its own grey, in broad patches."""
        n = self.c.size
        self.add("F", 0, n, 0, n, lambda Y, X, nz: base + amount * nz("big"), ids)

    def wash(self, ids, amount=0.012):
        """Faint vertical rain runs down a wall."""
        n = self.c.size
        self.add("W", 0, n, 0, n, lambda Y, X, nz: amount * nz("wash"), ids)

    def plinth(self, x0, x1, y_ground, y_top, ids, ppm=None):
        """A masonry base from ground row *y_ground* up to *y_top*: soil and
        splash specks at its foot, a green film under them, and runs where
        the water leaves the drip edge above it."""
        p = ppm or self.c.ppm
        ztop = (y_top - y_ground) / p

        def soil(Y, X, nz):
            z = np.clip((Y - y_ground) / p, 0.0, None)
            return (0.30 * np.exp(-z / 0.12) * (0.7 + 0.3 * nz("blotch"))
                    + 0.25 * nz("speck") * np.exp(-z / 0.20)
                    + 0.25 * atlas.smoothstep(0.3, 1.5, nz("runs"))
                    * np.exp(-np.clip(ztop - z, 0.0, None) / 0.25))
        self.add("D", x0, x1, y_ground - 2, y_top, soil, ids)
        self.add("G", x0, x1, y_ground - 2, y_top, lambda Y, X, nz: 0.20 * np.exp(
            -np.clip((Y - y_ground) / p, 0.0, None) / 0.10) * nz("blotch"), ids)

    def splash(self, x0, x1, y_foot, y1, ids, amount=0.22, fall=0.18,
               specks=0.20, speck_fall=0.30, ppm=None):
        """Rain splash-back on a wall above row *y_foot*: dirt fading upward
        over *fall* metres, with specks thrown a little higher."""
        p = ppm or self.c.ppm

        def f(Y, X, nz):
            z = np.clip((Y - y_foot) / p, 0.0, None)
            return (amount * np.exp(-z / fall) * (0.6 + 0.4 * nz("blotch"))
                    + specks * nz("speck") * np.exp(-z / speck_fall))
        self.add("D", x0, x1, y_foot, y1, f, ids)

    def shelter(self, x0, x1, y0, y1, ids, amount=0.10, top=None):
        """Dust gathering from row *y0* up to row *y1*, under a soffit or a
        band board where no rain washes it off; at full strength from y1 up
        to *top*, when the band runs on above the eave."""
        self.add("D", x0, x1, y0, max(y1, top or y1), lambda Y, X, nz: amount
                 * atlas.smoothstep(y0, y1, Y) * (0.6 + 0.4 * nz("blotch")), ids)

    def runs(self, x0, x1, y0, y1, ids, amount, fall, noise="runs", lo=0.3, hi=1.5):
        """Dirty runs hanging from the rect's top edge, fading downward over
        *fall* pixels: under a cap, a gutter or a drip edge."""
        self.add("D", x0, x1, y0, y1, lambda Y, X, nz: amount * atlas.smoothstep(
            lo, hi, nz(noise)) * np.exp(-(y1 - Y) / fall), ids)

    def roof(self, x0, x1, y0, h, slope_len, ids):
        """A roof band, V from the eave (row y0) up *h* rows over *slope_len*
        metres: long runs down the slope, more dirt toward the eave, the paint
        chalking toward the ridge where the sun has it longest."""
        rpm = h / slope_len

        def dirt(Y, X, nz):
            s = np.clip((Y - y0) / rpm, 0.0, None)
            return (0.14 * atlas.smoothstep(0.0, 1.5, nz("long"))
                    * (0.4 + 0.6 * np.clip(1.0 - s / slope_len, 0.0, 1.0))
                    + 0.15 * np.exp(-s / 0.30))

        def chalk(Y, X, nz):
            s = (Y - y0) / rpm
            return 0.04 * nz("big") + 0.10 * atlas.smoothstep(
                0.24 * slope_len, 0.95 * slope_len, s)
        self.add("D", x0, x1, y0 - 2, y0 + h + 2, dirt, ids)
        self.add("F", x0, x1, y0 - 2, y0 + h + 2, chalk, ids)

    def bloom(self, x0, x1, y0, y1, ids, amount=0.18, fade=None):
        """Efflorescence: pale salt bloom on masonry, patchy, and fading out
        over the top *fade* pixels of the rect when given, as it rises from
        the damp foot of a wall or a stack."""
        def f(Y, X, nz):
            v = amount * atlas.smoothstep(0.5, 1.6, nz("bloom"))
            return v if fade is None else v * atlas.smoothstep(y1, y1 - fade, Y)
        self.add("F", x0, x1, y0, y1, f, ids)

    def spot(self, cx, cy, r, ids, amount=0.22):
        """A soft patch of hand grime, radius *r* pixels: round a handle."""
        self.add("D", cx - 3 * r, cx + 3 * r, cy - 3 * r, cy + 3 * r,
                 lambda Y, X, nz: amount * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / r ** 2),
                 ids)

    def window(self, x0, y0, rw, rh, oy0, oy1, frame, trim, sash, sill=True):
        """One window's region, casing origin (x0, y0) and size rw x rh, the
        opening from row oy0 to oy1: dirt and short runs on the sill, runs down
        the head casing from under the drip cap, water standing on the sash's
        bottom rail."""
        if sill:
            self.add("D", x0 - 2, x0 + rw + 2, y0 - 2, oy0, lambda Y, X, nz: 0.10
                     + 0.14 * atlas.smoothstep(0.2, 1.4, nz("short")), trim)
        top = y0 + rh - 4
        if top > oy1:
            self.add("D", x0 - 2, x0 + rw + 2, oy1, top, lambda Y, X, nz: 0.12
                     * atlas.smoothstep(0.3, 1.5, nz("runs"))
                     * np.clip((Y - oy1) / (top - oy1), 0.0, 1.0), trim)
        self.add("D", x0, x0 + rw, oy0, oy0 + frame, 0.12, sash)

    def door(self, ox0, ox1, oy0, oy1, ids, handle=None, ppm=None):
        """A door leaf: grime round the handle at (x, y), and kicked-up dirt
        across its foot."""
        p = ppm or self.c.ppm
        if handle is not None:
            self.spot(handle[0], handle[1], 0.08 * p, ids)
        self.splash(ox0, ox1, oy0, oy1, ids, amount=0.18, fall=0.15, specks=0.0, ppm=p)

    def dust(self, cav, ids, amount=0.18):
        """Dust settled in the cavities (under laps, in joints). Call after
        c.pad(), with the cavity() the export computes."""
        self.f["D"] += amount * cav * np.isin(self.c.mid, ids)

    # ---------------------------------------------------------- resolving
    def _field(self, k, hi=None):
        """A field ready to apply: clipped to 0 .. hi when given, and zero on
        the clean ids."""
        a = self.f[k].copy() if hi is None else np.clip(self.f[k], 0.0, hi)
        if self.clean:
            a[np.isin(self.c.mid, self.clean)] = 0.0
        return a

    def albedo(self, base, shade):
        """Weather linear base colours (samples x 3) in place; return the
        weathered shade. Called by atlas.albedo()."""
        c = self.c
        lum = base @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        chalk = np.minimum(lum * 1.12, 0.85)[..., None]
        base += (chalk - base) * self._field("F", 0.5)[..., None]
        dirt = np.tile(atlas.srgb_to_linear(DIRT), (256, 1)).astype(np.float32)
        if self.steel:
            dirt[list(self.steel)] = atlas.srgb_to_linear(STEEL_DIRT)
        base += (dirt[c.mid] - base) * self._field("D", 0.8)[..., None]
        for k, col in (("G", ALGAE), ("R", RUST)):
            lin = atlas.srgb_to_linear(col).astype(np.float32)
            base += (lin - base) * self._field(k, 0.8)[..., None]
        return shade * (1.0 + self._field("W"))

    def orm(self, rough, metal):
        """Weathered (roughness, metallic) samples. Called by atlas.orm()."""
        D, G, R, F = (self._field(k, 1.0) for k in "DGRF")
        rough = rough + 0.20 * D + 0.20 * G + 0.25 * R + 0.10 * F
        metal = metal * (1.0 - np.clip(D + R, 0.0, 1.0))
        return rough, metal
