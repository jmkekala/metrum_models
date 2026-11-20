# kaivoskonttori_brick

## Style brief

The staff building of a small mid-century Nordic mine (*kaivoskonttori*:
mine office): office at one end, changing rooms and wash room (the "dry") at
the other. Workers arrive here, and a consumer may use its main door as the
whole mine's entrance, so the entrance has to be unmistakable. A generic
composite of the type, not a portrait of any one building.

- **One storey, 16 x 8 m**, long side to the front, in red facing brick on a
  rendered plinth, under a low standing-seam gable in dark sheet metal with
  a galvanised gutter along each eave and a snow guard above it. Plain, tidy
  1950s institutional character.
- **The main entrance** is on the front, just east of the middle, toward the
  office end: a half-glazed door with a transom light in a light rendered
  surround, under a flat concrete canopy, up two concrete steps. It is the
  only light vertical mark on the front, with a metre of plain brick each
  side of it.
- **The office (east end)** has ordinary windows at desk height: three on
  each long wall and one in the gable.
- **The dry (west end)** has a row of small high windows: four on the front,
  three on the rear and one in the gable. The two window types tell the two
  uses apart from any side.
- **The rear** has the steel door the shift comes in by, straight into the
  dry, up two steps of its own.
- **Roof:** four downpipes from the painted gutters, two to each eave near
  the corners; three plain vent pipes over the wash room on the rear slope.
  No chimney, so no roof safety kit.

No signage, lettering or company marks anywhere on it.

## Category and secondary use

`buildings/industrial/`, as part of a mine's surface plant. Secondary use:
**offices** (east end) and **staff welfare** (changing rooms and wash room,
west end).

## Hero/landmark status

Not a hero. Ordinary triangle ceilings and the 1024 texture cap apply, and all
are met.

## Footprint

- **Walls: 16.0 x 8.0 m** (outer faces at x = +-8, y = +-4).
- **Roof: 16.6 x 8.9 m**: 0.30 m rakes, 0.45 m eaves.
- **Canopy:** 2.4 m wide, 1.2 m off the front wall.
- **Steps:** front 2.0 m wide, 1.3 m out; rear 1.6 m wide, 1.2 m out.
- **Overall plan extent: 16.6 x 10.5 m**, the rakes by the front steps to
  the rear steps. Ridge at 5.50 m; overall height **5.69 m** to the top of
  the wash room's exhaust.

The pivot is the centre of that 16.6 x 10.5 m box at ground level, 0.05 m in
front of the walls' own centre line, because the front steps project 0.1 m
further than the rear ones.

## Story height

One storey. **Floor at 0.3125 m** on the rendered plinth, which shows
0.375 m above the ground. The roof's underside meets the long walls at
**3.5 m**: **3.1875 m floor to eave**, within the 3.0-3.3 m band.

## Door leaf height

- **Entrance: leaf 1.0 x 2.125 m**, in a 1.125 x 2.4375 m opening; above
  the leaf a transom bar and a **0.19 m transom light** to the head, drawn in
  the atlas region. A 0.1875 m rendered surround runs round the jambs and
  0.25 m over the head, its top under the canopy.
- **Rear service door: leaf 1.0 x 2.125 m**, plain steel in a 1.125 x
  2.1875 m opening, the top 0.0625 m being the frame's head.
- Both thresholds are at the floor, 0.3125 m; the landing in front of each is
  3 cm lower, at 0.28125 m.

## Window sills

Heights above the floor (add 0.3125 m for above the ground):

- **Office windows, 1.375 x 1.3125 m:** sill **0.875 m**, head 2.1875 m,
  just over the leaf head (2.125 m) and under the entrance opening's head
  (2.4375 m).
- **High windows of the dry, 1.25 x 0.625 m:** sill **1.6875 m**, head
  2.3125 m: above head height for the changing rooms and the wash room, as
  intended, and level with the entrance's transom.

## Eave overhang

**0.45 m at the eaves**, 0.30 m at the rakes, inside the 0.3-0.6 m default.
A light soffit, a dark sheet fascia in the roof's colour carrying the painted
half-round galvanised gutter, and barge flashing over the gables. The canopy
top is 0.18 m below the eave soffit's outer edge.

## Construction

Closed solids unioned with Blender's exact boolean (`asset_build.union`):

