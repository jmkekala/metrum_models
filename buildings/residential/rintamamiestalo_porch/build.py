# SPDX-License-Identifier: GPL-3.0-or-later

"""Deterministic rebuild of rintamamiestalo_porch, all four LOD tiers.

Run inside Blender:

    import runpy; ns = runpy.run_path(".../build.py"); ns["build_all"]()

or headless, which builds, exports, and renders preview.png and variants.png:

    blender --background source.blend --python build.py

Regenerate the textures first (python3 facade_atlas.py export): the UVs index
into the atlas, and the renders read it.

A composite Finnish rintamamiestalo — the 1940s-50s one-and-a-half-storey
veterans' house: a 10 x 8 m block under a 45 degree gable roof, horizontal lap
siding over a concrete plinth with cellar lights, plain-glass windows, a
brick chimney on the ridge, and an enclosed entrance porch whose own gable
runs into the main eave.

Construction is a set of closed solids unioned with Blender's exact boolean:
the main body, the porch body, one roof slab per roof, the chimney, the
back-door canopy and the two flights of steps. Each solid is simple to build
on its own; the union is what cuts the porch roof's valleys, trims the walls
where the soffits meet them and removes everything that ends up inside, so the
result is the boundary of one empty volume and interior geometry cannot occur.

The walls are textured as a trim sheet (see facade_atlas.py): siding tiles,
and each window or door is a hole in the wall with its own faces mapped to the
region that carries its casing and glazing. What the four rintamamiestalo
houses share (the walls and openings, roofs, chimney, canopy, steps, the tier
policy and the common checks) is scripts/rintamamiestalo.py's; this file keeps
the house: its massing, its walls, the places of its downpipes, roof kit and
handrails, its own checks and its facts.
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
from rintamamiestalo import (  # noqa: E402
    ATTIC_SILL, EAVE_OV, GF, RAKE_OV, ROOF_T, STEP_PROFILE, TAN, Peak, Steps, Wall)

L = facade_atlas.LAYOUT
K = R.Kit(L, HERE)
BUILD = K.asset

# ------------------------------------------------------------------ massing
# Front faces -Y. Main block 10.0 x 8.0 m, ridge along X.
HX, HY = 5.0, 4.0
Z_APEX = L.Z_WALL_TOP + HY * TAN                 # body apex, inside the slab
Z_RIDGE = L.Z_EAVE + ROOF_T + HY * TAN           # top of the ridge

# Entrance porch: an enclosed kuisti on the front, off centre, its gable facing
# the street. It is a separate solid reaching 0.2 m into the main body; the
# union removes the overlap.
PX0, PX1 = -2.70, 0.30
PXC, PHW = (PX0 + PX1) / 2.0, (PX1 - PX0) / 2.0
PY_FRONT, PY_BACK = -6.20, -HY + 0.20
PZ_EAVE = 2.75
PZ_TOP = PZ_EAVE + (L.Z_WALL_TOP - L.Z_EAVE)
PORCH_OV = 0.30                  # both eave and rake: a smaller roof, a smaller overhang
PORCH_SLAB_BACK = -3.40          # well inside the main block, so its end is buried
PORCH_APEX = PZ_TOP + PHW * TAN

CHIMNEY = (0.30, 0.90, -0.42, 0.42, 7.60, Z_RIDGE + 0.95)

FRONT_STEPS = (PXC - 0.70, PXC + 0.70)           # along x, off the porch front
BACK_STEPS = (0.80, 2.20)                         # along x, off the rear wall
CANOPY_X = (0.75, 2.25)                           # the back-door canopy
STEPS = [Steps("tmp_steps_f", *FRONT_STEPS, PY_FRONT, -1.0),
         Steps("tmp_steps_r", *BACK_STEPS, HY, 1.0)]

# --------------------------------------------------------------- elevations
# Gable ends carry one window per storey: the wide living-room window below,
# centred under the wide attic window above. Two smaller windows side by side
# read as busier than the type is, and one large one is the catalog's rule for
# short walls (CLAUDE.md, Style Direction). The porch splits the front wall
# into two such runs, and each carries one window centred between the porch
# and its corner: a standard one west, the wide living-room window east, with
# the cellar light under it. The gables are rintamamiestalo.Peak tops.
E, G = L.EAVE_BANDS, L.GABLE_BANDS
MAIN_WALLS = [
    # front (-Y), s = x + 5; the porch covers s 2.3 .. 5.3
    Wall("front", (-HX, -HY), (HX, -HY), L.Z_WALL_TOP, [
        ("std", 1.15, GF), ("wide", 7.65, GF), ("cellar", 7.65, 0.25)], (True, True), E),
    # +X gable end, s = y + 4
    Wall("east", (HX, -HY), (HX, HY), Peak(L.Z_WALL_TOP, Z_APEX), [
        ("wide", 4.00, GF), ("wide", 4.00, ATTIC_SILL),
        ("vent", 4.00, 7.35), ("cellar", 6.10, 0.25)], (True, True), G, L.Z_EAVE),
    # rear (+Y), s = 5 - x
    Wall("rear", (HX, HY), (-HX, HY), L.Z_WALL_TOP, [
        ("std", 1.50, GF), ("door_back", 3.50, L.Z_FLOOR), ("bath", 5.30, 2.20),
        ("std", 8.40, GF), ("cellar", 1.50, 0.25)], (True, True), E),
    # -X gable end, s = 4 - y
    Wall("west", (-HX, HY), (-HX, -HY), Peak(L.Z_WALL_TOP, Z_APEX), [
        ("wide", 4.00, GF), ("wide", 4.00, ATTIC_SILL),
        ("vent", 4.00, 7.35), ("cellar", 2.00, 0.25)], (True, True), G, L.Z_EAVE),
]
PORCH_WALLS = [
    Wall("porch_left", (PX0, PY_BACK), (PX0, PY_FRONT), PZ_TOP, [("porch", 1.30, 1.55)],
         (False, True), E),
    Wall("porch_front", (PX0, PY_FRONT), (PX1, PY_FRONT), Peak(PZ_TOP, PORCH_APEX),
         [("door_front", 1.50, L.Z_FLOOR)], (True, True), E),
    Wall("porch_right", (PX1, PY_FRONT), (PX1, PY_BACK), PZ_TOP, [("porch", 1.10, 1.55)],
         (True, False), E),
    Wall("porch_back", (PX1, PY_BACK), (PX0, PY_BACK), Peak(PZ_TOP, PORCH_APEX), [],
         (False, False), E),
]
WALLS = {w.name: w for w in MAIN_WALLS + PORCH_WALLS}
MAIN_EDGE = [0.0, L.Z_EAVE, L.Z_WALL_TOP, L.Z_FLASH]
PORCH_EDGE = [0.0, PZ_TOP, L.Z_FLASH]
# Offsets into the tiling siding band, so butt joints differ wall to wall.
U_OFF = {"front": 0.0, "east": 3.3, "rear": 6.1, "west": 9.4,
         "porch_left": 2.2, "porch_right": 5.7, "porch_front": 0.0, "porch_back": 0.0}

# Downpipes (scripts/downpipes.py): one from each eave's gutter, at
# diagonally opposite corners, so each gable end shows one. The front's is at
# its east end, since a window crowds the west corner.
DOWNPIPE_SPOTS = [("front", 2 * HX - DP.CORNER), ("rear", 2 * HX - DP.CORNER)]
DOWNPIPES = [DP.eave_pipe(WALLS[w].p0, WALLS[w].p1, s, L.Z_EAVE, TAN, EAVE_OV)
             for w, s in DOWNPIPE_SPOTS]

# Roof safety kit (scripts/roof_safety.py), the sweep's way to the chimney,
# at the back, away from the entrance, as such kits usually are: a wall
# ladder up the rear wall between the bathroom and the west window, the roof ladder
# straight above it up the rear slope, and a level walkway along the slope
# 0.5 m below the ridge, east to stand behind the stack.
KIT_S = 6.70                                      # rear wall, s = 5 - x
EAVE_REAR = RS.Eave(WALLS["rear"].p0, WALLS["rear"].p1, L.Z_EAVE, EAVE_OV,
                    L.Z_EAVE + ROOF_T - EAVE_OV * TAN, TAN)
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


# ================================================================ assembly
def build_lod(level):
    base = to_object(K.body(level, MAIN_WALLS, MAIN_EDGE, U_OFF,
                            ridges=[[(HX, 0.0, Z_APEX), (-HX, 0.0, Z_APEX)]]), "tmp_body")
    parts = [
        to_object(K.body(level, PORCH_WALLS, PORCH_EDGE, U_OFF,
                         ridges=[[(PXC, PY_FRONT, PORCH_APEX), (PXC, PY_BACK, PORCH_APEX)]]),
                  "tmp_porch"),
        to_object(K.gable_slab("x", 0.0, HY, L.Z_EAVE, EAVE_OV,
                               -HX - RAKE_OV, HX + RAKE_OV), "tmp_roof"),
        to_object(K.gable_slab("y", PXC, PHW, PZ_EAVE, PORCH_OV,
                               PY_FRONT - PORCH_OV, PORCH_SLAB_BACK), "tmp_porch_roof"),
        to_object(K.chimney(CHIMNEY), "tmp_chimney"),
    ]
    return K.tier(level, base, parts, STEPS, (CANOPY_X, HY), DOWNPIPES, ROOF_KIT, HANDRAILS)


def check_layout():
    """Assert the constraints that are invisible in the numbers and obvious
    once rendered: the family's (openings colliding, clipping the rake or a
    corner board, or straddling the band change; the gable outgrowing its
    atlas band; the canopy, the flue, the walkway) and this house's: the
    porch roof missing the main roof it is meant to run into, the downpipes
    and the wall ladder crowding each other or the back door."""
    problems = K.apex_problems(Z_APEX) + K.slope_problems(HY)
    problems += K.opening_problems(MAIN_WALLS + PORCH_WALLS)
    rear = WALLS["rear"]
    door = next(K.item_rects(k, x, z)[0] for k, x, z in rear.items if k == "door_back")
    problems += K.canopy_problems(rear, door, CANOPY_X)
    cx = sorted(HX - v for v in door[:2])            # rear wall: s = 5 - x
    porch_ridge = PZ_EAVE + ROOF_T + PHW * TAN
    if not (Z_RIDGE - HY - EAVE_OV < porch_ridge < Z_RIDGE - HY + 0.5):
        problems.append("porch ridge %.2f does not run into the main eave" % porch_ridge)
    problems += K.flue_problems(CHIMNEY, Z_RIDGE)
    # downpipes clear of the corners, the openings, the back steps and canopy
    back = [("back steps", HX - BACK_STEPS[1], HX - BACK_STEPS[0]),
            ("back canopy", HX - CANOPY_X[1], HX - CANOPY_X[0])]
    wall = ROOF_KIT[0]
    for (w, _s), pipe in zip(DOWNPIPE_SPOTS, DOWNPIPES):
        avoid = [(k,) + K.item_rects(k, c, z)[0][:2] for k, c, z in WALLS[w].items]
        kit = [("wall ladder",) + wall.span()] if w == "rear" else []
        problems += DP.problems(pipe, "the %s downpipe" % w,
                                avoid + (back if w == "rear" else []) + kit)
    # the roof kit: the wall ladder clear of the rear's corners, openings,
    # back steps, canopy and downpipe; the walkway behind the stack, clear of
    # it and of the ridge
    avoid = [(k,) + K.item_rects(k, c, z)[0][:2] for k, c, z in rear.items]
    avoid += back
    avoid += [("downpipe", p.s - DP.A, p.s + DP.A)
              for (w, _s), p in zip(DOWNPIPE_SPOTS, DOWNPIPES) if w == "rear"]
    problems += RS.problems(wall, "the wall ladder", avoid)
    problems += HR.problems(HANDRAILS[0], "the front handrail", L.OPENINGS["door_front"][0])
    problems += HR.problems(HANDRAILS[1], "the back handrail",
                            L.OPENINGS["door_back"][0], (cx[0] + cx[1]) / 2.0)
    problems += K.rear_walkway_problems(ROOF_KIT[2], CHIMNEY, HX, HY)
    return problems


def build_all():
    """Build every tier; the tier bookkeeping is asset_build's."""
    return BUILD.build_all(check_layout, build_lod)


