# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of rintamamiestalo_gable_entry, all four LOD tiers.

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
brick chimney on the ridge. This one stands with a gable end to the street
and its entrance in that gable:

- a terrace the full width of the house in front of the door;
- over the door, a balcony, reached from the attic storey by a pair of glazed
  doors;
- the back door in the far gable.

Construction is a set of closed solids unioned with Blender's exact boolean:
the house, the roof slab, the chimney, the terrace, the balcony slab, the
railing boards standing on both, the back-door canopy and the two flights of
steps. Wherever two solids meet face to face, the union merges the faces away,
so the result is the boundary of one empty volume and interior geometry cannot
occur.

The walls are textured as a trim sheet (see facade_atlas.py): siding tiles,
and each window or door is a hole in the wall with its own faces mapped to the
region that carries its casing and glazing. What the four rintamamiestalo
houses share (the walls and openings, roofs, chimney, canopy, steps, the tier
policy and the common checks) is scripts/rintamamiestalo.py's; this file keeps
the house: its massing, its walls, the terrace and the balcony with their
railings, the places of its downpipes, roof kit and handrails, its own checks
and its facts.
"""

import importlib
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
    ATTIC_SILL, CANOPY_T, CANOPY_Z, EAVE_OV, EPS, GF, PPM, RAKE_OV, ROOF_T, STEP_PROFILE,
    TAN, Steps, Wall)

L = facade_atlas.LAYOUT
K = R.Kit(L, HERE)
BUILD = K.asset

# ------------------------------------------------------------------ massing
# Front faces -Y, and the front is a gable end: the siblings' 10.0 x 8.0 m
# block turned so that its ridge runs back from the street along Y. The street
# sees the 8 m gable with the entrance in it.
HX, HY = 4.0, 5.0
Z_APEX = L.Z_WALL_TOP + HX * TAN                 # body apex, inside the slab
Z_RIDGE = L.Z_EAVE + ROOF_T + HX * TAN           # top of the ridge

# The terrace runs the house's full width, flush with both long walls, and is
# 2.4 m deep. Its deck is 5 cm under the front door's threshold, on a concrete
# base like the house's plinth.
# - The railing is a solid board, as CLAUDE.md asks of a balcony's parapet: a
#   see-through one would need alpha. Its balusters and handrail are painted,
#   and its top face is the cap.
# - The steps come off the front edge through a gap in the railing, centred
#   on the door, so the way in runs straight from the street.
TERRACE_Y = -HY - 2.40
TERRACE_Z = 0.65
TERRACE_RAIL_Z = TERRACE_Z + 0.90
RAIL_T = 0.10                    # railing board thickness
HANDRAIL_H = 0.10                # the painted handrail band along its top
STEPS_X = (-0.70, 0.70)

# The balcony is a slab cantilevered 1.2 m off the front gable at the attic
# floor. It is centred over the front door, so it is the door's canopy too.
# Its deck is at the gables' belt height.
BAL_X = (-1.60, 1.60)
BAL_Y = -HY - 1.20
BAL_T = 0.20
DECK_Z = L.Z_BELT
BAL_RAIL_Z = DECK_Z + 1.00

CHIMNEY = (-0.42, 0.42, 0.40, 1.00, 7.60, Z_RIDGE + 0.95)

# Terrace steps: three treads down from the terrace, whose own edge is the
# top riser, so four equal risers of 0.1625 m; LOD3 keeps their footprint as
# a ramp, as it does the back steps' (rintamamiestalo.STEP_PROFILE).
TERRACE_STEP_PROFILE = [(-0.05, 0.0), (-0.05, 0.4875), (0.28, 0.4875),
                        (0.28, 0.325), (0.56, 0.325), (0.56, 0.1625),
                        (0.84, 0.1625), (0.84, 0.0)]
TERRACE_STEP_PROFILE_LOW = [(-0.05, 0.0), (-0.05, 0.4875), (0.28, 0.4875),
                            (0.84, 0.0)]
BACK_DOOR_X = 1.80
BACK_STEPS = (BACK_DOOR_X - 0.70, BACK_DOOR_X + 0.70)   # along x, off the rear gable
CANOPY_X = (BACK_DOOR_X - 0.75, BACK_DOOR_X + 0.75)     # the back-door canopy
STEPS = [Steps("tmp_steps_f", *STEPS_X, TERRACE_Y, -1.0, TERRACE_STEP_PROFILE,
               TERRACE_STEP_PROFILE_LOW),
         Steps("tmp_steps_r", *BACK_STEPS, HY, 1.0)]

# --------------------------------------------------------------- elevations
# The attic floor is 3.90 m, 5 cm over the balcony deck, and the attic window
# sits 0.75 m above it. The front gable has the balcony doors at that level
# instead of the attic window, so only the rear gable carries one. The gables
# switch to S2, whose belt board is at its foot, at the attic floor (Z_BELT in
# the atlas's layout).
BAL_DOOR_SILL = DECK_Z + 0.05
GABLE_TOP = [(0.0, L.Z_WALL_TOP), (HX, Z_APEX), (2 * HX, L.Z_WALL_TOP)]

# Openings as (kind, s, sill z), s being the centre measured along the wall
# from its start.
# The gables carry one window per storey besides their doors, the entrance
# storey of the front gable excepted: two smaller windows side by side read
# busier than the type is, and one large one is the catalog's rule for short
# walls (CLAUDE.md, Style Direction). The long walls keep several.
# Front gable, s = x + 4: the entrance under the balcony between two wide
# windows, the living room's and the kitchen's, mirrored about the door, and
# the balcony doors over it. Two windows on one storey of a gable is what
# CLAUDE.md allows an entrance gable: the door in the middle splits the
# storey, so they flank it rather than stand side by side.
FRONT_ITEMS = [("wide", 1.90, GF), ("door_front", HX, L.Z_FLOOR), ("wide", 6.10, GF),
               ("door_balcony", HX, BAL_DOOR_SILL), ("vent", HX, 7.35)]
# Rear gable, s = 4 - x: the back door and one wide window, and the one wide
# attic window lighting the attic from this end, as on the siblings.
REAR_ITEMS = [("door_back", HX - BACK_DOOR_X, L.Z_FLOOR),
              ("wide", 5.20, GF), ("cellar", 5.20, 0.25),
              ("wide", 4.00, ATTIC_SILL), ("vent", HX, 7.35)]
# east long wall, s = y + 5
EAST_ITEMS = [("std", 1.90, GF), ("wide", 5.30, GF), ("std", 8.30, GF),
              ("cellar", 5.30, 0.25)]
# west long wall, s = 5 - y: the living room's second window at the front
WEST_ITEMS = [("std", 1.80, GF), ("std", 5.00, GF), ("wide", 8.20, GF),
              ("cellar", 1.80, 0.25)]

# The house's walls (rintamamiestalo.Wall). Corners are the boards at the
# start and end. On the gables they run the full height and the belt board
# runs between them.
E, G = L.EAVE_BANDS, L.GABLE_BANDS
HOUSE_WALLS = [
    Wall("front", (-HX, -HY), (HX, -HY), GABLE_TOP, FRONT_ITEMS, (True, True), G),
    Wall("east", (HX, -HY), (HX, HY), L.Z_WALL_TOP, EAST_ITEMS, (True, True), E),
    Wall("rear", (HX, HY), (-HX, HY), GABLE_TOP, REAR_ITEMS, (True, True), G),
    Wall("west", (-HX, HY), (-HX, -HY), L.Z_WALL_TOP, WEST_ITEMS, (True, True), E),
]
WALLS = {w.name: w for w in HOUSE_WALLS}
HOUSE_EDGE = [0.0, L.Z_BELT, L.Z_EAVE, L.Z_WALL_TOP, L.Z_FLASH]
# Offsets into the tiling siding band, so butt joints differ wall to wall.
U_OFF = {"front": 0.0, "east": 3.3, "rear": 6.1, "west": 9.4}

# Downpipes (scripts/downpipes.py): one from each eave's gutter, at
# diagonally opposite corners: the east eave's at the street end, where it
# stands behind the terrace's railing, the west eave's at the back.
DOWNPIPE_SPOTS = [("east", DP.CORNER), ("west", DP.CORNER)]
DOWNPIPES = [DP.eave_pipe(WALLS[n].p0, WALLS[n].p1, s, L.Z_EAVE, TAN, EAVE_OV)
             for n, s in DOWNPIPE_SPOTS]

# Roof safety kit (scripts/roof_safety.py), the sweep's way to the chimney,
# at the back, away from the entrance, as such kits usually are. The gables
# take the front door and the back door, and a ladder has to pass an eave, so
# it stands on the west eave wall's rear half, the side away from the
# catalog's view: a wall ladder between the two standard windows, the roof
# ladder straight above it up the west slope, and a level walkway along the
# slope 0.5 m below the ridge, forward to stand beside the stack. The wall
# ladder stands outside the eave, the building's widest point on this side,
# so LOD3 keeps its bare rails and every tier keeps LOD0's extents and pivot.
WEST = WALLS["west"]                              # s = 5 - y
KIT_S = 3.40                                      # centred between the windows
EAVE_WEST = RS.Eave(WEST.p0, WEST.p1, L.Z_EAVE, EAVE_OV, L.Z_EAVE + ROOF_T - EAVE_OV * TAN, TAN)
WALK_OUT = -HX + 0.50 + RS.WALK_W                 # the walkway's downslope edge
ROOF_KIT = [
    RS.WallLadder(EAVE_WEST, KIT_S),
    RS.RoofLadder(EAVE_WEST, KIT_S, EAVE_WEST.roof_z(WALK_OUT)),
    RS.Walkway(EAVE_WEST, KIT_S - RS.HALF, HY - CHIMNEY[2], WALK_OUT),
]

# Handrails (scripts/handrails.py) on both flights, each on its right going
# up. The terrace steps fall 0.65 m in four risers from the deck; their rail
# starts on the deck against the end of the east railing board at the gap
# (inset 0), at the board's own height, so railing and handrail read as one.
# The back steps climb 0.68 m in three risers to their landing.
HANDRAILS = [
    HR.Flight(*STEPS_X, TERRACE_Y, -1.0, TERRACE_STEP_PROFILE, top=TERRACE_Z,
              inset=0.0),
    HR.Flight(*BACK_STEPS, HY, 1.0, STEP_PROFILE),
]


# ======================================================= terrace and balcony
def uv_deck(co):
    """Deck boards running along X: Y walks across the strip's boards, and
    every point samples the strip at the same V."""
    return ((co.y + 16.0) * PPM, L.DECK_Y0 + L.DECK_H / 2.0)


def uv_rail(fr, z0, z1):
    """The baluster strip. U runs along the railing in world metres, so the
    balusters on a board's two faces line up; V squeezes z0..z1 into the
    strip's rows, texel centre to texel centre."""
    along_x = abs(fr.t.x) > 0.5

    def fn(co):
        t = min(max((co.z - z0) / (z1 - z0), 0.0), 1.0)
        return (((co.x if along_x else co.y) + 16.0) * PPM,
                L.RAIL_Y0 + 0.5 + t * (L.RAIL_H - 1.0))
    return fn


