# savupiippu_brick_round

## Style brief

A composite free-standing chimney stack (*savupiippu*) of a small Nordic
town's coal-fired heat and power plant of the 1950s–60s. It is one of five
separate pieces of the plant (the boiler and turbine hall, coal reception,
office and transformer yard are other assets). Each stands alone on a lot:
no ground, no flue duct to the hall.

A round, battered stack of red radial brick, 46.5 m tall, 4.2 m across at
its foot and 2.4 m under its head, on a square brick plinth with a cast
concrete footing course and a sloped concrete coping. Steel tension bands
ring the shaft every 2 m. The head is corbelled out in three steps to a
1.3 m head band, a projecting crown course and a cast concrete cap, and the
stack is open at the top round a sooted flue. Soot darkens the top lift and
the head. On the plinth's front, toward the boiler house, is the closed flue
inlet under a concrete lintel; low in its east wall a cast iron cleanout
hatch. Step irons and a copper down conductor run up the back, and three
aviation obstruction lamps sit on the head band.

It is the plant's landmark from the play camera: the taper, the head's
flare and the open top are geometry; the bands, irons, conductor, lamps,
hatch and inlet closure are texture.

## Category and secondary use

`buildings/industrial/`, as part of a heat and power plant. No secondary
use.

## Hero/landmark status

**No budget exception.** The stack is a landmark by height only: every tier
is far under the ordinary ceilings and the atlas is 1024². There is no
height limit in CLAUDE.md, only triangle ceilings.

## Footprint

| | Width (X) × depth (Y) × height |
| --- | --- |
| Plinth (the outer wall outline) | 5.60 × 5.60 m, walls to 4.00 m |
| Overall | 5.60 × 5.60 × 46.50 m |

Nothing stands outside the plinth: the shaft's foot is 4.2 m across inside
the coping's 5.1 m flat top, and the head's crown, the widest part of the
stack, is about 3.0 m across (3.2 m to the corners of the 8-sided tier).

Heights: coping 4.00–4.25 m; shaft 4.25–44.25 m in ten 4 m lifts, its
outside radius falling straight from 2.10 m to 1.20 m (a batter of 2.25 %);
corbel 44.25–44.65 m; head band 44.65–45.95 m at radius 1.44 m; crown
course 45.95–46.30 m at radius 1.52 m; cap sloping to the rim at 46.50 m.

The pivot is at ground level on the plinth's centre, which is also the
shaft's axis. It is taken from `LOD0` and every tier has the same extents.

## Story height

n/a: a chimney has no occupied storey. The facts sidecar's `storeys` is
empty (see Export, *Facts sidecar*).

## Door leaf height

n/a: the stack has no pedestrian door. The two openings in the plinth are
not doors:

- **Flue inlet** (front, -Y): 1.625 × 2.00 m, sill at 1.00 m, head at
  3.00 m under a 0.25 m cast concrete lintel. It is closed by a bolted black
  steel blanking plate in an angle frame, with a small inspection door low
  in it.
- **Cleanout hatch** (east): 0.70 × 0.91 m, sill at 0.44 m, a painted cast
  iron door on two strap hinges in an iron frame.

Neither reads at human scale as a door: the inlet's sill is a metre up, and
the hatch is half a door's height. The plant's hall carries the door scale.

## Window sills

n/a: no windows. The inlet's sill is at 1.00 m and the hatch's at 0.44 m.

## Eave overhang

n/a: no roof. The head's crown projects 0.32 m beyond the shaft's top and
the coping slopes 0.25 m in from the plinth's walls.

## Construction

`build.py` builds one closed solid directly, with no boolean:

- the plinth's four walls, the inlet cut into the front at `LOD0`/`LOD1`
  (0.25 m reveals in brick, a concrete sill and lintel soffit, the closure
  at the back) and painted flush at `LOD2`/`LOD3`; the hatch a flush face in
  the east wall on every tier;
- the coping's four sloped faces and its flat top, holed by the shaft's
  foot polygon, whose vertices it shares;
- a surface of revolution: the shaft's ten lifts, the head, the rim, and
  the flue's lining straight down 1.0 m from the rim's inner edge;
- the flue's floor at 45.50 m, inside the head band, and the plinth's floor
  on the ground.

The stack's faces are shaded smooth round the circumference; edges are
sharp where the profile turns by more than 25° (the corbel steps, the
crown, the cap, the rim). The plinth is flat-shaded.

### The round

Side counts per tier: 24, 16, 12, 8. Vertices stand at r × 2 / (1 + cos(π/n)),
so the polygon's mean of apothem and corner radius is the true radius and
the shaft keeps its apparent width as sides drop (the 8-sided tier's
corners are 4 % out, its flats 4 % in). The back facet (+Y), which carries
the step irons, and the front facet (-Y), facing the inlet, are centred on
the axis on every tier.

