# hiilisiilo_drive_through

## Style brief

A composite screening and truck-loading plant for a small mid-century Nordic
coal mine, where the coal leaves by road. A raised storage bunker stands on
concrete legs, and trucks drive through underneath it to be loaded from
chutes.

- **Bunker house:** 12.0 × 8.0 m. Its long sides face the front and the
  rear. It stands on a concrete leg on the west and on the control and stair
  room on the east.
- **Truck lane:** one lane runs straight through under the bunker, from the
  front long side to the rear one. It is open at both ends, with no door
  leaf. Three steel loading hoppers hang from its ceiling.
- **Screen house:** above the lane is a concrete ring beam, the bunker's
  girder. On it stands the screen house: a concrete frame with profiled
  sheet infill under a low 1:10 mono-pitch sheet roof that falls to the
  rear. It has one row of small steel-framed windows at the screen floor.
- **Conveyor:** on the east side, the side the catalog view sees, a 2.0 ×
  2.0 m enclosed conveyor gallery rises at 30° from a low concrete intake
  hopper house into the screen house's east wall. It is the second half of
  the silhouette, and what makes the bunker read as a coal loading plant
  rather than a box on legs.

Materials are muted and coal-dusty, as a working plant's are: board-formed
concrete blackened at its foot by the coal the trucks throw up, a dusty lane
and dust-caked hoppers, moderately dirty cladding above; grey (or red-oxide) painted profiled sheet; a dark grey
roof; dark steel hoppers and doors; and the catalog's galvanised rainwater
steel for the rear gutter, the downpipes and the snow guard. The model shows
no recognisable real structure.

## Category and secondary use

`buildings/industrial/`. Its secondary use is the ground-level control and
stair room, the operators' access, which is part of the same plant.

## Hero/landmark status

**No.** It uses the ordinary budgets and a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) × height |
| --- | --- |
| Bunker house walls (lane inside) | 12.00 × 8.00 m |
| Intake house walls | 3.20 × 3.00 m, 4.20 m to its slab top |
| Overall bounds (roof overhangs, gallery, intake) | 20.65 × 8.70 × 13.08 m |

In the build frame the house spans x −6.0…6.0 and y −4.0…4.0. The other
parts sit as follows:

- **The lane** runs from y −4.0 to 4.0 between its side walls at x −4.40 and
  0.60.
- **The west leg** is x −6.00 to −4.40. The control and stair room is x 0.60
  to 6.00.
- **The gallery** is y 0.80 to 2.80, in the east wall's rear half. Its axis
  runs along X: it leaves the east wall at x 6.0 and ends inside the intake.
- **The intake house** is x 11.00 to 14.20 and y 0.30 to 3.30, with its slab
  overhanging 0.15 m.
- Everything east of the house stands 10 m or more from the lane's east
  wall, so the lane and both of its approaches are a clear, straight
  corridor x −4.40…0.60 for any y.

The roof slab overhangs 0.30 m at the front and rakes and 0.40 m at the
rear. The pivot is at ground level, centred on the bounding box: build point
(4.025, 0.05, 0). It is taken from `LOD0` and applied to every tier, and every
tier has the same extents.

The facts sidecar's footprint is a single simple polygon. It is the house
rectangle, the intake rectangle, and between them the 2.0 m strip under the
gallery, which joins the two.

These stand outside that polygon but inside the bounds:

- the roof slab's overhangs;
- the two downpipes on the rear wall, under the rear eave;
- the intake slab's 0.15 m overhang.

## Story height

**One occupied storey on the ground: the control and stair room, plus the
intake house.**

- The control room is a block 5.20 m to the deck, with no modelled
  interior.
- The lane is open, at 5.20 m clear to its ceiling.
- The bunker and screen house above it are plant, not storeys. The bunker's
  bins occupy the ring beam's zone up to the notional screen floor at 7.40
  m, which is the gallery's floor where it meets the wall. The screen floor
  rises to the roof, 12.0–12.8 m.

