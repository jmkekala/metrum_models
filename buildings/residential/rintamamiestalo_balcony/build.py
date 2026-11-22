# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of rintamamiestalo_balcony, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Run without a .blend (blender --background --python build.py) it starts from an
empty scene and writes source.blend itself. Regenerate the textures first
(python3 facade_atlas.py export): the UVs index into the atlas, and the renders
read it.

A composite Finnish rintamamiestalo — the 1940s-50s one-and-a-half-storey
veterans' house: a 10 x 8 m block under a 45 degree gable roof, horizontal lap
siding over a concrete plinth with cellar lights, plain-glass windows and a
brick chimney on the ridge. This one has the type's porch-and-balcony front:
a wide entrance porch centred on the long wall, its flat roof a balcony behind
a solid sided parapet, and over it a wall dormer (frontespiisi) with a shed
roof, whose front carries the balcony door out of the attic storey.

Construction is a set of closed solids unioned with Blender's exact boolean.
The house is three of them side by side, the west block, the dormer section
and the east block, because the dormer section's front wall runs from the
ground to the dormer eave in one plane: built as a separate part on top of a
whole house, it would overlap the house's front wall in that plane. Then the
porch-and-balcony, the roof slabs (the main roof in three pieces, cut back
over the dormer, and the dormer's shed roof), the chimney, the back-door canopy
and the two flights of steps. The union cuts the dormer roof into the main
roof, trims the walls where the soffits meet them and removes everything that
ends up inside, so the result is the boundary of one empty volume and interior
geometry cannot occur.

The walls are textured as a trim sheet (see facade_atlas.py): siding tiles,
and each window or door is a hole in the wall with its own faces mapped to the
region that carries its casing and glazing. What the four rintamamiestalo
houses share (the walls and openings, roofs, chimney, canopy, steps, the tier
policy and the common checks) is scripts/rintamamiestalo.py's; this file keeps
the house: its massing, its walls, the porch-and-balcony and the dormer roof,
the places of its downpipes, roof kit and handrails, its own checks and its
facts.
"""

import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "scripts"))
import rintamamiestalo as R  # noqa: E402
importlib.reload(R)       # an interactive session must not keep a stale family
import facade_atlas  # noqa: E402  (the layout shared with the atlas)
importlib.reload(facade_atlas)
import model_facts  # noqa: E402
from asset_build import to_object  # noqa: E402
import downpipes as DP  # noqa: E402
import handrails as HR  # noqa: E402
import roof_safety as RS  # noqa: E402
import shell_build as SB  # noqa: E402
from rintamamiestalo import (  # noqa: E402
    ATTIC_SILL, EAVE_OV, EPS, GF, PPM, RAKE_OV, ROOF_T, STEP_PROFILE, TAN, Steps, Wall)

L = facade_atlas.LAYOUT
K = R.Kit(L, HERE)
BUILD = K.asset

# ------------------------------------------------------------------ massing
# Front faces -Y. Main block 10.0 x 8.0 m, ridge along X.
HX, HY = 5.0, 4.0
Z_APEX = L.Z_WALL_TOP + HY * TAN                 # body apex, inside the slab
Z_RIDGE = L.Z_EAVE + ROOF_T + HY * TAN           # top of the ridge

# Porch, balcony and dormer: three stacked parts on one width, centred on the
# front.
#   - The entrance porch, 2.6 m deep. Its flat roof is the balcony.
#   - The balcony's parapet: the porch walls carried a metre past the deck,
#     solid and sided like the walls, under a cap board. A see-through railing
#     would need alpha, which CLAUDE.md rules out, and a solid sided parapet is
#     the type's own detail anyway.
#   - A wall dormer (frontespiisi) behind it: the front wall carried up
#     through the eave, so the attic storey gets a full-height wall for the
#     balcony door, under a shed roof falling to the front.
# One width means the porch sides, the parapet ends and the dormer corners
# stand on one line each side. CLAUDE.md asks for exact alignment or a real
# setback, and three near-misses stacked up would read as a mistake.
BX0, BX1 = -2.20, 2.20
PY_FRONT = -HY - 2.60
# The deck sits 5 cm under the 3.80 m attic floor, for the door's threshold.
DECK_Z = 3.75
PARAPET_Z = DECK_Z + 1.00
PARAPET_T = L.CW         # = the corner-board width, so cap and board lines meet
DZ_EAVE = 6.30           # dormer front meets its soffit, clear of door and window heads
DZ_TOP = DZ_EAVE + (L.Z_WALL_TOP - L.Z_EAVE)
D_PITCH = 0.30           # the shed roof rises 0.3 m per metre back, about 17 degrees
D_RAKE_OV = 0.30         # past the dormer's side walls; its front eave takes EAVE_OV
# Where the dormer's top meets the main roof, in metres back from the front
# wall. The dormer eave and wall top sit the same 2.0 m over the main ones, so
# the roof surfaces and the solids' lids meet on the same line.
D_JOIN = (DZ_TOP - L.Z_WALL_TOP) / (TAN - D_PITCH)
D_BACK = D_JOIN + 0.35   # the dormer roof runs on this far, buried in the main roof
MAIN_CUT = 2.20          # over the dormer the main slab starts this far back, inside the dormer

CHIMNEY = (0.30, 0.90, -0.42, 0.42, 7.60, Z_RIDGE + 0.95)

FRONT_DOOR_S = 0.90      # along the porch front from its west corner
BACK_DOOR_X = 1.20       # in the rear wall of the dormer section
FRONT_STEPS = (BX0 + FRONT_DOOR_S - 0.70, BX0 + FRONT_DOOR_S + 0.70)
BACK_STEPS = (BACK_DOOR_X - 0.70, BACK_DOOR_X + 0.70)   # along x, off the rear wall
CANOPY_X = (BACK_DOOR_X - 0.75, BACK_DOOR_X + 0.75)     # the back-door canopy
STEPS = [Steps("tmp_steps_f", *FRONT_STEPS, PY_FRONT, -1.0),
         Steps("tmp_steps_r", *BACK_STEPS, HY, 1.0)]

# --------------------------------------------------------------- elevations
# The dormer's windows sit 1.0 m over the attic floor, clear of the parapet in
# front of them. The dormer front carries only the balcony door: a wide window
# will not fit between the parapet, which sets the lowest sill that reads, and
# the dormer's eave, and two small windows flanking the door read busier than
# the type is.
#
# Siding regions, stacked from the ground: (z where each starts, atlas band,
# the z that band's first row stands for).
# - The parapet reads the gable band S2 from the deck up, so S2's belt board
#   becomes a trim band round the porch at the balcony floor, and the corner
#   boards stop under it as they do under a gable's belt.
# - The dormer front, to 6.40 m, is taller than S1's painted 4.44 m, so it
#   reads S1 shifted down two metres: whole 0.125 m courses, and S1's
#   under-soffit shadow lands right under the dormer's soffit.
EAVE_BANDS, GABLE_BANDS = L.EAVE_BANDS, L.GABLE_BANDS
PORCH_BANDS = [(0.0, "S1", 0.0), (DECK_Z, "S2", DECK_Z)]
DORMER_BANDS = [(0.0, "S1", 2.0)]

# Wall tops as (s, z) profiles; a plain height stands for a level top.
GABLE_TOP = [(0.0, L.Z_WALL_TOP), (HY, Z_APEX), (2 * HY, L.Z_WALL_TOP)]
# the dormer section's east side, s = y + 4: dormer top, then the house's lid
CHEEK_TOP = [(0.0, DZ_TOP), (D_JOIN, L.Z_WALL_TOP + D_JOIN * TAN), (HY, Z_APEX),
             (2 * HY, L.Z_WALL_TOP)]
CHEEK_TOP_W = [(2 * HY - s, z) for s, z in reversed(CHEEK_TOP)]

# Each solid's walls (rintamamiestalo.Wall). Gable ends carry one window per
# storey: the wide living-room window below, centred under the wide attic
# window above. Two smaller windows side by side read as busier than the type
# is, and one large one is the catalog's rule for short walls (CLAUDE.md,
# Style Direction).
WEST_WALLS = [
    # s = x + 5
    Wall("front_w", (-HX, -HY), (BX0, -HY), L.Z_WALL_TOP, [("std", 1.40, GF)],
         (True, False), EAVE_BANDS, None),
    # against the dormer section, merged away
    Wall("join_w", (BX0, -HY), (BX0, HY), GABLE_TOP, [], (False, False), GABLE_BANDS,
         L.Z_EAVE),
    # s = -2.2 - x
    Wall("rear_w", (BX0, HY), (-HX, HY), L.Z_WALL_TOP,
         [("std", 1.40, GF), ("cellar", 1.40, 0.25)], (False, True), EAVE_BANDS, None),
    # s = 4 - y
    Wall("west", (-HX, HY), (-HX, -HY), GABLE_TOP, [
        ("wide", 4.00, GF), ("wide", 4.00, ATTIC_SILL),
        ("vent", 4.00, 7.35), ("cellar", 2.00, 0.25)],
         (True, True), GABLE_BANDS, L.Z_EAVE),
]
EAST_WALLS = [
    # s = x - 2.2
    Wall("front_e", (BX1, -HY), (HX, -HY), L.Z_WALL_TOP,
         [("std", 1.40, GF), ("cellar", 1.40, 0.25)], (False, True), EAVE_BANDS, None),
    # s = y + 4
    Wall("east", (HX, -HY), (HX, HY), GABLE_TOP, [
        ("wide", 4.00, GF), ("wide", 4.00, ATTIC_SILL),
        ("vent", 4.00, 7.35), ("cellar", 6.10, 0.25)],
         (True, True), GABLE_BANDS, L.Z_EAVE),
    # s = 5 - x
    Wall("rear_e", (HX, HY), (BX1, HY), L.Z_WALL_TOP, [("std", 1.40, GF)],
         (True, False), EAVE_BANDS, None),
    Wall("join_e", (BX1, HY), (BX1, -HY), GABLE_TOP, [], (False, False), GABLE_BANDS,
         L.Z_EAVE),
]
DORMER_WALLS = [
    # s = x + 2.2: the balcony door at the attic floor, its one opening, as a
    # gable carries one per storey; below the deck this wall is merged away
    Wall("dormer_front", (BX0, -HY), (BX1, -HY), DZ_TOP, [
        ("door_balcony", 2.20, DECK_Z + 0.05)], (PARAPET_Z, PARAPET_Z),
         DORMER_BANDS, None),
    # the dormer's side walls above the main roof; below it, merged away
    Wall("cheek_e", (BX1, -HY), (BX1, HY), CHEEK_TOP, [], (PARAPET_Z, False),
         GABLE_BANDS, None),
    # s = 2.2 - x: the back door and the bathroom
    Wall("rear_m", (BX1, HY), (BX0, HY), L.Z_WALL_TOP, [
        ("door_back", BX1 - BACK_DOOR_X, L.Z_FLOOR), ("bath", 3.20, 2.20)],
         (False, False), EAVE_BANDS, None),
    Wall("cheek_w", (BX0, HY), (BX0, -HY), CHEEK_TOP_W, [], (False, PARAPET_Z),
         GABLE_BANDS, None),
]
PORCH_WALLS = [
    # s = -4 - y
    Wall("porch_w", (BX0, -HY), (BX0, PY_FRONT), PARAPET_Z, [("std", 1.30, GF)],
         (False, True), PORCH_BANDS, DECK_Z),
    # s = x + 2.2: the entrance beside a wide window
    Wall("porch_front", (BX0, PY_FRONT), (BX1, PY_FRONT), PARAPET_Z, [
        ("door_front", FRONT_DOOR_S, L.Z_FLOOR), ("wide", 3.00, GF)],
         (True, True), PORCH_BANDS, DECK_Z),
    # s = y + 6.6
    Wall("porch_e", (BX1, PY_FRONT), (BX1, -HY), PARAPET_Z, [("std", 1.30, GF)],
         (True, False), PORCH_BANDS, DECK_Z),
]
ALL_WALLS = WEST_WALLS + EAST_WALLS + DORMER_WALLS + PORCH_WALLS
WALLS = {w.name: w for w in ALL_WALLS}
HOUSE_EDGE = [0.0, L.Z_EAVE, L.Z_WALL_TOP, L.Z_FLASH]
# Offsets into the tiling siding band, so butt joints differ wall to wall. The
# pieces of the rear wall carry on from each other, since they meet in one
# plane; so do the two front pieces, though the porch stands between them.
U_OFF = {"front_w": 0.0, "front_e": 7.2, "dormer_front": 2.8, "east": 3.3,
         "rear_e": 6.1, "rear_m": 8.9, "rear_w": 13.3, "west": 9.4,
         "join_w": 0.0, "join_e": 0.0, "cheek_e": 4.1, "cheek_w": 11.7,
         "porch_w": 2.2, "porch_front": 0.3, "porch_e": 5.7}

# Downpipes (scripts/downpipes.py): one from each eave's gutter, at
# diagonally opposite corners, so each gable end shows one: the front's at
# its east end, the rear's at its west. The porch and the dormer take the
# middle of the front, so each eave's gutter drains to its outer end.
DOWNPIPE_SPOTS = [("front_e", HX - BX1 - DP.CORNER), ("rear_w", HX + BX0 - DP.CORNER)]
DOWNPIPES = [DP.eave_pipe(WALLS[w].p0, WALLS[w].p1, s, L.Z_EAVE, TAN, EAVE_OV)
             for w, s in DOWNPIPE_SPOTS]

# Roof safety kit (scripts/roof_safety.py), the sweep's way to the chimney.
# The porch and the dormer take the front, and its outer pieces are too short
# for a ladder beside their windows and downpipe, so the kit is on the rear:
# a wall ladder between the bathroom and the west window, the roof ladder
# straight above it up the rear slope, and a level walkway along the slope
# 0.5 m below the ridge, east to stand behind the stack. The rear wall's
# three pieces lie in one plane, so the kit takes the whole of it as its eave.
REAR = ((HX, HY), (-HX, HY))                      # s = 5 - x
KIT_S = HX + 2.15
EAVE_REAR = RS.Eave(*REAR, L.Z_EAVE, EAVE_OV, L.Z_EAVE + ROOF_T - EAVE_OV * TAN, TAN)
WALK_OUT = -HY + 0.50 + RS.WALK_W                 # the walkway's downslope edge
ROOF_KIT = [
    RS.WallLadder(EAVE_REAR, KIT_S),
    RS.RoofLadder(EAVE_REAR, KIT_S, EAVE_REAR.roof_z(WALK_OUT)),
    RS.Walkway(EAVE_REAR, HX - CHIMNEY[1], KIT_S + RS.HALF, WALK_OUT),
]

# Handrails (scripts/handrails.py) on both flights: each climbs 0.68 m in
# three risers to its landing, so each gets a rail on its right going up.
HANDRAILS = [
    HR.Flight(*FRONT_STEPS, PY_FRONT, -1.0, STEP_PROFILE),
    HR.Flight(*BACK_STEPS, HY, 1.0, STEP_PROFILE),
]


# ================================================================== solids
def west_block(level):
    return K.body(level, WEST_WALLS, HOUSE_EDGE, U_OFF,
                  ridges=[[(-HX, 0.0, Z_APEX), (BX0, 0.0, Z_APEX)]])


def east_block(level):
    return K.body(level, EAST_WALLS, HOUSE_EDGE, U_OFF,
                  ridges=[[(BX1, 0.0, Z_APEX), (HX, 0.0, Z_APEX)]])


def dormer_section(level):
    """The middle third of the house, with its front wall carried up into the
    dormer. Its lid is split at the ridge and where the dormer top meets the
    house's roof line."""
    y_j, z_j = -HY + D_JOIN, L.Z_WALL_TOP + D_JOIN * TAN
    return K.body(level, DORMER_WALLS, HOUSE_EDGE + [PARAPET_Z], U_OFF,
                  ridges=[[(BX0, 0.0, Z_APEX), (BX1, 0.0, Z_APEX)],
                          [(BX0, y_j, z_j), (BX1, y_j, z_j)]])


def porch_and_balcony(level):
    """The porch with the balcony on its roof, as one closed solid: sided walls
    carried up past the deck as a solid parapet, a cap board round the top,
    the parapet's inner faces and the deck. Its back face lies on the dormer
    section's front wall, and the union merges the two away."""
    B = K.Builder()
    edge = [0.0, DECK_Z, PARAPET_Z, L.Z_FLASH]
    K.ring(B, PORCH_WALLS, edge, level, U_OFF)
    t = PARAPET_T
    x0, x1, yf, yb = BX0, BX1, PY_FRONT, -HY
    xi0, xi1, yi = x0 + t, x1 - t, yf + t
    zt, zd = PARAPET_Z, DECK_Z

    # Cap board: one U-shaped face. Its outer edge carries every vertex the
    # wall tops have, the corner-board columns' included, and those sit
    # exactly on the parapet's inner lines because it is one board thick.
    outer = [(x0, yb), (x0, yi), (x0, yf), (xi0, yf), (xi1, yf), (x1, yf),
             (x1, yi), (x1, yb)]
    inner = [(xi1, yb), (xi1, yi), (xi0, yi), (xi0, yb)]
    B.face([(x, y, zt) for x, y in outer + inner], K.uv_patch("trim"))

    # the parapet's inner faces, sided like its outer ones, the belt at their
    # foot making a skirting round the deck
    for p0, p1 in (((xi1, yi), (xi0, yi)), ((xi0, yi), (xi0, yb)),
                   ((xi1, yb), (xi1, yi))):
        fr = SB.InwardFrame(p0, p1)
        B.face([fr.P(0.0, zd), fr.P(fr.L, zd), fr.P(fr.L, zt), fr.P(0.0, zt)],
               K.uv_band(fr, L.S2_Y0, DECK_Z, 0.0))
    B.face([(xi0, yi, zd), (xi1, yi, zd), (xi1, yb, zd), (xi0, yb, zd)],
           K.uv_patch("deck"))

    # the back, on the house wall: the porch's full width up to the deck and
    # the two parapet ends above it, through every height the side walls carry
    side = sorted({e for e in edge if e < zt - EPS} | {zt})
    back = ([(x0, 0.0), (x1, 0.0)] + [(x1, z) for z in side if z > EPS]
            + [(xi1, zt), (xi1, zd), (xi0, zd), (xi0, zt)]
            + [(x0, z) for z in reversed(side) if z > EPS])
    B.face([(x, yb, z) for x, z in back], K.uv_patch("blank"))
    SB.close_solid(B, K.uv_patch("blank"), count=1)
    return B


def dormer_roof():
    """The dormer's shed roof: a slab falling to the front at D_PITCH, from its
    eave over the balcony back into the main roof, which buries its back end.
    Mapped like the main roof: fascia band on the front edge, roof band up the
    slope from the eave, barge boards at the sides."""
    yf, yb = -HY - EAVE_OV, -HY + D_BACK

    def under(y):
        return DZ_EAVE + D_PITCH * (y + HY)

    sec = [(yf, under(yf)), (yf, under(yf) + ROOF_T), (yb, under(yb) + ROOF_T),
           (yb, under(yb))]
    kinds = ("fascia", "slope", "back", "soffit")
    sf = math.sqrt(1.0 + D_PITCH * D_PITCH)

    def slope_uv(co):
        return ((co.x + 16.0) * PPM, L.ROOF_Y0 + (co.y - yf) * sf * L.ROOF_RPM)

    def fascia_uv(co):
        return ((co.x + 16.0) * PPM, L.FASC_Y0 + (co.z - under(yf)) * PPM)

    fns = {"fascia": fascia_uv, "slope": slope_uv, "soffit": K.uv_patch("soffit"),
           "back": K.uv_patch("blank")}
    return K.slab("x", 0.0, sec, kinds, BX0 - D_RAKE_OV, BX1 + D_RAKE_OV, fns)


# ================================================================ assembly
def build_lod(level):
    base = to_object(west_block(level), "tmp_west")
    roof = lambda a0, a1, cut=None: K.gable_slab("x", 0.0, HY, L.Z_EAVE, EAVE_OV,  # noqa: E731
                                                a0, a1, cut)
    parts = [
        to_object(east_block(level), "tmp_east"),
        to_object(dormer_section(level), "tmp_dormer"),
        to_object(porch_and_balcony(level), "tmp_porch"),
        to_object(roof(-HX - RAKE_OV, BX0), "tmp_roof_w"),
        to_object(roof(BX0, BX1, cut=-HY + MAIN_CUT), "tmp_roof_m"),
        to_object(roof(BX1, HX + RAKE_OV), "tmp_roof_e"),
        to_object(dormer_roof(), "tmp_dormer_roof"),
        to_object(K.chimney(CHIMNEY), "tmp_chimney"),
    ]
    return K.tier(level, base, parts, STEPS, (CANOPY_X, HY), DOWNPIPES, ROOF_KIT, HANDRAILS)


def check_layout():
    """Assert the constraints that are invisible in the numbers and obvious
    once rendered: the family's (openings colliding, clipping a roof or a
    corner board, or straddling a band change; the gable outgrowing its atlas
    band; the canopy, the flue, the walkway) and this house's: a band read
    past its painted rows; the dormer's roof and the main roof failing to
    bury each other's cut ends; the balcony short of headroom; the downpipes
    and the wall ladder crowding each other or the back door."""
    problems = K.apex_problems(Z_APEX) + K.slope_problems(HY)

    # S1 is painted from the flashing to 4.44 m. The dormer front reads it
    # shifted, and must stay inside that, above the plinth where it shows, and
    # in board phase. The parapet reads S2 from its belt up.
    s1_top = (286.0 - L.S1_Y0) / PPM
    zref = DORMER_BANDS[0][2]
    if DZ_TOP - zref > s1_top + EPS:
        problems.append("dormer front reads S1 up to %.2f m, painted to %.2f"
                        % (DZ_TOP - zref, s1_top))
    if DECK_Z - zref < L.Z_FLASH - EPS:
        problems.append("dormer front shows S1's plinth above the deck")
    if abs(zref / L.BOARD - round(zref / L.BOARD)) > 1e-6:
        problems.append("dormer front's shift is not whole siding courses")
    if PARAPET_Z - DECK_Z > L.S2_SPAN:
        problems.append("parapet is taller than the S2 band")

    # a porch wall's top is its parapet, not a roof
    problems += K.opening_problems(ALL_WALLS, open_top={w.name for w in PORCH_WALLS})

    # the roofs' cut and back ends have to finish buried
    if not MAIN_CUT < D_JOIN < HY:
        problems.append("the main slab's cut (%.2f) must fall inside the dormer, "
                        "before it meets the roof (%.2f)" % (MAIN_CUT, D_JOIN))
    if L.Z_EAVE + ROOF_T + MAIN_CUT * TAN > DZ_TOP + D_PITCH * MAIN_CUT - 0.05:
        problems.append("the main slab's cut end pokes out of the dormer")
    if DZ_EAVE + ROOF_T + D_PITCH * D_BACK > L.Z_WALL_TOP + D_BACK * TAN - 0.02:
        problems.append("the dormer roof's back end pokes out of the main roof")
    # the main eave dies into the parapet's side, so the parapet must be taller
    if L.Z_EAVE + ROOF_T > PARAPET_Z - 0.05:
        problems.append("the main eave rises past the balcony parapet")
    head = DZ_EAVE - D_PITCH * EAVE_OV - DECK_Z
    if head < 2.2:
        problems.append("dormer fascia is %.2f m over the balcony deck" % head)

    rear = WALLS["rear_m"]
    door = next(K.item_rects(k, s, z)[0] for k, s, z in rear.items if k == "door_back")
    problems += K.canopy_problems(rear, door, CANOPY_X)
    problems += K.flue_problems(CHIMNEY, Z_RIDGE)
    # downpipes clear of the corners and the openings
    for (w, _s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        avoid = [(k,) + K.item_rects(k, c, z)[0][:2] for k, c, z in WALLS[w].items]
        problems += DP.problems(pipe, "the %s downpipe" % w, avoid)
    # the roof kit: the wall ladder clear of the rear's corners, openings,
    # back steps, canopy and downpipe, in the rear line's s = 5 - x; the
    # walkway behind the stack, clear of it and of the ridge
    wall = ROOF_KIT[0]
    avoid = []
    for w in ("rear_e", "rear_m", "rear_w"):
        x0 = WALLS[w].p0[0]
        avoid += [(k, HX - x0 + a, HX - x0 + b)
                  for k, c, z in WALLS[w].items for a, b in [K.item_rects(k, c, z)[0][:2]]]
    avoid += [("back steps", HX - BACK_STEPS[1], HX - BACK_STEPS[0]),
              ("back canopy", HX - CANOPY_X[1], HX - CANOPY_X[0])]
    for (w, _s), p in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        c = p.point(0.0, 0.0, 0.0)
        if abs(c.y - HY) < 0.2:
            avoid.append(("downpipe", HX - c.x - DP.A, HX - c.x + DP.A))
    problems += RS.problems(wall, "the wall ladder", avoid)
    problems += HR.problems(HANDRAILS[0], "the front handrail", L.OPENINGS["door_front"][0])
    problems += HR.problems(HANDRAILS[1], "the back handrail", L.OPENINGS["door_back"][0])
    problems += K.rear_walkway_problems(ROOF_KIT[2], CHIMNEY, HX, HY)
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
# Storeys: the ground floor on the plinth and the attic, whose floor is the
# balcony door's threshold, 5 cm over the deck.
Z_ATTIC = DECK_Z + 0.05


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the main block with the enclosed
    porch, whose walls stand on the ground like the block's own; the balcony
    on the porch's roof is open and counts in no storey. The attic counts
    where a roof's underside is 1.6 m or more over its floor: the strip under
    the main roof, and in front of it the dormer's width out to the front
    wall, where the dormer's roof is the higher one."""
    attic_w = model_facts.roof_clear_width(2 * HY, Z_ATTIC, L.Z_EAVE, TAN)
    lost = (2 * HY - attic_w) / 2.0              # the low strip along each eave
    if DZ_EAVE < Z_ATTIC + 1.6:
        raise ValueError("the dormer's soffit is under 1.6 m over the attic floor")
    return {
        "hero": False,
        "dwellings": 1,
        "footprint": [(-HX, HY), (-HX, -HY), (BX0, -HY), (BX0, PY_FRONT),
                      (BX1, PY_FRONT), (BX1, -HY), (HX, -HY), (HX, HY)],
        "storeys": [
            (L.Z_FLOOR, 2 * HX * 2 * HY + (BX1 - BX0) * (-HY - PY_FRONT)),
            (Z_ATTIC, 2 * HX * attic_w + (BX1 - BX0) * lost),
        ],
        "doors": [K.door(WALLS, "front", "entrance", "porch_front", "door_front", main=True),
                  K.door(WALLS, "back", "service", "rear_m", "door_back"),
                  K.door(WALLS, "balcony", "balcony", "dormer_front", "door_balcony")],
    }


render_views = K.render_views

if __name__ == "__main__":
    BUILD.main(build_all, facts)
