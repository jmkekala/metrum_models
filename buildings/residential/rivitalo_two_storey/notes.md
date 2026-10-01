# rivitalo_two_storey

## Style brief

A composite Finnish *rivitalo* — the terraced row that housing companies built
in huge numbers from the late 1960s through the 1980s, and that still fills
suburban streets. Six two-storey dwellings stand side by side in one straight
line under one continuous shallow gable roof. The body is vertical board
cladding over a low concrete plinth, with a horizontal panel seam at the upper
floor and dark casings round plain-glass windows.

Each dwelling has **one** front door, with the type's small stores shed built
on beside it: a stained-board box projecting from the front wall with its own
door, 1.80 m deep. The shed has no roof of its own — it runs up into the
entrance canopy, a single pent slab at the main roof's pitch that covers both
the shed and the door beside it and oversails the shed as a small eave.
Upstairs, each dwelling has two large bedroom windows; the end gables are
blank. Behind the row, each dwelling has a private yard closed by rendered block
screen walls, with a pedestrian gate set off centre in the end wall.

Materials follow the type: painted board cladding, painted trim, a profiled
steel roof, a board-formed concrete plinth, rendered blockwork in the yards
and a timber yard gate. The roof carries the safety kit Finnish rules ask of
it, in the gutter's steel: a ladder up the west gable at the back, a roof
ladder up the rear slope and a walkway along the ridge to the vent housings. Every window is one clear pane inside a thin frame,
with no crossbars and no mullions.

It is meant to be placed as residential filler, many times over, with colour
variety coming from the variants.

## Category and secondary use

`buildings/residential/`. No secondary use.

## Hero/landmark status

**No.** Ordinary budgets, a 1024 atlas. This is a long asset — 36 m — but a
terrace is street filler, not a landmark, so it is held to the ordinary
ceilings. Fitting `LOD3` inside 500 triangles at this length is what drove its
painted-elevation construction; see **Per-tier triangle counts**.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Main block, walls | 36.00 × 8.50 m |
| Six dwellings at | 6.00 m each |
| With the 0.30 m rake overhangs | 36.60 × 8.50 m |
| With the canopies in front (2.05 m; the sheds 1.80 m) | 36.60 × 10.55 m |
| With the back yards' screen walls | 36.60 × 15.13 m |
| Overall, including the gable ladder 0.48 m off the west gable | 36.78 × 15.13 m |

Heights: wall meets soffit at 6.35 m, fascia bottom 6.04 m, ridge 7.51 m, the
ridge vent housings to 8.46 m. The yards' screen walls are 1.90 m.

The pivot is centred on the plan's bounding box, overhangs, sheds and yard
walls included, which is the footprint `scripts/validate_asset.py` checks.
That puts it 1.26 m behind the main block's centre, because the yards reach
4.50 m back and the canopies only 2.05 m forward, and 0.09 m west of it,
because the gable ladder stands 0.18 m outside the west rake. It is taken from `LOD0` and
applied to every tier, and `build_all()` asserts every tier's plan extents
match, so a LOD switch never moves the row.

## Story height

**Ground floor 3.00 m and upper floor 3.00 m**, both inside the 3.0–3.3 m
standard. The floor sits at 0.35 m on the plinth, the upper floor at 3.35 m —
which is also the panel seam that runs round every elevation — and the eave at
6.35 m.

## Door leaf height

**2.10 m** for the front door and for the rear yard door, with no transom or
fanlight; the casing adds 0.19 m above the leaf. Both thresholds sit at the
0.35 m floor level.

Two shorter leaves are deliberate and are not dwelling entrances:

- the **stores shed door, 1.95 m**, in the shed's own boarded front;
- the **yard gate, 1.55 m**, hung 0.08 m clear of the ground in a 1.90 m
  screen wall.

## Window sills

**0.95 m above ground** on the ground floor, which is 0.60 m above the floor:
the type's large living-room window comes low. Upper sills are at **4.20 m**,
0.85 m above the upper floor, and the rear's small bathroom window at
4.75 m. All are well under the ~1.4 m guide, and read correctly against the
2.10 m doors beside them.

## Eave overhang

| Where | Projection |
| --- | --- |
| Main eaves | **0.40 m**, inside the 0.3–0.6 m default |
| Main rakes (gable ends) | 0.30 m |
| Entrance canopy | 2.05 m, a covered entrance rather than an overhang: 0.25 m past the shed's front and 0.15 m past its outer side |

The canopy is ruled a covered entrance, the same case as a portico at a
smaller scale: it shelters the door and the shed together, falls at the main
roof's 0.20 (11.3°) from 2.95 m at the wall to 2.54 m at its edge, and gives
2.29 m of headroom over the landing's edge and 2.40 m over the ground at its
own. Soffits slope with the rafters rather than being
boxed level. Overhangs are kept at every tier.

## Construction

`build.py` builds closed solids and unions them with Blender's Exact boolean:
the main body, the roof slab, one shed and one canopy per dwelling, the
entrance landings and yard-door steps, three ridge vent housings, and the yard
screen walls. Each wall ring rises 0.15 m into the roof slab. The union trims
the walls exactly where the soffits meet them and deletes the buried parts, so
the result is the boundary of one empty volume.

**The vent housings are open stacks**, as CLAUDE.md wants every chimney:
0.90 × 0.60 m sheet-metal boxes standing 0.95 m over the ridge, each a 0.10 m
rim round one flue sunk 0.80 m to a floor, lined and floored in the `flue`
patch (`asset_build.open_stack()`). The floor stays 0.15 m over the ridge, so
the roof slab never reaches into the flue; `check_layout()` asserts it. The
flue stays recessed on both tiers that keep the housings.

