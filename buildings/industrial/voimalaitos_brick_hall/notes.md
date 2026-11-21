# voimalaitos_brick_hall

## Style brief

The boiler and turbine hall of a small Nordic town's coal-fired heat and power
plant (*voimalaitos*), as built in the 1950s and 60s: one block of two volumes
in red facing brick infilling an exposed cast concrete frame, on a concrete
plinth, under flat roofs behind a concrete roof-edge beam and parapet. It is a
generic composite of the type, not any one plant.

- **Boiler house**, the west volume (Blender -X): 14 × 17 m and 19.5 m to its
  coping, with a louvred roof monitor. Its three front bays carry the type's
  signature: full-height steel multi-pane hall windows, 12.25 m tall, over a
  lower window or, in the middle bay, the main entrance under a concrete
  canopy.
- **Turbine hall**, the east volume (+X): 18 × 16 m and 11.6 m, abutting the
  boiler house's east face. Its four front bays carry 7.75 m hall windows,
  the east one the machinery door with a shorter window above.
- Smaller windows elsewhere, two hollow roof ventilators on the hall's roof.

The plant is five separate pieces on one lot (this hall, the chimney stack,
the coal reception, the office and control building and the transformer
yard). Nothing joins them in this model: no ground, base, conveyor, pipe
bridge or cable reaches out of this asset. The three sides that face the
other pieces are designed for them (Construction, *Sides facing the other
pieces*).

Downpipes run from both roofs' edge beams, and wall ladders climb to both
flat roofs at the back.

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
| Overall, with the 0.25 m roof edges | 32.50 × 17.50 m |
| Overall, with the entrance canopy (1.25 m) and the flue stub (1.0 m) | 32.50 × 19.25 m |

Heights:

| | Boiler house | Turbine hall |
| --- | --- | --- |
| Plinth top | 0.625 m | 0.625 m |
| Soffit of the roof edge beam | 18.625 m | 10.75 m |
| Deck | 18.875 m | 11.00 m |
| Coping top | 19.50 m | 11.625 m |
| On the roof | monitor to 20.625 m | ventilators to 12.20 m |

The roof monitor's top sets the height of the bounds on every tier. The upper
wall ladder's rails end at 20.50 m, below it.

The pivot is at ground level, centred on the plan's bounding box, which runs
from the canopy's front edge to the flue stub's end. That puts it 0.125 m in
front of the walls' centre line (build frame y = -0.125). It is taken from
`LOD0` and applied to every tier. Every tier keeps the roof edges, the canopy,
the flue stub and the monitor, so the extents never change.

Standing outside the footprint polygon but inside the bounds:

- the roof edge beams (0.25 m all round);
- the entrance canopy (1.25 m, at 3.25–3.5 m);
- the flue stub (1.0 m, at 12.75–14.75 m);
- the four downpipes, 0.03 m off the walls, their shoes kicking out 0.23 m at
  the foot;
- the lower wall ladder, 0.37 m off the turbine hall's rear wall, from the
  ground.

Nothing else stands on the ground outside the footprint: no steps, ramps or
bases.

## Story height

**One storey in each volume, at the ground.** The boiler house rises 18.6 m
from its floor to the soffit, the turbine hall 10.75 m. Both are authored
departures from the 3.0–3.3 m standard, and both are the type's. A boiler
house is one tall volume round the boiler, its galleries open steelwork
inside; a turbine hall is one volume under its overhead crane. Neither has a
built upper floor, so the facts sidecar lists one storey at the ground, the
two halls' floors together, 526 m² inside the outer wall faces (238 m² + 288
m²). The tall windows' transoms every 1.5 m are glazing, not floors.

## Door leaf height

- **Main entrance (boiler house front, middle bay): a pair of framed steel
  leaves, 1.81 × 2.30 m clear.** Each leaf has a tall light. A 0.09 m steel
  transom at 2.30–2.39 m separates them from a four-light fanlight that runs
  to the 3.0 m head. The opening is 2.0 × 3.0 m, under a concrete canopy at
  3.25 m.
- **Machinery door (turbine hall front, east bay): four folding steel
  leaves, 3.31 × 3.91 m clear** in a 3.5 × 4.0 m opening. It is a vehicle
  door, sized for plant, not a leaf at human scale. A wicket door, 0.8 ×
  2.05 m, is painted into the second leaf, and a row of small lights near
  the head is glazing, lit at night.
