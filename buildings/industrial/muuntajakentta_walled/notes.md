# muuntajakentta_walled

## Style brief

The walled transformer yard (*muuntajakenttä*) of a small Nordic town's
coal-fired heat and power plant, 1950s–60s. It is one of five separate
pieces of one plant, with the boiler and turbine hall, the brick chimney,
the coal reception and the office. The pieces stand apart on the lot and
nothing joins them: this asset has no ground slab shared with the others,
and no cables or busbars leave its compound.

A compound of 16.0 × 12.0 m behind an opaque brick wall on brick piers,
closed at the front by a painted sheet-steel double gate with a
high-voltage warning plate. Inside:

- two power transformers in grey-green paint, each on a concrete plinth
  with a gravel oil bed. Each has a tank, a radiator bank on each long
  side, a conservator drum on saddles over the east end, three brown
  porcelain high-voltage bushings toward the gantry and a cable box on the
  east end;
- a board-marked concrete fire wall between the transformers;
- a galvanised H-section portal on the west (incoming) side. From its beam,
  a suspension string over each of the six phases holds a rigid tubular bus
  that slopes down to its bushing;
- precast cable trench covers from each transformer's cable box to the
  switchgear house.

The switchgear house is the asset's building. It is a single-storey red
brick box of 5.0 × 4.0 m under a flat felt roof on a concrete slab, with one
steel door to the street and steel louvres for ventilation. It stands in the
compound's front-east corner, its front and east walls in the yard wall's
outer planes, so the wall stops on it.

The asset is generic and stands for no particular installation. It carries
no lettering, brands or logos. The warning plates are a plain yellow
triangle with a lightning arrow.

## Category and secondary use

`buildings/industrial/`, as part of a power plant. There is no secondary
use: the switchgear house serves the yard and nothing else.

## Hero/landmark status

**No.** Ordinary budgets, a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Compound, the piers' outer faces (the plan bounds) | 16.00 × 12.00 m |
| Yard wall's centre line | 15.64 × 11.64 m |
| Switchgear house, outer walls | 5.00 × 4.00 m, x 2.94–7.94, y −5.94 to −1.94 |

Coordinates are in the Blender build frame (front −Y), origin at the
compound's centre.

- **Yard wall:** 0.24 m thick, 2.00 m high with its coping, on a 0.31 m
  concrete footing.
- **Piers:** 17 of them, 0.36 m square and 2.20 m high with their caps,
  about 2.3–3.1 m apart. There is one at each free corner, one each side of
  the gate, and one where the east run meets the house's north wall.
- **House:** its front wall stands in the yard wall's outer plane, y −5.94,
  and its east wall in the east wall's, x 7.94. The piers stand 0.06 m
  proud of both planes.
- **Gate:** in the front wall between piers at x −0.98 and 2.80, with
  3.42 m clear between them (x −0.80 to 2.62). The leaves are 0.06 m thick,
  set 0.08 m behind the wall's outer face, and run from 0.04 to 2.04 m
  high.
- **Transformer plinths:** 4.40 × 3.40 × 0.30 m, centred on x −2.00 and
  y ±2.70.
- **Fire wall:** x −3.80 to −0.20, 0.30 m thick on y 0, 3.80 m high.
- **Gantry:** columns at x −6.50, y ±4.60, on 0.70 m square concrete pads.
  The columns' tops at 7.45 m are the highest point.

The pivot is at ground level, centred on the plan's bounding box, which is
the compound's centre. It is taken from `LOD0` and applied to every tier.
Every tier has the same plan bounds, including `LOD3`, whose pier-thick
wall keeps the piers' outer faces (Construction).

The facts sidecar's `footprint` is the house alone, since CLAUDE.md's
footprint leaves out fences (Export). In the glTF frame (metres, +Y up, +Z
front, origin at the pivot) the house is the rectangle x 2.94–7.94, z
1.94–5.94.

## Story height

