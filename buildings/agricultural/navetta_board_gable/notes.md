# navetta_board_gable

## Style brief

A composite mid-century Finnish farm barn (*navetta*) of the kind found on a
small post-war grain and dairy farm, in the same countryside as the
rintamamiestalo houses. It is a long, low byre under a 30° gable roof, and
the roof space is the hay loft. The walls are red-ochre vertical
board-and-batten on a low cast-concrete plinth, with white corner boards,
white casings round every opening, white fascias and barge boards, and a
dark trapezoidal profiled steel roof. A half-round galvanised gutter runs
along each eave, with one downpipe from each, and a tubular snow guard
(*lumieste*) runs along each slope just above the eave, all three in the same
galvanised steel as the gutters of the farm's grain dryer and machine shed.

The long front faces the yard. It carries a pair of big braced board doors on
a concrete ramp, a row of four small byre windows, and a plank pedestrian door
at the east end on its own small ramp. The east gable carries the loft hatch
high up, with one byre window below it. The west gable carries one byre window
and a louvred loft vent. The rear wall has four byre windows and a service
door, centred, on a third ramp. The doors are boarded leaves painted in the
wall colour, with white frames, diagonal braces and black strap hinges.

The barn has no chimney, no roof plant and no fences, ground or base slab. It is meant as farmyard filler, placed beside the catalog's
post-war houses, with three colours for variety.

## Category and secondary use

`buildings/agricultural/`. No secondary use: the byre is the ground floor and
the loft is hay storage in the roof space.

## Hero/landmark status

**No.** Ordinary budgets and a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Walls | 16.00 × 9.00 m |
| Overall, with the 0.35 m rakes, the 0.45 m eaves and the ramps (2.20 m at the front, 1.40 m at the rear) | 16.70 × 12.60 m |

Heights: the plinth top and byre floor are at 0.40 m. The wall meets the soffit
at 3.80 m, the fascia bottom is at 3.54 m, and the ridge is at 6.71 m.

The pivot is at ground level, centred on the bounding box of the plan,
overhangs and ramps included. That puts it 0.40 m in front of the walls' centre.
It is taken from `LOD0` and applied to every tier. Every tier keeps all three
ramps and the full roof, so the extents never change.

## Story height

**One storey: 3.40 m**, from the 0.40 m byre floor on the plinth to the eave at
3.80 m. The extra 0.1–0.4 m over the 3.0–3.3 m standard is the type's: a byre
wall is tall enough to take the 3.0 m vehicle doors under the eave with their
casing and drip cap. The loft above is roof space for hay, reached through the
gable hatch. It is not an occupied storey, so the facts sidecar lists one
storey of 144 m².

## Door leaf height

- **Pedestrian door (front, east end) and service door (rear): 0.95 × 2.10 m**,
  plank leaves with no transom. The casing adds 0.19 m above the leaf.
- **Vehicle doors: a pair, 3.20 × 3.00 m overall** (two 1.60 m leaves), with no
  transom. They are vehicle doors, not leaves at human scale; the 2.10 m
  pedestrian door beside them carries the scale.
- **Loft hatch: a pair, 1.20 × 1.40 m**, threshold at 4.05 m in the east gable,
  just above the gable belt board. Nobody reaches it from the ground; hay goes
  in through it from a loader or a wagon.

All ground-floor thresholds are at the 0.40 m floor. Each door is reached by a
concrete ramp that meets the wall 2 cm under the threshold. There are no steps,
so there are no handrails.

## Window sills

**Byre windows: sill 1.30 m above the ground, head 2.00 m**, 0.90 m above the
byre floor. That is below the pedestrian door's 2.50 m head, as small high
byre windows usually are. The sill is chest height from inside, out of reach
of the animals. All eleven windows are the same 1.00 × 0.70 m opening, on the
long walls and on both gables. Each gable has one window, centred on the
ground storey, per Style Direction's rule for short walls. The west gable's
loft vent (0.60 × 0.40 m, louvred, sill at 5.25 m) is not a window.

## Eave overhang

| Where | Projection |
| --- | --- |
| Eaves (long walls) | **0.45 m** |
| Rakes (gable ends) | 0.35 m |

Both are within 0.3–0.6 m. The soffits slope with the rafters, as the
underside of the roof slab. The overhangs are kept at every tier.

