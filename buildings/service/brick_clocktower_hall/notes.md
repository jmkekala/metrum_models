# brick_clocktower_hall

## Style brief

A composite late-19th-century Nordic civic hall: a long, horizontal
two-storey range in red brick with weathered off-white trim over a grey
granite plinth, a dentilled frieze and a continuous cornice, under a low
truncated-hip roof of dark painted standing-seam steel round one flat deck.
A centred clock attic in brick, under a roofed pediment with a white raking
cornice, carries the clock; behind it a slender tower rises from the deck to
a balustraded platform, a short drum with arched louvred belfry openings, a
round dome, a ball and a thin flagpole.

The intent is a building that reads at a glance as the town hall, the civic
centrepiece of a district, rather than as a generic two-storey block. The
clock's dial is lit at night, warm and apart from the windows' rooms: it is
the one fixture the building has, and how its tower is found after dark.

### Composition

Horizontally, a five-part front (end pavilion, recessed range, projecting
centre entrance bay, recessed range, end pavilion) on a U-shaped plan open to
the rear: two rear wings flush with the pavilions' sides and a shorter centre
link reaching about half way into the court. The cornice runs on round the
whole building; the roof steps where the masses do. Width to eave height is
about 4.3 : 1 and the plan about 1.8 : 1, which is what makes the building
read as long and low.

Vertically, the centre narrows in three stages: entrance bay, clock attic,
tower. The roof rises 3.0 m from the fascia to the deck at 14.66 m; the
platform is at 17.3–18.0 m, the drum 2.2 m, the dome 1.4 m, and the flagpole's
tip at 24.6 m, of which the top 2.5 m is the pole. A tower over a wide, low
range works by staying slender: the crown is a punctuation mark, not a second
building.

A generic composite: no recognisable real building, no lettering.

## Category and secondary use

`buildings/service/`, a civic hall. No secondary use.

## Hero/landmark status

**Hero/landmark: yes, for the texture only.** Every tier is inside the
*ordinary* triangle ceilings (Per-tier triangle counts); the exception is the
2048 atlas. The walls run 188.5 m round the building at 11.4 m high, and at
the catalog's 64 texels a metre the tiling wall band alone takes 2048 x 750
texels; the four roof, fascia and soffit bands, the opening items with their
room variants, the clock attic, the tower and the far tiers' elevations fill
the rest (Texture set). A 1024 atlas would halve the building's texel density
against its neighbours.

`scripts/validate_asset.py` takes one hero flag for texture and triangles,
so this asset is validated with it
(`-- buildings/service/brick_clocktower_hall building hero`). Without it the
2048 atlas fails the 1024 texture cap; the triangle counts pass either way.

## Footprint

- Walls: **48.75 x 26.75 m**, x ±24.375 m, y -10.25 to 16.5 m: the 48.75 m
  front with its 1.625 m pavilion and 2.25 m entrance-bay projections, the
  rear wings and the centre link round the U-court. Floor area 1,024.25 m²
  per storey.
- At the ground, with the quoin blocks standing 0.078 m off every convex
  corner: **48.91 x 26.91 m**. `LOD2` and `LOD3` paint the quoins, so they
  measure the walls' 48.75 x 26.75 m there.
- Plan bounds, every tier: **49.65 x 28.37 m**: the eave's 0.45 m overhang
  along X and at the rear, the balcony's top rail (y -11.42 m) at the front.
  Pivot: the plan bounds' centre, (0, 2.765) m in the build frame.
- Height **24.6 m** to the flagpole's tip.

## Story height

**Two storeys, floors at 0.156 m and 5.547 m**: 5.39 m floor to floor, and
the eave at 11.406 m, 5.86 m over the upper floor.

| Floor | Level | Set by |
| --- | --- | --- |
| Ground | 0.15625 m (course 2) | the entrance's and the service door's thresholds, each on a modelled stone step one riser up from the ground |
| Upper | 5.546875 m (course 71) | the string course's top and the balcony's deck; the balcony door's threshold is one course (0.078 m) over it |

On the walls the ground storey is the granite plinth (0–0.9375 m), its
moulded cap (to 1.172 m) and brick to the string course (5.078–5.547 m); the
upper storey is brick from 5.547 m to the frieze (9.922 m), under the frieze
and cornice to 11.172 m and a shaded fascia under the soffit. **The plinth is
the wall's stone base course, not a raised floor**: the floor runs 0.78 m
below its top, and the doors are cut down through it.