**One storey, 3.20 m** from the ground to the roof slab's underside line,
3.45 m to the slab's top. This is inside the 3.0–3.3 m band. It is a plant
room, not a habitable floor, and its height carries the high louvres over
the switchgear cubicles.

## Door leaf height

**Steel door leaf 1.00 × 2.10 m**, with no fanlight or transom. The pressed
steel frame adds 0.0625 m at the sides and head. The threshold is at
ground level and the door faces the street (−Y). It is the house's only
door.

The gate (two leaves, 3.42 m clear, 2.00 m high) is not a door in the
facts schema: it opens onto the open yard, not an occupied space. It reads
at the same scale as the wall it closes, under the 2.0–2.4 m band.

## Window sills

n/a: the house has no windows. It has five steel louvres, 0.875 × 0.50 m
in the clear, each in a 0.0625 m frame:

- **High louvres:** sill 2.30 m, head 2.80 m. One is on the front, two on
  the east wall and one on the north (yard) wall. Their heads stay 0.34 m
  under the slab, and their sills are 0.20 m over the door's head.
- **Low louvre:** sill 0.55 m, head 1.05 m, on the west (yard) wall, the
  intake under the high outlets.

## Eave overhang

**None.** The flat concrete roof slab is flush with the walls. Its 0.25 m
edge is painted as cast concrete with a drip line, a steel trim and the
felt dressed over it. Two reasons:

- The house's front and east walls stand in the compound's outer planes, so
  an overhang there would move the plan bounds and the pivot off the
  compound's centre.
- A flush slab with a trimmed edge is the period's ordinary detail for a
  small plant room.

The roof sheds over its edges. There is no gutter, so there are no
downpipes (CLAUDE.md, Geometry and Construction).

## Construction

`build.py` builds closed solids and unions them with Blender's Exact
boolean (`asset_build.union`). There is no ground: every solid stands on
z = 0 or on another solid. One mesh per tier.

### Orientation and the incoming side

- **Front (−Y):** the street, with the gate and the house's door. In the
  glTF frame it faces +Z.
- **West (−X):** the incoming side, toward the turbine end of the plant's
  hall, where the gantry stands. In the glTF frame this is −X.
- Nothing leaves the compound. The bus runs only between the gantry's
  strings and the bushings, and the trenches end inside the house.

### Yard wall

The yard wall is boxes:

- four runs, 0.24 m thick and 2.00 m high, each ending inside a pier or
  inside the house;
- 17 piers, 0.36 m square and 2.20 m high;
- the gate, as one 0.06 m plate whose ends run 0.05 m into its piers.

Every face is closed, both faces of the wall and its top included. The
gate's east pier stands against the house's front-west corner and runs
0.04 m into it. The east run ends inside a pier that runs into the house's
north wall, so no face of the wall is left coplanar and open against the
house.

On `LOD3` (only) the runs are one pier thick (0.36 m), centred so that
their outer faces are the piers' outer faces. The other 14 piers fold into
the wall, and the plan bounds stay 16.0 × 12.0 m. The two gate piers and
the junction pier are kept.

### Switchgear house

The house is one closed solid with its openings, built as the catalog's
brick buildings are (`nostokonehuone_brick`, `hiilisiilo_drive_through`):

- the four walls as regions on wall frames, the door notched into the
  front wall's foot, the louvres as holes;
- the 0.25 m slab edge as a strip on each wall;
- the flat roof and the floor as the two caps.

Openings by tier:

- **`LOD0`:** each opening is a casing ring round a recess, 0.12 m for the
  door and 0.10 m for the louvres;
- **`LOD1`:** one recess the size of the casing;
- **`LOD2`/`LOD3`:** a flush painted rectangle.

### Transformers

Each transformer is a set of closed solids:

- **plinth:** concrete, its top the gravel bed;
- **tank:** its base 0.05 m inside the plinth, its cover at 2.90 m;
- **radiator banks:** 2.00 × 0.55 m, z 0.70–2.55 m, run 0.05 m into the
  tank;