- **Service door (turbine hall rear, west bay): one steel leaf, 1.00 × 2.10
  m clear**, under a louvred vent panel to 2.28 m, in a 1.19 × 2.375 m
  opening.

All thresholds are at ground level, onto the hall floors, so there are no
steps and no handrails.

## Window sills

Every window is the same steel design: a 0.125 m frame, columns 0.5625 m
wide on mullions, and periods 1.5 m tall on heavy transoms, each of three
pane rows. Twenty-four windows:

| Where | Count | Size (w × h) | Sill | Head |
| --- | --- | --- | --- | --- |
| Boiler house front, hall windows | 3 | 2.5 × 12.25 m | 4.75 m | 17.00 m |
| Boiler house front, under them | 2 | 2.5 × 3.25 m | 0.875 m | 4.125 m |
| Turbine hall front, hall windows | 3 | 2.5 × 7.75 m | 1.75 m | 9.50 m |
| Turbine hall front, over the machinery door | 1 | 2.5 × 4.75 m | 4.75 m | 9.50 m |
| Turbine hall rear | 4 | 2.5 × 4.75 m | 4.75 m | 9.50 m |
| Boiler house rear, upper | 2 | 2.5 × 4.75 m | 9.75 m | 14.50 m |
| Boiler house rear, middle bay | 1 | 2.5 × 4.75 m | 5.50 m | 10.25 m |
| Boiler house rear, ground | 2 | 1.375 × 3.25 m | 1.00 m | 4.25 m |
| Boiler house west | 2 | 2.5 × 4.75 m | 6.00 m | 10.75 m |
| Turbine hall east | 2 | 2.5 × 3.25 m | 5.50 m | 8.75 m |
| Boiler house east, over the hall roof | 2 | 2.5 × 3.25 m | 13.50 m | 16.75 m |

The ground-level sills (0.875–1.75 m) sit below or near the 1.4 m chest line
and well under the 2.3 m entrance leaf, so the doors set the scale. Every
higher window lights a single tall volume, not an occupied floor, which is
the type: the hall windows start at the ground storey and run toward the
roof. Short walls get few, large openings: the west and east ends carry two
windows each, in their outer bays.

## Eave overhang

**None: flat roofs behind a parapet.** Each roof is a cast concrete edge beam
that oversails the walls by **0.25 m** on every side, 0.875 m deep from its
soffit to the coping, with the galvanised coping flashing over its top 0.125
m. That is under the 0.3–0.6 m eave default, and it is a parapet roof's edge,
not an eave: the deck lies 0.625 m below the coping. It is the type's flat
roof. The turbine hall's roof has no parapet on its west side, where it runs
into the boiler house's face.

## Construction

`build.py` builds up to fourteen closed solids and unions them with Blender's
exact boolean (`asset_build.union`):

- **the shell**: both volumes' walls as one closed solid, meshed directly,
  capped by a buried floor and two buried lids;
- **the two roofs**: each an edge beam, coping, parapet and sunk deck in one
  solid. The turbine hall's runs 0.5 m into the boiler house, which hides its
  open west end;
- the roof monitor, the two ventilators (`asset_build.open_stack`), the flue
  stub and the entrance canopy;
- four downpipes (`scripts/downpipes.py`) and two wall ladders
  (`scripts/roof_safety.py`).

The walls run 0.125 m up into the roof slabs. The union trims them and
removes everything inside, so the result is the boundary of one empty
volume. After the union every tier is welded at 0.1 mm. `LOD2`/`LOD3` are
then dissolved with `dissolve_limit` (UV and material seams kept). N-gons are
triangulated by ear clipping with the beauty rule.

### The shell

The plan is an eight-sided outline: the boiler house's 14 × 17 m and the
turbine hall's 18 × 16 m, the boiler house's corners standing 0.5 m proud of
the hall's front and rear. Those two 0.5 m returns are the boiler house's
corner columns. Above the hall's roof the boiler house's east face is its
own wall (`step`).

Each wall is a rectangle less its concrete columns and its openings. The
remaining brick is a grid of cells cut at every column, opening and slab
line. `trace_cells()` traces each slab's cells back into outlines with holes,
so a wall costs a polygon per brick slab, not a quad per cell.

