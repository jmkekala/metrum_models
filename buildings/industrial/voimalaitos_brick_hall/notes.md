# voimalaitos_brick_hall

## Style brief

The boiler and turbine hall of a small Nordic town's coal-fired heat and power
plant (*voimalaitos*), as built in the 1950s and 60s. It is one block of two
volumes in continuous red facing brick on a concrete plinth, under flat roofs
behind a low parapet with a light concrete coping. Light concrete appears only
in the plinth, the window band's sill, spandrels and head, the reveals and the
coping. It is a generic composite of the type, not any one plant.

- **Boiler house**, the west volume (Blender -X): 14 × 17 m and 19.5 m to its
  coping.
  - Its front carries the type's tell: one central band of five narrow steel
    lights on brick piers, 6.9 m wide and 3.5–16.9 m up, in three tiers on
    light concrete spandrels. The outer bays are blank brick with a column of
    small square gallery windows.
  - The main entrance, under a concrete canopy, stands at the foot of the
    band.
  - A **raised coal bunker bay** runs along the rear half of its roof, 13.8 ×
    6.5 m and up to 24.0 m. It is brick with a row of small square windows
    and a coping.
  - Two **steel stub stacks** stand on the deck in front of the bay: welded
    plate in weathered aluminium paint, sooted toward the mouth, with a
    rolled cap ring, two stiffening rings, a guy collar and a caged ladder
    up one side.
- **Turbine hall**, the east volume (+X): 18 × 16 m and 11.6 m, abutting the
  boiler house's east face.
  - Its front has four tall steel hall windows on equal brick piers, and the
    machinery door with a fifth window above it.
  - The generic word **VOIMALAITOS** is painted in plain individual capitals,
    1.0 m tall, in the brick band under the coping.
- Every other elevation has small square punched windows on the gallery
  levels.

The plant is five separate pieces on one lot (this hall, the chimney stack,
the coal reception, the office and control building and the transformer
yard). The **coal gallery's head** leaves this hall's west wall as a closed
stub, and the coal reception's gallery is designed to meet it. Nothing else
joins the pieces: no ground, base, pipe bridge or cable reaches out of this
asset. The sides facing the other pieces are designed for them (Construction,
*Sides facing the other pieces*).

Wall ladders with safety cages climb from the ground to the hall's roof and
from there to the boiler house's. The roofs drain internally, so there are no
gutters or downpipes.

## Category and secondary use

`buildings/industrial/`. No secondary use. It is one of five pieces of one
power plant, each its own asset.

## Hero/landmark status

**No.** Ordinary budgets and a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Walls: boiler house | 14.00 × 17.00 m |
| Walls: turbine hall | 18.00 × 16.00 m |
| Walls, the whole block | 32.00 × 17.00 m (the boiler house stands 0.5 m proud of the hall front and rear) |
| With the copings (0.05 m) | 32.10 × 17.10 m |
| Overall plan bounds, with the gallery head (5.0 m west), the entrance canopy (1.25 m) and the flue stub (1.0 m) | 37.05 × 19.25 m |

Heights:

| | Boiler house | Turbine hall |
| --- | --- | --- |
| Plinth top | 0.625 m | 0.625 m |
| Coping foot | 19.125 m | 11.25 m |
| Deck | 18.625 m | 10.75 m |
| Coping top | 19.50 m | 11.625 m |
| On the roof | bunker bay to 24.00 m, stub stacks to 24.75 m | ventilators to 11.95 m |

The stacks' tops set the height of the bounds on every tier.

The pivot is at ground level, centred on the plan's bounding box. The box
runs from the gallery head's far end (build x -21.0) to the turbine hall's
east coping (16.05), and from the canopy's front edge (y -9.75) to the flue
stub's end (9.5). That puts the pivot at build (-2.475, -0.125, 0). It is
taken from `LOD0` and applied to every tier. Every tier keeps the copings,
canopy, flue stub, gallery, bunker bay and stacks, so the extents never
change.

**In the glTF frame** (+Y up, +Z front, origin at the pivot):

- **Bounds:** [-18.525, 0, -9.625] to [18.525, 24.75, 9.625].
- **The gallery head** adds the plan rectangle x -18.525 to -13.525, z -5.925
  to -3.325, from 14.41 m up.

Standing outside the footprint polygon but inside the bounds:

- the copings (0.05 m all round, from 11.25 or 19.125 m up);
- the entrance canopy (1.25 m, at 3.25–3.5 m);
- the flue stub (1.0 m, at 12.75–14.75 m);
- the coal gallery head (5.0 m west, its underside 16.225 m at the wall and
  14.405 m at its end);
- the lower wall ladder and its cage, up to 0.9 m off the turbine hall's
  rear wall, from the ground.

Nothing stands on the ground outside the footprint: no steps, ramps, bases,
props or pipes. The ground under the gallery head is a declared lane in the
facts sidecar (Export).

## Story height

**One working storey at the ground in each volume.**

- The boiler house rises 18.6 m from its floor to its deck, the turbine hall
  10.75 m. Both are authored departures from the 3.0–3.3 m standard, and
  both are the type's. A boiler house is one tall volume round the boiler,
  its galleries open steelwork inside; a turbine hall is one volume under its
  overhead crane. The boiler house's small windows mark gallery levels every
  3.75 m, but none is a built floor.
- The bunker bay stands on the boiler house's roof, 18.625 m, under a roof
  5.4 m above it. It holds coal, not people, so it is no storey.

The facts sidecar lists one storey: the ground, 526 m² inside the outer
wall faces (238 m² + 288 m²).

## Door leaf height

