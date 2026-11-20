# kaivostorni_concrete

## Style brief

The headframe (*kaivostorni*, *nostotorni*) of a small mid-century Nordic
mine, built as a generic composite. It is the landmark that makes a site read
as a mine from a city-builder camera 35–150 m away, so the silhouette leads: a
tall, plain concrete shaft tower carrying a wider head room at the top for
the winding gear, with a low annex at its foot. It is the cast-concrete type
of the 1920s–50s, not an open steel lattice: the catalog is fully opaque.

- **Shaft tower:** 6 × 6 m, board-marked cast concrete with horizontal board
  imprints, a lift line every 2 m, plugged form-tie holes and rain streaks.
  It stands on a base 0.25 m wider each side, 3.70 m tall, with a 45°
  weathered top.
- **Head room:** cantilevered 0.80 m east and west, flush front and back,
  from 17.0 m to its 20.8 m eave. A strip of small steel-framed windows on
  the front (four) and back (three), two louvred steel vents in each
  cantilevered gable. A shallow 15° profiled-steel gable roof, ridge along X.
- **Shaft windows:** small steel-framed stair-landing windows: three stacked
  over the door on the front, staggered on the other faces.
- **Shaft-collar annex:** a single-storey concrete annex on the east side
  under a 10° mono-pitch steel roof falling away from the tower, with a pair
  of braced steel leaves (3.20 × 3.40 m) on its front.
- **Tower door:** a plain steel pedestrian door in the base's front, the main
  entrance.
- **Rainwater and access:** painted half-round galvanised gutters on the
  three eaves, modelled downpipes from each, painted snow guards on every
  slope, and a galvanised wall ladder up the back from the ground to a metre
  above the roof's edge.
- **Finish:** grey concrete with grey-green steelwork by default; an ochre
  lime-wash variant with oxide-red doors.

## Category and secondary use

`buildings/industrial/`. No secondary use.

## Hero/landmark status

**No.** Ordinary budgets and a 1024 atlas, although the asset is a landmark
by role: its counts sit well inside the ordinary ceilings.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Shaft | 6.00 × 6.00 m |
| Base | 6.50 × 6.50 m |
| Head room (0.80 m cantilevers east and west) | 7.60 × 6.00 m |
| Annex, beyond the base's face | 4.15 × 5.20 m |
| Base and annex walls together | 10.65 × 6.50 m |
| Overall, with overhangs, downpipe shoes and ladder | 11.90 × 7.10 m |

Heights:

| Feature | Height |
| --- | --- |
| Base vertical faces / sloped top into the shaft | 3.70 / 3.95 m |
| Cantilevers' soffit (head room underside) | 17.00 m |
| Head room eave (underside at the wall) | 20.80 m |
| Head room ridge top | 21.85 m |
| Wall ladder top | 21.94 m |
| Annex eave (outer wall) / underside at the shaft | 4.30 / 5.08 m |

The pivot is centred on the plan's bounding box at ground level: 1.85 m east
of the shaft's centre and 0.03 m behind it. It is taken from `LOD0` and
applied to every tier.

The facts sidecar's footprint is the base and annex wall outline, eight
corners. **Outside it but inside the bounds:** the head room's two
cantilevers and the roofs' overhangs (overhead), the tower downpipes' lower
runs and shoes on the base's front and back faces, the annex downpipe on its
east wall, and the wall ladder, which stands on the ground 0.27–0.33 m behind
the base's back face.

## Story height

**One occupied storey**: the ground floor of the tower base and the annex,
floor at 0.10 m. The annex is a single storey, 4.30 m to its eave, sized by
the 3.40 m vehicle door. The shaft and head room are machinery space (hoist
compartments, stair, sheave floor), not occupied storeys, so the
3.0–3.3 m rule does not apply. The 4 m lift-pair rhythm and the landing
windows at 1.2 m above each joint give the shaft a readable vertical scale.

## Door leaf height

