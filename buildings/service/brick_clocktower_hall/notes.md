# brick_clocktower_hall

## Style brief

A composite late-19th-century Nordic civic hall: a long, horizontal front range
in red brick with white painted trim, two tall ceremonial storeys of
rectangular windows over a grey stone plinth, a continuous dentilled cornice, and a low dark seamed-metal
truncated-hip roof over one continuous flat deck. A centred clock tower rises
through a pedimented attic to a balustraded platform, a short drum with arched
louvred openings, a small dome, and a thin flagpole.

The intent is a building that reads at a glance as a town hall — the civic
centrepiece of a district — rather than as a generic two-storey block. All of
the legibility is carried by proportion and the texture: geometry carries
silhouette only.

### Composition

Horizontally, a five-part front — end pavilion, recessed run, projecting centre
entrance bay, recessed run, end pavilion — on a U-shaped plan open to the rear,
with side wings and a shorter central rear projection reaching about 60 % into
the court. The cornice runs continuously across the whole facade, so the roofs
step where the masses do and the walls do not. Width to eave height is roughly
4.3 : 1 and the plan roughly 1.85 : 1 wide-to-deep, which is what makes the
building read as long and low rather than as a block.

Vertically, the centre narrows in three stages — entrance bay, then a narrower
clock attic, then a narrower tower again. Measured off the 11.4 m wall height:
roof 3.25 m above the eave, tower platform at roughly 18 m, a drum of only
about 2.1 m, a dome of about 1.4 m, and a tip at about 24.6 m, of which the top
3 m is a thin flagpole rather than a solid spire.

Those last figures are smaller than they look like they should be, and that is
the point. An earlier pass had the drum and dome each roughly twice as tall on
a 4.4 m shaft, which read as a campanile bolted onto a low building. A tower
over a wide, low range works by staying slender and letting the range keep the
horizontal — the crown is a punctuation mark, not a second building.

## Category and secondary use

`buildings/service/` — a civic/municipal building. No secondary use.

## Hero/landmark status

**Hero/landmark: yes, for texture size, and for the triangles of `LOD1` and
`LOD3`.** `LOD0` and `LOD2` sit inside the *ordinary* band. `LOD3` is 572,
over the ordinary 500 and inside the hero 700, since the six chimneys were
opened: their flues cost 96 triangles on every tier, and at `LOD3`'s 120 m
switch each flue is still about 7 px across (see Per-tier triangle counts and
LOD review). `LOD1` is 4,024, 24 over the ordinary 4,000 and well inside the
hero 6,000, since the rear service door's bay was split off its wall (see
Construction, Rear service door).

*Texture* is justified by texel density rather than importance. The facade is
48.8 m wide; at the catalog's 64 px/m target a 1024 atlas would give this
building roughly half the texel density of a small house on 1024, breaking the
"texel density stays consistent across the catalog" rule.

*Triangles* used to need the exception too. Under the budgets this asset was
first built to, `LOD0`'s 5,108 was over an ordinary 4,000 ceiling. The bands
have since been re-derived from the play camera's 20–150 m range, and 5,108 is
now well under the ordinary `LOD0` ceiling of 12,000. The spend itself has not moved:
openings are still cut on every elevation, courtyard included, because a town
hall is placed once per district and seen from all round.

One lesson from the earlier argument is still worth keeping. At 6,232 the hero
band was carrying about 3,000 triangles of invisible interior wall, not
courtyard windows, so the stated reason was true of the asset but not of most
of the count. When a budget exception is argued for, check that the triangles
are actually being spent on the thing named.

`scripts/validate_asset.py` takes one hero flag for both texture and
triangles, so this asset is validated with it
(`-- buildings/service/brick_clocktower_hall building hero`). Without the flag
the 2048 atlas fails the texture cap, `LOD1`'s 4,024 fails the ordinary
4,000 ceiling and `LOD3`'s 572 the ordinary 500.

## Footprint

**48.96 m × 26.86 m** (width × depth) measured at ground level, including the
1.6 m pavilion and 2.2 m centre-bay forward projections, the quoin blocks and
the rear wings. `LOD2` and `LOD3` paint their quoins rather than modelling
them, so they measure 48.80 m × 26.70 m at the ground. An earlier version of
these notes gave the pavilion projection as 1.2 m and the depth as 26.78 m.
Both were measured off the export and corrected.

The eave overhang and the balcony carry the overall extent to
**49.70 m × 28.35 m** on every tier. Use the ground figure for placement and
the overall one for culling bounds.

## Story height

**Two storeys, floors at 0.15 m and 5.55 m**, 5.40 m floor to floor, with
the eave at 11.4 m. Each floor is where a door opens onto it:

| Floor | Level | Set by |
| --- | --- | --- |
| Ground | 0.15 m | the entrance's and the rear service door's thresholds, each one painted 0.15 m step above the ground |
| Upper | 5.55 m | the balcony's deck and the string course's top; the balcony door's threshold is 0.05 m above it |

On the facade the ground storey is the grey stone plinth (0–0.95 m, capped
to 1.15 m) and the brick up to the string course (5.10–5.55 m); the upper
storey is the brick from 5.55 m to the frieze at 9.95 m, under the 1.45 m
frieze and cornice zone. **The plinth is the wall's stone base course, not
a raised floor**: the floor runs 0.80 m below its top, and the entrance is
cut down through it to the floor.

