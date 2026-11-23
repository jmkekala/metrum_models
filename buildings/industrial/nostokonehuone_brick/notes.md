# nostokonehuone_brick

## Style brief

A composite hoist house (*nostokonehuone*) of a small mid-century Nordic mine:
the engine hall that stands beside a headframe and houses the winding engine
and compressors. It is one tall, plainly industrial and well-built hall in red
facing brick on a cast concrete plinth, under a low standing-seam steel gable.
A cast concrete lintel band runs round the whole building at the window heads.

The gable end faces the front (-Y). It carries the steel machinery door,
through which the engine was brought in, between two tall windows mirrored
about it, with a louvred ventilation opening high in the gable above. Each
long wall carries four tall steel-framed multi-pane windows in a regular
2.75 m rhythm. The windows are the building's character. On the east wall the
front bay is the entrance: the window's steel frame brought down to the
ground round a plain steel leaf, with small panes above the transom. The rear
gable has one tall window and, high under the apex, the louvred slot the
winding ropes would pass through toward the headframe. No ropes or headframe
are modelled, since each piece is an independent model.

A painted half-round galvanised gutter runs along both eaves, with one
modelled downpipe from each at diagonally opposite corners, and a painted
two-tube snow guard runs just above each eave. Two plain vent pipes stand on
the slopes. There is no chimney and no roof plant, so there is no roof safety
kit.

## Category and secondary use

`buildings/industrial/`. No secondary use.

## Hero/landmark status

**No.** Ordinary budgets and a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Walls | 9.00 × 11.50 m |
| Overall, with the 0.40 m eaves and 0.30 m rakes | 9.80 × 12.10 m |

Heights: the plinth top is at 0.50 m, the window heads and the lintel band's
foot at 4.25 m, and the band's top at 4.5625 m. The long walls meet the soffit
at 5.75 m. The fascia's foot is at 5.59 m and the ridge at 7.80 m. The taller
vent pipe's top, at 7.90 m, sets the bounds.

The pivot is at ground level, centred on the plan's bounding box, which is
symmetric, so it is the walls' centre. It is taken from `LOD0` and applied to
every tier. Every tier keeps the whole roof and that vent, so the extents never
change.

Standing outside the footprint polygon but inside the bounds are the eave and
rake overhangs, the gutters painted on them, and the two downpipes. The
downpipes stand 0.03 m off the long walls on their clips, and their shoes kick
out 0.23 m at the foot.

## Story height

**One storey, 5.75 m** from the hall floor at ground level to the eave. This is
an authored departure from the 3.0–3.3 m standard, and it is the type's. A
winding-engine hall is one volume that has to clear the drum and engine and an
overhead crane over them. It is lit by tall windows that a 3 m storey could
not hold. There is no upper floor: the facts sidecar lists one storey of
103.5 m² at the ground, the area inside the outer wall faces.

## Door leaf height

- **Entrance (east wall, front bay): one steel leaf, 1.00 × 2.125 m clear**,
  the main door. A steel transom at 2.125–2.22 m separates the leaf from the
  small panes above it, which run to the lintel band at 4.25 m. The screen
  opening is 1.625 × 4.25 m, the windows' width. Solid steel side panels fill
  the 0.3 m each side of the leaf.
- **Machinery door (front gable): a pair of side-hung steel leaves, 3.19 ×
  3.66 m clear** inside a 6 px steel frame, in a 3.375 × 3.75 m opening. It is
  a vehicle door, not a leaf at human scale; the 2.125 m entrance leaf carries
  the scale. A row of three small lights near the head of each leaf is
  glazing, lit at night.

Both thresholds are at ground level, onto the hall floor, so there are no
steps or handrails. The entrance's 0.02 m floor slab (Construction) is a
floor finish, not a step.

## Window sills

**Every window: sill 1.25 m, head 4.25 m** (1.625 × 3.0 m). The head stands
under the concrete lintel band, which forms its soffit. The sill is below the
1.4 m chest-height line and below the entrance leaf's 2.125 m head. The opening
runs well above the head, as an engine hall's lighting does. There are eleven
windows: four on the west wall, three on the east (beside the entrance bay),
two flanking the machinery door, and one centred on the rear gable. Per Style
Direction the short walls get fewer, larger openings: the rear gable has one
window, and the entrance gable has the door between two mirrored windows.