Things in the builder worth knowing:

- **The shed has no roof of its own.** Its top is a sloped plane that runs
  0.03 m *into* the canopy slab, so the union makes the two one volume and the
  canopy's soffit is what covers the store door. An earlier pass gave the shed
  a flat roof of its own at 2.45 m, which left a visible gap under the sloping
  canopy that read as a modelling mistake. `check_layout()` now asserts the
  penetration is positive and smaller than the canopy's thickness.
- **The canopy oversails the shed** by 0.25 m in front and 0.15 m on its
  outer side (`CANOPY_EAVE`), so the shed reads as roofed with an eave rather
  than capped flush. The canopy is kept at every tier, so it is what sets the
  plan's front edge; the entrance landing sits inside the shed's projection,
  which is what makes it safe to drop at `LOD3`, and `check_layout()` asserts
  that and the eave.
- **The post-union weld is 1e-4, not the 1e-5 the earlier houses use.** The
  exact boolean resolves this row's 36 m eave lines in 32-bit floats and leaves
  the odd corner vertex a hundredth of a millimetre off its neighbour — enough
  to export as two vertices and fail a downstream manifold check. The smallest
  authored feature here is the gate's 0.06 m casing, so a 0.1 mm weld cannot
  reach anything real. This was found by the validator, not guessed at.
- **The yard gate hangs 0.08 m clear of the ground.** With its foot on the
  wall's own bottom edge the triangulator produced a zero-area triangle with no
  neighbour to flip against, and a gate that stands clear of the ground is
  correct anyway.
- **`tessellate_polygon` emits zero-area triangles** when a region's holes line
  up, as openings sharing head heights do. `_flip_slivers()` repairs each by
  flipping the long edge against its neighbour.
- **`close_solid()` walks and caps the rim itself** in edge-index order rather
  than using bmesh's `holes_fill`, which silently skips a loop whose vertices
  already carry a face, and rather than set order, which iterates by memory
  address and would triangulate differently each run.
- **`Builder.face()` computes its zero-area test in double precision**, from
  coordinates relative to the first vertex. A door has no bottom casing, so its
  casing ring's bottom face has zero area and must be skipped.

`check_layout()` asserts, before building, the constraints that are invisible
in the numbers and obvious once rendered: openings overlapping each other or
running off a wall; openings running under a rake or straddling the storey seam
or the plinth top; the gable outgrowing its atlas band; the roof slope
disagreeing with the atlas; each canopy failing to cover its own door and shed,
or to oversail the shed, or dropping below 2.2 m of headroom over the landing
or the ground;
a shed running into its door casing or into the next dwelling's bay; the shed
door running into the canopy; the yard gate straying into a dividing wall
or towards the middle of the end wall; and a downpipe within 0.25 m of a
corner, with less than 0.2 m of wall between it and an opening, a shed or a
canopy, or within 0.1 m of a landing, a yard step or a dividing wall; the
gable ladder within 0.3 m of the gable's corner or with a bracket in the
rake's soffit; the roof ladder outside the west rake or on a vent housing's
line; and the walkway not just behind the housings or stopping short of the
last one.

### Downpipes

Six downpipes from the shared `scripts/downpipes.py`, unioned in with the
other solids: three to each eave, each draining two dwellings' 12 m of
gutter. On the front each stands 0.15 m past a party line (x = -11.85, 0.15
and 12.15), just clear of a stores shed's canopy; on the rear 0.25 m
past one (x = 11.75, -0.25 and -12.25), inside the next yard beside its
dividing wall.

Each is a 0.1 m pipe standing 3 cm off the boarding, as it would on its
clips, and joined to nothing but the soffit it leaves, so it cuts no line
through the wall's triangles. It rises into the soffit 0.31 m out from the
wall, just inside the fascia the gutter is painted on, falls 0.25 m, steps
back to the wall at 45 degrees, and ends in a shoe kicked 0.15 m out, its
mouth about 0.2 m above the ground. Its sides sample the middle five rows of
the fascia band's gutter (`PIPE_STRIP` in `facade_atlas.py`), so the pipe
takes the gutter's steel in every colour, and the gutter's hangers, a metre
apart, read as its clips. No atlas region was added and no pixel changed.
The tiers are the module's, except that `LOD3` drops the pipes
(`downpipe_mode()`; see LOD review).

### Roof safety kit

From the shared `scripts/roof_safety.py`, as CLAUDE.md asks of a roof
steeper than 1:8 carrying something serviced from it: the 11.3° slopes carry
three ridge vent housings. The kit stands at the back, away from the front
doors:

- **a wall ladder on the west gable**, centred 0.80 m in from its rear
  corner. Neither long wall has a run clear of openings from the ground to the
  eave (the rear bays alternate yard doors and windows over both storeys, the
  front doors, sheds and windows), and the gables are blank, so the ladder
  stands on brackets 0.42 m off the gable, passes 0.12 m outside the rake and
  runs 1 m above the roof edge there, to 7.82 m;
- **a roof ladder up the rear slope**, 0.70 m inside the west gable's plane,
  from 0.25 m up from the eave to just behind the ridge, its rails 8 cm off the
  sheet on brackets that run down into the slab;
- **a level walkway**, 0.30 m wide, along the rear slope with its upslope
  edge 8 cm behind the housings, from the roof ladder's top east past the
  third housing at x = 12.45: 30 m on posts every 1.2 m or less.

