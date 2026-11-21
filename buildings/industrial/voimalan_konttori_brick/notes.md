# voimalan_konttori_brick

## Style brief

The office and control building of a small Nordic town's coal-fired heat and
power plant (*voimalan konttori*: the power plant's office), 1950s-60s. It
is one of the plant's separate buildings and holds its main entrance:
visitors and staff come in here, and the plant is run from the control room
on its ground floor. A generic composite of the type, not a portrait of any
one building.

- **Two storeys, 14 x 9 m**, long side to the front, red facing brick on a
  cast concrete plinth, in restrained post-war functionalism: a light cast
  band at the first floor right round the building, plain brick otherwise.
- **A low hipped roof** (17.4 degrees) of near-black bitumen felt on
  battens, a 0.5 m eave all round with a galvanised gutter painted on the
  fascia. Chosen over a gable and over a flat roof behind a parapet to set
  it apart from the mine office's gable and to read as the plant's
  administrative building rather than a shed.
- **The main entrance** on the front, one bay west of the middle: a pair of
  glazed teak leaves under a transom light in a cast concrete surround,
  under a thin canopy carried out from the first-floor slab, up three steps
  with a handrail.
- **The control room** fills the east half of the ground floor: three
  larger windows east of the entrance, one in the east end and two on the
  rear, wider and taller than the office windows and set a quarter metre
  lower, with a row of vent sashes along their heads. They are the
  building's tell from the yard.
- **The offices**: one regular row of five white-framed windows upstairs on
  each long side, one window to each storey on the ends, an office window at
  each ground-floor west bay.
- **The staff door** to the boiler house: a steel door on the rear, up
  three steps with a handrail.
- **Roof:** four downpipes, two plain vent pipes on the rear slope. No
  chimney (the building is heated from the plant), so no roof safety kit.

No signage, lettering or company marks anywhere on it.

## Category and secondary use

`buildings/industrial/`, as part of a heat and power plant. Secondary use:
**offices** (upper floor and the ground floor's west end) and the plant's
**control room** (ground floor, east half).

## Hero/landmark status

Not a hero. Ordinary triangle ceilings and the 1024 texture cap apply, and all
are met.

## Footprint

- **Walls: 14.0 x 9.0 m** (outer faces at x = +-7, y = +-4.5).
- **Roof: 15.0 x 10.0 m**: a 0.5 m eave on all four sides.
- **Canopy:** 2.6 m wide, 1.5 m off the front wall, at 3.5-3.75 m.
- **Steps:** front 2.6 m wide, 1.8 m out; rear 1.8 m wide, 1.6 m out.
- **Overall plan extent: 15.0 x 12.4 m**, the eaves by the front steps to
  the rear steps. Ridge at 8.53 m; overall height **8.66 m** to the top of
  the larger vent.

The pivot is the centre of that 15.0 x 12.4 m box at ground level, 0.1 m in
front of the walls' own centre line, because the front steps project 0.2 m
further than the rear ones.

## Story height

Two storeys. **Ground floor at 0.5 m** on the plinth, which shows 0.625 m
above the ground; **first floor at 3.75 m**: a **3.25 m** storey. The roof's
underside meets the walls at **6.875 m**: **3.125 m** from the first floor
to the eave. Both inside the 3.0-3.3 m band.

## Door leaf height

- **Entrance: a pair of 0.75 m leaves, 1.5 x 2.125 m clear**, in a
  1.625 x 2.6875 m opening; above the leaves a transom bar and a **0.5 m
  transom light** in two lights to the head, drawn in the atlas region. A
  0.1875 m cast surround runs round the jambs and 0.375 m over the head, up
  into the canopy.
- **Rear staff door: leaf 1.0 x 2.125 m**, plain steel with a small vision
  panel, in a 1.125 x 2.1875 m opening, the top 0.0625 m being the frame's
  head.
- Both thresholds are at the floor, 0.5 m; the landing in front of each is
  3 cm lower, at 0.469 m.

## Window sills

Heights above each storey's floor (ground floor at 0.5 m, first at 3.75 m):

- **Office windows, 1.5 x 1.6875 m:** sill **1.0 m**, head 2.6875 m, both
  storeys. Downstairs the head is level with the entrance's head (3.1875 m
  above the ground), 0.56 m over the door leaf's head.
- **Control-room windows, 2.0 x 1.9375 m:** sill **0.75 m**, head
  2.6875 m: the same head line, a quarter metre lower sill, so the room's
  desks and panels look out over the yard.
- Every ground-floor head is 0.31 m under the slab band; every upper sill
  1.0 m over it. The upper heads are 0.44 m under the eave.

## Eave overhang

**0.5 m on all four sides**, inside the 0.3-0.6 m default: a light soffit and
a dark sheet fascia carrying the painted half-round galvanised gutter, which
runs round the whole eave. The canopy is 3.0 m under the soffit.

## Construction

Closed solids unioned with Blender's exact boolean (`asset_build.union`):

1. **the shell**: four level-headed wall regions walked counter-clockwise,
   each opening built into its region as reveals round a closing plane (cut
   tiers) or a flat quad (flush tiers), the ring capped by a floor on the
   ground and a lid that is a hipped tent 0.125 m above the roof's
   underside, so it is a solid of the building's whole volume;
2. **the hipped roof**: one closed slab, the hipped underside, the same
   surface 0.25 m higher as the felt, and four vertical fascias; the walls
   run 0.125 m up into it;
3. **the canopy**: a 0.25 m concrete slab sunk 0.1 m into the front wall, at
   the height of the painted slab band;
4. **two flights of steps**, profiles extruded across the doors, their backs
   sunk 0.05 m into the wall below each threshold;
5. **two handrails** from `scripts/handrails.py`;
6. **four downpipes** from `scripts/downpipes.py`;
7. **two vent pipes**, each with its foot a slice of the roof plane inside
   the slab.

The union trims the walls into the roof and the rest into the shell and
leaves the boundary of one empty volume. A 0.1 mm weld follows; at `LOD2`
and `LOD3` a limited dissolve (0.001 rad, UV seams kept) recovers coplanar
boolean subdivisions.

Every number the mesh and the atlas share is in `facade_atlas.py`: the plan
(HX = 7, HY = 4.5), the floor, slab band, sill, leaf, entrance, canopy and
eave heights, TAN (0.3125, 17.4 degrees), ROOF_T (0.25), EAVE_OUT (0.5),
and every opening's size and reveal. `build.py` keeps the elevations'
opening lists on one grid of 2.625 m bays, the canopy, step, rail, vent and
downpipe positions, and `check_layout()`, which fails the build if:

- an opening (the entrance with its surround) comes within 0.4 m of a corner
  or 0.3 m of another opening, within 0.3 m of the wall head, or into the
  slab band;
- a leaf leaves 2.0-2.4 m, the entrance has no transom light, any sill
  leaves desk height, or either storey leaves 3.0-3.3 m;
- the canopy leaves the surround, is not wider than it, comes within 0.25 m
  of a window or does not cover the landing;
- the entrance steps are narrower than the surround, or a riser exceeds
  0.18 m;
- a handrail crowds its door or its foot post leaves its tread
  (`handrails.problems()`);
- a vent is on the ridge, the eave or a hip;
- a downpipe crowds a corner, an opening, the canopy or the steps
  (`downpipes.problems()`).

### The hipped roof

One pitch on every side and one overhang all round, so the underside's
height is set by the nearest wall line and the ridge runs 5.0 m along the
middle (x = -2.5 to 2.5). The walls are all level-headed at 7.0 m, inside
the slab; the shell's lid is the same hipped surface 0.125 m above the
underside, so it is buried in the slab everywhere and the union removes it.
No hip or ridge cap is modelled or painted (Known simplifications).

### The entrance

The entrance region in the atlas holds the cast surround and the doors
together. At `LOD0`/`LOD1` the surround is a U of concrete on the wall face
round the opening, the wall's hole is the surround's outline with the
opening's foot corners on it, and the reveals are concrete, the threshold
a grey sill. At `LOD2`/`LOD3` the whole surround is one quad. The canopy's
underside cuts the surround 6 cm below its top, so the two read as one
piece, and the canopy's edge lines up with the painted first-floor band, so
it reads as the slab carried out over the door.

### Steps and handrails

Three risers of 0.156 m to a landing 1.2 m (front) or 1.0 m (rear) deep,
two 0.3 m treads below it. Three risers, so a handrail on each flight, on
the right going up (`scripts/handrails.py`, `MODES` unchanged: `LOD0` and
`LOD1`). The steps set the plan's front and rear extents and stay on every
tier.

### Downpipes

Two to each long wall, 0.25 m in from the corners, where the hip's gutters
meet, standing 3 cm off the brick, leaving the soffit on a swan-neck and
ending in a shoe, all `scripts/downpipes.py`'s shape and `MODES` unchanged.
They sample the gutter's middle rows (`PIPE_STRIP`) and so are galvanised
in every variant; so are the handrails.

## Per-tier triangle counts

Measured on the exported GLBs by `scripts/validate_asset.py`:

| Tier | Triangles | Ceiling | Shell | Downpipes | Handrails | Vents |
| --- | --- | --- | --- | --- | --- | --- |
| `LOD0` | 1322 | 12,000 | 614 | 328 | 312 | 68 |
| `LOD1` | 1146 | 4,000 | 614 | 168 | 312 | 52 |
| `LOD2` | 428 | 1,500 | 316 | 76 | 0 | 36 |
| `LOD3` | 392 | 500 | 316 | 64 | 0 | 12 |

Shell = walls, 24 openings, roof, canopy and steps; the split was measured
by rebuilding each tier without the pipes, then without the rails, then
without the vents. The `LOD0` count is low for two storeys (the catalog's
two-storey terraces sit at 3,000-4,500) because the shell is one simple
box with a four-faced roof; nearly half of it is the pipes and rails,
whose cuts into the treads and the soffit cost more than the parts
themselves. `LOD2` flattens the openings and drops the rails; `LOD3`
differs from `LOD2` only in the pipes going three-sided and the small vent
going. `LOD3` is 392 against 500: the shell is already 24 flat quads in
four walls, a roof slab, the canopy and the steps.

## LOD review

- **Switches:** `LOD0` under 35 m, `LOD1` 35-70 m, `LOD2` 70-120 m, `LOD3`
  beyond; no overrides.
- **Camera:** `scripts/review_asset.py`, perspective, 50 degree vertical FOV,
  1920 x 1080, distance along the view direction to the front wall.
- **Pairs compared:** `LOD0`/`LOD1` at 30 and 40 m (front, oblique, noon);
  `LOD1`/`LOD2` at 65 and 75 m (front, oblique, noon and reversed sun);
  `LOD2`/`LOD3` at 115 and 125 m (front, oblique, aerial, noon).
- **Results:**
  - `LOD0`/`LOD1`: indistinguishable at 30-40 m; only the pipes' and vents'
    side counts change.
  - `LOD1`/`LOD2`: the flattened reveals lose their 0.15-0.2 m shadow line,
    about 2 px at 70 m, and the handrails go (a 4.5 cm rail is about two
    pixels there). The white frames, the slab band, the canopy and steps
    keep the window rhythm and the entrance in both lights.
  - `LOD2`/`LOD3`: at 120 m only the 0.16 m vent goes (about 1.5 px); the
    0.25 m one still breaks the roof line. Silhouette, hipped roofline and
    the band are unchanged.
- **The entrance at 40 m:** the light surround, canopy and steps are the
  only light vertical mark on the front and read as the way in from the
  front and the oblique, on every tier.
- **Geometry exceptions:** the downpipes and handrails, under the relief
  threshold, modelled per CLAUDE.md on the tiers their scripts give.

## Interior geometry

The shell is the boundary of one unioned volume, so there are no partitions
or duplicate surfaces. Hidden-surface test:

- **`LOD0`:** 11 of 1322 triangles flagged, 0.0 m2 vertical, at x = -1.37,
  y = -4.45, z 0.75-1.33: the back face of the front handrail's landing
  post and the level rail's end, 5 cm off the brick behind them. Exterior
  surface in a narrow gap the rays miss, not a buried face.
- **`LOD1`:** 7 of 1146, the same post.
- **`LOD2`:** 1 of 428, 0.0 m2, at (1.14, 2.71, 7.72): a sliver of the small
  vent's side on the line where it meets the felt.
- **`LOD3`:** 0.

Kept closure faces: none visible. The floor cap and the hipped lid are on
the ground and inside the roof slab, and the union removes them.

## Known simplifications

- Glazing bars, sashes, frames, the doors' glazing, kick plates and pull
  bars, the transom bars: textured.
- The gutter is painted on the fascia all round; there is no snow guard.
- No hip or ridge cap: the felt's battens meet at the hips, and the hips
  read by the change of shading between slopes.
- The first-floor slab band and the plinth's formwork joints are painted
  flush; the cast surround is flush, its arrises in the normal map.
- Windows and doors are flat at `LOD2`/`LOD3`.
- The vent pipes have no flashing collars at the felt.

## Texture set

- **1024 x 1024, 64 texels/m**, `atlas.SS` = 4 supersampling, lossless 8-bit
  RGB PNGs. The roof band runs 96 rows over 5.238 m of slope (18.3 rows/m),
  the only deviation: the battens run down the slope, so the felt varies
  only across U, and stretching V costs nothing visible, as on
  `tehdas_brick_gable`'s sheet.
- **Bands** (tile in U):
  - BRICK 0-448: cast plinth to 0.625 m with formwork joints, stretcher
    bond 0.25 x 0.078 m, the cast slab band at 3.5-3.75 m with tie holes
    every metre, brick to the wall head at 7.0 m. Every wall samples it by
    its height from the ground, and its U runs on round the corners.
  - ROOF 464-560: bitumen felt, battens every 0.5 m with lapped cap strips,
    a drip strip at the eave.
  - EAVE 568-584: dark fascia with the galvanised half-round gutter
    (`PIPE_STRIP` = rows 577-582).
  - CANOPY 592-608: the canopy's cast concrete edge with a drip groove.
- The roof and canopy bands start on 16-row boundaries, the roof 16 rows
  clear of the brick. Packed 6 rows apart, the first mip 4 render showed a
  red rim along every eave, the brick's top rows sharing a block with the
  felt's foot.
- **Regions** (from row 616): the entrance with its surround (128 x 196),
  the staff door, the office window, the control-room window, cast concrete
  for steps and canopy top, the vent pipe and its open end, and flat patches
  (row 1004).
- **Relief** for the normal map: brick 6 mm, slab band 4 mm proud of the
  brick, frames 30 mm, sashes 45 mm, felt battens 45 mm, gutter 70 mm
  half-round, cast surround 15 mm, door rails 40-50 mm. Glass flat.
- **Weathering** at the moderate level through `scripts/weathering.py`:
  plinth soil, splash-back and salt bloom on the height band, dirt on the
  slab band's top with faint runs under it, a sheltered band under the
  eave, roof runs and chalking, gutter dirt, sill dirt on the bottom rails,
  door feet and handles, worn concrete, sooty vent pipes.
- **Padding:** `atlas.pad()` last; `check_regions()` and `check_bands()`
  guard ownership.
- **Filtering:** mip 3 on `LOD1`/`LOD2` at 70 m and mip 4 on `LOD2`/`LOD3`
  at 120 m (`scripts/review_atlas_mips.py`), front, oblique and aerial. After
  the band realignment above, no roof or trim colour leaks and no dark
  seams; the gutter line, the slab band and the window frames survive.
- **Unique textures:** 3 albedo + ORM + normal + emission = 6 PNGs at
  1024 x 1024.

## Glazing treatment

`glazing.rooms()` on the finished albedo: measured by the validator at
**sRGB 55 (linear 0.034)** in every variant, 0.25-0.26x the surrounding
trim. ORM roughness `glazing.ROUGHNESS` (0.08), metallic 0. Inside the Style
Direction band; no departure.

## Variant list

Low-rise, so three brick variants on shared geometry and UVs. The names
match the plant's other brick buildings:

- **`red_brick`** (default): red brick, white frames, teak-brown entrance
  leaves, grey-green steel staff door.
- **`yellow_brick`**: buff brick, white frames, darker teak, a green-grey
  staff door.
- **`brown_brick`**: brown brick, off-white frames, mid-brown teak, a
  brown-grey staff door.

All three keep the near-black felt roof, the dark fascia, the galvanised
gutter, pipes and rails, and the grey concrete plinth, slab band, surround,
canopy and steps. ORM, normal and emission are shared.

## Night lighting

- **Mask:** `voimalan_konttori_brick_emission.png`, shared by every tier and
  colour: every window pane, the entrance leaves' glazing and the transom
  lights, and the staff door's vision panel, each painted neutral grey by
  `glazing.night_rooms()`. Frames, brick, concrete and the roof are black.
  No sign or lamp is luminous.
- **Reference lit factor: linear (1.0, 0.88, 0.72)**, fluorescent office and
  control-room light, as the catalog's other offices.
- **Default off:** `emissiveFactor [0, 0, 0]` in all four tiers, with the
  `emissiveTexture` binding intact.
- **Control:** one factor per placed building. Each window type shares one
  region, so no window, and not the control room alone, can be lit by
  itself.
- **`variants.png`:** the three colours at `LOD0`, a day row (emission off)
  above a night row at the reference factor, by `scripts/variant_previews.py`
  with camera, framing, exposure and colour management fixed. Light on the
  ground in the night row is the preview's bounce, **simulated**; spill is
  the consumer's.
- **Pending in the consumer:** off/on behaviour on reimported tiers, distant
  filtering under emission, LOD switches when lit.

## Export

`.glb` + external PNGs through `scripts/asset_build.py`:
`export_format='GLB'`, `use_selection=True`, `export_yup=True`,
`export_apply=True`, `export_keep_originals=True`, `export_cameras=False`,
`export_lights=False`. Emission is exported lit and the factor rewritten to
zero. `strip_embedded_images()` removes the placeholder `bufferView`s.

Checked by the validator on all four tiers:

- one mesh, one material slot;
- `baseColorTexture` → `voimalan_konttori_brick_albedo_red_brick.png`;
- `metallicRoughnessTexture` and `occlusionTexture` → `..._orm.png`;
- `normalTexture` → `..._normal.png`, scale 1, no tangents;
- `emissiveTexture` → `..._emission.png`, `emissiveFactor [0, 0, 0]`;
- every image a `uri`, no `bufferView`.

Pivot: ground level, centre of `LOD0`'s plan bounds, applied to every tier.
Front faces `-Y` in Blender, `+Z` in the exported glTF frame.

The facts sidecar `export/voimalan_konttori_brick.model.json` lists:

- **footprint:** the 14 x 9 m outer wall faces; the canopy, steps, rails,
  eaves and downpipes stand outside it;
- **storeys:** two, floors 0.5 m and 3.75 m, 126 m2 each (the upper one
  under a flat ceiling, 3.125 m to the eave);
- **dwellings:** 0;
- **doors:** `entrance` (main, kind entrance, front, the pair 1.5 m clear)
  and `staff` (kind service, rear).

Rebuild:

```bash
cd buildings/industrial/voimalan_konttori_brick
python3 facade_atlas.py export                          # every PNG in export/
blender --background source.blend --python build.py     # tiers, GLBs, preview, variants, sidecar
```

## Review status

Completed in this repository:

- `scripts/validate_asset.py`: 0 FAIL. One WARN: `source.dirty` on the
  sidecar, built from an uncommitted tree.
- `check_layout()`, `check_regions()` and `check_bands()` pass on every
  build.
- **Views inspected** at `LOD0`: the six pre-export views (orthographic
  front, rear, east, west and top, and a raised aerial off the front-east
  corner), plus a rear aerial and eye views at the entrance, at the staff
  door and along the front.
- LOD pairs at 30/40, 65/75 and 115/125 m (LOD review).
- Mip 3 and mip 4 stress renders (Texture set); the atlas bands were
  realigned once after the first mip 4 render.
- Day cycle (morning, noon, dusk, night with emission) at `LOD0`.
- Glazing measured against the band in all three colours.
- **Palette:** muted red, buff and brown brick; white frames; a near-black
  felt roof; grey concrete; galvanised steel. No saturated colour, and no
  baked light in any albedo.
- **Scale:** the door leaves are 2.125 m; the sills were checked against
  them and against both floors (Window sills).

Pending, outside this repository:

- Consumer import, LOD switching and runtime emission control.
- Consumer-side mipmap and anisotropic filtering.
- Performance in a representative scene.
- Placement beside the plant's other buildings, whose palettes this
  asset's variants are named to match.

## Tooling versions

- **Blender 5.3.0** (hash `02f0899d78e3`, built 2026-11-11), headless. This
  is a known-good diagnostic, not a pin. `source.blend` is saved by 5.3.0.
- **Blender MCP addon: not used.** Built and reviewed headless with
  `blender --background`, `build.py`'s `render_views()`,
  `scripts/review_asset.py`, `scripts/review_atlas_mips.py` and
  `scripts/validate_asset.py`.
- **CPython 3.14.10 with numpy 2.5.5, scipy 1.18.1 and Pillow 13.0.0** for
  the texture bake.
