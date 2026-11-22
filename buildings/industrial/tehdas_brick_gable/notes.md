# tehdas_brick_gable

## Style brief

A Finnish light-industrial building of the kind put up on a town's edge from
the 1970s on (*tehdas*: works, factory): workshop below, offices above, in red
facing brick under a shallow profiled-steel gable. It is a composite of the
type, not a portrait of any one building.

- **The main block** is 42 x 12 m and two storeys, with long ribbon windows in
  white frames on both floors keeping one 6 m rhythm along both long walls, a
  concrete plinth, and a light grey trapezoidal-sheet roof at about 20 degrees
  with a gutter along each eave.
- **Two single-storey wings with dark felt roofs** stand against its long
  sides behind a low parapet with a light coping: a smaller one on the front,
  and a larger one behind.
- **The main entrance** is on the front, next to the front wing: a glazed
  screen set 1.5 m back into a lobby under a flat steel canopy.
- **The east end:** the ground storey stops 3 m short of the gable and the
  upper storey runs on over four concrete pillars, sheltering a second glazed
  entrance and a window.
- **The west end:** the gable carries a sectional loading door and a steel
  personnel door, and the front wall a stair lit by one tall strip of glazing,
  with its own glazed door under a canopy.
- **Ladders:** from the ground to each wing's roof, on the wings' east faces;
  from the front wing's roof up the main wall and past the eave; and a roof
  ladder from there up the front slope to the ridge.
- **Vent pipes:** seven black steel pipes on both slopes near the ridge, in
  three sizes.
- **Downpipes:** eight, in the gutter's colour. Three on each long wall step
  back from the eave on a swan-neck; one on each wing's west face runs up
  under its roof slab. Each ends in a shoe above the ground.

No signage, lettering or company marks anywhere on it.

## Category and secondary use

`buildings/industrial/`. Secondary use: **offices**, on the upper storey,
which the ribbon windows at desk height and the two glazed entrances imply.
The loading door, the double-height hall behind it and the flat-roofed wings
are the industrial part, so the building's primary category is industrial.

## Hero/landmark status

Not a hero. Ordinary triangle ceilings and the 1024 texture cap apply, and all
are met.

## Footprint

- **Main block walls: 42.0 x 12.0 m.** The roof adds 0.30 m at each rake and
  0.45 m at each eave: **42.6 x 12.9 m** over the roof.
- **Front wing:** 8.4 m along the front wall by 5.0 m out from it; its roof
  slab oversails its walls by 0.125 m on three sides.
- **Back wing:** 11.4 m along the rear wall by 11.0 m out from it, same
  oversail.
- **East porch:** the ground storey's east wall is 3.0 m inside the gable;
  the pillars' outer faces are 0.15 m inside the upper walls.
- **Canopies:** 1.2 m (main entrance) and 1.0 m (stair door) off the front
  wall.
- **Overall plan extent: 42.6 x 28.25 m**, the full width of the roof by
  the front wing's fascia to the back wing's. Overall height **10.04 m** to
  the top of the tallest vent pipe; the ridge is at 9.41 m.

The pivot is the centre of that 42.6 x 28.25 m box, which is 3.0 m behind
the main block's own centre line because the back wing projects further than
the front one.

## Story height

**3.3125 m** floor to floor (212 texels), inside the 3.0-3.3 m band to within
a centimetre. The ground floor is at grade, with no raised threshold, so the
loading door opens onto the yard. The roof's underside meets the side walls
at **7.0 m**: the upper storey has 3.69 m to the eave, the extra 0.38 m being
its roof structure. The wings' felt decks are at 3.75 m, the coping at
3.875 m.

## Door leaf height

- **Every leaf is 2.125 m**, within 2.0-2.4 m.
- **Glazed doors** (the main entrance screen, the porch entrance screen and the
  stair door): the opening runs on to **2.6875 m**, so above each leaf is a
  **0.5625 m transom light**, with the transom bar drawn across at the leaf
  head in each door's atlas region.
- **Steel service doors** (rear wall, west gable, both wings): leaf 2.125 m
  in a 2.1875 m opening, the top 0.0625 m being the steel frame's head.
- **The loading door** is 4.0 m wide by 3.75 m high sectional steel. It is
  not a pedestrian door and not a human-scale anchor: the steel door beside it
  is.

## Window sills

- **Ground-storey ribbon windows:** sill **1.0 m**, head 2.406 m, between
  the doors' leaf head (2.125 m) and the head of their transom lights
  (2.6875 m).
- **Upper storey:** sill **4.3125 m**, 1.0 m above the upper floor; head
  5.719 m. Both are well under the 1.4 m chest-high line.
- **The stair glazing** runs from 3.25 to 6.5 m: it lights a stair, which has
  no floor at either sill line, so it ignores both on purpose.