- **Main entrance (boiler house front, at the band's foot): a pair of framed
  steel leaves, 1.81 × 2.30 m clear.** Each leaf has a tall light. A 0.09 m
  steel transom at 2.30–2.39 m separates them from a four-light fanlight that
  runs to the 3.0 m head. The opening is 2.0 × 3.0 m, under a concrete canopy
  at 3.25 m.
- **Machinery door (turbine hall front, east bay): four folding steel
  leaves, 3.31 × 3.91 m clear** in a 3.5 × 4.0 m opening. It is a vehicle
  door, sized for plant, not a leaf at human scale. A wicket door, 0.8 ×
  2.05 m, is painted into the second leaf. A row of small lights near the
  head is glazing, lit at night.
- **Service door (turbine hall rear, west bay): one steel leaf, 1.00 × 2.10
  m clear**, under a louvred vent panel to 2.28 m, in a 1.19 × 2.375 m
  opening.

All thresholds are at ground level, onto the hall floors, so there are no
steps and no handrails.

## Window sills

There are two steel window designs:

- **The hall window**: a 0.0625 m frame and panes 0.5 × 0.75 m on 0.047 m
  bars, every third pane row a hopper.
- **The small square window**: 0.8125 m, four panes on a cross.

Fifty-six windows are cut into the walls:

| Where | Count | Size (w × h) | Sill | Head |
| --- | --- | --- | --- | --- |
| Boiler house front, the band's lights (3 tiers × 5) | 15 | 1.125 × 3.875 m | 3.75 / 8.25 / 12.75 m | 7.625 / 12.125 / 16.625 m |
| Boiler house front, outer bays | 8 | 0.8125 m square | 4.0 / 7.75 / 11.5 / 15.25 m | +0.8125 m |
| Turbine hall front, hall windows | 4 | 1.625 × 6.875 m | 2.50 m | 9.375 m |
| Turbine hall front, over the machinery door | 1 | 1.625 × 4.625 m | 4.75 m | 9.375 m |
| Turbine hall rear | 7 | 0.8125 m square | 2.0 (3) / 7.75 (4) m | +0.8125 m |
| Turbine hall east | 2 | 0.8125 m square | 7.75 m | 8.5625 m |
| Boiler house rear | 10 | 0.8125 m square | 4.0 to 15.25 m, every 3.75 m | +0.8125 m |
| Boiler house west | 7 | 0.8125 m square | 4.0 to 15.25 m (three under the gallery) | +0.8125 m |
| Boiler house east, over the hall roof | 2 | 0.8125 m square | 15.25 m | 16.0625 m |

The bunker bay carries 20 more square windows (seven on each long face,
three on each end), sills at 21.22 m and heads at 22.03 m. They are cut
with 0.20 m reveals on `LOD0`/`LOD1` and painted flush from `LOD2`
(Construction, *The bunker bay*).

The band sits on a 0.25 m concrete sill at 3.5–3.75 m, directly over the
entrance canopy. Its spandrels are 0.625 m, and its head is 0.25 m. The only
ground-level sills are the turbine hall's 2.5 m and the rear's 2.0 m. Both
sit above the 1.4 m chest line, and the 2.3 m entrance leaf sets the scale
below them. Every higher window lights a single tall volume, not an occupied
floor, which is the type.

## Eave overhang

**None: flat roofs behind a parapet.**

- The brick walls run up 0.875 m past each deck to a precast concrete
  coping 0.375 m tall. It oversails the brick by 0.05 m outside and the
  parapet's inner face by 0.05 m inside. That is a parapet roof's flush
  edge, not an eave.
- The turbine hall's parapet is open on its west side, where its deck runs
  to the boiler house's face.
- The bunker bay's top edge is a 0.375 m coping band on its own brick,
  flush.

## Construction

`build.py` builds up to eleven closed solids and unions them with
Blender's exact boolean (`asset_build.union`):

- **The shell**: both volumes' walls as one closed solid, meshed directly.
  - On `LOD0`/`LOD1` it also carries both roofs' parapets (their tops, their
    brick inner faces and the sunk decks), so it closes with its floor alone.
  - On `LOD2`/`LOD3` flat lids at the wall tops close it, under coping boxes.
- **The copings**: a ring over each parapet (on `LOD2`/`LOD3`, a box over
  the whole roof, its top the deck). The boiler house's west face is cut
  4 m either side of the gallery's axis, and that middle stretch samples the
  dusted coping (`COPE_DUST`).
- **The coal bunker bay**, **the gallery head** and the two **stub stacks**.
- The two hall **ventilators** (`asset_build.open_stack`, `LOD0`/`LOD1`
  only), the **flue stub** and the **entrance canopy**.

The walls run 0.125 m up into the copings, and every roof item's foot is
buried in its deck. The union trims what is inside, so the result is the
boundary of one empty volume. After the union every tier is welded at 0.1 mm.
`LOD2`/`LOD3` are then dissolved with `dissolve_limit` (UV and material seams
kept). N-gons are triangulated by ear clipping with the beauty rule.

The two **wall ladders** with **safety cages** are `scripts/roof_safety.py`'s
lean kit: separate closed solids that touch nothing, appended after the
cleanup with `RS.append(..., check=True)` on `LOD0`–`LOD2`, never through the
union (Roof safety).

### The shell

The plan is an eight-sided outline: the boiler house's 14 × 17 m and the
turbine hall's 18 × 16 m, the boiler house's corners standing 0.5 m proud of
the hall's front and rear. Above the hall's roof the boiler house's east face
is its own wall (`step`). On the tiers with sunk decks it runs down to the
hall's deck between the hall's parapets, a T-shaped face.

Each wall is a rectangle less its openings and flush panels. There is no
frame: the walls are continuous brick, the piers between windows flush. Flush
panels are of three kinds:

- the window band's concrete sill, spandrels and head;
- the lettering and the brick under the gallery (Texture set);
- the cable bushing panel.

The remaining brick is a grid of cells cut at every opening, panel and slab
line. `trace_cells()` traces each slab's cells back into outlines with holes,
so a wall costs a polygon per brick slab, not a quad per cell. Then
`tjunctions()` gives every face every vertex lying on one of its edges. Every
shell face is axis-aligned, so this is an indexed lookup. Faces are
triangulated in their planes (`tessellate_polygon`, with `_flip_slivers()`
repairing collinear slivers), and the rim loops are capped.

### Openings

At `LOD0`/`LOD1` each opening is cut into the wall, with concrete reveals
(sill, head and jambs from the concrete band, V across the depth) and the
closing plane set back:

| Opening | Set back |
| --- | --- |
| Hall windows, entrance, service door | 0.25 m |
| Small square windows | 0.20 m |
| Machinery door | 0.30 m |

Doors have no threshold cheek; the floor cap covers the recess. At `LOD2`
each opening is the same rectangle, flush. At `LOD3` it is painted on the
wall's elevation.

A hall window's closing plane is made of the window region's sections
(`facade_atlas.window_sections()`). In height these are the bottom row, the
middle rows (plain, with a hopper row every third) and the top row; in width,
the outer columns and the middle ones. Consecutive sections that are
consecutive in the region are one quad.

### The bunker bay

The bay is one closed box on every tier, because it is silhouette. Its faces
stand 0.1 m behind the walls under it on the west, rear and east, so the
boiler house's coping reads as a string course under it. Its front stands on
the deck at y 1.9.

Each face is four horizontal bands:

| Band | Height | Texture |
| --- | --- | --- |
| Brick | to 21.0 m | brick band |
| Window row | 21.0–22.25 m | the atlas's BUNKER band |
| Brick | 22.25–23.625 m | brick band |
| Coping | 23.625–24.0 m | coping band |

