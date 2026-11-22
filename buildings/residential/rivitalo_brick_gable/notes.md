# rivitalo_brick_gable

## Style brief

A composite Finnish *rivitalo* of the brick-and-timber kind that housing
companies built from the late 1960s on: four two-storey dwellings in one
straight line, brick gables closing the ends and a brick pier on every party
line, with stained timber between them. The timber is horizontal lap siding
across the window bands and vertical board-and-batten round the doors, which is
what gives the elevation its vertical rhythm without any modelled trim.

The roof is a shallow **asymmetric** gable. Its ridge sits 2.4 m behind the
street wall, so the short slope drops to the street and the long one runs back
over the yard and cantilevers 2.2 m past the rear wall. That cantilever is the
point of the type: it roofs a recessed balcony on the upper floor and a covered
terrace under it, both carried on galvanised posts.

Street side, per dwelling: the front door recessed 0.30 m into the boarded
panel in the middle of the bay, with one large window each side of it on each
storey — **four windows to the front**.

Yard side, per dwelling: the balcony behind a solid boarded parapet, glazed
along its whole back wall; below it the covered terrace, with a large window in
its back wall and, beside that window, an alcove whose **side wall — at a right
angle to the wall the window is in** — carries the glazed door into the house.
Behind that, a private yard closed by a boarded fence with a gate.

The roof carries the safety kit Finnish rules ask of it, in the gutter's
steel: a ladder up the west gable at the back, a roof ladder up the long yard
slope and a walkway along it behind the ridge to the vents.

It is meant to be placed as residential filler, many times over, with colour
variety coming from the variants.

## Category and secondary use

`buildings/residential/`. No secondary use.

This is the catalog's second terrace, and deliberately not a repeat of
`rivitalo_two_storey`. That one is the painted-board type: six dwellings, 36 m,
a symmetric 11° gable, vertical boarding over a concrete plinth, a stores shed
and canopy at each entrance, and rendered block screen walls round the yards.
This one is the brick-and-timber type: four dwellings, 30 m, an asymmetric
gable, brick gables and piers, recessed balconies over a posted terrace, and
timber fences. They share no geometry, no atlas and no palette.

## Hero/landmark status

**No.** Ordinary budgets, a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Main block, walls | 30.00 × 8.00 m |
| Four dwellings at | 7.50 m each |
| With the 0.60 m rake overhangs and the roof front to back | 31.20 × 10.80 m |
| With the back yards' fences | 31.20 × 15.44 m |
| Overall, including the gable ladder 0.78 m off the west gable | 31.38 × 15.44 m |

Heights: plinth top (ground floor) 0.31 m, upper floor 3.44 m, balcony deck
3.50 m, balcony parapet 4.54 m, street soffit 6.56 m, yard soffit 6.46 m, roof
ridge 7.90 m, ridge vents to 8.85 m.

7.50 m per dwelling is wide for the type, and it is what the brief's four front
windows plus a centred door need: a 2.2 m window casing each side of a 1.8 m
boarded door panel, with a 0.6 m brick pier on each party line.

The pivot is centred on the plan's bounding box, overhangs and yard fences
included, which is the footprint `scripts/validate_asset.py` checks. That puts
it 3.12 m behind the main block's centre, because the yards reach 10.84 m back
and the roof only 4.60 m forward, and 0.09 m west of it, because the gable
ladder stands 0.18 m outside the west rake. It is taken from `LOD0` and applied to every
tier, and `build_all()` asserts every tier's plan extents match, so a LOD
switch never moves the row.

## Story height

**Ground floor 3.125 m**, floor to floor, inside the 3.0–3.3 m standard.

The upper storey runs from the 3.4375 m floor to the soffit, and under a
single-pitch roof that is not one number: **3.125 m at the street wall and
3.021 m at the yard wall**. Both are inside the standard. The taper is the
type's own — the roof falls 0.10 m across the 8 m depth on this side of the
ridge — and it is why the rear wall's top is recorded separately as
`facade_atlas.BAY_H_REAR`, which `check_layout()` asserts against the roof.

Every storey line is a whole number of cladding units: 3.125 m is 40 brick
courses of 0.078125 m and 25 lap boards of 0.125 m exactly. That is what lets
the brick and the siding hand over from one storey's atlas run to the next
without a part course; see **Texture set**.

## Door leaf height

**2.10 m** for all three door types — the front door, the balcony door and the
yard door in the alcove — with no transom or fanlight. The front door's casing
adds 0.20 m above the leaf, the glazed doors' 0.15 m. Every threshold sits at
the 0.3125 m floor level.

There is no shorter leaf anywhere on this asset: the yard gate is a fence leaf,
not a door, and is recorded under **Variant list** and **Construction**.

## Window sills

**0.90 m above ground** on the ground floor, which is 0.59 m above the floor,
and **4.30 m** on the upper floor, 0.86 m above its floor. Both are well under
the ~1.4 m guide and read correctly against the 2.10 m doors beside them.