| Door | Leaf (w × h) | Threshold | Notes |
| --- | --- | --- | --- |
| Tower door, base front (entrance, main) | 0.95 × 2.10 m | 0.10 m | no transom; smooth surround 0.12 m above |
| Collar door, annex front (vehicle) | 3.20 × 3.40 m (two 1.60 m leaves) | 0.10 m | no transom |

The 2.10 m steel leaf is the human-scale anchor, beside the vehicle door on
the same front. The vehicle door is a goods opening, not a pedestrian leaf.

## Window sills

All windows are the same 0.80 × 1.00 m steel-framed window (two lights
across, three up), on a 0.15 m precast sill.

| Face | Sills | Heads |
| --- | --- | --- |
| Base back, base west | 1.50 m | 2.50 m |
| Annex east | 1.50 m | 2.50 m |
| Shaft front | 5.20, 9.20, 13.20 m | 6.20, 10.20, 14.20 m |
| Shaft west | 6.60, 14.60 m | 7.60, 15.60 m |
| Shaft east | 9.20 m | 10.20 m |
| Shaft back | 10.60 m | 11.60 m |
| Head room front (4) and back (3) | 18.10 m | 19.10 m |

The ground-floor sills are 1.40 m above the floor, at the chest-high limit,
which suits a plant room. The head-room sills are 1.1 m over the head room's
underside. Louvres (1.20 × 1.00 m): head room gables sill 18.10 m; annex back
sill 2.00 m. No opening crosses a 4 m joint (`check_layout()`).

## Eave overhang

| Where | Projection |
| --- | --- |
| Head room eaves (front and back) | 0.40 m |
| Head room rakes (east and west) | 0.30 m |
| Annex eave (east) | 0.40 m |
| Annex rakes (front and back) | 0.25 m |

The annex rakes are kept short so they end 0.15 m behind the shaft's face
planes. Soffits slope with the rafters. The cantilevers' undersides are flat
concrete soffits. Every tier keeps every overhang.

## Construction

`build.py` builds closed solids and unions them with Blender's exact boolean
(`asset_build.union`):

- the tower: shaft and head room as **one ring of walls**;
- the base;
- the annex;
- the head room's roof slab, a chevron along X;
- the annex's mono-pitch slab;
- three downpipes (`scripts/downpipes.py`);
- the wall ladder (`scripts/roof_safety.py`), on `LOD0`–`LOD2`.

Parameters the tiers derive from:

| Parameter | Value |
| --- | --- |
| Shaft half-size `TX`/`TY` | 3.00 m |
| Head room half-length `HX` | 3.80 m |
| Base half-size `BX`, top `Z_BASE`, slope run `BASE_IN` | 3.25 m, 3.70 m, 0.35 m |
| Head room underside `Z_HEAD`, eave `Z_EAVE` | 17.00 m, 20.80 m |
| Head room pitch | 15° |
| Annex `AX0`..`AX1`, half-depth `AY` | 2.85..7.40 m, 2.60 m |
| Annex pitch, eave | 10°, 4.30 m |
| Downpipes | `PIPE_SPOTS`: front s 6.45, back s 1.15 (both x 2.65), annex east s 0.30 |
| Wall ladder | back eave wall, s 6.00 (x −2.20) |

### The tower as one ring

The head room is flush with the shaft on the front and back, so a separate
head-room box would overlap the shaft with coplanar faces. Instead the front
and back walls are a T outline (the shaft's width below 17.0 m, the head
room's above), the east and west sides are a shaft wall, a soffit quad and a
gable wall, and `close_solid()` caps the ring's foot (buried in the base at
1.0 m) and its lid (in the roof slab, split at the ridge). `clip_z()` cuts
the T into horizontal strips exactly, since every slab crosses it in one
piece.

### Walls cut at the 4 m joints

Every wall is clipped into strips at 4, 8, 12, 16 and 20 m. Below 4 m it
maps the S1 band from the ground; each strip above maps W2 from its own
joint, each 3.30 m further along U, so the 4 m repeat does not line up in a
column. The joints coincide with painted lift lines, so neither the strip
seam nor the U shift shows. Corners carry the same cut heights on both walls.

### Base and annex

