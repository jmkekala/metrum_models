# kampaamo_tile_corner

## Style brief

A late-1980s Finnish postmodern corner shop let to a hair salon (kampaamo):
one tall storey clad in small glazed ceramic tile, a flat roof hidden behind
a parapet with a thin painted coping, and a quarter-round corner as its
signature. Generic and composite: no real building, business, brand or
chain look.

- Tile is 250 x 125 mm in half bond, on 125 mm courses: a dark tile
  plinth, a muted accent tile (teal by default) over the whole shopfront
  storey, and a white tile sign band above it with one accent course near
  its top. The band runs on unbroken round the curve.
- At the curve the shopfront stands 0.6 m back from the band under a tiled
  soffit. It is glazed in facets between slim white mullions on a smaller
  arc, over a dark tile kick. One slim round white column on a short dark
  steel shoe stands free under the middle of the band. A small projecting
  light box (scissors over a comb) stands out of the band above the column.
- On the straight front are two display windows under striped fabric
  awnings. Each is its own room: vertical blinds drawn aside over a few
  small pot plants in one, a half-lowered venetian blind over a plant, a
  row of hair-care bottles and a trailing plant in the other. The word
  KAMPAAMO is set in dark red block capitals on the band over them. The one
  shop door is beside the corner, at grade, under a thin steel canopy hung
  on two rods.
- On the sides and back: two windows on the left side; on the right side a
  window, the meter cupboard and an exhaust louvre; at the back a small
  window, the staff door under a small steel canopy, and the wall ladder to
  the roof. On the felt deck are a roof extract fan, two vent pipes, two
  roof drains and a flush roof hatch.

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
- its shoe: a prism of 0.15 m radius and 0.15 m height round the column's
  foot, in the coping's darker paint (`SHOE`); on every tier that keeps the
  column, with the column's side count;
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

- Facets per tier: 8 / 6 / 4 / 3, the same for the band, the soffit, the
  shopfront, the parapet and the coping (painted on `LOD3`). Every tier
  that keeps the column or the light box has an even count, which puts a
  vertex at the curve's middle where they stand; `LOD3` has neither, and
  its three facets keep the corner round at the last switch
  (`check_layout()` asserts this per tier).
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
  `COLUMN_*`, `SHOE`);
- the other openings;
- what is painted on the deck, in plan metres (`DRAINS`, `HATCH`, `WALK`).

`build.py` adds the per-wall item lists, the roof plant and the ladder's
place. `check_layout()` checks:

- openings clear of corners and of each other;
- door leaves within 2.0–2.4 m, with room for a transom;
- awnings between the shopfront head and the lettering, and clear of the
  canopy;
- the staff canopy over its door and clear of the back window and the
  ladder;
- the column and its shoe under the soffit, clear of the shopfront, and
  the light box buried in the parapet's solid;
- even facet counts on every tier with a column or light box;
- the parapet at least 0.5 m over the deck;
- the roof plant clear of the parapet;
- the ladder's place.

## Per-tier triangle counts

| Tier | Triangles | Ceiling |
| --- | --- | --- |
| `LOD0` | 1,168 | 12,000 |
| `LOD1` | 912 | 4,000 |
| `LOD2` | 494 | 1,500 |
| `LOD3` | 258 | 500 |

- **LOD0** carries everything:
  - 8 curve facets;
  - openings cut (shopfront and door 0.15 m, side and back windows 0.12 m,
    staff door 0.10 m);
  - column and its shoe 16 sides (the shoe about 130 triangles), fan 12,
    vents 8;
  - the canopy rods;
  - the ladder with every rung and bracket.
- **LOD1**: 6 facets, column and shoe 10 sides, fan 8, vents 6, ladder
  every other rung.
- **LOD2**:
  - openings flat on the wall plane with the same regions;
  - 4 facets, column and shoe 6 sides, fan 6 sides;
  - vents and canopy rods dropped;
  - ladder every fourth rung, no brackets.