This **deviates from the ~3.0–3.3 m standard**, deliberately: ceremonial civic
architecture of the period has tall ground-floor openings and a grand upper
storey, and forcing 3.0–3.3 m would make the building read as offices. The
deviation belongs to this kind of building; it is not for residential work.

Every height the walls share with the brick is a line of the catalog's
78.125 mm coursing (Construction, Brick module).

## Door leaf height

| Door | Leaf (w x h) | Threshold | Above the leaf |
| --- | --- | --- | --- |
| Entrance, centre bay (main) | 2.0 x **2.344 m**, a pair of panelled leaves | 0.156 m, the ground floor | transom bar 2.50–2.578 m at the cut's head (the arch's springing), then a flush arched fanlight with radial bars to 3.578 m |
| Balcony door, over the entrance | 1.25 x **2.266 m**, a glazed pair | 5.625 m, one course over the upper floor | transom 7.891–8.01 m, twice a glazing bar's weight, then a fanlight to the 9.141 m head |
| Service door, right rear wing's end | 1.375 x **2.344 m**, a pair of panelled leaves | 0.156 m, the ground floor | head rail 2.50–2.578 m, the cut's head |

All three are within 2.0–2.4 m; the entrance's ceremony is its fanlight,
its rusticated stone surround and its keystone, not a taller leaf. The
balcony door's 3.52 m opening reads as a leaf under a fanlight by its heavy
transom with a shadow line under it. Each door stands on its step on every
tier that recesses it: the entrance to `LOD2`, the service door to `LOD1`;
the flush doors beyond have the riser painted under the threshold
(Construction, Balcony and steps).

## Window sills

| Window | Opening | Sill – head | Over its floor |
| --- | --- | --- | --- |
| Ground floor | 1.375 m wide | **1.25 – 3.672 m** | sill 1.09 m, head 3.52 m |
| Upper floor | 1.375 m wide | **6.328 – 8.984 m** | sill 0.78 m, head 3.44 m |
| Upper floor, entrance bay's outer and the link's sides | 1.25 m wide | 6.328 – 8.984 m | as upper floor |
| Ground floor, the link's sides | 1.25 m wide | 1.25 – 3.672 m | as ground floor |
| Entrance bay's tall windows (beside the balcony door) | 1.25 m wide | **6.563 – 9.141 m** | sill 1.02 m |

Every sill is under the ~1.4 m chest-high line. The tall windows' transom
at about 8.31 m and the balcony door's at 7.89 m are within half a metre of
each other, and their heads share one entablature.

## Eave overhang

**0.45 m** all round, with a level painted soffit and a 0.25 m white fascia
under the dark half-round gutter, the middle of the 0.3–0.6 m convention. The
eave **breaks round the clock attic**: the roof is cut away in front of it
(`roof_object()`), so the attic rises straight from the cornice and the eave
returns against its sides in two small white end faces. On `LOD3` the soffit
and the fascia are one face from the wall's head to the fascia's top; the
eave's outline does not move.

## Construction

Closed solids unioned with Blender's exact boolean
(`asset_build.union(..., snap=asset_build.SNAP)`), welded at 0.1 mm, faces
sorted by their corners so a rebuild writes the same files:

1. **the body:** the wall ring on the union of the massing rectangles
   (`RECTS`; `check_layout()` checks the twenty walls in `facade_atlas.WALLS`
   are that outline), each wall one cell from the ground to 11.5625 m (inside
   the roof), holed for its items or notched at its foot for the doors, and
   cut into its own cell under each quoin block on the tiers that have them;
   capped with a floor and a lid (`close_solid()`). Nothing inside: the
   masses overlap only as rectangles in the code.
2. **the roof:** one solid over the wall outline: the level soffit, the
   fascia, twenty slopes rising 3.0 m over 3.5 m (40.6°) to one flat deck at
   14.656 m (the wall outline offset 0.45 m out, then 3.5 m in), and the
   underside inside the wall line, which the union buries in the body; then
   notched by `asset_build.difference()` in front of the attic.
3. **the clock attic** (8.0 x 1.875 m, 11.5625–14.609 m) on the entrance
   bay's front, its front flush with the wall below, and **the pediment** over
   it (apex 16.406 m), oversailing the attic's front and sides by 0.125 m;
4. **the dial** (`LOD0`): a 16-sided disc 1.875 m across, standing 0.10 m off
   the attic;
5. **the tower:** the shaft (3.0 m square) from inside the roof to 20.2 m,
   the platform, the dome, the ball and the pole;