The balcony's parapet stands 1.04 m above the deck, so from the yard it hides
the bottom 0.24 m of the upper windows. That is what a real recessed balcony
does and is not a sill-height problem; the glazing still reads as a continuous
band under the soffit.

## Eave overhang

| Where | Projection |
| --- | --- |
| Street eave | **0.60 m**, at the top of the 0.3–0.6 m default |
| Rakes (gable ends) | **0.60 m** |
| Yard side | **2.20 m** past the rear wall |

The 2.20 m yard cantilever is ruled a covered space rather than an overhang —
the same case as a portico, at the scale of a whole elevation. It roofs the
balcony and the terrace under it and is carried on eight posts at its outer
edge; without it neither would be weatherproof and the type would not read.
Soffits are boarded and slope with the rafters rather than being boxed level.
All three are kept at every tier.

## Construction

`build.py` builds closed solids and unions them with Blender's Exact boolean:
the main body, the roof slab, the balcony slab and its parapet, five screens
between the balconies, eight posts, the terrace paving, the entrance and alcove
steps, two ridge vents, and the yard fences. Each wall ring rises 0.12 m into
the roof slab. The union trims the walls exactly where the soffits meet them
and deletes the buried parts, so the result is the boundary of one empty volume.

**The ridge vents are open stacks**, as CLAUDE.md wants every chimney:
0.84 × 0.68 m sheet-metal boxes standing 0.95 m over the ridge, each a 0.10 m
rim round one flue sunk 0.80 m to a floor, lined and floored in the `flue`
patch (`asset_build.open_stack()`). The floor stays 0.15 m over the ridge, so
the roof slab never reaches into the flue; `check_layout()` asserts it. The
flue stays recessed on both tiers that keep the vents.

Things in the builder worth knowing:

- **`roof_under()` is the soffit line, and the slab sits on it.** Built the
  other way round — the slab hanging below that line — every wall top, every
  screen and every post stands 0.12–0.30 m proud of the roof, and the body's
  own lid, which is supposed to be buried inside the slab, is left exposed
  above it as a second roof surface. That happened, it was caught in review,
  and `check_layout()` now asserts for each of those solids that its top lies
  strictly between the slab's soffit and its top surface.
- **The walls are a grid of panel-by-storey regions**, not one region per
  storey: a brick pier on every party line, lap siding across the window bands,
  board-and-batten round the doors. Each panel is its own region with its own
  band, and every region carries its neighbours' breakpoints on each shared
  edge, so two that meet do so on the same vertices. The panel layout differs
  between the ground and upper storeys on the yard side, which is why the
  shared edge at 3.4375 m carries the union of both storeys' breakpoints.
- **Doors stand on a storey's floor line, which is also where one cladding band
  hands over to the next.** They are therefore notches in the region's bottom
  edge, not holes inside it, and the region below has to carry every vertex the
  faces above put on that line — for a casing ring that is four, because the
  two jambs and the recess's floor all meet it. `_standing()` works those out
  and `build_wall()` detours the outline round them.
- **The yard alcove is a pocket, not a plan notch.** The upper floor runs over
  it unbroken, so the ground storey's rear wall is holed for it and five faces
  are built inward: two side walls, a back, a boarded ceiling and a paved
  floor. The door is a casing ring in the far side wall, at a right angle to
  the wall the window is in, and it stands on the alcove's own floor — so the
  floor polygon carries the door's four vertices along that edge, which is what
  keeps the pocket closed.
- **The row-long slabs are subdivided in x on the screens' faces**
  (`screen_faces()`). The boolean's cut where a screen passes through the
  balcony slab, the parapet or the terrace then lands on an edge that is
  already there, instead of retriangulating a thirty-metre n-gon round five
  small rectangles. The same reasoning puts a station at each gable in the roof
  slab's extrusion.
- **One fence run across the whole back, not one per dwelling.** Four runs
  would abut end to end, and a pair of coincident end caps is the one thing an
  exact boolean resolves expensively. The gates sit in it, one per dwelling, in
  the same bay of each. The party fences start 0.15 m inside the terrace
  screens for the same reason — face to face they would be coincident.
- **Every fence run is a whole number of 2.5 m bays**, so the boards keep their
  pitch however long the run is, and the gate is one such bay mapped to its own
  region rather than a hole cut in the boards.
- **The post-union weld is 1e-4, not 1e-5.** The exact boolean resolves this
  row's 30 m eave lines in 32-bit floats and leaves the odd corner vertex a
  hundredth of a millimetre off its neighbour — enough to export as two
  vertices and fail a downstream manifold check. The smallest authored feature
  here is the 0.10 m window casing, so a 0.1 mm weld cannot reach anything real.
- **`tessellate_polygon` emits zero-area triangles** when a region's holes line
  up, as openings sharing head heights do. `_flip_slivers()` repairs each by
  flipping the long edge against its neighbour.
- **`close_solid()` walks and caps the rim itself** in edge-index order rather
  than using bmesh's `holes_fill`, which silently skips a loop whose vertices
  already carry a face, and rather than set order, which iterates by memory
  address and would triangulate differently each run. The lid is the roof's own
  chevron, split at the ridge by `connect_verts`.