The eave fascias carry a painted half-round gutter across their top 0.14 m,
under the sheet's drip edge, so the white board shows below it. The rakes
have no gutter.

## Construction

`build.py` builds up to seven closed solids and unions them with Blender's
exact boolean (`asset_build.union`):

- the body: a wall ring capped by a buried floor and a roof-shaped lid;
- the roof slab;
- three ramps;
- two downpipes (`scripts/downpipes.py`).

The wall ring rises 0.1 m into the roof slab. The union trims the walls exactly
where the soffits meet them and removes the buried parts of the slab, the
ramps and the pipes' tops, so the result is the boundary of one empty volume.

The mesh kit is the catalog's shared `scripts/shell_build.py`: walls are
filled as polygons with holes (`fill_region()`), openings recessed with
`recess()`, and the body closed by `close_solid()`, which walks the rim in
edge-index order, so rebuilds are deterministic. Every vertex on a shared
edge is a corner of both faces. The gables hand over from the S1 board band to the S2 band at
the eave height, behind a white belt board.

Authored parameters, which the tiers derive from:

- walls 16.0 × 9.0 m, with the ridge along X;
- a 30° pitch;
- eave 3.80 m;
- plinth 0.40 m;
- eave overhang 0.45 m, rake overhang 0.35 m;
- a slab 0.3125 m thick, the fascia height;
- the opening table in `facade_atlas.py`;
- the elevation lists (`MAIN_WALLS`) in `build.py`.

Openings at `LOD0` are recessed 0.12 m with reveals, and closed by their leaf
or glass plane (the vent 0.08 m). Detached farm buildings are seen from every
side, so every opening on all four elevations is cut.

**Ramps.** Each ramp is a concrete wedge from 0.38 m at the wall down to the
ground: 4.00 × 2.20 m under the vehicle doors, 1.60 × 1.40 m under the
pedestrian and service doors. Its back runs 5 cm into the wall. The top stops
2 cm under the threshold, so it never lies in the plane of a door recess's
floor. The sloping top samples the atlas's `RAMP` region at true scale, U
across the ramp and V up the slope from its foot; the cheeks sample the
plinth's rows of S1 by height, also at true scale.

`check_layout()` asserts, before building:

- no opening overlaps another or a corner board;
- no opening runs under a soffit or a rake;
- no window straddles the plinth top;
- nothing in a gable meets the belt board;
- the apex fits the S2 band;
- the roof slope matches the atlas;
- every ramp is wider than the casing of the door it serves, and its top
  fits the `RAMP` region at true scale;
- each downpipe is clear of the corners, of every opening's casing on its
  wall and of the ramps there (`downpipes.problems()`).

### Gutters and downpipes

The gutters are painted on the eave fascias (Texture set); the downpipes are
modelled with `scripts/downpipes.py`, one from each eave at diagonally
opposite corners, so each gable end shows one:

| Pipe | Wall | Along the wall | Nearest neighbour |
| --- | --- | --- | --- |
| front | front (−Y) | s 15.75 m, x = 7.75 m (east end) | the plank door's ramp, 0.35 m away; its casing 0.55 m |
| rear | rear (+Y) | s 15.75 m, x = −7.75 m (west end) | the west byre window's casing, 1.53 m away |

Each is `DP.eave_pipe()` on the 0.45 m eave at the 30° pitch: a 0.1 m
pipe 0.03 m off the boards, leaving the soffit on a swan-neck just inside the
fascia and ending in a shoe 0.2 m above the ground. Its sides sample the
gutter's middle rows (`PIPE_STRIP`), so it takes the gutter's colour in every
variant, and the gutter's hangers read as its clips. The pipes stay inside the
rakes, the eaves and the ramps, so they do not change the extents or the pivot.

### Snow guard

A two-tube snow guard runs the full length of both slopes, 0.60 m up the
slope from the eave's edge, just inside the wall line. It is painted in the
roof band (Texture set), not modelled: tubes about 30 mm across a few
centimetres over the sheet are relief, far under the 0.25 m threshold, and
the roof band is a full-width tiling band that both slopes sample, so one
painted guard lands on both.

### No chimney or roof safety kit

