# hiilenvastaanotto_brick_shed

## Style brief

The coal reception of a small mid-century (1950s–60s) Nordic town
heat-and-power plant. Trucks drive straight through a brick tipping shed and
tip their coal through a steel grate in the floor into a pit. A bucket
elevator in a tower beside the lane lifts the coal toward the boiler house's
bunkers. It is one of five separate pieces of one plant, with the boiler and
turbine hall, the chimney, the office and the transformer yard. The pieces
stand apart on a lot, and nothing joins them: no ground, no conveyor bridge.

- **Tipping shed:** 14.0 × 6.4 m of red brick between the flush columns of a
  concrete frame, on a concrete plinth, under a 14° profiled-sheet gable
  roof. Three tall steel multi-pane windows sit high on the front wall,
  under the concrete ring beam.
- **Truck lane:** straight, level and doorless along the shed's length,
  open at both gables. Each gable is a concrete portal: two piers and a
  lintel, with brick and the gable triangle above.
- **Lean-to and tower:** behind the shed, a low brick lean-to with the
  attendant's room and the drive room. The elevator tower rises through it,
  13.5 m, under a flat concrete slab, with a closed steel outlet hatch high
  on its rear face. No conveyor leaves it.

Materials are muted and coal-dusty, as a working plant's are. Facing brick
in the plant's brick trio, light cast concrete for the frame, the plinth
blackened by the coal the trucks throw up, a dark dusty lane, light-grey
steel windows (in the red variant) and a dark grey sheet roof. The
gutters, downpipes and snow guard are the catalog's galvanised steel. It is
a generic composite and shows no recognisable real building.

## Category and secondary use

`buildings/industrial/`. The secondary use is the attendant's room in the
lean-to, which is part of the same plant.

## Hero/landmark status

**No.** It uses the ordinary budgets and a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) × height |
| --- | --- |
| Shed walls (lane inside) | 14.00 × 6.40 m, eave underside 7.20 m, ridge 8.25 m |
| Lean-to walls | 9.20 × 3.60 m behind the shed, roof 3.47–4.13 m |
| Tower | 3.40 × 4.00 m from the shed's rear face, 0.40 m proud of the lean-to, 13.50 m to its slab top |
| Overall bounds (roof overhangs, tower slab) | 14.60 × 11.05 × 13.50 m |

In the build frame the shed spans x −7.0…7.0 and y −3.4…3.0, and the other
parts sit as follows:

- **The lane** runs from x −7.0 to 7.0 between its side walls at y −3.0 and
  2.6.
- **The lean-to** is x −4.5 to 4.7, y 3.0 to 6.6. Its front runs 0.10 m
  into the shed's rear wall.
- **The tower** is x −1.7 to 1.7, y 3.0 to 7.0.

The pivot is at ground level, centred on the bounding box: build point (0,
1.725, 0). It is taken from `LOD0` and applied to every tier, and every tier
has the same extents.

The facts sidecar's footprint is a single 12-cornered polygon: the shed
rectangle with the lane inside it, the lean-to and the tower's step. These
stand outside it but inside the bounds:

- the main roof's 0.40 m eaves and 0.30 m rakes;
- the lean-to's 0.30 m eave and rakes;
- the tower slab's 0.25 m overhang;
- six downpipes.

## Story height

**One occupied storey on the ground:** the lean-to's two rooms and the
tower's foot. The lean-to's ceiling is about 3.4–3.9 m. The shed is one
open lane, 5.98 m clear above its floor slab (Construction), and it is not a
storey. The tower is plant to its slab, with no floors modelled. None of
these is a habitable storey, so the 3.0–3.3 m band does not apply.

## Door leaf height

- **Attendant's door (main entrance): 0.95 × 2.10 m** steel leaf in a
  0.05 m steel frame, with no transom. The threshold is at ground level on
  the lean-to's east end, build (4.7, 4.0).
- **Elevator door (service): 0.95 × 2.10 m**, the same door, at the tower's
  foot on its rear face, build (0, 7.0). It gives access to the elevator's
  boot room.
- The lane's two mouths have no door leaf and are not doors.

## Window sills

- **Shed windows:** three of 2.80 × 1.75 m on the front wall, sill 4.25 m,
  head 6.00 m under the ring beam. They are deliberately high, lighting
  the lane over the trucks; the lane is not an occupied floor.
