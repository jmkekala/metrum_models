# viljakuivuri_tower

## Style brief

The grain dryer (*viljankuivuri*) of a small Finnish grain farm, from the same
post-war countryside as the rintamamiestalo houses, built as a generic
composite. It is the piece that makes a farmyard read as a grain farm from a
city-builder play camera 35–120 m away, so the silhouette leads: a tall,
narrow board tower under its own small gable roof, a low intake lean-to at
its foot, and a round galvanised bin beside it, fed by a sloping spout from
high on the tower.

- **Tower:** 5 × 5 m, 10.5 m to the eave, under a 30° dark steel gable roof.
  It is sized by the grain elevator inside it, not by storeys.
- **Intake lean-to:** against the tower's east side, under a mono-pitch roof
  falling away from the tower. Its front holds the tipping-pit door, a pair of
  white-framed and braced board leaves that a trailer backs up to.
- **Operator door:** a plain ledged-and-braced board door into the tower's
  base on the front, for the furnace and the controls.
- **Windows:** small plain-glass windows stacked up the front for the stair
  landings, with furnace-room windows at the foot of the west and rear walls
  and one landing window on the west.
- **Exhaust:** a louvred panel high on the rear gable.
- **Flue:** the furnace's black steel flue rises through the lean-to's roof.
- **Bin:** corrugated galvanised steel with bolted ring and sheet seams and a
  shallow ribbed cone roof. The spout runs into a fill collar at its apex.
- **Finish:** red-ochre vertical board-and-batten with white corner boards,
  casings and fascias, on a low concrete plinth. Drip boards cover the board
  joints at 4.8 m and 8.8 m. Half-round galvanised gutters run along the
  three eaves, each with a downpipe: the tower's west one and the lean-to's
  to the ground, the tower's east one onto the lean-to's roof. Every roof slope carries a snow guard near its eave. The
  gutters, downpipes and snow guards are one galvanised steel, the same as
  on the farm's barn and machine shed and darker than the bin's newer zinc.
  There is no ground or slab.

## Category and secondary use

`buildings/agricultural/`, a category new with this asset and its two farm
siblings. No secondary use.

## Hero/landmark status

