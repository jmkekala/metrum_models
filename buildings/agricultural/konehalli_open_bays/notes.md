# konehalli_open_bays

## Style brief

A composite Finnish *konehalli* (*konesuoja*), the machine shed of a small
post-war grain farm, from the same countryside as the rintamamiestalo houses.
It is a plain, low, long shed for a tractor, a combine header and implements.
It has three bays under a mono-pitch roof that falls from the yard side to
the rear. Two bays are open to the yard for the full depth of the shed, with
a white post between them and a white header over them. The third is a
closed workshop and store, with a pair of framed board doors on the front
and a pedestrian door in its end wall.

Materials: red-ochre (*punamulta*) vertical board-and-batten on a low concrete
footing strip, white corner boards, white door casings and white framed and
braced doors. The roof is dark profiled sheet steel. Inside the open bays the
boards are bare and unpainted, crossed by two girts, under the roof's
rafters, purlins and bare sheet. Those surfaces are darker, and their
occlusion is painted.

It is meant as yard filler on farmsteads. Colour variety comes from the
variants. It has no gutters, chimney, roof plant, fences, ground or slab.

## Category and secondary use

`buildings/agricultural/`. Its secondary use is the closed bay's workshop and
store, which is part of the same farm-machinery function.

## Hero/landmark status

**No.** Ordinary budgets, a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Outer walls and front post line | 10.50 × 6.00 m |
| Overall, with 0.40 m front and rake overhangs and 0.20 m at the rear | 11.30 × 6.60 m |

Bays, west to east: two open bays, 3.20 m clear each, split by one 0.20 m
post at x −1.75. The closed bay is 3.70 m outside, from x 1.55 to 5.25. Its
extra 0.20 m over the brief's 3.5 m lets the 3.25 m door pair with its
casing sit 0.10 m clear of both corner boards. The open bays run 5.80 m
deep, from the front post line to the back wall's inner face. The back wall
and the open end wall are each one board wall, 0.20 m thick.

Heights: the roof's underside meets the front wall line at 4.00 m and the
rear wall at 3.00 m. The front fascia's bottom edge is 4.07 m and its top
4.32 m, the highest point. The header's underside is at 3.70 m.

The pivot is at ground level, centred on the plan's bounding box (overhangs
included). That puts it 0.10 m in front of the walls' centre. It is taken from
`LOD0` and applied to every tier, and every tier has the same extents.

## Story height

**One storey, 3.00–4.00 m.** The floor is the ground. The clear height under
the roof falls from 4.00 m at the front wall to 3.00 m at the rear, and the
open bays' opening is 3.70 m under the header. That is above the
3.0–3.3 m storey because this is a single tall farm-machinery storey, not a
habitable floor: a tractor with a cab and a combine header need about 3.5 m
at the door.

## Door leaf height

- **Pedestrian door (main entrance): leaf 0.90 × 2.10 m**, with no transom.
  The casing adds 0.19 m above it. The threshold is at ground level.
- **Vehicle door pair: 3.00 × 3.20 m clear**, two 1.50 m leaves. This is a
  vehicle door, not a door leaf at human scale, so the 2.0–2.4 m band does
  not apply. The 2.10 m pedestrian door beside it in the end wall carries
  the scale. The pair's frames and braces are painted at full size: a
  0.10 m frame, a mid rail at 1.54 m and one diagonal brace per panel,
  rising away from the hinges.
- The open bays have no door leaf.

## Window sills

n/a: the shed has no windows. The tallest painted features are the door
pair's head casing at 3.39 m and the header's soffit at 3.70 m. Both sit
under the 4.00 m front eave, and `check_layout()` keeps each door's head at
least 0.15 m under the roof.

## Eave overhang

**0.40 m at the front eave and both rakes, 0.20 m at the rear eave**, which is
the low edge. The rear is short because the roof falls toward it and a
lean-to shed's back is often close to a field edge or another building. The
slab is 0.25 m thick vertically. Its edge is a white fascia under a steel
flashing in the roof colour. The underside is bare sheet over rafters and
purlins (Texture set), not a boxed soffit.

