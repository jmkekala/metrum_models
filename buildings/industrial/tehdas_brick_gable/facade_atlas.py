# SPDX-License-Identifier: GPL-3.0-or-later

"""Albedo, ORM, normal and emission atlas, and shared layout, for
tehdas_brick_gable.

Run standalone to bake the textures into export/:

    python3 facade_atlas.py export

build.py imports this module for every number the mesh and the atlas share --
storey heights, band rows, opening sizes, region rectangles -- so a change here
cannot leave the UVs pointing at the wrong artwork.

The atlas is a trim sheet. Five bands run the full width and tile in U:

    y    0 ..  456   BRICK   z 0 .. 7.125 m: concrete plinth, then brick
    y  462 ..  552   WINDOW  ribbon windows, sill to head, in 2 m cells
    y  558 ..  630   ROOF    profiled steel sheet, V stretched up the slope
    y  636 ..  652   EAVE    the eave fascia with its gutter
    y  658 ..  682   FLASH   sheet flashing: wing fascias, canopy edges
    y  690 .. 1022   unique  doors, the stair glazing, the loading door, the
                             pillar, the felt deck, the vent pipes, LOD3's
                             wing lids, window bay and stair column, patches

The brick band stops at the wall head. The two gable triangles above Z_GABLE
sample the same band GABLE_SHIFT metres lower, a whole number of courses, so
the bond runs on across the line without spending another 150 rows on brick.

Every ribbon window samples the one WINDOW band from its start: a 2 m cell is
a fixed light and an opening casement, the cells alternate so a 4 m window
has a casement at each end, and a window is a whole number of cells. The
singular things -- the entrance screen, the doors, the stair glazing, the
loading door -- get regions of their own.

Rasterising is scripts/atlas.py's: a canvas supersampled SS x SS per pixel,
with a height channel the normal map is derived from (numpy and scipy; Pillow
to save). Dirt, algae, rust and faded paint are scripts/weathering.py's
fields: weather() below says where they go on this layout, and each variant
resolves them against its own colours.
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

ASSET = "tehdas_brick_gable"
ATLAS = 1024
PPM = 64.0
PAD = 2                 # rows each band paints beyond its own edge

# ------------------------------------------------------------------ plan
# Front (-Y) is the long street elevation. The main block is 42 x 12 m; its
# ground storey stops at PORCH_X, and the upper storey runs on over four
# pillars to the east gable. Wings are (x0, x1, y0, y1) at wall faces.
HX, HY = 21.0, 6.0
PORCH_X = 18.0
FRONT_WING = (9.0, 17.4, -11.0, -HY)
BACK_WING = (6.0, 17.4, HY, 17.0)
WING_BURY = 0.2         # wing walls and slabs run this far into the block

# ------------------------------------------------------------ vertical layout
# Metres above ground. Every height is a whole number of texels at 64 px/m,
# so a band's rows and the metres they stand for never drift apart.
Z_PLINTH = 0.375        # 24 px; cast concrete base under every wall
Z_STOREY = 3.3125       # 212 px; the upper floor
Z_SILL = 1.0            # 64 px; ground-storey window sills
WIN_H = 1.40625         # 90 px; every ribbon window, sill to head
Z_SILL_UP = Z_SILL + Z_STOREY                   # 4.3125, upper-storey sills
Z_LEAF = 2.125          # 136 px; door-leaf head
Z_DOOR = 2.6875         # 172 px; glazed doors' opening head, transom above
Z_PORCH = 3.0           # 192 px; soffit under the upper storey at the pillars
Z_EAVE = 7.0            # 448 px; roof underside at the side-wall face
WALL_INTO_ROOF = 0.125  # walls run this far into the roof slab
Z_WALL_TOP = Z_EAVE + WALL_INTO_ROOF             # 7.125, 456 px
GABLE_SHIFT = 3.75      # 240 px = 48 courses; see the module docstring
Z_GABLE = 6.75          # 432 px; the gable walls change rows here, a quarter
                        # metre under the soffit: a split line on the roof's
                        # own underside left the exact boolean a corner it
                        # resolved into a dozen coincident vertices

# the gable roof
TAN = 0.36              # 19.8 degrees
ROOF_T = 0.25           # slab's vertical thickness = the fascia's height
EAVE_OUT = 0.45         # eave overhang, horizontal
RAKE_OUT = 0.30         # rake overhang at the gables
SLOPE_F = float(np.sqrt(1.0 + TAN * TAN))
SLOPE_LEN = (HY + EAVE_OUT) * SLOPE_F           # eave edge to ridge, 6.855 m

# the flat-roofed wings: walls up into a slab with a low parapet round a deck
Z_WING_SOF = 3.5        # slab underside, and the fascia's foot
Z_WING_WALL = 3.625     # wing walls run up into the slab
Z_DECK = 3.75           # the felt deck
Z_COPE = 3.875          # the parapet's coping, 0.125 m above the deck
WING_OVER = 0.125       # slab projection past the wing walls
PARAPET = 0.25          # coping width inside the wall line

# canopies over the entrance and the stair door, and the stair glazing's sill
# just above the second
Z_CAN0, Z_CAN1 = 2.8125, 3.0
Z_STAIR = 3.25

# ------------------------------------------------------------------ openings
# kind -> (width, height) of the opening in the brick, metres. Brick openings
# have no casing: the reveal is the brick itself, and the frame is set back
# REVEAL metres in it.
OPENINGS = {
    "ribbon4": (4.0, WIN_H),
    "ribbon2": (2.0, WIN_H),
    "entrance": (3.0, Z_DOOR),
    "glazed_door": (1.1875, Z_DOOR),
    "service_door": (1.125, 2.1875),
    "loading_door": (4.0, 3.75),
    "stair": (1.25, 3.25),
    # LOD3 only: one quad over a bay's two ribbon windows and the brick
    # between them, sill of the lower to just over the head of the upper
    "lod3_bay": (4.0, 4.75),
    # and the stair's door and glazing, one above the other, as one column
    "lod3_stair": (1.25, 6.5),
}
REVEAL = {"lod3_bay": 0.0, "lod3_stair": 0.0, "ribbon4": 0.20, "ribbon2": 0.20, "entrance": 0.20,
          "glazed_door": 0.20, "service_door": 0.15, "loading_door": 0.25,
          "stair": 0.20}
LOBBY_DEPTH = 1.5       # the main entrance is set back into a lobby this deep
WIN_CELL = 2.0          # 128 px; ribbon windows are whole cells

# ------------------------------------------------------------------- bands
BRICK_Y0, BRICK_H = 0, 456        # z 0 .. Z_WALL_TOP, plinth in the bottom 24
WIN_Y0, WIN_H_PX = 462, 90        # z sill .. head
ROOF_Y0, ROOF_H = 558, 72         # the slope, eave edge to ridge
EAVE_Y0, EAVE_H = 636, 16         # the eave fascia, ROOF_T tall
GUTTER_PX = 9                     # the gutter's rows, across the fascia's top
# The downpipes' sides span the middle five of them (scripts/downpipes.py)
PIPE_STRIP = (EAVE_Y0 + EAVE_H - GUTTER_PX + 2, EAVE_Y0 + EAVE_H - 2)
FLASH_Y0, FLASH_H = 658, 24       # 0.375 m of flashing
ROOF_RPM = ROOF_H / SLOPE_LEN     # roof rows per metre up the slope

COURSE = brickwork.COURSE      # brick course pitch: 5 px
BRICK_L = brickwork.BRICK_L    # stretcher: 16 px, 64 bricks per atlas width
TONE_COURSES = 48       # brick tone repeats every GABLE_SHIFT, so the gable
                        # triangles continue the same bricks across the seam

# ------------------------------------------------------------ unique regions
# (x, y, w, h) in pixels. check_regions() asserts they neither overlap nor run
# off the sheet; the metres each stands for are beside it.
UNI_Y = 690
ENTRANCE = (4, UNI_Y, 192, 172)          # 3.0 x 2.6875 m at 64 px/m
GLAZED_DOOR = (200, UNI_Y, 76, 172)      # 1.1875 x 2.6875 m
SERVICE_DOOR = (280, UNI_Y, 72, 140)     # 1.125 x 2.1875 m
LOADING_DOOR = (356, UNI_Y, 160, 150)    # 4.0 x 3.75 m at 40 px/m
STAIR = (520, UNI_Y, 80, 208)            # 1.25 x 3.25 m
PILLAR = (604, UNI_Y, 26, 200)           # 0.40625 x 3.125 m, one face
DECK = (634, UNI_Y, 116, 112)            # felt, DECK_PPM
VENT = (754, UNI_Y, 32, 96)              # a pipe's side: across x 1.5 m up
PIPE_TOP = (790, UNI_Y, 24, 24)          # a pipe's open end, planar
DECK_PPM = 10.0
PILLAR_W = 26 / PPM
# LOD3's wings are plain boxes: each lid is one quad over the whole wing,
# wall face to wall face and on into the block, painted with the coping's
# light edge on its three open sides. 8 px/m, sized from the wings' plans.
LOD3_PPM = 8.0
LOD3_FW_DECK = (634, 808, 67, 42)        # 8.4 x 5.2 m
LOD3_BW_DECK = (705, 808, 91, 90)        # 11.4 x 11.2 m
# and a long wall's bay, both storeys' windows in one region, a downsampled
# copy of the bands they stand for (paint_lod3_bay)
LOD3_BAY_PPM = 16.0
LOD3_BAY = (4, 870, 64, 76)              # 4.0 x 4.75 m
LOD3_STAIR = (204, 868, 20, 104)         # 1.25 x 6.5 m, the same density

REGION = {"entrance": ENTRANCE, "glazed_door": GLAZED_DOOR,
          "service_door": SERVICE_DOOR, "loading_door": LOADING_DOOR,
          "stair": STAIR, "lod3_bay": LOD3_BAY, "lod3_stair": LOD3_STAIR}
REGION_PPM = {"loading_door": 40.0, "lod3_bay": LOD3_BAY_PPM,
              "lod3_stair": LOD3_BAY_PPM}

PATCH_NAMES = ("blank", "soffit", "sill", "steel", "coping", "barge",
               "parapet_in", "conc", "ceiling", "pipe", "felt")
PATCHES = {n: (4 + 20 * i, 1004, 16, 16) for i, n in enumerate(PATCH_NAMES)}

# ----------------------------------------------------------- material ids
ID_BLANK, ID_PLINTH, ID_BRICK, ID_BRICK2, ID_MORTAR = 0, 1, 2, 3, 4
ID_FRAME, ID_GLASS, ID_ROOF, ID_FLASH, ID_FELT = 5, 6, 7, 8, 9
ID_CONC, ID_DOOR, ID_LOAD, ID_STEEL, ID_PIPE = 10, 11, 12, 13, 14
ID_SOFFIT, ID_GUTTER, ID_HANDLE, ID_DARK, ID_SEAL = 15, 16, 17, 18, 19

# (roughness, metallic). Painted sheet stays mostly dielectric -- the paint is
# what the light sees; the ladders, handles and roof ladder are galvanised or
# stainless and are the only bare metal.
SURFACE = {
    ID_BLANK: (0.95, 0.0), ID_PLINTH: (0.90, 0.0), ID_BRICK: (0.84, 0.0),
    ID_BRICK2: (0.82, 0.0), ID_MORTAR: (0.94, 0.0), ID_FRAME: (0.42, 0.0),
    ID_GLASS: (glazing.ROUGHNESS, 0.0), ID_ROOF: (0.44, 0.25),
    ID_FLASH: (0.42, 0.20), ID_FELT: (0.93, 0.0), ID_CONC: (0.88, 0.0),
    ID_DOOR: (0.50, 0.0), ID_LOAD: (0.46, 0.0), ID_STEEL: (0.38, 0.75),
    ID_PIPE: (0.55, 0.20), ID_SOFFIT: (0.72, 0.0), ID_GUTTER: (0.40, 0.30),
    ID_HANDLE: (0.30, 0.85), ID_DARK: (0.96, 0.0), ID_SEAL: (0.90, 0.0),
}

# ---------------------------------------------------------------- palettes
# One coherent treatment per instance: the brick changes, and the frames,
# roof, flashing and doors move with it, never within one building.
VARIANTS = {
    "red_brick": {"brick": (146, 74, 54), "brick2": (116, 60, 47),
                  "mortar": (150, 145, 136), "frame": (224, 222, 214),
                  "roof": (156, 158, 158), "flash": (206, 206, 202),
                  "door": (112, 116, 118), "load": (196, 196, 192)},
    "brown_brick": {"brick": (112, 76, 60), "brick2": (90, 62, 50),
                    "mortar": (128, 122, 114), "frame": (76, 64, 54),
                    "roof": (66, 64, 62), "flash": (74, 72, 70),
                    "door": (82, 70, 60), "load": (150, 144, 136)},
    "yellow_brick": {"brick": (190, 168, 124), "brick2": (166, 144, 104),
                     "mortar": (162, 158, 150), "frame": (70, 74, 78),
                     "roof": (62, 66, 70), "flash": (72, 76, 80),
                     "door": (84, 90, 96), "load": (182, 182, 178)},
    "grey_brick": {"brick": (140, 134, 126), "brick2": (118, 114, 108),
                   "mortar": (166, 164, 158), "frame": (224, 223, 219),
                   "roof": (96, 100, 104), "flash": (190, 190, 188),
                   "door": (74, 78, 82), "load": (200, 200, 198)},
}
DEFAULT_VARIANT = "red_brick"

FIXED = {
    ID_GLASS: glazing.BASE, ID_PLINTH: (152, 150, 144), ID_FELT: (50, 50, 52),
    ID_CONC: (184, 182, 176), ID_STEEL: (150, 152, 150), ID_PIPE: (62, 62, 64),
    ID_SOFFIT: (198, 196, 190), ID_HANDLE: (168, 168, 166),
    ID_DARK: (24, 24, 24), ID_SEAL: (34, 34, 34), ID_BLANK: (52, 52, 52),
}

# A stray pixel in a tiling band is not a local blemish: every surface that
# samples the band repeats it.
BAND_IDS = {
    "BRICK": ((0, 458), {ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH}),
    "WINDOW": ((460, 554), {ID_FRAME, ID_GLASS}),
    "ROOF": ((556, 632), {ID_ROOF}),
    "EAVE": ((634, 654), {ID_FLASH, ID_GUTTER}),
    "FLASH": ((656, 684), {ID_FLASH}),
}

# The candidate-glazing mask is the emission map, neutral white.
EMIT = {ID_GLASS: (255, 255, 255)}
# Linear RGB. Workshop and office floors are lit by fluorescent tubes, not a
# living-room bulb, so the catalog's warm residential factor would misread
# them; the value is the one lahikauppa_corner uses for its sales floor.
LIT_FACTOR = (1.0, 0.88, 0.72)

# ---------------------------------------------------------------- relief
# Heights in metres, relative to the face each region maps onto: only the few
# centimetres the mesh does not model. Regions painted coarser than 64 px/m
# scale their relief by their own px/m over PPM, so the slope the normal map
# derives stays physical; the deck (10 px/m) stays flat.
BRICK_FACE = brickwork.BRICK_FACE   # brick face proud of the recessed mortar
FRAME_H = 0.030         # window and door frames, proud of the glass
SASH_H = 0.045          # an opening casement's sash, proud of the frame
DOOR_FRAME_H = 0.020    # steel door frames
RIB_H = 0.035           # the roof sheet's trapezoid ribs
STEP_H = 0.008          # the roof sheet's minor stiffeners
GUTTER_R = 0.070        # half-round gutter
PANEL_D = 0.008         # the loading door's section joints


def m(v):
    """Metres -> pixels."""
    return v * PPM


def region_size_m(kind):
    x, y, w, h = REGION[kind]
    p = REGION_PPM.get(kind, PPM)
    return w / p, h / p


# ================================================================== bands
def paint_plinth(c, y0):
    """Cast concrete, the 0.375 m base every wall stands on."""
    h = m(Z_PLINTH)
    c.paint(0, ATLAS, y0 - PAD, y0 + h, ID_PLINTH, 1.0, 1.0, height=0.0)
    sy, sx, Y, _ = c.field(0, ATLAS, y0 - PAD, y0 + h)
    z = (Y - y0) / PPM
    c.shade[sy, sx] *= 0.82 + 0.18 * np.clip(z / 0.20, 0.0, 1.0) ** 0.7
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.84 + 0.16 * np.clip(z / 0.20, 0, 1))
    # board-formed pour line, and the occluded strip under the brick's drip
    c.mul(0, ATLAS, y0 + m(0.18), y0 + m(0.18) + 1, 0.94, ao=0.94)
    c.lift(0, ATLAS, y0 + m(0.18), y0 + m(0.18) + 1, -0.002)
    c.mul(0, ATLAS, y0 + h - 2, y0 + h, 0.88, ao=0.86)


def paint_brick(c):
    """Stretcher-bond facing brick, 0.25 x 0.078125 m, 64 bricks per width,
    in two tones: most of the burn, and one brick in six from the darker end
    of the kiln. Mortar is its own id, recessed, and lighter than red brick
    the way a real joint is. Tone and bond repeat exactly at the atlas wrap in
    U and every TONE_COURSES in V, which is what lets the gables sample these
    rows again higher up."""
    brickwork.paint(c, 0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + BRICK_H + PAD,
                    (ID_BRICK, ID_BRICK2, ID_MORTAR), TONE_COURSES, seed=17)
    paint_plinth(c, BRICK_Y0)


def paint_windows(c):
    """The ribbon-window band: every 2 m cell is a fixed light and an opening
    casement, framed in the variant's frame colour.

    The cells alternate, casement first and then casement last, so a 4 m
    window has its casements at its two ends and its fixed lights together in
    the middle, and a 2 m window its casement at its left jamb. The frame at a
    cell edge is split across it, 4 px each side, so a window that starts on a
    pair's boundary gets its jamb frame and two cells coupled side by side get
    a doubled mullion; the band tiles because the pair divides the atlas
    width. The casement's sash stands proud of the frame. scripts/glazing.py
    paints one room per light.
    """
    y0, h = WIN_Y0, WIN_H_PX
    cell = m(WIN_CELL)
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_FRAME, 1.0, 1.0, height=FRAME_H)
    rail_b, rail_t = 6, 5
    for i in range(int(ATLAS / cell)):
        x = i * cell
        # bevel the frame round each light so its arrises catch the light
        c.bevel(x, x + cell, y0 - PAD, y0 + h + PAD, FRAME_H, 1.0, axes="x")
        if i % 2:
            fx0, fx1, sx0, sx1 = x + 4, x + 80, x + 84, x + cell - 4
            jamb = fx0
        else:
            sx0, sx1, fx0, fx1 = x + 4, x + 44, x + 48, x + cell - 4
            jamb = fx1 - 2
        c.paint(fx0, fx1, y0 + rail_b, y0 + h - rail_t, ID_GLASS, 1.0, 0.92, height=0.0)
        c.paint(sx0, sx1, y0 + rail_b, y0 + h - rail_t, ID_FRAME, 1.0, 0.88)
        c.bevel(sx0, sx1, y0 + rail_b, y0 + h - rail_t, SASH_H, 1.0)
        c.paint(sx0 + 3, sx1 - 3, y0 + rail_b + 3, y0 + h - rail_t - 3,
                ID_GLASS, 1.0, 0.92, height=0.0)
        # the head rail shades the top of each light; the sash's own edge too
        for a0, a1, b0 in ((fx0, fx1, y0 + h - rail_t), (sx0 + 3, sx1 - 3,
                                                          y0 + h - rail_t - 3)):
            c.mul(a0, a1, b0 - 5, b0, 0.90, ao=0.84)
        c.mul(jamb, jamb + 2, y0 + rail_b, y0 + h - rail_t, 0.92, ao=0.88)
    # the bottom rail, a little heavier, and its drip
    c.mul(0, ATLAS, y0 - PAD, y0 + 2, 0.90, ao=0.86)


def paint_roof(c):
    """Profiled steel sheet: trapezoid ribs down the slope every 0.5 m with a
    stiffener between, a drip at the eave and the ridge flashing at the top.

    V is stretched up the slope (ROOF_H rows over SLOPE_LEN). The ribs vary in
    U only, at 64 px/m; what varies in V is scaled by the band's rows per metre
    over PPM, so its slope stays physical.
    """
    y0, h = ROOF_Y0, ROOF_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_ROOF, 1.0, 1.0, height=0.0)
    sy, sx, Y, X = c.field(0, ATLAS, y0 - PAD, y0 + h + PAD)
    d = np.abs(((X % 32.0) + 16.0) % 32.0 - 16.0)        # to the rib's centre
    height = RIB_H * np.clip((4.5 - d) / 2.0, 0.0, 1.0)
    foot = (d >= 4.5) & (d < 6.0)
    ds = np.abs(((X % 32.0)) - 16.0)                      # the stiffener
    height = height + STEP_H * np.clip(1.5 - ds, 0.0, 1.0)
    shade = np.where(foot, 0.93, 1.0)
    ao = np.where(foot, 0.86, 1.0)
    v = Y - y0
    k = ROOF_RPM / PPM
    shade = np.where(v < 2, shade * 0.84, shade)                    # eave drip
    ridge = v >= h - 3                                               # ridge cap
    height = np.where(ridge, 0.01 * k, height)
    shade = np.where(ridge, 0.96, shade)
    ao = np.where(ridge, 1.0, ao)
    shade = np.where((v >= h - 4) & (v < h - 3), shade * 0.82, shade)
    c.height[sy, sx], c.shade[sy, sx], c.ao[sy, sx] = height, shade, ao


def paint_eave(c):
    """The eave's vertical edge: a fascia board in the flashing colour with a
    half-round gutter hung across its top, hangers every metre."""
    y0 = EAVE_Y0
    top = y0 + EAVE_H
    c.paint(0, ATLAS, y0 - PAD, top + PAD, ID_FLASH, 1.0, 1.0, height=0.0)
    c.paint(0, ATLAS, y0 - PAD, y0 + 1, ID_FLASH, 0.86, 0.9)       # drip edge
    gh = float(GUTTER_PX)
    g0 = top - gh
    c.paint(0, ATLAS, g0, top + PAD, ID_GUTTER, 1.0, 1.0)
    sy, sx, Y, _ = c.field(0, ATLAS, g0, top)
    u = 2.0 * (Y - g0) / gh - 1.0
    c.height[sy, sx] = GUTTER_R * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
    c.paint(0, ATLAS, g0, g0 + 1, ID_GUTTER, 0.82, 0.86)
    for k, f in enumerate((0.84, 0.90, 0.95)):             # under the gutter
        c.mul(0, ATLAS, g0 - 1 - k, g0 - k, f, ao=0.86)
    sy, sx, _, X = c.field(0, ATLAS, g0 + 1, top)           # hangers, 1 m
    hang = (X % 64.0) < 2.0
    c.shade[sy, sx] = np.where(hang, c.shade[sy, sx] * 0.84, c.shade[sy, sx])
    c.height[sy, sx] = np.where(hang, c.height[sy, sx] + 0.004, c.height[sy, sx])


def paint_flash(c):
    """Folded sheet flashing: the wings' fascias and the canopies' edges. A
    fold at the top, a drip at the foot, and a lap joint every 2 m, which
    divides the atlas width so the band tiles."""
    y0, h = FLASH_Y0, FLASH_H
    c.paint(0, ATLAS, y0 - PAD, y0 + h + PAD, ID_FLASH, 1.0, 1.0, height=0.0)
    c.bevel(0, ATLAS, y0 + 2, y0 + h - 2, 0.010, 1.5, axes="y")
    c.paint(0, ATLAS, y0 - PAD, y0 + 2, ID_FLASH, 0.84, 0.86, height=0.0)
    c.mul(0, ATLAS, y0 + h - 2, y0 + h + PAD, 0.96)
    for i in range(int(ATLAS / 128)):
        x = i * 128.0
        c.mul(x, x + 1, y0, y0 + h, 0.86, ao=0.88)
        c.lift(x + 1, x + 3, y0 + 2, y0 + h - 2, 0.002)


# ================================================================= regions
def _bar(c, a0, a1, b0, b1, mid=ID_FRAME, h=FRAME_H, ao=0.86, shade=1.0, axes="xy"):
    c.paint(a0, a1, b0, b1, mid, shade, ao)
    c.bevel(a0, a1, b0, b1, h, 1.0, axes=axes)


def _handle(c, x, y0, y1):
    """A stainless pull bar standing off the leaf."""
    c.paint(x - 1.2, x + 1.2, y0, y1, ID_HANDLE, 1.0, 0.9)
    sy, sx, _, X = c.field(x - 1.2, x + 1.2, y0, y1)
    u = (X - x) / 1.2
    c.height[sy, sx] = 0.05 * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))


def paint_entrance(c):
    """The main entrance screen: a pair of glazed leaves between two side
    lights, a transom light over the lot at the leaf head, in the frame
    colour. Used twice: in the lobby on the front and under the pillars."""
    x, y, w, h = ENTRANCE
    c.paint(x, x + w, y, y + h, ID_GLASS, 1.0, 1.0, height=0.0)
    F = 5
    yt = y + m(Z_LEAF)
    _bar(c, x, x + w, y, y + 4, axes="y")                 # threshold
    _bar(c, x, x + w, y + h - F, y + h, axes="y")
    _bar(c, x, x + F, y, y + h, axes="x")
    _bar(c, x + w - F, x + w, y, y + h, axes="x")
    _bar(c, x, x + w, yt - 3, yt + 3, axes="y")           # transom bar
    for mx in (x + 32, x + 160):                          # side-light mullions
        _bar(c, mx - 3, mx + 3, y, y + h, axes="x")
    # side lights: a solid kick panel at the foot
    for a0, a1 in ((x + F, x + 29), (x + 163, x + w - F)):
        _bar(c, a0, a1, y + 4, y + 30, h=0.02)
    # the two leaves meet on the centre line
    for l0, l1, hx in ((x + 35, x + 96, x + 90), (x + 96, x + 157, x + 102)):
        _bar(c, l0, l0 + 6, y + 4, yt - 3, h=0.04, axes="x")
        _bar(c, l1 - 6, l1, y + 4, yt - 3, h=0.04, axes="x")
        _bar(c, l0, l1, yt - 9, yt - 3, h=0.04, axes="y")
        _bar(c, l0, l1, y + 4, y + 20, h=0.04, axes="y")
        _handle(c, hx, y + m(0.85), y + m(1.45))
    # the lobby is in shade and deep: the glass reads darker at its foot
    sy, sx, Y, _ = c.field(x, x + w, y, y + h)
    c.ao[sy, sx] = np.minimum(c.ao[sy, sx], 0.80 + 0.15 * (Y - y) / h)


def paint_glazed_door(c):
    """A single glazed leaf with a transom light: the stair door and the
    wings' side doors."""
    x, y, w, h = GLAZED_DOOR
    c.paint(x, x + w, y, y + h, ID_GLASS, 1.0, 1.0, height=0.0)
    F = 4
    yt = y + m(Z_LEAF)
    _bar(c, x, x + w, y, y + 4, axes="y")
    _bar(c, x, x + w, y + h - F, y + h, axes="y")
    _bar(c, x, x + F, y, y + h, axes="x")
    _bar(c, x + w - F, x + w, y, y + h, axes="x")
    _bar(c, x, x + w, yt - 3, yt + 3, axes="y")
    l0, l1 = x + F, x + w - F
    _bar(c, l0, l0 + 7, y + 4, yt - 3, h=0.04, axes="x")
    _bar(c, l1 - 7, l1, y + 4, yt - 3, h=0.04, axes="x")
    _bar(c, l0, l1, yt - 10, yt - 3, h=0.04, axes="y")
    _bar(c, l0, l1, y + 4, y + 22, h=0.04, axes="y")
    _handle(c, l1 - 12, y + m(0.85), y + m(1.35))