Then `tjunctions()` gives every face every vertex lying on one of its edges:
slab lines on a column's side, window sections on a jamb, the hall's wall
tops on the boiler house's returns. Every shell face is axis-aligned, so this
is an indexed lookup. Faces are triangulated in their planes
(`tessellate_polygon`, with `_flip_slivers()` repairing collinear slivers),
and the rim loops are capped as the floor and the two lids.

### Openings

At `LOD0`/`LOD1` each opening is cut into the wall, with concrete reveals
(sill, head and jambs from the column band, V across the depth) and the
closing plane set back:

| Opening | Set back |
| --- | --- |
| Windows, entrance, service door | 0.25 m |
| Machinery door | 0.30 m |
| Coal hatch | 0.20 m |

Doors have no threshold cheek; the floor cap covers the recess. At `LOD2`
each opening is the same rectangle, flush. At `LOD3` it is painted on the
wall's elevation.

A window's closing plane is made of the window region's sections
(`facade_atlas.window_sections()`), so any window of the one steel design
comes from one painted region:

- in height, the bottom period, alternating middle periods (A with the
  hopper, B without) and the top period;
- in width, the outer columns and the middle ones.

Consecutive sections that are consecutive in the region are one quad. A
12.25 m hall window is three quads, a 2.5 m-wide one is one quad across.
The cuts fall on the centres of transoms and mullions, which are painted the
same on both sides.

### Roof joins

Both roofs are flat: a parapet ring of coping round a deck sunk 0.625 m.

- The turbine hall's deck runs to the boiler house's east face, which the
  union trims it against. Its front and rear edge beams die into the boiler
  house's returns.
- The roof monitor's foot is buried 0.2 m in the boiler house's slab. The
  ventilators' feet are buried in the hall's, with their flue floors 0.3 m
  above the deck.

### Sides facing the other pieces

In the build frame (Blender), with the front toward -Y:

| Side | Blender | glTF | What faces it | What is on the wall |
| --- | --- | --- | --- | --- |
| Rear of the boiler house | +Y | -Z | the chimney stack | the **flue stub**: a 2 × 2 m concrete casing projecting 1.0 m at 12.75–14.75 m in the middle bay, its end closed by a bolted steel blanking plate (sooted, dark). Nothing reaches beyond it. |
| West end of the boiler house | -X | -X | the coal reception | the **coal intake hatch**: a closed pair of heavy steel hatches, 2.5 × 2.0 m, recessed 0.2 m, at 13.0–15.0 m in the middle bay, where the reception's elevator would feed. Opaque, coal-dusted. |
| East end of the turbine hall | +X | +X | the transformer yard | the **cable bushing panel**: flush and painted, 2.5 × 1.25 m at 6.25–7.5 m in the middle bay. It is a concrete panel in a steel frame with three porcelain bushings and cable glands. Otherwise blank brick between two small windows. |

The office and control building faces no designed side: the front (-Y,
glTF +Z) carries the entrance and the machinery door.

### Downpipes

Four downpipes, `scripts/downpipes.py`'s `slab_pipe`, run straight up into
an edge beam's soffit, fed through the parapet. Each stands on a column
between bays, clear of the openings:

| Wall | Pipe at |
| --- | --- |
| Boiler house front | x -6.75 |
| Boiler house rear | x -11.25 |
| Turbine hall front | x 11.25 |
| Turbine hall rear | x 2.25 |

There is no gutter. `PIPE_STRIP` is a galvanised band painted for the
downpipes and the ladders, the coping's steel. The pipes follow
`downpipes.MODES` on every tier. `check_layout()` passes
`downpipes.problems()`.

### Roof safety

Both roofs are flat decks, so CLAUDE.md asks only for a wall ladder up to
each. The monitor and the ventilators stand on level decks. Both ladders
are at the back:

- **Lower wall ladder**: from the ground up the turbine hall's rear wall, on
  the column at x 11.25, 0.37 m out, passing outside the edge beam to 1.0 m
  above the coping (12.625 m).
- **Upper wall ladder**: from the hall's deck up the boiler house's east
  face, in its rear bay (y 5.5), to 1.0 m above its coping (20.5 m). Its
  foot hangs 0.3 m above the deck on its brackets, as such ladders do.

Both use `roof_safety.WallLadder` on a level `Eave` (the edge beam's soffit,
its oversail and the coping). `check_layout()` passes
`roof_safety.problems()`. Tiers: every rung at `LOD0` and every other at
`LOD1`, both with brackets. `LOD2` keeps only the bare rails, appended after
the cleanup (`RS.append`). `LOD3` has no kit (LOD review).

