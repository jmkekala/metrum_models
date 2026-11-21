# rigid_box_18t

## Style brief

A generic European cab-over distribution truck of 2005-2020: a two-axle
18 t rigid with a day cab and a dry box body with a rear roller door. The
cab's front is crowned in plan and rounded into its sides, which are widest
at the belt and lean in above it; a raked screen with rounded corners in a
dark surround over a slatted wiper cowl, under a dark sun visor wrapped
round the corners. Below a brow at the belt the front flap carries a
trapezoid slatted grille in a shallow recessed field, a centre intake slot
and two grab handle recesses; body-colour air deflector blades stand off
the corners over a dark slot. Under it a dark plastic lower module: a
bumper with a set-back chin, bright headlamp units in gloss black inserts
in its corners, a recess with a moulded rim between them, a ribbed step
tread on its top, tow-eye covers, fog lamps and the plate on its plinth on
the chin, wrapped round the corners into the step fairings and the front
arches' black lips. A door with a dropped front window corner, a recessed
handle and a grab handle behind it; a moulded roof fairing that rises in
one smooth convex curve to the box top and flares to the box corners, side
collars under it from the cab's rear edges. Under the box: chassis
members and cross bearers, a strapped aluminium fuel tank, a battery box,
an AdBlue tank, an air tank and a silencer behind two side guard rails;
the front mudguards' rear quarters with flaps, twin rear wheels under flat
mudguards with flaps, a rear under-run bar with the lamp housings and the
plate. No make, badge, signature grille, lamp graphic or real livery; the
plates are blank.

## Body class

`truck`, box 8.00 x 2.55 x 3.80 m, mirrors 0.25 a side, 1024 atlas.

## Dimensions