**No.** Ordinary budgets and a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Tower, walls | 5.00 × 5.00 m |
| Lean-to, walls (set back 0.40 m from the tower's front and back) | 3.90 × 4.20 m |
| Tower and lean-to walls together | 8.90 × 5.00 m |
| Overall, with overhangs, the bin and its eave | 9.70 × 8.80 m |

Heights:

| Feature | Height |
| --- | --- |
| Tower eave (underside at the wall) | 10.50 m |
| Tower ridge top | 12.19 m |
| Lean-to eave, outer wall | 3.60 m |
| Lean-to underside where it meets the tower | 4.65 m |
| Bin eave | 5.45–5.50 m |
| Bin cone apex | 6.25 m |
| Fill collar top | 6.45 m |
| Flue top | 7.00 m |

The bin is a 3.00 m diameter cylinder (3.20 m at its eave), centred 1.90 m east
of the tower's east wall and 1.80 m behind its back wall line. Its wall stands
0.45 m behind the lean-to's rear rake.

The pivot is centred on the plan's bounding box, bin included, at ground
level. It sits 1.95 m east and 1.50 m behind the tower's centre. It is taken
from `LOD0` and applied to every tier. The bin's rings start their corners at
+Y on every tier, so its eave sets the same +Y extent at 16, 12, 8 and 6 sides;
`build_all()` asserts that all four tiers share LOD0's extents.

The facts sidecar's footprint is the tower and lean-to wall outline only:
eight corners, with the lean-to's setback steps. **The bin is equipment
standing apart and is left out** of the footprint, as are the overhangs.

## Story height

**One occupied storey**: the ground floor of the tower base and the lean-to,
floor slab at 0.10 m. The lean-to is a single storey, 3.60 m to its outer
eave. The tower above the ground floor is machinery space for the elevator
and the dryer column, not occupied storeys, so it is not held to the
3.0–3.3 m rule. Its 10.5 m is the height of the machinery, the typical range
for a farm dryer being 8–12 m.

The board joints at 4.80 m and 8.80 m, with the stair-landing windows 0.5 m
above each, give the tower a 4 m rhythm, which reads as stair landings at
play distance. The windows sit at the same heights on every tier.

## Door leaf height

| Door | Leaf (w × h) | Threshold | Notes |
| --- | --- | --- | --- |
| Operator door, front of the tower (entrance, main) | 0.90 × 2.10 m | 0.10 m | no transom; casing 0.19 m above |
| Tipping-pit door, front of the lean-to (vehicle) | 3.00 × 3.20 m (two 1.50 m leaves) | 0.10 m | no transom; casing 0.19 m above |

The 2.10 m operator door is the human-scale anchor. The 3.20 m opening is a
vehicle door for a tractor and trailer, not a pedestrian leaf, so the
2.0–2.4 m rule does not apply to it. It stands beside the operator door on the
same front, so the difference in scale reads directly.

## Window sills

All windows are the same 0.70 × 0.80 m single pane.

| Face | Sills | Heads |
| --- | --- | --- |
| Front | 1.30, 5.30, 9.30 m | 2.10, 6.10, 10.10 m |
| West | 1.30, 7.30 m | 2.10, 8.10 m |
| Rear | 1.30 m | 2.10 m |

The ground-floor heads line up with the 2.10 m door head. The ground-floor
sill is 1.20 m above the floor, under the ~1.4 m chest-high limit. The
landing windows sit 0.5 m above each board joint.

The rear louvre is 1.50 × 1.20 m, sill 9.20 m and head 10.40 m. Its casing
stays clear of the rake.

## Eave overhang

| Where | Projection |
| --- | --- |
| Tower eaves (east and west) | 0.40 m |
| Tower rakes (front and back) | 0.40 m |
| Lean-to eave (east) | 0.40 m |
| Lean-to rakes (front and back) | 0.25 m |
| Bin cone, beyond its wall | 0.10 m |

All the building's overhangs are within 0.3–0.6 m except the lean-to's rakes,
at 0.25 m. These are kept short so they end 0.15 m behind the tower's face
planes (see Construction). Soffits slope with the rafters. Every tier keeps
every overhang.

The three eave fascias (tower east and west, lean-to east) carry a painted
0.125 m half-round gutter across their top, inside the projection above; the
rakes and the bin's eave have none.

## Construction

`build.py` builds up to fourteen closed solids (and the walkway's posts) and
unions them with Blender's exact boolean (`asset_build.union`), then appends
the roof safety kit's lean wall ladder after the weld:

- the tower body;
- the lean-to body;
- the tower's roof slab, a chevron along Y;
- the lean-to's mono-pitch slab;
- the bin's wall;
- the bin's cone;
- the fill collar;
- the spout;
- the flue;
- three downpipes (`scripts/downpipes.py`);
- the roof safety kit's roof ladder and walkway (`scripts/roof_safety.py`).

Wall rings rise 0.10 m into their slabs. The union trims them at the soffits,
removes the lean-to's buried west wall and the tower's east wall behind it,
and cuts the spout's way through the tower's back wall. It joins the bin to
the building through the spout and the collar, so each tier exports as one
mesh and one closed shell.

The mesh kit is the catalog's shared `scripts/shell_build.py`:

- every vertex on a shared edge is a corner of both faces;
- walls are polygons with holes (`fill_region()`), openings recessed with
  `recess()`;
- `close_solid()` caps a wall ring by walking its rim;
- `Builder.face()` tests for zero area in double precision.

Parameters the tiers derive from:

| Parameter | Value |
| --- | --- |
| Tower half-size | 2.50 m |
| Tower pitch | 30° |
| Tower eave | 10.50 m |
| Lean-to run | 3.90 m |
| Lean-to setback | 0.40 m |
| Lean-to pitch | 15° |
| Lean-to eave | 3.60 m |
| Bin radius | 1.50 m |
| Bin eave | 5.50 m |
| Bin cone pitch | 25° |
| Bin ring | 1.00 m |
| Spout | from (1.60, 2.20, 9.60) to the collar |
| Flue | (3.20, −1.00), 7.00 m top |
| Downpipes | `DOWNPIPE_SPOTS`: west wall s 4.75 m, lean-to east wall s 0.25 m, tower east wall s 0.75 m |
| Sides per round part | `SIDES` |

### The lean-to stands into the tower, not against it

The first build stood the lean-to with its inner wall on the tower's east wall
plane, its front and back flush with the tower's. The exact solver kept the
two coincident opposite walls as a zero-thickness double wall: four edges
with four faces each, along the junction. The lean-to now runs 0.15 m into the
tower, which removes the coincident walls. It is set back 0.40 m from the
tower's front and back faces, which removes the flush coplanar faces, and its
0.25 m rakes then end 0.15 m behind the tower's face planes. The setback reads
as an addition to the tower, which suits it. It also gives the tower a true
corner, with its corner board, on all four edges.

### Walls cut at the board joints

The tower is 12 m to its apex, and no band at 64 px/m holds that in a 1024
atlas. Every wall is therefore an outline clipped into height bands:

- S1 from the ground to 4.80 m;
- W2 from 4.80 to 8.80 m;
- W2 again from 8.80 m to the top.

Each strip maps onto the same W2 rows from its own joint (`wall_bands`,
`clip_z`). The joints are where vertical boards really end, covered by a drip
board, so the repeat lands on a line the eye expects. Openings may not cross
a joint, which `check_layout()` checks. The lean-to's walls, 4.75 m at most
where they meet the tower, stay in S1 entirely.

### The bin, its spout and the flue

- **The bin's wall** is an n-sided prism cut at its ring joints: 0.5 m, then
  every 1.00 m to the 5.50 m eave. Each strip maps one ring of the BIN band
  from its own foot, and U runs once round the bin over the atlas's full
  width.
- **The cone** is a short rolled lip and n triangles to the apex, projected
  from above onto the BINROOF disc. The collar's lid lands on the disc's
  centre.
- **The spout** is a 0.20 m pipe from inside the tower, out through the back
  wall at 9.13 m and 0.50 m in from the corner. It falls at 43° into the
  collar, steep enough for grain to run.
- **The flue** is a 0.30 m black steel pipe from inside the lean-to up through
  its roof to 7.00 m, 0.55 m clear of the tower wall. It is open at the top:
  a thin rim round a mouth lined and floored with soot 0.50 m down, its floor
  well above the slab, on every tier.

### Gutters and downpipes

The gutter is painted, not modelled: a 0.125 m half-round galvanised gutter
across the top of the FASCIA band, which only the eave fascias sample (the
rakes take the barge patch). So it runs along the tower's two eaves and the
lean-to's low eave, and nowhere else; the bin has none.

The downpipes are modelled with `scripts/downpipes.py` (`DP.eave_pipe`), each
hung from its eave's gutter on a swan-neck into the soffit, standing 0.03 m
off the wall on its clips, with a shoe at the foot. Their sides sample the
gutter's middle rows, `PIPE_STRIP` in `facade_atlas.py`, so they take its
galvanised colour and its hangers read as the pipe's clips.

| Pipe | Wall | Where | Height |
| --- | --- | --- | --- |
| Tower | west eave wall | 0.25 m from the front corner (s 4.75 m) | soffit 10.32 m at the outlet to the shoe |
| Lean-to | its outer, east wall | 0.25 m from the front corner (s 0.25 m) | soffit 3.52 m at the outlet to the shoe |
| Tower, east | east eave wall, above the lean-to | 0.75 m from the front corner (s 0.75 m) | soffit 10.32 m at the outlet to the shoe's mouth at 4.99 m, over the lean-to's slope |

All three stand near the front end of their eave, so the front view and the
catalog's oblique see them. The module has no limit on a pipe's length, so
the 10 m tower pipes are the same sweep as the lean-to's.

#### The east pipe spills onto the lean-to's roof

The lean-to's roof covers the tower's east wall all but 0.40 m at each end,
too little for a pipe `DP.CORNER` (0.25 m) from the corner and clear of the
lean-to's 0.25 m rake, so no pipe from the east gutter can reach the ground.
It comes down the tower's wall above the lean-to instead and discharges onto
the lean-to's slope, which carries the water to the lean-to's own gutter and
pipe, as a pipe from an upper roof does on a lower one.

`scripts/downpipes.py` runs a pipe to the ground only, so `build.py`'s
`RoofPipe` subclasses its `Pipe` and lifts the foot: the part of the path
below the swan-neck's offset (the shoe at `LOD0`/`LOD1`, the straight pipe's
open end at `LOD2`/`LOD3`) rises by 4.79 m, so the straight end stops
`ON_ROOF` = 0.10 m over the slope at the pipe's wall-side face (4.99 m), and
the shoe starts at 5.14 m and kicks 0.15 m out, down the slope, its mouth
about 0.11 m clear of the sheet. Everything else (the swan-neck, the
section, the UVs on `PIPE_STRIP`, `DP.MODES` per tier, `DP.problems()`) is
the module's. The pipe stands 0.75 m from the front corner, 0.35 m inside
the lean-to's front wall plane (`ON_ROOF_IN` asks 0.30 m), so the shoe lands
on the roof and not on the rake. The foot is not joined to the roof: like
every pipe it hangs from the soffit only.

### Snow guards

Every roof slope carries a painted snow guard, as a Finnish metal roof does:
two round tubes 0.5 m up the slope from the eave, on brackets on every
second rib (0.5 m apart), in the gutter's galvanised steel (`ID_GUTTER`) as
a matched system. It is painted in both roof regions (`ROOF_T`, `ROOF_L`),
whose V runs up from each slope's own eave (`slab()`'s `slope_v`), so the
rail lands 0.5 m above the eave on the tower's two slopes and on the
lean-to's. The lean-to's matters most: it is
the low roof beside the vehicle door, where the tractor and trailer stand.
No geometry: `rintamamiestalo_porch` paints its snow guard the same way.