Every part samples the gutter's rows (`PIPE_STRIP`), the rows the downpipes
use, so the kit takes the gutter's steel in every colour, as a matched
rainwater and safety system does. The ladders' rungs are 0.28 m apart, 3 cm
square, each one's faces meeting the holes it leaves in the rails, so each
ladder is one closed solid; the walkway's plank and posts are separate solids
the union joins to the roof.

The tiers are the module's thinned to this row's budgets (`kit_modes()`):
every rung with brackets and posts at `LOD0`; every fourth rung and the plank
alone at `LOD1`, whose 500 spare triangles would not take more along a 30 m
walkway; and from `LOD2`, where the housings the walkway serves go, only the
gable ladder's bare rails, three-sided, kept because they stand outside the
rake and so set the row's west extent and its pivot. They touch nothing, so
they join the tier after its weld and dissolve (`roof_safety.append()`):
unioned as one more operand, they changed what those passes merged on the
ground faces, for 8 triangles `LOD3` does not have.


## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 6592 | 12,000 | casing rings, reveals and glass on every window and door on all four elevations; shed doors recessed; yard gates flush; six downpipes, eight-sided with swan-neck and shoe; roof safety kit with every rung, brackets and posts |
| `LOD1` | 3806 | 4,000 | each opening becomes one recess the size of its casing (casing painted on the recessed plane); downpipes four-sided; kit with every fourth rung, no brackets or posts |
| `LOD2` | 1448 | 1,500 | openings flush; coplanar subdivisions dissolved; ridge vents dropped, and the kit with them but for the gable ladder's bare rails; downpipes straight, no swan-neck or shoe |
| `LOD3` | 494 | 500 | front and rear walls painted, not cut (see below); downpipes dropped; the gable ladder's bare rails kept |

**`LOD0` sits far under its ceiling, and that is correct rather than
something to pad.** The row is a 36 × 8.5 m box with one gable roof, six shed boxes and a
set of screen walls. The walls are triangulated as polygons with holes, not as
a grid of cells, so a wall with twelve windows costs about 90 triangles plus
the openings. Every opening on all four elevations is already cut at `LOD0`,
since a terrace is seen from every side, and nothing else here clears the
0.25 m relief test. Everything that would add triangles in this style
(casings, sash frames, the board cladding, the storey seam, gutters, the
block courses in the yards) belongs in the texture.

### How `LOD3` fits 500 triangles

**`LOD3` does not cut its front or rear wall at all.** Each dwelling bay is
one quad mapped to a painted elevation of that bay (`facade_atlas.LOD3_FRONT`
and `LOD3_REAR`, at 14 px/m), and the entrance shed's front is one quad mapped
to a painted elevation of its own. All six bays sample the same region,
because all six dwellings are identical, and the bay boundaries become UV
seams. This is CLAUDE.md's "flatten geometry into suitable shared-atlas
regions": it replaces roughly 250 triangles of wall-with-holes with about 30.
14 px/m is ample here — at the tier's 120 m a 6 m bay is about 58 px on
screen, and the region is 84 px wide.

**What that buys is the thing worth having: every yard dividing wall survives
to the last tier, so the back still reads as six private yards.** An earlier
version dropped five of the seven dividers at `LOD3` and the back became one
long walled strip. That was wrong. Each divider runs into the rear wall, and
while that wall was still being cut for its windows the boolean had to
retriangulate it around every divider, which cost more than the entire house
shell; with the wall painted instead, the dividers are cheap. The canopies
stay at `LOD3` for the same reason.

Three things do still go at `LOD3`, and each is small and checked:

- **the six yard gates.** The six end walls are collinear and abut, so at
  `LOD3` they become one span — geometrically the same wall, with only the
  gates lost. A 1.0 m gate is about 9 px at 120 m.
- **the entrance landings and the yard-door steps.** Both sit inside a
  projection every tier keeps — the sheds in front, the screen walls behind —
  so neither can move the plan's extents, and `check_layout()` asserts that.
- **the shed doors' recess.** At `LOD3` each shed's front is one quad mapped
  to its own painted elevation (`LOD3_SHED`), so its door is painted, not cut.
  The end walls are blank at every tier, and the rear's small windows are
  painted into its bay region.

The ridge vent housings go at `LOD2`, as rooftop clutter should.

Modelled trim (roof-slab overhangs, canopies, shed boxes, vent housings) is a
few hundred triangles at `LOD0`, far under the quarter-budget cap. Opening the
housings' flues cost 16 triangles each, 48 on `LOD0` and `LOD1`, which leaves
`LOD1` 194 under its ceiling.

**The roof safety kit costs 1814, 260, 16 and 16 triangles** on the four
tiers. At `LOD0` most of it is the ladders' 38 rungs with their holes, and
the walkway's 26 posts with the squares they cut in the sheet.

**The six downpipes cost 484, 244 and 90 triangles** on `LOD0`-`LOD2`, the
pipes' own faces and the holes they leave in the soffit together. With the
kit that leaves `LOD2` 52 under its ceiling. `LOD3` drops them: it has 6
triangles to spare, and six three-sided pipes would cost about 70.

## LOD review

Intended switches at the catalog's suggested distances — `LOD0` under 35 m,
`LOD1` 35–70 m, `LOD2` 70–120 m, `LOD3` beyond 120 m — with no overrides. The
projected sizes quoted elsewhere in these notes (a 6 m bay about 58 px at
120 m, a 1.0 m gate about 9 px) use
the catalog's review setup: perspective, 1080p, 50° vertical FOV, distance
measured along the view direction.