| | Target | Built |
| --- | --- | --- |
| Length | 7.90 | 7.900 |
| Width without mirrors | 2.53 | 2.530 (the box; cab 2.30 at its foot and 2.32 at the belt, lower module 2.38, rear twins 2.48) |
| Width with mirrors | box + up to 0.25 a side | 2.986 (heads to x 1.493, 0.228 past the box, 0.34 past the cab) |
| Height | 3.70 | 3.700 (box roof; cab roof 2.75, fairing 3.535) |
| Wheelbase | 4.50 | 4.500 |
| Front / rear overhang | 1.40 / 2.00 | 1.400 / 2.000 |
| Front track | 2.05 | 2.050 |
| Rear track (twin centres) | about 1.84 | 1.840, 2.48 over the twins |
| Ground clearance | 0.20-0.25 | 0.250 (the rear mud flaps' lower edge; the front flaps 0.26, the valance 0.38, the tank 0.43) |

Lower module: bumper face at s 0 on the centre line, 0.11 back at the
corner radius (0.22), z 0.585 to 0.955, a rolled top edge to 0.995, the
chin 35 mm behind the face from z 0.43 to 0.555, the valance tucked back
to s 0.085 at z 0.38; 2.38 wide. Cab: its foot at z 1.00, 85 mm behind the
bumper face (a 55 mm ledge), the front panel leaning 5 mm forward to its
brow at the belt (z 1.54, s 0.080), which stands 35 mm proud of the
screen's foot; the screen panel from z 1.62 (s 0.115) to 2.52 (s 0.275),
raked 10 degrees; back wall at s 1.80, so 1.72 long, 2.30 wide at its
foot, 2.324 at the belt and 2.19 at the screen's head, roof 2.75. Box:
s 1.90 to 7.90 (5.95 plus the rear frame), z 1.15 to 3.70, 2.53 wide; gap
to the cab 0.10, closed in side view by the cab's collars and the fairing
over them. Against the review sheet's 1.8 m figure the cab floor sits at
chest height and the box floor above head height, as it should.

## Construction

Stations and the atlas share one module, `truck_atlas.py` (s metres back
from the bumper face, z up, x the driver's left); `build.py` builds the
tiers as `vehicle_build.Piece`s. Front toward -Y; the origin on the ground
at the centre of the 7.90 x 2.53 plan box.

- **Shell (lower module and cab):** one loft of thirteen plan rings from
  z 0.38 to the roof, 20 points a ring at LOD0. Each ring is a front bowed
  in plan (a parabola, the centre line 110 mm proud of where the corner
  radius starts; three segments a side), a corner arc that starts on the
  parabola's tangent (four segments), a straight side and a chamfered rear
  corner (0.07). Six rings make the lower module: the tucked valance, the
  chin, the face that carries the lamps (corner radius 0.22, half width
  1.19) and its rolled top edge; then a ledge 55 mm back to the cab's
  foot. The cab's rings: front corner radius 0.24 at its foot and 0.22 at
  the belt, where the front panel has its brow (5 mm forward of the foot,
  then 35 mm back to the screen's foot over 80 mm) and the sides their
  crown (half width 1.150 at the foot, 1.162 at the belt, 1.150 at the
  screen's foot); the corner tightening over that shoulder to 0.15 and
  0.13 at the screen's head (the A-pillars), the sides leaning in 3.5
  degrees to 1.095, the roof edge rounded by two rings that pull the front
  back to s 0.46 and the sides in to 0.985. Twisted quads are split into
  triangles before any boolean (`split_quads`), mirrored about x = 0: left
  whole, one boolean cut them one way and the next the other, and the cuts
  stood off the surface as fins.
- **Cuts, exact booleans:** two arch cutters (radius 0.64 about the axle,
  inner wall at |x| 0.58, 12 segments); the screen inside its rounded
  outline (a trapezoid 1.99 wide at its foot, 1.91 at its head, 0.83 tall,
  corner radius 0.09, recessed 30 mm, its floor following the bow in
  strips); the grille (a trapezoid 1.52 wide at its foot, 1.28 at its
  head, 0.375 tall, chamfered corners, recessed 40 mm); the door glass on
  the leaning side (an eight-point outline with a dropped front lower
  corner and a front edge parallel to the A-pillar, recessed 22 mm); the
  side repeaters; on the lower module the two step wells a side (0.20
  deep; ribbed tread, dark liner walls), the headlamp units and the fog
  lamps (below) and the recess between the lamp pods (0.88 x 0.265, 80 mm
  deep, a mesh floor over a tread). A recess's strips break at its
  outline's own corners, at the centre line and at chosen stations kept
  away from the shell's facet edges, so no sliver is left beside one. A
  lamp or pane is the floor of the cutter that makes its recess, built
  with its own id and UVs. LOD1 keeps the grille, the step wells and the
  centre recess in the texture, and cuts the screen with sharp corners.
- **Headlamp units:** 0.43 x 0.25 in the bumper face's corners (centre
  |x| 0.775, z 0.735), each recess turned square to the bowed face (9
  degrees) and 30 mm deep, its walls a light bezel: the amber indicator
  at the outer end (0.105 x 0.25), the low (0.145 x 0.195) and high beam
  (0.18 x 0.195) reflectors and the daytime strip under them (0.325 x
  0.055), six cells that share every corner. At LOD0 the recess sits
  inside a step 14 mm wide and 6 mm deep whose ledge is the gloss black
  insert, a real rim round the unit. LOD1 cuts the plain recess in LOD0's
  planes; LOD2 carries the lenses on plaques in those planes.
- **Fog lamps:** a pair in the chin's corners (centre |x| 0.875, z 0.497,
  0.124 x 0.062, recessed 12 mm, turned square to the bow, each in a gloss
  black insert). LOD1 cuts the same recesses, deeper, through its flat
  lower module; LOD2 keeps the left one as the face of a small
  tetrahedron in LOD0's plane.
- **Unioned with the shell:** the roof fairing, a second loft of six plan
  rings from the roof (z 2.70) to 3.535 whose nose is a quadratic Bezier
  in side view, leaving the roof at s 0.62 at 44 degrees and flattening
  all the way to 22 degrees at the top (s 1.86, z 3.56): one smooth
  convex rise, neither a ramp nor a dome. Its sides close in toward the
  nose by 0.24 per metre and are 2.44-2.49 wide at the back, 20 mm inside
  the box corners, the top edge rounded over by 50 mm; 14 points a ring.
  The sun visor, a plank swept along the cab's plan at the screen's head
  in six segments, bowed with the front and wrapped round the corners
  onto the pillars, its reach tapering from 0.205 to 0.03 there. The
  corner blades (LOD0): a body-colour blade a side, z 1.035 to 1.52,
  rooted inside the front panel at a tenth of the corner arc and standing
  off the corner toward its tail (48 mm out, 14 mm thick), an open slot
  34 mm wide behind it, drawn dark on the corner panel. Black fender lips
  round the arches (five segments). This union is not snapped to the
  boolean grid: none of them shares a wall with the cab.
- **Closed solids that touch nothing:** the plate's plinth on the chin
  (0.54 x 0.114, 18 mm deep, LOD0; its face is the plate); the cab's side
  collars (a painted flap from each rear edge of the cab to the box
  corner, z 1.55 to 2.694 under the fairing's overhang, its foot
  following the leaning side; LOD0 and LOD1); the front mudguards' rear
  quarters behind the cab with their flaps (LOD0; LOD1 one plate a side);
  LOD1's blades (a short tail plate off its own, more conical corner);
  two parked wiper arms (LOD0), parallel, each from its pivot 0.45 either
  side of the centre line over a boss drawn on the cowl.
- **Box:** one closed solid built face by face, no booleans: aluminium
  bottom and top rails and corner posts proud by 12 mm of the side panels
  (LOD0), the marker lamps as cells in the rails and the end frames, the
  roller door set 0.10 in behind the rear frame (LOD0).
- **Chassis and gear:** closed solids that touch nothing, 2 mm apart where
  they would meet (a rail and subframe member a side, six cross bearers,
  rear axle housings and differential, tank, battery, AdBlue, air tank,
  silencer, guards and brackets, under-run bar and brackets, lamp
  housings, mudguards, flaps). LOD0's rear mudguards follow the twins: a
  band round the axle from 20 to 160 degrees in four segments (inner
  radius 0.577, 30 mm over the tyre at the facets' middles), the flap
  under its tail; LOD1 keeps a flat guard with a rubber lip. The tank is mapped along and round its
  patch, so its two dark straps are rings. Tank, battery box, AdBlue
  tank, air tank and silencer hang 2-14 mm off the rail's side, so none
  needs a bracket. Unioning them first cut every long face at every
  contact.
- **Mirrors:** per side two heads behind a square tube post, the post
  between two tube arms from the door frame (the upper slanting back to
  the frame beside the A-pillar), as five closed solids 2 mm or more
  apart: the tall main head (0.20 x 0.41, its corners rounded in two
  steps, three bands swelling from a small front to the full rear face)
  and the squarer wide-angle one (0.18 x 0.16) under it, the dark mirror
  glass on the rear face (a plain face on a dark, metallic patch, not a
  glass id); the arms stop 3 mm off the cab. LOD1: one arm and one block.
- Normals: every face smooth, edges over 40 degrees (LOD1 50, LOD2/3 30)
  sharp, then a face-area weighted normal pass, so the big flat panels
  shade flat and the rounded corners blend into them.

### Decisions

- The white front end-outline lamps sit on the box's front top rail, above
  the deflector (z 3.60-3.66, 0.10 m in from the side): above the screen's
  top and within 0.40 of the side as UN R48 asks, the front third of a
  three-colour corner set with the red ones on the rear header, and on a
  flat face every tier keeps. The cab roof was the brief's other option.
- The whole lower module (bumper, chin, corner and step fairings) is
  unpainted dark plastic, as are the cab's sides below the door line, the
  fender lips and the visor; the cab's front is painted from the bumper's
  top up. The corner blades and the collars are painted with the cab. The
  cab's back wall is dark and unpainted, so the gap to the box reads as a
  clean shadow under any paint.
- The fairing's sides and the collars under them stand 20-27 mm inside the
  box corners and end 40 mm before the box front.
- The right rear lamp unit carries a red retro-reflector (a plain face)
  where the left one has the fog lamp, so the two units match.
- Contour marking: broken yellow retroreflective tape on the box's bottom
  rail and round the rear frame (UN R48 6.21), on unpainted aluminium.

## Wheels

Four parts: 1 front left, 2 front right (steer), 3 rear left, 4 rear
right, the rear twins one part a side (`twin=True`). Radius 0.52; front
width 0.30 (one 295 tyre), rear 0.64 (two tyres and the gap between).
Revolved closed solids with a ring corner at the very bottom.

- LOD0: 20 sides. Front: a tyre with its outer shoulder, the disc dished
  50 mm in, the hub a cone standing back out to the tyre's face. Rear: two
  tyres with a groove between, the outer one shouldered, the outer disc
  recessed 70 mm, the hub boss protruding 55 mm from it. The inner
  sidewalls, which nothing shows at any use distance, have no shoulder.
  The disc's texture and height carry ten wheel nuts on a 335 mm circle
  round the hub, the hand holes outside them and the hub's darker cone
  and cap.
- LOD1: 10 sides, tread, outer sidewall and a dished disc.
- LOD2: each axle's wheels one hexagonal prism across it in the body
  (part 0), the middle inside the body; the front one stands 6 mm proud
  of the lower module's sides, which LOD2 does not cut for arches, so
  the discs show. LOD3: wheel feet of the under-body profile.
- Arches: the front ones 0.64 radius about the axle with the inner wall at
  |x| 0.58; a front wheel turned 35 degrees reaches |x| 0.62, and its
  corners 0.541 from the wheel centre, inside the fender lips (0.615) and
  the wings behind the cab (0.645). Validator: 23.9 mm nearest at LOD0
  (a front wheel turned 35 degrees), 30.0 mm at LOD1 (the rear twin under
  its mudguard, straight).

## Ids

`COLOR_0` normalised `UNSIGNED_BYTE` `VEC4` on every tier, A 255, written
by the shared chain from per-face surface and paint: part in R, surface in
G, paint in B (255 on the painted faces of every tier). Validator:
whole ids, one R, G and B per triangle, lamps and glass unpainted body.
LOD0/LOD1: parts 0-4, lamps 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, glass 32, 33.
LOD2: part 0, the same lamp groups, glass 32. LOD3: R 0, G 0; paint on the
upper (cab and box) solid only.

## Lamps

29 lenses at LOD0, each a recessed cutter floor or a cell:

| Group | Id | Lenses | Where |
| --- | --- | --- | --- |
| `tail_brake` | 3 | 2 | rear lamp housings, red |
| `indicator_left` / `_right` | 4 / 5 | 3 + 3 | headlamp outer ends (0.105 x 0.25), side repeaters on the doors' front edges, rear housings, amber |
| `reverse` | 6 | 2 | rear housings, inner cells, white |
| `low_beam` | 7 | 2 | headlamp units, 0.145 x 0.195 reflector cells |
| `high_beam` | 8 | 2 | headlamp units, 0.18 x 0.195 |
| `daytime` | 9 | 2 | 0.325 x 0.055 strip under the low and high beams |
| `fog_front` | 10 | 2 | the chin's corners, 0.124 x 0.062, white |
| `fog_rear` | 11 | 1 | left (driver's) rear housing |
| `marker` | 15 | 10 | 2 white on the box's front top rail, 6 amber on the bottom rails at s 2.30, 4.60, 6.90, 2 red on the rear header |

Unlit colours in the albedo, lit colours in the emission (markers in their
own white, amber or red; validator: 12 white, 12 amber, 5 red). The
front lenses are bright silver behind clear glass, each mapped whole onto
its own patch at about 240 texels per metre: a field of about sRGB 200
(low beam 202, high beam 198), each reflector a soft bowl across its whole
cell, falling smoothly with no edge to a darker heart (about 162) with a
small soft bulb cap in it (a low oval, about 150); the high beam has faint
upright flutes lighter than the bowl; the daytime strip is only subtly
lighter (214); the cells are parted by light chrome dividers (227, lit
with the lenses). No darker line anywhere inside a unit (no joints, rings,
outlines or flute lines) and no glints; roughness 0.12, nonmetallic. The
only dark line is the gloss black insert the unit sits in. The fog lenses
are the same bowl and cap. The rear lenses have soft ribs 5 % apart. LOD1
keeps every lens, as flat cells on the housings and box and as recesses on
the shell (the headlamp and fog recesses in LOD0's planes, so the lens
rectangles are the same). LOD2 keeps every group on flat faces inside the
LOD0 rectangles but not every lens: the side repeaters, the side and front
markers, the right reverse lens and the right fog lamp are dropped (37
lamp faces); its headlamp lenses are plaques' outer faces. LOD3 has none.
No plate lamp or high-mounted stop lamp.

## Glass

| Group | Id | Area |
| --- | --- | --- |
| `glass_windscreen` | 32 | 1.646 m2 (bowed with the front, in strips, rounded corners) |
| `glass_front_side` | 33 | 1.251 m2 (both door windows, the front lower corner dropped) |

No cab rear window (37): a box truck's day cab has none here.

### Glazing treatment

A departure from `glazing.rooms()`, which paints each pane as a room with a
lit far wall: on a vehicle the wall patch read as a brown stain across the
screen. `truck_atlas.vehicle_glass()` paints every glass texel as the dark
cab behind the pane instead: a neutral, slightly cool base (sRGB 54, 58, 62)
with a gentle vertical falloff in each pane, 0.80 at its foot (the
dashboard's shadow) to 1.10 at its head (sky-lit headlining), a 1.5 %
grain, no per-pane level and no wall patch. Measured over the glass texels
(validator): sRGB 57, roughness 0.083, metallic 0, inside the Style
Direction's 45-70. The glass is darker than the painted cab round it but
brighter than its black rubber seals and the dark surround drawn round the
screen (a seal band and the wiper cowl under it), which no pane in the band
can avoid.
Emission: the lit cabin at a quarter, `glazing.night_rooms()`, unchanged.
LOD1: the screen's corners are sharp, inside the same dark surround.
LOD2: the screen is the whole front face between the screen rings, tagged
32; the door windows are dark seal texels in the cab band (not glass ids).
LOD3: glass is in the texture, flat base. `glass_texels.png` beside this
file.

## Paint

Painted (B = 1): the cab from the bumper's top up round the front and
from the door line up on the sides, its roof, the corner blades, the
fairing, the collars, the box side panels and front wall. A neutral base
of 0.78 linear (sRGB 229) with panel seams, shut lines, rivets, cavity
shading and a light, neutral road film and faint runs: the panel field
(validator, area-weighted median of the painted texels) is 0.761 linear at
LOD0 and LOD1, mean chroma 0.1. Dark trim runs a texel past its faces'
outline (the lower module one texel up the cab's foot, the lower side band
one texel into the corner arc and above the door line, the back wall one
texel into the rear corners), so no unpainted face samples paint and no
light fringe shows; checked in close renders under dark grey and red paint
at the ledge, the grille and its field, the blades and slots, the step
fairing, the fender lips, the lamp pods and the screen surround.
Unpainted: the lower module, fender lips and visor, the cab's back wall,
aluminium rails, posts and rear frame, the roller door, the box roof (pale
translucent-white panel, the largest surface seen from above), chassis,
wheels. Plates blank white with a thin dark border, unpainted. The review
sheet's white, dark grey and red paint read on cab and box alike; the
fairing's back, the blades, the collars and the roof take a uniform
painted patch or their own region.

### Brightness across tiers

The painted mean (area-weighted over the albedo texels the painted faces
sample, linear) of each tier stays within 10 % of LOD0's, so a tier switch
does not change the truck's brightness under the same paint (validator):
plain LOD0 0.744, LOD1 0.731 (-1.7 %), LOD2 0.717 (-3.6 %), LOD3 0.730
(-1.9 %). LOD2's and LOD3's few large painted faces carry windows, grille
and trim inside them, so the LOD3 pictures paint their cab and box with
their own ids (`M_CAB_FAR`, `M_BOX_FAR`) at 0.83 linear in `plain`, the
haulier's own colours in `haulier`. LOD2 shares the cab band with
LOD0/LOD1.

Rendered check (AgX, the review camera's 75 degree field of view,
silhouette mean, 100 m / 400 m, against LOD0): under white paint every
tier within 1.6 %; under red LOD1 -1.9 / -1.9 %, LOD2 -3.2 / -3.3 %, LOD3
-7.3 / -5.3 %; under dark grey LOD1 -2.6 / -3.1 %, LOD2 -4.5 / -5.0 %,
LOD3 -11.5 / -8.7 %; `haulier` LOD1 +0.0 / +0.5 %, LOD2 -0.3 / -0.1 %,
LOD3 -3.4 / -3.0 %. Under dark paint the far tiers are darker overall than
LOD0 because LOD0's light unpainted parts (rails and posts, tank, guards,
rims, tape, lamps) shrink to a few texels. LOD2's box keeps both its
rails as unpainted aluminium. LOD3's box sides are one painted face each,
so its rails darken with the paint; freeing them would take triangles it
does not have.

## Per-tier triangle counts

| Tier | Triangles | Ceiling |
| --- | --- | --- |
| LOD0 | 4,490 | 4,500 |
| LOD1 | 1,398 | 1,400 |
| LOD2 | 348 | 350 |
| LOD3 | 60 | 60 |

LOD0: cab group 1,854 (the shell's loft 516 before its cuts, the arches
and recesses about 960, fairing 164, visor 68, fender lips 2 x 44, blades
2 x 28), wheels 1,344 (front 2 x 276, rear 2 x 396), chassis and gear 596
as 35 small solids (the round mudguards 2 x 36), mirrors 2 x 172, box 196,
wings and flaps 96, collars 24, wipers 24, plinth 12. LOD1: cab group 546
(loft 140, fairing 44, visor 20), wheels 304, chassis and gear 288, box
140, mirrors 2 x 24, collars 24, blades 24, wing plates 24. LOD2: shell
92, box 52, headlamp plaques 2 x 24, fairing 20, visor 8, fog lens 4, dark
under-box block 12, bar 12, lamp housings 32 + 28, one hexagonal prism an
axle 2 x 20. LOD3: two extruded profiles, the painted cab and box (7
points, 24) and the dark lower module and under-body (10 points, 36).

## LOD review

Switch distances as the contract's truck row: LOD0 under 30 m, LOD1
30-100 m, LOD2 100-400 m, LOD3 beyond. Reviewed on the review sheet
(75 degree vertical field of view, 1080p, tiers side by side at 30, 100
and 400 m) and in close renders of LOD0-2 from fixed cameras (1280 x 720,
21-28 degree fields of view, the catalog sun): head-on, front
three-quarter and the cab's side, far nearer than LOD1 and LOD2 are used.

- LOD1 keeps the bowed, round-cornered front (one segment a side of the
  bow, two round the corner), the lower module and its ledge, the
  leaning sides, the fairing (three rings), visor (unwrapped), screen
  recess, door glass with its dropped corner, arches, collars, the blades
  as short tail plates, the wings as one plate a side, guards, tank, twin
  width, under-run bar, mirrors and every lamp; loses the chin and the
  rolled bumper edge, the belt's brow and crown, the step wells, grille
  recess, plinth, centre recess and the lamp pods' step (all in the
  texture), the round rear mudguards (a flat guard), the fender lips
  (their dark shape is painted under them, so the colour holds), the
  blades' roots, the visor's wrapped ends, guard brackets, cross bearers,
  AdBlue and air tanks, the panel recess and the roller door's inset
  (both in the texture), and the shaped mirror heads (one block a side);
  the cab's shut lines, flap, handles and inserts are the same texture
  on both tiers.
- LOD2 keeps the box-over-cab massing, the bowed nose (two flat halves),
  the bumper's ledge, fairing (a wedge), visor, the dark lower module and
  under-box mass, wheel positions with the discs showing and the wider
  rear, the dark screen and the pale roof; the wheels go hexagonal and
  the mirrors, collars, blades (their slots stay, drawn) and guards go
  (the dark under-box block's sides carry the far picture's guards and
  tank); the rear is the bar with the two lamp housings over its ends, as
  LOD0's. At 100 m the silhouette holds.
- LOD3: the cab's raked nose from the bumper's top, fairing and box front
  one slope, from pictures at 16 texels per metre, as one painted solid
  (its cab and box in a lighter far paint field, see Paint); the lower
  module and under-body a second, narrower solid on four wheel feet,
  unpainted (B = 0), its front face the bumper with its lamps, its sides
  showing the picture's tyres, silver rims, guard rails and tank in their
  own colours, so it stays dark under any paint. The gap under the box
  front is open.

## Interior geometry

No interior. Hidden faces (validator, inspection candidates): LOD0 187 of
4,490 (4.2 %), LOD1 32 (2.3 %), LOD2 46 (13.2 %), LOD3 1. They are the
faces kept closed 2 mm under or beside another solid, and exterior
surface in a narrow gap: the shell's bottom, the chassis members' and
bearers' tops under the box floor, the tank's and boxes' faces against
the rails, the plinth's back, the mirror arm roots beside the cab, the
box's front wall behind the cab (10 cm off its back, between the
collars), and at LOD2 the dark block's top under the box and the wheel
prisms' middles inside the shell and the block. LOD0's count rose by 34
with the final round's round mudguards and lamp pod steps; those
candidates were not inspected one by one.

## Known simplifications

- No suspension, brakes, tread geometry, steering linkage, front axle
  beam, cab suspension, tow pin, wiper linkage, door handles or grab
  handles in geometry; handles, seams, rivets, hatch, intake grille,
  the chin's intake slots and tread are texture and normal map.
- Panel lines are texture and normal map, not modelled grooves (decided):
  two texels (31 mm) of darkening over a 4 mm groove in the height.
- Chassis members are plain boxes, not channel sections; the solids floating
  2 mm apart is invisible at any use distance.
- The bumper's lamp pods and the recess between them are cuts in one
  rounded volume; their inserts' and rims' relief, the step tread, the
  tow-eye covers, the front flap's field, slot and grab handles, the cowl's
  slats and pivot bosses, the door's handle recess and the grab handle
  behind it are texture and normal map.
- The cab band's texture is mirrored about the centre line, so the two
  wiper pivots' bosses sit symmetrically (0.45 either side) and the
  parallel arms start from them.
- The rear mudguards are four flat facets round the tyre, not a smooth
  curve; LOD1's are flat boxes.
- No tail lift, kerb mirror, roof antenna or plate lamp.
- The door window is one recessed pane with a dropped front corner,
  without a separate quarter light.
- The glass shows no interior (seats, dash, wheel): only the neutral dark
  cab and its vertical falloff.
- Under the studio sun the main mirror head casts a soft dark shape on the
  door window and the door below it (a cast shadow, not geometry or
  texture).

## Texture set

One 1024 atlas, 64 texels per metre in final pixels, supersampled 4x
(`atlas.SS`); albedo per variant, ORM, normal and emission, PNG, external.

- Layout: the large regions in three bands from the bottom; the small
  uniform, lens and plate patches each alone in a 32-texel block on a
  64-texel grid, the bottom-rail strip 20 texels clear of the tyre
  treads, the cab band 186 texels clear of the box regions; the four
  headlamp lens patches in the open field right of the box front, the
  white ones together, the amber one a block away; the fog lens in its
  own block after the plate's.
- At 64 texels/m: box sides (both sides share one mirrored region), roof,
  front, rear; the cab band (268 x 178: U round each plan ring from the
  front centre, mirrored, V up the profile on the centre line from the
  valance to the roof edge, so the bumper's ledge has its own rows) and
  cab roof; the fairing (U round its rings, V up its nose; its back wall
  a plain patch); the bottom-rail strip; grille; tyre treads; door and
  screen glass (stretched within 5 %).
- Deviations: the wheel faces 69 texels/m; the headlamp lenses about 240
  texels/m; uniform patches (chassis black, arch liner, aluminium, tank,
  guard grey, rubber, plastic, step, lamp housing, lamp bezel, mesh,
  mirror glass and body, seal, cab paint) and the other lens and plate
  patches are stretched over their faces, which carries no detail to
  stretch; the LOD3 side, front and rear pictures at 16 texels/m, their
  cab and box in the far paint ids (0.83 linear in `plain`).
- Cab shut lines are two texels (31 mm) of darkening on a 4 mm groove:
  the door all round (its front line straight up to the screen's foot,
  then up the A-pillar, across the top under the roof's rounding and
  along the door line), and the front flap all round (the corner panels'
  lines and one under the brow).
- The face: the flap carries a field recessed 10 mm round the grille with
  rounded corners and a 12 mm bevel (relief only), over it a centre
  intake slot (0.42 x 0.028) with a raised lip between two grab handle
  recesses (0.20 x 0.044, a pull across each); the cowl under the screen
  has vent slats and the two wiper pivots' bosses. The fairing's front
  carries a field recessed 8 mm with rounded corners and a 16 mm bevel
  (relief only), following the nose's width.
- The lower module: gloss black inserts with a proud, lighter rim round
  the headlamp units (40 mm) and the fog lamps (20 mm), a moulded rim
  round the centre recess, tow-eye covers (68 mm squares) between pods
  and recess, a ribbed non-slip tread across the middle metre of the
  bumper's top (rolled edge and ledge), the chin's intake slots, a dark
  surround under the plinth.
- The side: the door handle a pull across a rounded dark recess (0.18 x
  0.08), a dark grab handle in a shallow recess behind the door (z 1.25
  to 1.80), the step wells drawn dark with a light tread edge under
  LOD0's cuts, the step patch ribbed both ways.
- Drawn for the tiers that do not model them: the grille, the recess
  between the lamp pods, the plate, the step wells, the fender lips, the
  slots behind the blades, the door glass (LOD2).
- Relief in the height channel: box panel joints 1.5 mm, rivets 1 mm,
  roof bows 4 mm, roller door slat grooves 4 mm, its bottom rail 4 mm and
  lock 12 mm, cab shut lines 4 mm, the grille's field 10 mm, grille slats
  8-10 mm, intake slots 10-12 mm, handle recesses 12-14 mm and their pulls
  10-12 mm, insert rims 4 mm, tread ribs 3 mm, tank straps 4 mm, wheel
  nuts 8 mm, reflector bowls 4 mm, tread grooves 8 mm, rim edges 4 mm;
  glass flat.
- Padding by `atlas.pad()`.
- Mip review: whole-atlas mips 3, 4 and 5 (`scripts/review_atlas_mips.py`,
  linear-light box filter) rendered on LOD1 (mip 3, about 100 m) and LOD2
  (mips 4 and 5, about 200-400 m) from the front three-quarter, the rear
  three-quarter and above, again after the second round (new fog lens and
  reflector patches, chrome dividers in the lens patches). No leak of the yellow tape, the amber
  or red lenses or the dark chassis into the painted panels at any of the
  three levels; the headlamps stay white with their amber ends; the tape
  softens into its own aluminium as it should. Consumer filtering pending.
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

- Validator (`vehicle_truck`): 0 FAIL; WARN only for a folder outside the
  catalog tree while the asset is reviewed as a copy.
- Review sheet looked at: views, both steering angles (wheels clear the
  arches, fender lips and wings), every lamp group lit alone, the night
  set, the lit cabin, ids, white, dark grey and red paint, the tiers at
  30, 100 and 400 m.
- Two rounds against the committed build before each (see Revision log),
  every build shot from the same fixed cameras (head-on low, front
  three-quarter low, raised and close, side, cab side, rear
  three-quarter, top, and close-ups of the face band, lower module,
  headlamp, corner blade and fairing; white, dark grey, red and the
  livery) and compared with the snapshot of the build before.
- Light-fringe sweep in close renders under dark grey and red paint: the
  bumper's ledge and the cab's foot, grille and field, blades and slots,
  step fairing and wells, fender lips, lamp pods and recesses, screen
  surround. None found.
- Mip stress renders at mips 3-5 (Texture set).
- Tier brightness rendered under white, red and dark grey paint and the
  livery (Paint).
- Glass and paint measured; lens rectangles, glass texels and pairs pass.
- A generic composite: no make, badge, signature grille or livery.

Pending in the consumer: wheel spin and steer about the sidecar axes,
lamp and cabin control by id, paint through B, mip filtering at distance,
LOD switching, performance.

## Tooling versions

Blender 5.3.0 (2026-11-11); Blender MCP extension not used for this build
(headless scripts only).

## Revision log

- 2026-11-21, final round. Headlamp and fog lenses back from near white to
  bright silver: a field of about sRGB 200, each reflector a soft bowl to a
  darker heart with a small bulb cap, light chrome dividers, the daytime
  strip only subtly lighter (were lenses of 198/176 with 236-247 strip
  and dividers and light ribs). The lamp pods' rim a real step at LOD0
  (14 mm wide, 6 mm deep). Two wiper pivots under two parallel arms (were
  three bosses). A recessed field on the fairing's front. LOD0's rear
  mudguards round the twins (were flat boxes). Fender lips five segments.

- 2026-11-21, second shape round. Face: a brow at the belt (the front
  panel now leans 5 mm forward to it and tucks 35 mm back to the screen),
  the front flap with a recessed field round the grille, a centre intake
  slot, two grab handle recesses and its shut line under the brow, cowl
  slats and pivot bosses. Lower module: gloss black inserts with proud
  rims round the lamp units, a moulded rim round the centre recess, a
  ribbed step tread on the bumper's top, tow-eye covers, the plate on a
  plinth (was a recess), a pair of fog lamps in the chin (lamp 10; 29
  lenses, were 27). Headlamp lenses redrawn with nothing darker than the
  lens inside a unit: light chrome dividers and light ribs in place of
  the mid grey rims and dark flutes. Corner blades reshaped: body colour,
  rooted in the front panel, a tail standing 48 mm off over an open dark
  slot (were free-standing dark plates). Visor wrapped round the corners.
  Fairing: one smooth convex rise from 44 to 22 degrees to z 3.535 (was a
  dome to 3.485), flaring to 2.44-2.49 at the back by the box corners
  (was 2.32); collars up to its overhang. Cab side: widest at the belt
  (2.324), a recessed door handle, a grab handle behind the door, the
  back wall dark. Wheels: deeper front dish, hub cone, ten nuts on the
  disc. Tank straps as rings; a reflector in the right rear lamp unit.
  LOD1: blade tails and wing plates restored. LOD2: the bumper's ledge in
  geometry, the front wheel discs showing, one prism an axle. Paid for by
  one roof ring, chamfered rear cab corners, the front wheels' hidden
  inner shoulder, rail and subframe as one member, the gearbox block,
  square mirror tubes, six-sided axle housings, LOD1's guard brackets.

- 2026-11-21, shape round: the cab and bumper rebuilt as one loft of plan
  rings. Front bow 110 mm (was 60) with the corner arcs starting on its
  tangent; front corner radius 0.24-0.22 below the belt and 0.15-0.13 at
  the pillars (was 0.18 throughout); sides leaning in 3.4 degrees above
  the belt (were upright); screen raked 10 degrees (was 8.5), a trapezoid
  with 0.09 corner radii in a dark surround (was a rectangle); the door
  glass larger with a dropped front corner and a raked front edge; a
  trapezoid grille. The bumper, 0.40 tall and 40 mm proud, became a lower
  module 0.62 tall, 85 mm proud with a 55 mm ledge, a set-back chin, a
  recess between two lamp pods, corner radius 0.22 (was 0.15), wrapped
  into the step fairings; headlamp units 0.43 x 0.25 (were 0.38 x 0.18)
  with fluted reflector lenses mapped whole. New: corner blades, cab side
  collars (the upright extender boards went), the front mudguards' rear
  quarters with flaps, a moulded fairing with a convex nose in place of
  the five-section wedge, a bowed visor, rounder mirror heads as separate
  solids (368 triangles, were 494), a lock, bottom rail, guide tracks and
  pull strap on the roller door. Brackets hidden behind the tank and
  boxes, the front axle beam and one cross bearer went to pay for it; the
  rear twins' hidden inner shoulder too. LOD2's box keeps its top rail
  unpainted. Tank, battery box and side guards moved 40-120 mm back,
  clear of the front wings.

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
