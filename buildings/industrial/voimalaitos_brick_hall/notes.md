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
    lights on brick piers, 7.1 m wide and 3.5–17.0 m up, in three tiers on
    light concrete spandrels. The outer bays are blank brick with a column of
    small square gallery windows.
  - The main entrance, under a concrete canopy, stands at the foot of the
    band.
  - A **raised coal bunker bay** runs along the rear half of its roof, 13.75
    × 6.5 m and up to 23.97 m. It is brick with a row of small square
    windows and a coping.
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
yard). The hall carries **no conveyor gallery**: the coal reception carries
the whole gallery and ends it against this hall's west wall, at a **closed
conveyor inlet** in a steel frame standing 0.05 m proud, which reads as
complete when the hall stands alone or beside anything else. Nothing joins the pieces: no
ground, base, gallery, pipe bridge or cable reaches out of this asset. The
sides facing the other pieces are designed for them (Construction, *Sides
facing the other pieces*).

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
| Overall plan bounds, with the copings, the entrance canopy (1.25 m) and the flue stub (1.0 m) | 32.10 × 19.25 m |

Heights:

| | Boiler house | Turbine hall |
| --- | --- | --- |
| Plinth top | 0.625 m | 0.625 m |
| Coping foot | 19.140625 m | 11.25 m |
| Deck | 18.671875 m | 10.78125 m |
| Coping top | 19.515625 m | 11.625 m |
| On the roof | bunker bay to 23.96875 m, stub stacks to 24.75 m | ventilators to 11.98 m |

Every height where brick meets something else is a whole number of the
catalog's 0.078125 m courses (Texture set, *The brick band and the slab
lines*).

The stacks' tops set the height of the bounds on every tier.

The pivot is at ground level, centred on the plan's bounding box. The box
runs from the boiler house's west coping (build x -16.05) to the turbine
hall's east coping (16.05), and from the canopy's front edge (y -9.75) to
the flue stub's end (9.5). That puts the pivot at build (0, -0.125, 0). It
is taken from `LOD0` and applied to every tier. Every tier keeps the
copings, canopy, flue stub, bunker bay and stacks, so the extents never
change.

**In the glTF frame** (+Y up, +Z front, origin at the pivot):

- **Bounds:** [-16.05, 0, -9.625] to [16.05, 24.75, 9.625].
- **The west (coal) wall's face** is the plane x = -16.0. The furthest
  west anything reaches is x = -16.05, the bounds' face: the coping's outer
  face at 19.14–19.52 m and the conveyor inlet's frame face at
  15.8176–18.9176 m (y, glTF), the plane the coal reception's gallery
  butts against.

Standing outside the footprint polygon but inside the bounds:

- the copings (0.05 m all round, from 11.25 or 19.14 m up);
- the conveyor inlet's steel frame (0.05 m, at 15.8176–18.9176 m);
- the entrance canopy (1.25 m, at 3.28–3.52 m);
- the flue stub (1.0 m, at 12.73–14.77 m);
- the lower wall ladder and its cage, up to 0.9 m off the turbine hall's
  rear wall, from the ground.

Nothing stands on the ground outside the footprint: no steps, ramps, bases,
props or pipes. Below its coping nothing projects from the west wall but
the conveyor inlet's frame, to the coping's own plane (Construction, *The
conveyor inlet*).

## Story height

**One working storey at the ground in each volume.**

- The boiler house rises 18.67 m from its floor to its deck, the turbine
  hall 10.78 m. Both are authored departures from the 3.0–3.3 m standard, and
  both are the type's. A boiler house is one tall volume round the boiler,
  its galleries open steelwork inside; a turbine hall is one volume under its
  overhead crane. The boiler house's small windows mark gallery levels every
  3.75 m, but none is a built floor.
- The bunker bay stands on the boiler house's roof, 18.67 m, under a roof
  5.3 m above it. It holds coal, not people, so it is no storey.

The facts sidecar lists one storey: the ground, 526 m² inside the outer
wall faces (238 m² + 288 m²).

## Door leaf height

- **Main entrance (boiler house front, at the band's foot): a pair of framed
  steel leaves, 1.81 × 2.30 m clear.** Each leaf has a tall light. A 0.09 m
  steel transom at 2.30–2.39 m separates them from a four-light fanlight that
  runs to the 3.05 m head. The opening is 2.0 × 3.046875 m (16 half
  stretchers × 39 courses), under a concrete canopy at 3.28 m. Its axis
  stands 0.0625 m west of the band's middle light's (Window sills).
- **Machinery door (turbine hall front, east bay): four folding steel
  leaves, 3.19 × 3.89 m clear** in a 3.375 × 3.984375 m opening (27 half
  stretchers × 51 courses), on one axis with the window over it. It is a
  vehicle door, sized for plant, not a leaf at human scale. A wicket door,
  0.8 × 2.05 m, is painted into the second leaf. A row of small lights near
  the head is glazing, lit at night.
- **Service door (turbine hall rear, west bay): one steel leaf, 1.06 × 2.10
  m clear**, under a louvred vent panel to 2.33 m, in a 1.25 × 2.421875 m
  opening (10 half stretchers × 31 courses).

All thresholds are at ground level, onto the hall floors, so there are no
steps and no handrails.

## Window sills

There are two steel window designs:

- **The hall window**: a 0.0625 m frame and panes 0.5 × 0.75 m on 0.047 m
  bars, every third pane row a hopper. Its opening is rounded to whole
  courses, and its pane rows stretch to fill it (`win_k()`): by +0.8 % in
  the band's lights, -0.3 % over the machinery door, not at all in the
  hall windows.
- **The small square window**: 0.75 × 0.78125 m (six half stretchers by
  ten courses, as near square as the brick allows), four panes on a cross.

Every window's sides fall on whole or half stretchers. The hall windows
are an odd number of half stretchers wide (nine or thirteen), so their axes
stand a sixteenth of a metre off the half-stretcher grid.

Fifty-six windows are cut into the walls:

| Where | Count | Size (w × h) | Sill | Head |
| --- | --- | --- | --- | --- |
| Boiler house front, the band's lights (3 tiers × 5) | 15 | 1.125 × 3.90625 m | 3.75 / 8.28125 / 12.8125 m | 7.65625 / 12.1875 / 16.71875 m |
| Boiler house front, outer bays | 8 | 0.75 × 0.78125 m | 3.984 / 7.734 / 11.484 / 15.234 m | +0.78125 m |
| Turbine hall front, hall windows | 4 | 1.625 × 6.875 m | 2.50 m | 9.375 m |
| Turbine hall front, over the machinery door | 1 | 1.625 × 4.609375 m | 4.765625 m | 9.375 m |
| Turbine hall rear | 7 | 0.75 × 0.78125 m | 2.03125 (3) / 7.734 (4) m | +0.78125 m |
| Turbine hall east | 2 | 0.75 × 0.78125 m | 7.734 m | 8.516 m |
| Boiler house rear | 10 | 0.75 × 0.78125 m | 3.984 to 15.234 m, every 3.75 m | +0.78125 m |
| Boiler house west | 7 | 0.75 × 0.78125 m | 3.984 to 15.234 m (three under the conveyor inlet) | +0.78125 m |
| Boiler house east, over the hall roof | 2 | 0.75 × 0.78125 m | 15.234 m | 16.016 m |

The band's five lights stand on 0.375 m brick piers (three half
stretchers), 1.5 m apart. Its axis is x -8.9375 (build), a sixteenth east
of the entrance's: the lights' odd width puts it off the grid the
entrance's even width keeps to. The 0.06 m does not read under the canopy.
The turbine hall's windows and the machinery door stand on axes at x
0.5625, 3.8125, 7.0625, 10.3125 and 13.5625.