### Roof safety kit

The furnace flue through the lean-to's 15° roof (steeper than 1:8) is a
sooted chimney, swept from the roof, so it is a serviced item and the roof
carries the kit (`scripts/roof_safety.py`), at the back, away from the
street and the catalog view. The tower's 30° roof carries nothing serviced.

- **Wall ladder**, on the lean-to's blank rear (rake) wall, centred 0.60 m
  from its low (east) corner (x 5.80 m), passing 0.12 m outside the 0.25 m
  rake and running 1.0 m above the roof there (5.08 m long, no cage). The
  lean-to's eave wall (+X) has a run, but a ladder passing outside its eave
  would stand 0.18 m past the fascia, the plan's +X extent, and move the
  bounds and the pivot; on the rear wall it stays inside the +Y bound the
  bin sets (rails at y 2.53 m against the bin's 5.90 m), so bounds, pivot,
  footprint and doors are unchanged. It is the lean kit
  (`WallLadder(lean=True)`): separate solids that touch nothing, appended
  after the weld with `RS.append(check=True)`.
- **Roof ladder**, up the slope from the lean-to's eave just inside the rear
  rake (s 4.10 m along the east eave, y 2.00 m), beside the wall ladder's
  top, to the walkway: 2.9 m long, on brackets into the slab.
- **Walkway**, a level plank along the slope from the roof ladder's top
  across the flue's width (y −1.30 to 2.25 m), its upslope edge 0.20 m below
  the flue (x 3.55 m), on posts into the slab.

The kit takes the gutter's galvanised colour through `PIPE_STRIP`. Tiers
follow `roof_safety.MODES`: every rung and the brackets at `LOD0`, every
other rung at `LOD1`, every fourth rung without brackets or posts at
`LOD2`, and no kit at `LOD3` (its rails under half a pixel past 98 m;
`LOD3` keeps 490 of its 500 triangles as before, with every downpipe).

### What the catalog's shared kits do not apply to

- **No handrails**, because both doors have their threshold one 0.10 m step
  above the ground.

### check_layout()

`check_layout()` asserts, before building:

- openings overlapping, running into a corner board, reaching the soffit or
  the rake, crossing a board joint, or (other than doors) reaching the
  plinth;
- the lean-to's walls outgrowing S1, or its rakes reaching the tower's face
  planes;
- the tower's apex outgrowing W2's second repeat;
- either slope's length or either slab's length disagreeing with its roof
  region, or the two regions overlapping or leaving the atlas;
- the wall ladder within `roof_safety.CORNER` of its wall's ends
  (`RS.problems()`), outside the bin's +Y bound or within 0.3 m of the bin;
  the roof ladder off the rake or crowding the lean-to's downpipe; the
  walkway short of the flue's width, into the flue or near the tower wall;
- the bin within 0.2 m of the lean-to's rake, its eave not above the lean-to,
  or the bin within 0.3 m of the tower;
- the spout falling at under 35°, or leaving the back wall near a corner,
  the louvre or a joint;
- the flue within 0.4 m of the tower, its foot outside the lean-to, or its
  soot floor down in the slab;
- a downpipe within `DP.CORNER` of its wall's ends or within `DP.CLEAR` of an
  opening on its wall (`DP.problems`), or within 0.3 m of the bin's eave;
- the east downpipe less than `ON_ROOF_IN` inside the lean-to's front and
  rear wall planes, or either of its feet (the shoe's mouth, the straight
  end) not 0.03–0.25 m above the lean-to's slope.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 1,836 | 12,000 | casing rings, reveals and closures on all eight openings; bin 16-sided, spout and flue 8-sided, collar 8; downpipes 8-sided with swan-neck and shoe; the roof safety kit with every rung, brackets and posts (644) |
| `LOD1` | 1,460 | 4,000 | the same casing rings, reveals and closures as `LOD0`; bin 12, spout and flue 6; downpipes 4-sided, bent; the kit with every other rung (the rings and the kit add 544 together over the old casing-sized recesses) |
| `LOD2` | 684 | 1,500 | openings flush; coplanar boolean splits dissolved; bin 8, spout and flue 4, collar 6; downpipes 4-sided, straight; the kit with every fourth rung, no brackets or posts (140) |
| `LOD3` | 490 | 500 | as `LOD2`, bin a 6-sided prism, collar 4; downpipes 3-sided, straight; no kit |

What the bin and the spout cost together (bin wall, cone, collar and spout),
the flue, and the three downpipes (each pipe's faces and its hole in the
soffit, `DP.MODES`):

| Tier | Bin, cone, collar, spout | Flue | Downpipes |
| --- | --- | --- | --- |
| `LOD0` | 376 | 66 | 248 |
| `LOD1` | 304 | 52 | 130 |
| `LOD2` | 204 | 34 | 58 |
| `LOD3` | 162 | 36 | 46 |

The east pipe is 82 / 42 / 18 / 12 of those. No tier drops the downpipes:
every tier keeps all three at the module's default `DP.MODES`, and `LOD3`
stays under its ceiling with them (490 of 500). That leaves `LOD3` 10
triangles of headroom, which the roof safety kit does not touch: `LOD3`
drops it, as `roof_safety.MODES` does, and the kit stands inside the
bounds, so no bare rails need to stay for the extents. Anything added to
`LOD3` later goes past the ceiling; the first saving would be the east pipe,
a one-pixel line there.

The building itself is about 500 triangles at `LOD0` and about 250 at `LOD3`,
before the downpipes and the kit. The kit is most of the rise over the
farm's other buildings: the unioned roof ladder's rungs and brackets cut
the rails and the slab, and the walkway's posts the slab.

**These counts are far under the ceilings, and that is correct, not something
to pad.** The building is two boxes with two roofs and eight openings. The
walls are polygons with holes, not grids. Everything this style would
otherwise model (battens, drip boards, casings, braces, corrugation) is
texture.

`LOD3` stays close to `LOD2` for two reasons. The bin's ring cuts are UV
seams the tiling band needs, so they stay. The tower's corner columns are
split at the joints for the same reason.

## LOD review

### The consumer's switches

The consumer switches by screen size: adjacent tiers are judged at 1.8, 4 and
8 times the largest bounds dimension (12.19 m, the height), so **22, 49 and
98 m**, with its camera, 75° vertical FOV at 1920×1080, distance from the
camera to the centre of `LOD0`'s bounds. Rendered on reimported GLBs (Cycles
24 samples, AgX, the `review_asset.py` scene with the lens swapped): front,
corner (45° round, 25° up), eye level and rear at noon, the corner at night
with the reference emission on; each pair side by side with its difference,
before and after the 2026-11-22 fixes with identical settings
(`review/older_audit_2026_11_22/fix_agricultural/viljakuivuri_tower/sheets/`,
local, git-ignored).