- **`Builder.face()` computes its zero-area test in double precision**, from
  coordinates relative to the first vertex. A door has no bottom casing, so its
  casing ring's bottom face has zero area and must be skipped.

`check_layout()` asserts, before building, the constraints that are invisible
in the numbers and obvious once rendered: openings overlapping each other,
leaving their cladding panel, running off a wall or leaving their storey; the
gable apex or a storey outgrowing its atlas band; a roof slope longer than the
roof band; the balcony ceiling or the street eave outgrowing the bands they
sample; the roof failing to reach past the parapet; headroom under 2.2 m on the
balcony or 2.4 m on the terrace; the entrance step reaching past the eave; a
fence run that is not a whole number of bays, or a gate in the middle of one;
the yard door not fitting the alcove's side wall; a door leaf outside
2.0–2.4 m; a sill above chest height; four front windows per dwelling; the
roof-slab containment described above; and a street downpipe off its brick
pier, within 0.25 m of a corner or with less than 0.2 m of wall between it
and an opening or a step, or a yard downpipe crowding the parapet or standing
out past the gutter; the gable ladder within 0.3 m of the gable's corner or
with a bracket in the rake's soffit; the roof ladder outside the west rake or
on a vent's line; and the walkway not just behind the vents or stopping short
of the east one.

### Downpipes

Seven downpipes from the shared `scripts/downpipes.py`, unioned in with the
other solids. The street eave's gutter drains to three, one down the middle
of the 0.6 m brick pier on each party line. Each rises into the soffit
0.51 m out from the wall, just inside the fascia the gutter is painted on,
falls 0.25 m, steps back to the wall at 45 degrees, and ends in a shoe kicked
0.15 m out. The yard eave oversails the wall by 2.2 m, so each dwelling's
pipe drops straight from its gutter down the outer face of the balcony post
nearer its east party line, 3 cm off the post, to a shoe; it goes with the
posts at `LOD2`.

Every pipe is 0.1 m and joined to nothing but the soffit it leaves, so it
cuts no line through the wall's triangles. Its sides sample the middle five
of the fascia band's eight gutter rows (`PIPE_STRIP` in `facade_atlas.py`),
so the pipe takes the gutter's steel in every colour, and the gutter's
hangers, a metre apart, read as its clips. No atlas region was added and no
pixel changed. The tiers are the module's: eight sides with both bends at
`LOD0`, four at `LOD1`, straight at `LOD2`, three-sided at `LOD3`.

### Roof safety kit

From the shared `scripts/roof_safety.py`, as CLAUDE.md asks of a roof
steeper than 1:8 carrying something serviced from it: the 10.8° yard slope
and the 21.8° street slope carry two ridge vents. The kit stands at the
back, away from the front doors:

- **a wall ladder on the west gable**, centred 0.80 m in from its rear
  corner. The yard slope oversails its wall by 2.2 m over the balconies, too
  far for a ladder to pass outside it, the street wall is the front, and the
  gables are blank brick, so the ladder stands on brackets 0.72 m off the
  gable, passes 0.12 m outside the 0.60 m rake and runs 1 m above the roof
  edge there;
- **a roof ladder up the yard slope**, 0.70 m inside the west gable's plane,
  from 0.25 m up from the yard eave to just behind the ridge, its rails 8 cm
  off the sheet on brackets that run down into the slab;
- **a level walkway**, 0.30 m wide, along the yard slope with its upslope
  edge 8 cm behind the vents, from the roof ladder's top east past the east
  vent at x = 7.92: 22.5 m on posts every 1.2 m or less.

Every part samples the gutter's rows (`PIPE_STRIP`), the rows the downpipes
use, so the kit takes the gutter's steel in every colour, as a matched
rainwater and safety system does. The ladders' rungs are 0.28 m apart, 3 cm
square, each one's faces meeting the holes it leaves in the rails, so each
ladder is one closed solid; the walkway's plank and posts are separate solids
the union joins to the roof.

The tiers are the module's thinned to this row's budgets (`kit_modes()`):
every rung with brackets and posts at `LOD0`; every other rung and the plank
alone at `LOD1`, whose brackets and posts along the 22.5 m walkway would take
it past its ceiling; and from `LOD2`, where the vents the walkway serves go,
only the gable ladder's bare rails, three-sided, kept because they stand
outside the rake and so set the row's west extent and its pivot. They touch
nothing, so they join the tier after its weld and dissolve
(`roof_safety.append()`), where they cannot change what those passes merge.


## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 5652 | 12,000 | casing rings, reveals and glass on every window and door; the front door recessed 0.30 m; the yard alcove cut 1.4 m into the wall; seven downpipes, eight-sided with swan-neck and shoe; roof safety kit with every rung, brackets and posts |
| `LOD1` | 3686 | 4,000 | each opening becomes one recess the size of its casing (casing painted on the recessed plane); the alcove and the door recess stay; downpipes four-sided; kit with every other rung, no brackets or posts |
| `LOD2` | 1172 | 1,500 | openings flush; coplanar subdivisions dissolved; ridge vents, posts and steps dropped, and the kit with the vents but for the gable ladder's bare rails; plain fence runs collapse to one bay; the yard downpipes go with the posts, the street ones straight |
| `LOD3` | 492 | 500 | street and yard walls painted, not cut (see below); street downpipes three-sided; the gable ladder's bare rails kept |

