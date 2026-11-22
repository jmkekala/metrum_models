# parturi_brick_pyramid

## Style brief

A late-1980s Finnish suburban barber's pavilion: one storey of yellow-buff
facing brick, 10 x 8 m, under a brown standing-seam steel hipped roof of one
pitch (21.8°) on all four sides, so short in the ridge (2.0 m) that it reads
as a pyramid. A dark brown brick plinth, a brown sheet sign band under the
eave across the front, brown aluminium frames, soldier courses over every
opening. Meant for a 20 x 20 m lot with the building at the back and a
forecourt for a few cars in front. It is deliberately not a flat-roofed box:
the roof, the entrance lobby and the projecting sign carry its identity.

The public side faces `-Y`:

- an **entrance lobby** (the Finnish windbreak) set 0.88 m into the brick
  left of centre, 2.25 m wide, with brick cheeks, a boarded soffit and a soldier
  lintel; at its back a brown glazed screen: one door leaf under a transom
  light and a sidelight with a kick panel;
- two windows to its right, each one big light under a top light, on the
  lobby's head line; vertical blinds are part of the room behind them;
- **PARTURI** (Finnish for barber) in cut cream capitals on the brown band,
  centred over the two windows;
- a square **light box** on two arms on the pier beside the lobby, standing
  out at right angles to the wall: white opal faces with PARTURI in deep blue
  over this asset's own comb-and-scissors mark, which takes most of the face;
- the period's small things round the door: on the pier left of the lobby a
  box wall lamp with an opal diffuser under a lit blue house-number plate,
  on the pier right of it a framed opening-hours board (abstract marks, no
  legible text), a ceiling light in the lobby's soffit and a letter plate in
  the door leaf's bottom rail.

The east wall has a two-light side window and a small staff window, the rear
the service door under a steel canopy with a wall lamp beside it and a high
window, the west the meter cupboard, a small high WC window and an air
louvre. On the roof: a louvred attic vent hood on the front slope under a
cap plate, a sheet-steel ventilation housing on the ridge with louvred sides,
a flashing skirt and a hipped lid (serviced, so the roof safety kit climbs to
it at the back), a soil vent on the rear slope. Gutters on all four eaves,
downpipes at two diagonal corners.

Generic and period-correct: no shop name, no brand, no barber pole (a much
later idiom here). Lettering is stroked from centrelines in `facade_atlas.py`;
no font file.

## Category and secondary use

`buildings/commercial/`. No secondary use: one salon room with a staff room
and WC behind it, which the side, staff, rear and west windows and the
service door imply.

## Hero/landmark status

Not a hero. Ordinary ceilings and the 1024 texture apply; both are met with
wide margins.

## Footprint

- Walls: **10.0 x 8.0 m** rectangle, less the entrance lobby's 2.25 x 0.88 m
  recess in the front wall; floor area 78.02 m².
- Plan bounds: **10.906 x 9.483 m**. Along X the eave (0.453 m each side)
  sets them; along Y the light box at the front (its outer edge 0.85 m off the
  wall) and the wall ladder at the back (its rails' fronts 0.633 m off the
  rear wall). Pivot offset from the wall plan's centre: (0, -0.108) m.
- Height: **5.954 m** to the ridge of the ventilation housing's hipped lid;
  ridge 5.344 m.
- Fits the 20 x 20 m lot with about 10 m of forecourt when set at the back.

## Story height

One storey. The level soffit meets the wall at **3.3125 m** (the eave
height); the sign band runs 2.734–3.3125 m on the front. Every wall height
the brick shares is a line of the catalog's 78.125 mm coursing: plinth top
0.391 m (course 5), sheet sills 0.781 m and window sills 0.859 m (10, 11),
small sills 1.25 m (16), the service door's head 2.109 m (27), the common
head 2.344 m (30), soldier tops 2.344 and 2.578 m (30, 33), the band's foot
2.734 m (35), the wall top in the roof 3.4375 m (44); the meter cupboard
0.547–1.641 m (7–21) and the louvre 2.109–2.422 m (27–31). The eave alone is
off it, 2 cm over course line 42, under the soffit.

## Door leaf height

- **Entrance:** one glazed aluminium leaf **0.95 m wide (stiles included) x
  2.10 m**, at grade with a threshold strip and no step. The transom bar is
  drawn at 2.10 m across the whole screen, with a **transom light** above it
  to the head frame at 2.344 m. The leaf stands 0.88 m back in the lobby;
  its facts threshold is on the front wall plane (Export).
