# estate_compact

## Style brief

A generic Nordic everyday family estate of 2005-2020: a compact (C-segment)
five-door station wagon with a long flat roof on two rails, an upright
tail over a rounded bumper, three side glass groups closed by a thick
body-colour D-pillar, a short crowned bonnet falling to a rounded,
leaned-back nose, a clear cowl step, and 16-inch alloy wheels. A composite
with no recognisable make: no badge, script or signature grille, conventional
lamp shapes (headlamp units swept back along the wings to an amber end, a
plain slatted grille between them, wrap-round tail clusters), black window
surrounds, black sill trim and bumper lips, and one dark line round the car
at door-moulding height (rub strips on the bumpers' corners, mouldings on
the doors). Moderate Nordic road film: darker
lower body and spray behind the wheels, a dusty lower tailgate; not
neglected.

## Body class

`car`, box 4.50 x 1.80 x 1.95 m, mirrors 0.12 m a side.

## Dimensions

| | Target | Built |
| --- | --- | --- |
| Length | 4.48 | 4.480 |
| Width without mirrors | 1.78-1.80 | 1.790 |
| Width with mirrors | 2.04 max | 2.020 (0.115 a side) |
| Height over the rails | about 1.47 | 1.468 (body roof 1.446) |
| Wheelbase | 2.65 | 2.650 |
| Track | 1.54 | 1.540 |
| Front / rear overhang | 0.86 / 0.97 | 0.860 / 0.970 |
| Wheel radius / tyre width | 0.32 / 0.205 | 0.320 / 0.205 (0.207 over the rim lip) |
| Ground clearance (lowest body point) | n/a | 0.190 (front lip); sills 0.23 |

Belt 0.92 at the A-pillar foot rising to 1.065 at the quarter glass, sill
bottom 0.23, side glass top 1.345-1.36, windscreen 27 degrees from
horizontal (cowl 1.01 m at s 1.27 to header 1.40 at s 2.05), tailgate glass
about 35 degrees from vertical. The bonnet's leading edge is 0.80 high and
0.125 behind the bumper's foremost line (0.53 high) on the centre line. The
body is 1.79 wide over the wheel arches and 1.768 along the doors. A
1.8 m figure stands beside the car on the review sheet: the roof comes to
its chin.

## Construction

`estate_shape.py` holds the whole shape as plain face lists (numpy only), so
the atlas generator and `build.py` read one description.

- **Body**: a closed shell lofted through 19 stations along the length
  (`key_stations()`), each a loop of up to 13 rows a side (sill to belt,
  then glass bottom over the roof to the centre line). Station points carry
  their own s, so a station bends where a pillar leans. Behind the
  windscreen's header the roof keeps three rows only (edge, the row under
  the rails, centre line); the rows it drops end at the header as points
  of the first roof cells, and the roof runs straight from the B-pillar to
  the C-pillar. One station crosses the windscreen between cowl and header.
  Front and rear are grids ("caps") whose rows are the side rows and whose
  columns are the top rows laid round the plan corner, with three extra
  corner columns (`K1`-`K3`) carried by the end stations only, so the
  corners and lamps are cells of one grid. The windscreen bows 12 mm
  outward, the roof is crowned and falls 0.05 to the rear, the side glass
  leans in about 21 degrees above a painted belt shoulder carrying an 18 mm
  waist seal.