None of these levels is a habitable storey, so the 3.0–3.3 m band does not
apply.

## Door leaf height

- **Control room door (main entrance): 0.95 × 2.10 m** steel leaf, with no
  transom. Its steel frame adds 0.08 m above it. The threshold is at ground
  level, on the front wall at x 1.90.
- **Intake door (vehicle): 2.40 × 2.60 m** steel sliding door, under a 0.12
  m track hood, centred on the intake's front face, so the tipping vehicles
  reach it from the front yard, 10 m east of the lane's approach. It is a
  vehicle door, so the leaf band does not apply; the 2.10 m door carries the
  human scale.
- The lane's two mouths have no door leaf and are not doors.

## Window sills

- **Control room:** two windows of 1.20 × 0.90 m, one on the front and one
  on the east face. Sill 1.10 m, head 2.00 m, level with the door's head
  (2.10 m) less its frame.
- **Screen house:** five windows of the same size, sill 8.70 m and head 9.60
  m. That is 1.30 m above the 7.40 m screen floor, a working sill for the
  operators on that floor. There are two on the front, one at the rear over
  the lane, and one in each end wall. The east one is at y −1.0, over the
  control room's east window and clear of the gallery's mouth. All of them sit in the 8.40–10.40 m
  cladding strip, clear of its joints and the frame's columns
  (`check_layout()`).

## Eave overhang

**0.30 m at the front (high) eave and the rakes, 0.40 m at the rear (low)
eave**, where the gutter is. This is within the 0.3–0.6 m default. The slab
is 0.25 m thick.

- **Front and rakes:** a steel fascia flashing in the roof's trim colour.
- **Rear:** a painted half-round galvanised gutter across the fascia's top.
- **Underside:** bare sheet.

The intake house has a flat concrete slab with a 0.15 m overhang and no
gutter: it drains off its edge.

## Construction

`build.py` builds closed solids and unions them with Blender's Exact
boolean (`asset_build.union`):

- the bunker house;
- the roof slab;
- the gallery;
- the intake house's walls and its roof slab;
- three hoppers;
- two downpipes.

### The lane as a tunnel through the one shell

The bunker house is a single hand-built closed solid of genus one: a box
with the lane as a tunnel through it.

- The front and rear walls' concrete regions are U-shaped round the lane's
  mouths.
- The lane's two side walls and its ceiling are ordinary outside surface.
- The lane has no floor face. The ground is its floor, so the shell's bottom
  is two floor caps, under the west leg and the control room, and nothing
  lies between them. No coplanar floor is left. The pedestrian door's
  recess is built with `floor=False` for the same reason, as in
  `konehalli_open_bays`.

**Lane, stated for the consumer:**

- it runs along Y, front to rear;
- it is 5.00 m clear between its walls;
- it is 5.20 m clear to its ceiling, and 4.60 m under the hoppers' mouths;
- trucks enter from the front (−Y) and leave at the rear.

The facts sidecar states it as its one passage (Export).

### Hoppers

Three steel hoppers hang on the lane's centre line, at y −2.5, 0 and 2.5.
Each is a frustum 1.50 × 1.20 m at its top, buried 0.12 m in the ceiling,
tapering to 0.60 × 0.45 m at its mouth at 4.60 m. A truck stops with its
body under them, centred on the middle hopper.

### Walls and the concrete frame

- Every wall carries a concrete region from the ground to 6.40 m (S1). That
  covers the plinth, the board-formed legs and walls, the deck joint at
  5.20 m and the ring beam.
- Above it are 2.00 m cladding strips cut at 8.40, 10.40 and 12.40 m and
  clipped to the sloping wall top. Each strip is split by the concrete
  frame's 0.40 m columns: at the four corners, and on the front and rear
  over the lane's side walls, so the legs read as running up through the
  house.
- Region outlines carry every neighbour's breakpoint, so walls and strips
  meet without T-junctions. `close_solid()` caps the three rims: two floors
  and the lid.

### Gallery and intake

The gallery is one closed box whose axis runs along X and falls at 30°,
east of the house on the side the catalog camera sees.