6. **six chimneys** by `asset_build.open_stack()`, from inside the roof to
   16.328 m, each a 0.25 m shell round one flue sunk 1.0 m to a soot floor
   still 0.67 m over the deck, open on every tier;
7. **the balcony** over the entrance and the **two steps**, each on every
   tier that recesses its door (the entrance's to `LOD2`, the service
   door's to `LOD1`);
8. **twelve quoin blocks** (`LOD0`/`LOD1`);
9. **twelve downpipes** (`scripts/downpipes.py`) and the **roof ladder**
   (`scripts/roof_safety.py`); the caged wall ladder goes in after the weld as
   the lean kit (`RS.append(..., check=True)`).

### Brick module

The walls sample the band in true metres, at the catalog's module
(`scripts/brickwork.py`): a 0.25 m stretcher on a 0.078125 m course. Every
height the walls share with the coursing is a course line (plinth 0.9375,
cap 1.172, sills 1.25 and 6.328, heads 3.672 and 8.984, string course
5.078–5.547, frieze 9.922, cornice 10.469–11.172, eave 11.406, the attic's top
14.609, the pediment's apex 16.406, the chimneys' tops 16.328); every corner
of the plan, every opening's and item's side a whole or half stretcher of its
wall's bond, which each wall samples from its own U (`U_OFF`); and at every
concave corner the bond turns, the course that ends on a whole brick on one
face ending on a half on the other. Convex corners are under the quoins.
`check_layout()` asserts all of it.

### Openings as items

Every opening kind is an item: a rectangle on its wall fully covered by its
own atlas region (casing, cornice cap, sill and the opening's sash, leaves or
fanlight), so no brick is painted inside one and the wall's band shows only
round it. The architrave is a quarter metre wide, which puts both an item's
sides and its opening's on half stretchers. Kinds: `gf` and `uf` (1.375 m),
`gf125` and `uf125` (1.25 m), `door` (the arched entrance), `service`,
`group` (the balcony door between the tall windows, panelled pilasters
between them, aprons under, one entablature) and `pilaster` (flush). The
windows of a kind are painted three or four times; a wall cycles through
them so no two neighbours share a room (`check_layout()`).

The bays keep the original rhythm: two on each pavilion front, three on each
front range and each rear wing's end, eight on each side, four on the link's
end, three on each wing's court face, two on each court face of the main
range and two on each side of the link; upper-storey pilasters between bays.
The four short returns (1.625 and 2.25 m) are blank, and no item comes within
0.75 m of a convex corner (the quoin block and a quarter metre). The
entrance bay's outer upper windows are 1.25 m wide at x ±3.875 m, clear of the
quoins and the balcony group.

### Roof form

A truncated hip: a short band of slopes from the eave to one broad flat deck,
not hips meeting at a ridge, which keeps the roofline low over a building this
wide. Built from the outline, so the slopes exist only on the outer perimeter
and the deck is continuous. The deck is mapped in plan (Texture set).

### Clock attic and pediment

The attic is brick on all four faces: its front its own region (a trim base
course, a framed panel round the dial, a cornice under the pediment), its
sides and back the wall band's upper-storey brick, five metres lower. The
pediment's slopes are the roof sheet; its front is a brick tympanum in a
white raking cornice and a horizontal cornice along its foot, its underside
the cornice's soffit. Its back stands flush with the attic's.

### Tower

The shaft rises from inside the roof, brick between corner pilasters over a
granite band at the deck, a belt under the platform. The **platform**
(17.3–18.0 m) stands 0.35 m out all round: on `LOD0` a bottom rail, a dado
recessed 0.05 m with the balusters painted on it and a top rail; from `LOD1`
one block with the balusters on its faces. Above it the **drum** carries an
arched louvred opening on each face under a dentilled cornice. The **dome** is
round: the profile (r, z) = (1.45, 20.2), (1.36, 20.55), (1.12, 20.9),
(0.80, 21.3), (0.45, 21.6) at 16 sides on `LOD0`, four rings at 12 on `LOD1`,
three at 8 on `LOD2`, a four-sided frustum on `LOD3`, flats toward the four
fronts so its outline matches the drum's. A 0.5 m octagonal ball (`LOD0`; a
box on `LOD1`/`LOD2`) and the 0.18 m flagpole to 24.6 m on every tier.

### Balcony and steps

