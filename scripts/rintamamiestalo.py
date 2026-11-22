# SPDX-License-Identifier: GPL-3.0-or-later

"""The rintamamiestalo family of buildings/residential/: one atlas, the mesh
kit, the tier policy and the shared checks of four houses that are variations
of one design, which each house's two scripts parameterise.

The rintamamiestalo is the 1940s-50s one-and-a-half-storey Finnish veterans'
house: a 10 x 8 m block under a 45 degree gable roof, horizontal lap siding
over a concrete plinth with cellar lights, plain-glass windows, a brick
chimney open at the top, a back-door canopy. rintamamiestalo_porch,
_side_entry, _balcony and _gable_entry share its sizes, palettes, siding,
roof, windows and doors, and differ in their massing: where the entrance
porch stands, the balcony and its dormer, the terrace on a gable entrance.
So the type lives here, and each house keeps what makes it that house:

    facade_atlas.py     LAYOUT = rintamamiestalo.Layout(name, ...): which of
                        the family's optional regions its atlas carries (a
                        balcony door, the bathroom window, the deck patch,
                        the deck and railing strips) and where its gable
                        band and roof band lie; export(out_dir) paints it.
    build.py            K = rintamamiestalo.Kit(LAYOUT, HERE): its massing,
                        its walls as Wall tables, its own solids, its layout
                        checks and facts(); K builds the walls, roofs,
                        chimney, canopy and steps, and K.tier() everything a
                        tier adds to them and the union.

Two steps rebuild a house, as before: its textures (system Python with scipy
and Pillow), then its tiers in Blender, which only read the PNGs:

    python3 buildings/residential/<house>/facade_atlas.py export
    blender --background --python buildings/residential/<house>/build.py

The atlas is a trim sheet rather than one picture per elevation: a house's
elevations are all different, and painting each at the catalog's 64 px/m does
not fit in 1024², so the walls sample tiling bands and every opening samples
a region of its own (V up, in pixels; the default rows, the gable entry's
taller gable band in brackets):

    y    0 ..  286   S1      lower walls, z 0 .. 4.40: plinth, flashing, siding
    y  288 ..  561   S2      gables from the belt board up [.. 586]
    y  563 ..  823   ROOF    standing-seam roof, V stretched up the slope [588 .. 824]
    y  825 ..  849   FASCIA  eave fascia with its gutter
    y  852 .. 1000   unique  doors, windows, cellar lights, vent, chimney,
                             corner-board strip, flat patches
    y 1002 .. 1012   DECK    deck boards across U (strips=True)
    y 1012 .. 1024   RAIL    railing balusters across U (strips=True)

The bands span the full width and tile in U. Every opening's region carries
its casing as well as its glazing, because the casing is the one part of a
window a tiling siding band cannot place; the build cuts a ring of faces
round each opening for it to land on. Painting produces a material-id map, a
shade multiplier, an AO map and a height map once; each variant is those
coloured by its own palette, so the variants cannot differ in anything but
colour. Relief that should answer the sun (siding laps, standing seams, the
gutter's roll, raised casings) is height and reaches the renderer through the
normal map; shade carries tone, wear and the occlusion in laps and joints.
Weather is scripts/weathering.py's: weather() says where it goes.

What later fixes change once for all four lives in one place each: the tier
policy (ITEM_MODES with a house's exceptions in ITEM_MODES_HOUSE,
CANOPY_LAST, RAMP_FROM, RAILS, DISSOLVE_FROM; the downpipes and the roof kit
keep theirs in their own scripts, but for a house's own downpipe tiers in
DOWNPIPE_MODES_HOUSE), the ORM table
(SURFACE, with the roughness noise in export()) and the night tint (TINT).

Imports numpy alone at the top (with the atlas scripts, which do the same),
so system Python paints and Blender's Python reads the layout; painting needs
scipy and Pillow, the build half bpy, each imported where used.
"""

import math
import os
import sys
from collections import namedtuple

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import atlas  # noqa: E402
import brickwork  # noqa: E402
import glazing  # noqa: E402
import weathering  # noqa: E402

ATLAS = 1024
PPM = 64.0

# --------------------------------------------------------- vertical layout
# Metres above ground, shared by every wall so storey lines agree all round.
Z_FLOOR = 0.70       # plinth top = ground-floor level; door thresholds
Z_FLASH = 0.75       # top of the plinth flashing; siding and corner boards
Z_EAVE = 4.30        # long walls meet the soffit; the default gable belt
Z_WALL_TOP = 4.40    # walls run on up into the roof slab, which trims them
BELT_H = 0.1875      # belt board across the foot of each gable (12 px)
BOARD = 0.125        # lap-siding pitch (8 px)
CW = 0.125           # corner-board width (8 px)

# ------------------------------------------------------------- openings
# kind -> (width, height, casing side, casing bottom, casing top), metres.
# Casing is painted, never modelled: at 20-40 mm proud it fails the 0.25 m
# test by an order of magnitude. Doors have no bottom casing: the leaf runs
# down to the threshold. A Layout picks the optional ones.
DOOR = (0.90, 2.10, 0.125, 0.0, 0.1875)
OPENING_SIZES = {
    "door_front": DOOR,
    "door_back": DOOR,
    "wide": (1.80, 1.40, 0.125, 0.125, 0.1875),
    "std": (1.20, 1.40, 0.125, 0.125, 0.1875),
    "porch": (0.60, 0.80, 0.125, 0.125, 0.1875),
    "bath": (0.60, 0.60, 0.125, 0.125, 0.1875),
    "cellar": (0.60, 0.35, 0.0625, 0.0625, 0.0625),
    "vent": (0.50, 0.35, 0.0625, 0.0625, 0.0625),
}
# The balcony door onto a balcony: one glazed leaf, or a pair (1.40 m).
BALCONY_DOORS = {"single": DOOR, "pair": (1.40, 2.10, 0.125, 0.0, 0.1875)}
# Recess from the wall face to the glass or leaf. A timber wall sets its
# windows near the outside, so this is shallower than the masonry reveals the
# 0.25 m test was written around.
REVEAL_DEPTH = {"cellar": 0.12}
REVEAL_DEFAULT = 0.15

# ------------------------------------------------------------ atlas bands
S1_Y0 = 2.0          # v of z = 0
S2_Y0 = 290.0        # v of z = the gables' belt (Layout.Z_BELT)
ROOF = (565.0, 256.0)   # the default roof band's first row and height
# Main roof slope, fascia top to ridge, in metres. The roof band stretches
# this over its rows; every roof (porch, dormer, canopy) samples the same rows
# at the same scale, so its snow guard lands the same distance above its own
# eave. Each build.py asserts it against its massing.
ROOF_SLOPE_LEN = 6.293
FASC_Y0 = 827.0      # v of the fascia's bottom edge
FASC_H = 20.0        # = the roof slab's 0.3125 m vertical thickness
GUTTER_PX = 9.0      # the gutter's rows, hung across the fascia's top
# The downpipes' sides span the middle five of them (scripts/downpipes.py)
PIPE_STRIP = (FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 - 2.5,
              FASC_Y0 + FASC_H - 1 - GUTTER_PX / 2.0 + 2.5)
UNI_Y0 = 852.0
# Two strips across the full width, above the unique row (strips=True). Their
# patterns vary across U only, so they tile along a surface of any length.
# The deck samples its strip at one V. The railing squeezes its whole
# baluster zone into RAIL_H rows, which carry only a shading gradient.
DECK_Y0, DECK_H = 1004.0, 6.0
RAIL_Y0, RAIL_H = 1014.0, 8.0