The base's four walls stop at 3.70 m and a 45° sloped top runs in to 2.90 m
at 4.05 m, inside the shaft; the union leaves a weathered ledge meeting the
shaft at 3.95 m. The annex runs 0.15 m into the shaft (no coincident walls)
and is set back 0.40 m from the shaft's front and back faces.

### Gutters and downpipes

The gutters are painted (FASCIA band) along the head room's two eaves and the
annex's east eave. The pipes hang from them on swan-necks
(`DP.eave_pipe`). The two tower pipes run straight down the shaft's face,
which is flush with the head room's, 0.35 m from the shaft's east corners.
The base stands 0.25 m proud of the shaft, which `scripts/downpipes.py`
cannot step round, so `build.py` subclasses `DP.Pipe` as `StepPipe`: a 45°
jog out by 0.25 m ending at 3.95 m, over the base's sloped top, then the
module's own path below. **The tower pipes keep their shoes and four sides on
every tier**: the front pipe's shoe is the building's −Y extent, and a
three-sided ring's corner, or a dropped shoe, moved the extents between
tiers. The annex pipe uses `DP.MODES` unchanged.

### Snow guards

Painted in the ROOF band 0.5 m up from each eave, in the gutter's galvanised
id, as on the catalog's other steel roofs.

### Roof safety

The head room roof carries nothing serviced, so the kit is not required.
The brief asks for a ladder for the read, and one serves the roof, the
gutters and the head room from outside. It is `RS.WallLadder` on the back
eave wall, west of the windows, from the ground to 1 m above the roof's edge,
passing 0.12 m outside the fascia. Its brackets below 3.95 m run into the
base. **No cage**: the module has none, and see-through hoops would be thin
opaque bars costing hundreds of triangles; a real 22 m ladder would carry a
cage or a fall-arrest rail. There is no roof ladder or walkway. The ladder
sets the +Y extent and the top, so `LOD3` keeps its bare rails
(`RS.solids(extents=True)`, appended after the weld).

### No handrails

Both thresholds are a single 0.10 m step.

### check_layout()

Asserts, before building:

- openings leaving their wall's visible outline (corners, the cantilever's
  step, the soffit), taking in a corner, crossing a joint, or overlapping;
- the annex outgrowing the first W2 strip, its rakes reaching the shaft's
  faces, or its roof reaching the head room;
- the head room's apex outgrowing the last strip; the soffit on a joint;
- the annex slope disagreeing with the roof band, or the head room's slope
  being longer than it;
- downpipes within `DP.CORNER` of a wall's or the shaft's corner or within
  `DP.CLEAR` of an opening (`DP.problems`), and the back pipe crowding the
  ladder;
- the ladder within `RS.CORNER` of the shaft's corners or crowding any
  opening at any height on the back, the base's included, or the pipe
  (`RS.problems`).

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 3,246 | 12,000 | surround rings, reveals and closures on all 24 openings; downpipes 8-sided with swan-necks; ladder with all 77 rungs and its brackets |
| `LOD1` | 2,142 | 4,000 | each opening one recess the size of its surround; pipes 4-sided bent; every other rung |
| `LOD2` | 882 | 1,500 | openings flush; coplanar splits dissolved; pipes 4-sided straight (tower pipes keep jog and shoe); every fourth rung, no brackets |
| `LOD3` | 472 | 500 | as `LOD2`; annex pipe 3-sided; ladder reduced to bare rails |

Where the triangles go, measured by building without each part:

| Tier | Ladder | Three downpipes | The rest |
| --- | --- | --- | --- |
| `LOD0` | 2,140 | 308 | ~800 |
| `LOD1` | 1,380 | 156 | ~600 |
| `LOD2` | 424 | 102 | ~356 |
| `LOD3` | 16 | 100 | ~356 |

The building itself is four boxes, two slabs and 24 openings, polygons with
holes rather than grids; board marks, lift lines, ties, frames, louvres and
door bracing are texture. The ladder is two-thirds of `LOD0`: 77 rungs on a
22 m ladder. `LOD3` sits 28 under its ceiling, mostly the 24 flush openings'
holes and the strip cuts the tiling band needs.