def paint_service_door(c):
    """A plain steel leaf in a steel frame: the back door, the wings' and the
    west gable's personnel doors."""
    x, y, w, h = SERVICE_DOOR
    c.paint(x, x + w, y, y + h, ID_DOOR, 0.86, 0.9, height=0.0)
    F = 4
    _bar(c, x, x + F, y, y + h, ID_DOOR, DOOR_FRAME_H, 0.84, 0.86, "x")
    _bar(c, x + w - F, x + w, y, y + h, ID_DOOR, DOOR_FRAME_H, 0.84, 0.86, "x")
    _bar(c, x, x + w, y + h - F, y + h, ID_DOOR, DOOR_FRAME_H, 0.84, 0.86, "y")
    l0, l1, t = x + F, x + w - F, y + h - F
    c.paint(l0, l1, y, t, ID_DOOR, 1.0, 0.96, height=0.0)
    c.mul(l0, l1, t - 3, t, 0.88, ao=0.84)
    # a kick plate, the lever and its escutcheon
    c.paint(l0 + 2, l1 - 2, y + 2, y + m(0.25), ID_STEEL, 0.9, 0.9, height=0.003)
    hx, hy = l1 - 8, y + m(1.0)
    c.paint(hx - 1.5, hx + 1.5, hy - 5, hy + 5, ID_HANDLE, 1.0, 0.9, height=0.01)
    c.stroke((hx, hy + 2), (hx - 8, hy + 2), 2.2, ID_HANDLE, 1.0, 0.9, height=0.04)


