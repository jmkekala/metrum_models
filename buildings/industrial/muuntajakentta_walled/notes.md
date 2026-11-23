# muuntajakentta_walled

## Style brief

The walled transformer yard (*muuntajakenttä*) of a small Nordic town's
coal-fired heat and power plant, 1950s–60s. It is one of five separate
pieces of one plant, with the boiler and turbine hall, the brick chimney,
the coal reception and the office. The pieces stand apart on the lot and
nothing joins them: this asset has no ground slab shared with the others,
and no cables or busbars leave its compound.

A compound of 20.0 × 12.0 m behind a plain industrial perimeter wall,
1.56 m of brick with a thin light coping and plain piers at the corners,
the gate and every 4–6 m, low enough that the plant inside reads over it.
A painted sheet-steel double gate with a high-voltage warning plate closes
the front. Inside, from the incoming (west) side:

- a galvanised lattice portal 10.9 m tall: two tapering square columns of
  four corner angles braced on every face, each rising into a lattice
  shield-wire peak with a finial, and a box truss between them, a
  suspension string hanging from it over each of the six phases;
- for each transformer, a switchgear bay, the yard's "forest of
  insulators": a disconnector with six post insulators on a tall table on
  two lattice legs, three minimum-oil breaker poles (brown porcelain columns with
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
outer planes, so the wall stops on it. Its two yard walls carry what a
plant room's yard side has: the cable trenches meeting the wall under
galvanised cover plates, an unlit wall-mounted yard lamp and a small blue
enamel number plate.

The asset is generic and stands for no particular installation. It carries
no words, brands or logos. The warning plates are a plain yellow triangle
with a lightning arrow, and the number plate a plain numeral 1.

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

- **Yard wall:** 0.24 m thick, 1.5625 m high (20 courses) with its
  0.078 m (one course) coping, on a 0.3125 m (4 courses) concrete footing.
- **Piers:** 12 of them, 0.36 m square, standing 0.02 m over the wall's
  coping (1.58 m), with no caps. There is one at each free corner, one each
  side of the gate, one
  where the east run meets the house's north wall, and between: one on the
  front run (5.4 m bays), one on the west (5.8 m), three on the north
  (4.9 m) and one on the east (3.9 m).
- **Brick module:** the catalog's (`scripts/brickwork.py`), as the plant
  hall's: every brick-bound height on a 0.078125 m course line, every
  opening's sides on a half stretcher in the U its wall samples, and the
  bond turning a half stretcher at the house's four corners
  (`brick_problems()`). The piers' 0.36 m and the wall's 0.24 m are kept
  (one and a half bricks and one brick, as built); the bond runs on round
  the piers in the wall's band.
- **House:** its front wall stands in the yard wall's outer plane, y −5.94,
  and its east wall in the east wall's, x 7.94. The piers stand 0.06 m
  proud of both planes.
- **Gate:** in the front wall between piers at x −0.93 and 2.805, with
  3.375 m clear between them (x −0.75 to 2.625, on half stretchers). The
  leaves are 0.06 m thick, set 0.08 m behind the wall's outer face, and
  run from 0.04 to 1.52 m high.
- **Transformer plinths:** 4.40 × 3.40 × 0.30 m, centred on x −2.00 and
  y ±2.70.
- **Fire wall:** x −3.80 to −0.20, 0.30 m thick on y 0, 3.80 m high.
- **Switchgear bays:** centred on y ±2.70, phases 1.00 m apart (y ±1.70,
  ±2.70, ±3.70); every frame runs 1.35 m either side of the bay's centre
  line. Disconnector posts at x −9.30 and −8.70 on a deck x −9.45 to
  −8.55, 4.20 m up; breaker poles on x −7.00, on a stand 2.00 m up;
  current transformers on x −5.30, on a table 2.20 m up.
- **Gantry:** columns at x −10.60, y ±4.60, on 0.80 m square concrete pads,
  0.64 m square over the pads tapering to 0.40 m at 9.70 m. The finials'
  tips at 10.90 m are the highest point.

The pivot is at ground level, centred on the plan's bounding box, which is
the compound's centre. It is taken from `LOD0` and applied to every tier.
Every tier has the same plan bounds, including `LOD2` and `LOD3`, whose
pier-thick wall keeps the piers' outer faces (Construction).

The facts sidecar's `footprint` is the house alone, since CLAUDE.md's
footprint leaves out fences (Export). In the glTF frame (metres, +Y up, +Z
front, origin at the pivot) the house is the rectangle x 4.94–9.94, z
1.94–5.94.

## Story height

**One storey, 3.203 m** (41 courses) from the ground to the roof slab's
underside line, 3.453 m to the slab's top, over a 0.391 m (5 courses)
concrete plinth. This is inside the 3.0–3.3 m band. It is a plant
room, not a habitable floor, and its height carries the high louvres over
the switchgear cubicles.

## Door leaf height

**Steel door leaf 1.00 × 2.125 m**, with no fanlight or transom. The pressed
steel frame adds 0.0625 m at the sides and head, so its opening in the
brick is 1.125 × 2.1875 m (9 half stretchers by 28 courses). The threshold
is at ground level and the door faces the street (−Y); the reveal's 0.02 m
concrete floor slab (Construction) is a floor finish, not a step. It is the
house's only door.

The gate (two leaves, 3.375 m clear, 1.48 m high) is not a door in the
facts schema: it opens onto the open yard, not an occupied space. It reads
at the scale of the 1.56 m wall it closes, under the 2.0–2.4 m band.

## Window sills

n/a: the house has no windows. It has five steel louvres, 0.875 × 0.50 m
in the clear, each in a 0.0625 m frame, so 1.0 × 0.625 m in the brick (8
half stretchers by 8 courses):

- **High louvres:** sill 2.328 m, head 2.828 m (frame 2.266–2.891 m, 29–37
  courses). One is on the front, two on the east wall and one on the north
  (yard) wall. Their heads stay 0.31 m under the slab, and their sills are
  0.20 m over the door's leaf.
- **Low louvre:** sill 0.531 m, head 1.031 m (frame 0.469–1.094 m, 6–14
  courses), on the west (yard) wall, the intake under the high outlets.

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

- on `LOD0` and `LOD1`, the wall as separate lengths between piers, 0.24 m
  thick and 1.5625 m high, each running 0.05 m into the pier at either end
  and standing 1 mm off the ground (`between_piers()`);
- 12 plain piers, 0.36 m square, standing 0.02 m over the coping;
- the gate, as one 0.06 m plate whose ends run 0.05 m into its piers
  (through `LOD2`; on `LOD3` it stops 4 mm short of the runs' ends and
  touches nothing, so the union cuts no holes in them).

With the piers proud of the wall's top and the lengths clear of the
ground, no face of a length is coplanar with a pier's, so the union cuts
one clean rectangular hole in each pier side it enters. Threading the
piers onto four long runs flush top and bottom split every pier's top and
foot along the run and cost 162 more triangles per tier. The 1 mm under
each length is the piers' and the gate's foot, invisible at any distance.

Every face is closed, both faces of the wall and its top included. The
gate's east pier stands against the house's front-west corner and runs
0.045 m into it. The east run ends inside a pier that runs into the house's
north wall, so no face of the wall is left coplanar and open against the
house. The piers' faces take the wall's band, so the footing, the brick
and the thin coping run round them.

The height was chosen from renders at the catalog camera and at 30 m eye
level: at 1.55 m (now 1.5625 m, on the course grid) more of the
transformers' tanks and the switchgear's
stands show over the front wall, and the yard reads as plant behind a
wall rather than a walled garden. Lower would no longer read as a
security wall round high-voltage plant. Coal fines
darken the wall's foot (Texture set, Weathering), which sets it back
further at play distance.

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

The door's reveal stands on a concrete floor slab on `LOD0` and `LOD1`
(Door floor slab below).

Every opening's casing is on the brick module: its sides on half
stretchers in its wall's U (`HOUSE_U_OFF`: front 0, east 5.125, north
9.0, west 14.125, each a half stretcher, chosen so the bond turns a half
stretcher at all four corners), its head and foot on course lines. The
door is centred at s 1.3125 on the front wall, the louvres at s 3.50
(front), 1.25 and 2.75 (east), 1.375 (north) and 2.00 (west).