The sidecar first stated the floors as 0.95 m (the plinth's top) and 5.10 m
(the string course's foot), which left the entrance threshold 0.80 m under
the ground floor and the balcony door 0.50 m over the upper one, with no step
between them. Measured on `LOD0`, the building says otherwise. The entrance
recess's floor is at 0.15 m, over a flush wall face from the ground and no
modelled step. The ground-floor sills stand 1.10 m over a 0.15 m floor, against
0.30 m over a 0.95 m one, and the upper sills 0.80 m over 5.55 m. The arched
entrance's fanlight tops out at 3.60 m, level with the window heads at
3.70 m, which is an entrance composed at grade. So the stated levels were
wrong, not the building, and only the levels changed. `check_massing()`
now fails the build if a door's threshold is not on a floor or at most
0.10 m above one.

This **deviates from the ~3.0–3.3 m standard**, deliberately. Ceremonial civic
architecture of this period has genuinely tall floors — tall ground-floor
openings and a grand upper storey are what the type is. Forcing 3.0–3.3 m
would have produced a squat building that reads as offices rather than as a
civic hall. The deviation is confined to this asset class of building; it should
not be copied into residential work.

## Door leaf height

**2.35 m** for the entrance, with an arched fanlight above the transom
carrying the opening to 3.60 m; **2.30 m** for the other two doors. All three
are within the 2.0–2.4 m anchor range, so no deviation to justify — the
grandeur of the entrance is in the fanlight and the surround, not in a taller
leaf.

| Door | Leaf (w × h) | Threshold | Above the leaf |
| --- | --- | --- | --- |
| Entrance, centre bay (main) | 2.00 × 2.35 m (a pair of leaves) | 0.15 m, the ground floor | transom bar at 2.42–2.50 m, the cut's head at the 2.60 m springing, then an arched fanlight to 3.60 m, flush |
| Balcony door, over the entrance | 1.24 × 2.30 m (a glazed pair) | 5.60 m, 0.05 m over the upper floor and the balcony's deck | transom at 7.90–8.02 m, then a fanlight 1.08 m tall to the 9.10 m head |
| Rear service door, right rear wing's end | 1.40 × 2.30 m (a pair of panelled timber leaves) | 0.15 m, the ground floor | head rail at 2.45–2.60 m, the cut's head |

The entrance's and the service door's thresholds are the floor they open
onto, one 0.15 m step above the ground: each step is painted across the
wall's foot (3.8 m wide at the entrance, 2.0 m at the service door), not
modelled.

The balcony door's opening is 3.50 m tall, cut in one piece. The leaf
height reads inside it by its transom, 0.12 m deep against the glazing bars'
0.06 m, standing 25 mm off the glass against their 15 mm, with a shadow line
under it; the leaves below carry a bottom rail and two bars, the fanlight
above only the meeting stiles' upright, so the two read as different lights.
The sidecar gives the leaf, 2.30 m, not the opening.

The service door's cut runs to 2.60 m, a height the wall ring already cuts
at, so the door adds no band round the building; the 0.15 m head rail at the
top of the cut ends the leaves at 2.45 m.

## Window sills

| | Sill / head | Height |
| --- | --- | --- |
| Ground-floor windows | 1.25 – 3.70 m | 2.45 m |
| Upper-floor windows | 6.35 – 8.95 m | 2.60 m |
| Main doorway leaf | 0.15 – 2.50 m | **2.35 m**, with an arched fanlight to 3.60 m |
| Balcony door leaf | 5.60 – 7.90 m | **2.30 m**, with a fanlight over the transom to 9.10 m |
| Rear service door leaf | 0.15 – 2.45 m | **2.30 m**, under a head rail to 2.60 m |

Against the floors (Story height): the ground-floor sills are 1.10 m over
the 0.15 m ground floor and the heads 3.55 m; the upper sills are 0.80 m over
the 5.55 m upper floor and the heads 3.40 m. Both are under the ~1.4 m
chest-high line, and every door's leaf starts on its floor (the balcony
door's 0.05 m over it). The balcony door's transom at 7.90 m sits within
0.05 m of the middle bar of the tall windows either side of it (7.85 m), so
the three read across as one line.

These were rescaled after a check against human scale. The first pass had a
1.75 m sill — chest height — with 2.8 m windows, and a doorway opening 3.75 m
tall, so the door read as no larger than a window beside it.

That mistake is the reason CLAUDE.md now treats door height as the catalog's
human-scale anchor, stricter than story height and with no authored-deviation
escape. A 3.75 m door does not read as a grand door: it reads as a normal door
on a building scaled 1.6x, and since a consuming project will often scale an
imported building by matching its door to their character height, the error
would have propagated to everything placed beside it.

## Eave overhang

**0.45 m**, with a 0.25 m fascia and a soffit, around the whole building — the
middle of the 0.3–0.6 m convention, so this asset sets the catalog default.

The overhang is applied by growing the union footprint before the roof solid
is built, so the soffit and the attic floor are one coplanar face. It is kept
at every tier: the rules allow dropping it at `LOD3`, but a single construction
path is worth more than the handful of faces that would save.

## Construction

The shell is a union of wall rectangles — the five-part front range, the two
end pavilions, the rear wings and the central rear projection, plus the tower
— with the roof raised from the same outline, so the eave and the hip follow
the plan exactly and the cornice can run continuously across the masses.
Three parts of that are worth knowing before changing any of it.

### Roof form

**One truncated hip over the whole union footprint** — a 3.5 m sloped band up
from the eave to a single flat deck at 14.65 m. Roof height above the eave is
3.25 m, a little under a third of the wall height below it.

Two fixes, in order. First, steep hips meeting at a 15.6 m ridge made the roof
far too tall for a 48.96 m-wide building; the truncated-hip profile is what
keeps the roofline low. Second, and less obvious: building one
hip *per mass* put a slope on every internal boundary too, so where two masses
abutted, each sloped down to its own eave and back up, cutting deep valleys
across what should be continuous deck. Those read as large wedges in the middle
of the roof. The roof is therefore built by `roof_solid()` as a single solid
over the union of the wall rects, which puts slopes only on the outer
perimeter.

Two bmesh traps in that construction, both worth knowing about. `inset_region`
applies its depth along the face normal, and a face built from an edge loop can
come back pointing down, which drove the whole roof 3 m *below* the eave
instead of up to a deck. And `dissolve_faces(use_verts=True)` dissolves any
vertex left with two edges — which includes the outline's genuine right-angle
corners, not only collinear ones. That turned every step in the plan into a
diagonal and sent the roof cantilevering out over the courtyard, visible only
from the rear. Collinear vertices are now removed by an explicit per-vertex
test instead.

Chimneys are dark rendered stacks rather than exposed brick, so they sit against
the dark roof instead of reading as red posts standing on it.

Each stack is open at the top: a one-brick 0.25 m shell, capped in steel along
its rim, round one 0.70 × 0.70 m flue. The flue is sunk 1.00 m and lined and
floored with the atlas's soot patch on every tier, which leaves its floor
0.65 m over the 14.65 m deck. `check_massing()` fails the build if a flue
reaches within 0.10 m of the deck or leaves less than 0.30 m of opening in its
stack.

### Side elevations

**Defect, found and fixed: each side elevation was two walls that missed each
other by 0.8 m.** The end pavilions run to x = ±24.4 and the rear wings
originally stopped at ±23.6, so the side had a 15.6 m run, an 0.8 m return, and
a 10.5 m run instead of one plane — and since the roof is raised from the same
rectangles, the eave and hip stepped at the same place. Two of the quoin blocks
sat on that jog, which drew a vertical quoin strip down the middle of what
should have been a flat wall and made it read as a seam.

The trap is the size. A 0.8 m setback is too small to be seen as articulation
and too large to be missed, so it reads as two misaligned buildings rather than
as a design move. A real setback would need to be deep enough to cast its own
shadow; anything under about a metre should simply be flush.

Fixed by widening both wings to x = ±24.4 and deleting the two stranded quoin
blocks. Each side is now a single 26.1 m plane, and the outline went from 24
segments to 20. `LOD0` 5,220 → 5,036.

`check_massing()` in `build.py` asserts at build time that no outline segment
is under 1 m. That failure is invisible in the rectangle list and obvious only
once rendered, which is the worst combination — and it would never have been
caught by the interior-geometry check, since the jog was perfectly visible. It
was wrong, not hidden.

### Quoined corners

Quoins are **derived from the plan outline**, one block per convex corner, by
`quoin_blocks()`. They were hand-listed at first, and that list went wrong
twice in opposite directions within one session. Flattening the side jog
dissolved the corner two blocks were sitting on, leaving them stranded
mid-wall where they read as vertical seams. Removing those two then left the
entire rear of the building unquoined while the front was quoined — a
consistency error that is obvious from the courtyard and invisible in the
rectangle list.

Both are the same bug: a corner list that does not follow the massing it
describes. Deriving the blocks makes the two agree by construction, so neither
failure can recur. The generator reproduces all six of the original
hand-written blocks exactly, which is what gave confidence the substitution
changed nothing except adding the six that were missing. 12 corners now: 6 on
the entrance front, 4 at the wing ends, 2 on the centre rear link. `LOD0`
5,036 → 5,108.

Concave corners get nothing, deliberately — there is no arris to dress at an
internal angle, and a block there would just fill the reentrant.

The blocks are `LOD0`/`LOD1` geometry. `is_convex()` is shared with the flat
strips that carry the quoins below that, so the painted ones are derived from
the same outline and cannot drift from the modelled ones. The first
four-tier draft simply dropped the blocks at `LOD2`, as CLAUDE.md allows. At
the 70 m switch that took the white corners off every pavilion and the
entrance bay at once, the most visible change left on the building. The
painted strips cost 96 triangles on `LOD2`.

This also nudged the hidden-surface figure from 9.5% to 12.9%, which is
expected rather than a regression: each block buries two of its own faces in
the wall and occludes the wall behind it. That is the deliberate
interpenetrate-don't-touch strategy used everywhere small pieces meet a wall,
and it is occluded exterior surface, not interior geometry.

### Clock dial

The 1.96 m dial is a shallow modelled disc with a 0.10 m rim on `LOD0`/`LOD1`,
about 60 triangles. That is under the 0.25 m relief threshold, and it is kept
as a singular fixture: there is one per building, so the cost stays small, and
its rim's edge, parallax and shadow show at the near tiers. The geometry
is not there to keep the circle round. A modelled disc and a painted circle
both foreshorten to an ellipse at an angle, so modelling cannot help with
that. At `LOD2` the dial becomes paint (the rim is about 1.7 px at 70 m), and
the same dial artwork serves both.

### Rear service door

**Where:** the right rear wing's end wall (x 13.4–24.4 m, facing +Y, 11.0 m
in three bays), in place of the middle bay's ground-floor window, centred at
x = 18.9 m; the window above it stays. The rear's other candidates were
worse. The centre rear link's end, on the building's axis, has four 3.0 m
bays and so no middle bay: a door there would either sit off the axis or be
wedged between two windows at the bay joint, with 1.1 m between their
architraves. It is also a court wall, which `LOD1` bakes flat. A wing end is
an outer wall, cut at `LOD1` like the street fronts, it faces the open side
of the U onto the rear street, where deliveries come, and its middle bay
holds a door with its surround symmetrically. One door, on one wing, is
enough for a service entrance; the left wing's end is unchanged.

**Geometry.** The door is an opening in the wall ring like a window:
`REAR_DOOR` replaces that bay's ground-floor window in `_bay_openings()`'s
list, so `LOD0`/`LOD1` cut it 0.28 m deep with jambs, head, a threshold
floor sampling the reveal patch, and a closing door plane; `LOD2`/`LOD3`
leave it flat, painted, like every other opening. The cut is 1.40 m wide,
the window's own half-width, so it shares the window column above it, and
runs from 0.15 m to 2.60 m, two heights the ring already cuts at, so no band
is added round the building. Against the window it replaces it has the same
number of cells, faces and reveal sides: the door itself costs no triangles.

**Texture.** The wall maps the tiling facade band, whose bays all have a
ground-floor window, so the door's bay samples its own atlas region, `REAR`
(below). From every tier the wall is split at the door bay's two joints
(s = 3.67 and 7.33 m), and the faces between sample `REAR` through
`_uv_rear_bay()`: the band's own mapping, moved onto the copy. Those two
splits are the door's whole cost: +44 triangles on `LOD0` and `LOD1` (two
columns through the ring's ten bands, and two more corners on each of the
wall ring's caps) and +8 on `LOD2`/`LOD3`.

`check_massing()` fails the build if the wall is no longer one outline
segment, if it no longer has three bays (the door is painted narrowed for
exactly that stretch of the band), if the door leaves its bay's centre, or
if its threshold is not on a floor.

## Per-tier triangle counts

| Tier | Triangles | Ceiling, ordinary / hero | Notes |
| --- | --- | --- | --- |
| `LOD0` | 5248 | 12,000 / 20,000 | Cut window and door reveals on every elevation, the rear service door included, modelled clock dial, eave overhang, balcony, quoin blocks on all 12 convex corners, chimneys with open flues, and the full tower crown: balustraded platform, two-stage dome, finial ball and flagpole |
| `LOD1` | 4024 | 4,000 / 6,000 | as `LOD0`, but the seven walls inside the U-court have their windows baked flat; over the ordinary ceiling by 24, inside the hero one |
| `LOD2` | 592 | 1,500 / 2,500 | All windows and doors baked flat. Quoins painted onto 0.5 m corner strips, and the dial left to the painted clock. Massing, overhang, pedimented attic, balcony, chimneys and the full crown are all kept |
| `LOD3` | 572 | 500 / 700 | as `LOD2`, with the dome's two stages merged into one and the finial ball folded into the flagpole |

The rear service door costs 44 triangles on `LOD0`/`LOD1` and 8 on
`LOD2`/`LOD3`, all of it the split that gives its bay its own atlas region;
its opening has as many faces as the window it replaced (Construction, Rear
service door). That split is what takes `LOD1` over the ordinary 4,000; the
door's alternatives, a court wall that `LOD1` bakes flat or a door without
its own artwork, were worse trades than 24 triangles inside the hero band.

**Modeled trim at `LOD0`: about 278 triangles.** That is roughly 144 for the
twelve quoin blocks, 48 for the balcony, ~28 for the eave fascia ring (its
soffit costs nothing extra, being the same face as the attic floor) and ~60
for the clock dial. The cap is roughly a quarter of the tier's ceiling, which
is about 3,000 for `LOD0`, and this is far under it; `LOD2`/`LOD3` carry only
the balcony and fascia. Window and door reveals are not trim under that cap —
the opening is massing, and the ornament around it is still painted.

**Why the counts are low.** A tier far under its ceiling is a finding to
record, not a defect to pad.

- **`LOD0`:** the silhouette is simple, a U-plan mass under one hip roof with
  one tower. The spend is in cut openings, and there is nothing further that
  carries shape. Adding triangles made this building worse the one time it was
  tried: stepping the arched windows' cut to follow the curve took `LOD0` to
  13,304 and read as a staircase (see Known simplifications).
- **`LOD2`:** everything left on it is massing, roofline or crown, and the
  step to `LOD3` shows what little is left to remove.
- **`LOD2` and `LOD3` are close together:** 592 against 572. That is what this
  silhouette actually costs, the six open chimney flues' 96 included. Anything more a `LOD3` could drop — chimneys,
  balcony, projections, crown — shows as a change at the 120 m switch.
  Chimneys were tried: dropping them left six gaps of about 12 × 16 px each in
  the roofline at that switch. The balcony is also the frontmost element, so
  dropping it would move every tier's bounds, and with them the shared pivot.

**History, in order.**

1. 6232 / 388 / 166: the original three tiers, carrying interior geometry
   (see Interior geometry).
2. 5220 / 396 / 178: with the interior removed, but still with the side
   elevation jog (see Side elevations).
3. 5108 / 356 / 138: the three-tier chain as it stood before `LOD3`.
4. 5108 / 3884 / 488 / 468: the four tiers with solid chimneys.
5. 5204 / 3980 / 584 / 564: the chimneys open.
6. 5248 / 4024 / 592 / 572: the current four tiers, with the rear service
   door's bay split off its wall.

The three-tier chain predated both the fourth tier and the current bands, and
its lower tiers dropped far more than silhouette:
- `LOD1` lost the tower's platform and flagpole.
- `LOD2` also lost the balcony and pediment. It collapsed the 1.6–2.2 m facade
  projections flush and capped the tower with a plain pyramid. Those
  projections were taken as sub-pixel at `LOD2`'s range, but at 70–120 m they
  are 16–37 px.
- Because every tier was pivoted on its own bounds, and the old `LOD2` had no
  balcony, `LOD2` also sat 0.98 m off `LOD0` in Y. The engine would have moved
  the building at the switch while every file looked correct on its own.

All tiers now share `LOD0`'s pivot, and `build_all()` raises if a tier's bounds
disagree with it.

## LOD review

**The chimney flues stay recessed on every tier**, where the windows go flush
at `LOD2`, as CLAUDE.md asks of every chimney. Each flue is 0.70 m across. The
area a flue changes is up to 38 × 26 px in the 35 m aerial views and still
11–13 px at 120 m, where `LOD3` shows it as a dark opening in each stack.
Painted flush, sunlit soot reads as dark grey, barely apart from the steel cap.
The recess costs 96 triangles on each tier and takes `LOD3` into the hero band
(see Hero/landmark status).

The crown is how this building reads on the skyline, so it is the part the chain
protects. The dome was already four-sided, the least a dome can have and still
read as one, so there was no coarser version to fall back to. The crown is kept
unchanged through `LOD2`. At `LOD3` it changes by about a pixel, and its
outline and the flagpole's 24.6 m tip do not move.

What changes at each of CLAUDE.md's standard switch distances, sized at the
catalog's reference density of 1,160 / d px per metre on a 1080p viewport:

| Switch | What changes | Size there |
| --- | --- | --- |
| `LOD0`→`LOD1`, 35 m | the U-court's windows go flat. The court is seen only from behind and past the wings | reveals 0.28 m ≈ 9 px, in the court only |
| `LOD1`→`LOD2`, 70 m | all other windows and the three doors go flat; the quoin blocks become painted strips; the dial becomes paint | reveals ≈ 4.6 px; quoin blocks 0.08 m proud ≈ 1.3 px; dial rim 0.10 m ≈ 1.7 px |
| `LOD2`→`LOD3`, 120 m | the dome's break merges and the ball folds into the pole | dome profile moves 0.13 m ≈ 1.2 px; ball stood ≈ 1 px either side of the pole |

**The 70 m hard switch is not accepted by the 2026-09-19 daylight review.**
Paired renders at 65/75 m show several-pixel reveal shadows disappearing
together, including on the front; silhouette preservation alone does not
make this inconspicuous. Keep the existing geometry and use **140 m for
`LOD1`→`LOD2`, then 180 m for `LOD2`→`LOD3` as provisional authoring
recommendations**. The 35 m first switch is unchanged by this focused review.
At 135/145 m the flattening is reduced to small window-edge changes; it is
still detectable when blinking frames, not a seamless transition. The crown
stays legible at 175/185 m and 250 m. See the focused review below for setup.
These are suggestions for consumer integration, not implemented runtime
switches or measured performance acceptance; retaining LOD1 farther costs
more than retaining LOD2 despite both exports meeting their ceilings.

Checked by rendering each pair of tiers from one fixed game camera at each switch
distance: 1920 × 1080, 50° vertical field of view, 12° above the horizon, off
the front-right. A difference image was taken for each pair.
- At 35 m the pair is identical: the court is out of view from that side.
- At 70 m the crown's difference is empty; only the facade's reveals, quoin
  edges and dial rim change.
- At 120 m the difference is the dome's break line and the ball's outline,
  a pixel or two wide.

**The rear service door and the balcony door's transom across the tiers**
(reviewed as listed under Review status). The door's bay samples the same atlas copy on
every tier, so at `LOD2`/`LOD3` it is the same door, flat, under the same
upper window, lit the same at night; only its 0.28 m recess goes, at the
70 m switch with every other opening on that wall. The balcony door's
transom is paint on every tier.

### Focused transition and lighting review

Geometry, source.blend, GLBs, atlases and catalog preview were preserved
byte-for-byte. Counts then remained **5,108 / 3,884 / 488 / 468**; the small
LOD2-to-LOD3 reduction is intentional and does not warrant reconstruction.

Reimported exports were compared in Cycles CPU, AgX/None, exposure 0,
1920×1080 with 50° vertical FOV and 16 samples/denoising. Images are cropped
at native pixel size. Front views use 0° azimuth/12° elevation; front-right
40°/30°; rear 150°/30°. Camera distance is along the view direction to the
front/rear bounding face at mid-height, not orbit distance to the origin.
Noon and opposing sun directions provide contrasting reveal shadows.

LOD0/LOD1/LOD2 were compared at 65/75 m from all three views, and at
135/145 m from front and front-right. The 70 m transition visibly loses
reveal shadows across rows of windows. The proposed 140 m transition
reduces this considerably, although window-edge changes remain detectable
in a blink comparison. LOD0/LOD2/LOD3 were compared at 175/185 m and 250 m
from front-right daylight: crown, flagpole and major roofline remain stable.
The proposed 140/180 m later switches require consumer performance and
temporal review; no runtime configuration exists here to modify.

The day/night sheet uses LOD0, 960×720, 24 samples, one fitted 50° vertical
FOV camera and fixed exposure. Morning/noon/dusk sun elevations are
15°/60°/6°; night uses a 35° moon proxy with weak ambient light. A neutral
lower hemisphere and blue upper hemisphere give view-dependent reflections.
Glass was pale and panel-like in bright diffuse illumination at the value in
use then, darkening with the environment at night. Its opaque nonmetallic
shading and low roughness are correctly bound. Those renders predate both the
emission mask and the glazing revision: Night lighting and Glazing treatment
below record the behaviour and the glass value the asset now ships.
Calibration under the actual game day/night environment remains pending.

Explicit mip3/mip4 atlas stress renders were checked face-on at 75 m and
at 75° grazing azimuth at 125 m. Albedo was averaged in linear light and
ORM linearly; temporary mips replace both maps together. Fine detail softens,
but no conspicuous foreign-colour blocks appear in these clocktower views.
Those renders went through `review_asset.py --texture-dir`, which then
rendered the full-resolution textures, because Blender's glTF importer packs
images and a packed image ignores the substitute; the mip4 set was redone
after the fix (see Review status).
This is bounded authoring evidence: the half-texel inset alone does not
guarantee safe mip/anisotropic filtering, and consumer filtering remains
pending. Export validation has no failures or warnings, and the previously documented
hidden-surface candidates remain unchanged.

Reproduction tools are scripts/review_asset.py, scripts/review_atlas_mips.py
and scripts/review_gallery.py. Working renders stay outside deliverable
asset folders. Blender 5.2.1 LTS was used in isolated background processes;
the MCP addon was not used for this focused review.

## Interior geometry

**Defect, found and fixed: the building was not hollow.** The seven masses in
`WALLS` overlap by design, and each was built as its own closed box, so both
sides of every overlap survived inside the shell. The result was a set of
complete full-height interior partition walls — with their own cut windows,
reveals and glass planes, because the wall gridding ran before anything asked
whether a wall was exterior. Rendered on their own they look like a row of
smaller houses standing inside the building. CLAUDE.md's "No interior geometry"
is unambiguous, and this failed it.

The cost was about half the tier. Measured by ray visibility — fire a
cosine-weighted hemisphere of rays off each face and ask whether any escapes —
`LOD0` had **3,018 of 6,232 triangles (48%) that no camera could ever reach.**

The fix is `union_outline`, which is the construction `roof_solid` already
used for the roof and which the walls never got: dissolve the rects into one
plan outline first, then raise the walls from that outline as a single ring.
Interior geometry then cannot occur, rather than having to be detected and
deleted. `wall_with_openings` takes a polygon instead of a rect, and all four
tiers now share that one path.

Net `LOD0` is 6,232 → 5,220, which understates the repair: about 2,400
triangles of interior wall came out, and roughly 1,400 went back in as real
geometry, because courtyard elevations that used to be buried are now genuine
exterior surface and correctly get their own windows. The facade rhythm shifted
with it — bay counts are derived per outline segment, so the front range now
reads as two 10.9 m runs flanking the entrance bay instead of one 34.4 m run
whose ends were hidden behind the pavilions. That is a fidelity improvement, not
just a saving.

**What is still hidden, and why it is allowed to be:**

| Tier | Hidden | Share |
| --- | --- | --- |
| `LOD0` | 659 | 12.6% |
| `LOD1` | 541 | 13.4% |
| `LOD2` | 140 | 23.6% |
| `LOD3` | 134 | 23.4% |

All of it is structural closure or small buried abutments:
- the cap that closes the wall ring, a single n-gon carrying a vertex per
  window column (146 on `LOD0`);
- the roof underside where it doubles as the attic floor;
- the lower parts of the chimney, tower and clock-attic shafts inside the roof
  volume;
- the backs of the quoin blocks and balcony.

The open chimney flues added none: their lining and floor see the sky up the
shaft, and the hidden counts did not move when they were cut. The rear
service door added two per tier, the two more triangles of the wall ring's
top cap, inside the roof, where the door bay's splits meet it; its recess is
exterior surface like a window's.

A watertight manifold shell has to close somewhere. That closure is roughly
the same size on every tier, which is why it is a larger share of the two
small ones. This is categorically different from a partition wall with windows
in it.

This is checked mechanically by `scripts/validate_asset.py`, which runs
against `export/` rather than the authoring scene. This asset passes it on
every tier. The whole run reports 0 FAIL and 0 WARN.

Two things worth carrying forward. First, the original choice was recorded in
these notes as a *virtue* — buried faces avoid z-fighting — and it is, for a
quoin block; it was simply never valid at the scale of a whole wall, and
writing it down approvingly is part of why it went unexamined. Second, a
point-in-solid test is the wrong way to measure this: recessed window glass
sits 0.28 m behind the wall plane, so that test calls every recessed window
"buried" and inflates the number badly. Ray visibility is the honest measure.

## Known simplifications

- **Each chimney has one plain flue.** It stands for however many flues the
  stack carries: no dividing walls, no pots, no rain hood.
- **No gutters, so no downpipes.** The roof's fascia samples the facade
  band's top trim rows, the same rows the walls show just under the soffit,
  so a gutter painted there would also appear on the wall. A gutter needs a
  band of its own; the 2048² atlas has free rows for one. The pipes would
  also need placing clear of the quoins, the pavilions' corners and the
  3.2 m window bays. Until then the hall carries no downpipes
  (`scripts/downpipes.py` hangs every pipe from a painted gutter).
- **All windows are rectangular**, though the period's ground floor would
  normally be arched. This was a deliberate reversal after three attempts at
  the arched head, and it is the single most useful thing recorded here.

  A rectangular cut around a round-headed window never resolves: the opening
  and the painted shape disagree, so the recess boundary always reads across
  the arch. Painting the spandrels as shadowed plaster helped; anti-aliasing
  the curve helped; neither removed it. **Stepping the cut to follow the curve
  cost +7,000 triangles** — 6,232 to 13,304, far past the ceiling of the time, because
  extra column breakpoints multiply across *every* band rather than only the
  one they belong to — and it looked *worse*, a chunky staircase ledge that
  reads as a modelling error.

  Rectangular windows make the cut and the artwork agree exactly, so the
  artifact disappears at zero cost. Two cost estimates here were wrong by
  roughly an order of magnitude: treat wall-grid cost as something to measure,
  not predict.

  The main entrance doorway keeps its arch, but only in the texture: the cut
  stops at the springing and the fanlight above it stays flush. Making the cut
  follow the curve **was tried here too and reverted** — as a single opening it
  is affordable (6 steps cost +1,300, well inside the hero band), but at
  walk-up distance six steps read as a staircase rather than an arch, and the
  step count that would look smooth does not fit. Stopping at the springing is
  clean because the springing is where a real reveal head sits anyway, and the
  dark door leaf keeps the boundary from reading.
  - Three related fixes are in. The painted surround runs on a wider arc than
    the cut, so the part falling inside the recess is painted as shadowed
    plaster, which stops the white band visibly stepping back 0.28 m at the
    rect edge. Reveals sample a dedicated shadowed patch rather than the bright
    trim patch. Both of those tones are deliberately dark **in albedo**, not
    left to AO. The ORM's R channel reaches the engine through the glTF
    occlusion output, but Blender's own renderer ignores that output, so
    preview renders show reveals brighter than the engine will. Anything judged
    by eye here has to read correctly on albedo alone.
- **Window reveals are `LOD0` and `LOD1` detail.**
  - `LOD0` cuts them on every elevation.
  - `LOD1` cuts every elevation except the seven walls inside the U-court.
  - `LOD2`/`LOD3` bake all of them flat.

  So the court's windows go flat at 35 m, and everything else goes flat at
  70 m, which is where CLAUDE.md expects the pop on every building. **Open
  question:** LOD switching is not implemented in the consuming game yet, so
  how visible either pop is has never been tested. Check it when switching
  lands; see LOD chain and switch distances for what to adjust.
- **Quoins run the full wall height**, including across the plinth, rather than
  stopping at the plinth cap. Rusticated corners carried down to the base are
  plausible for the period, so this reads as a design choice, but a future pass
  could start them above the plinth.
- **No chajja or dormers**, neither of which belongs on this building type.
- **The entrance and the rear service door are at grade**, each one 0.15 m
  threshold step up, painted across the wall's foot rather than modelled;
  there is no flight, so no handrail. The 0.95 m plinth is a base course the
  doors are cut through, not a raised floor (Story height).
- **The service door's leaves, panels and pulls are paint** on its recessed
  closing plane; its head rail is paint too, at the top of the cut.
- **The balcony door's transom is paint.** The door is cut as one 3.50 m
  opening; the transom that ends the 2.30 m leaf is a heavier painted bar
  (Door leaf height), not a modelled member.
- The painted balustrade was **removed from the entrance atlas region** when
  the balcony became geometry; leaving it would have shown a flat balustrade
  through the real one at oblique angles.
- Interpenetrating solids are used where small pieces meet a wall — quoin
  blocks, the balcony, the chimney and tower shafts passing through the roof —
  so the abutting faces are buried rather than coplanar and nothing z-fights.
  All four tiers are fully manifold with no loose geometry. The walls
  themselves are *not* built this way; see Interior geometry.

## Texture set

| File | Space | Notes |
| --- | --- | --- |
| `_albedo_red_brick.png` | sRGB | 2048², 8-bit RGB, no alpha |
| `_orm.png` | Non-Color / linear | 2048², R = AO, G = roughness, B = metallic |
| `_normal.png` | Non-Color / linear | 2048², OpenGL tangent space (+Y green up); shared across tiers |
| `_normal.png` | Non-Color | 1024², OpenGL tangent space (+Y green up), shared across tiers/colours |
| `_emission.png` | sRGB | 2048², 8-bit RGB neutral window/clock/belfry mask; shared across tiers/colours |

- **Texel density: 64 px/m**, uniform across the atlas. This asset is the first
  in the catalog, so that figure is the proposed catalog-wide target.
- Glass is authored neutral and dark by `scripts/glazing.py`, with roughness
  ≈ 0.10 and metallic 0; it is fully opaque, and no reflection or environment
  is baked into the albedo. The near-white grey recorded here before, and the
  sill-to-head ramp that went with it, are both gone. See Glazing treatment
  below.
- Roof metal roughness ≈ 0.38 / metallic 0.25; brick ≈ 0.80; painted trim
  ≈ 0.62; stone plinth ≈ 0.71 — so the materials separate under light.
- The atlas is laid out in three horizontal bands (facade / roof / unique
  features). The facade band tiles horizontally and is mapped from world Z, so
  the plinth, string course and cornice line up across every wall without
  per-wall tweaking. Facade U is snapped to a whole number of 3.2 m bays per
  wall, so windows stay centred and are never cut at a corner.
- The unique band also carries the toothed quoin strip and the balcony
  balustrade, both added when those features became geometry. The quoin strip
  is 0.5 m wide at 64 px/m, the same as a quoin block's depth along the wall.
  From `LOD2`, where the blocks are gone, the same strip is mapped flat onto
  the outermost 0.5 m of each wall at every convex corner. The painted quoins
  stay where the modelled ones were, one texel to one texel.
- A 60 px soot patch lines and floors the chimney flues: the dark id at a
  0.36 shade (albedo about sRGB 32), AO 0.35. It sits above the blank patch
  with a gap on every side, so its padding touches no sampled region; placed
  first against the roof band and the atlas's right edge, it changed a few
  roof texels and, through the wrapping filters, the entrance artwork's
  leftmost columns.
- **The rear service door's bay, `REAR`** (x 1816–2023, y 1290–2020,
  207 × 730 px): one full-height bay of the facade band with the door in
  place of the ground-floor window, in the free strip right of the reveal
  patch. It is not painted there. `paint()` paints the whole atlas twice,
  the second time with the door in the band's bay 1, and copies that bay's
  columns 204–411, every channel and every weathering field, into `REAR`
  before padding. So the brick bond, the grime and the weather noise are the
  band's own, and the wing end's bays either side meet the copy without a
  step in tone at the joints; painted in place, `REAR` would have drawn
  another stretch of every noise field. The door is painted 1/1.146 as wide
  as it stands, since the band is stretched by that across the wing end's
  3.67 m bays, so it fills its 1.40 m cut exactly. Its weathering is the
  shared `door()`: kicked-up dirt across the foot and grime at the pulls. The
  export takes about twice as long for the second painting (about 100 s).
