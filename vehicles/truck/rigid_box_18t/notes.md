# rigid_box_18t

## Style brief

A generic European cab-over distribution truck of 2005-2020: a two-axle
18 t rigid with a day cab and a dry box body with a rear roller door. Flat
fronted cab with rounded vertical corners and roof edge, a raked screen
under a dark sun visor, a slatted grille, a dark plastic bumper carrying
the headlamp units, step wells ahead of the front arches, a roof deflector
with side extenders closing the gap to the box. Under the box: chassis
rails, subframe and cross bearers, an aluminium fuel tank, a battery box,
an AdBlue tank, an air tank and a silencer behind two side guard rails;
twin rear wheels under flat mudguards with flaps, a rear under-run bar
with the lamp housings and the plate. No make, badge, signature grille,
lamp graphic or real livery; the plates are blank.

## Body class

`truck`, box 8.00 x 2.55 x 3.80 m, mirrors 0.25 a side, 1024 atlas.

## Dimensions

| | Target | Built |
| --- | --- | --- |
| Length | 7.90 | 7.900 |
| Width without mirrors | 2.53 | 2.530 (the box; cab 2.30, bumper 2.34, rear twins 2.48) |
| Width with mirrors | box + up to 0.25 a side | 2.980 (heads to x 1.490, 0.225 past the box, 0.34 past the cab) |
| Height | 3.70 | 3.700 (box roof; cab roof 2.75, deflector 3.55) |
| Wheelbase | 4.50 | 4.500 |
| Front / rear overhang | 1.40 / 2.00 | 1.400 / 2.000 |
| Front track | 2.05 | 2.050 |
| Rear track (twin centres) | about 1.84 | 1.840, 2.48 over the twins |
| Ground clearance | 0.20-0.25 | 0.250 (the mud flaps' lower edge; the tank 0.43, the bumper 0.40) |

Cab: front at s 0.11 at the corners and 0.05 at the centre line at its
foot (bowed, the lower front tucked back to the bumper), the screen's foot
at s 0.13 at the corners; bumper face at s 0 (centre) to 0.02 (corners);
back wall at s 1.80, so 1.69-1.75 long, 2.30 wide, roof 2.75. Box: s 1.90 to 7.90 (5.95 plus the rear frame), z
1.15 to 3.70, 2.53 wide; gap to the cab 0.10, closed at the sides by the
deflector's extenders to 0.03. Against the review sheet's 1.8 m figure the
cab floor sits at chest height and the box floor above head height, as it
should.

## Construction

Stations and the atlas share one module, `truck_atlas.py` (s metres back
from the bumper face, z up, x the driver's left); `build.py` builds the
tiers as `vehicle_build.Piece`s. Front toward -Y; the origin on the ground
at the centre of the 7.90 x 2.53 plan box.

- **Cab:** a loft of eight rounded plan rings (front corner radius 0.18,
  rear 0.06, four and two segments) from z 0.80 to the roof: the lower
  front tucked back 30 mm toward its foot over the bumper, the grille
  panel leaning 3.6 degrees, the screen 8.5 degrees, the roof edge rounded
  all round by three rings that pull the front back to s 0.43 and the
  sides in to 1.08. The front panel is bowed in plan: the centre line
  stands 60 mm proud of the corners on a parabola (three segments a side
  at LOD0, one at LOD1 and LOD2), sweeping into the corner radius. Cut by
  exact booleans: two arch cutters (radius 0.64 about the axle, inner wall
  at |x| 0.58, 12 segments), the step wells (0.20 deep; tread, dark
  liner walls and a plastic riser), the screen and grille recesses (30 and
  35 mm) and a dark wiper cowl recessed 20 mm under the screen up to its
  foot, their floors following the bow in strips (LOD1 keeps grille and
  cowl in the texture), the door glass
  recesses (20 mm) and the side repeaters. A lamp or pane is the floor
  of the cutter that makes its recess, built with its own id and UVs, so
  the difference leaves it tagged and mapped. Unioned with the deflector (a
  loft of five sections), its side extenders, the sun visor and, at LOD0,
  black fender lips round the arches.
- **Bumper:** its own shape, a four-ring loft bowed 20 mm in plan and
  wrapped round the corners (radius 0.15): a chamfered lower edge (70 mm
  back over 70 mm), a vertical face carrying the lamps, a small chamfer
  back at the top, 40 mm proud of the cab's lower front at the centre. The
  two headlamp units, 0.38 x 0.18, are recessed 26 mm: a thin (12 mm)
  dark frame round a light silver interior, the amber indicator at the
  outer end, the low and high beam cells with soft reflector bowls (a
  little lighter at the heart, a little darker toward the rim, no dark
  rings) and the daytime strip under them; lens roughness 0.12. The front plate is recessed 6 mm. The
  step carriers behind it are boxes with the lower step recessed (tread,
  dark walls). LOD1/LOD2: a tiled box with the same lens rectangles flat
  on its face.
- **Box:** one closed solid built face by face, no booleans: aluminium
  bottom and top rails and corner posts proud by 12 mm of the side panels
  (LOD0), the marker lamps as cells in the rails and the end frames, the
  roller door set 0.10 in behind the rear frame (LOD0).
- **Chassis and gear:** closed solids that touch nothing, 2 mm apart where
  they would meet (rails, subframe, cross bearers, engine and gearbox
  block, axle beam and housings, tank and straps, battery, AdBlue, air
  tank, silencer, guards and brackets, under-run bar and brackets, lamp
  housings, mudguards, flaps). Unioning them first cut every long face at
  every contact and cost 940 triangles at LOD0.
- **Mirrors:** per side two shaped heads, the tall main mirror (0.20 x
  0.38) and the squarer wide-angle one (0.16 x 0.15) under it, each a
  chamfered housing lofted from a front 20 % (16 %) smaller to the full
  rear, the dark mirror glass on the rear face (a plain face on a dark,
  metallic patch, not a glass id); a hexagonal tube post and two tube
  arms; unioned; the arms stop 2-6 mm off the cab. LOD1: one arm and one
  block.
- Normals: every face smooth, edges over 40 degrees (LOD1 50, LOD2/3 30)
  sharp, then a face-area weighted normal pass, so the big flat panels
  shade flat and the rounded corners blend into them.

### Decisions

- The white front end-outline lamps sit on the box's front top rail, above
  the deflector (z 3.60-3.66, 0.10 m in from the side): above the screen's
  top and within 0.40 of the side as UN R48 asks, the front third of a
  three-colour corner set with the red ones on the rear header, and on a
  flat face every tier keeps. The cab roof was the brief's other option.
- The bumper is unpainted dark plastic and the cab's lower side panels
  (step wells, below the door) dark plastic; the lower front panel between
  grille and bumper is painted.
- Contour marking: broken yellow retroreflective tape on the box's bottom
  rail and round the rear frame (UN R48 6.21), on unpainted aluminium.

## Wheels

Four parts: 1 front left, 2 front right (steer), 3 rear left, 4 rear
right, the rear twins one part a side (`twin=True`). Radius 0.52; front
width 0.30 (one 295 tyre), rear 0.64 (two tyres and the gap between).
Revolved closed solids with a ring corner at the very bottom.

- LOD0: 20 sides. Front: a shouldered tyre, the disc dished 25 mm in, the
  hub standing back out to the tyre's face. Rear: two shouldered tyres with
  a groove between, the outer disc recessed 70 mm, the hub boss
  protruding 50 mm from it.
- LOD1: 10 sides, tread, outer sidewall and a dished disc.
- LOD2: hexagonal prisms in the body (part 0), the rear twins one prism
  across the axle; LOD3: wheel feet of the under-body profile.
- Arches: the front ones 0.64 radius about the axle with the inner wall at
  |x| 0.58; a front wheel turned 35 degrees reaches |x| 0.62. Validator:
  15.0 mm nearest at LOD0 (the rear twin under its mudguard, straight),
  30.0 mm at LOD1; the turned fronts clear by more.

## Ids

`COLOR_0` normalised `UNSIGNED_BYTE` `VEC4` on every tier, A 255, written
by the shared chain from per-face surface and paint: part in R, surface in
G, paint in B (255 on 1,054 painted faces over the four tiers). Validator:
whole ids, one R, G and B per triangle, lamps and glass unpainted body.
LOD0/LOD1: parts 0-4, lamps 3, 4, 5, 6, 7, 8, 9, 11, 15, glass 32, 33.
LOD2: part 0, the same lamp groups, glass 32. LOD3: R 0, G 0; paint on the
upper (cab and box) solid only.

## Lamps

27 lenses at LOD0, each a recessed cutter floor:

| Group | Id | Lenses | Where |
| --- | --- | --- | --- |
| `tail_brake` | 3 | 2 | rear lamp housings, red |
| `indicator_left` / `_right` | 4 / 5 | 3 + 3 | headlamp outer ends, side repeaters on the cab sides, rear housings, amber |
| `reverse` | 6 | 2 | rear housings, inner cells, white |
| `low_beam` | 7 | 2 | headlamp units, 0.14 x 0.10 reflector cells |
| `high_beam` | 8 | 2 | headlamp units, 0.14 x 0.10 |
| `daytime` | 9 | 2 | 0.28 x 0.04 strip under the low and high beams |
| `fog_rear` | 11 | 1 | left (driver's) rear housing |
| `marker` | 15 | 10 | 2 white on the box's front top rail, 6 amber on the bottom rails at s 2.30, 4.60, 6.90, 2 red on the rear header |

Unlit colours in the albedo, lit colours in the emission (markers in their
own white, amber or red). LOD1 keeps every lens, as flat cells on the
simplified bumper, housings and box and as recesses on the cab. LOD2 keeps
every group on flat faces inside the LOD0 rectangles but not every lens:
the side repeaters, the side and front markers and the right reverse lens
are dropped (38 lamp faces). LOD3 has none. No
plate lamp, front fog lamps or high-mounted stop lamp.

## Glass

| Group | Id | Area |
| --- | --- | --- |
| `glass_windscreen` | 32 | 1.611 m2 (bowed with the front, in six strips) |
| `glass_front_side` | 33 | 0.993 m2 (both door windows) |

No cab rear window (37): a box truck's day cab has none here.

### Glazing treatment

A departure from `glazing.rooms()`, which paints each pane as a room with a
lit far wall: on a vehicle the wall patch read as a brown stain across the
screen. `truck_atlas.vehicle_glass()` paints every glass texel as the dark
cab behind the pane instead: a neutral, slightly cool base (sRGB 54, 58, 62)
with a gentle vertical falloff in each pane, 0.80 at its foot (the
dashboard's shadow) to 1.10 at its head (sky-lit headlining), a 1.5 %
grain, no per-pane level and no wall patch. Measured over the glass texels
(validator): sRGB 57, roughness 0.082, metallic 0, inside the Style
Direction's 45-70. The glass is darker than the painted cab round it but
brighter than its black rubber seals, which no pane in the band can avoid.
Emission: the lit cabin at a quarter, `glazing.night_rooms()`, unchanged.
LOD2: the screen is the whole front face between the screen rings, tagged
32; the door windows are dark seal texels in the cab band (not glass ids).
LOD3: glass is in the texture, flat base. `glass_texels.png` beside this
file.

## Paint

Painted (B = 1): the cab shell above the door line and its lower front
panel, the deflector and extenders, the box side panels and front wall.
A neutral base of 0.78 linear (sRGB 229) with panel seams, shut lines,
rivets, cavity shading and a light, neutral road film and faint runs: the
panel field (validator, area-weighted median of the painted texels) is
0.761 linear at LOD0 and LOD1, mean chroma 0.1. The band's dark details
stop at the openings' own edges, so the small LOD0 faces round the
recesses sample paint, not rubber. Unpainted: bumper and lower cab
plastic, aluminium rails, posts and rear frame, the roller door, the box
roof (pale translucent-white panel, the largest surface seen from above),
chassis, wheels. Plates blank white with a thin dark border, unpainted.
The review sheet's white, dark grey and red paint read on cab and box
alike; the deflector's caps and extenders take a uniform painted patch.

### Brightness across tiers

The painted mean (area-weighted over the albedo texels the painted faces
sample, linear) of each tier stays within 10 % of LOD0's, so a tier switch
does not change the truck's brightness under the same paint (validator):
plain LOD0 0.749, LOD1 0.741 (-1.1 %), LOD2 0.709 (-5.3 %), LOD3 0.740
(-1.2 %); haulier 0.523, 0.522, 0.483 (-7.8 %), 0.519 (-0.9 %). LOD2's and
LOD3's few large painted faces carry windows, grille and lower plastic
inside them, so the LOD3 pictures paint their cab and box with their own
ids (`M_CAB_FAR`, `M_BOX_FAR`) at 0.83 linear in `plain`, the haulier's
own colours in `haulier`. LOD2 shares the cab band with LOD0/LOD1, and
splitting its window and grille into their own faces would not fit its
350 triangles, so it stays at -5.3 %.

Rendered check (AgX, the review camera's 75 degree field of view,
silhouette mean): from LOD2 to LOD3 the step is under 1 % under white
paint, -4 % under red, -6 % under dark grey. Under dark paint the far
tiers are darker overall than LOD0 (LOD2 -6 %, LOD3 -12 % at 100 m)
because LOD0's light unpainted parts (tank, guards, rims, tape) shrink to
a few texels; the far pictures' light under-body parts were enlarged and
LOD2's under-box block now shows them, which took LOD2 from -9 % to -6 %
and LOD3 from -13 % to -12 %. More would need the light parts drawn larger
than they are.

## Per-tier triangle counts

| Tier | Triangles | Ceiling |
| --- | --- | --- |
| LOD0 | 4,316 | 4,500 |
| LOD1 | 1,380 | 1,400 |
| LOD2 | 348 | 350 |
| LOD3 | 60 | 60 |

LOD0: wheels 1,504 (front 2 x 316, rear 2 x 436), cab group 1,076 (the
bowed shell before its cuts, arches, recesses, deflector, visor, fender
lips, cowl), bumper 214, box 196, mirrors 248 + 246, step carriers 56, chassis
and gear about 780 as some 50 small solids, wipers 24. LOD1: wheels 304,
cab group 408, box 140, bumper 84, mirrors 2 x 24, chassis and gear about
350. LOD2: cab 60, bumper 68, box 44, bar 12 and lamp housings 32 + 28,
front wheels 2 x 20, the rear twins one hexagonal prism across the axle
(20, its middle inside the under-box mass), visor, deflector and dark
under-box block 44. LOD3: two extruded profiles, the painted cab and box
(8 points, 28) and the dark under-body (9 points, 32).

## LOD review

Switch distances as the contract's truck row: LOD0 under 30 m, LOD1
30-100 m, LOD2 100-400 m, LOD3 beyond. Reviewed on the review sheet
(75 degree vertical field of view, 1080p, tiers side by side at 30, 100
and 400 m) and in close renders at 35 mm, 1280 x 800, of each of LOD0-2
from the front right low, the left side low, the rear left, above the
front and under the left side, fixed camera and studio light.

- LOD1 keeps the cab/box step, deflector, visor, screen band and recess,
  door glass, arches, guards, tank, twin width, under-run bar, mirrors and
  every lamp; loses the step wells, fender lips, cross bearers, AdBlue and
  air tanks, the panel recess and the roller door's inset (both kept in
  the texture), the grille's and the cowl's recesses (texture), and the
  shaped mirror heads (one block a side); the cab's shut lines, flap,
  corner panels and handle are the same texture on both tiers.
- LOD2 keeps the box-over-cab massing, deflector, visor, the dark under-box
  mass, wheel positions and the wider rear, the dark screen and the pale
  roof; the wheels go hexagonal and the mirrors and guards go (the dark
  under-box block's sides carry the far picture's guards and tank); the rear is
  the bar with the two lamp housings over its ends, as LOD0's. At 100 m
  the silhouette holds.
- LOD3: the cab's nose chamfered, deflector and box front one slope, from
  pictures at 16 texels per metre, as one painted solid (its cab and box
  in a lighter far paint field, see Paint); the under-body a second,
  narrower solid on four wheel feet, unpainted (B = 0), its sides showing
  the picture's tyres, silver rims, guard rails and tank in their own
  colours, so it stays dark under any paint. Its front is one chamfer from the cab's foot to the
  front wheels' contact, and the gap under the box front is open.

## Interior geometry

No interior. Hidden faces (validator, inspection candidates): LOD0 275 of
4,062 (6.8 %), LOD1 90 (6.5 %), LOD2 43 (12.4 %), LOD3 0. They are the
faces kept closed 2 mm under another solid: the cab's bottom over the
bumper and the engine block, the bumper's and carriers' tops, the
subframe's and bearers' tops under the box floor, the mirror arm roots
beside the cab, and at LOD2 the dark block's top under the box and the
wheel prisms' tops inside the cab and the block.

## Known simplifications

- No suspension, brakes, tread geometry, steering linkage, cab
  suspension, tow pin, wiper linkage, door handles or grab handles in
  geometry; handles, seams, rivets, hatch, intake grille and tread are
  texture and normal map.
- Chassis members are plain boxes, not channel sections; the solids floating
  2 mm apart is invisible at any use distance.
- No tail lift, kerb mirror, roof antenna, front fog lamps or plate lamp.
- The door window is one recessed pane, without the lower front peep
  window many cabs have.
- The glass shows no interior (seats, dash, wheel): only the neutral dark
  cab and its vertical falloff.
- Under the studio sun the main mirror head casts a soft dark shape on the
  door below its window (checked with shadows off: it is the cast
  shadow, not geometry or texture).

## Texture set

One 1024 atlas, 64 texels per metre in final pixels, supersampled 4x
(`atlas.SS`); albedo per variant, ORM, normal and emission, PNG, external.

- Layout: the large regions in three bands from the bottom; the small
  uniform, lens and plate patches each alone in a 32-texel block on a
  64-texel grid, the bottom-rail strip 20 texels clear of the tyre
  treads, the cab band 186 texels clear of the box regions.
- At 64 texels/m: box sides (both sides share one mirrored region), roof,
  front, rear; the cab band (U round the perimeter from the front centre,
  mirrored, V up the profile) and cab roof; deflector; bumper band; the
  bottom-rail strip; grille; tyre treads; door and screen glass (stretched
  within 5 %).
- Deviations: the wheel faces 69 texels/m; uniform patches (chassis black,
  arch liner, aluminium, tank, guard grey, rubber, plastic, step, lamp
  housing, mirror glass and body, seal, cab paint) and the lens and plate
  patches are stretched over their faces, which carries no detail to
  stretch; the LOD3 side, front and rear pictures at 16 texels/m, their
  cab and box in the far paint ids (0.83 linear in `plain`) and the cab's
  lower front painted as LOD0's.
- Cab shut lines are two texels (31 mm) of darkening on a 3 mm groove:
  the door all round (from the step up into the roof's rounding, across
  the top and along the door line), the front service flap round the
  grille with rounded corners, the corner panels either side of the front
  below the screen and just round the corner up the A-pillar, and the
  break between the upper and the lower panels at the door line; the
  door handle a dark recess with a lighter pull; the step area under the
  door dark plastic with tread lines (the step patches too).
- Relief in the height channel: box panel joints 1.5 mm, rivets 1 mm,
  roof bows 4 mm, roller door slat grooves 4 mm, door seams 2 mm, grille
  slats 8-10 mm, tread grooves 8 mm, rim edges 4 mm; glass flat.
- Padding by `atlas.pad()`.
- Mip review: whole-atlas mips 3, 4 and 5 (`scripts/review_atlas_mips.py`,
  linear-light box filter) rendered on LOD1 (mip 3, about 100 m) and LOD2
  (mips 4 and 5, about 200-400 m) from the front three-quarter, the rear
  three-quarter and above. The first pass showed the red marker lens
  patch bleeding into the black visor and bumper plastic patch at mip 5;
  the uniform and lens patches were then spaced 64 texels apart, which
  cleared it. No leak of the yellow tape, the amber markers or the dark
  chassis into the box panels at any of the three levels; the tape and the
  rear frame's tape soften into their own aluminium as they should.
  Consumer filtering pending.
- Weathering at the moderate level: road film on the lower cab, box sides
  and rear door's lower half, spray behind the rear wheels, faint runs and
  wash down the box sides, dust on the roof and the deflector's lip, dirt
  on chassis, flaps, steps and tyres; painted ids take the neutral dust
  so no colour is baked into the panels.
- Unique textures: 6 of 1024 x 1024 (2 albedo, ORM, normal, emission);
  `glass_texels.png` is not shipped.

## Variant list

- `plain` (paint true, default): painted panels neutral grey; the
  consumer multiplies them by the truck's colour.
- `haulier` (paint false): a muted dark blue cab and a white box in full
  colour, no lettering, no logo; the consumer paints it white, so it shows
  as shipped. Same mesh, UVs, ORM, normal and emission.

## Export

`blender --background --python build.py` after `python3 truck_atlas.py
export` (system Python with scipy and Pillow). The shared chain exports
each tier `export_yup`, `export_apply`, `export_keep_originals`, cameras
and lights off, `metrum_ids` as the only colour (`COLOR_0`), Draco and
meshopt off; images stripped of embedded bufferViews; emission factor
rewritten to zero; `COLOR_0` rewritten as exact bytes. One material on
every tier: albedo (`plain`) to base colour, ORM to roughness, metallic
and occlusion, normal map at strength 1, emission default off.
`preview.png` and `variants.png` use the albedo as shipped
(`preview_paint` None). `blender --background --python build.py -- facts`
rewrites the sidecar alone.

## Review status

Done here:

- Validator (`vehicle_truck`): 0 FAIL; WARN only for `source.dirty` before
  the commit.
- Review sheet looked at: views, both steering angles (wheels clear the
  arches and fender lips), every lamp group lit alone, the night set, the
  lit cabin, ids, white, dark grey and red paint, the tiers at 30, 100 and
  400 m. Three critique rounds, a polish round and a cab detail round
  (see Revision log), each compared before and after with renders of a
  snapshot of the previous build.
- Light-fringe sweep in close renders: arches and fender lips, step wells
  and carriers, visor, mirror arms and heads, bumper top, grille and cowl
  recesses, box rails, mudguards and flaps. One found and fixed: a painted
  strip between the cowl and the screen recess (the cowl now runs up to
  the screen's foot).
- Mip stress renders at mips 3-5 (Texture set).
- Glass and paint measured; lens rectangles, glass texels and pairs pass.
- A generic composite: no make, badge, signature grille or livery.

Pending in the consumer: wheel spin and steer about the sidecar axes,
lamp and cabin control by id, paint through B, mip filtering at distance,
LOD switching, performance.

## Tooling versions

Blender 5.3.0 (2026-11-11); Blender MCP extension not used for this build
(headless scripts only).

## Revision log

- 2026-11-21, cab detail: shut lines for the front service flap, the
  corner panels, the upper/lower panel break and the door all round, a
  dark recessed handle and tread lines on the step area; a recessed wiper
  cowl under the screen; the front bowed 60 mm (was 40), the lower front
  tucked back 30 mm toward the bumper, the screen raked 8.5 degrees (was
  6); headlamp units as light silver interiors in a 12 mm dark frame with
  soft reflector bowls, lens roughness 0.12; shaped, tapered mirror heads
  on tube arms, darker mirror glass; door, door glass and repeaters moved
  back with the corner; the far pictures' light under-body parts larger
  and shown on LOD2's under-box block.

- 2026-11-21, tier brightness: the LOD3 pictures' cab and box on their own
  far paint ids at 0.83 linear (LOD3 painted mean 0.681 to 0.739, LOD0
  0.753), the LOD3 front's lower panel painted as LOD0's, the under-body
  picture's guards, tank and rims restored now that its solid is
  unpainted. No geometry changed.
- 2026-11-21, polish: vehicle glass painted neutral dark with a vertical
  falloff instead of `glazing.rooms()`; the paint base raised to 0.78
  linear, wear on paint lightened and the band's dark details kept to the
  openings, so the painted mean is 0.744; the cab front bowed 40 mm in
  plan with the screen and grille recesses following it; the bumper
  reshaped (bow, chamfers, corner wrap) with 0.38 x 0.18 framed headlamp
  units; step wells shaded; LOD3 split so the under-body is unpainted; the
  LOD2 rear as a bar and two lamp housings; the atlas's small patches
  spaced for mip 5; door, mirrors and seam moved 40 mm back with the cab's
  new corner station.
- 2026-11-21: first build and three review rounds. Round 1: the lower cab
  front painted, black fender lips round the front arches, a sun visor,
  parked wipers, wheels to 20 sides, the intake vent smaller, plastic and
  steps given neutral dust. Round 2: the grille narrower and lower, lens
  detail in the head and rear lamps, the LOD3 underbody kept dark,
  a non-manifold mirror arm union fixed. Round 3: the visor added to LOD2
  (one LOD2 reverse lens dropped to pay for it), a rounder fuel tank, the
  glass base lifted into the Style Direction band, previews on the albedo
  as shipped.