The yard walls (north and west) carry painted fittings on the house band,
at U values that map onto those walls only (`paint_house_fittings()`):

- a galvanised cover plate, 0.68 m wide and up to 0.50 m, where each cable
  trench meets the wall, bolted, with two cable glands;
- a yard lamp on the west wall, over the south trench: a wall plate, a
  short arm and a dark conical shade, its rim 2.70 m up, the white enamel
  reflector showing under it. It is paint, not emission;
- a blue vitreous enamel number plate, 0.22 × 0.16 m, at 1.62 m on the
  north wall, white border and a plain numeral 1.

### Door floor slab

The door stands on the ground in a 0.12 m reveal that had no upward face
under it (the house's floor cap faces down), so a consumer's terrain showed
inside, across the foot of the door. The reveal is floored with a concrete
slab from the shared `scripts/door_floor.py` (`build_item()` calls
`door_floor.recess()`; `floored()` decides the tiers):

| Tier | Recess | Slab, width x depth |
| --- | --- | --- |
| `LOD0` | the leaf's, inside the flush casing ring | 1.0 x 0.12 m |
| `LOD1` | the casing's rectangle | 1.125 x 0.12 m |
| `LOD2`, `LOD3` | none: the door is painted flush | none |

- **Top 0.02 m over the ground** (`door_floor.T`), clear of terrain at
  z = 0 and too low to read as a step.
- **A nosing on the wall plane** between the recess's jambs. Nothing
  projects past the wall, so the bounds, the pivot, the footprint and the
  door's threshold in the sidecar are as they were.
- **The reveal starts on the slab's top:** the cheeks and the leaf begin at
  z 0.02. On `LOD1` the wall's notch carries the nosing's two top corners
  (`door_floor.notch()`); on `LOD0` the casing ring's two jambs do, each a
  five-cornered face, and the wall's notch round the casing is unchanged.
  Wall or ring, nosing, slab and cheeks meet on shared vertices, and under
  the nosing the floor cap runs straight along the wall line instead of
  round the reveal. The door's artwork keeps its place, so the slab covers
  the bottom 1.3 px of its dark threshold bar.
- **Its own atlas region** (Texture set), sized to `LOD1`'s casing width;
  `LOD0`'s narrower slab samples its middle 1.0 m (`u0` at the casing's left
  side), so both tiers share it.

`check_layout()` adds `door_floor.problems()`: the region the casing's
width and the reveal's depth, under a door at grade.

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
  aluminium terminal, the tip at 3.95 m; on `LOD3` each a 3-sided pyramid
  standing 4 mm over the cover to the same tip, touching nothing
  (`pyramid()`);
- **cable box:** on the east end.

The sheds, fins, bolts and valves are texture.

`check_layout()` keeps the following clear:

- the turrets inside the cover;
- the conservator clear of the bushings;
- the radiators 0.8 m clear of the fire wall;
- the fire wall 0.5 m past both tank ends and above the conservators;
- the plinths clear of the yard wall and 2 m from the house.

### Gantry and strings

A galvanised lattice portal, as every period yard built them. The catalog
is opaque, so the lattice is real geometry, built lean: every corner
angle, chord and bracing bar is its own closed solid, stopping 4 mm
(`G_GAP`) short of whatever it meets, and bars crossing in a face are cut
back so they never intersect. Exact-boolean intersections between bars
would multiply triangles, so only the columns' corner angles go into the
union (into their pads); the bracing, the truss's chords and the finials
join the mesh after it, and `build_lod()` asserts with a BVH overlap test
(`touching()`) that none of them comes within 1 mm of another shell. The
validator's welded-manifold check passes with them on every tier.