- `REAR`'s padding reaches the atlas's right edge, which the wrapping filters
  read beside its left edge. The leftmost one to four columns of the
  entrance panel and of the balcony parapet changed with it (the cavity, the
  normal map's edge column, a few levels of albedo). The entrance panel's are
  under the quoin blocks on `LOD0`/`LOD1` and the painted quoin strips below;
  the parapet's are its left end and one edge of each return.
- Roughly a third of the atlas is still unused. Packing could be tightened, or
  the density raised, on a future asset.
- **Sill weathering is a falloff, not a rectangle.** It was originally a
  hard-edged box the window's width and 0.6 m tall, flat-darkened 10%, sitting
  directly under the white sill course. It read as a painted shadow rather than
  as dirt: crisp bottom edge, crisp sides, nothing on the wall to explain
  either.

  It became obvious only when the windows were rescaled smaller. The band was
  positioned relative to the sill and kept its size, so it moved down with it —
  on the ground floor from brick, where the coursing broke it up, onto the flat
  grey plinth, where nothing hid the edges. The band did not change; what was
  behind it did.

  `sill_grime()` now fades it downwards and sideways from just under the sill,
  at roughly three-quarters the strength, modulated with noise so it does not
  read as a clean gradient ramp either. Worth keeping in mind generally: an
  effect that looks fine can be wrong already and simply well camouflaged, so
  when something starts showing after an unrelated change, check whether it
  moved or whether its backdrop did.
- **Band boundaries are the atlas' sharp edge, and artwork crossing one goes
  somewhere it was never meant to appear.** Two separate defects came out of
  this and both looked like modelling errors, not texture ones.

  The entrance steps were stacked *downwards* from the door sill, which put all
  three of them up to 0.21 m below the ENT panel's baseline. That baseline is
  z = 0, so they were invisible on the entrance — and they landed in the roof
  band directly underneath, which is tiled under every slope on the building.
  They came back as a pale rectangle on each pavilion roof: the right shape and
  colour for a step, in a place nothing explains. They are now drawn upwards
  from the baseline as a 0.15 m threshold, where they are actually visible.

  Separately, `_uv_roof` mapped V onto the band's exact bounds, 730 and 986.
  A bound is the seam *between* two texels, so bilinear filtering blended the
  eave edge of every slope with the white cornice course below the band and the
  deck edge with whatever the unique band starts with. `_inset()` in `build.py`
  now pulls every region rect in by half a texel, which closes the same hole on
  the entrance panel and the quoin strip too.

  `facade_atlas.py` ends with a guard asserting the roof band holds
  nothing but roof material, since a stray pixel there is repeated across the
  whole roof rather than being a local blemish. Inspecting the atlas would not
  have caught it: in the atlas it is a few correct-looking pixels of step, just
  a dozen rows too low.
- **No plaque below the clock dial.** A painted one sat there, 2.2 m wide
  against the modelled dial's 1.96 m and running from 0.25 m below the dial's
  foot up behind it. Since the dial is geometry, the painted disc was hidden
  and only the strip poking out underneath survived, reading as a white tab
  hanging off the clock. There is 0.37 m of clear wall between the dial's foot
  and the framed panel's bottom rail, not enough for anything legible, so the
  wall is left plain. The general point is the same as the steps: a painted
  element sharing a surface with a modelled one has to be checked *against* it,
  not on its own in the atlas, where it looked fine.

### Curve anti-aliasing

Every curved shape in the atlas — arch heads, the entrance doorway, the tower's
belfry opening, the clock dial — is drawn by **coverage blending**, not by a
boolean mask. At 64 px/m an arch head is only about 40 px across, so a hard
mask stair-steps visibly on the curve. `arch_cov` / `disc_cov` return 0–1
coverage and `paint_cov` blends by it, while material ids and AO still follow
the solid interior. Straight edges keep the cheaper boolean path.

### Supersampled atlas, normal map and padding

- **Rasterised by `scripts/atlas.py` at 4 x 4 samples per pixel.** `facade_atlas.py` paints in
  final-pixel coordinates and the canvas stores the samples; they are
  box-filtered down in linear light, so an edge at a fractional position lands
  partway across its pixel and the arched doorway, the belfry arch and the clock dial come out anti-aliased, instead of snapping to it. The emission mask
  carries the same coverage as grey at pane edges.
- **The normal map is derived from a painted height channel** in metres by
  `atlas.normal_map()`, OpenGL convention. The relief is physical, not
  exaggerated, and only covers what the mesh does not model:
  - brick faces 6 mm proud of recessed bed and perpend joints;
  - the string course, cornice and pediments 60 mm, the window surrounds,
    plinth cap and pilasters 40 mm, the dentils 30 mm;
  - the dark reveal ring round each window set 20 mm back, with the glazing
    bars standing off the glass;
  - standing seams 25 mm with the roof's transverse joints;
  - quoin stones 40 mm proud of the brick, the balusters, the belfry's louvre.
  The clock face stays flat with the glass: the dial is modelled on the near
  tiers.
  Glass stays flat. The roof band is stretched across each slope, so its transverse joints
  are shallow grooves.
- **Albedo carries no directional light.** Highlights that faked a fixed sun
  (lit top edges, sunny board or seam faces) were removed; that relief is
  height now and answers the real sun through the normal map. Shade keeps only
  tone, wear and the occlusion that holds whatever the sun does: laps, joints,
  under drips and overhangs.
- **Cavity and weathering come from shared helpers.** `atlas.cavity()` (height
  minus its Gaussian blur) deepens the ORM's AO and darkens the albedo slightly
  in joints and recesses. Tone wear, grain and rain streaks are `atlas.noise()`
  fields, white noise blurred through the FFT, so they tile exactly; they
  replace the sums of sines, whose regular diagonal blotches showed at a
  distance.
- **The gaps are padded.** `atlas.pad()` fills every texel no region claims
  from the nearest region's own edge, in every map, height included, so a mip
  level's wider footprint at a region's edge finds more of that region rather
  than background. The padding itself keeps a flat normal.
- **Colours are ids and shades.** The old generator painted colours straight
  into an RGB array at import time. Each colour is now a material id and a
  shade on it (the lighter and darker bricks are the wall at 1.08 and 0.905),
  so the albedo, ORM and height come from one painting pass, and
  `python3 facade_atlas.py export` is the same command as every other asset's.

### Weathering

- **Placed by `facade_atlas.py`'s `weather()`, drawn by
  `scripts/weathering.py`** at the catalog's moderate level. Its fields
  (dirt, algae, rust, faded paint, rain runs) are amounts, resolved against
  each colour's own palette. Dirt lerps toward a warm soil colour;
  on steel it is a neutral dust, because soil's brown turned dark roofs
  orange. Dirt roughens the ORM and strips the metallic. Height, the normal
  map and the emission mask are untouched, and glass never weathers.
- **Added to the existing soiling**, not replacing it: the broad grime field,
  the darkening toward the ground and `sill_grime()` stay as they were.
- **The facade band and the entrance panel run from the ground to the wall
  top**, windows included, so: soil, splash specks and a green film at the
  plinth's foot with runs under its cap; a pale salt bloom on the brick just
  above the plinth, fading out over 0.8 m; runs down the brick under the
  string course; dirt on every sill moulding with runs down the wall below it;
  kicked-up dirt at the entrance door's foot; dust in the mortar joints, from
  the cavity.
- **The roof band reads the same either way up.** Its V runs across each
  slope in whichever direction that face gives, so it takes long runs down
  the slope, silt at the seams and an even chalking, and no darker eave.
- **Elsewhere:** runs under the tower's balustrade and drum cornice, under the
  stacks' caps and under the balcony parapet's rail; splash at the foot of
  the quoin strip.
- **Kept clean:** the glazing and the clock dial.
- The level was chosen on `rintamamiestalo_porch` (see its notes); this
  building takes the same helpers with its own layout.
- The albedo and ORM PNGs are larger on disk (2 files, 2.0 MB against 1.6 MB before), as the noise
  compresses less; resolution, count and GPU memory are unchanged.

## Glazing treatment

Panes are painted by `scripts/glazing.py`, the catalog's shared treatment.

| | |
| --- | --- |
| base colour | sRGB 50/54/57 (`glazing.BASE`) |
| measured over the glass mask | mean sRGB 54, linear 0.033 |
| relative to the trim around it | 0.23x |
| roughness / metallic | 0.10 / 0 |
| panes in the atlas | 38 |

`albedo()` builds the atlas as before and then hands the glass mask to
`glazing.rooms()`, which gives each pane its own overall level, a falloff
toward the floor, and a lit patch of far wall on about half of them. That is
the room behind the pane rather than a reflection, so it belongs in base
colour; no sill-to-head sky gradient is baked, which Texture Requirements
rule out.

Why it changed: at the previous value the glass measured linear 0.457
and sat at 0.77x the trim around it, so the panes read as glossy
white paint rather than as openings. Seen from outside a window is mostly the
unlit room behind it, and the sky reflection is generated at shading time from
roughness and the dielectric F0 — a pale base colour asks the diffuse lobe to
reflect the sky as well, which double-counts it. The eight-way comparison that
settled the choice lives in `studies/window_glass/`, local only and gitignored.

The balcony door's transom splits its glass into two panes, the leaves and
the fanlight, each with its own room; the copy of the band's bay in `REAR`
brings one more, the window over the service door, which therefore differs
from the other windows on its wall.

Limit: the atlas is a trim sheet with 38 glass regions, one per opening
kind, so panes vary between kinds and not between windows — every window of a
kind on this building is identical. Per-window variety would need several pane
regions per kind and `build.py` picking one per instance. This is the same
constraint already recorded for emission.

Pending: calibration in the consumer's lighting.

## Variant list

**One variant: `red_brick`** (`_albedo_red_brick.png`).

CLAUDE.md asks for 3–6 albedo variants on low-rise/small-scale buildings and
none on large-scale/monolithic ones, deciding from actual massing and material
uniformity rather than the category folder. This asset sits between the two
cases, so per that instruction, the reasoning:

- it is materially uniform — one brick-and-trim treatment across a 48.8 m
  facade — which is the monolithic case, not the per-building-colour case
- more decisively, a town hall is a **singular landmark**: a city places one,
  not a street of them, so per-building colour diversity has no use here

Variety in this category should therefore come from additional distinct civic
assets, not from re-tinting this mesh. The ORM and the normal map are
shared (there is only one variant).

## Night lighting

**Current support.** `brick_clocktower_hall_emission.png` is a neutral RGB mask
of glazing, the clock dial, and gaps between the upper tower's louvre slats,
grey where an edge covers part of a pixel. The clock face and the louvre
gaps stay at full strength; each window pane is lit as a room (see Room-lit
panes below).
Glazed door panels participate: the balcony door's leaves and fanlight are
lit as two panes, with its transom dark between them. The clock's
hands/hour marks, louvre slats, frames, walls, roof and solid doors stay
dark, the rear service door's timber leaves among them; the window above
that door is lit from `REAR`'s copy on every tier. The dial uses the generator's
final `ID_CLOCK` pixels; the tower mask is restricted to its authored arched
opening, rather than all `ID_DARK` artwork. No interiors or additional
geometry were added. The same dial artwork serves the raised LOD0/LOD1 dial
and painted LOD2/LOD3 clock; the tower opening repeats on its four sides.
All four GLBs bind the same external sRGB mask through `emissiveTexture`
on UV0. It is shared across every colour. Current texture inventory:
four unique 2048² images: one albedo, one ORM, one normal map, one emission.

**Game control.** Every GLB defaults to `emissiveFactor = [0, 0, 0]`, with
the texture binding retained. A reference lit factor is linear RGB
`[1.0, 0.55, 0.23]`; scale it toward zero to dim or switch off. Saved
`source.blend` uses the same linked mask/tint and emission strength zero.
`scripts/window_emission.py` exports a positive reference state, then writes
the default-off core glTF factor while preserving the texture. No emission
extension is needed at this reference intensity. The game owns occupancy,
time and fading: choose lit buildings more frequently in early night and
rarely late at night. Keep that state per placed building. Reused glazing
UVs mean this is one building-wide control, not independent room/window
switching. The windows, clock and belfry share this control and tint;
separate clock/tower schedules are not encoded. The PNG contains luminous
regions, not a baked occupancy pattern.

**Deliverable sheet.** `variants.png` is 640×820, showing the single `red_brick` variant.
Each 640 px column has DAY above NIGHT: emission off versus reference on.
LOD0, fixed catalog camera/lens and framing, AgX/None, exposure 0, Cycles CPU,
48 samples, denoising, seed 42. Day uses the catalog grey world at strength
1 and white sun at strength 3. Night keeps the same light direction with a
blue moon proxy (RGB 0.48/0.62/1, strength 0.12), blue world
(RGBA 0.24/0.32/0.50/1, strength 0.08). Camera and exposure do not change
between rows. `build.py:render_variants()` uses the shared
`scripts/variant_previews.py` implementation. No morning or dusk tiles.
Cycles simulates emission spill onto adjacent surfaces in these previews;
matching spill in the game needs its renderer/GI or separate game lights.
The assets do not contain exported punctual lights.

**Validation.** All four exports pass `scripts/validate_asset.py`, including
external emission binding, UV attribute, default-off state, existing topology
and budgets. A binary-accessor comparison confirms exported positions,
normals, UVs and triangle indices match the previous exports exactly.
Source files reopen with
one shared material across all tiers, relative external textures, and lights
off. Reimported GLBs were rendered both off/on, with lit adjacent-tier
comparisons at 135/145 m and 175/185 m, 1920×1080 projection, 50° vertical
FOV, 40° azimuth/30° elevation, fixed exposure 0; native pixel crops, Cycles
16 samples with denoising. Rear LOD0/LOD3 views at 75 m supplement the sheet.
Base-atlas versus explicit whole-atlas mip4 views compare LOD2/LOD3 face-on
and at 75° grazing azimuth at 185 m; all three maps are minified
together, emission/albedo in linear light. These are temporary stress mips,
not a simulation of the consumer's sampler or shipping mip chain.

**Review limits.** Major lit-window patterns survive through all tiers.
Existing recess flattening changes apparent lit-window edges/width and
surrounding spill; existing small-window omissions remove their light too.
These transitions can read more strongly at night and remain consumer
switching-review items. Mip4 softens glazing/frame boundaries without a
conspicuous new glow patch on unrelated roof/wall regions in the reviewed
views. It does not resolve the previously documented atlas-padding limits.
Daylight glass-value calibration, actual game import/material control,
night exposure, light spill, mip/anisotropic filtering and runtime performance
remain pending in the consumer. This update preserves the current LOD chain.
Working renders/settings are local-only and untracked; reproduce with
`scripts/review_asset.py --lights night --emission on` or `off`, and
`scripts/review_atlas_mips.py` for temporary mip inputs. Blender 5.2.1 LTS;
background processes, no MCP addon used for this pass.

**Clock and belfry lighting follow-up.** The emission mask now includes the
clock dial and all four tower openings. Mask differences are confined to
`ID_CLOCK` and the dark gaps inside the louvre artwork; existing window
emission is unchanged. Exported UV sampling confirms both regions are
present on all four LODs, including each tower side. Reimported night renders
at 135/185 m (front and oblique, every tier) and mip4 stress views at 185 m
(front/grazing, LOD2/LOD3) retain the clock and tower lights; those mip4
views went through the same substitution and so show the full-resolution maps. Hands and slats
naturally lose detail at distance. Working evidence is local-only and
untracked, using the same review projection and lighting described above. The GLBs, albedo, ORM, catalog `preview.png`, and
the DAY row of `variants.png` are byte/pixel-identical to before this
follow-up; all tiers already reference the shared external emission PNG.
The source file reloads that mask and remains off by default.

### Room-lit panes

Each pane in the emission mask is the lit room behind it, not a flat panel:
`scripts/glazing.py`'s `night_rooms()` multiplies it by its own level, a soft
lamp glow and a falloff toward the floor, and never takes it below about a
fifth. The mask stays neutral grey, so colour, intensity and which buildings
are lit are still the consumer's, and nothing in it says whether a room is
occupied. Averaged over the glass it is 63 % of the old full-white mask
(the catalog runs 52-63 %),
so at the same reference factor the windows read as warm lamplight rather than
pale panels. Every window of one type samples the same atlas region, so every
window of that type carries the same room; see the limit under Glazing
treatment.

## Export

Both scripts live in this folder, because both describe this building alone —
`facade_atlas.py` is not reusable tooling, its region constants are this asset's
UV layout written a second time. Regenerate the textures first, then the meshes,
since the UVs index into the atlas:

```
python3 facade_atlas.py export                            # CPython: numpy, scipy, Pillow
blender --background source.blend --python build.py       # bpy
```

`build.py` carries the whole pipeline: `build_all()`, `export_all()`,
`render_preview()`, `render_variants()`, then it saves `source.blend`; all but
the massing behind `build_all()` are `scripts/asset_build.py`'s, shared with
every asset. The last two steps exist
because their settings previously lived only in a chat session or in the
`.blend`, which made the defect below impossible to fix durably — a re-export
would have reintroduced it. `render_views()` renders the six verification
views of any tier to a folder of your choosing. They are working views and
are not committed.

The `source.blend` saved before the four-tier rebuild was stale. It predated
the last three-tier export and held absolute texture paths. It is now
rewritten by every build, with the textures linked relative to it
(`//export/…`), so it opens wherever the repository is checked out.

`preview_studio()`, now `scripts/asset_build.py`'s with this asset's camera
location passed in, pins the catalog's fixed preview camera, sun and backdrop in
code, so "the same angle and lighting for every asset" no longer depends on
nobody nudging the viewport camera. It records one deviation rather than hiding
it: CLAUDE.md asks for a neutral studio HDRI and this is a flat neutral grey
world, which is fixed and comparable but gives no directional fill. That is
still open, and it is now a question for the whole catalog, since every later
asset copied this setup. `preview.png` was re-rendered with the four tiers.
`LOD0` is unchanged, and so is the image, to within one level in 255.

**Facts sidecar.** `export/brick_clocktower_hall.model.json`, written by every
full build (or `build.py -- facts`), in the glTF frame: metres, +Y up, +Z
front, origin at the pivot, which is 2.775 m behind the build origin (LOD0's
plan-bounds centre).

| Fact | Value |
| --- | --- |
| hero | true |
| dwellings | 0 |
| footprint | the 20-corner wall outline, quoins, eaves and balcony left out |
| storeys | two: floors 0.15 m and 5.55 m, 1,024 m² each |
| `front` door | entrance, main; at [0, 0.15, 12.975], facing +Z, 2.00 × 2.35 m |
| `balcony` door | balcony; at [0, 5.60, 12.975], facing +Z, 1.24 × 2.30 m (the leaf, under the transom) |
| `rear` door | service; at [18.9, 0.15, -13.725], facing -Z, 1.40 × 2.30 m |

Settings: `export_yup=True` (Blender Z-up → glTF Y-up), `export_apply=True`,
one tier per file by selection, and `export_keep_originals=True` so the two
2048² PNGs are referenced rather than embedded. The material has backface
culling on, so it exports single-sided.

- **Defect found and fixed: the baked AO never shipped.** The ORM's R channel
  was wired to nothing, so the exporter wrote no `occlusionTexture`. The
  engine got roughness and metallic from the ORM and no occlusion at all.
  `get_material()` now routes R into a "glTF Material Output" group's
  Occlusion input, as the later assets in the catalog do, and all four tiers
  carry the texture.
- **Rebuilds are byte-identical.** They were not. The roof deck's n-gon was
  built from a Python set of BMVerts, which iterates in memory-address order,
  so the deck triangulated differently from run to run. The roof's extrude and
  inset operators also emit faces in address order. The vertex set is now
  sorted, and every tier's faces are sorted by their corners before the mesh
  is written. Two rebuilds against `source.blend` produce identical files.
  Relative to the last three-tier export, `LOD0`'s geometry is unchanged
  except for the deck's 18 triangles, which cover the same flat face split
  differently.

`check_toolchain()` runs when `build.py` loads and covers the two ways the
toolchain can drift out from under it. Below the 5.3 floor an old Blender
otherwise fails as an unrelated `AttributeError` deep in the build; above it,
the exposed surface is exactly those exporter keywords, so the check asserts
each one still exists and names the missing ones rather than letting a rename
surface as a `TypeError` a thousand lines from the settings it broke. It cannot
catch the worse case — a flag that keeps its name and changes its default —
which is the reason these settings are written down here at all.

- **Defect found and fixed: every `.glb` had images carrying both `uri` and
  `bufferView`.** Godot rejected them with `Invalid image definition in glTF
  file using both 'uri' and 'bufferView'`. The cause is
  `export_keep_originals=True`: it writes the external `uri` as intended, but
  *also* leaves a 250-byte 1×1 placeholder `bufferView` behind, and the glTF
  spec allows only one source per image. Turning the option off is not the fix
  — that embeds the full ~1 MB atlas in every tier's file, which duplicates bytes
  that already ship in `export/` and can drift out of sync.

  So `export_all()` runs `strip_embedded_images()` from `scripts/glb_images.py` over each file afterward: it
  walks the GLB chunks, deletes `bufferView` and `mimeType` from any image that
  has a `uri`, re-pads the JSON chunk with spaces and the BIN chunk with nulls
  to stay 4-byte aligned, and rewrites the header length. Verified at the time on
  all three tiers — no conflicts remain, headers and chunk alignment are valid, and
  `lod0.glb` re-imports into Blender at 6,232 triangles with one material and
  both textures resolving from disk. Triangle counts are unchanged.

  Worth remembering as a class of bug: this is silent on the authoring side.
  Blender exported, reported success, and the viewport looked correct; the only
  symptom was a warning in the consuming engine. CLAUDE.md now carries the rule
  under Texture Requirements and a checklist item that says to inspect the
  exported file rather than trust the export dialog.

The material, the export and the previews are `scripts/asset_build.py`'s,
shared by every asset: `build.py` keeps this building's massing, UVs and
layout checks and hands the rest to one `asset_build.Asset`. The material binds
`_normal.png` through a tangent-space Normal Map node at strength 1, so every
tier carries `normalTexture` at scale 1 beside the base colour, ORM, occlusion
and emission bindings. No tangents are exported; a glTF consumer generates
MikkTSpace tangents when none are given, as Blender's importer does. The export
still writes every tier lit and rewrites its emission factor to zero, and
strips the placeholder `bufferView` keep-originals leaves.

## Review status

Checked here, in Blender:

- Difference images between each pair of tiers at 35, 70 and 120 m from one
  fixed camera, and paired renders at 65/75, 135/145, 175/185 and 250 m under
  noon and opposing sun, at the setup recorded under LOD review.
- All six pre-export views, and the crown's outline and flagpole tip across
  the tiers.
- `scripts/validate_asset.py` over `export/` with hero status: no failures or
  warnings; the sampled hidden-surface candidates are the ones recorded under
  Interior geometry.
- mip3/mip4 atlas stress renders face-on at 75 m and at 75° grazing azimuth
  at 125 m, and at 185 m for the clock and tower lights. These predate the
  `review_asset.py` fix below and show the full-resolution textures.
- Glazing measured over the glass mask against Style Direction's band.
- Emission off/on on reimported tiers, including the clock dial and the four
  tower openings on all four LODs, and the day/night sheet at `LOD0`.
- The texture pipeline change, before against after with
  `scripts/review_compare.py`: `LOD0` front and oblique at 20 m and 35 m under
  noon, morning and backlight; mip4 stress renders of `LOD2` at 75 m and
  `LOD3` grazing at 125 m; and the catalog preview. Laps, seams and
  mouldings read as raised in direct sun, which confirms the OpenGL green
  channel, and no new colour leaks appear at mip4.
  These mip4 renders were made after fixing `scripts/review_asset.py`: Blender
  5.2's glTF importer packs images, and a packed image ignores `--texture-dir`,
  so every earlier stress render had shown the full-resolution textures.
- The open chimney flues, before against after with
  `scripts/review_compare.py`: every tier, oblique and aerial at 35 m and
  120 m, under the noon and reverse suns. Every render differs in six small
  areas, one per stack, and nowhere else. Every stack reads as a dark open
  flue inside its capped rim, `LOD3` at 120 m included. The validator, run
  with the hero flag, reports no failures or warnings, and the hidden-surface
  counts did not move.
- The weathering, before against after with `scripts/review_compare.py`:
  `LOD0` oblique and aerial at 35 m and 60 m under noon and morning sun. The
  changes land where `weather()` puts them, and no seam or wrap line shows.
  `scripts/validate_asset.py` still reports no failures or warnings. The
  rebuilt GLBs are byte-identical to the previous ones.

- The floor levels in the facts sidecar, measured on `LOD0` (Story height)
  and corrected to 0.15 m and 5.55 m; `check_massing()` passes with the new
  door-on-floor check. The full rebuild in Blender 5.3.0 leaves every tier's
  triangles, positions, UVs and materials identical to the previous export
  (decoded and compared; the files differ only by the exporter's version),
  bounds 49.70 × 28.35 × 24.60 m and pivot unchanged. Before/after renders
  with `review_asset.py` (`LOD0`/`LOD1` front and oblique at 20 and 35 m,
  `LOD2`/`LOD3` oblique at 70 and 120 m, noon), compared with
  `review_compare.py`: 0.0/255 mean difference on every pair. The validator,
  with the hero flag, reports no failures; its one warning is the sidecar's
  `source.dirty` until it is rewritten from a committed tree.

- The balcony door's transom and the rear service door, before against
  after with `scripts/review_asset.py` and `scripts/review_compare.py`
  (Blender 5.3.0, Cycles, the standard 1920 × 1080, 50° review camera):
  `LOD0`/`LOD1` front, back and rear-oblique at 20 and 35 m under noon and
  reverse sun; every tier front, rear-oblique and front-oblique at 70 and
  120 m at noon; every tier front and back at 35 and 70 m at night with the
  reference emission. Close views at 9–22 m of the service door (face-on and
  40° oblique, every tier, noon and reverse sun, and at night) and at 12 m
  of the balcony door. The renders differ only at the two doors, in the
  copied window over the service door (at night, its own room) and by a
  pixel's shading at the balcony parapet's left end (Texture set); the bays
  either side of the door's bay meet it without a seam in tone, brick bond
  or weather.
  The door reads as a pair of timber leaves under a pale head rail in a
  white architrave, recessed on `LOD0`/`LOD1` and flat from `LOD2`; at night
  it stays dark under its lit window on every tier, and the balcony door
  shows its transom as a dark bar between the lit leaves and fanlight.
  `variants.png` was regenerated and checked. The validator, with the hero
  flag, reports no failures; its one warning is the sidecar's `source.dirty`.
  LOD0's bounds (49.70 × 28.35 × 24.60 m) and the pivot are unchanged.

Pending, and outside this repository:

- The provisional 140 m and 180 m switch recommendations, which need consumer
  performance and temporal review; retaining `LOD1` farther costs more than
  retaining `LOD2`, and nothing here can measure that.
- Consumer-side mip and anisotropic filtering: the half-texel inset alone does
  not guarantee safe filtering, and the atlas-padding limit recorded under
  Texture set is unresolved.
- Consumer import and material control, night exposure, light spill and
  runtime performance measurement.

## Tooling versions

- **Blender 5.3.0** (build 2026-11-11), headless, for the last full rebuild,
  which saved `source.blend`; earlier passes used **Blender 5.2.1 LTS**
  (build date 2026-09-01).
- **Blender Lab "MCP" extension v1.0.3** (`lab_blender_org/mcp`, requires
  Blender ≥ 5.1), with the MCP server from `projects.blender.org/lab/blender_mcp`.

The four-tier rebuild was run headless on the same Blender, driving
`build.py` directly rather than through the MCP extension.

Recorded as a known-good marker, not a requirement — anything at or above
CLAUDE.md's 5.3 floor should build this asset.

- **CPython 3.14.7 with numpy 2.5.3, scipy 1.18.1 and Pillow 12.3.0** for the
  texture export.

## Revision log

- **2026-11-21 — balcony door transom; rear service door.** The balcony
  door's five even bars became a 2.30 m glazed leaf under a 0.12 m transom
  at 7.90 m and a fanlight to the 9.10 m head (`draw_balcony_door()`), and
  the sidecar gives its leaf, 2.30 m, not the 3.50 m opening. A service door,
  a 1.40 × 2.30 m pair of leaves on the ground floor, replaces the middle
  ground-floor window of the right rear wing's end wall, cut like a window
  on `LOD0`/`LOD1` and painted from a new atlas region, `REAR`, a copy of the
  facade band's bay with the door painted in (Construction, Rear service
  door). Counts 5204 / 3980 / 584 / 564 → 5248 / 4024 / 592 / 572, which
  takes `LOD1` 24 over the ordinary ceiling. Every PNG, the GLBs, the
  sidecar, `source.blend`, `preview.png` and `variants.png` were
  regenerated; bounds and pivot are unchanged.

- **2026-11-20 — floor levels.** The facts sidecar's floors go from 0.95 m and
  5.10 m to 0.15 m and 5.55 m, where the entrance and the balcony door open
  onto them (Story height); `check_massing()` checks every door against
  them. No geometry, texture or bound changed.

- **2026-09-25 — weathering.** `facade_atlas.py` gained `weather()`, which
  places the shared `scripts/weathering.py` fields: dirt, algae, rust, faded
  paint and rain runs (Texture set, Weathering). Every albedo and the ORM
  changed; the normal map and the emission mask did not. `source.blend`,
  `preview.png` and `variants.png` were regenerated, and the GLBs rebuilt
  byte-identical.

- **2026-09-25 — open chimney flues.** The six chimneys were solid stacks
  under a steel-capped top. Each is now a 0.25 m shell round one 0.70 × 0.70 m
  flue, sunk 1.00 m and lined and floored in soot on every tier; the soot is a
  new 60 px atlas patch above the blank patch. Triangle counts rose by 96 on
  every tier, which puts `LOD3`'s 564 over the ordinary 500 ceiling and inside
  the hero 700. The albedo and ORM changed only in the new patch and its
  padding; the normal map and emission mask did not. The GLBs,
  `source.blend`, `preview.png` and `variants.png` were regenerated.

- **2026-09-25 — room-lit night windows.** The emission mask now paints each
  pane as a room (`glazing.night_rooms()`: level, lamp glow, floor falloff)
  instead of full white. Only `_emission.png` and the night row of
  `variants.png` changed; the GLBs, the other maps and `preview.png` were
  regenerated unchanged in content.

- **2026-09-24 — supersampled atlas with a normal map, shared build code.**
  `facade_atlas.py` now paints through the shared `scripts/atlas.py` at
  4 x 4 samples per pixel, with a height channel from which a new
  `_normal.png` is derived; directional highlights left the albedo for the
  normal map, the sine-sum noise became periodic FFT noise, and
  `atlas.pad()` fills the gutters. `build.py` hands its material, export,
  previews and tier bookkeeping to `scripts/asset_build.py`, and binds the
  normal map on every tier. Every PNG, the GLBs, `preview.png` and
  `variants.png` were regenerated.
