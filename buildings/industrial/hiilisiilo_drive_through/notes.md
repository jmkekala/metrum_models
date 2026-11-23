# hiilisiilo_drive_through

## Style brief

A composite screening and truck-loading plant for a small mid-century Nordic
coal mine, where the coal leaves by road. A raised storage bunker stands on
concrete legs, and trucks drive through underneath it to be loaded from
chutes.

- **Bunker house:** 12.0 × 8.0 m. Its long sides face the front and the
  rear. It stands on a concrete leg on the west and on the control and stair
  room on the east.
- **Truck lane:** one lane runs straight through under the bunker, from the
  front long side to the rear one. It is open at both ends, with no door
  leaf. Three steel loading hoppers hang from its ceiling.
- **Screen house:** above the lane is a concrete ring beam, the bunker's
  girder. On it stands the screen house: a concrete frame with profiled
  sheet infill under a low 1:10 mono-pitch sheet roof that falls to the
  rear. It has one row of small steel-framed windows at the screen floor.
- **Conveyor:** on the east side, the side the catalog view sees, a 2.0 ×
  2.0 m enclosed conveyor gallery rises at 30° from a low concrete intake
  hopper house into the screen house's east wall, carried at mid-span on a
  steel trestle. It is the second half of the silhouette, and what makes
  the bunker read as a coal loading plant rather than a box on legs.

Materials are muted and coal-dusty, as a working plant's are: board-formed
concrete blackened at its foot by the coal the trucks throw up, a dusty lane
and dust-caked hoppers, a coal-caked gallery underside and intake roof,
moderately dirty cladding above; grey (or red-oxide) painted profiled sheet; a dark grey
roof; dark steel hoppers and doors; and the catalog's galvanised rainwater
steel for the rear gutter, the downpipes and the snow guard. The model shows
no recognisable real structure.

## Category and secondary use

`buildings/industrial/`. Its secondary use is the ground-level control and
stair room, the operators' access, which is part of the same plant.

## Hero/landmark status

**No.** It uses the ordinary budgets and a 1024 atlas.

## Footprint

| | Width (X) × depth (Y) × height |
| --- | --- |
| Bunker house walls (lane inside) | 12.00 × 8.00 m |
| Intake house walls | 3.20 × 3.00 m, 4.20 m to its slab top |
| Overall bounds (roof overhangs, gallery, intake) | 20.65 × 8.70 × 13.08 m |

In the build frame the house spans x −6.0…6.0 and y −4.0…4.0. The other
parts sit as follows:

- **The lane** runs from y −4.0 to 4.0 between its side walls at x −4.40 and
  0.60.
- **The west leg** is x −6.00 to −4.40. The control and stair room is x 0.60
  to 6.00.
- **The gallery** is y 0.80 to 2.80, in the east wall's rear half. Its axis
  runs along X: it leaves the east wall at x 6.0 and ends inside the intake.
- **The intake house** is x 11.00 to 14.20 and y 0.30 to 3.30, with its slab
  overhanging 0.15 m.
- **The trestle** stands at mid-span, its bent in the plane x 8.50: legs at
  y 0.66 and 2.94, footings x 8.20 to 8.80 and y 0.36 to 3.24. In the glTF
  frame its centre plane is x 4.475 and its legs are at z −0.61 and −2.89.
- Everything east of the house stands well clear of the lane's east wall
  (x 0.60): the gallery from x 6.0, 5.4 m off; the trestle's footings from
  x 8.20, 7.6 m off; the intake's slab from x 10.85. The lane and both of its
  approaches are a clear, straight corridor x −4.40…0.60 for any y.

The roof slab overhangs 0.30 m at the front and rakes and 0.40 m at the
rear. The pivot is at ground level, centred on the bounding box: build point
(4.025, 0.05, 0). It is taken from `LOD0` and applied to every tier, and every
tier has the same extents.

The facts sidecar's footprint is a single simple polygon. It is the house
rectangle, the intake rectangle, and between them the 2.0 m strip under the
gallery, which joins the two.

These stand outside that polygon but inside the bounds:

- the roof slab's overhangs;
- the two downpipes on the rear wall, under the rear eave;
- the intake slab's 0.15 m overhang;
- the trestle's legs and footings, which are not walls. Its legs stand
  0.04 m outside the gallery's strip on each side.

## Story height

**One occupied storey on the ground: the control and stair room, plus the
intake house.**

- The control room is a block 5.20 m to the deck, with no modelled
  interior.
- The lane is open, at 5.20 m clear to its ceiling.
- The bunker and screen house above it are plant, not storeys. The bunker's
  bins occupy the ring beam's zone up to the notional screen floor at 7.40
  m, which is the gallery's floor where it meets the wall. The screen floor
  rises to the roof, 12.0–12.8 m.

None of these levels is a habitable storey, so the 3.0–3.3 m band does not
apply.

## Door leaf height

- **Control room door (main entrance): 0.95 × 2.10 m** steel leaf, with no
  transom. Its steel frame adds 0.08 m above it. The threshold is at ground
  level, on the front wall at x 1.90; its reveal's 0.02 m floor slab
  (Construction) is a floor finish, not a step.
- **Intake door (vehicle): 2.40 × 2.60 m** steel sliding door, under a 0.12
  m track hood, centred on the intake's front face, so the tipping vehicles
  reach it from the front yard, 10 m east of the lane's approach. It is a
  vehicle door, so the leaf band does not apply; the 2.10 m door carries the
  human scale. Its threshold is at ground level too, and its reveal's
  0.02 m floor slab (Construction) is likewise a floor finish, not a step.
- The lane's two mouths have no door leaf and are not doors.

## Window sills

- **Control room:** two windows of 1.20 × 0.90 m, one on the front and one
  on the east face. Sill 1.10 m, head 2.00 m, level with the door's head
  (2.10 m) less its frame.
- **Screen house:** five windows of the same size, sill 8.70 m and head 9.60
  m. That is 1.30 m above the 7.40 m screen floor, a working sill for the
  operators on that floor. There are two on the front, one at the rear over
  the lane, and one in each end wall. The east one is at y −1.0, over the
  control room's east window and clear of the gallery's mouth. All of them sit in the 8.40–10.40 m
  cladding strip, clear of its joints and the frame's columns
  (`check_layout()`).

## Eave overhang

**0.30 m at the front (high) eave and the rakes, 0.40 m at the rear (low)
eave**, where the gutter is. This is within the 0.3–0.6 m default. The slab
is 0.25 m thick.

- **Front and rakes:** a steel fascia flashing in the roof's trim colour.
- **Rear:** a painted half-round galvanised gutter across the fascia's top.
- **Underside:** bare sheet.

The intake house has a flat concrete slab with a 0.15 m overhang and no
gutter: it drains off its edge.

## Construction

`build.py` builds closed solids and unions them with Blender's Exact
boolean (`asset_build.union`):

- the bunker house;
- the roof slab;
- the gallery;
- the intake house's walls and its roof slab;
- the trestle: its legs, cross-head, bracing and footings (one solid at
  `LOD3`);