- **Columns:** four corner angles each (a right-triangle hull, 0.08 m
  legs), 0.64 m square over the 0.30 m pads tapering to 0.40 m at 9.70 m,
  then converging up the peak to 0.22 m at 10.50 m. On `LOD0` every face
  has a rail at 11 panel points (0.86 m apart, the top one level with the
  truss's top chord) and one diagonal per panel, the faces' diagonals
  alternating; the peak has one diagonal up to a rail at 10.10 m. Bracing
  angles are triangular prisms, a 0.05 m flange in the face and a
  0.035 m toe.
- **Finials:** a cap plate over the legs' tops and a pyramid spike to
  10.90 m for the shield wire.
- **Truss:** a box of four chord angles (0.07 m legs), 0.60 m deep
  (z 9.00–9.60) and 0.41 m wide, as wide as the columns at its
  mid-height, stopping short of the columns' inner faces. Its sides are an
  18-panel Warren zigzag with end posts; its bottom has a rail under each
  string and at mid-span with a diagonal per panel; its top the same
  zigzag between end rails.
- **Strings:** one over each switchgear phase, at y = ±2.70 and
  ±2.70 ± 1.00, hanging 0.85 m from 4 mm under the truss's bottom rail.
  Each has a cap, four discs of r 0.125 m at a 0.146 m pitch, and a clamp.

By tier:

- **`LOD1`:** legs on every face with a zigzag of diagonals between 7
  panel points (no rails), the truss's chords and 10-panel side zigzags,
  and a bottom rail under each string. Same outline, a coarser web.
- **`LOD2`:** the corner angles, the chords and a plain spike finial; no
  bracing (Per-tier triangle counts).
- **`LOD3`:** slim solids with the lattice painted on (`paint_lattice()`):
  each column one tapered square solid 0.42 of the lattice's width (0.27 m
  at the foot, 0.17 m at 9.70 m) with a pyramid peak to 10.90 m, and the
  truss one box 0.18 m wide and 0.21 m deep on the lattice's mid-height.
  The painted members are galvanised on a lighter grey (`ID_LAT_GAP`) that
  stands for the openings against the sky. `LOD3`'s strings are 3-sided
  pyramids from 4 mm under the slim truss to the clamp's height, touching
  nothing (4 triangles each).

### Switchgear

One bay per transformer, on the transformer's centre line, phases 1.00 m
apart across Y. West to east, with a walkway of 0.75–1.4 m between parts:

- **Disconnector:** a galvanised deck 0.90 × 2.70 × 0.15 m, its top at
  4.20 m, on two 0.24 m square legs, solid posts with a lattice painted on
  every face (`DIS_LAT_R`: corner angles, a rail at ten panel points and a
  zigzag of diagonals over a dark grey for the shade inside), so they
  read as the gantry's kind of steelwork; on it six post insulators in
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

Each turned part is an 8-, 6-, 5- or 4-sided prism by tier; the sheds are
texture. Every turned part of 4 sides or more shades smooth on its steep
bands (`lathe()`, `SMOOTH_SIDES`), so a porcelain column reads round on
every tier; its caps and flat steps (a head's top and foot) stay flat.

`LOD3` keeps the breaker poles, each one 3-sided prism from the ground to
its top head (`poles3()`), its stand painted at its foot on a strip of its
own (`POLE3_R`, 32 px/m along V), and the disconnector tables
(`dis3()`): each deck a 3-sided prism along the bay (its top the deck's,
its undersides meeting on its centre line), on two 3-sided legs with the
painted lattice that stop 4 mm under it, touching nothing. The posts,
breaker stands and current transformers go.

### Conductors

Flexible conductors as thin closed tubes (r 0.025 m) through points on a
parabolic sag, rings square to the local tangent, both ends buried in the
parts they join. Per phase:

- **drop:** from the string's clamp at 8.19 m down to the disconnector's
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
- the door's floor slab region is the casing's width and the reveal's
  depth, and the door stands at grade (`door_floor.problems()`);
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
| `LOD0` | 8,794 | 12,000 | everything; the lattice portal braced on every face (rails and a diagonal per panel), its truss a Warren zigzag on the sides with rails and diagonals top and bottom; turned disc strings (6 sides); 8-sided breaker poles and current transformers, 6-sided disconnector posts with caps and blades; conductors 4-sided, 6 segments on the drop and 4 on each span; 8-sided bushings and conservators; the wall as lengths between piers; house openings as casing rings round recesses |
| `LOD1` | 3,938 | 4,000 | the lattice coarser: legs and one zigzag of diagonals per face over 6 panels, no rails, the truss's sides a 10-panel zigzag and a rail under each string; strings as plain 4-sided prisms carrying the discs in paint; poles and current transformers 5-sided, the current transformers without the base step, posts 3-sided tapers with no caps, no blades; conductors 3-sided, 3 segments on the drop and 2 on the spans; bushings 5-sided turret and one taper; conservators 6-sided; openings one recess each |
| `LOD2` | 1,476 | 1,500 | the wall one pier thick, the piers folded in; the lattice's corner angles and chords alone, a plain spike finial; poles and current transformers 4-sided single tapers carrying heads and bases in paint, posts 3-sided, no breaker cabinet; only the six drops kept, straight; strings 3-sided, bushings (one taper) and conservators 4-sided, the conservators' saddles gone and each drum a box down into its cover; openings flush; coplanar boolean splits dissolved |
| `LOD3` | 494 | 500 | the switchgear goes but for the six breaker poles, each one 3-sided prism from the ground, and the two disconnector tables, each deck a 3-sided prism on two 3-sided legs; the gantry slim solids with the lattice painted on; the strings 3-sided pyramids; the bushings 3-sided pyramids over the covers; every one of those touches nothing, nor does the gate, which stops 4 mm short of its runs; conductors go; both radiator banks one box through the tank; cable boxes and pads go; trenches go; the house's two yard-side louvres go |

The door's floor slab (Construction) costs 4 triangles, the nosing and the
top, on `LOD0` and `LOD1`; `LOD2` and `LOD3` have no recess and are the
same files as before it. `LOD0` is still 8,794: the slab's 4 and the ring
jambs' extra corners are offset in the house's own triangulation, the
floor cap no longer detouring round the reveal (measured on the export,
not broken down further). `LOD1` rose
by 2, to 3,938.

Where `LOD0`'s triangles go, measured by building each group alone (with
the union inside the group) and by leaving groups out of the union:

| Group | Triangles |
| --- | --- |
| Gantry lattice | about 2,320: the bars joined after the union 2,212 (columns' bracing about 1,600, truss chords and bracing about 570, finials 44, each bar 8 triangles), the eight corner angles 112 |
| Gantry pads and strings | about 1,260, nearly all in the six turned strings (200 each) |
| Switchgear, both bays, with their unions | about 2,480 (2,136 before the union: 6 poles about 124 each, 12 posts 44 each, 6 current transformers 92 each, frames and blades) |
| Conductors, 24 of them, with their unions | about 1,190 (960 before) |
| Each transformer | about 440 |
| Yard wall, 12 piers and gate | 364 |
| House | 164 |
| Trenches and fire wall | 52 |

The lattice is the pass's main cost: `LOD0` rose by 1,938 triangles, the
lattice's 2,320 less the solid portal's columns, peaks and I-beam, and
less 162 saved on the wall by building it as lengths between proud piers.
Bars joined after the union add exactly their own triangles; every
intersection between them would have added more.

### What `LOD1` traded for its lattice

The coarse lattice costs 780 triangles (668 in bars, 112 in legs); the
gantry and strings went from 392 to 908. `LOD1` had 240 to spare, so it
paid with:

- the wall as lengths between proud piers: 162;
- breaker poles and current transformers 6- to 5-sided: 140;
- bushings 6- to 5-sided: 48;
- strings from 6- to 4-sided prisms: about 48.

At 35–70 m a 5-sided pole and a 6-sided one have the same outline and
shading within a pixel; the painted discs carry the strings.

### `LOD2` and `LOD3`

`LOD2` keeps the lattice's 8 corner angles and 4 chords (156 triangles)
and no bracing; the budget, 20 under its ceiling, has no room for a
diagonal per panel. Slim solid columns and truss with the lattice painted
on were tried first at `LOD2`, at the lattice's full width and at about
half of it. Both read as a heavy grey frame against `LOD1`'s open web at
65/75 m, and the legs-only frame pops least (LOD review). `LOD3` takes the
painted slim solids (40 triangles with the truss): at 120 m and beyond the
lattice's members are under a pixel and a thin solid reads as the
portal's outline. Its truss is 0.21 m deep, a continuous thin line at
125 m; at 0.33 m it read as a dark bar heavier than `LOD2`'s chords, its
sides being in shade under most sun directions.

`LOD3` keeps the yard full of switchgear at the consumer's 160 m switch
by building what it keeps as separate closed solids that touch nothing,
so the union cuts nothing: the bushings were 3-sided tapers cut into the
covers (76 triangles for the six) and are 3-sided pyramids standing 4 mm
over them (24); that and the gate stopping 4 mm short of its runs (about
16 fewer) paid for the two disconnector tables (24 each: a 3-sided deck
prism on two 3-sided legs) and the six strings as 3-sided pyramids (24).
494 of 500.

**Comparison with the catalog.** `LOD0` is well above the small brick
buildings (`nostokonehuone_brick` 540, `kaivoskonttori_brick` 896) because
the yard is mostly equipment, not wall plane: the switchgear's 18 turned
parts per bay, the 24 conductors and the lattice portal are the asset. It
is under three quarters of the ceiling. The strings and the switchgear's turned profiles are where
triangles buy silhouette below the relief threshold: at 20–35 m a pole
reads by its two stepped heads and a string by its scalloped outline.
Trim in CLAUDE.md's sense (the piers, the house's slab edge and the
trench covers) is under 500 triangles.

**Every tier from `LOD1` down sits near its ceiling** (`LOD1` 62 to
spare, `LOD2` 24, `LOD3` 6), so any change to them must be recounted. The
union costs more than the parts here: every conductor end, post foot and
leg cuts the face it enters. Thinning the posts to 3 sides, the spans to 2
segments and the bushings to one taper paid for `LOD1` before the lattice,
and the trades above for the lattice; the pier-thick wall, the one-taper
bushings and dropping every span but the drops paid for `LOD2`. `LOD3`'s
pointed peaks pay for its conservators' boxes; the six poles cost 48, the
two tables 48, the strings 24 and the bushings 24.

## LOD review

**The consumer's switches**, by its screen-size measure at 1080p and a
75° vertical FOV, fall at about 1.8, 4 and 8 times the largest bounds
dimension (20.0 m): **36, 80 and 160 m**. The 2026-11-22 pass reviewed
the tier pairs there (`review/older_audit_2026_11_22/fix_industrial_b2/
muuntajakentta_walled/`: `renders_before/` from the copy in `before/`,
`renders_after/`, before-above-after sheets in `compare/`, `LOD0` at 20
and 35 m in `compare_lod0/`), with the audit's camera (front 10° up,
corner 45° round and 25° up, eye level at 1.7 m), noon:

- **36 m (`LOD0`→`LOD1`):** the 5-sided porcelain poles and current
  transformers no longer turn pale and streaked at eye level: every turned
  part of 4 sides or more shades smooth, so at `LOD1` they keep `LOD0`'s
  dark red-brown. Pixels differing by more than 24 levels fell from
  1,272 / 1,699 / 1,710 (front / corner / eye) to 1,229 / 1,292 / 1,105;
  what is left is the lattice's thinner web, unchanged by design.
- **80 m (`LOD1`→`LOD2`):** unchanged by the pass (339 px over 24 in the
  corner view, from 439, with the smooth shading). The piers' 0.06 m
  returns still fold into the pier-thick wall: 0.5 px at 80 m, and `LOD2`
  has 24 triangles to spare, so they are neither kept nor painted (a
  painted pier line would need a band of its own: the wall's band is
  shared by every run at every tier, and the atlas has no free rows).
- **160 m (`LOD2`→`LOD3`):** the yard no longer empties: the disconnector
  tables stand on their legs and the strings hang from the truss, as on
  `LOD2`; the current transformers, the posts, the drops and the trench
  covers still go. Over 24 levels: 131 / 307 / 167 px before, 74 / 213 /
  124 after.

The earlier passes' review, at the catalog defaults (35, 70 and 120 m):

The review camera was perspective, 1920×1080, 50° vertical FOV, with
distance measured along the view to the visible front or rear wall
(`scripts/review_asset.py`). Rendering was Cycles at 24 samples with
denoising, AgX, exposure 0. Pairs compared:

- `LOD0`/`LOD1` at 30/40 m, front and oblique, noon and reverse sun;
- `LOD1`/`LOD2` at 65/75 m, front, oblique and rear, noon;
- `LOD2`/`LOD3` at 115/125 m, front, oblique and aerial, noon and reverse.

Every working render is in the local, untracked
`review/power_plant_polish_2026_11_21/muuntajakentta_walled/` (the lattice
pass: `before/`, `after/`, `compare/`, `mip4/`), with the earlier passes'
in `review/power_plant_rev_2026_11_21/` and `review/power_plant_2026_11_21/`.