- **22 m, `LOD0`/`LOD1`:** `LOD1` used to cut one casing-sized recess per
  opening, so every white casing lost its top and one side to the recess's
  shadow at this switch. `LOD1` now keeps `LOD0`'s casing ring on the wall
  and recesses only the opening: the two tiers differ only in the round
  parts' sides and the kit's rungs (mean difference over the front 1.64 →
  0.19 / 255, eye level 1.61 → 0.21, night 0.28 → 0.03). Nothing pops.
- **49 m, `LOD1`/`LOD2`:** the openings go flush. The casings no longer jump
  back to full width (they are full width on both tiers); what changes is
  the recess's shadow inside the casing, the head shadow over each pane and
  the leaf's depth, CLAUDE.md's flat openings from `LOD2` (mean 1.85 → 1.42
  front, 2.10 → 1.50 eye). The kit's rungs thin to every fourth. Left as is.
- **98 m, `LOD2`/`LOD3`:** the bin's and collar's sides, the downpipes'
  third side, and the roof safety kit, which `LOD3` drops: the walkway
  plank, a one-pixel light line on the lean-to's roof at this distance, and
  the ladders' rails, under half a pixel (mean 0.29 → 0.36 at the corner).
  `LOD3` has 10 triangles of headroom, too few for the 12-triangle plank, so
  that line goes; recorded rather than hidden.
- At night the lit panes match across every pair.

### Authoring review

**Intended switches: 35 / 70 / 120 m**, the catalog defaults; no overrides.
Distances were reviewed with `scripts/review_asset.py` on the exported tiers:

- perspective, 1920×1080, 50° vertical FOV, Cycles, AgX, exposure 0, noon
  sun;
- views: oblique (40° azimuth, 30° elevation) and rear (150°, 30°);
- all four tiers at 35, 70 and 120 m, compared side by side at native pixel
  size.

Renders are in `review/farm_2026_11_20/viljakuivuri_tower/lod/`.

- **Silhouette.** At 70 m and 120 m the read is a tall narrow red tower with a
  white-trimmed gable, a low lean-to, a pale cylinder with a bright cone, and
  the diagonal spout between them. That is a grain farm's dryer, and it holds
  on every tier. At 120 m the spout is a two-pixel line and still reads.
- **Openings.** `LOD1` builds the openings as `LOD0` does. At the
  70 m switch the move from recessed to flush openings changes only the
  shadow inside the reveals. Every window, both doors and the louvre keep
  their place, size and contrast on every tier.