The window row is brick with a square window every 2.0 m, one centred on
each face: seven on each long face, three on each end
(`bunker_windows()`). The band paints each window with a concrete sill
under it and the recess's occlusion round it.

- On `LOD0`/`LOD1` each window is cut into the row's face (a polygon with
  20 holes in all), with 0.20 m concrete reveals and the small square
  window's region on its closing plane, as on the walls. The painted sill
  under each hole stays, as a sill. The 20 windows cost 320 triangles.
- From `LOD2` the band's painted windows stand flush, as the walls' do.

Its top is a felt roof with a drain and a hatch, its edge the coping's
top.

### The gallery head

The coal conveyor's gallery leaves the west wall as an enclosed stub,
**sloping down away from the wall at exactly 20°**:

- **Section:** 2.6 m wide (along y) and 2.8 m tall, measured vertically.
- **Centre line:** leaves the wall face (x -16.0) at y 4.5 and 17.625 m.
- **Length:** 5.0 m on the plan, so its closed end's centre is at x -21.0,
  15.805 m.
- **Underside:** 16.225 m at the wall and 14.405 m at the end.

The mouth is 0.375 m lower than the brief's 18.0 m. At 18.0 m the gallery's
top, 19.4 m, would cut through the coping (19.125–19.5 m). At 17.625 m its
top meets the wall 0.1 m under the coping's foot and passes under the bunker
bay, which it feeds.

Its back runs 0.2 m into the parapet's brick (inside the parapet's inner
face, so nothing shows on the deck). Its sides, top and end are light
corrugated sheet with coal dust. The end is a closed blank face, a dark
panel set in a sheet frame, painted. It cantilevers: there is no trestle,
prop or strut under it, so the ground beneath stays clear. It is kept on
every tier.

### The stub stacks

Two steel stacks stand on the boiler house's deck in front of the bay, at
(-12.5, 0) and (-10.0, 0). Each is an octagon 1.56 m across its corners and
1.44 m across its flats, rising 6.1 m from the deck to 24.75 m. Both are
hollow (CLAUDE.md): a 0.08 m rim round a flue sunk 1.0 m, sooted, its floor
at 23.75 m, well clear of the deck. They are made locally rather than with
`asset_build.open_stack()`, which builds square stacks; a round steel stack
reads as one only with facets. They are kept on every tier.

Each is built as one closed solid from a profile (`stub_stack()`), so its
rings cost no boolean:

| Ring | Height | Proud | Modelled on |
| --- | --- | --- | --- |
| Rolled cap ring | 24.60–24.75 m | 0.035 m | `LOD0`, `LOD1` |
| Stiffening rings | 20.875–20.955 and 22.875–22.955 m | 0.03 m | `LOD0` |

Every ring is also painted, with its shadow line, on every tier, so a tier
that drops its geometry keeps it in the texture (`stack_rings()`). The cap
ring shapes the mouth's outline, so it stays to 70 m; at 35 m the
stiffening rings are about a pixel proud.

The rest is texture: welded seams every 1.5 m, the foot flange, a guy
collar at 23.625 m with a lug on seven faces, and on face 6 (facing the
front and the turbine hall) a caged ladder: rails, a rung every 0.3 m, and
hoops every 0.75 m from 2.6 m over the deck with three straps. That face
samples a region of its own (`STACK_L`), turned a quarter.

### Roof joins

- The turbine hall's deck runs to the boiler house's east face, which is
  one face with the hall's parapets' inner faces. Its coping runs 0.5 m into
  the boiler house at both ends.
- The bay's faces cross the boiler house's parapet and coping on three
  sides. Its foot and the stacks' feet are buried 0.2 m in the deck, and
  the ventilators' in the hall's.

### Sides facing the other pieces

In the build frame (Blender), with the front toward -Y:

| Side | Blender | glTF | What faces it | What is on the wall |
| --- | --- | --- | --- | --- |
| Rear of the boiler house | +Y | -Z | the chimney stack | the **flue stub**: a 2 × 2 m concrete casing projecting 1.0 m at 12.75–14.75 m in the middle, its end closed by a bolted steel blanking plate, sooted. In glTF its end face is centred at (-6.525, 13.75, -9.625). Nothing reaches beyond it. |
| West end of the boiler house | -X | -X | the coal reception | the **coal gallery head** (above). In glTF its mouth centre is (-13.525, 17.625, -4.625) and its end centre (-18.525, 15.8051, -4.625). It runs along -X, sloping down 20° (direction (-0.9397, -0.3420, 0)), in a 2.6 m (along Z) × 2.8 m (vertical) section. The brick under it carries coal dust. |
| East end of the turbine hall | +X | +X | the transformer yard | the **cable bushing panel**: flush and painted, 2.5 × 1.25 m at 6.25–7.5 m in the middle. It is a concrete panel in a steel frame with three porcelain bushings and cable glands. Otherwise blank brick between two small windows. |

The office and control building faces no designed side: the front (-Y,
glTF +Z) carries the entrance and the machinery door.

### Drainage

The roofs drain inward, to outlets painted on each deck. This is the
flat-roofed Nordic hall's usual detail, where an outside gutter would
freeze. The copings are flush, so there is no gutter, and a building without
a gutter has no downpipes (CLAUDE.md). The galvanised band `PIPE_STRIP` is
kept for the ladders.

### Roof safety

Both roofs are flat decks, so CLAUDE.md asks only for a wall ladder up to
each. The stacks stand on the boiler house's deck, the ventilators on the
hall's. The two ladders make one route: up the hall's rear wall, across the
hall's deck, and up the boiler house's east face. Nothing serviced stands on
the bunker bay's roof, so it has no ladder.

- **Lower wall ladder**: from the ground up the turbine hall's rear wall at
  x 11.25, 0.17 m out, past the coping to 1.0 m above it (12.625 m long).
- **Upper wall ladder**: from the hall's deck up the boiler house's east
  face at y 0, its foot hanging 0.3 m above the deck, to 1.0 m above the
  coping (9.45 m long).
  - It is in the face's middle, not its rear half. The bunker bay fills the
    rear half of that roof edge, so a ladder there would land against the
    bay's face.
  - It is out of sight from the street, over the hall roof.

Both run more than 8 m, so each carries a safety cage (`roof_safety.Cage`,
its defaults): hoops from 2.5 m over the foot to just under the top, 1.43 m
and 1.36 m apart (8 and 6 hoops), and three straps.