The two louvres (1.5 × 0.75 m, sill 6.0 m, centred in each gable triangle) are
not windows. The front one is ventilation for the engine and compressors. The
rear one is the rope slot.

## Eave overhang

| Where | Projection |
| --- | --- |
| Eaves (long walls) | **0.40 m** |
| Rakes (gables) | 0.30 m |

Both are within 0.3–0.6 m. The soffits slope with the roof, as the underside
of the roof slab, in a light grey soffit patch. The eave fascias are folded
sheet in the roof's colour, with the galvanised gutter painted across their top
0.14 m. The rakes have no gutter.

## Construction

`build.py` builds up to five closed solids and unions them with Blender's
exact boolean (`asset_build.union`):

- the wall ring: four walls with their openings, capped by a buried floor and
  a lid split at the two gable apexes;
- the roof slab: a chevron section across X, extruded along the ridge (Y);
- two downpipes (`scripts/downpipes.py`);
- one or two vent pipes.

The walls run 0.125 m into the slab. The union trims them where the soffits
meet them and removes everything that ends up inside, so the result is the
boundary of one empty volume. Walls are triangulated as polygons with holes
(`tessellate_polygon`, with `_flip_slivers()` repairing collinear-hole
slivers). Every vertex on a shared edge is a corner of both faces. The
construction is `tehdas_brick_gable`'s, cut down to one volume with the ridge
turned along Y.

After the union every tier is welded at 0.1 mm. `LOD2`/`LOD3` are then
dissolved with `dissolve_limit` (UV and material seams kept). Every tier then
has its n-gons triangulated by ear clipping with the beauty rule. The union
returns each gable's brick as an n-gon that keeps the rake soffit's meeting
vertices in a straight line along its top. The exporter's own triangulation
joined three of them into a zero-area triangle on every tier, which the
validator reported as hidden on `LOD2`/`LOD3`. With the beauty triangulation
there are none, at the same triangle count.

The parameters every tier derives from live in `facade_atlas.py`:

- plan `HX`, `HY` = 4.5, 5.75;
- `Z_PLINTH` 0.5, `Z_SILL` 1.25, `WIN_H` 3.0, `Z_HEAD` 4.25, `Z_BAND` 4.5625,
  `Z_EAVE` 5.75, `Z_GABLE` 5.5, `Z_SLOT` 6.0;
- `TAN` 0.4 (21.8°), `ROOF_T` 0.25, `EAVE_OUT` 0.40, `RAKE_OUT` 0.30;
- the openings and their reveals (`OPENINGS`, `REVEAL`).

### Openings

At `LOD0`-`LOD2` each opening is cut into the brick with four cheeks and a
closing plane set back 0.20 m (windows, entrance screen), 0.25 m (machinery
door) or 0.15 m (louvres):

- The cheeks are the wall's own brick, unrolled round the corner so the
  coursing and the plinth run on into them.
- The sill is a concrete patch.
- A head under the lintel band is the band's concrete.
- The entrance screen's reveal stands on a concrete floor slab (Entrance
  floor slab below). The machinery door has no threshold cheek; the floor
  cap covers its recess.

At `LOD3` the windows and the entrance screen are the same rectangles,
flush; the two louvres and the machinery door stay recessed, since their
deep shade is how they read. `LOD2` keeps every recess: flattened there, at
the consumer's screen-size switch (about 48 m), the frames and glass
brightened, the gable louvre turned from a dark recess into a light patch
and the machinery door lightened (LOD review).

### Entrance floor slab