# Region origins: the bottom-left of each opening's casing, in pixels.
ITEM_ORIGINS = {
    "door_front": (4.0, UNI_Y0),
    "door_back": (84.0, UNI_Y0),
    "wide": (164.0, UNI_Y0),
    "std": (302.0, UNI_Y0),
    "porch": (488.0, UNI_Y0),
    "bath": (549.0, UNI_Y0),
    "cellar": (610.0, UNI_Y0),
    "vent": (610.0, UNI_Y0 + 38.0),
    "door_balcony": (866.0, UNI_Y0),
}
CHIMNEY = (663.0, UNI_Y0, 64.0, 128.0)      # 1.0 m x 2.0 m, top-anchored
CHIMNEY_CAP = 0.12                          # the sheet cap down the stack's top, metres
CORNER = (734.0, UNI_Y0, 8.0, 64.0)         # corner-board strip, V stretched
PATCH_NAMES = ("trim", "soffit", "reveal", "blank", "tread", "cap", "barge")

# ----------------------------------------------------------- material ids
ID_WALL, ID_TRIM, ID_SASH, ID_GLASS, ID_PLINTH, ID_METAL = 0, 1, 2, 3, 4, 5
ID_ROOF, ID_DOOR, ID_BRICK, ID_MORTAR, ID_CAP, ID_BLANK, ID_HANDLE, ID_DECK = (
    6, 7, 8, 9, 10, 11, 12, 13)
# The ORM table: (roughness, metallic). Painted steel (the roof, the gutter,
# flashing and drip caps, the chimney cap) is dielectric: the paint is what
# the light sees. It separates from the timber beside it by its roughness,
# and it takes no roughness noise (PAINTED_STEEL, export()): a metallic
# sheet, and noise at the scale of metres, put dark blotches about 2 m
# across on the sunward slope at every distance. The door handles are the
# one bare metal. ID_DECK only where a house has the deck strip; an id a
# house does not paint changes none of its texels.
SURFACE = {
    ID_WALL: (0.74, 0.0), ID_TRIM: (0.58, 0.0), ID_SASH: (0.50, 0.0),
    ID_GLASS: (0.08, 0.0), ID_PLINTH: (0.90, 0.0), ID_METAL: (0.46, 0.0),
    ID_ROOF: (0.46, 0.0), ID_DOOR: (0.55, 0.0), ID_BRICK: (0.86, 0.0),
    ID_MORTAR: (0.92, 0.0), ID_CAP: (0.48, 0.0), ID_BLANK: (0.95, 0.0),
    ID_HANDLE: (0.35, 0.80), ID_DECK: (0.80, 0.0),
}
PAINTED_STEEL = (ID_ROOF, ID_METAL, ID_CAP)

# ---------------------------------------------------------------- palettes
# Traditional Finnish house paints, kept muted: punamulta red, ochre yellow,
# off-white, grey-blue and sage green. Colour only: each variant is the same
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
    # weathered grey-brown decking, the same on every colour of house
    ID_DECK: (116, 104, 90),
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


def m(v):
    """Metres -> pixels."""
    return v * PPM


# ================================================================== layout
class Layout:
    """One house's atlas layout: the family's numbers, and which optional
    regions this house carries.

    name          the asset's folder name; the PNGs are named for it
    balcony_door  None, "single" (one glazed leaf) or "pair" (two)
    bath          the small bathroom window's region
    deck_patch    a flat "deck" patch in the roof's colour, a shade darker
    strips        the DECK and RAIL strips over the unique row
    z_belt        where the gables' belt board, and band S2, start
    s2_span       how far S2 reaches above z_belt; the gable apex must fit
    roof          (first row, height) of the roof band; S2 ends 4 rows under it

    Attributes are the numbers a facade_atlas.py used to hold, in capitals
    (OPENINGS, ITEM_ORIGIN, PATCHES, ROOF_Y0, ROOF_H, ROOF_RPM, Z_BELT,
    S2_SPAN, S2_TOP, BAND_IDS, ...). A capitalised name a Layout does not set
    is the family's module constant, so build.py reads every number as L.X.
    """

    def __init__(self, name, balcony_door=None, bath=True, deck_patch=False, strips=False,
                 z_belt=Z_EAVE, s2_span=4.20, roof=ROOF):
        if balcony_door not in (None, "single", "pair"):
            raise ValueError("balcony_door is None, single or pair, not %r" % (balcony_door,))
        self.ASSET = name
        self.BALCONY_DOOR = balcony_door
        self.STRIPS = bool(strips)
        # Opening sizes, in the order they are painted and weathered; the
        # region row keeps its own order, the balcony door's last.
        sizes = dict(OPENING_SIZES)
        kinds = ["door_front", "door_back"] + (["door_balcony"] if balcony_door else [])
        kinds += ["wide", "std", "porch"] + (["bath"] if bath else []) + ["cellar", "vent"]
        sizes["door_balcony"] = BALCONY_DOORS.get(balcony_door)
        self.OPENINGS = {k: sizes[k] for k in kinds}
        self.ITEM_ORIGIN = {k: xy for k, xy in ITEM_ORIGINS.items() if k in self.OPENINGS}
        names = PATCH_NAMES + (("deck",) if deck_patch else ())
        self.PATCHES = {n: (750.0 + 14.0 * i, UNI_Y0, 8.0, 8.0) for i, n in enumerate(names)}
        # The chimney flue's soot lining, in a row of its own above the others.
        self.PATCHES["flue"] = (750.0, UNI_Y0 + 14.0, 8.0, 8.0)
        self.Z_BELT = z_belt
        self.S2_SPAN = s2_span
        self.S2_TOP = z_belt + s2_span      # build.py asserts the apex fits
        self.ROOF_Y0, self.ROOF_H = roof
        self.ROOF_RPM = self.ROOF_H / ROOF_SLOPE_LEN    # atlas px per metre up a slope
        # Which ids each tiling band may contain. A stray pixel in a band is
        # not a local blemish: every surface sampling that band repeats it.
        r0 = int(self.ROOF_Y0)
        self.BAND_IDS = {
            "S1": ((0, 286), {ID_PLINTH, ID_METAL, ID_WALL}),
            "S2": ((288, r0 - 4), {ID_TRIM, ID_WALL}),
            "ROOF": ((r0 - 2, int(self.ROOF_Y0 + self.ROOF_H) + 2), {ID_ROOF}),
            "FASCIA": ((825, 849), {ID_METAL, ID_TRIM}),
        }
        if self.STRIPS:
            self.BAND_IDS["DECK"] = ((1002, 1012), {ID_DECK})
            self.BAND_IDS["RAIL"] = ((1012, 1024), {ID_TRIM})
        # Siding regions, stacked from the ground: (z where each starts,
        # atlas band, the z that band's first row stands for).
        self.EAVE_BANDS = [(0.0, "S1", 0.0)]
        self.GABLE_BANDS = [(0.0, "S1", 0.0), (z_belt, "S2", z_belt)]

    def __getattr__(self, name):
        if name.isupper() and name in globals():
            return globals()[name]
        raise AttributeError(name)

    def item_size_px(self, kind):
        w, h, cs, cb, ct = self.OPENINGS[kind]
        return (w + 2.0 * cs) * PPM, (h + cb + ct) * PPM

    def region_problems(self):
        """Two unique regions overlapping, bleed included, or one leaving the
        atlas or running into the deck strip. The unique row is packed by
        hand, so a region added at the end is exactly where a collision would
        happen unnoticed."""
        rects = {k: (x0, y0) + self.item_size_px(k) for k, (x0, y0) in self.ITEM_ORIGIN.items()}
        rects.update({"chimney": CHIMNEY, "corner": CORNER})
        rects.update({"patch_" + k: r for k, r in self.PATCHES.items()})
        problems = atlas.region_problems(rects, ATLAS)
        if self.STRIPS:
            problems += ["%s runs into the deck strip" % a for a, (ax, ay, aw, ah)
                         in sorted(rects.items()) if ay + ah + 2 > DECK_Y0 - 2]
        return problems

    def check_regions(self):
        problems = self.region_problems()
        if problems:
            raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ painting
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
    # shadow just under the long walls' soffit (where the belt is at the
    # eave, under the gables' belt board too)
    for k, f in enumerate((0.84, 0.90, 0.95)):
        yy = y0 + m(Z_EAVE) - 1 - k
        c.mul(0, ATLAS, yy, yy + 1, f, ao=0.8 + 0.06 * k)