def paint_loading_door(c):
    """A sectional overhead door: eight horizontal sections with a fine rib
    in each, running in steel guides, rubber seal at the floor. Painted at
    40 px/m, so its relief is scaled by 40/64."""
    x, y, w, h = LOADING_DOOR
    k = 40.0 / PPM
    c.paint(x, x + w, y, y + h, ID_LOAD, 1.0, 1.0, height=0.0)
    G = 4
    c.paint(x, x + G, y, y + h, ID_STEEL, 0.70, 0.78, height=0.02 * k)
    c.paint(x + w - G, x + w, y, y + h, ID_STEEL, 0.70, 0.78, height=0.02 * k)
    c.paint(x, x + w, y + h - 3, y + h, ID_STEEL, 0.72, 0.76, height=0.02 * k)
    dx0, dx1, top = x + G, x + w - G, y + h - 3
    n = 8
    for i in range(n):
        s0 = y + (top - y) * i / n
        s1 = y + (top - y) * (i + 1) / n
        # a shallow rib along each section's middle
        mid = (s0 + s1) / 2.0
        c.mul(dx0, dx1, mid - 0.5, mid + 0.5, 0.94, ao=0.92)
        c.lift(dx0, dx1, mid - 0.5, mid + 0.5, -0.003 * k)
        if i:
            c.mul(dx0, dx1, s0 - 1, s0 + 1, 0.80, ao=0.74)
            c.lift(dx0, dx1, s0 - 1, s0 + 1, -PANEL_D * k)
    c.paint(dx0, dx1, y, y + 2, ID_SEAL, 1.0, 0.8)
    # the lock and lift handle on the bottom section
    cx = x + w / 2.0
    c.paint(cx - 6, cx + 6, y + 6, y + 9, ID_HANDLE, 0.9, 0.85, height=0.03 * k)
    c.mul(dx0, dx1, top - 5, top, 0.88, ao=0.80)