- **Lean-to:** small windows of 0.90 × 1.20 m, sill 1.00 m, head 2.20 m,
  just over the door's 2.10 m head. There is one on the east end beside the
  door and one in each rear wall.
- **Attendant's window onto the lane:** 0.90 × 1.20 m in the lane's rear
  side wall at x 3.3, sill 1.30 m, head 2.50 m, at a truck driver's eye
  height.
- **Tower:** windows of the same size high on its front and east faces,
  sill 10.20 m, clear of both roofs. A 1.00 × 0.60 m louvre sits on its
  west face at 11.0 m.

## Eave overhang

- **Main roof:** 0.40 m at the front and rear eaves, 0.30 m at the rakes.
  This is within the 0.3–0.6 m default. The slab is 0.25 m thick. A
  galvanised gutter is painted on both eave fascias, with steel barge
  flashing on the rakes.
- **Lean-to:** 0.30 m at its rear eave (with the gutter) and its rakes.
- **Tower slab:** a flat concrete slab overhanging 0.25 m. It drains off its
  edge, with no gutter.

The rakes overhang the mouths' wall planes by 0.30 m, with their lowest
point at 7.10 m, 1.1 m above the lintels (Construction).

## Construction

`build.py` builds the shed as one hand-built closed box: four walls to a lid
inside the roof slab, a floor cap, and the lid cut along the ridge. The lane
is then cut out of it with an exact boolean **difference**
(`asset_build.difference`). Everything else is unioned in with Blender's
Exact boolean (`asset_build.union`):

- the lean-to and tower, one hand-built solid;
- the gable roof slab, the lean-to slab and the tower slab;
- at `LOD0`/`LOD1`, two tie beams;
- six downpipes.

### The lane as a void cut through the shed

The cutter is one closed solid (`lane_void()`), extended 0.5 m past both
gables:

- the mouths' sections through the 0.4 m gables, 6.00 m high;
- between the gables' inner faces, the hall up to its pitched ceiling, 0.30
  m under the roof's underside (7.00 m at the side walls, 7.70 m at the
  apex);
- at `LOD0`/`LOD1`, a second cutter for the attendant's window recess.

The cutter's faces become the lane's surfaces with the cutter's own UVs:
the side walls, the ceiling, the lintels' soffits and the gables' inner
faces over the lintels. Because the cutter's floor is at 0.02 m, the box
keeps **a 0.02 m floor slab under the lane** whose top is the lane's floor,
carrying the tipping grate. This follows the brief's thin closed slab, not
`hiilisiilo_drive_through`'s floorless lane: that lane has no floor face, and
the grate needed one. The slab's edge shows as 2 cm of plinth concrete
across each mouth. There is no kerb, threshold or ramp.

**Lane, stated for the consumer:**

- it runs along X, the shed's long axis, straight and level;
- it is 5.60 m clear between its side walls and 14.00 m from wall plane to
  wall plane;
- it is 6.00 m above the ground to the lintels' soffit, the lowest geometry
  over it, which is 5.98 m above the floor slab trucks run on;
- tie beams at 6.20 m, the ceiling at 7.00–7.70 m;
- it works both ways. The sidecar states it from the west mouth (Export).

**Tipping grate:** 3.0 m along the lane × 4.0 m across it, on the centre
line at mid-length (build x −1.5…1.5, y −2.2…1.8). It is painted on the
floor slab: a steel frame, bars across the traffic every 0.15 m, a cross
bearer, and coal in the pit below them. A tipping truck stops with its tail
over the grate's centre, build (0, −0.2).

**Nothing stands beyond a mouth's plane in line with the lane or within 1 m
of it** below the lintels (`check_layout()`):

- the lean-to and its slab end at x −4.8 and 5.0;
- the downpipes stand 0.65–0.75 m inside the mouths' planes;
- only the main roof's rakes pass the planes, 0.30 m, at 7.10 m and up.

### The rear side faces the hall

The lean-to and the elevator tower are on the rear (+Y). The tower's outlet
hatch is high on its rear face, at 10.6–11.8 m, so **the rear (+Y) is the
side that faces the boiler and turbine hall's coal side**.

### Walls, frame and band

- **Regions:** every wall is cut into regions by two horizontal splits and,
  below the first, by the frame's 0.40 m columns. The columns stand at the
  shed's corners, at x ±2.4 on the long walls, and as the portals' piers.
  Each region carries its neighbours' breakpoints (`fix_tjunctions()`), so
  walls meet without T-junctions.
