# rintamamiestalo_balcony

## Style brief

A composite Finnish *rintamamiestalo*, the standardised one-and-a-half-storey
timber house built in huge numbers after 1945. The type is a near-square block
under a steep 45° gable roof, the attic storey lit by one wide window in each
gable end, a tall concrete plinth over a cellar, a chimney on the ridge, and
horizontal lap siding with contrasting corner boards and window casings.

This is the balcony sibling of `rintamamiestalo_porch` and
`rintamamiestalo_side_entry`. It has the same block, roof and window types,
with the type's porch-and-balcony front:

- **A wide entrance porch**, 4.40 × 2.60 m, centred on the long front wall.
  The front door is on its front face beside a wide window, with a window in
  each side wall.
- **A balcony on the porch's flat roof.** It has a solid parapet, 1.0 m high,
  clad in the same siding and capped with a trim board. A white trim band runs
  round the porch at the balcony floor line.
- **A wall dormer (frontespiisi)** over the porch: the front wall carried up
  through the eave. It gives the attic storey a full-height wall for the door
  onto the balcony, its one opening. Its shed roof falls to the
  front and overhangs the balcony door.
- **The back door** is in the middle of the rear wall, under its canopy.

The porch, the parapet and the dormer share one width, so their sides stand on
one line.

Materials follow the type:

- painted lap siding and painted trim;
- a standing-seam steel roof with snow guards;
- a board-formed concrete plinth;
- a red-brick chimney with a metal-capped rim round an open flue;
- a roof-coloured steel balcony deck;
- plain-glass windows: every window, and the balcony door's glazing, is one
  clear pane inside a thin frame, with no crossbars and no mullions. Don't add
  divisions on a rebuild.

The roof carries the safety kit Finnish rules ask of it, in the gutter's steel:
a ladder up the back wall, a roof ladder up the rear slope and a walkway along
it to the chimney.

It is meant to be placed as street filler in a residential district, many
times over, beside its two siblings. Colour variety comes from the variants,
and front variety from mixing the three houses.

## Category and secondary use

`buildings/residential/`. No secondary use.

## Hero/landmark status

**No.** Ordinary budgets, a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) |
| --- | --- |
| Main block, walls | 10.00 × 8.00 m |
| With the porch (2.60 m forward, 4.40 m wide, centred) | 10.00 × 10.60 m |
| Ground contact, including both flights of steps | 10.00 × 14.08 m |
| Overall, including the 0.35 m rake overhangs | 10.70 × 14.08 m |

Main block heights: the wall meets the soffit at 4.30 m, the fascia bottom is
at 3.85 m, the ridge at 8.61 m and the chimney top at 9.56 m.

Porch, balcony and dormer heights:

- The balcony deck is at 3.75 m and the parapet top at 4.75 m.
- The dormer's front wall meets its soffit at 6.30 m.
- The dormer's fascia bottom, at the eave edge, is 6.17 m, which leaves
  2.42 m of headroom over the deck.
- The dormer's roof runs into the main roof 2.86 m back from the front wall.

The pivot is centred on the plan's bounding box, overhangs and steps included.
That is the footprint `scripts/validate_asset.py` checks, and it puts the pivot
1.30 m in front of the main block's centre. The pivot is taken from `LOD0` and
applied to every tier. Every tier keeps the same extents (at `LOD3` the steps
become ramps with the same footprint), so a LOD switch never moves the house.
`build_all()` asserts this.

## Story height

**Ground floor 3.10 m.** The floor is at 0.70 m on the plinth and the attic
floor at 3.80 m, inside the 3.0–3.3 m standard.

The attic storey sits under the roof, with a 0.50 m knee wall up to the eave
at 4.30 m. Its windows are in the gables and the dormer. Behind the dormer
front it has a full-height wall, 2.50 m from the attic floor to the dormer
soffit.

## Door leaf height

**2.10 m** for all three doors, with no transom or fanlight. The casing adds
0.19 m above each leaf.

- **Front and back doors:** the thresholds are at the 0.70 m floor level,
  reached by a landing and three risers.
- **Balcony door:** the threshold is at the 3.80 m attic floor, 5 cm above the
  deck. It is glazed: one clear pane over a solid bottom panel.

## Window sills

**1.50 m above ground**, which is 0.80 m above the floor. That is a little
above the ~1.4 m guide, and the reason is the type itself: the cellar plinth
lifts the whole ground floor 0.70 m, as it does on the real houses. The steps
up to both ground-floor doors make that lift legible beside the door.