The entrance stands on the ground in a 0.20 m reveal that had no upward face
under it (the ring's floor cap faces down), so a consumer's terrain showed
inside: grass across the foot of the screen. The reveal is floored with a
concrete slab from the shared `scripts/door_floor.py` (`build_opening()`
calls `door_floor.recess()`; `outline_with_notches()` takes
`door_floor.notch()`):

| Entrance | Sidecar door | Slab, width x depth | Tiers |
| --- | --- | --- | --- |
| the entrance screen, east wall | `entrance` | 1.625 x 0.20 m | `LOD0`, `LOD1`, `LOD2` |

- **Top 0.02 m over the ground** (`door_floor.T`), clear of terrain at
  z = 0 and too low to read as a step.
- **A nosing on the wall plane** between the jambs. Nothing projects past
  the wall, so the bounds, the pivot, the footprint and the door's threshold
  in the sidecar are as they were.
- **The reveal starts on the slab's top:** the cheeks and the closing face
  begin at z 0.02, and the wall's notch carries the nosing's two top
  corners, so wall, nosing, slab and cheeks meet on shared vertices. Under
  the nosing the floor cap runs straight along the wall line instead of
  round the reveal. The screen's artwork keeps its place, so the slab covers
  the bottom 1.3 px of its threshold.
- **Its own atlas region** (Texture set).

`floor_for()` gives the entrance its slab on every tier that cuts its recess
(`opening_mode()`): `LOD0`-`LOD2`, since `LOD3` paints the screen flat on
the wall with no reveal. The machinery door, a vehicle door, keeps its
0.25 m reveal on the ground with no floor (Known simplifications).
`check_layout()` adds `door_floor.problems()`: the slab's region the
opening's width and the reveal's depth, the door at grade.

### Roof joins

The gable walls end in the slab along the rake (`gtop`). The lid that closes
the ring is split at the apexes into two planar halves. Both gables hand over
from the brick band to the same band 3.75 m lower at `Z_GABLE` = 5.5 m, a
quarter metre under the soffit line. The bond and tone continue across that
line (Texture set).

### Downpipes

Two downpipes come from the painted gutters, at diagonally opposite corners,
so each gable shows one. The east one is 0.4 m from the rear corner, clear of
the entrance bay; the west one is 0.4 m from the front corner. Both are 0.41 m
from the nearest window's side. They follow `downpipes.MODES` on every tier:
8-sided with swan-neck and shoe, 4-sided bent, 4-sided straight, then
3-sided. `check_layout()` passes `downpipes.problems()`.

### Vents and roof safety

The vent pipes are a 0.30 m one on the east slope (x 2.0, y 1.6, 0.9 m above
the sheet) and a 0.16 m one on the west slope (x -1.9, y -2.4, 0.55 m). They
are plain vents, not serviced items, and nothing else on the roof is serviced,
so CLAUDE.md requires no roof safety kit.

## Per-tier triangle counts

| Tier | Triangles | Ceiling |
| --- | --- | --- |
| `LOD0` | 544 | 12,000 |
| `LOD1` | 448 | 4,000 |
| `LOD2` | 332 | 1,500 |
| `LOD3` | 232 | 500 |

The entrance's floor slab costs 4 triangles, the nosing and the top, on
each tier that keeps it (`LOD0`-`LOD2`): measured against the tiers before
it, +4 on each and nothing else: the east wall's re-triangulation round the
nosing's corners and the floor cap's straighter rim come out even. `LOD3`,
with the screen flat, is byte-identical to before.

The building is one box with a gable roof and thirteen openings, so the counts
are low and are not padded. They sit beside the catalog's houses and under the
two-storey terraces, which is expected for a single-volume hall.

At `LOD0` the triangles go to:

- the thirteen recessed openings (cheeks, closing planes and the wall round
  them), about 300;
- the two 8-sided downpipes with their bends, about 150;
- the two 8-sided vents and the roof slab, the rest.

`LOD1` saves on the pipes' and vents' sides. `LOD2` keeps every recessed
opening, drops the 0.16 m vent and goes to four-sided pipes; the limited
dissolve recovers the boolean's coplanar splits. `LOD3` flattens the eleven
windows and the entrance screen, which is most of its 96-triangle saving,
and takes the downpipes to three sides; it keeps the louvres and the
machinery door recessed. A further cut would have to remove the downpipes,
the last vent or those three recesses: the pipes and vent are light marks
still seen past 120 m, and the recesses popped when flattened (LOD review),
so they stay, well under the ceiling.

## LOD review

**Switches, the consumer's screen-size measure** (1080p, 75° vertical FOV;
about 1.8, 4 and 8 times the 12.1 m largest bounds dimension): `LOD1` from
about **22 m**, `LOD2` from about **48 m**, `LOD3` from about **97 m**, far
nearer than the distance table's 35 / 70 / 120 m. The tiers are judged at
these.

