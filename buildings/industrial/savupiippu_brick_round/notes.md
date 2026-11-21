# savupiippu_brick_round

## Style brief

A composite free-standing chimney stack (*savupiippu*) of a small Nordic
town's coal-fired heat and power plant of the 1950s–60s. It is one of five
separate pieces of the plant (the boiler and turbine hall, coal reception,
office and transformer yard are other assets). Each stands alone on a lot:
no ground, no flue duct to the hall.

A round, battered stack of dull red radial brick, 46.5 m to its rim, about 2.4
times the boiler house, 4.1 m across at its foot and 2.4 m at its top (top
to foot 0.58). It stands on a massive brick base, 6.8 m square on a low cast
concrete footing, turned to an octagon by sloping brick fillets at its
corners and to the round by a concrete wash. The shaft is plain and runs
straight up to a pale cast concrete head band under a thin steel cap ring,
open at the top round a sooted flue. Soot thickens up the stack's upper
third and is heaviest on the head; three thin galvanised flats ring the top
10 m. A narrow steel service platform with a railing rings the head 1.5 m
under the rim; an iron ladder in a hooped safety cage climbs the back along
the batter from 2.5 m above the base to it, with a copper lightning down
conductor beside it, up to a lightning rod rising a metre over the rim.
Three red aviation obstruction lamps on the head band glow at night. On the base's front, toward the boiler house, is the closed
flue inlet under a concrete lintel; low in its east wall a cast iron
cleanout hatch.

It is the plant's landmark from the play camera: the taper, the base's
fillets, the head band, the platform's deck, the open top and the
lightning rod are geometry on every tier; the ladder and its cage, the
conductor, the railing and the platform brackets are geometry close up,
and the ladder and conductor painted lines beyond 70 m.

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
| Overall | 6.80 × 6.80 × 47.50 m (to the lightning rod's tip; the rim at 46.50 m) |

Nothing stands outside the base: the platform reaches 2.0 m from the axis,
the ladder's cage 2.86 m at its lowest hoop (the base's flat is at 3.40 m),
and the shaft's foot is 4.1 m across.

Heights: footing course 0–0.31 m; square walls to 4.20 m; corner fillets
4.20–5.40 m, where the plan is an octagon 6.8 m across its flats; the
octagon's concrete coping 5.40–5.70 m; the wash rising to the shaft's foot
at 6.20 m. The shaft runs 6.20–44.70 m, its outside radius falling straight
from 2.06 m to 1.19 m (a batter of 2.26 %). The head band, 0.06 m proud,
runs 44.70–46.50 m at radius 1.25 m, its top 0.10 m the painted steel cap
ring; the rim at 46.50 m. The platform's deck is 44.88–45.00 m, to radius
2.00 m; its hand rail's top 46.00 m. The lamps stand 46.06–46.27 m. The
lightning rod stands 46.20–47.50 m on the back, 0.275 m east of the
ladder's axis, its tip a metre over the rim: it sets the height, on every
tier.

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

`build.py` builds the stack as one closed solid directly and adds every
attachment as a separate closed solid beside it, in the same mesh. Nothing
is boolean-cut: each attachment stops `GAP` (1.5 mm) short of the shaft,
the deck, a rail or a hoop, so the shaft's and the rails' faces stay whole
and the kit costs only its own triangles. `build_lod()` tests every pair of
shells (the stack included) for intersecting triangles and refuses the
build if any touch; `to_object()` refuses an open one. The exported mesh is
one object of many closed shells, each welded manifold.

- the base's four square walls, the inlet cut into the front at
  `LOD0`/`LOD1` (0.25 m reveals in brick, a concrete sill and lintel
  soffit, the closure at the back) and painted flush at `LOD2`/`LOD3`; the
  hatch a flush face in the east wall on every tier;
- above them, each wall running on as a trapezoid between the corner
  fillets, the four fillets as sloping brick triangles, and the octagon's
  eight vertical coping faces; the rear wall, its trapezoid and the rear
  coping side split by a 0.19 m strip that samples the conductor's own
  copy of the brick and concrete (Texture set);
- the wash, triangulated between the octagon's head (its corners and the
  points where rays to the shaft's vertices leave it) and the shaft's foot
  ring, whose vertices it shares;