def box(x0, x1, y0, y1, zs, side_uv, top_uv, bottom_uv):
    """A closed box on a plan rectangle. Its sides are split at every height
    in *zs* (ascending, the first and last being its bottom and top), so each
    band of a side can take its own mapping: side_uv(frame, k) for band k.
    Kept here rather than shell_build.box(): the banded sides are not a
    prism's one face per edge."""
    B = K.Builder()
    rim = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for i in range(4):
        fr = SB.InwardFrame(rim[i], rim[(i + 1) % 4])
        for k in range(len(zs) - 1):
            B.face([fr.P(0.0, zs[k]), fr.P(fr.L, zs[k]), fr.P(fr.L, zs[k + 1]),
                    fr.P(0.0, zs[k + 1])], side_uv(fr, k))
    B.face([(x, y, zs[-1]) for x, y in rim], top_uv)
    B.face([(x, y, zs[0]) for x, y in reversed(rim)], bottom_uv)
    return B


def railing(x0, x1, y0, y1, zb, zt):
    """One railing board standing on a deck. Balusters are painted up to the
    handrail band. The handrail, the cap and the board's 0.1 m ends are
    plain trim, and the ends read as posts."""
    zs = (zb, zt - HANDRAIL_H, zt)
    trim = K.uv_patch("trim")

    def side(fr, k):
        return uv_rail(fr, zb, zs[1]) if k == 0 and fr.L > RAIL_T + EPS else trim
    return box(x0, x1, y0, y1, zs, side, trim, K.uv_patch("blank"))


