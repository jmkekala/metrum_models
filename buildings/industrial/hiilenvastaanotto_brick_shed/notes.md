# hiilenvastaanotto_brick_shed

## Style brief

The coal reception of a small mid-century (1950s–60s) Nordic town
heat-and-power plant, of the **truck-fed** kind: coal comes by road, and
trucks drive straight through a brick tipping shed and tip their loads
through a steel grate in the floor into a pit. Rail sidings fed most plants
of the period; a small town plant added or built a truck reception as road
haulage took over in the 1960s, and this is that building. A bucket
elevator in a tower beside the lane lifts the coal to a head house, where it
drops onto the belt of an enclosed, inclined conveyor gallery that rises
toward the boiler house's bunkers.

It is one of five separate pieces of one plant, with the boiler and turbine
hall, the chimney, the office and the transformer yard. The pieces stand
apart on a lot with no ground between them. The gallery here is the whole
conveyor: it runs from the head house to the hall's coal wall and ends
against it, where the hall has a closed inlet of the same section. The
hall carries no gallery of its own.

- **Tipping shed:** 14.0 × 6.375 m of red brick between the flush columns of a
  concrete frame, on a concrete plinth, under a low 6.8° profiled-sheet
  gable roof. Three tall steel multi-pane windows sit high on the front
  wall, under the concrete ring beam.
- **Truck lane:** straight, level and doorless along the shed's length,
  open at both gables, used one way. Each gable is a plain concrete portal:
  two piers and a lintel, with brick and a shallow gable above. The mouths
  are wide dark voids, the lane's walls, soffits and ceiling black with
  dust. Painted traffic marks say what the lane is for: black and yellow
  bands on the portal legs to 2 m, a stop mark where a stopped truck's
  front is, the tipping height over the grate and a signal box at the
  entry.
- **Lean-to and tower:** behind the shed, a low brick lean-to with the
  attendant's room and the drive room. The elevator tower rises through it
  as a slim brick shaft, its stair's small windows stacked up the east face,
  to a sheet-clad head house that oversails it on three sides. The head
  house carries a loading hatch under a hoist beam with its trolley.
- **Conveyor gallery:** a pale sheet-clad box on a long-span side girder,
  with a row of small windows, leaving the head house's rear face and
  rising 12.0 m away from the building at 20° to the hall's wall, a dark
  flashing collar where it meets it. Two raking steel struts from the
  shaft carry it 4.5 m out and a braced steel trestle bent near its far
  end; the ground under its first 9 m is a truck road.

Materials are muted and coal-dusted, as a working plant's are, without
decay. Facing brick in the plant's brick trio, light cast concrete for the
frame, the plinth and the lowest couple of metres of brick blackened by the
coal the trucks throw up, only a light film on the brick above so each
variant's brick colour reads, a black dusty lane, pale grey cladding on the
head house and gallery, chalked, dust-streaked and spotted with rust at its
fixings, light-grey steel windows (in the red variant) and a dark grey
sheet roof. The gutters, downpipes and snow guard are the
catalog's galvanised steel. It is a generic composite and shows no
recognisable real building.

## Category and secondary use

`buildings/industrial/`. The secondary use is the attendant's room in the
lean-to, which is part of the same plant.

## Hero/landmark status

**No.** It uses the ordinary budgets and a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) × height |
| --- | --- |
| Shed walls (lane inside) | 14.00 × 6.375 m, eave underside 7.19 m, ridge 7.82 m |
| Lean-to walls | 9.25 × 3.65 m behind the shed, roof 3.49–4.15 m |
| Tower shaft | 2.625 × 4.125 m from inside the shed's rear wall, 0.375 m proud of the lean-to, to 11.33 m |
| Head house | 4.00 × 4.80 m, 11.33–15.25 m, slab to 15.50 m |
| Conveyor gallery | 2.60 m wide, 12.00 m in plan behind the tower, top 18.77 m at its end; its collar 2.70 m wide, top 18.82 m |
| Trestle | two legs on 1.0 m pad footings, x ±1.0…2.0, 10.0–11.0 m behind the tower |
| Overall bounds (roof overhangs, gallery) | 14.60 × 22.80 × 18.82 m |

The brick is the catalog module (`scripts/brickwork.py`): every plan
length a brick corner turns on is a whole number of half stretchers (the
shed's depth 51, the shaft 21 × 33, the lean-to's rear walls 27 and 26),
and every brick-bound height a whole number of 0.078125 m courses
(Construction, *The brick module*). The depth came to 6.375 m by moving
the rear wall 0.025 m forward, so the bounds and the pivot stayed.

In the build frame the shed spans x −7.0…7.0 and y −3.4…2.975, and the
other parts sit as follows:

- **The lane** runs from x −7.0 to 7.0 between its side walls at y −3.0 and
  2.575.
- **The lean-to** is x −4.5625 to 4.6875, y 2.875 to 6.625. Its front runs
  0.10 m into the shed's rear wall.
- **The shaft** is x −1.3125 to 1.3125, y 2.875 to 7.0.
- **The head house** is x −2.0 to 2.0, y 2.2 to 7.0: about 0.7 m over the
  shaft at the front and both sides (0.675 and 0.6875), flush with its rear
  face.
- **The gallery** is x −1.3 to 1.3 (its collar ±1.35), y 7.0 to 19.0,
  high in the air; its struts meet the shaft's rear face at 8.85 m (axis).
- **The trestle** stands with its centre plane at y 17.5, its footings at
  x ±1.0…2.0, y 17.0–18.0. **Nothing else stands on the ground behind the
  shaft's rear face**, and nothing at all from it to y 17.0 (10.0 m out),
  across the whole width of the bounds.

The pivot is at ground level, centred on the bounding box: build point (0,
7.6, 0). It is taken from `LOD0` and applied to every tier, and every tier
has the same plan extents (the gallery's end face sets the rear one on all
of them).

The facts sidecar's footprint is a single 12-cornered polygon: the shed
rectangle with the lane inside it, the lean-to and the shaft's step. These
stand outside it but inside the bounds:

- the main roof's 0.40 m eaves and 0.30 m rakes;
- the lean-to's 0.30 m eave and rakes;
- the head house's oversail and its slab's 0.15 m overhang, the hoist
  beam and trolley, the gallery, its collar and struts, all 8.68 m up or
  more;
- the downpipes (six on `LOD0`–`LOD2`), whose shoes stop 0.165 m over the
  ground;
- **the trestle, which stands on the ground:** two legs and their pad
  footings (1.0 × 1.0 × 0.25 m) 10.0–11.0 m behind the shaft's rear face,
  at x ±1.0…2.0, on `LOD0`–`LOD2`; on `LOD3` the legs alone, three-sided
  prisms in the 0.30 m square at x ±1.35…1.65, 10.35–10.65 m out, with an
  X of bars between them. Nothing else outside the footprint comes within
  2.5 m of the ground.

## Story height

**One occupied storey on the ground:** the lean-to's two rooms and the
shaft's foot. The lean-to's ceiling is about 3.5–3.9 m. The shed is one
open lane, 5.996 m clear above its floor slab (Construction), and it is not
a storey. The shaft is the elevator's casing and its stair, with landings,
not floors; the head house is one plant floor at 11.33 m, 3.92 m to its slab,
reached by that stair. None of these is a habitable storey, so the 3.0–3.3 m
band does not apply. The head house is not stated as a storey in the
sidecar: it is the elevator's and the belt's machinery floor, visited by a
fitter, not an occupied floor.

## Door leaf height

- **Attendant's door (main entrance): 0.90 × 2.1375 m** steel leaf in a
  0.05 m steel frame, with no transom: an opening of 1.0 × 2.1875 m in the
  brick, 8 half stretchers by 28 courses. The threshold is at ground level
  on the lean-to's east end, build (4.6875, 4.0); its reveal's 0.02 m floor
  slab (Construction) is a floor finish, not a step.
- **Elevator door (service): 0.90 × 2.1375 m**, the same door, at the
  shaft's foot on its rear face, build (0.0625, 7.0). The rear face is 21
  half stretchers and the door 8, so it cannot be centred: it stands a
  sixteenth of a metre east of the shaft's axis. It gives access to the
  elevator's boot room and the tower's stair, and it opens onto the clear
  strip under the gallery (Construction).
- **Loading hatch: 1.20 × 1.20 m** on the head house's east face, sill
  11.60 m (0.27 m over its floor), under the hoist beam. It is a hatch, not
  a door: nothing walks out of it.
- The lane's two mouths have no door leaf and are not doors.

## Window sills

Every brick opening is a whole number of half stretchers wide and courses
tall, its sides on half stretchers and its sill and head on course lines.

- **Shed windows:** three of 2.75 × 1.797 m (22 half stretchers × 23
  courses) on the front wall, centred on x −4.625, 0 and 4.625, sill 4.219
  m, head 6.016 m under the ring beam. They are deliberately high, lighting
  the lane over the trucks; the lane is not an occupied floor.
- **Lean-to:** small windows of 0.875 × 1.172 m (7 × 15), sill 1.016 m,
  head 2.188 m, level with the doors' opening head. There is one on the
  east end beside the door and one in each rear wall.
- **Attendant's window onto the lane:** 0.875 × 1.172 m in the lane's rear
  side wall at x 3.3125, sill 1.328 m, head 2.500 m, at a truck driver's
  eye height (on the lane's own bond, which counts courses from the ground
  and stretchers from the west mouth).
- **Shaft:** windows of the same size. One on its front face, sill 9.688 m,
  clear of the shed's roof and 0.47 m under the head house. Three up its
  east face, one a stair flight 2.50 m (32 courses) apart, sills 4.688,
  7.188 and 9.688 m. The sill over 9.5625 m keeps each window inside one of
  the walls' brick samplings (Texture set).
- **Head house:** two on its front face, one on each side, sill 12.50 m,
  1.17 m over its floor, the same 0.875 × 1.172 m windows (sheet, not
  brick). A 1.00 × 0.60 m louvre sits on its west face at 13.60 m.
