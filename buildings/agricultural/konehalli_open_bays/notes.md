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
variants. The roof sheds to the rear, so the rear (low) eave carries a
galvanised half-round gutter, with a downpipe at each end of the rear wall
and a snow guard (*lumieste*) on the roof just above the eave, all three in
the same galvanised steel as the gutters of the farm's barn and grain dryer.
It has no chimney, roof plant, fences, ground or slab; only the workshop
door's reveal stands on a small concrete entrance slab (Construction).

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

The downpipes stand inside the rear eave's 0.20 m (Construction), so they
change neither figure.

The pivot is at ground level, centred on the plan's bounding box (overhangs
included). That puts it 0.10 m in front of the walls' centre. It is taken from
`LOD0` and applied to every tier, and every tier has the same extents.

## Story height

**One storey, 3.00–4.00 m.** The floor is the ground; the workshop door's
0.02 m floor slab (Construction) is a floor finish in its reveal, not a
step. The clear height under
the roof falls from 4.00 m at the front wall to 3.00 m at the rear, and the
open bays' opening is 3.70 m under the header. That is above the
3.0–3.3 m storey because this is a single tall farm-machinery storey, not a
habitable floor: a tractor with a cab and a combine header need about 3.5 m
at the door.

## Door leaf height

- **Pedestrian door (main entrance): leaf 0.90 × 2.10 m**, with no transom.
  The casing adds 0.19 m above it. The threshold is at ground level; its
  reveal stands on a 0.02 m concrete floor slab (Construction), which leaves
  the leaf's 2.10 m as built.
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
slab is 0.25 m thick vertically. At the front and rakes its edge is a white
fascia under a steel flashing in the roof colour. At the rear, where the
water leaves the roof, a half-round galvanised gutter hangs across the
fascia's top under the sheet's drip edge, painted with its relief (Texture
set). The underside is bare sheet over rafters and purlins (Texture set),
not a boxed soffit.

## Construction

`build.py` builds up to six closed solids and unions them with Blender's
Exact boolean (`asset_build.union`): the wall ring, the roof slab, the post,
the header and the two downpipes.

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
ground too. The vehicle pair's recess is built with `floor=False`, so the
ring's rim detours round it and the floor cap closes it; the workshop door's
reveal stands on a concrete floor slab (Entrance floor slab below). No
coplanar floor is left anywhere.

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

The slab's top is one face on the ROOF region, the snow guard painted on it
(Texture set); its underside's middle strip samples the CEIL region.

### Rainwater goods and snow guard

- **Gutter:** painted, on the rear fascia only (Texture set). The front eave
  and the rakes have none: a mono-pitch roof sheds its water off the low
  edge.
- **Downpipes:** modelled with `scripts/downpipes.py`, one at each end of the
  rear wall, 0.25 m (`DP.CORNER`) in from its corners at s 0.25 and 10.25 m.
  The rear wall is blank and the gutter runs the slab's full 11.30 m, so a
  pipe at each end halves the run each drains, keeps the rear symmetrical,
  and puts a pipe at the rear corner of both end walls' oblique views. They
  stand `DP.GAP` 0.03 m off the boards on their axis 0.08 m out, sample the
  gutter's middle rows (`PIPE_STRIP`), and run up 0.10 m into the slab.
- **No swan-neck.** The module's swan-neck would leave the soffit at
  `DP.outlet(0.20)` = 0.11 m and come back to the pipe's axis at 0.08 m: a
  0.03 m jog, under two pixels at 20 m, for 32 more triangles a pipe at
  `LOD0`. The pipes run straight up into the soffit instead, the module's
  own course under a shallow overhang (`outlet` None).