**`LOD0` sits far under its ceiling, and that is correct rather than
something to pad.** The row is a 30 × 8 m box with one roof slab, a balcony, five screens
and a set of fences. The walls are triangulated as polygons with holes, not as
a grid of cells, and everything that would add triangles in this style — the
casings, the sashes, the lap siding, the board-and-batten, the brick coursing
and bond, the piers, the gutter, the rafter ends, the fence boards and rails —
belongs in the texture. Three things clear the 0.25 m relief test and are cut:
the front door's 0.30 m recess, the 1.4 m yard alcove, and the balcony itself.

**The roof safety kit costs 1990, 580, 16 and 16 triangles** on the four
tiers. At `LOD0` most of it is the ladders' rungs with their holes, and the
walkway's 20 posts with the squares they cut in the sheet.

### How `LOD3` fits 500 triangles

**`LOD3` does not cut its street or yard wall at all.** Each dwelling bay is one
quad mapped to a painted elevation of that bay (`facade_atlas.LOD3_FRONT` and
`LOD3_REAR`, at 14 px/m), and all four bays sample the same region because all
four dwellings are identical. This is CLAUDE.md's "flatten geometry into
suitable shared-atlas regions": the bay boundaries become UV seams and four
faces do the work of a wall with twenty holes in it.

What that buys is the thing worth having: **the balcony, its parapet, all five
screens between the balconies and every yard fence survive to the last tier**,
so the back still reads as four private dwellings rather than one long shed.

Three things do go at `LOD3`, and each is small and checked:

- **the eight terrace posts.** 0.18 m across is about 1.5 px at 120 m, and they
  stand inside the roof's own projection, so dropping them cannot move the
  plan. The parapet and the screens keep the balcony reading without them.
- **the four yard gates**, because the four back fence runs become one span at
  this tier. A 1.05 m leaf is about 9 px at 120 m. The party fences all stay,
  which is what makes four yards read as four.
- **the yard alcove**, which is painted as a dark recess into the `LOD3_REAR`
  bay. At 1.3 m wide it is about 11 px at this distance.

The ridge vents go at `LOD2`, as rooftop clutter should, and so do the entrance
and alcove steps — a 0.31 m step is about 2 px at 70 m, and both sit inside a
projection every tier keeps (the roof in front, the balcony behind), which
`check_layout()` asserts.

Modelled trim — the roof slab, the balcony slab and parapet, the screens, the
posts, the vents — is a few hundred triangles at `LOD0`, far under the
quarter-budget cap. Opening the vents' flues cost 16 triangles each, 32 on
`LOD0` and `LOD1`.

**The seven downpipes cost 442 and 222 triangles** at `LOD0` and `LOD1`, the
pipes' own faces and the holes they leave in the soffits together. The three
street pipes cost 46 at `LOD2` and 40 at `LOD3`, where they are three-sided,
which leaves `LOD3` 24 under its ceiling.

## LOD review

Compared with a perspective camera, 1920×1080, **50° vertical FOV**, distance
measured along the view direction to the centre of the assessed wall, under the
preview sun. Two lines of sight were used, because this asset's two long
elevations are completely different: one off the street corner and one off the
yard corner, both raised about 12°. Tiers were compared in adjacent pairs
around the table's switches (35 m, 70 m, 120 m) and each against `LOD0`.

- `LOD0`→`LOD1` at 35 m: reveals shallow out and each casing ring becomes one
  recess. Window positions, sizes and colours are identical. The front door's
  recess, the alcove and the balcony are unchanged.
- `LOD1`→`LOD2` at 70 m: openings go flat, the ridge vents, the posts and the
  steps go, and the plain fence runs collapse to one bay. The posts are the
  only noticeable loss and they are about 2.6 px across there; the parapet and
  the screens hold the balcony's read.
- `LOD2`→`LOD3` at 120 m: the street and yard walls change from cut openings to
  painted ones and the alcove becomes a painted recess. Silhouette, roofline,
  the balcony, the parapet, all five screens and every party fence are
  unchanged.

These are authoring comparisons in stable Blender renders. They are not proof
of runtime switching, filtering or performance; the table's distances are
starting points and the consumer owns the real switch distances.

**Downpipes across the switches**, from `review/downpipes_shared_2026_09_25/`
(front, oblique and rear at 35 and 70 m, front and oblique at 120 m, under
noon). At 35 m the eight- and four-sided pipes cannot be told apart. At 70 m
the street pipes' swan-necks straighten: the 0.43 m kick is about 4 px in the
oblique view, and side by side the kink under the eave can be found, but each
pipe keeps its dark line down its pier. The yard pipes go with the posts they
hang on, which was already the change at this switch. At 120 m the street pipes
are the same one-pixel line on the piers in `LOD2` and in `LOD3`'s three-sided
pipes.