The bunker bay carries 20 more square windows (seven on each long face,
three on each end), sills at 21.25 m and heads at 22.03 m. They are cut
with 0.20 m reveals on `LOD0`/`LOD1` and painted flush from `LOD2`
(Construction, *The bunker bay*).

The band sits on a 0.234 m (three-course) concrete sill at 3.52–3.75 m,
directly over the entrance canopy. Its spandrels are 0.625 m (eight
courses), and its head is 0.234 m, to 16.95 m. The only
ground-level sills are the turbine hall's 2.5 m and the rear's 2.0 m. Both
sit above the 1.4 m chest line, and the 2.3 m entrance leaf sets the scale
below them. Every higher window lights a single tall volume, not an occupied
floor, which is the type.

## Eave overhang

**None: flat roofs behind a parapet.**

- The brick walls run up 0.46875 m (six courses) past each deck to a
  precast concrete coping 0.375 m tall. It oversails the brick by 0.05 m outside and the
  parapet's inner face by 0.05 m inside. That is a parapet roof's flush
  edge, not an eave.
- The turbine hall's parapet is open on its west side, where its deck runs
  to the boiler house's face.
- The bunker bay's top edge is a 0.375 m coping band on its own brick,
  flush.

## Construction

`build.py` builds up to ten closed solids and unions them with
Blender's exact boolean (`asset_build.union`):

- **The shell**: both volumes' walls as one closed solid, meshed directly.
  - On `LOD0`/`LOD1` it also carries both roofs' parapets (their tops, their
    brick inner faces and the sunk decks), so it closes with its floor alone.
  - On `LOD2`/`LOD3` flat lids at the wall tops close it, under coping boxes.
- **The copings**: a ring over each parapet (on `LOD2`/`LOD3`, a box over
  the whole roof, its top the deck). The boiler house's west face is cut
  2 m either side of the conveyor inlet's axis, and that middle stretch
  samples the dusted coping (`COPE_DUST`).
- **The coal bunker bay** and the two **stub stacks**.
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
- the lettering and the dusted brick round and under the conveyor inlet
  (Texture set), the latter cut round the inlet's frame;
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

The bay is one closed box on every tier, because it is silhouette, 13.75 ×
6.5 m in plan. Its faces stand 0.125 m behind the walls under it on the
west, rear and east, so the boiler house's coping reads as a string course
under it. Its front stands on the deck at y 1.875. Its corners and windows
fall on whole and half stretchers, and the bond turns at its corners.

Each face is four horizontal bands:

| Band | Height | Texture |
| --- | --- | --- |
| Brick | to 21.015625 m (cut at the 20.0 m slab line) | brick band |
| Window row | 21.015625–22.265625 m | the atlas's BUNKER band |
| Brick | 22.265625–23.59375 m | brick band |
| Coping | 23.59375–23.96875 m | coping band |

The window row is brick with a square window every 2.0 m, one centred on
each face: seven on each long face, three on each end
(`bunker_windows()`). The band paints each window with a one-course
concrete sill under it and the recess's occlusion round it. Each face
samples the brick band at the U the row's band has there (`bunker_u()`),
so the bond runs on across the row's edges.

- On `LOD0`/`LOD1` each window is cut into the row's face (a polygon with
  20 holes in all), with 0.20 m concrete reveals and the small square
  window's region on its closing plane, as on the walls. The painted sill
  under each hole stays, as a sill. The 20 windows cost 320 triangles.
- From `LOD2` the band's painted windows stand flush, as the walls' do.

Its top is a felt roof with a drain and a hatch, its edge the coping's
top.

Its west face stands 0.125 m behind the wall, inside the parapet, but the
conveyor inlet's recess is 0.12 m deep and its head (18.77 m) is above the
deck (18.67 m), where the bay's buried foot starts (18.47 m). So below
19.0 m (`BUNKER_STEP_Z`), hidden in the parapet, the bay's west face steps
back a further 0.05 m (`BUNKER_STEP`) to 0.175 m behind the wall, behind
the inlet's blanking panel, 0.055 m clear of it rather than the 5 mm the
bay's plain face would leave. Nothing of the step shows, and the bay's visible
faces are unchanged.