Camera: perspective, 1920×1080, 75° vertical FOV, distance from the camera
to the centre of `LOD0`'s bounds; each pair face-on (10° up), oblique (45°
round, 25° up) and from eye level (30° round, 1.7 m) at noon, and oblique
at night with the reference emission on. Before/after pair sheets of this
revision are in
`review/older_audit_2026_11_22/fix_industrial_a1/nostokonehuone_brick/`
(local, git-ignored).

Results (mean |difference| per view, of 255):

- **22 m.** `LOD1` is indistinguishable from `LOD0` (0.03-0.06). The pipes'
  and vents' fewer sides are under a pixel's difference.
- **48 m.** `LOD1`/`LOD2` match (0.07-0.14); the 0.16 m vent (under two
  pixels) goes and is not missed. When `LOD2` flattened all thirteen
  openings, this was the group's strongest pop (2.0-2.8, 1,600-2,300
  pixels changing by more than 24): frames and glass brightened, the gable
  louvre turned from a dark recess into a light patch, the machinery door
  lightened and the lit windows grew at night. `LOD2` now keeps every
  recess.
- **97 m.** `LOD3` flattens the windows and the entrance screen (0.8-1.3,
  160-430 pixels over 24): their steel frames read a little lighter and the
  lit panes a frame's width larger, a reveal shadow of about a pixel and a
  half going. Flattening the louvres and the machinery door here too still
  turned the front louvre light (1.1-1.6), so those three stay recessed.
  The window change is left: keeping those recesses as well would make
  `LOD3` no reduction on `LOD2`.

The windows' dark glass and light frames, the concrete band and plinth, and
the dark roof hold on every tier.

**The entrance floor slab (2026-11-23)** adds no transition of its own: it
goes with the screen's 0.20 m reveal at the `LOD2`/`LOD3` switch (about
97 m), where a 0.02 m nosing and 0.2 m of slab are well under a pixel.
Checked from a standing eye and from 0.35 m over a terrain plane at z = 0,
every tier (Review status).

These are authoring comparisons. Consumer switching, filtering and
performance are pending.

## Interior geometry

The validator's hidden-surface test reports **0 hidden triangles on every
tier**. The only closure faces are the buried wall-ring floor and lid and the
buried tops of the pipes. The union removes all of them. Recessed glass, door
leaves and louvres are exterior surfaces. The wall ring's floor, at z = 0 and
facing the ground, runs straight along the east wall line under the
entrance's floor slab, so no face lies at grade inside its reveal; the slab
is exterior surface and adds no face inside the shell.

## Known simplifications

- **Painted, not modelled:** the glazing bars, the hopper sashes, the
  entrance's transom and side panels, the machinery door's ribs, rails,
  hinges and lights, and the louvre blades.
- **Painted on the roof and eaves:** the lintel band's formwork joints, the
  standing seams, the snow guard, the ridge cap, the gutters and their
  hangers.