## Construction

`build.py` builds up to four closed solids and unions them with Blender's
Exact boolean (`asset_build.union`): the wall ring, the roof slab, the post
and the header.

### Open bays as a notch in the wall ring

The wall ring is not a rectangle. It is the closed bay plus the back wall and
the open end wall, one board wall thick. Its plan outline runs from the front
of the end wall, round the open bays' side wall, back wall and partition, and
then round the closed bay and the outer walls. The faces of that notch are
the open bays' two side walls and back wall. They are ordinary outer surface
of the one closed shell, like the loading bay in
`commercial/lahikauppa_corner`. The roof slab passes over the notch, and its
underside there is the bays' ceiling.

The bays have no floor face. The ground is their floor, so the shell's bottom
is the ring's own floor cap and the post's foot. Both doors stand on the
ground too. Their recesses are built with `floor=False`, so the ring's rim
detours round them and the floor cap closes them. No coplanar floor is left
anywhere.

The front of the open end wall (0.20 m) and the first 0.15 m of each bay
side wall are painted as white posts. With the free post and the header,
that frames each bay in white.

### Roof

The roof is a mono-pitch at 1:6 (9.5°), one closed slab 0.25 m thick
vertically. The wall ring's lid runs 0.12 m up into it everywhere, so the
union trims every wall exactly at the underside. The slab's underside is
three strips across x, the two rake soffits and the middle. Their
breakpoints sit 0.05 m inside the end walls' outer faces. The first build
put them in the wall planes, and the exact boolean then left a sliver
triangle of wall inside the slab at each end. The front and rear edges carry
the breakpoints, so the slab is closed with no T-junctions.

### Post and header

The post is 0.20 m square, from the ground up into the slab, centred in the
6.60 m open span. Its front is flush with the walls' front faces.

The header is 0.20 m deep and runs from 3.70 m up into the slab. It sits
0.05 m behind the post's face, and its ends run 0.10 m into the end wall and
into the closed bay. No face of it is coplanar with a wall's.

### Authored parameters

`facade_atlas.py` holds the numbers both scripts use: `HX`/`HY`, `Z_FOOT`
0.1875, `Z_EAVE_F` 4.00, `Z_EAVE_R` 3.00, the overhangs, `ROOF_T`,
`WALL_INTO`, the openings and the bay depth. `build.py` adds the plan
breakpoints (`X_PART`, `T_WALL`, post and header boxes).

`check_layout()` asserts the following:

- doors stand on the ground, clear of the corner boards and under the roof;
- the massing fits the S1 band, the side region and the back-wall band;
- the roof slope matches the atlas;
- the lid, post and header end inside the slab, and the header's ends are
  buried;
- the post is centred, and the end wall's face matches the post strip.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 234 | 12,000 | full-depth open bays, post, header; both doors with a casing ring and a 0.15/0.12 m recess |
| `LOD1` | 218 | 4,000 | each door one recess the size of its casing |
| `LOD2` | 158 | 1,500 | doors flush painted rectangles; coplanar boolean subdivisions dissolved (UV and material seams kept) |
| `LOD3` | 134 | 500 | header dropped; bays, post and corner-board paint kept |

**`LOD0` is under the brief's 400–1200 estimate, and it is not padded.** The
shed is three boxes' worth of plane, one roof slab and two doors. The walls
are polygons, not grids, and everything shallow (battens, frames, braces,
hinges, girts, rafters, ribs) is texture. The open bays cost about 40
triangles at `LOD0`: three inner walls cut by the slab, and the ceiling
face. The post and header cost about 30. Modelled trim (slab overhangs,
post, header) is a few dozen triangles, far under the quarter-budget cap.

## LOD review

Intended switches are the catalog defaults: 35, 70 and 120 m. No overrides.

The review camera was perspective, 1920×1080, 50° vertical FOV, with
distance measured along the view to the front or rear bounding face
(`scripts/review_asset.py`). Rendering was Cycles CPU, 16–24 samples with
denoising, AgX, exposure 0. Pairs compared:

- `LOD0`/`LOD1` at 30/40 m, front and oblique, noon and reverse sun;
- `LOD1`/`LOD2` at 65/75 m, front, oblique and rear, noon;
- `LOD2`/`LOD3` at 115/125 m, front and oblique, noon and reverse.

Every working render is in the local, untracked
`review/farm_2026_11_20/konehalli_open_bays/`.

- **The open bays keep their full depth on every tier.** The brief allowed
  shallower bays at `LOD2` and painted rectangles at `LOD3`. Neither was
  needed: the bays cost about 40 triangles, and a painted rectangle would
  have needed a bay-front region the atlas has no room for. They read as deep
  black shade with the white post in front, from 30 m to 125 m and under both
  sun directions.
- **Door recesses** go from a ring (`LOD0`) to one recess (`LOD1`) to flush
  (`LOD2`). Their 0.15 m reveal is about 2 px at 70 m. Blinking the 65/75 m
  frames shows the door pair's shadow line going, not the door.
- **The header goes at `LOD3`.** Its 0.29 m face is under three pixels at
  120 m, and the fascia's own white line carries the top of the opening.
  Side by side at 115/125 m the opening's top moves up by about two pixels.
  It does not show at a glance.
- **The post stays on every tier.** It is the high-contrast feature that
  says "two bays", and it costs about 12 triangles.

Corner boards, posts and door casings keep their white on every tier, since
they are flush UV strips or regions, not geometry.

The six working views (`build.py:render_views`, orthographic front, rear,
east, west, top and a 45° front-right aerial) were looked at for `LOD0` and
`LOD3`. In the front elevation the first ceiling read like a glazed transom:
the underside slopes down to the back, so the front sees it face-on through
the opening. Rib, purlin and rafter contrast were cut, the ceiling darkened
faster with depth, and the sheet made nearly dielectric (Texture set).

In the 70 m rear view under noon sun the dark roof shows a broad grey sheen.
The camera sits near the sun's mirror direction off the rear-tilted slope,
so this is specular light, not albedo. The roof's metallic went from 0.30
to 0.10 anyway, because painted steel is dielectric to the light. The sheen
remains in that one view; it is not measured, only compared by eye.

Pending in the consumer: real LOD switching, its shadows and ambient
occlusion inside the bays, and performance.

## Interior geometry

The validator's hidden-surface test reports **0 hidden triangles on every
tier.** Two fixes got it there:

- The soffit breakpoints moved inside the end walls (Construction).
- `build_lod()` now triangulates every tier itself, by the beauty method,
  and raises on any zero-area triangle.

The candidates before those fixes were all zero-area triangles, never
buried surface. The end walls' top edges run along the slab's underside and
carry several of its vertices in a straight line. Left as n-gons, the
exporter's triangulation joined three such collinear vertices into
triangles with no area. They are unseen in renders but have no real normal.
The triangle counts did not change. The open bays' walls, ceiling and back wall are exterior
surface, reachable from the front, and the test agrees. The closed bay is
solid: no interior is modelled, and its lid and the slab's underside over it
are removed by the union. The only closure faces kept are the floor caps on
the ground under the walls and the post.

## Known simplifications

- The open bays are empty. They have no floor slab, machinery, shelving or
  lighting, and the ground is their floor.
- Board-and-batten, door frames, braces, strap hinges and the drop bar are
  textured. So are girts, rafters, purlins and the sheet's ribs. The roof's
  trapezoid ribs are normal-map relief on a flat slab.
- The closed bay's floor is the ground, at the door thresholds. The footing
  strip is painted on the walls' foot, and the doorways cut it.
- The rear eave has no gutter and no downpipes (brief). No roof safety kit:
  nothing on the roof is serviced, so CLAUDE.md asks for none.
- The rake soffits use one flat patch. The front and rear soffits sample the
  ceiling band, so rafter ends show under the front eave.

## Texture set

