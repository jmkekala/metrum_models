# rintamamiestalo_gable_entry

## Style brief

A composite Finnish *rintamamiestalo*, the standardised one-and-a-half-storey
timber house built in huge numbers after 1945. The type is a near-square block
under a steep 45° gable roof, the attic storey lit by one wide window in each
gable end, a tall concrete plinth over a cellar, a chimney on the ridge, and
horizontal lap siding with contrasting corner boards and window casings.

This is the gable-entry sibling of `rintamamiestalo_porch`,
`rintamamiestalo_side_entry` and `rintamamiestalo_balcony`. It has the same
block, roof and window types, but it stands with a gable end to the street and
its entrance in that gable:

- **The block is turned.** The ridge runs back from the street, so the street
  sees the 8 m gable, not the 10 m eave wall.
- **The front door is in the middle of the front gable**, between two wide
  windows, the living room's and the kitchen's, mirrored about it: Style
  Direction's entrance-gable allowance, one window each side of a centred
  front door in place of the gable's one per storey.
- **A terrace runs the house's full width** in front of the door, 2.40 m deep
  and flush with both long walls. It has:
  - a timber deck, 5 cm under the door's threshold, on a concrete base;
  - a railing of white balusters round its three open sides;
  - steps off its front edge, centred on the door, through a gap in the
    railing, so the way in runs straight from the street. A first version had
    them off to the east side; they were moved to the door's centre line.
- **A balcony over the front door**, 3.20 × 1.20 m, cantilevered off the gable
  at the attic floor, with the same railing. It is the front door's canopy, and
  a pair of glazed doors opens onto it from the attic storey.
- **The back door is in the far gable**, under its canopy, with its steps.

On both gables the white belt board sits at the attic floor, 3.85 m, instead
of the siblings' 4.30 m, because the balcony doors run from 3.90 m up through
where the belt would be. At 3.85 m it is level with the balcony deck, and
exactly level with the eave fascia's lower edge. From the front, the fascia's
line carries on across the gable as the belt, and the corner boards run the
full height with the belt between them.

Materials follow the type:

- painted lap siding and painted trim;
- a standing-seam steel roof with snow guards;
- a board-formed concrete plinth and terrace base;
- a red-brick chimney with a metal-capped rim round an open flue;
- weathered grey-brown timber decking on the terrace and the balcony;
- railings in the trim colour;
- plain-glass windows: every window, and each balcony door leaf, is one clear
  pane inside a thin frame, with no crossbars and no mullions. Don't add
  divisions on a rebuild.

The roof carries the safety kit Finnish rules ask of it, in the gutter's steel:
a ladder up the west wall's rear half, a roof ladder up the west slope and a
walkway along it to the chimney.

It is meant to be placed as street filler in a residential district, many
times over, beside its three siblings. Colour variety comes from the variants.
Variety along a street comes from mixing the four houses, this one being the
narrow-fronted one, 8 m to the street where the others are 10 m.

## Category and secondary use

`buildings/residential/`. No secondary use.

## Hero/landmark status

**No.** Ordinary budgets, a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Main block, walls | 8.00 × 10.00 m |
| With the terrace (2.40 m forward, full width) | 8.00 × 12.40 m |
| Ground contact, including both flights of steps | 8.00 × 14.98 m |
| With the 0.45 m eave overhangs | 8.90 × 14.98 m |
| Overall, including the wall ladder 0.63 m off the west wall | 9.08 × 14.98 m |

Main block heights:

- The wall meets the soffit at 4.30 m.
- The fascia bottom and the gables' belt are both at 3.85 m.
- The ridge is at 8.61 m and the chimney top at 9.56 m.

Terrace and balcony heights:

- The terrace deck is at 0.65 m and its railing top at 1.55 m.
- The balcony slab's underside is at 3.65 m, 3.00 m clear over the terrace.
- The balcony deck is at 3.85 m and its railing top at 4.85 m.

The pivot is centred on the plan's bounding box, overhangs and steps included.
That is the footprint `scripts/validate_asset.py` checks, and it puts the pivot
0.75 m in front of the main block's centre and 0.09 m west of it, because the
wall ladder stands 0.18 m outside the west eave.

The pivot is taken from `LOD0` and applied to every tier. Every tier keeps the
same extents (at `LOD3` both flights of steps become ramps with the same
footprint), so a LOD switch never moves the house. `build_all()` asserts this.

## Story height

**Ground floor 3.20 m.** The floor is at 0.70 m on the plinth and the attic
floor at 3.90 m, inside the 3.0–3.3 m standard. The attic storey sits under the
roof, with a 0.40 m knee wall up to the eave at 4.30 m.

## Door leaf height

**2.10 m** for every door, with no transom or fanlight. The casing adds 0.19 m
above each leaf.

- **Front door:** the threshold is at the 0.70 m floor, 5 cm above the terrace
  deck.
- **Back door:** the threshold is at the same floor level, reached by a landing
  and three risers.
- **Balcony doors:** a pair of 0.70 m leaves, 1.40 m together, with the
  threshold at the 3.90 m attic floor, 5 cm above the balcony deck. Each leaf is
  one clear pane over a solid bottom panel.

## Window sills

**1.50 m above ground**, which is 0.80 m above the floor. That is a little
above the ~1.4 m guide, and the reason is the type itself: the cellar plinth
lifts the whole ground floor 0.70 m, as it does on the real houses. The
terrace and the back steps make that lift legible beside the doors.

Seen square-on, the terrace railing hides the lowest 0.18 m of the two front
windows' casings, as a railing in front of a window would.

The rear gable's window has its sill at 4.65 m, 0.75 m above the attic floor.
The front gable has no attic window: beside the balcony doors, under the rake,
there is no room for one with a sensible margin to the soffit. The doors light
the front rooms instead.

## Eave overhang

| Where | Projection |
| --- | --- |
| Eaves (the long side walls) | **0.45 m**, the catalog default |
| Rakes (the gables) | 0.35 m |
| Balcony | 1.20 m, a balcony rather than an overhang |
| Back-door canopy | 0.80 m, a covered entrance rather than an overhang |

The eaves and rakes are within 0.3–0.6 m. The balcony is inside CLAUDE.md's
1.0–1.8 m balcony range, and the canopy is ruled as a covered entrance, the
same case as a portico at a smaller scale. Soffits slope with the rafters
(the underside of the roof slab). All of these are kept at every tier except
the canopy, which goes at `LOD3`.

## Construction

`build.py` unions closed solids with Blender's Exact boolean:

- the house, one solid;
- the roof, one gable slab along Y;
- the chimney;
- the terrace base;
- the balcony slab;
- seven railing boards, four on the terrace and three on the balcony;
- the back canopy and two flights of steps.

**The house is the siblings' block authored in place with its ridge along Y**,
not built along X and rotated. The wall builder, gable slab, steps and chimney
already take any orientation, and the back canopy's rear wall is at y = +5,
where the rear gable now is.