- **Shortened shoe.** The module's shoe kicks out 0.15 m, which would put
  its mouth 0.27 m off the wall, past the 0.20 m eave. `LOD0`/`LOD1` (bent)
  would then be deeper than `LOD2`/`LOD3` (straight), which
  `asset_build.build_all()` refuses, and the pivot would move. `build.py`'s
  `ShedPipe` subclass kicks it 0.075 m instead, so the mouth reaches 0.19 m:
  every tier keeps the 11.30 × 6.60 × 4.32 m bounds and the pivot.
- **Snow guard:** painted on the roof, two round tubes on brackets every
  1.0 m, their foot 0.20 m up the slope from the edge, over the rear wall's
  line. No geometry, as in `rintamamiestalo_porch`, which paints its own.

### Post and header

The post is 0.20 m square, from the ground up into the slab, centred in the
6.60 m open span. Its front is flush with the walls' front faces.

The header is 0.20 m deep and runs from 3.70 m up into the slab. It sits
0.05 m behind the post's face, and its ends run 0.10 m into the end wall and
into the closed bay. No face of it is coplanar with a wall's.

### Entrance floor slab

The workshop door (sidecar `workshop`, the main entrance) stands on the
ground in a 0.12 m reveal that had no upward face under it (the ring's floor
cap faces down), so a consumer's terrain showed inside, at the foot of the
leaf. The reveal is floored with a concrete slab from the shared
`scripts/door_floor.py` (`build_item()` calls `door_floor.recess()`; at
`LOD1` the wall's outline takes `door_floor.notch()`):

| Entrance | Sidecar door | Slab, width x depth | Tiers |
| --- | --- | --- | --- |
| the workshop door, east end wall | `workshop` | 0.90 x 0.12 m inside the casing ring | `LOD0` |
| | | 1.15 x 0.12 m, the casing's recess | `LOD1` |

- **Top 0.02 m over the ground** (`door_floor.T`), clear of terrain at
  z = 0 and too low to read as a step.
- **A nosing on the wall plane** between the jambs. Nothing projects past
  the wall, so the bounds, the pivot, the footprint and the door's threshold
  in the sidecar are as they were.
- **The reveal starts on the slab's top:** the cheeks and the leaf begin at
  z 0.02. At `LOD1` the wall's notch carries the nosing's two top corners;
  at `LOD0` the flush casing ring's jambs carry them, and the slab samples
  its region from the casing's left side (`u0`), so both tiers share one
  region. Wall (or ring), nosing, slab and cheeks meet on shared vertices,
  and under the nosing the floor cap runs straight along the wall line
  instead of round the reveal. The door's artwork keeps its place, so the
  slab covers the bottom 1.3 px of the leaf.
- **Its own atlas region** (Texture set).

`floored()` gives the door its slab on every tier that recesses it
(`item_mode()` ring or cut): `LOD0` and `LOD1`. `LOD2` and `LOD3` paint it
flat on the wall with no reveal, so they are unchanged. The vehicle pair's
0.15 m reveal on the front keeps standing on the ground with no floor, and
the open bays, which are not doors, keep the consumer's terrain as their
floor by design (Known simplifications).

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
- the post is centred, and the end wall's face matches the post strip;
- the downpipes clear the rear wall's corners (`downpipes.problems()`), their
  tops end inside the slab and their shoes stay under the rear eave;
- the snow guard lies on the roof, the slab's length matches the roof and
  ceiling regions, and the regions clear each other, S1, INT and the fascia
  bands;
- `door_floor.problems()` finds the workshop door's floor slab region not
  the casing's width and the reveal's depth, or the door off the ground; and
  `atlas.region_problems()` finds the slab's region overlapping another
  unique region, the INT band or the rear fascia band.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 336 | 12,000 | full-depth open bays, post, header; both doors with a casing ring and a 0.15/0.12 m recess, the workshop door's on its floor slab; two eight-sided downpipes with shoes |
| `LOD1` | 272 | 4,000 | each door one recess the size of its casing, the workshop door's on its floor slab; downpipes four-sided, shoes kept |
| `LOD2` | 192 | 1,500 | doors flush painted rectangles; coplanar boolean subdivisions dissolved (UV and material seams kept); downpipes straight and four-sided |
| `LOD3` | 186 | 500 | as `LOD2`, the header kept; downpipes three-sided |

**`LOD0` is under the brief's 400–1200 estimate, and it is not padded.** The
shed is three boxes' worth of plane, one roof slab and two doors. The walls
are polygons, not grids, and everything shallow (battens, frames, braces,
hinges, girts, rafters, ribs) is texture. The open bays cost about 40
triangles at `LOD0`: three inner walls cut by the slab, and the ceiling
face. The post and header cost about 30. The two downpipes cost about 98
triangles at `LOD0`, 50 at `LOD1`, 34 at `LOD2` and 28 at `LOD3`, with the
holes they leave in the rear soffit. The header costs 24 at `LOD3`, which
keeps it (LOD review). Modelled trim (slab overhangs, post, header, downpipes) is about
150 triangles at `LOD0`, far under the quarter-budget cap. The workshop
door's floor slab costs 4 triangles, the nosing and the top, on `LOD0` and
`LOD1` (332 / 268 before it); the east wall and the floor cap
re-triangulate round its corners with no net change. `LOD2` and `LOD3`
are byte-identical to the tiers before it.

## LOD review

### The consumer's switches

The consumer switches by screen size: adjacent tiers are judged at 1.8, 4 and
8 times the largest bounds dimension (11.30 m), so **20, 45 and 90 m**, with
its camera, 75° vertical FOV at 1920×1080, distance from the camera to the
centre of `LOD0`'s bounds. Rendered on reimported GLBs (Cycles 24 samples,
AgX, the `review_asset.py` scene with the lens swapped): front, corner (45°
round, 25° up), eye level and rear at noon, each pair side by side with its
difference, before and after the 2026-11-22 fixes with identical settings
(`review/older_audit_2026_11_22/fix_agricultural/konehalli_open_bays/sheets/`,
local, git-ignored).