There is no chimney, vent stack or roof plant, so nothing on the 30° roof is
serviced from it. CLAUDE.md asks for the wall ladder, roof ladder and walkway
only where a roof steeper than 1:8 carries such an item, so this barn has no
roof safety kit. The snow guard is not a serviced item.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 756 | 12,000 | casing ring, reveals and closing plane on all 15 openings (vent flush); corner-board columns; roof slab; three ramps; two eight-sided downpipes with swan-neck and shoe (164 together) |
| `LOD1` | 536 | 4,000 | each opening becomes one recess the size of its casing, the casing painted on the recessed plane; the pipes four-sided, still bent (84) |
| `LOD2` | 266 | 1,500 | openings flush, the casing rect a quad in the wall; the loft vent dropped; coplanar boolean subdivisions dissolved (UV seams kept); the pipes straight and four-sided (34) |
| `LOD3` | 262 | 500 | `LOD2`'s body; the pipes straight and three-sided (30) |

The downpipes follow `downpipes.MODES` on every tier; no tier drops them.
The gutters and the snow guard are texture and cost nothing.

The counts sit far under the ceilings, and well under the 800–2000 the brief
expected. This is correct, not something to pad. The barn is one box under one
gable roof, with no porch, chimney or roof kit, and two downpipes. The walls are
polygons with holes rather than grids. All the shallow detail is texture: the
battens, the braces, the hinges, the sashes and the profiled sheet. A
rintamamiestalo without its downpipes, roof kit and handrails comes to about
900 at `LOD0`. This barn has fewer kinds of solid than that, and a longer, emptier wall.

**`LOD3` is `LOD2` but for the pipes.** At `LOD2` every opening is already
one flush quad. The only further cuts would be the windows, the doors or the
ramps. The
windows and doors carry the window rhythm and the white casings, which
Appearance Across LODs asks every tier to keep: a byre window is about
12 × 9 px at 120 m. The ramps set the bounds and the pivot. So the fourth tier
ships the third's body rather than inventing a reduction, with the pipes one
side thinner, as `downpipes.MODES` has it.

## LOD review

### The consumer's switches

The consumer switches by screen size: adjacent tiers are judged at 1.8, 4 and
8 times the largest bounds dimension (16.70 m), so **30, 67 and 134 m**, with
its camera, 75° vertical FOV at 1920×1080, distance from the camera to the
centre of `LOD0`'s bounds. Rendered on reimported GLBs (Cycles 24 samples,
AgX, the `review_asset.py` scene with the lens swapped): front, corner (45°
round, 25° up), eye level and rear at noon, and the corner at night with the
reference emission on, each pair side by side with its difference.

- **30 m, `LOD0`/`LOD1`:** the casing ring and reveals against one
  casing-sized recess: the head shadow sits a few pixels higher on `LOD1`,
  which does not read as a change.
- **67 m, `LOD1`/`LOD2`:** the recesses go flush; window rhythm, white
  casings, braces and dark glass hold, and the loft vent (about 4 px) goes
  unnoticed.
- **134 m, `LOD2`/`LOD3`:** identical but for the pipes' thinning (mean
  difference 0.04 / 255).
- At night the lit panes match across every pair.

Nothing pops at any of the three. Rendered for the 2026-11-22 palette pass
before and after with identical settings (`review/older_audit_2026_11_22/
fix_agricultural/navetta_board_gable/`, local, git-ignored); the tier
differences are unchanged by it.

### Authoring review

The authoring switch distances are the catalog defaults: 35, 70 and 120 m. Reviewed on
reimported GLBs with `scripts/review_asset.py`: perspective 1920×1080, 50°
vertical FOV, Cycles 16–24 samples with denoising, AgX/None, exposure 0.
Distances are measured along the view direction to the centre of the visible
front or rear wall. Renders are in `review/farm_2026_11_20/navetta_board_gable/`
(local, git-ignored).

- **35 m switch** (`switch35/`): `LOD0` against `LOD1` at 30 and 40 m, front,
  oblique and rear, under noon and reverse sun. The ring-and-reveal and the
  single casing-sized recess cannot be told apart at 40 m. At 30 m, the
  shadow under the casing's head becomes a slightly wider shadow at the top of the
  recess.
- **70 m switch** (`switch70/`): `LOD1` against `LOD2` at 65 and 75 m, front,
  oblique and aerial, under noon and reverse sun. The flush openings lose the
  recess's 1–2 px shadow line. Window rhythm, white casings, door braces and the
  dark glass all hold. The loft vent, about 4 px, goes without being noticed.
