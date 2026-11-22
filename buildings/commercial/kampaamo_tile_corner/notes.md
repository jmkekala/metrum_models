# kampaamo_tile_corner

## Style brief

A late-1980s Finnish postmodern corner shop let to a hair salon (kampaamo):
one tall storey clad in small glazed ceramic tile, a flat roof hidden behind
a parapet with a thin painted coping, and a quarter-round corner as its
signature. Generic and composite: no real building, business, brand or
chain look.

- Tile is a true 125 mm grid: a dark tile plinth, a muted accent tile
  (teal by default) over the whole shopfront storey, and a white tile sign
  band above it with one accent course near its top. The band runs on
  unbroken round the curve.
- At the curve the shopfront stands 0.6 m back from the band under a tiled
  soffit. It is glazed in facets between slim white mullions on a smaller
  arc, over a dark tile kick. One slim round white column stands free under
  the middle of the band. A small projecting light box (scissors over a
  comb) stands out of the band above the column.
- On the straight front are two display windows under striped fabric
  awnings, with vertical blinds and pot plants behind the glass. The word
  KAMPAAMO is set in dark red block capitals on the band over them. The one
  shop door is beside the corner, at grade, under a thin steel canopy hung
  on two rods.
- On the sides and back: two windows on the left side; on the right side a
  window, the meter cupboard and an exhaust louvre; at the back a small
  window, the staff door under a small steel canopy, and the wall ladder to
  the roof. On the deck are a roof extract fan and two vent pipes.

## Category and secondary use

`buildings/commercial/`. Single use: a hair salon. No secondary use.

## Hero/landmark status

Not hero. Ordinary ceilings and the 1024 atlas.

## Footprint

- Wall plan: 10.0 x 9.0 m. Its front-right corner (+X, -Y) is a quarter
  circle of radius 2.5 m about (2.5, -2.0).
- At ground level the curved shopfront follows a 1.9 m arc. The ground-level
  wall outline is therefore the plan with a 0.6 m deep quarter-annulus
  recess and a return at each end. Its LOD0 polygon (8 facets) encloses
  86.57 m²; this is the sidecar's footprint and storey area.
- LOD0 plan bounds: 10.125 x 10.40 m.
  - X ±5.0625: the coping's 0.0625 m oversail.
  - Front: y -5.40 at the shop door's canopy (0.9 m out); the awnings reach
    0.85 m.
  - Back: y +5.00 at the staff door's canopy (0.5 m out); the wall ladder's
    rails reach about +4.74.
- Height 5.125 m to the ladder's top. The parapet's coping is at 4.125 m and
  the vent pipes at 4.45 m.
- Pivot: ground, centre of the LOD0 plan bounds. That is build (0, -0.20, 0)
  and is shared by all tiers.

## Story height

One storey from the pavement (floor 0.0) to the roof deck at 3.5 m. That is
above the 3.0–3.3 m default, for the tall retail storey these shops have.
The shopfront head is at 2.75 m and the tile band carries on to the coping
at 4.125 m. The parapet stands 0.625 m over the deck.

## Door leaf height

- **Shop door** (id `salon`, main entrance):
  - One glazed leaf, 0.94 x 2.10 m, in white aluminium, at grade. No steps
    and no handrail.
  - A 0.06 m transom bar at 2.10–2.16 m, then a transom light to the head
    frame at 2.71 m. The opening is 1.0 x 2.75 m.
  - The transom bar continues across the display windows and the curved
    shopfront at the same height.
- **Staff door** (id `staff`, service): leaf 0.90 x 2.10 m in a 1.0 x 2.15 m
  steel frame. No transom.
- Checked against the 1.8 m figure in the eye-level views.

## Window sills