### Authored parameters

Every tier derives from `facade_atlas.py`:

- plan `BH`, `TH`, `COL` 0.5;
- `Z_PLINTH` 0.625, `FASCIA` 0.875, `O` 0.25, `PIN` 0.25, `DECK_DOWN` 0.625;
- `Z_BS` 18.625 and `Z_TS` 10.75;
- `CUTS` and `SLAB` for the brick;
- the window design (`FR`, `CW`, `PER`, `MUL`, `TRAN`, `BAR`);
- `SIZES` and `REVEAL` for the other openings;
- `WALLS`, `COLUMNS`, `ITEMS`;
- `CANOPY`, `FLUE`, `MONITOR`, `VENTS`.

`check_layout()` asserts the openings' clearance from corners, columns, each
other, the soffits and the slab lines, the leaf heights, the pipes and
ladders, and the roof items' places.

## Per-tier triangle counts

| Tier | Triangles | Ceiling |
| --- | --- | --- |
| `LOD0` | 3874 | 12,000 |
| `LOD1` | 3038 | 4,000 |
| `LOD2` | 1288 | 1,500 |
| `LOD3` | 204 | 500 |

Where they go, counted on the solids before the union:

| | `LOD0` | `LOD1` | `LOD2` | `LOD3` |
| --- | --- | --- | --- | --- |
| Shell (walls, columns, openings) | 1184 | 1184 | 960 | 32 |
| Roofs | 56 | 56 | 56 | 24 |
| Monitor, ventilators | 100 | 100 | 100 | 44 |
| Downpipes | 176 | 80 | 48 | 32 |
| Wall ladders | about 2000 | about 1260 | 32 (rails) | 0 |

The union adds the cuts where the pipes, canopy, flue and monitor meet what
they stand on.

The ladders are over half of `LOD0`, and at `LOD1` they are a third of the
ceiling, past the quarter CLAUDE.md suggests for trim. Two ladders of 12.6 m
and 9.2 m make 22 m of rail and about 80 rungs, and they are what roof safety
asks for. They follow `roof_safety.MODES` to 70 m. Past that their rungs are
under half a pixel, so `LOD2` keeps the rails and `LOD3` none.

The building is far larger than the catalog's other brick industrial assets
(`nostokonehuone_brick`, 540 at `LOD0`), but its walls are no denser: one
polygon per brick slab and a few quads per opening. Without the ladders it
would be about 1,900 at `LOD0`, beside the catalog's two-storey terraces.

## LOD review

Review camera: `scripts/review_asset.py`, perspective, 50° vertical FOV,
1920×1080, Cycles at 16 samples, distance along the view direction to the
centre of the facing wall. Views were front, oblique (40° azimuth, 30° up),
aerial (40°, 45°) and rear (150°, 30°).

| Switch | Intended distance | Renders |
| --- | --- | --- |
| `LOD0` → `LOD1` | ~35 m | 30 m and 40 m, `LOD0`/`LOD1`, front and oblique, noon and reverse sun |
| `LOD1` → `LOD2` | ~70 m | 65 m and 75 m, `LOD0`/`LOD1`/`LOD2`, front, oblique and aerial, noon and reverse |
| `LOD2` → `LOD3` | ~120 m | 115 m and 125 m, `LOD0`/`LOD2`/`LOD3`, front, oblique and rear, noon, dusk and night (emission on) |

No distance overrides.

- **35 m.** `LOD1` matches `LOD0`. The ladders' every other rung and the
  pipes' four sides are about a pixel's difference.
- **70 m.** Flattening the openings loses the 0.25 m reveal shadow, about
  2 px. The window steel then reads slightly lighter. The window rhythm, the
  concrete frame, the canopy, the flue stub and the roofline are unchanged
  under both sun directions. The ladders' rungs go; their rails stay as two
  hair lines.
- **120 m.** `LOD3` replaces the walls' geometry with the 6 px/m
  elevations. The columns, plinth, windows and doors are painted on single
  faces. At 120 m a metre is about 9.7 px, so the elevations are slightly
  soft but keep the bays, the light window frames, the dark glass and the
  doors. Each window averages within about 10 sRGB levels of the region
  `LOD2` samples (after two fixes, Texture set, *The LOD3 elevations*). The
  parapets keep the roofline as boxes to the coping. The ladder rails and
  the ventilators go; both are under a pixel or hidden by the parapet from
  the ground. At night the `LOD3` windows are lit at the same mean (linear
  0.20–0.35 per window against 0.24 for the region) but read more even:
  each window is one room, where `LOD2` shows a stack of 1.5 m periods at
  different levels. That difference is visible at the switch when looked
  for, and accepted.

