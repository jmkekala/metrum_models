# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas for rintamamiestalo_side_entry, and the
layout build.py maps into.

This describes one asset and nothing else, so it lives beside build.py rather
than in scripts/. It started as a copy of rintamamiestalo_porch's atlas, and is
kept as a copy rather than shared: the two houses are meant to be free to
diverge, and a shared atlas would repaint one whenever the other changed. It is also the single source of the numbers the two files
share: build.py imports the z-levels, opening sizes and region rects from here
instead of writing them a second time, so the pixel layout and the UVs cannot
drift apart. Importing this module only defines those constants; the painting
runs when paint() is called. Rasterising is scripts/atlas.py's: a canvas
supersampled SS x SS per pixel, with a height channel the normal map is
derived from (numpy and scipy; Pillow to save).

    python3 facade_atlas.py export      # writes every map into ./export

The atlas is a trim sheet rather than one picture per elevation. A house's
elevations are all different, and painting each one at the catalog's 64 px/m
does not fit in 1024², so the walls sample tiling bands and every opening
samples a region of its own:

    y    0 ..  286   S1      lower walls, z 0 .. 4.40: plinth, flashing, siding
    y  288 ..  561   S2      gable triangles, z 4.30 .. 8.50: belt board, siding
    y  563 ..  823   ROOF    standing-seam roof, V stretched up the slope
    y  825 ..  849   FASCIA  eave fascia with its gutter
    y  852 .. 1000   unique  doors, windows, cellar lights, vent, chimney,
                             corner-board strip, flat patches

S1, S2, ROOF and FASCIA span the full width and tile in U. Every opening's
region carries its casing as well as its glazing, because the casing is the
one part of a window a tiling siding band cannot place. build.py cuts a ring of
faces round each opening for it to land on.

