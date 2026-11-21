# estate_compact

## Style brief

A generic Nordic everyday family estate of 2005-2020: a compact (C-segment)
five-door station wagon with a long flat roof on two rails, a near-vertical
tail, three side glass groups closed by a thick body-colour D-pillar, a short
sloping bonnet with a clear cowl step, and 16-inch alloy wheels. A composite
with no recognisable make: no badge, script or signature grille, conventional
lamp shapes (horizontal headlamp units with an amber corner, wrap-round tail
clusters), black window surrounds, black sill trim and bumper lips. Moderate
Nordic road film: darker lower body and spray behind the wheels, a dusty
lower tailgate; not neglected.

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
about 30 degrees from vertical. A 1.8 m figure stands beside the car on the
review sheet: the roof comes to its chin.

## Construction

`estate_shape.py` holds the whole shape as plain face lists (numpy only), so
the atlas generator and `build.py` read one description.

- **Body**: a closed shell lofted through 19 stations along the length
  (`key_stations()`), each a loop of 13 rows a side (sill to belt, then glass
  bottom over the roof to the centre line: 27 points round). Station points
  carry their own s, so a station bends where a pillar leans. Front and rear
  are grids ("caps") whose rows are the side rows and whose columns are the
  top rows laid round the plan corner (radius 0.30-0.38 at the nose,
  0.10-0.25 at the tail), with three extra corner columns (`K1`-`K3`) carried
  by the end stations only, so the corners and lamps are cells of one grid.
  The bonnet stations sample a crowned bonnet surface (about 10 degrees to
  the cowl) with a soft raised centre, the windscreen bows 14 mm outward, the
  roof is crowned and falls 0.05 to the rear, the side glass leans in about
  20 degrees above a painted belt shoulder carrying an 18 mm waist seal.
- **Section**: barrelled below the belt: widest (0.895) at 0.6-0.75 m,
  tucking in 0.04 toward the black sill and 0.03 toward the belt's shoulder.
- **Nose**: the bumper face is upright only between 0.395 and 0.55 m; below
  it the lip tucks back 0.10, above it the lamp band and bonnet edge lean
  back (setback 0.135 at the bonnet edge). The headlamps' lower edge rises
  0.03 toward the wing, so the units slim outward under the crowned bonnet
  line; their outer ends sweep back round the 0.36-0.38 corner radius. The
  lip's corner radius brings its side point level with the bumper's, so the
  lip turns the corner without a pinch.
- **Pillars**: the A-pillar is a constant 0.08 m band beside the windscreen
  edge; the side glass's front edge runs parallel to it from a small black
  mirror patch (sail) at its foot. B black-out 0.10 constant, C black-out
  0.16 at the belt to 0.10 at the top, D body colour 0.19 at the belt to
  0.13 at the roof. LOD1 keeps the same A-pillar line (the sail merges into
  its front door pane).
- **Lamps, panes, plates, front fog lamps** are whole grid cells or bilinear
  sub-cells (`inset()`); `build.py` conforms the T-junctions away and deletes
  any edge left without a face. The front fog lamps are their own faces in
  the lower intake's outer pods (no lamp id).
- **Wheel arches**: exact boolean difference (`asset_build.difference`,
  snapped) of a prism per arch (radius 0.37, centre 15 mm above the axle, 16
  arc segments at LOD0, 5 at LOD1) reaching in to the liner wall at
  |x| = 0.465; its faces stay as the dark closed liners. The arch lip is
  painted relief.
- **Mirrors**: separate closed solids lofted outward from a short arm on the
  sail (x 0.80-1.01), a tapered rounded housing, a dark mirror face (not a
  glass id) and the side repeater across the outer end.
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
prism through the body (part 0). Arch clearance: 37.5 mm (LOD0) and 12 mm
(LOD1) with the front wheels turned 35 degrees; liner wall clear of the
turned tyre by design (`check_layout()`).

## Ids

`COLOR_0` normalised UNSIGNED_BYTE VEC4 on every tier (validator: whole ids,
one R, G and B per triangle, A 255). LOD0/LOD1: parts 0-4, lamps 1, 2, 3, 4,
5, 6, 7, 8, 9, 11, glass 32-35. LOD2: part 0, lamps 1, 3-9, 11 (no 2, see
Lamps), glass 32-35 with the side glass as one band a side tagged 33. LOD3:
part 0 and paint only.

## Lamps

20 lenses, measured from LOD0 into the sidecar:

- Front, each side: low beam (7) and high beam (8) in the upper headlamp
  cells, daytime (9) as a strip along the headlamp's foot, indicator (4/5) at
  the outer corner. Headlamps about 0.36 wide seen from the front and 0.145
  high inboard, 0.115 at the wing, wrapping round the corner.
- Mirrors: side repeaters (4/5) across the housings' outer ends.
- Rear, each side: tail and brake (3) on the corner, a tail (1) section
  wrapping onto the side, indicator (4/5) over reverse (6) on the inboard
  end; cluster z 0.80-0.985.
- High-mounted brake (2) across the spoiler lip, 0.33 x 0.03, centred.
- Rear fog (11) low in the bumper on the left; a red reflector (no id) in
  its place on the right.

Unlit lens colours: red (128, 28, 26), amber (196, 112, 30), clear
(172, 175, 174) sRGB; lit as `vehicle_ids.LENS_LIT`. Lens pictures: pale
lenses with soft reflector shading (a projector bowl in the low beam, a
bowl in the high beam), a lighter strip for the daytime lamp, ribbed amber,
ribbed red clusters with a lighter light guide, a clear reverse cell, LED
dots in the high-mounted lamp; a one-texel dark outline where each unit
meets the body; glossy in the ORM only (roughness 0.12). Every lens rect is
lit in full in the emission. LOD1 keeps every lens (its brake and fog lamps
are shrunk insets of coarser cells); LOD2 keeps all but the high-mounted
brake: at 218 of 220 triangles it would cost about 22 more (WARN, recorded);
LOD3 none.

## Glass

Groups 32 windscreen (1.20 m2), 33 front door (0.41), 34 rear door and
quarter (0.82), 35 tailgate (0.39). Separate faces on their own UV islands;
LOD2 merges the side glass into one band a side, tagged 33. Measured over
the glass texels: sRGB 49 mean, roughness 0.086, metallic 0.

### Glazing treatment

Departure from `glazing.rooms()`: its lit far-wall patch read as a stain on
a windscreen, so `vehicle_glass()` paints each pane (found with glazing's
own components) neutral dark (52, 56, 60) with a gentle 0.86-1.08 falloff
toward the pane's foot, a per-pane level of 0.92-1.06 and glazing's grain.
No privacy glass. The emission's cabin is `glazing.night_rooms()` at 0.25
on the glass texels; partly covered texels are black.

## Paint

Painted panels (B = 1) are neutral grey 237 sRGB before wear; the validator
measures the painted faces at 0.75 linear on average (chroma 0.1): per tier
LOD0 0.76, LOD1 0.73, LOD2 0.70, LOD3 0.40 (LOD3's faces are all painted,
its windows and under-body included, so a coarse mip of its strip never
shows untinted). Panel gaps, handles, the waist seal, the bonnet shut lines
and the flank's character line are relief and darkening on the paint; the
black trims (sill, lips, slim cowl, grille, intake, B/C pillars, sail) are
unpainted faces, rastered a texel past their outlines so their edges never
pick up a light fringe. Plates are blank white 0.52 x 0.11 with
a thin dark border, unpainted, each one face group mapped whole onto one
plate rect (no mirror seam). The preview multiplies the paint by linear
(0.22, 0.30, 0.40).

## Per-tier triangle counts

| Tier | Triangles | Ceiling |
| --- | --- | --- |
| LOD0 | 2906 | 3000 |
| LOD1 | 890 | 900 |
| LOD2 | 218 | 220 |
| LOD3 | 40 | 40 |

LOD0: body shell about 1566 before the arches and 1882 after them, four
wheels 752, mirrors 2 x 84, rails 2 x 52. LOD1 (body 678, wheels 4 x 28, mirrors 2 x 36,
rails 2 x 14): 12 stations, rows sill
top / widest / lamp foot / belt / glass top / roof edge / centre, 8-sided
wheels, 3-section mirrors, triangular rails, 5-segment arches. LOD2: 5
stations, rows sill / belt / glass top / centre (the sill carries the width),
caps with the lamp rows, two axle prisms. LOD3: the side profile (11 points:
nose, bonnet edge, cowl, header, roof end, glass foot, tail, tail foot, two
wheel contacts, chin) extruded across the width.

## LOD review

Contract distances (75 degree vertical FOV at 1080p): LOD0 under 30 m,
LOD1 30-100 m, LOD2 100-400 m, LOD3 beyond. Reviewed on the review sheet's
tier rows at 30, 100 and 400 m and in close-ups: LOD1 keeps the stations,
glasshouse, pillars, rails, mirrors and arches; LOD2 keeps the two-box
silhouette, bonnet step and windscreen slope, the wheels as dark prisms
under painted wheels in the side texture; LOD3 keeps the bonnet step and
both glass slopes, its sides show the painted car (wheels, glass band). Known
transition limits: LOD1's front lip sits at the sill-top row (0.27 instead of
0.19, about 2 px at 30 m); LOD2 loses the arches (painted) and the
high-mounted brake lamp. Runtime switching and performance are pending in
the consumer.