The working renders are in
`review/power_plant_2026_11_21/voimalaitos_brick_hall/` (local, git-ignored).

These are authoring comparisons. Consumer switching, filtering and
performance are pending.

## Interior geometry

The validator's hidden-surface test reports 106 hidden triangles (2.7 %) at
`LOD0`, 63 at `LOD1`, 25 at `LOD2` and 8 at `LOD3`. Its largest candidates
are the downpipes' backs, 0.03 m from the walls they stand off, which the
rays cannot reach. They are exterior surface.

The shell's floor and lids, the roofs' buried west end and soffits inside
the walls, the stubs' buried backs and the pipes' tops are all removed by
the union, so there are no buried partitions or duplicate surfaces. Recessed
glass, doors and the hatch are exterior surfaces.

## Known simplifications

- **Painted, not modelled:**
  - the glazing bars, transoms, mullions and hopper sashes;
  - the entrance's leaves, lights and fanlight;
  - the machinery door's leaves, ribs, lights and wicket door;
  - the service door's vent panel;
  - the hatch's bracing and hinges;
  - the flue's flange and bolts;
  - the bushings and cable glands;
  - the monitor's louvres.
- **Painted on the frame and the roof:** the columns are flush concrete
  strips (their arrises in the normal map), the formwork joints and tie
  plugs, the coping flashing and its lip, the felt laps.
- **Not modelled:**
  - window sills (a concrete reveal face);
  - a lintel over the machinery door (plain brick above it);
  - the plinth step (flush with the brick).
- No boiler, turbine, crane, conveyors, flue duct beyond the stub, pipe
  bridges, cables, ground slab or yard. Each piece of the plant is its own
  asset.
- The ladders have no back guards (cages), though ladders this tall usually
  carry them. A cage is a hoop every 0.9 m, twenty-odd closed solids, beyond
  what the shared kit builds.
- The roof monitor is closed by louvres and the ventilators are capped by
  their sooted flues, so no unmodelled interior shows.

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
| 344–376 | COLUMN | 0.5 m of board-formed concrete across V: columns (U up the column), reveals and heads (V the depth) |
| 384–440 | FASCIA | the roof edge beam, 0.875 m, its coping flashing in the top 8 rows |
| 448–460 | PIPE | galvanised steel; `PIPE_STRIP` is rows 450–458 |
| 470–1020 | unique | see below |

The unique regions:

- the window (2.5 × 6.25 m, four periods);
- the machinery door, the entrance, the service door and the coal hatch;
- the flue's end and the bushing panel;
- a monitor louvre module (2 × 1.75 m);
- the roof deck (8 px/m);
- the five `LOD3` elevations (6 px/m);
- ten flat patches.

`check_regions()` asserts that the regions neither overlap nor run off the
sheet, and that each matches its opening's size. `pad()` fills every
unclaimed texel from the nearest region's edge.

### The brick band and the slab lines

The walls are far taller than the brick band, so above 5.25 m they are cut
at 5.25, 9.25, 13.25 and 17.25 m into 4 m slabs (`CUTS`). Slab *i* samples
the band 4*i* m lower, its rows 1.25–5.25 m.

The bond and tones repeat every 48 courses (courses 1/12 m, 256 rows), and
every noise field repeats every 256 rows (`TILE_Y` = 4). So the band's rows
*r* and *r* + 256 are identical, and the slab lines vanish. Rows above
1.25 m are clean brick: the splash-back and salt bloom stay below.
`check_regions()` asserts the periods and the clearance, and `check_layout()`
keeps every opening's edge 0.1 m off a slab line.

### Texel density

Texel density is 64 px/m everywhere, with these exceptions:

- the roof deck, at 8 px/m, a uniform felt seen only from above;
- the `LOD3` elevations, at 6 px/m: about 1:1.6 at the 120 m switch;
- the flat patches.

### The LOD3 elevations