- **20 m, `LOD0`/`LOD1`:** the doors' casing ring against one casing-sized
  recess; a thin shadow change round the door pair's casing, no pop.
- **45 m, `LOD1`/`LOD2`:** the door recesses go flush, CLAUDE.md's flat
  openings from `LOD2`; the doors' shadow line goes, the doors stay.
- **90 m, `LOD2`/`LOD3`:** `LOD3` used to drop the header, and the white
  line over the open bays vanished at this switch (mean difference 0.60 /
  255 from the front). `LOD3` now keeps it, for 24 triangles, and the two
  tiers are identical in every view (0.00).

### Authoring review

Intended switches are the catalog defaults: 35, 70 and 120 m. No overrides.

The review camera was perspective, 1920×1080, 50° vertical FOV, with
distance measured along the view to the front or rear bounding face
(`scripts/review_asset.py`). Rendering was Cycles CPU, 16–24 samples with
denoising, AgX, exposure 0. Pairs compared:

- `LOD0`/`LOD1` at 30/40 m, front and oblique, noon and reverse sun;
- `LOD1`/`LOD2` at 65/75 m, front, oblique and rear, noon;
- `LOD2`/`LOD3` at 115/125 m, front and oblique, noon and reverse.

Every working render is in the local, untracked
`review/farm_2026_11_20/konehalli_open_bays/`. The rainwater goods and snow
guard were reviewed as a before/after pair with identical settings
(`review_asset.py`, `review_compare.py`) in
`review/farm_gutters_2026_11_20/konehalli_open_bays/`: `LOD0`/`LOD1` at 20
and 40 m from the oblique, front and rear views, and `LOD2`/`LOD3` at 70 and
120 m from the oblique and rear, under noon and reverse sun, with 9 m close
renders of the rear.