The dormer front carries only the balcony door, at the attic floor. A wide
window will not fit beside it: the 4.75 m parapet sets the lowest sill that
reads, and the dormer's eave the highest head. The gable windows have their
sills at 4.65 m.

## Eave overhang

| Where | Projection |
| --- | --- |
| Main eaves | **0.45 m**, the catalog default |
| Main rakes (gable ends) | 0.35 m |
| Dormer front eave | 0.45 m, over the balcony |
| Dormer rakes | 0.30 m |
| Back-door canopy | 0.80 m, a covered entrance rather than an overhang |

All sit within 0.3–0.6 m except the canopy, which is ruled as a covered
entrance: the same case as a portico at a smaller scale. Soffits slope with the
rafters (the underside of the roof slab). Overhangs are kept at every tier.

The main eaves on either side of the porch run into the parapet's side walls.
The parapet is 0.14 m taller than the eave at the wall line, so the eave's end
is wholly covered.

## Construction

`build.py` unions closed solids with Blender's Exact boolean:

- the house as **three side-by-side solids**: the west block, the dormer
  section and the east block;
- the porch-and-balcony;
- the main roof in three pieces;
- the dormer's shed roof;
- the chimney, the back canopy and two flights of steps.

**Why the house is three solids.** The dormer section's front wall runs from
the ground to the dormer eave in one plane. A dormer built as a separate part
on top of a whole house would overlap the house's front wall in that plane, and
the balcony door, from 3.80 to 5.99 m, would straddle the join at the wall top.
Split at the dormer's width instead, the three parts touch face to face, and
the union merges the touching faces away. The rear wall is in three pieces
too. Their siding offsets carry on from each other, so the boards run
unbroken along the rear.

**Why the main roof is three pieces.** Over the dormer, the main roof's front
slope has to start behind the dormer's front wall. The middle piece is the
same chevron cut 2.20 m back from the front wall, a cut buried inside the
dormer section. The dormer's roof runs 0.35 m past the line where it meets
the main roof, and its back end is buried there. `check_layout()` asserts
that both cut ends finish buried.

**The porch-and-balcony is one solid:**

- sided outer walls, carried up past the deck as the parapet;
- a U-shaped cap board;
- the parapet's inner faces;
- the deck.

Its back face lies on the dormer section's front wall. The parapet is one
corner board thick, so its inner lines fall exactly on the corner-board
columns' vertices, and the cap meets the walls without T-junctions at every
tier.

**The wall builder takes a top profile** of (s, z) points instead of a height
and an apex, so the same code builds eave walls, gables and the dormer
section's stepped sides. It also takes a stack of siding bands, so the porch's
S1-then-S2 walls and the dormer's shifted S1 need no special case.

**Two fixes found here:**

- **`Builder.face()` computes its zero-area test in double precision, from
  coordinates relative to the first vertex.** A door has no bottom casing, so
  its casing ring's bottom face has zero area and is skipped. The old test
  summed cross products of absolute positions in mathutils' 32-bit floats. At
  the balcony door's height, that left enough rounding for the degenerate face
  to pass as real and land a third face on the threshold edge. The fix has
  been ported to both siblings, where it had not triggered.
- **`close_solid()` caps a given number of loops.** The porch-and-balcony has
  only a floor to cap, and each pair of vertices it is given splits the lid:
  the dormer section's lid is split at the ridge and at the kink where the
  dormer top meets the roof line.

**The chimney is open at the top.** Its steel-capped rim is a 0.12 m half-brick
shell round one 0.36 × 0.60 m flue, sunk 0.80 m and lined and floored with the
atlas's soot patch, on every tier (see LOD review). The top stands 0.95 m over
the ridge, so the flue's floor stays clear of the roof slab and the union
leaves the shaft empty.

`check_layout()` asserts, before building:

- openings overlapping each other or a corner board, running under a roof
  line, or straddling a band change or the plinth top;
- the dormer front reading S1 outside its painted rows, or its shift out of
  course phase, or the parapet taller than S2;
- the gable outgrowing its atlas band, or the roof slope disagreeing with the
  atlas;
- the main slab's cut or the dormer roof's back end poking out;
- the main eave rising past the parapet;
- the dormer fascia under 2.2 m over the deck;
- the back canopy missing its door, sitting on it, or below head height;
- the chimney flue's floor reaching into the roof slab;
- a downpipe within 0.25 m of a corner, or with less than 0.2 m of wall
  between it and an opening;
- the wall ladder within 0.3 m of a corner or with less than 0.2 m of wall
  between it and an opening, the back steps, the back canopy or the downpipe,
  or with a bracket in the soffit; the walkway not running the stack's width,
  or its edge not just behind the stack;