**The roof safety kit across the switches**, from
`review/roof_safety_2026_09_25/rivitalo_brick_gable/` (every tier; front,
oblique, aerial and rear at 20 and 60 m, under noon; a close-up of the west
end at `LOD0`). At 35 m every other rung still reads as a ladder and the plank
without its 4 cm posts is the same dark line behind the ridge. At 70 m the
walkway and the roof ladder go with the vents, and the gable ladder drops to
its bare rails: from the yard and from above the line behind the ridge can be
found missing side by side, not at a glance, and the rails still stand over
the rake as a tick at the west end.

## Interior geometry

Measured with `scripts/validate_asset.py` on the exports:

| Tier | Hidden triangles | Share |
| --- | --- | --- |
| `LOD0` | 130 of 5652 | 2.3 % |
| `LOD1` | 107 of 3686 | 2.9 % |
| `LOD2` | 26 of 1172 | 2.2 % |
| `LOD3` | 28 of 492 | 5.7 % |

**All but the downpipes' backs are the inside of a balcony, and none is a
buried partition.** The backs face the brick or a post 3 cm away, and every
sampled ray from them heads for it and meets it: 6-11 triangles a tier,
exterior surface seen at a grazing angle. The roof ladder's rung undersides,
a few centimetres over the sheet, and on `LOD2` and `LOD3` the backs of the
gable ladder's bare rails, facing the gable, are the same case. The faces were listed and grouped by
normal: the balcony decks (z 3.50, y 4.00–5.62), the parapets' inner faces (y
5.62, z 3.50–4.54) and the screens' inner faces (x on the party lines). All are
exterior boundary, the same case CLAUDE.md makes for recessed glass.

The test misses them because the escape cone is narrow, not because they are
enclosed. From the middle of a deck a ray has to clear the parapet
(1.04 m at 0.8 m away) and still pass under the roof edge 2.2 m further out:
that is elevations of roughly 52°–65°, in the +Y half only. Forty directions
over a hemisphere do not reliably land in it. A camera in the yard sees all of
it. No wall stands inside the dwellings, by construction.

## Known simplifications

- **`LOD3`'s street and yard walls are painted, so their reveals flatten and
  the alcove becomes a painted recess.** Openings keep their exact positions
  and sizes across the switch — both files read the elevation layout from
  `facade_atlas.py`, so a window cannot drift between the cut tiers and the
  painted one — but at 14 px/m a 0.10 m casing is under two texels.
- **Reveals are 0.14 m deep** on the windows, shallower than the 0.2–0.4 m
  masonry reveals the 0.25 m test was written around, because a boarded timber
  wall sets its windows near the outside face. They are cut anyway: even 0.14 m
  gives the glass a visible shadow line at `LOD0`. The front door is the
  exception at 0.30 m, which is the type's own recessed entrance and clears the
  test on its own.
- **Windows pop from recessed to flat at the `LOD1`→`LOD2` switch**, as
  CLAUDE.md expects. The front door's 0.30 m recess is kept through `LOD1` for
  that reason and goes at the same switch.
- **Plain fence runs collapse from 2.5 m bays to one stretched bay at `LOD2`.**
  The boards are 0.125 m, about one pixel at 70 m, so what stretches is a
  pattern that is already sub-pixel. The gated back run keeps its bays until
  `LOD3`.
- **The balcony screens stop 0.05 m short of the soffit at `LOD2` and `LOD3`**
  instead of running into it. The gap is invisible past 70 m and keeping five
  screens out of the roof's underside is worth more than the gap costs.
- **Not modelled, and not painted either:** the entrance lamps beside each
  front door and house numbers. Both fail the 0.25 m test, and each is
  placement-specific, so a tiling band cannot carry it. Worth revisiting if
  the row is ever seen closer than the 20 m camera floor.
- **The roof safety kit is simplified** (Construction): the gable ladder has
  no safety hoop and its top is straight rails rather than a curved grab rail
  over the rake; the walkway is a plain plank on posts, not a perforated
  grating on raked brackets; there are no snow guards on the street slope.
- **The gutters are painted and the downpipes modelled** (Construction). The
  pipes' clips are the gutter's painted hangers, the yard pipes are not
  fixed to their posts by anything modelled, and each shoe discharges onto
  open ground, with no splash block or gully.
- **The terrace paving and the alcove floor are flat concrete**, with no slab
  joints: they are seen at a grazing angle at every review distance, and a
  joint pattern would have to be either its own band or stretched. The balcony
  deck does get boards, because it can share the siding band at true scale.
- **Only two ridge vents** stand for the row's roof stacks, on the party lines
  either side of the middle. They are rooftop clutter and are dropped at
  `LOD2`, where they are insignificant.
- **The four dwellings are identical, not mirrored in pairs.** Real rows of
  this type are built both ways; unmirrored keeps one door per bay centred,
  which is what the brief asks for.

## Texture set