One 1024² trim-sheet atlas, rasterised by `scripts/atlas.py` at the default
supersampling (`atlas.SS` = 4), padded last by `atlas.pad()`. Layout, in rows
from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–272 | S1, outer walls | U along the wall, V = height, 64 px/m; footing, then board-and-batten |
| 274–374 | ROOF | U = x at 64 px/m; V up the slope from the low edge, 96 rows over 6.69 m (14.3 px/m) |
| 376–396 | FASCIA | U along the edge, V = height over the underside, 64 px/m |
| 398–498 | CEIL, the underside | U = x at 64 px/m; V = plan depth from the front edge, 96 rows over 6.60 m (14.5 px/m) |
| 500–712 | INT, the bays' back wall | U along the wall, V = height, 64 px/m |
| 716–985 | unique | bay side walls (5.80 × 4.20 m, one region for both, U = depth); door pair; pedestrian door; post strip; corner strip; flat patches (header, soffit, reveal, blank) |

The ROOF and CEIL bands are stretched in V. Only the ribs, rafters and
purlins vary there, and they are low-contrast. This is a recorded deviation
from 64 px/m. Everything else is at 64 px/m.

### Relief and the normal map

Relief heights for the normal map:

- battens 20 mm, over a 0.20 m pitch (12.8 px, 80 to the atlas width, so
  the bands wrap);
- casings, corner boards and post arrises 20 mm;
- door frames and braces 20 mm, hinges 26 mm, the drop bar 32 mm;
- trapezoid sheet ribs 30 mm;
- girts and rafters 40 mm.

The girts and rafters are kept shallower than their real 50–150 mm. They
are shaded surfaces seen in shade, and full depth only steepened their
edges.

Battens and ribs read raised, not dented, under a 15° morning sun in the
9 m close renders.

### Occlusion in the open bays

The back wall's shade is 0.64 and its AO 0.42, evenly. The side walls fall
from open (1.0) to those values with depth. The ceiling falls sooner and
further (shade 0.52, AO 0.35), then lifts again under the rear overhang. The
inner board colour is fixed across variants: the inside of a painted shed
is bare.

### Weathering

`scripts/weathering.py`'s moderate level:

- grime and fade on painted wood, rain wash down the boards;
- the footing as a plinth, splash on the boards' foot, posts, corner boards
  and door feet;
- the roof's dirtier low edge and chalked high edge, runs down the fascia;
- settled dust inside the bays, thickest at the floor.

### Filtering

Whole-atlas mip4 stress renders (`scripts/review_atlas_mips.py`) of `LOD2`
and `LOD3` were checked at 125 m: front, 75° grazing and rear, under noon.
They showed no roof/trim colour leaks and no dark seams. The posts and
corner boards stay white, and the bays stay black.

Unique textures: five 1024² RGB PNGs, about 20 MB uncompressed, 4 MiB each
in memory without mips. They are three albedos, one ORM and one normal map;
ORM and normal are shared by every variant.

## Glazing treatment

n/a: the shed has no glazing. No glass id is painted, `scripts/glazing.py`
is not used, and the validator's glazing measurement does not run, because
there is no emission mask to select glass with.

## Variant list

| Variant | Meaning |
| --- | --- |
| `red_ochre` (default) | red-ochre boards and doors, white trim, near-black grey roof |
| `grey_weathered` | unpainted boards gone silver-grey, faded off-white trim, dark grey roof |
| `yellow_ochre` | yellow-ochre boards and doors, white trim, dark red-brown roof |

The three variants are a low-rise farm building's ordinary colour range (3 of
the 3–6 band). Geometry, UVs, ORM and normal are shared. The bays' bare
interior, the footing and the hardware are the same in every variant.

## Night lighting

**None. The shed is not night-lit, and it ships no `_emission.png`.** It has
no glazing, and CLAUDE.md's Output Contract allows a windowless shed to ship
no emission map. No lit signs or lamps were asked for. Consequences:

- **No `emissiveTexture` on any tier.** The validator's emission checks do
  not apply. The facts sidecar omits `textures.emission`.