- a handrail within 0.1 m of its door's jamb, a bottom post off its
  tread, or a flight too short for a sloping rail.

### Downpipes

Four downpipes from the shared `scripts/downpipes.py`, unioned in with the
other solids, one from every gutter. The porch and the dormer take the middle
of the front, so the main front eave is two runs, each draining to its outer
end: the east run's pipe stands 0.25 m in from the front's east corner and
the 2.8 m west run's 0.25 m in from its west corner, clear of the standard
window beside it. The rear eave's stands 0.25 m in from its west corner. The
west gable end therefore shows a pipe at each corner, the east gable one.

The dormer's gutter drains down the dormer front at its east end, 0.25 m in
from the corner and clear of the balcony door, onto the balcony deck: the same
pipe, swan-neck from the dormer's sloping soffit and shoe, standing on the
deck instead of the ground (`DeckPipe` in `build.py`, which only moves the
foot; the shape is `downpipes.py`'s). `check_layout()` asserts it clear of the
dormer's corners and the door, and its shoe over the deck inside the parapet.

The deck behind its solid parapet drains through a **spout**: a closed box
0.12 m wide and 0.08 m tall, 2 cm over the deck, run through the parapet's
east side 0.35 m behind the front corner and standing 0.25 m out, sampling the
gutter's rows like the pipes. It is clear of the porch's corner board and its
east window, and away from the entrance, so the water falls beside the porch's
front corner. A painted scupper was not an option: the parapet samples the
tiling S2 band, which cannot place one. Both go at `LOD3` (`SPOUT_LAST`),
where each is under a pixel across at the switch, the pipe mostly behind the
parapet, and the tier has no 18 triangles to spare for them under its
ceiling (Per-tier triangle counts).

Each is a 0.1 m pipe standing 3 cm off the siding, as it would on its
clips, and joined to nothing but the soffit it leaves, so it cuts no line
through the wall's triangles. It rises into the soffit 0.36 m out from the
wall, just inside the fascia the gutter is painted on, falls 0.25 m, steps
back to the wall at 45 degrees, and ends in a shoe kicked 0.15 m out, its
mouth about 0.2 m above the ground. Its sides sample the middle five rows of
the fascia band's gutter (`PIPE_STRIP` in `facade_atlas.py`), so the pipe
takes the gutter's steel in every colour, and the gutter's hangers, a metre
apart, read as its clips. No atlas region was added and no pixel changed.
The tiers are the module's: eight sides with both bends at `LOD0`, four at
`LOD1`, straight at `LOD2`, three-sided at `LOD3`.

On this house the union leaves the soffits round the pipes' holes on every tier
as a keyhole: one face running out to the hole and back along a bridge of
coincident vertices, which the weld would split into two overlapping faces.
`scripts/asset_build.py`'s `union()` triangulates any such face before the
weld, so the soffit there is triangles.

### Roof safety kit

From the shared `scripts/roof_safety.py`, as CLAUDE.md asks of a roof steeper
than 1:8 carrying something serviced from it: the chimney, which the sweep has
to reach. The porch and the dormer take the front, whose outer pieces are too
short for a ladder beside their windows and downpipe, and the kit belongs at
the back anyway, where such kits usually are.

- **a wall ladder up the rear wall**, centred at x = -2.15 between the
  bathroom window and the west window, where the rear wall's three pieces lie
  in one plane, on brackets 0.57 m off the siding, passing 0.12 m outside the
  fascia and running 1 m above the roof edge, to 5.16 m;
- **a roof ladder straight above it up the rear slope**, from 0.25 m up from
  the eave to 0.8 m short of the ridge, its rails 8 cm off the sheet on
  brackets that run down into the slab;
- **a level walkway**, 0.30 m wide, along the rear slope 0.5 m below the
  ridge, from the roof ladder east to stand behind the stack: 3.30 m on
  posts.

Every part samples the gutter's rows (`PIPE_STRIP`), the rows the downpipes
use, so the kit takes the gutter's steel in every colour, as a matched
rainwater and safety system does, and the painted hangers, a metre apart,
read as joints. The ladders' rungs are 0.28 m apart, 3 cm square, each one's
faces meeting the holes it leaves in the rails, so each ladder is one closed
solid; the walkway's plank and posts are separate solids the union joins to
the roof. The tiers are the module's: every rung with brackets and posts at
`LOD0`, every other rung at `LOD1`, every fourth and no brackets or posts at
`LOD2`, and no kit at `LOD3`, where the rails are under half a pixel.

### Handrails

From the shared `scripts/handrails.py`. CLAUDE.md asks for them on every
entrance flight of three risers or more, and this house has two: the front
steps up to the porch door and the back steps up to the kitchen door, each
climbing 0.68 m in three risers to a landing. Each flight has one rail, on its
right going up: the east side of the front flight and the west side of the
back one. It runs 5 cm in from the steps' edge, level over the landing and
then down the flight, on three posts: one on the landing by the wall, one at
the head of the flight and one on the bottom tread.

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
  a flight, so the rail's line over the steps survives the `LOD1`/`LOD2`
  switch at about 56 m. They go at `LOD3`, where a 45 mm rail is a third of
  a pixel.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 2896 | 12,000 | casing rings, reveals and glass on every window and door, the balcony door included; cellar lights recessed; corner boards; stepped treads; canopy, open chimney flue; four downpipes, eight-sided with swan-neck and shoe, the dormer's onto the deck; the deck's spout; roof safety kit with every rung, brackets and posts; a handrail on each flight |
| `LOD1` | 2214 | 4,000 | each opening becomes one recess the size of its casing; cellar lights and vent go flush; downpipes four-sided; kit with every other rung; handrails kept |
| `LOD2` | 980 | 1,500 | openings flush, the cellar lights and gable vents among them; corner-board paint retained; redundant coplanar subdivisions dissolved; downpipes straight, no swan-neck or shoe; kit with every fourth rung, no brackets or posts; handrails lean (separate solids, 120) |
| `LOD3` | 498 | 500 | every opening still flush, the bathroom window, cellar lights and vents included; back canopy dropped, steps become ramps; corner-board paint retained; three downpipes three-sided, the dormer's and the spout dropped; roof safety kit and handrails dropped |

The two downpipes added for the dormer's gutter and the front-west eave run,
and the deck's spout, cost 180, 102, 56 and 8 triangles (`LOD3` keeps only
the front-west pipe). The small openings kept as flush quads on the far
tiers cost about 10 triangles each with the hole they leave in their wall:
62 at `LOD2` (four cellar lights, two vents) and 72 at `LOD3` (with the
bathroom window).