- **`LOD0`→`LOD1`:** the gantry's lattice loses its rails and half its
  diagonals but keeps its corner angles, chords, finials and a zigzag on
  every face, so at 30–40 m both read as braced lattice of the same
  outline; the strings lose their modelled discs and keep them in
  paint; the disconnector posts lose their caps and blades; the poles and
  current transformers go from 8 to 5 sides; the conductors lose
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
  The gantry keeps its outline as the lattice's corner angles and chords;
  its bracing goes. At 65 m a bracing bar is about 1 px and `LOD1`'s
  columns read as a light, faintly crossed web; `LOD2`'s as four thin
  rails. Blinked, the columns lighten slightly but neither the silhouette
  nor the tone jumps. Slim painted solids tried here read as a heavier
  grey frame and popped more (Per-tier triangle counts). The openings go
  flush.
- **`LOD2`→`LOD3`:** the switchgear cannot fit in 500 triangles, and with
  it simply dropped the whole west half of the yard emptied at 120 m: an
  identity change. `LOD3` therefore keeps the six breaker poles as single
  3-sided prisms from the ground (`poles3()`), their stands painted grey
  at the foot and their red-brown heads painted on a strip of their own,
  48 triangles. The gantry becomes slim solids with the lattice painted
  on; at 115/125 m its columns and truss stay thin continuous lines of
  the lattice's outline and tone, the peaks pointed. The transformers'
  bushings stay, as 3-sided pyramids. The poles keep the bays' verticals
  and red heads, and since 2026-11-22 the disconnectors' tables and the
  strings stay too (Per-tier triangle counts); the current transformers,
  posts and drops go. The trench covers go too. The radiator banks become one box, keeping their
  outline. The gantry, tanks, conservators, fire wall, wall, gate and
  house keep their silhouettes on every tier.
- **Bounds:** every tier keeps the 20.0 × 12.0 m plan bounds and the
  pivot. The 10.90 m height is the gantry's finials, kept on every tier.

The six working views (`review_asset.py --six-views`: orthographic front,
rear, both sides, top and a raised aerial) were looked at for `LOD0` and
`LOD3`, with the reference set beside them for proportion. The top view
shows each phase running straight from its string through disconnector,
breaker and current transformer to its bushing, converging on the
bushings' closer spacing; the aerial shows the switchgear and gantry well
over the 1.56 m wall. The lattice pass's six views at all four tiers,
20/30 m eye-level and oblique views and the three LOD pairs were rendered
before and after with identical settings, with sheets from
`scripts/review_compare.py` in its `compare/`.

**The door's floor slab (2026-11-23)** adds no transition of its own. It
goes with the door's 0.12 m reveal at the `LOD1`/`LOD2` switch, where the
door is already painted flat: a 0.02 m nosing and 0.12 m of slab are under
a pixel at 70 m and at the consumer's 80 m. Between `LOD0` and `LOD1` the
slab widens from the leaf's 1.0 m to the casing's 1.125 m with the recess,
as the recess itself does. Checked from a standing eye (1.7 m, 75° vertical
FOV, 1280 × 720) and from 0.35 m over a terrain plane at z = 0, 1–4 m from
the door, face-on, from both sides and from above, noon and reversed sun,
every tier (Review status).

Pending in the consumer: real LOD switching, shadows in the yard and
performance.

## Interior geometry

The validator's hidden-surface test reports 19 of 8,794 triangles at
`LOD0` (1.4 m² of it vertical), 4 at `LOD1`, 2 at `LOD2` and 15 at `LOD3`
(0.6 m² vertical), all PASS. `LOD3`'s are its separate solids' faces
that look into their 4 mm gaps: the bushing pyramids' bases over the
covers, the strings' tops under the slim truss, the disconnector legs'
tops under their decks, and the gate's two ends against its runs; each
closes its solid and is kept. The rest, listed face by face from the
exported tiers:

- **The tank strips** (every tier): the strips of each tank's long sides
  under its radiator banks, between the plinth's top at 0.30 m and the
  banks' undersides at 0.70 m, 0.55 m deep under the bank, and one bank's
  underside. That is exterior surface, visible from low views along the
  plinth, but the test's 40 fixed rays from each face's centre all strike
  the bank or the plinth.
- **The strings' top caps** (`LOD0` only, 15 faces of about 0.001 m²
  each): each string hangs from 4 mm under the truss's bottom rail, so
  the rays from its top cap all hit the rail. They close the string's
  solid and are kept: the lattice's bars and the strings touch nothing,
  which is what keeps the union from cutting them.

What is removed and kept:

- No interior is modelled. The house is one closed solid, so its floor
  and roof are its caps and it has no room.
- The union removes every buried face: the tank's base in the plinth, the
  banks' and cable boxes' backs, the bushings' and saddles' feet, the
  conservator boxes' feet in the covers (`LOD2`, `LOD3`), the corner
  angles' and the slim columns' feet in their pads, the switchgear's legs
  in their decks and its posts, poles and current transformers in theirs,
  the conductors' ends, the wall lengths' ends in the piers and the
  house, and the trenches' ends.
- The closure faces kept are the floor faces on the ground under the
  piers, house, plinths, pads, legs, fire wall and trenches (the house's
  runs straight along the front wall line under the door's floor slab, so
  no face lies at grade inside the reveal; the slab is exterior surface and
  adds no face inside the shell), the wall
  lengths' undersides 1 mm over the ground, and every lattice bar's own
  faces where it stops 4 mm short of the bar or angle it meets.

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
  carry no secondary wiring. The breaker stands are plain galvanised
  boxes; the disconnector tables' legs are solid posts with the lattice
  painted on, so they cast solid shadows.
- **Conductors:** thin closed tubes on a parabolic sag, with no clamps or
  spacers. Nothing runs between the gantry and the world outside: the
  beam carries strings but no incoming line, and the portal stands for the
  yard's incoming side without wiring it to anything outside. The
  transformers' low-voltage side is the cable box and trench to the house,
  with no cables modelled.
- **Lattice:** the gantry's angles and bars are closed prisms (triangular
  hulls) with no bolts, gussets or gusset plates, and every joint is a
  4 mm gap rather than a connection; the gaps are under a pixel from 5 m
  on. `LOD2` drops the bracing and `LOD3` paints it.