- **Service door (rear):** brown steel leaf **0.94 x 2.055 m** (2.0555 in
  the sidecar) in a 30 mm steel frame filling a 1.0 m opening, frame head
  2.109 m, soldier course over it to 2.344 m, the windows' head line.
- Against the brick: the entrance leaf is about 27 courses tall (26.9).

## Window sills

| Window | Wall | Width | Sill | Head | Notes |
| --- | --- | --- | --- | --- | --- |
| front (x2) | front | 1.75 m | **0.859 m** | 2.344 m | top light over the 2.10 m transom bar; sheet sill 0.781–0.859 m |
| side | east | 1.375 m | 0.859 m | 2.344 m | two lights below the transom bar, top light |
| small (x3) | east, rear, west | 0.875 m | **1.25 m** | 2.344 m | one opening light |

All heads are on the entrance's head line; the transom bars on the door's
2.10 m leaf head. The highest sill, 1.25 m, is under the 1.4 m chest-high
line; the occupied floor is the ground. Widths are whole or half
stretchers (Texture set).

## Eave overhang

**0.453 m on all four sides**, inside the 0.3–0.6 m default: a level boarded
soffit from the wall head at 3.3125 m out to a **0.25 m brown sheet fascia**
(top 3.5625 m), the painted half-round gutter across the fascia's top. No
parapet.

## Construction

Closed solids unioned with Blender's exact boolean
(`asset_build.union(..., snap=asset_build.SNAP)`), welded at 0.1 mm:

1. **the body:** the four walls walked counter-clockwise, each split into
   cells (brick to the band's foot at 2.734 m; above it brick, or on the front
   between s 0.2 and 9.8 m the sign band's artwork); each cell holed for its
   openings, or notched at its foot for the lobby and the service door; every
   cell corner on a neighbour's edge put on that edge, so the cells meet
   vertex to vertex; capped with a floor and a lid (`close_solid()`);
2. **the roof:** one solid: four slopes from the fascia top (3.5625 m) to the
   ridge (5.344 m, x ±1.0 m), the fascia, the four soffit trapezoids and the
   underside inside the wall line, which the union buries in the body;
3. **hip and ridge flashings** (LOD0/LOD1): five-sided caps in vertical
   sections along each hip and the ridge, 0.18 m wide, 35 mm proud, each hip
   cap stopping 0.2 m short of its eave corner so nothing passes the fascia;
4. **the ventilation housing** on the ridge, 1.0 x 0.8 m, 0.50 m over the
   ridge, foot buried 0.45 m (`housing_mode()`; see below);
5. **the attic vent hood** on the front slope: 0.9 m wide, its louvred front
   0.40 m tall at y = -2.6 m, its top falling 3° forward back into the slope;
   to LOD1 four modelled louvre blades and a cap plate 55 mm thick
   oversailing the front 60 mm and the sides 30 mm, its front edge a drip
   (`hood_mode()`);
6. **the sign band** (LOD0/LOD1): 9.6 x 0.58 m, 0.10 m proud of the brick,
   its back in the wall and its top in the roof slab;
7. **the light box:** 0.70 x 0.70 x 0.15 m at x = -1.2 m, z 2.25–2.95 m,
   0.15–0.85 m off the wall (clear of the band), on two 40 mm arms let into
   the pier (one arm from LOD2);
8. **the rear canopy** (to LOD2): a 1.5 x 0.6 x 0.1 m steel tray over the
   service door;
9. **a soil vent** (LOD0/LOD1) on the rear slope, octagonal, r 0.06 m;
10. **the small fittings** (`fitting_solids()`, below);
11. **downpipes** and the **roof safety kit** (below).

Openings: LOD0/LOD1 recess the glass and doors 0.12 m (brick reveals, sheet
sill) with the sheet sill and the soldier course flush on the wall; the lobby
is a 0.88 m recess through LOD2; LOD2 paints the windows and the service door
flush; LOD3 paints the lobby flush too (`item_mode()`). Ground-standing
openings get no floor of their own; the body's floor cap closes them.

Authored parameters: `facade_atlas.py`'s plan, heights, pitch, `ITEMS`,
the housing, louvre and fitting sizes and the regions; `build.py`'s `WALLS`,
the light box, band, canopy, hood, vent, cap and fitting constants,
`DOWNPIPES`, the kit, and the per-tier switches (`item_mode()`,
`caps_kept()`, `band_modelled()`, `arms()`, `canopy_kept()`,
`housing_mode()`, `hood_mode()`, `fittings()`, `vent_kept()`).

### Ventilation housing

A sheet-steel box on the ridge, built to read as a vent housing rather
than a chimney:

- **Louvred sides:** on each of the four sides, four sawtooth blades every
  75 mm between 0.13 and 0.43 m over the ridge, inset 70 mm from the
  corners: each a solid whose sloping face runs from the side down and out
  35 mm to its drip 50 mm below, over a level underside in shadow. They sit
  exactly on painted blade strips over dark slots (`louvre_face()`), so the
  tiers that drop them show the same louvre painted, the slope in the
  height channel.
- **Flashing skirt:** a prism along X round the foot, 30 mm off the sides,
  its top following both slopes 0.10 m above the sheet, in the roof's
  lighter flashing colour.
- **Lid:** a 60 mm drip edge oversailing the sides 80 mm, under a hipped
  top rising 70 mm; its underside in shadow.
- Tiers (`housing_mode()`): all of it to LOD1; at LOD2 a plain 80 mm
  oversailing slab lid on the box, louvres painted; at LOD3 the bare box.

### Small fittings

Boxes let 20 mm into the brick, their faces on 128 px/m art
(`paint_fittings()`):

| Fitting | Where | Size (w x h x d) | Tiers |
| --- | --- | --- | --- |
| box wall lamp, opal diffuser in a brown frame | front, pier left of the lobby, s 0.55, z 1.98 | 0.18 x 0.30 x 0.13 m | LOD0–LOD2 |
| lit house number `14`, blue enamel field | over the lamp, z 2.38 | 0.34 x 0.22 x 0.03 m | LOD0–LOD2 |
| opening-hours board | front, pier right of the lobby, s 3.80, z 1.25 | 0.30 x 0.40 x 0.025 m | LOD0–LOD1 |
| lobby ceiling light | the lobby soffit's centre | 0.30 x 0.30 x 0.07 m | LOD0–LOD1 |
| box wall lamp | rear, right of the canopy, s 8.0, z 1.98 | as the front lamp | LOD0–LOD1 |

The letter plate (0.30 x 0.08 m, brushed metal over a dark slit) is painted
in the entrance leaf's bottom rail. `check_layout()` keeps each fitting on
its pier, clear of corners, openings, the band, the light box and the
canopy, and the front lamp over head height.

### Rainwater

Half-round gutters painted on all four fascias (`PIPE_STRIP`). Two
**downpipes** (`scripts/downpipes.py`), swan-necked from the soffit: on the
west wall 0.3 m from its front corner (y = -3.7 m) and on the east wall 0.3 m
from its rear corner (y = +3.7 m), so the street front stays clear and each
side elevation shows one. `downpipes.problems()` checks both against the
corners and the openings. Tiers follow `downpipes.MODES` (8 sides bent, 4
bent, 4 straight, 3 straight); every tier keeps them.

### Roof safety equipment

The roof is 21.8°, steeper than 1:8, and the ridge housing is serviced from
it, so the kit applies (`scripts/roof_safety.py`), at the back: a **wall
ladder** centred on the rear wall (x = 0), 0.12 m outside the fascia, rising
1.0 m over the roof edge to 4.56 m (4.6 m long: no cage), and a **roof
ladder** straight above it up the rear slope to 0.30 m short of the housing's
back (z 5.04 m). The roof ladder reaches the housing, so there is no walkway.
`roof_safety.problems()` checks the wall ladder against the corners, the
rear window, the service door and the canopy. Tiers follow `RS.MODES`: every
rung, every other rung, every fourth without brackets, then no kit; the wall
ladder sets the rear plan bound, so LOD3 keeps its bare rails (16 triangles,
appended after the weld, `extents=True`).

## Per-tier triangle counts

Measured on the exported GLBs by `scripts/validate_asset.py`:

| Tier | Triangles | Ceiling | Status |
| --- | --- | --- | --- |
| `LOD0` | 1,982 | 12,000 | far under |
| `LOD1` | 1,642 | 4,000 | far under |
| `LOD2` | 496 | 1,500 | under |
| `LOD3` | 236 | 500 | under |

Where they go at LOD0: the roof kit and the two bent downpipes (about 600
together, mostly the ladders' rung holes and the pipes' bends), the body's
cells round twelve openings with their reveals and the lobby, the roof solid
with the five flashing caps cut into it, the housing with its 16 louvre
blades, skirt and hipped lid (about 330 with the hood's four blades and cap),
the hood, the five fittings (about 90 with their cuts in the brick), the
sign band, the light box and arms, the canopy and the vent.

- `LOD0` → `LOD1` (−340): rungs halved, downpipes 4-sided.
- `LOD1` → `LOD2` (−1,146): flashings, sign band, louvre blades, skirt,
  hipped lid (for a plain slab), hood cap, vent, three of the five fittings
  and one light-box arm go; windows and the service door paint flush; kit
  to every fourth rung without brackets; downpipes straight; coplanar
  boolean splits dissolved.
- `LOD2` → `LOD3` (−260): the lobby paints flush, the canopy, the housing's
  lid, the front lamp, the house number and the kit go (the wall ladder's
  bare rails stay), downpipes 3-sided.

Between the catalog's sheds and shops (300–1,000) and its detached houses
(about 2,600): a small box, but with a pitched roof, its safety kit and
pipes, a louvred vent housing, twelve openings, two signs and the fittings
round its door, where the flat-roofed shops have no kit.

## LOD review

Authoring review with `scripts/review_asset.py`: perspective, **1920 x 1080**,
**50° vertical FOV**, distance along the view direction to the centre of the
visible front wall, noon sun, emission off; tiers 0–3 at **35, 70 and 120 m**,
front and oblique; and the oblique at 35 and 120 m by night with emission on.
Renders in `review/small_shops_2026_11_22/parturi_brick_pyramid_polish/`
(`after_lod/`, `after_night_lod/`; not committed); by day repeated after the
re-coursing in `parturi_brick_pyramid_recourse/after_lod/`. Intended switches: the
catalog's 35 / 70 / 120 m.

| Switch | Distance | Verdict |
| --- | --- | --- |
| `LOD0` → `LOD1` | 35 m | Indistinguishable: only rung count and pipe sides change. |
| `LOD1` → `LOD2` | 70 m | Holds. The flashings' highlight lines go, but the change of light between slopes still draws the hips; the band's letters are painted at the same place and colour; flush windows keep frames, transom bars, blinds and dark glass. The housing's blades, skirt and hipped lid give way to a slab lid over the painted louvre, which still reads as striped at 70 m; the hood loses its blades and cap the same way. The opening-hours board, lobby light and rear lamp (a few pixels each) go. The lobby stays a recess. |
| `LOD2` → `LOD3` | 120 m | Holds. The lobby goes flat with its screen painted on the wall; at 120 m it is a dark rectangle either way. The housing loses its lid (under a pixel), the front lamp and house number go. The ladder's rails remain as two thin lines at the back. |

Kept on every tier: the pyramid roof and its eave line, the ridge housing and
the front vent hood (the roofline), the light box (it also sets the front
plan bound), the sign band's PARTURI, brick and plinth, window rhythm and
dark glass, the downpipes. A consumer switching by screen size may show
`LOD3` near: it still has every opening, both signs and the roof features,
but no fittings and a lidless housing.
At 35 m `LOD2` shows its flush windows as flat by their missing reveal
shadow; acceptable for a 70 m switch. One origin for all four tiers
(`asset_build.build_all()`).

**Pending:** runtime acceptance in a consumer scene (visible counts, hardware,
resolution, FOV, shadows, frame times). Triangle counts prove neither frame
time nor VRAM.

## Interior geometry

Welded manifold check, all four tiers: **0 boundary edges, 0 edges with more
than two faces, 0 loose vertices or edges**.

Sampled hidden-surface test (40 rays per face): `LOD0` 51/1,982 (2.6 %),
`LOD1` 42/1,642, `LOD2` 5/496, `LOD3` 8/236. Inspected by position: on
LOD0–LOD2 they are the **roof ladder's rails and rungs' undersides**, 80 mm
over the sheet (x ±0.22 m on the rear slope, z 4.6–4.9 m), and the light
box's arms in its 0.15 m gap (the count did not grow with the louvre
blades, skirt, lids and fittings, and the largest candidates are still on
the ladder); on LOD3 the **wall ladder's bare rails' backs**,
0.57 m off the rear wall, whose rays mostly hit the wall and the eave. All
exterior surface; nothing buried. The union of closed solids leaves one
volume's boundary, so there are no partitions or duplicate surfaces; the
body's lid and the roof's underside inside the wall line are removed by it.
The body's floor at z = 0 is kept as the closed shell's bottom.

## Known simplifications

- **Gutters are painted** on the fascia; downpipes and the kit are modelled.
  A modelled gutter would stand about 0.12 m proud of the fascia, into the
  rear wall ladder's path outside the eave.
- **Soldier courses, sheet sills, frames, transom bars, the door's stiles,
  handle and kick rail, blinds, the meter cupboard and the wall louvre are
  painted**, all under the relief threshold. The housing's and hood's
  louvre blades are modelled to LOD1 and painted beyond.
- The lobby has **no mat or step**; the entrance is at grade.
- The **letter plate** in the door leaf and the opening-hours board's marks
  are painted; the board, lamps and house number are modelled boxes.
- **Glass is opaque**; the salon is `glazing.py`'s room behind it.
- The light box's art is **one image on both faces**, each mapped to read
  left to right from its side.
- No snow guards modelled: they are painted in the roof band.

## Texture set

Seven unique PNGs, all **1024 x 1024, RGB, 8-bit, lossless**, no alpha:

| File | Colour space | Shared across |
| --- | --- | --- |
| `parturi_brick_pyramid_albedo_yellow_brick.png` | sRGB | all tiers |
| `parturi_brick_pyramid_albedo_red_brick.png` | sRGB | all tiers |
| `parturi_brick_pyramid_albedo_brown_brick.png` | sRGB | all tiers |
| `parturi_brick_pyramid_albedo_white_brick.png` | sRGB | all tiers |
| `parturi_brick_pyramid_orm.png` | Non-Color | all tiers, all variants |
| `parturi_brick_pyramid_normal.png` | Non-Color | all tiers, all variants |
| `parturi_brick_pyramid_emission.png` | sRGB | all tiers, all variants |

### Layout

Four bands run the full width and tile in U:

| Band | Rows | Covers |
| --- | --- | --- |
| brick | 0–220 | z 0–3.4375 m; dark plinth brick in the lowest five courses |
| roof | 226–456 | standing seam, V up the 4.80 m slope at 48 rows/m |
| fascia | 462–478 | the 0.25 m fascia, gutter across its top 9 rows (`PIPE_STRIP`) |
| soffit | 482–511 | stained boards, V out from the wall, vent gap at the wall |

Regions above them at 64 px/m: the lobby screen with its soldier lintel
(144 x 165 px), the front window, side window and small window (each with
sheet sill and soldier course), the service door, the meter cupboard, the
louvre, the sign band (614 x 45), and a row of 16 px patches; the light box
face is 112 x 112 px at **160 px/m**. At **128 px/m**, in the row over the
sign band: the housing's two side widths (128 x 122 and 102 x 122 px) and the
hood's front (115 x 83), where the louvres' 75 mm blades and 25 mm slots need
the texels, and the fittings' faces (lamp front and side, house number,
opening-hours board).
`check_regions()` fails the bake on overlap, run-off or a band collision,
`check_bands()` on a stray id in a band.