The balcony's slab (y -11.4 m, 4.8 m wide) runs into the wall under the
upper floor; three parapets 0.94 m high, each on `LOD0` a bottom rail, a dado
recessed 0.03 m with the balusters painted on it and a top rail, from `LOD1`
one block, from `LOD3` the slab and parapets one block. The top rail stops a
course under the tall windows' sills, so the side parapets run into the wall
clear of their recesses. A **stone step** one riser high (0.156 m) under the
entrance (3.5 x 0.45 m) and the service door (2.0 x 0.4 m) fills each door's
recess and runs into the wall: under three risers, so no handrail. **The step
is the door's floor**, so it stays on every tier that keeps the door's
recess and goes only where the door is flush (`steps_kept()`, which asks
`wall_mode()`, the predicate that cuts the recess): the entrance's to `LOD2`
with the street front's reveals, the service door's to `LOD1`, where the
right rear wing's end goes to its flush elevation. No recess at grade stands
open to the terrain on any tier, and the sidecar's 0.156 m thresholds hold
on every tier that models them. On the flush tiers the door items paint the
step's riser in granite under the threshold; at the elevations' 16 texels a
metre that is a faint pale line at the door's foot (2.5 texels), and the
door reads as standing at the ground.

### Quoined corners

One block per convex corner of the outline (twelve), 0.5 m back along each
face and 0.078 m proud of both, from the ground to the frieze (9.922 m), so
the entablature runs on round the corner above them. Each face samples a
toothed quoin strip, long and short stones alternating 0.3125 m courses with
brick between, the two faces of a corner a course out of step. `LOD2` and
`LOD3` paint the same strips on the elevations.

### Downpipes

Twelve, from the gutter on a swan-neck to a shoe (`LOD0`; straight from
`LOD1`): on the four short returns at the front beside the roof's valleys,
two on each side wall beside a pilaster, one on each rear wing's end, two in
the U-court beside the link. `check_layout()` runs `downpipes.problems()` on
each against its wall's items (pilasters at 0.15 m), its quoins and the
ladder. Painted on the elevations, so `LOD3` drops their geometry without
losing them.

### Roof safety kit

The chimneys are serviced from the deck, over 40.6° slopes, so a fixed route
from the ground is modelled, at the back of the building in the U-court: a
**wall ladder** on the left wing's court face (x -13.375 m, at y 9.25 m) in
front of the pilaster between its first two bays, from the ground past the
eave to 1.0 m over the roof edge (12.66 m); over 8 m, so it carries a **cage**
from 2.5 m up; then a **roof ladder** straight up the slope from the eave to
the deck's edge (4.36 m). The deck is flat, so no walkway. The wall ladder and
cage are the lean kit (`lean=True`), appended after the weld and checked
clear of the building; the roof ladder is unioned. Both take the gutter's
colour from `PIPE_STRIP`. `check_layout()` runs `roof_safety.problems()` on
the ladder and the cage. Standing in the court, the kit sets no bound.

### Layout checks

`check_layout()` asserts, before any geometry: the walls are the massing's
outline; corners, items and openings on the brick module and every concave
corner turning the bond; items clear of quoins, corners and each other, no
item on a wall under 2.5 m, no two neighbouring windows with one room; door
leaves 2.0–2.4 m with a transom over each; sills over their floors; the eave
0.3–0.6 m and the roof steeper than 1:8; every deck edge parallel to its eave;
the stacks and the tower on the deck, their flues clear of it; the attic over
the slope; the dial inside its panel; the balcony's rail under the tall
windows' sills; `downpipes.problems()` and `roof_safety.problems()`; the roof
ladder reaching the deck.

## Per-tier triangle counts

| Tier | Triangles | Ordinary ceiling | Hero ceiling |
| --- | --- | --- | --- |
| `LOD0` | **6,956** | 12,000 | 20,000 |
| `LOD1` | **3,802** | 4,000 | 6,000 |
| `LOD2` | **1,330** | 1,500 | 2,500 |
| `LOD3` | **500** | 500 | 700 |

Every tier is inside the ordinary ceiling; `LOD3` is at it.

Where they go, counted on the solids before the union (the union then adds
the cuts: the quoin blocks, pipes, chimneys, tower, attic and kit meeting the
walls, soffit and deck):

| Part | `LOD0` | `LOD1` | `LOD2` | `LOD3` |
| --- | --- | --- | --- | --- |
| walls with their openings | 3,036 | 2,100 | 524 | 76 |
| roof | 156 | 156 | 156 | 116 |
| tower (shaft, platform, dome, ball, pole) | 276 | 140 | 92 | 48 |
| chimneys | 168 | 168 | 168 | 168 |
| downpipes | 912 | 144 | 144 | – |
| roof safety kit (roof ladder; wall ladder and cage) | 464; 832 | 104; 250 | – | – |
| balcony | 120 | 48 | 48 | 12 |
| quoin blocks | 144 | 144 | – | – |
| attic, pediment, dial, steps | 104 | 44 | 32 | 20 |