**Each railing is a box**, split into two bands up its sides:

- the baluster zone, mapped to the `RAIL` strip with U in world metres, so the
  balusters on a board's two faces line up;
- the top 0.10 m, the handrail, in the trim patch.

The top face is the cap. The 0.10 m end faces are trim too, and they read as
posts at the step gap. The side boards start behind the front ones, so no two
boards overlap. The union merges away every face a board shares with a deck,
another board or the house.

**The house solid carries the belt height as a breakpoint on every wall end.**
The gables change band at 3.85 m, so the long walls' ends need a vertex there
too, or the corners would meet on different vertices.

Removed from the balcony sibling's script because nothing here uses them:

- the dormer and porch solids;
- the gable slab's cut end;
- the corner boards' `board_to` stop. On this house the boards run the full
  height and the belt runs between them.

**The chimney is open at the top.** Its steel-capped rim is a 0.12 m half-brick
shell round one 0.36 × 0.60 m flue, sunk 0.80 m and lined and floored with the
atlas's soot patch, on every tier (see LOD review). The top stands 0.95 m over
the ridge, so the flue's floor stays clear of the roof slab and the union
leaves the shaft empty.

`check_layout()` asserts, before building:

- openings overlapping each other or a corner board, running under a roof
  line, or straddling a band change or the plinth top;
- the gable outgrowing its atlas band, or the roof slope disagreeing with the
  atlas;
- the belt off the fascia's lower edge;
- anything standing against the front gable (the terrace, its side boards,
  the balcony slab and its side boards) across an opening's casing;
- the balcony not covering the front door, sitting on its casing, or under
  head height over the terrace;
- the balcony doors not well inside its railings;
- the terrace deck not under the threshold, the steps off the door's centre
  line or narrower than its casing, the step gap crowding a corner, or unequal
  risers;
- the back canopy missing its door, sitting on it, below head height, or
  running into the gable's belt;
- the chimney flue's floor reaching into the roof slab;
- a downpipe within 0.25 m of a corner, with less than 0.2 m of wall
  between it and an opening, or standing in the terrace;
- the wall ladder within 0.3 m of a corner or with less than 0.2 m of wall
  between it and an opening or the downpipe, or with a bracket in the soffit;
  the walkway not running the stack's length, or its edge not just beside the
  stack;
- a handrail within 0.1 m of its door's jamb, a bottom post off its
  tread, or a flight too short for a sloping rail;
- the terrace handrail not meeting the railing's top.

### Downpipes

Two downpipes from the shared `scripts/downpipes.py`, unioned in with the other
solids: one from each eave's gutter, on the side walls, at diagonally opposite
corners: the east eave's 0.25 m in from the street corner, where it stands just
behind the end of the terrace's railing, and the west eave's 0.25 m in from the
back corner.

Each is a 0.1 m pipe standing 3 cm off the siding, as it would on its
clips, and joined to nothing but the soffit it leaves, so it cuts no line
through the wall's triangles. It rises into the soffit 0.36 m out from the
wall, just inside the fascia the gutter is painted on, falls 0.25 m, steps
back to the wall at 45 degrees, and ends in a shoe kicked 0.15 m out, its
mouth about 0.2 m above the ground. Its sides sample the middle five rows of
the fascia band's gutter (`PIPE_STRIP` in `facade_atlas.py`), so the pipe
takes the gutter's steel in every colour, and the gutter's hangers, a metre
apart, read as its clips. No atlas region was added and no pixel changed.
The tiers are eight sides with both bends at `LOD0`, four at `LOD1` and
straight at `LOD2`; `LOD3` drops them (the family module's
`DOWNPIPE_MODES_HOUSE`; Per-tier triangle counts), where the module's other
houses keep them three-sided.

On this house the union leaves the soffit round both pipes' holes at `LOD2` as
a keyhole: one face running out to the hole and back along a bridge
of coincident vertices, which the weld would split into two overlapping faces.
`scripts/asset_build.py`'s `union()` triangulates any such face before the
weld, so the soffit there is triangles.

### Roof safety kit

From the shared `scripts/roof_safety.py`, as CLAUDE.md asks of a roof steeper
than 1:8 carrying something serviced from it: the chimney, which the sweep has
to reach. The gables take the front door and the back door, and a ladder has to
pass an eave, so the kit stands on the west eave wall's rear half: at the back,
away from the entrance, and the side away from the catalog view. The wall
ladder stands outside the eave, the house's widest point on that side, so
`LOD3` keeps its bare rails, three-sided, and every tier keeps `LOD0`'s extents
and pivot; they touch nothing, so they join the tier after its weld and
dissolve (`roof_safety.append()`).

- **a wall ladder up the west eave wall**, centred at y = 1.60 between its
  two standard windows, on its rear half, on brackets 0.57 m off the siding,
  passing 0.12 m outside the fascia and running 1 m above the roof edge, to
  5.16 m;
- **a roof ladder straight above it up the west slope**, from 0.25 m up from
  the eave to 0.8 m short of the ridge, its rails 8 cm off the sheet on
  brackets that run down into the slab;
- **a level walkway**, 0.30 m wide, along the west slope 0.5 m below the
  ridge, from the roof ladder forward to stand beside the stack: 1.45 m on
  posts.

Every part samples the gutter's rows (`PIPE_STRIP`), the rows the downpipes
use, so the kit takes the gutter's steel in every colour, as a matched
rainwater and safety system does, and the painted hangers, a metre apart,
read as joints. The ladders' rungs are 0.28 m apart, 3 cm square, each one's
faces meeting the holes it leaves in the rails, so each ladder is one closed
solid; the walkway's plank and posts are separate solids the union joins to
the roof. The tiers are the module's: every rung with brackets and posts at
`LOD0`, every other rung at `LOD1`, every fourth and no brackets or posts at
`LOD2`, and at `LOD3` only the wall ladder's bare rails, for the extents.

### Handrails

From the shared `scripts/handrails.py`. CLAUDE.md asks for them on every
entrance flight of three risers or more, and this house has two: the terrace
steps, falling 0.65 m in four risers from the deck, and the back steps up to
the kitchen door, climbing 0.68 m in three risers to a landing. Each flight
has one rail, on its right going up: the east side of the terrace flight and
the west side of the back one. On the back steps it runs 5 cm in from the
steps' edge, level over the landing and then down the flight, on three posts:
one on the landing by the wall, one at the head of the flight and one on the
bottom tread. The terrace flight has no landing of its own. Its rail stands on
the flight's edge and starts on the deck against the end of the east railing
board at the gap, on one post there and one on the bottom tread. It meets the
board at the board's own 0.9 m, so the railing and the handrail read as one.

- The rails and the posts are 45 mm square steel.
- The rails' tops are 0.9 m above the landing and above the line through the
  nosings.