- **Section** (`W_MID`, `Z_MID`, `hw()`): the doors have a section of their
  own, bottom to top. The black sill cover leans out 18 degrees from its
  foot (0.826 at 0.23 m) to its top edge (0.857 at 0.325), which stands
  11 mm proud of the door's foot (0.846 at 0.40): the cover is a surface of
  its own under the doors' lower edge. The door's lower zone leans out 9
  degrees to a soft break at 0.60 (0.877), above which the skin is crowned,
  fullest (0.884) at 0.78 and back to 0.878 at the shoulder crease 65 mm
  under the belt (row `S5`). A row of the doors and the rear quarter only
  (`SD`, carried by the stations from the cowl to the D-pillar, ending as a
  point of the cells beside it elsewhere) sits 45 mm under the crease and
  6 mm proud of the line between its neighbours, so the skin swells under
  the crease and rolls in to it over the last 45 mm; above the crease it leans in 40 mm to the belt
  (32 degrees) and a further 22 mm of painted shoulder to the glass. The
  crease is a real break along the doors and the rear quarter:
  `crease_edges()` hands its edges to `build.py`, which marks them sharp
  from behind the front arch to the D-pillar; forward of the front door
  the row runs on smooth to the headlamp, so the crease fades into the
  wing. In plan the body tapers toward both ends (`TAPER_F`, `TAPER_R`: the
  belt by 34 mm at the nose and 40 mm at the tail, the crease by 20 and
  30 mm; the nose's rows keep their own widths, which the lamps' cells are
  laid out on), and the rows from the sill's top to just over the arches
  stand 8-22 mm proud round each wheel (`FLARE`: the rows the arches cut
  fall off over 0.42 m, so the lips stand proud at the arches' sides too;
  the rows above over 0.32 m). The row over the arch tops (`S4`) is not cut
  away by the arches and carries the full 1.79 width at both axles.
- **Ends** (`CAP`): each cap row has its height on the centre line and at
  the side, its setback from the bumper line, a bow across the face, the
  distance at which it reaches the body side, and the exponent of the
  superellipse that turns its corner, so every row is one smooth plan
  curve, tangent to the side.
- **Nose**: the black lip tucks 0.105 under at 0.19 m and the lower valance
  (the intake's and the fog lamps') leans back 17 degrees from 0.27 to
  0.40 m, under an upright face that carries the plate and is fullest at
  0.53 m (row `S3`), bowed 45 mm across and turning a corner that reaches
  the side 0.36 behind the bumper line (half-width 0.77 at 0.10 behind it,
  exponent 3.8); its top rolls back to a shelf (0.595 to 0.622 m, setback
  22 to 62 mm) under the lamps and the grille. Those lean back 20 degrees
  from vertical on the centre line and 37 degrees at the outer lamp, to
  the bonnet's leading edge 0.80 m high and 0.125 behind the bumper line,
  which in plan sweeps back to 0.16 at the lamp's inner corner (x 0.435),
  0.26 at x 0.705 and reaches the wing top 0.46 behind the bumper line.
  The lamps' foot climbs from 0.622 at the grille to 0.70 at the side,
  where it runs on as the shoulder crease. A roll station 4 cm behind the
  leading edge (`FR`) turns the bonnet's lip up at about 30 degrees before
  its 10-degree run to the cowl, so the edge is rounded in silhouette; the
  same station's side rows stand 6-10 cm behind the nose's and rake, so the
  first side cell under the belt is the headlamp's blunt end on the wing
  (0.56 behind the bumper line at the shoulder, 0.46 at its foot). The
  bonnet is crowned across (0.10 x squared, a soft raised centre); the wing
  tops roll down from it to the belt.
- **Tail**: the bumper is fullest at 0.52 m, bowed 45 mm across, tucked
  18 mm at its foot, its top rolling 40 mm forward at 0.64 m under a
  tailgate panel that leans 22 degrees to the lamps' foot (0.80) and 26
  degrees above it, so the panel is crowned. The
  clusters' foot climbs to 0.85 and their top from 0.975 to 1.00 round the
  corner, their inner edge leans out with the tailgate's opening line, and
  each runs out to a point on the shoulder crease beside the D-pillar. The
  glass is 1.25 wide at its foot and 1.17 under the spoiler lip, which
  overhangs it by about 3 cm; plan corners squarer than the nose's
  (exponent 3-4).
