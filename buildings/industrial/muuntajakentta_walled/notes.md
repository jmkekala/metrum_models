# muuntajakentta_walled

## Style brief

The walled transformer yard (*muuntajakenttä*) of a small Nordic town's
coal-fired heat and power plant, 1950s–60s. It is one of five separate
pieces of one plant, with the boiler and turbine hall, the brick chimney,
the coal reception and the office. The pieces stand apart on the lot and
nothing joins them: this asset has no ground slab shared with the others,
and no cables or busbars leave its compound.

A compound of 20.0 × 12.0 m behind a plain industrial perimeter wall,
1.70 m of brick with a thin light coping and plain piers at the corners,
the gate and every 4–6 m, low enough that the plant inside reads over it.
A painted sheet-steel double gate with a high-voltage warning plate closes
the front. Inside, from the incoming (west) side:

- a solid galvanised portal 10.9 m tall: two tapered box columns with
  shield-wire peaks and a deep I-beam, a suspension string hanging from it
  over each of the six phases;
- for each transformer, a switchgear bay, the yard's "forest of
  insulators": a disconnector with six post insulators on a tall steel
  table, three minimum-oil breaker poles (brown porcelain columns with
  red-brown cast heads) on a 2 m steel stand, and three current
  transformers on a concrete table;
- slack flexible conductors: a drop from each string to its disconnector,
  then near-level spans from disconnector to breaker, breaker to current
  transformer and current transformer to the transformer's bushing;
- two power transformers in grey-green paint, each on a concrete plinth
  with a gravel oil bed. Each has a tank, a radiator bank on each long
  side, a conservator drum on saddles over the east end, three brown
  porcelain high-voltage bushings toward the switchgear and a cable box on
  the east end;
- a board-marked concrete fire wall between the transformers;
- precast cable trench covers from each transformer's cable box to the
  switchgear house.

The switchgear house is the asset's building. It is a single-storey red
brick box of 5.0 × 4.0 m under a flat felt roof on a concrete slab, with one
steel door to the street and steel louvres for ventilation. It stands in the
compound's front-east corner, its front and east walls in the yard wall's
outer planes, so the wall stops on it.

The asset is generic and stands for no particular installation. It carries
no lettering, brands or logos. The warning plates are a plain yellow
triangle with a lightning arrow.

## Category and secondary use

`buildings/industrial/`, as part of a power plant. There is no secondary
use: the switchgear house serves the yard and nothing else.

## Hero/landmark status

**No.** Ordinary budgets, a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Compound, the piers' outer faces (the plan bounds) | 20.00 × 12.00 m |
| Yard wall's centre line | 19.64 × 11.64 m |
| Switchgear house, outer walls | 5.00 × 4.00 m, x 2.94–7.94, y −5.94 to −1.94 |

Coordinates are in the Blender build frame (front −Y). Its origin is where
the first build's compound centre was: the compound grew 4.0 m west for the
switchgear bays, and keeping the origin kept the house's, transformers' and
trenches' numbers. The pivot is the plan's centre, x −2.0, y 0 in this
frame.

- **Yard wall:** 0.24 m thick, 1.70 m high with its 0.06 m coping, on a
  0.31 m concrete footing.
- **Piers:** 12 of them, 0.36 m square and as high as the wall, with no
  caps. There is one at each free corner, one each side of the gate, one
  where the east run meets the house's north wall, and between: one on the
  front run (5.4 m bays), one on the west (5.8 m), three on the north
  (4.9 m) and one on the east (3.9 m).
- **House:** its front wall stands in the yard wall's outer plane, y −5.94,
  and its east wall in the east wall's, x 7.94. The piers stand 0.06 m
  proud of both planes.
- **Gate:** in the front wall between piers at x −0.98 and 2.80, with
  3.42 m clear between them (x −0.80 to 2.62). The leaves are 0.06 m thick,
  set 0.08 m behind the wall's outer face, and run from 0.04 to 1.66 m
  high.
- **Transformer plinths:** 4.40 × 3.40 × 0.30 m, centred on x −2.00 and
  y ±2.70.
- **Fire wall:** x −3.80 to −0.20, 0.30 m thick on y 0, 3.80 m high.
- **Switchgear bays:** centred on y ±2.70, phases 1.00 m apart (y ±1.70,
  ±2.70, ±3.70); every frame runs 1.35 m either side of the bay's centre
  line. Disconnector posts at x −9.30 and −8.70 on a deck x −9.45 to
  −8.55, 4.20 m up; breaker poles on x −7.00, on a stand 2.00 m up;
  current transformers on x −5.30, on a table 2.20 m up.
- **Gantry:** columns at x −10.60, y ±4.60, on 0.80 m square concrete pads.
  The shield-wire peaks' tips at 10.90 m are the highest point.