- **Column strip:** the columns map onto the atlas's column strip, and the
  brick onto the brick band.
- **The band** at 6.00–6.5625 m runs round the shed as the ring beam and is
  the portals' lintel. It is painted on both strips.
- **Above the band:** walls sample the brick rows 3.75 m lower (and 7.5 m
  lower above 9.5625 m, on the tower), a whole tone period, so the bond runs
  on (Texture set).
- **The lean-to and tower** solid has four rims: the floor, the lean-to's
  two sloping lids either side of the tower, and the tower's lid. The
  tower's side walls rise from the lean-to's lid, so the lean-to's roof
  slab buries their junction.

### Roofs, rainwater goods and roof safety

- **Main roof:** a gable at 1:4, ridge along X at build y −0.2. Its rear
  eave runs into the tower's front face.
- **Lean-to roof:** 1:10, falling to the rear, its high end buried in the
  shed's rear wall.
- **Gutters:** painted on the main roof's two eave fascias and the
  lean-to's rear fascia.
- **Downpipes:** six, modelled with `scripts/downpipes.py` with its default
  swan-neck and shoe:
  - front wall: s 0.7 and 13.3 (x ∓6.3);
  - shed's rear wall, beyond the lean-to: x ±6.3;
  - lean-to's rear walls, 0.25 m in from its corners: x 4.45 and −4.25.

  All clear their walls' corners and openings (`downpipes.problems()`).
- **Snow guard:** painted near the eave on both main slopes and the
  lean-to.
- **No roof safety kit.** The main roof is steeper than 1:8 but carries
  nothing serviced from it: no chimney, plant or ventilation housing. The
  tower's head is serviced from inside. The lean-to is under 1:8 and the
  tower's flat slab carries nothing either.
- **No handrails:** both doors are at ground level, so there is no entrance
  flight.

### Authored parameters

`facade_atlas.py` holds every shared number:

- the plan (`HX`, `Y_F`, `Y_R`, `WALL_T`), giving the lane `YL0`/`YL1`;
- `FLOOR_T`, `Z_MOUTH`, the band, `Z_BEAM` and `CEIL_DROP`;
- the roofs (`Z_EAVE`, `TAN`, `Z_AE`, `TAN_A`);
- the lean-to and tower (`AX0`, `AX1`, `AY1`, `TX0`, `TX1`, `TY1`,
  `Z_TSLAB`);
- the splits and shifts, the openings and the grate.

`build.py` holds the wall specs. `check_layout()` asserts the following:

- openings clear the corners, columns, splits, the band, both roofs and each
  other;
- the lane is at least 5.0 m wide and 4.6 m clear, with the beams over the
  lintels, and 12–16 m long;
- nothing stands beyond a mouth's plane beside the lane below the lintels;
- the attendant's window is inside the attendant's room and clear of the frames;
- the downpipes are placed correctly;
- the lean-to is not steeper than 1:8;
- every wall's brick stays inside the band and inside the clean shifted
  rows.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 1176 | 12,000 | openings recessed with brick reveals; two tie beams; attendant's window recessed; eight-sided downpipes with swan-necks and shoes |
| `LOD1` | 936 | 4,000 | downpipes four-sided, bent |
| `LOD2` | 504 | 1,500 | openings flush; tie beams dropped; coplanar boolean subdivisions dissolved (UV seams kept); downpipes straight, four-sided |
| `LOD3` | 480 | 500 | downpipes three-sided; the lane, lean-to, tower and all openings' paint kept |

The counts are not padded. The massing is a box with a tunnel, a lean-to, a
tower and three slabs. Everything shallow is texture: the frame's columns,
the band, the bond, the grate, the purlins and rafters.

Where the triangles go at `LOD0`:

- the six eight-sided downpipes: about 480 (the 240 that `LOD1` saves is
  their halved sides);
- the thirteen recessed openings with their reveals, and the wall
  triangulation round them: most of the rest;
- the lane's void, its two beams and the attendant's window recess: about
  120.

`LOD3` sits 20 under its ceiling, mostly because the six three-sided
downpipes stay; a tier that needed room would drop the lean-to's two first.
The count is close to `hiilisiilo_drive_through` (782 at `LOD0`) given the
extra openings and pipes.

## LOD review

Intended switches are the catalog defaults: 35, 70 and 120 m, with no
overrides.