- **Gallery:** a row of eight 0.60 × 0.55 m lights each side, one in every
  1.5 m panel of its side girder, 1.30 m over its floor, painted on the
  cladding.

## Eave overhang

- **Main roof:** 0.40 m at the front and rear eaves, 0.30 m at the rakes.
  This is within the 0.3–0.6 m default. The slab is 0.25 m thick. A
  galvanised gutter is painted on both eave fascias, with steel barge
  flashing on the rakes.
- **Lean-to:** 0.30 m at its rear eave (with the gutter) and its rakes.
- **Head house slab:** a flat concrete slab overhanging 0.15 m all round,
  under the default: on a clad box 12 m up a deeper slab read as a cap
  rather than a roof edge. It drains off its edge, with no gutter and so no
  downpipe: a flat 4.3 × 5.1 m deck 15.5 m up sheds little, and what runs
  off its edge falls clear of the cladding on the 0.15 m overhang (the
  runs painted under it, Texture set).
- **Gallery roof:** no gutter either. The gallery's roof is a 2.6 m wide
  sloping sheet; it sheds off both long edges, as an enclosed conveyor's
  does, and its sides carry the dark runs from the top flashing.

The rakes overhang the mouths' wall planes by 0.30 m, with their lowest
point at 7.14 m, 1.12 m above the lintels (Construction).

## Construction

`build.py` builds the shed as one hand-built closed box: four walls to a lid
inside the roof slab, a floor cap, and the lid cut along the ridge. The lane
is then cut out of it with an exact boolean **difference**
(`asset_build.difference`). Everything else is unioned in with Blender's
Exact boolean (`asset_build.union`):

- the lean-to and shaft, one hand-built brick solid;
- the head house, one hand-built clad box with its openings, its floor at
  11.33 m;
- the gable roof slab, the lean-to slab and the head house's slab;
- the conveyor gallery with its end collar (none at `LOD3`), one closed
  solid;
- the trestle bent: at `LOD0`/`LOD1` H-section legs, pad footings, an
  H-section cross-head and its bracing bars; at `LOD2` one portal solid
  with the bracing, on the pad footings; at `LOD3` two plain legs and one
  X of bars, separate closed solids;
- the gallery's two struts: square and unioned at `LOD0`–`LOD2`, separate
  three-sided prisms at `LOD3`;
- at `LOD0`–`LOD2`, the hoist beam and its trolley and two ventilators on
  the gallery's roof;
- at `LOD0`/`LOD1`, two tie beams;
- at `LOD0`–`LOD2`, six downpipes.

### The brick module

The brick is the catalog's (`scripts/brickwork.py`): 0.25 m stretchers on
0.078125 m courses, as the plant hall re-coursed to. `brick_problems()` in
`check_layout()` holds it, as the hall's does:

- every height the brick meets something at is on a course line: the
  plinth 0.625 (8 courses), the band's foot 6.015625 (77) and top 6.5625
  (84), the main eave 7.1875 (92), the lean-to's eave 3.515625 (45), the
  shaft's top under the head house 11.328125 (145), the lane's impact
  wall 1.171875 (15), and every opening's sill and head;
- every opening's sides are on whole or half stretchers in the U its wall
  samples (each wall's `u_off` is itself a half stretcher);
- the bond turns a half stretcher at every brick corner: the shed's four
  above the band (under it the corners are the concrete frame's columns),
  and the lean-to's and the shaft's, the shaft's front corners over the
  lean-to's roof included (`BRICK_CORNERS`). The lean-to's front corners
  are buried in the shed's rear wall.

The concrete frame's columns are not held to it: the brick is infill
between them, cut to the frame as it is laid, so the panels between them
end on cut bricks. The columns' 0.40 m and the frame's x ±2.4 are as they
were.

### The lane as a void cut through the shed

The cutter is one closed solid (`lane_void()`), extended 0.5 m past both
gables:

- through `LOD2`, the mouths' sections through the 0.4 m gables, 6.016 m
  high, and between the gables' inner faces the hall up to its pitched
  ceiling, 0.30 m under the roof's underside (6.94 m at the side walls,
  7.27 m at the apex);
- at `LOD3`, one box at the mouths' section, its ceiling flat at the
  lintels' soffit (`lane_mode()`): no gable inner faces, ceiling slopes or
  soffit steps, and no attendant's window, which is seen only through a
  mouth deep in the lane's side. Past 160 m the lane is a dark void either
  way; the clear height is the same. Its flat ceiling keeps the ceiling
  region's mapping, which on a face with no apex vertex samples the
  region's wall-edge row only, its darkest (a flat dark ceiling);
- at `LOD0`–`LOD2`, a second cutter for the attendant's window recess.

The cutter's faces become the lane's surfaces with the cutter's own UVs:
the side walls, the ceiling, the lintels' soffits and the gables' inner
faces over the lintels. Because the cutter's floor is at 0.02 m, the box
keeps **a 0.02 m floor slab under the lane** whose top is the lane's floor,
carrying the tipping grate. This follows the brief's thin closed slab, not
`hiilisiilo_drive_through`'s floorless lane: that lane has no floor face, and
the grate needed one. The slab's edge shows as 2 cm of plinth concrete
across each mouth. There is no kerb, threshold or ramp.

**Lane, stated for the consumer** (unchanged in plan by the revisions; in
the glTF frame it moved with the pivot, Export):

- it runs along X, the shed's long axis, straight and level, its centre
  line at build y −0.2125;
- it is 5.575 m clear between its side walls (build y −3.0 and 2.575) and
  14.00 m from wall plane to wall plane (x −7.0 and 7.0);
- it is 6.016 m above the ground to the lintels' soffit, the lowest
  geometry over it, which is 5.996 m above the floor slab trucks run on; tie
  beams at 6.20 m, the ceiling at 6.94–7.27 m;
- **it is used one way: in at the west mouth (−X), out at the east (+X).**
  The sidecar states it from the west mouth (Export);
- **stop point:** a truck stops with its centre at the lane's centre,
  build (0, −0.2125), on the floor slab. An 8 m rear-tipping truck then has
  its tail 4 m back toward the entry, over the grate;
- it is see-through on every tier, and nothing stands on the ground beyond
  either mouth's plane (below);
- nothing stands in it: its traffic marks are paint only (below).

**Tipping grate:** 3.0 m along the lane × 4.0 m across it, on the centre
line with its centre 2.5 m west of the lane's centre (build x −4.0…−1.0,
y −2.21…1.79), under the stopped truck's tail. It is painted on the floor
slab: a steel frame, bars across the traffic every 0.15 m, a cross bearer,
and coal in the pit below them. The frame column and tie beam at x −2.4
pass over it, 6.20 m up.

**Traffic paint**, texture only, so the lane reads as a tipping lane from
the catalog view into the east mouth:

- **portal legs:** the shed's four corner columns are the portals' legs.
  Their outer faces (gable and long wall) map to their own atlas strip
  (`PIER`) and carry black and yellow diagonal bands 0.20 m tall from the
  ground to 2.0 m. The bands run on round each leg's corners and onto the
  mouths' jambs (the lane's side walls' first 0.40 m), because their 0.40 m
  period divides the legs' faces;
- **stop mark:** where a stopped truck's front is (build x 4.0, 3 m inside
  the east mouth): a banded post 0.30 m wide to 3.0 m on both side walls,
  which the catalog view sees on the far wall, and a yellow line across the
  floor;
- **tipping height:** a banded line 0.15 m tall at 5.50 m on both side
  walls from x −5.0 to 0.0, over the grate: the highest a raised body may
  go clear of the lintels (6.016 m) and the tie beams (6.20 m);
- **grate border:** a banded border 0.15 m wide round the grate;
- **entry signal:** a steel signal box with a hood over two unlit lenses,
  red over green, on both west jambs at 2.45–3.05 m. Not emissive: it is
  paint, and its state is the consumer's.

The paint takes the lane's dust lighter than the walls and half its
baked fall into the lane, so it still reads in the gloom. A wheel stop or
kerb across the lane was ruled out: the lane stays clear and level.

**Nothing stands beyond a mouth's plane in line with the lane or within 1 m
of it** below the lintels (`check_layout()`):

- the lean-to and its slab end at x −4.86 and 4.99;
- the downpipes stand 0.65–0.75 m inside the mouths' planes, 3.28 m or more
  from the lane's centre line;
- only the main roof's rakes pass the planes, 0.30 m, at 7.14 m and up.

### The tower: shaft, head house and gallery

The tower is a slim brick shaft with a head house on it, so that it reads
as an elevator tower rather than a stair or water tower:

- **Shaft:** 2.625 × 4.125 m of the shed's brick, rising through the
  lean-to to 11.33 m. Its stair's windows climb its east face, one a
  flight; one window on its front face looks over the shed's roof.
- **Head house:** 4.0 × 4.8 m, 11.33–15.25 m, oversailing the shaft by
  about 0.7 m at the front and both sides and flush with its rear face. Pale
  profiled sheet on a steel frame, a flat concrete slab over it, the
  oversail's soffit in the same sheet. Two windows to the front, one each
  side, the louvre on the west, and on the east a loading hatch at its floor
  under a steel hoist beam that runs 1.10 m out at 14.55–14.80 m, a trolley
  block 0.30 × 0.22 × 0.28 m hanging under its outer end.
- **Conveyor gallery:** an enclosed box 2.60 m wide and 2.80 m tall in
  vertical section, its sides pale profiled sheet on a long-span side
  girder: a deep steel bottom chord (0.40 m), a flashing along the top
  chord, a steel post every 1.5 m panel and a small light in every panel,
  all painted. It leaves the head house's rear face (the shaft's rear face
  plane, build y 7.0) with its centre line at 13.00 m and rises **away from
  the building (+Y) at exactly 20°**, **12.000 m in plan** to its end face
  (build y 19.0), whose centre is at 13.0 + 12.0 × tan 20° = **17.3676 m**.
  Its underside is 11.60 m over the ground at the head house and 15.97 m
  at its end. Its roof passes the head house's slab about 3 m out, and
  carries two small steel ventilators at 3.0 and 8.0 m out
  (`LOD0`–`LOD2`), plain vent boxes for the walkway inside, not serviced
  housings (Roofs). It starts 0.30 m inside the head house, so the union
  cuts its mouth.