- a surface of revolution: the shaft's ten lifts, the head band's foot
  annulus, the band below the deck, the deck's underside, outer edge and
  top (the platform's deck is the profile's own, so it needs no cut), the
  band above it, the rim, and the flue's lining straight down 1.0 m from
  the rim's inner edge; the flue's floor at 45.50 m, inside the band; the
  base's floor on the ground;
- separate closed solids, each a section swept along a polyline and
  mitred at its bends (`sweep()`), or built directly: the three lamps and
  the lightning rod (every tier), the platform's railing, posts and
  brackets (as far as the tier keeps them), and on `LOD0`/`LOD1` the
  ladder, its cage, the down conductor and the rod's clamp and bracket.

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

A steel service platform 1.5 m under the rim: a 0.12 m deck from the band
out to radius 2.0 m, part of the stack's surface of revolution; a ring
hand rail (top 46.0 m) and knee rail (top 45.5 m), each a triangular bar
0.044 m wide and 0.0375 m deep swept round a polygon of the tier's side
count; six posts at 0°, 60°, … 300° from +X (none at the ladder, at 90°),
standing just inside the rings from `GAP` over the deck to the hand rail's
top; and six brackets from `GAP` off the shaft at 44.1 m to `GAP` under
the deck at radius 1.82 m. Posts and brackets are square bars on `LOD0`
and triangular after. No grating: the deck is opaque. Per tier
(`PLATFORM` in `build.py`): hand rail, knee rail, posts and brackets on
`LOD0`; the same without the knee rail on `LOD1` and `LOD2`; the deck alone
on `LOD3`, so the head's silhouette keeps its flange.

### Access and lightning protection