- **One door and no yard door:** the house has no door into the yard, and
  the yard's only way in is the gate. The house's door is on the street.
- **Floors:** only the door's reveal has one, a flat concrete slab with no
  mat, drain or threshold strip (Construction). The gate stands in the
  wall's thickness on the consumer's ground, as the yard does.
- **Yard lamp, number plate and trench cover plates are paint** on the
  house's yard walls, flat to the wall; the lamp is unlit (Night
  lighting). No signage text, fence wire or barbed wire.
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
| 0–248 | HOUSE band | U along the wall, V = height, 64 px/m; concrete plinth to 0.391 m (5 courses), then the catalog's stretcher bond (`scripts/brickwork.py`); on the yard walls' own U ranges the trench cover plates, the yard lamp and the number plate (`HOUSE_U_OFF`) |
| 252–384 | FENCE band | U along the wall, V = height; concrete footing to 0.3125 m, brick, the thin precast coping one course tall, 1.484–1.5625 m; the piers' faces too (their 0.02 m over the coping samples the coping's top row and the padding above it) |
| 390–558 | unique, row A | tank side, gate, door, the door's floor slab, radiator face and end, conservator barrel, gravel bed |
| 566–734 | unique, row B | tank cover, roof, slab edge, radiator top, louvre, bushing, string, cable box, conservator end |
| 740–1016 | unique, row C | flat patches (the breakers' head paint among them), breaker pole, disconnector post, current transformer, `LOD3`'s whole-pole strip (32 px/m in V), `LOD3`'s painted lattice (a column face, the truss's sides, its top and bottom), the disconnector legs' painted lattice, the fire wall's board-marked concrete (also the current transformers' tables), the trench covers |

### Deviations from 64 px/m

- **Gravel bed on the plinths' tops:** 40 px/m.
- **House roof:** 32 px/m. Both are horizontal surfaces of low-contrast
  gravel and felt, seen from above at a distance.
- **Gantry lattice (`LOD0`–`LOD2`):** every bar takes the flat
  galvanised patch, as do the switchgear's steel and the conductors their
  aluminium patch.
- **`LOD3`'s painted gantry:** a column face's region is 40 px across
  whatever the face's width and 17.9 px/m up (`COL_LAT_R`); the truss's
  sides and top 40 px/m along it, its depth and width across the region
  (`BEAM_LAT_R`, `BEAM_TOP_R`). Members are painted about a pixel wide,
  seen only from 120 m on.
- **Disconnector legs:** 24 px across a 0.24 m face (100 px/m) and
  32 px/m up (`DIS_LAT_R`), members 2.6 px.
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
- form-tie holes −10 mm;
- the door's floor slab's pores, 0.4 mm.

### The door's floor slab

`FLOOR`, 72 × 8.96 px at (414, 544), in the free rows between the door's
region and row B, at 64 px/m (`scripts/door_floor.py`): the slab unfolded,
U along the wall from the casing's left side across its 1.125 m, V the
nosing's 0.02 m (1.28 px) and then the top from the wall plane to the leaf.
`LOD1` samples all of it, `LOD0` the middle 64 px. Painted by
`door_floor.paint()`, `grain()` and `weather()`, as the catalog's other
entrance slabs are: float-finished cast concrete, `ID_FLOOR`, sRGB
**(132, 130, 124)** in every variant, roughness **0.88**, nonmetallic.
Occlusion deepens toward the jambs and the leaf (within 0.048 m), a
slightly paler path is worn toward the leaf, the pores are the concrete's
noise at 5 % shade and 0.4 mm of height, and blotchy trodden-in dirt lies
over it. The region bleeds 2 px into its gutter. On `LOD0` the jambs'
occlusion is fainter than on `LOD1`, the region's edges being under the
casing ring.

Adding it changed only that free strip: the albedos and the ORM differ
from the previous bake only in x 389–517, y 531–563 (the slab and the
padding round it, which now carries the slab's edges instead of the door's
and row B's), the normal map only in x 412–487, y 542–554 (working diff in
`review/review_2026_11_23/muuntajakentta_walled/`, not committed).

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
- **coal fines on the yard wall:** a grey-black film thrown up along its
  foot, strongest at the footing and fading by 1/e every 0.45 m up, and a
  light patchy film above it and on the coping (`scripts/weathering.py`'s coal channel), so the
  wall sits back behind the plant;
- **gate and door:** kicked dirt at the foot, grime at the hasp and handle,
  a little rust at the gate's foot;
- **transformers:** runs down the tank sides, dust on the covers,
  radiator tops and conservators, rust at the base frames and the
  radiators' lower headers;
- **switchgear:** dust on the breakers' and current transformers' heads,
  runs down the breakers' mid heads, a trace on the porcelain;
- **ground surfaces:** dust and oil on the gravel and curbs, dust on the
  trench covers;
- **steel and porcelain:** light dust on the zinc (the galvanised patch
  and the painted lattices), a trace on the porcelain;
- **slab edge:** runs down it from the felt;
- **the door's floor slab:** trodden-in dirt.

### Filtering and inventory

Whole-atlas mip4 stress renders (`scripts/review_atlas_mips.py`) of `LOD2`
and `LOD3` were checked at 125 m in the first build (aerial, front and 75°
grazing) and again after the lattice pass (front, oblique and aerial),
under noon. They showed no colour leaks between regions and no dark
seams; the brick stayed brick-red, the copings light, the gate dark, the
porcelain brown and the breakers' heads red-brown, and `LOD3`'s painted
gantry stayed a neutral grey line with no brick or porcelain bleeding
into it. The lattice regions sit in row C with at least 8 px gutters.

A later mip review rendered each tier at its switch distance and one level
beyond (`LOD1` 70 m at mip 2–3, `LOD2` 120 m at mip 3–4, `LOD3` 250 m at
mip 4–5), front and oblique, noon and reverse sun, the default and one
contrasting variant, with whole-atlas mips and again at a per-texel level
matched to each tier's texel density
(`review/phase2_2026_11_21/mips/muuntajakentta_walled/`). No gutter leak
shows at any tier's real distance, and the painted lattice strips of
`LOD2`/`LOD3` hold.

- **Porcelain at distance:** under back light the bushings, breaker poles,
  current transformers and post insulators lose their bright shed
  highlights at `LOD1` 70 m and `LOD2` 120 m from mip 2, and read flat
  red-brown. The 30 mm sheds on their 0.07–0.08 m pitch average flat in
  the normal map's mips; a full-resolution normal map restores them, the
  ORM makes no difference. Not an atlas-layout fault: specular
  anti-aliasing is pending in the consumer; a future repaint could lower
  the sheds' contrast or fold some of the glaze into the albedo.
- **Latent, stress renders only:** the wrapped cylinder regions
  (`BUSH_R`, `BREAKER_R`, `POST_R`, `CT_R`, `POLE3_R`) have 8 px gaps and
  leak 27–50 levels across their wrap seams at mip 3–4 (`POLE3_R` 86 at
  mip 5); not visible at 120 or 250 m. Periodic padding in U would cure
  them.

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
- the lattice's painted openings, a light neutral grey (150, 153, 153)
  on `LOD3`'s gantry and a darker shade of it inside the disconnector
  legs;
- the number plate's blue enamel (44, 60, 92) and off-white (196, 194,
  186), the yard lamp's dark paint;
- the board-marked fire wall and tables, the concrete and the gravel;
- the felt roof.

`variants.png` shows the three at `LOD0`, one labelled daylight panel each
from the catalog preview camera; with no emission there is no night row.

## Night lighting

**None. The yard is not night-lit, and it ships no `_emission.png`.** The
house has no glazing, only steel louvres, because an unmanned switchgear
room is ventilated, not lit for the street. CLAUDE.md's Output Contract
allows a building without glazing to ship no emission map. The yard lamp
on the house's west wall is painted only, with no emission; a lit lamp
would be a luminous region the brief does not call for. Consequences:

- **No `emissiveTexture` on any tier.** The validator's emission checks do
  not apply. The facts sidecar omits `textures.emission`.
- **`variants.png` has a day row only**, one panel per colour (Variant
  list).

`build.py` builds through the shared `asset_build.Asset` with
`night_lit=False`, which leaves out only the window wiring:

- `material()` wires no emission mask;
- `export_all()` sets no lit state and rewrites no emission factor;
- `render_preview()` has no emission state to set;
- `render_variants()` renders the day row alone.

The 2026-11-21 revision's full rebuild was the first full export through
that path. It wrote no emission PNG; each tier's one material carries
`baseColorTexture`, `metallicRoughnessTexture`, `occlusionTexture` and
`normalTexture` and no `emissiveTexture` or `emissiveFactor`; and the
build printed "no variants.png: not night-lit" and wrote none; the
day-only sheet was rendered afterwards by `build.py -- variants`, from the
tiers in memory checked against `export/`, with nothing re-exported.

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
  street. It is at [6.2525, 0, 5.94], facing +Z, 1.00 × 2.125 m.

The validator's "doors on the footprint" check fits: the door is on the
house's front edge.

The schema has no place for the compound, so these are recorded here
rather than in the sidecar, in the same glTF frame:

- **Wall line (piers' outer faces):** the rectangle x −10.00 to 10.00, z
  −6.00 to 6.00, 1.5625 m high, the piers 1.5825 m. The house fills its
  corner x 4.94–9.94, z 1.94–5.94.
- **Gate:** its centre on the wall's outer face at [2.9375, 0, 5.94],
  3.375 m clear between its piers (x 1.25–4.625), 1.48 m high, facing +Z.
- **Transformer plinths:** x −2.20 to 2.20, z 1.00 to 4.40 (south) and z
  −4.40 to −1.00 (north), 0.30 m high.
- **Switchgear bays:** on z ±2.70, phases at z ±1.70, ±2.70 and ±3.70.
  Disconnectors on x −7.30 and −6.70, posts' tops 5.15 m; breaker poles
  on x −5.00, tops 5.27 m; current transformers on x −3.30, tops 3.92 m.
- **Gantry:** lattice columns at x −8.60, z ±4.60, truss 9.00–9.60 m,
  shafts to 9.70 m, lattice peaks to 10.50 m and finials to 10.90 m, on
  the −X (incoming) side.

## Review status

Checked here, in Blender:

- `scripts/validate_asset.py`: 0 FAIL and 0 WARN with the sidecar written
  from a committed tree (`build.py -- facts`); straight after a rebuild in
  a working tree its one WARN is `source.dirty`. On every tier the
  validator passes:
  - welded manifold topology;
  - one material and uri-only images;
  - the normal map at scale 1;
  - triangle ceilings;
  - pivot at ground and centred;
  - the hidden-surface test (Interior geometry).

  It also passes the five 1024² RGB PNGs and the facts sidecar's schema,
  hashes, tiers, footprint and door.
- `check_layout()`, with the brick module (`brick_problems()`) and the
  switchgear's and conductors' checks.
- The bindings traced in each GLB: albedo, ORM twice and normal, no
  emission (Night lighting).
- The six working views at every tier.
- LOD pairs around 35, 70 and 120 m from front, oblique, rear and aerial
  views, under two sun directions, before and after the lattice pass,
  with before/after sheets; the `LOD1`/`LOD2` gantry compared with legs
  only and with slim painted solids, the `LOD3` truss at three depths.
- `build_lod()`'s assertion that no lattice bar touches another shell or
  the union, on every tier, and the validator's welded-manifold check on
  the exports with the bars in them.
- Whole-atlas mip4 stress renders of `LOD2` and `LOD3` at 125 m (front,
  oblique and aerial after the lattice pass; grazing in the first build):
  the heads stay red-brown, the porcelain dark brown, the steel grey,
  with no leaks or dark seams.
- The mip review at each tier's switch distance and one level beyond,
  whole-atlas and distance-matched per-texel mips, under noon and reverse
  sun (Texture set, *Filtering and inventory*): no gutter leak at any
  tier's real distance; latent seam leaks on the wrapped cylinder regions
  in the stress renders only; the porcelain's shed highlights lost from
  mip 2 under back light.
- Close renders of the house's yard walls (trench cover plates, lamp,
  number plate) and of the disconnector legs at 20 m.
- The wall at 1.55 and 1.70 m from the catalog camera and at 30 m eye
  level (Construction).
- The day cycle (morning, noon, dusk, night) from the fitted oblique.
- The catalog preview: the fixed camera sees over the low front wall into
  the yard. The lattice gantry, its strings and drops, the switchgear's poles and
  heads, the current transformers, the bushings, conservators and fire
  wall all show over the wall, with the gate and the house's door in
  front.
- The red and brown brick against the plant's shared constants (Variant
  list).