- **120 m switch** (`switch120/`): `LOD0`, `LOD2` and `LOD3` at 115 and 125 m,
  front and oblique, under noon. All three are indistinguishable.
- **Mip stress** (`mip0/`, `mip4/`): `LOD2` and `LOD3` at 75 and 125 m, front,
  grazing (75° azimuth) and aerial, under noon, against whole-atlas mip4 from
  `scripts/review_atlas_mips.py`. Mean absolute difference over the building
  is 4–6 / 255. The doors' braces blur into the leaf colour, and the casings,
  corner boards and fascias stay white with no colour leak from neighbouring
  regions. The roof's weathering blotches become broad cloudy patches under
  noon specular at mip4. The same patches are faintly visible on the base
  atlas, so this is the weathering's own pattern minified, not a leak.
- **Six views** (`views1/`): the orthographic front, rear, both gables and top,
  plus the 45° aerial, at `LOD0` and `LOD2`. These are the pre-export views,
  rendered by `build.py`'s `render_views()`.
- A close range at 12 m (`close/`), front, oblique and the east gable under
  noon and reverse sun. The battens read raised: a lit arris on the sun side
  and a shadow line on the other. The glass is darker than its casing. The
  2.10 m pedestrian door scales the 3.00 m pair beside it.

### Gutters, downpipes and snow guard (2026-11-20)

Rendered on reimported GLBs with `scripts/review_asset.py` before and after
the change, with identical settings, and paired with `scripts/review_compare.py`
(`review/farm_gutters_2026_11_20/navetta_board_gable/`, local, git-ignored):
`LOD0` and `LOD1` at 20 and 40 m (front, oblique, rear), `LOD2` and `LOD3`
at 70 and 120 m (oblique), under noon and reverse sun.

- The gutter reads as a round steel trough along each eave: a lit roll, a
  dark belly and a shadow line on the white board under it, with the hangers
  visible at 20 m. At 70 m it is a light grey line between the roof and
  the fascia (re-rendered at `LOD2`, 70 m, oblique and rear, noon, after
  the galvanised steel pass, `review/farm_gutter_colour_2026_11_20/far/`).
- Both downpipes read at 20 m with the swan-neck and shoe, standing off the
  boards with their own shadow. At 40 m each is a 3 px dark line beside the
  white corner board, the swan-neck no longer separable. At 70 and 120 m the
  straight pipes are a one-pixel line at the corner, or lost in its shadow.
- The snow guard reads as a light rail with brackets a short way up each
  slope at 20 m, and as a faint line at 40 m; past 70 m it is gone into the
  roof, as intended.
- Nothing else changed: walls, openings, roof and ramps match the before set.
- Since the 2026-11-20 galvanised steel pass the gutter, the downpipes and
  the snow guard are light galvanised grey in every variant, no longer the
  roof's dark steel; at 20 m they read the same as the dryer's and the
  machine shed's, and still read against the white fascia and each roof.

These renders are authoring evidence only. Runtime switching, filtering and
performance are pending in the consumer.

## Interior geometry

Measured with `scripts/validate_asset.py` on the exports:

| Tier | Hidden triangles | Share |
| --- | --- | --- |
| `LOD0` | 3 of 756 | 0.4 % |
| `LOD1` | 4 of 536 | 0.7 % |
| `LOD2` | 1 of 266 | 0.4 % |
| `LOD3` | 2 of 262 | 0.8 % |

No hidden face is vertical on any tier (0.0 m²). The candidates are slivers
where the wall tops meet the eave and rake soffits, plus a sliver of the rear
ramp's cheek at the wall. The downpipes add none: they stand clear of the
walls and only their tops, buried in the soffit, are removed by the union. Both are closure faces left by the union. Nothing
stands inside the barn, by construction. The floor and the roof-shaped lid of
the body are removed by the union, and the shell is the boundary of one
volume.

## Known simplifications

- **No interior and no openings into it.** Every door and the hatch is closed,
  painted on its recessed plane.
- **Board-and-batten, casings, door frames, braces, strap hinges, the drip
  flashing, drip caps, the belt board and the roof's ribs are texture.** All
  are well under the 0.25 m relief threshold. The height channel carries them
  at physical heights.
- **Reveals are 0.12 m**, shallower than masonry reveals, because a boarded
  timber wall sets its frames near the outside face.
- **The ramps are plain wedges.** Their tops are painted concrete at true
  scale (a faint broom finish, soil carried onto the foot), with no grooves
  modelled.