1. **the shell**: four wall regions walked counter-clockwise, each opening
   built into its region as reveals round a closing plane (cut tiers) or a
   flat quad (flush tiers), and the ring capped by a floor on the ground and
   a lid split at the two gable apexes, so it is a solid of the building's
   whole volume;
2. **the gable roof**: one chevron-section slab extruded along the ridge, so
   deck, fascias, soffits and barge ends are one closed surface; the walls
   run 0.125 m up into it;
3. **the canopy**: a 0.1875 m concrete slab sunk 0.1 m into the front wall;
4. **two flights of steps**, profiles extruded across the doors, their backs
   sunk 0.05 m into the wall below each threshold;
5. **four downpipes** from `scripts/downpipes.py`;
6. **three vent pipes**, each with its foot a slice of the roof plane inside
   the slab.

The union trims the walls into the roof and the rest into the shell and
leaves the boundary of one empty volume. A 0.1 mm weld follows; at `LOD2`
and `LOD3` a limited dissolve (0.001 rad, UV seams kept) recovers coplanar
boolean subdivisions.

Every number the mesh and the atlas share is in `facade_atlas.py`: the plan
(HX = 8, HY = 4), the floor, sill, leaf, entrance, canopy and eave heights,
TAN (0.4375, 23.6 degrees), ROOF_T (0.25), EAVE_OUT, RAKE_OUT, and every
opening's size and reveal. `build.py` keeps the elevations' opening lists,
the canopy, step, vent and downpipe positions, and `check_layout()`, which
fails the build if:

- an opening (the entrance with its surround) comes within 0.4 m of a corner
  or 0.3 m of another opening, or within 0.3 m of the wall head;
- a leaf leaves 2.0-2.4 m, the entrance has no transom light, the office
  sills leave desk height or the high sills drop below 1.6 m;
- the canopy leaves the surround, comes within 0.15 m of the eave soffit, is
  not wider than the surround, or runs over a window;
- the entrance steps are narrower than the surround, or a riser exceeds
  0.18 m;
- a vent is on the ridge, the eave or a gable, or not over the wash room;
- a downpipe crowds a corner, an opening, the canopy or the steps
  (`downpipes.problems()`).

### The entrance

The entrance region in the atlas holds the rendered surround and the door
together. At `LOD0`/`LOD1` the surround is a U of render on the wall face
round the opening, the wall's hole is the surround's outline with the
opening's foot corners on it, and the reveals are render, the threshold a
concrete sill. At `LOD2`/`LOD3` the whole surround is one quad. The canopy's
underside cuts the surround 6 cm below its top, so the two read as one
piece.

### Steps

Two risers of 0.14 m to a landing 1.0 m (front) or 0.9 m (rear) deep, a
step 0.3 m deep below it. Two risers, so no handrail (CLAUDE.md asks for one
from three). The steps set the plan's front and rear extents and stay on
every tier.

### Downpipes

Two to each eave, 0.3 m in from the corners, standing 3 cm off the brick,
leaving the soffit on a swan-neck and ending in a shoe, all
`scripts/downpipes.py`'s shape and `MODES` unchanged. They sample the
gutter's middle rows (`PIPE_STRIP`) and so are galvanised in every variant.

## Per-tier triangle counts

Measured on the exported GLBs by `scripts/validate_asset.py`:

| Tier | Triangles | Ceiling | Shell | Downpipes | Vents |
| --- | --- | --- | --- | --- | --- |
| `LOD0` | 896 | 12,000 | 468 | 324 | 104 |
| `LOD1` | 712 | 4,000 | 468 | 164 | 80 |
| `LOD2` | 376 | 1,500 | 256 | 64 | 56 |
| `LOD3` | 324 | 500 | 256 | 52 | 16 |

Shell = walls, openings, roof, canopy and steps; the split was measured by
rebuilding each tier without the pipes and then without the vents. The
`LOD0` count is in line with the catalog's single-storey buildings (about
1,000). Over a third of it is the four bent eight-sided downpipes. `LOD0` to
`LOD1` changes only the pipes and vents; `LOD2` flattens the openings, which
is most of the shell's saving. `LOD3` differs from `LOD2` only in pipes and
vents: the shell is already 22 flat quads in four walls, a roof slab, the
canopy and the steps, and nothing in it can go without changing the
silhouette or the window rhythm.

## LOD review

- **Switches:** `LOD0` under 35 m, `LOD1` 35-70 m, `LOD2` 70-120 m, `LOD3`
  beyond; no overrides.