- **Upper end:** buried 0.50 m inside the screen house, through the east
  wall's rear half (y 0.80–2.80). Its floor is at 7.40 m and its top at 9.71
  m where it passes the east wall: in the cladding, 1.0 m clear of the
  ring beam's top and 2.4 m under the roof. The union cuts the wall round it
  and removes the buried end, so the join is one closed shell with no
  partition inside.
- **Lower end:** inside the intake house. Its floor crosses the intake's
  slab top (4.20 m) at x 11.54, 0.69 m inside the slab's edge.
- **Visible end:** the lower end's top 1.18 m stands out of the intake roof
  as the conveyor's tail housing.
- **Span:** 5.0 m clear between the house's east wall and the intake's west
  wall, unsupported.

The intake's walls run 0.12 m up into their slab. Nothing in the union is
coplanar.

### Roof, rainwater goods and snow guard

The roof is a mono-pitch at 1:10 (5.7°), falling to the rear. The underside
is at 12.80 m at the front wall line and 12.00 m at the rear. The walls run
0.12 m up into the slab.

- **Gutter:** painted on the rear fascia (Texture set).
- **Downpipes:** modelled with `scripts/downpipes.py` on the rear wall, at
  s 0.25 and 11.75 (x 5.75 and −5.75). The first is on the control room's
  back wall, the second on the west leg's.
  Both use the module's default swan-neck into the 0.40 m soffit and its
  shoe. The lane's mouth fills the middle of the rear wall.
- **Snow guard:** painted on the roof's lowest 0.40 m, which maps onto the
  rear eave band, as on `konehalli_open_bays`.
- **No roof safety kit:** the roof is not steeper than 1:8, and nothing on it
  is serviced.

### Authored parameters

`facade_atlas.py` holds every shared number, including:

- the plan (`HX`, `HY`) and the lane (`XL0`, `XL1`, `Z_DECK`);
- `Z_CLAD`, `JOINTS` and `COL_W`;
- the eave heights and overhangs;
- the hoppers, the gallery (`GAL_Y` across, `GAL_X` along, `Z_SCREEN`,
  30°) and the intake (`INT_X`, `INT_Y`), derived from the gallery;
- the openings.

`build.py` adds the wall specs. `check_layout()` asserts the following:

- openings clear joints, columns, the roof and the lane's mouths;
- the lane is at least 4.5 m wide and at least 4.5 m clear under the
  hoppers;
- the gallery is buried at both ends, crosses the intake roof inside the
  slab, and its mouth in the east wall clears the corner columns and the
  east windows by 0.3 m;
- the gallery and the intake stand east of the house, 1.5 m or more clear of
  the lane's line, so neither reaches the lane or its approaches;
- the downpipes clear the lane's mouth (`downpipes.problems()`);
- the cladding's U stays inside its band;
- the roof is no steeper than 1:8.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 782 | 12,000 | openings with a frame ring and a 0.12/0.15 m recess; three hoppers; eight-sided downpipes with swan-necks and shoes |
| `LOD1` | 630 | 4,000 | each opening one recess the size of its frame; downpipes four-sided, bent |
| `LOD2` | 446 | 1,500 | openings flush; coplanar boolean subdivisions dissolved (UV seams kept); downpipes straight, four-sided |
| `LOD3` | 438 | 500 | downpipes three-sided; the lane, hoppers, gallery and intake kept |

The counts are not padded. The massing is three boxes, a tunnel and a
gallery. The walls are polygons with holes, and everything shallow is
texture. That covers the ribs, board marks, the frame's columns, the ring
beam, the window bars and the wheel guard.

Where the triangles go at `LOD0`:

- the lane's walls and ceiling and the U-shaped mouths: about 40;
- the three hoppers, with their holes in the ceiling: 52;
- the downpipes and the gallery's cuts make up most of the rest.