- **LOD3**:
  - 3 facets (10 triangles more than 2 would cost);
  - the coping is not modelled: the parapet runs to 4.125 m with the coping
    painted on its face and top;
  - column, shoe, light box and fan dropped;
  - the ladder's bare rails kept, because they set the extents;
  - awnings and both canopies kept: they set the front and back plan bounds
    and carry the front's identity.

This is a small one-storey shop, in line with the catalog's sheds and shops
(300–1,000 at `LOD0`). The parapet, curve and recess are cheap; most of the
LOD0 count is the ladder, the round column with its shoe and the roof
plant.

## LOD review

### Method

- Review camera: perspective, 1920x1080, 50° vertical FOV
  (`scripts/review_asset.py`, Cycles 24 samples).
- Pairs at the switches:
  - `LOD0`/`LOD1` at 30 and 40 m, front and oblique, noon and reverse sun;
  - `LOD1`/`LOD2` at 65 and 75 m, front, oblique and aerial, noon;
  - `LOD0`/`LOD2`/`LOD3` at 115 and 125 m, front, oblique and aerial, noon.
- Night, emission on: all four tiers at 20 and 40 m, front and oblique.
- Every tier at 20, 35, 70 and 120 m, front and oblique, noon; `LOD2` and
  `LOD3` side by side at 120 m, and at 20 m oblique for a consumer that
  switches by screen size and shows `LOD3` near.
- Intended switches are the catalog defaults: 35 / 70 / 120 m. No override.

### Findings

- **35 m:** `LOD0` and `LOD1` cannot be told apart. 6 facets against 8 does
  not show on the curve, and the thinned ladder is behind the building.
- **70 m:** flattening the openings at `LOD2` keeps their position,
  proportion, frames and glass. The 0.15 m reveal shadow goes, as the
  contract's default allows. The 4-facet curve still reads round.
- **120 m:**
  - `LOD3`'s 3-facet curve reads as a rounded corner beside `LOD2`'s 4
    facets; the corner no longer turns into a chamfer at the switch. Up
    close (20 m) the three facets show as facets, as `LOD2`'s four do, and
    the band, soffit and recessed shopfront stay aligned.
  - The light box, the column and its shoe go: the column is 0.22 m, under
    2 px.
  - The parapet, lettering, awnings, canopy, recess and colour bands all
    hold.

## Interior geometry

The validator's sampled hidden-surface test passes on every tier:

| Tier | Hidden triangles | Share | Vertical area |
| --- | --- | --- | --- |
| `LOD0` | 71 / 1,168 | 6.1 % | 0.0 m² |
| `LOD1` | 43 / 912 | 4.7 % | 0.0 m² |
| `LOD2` | 28 / 494 | 5.7 % | 0.0 m² |
| `LOD3` | 8 / 258 | 3.1 % | 0.9 m² |

- On `LOD0`–`LOD2` the candidates are horizontal. They are the coping's
  0.0625 m drip underside at z 4.03 along its inner edge, over the felt
  upturn. It is a real exterior surface, visible only from the roof deck,
  and is kept.
- The `LOD3` candidates at (3.2, 4.9, 1.7–3.4) are the inner faces of the
  ladder's two bare rails, which face each other across the ladder. They
  are kept because the rails set the extents.
- There are no buried partitions. The parapet's top inside the coping, the
  wall band above the coping's drip, the column's foot inside its shoe, and
  the buried backs of the column, awnings, canopies, rods, light box and roof plant are removed by the
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
- **Behind the glass:** the blinds, the pot plants and the bottles are
  painted in the two display regions and the curve region, one room each
  (Glazing treatment). They are flat room content, not geometry.
- **On the deck:** the felt laps, the two roof drains and the roof hatch
  are painted flush in the deck region; the hatch has no modelled curb.
- **Not modelled:**
  - a scupper or overflow (the roof drains are painted);
  - door hardware beyond the painted pull;
  - signage beyond the band's lettering and the light box;
  - lamps over either door.

## Texture set