### The conveyor inlet

The hall carries no conveyor gallery: the coal reception's gallery, rising
at 20°, ends against the west wall. Where it would enter, the wall
has a **closed inlet** that reads as complete on its own (`inlet_polys()`,
`facade_atlas.INLET_*`):

- **Opening:** the gallery's section, 2.6 m wide (along y) × 2.8 m tall,
  centred at build y 4.5 (s 4.0 m from the wall's rear corner, the old
  stub's mouth position) and at **17.3676 m**, computed as
  13.0 + 12.0 tan 20° (`INLET_ZC`): sill 15.9676 m, head 18.7676 m.
- **Recess:** 0.12 m deep (`INLET_DEPTH`), lined with galvanised steel
  reveals (the `lining` patch), closed at the back by a **dark steel
  blanking panel**: three bolted plates on two joints with two upright
  stiffeners, painted in the inlet's region with the head's and jambs'
  shadow.
- **Frame:** a galvanised steel frame 0.15 m wide all round, 2.9 × 3.1 m
  outside (15.8176–18.9176 m), bolted every 0.3 m, standing **0.05 m
  proud of the brick** (`INLET_PROUD`, equal to the copings' oversail
  `CO`, which `check_layout()` asserts). Its face is flat (the painted
  bolts and edge arrises are normal-map relief only).
- **The contact plane** is the frame's face, glTF x = -16.05: the same
  plane as the coping's outer face and the hall's bounds face. The coal
  reception's gallery's end (2.6 × 2.8 m, its flashing collar 0.05 m
  proud all round, 2.70 × 2.90 m outside) butts against the frame there
  with 0.10 m of frame showing round it, so the two pieces' plan bounds
  meet without overlapping and without a slot between gallery and wall.
  The frame's head is 0.22 m under the coping's foot (19.14 m), and
  nothing passes x = -16.05.

The frame is part of the shell, not a separate solid: its face (a ring
round the opening), its four outer returns down to the brick, and the
opening's reveals running from the frame's face to the panel, all meshed
directly with the wall, so it needs no union. Returns and reveals sample
the galvanised `lining` patch; face and panel the inlet's region.

- `LOD0`/`LOD1`: the frame as above and the recess cut 0.12 m behind the
  brick (0.17 m behind the frame's face), 26 shell triangles with the
  wall's extra vertices.
- `LOD2`: the same ring, its reveals stopping at the brick and the panel
  in the wall's plane, so the panel is 0.05 m behind the frame's face (28
  shell triangles). The tier had room (1,452 of 1,500).
- `LOD3`: painted on the west elevation, flat. The frame's 0.05 m is
  half a pixel at 120 m, and the coping already sets x = -16.05 on every
  tier, so the bounds do not depend on it.

The inlet is the one opening off the course and stretcher grid: its size
and height are the coal reception's gallery's, and its proud frame covers
the brick's cut. The small square window under it (11.48–12.27 m) and the
other west windows keep their places.

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
| Stiffening rings | 20.92–21.00 and 22.92–23.00 m | 0.03 m | `LOD0` |

Every ring is also painted, with its shadow line, on every tier, so a tier
that drops its geometry keeps it in the texture (`stack_rings()`). The cap
ring shapes the mouth's outline, so it stays to 70 m; at 35 m the
stiffening rings are about a pixel proud.

The rest is texture: welded seams every 1.5 m, the foot flange, a guy
collar at 23.67 m with a lug on seven faces, and on face 6 (facing the
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
| Rear of the boiler house | +Y | -Z | the chimney stack | the **flue stub**: a 2.0 m wide × 2.03 m tall concrete casing projecting 1.0 m at 12.73–14.77 m in the middle, its end closed by a bolted steel blanking plate, sooted. In glTF its end face is centred at (-9.0, 13.75, -9.625). Nothing reaches beyond it. |
| West end of the boiler house | -X | -X | the coal reception | the **closed conveyor inlet** (above), the coal reception's gallery ending against it. In glTF the wall face is x = -16.0 and the inlet's centre is (-16.0, 17.3676, -4.625): a 2.6 m (along Z) × 2.8 m opening recessed 0.12 m to a steel panel, in a 2.9 × 3.1 m steel frame standing 0.05 m proud. The frame's flat face is the contact plane, x = -16.05, the coping's outer plane and the hall's bounds face: the gallery's end butts against it there. Nothing projects beyond it. Coal dust stains the brick round and under it. |
| East end of the turbine hall | +X | +X | the transformer yard | the **cable bushing panel**: flush and painted, 2.5 × 1.25 m at 6.25–7.5 m in the middle (both on the course and stretcher grid). It is a concrete panel in a steel frame with three porcelain bushings and cable glands. Otherwise blank brick between two small windows. |

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
  coping (9.43 m long).
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
- From `LOD2` the hall's roof is its coping box, whose top is 0.84 m above
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
- the brick module, `COURSE` 0.078125 and `BRICK_L` 0.25 from
  `scripts/brickwork.py`, and `courses()` and `HALF` (0.125), the grids
  every brick-bound height and plan position keeps to;
- the heights: `Z_PLINTH` 0.625 (8 courses), `COPING` 0.375, `CO`/`CO_IN`
  0.05, `PIN` 0.25, `WALL_IN` 0.125, `DECK_DOWN` 0.84375 (the coping and
  six courses), `Z_BS` 19.140625 (245 courses) and `Z_TS` 11.25 (144);
- `CUTS` and `SLAB` (48 courses) for the brick;
- the window designs (`FR`, `CW`, `RH`, `MUL`, `SQ_W`, `SQ_H`), and
  `win_size()`/`win_k()`, the openings rounded to whole courses;
- the window band (`BAND_X`, `LIGHT_PIER`, `LIGHT_X`, `TIERS`,
  `BAND_STRIPS`, `SQ_Z`) and the turbine hall's windows (`TH_WIN_X`,
  `TH_SILL`, `BIGDOOR_X`);
- `SIZES` and `REVEAL` for the other openings;
- `WALLS` and `ITEMS`;
- `CANOPY`, `FLUE`, `BUNKER` and `BUNKER_SILL`, `STACKS` and the stacks'
  rings (`STACK_CAP`, `STACK_STIFF`, `STACK_GUY`, `STACK_LADDER_FACE`),
  `VENTS`, the conveyor inlet (`INLET_*`) and the dusted coping
  (`COPE_DUST_HALF`).

`check_layout()` asserts:

- the openings' and panels' clearance from corners, each other, the coping
  and the slab lines, the leaf heights and a transom or vent panel over
  each leaf;
- the brickwork (`brick_problems()`): every brick-bound height (plinth,
  coping feet, decks, the band's top and slab lines, every opening's and
  panel's sill and head, the canopy, the flue stub, the bunker bay's rows,
  coping and windows) on a course line; every opening's sides, and so
  every pier, and the canopy's and flue stub's on a whole or half
  stretcher in the U its wall samples; the bond turning a half stretcher
  at every corner, the bunker bay's included; the step face on the
  returns' bond. The conveyor inlet is exempt (the gallery sets it), and
  the lettering and dusted panels are held to the band's rows and U by
  `check_regions()`;
- the ladders' and cages' places, and the upper ladder's landing clear of
  the bay;
- the conveyor inlet at the gallery's section and height (2.6 × 2.8 m at
  13.0 + 12.0 tan 20°), its frame wide enough for the gallery's collar,
  clear of the coping's foot and proud by the copings' oversail, its
  recess shallow, the west windows clear of
  it, the dusted panel wrapping its foot, and the bunker bay's buried foot
  stepped back behind the recess;
- the bay within the parapets, and the stacks and ventilators clear of each
  other, the parapets and the ladders.

## Per-tier triangle counts

| Tier | Triangles | Ceiling |
| --- | --- | --- |
| `LOD0` | 4144 | 12,000 |
| `LOD1` | 3306 | 4,000 |
| `LOD2` | 1452 | 1,500 |
| `LOD3` | 304 | 500 |

Where they go, counted on the solids before the union (the kit is appended
whole, so its count is exact):

| | `LOD0` | `LOD1` | `LOD2` | `LOD3` |
| --- | --- | --- | --- | --- |
| Shell (walls, openings, the conveyor inlet, parapets, decks) | 1638 | 1638 | 1134 | 32 |
| Copings | 68 | 68 | 32 | 32 |
| Bunker bay (its windows cut to `LOD1`; its lower brick cut at the 20.0 m slab line) | 372 | 372 | 52 | 52 |
| Stub stacks (their rings, `stack_rings()`) | 440 | 184 | 120 | 120 |
| Ventilators | 56 | 56 | 0 | 0 |
| Flue stub and canopy | 24 | 24 | 24 | 24 |
| Roof safety kit | 1412 | 830 | 48 | 0 |

The **roof safety kit's share of the finished tier**:

| | `LOD0` | `LOD1` | `LOD2` | `LOD3` |
| --- | --- | --- | --- | --- |
| Kit | 1412 (34.1 %) | 830 (25.1 %) | 48 (3.3 %) | 0 |
| The rest | 2732 | 2476 | 1404 | 304 |

Two ladders of 12.6 m and 9.43 m make 22 m of rail and 76 rungs, and both
cages are required by length. As the lean kit it cuts nothing: a rung is a
three-sided prism of 8 triangles, the hoops and straps are three-sided, and
no rail or strap is split where another part meets it. Unioned, the same
kit was 3554 triangles at `LOD0` and 1368 at `LOD1` (every third rung and
hoop), 63.5 % and 40.1 % of those tiers. `LOD1` keeps every other rung and every other hoop, and its
brackets as tetrahedra.

The kit is still over the quarter of a tier CLAUDE.md suggests for trim at
`LOD0`, by 9 points, because the rungs are kept whole. `LOD0` has 7,856
triangles to spare, and thinning rungs that read at 20–35 m would show.

The 20 cut bunker windows (320 triangles to `LOD1`) and the stacks' rings
(320 at `LOD0`, 64 at `LOD1`) are what the lean kit's saving paid for.
`LOD1` keeps 694 (17.4 %) of its ceiling, `LOD2` 48.

The conveyor inlet replaced the 12-triangle gallery head. Cut on
`LOD0`/`LOD1` (frame face with a hole, four reveals, the panel) and with
the dusted panel now notched round it, the shell grew by 32 triangles; on
`LOD2` the flush inlet and the notched panel cost 16 more than the old
flush panel. The bunker bay's stepped west foot (*The bunker bay*) adds 8
before the union, all buried. Net of the gallery and its joins with the
wall, the tiers moved by +16, +16, -4 and -20. Standing the frame 0.05 m
proud added its four outer returns: +8 on `LOD0`/`LOD1`, and +22 on
`LOD2`, where the flat quad became the ring with its returns, reveals and
panel (+24 before the coplanar cleanup).

## LOD review

Review camera: `scripts/review_asset.py`, perspective, 50° vertical FOV,
1920×1080, Cycles (16 samples in the earlier passes, the script's default
24 in the conveyor-inlet pass), distance along the view direction to the
centre of the facing wall. The west-wall views come from scratch
wrappers round the script, which itself is unchanged: `left` and two
views 30° up off the west corners, aimed as the script aims; and, since
those see the coal wall nearly edge-on, `west` (8° up), `west_front` and
`west_rear` (25° up, 50° off the wall's normal) built from the script's
own scene, lights and camera but aimed at the west wall's centre, 10 m up
(`westwall/`, `westwall_lod/`).

| Switch | Intended distance | Renders |
| --- | --- | --- |
| `LOD0` → `LOD1` | ~35 m | 30 and 40 m, `LOD0` and `LOD1`, front, oblique, rear, west and front-west oblique, noon |
| `LOD1` → `LOD2` | ~70 m | 65 and 75 m, `LOD1` and `LOD2`, the same views, noon; 60 m oblique at night, emission on |
| `LOD2` → `LOD3` | ~120 m | 115 and 125 m, `LOD2` and `LOD3`, the same views, noon; 120 m oblique at night, emission on |

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
  is unchanged: the bay, stacks, canopy, flue stub and coping line. So are
  the window band, the spandrels and the lettering. The conveyor inlet's
  recess shallows from 0.17 m to the frame's 0.05 m (the panel in the
  wall's plane); its head and jamb shadows are painted, so it stays a dark
  framed rectangle.
- **120 m.** `LOD3` replaces the walls' geometry with the 6 px/m
  elevations. The plinth, the band and its spandrels, the windows, the doors
  and the lettering are painted on single faces. At 120 m a metre is about
  9.7 px, so the elevations are slightly soft. The bay and the stacks keep
  their geometry and textures; the conveyor inlet and its dust are painted
  on the west elevation. The ladder rails go. The hall
  windows average within about 10 sRGB levels of what `LOD2` samples, the
  small square windows within -13 to +6 measured with their frames
  (Texture set, *The LOD3 elevations*); at 115/125 m they read alike.

The working renders are local and git-ignored:

- `review/brick_recourse_2026_11_22/voimalaitos_brick_hall/`: the
  re-course pass. `before/` (the asset folder copied first),
  `before_renders/` and `after/` (front, oblique and rear at 20, 35, 70
  and 120 m at noon, and at 35 m at night with emission on, `LOD0`–`LOD3`,
  identical settings), sheets in `compare/` and `compare_brick/`,
  `views_pass1/` (`LOD0`, `LOD2`) and `views_pass2/` (`LOD1`, `LOD3`), the
  atlas brick band at mip 3 (`mip3_brick_band.png`), and the brick beside
  `kaivoskonttori_brick` at 20 and 35 m (`brick_vs_kaivoskonttori.png`);

- `review/followups_2026_11_21/hall_inlet/`: `before/` (rendered from the
  copy in `../before_snapshot/voimalaitos_brick_hall/`) and `after/` of
  the inlet frame pass: the inlet from 10 m (`west`, `west_front`,
  `west_rear`, noon and reversed light) and the west wall at 30 m, on
  `LOD0`, `LOD1` and `LOD2`;
- `review/conveyor_joint_2026_11_21/`: `hall_before/` (rendered from the
  copy in `before_snapshot/voimalaitos_brick_hall/`) and `hall_after/`
  (six views, the west views at 30 m at noon and with the light reversed,
  and the LOD pairs, the west-wall views among them), sheets in `hall_compare/` (after padded to the
  before canvas, since the bounds shrank), and `hall_views/` (the build's
  views at `LOD0`, `LOD2` and `LOD3`, `eye_inlet` among them);
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
| `LOD0` | 205 (4.9 %) |
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
items' buried feet, and the flue stub's and canopy's backs are all removed
by the union. There are no buried partitions or duplicate surfaces.
Recessed glass and doors, and the conveyor inlet's reveals and blanking
panel, are exterior surfaces, as are its frame's face and outer returns.
The inlet is a 0.12 m recess closed by its panel, so the wall stays closed
and no interior shows.

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
  - the conveyor inlet's bolts and edge arrises (its frame stands 0.05 m
    proud as geometry), the blanking panel's plates, joints and
    stiffeners, and the whole inlet on `LOD3`;
  - the lettering;
  - the stacks' flanges.
- **Painted on the roofs:** the felt's laps and mineral grain, the parapet
  upstand, the drain outlets, the hatches, the skylight kerbs (opaque, dark)
  and the paving where people walk.
- **Not modelled:**
  - sills (a concrete reveal face, and the band's flush concrete sill);
  - a lintel over the machinery door (plain brick above it);
  - the plinth step (flush with the brick).
- No boiler, turbine, crane, conveyor or conveyor gallery (the coal
  reception carries the gallery to the inlet), flue duct beyond the stub,
  pipe bridges, cables, ground slab or yard. Each piece of the plant is its
  own asset.
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
| 0–320 | BRICK | z 0–5.0 m: the plinth (0–0.625 m) and the catalog's stretcher-bond brick |
| 320–340 | | the bond carried on into the gutter, meeting the bunker band's brick |
| 345–425 | BUNKER | 1.25 m of brick with a square window every 2 m: the bunker bay's window row |
| 440–480 | CONC | 0.625 m of light precast concrete: the band's sill, spandrels and head (V up the panel), and the reveals (V the depth) |
| 488–512 | COPE | the 0.375 m concrete coping, its units a metre long, a drip groove at its foot |
| 518–530 | PIPE | galvanised steel; `PIPE_STRIP` is rows 520–528 |
| 536–1020 | unique | see below |

Every 3.75 m slab's top samples the brick band's last row. So the bond runs
on into the gutter above it, and the band above that is the bunker bay's,
also brick, on the same course rows. A coarse mip there still averages brick. With the concrete band next
door, as first laid out, the slab lines showed as light hairlines at mip 3.

The unique regions:

- the hall window (2.125 × 3.125 m, four by four panes) and the small
  square window;
- the machinery door, the entrance and the service door;
- the flue's end and sides, and the bushing panel;
- the lettering and the dusted brick round and under the conveyor inlet,
  both 64 px/m brick;
- the conveyor inlet, frame and blanking panel in one 2.9 × 3.1 m region
  at 40 px/m (`INLET`, 116 × 124 px), in the space the gallery's three
  regions left;
- two stack faces (32 px/m): the plain one, and the one with the ladder,
  turned a quarter (U up the stack) to fit a 20-row strip;
- the dusted stretch of the west coping, 4.0 × 0.375 m, painted as the
  coping band at the U its face samples it at, so its unit joints run on;
- the two roof decks (8 px/m);
- the five `LOD3` elevations (6 px/m);
- ten flat patches (`lining`, the inlet's reveals, in the gallery
  underside's place).

`check_regions()` asserts:

- that the regions neither overlap nor run off the sheet, and that each
  matches its face's size;
- the bands' periods, that the brick band tiles on whole courses and
  bricks, and that the brick regions keep the band's bond (a panel may
  cross a slab line, since a slab is 240 rows, 24 bond repeats);
- that the bunker band's windows and their one-course sills fit its rows;
- that the lettering fits its panel, and the elevations and decks their
  walls and roofs.

`pad()` fills every unclaimed texel from the nearest region's edge.

### The brick band and the slab lines

The brick is the catalog's, painted by `scripts/brickwork.py`'s `paint()`:
0.25 m stretchers (16 px) on 0.078125 m courses (5 px), 1 px recessed
joints, a hashed tone per brick and about one in six the darker id
(`TONE_COURSES` 48, seed 17). Courses run from the plinth's top, row 40.

The walls are far taller than the brick band, so above 5.0 m they are cut
at 5.0, 8.75, 12.5, 16.25 and 20.0 m into 3.75 m slabs (`CUTS`). Slab *i*
samples the band 3.75*i* m lower, its rows 1.25–5.0 m. The bond and tones
repeat every 48 courses (240 rows), and so does every noise field, so the
slab lines vanish. No power-of-two division of the sheet is a whole number
of 5 px courses, so `atlas.noise()`'s `tile_y` cannot give that period:
`slab_noise()` makes it locally (the same FFT-blurred field on a 240-row
period, tiled up the sheet), and `SlabWeather` gives `weathering.Weather`'s
named fields the same period. Rows above 1.25 m are clean brick: the
splash-back and salt bloom stay below. `check_layout()` keeps every
opening's edge 0.1 m off a slab line.

The bunker bay's brick is cut at the slab lines too (its lower brick at
20.0 m), each piece sampling its own slab.

`brickwork.py` has no low-density painter, so `paint_brick_lo()` (the
`LOD3` elevations' brick at 6 px/m, brick, darker brick and mortar per
sample in their proportions) stays local, as does `slab_noise()`.

### Brick that continues the band

Three places carry brick that cannot come from the tiling band:

- **the lettering panel** under the turbine hall's coping, 10.5 × 1.25 m;
- **the dusted panel round and under the conveyor inlet**, 3.875 ×
  3.906 m at 12.656–16.563 m, centred under the inlet and cut round the
  foot of its frame (a notch 2.9 m wide from 15.82 m up), where coal dust
  falls from the inlet's sill. It crosses the 16.25 m slab line, which the
  bond does not see, and stops 0.39 m over the head of the small window
  under the inlet. It is about the largest 64 px/m square the sheet holds
  (`MOUTH`, 248 × 250 px);
- **the bunker bay's window row**.

Each is painted by `brickwork.paint()` as the band is, so its bond runs on
into the band's across its edges:

- The two panels sit in the atlas at the U their wall samples the band at:
  `U_OFF` takes the turbine hall front's and the west wall's U from them,
  and their columns (16 and 764) are chosen so that U still turns the bond
  a half stretcher at those walls' corners.
- All three sit on rows a whole number of bond repeats (10 rows, two
  courses) from the band rows their heights sample. `brickwork.paint()`
  counts courses from its rect's foot, so `paint_brick_area()` paints each
  from the last even-course row under it and hands the rows it overpaints
  below the region back to `pad()`.

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
- the conveyor inlet, at 40 px/m: the frame's face (6 px wide) and a
  plain steel panel 15.8–18.9 m up, seen from 15 m or more; the only room
  the sheet had left beside the largest dusted brick panel was the
  gallery's old 128 × 136 px corner, too small for it at 48 or 64 px/m;
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
| Conveyor inlet's frame, its edges (the frame itself is 0.05 m proud geometry) | 0.020 (bolts 0.028) |
| Its blanking panel, below the frame | -0.020 (joints -0.025, stiffeners -0.004) |
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
they reach about mip 1.3, and only past about 1 km mip 3.

The mip review after the repack and the inlet passes rendered each tier at
its switch distance and one level beyond (`LOD1` 70 m at mip 2–3, `LOD2`
120 m at mip 3–4, `LOD3` 250 m at mip 4–5), front and oblique, noon and
reverse sun, default and one contrasting variant, and again at a per-texel
mip level matched to each tier's own texel density (renders in
`review/phase2_2026_11_21/mips/voimalaitos_brick_hall/`). No gutter leak
shows at any tier's real distance: the inlet, the dusted panel, the coping
over it, the bushing panel, the flue stub's sides, the decks and the `LOD3`
elevations are clean. Latent, in the stress renders only:

- `STACK_L` (236, 740, 204, 20) sits 4 px above `WINDOW` (top 736) and
  picks up window artwork on its lower edge at mip 2–3 (36–41 levels); not
  visible at 120 m.
- `INLET`'s bottom edge picks up `MOUTH` (10 px gap) at mip 3, 29 levels
  in the yellow variant.
- The deck smear in the whole-atlas mip 3 renders is the stress test's: the
  8 px/m decks sample mip 0–1 at their real distances.

The small square bunker windows' white frames average toward pale grey at
120 m; that is averaging within the region, not a leak.

### Weathering

Weathering is `scripts/weathering.py` at its moderate level, its noise on
the 240-row slab period (`SlabWeather`):

- grime, and paint fade on the window steel, the doors, the letters and
  the stacks;
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
  even, not heavier toward the coping, because every 3.75 m slab samples the
  same band rows; for the same reason darker runs under the copings and
  sills cannot live in the band and are not painted (the coping's own face
  carries its runs);
- a light film on the coping and the boiler house's deck;
- **a broad soft stain round and under the conveyor inlet**
  (`mouth_dust()`), where a conveyor entering there would dust the wall:
  heaviest under the inlet's middle, where a belt drops its fines, over a
  fainter veil as wide as the frame, both spreading as they fall and
  broken by vertical runs. Down the middle it goes from about 0.9 at the
  sill to 0.5 at 1.5 m below and 0.3 at 3 m, then out over the panel's
  last metre, 3.3 m below the sill; it rises a little up the frame's
  sides and fades out by the panel's top at 16.56 m. It cannot run the
  5–6 m a free wall would show: the panel is already the largest 64 px/m
  square the sheet holds (the space the gallery's regions freed is a
  separate 128 × 136 px corner, which the inlet's own region now fills),
  and below it the small window at 11.48–12.27 m is shared with every
  other. The `LOD3` west elevation carries the same function;
- the conveyor inlet's frame and panel dusted, heaviest along the sill and
  in runs down the panel, and its reveals;
- the stretch of west coping over the inlet, darkest over its axis;
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

- the glass at sRGB 56–58 (linear 0.036–0.038) across the variants;
- 0.29–0.32× the brightest trim;
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
- The concrete, coping, roofs, conveyor inlet, stacks and kit are the same in every
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
  band clear of windows and plinth) measures sRGB (102.9, 76.8, 68.2) on
  `red_brick`, R − G 26.1, and (78.8, 65.2, 62.0) on `brown_brick`, R − G
  13.6, within 0.3 of the previous brick painter's. The soot film took the
  red from (110.5, 81.0, 71.9), R − G 29.5, with the palette constants
  unchanged.