def paint_stair(c):
    """The stair glazing on the front: one tall light divided by transoms
    into four, in the frame colour. The stair it lights has no storeys, so it
    runs past the upper floor's sill line."""
    x, y, w, h = STAIR
    c.paint(x, x + w, y, y + h, ID_GLASS, 1.0, 1.0, height=0.0)
    F = 5
    _bar(c, x, x + w, y, y + 6, axes="y")
    _bar(c, x, x + w, y + h - F, y + h, axes="y")
    _bar(c, x, x + F, y, y + h, axes="x")
    _bar(c, x + w - F, x + w, y, y + h, axes="x")
    for i in range(1, 4):
        yy = y + h * i / 4.0
        _bar(c, x, x + w, yy - 2.5, yy + 2.5, axes="y")
        c.mul(x + F, x + w - F, yy - 7.5, yy - 2.5, 0.92, ao=0.86)
    c.mul(x + F, x + w - F, y + h - F - 5, y + h - F, 0.92, ao=0.86)


def paint_pillar(c):
    """One face of a cast concrete pillar, ground at the foot: the arrises
    chamfered, a pour joint every metre."""
    x, y, w, h = PILLAR
    c.paint(x, x + w, y, y + h, ID_CONC, 1.0, 1.0, height=0.0)
    c.bevel(x, x + w, y - 2, y + h + 2, 0.008, 1.5, axes="x")
    for zz in (1.0, 2.0):
        yy = y + m(zz)
        c.mul(x, x + w, yy, yy + 1, 0.93, ao=0.92)
        c.lift(x, x + w, yy, yy + 1, -0.002)
    c.mul(x, x + 1, y, y + h, 0.94)
    c.mul(x + w - 1, x + w, y, y + h, 0.94)