- **The open bays keep their full depth on every tier.** The brief allowed
  shallower bays at `LOD2` and painted rectangles at `LOD3`. Neither was
  needed: the bays cost about 40 triangles, and a painted rectangle would
  have needed a bay-front region the atlas has no room for. They read as deep
  black shade with the white post in front, from 30 m to 125 m and under both
  sun directions.
- **Door recesses** go from a ring (`LOD0`) to one recess (`LOD1`) to flush
  (`LOD2`). Their 0.15 m reveal is about 2 px at 70 m. Blinking the 65/75 m
  frames shows the door pair's shadow line going, not the door.
- **The header stays on every tier.** It frames the open bays in white;
  dropped at `LOD3`, its line vanished at the consumer's 90 m switch.
- **The post stays on every tier.** It is the high-contrast feature that
  says "two bays", and it costs about 12 triangles.
- **The downpipes stay on every tier**, in `downpipes.MODES`: eight sides
  with the shoe at `LOD0`, four with the shoe at `LOD1`, four and straight
  at `LOD2`, three and straight at `LOD3`. No tier drops them. They read as
  two stood-off pipes at the rear corners at 20 and 40 m from the rear,
  with their shadow on the boards under a rear sun. At 70 and 120 m they
  are a one- or two-pixel line beside the corner boards.
- **The gutter and the snow guard are texture**, on every tier alike.
  The gutter reads as a raised, rounded grey band with a shadow line on the
  white board under it, and the guard as two light tubes on brackets, from
  9 to 40 m under a rear sun. Under the noon sun the rear is in shade and
  the gutter reads as a darker band under the roof's edge. At 70 m and
  beyond the eave reads as one grey line.

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
to 0.10, and on 2026-11-22 to 0, because painted steel is dielectric. The
sheen remains in that one view; it is not measured, only compared by eye.

**The workshop door's floor slab (2026-11-23)** adds no transition of its
own. It goes with the door's 0.12 m reveal at the `LOD1`/`LOD2` switch,
where the door is already painted flat: a 0.02 m nosing and 0.12 m of slab
are under a pixel at 70 m and at the consumer's 45 m. Checked from a
standing eye (1.7 m, 75 degree vertical FOV, 1280 x 720), from 0.35 m over
a terrain plane at z = 0 and from above, 1-5 m from the door, noon and
reversed sun, every tier (Review status).

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
the ground under the walls and the post. Under the workshop door's floor
slab (`LOD0`, `LOD1`) the ring's cap runs straight along the wall line, so
no face lies at grade inside the reveal; the slab is exterior surface and
adds no face inside the shell. The downpipes' tops are buried in
the slab and removed by the union like the walls' lid.

## Known simplifications

- The open bays are empty. They have no floor slab, machinery, shelving or
  lighting, and the ground is their floor: the consumer's terrain stands
  under them by design, between the end wall, the post and the partition,
  back to the back wall. They are not doors.
- Board-and-batten, door frames, braces, strap hinges and the drop bar are
  textured. So are girts, rafters, purlins and the sheet's ribs. The roof's
  trapezoid ribs are normal-map relief on a flat slab.
- The closed bay's floor is the ground, at the door thresholds. The footing
  strip is painted on the walls' foot, and the doorways cut it.
- **Floors:** only the workshop door's reveal has one, a flat concrete slab
  with no mat or threshold strip (Construction). The vehicle pair's 0.15 m
  reveal stands on the consumer's ground, as before.
- The gutter is painted on the rear fascia, with its relief in the normal
  map; its ends are not modelled and stop at the slab's corners. Its
  outlets are not modelled: the downpipes run up into the soffit 0.07 m
  behind the fascia it is painted on.
- The downpipes have no swan-neck, and their shoes kick out 0.075 m rather
  than the module's 0.15 m, so they stay under the 0.20 m rear eave
  (Construction).
- The snow guard is painted on the roof's region, tubes and brackets
  alike, with no geometry.
- No roof safety kit: nothing on the roof is serviced, so CLAUDE.md asks for
  none.