- **Pillars**: the A-pillar is a constant 0.08 m band beside the windscreen
  edge; the side glass's front edge runs parallel to it from a small black
  mirror patch (sail) at its foot. B black-out 0.10 constant, C black-out
  0.16 at the belt to 0.10 at the top, D body colour 0.19 at the belt to
  0.13 at the roof. LOD1 keeps the same A-pillar line (the sail merges into
  its front door pane).
- **Lamps, panes, plates, front fog lamps** are whole grid cells or bilinear
  sub-cells (`inset()`); `build.py` conforms the T-junctions away and deletes
  any edge left without a face. The headlamp's end is the first side cell
  under the belt, the tail lamp's tip a triangle cut from the last. The
  plates sit 12 mm back in shallow recesses with black walls (LOD0). The
  front fog lamps are their own faces (no lamp id) in pods beside the lower
  intake; each pod is the rest of the lamp's grid cell, an unpainted dark
  face, so its leaning edges are the mesh's own.
- **Wiper, tailpipe, aerial**: three small closed solids of their own
  (LOD0): the rear wiper's blade, one dark bar 0.42 long a few millimetres
  off the tailgate glass above its foot (its arm and pivot are drawn on the
  glass, as dark as the printed band); the exhaust, a six-sided prism
  tucked up under the rear bumper on the right (x -0.46, 0.20-0.25 m high), dark
  from under the floor back to a bright tip 9 cm long (the mirror's
  metallic patch), its ends dark; and the aerial's fin on the
  roof's rear centre line, a dark wedge 0.15 long and 45 mm high, lower
  than the rails.
- **Wheel arches**: exact boolean difference (`asset_build.difference`,
  snapped) of a prism per arch (radius 0.37, centre 15 mm above the axle, 18
  arc segments at LOD0, 5 at LOD1) reaching in to the liner wall at
  |x| = 0.465; its faces stay as the dark closed liners. The arch lip is
  painted relief.
- **Mirrors**: separate closed solids lofted outward from a slim arm on the
  sail (x 0.80-1.01; the arm 3 x 3.5 cm), an eight-sided housing rounded
  toward its front and tapered over its last 5 cm to an end half its
  section, a dark mirror face (not a glass id) and the side repeater
  across the front of the outer end. The sail patch under it maps to a
  uniform black patch of its own, so its outline is the mesh's edge at any
  distance. LOD1's mirror is one tapered six-sided section with its whole
  rear face dark, so it reads as a mirror from behind like LOD0's.
- **Roof rails**: closed solids at x +-0.525 floating about 10 mm over the
  roof, their ends dipped into it as feet.
- **Smoothing**: smooth shading throughout; edges are sharp past 50 degrees,
  where glass meets anything else, where unpainted trim meets paint, and
  along the shoulder crease.
- **Front** toward -Y; origin on the ground at the centre of the body's plan
  box (mirrors excluded), one origin for every tier.

## Wheels

Four parts (front left/right steering, rear left/right), radius 0.320,
width 0.205, each a closed solid with its origin at the wheel centre and a
tread corner at the very bottom. LOD0: 16 sides, a revolved profile (tread
from the flat inner face, a rounded outer shoulder, the sidewall down to a
rim lip standing 2 mm proud at r 0.226, the dish's wall 38 mm deep to
r 0.208, and the spoke face rising from there as a cone to the hub's flat
cap, 24 mm proud of the dish's floor at r 0.064: rim face about 0.66 of the
radius, sidewall 0.10), 188 triangles each, every vertex inside the
wheel's cylinder (radius 0.320, x -0.1025 to 0.1045). One wheel face picture for all four wheels and every tier:
five silver spokes over near-black openings, a dark gap at the bead, a bright
lip, a hub with cap and nuts; alloy as metallic 0.85, roughness 0.35, the
openings rough and nonmetallic, rubber 0.88, the tread's crown worn lighter.
LOD1: 8-sided prisms carrying the same picture. LOD2: each axle one 5-sided
prism through the body (part 0). Arch clearance: 37.5 mm (LOD0) and 12.0 mm
(LOD1) with the front wheels turned 35 degrees (validator); liner wall clear of the
turned tyre by design (`check_layout()`).