The walls are the largest share: 106 items, each recessed costing about 24
triangles (the casing round the opening, four reveals, the back face, the
hole in the wall) and flush about 8. The kit and the pipes are the next: they
are placement-specific and under the relief threshold, modelled as the
contract asks, and thinned by tier.

The old asset carried 5,248 / 4,024 / 592 / 572 with 659 / 541 / 140 / 134
triangles of them hidden; this one's `LOD0` is larger for the pipes, the kit,
the round dome, the rails and the openings' casings, and its `LOD1` and
`LOD3` are inside the ordinary ceilings.

## LOD review

Review camera: `scripts/review_asset.py`, perspective, 1920 x 1080, 50°
vertical FOV, distance along the view to the centre of the visible front or
rear wall, Cycles at 16 samples, noon; front, oblique (40°, 30° up) and rear
(150°, 30° up). Switch distances: the catalog's defaults, `LOD0` to 35 m,
`LOD1` to 70 m, `LOD2` to 120 m, `LOD3` beyond.

Renders, kept out of the commit, in
`review/clocktower_rebuild_2026_11_22/`: `before_renders/` from a copy of the
asset as it was, `after_final/` with identical settings, and the sheets in
`compare/` (`scripts/review_compare.py`).

| Switch | What changes | Looked at |
| --- | --- | --- |
| `LOD0` → `LOD1`, 35 m | the U-court's walls to their elevations; dial, ball and rails flat; pipes straight; the kit thinned to every fourth rung and sixth hoop | front and oblique at 35 m: indistinguishable at native size |
| `LOD1` → `LOD2`, 70 m | every wall to its elevation, the street front's openings still recessed, the entrance on its step; quoin blocks painted; the service door flush and its step gone; dome 12 → 8 sides; the kit gone (it stands in the court) | front, oblique and rear at 70 m: the walls, quoins, trim and windows read the same; the court's kit is not visible from the street views |
| `LOD2` → `LOD3`, 120 m | the street front's openings flush, the entrance's step with them (its riser painted, faint at 16 texels a metre); dome 8 → 4 sides; no ball, no pipes (painted); balcony one block; soffit and fascia one face | front, oblique and rear at 120 m: the same building; the dome's flats are the visible change, about 25 px wide there; the entrance's step, about 2 px tall, goes as a pale line under the door, with the reveals (2026-11-23, front and oblique) |

### The street front's reveals on `LOD2`

`LOD2` keeps the openings of the five street-front walls recessed (464
triangles) and the entrance on its step, the recessed door's floor (22):
1,330 against 844 flat. Compared at 70 m, oblique and front-on,
noon and reversed light, with the same tier built flat
(`review/clocktower_rebuild_2026_11_22/compare_lod2_reveals/`): with the
reveals the windows keep the shaded heads and reveals `LOD1` shows at the
switch; flat, they lift a little toward their casings. The difference is
small, but it is the switch the old asset's review found visible, and the
tier stays inside its ceiling with it, so the reveals stay. They go at
`LOD3`, beyond 120 m.

### Geometry kept under the relief threshold

- Downpipes (0.10 m), the roof safety kit (rails 0.05 m), the balustrade
  rails (0.02–0.05 m), the quoin blocks (0.078 m), the dial (0.10 m) and the
  steps (0.156 m): placement-specific or contract-required, each thinned by
  tier as above.

## Interior geometry

None: the body is the union outline's wall ring and every other part is a
closed solid unioned into it, so the overlaps of the massing rectangles, the
roof's underside inside the walls, the walls' tops inside the roof, the
buried feet of the tower, the chimneys, the attic, the quoin blocks and the
balcony's slab are all removed by the union.

`scripts/validate_asset.py`'s hidden-surface candidates (40 rays from each
face): **308 / 59 / 26 / 0** triangles (4.4 / 1.6 / 2.0 / 0 %) on `LOD0` to
`LOD3`, against 659 / 541 / 140 / 134 before the rebuild. Every one inspected
by place (`review/clocktower_rebuild_2026_11_22/hidden.py`) is exterior
surface that the rays cannot leave from:

- each downpipe's flat facing its wall across the 30 mm gap (one per run, on
  every tier with pipes);
- the roof safety kit's rungs, brackets, hoops and straps between the rails
  and in front of the wall, and the roof ladder's brackets over the sheet;