- **Bin.** The 16- to 12-sided switch at 35 m is not visible. At 70 m, 8
  sides read round. At 120 m, 6 sides read as a cylinder, and its highlight
  facets differ from `LOD2`'s only when the two are blinked side by side.
- **Corner boards** survive every tier as UV columns, and the drip joints'
  lines stay at the same heights.
- **Gutters, downpipes and snow guards.** Reviewed before and after with
  identical `review_asset.py` runs (`LOD0`/`LOD1` at 20 and 40 m, oblique,
  front, rear and left (west); `LOD2`/`LOD3` at 70 and 120 m, oblique; noon
  and reverse suns), compared with `review_compare.py` in
  `review/farm_gutters_2026_11_20/viljakuivuri_tower/compare/`. At 20 m the
  gutter reads as a raised grey roll along the top of each eave fascia, with
  its shadow on the board below and its hangers; the tower's west pipe reads
  down the whole wall with its swan-neck and shoe, and the lean-to's beside
  its front corner board. At 40 m both pipes are still a clear line. The
  snow guard reads as a double rail near each eave, strongest under the
  reverse sun. Nothing else changed: bounds (9.70 × 8.80 × 12.19 m) and pivot
  are as before on every tier. Every tier keeps every pipe (`DP.MODES`:
  8-sided bent, 4-sided bent, 4-sided straight, 3-sided straight); past
  70 m the swan-neck and shoe go, which is under two pixels.
- **The tower's east downpipe.** Reviewed before and after with identical
  `review_asset.py` runs (`LOD0`/`LOD1` at 20 and 40 m, oblique, right (east)
  and front; `LOD2`/`LOD3` at 70 and 120 m, oblique and right; noon), in
  `review/mine_fixes_2026_11_20/viljakuivuri_tower/compare/`. At 20 m the
  pipe reads down the tower's east wall from its swan-neck under the eave to
  the lean-to's roof, where the shoe kicks out down the slope in the tower's
  shadow; from the east it is a thin grey line beside the flue, ending on the
  sheet. At 70 m (`LOD3`) it is still a one-pixel line in the oblique. Nothing
  else in the frames changed; bounds and pivot are as before.

The six working views at `LOD0` and `LOD3` (orthographic front, rear, sides,
top, and the raised three-quarter aerial) are in `views/`. Close views at 10 m
under the morning and noon suns are in `close/`.

**Filtering.** `scripts/review_atlas_mips.py` wrote whole-atlas mip4 maps
(16 × 16 texel averages, albedo in linear light). `LOD2` and `LOD3` were
rendered at 120 m, oblique and grazing (75°), base against mip4 (`mip_base/`,
`mip_mip4/`). At mip4:

- the corner boards, casings, glass and roof keep their contrast;
- the doors' white braces blend into a lighter pink-red leaf;
- the bin stays neutral grey, and no colour leaks onto the roof or walls.

This is a stress test, not the consumer's sampler.

## Interior geometry

Measured with `scripts/validate_asset.py` on the exports:

| Tier | Hidden triangles | Share | Vertical area |
| --- | --- | --- | --- |
| `LOD0` | 67 of 1,836 | 3.6 % | 0.4 m² |
| `LOD1` | 36 of 1,460 | 2.5 % | 0.5 m² |
| `LOD2` | 11 of 684 | 1.6 % | 0.6 m² |
| `LOD3` | 4 of 490 | 0.8 % | 0.9 m² |

The candidates are exterior surface the 40 sampled rays rarely escape:

- the lean wall ladder's closure faces, where the largest candidates now
  sit and which account for the rise since the kit was added (+57 at
  `LOD0`, +28 at `LOD1`, +5 at `LOD2`, not traced face by face): the end caps of its
  rungs and brackets, which face a rail or the wall across the lean kit's
  1.5 mm gap by design (`roof_safety.LEAN_GAP`), so no ray leaves them. They
  are kept: each is the closing face of a separate solid;

- the flue's soot lining and floor, which see the sky up a 0.24 m mouth;
- slivers where the tower's eave-wall tops meet the soffits;
- the lean-to's rear-east wall top under its rake soffit;
- the tower's east downpipe's flat that faces the wall across its 0.03 m
  gap, all of the vertical area: the soffit above it and the lean-to's roof
  below it close off the rays that escape the west pipe's gap downward. It
  is exterior surface, seen edge-on from the side, and its area is one flat
  of the pipe (wider at three sides on `LOD3`).

No wall stands inside the building, by construction. The coincident double
wall of the first build (Construction) is gone; the welded export is manifold
on every tier.

## Known simplifications

- **No dryer machinery outside**: no elevator head on the roof, no
  distributor, no fan housing. The only ladders are the roof safety kit's. One spout stands for the grain
  handling, one louvre for the exhaust, one flue for the furnace.
- **The bin has no ladder, roof hatch, aeration fan or unloading auger**, and
  stands on no slab. Its corrugation, ring and sheet seams and bolts are
  height and texture on a plain prism. The fill collar is a plain lidded
  cylinder.
- **The flue has no rain cap, guy wires or roof collar**, and the spout no
  supports or flexible end.
- **Board-and-batten, drip boards, casings, door frames and braces, drip
  caps and the profiled roof's ribs are texture**; none clears the 0.25 m
  relief threshold.
- **The tower's ridge has no ridge cap.** Only the lean-to's roof region
  carries a flashing along its top, where it meets the tower wall.
- **The roof safety kit's walkway goes at `LOD3`**, with the rest of the
  kit (LOD review).
- **The gutters are texture**: a painted half-round with its roll in the
  height channel on the eave fascias, with no modelled outlet or end caps.
  The downpipes are modelled (Construction).
- **The tower's east downpipe ends on the lean-to's roof**, with its shoe
  (or open end) just above the sheet; there is no spreader or roof-mounted
  outlet, and the water's way down the slope to the lean-to's gutter is not
  shown (Construction, Gutters and downpipes).