- The plant palette pass: ORM, normal and `yellow_brick` albedo
  pixel-identical to the previous build, triangle counts and bounds
  unchanged; a 35 m oblique noon render of each variant before and after.
- `variants.png`, the three colours in daylight (`build.py -- variants`).

- The 2026-11-22 pass: the tier pairs at the consumer's 36, 80 and 160 m
  and `LOD0` at 20 and 35 m, before and after with identical settings
  (LOD review); the sidecar diffed against the previous one (only the
  door's x, 6.24 → 6.2525, and height, 2.10 → 2.125, the `LOD2`/`LOD3`
  counts, hashes and source moved); the validator, 0 FAIL.

- The door's floor slab (Construction, Revision log), from a snapshot in
  `review/review_2026_11_23/muuntajakentta_walled/before/`:
  - **Door views** (`review/review_2026_11_23/muuntajakentta_walled/
    door_views.py`, every tier, noon and reversed sun, over a green terrain
    plane at z = 0): the door from 4 m and 2 m at eye level, from either
    side, from 0.35 m up and from above, and the yard wall's and the
    house's feet from 0.35 m. Before, grass ran into the reveal up to the
    leaf on `LOD0` and `LOD1`; after, concrete fills it jamb to jamb, its
    nosing a light line on the wall plane with nothing past it, no dark
    seam or stretched texels. `LOD2` and `LOD3`, whose door is flush, are
    the same files as before. Every camera stands outside the compound.
  - **`review_asset.py`** from both: the day cycle on `LOD0`, the six
    orthographic views, and every tier front and oblique at 20, 35, 70 and
    120 m under noon; `review_compare.py` sheets in
    `review/review_2026_11_23/muuntajakentta_walled/compare/`.
  - Bounds, pivot, footprint, storey and the door in the sidecar
    unchanged; `LOD2` and `LOD3` byte-identical. On `LOD0` and `LOD1` a
    downward ray meets an upward face at 0.020 m at 9 of 9 sample points
    of the reveal (none before), no face lies at grade inside it, and the
    only upward faces under 0.1 m near the door are the slab's top.
  - `scripts/validate_asset.py`: 0 FAIL; the one WARN is `source.dirty`,
    the sidecar written from an uncommitted tree, to be rewritten with
    `build.py -- facts` once committed.