### The brick

The catalog's module: **250 x 78.125 mm, joints included** (`BRICK_L`,
`COURSE`): a 16 px stretcher, 64 across the 16 m band, and a 5 px course,
so every brick and joint sits on whole pixels and the bond wraps exactly at
the atlas edge. 15.6 mm (1 px) recessed joints in their own mortar colour,
brick faces 6 mm proud (`BRICK_FACE`), as `lahikauppa_corner` and
`kaivoskonttori_brick`; stretcher bond, each brick's tone hashed from its
index modulo the 64 stretchers; a few harder-fired darker bricks. The
plinth brick is the same module and bond, five courses (0.391 m); its
joints are pointed in a darker mortar (`PLINTH_JOINT`, 0.62 of the walling
mortar's shade), as at the foot of a wall: pale joints round dark bricks
drew a coarse white grid that made the plinth bricks read larger than the
walling. Soldier courses are bricks on end, 3 courses (15 px) tall, a whole
number of soldiers across each opening (the perpends take the odd fraction
of a pixel, so neither end is a cut brick), a shade darker so they read as
lintels.

Every opening's sides, every corner and both lobby cheeks fall on a whole
or half stretcher of the bond, so each course ends on a whole or a half
brick; the walls' band offsets (`u` 0, 3.125, 6.25 and 9.625 m) and the
cheeks' (`CHEEK_U`) turn each corner a half stretcher out of step, so a
course ending on a whole brick on one face ends on a half on the other.
`check_layout()` asserts all of it, and that every brick height is a course
line.

Measured against `buildings/commercial/lahikauppa_corner` with identical
`review_asset.py` settings (front, noon, LOD0, 20 and 35 m; crops
auto-contrasted, since that wall stands in its canopy's shade): the same
course pitch and stretcher length, about 4.5 x 14.5 px a brick at 20 m, and
equally sharp.

### Lettering and pictogram

- Band: `PARTURI`, 22 px cap (0.34 m letters), 4.6 px stroke, cream, 20 mm
  proud in the height channel, with a soft shadow ring, centred at s = 6.7 m.
- Light box: `PARTURI`, 14 px cap at 160 px/m (88 mm letters, 3.8 px
  stroke), deep blue, across the top; under it the comb-and-scissors mark
  (`pictogram()`), fitted to the rest of the face, about 102 x 62 px
  (0.64 x 0.39 m) of the 112 px face: a level comb, a solid rounded back
  over a fringe of 12 teeth, and just past its end an open pair of
  scissors, two tapering blades (polygons, `poly()`) up and to the right
  and two bold finger rings below. Drawn bold so the shapes, not the
  detail, carry: box-filtered to the face's projected size, it reads as a
  comb and scissors at 20 m (40 px face) and still as a dark comb bar and a
  ringed X at 35 m (23 px).
- The box stays 0.70 m: its inner edge must stand 0.13 m off the brick to
  clear the sign band and its outer edge sets the front plan bound, so a
  larger face would move the plan bounds and the pivot for about 3 px more
  at 35 m.
- House number: `14` at 0.14 m, 3.4 px stroke at 128 px/m.

### Texel density

64 px/m on walls, openings and the sign band. Deviations: roof 64 along the
eave x 48 up the slope; light box 160 px/m; soffit 64 out from the wall but
the lobby soffit compressed 2x across its 0.88 m depth; the housing's sides,
the hood's front and the fittings 128 px/m (louvre blades and slots, the
lamps' frames and the number's figures need the texels; each surface is
under 1 m², so the sharper patch does not show beside the 64 px/m walls at
any review distance). Relief for the normal map: brick faces 6 mm, frames
25 mm, roof seams 25 mm, gutter roll 60 mm, letters 20 mm, louvre blades
35 mm (their slope, for the tiers without the modelled blades), pressed
sheet lines 4 mm, soffit grooves 3 mm; glass and the light box face flat.
Supersampled `atlas.SS` = 4.

### Padding and filtering

Bands 4–6 rows apart, each painting 2 rows past its edge; regions keep a
≥ 4 px gutter; `atlas.pad()` fills the rest. Mip stress
(`scripts/review_atlas_mips.py`): mip 3 on LOD1–LOD3 (oblique and grazing,
75 and 125 m), mip 4 on LOD2/LOD3 (front and oblique, 75 and 125 m). Brick,
plinth, roof, fascia and glass keep their colours; no roof brown leaks into
the brick or the band; the gutter line holds; the fitting and housing art
in its new 128 px/m row leaks into nothing. At mip 4 the band's letters
(about 1.4 texels tall) smear into a lighter strip and the housing's painted
louvres into an even darker brown, expected and accepted.
**Pending:** the consumer's sampler and shipped mipmaps.

### Weathering

`weather()` at the catalog's moderate level: soil, algae and splash on the
plinth and the brick above it, light efflorescence low on the masonry,
shelter dust under the eave, dirt in the joints (cavity), long runs and
eave dirt on the roof band, runs under the gutter on the fascia, dirt on the
sheet sills and frame feet, the screen's kick panels, the service door's
foot and handle, runs on the housing's sides and the hood's front, dust on
the meter cupboard's foot. Glass, the light box, the letters, the house
number and the opening-hours sheet stay clean.

## Glazing treatment

- Measured by `scripts/validate_asset.py`, all four variants: glass mean
  **sRGB 57**, linear **0.037**, **0.25–0.26x** the trim; darker than the
  brown frames round it.
- Roughness **0.08** (`glazing.ROUGHNESS`), metallic 0.
- Panes painted by `glazing.rooms()` on the finished albedo. The two front
  windows' big lights then get **vertical blinds** in the albedo (89 mm slats
  mixed 42 % toward a pale grey-beige, `blinds()`): part of the room, not a
  reflection, and absent from the emission. They lift the measured mean from
  the catalog's usual ~52 to 57, still inside the band.
