# estate_compact

## Style brief

A generic Nordic everyday family estate of 2005-2020: a compact (C-segment)
five-door station wagon with a long flat roof on two rails, an upright
tail over a rounded bumper, three side glass groups closed by a thick
body-colour D-pillar, a short crowned bonnet falling to a rounded,
leaned-back nose, a clear cowl step, and 16-inch alloy wheels. A composite
with no recognisable make: no badge, script or signature grille, conventional
lamp shapes (slim headlamp units swept back along the wings to an amber tip,
a plain slatted grille between them, wrap-round tail clusters), black window
surrounds, black sill trim and bumper lips. Moderate Nordic road film: darker
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
0.125 behind the bumper's foremost line (0.515 high) on the centre line. The
body is 1.79 wide over the wheel arches and 1.766 along the doors. A
1.8 m figure stands beside the car on the review sheet: the roof comes to
its chin.

## Construction

`estate_shape.py` holds the whole shape as plain face lists (numpy only), so
the atlas generator and `build.py` read one description.

- **Body**: a closed shell lofted through 20 stations along the length
  (`key_stations()`), each a loop of up to 13 rows a side (sill to belt,
  then glass bottom over the roof to the centre line). Station points carry
  their own s, so a station bends where a pillar leans. Behind the
  windscreen's header the roof keeps three rows only (edge, the row under
  the rails, centre line); the rows it drops end at the header as points
  of the first roof cells. Front and rear are grids ("caps") whose rows are
  the side rows and whose columns are the top rows laid round the plan
  corner, with three extra corner columns (`K1`-`K3`) carried by the end
  stations only, so the corners and lamps are cells of one grid. The
  windscreen bows 14 mm outward, the roof is crowned and falls 0.05 to the
  rear, the side glass leans in about 23 degrees above a painted belt
  shoulder carrying an 18 mm waist seal.
- **Section** (`W_MID`, `hw()`): amidships the door skin is fullest (0.883)
  at 0.77 m, barrelled 0.05 down to the black sill (0.832 at its foot) and
  nearly upright up to a shoulder crease 65 mm under the belt (row `S5`,
  0.876), above which it leans in 26 mm to the belt and a further 22 mm of
  painted shoulder to the glass. In plan the body tapers toward both ends
  (`TAPER_F`, `TAPER_R`: the belt by 44 mm at the nose and 40 mm at the
  tail, the crease by 20 and 30 mm, the sill by 15-20 mm), and the rows
  from the sill's top to just over the arches stand 6-18 mm proud round
  each wheel (`FLARE`, falling off over 0.34 m). The row over the arch
  tops (`S4`) is not cut away by the arches and carries the full 1.79
  width at both axles.
- **Ends** (`CAP`): each cap row has its height on the centre line and at
  the side, its setback from the bumper line, a bow across the face, the
  distance at which it reaches the body side, and the exponent of the
  superellipse that turns its corner, so every row is one smooth plan
  curve, tangent to the side.
- **Nose**: the black lip tucks 0.105 under at 0.19 m; the bumper is
  fullest at 0.515 m (row `S3`), bowed 50 mm across the face and turning a
  corner that reaches the side 0.38 behind the bumper line (half-width
  0.72 at 0.10 behind it; plan radius of curvature about 6 m on the centre
  line, tightening to about 0.20 at the corner); its top rolls back to a
  shelf (0.605 to 0.635 m, setback 22 to 62 mm) under the lamps and the
  grille. Those lean back 21 degrees from vertical on the centre line and
  39 degrees at the outer lamp, to the bonnet's leading edge 0.80 m high
  and 0.125 behind the bumper line, which in plan sweeps back to 0.17 at
  the lamp's inner corner (x 0.445), 0.27 at x 0.70 and reaches the wing
  top 0.48 behind the bumper line. The lamps' foot climbs from 0.635 at
  the grille to 0.715 at the side, where it runs on as the shoulder
  crease; the lamp's outer end is a point on the wing 0.57 behind the
  bumper line. The bonnet is crowned across (0.10 x squared, a soft raised
  centre) and rolls up from its leading edge at about 20 degrees to a
  10-degree run to the cowl; the wing tops roll down from it to the belt.