Tiers were compared by re-rendering the six pre-export views at `LOD0`,
`LOD1`, `LOD2` and `LOD3`: orthographic front, rear and both ends, a plan from
above, and a raised three-quarter aerial off the front corner. The visible
transitions that survive the comparison are recorded under Known
simplifications — the recessed-to-flat window pop at `LOD1`→`LOD2`, and the
cut-to-painted front and rear at `LOD2`→`LOD3`, whose openings keep their
exact positions and sizes because both sides read the elevation layout from
`facade_atlas.py`.

These are authoring comparisons in Blender. They are not evidence about
runtime switching, mipmap selection or frame time; the consumer-side items are
listed under Review status.

**Downpipes across the switches**, from `review/downpipes_shared_2026_09_25/`
(front, oblique and rear at 35 and 70 m, front and oblique at 120 m, under
noon). At 35 m the eight- and four-sided pipes cannot be told apart. At 70 m
the swan-neck's 0.23 m kick and the shoe, each about two pixels, straighten
into one line, which still reads as a dark line down the boarding. At the 120 m
switch the pipes go: in `LOD2` each is a dark line about a pixel wide at a
party line, and side by side at native size they can be found, but they do not
show at a glance. This is recorded rather than fixed because keeping them would
cost about 70 triangles and the tier has 6 to spare.

**The roof safety kit across the switches**, from
`review/roof_safety_2026_09_25/rivitalo_two_storey/` (every tier; front,
oblique, aerial and rear at 20 and 60 m, under noon; close-ups of the west end
at `LOD0`). At 35 m every fourth rung still reads as a ladder, and the plank
without its 4 cm posts is the same dark line behind the ridge. At 70 m the
walkway and the roof ladder go with the vent housings, and the gable ladder
drops to its bare rails: from the rear and from above the line behind the
ridge can be found missing side by side, not at a glance, and the rails still
stand over the rake as a tick at the west end.

## Interior geometry

Measured with `scripts/validate_asset.py` on the exports:

| Tier | Hidden triangles | Share |
| --- | --- | --- |
| `LOD0` | 66 of 6592 | 1.0 % |
| `LOD1` | 51 of 3806 | 1.3 % |
| `LOD2` | 28 of 1448 | 1.9 % |
| `LOD3` | 8 of 494 | 1.6 % |

The roof ladder's rung undersides, a few centimetres over the sheet, and on
`LOD2` and `LOD3` the backs of the gable ladder's bare rails, facing the
gable, add the new candidates; all are exterior surface seen at a grazing
angle. The vertical remainder, 1.4-5.1 m² a tier, is the downpipes' backs, facing
the boarding 3 cm away: every sampled ray from them heads for the wall and
meets it, though they are exterior surface seen at a grazing angle. The
rest sits where each
yard dividing wall runs into the end wall behind it, which is a real overlap of
two closed solids, and at wall-top/soffit slivers. No wall stands inside the
dwellings, by construction.

## Known simplifications

- **`LOD3`'s front and rear are painted, so their reveals flatten and small
  separations close up.** Openings keep their exact positions and sizes across
  the switch — both files read the elevation layout from `facade_atlas.py`, so
  a window cannot drift between the cut tiers and the painted one — but at
  14 px/m the 0.28 m gap between a front door's casing and the shed beside it
  is under four texels and closes. At the tier's distance that gap is
  sub-pixel on screen anyway. Compare `L2_front`/`L3_front` and
  `L2_rear`/`L3_rear` after any change to the bay layout.
- **Reveals are 0.15 m deep**, shallower than the 0.2–0.4 m masonry reveals the
  0.25 m test was written around, because a boarded timber wall sets its
  windows near the outside face. They are cut anyway: even 0.15 m gives the
  glass a visible shadow line at `LOD0`. The shed door sits 0.08 m back in its
  boarding.
- **Not modelled, and not painted either:** house numbers and entrance
  lights. Both fail the 0.25 m test, and each is placement-specific, so a
  tiling band cannot carry it. Worth revisiting if the row is ever seen
  closer than the 20 m camera floor.
- **The roof safety kit is simplified** (Construction): the gable ladder has
  no safety hoop and its top is straight rails rather than a curved grab rail
  over the rake; the walkway is a plain plank on posts, not a perforated
  grating on raked brackets; there are no snow guards, whose run along the
  eave a tiling band could carry but does not yet.
- **The gutter is painted and the downpipes modelled** (Construction). The
  pipes' clips are the gutter's painted hangers, and each shoe discharges
  onto open ground, with no splash block or gully.
- **Only three ridge vent housings** stand for the row's roof stacks, at the
  second, fourth and sixth bay lines. They are rooftop clutter and are dropped
  at `LOD2`, where they are insignificant.
- **Windows pop from recessed to flat at the `LOD1`→`LOD2` switch**, as
  CLAUDE.md expects.
- **The six dwellings are identical, not mirrored in pairs.** Real rows of this
  type are often built in mirrored pairs, which puts two entrances together
  under one canopy. An earlier pass did that and it read as two front doors
  side by side, which is not what this type does: one door per dwelling, with
  the stores shed beside it. Unmirrored is the clearer read and is what is
  built here.

## Texture set

| File | Space | Notes |
| --- | --- | --- |
| `_albedo_<variant>.png` ×5 | sRGB | 1024², 8-bit RGB, no alpha |
| `_orm.png` | Non-Color | 1024², R = AO, G = roughness, B = metallic |
| `_normal.png` | Non-Color | 1024², OpenGL tangent space (+Y green up), shared across tiers/colours |
| `_emission.png` | sRGB | 1024², neutral glazing mask; shared across tiers/colours |