- **The end and its collar:** the end face is vertical and closed, the
  asset's rear bounds face: nothing of the asset reaches beyond it on any
  tier. A dark painted steel flashing collar (the `strut` patch) runs round
  the gallery's last 0.18 m, 0.05 m proud all round (2.70 × 2.90 m outside),
  its outer end flush with the end face. It is built into the gallery's
  solid: the body's faces stop at the collar's back face, a ring, and the
  collar's faces run on to the end. Inside the collar's ring the end is the
  gallery's dark steel blanking plate in a 0.15 m rim, set back 0.08 m at
  `LOD0`/`LOD1` and flush at `LOD2`. At `LOD3` there is no collar: the
  gallery's own faces run on to the end plane, closed by one flat dark
  face of the gallery's section (`gal_end_mode()` "bare", 8 triangles
  fewer than the flare `LOD3` had). The end plane and the inlet's centre
  stay; the 0.05 m collar is the only thing that goes, and with it the
  tier's top is 0.05 m lower at the end (18.77 m), a quarter of a pixel
  past 160 m.
- **The joint rule:** the plant hall's coal wall is placed on this asset's
  rear bounds plane, with a closed inlet of the gallery's section centred
  at 17.3676 m; the collar covers the joint. If the consumer's 1 cm grid
  leaves the wall a centimetre off the plane, the collar reads as the
  flashing where the gallery meets the wall, with a hairline under it or
  its last centimetre in the wall (Review status). The two stay separate
  models; the hall has no gallery stub.
- **Struts:** two 0.24 m square steel members under the gallery's sides (x
  ±1.0), from the shaft's rear face (axis at 8.85 m) up and out to the
  gallery's floor 4.5 m out (build y 11.5, floor 13.24 m), at about 44° —
  knee braces carrying the first span. Their lowest point is their
  underside at the shaft's face, **8.683 m**, the strip's clear height.
  At `LOD3` each is a three-sided prism in the same square, flat side
  down, stopping 0.01 m off the shaft and under the floor, a separate
  closed solid (`strut_prism()`).
- **Trestle:** one steel bent across the gallery, its centre plane 10.5 m
  out from the shaft's rear face (build y 17.5), 1.5 m short of the end
  face. Two H-section legs 0.30 m square at x ±1.5, just outside the
  gallery's sides (0.05 m clear), their flanges facing along the gallery;
  pad footings 1.0 × 1.0 × 0.25 m, 10.0–11.0 m out, inside the 9.9–11.1 m
  band the brief allows; an H-section cross-head 0.30 m wide under the
  floor, its level bottom at 14.98 m, its sloped top 0.012 m up into the
  floor and standing proud of it beyond the sides as bearing seats; three
  panels of X bracing of 0.10 m square bars, each X's two bars either side
  of the bent's plane so they never touch, with two ties between the panels,
  every bar ending in a leg's web. The legs, footings, head and bars are
  unioned. At `LOD2` the legs and cross-head are one portal solid on the
  same footings, with the same bracing; at `LOD3` two plain three-sided
  legs and one X of 0.22 m three-sided bars over the bracing's whole
  height, the two bars either side of the bent's plane, every piece a
  separate closed solid 0.01 m clear of the others (`tr_x_plain()`). The
  spans are 4.5 m of knee-braced cantilever, 6.0 m to the trestle and 1.5
  m over to the hall's wall.
- **The truck road under it:** nothing stands on the ground between the
  shaft's rear face and the trestle's footings, 10.0 m out (the brief's
  minimum is 9.0 m, for a lane 1.5–4.5 m out). This strip is declared as a
  passage (Export); the elevator door opens onto it.
- **No hanger:** a tie from the head house's roof edge (15.50 m) would have
  to rise to the gallery's top and would push, not hang, so the struts and
  the trestle carry the gallery.

The rear (+Y) is therefore **the side that faces the boiler and turbine
hall's coal side.**

### Entrance floor slab

The attendant's door stands on the ground in a 0.20 m brick reveal that had
no upward face under it (the floor cap faces down), so a consumer's terrain
showed inside, across the door's foot. The reveal is floored with a
concrete slab from the shared `scripts/door_floor.py` (`build_opening()`
calls `door_floor.recess()`; the wall's notch is `door_floor.notch()`):

| Entrance | Sidecar door | Slab, width x depth | Tiers |
| --- | --- | --- | --- |
| the attendant's door | `attendant` | 1.00 x 0.20 m | `LOD0`, `LOD1`, `LOD2` |

- **Top 0.02 m over the ground** (`door_floor.T`), clear of terrain at
  z = 0 and too low to read as a step.
- **A nosing on the wall plane** across the 1.0 m opening in the brick.
  Nothing projects past the wall, so the bounds, the pivot, the footprint
  and the door's threshold in the sidecar are as they were.
- **The reveal starts on the slab's top:** the brick cheeks and the door's
  closing face begin at z 0.02, and the wall's notch carries the nosing's
  top corners, so wall, nosing, slab and cheeks meet on shared vertices.
  Under the nosing the lean-to's floor cap runs straight along the wall
  line instead of round the reveal. The door's artwork keeps its place, so
  the slab covers the bottom 1.3 px of the leaf's foot.
- **Follows the openings' tier mode** (`opening_mode()`): the reveal is cut
  on `LOD0`–`LOD2` and the slab with it; `LOD3` paints the door flat on the
  wall, with no reveal to floor.
- **Its own atlas region** (Texture set).

`floor_for()` gives the door its slab on every tier that cuts its recess.
The elevator's service door, the same 0.20 m reveal on the shaft's rear
face, keeps it on the ground with no floor (Known simplifications).

### Walls, frame and band

- **Regions:** every brick wall is cut into regions by two horizontal splits
  and, below the first, by the frame's 0.40 m columns. The columns stand at
  the shed's corners, at x ±2.4 on the long walls, and as the portals'
  piers. Each region carries its neighbours' breakpoints
  (`fix_tjunctions()`), so walls meet without T-junctions.
- **Column strip:** the columns map onto the atlas's column strip, and the
  brick onto the brick band.
- **The band** at 6.016–6.5625 m (7 courses) runs round the shed as the
  ring beam and is the portals' lintel. It is painted on both strips.
- **Above the band:** walls sample the brick rows 3.75 m lower (and 7.5 m
  lower above 9.5625 m, on the shaft), a whole tone period, so the bond runs
  on (Texture set).
- **Portal legs:** the four corner columns' faces map to the legs' strip
  (`PIER`), the frame's other columns to the column strip.
- **The lean-to and shaft** solid has four rims: the floor, the lean-to's
  two sloping lids either side of the shaft, and the shaft's lid, 0.12 m up
  inside the head house. The shaft's side walls rise from the lean-to's lid,
  so the lean-to's roof slab buries their junction.
- **The head house's walls** are single regions on the cladding (Texture
  set), each opening cut with sheet reveals through `LOD2` and flush at
  `LOD3`, as the brick walls' are.

### Roofs, rainwater goods and roof safety

- **Main roof:** a low gable at 0.12 (6.8°), ridge along X at build y
  −0.2125.
  Its rear eave runs into the shaft's front face.
- **Lean-to roof:** 1:10, falling to the rear, its high end buried in the
  shed's rear wall.
- **Gutters:** painted on the main roof's two eave fascias and the
  lean-to's rear fascia.
- **Downpipes:** six on `LOD0`–`LOD2`, modelled with `scripts/downpipes.py`
  with its default swan-neck and shoe; `LOD3` drops them (Per-tier triangle
  counts):
  - front wall: s 0.7 and 13.3 (x ∓6.3);
  - shed's rear wall, beyond the lean-to: x ±6.3;
  - lean-to's rear walls, 0.25 m in from its corners: x 4.4375 and −4.3125.

  All clear their walls' corners and openings (`downpipes.problems()`).
- **No gutter on the head house's slab or the gallery's roof** (Eave
  overhang): both shed off their edges, so neither has downpipes.
- **Snow guard:** painted near the eave on both main slopes and the
  lean-to.
- **No roof safety kit, by the brief.** Neither the main roof (0.12) nor the
  lean-to (0.10) is steeper than 1:8, and neither carries anything serviced.
  The head house's flat roof carries nothing either: the elevator's head
  and drive and the gallery's tail pulley are inside the head house, which
  is reached by the stair inside the shaft. The brief settles access as
  internal by that stair, so the tower has no wall ladder and cage.
- **The gallery's two roof boxes are plain vents**, not serviced items:
  0.6 m steel ventilator boxes over the walkway inside, with nothing on
  the roof to maintain, as CLAUDE.md's plain vent pipes. The gallery's
  roof (20°, steeper than 1:8) therefore needs no roof ladder or walkway.
- **No handrails:** both doors are at ground level, so there is no entrance
  flight.

### Authored parameters

`facade_atlas.py` holds every shared number:

- the brick module (`COURSE`, `BRICK_L` from `scripts/brickwork.py`, and
  `HALF`), the grids the brick-bound heights and positions keep to;
- the plan (`HX`, `Y_F`, `Y_R`, `WALL_T`), giving the lane `YL0`/`YL1`;
- `FLOOR_T`, `Z_MOUTH`, the band, `Z_BEAM`, `CEIL_DROP` and `IMPACT_Z`;
- the roofs (`Z_EAVE`, `TAN`, `Z_AE`, `TAN_A`);
- the lean-to, shaft and head house (`AX0`, `AX1`, `AY1`, `TX0`, `TX1`,
  `TY1`, `HX0`, `HX1`, `HY0`, `HH_Z0`, `Z_TSLAB`);
- the gallery (`GAL_W`, `GAL_H`, `GAL_ANG`, `GAL_Z0`, `GAL_LEN`, giving its
  end `GAL_Y1` and end centre `GAL_Z1`), its collar (`COLLAR_PROUD`,
  `COLLAR_L`), its struts (`STRUT_FOOT`, `STRUT_OUT`), its trestle (`TR_OUT`,
  `TR_CLEAR`, `TR_PAD_BAND`, the legs', head's, footings' and bracing's
  sizes), the hoist beam and trolley;