- on `LOD0`, the undersides of the balcony's and the platform's top rails
  where they oversail the dado by 0.03–0.05 m, and the dado's inner face
  under the top rail, a metre from the wall.

No closure faces are kept.

## Known simplifications

- No interior: the glass is opaque and painted as the room behind it.
- Window casings, cornice caps, sills, the string course, frieze, dentils,
  cornice, pilasters, the plinth's granite courses, the balusters and the
  belfry louvres are texture and normal map, not geometry; the openings'
  recesses, the quoin blocks, the balustrades' rails, the dial and the steps
  are geometry.
- The fanlights are flush: the entrance is cut to the arch's springing.
- The deck is one flat sheet: no falls, outlets or roof hatch; the deck
  drains to the perimeter gutter through no modelled outlet.
- The gutter is painted on the fascia; the downpipes' swan-necks and shoes
  are modelled to `LOD0` only.
- The roof safety kit has no walkway (the deck is flat) and no handrails on
  the deck.
- `LOD2` and `LOD3` walls are their elevations at 16 texels a metre, with the
  downpipes painted on (Texture set).

## Texture set

**2048 atlas** (the hero exception), 64 texels a metre on every wall, the
attic, the tower and the chimneys; supersampled `atlas.SS` = 4 per axis and
box-filtered in linear light. One set of four PNGs serves every tier.

| Rows | Band / region | Content |
| --- | --- | --- |
| 2–752 | `WALL` | z 0–11.72 m, tiling in U every 32 m: granite plinth, its cap, brick (`brickwork.paint()`, brick / darker brick / mortar ids, tones repeating every 160 courses), string course, frieze with dentils, cornice, the fascia under the soffit, and trim above the eave for the attic's foot |
| 760–908 | `ROOF` | painted standing-seam steel, seams every 0.5 m along U, V up the slope at 32 rows a metre (4.61 m), a snow guard 0.6 m up, the drip edge |
| 914–930 | `FASCIA` | the white fascia board, the dark half-round gutter over it; `PIPE_STRIP` its middle rows |
| 936–965 | `SOFFIT` | painted soffit boards, V out from the wall |
| 972–1348 | `ELEV` | the twenty walls' elevations at 16 texels a metre, two rows |
| above | items and the rest | the window items (`gf` x4, `uf` x4, `gf125` x2, `uf125` x3), the entrance, the service door, the balcony group, the pilaster; two quoin strips; the tower face; the chimney face; a dome facet; the deck in plan at 16 texels a metre; the attic's front; the pediment's front; two balustrade dados; 16 px flat patches |

Deviations from 64 texels a metre, each where only distance or a steep view
sees the surface: the elevations (16, the far tiers only), the deck (16, seen
only from above), the roof band along the slope (32 rows a metre; 64 along
the eave).

### Elevations

`compose_elevations()` builds each wall's elevation after the maps are
resolved: the band at the wall's U, its items at their places, the quoin
strips at its convex corners and its downpipes as dark 0.1 m stripes, at 64
texels a metre, then box-filtered 4 x 4 to 16 (albedo and emission in linear
light, normals renormalised) into its region with a two-texel edge gutter.
The far tiers show exactly what the near ones do, room by room.

### Relief

Heights the normal map is derived from (metres over the face): brick faces
0.006 over recessed joints; trim courses, casings, quoin stones and pilasters
0.035; cornices, heads and the string course 0.06; dentils 0.03; window
frames 0.025; standing seams 0.025; the gutter's roll 0.06; balusters 0.03.
Glass and the dial's face are flat.

### Padding and filtering

`atlas.pad()` fills every unclaimed texel from the nearest region's edge in
every channel; the elevations carry a two-texel edge gutter of their own;
regions keep at least 4 px apart (`check_regions()`); the tiling bands bleed
two rows each way.

Mip stress (`scripts/review_atlas_mips.py`, whole-atlas mips rendered with
`review_asset.py --texture-dir`): mip 2 on `LOD1` and `LOD2` at 70 m and mip 3
on `LOD2` and `LOD3` at 120 m, front and oblique. No region bleeds into its
neighbour: no roof grey on the walls or cornice, no dark seams at the
elevations' or items' edges, the fascia's gutter still a dark line. The
elevations, at 16 texels a metre, wash out to a pink-grey at those stress
mips (4 and 2 texels a metre); in use they are sampled near 1:1 (16.6 px a
metre on screen at 70 m, 9.7 at 120 m), where the unstressed renders show
them sharp. The consumer's own filtering and compression are pending.