Eight unique 1024² images in total, one normal map among them.

- **Texel density 64 px/m**, matching the catalog, except the roof band, which
  is stretched up the slope to about 23 px/m. Nothing changes along a profiled
  sheet's slope except the transverse step, so the stretch is on the axis with
  no detail. This is a bigger stretch than the first houses used (41 px/m),
  and it is what bought the row space for the shed strip; it is recorded here
  rather than treated as free.
- **A trim sheet, not one picture per elevation.** A 36 m elevation would need
  2304 px at 64 px/m. Instead the walls sample two tiling cladding bands,
  mapped from world Z so the storey seam lines up all round: S1 for the ground
  storey with its plinth, S2 for the upper storey with the seam board at its
  foot. Each window and door type has a region carrying its casing, sill, drip
  cap, sashes and glass. `build.py` cuts a ring of faces round every opening
  for the casing to land on, so windows stay exactly where they are at every
  tier and none depends on a painted elevation.
- **The cladding is vertical boarding on a 0.5 m pitch.** 1024 px is 32 boards
  exactly, and the per-board tone is hashed by board index, so both the joints
  and the tone repeat exactly at the atlas wrap: a wall whose U crosses the
  wrap sees a board continue rather than change tone with no joint to explain
  it. The 6.0 m dwelling module is a whole number of boards, and the roof's rib
  pitch (0.5 m) and the gutter hangers (1.0 m) also divide 1024. The
  downpipes sample the gutter's middle rows (`PIPE_STRIP`), so they need no
  region of their own.
- **Every wall is at U offset zero**, so board joints line up with the dwelling
  module and with each other where two walls meet at a corner. The 8.50 m depth
  is 17 boards exactly, so the end walls come out whole too.
- **The back yards have their own tiling band** (rendered blockwork with a
  sheet-metal coping), and the **entrance shed has a strip** mapped from each
  face's own along-coordinate and from world z, so the boards stand upright on
  its front and both returns and the plinth line turns the corner unbroken.
- **The flues sample a `flue` patch**, the blank grey darkened to about sRGB
  34 and occluded, as a narrow shaft is whatever the sun does. Painted
  separately from `cap` so the lining reads as soot rather than sheet metal.
- `check_bands()` fails the bake if any tiling band contains a material id it
  should not. Regions are bled 2 px, and `atlas.pad()` then fills every gap, so filtering at
  their edges stays inside
  the artwork.
- **Glass is painted by `scripts/glazing.py`,** the catalog's shared
  treatment, at the catalog base colour. The mid grey (150/156/158) recorded
  here before was already darker than the first houses, and still too pale:
  this row is largely glazed and the openings read as white panels in direct
  sun. It stays neutral and low-saturation, opaque, with the separation
  carried by roughness, and nothing is reflected into the albedo. See Glazing
  treatment below.
- Roughness separates the materials: cladding 0.76, casings 0.56, sashes 0.50,
  glass 0.08, concrete 0.90, roof steel 0.44 with metallic 0.25, render 0.88,
  gate timber 0.72, shed boarding 0.68.
- **The ORM's AO reaches the engine.** The red channel is wired to a
  `glTF Material Output` group's Occlusion input, so the exporter writes an
  `occlusionTexture` pointing at the same PNG as `metallicRoughnessTexture`.
  Blender's own preview ignores AO, so judge renders on albedo.

### Supersampled atlas, normal map and padding

- **Rasterised by `scripts/atlas.py` at 4 x 4 samples per pixel.** `facade_atlas.py` paints in
  final-pixel coordinates and the canvas stores the samples; they are
  box-filtered down in linear light, so an edge at a fractional position lands
  partway across its pixel instead of snapping to it. The emission mask
  carries the same coverage as grey at pane edges.
- **The normal map is derived from a painted height channel** in metres by
  `atlas.normal_map()`, OpenGL convention. The relief is physical, not
  exaggerated, and only covers what the mesh does not model:
  - vertical boarding 15 mm proud of the plinth, slightly crowned, with 6 mm
    V-joints; the storey band and fascia 28 mm;
  - the roof sheet's 30 mm trapezoid ribs and its transverse steps;
  - the gutter as a 70 mm half-round;
  - the yard wall's rendered block courses and its 30 mm coping;
  - casings 20 mm, sills 35 mm, sashes 12 mm proud of the glass;
  - boarded door leaves and gates with raised ledger rails, and the stained
    shed boarding's joints.
  The LOD3 bay elevations are painted at 14 px/m and seen only beyond 120 m, so
  they stay flat.
  Glass stays flat. The roof band is stretched up the slope, so relief that varies up it is
  scaled by the band's px/m over 64 to keep its slope physical.
- **Albedo carries no directional light.** Highlights that faked a fixed sun
  (lit top edges, sunny board or seam faces) were removed; that relief is
  height now and answers the real sun through the normal map. Shade keeps only
  tone, wear and the occlusion that holds whatever the sun does: laps, joints,
  under drips and overhangs.
- **Cavity and weathering come from shared helpers.** `atlas.cavity()` (height
  minus its Gaussian blur) deepens the ORM's AO and darkens the albedo slightly
  in joints and recesses. Tone wear, grain and rain streaks are `atlas.noise()`
  fields, white noise blurred through the FFT, so they tile exactly; they
  replace the sums of sines, whose regular diagonal blotches showed at a
  distance.