The review camera was perspective, 1920×1080, 50° vertical FOV, with
distance along the view to the front or rear bounding face
(`scripts/review_asset.py`). Rendering was Cycles CPU, 16 samples with
denoising, AgX, exposure 0. Pairs compared:

- `LOD0`/`LOD1` at 30/40 m, oblique and front, noon;
- `LOD1`/`LOD2` at 65/75 m, oblique and rear, noon and reverse sun;
- `LOD2`/`LOD3` at 115/125 m, oblique and end-on (`left`), noon.

Renders are in the local, untracked
`review/power_plant_2026_11_21/hiilenvastaanotto_brick_shed/` (`lod/`).

- **The lane is open on every tier.** End-on at 125 m, `LOD2` and `LOD3`
  both show the ground through the portal.
- **Openings** go from recessed (`LOD0`/`LOD1`) to flush (`LOD2`). At the
  65/75 m switch the flush windows read a touch lighter, without the
  reveals' shadow, but the rhythm, size and frame colour are unchanged.
- **The tie beams** go at `LOD2`. They are seen only from inside the lane
  or end-on through a mouth, a dark bar under a dark ceiling; nothing
  visibly changes at the switch.
- **Massing** is unchanged on every tier: tower, lean-to, roofs, portals,
  columns and band (UV regions).
- **Downpipes:** `downpipes.MODES` on every tier; no tier drops them.
- **Coal dust** is texture only, the same on every tier.

Pending in the consumer: real LOD switching, shadows and ambient occlusion
in the lane, and performance.

## Interior geometry

The validator's hidden-surface test reports **10/8/10/10 triangles** on
`LOD0`–`LOD3` (0.9–2.1 %), all of them the gables' inner faces over the
lintels at x ±6.6 and 6.0–7.7 m. These are exterior surface, reachable only
along the 14 m lane, so few of the test's fixed rays escape; they are not
buried.

- The lane's walls, floor, ceiling, soffits and beams are exterior surface,
  open at both mouths.
- The shed's solid parts are the walls, the 0.02 m floor slab and the 0.42
  m over the ceiling. The lean-to and tower are solid: no interior is
  modelled.
- The kept closure faces are:
  - the floor caps under the shed, the lean-to and the tower;
  - the downpipes' shoe mouths.
- The walls' lids and the lean-to slab's buried end are removed by the
  union.

## Known simplifications

- **Lane:** no lighting, weighbridge, wheel guards or signage. The grate and
  its pit are painted on the 0.02 m floor slab; the pit is not modelled.
  The high windows are not shown from inside the lane, where the front wall
  is plain brick.
- **Interiors:** the elevator, its casing, the drive, the attendant's room
  and the stair are not modelled. The windows are closed opaque panes and
  the hatch is a closed steel plate.
- **Painted detail:** the frame's columns, the ring beam and lintels, the
  impact wall, purlins and rafters, sheet ribs, the bond and the snow guard.
- **Ground:** the asset has no ground. The coal spilt round the grate and
  at the walls' feet is carried by the floor slab, the lane's walls and the
  walls' plinths.

## Texture set

One 1024² trim-sheet atlas, rasterised by `scripts/atlas.py` at `atlas.SS`
= 4, padded last by `atlas.pad()`. Layout, in rows from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–422 | BRICK (x 0–960) and column strip (x 972, 0.40 m) | U along the wall, V = height 0–6.5625 m, 64 px/m: plinth to 0.625, bond, band 6.0–6.5625 |
| 428–524 | ROOF | U = x at 64 px/m; V up the slope from the eave edge, 96 rows over 3.81 m (25 px/m); ridge cap at the main slope's top |
| 532–548 | EAVE | the fascia (0.25 m) with the gutter |
| 558–1020 | unique | lane side walls (448 × 246), ceiling (448 × 92) and floor with the grate (448 × 179) at 32 px/m; the windows, door, hatch and louvre at 64 px/m; flat patches |

**Deviations from 64 px/m:**

- The lane's regions are at 32 px/m. They are in shade and seen
  obliquely; at 64 px/m they would need most of the atlas. Relief there is
  scaled by 32/64 so the normal map's slopes stay physical.
- The roof band is stretched in V; only its ribs vary there.

### Walls above the band