Each wall's elevation is painted at 6 px/m by the same painters as the
full-size regions (`paint_elevation()`), so the columns, plinth, windows and
doors sit where the mesh has them. Two measures keep their windows the
average colour of the region `LOD2` samples:

- glazing bars, mullions and transoms are never thinner than one sample, or
  at 6 px/m they vanish and the windows go dark;
- the glass is left at `glazing.BASE`, box-filtered with its bars, instead
  of being repainted by `glazing.rooms()`. A pane there is a pixel or two,
  so `rooms()` repainted whole pixels as glass and dropped the bars mixed
  into them, which made the `LOD3` windows 25–40 sRGB levels darker than
  the `LOD2` ones.

### Relief

The normal map is derived from a painted height channel, in metres:

| Feature | Height |
| --- | --- |
| Brick faces over mortar | 0.006 |
| Concrete arrises (columns, reveals) | 0.008 |
| Window frames | 0.035 |
| Transoms and mullions | 0.030 |
| Glazing bars | 0.020 |
| Hopper sash | 0.045 |
| Door frames and stiles | 0.030 |
| Sheet ribs (machinery door, hatch) | 0.006 |
| Coping lip | 0.030 |
| Louvre blades | 0.030 |

Glass is flat.

### Filtering

Atlas mips at levels 3 and 4 were made with `scripts/review_atlas_mips.py`,
and `LOD1`–`LOD3` were rendered at mip 4 (a 64² atlas), oblique and aerial,
at 20 m:

- `LOD1`/`LOD2`: the brick keeps its colour, the columns and edge beam stay
  light concrete, and the windows stay grey panels in their frames. The
  roofs show no brick or concrete leak.
- `LOD3`: the 6 px/m elevations are about 0.4 px/m at mip 4 and smear into
  brown blocks with darker blots, and padding from neighbouring regions
  shows.

That `LOD3` result is a stress case far past the tier's use. At 120 m a
metre is about 9.7 px, so the elevations sample mip 0. At 500 m they reach
about mip 1.3, and only past about 1 km mip 3, where the 8 px gutters are a
pixel. Consumer filtering beyond that is pending.

### Weathering

Weathering is `scripts/weathering.py` at its moderate level, its noise on
the 256-row period:

- grime, and paint fade on the steel;
- rain wash on the brick;
- splash-back and salt bloom on the brick's first metre;
- soil and algae on the plinth;
- patchy dirt on the frame's concrete;
- runs down the edge beam from under the coping;
- dirt on the windows' bottom rail;
- kicked-up dirt and handle grime on the doors;
- coal dust and rust on the hatch;
- soot and rust on the flue's plate;
- soot runs on the louvres;
- dirt on the deck.

Cavity dust settles in the mortar joints. Glass and porcelain stay clean.

## Glazing treatment

Glass is painted with `scripts/glazing.py`: `rooms()` on the finished albedo,
`glazing.BASE` (50, 54, 57). The heavy transoms are wider than its merge, so
each 1.5 m period of a window is its own room. A hall window reads as a
stack of slightly different panels, each with its falloff toward the foot.

The validator measures the glass at sRGB 61–65 (linear 0.043–0.049) across
the variants, at 0.32–0.35× the brightest trim. Roughness is `glazing.ROUGHNESS` (0.08),
metallic 0. All of this is inside the Style Direction band, and the glass is
darker than its steel frames in every variant. There are no brief-driven
departures.

In the `LOD3` elevations the glass is `glazing.BASE` box-filtered with its
bars, not `rooms()` (Texture set, *The LOD3 elevations*). The emission mask
there is still `night_rooms()`.

## Variant list

Large-scale, so a restrained, coherent treatment per instance: three
uniform brick alternatives on the shared mesh. The window steel and the
doors move with the brick. The window steel is always lighter than its
glass. The concrete frame, the coping, the roofs, the pipes and the ladders
are the same in every variant.

| Variant | Meaning |
| --- | --- |
| `red_brick` (default) | red facing brick, off-white window steel, dark green-grey doors |
| `yellow_brick` | yellow facing brick, grey-green window steel, oxide-red doors |
| `brown_brick` | dark brown facing brick, light grey window steel, blue-grey doors |

## Night lighting

- **Mask.** `voimalaitos_brick_hall_emission.png` is the neutral glazing
  mask:
  - every window's panes;
  - the entrance's leaf lights and fanlight;
  - the machinery door's lights;
  - the same in the `LOD3` elevations.

  Each is lit as a room by `glazing.night_rooms()`. Everything else is black,
  and there are no signs or lamps.