- **The gaps are padded.** `atlas.pad()` fills every texel no region claims
  from the nearest region's own edge, in every map, height included, so a mip
  level's wider footprint at a region's edge finds more of that region rather
  than background. The padding itself keeps a flat normal.

### Weathering

- **Placed by `facade_atlas.py`'s `weather()`, drawn by
  `scripts/weathering.py`** at the catalog's moderate level. Its fields
  (dirt, algae, rust, faded paint, rain runs) are amounts, resolved against
  each colour's own palette, so the five variants weather alike. Dirt lerps toward a warm soil colour;
  on steel it is a neutral dust, because soil's brown turned dark roofs
  orange. Dirt roughens the ORM and strips the metallic. Height, the normal
  map and the emission mask are untouched, and glass never weathers.
- **Following height, so it lands the same on every wall:** soil, splash
  specks and a faint green film at the plinth's foot, with runs where the
  boarding's drip edge sheds onto it; splash-back up the boarding's foot; dust
  under the soffit over the top half metre of the upper storey; dust in the
  board joints, from the cavity.
- **The roof band, up the slope from the eave:** long runs, silt along the
  ribs' feet, more dirt toward the eave, a few rust specks on the drip edge,
  and the paint chalking toward the ridge.
- **Elsewhere:** runs down the fascia from the gutter; the yards' rendered
  screen walls soiled at the foot, with runs from the coping; the entrance
  shed's plinth, splashed boarding and runs under its cap; dirt and short
  runs on the sills and head casings, water on the sashes' bottom rails, hand
  grime round the handles of the doors and the yard gate, and dirt at their
  feet. The LOD3 painted bays get the same plinth, splash and eave dust at
  their own 14 px/m, so the switch keeps the look.
- **What a shared band cannot carry:** streaks under one particular window or
  corner.
- The level was chosen on `rintamamiestalo_porch` (see its notes); this
  row takes the same function with its own layout.
- The albedo and ORM PNGs are larger on disk (6 files, 2.5 MB against 2.3 MB before), as the noise
  compresses less; resolution, count and GPU memory are unchanged.

## Glazing treatment

Panes are painted by `scripts/glazing.py`, the catalog's shared treatment.

| | |
| --- | --- |
| base colour | sRGB 50/54/57 (`glazing.BASE`) |
| measured over the glass mask | mean sRGB 51, linear 0.029 |
| relative to the trim around it | 0.23x |
| roughness / metallic | 0.08 / 0 |
| panes in the atlas | 15 |

`albedo()` builds the atlas as before and then hands the glass mask to
`glazing.rooms()`, which gives each pane its own overall level, a falloff
toward the floor, and a lit patch of far wall on about half of them. That is
the room behind the pane rather than a reflection, so it belongs in base
colour; no sill-to-head sky gradient is baked, which Texture Requirements
rule out.

Why it changed: at the previous value the glass measured linear 0.283
and sat at 0.65x the trim around it, so the panes read as glossy
white paint rather than as openings. Seen from outside a window is mostly the
unlit room behind it, and the sky reflection is generated at shading time from
roughness and the dielectric F0 — a pale base colour asks the diffuse lobe to
reflect the sky as well, which double-counts it. The eight-way comparison that
settled the choice lives in `studies/window_glass/`, local only and gitignored.

Limit: the atlas is a trim sheet with 15 glass regions, one per opening
kind, so panes vary between kinds and not between windows — every window of a
kind on this building is identical. Per-window variety would need several pane
regions per kind and `build.py` picking one per instance. This is the same
constraint already recorded for emission.

Pending: calibration in the consumer's lighting.

## Variant list

Five variants, `export/rivitalo_two_storey_albedo_<name>.png`, sharing one ORM
(roughness and metal patterns are identical across them):

| Variant | Walls | Casings | Fascia/seam band | Roof | Front door |
| --- | --- | --- | --- | --- | --- |
| `yellow` (default) | pale ochre | dark red | off-white | dark grey steel | red |
| `green` | sage green | dark green-grey | off-white | dark grey steel | red |
| `white` | off-white | brown | pale grey | brown-grey steel | red |
| `brown` | mid brown | off-white | off-white | near-black steel | dark brown |
| `red` | punamulta red | off-white | off-white | dark grey steel | dark green |

This is the low-rise case in CLAUDE.md: a street of these differs in paint,
and the variants are exactly that. `yellow` is the default because it is the
colour the type is most often seen in, and it is the one the reference
material was read from. Glass, the plinth, the yards' rendered walls and their
timber gates never change; the entrance shed's boarding is a stained tone that
moves with the body colour.

Every `.glb` references the default (`yellow`) albedo. Another variant is the
same mesh with that one file swapped; geometry and UVs are identical by
construction, since the atlas paints ids and shading once and colours them per
variant (`facade_atlas.albedo`).

## Night lighting

`rivitalo_two_storey_emission.png` is a neutral RGB mask of the atlas
generator's glass ownership. Glazing is grey, each pane lit as a room (see Room-lit panes below); cladding, roof, solid doors,
the shed, the yard walls and the gates are black. The front door's light and
the rear yard doors' glazing participate. No interiors or extra geometry were
added.

All four GLBs bind the same external sRGB mask through `emissiveTexture` on
UV0, shared across every colour and tier. Every GLB defaults to
`emissiveFactor = [0, 0, 0]` with the texture binding retained; a reference lit
factor is linear RGB `[1.0, 0.55, 0.23]`. The consumer owns occupancy, time and
fading, and should keep that state per placed building — which matters more for
this asset than for the single houses, since one placement is six households
and a real row is never uniformly lit. Reused glazing UVs mean this is one
building-wide control, not per-dwelling or per-window switching; the PNG
contains candidate windows, not a baked occupancy pattern. **Per-dwelling
lighting would need either separate UV islands per bay or six placed
instances**, and is the obvious thing to revisit once the consumer exists.