| File | Space | Notes |
| --- | --- | --- |
| `_albedo_<variant>.png` ×5 | sRGB | 1024², 8-bit RGB, no alpha |
| `_orm.png` | Non-Color | 1024², R = AO, G = roughness, B = metallic |
| `_normal.png` | Non-Color | 1024², OpenGL tangent space (+Y green up), shared across tiers/colours |
| `_emission.png` | sRGB | 1024², neutral glazing mask; shared across tiers/colours |

Eight unique 1024² images in total, one normal map among them.

- **Texel density 64 px/m**, matching the catalog, with three recorded local
  deviations, each on an axis that carries no detail:
  - the **roof band** is stretched up the slope to 12 px/m. A felt roof changes
    nothing along the slope but its sheet laps, which land every metre;
  - the **vertical board-and-batten band** keeps 64 px/m across the boards and
    normalises V over whatever panel it clads, 10–20 px/m. Nothing changes
    along a board but the grain;
  - the **`LOD3` bay elevations** are 14 px/m, which at that tier's 120 m is a
    105 px region for a bay about 72 px on screen.
- **A trim sheet, not one picture per elevation.** A 30 m elevation would need
  1920 px at 64 px/m. Instead the walls sample tiling bands — concrete plinth,
  lap siding, brick, board-and-batten, roof felt, fascia with its gutter, and
  the boarded soffit with its rafter ends — and every opening samples a region
  of its own carrying its casing, sill, drip cap, sashes and glass. `build.py`
  cuts a ring of faces round every opening for the casing to land on, so
  windows stay exactly where they are at every tier and none depends on a
  painted elevation.
- **The siding and brick bands are one storey tall and are sampled from each
  storey's own foot.** 3.125 m is 25 lap boards and 40 brick courses exactly.
  The brick is the catalog's module, laid by `scripts/brickwork.py`'s
  `bond()` (0.25 m stretcher on a 0.078125 m course, 16 x 5 px); the band
  keeps its own tone (±5.5 % per brick, seed 3, repeating every 40 courses)
  and has no mortar id, its joints the brick darkened to 0.80. The bond
  and per-brick tone repeat on 2 courses and 64
  bricks, both of which divide the band, so a wall hands over from the ground
  storey's run to the upper storey's at 3.4375 m without a part course and
  without a tone jump.
- **Every band tiles in U at 16 m**, and the 7.50 m dwelling module, the 0.25 m
  brick, the 0.125 m boards, the 0.60 m rafter spacing and the 1.0 m gutter
  hangers all divide 1024 px, so a wall whose U crosses the atlas wrap sees the
  pattern continue rather than break. The downpipes sample the middle five of
  the gutter's eight rows (`PIPE_STRIP`), so they need no region of their own.
- **The flues sample a `flue` patch**, the blank grey darkened to about sRGB
  34 and occluded, as a narrow shaft is whatever the sun does. Painted
  separately from `cap` so the lining reads as soot rather than sheet metal.
- `check_bands()` fails the bake if any tiling band contains a material id it
  should not, and `check_regions()` fails it if two unique regions overlap or
  run off the atlas. Regions are bled 2 px so filtering at their edges stays
  inside the artwork.
- **Glass is painted by `scripts/glazing.py`,** the catalog's shared
  treatment, at the catalog base colour. The dark grey (124/130/133) recorded
  here before was the darkest in the catalog and still about four times too
  bright: this type's windows are large and its balcony is glazed end to end,
  and the openings read as white panels in direct sun. It stays neutral and
  low-saturation, opaque, with the separation carried by roughness, and
  nothing is reflected into the albedo. See Glazing treatment below.
- Roughness separates the materials: lap siding 0.72, board-and-batten 0.74,
  brick 0.82, roof felt 0.86, casings 0.48, sashes 0.46, glass 0.08, concrete
  0.90, paving 0.88, soffit 0.76, fence boards 0.78, rails 0.70, gutter 0.38
  with metallic 0.35, galvanised posts 0.42 with metallic 0.65.
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
  - lap siding, 18 mm at the butt tapering to 4 mm;
  - brick faces 6 mm proud of recessed mortar;
  - board-and-batten with 18 mm battens;
  - the felt roof's laps and welted seams;
  - the gutter as a 70 mm half-round, and the soffit's rafter ends 50 mm deep;
  - casings 20 mm, sills 35 mm, sashes 12 mm proud of the glass;
  - fence and gate boards with grooved joints on 22 mm rails, and the posts.
  The LOD3 bay elevations are painted at 14 px/m and seen only beyond 120 m, so
  they stay flat.
  Glass stays flat. The felt roof band is stretched to 12 px/m up the slope, so relief that
  varies up it is scaled by 12/64 to keep its slope physical.
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
- **Only the plinth follows height.** WOOD and BRICK are sampled from each
  storey's own foot, so ground splash or eave dust painted there would come
  back at the upper floor line; those bands get only grime, faint rain runs
  and dust in the laps and mortar joints (from the cavity). The plinth band's
  V is height from the ground on every wall, and it takes the soil, splash
  specks, green film and runs from the cladding's drip.