## LOD review

**Intended switches: 35 / 70 / 120 m**, the catalog defaults; no overrides.
Reviewed with `scripts/review_asset.py` on the exported tiers: perspective,
1920×1080, 50° vertical FOV, Cycles, AgX, exposure 0, noon sun; oblique (40°
azimuth, 30° elevation) and rear (150°, 30°); all four tiers at 35, 70 and
120 m side by side. Renders are in `review/mine_2026_11_20/kaivostorni_concrete/lod/`.

- **Silhouette.** At 70 and 120 m every tier reads as a tall plain tower with
  a wider gabled head room, its cantilever soffits dark, and a low annex with
  a big green door: a headframe, not a house or a silo. Unchanged across
  tiers.
- **Openings.** Recessed to flush at 70 m changes only the shadow inside
  the reveals; every window, door and louvre keeps its place, size and dark
  glass.
- **Ladder.** Reads on the back and above the roof edge at 35 and 70 m; at
  120 m `LOD2`'s every-fourth rungs and `LOD3`'s bare rails read alike, a
  pale double line.
- **Downpipes.** The front pipe and its jog over the base read at 35 m; past
  70 m a thin line.

Six working views at `LOD0` (orthographic front, back, sides, top; raised
aerial) are in `views/`; close views at 25 m, morning and noon, in `close/`.

**Filtering.** `scripts/review_atlas_mips.py` wrote whole-atlas mip4 maps
(16 × 16 texel averages, albedo in linear light); `LOD2` and `LOD3` were
rendered at 120 m, oblique and grazing (75°), base against mip4
(`mip_base/`, `mip_mip4/`). At mip4 the lift lines and board marks average
out to a flat concrete grey, as they should at that footprint; the windows
and louvres stay dark, the doors stay grey-green, the roof stays dark, and no
colour leaks between the fascia, roof, ledge and wall bands. This is a stress
test, not the consumer's sampler.

## Interior geometry

Measured with `scripts/validate_asset.py` on the exports:

| Tier | Hidden triangles | Share | Vertical area |
| --- | --- | --- | --- |
| `LOD0` | 7 of 3,246 | 0.2 % | 0.1 m² |
| `LOD1` | 5 of 2,142 | 0.2 % | 0.4 m² |
| `LOD2` | 2 of 882 | 0.2 % | 0.4 m² |
| `LOD3` | 10 of 472 | 2.1 % | 4.3 m² |

The candidates are exterior surface the 40 sampled rays rarely escape: base
wall slivers behind the back downpipe's lower run, a sliver where the east
gable's top meets the rake soffit, and at `LOD3` the wall-facing sides of
the ladder's bare rails, 0.27–0.58 m off the wall. No wall stands inside the
building, by construction; the welded export is manifold on every tier.

## Known simplifications

- **No sheave wheels, hoist ropes or rope openings.** The winding gear is
  inside the head room; nothing ties the tower to a hoist house, whose
  placement belongs to the consumer.
- **No ladder cage** (Construction, Roof safety); no roof ladder or walkway.
- **Board marks, lift lines, tie holes, window frames and glazing bars,
  louvre blades, door ribs, braces, hinges and rivets** are texture; none
  clears the 0.25 m relief threshold.
- **Opening surrounds** are painted smooth concrete, flush with the boards.
- **The gutters and snow guards are texture**; the downpipes are modelled.
- **Streaks under individual windows or the cantilevers** cannot live in a
  tiling band; weathering is periodic noise and runs under every lift line.
- **One window type** for every window (Glazing treatment).
- **No ground slab, rails, skip or headgear yard.**

## Texture set

| File | Space | Notes |
| --- | --- | --- |
| `_albedo_<variant>.png` ×2 | sRGB | 1024², 8-bit RGB, no alpha |
| `_orm.png` | Non-Color | 1024², R = AO, G = roughness, B = metallic |
| `_normal.png` | Non-Color | 1024², OpenGL tangent space (+Y green up) |
| `_emission.png` | sRGB | 1024², neutral glazing mask |