- three hoppers;
- two downpipes.

### The lane as a tunnel through the one shell

The bunker house is a single hand-built closed solid of genus one: a box
with the lane as a tunnel through it.

- The front and rear walls' concrete regions are U-shaped round the lane's
  mouths.
- The lane's two side walls and its ceiling are ordinary outside surface.
- The lane has no floor face. The ground is its floor, so the shell's bottom
  is two floor caps, under the west leg and the control room, and nothing
  lies between them. No coplanar floor is left. The lane is a passage,
  not a door, and has no floor slab; both doors stand on one (Door floor
  slabs below).

**Lane, stated for the consumer:**

- it runs along Y, front to rear;
- it is 5.00 m clear between its walls;
- it is 5.20 m clear to its ceiling, and 4.60 m under the hoppers' mouths;
- trucks enter from the front (−Y) and leave at the rear.

The facts sidecar states it as its one passage (Export).

### Door floor slabs

Both doors stand on the ground in reveals (0.12 m and 0.15 m) that had no
upward face under them (the floor cap faces down), so a consumer's terrain
showed inside, across each door's foot. Each reveal is floored with a
concrete slab from the shared `scripts/door_floor.py` (`build_item()` calls
`door_floor.recess()`; on `LOD1` the wall's notch is `door_floor.notch()`):

| Door | Sidecar door | Slab, width x depth | Tiers |
| --- | --- | --- | --- |
| the control room's door | `control` | 0.95 x 0.12 m (`LOD0`), 1.11 x 0.12 m (`LOD1`) | `LOD0`, `LOD1` |
| the intake's vehicle door | `intake` | 2.40 x 0.15 m (`LOD0`), 2.60 x 0.15 m (`LOD1`) | `LOD0`, `LOD1` |

- **Top 0.02 m over the ground** (`door_floor.T`), clear of terrain at
  z = 0 and too low to read as a step.
- **A nosing on the wall plane** across the recessed opening. Nothing
  projects past the wall, so the bounds, the pivot, the footprint and the
  door's threshold in the sidecar are as they were.
- **The reveal starts on the slab's top:** the cheeks and the leaf begin at
  z 0.02, and the faces beside the nosing carry its top corners, so wall,
  casing, nosing, slab and cheeks meet on shared vertices. Under the nosing
  the floor cap runs straight along the wall line instead of round the
  reveal. The doors' artwork keeps its place, so each slab covers the
  bottom 1.3 px of its leaf (the control door's kick plate, the intake
  door's bottom rail).
- **Follows the opening's tier modes** (`item_mode()`). On `LOD0` the
  casing is a ring of faces on the wall plane and the recess is the leaf's
  (0.95 m, 2.40 m): the slab spans the leaf, and the casing's two legs
  carry the nosing's top corner on their inner edges (the wall's notch is
  unchanged). On `LOD1` the recess is the whole casing (1.11 m, 2.60 m),
  and the slab spans it, the wall's notch taking the nosing's corners. Each
  door's two slabs sample one casing-wide region, `LOD0`'s its middle
  (`door_floor.recess(u0=)`). `LOD2` and `LOD3` paint the doors flat on the
  wall, with no reveal to floor.
- **Its own atlas region** per door (Texture set).

`FLOORED` names each door's slab by wall and kind, and `floor_for()` gives
it on every tier that recesses the door; `check_layout()` fails any door at
grade without one. The lane's mouths are a passage, not doors, and the
ground is the lane's floor: it gets no slab, and the drive-through lane's
width, clear height and plan are as they were.

### Hoppers

Three steel hoppers hang on the lane's centre line, at y −2.5, 0 and 2.5.
Each is a frustum 1.50 × 1.20 m at its top, buried 0.12 m in the ceiling,
tapering to 0.60 × 0.45 m at its mouth at 4.60 m. A truck stops with its
body under them, centred on the middle hopper.

### Walls and the concrete frame

- Every wall carries a concrete region from the ground to 6.40 m (S1). That
  covers the plinth, the board-formed legs and walls, the deck joint at
  5.20 m and the ring beam.
- Above it are 2.00 m cladding strips cut at 8.40, 10.40 and 12.40 m and
  clipped to the sloping wall top. Each strip is split by the concrete
  frame's 0.40 m columns: at the four corners, and on the front and rear
  over the lane's side walls, so the legs read as running up through the
  house.
- Region outlines carry every neighbour's breakpoint, so walls and strips
  meet without T-junctions. `close_solid()` caps the three rims: two floors
  and the lid.

### Gallery and intake

The gallery is one closed box whose axis runs along X and falls at 30°,
east of the house on the side the catalog camera sees.

- **Upper end:** buried 0.50 m inside the screen house, through the east
  wall's rear half (y 0.80–2.80). Its floor is at 7.40 m and its top at 9.71
  m where it passes the east wall: in the cladding, 1.0 m clear of the
  ring beam's top and 2.4 m under the roof. The union cuts the wall round it
  and removes the buried end, so the join is one closed shell with no
  partition inside.
- **Lower end:** inside the intake house. Its floor crosses the intake's
  slab top (4.20 m) at x 11.54, 0.69 m inside the slab's edge.
- **Visible end:** the lower end's top 1.18 m stands out of the intake roof
  as the conveyor's tail housing.
- **Span:** 5.0 m clear between the house's east wall and the intake's west
  wall, carried at its middle by the trestle, so it spans 2.4 m either side.

The intake's walls run 0.12 m up into their slab. Nothing in the union is
coplanar.

### Trestle

One steel bent stands under the gallery at mid-span, in the plane x 8.50
(`TR_X`, half-way between the house's east wall and the intake's west
wall). Its members are closed solids; nothing is a lattice or needs alpha.

- **Legs:** two 0.20 × 0.20 m H-sections, centred at y 0.66 and 2.94, just
  outside the gallery's sides. Their flanges are square to X (a flat face
  to the east and west), the channels facing each other across the bent.
- **Footings:** a 0.60 × 0.60 m concrete pad under each leg, 0.20 m high.
  The legs stand 0.05 m down into them.
- **Cross-head:** an H-section along Y from y 0.54 to 3.06, across both legs
  and the gallery's whole width. Its 0.22 m flanges run along X; its bottom
  is level at 5.61 m; its top flange follows the gallery's 30° floor, 0.012
  m up into it, so 0.018 m of that flange shows under the floor and it
  stands 0.012 m proud beside the gallery, a bearing seat. It is 0.30 m
  deep at its east edge. The legs stop half-way up its bottom flange.
- **Bracing:** an X of two 0.07 m square bars between the legs, from 0.70 m
  at one leg to 5.41 m at the other. Each bar ends cut along the plane of a
  leg's web, inside it, and the two pass 0.01 m apart, one each side of the
  bent's centre plane, so neither touches the other.