- **Size and density:** one 1024 atlas at 64 texels/metre on every wall,
  opening, fitting, awning and coping, with these local deviations:
  - the light box face at 96 px/m (0.625 x 0.8125 m on 60 x 78 px);
  - the roof deck at 32 px/m (9.375 x 8.375 m on 300 x 268 px; seen from
    the air only, where its laps, drains and hatch carry it).
- **Rasterising:** `scripts/atlas.py`, supersampled at `atlas.SS` = 4,
  box-filtered in linear light. `atlas.pad()` runs last, with a 6 px gutter
  at every region and band.
- **Unique textures:** seven 1024 PNGs — four albedos, one shared ORM, one
  normal map and one emission map. ORM, normal and emission are shared by
  every variant.

### Layout

Tiling bands, U wrapping:

- **Wall band**, rows 6–270, z 0–4.125 m, 33 tile courses:
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

- row A (y 380): the curved shopfront (191 x 176), the shop door, the left
  display window (152 x 152), the staff door, the side and back windows,
  the meter cupboard, the louvre, the light box, the roof fan and pipe;
- row B (y 576): the lettered band (336 x 48), drawn on the band's own
  tile phase; the awning top and valance; flat patches;
- row C (y 722): the deck (300 x 268) and the right display window
  (152 x 152).

Each display window and the curved shopfront has its own region, so the
three rooms behind the glass differ. `check_regions()` asserts two gutters
between regions and checks that the bands and regions (both display
windows and the deck included) agree with the metres they stand for.

### Tile and relief

- **Module:** 250 x 125 mm glazed tile in half bond, 16 x 8 px. Courses
  are 125 mm, so every colour change (plinth, head, accent course, sign
  rows) is on a course line; every other course is shifted 125 mm, so the
  bed joints read as lines and the perpends stagger. 64 tiles span the
  atlas, so the band still wraps in U.
- **Joints** are 0.42 px, about 6.5 mm: a little heavier than a real
  4–5 mm joint, so that supersampling still draws a line. Grout is two
  ids: a light grey (194, 194, 188) in the white band and a mid grey
  (156, 156, 150), a little lighter than the accent tile, in the shopfront
  storey; `brown_tile` takes a darker brown-grey (112, 102, 92) there,
  because a light joint on brown half bond reads as brick. The dark plinth is grouted dark, its joints only its own tile at
  0.78 shade, so it reads as courses, not a checkerboard.
- Each tile takes a ±3 % hashed tone.
- Relief (height channel): tile faces cushioned 3 mm; aluminium sections
  25 mm; channel letters 40 mm; coping joints and felt laps 6 mm; the
  roof hatch's lid 30 mm.
- Glass and what stands behind it are flat. They take glass roughness in
  the ORM.

### Scale against the catalog

Front views at 20 and 35 m with identical `review_asset.py` settings, this
asset beside `liikekeskus_pharmacy` (64 px/m, split-face block): the two
are equally sharp, and the tile courses and the pharmacy's block courses
read at a similar scale. The earlier 125 mm square grid read as bathroom
tile with joints heavier than real; the half bond with lighter grout reads
as a coursed tile facade, and the white band reads as a quiet surface with
fine lines.

### Rooms behind the glass

Painted in the albedo under glass roughness (`BEHIND_GLASS`); in the
emission they are lit only as the pane they stand behind:

- left display window: vertical blinds drawn to both sides, a snake plant
  (0.42 m), a small flowering plant and a low bush;
- right display window: a venetian blind let down two fifths of the big
  light, a bush (0.36 m), five hair-care bottles and a trailing plant;
- curved shopfront: a small trailing plant in the first light, a snake
  plant in the third, a venetian blind a third of the way down the last.

Plants are 0.24–0.42 m tall overall in muted green (50, 60, 43) with
per-leaf shade, in terracotta pots 0.10–0.13 m tall; flowers dusty rose
(146, 98, 100); bottles a neutral (124, 118, 112) at varied shade.

### Deck