- **The snow guards are texture**: tubes and brackets painted in the roof
  regions, with relief in the height channel.
- **Thresholds are a 0.10 m step**, with no ramp up to the tipping-pit door.
- **Reveals are 0.15 m deep** (0.12 m at the louvre), a timber wall's, as in
  the rintamamiestalo houses.
- **One window type**, so every window is the same pane (Glazing treatment).

## Texture set

| File | Space | Notes |
| --- | --- | --- |
| `_albedo_<variant>.png` ×3 | sRGB | 1024², 8-bit RGB, no alpha |
| `_orm.png` | Non-Color | 1024², R = AO, G = roughness, B = metallic |
| `_normal.png` | Non-Color | 1024², OpenGL tangent space (+Y green up) |
| `_emission.png` | sRGB | 1024², neutral glazing mask |

That is six unique 1024² textures: three albedos, plus one ORM, one normal map
and one emission mask shared by every tier and colour.

**Atlas layout** (`facade_atlas.py`):

| Rows | Band | Contents |
| --- | --- | --- |
| 0–312 | S1 | plinth, flashing, boards, the 4.80 m drip |
| 312–576 | W2 | boards repeating every 256 rows, drip at each repeat's foot, gutters carrying the opposite ends |
| 578–650 | BIN | one 1.00 m ring of corrugated wall, repeating every 64 rows, likewise |
| 652–672 | FASCIA | white fascia board, a half-round galvanised gutter across its top 8 rows (661–669), hangers every 64 px; `PIPE_STRIP` = its middle five rows, 662.5–667.5 |
| 780 up | unique | the four opening regions, the bin roof disc, the corner strip, nine flat patches |
| 676–817, x 760–1004 | ROOF_T | the tower's slope, 5.80 × 3.35 m at 42 px/m both ways (both slopes share it): profiled sheet, the galvanised snow guard 0.5 m up from the eave |
| 822–1009, x 760–958 | ROOF_L | the lean-to's slope, 4.70 × 4.45 m at 42 px/m: the same sheet and snow guard, and the flashing against the tower wall along its top 0.25 m |

`check_bands()` fails the bake on a stray id in any band. `atlas.pad()` fills
the rest, the old roof band's rows (674–776, x 0–758) included, which no
face samples.

**Bands that tile in V.** W2 and BIN carry their opposite ends into their
gutters. Every noise over them repeats on their own period: `noise()` in
`facade_atlas.py` uses `tile_y=4` everywhere except the BIN rows, which use
`tile_y=16`. The Weather object runs at `tile_y=4`. The bin's weathering is
written from its own 64-row noise, and the canvas-wide grime skips the BIN
rows. Height-following weather goes on S1 only.

**Texel density** is 64 px/m, with these deliberate exceptions:

- the bin's wall runs once round in 1024 px (109 px/m along U), since nothing
  in it varies round the bin except the four sheet seams;
- the two roof regions are 42 px/m both ways (isotropic). Until 2026-11-22
  the roofs sampled one full-width band at 64 px/m along the eave and 21.6
  up the slope (anisotropy 2.97), which smeared the painted snow guard; at
  64 px/m the lean-to's slope alone would need 285 rows, so each roof is now
  a region of its own, and 42 is the most at which both fit, stacked, in the
  atlas's free right-hand columns;
- the bin roof disc is 38 px/m in plan;
- the corner strip is stretched along its length.

**Relief heights** in the height channel, from which `atlas.normal_map()`
derives the normal map:

| Feature | Height |
| --- | --- |
| Battens | 18 mm |
| Drip boards' lips | 30 mm |
| Casings | 20 mm |
| Sills | 35 mm |
| Sashes | 12 mm |
| Door braces and frames | 20–22 mm |
| Roof ribs | 20 mm |
| Bin corrugation | 13 mm |
| Bin sheet laps | 3 mm |
| Bin bolts | 6 mm |
| Bin roof ribs | 16 mm |
| Gutter, half-round | 62.5 mm (its radius) |
| Gutter hangers | +4 mm |
| Snow guard tubes | 35 mm (50 and 35 mm across) |
| Snow guard brackets | 30 mm |

Every height in the roof regions (ribs, snow guard, flashing) is scaled by
their 42 px/m over 64, so the slopes `atlas.normal_map()` derives stay
physical.

The battens read raised in a 10 m render under the low morning sun: a lit
edge toward the sun, a shadow away from it.

**Rasterised by `scripts/atlas.py`** at the catalog's 4 × 4 samples per pixel.
Glass keeps a flat normal.

**Roughness / metallic:**