The pivot is at ground level, centred on the plan's bounding box, which is
the compound's centre. It is taken from `LOD0` and applied to every tier.
Every tier has the same plan bounds, including `LOD2` and `LOD3`, whose
pier-thick wall keeps the piers' outer faces (Construction).

The facts sidecar's `footprint` is the house alone, since CLAUDE.md's
footprint leaves out fences (Export). In the glTF frame (metres, +Y up, +Z
front, origin at the pivot) the house is the rectangle x 4.94–9.94, z
1.94–5.94.

## Story height

**One storey, 3.20 m** from the ground to the roof slab's underside line,
3.45 m to the slab's top. This is inside the 3.0–3.3 m band. It is a plant
room, not a habitable floor, and its height carries the high louvres over
the switchgear cubicles.

## Door leaf height

**Steel door leaf 1.00 × 2.10 m**, with no fanlight or transom. The pressed
steel frame adds 0.0625 m at the sides and head. The threshold is at
ground level and the door faces the street (−Y). It is the house's only
door.

The gate (two leaves, 3.42 m clear, 1.62 m high) is not a door in the
facts schema: it opens onto the open yard, not an occupied space. It reads
at the scale of the 1.70 m wall it closes, under the 2.0–2.4 m band.

## Window sills

n/a: the house has no windows. It has five steel louvres, 0.875 × 0.50 m
in the clear, each in a 0.0625 m frame:

- **High louvres:** sill 2.30 m, head 2.80 m. One is on the front, two on
  the east wall and one on the north (yard) wall. Their heads stay 0.34 m
  under the slab, and their sills are 0.20 m over the door's head.
- **Low louvre:** sill 0.55 m, head 1.05 m, on the west (yard) wall, the
  intake under the high outlets.

## Eave overhang

**None.** The flat concrete roof slab is flush with the walls. Its 0.25 m
edge is painted as cast concrete with a drip line, a steel trim and the
felt dressed over it. Two reasons:

- The house's front and east walls stand in the compound's outer planes, so
  an overhang there would move the plan bounds and the pivot off the
  compound's centre.
- A flush slab with a trimmed edge is the period's ordinary detail for a
  small plant room.

The roof sheds over its edges. There is no gutter, so there are no
downpipes (CLAUDE.md, Geometry and Construction).

## Construction

`build.py` builds closed solids and unions them with Blender's Exact
boolean (`asset_build.union`). There is no ground: every solid stands on
z = 0 or on another solid. One mesh per tier.

### Orientation and the incoming side

- **Front (−Y):** the street, with the gate and the house's door. In the
  glTF frame it faces +Z.
- **West (−X):** the incoming side, toward the turbine end of the plant's
  hall, where the gantry and the switchgear stand. In the glTF frame this
  is −X.
- Nothing leaves the compound. The conductors run only from the gantry's
  strings through the switchgear to the bushings, and the trenches end
  inside the house.

### Yard wall

A plain perimeter wall: it closes the yard without hiding it, and the
catalog and play cameras see the plant over it. It is boxes:

- four runs, 0.24 m thick and 1.70 m high, each ending inside a pier or
  inside the house;
- 12 plain piers, 0.36 m square and as high as the runs, their tops
  flush with the coping;
- the gate, as one 0.06 m plate whose ends run 0.05 m into its piers.

Every face is closed, both faces of the wall and its top included. The
gate's east pier stands against the house's front-west corner and runs
0.04 m into it. The east run ends inside a pier that runs into the house's
north wall, so no face of the wall is left coplanar and open against the
house. The piers' faces take the wall's band, so the footing, the brick
and the thin coping run round them.

On `LOD2` and `LOD3` the runs are one pier thick (0.36 m), centred so that
their outer faces are the piers' outer faces, and the piers fold into the
wall. The gate's east pier becomes a short run into the house and the
junction pier the east run's foot, so the plan bounds stay 20.0 × 12.0 m.

### Switchgear house

The house is one closed solid with its openings, built as the catalog's
brick buildings are (`nostokonehuone_brick`, `hiilisiilo_drive_through`):

- the four walls as regions on wall frames, the door notched into the
  front wall's foot, the louvres as holes;
- the 0.25 m slab edge as a strip on each wall;
- the flat roof and the floor as the two caps.

Openings by tier:

- **`LOD0`:** each opening is a casing ring round a recess, 0.12 m for the
  door and 0.10 m for the louvres;
- **`LOD1`:** one recess the size of the casing;
- **`LOD2`/`LOD3`:** a flush painted rectangle.

### Transformers

Each transformer is a set of closed solids:

- **plinth:** concrete, its top the gravel bed;
- **tank:** its base 0.05 m inside the plinth, its cover at 2.90 m;
- **radiator banks:** 2.00 × 0.55 m, z 0.70–2.55 m, run 0.05 m into the
  tank;