Bitumen felt in one-metre rolls lapped along X (a 6 mm lap and a dark
line each metre) with staggered end laps; shallow ponding; two roof drains
(a dark grate in a galvanised ring, silt dried round each); a galvanised
roof hatch lid 0.8 x 0.8 m with its hinge line; a scuffed walking line
from the ladder's head to the fan.

### Weathering

`scripts/weathering.py` at the moderate level, lighter grime on the glazed
tile:

- soil, algae and specks on the plinth;
- splash on the accent tile and the curved kick;
- short runs under the coping's drip;
- kicked dirt on the doors and grime round the pulls;
- dirty sill flashings;
- a meter cupboard splashed and faded;
- the awning cloth greying toward its valance, whose foot is bound with a
  tape in the accent colour;
- deck dirt, silt round the drains and the walking line.

The lettering, the light box and the glazing stay clean.

### Filtering

Mip 3 at 75 m (`LOD1` and `LOD2`: front, oblique, grazing, aerial) and
mip 4 at 125 m (`LOD2` and `LOD3`: oblique, grazing, aerial), using
`scripts/review_atlas_mips.py`, on the current layout (row C added):

- no colour leaks between regions and no seams on the curve;
- the awning stripes average to a pale accent tint;
- the lettering stays red;
- the half-bond tile averages to the band colours without moiré at those
  distances;
- the deck stays dark felt; the hatch and drains fade to pale specks at
  mip 4.

## Glazing treatment

- **Method:** `scripts/glazing.py`. `rooms()` paints every pane after the
  albedo resolve, with the door's vision panel and transom as one room
  (`merge=8`). Glass base is `glazing.BASE` and roughness 0.08, metallic 0.
- **Measured** by the validator under the emission's neutral mask:
  - sRGB 55 (linear 0.035) in all four variants;
  - 0.24–0.25 x the trim.
- **Room variation behind the glass** (allowed in albedo), a different
  room in each display window and the curve (Texture set, Rooms behind the
  glass): vertical and venetian blinds (sRGB about 98 before shade), pot
  plants, flowers and bottles.
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
- The blinds, plants and bottles are lit as the pane they stand behind;
  none of them is drawn in the emission.

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
- Each display window and the curve has its own region, but the mask has
  the one control, so there is no per-window control.
- No schedule or occupancy is baked in.

### Previews and pending checks

- `variants.png`: day row with emission off, night row with the reference
  factor, fixed camera and exposure (`scripts/variant_previews.py`).
- Night review renders: all four tiers at 20 and 40 m, front and oblique,
  emission on. The lit pattern is consistent across tiers; `LOD3` drops
  the light box. Each display window is now its own lit room, at its own
  level.
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
  - Polish, two passes: a room of its own in each display window and the
    curve, with smaller, muted plants; half-bond tile with lighter grout;
    the column's shoe; the deck at 32 px/m with laps, drains and a hatch;
    the awning valance's binding; three facets at `LOD3`. Before and after
    sets (every tier at 20, 35, 70 and 120 m, front and oblique, noon; the
    night set) rendered with identical settings and compared with
    `scripts/review_compare.py`.
- **Scale:** front views at 20 and 35 m beside `liikekeskus_pharmacy`
  with identical settings (Texture set, Scale against the catalog).
- **LOD and night:** every tier at 20, 35, 70 and 120 m, `LOD2`/`LOD3` at
  120 m and up close, and the night set on all tiers (LOD review, Night
  lighting).
- **Mips:** mip 3 and mip 4 stress renders on the current layout (Texture
  set).
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

## Revision log

- **2026-11-22:** polish. Each display window has its own atlas region
  (`DISPLAY2_R`, row C) and room; plants smaller, muted and of four kinds,
  thinned in the curve; bottles and venetian blinds added. Tile changed
  from a 125 mm square grid to 250 x 125 mm half bond with lighter, finer
  grout (two grout ids). `LOD3` curve 2 → 3 facets (248 → 258
  triangles). Column shoe added (`LOD0`–`LOD2`). Deck region 16 → 32
  px/m with laps, drains, a hatch and a walking line. Awning valance bound
  with an accent tape. Plan bounds, footprint and doors unchanged.