Both ladders use `roof_safety.WallLadder(..., lean=True)` on a level
`Eave` (the coping's foot, its 0.05 m oversail and its top), with their
cages `roof_safety.Cage` lean with them. They take brackets every 2.4 m at
most rather than the shared 1.6 m. `check_layout()` passes
`roof_safety.problems()` for both ladders and both cages.

The lean kit cuts nothing: rungs stop 1.5 mm short of the rails, brackets
as short of the wall and the rails, hoops of the rails and straps of the
hoops. It goes into each tier with one `RS.append(obj, RS.solids(kit(level),
level, PAINT, extents=True, modes=LADDER_MODES), check=True)` after the
cleanup; `check=True` raises if any part meets the building or another
part.

- The walls and the plinth are flush, and the copings oversail 0.05 m, 0.12 m
  inside the rails, so no bracket needs `behind`.
- The upper ladder's foot hangs 0.3 m over the hall's deck, clear of it.
- From `LOD2` the hall's roof is its coping box, whose top is 0.875 m above
  that deck. There the upper ladder's bare rails start 0.01 m over the box
  (`WALL2_FLAT`), and its back strap keeps the cage's hoop heights
  (`CAGE2_FLAT`). The parapet hides that stretch from the ground on every
  tier.

Tiers (`LADDER_MODES`, `CAGE_MODES`, and the lean forms of
`roof_safety.LEAN_FORMS`):

| Tier | Rungs | Brackets | Cage |
| --- | --- | --- | --- |
| `LOD0` | every one, three-sided | yes, three-sided | every hoop |
| `LOD1` | every other one, three-sided | yes, tetrahedra | every other hoop, the top one always |
| `LOD2` | bare rails | no | each cage's back strap |
| `LOD3` | no kit | no | none (no append) |

The ladders never set the bounds, so `LOD3` can drop them.

### Authored parameters

Every tier derives from `facade_atlas.py`:

- the plan, `BH` and `TH`;
- the heights: `Z_PLINTH` 0.625, `COPING` 0.375, `CO`/`CO_IN` 0.05, `PIN`
  0.25, `WALL_IN` 0.125, `DECK_DOWN` 0.875, `Z_BC` 19.5 and `Z_TC` 11.625;
- `CUTS` and `SLAB` for the brick;
- the window designs (`FR`, `CW`, `RH`, `MUL`, `SQ`);
- the window band (`LIGHT_X`, `TIERS`, `BAND_STRIPS`, `SQ_Z`) and the
  turbine hall's windows (`TH_WIN_X`, `TH_SILL`);
- `SIZES` and `REVEAL` for the other openings;
- `WALLS` and `ITEMS`;
- `CANOPY`, `FLUE`, `BUNKER` and `BUNKER_SILL`, `STACKS` and the stacks'
  rings (`STACK_CAP`, `STACK_STIFF`, `STACK_GUY`, `STACK_LADDER_FACE`),
  `VENTS`, the gallery (`GAL_*`) and the dusted coping (`COPE_DUST_HALF`).

`check_layout()` asserts:

- the openings' and panels' clearance from corners, each other, the coping
  and the slab lines, and the leaf heights;
- the ladders' and cages' places, and the upper ladder's landing clear of
  the bay;
- the gallery under the coping, its back inside the parapet, the west
  windows clear of it and the dusted panel round its foot;
- the bay within the parapets, and the stacks and ventilators clear of each
  other, the parapets and the ladders.

## Per-tier triangle counts

| Tier | Triangles | Ceiling |
| --- | --- | --- |
| `LOD0` | 4114 | 12,000 |
| `LOD1` | 3276 | 4,000 |
| `LOD2` | 1434 | 1,500 |
| `LOD3` | 316 | 500 |

Where they go, counted on the solids before the union (the kit is appended
whole, so its count is exact):

| | `LOD0` | `LOD1` | `LOD2` | `LOD3` |
| --- | --- | --- | --- | --- |
| Shell (walls, openings, parapets, decks) | 1598 | 1598 | 1094 | 32 |
| Copings | 68 | 68 | 32 | 32 |
| Bunker bay (its windows cut to `LOD1`) | 356 | 356 | 36 | 36 |
| Gallery head | 12 | 12 | 12 | 12 |
| Stub stacks (their rings, `stack_rings()`) | 440 | 184 | 120 | 120 |
| Ventilators | 56 | 56 | 0 | 0 |
| Flue stub and canopy | 24 | 24 | 24 | 24 |
| Roof safety kit | 1412 | 830 | 48 | 0 |

The **roof safety kit's share of the finished tier**:

| | `LOD0` | `LOD1` | `LOD2` | `LOD3` |
| --- | --- | --- | --- | --- |
| Kit | 1412 (34.3 %) | 830 (25.3 %) | 48 (3.3 %) | 0 |
| The rest | 2702 | 2446 | 1386 | 316 |

Two ladders of 12.6 m and 9.45 m make 22 m of rail and 76 rungs, and both
cages are required by length. As the lean kit it cuts nothing: a rung is a
three-sided prism of 8 triangles, the hoops and straps are three-sided, and
no rail or strap is split where another part meets it. Unioned, the same
kit was 3554 triangles at `LOD0` and 1368 at `LOD1` (every third rung and
hoop), 63.5 % and 40.1 % of those tiers. `LOD1` keeps every other rung and every other hoop, and its
brackets as tetrahedra.

The kit is still over the quarter of a tier CLAUDE.md suggests for trim at
`LOD0`, by 9 points, because the rungs are kept whole. `LOD0` has 7,900
triangles to spare, and thinning rungs that read at 20–35 m would show.

The 20 cut bunker windows (320 triangles to `LOD1`) and the stacks' rings
(320 at `LOD0`, 64 at `LOD1`) are what the lean kit's saving paid for.
`LOD1` keeps 724 (18 %) of its ceiling, `LOD2` 66.

## LOD review

Review camera: `scripts/review_asset.py`, perspective, 50° vertical FOV,
1920×1080, Cycles at 16 samples, distance along the view direction to the
centre of the facing wall.

| Switch | Intended distance | Renders |
| --- | --- | --- |
| `LOD0` → `LOD1` | ~35 m | 30 and 40 m, `LOD0` and `LOD1`, front, oblique and rear, noon |
| `LOD1` → `LOD2` | ~70 m | 65 and 75 m, `LOD1` and `LOD2`, front, oblique and rear, noon; 60 m oblique at night, emission on |
| `LOD2` → `LOD3` | ~120 m | 115 and 125 m, `LOD2` and `LOD3`, front, oblique and rear, noon; 120 m oblique at night, emission on |

No distance overrides.

- **35 m.** `LOD1` matches `LOD0`. The ladders lose every other rung and
  keep their brackets as tetrahedra; the cages keep every other hoop and
  all three straps. The stacks lose their stiffening rings' geometry; the
  painted rings and shadow lines stay. At 35 m a rung is about one pixel.
- **70 m** (re-checked at 65/75 m after the lean kit). Flattening the
  openings loses the 0.2–0.25 m reveal shadow, about 2 px, the bunker
  bay's windows included. The ventilators and the stacks' cap ring
  geometry go. The sunk decks become coping boxes, which read the same from
  the ground and nearly so from above. The ladders keep their rails and the
  cages' back straps as hair lines, as before the lean kit. The silhouette
  is unchanged: the bay, stacks, gallery, canopy, flue stub and coping line.
  So are the window band, the spandrels and the lettering.
- **120 m.** `LOD3` replaces the walls' geometry with the 6 px/m
  elevations. The plinth, the band and its spandrels, the windows, the doors
  and the lettering are painted on single faces. At 120 m a metre is about
  9.7 px, so the elevations are slightly soft. The bay, the stacks and the
  gallery keep their geometry and textures. The ladder rails go. The hall
  windows average within about 10 sRGB levels of what `LOD2` samples, the
  small square windows within -13 to +6 measured with their frames
  (Texture set, *The LOD3 elevations*); at 115/125 m they read alike.

The working renders are local and git-ignored:

- `review/power_plant_polish_2026_11_21/voimalaitos_brick_hall/`: `before/`
  and `after/` (six views, the rear and west at 30 m, the LOD pairs and
  night), sheets in `compare/`, and `views_pass*/` (the build's eye views
  and close views of the gallery, the stacks, the bay and the ladders);
- `review/power_plant_rev_2026_11_21/voimalaitos_brick_hall/`, the
  previous revision's sets, `mip3/`, `mip4/` and `daycycle/`.

These are authoring comparisons. Consumer switching, filtering and
performance are pending.

## Interior geometry

The validator's hidden-surface test reports:

| Tier | Hidden triangles |
| --- | --- |
| `LOD0` | 207 (5.0 %) |
| `LOD1` | 99 (3.0 %) |
| `LOD2` | 35 (2.4 %) |
| `LOD3` | 0 |

The candidates are exterior surfaces the rays cannot reach:

- the copings' 0.05 m inner drips over the decks, the largest of them;
- the ladder rails' backs, 0.17 m off the walls;
- the lean kit's small faces between the rails and the walls: the rungs'
  and brackets' undersides and the hoops' inner ridges, each a closed solid
  of its own 1.5 mm clear of its neighbours.

The shell's floor and lids, the parapet tops inside the copings, the roof
items' buried feet, the gallery's buried back, and the flue stub's and
canopy's backs are all removed by the union. There are no buried partitions
or duplicate surfaces. Recessed glass and doors are exterior surfaces.

## Known simplifications

- **Painted, not modelled:**
  - the glazing bars and hopper sashes;
  - the entrance's leaves, lights and fanlight;
  - the machinery door's leaves, ribs, lights and wicket door;
  - the service door's vent panel;
  - the flue's flange and bolts;
  - the bushings and cable glands;
  - the bunker bay's windows from `LOD2` (flush, Construction);
  - the stacks' welded seams, guy collar and lugs, and the ladder and cage
    on one face of each (and their stiffening rings on `LOD1`, every ring
    from `LOD2`);
  - the gallery's corrugations, its end panel and the end's slight recess;
  - the lettering;
  - the stacks' flanges.
- **Painted on the roofs:** the felt's laps and mineral grain, the parapet
  upstand, the drain outlets, the hatches, the skylight kerbs (opaque, dark)
  and the paving where people walk.
- **Not modelled:**
  - sills (a concrete reveal face, and the band's flush concrete sill);
  - a lintel over the machinery door (plain brick above it);
  - the plinth step (flush with the brick).
- No boiler, turbine, crane, conveyor beyond the gallery head, flue duct
  beyond the stub, pipe bridges, cables, ground slab or yard. Each piece of
  the plant is its own asset.
- The ventilators are capped by their sooted flues and the stacks are open
  round sooted flues, so no unmodelled interior shows.

## Texture set

One 1024² set at 64 px/m, supersampled at `atlas.SS` = 4, shared by every
tier:

- three albedos;
- `_orm.png`;
- `_normal.png`;
- `_emission.png`.

That is six unique 1024² PNGs.

### Layout

| Rows | Band | Content |
| --- | --- | --- |
| 0–336 | BRICK | z 0–5.25 m: the plinth (0–0.625 m) and stretcher-bond brick |
| 336–348 | | the bond carried on into the gutter |
| 352–432 | BUNKER | 1.25 m of brick with a square window every 2 m: the bunker bay's window row |
| 440–480 | CONC | 0.625 m of light precast concrete: the band's sill, spandrels and head (V up the panel), and the reveals (V the depth) |
| 488–512 | COPE | the 0.375 m concrete coping, its units a metre long, a drip groove at its foot |
| 518–530 | PIPE | galvanised steel; `PIPE_STRIP` is rows 520–528 |
| 536–1020 | unique | see below |

Every 4 m slab's top samples the brick band's last row. So the bond runs on
into the gutter above it, and the band above that is the bunker bay's, also
brick. A coarse mip there still averages brick. With the concrete band next
door, as first laid out, the slab lines showed as light hairlines at mip 3.

The unique regions:

- the hall window (2.125 × 3.125 m, four by four panes) and the small
  square window;
- the machinery door, the entrance and the service door;
- the flue's end and sides, and the bushing panel;
- the lettering and the brick under the gallery, both 64 px/m brick;
- the gallery's side, roof and end (24 px/m);
- two stack faces (32 px/m): the plain one, and the one with the ladder,
  turned a quarter (U up the stack) to fit a 20-row strip;
- the dusted stretch of the west coping, 4.0 × 0.375 m, painted as the
  coping band at the U its face samples it at, so its unit joints run on;
- the two roof decks (8 px/m);
- the five `LOD3` elevations (6 px/m);
- ten flat patches.

`check_regions()` asserts:

- that the regions neither overlap nor run off the sheet, and that each
  matches its face's size;
- the bands' periods, and that the brick regions keep the band's bond (a
  panel may cross a slab line, since a slab is 256 rows, eight bond
  repeats);
- that the lettering fits its panel, and the elevations and decks their
  walls and roofs.

`pad()` fills every unclaimed texel from the nearest region's edge.

### The brick band and the slab lines

The walls are far taller than the brick band, so above 5.25 m they are cut
at 5.25, 9.25, 13.25, 17.25 and 21.25 m into 4 m slabs (`CUTS`). Slab *i*
samples the band 4*i* m lower, its rows 1.25–5.25 m. The bond and tones
repeat every 48 courses (256 rows), and so does every noise field
(`TILE_Y` = 4), so the slab lines vanish. Rows above 1.25 m are clean brick:
the splash-back and salt bloom stay below. `check_layout()` keeps every
opening's edge 0.1 m off a slab line.

### Brick that continues the band

Three places carry brick that cannot come from the tiling band:

- **the lettering panel** under the turbine hall's coping, 10.5 × 1.25 m;
- **the panel under the gallery**, 3.75 × 3.875 m at 12.625–16.5 m, where
  coal dust falls from the gallery's floor. It crosses the 13.25 m slab
  line, which the bond does not see, and stops 0.31 m over the head of the
  small window under the gallery;
- **the bunker bay's window row**.

Each is painted by the band's own brick painter, so its bond runs on into
the band's across its edges:

- The two panels sit in the atlas at the U their wall samples the band at.
  `U_OFF` places the turbine hall front's and the west wall's brick for
  that, which breaks the bond only at two corners.
- All three sit on rows a whole number of bond repeats (32 rows, six
  courses) from the band rows their heights sample.

The brick tones and noise across those edges are random either way, so the
joins do not show. The coal dust fades to nothing at the panel's edges, and
the even film every brick surface carries (Weathering) is the same inside
and outside them.

### The lettering

**VOIMALAITOS** is a generic word, not any plant's or company's name. It is
painted in plain geometric sans-serif capitals, 1.0 m tall with 0.14 m
strokes, centred in the brick band under the turbine hall's coping. The
capitals are drawn from primitives in `facade_atlas.py`, so no font file is
needed. They are painted metal letters, 2 cm proud in the normal map,
with a soft occlusion halo, and they are not luminous. They are off-white
(212, 210, 202) on the red and the brown brick; on the yellow brick, where
light letters all but vanish, they are a dark green-grey (66, 74, 70), a
shade of that variant's window steel (`VARIANTS["yellow_brick"]["letter"]`).

### Texel density

Texel density is 64 px/m everywhere, with these exceptions:

- the roof decks, at 8 px/m: felt seen only from above;
- the gallery's sheeting, at 24 px/m: a light corrugated sheet seen 15 m up
  or more;
- the stacks, at 32 px/m: plate seen from below or far off, its ladder's
  rails 1.3 px and its rungs 0.8 px wide, supersampled;
- the cable bushing panel, at 48 px/m: a flush painted panel 6–7.5 m up on
  the end facing the transformer yard, moved off the 64 px/m sheet to make
  room for the larger dusted panel;
- the flue stub's sides, at 32 px/m: plain concrete with a soot gradient;
- the `LOD3` elevations, at 6 px/m: about 1:1.6 at the 120 m switch;
- the flat patches.

### The LOD3 elevations

Each wall's elevation is painted at 6 px/m by the same painters as the
full-size regions (`paint_elevation()`). The windows, panels, doors and
lettering therefore sit where the mesh has them. Two measures keep their
windows the average colour of the region `LOD2` samples:

- **Bars stay visible.** Glazing bars and frames are never thinner than one
  sample, or at 6 px/m they vanish.
- **The glass keeps `glazing.BASE`, box-filtered with its bars, instead of
  being repainted by `glazing.rooms()`** (`ELEV_BASE_GLASS`). This exception
  was re-checked after the windows were regrouped, against a bake without
  it:
  - Without it the elevations' windows average 54 sRGB levels darker than
    their `LOD2` regions, up to 88.
  - With it the hall windows are within about 10 levels (the band's lights
    -10, the turbine hall's -1 to -2).
  - The small square windows, measured again with the crop including their
    frames (an area-weighted mean in linear light over each window's exact
    rectangle in the elevation, against the whole 52 px region `LOD2`
    samples): the front's 8 average +6 sRGB levels, the rear's 17 -7 to
    -9, the west's 7 -6 to -8, the east's and the step's -6 to -13. The
    earlier -25 came from a crop that dropped their light frames, so they
    are left as they are.

### Relief

The normal map is derived from a painted height channel, in metres:

| Feature | Height |
| --- | --- |
| Brick faces over mortar | 0.006 |
| Concrete arrises (panels, reveals, coping) | 0.008 |
| Window frames | 0.035 |
| Mullions and bars | 0.030 |
| Hopper sash | 0.045 |
| Door frames and stiles | 0.030 |
| Sheet ribs (machinery door) | 0.006 |
| Gallery corrugations | 0.012 |
| Gallery roof seams | 0.020 |
| Letters | 0.020 |
| Stack flanges and rings | 0.012 |
| Stack ladder, hoops and straps | 0.025–0.035 |
| Guy lug | 0.025 |

Glass is flat.

### Filtering

Atlas mips at levels 3 and 4 were made with `scripts/review_atlas_mips.py`.
`LOD1`–`LOD3` were rendered at mip 3 and mip 4 (a 64² atlas), oblique and
aerial, at 20 m:

- `LOD1`/`LOD2`: the brick keeps its colour with no slab lines, the copings,
  spandrels and the band's sill and head stay light concrete, and the
  windows stay grey panels in light frames. The lettering blurs but keeps
  its place and contrast. The decks show no brick or concrete leak.
- `LOD3`: the 6 px/m elevations smear into brown blocks at mip 4, as
  expected far past the tier's use.

At 120 m a metre is about 9.7 px, so the elevations sample mip 0. At 500 m
they reach about mip 1.3, and only past about 1 km mip 3. Consumer filtering
beyond that is pending.

### Weathering

Weathering is `scripts/weathering.py` at its moderate level, its noise on
the 256-row period:

- grime, and paint fade on the steel, the sheeting, the letters and the
  stacks;
- rain wash on the brick;
- splash-back and salt bloom on the brick's first metre;
- soil and algae on the plinth;
- patchy dirt on the precast concrete;
- runs down the coping's face;
- dirt on the windows' bottom rails;
- kicked-up dirt and handle grime on the doors;
- dirt on the decks.

The plant burns coal, so `Weather.coal()` lays coal dust and soot:

- **an even film on every brick surface**: coal 0.10 ± 0.04 with faint long
  runs on the slab period, and dirt 0.04. It takes the newness off the
  brick without changing the plant's shared palette (Variant list). It is
  even, not heavier toward the coping, because every 4 m slab samples the
  same band rows; for the same reason darker runs under the copings and
  sills cannot live in the band and are not painted (the coping's own face
  carries its runs);
- a light film on the coping and the boiler house's deck;
- **a broad soft stain under the gallery** (`mouth_dust()`): as wide as the
  gallery, spreading a little as it falls, from about 0.95 at the
  gallery's floor at the wall to 0.5 at 1.5 m below and 0.3 at 3 m, then
  out over the panel's last metre, 3.6 m below the floor, and a little
  round the mouth beside it. It cannot run the 5–6 m a free wall would
  show: the small window under the gallery (11.5–12.3 m) is shared with
  every other, and a taller 64 px/m panel has no room on the sheet. The
  `LOD3` west elevation carries the same function;
- the gallery's underside heavily dusted, its sides' lower sheet heavily
  over its bottom metre and its roof throughout;
- the stretch of west coping over the gallery, darkest over its axis;
- soot on the flue stub's plate and casing;
- the stacks: soot from the mouth (about 0.9 at the rim, falling off over
  1 m) and in streaks to mid-height, rust running from under the
  stiffening rings and the guy collar, and soot on the rims; their lower
  plate keeps the lighter aluminium paint;
- soot rings round the stacks' feet on the deck.

Cavity dust settles in the mortar joints. Glass and porcelain stay clean.

## Glazing treatment

Glass is painted with `scripts/glazing.py`: `rooms()` on the finished albedo,
`glazing.BASE` (50, 54, 57). Each pane row of a hall window, and each light
of the band, is its own room, with its own falloff toward the foot.

The validator measures:

- the glass at sRGB 58–59 (linear 0.038–0.041) across the variants;
- 0.29× the brightest trim;
- roughness `glazing.ROUGHNESS` (0.08), metallic 0.

All of this is inside the Style Direction band, and the glass is darker than
its steel frames in every variant. There are no brief-driven departures. In
the `LOD3` elevations the glass is `glazing.BASE` box-filtered with its bars
(Texture set). The bunker bay's windows take `rooms()` like the rest: the
small square window's region where they are cut, the band's painted ones
from `LOD2`.

## Variant list

Large-scale, so a restrained, coherent treatment per instance: three uniform
brick alternatives on the shared mesh.

- The window steel and the doors move with the brick, and the window steel
  is always lighter than its glass.
- The concrete, coping, roofs, gallery, stacks and kit are the same in every
  variant, and so is the weathering, the even soot film on the brick
  included.

| Variant | Meaning |
| --- | --- |
| `red_brick` (default) | red facing brick, off-white window steel, dark green-grey doors |
| `yellow_brick` | yellow facing brick, grey-green window steel, oxide-red doors |
| `brown_brick` | dark purple-brown clinker brick, light grey window steel, blue-grey doors |

`red_brick` and `brown_brick` are the same constants, sRGB, on all five of
the plant's pieces, so any two of them match side by side:

| | `red_brick` | `brown_brick` |
| --- | --- | --- |
| Brick | (114, 73, 62) | (80, 59, 57) |
| Darker brick | (90, 59, 51) | (62, 46, 45) |
| Mortar | (125, 123, 118) | (108, 106, 102) |

- `red_brick` is the catalog red (144, 72, 52), (114, 58, 45), mortar
  (150, 145, 136), each channel taken to Y + 0.6 (*c* − Y) (Y its Rec.709
  luma), times 0.94; the mortar is 10 % darker again.
- `brown_brick` is a dark clinker, well below the red in value and in
  redness, so the three variants read apart at a glance.
- The mean plain-wall albedo (the albedo PNG's rows 720–900, the brick
  band clear of windows and plinth) measures sRGB (102.7, 76.7, 68.2) on
  `red_brick`, R − G 26.0, and (78.6, 65.2, 61.9) on `brown_brick`, R − G
  13.4. The soot film took the red from (110.5, 81.0, 71.9), R − G 29.5,
  with the palette constants unchanged.
- `yellow_brick` keeps its brick; only its lettering is dark (Texture set).

## Night lighting

- **Mask.** `voimalaitos_brick_hall_emission.png` is the neutral glazing
  mask:
  - every window's panes, the bunker bay's included (the square window's
    region where they are cut, the band's painted ones from `LOD2`);
  - the entrance's leaf lights and fanlight;
  - the machinery door's lights;
  - the same in the `LOD3` elevations.

  Each is lit as a room by `glazing.night_rooms()`. Everything else is black.
  There are no signs or lamps, and the lettering is not lit.
- **Bindings.** All four GLBs bind the mask through `emissiveTexture` on UV0,
  with `emissiveFactor` `[0, 0, 0]` by default and the texture kept
  (`scripts/window_emission.py`, via `asset_build.export_all()`).
- **Reference lit factor.** Linear RGB `[1.0, 0.88, 0.72]`: industrial hall
  lamps, the catalog's works value.
- **Control.** One building-wide control. The windows share regions, so
  individual windows cannot be switched. The consumer owns intensity, colour
  and schedule.
- **Preview.** `variants.png` shows all three colours at `LOD0`: a DAY row
  (emission off) above a NIGHT row (reference emission on). Camera, framing
  and exposure are fixed between rows (`scripts/variant_previews.py`, Cycles,
  AgX, exposure 0). Spill onto nearby surfaces is simulated by Cycles in that
  sheet only.
- **Day cycle.** The day cycle (morning, noon, dusk, and night with emission
  on) was rendered on the reimported `LOD0`.
- **Across tiers.** The lit pattern was compared on the reimported tiers at
  60 m and 120 m, oblique, at night with emission on (LOD review). It stays
  the same across `LOD0`, `LOD2` and `LOD3`. The `LOD3` windows read
  slightly more even, each one room.
- **Pending in the consumer:** material control, night exposure, spill and
  LOD switching at night.

## Export

```
python3 facade_atlas.py export                      # textures, all three variants
blender --background source.blend --python build.py  # meshes, preview, variants, sidecar
blender --background --python build.py -- facts      # the facts sidecar alone
```

Generate the textures first, because the UVs index into the atlas.
`facade_atlas.py` is the single source of every number the two scripts
share.

Export settings, as `asset_build.export_all()` passes them:

- `export_format='GLB'`
- `use_selection=True`
- `export_yup=True`
- `export_apply=True`
- `export_keep_originals=True`
- `export_cameras=False`
- `export_lights=False`

The material has backface culling on, so it exports single-sided.
`strip_embedded_images()` removes the placeholder `bufferView` beside each
image `uri`.

The material bindings, traced per tier, are one material on every tier:

- `baseColorTexture`: the `red_brick` albedo;
- `metallicRoughnessTexture` and `occlusionTexture`: the ORM;
- `normalTexture` at scale 1, through a tangent-space Normal Map node, with
  no tangents exported;
- `emissiveTexture`: the mask, with a zero factor.

All of them are on UV0 and reference external PNGs.

The facts sidecar `export/voimalaitos_brick_hall.model.json` records:

- the footprint, as the eight-sided wall outline at the ground;
- one storey: the ground, 526 m² (the coal bunker bay is not an occupied
  floor);
- zero dwellings;
- three doors:

  | Door | Kind | Main |
  | --- | --- | --- |
  | Entrance (`entrance`), boiler house front, 1.81 × 2.30 m | entrance | yes |
  | Machinery door (`machinery`), turbine hall front, 3.31 × 3.91 m | vehicle | no |
  | Service door (`service`), turbine hall rear, 1.00 × 2.10 m | service | no |

- one passage, `under_gallery`: the clear ground under the gallery head
  (`build.py`'s `under_gallery()`, measured on the built `LOD0`).
  - It runs along the west wall over the plan bounds' full depth.
  - Its width runs from the coping's oversail (the wall's furthest-west
    surface at any height) to the gallery's far end.
  - Its clear height is the gallery's underside at its far end.
  - It is open at both ends.

```
{"id": "under_gallery", "position": [-16.05, 0.0, 9.625], "forward": [0.0, 0.0, -1.0], "width_m": 4.95, "length_m": 19.25, "clear_height_m": 14.4051, "through": true}
```

**Preview.** `preview.png` uses the catalog's fixed camera orientation, lens,
sun and flat grey world (`asset_build.preview_studio()`), with the distance
fitted to the `LOD0` bounds. It shows `LOD0`, the default variant, with the
lights off.

## Review status

Checked here, in Blender:

- `scripts/validate_asset.py`: 0 FAIL.
  - All four tiers have uri-only external images, one opaque material slot,
    and welded manifold topology.
  - Their hidden-surface candidates are only the exterior faces listed under
    Interior geometry (207, 99, 35 and 0 triangles).
  - The pivot is at ground level and centred.
  - Every tier binds emission on UV0, default off, and the normal map at
    scale 1.
  - Six 1024² RGB PNGs; normal vectors are unit length and face out.
  - The glass measures in band and darker than the trim.
  - The facts sidecar is consistent: 3 doors and 1 passage.
  - The one warning is `source.dirty` in the sidecar, expected until the
    asset is committed and the sidecar regenerated with `build.py -- facts`.
- `check_layout()` and `check_regions()` pass.
- The six pre-export views at `LOD0` (four orthographic elevations, the top
  view and the raised front three-quarter aerial). Also the aerials off the
  other three corners, and eye views at the entrance, the machinery door,
  the flue stub, the gallery head, the boiler house's roof and its east face
  over the hall roof. The same views were made at `LOD2` and `LOD3`.
- In those views:
  - the band's lights and spandrels;
  - door scale against the 2.3 m entrance leaf;
  - brick coursing scale, and no visible slab lines or panel edges;
  - the lettering's spacing;
  - glass darker than its frames;
  - the gallery's slope and its joint with the wall under the coping;
  - the bay's windows centred on every face;
  - the stacks' open flues.
- The before/after review sets (`scripts/review_asset.py`, identical
  settings) and their comparison sheets (`scripts/review_compare.py`). The
  after renders were padded to the before canvas, since the bounds grew.
- The LOD3 glazing exception, re-measured (Texture set).
- Mip 3 and mip 4 stress renders (Texture set, *Filtering*), and the day
  cycle (morning, noon, dusk, and night with emission on) on the reimported
  `LOD0`.
- The variant sheet (`variants.png`): day and night for all three colours.
- The plant palette pass: ORM, normal and emission maps pixel-identical to
  the previous build, triangle counts and bounds unchanged; the yellow
  albedo changed only in the lettering; a 35 m oblique noon render of each
  variant before and after; the three variants distinct in `variants.png`.

- The polish pass: before/after sets with identical settings and their
  sheets; the sidecar diffed against the previous one (only triangle
  counts, hashes and source changed); `check=True` on every appended kit;
  the `LOD3` small windows re-measured. The mip 3/4 stress renders were not
  re-run after the atlas repack: the moved regions keep 4 px gutters and
  are padded by `pad()`, but that review is outstanding.

Pending, outside this repository:

- **In the consumer:**
  - import, MikkTSpace tangent generation and the normal map at distance;
  - mip and anisotropic filtering;
  - LOD switching, night exposure and spill;
  - runtime performance;
  - how this piece sits beside the plant's other four, the coal reception's
    gallery meeting this one's end above all.

## Tooling versions

- **Blender 5.3.0**, headless, which saved `source.blend`. The MCP addon was
  not used for this asset.
- **CPython 3.14.10** with numpy 2.5.5, scipy 1.18.1 and Pillow 13.0.0, for
  the texture export.

These are recorded as known-good markers, not requirements.

## Revision log

- **2026-11-21**: Polish pass; LOD0 bounds, pivot, footprint, doors, the
  gallery head and the `under_gallery` lane unchanged (the sidecar differs
  only in triangle counts, hashes and source).
  - Rebuilt both caged wall ladders as `roof_safety.py`'s lean kit,
    appended on `LOD0`–`LOD2`: the kit went from 3554 to 1412 triangles at
    `LOD0` and from 1368 to 830 at `LOD1`, which now keeps every other rung
    and hoop.
  - Cut the bunker bay's 20 windows as recessed openings on `LOD0`/`LOD1`.
  - Gave the stub stacks aluminium paint grading to soot at the mouth, a
    modelled cap ring and stiffening rings, a guy collar and a painted caged
    ladder.
  - Made the coal dust under the gallery a broad soft stain on a larger
    panel (3.75 × 3.875 m), dusted the gallery's underside and lower sheet
    and the coping over it.
  - Laid an even light soot film on all the brick.
  - Repacked the atlas for the larger panel: the bushing panel at 48 px/m,
    the flue stub's sides at 32 px/m, two new regions.
  - Re-measured the `LOD3` small square windows with their frames.
- **2026-11-21**: Plant palette pass: `red_brick` and a darker, purple-brown
  `brown_brick` set to the plant's shared constants, dark lettering on
  `yellow_brick`, and the coal bunker bay dropped from the sidecar's storeys.
- **2026-11-21**: Revised the hall's weak spots.
  - Retired the exposed concrete frame: the walls are continuous brick,
    with a flush 0.375 m concrete coping in place of the oversailing edge
    beam.
  - Replaced the roof monitor with a raised coal bunker bay and two steel
    stub stacks.
  - Replaced the coal hatch with the gallery head (and a lane under it in
    the sidecar).
  - Regrouped the windows: the boiler house's central band of lights on
    spandrels, four tall hall windows on the turbine hall, small square
    windows elsewhere.
  - Recoloured `red_brick` by the plant's shared formula.
  - Added coal dust, the lettering, and the decks' felt, drains, hatches,
    kerbs and paving.
  - Gave both wall ladders safety cages.
  - Dropped the downpipes for internal drainage.