The band ends at 6.5625 m. Higher walls (the gables, the long walls'
strip under the eave and the tower to 13.37 m) sample the brick rows 3.75 m
lower, and the tower above 9.5625 m 7.5 m lower. Each shift is 48 courses,
the bond's tone period, so bond and tone run on across the split. The
shifted walls sample rows 2.06–5.87 m, which `check_layout()` keeps inside
clean brick: no height-following weather above 1.9 m, no runs below 5.90 m.

The lean-to roof samples the roof band scaled by 0.84, so its buried end
stops short of the ridge cap's rows.

### Relief

| Feature | Relief |
| --- | --- |
| Brick face over mortar | 6 mm |
| Band, column arrises | 10 mm, 8 mm |
| Window frames, bars, sash | 35, 22, 40 mm |
| Roof ribs | 30 mm |
| Gutter roll | 70 mm |
| Snow guard tubes | 45 mm, scaled by the band's stretch |
| Grate bars over the coal | 40 mm, scaled by 32/64 |

The bond and ribs read raised in the 22–25 m noon and morning renders.

### Weathering and coal dust

Weathering follows `scripts/weathering.py`'s moderate level: grime, fade on
painted steel and frames, wash on brick, plinth soil and algae, splash-back,
light efflorescence to 1.4 m, roof dirt toward the eave, and runs under the
band and the gutters.

Coal dust has its own field: `scripts/weathering.py`'s coal field `K`,
laid by `Weather.coal()` and carried by `pad()`, which lerps the weathered
colour toward the atlas's `COAL_DUST` (sRGB 44/43/42, passed as the
`Weather`'s `coal_dust`; clipped at 0.9), adds 0.22 roughness, strips the
metallic and deepens the shade by 0.30 of it. Where the dust lies:

- **every wall's foot:** 1.0 at the ground, falling by 1/e every 0.60 m and
  gone by 1.9 m, plus 0.25–0.40 over the plinth, all on rows whose V is
  height;
- **light haze over all the brick:** 0.05–0.17 in broad patches and runs,
  nothing that follows height;
- **the lane's walls:** 0.30 everywhere, 0.55 more at the foot, and up to
  0.30 more at the mouths' jambs;
- **the ceiling:** 0.30, rising to 0.65 over the grate;
- **the floor:** heavy round the grate and along the walls, lighter in the
  wheel tracks and at the mouths, where rain reaches;
- **the roof:** light, 0.05–0.13.

Measured albedo, sRGB band means:

| Surface | `red_brick` | `yellow_brick` | `brown_brick` |
| --- | --- | --- | --- |
| Plinth (0–0.6 m) | 69 | 69 | 69 |
| Brick 0.6–1.9 m | 123/78/64 | 154/138/109 | 90/70/60 |
| Brick 2–5.9 m | 132/82/67 | 165/149/117 | 95/74/62 |
| Band | 155 | 155 | 155 |

In the lane (all variants alike): side walls ~74 at the foot; floor ~101 at
the mouths, ~48 at mid-length and ~24 over the grate; ceiling ~56. The roof
is ~61. The plant reads as working, not abandoned: the dust darkens and
mattes, with no rust streaks, peeling or growth.

### Lane occlusion

The lane's walls fall to shade 0.62 and AO 0.48 by 3.5 m in from either
mouth. The ceiling falls to 0.50 and 0.38, the floor to 0.70 and 0.55. All
darken further into their corners. The lane is open at both ends, so this
is symmetric about mid-length, and one side region serves both walls.

### Filtering

Whole-atlas mip4 stress renders (`scripts/review_atlas_mips.py`) of `LOD2`
and `LOD3` at 120 m, oblique, grazing and rear, under noon sun. They showed
no brick/roof colour leaks and no dark seams; the columns, band, windows
and dark lane all hold. The pale rear roof slopes there are the noon sun's
glint, the same at full resolution.

### Unique textures

Six 1024² RGB PNGs, about 24 MB uncompressed (4 MiB each in memory without
mips): three albedos, plus one ORM, one normal map and one emission mask
shared by all variants.

## Glazing treatment

The glazing uses `scripts/glazing.py` `rooms()` on the finished albedo, with
the default base. It measures sRGB 65 (linear 0.050) in all three albedos,
0.32–0.36× the trim. Roughness is 0.08 (`glazing.ROUGHNESS`) and metallic 0.

- The shed's windows are steel frames of 7 × 4 lights with a hopper. The
  small windows are 3 × 4 lights.