- No sky gradient or reflection baked.

## Variant list

Four colours on the same geometry, UVs and tiers, albedo only:

| Variant | Meaning |
| --- | --- |
| `yellow_brick` | default; yellow-buff facing brick, grey mortar, brown roof |
| `red_brick` | red facing brick, a redder brown roof and trim |
| `brown_brick` | brown brick, the darkest roof and trim |
| `white_brick` | white sand-lime brick, light mortar, a warmer brown roof |

Low-rise / small-scale case: 3–6 variants. Roof, fascia, soffit, frames and
doors move a little with each brick; the plinth stays dark brown; the signs
(`FIXED`) do not change: they are the shop's identity.

## Night lighting

`parturi_brick_pyramid_emission.png`, one mask for every tier and colour.

- **Glazing, neutral, each pane a lit room** (`glazing.night_rooms()`): the
  lobby screen (leaf, sidelight, transom light), the front windows, the side
  window, the three small windows, the meter cupboard's reading window.
- **Luminous fixtures in their own colours**, which the validator reports
  as 16,337 coloured fixture pixels:
  - the light box: its opal face warm white (255, 228, 170), its letters and
    mark deep blue (52, 84, 200); its rim black;
  - the band's cut letters, cream (255, 214, 140); the brown field black;
  - the two wall lamps' opal diffusers, the lobby's ceiling light and the
    house number's figures and inner rim, the same opal warm white; the
    lamps' frames, the number's blue field and the opening-hours board
    stay black. At LOD2 the front lamp and the number remain; LOD3 has no
    fittings.