- **conservator:** r 0.28 m, its axis along Y at 3.40 m, on two saddles
  from the cover. Where a tier drops the saddles (`LOD2`, `LOD3`), the
  drum is a box of the square drum's width that comes down into the
  cover, so it never floats;
- **bushings:** three, turned from a profile, with a steel turret
  (r 0.15 m), a porcelain body tapering from r 0.115 to 0.075 m and an
  aluminium terminal, the tip at 3.95 m;
- **cable box:** on the east end.

The sheds, fins, bolts and valves are texture.

`check_layout()` keeps the following clear:

- the turrets inside the cover;
- the conservator clear of the bushings;
- the radiators 0.8 m clear of the fire wall;
- the fire wall 0.5 m past both tank ends and above the conservators;
- the plinths clear of the yard wall and 2 m from the house.

### Gantry and strings

A solid portal, as the period built them where a lattice was not wanted;
a lattice would need alpha here.

- **Columns:** square galvanised boxes tapering from 0.40 m at their pads
  to 0.22 m at 9.70 m, from inside their 0.30 m pads.
- **Shield-wire peaks:** a square spike on each column, 0.16 m at its foot,
  rising 1.20 m to a point at 10.90 m.
- **Beam:** an I on its side, 0.60 m deep with 0.30 m flanges, z
  9.00–9.60, from y −4.90 to 4.90.
- **Strings:** one over each switchgear phase, at y = ±2.70 and
  ±2.70 ± 1.00, hanging 0.85 m from inside the beam's bottom flange. Each
  has a cap, four discs of r 0.125 m at a 0.146 m pitch, and a clamp.

### Switchgear

One bay per transformer, on the transformer's centre line, phases 1.00 m
apart across Y. West to east, with a walkway of 0.75–1.4 m between parts:

- **Disconnector:** a galvanised deck 0.90 × 2.70 × 0.15 m, its top at
  4.20 m, on two 0.24 m square steel legs; on it six post insulators in
  two rows 0.60 m apart (porcelain r 0.09 tapering to 0.075 m, a
  galvanised cap r 0.10 m, tops at 5.15 m) and a closed blade across each
  phase's pair. It stands high so that its outgoing span meets the
  breakers' top heads level.
- **Breaker:** a galvanised stand deck 0.30 × 2.70 m at 1.85–2.00 m on two
  0.14 m legs, an operating cabinet under it, and three minimum-oil
  poles. Each pole, from 1.97 m: support porcelain r 0.12 m to 1.25 m, a
  red-brown mid head r 0.17 m 0.35 m tall (the interrupter's lower
  terminal), the chamber's porcelain r 0.12–0.11 m, and a red-brown top
  head r 0.16 m, its top at 5.27 m: 3.30 m of column on a 2.0 m stand.
- **Current transformers:** a concrete table, its beam 0.50 m wide at
  1.85–2.20 m on two 0.35 m legs; on it three posts from 2.17 m: a steel
  base r 0.15 m, porcelain r 0.12–0.10 m, and a grey-green oil head
  r 0.19 m 0.40 m tall, the top at 3.92 m.

Each turned part is an 8-, 6- or 4-sided prism by tier; the sheds are
texture. `LOD3` keeps only the breaker poles, each one 3-sided prism
from the ground to its top head (`poles3()`), its stand painted at its
foot on a strip of its own (`POLE3_R`, 32 px/m along V).

### Conductors

Flexible conductors as thin closed tubes (r 0.025 m) through points on a
parabolic sag, rings square to the local tangent, both ends buried in the
parts they join. Per phase:

- **drop:** from the string's clamp at 8.21 m down to the disconnector's
  incoming post cap, 0.35 m sag;
- **span:** from the outgoing post cap to the breaker's top head, level,
  0.14 m sag;
- **span:** from the breaker's mid head to the current transformer's head,
  rising 0.25 m, 0.12 m sag;
- **span:** from the current transformer's head to the transformer's
  bushing terminal, 0.18 m sag, converging from the switchgear's 1.00 m
  phase spacing to the bushings' 0.60 m.

### Fire wall and trenches

- **Fire wall:** one concrete box standing on the ground between the
  plinths.
- **Trenches:** covers 0.60 m wide and 0.08 m proud, starting inside their
  plinths and ending inside the house. The south one runs straight into
  the house's west wall. The north one runs east, then turns south at
  x 4.70 into the house's north wall. It is one closed L, its top three
  quads so that the covers' joints turn with it.

### Authored parameters

`facade_atlas.py` holds every number both scripts use, the switchgear's
turned profiles (`breaker_profile`, `post_profile`, `ct_profile`) among
them. `build.py` adds the pier spacing, the runs, the conductors' end
points and sags (`spans()`) and the tiers' modes (`mode()`).
`check_layout()` asserts the following:

- the openings sit clear of corners, piers, each other and the slab;
- the door leaf is in the 2.0–2.4 m band;
- the gate's piers frame the opening;
- the house's walls lie in the wall's planes;
- the clearances above;
- the switchgear's parts in order west to east with at least 0.6 m
  between them, the bays clear of the yard wall and of each other, the
  breaker heads at least 0.6 m apart, every leg under its frame;
- the spans within 15° of level, no conductor sagging more than 0.25 m
  under its lower end, the last span 0.6 m over the covers, and the
  strings 2 m over the disconnector.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 6,856 | 12,000 | everything; turned disc strings (6 sides); 8-sided breaker poles and current transformers, 6-sided disconnector posts with caps and blades; conductors 4-sided, 6 segments on the drop and 4 on each span; 8-sided bushings and conservators; I-beam; house openings as casing rings round recesses |
| `LOD1` | 3,760 | 4,000 | strings as plain 6-sided prisms carrying the discs in paint; poles 6-sided, current transformers 6-sided without the base step, posts 3-sided tapers with no caps, no blades; conductors 3-sided, 3 segments on the drop and 2 on the spans; bushings 6-sided turret and one taper; conservators 6-sided; openings one recess each |
| `LOD2` | 1,448 | 1,500 | the wall one pier thick, the piers folded in; poles and current transformers 4-sided single tapers carrying heads and bases in paint, posts 3-sided, no breaker cabinet; only the six drops kept, straight; strings, bushings (one taper) and conservators 4-sided, the conservators' saddles gone and each drum a box down into its cover; beam a box; openings flush; coplanar boolean splits dissolved |
| `LOD3` | 460 | 500 | the switchgear goes but for the six breaker poles, each one 3-sided prism from the ground; strings, conductors and bushings go; both radiator banks one box through the tank; cable boxes and pads go; trenches go; the house's two yard-side louvres go |

Where `LOD0`'s triangles go, measured by building each group alone and by
leaving groups out of the union:

| Group | Triangles |
| --- | --- |
| Switchgear, both bays, with their unions | about 2,480 (2,136 before the union: 6 poles about 124 each, 12 posts 44 each, 6 current transformers 92 each, frames and blades) |
| Conductors, 24 of them, with their unions | about 1,190 (960 before) |
| Gantry and strings | about 1,300, nearly all in the six turned strings (200 each) |
| Each transformer | about 390 |
| Yard wall, 12 piers and gate | 204 |
| House | 164 |
| Trenches and fire wall | 52 |

**Comparison with the catalog.** `LOD0` is well above the small brick
buildings (`nostokonehuone_brick` 540, `kaivoskonttori_brick` 896) because
the yard is mostly equipment, not wall plane: the switchgear's 18 turned
parts per bay and the 24 conductors are the asset. It is still under 60% of
the ceiling. The strings and the switchgear's turned profiles are where
triangles buy silhouette below the relief threshold: at 20–35 m a pole
reads by its two stepped heads and a string by its scalloped outline.
Trim in CLAUDE.md's sense (the piers, the house's slab edge and the
trench covers) is under 500 triangles.

**`LOD1` and `LOD2` sit near their ceilings** (240 and 52 to spare) and
**`LOD3` 40 under**, so any change to them must be recounted. The union
costs more than the parts here: every conductor end, post foot and leg cuts
the face it enters. Thinning the posts to 3 sides, the spans to 2 segments
and the bushings to one taper paid for `LOD1`; the pier-thick wall, the
one-taper bushings and dropping every span but the drops paid for `LOD2`.
`LOD3`'s pointed peaks pay for its conservators' new boxes, and its bushings (76 with their unions) for the six poles (48).

## LOD review

Intended switches are the catalog defaults, 35, 70 and 120 m, with no
overrides.

The review camera was perspective, 1920×1080, 50° vertical FOV, with
distance measured along the view to the visible front or rear wall
(`scripts/review_asset.py`). Rendering was Cycles at 24 samples with
denoising, AgX, exposure 0. Pairs compared:

- `LOD0`/`LOD1` at 30/40 m, front and oblique, noon and reverse sun;
- `LOD1`/`LOD2` at 65/75 m, front, oblique and rear, noon;
- `LOD2`/`LOD3` at 115/125 m, front, oblique and aerial, noon and reverse.