`LOD3` keeps the hoppers (LOD review), so it sits near `LOD2`. It stays 62
under the ceiling. The gallery's mouth shares the east wall's cladding strips
with the screen house window, so the wall's triangulation round both is a
little denser than a bare wall's.

## LOD review

Intended switches are the catalog defaults: 35, 70 and 120 m, with no
overrides.

The review camera was perspective, 1920×1080, 50° vertical FOV, with
distance measured along the view to the front or rear bounding face
(`scripts/review_asset.py`). Rendering was Cycles CPU, 16–20 samples with
denoising, AgX, exposure 0. Pairs compared:

- `LOD0`/`LOD1` at 30/40 m, front and oblique, noon;
- `LOD1`/`LOD2` at 65/75 m, front, oblique and rear, noon and reverse sun;
- `LOD2`/`LOD3` at 115/125 m, front and oblique, noon and reverse sun.

Close renders at 25 m (front, oblique, rear and grazing, noon and morning),
the six views and `oblique` tier sets at 70 and 120 m for every tier are in
the local, untracked `review/mine_fixes_2026_11_20/hiilisiilo_drive_through/`,
beside the earlier passes in `review/mine_2026_11_20/`.

- **The lane is a real opening on every tier.** It costs about 40
  triangles. From the front it reads as a dark tunnel with the lit ground at
  its far end, from 22 m to 125 m.
- **The hoppers stay on every tier.** A first build dropped them at `LOD3`.
  At 115/125 m their dark notch under the lintel then vanished at the
  switch, so they were kept for 52 triangles.
- **Opening recesses** go from a ring (`LOD0`) to one recess (`LOD1`) to
  flush (`LOD2`). The window rhythm and the door are unchanged at each
  switch.
- **The gallery and the intake keep their shape on every tier.** On the
  east side they show in the catalog view and every front or oblique view,
  rising from the right into the screen house; at 120 m all four tiers show
  the same diagonal. The frame's columns and the ring beam are UV regions,
  so they keep their contrast at every tier.
- **The coal dust** is texture only, so it is the same on every tier; at 70
  and 120 m the dark feet and the dark lane hold.
- **Downpipes:** `downpipes.MODES` on every tier; no tier drops them.

Pending in the consumer: real LOD switching, shadows and ambient occlusion
in the lane, and performance.

## Interior geometry

The validator's hidden-surface test reports **0 hidden triangles on `LOD0`,
`LOD1` and `LOD2`**. On `LOD3` it reports one triangle of 0.0 m², at the
east downpipe's top where the three-sided pipe meets the rear soffit. It is
a zero-area candidate, not buried surface, and is far under the warning
thresholds.

- The lane's walls and ceiling are exterior surface, reachable from both
  mouths.
- The leg, the control room and the intake are solid: no interior is
  modelled.
- The kept closure faces are:
  - the floor caps under the leg, the control room and the intake walls;
  - the hoppers' mouths, painted coal;
  - the downpipes' shoe mouths.
- The lids, the gallery's buried ends and the hoppers' tops are removed by
  the union.

## Known simplifications

- **Lane:** no floor, rails, weighbridge or lighting; the ground is the
  floor. The hoppers have no modelled gates; the gates are painted on their
  sides' foot.
- **Interiors:** the screen house's bins, screens, floors and stair are not
  modelled, and neither is the conveyor belt. The windows are closed opaque
  panes.
- **Painted detail:** the frame's columns, the ring beam, the deck joint,
  board marks, tie holes, the wheel guard, the downstand beams and hopper
  flanges on the lane's ceiling are all painted. So are the sheet's ribs and
  laps.
- **Gallery:** no supporting trestle (it spans 5.0 m between the house and
  the intake) and no windows. Its tail housing's top is a plain clad end.
  It has no belt, chute or skirt where it meets the screen house; the clad
  box simply runs into the wall.
- **Ground:** the asset has no ground, so the coal spilt under the gallery
  and in the lane is carried by the surfaces that exist: the gallery's
  floor, the intake's roof, the lane's walls and the legs' feet.