- **Default off:** `emissiveFactor [0, 0, 0]` on all four tiers with the
  `emissiveTexture` binding intact.
- **Reference lit factor** linear **(1.0, 0.88, 0.72)**, a salon's
  fluorescent tubes (`LIT_FACTOR`).
- **Control granularity: one.** Glass, light box, letters, lamps and the
  house number share the material and its one emission factor; a separately
  switched sign or lamp would need a second material slot. No occupancy or
  schedule baked in.
- `variants.png`: all four colours at `LOD0`, a day row (emission off) over
  a night row at the reference factor (`scripts/variant_previews.py`: Cycles,
  fixed camera, exposure and colour management between rows). The light on
  the ground in the night row is Cycles bounce in the preview scene, not
  carried by the asset.
- Checked on reimported tiers by night, emission on, LOD0–LOD3 at 35 and
  120 m: the lit pattern is the same on every tier (the LOD3 lobby screen
  lights on the wall plane).
- **Pending:** consumer control of intensity and colour on reimport.

## Export

`.glb` + external PNGs through `scripts/asset_build.py`'s `export_all()`:
`export_yup=True`, selection only, modifiers applied, keep original textures,
no cameras or lights; each tier exported lit, its emission factor then
rewritten to zero and the placeholder image `bufferView`s stripped.