Five unique 1024² textures: two albedos, plus one ORM, normal map and
emission mask shared by every tier and colour.

**Atlas layout** (`facade_atlas.py`):

| Rows | Band | Contents |
| --- | --- | --- |
| 0–262 | S1 | board-marked concrete, z 0–4.00 m from the ground |
| 262–526 | W2 | the same concrete, repeating every 256 rows (4 m), its opposite ends in its gutters |
| 530–550 | FASCIA | steel fascia, half-round galvanised gutter across its top 8 rows; `PIPE_STRIP` = its middle five rows, 540.5–545.5 |
| 554–670 | ROOF | profiled sheet, snow guard 0.5 m up, flashing at the annex's top |
| 674–710 | LEDGE | the base's sloped top, trowelled concrete |
| 716 up | unique | vehicle door, door, window, louvre, six flat patches |

`check_bands()` fails the bake on a stray id in a band; `check_regions()` on
overlapping unique regions; `atlas.pad()` fills the rest.

**One pattern, tiling in V.** S1 and W2 are painted by the same
`paint_concrete()`, phased so every 2 m is a lift line, so the pattern runs
on unbroken through z = 4 m. Every noise uses `tile_y=4`, the Weather object
too. Height-following weather (soil, algae, splash) goes on S1 only.

**Texel density** is 64 px/m, except the roof band (23 px/m up the slope,
its ribs along U), the ledge (stretched √2 up its slope) and the flat
patches.

**Relief heights** for `atlas.normal_map()`:

| Feature | Height |
| --- | --- |
| Board-joint grout fins | 1.5 mm |
| Board grain | ±0.5 mm |
| Lift lines | −4 mm |
| Form-tie holes | −10 mm |
| Precast sills | 35 mm |
| Window frames / bars | 25 / 15 mm |
| Door frames, rails, braces | 20 mm |
| Vehicle door ribs | 6 mm |
| Louvre blades | 22 mm |
| Roof ribs | 20 mm |
| Gutter (half-round radius) | 62.5 mm |
| Snow guard tubes / brackets | 35 / 30 mm |

The roof band's V-varying heights are scaled by its px/m over 64. Rasterised
by `scripts/atlas.py` at 4 × 4 samples per pixel; glass keeps a flat normal.

**Roughness / metallic:** concrete 0.90/0, smooth surrounds 0.86/0, sills
0.84/0, painted steel frames 0.50/0 and doors 0.55/0, glass 0.08/0, roof
0.46/0.25, fascia 0.44/0.25, galvanised gutter, pipes, ladder and snow guard
0.48/0.60 (sRGB 134/137/137). Dirt dulls all of them.

**Weathering** (`scripts/weathering.py`, moderate): grime; long rain streaks
and runs under every lift line, with lime bloom along the lines; soil, algae
and splash at the foot (S1); dirt and a green film on the base's ledge; the
roof band's runs and chalking; the fascia and gutter as the catalog's other
gutters; snow guard dust and rust; sills, door feet and handles; rust specks
on the painted steel.

## Glazing treatment

Panes are painted by `scripts/glazing.py`'s `rooms()` after the
id/shade/AO pass.

| | |
| --- | --- |
| base colour passed to `rooms()` | sRGB 68/73/77 (`glazing.BASE` × 1.35) |
| measured over the glass mask | mean sRGB 56, linear 0.035 (both variants) |
| relative to the brightest surround | 0.38× (grey), 0.30× (ochre) |
| frames | sRGB 92/100/96 (grey), 86/82/76 (ochre): lighter than the glass |
| roughness / metallic | 0.08 / 0 |

The atlas has one window region, so `rooms()` draws its room level once; at
`glazing.BASE` it measured sRGB 41, under the band, so the base is raised by
1.35 to land mid-band. The thin glazing bars merge into one pane.

## Variant list

Two variants, a restrained landmark (CLAUDE.md's large-scale case: one
coherent treatment per instance):

| Variant | Walls | Window frames, louvres | Doors | Roof |
| --- | --- | --- | --- | --- |
| `grey_concrete` (default) | bare grey board-marked concrete | grey-green | grey-green | dark grey steel |
| `ochre_render` | ochre lime wash over the concrete; the board marks show through | dark warm grey | oxide red | red-brown steel |