def paint_deck(c):
    """Bitumen felt on the wings' flat roofs: laid in 1 m rolls, a little
    ponding, and a darker walking line where the ladders land. 10 px/m."""
    x, y, w, h = DECK
    c.paint(x, x + w, y, y + h, ID_FELT, 1.0, 1.0, height=0.0)
    for i in range(1, int(w / DECK_PPM) + 1):
        xx = x + i * DECK_PPM
        c.mul(xx - 0.5, xx + 0.5, y, y + h, 0.90, ao=0.90)
    rs = np.random.RandomState(23)
    for _ in range(18):
        cx, cy = rs.uniform(x + 8, x + w - 8), rs.uniform(y + 8, y + h - 8)
        c.disc(cx, cy, rs.uniform(4, 11), None, rs.uniform(0.93, 0.99), 0.97)
    c.mul(x, x + w, y, y + h, 1.0, ao=0.95)


def _copy_down(c, rect, source):
    """Fill *rect* with a quarter-density copy of the atlas: *source(s, z)*
    gives, for each sample's position in metres across and up the region,
    the band or region pixel (U, V) it stands for. Each region pixel's 4 x 4
    samples land on 4 x 4 different source pixels, so the box filter
    averages them the way a mip of the source would, and the copy matches
    the walls round it at the distances LOD3 is seen from. Flat: its relief
    would be under a pixel at 120 m."""
    x, y, w, h = rect
    sy, sx, Y, X = c.field(x, x + w, y, y + h)
    U, V = source((X - x) / LOD3_BAY_PPM, (Y - y) / LOD3_BAY_PPM)
    n = c.size * c.ss
    iu = np.clip((U * c.ss).astype(np.int64), 0, n - 1)
    iv = np.clip((V * c.ss).astype(np.int64), 0, n - 1)
    c.mid[sy, sx] = c.mid[iv, iu]
    c.shade[sy, sx] = c.shade[iv, iu]
    c.ao[sy, sx] = c.ao[iv, iu]
    c.height[sy, sx] = 0.0