- The palette constants are the plant's whatever paints the bond: the
  shared tone hash (`brickwork.paint()`, seed 17, the darker id at seed
  29) only decides which bricks take which tone, as on the plant's pieces
  already on it.
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
  | Machinery door (`machinery`), turbine hall front, 3.19 × 3.89 m | vehicle | no |
  | Service door (`service`), turbine hall rear, 1.06 × 2.10 m | service | no |

- no passages (the sidecar has no `passages` key): nothing stands over
  the ground outside the walls but the copings' oversail, the conveyor
  inlet's frame, the canopy, the flue stub and the lower ladder.

In the glTF frame (origin at the pivot, build (0, -0.125, 0)), as written
and checked against the exported `LOD0`'s vertices:

- bounds [-16.05, 0, -9.625] to [16.05, 24.75, 9.625];
- footprint from x -16.0 to 16.0, z -8.625 to 8.375 (boiler house) and
  -8.125 to 7.875 (turbine hall);
- the entrance at [-9.0, 0, 8.375], the machinery door at [13.5625, 0, 7.875],
  both facing +Z, and the service door at [0.0, 0, -8.125], facing -Z;
- the conveyor inlet (not a sidecar fact): the frame's face on the plane
  x = -16.05 (the bounds' face), from y 15.8176 to 18.9176 and z -6.075 to
  -3.175; the wall at x -16.0; the panel at x -15.88, the opening from
  y 15.9676 to 18.7676 and z -5.925 to -3.325, its centre
  [-16.0, 17.3676, -4.625].

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
    Interior geometry (205, 99, 35 and 0 triangles).
  - The pivot is at ground level and centred.
  - Every tier binds emission on UV0, default off, and the normal map at
    scale 1.
  - Six 1024² RGB PNGs; normal vectors are unit length and face out.
  - The glass measures in band and darker than the trim.
  - The facts sidecar is consistent: 3 doors, no passages.
  - The one warning is `source.dirty` in the sidecar, expected until the
    asset is committed and the sidecar regenerated with `build.py -- facts`.
- `check_layout()` and `check_regions()` pass.
- The six pre-export views at `LOD0` (four orthographic elevations, the top
  view and the raised front three-quarter aerial). Also the aerials off the
  other three corners, and eye views at the entrance, the machinery door,
  the flue stub, the conveyor inlet, the boiler house's roof and its east face
  over the hall roof. The same views were made at `LOD2` and `LOD3`.
- In those views:
  - the band's lights and spandrels;
  - door scale against the 2.3 m entrance leaf;
  - brick coursing scale, and no visible slab lines or panel edges;
  - the lettering's spacing;
  - glass darker than its frames;
  - the conveyor inlet: a framed opening closed by a dark steel panel,
    under the coping, reading as finished, with the dust stain under it;
  - the bay's windows centred on every face;
  - the stacks' open flues.
- The before/after review sets (`scripts/review_asset.py`, identical
  settings) and their comparison sheets (`scripts/review_compare.py`). The
  after renders were padded to a common canvas, since the bounds changed
  (they grew in the polish pass and shrank in the conveyor-inlet pass).
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
  the `LOD3` small windows re-measured.
- The conveyor-inlet pass: the asset folder copied to
  `review/conveyor_joint_2026_11_21/before_snapshot/` first; before/after
  sets with identical settings and their sheets; the exported tiers
  measured in the glTF frame (the frame then flush on x = -16.0, the panel at
  -15.88, the opening's centre at 17.3676 m, nothing west of the wall
  below the coping); the emission map and the glass pixel-identical to
  the previous build, and the ORM, normal and albedos changed only in the
  inlet's, the dusted panel's, the freed regions' and the west
  elevation's texels (and their gutters); the `eye_inlet` and west views
  at `LOD0`, `LOD2` and `LOD3`.

- The inlet frame pass: the asset folder copied to
  `review/followups_2026_11_21/before_snapshot/` first; the inlet at 10 m
  and the west wall at 30 m before and after, with identical settings, on
  `LOD0`–`LOD2` (the frame's returns and the deeper recess read from the
  oblique views and under reversed light; `LOD2` now reads as a framed,
  slightly recessed panel instead of a flat painted one; the three tiers
  match at 30 m); the exported tiers measured in the glTF frame (the
  frame's face on x = -16.050, from y 15.8176 to 18.9176 and z -6.075 to
  -3.175, the panel at -15.88, the opening's centre at y 17.3676,
  z -4.625; nothing west of x = -16.05 on any tier; every tier welded
  manifold); the sidecar diffed against the previous one (only triangle
  counts, hashes and source changed); the textures re-exported
  byte-identical.

- The mip review of the current atlas (Texture set, *Filtering*): every
  tier at its switch distance and one level beyond, front and oblique, noon
  and reverse sun, `red_brick` and `yellow_brick`, with whole-atlas and
  distance-matched per-texel mips. No gutter leak at any tier's real
  distance; two latent edges (`STACK_L`, `INLET`) in the stress renders.

- The re-course pass (catalog brick module): the asset folder copied to
  `review/brick_recourse_2026_11_22/voimalaitos_brick_hall/before/` first;
  before/after sets with identical settings and their sheets (no view
  reads worse: the brick keeps its colour, the band, spandrels, lettering,
  inlet and dust read as before, and no slab line shows at any distance or
  tier); the build's views at every tier; the brick band at mip 3 (no slab
  or band seam); the brick beside `kaivoskonttori_brick` at 20 and 35 m
  (the same module, bond and tone pattern, in the plant's palette); the
  LOD pairs at 35, 70 and 120 m; the sidecar diffed against the previous
  one (only the machinery door's position and size, the service door's
  width, triangle counts, hashes and source changed); `check_layout()`
  with its new brick checks and `check_regions()`.
- Not re-measured in that pass: the `LOD3` elevations' window averages
  against their `LOD2` regions (Texture set), and the mip 4 and day-cycle
  renders.

Pending, outside this repository:

- **In the consumer:**
  - import, MikkTSpace tangent generation and the normal map at distance;
  - night/emission mips, anisotropic filtering and the consumer's own mip
    generator;
  - LOD switching, night exposure and spill;
  - runtime performance;
  - how this piece sits beside the plant's other four, above all the coal
    reception's gallery ending against the conveyor inlet: its end face
    (2.70 × 2.90 m over the collar) on the bounds' plane x = -16.05,
    butting against the 2.9 × 3.1 m frame's face.

## Tooling versions

- **Blender 5.3.0**, headless, which saved `source.blend`. The MCP addon was
  not used for this asset.
- **CPython 3.14.10** with numpy 2.5.5, scipy 1.18.1 and Pillow 13.0.0, for
  the texture export.

These are recorded as known-good markers, not requirements.

## Revision log

- **2026-11-22**: Re-coursed to the catalog brick (`scripts/brickwork.py`:
  0.25 m stretchers on 0.078125 m courses, the shared tone hash) from the
  asset's own 0.0833 m courses; bounds, pivot, footprint, storeys, palette
  and every opening's kind unchanged.
  - Every brick-bound height on a course line: coping feet 19.140625 and
    11.25, decks 18.671875 and 10.78125, the band's tiers 3.75 / 8.28125 /
    12.8125 (lights 3.90625 tall), square windows 0.75 × 0.78125 at 3.984
    + 3.75 k, the door window's sill 4.765625, the lettering 9.609375, the
    dusted panel 12.65625, canopy 3.28–3.52, flue stub 12.73–14.77, the
    bunker bay's row 21.016–22.266 and coping 23.59–23.97.
  - Every opening side, pier and corner on a whole or half stretcher, the
    bond turning at every corner: the band's piers 0.375 m (lights 1.5 m
    apart, its axis x -8.9375), the hall windows and machinery door a
    sixteenth east, the machinery door 3.375 × 3.984 m on its window's
    axis, the service door 1.25 × 2.42 m, the bunker bay 13.75 × 6.5 m.
  - Slabs 3.75 m (48 courses), the noise on their 240-row period
    (`slab_noise()`, `SlabWeather`); the bunker bay's brick cut at 20.0 m.
  - `check_layout()` checks the coursing and the stretcher grid
    (`brick_problems()`).
  - Triangles 4138/3300/1452/296 → 4144/3306/1452/304.