### Weathering

Only `scripts/weathering.py`, at the catalog's moderate level: a light
grime over everything; fading on the trim, frames and doors; faint rain wash
on brick; soil, splash and algae at the plinth; splash and a little salt
bloom above it; runs under the string course and the frieze; dust under the
cornice; the roof band's own `Weather.roof()`; runs under the gutter; each
window item's `Weather.window()` (dirt on the sill, runs down the casing,
water on the sash's rail) and each door's `Weather.door()`; splash at the
quoins' foot, the tower's base and the chimneys' flashing; runs under the
platform, the drum's cornice, the chimneys' caps, the attic's cornice and the
balustrades' rails; dust and light chalking on the deck; dust in the mortar
joints after padding. Glass and the dial's face stay clean.

Unique textures: four 2048 PNGs (albedo `red_brick`, ORM, normal, emission).

## Glazing treatment

`scripts/glazing.py`'s `rooms()` on the finished albedo, `night_rooms()` on
the emission. Measured by the validator over the emission mask's neutral
pixels: **glass sRGB 58, linear 0.039, 0.27 x the trim**; roughness
`glazing.ROUGHNESS` (0.08), metallic 0. The frames are painted timber
(sRGB 178, 172, 160), lighter than the glass. Each window kind is painted in
three or four places in the atlas, so each has three or four rooms, and a
wall cycles through them. On four of those (one per kind) pale curtains are
drawn back to either side of the lower lights: the room, in the albedo only;
the night's panes have none.

## Variant list

| Variant | Meaning |
| --- | --- |
| `red_brick` (default) | deep civic red brick with about one brick in six darker, lime mortar, weathered off-white trim, grey granite plinth, dark painted-steel roof |

A singular landmark; one coherent treatment.

## Night lighting

- `_emission.png`, bound on every tier (`emissiveTexture`, UV 0) with the
  factor zero (`window_emission.rewrite_glb_emission()`), so the building
  ships unlit.
- Glazing: every pane neutral white in the mask, then a room by
  `glazing.night_rooms()` (its own level, a lamp's glow, the floor's
  falloff). The far tiers' elevations carry the same rooms.
- **The clock's dial** is the one other luminous region: its enamel face
  (`ID_CLOCK`) is written in its own warm light, sRGB (255, 208, 146); the
  hands, hour marks and ring stay dark. Mask region: the dial on the attic
  front (`ATTIC_F`), which the modelled dial (`LOD0`) and the attic's face
  (every tier) both sample. It shares the mask's one control with the
  windows; the validator reports it as a coloured fixture.
- The belfry is not lit.
- Reference lit factor: `LIT_FACTOR` = (1.0, 0.88, 0.72) linear, passed as
  the asset's `tint`; `variants.png` shows the night row with it.
- Control granularity: one factor for the whole building; windows share
  their items' rooms, so no per-window control.
- No light spill is simulated; glow is an emissive surface only.

Reviewed at night (`review_asset.py`, moon light, the reference factor) at
35 and 120 m on every tier: every pane a room of its own level, the dial a
warm disc clearly apart from them, the belfry dark; the far tiers'
elevations carry the same rooms in the same places, so the lit pattern does
not change at a switch.

## Export

- Bindings, traced in the `LOD2` GLB's JSON chunk and the same on every
  tier: one material `brick_clocktower_hall`;
  `pbrMetallicRoughness.baseColorTexture` → `..._albedo_red_brick.png`,
  `metallicRoughnessTexture` and `occlusionTexture` → `..._orm.png`,
  `normalTexture` → `..._normal.png` (scale 1), `emissiveTexture` →
  `..._emission.png` with `emissiveFactor` [0, 0, 0]; one primitive with
  `POSITION`, `NORMAL`, `TEXCOORD_0`; images by `uri` only, no `bufferView`;
  one sampler, linear and trilinear-mipmapped.
- `asset_build`'s export: GLB, selection only, `+Y` up, modifiers applied,
  keep originals (external PNGs), no cameras or lights; then
  `strip_embedded_images()` and the emission factor rewritten to zero.
- Rebuild: `python3 facade_atlas.py export` (system Python with numpy, scipy
  and Pillow), then
  `blender --background source.blend --python build.py`, which builds,
  exports, renders `preview.png` and `variants.png`, saves and writes the
  sidecar. `build.py -- facts` rewrites the sidecar alone from a committed
  tree.