# =================================================================== facts
# Storeys: the ground floor on the plinth and the attic 3.10 m above it.
Z_ATTIC = L.Z_FLOOR + 3.10


def facts():
    """The geometry facts sidecar's per-asset half (scripts/model_facts.py),
    in the build frame. The footprint is the main block with the enclosed
    porch, whose walls stand on the ground like the block's own. The attic
    counts where the roof's underside is 1.6 m or more over its floor."""
    attic_w = model_facts.roof_clear_width(2 * HY, Z_ATTIC, L.Z_EAVE, TAN)
    return {
        "hero": False,
        "dwellings": 1,
        "footprint": [(-HX, HY), (-HX, -HY), (PX0, -HY), (PX0, PY_FRONT),
                      (PX1, PY_FRONT), (PX1, -HY), (HX, -HY), (HX, HY)],
        "storeys": [
            (L.Z_FLOOR, 2 * HX * 2 * HY + (PX1 - PX0) * (-HY - PY_FRONT)),
            (Z_ATTIC, 2 * HX * attic_w),
        ],
        "doors": [K.door(WALLS, "front", "entrance", "porch_front", "door_front", main=True),
                  K.door(WALLS, "back", "service", "rear", "door_back")],
    }


render_views = K.render_views

if __name__ == "__main__":
    BUILD.main(build_all, facts)