- The rake soffits use one flat patch. The front and rear soffits sample the
  ceiling region, so rafter ends show under the front eave.

## Texture set

One 1024² trim-sheet atlas, rasterised by `scripts/atlas.py` at the default
supersampling (`atlas.SS` = 4), padded last by `atlas.pad()`. Layout, in rows
from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–272 | S1, outer walls | U along the wall, V = height, 64 px/m; footing, then board-and-batten |
| 274–499, x 2–379 | ROOF | the roof's top, 11.30 × 6.69 m at 33 px/m both ways: U = plan x from the rake edge, V up the slope from the low edge; the snow guard near its foot |
| 274–496, x 382–759 | CEIL, the underside | 11.30 × 6.60 m at 33 px/m both ways: U = plan x, V = plan depth from the front edge |
| 500–712 | INT, the bays' back wall | U along the wall, V = height, 64 px/m |
| 716–984 | unique | bay side walls (5.80 × 4.15 m, one region for both, U = depth); door pair; pedestrian door; post strip; corner strip; flat patches (header, soffit, reveal, blank); the workshop door's floor slab |
| 984–1004 | FASC_R, the rear eave | the rear fascia, V = height over the underside, 64 px/m, with the gutter across its top; its top row is the roof's edge |
| 1004–1024 | FASCIA | the front and rake edges, V = height over the underside, 64 px/m |

**Texel density** is 64 px/m but on the roof and the ceiling, the two largest
surfaces, seen from raised views and through the open front: both are 33
px/m both ways (isotropic). Until 2026-11-22 they were full-width bands at
64 px/m along x and 14.3 / 14.5 px/m in V (anisotropy 4.46). At 64 px/m the
two would need about 850 rows; 33 px/m is the most at which they fit side
by side between S1 and INT, with the fascia bands moved to the atlas's top
rows and the unique regions trimmed to the 4.15 m the walls reach. A
recorded deviation from 64 px/m. Every height in the two regions is scaled
by 33/64, so the slopes the normal map derives stay physical.

### Rear eave and snow guard

The gutter and the snow guard are only on the rear eave.

- **Gutter:** half-round, 9 rows (0.14 m) under the rear fascia's top row,
  which is the sheet's drip edge, as in `rintamamiestalo_porch`. Its roll is
  height, a 70 mm radius, with a darker belly and three rows of shadow on
  the board below. Hangers every 1.0 m. The downpipes' sides sample its
  middle five rows, `PIPE_STRIP` (rows 994–999).
- **Snow guard:** two round tubes, 50 and 37 mm, their foot 0.20 m up the
  slope from the low edge, on brackets every metre over the rafters, painted
  in the ROOF region at its 33 px/m (until 2026-11-22 on a separate 0.40 m
  eave strip at 40 px/m, resampled from the stretched band).
- **Steel:** one galvanised id (`ID_GUTTER`) for the gutter, the downpipes
  and the guard, the same in every variant and the same id colour and
  surface as on `navetta_board_gable` and `viljakuivuri_tower`, so the
  farm's rainwater goods match: sRGB (134, 137, 137), roughness 0.48,
  metallic 0.60, a zinc patina between the dark roof and the white trim, so
  it suits all three roofs. Measured over `PIPE_STRIP` after weathering:
  mean sRGB 130/133/133 in all three albedos, roughness 0.50, metallic 0.56
  (ORM).

### Relief and the normal map

Relief heights for the normal map:

- battens 20 mm, over a 0.20 m pitch (12.8 px, 80 to the atlas width, so
  the bands wrap);
- casings, corner boards and post arrises 20 mm;
- door frames and braces 20 mm, hinges 26 mm, the drop bar 32 mm;
- trapezoid sheet ribs 30 mm;
- girts and rafters 40 mm;
- the gutter's roll 70 mm, its hangers 4 mm over it;
- the snow guard's tubes 35 mm and brackets 30 mm;
- the floor slab's pores, 0.4 mm;
- in the ROOF and CEIL regions every height scaled by 33/64.

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
- runs down the rear fascia from the gutter; a dirty belly on the gutter
  and light runs down its face from the lip, the same treatment as the
  farm's other two gutters; light dust on the snow guard, rust at its
  brackets, debris held on the sheet above it;