- **No `variants.png`.** CLAUDE.md asks for it only of night-lit buildings.
  The three colours were reviewed in day renders from the catalog camera,
  kept in the local review folder.

The shared `scripts/asset_build.Asset` always wires the window mask. Its
`material()` loads the emission PNG, its `export_all()` reads the material's
"Window emission tint" node and rewrites the glTF emission factor (and fails
when no `emissiveTexture` exists), and its `render_variants()` renders a
night row.

`build.py`'s `UnlitAsset` subclass keeps everything else shared and leaves
out only those three things:

- `material()` runs the shared material with `attach()` disabled;
- `export_all()` is the shared export without the emission state and
  rewrite;
- `render_preview()` has no emission state to set;
- `render_variants()` renders nothing.

This should become an option in `scripts/asset_build.py` once a second unlit
asset needs it.

## Export

```
python3 facade_atlas.py export                      # albedo x3, ORM, normal
blender --background source.blend --python build.py  # meshes, preview, sidecar
```

Run the textures first: the UVs index into the atlas, and the preview reads
it. A first build from a factory scene is
`blender --background --python build.py`, which creates `source.blend`.
`facade_atlas.py` is the single source of the numbers both scripts share.

Export settings, as `UnlitAsset.export_all()` passes them (the same flags as
`asset_build`):

- `export_format='GLB'`, `use_selection=True`, `export_yup=True`;
- `export_apply=True`, `export_keep_originals=True`;
- `export_cameras=False`, `export_lights=False`.

`scripts/glb_images.py`'s `strip_embedded_images()` then removes the
placeholder `bufferView` beside each image `uri`.

Bindings, traced per tier: the validator confirms one material, uri-only
external images, and `normalTexture` at scale 1 on UV0 for every tier. The
shared `asset_build` material binds the following, the same for all four
tiers:

- the default variant's albedo to `baseColorTexture`;
- the ORM's G/B to `metallicRoughnessTexture`;
- the ORM's R to `occlusionTexture`.

The material has backface culling on and exports single-sided and opaque.
The other variants swap the albedo file only.

The preview uses the catalog's fixed camera orientation, lens, sun and flat
grey world. Only the distance is fitted, by `asset_build.fit_camera`. It
shows `LOD0`, `red_ochre`.

The facts sidecar (`export/konehalli_open_bays.model.json`) states the
following:

- **footprint:** the 10.5 × 6.0 m rectangle of the outer walls, closed along
  the front by the post line;
- **storeys:** one storey, floor at ground, 56.76 m². That is the open bays'
  clear floor (6.60 × 5.80 m) plus the closed bay inside 0.20 m walls
  (3.30 × 5.60 m), with the post not deducted;
- **dwellings:** none;
- **doors:** two, the pedestrian door (`entrance`, main) and the pair
  (`vehicle`).

The open bays are not doors.

## Review status

Checked here, in Blender:

- `scripts/validate_asset.py`: 0 FAIL. The one WARN is `source.dirty` (the
  sidecar was written from an uncommitted tree). Every tier passes:
  - welded manifold topology, one material, uri-only images;
  - the normal map at scale 1, triangle ceilings;
  - pivot at ground and centred;
  - 0 hidden triangles.

  Five 1024² RGB PNGs; the facts sidecar is consistent.
- `check_layout()`.
- The six working views at `LOD0` and `LOD3`.
- LOD pairs around 35, 70 and 120 m from front, oblique and rear, under two
  sun directions.
- A four-state day cycle (morning, noon, dusk, night).
- 9 m close renders of the battens, ribs and door frames under low and high
  sun.
- Whole-atlas mip4 stress renders at 125 m.
- The three variants from the catalog camera.

Pending in the consumer:

- import, orientation and pivot on reimport in the engine;
- LOD switching and shadows inside the bays;
- mip and anisotropic filtering of the stretched ROOF and CEIL bands;
- performance.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`) throughout.
The MCP addon was not used. Texture generation used the system Python 3
with numpy, scipy and Pillow.
