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
steps or handrails.

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

At `LOD0`/`LOD1` each opening is cut into the brick with four cheeks and a
closing plane set back 0.20 m (windows, entrance screen), 0.25 m (machinery
door) or 0.15 m (louvres):

- The cheeks are the wall's own brick, unrolled round the corner so the
  coursing and the plinth run on into them.
- The sill is a concrete patch.
- A head under the lintel band is the band's concrete.
- Doors have no threshold cheek; the floor cap covers the recess.

At `LOD2`/`LOD3` each opening is the same rectangle, flush.

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
| `LOD0` | 540 | 12,000 |
| `LOD1` | 444 | 4,000 |
| `LOD2` | 216 | 1,500 |
| `LOD3` | 208 | 500 |

The building is one box with a gable roof and thirteen openings, so the counts
are low and are not padded. They sit beside the catalog's houses and under the
two-storey terraces, which is expected for a single-volume hall.

At `LOD0` the triangles go to:

- the thirteen recessed openings (cheeks, closing planes and the wall round
  them), about 300;
- the two 8-sided downpipes with their bends, about 150;
- the two 8-sided vents and the roof slab, the rest.

`LOD1` saves on the pipes' and vents' sides. `LOD2` flattens the openings,
which halves the count again. `LOD3` keeps everything `LOD2` has; only the
downpipes go to three sides. A further cut would have to remove the downpipes
or the last vent. Both are light marks still seen past 120 m, and the tier is
well under its ceiling, so they stay.

## LOD review

Review camera: `scripts/review_asset.py`, perspective, 50° vertical FOV,
1920×1080, distance along the view direction to the centre of the facing
wall. Views were front, oblique (40° azimuth, 30° up) and aerial (40°, 45°).

| Switch | Intended distance | Renders |
| --- | --- | --- |
| `LOD0` → `LOD1` | ~35 m | 30 m and 40 m, `LOD0`/`LOD1`, noon and reverse sun |
| `LOD1` → `LOD2` | ~70 m | 65 m and 75 m, `LOD0`/`LOD1`/`LOD2`, noon and reverse |
| `LOD2` → `LOD3` | ~120 m | 115 m and 125 m, `LOD0`/`LOD2`/`LOD3`, noon and dusk |

No distance overrides.

- **35 m.** `LOD1` is indistinguishable from `LOD0`. The pipes' and vents'
  fewer sides are under a pixel's difference.
- **70 m.** Flattening the openings loses the reveal shadow, about 1.5 px.
  The steel frames then read a little lighter at `LOD2`. The window rhythm,
  the lintel band, the machinery door, both louvres and the roofline are
  unchanged under both sun directions. The 0.16 m vent (under two pixels)
  goes at this switch and is not missed.
- **120 m.** `LOD2` and `LOD3` are the same shape, and no transition is
  visible.

The windows' dark glass and light frames, the concrete band and plinth, and
the dark roof hold on every tier. The working renders are in
`review/mine_2026_11_20/nostokonehuone_brick/` (local, git-ignored).

These are authoring comparisons. Consumer switching, filtering and
performance are pending.

## Interior geometry

The validator's hidden-surface test reports **0 hidden triangles on every
tier**. The only closure faces are the buried wall-ring floor and lid and the
buried tops of the pipes. The union removes all of them. Recessed glass, door
leaves and louvres are exterior surfaces.

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
| 586–1020 | unique | the two window regions, the entrance screen, the machinery door, the louvre, the vent pipe and its open end, flat patches |

`PIPE_STRIP` is rows 567–572, the gutter's middle. The downpipes sample it and
measure sRGB 130/133/133 in every variant. That is the galvanised steel of the
farm buildings (`ID_GUTTER`, 134/137/137, roughness 0.48, metallic 0.60). The
snow guard is the same steel.

Two window regions (`window`, `window_b`) are alternated along each wall, so
neighbours show different rooms behind the glass. The bands have 6–8 px
gutters. `pad()` fills every unclaimed texel from the nearest region's edge.

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
- soot runs on the louvres and the vent pipes.

Cavity dust settles in the mortar joints. Glass stays clean.

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
  across tiers at 115–125 m dusk.
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

- `scripts/validate_asset.py`: 0 FAIL.
  - All four tiers have uri-only external images, one opaque material slot,
    welded manifold topology and 0 hidden triangles.
  - The pivot is at ground level and centred.
  - Every tier binds emission on UV0, default off, and the normal map at
    scale 1.
  - Six 1024² RGB PNGs; normal vectors are unit length and face out.
  - The glass measures in band and darker than the trim.
  - The facts sidecar is consistent.
  - The one warning is `source.dirty` in the sidecar, expected until the
    asset is committed and the sidecar regenerated with `build.py -- facts`.
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
- The tier comparisons at the three switches, the mip 4 stress renders and
  the day cycle, recorded under LOD review and Texture set.
- The variant sheet (`variants.png`): day and night for all three colours.

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