- Two regions of each size alternate, so neighbouring windows show
  different rooms.
- The steel frames (sRGB 206, 104 or 186 by variant) are lighter than the
  glass.

There is no departure from the Style Direction band.

## Variant list

| Variant | Meaning |
| --- | --- |
| `red_brick` (default) | red facing brick, light grey steel windows, grey-green doors and hatch, dark grey roof |
| `yellow_brick` | yellow facing brick, dark green-grey windows, oxide-red doors |
| `brown_brick` | brown facing brick, light windows, blue-grey doors, darkest roof |

These are the plant's brick trio, matching the catalog's other brick works
buildings. The concrete, the coal dust and the galvanised rainwater steel
are the same in all three. Geometry, UVs, ORM, normal and emission are
shared.

## Night lighting

**Night-lit: it ships `_emission.png`.**

- **Mask:** the window glass only, via `glazing.night_rooms()`. That covers
  the shed's three high windows, the tower's two, the lean-to's three and the
  attendant's window onto the lane.
- **Not lit:** the doors, the hatch, the louvre, and the lane itself.
  There are no lamps or signs.
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

`export/hiilenvastaanotto_brick_shed.model.json`, in the glTF frame:

- **footprint:** the shed rectangle with the lane inside it, its mouths
  closed across their wall planes as `hiilisiilo_drive_through` does, plus
  the lean-to and the tower's step (Footprint).
- **storeys:** one at the ground, 29.50 m². That is the lean-to's rooms
  inside 0.30 m walls (8.60 × 3.30 m) plus the tower's step (2.80 × 0.40
  m). The lane is not a storey, as for `hiilisiilo_drive_through`.
- **dwellings:** none.
- **doors:**
  - `attendant`: `entrance`, main, the lean-to's east end, facing +X;
  - `elevator`: `service`, the tower's rear face, facing −Z.

  The lane's mouths are not doors.
- **passages:** one, `truck_lane`, stated from the west mouth (glTF −X). It
  works both ways and nothing favours either mouth, so the brief's default
  stands.
  - position [−7.0, 0, 1.925]: the lane's centre line on the west gable's
    outer plane;
  - forward [1, 0, 0];
  - width 5.60 m between the side walls, length 14.00 m to the east
    gable's plane, through (open at the far end);
  - clear height 5.98 m. It is measured on the exported `LOD0` mesh by
    `measure_lane()`: every triangle clipped to the lane's plan, inset 1
    mm. The lowest point over the floor is the lintels' soffit at 6.000 m,
    above the floor slab's top at 0.020 m.

## Review status

Checked here, in Blender:

- **Validator:** `scripts/validate_asset.py`, 0 FAIL. The one WARN is
  `source.dirty`, from an uncommitted tree. Every tier passes:
  - welded manifold topology, one material, uri-only images;
  - the normal and emission bindings, the default-off factor;
  - triangle ceilings, pivot at ground and centred;
  - hidden surface 10/8/10/10 (Interior geometry).

  The glazing measures within its band in all three albedos.
- **Layout:** `check_layout()`, including the lane's clearances and the
  ground beyond the mouths.
- **Six views:** `LOD0` (`review_asset.py --six-views`). The end views show
  straight through the lane.
- **Lane views:** perspective from 20 m off each mouth on the centre line,
  and from inside. Both show the far mouth and the lit ground beyond, with
  nothing in the way.
- **Close renders:** 22–25 m, front, oblique, rear and grazing, under noon
  and morning sun. They checked the portals, the grate seen through the
  east mouth, the attendant's window, the door's scale, and the coal dust.
- **Sidecar against `LOD0`:** the clear height is measured on the exported
  file; both doors sit on their walls' outer planes, facing out.
- **LOD pairs:** around 35, 70 and 120 m, under two sun directions.
- **Filtering:** mip4 stress renders at 120 m.
- **Variants:** day and night for all three (`variants.png`).

Pending in the consumer:

- import, orientation and pivot on reimport in the engine;
- that its trucks fit the lane: 2.6 m wide, against 5.60 m clear and 5.98 m
  over the slab;
- that the 0.02 m slab edge across the mouths is acceptable to its driving;
- LOD switching, shadows and AO in the lane;
- filtering of the stretched roof band and the 32 px/m lane regions;
- night intensity;
- performance.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`) throughout.
The MCP addon was not used. Texture generation used the system Python 3
with numpy, scipy and Pillow.