def terrace():
    """The terrace's concrete base with the deck on top, and its railing.
    The railing is a board along the front on each side of the steps, and
    one down each side to the house. The side boards start behind the front
    ones, so no two boards overlap, and the union merges away every face
    they share with the base, each other and the house."""
    t, z0, z1 = RAIL_T, TERRACE_Z, TERRACE_RAIL_Z
    yf, yb = TERRACE_Y, -HY
    base = box(-HX, HX, yf, yb, (0.0, z0),
               lambda fr, k: K.uv_band(fr, L.S1_Y0, 0.0, 0.0), uv_deck, K.uv_patch("blank"))
    return [("terrace", base),
            ("rail_fw", railing(-HX, STEPS_X[0], yf, yf + t, z0, z1)),
            ("rail_fe", railing(STEPS_X[1], HX, yf, yf + t, z0, z1)),
            ("rail_w", railing(-HX, -HX + t, yf + t, yb, z0, z1)),
            ("rail_e", railing(HX - t, HX, yf + t, yb, z0, z1))]


def balcony():
    """The balcony: a slab with trim-faced edges, a soffit under it and the
    deck on top, and three railing boards on it."""
    x0, x1 = BAL_X
    t, yf, yb = RAIL_T, BAL_Y, -HY
    deck = box(x0, x1, yf, yb, (DECK_Z - BAL_T, DECK_Z),
               lambda fr, k: K.uv_patch("trim"), uv_deck, K.uv_patch("soffit"))
    return [("balcony", deck),
            ("rail_bf", railing(x0, x1, yf, yf + t, DECK_Z, BAL_RAIL_Z)),
            ("rail_bw", railing(x0, x0 + t, yf + t, yb, DECK_Z, BAL_RAIL_Z)),
            ("rail_be", railing(x1 - t, x1, yf + t, yb, DECK_Z, BAL_RAIL_Z))]