## Ids

`COLOR_0` normalised UNSIGNED_BYTE VEC4 on every tier (validator: whole ids,
one R, G and B per triangle, A 255). LOD0/LOD1: parts 0-4, lamps 1, 2, 3, 4,
5, 6, 7, 8, 9, 11, glass 32-35. LOD2: part 0, lamps 1, 3-9, 11 (no 2, see
Lamps), glass 32-35 with the side glass as one band a side tagged 33. LOD3:
part 0 and paint only.

## Lamps

20 lenses, measured from LOD0 into the sidecar:

- Front, each side, one unit under the bonnet's edge, from the grille's post
  out: high beam (8), low beam (7), and the indicator (4/5) in the end on
  the wing, with the daytime lamp (9) as a strip along the foot of the high
  beam. The unit is 0.175 high at its slanted inner edge (parallel to the
  grille's side, 5 cm from it), 0.13 at mid-length and 0.11 where it turns
  onto the wing, and ends bluntly there on a raked edge, 0.46 behind the
  bumper line at its foot and 0.56 at the shoulder; seen from the front it
  spans x 0.355-0.86. The grille between the units is an inverted
  trapezoid 0.77 wide at the bonnet's edge and 0.61 at its foot, 0.178
  high, foot and top level with the lamps'; the lower intake repeats its
  shape (1.00 wide at the top, 0.84 at the lip) between the fog lamps'
  pods.
- Mirrors: side repeaters (4/5) across the housings' outer ends.
- Rear, each side, one cluster on the quarter, outboard of the tailgate's
  opening line: indicator (4/5) over reverse (6) on its inboard end, tail
  and brake (3) on the corner, a tail (1) section wrapping onto the side
  and running out to a point on the shoulder crease; z 0.80-0.975 inboard,
  0.85-1.00 at the corner.
- High-mounted brake (2) across the spoiler lip, 0.33 x 0.03, centred.
- Rear fog (11) low in the bumper on the left; a red reflector (no id) in
  its place on the right.

Unlit lens colours: red (128, 28, 26), amber (196, 112, 30), clear
(172, 175, 174) sRGB; lit as `vehicle_ids.LENS_LIT`. Headlamps: a light silvery
housing behind the clear lens (its own id `hl_chrome`, sRGB 206, roughness
0.25, metallic 0.55), darker under its roof. The high beam is a fluted
reflector bowl, wider than tall, its flutes upright and lighter toward its
foot, with a small bulb shield; the low beam a projector's glass lens (the
clear lens colour at 0.6-0.74, shaded below its cut-off) in a square
shroud; the daytime strip a pale lens with a lighter light guide following
the foot; the indicator a ribbed amber cell out to the end. No ring round
a dot, no dark housing, no painted glints. The bowl and the shroud are
sized from each cell's mean height and set on its centre of area. A unit's
cells are parted by fine dark joints and its dark outline is drawn along
its own outer edges (`unit_edges()`: the edges no other face of the unit
shares), two lens texels wide, so it follows the slanted inner end and the
raked end; the tail clusters are outlined and parted the same way, with
ribbed red cells crossed by a lighter light guide, a ribbed amber cell and
a clear ribbed reverse cell. LED dots in the high-mounted lamp; a one-texel
dark outline round the lenses that stand alone; glossy in the ORM only
(roughness 0.12). Every lens rect is lit in full in the emission. LOD1
keeps every lens (its brake and fog lamps are shrunk insets of coarser
cells; it has the roll station, so its headlamp's end is LOD0's cell);
LOD2 keeps all but the high-mounted brake: its lens is a 3 cm strip on the
spoiler lip, which LOD2's roof end does not have, and a face inside that
rectangle would cost about 22 triangles of the 4 it has spare (WARN,
recorded); LOD3 none. The headlamps and fog lamps (cells, pictures and
materials) are as accepted; later work on the body left them unchanged.