**`LOD0`–`LOD2` sit far under their ceilings. That is correct, and they
should not be padded.**

- The building is a 10 × 8 m box with one gable roof, one dormer and one
  porch.
- The walls are triangulated as polygons with holes, not as a grid of cells.
- Every opening on every elevation is already cut at `LOD0`.
- Nothing else here clears the 0.25 m test.

**`LOD3` is 2 under the 500 ceiling.** The dormer, balcony and porch stay
whole at every tier, and so does every opening; the dormer's downpipe and
the deck's spout are what it cannot afford. When the corner paint was kept on the low tiers,
dissolving redundant coplanar subdivisions brought this tier from 576 to 406
triangles, and `LOD2` from 656 to 486, without removing those features.

Modelled trim (overhangs, canopy, chimney) is a few dozen triangles, far under
the quarter-budget cap.

**The roof safety kit costs 1210, 890, 242 and 0 triangles** on the four
tiers. Most of it is the rungs with the holes they leave in the rails,
and the brackets and posts with the squares they cut in the wall and the
sheet.

**The handrails cost 314, 314, 0 and 0 triangles** on the four tiers: two
rails in two runs each, the posts, and the squares the posts cut in the
landings and treads. At about an eighth of `LOD0` they cost more than the
downpipes and far less than the roof kit, and leave `LOD0` and `LOD1` far
under their ceilings.

**The two downpipes cost 164, 84, 30 and 22 triangles** on the four tiers, the
pipes' own faces and the holes they leave in the soffit together.

## LOD review

### Consumer screen-size switches

The consumer switches by screen size, at about 1.8, 4 and 8 times the
house's largest bounds dimension (14.08 m): **`LOD0`/`LOD1` at 25.3 m,
`LOD1`/`LOD2` at 56.3 m, `LOD2`/`LOD3` at 112.6 m**, measured from the camera
to the centre of `LOD0`'s bounds, at 1080p with a 75° vertical FOV
(1920×1080 renders of the reimported tiers in `scripts/review_asset.py`'s
scene, cropped to the house). Each pair was rendered front, corner and eye
level by noon, from the corner at night with the reference emission, and
from the yard side (160°) by noon and night
(`review/older_audit_2026_11_22/fix_residential/rintamamiestalo_balcony/`).

- `LOD0`→`LOD1` at 25.3 m: rings become single recesses; nothing goes.
- `LOD1`→`LOD2` at 56.3 m: the openings go flat, as CLAUDE.md expects. The
  cellar lights and gable vents stay as flush quads and the cellar lights
  stay lit at night; the handrails stay as lean solids; the four downpipes
  straighten, the spout stays.