Painting produces a material-id map, a shade multiplier, an AO map and a
height map once; each variant is those coloured by its own palette, so the
variants cannot differ in anything but colour. Relief that should answer the
sun (siding laps, standing seams, the gutter's roll, raised casings) is height,
and reaches the renderer through the normal map; shade only carries tone, wear
and the occlusion in laps and joints, which does not depend on where the sun
is. Dirt, algae, rust and faded paint are scripts/weathering.py's fields:
weather() below says where they go on this layout, and each variant resolves
them against its own colours.
"""

import os
import sys

import numpy as np

# Windows are painted the same way across the whole catalog, and every atlas is
# rasterised the same way, so both live in scripts/ and not here; see
# CLAUDE.md's Style Direction and Texture Requirements.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import atlas  # noqa: E402
import brickwork  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ASSET = "rintamamiestalo_side_entry"
ATLAS = 1024
PPM = 64.0

# --------------------------------------------------------- vertical layout
# Metres above ground, shared by every wall so storey lines agree all round.
Z_FLOOR = 0.70       # plinth top = ground-floor level; door thresholds
Z_FLASH = 0.75       # top of the plinth flashing; siding and corner boards
Z_EAVE = 4.30        # long walls meet the soffit; gable siding begins
Z_WALL_TOP = 4.40    # walls run on up into the roof slab, which trims them
BELT_H = 0.1875      # belt board across the foot of each gable (12 px)
BOARD = 0.125        # lap-siding pitch (8 px)
CW = 0.125           # corner-board width (8 px)
S2_TOP = 8.50        # gable band reaches this high; build.py asserts the apex fits

# ------------------------------------------------------------- openings
# kind -> (width, height, casing side, casing bottom, casing top), metres.
# Casing is painted, never modelled: at 20-40 mm proud it fails the 0.25 m
# test by an order of magnitude. Doors have no bottom casing — the leaf
# runs down to the threshold.
OPENINGS = {
    "door_front": (0.90, 2.10, 0.125, 0.0, 0.1875),
    "door_back": (0.90, 2.10, 0.125, 0.0, 0.1875),
    "wide": (1.80, 1.40, 0.125, 0.125, 0.1875),
    "std": (1.20, 1.40, 0.125, 0.125, 0.1875),
    "porch": (0.60, 0.80, 0.125, 0.125, 0.1875),
    "bath": (0.60, 0.60, 0.125, 0.125, 0.1875),
    "cellar": (0.60, 0.35, 0.0625, 0.0625, 0.0625),
    "vent": (0.50, 0.35, 0.0625, 0.0625, 0.0625),
}
# Recess from the wall face to the glass or leaf. A timber wall sets its
# windows near the outside, so this is shallower than the masonry reveals the
# 0.25 m test was written around; see notes.md.
REVEAL_DEPTH = {"cellar": 0.12}
REVEAL_DEFAULT = 0.15

# ------------------------------------------------------------ atlas bands
S1_Y0 = 2.0          # v of z = 0
S2_Y0 = 290.0        # v of z = Z_EAVE
ROOF_Y0, ROOF_H = 565.0, 256.0
# Main roof slope, fascia top to ridge, in metres. The roof band stretches
# this over ROOF_H rows; the porch roof samples the same rows at the same
# scale, so its snow guard lands the same distance above its own eave.
# build.py asserts it against the massing.
ROOF_SLOPE_LEN = 6.293
FASC_Y0 = 827.0      # v of the fascia's bottom edge
FASC_H = 20.0        # = the roof slab's 0.3125 m vertical thickness
GUTTER_PX = 9.0      # the gutter's rows, hung across the fascia's top
# The downpipes' sides span the middle five of them (scripts/downpipes.py)
PIPE_STRIP = (FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 - 2.5,
              FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 + 2.5)
UNI_Y0 = 852.0

# Region origins: the bottom-left of each opening's casing, in pixels.
ITEM_ORIGIN = {
    "door_front": (4.0, UNI_Y0),
    "door_back": (84.0, UNI_Y0),
    "wide": (164.0, UNI_Y0),
    "std": (302.0, UNI_Y0),
    "porch": (488.0, UNI_Y0),
    "bath": (549.0, UNI_Y0),
    "cellar": (610.0, UNI_Y0),
    "vent": (610.0, UNI_Y0 + 38.0),
}
CHIMNEY = (663.0, UNI_Y0, 64.0, 128.0)      # 1.0 m x 2.0 m, top-anchored
CHIMNEY_CAP = 0.12                          # the sheet cap down the stack's top, metres
CORNER = (734.0, UNI_Y0, 8.0, 64.0)         # corner-board strip, V stretched
PATCHES = {name: (750.0 + 14.0 * i, UNI_Y0, 8.0, 8.0) for i, name in enumerate(
    ("trim", "soffit", "reveal", "blank", "tread", "cap", "barge"))}
# The chimney flue's soot lining, in a row of its own above the others.
PATCHES["flue"] = (750.0, UNI_Y0 + 14.0, 8.0, 8.0)


def item_size_px(kind):
    w, h, cs, cb, ct = OPENINGS[kind]
    return (w + 2.0 * cs) * PPM, (h + cb + ct) * PPM


# ----------------------------------------------------------- material ids
ID_WALL, ID_TRIM, ID_SASH, ID_GLASS, ID_PLINTH, ID_METAL = 0, 1, 2, 3, 4, 5
ID_ROOF, ID_DOOR, ID_BRICK, ID_MORTAR, ID_CAP, ID_BLANK, ID_HANDLE = (
    6, 7, 8, 9, 10, 11, 12)
# (roughness, metallic). Painted steel stays mostly dielectric — the paint is
# what the light sees — but gets a little metallic so it separates from the
# timber beside it.
SURFACE = {
    ID_WALL: (0.74, 0.0), ID_TRIM: (0.58, 0.0), ID_SASH: (0.50, 0.0),
    ID_GLASS: (0.08, 0.0), ID_PLINTH: (0.90, 0.0), ID_METAL: (0.40, 0.30),
    ID_ROOF: (0.42, 0.25), ID_DOOR: (0.55, 0.0), ID_BRICK: (0.86, 0.0),
    ID_MORTAR: (0.92, 0.0), ID_CAP: (0.48, 0.35), ID_BLANK: (0.95, 0.0),
    ID_HANDLE: (0.35, 0.80),
}

# ---------------------------------------------------------------- palettes
# Traditional Finnish house paints, kept muted: punamulta red, ochre yellow,
# off-white, grey-blue and sage green. Colour only — each variant is the same
# set of ids and shading. Roof, trim and door vary with the body colour the
# way they would on a real street; glass, plinth and chimney never do.
VARIANTS = {
    "red": {"wall": (124, 54, 44), "trim": (222, 219, 208),
            "roof": (56, 58, 60), "door": (72, 80, 68)},
    "yellow": {"wall": (196, 164, 100), "trim": (224, 220, 208),
               "roof": (104, 54, 44), "door": (98, 72, 52)},
    "white": {"wall": (222, 219, 208), "trim": (98, 70, 52),
              "roof": (90, 68, 54), "door": (98, 72, 52)},
    "blue": {"wall": (134, 154, 168), "trim": (224, 221, 210),
             "roof": (60, 64, 68), "door": (80, 66, 56)},
    "green": {"wall": (142, 156, 122), "trim": (224, 221, 210),
              "roof": (84, 52, 44), "door": (98, 72, 52)},
}
DEFAULT_VARIANT = "red"
FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (148, 146, 140),
    ID_BRICK: (128, 66, 52), ID_MORTAR: (152, 146, 136),
    ID_CAP: (62, 64, 66), ID_BLANK: (52, 52, 52), ID_HANDLE: (150, 146, 138),
}

# Which ids each tiling band may contain. A stray pixel in a band is not a
# local blemish: every surface sampling that band repeats it.
BAND_IDS = {
    "S1": ((0, 286), {ID_PLINTH, ID_METAL, ID_WALL}),
    "S2": ((288, 561), {ID_TRIM, ID_WALL}),
    "ROOF": ((563, 823), {ID_ROOF}),
    "FASCIA": ((825, 849), {ID_METAL, ID_TRIM}),
}


# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto. The mesh
# already models every recess over 0.25 m; these are the few centimetres of
# board and sheet that only a normal map can show.
LAP_BUTT = 0.018     # lap siding: thickness at a board's butt
LAP_TOP = 0.004      # ... and at its top, under the next board's butt
CASING_H = 0.020     # window and door casings, proud of the wall
SILL_H = 0.035       # sill board, proud of the casing
SASH_H = 0.012       # sash frame, proud of the glass
SEAM_H = 0.022       # standing seams on the roof
GUTTER_R = 0.070     # half-round gutter's radius


# ============================================================ painting
def m(v):
    """Metres -> pixels."""
    return v * PPM


def paint_siding(c, y_lo, y_hi, y_first, seed):
    """Lap siding across the full width, boards BOARD tall from row y_first.

    Each board is a wedge, thick at its butt and thin at its top where the
    board above laps over it, so the normal map tilts every board face towards
    the sky and puts a downward-facing step under each butt. The lap is also an
    occlusion line, darker whatever the sun does. Board tone varies per run
    between butt joints. Boards are 4 m (256 px), which divides the atlas
    width, and each board's joints are offset by a hash: both the joints and
    the tone segments then repeat exactly every 1024 px, so a wall whose U
    crosses the wrap sees a board continue rather than change tone with no
    joint to explain it.
    """
    p = m(BOARD)
    run = 256
    assert ATLAS % run == 0
    sy, sx, Y, X = c.field(0, ATLAS, y_lo, y_hi)
    t = (Y - y_first) / p
    b = np.floor(t).astype(np.int64)
    r = t - b                                   # 0 at a board's butt, 1 at its top
    xs = np.floor(X).astype(np.int64) + atlas.hash_int(seed, b) % run
    seg = (xs // run) % (ATLAS // run)
    tone = 1.0 + 0.05 * (atlas.hash_unit(seed, b, seg) - 0.5)
    joint = (xs % run) == 0
    butt = r < 1.0 / p                          # the butt's end grain, facing down
    shade = tone * (1.0 - 0.14 * atlas.smoothstep(0.70, 1.0, r))
    shade = np.where(butt, 0.86 * tone, shade)
    c.mid[sy, sx] = ID_WALL
    c.shade[sy, sx] = np.where(joint, shade * 0.80, shade)
    c.ao[sy, sx] = np.where(butt | (r > 1.0 - 1.0 / p), 0.86, 1.0)
    h = LAP_TOP + (LAP_BUTT - LAP_TOP) * (1.0 - r)
    c.height[sy, sx] = np.where(joint, h - 0.004, h)


def paint_s1(c):
    y0 = S1_Y0
    top = int(np.ceil(y0 + m(Z_WALL_TOP))) + 2
    # concrete plinth, with the bleed rows under z = 0 painted the same
    c.paint(0, ATLAS, 0, y0 + m(Z_FLOOR), ID_PLINTH, 1.0, height=0.0)
    for k in range(1, 5):                          # faint formwork lines
        zz = y0 + m(0.15 * k)
        c.mul(0, ATLAS, zz, zz + 1, 0.94)
        c.lift(0, ATLAS, zz, zz + 1, -0.002)
    sy, sx, Y, _ = c.field(0, ATLAS, 0, y0 + m(Z_FLOOR))
    z = (Y - y0) / PPM
    splash = 0.80 + 0.20 * np.clip(z / 0.35, 0.0, 1.0) ** 0.7   # rain splash-back
    c.shade[sy, sx] *= splash
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.85 + 0.15 * np.clip(z / 0.35, 0, 1))
    c.mul(0, ATLAS, y0 + m(Z_FLOOR) - 2, y0 + m(Z_FLOOR), 0.86, ao=0.80)  # under the flashing
    # plinth flashing: a folded sheet sloping out to a lip that sheds water
    # clear of the concrete; its underside is in shadow whatever the sun does
    fy0, fy1 = y0 + m(Z_FLOOR), y0 + m(Z_FLASH)
    c.paint(0, ATLAS, fy0, fy1, ID_METAL, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, fy0, fy1)
    c.height[sy, sx] = 0.022 - 0.010 * (Y - fy0) / (fy1 - fy0)
    c.paint(0, ATLAS, fy0, fy0 + 1, ID_METAL, 0.80)
    # siding up to the wall top, plus bleed
    paint_siding(c, fy1, min(top, 286), fy1, seed=11)
    # shadow under the gable belt board; on the long walls the same rows sit
    # just under the soffit, where a darker band is correct too
    for k, f in enumerate((0.84, 0.90, 0.95)):
        yy = y0 + m(Z_EAVE) - 1 - k
        c.mul(0, ATLAS, yy, yy + 1, f, ao=0.8 + 0.06 * k)


def paint_s2(c):
    y0 = S2_Y0
    bt = y0 + m(BELT_H)
    c.paint(0, ATLAS, y0 - 2, bt, ID_TRIM, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, bt, CASING_H, 1.0, axes="y")          # belt board
    c.mul(0, ATLAS, y0 - 2, y0 + 1, 0.85)                        # its lower edge
    paint_siding(c, bt, 561, bt, seed=29)
    c.mul(0, ATLAS, bt, bt + 2, 0.86, ao=0.82)                   # under the belt's drip


def paint_roof(c):
    """Standing-seam steel, V stretched up the slope (ROOF_H rows over
    ROOF_SLOPE_LEN metres). Seams vary in U only and need no correction; the
    snow guard varies in V, so its heights are scaled by the band's px/m over
    PPM to keep the slope the normal map derives from physical."""
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0 - 2, y0 + h + 2, ID_ROOF, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - 2, y0 + h + 2)
    xm = X % 32.0
    v = Y - y0
    rib = xm < 2.0
    height = np.where(rib, SEAM_H * np.clip(np.sin(np.pi * xm / 2.0), 0.0, 1.0), 0.0)
    shade = np.where((xm >= 2.0) & (xm < 3.0), 0.93, 1.0)       # foot of the seam
    ao = np.where((xm >= 2.0) & (xm < 3.0), 0.85, 1.0)
    shade = np.where(v < 3, shade * 0.85, shade)                 # eave drip edge
    # snow guard: two round tubes on brackets, ~0.5 m up from the eave --
    # standard on Finnish metal roofs
    rpm = ROOF_H / ROOF_SLOPE_LEN
    k = rpm / PPM
    g = round(0.50 * rpm)
    for t0, t1 in ((g, g + 2.0), (g + 3.0, g + 4.5)):
        inside = (v >= t0) & (v < t1)
        tube = 0.035 * k * np.sqrt(np.clip(1.0 - (2.0 * (v - t0) / (t1 - t0) - 1.0) ** 2, 0, 1))
        height = np.where(inside, np.maximum(height, tube), height)
    shade = np.where((v >= g - 3) & (v < g - 1), shade * 0.80, shade)   # under the tubes
    ao = np.where((v >= g - 3) & (v < g + 4.5), np.minimum(ao, 0.85), ao)
    bracket = (xm >= 29.0) & (xm < 31.0) & (v >= g - 3) & (v < g + 4.5)
    height = np.where(bracket, 0.030 * k, height)
    shade = np.where(bracket, shade * 0.75, shade)
    # ridge flashing across the top, with the edge where it laps the sheet
    ridge = v >= h - 12
    height = np.where(ridge, 0.008 * k, height)
    shade = np.where(ridge, 0.97, shade)
    shade = np.where((v >= h - 12) & (v < h - 11), shade * 0.85, shade)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao


def paint_fascia(c):
    """The eave's vertical edge: a fascia board in the trim colour, with a
    half-round steel gutter hung across its top.

    The band's top row is the roof's edge, where the water leaves the roof,
    so the gutter sits right under it and the board shows below. The first
    version painted the gutter across the board's foot instead, where no
    water could reach it.
    """
    y0 = FASC_Y0
    top = y0 + FASC_H                       # the roof's edge
    c.paint(0, ATLAS, y0 - 2, top + 2, ID_TRIM, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 - 2, y0 + 1, ID_TRIM, 0.88)      # board's lower edge
    # half-round gutter: belly at the bottom, rolled lip at the top. Its roll
    # is height; only the belly's underside is darker.
    gh = GUTTER_PX
    g0 = top - 1 - gh
    c.paint(0, ATLAS, g0, top - 1, ID_METAL, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top - 1)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_METAL, 0.80)
    c.paint(0, ATLAS, top - 1, top + 2, ID_METAL, 0.80, height=0.0)  # roof sheet's drip edge
    c.ao[c.sl(0, ATLAS, g0 - 3, top + 2)] = 0.9
    for k, f in enumerate((0.92, 0.86, 0.80)):            # occluded under the gutter
        c.mul(0, ATLAS, g0 - 3 + k, g0 - 2 + k, f)
    # hangers every 1.0 m, a spacing that divides the atlas width
    sy, sx, _, X = c.field(0, ATLAS, g0 + 2, top - 1)
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.80, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_opening(c, kind, style):
    """One window or door: casing, sill, sash frames, glass."""
    x0, y0 = ITEM_ORIGIN[kind]
    w, h, cs, cb, ct = OPENINGS[kind]
    rw, rh = item_size_px(kind)
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0 + m(cb), y0 + m(cb + h)
    concrete = style == "cellar"
    cas_id = ID_PLINTH if concrete else ID_TRIM
    # casing, bled 2 px outward so filtering at the region edge stays casing;
    # a timber casing stands proud of the wall with rounded arrises
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, cas_id, 1.0, 1.0, height=0.0)
    if not concrete:
        c.bevel(x0, x0 + rw, y0, y0 + rh, CASING_H, 1.0)

    if not concrete and style != "vent":
        top = y0 + rh
        # drip cap: sheet steel over the head casing, sloping out
        c.paint(x0 - 2, x0 + rw + 2, top - 3, top + 2, ID_METAL, 1.0)
        sy, sx, Y, _ = c.field(x0 - 2, x0 + rw + 2, top - 3, top + 2)
        c.height[sy, sx] = 0.032 - 0.012 * np.clip((Y - (top - 3)) / 3.0, 0.0, 1.0)
        c.paint(x0 - 2, x0 + rw + 2, top - 4, top - 3, ID_TRIM, 0.85, 0.8)
        c.mul(ox0 - 1, ox1 + 1, oy1, oy1 + 1, 0.84, ao=0.8)             # head shadow
        c.mul(ox0 - 1, ox0, oy0, oy1, 0.93)
        if cb > 0:                                                       # sill board
            c.paint(x0 - 2, x0 + rw + 2, y0 - 2, oy0, ID_TRIM, 1.0)
            c.bevel(x0, x0 + rw, y0, oy0, SILL_H, 1.0)
            c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + 1, ID_TRIM, 0.80, 0.8)

    if style in ("door_front", "door_back"):
        paint_door(c, ox0, ox1, oy0, oy1, style)
        return
    if style == "vent":
        c.paint(ox0, ox1, oy0, oy1, ID_TRIM, 0.62, 0.6, height=-0.010)
        for yy in np.arange(oy0, oy1, 3.0):
            # louvre blades, sloping out and down to shed rain
            c.paint(ox0, ox1, yy, yy + 2, ID_TRIM, 1.0, 0.9)
            sy, sx, Y, _ = c.field(ox0, ox1, yy, yy + 2)
            c.height[sy, sx] = 0.020 * (1.0 - (Y - yy) / 2.0)
            c.paint(ox0, ox1, yy, yy + 1, ID_TRIM, 0.85, 0.8)
        return

    # Glass: this sets the id and the AO, and albedo then hands every pane to
    # glazing.rooms(), which owns the colour. Nothing written to shade inside a
    # pane survives that; the sash shading below stays because it writes AO.
    # The glass keeps a flat normal (normal_map's flat_ids).
    f = 3.0 if concrete else m(0.0625)      # frame round the glass
    sash_id = ID_BLANK if concrete else ID_SASH
    c.paint(ox0, ox1, oy0, oy1, sash_id, 1.0, 1.0)
    if not concrete:
        c.bevel(ox0, ox1, oy0, oy1, SASH_H, 1.0)
    c.paint(ox0 + f, ox1 - f, oy0 + f, oy1 - f, ID_GLASS, ao=0.9, height=0.0)
    # Plain glass: one clear pane inside the frame, with no crossbars and no
    # mullions. Two earlier passes painted divisions here -- first a T-pattern
    # top light, then upright mullions between sashes -- and both were wrong
    # for these windows. A pane sits a few mm behind its sash: occlusion inside
    # the top and left bars.
    c.mul(ox0 + f, ox1 - f, oy1 - f - 1, oy1 - f, 0.82, ao=0.8)
    c.mul(ox0 + f, ox0 + f + 1, oy0 + f, oy1 - f, 0.88)


def paint_door(c, x0, x1, y0, y1, style):
    c.paint(x0, x1, y0, y1, ID_DOOR, 1.0, 1.0, height=0.0)
    wpx = x1 - x0
    if style == "door_front":
        # framed-and-panelled leaf: stiles and rails proud, the two panels
        # sunk and fielded, and a glazed upper panel
        st = m(0.11)
        c.paint(x0, x1, y0, y1, height=0.012)
        for p0, p1 in ((y0 + st, y0 + m(0.95)), (y0 + m(0.95) + st, y1 - st)):
            c.bevel(x0 + st, x1 - st, p0, p1, 0.006, 1.5)
            c.mul(x0 + st, x1 - st, p0, p1, 0.97)
            c.mul(x0 + st, x1 - st, p1 - 1, p1, 0.90, ao=0.75)       # under the top rail
            c.mul(x0 + st, x0 + st + 1, p0, p1, 0.92, ao=0.8)
        gx0, gx1 = x0 + wpx * 0.30, x1 - wpx * 0.30
        gy0, gy1 = y0 + m(1.35), y0 + m(1.85)
        c.paint(gx0, gx1, gy0, gy1, ID_GLASS, 0.86, 0.85, height=0.0)
        c.mul(gx0, gx1, gy1 - 1, gy1, 0.8)
    else:
        # plank leaf, the plainer back door: V-grooves between the planks
        for xx in np.arange(x0, x1, m(0.15)):
            c.mul(xx, xx + 1, y0, y1, 0.82, ao=0.8)
            c.lift(xx, xx + 1, y0, y1, -0.003)
        c.paint(x0 + wpx * 0.32, x1 - wpx * 0.32, y0 + m(1.45), y0 + m(1.85),
                ID_GLASS, 0.86, 0.85, height=0.0)
    hx = x1 - m(0.12)
    c.paint(hx - 1, hx, y0 + m(0.92), y0 + m(1.10), ID_HANDLE, 0.9, height=0.015)
    c.paint(hx - 2, hx + 1, y0 + m(1.00), y0 + m(1.06), ID_HANDLE, 1.0, height=0.030)
    c.paint(x0, x1, y0, y0 + 2, ID_DOOR, 0.8, 0.7)                    # kick wear


def paint_chimney(c):
    """The stack's brick, in the catalog's module and bond (scripts/
    brickwork.py), under a sheet cap with soot below it. The region is
    top-anchored, so the courses are counted down from the cap: the course
    under it is whole, and the cut course lands at the region's foot, inside
    the roof. Its rows below that stay mortar."""
    x0, y0, w, h = CHIMNEY
    top = y0 + h
    cap = top - m(CHIMNEY_CAP)
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_MORTAR, 1.0, height=0.0)
    course = m(brickwork.COURSE)
    foot = cap - course * np.floor((cap - (y0 - 2)) / course)
    # up to the cap only: the joints' AO would show through it
    brickwork.paint(c, x0 - 2, x0 + w + 2, foot, cap, (ID_BRICK, ID_BRICK, ID_MORTAR),
                    tone_courses=32, seed=5)
    c.mul(x0 - 2, x0 + w + 2, top - m(0.55), cap, 0.78)               # soot
    c.paint(x0 - 2, x0 + w + 2, cap, top + 2, ID_CAP, 1.0, height=0.020)
    c.paint(x0 - 2, x0 + w + 2, cap, cap + 1, ID_CAP, 0.8, 0.7)


def paint_corner(c):
    x0, y0, w, h = CORNER
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_TRIM, 1.0, height=0.0)
    c.bevel(x0, x0 + w, y0 - 2, y0 + h + 2, CASING_H, 1.0, axes="x")
    c.mul(x0 - 2, x0 + w + 2, y0 - 2, y0 + 4, 0.92)


def paint_patches(c):
    spec = {"trim": (ID_TRIM, 1.0, 1.0), "soffit": (ID_TRIM, 0.88, 0.85),
            "reveal": (ID_TRIM, 0.70, 0.6), "blank": (ID_BLANK, 1.0, 0.5),
            "tread": (ID_PLINTH, 0.96, 1.0), "cap": (ID_CAP, 1.0, 1.0),
            "barge": (ID_TRIM, 0.97, 1.0),
            # soot inside the flue: blank darkened to about sRGB 34, and
            # occluded, as a narrow shaft is whatever the sun does
            "flue": (ID_BLANK, 0.45, 0.35)}
    atlas.paint_patches(c, PATCHES, spec)


def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.
    The wall bands' V is height and the roof band's is slope, so ground
    splash, the sheltered eaves and the dirtier eave land the same on every
    wall and every roof face."""
    w = weathering.Weather(c, clean=(ID_GLASS,), steel=(ID_ROOF, ID_METAL, ID_CAP))
    w.grime()
    w.fade((ID_WALL, ID_TRIM, ID_SASH, ID_DOOR))
    w.wash((ID_WALL,))
    # S1: the plinth, its flashing, the siding's splashed foot and its top
    # sheltered under the soffit
    w.plinth(0, ATLAS, S1_Y0, S1_Y0 + m(Z_FLOOR), (ID_PLINTH,))
    w.add("D", 0, ATLAS, S1_Y0 + m(Z_FLOOR), S1_Y0 + m(Z_FLASH),
          lambda Y, X, nz: 0.10 * nz("blotch"), (ID_METAL,))
    w.splash(0, ATLAS, S1_Y0 + m(Z_FLASH), 287, (ID_WALL,))
    w.shelter(0, ATLAS, S1_Y0 + m(3.8), S1_Y0 + m(Z_EAVE), (ID_WALL,), top=287)
    # the roof, silt at the seams' feet, debris held above the snow guard,
    # rust at its brackets and in short runs under them, and on the drip edge
    rpm = ROOF_H / ROOF_SLOPE_LEN
    roof = (ID_ROOF,)
    y0, y1 = ROOF_Y0 - 2, ROOF_Y0 + ROOF_H + 2
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, ROOF_SLOPE_LEN, roof)
    w.add("D", 0, ATLAS, y0, y1, lambda Y, X, nz: 0.12 * (
        ((X % 32.0) >= 2.0) & ((X % 32.0) < 5.0)), roof)
    g = ROOF_Y0 + round(0.50 * rpm)
    w.add("D", 0, ATLAS, g + 4.5, g + 16.0, lambda Y, X, nz: 0.25 * nz("blotch")
          * (1.0 - (Y - g - 4.5) / 11.5), roof)
    w.add("R", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.18 * ((X % 32.0) >= 28.0), roof)
    w.add("R", 0, ATLAS, g - 14, g - 3, lambda Y, X, nz: 0.15 * (
        ((X % 32.0) >= 29.2) & ((X % 32.0) < 30.8)) * (1.0 - (g - 3 - Y) / 11.0)
        * atlas.smoothstep(-0.5, 0.8, nz("runs")), roof)
    w.add("R", 0, ATLAS, y0, ROOF_Y0 + 3, lambda Y, X, nz: 0.12 * nz("speck"), roof)
    # the fascia: runs down the board from the gutter, a dirty belly
    g0 = FASC_Y0 + FASC_H - 10.0
    w.add("D", 0, ATLAS, FASC_Y0 - 2, g0, 0.06, (ID_TRIM,))
    w.runs(0, ATLAS, FASC_Y0 - 2, g0, (ID_TRIM,), 0.22, fall=6.0, lo=0.4, hi=1.6)
    w.add("D", 0, ATLAS, g0, g0 + 4, lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"), (ID_METAL,))
    # openings: sills, heads and bottom rails; doors' handles and feet
    for kind, (wd, h, cs, cb, ct) in OPENINGS.items():
        if kind in ("cellar", "vent"):
            continue
        x0, yb = ITEM_ORIGIN[kind]
        rw, rh = item_size_px(kind)
        ox0, ox1 = x0 + m(cs), x0 + m(cs + wd)
        oy0, oy1 = yb + m(cb), yb + m(cb + h)
        if kind.startswith("door"):
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR,), handle=(ox1 - m(0.12), oy0 + m(1.03)))
        else:
            w.window(x0, yb, rw, rh, oy0, oy1, m(0.0625), (ID_TRIM,), (ID_SASH,))
    # the chimney: runs under the cap, salt bloom low on the stack
    cx0, cy0, cw, ch = CHIMNEY
    ctop = cy0 + ch
    brick = (ID_BRICK, ID_MORTAR)
    w.runs(cx0 - 2, cx0 + cw + 2, cy0 - 2, ctop - m(CHIMNEY_CAP), brick, 0.22, fall=m(0.6),
           hi=1.6)
    w.bloom(cx0 - 2, cx0 + cw + 2, cy0 - 2, ctop - m(0.9), brick, fade=m(0.5))
    # corner boards: splashed at the foot (the strip's V starts at Z_FLASH)
    kx0, ky0, kw, kh = CORNER
    w.add("D", kx0 - 2, kx0 + kw + 2, ky0 - 2, ky0 + kh + 2, lambda Y, X, nz: 0.22
          * np.exp(-np.clip(Y - ky0, 0.0, None) / 4.0), (ID_TRIM,))
    return w