The housing's metallic was tried at 0.30, 0.55 and 0.85 under the preview's
flat grey world: the unit's mean brightness in a close render fell from 164
to 159 to 149 (8-bit), 0.85 reading grey and flat, so 0.55 stays.

## Glass

Groups 32 windscreen (1.20 m2), 33 front door (0.41), 34 rear door and
quarter (0.81), 35 tailgate (0.40). Separate faces on their own UV islands;
LOD2 merges the side glass into one band a side, tagged 33. Measured over
the glass texels: sRGB 51 mean, roughness 0.080, metallic 0.

### Glazing treatment

Departure from `glazing.rooms()`: its lit far-wall patch read as a stain on
a windscreen, so `vehicle_glass()` paints each pane (found with glazing's
own components) neutral dark (52, 56, 60) with a gentle 0.86-1.08 falloff
toward the pane's foot, a per-pane level of 0.92-1.06 and glazing's grain.
No privacy glass. The windscreen and the tailgate glass carry a printed
black band round their edge with rounded inner corners (`frit()`: 4 texels
wide with an 8-texel corner radius on the windscreen, 5.5 and 12 on the
tailgate, the glass's albedo at 0.42), so the panes read shaped although
their faces are plain quads; it is still glass (same ids, texels, gloss
and emission). The emission's cabin is `glazing.night_rooms()` at 0.25 on
the glass texels; partly covered texels are black.

## Paint

Painted panels (B = 1) are neutral grey 228 sRGB before wear (chroma 0.1):
the panel field (the area-weighted median of the painted texels, LOD0 and
LOD1) measures 0.761 linear, level with the catalog's other vehicles. The
tiers keep one brightness under one paint: the area-weighted mean of the
albedo the painted faces sample is, in linear, LOD0 0.705, LOD1 0.695
(-1.4 %), LOD2 0.676 (-4.2 %), LOD3 0.711 (+0.8 %). LOD2's sides start at the
sill's top, so they never sample the black sill, and the wheel pictures they
show in the arches are a large light rim in a thin dark tyre with the arch
gap left as paint. LOD3's painted faces sample a uniform light block (shaded
to the tiers' level); its dark parts are unpainted faces. Panel gaps (doors,
tailgate, fuel flap, the front bumper's joint from the headlamp's end to
the arch, the rear bumper's joint, roof hinge) and the bonnet's shut lines
are 13.5 mm (1.7 texels) dark gap lines, albedo at 0.10 of the paint (about
sRGB 70 on the light field), a 4 mm groove (6 mm on the bonnet's lines,
with a 1.5 mm raised lip on the bonnet's side). The bonnet spans nearly
the car's width: its front line runs just behind the leading edge, over
the grille and along the lamps' tops out to the middle of the low beam
(x 0.705),
and each side line runs from there back along the wing's top, nearly
parallel to the car's length (x 0.705 at the lamp, 0.72-0.73 along the
bonnet, 0.09-0.10 inboard of the wing's crest), curving in over its last
0.15 to the windscreen's base corner just inboard of the A-pillar's foot
(x 0.705), where it meets the bonnet's rear edge at the cowl; the wing
shows as a strip about 0.10 wide outboard of it. The lines are texture and normal
map only, no modelled grooves; the bonnet strips ahead of the cowl stay in the top island so
the side lines run straight to the windscreen. The waist seal is relief and darkening on the paint. Each door handle is
a raised grip across a scallop dished 12 mm into the door, 10 cm under the
shoulder crease (height and a soft shade, darker under its upper edge),
deep enough to read in the catalog's light. The doors' lower break at
0.60 m is pressed deeper in the height channel than the mesh has it (the
skin 4 mm in below the line, over a 3 cm turn, fading out at the doors'
ends), so it reads as a soft pressed line above the mouldings.
The doors' frames are drawn too: their shut line to the roof above the
window seal, the doors' lower edge over the sill cover (0.337 m), and the
door gaps carried up the B- and C-pillars' black-outs as lighter lines;
the black-outs are satin (sRGB 26, roughness 0.42), apart from the glossy
glass. Painted
on the panels in dark trim grey (so they take a paint colour as near
black): the side mouldings and the bumpers' rub strips, one line at
0.462-0.50 m from the nose to the tail, broken by the arches; an 8 mm trim
edge round each wheel arch inside the body's raised, rolled lip (it also
rounds the cut's facets); the plates' holders, 2 cm larger than the
plates, with a light patch inside for LOD2's bumper faces; the tailgate's
handle recess under a raised body-colour garnish; the
black trims (sill, lips, slim cowl, grille, intake, B/C pillars) are
unpainted faces, and the mirror sail is unpainted satin black (sRGB 24,
roughness 0.62). Trim and glass faces are rastered grown by a true offset of
1.3 (glass 1.2) texels all round their outline, so even a thin sliver face
(the sail's wedge under the mirror) samples its own colour and never picks
up a light fringe. Plates are blank white 0.52 x 0.11 with
a thin dark border, unpainted, each one face group mapped whole onto one
plate rect (no mirror seam). The preview multiplies the paint by linear
(0.22, 0.30, 0.40).

## Per-tier triangle counts

| Tier | Triangles | Ceiling |
| --- | --- | --- |
| LOD0 | 2990 | 3000 |
| LOD1 | 880 | 900 |
| LOD2 | 216 | 220 |
| LOD3 | 40 | 40 |

LOD0: body shell about 1474 before the arches and 1894 after them, four
wheels 752, mirrors 2 x 110, rails 2 x 36, wiper 12, exhaust 32, fin 8.
The nose's corner columns, the roll station, the stations round the
arches, the plates' recesses, the eight-sided mirrors and the three small
solids were paid for with the roof's spare rows, the mid-door and second
windscreen stations, one row along the bonnet's centre and two rail
sections. LOD1 (body 696, wheels 4 x 28, mirrors 2 x 22, rails 2 x 14): 13
stations, the roll station among them, rows sill top / over the arches /
shoulder crease / belt / glass top / roof edge / centre, so it keeps the
crease (marked sharp along the doors, as on LOD0) and the bonnet's rolled
edge; the same nose rows as LOD0 less the lips' lower edge and the
valance's break, the same tail rows less the lip's edge, four columns a
side on each end, the headlamp's end and the tail lamp's tip as on LOD0,
8-sided wheels, one-section mirrors, triangular rails, 5-segment arches,
flat plates, no wiper, tailpipe or fin.
LOD2: 5 stations, rows sill / belt /
glass top / centre (the sill carries the width), a nose of the bumper face
in three cells a side turning the corner, leaning back to the lamps' foot,
and the lamp band to the bonnet's edge, the tail's lamp rows, two axle
prisms; its sides start at the sill's top (0.30), the prisms showing under
them. LOD3: the side profile (11 points:
nose (0.53 high), bonnet edge (0.125 back, 0.80 high), cowl, header, roof
end, glass foot, tail, tail foot, two wheel contacts, chin) extruded across the width; each side cut along those
points into three polygons (2 + 5 + 2 triangles, the plain extrusion's 9):
the glasshouse (cowl, header, roof end, glass foot) and the lower strip
(chin, wheel contacts, tail foot) unpainted and dark, the body between
painted; the windscreen, rear glass and the three underside quads unpainted
and dark, the other perimeter quads painted.

## LOD review

Contract distances (75 degree vertical FOV at 1080p): LOD0 under 30 m,
LOD1 30-100 m, LOD2 100-400 m, LOD3 beyond. Reviewed on the review sheet's
tier rows at 30, 100 and 400 m and in close-ups: LOD1 keeps the stations,
glasshouse, pillars, rails, mirrors and arches; LOD2 keeps the two-box
silhouette, bonnet step and windscreen slope, the wheels as dark prisms
under painted wheels in the side texture; LOD3 keeps the bonnet step and
both glass slopes, a dark glass band and a dark lower strip on plain body
colour. The tier switches checked for brightness and colour under white,
dark grey and red paint at 100 m and 400 m, with full textures and with
mips 4 and 6 (`review_atlas_mips.py`): no brightness jump at LOD1-LOD2 or
LOD2-LOD3. Known transition limits: LOD1's front lip sits at the sill-top row
(0.27 instead of 0.19, about 2 px at 30 m), it has no break at the
valance or low on the doors, and no wiper, tailpipe or fin; LOD2's body
bottom at 0.30;
LOD2 loses the arches (painted) and the high-mounted brake lamp; LOD3 has no
wheels, only the dark lower strip. Runtime switching and performance are pending in
the consumer.

## Interior geometry

Validator hidden-surface test: LOD0 13/2990 (the roof rails' buried feet, the fin's foot and the exhaust's top), LOD1 0, LOD2 22/216 (the middles of the
axle prisms inside the body, kept: one prism per axle is cheaper than two
wheels), LOD3 0. No seats, no interior.

## Known simplifications

Textured, not modelled: panel gaps, bonnet shut lines, handles, side
mouldings and rub strips, window and waist seals, the glass's printed
bands, the grille's frame and slats, the lower intake's frame and mesh,
the plates' holders, wipers (on the cowl), fuel flap
(right rear), arch lips and their trim edge, bumper joints, the front
lip's chamfer, the tailgate's handle recess and garnish. The grille's and the intake's frames are rails along the top and the foot
of their cells; their leaning sides are the mesh's own edges. No washer
jets, tow eye or brake discs. Glass is
opaque. Wheels have no tread geometry and no hub geometry. LOD2 shows the
wheels' upper parts as painted pictures on painted side faces, so their rims
take the body colour at 100 m and beyond.

## Texture set

One 1024 atlas at 128 texels/m (the owner's decision for every vehicle
class): albedo `plain`, ORM, normal, emission and `glass_texels.png`, all
1024, no alpha. The layout is the 512 one scaled by 2 (`SC`), the pictures
the same, painted crisper (panel gaps 13.5 mm, thinner seals).
Local densities above that: the lamp rects at 224 texels/m (1.75x, each
centred in its own 192 x 96 cell) and the wheel face at 294 texels/m
(192 x 192, shared by all four wheels), because they are small in area and
carry the car's face. Islands (`estate_shape.py`, `R_*`): both
sides unmirrored (s, z), top mirrored (s, |x|), front and rear mirrored
(|x|, z), each face choosing by its normal; glass on its own islands (side
mirrored, windscreen and tailgate whole, LOD2's band apart); lenses on rects
packed from LOD0's lens extents (left and right share one, mirrored);
plate, front fog lamp, wheel face, tread, mirror, rail, reflector,
under-body patches and LOD3's three uniform 64-texel blocks (paint, dark
glass, under-body). The layout keeps the paint islands on 64-texel blocks
apart from every dark or coloured patch (a free block between), so the
minified atlas does not bleed lamp or trim colour into paint. Every tier's face is mapped by the same projections, so the
tiers share the artwork. The projected islands start as paint; texels no
LOD0 face uses carry LOD2's pictures (light wheels in the arches, shadow
under the sills). Deviations: the under-body patch and LOD3's blocks carry
no density (uniform colour); 45-degree faces stretch up to 1.4x in
their projection. Painted with `scripts/atlas.py` at SS 4; heights for the
normal map: panel gaps -4 mm (the bonnet's lines -6 mm with a +1.5 mm lip), handle grips +8 mm over scallops -12 mm, the doors' lower break -4 mm, side mouldings +6 mm and rub strips +5 mm, arch
trim +2 mm and lip +4 mm, plate holders +4 mm, the tailgate's recess -6 mm
under a +6 mm garnish, headlamp bowls -5 mm, grille slats +4 mm over a -6 mm grille, intake mesh, rim lip and hub
+3 mm, spoke openings -12 mm, tread grooves -6 mm; glass and lens faces flat
(0.5 mm ribs on amber and red); cavity darkens grooves. Weathering
through `scripts/weathering.py` at the moderate level (grime, road film
falling off over 0.2 m above the sills, spray behind each wheel, bumper and
tailgate wake dust; dirt resolved to its neutral steel dust so the paint
stays neutral). The weathering module's noise is sized in texels, so its
blotches are half the physical size they were at 512.

### Mip review

`scripts/review_atlas_mips.py` at mips 4 and 6, rendered on LOD1, LOD2 and
LOD3 from the exported tiers in white and in dark grey paint, front and rear
three-quarter: no lamp red or amber bleeds into paint, the black trims stay
inside their parts, the headlamps stay light against dark paint, and the
white plate greys toward its border at mip 4 and beyond (it averages with
its dark rim; it is a 3-pixel feature at those distances; the plate's rect
sits in a white block so it stays light). The wheel faces average to a mid
grey at mip 6. LOD3's faces each sample one uniform block, so its mips keep
paint, glass and under-body apart. The atlas's rects and blocks are the
ones the earlier 512 and 1024 reviews (mips 3 to 6) passed; the pictures
inside them changed with the shape, and the set was rendered again on the
current textures.
Consumer filtering is pending.

## Variant list

`plain` (paint true): the only variant; the consumer paints the body.

## Export

Every tier: one mesh, one material (albedo to base colour, ORM to
roughness/metallic and occlusion, normal map at scale 1, emission bound with
factor 0), external PNGs with no `bufferView`, `COLOR_0` as exact bytes, no
other attribute; `asset_build` export options (yup, selection only, keep
originals, apply, Draco and meshopt off). Rebuild:

    python3 estate_atlas.py export
    blender --background --python build.py

`build.py -- facts` rewrites the sidecar alone from a committed tree.

## Review status

Done here: validator (0 FAIL; WARN for LOD2's brake lamp, and for
`source.dirty` until the tree is committed); review sheet
(`scripts/review_vehicle.py`): side, front, rear, top, three-quarter,
steered wheels, each lamp group, night set, cabin, ids, white/dark grey/red
paint, tiers at 30/100/400 m; fixed-camera sets of LOD0 in white and
blue-grey paint (orthographic side, front, rear and top; head-on from 0.95 m;
front three-quarter from eye height, raised and close; rear three-quarter
low and raised; a low side perspective, a front-quarter view along the
flank, and the side under a sun 10 degrees above the horizon from ahead
and from behind) after each change to the shape, with the head-on and front
three-quarter frames judged every time; close-ups of the face, a
headlamp, the front bumper, the tail from the quarter and from behind, a
front wheel in its arch (dark liner, an even gap of about 0.05, the trim
edge), and a mirror with its sail patch from the front and from behind (no
light fringe, a clean edge); the same frames without textures on a plain
glossy grey, for the nose corners' shading (no facets) and the flank's
highlights; all four tiers from the front and rear three-quarter, head-on
and side; the mip set above. Before any build the face lists were checked
without Blender: each tier's shell closed once its T-junctions are
conformed, every tier on LOD0's plan box, LOD1's and LOD2's lamp faces
inside LOD0's lens rectangles. Pending in the consumer: runtime LOD
switching and mip filtering, lamp intensities and cabin lighting, paint
colours on the real shader, tangents for the normal map, performance.

## Tooling versions

Blender 5.3.0, headless (`--background`); the MCP addon was not used for
this asset.