- **Rainwater goods:** the gutter is painted, with its relief in the normal
  map. The downpipes run up into the soffit behind it. The intake house's
  flat roof has no gutter.

## Texture set

One 1024² trim-sheet atlas, rasterised by `scripts/atlas.py` at `atlas.SS`
= 4, padded last by `atlas.pad()`. Layout, in rows from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–414 | S1, concrete | U along the wall, V = height 0–6.40 m, 64 px/m |
| 414–554 | C, cladding (x 0–960) and column strip (x 972) | one 2.00 m repeat (rows 420–548) tiling in V, 64 px/m; periodic gutters 6 rows each side |
| 558–658 | ROOF | U = x at 64 px/m; V up the slope from the low edge, 96 rows over 9.60 m (10 px/m); also the gallery's top |
| 660–680 | FASCIA | front and rake edges, 64 px/m |
| 684–944 | unique | lane ceiling (160 × 256) and side walls (256 × 166) at 32 px/m; door, window, intake door at 64 px/m; hopper side; flat patches |
| 988–1024 | EAVE_R | rear fascia with the gutter, then the roof's lowest 0.40 m at 40 px/m with the snow guard |

**Deviations from 64 px/m:**

- The lane's regions are at 32 px/m. They are in shade and seen obliquely;
  at 64 px/m they would need a third of the atlas. Relief heights there are
  scaled by 32/64, so the normal map's slopes stay physical.
- The roof band is stretched in V; only its ribs vary there.

### Repeating cladding

The screen house is 13 m tall, too much for one band. The walls are cut at
the 2.00 m joints and every strip maps onto the same rows. Profiled sheet
varies only across its ribs. The band's noise and weather are drawn on its
own 128-row period (`noise()` and the `Weather` subclass in
`facade_atlas.py`), so the repeat is seamless. Height-following weather goes
only on S1.

The gallery's sides map onto C with U along the axis and V square to it, so
the ribs stand square to the gallery.

### Relief

| Feature | Relief |
| --- | --- |
| Sheet ribs | 25 mm (roof 30 mm), every 0.25 m |
| Formwork board lines | 2 mm; tie holes 6 mm |
| Steel flashings | 15 mm |
| Window frames | 12 mm; bars 8 mm |
| Wheel guard | 50 mm |
| Ceiling beams | 40 mm |
| Gutter roll | 70 mm |
| Snow guard tubes | 35 mm, scaled by 40/64 |

The ribs read raised in the 22 m morning renders.

### Weathering

Weathering follows `scripts/weathering.py`'s moderate level: grime, fade on
painted steel, wash, plinth and splash on S1, roof dirt toward the low edge,
runs under the flashings and the gutter.

- **Coal dust instead of soil.** Dirt resolves to the module's neutral dust
  colour on every id (the `steel` list). That dust is a mid-grey, lighter
  than the dark steel it settles on, so coal has its own field: the local
  `Weather` subclass in `facade_atlas.py` adds a coal field `K`, carried by
  `pad()` with the module's fields, which lerps the weathered colour toward
  `COAL_DUST` (sRGB 46/45/44, clipped at 0.9), adds 0.22 roughness and
  strips the metallic. `coal()` writes it, and deepens the shade by 0.30
  of it where it lies thick.
- **Where the coal dust goes, and how much (`K`):**
  - the legs' and walls' feet: `FOOT_COAL` 1.0 at the ground, falling by
    1/e every 1.50 m (`FOOT_FALL`), blotched. S1's V is height from the
    ground on every wall, so this height-following term is exact there;
  - the rest of S1: 0.06–0.28 in broad patches and long streaks;
  - the cladding band and the columns: 0.05–0.31, as periodic patches and
    streaks on the band's own period, nothing that follows height, since
    the band repeats up the wall;
  - the lane's walls: `LANE_COAL` 0.35 plus blotches everywhere, and 0.6
    more at the foot, falling by 1/e every 1.0 m;
  - the lane's ceiling: 0.35 plus 0.55 round each hopper's throat;
  - the hoppers' sides: 0.35 at the flange to 0.8 at the mouth;
  - the gallery's floor 0.55 and the intake's roof 0.60, where the spill
    falls; the slab soffits and reveals 0.25–0.30; the door feet 0.45.