- Facts sidecar, version 1: footprint the wall outline; storeys at 0.156 and
  5.547 m, 1,024.25 m² each; no dwellings; three doors (the entrance, main;
  the balcony door; the service door); hero.
- `preview.png`: the catalog setup with this asset's pinned camera
  (`camera_location`), `LOD0`, emission off.

## Review status

Done here:

- `scripts/validate_asset.py ... building hero`: 0 FAIL, 1 WARN
  (`source.dirty`, until the sidecar is rewritten from a committed tree),
  11 MANUAL; its door-floor probe finds the entrance and the service door
  on their steps (0.156 m) on every tier that recesses them, the balcony
  door on its sill through `LOD2`, every door flush on `LOD3`. Without
  `hero` only the four 2048 PNGs (and the sidecar's hero flag) fail; every
  tier's triangles pass the ordinary ceilings.
- The six views and the aerials of every tier, plus close views of the
  entrance with a 1.8 m figure, the U-court, the crown, the attic, a
  pavilion's corner, the side, the service door, the ladder and the deck
  (`build.py`'s `render_views()`), over three passes.
- Before and after review sets with identical settings (day at 20, 35, 70
  and 120 m front, oblique and rear, every tier; night at 35 and 120 m) and
  their comparison sheets; the LOD pairs at 35, 70 and 120 m; the `LOD2`
  street-front reveals against a flat `LOD2`; mip 2 and mip 3 stress renders.
- The entrance's step kept on `LOD2` (2026-11-23): before and after sets
  with identical settings (the six views; every tier at 20, 35, 70 and
  120 m, front and oblique; eye-level, low and oblique views of the
  entrance and the service door over a terrain plane, noon and reversed
  sun, every tier) and their comparison sheets, in
  `review/review_2026_11_23/brick_clocktower_hall_pass2/`; `LOD0`, `LOD1`
  and `LOD3` byte-identical.
- Hidden-surface candidates inspected by place (Interior geometry); the
  material bindings traced in a GLB (Export); the glazing measured (Glazing
  treatment); laps, joints and mouldings read raised in the lit renders.
- The palette against the catalog's red-brick buildings: a deeper, browner,
  more varied red than before, the trim off-white and weathered.
- Generic composite: no recognisable real building, no lettering.

Pending in the consumer:

- runtime LOD switching, mip filtering and texture compression of the 2048
  atlas; frame time and memory;
- the night state under the consumer's lighting, and the dial's warmth
  against the windows;
- the facts sidecar against the consumer's importer.

## Tooling versions

- **Blender 5.3.0** (build 2026-11-11), headless, for the rebuild, the
  review renders and validation.
- **Blender Lab "MCP" extension v1.0.3**, not used for this rebuild, which
  drove `build.py` headless.
- **CPython 3.14 with numpy, scipy and Pillow** for the texture export.

Known-good markers, not requirements: anything at or above CLAUDE.md's 5.3
floor should build this asset.

## Revision log

- **2026-11-23 — the entrance keeps its step on `LOD2`.** `LOD2` kept the
  entrance's 0.28 m recess but dropped the step under it, so the door stood
  0.156 m over a reveal open to the terrain. Each step now stays on every
  tier that recesses its door (`steps_kept()`): the entrance's to `LOD2`.
  `LOD2` 1,308 → 1,330; the other tiers, the bounds, footprint and doors
  unchanged.
- **2026-11-22 — rebuilt to the current contract.** After an audit: one
  closed shell by union (no buried partitions), walls in true metres on the
  catalog brick module with every opening kind its own atlas item and room
  variants, the far tiers on composed elevations, a painted gutter with
  modelled downpipes, the caged ladder and roof ladder, the deck mapped in
  plan, a round dome, a brick attic under a roofed pediment with the eave
  broken round it, modelled balustrade rails and steps, painted steel as
  dielectric, weathering through `scripts/weathering.py` only, the clock lit
  warm, a new palette. Heights and plan snapped to the brick module: the
  entrance front 5 cm forward, the walls' outline 48.80 x 26.70 → 48.75 x
  26.75 m, the plan bounds 49.70 x 28.35 → 49.65 x 28.37 m, the pivot 1 cm,
  the doors by a few centimetres. Counts 5,248 / 4,024 / 592 / 572 →
  6,956 / 3,802 / 1,308 / 500.
- **2026-11-21 — balcony door transom; rear service door.**
- **2026-11-20 — floor levels** at the doors' thresholds.
- **2026-09-25 — weathering; open chimney flues; room-lit night windows.**
- **2026-09-24 — supersampled atlas with a normal map, shared build code.**