Pending here: the six views and the whole-atlas mip review after the
2026-11-22 pass (its texture change is the re-coursed heights, gate and
door, in their own regions).

Pending in the consumer:

- import, orientation and pivot on reimport in the engine;
- LOD switching, shadows in the yard and performance;
- mip and anisotropic filtering of the lattice's thin bars (aliasing and
  shimmer at 35–70 m in motion), `LOD3`'s painted lattice, the radiator
  fins (a 3.2 px period), the porcelain sheds and the brick, under the
  consumer's own mip generator;
- specular anti-aliasing of the porcelain's sheds, whose highlights the
  normal map's mips flatten at 70–120 m under back light;
- shadow-map resolution on the lattice's 0.05 m bars;
- the yard's placement on terrain, with no ground of its own.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`)
throughout. The MCP addon was not used. Texture generation used the system
Python 3 with numpy, scipy and Pillow.

## Revision log

- **2026-11-23 — door floor slab.** The switchgear door's 0.12 m reveal
  had no upward face under it, so a consumer's terrain showed inside, at
  the foot of the leaf. It now stands on a concrete slab 0.02 m over the
  ground, nosing on the wall plane, on its own atlas region, built and
  painted by the shared `scripts/door_floor.py`, on `LOD0` (1.0 m, inside
  the casing ring) and `LOD1` (1.125 m, the casing's recess). Tiers
  8,794 / 3,936 / 1,476 / 494 to 8,794 / 3,938 / 1,476 / 494; bounds,
  pivot, footprint and door unchanged.
- **2026-11-22 — audit fixes.** Re-coursed to the catalog brick module as
  the plant hall was (`brick_problems()`): the yard wall 1.55 → 1.5625 m
  with a one-course coping from 1.484 m (was 1.4875), the gate opening
  3.42 → 3.375 m (x −0.80…2.62 → −0.75…2.625), the house's plinth 0.375 →
  0.391 m, slab underside 3.20 → 3.203 m, the door leaf 2.10 → 2.125 m
  and 1.25 cm east, the high louvres' sills 2.30 → 2.328 m and the low one
  0.55 → 0.531 m, the louvres 0–10 cm along their walls, the east and west
  walls' U a half stretcher on. Every turned part of 4 sides or more shades
  smooth. `LOD3` keeps the disconnector tables and the strings, paid for by
  bushing pyramids and a gate that touches nothing. Triangles 8,794 /
  3,936 / 1,480 / 482 → 8,794 / 3,936 / 1,476 / 494; bounds, footprint and
  pivot unchanged.
- **2026-11-21 — mip review.** The review at each tier's switch distance
  recorded (Texture set, Review status); no asset change.
- **2026-11-21 — lattice pass.** The solid portal became a galvanised
  lattice: four corner angles per tapering column (0.64 to 0.40 m),
  braced on every face, lattice peaks with finials, and a box truss
  between them, every bar a closed solid joined after the union. `LOD1`
  takes a coarser lattice, paid for by the wall built as lengths between
  proud piers and 5-sided poles, current transformers and bushings and
  4-sided strings; `LOD2` keeps the angles and chords; `LOD3` slim solids
  with the lattice painted on, and its transformers' bushings came back.
  The yard wall came down from 1.70 to 1.55 m (piers 0.02 m proud, the
  gate's leaves to 1.51 m) with coal fines at its foot. The house's yard
  walls got painted trench cover plates, an unlit yard lamp and an enamel
  number plate; the disconnector tables' legs a painted lattice. Triangles
  6,856 / 3,760 / 1,448 / 460 became 8,794 / 3,936 / 1,480 / 482. Bounds,
  height (10.90 m), footprint, door and pivot are unchanged. Every PNG,
  GLB, `source.blend`, `preview.png` and the sidecar changed.
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