def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_s1(c)
    paint_s2(c)
    paint_roof(c)
    paint_fascia(c)
    for kind in OPENINGS:
        paint_opening(c, kind, {"door_front": "door_front", "door_back": "door_back",
                                "cellar": "cellar", "vent": "vent"}.get(kind, kind))
    paint_chimney(c)
    paint_corner(c)
    paint_patches(c)
    c.check_bands(BAND_IDS)

    # Weathering. Every field is periodic, so the bands still wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    wood = np.isin(c.mid, (ID_WALL, ID_TRIM, ID_DOOR))
    grain = atlas.noise(c, 5, 60.0, 0.35)            # streaks along the boards
    c.shade[wood] *= 1.0 + 0.02 * grain[wood]
    c.height[wood] += 0.0003 * grain[wood]
    roof = c.mid == ID_ROOF
    streak = atlas.noise(c, 7, 0.8, 40.0)            # rain runs down the slope
    c.shade[roof] *= 1.0 + 0.035 * streak[roof]
    concrete = c.mid == ID_PLINTH
    pores = atlas.noise(c, 9, 0.8)
    c.shade[concrete] *= 1.0 + 0.03 * pores[concrete]
    c.height[concrete] += 0.0006 * pores[concrete]
    weather(c)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    t[ID_WALL] = pal["wall"]
    t[ID_TRIM] = t[ID_SASH] = pal["trim"]
    t[ID_ROOF] = pal["roof"]
    t[ID_METAL] = np.minimum(np.array(pal["roof"], np.float32) * 1.18 + 6, 255)
    t[ID_DOOR] = pal["door"]
    return t


def export(out_dir, ss=atlas.SS):
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.012)
    c.weather.dust(cav, (ID_WALL,))                  # along the laps
    rough = 0.04 * atlas.noise(c, 13, 20.0)
    path = os.path.join(out_dir, ASSET)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS,)), path + "_normal.png"),
               atlas.save(glazing.night_rooms(atlas.coverage(c, ID_GLASS) > 0,
                                          atlas.emission(c, ID_GLASS)),
                          path + "_emission.png")]
    glass = atlas.coverage(c, ID_GLASS) >= 0.5
    for v in VARIANTS:
        rgb = glazing.rooms(glass, atlas.albedo(c, lut(v), grime=0.25 * cav))
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