- **conservator:** r 0.28 m, its axis along Y at 3.40 m, on two saddles
  from the cover;
- **bushings:** three, turned from a profile, with a steel turret
  (r 0.15 m), a porcelain body tapering from r 0.115 to 0.075 m and an
  aluminium terminal, the tip at 3.95 m;
- **cable box:** on the east end.

The sheds, fins, bolts and valves are texture.

`check_layout()` keeps the following clear:

- the turrets inside the cover;
- the conservator clear of the bushings;
- the radiators 0.8 m clear of the fire wall;
- the fire wall 0.5 m past both tank ends and above the conservators;
- the plinths clear of the yard wall and 2 m from the house.

### Gantry, strings and bus

- **Columns:** H-sections 0.30 × 0.30 m (0.03 m flanges, 0.02 m web), from
  inside their 0.30 m pads to 7.45 m. Their flanges face ±X, so the H shows
  from the front and rear.
- **Beam:** an H on its side, 0.30 m deep and 0.24 m wide, z 7.00–7.30, from
  y −4.90 to 4.90.
- **Strings:** one over each phase at y = ±2.70 and ±2.70 ± 0.60, hanging
  0.85 m from inside the beam's bottom flange. Each has a cap, four discs
  of r 0.125 m at a 0.146 m pitch, and a clamp.
- **Bus:** a 0.06 m tube from inside each string's clamp to inside its
  bushing's terminal, sloping about 30°.

### Fire wall and trenches

- **Fire wall:** one concrete box standing on the ground between the
  plinths.
- **Trenches:** covers 0.60 m wide and 0.08 m proud, starting inside their
  plinths and ending inside the house. The south one runs straight into
  the house's west wall. The north one runs east, then turns south at
  x 4.70 into the house's north wall. It is one closed L, its top three
  quads so that the covers' joints turn with it.

### Authored parameters

`facade_atlas.py` holds every number both scripts use. `build.py` adds the
pier spacing, the runs and the tiers' modes (`mode()`).
`check_layout()` asserts the following:

- the openings sit clear of corners, piers, each other and the slab;
- the door leaf is in the 2.0–2.4 m band;
- the gate's piers frame the opening;
- the house's walls lie in the wall's planes;
- the clearances above;
- the bus's ends are buried, it clears the covers and its slope stays
  between 15° and 50°;
- the strings hang at least 1.5 m over the bushings' tips.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 3,580 | 12,000 | everything; turned disc strings (6 sides); 8-sided bushings and conservators; H-section gantry; house openings as casing rings round recesses |
| `LOD1` | 2,290 | 4,000 | strings as plain 6-sided prisms carrying the discs in paint; 6-sided bushings and conservators; openings one recess each |
| `LOD2` | 1,416 | 1,500 | bus tubes 3-sided; the conservators' saddles go; 4-sided strings, bushings (turret and one taper) and conservators; gantry members as boxes; openings flush; coplanar boolean splits dissolved |
| `LOD3` | 492 | 500 | strings and bus go; bushings one 3-sided taper; both radiator banks one box through the tank; cable boxes and pads go; trenches go; the wall one pier thick with only the gate and junction piers; the house's two yard-side louvres go |

Where `LOD0`'s triangles go, measured by building each group alone:

| Group | Triangles |
| --- | --- |
| Gantry, strings and bus | about 1,700, nearly all in the six turned strings (about 230 each) |
| Yard wall, 17 piers and gate | 644 |
| Each transformer | 440 |
| House | 164 |
| Trenches | 40 |
| Fire wall | 12 |

The union's intersections add the rest. `LOD1` keeps the wall (644) and
drops the strings to about 616 for the whole gantry.