- **Paint:** dark painted steel, coal-caked at its feet (Texture set).
- **Tiers:** `LOD0`, `LOD1` and `LOD2` build all of it. `LOD3` builds the
  legs and head as one plain solid, an upturned U of the legs' 0.20 m width
  standing on the ground, with no footings, and drops the X (LOD review).
  `LOD2` built the same plain solid until 2026-11-22; its sunlit flat legs
  read grey where `LOD1`'s shaded H channels read black, and its feet lost
  the footings' dark blocks, a visible change at the 83 m switch.

The trestle stays inside the `LOD0` bounds, so the pivot, the doors, the
footprint and the passage are unchanged by it.

### Roof, rainwater goods and snow guard

The roof is a mono-pitch at 1:10 (5.7°), falling to the rear. The underside
is at 12.80 m at the front wall line and 12.00 m at the rear. The walls run
0.12 m up into the slab. Its top is cut across every 2.00 m up the slope
from the low edge (at 2, 4, 6 and 8 m), as the walls are at their strip
joints, so each strip maps the repeating ROOF band (Texture set); the rake
edges carry the cuts. The gallery's top is cut the same way from its lower
end. `LOD3` leaves both uncut (Texture set).

- **Gutter:** painted on the rear fascia (Texture set).
- **Downpipes:** modelled with `scripts/downpipes.py` on the rear wall, at
  s 0.25 and 11.75 (x 5.75 and −5.75). The first is on the control room's
  back wall, the second on the west leg's.
  Both use the module's default swan-neck into the 0.40 m soffit and its
  shoe. The lane's mouth fills the middle of the rear wall.
- **Snow guard:** painted on the roof's lowest 0.40 m, which maps onto the
  rear eave band, as on `konehalli_open_bays`.
- **No roof safety kit:** the roof is not steeper than 1:8, and nothing on it
  is serviced.

### Authored parameters

`facade_atlas.py` holds every shared number, including:

- the plan (`HX`, `HY`) and the lane (`XL0`, `XL1`, `Z_DECK`);
- `Z_CLAD`, `JOINTS` and `COL_W`;
- the eave heights and overhangs;
- the hoppers, the gallery (`GAL_Y` across, `GAL_X` along, `Z_SCREEN`,
  30°) and the intake (`INT_X`, `INT_Y`), derived from the gallery;
- the trestle (`TR_X`, `TR_LEG_Y`, the sections, `TR_BURY`, `TR_PAD`),
  derived from the gallery and the intake;
- the openings.

`build.py` adds the wall specs. `check_layout()` asserts the following:

- openings clear joints, columns, the roof and the lane's mouths;
- the lane is at least 4.5 m wide and at least 4.5 m clear under the
  hoppers;
- the gallery is buried at both ends, crosses the intake roof inside the
  slab, and its mouth in the east wall clears the corner columns and the
  east windows by 0.3 m;
- the gallery and the intake stand east of the house, 1.5 m or more clear of
  the lane's line, so neither reaches the lane or its approaches;
- the trestle's footings are 1.5 m or more clear of the lane's line too, in
  the open between the house and the intake's slab, 1.0 m or more clear of
  the intake door's approach; its legs stand outside the gallery's sides,
  its cross-head spans them and the gallery, its top flange sits just under
  the floor, the bracing fits between its feet, its head and the legs'
  flanges, and its UVs stay inside their region;
- the downpipes clear the lane's mouth (`downpipes.problems()`);
- every door at grade has a floor slab, and `door_floor.problems()` finds
  each slab's region the casing's width and the reveal's depth, under a
  door at grade, and the atlas's unique regions, the slabs' among them,
  clear of one another (`atlas.region_problems()`);
- the cladding's U stays inside its band;
- the roof band is one 2.00 m repeat at 64 px/m, and the eave strip ends
  inside its first repeat;
- the roof is no steeper than 1:8.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What changes |
| --- | --- | --- | --- |
| `LOD0` | 1,062 | 12,000 | openings with a frame ring and a 0.12/0.15 m recess; three hoppers; eight-sided downpipes with swan-necks and shoes; the full trestle; roof and gallery top cut every 2 m |
| `LOD1` | 910 | 4,000 | each opening one recess the size of its frame; downpipes four-sided, bent; the full trestle |
| `LOD2` | 718 | 1,500 | openings flush; coplanar boolean subdivisions dissolved (UV seams kept); downpipes straight, four-sided; the full trestle |
| `LOD3` | 486 | 500 | downpipes three-sided; the trestle one U-shaped solid without its X; roof and gallery top uncut; the lane, hoppers, gallery and intake kept |

The counts are not padded. The massing is three boxes, a tunnel, a gallery
and its trestle. The walls are polygons with holes, and everything shallow
is texture. That covers the ribs, board marks, the frame's columns, the ring
beam, the window bars and the wheel guard.

Where the triangles go at `LOD0`:

- the lane's walls and ceiling and the U-shaped mouths: about 40;
- the three hoppers, with their holes in the ceiling: 52;
- the trestle: 240, with its cut in the gallery's floor. The two H-section
  legs and the H-section cross-head take most of it, each 12-sided, with
  the legs' joints into the head and the footings; the bracing bars and
  footings take the rest;