- settled dust inside the bays, thickest at the floor;
- trodden-in dirt on the workshop door's floor slab.

### The entrance floor slab

Painted by `scripts/door_floor.py` (`paint()`, `grain()`, `weather()`), as
the catalog's other entrance slabs are, in the free rows over the pedestrian
door's region (`FLOOR`): 73.6 x 8.96 px at (600, 872), 64 px/m, the slab
unfolded, U across the casing's 1.15 m from its left side, V the nosing's
0.02 m (1.28 px) and then the top from the wall plane to the leaf (0.12 m).
Float-finished cast concrete, `ID_FLOOR`, sRGB **(132, 130, 124)** in every
variant, roughness **0.88**, nonmetallic. Occlusion deepens toward the jambs
and the door (within 0.048 m), a slightly paler path is worn toward the
leaf, the pores are the footing's noise at 5 % shade and 0.4 mm of height,
and blotchy trodden-in dirt lies over it. It bleeds 2 px into its gutter.

Adding it changed only the free block it stands in: the normal map differs
only in the slab's rows (x 598-675, y 870-882), and the albedos and the ORM
elsewhere only in that block's padding (x 592-680, y 861-927), which now
carries the slab's edges instead of the pedestrian door's drip flashing,
and by at most 3/255 in the four rows over the flashing's top (y 863-866).

### Filtering

Whole-atlas mip4 stress renders (`scripts/review_atlas_mips.py`) of `LOD2`
and `LOD3` were checked at 125 m: front, 75° grazing and rear, under noon.
They showed no roof/trim colour leaks and no dark seams. The posts and
corner boards stay white, and the bays stay black. The rear eave band was
checked the same way (mip4, `LOD2`/`LOD3`, 120 m, rear and grazing, noon and
reverse sun): the gutter, board and strip merge into one grey eave line,
with no colour leak from the rows below it or from the atlas's bottom rows.
That mip review predates the 2026-11-22 repack (the fascia bands now sit in
the top 40 rows, the roof and ceiling in regions of their own) and has not
been repeated.

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
| `red_ochre` (default) | red-ochre boards (sRGB 122/52/42) and door planks a shade darker (112/48/39), off-white trim (221/217/205), dark grey steel roof (54/56/58) |
| `grey_weathered` | unpainted boards gone silver-grey (110/106/98), silvered door planks (101/98/90), weathered light grey trim, lighter than the boards but no white (150/146/137), dark grey roof (62/62/60) |
| `yellow_ochre` | yellow-ochre boards (184/148/86) and door planks (169/136/79), off-white trim (222/218/206), dark red-brown roof (75/51/45) |

The farmstead's three buildings (this shed, `navetta_board_gable` and
`viljakuivuri_tower`) stand together, so they share these variant names and
these exact numbers: one name dresses the set. Until 2026-11-22 the shed's
door planks took the wall colour; they now take the shared door colour, as
on the other two.

The three variants are a low-rise farm building's ordinary colour range (3 of
the 3–6 band). Geometry, UVs, ORM and normal are shared. The bays' bare
interior, the footing, the hardware and the galvanised gutter, downpipes
and snow guard are the same in every variant.

## Night lighting

**None. The shed is not night-lit, and it ships no `_emission.png`.** It has
no glazing, and CLAUDE.md's Output Contract allows a windowless shed to ship
no emission map. No lit signs or lamps were asked for. Consequences:

- **No `emissiveTexture` on any tier.** The validator's emission checks do
  not apply. The facts sidecar omits `textures.emission`.