A continuous iron ladder up the back (+Y), on `LOD0`/`LOD1`, built locally
(`scripts/roof_safety.py`'s kit assumes a vertical wall): two rails
0.05 × 0.07 m, centred 0.22 m either side of the axis and 0.20 m off the
back facet, following the batter in a straight line from 8.70 m (2.5 m
above the wash's top) to `GAP` under the deck, and on from `GAP` over it as
grab handles to 46.0 m; a rung every 0.333 m (108 rungs) on `LOD0`, every
third on `LOD1`, each a triangular bar 0.03 m wide with a flat tread,
stopping `GAP` short of both rails; on `LOD0` ten pairs of brackets
(triangular bars 0.04 m) from `GAP` off the shaft to `GAP` off the rails'
inner faces, at 8.9 m, every 4 m from 12.7 m, and at 44.3 m; none on
`LOD1`, where they are under a pixel.

**Safety cage.** A ladder this tall has a cage from about 2.5 m above its
foot: 21 hoops every 1.65 m along the batter from 11.2 m to 44.2 m (the
top one 0.68 m under the deck), each a flat bar 0.05 m deep and 8 mm
thick (a triangular section, its broad face outward) of four chords in
plan, from `GAP` off one rail's outer face out to 0.35 m either side of
the axis 0.38 m behind the rails and round to a point 0.70 m behind them;
three straps (0.05 m × 8 mm, flat face in) run outside the hoops' corners
and back, `GAP` and a little more off their arrises, the full height of
the cage. `LOD1` keeps every third hoop and the top one (8) and the three
straps. The cage's furthest reach, the back strap at the lowest hoop, is
2.86 m from the axis, inside the base's 3.40 m flat, so it sets no extent.
`LOD2`/`LOD3` carry the ladder as paint on the back facet (Texture set,
*The ladder strips*); the cage is not painted there (its bars are under a
pixel beyond 70 m, and the back facet is too narrow to hold its width).

**Lightning protection.** A copper down conductor beside the ladder,
0.275 m east of its axis: on `LOD0`/`LOD1` a strap 25 mm wide and 12 mm
deep (triangular, flat face in) standing 0.04 m off the brickwork from
6.23 m to `GAP` under the head band, then 0.04 m off the band from its foot
to `GAP` under the deck and from `GAP` over it up to `GAP` under the air
terminal's clamp block at 46.11 m. Down the wash, the rear coping and the
base's rear wall to the ground the conductor is paint on every tier (a
0.19 m strip of the wall, its trapezoid and the coping with their own copy
of the brick or concrete and the strap painted on, and a 2 px line across
the wash), and on `LOD2`/`LOD3` it is paint on the back facet's strip
beside the ladder. Below the ladder's foot (6.2–8.7 m) the far tiers have
no line: that part lift samples the band without a strip.

**Air terminal.** One lightning rod on the strap's line, so the route reads
rod, strap down the band, under and over the deck, down the shaft and the
base. On `LOD0`/`LOD1` (`air_terminal()`, 38 triangles): a square copper
rod, 45 mm at its foot tapering to 26 mm at a shoulder 0.12 m under its
tip and then to a point, from 46.20 m to 47.50 m, its inner face 0.04 m
off the band (the strap's stand-off), so it rises 1.0 m over the rim; a
clamp block 0.07 m wide, 0.09 m tall (46.11–46.20 m), 12 mm to 95 mm out
from the band, between the strap's top and the rod's foot; and a bracket
0.03 m square from the band to the rod's inner face at 46.33–46.37 m,
under the cap ring. Each is its own closed solid, `GAP` clear of the
strap, of the others and of the band, in `build_lod()`'s clash test. The
real rod would be 20–25 mm round; at 45 mm it is about 1.5 px at 50 m with
the review camera. On `LOD2`/`LOD3` a three-sided spike 0.05 m wide at its
foot (46.20 m) to the same tip (4 triangles), floating 0.04 m off the
band without clamp: the rod sets the height, so every tier keeps it and
the bounds are the same on all four. It takes the strap's copper patch.
The rod stands on the back, where the ladder and the strap are; the
lamps are at east, west and front.

### Authored parameters

`facade_atlas.py` holds every shared number: the base (`BH`, `Z_FOOT`,
`Z_SQ`, `Z_OCT`, `Z_CAP`, `Z_SHAFT0`), the shaft (`R0`, `R1`, `SEG`,
`NLIFT`, `Z_LADDER0`, `Z_HEAD0`, `LIFTS`), the head (`R_HEAD`, `Z_TOP`,
`CAP_RING`, `R_FLUE`, `FLUE_DEPTH`), the platform (`Z_DECK`, `DECK_T`,
`R_DECK`, `RAIL_R`, `RAIL_Z`, `POSTS`, `STRUT_*`), the ladder
(`LADDER_HALF`, `RAIL_W`, `RAIL_D`, `STANDOFF`, `RUNG_PITCH`, `RUNG_EVERY`,
`LADDER_BRACKETS`, `BRACKET_EVERY`), the cage (`CAGE_Z0`, `CAGE_PITCH`,
`CAGE_N`, `CAGE_EVERY`, `HOOP`, `HOOP_T`, `HOOP_H`, `STRAP_*`), the
conductor (`COND_X`, `COND_W`, `COND_T`, `COND_OFF`, its strips
`COND_*_R`), the air terminal (`ROD_TIP`, `ROD_FOOT`, `ROD_W`, `ROD_W_TOP`,
`ROD_POINT`, `CLAMP_Z`, `CLAMP_W`, `CLAMP_OFF`, `ROD_BRACKET_Z`,
`ROD_BRACKET_W`, `SPIKE_W`), the attachments' clearance `GAP`, the lamps (`LAMP_ANGLES`,
`LAMP_Z`, `LAMP_RAD`, `LAMP_OUT`, `LAMP_ARM`), the inlet, lintel and hatch,
`SIDES`, and the atlas layout. `check_layout()` asserts:

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
  than the railing;
- the cage starting 2.2–3.0 m above the ladder's foot, hoops no more than
  1.8 m apart, wider than the ladder, under the deck and ending within a
  pitch of it, its furthest reach 0.3 m inside the base's plan;
- the conductor clear of the brackets; the air terminal's tip 0.8–1.2 m
  over the rim, tapering to a point, its clamp and bracket on the band
  over the railing and under the cap ring; the lamps' heights in order
  and under the cap ring, their bodies off the band and clear of the
  railing.

`build_lod()` then proves the clearances: no two shells' triangles
intersect, on every tier.

## Per-tier triangle counts

| Tier | Sides | Triangles | Kit | Ceiling | What changes |
| --- | --- | --- | --- | --- | --- |
| `LOD0` | 24 | 3254 | 2226 | 12,000 | inlet recessed; full railing; ladder with every rung and its brackets; 21 hoops, 3 straps; conductor; lightning rod with clamp and bracket; six-sided lamps on arms |
| `LOD1` | 16 | 1588 | 864 | 4,000 | no knee rail; every third rung, no brackets; 8 hoops, 3 straps; four-sided lamps, no arms |
| `LOD2` | 12 | 770 | 214 | 1,500 | inlet flush; ladder, cage and conductor painted; the rod a three-sided spike; hand rail, posts, brackets |
| `LOD3` | 8 | 426 | 46 | 500 | deck alone; lamps and spike kept |

"Kit" is everything outside the stack's own solid (`kit_triangles()` in
`build.py`). On `LOD0`: the ladder 1,072 (rails 48, 108 rungs at 8
triangles 864, 20 brackets 160), the cage 570 (21 hoops at 26, three straps
24), the conductor 24, the air terminal 38 (rod 14, clamp 12, bracket
12), the platform's railing, posts and brackets 432, the lamps 90 (30
each: a six-sided body, its dome and underside, and its arm). On `LOD1`:
ladder 336, cage 232, conductor 24, air terminal 38, railing and steel
192, lamps 42. On `LOD2`: railing and steel 168, lamps 42, spike 4; on
`LOD3` lamps 42 and spike 4.