- **Measured albedo** (grey_sheet, sRGB, band means):
  - concrete plinth (0–0.3 m) ~61, foot (0.3–1.0 m) ~80, 1–2 m ~97,
    2–4 m ~113, ring beam ~122 (both variants);
  - cladding ~105 (grey_sheet), 93/57/49 (red_sheet); columns ~122;
  - lane walls ~42 at the foot and ~82 at 1.5–4 m; lane ceiling ~61;
  - hopper sides ~51; gallery floor and intake roof ~44;
  - roof ~73 (grey_sheet), ~64 (red_sheet).
- **Working, not abandoned:** the dust darkens and mattes; it adds no rust,
  stains, peeling or growth, and the cladding and roof above stay only
  moderately dirty.

### Lane occlusion

The lane's walls fall to shade 0.66 and AO 0.50 at mid-length, and its
ceiling to 0.55 and 0.40. Both darken further into the corners. The lane is
open at both ends, so the fall is symmetric about its middle, and one side
region serves both walls.

### Filtering

Whole-atlas mip4 stress renders (`scripts/review_atlas_mips.py`) of `LOD2`
and `LOD3` at 120 m, front, 75° grazing and rear, under noon sun, showed no
roof/cladding colour leaks and no dark seams. The columns, the ring beam
line, the windows and the dark lane all hold.

### Unique textures

Six 1024² RGB PNGs, about 24 MB uncompressed (4 MiB each in memory without
mips): two albedos, plus one ORM, one normal map and one emission mask
shared by both variants.

## Glazing treatment

The glazing uses `scripts/glazing.py` `rooms()` on the finished albedo, with
the default base, after the id, shade and AO pass. It measures sRGB 57
(linear 0.037), 0.44× the trim, in both albedos. Roughness is 0.08
(`glazing.ROUGHNESS`) and metallic 0.

Each window is a steel frame of four by three lights. Its 0.03 m bars are
merged by `rooms()` into one pane, and every window shares the one region,
so all seven windows show the same room.

The steel frame (sRGB ~92–94) is lighter than the glass, and the flashing
round it lighter still. There is no departure from the Style Direction band.

## Variant list

| Variant | Meaning |
| --- | --- |
| `grey_sheet` (default) | grey painted (or long-dulled galvanised) profiled sheet, dark grey roof, grey-green steel doors and frames |
| `red_sheet` | red-oxide painted cladding, dark warm-grey roof, dark grey doors |

Two variants, as the brief asks. This is an industrial plant with one
coherent treatment per instance: the concrete, the coal dust, the hoppers
and the galvanised rainwater goods are the same in both. Geometry, UVs, ORM,
normal and emission are shared.

## Night lighting

**Night-lit: it ships `_emission.png`.**

- **Mask:** the window glass only, via `glazing.night_rooms()`. That covers
  the five screen house windows and the two control room windows, all from
  one region, so every window shares one room pattern.
- **Not lit:** the lane is unlit, and there are no lamps or signs.
- **Default state:** `emissiveTexture` is bound on every tier with the factor
  rewritten to zero (`window_emission.rewrite_glb_emission`), so the asset
  ships with its lights off.
- **Reference lit factor:** the catalog's warm default
  (`window_emission.LIT_FACTOR`).
- **Control:** per building. Shared window UVs prevent per-window control.
- **`variants.png`:** day above night for both colours, from the catalog
  camera with fixed exposure (`scripts/variant_previews.py`).
- **No light spill** was simulated.
- **Pending in the consumer:** off/on on reimport and night intensity.

## Export