- `LOD2`→`LOD3` at 112.6 m: the bathroom window stays and stays lit; what
  changes is the steps becoming ramps, the lean handrails, the dormer's
  downpipe and the spout going (each under a pixel across), and the back
  canopy. The night pairs differ by a mean of 0.12 to 0.13, with no pixel
  over 24 (16 from the yard before).

The older review below used the catalog's 50° review camera at 35/70/120 m;
it is kept for what it measured, but the switches above are the consumer's.

**The chimney flue stays recessed on every tier**, where the windows go flush
at `LOD2`. Two flush versions were rendered and dropped. Painted flush from
`LOD2`, the soot lay in the noon sun and read as a dark grey square in the
20 m aerial views, where `LOD1`'s shaded shaft reads black: a change the 70 m
switch would show. Painted flush at `LOD3` alone, it came out barely apart
from the cap (12 grey levels at most, measured on `rintamamiestalo_porch`),
close to the solid top it replaced, for 8 triangles. The recess costs 18
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
`review/roof_safety_2026_09_25/rintamamiestalo_balcony/` (every tier; front,
oblique, aerial and rear at 20 and 60 m, under noon). At 35 m every other rung
still reads as a ladder, and the brackets and the walkway's posts are under a
pixel either side of the switch. At 70 m every fourth rung keeps the hatching
on the slope and the wall ladder's line over the eave, and the walkway stays.
At 120 m the kit goes: its rails are under half a pixel there, and side by
side the ladder's line over the eave can be found missing, not at a glance.

**The handrails across the switches**, from
`review/handrails_2026_09_25/rintamamiestalo_balcony/`: `LOD0` to `LOD2`,
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
| `LOD0` | 47 of 2896 | 1.6 % |
| `LOD1` | 32 of 2214 | 1.4 % |
| `LOD2` | 34 of 980 | 3.5 % |
| `LOD3` | 2 of 498 | 0.4 % |

The largest candidates on `LOD0`-`LOD2` are the dormer downpipe's back,
3 cm off the dormer front, where every sampled ray meets the wall: exterior
surface, as for every pipe. On `LOD2` the lean handrails add most of the
rest: the rails' undersides over the treads and the landing posts' faces
toward the wall.

The roof safety kit adds most of the candidates: the roof ladder's rung
undersides, a few centimetres over the sheet, and the walkway plank's
underside over its posts, all exterior surface seen at a grazing angle.

The handrails add a handful more on `LOD0` and `LOD1`: the rails' undersides
over the treads, and the landing posts' faces towards the wall, 2.75 cm off
the siding, exterior surface where most sampled rays meet the wall. No hidden
face is vertical on any tier (0.0 m²). The remainder is slivers where wall
tops meet the roofs above them, round the gables' rakes and the dormer. No
wall stands inside the house, by construction. The open chimney flue is not a
candidate: its lining and floor see the sky up the shaft.

## Known simplifications

- **The chimney has one plain flue.** It stands for however many flues the
  stack carries: no dividing walls, no rain hood. Every tier keeps it
  recessed, where the windows go flush at `LOD2`.
- **The balcony has a solid parapet, not a railing.** A see-through railing
  would need alpha, which CLAUDE.md rules out, and a sided parapet is a normal
  detail on these houses anyway. From street level it hides the lower half of
  the balcony door.
- **The deck is flat**, with no modelled fall; it drains through the spout
  in the parapet's east side (Construction), and its sheet is one flat patch
  colour.
- **Reveals are 0.15 m deep**, the siblings' timber-wall figure. Cellar lights
  sit 0.12 m back in the concrete.
- **The handrails are simplified** (Construction): square-section rails and
  posts, not round tube, with no balusters or infill and no end returns.
- **The roof safety kit is simplified** (Construction): the wall ladder has
  no safety hoop and its top is straight rails rather than a curved grab rail
  over the eave; the walkway is a plain plank on posts, not a perforated
  grating on raked brackets; there is no sweep's platform at the stack.
- **The gutter is painted and the downpipes modelled** (Construction). The
  pipes' clips are the gutter's painted hangers, and each shoe discharges
  onto open ground or the deck, with no splash block.
- **There are no inside-corner boards** where the porch meets the front wall;
  only convex corners get one.
- **Windows go from recessed to flat at the `LOD1`→`LOD2` switch**, as
  CLAUDE.md expects. No opening is dropped on any tier: the cellar lights,
  the gable vents and the bathroom window stay to `LOD3` as flush quads.