**Comparison with the catalog.** `LOD0` is above the small brick buildings
(`nostokonehuone_brick` 540, `kaivoskonttori_brick` 896) because the yard is
mostly equipment, not wall plane. The strings are the one place triangles
buy silhouette below the relief threshold. At 20–35 m a disc string reads
by its scalloped outline; as a prism with painted discs it reads as a rod.
`LOD1` takes them back to prisms, so the difference shows only at `LOD0`'s
range. Trim in CLAUDE.md's sense (the piers, the house's slab edge and the
trench covers) is under 700 triangles, under a quarter of the ceiling.

**`LOD3` sits 8 triangles under its ceiling**, so any change to it must be
recounted. The wall was the expensive part: 17 piers unioned into the runs
cost 172 triangles at `LOD3`, and the pier-thick ring with three piers
costs 106.

## LOD review

Intended switches are the catalog defaults, 35, 70 and 120 m, with no
overrides.

The review camera was perspective, 1920×1080, 50° vertical FOV, with
distance measured along the view to the visible front or rear wall
(`scripts/review_asset.py`). Rendering was Cycles at 16 samples with
denoising, AgX, exposure 0. Pairs compared:

- `LOD0`/`LOD1` at 30/40 m, front and oblique, noon and reverse sun;
- `LOD1`/`LOD2` at 65/75 m, front, oblique and rear, noon;
- `LOD2`/`LOD3` at 115/125 m, front, oblique and aerial, noon and reverse.

Every working render is in the local, untracked
`review/power_plant_2026_11_21/muuntajakentta_walled/`.

- **`LOD0`→`LOD1`:** the strings lose their modelled discs and keep them in
  paint. At 30 m the only visible difference is the strings' outline, a few
  pixels wide. The house's openings go from ring to one recess, which is
  not visible at 40 m.
- **`LOD1`→`LOD2`:** the first build dropped the bus tubes at `LOD2`, as
  the brief allows. At 65 m they read as clear dark lines from each string
  to its bushing, and their loss cut the gantry off from the transformers
  at the switch. `LOD2` now keeps them as 3-sided tubes, for 144
  triangles. In the re-rendered 65/75 m pair the two tiers differ only in
  the strings' outline and the openings' recesses. The H-sections become
  boxes, the same 0.30 m outline. The openings go flush; the louvres'
  0.10 m recess was under 2 px.
- **`LOD2`→`LOD3`:** the strings and the bus go. Each string is 0.25 m,
  about 2.4 px wide at 120 m, under the beam, and the beam then carries
  nothing. That shows when the 115/125 m pair is blinked, not at a glance;
  `LOD3` has 8 triangles to spare, and keeping the strings would cost about
  70. The trench covers go too. From the aerial they are light strips
  against the studio's ground, and on a gravel yard they would be
  fainter. The bushings become single tapers and the radiator
  banks one box, keeping their outline. The piers' 0.20 m rise over the
  coping, about 2 px, goes from the runs but stays at the gate. The wall
  top's rhythm of light caps becomes a plain band; that also shows only
  when the pair is blinked. The two
  yard-side louvres go: the north one is seen only over the yard wall from
  raised views, and the west one only from inside the yard. The gantry,
  the tanks, conservators, fire wall, wall, gate and house keep their
  silhouettes on every tier.
- **Bounds:** every tier keeps the 16.0 × 12.0 m plan bounds and the
  pivot. The 7.45 m height is the gantry columns' tops, kept on every
  tier.

The six working views (`build.py:render_views`: orthographic front, rear,
east, west, top and a 45° front-right aerial) were looked at for `LOD0` and
`LOD3`. The first pass had a brick fire wall the full plinth length. In
the front elevation it read as a second building behind the wall, so it is
now board-marked concrete, cut to the tanks plus 0.5 m. The first pass's
empty north-east quarter of the yard read as a storage compound from above,
and the cable trenches to the house now give it a purpose.

Pending in the consumer: real LOD switching, shadows in the yard and
performance.

## Interior geometry