- **The felt roof band, up the slope from the eave:** long runs, more dirt
  toward the eave, and the surface chalking toward the ridge.
- **Elsewhere:** runs down the fascia from the gutter; dust on the soffit
  boarding next to the wall; dirt and short runs on the sills and head
  casings, water on the sashes' bottom rails, hand grime and dirty feet on the
  doors; splash at the foot of the fence bays and grime at the gate's handle;
  the LOD3 bays' plinths at their own 14 px/m.
- The level was chosen on `rintamamiestalo_porch` (see its notes); this
  row takes the same function with its own layout.
- The albedo and ORM PNGs are larger on disk (6 files, 2.4 MB against 2.0 MB before), as the noise
  compresses less; resolution, count and GPU memory are unchanged.

## Glazing treatment

Panes are painted by `scripts/glazing.py`, the catalog's shared treatment.

| | |
| --- | --- |
| base colour | sRGB 50/54/57 (`glazing.BASE`) |
| measured over the glass mask | mean sRGB 56, linear 0.036 |
| relative to the trim around it | 0.37x |
| roughness / metallic | 0.08 / 0 |
| panes in the atlas | 14 |

`albedo()` builds the atlas as before and then hands the glass mask to
`glazing.rooms()`, which gives each pane its own overall level, a falloff
toward the floor, and a lit patch of far wall on about half of them. That is
the room behind the pane rather than a reflection, so it belongs in base
colour; no sill-to-head sky gradient is baked, which Texture Requirements
rule out.

Why it changed: at the previous value the glass measured linear 0.197
and sat at 0.78x the trim around it, so the panes read as glossy
white paint rather than as openings. Seen from outside a window is mostly the
unlit room behind it, and the sky reflection is generated at shading time from
roughness and the dielectric F0 — a pale base colour asks the diffuse lobe to
reflect the sky as well, which double-counts it. The eight-way comparison that
settled the choice lives in `studies/window_glass/`, local only and gitignored.

Limit: the atlas is a trim sheet with 14 glass regions, one per opening
kind, so panes vary between kinds and not between windows — every window of a
kind on this building is identical. Per-window variety would need several pane
regions per kind and `build.py` picking one per instance. This is the same
constraint already recorded for emission.

Pending: calibration in the consumer's lighting.

## Variant list

Five variants, `export/rivitalo_brick_gable_albedo_<name>.png`, sharing one ORM
(roughness and metal patterns are identical across them):

| Variant | Timber stain | Brick | Casings | Roof | Fence |
| --- | --- | --- | --- | --- | --- |
| `brown` (default) | dark red-brown | red | near-black | dark grey felt | red-brown |
| `red` | punamulta red | red | near-black | dark grey felt | red |
| `ochre` | warm ochre | pale yellow brick | dark brown | grey-brown felt | ochre |
| `grey` | grey stain | grey-brown | dark grey | grey felt | grey |
| `green` | dark green stain | red | dark green-grey | dark grey felt | green |

This is the low-rise case in CLAUDE.md: a street of these differs in stain, and
the variants are exactly that. The brick moves with the stain — the pale yellow
brick Finnish suburbs are full of under the ochre, red under the dark stains —
but never within one building. `brown` is the default because it is the
combination the type is most often seen in. Glass, the concrete plinth, the
paving, the galvanised posts and the dark casings' metal drip caps never change.

Every `.glb` references the default (`brown`) albedo. Another variant is the
same mesh with that one file swapped; geometry and UVs are identical by
construction, since the atlas paints ids and shading once and colours them per
variant (`facade_atlas.albedo`).

## Night lighting

`rivitalo_brick_gable_emission.png` is a neutral RGB mask of the atlas
generator's glass ownership. Glazing is grey, each pane lit as a room (see Room-lit panes below); siding, boarding, brick, roof,
solid door panels, the plinth, the paving, the posts, the fences and the gates
are black. The front door's narrow light and the balcony and yard doors'
glazing participate. No interiors or extra geometry were added.

All four GLBs bind the same external sRGB mask through `emissiveTexture` on
UV0, shared across every colour and tier. Every GLB defaults to
`emissiveFactor = [0, 0, 0]` with the texture binding retained; a reference lit
factor is linear RGB `[1.0, 0.55, 0.23]`. The consumer owns occupancy, time and
fading, and should keep that state per placed building — which matters here,
since one placement is four households and a real row is never uniformly lit.
Reused glazing UVs mean this is one building-wide control, not per-dwelling or
per-window switching; the PNG contains candidate windows, not a baked occupancy
pattern. **Per-dwelling lighting would need either separate UV islands per bay
or four placed instances**, and is the obvious thing to revisit once the
consumer exists.

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
occupied. Averaged over the glass it is 55 % of the old full-white mask
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
share: `build.py` imports z-levels, panel layouts, opening sizes and region
rects from it rather than repeating them.

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