- **The steps become ramps at `LOD3`**, keeping their footprint. At the
  `LOD2`/`LOD3` switch (about 113 m) a 0.17 m riser is about one pixel, and
  the change is a shading change inside a patch of about 10 x 6 px.
- **`LOD3` has no dormer downpipe and no deck spout** (Construction): both
  are under a pixel across at that switch.

## Texture set

| File | Space | Notes |
| --- | --- | --- |
| `_albedo_<variant>.png` ×5 | sRGB | 1024², 8-bit RGB, no alpha |
| `_orm.png` | Non-Color | 1024², R = AO, G = roughness, B = metallic |
| `_normal.png` | Non-Color | 1024², OpenGL tangent space (+Y green up), shared across tiers/colours |
| `_emission.png` | sRGB | 1024², 8-bit RGB neutral glazing mask; shared across tiers/colours |

The atlas is the rintamamiestalo family's, painted by the shared family
module `scripts/rintamamiestalo.py` for all four houses; `facade_atlas.py`
names this house's layout (`rintamamiestalo.Layout`), which adds two of the
family's optional regions to the default:

- a `door_balcony` region (`balcony_door="single"`): the glazed door, one
  clear pane over a solid bottom panel;
- a `deck` patch (`deck_patch=True`): roof steel a shade darker.

The layout's `check_regions()` fails the bake if two regions in the
hand-packed unique row overlap or one leaves the atlas. A change to the
family's artwork, ORM table or night tint is made once in the module and
reaches all four houses on their next export. The rest is the family's:

- 64 px/m, with the roof band stretched up the slope.
- A trim sheet with tiling siding bands (S1 lower walls, S2 gables) and one
  region per opening type. The gable window is the `wide` type and shares that
  region.
- Bands that tile exactly in U.
- `check_bands()`.
- Neutral, dark, opaque glass at roughness 0.08, painted by
  `scripts/glazing.py`. See Glazing treatment below.
- Roughness separates the materials: siding 0.74, trim 0.58, sashes 0.50,
  concrete 0.90, brick 0.86, and the painted steel of the roof, deck sheet,
  gutter, flashing and drip caps 0.46 (the chimney cap 0.48). Painted steel
  is dielectric, metallic 0; the door handles are the one bare metal (0.35,
  metallic 0.80). A ±0.04 roughness noise on a 20 px blur varies the timber
  and concrete; the painted steel takes none. With the roof at metallic 0.25
  and that noise on it, the sunward slope showed dark blotches about 2 m
  across at every distance.
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

**Two walls read their siding from outside the usual rows:**

- **The parapet reads S2 from the deck up.** S2's belt board lands at the
  balcony floor line as a trim band round the porch, and as a skirting inside
  the parapet. The corner boards stop under it, as they do under a gable's
  belt.
- **The dormer front reads S1 shifted down two metres.** It rises to 6.40 m,
  and S1 is only painted to 4.44 m. Two metres is sixteen whole courses, so
  the boards stay in phase. The shift also lands S1's under-soffit shadow
  directly under the dormer's soffit. `check_layout()` asserts the range, the
  plinth staying out of sight above the deck, and the course phase.

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
  rails; hand grime round the door handles and kicked-up dirt at the
  doors' feet; runs under the chimney cap and salt bloom low on the stack;
  splash at the corner boards' foot.
- **What a shared band cannot carry:** streaks under one particular window or
  corner. Those would repeat on every wall that samples the band.
- The level was chosen on `rintamamiestalo_porch` (see its notes); this
  house takes the same function with its own layout.
- The albedo and ORM PNGs are larger on disk (6 files, 2.5 MB against 1.7 MB before), as the noise
  compresses less; resolution, count and GPU memory are unchanged.

## Glazing treatment

Panes are painted by `scripts/glazing.py`, the catalog's shared treatment.

| | |
| --- | --- |
| base colour | sRGB 50/54/57 (`glazing.BASE`) |
| measured over the glass mask | mean sRGB 60, linear 0.041 |
| relative to the trim around it | 0.27x |
| roughness / metallic | 0.08 / 0 |
| panes in the atlas | 8 |

`albedo()` builds the atlas as before and then hands the glass mask to
`glazing.rooms()`, which gives each pane its own overall level, a falloff
toward the floor, and a lit patch of far wall on about half of them. That is
the room behind the pane rather than a reflection, so it belongs in base
colour; no sill-to-head sky gradient is baked, which Texture Requirements
rule out.