The validator's hidden-surface test reports 16 of 3,580 triangles at
`LOD0` (2.0 m²), 16 at `LOD1`, 5 at `LOD2` and 3 at `LOD3`, all PASS.

The candidates are the strips of each tank's long sides under its radiator
banks. They run between the plinth's top at 0.30 m and the banks'
undersides at 0.70 m, 0.55 m deep under the bank. That is exterior surface,
visible from low views along the plinth, but the test's 40 fixed rays from
each face's centre all strike the bank or the plinth.

What is removed and kept:

- No interior is modelled. The house is one closed solid, so its floor
  and roof are its caps and it has no room.
- The union removes every buried face: the tank's base in the plinth, the
  banks' and cable boxes' backs, the bushings' and saddles' feet, the
  strings' tops in the beam, the bus tubes' ends, the runs' ends in the
  piers and the house, and the trenches' ends.
- The only closure faces kept are the floor faces on the ground under the
  walls, piers, house, plinths, pads, fire wall and trenches.

## Known simplifications

- **This is a building-class asset whose shell is a compound.** The
  building is the switchgear house. The rest is a walled yard of
  electrical plant with no roof over it, open to the sky, with no ground
  modelled inside or outside the wall. The yard is meant to sit on the
  consumer's terrain.
- **No ground or yard surface:** the gravel bed is painted on the
  plinths' tops only. The trenches' covers stand 0.08 m proud, with no
  trench walls under them.
- **Equipment detail is painted:** the radiators' fins, the tanks'
  stiffeners, bolted flanges, valves, lugs and blank rating plates, the
  bushings' porcelain sheds and the cable box's lid are paint. On
  `LOD1`–`LOD2` the strings' discs are paint too.
- **No conductors leave the compound** and the gantry's beam carries no
  line. The portal stands for the yard's incoming side without wiring it
  to anything outside. The transformers' low-voltage side is the cable box
  and trench to the house, with no cables modelled.
- **No lattice:** the gantry is solid H-section steel, with no lattice
  (which would need alpha), no bracing and no earth-wire peaks.
- **One door and no yard door:** the house has no door into the yard, and
  the yard's only way in is the gate. The house's door is on the street.
- **No yard lighting, signage text, fence wire or barbed wire.**
- **No equipment inside the house:** the louvres are dark behind their
  blades.
- **One-sided gate artwork:** the gate's back shows the same leaves
  mirrored, so the warning plate appears on the inside too.

## Texture set

One 1024² trim-sheet atlas at 64 px/m, rasterised by `scripts/atlas.py` at
the default supersampling (`atlas.SS` = 4) and padded last by
`atlas.pad()`. Layout, in rows from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–248 | HOUSE band | U along the wall, V = height, 64 px/m; concrete plinth to 0.375 m, then stretcher-bond brick |
| 252–384 | FENCE band | U along the wall, V = height; concrete footing to 0.3125 m, brick, the precast coping from 1.906 m |
| 390–558 | unique, row A | tank side, gate, door, pier face, radiator face and end, conservator barrel, gravel bed |
| 566–734 | unique, row B | tank cover, roof, slab edge, radiator top, louvre, bushing, string, galvanised steel, cable box, conservator end |
| 740–1016 | unique, row C | flat patches, the fire wall's board-marked concrete, the trench covers |

### Deviations from 64 px/m

- **Gravel bed on the plinths' tops:** 40 px/m.
- **House roof:** 32 px/m. Both are horizontal surfaces of low-contrast
  gravel and felt, seen from above at a distance.
- **Gantry steel:** U at 64 px/m, V stretched along the members. It is
  uniform galvanised mottling with nothing that shows the stretch.
- **Bushings and strings:** wrapped once round, U by angle, V at 64 px/m
  along the axis.

### Relief heights for the normal map

