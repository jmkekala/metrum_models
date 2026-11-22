# liikekeskus_pharmacy

## Style brief

A neighbourhood pharmacy of the kind that stands on its own in a car park at
the edge of a housing estate: one shop under one roof, behind one customer
door in the middle of the street front. One tall retail storey in coursed
split-face stone under a single broad gable whose ridge runs front to back, so
the whole of the street elevation is one gable end. Deep overhangs in white
painted boarding, a white crest capping the ridge from rake to rake, and the
pharmacy's illuminated sign standing on the crest on short steel legs: a
1.6 m cube carrying the pharmacy mark on all four sides, because a building in
a car park is approached from every direction and a flat blade would show half
of them nothing but its edge.

The street front reads as one generous shop: two 9 m display windows on a low
kick panel, one each side of the middle pier, and the entrance -- a glazed
pair under a transom light -- through a portal in the foot of that pier, on
the centre line, so a central walk can run straight to it between parking
either side. One green sign band over the windows, broken only by the pier,
names the shop once ("APTEEKKI", over the left window) and carries the mark
once (over the right); a lit plaque with the same mark hangs on the pier over
the door.

The type's recognisable move is the contrast between that white A and the stone
under it, and the way the gable is opened up: above the sign band the wall
becomes two raking curtain-wall panels, one each side of a wide stone pier that
runs from the pavement to the apex, opened at its foot for the door.

The rainwater goods and the roof safety kit are one matched system in the
white of the boarding: a half-round gutter along each eave fascia, a downpipe
at each end of each gutter, and, at the back of the left (-X) side, the
fixed route the roof's two ventilation housings and the ridge sign are
serviced by -- a wall ladder up past the eave, a roof ladder up the slope, a
walkway along the ridge to the sign and one across to the left housing, and
a short roof ladder down the other slope beside the right housing. The rakes
carry no gutter, so the gables carry no pipes.

## Category and secondary use

`buildings/commercial/`. Single use: one shop, a pharmacy. No secondary use,
no residential component.

## Hero/landmark status

Not a hero. Ordinary triangle ceilings and the 1024 texture limit apply and are
met; no budget exception is claimed.

## Footprint

24.0 x 16.0 m of wall. Including the roof, which overhangs on every side, and
the wall ladder, which stands 1.08 m off the left wall, 0.18 m outside the
eave's 0.9 m, the exported bounding box is 25.98 x 18.48 m in plan and
11.925 m tall to the top of the ridge sign; the ridge crest's end caps stand
0.04 m past each rake board. The pivot is the centre of that box, so it sits
0.09 m left (-X) of the wall ring's centre.
The middle pier projects 0.25 m in front of the wall line (`LOD0` - `LOD2`)
and the lit plaque over the door 0.10 m in front of the pier; the side
buttresses 0.30 m and the wall-hung air handler 0.55 m from the side walls.
None is inside the 24.0 x 16.0 figure, so a placement footprint should use the
bounding box.

### What stands outside the wall line

- **Front (street):** the middle pier, 2.8 m wide, 0.25 m proud, with the
  entrance through its foot (the passage is open pavement, no step); the
  plaque over the door, 0.35 m proud of the wall line at 3.45 - 4.65 m; the
  roof's 1.2 m rake overhead. Nothing else on the ground: no steps, ramp,
  canopy, bollards or planters.
- **Sides:** two stone buttresses per side, 0.70 m wide and 0.30 m proud, on
  the ground (`LOD0`/`LOD1` only); the air handler on the right side at
  1.5 - 2.7 m, 0.55 m proud; two downpipes per side, 0.1 m across, 0.03 m
  off the wall, their shoes kicking out to 0.23 m; on the left side the wall
  ladder, 0.5 m wide, its rails 1.02 - 1.08 m off the wall, on every tier;
  the 0.9 m eaves overhead.
- **Rear:** nothing on the ground; the maintenance door and the louvres are
  in the wall plane. The 1.2 m rake overhead.

## Story height

One storey, 4.0 m from the pavement to the eave line. That is a deliberate
departure from the 3.0 - 3.3 m catalog default, under Style Direction's
allowance for a taller retail ground floor: the shopfront head is at 3.25 m and
the 0.75 m of sign fascia above it has to clear it. Nothing above the eave is
floor -- the gable is roof space, lit through the curtain wall.

## Door leaf height

2.25 m to the head of every leaf, inside the 2.0 - 2.4 m band. The shop has
one customer door, its main entrance: a pair 2.0 m wide overall (two 1.0 m
leaves), centred on the street front. Above it a 1.0 m transom light runs to
the 3.25 m head, glazing rather than door, behind a transom bar at 2.25 m, so
the leaf height stays readable. The maintenance door at the back (service) is
a 1.0 m single leaf, 2.25 m.

## Window sills

The display windows start at 0.35 m, above a kick panel, with a transom
bar at the door's 2.25 m head line and their head at 3.25 m; the side
windows sit at 1.1 m (head 2.5 m), below the 1.4 m the catalog treats as chest height. The gable
curtain wall starts at 4.0 m, which is above the occupied floor and reads as
clerestory, not as a window anyone stands at.

## Eave overhang

0.9 m at the two eaves and 1.2 m at the two rakes, both with a 0.375 m fascia
and a boarded soffit. That is well past the 0.3 - 0.6 m default and is the
point of the type: the overhang is what the building is recognised by from a
car park, it shelters the shopfronts, and the reference band would leave the
gable looking like a shed. The catalog already carries one documented wide
overhang, `lahikauppa_corner` at 1.5 m.

## Construction

The exported shell is the union of the closed solids of the wall ring, the
roof, the ridge crest, the middle pier, the plaque over the door, the ridge
sign and its stand, the wall-hung air handler, the roof stacks, four
buttresses, four downpipes (`scripts/downpipes.py`) and the roof safety kit
(`scripts/roof_safety.py`). Each is
simple on its own; the union is what trims the wall tops into the roof slab
and leaves the boundary of one empty volume.

Five details are worth knowing before changing anything:

- **The wall ring's lid is two faces, not one.** Its rim follows the gable, so
  a single n-gon across it would not be planar. It is split at the two ridge
  vertices and each half lies in one roof plane.
- **Everything that meets the roof runs *into* the slab, never up to it.** The
  soffit falls 0.45 m for every metre it comes out, so anything stopping at the
  wall head would touch it along one line and push through it everywhere
  further out -- tangential contact, which is the case an exact boolean handles
  worst, and it leaves a slot that reads as hidden surface. Walls, buttresses
  and the middle pier all overshoot by 0.12 m and are trimmed flush.