## Interior geometry

Validator hidden-surface test: LOD0 8/2906 (the roof rails' buried feet), LOD1 0, LOD2 26/218 (the middles of the
axle prisms inside the body, kept: one prism per axle is cheaper than two
wheels), LOD3 0. No seats, no interior.

## Known simplifications

Textured, not modelled: panel gaps, bonnet shut lines, handles, side
mouldings, window and waist seals, grille slats, intake mesh, wipers (on the
cowl), fuel flap (right rear), arch lips, bumper break lines and tailgate
handle strip. No rear
wiper, exhaust, antenna, washer jets, tow eye or brake discs. Glass is
opaque. Wheels have no tread geometry and no hub geometry. LOD2 and LOD3 show
the wheels as painted pictures on painted side faces, so their rims take the
body colour at 100 m and beyond.

## Texture set

One 512 atlas at 64 texels/m: albedo `plain`, ORM, normal, emission (four
unique PNGs, 512, no alpha). Local densities above that: the lamp rects at
112 texels/m (1.75x, each centred in its own 96 x 48 cell) and the wheel
face at 147 texels/m (96 x 96, shared by all four wheels), because they are
small in area and carry the car's face. Islands (`estate_shape.py`, `R_*`): both
sides unmirrored (s, z), top mirrored (s, |x|), front and rear mirrored
(|x|, z), each face choosing by its normal; glass on its own islands (side
mirrored, windscreen and tailgate whole, LOD2's band apart); lenses on rects
packed from LOD0's lens extents (left and right share one, mirrored);
plate, front fog lamp, wheel face, tread, mirror, rail, reflector,
under-body and LOD3 strip patches. The layout keeps the paint islands on
32-texel blocks apart from every dark or coloured patch (a free block
between), so the minified atlas does not bleed lamp or trim colour into
paint. Every tier's face is mapped by the same projections, so the
tiers share the artwork. The projected islands start as paint; texels no
LOD0 face uses carry LOD3's pictures (side glass dark, wheels in the arches,
shadow under the sills). Deviations: under-body patch and LOD3 strip far
below 64 texels/m (never seen near); 45-degree faces stretch up to 1.4x in
their projection. Painted with `scripts/atlas.py` at SS 4; heights for the
normal map: panel gaps -2.5 mm, handles +6 mm, side moulding +6 mm, arch lip
+3 mm, grille slats +4 mm over a -6 mm grille, intake mesh, rim lip and hub
+3 mm, spoke openings -4 mm, tread grooves -6 mm; glass and lens faces flat
(0.5 mm ribs on amber and red); cavity darkens grooves. Weathering
through `scripts/weathering.py` at the moderate level (grime, road film
falling off over 0.2 m above the sills, spray behind each wheel, bumper and
tailgate wake dust; dirt resolved to its neutral steel dust so the paint
stays neutral).

### Mip review

`scripts/review_atlas_mips.py` at mips 3, 4 and 5, rendered on LOD1 and
LOD2 from `source.blend` (not through the glTF importer): no lamp red or
amber bleeds into paint, the black trims stay inside their parts, the white
plate greyed toward its border at mip 4 and beyond (it averaged with its
dark rim; it is a 3-pixel feature at those distances; the plate's rect sits
in a white 32-texel block so it stays light). LOD2's painted wheels
blur into dark blotches on the sides by mip 4, as intended. Consumer
filtering is pending.

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

Done here: validator (0 FAIL apart from this file's absence before it was
written; WARN for `source.dirty` before commit and for LOD2's brake lamp);
review sheet (`scripts/review_vehicle.py`): side, front, rear, top,
three-quarter, steered wheels, each lamp group, night set, cabin, ids,
white/dark grey/red paint, tiers at 30/100/400 m; close-ups of nose, tail,
wheel, belt, roof, lamps, bumper corners, sills and glass feet at LOD0 and
LOD1; the hand-in lamp close-ups beside the polished ones. Pending in the
consumer: runtime LOD switching and
mip filtering, lamp intensities and cabin lighting, paint colours on the
real shader, tangents for the normal map, performance.

## Tooling versions

Blender 5.3.0, headless (`--background`); the MCP addon was not used for
this asset.
