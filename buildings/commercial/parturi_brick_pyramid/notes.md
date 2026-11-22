# parturi_brick_pyramid

## Style brief

A late-1980s Finnish suburban barber's pavilion: one storey of yellow-buff
facing brick, 10 x 8 m, under a brown standing-seam steel hipped roof of one
pitch (21.8°) on all four sides, so short in the ridge (2.0 m) that it reads
as a pyramid. A dark brown brick plinth, a brown sheet sign band under the
eave across the front, brown aluminium frames, soldier courses over every
opening. Meant for a 20 x 20 m lot with the building at the back and a
forecourt for a few cars in front. It is deliberately not a flat-roofed box:
the roof, the entrance lobby and the projecting sign carry its identity.

The public side faces `-Y`:

- an **entrance lobby** (the Finnish windbreak) set 0.9 m into the brick left
  of centre, 2.2 m wide, with brick cheeks, a boarded soffit and a soldier
  lintel; at its back a brown glazed screen: one door leaf under a transom
  light and a sidelight with a kick panel;
- two windows to its right, each one big light under a top light, on the
  lobby's head line; vertical blinds are part of the room behind them;
- **PARTURI** (Finnish for barber) in cut cream capitals on the brown band,
  centred over the two windows;
- a square **light box** on two arms on the pier beside the lobby, standing
  out at right angles to the wall: white opal faces with PARTURI in deep blue
  and this asset's own comb-and-scissors mark.

The east wall has a two-light side window and a small staff window, the rear
the service door under a steel canopy and a high window, the west the meter
cupboard and an air louvre. On the roof: a louvred attic vent hood on the
front slope, a sheet-steel ventilation housing on the ridge (serviced, so the
roof safety kit climbs to it at the back), a soil vent on the rear slope.
Gutters on all four eaves, downpipes at two diagonal corners.

Generic and period-correct: no shop name, no brand, no barber pole (a much
later idiom here). Lettering is stroked from centrelines in `facade_atlas.py`;
no font file.

## Category and secondary use

`buildings/commercial/`. No secondary use: one salon room with a staff room
and WC behind it, which the side, staff and rear windows and the service
door imply.

## Hero/landmark status

Not a hero. Ordinary ceilings and the 1024 texture apply; both are met with
wide margins.

## Footprint

- Walls: **10.0 x 8.0 m** rectangle, less the entrance lobby's 2.2 x 0.9 m
  recess in the front wall; floor area 78.02 m².
- Plan bounds: **10.906 x 9.483 m**. Along X the eave (0.453 m each side)
  sets them; along Y the light box at the front (its outer edge 0.85 m off the
  wall) and the wall ladder at the back (its rails' fronts 0.633 m off the
  rear wall). Pivot offset from the wall plan's centre: (0, -0.108) m.
- Height: **5.904 m** to the ventilation housing's lid; ridge 5.344 m.
- Fits the 20 x 20 m lot with about 10 m of forecourt when set at the back.

## Story height

One storey. The level soffit meets the wall at **3.3125 m** (the eave
height); the sign band runs 2.75–3.3125 m on the front. Every wall height is
on a brick course line of the 85.9 mm coursing except the openings' common
head (2.363 m, half a course down so the soldier course above it ends on
course line 31).

## Door leaf height

- **Entrance:** one glazed aluminium leaf **0.95 m wide (stiles included) x
  2.10 m**, at grade with a threshold strip and no step. The transom bar is
  drawn at 2.10 m across the whole screen, with a **transom light** above it
  to the head frame at 2.363 m. The leaf stands 0.9 m back in the lobby; its
  facts threshold is on the front wall plane (Export).
- **Service door (rear):** brown steel leaf **0.94 x 2.055 m** in a 30 mm
  steel frame, frame head 2.105 m, soldier course over it to 2.406 m.
- Against the brick: the entrance leaf is about 24.5 courses tall.

## Window sills

| Window | Wall | Width | Sill | Head | Notes |
| --- | --- | --- | --- | --- | --- |
| front (x2) | front | 1.8 m | **0.859 m** | 2.363 m | top light over the 2.10 m transom bar; sheet sill 0.773–0.859 m |
| side | east | 1.4 m | 0.859 m | 2.363 m | two lights below the transom bar, top light |
| small (x2) | east, rear | 0.9 m | **1.289 m** | 2.363 m | one opening light |