Why it changed: at the previous value the glass measured linear 0.506
and sat at 0.83x the trim around it, so the panes read as glossy
white paint rather than as openings. Seen from outside a window is mostly the
unlit room behind it, and the sky reflection is generated at shading time from
roughness and the dielectric F0 — a pale base colour asks the diffuse lobe to
reflect the sky as well, which double-counts it. The eight-way comparison that
settled the choice lives in `studies/window_glass/`, local only and gitignored.

Limit: the atlas is a trim sheet with 9 glass regions, one per opening
kind, so panes vary between kinds and not between windows — every window of a
kind on this building is identical. Per-window variety would need several pane
regions per kind and `build.py` picking one per instance. This is the same
constraint already recorded for emission.

Pending: calibration in the consumer's lighting.

## Variant list

There are five variants, each `export/rintamamiestalo_balcony_albedo_<name>.png`.
They share one ORM.

| Variant | Walls | Trim | Roof and balcony deck | Door |
| --- | --- | --- | --- | --- |
| `red` (default) | punamulta (falu) red | off-white | dark grey steel | dark green |
| `yellow` | ochre | off-white | brick-red steel | brown |
| `white` | off-white | dark brown | brown steel | brown |
| `blue` | grey-blue | off-white | dark grey steel | brown |
| `green` | sage green | off-white | dark red-brown steel | brown |

This is the low-rise case in CLAUDE.md: a street of these houses differs in
paint, and the variants are exactly that. Glass, plinth and chimney never
change.

Every `.glb` references the default (`red`) albedo. Another variant is the same
mesh with that one file swapped. `variants.png` beside `preview.png` shows all
five from the catalog preview camera, with matching day and night rows.

## Night lighting

**Current support.** `rintamamiestalo_balcony_emission.png` is a neutral RGB mask
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

**Deliverable sheet.** `variants.png` is 3200×1286, showing red, yellow, white, blue and green, in that order.
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
occupied. Averaged over the glass it is 61 % of the old full-white mask
(the catalog runs 52-63 %),
so at the same reference factor the windows read as warm lamplight rather than
pale panels. Every window of one type samples the same atlas region, so every
window of that type carries the same room; see the limit under Glazing
treatment.

## Export

```
python3 facade_atlas.py export                      # textures, all five variants
blender --background source.blend --python build.py  # meshes, preview, variants sheet, source.blend
```

Run the textures first, because the UVs index into the atlas and the renders
read it. Run without a `.blend`, `build.py` starts from an empty scene and
writes `source.blend` itself, with the textures linked by relative path.

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
world, with the distance fitted by `_fit_camera()`. The neutral flat grey
world and sun are `scripts/asset_build.py`'s, the same for every catalog
asset, which is what CLAUDE.md asks of a preview; it is not a deviation.

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
  every tier: the union had left the soffit round a pipe's hole as a keyhole
  face, which the weld split into two overlapping faces.
  `scripts/asset_build.py`'s `union()` now triangulates such faces before the
  weld (Construction). `scripts/validate_asset.py` reports no failures or
  warnings.

- The roof safety kit, as CLAUDE.md asks of a change to a finished asset: the
  folder snapshotted into
  `review/roof_safety_2026_09_25/rintamamiestalo_balcony/before_snapshot/`
  first, then every tier rendered from the snapshot and from the change, front,
  oblique, aerial and rear at 20 m and 60 m under noon. The wall ladder, the
  roof ladder and the walkway are the only additions; the bounds and the pivot
  are unchanged. `scripts/validate_asset.py` still reports no failures or
  warnings.
- The handrails, as CLAUDE.md asks of a change to a finished asset. The folder
  was snapshotted into
  `review/handrails_2026_09_25/rintamamiestalo_balcony/before_snapshot/` first.
  `LOD0` to `LOD2` were then rendered from the snapshot and from the change:
  front, oblique and rear at 12 m and 40 m under noon. The rails and posts are
  the only additions, and the bounds and the pivot are unchanged.
  `scripts/validate_asset.py` still reports no failures or warnings.