- **Camera:** `scripts/review_asset.py`, perspective, 50 degree vertical FOV,
  1920 x 1080, distance along the view direction to the front wall.
- **Pairs compared:** `LOD0`/`LOD1` at 30 and 40 m (front, oblique, noon);
  `LOD1`/`LOD2` at 65 and 75 m (front, oblique, noon and reversed sun);
  `LOD2`/`LOD3` at 115 and 125 m (front, oblique, aerial, noon).
- **Results:**
  - `LOD0`/`LOD1`: indistinguishable at 30-40 m.
  - `LOD1`/`LOD2`: the flattened reveals lose their 0.15-0.2 m shadow line,
    about 2 px at 70 m. The frames and glass keep the rhythm, and the canopy
    and steps keep the entrance.
  - The two 0.16 m vents first went at `LOD2`, and at 65 m they visibly
    vanished from over the ridge. They now stay four-sided through `LOD2`.
  - `LOD2`/`LOD3`: at 120 m only the two small vents go (about 1.5 px wide).
    The 0.25 m exhaust (2.4 px) stays, so the ridge line still breaks.
- **The entrance at 40 m:** the light surround, canopy and steps are the only
  light marks on the front's ground storey and read as the way in from the
  front and the oblique, on every tier.
- **Geometry exceptions:** the downpipes, under the relief threshold,
  modelled per CLAUDE.md on every tier.

## Interior geometry

The shell is the boundary of one unioned volume, so there are no partitions
or duplicate surfaces. Hidden-surface test:

- **`LOD1`-`LOD3`:** 0 triangles flagged.
- **`LOD0`:** 1 of 896 triangles flagged, 0.0 m2, at (-1.35, -3.95, 3.5):
  a zero-area triangle on the line where the eave soffit meets the front
  wall's face. It comes from triangulating an n-gon with collinear corners
  along that line, not from a buried face. `dissolve_degenerate` after the
  weld left it in place, and the welded-manifold check passes, so it is
  kept.

Kept closure faces: none visible. The floor cap and the lid are inside the
roof slab and on the ground, and the union removes them.

## Known simplifications

- Glazing bars, sashes, frames, the door's panel, kick plate and handle, the
  transom bar: textured.
- The gutters are painted on the fascia, and the snow guards on the roof
  band about 0.5-0.75 m up the slope from the eave edge: two round rails on a
  bracket every metre.
- The rendered surround is flush, its arrises painted in the normal map.
- No eaves on the gables other than the 0.3 m rake.
- Windows and doors are flat at `LOD2`/`LOD3`.
- The vent pipes have no flashing collars at the sheet.

## Texture set

- **1024 x 1024, 64 texels/m**, `atlas.SS` = 4 supersampling, lossless 8-bit
  RGB PNGs. The roof band runs 310 rows over 4.857 m of slope (63.8 rows/m),
  the only deviation.
- **Bands** (tile in U):
  - BRICK 0-232: rendered plinth to 0.375 m, then stretcher bond 0.25 x
    0.078 m to the wall head at 3.625 m. The gable triangles sample it
    1.875 m (24 courses, one tone period) lower.
  - ROOF 238-548: standing seams every 0.5 m, the snow guard, a ridge cap.
  - EAVE 554-570: dark fascia with the galvanised half-round gutter
    (`PIPE_STRIP` = rows 563-568).
  - CANOPY 576-588: the canopy's cast concrete edge with a drip groove.
- **Regions** (from row 596): the entrance with its surround (96 x 172), the
  service door, the office window, the high window, cast concrete for steps
  and canopy top, the vent pipe and its open end, and flat patches (row
  1004).
- **Relief** for the normal map: brick 6 mm, frames 30 mm, sashes 45 mm,
  seams 25 mm, gutter 70 mm half-round, snow-guard rails 35 mm, render
  surround 12 mm, door panel 46 mm. Glass flat.
- **Weathering** at the moderate level through `scripts/weathering.py`:
  plinth soil, splash-back and salt bloom on the height band, roof runs and
  chalking, gutter dirt, sill dirt on the bottom rails, door feet and
  handles, worn concrete, sooty vent pipes.
- **Padding:** `atlas.pad()` last; `check_regions()` and `check_bands()`
  guard ownership.
- **Filtering:** mip 3 on `LOD1`/`LOD2` at 70 m and mip 4 on `LOD2`/`LOD3`
  at 120 m (`scripts/review_atlas_mips.py`), front, oblique and aerial. No
  roof or trim colour leaks, no dark seams. The gutter line and the window
  frames survive.