- **One window type, painted on two regions**, so the windows alternate between
  two rooms behind the glass, not one per window.
- **The gutters are painted**, on the eave fascias: a half-round trough with
  its roll in the height channel, its hangers every metre, and flat-cut ends
  at the rakes with no end caps or outlets modelled. The downpipes are
  modelled and run up into the soffit just inside the fascia.
- **The snow guard is painted** in the roof band: two tubes and their
  brackets as relief, with no geometry, so it has no silhouette over the
  eave and does not stand off the sheet in a grazing view.

## Texture set

| File | Space | Notes |
| --- | --- | --- |
| `_albedo_<variant>.png` ×3 | sRGB | 1024², 8-bit RGB, no alpha |
| `_orm.png` | Non-Color | 1024², R = AO, G = roughness, B = metallic; shared |
| `_normal.png` | Non-Color | 1024², OpenGL tangent space (+Y green up); shared |
| `_emission.png` | sRGB | 1024², neutral glazing mask; shared |

That is six unique 1024² textures: three albedos, one ORM, one normal map
and one emission mask.

- **Texel density is 64 px/m**, except the roof band, which is stretched up the
  slope (316 rows over 5.716 m, about 55 px/m; the ribs run down the slope, so
  nothing changes along it). The corner-board strip is also stretched along its
  length. The ramps' tops are at true scale in their own region (until
  2026-11-22 they sampled S1 by height, stretched 5.9:1 up the slope).
- **The atlas is a trim sheet** generated by `facade_atlas.py` through
  `scripts/atlas.py` at 4×4 supersampling, box-filtered in linear light. The
  bands run from the bottom of the atlas:

  | Band | Rows | Content |
  | --- | --- | --- |
  | S1 | 0–256 | The lower walls by height from the ground: concrete plinth with a formwork line, drip flashing, board-and-batten. |
  | S2 | 258–448 | The gables from the eave: white belt board, board-and-batten. |
  | ROOF | 452–772 | Trapezoidal profiled steel, with the snow guard 0.60 m up from the eave. |
  | FASCIA | 774–798 | White fascia board with the half-round gutter across its top 9 rows, under the sheet's drip edge. `PIPE_STRIP` is the gutter's middle five rows, which the downpipes sample. |
  | Unique | 802–1010 | The braced vehicle doors, the plank door, the loft hatch, two byre-window regions, the vent, the corner strip and flat patches. |
  | RAMP | 806–953, x 708–964 | The ramps' concrete tops, 4.00 × 2.30 m at 64 px/m: U across the ramp, V up the slope from its foot. Darker over the first 0.30 m, a faint broom finish across the slope, soil splash at the foot. |

  Every band spans the full width and tiles in U; RAMP is a region of its own. The battens (0.25 m), board
  tones and roof ribs (0.25 m) all repeat at periods that divide 1024.
  The gutter's hangers (1 m) and the snow guard's brackets (0.5 m, on every
  second rib) also divide 1024. `check_bands()` fails the bake on a stray id
  in a band; the roof band admits the guard's steel (`ID_GUTTER`) beside the
  sheet, and the fascia band the gutter's beside the board and the drip edge. `atlas.pad()` fills every gutter last, in every channel.
- **Relief heights**, used by `atlas.normal_map()`:
  - battens 20 mm, with arrises rounded over a pixel;
  - casings and the corner board 20 mm, sills 35 mm, sashes 12 mm;
  - door frame and brace boards 22 mm, strap hinges 28 mm, plank V-grooves
    3 mm deep;
  - roof ribs 22 mm on a trapezoid, with a 2 mm flute mid-pan and the ridge
    flashing;
  - the snow guard's tubes 45 mm, on a round profile, and its brackets 40 mm;
  - the gutter: a half-round roll of 70 mm radius, its hangers 4 mm proud;
  - the flashing and drip caps.

  Glass stays flat. The ridge flashing and the snow guard, which vary along
  the stretched V, are scaled by the band's px/m over 64.