- the openings' heights on the head house and shaft (`HH_WIN_Z`,
  `HH_HATCH_Z`, `HH_LOUVRE_Z`, `SHAFT_WIN_Z`, `SHAFT_FRONT_Z`);
- the stop point, the grate and the traffic paint (`STOP_X`, `GRATE_C`,
  `HAZARD_TOP`, `HAZARD_W`, `STOP_LINE_X`, `TIP_Z`, `TIP_X`, `SIGNAL_Z`);
- the splits and shifts, the openings.

`build.py` holds the wall specs, their `u_off` and `BRICK_CORNERS`.
`check_layout()` asserts the following:

- the brick module (`brick_problems()`, *The brick module* above);
- openings clear the corners, columns, splits, the band, both roofs, the
  head house and each other, and the head house's clear its floor and slab;
- the lane is at least 5.0 m wide and 4.6 m clear, with the beams over the
  lintels, and 12–16 m long;
- nothing stands beyond a mouth's plane beside the lane below the lintels;
- nothing but the trestle comes lower than 4.6 m over the strip behind
  the shaft's rear face, and nothing at all stands on the truck road within
  9.0 m of it;
- the gallery's mouth lies inside the head house's rear face, its end face
  12.0 m out with its centre at 17.3676 m, its collar 0.05 m proud and
  0.15–0.20 m long; its struts on the shaft under it, meeting it 4–5 m out,
  their feet between 8 m and 1.5 m under the head house; the trestle's
  footings inside their band, its legs beside the gallery, its cross-head
  across them, the bracing between the legs' flanges, clear of the collar;
  the hoist beam sits between the hatch and the slab, its trolley clear of
  the hatch;
- the attendant's window is inside the attendant's room and clear of the
  frames;
- `door_floor.problems()` finds the attendant door's floor slab region the
  opening's width and the reveal's depth, under a door at grade, and the
  atlas's `check_regions()` keeps that region clear of the others;
- the downpipes are placed correctly;
- the lean-to is not steeper than 1:8;
- every brick wall's brick stays inside the band and inside the clean
  shifted rows.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 1966 | 12,000 | openings recessed with brick or sheet reveals; gallery end plate recessed in its collar; two tie beams; attendant's window recessed; two struts, two roof ventilators, the hoist beam and its trolley; the trestle's H-section legs, pad footings, cross-head and bracing; eight-sided downpipes with swan-necks and shoes |
| `LOD1` | 1726 | 4,000 | downpipes four-sided, bent |
| `LOD2` | 1220 | 1,500 | openings still recessed, the attendant's window too; the gallery's end plate flush; tie beams dropped; the ventilators and the trestle's pad footings kept, its legs and cross-head one portal solid with the bracing; coplanar boolean subdivisions dissolved (UV seams kept); downpipes straight, four-sided |
| `LOD3` | 498 | 500 | openings flush; **downpipes, hoist beam and trolley, ventilators, footings and the trestle's cross-head dropped**; the struts kept as three-sided prisms, the trestle as two three-sided legs and one X of three-sided bars, all separate closed solids; the gallery bare to its end plane (no collar), one flat end face; the lane one box at the mouths' section, without the attendant's window; the lean-to, shaft, head house, gallery box and every other opening's paint kept |

The counts are not padded. The massing is a box with a tunnel, a lean-to, a
shaft, a head house, a gallery box with its collar, a trestle and three
slabs. Everything shallow is texture: the frame's columns, the band, the
bond, the grate, the purlins and rafters, the cladding's ribs, the
gallery's side girder and lights and the lane's traffic paint.

Where the triangles go at `LOD0`:

- the six eight-sided downpipes: about 480 (the 240 that `LOD1` saves is
  their halved sides);
- the trestle: about 440 (two twelve-sided H legs, the cross-head, two
  footings, six X bars and two ties, and the union's cuts where every bar
  ends in a web);
- the head house with its six recessed openings, its slab, the gallery and
  its collar, the struts, the ventilators, the hoist beam and trolley:
  about 350;
- the shed's and shaft's recessed openings with their reveals, and the wall
  triangulation round them: most of the rest;
- the lane's void, its two beams and the attendant's window recess: about
  120;
- the attendant door's floor slab: its nosing and its top, with the wall's
  notch carrying the nosing's corners and the floor cap losing the
  reveal's detour, 6 more on `LOD0` and `LOD1`; on `LOD2`, whose coplanar
  dissolve retriangulates the lean-to's walls, 2 fewer; `LOD3` unchanged.

The 12 m gallery costs the same as the 6.5 m one: its length is texture.
The collar costs 16 triangles (its back ring and four faces).

`LOD2` has the budget to keep what used to go at its switch: the recessed
openings (+about 150 over flush, with the wall triangulation round them),
the two ventilators and the two pad footings with their cuts round the
portal's legs (+about 90); 1220 of 1,500.

`LOD3` sits at its ceiling, so what it keeps of the steel was paid for in
places nothing shows past 160 m:

- the lane as one box at the mouths' section, without the gables' inner
  faces over the lintels, the ceiling's slopes, the soffits' steps and the
  attendant's window deep in the lane's side: about 24 triangles;
- the gallery bare to its end plane, without the collar's flare: 8.

That paid for the struts as two three-sided prisms (16) and one X of two
three-sided bars between the trestle's legs (16), each a separate closed
solid touching nothing, so the union cuts nothing; the legs themselves are
the same two prisms (16). 498 of 500.

## LOD review

**The consumer's switches**, by its screen-size measure at 1080p and a
75° vertical FOV, fall at about 1.8, 4 and 8 times the largest bounds
dimension (22.8 m): **41, 91 and 182 m**. The 2026-11-22 pass reviewed the
tier pairs there (`review/older_audit_2026_11_22/fix_industrial_b2/
hiilenvastaanotto_brick_shed/`: `renders_before/` from the copy in
`before/`, `renders_after/`, before-above-after sheets in `compare/`,
`LOD0` at 20 and 35 m in `compare_lod0/`), with the audit's camera (front
10° up, corner 45° round and 25° up, eye level at 1.7 m, rear), noon, and
the corner at night:

- **41 m (`LOD0`→`LOD1`):** only the downpipes' sides halve; no change.
- **91 m (`LOD1`→`LOD2`):** no longer a pop. `LOD2` keeps the recessed
  openings, the ventilators and the footings; what changes are the tie
  beams (inside the dark lane), the trestle's H legs and cross-head
  becoming one portal, and the downpipes straightening. The 99th
  percentile of the difference fell from 15–25 to 1 in every view.
- **182 m (`LOD2`→`LOD3`):** the trestle keeps one X between its legs and
  the struts stay (before, the bent became two bare posts and the struts
  went); the flush windows take their painted reveals and match `LOD2`'s
  recesses to within 4 levels on average in the front view; the
  ventilators go to their painted tops, which read as two fainter dots;
  the hoist beam, the downpipes, the footings and the collar go. What
  still shows when blinked: the X is lighter than `LOD2`'s three braced
  panels, and the ventilators' dark boxes fade (about 2 px each).
  Pixels differing by more than 24 levels (front / corner / corner night
  / eye / rear): 76 / 218 / 170 / 111 / 28, against 5 / 177 / 0 / 72 / 25
  before; the switch carries more now because `LOD2` keeps what used to go
  at 91 m, where the same count fell from 477 / 518 / 457 / 524 / 60 to
  5 / 3 / 0 / 7 / 0. At night the flush windows light a little more glass
  than the recesses show, and the attendant's lane window goes.

The earlier passes' review, at the catalog defaults (35, 70 and 120 m):

The review camera was perspective, 1920×1080 (LOD pairs at 1280×720), 50°
vertical FOV, with distance along the view to the front or rear bounding
face (`scripts/review_asset.py`). Rendering was Cycles CPU, 16 samples with
denoising, AgX, exposure 0. Pairs compared:

- `LOD0`/`LOD1` at 30/40 m, oblique, noon;
- `LOD1`/`LOD2` at 65/75 m, oblique and rear, noon and reverse sun;
- `LOD2`/`LOD3` at 115/125 m, oblique and end-on (`left`), noon.

Renders are in the local, untracked `review/conveyor_joint_2026_11_21/`:
`before/` from the copy in `before_snapshot/`, `after/`, the before/after
sheets in `compare/` (padded to a common canvas in `compare_in/`, because
the bounds changed), and the end against a stand-in wall in `joint/`. The
earlier pass's mip4 stress renders are in
`review/power_plant_polish_2026_11_21/hiilenvastaanotto_brick_shed/mip4/`.
The latest pass rendered `LOD0`/`LOD1` at 30/40 m, `LOD1`/`LOD2` at 65/75 m
and `LOD2`/`LOD3` at 115/125 m, oblique and rear three-quarter, noon, with
the six views and a 40 m rear three-quarter.

- **The lane is open on every tier.** End-on at 125 m, `LOD2` and `LOD3`
  both show the ground through the portal.