# ================================================================ assembly
def build_lod(level):
    base = to_object(K.body(level, HOUSE_WALLS, HOUSE_EDGE, U_OFF,
                            ridges=[[(0.0, -HY, Z_APEX), (0.0, HY, Z_APEX)]]), "tmp_house")
    parts = [
        to_object(K.gable_slab("y", 0.0, HX, L.Z_EAVE, EAVE_OV,
                               -HY - RAKE_OV, HY + RAKE_OV), "tmp_roof"),
        to_object(K.chimney(CHIMNEY), "tmp_chimney"),
    ]
    parts += [to_object(B, "tmp_" + name) for name, B in terrace() + balcony()]
    return K.tier(level, base, parts, STEPS, (CANOPY_X, HY), DOWNPIPES, ROOF_KIT, HANDRAILS,
                  kit_extents=True)


def check_layout():
    """Assert the constraints that are invisible in the numbers and obvious
    once rendered: the family's (openings colliding, clipping a roof or a
    corner board, or straddling a band change; the gable outgrowing its
    atlas band; the canopy, the flue) and this house's:
    - the gables' belt missing the fascia line;
    - something standing against the front gable across an opening;
    - the balcony missing the doors it serves;
    - the terrace's steps off the door's centre line or crowding a corner;
    - the back canopy running into the belt;
    - the downpipes, the wall ladder and the walkway out of place."""
    problems = K.apex_problems(Z_APEX) + K.slope_problems(HX)
    fascia_foot = L.Z_EAVE - EAVE_OV * TAN
    if abs(L.Z_BELT - fascia_foot) > EPS:
        problems.append("the gables' belt at %.2f is off the fascia's lower edge at %.2f"
                        % (L.Z_BELT, fascia_foot))
    problems += K.opening_problems(HOUSE_WALLS)

    # What stands against the front gable, as (x0, x1, z0, z1). It may not
    # cover any part of an opening's casing.
    contacts = {
        "terrace": (-HX, HX, 0.0, TERRACE_Z),
        "terrace's west railing": (-HX, -HX + RAIL_T, TERRACE_Z, TERRACE_RAIL_Z),
        "terrace's east railing": (HX - RAIL_T, HX, TERRACE_Z, TERRACE_RAIL_Z),
        "balcony slab": (BAL_X[0], BAL_X[1], DECK_Z - BAL_T, DECK_Z),
        "balcony's west railing": (BAL_X[0], BAL_X[0] + RAIL_T, DECK_Z, BAL_RAIL_Z),
        "balcony's east railing": (BAL_X[1] - RAIL_T, BAL_X[1], DECK_Z, BAL_RAIL_Z),
    }
    for k, s, z in FRONT_ITEMS:
        l, r, b, t = K.item_rects(k, s, z)[0]
        for what, (x0, x1, z0, z1) in contacts.items():
            if l - HX < x1 and x0 < r - HX and b < z1 and z0 < t:
                problems.append("front: the %s stands across the %s" % (what, k))

    # The balcony roofs the front door, and holds the balcony doors between
    # its railings with room to step out.
    l, r, b, t = K.item_rects("door_front", HX, L.Z_FLOOR)[0]
    if not (BAL_X[0] < l - HX and r - HX < BAL_X[1]):
        problems.append("the balcony does not cover the front door")
    if DECK_Z - BAL_T < t + 0.30:
        problems.append("the balcony slab sits on the front door's casing")
    if abs(sum(STEPS_X) / 2.0 - ((l + r) / 2.0 - HX)) > EPS:
        problems.append("the terrace steps are not centred on the front door")
    if STEPS_X[1] - STEPS_X[0] < r - l:
        problems.append("the terrace steps are narrower than the front door's casing")
    if DECK_Z - BAL_T - TERRACE_Z < 2.2:
        problems.append("the balcony is below head height over the terrace")
    l, r, b, t = K.item_rects("door_balcony", HX, BAL_DOOR_SILL)[0]
    if not (BAL_X[0] + RAIL_T + 0.30 < l - HX and r - HX < BAL_X[1] - RAIL_T - 0.30):
        problems.append("the balcony doors are not well inside its railings")
    if TERRACE_Z > L.Z_FLOOR - 0.02:
        problems.append("the terrace deck is not under the front door's threshold")
    if STEPS_X[0] < -HX + RAIL_T + 0.30 or STEPS_X[1] > HX - RAIL_T - 0.30:
        problems.append("the terrace steps crowd a corner of the railing")
    top = TERRACE_STEP_PROFILE[1][1]
    risers = [TERRACE_Z - top] + [TERRACE_STEP_PROFILE[k][1] - TERRACE_STEP_PROFILE[k + 1][1]
                                  for k in (2, 4, 6)]
    if max(risers) - min(risers) > 1e-6:
        problems.append("the terrace steps' risers differ: %s" % risers)

    door = next(K.item_rects(k, s, z)[0] for k, s, z in REAR_ITEMS if k == "door_back")
    problems += K.canopy_problems(WALLS["rear"], door, CANOPY_X)
    if CANOPY_Z[0] > L.Z_BELT - 0.20:
        problems.append("back canopy runs into the gable's belt")
    problems += K.flue_problems(CHIMNEY, Z_RIDGE)
    # downpipes clear of the corners and the openings, and behind the terrace
    for (w, _s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        avoid = [(k,) + K.item_rects(k, c, z)[0][:2] for k, c, z in WALLS[w].items]
        problems += DP.problems(pipe, "the %s downpipe" % w, avoid)
        if pipe.point(0.0, 0.0, 0.0).y - DP.A < -HY + EPS:
            problems.append("the %s downpipe stands in the terrace" % w)
    # the roof kit: the wall ladder clear of the west wall's corners,
    # openings and downpipe; the walkway beside the stack, clear of it and of
    # the ridge
    wall = ROOF_KIT[0]
    avoid = [(k,) + K.item_rects(k, c, z)[0][:2] for k, c, z in WEST.items]
    avoid += [("downpipe", p.s - DP.A, p.s + DP.A)
              for (w, _s), p in zip(DOWNPIPE_SPOTS, DOWNPIPES) if w == "west"]
    problems += RS.problems(wall, "the wall ladder", avoid)
    problems += HR.problems(HANDRAILS[0], "the terrace handrail", L.OPENINGS["door_front"][0])
    problems += HR.problems(HANDRAILS[1], "the back handrail", L.OPENINGS["door_back"][0])
    if abs(TERRACE_RAIL_Z - (TERRACE_Z + HR.HEIGHT)) > 1e-6:
        problems.append("the terrace handrail does not meet the railing's top")
    walk = ROOF_KIT[2]
    if walk.s0 > HY - CHIMNEY[3] or walk.s1 < HY - CHIMNEY[2]:
        problems.append("the walkway does not run the stack's length")
    x_hi = -HX - walk.out_hi                         # its upslope edge, in x
    if not CHIMNEY[0] - 0.30 < x_hi < CHIMNEY[0] - 0.02:
        problems.append("the walkway's edge is not just beside the stack")
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
# Storeys: the ground floor on the plinth and the attic, whose floor is the
# balcony doors' threshold, 5 cm over the balcony deck.
Z_ATTIC = BAL_DOOR_SILL


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the house's four walls: the terrace
    is an open deck in front of them and the balcony a slab off the gable, so
    neither is wall outline or storey area. The attic counts where the roof's
    underside is 1.6 m or more over its floor."""
    attic_w = model_facts.roof_clear_width(2 * HX, Z_ATTIC, L.Z_EAVE, TAN)
    return {
        "hero": False,
        "dwellings": 1,
        "footprint": [(-HX, HY), (-HX, -HY), (HX, -HY), (HX, HY)],
        "storeys": [(L.Z_FLOOR, 2 * HX * 2 * HY), (Z_ATTIC, attic_w * 2 * HY)],
        "doors": [K.door(WALLS, "front", "entrance", "front", "door_front", main=True),
                  K.door(WALLS, "back", "service", "rear", "door_back"),
                  K.door(WALLS, "balcony", "balcony", "front", "door_balcony")],
    }


render_views = K.render_views

if __name__ == "__main__":
    BUILD.main(build_all, facts)