- the roof's and the gallery top's 2 m cuts for the repeating roof band:
  32 on `LOD0`–`LOD2` (eight more top triangles and their breakpoints on
  the rakes and the gallery's sides);
- the downpipes and the gallery's cuts make up most of the rest;
- the doors' floor slabs: 4 each, a nosing and a top, on `LOD0` and
  `LOD1`. The casing's legs (`LOD0`) and the wall's notch (`LOD1`) take
  the nosing's corners and the floor cap loses the reveal's detour, which
  balance: each slab put its tier 4 over its count before it (1,054 / 902
  with neither, 1,062 / 910 with both), and `LOD2` and `LOD3` are
  unchanged.

The trestle costs 240 at `LOD0`, `LOD1` and `LOD2`. At `LOD3` its legs and
head are one solid, 48, without the bracing. Built there as three boxes,
the leg tops' holes in the head cost 64, which took `LOD3` to 502, over its
ceiling; the 2 m roof cuts, 32 more, are why `LOD3` maps its roof uncut.

`LOD3` keeps the hoppers and a trestle (LOD review). It stays 14 under the
ceiling, 232 under `LOD2`: the trestle's H-sections, footings and X, the
roof cuts and the downpipes' fourth sides. The gallery's mouth shares the
east wall's cladding strips with the screen house window, so the wall's
triangulation round both is a little denser than a bare wall's.

## LOD review

**Switches: about 37 / 83 / 165 m**, the consumer's screen-size measure:
1.8, 4 and 8 times the largest bounds dimension (20.65 m, the width), with
a 75° vertical FOV at 1920×1080. Reviewed there on the exported tiers, each
pair at the same camera, distance to the centre of `LOD0`'s bounds: front
(10° up), corner (45° round, 25° up) and eye level (30° round, camera at
1.7 m) at noon, and the corner at night with the reference emission
(`review/older_audit_2026_11_22/fix_industrial_a2/hiilisiilo_drive_through/`,
`renders_before/` and `renders_after/`, before-above-after pair sheets in
`compare/`). Pixels changing by more than 24 at each switch, front / corner
/ eye / night: `LOD0`→`LOD1` 485 / 387 / 760 / 207 (the opening rings
becoming recesses; 434 / 307 / 717 / 220 before the 2026-11-22 fixes, the
dielectric frames now a little brighter in sun); `LOD1`→`LOD2`
92 / 94 / 154 / 205 (72 / 83 / 229 / 209 before: the eye view's 229 was
`LOD2`'s plain trestle legs turning grey and losing their footings; what
remains is the openings going flush, thin light frames round each window
and door, a little brighter now the frames are dielectric, and the lit
windows' outlines at night); `LOD2`→`LOD3` 0 / 0 / 24 / 0 (the
trestle's H-sections, footings and X becoming the plain U, under a pixel
wide at 165 m). `LOD3` reads the same as `LOD2` at 165 m in every view:
it keeps everything with an outline at that size, and the 232 triangles
it saves are what is under a pixel there (trestle detail, the roof's
2 m cuts, the downpipes' fourth sides).

Earlier authoring passes used `scripts/review_asset.py`: perspective,
1920×1080, 50° vertical FOV, distance measured along the view to the front
or rear bounding face, Cycles CPU, 16–20 samples with denoising, AgX,
exposure 0. Pairs compared there:

- `LOD0`/`LOD1` at 30/40 m, front and oblique, noon;
- `LOD1`/`LOD2` at 65/75 m, front, oblique and rear, noon and reverse sun;
- `LOD2`/`LOD3` at 115/125 m, front and oblique, noon and reverse sun.

Close renders at 25 m (front, oblique, rear and grazing, noon and morning),
the six views and `oblique` tier sets at 70 and 120 m for every tier are in
the local, untracked `review/mine_fixes_2026_11_20/hiilisiilo_drive_through/`,
beside the earlier passes in `review/mine_2026_11_20/`. The trestle pass is
in `review/bunker_trestle_2026_11_21/`: the six views, 25 m close renders
(`oblique` and `grazing`, noon and morning, `LOD0`/`LOD1`) and every tier
at 35, 70 and 120 m (`oblique` and `front`, noon), each before and after,
with `review_compare.py` sheets in `compare/`. Distances in the bullets
below that are not the consumer's 37 / 83 / 165 m are those passes'.

- **The lane is a real opening on every tier.** It costs about 40
  triangles. From the front it reads as a dark tunnel with the lit ground at
  its far end, from 22 m to 125 m.
- **The hoppers stay on every tier.** A first build dropped them at `LOD3`.
  At 115/125 m their dark notch under the lintel then vanished at the
  switch, so they were kept for 52 triangles.
- **Opening recesses** go from a ring (`LOD0`) to one recess (`LOD1`) to
  flush (`LOD2`). The window rhythm and the door are unchanged at each
  switch.
- **The gallery and the intake keep their shape on every tier.** On the
  east side they show in the catalog view and every front or oblique view,
  rising from the right into the screen house; at 120 m all four tiers show
  the same diagonal. The frame's columns and the ring beam are UV regions,
  so they keep their contrast at every tier.
- **The trestle** reads at 37 m as two dark legs on black footings with
  the X between them, the cross-head under the gallery's floor. `LOD2`
  keeps all of it: at the 83 m switch the old plain `LOD2` solid showed
  sunlit grey legs where `LOD1`'s shaded H channels read black, and lost
  the footings' dark feet (Construction). At 165 m the X is a faint pair of
  lines against the shaded east wall; `LOD3` drops it and the H-sections
  and keeps the two legs and the head as one plain solid, so the gallery
  stays visibly supported; the change there is barely visible (24 pixels
  in the eye view).
- **The roof** maps the repeating band on 2 m strips through `LOD2` and
  uncut, the band once over its length, on `LOD3`; at 165 m the corner
  view, which sees the roof most, shows no pixel over 24 changing.
- **The coal dust** is texture only, so it is the same on every tier; at 70
  and 120 m the dark feet and the dark lane hold. The intake roof's drifts
  read from raised views at 25 m and blur to a darker roof by 70 m.
- **Downpipes:** `downpipes.MODES` on every tier; no tier drops them.
- **The doors' floor slabs (2026-11-23)** add no transition of their
  own. Each goes with its door's reveal (0.12 m, 0.15 m) at the
  `LOD1`/`LOD2` switch, where the door is already painted flat: a 0.02 m
  nosing and 0.12–0.15 m of slab are under a pixel at 83 m. Checked from a
  standing eye (1.7 m, 75° vertical FOV, 1280 × 720) and from 0.35 m over a
  terrain plane at z = 0, 2–5 m from each door, face-on, from both sides
  and from above, noon and reversed sun, every tier (Review status).

Pending in the consumer: real LOD switching, shadows and ambient occlusion
in the lane, and performance.

## Interior geometry

The validator's hidden-surface test reports **0 hidden triangles on `LOD0`,
`LOD1` and `LOD2`**. On `LOD3` it reports one triangle of 0.0 m², at the
east downpipe's top where the three-sided pipe meets the rear soffit. It is
a zero-area candidate, not buried surface, and is far under the warning
thresholds.

- The lane's walls and ceiling are exterior surface, reachable from both
  mouths.
- The leg, the control room and the intake are solid: no interior is
  modelled.
- The kept closure faces are:
  - the floor caps under the leg, the control room and the intake walls.
    The control room's and the intake's run straight along the wall line
    under their doors' floor slabs on `LOD0` and `LOD1`, so no face lies at
    grade inside either reveal; the slabs are exterior surface and add no
    face inside the shell;
  - the trestle footings' bottoms (`LOD0`/`LOD1`) and its legs' feet
    (`LOD2`/`LOD3`), on the ground;
  - the hoppers' mouths, painted coal;
  - the downpipes' shoe mouths.
- The lids, the gallery's buried ends, the hoppers' tops and the trestle's
  buried ends (the legs in their footings and the head, the bars in the
  legs' webs, the head's top in the gallery's floor) are removed by the
  union.

## Known simplifications

- **Lane:** no floor, rails, weighbridge or lighting; the ground is the
  floor.
- **Floors:** each door's reveal has a flat concrete slab with no mat,
  drain, threshold strip or door track (Construction). The lane has none;
  the consumer's ground is its floor. The hoppers have no modelled gates;
  the gates are painted on their sides' foot.
- **Interiors:** the screen house's bins, screens, floors and stair are not
  modelled, and neither is the conveyor belt. The windows are closed opaque
  panes.
- **Painted detail:** the frame's columns, the ring beam, the deck joint,
  board marks, tie holes, the wheel guard, the downstand beams and hopper
  flanges on the lane's ceiling are all painted. So are the sheet's ribs and
  laps.
- **Gallery:** no windows. Its tail housing's top is a plain clad end.
  It has no belt, chute or skirt where it meets the screen house; the clad
  box simply runs into the wall.
- **Trestle:** no base plates, bolts, gussets or bearing; the bracing bars
  stand for the angles a real bent would carry, and they end in the legs'
  webs. The footings are plain concrete blocks, and the trestle has no
  ladder or walkway.
- **Ground:** the asset has no ground, so the coal spilt under the gallery
  and in the lane is carried by the surfaces that exist: the gallery's
  floor, the intake's roof, the trestle's feet and footings, the lane's
  walls and the legs' feet.
- **Rainwater goods:** the gutter is painted, with its relief in the normal
  map. The downpipes run up into the soffit behind it. The intake house's
  flat roof has no gutter.

## Texture set

One 1024² trim-sheet atlas, rasterised by `scripts/atlas.py` at `atlas.SS`
= 4, padded last by `atlas.pad()`. Layout, in rows from the bottom:

| Rows | Region | Mapping |
| --- | --- | --- |
| 0–414 | S1, concrete | U along the wall, V = height 0–6.40 m, 64 px/m |
| 414–554 | C, cladding (x 0–960) and column strip (x 972) | one 2.00 m repeat (rows 420–548) tiling in V, 64 px/m; periodic gutters 6 rows each side |
| 558–694 | ROOF | U = x at 64 px/m; V up the slope from the low edge, one 2.00 m repeat (rows 562–690) at 64 px/m tiling in V; periodic gutters 4 rows each side; also the gallery's top |
| 696–956 | unique | lane ceiling (160 × 256) and side walls (256 × 166) at 32 px/m; door, window, intake door at 64 px/m; hopper side; flat patches; the intake's roof (112 × 106 at x 444, y 846) and the trestle's steel (84 × 200 at x 880, y 718), both at 32 px/m; the doors' floor slabs, the control door's (71.04 × 8.96 at x 522, y 780) and the intake door's (166.4 × 10.88 at x 608, y 888), at 64 px/m |
| 960–980 | FASCIA | front and rake edges, 64 px/m |
| 988–1024 | EAVE_R | rear fascia with the gutter, then the roof's lowest 0.40 m at 40 px/m with the snow guard |

**Deviations from 64 px/m:**

- The lane's regions are at 32 px/m. They are in shade and seen obliquely;
  at 64 px/m they would need a third of the atlas. Relief heights there are
  scaled by 32/64, so the normal map's slopes stay physical.
- The intake's roof is at 32 px/m, planar from its slab's corner: felt and
  coal, nothing sharper than its roll seams, seen from above at a distance.
- The trestle's steel is at 32 px/m: every face maps U along its own
  horizontal run and V up from the ground, so the coal on its feet follows
  height. At 64 px/m its 6.25 m of height would need 400 rows. It is plain
  plate with no relief.
- The gallery's sides are sheared, a 15 % stretch: their U is taken from x
  alone, so the sheets' ribs stand plumb as on the walls, while V runs
  square to the 30° axis. Measured 64 px/m along the axis and 55.4 px/m
  across it (anisotropy 1.15), and the same on the tail housing's visible
  end. Kept: plumb ribs match the walls', and the stretch runs across the
  ribs, where only the band's noise varies.
- `LOD3`'s roof and gallery top are uncut and map the ROOF band once over
  their length: the roof from the eave strip's last row to the band's top,
  102 rows over 8.34 m (12 px/m), the gallery's top 128 rows over 9.24 m
  (14 px/m). Its ceiling has no room for the cuts (Per-tier triangle
  counts); past 165 m a metre is 4 px on screen, so the band's weathering
  is mip-averaged either way.

### Repeating roof

Until 2026-11-22 the roof band was 96 rows stretched over 9.60 m of slope
(10 px/m up the slope, anisotropy 6.4), so on the surface the catalog view
sees most its weathering was smeared six-fold. It now repeats as the
cladding does: one 2.00 m repeat at 64 px/m, every 2 m strip of the roof
and the gallery's top mapping the same rows (Construction), with its
noise and weather on the band's 128-row period (`noise()` covers both
bands). The ribs vary only in U. What follows the slope cannot live on a
repeating band, so it moved to the eave strip, whose V is the slope from
the low edge: the sheet's drip edge (0.85 shade over its first 0.15 m) and
the dirt gathering toward the gutter (`Weather.roof()`'s eave term, 0.15
falling by 1/e every 0.30 m). The band keeps that function's runs and
chalking at their slope-average strength (0.10 runs, 0.05 + 0.04 chalk in
broad patches), so the high front no longer chalks paler than the rest.
The eave strip still resamples the finished band's first rows, which now
sit at the same 64 px/m, so the strips meet without a seam.

### Repeating cladding

The screen house is 13 m tall, too much for one band. The walls are cut at
the 2.00 m joints and every strip maps onto the same rows. Profiled sheet
varies only across its ribs. The band's noise and weather are drawn on its
own 128-row period (`noise()` and the `Weather` subclass in
`facade_atlas.py`), so the repeat is seamless. Height-following weather goes
only on S1.

The gallery's sides map onto C with U from x and V square to the axis, so
the ribs stand plumb, sheared by the slope (Deviations above).

### Relief

| Feature | Relief |
| --- | --- |
| Sheet ribs | 25 mm (roof 30 mm), every 0.25 m |
| Formwork board lines | 2 mm; tie holes 6 mm |
| Steel flashings | 15 mm |
| Window frames | 12 mm; bars 8 mm |
| Wheel guard | 50 mm |
| Ceiling beams | 40 mm |
| Gutter roll | 70 mm |
| Snow guard tubes | 35 mm, scaled by 40/64 |
| Floor slab pores | 0.4 mm |

The ribs read raised in the 22 m morning renders.

### Weathering

Weathering follows `scripts/weathering.py`'s moderate level: grime, fade on
painted steel, wash, plinth and splash on S1, roof dirt toward the low edge,
runs under the flashings and the gutter.

- **Coal dust instead of soil.** Dirt resolves to the module's neutral dust
  colour on every id (the `steel` list). That dust is a mid-grey, lighter
  than the dark steel it settles on, so coal has its own field:
  `scripts/weathering.py`'s coal field `K`, carried by `pad()` with the
  other fields, which lerps the weathered colour toward the atlas's
  `COAL_DUST` (sRGB 46/45/44, passed as the `Weather`'s `coal_dust`;
  clipped at 0.9), adds 0.22 roughness and strips the metallic.
  `Weather.coal()` writes it, and deepens the shade by 0.30 of it where it
  lies thick. The atlas's own `Weather` subclass only makes the named
  noise periodic on the cladding band.
- **Where the coal dust goes, and how much (`K`):**
  - the legs' and walls' feet: `FOOT_COAL` 1.0 at the ground, falling by
    1/e every 1.50 m (`FOOT_FALL`), blotched. S1's V is height from the
    ground on every wall, so this height-following term is exact there;
  - the rest of S1: 0.06–0.28 in broad patches and long streaks;
  - the cladding band and the columns: 0.05–0.31, as periodic patches and
    streaks on the band's own period, nothing that follows height, since
    the band repeats up the wall;
  - the lane's walls: `LANE_COAL` 0.35 plus blotches everywhere, and 0.6
    more at the foot, falling by 1/e every 1.0 m;
  - the lane's ceiling: 0.35 plus 0.55 round each hopper's throat;
  - the hoppers' sides: 0.35 at the flange to 0.8 at the mouth;
  - the gallery's underside 0.85, caked with what the belt's return drops;
  - the intake's roof (its own region): 0.12 plus 0.30 and 0.15 in
    blotches and broad patches everywhere, and up to 0.65 more heaped round
    the gallery's tail where it stands through the slab, falling by 1/e
    every 0.50 m. Its felt is a lighter mineral grey (sRGB 80/79/77), so the
    drifts read against it;
  - the trestle: 0.20 plus blotches all over, 0.75 more at the ground
    falling by 1/e every 0.90 m, and 0.30 more on the cross-head under the
    gallery's floor; its footings take S1's foot, the heaviest coal there;
  - the slab soffits and reveals 0.25–0.30; the door feet 0.45;
  - the doors' floor slabs: 0.35 plus 0.15 in blotches, over
    `door_floor.weather()`'s trodden-in dirt, so they read with the
    coal-dark plinth and the doors' feet beside them.
- **Measured albedo** (grey_sheet, sRGB, band means):
  - concrete plinth (0–0.3 m) ~61, foot (0.3–1.0 m) ~80, 1–2 m ~97,
    2–4 m ~113, ring beam ~122 (both variants); the control door's floor
    slab ~100, lighter than the plinth beside it, as a trodden threshold;
  - cladding ~105 (grey_sheet), 93/57/49 (red_sheet); columns ~122;
  - lane walls ~42 at the foot and ~82 at 1.5–4 m; lane ceiling ~61;
  - hopper sides ~51; gallery underside ~35;
  - intake roof ~52 mean, 40 in the heaped coal to 72 on the bare felt;
  - trestle ~47 at its feet (0–0.5 m), ~60 at 1–2 m, ~67 at 3–5 m, ~57 on
    the cross-head;
  - roof ~73 (grey_sheet), ~64 (red_sheet).
- **Working, not abandoned:** the dust darkens and mattes; it adds no rust,
  stains, peeling or growth, and the cladding and roof above stay only
  moderately dirty.

### The door floor slabs

Painted by `scripts/door_floor.py` (`paint()`, `grain()`, `weather()`), as
the catalog's other door slabs are: float-finished cast concrete,
`ID_FLOOR`, sRGB **(132, 130, 124)** in both variants, roughness **0.88**,
nonmetallic. Occlusion deepens toward the jambs and the door (within
0.05–0.06 m in these shallow reveals), the pores are the concrete's noise
at 5 % shade and 0.4 mm of height, and trodden-in dirt and the coal above
lie over both. One region a door, U across the casing's width from its
left side, V the nosing's 0.02 m (1.28 px) and then the top from the wall
plane to the door, each bleeding 2 px into its gutter:

- **control:** 71.04 × 8.96 px at (522, 780), in the free block under the
  window; a slightly paler path is worn toward the leaf.
- **intake:** 166.4 × 10.88 px at (608, 888), in the free block above the
  intake door's region, 14 rows clear of it so the cavity blur does not
  reach the door's art. Wheels, not feet, cross it, so it has no worn path
  (`tread` off the slab); the coal film carries its wear.

Adding the control slab changed only its free block (x 510–601,
y 768–820); adding the intake slab only its own (x 578–831, y 874–935),
the region and the padding round it. The emission map is the same file.

### Lane occlusion

The lane's walls fall to shade 0.66 and AO 0.50 at mid-length, and its
ceiling to 0.55 and 0.40. Both darken further into the corners. The lane is
open at both ends, so the fall is symmetric about its middle, and one side
region serves both walls.

### Roughness and metallic

One ORM for both variants (`SURFACE` in `facade_atlas.py`). Everything
painted is dielectric, metallic 0: the cladding 0.55, the roof and its
flashings 0.52, the sashes 0.50, the doors 0.55, and the painted steel of
the hoppers, the trestle and the reveals 0.55. Until 2026-11-22 they
carried 0.10–0.30 metallic, which made the dark roof and steel flare grey
in the sun. Metal stays metal only where it is bare: the galvanised
gutter, downpipes and snow guard 0.48 / 0.60 and the door hardware
0.45 / 0.55. Concrete 0.90, the doors' floor slabs 0.88, coal 0.92, felt 0.90, glass 0.08, all 0; coal
dust adds roughness and strips metallic (Weathering).

### Filtering

Whole-atlas mip4 stress renders (`scripts/review_atlas_mips.py`) of `LOD2`
and `LOD3` at 120 m, front, 75° grazing and rear, under noon sun, showed no
roof/cladding colour leaks and no dark seams. The columns, the ring beam
line, the windows and the dark lane all hold. Repeated after the
2026-11-22 repeating roof band and atlas re-layout (the unique block up 12
rows, the fascia band above it) for `LOD2` and `LOD3` at 83 and 120 m,
oblique and aerial, base against mip3 and mip4
(`review/older_audit_2026_11_22/fix_industrial_a2/hiilisiilo_drive_through/mips/`):
at mip3 the roof's 2 m strip joints do not show; at mip4 they show on
`LOD2` as faint lighter lines across the roof, where the 16-texel average
reaches past the band's 4-row gutters. With the consumer's camera the
roof samples about mip3 at the 83 m switch and nears mip4 only toward
165 m, where `LOD3`, which maps the roof uncut, takes over; so the lines
can show faintly at the far end of `LOD2`'s range. Pending in the
consumer's sampler.

### Unique textures

Five 1024² RGB PNGs (4 MiB each in memory as RGBA without mips): two
albedos, plus one ORM, one normal map and one emission mask
shared by both variants.

## Glazing treatment

The glazing uses `scripts/glazing.py` `rooms()` on the finished albedo, with
the default base (sRGB 50/54/57), after the id, shade and AO pass. Measured
on the exported albedos, it is **sRGB 41 mean (linear 0.018), 0.31× the
trim** (the albedo's 99th percentile off the glass, 130), the same in both:
`scripts/validate_asset.py`'s measure over the emission mask's neutral
pixels shrunk by one, 40.9, and the texels the glass covers wholly, 40.7.
That mean is under the Style Direction band's 45 (the validator's own
window is 40–78): the panes' room levels and falloff toward the floor pull
it below the base. The glass is as built; this records what it measures.
Roughness is 0.08 (`glazing.ROUGHNESS`) and metallic 0.

Each window is a steel frame of four by three lights. Its 0.03 m bars are
merged by `rooms()` into one pane, and every window shares the one region,
so all seven windows show the same room.

The steel frame (sRGB ~92–94) is lighter than the glass, and the flashing
round it lighter still. There is no brief-driven departure from the Style
Direction band; the measured mean's shortfall under 45 is recorded above
and pending a look at the glass.

## Variant list

| Variant | Meaning |
| --- | --- |
| `grey_sheet` (default) | grey painted (or long-dulled galvanised) profiled sheet, dark grey roof, grey-green steel doors and frames |
| `red_sheet` | red-oxide painted cladding, dark warm-grey roof, dark grey doors |

Two variants, as the brief asks. This is an industrial plant with one
coherent treatment per instance: the concrete, the coal dust, the hoppers
and the galvanised rainwater goods are the same in both. Geometry, UVs, ORM,
normal and emission are shared.

## Night lighting

**Night-lit: it ships `_emission.png`.**

- **Mask:** the window glass only, via `glazing.night_rooms()`. That covers
  the five screen house windows and the two control room windows, all from
  one region, so every window shares one room pattern.
- **Not lit:** the lane is unlit, and there are no lamps or signs.
- **Default state:** `emissiveTexture` is bound on every tier with the factor
  rewritten to zero (`window_emission.rewrite_glb_emission`), so the asset
  ships with its lights off.
- **Reference lit factor:** the catalog's warm default
  (`window_emission.LIT_FACTOR`).
- **Control:** per building. Shared window UVs prevent per-window control.
- **`variants.png`:** day above night for both colours, from the catalog
  camera with fixed exposure (`scripts/variant_previews.py`).
- **No light spill** was simulated.
- **Pending in the consumer:** off/on on reimport and night intensity.

## Export

```
python3 facade_atlas.py export                       # albedo x2, ORM, normal, emission
blender --background source.blend --python build.py  # meshes, preview, variants, sidecar
```

Run the textures first. A first build from a factory scene is
`blender --background --python build.py`.

Export settings, as `asset_build.Asset.export_all()` passes them:

- `export_format='GLB'`, `use_selection=True`, `export_yup=True`;
- `export_apply=True`, `export_keep_originals=True`;
- `export_cameras=False`, `export_lights=False`.

After export, `strip_embedded_images()` removes the placeholder
`bufferView`s, and the emission factor is rewritten to zero.

**Bindings**, from the shared material on every tier:

- albedo → `baseColorTexture`;
- ORM G/B → `metallicRoughnessTexture`;
- ORM R → `occlusionTexture`;
- normal → `normalTexture` at scale 1;
- emission → `emissiveTexture`, factor 0.

The validator confirms one material, uri-only images, the normal and
emission bindings and the default-off factor on every tier. Backface
culling is on, and the material is single-sided and opaque. The preview is
`LOD0`, `grey_sheet`, from the catalog's fixed camera, sun and grey world.

### Facts sidecar

`export/hiilisiilo_drive_through.model.json`, in the glTF frame:

- **footprint:** the house rectangle, the gallery strip and the intake
  rectangle as one polygon (Footprint). The strip's four corners lie under
  the gallery, not on a wall.
- **storeys:** one storey at the ground, 42.27 m². That is the control room
  inside 0.30 m walls (4.80 × 7.40 m) plus the intake house inside 0.25 m
  walls (2.70 × 2.50 m). The lane, the bunker and the screen house are not
  storeys, and the west leg is a solid pier.
- **dwellings:** none.
- **doors:**
  - `control`: `entrance`, main, front wall;
  - `intake`: `vehicle`, on the intake's front face, facing −Y (+Z in
    the sidecar).

  The lane's mouths are not doors.
- **passages:** one, `truck_lane`, stated from the front mouth trucks
  enter by:
  - position [−5.925, 0, 4.35]: the lane's centre line (build x −1.90) on
    the front edge of the plan bounds (build y −4.30), under the roof
    slab's 0.30 m front overhang. The contract takes the whole plan bounds
    as solid, so a mouth under an overhang is stated on the bounds' edge,
    not on the wall plane (z 4.05), where an earlier sidecar put it;
  - forward [0, 0, −1], into the building towards the rear;
  - width 5.00 m between the side walls, length 8.70 m from the front
    bounds edge to the rear one at z −4.35 (build y 4.40, under the 0.40 m
    rear overhang), through (open at the rear). Under the overhangs nothing
    narrows the lane: the rear downpipes stand at build x ±5.75, outside
    it;
  - clear height 4.60 m, the hoppers' mouths (`Z_HOP`), over the whole
    length; the ceiling is at 5.20 m and the overhangs' undersides at
    12.83 m (front) and 11.96 m (rear).

## Review status

Checked here, in Blender:

- **Validator:** `scripts/validate_asset.py`, 0 FAIL, 10 MANUAL, and 0 WARN
  on a sidecar written from a committed tree (one WARN, `source.dirty`,
  until `build.py -- facts` rewrites it from one). Every tier passes:
  - welded manifold topology, one material, uri-only images;
  - the normal and emission bindings, the default-off factor;
  - triangle ceilings, pivot at ground and centred;
  - hidden surface 0/0/0/1 (Interior geometry).

  The glazing measures within its band in both albedos, and the facts
  sidecar is consistent.
- **Layout:** `check_layout()`, including the lane's clearances, the
  gallery's burial, the trestle's clearances and the downpipes.
- **Six views:** `LOD0` (`review_asset.py --six-views`). The lane shows the
  ground through it in the front view, clear of everything east of the
  house, and the gallery's joins into the east wall and the intake roof are
  clean.
- **Close renders:** 25 m, front, oblique, rear and grazing, under noon and
  morning sun. They checked the lane's read, the door's scale against the
  2.10 m leaf, the gallery's join, and the coal dust: black at the legs'
  feet and the intake's, in the lane and on the hoppers, light on the
  cladding.
- **Trestle pass** (`review/bunker_trestle_2026_11_21/`), before and after
  with identical settings: the trestle stands clear of the house, the lane
  and the intake door, its joins into the gallery's floor and its footings
  are clean in the six views and at 25 m, and the rest of the asset is
  unchanged beside them (whole-frame mean difference 0.2/255 in the 25 m
  oblique). The regenerated sidecar differs from the previous one only in its
  triangle counts, hashes and source: bounds, pivot, footprint, doors and
  the passage are the same.
- **Sidecar against `LOD0`:** the bounds match the mesh's; every footprint
  corner on a wall is a ground vertex (the strip's four corners under the
  gallery are not, by design); both doors sit on their walls' outer planes,
  facing out. The passage was measured on the exported `LOD0` (vertical
  rays from 1 cm up over a 41 × 88 grid on the lane's plan, from z 4.35 to
  −4.35, and sideways rays at 0.5, 2.5 and 4.4 m): the walls stand 2.50 m
  each side of the centre line between the wall planes (z 4.05 to −3.95),
  nothing stands inside the 5.00 m width under either overhang (the first
  thing sideways there is the rear downpipes, 3.8 and 7.6 m off), and the
  lowest geometry over the lane is 4.600 m, the hoppers' mouths; under the
  overhangs it is 12.83 m (front) and 11.96 m (rear).
- **LOD pairs:** at the consumer's 37 / 83 / 165 m (LOD review), and
  earlier around 35, 70 and 120 m under two sun directions.
- **The 2026-11-22 fixes** (lane, roof band, dielectric paint, `LOD2`
  trestle), before and after with identical settings in
  `review/older_audit_2026_11_22/fix_industrial_a2/hiilisiilo_drive_through/`:
  the tier pairs, and `LOD0` front and oblique at 20, 35 and 40 m (noon
  and `reverse`), both colours (`compare/lod0/`, `compare/lod0_red/`).
  The sidecar's only changes are the passage's position and length, the
  triangle counts of `LOD0`–`LOD2` and the hashes; bounds, footprint,
  storeys and doors are unchanged.
- **Filtering:** mip3/mip4 stress renders at 83 and 120 m, after the
  2026-11-22 roof band and atlas re-layout (Texture set).
- **Variants:** day and night for both (`variants.png`).
- **The door floor slabs** (Construction, Revision log). The control
  door's, from a snapshot in
  `review/review_2026_11_23/hiilisiilo_drive_through_before/`:
  - **Door views** (`review/review_2026_11_23/hiilisiilo_door_views.py`,
    every tier, noon and reversed sun, over a green terrain plane at
    z = 0): the control door from 5 m, 2.4 m, both sides, 0.35 m up and
    from above; the intake door from eye level and 0.35 m up. Before, grass
    filled the door's reveal between the casing's legs (`LOD0`) and the
    reveal's walls (`LOD1`); after, concrete fills it wall to wall, its
    nosing a light line on the wall plane with nothing past it, no dark
    seam or stretched texels. The `LOD2` and `LOD3` views and every intake
    view are unchanged (no pixel over 1/255).
  - **`review_asset.py`** from both: the day cycle on `LOD0`, the six
    orthographic views, and every tier front and oblique at 20, 35, 70 and
    120 m under noon; at most 131 pixels change by more than 24, at the
    door, in the 20 m front view. `review_compare.py` sheets in
    `review/review_2026_11_23/hiilisiilo_drive_through_compare/`.
  - The sidecar's bounds, pivot, footprint, storeys, both doors and the
    passage are unchanged; `LOD2` and `LOD3` are byte-identical. Measured on
    the exported `LOD0` and `LOD1`, an upward face at 0.020 m under 9 of 9
    sample points of the reveal and at its four corners, no face at grade
    inside it; the intake's reveal has none, as before.
  - `scripts/validate_asset.py`: 0 FAIL; the one WARN is `source.dirty`,
    the sidecar written from an uncommitted tree, to be rewritten with
    `build.py -- facts` once committed.

  The intake door's, from a snapshot in
  `review/review_2026_11_23/hiilisiilo_drive_through_pass2/before_src/`:
  - **Door views** (`.../hiilisiilo_drive_through_pass2/intake_door_views.py`,
    every tier, noon and reversed sun, over a green terrain plane at
    z = 0): the intake door from 4.3 m, 2.4 m, both sides, 0.35 m up and
    from above. Before, grass filled the reveal between the casing's legs
    (`LOD0`) and the reveal's walls (`LOD1`); after, concrete fills it wall
    to wall, its nosing a line on the wall plane with nothing past it, no
    dark seam or stretched texels. Under reversed sun no pixel changes by
    more than 26; the `LOD2` and `LOD3` views are identical.
  - **`review_asset.py`** from both: the six orthographic views, and every
    tier front and oblique at 20, 35, 70 and 120 m under noon: at most 653
    pixels change by more than 24, all at the intake door's foot, in the
    20 m oblique (`LOD1`); none at 120 m, and `LOD2`/`LOD3` identical.
    `review_compare.py` sheets in
    `review/review_2026_11_23/hiilisiilo_drive_through_pass2/compare/`.
  - The sidecar's bounds, pivot, footprint, storeys, both doors and the
    passage are unchanged (against the committed sidecar); `LOD2` and
    `LOD3` are byte-identical. Measured on the exported `LOD0` and `LOD1`,
    the intake reveal's upward face is at 0.020 m under 15 of 15 sample
    points (2.40 × 0.15 m on `LOD0`, 2.60 × 0.15 m on `LOD1`), its nosing
    on the wall plane, and no vertex at its foot in front of it.
  - `scripts/validate_asset.py`: 0 FAIL, `door floors` on the slab for
    both doors on `LOD0` and `LOD1`; the one WARN is `source.dirty`.

Pending in the consumer:

- import, orientation and pivot on reimport in the engine;
- that its trucks fit the lane: 3.5 × 4.0 m against 5.00 m clear and 4.60 m
  under the hoppers;
- LOD switching, shadows and AO in the lane;
- filtering of the repeating roof band's strip joints and the 32 px/m
  lane regions;
- night intensity;
- performance.

## Tooling versions

Blender 5.3.0 (built 2026-11-11), run headless (`--background`) throughout.
The MCP addon was not used. Texture generation used the system Python 3
with numpy, scipy and Pillow.

## Revision log

- **2026-11-23 — intake door floor slab.** The intake's vehicle door had
  no upward face in its 0.15 m reveal, so a consumer's terrain showed
  inside. It now stands on a concrete slab like the control door's,
  2.40 × 0.15 m on `LOD0` and 2.60 × 0.15 m on `LOD1`, on its own atlas
  region with no worn path. Tiers 1,058/906/718/486 to 1,062/910/718/486;
  bounds, pivot, footprint, doors and the passage unchanged; the emission
  map unchanged. The glazing's recorded measure corrected from sRGB 57
  (0.44× trim) to the measured 41 (0.31×); the glass is unchanged.
- **2026-11-23 — entrance floor slab.** The control room's door had no
  upward face in its 0.12 m reveal, so a consumer's terrain showed inside.
  It now stands on a concrete slab 0.02 m over the ground, nosing on the
  wall plane, on its own atlas region, built and painted by the shared
  `scripts/door_floor.py`, on `LOD0` and `LOD1`, where the reveal is cut.
  Tiers 1,054/902/718/486 to 1,058/906/718/486; bounds, pivot, footprint,
  doors and the passage unchanged; the emission map unchanged. The intake's
  vehicle door is left as it was.
- **2026-11-22:** audit fixes. The sidecar's truck lane now starts on the
  plan bounds' front edge under the overhang (z 4.05 to 4.35) and runs to
  the rear edge (length 8.00 to 8.70 m); width and clear height unchanged.
  The roof band repeats at 64 px/m on a 2 m period (was 10 px/m stretched),
  the roof and the gallery's top cut every 2 m on `LOD0`–`LOD2`; the atlas
  re-laid (unique block up 12 rows, the fascia band above it). Painted
  cladding, roof, flashings, sashes, doors and steel dielectric. `LOD2`
  keeps the full trestle. The gallery sides' 15 % shear recorded; LOD
  review at the consumer's 37 / 83 / 165 m. Triangles
  1,022 / 870 / 534 / 486 to 1,054 / 902 / 718 / 486.