- **Roughness / metallic:**

  | Surface | Roughness | Metallic |
  | --- | --- | --- |
  | Boards | 0.82 | 0 |
  | Trim | 0.62 | 0 |
  | Sashes | 0.52 | 0 |
  | Door leaves | 0.78 | 0 |
  | Glass | 0.08 | 0 |
  | Concrete | 0.90 | 0 |
  | Roof steel (coil-coated, painted) | 0.50 | 0 |
  | Flashing, drip caps (painted, the roof's colour) | 0.46 | 0 |
  | Gutter, downpipes, snow guard (galvanised) | 0.48 | 0.60 |
  | Hinge iron | 0.55 | 0.45 |
- **Albedo carries no directional light.** Shade holds only tone, wear and the
  occlusion that holds whatever the sun does: beside battens, under rails and
  drips, under the soffit, under the gutter and the snow guard's tubes.
- **Gutter and snow-guard colour.** Both are `ID_GUTTER`, galvanised steel at
  sRGB 134/137/137, roughness 0.48, metallic 0.60, the same in every variant
  and the same id, colour and surface as on `viljakuivuri_tower` and
  `konehalli_open_bays`, so the farm's rainwater goods match. The downpipes
  take it through `PIPE_STRIP`. Measured over `PIPE_STRIP` after weathering:
  mean sRGB 130/133/132 in all three albedos, roughness 0.50, metallic 0.55
  (ORM). The drip flashing, the drip caps and the roof's drip edge over the
  gutter stay `ID_METAL`, which follows each variant's roof colour (1.18 ×
  roof + 6).

### Weathering

Placed by `facade_atlas.py`'s `weather()` and drawn by `scripts/weathering.py`
at the catalog's moderate level:

- light grime everywhere;
- paint chalking on boards, trim and doors;
- faint rain wash on the boards;
- soil, splash specks and a green film at the plinth's foot;
- splash-back up the boards from the flashing;
- dust under the soffit from 3.3 m;
- on the roof, long runs, more dirt toward the eave, chalking toward the
  ridge, silt beside the ribs and specks of rust on the drip edge;
- light dust on the snow guard and rust at its brackets, debris held on the
  sheet above it and short rust runs on the sheet under the brackets;
- a dirty belly on the gutter and light runs down its face from the lip, the
  same treatment as the farm's other two gutters, and dirt and runs down the
  fascia board under it;
- dirt on the sills and head casings;
- hand grime and kicked-up dirt on the doors;
- splash at the corner boards' foot;
- soil carried onto the ramps' feet, fading up the slope;
- dust in the cavities beside the battens.

Glass never weathers. Everything that follows height sits in S1, S2, ROOF or
RAMP, whose V is height or slope.

## Glazing treatment

Panes are painted by `scripts/glazing.py`'s `rooms()` on the finished albedo.

| | |
| --- | --- |
| base colour | sRGB 50/54/57 (`glazing.BASE`) |
| measured over the glass mask, every variant | mean sRGB 55, linear 0.034 |
| relative to the trim around it | 0.25× (red, yellow), 0.37× (grey) |
| roughness / metallic | 0.08 / 0 |
| panes in the atlas | 2 |

Every window is the same plain byre window: one clear pane in a white sash,
with no glazing bars. It is painted on two atlas regions, `window` and
`window_b`, and `build.py` alternates them along each wall, so neighbouring
windows show different rooms. `rooms()` seeds each pane's room from the pane's
box in the atlas. With a single region, the first bake drew a dark room
(level 0.75 of `glazing.BASE`), which measured sRGB 40, under the 45–70
band. The two region origins were then chosen so both rooms land mid-band
(levels 1.09 and 1.06). That was a placement choice, not a change to the
treatment or its constants.

The grey variant's trim is weathered light grey, and the glass is well under
it. No brief-driven departure. Pending: calibration in the consumer's
lighting.

## Variant list

Three variants, `export/navetta_board_gable_albedo_<name>.png`, sharing one
ORM, normal map and emission mask:

| Variant | Boards | Trim | Doors | Roof |
| --- | --- | --- | --- | --- |
| `red_ochre` (default) | red ochre (punamulta), sRGB 122/52/42 | off-white 221/217/205 | red ochre, a shade darker, 112/48/39 | dark grey steel 54/56/58 |
| `grey_weathered` | unpainted boards gone silver-grey, 110/106/98 | weathered light grey, lighter than the boards but no white, 150/146/137 | silvered, 101/98/90 | dark grey steel 62/62/60 |
| `yellow_ochre` | yellow ochre, 184/148/86 | off-white 222/218/206 | yellow ochre, a shade darker, 169/136/79 | dark red-brown steel 75/51/45 |