All heads are on the entrance's head line; the transom bars on the door's
2.10 m leaf head. The highest sill, 1.289 m, is under the 1.4 m chest-high
line; the occupied floor is the ground.

## Eave overhang

**0.453 m on all four sides**, inside the 0.3–0.6 m default: a level boarded
soffit from the wall head at 3.3125 m out to a **0.25 m brown sheet fascia**
(top 3.5625 m), the painted half-round gutter across the fascia's top. No
parapet.

## Construction

Closed solids unioned with Blender's exact boolean
(`asset_build.union(..., snap=asset_build.SNAP)`), welded at 0.1 mm:

1. **the body:** the four walls walked counter-clockwise, each split into
   cells (brick to the band's foot at 2.75 m; above it brick, or on the front
   between s 0.2 and 9.8 m the sign band's artwork); each cell holed for its
   openings, or notched at its foot for the lobby and the service door; every
   cell corner on a neighbour's edge put on that edge, so the cells meet
   vertex to vertex; capped with a floor and a lid (`close_solid()`);
2. **the roof:** one solid: four slopes from the fascia top (3.5625 m) to the
   ridge (5.344 m, x ±1.0 m), the fascia, the four soffit trapezoids and the
   underside inside the wall line, which the union buries in the body;
3. **hip and ridge flashings** (LOD0/LOD1): five-sided caps in vertical
   sections along each hip and the ridge, 0.18 m wide, 35 mm proud, each hip
   cap stopping 0.2 m short of its eave corner so nothing passes the fascia;
4. **the ventilation housing** on the ridge, 1.0 x 0.8 m, 0.50 m over the
   ridge, foot buried 0.45 m, with a 60 mm lid overhanging 50 mm
   (LOD0/LOD1; a bare box from LOD2);
5. **the attic vent hood** on the front slope: 0.9 m wide, its louvred front
   0.40 m tall at y = -2.6 m, its top falling 3° forward back into the slope;
6. **the sign band** (LOD0/LOD1): 9.6 x 0.56 m, 0.10 m proud of the brick,
   its back in the wall and its top in the roof slab;
7. **the light box:** 0.70 x 0.70 x 0.15 m at x = -1.2 m, z 2.25–2.95 m,
   0.15–0.85 m off the wall (clear of the band), on two 40 mm arms let into
   the pier (one arm from LOD2);
8. **the rear canopy** (to LOD2): a 1.5 x 0.6 x 0.1 m steel tray over the
   service door;
9. **a soil vent** (LOD0/LOD1) on the rear slope, octagonal, r 0.06 m;
10. **downpipes** and the **roof safety kit** (below).

Openings: LOD0/LOD1 recess the glass and doors 0.12 m (brick reveals, sheet
sill) with the sheet sill and the soldier course flush on the wall; the lobby
is a 0.9 m recess through LOD2; LOD2 paints the windows and the service door
flush; LOD3 paints the lobby flush too (`item_mode()`). Ground-standing
openings get no floor of their own; the body's floor cap closes them.

Authored parameters: `facade_atlas.py`'s plan, heights, pitch, `ITEMS` and
regions; `build.py`'s `WALLS`, the light box, band, canopy, hood, vent and
cap constants, `DOWNPIPES`, the kit, and the per-tier switches
(`item_mode()`, `caps_kept()`, `band_modelled()`, `arms()`,
`canopy_kept()`, `housing_lid()`, `vent_kept()`).

### Rainwater

Half-round gutters painted on all four fascias (`PIPE_STRIP`). Two
**downpipes** (`scripts/downpipes.py`), swan-necked from the soffit: on the
west wall 0.3 m from its front corner (y = -3.7 m) and on the east wall 0.3 m
from its rear corner (y = +3.7 m), so the street front stays clear and each
side elevation shows one. `downpipes.problems()` checks both against the
corners and the openings. Tiers follow `downpipes.MODES` (8 sides bent, 4
bent, 4 straight, 3 straight); every tier keeps them.

### Roof safety equipment

The roof is 21.8°, steeper than 1:8, and the ridge housing is serviced from
it, so the kit applies (`scripts/roof_safety.py`), at the back: a **wall
ladder** centred on the rear wall (x = 0), 0.12 m outside the fascia, rising
1.0 m over the roof edge to 4.56 m (4.6 m long: no cage), and a **roof
ladder** straight above it up the rear slope to 0.30 m short of the housing's
back (z 5.04 m). The roof ladder reaches the housing, so there is no walkway.
`roof_safety.problems()` checks the wall ladder against the corners, the
rear window, the service door and the canopy. Tiers follow `RS.MODES`: every
rung, every other rung, every fourth without brackets, then no kit; the wall
ladder sets the rear plan bound, so LOD3 keeps its bare rails (16 triangles,
appended after the weld, `extents=True`).

## Per-tier triangle counts

Measured on the exported GLBs by `scripts/validate_asset.py`:

| Tier | Triangles | Ceiling | Status |
| --- | --- | --- | --- |
| `LOD0` | 1,568 | 12,000 | far under |
| `LOD1` | 1,228 | 4,000 | far under |
| `LOD2` | 442 | 1,500 | under |
| `LOD3` | 232 | 500 | under |

Where they go at LOD0: the roof kit and the two bent downpipes (about 600
together, mostly the ladders' rung holes and the pipes' bends), the body's
cells round eleven openings with their reveals and the lobby, the roof solid
with the five flashing caps cut into it, the housing and lid, the hood, the
sign band, the light box and arms, the canopy and the vent.

- `LOD0` → `LOD1` (−340): rungs halved, downpipes 4-sided.
- `LOD1` → `LOD2` (−786): flashings, sign band, housing lid, vent and one
  light-box arm go; windows and the service door paint flush; kit to every
  fourth rung without brackets; downpipes straight; coplanar boolean splits
  dissolved.
- `LOD2` → `LOD3` (−210): the lobby paints flush, the canopy and the kit go
  (the wall ladder's bare rails stay), downpipes 3-sided.

Between the catalog's sheds and shops (300–1,000) and its detached houses
(about 2,600): a small box, but with a pitched roof, its safety kit and
pipes, eleven openings and two signs, where the flat-roofed shops have no kit.

## LOD review

Authoring review with `scripts/review_asset.py`: perspective, **1920 x 1080**,
**50° vertical FOV**, distance along the view direction to the centre of the
visible front wall, noon sun, emission off; tiers 0–3 at **35, 70 and 120 m**,
front and oblique; and the oblique at 35 and 120 m by night with emission on.
Renders in `review/small_shops_2026_11_22/parturi_brick_pyramid/lod/` and
`night/` (not committed). Intended switches: the catalog's 35 / 70 / 120 m.

| Switch | Distance | Verdict |
| --- | --- | --- |
| `LOD0` → `LOD1` | 35 m | Indistinguishable: only rung count and pipe sides change. |
| `LOD1` → `LOD2` | 70 m | Holds. The flashings' highlight lines go, but the change of light between slopes still draws the hips; the band's letters are painted at the same place and colour; flush windows keep frames, transom bars, blinds and dark glass. The lobby stays a recess. |
| `LOD2` → `LOD3` | 120 m | Holds. The lobby goes flat with its screen painted on the wall; at 120 m it is a dark rectangle either way. The ladder's rails remain as two thin lines at the back. |

Kept on every tier: the pyramid roof and its eave line, the ridge housing and
the front vent hood (the roofline), the light box (it also sets the front
plan bound), the sign band's PARTURI, brick and plinth, window rhythm and
dark glass, the downpipes. A consumer switching by screen size may show
`LOD3` near: it still has every opening, both signs and the roof features.
At 35 m `LOD2` shows its flush windows as flat by their missing reveal
shadow; acceptable for a 70 m switch. One origin for all four tiers
(`asset_build.build_all()`).

**Pending:** runtime acceptance in a consumer scene (visible counts, hardware,
resolution, FOV, shadows, frame times). Triangle counts prove neither frame
time nor VRAM.

## Interior geometry

Welded manifold check, all four tiers: **0 boundary edges, 0 edges with more
than two faces, 0 loose vertices or edges**.

Sampled hidden-surface test (40 rays per face): `LOD0` 53/1,568 (3.4 %),
`LOD1` 44/1,228, `LOD2` 5/442, `LOD3` 8/232. Inspected by position: on
LOD0–LOD2 they are the **roof ladder's rails and rungs' undersides**, 80 mm
over the sheet (x ±0.22 m on the rear slope, z 4.6–4.9 m), and the light
box's arms in its 0.15 m gap; on LOD3 the **wall ladder's bare rails' backs**,
0.57 m off the rear wall, whose rays mostly hit the wall and the eave. All
exterior surface; nothing buried. The union of closed solids leaves one
volume's boundary, so there are no partitions or duplicate surfaces; the
body's lid and the roof's underside inside the wall line are removed by it.
The body's floor at z = 0 is kept as the closed shell's bottom.

## Known simplifications

- **Gutters are painted** on the fascia; downpipes and the kit are modelled.
- **Soldier courses, sheet sills, frames, transom bars, the door's stiles,
  handle and kick rail, blinds, the meter cupboard, the louvre and the
  housing's and hood's louvres are painted**, all under the relief threshold.
- The lobby has **no ceiling lamp, mat or step**; the entrance is at grade.
- The rear door has a **canopy but no wall lamp**.
- **Glass is opaque**; the salon is `glazing.py`'s room behind it.
- The light box's art is **one image on both faces**, each mapped to read
  left to right from its side.
- No snow guards modelled: they are painted in the roof band.

## Texture set

Seven unique PNGs, all **1024 x 1024, RGB, 8-bit, lossless**, no alpha:

| File | Colour space | Shared across |
| --- | --- | --- |
| `parturi_brick_pyramid_albedo_yellow_brick.png` | sRGB | all tiers |
| `parturi_brick_pyramid_albedo_red_brick.png` | sRGB | all tiers |
| `parturi_brick_pyramid_albedo_brown_brick.png` | sRGB | all tiers |
| `parturi_brick_pyramid_albedo_white_brick.png` | sRGB | all tiers |
| `parturi_brick_pyramid_orm.png` | Non-Color | all tiers, all variants |
| `parturi_brick_pyramid_normal.png` | Non-Color | all tiers, all variants |
| `parturi_brick_pyramid_emission.png` | sRGB | all tiers, all variants |

### Layout

Four bands run the full width and tile in U:

| Band | Rows | Covers |
| --- | --- | --- |
| brick | 0–220 | z 0–3.4375 m; dark plinth brick in the lowest five courses |
| roof | 226–456 | standing seam, V up the 4.80 m slope at 48 rows/m |
| fascia | 462–478 | the 0.25 m fascia, gutter across its top 9 rows (`PIPE_STRIP`) |
| soffit | 482–511 | stained boards, V out from the wall, vent gap at the wall |

Regions above them at 64 px/m: the lobby screen with its soldier lintel
(141 x 171 px), the front window, side window and small window (each with
sheet sill and soldier course), the service door, the meter cupboard, the
louvre, the housing's side (64 x 61), the sign band (614 x 44), and a row of
16 px patches; the light box face is 112 x 112 px at **160 px/m**.
`check_regions()` fails the bake on overlap, run-off or a band collision,
`check_bands()` on a stray id in a band.

### The brick

True size: a **285 x 85 mm module**, joints included (56 stretchers across
the 16 m band, a course 5.5 px), 12 mm recessed joints in their own mortar
colour, stretcher bond, each brick's tone hashed from its index so the band
wraps exactly; a few harder-fired darker bricks. Soldier courses are bricks
on end, 3.5 courses tall, a shade darker so they read as lintels.

### Lettering and pictogram

- Band: `PARTURI`, 22 px cap (0.34 m letters), 4.6 px stroke, cream, 20 mm
  proud in the height channel, with a soft shadow ring, centred at s = 6.7 m.
- Light box: `PARTURI`, 14 px cap at 160 px/m (88 mm letters), deep blue,
  and under it the comb-and-scissors mark drawn with canvas strokes, discs
  and rings (`pictogram()`): a tilted comb, teeth down, and open scissors
  crossing its end.

### Texel density

64 px/m on walls, openings and the sign band. Deviations: roof 64 along the
eave x 48 up the slope; light box 160 px/m; soffit 64 out from the wall but
the lobby soffit compressed 2x across its 0.9 m depth; housing and hood
fronts 64. Relief for the normal map: brick faces 6 mm, frames 25 mm, roof
seams 25 mm, gutter roll 60 mm, letters 20 mm, pressed sheet lines 4 mm,
soffit grooves 3 mm; glass and the light box face flat. Supersampled
`atlas.SS` = 4.

### Padding and filtering

Bands 4–6 rows apart, each painting 2 rows past its edge; regions keep a
≥ 4 px gutter; `atlas.pad()` fills the rest. Mip stress
(`scripts/review_atlas_mips.py`): mip 3 on LOD1–LOD3 (oblique and grazing,
75 and 125 m), mip 4 on LOD2/LOD3 (front and oblique, 75 and 125 m). Brick,
plinth, roof, fascia and glass keep their colours; no roof brown leaks into
the brick or the band; the gutter line holds. At mip 4 the band's letters
(about 1.4 texels tall) smear into a lighter strip, expected and accepted.
**Pending:** the consumer's sampler and shipped mipmaps.

### Weathering

`weather()` at the catalog's moderate level: soil, algae and splash on the
plinth and the brick above it, light efflorescence low on the masonry,
shelter dust under the eave, dirt in the joints (cavity), long runs and
eave dirt on the roof band, runs under the gutter on the fascia, dirt on the
sheet sills and frame feet, the screen's kick panels, the service door's
foot and handle, runs on the housing, dust on the meter cupboard's foot.
Glass, the light box and the letters stay clean.

## Glazing treatment

- Measured by `scripts/validate_asset.py`, all four variants: glass mean
  **sRGB 59**, linear **0.040**, **0.27–0.34x** the trim; darker than the
  brown frames round it.
- Roughness **0.08** (`glazing.ROUGHNESS`), metallic 0.
- Panes painted by `glazing.rooms()` on the finished albedo. The two front
  windows' big lights then get **vertical blinds** in the albedo (89 mm slats
  mixed 42 % toward a pale grey-beige, `blinds()`): part of the room, not a
  reflection, and absent from the emission. They lift the measured mean from
  the catalog's usual ~52 to 59, still inside the band.
- No sky gradient or reflection baked.

## Variant list

Four colours on the same geometry, UVs and tiers, albedo only:

| Variant | Meaning |
| --- | --- |
| `yellow_brick` | default; yellow-buff facing brick, grey mortar, brown roof |
| `red_brick` | red facing brick, a redder brown roof and trim |
| `brown_brick` | brown brick, the darkest roof and trim |
| `white_brick` | white sand-lime brick, light mortar, a warmer brown roof |

Low-rise / small-scale case: 3–6 variants. Roof, fascia, soffit, frames and
doors move a little with each brick; the plinth stays dark brown; the signs
(`FIXED`) do not change: they are the shop's identity.

## Night lighting

`parturi_brick_pyramid_emission.png`, one mask for every tier and colour.

- **Glazing, neutral, each pane a lit room** (`glazing.night_rooms()`): the
  lobby screen (leaf, sidelight, transom light), the front windows, the side
  window, both small windows, the meter cupboard's reading window.
- **Two luminous fixtures in their own colours**, which the validator
  reports as 12,672 coloured fixture pixels:
  - the light box: its opal face warm white (255, 228, 170), its letters and
    mark deep blue (52, 84, 200); its rim black;
  - the band's cut letters, cream (255, 214, 140); the brown field black.
- **Default off:** `emissiveFactor [0, 0, 0]` on all four tiers with the
  `emissiveTexture` binding intact.
- **Reference lit factor** linear **(1.0, 0.88, 0.72)**, a salon's
  fluorescent tubes (`LIT_FACTOR`).
- **Control granularity: one.** Glass, light box and letters share the
  material and its one emission factor; a separately switched sign would need
  a second material slot. No occupancy or schedule baked in.
- `variants.png`: all four colours at `LOD0`, a day row (emission off) over
  a night row at the reference factor (`scripts/variant_previews.py`: Cycles,
  fixed camera, exposure and colour management between rows). The light on
  the ground in the night row is Cycles bounce in the preview scene, not
  carried by the asset.
- Checked on reimported tiers by night, emission on, LOD0–LOD3 at 35 and
  120 m: the lit pattern is the same on every tier (the LOD3 lobby screen
  lights on the wall plane).
- **Pending:** consumer control of intensity and colour on reimport.

## Export

`.glb` + external PNGs through `scripts/asset_build.py`'s `export_all()`:
`export_yup=True`, selection only, modifiers applied, keep original textures,
no cameras or lights; each tier exported lit, its emission factor then
rewritten to zero and the placeholder image `bufferView`s stripped.

Traced in the GLB JSON (`LOD2` read in full; the validator confirms the same
bindings on every tier):

- `pbrMetallicRoughness.baseColorTexture` → `parturi_brick_pyramid_albedo_yellow_brick.png`;
- `metallicRoughnessTexture` → `parturi_brick_pyramid_orm.png`;
- `occlusionTexture` → `parturi_brick_pyramid_orm.png`;
- `normalTexture` → `parturi_brick_pyramid_normal.png`;
- `emissiveTexture` → `parturi_brick_pyramid_emission.png`, `emissiveFactor [0, 0, 0]`;
- no `texCoord` on any binding (`TEXCOORD_0` only); default factors and
  scales; one sampler (linear / linear-mipmap-linear); attributes `POSITION`,
  `NORMAL`, `TEXCOORD_0`; every image a `uri`, no `bufferView`.

Pivot on the ground at the centre of `LOD0`'s plan bounds, (0, -0.108) m from
the wall plan's centre in the build frame; every tier's bounds centred on it.
Front `-Y` in Blender, `+Z` in the export.

Facts sidecar `export/parturi_brick_pyramid.model.json`, version 1: the wall
rectangle as footprint (the lobby is a recess in the front wall and leaves
the outline straight), one storey of 78.02 m² (the rectangle less the lobby),
0 dwellings, hero false, two doors:

- `barber`: entrance, **main**, 0.95 x 2.10 m, threshold at x -3.465, y -4.0,
  z 0 in the build frame: on the **front wall plane**, at the leaf's centre,
  although the leaf itself stands 0.9 m back at the lobby's rear;
- `staff`: service, rear wall at x -2.0, 0.94 x 2.055 m.

Rebuild:

```bash
cd buildings/commercial/parturi_brick_pyramid
python3 facade_atlas.py export
blender --background source.blend --python build.py
blender --background --python build.py -- facts      # sidecar alone, from a committed tree
```

## Review status

Completed in this repository:

- `scripts/validate_asset.py`: every mechanical check passes; the only flag
  left is the sidecar's `source.dirty`, which clears when the sidecar is
  rewritten from a committed tree.
- Working views at every tier (`render_views()`: four orthographic
  elevations, plan, front and rear aerials, an eye-level street view and an
  entrance view with a 1.8 m figure), three passes:
  - pass 1: proportions, brick scale against the door, the lobby's depth and
    lintel, the leaf against the transom, sills, the signs' legibility, glass
    darker than frames, hips and eave, ladder, gutters and pipes, every
    elevation. The roof read as one plain field, the soldier courses were
    lost in the walling and the light box's mark was too small;
  - pass 2: added the louvred vent hood on the front slope and the soil
    vent, darkened the soldier courses, enlarged the mark and refitted the
    light box's lettering; LOD1–LOD3 views;
  - pass 3: preview, variants day/night, LOD distance pairs, night tiers and
    mip stress renders (LOD review, Texture set).
- GLB material bindings and image sources.
- Manifold and hidden-surface checks, all tiers; candidates explained.
- Glazing against the Style Direction band, all four variants.
- Palette: muted brick, brown steel and aluminium, stained boards; the only
  saturated colours are the light box's deep blue and the lit letters. No
  lighting baked into any albedo.
- A generic composite: no real building, shop name or mark.

Pending, outside this repository:

- Consumer import, LOD switching and runtime emission control.
- Consumer mipmap and anisotropic filtering.
- Performance in a representative scene.

## Tooling versions

- **Blender 5.3.0** (hash `02f0899d78e3`, built 2026-11-11), which built the
  tiers and saved `source.blend`; a 5.3 file needs Blender 5.3 or newer.
- **Blender MCP server addon: not used for this asset.** It was built
  headless (`blender --background ... --python build.py`), with the visual
  review done on rendered views (`render_views()`, `scripts/review_asset.py`).
- Textures baked with **CPython 3.14.10, numpy 2.5.5, scipy 1.18.1 and Pillow
  13.0.0**: `python3 facade_atlas.py export`.