- The posts' feet are cut into the concrete.
- The rails sample the gutter's rows (`PIPE_STRIP`), like the downpipes and
  the roof safety kit.
- There are no balusters, because a see-through infill would need alpha.
- They stand inside the steps' footprint and well under the eaves, so no
  tier's bounds change.
- They are unioned with the steps on `LOD0` and `LOD1`. `LOD2` keeps them
  lean (the family module's `RAILS`): the same rail and posts as separate
  closed solids that touch nothing, appended after the weld at 60 triangles
  a flight, so the rails' lines survive the `LOD1`/`LOD2` switch at about
  60 m. Lean, the terrace flight's rail cannot run into the railing board
  it continues, so it stands 2.6 cm further in from the flight's edge, half
  its width and two gaps, a shift far under a pixel at that switch. They go
  at `LOD3`, where a 45 mm rail is a third of a pixel.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 2572 | 12,000 | casing rings, reveals and glass on every window and door, the balcony doors included; cellar lights recessed; corner boards; stepped treads; canopy, open chimney flue; two downpipes, eight-sided with swan-neck and shoe; roof safety kit with every rung, brackets and posts; a handrail on each flight |
| `LOD1` | 2008 | 4,000 | each opening becomes one recess the size of its casing; cellar lights and vent go flush; downpipes four-sided; kit with every other rung; handrails kept |
| `LOD2` | 912 | 1,500 | openings flush, the cellar lights and gable vents among them; corner-board paint retained; redundant coplanar subdivisions dissolved; downpipes straight, no swan-neck or shoe; kit with every fourth rung, no brackets or posts; handrails lean (separate solids, 120) |
| `LOD3` | 488 | 500 | every opening still flush, the cellar lights and gable vents included; back canopy dropped, steps become ramps; corner-board paint retained; downpipes dropped; roof safety kit dropped but for the wall ladder's bare rails; handrails dropped |

The small openings kept as flush quads on the far tiers cost about 6-9
triangles each with the hole they leave in their wall: 30 at `LOD2` (three
cellar lights, two vents) and 44 at `LOD3`.

**`LOD0`–`LOD2` sit far under their ceilings. That is correct, and they
should not be padded.**

- The building is an 8 × 10 m box with one gable roof, a terrace and a balcony.
- The walls are triangulated as polygons with holes, not as a grid of cells.
- Every opening on every elevation is already cut at `LOD0`.
- Nothing else here clears the 0.25 m test.

**`LOD3` is 12 under the 500 ceiling.** The terrace, its railing and the
balcony are the house's read from the street, so they stay whole at every
tier. The seven railing boards are most of what `LOD3` spends beyond the
house itself. That left 30 triangles for the five small openings' 44, so
this house alone drops its two downpipes at `LOD3` (26 triangles; the family
module's `DOWNPIPE_MODES_HOUSE`), as `scripts/downpipes.py` allows a tier
that cannot afford them. At the `LOD2`/`LOD3` switch, about 120 m, a 0.1 m
pipe is 0.6 px beside its corner board, where a gable vent's pale louvre is a
3.7 x 2.8 px spot on the gable: dropping the vents instead was tried and
showed as a spot going at the front gable's apex. Keeping the stepped
flights instead of ramps would cost another 42.

Modelled trim (overhangs, canopy, chimney) is a few dozen triangles, far under
the quarter-budget cap.

**The roof safety kit costs 1196, 876, 240 and 16 triangles** on the four
tiers. Most of it is the rungs with the holes they leave in the rails,
and the brackets and posts with the squares they cut in the wall and the
sheet.

**The handrails cost 276, 276, 120 and 0 triangles** on the four tiers: two
rails in two runs each, the posts, and the squares the posts cut in the
landings and treads; on `LOD2` the lean rails, 60 a flight, cut nothing. At about an eighth of `LOD0` they cost more than the
downpipes and far less than the roof kit, and leave `LOD0` and `LOD1` far
under their ceilings.

**The two downpipes cost 164, 84, 40 and 0 triangles** on the four tiers, the
pipes' own faces and the holes they leave in the soffit together (26 at
`LOD3` before that tier dropped them).

## LOD review

### Consumer screen-size switches

The consumer switches by screen size, at about 1.8, 4 and 8 times the
house's largest bounds dimension (14.98 m): **`LOD0`/`LOD1` at 27.0 m,
`LOD1`/`LOD2` at 59.9 m, `LOD2`/`LOD3` at 119.8 m**, measured from the camera
to the centre of `LOD0`'s bounds, at 1080p with a 75° vertical FOV
(1920×1080 renders of the reimported tiers in `scripts/review_asset.py`'s
scene, cropped to the house). Each pair was rendered front, corner and eye
level by noon, from the corner at night with the reference emission, and
from the yard side (160°) by noon and night
(`review/older_audit_2026_11_22/fix_residential/rintamamiestalo_gable_entry/`).

- `LOD0`→`LOD1` at 27.0 m: rings become single recesses; nothing goes.
- `LOD1`→`LOD2` at 59.9 m: the openings go flat, as CLAUDE.md expects. The
  gable vents' pale louvres stay on the red gables and the cellar lights stay
  lit at night, as flush quads; the handrails stay as lean solids. Before
  this pass all three went at this switch, the vents most visibly.
- `LOD2`→`LOD3` at 119.8 m: every opening stays; what changes is the steps
  becoming ramps, the lean handrails and the downpipes going (each under a
  pixel across) and the back canopy. A trial that dropped the vents here
  instead of the pipes showed the front gable's vent going as a pale spot
  under the apex (`trial_vents_dropped_at_lod3/` in the review folder). The
  night pairs differ by a mean of 0.10 to 0.13, with no pixel over 24.

The older review below used the catalog's 50° review camera at 35/70/120 m;
it is kept for what it measured, but the switches above are the consumer's.

**The chimney flue stays recessed on every tier**, where the windows go flush
at `LOD2`. Two flush versions were rendered and dropped. Painted flush from
`LOD2`, the soot lay in the noon sun and read as a dark grey square in the
20 m aerial views, where `LOD1`'s shaded shaft reads black: a change the 70 m
switch would show. Painted flush at `LOD3` alone, it came out barely apart
from the cap (12 grey levels at most, measured on `rintamamiestalo_porch`),
close to the solid top it replaced, for 10 triangles. The recess costs 12
triangles at `LOD2` and 20 at `LOD3`. In the 120 m aerial views it is a dark
dot two or three pixels across on both tiers, and nothing shows at the switch.

The corner-board UV columns now survive through LOD2 and LOD3, including
their plinth/belt boundaries and any raised board starts. These are flush
surface divisions, not added projecting trim. UV/material-seam-preserving
coplanar cleanup (0.001 rad angular tolerance) pays for them within the
ordinary ceilings.

All four exported tiers sample the existing corner region. The white-body
variant consequently retains its contrasting brown boards too. Mechanical
validation reports no failures, closed welded topology, unchanged shared
origin/bounds, and one opaque material with external albedo and correctly
bound ORM (AO/R, roughness/G, metallic/B; UV0 and unit multiplying factors).
The small
hidden-face results in the table are sampled candidates at closure/roof
joins, not evidence of interior partitions.

**Appearance checks.** Reimported GLBs; Cycles CPU, AgX/None, exposure 0.
Perspective 1920×1080, 50° vertical FOV; native-resolution crops without
enlargement. At 65/75 m, compared LOD0/LOD1/LOD2 from front-right (40° azimuth,
30° elevation) and rear (150°/30°), with opposing sun directions. At
115/125/180 m, compared LOD0/LOD2/LOD3 from the front-right under daylight.
Distances are along the view direction to the front/rear bounding face's
mid-height. Corner contrast remains across tiers; the existing flat-window,
small-window removal and stair-ramp transitions are still visible when
blinking frames. The six LOD2 views were also checked at 720²: orthographic
front, rear, sides, top and a 45° elevated front-right view.

**Day/night previews.** LOD0/default red; fixed camera and exposure across
morning, noon, dusk and night, 960×720, 24 samples with denoising. Sun
elevations 15°/60°/6°; night uses a 35° moon proxy and weak ambient light.
The world has a neutral lower hemisphere and blue upper hemisphere.
Glass responded to light direction and darkened at night, but at the value
in use then the pale albedo still read as solid panels in direct daylight.
Those previews were rendered unlit and at that glass value: Night lighting and
Glazing treatment below record the emission behaviour and the glass value the
asset now ships. Calibration in the consumer's day/night environment remains
pending.

**Filtering review is not final acceptance.** Explicit whole-atlas mip3/mip4
stress renders (8×8/16×16 source-texel averaging, albedo in linear light,
ORM linear) were checked face-on at 75 m and at 75° grazing azimuth at
125 m. Narrow trim loses contrast at mip4: a representative corner texel
changes from RGB 213/211/200 to 159/157/149 as its footprint includes
neighboring blank texels. That was with 2 px of padding. The atlas is now padded by `atlas.pad()`,
which fills every texel no region claims from the nearest region's own
edge, and the mip4 stress renders were repeated on the new maps and compared
with the old (see Review status). Coarse mips can still merge regions that
touch, so a demonstrated consumer sampling arrangement is still needed
before filtering sign-off. The renders in that first pass went through
`review_asset.py --texture-dir`, which then rendered the full-resolution
textures, because Blender's glTF importer packs images and a packed image
ignores the substitute; the texel figures above come from the mip files
themselves. The repeat was rendered after the fix. This
review preserves the existing atlases; it does not claim consumer mip
selection, anisotropic filtering, temporal stability or runtime performance.

Reproduce the lighting with `scripts/review_asset.py --day-cycle`, LOD views
with its tier/distance/view options, and explicit mip stress inputs with
`scripts/review_atlas_mips.py`. Working renders and the local gallery are
kept outside the deliverable asset folders. This pass used Blender 5.2.1 LTS
in isolated background processes; the installed MCP addon was not used.

**Downpipes across the switches**, from `review/downpipes_shared_2026_09_25/`
(front, oblique and rear at 35 and 70 m, front and oblique at 120 m, under
noon). At 35 m the eight- and four-sided pipes cannot be told apart. At 70 m
the swan-neck's 0.28 m kick, about 3 px in the oblique view, and the shoe
straighten into one line; side by side the kink under the eave can be found,
and the pipe still reads as a dark line beside the corner board. At 120 m
`LOD2`'s square pipe and `LOD3`'s three-sided one are the same one-pixel line,
so the pipes neither flatten nor vanish at any switch.

**The roof safety kit across the switches**, from
`review/roof_safety_2026_09_25/rintamamiestalo_gable_entry/` (every tier;
front, oblique, aerial and rear at 20 and 60 m, under noon). At 35 m every
other rung still reads as a ladder, and the brackets and the walkway's posts
are under a pixel either side of the switch. At 70 m every fourth rung keeps
the hatching on the slope and the wall ladder's line over the eave, and the
walkway stays. At 120 m the kit goes: its rails are under half a pixel there,
and side by side the ladder's line over the eave can be found missing, not at a
glance. The wall ladder's bare rails stay on `LOD3`, for the extents.

**The handrails across the switches**, from
`review/handrails_2026_09_25/rintamamiestalo_gable_entry/`: `LOD0` to `LOD2`,
front, oblique and rear at 12 and 40 m under noon, before (`before/`) and
after (`after_one/`), and `LOD1` against `LOD2` at 70 m (`switch70/`). At 40 m
the rails and posts read clearly against the plinth and the treads, and `LOD1`
keeps them whole. At 70 m they are about two pixels wide; that pass's `LOD2`
had dropped them, which a side-by-side comparison showed. `LOD2` now keeps
them lean (Consumer screen-size switches above).

## Interior geometry

Measured with `scripts/validate_asset.py` on the exports:

| Tier | Hidden triangles | Share |
| --- | --- | --- |
| `LOD0` | 77 of 2572 | 3.0 % |
| `LOD1` | 64 of 2008 | 3.2 % |
| `LOD2` | 36 of 912 | 3.9 % |
| `LOD3` | 8 of 488 | 1.6 % |

On `LOD2` the lean handrails add most of the new candidates: the rails'
undersides over the treads and the landing post's faces toward the wall,
exterior surface where most sampled rays meet the steps or the wall.

The roof safety kit adds most of the candidates: the roof ladder's rung
undersides, a few centimetres over the sheet, and the walkway plank's
underside over its posts, all exterior surface seen at a grazing angle.

The handrails add a handful more on `LOD0` and `LOD1`: the rails' undersides
over the treads, and the back landing's post's face towards the wall, 2.75 cm
off the siding. The vertical area, 0.2, 0.3, 0.2 and 1.3 m² on the four tiers,
is that post, the downpipes' backs, facing the siding 3 cm away, and on `LOD3`
mostly the backs of the wall ladder's bare rails, facing the west wall. Every
sampled ray from them heads for the wall and meets it, though they are
exterior surface seen at a grazing angle. The rest are slivers where a long
wall's top meets the rake soffit at the eave line, the same class the siblings
keep. The earlier build had none, and the difference is the wall regions
retriangulating after the gable's two attic windows became one. No wall stands
inside the house, by construction. The open chimney flue is not a candidate:
its lining and floor see the sky up the shaft.

## Known simplifications

- **The chimney has one plain flue.** It stands for however many flues the
  stack carries: no dividing walls, no rain hood. Every tier keeps it
  recessed, where the windows go flush at `LOD2`.
- **The railings are solid boards with painted balusters.** A see-through
  railing would need alpha, which CLAUDE.md rules out, and CLAUDE.md asks for
  exactly this of a balcony parapet. The gaps are painted dark, as if in
  shadow. Close up, the railing reads as solid.
- **The terrace base is solid concrete to the ground**, with no skirt boards or
  lattice. It reads as a continuation of the house's plinth.
- **The decks are flat**, with no modelled fall or drain.
- **Reveals are 0.15 m deep**, the siblings' timber-wall figure. Cellar lights
  sit 0.12 m back in the concrete.
- **Some small fixtures are neither modelled nor painted:** wall lamps.
  They fail the 0.25 m test and are placement-specific.
- **The handrails are simplified** (Construction): square-section rails and
  posts, not round tube, with no balusters or infill and no end returns.
- **The roof safety kit is simplified** (Construction): the wall ladder has
  no safety hoop and its top is straight rails rather than a curved grab rail
  over the eave; the walkway is a plain plank on posts, not a perforated
  grating on raked brackets; there is no sweep's platform at the stack.
- **The gutter is painted and the downpipes modelled** (Construction). The
  pipes' clips are the gutter's painted hangers, and each shoe discharges
  onto open ground, with no splash block.
- **Windows go from recessed to flat at the `LOD1`→`LOD2` switch**, as
  CLAUDE.md expects. No opening is dropped on any tier: the cellar lights
  and the gable vents stay to `LOD3` as flush quads.
- **`LOD3` has no downpipes** (Per-tier triangle counts): at that switch they
  are 0.6 px lines.
- **The steps become ramps at `LOD3`**, keeping their footprint. At the
  `LOD2`/`LOD3` switch (about 120 m) a 0.16 m riser is under a pixel, and
  the change is a shading change inside a small patch.

## Texture set

| File | Space | Notes |
| --- | --- | --- |
| `_albedo_<variant>.png` ×5 | sRGB | 1024², 8-bit RGB, no alpha |
| `_orm.png` | Non-Color | 1024², R = AO, G = roughness, B = metallic |
| `_normal.png` | Non-Color | 1024², OpenGL tangent space (+Y green up), shared across tiers/colours |
| `_emission.png` | sRGB | 1024², 8-bit RGB neutral glazing mask; shared across tiers/colours |

The atlas is the rintamamiestalo family's, painted by the shared family
module `scripts/rintamamiestalo.py` for all four houses; `facade_atlas.py`
names this house's layout (`rintamamiestalo.Layout`). A change to the
family's artwork, ORM table or night tint is made once in the module and
reaches all four houses on their next export. Against the family's default
layout this one differs in four things:

- **The gable band S2 is taller.** Its first row now stands for the 3.85 m
  belt, not 4.30 m. Reading from there to the 8.40 m apex takes 4.55 m of
  band, so S2 is painted 4.60 m (rows 288–586).
- **The roof band is shorter to make room for it:** 232 rows over the 6.29 m
  slope, 37 px/m along the slope where the siblings have 41. Across the slope
  it keeps full density. Along it, the only pattern is the snow guard, the
  ridge flashing and the drip edge.
- **The balcony door is a pair of leaves**, 1.40 m across, each one clear
  pane over a solid bottom panel.
- **Two thin full-width strips sit above the unique row:**
  - `DECK`: 0.125 m boards, each its own tone, in a fixed weathered
    grey-brown. The decks sample it at one V, so each board runs the deck's
    length unbroken.
  - `RAIL`: square balusters on a 0.125 m pitch in the trim colour, dark
    between. A railing's baluster zone is squeezed onto its eight rows, which
    carry only a shading gradient.
  Both patterns vary across U only, so they tile along a surface of any
  length. `check_regions()` also fails the bake if a unique region runs
  into the strips, and `check_bands()` checks both strips.

It has no steel deck patch (the balcony sibling's), since this house's decks
are timber, and no bathroom window region.

The rest is the family's:

- 64 px/m on the walls.
- A trim sheet with tiling siding bands (S1 lower walls, S2 gables) and one
  region per opening type. The gable window is the `wide` type, so it shares
  that region and the atlas carries no attic window of its own.
- Bands that tile exactly in U.
- Neutral, dark, opaque glass at roughness 0.08, painted by
  `scripts/glazing.py`. See Glazing treatment below.
- Roughness separates the materials: siding 0.74, trim 0.58, sashes 0.50,
  concrete 0.90, brick 0.86, deck boards 0.80, and the painted steel of the
  roof, gutter, flashing and drip caps 0.46 (the chimney cap 0.48). Painted
  steel is dielectric, metallic 0; the door handles are the one bare metal
  (0.35, metallic 0.80). A ±0.04 roughness noise on a 20 px blur varies the
  timber and concrete; the painted steel takes none. With the roof at
  metallic 0.25 and that noise on it, the sunward slope showed dark blotches
  about 2 m across at every distance.
- The eave fascia is a white board with the gutter across its top, directly
  under the roof edge. Don't move the gutter back to the foot of the board, or
  paint the whole fascia in roof steel; both were tried on the siblings and
  rejected. The downpipes sample the gutter's middle rows (`PIPE_STRIP`), so
  they need no region of their own.
- The chimney flue is soot: a `flue` patch, the blank patch darkened to about sRGB 34 with AO
  0.35, in a row of its own above the other patches (x 750, y 866). It
  lines and floors the open flue on every tier.
- **The chimney brick is the catalog's**, painted by `scripts/brickwork.py`'s
  `paint()`: 0.25 m stretchers on a 0.078125 m course (16 x 5 px), recessed
  joints, a hashed ±10 % tone per brick (seed 5, repeating over the stack's
  24 whole courses; one brick id, no darker id, so no darker bricks). The
  region is top-anchored, so the courses count from the 0.12 m cap
  (`y_ref=cap`) and the course under it is whole; the cut course lands at
  the region's foot, inside the roof, painted as brick. The brick edges are
  rounded (`arris=0.003`: the face rounds down 3 mm over 1 px, a quarter
  round, in the height channel), which reads the stack as separate bricks at
  20 m; at mip 3 it is indistinguishable from square edges. At mip 3 the 5 px
  course beats against the 8 px footprint as faint horizontal banding, as on
  every catalog brick.

### Supersampled atlas, normal map and padding

- **Rasterised by `scripts/atlas.py` at 4 x 4 samples per pixel.** `facade_atlas.py` paints in
  final-pixel coordinates and the canvas stores the samples; they are
  box-filtered down in linear light, so an edge at a fractional position lands
  partway across its pixel instead of snapping to it. The emission mask
  carries the same coverage as grey at pane edges.
- **The normal map is derived from a painted height channel** in metres by
  `atlas.normal_map()`, OpenGL convention. The relief is physical, not
  exaggerated, and only covers what the mesh does not model:
  - siding laps, 18 mm at the butt tapering to 4 mm under the next board, with
    a 4 mm groove at butt joints;
  - casings and the corner-board strip 20 mm proud with rounded arrises; sill
    boards 35 mm; sashes 12 mm proud of the glass;
  - standing seams 22 mm, the snow-guard tubes and brackets, the ridge flashing;
  - the gutter as a 70 mm half-round, and the drip caps;
  - panelled and planked door leaves, the vent's louvre blades, and brick faces
    6 mm proud of the chimney's mortar.
  Glass stays flat. The roof band is stretched in V, so relief that varies up the slope is
  scaled by the band's px/m over 64 to keep its slope physical.
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

### Weathering

- **Placed by `facade_atlas.py`'s `weather()`, drawn by
  `scripts/weathering.py`** at the catalog's moderate level. Its fields
  (dirt, algae, rust, faded paint, rain runs) are amounts, resolved against
  each colour's own palette, so the five variants weather alike. Dirt lerps toward a warm soil colour;
  on steel it is a neutral dust, because soil's brown turned dark roofs
  orange. Dirt roughens the ORM and strips the metallic. Height, the normal
  map and the emission mask are untouched, and glass never weathers.
- **Following height, so it lands the same on every wall:** soil, splash
  specks and a faint green film at the plinth's foot, with runs under the
  flashing's lip; splash-back up the first half metre of siding; dust under
  the soffit from 3.8 m; dust along the laps, from the cavity.
- **The roof band, up the slope from the eave:** long runs, silt at the
  seams' feet, more dirt toward the eave, debris held above the snow guard,
  a little rust at its brackets and on the drip edge, and the paint chalking
  toward the ridge.
- **In the regions:** runs down the fascia from the gutter; dirt and short
  runs on the sills and head casings; water standing on the sashes' bottom
  rails; hand grime round the door handles (on the balcony pair, at the meeting stile) and kicked-up dirt at the
  doors' feet; runs under the chimney cap and salt bloom low on the stack;
  splash at the corner boards' foot.
- **What a shared band cannot carry:** streaks under one particular window or
  corner. Those would repeat on every wall that samples the band.
- The level was chosen on `rintamamiestalo_porch` (see its notes); this
  house takes the same function with its own layout.
- The albedo and ORM PNGs are larger on disk (6 files, 2.6 MB against 1.8 MB before), as the noise
  compresses less; resolution, count and GPU memory are unchanged.

## Glazing treatment

Panes are painted by `scripts/glazing.py`, the catalog's shared treatment.

| | |
| --- | --- |
| base colour | sRGB 50/54/57 (`glazing.BASE`) |
| measured over the glass mask | mean sRGB 57, linear 0.037 |
| relative to the trim around it | 0.25x |
| roughness / metallic | 0.08 / 0 |
| panes in the atlas | 8 |

`albedo()` builds the atlas as before and then hands the glass mask to
`glazing.rooms()`, which gives each pane its own overall level, a falloff
toward the floor, and a lit patch of far wall on about half of them. That is
the room behind the pane rather than a reflection, so it belongs in base
colour; no sill-to-head sky gradient is baked, which Texture Requirements
rule out.

Why it changed: at the previous value the glass measured linear 0.506
and sat at 0.84x the trim around it, so the panes read as glossy
white paint rather than as openings. Seen from outside a window is mostly the
unlit room behind it, and the sky reflection is generated at shading time from
roughness and the dielectric F0 — a pale base colour asks the diffuse lobe to
reflect the sky as well, which double-counts it. The eight-way comparison that
settled the choice lives in `studies/window_glass/`, local only and gitignored.

Limit: the atlas is a trim sheet with one glass region per opening kind, so
panes vary between kinds and not between windows — every window of a kind on
this building is identical, the two wide windows flanking the front door
included. Per-window variety would need several pane
regions per kind and `build.py` picking one per instance. This is the same
constraint already recorded for emission.

Pending: calibration in the consumer's lighting.

## Variant list

There are five variants, each
`export/rintamamiestalo_gable_entry_albedo_<name>.png`. They share one ORM.

| Variant | Walls | Trim and railings | Roof | Door |
| --- | --- | --- | --- | --- |
| `red` (default) | punamulta (falu) red | off-white | dark grey steel | dark green |
| `yellow` | ochre | off-white | brick-red steel | brown |
| `white` | off-white | dark brown | brown steel | brown |
| `blue` | grey-blue | off-white | dark grey steel | brown |
| `green` | sage green | off-white | dark red-brown steel | brown |

This is the low-rise case in CLAUDE.md: a street of these houses differs in
paint, and the variants are exactly that. Glass, plinth, chimney and decking
never change. The railings are trim, so on the `white` house they are dark
brown like its casings.

Every `.glb` references the default (`red`) albedo. Another variant is the same
mesh with that one file swapped. `variants.png` beside `preview.png` shows all
five from the catalog preview camera, with matching day and night rows.

## Night lighting

**Current support.** `rintamamiestalo_gable_entry_emission.png` is a neutral RGB mask
of the atlas generator's final glass ownership IDs. Glazing is grey, each pane lit as a room (see Room-lit panes below);
frames, walls, roof, solid doors and vents are black. Glazed door panels
participate. No interiors or additional geometry were added.
All four GLBs bind the same external sRGB mask through `emissiveTexture`
on UV0. It is shared across every colour. Current texture inventory:
eight unique 1024² images: five albedos, one ORM, one normal map, one emission.

**Game control.** Every GLB defaults to `emissiveFactor = [0, 0, 0]`, with
the texture binding retained. A reference lit factor is linear RGB
`[1.0, 0.88, 0.72]`, the warm white the newer catalog assets use (the family
module's `TINT`); scale it toward zero to dim or switch off. Saved
`source.blend` uses the same linked mask/tint and emission strength zero.
`scripts/window_emission.py` exports a positive reference state, then writes
the default-off core glTF factor while preserving the texture. No emission
extension is needed at this reference intensity. The game owns occupancy,
time and fading: choose lit buildings more frequently in early night and
rarely late at night. Keep that state per placed building. Reused glazing
UVs mean this is one building-wide control, not independent room/window
switching. The PNG contains candidate windows, not a baked occupancy pattern.

**Deliverable sheet.** `variants.png` is 3200×1252, showing red, yellow, white, blue and green, in that order.
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
comparisons at 65/75 m and 115/125 m, 1920×1080 projection, 50° vertical
FOV, 40° azimuth/30° elevation, fixed exposure 0; native pixel crops, Cycles
16 samples with denoising. Rear LOD0/LOD3 views at 75 m supplement the sheet.
Base-atlas versus explicit whole-atlas mip4 views compare LOD2/LOD3 face-on
and at 75° grazing azimuth at 125 m; all three maps are minified
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

### Room-lit panes

Each pane in the emission mask is the lit room behind it, not a flat panel:
`scripts/glazing.py`'s `night_rooms()` multiplies it by its own level, a soft
lamp glow and a falloff toward the floor, and never takes it below about a
fifth. The mask stays neutral grey, so colour, intensity and which buildings
are lit are still the consumer's, and nothing in it says whether a room is
occupied. Averaged over the glass it is 59 % of the old full-white mask
(the catalog runs 52-63 %),
so at the same reference factor the windows read as warm lamplight rather than
pale panels. Every window of one type samples the same atlas region, so every
window of that type carries the same room, the lamp included: the two wide
windows either side of the front door show the same room at night. See the
limit under Glazing treatment.

## Export

```
python3 facade_atlas.py export                      # textures, all five variants
blender --background source.blend --python build.py  # meshes, preview, variants sheet, source.blend
```

Run the textures first, because the UVs index into the atlas and the renders
read it. Run without a `.blend`, `build.py` starts from an empty scene and
writes `source.blend` itself, with the textures linked by relative path. That
is how this asset's `source.blend` was made.

Re-running the build reproduces the four `.glb` files byte for byte, which was
checked over consecutive runs.

Export settings, as `export_all()` passes them:

- `export_format='GLB'`
- `use_selection=True`
- `export_yup=True`
- `export_apply=True`
- `export_keep_originals=True`
- `export_cameras=False`
- `export_lights=False`

`scripts/glb_images.py`'s `strip_embedded_images()` then strips the placeholder `bufferView` that
keep-originals leaves beside each `uri`. The validator confirms uri-only images
on every tier.

**Preview.** It uses the catalog's camera orientation, lens, sun and flat grey
world, with the distance fitted by `_fit_camera()`. It shows the front gable
and the east side. The neutral flat grey world and sun are
`scripts/asset_build.py`'s, the same for every catalog asset, which is what
CLAUDE.md asks of a preview; it is not a deviation.

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

- `scripts/validate_asset.py` on all four tiers: no failures, uri-only
  external images, one material slot, welded manifold topology, pivot at
  ground level and centred on the footprint, emission bound to UV0 and default
  off, the normal map bound at
  scale 1 on every tier with unit-length vectors that all face out, and
  eight 1024² RGB PNGs. No warnings.
- `check_layout()`, so every opening clears the corner boards, the rake and
  the belt line with its margins.
- The six working views at `LOD0`, and the gable elevation compared across
  `LOD1`, `LOD2` and `LOD3` with camera and lighting fixed.
- Tier comparisons at the distances, views and light directions recorded under
  LOD review, and the whole-atlas mip3/mip4 stress renders described there.
- Glazing measured over the glass mask against Style Direction's band.
- Emission off/on on reimported tiers, and the day/night sheet across all five
  colours at `LOD0`.
- The texture pipeline change, before against after with
  `scripts/review_compare.py`: `LOD0` front and oblique at 20 m and 35 m under
  noon, morning and backlight; mip4 stress renders of `LOD2` at 75 m and
  `LOD3` grazing at 125 m; and the catalog preview. Laps, seams and
  mouldings read as raised in direct sun, which confirms the OpenGL green
  channel, and no new colour leaks appear at mip4.
  These mip4 renders were made after fixing `scripts/review_asset.py`: Blender
  5.2's glTF importer packs images, and a packed image ignores `--texture-dir`,
  so every earlier stress render had shown the full-resolution textures.
- The second front window, before against after with
  `scripts/review_compare.py`: every tier, front and oblique at 20 m and 60 m,
  under noon and at night with the reference emission. The window keeps its
  casing, recess and glass on each tier's rules and lights like its twin.
- The open chimney flue, before against after with
  `scripts/review_compare.py`: every tier, oblique and aerial at 20 m and
  60 m, under the noon and reverse suns, and `LOD2` against `LOD3` at 120 m.
  Every difference lies in the chimney top (36 × 19 px at most). The flue
  reads as a dark shaft inside the capped rim on every tier, and as a dark
  dot at 120 m on both sides of the switch.
- The weathering, before against after with `scripts/review_compare.py`:
  `LOD0` oblique and aerial at 20 m and 35 m under noon and morning sun. The
  changes land where `weather()` puts them, and no seam or wrap line shows.
  `scripts/validate_asset.py` still reports no failures or warnings. The
  rebuilt GLBs are byte-identical to the previous ones.
- The downpipes, as CLAUDE.md asks of a change to a finished asset: the folder
  snapshotted into `review/downpipes_shared_2026_09_25/before_snapshot/` first,
  then the same `scripts/review_asset.py` sets rendered from the snapshot and
  from the change and compared with `scripts/review_compare.py`: `LOD0` at 20 m
  from all four sides and the oblique; tiers 0-2 at 35 and 70 m from the front,
  oblique and rear; tiers 2-3 at 120 m from the front and oblique; all under
  noon. Every difference lies on the pipes and their shadows (mean absolute
  difference 0.28 / 255 at most in any view). Close-ups of each pipe's
  swan-neck and shoe at `LOD0` and `LOD1`, and of the whole pipe at `LOD0` and
  `LOD2`. The first rebuild failed the validator's welded-manifold check on
  `LOD2` and `LOD3`: the union had left the soffit round a pipe's hole as a
  keyhole face, which the weld split into two overlapping faces.
  `scripts/asset_build.py`'s `union()` now triangulates such faces before the
  weld (Construction). `scripts/validate_asset.py` reports no failures or
  warnings.

- The roof safety kit, as CLAUDE.md asks of a change to a finished asset: the
  folder snapshotted into
  `review/roof_safety_2026_09_25/rintamamiestalo_gable_entry/before_snapshot/`
  first, then every tier rendered from the snapshot and from the change, front,
  oblique, aerial and rear at 20 m and 60 m under noon. The wall ladder, the
  roof ladder and the walkway are the only additions; the west extent grew 0.18
  m and the pivot moved 0.09 m west with it. `scripts/validate_asset.py` still
  reports no failures or warnings.
- The handrails, as CLAUDE.md asks of a change to a finished asset. The folder
  was snapshotted into
  `review/handrails_2026_09_25/rintamamiestalo_gable_entry/before_snapshot/`
  first. `LOD0` to `LOD2` were then rendered from the snapshot and from the
  change: front, oblique and rear at 12 m and 40 m under noon. The rails and
  posts are the only additions, and the bounds and the pivot are unchanged.
  `scripts/validate_asset.py` still reports no failures or warnings.

- The 2026-11-22 audit fixes (Revision log), as CLAUDE.md asks of a change
  to a finished asset: the folder snapshotted into
  `review/older_audit_2026_11_22/fix_residential/rintamamiestalo_gable_entry/before/`
  first, then the same sets rendered from the snapshot and from the rebuild
  and compared (`compare/`): the tier pairs at the consumer's switches
  (front, corner, eye, rear, noon and night; LOD review), `LOD0` front and
  oblique at 20 and 35 m under noon and the reversed sun, and an aerial and
  an oblique at 25 m under noon and morning sun for the roof. The roof's
  blotches are gone, the gutter, pipes and flashing read as painted steel,
  the far tiers keep every opening and the `LOD2` rails, and nothing else
  changed. Only the ORM changed among the PNGs; albedos, normal map and
  emission are byte-identical. `scripts/validate_asset.py`: 58 PASS, 0 FAIL,
  9 MANUAL, 1 WARN (`source.dirty` true, expected until the sidecar is
  rewritten from a committed tree).

Pending, and outside this repository:

- Consumer filtering: `atlas.pad()` fills every gutter, but coarse mips can
  still merge regions that touch, and no consumer filtering arrangement has
  been demonstrated.
- The normal map in the consumer: MikkTSpace tangent generation on import and
  its filtering at distance.
- Consumer import and material control, LOD switching, night exposure, light
  spill, anisotropic filtering and runtime performance measurement.

## Tooling versions

- **Blender 5.3.0**, which saved the current `source.blend` and built and
  validated the current exports.
- **MCP extension: not used for this asset.** It was built, rendered and
  checked entirely headless. The Blender Lab "MCP" extension installed at the
  time was v1.0.3.

These are recorded as a known-good marker, not a requirement.

- **CPython 3.14.10 with numpy 2.5.5, scipy 1.18.1 and Pillow 13.0.0** for the
  texture export.

## Revision log

- **2026-11-22 — audit fixes: far-tier openings, lean handrails, painted
  steel, night tint.** In the family module `scripts/rintamamiestalo.py`:
  the cellar lights and gable vents stay to `LOD3` as flush quads, and this
  house's downpipes go at `LOD3` to pay for them; the handrails stay on
  `LOD2` as lean solids, the terrace flight's 2.6 cm further in; painted
  steel (roof, gutter, flashing, drip caps, chimney cap) is dielectric at
  roughness 0.46-0.48 with no roughness noise; the reference lit factor is
  `[1.0, 0.88, 0.72]`. Triangle counts changed from 2572 / 2008 / 762 / 470
  to 2572 / 2008 / 912 / 488. Only the ORM changed among the PNGs; the GLBs,
  `source.blend`, the sidecar, `preview.png` and `variants.png` were
  regenerated. Notes corrected where stale (the Blender version, the
  consumer's switch distances, the preview world, the hidden-face counts,
  `facade_atlas.py` now the family module's layout rather than a copy).
- **2026-11-22 — rounded chimney brick.** The chimney's `brickwork.paint()`
  call counts its courses from the cap with the painter's `y_ref` instead of
  computing the foot itself (same bond and tones; the cut course at the
  region's foot, inside the roof, is now brick, not mortar) and turns on its
  3 mm rounded arris (Texture set). Albedo, ORM and normal map changed in the
  chimney region and its gutter only. No geometry changed; triangle counts
  unchanged.
- **2026-11-22 — catalog brick on the chimney.** The chimney's private brick
  loop (0.0625 m course, bevelled bricks) gave way to `scripts/brickwork.py`'s
  `paint()` on the catalog's 0.078125 m course (Texture set). No geometry
  changed; triangle counts unchanged.
- **2026-09-25 — handrails.** A rail on posts down the right-hand side, going
  up, of both entrance flights, from the new shared `scripts/handrails.py`
  (Construction). Triangle counts changed from 2296 / 1732 / 762 / 470 to 2572 /
  2008 / 762 / 470. No atlas pixel changed. The GLBs, `source.blend`,
  `preview.png` and `variants.png` were regenerated.

- **2026-09-25 — roof safety kit.** A wall ladder, a roof ladder and a walkway
  to the chimney, from the new shared `scripts/roof_safety.py` (Construction),
  at the back of the house. Triangle counts changed from 1100 / 856 / 522 / 454
  to 2296 / 1732 / 762 / 470. The overall width grew from 8.90 m to 9.08 m and
  the pivot moved 0.09 m west. No atlas pixel changed; the GLBs,
  `source.blend`, `preview.png` and `variants.png` were regenerated.

- **2026-09-25 — downpipes.** Two downpipes from the new shared
  `scripts/downpipes.py` (Construction). One from each eave, at diagonally
  opposite corners. `scripts/asset_build.py`'s `union()` now triangulates the
  keyhole faces the union leaves round the pipes' holes here. `facade_atlas.py`
  gained `GUTTER_PX` and `PIPE_STRIP`, which name the gutter rows the pipes
  sample; no pixel changed and the PNGs were not regenerated. Triangle counts
  rose by 164, 84, 40 and 26. The GLBs, `source.blend`, `preview.png` and
  `variants.png` were regenerated.

- **2026-09-25 — weathering.** `facade_atlas.py` gained `weather()`, which
  places the shared `scripts/weathering.py` fields: dirt, algae, rust, faded
  paint and rain runs (Texture set, Weathering). Every albedo and the ORM
  changed; the normal map and the emission mask did not. `source.blend`,
  `preview.png` and `variants.png` were regenerated, and the GLBs rebuilt
  byte-identical.

- **2026-09-25 — open chimney flue.** The chimney was a solid block with a
  capped top. It is now a 0.12 m shell round one 0.36 × 0.60 m flue, sunk
  0.80 m and lined and floored in soot on every tier; the soot is a new `flue`
  atlas patch. Triangle counts rose by 16, 16, 12 and 20. Every albedo and
  the ORM changed around the new patch, and the normal map in 12 padding
  texels; the emission mask did not. The GLBs, `source.blend`, `preview.png`
  and `variants.png` were regenerated.

- **2026-09-25 — second front window.** The front gable gained a wide window
  right of the door, at x = +2.10 m, mirroring the living room's about the
  door, sill 1.50 m like it. It reuses the `wide` atlas region, so no texture
  changed; the triangle counts rose by 24, 16, 8 and 2. The GLBs, `preview.png`,
  `variants.png` and `source.blend` were regenerated.

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
  normal map on every tier. The front gable lost its kitchen window, leaving the wide window beside
  the door, and the rear gable's bathroom window and window became one
  wide window, the `bath` atlas region going with them. The triangle
  counts fell by 48, 32, 12 and 4. Every PNG, the GLBs, `preview.png` and
  `variants.png` were regenerated.

- **2026-09-20 — gable window.** The rear gable's two narrow windows became one
  wide 1.80 × 1.40 m sash centred under the ridge, sill unchanged at 4.65 m;
  triangle counts fell by 22, 14, 8 and 4. The front gable was left alone,
  having the balcony doors at that level and no room beside them. The `attic`
  atlas region went — its 80 × 97 px slot at x = 401 is blank background now,
  no other region moved, and all seven images were re-baked at 1024².
  Massing, roof, entrances, steps, pivot, atlas bands and the per-tier opening
  rules were untouched.

- **2026-09-19 — corner boards through the lower tiers.** `LOD2` and `LOD3` were
  rebuilt so the corner-board UV columns survive, coplanar cleanup paying for
  them inside the ordinary ceilings. Only those two meshes were replaced in
  `source.blend` and re-exported; the `LOD0`/`LOD1` meshes and GLBs, every PNG
  and the catalog preview were preserved, and no palette or architectural
  change was made.