Traced in the GLB JSON (`LOD2` read in full; the validator confirms the same
bindings on every tier):

- `pbrMetallicRoughness.baseColorTexture` → `parturi_brick_pyramid_albedo_yellow_brick.png`;
- `metallicRoughnessTexture` → `parturi_brick_pyramid_orm.png`;
- `occlusionTexture` → `parturi_brick_pyramid_orm.png`;
- `normalTexture` → `parturi_brick_pyramid_normal.png`;
- `emissiveTexture` → `parturi_brick_pyramid_emission.png`, `emissiveFactor [0, 0, 0]`;
- no `texCoord` on any binding (`TEXCOORD_0` only); default factors and
  scales; one sampler (linear / linear-mipmap-linear); attributes `POSITION`,
  `NORMAL`, `TEXCOORD_0`; every image a `uri`, no `bufferView`.

Pivot on the ground at the centre of `LOD0`'s plan bounds, (0, -0.108) m from
the wall plan's centre in the build frame; every tier's bounds centred on it.
Front `-Y` in Blender, `+Z` in the export.

Facts sidecar `export/parturi_brick_pyramid.model.json`, version 1: the wall
rectangle as footprint (the lobby is a recess in the front wall and leaves
the outline straight), one storey of 78.02 m² (the rectangle less the lobby),
0 dwellings, hero false, two doors:

- `barber`: entrance, **main**, 0.95 x 2.10 m, threshold at x -3.465, y -4.0,
  z 0 in the build frame: on the **front wall plane**, at the leaf's centre,
  although the leaf itself stands 0.88 m back at the lobby's rear;
- `staff`: service, rear wall at x -2.0, 0.94 x 2.055 m.

Rebuild:

```bash
cd buildings/commercial/parturi_brick_pyramid
python3 facade_atlas.py export
blender --background source.blend --python build.py
blender --background --python build.py -- facts      # sidecar alone, from a committed tree
```

## Review status

Completed in this repository:

- `scripts/validate_asset.py`: every mechanical check passes; the only flag
  left is the sidecar's `source.dirty`, which clears when the sidecar is
  rewritten from a committed tree.