- **`variants.png` is a day-only sheet**: one labelled row of the three
  colours at `LOD0`, as CLAUDE.md asks of an unlit asset with more than one
  variant, rendered by `scripts/variant_previews.py` with the catalog's
  camera and lighting.

`build.py` builds through the shared `scripts/asset_build.Asset` with
`night_lit=False`, which leaves out only the window wiring:

- `material()` wires no emission mask;
- `export_all()` sets no lit state and rewrites no emission factor;
- `render_preview()` has no emission state to set;
- `render_variants()` renders the day row only.

## Export

```
python3 facade_atlas.py export                      # albedo x3, ORM, normal
blender --background source.blend --python build.py  # meshes, preview, sidecar
```

Run the textures first: the UVs index into the atlas, and the preview reads
it. A first build from a factory scene is
`blender --background --python build.py`, which creates `source.blend`.
`facade_atlas.py` is the single source of the numbers both scripts share.

Export settings, as `asset_build`'s `export_all()` passes them:

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

- `scripts/validate_asset.py`: 0 FAIL, and no WARN once the sidecar is
  written from a committed tree (after a rebuild from a working tree it
  warns `source.dirty` until `build.py -- facts` is rerun from the commit).
  Every tier passes:
  - welded manifold topology, one material, uri-only images;
  - the normal map at scale 1, triangle ceilings;
  - pivot at ground and centred;
  - 0 hidden triangles.

  Five 1024² RGB PNGs; the facts sidecar is consistent.
- `check_layout()`, including the downpipes' and the roof and ceiling
  regions' checks.
- The 2026-11-22 audit fixes: 0 FAIL on the rebuilt tiers (332 / 268 / 192 /
  186); bounds, pivot, footprint, storeys and doors unchanged in the
  sidecar. Tier pairs at the consumer's 20 / 45 / 90 m, `LOD0` front and
  oblique at 20 and 35 m and each variant at 35 m, before and after with
  identical settings; the three farm buildings' default and grey variants
  side by side; `variants.png` looked at.
- The six working views at `LOD0` and `LOD3`.
- The shared galvanised steel pass of 2026-11-20: a texture-only change.
  Triangle counts (336 / 272 / 196 / 166) and bounds match the sidecar; the
  normal map is byte-identical. `PIPE_STRIP` measured as above (Texture
  set), within two sRGB levels of the other two farm buildings. Before/after
  renders at 20 m (`LOD0`, oblique and rear, noon) in
  `review/farm_gutter_colour_2026_11_20/` (local, git-ignored), compared
  side by side with the other two; `preview.png` regenerated.
- The rainwater goods and snow guard, before/after with identical settings:
  `LOD0`/`LOD1` at 20 and 40 m, `LOD2`/`LOD3` at 70 and 120 m, rear and
  oblique, noon and reverse sun; the front views are unchanged pixel for
  pixel, and `preview.png` (a front view) differs by at most 2/255. 9 m
  close renders of the rear, and mip4 stress renders of the rear eave.
- LOD pairs around 35, 70 and 120 m from front, oblique and rear, under two
  sun directions.
- A four-state day cycle (morning, noon, dusk, night).
- 9 m close renders of the battens, ribs and door frames under low and high
  sun.
- Whole-atlas mip4 stress renders at 125 m.
- The three variants from the catalog camera.