- **2026-11-21**: Mip review of the current atlas recorded (Texture set,
  Review status); no asset change.
- **2026-11-21**: Inlet frame pass, so the coal reception's gallery meets
  the hall on its bounds' plane; `LOD0` bounds, pivot, footprint and doors
  unchanged (the sidecar differs only in triangle counts, hashes and
  source).
  - Stood the conveyor inlet's 2.9 × 3.1 m steel frame 0.05 m proud of the
    brick (`INLET_PROUD` = `CO`) as part of the shell, its flat face on
    x = -16.05 (glTF), the copings' outer plane and the bounds' face: the
    gallery's end butts against it there, with neither the 0.05 m bounds
    overlap nor the 5 cm slot a flush frame left.
  - `LOD0`/`LOD1`: the reveals run from the frame's face to the panel,
    0.17 m. `LOD2`: the same ring, the panel in the wall's plane, in place
    of the flat quad. `LOD3`: painted, unchanged.
  - Textures unchanged (re-exported pixel-identical).
  - Triangles 4130/3292/1430/296 → 4138/3300/1452/296.
- **2026-11-21**: Conveyor inlet pass, so the hall combines with any
  neighbour.
  - Removed the coal gallery stub on every tier, its three atlas regions,
    its underside patch, its layout checks and its dust, and the
    `under_gallery` passage from the sidecar (no `passages` key now).
  - The plan bounds went back to the building, 37.05 → 32.10 m across;
    the pivot moved from build (-2.475, -0.125, 0) to (0, -0.125, 0), so
    every sidecar x shifted by -2.475 m.
  - Added the closed conveyor inlet in the west wall: a 2.6 × 2.8 m
    opening at 17.3676 m (13.0 + 12.0 tan 20°), recessed 0.12 m to a dark
    steel blanking panel on `LOD0`/`LOD1`, in a flush 2.9 × 3.1 m
    galvanised flashing frame; painted flush from `LOD2`. It keeps the old
    mouth's place along the wall (build y 4.5).
  - Widened the dusted panel to 3.875 m, cut it round the inlet's frame,
    and recentred its stain on the inlet's middle with runs.
  - Stepped the bunker bay's buried west foot back 0.05 m below 19.0 m,
    inside the parapet, so the bay no longer fills the recess's head.
  - Triangles 4114/3276/1434/316 → 4130/3292/1430/296.
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