The stack is about 1,030 triangles at `LOD0` (the shaft's ten lifts 2n
each, because the texture repeats per lift; the head band in two parts,
the deck's three rings, the rim, lining and floor; the base with its
fillets, coping, wash and the conductor strip's splits about 220). The
previous revision unioned the ladder into the shaft and the rungs into the
rails (5,134 at `LOD0` without a cage); the kit now cuts nothing, so the
cage costs only its bars and the whole tier is 37 % lighter. The kit
(2,226) is under CLAUDE.md's quarter-of-ceiling trim allocation (3,000) on
`LOD0`; on `LOD1` (864 of 1,000) too. Nothing is padded.

### Air terminal: one rod

Two or three rods round the rim joined by a ring conductor on the cap, as
many stacks carry, would cost about 80 triangles on `LOD0` (a ring of six
or more triangular chords on the rim, about 36–48, and two more rods at 14
each), over the 40 allowed for it; the single rod on the strap's line
reads as the conductor's end on its own, so it is one rod.

## LOD review

Intended switches are the catalog defaults: 35, 70 and 120 m. No overrides.
The review camera was perspective, 1920×1080, 50° vertical FOV, distance
along the view to the front face (`scripts/review_asset.py`), Cycles CPU, 16
samples with denoising, AgX, exposure 0; close renders at 1280×960, 40–50°
vertical FOV, 24 samples. Renders are in the local, untracked
`review/power_plant_polish_2026_11_21/savupiippu_brick_round/`
(`before/` and `after/`, the same sets; `compare/` the sheets;
`mipstress/` the filtering renders), and for the air terminal in
`review/power_plant_polish_2026_11_21/savupiippu_rod/` (`before/`,
`after/`, `compare/`).

Pairs compared with identical camera and light (this revision):

- `LOD0`/`LOD1`/`LOD2` from behind at 20, 35 and 70 m, noon: the ladder,
  cage and conductor across both switches;
- `LOD1`/`LOD2` at 70 m and `LOD2`/`LOD3` at 125 m, rear and oblique, noon
  and reverse sun, at full resolution and with mip textures;
- `LOD0` against `LOD3` at 150 and 300 m, front and oblique, noon: the
  landmark range;
- `LOD0` and `LOD1` close up: the head from 14 m (front, rear, from above),
  from 60 m and at night; the base from 20–22 m (front, east, rear); the
  ladder from 30 m behind, its foot and top from 9–10 m, its side from
  8 m; the whole stack at night from 90 m (and `LOD2`).

- the air terminal, before and after: the head from 14 m (front on
  `LOD0`/`LOD3`, rear on every tier), from 5 m at the rod on every tier,
  from 60 m front and rear on `LOD0`/`LOD3`; the whole stack at 150 m
  front, oblique and rear on `LOD0`/`LOD3`; the base's rear from 10 and
  22 m; the catalog preview.

The previous revision's pairs at 30/40, 65/75 and 115/125 m for the stack
itself (unchanged here) still stand.

Findings:

- **The round.** 24 to 16 sides is not visible at 35 m; 12 at 70 m and 8 at
  120 m keep the shaft's width on smooth shading.
- **The head.** The band, the platform's deck and the open flue keep their
  shape on every tier. The railing's 0.04 m rails are about two pixels
  at 35 m; `LOD1` and `LOD2` keep the hand rail, so the switch at 35 m loses
  only the knee rail (spent on the cage instead) and the one at 70 m
  nothing; `LOD3` keeps the deck, which carries the head's flange in
  outline to 300 m.
- **The ladder and cage.** Close up (8–10 m) the hoops and straps read as a
  cage round the ladder, its foot 2.5 m over the ladder's; at 30–40 m from
  behind the rails, rungs and hoops read as a caged ladder in light and as
  a dark band in shade, and from the 45° aerial the cage's outline shows
  against the shaft. `LOD1`'s every third hoop holds the cage's outline at
  35–70 m. From 70 m the painted ladder on `LOD2`/`LOD3` (dark rails and
  rungs over a darkened band 0.44 m wide) reads as one dark line up the
  back, as the thin modelled rails and cage do on `LOD1` at that range;
  the hoops (0.05 m) are under a pixel there, so losing them at the switch
  is not visible. The painted line starts at the same 8.7 m.
- **The conductor** reads as a thin line beside the ladder at 8–35 m; the
  painted line on the far tiers is about half a pixel from 70 m and does
  not read, as expected.
- **The air terminal** reads as a thin tapered spike with a clamp at its
  foot, continuous with the strap, from 5 m and 14 m, and over the rim
  from the front at 14 m as a thin line behind the head. From 60 m it is a
  pixel-wide tick over the rim; at 150 m and in the catalog preview it is
  under a pixel and does not show. The far tiers' three-sided spike has
  the same outline from 5 m; past 70 m, where `LOD2` takes over, the
  clamp it lacks is under a pixel. Its only lasting effect at range is the
  1.0 m taller bounds, so a fitted camera frames the stack a little
  smaller.
- **The conductor on the base** now reads as a dark line on the rear wall
  in shade and across the wash, no longer a faint light seam.
- **The inlet** goes flush at `LOD2`: its 0.25 m recess is about 3 px at
  70 m, and the black plate keeps the opening's weight.
- **The soot** darkens the upper third from 32.7 m to the head; in the
  catalog preview and at 60–150 m it reads as a darker, streaked top to the
  shaft under the pale band, and at 300 m as a slightly darker top.
- **The lamps** are about a pixel from 120 m by day; close up they read as
  small domed lamps on arms. At night, from 16 m and 90 m, they read as red
  points at the head, red under the reference warm factor too, on every
  tier rendered (`LOD0`, `LOD2`). Night views farther out were not
  rendered.
- **The head band** reads as board-marked cast concrete in sun, no longer
  as a turned metal drum: the staves, the lift joint and the tie holes
  show at 12–16 m, the soot runs under the dark cap ring at 14–60 m.

The six working views (`review_asset.py --six-views`: orthographic front,
back, left, right, top and a 45° aerial) were looked at for `LOD0` and
`LOD3`.

Pending in the consumer: real LOD switching, shadows of a 46 m stack in the
consumer's shadow cascades, and performance.

## Interior geometry

The stack has no interior partition and no buried surface: the deck is
part of its profile, and nothing runs into it. The only closure faces are
the base's floor on the ground and the flue's floor, which is exterior
surface seen from above and lit by the open top.

The validator's hidden-surface test reports 222 of 3,254 triangles (6.8 %)
on `LOD0`, 86 of 1,588 on `LOD1`, 18 of 770 on `LOD2` and none on `LOD3`,
0.1 m² of vertical area at most. Inspected by position, they are the
attachments' end faces that face what they stop `GAP` (1.5 mm) short of: the
platform brackets' ends against the shaft (the largest, at 44.2 m) and
under the deck, the rungs' ends against the rails, the brackets' ends against
the shaft and the rails, the hoops' ends against the rails, the conductor's
ends under the band's foot, the deck and the air terminal's clamp (and the
clamp's and the rod's faces that meet there), the lamp arms' ends against
the band. They are kept deliberately: each closes its solid, and cutting the
parts into each other instead is what cost the previous revision about
3,000 triangles.

## Known simplifications

- The flue is 1 m deep and floored; the real stack's flue runs to the
  inlet. The lining is not tapered.
- The ladder passes through the deck without a modelled hatch, and the
  cage stops under the deck rather than through it; the deck is a solid
  plate, not grating. Rungs, hoops, straps and brackets are triangular
  bars, and nothing is bolted: every part floats `GAP` off what holds it.
- The galvanised flats, the cap ring, the head band's formwork staves, lift
  joint and tie holes, the hatch and the inlet's closure are texture with
  relief in the normal map.
- One air terminal, square and tapered rather than a round rod, about
  twice a real rod's thickness so it reads; no ring conductor on the cap
  and no second or third rod (Per-tier triangle counts, *Air terminal: one
  rod*). On `LOD2`/`LOD3` it is a bare spike off the band, with no clamp.
  The conductor's saddles are painted, and on the wash, the coping and the
  base it is paint only. The far tiers have no conductor below the
  ladder's foot or on the head band.
- The lamps are six-sided (four-sided beyond `LOD0`) bodies with a pointed
  dome, not round.
- The wash's and the inlet's soot are static.
- No flue duct, foundation slab, ground or fence.

## Texture set

One 1024² atlas at 64 px/m, rasterised by `scripts/atlas.py` at `atlas.SS`
= 4 and padded last by `atlas.pad()`. Rows from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–269, x 0–870 | BASE | the base's walls, z 0–4.2 m, V = height; range A (x 0–435) the east, rear and west walls, range B the front's |
| 6–258, x 880–992 | unique | the inlet's closure; the wash seen from above |
| 0–269, x 998–1010 | strip | the conductor's strip of the rear wall and its trapezoid |
| 276–540 | MID, U1 | shaft bands with their ladder strips |
| 544–808 | U2, U3 | shaft bands with their ladder strips; at x 940–1004 the hatch, the lamp, flat patches |
| 816–932 | HEAD | the head band, unwrapped round the stack; at x 532–712 one side of the octagon's coping, at x 724–736 the conductor's strip of the rear coping side |

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
brick between them in the ladder's shade, and the copper conductor 0.275 m
east of the ladder's axis (U runs west across the back facet), 25 mm wide
with a saddle every metre, inside the narrowest back facet (`LOD2`'s at
the top, 0.31 m from its centre). The cage is not painted. `LOD0`/`LOD1`'s back facet
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

### The conductor's strips on the base

The base's rear wall shares range A with the east and west walls, so the
conductor's painted run down it has its own strip: the rear wall and its
trapezoid are split at 0.18–0.37 m east of the axis, and that 12 px (0.19 m)
column samples a copy of range A's own columns there (copied after
weathering, every field included), so the brick runs on across the strip's
edges, with the strap painted down the middle from the ground, darker
than on the shaft's strips (shade 0.78) between deeper shadow edges
(0.72), so it holds against the brick when the rear wall is in shade. The
rear coping side is split the same way onto a copy of the coping's
columns; the wash's outer edge and the base's floor carry the strip's
corners, so the shell stays closed. Across the wash the strap is a line
on the wash region, 2 px (0.125 m at the wash's 16 px/m) of dark
weathered copper (shade 0.6) with 6 mm relief: thinner or lighter, it read
as a light seam in the concrete.

### The head band

Cast concrete against narrow vertical staves, so it reads as concrete,
not a turned drum: 80 staves round the band (about 0.1 m), each its own
tone (±5 %) and up to 0.75 mm proud or back, a 1.8 mm fin at every joint,
long wood-grain streaks in height and tone, a dark lift joint 0.9 m above
the foot with the upper lift's staves offset half a stave, a row of
form-tie holes in each lift, and roughness 0.95 before weathering (about
0.98 measured). Soot grades from about 0.34 at the foot to heavy under the
cap ring, with ninety soot runs of random width and length (0.15–1.5 m)
hanging from the ring, 22 % heavier on the lee (east) side than the
windward, which the band can carry because it is unwrapped once and does
not tile. The cap ring is distinct dark steel, sRGB (46, 46, 47), roughness
0.66, metallic 0.25, sooted and rusted, with a drip shadow under it.

### Relief

Brick 6 mm proud of the joint; galvanised flats 8 mm; the painted ladder
30 mm, the painted conductor 6 mm (on the wash too) and its saddles 9 mm; the inlet plate's
frame, bolts and stiffener 25–35 mm; the hatch's frame 20 mm and panel
12 mm; the head band's stave fins 1.8 mm, staves ±0.75 mm, grain 0.5 mm,
lift joint and tie holes −4 mm, its cap ring 6 mm.

### Weathering and soot

`scripts/weathering.py` at its moderate level: grime, rain wash, faded
paint on the hatch and lamp housings; soil and algae on the footing,
splash-back and salt bloom on the base's brick; dirt on the coping and the
wash; runs and rust on the head band and cap ring; rust and runs on the
inlet's plate and the hatch's foot. MID gets periodic noise only.

The module has no soot, so `facade_atlas.soot()` darkens shade and adds the
module's dirt field: on the shaft by height alone, nothing below 32.7 m
and thickening almost linearly, 0.98 t^1.05, to the head (t the fraction of
the way from 32.7 to 44.7 m: the shaft's upper third), modulated by
vertical streaks periodic round the stack; on the head band as above; a
soot plume over the inlet's lintel. The grade cannot start lower: every
lift below 32.7 m samples MID, so soot there would repeat down the stack,
and the atlas has no room for a fifth band. Nor can the shaft favour one
side: its bands tile round the stack every 4 m, so any bias would repeat
two or three times round it; the one-sided soot is the head band's only.
Mean sRGB of the plain shaft, from MID to U3's top, falls from about
(111, 82, 73) to about (65, 51, 44).

### Filtering

Mip stress renders (`scripts/review_atlas_mips.py`, levels 2–4, rendered
through `review_asset.py --texture-dir`) against the same views at full
resolution: `LOD1`/`LOD2` at 70 m with mip 2, `LOD2`/`LOD3` at 125 m with
mip 3, `LOD3` at 250 m with mip 4, rear and oblique views, noon and reverse
sun. Mean per-pixel difference 0.2–0.45 sRGB levels, 99.9th percentile
3–10, largest 20 (sampling noise at silhouettes): no colour leaking into
the narrow periodic bands or the ladder strips, no seam at the bands'
period, no roughness shift. U3's strip ends 8 px from the patch column at
x 940 and the far tiers' back facet samples up to about 6 px inside it, so
at mip 4 (16 px texels) a bilinear tap can reach the patches' texel; the
renders show no visible effect, and at mip 5 (beyond about 500 m) the two
would merge. Consumer filtering is pending.

Unique textures: six 1024² RGB PNGs (three albedos, one ORM, one normal
map, one emission map), 4 MiB each in memory without mips. ORM, normal and
emission are shared.

## Glazing treatment

No windows. The three obstruction lamps' lenses are the only glass: dark
red glass, albedo sRGB (112, 30, 26) before weathering (lenses stay clean),
roughness 0.06 before the atlas's roughness noise, metallic 0. Measured
under the emission mask's lit core: sRGB (113, 31, 27), mean 57, inside the
Style Direction band by mean value and darker than the lamp housing round
it (91, 92, 94) in every variant; red by brief, as an obstruction lamp's
lens is. They are painted directly, not with `scripts/glazing.py`, which
paints window panes as rooms. The validator no longer measures them: its
glazing check measures only neutral-mask glass, and the lamps' mask is red
(Night lighting), so it reports them as coloured fixtures (`MANUAL`); the
values above were measured by hand.

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
three lamps' lenses: the lamp region's lens part (`LAMP_R`'s upper 7 rows,
x 940–956, rows 629–636, 264 lit pixels with their padding), a soft bright
core falling to about 0.6 at the lens's rim, written by
`facade_atlas.lamp_emission()`. Housings, the stack and everything else
stay black. Every tier's lamps sample the same lens rows, so they glow
alike.

- **Coloured mask, a deliberate departure.** Window masks are neutral grey
  so the consumer owns their colour. An aviation obstruction lamp is red
  by definition, and a neutral mask made it glow in the consumer's default
  warm white, so this lamp region is painted saturated red, sRGB
  (255, 26, 14) at the core, blended in linear light: the consumer's
  colour and intensity multiply a red source, and any warm or white factor
  still gives a red lamp. Nothing else in the mask is lit. The validator
  reports the 264 pixels as coloured luminous fixtures (`MANUAL`) and finds
  no neutral glazing to measure; its binding and default-off checks pass.
- **Control scope:** the consumer's intensity and colour apply to the whole
  mask, which here is the three lamps only. One mask, one control: the
  three lamps cannot be switched or flashed apart.
- Bound as `emissiveTexture` on every tier, factor written as zero
  (default off) by `asset_build`'s export; the texture is kept at zero.
- `variants.png`: the three colours at `LOD0`, a day row above a night row
  at the catalog's warm reference factor (`window_emission.LIT_FACTOR`),
  the preview studio's camera, sun and exposure; the lamps show red under
  the warm factor. No light spill is simulated.
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
factor rewritten to zero. The build uses no boolean: the stack and every
attachment are written into one mesh as separate closed shells.

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

- `scripts/validate_asset.py`: 0 FAIL. Every tier welded manifold (the
  kit's shells each closed), one material, uri-only images, normal map at
  scale 1, emission bound and default off, under its ceiling, pivot at
  ground and centred; hidden-surface candidates 219 / 83 / 18 / 0, the
  attachments' end faces (Interior geometry); six 1024² RGB PNGs; the
  red lamp mask reported as coloured fixtures (`MANUAL`), the lens's
  albedo measured by hand (Glazing treatment); the facts sidecar, its
  bounds 6.8 × 6.8 × 47.5 m (the air terminal's tip; plan bounds,
  footprint and pivot unchanged from the previous revision), the same
  extents on every tier's GLB. The sidecar's `source.dirty` is true (written from an
  uncommitted tree); it must be rewritten from a committed one
  (`build.py -- facts`).
- `check_layout()`, `build_lod()`'s no-intersection test on every tier
  (the air terminal's rod, clamp, bracket and spike included), and the
  atlas's `check_regions()` and `check_bands()`.
- The six working views at `LOD0` and `LOD3`; close renders of the head
  (front, rear, above, 60 m, night), the base (front, rear, east), the
  ladder (rear at 30 m, its foot, its top, its side) on `LOD0` and `LOD1`;
  rear views at 20, 35 and 70 m on `LOD0`–`LOD2`; `LOD0`/`LOD3` at 150 and
  300 m; night at 90 m on `LOD0` and `LOD2`.
- Before/after sheets against the previous revision, the same sets; for
  the air terminal and the base's conductor, the head, rod, base and
  150 m sets (LOD review).
- Mip stress renders at 70, 125 and 250 m (Texture set, *Filtering*).
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

- in the consumer: import, orientation and pivot on reimport, LOD
  switching, shadows, filtering of the tiling shaft bands, the lamps'
  colour and flashing, performance.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`) throughout.
The MCP addon was not used. Texture generation used the system Python 3
with numpy, scipy and Pillow.

## Revision log

- **2026-11-21:** air terminal. A lightning rod on the strap's line,
  rising 1.0 m over the rim to 47.5 m: a tapered square copper rod on a
  clamp block, with a bracket under the cap ring, on `LOD0`/`LOD1`; a
  three-sided spike to the same tip on `LOD2`/`LOD3`, so every tier sets
  the same height. The strap now ends under the clamp. One rod, no ring
  conductor (its cost). The conductor's line across the wash widened to
  2 px of dark copper, and its strap on the base's rear wall and coping
  darkened between deeper shadow edges. Triangles 3,254 / 1,588 / 770 /
  426; height 46.5 to 47.5 m; plan bounds, footprint and pivot unchanged.
  Not remeasured: the filtering renders (Texture set, *Filtering*); the
  change to the atlas is the base's conductor strips and the wash line.

- **2026-11-21:** polish pass. A hooped safety cage (21 hoops, three
  straps) on the ladder; the ladder, rungs, brackets, railing, platform
  brackets and lamps rebuilt as separate closed solids held 1.5 mm clear of
  everything instead of boolean-cut, and the deck made part of the stack's
  profile (`LOD0` 5,134 to 3,216 triangles with the cage). Obstruction
  lamps smaller, six-sided with a dome, on arms, their emission mask
  painted red. The head band repainted as board-marked cast concrete with a
  lift joint, tie holes, rougher ORM, heavier soot grading and runs, lee
  bias, under a dark steel cap ring. Shaft soot graded almost linearly over
  its upper third. The copper down conductor restored: modelled beside the
  ladder on `LOD0`/`LOD1` up to an air terminal level with the rim, painted
  on the far tiers' ladder strips, and down the base's rear on its own
  strip. Bounds, footprint and pivot unchanged.

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