### Hollow top

The rim is a cast concrete ring 0.28 m wide round a flue of radius 1.02 m.
The lining and floor take the soot patch; the floor is 1.0 m down, at
45.50 m, above the head band's foot. The flue stays recessed on every tier.

### Head

`LOD0`/`LOD1` corbel out in three steps of 0.08 m by 0.20 m. `LOD2`/`LOD3`
replace the steps by one flare from the shaft's top to the head band's foot;
it samples the stepped texture, so the steps stay painted.

### Authored parameters

`facade_atlas.py` holds every shared number: the plinth (`PH`, `Z_FOOT`,
`Z_PLINTH`, `WASH_IN`), the shaft (`R0`, `R1`, `SEG`, `NSEG`), the head
profile `HEAD` and its flare indices, `R_FLUE`, `FLUE_DEPTH`, the inlet,
lintel and hatch, `SIDES`, and the atlas rows. `check_layout()` asserts:

- the inlet clear of the corners and under its lintel, the lintel clear of
  the coping, the hatch low and above the footing;
- the shaft's foot inside the coping's top on every tier;
- on every tier the back facet inside the iron strip, the shaft unwrapped
  in the atlas, the head inside its region;
- the head profile starting on the shaft's top, the flue's floor above the
  head band's foot, the rim at least 0.3 m wide.

### Access and lightning protection

Painted, not modelled. Galvanised step irons run up the back (+Y) every
0.333 m from 2.5 m up the plinth's rear wall to the cap, with a grip at the
rim. The copper down conductor runs from the cap down beside the back
facet, and down the plinth's rear wall to a test clamp at 1.5 m and the
ground. `scripts/roof_safety.py`'s wall ladder assumes a vertical wall; a
modelled iron or caged ladder for 42 m of battered shaft would be about
130 rungs, under a pixel each beyond 35 m. The irons are close-range detail
(LOD review). This is CLAUDE.md's roof-safety rule only by
analogy: a chimney is not a roof.

## Per-tier triangle counts

| Tier | Sides | Triangles | Ceiling | What changes |
| --- | --- | --- | --- | --- |
| `LOD0` | 24 | 1100 | 12,000 | stepped corbel, inlet recessed |
| `LOD1` | 16 | 748 | 4,000 | the same, 16 sides |
| `LOD2` | 12 | 468 | 1,500 | corbel as one flare, inlet flush |
| `LOD3` | 8 | 324 | 500 | the same, 8 sides |

The shaft's ten lifts cost 2n triangles each (480 at `LOD0`), because the
texture repeats per lift (Texture set). The head costs 2n per profile
segment, ten at `LOD0`/`LOD1` and six after; the lining 2n and the floor
n − 2. The plinth, the inlet recess and the coping's top are 70 at `LOD0`
and 46 at `LOD3`. The counts follow from the round and the lifts; nothing is padded.

## LOD review

Intended switches are the catalog defaults: 35, 70 and 120 m. No overrides.
The review camera was perspective, 1920×1080, 50° vertical FOV, distance
along the view to the front face (`scripts/review_asset.py`), Cycles CPU, 16
samples with denoising, AgX, exposure 0. Renders are in the local,
untracked `review/power_plant_2026_11_21/savupiippu_brick_round/`.

Pairs compared, each tier against its neighbour with identical camera and
light:

- `LOD0`/`LOD1` at 30/40 m, front, oblique and rear, noon and reverse sun;
- `LOD1`/`LOD2` at 65/75 m, front, oblique and rear, noon and reverse;
- `LOD2`/`LOD3` at 115/125 m, front, oblique and 45° aerial, noon and
  reverse;
- `LOD0` against `LOD3` at 150 and 300 m, front, oblique and aerial, noon:
  the landmark range;
- all four tiers side by side at the head from 35 m (front, sun from the
  front) and 60 m (rear, raised), and at the plinth from 35 m.

Findings:

- **The round.** 24 to 16 sides is not visible at 35 m. 12 sides at 70 m
  and 8 at 120 m keep the shaft's width and read round on smooth shading;
  the 8-sided rim is visibly octagonal from the 125 m aerial. At 150 and 300 m `LOD0` and `LOD3` are
  indistinguishable.
- **The head.** The three corbel steps read as steps at 35 m; on `LOD2`
  the single flare carries them as paint, and at the 70 m switch the
  change is a pixel or two of outline. The crown, the cap's slope and the
  open flue keep their shape on every tier; the soot-dark top reads from
  300 m.
- **The inlet** goes flush at `LOD2`: its 0.25 m recess is about 3 px at
  70 m, and the black plate keeps the opening's weight.