- **Unique textures:** 3 albedo + ORM + normal + emission = 6 PNGs at
  1024 x 1024.

## Glazing treatment

`glazing.rooms()` on the finished albedo: measured by the validator at
**sRGB 54 (linear 0.032)** in every variant, 0.25-0.28x the surrounding
trim. ORM roughness `glazing.ROUGHNESS` (0.08), metallic 0. Inside the Style
Direction band; no departure.

## Variant list

Low-rise, so three brick variants on shared geometry and UVs. The names
match the mine's hoist house:

- **`red_brick`** (default): red brick, off-white frames, a dark teak-brown
  entrance door, grey-green steel service door.
- **`yellow_brick`**: buff brick, dark green-grey frames, a dark green
  entrance door.
- **`brown_brick`**: brown brick, off-white frames, a mid-brown entrance
  door.

All three keep the dark grey roof and fascia, the galvanised gutter and
pipes, the grey rendered plinth and the light render surround and concrete.
ORM, normal and emission are shared.

## Night lighting

- **Mask:** `kaivoskonttori_brick_emission.png`, shared by every tier and
  colour: every window pane, the entrance door's glazed panel and its
  transom light, each painted neutral grey by `glazing.night_rooms()`.
  Frames, brick, the steel service door and the roof are black. No sign or
  lamp is luminous.
- **Reference lit factor: linear (1.0, 0.88, 0.72)**, fluorescent office and
  changing-room light, as `tehdas_brick_gable`.
- **Default off:** `emissiveFactor [0, 0, 0]` in all four tiers, with the
  `emissiveTexture` binding intact.
- **Control:** one factor per placed building. Each window type shares one
  region, so no window can be lit alone.
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

Traced in the GLB JSON of all four tiers:

- one mesh, one primitive, one material;
- `baseColorTexture` → `kaivoskonttori_brick_albedo_red_brick.png`;
- `metallicRoughnessTexture` and `occlusionTexture` → `..._orm.png`,
  factors 1;
- `normalTexture` → `..._normal.png`, scale 1, no tangents;
- `emissiveTexture` → `..._emission.png`, `emissiveFactor [0, 0, 0]`;
- `OPAQUE`, single-sided;
- every image a `uri`, no `bufferView`;
- attributes POSITION, NORMAL, TEXCOORD_0.

Pivot: ground level, centre of `LOD0`'s plan bounds, applied to every tier.
Front faces `-Y` in Blender, `+Z` in the exported glTF frame.

The facts sidecar `export/kaivoskonttori_brick.model.json` lists:

- **footprint:** the 16 x 8 m outer wall faces; the canopy, steps, eaves and
  downpipes stand outside it;
- **storeys:** one, floor 0.3125 m, 128 m2;
- **dwellings:** 0;
- **doors:** `entrance` (main, kind entrance, front) and `shift` (kind
  service, rear).

Rebuild:

```bash
cd buildings/industrial/kaivoskonttori_brick
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
  corner), plus a rear aerial and eye views at the entrance, at the service
  door and along the front.
- LOD pairs at 30/40, 65/75 and 115/125 m (LOD review). The vents' tiers
  were reworked once after the comparison.
- Mip 3 and mip 4 stress renders (Texture set).
- Glazing measured against the band in all three colours.
- GLB bindings traced on all four tiers (Export).
- **Palette:** muted red, buff and brown brick; off-white or dark frames;
  a dark grey roof; grey render; light concrete; galvanised steel. No
  saturated colour, and no baked light in any albedo.
- **Scale:** the door leaf is 2.125 m; the sills were checked against it and
  against the floor (Window sills).

Pending, outside this repository:

- Consumer import, LOD switching and runtime emission control.
- Consumer-side mipmap and anisotropic filtering.
- Performance in a representative scene.

## Tooling versions

- **Blender 5.3.0** (hash `02f0899d78e3`, built 2026-11-11), headless. This
  is a known-good diagnostic, not a pin. `source.blend` is saved by 5.3.0.
- **Blender MCP addon: not used.** Built and reviewed headless with
  `blender --background`, `build.py`'s `render_views()`,
  `scripts/review_asset.py`, `scripts/review_atlas_mips.py` and
  `scripts/validate_asset.py`.
- **CPython 3.14.10 with numpy 2.5.5, scipy 1.18.1 and Pillow 13.0.0** for
  the texture bake.