| Surface | Roughness | Metallic |
| --- | --- | --- |
| Boards | 0.78 | 0 |
| Trim | 0.60 | 0 |
| Glass | 0.08 | 0 |
| Concrete | 0.90 | 0 |
| Roof (coil-coated, painted steel) | 0.50 | 0 |
| Flashings, drip caps (painted, the roof's colour) | 0.46 | 0 |
| Galvanised steel | 0.40 | 0.85 |
| Gutters, downpipes and snow guards (`ID_GUTTER`, older zinc, sRGB 134/137/137) | 0.48 | 0.60 |
| Flue | 0.62 | 0.30 |

Dirt dulls all of them.

**Gutter steel.** `ID_GUTTER` is the farm buildings' one galvanised
rainwater steel, the same id colour and surface on `navetta_board_gable` and
`konehalli_open_bays`, fixed in every variant. Measured over `PIPE_STRIP`
after weathering: mean sRGB 128/131/131 in all three albedos, roughness 0.53,
metallic 0.52 (ORM). The bin's `ID_GALV` (164/167/168, 0.40/0.85) and the
flue are separate ids and unchanged.

**Weathering** is `scripts/weathering.py` at its moderate level:

- on S1: soil and algae at the plinth, splash on the boards' foot;
- dirt on the drip boards and short runs under them;
- on each roof region, runs and chalking up its own slope, and dirt between
  the ribs;
- runs down the fascia board under the gutter; a dirty gutter belly and
  light runs down its face from the lip, the same treatment as the farm's
  other two gutters;
- light dust on the snow guard and rust at its brackets; debris held above
  it, rust on the sheet round the brackets and short runs under them;
- sills, door feet and handles; dust blown out over the louvre;
- on the bin: dust and white bloom on the zinc, runs under each ring's lap;
- dust toward the bin roof's eave, and rust specks;
- rust on the flue.

## Glazing treatment

Panes are painted by `scripts/glazing.py`'s `rooms()` after the
id/shade/AO pass.

| | |
| --- | --- |
| base colour passed to `rooms()` | sRGB 62/68/71 (`glazing.BASE` × 1.25) |
| measured over the glass mask | mean sRGB 54, linear 0.033 |
| relative to the trim around it | 0.25× (red), 0.24× (yellow), 0.33× (grey) |
| roughness / metallic | 0.08 / 0 |
| panes in the atlas | 1 |

**The base is raised, and the measured glass is inside the Style Direction
band.** The atlas has one window region, so `rooms()` sees one pane and draws
its room level once. At `glazing.BASE` that draw came out at 0.82 of the mean,
and the glass measured sRGB 44, under the 45–70 band. Raising the base by the
inverse puts the one pane mid-band. The room treatment itself (falloff, lit
far wall, grain) is `rooms()`' own. Every window on the building is the same
pane.

## Variant list

Three variants, `export/viljakuivuri_tower_albedo_<name>.png`, sharing one
ORM, normal map and emission mask:

| Variant | Boards | Trim | Roof | Doors |
| --- | --- | --- | --- | --- |
| `red_ochre` (default) | punamulta red ochre, sRGB 122/52/42 | off-white 221/217/205 | dark grey steel 54/56/58 | boards a shade darker than the walls (112/48/39), white frames and braces |
| `grey_weathered` | unpainted boards gone silver, 110/106/98 | weathered light grey, lighter than the boards but no white, 150/146/137 | dark grey steel 62/62/60 | silvered boards 101/98/90, grey frames and braces |
| `yellow_ochre` | yellow ochre, 184/148/86 | off-white 222/218/206 | dark red-brown steel 75/51/45 | boards 169/136/79, white frames and braces |

The farmstead's three buildings (this dryer, `navetta_board_gable` and
`konehalli_open_bays`) stand together, so they share these variant names and
these exact numbers: one name dresses the set.

The bin, spout, collar, flue, plinth, glass and the galvanised gutters,
downpipes, snow guards and roof safety kit never change. This is
CLAUDE.md's low-rise case, paint on shared geometry. Every `.glb`
references the default albedo; another variant is that one file swapped.

## Night lighting

`viljakuivuri_tower_emission.png` masks the glass of the one window region,
painted as a lit room by `glazing.night_rooms()`. Doors, louvre, walls, roofs
and the bin are black.

**Bindings.** All four GLBs bind it through `emissiveTexture` on UV0, with
`emissiveFactor` `[0, 0, 0]` by default (`scripts/window_emission.py`). The
reference lit factor is linear RGB `[1.0, 0.88, 0.72]`
(`facade_atlas.LIT_FACTOR`, passed to `asset_build.Asset`), the warm white of
the catalog's newer buildings; it tints `variants.png` and `source.blend`
only, as the exports ship the factor at zero.

**Control.** All windows share one region, so there is one building-wide
control; per-window switching is not possible. Occupancy, schedule, colour
and intensity are the consumer's.

**Preview.** `variants.png` (1920×1508): every colour at `LOD0`, a day row
with the emission off above a night row at the reference factor. Camera,
framing and exposure are fixed between the rows (`scripts/variant_previews.py`,
Cycles, AgX, exposure 0). Cycles simulates the spill onto the casings; the
game's spill is its own lighting's.

No sign or lamp emits. Pending in the consumer: night exposure, spill, and
off/on behaviour across LOD switches.

## Export

```
python3 facade_atlas.py export                       # textures, all three variants
blender --background source.blend --python build.py   # tiers, preview, variants, sidecar
```

The first build ran without `source.blend`
(`blender --background --python build.py`), which creates it.

Export settings, from `scripts/asset_build.py`'s `export_all()`:

- `export_format='GLB'`, `use_selection=True`, `export_yup=True`,
  `export_apply=True`;
- `export_keep_originals=True`, `export_cameras=False`,
  `export_lights=False`;
- one material, backface culling on (single-sided);
- `strip_embedded_images()` leaves the image `uri`s only;
- the emission factor is rewritten to zero.

**Bindings, traced per tier.** Each tier binds:

- `baseColorTexture` to the `red_ochre` albedo;
- `metallicRoughnessTexture` and `occlusionTexture` to the ORM;
- `normalTexture` at scale 1;
- `emissiveTexture` to the mask.

All are external PNGs on UV0. The validator confirms the normal and emission
bindings and the uri-only images on every tier.

`export/viljakuivuri_tower.model.json` is the facts sidecar, in the glTF frame:

| Fact | Value |
| --- | --- |
| hero | false |
| dwellings | 0 |
| footprint | the eight-corner tower and lean-to outline, the bin left out |
| storeys | one: floor 0.10 m, 41.38 m² |
| `front` door | entrance, main; at [−3.15, 0.10, 4.00], facing +Z, 0.90 × 2.10 m |
| `intake` door | vehicle; at [2.60, 0.10, 3.60], facing +Z, 3.00 × 3.20 m |

## Review status

Checked here, in Blender 5.3.0, headless:

- `scripts/validate_asset.py` reports no failures, and no warnings once the
  sidecar is written from a committed tree; after a rebuild from a working
  tree it warns `source.dirty` until `build.py -- facts` is rerun from the
  commit. It also confirms:
  - welded manifold topology on every tier;
  - one material, uri-only images, the normal map at scale 1, emission bound
    and default off;
  - the pivot at ground and centred;
  - the counts against the ceilings;
  - six 1024² RGB PNGs;
  - the glass inside the band;
  - the sidecar's schema, hashes, footprint and doors.
- `check_layout()` passes; the build is manifold before export on every tier.
- The six working views at `LOD0` and `LOD3`.
- The tier comparisons at 35, 70 and 120 m, and the mip4 stress renders at
  120 m (LOD review).
- Close renders at 10 m, morning and noon: battens and drip boards read
  raised.
- The glass measured against the band and its casing.
- The day/night sheet across all three colours.
- Gutters, downpipes and snow guards: before/after sheets at 20–120 m
  (LOD review); `preview.png` and `variants.png` regenerated and checked.
- The shared galvanised steel pass of 2026-11-20: a texture-only change.
  Triangle counts (1,110 / 874 / 526 / 478) and bounds match the sidecar;
  the normal map and emission mask are byte-identical. `PIPE_STRIP`
  measured as above (Texture set), within two sRGB levels of the other two
  farm buildings. Before/after renders at 20 m (`LOD0`, oblique and rear,
  noon) in `review/farm_gutter_colour_2026_11_20/` (local, git-ignored),
  compared side by side with the other two, and `variants.png` looked at.

- The tower's east downpipe: `check_layout()` passes with it; the validator
  reports no failures on the rebuilt tiers (1,192 / 916 / 544 / 490, bounds
  9.70 × 8.80 × 12.19 m and pivot unchanged, sidecar doors unchanged);
  before/after sheets at 20–120 m and an enlarged crop of its foot looked at
  (LOD review); `preview.png` and `variants.png` regenerated and checked.
- The mip4 stress renders re-run at 120 m (`LOD2`/`LOD3`, oblique and
  grazing, `review/farm_gutters_2026_11_20/viljakuivuri_tower/mip4/`): the
  eave fascias average to a light grey line, gutter and board together, the
  roof edge stays dark, and no colour leaks between the fascia and roof
  bands.
- The 2026-11-22 audit fixes: `check_layout()` passes with the roof safety
  kit (`RS.append(check=True)` found no clash); 0 FAIL on the rebuilt tiers
  (1,836 / 1,460 / 684 / 490), bounds 9.70 × 8.80 × 12.19 m, pivot,
  footprint, storeys and doors unchanged in the sidecar. Tier pairs at the
  consumer's 22 / 49 / 98 m, `LOD0` front and oblique at 20 and 35 m and
  each variant at 35 m, before and after with identical settings; the
  audit's close views re-rendered (the roof and flue, the openings); the
  three farm buildings' default and grey variants side by side.

Pending, in the consumer:

- import and material control;
- LOD switching;
- mip, anisotropic and padding behaviour of its sampler;
- MikkTSpace tangents;
- night exposure and spill;
- runtime performance.

## Tooling versions

- **Blender 5.3.0** (build 2026-11-11), headless, which saved `source.blend`.
  No MCP addon was used.
- **CPython 3.14.10, numpy 2.5.5, scipy 1.18.1, Pillow 13.0.0** for the
  texture export.

Recorded as known-good markers, not requirements.

## Revision log

- **2026-11-22:** audit fixes. A roof safety kit to the furnace flue (a lean
  wall ladder on the lean-to's rear wall, a roof ladder and a walkway;
  inside the old bounds). `LOD1` keeps `LOD0`'s casing rings instead of
  casing-sized recesses, which popped at the 22 m switch. The roofs repacked
  from a 64 × 21.6 px/m band into two isotropic 42 px/m regions. One palette
  for the farmstead (all three variants identical on the three farm
  buildings; red, yellow and the grey trim moved). Roof steel and flashings
  dielectric (0.50 / 0, 0.46 / 0; were 0.46 / 0.25, 0.42 / 0.30). Night tint
  (1.0, 0.88, 0.72). The consumer's switch distances recorded. Triangles
  1,192 / 916 / 544 / 490 → 1,836 / 1,460 / 684 / 490.
- **2026-11-20:** a downpipe for the tower's east eave gutter, down the
  tower's wall above the lean-to and spilling onto the lean-to's roof
  (`RoofPipe` in `build.py`, lifting `scripts/downpipes.py`'s foot onto the
  slope). Triangles 1,110 / 874 / 526 / 478 → 1,192 / 916 / 544 / 490;
  bounds, pivot, textures and the sidecar's doors unchanged.
- **2026-11-20:** the gutters, downpipes and snow guards share one
  galvanised steel with the farm's other two buildings: `ID_GUTTER` goes
  from sRGB 146/149/150, 0.48/0.70 to 134/137/137, roughness 0.48, metallic
  0.60, and the snow guard moves from the roof sheet's id onto it. Gutter
  weathering is the shared treatment (dirty belly over four rows, light runs
  on its face) and the snow guard gets light dust and rust at its brackets.
  Texture-only: geometry, UVs, relief heights, layout, the normal map and
  the emission mask are unchanged; the bin's galvanised id and the flue are
  untouched.
- **2026-11-20:** gutters, downpipes and snow guards. A painted half-round
  galvanised gutter on the three eave fascias (`PIPE_STRIP` named in
  `facade_atlas.py`, new `ID_GUTTER`); two modelled downpipes
  (`scripts/downpipes.py`), down the tower's west wall and the lean-to's east
  wall, both at the front end of their eave; the tower's east gutter has no
  pipe, which the module cannot place there. A painted snow guard 0.5 m up
  every roof slope. Triangles 944 / 786 / 486 / 444 → 1,110 / 874 / 526 /
  478; bounds and pivot unchanged.