- **Tension bands** read as dark rings to 125 m and merge into the shaft's
  tone by 300 m. The **step irons**, **conductor** and **lamps** are clear
  in the 6–15 m close renders and the 35 m head views; in the 30/40 m rear
  views, with the back in shade under the noon sun, the irons do not
  separate from the brick. They are detail for a close look, not
  silhouette.

The six working views (`review_asset.py --six-views`: orthographic front,
back, left, right, top and a 45° aerial) were looked at for `LOD0` and
`LOD3`. Close renders at 6–15 m of the head (front, back, from above) and
the plinth (front, east, rear) checked the open top, the irons, the
conductor, the inlet, the hatch and the coping.

Pending in the consumer: real LOD switching, shadows of a 46 m stack in the
consumer's shadow cascades, and performance.

## Interior geometry

The validator's hidden-surface test reports 0 hidden triangles on every
tier. The solid has no interior partition. The only closure faces are the
plinth's floor on the ground and the flue's floor, which is exterior
surface seen from above and lit by the open top.

## Known simplifications

- The flue is 1 m deep and floored; the real stack's flue runs to the
  inlet. The lining is not tapered.
- Tension bands, step irons, the down conductor and its clips, the band
  tensioners, the lamps and their brackets, the hatch and the inlet's
  closure are texture with relief in the normal map. The irons' 0.12 m
  standoff is shallowed to 30 mm of relief.
- The conductor stops at the coping's top and starts again on the plinth's
  rear wall; across the coping's flat top it is not painted.
- The corbel's steps are geometry on `LOD0`/`LOD1` and painted on the
  single flare of `LOD2`/`LOD3`.
- The inlet's soot staining and the head's soot are static.
- No flue duct, foundation slab, ground, fence or lightning finial.

## Texture set

One 1024² atlas at 64 px/m, rasterised by `scripts/atlas.py` at `atlas.SS`
= 4 and padded last by `atlas.pad()`. Rows from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–279 | PLINTH | the plinth's walls (z 0–4.0 m, V = height) and the coping's slope (V on along it); U walks the walls and wraps |
| 288–544 | MID | one 4 m lift of the shaft, tiling in V; U = chord length round the stack |
| 552–997, x 0–736 | TOPHEAD | the shaft's top lift (z 40.25–44.25 m, V = height), then the head with V along its profile, to the rim's inner edge |
| 552–784, x 744–1008 | unique | the inlet's closure, the hatch, the coping's flat top, flat patches |

### The shaft's height

The stack is 46.5 m tall and the atlas holds 16 m, so the shaft cannot have
one band whose V is height from the ground. It is cut into ten 4 m lifts:
nine sample MID, which tiles in V; the top one samples TOPHEAD, which also
holds the head. MID is painted four rows into each gutter from its own
formula, so the gutters carry its opposite end, and every noise in the
atlas repeats on its 256 rows (`atlas.noise(tile_y=4)`, and
`weathering.Weather(tile_y=4)`). Header bond at 43 courses a lift
(0.093 m), two tension bands a lift and twelve irons a lift all repeat with
it. The repeat is hidden by the tension bands and the brick's own tone
variation; no deviation from 64 px/m was needed.

### U round the stack

U is chord length at 64 px/m, so every facet of every tier shows bricks at
their true size. The back facet samples a strip of its own, 112 px wide,
centred on U 56: the step irons. The other facets run on from U 112
without wrapping. The bond is broken only at the back facet's two edges,
under the ladder, and on the plinth at its west corners (the plinth's
walls walk 22.4 m round a 16 m band; the west wall reuses the east wall's
range so that the front's range, with the inlet's lintel and soot, is its
own).

### Deviations from 64 px/m

- The coping's flat top is mapped from above at 16 px/m (seen only from
  above, and plain concrete).
- On `LOD2`/`LOD3` the corbel's flare samples the 0.64 m of stepped texture
  over its 0.47 m slope, about 88 px/m along the slope.
- The lining and both floors use flat patches.

### Relief

Brick 6 mm proud of the joint; tension bands 10 mm, their tensioners 22 mm;
step irons 30 mm; conductor 3 mm with 6 mm clips; lamps 60 mm; the inlet
plate's frame, bolts and stiffener 25–35 mm; the hatch's frame 20 mm and
panel 12 mm; the head band's sunk course −12 mm.

### Weathering

`scripts/weathering.py` at its moderate level: grime, rain wash, faded
paint on the steel; soil and algae on the footing, splash-back and salt
bloom on the plinth's brick, dirt on the coping and runs under it; rust on
the bands and irons and short rust runs under the bands; rust and runs on
the inlet's plate and the hatch's foot; dirt on the coping's top.