def paint_lod3_bay(c):
    """LOD3's two-storey window bay: the ribbon window at each storey's sill
    and the brick between, from the bands."""
    def source(s, dz):
        z = Z_SILL + dz
        zw = np.where(z >= Z_SILL_UP, z - Z_SILL_UP, z - Z_SILL)
        win = zw < WIN_H
        return s * PPM, np.where(win, WIN_Y0 + zw * PPM, BRICK_Y0 + z * PPM)
    _copy_down(c, LOD3_BAY, source)


def paint_lod3_stair(c):
    """LOD3's stair column: the glazed door on the ground, a strip of brick
    behind the canopy, and the stair glazing above, from their regions."""
    dw = OPENINGS["glazed_door"][0]
    side = (OPENINGS["stair"][0] - dw) / 2.0
    z0 = Z_STAIR

    def source(s, z):
        gx, gy = GLAZED_DOOR[:2]
        sx_, sy_ = STAIR[:2]
        door = (z < Z_DOOR) & (s >= side) & (s < side + dw)
        glaze = z >= z0
        U = np.where(door, gx + (s - side) * PPM,
                     np.where(glaze, sx_ + s * PPM, s * PPM))
        V = np.where(door, gy + z * PPM,
                     np.where(glaze, sy_ + (z - z0) * PPM, BRICK_Y0 + z * PPM))
        return U, V
    _copy_down(c, LOD3_STAIR, source)


def paint_lod3_decks(c):
    """LOD3's wing lids: felt, with the coping's light edge on the three
    sides that oversail a wall, dark on the side that runs into the block.
    The front wing's open side is at the top of its region (its plan's +y),
    the back wing's at the foot."""
    edge = (WING_OVER + PARAPET) * LOD3_PPM
    for rect, open_top in ((LOD3_FW_DECK, True), (LOD3_BW_DECK, False)):
        x, y, w, h = rect
        c.paint(x, x + w, y, y + h, ID_FELT, 1.0, 1.0, height=0.0)
        for i in range(1, int(w / LOD3_PPM) + 1):
            xx = x + i * LOD3_PPM
            c.mul(xx - 0.4, xx + 0.4, y, y + h, 0.92, ao=0.92)
        c.paint(x, x + edge, y, y + h, ID_FLASH, 1.0, 0.96)
        c.paint(x + w - edge, x + w, y, y + h, ID_FLASH, 1.0, 0.96)
        if open_top:
            c.paint(x, x + w, y, y + edge, ID_FLASH, 1.0, 0.96)
            inner = (x + edge, x + w - edge, y + edge, y + h)
        else:
            c.paint(x, x + w, y + h - edge, y + h, ID_FLASH, 1.0, 0.96)
            inner = (x + edge, x + w - edge, y, y + h - edge)
        # the parapet's shadow line inside the coping
        a0, a1, b0, b1 = inner
        c.mul(a0, a0 + 1, b0, b1, 0.8, ao=0.8)
        c.mul(a1 - 1, a1, b0, b1, 0.8, ao=0.8)
        if open_top:
            c.mul(a0, a1, b0, b0 + 1, 0.8, ao=0.8)
        else:
            c.mul(a0, a1, b1 - 1, b1, 0.8, ao=0.8)