- brick faces 6 mm over the mortar;
- coping and pier caps 20 mm;
- the gate's pressed ribs 8 mm and its frame 25 mm, hinges 40 mm;
- the door's frame 25 mm;
- louvre blades 30 mm;
- tank stiffeners 30 mm and flange bolts 40 mm;
- radiator fin edges 60 mm over their gaps, header pipes 80 mm;
- porcelain sheds 30 mm, painted discs 25 mm;
- felt laps 6 mm, scaled by 32/64;
- form-tie holes −10 mm.

### Weathering

`scripts/weathering.py`'s moderate level:

- **masonry:** grime, plinth soil, splash and salt bloom on both brick bands
  and the fire wall, dust on the copings and runs under them;
- **gate and door:** kicked dirt at the foot, grime at the hasp and handle,
  a little rust at the gate's foot;
- **transformers:** runs down the tank sides, dust on the covers,
  radiator tops and conservators, rust at the base frames and the
  radiators' lower headers;
- **ground surfaces:** dust and oil on the gravel and curbs, dust on the
  trench covers;
- **steel and porcelain:** light dust on the zinc, a trace on the
  porcelain;
- **slab edge:** runs down it from the felt.

### Filtering and inventory

Whole-atlas mip4 stress renders (`scripts/review_atlas_mips.py`) of `LOD2`
and `LOD3` were checked at 125 m: aerial, front and 75° grazing, under
noon. They showed no colour leaks between regions and no dark seams. The
brick stays brick-red, the copings and caps light, the gate dark and the
porcelain brown. The radiator fins merge to a dark grey, as their
shading intends.

Unique textures are five 1024² RGB PNGs: three albedos, one ORM and one
normal map, about 4 MiB each in memory without mips. The ORM and normal
map are shared by every variant.

## Glazing treatment

n/a: the yard has no glazing. No glass id is painted and
`scripts/glazing.py` is not used. The validator's glazing measurement does
not run, because there is no emission mask to select glass with.

## Variant list

| Variant | Meaning |
| --- | --- |
| `red_brick` (default) | red facing brick on the house and yard wall, grey mortar; the gate and door dark green |
| `yellow_brick` | yellow facing brick, pale mortar; the gate and door oxide red-brown |
| `brown_brick` | dark brown facing brick, grey mortar; the gate and door blue-grey |

The brick and its mortar are the plant's, the same three tones as
`nostokonehuone_brick`, so the yard can follow the hall it serves. The
painted steel of the gate and door moves with the brick, as that asset's
doors do. Geometry, UVs, the ORM and the normal map are shared.

Fixed in every variant:

- the electrical plant: grey-green tank paint sRGB (104, 114, 104),
  galvanised gantry (134, 137, 137), brown porcelain (98, 54, 36) and
  aluminium bus;
- the board-marked fire wall, the concrete and the gravel;
- the felt roof.

## Night lighting

**None. The yard is not night-lit, and it ships no `_emission.png`.** The
house has no glazing, only steel louvres, because an unmanned switchgear
room is ventilated, not lit for the street. CLAUDE.md's Output Contract
allows a building without glazing to ship no emission map. No yard lamp is
painted or lit. Consequences:

- **No `emissiveTexture` on any tier.** The validator's emission checks do
  not apply. The facts sidecar omits `textures.emission`.
- **No `variants.png`.** CLAUDE.md asks for it only of night-lit buildings.

`build.py` builds through the shared `asset_build.Asset` with
`night_lit=False`, which leaves out only the window wiring:

- `material()` wires no emission mask;
- `export_all()` sets no lit state and rewrites no emission factor;
- `render_preview()` has no emission state to set;
- `render_variants()` renders nothing.

## Export

```
python3 facade_atlas.py export                      # albedo x3, ORM, normal
blender --background source.blend --python build.py  # meshes, preview, sidecar
```

Run the textures first: the UVs index into the atlas, and the preview reads
it. A first build from a factory scene is
`blender --background --python build.py`, which creates `source.blend`.

### Export settings