`variants.png` shows all five colours at `LOD0` from the catalog camera, with a
day row (emission off) above a matching night row (reference factor on). Camera,
framing, exposure and colour management are fixed between the rows. Cycles
simulates emission spill onto adjacent surfaces in these previews; matching
spill in the game needs its renderer's GI or separate game lights. The assets
contain no exported punctual lights.

### Room-lit panes

Each pane in the emission mask is the lit room behind it, not a flat panel:
`scripts/glazing.py`'s `night_rooms()` multiplies it by its own level, a soft
lamp glow and a falloff toward the floor, and never takes it below about a
fifth. The mask stays neutral grey, so colour, intensity and which buildings
are lit are still the consumer's, and nothing in it says whether a room is
occupied. Averaged over the glass it is 62 % of the old full-white mask
(the catalog runs 52-63 %),
so at the same reference factor the windows read as warm lamplight rather than
pale panels. Every window of one type samples the same atlas region, so every
window of that type carries the same room; see the limit under Glazing
treatment.

## Export

```
python3 facade_atlas.py export                       # textures, all five variants
blender --background source.blend --python build.py  # meshes, preview, variants sheet
```

Textures first, because the UVs index into the atlas and the renders read it.
`facade_atlas.py` is also the single source of the numbers the two scripts
share: `build.py` imports z-levels, opening sizes and region rects from it
rather than repeating them.

Export settings, as `export_all()` passes them: `export_format='GLB'`,
`use_selection=True`, `export_yup=True`, `export_apply=True`,
`export_keep_originals=True`, `export_cameras=False`, `export_lights=False`.
The material has backface culling on, so it exports single-sided.
`scripts/glb_images.py`'s `strip_embedded_images()` then strips the placeholder `bufferView` that
keep-originals leaves beside each `uri` (see `brick_clocktower_hall/notes.md`),
and the validator confirms uri-only images on every tier.

**Preview.** Same camera orientation and lens, sun and flat grey world as the
other assets; only the distance differs, and `_fit_camera()` keeps the line of
sight and moves the camera until the bounding box fills the frame with an 8 %
margin. The flat grey world rather than a studio HDRI is the deviation
`brick_clocktower_hall/notes.md` records, kept so the previews stay comparable;
that choice is still open across the catalog.

The material, the export and the previews are `scripts/asset_build.py`'s,
shared by every asset: `build.py` keeps this building's massing, UVs and
layout checks and hands the rest to one `asset_build.Asset`. The material binds
`_normal.png` through a tangent-space Normal Map node at strength 1, so every
tier carries `normalTexture` at scale 1 beside the base colour, ORM, occlusion
and emission bindings. No tangents are exported; a glTF consumer generates
MikkTSpace tangents when none are given, as Blender's importer does. The export
still writes every tier lit and rewrites its emission factor to zero, and
strips the placeholder `bufferView` keep-originals leaves.

## Review status

**Done in authoring.** All six pre-export views inspected at `LOD0`, and the
same six re-rendered at `LOD1`, `LOD2` and `LOD3` for comparison: orthographic
front, rear and both ends, a plan from above, and a raised three-quarter aerial
off the front corner. Mechanical validation passes with no failures — closed
welded topology on every tier, one material slot, shared ground-level origin
and matching plan extents, external uri-only images, correctly bound ORM
(AO/R, roughness/G, metallic/B) and a default-off emission binding on all four
tiers. Triangle ceilings are met on every tier, with no warnings.

**Texture pipeline change, checked before against after** with
`scripts/review_compare.py`: `LOD0` front and oblique at 20 m and 35 m under
noon, morning and backlight; mip4 stress renders of `LOD2` at 75 m and `LOD3`
grazing at 125 m; and the catalog preview. The boards, laps and seams read as
raised in direct sun, which confirms the OpenGL green channel, and no new colour
leaks appear at mip4. These mip4 renders were made after fixing
`scripts/review_asset.py`: Blender 5.2's glTF importer packs images, and a
packed image ignores `--texture-dir`, so every earlier stress render had shown
the full-resolution textures. The normal map is bound at scale 1 on every tier.

**Weathering, checked before against after** with `scripts/review_compare.py`:
`LOD0` oblique and aerial at 20 m and 35 m under noon and morning sun. The
changes land where `weather()` puts them, and no seam or wrap line shows.
`scripts/validate_asset.py` still reports no failures or warnings. The rebuilt
GLBs are byte-identical to the previous ones.

**Downpipes, checked before against after** with `scripts/review_compare.py`,
the folder snapshotted into
`review/downpipes_shared_2026_09_25/before_snapshot/` first: `LOD0` at 20 m
from all four sides and the oblique; tiers 0-2 at 35 and 70 m from the front,
oblique and rear; tiers 2-3 at 120 m from the front and oblique; all under
noon. Every difference lies on the pipes and their shadows (mean absolute
difference 1.14 / 255 at most in any view). Close-ups of swan-necks and shoes
at `LOD0` and `LOD1`, and of whole pipes at `LOD0` and `LOD2`.
`scripts/validate_asset.py` still reports no failures or warnings.