The module has no soot, so `facade_atlas.soot()` darkens shade and adds the
module's dirt field: thickening up the top lift from nothing, then to
heavy over the head, and heaviest on the cap and rim; a soot plume rising
from the inlet over its lintel. Rain runs hang under the corbel and down
the head band.

### Filtering

Whole-atlas mip4 stress renders (`scripts/review_atlas_mips.py`,
`review_asset.py --texture-dir`) of `LOD2` and `LOD3` at 125 m, front,
75° grazing and rear, noon and reverse sun: no leaks between the plinth,
MID and TOPHEAD, no dark seams at the lifts' rings, the cap and rim stay
dark and the coping light. The lifts' ring seams are not visible at full
resolution either. Consumer filtering is pending.

Unique textures: five 1024² RGB PNGs (three albedos, one ORM, one normal
map), 4 MiB each in memory without mips. ORM and normal are shared.

## Glazing treatment

n/a: no glazing. The obstruction lamps' lenses are painted dark red, not
glass, and `scripts/glazing.py` is not used.

## Variant list

| Variant | Meaning |
| --- | --- |
| `red_brick` (default) | red facing brick |
| `yellow_brick` | yellow (cream) brick |
| `brown_brick` | dark brown brick |

The same three bricks as the catalog's brick industrial buildings, so the
stack matches its hall. Only the brick and mortar change; concrete, steel,
soot, the hatch's paint and the lamps are the same in every variant.
Geometry, UVs, ORM and normal are shared.

## Night lighting

**None: the stack is not night-lit and ships no `_emission.png`.** It has no
glazing. Its three aviation obstruction lamps are painted unlit. A red
emission region for them would be a lamp, not glazing, and CLAUDE.md asks
for one only when a brief calls for it; this brief left it optional, and the
shared window-emission path would apply the consumer's window tint and
schedule to what must be a steady or flashing red light. Whether the lamps
should glow is pending with the owner.

- No `emissiveTexture` on any tier; the facts sidecar has no
  `textures.emission`.
- No `variants.png`; the three colours were reviewed in day renders.

`build.py` builds through the shared `asset_build.Asset` with
`night_lit=False`, which keeps the shared material, previews and
bookkeeping and leaves out the window wiring: `material()` wires no
emission mask, `export_all()` has no emission state or rewrite,
`render_variants()` renders nothing.

## Export

```
python3 facade_atlas.py export                       # albedo x3, ORM, normal
blender --background source.blend --python build.py  # meshes, preview, sidecar
```

Run the textures first. A first build from a factory scene is
`blender --background --python build.py`. Export settings, as
`asset_build`'s `export_all()` passes them: `export_format='GLB'`,
`use_selection=True`, `export_yup=True`, `export_apply=True`,
`export_keep_originals=True`, `export_cameras=False`,
`export_lights=False`; then `strip_embedded_images()`.

Bindings, the same on every tier: the default variant's albedo to
`baseColorTexture`; the ORM's G/B to `metallicRoughnessTexture` and its R to
`occlusionTexture`; the normal map to `normalTexture` at scale 1. One
material, backface culling on, single-sided and opaque. Other variants swap
the albedo file only.

The preview uses the catalog's fixed camera orientation, lens, sun and flat
grey world, the distance fitted by `asset_build.fit_camera`: `LOD0`,
`red_brick`.

### Facts sidecar

`export/savupiippu_brick_round.model.json`: the plinth's 5.6 × 5.6 m square
as the footprint, `storeys` empty, `dwellings` 0, `doors` empty, `hero`
false. The stack has no door (the cleanout hatch and the flue inlet are
not doors) and no occupied floor, so it lists neither and has no main door,
which the schema allows; the shared `write_facts()` writes it.

## Review status

Checked here, in Blender:

- `scripts/validate_asset.py`: 0 FAIL. Every tier welded manifold, one
  material, uri-only images, normal map at scale 1, under its ceiling,
  pivot at ground and centred, 0 hidden triangles; five 1024² RGB PNGs;
  the facts sidecar.
  The sidecar's `source.dirty` is true (written from an uncommitted tree);
  it must be rewritten from a committed one (`build.py -- facts`).
- `check_layout()` and the atlas's `check_regions()` and `check_bands()`.
- The six working views at `LOD0` and `LOD3`; close renders of the head and
  the plinth.
- LOD pairs around 35, 70 and 120 m, and `LOD0`/`LOD3` at 150 and 300 m.
- Whole-atlas mip4 stress renders at 125 m.
- The three variants from the catalog camera.

Pending:

- whether the obstruction lamps should glow (Night lighting);
- in the consumer: import, orientation and pivot on reimport, LOD
  switching, shadows, filtering of the tiling MID band, performance.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`) throughout.
The MCP addon was not used. Texture generation used the system Python 3
with numpy, scipy and Pillow.