The farmstead's three buildings (this barn, `viljakuivuri_tower` and
`konehalli_open_bays`) stand together, so they share these variant names and
these exact numbers: one name dresses the set.

This is the low-rise case: a farm building that differs in paint. The roof,
with the flashing and drip caps, shifts a little with the body colour. Glass,
concrete, hinge iron and the galvanised gutters, downpipes and snow guard
never change. Every `.glb` references the default (`red_ochre`) albedo. The other
variants are the same mesh with that one file swapped, since geometry and UVs
are identical by construction.

## Night lighting

- **Mask.** `navetta_board_gable_emission.png` is the neutral glazing mask: the
  byre windows' panes, each lit as a room by `glazing.night_rooms()` (its own
  level, a lamp glow and a falloff toward the floor, never under about a fifth).
  Everything else is black: the frames, walls, roof and every door, none of
  which is glazed. There are no signs or lamps.
- **Bindings.** All four GLBs bind the mask through `emissiveTexture` on UV0,
  with `emissiveFactor` `[0, 0, 0]` by default and the texture kept
  (`scripts/window_emission.py`, via `asset_build.export_all()`).
- **Reference lit factor.** Linear RGB `[1.0, 0.88, 0.72]`
  (`facade_atlas.LIT_FACTOR`, passed to `asset_build.Asset`), the warm white
  of the catalog's newer buildings; it tints `variants.png` and
  `source.blend` only, as the exports ship the factor at zero.
- **Control.** One building-wide control. The windows share two atlas regions,
  so individual windows cannot be switched. The consumer owns intensity,
  colour and schedule; a byre lit at night is a milking or feeding hour.
- **Preview.** `variants.png` is 1920×904, with all three colours at `LOD0`:
  a DAY row (emission off, catalog grey world, white sun at 3) above a NIGHT
  row (reference emission on, blue moon proxy at 0.12, blue world at 0.08).
  Camera, framing and exposure are fixed between the rows (Cycles, AgX/None,
  exposure 0), via `scripts/variant_previews.py`. Cycles simulates spill onto
  nearby surfaces in that sheet. Spill in the consumer depends on its lighting.
- **Day cycle.** The day cycle (`cycle/`: morning, noon, dusk, night with
  emission on) was rendered on the reimported `LOD0`.
- **Pending in the consumer:** import, material control, night exposure, spill
  and LOD switching at night.

## Export

```
python3 facade_atlas.py export                      # textures, all three variants
blender --background source.blend --python build.py  # meshes, preview, variants, sidecar
blender --background --python build.py -- facts      # the facts sidecar alone
```

Generate the textures first, because the UVs index into the atlas and the
renders read it. The first build ran from an empty scene
(`blender --background --python build.py`), which saves `source.blend`.
`facade_atlas.py` is the single source of the numbers the two scripts share.

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

- `baseColorTexture`: the `red_ochre` albedo;
- `metallicRoughnessTexture` and `occlusionTexture`: the ORM, through the
  `glTF Material Output` group;
- `normalTexture` at scale 1, through a tangent-space Normal Map node, with
  no tangents exported;
- `emissiveTexture`: the mask, with a zero factor.

All of them are on UV0 and reference external PNGs.

The facts sidecar `export/navetta_board_gable.model.json` records:

- the footprint, as the wall outline without the ramps and eaves;
- one storey at the 0.40 m floor, 144 m², and zero dwellings;
- four doors:

  | Door | Kind | Main |
  | --- | --- | --- |
  | Pedestrian door (`front`) | entrance | yes |
  | Vehicle pair (`big_doors`) | vehicle | no |
  | Rear door (`rear`) | service | no |
  | Loft hatch (`loft_hatch`) | balcony: `model_facts` defines it as any door not reachable from the ground, which the 4.05 m hatch is; `store` is for shed and store doors a person walks through | no |

**Preview.** `preview.png` uses the catalog's fixed camera orientation, lens,
sun and flat grey world (`asset_build.preview_studio()`), with the distance
fitted to the `LOD0` bounds and an 8 % margin. It shows `LOD0`, the default
variant, with the lights off.

## Review status

Checked here, in Blender:

- `scripts/validate_asset.py`: no failures.
  - All four tiers have uri-only external images, one opaque material slot and
    welded manifold topology.
  - The pivot is at ground level and centred.
  - Every tier binds emission on UV0, default off, and the normal map at
    scale 1.
  - Six 1024² RGB PNGs; normal vectors are unit length and face out.
  - The glass measures in band and darker than the trim.
  - The facts sidecar is consistent.
  - No warnings once the sidecar is written from a committed tree; after a
    rebuild from a working tree it warns `source.dirty` until
    `build.py -- facts` is rerun from the commit.
- `check_layout()` passes, downpipe placement included.
- The gutter, downpipe and snow-guard pass of 2026-11-20: before/after
  renders at 20–120 m (LOD review), `preview.png` and `variants.png` looked
  at. Bounds and pivot are unchanged on every tier (16.70 × 12.60 × 6.71 m,
  pivot 0.40 m in front of the walls' centre).
- The shared galvanised steel pass of 2026-11-20: a texture-only change.
  Triangle counts (756 / 536 / 266 / 262) and bounds match the sidecar; the
  normal map and emission mask are byte-identical. `PIPE_STRIP` measured as
  above (Texture set), within two sRGB levels of the other two farm
  buildings. Before/after renders at 20 m (`LOD0`, oblique and rear, noon) in
  `review/farm_gutter_colour_2026_11_20/` (local, git-ignored), compared side
  by side with the other two, and `variants.png` looked at.
- The six pre-export views at `LOD0` and `LOD2`.
- The tier comparisons at the three switches, the 12 m close range, the day
  cycle and the mip4 stress renders, all recorded under LOD review. Battens,
  laps on the casings and roof ribs read raised in direct sun, which confirms
  the OpenGL green channel.
- The variant sheet (`variants.png`): day and night for all three colours.
- The 2026-11-22 audit fixes: tier pairs at the consumer's 30 / 67 / 134 m
  and `LOD0` front and oblique at 20 and 35 m, each variant at 35 m, before
  and after with identical settings; the ramp close-up from the audit's
  camera; the three farm buildings' default and grey variants side by side.
  Triangle counts, bounds, pivot, footprint and doors unchanged.

Pending, and outside this repository:

- Consumer import, MikkTSpace tangent generation and the normal map at
  distance.
- Consumer mip and anisotropic filtering.
- LOD switching, night exposure and spill.
- Runtime performance.

## Tooling versions

- **Blender 5.3.0**, headless, which saved `source.blend`. The MCP addon was
  not used for this asset.
- **CPython 3.14.10** with numpy 2.5.5, scipy 1.18.1 and Pillow 13.0.0, for
  the texture export.

These are recorded as known-good markers, not requirements.

## Revision log

- **2026-11-22.** Audit fixes. One palette for the farmstead: the three
  variants now carry the same numbers on all three farm buildings, and
  `grey_weathered`'s trim is weathered light grey (150/146/137) over the
  boards (110/106/98) instead of darker than them. The roof steel and its
  flashings are dielectric (0.50 / 0 and 0.46 / 0, were part metallic). The
  reference night tint is (1.0, 0.88, 0.72). The ramps' tops map onto a new
  true-scale `RAMP` region instead of S1 stretched 5.9:1. The consumer's
  switch distances recorded; stale construction notes corrected. Geometry
  and counts unchanged.
- **2026-11-20.** The gutter, downpipes and snow guard moved off the
  roof-matched flashing steel (`ID_METAL`) onto a new `ID_GUTTER`: galvanised
  steel at sRGB 134/137/137, roughness 0.48, metallic 0.60, the same in every
  variant and on the farm's other two buildings. Gutter weathering is now the
  shared treatment (dirty belly, light runs on its face) and the snow guard
  gets light dust and rust at its brackets. Texture-only: geometry, UVs,
  relief heights, layout, the normal map and the emission mask are
  unchanged.
- **2026-11-20.** Added rainwater gutters, downpipes and a snow guard. A
  half-round steel gutter is painted across the top of both eave fascias,
  with `PIPE_STRIP` defined on its middle rows; two downpipes from
  `scripts/downpipes.py` are unioned at diagonally opposite corners (front
  east, rear west), per `downpipes.MODES` on every tier; a two-tube snow
  guard on brackets is painted 0.60 m up both slopes in the roof band. All
  three take the roof-matched flashing steel. Weathering added for the
  gutter's belly, the fascia under it and the snow guard. Triangles went
  from 592 / 452 / 232 / 232 to 756 / 536 / 266 / 262; bounds and pivot
  unchanged.