- The 2026-11-22 audit fixes (Revision log), as CLAUDE.md asks of a change
  to a finished asset: the folder snapshotted into
  `review/older_audit_2026_11_22/fix_residential/rintamamiestalo_balcony/before/`
  first, then the same sets rendered from the snapshot and from the rebuild
  and compared (`compare/`): the tier pairs at the consumer's switches
  (front, corner, eye, rear, noon and night; LOD review), `LOD0` front and
  oblique at 20 and 35 m under noon and the reversed sun, an aerial and an
  oblique at 25 m under noon and morning sun for the roof, and every tier at
  14 m (oblique, rear, aerial) for the new pipes and the spout. The roof's
  blotches are gone, the gutter, pipes and flashing read as painted steel,
  the dormer's pipe stands at the dormer front's east end with its shoe on
  the deck, the front-west eave's pipe at its west corner, and the spout
  reads as a short steel stub through the parapet's east side at the deck;
  the far tiers keep every opening and the `LOD2` rails. Only the ORM
  changed among the PNGs; albedos, normal map and emission are
  byte-identical. `check_layout()` passes with the new pipes' and spout's
  checks. `scripts/validate_asset.py`: 58 PASS, 0 FAIL, 9 MANUAL, 1 WARN
  (`source.dirty` true, expected until the sidecar is rewritten from a
  committed tree).

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
  steel, night tint; downpipes for the dormer and the front-west eave, a
  spout for the deck.** In the family module `scripts/rintamamiestalo.py`:
  the cellar lights, gable vents and the bathroom window stay to `LOD3` as
  flush quads; the handrails stay on `LOD2` as lean solids; painted steel
  (roof, deck sheet, gutter, flashing, drip caps, chimney cap) is dielectric
  at roughness 0.46-0.48 with no roughness noise; the reference lit factor
  is `[1.0, 0.88, 0.72]`. In `build.py`: a downpipe from the front-west
  eave run's gutter, one from the dormer's gutter onto the deck (`DeckPipe`)
  and a spout through the parapet (Construction). Triangle counts changed
  from 2716 / 2112 / 742 / 418 to 2896 / 2214 / 980 / 498. Only the ORM
  changed among the PNGs; the GLBs, `source.blend`, the sidecar,
  `preview.png` and `variants.png` were regenerated. Notes corrected where
  stale (the Blender version, the consumer's switch distances, the preview
  world, the hidden-face counts, `facade_atlas.py` now the family module's
  layout rather than a copy).
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
  (Construction). Triangle counts changed from 2402 / 1798 / 742 / 418 to 2716 /
  2112 / 742 / 418. No atlas pixel changed. The GLBs, `source.blend`,
  `preview.png` and `variants.png` were regenerated.

- **2026-09-25 — roof safety kit.** A wall ladder, a roof ladder and a walkway
  to the chimney, from the new shared `scripts/roof_safety.py` (Construction),
  at the back of the house. Triangle counts changed from 1192 / 908 / 500 / 418
  to 2402 / 1798 / 742 / 418. No atlas pixel changed; the GLBs, `source.blend`,
  `preview.png` and `variants.png` were regenerated.

- **2026-09-25 — downpipes.** Two downpipes from the new shared
  `scripts/downpipes.py` (Construction). One from each eave, at diagonally
  opposite corners. `scripts/asset_build.py`'s `union()` now triangulates the
  keyhole faces the union leaves round the pipes' holes here. `facade_atlas.py`
  gained `GUTTER_PX` and `PIPE_STRIP`, which name the gutter rows the pipes
  sample; no pixel changed and the PNGs were not regenerated. Triangle counts
  rose by 164, 84, 30 and 22. The GLBs, `source.blend`, `preview.png` and
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
  atlas patch. Triangle counts rose by 16, 16, 18 and 20. Every albedo and
  the ORM changed around the new patch, and the normal map in 12 padding
  texels; the emission mask did not. The GLBs, `source.blend`, `preview.png`
  and `variants.png` were regenerated.

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
  normal map on every tier. Each gable end now carries one wide window per storey, and the dormer
  front only the balcony door: its two small windows went, with their
  `dormer` atlas region. The triangle counts fell by 100, 68, 34 and 30. Every PNG, the GLBs, `preview.png` and
  `variants.png` were regenerated.

- **2026-09-20 — gable window.** The two narrow windows in each gable end became
  one wide 1.80 × 1.40 m sash centred under the ridge, sill unchanged at
  4.65 m; triangle counts fell by 44, 28, 16 and 20. The wall dormer kept its
  own pair flanking the balcony door, so the small atlas region stayed and was
  renamed from `attic` to `dormer` — a rename and nothing else, re-baking to
  byte-identical albedo, ORM and emission files. Massing, roof, entrances,
  steps, pivot, atlas bands and the per-tier opening rules were untouched.

- **2026-09-19 — corner boards through the lower tiers.** `LOD2` and `LOD3` were
  rebuilt so the corner-board UV columns survive, coplanar cleanup paying for
  them inside the ordinary ceilings. Only those two meshes were replaced in
  `source.blend` and re-exported; the `LOD0`/`LOD1` meshes and GLBs, every PNG
  and the catalog preview were preserved, and no palette or architectural
  change was made.