def paint_s2(c, L):
    y0 = S2_Y0
    bt = y0 + m(BELT_H)
    c.paint(0, ATLAS, y0 - 2, bt, ID_TRIM, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0, bt, CASING_H, 1.0, axes="y")          # belt board
    c.mul(0, ATLAS, y0 - 2, y0 + 1, 0.85)                        # its lower edge
    paint_siding(c, bt, L.BAND_IDS["S2"][0][1], bt, seed=29)
    c.mul(0, ATLAS, bt, bt + 2, 0.86, ao=0.82)                   # under the belt's drip


def paint_roof(c, L):
    """Standing-seam steel, V stretched up the slope (ROOF_H rows over
    ROOF_SLOPE_LEN metres). Seams vary in U only and need no correction; the
    snow guard varies in V, so its heights are scaled by the band's px/m over
    PPM to keep the slope the normal map derives from physical."""
    y0, h = L.ROOF_Y0, L.ROOF_H
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
    rpm = L.ROOF_H / ROOF_SLOPE_LEN
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
    half-round steel gutter hung across its top. The band's top row is the
    roof's edge, where the water leaves the roof, so the gutter sits right
    under it and the board shows below."""
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


def paint_opening(c, L, kind):
    """One window or door: casing, sill, sash frames, glass."""
    x0, y0 = L.ITEM_ORIGIN[kind]
    w, h, cs, cb, ct = L.OPENINGS[kind]
    rw, rh = L.item_size_px(kind)
    ox0, ox1 = x0 + m(cs), x0 + m(cs + w)
    oy0, oy1 = y0 + m(cb), y0 + m(cb + h)
    concrete = kind == "cellar"
    cas_id = ID_PLINTH if concrete else ID_TRIM
    # casing, bled 2 px outward so filtering at the region edge stays casing;
    # a timber casing stands proud of the wall with rounded arrises
    c.paint(x0 - 2, x0 + rw + 2, y0 - 2, y0 + rh + 2, cas_id, 1.0, 1.0, height=0.0)
    if not concrete:
        c.bevel(x0, x0 + rw, y0, y0 + rh, CASING_H, 1.0)

    if not concrete and kind != "vent":
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

    if kind in ("door_front", "door_back", "door_balcony"):
        paint_door(c, L, ox0, ox1, oy0, oy1, kind)
        return
    if kind == "vent":
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
    # mullions; the type's windows have none. A pane sits a few mm behind its
    # sash: occlusion inside the top and left bars.
    c.mul(ox0 + f, ox1 - f, oy1 - f - 1, oy1 - f, 0.82, ao=0.8)
    c.mul(ox0 + f, ox0 + f + 1, oy0 + f, oy1 - f, 0.88)


def handle_x(L, kind, x0, x1):
    """Where a door's handle is: on the pair, on the right-hand leaf's
    meeting stile; on a single leaf, near its free edge."""
    if kind == "door_balcony" and L.BALCONY_DOOR == "pair":
        return (x0 + x1) / 2.0 + m(0.07)
    return x1 - m(0.12)


def paint_door(c, L, x0, x1, y0, y1, kind):
    c.paint(x0, x1, y0, y1, ID_DOOR, 1.0, 1.0, height=0.0)
    wpx = x1 - x0
    if kind == "door_front":
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
    elif kind == "door_balcony" and L.BALCONY_DOOR == "single":
        # glazed leaf onto the balcony: one clear pane over a solid bottom
        # panel, no glazing bars, like every other window here; stiles and
        # rails proud, the bottom panel sunk and fielded
        st = m(0.11)
        rail = y0 + m(0.80)
        c.paint(x0, x1, y0, y1, height=0.012)
        c.bevel(x0 + st, x1 - st, y0 + st, rail, 0.006, 1.5)
        c.mul(x0 + st, x1 - st, y0 + st, rail, 0.97)
        c.mul(x0 + st, x1 - st, rail - 1, rail, 0.90, ao=0.75)
        gx0, gx1, gy0, gy1 = x0 + st, x1 - st, rail + st, y1 - st
        c.paint(gx0, gx1, gy0, gy1, ID_GLASS, ao=0.9, height=0.0)
        c.mul(gx0, gx1, gy1 - 1, gy1, 0.8)
    elif kind == "door_balcony":
        # a pair of glazed leaves onto the balcony, each one clear pane over
        # a solid bottom panel, no glazing bars, like every other window here
        st = m(0.09)
        mid = (x0 + x1) / 2.0
        rail = y0 + m(0.80)
        c.paint(x0, x1, y0, y1, height=0.012)
        for a, b in ((x0, mid), (mid, x1)):
            c.bevel(a + st, b - st, y0 + st, rail, 0.006, 1.5)
            c.mul(a + st, b - st, y0 + st, rail, 0.97)
            c.mul(a + st, b - st, rail - 1, rail, 0.90, ao=0.75)
            gx0, gx1, gy0, gy1 = a + st, b - st, rail + st, y1 - st
            c.paint(gx0, gx1, gy0, gy1, ID_GLASS, ao=0.9, height=0.0)
            c.mul(gx0, gx1, gy1 - 1, gy1, 0.8)
        c.mul(mid - 1, mid + 1, y0, y1, 0.80, ao=0.75)       # where the leaves meet
        c.lift(mid - 0.5, mid + 0.5, y0, y1, -0.004)
    else:
        # plank leaf, the plainer back door: V-grooves between the planks
        for xx in np.arange(x0, x1, m(0.15)):
            c.mul(xx, xx + 1, y0, y1, 0.82, ao=0.8)
            c.lift(xx, xx + 1, y0, y1, -0.003)
        c.paint(x0 + wpx * 0.32, x1 - wpx * 0.32, y0 + m(1.45), y0 + m(1.85),
                ID_GLASS, 0.86, 0.85, height=0.0)
    hx = handle_x(L, kind, x0, x1)
    c.paint(hx - 1, hx, y0 + m(0.92), y0 + m(1.10), ID_HANDLE, 0.9, height=0.015)
    c.paint(hx - 2, hx + 1, y0 + m(1.00), y0 + m(1.06), ID_HANDLE, 1.0, height=0.030)
    c.paint(x0, x1, y0, y0 + 2, ID_DOOR, 0.8, 0.7)                    # kick wear


def paint_chimney(c):
    """The stack's brick, in the catalog's module and bond (scripts/
    brickwork.py), under a sheet cap with soot below it. The region is
    top-anchored, so the courses are counted down from the cap (y_ref): the
    course under it is whole, and the cut course lands at the region's foot,
    inside the roof. One brick id; the tone repeats over the stack's 24
    whole courses. The stack is seen close, so its bricks' arrises are
    rounded (3 mm)."""
    x0, y0, w, h = CHIMNEY
    top = y0 + h
    cap = top - m(CHIMNEY_CAP)
    # up to the cap only: the joints' AO would show through it
    brickwork.paint(c, x0 - 2, x0 + w + 2, y0 - 2, cap, (ID_BRICK, None, ID_MORTAR),
                    tone_courses=24, seed=5, y_ref=cap, arris=0.003)
    c.mul(x0 - 2, x0 + w + 2, top - m(0.55), cap, 0.78)               # soot
    c.paint(x0 - 2, x0 + w + 2, cap, top + 2, ID_CAP, 1.0, height=0.020)
    c.paint(x0 - 2, x0 + w + 2, cap, cap + 1, ID_CAP, 0.8, 0.7)


def paint_corner(c):
    x0, y0, w, h = CORNER
    c.paint(x0 - 2, x0 + w + 2, y0 - 2, y0 + h + 2, ID_TRIM, 1.0, height=0.0)
    c.bevel(x0, x0 + w, y0 - 2, y0 + h + 2, CASING_H, 1.0, axes="x")
    c.mul(x0 - 2, x0 + w + 2, y0 - 2, y0 + 4, 0.92)


def paint_patches(c, L):
    spec = {"trim": (ID_TRIM, 1.0, 1.0), "soffit": (ID_TRIM, 0.88, 0.85),
            "reveal": (ID_TRIM, 0.70, 0.6), "blank": (ID_BLANK, 1.0, 0.5),
            "tread": (ID_PLINTH, 0.96, 1.0), "cap": (ID_CAP, 1.0, 1.0),
            "barge": (ID_TRIM, 0.97, 1.0),
            # soot inside the flue: blank darkened to about sRGB 34, and
            # occluded, as a narrow shaft is whatever the sun does
            "flue": (ID_BLANK, 0.45, 0.35)}
    if "deck" in L.PATCHES:
        # the balcony floor: sheet steel in the roof's colour, a shade
        # darker, as it would be dressed to match the roof it adjoins
        spec["deck"] = (ID_ROOF, 0.82, 0.9)
    atlas.paint_patches(c, L.PATCHES, spec)


def paint_deck(c):
    """Deck boards for a terrace and a balcony floor.

    The boards are 0.125 m, each with its own tone, a slight crown and a dark
    gap. A build samples the strip at one V, so each board runs the surface's
    full length unbroken. The pitch divides the atlas width, so the strip
    tiles.
    """
    p = m(BOARD)
    sy, sx, _, X = c.field(0, ATLAS, DECK_Y0 - 2, DECK_Y0 + DECK_H + 2)
    b = np.floor(X / p).astype(np.int64)
    r = X / p - b
    gap = r < 1.0 / p
    tone = 0.93 + 0.14 * atlas.hash_unit(41, b)
    c.mid[sy, sx] = ID_DECK
    c.shade[sy, sx] = tone * np.where(gap, 0.50, 1.0)
    c.ao[sy, sx] = np.where(gap, 0.6, 1.0)
    c.height[sy, sx] = np.where(gap, -0.006, 0.002 * np.sin(np.pi * r))


def paint_rail(c):
    """The railings' baluster zone, from the deck to the handrail.

    The balusters are square, on a 0.125 m pitch, in the trim colour, with dark
    gaps between them. The railing itself is solid, as CLAUDE.md asks of a
    balcony parapet; the balusters are paint and relief, 20 mm proud of the
    gaps. V is squeezed: a build maps the zone's full height onto RAIL_H rows,
    so the rows carry only a gradient, darker at the foot where the deck
    shades it and just under the handrail.
    """
    p = m(BOARD)
    sy, sx, Y, X = c.field(0, ATLAS, RAIL_Y0 - 2, RAIL_Y0 + RAIL_H + 2)
    r = (X % p) / p
    gap = r >= 5.0 / 8.0
    t = np.clip((Y - RAIL_Y0) / RAIL_H, 0.0, 1.0)
    top = np.where(Y >= RAIL_Y0 + RAIL_H - 1, 0.90, 1.0)
    c.mid[sy, sx] = ID_TRIM
    c.shade[sy, sx] = np.where(gap, 0.40, 1.0) * (0.84 + 0.16 * t) * top
    c.ao[sy, sx] = np.where(gap, 0.55, 0.88 + 0.12 * t)
    c.height[sy, sx] = np.where(gap, -0.020,
                                0.020 * np.clip(np.sin(np.pi * np.clip(r / (5.0 / 8.0), 0, 1)), 0, 1) ** 0.5)


def weather(c, L):
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
    rpm = L.ROOF_H / ROOF_SLOPE_LEN
    roof = (ID_ROOF,)
    y0, y1 = L.ROOF_Y0 - 2, L.ROOF_Y0 + L.ROOF_H + 2
    w.roof(0, ATLAS, L.ROOF_Y0, L.ROOF_H, ROOF_SLOPE_LEN, roof)
    w.add("D", 0, ATLAS, y0, y1, lambda Y, X, nz: 0.12 * (
        ((X % 32.0) >= 2.0) & ((X % 32.0) < 5.0)), roof)
    g = L.ROOF_Y0 + round(0.50 * rpm)
    w.add("D", 0, ATLAS, g + 4.5, g + 16.0, lambda Y, X, nz: 0.25 * nz("blotch")
          * (1.0 - (Y - g - 4.5) / 11.5), roof)
    w.add("R", 0, ATLAS, g - 3, g + 4.5, lambda Y, X, nz: 0.18 * ((X % 32.0) >= 28.0), roof)
    w.add("R", 0, ATLAS, g - 14, g - 3, lambda Y, X, nz: 0.15 * (
        ((X % 32.0) >= 29.2) & ((X % 32.0) < 30.8)) * (1.0 - (g - 3 - Y) / 11.0)
        * atlas.smoothstep(-0.5, 0.8, nz("runs")), roof)
    w.add("R", 0, ATLAS, y0, L.ROOF_Y0 + 3, lambda Y, X, nz: 0.12 * nz("speck"), roof)
    # the fascia: runs down the board from the gutter, a dirty belly
    g0 = FASC_Y0 + FASC_H - 10.0
    w.add("D", 0, ATLAS, FASC_Y0 - 2, g0, 0.06, (ID_TRIM,))
    w.runs(0, ATLAS, FASC_Y0 - 2, g0, (ID_TRIM,), 0.22, fall=6.0, lo=0.4, hi=1.6)
    w.add("D", 0, ATLAS, g0, g0 + 4, lambda Y, X, nz: 0.10 + 0.12 * nz("blotch"), (ID_METAL,))
    # openings: sills, heads and bottom rails; doors' handles and feet
    for kind, (wd, h, cs, cb, ct) in L.OPENINGS.items():
        if kind in ("cellar", "vent"):
            continue
        x0, yb = L.ITEM_ORIGIN[kind]
        rw, rh = L.item_size_px(kind)
        ox0, ox1 = x0 + m(cs), x0 + m(cs + wd)
        oy0, oy1 = yb + m(cb), yb + m(cb + h)
        if kind.startswith("door"):
            w.door(ox0, ox1, oy0, oy1, (ID_DOOR,),
                   handle=(handle_x(L, kind, ox0, ox1), oy0 + m(1.03)))
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


def paint(L, ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_s1(c)
    paint_s2(c, L)
    paint_roof(c, L)
    paint_fascia(c)
    for kind in L.OPENINGS:
        paint_opening(c, L, kind)
    paint_chimney(c)
    paint_corner(c)
    paint_patches(c, L)
    if L.STRIPS:
        paint_deck(c)
        paint_rail(c)
    c.check_bands(L.BAND_IDS)
    L.check_regions()

    # Weathering. Every field is periodic, so the bands still wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    wood = np.isin(c.mid, (ID_WALL, ID_TRIM, ID_DOOR, ID_DECK))
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
    weather(c, L)
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


def export(L, out_dir, ss=atlas.SS):
    """Paint once; write the ORM, normal and emission maps and an albedo per
    variant into *out_dir*, named for the house."""
    c = paint(L, ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.012)
    c.weather.dust(cav, (ID_WALL,))                  # along the laps
    # timber and concrete vary in roughness; painted steel stays even
    rough = 0.04 * atlas.noise(c, 13, 20.0) * ~np.isin(c.mid, PAINTED_STEEL)
    path = os.path.join(out_dir, L.ASSET)
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


# ================================================================ geometry
# Everything below runs inside Blender only.

# ------------------------------------------------------------------ massing
EPS = 1e-6
TAN = 1.0                        # 45 degree roof, the type's defining pitch
ROOF_T = FASC_H / PPM            # slab's vertical thickness = fascia height
EAVE_OV = 0.45                   # eave overhang, the catalog default
RAKE_OV = 0.35                   # gable (rake) overhang
SLOPE_F = math.sqrt(1.0 + TAN * TAN)            # slope length per horizontal metre
# Sills sit at 1.5 m: 0.8 m above the 0.7 m floor, the floor itself being
# carried by the cellar plinth. The attic storey is lit from the gables, one
# window per end: the standard 1.80 x 1.40 m "wide" unit, centred under the
# ridge at ATTIC_SILL. It is the same sash the living room has, which is how
# the standardised type worked, and it is why no separate attic region is
# painted in the atlas.
GF, ATTIC_SILL = 1.50, 4.65
# The chimney is open at the top: a half-brick shell round one flue, which
# drops FLUE_DEPTH to a soot floor. A house stands its top 0.95 m over the
# ridge, so the floor stays clear of the roof slab.
FLUE_WALL = 0.12
FLUE_DEPTH = 0.80
# Steps: landing just under the threshold, then three risers of ~0.17 m.
STEP_PROFILE = [(-0.05, 0.0), (-0.05, 0.68), (0.90, 0.68), (0.90, 0.51),
                (1.18, 0.51), (1.18, 0.34), (1.46, 0.34), (1.46, 0.17),
                (1.74, 0.17), (1.74, 0.0)]
# LOD3 keeps the steps' footprint as a ramp, so every tier has the same extents
# and therefore the same pivot.
STEP_PROFILE_LOW = [(-0.05, 0.0), (-0.05, 0.68), (0.90, 0.68), (1.74, 0.0)]
# Lean-to canopy over the back door, the type's usual kitchen entrance: 0.8 m
# out from the wall, a shallow fall, sitting clear above the door casing. It
# clears the 0.25 m test as a covered entrance, and is silhouette, so it
# survives to LOD2.
CANOPY_OUT = 0.80
CANOPY_Z = (3.30, 3.14)                           # top at the wall, top at the edge
CANOPY_T = 0.12

# ------------------------------------------------------------- tier policy
# How an opening is built at each tier, LOD0..LOD3:
#   ring  - the casing is a ring of faces on the wall, the opening inside it
#           recessed with reveals and closed by its glass or door plane.
#   cut   - one recess the size of the casing; the casing is painted on the
#           recessed plane. Half the wall breakpoints for the same shadow.
#   flush - the casing rect as a flat quad in the wall.
#   None  - dropped.
# The consumer switches by screen size, at about 1.8, 4 and 8 times a house's
# largest dimension (25 / 55 / 110 m on these): every opening is kept to the
# last tier, the small ones as flush quads (about 8 triangles each with the
# hole they leave), so the cellar lights and the gable vent, 9 x 6 px at the
# LOD1/LOD2 switch, and the bath and porch windows, 5-7 px at LOD2/LOD3, stay
# by day and stay lit at night.
ITEM_MODES = {
    "cellar": ("ring", "flush", "flush", "flush"),
    "vent": ("flush", "flush", "flush", "flush"),
}
ITEM_MODES_DEFAULT = ("ring", "cut", "flush", "flush")
# A house's own exceptions to ITEM_MODES, kind -> modes (none at present).
ITEM_MODES_HOUSE = {}
# A house's own downpipe tiers, replacing downpipes.MODES, where its LOD3
# cannot keep every small opening under the 500 ceiling. The gable entry's
# terrace, railings and balcony leave its LOD3 30 triangles, and its five
# small openings take 44: its two pipes (26) go at LOD3 instead, where a
# 0.1 m pipe is 0.6 px beside its corner board at the switch (about 120 m),
# while a gable vent's pale louvre is a 3.7 x 2.8 px spot on the red gable.
DOWNPIPE_MODES_HOUSE = {
    "rintamamiestalo_gable_entry": ((8, True), (4, True), (4, False), (0, False)),
}
CANOPY_LAST = 2          # the last tier with the back-door canopy
RAMP_FROM = 3            # from this tier each flight of steps is its ramp
# How each tier keeps the handrails (scripts/handrails.py): "union", joined to
# the steps through the build's union; "lean", the same rail and posts as
# separate solids appended after the weld (60 triangles a flight), which
# keeps the rail's line over the steps at the LOD1/LOD2 switch; None, gone:
# at the LOD2/LOD3 switch a 45 mm rail is a third of a pixel.
RAILS = ("union", "union", "lean", None)
# From this tier the weld is followed by a dissolve of coplanar faces, which
# recovers the cost of the persistent corner paint from the boolean's
# subdivisions, keeping UV and material seams and every architectural edge.
DISSOLVE_FROM = 2

# The reference lit factor for previews (asset_build.Asset's tint): the
# warm-white lamplight the newer assets use, not asset_build's older orange
# default.
TINT = (1.0, 0.88, 0.72)


def item_mode(kind, level, house=None):
    """How opening *kind* is built at *level* on the house named *house*."""
    modes = (ITEM_MODES_HOUSE.get(house, {}).get(kind)
             or ITEM_MODES.get(kind, ITEM_MODES_DEFAULT))
    return modes[level]


class Peak:
    """A wall's top as the porch and side-entry houses give it: level at
    *top* and, with *apex*, rising at TAN to it midway, z(s) = top +
    min(s, L - s) * TAN. An (s, z) profile interpolates its points instead,
    which agrees to rounding but not bit for bit, and the exact boolean
    sees the difference; so each house keeps the form it was built with."""

    def __init__(self, top, apex=None):
        self.top, self.apex = top, apex

    def rake(self, length):
        if self.apex is None:
            return lambda s: self.top
        return lambda s: self.top + min(s, length - s) * TAN

    def points(self, length):
        mid = [] if self.apex is None else [(length / 2.0, self.apex)]
        return [(0.0, self.top)] + mid + [(length, self.top)]


def wall_profile(top, length):
    """A wall's top edge as (s, z) points: a level height, a list of points
    (a gable, a dormer's stepped side) or a Peak."""
    if isinstance(top, Peak):
        return top.points(length)
    return [(0.0, top), (length, top)] if isinstance(top, float) else top


def profile_z(prof, s):
    """Height of a wall's top edge at *s*, from its (s, z) profile."""
    for (sa, za), (sb, zb) in zip(prof, prof[1:]):
        if s <= sb + EPS:
            return za if sb - sa < EPS else za + (zb - za) * (s - sa) / (sb - sa)
    return prof[-1][1]


def rake_of(top, length):
    """The function s -> height of a wall's top edge."""
    if isinstance(top, Peak):
        return top.rake(length)
    prof = wall_profile(top, length)
    return lambda s: profile_z(prof, s)


# One wall of a solid, walked counter-clockwise seen from above so its
# outward face is on the right. top: see wall_profile(). items: openings as
# (kind, s, sill z), s the centre measured along the wall from p0. corners:
# the boards at the start and end, True from the plinth up, False for none,
# or the height a board starts at. bands: the Layout's EAVE_BANDS or
# GABLE_BANDS, or a house's own stack. board_to: where boards stop under a
# belt board that runs over them.
Wall = namedtuple("Wall", "name p0 p1 top items corners bands board_to")
Wall.__new__.__defaults__ = (None,)

# A flight of steps for Kit.tier(): steps()' arguments, the ramp it becomes
# from RAMP_FROM, and its object's name.
Steps = namedtuple("Steps", "name a0 a1 wall outward profile low axis")
Steps.__new__.__defaults__ = (STEP_PROFILE, STEP_PROFILE_LOW, "y")


class Kit:
    """The build half for one house: its Asset, and the family's solids and
    checks on its Layout. Imports bpy and the Blender-side scripts."""

    def __init__(self, layout, here):
        import functools
        import asset_build
        import shell_build
        asset_build.check_toolchain()
        self.L = layout
        self.SB = shell_build
        self.asset = asset_build.Asset(layout.ASSET, here, VARIANTS, DEFAULT_VARIANT, tint=TINT)
        self.Builder = functools.partial(shell_build.Builder, ATLAS)

    # -------------------------------------------------------- UV mappings
    # Each returns (u, v) in atlas pixels for a vertex position. Walls are
    # shell_build.InwardFrame: the third coordinate is depth into the wall.
    @staticmethod
    def uv_band(fr, y0, z_ref, u_off):
        return lambda co: ((fr.s_of(co) + u_off) * PPM, y0 + (co.z - z_ref) * PPM)

    def uv_item(self, fr, kind, s_left, z_bot):
        """Planar, at true scale. Recessed faces sit behind the wall only along
        its normal, so they sample the same texels as if they were flush."""
        x0, y0 = self.L.ITEM_ORIGIN[kind]
        return self.SB.uv_region(fr, (x0, y0, 0, 0), s_left, z_bot, PPM)

    @staticmethod
    def uv_strip(fr, rect, a, b, z0, z1):
        x0, y0, w, h = rect
        return lambda co: (x0 + (fr.s_of(co) - a) / (b - a) * w,
                           y0 + min(max((co.z - z0) / (z1 - z0), 0.0), 1.0) * h)

    def uv_patch(self, name):
        return self.SB.uv_patch(self.L.PATCHES[name])

    # -------------------------------------------------------------- walls
    def item_rects(self, kind, s, z):
        return self.SB.item_rects(self.L.OPENINGS[kind], s, z)

    def build_item(self, B, fr, kind, s, z, level):
        """Faces for one opening; returns the hole it needs in its wall region."""
        SB = self.SB
        mode = item_mode(kind, level, self.L.ASSET)
        (ol, orr, ob, ot), (il, ir, ib, it) = self.item_rects(kind, s, z)
        fn = self.uv_item(fr, kind, ol, ob)
        depth = REVEAL_DEPTH.get(kind, REVEAL_DEFAULT)
        rev = self.uv_patch("tread" if kind == "cellar" else "reveal")
        o = SB.rect_poly((ol, orr, ob, ot))
        if mode == "flush":
            B.face([fr.P(*p) for p in o], fn)
            return o
        if mode == "cut":
            SB.recess(B, fr, o, 0.0, depth, fn, rev)
            return o
        i = SB.rect_poly((il, ir, ib, it))
        for k in range(4):
            B.face([fr.P(*o[k]), fr.P(*o[(k + 1) % 4]),
                    fr.P(*i[(k + 1) % 4]), fr.P(*i[k])], fn)
        SB.recess(B, fr, i, 0.0, depth, fn, rev)
        if abs(ob - ib) < EPS:
            # A door has no bottom casing, so the threshold edge lies on the hole's
            # own bottom edge; the hole has to carry those two corners too.
            return [(ol, ob), (il, ib), (ir, ib), (orr, ob), (orr, ot), (ol, ot)]
        return o

    def build_wall(self, B, fr, top, bands, edge_z, corners, items, u_off, level,
                   board_to=None):
        """One elevation: corner-board columns, then siding regions with holes.

        *top* is the wall's top edge (wall_profile()): level for an eave
        wall, peaked for a gable, stepped for a dormer's side. *bands* stacks
        the siding regions from the ground up. *edge_z* is the set of heights
        every panel end of this solid carries, so two walls meeting at a
        corner meet on exactly the same vertices. Corner boards stop at
        *board_to* when a belt board runs over them.
        """
        L = self.L
        Lw = fr.L
        prof = wall_profile(top, Lw)
        rake = rake_of(top, Lw)
        # Contrasting paint survives every tier; these are flush UV strips.
        c0, c1 = corners
        s0 = L.CW if c0 else 0.0
        s1 = Lw - L.CW if c1 else Lw

        def ez(s, end):
            # every level under this end of the wall's top, then the top at s
            return sorted({e for e in edge_z if e < rake(end) - EPS} | {rake(s)})

        regions = [(z0, self.uv_band(fr, L.S1_Y0 if band == "S1" else L.S2_Y0, zref, u_off))
                   for z0, band, zref in bands]

        def band_at(z):
            fn = regions[0][1]
            for z0, f in regions:
                if z >= z0 - EPS:
                    fn = f
            return fn

        for a, b, end, has in ((0.0, L.CW, 0.0, c0), (Lw - L.CW, Lw, Lw, c1)):
            if not has:
                continue
            # True: a board from the plinth up; a height: the board starts there
            z_from = L.Z_FLASH if has is True else has
            strip = self.uv_strip(fr, L.CORNER, a, b, L.Z_FLASH, max(rake(a), rake(b)))
            lo = [e for e in edge_z if e < rake(end) - EPS]
            for k, za in enumerate(lo):
                if k + 1 < len(lo):
                    zb = lo[k + 1]
                    poly = [(a, za), (b, za), (b, zb), (a, zb)]
                else:
                    zb = rake(end)
                    poly = [(a, za), (b, za), (b, rake(b)), (a, rake(a))]
                if zb <= z_from + EPS or (board_to is not None and za >= board_to - EPS):
                    fn = band_at(za)                 # plinth or flush wall below, belt above
                else:
                    fn = strip
                B.face([fr.P(s, z) for s, z in poly], fn)

        rect = {}
        for kind, s, z in items:
            if item_mode(kind, level, L.ASSET):
                rect[(kind, s, z)] = self.item_rects(kind, s, z)[0]

        splits = [z0 for z0, _, _ in bands[1:]]
        bounds = [0.0] + splits + [None]
        peaks = [(s, z) for s, z in reversed(prof) if s0 + EPS < s < s1 - EPS]
        if splits and any(z < splits[-1] for _, z in peaks):
            raise ValueError("a %.1f m wall's top dips under its last band change" % Lw)
        left, right = ez(s0, 0.0), ez(s1, Lw)
        placed = 0
        for i in range(len(bounds) - 1):
            zlo, zhi = bounds[i], bounds[i + 1]
            last = zhi is None

            def within(z):
                return z > zlo + EPS and (last or z < zhi - EPS)

            outline = [(s0, zlo), (s1, zlo)] + [(s1, z) for z in right if within(z)]
            outline += peaks if last else [(s1, zhi), (s0, zhi)]
            outline += [(s0, z) for z in reversed(left) if within(z)]
            its = [(kind, s, z) for (kind, s, z), r in rect.items()
                   if r[2] > zlo - EPS and (last or r[3] < zhi + EPS)]
            holes = [self.build_item(B, fr, kind, s, z, level) for kind, s, z in its]
            placed += len(its)
            self.SB.fill_region(B, fr, outline, holes, regions[i][1])
        if placed != len(rect):
            raise ValueError("an opening straddles a band change on a %.1f m wall" % Lw)

    def ring(self, B, walls, edge, level, u_off):
        """Build a solid's Walls; *u_off* offsets each into the tiling
        siding band by name, so butt joints differ wall to wall."""
        for w in walls:
            fr = self.SB.InwardFrame(w.p0, w.p1)
            self.build_wall(B, fr, w.top, w.bands, sorted(set(edge)), w.corners, w.items,
                            u_off[w.name], level, w.board_to)

    def body(self, level, walls, edge, u_off, ridges=()):
        """A wall ring capped by a floor and a roof-shaped lid split along
        each pair of points in *ridges* (a ridge, a kink):
        shell_build.close_solid()."""
        B = self.Builder()
        self.ring(B, walls, edge, level, u_off)
        self.SB.close_solid(B, self.uv_patch("blank"), ridges=ridges)
        return B

    # -------------------------------------------------------------- roofs
    def slab(self, axis, c, section, kinds, a0, a1, fns):
        """A closed slab: *section*, (across, z) points, extruded along *axis*
        from a0 to a1. Each section edge takes the UV function its kind names;
        the two end caps are the barge boards."""
        B = self.Builder()

        def W(a, p, z):
            return (a, c + p, z) if axis == "x" else (c + p, a, z)

        n = len(section)
        for k in range(n):
            (p0, z0_), (p1, z1_) = section[k], section[(k + 1) % n]
            B.face([W(a0, p0, z0_), W(a0, p1, z1_), W(a1, p1, z1_), W(a1, p0, z0_)],
                   fns[kinds[k]])
        barge = self.uv_patch("barge")
        B.face([W(a0, p, z) for p, z in section], barge)
        B.face([W(a1, p, z) for p, z in reversed(section)], barge)
        return B

    def gable_slab(self, axis, c, half_w, z_eave, over, a0, a1, cut=None):
        """A gable roof as one closed slab: a chevron section extruded along
        the ridge.

        The section's underside meets the wall face at *z_eave*, so once the
        slab is unioned with the walls the part outside them is the soffit and
        the part inside disappears. The vertical ends of the section are the
        fascias; the two chevron end caps are the barge boards over the
        gables. With *cut*, the front slope stops at that distance across from
        the ridge (negative, on the front) in a vertical face that has to end
        up buried, as it does inside a dormer.
        """
        L = self.L
        pe = half_w + over
        z0 = z_eave + ROOF_T + half_w * TAN
        zt = z0 - pe * TAN
        if cut is None:
            sec = [(-pe, zt - ROOF_T), (-pe, zt), (0.0, z0), (pe, zt),
                   (pe, zt - ROOF_T), (0.0, z0 - ROOF_T)]
            kinds = ("fascia", "slope", "slope", "fascia", "soffit", "soffit")
        else:
            zc = z0 + cut * TAN
            sec = [(cut, zc - ROOF_T), (cut, zc), (0.0, z0), (pe, zt),
                   (pe, zt - ROOF_T), (0.0, z0 - ROOF_T)]
            kinds = ("cut", "slope", "slope", "fascia", "soffit", "soffit")

        def along(co):
            return co.x if axis == "x" else co.y

        def across(co):
            return (co.y if axis == "x" else co.x) - c

        def slope_uv(co):
            d = (pe - abs(across(co))) * SLOPE_F
            return ((along(co) + 16.0) * PPM, L.ROOF_Y0 + d * L.ROOF_RPM)

        def fascia_uv(co):
            return ((along(co) + 16.0) * PPM, L.FASC_Y0 + (co.z - (zt - ROOF_T)) * PPM)

        fns = {"fascia": fascia_uv, "slope": slope_uv, "soffit": self.uv_patch("soffit"),
               "cut": self.uv_patch("blank")}
        return self.slab(axis, c, sec, kinds, a0, a1, fns)

    # ------------------------------------------------------------ chimney
    def chimney(self, spec):
        """The stack, *spec* (x0, x1, y0, y1, z bottom, z top): brick sides
        from inside the roof slab up to a capped rim round one open flue, sunk
        FLUE_DEPTH and lined and floored in soot. Every tier keeps the
        recess: painted flush, the soot lies in the sun and reads as dark
        grey, barely apart from the cap, where the shaded shaft reads black.

        Not asset_build.open_stack(): each side here centres its own width
        on the brick region (one UV function per face, which open_stack's
        single *side* function cannot give at the shared corners), and the
        faces are made sides-and-rims first, then the lining."""
        x0, x1, y0, y1, zb, zt = spec
        B = self.Builder()
        cx0, cy0, cw, ch = CHIMNEY

        def side(a, b, z0, z1, fn=None):
            # a -> b along the face, left to right seen from the side it faces
            ax, ay = a
            bx, by = b
            length = math.hypot(bx - ax, by - ay)

            def brick(co):
                s = math.hypot(co.x - ax, co.y - ay)
                return (cx0 + (cw - length * PPM) / 2.0 + s * PPM, cy0 + ch - (zt - co.z) * PPM)
            B.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], fn or brick)

        w = FLUE_WALL
        ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        flue = [(x0 + w, y0 + w), (x1 - w, y0 + w), (x1 - w, y1 - w), (x0 + w, y1 - w)]
        cap, soot = self.uv_patch("cap"), self.uv_patch("flue")
        for k in range(4):
            side(ring[k], ring[(k + 1) % 4], zb, zt)
            B.face([ring[k] + (zt,), ring[(k + 1) % 4] + (zt,),
                    flue[(k + 1) % 4] + (zt,), flue[k] + (zt,)], cap)
        zf = zt - FLUE_DEPTH
        # walked the other way round, so the lining faces into the flue
        for k in range(4):
            side(flue[(k + 1) % 4], flue[k], zf, zt, soot)
        B.face([(x, y, zf) for x, y in flue], soot)
        B.face([(x, y, zb) for x, y in reversed(ring)], self.uv_patch("blank"))
        return B

    # ------------------------------------------------- canopy and steps
    def canopy(self, x_range, wall_y):
        """The back-door canopy over x_range on the rear wall at y = *wall_y*
        (facing +Y): a thin sloped slab with its back buried in the wall. Top
        samples the roof band, underside the soffit patch, edges the barge
        patch."""
        L = self.L
        B = self.Builder()
        x0, x1 = x_range
        zw, ze = CANOPY_Z
        fall = (zw - ze) / CANOPY_OUT
        back = -0.10                                   # into the wall

        def top(d):
            return zw - fall * d

        sec = [(back, top(back)), (CANOPY_OUT, ze), (CANOPY_OUT, ze - CANOPY_T),
               (back, top(back) - CANOPY_T)]
        slope_len = math.hypot(CANOPY_OUT, zw - ze)

        def W(x, d, z):
            return (x, wall_y + d, z)

        def top_uv(co):
            d = (CANOPY_OUT - (co.y - wall_y)) * slope_len / CANOPY_OUT
            return ((co.x + 16.0) * PPM, L.ROOF_Y0 + d * L.ROOF_RPM)

        fns = (top_uv, self.uv_patch("barge"), self.uv_patch("soffit"), self.uv_patch("blank"))
        for k in range(4):
            (d0, z0), (d1, z1) = sec[k], sec[(k + 1) % 4]
            B.face([W(x0, d0, z0), W(x0, d1, z1), W(x1, d1, z1), W(x1, d0, z0)], fns[k])
        B.face([W(x0, d, z) for d, z in sec], self.uv_patch("barge"))
        B.face([W(x1, d, z) for d, z in reversed(sec)], self.uv_patch("barge"))
        return B

    def steps(self, a0, a1, wall, outward, profile, axis="y"):
        """A flight of steps: *profile* is (distance out from the wall, z),
        extruded across a0..a1. *axis* is the way the flight runs: "y" off a
        front or rear wall at y = *wall*, "x" off a side wall at x = *wall*. Its
        back is buried in the wall it serves."""
        L = self.L
        B = self.Builder()

        def W(a, d, z):
            return (a, wall + outward * d, z) if axis == "y" else (wall + outward * d, a, z)

        def across(co):
            return co.x if axis == "y" else co.y

        def out(co):
            return ((co.y if axis == "y" else co.x) - wall) * outward

        # risers and cheeks read the plinth's concrete in S1: risers along the
        # flight's width, cheeks along its run
        def riser_uv(co):
            return ((across(co) + 11.0) * PPM, L.S1_Y0 + co.z * PPM)

        def cheek_uv(co):
            return ((out(co) + 11.0) * PPM, L.S1_Y0 + co.z * PPM)

        n = len(profile)
        for k in range(n):
            (d0, z0), (d1, z1) = profile[k], profile[(k + 1) % n]
            flat = abs(z1 - z0) < EPS
            fn = self.uv_patch("tread") if flat and z0 > EPS else (
                self.uv_patch("blank") if flat else riser_uv)
            B.face([W(a0, d0, z0), W(a1, d0, z0), W(a1, d1, z1), W(a0, d1, z1)], fn)
        B.face([W(a0, d, z) for d, z in profile], cheek_uv)
        B.face([W(a1, d, z) for d, z in reversed(profile)], cheek_uv)
        return B

    # --------------------------------------------------------------- tier
    def tier(self, level, base, parts, flights, canopy, downpipes, roof_kit, handrails,
             kit_extents=False):
        """One tier as an object named <asset>_LOD<level>: the house's own
        solids (*base* and *parts*, objects in union order) with what every
        house adds after them, in this order: the back-door canopy
        (*canopy*: (x range, rear wall y)) to CANOPY_LAST, each of *flights*
        (Steps), the downpipes and the roof kit, each at its own script's
        tier, and the handrails as RAILS says; then the union, the weld,
        the dissolve from DISSOLVE_FROM. *kit_extents* is for a house whose
        wall ladder sets its extents: where the kit goes, its bare rails are
        appended after the weld and the dissolve, whose greedy passes the
        extra faces would otherwise reorder (roof_safety.append()); so are
        lean handrails."""
        import copy
        import bmesh
        import downpipes as DP
        import handrails as HR
        import roof_safety as RS
        from asset_build import to_object, union
        if level <= CANOPY_LAST:
            parts.append(to_object(self.canopy(*canopy), "tmp_canopy"))
        for f in flights:
            prof = f.low if level >= RAMP_FROM else f.profile
            parts.append(to_object(self.steps(f.a0, f.a1, f.wall, f.outward, prof, axis=f.axis),
                                   f.name))
        pipe_modes = DOWNPIPE_MODES_HOUSE.get(self.L.ASSET, DP.MODES)
        parts += [to_object(B, name) for B, name in
                  DP.solids(downpipes, *pipe_modes[level], PIPE_STRIP, ATLAS)]
        kit = RS.solids(roof_kit, level, RS.Paint(ATLAS, strip=PIPE_STRIP),
                        extents=kit_extents)
        bare = kit_extents and RS.MODES[level][0] is None    # the rails alone, clear of all
        parts += [] if bare else [to_object(B, name) for B, name in kit]
        rails = RAILS[level]
        every = (True,) * 4
        if rails == "union":
            parts += [to_object(B, name) for B, name in
                      HR.solids(handrails, level, RS.Paint(ATLAS, strip=PIPE_STRIP), every)]
        obj = union(base, parts)
        obj.name = "{}_LOD{}".format(self.L.ASSET, level)
        obj.data.name = obj.name + "_mesh"

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        if level >= DISSOLVE_FROM:
            # 0.001 radians tolerates float noise on nominally planar faces.
            bmesh.ops.dissolve_limit(
                bm, angle_limit=0.001, verts=bm.verts[:], edges=bm.edges[:],
                delimit={'UV', 'MATERIAL'})
        bm.to_mesh(obj.data)
        bm.free()
        if bare:
            RS.append(obj, kit)
        if rails == "lean":
            lean = []
            for f in handrails:
                f = copy.copy(f)
                f.lean = True
                # a rail set on the flight's edge (inset 0) runs into the
                # railing it continues; lean, it must clear it, so it moves
                # in by half its width and two gaps, 2.6 cm
                f.inset = max(f.inset, HR.RAIL / 2.0 + 2.0 * RS.LEAN_GAP)
                lean.append(f)
            RS.append(obj, HR.solids(lean, level, RS.Paint(ATLAS, strip=PIPE_STRIP), every),
                      check=True)
        return obj

    # ------------------------------------------------------------- checks
    def apex_problems(self, z_apex):
        if z_apex - self.L.Z_BELT > self.L.S2_SPAN:
            return ["gable apex %.2f is above the S2 band's %.2f" % (z_apex, self.L.S2_TOP)]
        return []

    def slope_problems(self, half):
        """The main roof's slope, over a half-width *half*, against the
        length the roof band is painted for."""
        slope = (half + EAVE_OV) * SLOPE_F
        if abs(slope - ROOF_SLOPE_LEN) > 1e-3:
            return ["main slope is %.3f m, atlas assumes %.3f" % (slope, ROOF_SLOPE_LEN)]
        return []

    def opening_problems(self, walls, open_top=()):
        """Openings colliding, clipping their wall's top (the soffit's
        underside, or the wall's own top where its name is in *open_top*: a
        parapet) or a corner board, or straddling a band change or the
        plinth top."""
        L = self.L
        problems = []
        gap = 0.05
        for w in walls:
            fr = self.SB.InwardFrame(w.p0, w.p1)
            rake = rake_of(w.top, fr.L)
            c0, c1 = w.corners
            splits = [z0 for z0, _, _ in w.bands[1:]]
            rects = [(k, self.item_rects(k, s, z)[0]) for k, s, z in w.items]
            for k, (l, r, b, t) in rects:
                lo = (L.CW if c0 else 0.0) + gap
                hi = fr.L - (L.CW if c1 else 0.0) - gap
                if l < lo or r > hi:
                    problems.append("%s: %s at s %.2f..%.2f runs into a corner"
                                    % (w.name, k, l, r))
                for s in (l, r):
                    vis = rake(s) - (0.0 if w.name in open_top else L.Z_WALL_TOP - L.Z_EAVE)
                    if t > vis - gap:
                        problems.append("%s: %s top %.2f is under the roof (%.2f)"
                                        % (w.name, k, t, vis))
                for sp in splits:
                    if b < sp < t:
                        problems.append("%s: %s straddles the band change at %.2f"
                                        % (w.name, k, sp))
                if b < L.Z_FLASH < t and not k.startswith("door"):
                    problems.append("%s: %s straddles the plinth top" % (w.name, k))
            for i in range(len(rects)):
                for j in range(i + 1, len(rects)):
                    if self.SB.overlap(rects[i][1], rects[j][1], gap):
                        problems.append("%s: %s and %s overlap"
                                        % (w.name, rects[i][0], rects[j][0]))
        return problems

    def canopy_problems(self, wall, door, x_range):
        """The back canopy over x_range against the back door's casing rect
        *door* on *wall*, a rear wall walked toward -X (x = p0.x - s)."""
        problems = []
        cx = sorted(wall.p0[0] - v for v in door[:2])
        if not (x_range[0] < cx[0] and cx[1] < x_range[1]):
            problems.append("back canopy does not cover the door casing")
        if CANOPY_Z[0] - CANOPY_T < door[3] + 0.10:
            problems.append("back canopy meets the wall on top of the door casing")
        if CANOPY_Z[1] - CANOPY_T - STEP_PROFILE[2][1] < 2.2:
            problems.append("back canopy's edge is below head height over the landing")
        return problems

    @staticmethod
    def flue_problems(spec, z_ridge):
        if spec[5] - FLUE_DEPTH < z_ridge + 0.05:
            return ["the flue's floor is down in the roof slab"]
        return []

    @staticmethod
    def rear_walkway_problems(walk, spec, hx, hy):
        """A walkway along the rear slope (s = hx - x) running the stack's
        width, its upslope edge just behind it."""
        problems = []
        if walk.s0 > hx - spec[1] or walk.s1 < hx - spec[0]:
            problems.append("the walkway does not run the stack's width")
        y_hi = hy + walk.out_hi                          # its upslope edge, in y
        if not spec[3] + 0.02 < y_hi < spec[3] + 0.30:
            problems.append("the walkway's edge is not just behind the stack")
        return problems

    # -------------------------------------------------------------- facts
    def door(self, walls, door_id, kind, wall, item, main=False):
        """A door in the facts sidecar (model_facts.wall_door()): opening
        *item* on the Wall named *wall* in *walls* (name -> Wall)."""
        import model_facts
        w = walls[wall]
        s, z = next((s, z) for k, s, z in w.items if k == item)
        wd, h = self.L.OPENINGS[item][:2]
        return model_facts.wall_door(door_id, kind, w.p0, w.p1, s, z, wd, h, main)

    # ------------------------------------------------------------ previews
    def render_views(self, out_dir, level=0, res=(1400, 1000)):
        """The six working views CLAUDE.md asks for before export
        (shell_build.render_views()): four orthographic elevations, a plan
        from above, and a raised three-quarter aerial off the front corner.
        Working views only, not committed."""
        return self.SB.render_views(self.asset, out_dir, level, res, distance=60.0)


if __name__ == "__main__":
    print(__doc__)