def paint_vent(c):
    """A black steel vent pipe's side, wrapped once round, with a collar
    near the top and a welded seam; its open end, the bore dark."""
    x, y, w, h = VENT
    c.paint(x, x + w, y, y + h, ID_PIPE, 1.0, 1.0, height=0.0)
    sy, sx, _, X = c.field(x, x + w, y, y + h)
    u = 2.0 * (X - x) / w - 1.0
    c.shade[sy, sx] *= 0.96 + 0.04 * np.cos(np.pi * u)
    c.mul(x + w / 2 - 0.5, x + w / 2 + 0.5, y, y + h, 0.88, ao=0.9)
    for yy in (y + m(0.45), y + m(0.9)):
        c.paint(x, x + w, yy - 2, yy + 2, ID_PIPE, 0.90, 0.9, height=0.006)
    x, y, w, h = PIPE_TOP
    c.paint(x, x + w, y, y + h, ID_PIPE, 1.0, 1.0, height=0.0)
    cx, cy = x + w / 2.0, y + h / 2.0
    c.disc(cx, cy, w / 2.0 - 1.5, ID_DARK, 1.0, 0.5, height=-0.02)
    c.disc(cx, cy, w / 2.0 - 4.0, ID_DARK, 0.6, 0.3, height=-0.04)


def paint_patches(c):
    """Flat cells for surfaces a whole face takes one colour from."""
    spec = {
        "blank": (ID_BLANK, 1.0, 1.0),
        "soffit": (ID_SOFFIT, 0.92, 0.80),
        "sill": (ID_FLASH, 0.96, 0.92),
        "steel": (ID_STEEL, 1.0, 0.95),
        "coping": (ID_FLASH, 1.0, 0.98),
        "barge": (ID_FLASH, 0.92, 0.94),
        "parapet_in": (ID_FELT, 0.92, 0.86),
        "conc": (ID_CONC, 0.9, 0.9),
        "ceiling": (ID_SOFFIT, 0.70, 0.62),
        "pipe": (ID_PIPE, 1.0, 0.95),
        "felt": (ID_FELT, 1.0, 1.0),
    }
    atlas.paint_patches(c, PATCHES, spec)


# ------------------------------------------------------------------ checks
def check_regions():
    """Fail the bake if two unique regions overlap, collide with the bands, or
    run off the sheet."""
    rects = {"entrance": ENTRANCE, "glazed_door": GLAZED_DOOR,
             "service_door": SERVICE_DOOR, "loading_door": LOADING_DOOR,
             "stair": STAIR, "pillar": PILLAR, "deck": DECK, "vent": VENT,
             "pipe_top": PIPE_TOP, "lod3_fw_deck": LOD3_FW_DECK,
             "lod3_bw_deck": LOD3_BW_DECK, "lod3_bay": LOD3_BAY,
             "lod3_stair": LOD3_STAIR}
    rects.update(PATCHES)
    problems = atlas.region_problems(rects, ATLAS, bands_top=FLASH_Y0 + FLASH_H + PAD)
    for rect, wing in ((LOD3_FW_DECK, FRONT_WING), (LOD3_BW_DECK, BACK_WING)):
        w = (wing[1] - wing[0]) * LOD3_PPM
        h = (wing[3] - wing[2] + WING_BURY) * LOD3_PPM
        if abs(rect[2] - w) > 1.0 or abs(rect[3] - h) > 1.0:
            problems.append("a LOD3 deck region is %d x %d px for %.1f x %.1f px "
                            "of wing" % (rect[2], rect[3], w, h))
    for kind, (w, h) in OPENINGS.items():
        if kind in REGION:
            rw, rh = region_size_m(kind)
            if abs(rw - w) > 0.02 or abs(rh - h) > 0.02:
                problems.append("%s region is %.3f x %.3f m for a %.3f x %.3f m "
                                "opening" % (kind, rw, rh, w, h))
    if abs(m(WIN_H) - WIN_H_PX) > 1e-6:
        problems.append("the window band is not WIN_H tall")
    if ATLAS % m(2 * WIN_CELL):
        problems.append("a pair of window cells does not divide the atlas width")
    if abs(m(Z_WALL_TOP) - BRICK_H) > 1e-6:
        problems.append("the brick band does not reach the wall head")
    if (m(GABLE_SHIFT) / m(COURSE)) % TONE_COURSES:
        problems.append("GABLE_SHIFT is not a whole tone period of courses")
    if problems:
        raise ValueError("atlas layout: " + "; ".join(problems))