- Working views at every tier (`render_views()`: four orthographic
  elevations, plan, front and rear aerials, an eye-level street view and an
  entrance view with a 1.8 m figure), three passes:
  - pass 1: proportions, brick scale against the door, the lobby's depth and
    lintel, the leaf against the transom, sills, the signs' legibility, glass
    darker than frames, hips and eave, ladder, gutters and pipes, every
    elevation. The roof read as one plain field, the soldier courses were
    lost in the walling and the light box's mark was too small;
  - pass 2: added the louvred vent hood on the front slope and the soil
    vent, darkened the soldier courses, enlarged the mark and refitted the
    light box's lettering; LOD1–LOD3 views;
  - pass 3: preview, variants day/night, LOD distance pairs, night tiers and
    mip stress renders (LOD review, Texture set);
  - polish pass (two iterations, before/after with `review_compare.py` at
    front and oblique 20, 35 and 70 m by day and 20 and 35 m by night, and
    the light box face-on along the street at 20 and 35 m): the bolder
    pictogram, the louvred housing and hood, the fittings, the west window,
    the plinth's darker joints; brick scale checked against
    `lahikauppa_corner` at 20 and 35 m (Texture set); LOD pairs at 35, 70 and
    120 m, night tiers at 35 and 120 m, mip 3 and mip 4 stress renders
    repeated after the atlas layout change;
  - re-coursing pass (`review/small_shops_2026_11_22/parturi_brick_pyramid_recourse/`):
    before/after with `review_compare.py` at front and oblique 20, 35 and
    70 m by day, LOD0 and LOD1; working views at LOD0 and LOD2; brick scale
    against `lahikauppa_corner` at 20 and 35 m (Texture set); LOD pairs by
    day at 35, 70 and 120 m; mip 3 at 75 m (front, grazing on LOD1, oblique
    on LOD2): the brick band reads as an even buff field over the dark
    plinth line, no leaks. Night tiers and mip 4 not repeated: the emission
    mask moved only with the regions, and the band's mip 4 is a flat field
    either way.
- GLB material bindings and image sources.
- Manifold and hidden-surface checks, all tiers; candidates explained.
- Glazing against the Style Direction band, all four variants.
- Palette: muted brick, brown steel and aluminium, stained boards; the only
  saturated colours are the deep blue of the light box, the house number and
  the opening-hours heading, and the lit letters. No
  lighting baked into any albedo.
- A generic composite: no real building, shop name or mark.

Pending, outside this repository:

- Consumer import, LOD switching and runtime emission control.
- Consumer mipmap and anisotropic filtering.
- Performance in a representative scene.

## Tooling versions

- **Blender 5.3.0** (hash `02f0899d78e3`, built 2026-11-11), which built the
  tiers and saved `source.blend`; a 5.3 file needs Blender 5.3 or newer.
- **Blender MCP server addon: not used for this asset.** It was built
  headless (`blender --background ... --python build.py`), with the visual
  review done on rendered views (`render_views()`, `scripts/review_asset.py`).
- Textures baked with **CPython 3.14.10, numpy 2.5.5, scipy 1.18.1 and Pillow
  13.0.0**: `python3 facade_atlas.py export`.

## Revision log

- **2026-11-22, re-coursing:** the brick moved from its own 285.7 x 85.9 mm
  module to the catalog's 250 x 78.125 mm (16 px stretcher, 5 px course,
  1 px joints). Heights re-snapped: plinth 0.430 → 0.391 m, sheet sills
  0.773 → 0.781, window sills 0.859 (unchanged, now course 11), small sills
  1.289 → 1.25, common head 2.363 → 2.344, soldier 0.301 → 0.234 tall
  (tops 2.664 → 2.578), service frame head 2.105 → 2.109 and its soldier top
  2.406 → 2.344, band foot 2.75 → 2.734, meter 0.55–1.65 → 0.547–1.641,
  louvre 2.15–2.45 → 2.109–2.422; wall top 3.4375 and eave 3.3125 kept.
  Openings set on whole or half stretchers: windows 1.8 → 1.75, side 1.4 →
  1.375, small 0.9 → 0.875, service opening 1.06 → 1.0, meter 0.6 → 0.625,
  lobby 2.2 x 0.9 → 2.25 x 0.88 m (same floor area), centres moved by up to
  6 cm, the band's word with the windows' midpoint (6.7 → 6.6875). Triangles
  1,986 / 1,646 / 500 / 238 → 1,982 / 1,642 / 496 / 236; plan bounds, pivot,
  height, footprint, storeys and both doors unchanged.
- **2026-11-22, polish:** the light box's comb-and-scissors redrawn bold and
  given most of the face, PARTURI rebalanced over it (box size unchanged);
  the ridge housing given modelled louvre blades, a flashing skirt and a
  hipped drip-edge lid, the front hood blades and a cap plate, both on new
  128 px/m louvre art; a wall lamp, a lit house number, an opening-hours
  board, a lobby ceiling light, a letter plate and a rear wall lamp; a small
  WC window on the west wall; the plinth's joints pointed darker. Brick
  module measured and kept at 285.7 x 85.9 mm. Triangles LOD0–LOD3 1,568 /
  1,228 / 442 / 232 → 1,986 / 1,646 / 500 / 238; plan bounds, pivot and
  doors unchanged, height 5.904 → 5.954 m.