- **The ridge crest's foot follows the roof planes rather than cutting them
  flat.** A horizontal cut across a ridge lies inside a 0.375 m slab over only
  about 15 mm of height, which is not a solid intersection to hand a boolean.
  Its foot is 0.15 m above the slab's underside, so its two end faces are
  five-sided, folding where the roof does. The union trims it to the shingles
  and leaves a 0.6 m wide box, 0.30 m above the ridge and 0.435 m at its
  sides, running rake to rake. Its ends stand 0.04 m past the rake boards
  rather than flush with them, which would lay a face on a face, so each end
  caps the apex.
- **The sign stands on the crest on four legs**, 80 mm square steel, in two
  pairs along the ridge 1.2 m apart and 0.4 m across between centres: the
  crest is 0.6 m wide and a leg beside it would stand on the shingles. The
  cube's underside is 0.25 m clear of the crest. Each leg runs 0.05 m into the
  crest and the cube so the union meets solid overlaps. `check_layout()` fails
  the build if a leg stands off the crest or outside the cube, if the crest's
  foot leaves the slab, or if a roof stack comes within 0.1 m of the crest.
- **The entrance goes through the middle pier.** The front is corner pier
  (1.6 m), display window (9.0 m), middle pier (2.8 m), display window,
  corner pier; there are no party piers. The door unit (2.0 x 3.25 m, leaves
  to 2.25 m) is cut into the wall at the front's centre and recessed 0.18 m
  like the windows. The pier solid has a portal through its whole depth,
  2.10 x 3.30 m, i.e. 50 mm clear of the door's reveal on each side and at
  the head, so no pier face lies in the plane of a wall face; the 50 mm step
  of wall reads as a rebate round the door inside the passage. The portal is
  lined in the pier's own coursing turned round its corners and has no floor.
  `check_layout()` fails the build if the door leaves the front's centre, if
  the portal leaves less than 0.3 m of stone either side, or if the plaque
  leaves the pier above the portal. The plaque runs back 0.10 m behind the
  wall line on every tier, so at `LOD3`, where the pier is gone, it still
  meets a solid overlap and stands 0.20 m proud of the bare wall.
- **The sign boards carry the gable panels' outer jambs** (6.6 m and 17.4 m
  along the front) as vertices on their top edge, since those no longer land
  on a pier.

### Rainwater goods

A half-round gutter is painted across the top of each eave fascia (Texture
set), and four downpipes hang from it, built by `scripts/downpipes.py` with
its own tier modes: one at each end of each eave, 0.5 m in from the corner
(right wall at 0.5 m and 15.5 m from the front corner, left wall at 0.5 m
and 15.5 m from the rear corner), where both ends of either side wall are
clear of the windows, the buttresses and the air handler. Each leaves the
soffit 0.81 m out from the wall, just inside the fascia, on a swan-neck, runs
down 0.03 m off the wall on its clips and ends in a shoe; it is joined to
nothing but the soffit it rises into. `check_layout()` runs
`downpipes.problems()` on each against the windows, buttresses, air handler
and the wall ladder. The rakes carry no gutter.

### Roof safety kit

The two ventilation housings and the lit sign on the ridge are serviced from
the roof, whose 1:2.2 slope is far over 1:8, so the roof carries the fixed
route `scripts/roof_safety.py` builds, in the gutter's white (it samples
`PIPE_STRIP`). The entrance is in the front gable and the catalog view looks
at the right side, so the kit is on the left (-X) eave wall's rear half.

- **Wall ladder** at 1.8 m from the rear corner (y = 6.2 m), between the rear
  downpipe and the first window, from the ground to 1.0 m above the eave
  edge (4.97 m), its rails 1.02 m off the wall, 0.12 m outside the fascia, on
  three brackets. The eave is under 8 m, so no cage. The eave's soffit falls
  0.45 m per metre outward, so the top bracket is set from the soffit at the
  fascia (3.595 m), not at the wall (4.0 m): it stops at 3.37 m.
- **Roof ladder** straight above it, from 0.25 m up the slope from the eave
  edge to 0.75 m short of the ridge line, 13.1 m of ladder, on brackets
  running into the slab.
- **Ridge walkway**, a level plank on posts along the left slope just under
  the crest (0.15 m clear of its side), from the roof ladder's top forward to
  0.2 m behind the sign (y = -6.3 m), 12.75 m.
