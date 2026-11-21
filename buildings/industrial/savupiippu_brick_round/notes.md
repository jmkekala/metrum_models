# savupiippu_brick_round

## Style brief

A composite free-standing chimney stack (*savupiippu*) of a small Nordic
town's coal-fired heat and power plant of the 1950s–60s. It is one of five
separate pieces of the plant (the boiler and turbine hall, coal reception,
office and transformer yard are other assets). Each stands alone on a lot:
no ground, no flue duct to the hall.

A round, battered stack of dull red radial brick, 46.5 m tall, about 2.4
times the boiler house, 4.1 m across at its foot and 2.4 m at its top (top
to foot 0.58). It stands on a massive brick base, 6.8 m square on a low cast
concrete footing, turned to an octagon by sloping brick fillets at its
corners and to the round by a concrete wash. The shaft is plain and runs
straight up to a pale cast concrete head band under a thin steel cap ring,
open at the top round a sooted flue. Soot thickens up the stack's upper
third and is heaviest on the head; three thin galvanised flats ring the top
10 m. A narrow steel service platform with a railing rings the head 1.5 m
under the rim; an iron ladder climbs the back along the batter from 2.5 m
above the base to it. Three aviation obstruction lamps on the head band
glow at night. On the base's front, toward the boiler house, is the closed
flue inlet under a concrete lintel; low in its east wall a cast iron
cleanout hatch.

It is the plant's landmark from the play camera: the taper, the base's
fillets, the head band, the platform's deck and the open top are geometry
on every tier; the ladder, railing and platform brackets are geometry
close up and the ladder a painted line beyond 70 m.

## Category and secondary use

`buildings/industrial/`, as part of a heat and power plant. No secondary
use.

## Hero/landmark status

**No budget exception.** The stack is a landmark by height only: every tier
is under the ordinary ceilings and the atlas is 1024². There is no height
limit in CLAUDE.md, only triangle ceilings.

## Footprint

| | Width (X) × depth (Y) × height |
| --- | --- |
| Base (the outer wall outline) | 6.80 × 6.80 m, square walls to 4.20 m |
| Overall | 6.80 × 6.80 × 46.50 m |

Nothing stands outside the base: the platform reaches 2.0 m from the axis,
the ladder's rails 1.6 m, and the shaft's foot is 4.1 m across.

Heights: footing course 0–0.31 m; square walls to 4.20 m; corner fillets
4.20–5.40 m, where the plan is an octagon 6.8 m across its flats; the
octagon's concrete coping 5.40–5.70 m; the wash rising to the shaft's foot
at 6.20 m. The shaft runs 6.20–44.70 m, its outside radius falling straight
from 2.06 m to 1.19 m (a batter of 2.26 %). The head band, 0.06 m proud,
runs 44.70–46.50 m at radius 1.25 m, its top 0.10 m the painted steel cap
ring; the rim at 46.50 m. The platform's deck is 44.88–45.00 m, to radius
2.00 m; its hand rail's top 46.00 m. The lamps stand 46.02–46.30 m.

The pivot is at ground level on the base's centre, which is also the
shaft's axis. It is taken from `LOD0` and every tier has the same extents.

## Story height

n/a: a chimney has no occupied storey. The facts sidecar's `storeys` is
empty (see Export, *Facts sidecar*).

## Door leaf height

n/a: the stack has no pedestrian door. The two openings in the base are not
doors:

- **Flue inlet** (front, -Y): 1.625 × 2.00 m, sill at 1.00 m, head at
  3.00 m under a 0.25 m cast concrete lintel. It is closed by a bolted black
  steel blanking plate in an angle frame, with a small inspection door low
  in it.
- **Cleanout hatch** (east): 0.70 × 0.91 m, sill at 0.44 m, a painted cast
  iron door on two strap hinges in an iron frame.

Neither reads at human scale as a door: the inlet's sill is a metre up, and
the hatch is half a door's height. The plant's hall carries the door scale;
the platform's 1.0 m railing and the ladder's 0.44 m width carry it at the
head.

## Window sills

n/a: no windows. The inlet's sill is at 1.00 m and the hatch's at 0.44 m.

## Eave overhang

n/a: no roof. The head band stands 0.06 m proud of the shaft's top; the
platform's deck projects 0.75 m beyond the band.

## Construction

`build.py` builds the stack as one closed solid directly, then unions the
attachments into it with `asset_build.union()`:

- the base's four square walls, the inlet cut into the front at
  `LOD0`/`LOD1` (0.25 m reveals in brick, a concrete sill and lintel
  soffit, the closure at the back) and painted flush at `LOD2`/`LOD3`; the
  hatch a flush face in the east wall on every tier;
- above them, each wall running on as a trapezoid between the corner
  fillets, the four fillets as sloping brick triangles, and the octagon's
  eight vertical coping faces;
- the wash, triangulated between the octagon's head (its corners and the
  points where rays to the shaft's vertices leave it) and the shaft's foot
  ring, whose vertices it shares;
- a surface of revolution: the shaft's ten lifts, the head band's foot
  annulus, the band, the rim, and the flue's lining straight down 1.0 m from
  the rim's inner edge; the flue's floor at 45.50 m, inside the band; the
  base's floor on the ground;
- unioned closed solids: the three lamps (every tier), the platform (as
  far as the tier keeps it) and the ladder (`LOD0`/`LOD1`).

The stack's faces are shaded smooth round the circumference; edges are
sharp where the profile turns by more than 25° (the band's foot, the rim,
the wash's edges). The base and the attachments are flat-shaded.

### The base

A massive brick base: 6.8 m square to 4.2 m, the corner fillets rising
1.2 m over a 1.41 m run (40°) to an octagon whose flats are the walls'
planes, a 0.3 m concrete coping round the octagon, and a concrete wash
rising 0.5 m from the coping to the shaft (about 19°). The shaft's foot
stands 1.3 m inside the octagon's flats.

### The round

Side counts per tier: 24, 16, 12, 8. Vertices stand at r × 2 / (1 + cos(π/n)),
so the polygon's mean of apothem and corner radius is the true radius and
the shaft keeps its apparent width as sides drop. The back facet (+Y),
which carries the ladder, and the front facet (-Y), facing the inlet, are
centred on the axis on every tier.

### Head

Period head, no corbel: the shaft runs straight to a pale cast concrete head
band 1.8 m tall, 0.06 m proud, the top 0.10 m painted as the galvanised cap
ring. The rim is a 0.30 m ring round a flue of radius 0.95 m; the lining
and floor take the soot patch, the floor 1.0 m down at 45.50 m. The flue
stays recessed on every tier.

### Platform

A steel service platform 1.5 m under the rim: a 0.12 m deck from inside the
band out to radius 2.0 m (embedded 0.04 m in the band), a ring hand rail
(top 46.0 m) and knee rail (top 45.5 m), each a 0.05 × 0.05 m solid
polygonal ring, on six posts at 0°, 60°, … 300° from +X (none at the
ladder, at 90°), and six brackets from the shaft at 44.1 m to the deck's
underside at radius 1.82 m. No grating: the deck is opaque. Per tier
(`PLATFORM` in `build.py`): everything on `LOD0`/`LOD1`; deck, hand rail,
posts and brackets on `LOD2`; the deck alone on `LOD3`, so the head's
silhouette keeps its flange.

### Access and lightning protection

A continuous iron ladder up the back (+Y), on `LOD0`/`LOD1`: two rails
0.05 × 0.07 m, centred 0.22 m either side of the axis and 0.20 m off the
back facet, following the batter in a straight line from 8.70 m (2.5 m
above the wash's top) through the deck to grab handles at 46.0 m; a
0.03 m square rung every 0.333 m (108 rungs) on `LOD0`, every third rung on
`LOD1`; ten pairs of brackets into the shaft, at 8.9 m, every 4 m from
12.7 m, and at 44.3 m. No hoops: `scripts/roof_safety.py`'s ladder and
cage assume a vertical wall, and a cage would cost about 3,000 triangles at
`LOD0`. `LOD2`/`LOD3` carry the ladder as paint on the back facet (Texture
set, *The ladder strips*). The ladder stands inside the base's plan, so it
sets no extent.

The earlier painted copper down conductor is gone: the back facet of the
near tiers samples the tiling band like every other facet, and has no
unique strip to carry it. The ladder's rails stand for the lightning path;
see Known simplifications.

### Authored parameters

`facade_atlas.py` holds every shared number: the base (`BH`, `Z_FOOT`,
`Z_SQ`, `Z_OCT`, `Z_CAP`, `Z_SHAFT0`), the shaft (`R0`, `R1`, `SEG`,
`NLIFT`, `Z_LADDER0`, `Z_HEAD0`, `LIFTS`), the head (`R_HEAD`, `Z_TOP`,
`CAP_RING`, `R_FLUE`, `FLUE_DEPTH`), the platform (`Z_DECK`, `DECK_T`,
`R_DECK`, `RAIL_R`, `RAIL_Z`, `POSTS`, `STRUT_*`), the ladder
(`LADDER_HALF`, `RAIL_W`, `RAIL_D`, `STANDOFF`, `RUNG_PITCH`, `RUNG_EVERY`,
`LADDER_BRACKETS`), the lamps (`LAMP_ANGLES`, `LAMP_Z`), the inlet, lintel
and hatch, `SIDES`, and the atlas layout. `check_layout()` asserts:

- the inlet clear of the corners and under its lintel, the hatch low and
  above the footing; the base's heights in order and the wash at least
  0.8 m wide;
- on every tier, every lift's facets within their band's overrun and its
  taper within the band's left margin, the far tiers' back facet inside its
  strip, the head band inside its region; the lifts running from the
  shaft's foot to the head;
- the rim at least 0.25 m wide, the flue's floor inside the band, the lamps
  under the cap ring;
- the deck about 1.5 m under the rim, the railing clear of the rim, the
  lamps and the ladder, no post at the ladder;
- the ladder's foot out of reach, its rails clear of the head band and
  inside the plan, its brackets on the shaft, its grab handles no higher
  than the railing.

## Per-tier triangle counts

| Tier | Sides | Triangles | Ceiling | What changes |
| --- | --- | --- | --- | --- |
| `LOD0` | 24 | 5134 | 12,000 | inlet recessed; full platform; ladder with every rung |
| `LOD1` | 16 | 2784 | 4,000 | the same, 16 sides, every third rung |
| `LOD2` | 12 | 924 | 1,500 | inlet flush; ladder painted; no knee rail |
| `LOD3` | 8 | 412 | 500 | deck alone; lamps kept |

The stack itself is about 900 triangles at `LOD0` (the shaft's ten lifts
2n each, because the texture repeats per lift; the head, rim, lining and
floor; the base and its fillets, coping and wash about 200). The ladder is
most of the rest: each rung is a box whose ends hole the rails' inner
faces, so 108 rungs cost about 2,800 triangles with the rails; the platform
about 900, the lamps about 40. Ladder, platform and lamps together are
about 3,700 at `LOD0`, more than CLAUDE.md's quarter-of-ceiling trim
allocation (3,000): the ladder is the owner's requested change and its rungs
are what make it read as a ladder at 30 m (LOD review); `LOD1` thins them to
a third. Nothing is padded.

## LOD review

Intended switches are the catalog defaults: 35, 70 and 120 m. No overrides.
The review camera was perspective, 1920×1080, 50° vertical FOV, distance
along the view to the front face (`scripts/review_asset.py`), Cycles CPU, 16
samples with denoising, AgX, exposure 0; close renders at 1280×960, 40–50°
vertical FOV, 24 samples. Renders are in the local, untracked
`review/power_plant_rev_2026_11_21/savupiippu_brick_round/`
(`before/` and `after/`, the same sets; `compare/` the sheets).

Pairs compared with identical camera and light:

- `LOD0`/`LOD1` at 30/40 m, front, oblique and rear, noon;
- `LOD1`/`LOD2`/`LOD3` at 65/75 and 115/125 m, oblique, noon and reverse
  sun;
- `LOD0` against `LOD3` at 150 and 300 m, front, oblique and 45° aerial,
  noon: the landmark range;
- close renders of every tier: the head from 14 m (front, rear, from
  above), from 60 m and at night; the base from 20–22 m (front, east,
  rear); the ladder from 30 m behind; the whole stack at night from 90 m.

Findings:

- **The round.** 24 to 16 sides is not visible at 35 m; 12 at 70 m and 8 at
  120 m keep the shaft's width on smooth shading.
- **The head.** The band, the platform's deck and the open flue keep their
  shape on every tier. The railing's 0.05 m rails are under two pixels
  beyond 35 m; `LOD2` keeps the hand rail so the switch at 70 m loses only
  the knee rail; `LOD3` keeps the deck, which carries the head's flange in
  outline to 300 m.
- **The ladder.** At 30–40 m from behind, the modelled rails and rungs read
  as a ladder in light and as a dark line in shade. From 70 m the painted
  ladder on `LOD2`/`LOD3` (dark rails and rungs over a darkened band 0.44 m
  wide) reads as one dark line up the back, as the thin modelled rails do on
  `LOD1` at that range. The painted line starts at the same 8.7 m.
- **The inlet** goes flush at `LOD2`: its 0.25 m recess is about 3 px at
  70 m, and the black plate keeps the opening's weight.
- **The soot** darkens the upper third from 32.7 m to the head; in the
  catalog preview and at 60–150 m it reads as a darker, streaked top to the
  shaft under the pale band, and at 300 m as a slightly darker top.
- **The lamps** are about a pixel from 120 m by day; at night, from 90 m,
  they read as points of light at the head on every tier (`LOD3`
  included). Night views farther out were not rendered.

The six working views (`review_asset.py --six-views`: orthographic front,
back, left, right, top and a 45° aerial) were looked at for `LOD0` and
`LOD3`.

Pending in the consumer: real LOD switching, shadows of a 46 m stack in the
consumer's shadow cascades, and performance.

## Interior geometry

The validator's hidden-surface test reports 0 hidden triangles on every
tier. The stack has no interior partition: the union removes the deck's inner edge
inside the band, the rung ends inside the rails, the rails' run through the
deck and the brackets' ends inside the shaft. The only closure faces are
the base's floor on the ground and the flue's floor, which is exterior
surface seen from above and lit by the open top.

## Known simplifications

- The flue is 1 m deep and floored; the real stack's flue runs to the
  inlet. The lining is not tapered.
- The ladder has no hoops or cage, and passes through the deck without a
  modelled hatch; the deck is a solid plate, not grating.
- The galvanised flats, the cap ring, the head band's formwork joints, the
  hatch and the inlet's closure are texture with relief in the normal map.
- No lightning finial or down conductor: the ladder's rails are taken as the
  lightning path.
- The lamps are boxes of housing and lens, not domes.
- The wash's and the inlet's soot are static.
- No flue duct, foundation slab, ground or fence.

## Texture set

One 1024² atlas at 64 px/m, rasterised by `scripts/atlas.py` at `atlas.SS`
= 4 and padded last by `atlas.pad()`. Rows from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–269, x 0–870 | BASE | the base's walls, z 0–4.2 m, V = height; range A (x 0–435) the east, rear and west walls, range B the front's |
| 6–258, x 880–992 | unique | the inlet's closure; the wash seen from above |
| 276–540 | MID, U1 | shaft bands with their ladder strips |
| 544–808 | U2, U3 | shaft bands with their ladder strips; at x 940–1004 the hatch, the lamp, flat patches |
| 816–932 | HEAD | the head band, unwrapped round the stack; at x 532–712 one side of the octagon's coping |

### The shaft's bands

The stack is 46.5 m tall and the atlas holds 16 m, so the shaft is cut into
4 m lifts (a part lift of 2.5 m at its foot, then nine), each sampling a
band 256 rows tall whose V tiles. Every band also tiles in U, on a 256 px
(4 m) period: it is painted 40 px further left and an overrun further right
(110 px for MID, 78 for the narrower upper lifts) from its own period, and
each facet's U is its chord length at 64 px/m less whole periods, the same
for its foot and head, so the bond runs on across every facet and no
facet's taper folds it over a wrap. MID is painted once; the noise over it
(tone, grime, weathering fields, roughness) is blended over the period's
last 32 px into what lies left of its start, so its ends meet. U1–U3 are
copies of MID with the soot laid over them, so V and U stay continuous from
lift to lift. Header bond at 42 courses a lift (0.095 m) repeats with the
period, and the half-brick offset alternates across a lift's joint. No
deviation from 64 px/m was needed.

### The ladder strips

Each band has a strip the back facet of `LOD2`/`LOD3` samples on the lifts
that carry the ladder: a copy of the band's first columns with the ladder
painted on it, two dark rails 0.05 m wide and a rung every 0.333 m, the
brick between them in the ladder's shade. `LOD0`/`LOD1`'s back facet
samples the band like every other facet, behind the modelled ladder. The
part lift under the ladder's foot samples MID's top 2.5 m, without strip.

### The base's trapezoids and fillets

The base band holds the walls to 4.2 m only. The trapezoids and fillets
above sample range A 14 courses (1.33 m) lower, where it is plain brick,
the courses aligned; the fillets' coursing is level and runs along their
head.

### Deviations from 64 px/m

- The wash is mapped from above at 16 px/m (plain concrete, seen from
  above).
- The lining, both floors, the rim, the band's foot and the steel of the
  platform and ladder use flat patches.

### Relief

Brick 6 mm proud of the joint; galvanised flats 8 mm; the painted ladder
30 mm; the inlet plate's frame, bolts and stiffener 25–35 mm; the hatch's
frame 20 mm and panel 12 mm; the head band's formwork joints −3 mm, its cap
ring 6 mm.

### Weathering and soot

`scripts/weathering.py` at its moderate level: grime, rain wash, faded
paint on the hatch and lamp housings; soil and algae on the footing,
splash-back and salt bloom on the base's brick; dirt on the coping and the
wash; runs and rust on the head band and cap ring; rust and runs on the
inlet's plate and the hatch's foot. MID gets periodic noise only.

The module has no soot, so `facade_atlas.soot()` darkens shade and adds the
module's dirt field: on the shaft by height alone, nothing below 32.7 m
and thickening as 0.95 t^1.3 to the head (t the fraction of the way from
32.7 to 44.7 m), modulated by vertical streaks periodic round the stack;
over the head band from 0.5 at its foot to 1.0 at the cap ring, streakier;
a soot plume over the inlet's lintel. Mean sRGB of the plain shaft per
lift, from MID to U3's top, falls from about (111, 82, 73) to about
(67, 52, 45); the head band's from about (124, 121, 116) at its foot to
(94, 91, 86) under the cap ring.

### Filtering

Mip stress renders were not rerun for this revision (pending, Review
status). Consumer filtering is pending.

Unique textures: six 1024² RGB PNGs (three albedos, one ORM, one normal
map, one emission map), 4 MiB each in memory without mips. ORM, normal and
emission are shared.

## Glazing treatment

No windows. The three obstruction lamps' lenses are the only glass: dark
red glass, albedo sRGB (112, 30, 26) before weathering (lenses stay clean),
roughness 0.08, metallic 0 — inside the Style Direction band by mean value,
red by brief, as an obstruction lamp's lens is. They are painted directly,
not with `scripts/glazing.py`, which paints window panes as rooms; the
validator's glazing check measures them as the only neutral-mask glass.

## Variant list

| Variant | Meaning |
| --- | --- |
| `red_brick` (default) | dull red facing brick, the plant's shared red |
| `yellow_brick` | yellow (cream) brick |
| `brown_brick` | dark purple-brown clinker brick |

`red_brick` and `brown_brick` are the same constants, sRGB, on all five of
the plant's pieces:

| | `red_brick` | `brown_brick` |
| --- | --- | --- |
| Brick | (114, 73, 62) | (80, 59, 57) |
| Dark brick | (90, 59, 51) | (62, 46, 45) |
| Mortar | (125, 123, 118) | (108, 106, 102) |

`red_brick` is every brick-face colour of the catalog's red brick taken to
Y + 0.6 (c − Y), Y its Rec.709 luma, then times 0.94, and the mortar a
further 10 % darker. `brown_brick` is a dark clinker, well below the red in
value and redness, so the three variants read apart. Only the brick and
mortar change; concrete, steel, soot, the hatch's paint and the lamps are the same
in every variant. Geometry, UVs, ORM, normal and emission are shared.

## Night lighting

**Night-lit through its obstruction lamps.** `_emission.png` lights only the
three lamps' lenses: the lamp region's lens part (`LAMP_R`'s upper 13
rows, x 940–956, rows 631–644), a soft bright core falling to about 0.6 at
the lens's rim, neutral grey, written by `facade_atlas.lamp_emission()`.
Housings, the stack and everything else stay black. The lamps are boxes on
every tier, so every tier's lamps glow alike.

- **Control scope:** the consumer's intensity and colour apply to the whole
  mask, which here is the three lamps only, so the lamps take whatever
  colour the consumer gives this building. The mask is neutral so as not to
  bake a colour; a consumer that wants them red sets a red factor for the
  stack. One mask, one control: the three lamps cannot be switched or
  flashed apart.
- Bound as `emissiveTexture` on every tier, factor written as zero
  (default off) by `asset_build`'s export; the texture is kept at zero.
- `variants.png`: the three colours at `LOD0`, a day row above a night row
  at the catalog's warm reference factor (`window_emission.LIT_FACTOR`),
  the preview studio's camera, sun and exposure, so the night lamps there
  are warm rather than red. No light spill is simulated.
- Pending in the consumer: the lamps' colour and any flashing, steady-red
  being the obstruction lamp's usual state; their visibility at distance
  under the consumer's bloom and exposure.

## Export

```
python3 facade_atlas.py export                       # albedo x3, ORM, normal, emission
blender --background source.blend --python build.py  # meshes, previews, sidecar
```

Run the textures first. A first build from a factory scene is
`blender --background --python build.py`. Export settings, as
`asset_build`'s `export_all()` passes them: `export_format='GLB'`,
`use_selection=True`, `export_yup=True`, `export_apply=True`,
`export_keep_originals=True`, `export_cameras=False`,
`export_lights=False`; then `strip_embedded_images()` and the emission
factor rewritten to zero.

Bindings, the same on every tier: the default variant's albedo to
`baseColorTexture`; the ORM's G/B to `metallicRoughnessTexture` and its R to
`occlusionTexture`; the normal map to `normalTexture` at scale 1; the
emission map to `emissiveTexture`, factor zero. One material, backface
culling on, single-sided and opaque. Other variants swap the albedo file
only.

The preview uses the catalog's fixed camera orientation, lens, sun and flat
grey world, the distance fitted by `asset_build.fit_camera`: `LOD0`,
`red_brick`, lamps off.

### Facts sidecar

`export/savupiippu_brick_round.model.json`: the base's 6.8 × 6.8 m square
as the footprint, `storeys` empty, `dwellings` 0, `doors` empty, `hero`
false, the emission map among the textures. The stack has no door (the
cleanout hatch and the flue inlet are not doors) and no occupied floor, so
it lists neither and has no main door, which the schema allows.

## Review status

Checked here, in Blender:

- `scripts/validate_asset.py`: 0 FAIL. Every tier welded manifold, one
  material, uri-only images, normal map at scale 1, emission bound and
  default off, under its ceiling, pivot at ground and centred, 0 hidden
  triangles; six 1024² RGB PNGs; the lens measured as glass at sRGB 56
  (0.29–0.38 × trim) in every variant; the facts sidecar. The sidecar's
  `source.dirty` is true (written from an uncommitted tree); it must be
  rewritten from a committed one (`build.py -- facts`).
- `check_layout()` and the atlas's `check_regions()` and `check_bands()`.
- The six working views at `LOD0` and `LOD3`; close renders of the head,
  base and ladder on every tier; night renders of the head and the whole
  stack.
- LOD pairs around 35, 70 and 120 m, and `LOD0`/`LOD3` at 150 and 300 m.
- Before/after sheets against the previous revision.
- The three variants, day and night, in `variants.png`.
- Mean plain-shaft albedo of `red_brick` (MID's period): R − G = 28 sRGB
  levels.
- The plant palette pass: ORM, normal, emission, `red_brick` and
  `yellow_brick` albedos pixel-identical to the previous build, triangle
  counts and bounds unchanged; the base's clean brick (atlas rows 860–990,
  columns 0–560) measures sRGB (110, 80, 71) on `red_brick` and (82, 66, 64)
  on `brown_brick`; a 35 m oblique noon render of each variant before and
  after.

Pending:

- whole-atlas mip stress renders for the new layout (the narrow periodic
  bands and the ladder strips);
- in the consumer: import, orientation and pivot on reimport, LOD
  switching, shadows, filtering of the tiling shaft bands, the lamps'
  colour and flashing, performance.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`) throughout.
The MCP addon was not used. Texture generation used the system Python 3
with numpy, scipy and Pillow.

## Revision log

- **2026-11-21:** plant palette pass: `brown_brick` set to the plant's
  shared dark purple-brown clinker constants.
- **2026-11-21:** period revision. Tension bands every 2 m removed (three
  thin galvanised flats in the top 10 m instead); the corbelled head, crown
  course and cap replaced by a straight shaft to a pale concrete head band
  and painted steel cap ring; a steel service platform with railing and
  three modelled, night-lit obstruction lamps added; the 5.6 m plinth
  replaced by a 6.8 m square brick base with corner fillets, an octagonal
  coping and a wash (footprint and bounds changed); a modelled iron ladder
  up the back on the near tiers, painted on the far ones, replacing the
  painted step irons and down conductor; `red_brick` recoloured to the
  plant's shared dull red; soot over the upper third; the shaft's bands
  made periodic in U so that four of them fit the atlas. The asset became
  night-lit and ships an emission map and `variants.png`.