- The workshop door's floor slab (Construction, Revision log), from a
  snapshot in `review/review_2026_11_23/konehalli_open_bays/before/`:
  - **Door views** (`review/review_2026_11_23/konehalli_open_bays/door_views.py`,
    every tier, noon and reversed sun, over a green terrain plane at
    z = 0): the workshop door from 4.8 m and 2.3 m, both sides, 0.35 m up
    and from above; the vehicle pair from eye level and 0.35 m up; the open
    bays from 7 m. Before, grass filled the door's reveal at the foot of the
    leaf; after, concrete fills it wall to wall (between the casing's legs
    on `LOD0`, across the casing's recess on `LOD1`), its nosing a light
    line on the wall plane with nothing past it, no dark seam or stretched
    texels. `LOD2` and `LOD3`, the vehicle pair and the open bays are
    unchanged (at most 2/255).
  - **`review_asset.py`** from both: the day cycle on `LOD0`, the six
    orthographic views, and every tier front and oblique at 20, 35, 70 and
    120 m under noon; mean differences at most 0.01/255, `review_compare.py`
    sheets in `review/review_2026_11_23/konehalli_open_bays/compare/`.
  - Bounds, pivot, footprint, storeys and both doors in the sidecar
    unchanged; `LOD2` and `LOD3` byte-identical. Measured on the reimported
    tiers (`check_slab.py`): an upward face at 0.020 m under 9 of 9 sample
    points of the reveal on `LOD0` and `LOD1`, upward faces under 0.1 m
    only the slab's top, no face at grade inside the reveal, welded and
    closed.
  - `scripts/validate_asset.py`: 0 FAIL; the one WARN is `source.dirty`,
    the sidecar written from an uncommitted tree, to be rewritten with
    `build.py -- facts` once committed.

Pending in the consumer:

- import, orientation and pivot on reimport in the engine;
- LOD switching and shadows inside the bays;
- mip and anisotropic filtering of the ROOF and CEIL regions and the fascia
  bands (not re-run here since the repack);
- performance.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`) throughout.
The MCP addon was not used. Texture generation used the system Python 3
with numpy, scipy and Pillow.

## Revision log

- **2026-11-23 — workshop door floor slab.** The workshop door's 0.12 m
  reveal had no upward face under it, so a consumer's terrain showed
  inside, at the foot of the leaf. It now stands on a concrete slab 0.02 m
  over the ground, nosing on the wall plane, on its own atlas region, built
  and painted by the shared `scripts/door_floor.py`, on `LOD0` (0.90 m,
  inside the casing ring) and `LOD1` (1.15 m, the casing's recess). Tiers
  332 / 268 / 192 / 186 to 336 / 272 / 192 / 186; bounds, pivot, footprint
  and doors unchanged. The vehicle pair and the open bays are left on the
  ground.
- **2026-11-22:** audit fixes. The roof's top and the bays' ceiling repacked
  from full-width bands at 64 × 14.3 px/m into isotropic 33 px/m regions
  side by side; the snow guard is painted on the roof region and the old
  0.40 m eave strip and its split in the slab's top are gone (−4 triangles
  on every tier); the fascia bands moved to the atlas's top. `LOD3` keeps
  the header (+24). One palette for the farmstead (all three variants
  identical on the three farm buildings; the grey boards darker and the
  grey trim from near-white to weathered light grey; door planks take the
  shared door colour). Roof steel dielectric (0.50 / 0, was 0.50 / 0.10).
  Stale `variants.png` note fixed; the consumer's switch distances
  recorded. Triangles 336 / 272 / 196 / 166 → 332 / 268 / 192 / 186.
- **2026-11-20:** the gutter, downpipes and snow guard share one galvanised
  steel with the farm's other two buildings: `ID_GUTTER` goes from sRGB
  120/122/121, roughness 0.50, metallic 0.40 to 134/137/137, 0.48, 0.60, and
  the gutter gains light runs down its face beside its dirty belly.
  Texture-only: geometry, UVs, relief heights, layout and the normal map are
  unchanged.
- **2026-11-20:** added the rainwater goods and the snow guard. A
  half-round galvanised gutter is painted on the rear fascia, and the roof's
  lowest 0.40 m maps onto a new rear eave band at 40 px/m that carries a
  painted snow guard. Two downpipes (`scripts/downpipes.py`), straight into
  the soffit with shortened shoes, stand at the rear wall's ends on every
  tier. Triangles went from 234/218/158/134 to 336/272/196/166. Bounds and
  pivot are unchanged.