# ================================================================ weather
def weather(c):
    """Where the weather goes; scripts/weathering.py says what it looks like.

    The brick band's V is height from the ground, so splash-back, the
    plinth's soil and salt bloom land the same on every wall. Nothing that
    follows height goes near the band's top: the gable triangles sample the
    rows 3.75 m lower, and the eave is too shallow to shelter a dust line.
    """
    brick = (ID_BRICK, ID_BRICK2, ID_MORTAR)
    steel = (ID_ROOF, ID_FLASH, ID_GUTTER, ID_STEEL, ID_PIPE, ID_FELT,
             ID_LOAD, ID_DOOR, ID_HANDLE)
    w = weathering.Weather(c, clean=(ID_GLASS,), steel=steel)
    w.grime()
    w.fade((ID_FRAME, ID_DOOR, ID_LOAD, ID_FLASH))
    w.wash(brick)
    w.plinth(0, ATLAS, BRICK_Y0, BRICK_Y0 + m(Z_PLINTH), (ID_PLINTH,))
    w.splash(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + BRICK_H + PAD, brick)
    w.bloom(0, ATLAS, BRICK_Y0 + m(Z_PLINTH), BRICK_Y0 + m(1.3), brick,
            amount=0.10, fade=m(0.7))
    # the ribbon windows: dirt standing on the bottom rail
    w.add("D", 0, ATLAS, WIN_Y0 - PAD, WIN_Y0 + 6, lambda Y, X, nz: 0.10
          + 0.12 * atlas.smoothstep(0.2, 1.4, nz("short")), (ID_FRAME,))
    # the roof: runs down the slope, dirt toward the gutter, chalking up top
    w.roof(0, ATLAS, ROOF_Y0, ROOF_H, SLOPE_LEN, (ID_ROOF,))
    # the gutter and the flashings: runs from their top edges
    w.add("D", 0, ATLAS, EAVE_Y0 + EAVE_H - 9, EAVE_Y0 + EAVE_H,
          lambda Y, X, nz: 0.08 + 0.10 * nz("blotch"), (ID_GUTTER,))
    w.runs(0, ATLAS, EAVE_Y0 - PAD, EAVE_Y0 + EAVE_H - 9, (ID_FLASH,), 0.12,
           fall=6.0, noise="short")
    w.runs(0, ATLAS, FLASH_Y0, FLASH_Y0 + FLASH_H, (ID_FLASH,), 0.14, fall=10.0,
           noise="short")
    # thresholds, handles and the feet of the doors
    for rect, handle in ((ENTRANCE, None), (GLAZED_DOOR, None),
                         (SERVICE_DOOR, (SERVICE_DOOR[0] + SERVICE_DOOR[2] - 12,
                                         SERVICE_DOOR[1] + m(1.0)))):
        x, y, rw, rh = rect
        w.add("D", x, x + rw, y, y + 6, lambda Y, X, nz: 0.14 + 0.08 * nz("blotch"),
              (ID_FRAME, ID_DOOR, ID_STEEL))
        if handle:
            w.door(x + 4, x + rw - 4, y, y + rh - 4, (ID_DOOR,), handle=handle)
    x, y, rw, rh = LOADING_DOOR
    w.door(x + 4, x + rw - 4, y, y + rh, (ID_LOAD,), ppm=40.0)
    w.add("R", x, x + 4, y, y + 30, lambda Y, X, nz: 0.12 * nz("blotch"), (ID_STEEL,))
    w.add("R", x + rw - 4, x + rw, y, y + 30, lambda Y, X, nz: 0.12 * nz("blotch"),
          (ID_STEEL,))
    # the pillars stand in the porch's splash
    x, y, rw, rh = PILLAR
    w.splash(x, x + rw, y, y + rh, (ID_CONC,), amount=0.26, fall=0.22)
    # the felt deck: dirt where it ponds
    x, y, rw, rh = DECK
    w.add("D", x, x + rw, y, y + rh, lambda Y, X, nz: 0.10 * nz("big")
          + 0.06 * nz("blotch"), (ID_FELT,))
    # the vent pipes: soot and rust runs down from the open end
    x, y, rw, rh = VENT
    w.runs(x, x + rw, y, y + rh, (ID_PIPE,), 0.14, fall=rh / 2.0)
    w.add("R", x, x + rw, y, y + rh, lambda Y, X, nz: 0.10 * atlas.smoothstep(
        0.4, 1.6, nz("runs")), (ID_PIPE,))
    return w


# ================================================================ painting
def paint(ss=atlas.SS):
    """Paint once: ids, shade, AO and height. Colour comes later, per variant."""
    check_regions()
    c = atlas.Canvas(ATLAS, ss, PPM)
    paint_brick(c)
    paint_windows(c)
    paint_roof(c)
    paint_eave(c)
    paint_flash(c)
    c.check_bands(BAND_IDS)
    paint_lod3_bay(c)
    paint_entrance(c)
    paint_glazed_door(c)
    paint_service_door(c)
    paint_loading_door(c)
    paint_stair(c)
    paint_lod3_stair(c)
    paint_pillar(c)
    paint_deck(c)
    paint_lod3_decks(c)
    paint_vent(c)
    paint_patches(c)

    # Tone wear, grain and pores. Every field is periodic, so the bands wrap.
    wear = 0.025 * atlas.noise(c, 3, 40.0) + 0.015 * atlas.noise(c, 4, 8.0)
    c.shade *= 1.0 + wear
    walls = np.isin(c.mid, (ID_BRICK, ID_BRICK2, ID_MORTAR, ID_PLINTH))
    streak = atlas.noise(c, 7, 0.8, 40.0)
    c.shade[walls] *= 1.0 + 0.03 * streak[walls]
    sheet = np.isin(c.mid, (ID_FLASH, ID_LOAD, ID_DOOR))
    grain = atlas.noise(c, 5, 60.0, 0.35)
    c.shade[sheet] *= 1.0 + 0.016 * grain[sheet]
    roof = c.mid == ID_ROOF
    runs = atlas.noise(c, 6, 0.6, 20.0)
    c.shade[roof] *= 1.0 + 0.02 * runs[roof]
    mineral = np.isin(c.mid, (ID_PLINTH, ID_CONC, ID_MORTAR))
    pores = atlas.noise(c, 9, 0.8)
    c.shade[mineral] *= 1.0 + 0.03 * pores[mineral]
    c.height[mineral] += 0.0006 * pores[mineral]
    weather(c)
    c.pad()
    return c


def lut(variant):
    pal = VARIANTS[variant]
    t = np.zeros((256, 3), np.float32)
    for i, col in FIXED.items():
        t[i] = col
    t[ID_BRICK] = pal["brick"]
    t[ID_BRICK2] = pal["brick2"]
    t[ID_MORTAR] = pal["mortar"]
    t[ID_FRAME] = pal["frame"]
    t[ID_ROOF] = pal["roof"]
    t[ID_FLASH] = pal["flash"]
    t[ID_GUTTER] = pal["flash"]
    t[ID_DOOR] = pal["door"]
    t[ID_LOAD] = pal["load"]
    return t


def export(out_dir, ss=atlas.SS):
    """Candidate glazing in the emission map is neutral grey, each light the
    lit room behind it; nothing else on the building glows, and no occupancy
    or schedule is baked in."""
    os.makedirs(out_dir, exist_ok=True)
    c = paint(ss)
    cav = atlas.cavity(c, radius_px=1.5, depth_m=0.010)
    c.weather.dust(cav, (ID_BRICK, ID_BRICK2, ID_MORTAR))
    rough = 0.04 * atlas.noise(c, 13, 20.0)
    path = os.path.join(out_dir, ASSET)
    glass = atlas.coverage(c, ID_GLASS)
    written = [atlas.save(atlas.orm(c, SURFACE, rough, 0.5 * cav), path + "_orm.png"),
               atlas.save(atlas.normal_map(c, flat_ids=(ID_GLASS,)), path + "_normal.png"),
               atlas.save(glazing.night_rooms(glass > 0, atlas.emission_colours(c, EMIT)),
                          path + "_emission.png")]
    for v in VARIANTS:
        rgb = glazing.rooms(glass >= 0.5, atlas.albedo(c, lut(v), grime=0.25 * cav))
        written.append(atlas.save(rgb, "%s_albedo_%s.png" % (path, v)))
    return written


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        for p in export(os.path.join(here, "export")):
            print(p)
    else:
        print(__doc__)