As `asset_build`'s `export_all()` passes them:

- `export_format='GLB'`, `use_selection=True`, `export_yup=True`;
- `export_apply=True`, `export_keep_originals=True`;
- `export_cameras=False`, `export_lights=False`.

`scripts/glb_images.py`'s `strip_embedded_images()` then removes the
placeholder `bufferView` beside each image `uri`.

### Bindings

The validator confirms one material, uri-only external images, and
`normalTexture` at scale 1 on UV0 for every tier. The shared `asset_build`
material binds the same set on all four tiers:

- the default variant's albedo to `baseColorTexture`;
- the ORM's G/B to `metallicRoughnessTexture`;
- the ORM's R to `occlusionTexture`.

The material has backface culling on and exports single-sided and opaque.
The other variants swap the albedo file only.

The preview uses the catalog's fixed camera orientation, lens, sun and flat
grey world, with only the distance fitted (`asset_build.fit_camera`). It
shows `LOD0`, `red_brick`.

### Facts sidecar

`export/muuntajakentta_walled.model.json` states:

- **footprint:** the switchgear house's outer walls, 5.0 × 4.0 m;
- **storeys:** one, its floor at ground, 15.91 m² inside 0.24 m walls;
- **dwellings:** none;
- **doors:** one, the house's steel door (`entrance`, main), facing the
  street. In the glTF frame it is at [4.24, 0, 5.94], facing +Z,
  1.00 × 2.10 m.

The validator's "doors on the footprint" check fits: the door is on the
house's front edge.

The schema has no place for the compound, so these are recorded here
rather than in the sidecar. They are in the glTF frame: x, then z = −(build
y), +Z the front.

- **Wall line (piers' outer faces):** the rectangle x −8.00 to 8.00, z
  −6.00 to 6.00. The house fills its corner x 2.94–7.94, z 1.94–5.94.
- **Gate:** its centre on the wall's outer face at [0.91, 0, 5.94], 3.42 m
  clear between its piers, 2.00 m high, facing +Z.
- **Transformer plinths:** x −4.20 to 0.20, z 1.00 to 4.40 (south) and z
  −4.40 to −1.00 (north), 0.30 m high.
- **Gantry:** columns at x −6.50, z ±4.60, beam 7.00–7.30 m, tops 7.45 m,
  on the −X (incoming) side.

## Review status

Checked here, in Blender:

- `scripts/validate_asset.py`: 0 FAIL. The one WARN is `source.dirty`, from
  an uncommitted tree. On every tier the validator passes:
  - welded manifold topology;
  - one material and uri-only images;
  - the normal map at scale 1;
  - triangle ceilings;
  - pivot at ground and centred;
  - the hidden-surface test (Interior geometry).

  It also passes the five 1024² RGB PNGs and the facts sidecar's schema,
  hashes, tiers, footprint and door.
- `check_layout()`.
- The six working views at `LOD0` and `LOD3`, two passes.
- LOD pairs around 35, 70 and 120 m from front, oblique, rear and aerial
  views, under two sun directions. The 65/75 m pair was re-rendered after
  the bus was kept on `LOD2`.
- Whole-atlas mip4 stress renders at 125 m (Texture set).
- The catalog preview: the fixed camera sees over the front wall into the
  yard. The bushings, conservators, fire wall, strings, bus and gantry all
  show above the wall, with the gate and the house's door in front.
- The three variants from the catalog camera, `LOD0`. Each brick reads
  as one coherent brick with the painted gate and door, beside the same
  grey-green plant.

Pending in the consumer:

- import, orientation and pivot on reimport in the engine;
- LOD switching, shadows in the yard and performance;
- mip and anisotropic filtering of the stretched gantry steel, the radiator
  fins (a 3.2 px period) and the brick;
- the yard's placement on terrain, with no ground of its own.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`)
throughout. The MCP addon was not used. Texture generation used the system
Python 3 with numpy, scipy and Pillow.