- **Tail**: the bumper is fullest at 0.52 m, bowed 45 mm across, its top
  rolling 35 mm forward at 0.64 m under a tailgate panel leaning about 23
  degrees to the lamps' foot (0.80, climbing to 0.85 at the corner) and
  top (0.975, climbing to 1.00, the shoulder crease's height), so each
  cluster narrows round the corner and runs out to a point on the crease
  beside the D-pillar; a ledge under the glass, whose foot is 1.20 wide;
  plan corners squarer than the nose's (exponent 3-4).
- **Pillars**: the A-pillar is a constant 0.08 m band beside the windscreen
  edge; the side glass's front edge runs parallel to it from a small black
  mirror patch (sail) at its foot. B black-out 0.10 constant, C black-out
  0.16 at the belt to 0.10 at the top, D body colour 0.19 at the belt to
  0.13 at the roof. LOD1 keeps the same A-pillar line (the sail merges into
  its front door pane).
- **Lamps, panes, plates, front fog lamps** are whole grid cells or bilinear
  sub-cells (`inset()`); `build.py` conforms the T-junctions away and deletes
  any edge left without a face. The headlamps' and the tail lamps' tips are
  triangles cut from the first side cells behind the ends. The front fog
  lamps are their own faces in the pods beside the lower intake (no lamp
  id).
- **Wheel arches**: exact boolean difference (`asset_build.difference`,
  snapped) of a prism per arch (radius 0.37, centre 15 mm above the axle, 16
  arc segments at LOD0, 5 at LOD1) reaching in to the liner wall at
  |x| = 0.465; its faces stay as the dark closed liners. The arch lip is
  painted relief.
- **Mirrors**: separate closed solids lofted outward from a short arm on the
  sail (x 0.80-1.01), a tapered housing rounded toward its front, a dark mirror face (not a
  glass id) and the side repeater across the outer end. LOD1's 3-section
  mirror has its whole rear face dark (arm to end), so it reads as a mirror
  from behind like LOD0's.
- **Roof rails**: closed solids at x +-0.525 floating 10-12 mm over the roof,
  their ends dipped into it as feet.
- **Smoothing**: smooth shading throughout; edges are sharp past 50 degrees,
  where glass meets anything else and where unpainted trim meets paint.
- **Front** toward -Y; origin on the ground at the centre of the body's plan
  box (mirrors excluded), one origin for every tier.

## Wheels

Four parts (front left/right steering, rear left/right), radius 0.320,
width 0.205, each a closed solid with its origin at the wheel centre and a
tread corner at the very bottom. LOD0: 16 sides, a revolved profile (tread
from the flat inner face, a rounded outer shoulder, the sidewall down to a
rim lip standing 2 mm proud at r 0.226, the lip, and the spoke face dished
38 mm at r 0.208: rim face about 0.66 of the radius, sidewall 0.10), 188
triangles each. One wheel face picture for all four wheels and every tier:
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
  out: high beam (8), low beam (7), and the indicator (4/5) in the swept
  tip, with the daytime lamp (9) as a strip along the foot of the high
  beam. The unit is 0.16 high at its slanted inner edge (parallel to the
  grille's side), 0.115 at mid-length and 0.095 where it turns onto the
  wing, and ends in a point on the shoulder line 0.57 behind the bumper
  line; seen from the front it spans x 0.37-0.86. The grille between the
  units is an inverted trapezoid 0.77 wide at the bonnet's edge and 0.62
  at its foot, 0.165 high; the lower intake repeats its shape (1.00 wide
  at the top, 0.84 at the lip) between the fog lamps' pods.
- Mirrors: side repeaters (4/5) across the housings' outer ends.
- Rear, each side: tail and brake (3) on the corner, a tail (1) section
  wrapping onto the side and running out to a point on the shoulder
  crease, indicator (4/5) over reverse (6) on the inboard end; cluster z
  0.80-0.975 inboard, 0.85-1.00 at the corner.
- High-mounted brake (2) across the spoiler lip, 0.33 x 0.03, centred.
- Rear fog (11) low in the bumper on the left; a red reflector (no id) in
  its place on the right.

Unlit lens colours: red (128, 28, 26), amber (196, 112, 30), clear
(172, 175, 174) sRGB; lit as `vehicle_ids.LENS_LIT`. Headlamps: a light silvery
housing behind the clear lens (its own id `hl_chrome`, sRGB 206, roughness
0.25, metallic 0.55: at 0.85 it mirrored the neutral world's grey and read
darker than the paint, so it was lowered), in the high and low beam cells a
shaded dish (light rim, darker centre) inside a fine bezel line, sized
from the cell's mean height and set on its centre of area, a projector
lens with a shaded lower half in the low beam and a small bulb cap in the
high beam, a soft darker band under the housing's roof; the daytime strip
a pale lens with a slim, slightly lighter light guide following the foot;
the indicator a ribbed amber cell out to the tip. The unit's dark outline
is drawn along its own outer edges (`unit_outline()`: the edges no other
face of the unit shares), two lens texels wide, so it follows the slanted
inner end and the tip. Elsewhere ribbed red clusters with a lighter light
guide, a clear reverse cell, LED dots in the high-mounted lamp, each with
a one-texel dark outline where it meets the body; glossy in the ORM only
(roughness 0.12). Every lens rect is
lit in full in the emission. LOD1 keeps every lens (its brake and fog lamps
are shrunk insets of coarser cells); LOD2 keeps all but the high-mounted
brake: at 208 of 220 triangles it would cost about 22 more (WARN, recorded);
LOD3 none.

## Glass

Groups 32 windscreen (1.20 m2), 33 front door (0.41), 34 rear door and
quarter (0.82), 35 tailgate (0.39). Separate faces on their own UV islands;
LOD2 merges the side glass into one band a side, tagged 33. Measured over
the glass texels: sRGB 52 mean, roughness 0.080, metallic 0.

### Glazing treatment

Departure from `glazing.rooms()`: its lit far-wall patch read as a stain on
a windscreen, so `vehicle_glass()` paints each pane (found with glazing's
own components) neutral dark (52, 56, 60) with a gentle 0.86-1.08 falloff
toward the pane's foot, a per-pane level of 0.92-1.06 and glazing's grain.
No privacy glass. The emission's cabin is `glazing.night_rooms()` at 0.25
on the glass texels; partly covered texels are black.

## Paint

Painted panels (B = 1) are neutral grey 228 sRGB before wear (chroma 0.1):
the panel field (the area-weighted median of the painted texels, LOD0 and
LOD1) measures 0.761 linear, level with the catalog's other vehicles. The
tiers keep one brightness under one paint: the area-weighted mean of the
albedo the painted faces sample is, in linear, LOD0 0.716, LOD1 0.707
(-1.3 %), LOD2 0.686 (-4.2 %), LOD3 0.711 (-0.7 %). LOD2's sides start at the
sill's top, so they never sample the black sill, and the wheel pictures they
show in the arches are a large light rim in a thin dark tyre with the arch
gap left as paint. LOD3's painted faces sample a uniform light block (shaded
to the tiers' level); its dark parts are unpainted faces. Panel gaps (doors,
tailgate, fuel flap, the front bumper's joint from the headlamp's tip to
the arch, the rear bumper's joint, roof hinge) and the bonnet's shut lines
are 13.5 mm (1.7 texels) dark gap lines, albedo at 0.10 of the paint (about
sRGB 70 on the light field), a 4 mm groove (6 mm on the bonnet's lines,
with a 1.5 mm raised lip on the bonnet's side). The bonnet spans nearly
the car's width: its front line runs just behind the leading edge, over
the grille and along the lamps' tops out to the low beam cell (x 0.67),
and each side line runs from there back along the wing's top, nearly
parallel to the car's length (x 0.67 to 0.705, 0.13-0.14 inboard of the
body side), to the windscreen's base corner just inboard of the A-pillar's
foot, where it meets the bonnet's rear edge at the cowl; the wing shows as
a strip about 0.13 wide outboard of it. The lines are texture and normal
map only, no modelled grooves; the bonnet strips ahead of the cowl stay in the top island so
the side lines run straight to the windscreen. Handles, the waist seal and
the flank's character line are relief and darkening on the paint; the
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
| LOD0 | 2944 | 3000 |
| LOD1 | 892 | 900 |
| LOD2 | 208 | 220 |
| LOD3 | 40 | 40 |

LOD0: body shell about 1570 before the arches and 1920 after them, four
wheels 752, mirrors 2 x 84, rails 2 x 52. The nose's corner columns and
the stations round the arches were paid for with the roof's two spare
rows. LOD1 (body 680, wheels 4 x 28, mirrors 2 x 36,
rails 2 x 14): 12 stations, rows sill
top / arch height / 0.77 / belt / glass top / roof edge / centre, the same
nose and tail rows as LOD0 less the lips' lower edge and one bumper row
(its rear bumper's top stands on the bumper line, so the tier keeps the
plan box), the headlamp's tip cut at the same point of the shoulder line,
8-sided wheels, 3-section mirrors, triangular rails, 5-segment arches.
LOD2: 5 stations, rows sill / belt / glass top / centre (the sill carries
the width), a nose of the bumper face leaning back to the lamps' foot and
the lamp band to the bonnet's edge, the tail's lamp rows, two axle prisms;
its sides start at the sill's top (0.30), the prisms showing under them. LOD3: the side profile (11 points:
nose (0.515 high), bonnet edge (0.15 back, 0.78 high), cowl, header, roof
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
(0.27 instead of 0.19, about 2 px at 30 m), its rear bumper's top is not
rolled and its tail is not bowed between the lamps; LOD2's body bottom at
0.30, its nose two flat halves from the bumper line to the lamps' foot;
LOD2 loses the arches (painted) and the high-mounted brake lamp; LOD3 has no
wheels, only the dark lower strip. Runtime switching and performance are pending in
the consumer.

## Interior geometry

Validator hidden-surface test: LOD0 8/2944 (the roof rails' buried feet), LOD1 0, LOD2 22/208 (the middles of the
axle prisms inside the body, kept: one prism per axle is cheaper than two
wheels), LOD3 0. No seats, no interior.

## Known simplifications

Textured, not modelled: panel gaps, bonnet shut lines, handles, side
mouldings, window and waist seals, the grille's frame and slats, the lower
intake's frame and mesh, the fog lamps' dark pods, wipers (on the cowl),
fuel flap (right rear), arch lips, bumper joints and tailgate handle
strip. The grille's and the intake's frames are drawn 2-3 texels inside
their cells' own outline, whatever its shape. No rear
wiper, exhaust, antenna, washer jets, tow eye or brake discs. Glass is
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
normal map: panel gaps -4 mm (the bonnet's lines -6 mm with a +1.5 mm lip), handles +6 mm, side moulding +6 mm, arch lip
+3 mm, grille slats +4 mm over a -6 mm grille, intake mesh, rim lip and hub
+3 mm, spoke openings -4 mm, tread grooves -6 mm; glass and lens faces flat
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
ones the earlier 512 and 1024 reviews (mips 3 to 6) passed; only the
pictures inside the front, top and lens rects changed with the nose.
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
low and raised; a low side perspective) after each change to the shape, with
the head-on and front three-quarter frames judged every time; the same
frames without textures on a plain glossy grey, for the nose corners'
shading (no facets) and the flank's highlights; all four tiers from the
front and rear three-quarter, head-on and side; close-ups of the mirrors
and sail patches and of the front wheels in their arches (dark liner, an
even gap of about 0.05); the mip set above. Before any build the face
lists were checked without Blender: each tier's shell closed once its
T-junctions are conformed, every tier on LOD0's plan box, LOD1's and LOD2's
lamp faces inside LOD0's lens rectangles. Pending in the consumer: runtime
LOD switching and mip filtering, lamp intensities and cabin lighting, paint
colours on the real shader, tangents for the normal map, performance.

## Tooling versions

Blender 5.3.0, headless (`--background`); the MCP addon was not used for
this asset.