Every working render is in the local, untracked
`review/power_plant_rev_2026_11_21/muuntajakentta_walled/` (the first
build's in `review/power_plant_2026_11_21/muuntajakentta_walled/`).

- **`LOD0`→`LOD1`:** the strings lose their modelled discs and keep them in
  paint; the disconnector posts lose their caps and blades; the poles and
  current transformers go from 8 to 6 sides; the conductors lose
  segments, their sag now in two or three straight runs. At 30 m the
  switchgear's outline, the heads' red-brown and the conductors' paths are
  the same; the caps and blades are 1–2 px. The house's openings go from
  ring to one recess, which is not visible at 40 m.
- **`LOD1`→`LOD2`:** the spans between the switchgear's parts go and only
  the six drops stay, straight, so the gantry still feeds the bays. At
  65 m a span is 0.05 m, under half a pixel, and the bays read by their
  parts, which stay: poles and current transformers as tapers with their
  heads in paint, posts as 3-sided prisms, the tables and stands. The
  piers' 0.06 m projection folds into a pier-thick wall, under a pixel.
  The beam becomes a box of the same outline; the openings go flush.
- **`LOD2`→`LOD3`:** the switchgear cannot fit in 500 triangles, and with
  it simply dropped the whole west half of the yard emptied at 120 m: an
  identity change. `LOD3` therefore keeps the six breaker poles as single
  3-sided prisms from the ground (`poles3()`), their stands painted grey
  at the foot and their red-brown heads painted on a strip of their own,
  48 triangles; the bushings (76) went to pay for them. In the 115/125 m
  pair the poles keep the bays' verticals and red heads; the
  disconnectors' tables, the current transformers, the strings, the drops
  and the bushings go, which shows when the pair is blinked. The trench
  covers go too. The radiator banks become one box, keeping their
  outline. The gantry, tanks, conservators, fire wall, wall, gate and
  house keep their silhouettes on every tier.
- **Bounds:** every tier keeps the 20.0 × 12.0 m plan bounds and the
  pivot. The 10.90 m height is the gantry's peaks, kept on every tier.

The six working views (`review_asset.py --six-views`: orthographic front,
rear, both sides, top and a raised aerial) were looked at for `LOD0` and
`LOD3`, with the reference set beside them for proportion. The top view
shows each phase running straight from its string through disconnector,
breaker and current transformer to its bushing, converging on the
bushings' closer spacing; the aerial shows the switchgear and gantry well
over the 1.7 m wall. Before/after sheets against the first build (padded
to a common canvas, since the bounds changed) are in `compare/`.

Pending in the consumer: real LOD switching, shadows in the yard and
performance.

## Interior geometry

The validator's hidden-surface test reports 4 of 6,856 triangles at
`LOD0` (1.4 m²), 4 at `LOD1`, 2 at `LOD2` and 3 at `LOD3`, all PASS.

The candidates are the strips of each tank's long sides under its radiator
banks. They run between the plinth's top at 0.30 m and the banks'
undersides at 0.70 m, 0.55 m deep under the bank. That is exterior surface,
visible from low views along the plinth, but the test's 40 fixed rays from
each face's centre all strike the bank or the plinth.

What is removed and kept:

- No interior is modelled. The house is one closed solid, so its floor
  and roof are its caps and it has no room.
- The union removes every buried face: the tank's base in the plinth, the
  banks' and cable boxes' backs, the bushings' and saddles' feet, the
  conservator boxes' feet in the covers (`LOD2`, `LOD3`), the strings' tops
  in the beam, the columns' feet in their pads and the peaks' feet in the
  columns, the switchgear's legs in their decks and its posts, poles and
  current transformers in theirs, the conductors' ends, the runs' ends in
  the piers and the house, and the trenches' ends.
- The only closure faces kept are the floor faces on the ground under the
  walls, piers, house, plinths, pads, legs, fire wall and trenches.

## Known simplifications

- **This is a building-class asset whose shell is a compound.** The
  building is the switchgear house. The rest is a walled yard of
  electrical plant with no roof over it, open to the sky, with no ground
  modelled inside or outside the wall. The yard is meant to sit on the
  consumer's terrain.
- **A wall, not a fence:** the period's yards stood open behind chain-link,
  which needs alpha. The wall is kept low and plain instead, so the plant
  reads over it.
- **No ground or yard surface:** the gravel bed is painted on the
  plinths' tops only. The trenches' covers stand 0.08 m proud, with no
  trench walls under them.
- **Equipment detail is painted:** the radiators' fins, the tanks'
  stiffeners, bolted flanges, valves, lugs and blank rating plates, the
  porcelain sheds on every bushing, post, pole and current transformer,
  the breakers' head flanges, the current transformers' sight glasses and
  the cable box's lid are paint. On `LOD1`–`LOD2` the strings' discs are
  paint too, and on `LOD2` the poles' and current transformers' heads.
- **Switchgear simplified:** each disconnector is a closed blade between
  two posts, with no operating rod or arcing horns; each breaker has one
  operating cabinet and no linkage to the poles; the current transformers
  carry no secondary wiring. The steel tables and stands are plain
  galvanised boxes, not lattice.
- **Conductors:** thin closed tubes on a parabolic sag, with no clamps or
  spacers. Nothing runs between the gantry and the world outside: the
  beam carries strings but no incoming line, and the portal stands for the
  yard's incoming side without wiring it to anything outside. The
  transformers' low-voltage side is the cable box and trench to the house,
  with no cables modelled.
- **No lattice:** the gantry is solid tapered box section with no lattice
  (which would need alpha) and no bracing.
- **One door and no yard door:** the house has no door into the yard, and
  the yard's only way in is the gate. The house's door is on the street.
- **No yard lighting, signage text, fence wire or barbed wire.**
- **No equipment inside the house:** the louvres are dark behind their
  blades.
- **One-sided gate artwork:** the gate's back shows the same leaves
  mirrored, so the warning plate appears on the inside too.

## Texture set

One 1024² trim-sheet atlas at 64 px/m, rasterised by `scripts/atlas.py` at
the default supersampling (`atlas.SS` = 4) and padded last by
`atlas.pad()`. Layout, in rows from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–248 | HOUSE band | U along the wall, V = height, 64 px/m; concrete plinth to 0.375 m, then stretcher-bond brick |
| 252–384 | FENCE band | U along the wall, V = height; concrete footing to 0.3125 m, brick, the thin precast coping from 1.6375 m to 1.70 m; the piers' faces too |
| 390–558 | unique, row A | tank side, gate, door, radiator face and end, conservator barrel, gravel bed |
| 566–734 | unique, row B | tank cover, roof, slab edge, radiator top, louvre, bushing, string, galvanised steel, cable box, conservator end |
| 740–1016 | unique, row C | flat patches (the breakers' head paint among them), breaker pole, disconnector post, current transformer, `LOD3`'s whole-pole strip (32 px/m in V), the fire wall's board-marked concrete (also the current transformers' tables), the trench covers |

### Deviations from 64 px/m

- **Gravel bed on the plinths' tops:** 40 px/m.
- **House roof:** 32 px/m. Both are horizontal surfaces of low-contrast
  gravel and felt, seen from above at a distance.
- **Gantry steel:** U at 64 px/m at the columns' feet, held across their
  taper, V stretched along the members. It is uniform galvanised mottling
  with nothing that shows the stretch. The peaks, the switchgear's steel
  and the conductors take flat patches.
- **Bushings, strings, poles, posts and current transformers:** wrapped
  once round, U by angle, V at 64 px/m along the axis.

### Relief heights for the normal map

- brick faces 6 mm over the mortar;
- coping 20 mm;
- the gate's pressed ribs 8 mm and its frame 25 mm, hinges 40 mm;
- the door's frame 25 mm;
- louvre blades 30 mm;
- tank stiffeners 30 mm and flange bolts 40 mm;
- radiator fin edges 60 mm over their gaps, header pipes 80 mm;
- porcelain sheds 30 mm, painted discs 25 mm;
- the breakers' and current transformers' head flanges 12–15 mm;
- felt laps 6 mm, scaled by 32/64;
- form-tie holes −10 mm.

### Porcelain on the switchgear

The switchgear's porcelain is the bushings' brown glaze, but its sheds are
painted with a deeper shadow under each (a third of the pitch at 0.42),
so a tall column reads dark brown and its red-brown cast heads stand
apart from it, as they do on such breakers. The bushings keep their own,
lighter shed paint.

### Weathering

`scripts/weathering.py`'s moderate level:

- **masonry:** grime, plinth soil, splash and salt bloom on both brick bands
  and the fire wall, dust on the coping and runs under it;
- **gate and door:** kicked dirt at the foot, grime at the hasp and handle,
  a little rust at the gate's foot;
- **transformers:** runs down the tank sides, dust on the covers,
  radiator tops and conservators, rust at the base frames and the
  radiators' lower headers;
- **switchgear:** dust on the breakers' and current transformers' heads,
  runs down the breakers' mid heads, a trace on the porcelain;
- **ground surfaces:** dust and oil on the gravel and curbs, dust on the
  trench covers;
- **steel and porcelain:** light dust on the zinc, a trace on the
  porcelain;
- **slab edge:** runs down it from the felt.

### Filtering and inventory

Whole-atlas mip4 stress renders (`scripts/review_atlas_mips.py`) of `LOD2`
and `LOD3` were checked at 125 m in the first build: aerial, front and 75°
grazing, under noon. They showed no colour leaks between regions and no
dark seams; the brick stayed brick-red, the copings light, the gate dark
and the porcelain brown. The new regions sit in row C with 8 px gutters
and were not mip-reviewed separately (Review status).

Unique textures are five 1024² RGB PNGs: three albedos, one ORM and one
normal map, about 4 MiB each in memory without mips. The ORM and normal
map are shared by every variant.

## Glazing treatment

n/a: the yard has no glazing. No glass id is painted and
`scripts/glazing.py` is not used. The validator's glazing measurement does
not run, because there is no emission mask to select glass with.

## Variant list

| Variant | Meaning |
| --- | --- |
| `red_brick` (default) | muted red facing brick on the house and yard wall, grey mortar; the gate and door dark green |
| `yellow_brick` | yellow facing brick, pale mortar; the gate and door oxide red-brown |
| `brown_brick` | dark purple-brown clinker brick, darker grey mortar; the gate and door blue-grey |

The brick and its mortar are the plant's: `red_brick` and `brown_brick`
are the same constants on all five of the plant's pieces, so the yard can
follow the hall it serves.

| | `red_brick` | `brown_brick` |
| --- | --- | --- |
| Brick | (114, 73, 62) | (80, 59, 57) |
| Darker brick | (90, 59, 51) | (62, 46, 45) |
| Mortar | (125, 123, 118) | (108, 106, 102) |

`red_brick` is the catalog red (144, 72, 52), (114, 58, 45), mortar
(150, 145, 136), each channel taken to Y + 0.6 (c − Y), Y its Rec. 709
luma, then times 0.94, and the mortar to 0.94 × 0.90. `brown_brick` is a
dark clinker, well below the red in value and redness. The yard wall's
plain brick (atlas rows 800–980) measures sRGB (111, 81, 72), R − G 29.7,
on `red_brick` and (83, 68, 65), R − G 15.5, on `brown_brick`. The painted steel of the gate and door
moves with the brick. Geometry, UVs, the ORM and the normal map are shared.

Fixed in every variant:

- the electrical plant: grey-green tank paint sRGB (104, 114, 104),
  galvanised gantry and switchgear steel (134, 137, 137), brown porcelain
  (98, 54, 36), the breakers' red-brown heads (144, 66, 44) and aluminium
  conductors;
- the board-marked fire wall and tables, the concrete and the gravel;
- the felt roof.

## Night lighting

**None. The yard is not night-lit, and it ships no `_emission.png`.** The
house has no glazing, only steel louvres, because an unmanned switchgear
room is ventilated, not lit for the street. CLAUDE.md's Output Contract
allows a building without glazing to ship no emission map. No yard lamp is
painted or lit. Consequences:

- **No `emissiveTexture` on any tier.** The validator's emission checks do
  not apply. The facts sidecar omits `textures.emission`.
- **No `variants.png`.** CLAUDE.md asks for it only of night-lit buildings.

`build.py` builds through the shared `asset_build.Asset` with
`night_lit=False`, which leaves out only the window wiring:

- `material()` wires no emission mask;
- `export_all()` sets no lit state and rewrites no emission factor;
- `render_preview()` has no emission state to set;
- `render_variants()` renders nothing.

The 2026-11-21 revision's full rebuild was the first full export through
that path. It wrote no emission PNG; each tier's one material carries
`baseColorTexture`, `metallicRoughnessTexture`, `occlusionTexture` and
`normalTexture` and no `emissiveTexture` or `emissiveFactor`; and the
build printed "no variants.png: not night-lit" and wrote none.

## Export

```
python3 facade_atlas.py export                      # albedo x3, ORM, normal
blender --background source.blend --python build.py  # meshes, preview, sidecar
```

Run the textures first: the UVs index into the atlas, and the preview reads
it. A first build from a factory scene is
`blender --background --python build.py`, which creates `source.blend`.

### Export settings

As `asset_build`'s `export_all()` passes them:

- `export_format='GLB'`, `use_selection=True`, `export_yup=True`;
- `export_apply=True`, `export_keep_originals=True`;
- `export_cameras=False`, `export_lights=False`.

`scripts/glb_images.py`'s `strip_embedded_images()` then removes the
placeholder `bufferView` beside each image `uri`.

### Bindings

The validator confirms one material, uri-only external images, and
`normalTexture` at scale 1 on UV0 for every tier. The shared `asset_build`
material binds the same set on all four tiers, traced in each GLB:

- the default variant's albedo to `baseColorTexture`;
- the ORM's G/B to `metallicRoughnessTexture`;
- the ORM's R to `occlusionTexture`.

The material has backface culling on and exports single-sided and opaque.
The other variants swap the albedo file only.

The preview uses the catalog's fixed camera orientation, lens, sun and flat
grey world, with only the distance fitted (`asset_build.fit_camera`). It
shows `LOD0`, `red_brick`.

### Facts sidecar

`export/muuntajakentta_walled.model.json` states, in the glTF frame
(metres, +Y up, +Z front, origin at the pivot, which is the build frame's
x −2.0):

- **bounds:** x −10.0 to 10.0, y 0 to 10.9, z −6.0 to 6.0;
- **footprint:** the switchgear house's outer walls, 5.0 × 4.0 m, x
  4.94–9.94, z 1.94–5.94;
- **storeys:** one, its floor at ground, 15.91 m² inside 0.24 m walls;
- **dwellings:** none;
- **doors:** one, the house's steel door (`entrance`, main), facing the
  street. It is at [6.24, 0, 5.94], facing +Z, 1.00 × 2.10 m.

The validator's "doors on the footprint" check fits: the door is on the
house's front edge.

The schema has no place for the compound, so these are recorded here
rather than in the sidecar, in the same glTF frame:

- **Wall line (piers' outer faces):** the rectangle x −10.00 to 10.00, z
  −6.00 to 6.00, 1.70 m high. The house fills its corner x 4.94–9.94, z
  1.94–5.94.
- **Gate:** its centre on the wall's outer face at [2.91, 0, 5.94], 3.42 m
  clear between its piers (x 1.20–4.62), 1.62 m high, facing +Z.
- **Transformer plinths:** x −2.20 to 2.20, z 1.00 to 4.40 (south) and z
  −4.40 to −1.00 (north), 0.30 m high.
- **Switchgear bays:** on z ±2.70, phases at z ±1.70, ±2.70 and ±3.70.
  Disconnectors on x −7.30 and −6.70, posts' tops 5.15 m; breaker poles
  on x −5.00, tops 5.27 m; current transformers on x −3.30, tops 3.92 m.
- **Gantry:** columns at x −8.60, z ±4.60, beam 9.00–9.60 m, column tops
  9.70 m, peaks to 10.90 m, on the −X (incoming) side.

## Review status

Checked here, in Blender:

- `scripts/validate_asset.py`: 0 FAIL. The one WARN is `source.dirty`, from
  an uncommitted tree. On every tier the validator passes:
  - welded manifold topology;
  - one material and uri-only images;
  - the normal map at scale 1;
  - triangle ceilings;
  - pivot at ground and centred;
  - the hidden-surface test (Interior geometry).

  It also passes the five 1024² RGB PNGs and the facts sidecar's schema,
  hashes, tiers, footprint and door.
- `check_layout()`, with the switchgear's and conductors' checks.
- The bindings traced in each GLB: albedo, ORM twice and normal, no
  emission (Night lighting).
- The six working views at `LOD0` and `LOD3`.
- LOD pairs around 35, 70 and 120 m from front, oblique, rear and aerial
  views, under two sun directions; the 115/125 m pair re-rendered after
  `LOD3` kept the breaker poles.
- Whole-atlas mip4 stress renders of `LOD2` and `LOD3` at 125 m, aerial,
  front and grazing: the heads stay red-brown, the porcelain dark brown,
  the steel grey, with no leaks or dark seams.
- The day cycle (morning, noon, dusk, night) from the fitted oblique.
- The catalog preview: the fixed camera sees over the low front wall into
  the yard. The gantry, its strings and drops, the switchgear's poles and
  heads, the current transformers, the bushings, conservators and fire
  wall all show over the wall, with the gate and the house's door in
  front.
- The red and brown brick against the plant's shared constants (Variant
  list).
- The plant palette pass: ORM, normal and `yellow_brick` albedo
  pixel-identical to the previous build, triangle counts and bounds
  unchanged; a 35 m oblique noon render of each variant before and after.

Pending in the consumer:

- import, orientation and pivot on reimport in the engine;
- LOD switching, shadows in the yard and performance;
- mip and anisotropic filtering of the stretched gantry steel, the radiator
  fins (a 3.2 px period), the porcelain sheds and the brick;
- the yard's placement on terrain, with no ground of its own.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`)
throughout. The MCP addon was not used. Texture generation used the system
Python 3 with numpy, scipy and Pillow.

## Revision log

- **2026-11-21 — plant palette pass.** `red_brick`'s mortar and a dark
  purple-brown `brown_brick` set to the plant's shared constants.
- **2026-11-21 — open switchyard.** The garden-like wall became a plain
  1.70 m perimeter wall with a thin coping and 12 plain piers instead of 17
  capped ones, and the compound grew 4.0 m west (20.0 × 12.0 m) for a
  switchgear bay per transformer: disconnector, three minimum-oil breakers
  and three current transformers. The H-section portal became a 10.9 m
  solid one with tapered columns, a 0.60 m I-beam and shield-wire peaks,
  its strings now over the switchgear's phases, and the six sloping
  tubular buses gave way to slack conductors through the switchgear. On
  `LOD2` and `LOD3` the conservator now sits on its cover instead of
  floating 0.3 m over it. `red_brick` took the plant's shared muted red.
  The pivot moved with the bounds: every glTF coordinate in the sidecar
  shifted +2.0 m in x (the door from x 4.24 to 6.24), and the height rose
  from 7.45 to 10.90 m. `LOD3` keeps the breaker poles and drops the
  bushings. Every PNG changed
  (the yellow and brown albedos in their new and moved regions only, not
  their brick), as did every GLB, `source.blend`, `preview.png` and the
  sidecar.