- **Housing walkway** leaving the roof ladder's side at the left housing's
  level (centred on the housing's middle up the slope) and stopping 0.2 m
  beside it, 2.7 m.
- **Housing ladder.** The right housing stands on the other slope, which no
  walkway on the left can reach: a short roof ladder (3.3 m) runs from 0.15 m
  below the housing's downslope side up beside it, 0.2 m clear, to 0.15 m
  short of the crest's side, where the climber steps over the crest to the
  ridge walkway. The module's roof ladder starts at an eave; this one is
  given an eave line on the slope at its foot.
- The plain vent pipes are not serviced items.

`check_layout()` runs `roof_safety.problems()` on the wall ladder (corners,
windows, buttresses, downpipes, soffit) and checks every piece on the roof
against the stacks, the crest and the sign, 0.1 m clear of each, and each
walkway or ladder against what it serves, within 0.4 m of it. The kit thins
by its own modes (Per-tier triangle counts); `LOD3`, which drops its rungs
and fittings, keeps bare rails on the three ladders and the ridge plank. The
wall ladder's rails set the building's -X extent, so the bounds and the
pivot hold on every tier.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | Note |
| --- | --- | --- | --- |
| `LOD0` | 4,002 | 12,000 | shell 1,024, downpipes 320, roof kit 2,658 |
| `LOD1` | 1,972 | 4,000 | shell 976, downpipes 160, roof kit 836 |
| `LOD2` | 796 | 1,500 | shell 428, downpipes 72, roof kit 296 |
| `LOD3` | 484 | 500 | shell 368, downpipes 56, roof kit 60 (bare rails, ridge plank) |

Every tier is under its ceiling and nothing has been padded. The
building is a rectangular box with a single unbroken gable over it: there are
no dormers, no roof steps, no bays and no returns in the plan. What makes it
read is texture and one large piece of massing, and the only shell geometry
that earns its place is the opening reveals, the middle pier and its portal,
the plaque over the door, the four side buttresses, the wall-hung air
handler, the five roof stacks, the ridge crest and the sign's stand. The
crest and the stand cost 110 triangles on every tier, most of them where the
union cuts the four legs into the crest's top and the cube's underside.

Most of the rest is the roof safety kit: 13.1 m of roof ladder, 12.75 m and
2.7 m of walkway on posts, a 5 m wall ladder and a 3.3 m housing ladder,
every rung's hole in its rails and every bracket's and post's cut in the roof
counted. That is about 22 % of each tier's ceiling at `LOD0`, `LOD1` and
`LOD2`, within Trim allocation's quarter, which is why the kit thins faster
than `roof_safety.MODES`: with the module's own modes `LOD1` came out at
3,076, three quarters of its ceiling. The downpipes cost 80 triangles each
at `LOD0` (eight sides, both bends), 40 at `LOD1`, 18 straight at `LOD2` and
14 three-sided at `LOD3`.

The tiers are genuinely distinct rather than four copies:

- `LOD0` cuts every opening on every elevation; the roof pipes are drums of
  eight sides; the downpipes are eight-sided with both bends; the kit has
  every rung, its brackets and the walkways' posts.
- `LOD1` cuts every opening too (the side windows' 0.14 m reveals,
  78 triangles, were flat here until the audit found their loss at the 46 m
  switch). The roof pipes and the downpipes go to four sides; the kit keeps
  every other rung and drops its brackets and posts, 4 cm bars under a pixel
  at 46 m (`KIT_MODES`).
- `LOD2` takes every opening flat, the door included (the pier and its
  portal stay, as massing), and drops the three roof pipes. The downpipes are
  straight, without swan-neck or shoe; the kit keeps every eighth rung, the
  rails being what reads at 103 m.
- `LOD3` keeps the two ventilation housings, four-sided boxes as on every
  tier (40 triangles; their going showed on the roofline at the 206 m
  switch), and drops the middle pier's 0.25 m projection, portal included: the door stays, painted flat in the wall, and
  the plaque stays over it. The pier is the same stone as the wall behind it,
  so what is lost is a shadow line, not a colour. The downpipes are
  three-sided. The kit loses its rungs, fittings and the housing walkway and
  keeps bare three-sided rails on the wall ladder (which sets the -X extent),
  the roof ladder and the housing ladder, 16 triangles each, and the ridge
  walkway's plank, 12: with only the wall ladder's rails kept, the white
  lines of the roof ladder and the ridge plank vanishing were the largest
  change at the 206 m switch. They touch nothing and are appended after the
  weld. That leaves `LOD3` 16 triangles under its ceiling.
- The ridge crest and the sign's stand stay on every tier. The crest is the
  white line along the roofline, which Appearance Across LODs keeps, and
  without its legs the sign would float over the ridge.

## LOD review

**The consumer's switches** are by screen size: at about 1.8, 4 and 8 times
`LOD0`'s largest bounds dimension (25.98 m), seen with a 75 degree vertical
FOV at 1920 x 1080, i.e. `LOD0`/`LOD1` at about 47 m, `LOD1`/`LOD2` at
104 m and `LOD2`/`LOD3` at 208 m (46 / 103 / 206 m before the wall ladder
widened the bounds by 0.18 m). Those are the distances the tiers are judged
at now; the review below them, at the catalog's suggested 35 / 70 / 120 m
with a 50 degree camera, is the older authoring record.

Reviewed at the consumer's switches with the game camera (75 degree vertical
FOV, 1920 x 1080, distance from the camera to the centre of `LOD0`'s bounds;
front at 10 degrees up, corner at 45 degrees round and 25 up, eye level at
1.7 m and 30 degrees round, noon, and the corner at night lit), before and
after the gutter-and-kit revision, as pair sheets of adjacent tiers with
their difference:

- **47 m, `LOD0`/`LOD1`:** the side windows' reveals going flat, the change
  the audit found (171 pixels over 24 levels in the eye view, 594 at night),
  is gone: the reveals are cut on `LOD1` now. What changes is the kit's
  brackets and the walkway's posts going, a dotted line of single pixels
  along the ridge walkway seen over the left rake from the front, and the
  downpipes' bends going from eight to four sides: 16, 36 and 4 pixels over
  24 levels by day, none at night.
- **104 m, `LOD1`/`LOD2`:** the three roof pipes go, the front reveals and
  now the side windows' reveals flatten, and the kit's rungs thin from every
  other to every eighth, which at a fifth of a pixel per rung does not show;
  the downpipes lose their bends. 48 - 167 pixels over 24 levels by day, as
  before the revision (51 - 157); at night the lit side windows' reveals
  flattening adds a little (764 against 650).