- **Openings** stay recessed through `LOD2` and go flush at `LOD3`, on the
  brick and on the head house alike; `LOD3`'s windows carry the reveals'
  occlusion in paint (`REGION3`). (In the earlier pass,
  `LOD2`'s flush windows read lighter at its switch.) The gallery's end
  plate goes flush at `LOD2`; it stays a dark panel in a pale rim.
- **The lane** is a box at `LOD3`, its ceiling flat at the lintels'
  soffit; seen end-on it is the same dark void.
- **The tie beams** go at `LOD2`. They are seen only from inside the lane
  or end-on through a mouth, a dark bar under a dark ceiling; nothing
  visibly changes at the switch.
- **Massing** is unchanged on every tier: shaft, head house, gallery box,
  lean-to, roofs, portals, columns and band (UV regions).
- **Downpipes, hoist beam and trolley** follow `downpipes.MODES` through
  `LOD2` and vanish at `LOD3` (Per-tier triangle counts): the pipes are
  under half a pixel at 182 m. **The struts** stay on every tier, as
  three-sided prisms at `LOD3`.
- **The trestle** keeps its shape through `LOD2`, on its footings: the
  portal and its X read as the `LOD1` bent did. At `LOD3` the cross-head
  and footings go and one X of thicker bars stands for the three braced
  panels between the two legs; the obstacle's place and height stay.
- **The gallery's end and collar** keep their outline through `LOD2`; the
  end plate goes flush at `LOD2`, and at `LOD3` the collar goes and the
  end is one dark face of the gallery's section. It stands against the
  hall's wall, so the end itself is not seen in the plant.
- **Coal dust and traffic paint** are texture only, the same on every tier.
  The legs' bands stay legible as yellow and black to 75 m and blend to a
  dull ochre at mip4.
- **The attendant door's floor slab (2026-11-23)** adds no transition of
  its own. It goes with the door's 0.20 m reveal at the `LOD2`/`LOD3`
  switch (182 m), where a 0.02 m nosing and 0.20 m of slab are well under a
  pixel. Checked from a standing eye (1.7 m, 75° vertical FOV, 1280 × 720)
  and from 0.35 m over a terrain plane at z = 0, 2–5 m from the door,
  face-on, from both sides and from above, noon and reversed sun, every
  tier (Review status).

Pending in the consumer: real LOD switching, shadows and ambient occlusion
in the lane, and performance.

## Interior geometry

The validator's hidden-surface test reports **8/8/8/0 triangles** on
`LOD0`–`LOD3` (0.4–0.7 %), all of them the gables' inner faces over the
lintels at x ±6.6 and 6.0–7.3 m. These are exterior surface, reachable only
along the 14 m lane, so few of the test's fixed rays escape; they are not
buried. `LOD3`'s box-shaped lane has no such faces.

- The lane's walls, floor, ceiling, soffits and beams are exterior surface,
  open at both mouths.
- The shed's solid parts are the walls, the 0.02 m floor slab and the 0.42
  m over the ceiling. The lean-to, shaft, head house and gallery are solid:
  no interior is modelled.
- The kept closure faces are:
  - the floor caps under the shed, the lean-to and the tower. The
    lean-to's runs straight along the wall line under the attendant door's
    floor slab on `LOD0`–`LOD2`, so the only face at grade in that reveal
    is the cap facing down under the slab, closed by it; the slab is
    exterior surface and adds no face inside the shell;
  - the downpipes' shoe mouths.
- The walls' lids, the lean-to slab's buried end, the shaft's lid inside
  the head house, the gallery's start inside it, the struts', ventilators'
  and hoist beam's buried ends, the legs' feet inside their footings and
  the bracing's ends inside the legs' webs are removed by the union.
- The gallery's end face is exterior surface: it stands against the hall's
  wall in the plant, but the asset is closed on its own. At `LOD3` the two
  plain legs, the X's two bars and the two struts are separate closed
  solids: the legs 8 mm under the floor's height beside the gallery, the
  bars 0.01 m off the legs and 0.005 m either side of the bent's plane, the
  struts 0.01 m off the shaft's face and under the floor. Their caps are
  kept closure faces.

## Known simplifications

- **Lane:** no lighting, weighbridge, wheel guards or sign boards; the
  traffic marks and the entry signal are paint (Construction), the signal
  unlit. The grate and its pit are painted on the 0.02 m floor slab; the
  pit is not modelled.
  The high windows are not shown from inside the lane, where the front wall
  is plain brick.
- **Interiors:** the elevator, its casing, the drive, the attendant's room,
  the stair, the head house's machinery and the gallery's belt are not
  modelled. The windows are closed opaque panes, the loading hatch is a
  closed steel plate and the gallery's end a blanking plate.
- **Gallery:** its lights, side girder (bottom chord, posts) and top
  flashing are painted on its sides; its steel frame is inside the
  cladding. It is the whole conveyor to the hall's wall; the hall's inlet
  belongs to the hall. Its trestle's bracing is solid bars, its bolted
  joints and the footings' anchor bolts are not modelled, and from the side
  the cross-head's end shows as a bare I section.
- **Head house and hoist:** the cladding's ribs, laps and fixings are
  texture; the hoist's trolley is a block, with no hook or chain. There is
  no maintenance balcony.
- **Painted detail:** the frame's columns, the ring beam and lintels, the
  impact wall, purlins and rafters, sheet ribs, the bond, the snow guard,
  the dark coal runs on the gallery and the lane's traffic paint.
- **Floors:** only the attendant door's reveal has one, a flat concrete
  slab with no mat, drain or threshold strip (Construction). The elevator's
  service door's 0.20 m reveal stands on the consumer's ground on
  `LOD0`–`LOD2`, as before.
- **Ground:** the asset has no ground. The coal spilt round the grate and
  at the walls' feet is carried by the floor slab, the lane's walls and the
  walls' plinths.

## Texture set

One 1024² trim-sheet atlas, rasterised by `scripts/atlas.py` at `atlas.SS`
= 4, padded last by `atlas.pad()`. Layout, in rows from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–422 | BRICK (x 0–944), column strip (x 952, 0.40 m) and the portal legs' strip `PIER` (x 984, 0.40 m) | U along the wall, V = height 0–6.5625 m, 64 px/m: plinth to 0.625, the catalog bond (`scripts/brickwork.py`), band 6.016–6.5625; `PIER` adds the traffic bands to 2.0 m |
| 428–547 | `ROOF` (x 4–471), with `GAL_SIDE` (x 480–844, 364 × 106, 30 px/m along it), `GAL_END` (x 852, 83 × 90, 32 px/m) and the hatch (x 943) beside it | ROOF: U = x from the west rake's edge, V up the slope from the eave's edge, both 32 px/m (119 rows over 3.71 m); ridge cap at the main slope's top |
| 555–575 | EAVE, full width | the fascia (0.25 m) with the gutter, U = x at 64 px/m |
| 580–1018 | unique | lane side walls (448 × 246, with the jambs' bands, the stop mark, the tipping height and the entry signal), ceiling (448 × 90) and floor with the grate, its border and the stop line (448 × 178) at 32 px/m; the gallery's roof `GAL_ROOF` (419 × 83, 32 px/m); the head house's cladding `CLAD` (224 × 127, 32 px/m); the windows, door and louvre at 64 px/m; `LOD3`'s two windows with their reveals' occlusion (`REGION3`, 32 px/m); flat patches; the attendant door's floor slab (64 × 14.08 at x 850, y 950) at 64 px/m |

**Deviations from 64 px/m**, each isotropic but `GAL_SIDE`:

- The lane's regions are at 32 px/m. They are in shade and seen
  obliquely; at 64 px/m they would need most of the atlas. Relief there is
  scaled by 32/64 so the normal map's slopes stay physical.
- `ROOF` is 32 × 32 px/m. It was 64 px/m along x and 25 up the slope, a
  full-width band; the roof is seen from above at a distance and its ribs
  (8 px apart) and snow guard read at 32, though at 20 m the ribs and the
  snow guard are visibly softer than they were (`compare_lod0/`). Relief scaled by 32/64. The
  lean-to's slope samples it scaled by 0.81, so 32 × 26 px/m there.
  Measured on the `LOD0` export (`industrial_b/texel_density.py`): every
  up-facing surface 32 × 32 but the lean-to; `CLAD` 32 × 32.
- `CLAD` is 32 × 32 px/m, 7.0 m of U (the walls' offsets overlap in it)
  by 3.96 m, from the head house's floor to just over its slab's soffit.
  It was 64 px/m across U and 21 px/m up V, which stretched its lap, rust
  and runs threefold; the atlas has no room for 7 m × 4 m at 64 px/m, so it
  takes the isotropic 32 px/m the lane's regions have. Its ribs are
  painted at 0.25 m (`paint_sheet(..., pitch=)`), relief scaled by 32/64.
- `GAL_ROOF` is the gallery's roof's own region, 32 × 32 px/m: U down the
  slope's 13.1 m (from 0.30 m inside the head house to the end plane), V
  across its 2.6 m, the ribs running down the slope, end laps every 6 m,
  coal heavier near the head house. The roof sampled `CLAD`, squeezed to
  about 6 px/m along the slope. The two ventilators' tops are painted on
  it under their boxes, for `LOD3`, which drops the boxes.
- `GAL_SIDE` is 30 px/m along the gallery in plan (28 along its slope) and
  38 px/m up its 2.8 m section, so its 12.1 m (from 0.30 m inside the head
  house to the collar) fit one row; its ribs are painted at the head
  house's 0.25 m pitch, its lights 18 × 21 px, its posts 3 px. At 15–30 m
  it reads softer than the head house beside it; from the street it is
  seen 15 m up. On `LOD3` the sides run on 0.18 m to the end plane over
  the same region (1.5 % compressed along).
- `GAL_END` is at 32 px/m: a rim and a dark plate seen end-on high up.
- `REGION3`: the shed's and the small windows again at 32 px/m, with the
  reveal's occlusion round the glass as dark frame (deep under the head,
  narrower at the sides, a lip at the sill), for `LOD3`'s flush windows,
  so the switch from `LOD2`'s recesses does not lighten them; the band is
  not glass, so it neither takes `glazing.rooms()` nor lights at night.

### Walls above the band

The band ends at 6.5625 m. Higher walls (the gables, the long walls'
strip under the eave and the shaft to 11.45 m) sample the brick rows 3.75 m
lower, and the shaft above 9.5625 m 7.5 m lower. Each shift is 48 courses,
the bond's tone period, so bond and tone run on across the split. The
shifted walls sample rows 2.06–5.87 m, which `check_layout()` keeps inside
clean brick: no height-following weather above 1.9 m but a faint tail
(under 0.03 of coal dust at 2.06 m, gone by 2.3 m), no runs below 5.90 m.
This is why the heavy dust on the brick stops at about 2 m rather than
2.5–3 m: dust that followed height to 3 m would show again on the shaft
above 9.5625 m, which samples rows from 2.06 m, as a step at the split.

The lean-to roof samples the roof region scaled by 0.81, so its buried end
stops short of the ridge cap's rows.

### Relief

| Feature | Relief |
| --- | --- |
| Brick face over mortar | 6 mm |
| Band, column arrises | 10 mm, 8 mm |
| Window frames, bars, sash | 35, 22, 40 mm |
| Roof ribs | 30 mm, scaled by 32/64 |
| Gutter roll | 70 mm |
| Snow guard tubes | 45 mm, scaled by 32/64 |
| Grate bars over the coal | 40 mm, scaled by 32/64 |
| Cladding ribs (head house, gallery's roof) | 30 mm, scaled by 32/64 |
| Cladding ribs (gallery's sides) | 30 mm |
| Gallery side girder: bottom chord, its top edge, posts, top flashing | 30, 50, 30, 15 mm |
| Traffic paint | none (flat) |
| Floor slab pores | 0.4 mm |

The bond and ribs read raised in the 30 m noon renders.

### Weathering and coal dust

Weathering follows `scripts/weathering.py`'s moderate level: grime, fade on
painted steel and frames, wash on brick, plinth soil and algae, splash-back,
light efflorescence to 1.4 m, roof dirt toward the eave, and runs under the
band and the gutters.

Coal dust has its own field: `scripts/weathering.py`'s coal field `K`,
laid by `Weather.coal()` and carried by `pad()`, which lerps the weathered
colour toward the atlas's `COAL_DUST` (sRGB 44/43/42, passed as the
`Weather`'s `coal_dust`; clipped at 0.9), adds 0.22 roughness, strips the
metallic and deepens the shade by 0.30 of it. A working plant's dust is
heavy where the coal moves and moderate elsewhere, never neglect. Where it
lies:

- **every wall's foot:** 1.3 at the ground (clipped to 1), falling by 1/e
  every 1.10 m and gone by 1.9 m with a faint tail to 2.3 m, plus 0.45–0.60
  over the plinth, all on rows whose V is height;
- **the concrete frame, band, piers and lintels:** the foot's dust and
  0.40–0.60 above it, in patches;
- **all the brick above:** only a light film, 0.025–0.10 in broad patches
  and runs, nothing that follows height, so each variant's brick reads;
- **the portal legs' traffic paint:** 0.08–0.13, rising to 0.6 at the
  ground, and faded;
- **the lane's walls:** 0.55 everywhere, 0.45 more at the foot, and up to
  0.40 more at the mouths' jambs, so the mouths read as dark voids;
- **the lintels' soffits and the tie beams:** 0.75 and 0.70;
- **the ceiling:** 0.30, rising to 0.65 over the grate;
- **the floor:** heavy round the grate and along the walls, a little lighter
  in the wheel tracks and at the mouths, where rain reaches;
- **the head house's cladding:** 0.15–0.31, more toward its foot, with dark
  runs from under the slab's edge; coal settled on the lap's ledge 2.0 m up
  and run down under it; 0.35–0.50 under the gallery's mouth and streaks
  down the mouth's seal either side; the paint chalked; rust at every
  other rib's fixing on five girts, with short runs under each, along the
  lap and on the foot's drip flashing;
- **the gallery:** 0.20 over its sides, up to 0.30 more near the head house
  where the belt is loaded, up to 0.80 along the bottom chord where the
  belt spills, **dark runs down from the top flashing and from every
  light's sill**, 0.75 on its underside, 0.45 on the struts, the trestle's
  steel and the collar (the `strut` patch);
- **the lane's traffic paint and signal:** 0.12–0.18, more at the foot;
- **the roof:** light, 0.05–0.13;
- **the attendant door's floor slab:** 0.35 plus 0.15 in blotches, over
  `door_floor.weather()`'s trodden-in dirt, so it reads with the coal-dark
  plinth and the door's foot beside it (the same film as the plant's coal
  silo's door slab).

Measured albedo, sRGB band means:

| Surface | `red_brick` | `yellow_brick` | `brown_brick` |
| --- | --- | --- | --- |
| Plinth (0–0.6 m) | 49 | 49 | 49 |
| Brick 0.6–1.9 m | 83/63/57 | 125/113/90 | 65/55/53 |
| Brick 3–5.9 m (the clean upper wall) | 108/80/71 | 169/152/119 | 81/66/64 |
| Band | 111/109/103 | 111/109/103 | 111/109/103 |
| Column strip 2–5 m | 119 | 119 | 119 |
| Portal legs' yellow, 1–2 m | 168/141/74 | 168/141/74 | 168/141/74 |

The attendant door's floor slab measures ~89/87/83 in every variant,
lighter than the plinth beside it (49), as a trodden threshold.

The clean upper wall is within 3 sRGB levels of the plant hall's
(`red_brick` about 110.5/81/72, `brown_brick` about 82.5/67/64.6), so the
two variants read apart here as they do on the hall. In the lane (all
variants alike, `red_brick` figures): side walls ~45 at mid-length; floor
~90 at the mouths. The roof is ~60. The cladding averages ~136, the
gallery's sides ~119. The plant reads as working, not abandoned: the dust darkens and
mattes, with no rust streaks, peeling or growth.

### The entrance floor slab

Painted by `scripts/door_floor.py` (`paint()`, `grain()`, `weather()`), as
the catalog's other entrance slabs are: float-finished cast concrete,
`ID_DOOR_FLOOR` (the lane's own `ID_FLOOR` keeps its pores and dust), sRGB
**(132, 130, 124)** in every variant, roughness **0.88**, nonmetallic;
the coal over it raises the roughness and darkens it as on the plinth.
Occlusion deepens toward the jambs and the door (within 0.08 m), a
slightly paler path is worn toward the leaf, the pores are the concrete's
noise at 5 % shade and 0.4 mm of height, and trodden-in dirt and the coal
above lie over it. The region is 64 × 14.08 px at (850, 950), in the free
block under the louvre: U across the opening's 1.0 m from its left side, V
the nosing's 0.02 m (1.28 px) and then the top from the wall plane to the
door. It bleeds 2 px into its gutter.

Adding it changed only that free block (x 815–970, y 920–988: the region
and the padding round it, which now carries the slab's edges instead of
the louvre's, the door's and the patches'); no texel of any other region
changed. The emission map is the same file.

### Lane occlusion

The lane's walls fall to shade 0.52 and AO 0.44 by 3.5 m in from either
mouth. The ceiling falls to 0.42 and 0.34, the floor to 0.70 and 0.55. All
darken further into their corners. The lane is open at both ends, so this
is symmetric about mid-length, and one side region serves both walls.

### Filtering

Whole-atlas mip4 stress renders (`scripts/review_atlas_mips.py`) of `LOD2`
and `LOD3` at 120 m, oblique, grazing and rear, under noon sun. They showed
no brick/roof/cladding colour leaks and no dark seams; the columns, band,
windows, the pale head house and gallery and the dark lane all hold. The
pale lean-to slopes in the rear view are the noon sun's glint, the same at
full resolution.

The mip reviews below were of the atlas before the 2026-11-22 repack
(Revision log), which moved `GAL_SIDE`, `GAL_END`, `CLAD`, the windows,
door, hatch, louvre and patches and made `ROOF`, `GAL_ROOF` and
`REGION3`. The repack keeps 6 px or more between regions (8 px round
`GAL_SIDE`); the whole-atlas mip review has not been run on it (Review
status, pending).

The earlier mip review rendered each tier at its switch
distance and one level beyond (`LOD1` 70 m at mip 2–3, `LOD2` 120 m at mip
3–4, `LOD3` 250 m at mip 4–5), front and oblique, noon and reverse sun, the
default and one contrasting variant, and again at a per-texel mip level
matched to each tier's own texel density (renders in
`review/phase2_2026_11_21/mips/hiilenvastaanotto_brick_shed/`). No gutter
leak shows at any tier's real distance; the hazard strip is clean on every
tier. Latent, in the stress renders only (the first now gone with the
repack):

- `GAL_SIDE` was 5.2 px above `win_s_b`: the brick surround bled into the
  gallery side's bottom edge at mip 2–3. It now stands 8 px clear of the
  roof sheet and the gallery's end.
- The `PIER` hazard strip (984, 0, 25.6, 420) is 6.4 px from `COL`:
  yellow/black reaches the column strip's edge at mip 3 (45 levels), under
  a pixel at 120 m. Nothing reaches the brick.
- `LANE_FLOOR`'s top is 7.6 px from `CLAD`, a window and the door (it
  was 8.8 px from a window): frame or sheet into the floor's far edge at
  mip 3, inside the dark lane.
- With REPEAT sampling the brick band's bottom rows at y = 0 pick up the
  atlas's top rows at mip 2–3, on the ground line; negligible.

The cheap fixes left are an 8 px gap at the `PIER`/`COL` edge and
starting the brick band a few pixels above y = 0.

### Unique textures

Six 1024² RGB PNGs, about 24 MB uncompressed (4 MiB each in memory without
mips): three albedos, plus one ORM, one normal map and one emission mask
shared by all variants.

## Glazing treatment

The glazing uses `scripts/glazing.py` `rooms()` on the finished albedo, with
the default base. The validator measures sRGB 48 (linear 0.025) in all
three albedos, 0.24–0.27× the trim. Roughness is 0.08
(`glazing.ROUGHNESS`) and metallic 0. It was 65 before the 2026-11-22
repack: `rooms()` seeds each window's room from its box in the atlas, so
moving the window regions drew new, on the whole darker rooms; both are
inside the 45–70 band.

- The shed's windows are steel frames of 7 × 4 lights with a hopper. The
  small windows are 3 × 4 lights. The gallery's eight lights a side are
  2 × 1, painted on its sides.
- Two regions of each size alternate, so neighbouring windows show
  different rooms.
- The steel frames (sRGB 206, 104 or 186 by variant) are lighter than the
  glass.

There is no departure from the Style Direction band.

## Variant list

| Variant | Meaning |
| --- | --- |
| `red_brick` (default) | red facing brick in the plant's shared tone, light grey steel windows, grey-green doors and hatch, dark grey roof |
| `yellow_brick` | yellow facing brick, dark green-grey windows, oxide-red doors |
| `brown_brick` | dark purple-brown clinker brick, light windows, blue-grey doors, darkest roof |

These are the plant's brick trio. The concrete, the coal dust, the pale
cladding of the head house and gallery and the galvanised rainwater steel
are the same in all three. Geometry, UVs, ORM, normal and emission are
shared.

### The plant's red and brown brick

`red_brick` and `brown_brick` are the same constants on all five of the
plant's pieces. `brown_brick` is a dark clinker, brick 80/59/57, darker
brick 62/46/45, mortar 108/106/102 (sRGB): well below the red in value and
redness, so the three variants read apart.

`red_brick` is the tone all five of the plant's pieces share
(`plant_brick()` in `facade_atlas.py`): each brick-face colour of the
original red palette is pulled 40 % toward its Rec. 709 luma per channel,
`Y + 0.6 × (c − Y)`, then multiplied by 0.94; the mortar takes the same
formula and a further 0.90.

| Constant | Original | Plant tone |
| --- | --- | --- |
| `brick` | 144/72/52 | 114/73/62 |
| `brick2` | 114/58/45 | 90/59/51 |
| `mortar` | 150/145/136 | 125/123/118 |

The plain wall's mean albedo at 2–5.9 m, before the coal dust, measures
111/81/72: R − G = 30 sRGB levels. The coal dust laid over the whole band
takes that to 102/75/67 (Texture set); the brown measures 77/63/61 there.

## Night lighting

**Night-lit: it ships `_emission.png`.**

- **Mask:** the window glass only, via `glazing.night_rooms()`. That covers
  the shed's three high windows, the shaft's four, the head house's four,
  the gallery's sixteen lights, the lean-to's three and the attendant's window
  onto the lane (`LOD0`–`LOD2`: `LOD3`'s box lane has no window). `LOD3`'s
  flush windows take their own regions (`REGION3`), whose glass lights and
  whose reveal band does not, so they light about as much glass as the
  recessed windows show on `LOD2`.
- **Not lit:** the doors, the loading hatch, the louvre, the gallery's end,
  the lane itself and the entry signal's lenses (painted, unlit). There are
  no lamps or lit signs.
- **Default state:** `emissiveTexture` is bound on every tier with the factor
  rewritten to zero (`window_emission.rewrite_glb_emission`).
- **Reference lit factor:** industrial lamps, linear (1.0, 0.88, 0.72), as
  the catalog's other works buildings use.
- **Control:** per building. Shared window UVs prevent per-window control.
- **`variants.png`:** day above night for all three colours, from the
  catalog camera with fixed exposure (`scripts/variant_previews.py`).
- **No light spill** was simulated.
- **Pending in the consumer:** off/on on reimport and night intensity.

## Export

```
python3 facade_atlas.py export                       # albedo x3, ORM, normal, emission
blender --background source.blend --python build.py  # meshes, preview, variants, sidecar
```

Run the textures first. A first build from a factory scene is
`blender --background --python build.py`.

Export settings, as `asset_build.Asset.export_all()` passes them:

- `export_format='GLB'`, `use_selection=True`, `export_yup=True`;
- `export_apply=True`, `export_keep_originals=True`;
- `export_cameras=False`, `export_lights=False`.

After export, `strip_embedded_images()` removes the placeholder
`bufferView`s, and the emission factor is rewritten to zero.

**Bindings**, from the one shared material on every tier:

- albedo → `baseColorTexture`;
- ORM G/B → `metallicRoughnessTexture`;
- ORM R → `occlusionTexture`;
- normal → `normalTexture` at scale 1;
- emission → `emissiveTexture`, factor 0.

The validator confirms one material, uri-only images, the normal and
emission bindings and the default-off factor on every tier. The material is
single-sided and opaque. The preview is `LOD0`, `red_brick`, from the
catalog's fixed camera, sun and grey world.

### Facts sidecar

`export/hiilenvastaanotto_brick_shed.model.json`, in the glTF frame (pivot
build (0, 7.6, 0); a build point (x, y, z) is glTF [x, z, −(y − 7.6)]):

- **bounds:** [−7.3, 0, −11.4] to [7.3, 18.8176, 11.4]. The gallery's end
  face sets the rear (glTF z −11.4), the collar's top at the end the top,
  the front eave the front (11.4).
- **footprint:** the shed rectangle with the lane inside it, its mouths
  closed across their wall planes as `hiilisiilo_drive_through` does, plus
  the lean-to and the shaft's step (Footprint): x −7.0…7.0, z 0.6 (the
  shaft's rear face) to 11.0 (the shed's front wall); the shed's rear wall
  at z 4.625, the lean-to x −4.5625…4.6875 to z 0.975, the shaft x
  ±1.3125. The head house and gallery are in the air and the trestle
  stands apart: none is in it.
- **storeys:** one at the ground, 29.74 m². That is the lean-to's rooms
  inside 0.30 m walls (8.65 × 3.35 m) plus the shaft's step (2.025 × 0.375
  m). The lane is not a storey, as for `hiilisiilo_drive_through`, nor is
  the head house (Story height).
- **dwellings:** none.
- **doors:** both 0.90 × 2.1375 m leaves:
  - `attendant`: `entrance`, main, the lean-to's east end, [4.6875, 0,
    3.6], facing +X;
  - `elevator`: `service`, the shaft's rear face, [0.0625, 0, 0.6], facing
    −Z, onto the strip under the gallery.

  The lane's mouths are not doors; the loading hatch is not a door.
- **passages:**
  - `truck_lane`, stated from its entry, the west mouth (glTF −X): it is
    used one way, out at the east. Position [−7.0, 0, 7.8125], the lane's
    centre line on the west gable's outer plane; forward [1, 0, 0]; width
    5.575 m between the side walls; length 14.00 m to the east gable's
    plane, through. Clear height 5.996 m, measured on the exported `LOD0`
    mesh by `measure_lane()`: every triangle clipped to the lane's plan,
    inset 1 mm. The lowest point over the floor is the lintels' soffit at
    6.016 m, above the floor slab's top at 0.020 m. The stop point is the
    lane's centre, [0, 0, 7.8125] (floor 0.02 m), with the grate's centre at
    [−2.5, 0.02, 7.8125] under the tail. The lane's wall planes are glTF z
    5.025 and 10.6, its mouths' planes x −7.0 and 7.0.
  - `under_gallery`: the clear ground behind the shaft, from its rear face
    (glTF z 0.6), the rearmost low thing, to the trestle's near face with
    its footings (z −9.4), across the bounds' whole width. Position [−7.3,
    0, −4.4] on the bounds' −X edge; forward [1, 0, 0]; width 10.00 m;
    length 14.60 m, through. Clear height 8.683 m, measured on the exported
    `LOD0` mesh by `measure_strip()`: the struts' undersides at the shaft's
    face. The gallery's underside is 11.60 m over the ground at the shaft
    and 15.97 m at its end; the struts meet it at glTF z −3.9. Nothing
    lower stands on the strip: the lean-to's eave and downpipes stop at
    glTF z 0.7 and 0.77, in front of it, and the elevator door opens onto
    it. **The trestle beyond it is an obstacle**, not part of the passage:
    centre plane z −9.9, footings x −2.0…−1.0 and 1.0…2.0, z −10.4…−9.4,
    its cross-head 14.98 m up; between its legs (x −1.35…1.35) it is open
    under the cross-head and bracing, but the bracing fills the bent.

## Review status

Checked here, in Blender, after the revision:

- **Validator:** `scripts/validate_asset.py`, 0 FAIL and 0 WARN with the
  sidecar written from a committed tree (`build.py -- facts`); straight
  after a rebuild in a working tree its one WARN is `source.dirty`. Every
  tier passes:
  - welded manifold topology, one material, uri-only images;
  - the normal and emission bindings, the default-off factor;
  - triangle ceilings (`LOD3` 498 of 500), pivot at ground and centred,
    every tier's plan bounds equal to `LOD0`'s;
  - the sidecar's schema, hashes, counts, bounds, doors and both passages;
  - hidden surface 8/8/8/0 (Interior geometry).

  The glazing measures sRGB 48 (Glazing treatment) in all three albedos.
- **Layout:** `check_layout()`, including the brick module
  (`brick_problems()`), the lane's clearances, the ground beyond the
  mouths, the truck road and the clear strip under the gallery, the
  gallery's mouth, length and end centre, the collar, the struts, the
  trestle's footings, legs, head and bracing, and the hoist's trolley.
- **Exported tiers against the sidecar** (a separate reading of every
  `.glb`, `review/older_audit_2026_11_22/fix_industrial_b2/shed_measure.py`):
  every tier has the plan bounds x ±7.3, z ±11.4 and `LOD0`–`LOD2` the
  height 18.8176 (`LOD3`, without the collar, 18.7676). On every tier:
  - the end face is the plane glTF z −11.400; through `LOD2` the collar's
    outline on it x −1.35…1.35, y 15.9176…18.8176 (2.70 × 2.90 m, centre
    17.3676 m), and the collar's back face at z −11.22 with the gallery's
    2.60 m section (x ±1.30) inside it; on `LOD3` the gallery's own section
    on it, centre 17.3676 m (these end figures were measured in the earlier
    pass; the end's geometry through `LOD2` is unchanged by this one);
  - the gallery's side faces' top and bottom edges run from the head
    house's face (z 0.6: 14.400 and 11.600) to the collar's back (z −11.22:
    18.70213 and 15.90213), both at a slope of 0.363970 (tan 20°); extended
    along it to the end plane they give 18.76764 and 15.96764, so a section
    2.8000 m tall with its centre line at **17.36764 m** there, and 13.000 m
    at the shaft's face, 12.000 m from it in plan; its sides are at x ±1.300,
    centred on x 0;
  - the lowest geometry over the lane (inset 1 mm) is the lintels' soffit at
    6.0156 m, 5.996 m over the slab, and nothing stands beyond either
    mouth's plane within 1.0 m of the lane's walls lower than 6.0 m;
  - over the strip z 0.6…−9.4 the lowest geometry is 8.683 m (the struts'
    undersides at the shaft's face, x ±0.88) on `LOD0`–`LOD2` and 8.856 m
    (the prism struts' undersides, 0.01 m off the face) on `LOD3`;
  - behind the shaft nothing touches the ground but the trestle: its
    footings at x ±1.0…2.0, z −10.4…−9.4 on `LOD0`–`LOD2`, its legs at x
    ±1.35…1.65, z −10.05…−9.75 on `LOD3`. Elsewhere outside the footprint
    nothing comes within 2.5 m of the ground but the downpipes' shoes,
    0.165 m up.
- **Six views:** `LOD0` (`review_asset.py --six-views`). The end views show
  straight through the lane; the side views show the gallery's girder
  panels and lights, the struts and the trestle's legs as one line.
- **The end against a stand-in wall** (`review/conveyor_joint_2026_11_21/
  joint/`): `LOD0` and `LOD3` imported from the exported `.glb`, a plain box
  wall with a dark 0.3 m recess of the gallery's section as the hall's
  inlet, its face on the end plane, then 1 cm off it and 1 cm into it, from
  below, from the side (14 m and 5 m) and from above. Flush, the collar
  reads as the flashing where the gallery meets the wall, the same on
  `LOD3` with its flare. 1 cm off, a one-pixel dark hairline shows along
  the collar's edge in the 5 m side view (1280 × 960, 50°) and nothing at
  14 m or from below or above. 1 cm in, the collar's last centimetre is
  lost in the wall with no visible change. (Not repeated for `LOD3`'s bare
  end, which only the far distances show.)
- **LOD pairs:** at the consumer's 41, 91 and 182 m (LOD review), front,
  corner, eye and rear, noon, and corner at night, before and after the
  2026-11-22 pass.
- **Filtering:** mip4 stress renders (`scripts/review_atlas_mips.py`) of
  `LOD2` and `LOD3` at 120 m from the earlier pass, and the mip review of
  the current atlas, the 30 px/m gallery side included (Texture set,
  *Filtering*): every tier at its switch distance and one level beyond,
  whole-atlas and distance-matched per-texel mips. No gutter leak at any
  tier's real distance; latent edges at `GAL_SIDE`, the `PIER` strip,
  `LANE_FLOOR` and the band's y = 0 rows in the stress renders only. That
  review predates the 2026-11-22 repack and was not re-run on it.
- **Before/after:** the review set rendered from the copy taken before the
  revision and again after, compared with `scripts/review_compare.py`.
- **The entrance floor slab** (Construction, Revision log), from a snapshot
  in `review/review_2026_11_23/hiilenvastaanotto_brick_shed/before/`:
  - **Door views** (`review/review_2026_11_23/hiilenvastaanotto_brick_shed/
    door_views.py`, every tier, noon and reversed sun, over a green
    terrain plane at z = 0): the attendant's door from 4.9 m, 2.4 m, both
    sides, 0.35 m up and from above; the elevator door from eye level and
    0.35 m up. Before, grass filled the attendant door's reveal between
    its brick cheeks on `LOD0`–`LOD2`; after, concrete fills it wall to
    wall, mid-grey under its coal, lighter than the plinth, its nosing a
    light line on the wall plane with nothing past it, no dark seam or
    stretched texels. The `LOD3` views and every elevator view are
    unchanged (no pixel over 1/255).
  - **`review_asset.py`** from both: the day cycle on `LOD0`, the six
    orthographic views, and every tier front and oblique at 20, 35, 70 and
    120 m under noon; no pixel changes by more than 24 and at most 30 by
    more than 1/255 (the east side view, at the door). `review_compare.py`
    sheets in `review/review_2026_11_23/hiilenvastaanotto_brick_shed/
    compare/`.
  - The sidecar's bounds, pivot, footprint, storeys, both doors and both
    passages are unchanged; `LOD3` is byte-identical. Measured on the
    exported `LOD0`–`LOD2`, an upward face at 0.020 m under 9 of 9 sample
    points of the reveal, and at grade only the floor cap facing down
    under it; the elevator's reveal has no face, as before.
  - The texture change is confined to the slab's region and the unclaimed
    gutter round it (Texture set); the emission map is unchanged.
  - `scripts/validate_asset.py`: 0 FAIL; the one WARN is `source.dirty`,
    the sidecar written from an uncommitted tree, to be rewritten with
    `build.py -- facts` once committed. Hidden surface 8/8/8/0, as before.
- **Variants:** day and night for all three (`variants.png`).

Pending here: the whole-atlas mip review of the repacked atlas (`ROOF`,
`CLAD`, `GAL_ROOF`, `REGION3` and the moved regions), and the six views
after the 2026-11-22 pass.

Pending in the consumer:

- import, orientation and pivot on reimport in the engine;
- that its trucks fit the lane: 2.6 m wide, against 5.575 m clear and
  5.996 m over the slab, and stop with their tail over the grate;
- that the 0.02 m slab edge across the mouths is acceptable to its driving;
- that the strip under the gallery routes as declared, and the trestle is
  treated as an obstacle beyond it;
- the gallery's end against the hall's coal wall when both are placed
  (the hall's wall face on this asset's rear bounds plane, its inlet's
  centre at 17.3676 m);
- that the painted stop mark and tipping height match its trucks;
- LOD switching (the trestle's bracing going to one X at 182 m), shadows
  and AO in the lane;
- filtering of the 30–32 px/m roof, cladding, gallery and lane regions
  under the consumer's own mip generator and anisotropic filtering, and the
  emission mask's mips at night;
- night intensity;
- performance.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`) throughout.
The MCP addon was not used. Texture generation used the system Python 3
with numpy, scipy and Pillow.

## Revision log

- **2026-11-23 — entrance floor slab.** The attendant's door had no upward
  face in its 0.20 m reveal, so a consumer's terrain showed inside. It now
  stands on a concrete slab 0.02 m over the ground, nosing on the wall
  plane, on its own atlas region, built and painted by the shared
  `scripts/door_floor.py`, on `LOD0`–`LOD2`, where the reveal is cut.
  Tiers 1960/1720/1222/498 to 1966/1726/1220/498; bounds, pivot,
  footprint, doors and both passages unchanged; the emission map
  unchanged. The elevator's service door is left as it was.
- **2026-11-22:** audit fixes. Re-coursed to the catalog brick module as
  the plant hall was (`brick_problems()`): the depth 6.40 → 6.375 m by the
  rear wall (bounds, pivot, gallery and inlet unchanged), the band's foot
  and lintels 6.00 → 6.016 m (lane clear 5.98 → 5.996 m, width 5.60 →
  5.575 m), eave 7.20 → 7.1875 m, lean-to eave 3.50 → 3.516 m, shaft
  2.60 → 2.625 m and its top 11.30 → 11.328 m, lean-to x −4.5…4.7 →
  −4.5625…4.6875 and rear 6.60 → 6.625 m, shed windows 2.80 × 1.75 →
  2.75 × 1.797 m (sill 4.25 → 4.219, x ±4.6 → ±4.625), small windows 0.90
  × 1.20 → 0.875 × 1.172 m (sills 1.00 → 1.016, 1.30 → 1.328, 4.65 / 7.15
  / 9.65 → 4.688 / 7.188 / 9.688), doors 0.95 × 2.10 → 0.90 × 2.1375 m
  leaves, the elevator door 0.0625 m east. `LOD2` keeps its openings'
  recesses, the gallery's ventilators and the trestle's footings; `LOD3`
  keeps the struts and one X of the trestle's bracing as three-sided
  prisms, paid for by a box lane and a bare gallery end, and its flush
  windows and the ventilators' tops are painted (`REGION3`, `GAL_ROOF`).
  The atlas repacked: the roof sheet, the cladding and a new gallery-roof
  region isotropic at 32 px/m. Triangles 1958 / 1718 / 978 / 500 →
  1960 / 1720 / 1222 / 498.
- **2026-11-21:** mip review of the current atlas recorded (Texture set,
  Review status); no asset change.

- **2026-11-21:** the whole conveyor: the plant hall drops its gallery stub,
  so this gallery now runs 12.0 m in plan (end centre 17.3676 m) to an end
  face that is the rear bounds plane, where the hall's coal wall stands,
  with a 0.05 m proud, 0.18 m dark steel flashing collar flush with it; the
  struts moved to 4.5 m out from 8.85 m on the shaft; a braced steel
  trestle bent added 10.5 m out on pad footings (two plain legs at
  `LOD3`), nothing on the ground within 10.0 m of the tower; two roof
  ventilators; the gallery's sides repainted at 30 px/m as a long-span side
  girder with a post and a light in every 1.5 m panel; the pivot moved to
  build y 7.6 and every sidecar coordinate with it; `under_gallery`
  re-derived to the trestle's near face.

- **2026-11-21:** polish: the gallery lengthened to 6.5 m and lowered (mouth
  centre 13.0 m, end centre 15.3658 m, collinear with the hall's stub 1.21
  m off), the head house and shaft lowered 1.0 m with the stair windows
  re-spaced, the struts moved to two-thirds along the gallery from 8.6 m on
  the shaft, a trolley under the hoist beam; the head house weathered
  (chalking, dust on the lap and under the gallery's mouth, rust at the
  fixings and foot); the dust on the brick above 2 m cut to a light film;
  traffic paint on the portal legs and in the lane, and an entry signal;
  the gallery's sides at 54 px/m in a new atlas slot.
- **2026-11-21:** plant palette pass: `brown_brick` set to the plant's
  shared dark purple-brown clinker constants.
- **2026-11-21:** the tower re-proportioned as a slim shaft under a
  sheet-clad head house with a loading hatch and hoist beam; the inclined
  conveyor gallery added off its rear face on two struts, replacing the
  closed outlet hatch; the main roof lowered from 14° to 6.8°; the lane made
  one-way with the grate moved 2.5 m toward the entry and the stop point
  stated; the clear strip under the gallery declared as a second passage;
  much heavier coal dust; `red_brick` moved to the plant's shared tone;
  `LOD3` drops the downpipes, struts and hoist beam.