**Done in authoring.** All six pre-export views inspected at `LOD0` — front,
rear and both ends orthographic, a plan from above, and raised three-quarter
aerials off both the street and the yard corners, the second added because this
type's yard elevation carries the balcony — plus eye-level perspective views of
the entrance, the terrace and the alcove. Mechanical validation passes with no
failures: closed welded topology on every tier, one material slot, shared
ground-level origin and matching plan extents, external uri-only images,
correctly bound ORM (AO/R, roughness/G, metallic/B) and a default-off emission
binding on all four tiers. Triangle ceilings are met on every tier, with no warnings.

**Texture pipeline change, checked before against after** with
`scripts/review_compare.py`: `LOD0` front and oblique at 20 m and 35 m under
noon, morning and backlight; mip4 stress renders of `LOD2` at 75 m and `LOD3`
grazing at 125 m; and the catalog preview. The boards, laps and seams read as
raised in direct sun, which confirms the OpenGL green channel, and no new colour
leaks appear at mip4. These mip4 renders were made after fixing
`scripts/review_asset.py`: Blender 5.2's glTF importer packs images, and a
packed image ignores `--texture-dir`, so every earlier stress render had shown
the full-resolution textures. The normal map is bound at scale 1 on every tier. The sampled
hidden-surface findings were listed, grouped and accounted for above.

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
difference 0.63 / 255 at most in any view). Close-ups of swan-necks and shoes
at `LOD0` and `LOD1`, and of whole pipes at `LOD0` and `LOD2`, and of a yard
pipe on its post. `scripts/validate_asset.py` still reports no failures or
warnings.

**Roof safety kit, checked before against after**, the folder snapshotted
into `review/roof_safety_2026_09_25/rivitalo_brick_gable/before_snapshot/`
first: every tier, front, oblique, aerial and rear at 20 m and 60 m under
noon, and a close-up of the west end at `LOD0`. The gable ladder, the roof
ladder and the walkway are the only additions; the west extent grew 0.18 m
and the pivot moved 0.09 m west with it. `scripts/validate_asset.py` still
reports no failures or warnings.

**Pending, and not claimed.** These need the consumer and are recorded as open
rather than assumed:

- switch distances and runtime performance, which no authoring render can
  establish;
- mipmapped and anisotropic appearance at and beyond the switches in the
  consumer: `atlas.pad()` now fills every gutter, but coarse mips can still
  merge regions that touch. The brick bond and the lap siding are the patterns most likely to
  merge into flat colour early on this asset;
- daylight glass-value calibration in the consumer's lighting, night exposure
  and emission spill;
- the normal map in the consumer: MikkTSpace tangent generation on import and
  its filtering at distance;
- the `LOD2`→`LOD3` switch, where the street and yard walls change from cut
  openings to painted ones, judged against the consumer's actual switch
  distance rather than the 120 m review assumption.

## Tooling versions

- **Blender 5.2.2 LTS.**
- **Blender Lab "MCP" extension:** not used for this asset. It was built,
  exported and rendered in background Blender processes, and the MCP server was
  not connected during authoring.

Recorded as a known-good marker, not a requirement. Blender 5.2 flags
`Material.use_nodes` and `World.use_nodes` as going away in 6.0, so `build.py`
only sets them when a node tree is missing.

- **CPython 3.14.7 with numpy 2.5.3, scipy 1.18.1 and Pillow 12.3.0** for the
  texture export.

## Revision log

- **2026-11-22 — shared brick bond.** The brick band is laid by
  `scripts/brickwork.py`'s `bond()`; same module, joints and relief, only the
  per-brick tone of alternate courses reshuffled. Triangle counts unchanged.
- **2026-10-01 — hollow ridge vents.** Each vent is now an open stack, a rim
  round a flue sunk 0.80 m to a soot floor, and stands 0.95 m over the ridge
  instead of 0.62 m so the floor clears the roof (Construction). A `flue`
  patch was added to the atlas; triangle counts changed from
  5620 / 3654 / 1172 / 492 to 5652 / 3686 / 1172 / 492. The textures, GLBs,
  `source.blend`, `preview.png` and `variants.png` were regenerated.

- **2026-09-25 — roof safety kit.** A wall ladder on the west gable, a roof
  ladder up the yard slope and a walkway behind the ridge to the two vents,
  from the new shared `scripts/roof_safety.py` (Construction). Triangle
  counts changed from 3630 / 3074 / 1156 / 476 to 5620 / 3654 / 1172 / 492.
  The overall width grew from 31.20 m to 31.38 m and the pivot moved 0.09 m
  west. No atlas pixel changed; the GLBs, `source.blend`, `preview.png` and
  `variants.png` were regenerated.

- **2026-09-25 — downpipes.** Seven downpipes from the new shared
  `scripts/downpipes.py` (Construction). Three from the street eave down the
  party-line piers, and one per dwelling from the yard eave down a balcony
  post. `facade_atlas.py` gained `GUTTER_PX` and `PIPE_STRIP`, which name the
  gutter rows the pipes sample; no pixel changed and the PNGs were not
  regenerated. Triangle counts rose by 442, 222, 46 and 40. The GLBs,
  `source.blend`, `preview.png` and `variants.png` were regenerated.

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