**Upper windows, blank gables and deeper sheds, checked before against
after**, the folder snapshotted into
`review/rivitalo_upper_window_2026_09_25/before_snapshot/` first: every
tier, front, oblique and aerial at 20 m and 60 m under noon. Each front bay's
upstairs pair of small windows became a second large window, the gables lost
both windows, and the sheds and canopies came forward; nothing else moved.
`scripts/validate_asset.py` still reports no failures or warnings.

**Roof safety kit, checked before against after**, the folder snapshotted
into `review/roof_safety_2026_09_25/rivitalo_two_storey/before_snapshot/`
first: every tier, front, oblique, aerial and rear at 20 m and 60 m under
noon, and close-ups of the west end at `LOD0`. The gable ladder, the roof
ladder and the walkway are the only additions; the west extent grew 0.18 m
and the pivot moved 0.09 m west with it. `scripts/validate_asset.py` still
reports no failures or warnings.

**Pending, and not claimed.** These need the consumer and are recorded as open
rather than assumed:

- switch distances and runtime performance, which no authoring render can
  establish;
- mipmapped and anisotropic appearance at and beyond the switches in the
  consumer: `atlas.pad()` now fills every gutter, but coarse mips can still
  merge regions that touch;
- daylight glass-value calibration in the consumer's lighting, night exposure
  and emission spill;
- the normal map in the consumer: MikkTSpace tangent generation on import and
  its filtering at distance;
- the `LOD2`→`LOD3` switch, where the front and rear change from cut openings
  to painted ones, judged against the consumer's actual switch distance rather
  than the 120 m review assumption.

## Tooling versions

- **Blender 5.2.2 LTS.**
- **Blender Lab "MCP" extension v1.0.3** (`lab_blender_org/mcp`, requires
  Blender ≥ 5.1). Not used for this asset: it was built and rendered in
  background processes.

Recorded as a known-good marker, not a requirement. Blender 5.2 flags
`Material.use_nodes` and `World.use_nodes` as going away in 6.0, so `build.py`
only sets them when a node tree is missing.

- **CPython 3.14.7 with numpy 2.5.3, scipy 1.18.1 and Pillow 12.3.0** for the
  texture export.

## Revision log

- **2026-10-01 — hollow ridge vents.** Each vent housing is now an open
  stack, a rim round a flue sunk 0.80 m to a soot floor, and stands 0.95 m
  over the ridge instead of 0.55 m so the floor clears the roof
  (Construction). A `flue` patch was added to the atlas; triangle counts
  changed from 6540 / 3758 / 1448 / 494 to 6592 / 3806 / 1448 / 494. The
  textures, GLBs, `source.blend`, `preview.png` and `variants.png` were
  regenerated.

- **2026-09-25 — roof safety kit.** A wall ladder on the west gable, a roof
  ladder up the rear slope and a walkway along the ridge to the three vent
  housings, from the new shared `scripts/roof_safety.py` (Construction).
  Triangle counts changed from 4726 / 3498 / 1432 / 478 to
  6540 / 3758 / 1448 / 494. The overall width grew from 36.60 m to 36.78 m and
  the pivot moved 0.09 m west. No atlas pixel changed; the GLBs,
  `source.blend`, `preview.png` and `variants.png` were regenerated.

- **2026-09-25 — upper windows, blank gables, deeper sheds.** Each front
  bay's two small upstairs windows became a second large window at s 4.50,
  so the upper storey runs on an even 3 m rhythm. Both end gables lost their
  windows. The stores sheds went from 0.90 m to 1.80 m deep, and the canopy
  now falls at the main roof's pitch and oversails the shed by 0.25 m in
  front and 0.15 m at the side; the front downpipes moved 0.10 m to clear
  it. Triangle counts changed from 5004 / 3696 / 1478 / 482 to
  4726 / 3498 / 1432 / 478. Every PNG, the GLBs, `source.blend`,
  `preview.png` and `variants.png` were regenerated.

- **2026-09-25 — downpipes.** Six downpipes from the new shared
  `scripts/downpipes.py` (Construction). Three to each eave, at alternate party
  lines; `LOD3` drops them. `facade_atlas.py` gained `GUTTER_PX` and
  `PIPE_STRIP`, which name the gutter rows the pipes sample; no pixel changed
  and the PNGs were not regenerated. Triangle counts rose by 484, 244, 90 and
  0. The GLBs, `source.blend`, `preview.png` and `variants.png` were
  regenerated.

- **2026-09-25 — weathering.** `facade_atlas.py` gained `weather()`, which
  places the shared `scripts/weathering.py` fields: dirt, algae, rust, faded
  paint and rain runs (Texture set, Weathering). Every albedo and the ORM
  changed; the normal map and the emission mask did not. `source.blend`,
  `preview.png` and `variants.png` were regenerated, and the GLBs rebuilt
  byte-identical.

- **2026-09-25 — room-lit night windows.** The emission mask now paints each
  pane as a room (`glazing.night_rooms()`: level, lamp glow, floor falloff)
  instead of full white. Only `_emission.png` and the night row of
  `variants.png` changed; the GLBs, the other maps and `preview.png` were
  regenerated unchanged in content.

- **2026-09-24 — supersampled atlas with a normal map, shared build code.**
  `facade_atlas.py` now paints through the shared `scripts/atlas.py` at
  4 x 4 samples per pixel, with a height channel from which a new
  `_normal.png` is derived; directional highlights left the albedo for the
  normal map, the sine-sum noise became periodic FFT noise, and
  `atlas.pad()` fills the gutters. `build.py` hands its material, export,
  previews and tier bookkeeping to `scripts/asset_build.py`, and binds the
  normal map on every tier. Every PNG, the GLBs, `preview.png` and
  `variants.png` were regenerated.