- **Bindings.** All four GLBs bind the mask through `emissiveTexture` on UV0,
  with `emissiveFactor` `[0, 0, 0]` by default and the texture kept
  (`scripts/window_emission.py`, via `asset_build.export_all()`).
- **Reference lit factor.** Linear RGB `[1.0, 0.88, 0.72]`: industrial hall
  lamps, the catalog's works value.
- **Control.** One building-wide control. The windows share one region, so
  individual windows cannot be switched. The consumer owns intensity, colour
  and schedule.
- **Preview.** `variants.png` shows all three colours at `LOD0`: a DAY row
  (emission off) above a NIGHT row (reference emission on). Camera, framing
  and exposure are fixed between rows (`scripts/variant_previews.py`, Cycles,
  AgX, exposure 0). Spill onto nearby surfaces is simulated by Cycles in that
  sheet only.
- **Day cycle.** The day cycle (morning, noon, dusk, and night with emission
  on) was rendered on the reimported `LOD0`. The lit pattern was compared
  across `LOD0`/`LOD2`/`LOD3` at 115–125 m at night (LOD review).
- **Pending in the consumer:** material control, night exposure, spill and
  LOD switching at night.

## Export

```
python3 facade_atlas.py export                      # textures, all three variants
blender --background source.blend --python build.py  # meshes, preview, variants, sidecar
blender --background --python build.py -- facts      # the facts sidecar alone
```

Generate the textures first, because the UVs index into the atlas. The first
build ran from an empty scene (`blender --background --python build.py`),
which saves `source.blend`. `facade_atlas.py` is the single source of every
number the two scripts share.

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
- one storey at the ground, 526 m², and zero dwellings;
- three doors:

  | Door | Kind | Main |
  | --- | --- | --- |
  | Entrance (`entrance`), boiler house front, 1.81 × 2.30 m | entrance | yes |
  | Machinery door (`machinery`), turbine hall front, 3.31 × 3.91 m | vehicle | no |
  | Service door (`service`), turbine hall rear, 1.00 × 2.10 m | service | no |

The coal hatch, 13 m up, is not a door.

**Preview.** `preview.png` uses the catalog's fixed camera orientation, lens,
sun and flat grey world (`asset_build.preview_studio()`), with the distance
fitted to the `LOD0` bounds. It shows `LOD0`, the default variant, with the
lights off.

## Review status

Checked here, in Blender:

- `scripts/validate_asset.py`: 0 FAIL.
  - All four tiers have uri-only external images, one opaque material slot,
    welded manifold topology, and hidden-surface candidates only at the
    downpipes' backs.
  - The pivot is at ground level and centred.
  - Every tier binds emission on UV0, default off, and the normal map at
    scale 1.
  - Six 1024² RGB PNGs; normal vectors are unit length and face out.
  - The glass measures in band and darker than the trim.
  - The facts sidecar is consistent.
  - The one warning is `source.dirty` in the sidecar, expected until the
    asset is committed and the sidecar regenerated with `build.py -- facts`.
- `check_layout()` and `check_regions()` pass.
- The six pre-export views at `LOD0` (four orthographic elevations, the top
  view and the raised front three-quarter aerial). Also the aerials off the
  other three corners, and eye views at the entrance, the machinery door,
  the flue stub, the coal hatch and the boiler house's east face over the
  hall roof.
- In those views: window proportions; door scale against the 2.3 m entrance
  leaf; brick coursing scale; no visible slab lines; columns and edge beam
  reading as the concrete frame; glass darker than its frames.
- The tier comparisons at the three switches, the mip 4 stress renders and
  the day cycle, recorded under LOD review and Texture set.
- The variant sheet (`variants.png`): day and night for all three colours.

Pending, and outside this repository:

- Consumer import, MikkTSpace tangent generation and the normal map at
  distance.
- Consumer mip and anisotropic filtering.
- LOD switching, night exposure and spill.
- Runtime performance.
- How this piece sits beside the plant's other four.

## Tooling versions

- **Blender 5.3.0**, headless, which saved `source.blend`. The MCP addon was
  not used for this asset.
- **CPython 3.14.10** with numpy 2.5.5, scipy 1.18.1 and Pillow 13.0.0, for
  the texture export.

These are recorded as known-good markers, not requirements.