| Opening | Sill (m) | Head (m) | Notes |
| --- | --- | --- | --- |
| Display windows | 0.375 | 2.75 | Sill on the plinth line. Glass from about 0.42 m (the sill rail) to the head; transom at 2.10 |
| Curved shopfront | 0.375 | 2.75 | Dark tile kick below the sill, as the plinth |
| Side windows (2 west, 1 east) | 0.875 | 2.25 | 1.25 x 1.375 m |
| Back window | 1.50 | 2.125 | 0.625 m square |

All heads are at or under the door's 2.75 m head line, and no sill reads as
chest-high against the 2.1 m leaf.

## Eave overhang

None: a parapet with internal drainage.

- The coping oversails each face of the parapet by 0.0625 m.
- There is no gutter, so there are no downpipes. Rainwater goes to roof
  drains inside the parapet; these are not modelled.
- The roof safety kit takes its colour from the coping band's strip
  (`PIPE_STRIP`), not from a gutter.

## Construction

Closed solids are unioned with `asset_build.union(..., snap=asset_build.SNAP)`,
then welded at 0.1 mm and normals recalculated. LOD2 and LOD3 then run a
coplanar `dissolve_limit` (UV seams kept). The wall ladder is appended after
that.

### Shell

One solid built face by face in `main_body()`:

- the four straight walls, holed for windows and panels and notched for the
  doors;
- every cut opening's reveals and closing face;
- the curved corner:
  - the band on the outer arc from 2.75 m up;
  - its soffit back to the inner arc;
  - the faceted shopfront on the inner arc down to the ground;
  - a tiled return at each end of the recess;
- the parapet's top and inner face, and the deck;
- a floor cap triangulated in plan, because the recess makes it concave.

### Other solids

- the coping ring;
- the column: a prism from the pavement up into the band, 0.11 m radius, at
  2.25 m from the arc centre, under the soffit's middle;
- the light box: a slab 0.625 m out x 0.8125 m tall x 0.12 m thick, standing
  radially at the curve's middle, z 2.95 m;
- two awnings: closed wedges from the wall at about 2.82–2.97 m to a
  0.85 m projection, with a 0.2 m valance down to 2.25 m;
- the shop door canopy: 1.4 x 0.9 x 0.10 m at 2.85–2.95 m;
- its two 3 cm tie rods up to 3.55 m;
- the staff door canopy: 1.2 x 0.5 x 0.08 m at 2.40–2.48 m;
- the roof fan: a 0.28 m drum under a 0.36 m hood, to 0.76 m over the deck;
- two vent pipes, 0.95 and 0.80 m over the deck.

### The curve

- Facets per tier: 8 / 6 / 4 / 2, the same for the band, the soffit, the
  shopfront, the parapet and the coping. Every count puts a vertex at the
  curve's middle, where the column and the light box stand.
- Band UVs unroll along the true arc length: U is the running length round
  the building at 64 px/m. Tile courses and the accent course therefore run
  continuously from the front, round the curve and on down the east side.
- The shopfront's region also unrolls along its own arc (2.985 m). Its four
  panes and five mullions sit at 22.5° pitch, so they land on every other
  LOD0 facet edge.

### Roof safety

- A wall ladder on the back wall, s = 2.0 m from its east end (x = 3.0),
  clear of the back window, the staff door, its canopy and the corners.