Glass, gutters, pipes, ladder and snow guards never change. Every `.glb`
references the default albedo; the other variant is that one file swapped.

## Night lighting

`kaivostorni_concrete_emission.png` masks the glass of the one window region,
painted as a lit room by `glazing.night_rooms()`. Doors, louvres, walls and
roofs are black.

**Bindings.** All four GLBs bind it through `emissiveTexture` on UV0 with
`emissiveFactor` `[0, 0, 0]` by default (`scripts/window_emission.py`); the
reference lit factor is the catalog's warm `LIT_FACTOR`.

**Control.** One region, so one building-wide control; per-window switching
is not possible. Occupancy, schedule, colour and intensity are the
consumer's.

**Preview.** `variants.png` (1280×1942): both colours at `LOD0`, a day row
with emission off over a night row at the reference factor, camera and
exposure fixed (`scripts/variant_previews.py`). Spill is Cycles' in the
preview only. Pending in the consumer: night exposure, spill, off/on across
LOD switches.

## Export

```
python3 facade_atlas.py export                         # textures, both variants
blender --background source.blend --python build.py   # tiers, preview, variants, sidecar
```

The first build ran without `source.blend` (`blender --background --python
build.py`), which creates it.

Export settings, from `scripts/asset_build.py`'s `export_all()`:
`export_format='GLB'`, `use_selection=True`, `export_yup=True`,
`export_apply=True`, `export_keep_originals=True`, `export_cameras=False`,
`export_lights=False`; one material, backface culling on;
`strip_embedded_images()` leaves image `uri`s only; the emission factor is
rewritten to zero.

**Bindings, per tier:** `baseColorTexture` → the `grey_concrete` albedo;
`metallicRoughnessTexture` and `occlusionTexture` → the ORM; `normalTexture`
at scale 1; `emissiveTexture` → the mask; all external PNGs on UV0. The
validator confirms the normal and emission bindings and uri-only images on
every tier.

`export/kaivostorni_concrete.model.json` is the facts sidecar, glTF frame:

| Fact | Value |
| --- | --- |
| hero | false |
| dwellings | 0 |
| bounds | [−5.95, 0, −3.548] to [5.95, 21.943, 3.548] |
| footprint | the eight-corner base and annex outline |
| storeys | one: floor 0.10 m, 63.83 m² |
| `tower` door | entrance, main; at [−3.35, 0.10, 3.282], facing +Z, 0.95 × 2.10 m |
| `collar` door | vehicle; at [3.50, 0.10, 2.632], facing +Z, 3.20 × 3.40 m |

## Review status

Checked here, in Blender 5.3.0, headless:

- `scripts/validate_asset.py`: no failures; one warning, the sidecar's
  `source.dirty` (the asset is not committed yet; rewrite with
  `build.py -- facts` from a committed tree). It confirms manifold welded
  topology, one material, uri-only images, normal map at scale 1, emission
  bound and default off, pivot, counts against the ceilings, the PNGs, the
  glass in the band, and the sidecar.
- `check_layout()` passes; every tier is manifold before export and shares
  `LOD0`'s extents.
- The six working views at `LOD0`.
- Tier comparisons at 35, 70 and 120 m, oblique and rear.
- Close renders at 25 m, morning and noon: board marks, lift lines and tie
  holes read as concrete, frames and sills raised, glass darker than its
  frames.
- The day/night sheet for both colours.
- Mip4 stress renders at 120 m (LOD review).

Pending, in the consumer:

- import and material control, LOD switching, sampler
  filtering and padding, MikkTSpace tangents, night exposure and spill,
  runtime performance.

## Tooling versions

- **Blender 5.3.0** (build 2026-11-11), headless, which saved `source.blend`.
  No MCP addon was used.
- **CPython 3.14.10, numpy 2.5.5, scipy 1.18.1, Pillow 13.0.0** for the
  texture export.

Recorded as known-good markers, not requirements.