- **Not modelled:** sills (a concrete patch on the recess's bottom cheek),
  any lintel over the machinery door (plain brick above it), and the plinth
  step (flush with the brick).
- No headframe, ropes, sheaves, ground slab, apron or yard furniture.
- **Floors:** only the entrance's reveal has one, a flat concrete slab with
  no mat, drain or threshold strip (Construction). The machinery door's
  0.25 m reveal stands on the consumer's ground.
- The rope slot is closed by a louvre, so no unmodelled interior shows.

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
| 0–376 | BRICK | z 0–5.875 m: plinth, brick, the concrete lintel band at 4.25–4.5625 m |
| 384–552 | ROOF | standing seam, V stretched (168 rows over the 5.28 m slope, 31.8 rows/m) |
| 558–574 | EAVE | the fascia (0.25 m) with the half-round gutter across its top 9 rows |
| 586–1020 | unique | the two window regions, the entrance screen, the machinery door, the louvre, the vent pipe and its open end, the entrance's floor slab, flat patches |

`PIPE_STRIP` is rows 567–572, the gutter's middle. The downpipes sample it and
measure sRGB 130/133/133 in every variant. That is the galvanised steel of the
farm buildings (`ID_GUTTER`, 134/137/137, roughness 0.48, metallic 0.60). The
snow guard is the same steel.

ORM: only that bare galvanised steel and the handles (0.35, 0.80) are
metallic. Painted or coated steel is dielectric, metallic 0: the roof sheet
(roughness 0.48), the fascia and barge flashing (0.46), the black vent pipes
(0.55), the window steel (0.44) and the doors (0.52).

Two window regions (`window`, `window_b`) are alternated along each wall, so
neighbours show different rooms behind the glass. The bands have 6–8 px
gutters. `pad()` fills every unclaimed texel from the nearest region's edge.

The entrance's floor slab has its own region at 64 px/m, right of the vent
pipe's open end (`FLOORS`, `scripts/door_floor.py`): 104 x 14.08 px at
(740, 586). It is the slab unfolded: U along the wall from the opening's
left side, V the nosing's 0.02 m (1.28 px) and then the top from the wall
plane to the screen.

### Texel density

Texel density is 64 px/m everywhere, with two exceptions:

- the roof band's V, at 31.8 rows/m up the slope, where only the snow guard
  and the ridge cap vary;
- the flat patches.

The facade regions are all at true 64 px/m scale.

### The brick band and the gables

The gable triangles above `Z_GABLE` (5.5 m) sample the brick band 3.75 m
lower. That is 48 courses, the tone period, so the bond and the brick tones
run on across the line. The rows they sample (1.75–3.93 m) are clean brick:
above the plinth's splash and bloom, and below the lintel band.
`check_regions()` asserts this. Nothing that follows height is painted near
the band's top.

### Relief

The normal map is derived from a painted height channel, in metres:

| Feature | Height |
| --- | --- |
| Brick faces over mortar | 0.006 |
| Lintel band | 0.010 |
| Window frames | 0.035 |
| Glazing bars | 0.022 |
| Hopper sash | 0.045 |
| Door frames and stiles | 0.030 |
| Machinery door's ribs | 0.006 |
| Standing seams | 0.040 |
| Gutter radius | 0.070 |
| Snow-guard tubes | 0.045 |
| Floor slab pores | 0.0004 |

Relief that varies in V on the roof band is scaled by its rows per metre over
64. Glass is flat. Seams, frames and bars read raised in sun from both
directions, which confirms the OpenGL green channel.

### Filtering

Atlas mips at levels 3 and 4 were made with `scripts/review_atlas_mips.py`.
`LOD1`–`LOD3` were rendered at mip 4 (64² atlas), oblique and aerial at 20 m.
The roof keeps its colour with no brick or band leak. The gutter merges into
the roof's dark edge, as expected at that size. The windows, door and louvre
keep their regions, and the plinth and band stay distinct.

### Weathering

Weathering is `scripts/weathering.py` at its moderate level:

- grime and paint fade overall;
- rain wash, splash-back and salt bloom on the brick;
- soil and algae on the plinth;
- dust on the lintel band's top, with runs on the brick piers under it;
- roof runs, chalking toward the ridge and debris above the snow guard, with
  rust at its brackets;
- the gutter's dirty belly and runs down the fascia;
- dirt on the windows' bottom rails;
- kicked-up dirt and handle grime on both doors;
- soot runs on the louvres and the vent pipes;
- trodden-in dirt on the entrance's floor slab.

Cavity dust settles in the mortar joints. Glass stays clean.

### The entrance floor slab

Painted by `scripts/door_floor.py` (`paint()`, `grain()`, `weather()`), as
the catalog's other entrance slabs are: float-finished cast concrete,
`ID_FLOOR`, sRGB **(132, 130, 124)** in every variant, roughness **0.88**,
nonmetallic. Occlusion deepens toward the jambs and the screen (within
0.08 m), a slightly paler path is worn toward the leaf, the pores are the
plinth's noise at 5 % shade and 0.4 mm of height, and blotchy trodden-in
dirt lies over it. The region bleeds 2 px into its gutter.

## Glazing treatment

Glass is painted with `scripts/glazing.py`: `rooms()` on the finished albedo,
`glazing.BASE` (50, 54, 57), one room per window, since the 2 px glazing bars
are thinner than its merge.

Measured over the window regions:

| Variant | Glass (sRGB mean) | Steel frames (sRGB mean) |
| --- | --- | --- |
| `red_brick` | 67 | 198 |
| `yellow_brick` | 65 | 108 |
| `brown_brick` | 66 | 177 |

The validator measures glass at sRGB 55 (linear 0.034) over the whole mask, at
0.27–0.29× the brightest trim. Roughness is 0.089 over the glass, metallic 0.
All of this is inside the Style Direction band and darker than the frames in
every variant. There are no brief-driven departures.

## Variant list

Three uniform brick alternatives on the shared mesh: one coherent treatment
per instance. Window steel, doors and the roof move with the brick, and the
window steel is always lighter than its glass.

| Variant | Meaning |
| --- | --- |
| `red_brick` (default) | red facing brick, off-white window steel, dark green-grey doors, dark grey roof |
| `yellow_brick` | yellow facing brick, grey-green window steel, oxide-red doors, grey roof |
| `brown_brick` | dark brown facing brick, light grey window steel, blue-grey doors, near-black roof |

The concrete plinth and band, the soffit, and the galvanised gutter, downpipes
and snow guard are the same in every variant.

## Night lighting

- **Mask.** `nostokonehuone_brick_emission.png` is the neutral glazing mask:
  - every window's panes;
  - the entrance screen's panes above the transom;
  - the machinery door's six small lights.

  Each is lit as a room by `glazing.night_rooms()`. Everything else is black:
  frames, leaves, louvres, walls and roof. There are no signs or lamps.
- **Bindings.** All four GLBs bind the mask through `emissiveTexture` on UV0,
  with `emissiveFactor` `[0, 0, 0]` by default and the texture kept
  (`scripts/window_emission.py`, via `asset_build.export_all()`).
- **Reference lit factor.** Linear RGB `[1.0, 0.88, 0.72]`, the industrial
  value `tehdas_brick_gable` uses, not the warm residential default.
- **Control.** One building-wide control. The windows share two atlas
  regions, so individual windows cannot be switched. The consumer owns
  intensity, colour and schedule.
- **Preview.** `variants.png` shows all three colours at `LOD0`: a DAY row
  (emission off) above a NIGHT row (reference emission on). Camera, framing
  and exposure are fixed between rows (`scripts/variant_previews.py`, Cycles,
  AgX, exposure 0). Spill onto nearby surfaces is simulated by Cycles in that
  sheet only.
- **Day cycle.** The day cycle (morning, noon, dusk, and night with emission
  on) was rendered on the reimported `LOD0`. The lit pattern was compared
  across tiers at night at the consumer's switches (LOD review): it matches
  through `LOD2`; at `LOD3` the flush windows' lit panes read a frame's
  width larger.
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

The facts sidecar `export/nostokonehuone_brick.model.json` records:

- the footprint, as the wall outline;
- one storey at the ground, 103.5 m², and zero dwellings;
- two doors:

  | Door | Kind | Main |
  | --- | --- | --- |
  | Entrance (`entrance`), east wall, 1.00 × 2.125 m | entrance | yes |
  | Machinery door (`machinery`), front gable, 3.19 × 3.66 m | vehicle | no |

**Preview.** `preview.png` uses the catalog's fixed camera orientation, lens,
sun and flat grey world (`asset_build.preview_studio()`), with the distance
fitted to the `LOD0` bounds. It shows `LOD0`, the default variant, with the
lights off.

## Review status

Checked here, in Blender:

- `scripts/validate_asset.py`: 0 FAIL, 0 WARN, 9 MANUAL with the sidecar
  written from a committed tree.
  - All four tiers have uri-only external images, one opaque material slot,
    welded manifold topology and 0 hidden triangles.
  - The pivot is at ground level and centred.
  - Every tier binds emission on UV0, default off, and the normal map at
    scale 1.
  - Six 1024² RGB PNGs; normal vectors are unit length and face out.
  - The glass measures in band and darker than the trim.
  - The facts sidecar is consistent. A build from an uncommitted tree gives
    one WARN, `source.dirty`, until `build.py -- facts` rewrites the sidecar
    from a committed one.
- No zero-area triangles on any tier, checked in the scene.
- `check_layout()` and `check_regions()` pass: openings clear of corners and
  each other, the band and the rake; downpipes clear of corners and
  openings; the gables' sampled rows clean brick.
- The six pre-export views at `LOD0` (four orthographic elevations, the top
  view and the raised front three-quarter aerial), plus rear and west
  aerials and eye-level views at the machinery door, the entrance, the rear
  gable and the eave.
- Window proportions, door scale against the 2.125 m leaf, brick coursing
  scale, the gutter reading as a gutter, and glass darker than its frames,
  all checked in those views.
- The tier comparisons at the consumer's three screen-size switches (22, 48
  and 97 m at 75°), the mip 4 stress renders and the day cycle, recorded
  under LOD review and Texture set.