- It is `scripts/roof_safety.py`'s lean kit, `Eave(rear wall, z_wall=4.03125,
  eave_out=0.0625, z_edge=4.125, tan=0)`.
- It rises 1 m over the coping, at 5.125 m. It is 5.125 m long, so it has no
  cage.
- It serves the roof fan on the flat deck. `roof_safety.problems()` runs in
  `check_layout()`, and `append(check=True)` verifies that the kit touches
  nothing.

### Authored parameters

Everything is in `facade_atlas.py`:

- the plan (`HX`, `HY`, `R_OUT`, `RECESS`, `PARAPET_T`, `COPING_OUT`);
- heights on whole tile courses (`Z_PLINTH`, `Z_HEAD`, `Z_STRIPE`, sign
  rows);
- the front layout (`DISPLAYS`, `DOOR_SPAN`, `SIGN_SPAN`);
- the fittings (`AWN_PROFILE`, `CANOPY`, `REAR_CANOPY`, `LIGHTBOX`,
  `COLUMN_*`);
- the other openings.

`build.py` adds the per-wall item lists, the roof plant and the ladder's
place. `check_layout()` checks:

- openings clear of corners and of each other;
- door leaves within 2.0–2.4 m, with room for a transom;
- awnings between the shopfront head and the lettering, and clear of the
  canopy;
- the staff canopy over its door and clear of the back window and the
  ladder;
- the column under the soffit and the light box buried in the parapet's
  solid;
- even facet counts;
- the parapet at least 0.5 m over the deck;
- the roof plant clear of the parapet;
- the ladder's place.

## Per-tier triangle counts

| Tier | Triangles | Ceiling |
| --- | --- | --- |
| `LOD0` | 1,038 | 12,000 |
| `LOD1` | 836 | 4,000 |
| `LOD2` | 472 | 1,500 |
| `LOD3` | 248 | 500 |

- **LOD0** carries everything:
  - 8 curve facets;
  - openings cut (shopfront and door 0.15 m, side and back windows 0.12 m,
    staff door 0.10 m);
  - column 16 sides, fan 12, vents 8;
  - the canopy rods;
  - the ladder with every rung and bracket.
- **LOD1**: 6 facets, column 10 sides, fan 8, vents 6, ladder every other
  rung.
- **LOD2**:
  - openings flat on the wall plane with the same regions;
  - 4 facets, column 6 sides, fan 6 sides;
  - vents and canopy rods dropped;
  - ladder every fourth rung, no brackets.
- **LOD3**:
  - 2 facets;
  - the coping is not modelled: the parapet runs to 4.125 m with the coping
    painted on its face and top;
  - column, light box and fan dropped;
  - the ladder's bare rails kept, because they set the extents;
  - awnings and both canopies kept: they set the front and back plan bounds
    and carry the front's identity.

This is a small one-storey shop, in line with the catalog's sheds and shops
(300–1,000 at `LOD0`). The parapet, curve and recess are cheap; most of the
LOD0 count is the ladder, the round column and the roof plant.

## LOD review

### Method

- Review camera: perspective, 1920x1080, 50° vertical FOV
  (`scripts/review_asset.py`, Cycles 24 samples).
- Pairs at the switches:
  - `LOD0`/`LOD1` at 30 and 40 m, front and oblique, noon and reverse sun;
  - `LOD1`/`LOD2` at 65 and 75 m, front, oblique and aerial, noon;
  - `LOD0`/`LOD2`/`LOD3` at 115 and 125 m, front, oblique and aerial, noon.
- Night, emission on: all four tiers at 40 m oblique.
- Intended switches are the catalog defaults: 35 / 70 / 120 m. No override.

### Findings

- **35 m:** `LOD0` and `LOD1` cannot be told apart. 6 facets against 8 does
  not show on the curve, and the thinned ladder is behind the building.
- **70 m:** flattening the openings at `LOD2` keeps their position,
  proportion, frames and glass. The 0.15 m reveal shadow goes, as the
  contract's default allows. The 4-facet curve still reads round.
- **120 m:**
  - `LOD3`'s 2-facet curve reads as a chamfered corner against `LOD2`'s
    rounded one. This is the one visible profile change. It comes from the
    facet count the brief set, and at that distance the building is about
    40 px across.
  - The light box and column go: the column is 0.22 m, under 2 px.
  - The parapet, lettering, awnings, canopy, recess and colour bands all
    hold.

## Interior geometry

The validator's sampled hidden-surface test passes on every tier:

| Tier | Hidden triangles | Share | Vertical area |
| --- | --- | --- | --- |
| `LOD0` | 71 / 1,038 | 6.8 % | 0.0 m² |
| `LOD1` | 43 / 836 | 5.1 % | 0.0 m² |
| `LOD2` | 28 / 472 | 5.9 % | 0.0 m² |
| `LOD3` | 8 / 248 | 3.2 % | 0.9 m² |

- On `LOD0`–`LOD2` the candidates are horizontal. They are the coping's
  0.0625 m drip underside at z 4.03 along its inner edge, over the felt
  upturn. It is a real exterior surface, visible only from the roof deck,
  and is kept.
- The `LOD3` candidates at (3.2, 4.9, 1.7–3.4) are the inner faces of the
  ladder's two bare rails, which face each other across the ladder. They
  are kept because the rails set the extents.
- There are no buried partitions. The parapet's top inside the coping, the
  wall band above the coping's drip, and the buried backs of the column,
  awnings, canopies, rods, light box and roof plant are removed by the
  union. The floor cap faces the ground and is kept as the shell's closure.

## Known simplifications

- **Letters:** the lettering is painted in the band's own region, with
  0.04 m of relief in the height channel. It is not individual letter
  geometry.
- **Kept flat in the texture:**
  - the tile joints;
  - the shopfront mullions and transoms;
  - the door's stiles and pull;
  - the meter cupboard and the louvre (flush panels on every tier);
  - the coping's joints.
- **Awnings:** closed wedges, without arms, rollers or an open underside.
- **Behind the glass:** the vertical blinds and the plants are painted in
  the display and curve regions. Both display windows show the same room.
- **Not modelled:**
  - roof drains, a scupper or overflow;
  - door hardware beyond the painted pull;
  - signage beyond the band's lettering and the light box;
  - lamps over either door.

## Texture set

- **Size and density:** one 1024 atlas at 64 texels/metre on every wall,
  opening, fitting, awning and coping, with these local deviations:
  - the light box face at 96 px/m (0.625 x 0.8125 m on 60 x 78 px);
  - the roof deck at 16 px/m (seen from the air only).
- **Rasterising:** `scripts/atlas.py`, supersampled at `atlas.SS` = 4,
  box-filtered in linear light. `atlas.pad()` runs last, with a 6 px gutter
  at every region and band.
- **Unique textures:** seven 1024 PNGs — four albedos, one shared ORM, one
  normal map and one emission map. ORM, normal and emission are shared by
  every variant.

### Layout

Tiling bands, U wrapping:

- **Wall band**, rows 6–270, z 0–4.125 m:
  - dark tile plinth to 0.375;
  - accent tile to 2.75, with a sealant hairline at the head;
  - white tile to 3.75;
  - one accent course 3.75–3.875;
  - white tile to the coping's drip at 4.03;
  - coping face above that (seen only on `LOD3`).
- **Coping band**, rows 282–316: a 6 px face, then a 28 px top with folded
  joints every 2 m. `PIPE_STRIP` is rows 294–310.
- **Felt upturn band**, rows 328–368.

Regions:

- the curved shopfront (191 x 176), the shop door, a display window and the
  staff door;
- the side and back windows, the meter cupboard, the louvre and the light
  box;
- the roof fan and pipe;
- the lettered band (336 x 48), drawn on the band's own tile grid phase;
- the awning top and valance;
- the deck;
- flat patches.

`check_regions()` asserts two gutters between regions and checks that the
bands and regions agree with the metres they stand for.

### Tile and relief

- Joints are 0.55 px, which supersampling draws as fine lines. The grout is
  a mid grey (150, 150, 146) between the white and the accent tile; the dark
  plinth is grouted dark.
- Each tile takes a ±3.5 % hashed tone.
- Relief (height channel): tile faces cushioned 3 mm; aluminium sections
  25 mm; channel letters 40 mm; coping joints and felt laps 6 mm.
- Glass and what stands behind it are flat. They take glass roughness in
  the ORM.

### Weathering

`scripts/weathering.py` at the moderate level, lighter grime on the glazed
tile:

- soil, algae and specks on the plinth;
- splash on the accent tile and the curved kick;
- short runs under the coping's drip;
- kicked dirt on the doors and grime round the pulls;
- dirty sill flashings;
- a meter cupboard splashed and faded;
- the awning cloth greying toward its valance;
- deck dirt.

The lettering, the light box and the glazing stay clean.

### Filtering

Mip 3 at 75 m (`LOD2`: front, oblique, grazing) and mip 4 at 125 m (`LOD3`:
oblique, grazing), using `scripts/review_atlas_mips.py`:

- no colour leaks between regions and no seams on the curve;
- the awning stripes average to a pale accent tint;
- the lettering stays red;
- the tile averages to the band colours without moiré at those
  distances.

## Glazing treatment

- **Method:** `scripts/glazing.py`. `rooms()` paints every pane after the
  albedo resolve, with the door's vision panel and transom as one room
  (`merge=8`). Glass base is `glazing.BASE` and roughness 0.08, metallic 0.
- **Measured** by the validator under the emission's neutral mask:
  - sRGB 54 (linear 0.033) in all four variants;
  - 0.23–0.24 x the trim.
- **Room variation behind the glass** (allowed in albedo):
  - the display windows' vertical blinds (sRGB about 98, drawn to both
    sides);
  - the pot plants in the display windows and the curve.
- These are their own ids with glass roughness, and are lit as panes in the
  emission. No departure from the Style Direction band.

## Variant list

Textures only; geometry and UVs are shared. Each variant changes the band
tile, the accent tile (and the awning stripe that follows it), the plinth,
the coping paint and the staff door.

| Variant | Band | Accent tile | Coping |
| --- | --- | --- | --- |
| `teal_tile` (default) | white | muted teal | grey |
| `rose_tile` | white | muted salmon | warm grey |
| `blue_tile` | white | grey-blue | cool grey |
| `brown_tile` | cream | brown | dark brown |

The lettering and the light box are the same dark red in all four. As a
low-rise building it takes four variants, within the 3–6 range.

## Night lighting

`_emission.png` is bound on every tier, factor 0 by default
(`window_emission`). The reference lit factor is fluorescent,
`LIT_FACTOR = (1.0, 0.88, 0.72)`, as the catalog's shops.

### Glazing

- Neutral white, made into lit rooms by `glazing.night_rooms()` (the door
  merged as one room).
- The blinds and plants are lit as the pane they stand behind; none of them
  is drawn in the emission.

### Luminous fixtures

These are written in non-neutral colours, so the validator reports them as
fixtures (18,168 mask pixels):

- the letters: sRGB (226, 60, 44);
- the light box's diffuser: (255, 230, 200);
- the light box's red graphics: (150, 26, 20), far dimmer, so the mark
  reads at night as by day.

### Control

- One control for the whole building: windows, letters and light box share
  the emissive factor.
- Shared UVs prevent per-window control: both display windows sample one
  region.
- No schedule or occupancy is baked in.

### Previews and pending checks

- `variants.png`: day row with emission off, night row with the reference
  factor, fixed camera and exposure (`scripts/variant_previews.py`).
- Night review renders: all four tiers at 40 m oblique, emission on. The
  lit pattern is consistent across tiers; `LOD3` drops the light box.
- No lamp was placed to simulate spill. Any glow on the ground in the
  renders is the renderer lighting from the emissive surfaces.
- Pending in the consumer: runtime control and the intensity and colour of
  the fixtures against the windows.

## Export

`.glb` with external PNGs, from `asset_build`'s `export_all()`:

- `export_yup=True`, `use_selection=True`, `export_apply=True`,
  `export_keep_originals=True`, cameras and lights off;
- exported lit, then the emission factor rewritten to zero;
- the placeholder `bufferView` stripped (`scripts/glb_images.py`).

### Bindings

Traced in the GLB JSON chunk of all four tiers:

- one material, `kampaamo_tile_corner`;
- `baseColorTexture` → `kampaamo_tile_corner_albedo_teal_tile.png`;
- `metallicRoughnessTexture` and `occlusionTexture` →
  `kampaamo_tile_corner_orm.png`;
- `normalTexture` → `kampaamo_tile_corner_normal.png` (scale 1);
- `emissiveTexture` → `kampaamo_tile_corner_emission.png`, with
  `emissiveFactor [0, 0, 0]`.

All bindings are on `TEXCOORD_0`. Every image has a `uri` and no
`bufferView`. Attributes: `POSITION`, `NORMAL`, `TEXCOORD_0`; no tangents
(MikkTSpace in the consumer).

### Frame

Front toward Blender -Y, exported +Y up, +Z front. The pivot is at ground
level, at the centre of the `LOD0` plan bounds, for every tier. The
validator measures min z 0 and centre (0.000, 0.000) on all four tiers.

### Facts sidecar

`export/kampaamo_tile_corner.model.json`, version 1:

- `footprint`: the ground-level outline with the recess (`LOD0` facets);
- `storeys`: one storey at floor 0, 86.57 m²;
- `dwellings`: 0;
- `hero`: false;
- doors:
  - `salon`: entrance, main, 0.94 x 2.10 m, on the front wall at build
    (1.75, -4.5);
  - `staff`: service, 0.90 x 2.10 m, on the back wall at build (-2.0, 4.5).

### Rebuild

From the asset folder:

```bash
python3 facade_atlas.py export
blender --background source.blend --python build.py
```

Run the first step with system Python (numpy, scipy, Pillow). The second
builds, exports, renders `preview.png` and `variants.png`, saves
`source.blend` and writes the sidecar. `build.py -- facts` rewrites the
sidecar alone, from a committed tree.

## Review status

### Completed here

- **Validator:** `scripts/validate_asset.py` reports no FAIL. The one WARN
  is `source.dirty`, which clears when the sidecar is rewritten from a
  committed tree.
- **Working views:** three passes of the six views (front, rear, east and
  west orthographic, top-down, raised front-corner aerial), plus a rear
  aerial and three eye-level views with a 1.8 m figure, at `LOD0` and
  checked at `LOD1`–`LOD3`.
  - Pass 1: tile grout too heavy, a checkerboard plinth, solid-accent
    awning cheeks. Fixed with finer, mid-grey grout, dark plinth joints,
    fabric-white cheeks and heavier lettering strokes.
  - Pass 2: confirmed the fixes; checked the lower tiers.
  - Pass 3: added the staff door's canopy to the plain back elevation.
- **LOD and night:** LOD pairs at 35, 70 and 120 m, and the night set on all
  tiers (LOD review, Night lighting).
- **Mips:** mip 3 and mip 4 stress renders (Texture set).
- **GLB:** material bindings and image sources on all four tiers.
- **Mesh:** manifold and hidden-surface checks on all four tiers.
- **Glazing:** measured against the band in all four variants.
- **Palette:** muted tile colours, dark red lettering, white aluminium,
  grey coping, dark felt. No baked light or reflection in the albedo.
- **Originality:** the lettering is generic Finnish ("hair salon"), with no
  business name, brand or chain look. The design is a composite, not a
  reproduction of any real building.

### Pending, outside this repository

- Consumer import, LOD switching and runtime emission control.
- Consumer-side mipmap and anisotropic filtering.
- Performance in a representative scene.

## Tooling versions

- **Blender 5.3.0** (hash `02f0899d78e3`, build date 2026-11-11). Built
  headless (`blender --background ...`), and `source.blend` was saved by
  5.3.0. This is a known-good diagnostic, not a pin; `build.py` asserts the
  version floor and the exporter flags.
- **Blender MCP addon: not used.** Visual iteration was done on rendered
  views (`render_views()` in `build.py`, `scripts/review_asset.py`).
- Textures baked with the system CPython, numpy, scipy and Pillow:
  `python3 facade_atlas.py export`.