```
python3 facade_atlas.py export                       # albedo x2, ORM, normal, emission
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

**Bindings**, from the shared material on every tier:

- albedo → `baseColorTexture`;
- ORM G/B → `metallicRoughnessTexture`;
- ORM R → `occlusionTexture`;
- normal → `normalTexture` at scale 1;
- emission → `emissiveTexture`, factor 0.

The validator confirms one material, uri-only images, the normal and
emission bindings and the default-off factor on every tier. Backface
culling is on, and the material is single-sided and opaque. The preview is
`LOD0`, `grey_sheet`, from the catalog's fixed camera, sun and grey world.

### Facts sidecar

`export/hiilisiilo_drive_through.model.json`, in the glTF frame:

- **footprint:** the house rectangle, the gallery strip and the intake
  rectangle as one polygon (Footprint). The strip's four corners lie under
  the gallery, not on a wall.
- **storeys:** one storey at the ground, 42.27 m². That is the control room
  inside 0.30 m walls (4.80 × 7.40 m) plus the intake house inside 0.25 m
  walls (2.70 × 2.50 m). The lane, the bunker and the screen house are not
  storeys, and the west leg is a solid pier.
- **dwellings:** none.
- **doors:**
  - `control`: `entrance`, main, front wall;
  - `intake`: `vehicle`, on the intake's front face, facing −Y (+Z in
    the sidecar).

  The lane's mouths are not doors.
- **passages:** one, `truck_lane`, stated from the front mouth trucks
  enter by:
  - position [−5.925, 0, 4.05]: the lane's centre line (build x −1.90) on
    the front wall's plane (build y −4.0), not the roof overhang's edge at
    4.35;
  - forward [0, 0, −1], into the building towards the rear;
  - width 5.00 m between the side walls, length 8.00 m from the front
    mouth to the rear one at z −3.95, through (open at the rear);
  - clear height 4.60 m, the hoppers' mouths (`Z_HOP`); the ceiling is
    at 5.20 m.

## Review status

Checked here, in Blender:

- **Validator:** `scripts/validate_asset.py`, 0 FAIL. The one WARN is
  `source.dirty`, from an uncommitted tree. Every tier passes:
  - welded manifold topology, one material, uri-only images;
  - the normal and emission bindings, the default-off factor;
  - triangle ceilings, pivot at ground and centred;
  - hidden surface 0/0/0/1 (Interior geometry).

  The glazing measures within its band in both albedos, and the facts
  sidecar is consistent.
- **Layout:** `check_layout()`, including the lane's clearances, the
  gallery's burial and the downpipes.
- **Six views:** `LOD0` (`review_asset.py --six-views`). The lane shows the
  ground through it in the front view, clear of everything east of the
  house, and the gallery's joins into the east wall and the intake roof are
  clean.
- **Close renders:** 25 m, front, oblique, rear and grazing, under noon and
  morning sun. They checked the lane's read, the door's scale against the
  2.10 m leaf, the gallery's join, and the coal dust: black at the legs'
  feet and the intake's, in the lane and on the hoppers, light on the
  cladding.
- **Sidecar against `LOD0`:** the bounds match the mesh's; every footprint
  corner on a wall is a ground vertex (the strip's four corners under the
  gallery are not, by design); both doors sit on their walls' outer planes,
  facing out. The passage was measured on the exported `LOD0`: rays across
  the lane meet its walls at x −8.425 and −3.425 at every height and
  depth below the hoppers, rays along it meet the wall planes at z 4.05 and
  −3.95, and the lowest geometry clipped to the lane's plan is 4.600 m,
  the hoppers' mouths.
- **LOD pairs:** around 35, 70 and 120 m, under two sun directions.
- **Filtering:** mip4 stress renders at 120 m.
- **Variants:** day and night for both (`variants.png`).

Pending in the consumer:

- import, orientation and pivot on reimport in the engine;
- that its trucks fit the lane: 3.5 × 4.0 m against 5.00 m clear and 4.60 m
  under the hoppers;
- LOD switching, shadows and AO in the lane;
- filtering of the stretched roof band and the 32 px/m lane regions;
- night intensity;
- performance.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`) throughout.
The MCP addon was not used. Texture generation used the system Python 3
with numpy, scipy and Pillow.