- The ORM change compared before/after with `scripts/review_asset.py`
  (`LOD0`, front and oblique at 20 and 35 m, noon and reversed sun,
  `scripts/review_compare.py`): the roof, fascia and vent pipes lose their
  metallic sheen and read as painted sheet; nothing else changed.
- The variant sheet (`variants.png`): day and night for all three colours.
- The entrance floor slab (Construction, Revision log), from a snapshot in
  `review/review_2026_11_23/nostokonehuone_brick/before/`:
  - **Door views** (`review/review_2026_11_23/nostokonehuone_brick/door_views.py`,
    every tier, noon and reversed sun, over a green terrain plane at
    z = 0): the entrance from 5 m and 2.5 m, both sides, 0.35 m up and from
    above; the machinery door from eye level and 0.35 m up.
    Before, grass ran into the entrance's reveal up to the screen on
    `LOD0`-`LOD2`; after, concrete fills it jamb to jamb, its nosing a
    light line on the wall plane with nothing past it, the brick cheeks
    and the plinth standing on it, no dark seam or stretched texels.
    `LOD3`'s flat screen is unchanged. The machinery door's reveal still
    shows grass, as a vehicle door's may. Every camera stands outside the
    plan bounds.
  - **`review_asset.py`** from both: the day cycle on `LOD0`, the six
    orthographic views, and every tier front and oblique at 20, 35, 70 and
    120 m under noon; `review_compare.py` sheets in
    `review/review_2026_11_23/nostokonehuone_brick/compare/`. Every one
    of those sheets differs by 0.00-0.01/255 mean (the slab is a few
    pixels in the 20 m views); of the door views only the entrance's on
    `LOD0`-`LOD2` change.
  - Bounds, pivot, footprint, storeys and both doors in the sidecar
    unchanged; the entrance measured on `LOD0`-`LOD2` with an upward face
    at 0.020 m under 9 of 9 sample points of its reveal (none before);
    upward faces under 0.1 m are only the slab's top, and none lies at
    grade, on every tier; every tier closed and manifold when welded.
  - Textures: the emission map is the same file; the normal map differs
    only in the slab's region and its 2 px bleed; the albedos and the ORM
    differ in the free block round the region (x 733-997, y 575-1023),
    whose padding `pad()` now fills from the slab instead of the vent
    pipe's open end, by 1/255 in a few texels of the eave band's top bleed
    rows (y 575-576), and nowhere else.
  - `scripts/validate_asset.py`: 0 FAIL; the one WARN is `source.dirty`,
    the sidecar written from an uncommitted tree, to be rewritten with
    `build.py -- facts` once committed.

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

- **2026-11-23 — entrance floor slab.** The entrance's 0.20 m reveal had
  no upward face under it, so a consumer's terrain showed inside. It now
  stands on a 1.625 x 0.20 m concrete slab 0.02 m over the ground, nosing
  on the wall plane, on its own atlas region, from the shared
  `scripts/door_floor.py`, on `LOD0`-`LOD2`, where the reveal is cut.
  Tiers 540/444/328/232 to 544/448/332/232; bounds, pivot, footprint and
  doors unchanged; the emission map unchanged. The machinery door, a
  vehicle door, is left as it was.
- **2026-11-22:** audit fixes: painted roof, fascia, barge flashing and vent
  pipes made dielectric in the ORM (metallic 0); `LOD2` keeps all thirteen
  recessed openings (216 -> 328 triangles), and `LOD3` keeps the louvres
  and the machinery door recessed (208 -> 232), so the flattening pop at
  the consumer's 48 m switch is gone and `LOD3` is a real reduction; LOD
  review redone at the consumer's screen-size switches; stale validator
  note corrected.