- **208 m, `LOD2`/`LOD3`:** the middle pier and its portal flatten (left,
  as the audit called it minor: the pier is the wall's own stone and costs a
  shadow line), the air handler goes, and the kit loses its rungs and the
  housing walkway. The ventilation housings, which went here before and
  showed as two bumps on the roofline, stay; so do the white rails of the
  three ladders and the ridge plank, whose going was otherwise the largest
  change at this switch (88 - 124 pixels over 24 levels with only the wall
  ladder's rails kept). 30, 86 and 80 pixels over 24 levels by day, 31 at
  night (before the revision 30, 105, 87 and 31): what is left is the pier
  and the air handler, and the roof ladder's rungs.

The roof kit is seen from the street front too: from a low front view the
left roof ladder shows as a white line just above the left rake and the wall
ladder's top over the left eave, as a roof ladder does on a real gable. The
kit stands where the rules put it, at the back; nothing was moved for that.

The older authoring record, with `scripts/review_asset.py` (perspective,
1920 x 1080, 50 degree vertical FOV, distance along the view direction to the
centre of the assessed wall, front and oblique, noon), at the catalog's
suggested 35 / 70 / 120 m, before the gutter and the kit: at 35 m the
four-sided roof pipes were indistinguishable from the eight-sided ones; at
70 m the three pipes went, each about a pixel of dark against the roof; at
120 m the middle pier flattened. The single-shop front was reviewed the same
way at 30/40, 65/75 and 115/125 m: the portal reads as a dark recess at the
pier's foot through `LOD2`; at `LOD3` the flat door, the plaque and the two
green boards keep the entrance and the window rhythm legible. The roof pipes
once stopped at `LOD0`, and three dark posts disappearing off the ridge was
the one change caught at the first switch, so they carry to `LOD1`.

These are authoring comparisons in Blender. They are not evidence about
runtime switching, mipmap selection or frame time. **Pending:** representative
consumer-scene measurement -- visible instance counts per tier, hardware,
resolution, FOV, shadow settings, timings and VRAM -- none of which can be
taken here.

## Interior geometry

`scripts/validate_asset.py`'s sampled test reports 307 of 4,002 triangles
hidden at `LOD0` (7.7 %, 0.1 m2 of it vertical), 66 of 1,972 at `LOD1`
(3.3 %), 26 of 796 at `LOD2` (3.3 %) and 9 of 484 at `LOD3` (1.9 %, 0.0 m2
vertical). Before the roof kit the shell alone gave 1, 1, 0 and 1, slivers the
exact boolean leaves where a gable panel's raking head meets the rake and in
the rear gable's coursing, each under a centimetre across. The rest are the
kit's own exterior faces, located by the coordinates the validator prints:
the roof ladders' and walkways' undersides and rung-hole cheeks 5 - 8 cm over
the shingles, which the fixed ray fan mostly sends into the sheet or the
ladder itself; at `LOD3` the largest are at the same points as `LOD2`'s.
The bare rails and the ridge plank `LOD3` appends add none: they are closed
solids wound outward. (An earlier export had one rail of each ladder and
the plank inside out, 32 of its 41 candidates then.) All are surface of the
outside, seen from the low oblique views of the kit; none is buried. They are inspection candidates,
not proof either way; no buried partition was found. The wall ring is a
single closed solid capped with a floor and a two-plane lid, so there is no
interior to bury anything in.

## Known simplifications

What the shell does not model, and what carries the feature instead:

- **No interior.** The wall ring is one closed solid with a floor and a lid,
  and every opening is closed by an opaque pane or door leaf.
- **Coursing, shingles, board joints and the gutter's roll are texture, not
  geometry.** The normal map (`_normal.png`, bound on every tier) carries
  their relief from the painted height channel; the modelled depth is the
  opening reveals, the middle pier, the four buttresses, the wall-hung air
  handler, the roof stacks, the downpipes and the roof kit.
- **The gutter is painted on the eave fascia**, a half-round roll in the
  height channel with a hanger every metre; no stop ends or outlets are
  modelled, and the downpipes rise into the soffit just inside the fascia
  where the outlet would be.
- **The roof kit has no guard rails or toe boards on the walkways and no
  snow guards**; the walkways are one plank on posts, the ladders rails and
  rungs on brackets, as `scripts/roof_safety.py` builds them. The ridge
  walkway and the right housing's ladder meet over the crest with no crossing
  step.
- **The roof is textured at 13 texels/metre**, a fifth of the density used at
  eye level, so a shingle reads as a tab and a course rather than as an edge.
- **One emissive factor for the whole shop**: the two display windows share
  the shopfront band, so they cannot be lit separately.
- **The entrance has no step, ramp or canopy.** The pavement runs level
  through the portal to the threshold, and the 1.2 m rake overhangs it.
- **The sign's stand is four plain legs.** No rails, braces or fixing plates:
  at 80 mm they span under three pixels at the 35 m switch, and anything
  finer is open framework that no texture could carry.

## Texture set

Seven PNGs, all 1024 x 1024, 8-bit RGB, lossless, no alpha:

| File | Role | Shared by |
| --- | --- | --- |
| `_albedo_grey_stone.png` | default colour | all four tiers |
| `_albedo_beige_stone.png` | colour | all four tiers |
| `_albedo_red_stone.png` | colour | all four tiers |
| `_albedo_brown_stone.png` | colour | all four tiers |
| `_orm.png` | occlusion / roughness / metallic | every colour, all tiers |
| `_normal.png` | tangent-space normal, OpenGL (+Y green up) | every colour, all tiers |
| `_emission.png` | candidate glazing and lit fixtures | every colour, all tiers |

The large relief is modelled; the normal map, derived from the painted height,
carries the split-face coursing, the shopfront sections, the board joints and
the shingles (see Supersampled atlas, normal map and padding below).

**Texel density.** 64 texels/metre on everything a customer stands in front
of -- the stone, the display windows, the doors, the side windows, the soffit and
the sign boards. Two documented deviations:

- the gable curtain wall at 48, because it is 4 m above the fascia and never
  closer than the width of a car park;
- the roof at 13, because 18.4 x 14.1 m of slope at 64 would need more of the
  sheet than the whole rest of the building. A shingle tab is 12 px across and
  a course 5 deep, which is enough to read as a shingled slope from the air and
  from an upper window.

**Atlas layout.** A trim sheet: three bands running the full width and tiling
horizontally (stone, shopfront, white eave), then unique regions above them.
`facade_atlas.check_regions()` fails the bake if two regions overlap, collide
with the bands or leave no room for their gutter, and `check_bands()` fails it
if a stray id lands in a tiling band.

The stone band also tiles **vertically**, on a 4 m period, because the gable
walls run to 9.5 m and a band tall enough to cover them at 64 texels/metre
would take two thirds of the sheet. `build.py` cuts every gable elevation into
horizontal courses at 4.0 m and 8.0 m and indexes the band from each course's
own base, and the band carries **periodic** padding at both ends -- its top
rows in the gutter below it and its bottom rows in the gutter above -- so a
sample straddling a wrap line finds the artwork that actually continues there.
The wear and rain noise on that band is restricted to vertical frequencies that
are multiples of four for the same reason; anything else would put a different
blemish either side of the seam. The seams are invisible in the rear elevation,
which is the largest unbroken run of stone on the building.

Opening reveals and the returns of the buttresses and the middle pier sample
the stone band too, unrolled round their corner, rather than taking a flat
swatch. The portal through the middle pier is lined the same way. Only three
flat swatches remain: for the caps the union buries, for the sign box's lid
(and the plaque's edges) and its steel underside and legs, and for the
painted returns of the roof plant.

**The gutter and the eave band's rows.** The soffit band's 24 fascia rows are
the eave fascia's, 0.375 m at 64 texels/metre: the drip edge (rows 0-1),
board with joints every 0.2 m, a line along the board's top (rows 10-11), the
gutter's shadow on the board (12-13), the half-round gutter (`GUTTER_PX` 9
rows, 0.14 m, 14-22) with its roll in the height channel (0.06 m) and a
hanger every metre, and the roof's edge (row 23). The gutter is the boards'
white (`ID_GUTTER`, the variant's eave colour, roughness 0.48, dielectric).
Its middle five rows are `PIPE_STRIP`, which the downpipes and the whole roof
kit sample along their length, so the rainwater goods and the kit are one
colour in every variant and the hangers read as their clips and joints. The
band is full width, so the kit's and the pipes' long runs wrap in u like the
fascia's own. The atlas had no free full-width rows for a gutter band of its
own, which is why the rakes and the crest, which carry no gutter, now take
only the fascia rows under it:

- the rake boards map their 0.375 m onto rows 0-11 (`RAKE_ROWS`), a 2.0 times
  stretch in v of a face whose only detail along v is the drip edge and the
  top line, both now about 6 cm deep where they were 3 cm;
- the ridge crest's sides and end caps map the solid's whole height, foot
  included, onto the same 12 rows, so the drip edge along the bottom shows
  only under the end caps, where they stand clear of the rake boards; the
  shingles cut the long sides off above it. That stretches the rows about
  3.5 times in v (1.8 before the gutter), on a plain white face;
- the crest's top samples the far soffit rows (`CREST_TOP_ROWS`, 84-100 of
  the band, past the eave's shadow ramp), its 0.6 m across 16 rows: a 2.40
  times stretch across the crest, as before, now on soffit board whose
  joints are a shade darker than the fascia's.

The roof stacks' sides each take their whole casing region across them: the
0.70 m box's sides fit `VENT_BOX`'s 45 px at 64 texels/metre, and the 0.85 m
box's are squeezed to 0.83 of that density, on plain painted steel.

The sign's four faces share one 1.6 x 1.6 m region
(`LOGO`, 102 x 102 px); the whole face is clear of the roof, so the mark is
centred on it between a white edge top and bottom. The plaque over the door
takes the same region on its 1.2 m face, so it is drawn at 85 texels/metre
rather than 64: a third deviation, sharper rather than blurrier, on one small
sign.

The two sign boards are 9.0 x 0.75 m each, 576 x 48 px at 64 texels/metre,
one region per board (`FASCIA`). To make room for them the roof stacks'
regions and the three flat swatches moved to the free corner of the upper
shelf; the single-door region of the old three-unit front is gone.

**Padding** is 6 px everywhere, clamped for the non-repeating bands and the
regions, periodic for the stone band.

**Mip review** of the single-shop atlas: every tier at its switch distance
and one level beyond (`LOD1` 70 m at mip 2-3, `LOD2` 120 m at mip 3-4,
`LOD3` 250 m at mip 4-5), front and oblique, noon and reverse sun, the
default and one contrasting colour, with whole-atlas mips and again at a
per-texel level matched to each tier's texel density
(`review/phase2_2026_11_21/mips/liikekeskus_pharmacy/`). No gutter leak at
any tier's real distance: the shopfront, the sign boards with their
lettering and cross, and the plaque blur as expected with no foreign
colour. Latent, one level beyond only: a little white frame bleeds onto the
logo plaque's sides across its 6 px gaps to `SIDE_WINDOW` and
`GABLE_GLAZE`. That review predates the gutter; the rows it changed
(fascia rows 10-23) are inside the eave band, whose neighbours above are
its own soffit rows and below its own padding, so a mip can only blend the
gutter with white board. Not re-reviewed on mips. **Pending in the
consumer:** night/emission mips, anisotropic sampling and the consumer's
own mip generator.

### Signage and artwork

All artwork is generated by `facade_atlas.py` from numpy primitives. The sign
is set in the catalog's one stroked-centreline alphabet, `scripts/lettering.py`,
so no font file is read and the artwork carries no third party's licence.

The pharmacy mark is this asset's own device: a bold cross with a broken ring,
four short arcs sitting in the quadrants between its arms. The shop is named
once, by the generic Finnish trade word "APTEEKKI" (0.47 m capitals, 30 px
at a 5.3 px stroke, 3.3 m of ink centred on the 9.0 m left board, 2.9 m
clear each side), not by a business name. The right board carries the mark alone. Each
glyph's ink runs from its origin to its advance, so the word is centred and
spaced on its ink: the I, a lone stem, has no advance, and the doubled E and
K sit at the same 0.16 em ink gap as every other pair.

### Supersampled atlas, normal map and padding

- **Rasterised by `scripts/atlas.py` at 4 x 4 samples per pixel.** `facade_atlas.py` paints in
  final-pixel coordinates and the canvas stores the samples; they are
  box-filtered down in linear light, so an edge at a fractional position lands
  partway across its pixel and the sign board's lettering and the marks come out anti-aliased like everything else, instead of snapping to it. The emission mask
  carries the same coverage as grey at pane edges.
- **The normal map is derived from a painted height channel** in metres by
  `atlas.normal_map()`, OpenGL convention. The relief is physical, not
  exaggerated, and only covers what the mesh does not model:
  - split-face stone blocks 12 mm proud of recessed bed joints, with a rough
    face;
  - the shopfront's sections 30 mm proud of the glass, and the kick panel;
  - the soffit and fascia board joints, and the gutter's 0.06 m roll and its
    hangers;
  - the shingles' courses and tab slots, the curtain wall's frame, the door
    leaves and handles, the air handler's and louvre's blades, and the vents.
  The sign boards' printed faces are flat.
  Glass stays flat. The shingles (13 px/m) and the curtain wall (48 px/m) scale their relief
  by their px/m over 64.
- **Albedo carries no directional light.** Highlights that faked a fixed sun
  (lit top edges, sunny board or seam faces) were removed; that relief is
  height now and answers the real sun through the normal map. Shade keeps only
  tone, wear and the occlusion that holds whatever the sun does: laps, joints,
  under drips and overhangs.
- **Cavity and weathering come from shared helpers.** `atlas.cavity()` (height
  minus its Gaussian blur) deepens the ORM's AO and darkens the albedo slightly
  in joints and recesses. Tone wear, grain and rain streaks are `atlas.noise()`
  fields, white noise blurred through the FFT, so they tile exactly (the stone band's also repeat on its own 4 m vertical period); they
  replace the sums of sines, whose regular diagonal blotches showed at a
  distance.
- **The gaps are padded.** `atlas.pad()` fills every texel no region claims
  from the nearest region's own edge, in every map, height included, so a mip
  level's wider footprint at a region's edge finds more of that region rather
  than background. The padding itself keeps a flat normal.
- **The shopfront band now tiles.** The old bake painted the mullion at u = 0
  only on its right half, clipped at the sheet's edge, so the band's wrap showed
  a half-width mullion. The mullions are now placed by distance to the nearest
  light line and are whole at both edges. The stone band's gutter still carries
  its opposite end, so a sample across its wrap line finds the continuing
  courses.

### Weathering

- **Placed by `facade_atlas.py`'s `weather()`, drawn by
  `scripts/weathering.py`** at the catalog's moderate level. Its fields
  (dirt, algae, rust, faded paint, rain runs) are amounts, resolved against
  each colour's own palette, so the four variants weather alike. Dirt lerps toward a warm soil colour;
  on steel it is a neutral dust, because soil's brown turned dark roofs
  orange. Dirt roughens the ORM and strips the metallic. Height, the normal
  map and the emission mask are untouched, and glass never weathers.
- **Nothing on the stone band follows height.** The band repeats every 4 m up
  the gables, so ground splash painted on it would come back at 4 and 8 m.
  It takes only grime, faint rain runs and dust in the bed joints, and every
  weathering noise repeats on the band's period (`tile_y=4`);
  `pad_periodic()` carries the fields across its wrap with the other
  channels. The wrap was checked numerically against an in-band row.
- **Splash goes on the shopfront's kick panels instead**, whose band starts at
  the pavement.
- **Elsewhere:** the shingle roof's long runs, dirtier eave course and
  chalking toward the ridge; kicked-up dirt at the shop door's foot and hand
  grime round its pulls; the maintenance door's foot and handle; the staff
  window's bottom rail with runs down the stone below it; the curtain wall's
  sill member; runs down the air handler, louvre and vent box. The gutter
  fades with the boards and takes the neutral dust of painted steel, and the
  downpipes and the kit, which sample it, carry the same.
- **Kept clean:** the two sign boards, the plaque and the ridge sign, which
  the shop keeps, and every pane.
- The level was chosen on `rintamamiestalo_porch` (see its notes); this
  building takes the same helpers with its own layout.
- The albedo and ORM PNGs are larger on disk (5 files, 2.3 MB against 2.1 MB before), as the noise
  compresses less; resolution, count and GPU memory are unchanged.

## Glazing treatment

Measured on the finished albedo over the emission mask's neutral glazing:
**sRGB 61, linear 0.042**, and 0.25 - 0.26x the trim (validator, all four
colours) -- comfortably inside Style Direction's 45 - 70 band and well
below the trim around it. Roughness 0.08, metallic 0, from
`scripts/glazing.ROUGHNESS`.

Painted with `scripts/glazing.py`: `rooms()` is called on the finished albedo
after the id/shade/AO pass, so every pane gets its own level, a vertical
falloff and, on rather more than half of them, a lit patch of far wall. No
departure from the default band, and no baked reflection or sky gradient. The
two display windows and the gable curtain wall are all handled by it; the
glazing bars divide panes, not rooms, so a run of shopfront reads as one
interior.

The door unit is painted first, with a wider merge. It is one opening into
the shop, so its two leaves, their vision panels and the transom above them
have to be one room; the default merge bridges a glazing bar but not a pair of
0.10 m meeting stiles, and left to it the two leaves came out at different
levels with a lit wall behind one of them.

One thing worth recording for anyone extending this asset: the lit signs
are written into the emission mask in a **cool** white, not a neutral one.
Downstream the mask is read as glazing wherever it is bright and neutral, so a
neutral white board would be measured against the glazing band and dragged the
reported glass value from 60 to 82. The colour is both correct for a
fluorescent diffuser and necessary for the measurement to mean anything.

## Variant list

Four colours, all on identical geometry and UVs, differing in the albedo only.
The ORM and the emission mask are shared, since neither the roughness pattern
nor the glazing changes:

- `grey_stone` -- warm grey split-face stone (default)
- `beige_stone` -- pale sand
- `red_stone` -- muted red-brown
- `brown_stone` -- dark grey-brown

The stone changes and the roof and the white move slightly with it; the
pharmacy's signs are its identity and are the same green and the same white in
every colour. Four rather than the low-rise default of three to six: this is a
small-scale building by Color & Material Variants' test, and four covers the
range without any two reading as the same building twice.

Unique textures across all colours: seven 1024 x 1024 PNGs, as tabulated above.
Source bytes are not a VRAM figure; the consumer owns compression and mipmaps.

## Night lighting

`_emission.png` is bound as `emissiveTexture` on all four tiers with
`emissiveFactor` rewritten to `[0, 0, 0]` at export, so the asset ships lights
off and the consumer owns intensity, colour and occupancy. The texture is
retained at zero factor. Verified on reimport of all four tiers.

The mask marks:

- **glazing**, in neutral grey, each pane lit as a room (see Room-lit panes below): the two display windows, the door's transom
  and vision panels, and the two gable curtain-wall panels;
- **luminous fixtures**, in their own colours, all of them the pharmacy's
  own: the two green sign boards over the windows (`FASCIA`, the name on the
  left, the mark on the right), the plaque over the door and all four faces
  of the cube on its stand over the ridge (both `LOGO`), whose lid and the
  plaque's edges glow faintly in the field's green; the cube's steel
  underside and legs are black. No luminous region was added for the single
  shop: the plaque reuses `LOGO`, and two of the four old board regions were
  removed.
    The cube is square in plan so its four faces can share one atlas region;
    `check_layout()` fails the build if its depth stops matching its width, or
    if it grows past the roof it stands on.  The mark is symmetric about its
    upright, so the two faces mapped along y need no mirroring to read the
    right way round. Their fields, their printed ink
  and their white are written separately, because a lit box is a bright
  diffuser with graphics printed on it and print transmits far less light than
  the blank panel does -- the ink emits roughly twenty times less than the
  field it sits on, which is what keeps the wordmark legible after dark
  instead of glowing as hard as the board.

Frames, stone, roof, soffit, doors' solid panels and the plant are black.

Reference lit factor for previews: linear `(1.0, 0.88, 0.72)`. A shop interior
is fluorescent, not a living-room bulb, so this type states its own factor
rather than taking the catalog's warmer default.

**Control granularity.** Per placed building, not per window. Every shopfront
bay and both gable panels reuse the same atlas regions, so their UVs are
shared, and the signs share the glazing's one emissive factor: the consumer
cannot light the signs and leave the shop dark without splitting the
material. For one shop that is the expected granularity.

`variants.png` shows all four colours at `LOD0`, a labelled day row with
emission off above a night row at factor 1.0, camera, framing, exposure and
colour management fixed between rows. Night row lighting: world `(0.24, 0.32,
0.50)` at strength 0.08, sun 0.12 at `(0.48, 0.62, 1.0)`, Cycles, 48 samples,
seed 42. **No light spill was simulated** -- the ground under the windows is
lit by the world, not by the building. Visible glow is an emissive surface;
illumination of the ground and of anything standing near it depends on the
consumer's lighting or GI, or on separately placed lights.

**Pending:** off/on behaviour has been checked on reimported tiers at `LOD0`
only (and in the single-shop review's night renders, `LOD0` at 25 m). Oblique and distant filtering of the mask, and its behaviour across the
`LOD` switches, have not been reviewed; a `LOD0` sheet cannot validate those.

### Room-lit panes

Each pane in the emission mask is the lit room behind it, not a flat panel:
`scripts/glazing.py`'s `night_rooms()` multiplies it by its own level, a soft
lamp glow and a falloff toward the floor, and never takes it below about a
fifth. The mask stays neutral grey, so colour, intensity and which buildings
are lit are still the consumer's, and nothing in it says whether a room is
occupied. Averaged over the glass it is 52 % of the old full-white mask
(the catalog runs 52-63 %), so at the same reference factor the windows read
as lamplight rather than pale panels. A pane much wider than it is tall -- the
shopfront band, the curtain wall, whose thin mullions the merge bridges -- gets
one lamp per bay, so the sales floors read evenly lit rather than as one glow
fading out along the whole frontage. Every window of one type samples the same atlas region, so every
window of that type carries the same room, and the shopfront repeats its
room from bay to bay.

## Export

`bpy.ops.export_scene.gltf` with `export_format='GLB'`,
`use_selection=True`, `export_yup=True`, `export_apply=True`,
`export_keep_originals=True`, `export_cameras=False`, `export_lights=False`.
`build.py` asserts those keywords exist before it runs, so a renamed exporter
flag reports itself rather than failing as a distant `TypeError`.

Keeping original textures makes the exporter write each image with both a
`uri` and a 1x1 placeholder `bufferView`. glTF allows one source per image and
Godot drops images that carry both, so `scripts/glb_images.py`'s `strip_embedded_images()` strips the
`bufferView` and leaves the external reference. Verified: all four tiers carry
`uri` only.

**Material.** One slot on every tier. Base colour from the albedo, roughness
from the ORM's green and metallic from its blue through a Separate Color node,
and the ORM's red into a `glTF Material Output` group's Occlusion input, which
is what makes the exporter write an `occlusionTexture`. Albedo and emission are
sRGB; the ORM is Non-Color. Textures are linked relatively from `export/`, never
packed.

### Reproducing

From the repository root:

```bash
python3 buildings/commercial/liikekeskus_pharmacy/facade_atlas.py export   # the seven textures first
blender --background buildings/commercial/liikekeskus_pharmacy/source.blend \
    --python buildings/commercial/liikekeskus_pharmacy/build.py           # geometry, export, previews, sidecar
```

`facade_atlas.py` owns every number the mesh and the atlas share, and
`build.py` imports it rather than repeating them, so a change to a bay
position or a band row cannot leave the UVs pointing at the wrong artwork.
`build.check_layout()` runs before any geometry and fails on a gap in the
front's bays, an entrance off the front's centre or too wide for the middle
pier, a plaque off the pier, a leaf outside the 2.0 - 2.4 m band, a
gable panel whose head is through the roof or across the band's wrap line, and
on any region whose pixel size does not match the metres it is stretched over.

The material, the export and the previews are `scripts/asset_build.py`'s,
shared by every asset: `build.py` keeps this building's massing, UVs and
layout checks and hands the rest to one `asset_build.Asset`. The material binds
`_normal.png` through a tangent-space Normal Map node at strength 1, so every
tier carries `normalTexture` at scale 1 beside the base colour, ORM, occlusion
and emission bindings. No tangents are exported; a glTF consumer generates
MikkTSpace tangents when none are given, as Blender's importer does. The export
still writes every tier lit and rewrites its emission factor to zero, and
strips the placeholder `bufferView` keep-originals leaves.

### Facts sidecar

`export/liikekeskus_pharmacy.model.json`, schema version 1, glTF frame
(metres, +Y up, +Z street front, origin at the pivot): bounds
`[-12.99, 0, -9.24]` - `[12.99, 11.925, 9.24]`, the -X side set by the wall
ladder; footprint the 24 x 16 m wall ring, `[-11.91, -8]` - `[12.09, 8]`,
since the pivot is 0.09 m left of the ring's centre; one storey, floor at 0,
384 m2; 0 dwellings; hero false. Two doors: `pharmacy`, kind `entrance`,
main, at `[0.09, 0, 8]` facing `+Z`, 2.0 x 2.25 m, on the front's centre
line; `maintenance`, kind `service`, at `[1.09, 0, -8]` facing `-Z`,
1.0 x 2.25 m. No other door.

## Review status

Checked here, in Blender:

- Adjacent tiers and each tier against `LOD0` at 35, 70 and 120 m, front and
  oblique, with identical camera, framing, lighting and variant.
- `scripts/validate_asset.py` over `export/`; its sampled hidden-surface
  finding is recorded under Interior geometry.
- Glazing measured against Style Direction's band on the finished albedo.
- `uri`-only images, the single material slot and the `emissiveTexture`
  binding at zero factor, on reimport of all four tiers.
- The day/night sheet across all four colours at `LOD0`.
- The texture pipeline change, before against after with
  `scripts/review_compare.py`: `LOD0` front and oblique at 20 m and 35 m under
  noon, morning and backlight; mip4 stress renders of `LOD2` at 75 m and
  `LOD3` grazing at 125 m; and the catalog preview. Laps, seams and
  mouldings read as raised in direct sun, which confirms the OpenGL green
  channel, and no new colour leaks appear at mip4.
  These mip4 renders were made after fixing `scripts/review_asset.py`: Blender
  5.2's glTF importer packs images, and a packed image ignores `--texture-dir`,
  so every earlier stress render had shown the full-resolution textures.
- The weathering, before against after with `scripts/review_compare.py`:
  `LOD0` oblique and aerial at 20 m and 35 m under noon and morning sun. The
  changes land where `weather()` puts them, and no seam or wrap line shows.
  The stone band's wrap row was checked numerically against an in-band row,
  before and after, and steps no more than they do.
  `scripts/validate_asset.py` still reports no failures or warnings. The
  rebuilt GLBs are byte-identical to the previous ones.
- The ridge crest and the sign's stand, before against after with
  `scripts/review_asset.py`: all four tiers, front, oblique and aerial at 30,
  60, 100 and 150 m under noon sun. The bounds grew, so the renders differ in
  size and were paired by hand rather than with `review_compare.py`. The
  crest holds as a white line along the ridge on every tier, `LOD3` at 150 m
  included; the end cap reads as a cap on the apex, and the legs as short
  feet. A first pass with 0.6 m of clear height read as spikes and was
  shortened to 0.25 m. `scripts/validate_asset.py` reports no failures or
  warnings.

- The single-shop redesign, before against after with
  `scripts/review_asset.py` and `scripts/review_compare.py` (identical
  settings and bounds): the six orthographic/aerial views; `LOD0` front and
  oblique at 15 and 25 m; the tier pairs at 30/40, 65/75 and 115/125 m; the
  night state at 25 m; and every colour by day and by night at 25 m through
  `--texture-dir`. The front reads as one pharmacy with one door; no trace of
  the old salon and barber boards, doors or party piers is left by day or
  by night, in any colour. `scripts/validate_asset.py` reports no failures;
  its one warning is the sidecar's dirty source, pending a rewrite from the
  committed tree.

- The mip review of the single-shop atlas (Texture set): every tier at its
  switch distance and one level beyond, whole-atlas and distance-matched
  per-texel mips, under noon and reverse sun. No gutter leak at any tier's
  real distance; a latent white bleed onto the plaque's sides one level
  beyond only.

- The Finnish sign word, before against after with
  `scripts/review_asset.py` and `scripts/review_compare.py` (identical
  settings): `LOD0` and `LOD1` front and oblique at 20, 35 and 70 m, noon
  and night (lit), and `LOD1` front, oblique and grazing at 70 m on the
  whole-atlas mip 3. Only the lettering differs; the rebaked PNGs differ from
  the old ones inside the left board alone, and the GLBs are byte-identical.
  The word reads at 35 m and still at 70 m on the full-resolution atlas; on
  mip 3 it blurs to a light strip on the green, as the old word did, with no
  leak. The word's ink, measured on the emission mask in the shared
  lettering: 210 px, 183 px clear each side.

- The gutters, downpipes and roof safety kit (2026-11-22), before against
  after with identical settings: the tier pairs at the consumer's switches
  (47 / 104 / 208 m, 75 degree FOV; before at 46 / 103 / 206 m, the bounds
  having grown) as before-above-after pair sheets; `LOD0` front, oblique and
  rear at 20 and 35 m through `scripts/review_compare.py`; `review_asset.py
  --six-views` of all four tiers; the asset's working views
  (`render_views`, with close views of the wall ladder, the ridge and a
  downpipe) after each of three build passes, which moved the housing
  ladder's top to the crest, thinned the kit's `LOD1` and `LOD2`, and kept
  the housings and the kit's rails on `LOD3`. The rebaked PNGs differ from
  the old ones in the eave band's rows only. `scripts/validate_asset.py`:
  0 FAIL; its one warning is the sidecar's dirty source, pending a rewrite
  from the committed tree. The gutter's rows were not reviewed on mips.

Pending, and outside this repository:

- Anisotropic appearance, the emission mask's mips at night, the
  consumer's own mip generator and any explicit consumer filtering
  arrangement.
- Emission off/on across the LOD switches and at oblique or distant views.
- Consumer import, LOD selection and performance measurement in a
  representative scene.

## Tooling versions

Blender **5.3.0** (hash `02f0899d78e3`, built 2026-11-11), at the 5.3 floor
`scripts/asset_build.py` asserts for every `build.py`. numpy and Pillow for the
bake.

The Blender MCP addon was available in this session but was **not** used to
build this asset: the geometry, the export and every review render were run
headless, `blender --background --python build.py` and
`blender -b -P scripts/review_asset.py`, so no addon version applies to the
result. Recorded as a known-good diagnostic, not a pin: nobody has to match it.

`source.blend` was saved by 5.3.0, the catalog floor: Blender opens older
files, not newer ones. The `.glb` and PNG exports are unaffected.

- **CPython 3.14.7 with numpy 2.5.3, scipy 1.18.1 and Pillow 12.3.0** for the
  texture export.

## Revision log

- **2026-11-23 — far kit wound outward.** `scripts/roof_safety.py` built
  the mirrored bare rails with one winding and a walkway plank in the
  eave's left-handed axes, so on `LOD3` one rail of each of the three
  ladders and the ridge plank were inside out; they are turned outward at
  the source. Same triangles and vertices; `LOD3`'s hidden-surface
  candidates 41 -> 9.
- **2026-11-22 — gutters, downpipes and the roof safety kit (audit fix).**
  A half-round gutter is painted across the top of each eave fascia; the
  rake boards and the ridge crest's sides now take the fascia rows under it
  and the crest's top the far soffit rows (Texture set). Four downpipes
  (`scripts/downpipes.py`) and the roof safety kit (`scripts/roof_safety.py`:
  wall ladder, roof ladder, ridge walkway, housing walkway, housing ladder)
  went in (Construction). The side windows, back door and louvres are cut
  through `LOD1` again, and the ventilation housings stay on `LOD3`.
  Triangles 4,002 / 1,972 / 796 / 484 (were 1,024 / 898 / 428 / 328). The
  wall ladder stands 0.18 m outside the left eave, so the bounds grew from
  25.8 to 25.98 m across and the pivot moved 0.09 m toward -X: in the
  sidecar the bounds are `[-12.99, 0, -9.24]` - `[12.99, 11.925, 9.24]`
  (were +-12.9 in x), the footprint's x runs -11.91 .. 12.09 (was +-12.0),
  the entrance is at `[0.09, 0, 8]` (was `[0, 0, 8]`) and the maintenance
  door at `[1.09, 0, -8]` (was `[1, 0, -8]`). The albedos, ORM and normal
  map changed in the eave band's rows only; the emission mask is unchanged.
  Every GLB, `source.blend`, `preview.png`, `variants.png` and the sidecar
  changed. Notes: the stale "no normal map" statement corrected, the
  consumer's switch distances added to the LOD review.

- **2026-11-22 — shared lettering.** The sign is set in
  `scripts/lettering.py`, the catalog's one alphabet, instead of this
  file's own glyphs: E 0.56 → 0.60 em wide, T 0.62 → 0.68, and K the
  two-stroke form (arm and leg meeting on the stem) instead of the leg
  leaving the arm, so the word's ink is 210 px instead of 206, still
  centred.
  The albedos, ORM and emission changed inside the left board only; the
  normal map and the GLBs are byte-identical. Before/after renders at 20 and
  35 m, noon and night, in
  `review/atlas_refactor_2026_11_22/renders/liikekeskus_pharmacy/compare/`.

- **2026-11-22 — sign in Finnish.** The left board reads "APTEEKKI" instead
  of "PHARMACY", in the same letterforms, cap height and weight, centred on
  the same board (Signage and artwork). The glyph table gained E, I, K and T
  and lost C, H, M, R and Y. Geometry, UVs, the mark, the colours and the
  board are unchanged; triangles 1,024 / 898 / 428 / 328 as before. The
  albedos, ORM and emission changed inside the board only; the normal map
  did not. The GLBs were re-exported byte-identical; `source.blend`,
  `preview.png` and `variants.png` were rewritten, and the sidecar changed
  only in its texture and preview hashes and its source record.

- **2026-11-21 — mip review.** The review at the switch distances recorded
  (Texture set, Review status); no asset change.

- **2026-11-21 — one shop, one door.** The three-unit front (a pharmacy
  between a beauty salon and a barber, three customer doors, four sign boards)
  became one pharmacy: two 9 m display windows either side of the middle
  pier, the party piers gone and the corner piers 1.6 m instead of 1.4 m; one
  door, a glazed pair under a transom, through a portal in the foot of the
  middle pier on the front's centre line, with a lit plaque carrying the mark
  above it; two green boards naming the shop once and carrying the mark once.
  The salon's and barber's doors, boards, lettering and glyphs are gone, and
  so is the single-door atlas region. Bounds, pivot, storeys, the rear
  service door, the roof, the ridge sign and the four colours are unchanged.
  Triangles 1,024 / 898 / 428 / 328 (were 1,018 / 894 / 428 / 348). Every
  PNG, the GLBs, the sidecar (one entrance, main, at the centre),
  `source.blend` (now saved by 5.3.0), `preview.png` and `variants.png`
  changed.

- **2026-09-25 — ridge crest and sign stand.** A white crest now caps the
  ridge from rake to rake, and the sign stands on it on four steel legs, 0.25 m
  clear, instead of straddling the bare ridge with its foot in the slab
  (Construction). The cube is 1.6 m tall rather than 2.0 m, since none of it
  is buried now, and `LOGO` shrank to match. 110 more triangles on every
  tier; the building is 11.9 m tall rather than 11.4 m. Every albedo, the
  ORM, the emission mask, the GLBs, `source.blend`, `preview.png` and
  `variants.png` changed; the normal map did not.

- **2026-09-25 — weathering.** `facade_atlas.py` gained `weather()`, which
  places the shared `scripts/weathering.py` fields: dirt, algae, rust, faded
  paint and rain runs (Texture set, Weathering). Every albedo and the ORM
  changed; the normal map and the emission mask did not. `source.blend`,
  `preview.png` and `variants.png` were regenerated, and the GLBs rebuilt
  byte-identical.

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