## Eave overhang

- **0.45 m at the eaves**, 0.30 m at the rakes, with a white-painted soffit and
  a flashing-coloured fascia carrying the half-round gutter. Both are inside
  the 0.3-0.6 m default.
- **The wings' roofs** are flat slabs that oversail their walls by 0.125 m
  behind a 0.375 m fascia. That is a parapet and coping detail, not an eave.

## Construction

About thirty closed solids unioned with Blender's exact boolean:

1. **the main block's wall ring**, walked counter-clockwise from above. Its
   front and rear walls are notched at the east end below 3.0 m for the
   porch; the porch's back wall and the upper storey's soffit close the ring
   there. It is capped by a floor on the ground and a lid split at the two
   apexes, since the rim follows both gables;
2. **the gable roof**: one chevron-section slab extruded along the ridge, so
   deck, fascias, soffits and barge ends are one closed surface;
3. **each wing's wall ring**, WING_BURY (0.2 m) into the block, and **each
   wing's roof** as one solid: a U of coping round the felt deck, the
   parapet's inner faces, the fascia and the oversailing soffit;
4. **four pillars**, sunk 0.125 m into the upper storey;
5. **two canopies**, sunk 0.1 m into the front wall;
6. **four ladders** from the shared `scripts/roof_safety.py`, each one closed
   solid built without a boolean. Two rails are boxes whose inner faces are
   holed for each rung, and whose rear faces are holed for each bracket. Each
   rung's four faces meet its holes on shared vertices; each bracket runs back
   into the wall. The places are this building's; the shape, the rung and
   bracket tiers and the sizes are the module's, which took them from here.
   Unlike the module's own roof ladder, which stands off the sheet on
   brackets, this one's rails stay bedded 3 cm into the sheet, as they were
   built, and it keeps its galvanised steel patch rather than the gutter's
   colour;
7. **seven vent pipes**, each with its foot a slice of the roof plane inside
   the slab;
8. **eight downpipes** from the shared `scripts/downpipes.py`, each one closed
   solid swept along its axis and mitred at every bend (see Downpipes below).

The union trims the wall tops into the roofs, the wings into the block and
the pillars into the upper floor, and leaves the boundary of one empty volume.
Every opening is built into its own wall region as brick reveals round a
closing plane. The wall regions carry their neighbours' breakpoints
explicitly, so all four corners and the porch meet on shared vertices.

The parameters everything derives from live in `facade_atlas.py`:

- the plan (HX, HY, PORCH_X, the two wings' rectangles);
- the storey, sill, door and eave heights;
- TAN (0.36, 19.8 degrees), ROOF_T, EAVE_OUT and RAKE_OUT;
- the wing slab's four heights;
- every opening's width and height.

`build.py` keeps the elevations' opening lists, the pillar, canopy, ladder
and vent positions, and `check_layout()`. That check fails the build if:

- an opening comes within 0.3 m of another opening or 0.4 m of a corner, or
  sits behind a wing or in the porch;
- a door leaf leaves the 2.0-2.4 m band, or a glazed door has no transom;
- a wing comes within 0.3 m of the porch line, or its coping reaches the
  upper sills;
- a canopy crowds the door head or the upper windows;
- the wall ladder misses the deck or crosses a window, or a wing ladder
  crosses a door or a window;
- a vent stands on the ridge, the eave, a gable or the roof ladder's line;
- a downpipe's axis comes within 0.25 m of a corner or leaves less than
  0.2 m of wall between it and an opening, a canopy or the wall ladder (the
  shared limits in `scripts/downpipes.py`), or would come down on a wing or
  into the porch.

### Two construction lessons from the weld

The union is followed by a 0.1 mm weld, as in the other catalog assets. On the
first build the weld itself created a zero-thickness sheet of faces at the
wall ladder's foot. The raw union was clean. The weld merged near-coincident
vertices from two sources, and both were fixed in the geometry rather than by
changing the tolerance:

- **The gable walls first changed atlas rows exactly at the eave line**, on
  the roof's own underside. The exact boolean resolved each eave corner into
  up to a dozen coincident vertices. The split is now at `Z_GABLE` = 6.75 m, a
  quarter metre under the soffit.
- **The wall ladder's rails were driven into the felt deck.** The long thin
  triangles of the rails' holed faces crossed the deck within a tenth of a
  millimetre of the rails' own edges. The ladder now hangs on its brackets and
  ends 0.15 m above the deck, above the coping, as such ladders do.

After both changes the raw union has no vertex pair closer than 0.1 mm, and
the weld changes nothing.

### Downpipes

The pipes were first written for this building and then moved into
`scripts/downpipes.py`, so the rest of the catalog hangs the same pipe.
That module owns the shape, the UVs, the placing limits and the default
tiers; `build.py` only places the eight pipes and drops them at `LOD3`.

Each pipe is a 0.1 m section, eight-sided at `LOD0` and square below, swept
down its axis with the ring at every bend on the bisecting plane, so the
flats meet cleanly and the whole pipe is one closed solid.

- **Eave pipes:** the outlet rises into the eave's slab 0.36 m out from the
  wall, just inside the fascia the gutter is painted on. It falls 0.25 m
  below the soffit, steps back at 45 degrees, and runs down.
- **Wing pipes:** run straight up into the wing's oversailing slab, as fed
  from a scupper through the parapet.
- **The shoe:** every pipe ends in one kicked 0.15 m out and down, its mouth
  about 0.16 m above the ground.

Placement:

- **Front and rear walls:** three each, at the west corner (0.4 m in) and in
  the gaps between window bays, at x = -9 and x = 3 on the front and at
  x = -9 and x = 2.5 on the rear, clear of the service door there.
- **None at the east end:** the porch leaves nothing for a pipe to come down
  to.
- **Wings:** one each, on the west face near the outer corner, so its shoe
  kicks out inside the plan's existing extent. On the front, the first
  placement pushed the footprint out 0.19 m and would have moved the pivot.

The pipes stand **3 cm off the brick** on nothing, hung from the slab they
leave, as they would on their clips. The first version buried each pipe's
back 15 mm in the wall so the union would join them. Each then cut two
6 m lines through the wall's long thin triangles and cost over 140 triangles
at `LOD0`. Standing off, they cost about 75, and cut nothing but the soffit
where they enter it.

The sides sample the middle five of the eave band's nine gutter rows along
the pipe's length (`PIPE_STRIP` in `facade_atlas.py`). The pipe therefore
takes the gutter's colour in every variant and its half-round shading across
each flat, and the gutter hangers painted a metre apart read as the pipe's
clips. No new atlas region was needed.

### The porch

The upper storey's east 3 m stands on four 0.406 m concrete pillars, evenly
spaced across the gable, and is open on three sides: front, back and east. It
is a covered passage at the building's end, with the second entrance and a
window in its back wall. The two wings end 0.6 m short of the porch line
(x = 17.4 against 18.0). Their east faces set in from it as a visible step,
and no wing wall is coplanar with the porch wall, which is the case a union
does not survive.

## Per-tier triangle counts

Measured on the exported, triangulated GLBs by `scripts/validate_asset.py`:

| Tier | Triangles | Ceiling | Status |
| --- | --- | --- | --- |
| `LOD0` | 3780 | 12,000 | under |
| `LOD1` | 2692 | 4,000 | under |
| `LOD2` | 1288 | 1,500 | under |
| `LOD3` | 488 | 500 | under |

Where they go, by the atlas area each triangle samples:

- **`LOD0`:**
  - The **ladders take 1696**, just over half. Every rung is a closed box
    meeting two holed rail faces, about 20 triangles each, and there are 67
    of them:
    - 16 each on the two wing ladders;
    - 14 on the wall ladder;
    - 21 on the roof ladder.

    That is within Geometry and Construction's quarter-of-the-ceiling trim
    allowance (3000), and the ladders were an explicit part of the brief.
  - The brick walls, reveals and wall regions round 37 openings take 733.
  - The downpipes about 600, with the splits their tops make in the soffits.
  - The roof 184 (the vents cut it), the vent pipes 161, and everything else
    about 400.
- **`LOD1`** keeps every other rung (ladders 996), cuts the vents to six
  sides and the downpipes to four (about 300). The openings and their reveals
  are unchanged.
- **`LOD2`** paints every opening flat except the entrance lobby. It keeps
  every fourth rung and the four larger vents as four-sided stacks, and the
  downpipes as straight square pipes with no swan-neck or shoe (about 160).
  The three 0.16 m vents go, and so do the ladders' brackets
  (`brackets_kept()`). The brackets are 4 cm bars, and each cost about twenty
  triangles in its box, its rail hole and its cut in the wall. Their 250
  triangles pay for the downpipes, so the tier went down, from 1380 to
  1288.
- **`LOD3`** drops the ladders, the downpipes and all but the two 0.5 m
  exhausts, and makes three simplifications:
  - **The wings become plain boxes** (`wing_box()`): brick, then the fascia's
    flashing on the wall up to the coping's height, and a lid painted with
    the coping's light edge. Parapet, oversail and soffits were about 40
    triangles, each about a pixel wide at 120 m.
  - **Stacked openings on the long walls share one flush quad**
    (`bays_merged()`, `storey_pairs()`):
    - each bay's two ribbon windows, over `LOD3_BAY`;
    - the stair's door and glazing, over `LOD3_STAIR`.

    Both are quarter-density regions copied down from the bands and regions
    they stand for. Eight pairs at about 8 triangles each.
  - **Both canopies stay** on every tier.

The first `LOD3` dropped the canopies and every vent and was still 524, over
its ceiling. Boxing the wings brought it under, to 492. Merging the eight
stacked pairs then paid for keeping both exhausts and both canopies, at 488.

What fixes the floor of the later tiers is the openings: 37 at `LOD2`, 29 at
`LOD3`, each a flush quad at about 8 triangles in its wall.

Against comparable catalog assets:

- **The two-storey terraces** run 3,000-4,500 at `LOD0`, and the civic hall
  about 5,200.
- **This building's walls and openings** alone are about 1,500 at `LOD0`,
  less than the terraces, because its openings are plain brick reveals with
  no casings, sills or surrounds modelled.
- **The rest is the ladders.** That is also why `LOD2` sits closer to its
  ceiling than the other catalog assets do: every fourth rung is still 18
  rungs.

## LOD review

**Setup:**

- **Renderer:** `scripts/review_asset.py`, perspective, **1920 x 1080**,
  **50 degree vertical FOV**, 24 samples.
- **Distance:** measured along the view direction to the centre of the
  visible front or rear wall.
- **Views:** front (0 degrees, 12 degrees up), oblique (40 degrees,
  30 degrees up) and aerial (40 degrees, 45 degrees up).
- **Lights:** noon, and the sun reversed from behind (`reverse`). Emission
  off.

Every pair was judged at native size, then enlarged 2x to find what changed.
Renders are in `review/tehdas_2026_09_25/` (lod35, lod70, lod120, lod200).
The downpipes' switches were rendered again with them in, in
`review/downpipes_2026_09_25/` (after, lod120).

| Switch | Distance | Verdict |
| --- | --- | --- |
| `LOD0` → `LOD1` | 35 m | Indistinguishable at native size. Rung density halves, and the vents go from eight sides to six and the downpipes to four. |
| `LOD1` → `LOD2` | 70 m | Indistinguishable at native size. The openings go flat, whose 0.15-0.25 m reveals are about 2 px of shadow at this distance. Rung density halves again and the ladders lose their brackets. The three 0.16 m vents go, under 2 px wide, and the downpipes straighten: the swan-neck's 0.3 m kick and the shoe are each about 2 px, and the pipes still read as light lines down the wall. |
| `LOD2` → `LOD3` | 120 m | Three things go. The downpipes are the most visible: light lines about half a pixel wide on the darker brick. The ladders are faint half-pixel lines on the roof and one above the front eave. The two 0.3 m pipes are 2 x 6 px marks over the ridge in the front view. Side by side at native size each can be found, but none shows at a glance. Keeping the downpipes would cost about 70 triangles, and the tier has 12 to spare. The boxed wings and the merged bays could not be told from `LOD2`'s. |
| `LOD3` alone | 200 m | Silhouette, roofline, both wings, the porch on its pillars, the window rhythm, the canopy and the stair strip all read. |

Each switch was reworked once after a comparison showed something visibly
vanishing:

- At 35 m the ladders first dropped to bare rails. The rungs' rhythm and
  their shadows on the sheet had read, and without them the ladders stopped
  being ladders.
- At 70 m the ladders first went entirely. From above the roof ladder is
  still a hatched strip there, and the wall ladder a line over the eave. The
  0.3 m pipes had also gone, 3.5 x 10 px over the ridge.
- At 120 m the exhausts and both canopies first went.

Each such feature now carries on, thinned where it could be (`ladder_mode()`,
`vent_sides()`, `canopy_kept()`), under CLAUDE.md's rule to keep a feature or
move the switch.

These are the **authoring** review's distances, at the review camera above:
a starting point for a consumer's switch distances, not a measurement.
**Pending:** runtime acceptance in a representative consumer scene. That
needs visible instance counts per tier, hardware, resolution, FOV, shadow
settings and frame times.

## Interior geometry

Sampled hidden-surface test (`scripts/validate_asset.py`, 40 rays per face):

| Tier | Hidden | Where |
| --- | --- | --- |
| `LOD0` | 76 / 3780 (2.0 %) | ladder rungs and downpipe backs, below |
| `LOD1` | 48 / 2692 (1.8 %) | the same, fewer rungs |
| `LOD2` | 27 / 1288 (2.1 %) | the same |
| `LOD3` | 0 / 488 | - |

Every candidate was located and inspected by face, and none is buried:

- **The roof ladder's rung undersides**, 3 cm above the sheet.
- **The wall ladders' rung backs**, facing a wall 0.2-0.6 m away.
- **The hung rail's bottom end.**
- **The downpipes' backs**, facing the brick 3 cm away. Every sampled ray
  from them heads toward the wall and meets it, however wide the gap. They
  are seen only at a grazing angle along the wall. This is up to 2.7 m² of
  vertical surface at `LOD2`, all of it pipe.

All four are exterior surface in gaps too narrow for a sampled ray to escape.
Nothing is a partition or a duplicate surface. The construction is a union
of closed solids, which has no interior by definition.

Closure faces kept deliberately:

- the floors of the three wall rings, at z = 0 and facing the ground;
- the pillars' feet;
- the rails' feet at the ground.

Welded manifold check on every exported tier: **0 boundary edges, 0 edges
with more than two faces, 0 loose vertices or edges**.

## Known simplifications

- **The gutter is painted, the downpipes modelled.** The gutter is a
  half-round painted on the eave fascia. The pipes' outlets rise into the
  soffit just inside it, and there is no modelled joint between them.
- **Downpipe clips are painted rings, and the pipes stand on nothing.** Each
  pipe's shoe discharges onto open ground; there are no splash plates or
  drains.
- **The window frames' mullions, sashes and glazing beads, the loading door's
  sections, the roof's ribs and ridge cap, the gutter, and the felt's roll
  seams are all painted.** Each is under the relief threshold and repeats.
- **Openings have plain brick reveals, no lintels.** The head reveal is brick
  unrolled round the corner, and the sill is a flat metal flashing patch.
- **The wall ladder has no safety hoop**, and the ladders' tops are straight
  rails 1 m past what they reach rather than curved grab rails.
- **No ridge walkway, snow guards or roof hatches.** The roof ladder ends
  0.45 m short of the ridge. CLAUDE.md's roof safety rule asks for a walkway
  only to serviced items, and the slopes carry only plain vent pipes, so the
  wall and roof ladders are the whole kit here.
- **Every ribbon window is two fixed lights between two casements**,
  identical on every wall. The upper floor carries no variation between
  rooms.
- **The porch is open front and back** as a passage. Nothing closes its sides
  but the wings' set-in east faces.

## Texture set

Seven unique PNGs, all **1024 x 1024, RGB, 8-bit, lossless**, no alpha:

| File | Colour space | Shared across |
| --- | --- | --- |
| `tehdas_brick_gable_albedo_red_brick.png` | sRGB | all four tiers |
| `tehdas_brick_gable_albedo_brown_brick.png` | sRGB | all four tiers |
| `tehdas_brick_gable_albedo_yellow_brick.png` | sRGB | all four tiers |
| `tehdas_brick_gable_albedo_grey_brick.png` | sRGB | all four tiers |
| `tehdas_brick_gable_orm.png` | Non-Color | all tiers, all variants |
| `tehdas_brick_gable_normal.png` | Non-Color | all tiers, all variants |
| `tehdas_brick_gable_emission.png` | sRGB | all tiers, all variants |

About 2.8 MB on disk. As uncompressed RGBA8 with a full mip chain each is
5.6 MB: 22 MB for one colour's set of four maps, 39 MB with all four colours
resident. The consumer owns GPU compression.

### Layout

A trim sheet. Five bands run the full width and tile in U:

| Band | Rows | Covers |
| --- | --- | --- |
| brick | 0-456 | z 0 ... 7.125 m, concrete plinth in the bottom 24 rows |
| window | 462-552 | a ribbon window, sill to head, in 2 m cells |
| roof | 558-630 | the profiled sheet, eave edge to ridge |
| eave | 636-652 | the eave fascia with its gutter |
| flash | 658-682 | 0.375 m of folded flashing |

Everything singular gets a region above the bands (rows 690-1020):

- the entrance screen, the glazed door, the service door and the loading door;
- the stair glazing and one face of a pillar;
- the felt deck, and for `LOD3` the two wing lids, the two-storey window
  bay and the stair column;
- a vent pipe's side and its open end;
- eleven flat patches.

`check_regions()` asserts that no two regions overlap, that none runs off the
sheet or into the bands, and that each opening's region matches its opening
to within 2 cm. `check_bands()` asserts that no band holds an id it should
not.

### The brick band and the gables

The brick band stops at the wall head. The gable triangles above `Z_GABLE`
(6.75 m) sample the same band `GABLE_SHIFT` (3.75 m, 240 rows, 48 courses)
lower, so the bond and its parity run on across the line. The brick's tone
hash repeats every 48 courses too, so a brick cut by the line keeps one tone.
That saves about 160 rows of brick. Nothing that follows height is painted near the
band's top, because a sheltered dust line under the eave would also land
halfway up each gable.

### The window band

Every ribbon window samples the one band from its start and is a whole
number of 2 m cells (128 px). A cell is:

- a 1.19 m fixed light;
- a 4 px mullion;
- a 0.625 m side-hung casement whose sash stands 15 mm proud of the frame.

The cells alternate, casement first and then casement last, so a 4 m window
reads casement, light, light, casement: the vents at its ends, the fixed
lights together in the middle. A 2 m window has its casement at its left
jamb. The pair, 256 px, divides the atlas width, so the band tiles. The frame
at a cell edge is split 4 px each side, so a window's jamb frame and a doubled
mullion between two cells both come for free.

### Texel density

64 texels/metre on every wall, window, door and the pillars. Deliberate local
deviations:

| Surface | px/m | Why |
| --- | --- | --- |
| roof, up the slope | 10.5 | 64 along the ribs, which vary in U only; V carries the eave drip, the ridge cap and the weathering's runs. Anisotropic by design. |
| loading door | 40 | a plain sectional door, 4 x 3.75 m |
| felt deck | 10 | flat membrane seen from above |
| `LOD3` wing lids | 8 | seen past 120 m only |
| `LOD3` window bay and stair column | 16 | seen past 120 m only; a mip-like copy of the bands and regions they stand for |
| vent pipe sides | 64 up, 170-520 round | each of a pipe's faces takes the whole 32 px width |

### Relief

The normal map is derived from painted height by `atlas.normal_map()`,
OpenGL convention, at physical heights:

- brick faces 6 mm proud of the mortar;
- window frames 30 mm proud of the glass, casement sashes 45 mm;
- door frames 20 mm; door stiles and rails 40 mm; handles 50 mm;
- the roof's trapezoid ribs 35 mm, with 8 mm stiffeners;
- the gutter's 70 mm half-round;
- the flashing's 10 mm folds;
- the loading door's 8 mm section joints, at 40/64 scale;
- the pillar's arris chamfers and pour joints.

Glass, the felt and the patches stay flat.

### Supersampling, padding and filtering

- **Supersampling:** 4 x 4 samples per pixel (`atlas.SS`), box-filtered in
  linear light.
- **Gutters:** bands are 4 rows apart, each painting 2 of its own rows into
  the gap. Regions keep at least a 4 px gutter.
- **Padding:** `atlas.pad()` fills every unclaimed texel from the nearest
  region's edge in every channel.
- **Periodic in U:** the brick bond at 16 px, the window cells at 128, the
  roof ribs at 32, the gutter hangers at 64 and the flashing laps at 128.
- **Mip review** (`scripts/review_atlas_mips.py` and `review_asset.py
  --texture-dir`):
  - **Mip 3 (8x) on `LOD2` at 75 m**, face-on and grazing: no roof or trim
    colour leaks into the walls, and no dark seams at the eave, the fascias
    or the window heads. The windows stay dark in light frames, and the
    brick stays one tone.
  - **Mip 4 (16x) on `LOD3` at 125 m**, oblique and grazing: the walls, roof,
    decks and pillars hold, but the merged window bays read as pale boxes.
    That is the test's own limit. It forces one mip on the whole sheet, and
    the bay region is painted at a quarter of the walls' density, so a real
    sampler, which picks the level from each quad's UV derivatives, reads it
    about two levels finer than the walls round it. At full resolution the
    200 m renders show no bays at all.
  - Four rows of padding cannot survive an arbitrarily coarse mip, and that
    is accepted here rather than engineered round.
  - **Pending:** the same check under the consumer's own sampler and shipped
    mipmaps.

### Weathering

- **Placement:** `facade_atlas.py`'s `weather()` places `scripts/weathering.py`'s
  fields at the catalog's moderate level.
- **The brick band:** soil and algae on the plinth, splash-back and a little
  salt bloom on the brick above it, faint rain runs, and dust in the joints
  from the cavity.
- **Roof and flashing:** runs down the roof, more dirt toward the gutter, the
  paint chalking toward the ridge; dirt in the gutter; runs down the eave
  fascia and the flashings from their top edges.
- **Doors and details:**
  - dirt standing on the ribbon windows' bottom rail;
  - dirt on the thresholds, and grime round the service door's handle;
  - kicked-up dirt across the loading door's foot and rust at its guides;
  - splash on the pillars;
  - dirt where the felt ponds;
  - soot and rust runs down the vent pipes.
- **Glass never weathers.**

## Glazing treatment

- Measured glass, all four variants: mean **sRGB 55**, linear **0.034**.
  Against the 99th percentile of the rest of the sheet it is **0.24x**
  (grey), **0.25x** (red), **0.28x** (yellow) and **0.32x** (brown). The frames are white
  on red and grey brick and dark on brown and yellow, so the glass is darker
  than its frame in every colour.
- Roughness **0.08**, metallic **0** (`glazing.ROUGHNESS`).
- Painted by `scripts/glazing.py`'s `rooms()` on the finished albedo: each
  light of every ribbon window, the stair glazing, the entrance screen and
  the glazed door is its own room. No brief-driven departure.

## Variant list

Four colours on the same geometry, UVs and LOD chain, differing only in the
albedo:

| Variant | Meaning |
| --- | --- |
| `red_brick` | default; red facing brick with light mortar, white frames, light grey roof and flashing, grey doors |
| `brown_brick` | dark brown brick, dark brown frames, near-black roof and flashing |
| `yellow_brick` | pale yellow brick, dark grey frames, dark grey roof |
| `grey_brick` | grey-buff brick, white frames, mid-grey roof, light flashing |

A 42 m two-storey brick block with wings is at the upper end of low-rise and
built in one uniform skin. That makes it CLAUDE.md's "alternative uniform
brick on the shared mesh" case, not a multicoloured building. The brick
changes, and the frames, roof, flashing, doors and loading door move with it
so each colour stays one coherent treatment. The felt, glass, concrete,
galvanised ladders and black pipes are fixed. Four sits inside the 3-6 band.

## Night lighting

`tehdas_brick_gable_emission.png` is shared by every tier and colour.

- **Candidate glazing, neutral grey, each light the lit room behind it**
  (`glazing.night_rooms()`): every ribbon window, the stair glazing, both
  entrance screens and the stair door. Frames, brick, doors, the loading door,
  roofs and everything else are black. No sign or lamp is luminous; the brief
  has none.
- **Reference lit factor: linear (1.0, 0.88, 0.72).** Workshop and office
  floors are lit by fluorescent tubes. The catalog's warm residential default
  would misread them, so the value is the one `lahikauppa_corner` uses for
  its sales floor.
- **Default off:** `emissiveFactor` is `[0, 0, 0]` in all four tiers,
  verified in the GLB JSON, with the `emissiveTexture` binding intact.
- **Control scope:** one factor per placed building. Every ribbon window
  samples the same band, so **no window can be lit without the rest**, and
  the building reads as one lit works, not scattered rooms. The consumer owns
  intensity, colour and schedule.
- **`variants.png`:** all four colours at `LOD0`, a day row with emission off
  above a night row at the reference factor. Camera, framing, exposure and
  colour management are fixed between the rows. Cycles at 48 samples with
  denoising, seed 42; the night world is (0.24, 0.32, 0.50) at strength 0.08,
  with the sun at 0.12, tinted (0.48, 0.62, 1.0).
- **Light spill:** the light on the ground in the night row is Cycles' bounce
  in the preview scene and is **simulated**; spill is the consumer's.
- **Pending in the consumer:** off/on behaviour on the reimported tiers,
  oblique and distant filtering, and LOD switches under emission.

## Export

`.glb` + external PNGs, exported by `scripts/asset_build.py` with
`export_format='GLB'`, `use_selection=True`, `export_yup=True`,
`export_apply=True`, `export_keep_originals=True`, `export_cameras=False`,
`export_lights=False`. The material is exported lit and each file's emission
factor rewritten to zero; `strip_embedded_images()` removes the placeholder
`bufferView` keep-originals leaves on each image.

Traced in the GLB JSON of **all four tiers**:

- one mesh, one primitive, one material;
- `baseColorTexture` → the default albedo (`..._albedo_red_brick.png`),
  UV set 0;
- `metallicRoughnessTexture` → `..._orm.png`, factors 1 and 1;
- `occlusionTexture` → `..._orm.png`, strength 1;
- `normalTexture` → `..._normal.png`, scale 1, no tangents exported (the
  consumer generates MikkTSpace);
- `emissiveTexture` → `..._emission.png`, `emissiveFactor [0, 0, 0]`;
- `alphaMode` OPAQUE, not double-sided;
- every image a `uri` and no `bufferView`.

Pivot: ground level, the centre of the plan's bounding box, taken from `LOD0`
and applied to every tier. `build_all()` fails if any tier's extents differ.
The validator confirms min z = 0 and a centred footprint on all four. Front
faces `-Y` in Blender; `+Y`-up, `+X`-right on export.

Rebuild:

```bash
cd buildings/industrial/tehdas_brick_gable
python3 facade_atlas.py export                          # every PNG in export/
blender --background source.blend --python build.py     # tiers, GLBs, preview, variants
```

## Review status

Completed in this repository:

- `scripts/validate_asset.py`: no FAIL, no WARN.
- `check_layout()` and `check_regions()`/`check_bands()` pass on every build.
- **Views inspected:**
  - the six pre-export views: orthographic front, rear, east, west and top,
    and a raised three-quarter aerial off the front-east corner;
  - aerials off the other three corners;
  - eye views at the main entrance, the porch and the west gable;
  - close-ups of the ladders and of the roof and its vents.

  All of these at every tier on the final build, in
  `review/downpipes_2026_09_25/views/`, with close-ups of a swan-neck, a shoe
  and a wing pipe at `LOD0`-`LOD2`.
- The weld findings in Construction, traced to the vertex pairs and fixed in
  the geometry, with the raw and welded unions compared.
- Hidden-surface candidates located face by face (Interior geometry).
- GLB bindings and image sources traced on all four tiers (Export).
- Glazing measured against Style Direction's band, all four colours.
- Palette:
  - muted red, brown, yellow and grey brick;
  - white or dark frames, light or dark grey steel roofs;
  - dark felt, light concrete, galvanised ladders, black pipes.

  No saturated colour, and no lighting or reflection in any albedo.
- LOD pairs at 35, 70 and 120 m and `LOD3` at 200 m, front, oblique and
  aerial, under noon and a reversed sun (LOD review). Each switch was reworked
  once after the comparison showed something visibly vanishing.
- The day cycle (morning, noon, dusk, and night with emission on) on `LOD0`,
  at 66.6 m.
- Mip-stress renders: mip 3 on `LOD2` at 75 m, and mip 4 on `LOD3` at 125 m
  (Texture set).
- The downpipes, as CLAUDE.md asks of a change to a finished asset: the
  folder snapshotted into `review/downpipes_2026_09_25/` first, the same
  `review_asset.py` set rendered from the snapshot and from the change, and
  `review_compare.py` sheets made of the two. The sets were tiers 0-2 at 35
  and 70 m and `LOD0` at 20 m, front, oblique, rear and west, under noon.
  The pipes are the only difference: mean absolute difference 0.04-0.33 /
  255, and the enlarged centre crops identical. The weld was rechecked on
  every tier: no vertex pair under 0.1 mm, and the weld changes nothing.
- The move of the pipe code into the shared `scripts/downpipes.py`,
  compared the same way from a fresh snapshot in
  `review/downpipes_shared_2026_09_25/`: `LOD0` at 20 m from all four sides
  and the oblique, tiers 0-2 at 35 and 70 m from the front, oblique and rear,
  and tiers 2-3 at 120 m from the front and oblique, under noon. The triangle
  counts are unchanged and `LOD3`, which has no pipes, is the same triangles.
  Elsewhere only the triangulation moved: the pipes' own quads split along
  their other diagonal, since each ring now starts on another corner, and at
  `LOD0` the eave soffits round the pipes, whose buried tops now reach 2 cm
  higher. The renders differ by at most 0.01 / 255 on average, the largest
  change being the shoes' mouths, which now take the gutter's colour instead
  of the coping patch's. `scripts/validate_asset.py` still reports no
  failures or warnings.
- The move of the ladder code into the shared `scripts/roof_safety.py`,
  compared the same way from a fresh snapshot in
  `review/roof_safety_2026_09_25/tehdas_brick_gable/`: every tier, front,
  oblique, aerial and rear at 20 and 60 m, under noon. The triangle counts
  are unchanged and every render is identical (mean absolute difference
  0.00 / 255 in every view). `scripts/validate_asset.py` still reports no
  failures or warnings.

Pending, outside this repository:

- Consumer import, LOD switching and runtime emission control.
- Consumer-side mipmap and anisotropic filtering.
- Performance in a representative scene.

## Tooling versions

- **Blender 5.3.0** (hash `02f0899d78e3`, built 2026-11-11) for the current
  export, recorded as a known-good diagnostic, not a pin. `build.py` asserts
  the 5.3 floor and the presence of every glTF exporter flag it sets.
  `source.blend` is saved by 5.3.0. The asset was built and reviewed on
  Blender 5.2.2 LTS (hash `d13f752e3b9c`).
- **Blender MCP addon: not used for this asset.** It was built and reviewed
  headless:
  - `blender --background` with `build.py`'s `render_views()`;
  - `scripts/review_asset.py`;
  - `scripts/validate_asset.py`.

  Every render was inspected and fed back into the massing and the atlas.
- **CPython 3.14.7 with numpy 2.5.3, scipy 1.18.1 and Pillow 12.3.0** for the
  texture bake: `python3 facade_atlas.py export`.

## Revision log

- **2026-11-22 — re-exported on Blender 5.3.0.** The four tiers were
  re-exported from an unchanged build on the current toolchain. Geometry, UVs,
  triangle counts and bounds are unchanged; `LOD0` and `LOD1` list the same
  vertices and triangles in another order, and every tier is 1488 bytes
  larger in the image placeholder buffer views. `source.blend`, `preview.png`,
  `variants.png` and the facts sidecar were rewritten; the textures were not
  rebaked.
