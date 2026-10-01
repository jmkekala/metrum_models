# lahikauppa_corner

## Style brief

A Finnish neighbourhood grocery — the kind of single-storey shop built beside
a housing estate from the 1980s on, standing on its own in a car park rather
than in a street wall. One tall retail storey in facing brick, banded and
panelled with white render, under a flat roof whose long white eave runs right
round the building and falls outward as it goes, so the deck is the high side
and snow pushed off it goes over the edge instead of piling behind a parapet.

The whole public side of the shop is on one elevation, which faces `-Y`:

- Its right-hand corner is cut off at 45 degrees and glazed, with a pair of
  sliding glass doors in the middle of the cut, and a lit sign standing on the
  eave above them carrying the shop's badge and wordmark.
- At the other end of the same wall the walls step back under the roof to make
  a covered loading bay deep enough to take all but the nose of a delivery van,
  with a sectional goods door in its back wall, a staff door in its side wall,
  and a steel column at the open corner where two walls have been taken away.

The brickwork is broken by white rendered panels standing 0.25 m proud of it,
plus the continuous band of render along the top of every wall under the eave.
That was the point of the brief: a thirty-metre brick elevation with nothing on
it reads as a warehouse, and the render strips are what make it read as a shop.

The sign carries this repository's own name — **Metrum Market**, after the
consumer project this catalog feeds — set in letterforms drawn from scratch in
`facade_atlas.py`: a stroked geometric alphabet of the seven capitals the
wordmark needs, not a font file, so the bake has no external dependency and the
artwork carries no third party's licence.

## Category and secondary use

`buildings/commercial/`. No secondary use: the whole floor area is one retail
hall with a back-of-house strip along the rear wall, which the two staff
windows and the rear staff door imply. Nothing about the shell would change if
a consumer placed it as a hardware shop or a pharmacy instead.

## Hero/landmark status

Not a hero. Ordinary triangle ceilings and the 1024 texture cap apply, and both
are met with room to spare.

## Footprint

Walls: **32.0 x 18.0 m**, with the front-east corner cut back **4.5 m** along
each wall, so the chamfered entrance face is 6.364 m long.

The loading bay is a notch taken out of that rectangle at the front-west
corner, **7.0 m** along the front wall by **5.0 m** deep. The roof passes
straight over it, so the notch is in the walls only and never in the plan.

The roof, and therefore the plan extent a consumer has to place, is the
rectangle plus the eave's 1.5 m projection on all four sides: **35.0 x 21.0 m**.
The 0.25 m render panels sit inside that projection and do not widen it.
Overall height **5.719 m** to the top of the sign; the roof deck itself is at
4.5625 m and the eave's outer edge comes down to 3.8125 m.

Covered depth in the loading bay is 5.0 m of recess plus 1.5 m of eave = **6.5 m**
measured from the outer edge of the roof to the bay's back wall, which is what
"all but the nose of a small van" means at Finnish delivery-van lengths of
roughly 6-7 m. The column at the open corner is set in the corner of the roof
outline and does not narrow the drive-in.

## Story height

One storey, wall head at **4.3125 m**, roof deck at 4.5625 m.

This is a deliberate departure from CLAUDE.md's ~3.0–3.3 m standard and the
reason is the building type, not a stylistic preference: a retail hall needs
clear height over the shelving and a ceiling void for the ventilation that the
roof plant belongs to, and a shop built at 3.0 m to the eave reads as a garage.
The human scale is held by the doors instead (below), and by the shopfront,
whose sill sits on the plinth at 0.375 m and whose head is at 3.25 m — a person
standing at the glass still reaches two-thirds of the way up it.

Nothing else in the catalog is affected: this is a single-storey type, so there
is no floor-to-floor rhythm that has to line up with the housing.

## Door leaf height

- **Entrance, sliding pair:** leaf **2.3125 m**, within the 2.0–2.4 m band. The
  opening continues to the shopfront head at 3.25 m, so the 0.9375 m above the
  leaves is a **transom light**, and the transom bar is drawn across it in the
  entrance's own atlas region and continues across the whole shopfront at the
  same height. The two leaves are 1.2 m each and meet on the centre line, with
  a fixed screen 0.35 m wide at each side for them to slide behind; that split
  and those pockets are what tell a slider from a hinged pair at a glance.
- **Staff and bay doors:** leaf **2.125 m**, casing head 2.225 m. Ordinary, and
  recorded here because CLAUDE.md asks for ordinary heights too.
- **Goods door:** 3.2 m wide by 3.2 m high sectional steel. Not a pedestrian
  door and not a human-scale anchor; it is sized for a van.

## Window sills

The two staff windows on the rear wall sit at **1.0 m**, below the 1.4 m line
CLAUDE.md warns about, and are 1.3 m tall. The shopfront sill is 0.375 m —
shop glazing goes nearly to the ground, which is correct for the type and is
what makes the entrance leaves read at the right size beside it.

## Eave overhang

**1.5 m on all four sides, falling outward.** The soffit leaves the wall head
at 4.3125 m and drops **0.5 m** over that projection to its outer bottom edge
at 3.8125 m; the fascia is 0.25 m of vertical edge above it, to 4.0625 m; and
the skirt's upper face rises back at the same pitch to meet the deck at
4.5625 m. Slope length 1.581 m, pitch about **18.4 degrees**.

This is well outside the 0.3-0.6 m default and is the type's single most
recognisable feature, so it is an authored exception rather than a drift:

- It is not a roof eave in the pitched-roof sense. It is a light steel-framed
  skirt that folds down from the deck, and the direction matters: the deck is
  the **high** side, so snow pushed off the roof runs out over the edge and
  falls clear of the wall. A skirt that rose outward would make a parapet and
  a snow trap, which is the opposite of what this roof is for.
- Because it falls, the outer edge comes down to 3.8125 m — head height and a
  bit — so the skirt itself shelters the shopfront and the entrance. No
  separate canopy is needed at the shopfront head, and none is modelled.
- Seen from the street it is read from below, as a white soffit over the brick;
  seen from above it is the white frame round the dark deck. Both faces carry
  the same standing-seam sheeting, the whole way round.
- It costs 30 quads swept round a ten-vertex outline, a small fraction of the
  tier budgets, and it is retained unchanged at every tier including `LOD3`.

**There is no parapet, and the roof plant is therefore visible** from any
elevated view and, at a distance, from the ground. That is a consequence of the
falling eave and it is correct for the type: the plant is part of what a
low-slung shop roof looks like. It also means this asset cannot claim the
"roof-concealing parapet" that CLAUDE.md asks be retained at every tier —
there is nothing to conceal it with. The profile-defining element that *is*
retained at every tier is the eave itself.

## Construction

Five closed solids unioned with Blender's exact boolean:

1. **the wall ring** — seven walls walked counter-clockwise from the loading
   bay's back wall round to the west wall, capped with a floor on the ground
   and a lid at the wall top;
2. **the roof** — deck, skirt, fascia, soffit and underside as *one* solid;
3. **the sign**;
4. **the column**;
5. **the eleven render panels** and the six pieces of roof plant.

Each is simple on its own and `to_object()` refuses any that is not closed. The
union is what does the work: it trims the wall tops into the roof, trims the
render panels flush against the soffit, removes the roof's underside everywhere
except over the loading bay, and leaves the boundary of one empty volume, so
interior geometry cannot occur by construction.

**Why the roof is one solid and not two.** The deck and the skirt are one
surface that folds at the wall line. Built as a slab and a separate swept ring
they meet along that fold tangentially — two boundaries touching along a line
without crossing — which is the case an exact boolean handles worst. In this
building it left the fold non-manifold on every tier, and in one configuration
the solver silently dropped unrelated operands: the whole roof plant vanished
from the result while every input solid was individually closed and correct.
Built as one solid the fold is simply two faces sharing vertices, and nothing
has to be resolved at all. The lesson generalises: where two authored surfaces
are meant to be continuous, make them continuous in one mesh rather than
asking the boolean to discover it.

Two details remain to keep the boolean out of tangential cases elsewhere:

- The walls run **0.125 m into the roof**, so the lid that closes the wall ring
  is strictly inside it rather than coplanar with its underside.
- The render panels run **up to 4.40625 m**, which is above the soffit at the
  wall line (4.3125 m) and below the skirt's upper face at their own 0.25 m
  projection (4.479 m) — strictly inside the eave's thickness. A panel that
  stopped level with the wall head would touch the soffit along one line and
  push through it beyond, and a panel that stopped short would leave a
  centimetre-high slot under the eave that reads as hidden surface.
  `check_layout()` fails the build if that clearance is ever lost.
- The render panels' 0.25 m sides sample the **render band wrapped round the
  corner** from their face: U runs on from the face's own s and V is world
  height, so the concrete plinth in the band's foot runs round each panel at
  the wall's 0.375 m line. A flat reveal patch there put white render down to
  the ground beside the plinth.

The walls themselves are built as regions: two courses of height (ground to the
top of the brickwork, then the render band to the wall top), each split into
cladding panels along the wall, each panel holed, notched or broken for every
opening that reaches it. Region outlines carry their neighbours' breakpoints
explicitly, which is the only reason two regions that meet do so on the same
vertices and the ring stays closed. The roof's outline carries breakpoints of
its own for the same reason: the loading bay's two corners, where the underside
is broken into separate faces.

The entrance is the one place where a recess steps back twice: the shopfront
bay is set 0.20 m into the wall, and the doors 0.50 m further into a lobby. The
bay's sill and head reveals are broken at the lobby's jambs so the deeper
opening's side faces meet them on shared vertices, and the hole the bay needs
in its wall carries those two vertices whether the entrance is a recess or, at
`LOD2` and `LOD3`, a painted rectangle.

An opening that stands on the ground — the goods door and both staff doors —
gets **no floor of its own**. The strip it would lay at z = 0 is inside the
building's own footprint and would sit on top of the floor the wall ring is
capped with; the two coplanar faces left the export non-manifold at the
threshold until `recess()` was given a `floor` flag. Left out, the rim simply
detours round the recess and the floor cap covers it.

## Per-tier triangle counts

Measured on the exported, triangulated GLBs by `scripts/validate_asset.py`:

| Tier | Triangles | Ceiling | Status |
| --- | --- | --- | --- |
| `LOD0` | 856 | 12,000 | far under, explained |
| `LOD1` | 704 | 4,000 | far under, explained |
| `LOD2` | 450 | 1,500 | far under, explained |
| `LOD3` | 396 | 500 | under |

The low counts have one cause, and it is not
under-modelling. The building is a box: one storey, one flat roof, four
straight walls and a chamfer. There is no roofline to preserve beyond a level
eave, no dormers, no bays, no repeated window grid — the whole opening budget
is three shopfront runs, one entrance, two staff windows and three doors. The
features that would ordinarily consume a building's triangles are all carried
by the texture, correctly: brick coursing, render panel joints, shopfront
mullions and transoms, the standing seams and rafter ends of the eave, the
goods door's sectional ribs, the roof membrane's roll seams.

What geometry there is went where it earns shadow:

- the roof solid — deck, skirt, fascia, soffit and the bay's ceiling — at every
  tier (about 90 triangles),
- the eleven 0.25 m render panels, at every tier (about 130 triangles) — at
  exactly the default relief threshold, and kept at every tier because they are
  also the elevation's dominant colour contrast, which CLAUDE.md does not allow
  a low tier to lose,
- the loading bay recess and its column,
- the shopfront's 0.20 m reveals and the entrance's further 0.50 m lobby,
- the sign and the roof plant.

Padding the count would mean subdividing flat walls, which
CLAUDE.md forbids outright. The counts are reported as they are.

The `LOD0` to `LOD1` step is modest (18%) for the same reason: most of what is
in `LOD0` is massing that cannot be dropped at 35-70 m. The step that carries
the ladder is `LOD1` to `LOD2` (35%).

## LOD review

Setup, recorded so it can be repeated: perspective, **1920 x 1080**, **50 deg
vertical FOV** (`sensor_fit = VERTICAL`, `sensor_height = 24`), EEVEE with the
catalog's studio sun and flat neutral world, aimed at the entrance corner
(6.0, -5.0, 3.0) from a direction of (0.85, -1.0, 0.33) normalised — a raised
three-quarter that puts the chamfer, the sign, the shopfront, the front wall's
render panels and the loading bay all in one frame. Distance measured along the
view direction to that point. Emission off.

| Switch | Distance | Verdict |
| --- | --- | --- |
| `LOD0` → `LOD1` | 35 m | Indistinguishable at intended screen size. The openings drop their casing ring for a single recess of the same depth, and the two fan cowls and two vent pipes leave the roof. At 35 m a 0.45 m cowl is about 2 px, on a dark deck seen at a shallow angle; at the switch it is not visible. |
| `LOD1` → `LOD2` | 70 m | Indistinguishable. The openings go flat; the 0.14–0.20 m reveals they lose are under a quarter of a pixel at this distance. The render panels, the eave, the sign, the bay and the column all remain. |
| `LOD2` → `LOD3` | 120 m | The two air handlers and the bay column leave. Enlarged 3x the change is visible; at true screen size the air handlers are about 2 px of grey on a dark roof and the column is about 1 px of dark against an already-dark bay. Neither is on the silhouette and neither moves the plan, which the eave's outer edge defines. |
| `LOD3` alone | 200 m | Silhouette, eave line, chamfer, sign and the white/brick rhythm all still read. |

Checked in both directions at each switch, and against `LOD0` directly at all
three distances. Preserved at every tier: the overall silhouette, the level
line of the eave, the loading bay recess, the chamfered corner, the sign, the
glazed frontage and — the one that a low tier most easily loses —
the high-contrast white render panels against the brick.

These distances are the **authoring** review's, at the review camera above.
They are a starting point for a consumer's switch distances, not a measurement
of anything. **Pending:** runtime acceptance in a representative consumer
scene, with visible instance counts per tier, hardware, resolution, FOV, shadow
settings and frame times. Export size and triangle ceilings prove neither frame
time nor VRAM.

## Interior geometry

`scripts/validate_asset.py`'s sampled hidden-surface test, 40 rays per face
centre: **zero hidden triangles on every tier**.

It was not always zero. The exact boolean had left one sliver of about a square
millimetre at the top of the chamfer wall, where the eave's soffit crossed it at
the boundary of the glazed length — three surfaces meeting very near a point.
Removing the glazing removed the boundary and with it the sliver, which is the
better fix: it was never a buried partition, but a face that survives a 0.1 mm
weld and cannot be deleted without opening the shell is a face worth not
creating.

The test is a sampled diagnosis, not a proof. It is backed here by the
construction argument below — a union of closed solids has no interior by
definition — and by the manifold check, which is exhaustive.

Welded manifold check on every exported tier, at a 1e-5 weld:
**0 boundary edges, 0 edges with more than two faces, 0 loose vertices or
edges**, all four tiers.

## Known simplifications

- **The roof outline is a plain rectangle with one chamfer.** The type it is
  drawn from steps its roof edge back over the loading bay. Keeping the roof
  a single unbroken plane makes the bay read as a clean cantilever, keeps the
  eave one continuous fold, and keeps the plan the consumer places rectangular.
- **The loading bay is open on two sides**, front and west, with a column at
  the free corner. That is the honest reading of an outer corner taken away
  from a building.
- **The eave over the entrance is sheeted, not glazed.** It was glazed at
  first, on the brief: the same slope and the same plane as the rest of the
  eave, reading as a clerestory over the lobby. Once the eave was turned over
  to fall outward it stopped being visible — a down-sloping plane is seen
  almost edge-on from the pavement, and the sign stands directly in front of
  what is left. It was carried for a while on the strength of the aerial view
  alone, which is not enough to justify a material. Taking it out also removed
  the last hidden-surface finding: the 1 mm² sliver the exact boolean had left
  behind sat precisely at the glazed span's boundary, where three surfaces met
  near a point. Its atlas region went to the roof deck.
- **No separate canopy over the shopfront.** The type this is drawn from has
  one, at the shopfront head, under a roof whose eave sits higher. Here the
  eave falls to 3.8125 m at its outer edge and does the same job, and a second
  white projection 0.4 m below it would have read as a slot rather than as
  shelter. Recorded because it is a visible difference from the type.
- **No downpipes, no wall louvres, no bollards or kerbs.** The eave has no
  gutter: it falls outward and sheds rain and snow over its edge 1.5 m from
  the wall, which is what the type does, so there is nothing for a downpipe
  to drain. A pipe from that edge would have to stand 1.5 m off the wall or
  run uphill under the soffit. Louvres are repeated shallow detail and belong
  in a texture, which this atlas does not currently have room for at
  64 px/m; kerbs and bollards are site furniture, not building.
- **The shopfront's mullions, the eave's rafter ends and the goods door's ribs
  are painted, not modelled.** All are well under the 0.25 m relief threshold
  and all repeat.
- **No roof hatch or ladder.** Plant only, as the brief asked: two air
  handlers, two fan cowls, two vent pipes.

## Texture set

Seven unique PNGs, all **1024 x 1024, RGB, 8-bit, lossless**, no alpha channel:

| File | Colour space | Shared across |
| --- | --- | --- |
| `lahikauppa_corner_albedo_red_brick.png` | sRGB | all four tiers |
| `lahikauppa_corner_albedo_brown_brick.png` | sRGB | all four tiers |
| `lahikauppa_corner_albedo_yellow_brick.png` | sRGB | all four tiers |
| `lahikauppa_corner_albedo_grey_brick.png` | sRGB | all four tiers |
| `lahikauppa_corner_orm.png` | Non-Color | all tiers, all variants |
| `lahikauppa_corner_normal.png` | Non-Color | all tiers, all variants |
| `lahikauppa_corner_emission.png` | sRGB | all tiers, all variants |

The normal map is derived from the painted height and carries the brick
coursing, the render joints, the shopfront sections and the eave's seams (see
Supersampled atlas, normal map and padding below). Adding it changed neither
the mesh nor the UVs.

### Layout

The atlas is a trim sheet. Four bands run the full width and tile horizontally:

| Band | Rows | Covers |
| --- | --- | --- |
| brick | 0–224 | z 0 … 3.5 m, with the concrete plinth in its bottom 24 rows |
| render | 228–504 | z 0 … 4.3125 m, plinth likewise in its bottom 24 rows |
| shopfront | 508–692 | z 0.375 … 3.25 m of glazing |
| eave soffit | 696–752 | the 1.581 m of eave slope |

Both cladding bands start at the **ground**, not at the plinth top, and carry
their own copy of the plinth. That is deliberate and it is what keeps the mesh
simple: a wall is then two courses of region with exactly one line across it,
at the top of the brickwork, and no opening straddles a band edge. `build.py`'s
`check_layout()` fails the build if one ever does, because an opening across a
band edge would need its casing, its reveal and its closure all split there to
stay welded to the wall.

Everything singular gets a region of its own above the bands: the entrance, the
sign panel, the goods door, the staff door, a staff window, the roof deck, the
loading-bay ceiling, and four small plates for the roof plant. `facade_atlas.py`'s `check_regions()` asserts that no two of
them overlap, that none runs off the sheet, and that none collides with the
bands; `check_bands()` asserts that no band contains an id it should not,
because a stray pixel in a tiling band is not a local blemish — every surface
sampling that band repeats it.

### The sign

The sign's region is **304 x 106 px** for 4.75 x 1.656 m — 64 texels/metre like
the rest of the shopfront. The artwork is a badge and a two-line wordmark: a
blue rounded square with the initial reversed out of it, then `METRUM` in
geometric caps at 40 px of cap height over a hairline rule, with `MARKET`
letterspaced at 16 px and centred on the name above it. One thing to recognise
at a hundred metres, one to read at ten. Set as described the name measures
184 px and the shop type 112 px inside a 304 px region, so the type stays
clearly the subordinate line and both keep a margin off the frame.

The letterforms are stroked centrelines from a small `GLYPHS` table — the seven
capitals the two lines need between them, and no more: `M E T R U` from the
name, plus `A` and `K` from the type. Nothing reads a font file, so the bake
stays self-contained and the artwork carries no third party's licence.

**The wordmark is a connected logotype.** Four of its five letter pairs are set
with no gap at all, so the stroke one letter ends on is the stroke the next one
starts from. They are listed in `JOIN`:

- `M|E` and `U|M` **share a full-height stem**. Left to ordinary tracking those
  two verticals land a third of a stroke apart and fuse into one bar of twice
  the intended weight, which reads as a blot; made to coincide they give one
  stroke of the right weight and the collision becomes a ligature.
- `E|T` and `T|R` **meet on the cap line**, where the E's top arm, the T's
  crossbar and the R's shoulder run into one another as a single unbroken seam
  across the top of the word. The T is tied to both its neighbours.
- `R|U` is the one pair left loose, because it has no shared stroke to make —
  the R ends on a diagonal at the baseline and the U starts on a stem at the
  cap line — so it takes ordinary tracking and gives the word its one breath.

**The ligatures are passed in, never applied by default.** They belong to the
name alone. The shop type is set from the same glyphs at a fifth of the size,
and it shares letter pairs with the name above it — `MARKET` contains `METRUM`'s
`E|T`. A ligature drawn there, at that scale and at 0.40 em of letterspacing,
would read as two letters that had collided rather than as a joined logotype,
so `text()` and `text_width()` take a `join` argument that only the name
supplies.

Two mechanics underneath that had to be right, and each showed up as a visible
defect first:

- **Tracking measures ink, not centrelines.** A stroked glyph's ink overruns
  its box by half a stroke at each end, so spacing measured on centrelines
  tightens as the weight goes up — at 0.12 em of nominal tracking and a 0.17 em
  stroke the real gaps went negative, and letters collided where they were not
  meant to. `_step()` adds the stroke-to-cap ratio back in, so tracking means
  what it says at any weight and the only letters that touch are the ones in
  `JOIN`.
- **The edges are supersampled, not blurred.** The whole atlas is painted at
  4 x 4 samples per pixel and averaged down (see Supersampled atlas, normal map
  and padding), so a letter's edge carries real partial coverage — seventeen
  levels — in both the albedo and the emission, instead of a stair-step. An
  earlier attempt blurred the id map's output instead; it took the hard edges
  off but thinned the strokes, and it could not help the emission at all.

The sign was once the only region drawn that way, through its own scratch
canvas; a stroked letterform at this size does not survive a stair-step, and
no mip level puts it back. Since the atlas moved to `scripts/atlas.py` every
region gets the same anti-aliasing, and the sign needs no separate pass.

### Texel density

64 texels/metre on everything a customer stands in front of: both cladding
bands, the shopfront, the entrance, the glazed eave slope and the sign. The
deliberate local deviations, all of them on surfaces seen from a van bay or
from the air:

| Surface | px/m | Why |
| --- | --- | --- |
| eave soffit, across the slope | 30.8 | 64 along the run; across it the artwork is two seam lines and a rafter end, so the cross-slope axis is compressed. Anisotropic by design. |
| goods door | 40 | inside a shadowed bay |
| staff door | 33 | rear elevation and bay |
| staff window | 49 | 1.2 m opening on the rear elevation |
| roof plant | 48 | on the open deck, seen from the air |
| loading-bay ceiling | 16 x 14.8 | flat sprayed soffit in shadow |
| roof deck | 10.3 x 10.2 | flat dark membrane, seen from above at distance and, because there is no parapet, obliquely from the ground beyond about 40 m. It inherited the space the glazed eave gave back, which more than doubled it from the 4.4 px/m it started at. |

The roof deck is the one large concession. At 64 px/m the deck alone would want
more than the whole sheet; at 4.4 px/m it costs 140 x 74 px and still reads as
laid membrane from the air. This is recorded rather than hidden because it is
the number a future reviewer will want.

### Padding and filtering

Bands are separated by **4 rows** of padding, into which each band paints 2
rows of its own edge texels. Unique regions have at least a 4 px gutter, which
`check_regions()` enforces, and each is painted to its own edge.

The tiling bands are periodic in u, which is what a gutter cannot provide: the
brick's perpend is wrapped back in at x = 0, the render's panel joints are at
multiples of 256 px (4 m), the eave soffit's seams at multiples of 32 px
(0.5 m), and the shopfront's structural mullion is split across the cell edge
so that **no glazing pane straddles u = 0**. That last one matters twice over:
it keeps the band tiling, and it keeps `scripts/glazing.py` from painting half
a room at one edge of the sheet and half at the other.

Reviewed at mip 3 — a whole-atlas 8x minification, harsher than any of this
asset's intended distances — rendered face-on and oblique at 75 m with
`scripts/review_atlas_mips.py` and `scripts/review_asset.py`. The brick/render
rhythm, the dark glazing and the white eave all hold; no roof colour leaks into
the wall bands and no dark seam appears along the shopfront's head. Four rows
of padding cannot survive an arbitrarily coarse mip — one texel at mip L spans
2^L source texels, so past mip 2 a sample near a band edge reaches into its
neighbour — and that limit is accepted here rather than engineered around.
**Pending:** the same check under the consumer's own sampler and shipped
mipmaps, which this repository does not own.

### Supersampled atlas, normal map and padding

- **Rasterised by `scripts/atlas.py` at 4 x 4 samples per pixel.** `facade_atlas.py` paints in
  final-pixel coordinates and the canvas stores the samples; they are
  box-filtered down in linear light, so an edge at a fractional position lands
  partway across its pixel and the sign's lettering, badge and the plant's discs come out anti-aliased like everything else, instead of snapping to it. The emission mask
  carries the same coverage as grey at pane edges.
- **The normal map is derived from a painted height channel** in metres by
  `atlas.normal_map()`, OpenGL convention. The relief is physical, not
  exaggerated, and only covers what the mesh does not model:
  - brick faces 6 mm proud of recessed mortar, the render's panel and movement
    joints;
  - the shopfront's and entrance's aluminium sections 30 mm proud of the glass;
  - the white eave's 15 mm standing seams and its rafter ends;
  - the steel doors' frames and panel joints, and the roof plant's louvres, fan
    rings and pipe.
  The sign's printed face is flat; only its frame stands proud. The roof deck
  (~10 px/m) and the bay ceiling stay flat.
  Glass stays flat. Regions painted coarser than 64 px/m (the goods door, the staff window,
  the plant) scale their relief by their px/m over 64.
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
- **The sign needs no separate pass.** The old bake drew the placard twice,
  once more into a scratch canvas at four times the scale, and composited the
  albedo and emission from that coverage. The whole canvas is supersampled now,
  so the sign is drawn once with everything else and keeps the same soft edges.

### Weathering

- **Placed by `facade_atlas.py`'s `weather()`, drawn by
  `scripts/weathering.py`** at the catalog's moderate level. Its fields
  (dirt, algae, rust, faded paint, rain runs) are amounts, resolved against
  each colour's own palette, so the four variants weather alike. Dirt lerps toward a warm soil colour;
  on steel it is a neutral dust, because soil's brown turned dark roofs
  orange. Dirt roughens the ORM and strips the metallic. Height, the normal
  map and the emission mask are untouched, and glass never weathers.
- **Following height, so it lands the same on every wall:** both cladding
  bands start at the ground, so each carries the plinth's soil, splash specks,
  green film and runs from the cladding's drip, and splash-back up its own
  brick or render; the render under the deep eave stays dry and gathers a
  little dust instead; dust in the mortar and render joints, from the cavity.
- **Elsewhere:** dirt on the shopfront's sill rail and on the entrance
  threshold; the staff window's bottom rail with runs down the render below
  it; kicked-up dirt at the feet of the service and goods doors and grime at
  the service door's handle; dirt where the flat roof's membrane ponds; runs
  down the plant's casings.
- **Kept clean:** the sign, which is the shop's own to keep, and every pane.
- The level was chosen on `rintamamiestalo_porch` (see its notes); this
  building takes the same helpers with its own layout.
- The albedo and ORM PNGs are larger on disk (5 files, 2.7 MB against 2.5 MB before), as the noise
  compresses less; resolution, count and GPU memory are unchanged.

## Glazing treatment

- Measured glass, all four variants: mean **sRGB 53**, linear **0.032**,
  **0.23x** the 99th percentile of everything else on the sheet.
- Roughness **0.08**, metallic **0**, from `scripts/glazing.ROUGHNESS`.
- Panes painted by `scripts/glazing.py`'s `rooms()`, called on the finished
  albedo after the id/shade/AO pass, exactly as CLAUDE.md's default requires.
  Each 2 m shopfront bay, each door leaf and the glazed eave get their own
  level, vertical falloff and — on rather more than half of them — a lit patch
  of far wall. Nothing about a reflection is in base colour: no sky gradient,
  no fixed highlight.

**One brief-driven exception, and it is not a window.** The sign panel over the
entrance is a lit sign face, so it sits far above the glazing band by design
(albedo around sRGB 206, with the graphics at sRGB 22/56/118). It is excluded
from the glazing measurement because it is written into the emission mask in
its own colours rather than neutral white — see the next section.

## Variant list

Four colours, all the same geometry, UVs and LOD chain, differing only in the
albedo PNG:

| Variant | Meaning |
| --- | --- |
| `red_brick` | default; warm red facing brick, warm off-white render |
| `brown_brick` | dark brown facing brick, slightly warmer render |
| `yellow_brick` | the pale yellow brick Finnish suburbs are full of |
| `grey_brick` | grey-buff brick, near-neutral render |

This is the **low-rise / small-scale** case in CLAUDE.md's Color & Material
Variants: 32 x 18 m and one storey is a small building whatever its floor area,
the brick skin is uniform, and a town wants more than one of these without
every one of them looking like the same shop. Four sits inside the 3–6 band.

The brick is what moves; the render, roof membrane and mullion tones move with
it by small amounts so each colour stays coherent. **The sign does not change.**
Its panel, its blue badge and wordmark and its dark surround are the shop's
identity and are the same in every variant, which is also why they live in `FIXED` rather
than in the palette table in `facade_atlas.py`.

## Night lighting

`lahikauppa_corner_emission.png` is shared by every tier and every colour.

**Candidate glazing, written neutral grey, each pane lit as a room (see Room-lit panes below):** all three shopfront
runs, the entrance leaves and their transom, and the two staff windows on the
rear elevation. Frames, mullions, walls, the
plinth, the eave sheeting and the roof are black.

**One luminous fixture, written in its own colours:** the sign. Its panel is
(176,198,222) and its badge and lettering **(16,44,118)** — roughly twenty
times dimmer, not a little dimmer.

That ratio is the whole trick, and it was wrong at first. A lit sign box is a
bright diffuser with the graphics printed on it, and print transmits far less
light than the blank panel does. Given emission of the same order as the panel,
the blue glowed nearly as hard as the ground it sat on and the wordmark washed
out after dark — legible by day, a pale smear by night. Dimmed properly it
reads as deep blue on a lit panel, which is how the sign reads by day too, and
the badge becomes a dark block with the initial punched bright through it. A shop sign is not a window and
measuring it against the glazing band would be meaningless, so
`scripts/validate_asset.py` now separates the two: neutral bright mask pixels
are glazing and get measured, coloured ones are reported as a fixture for a
reviewer. This asset contributes 30,576 fixture pixels, all of them the sign.

**Reference lit factor: linear (1.0, 0.88, 0.72).** This asset states its own
rather than taking the catalog's residential default of (1.0, 0.55, 0.23),
because what is behind this glass is a fluorescent-lit sales floor, not a
living room with a warm bulb, and the warm default turns the sign's blue
grey-green. `scripts/window_emission.attach()` and
`scripts/variant_previews.render_sheet()` both take a `tint` now; omitting it
keeps the old behaviour, so the residential assets are unaffected.

**Control scope.** The exported `emissiveFactor` is `[0, 0, 0]` in all four
tiers, verified in the GLB JSON, with the `emissiveTexture` binding intact. The
consumer owns intensity, colour and any occupancy schedule, per placed
building. One limitation to state plainly: because the shopfront band tiles,
**every bay of glazing shares its UVs, so no consumer can light one window of
this shop without lighting them all.** That is the right trade for a shop — a
shop's sales floor lighting is one switch — but it does mean this asset cannot
do the scattered-window effect the residential types can. The sign shares the
same material and therefore the same factor: it cannot be switched
independently of the windows either. If a consumer needs the sign on and the
floor off, that needs a second material slot and a re-export.

`variants.png` shows all four colours at `LOD0`, a day row with emission off
above a night row at the reference factor, camera, framing, exposure and colour
management fixed between the two. Rendered in Cycles at 48 samples with
denoising, seed 42; night world (0.24, 0.32, 0.50) at strength 0.08, sun energy
0.12 tinted (0.48, 0.62, 1.0). The light on the pavement in the night row is
**simulated** — it is Cycles' own bounce off an emissive surface in the preview
scene, not something the asset carries. Whether a placed building spills light
is the consumer's lighting and GI, not the mesh's.

### Room-lit panes

Each pane in the emission mask is the lit room behind it, not a flat panel:
`scripts/glazing.py`'s `night_rooms()` multiplies it by its own level, a soft
lamp glow and a falloff toward the floor, and never takes it below about a
fifth. The mask stays neutral grey, so colour, intensity and which buildings
are lit are still the consumer's, and nothing in it says whether a room is
occupied. Averaged over the glass it is 62 % of the old full-white mask
(the catalog runs 52-63 %),
so at the same reference factor the windows read as warm lamplight rather than
pale panels. Every window of one type samples the same atlas region, so every
window of that type carries the same room, and the shopfront repeats its
room from bay to bay.

## Export

`.glb` + external PNG, exported with `export_yup=True`, `use_selection=True`,
`export_apply=True`, `export_keep_originals=True`, cameras and lights off.

Verified in the GLB JSON of **all four tiers**:

- `baseColorTexture` → the default variant's albedo, UV set 0;
- `metallicRoughnessTexture` → `..._orm.png` (G roughness, B metallic);
- `occlusionTexture` → the same `..._orm.png` (R), strength 1;
- `emissiveTexture` → `..._emission.png`, `emissiveFactor [0, 0, 0]`;
- `metallicFactor` 1, `roughnessFactor` 1, `alphaMode` OPAQUE;
- every `image` has a `uri` and **no `bufferView`**.

That last one is not automatic. Blender's exporter, keeping original textures,
writes each image with both a `uri` and a 1x1 placeholder `bufferView`; glTF
permits exactly one source per image and Godot drops images carrying both.
`strip_embedded_images()` from `scripts/glb_images.py` strips the `bufferView` after each
export and leaves the external reference, which is the point — one copy of the
PNGs in `export/`, shared by all four tiers instead of embedded four times.

Pivot: ground level, centred on the plan's bounding box, one authored origin
taken from `LOD0` and applied to every tier. `build_all()` fails the build if
any tier's extents differ from `LOD0`'s by more than 1 mm, so a LOD switch
cannot move the shop. Verified by the validator: min z = 0.0000 and centre
(0.000, 0.000) on all four tiers.

Front faces `-Y` in Blender; `+Y`-up / `+X`-right on export. Checked on
reimport of each tier.

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

Completed in this repository:

- `scripts/validate_asset.py`: no FAIL and no WARN.
- Six pre-export views inspected: orthographic front, rear, east, west,
  top-down, plus a raised three-quarter aerial off the entrance corner, a
  second off the rear, and a third aimed into the loading bay.
- Eye-level views at the entrance and along the street, which is where the
  entrance's frame colours were changed from dark to light anodised: at dark
  the doorway read as a black hole rather than a way in.
- The eave was reviewed and **rebuilt**: it first rose outward, making a
  parapet, and was turned over to fall outward so the deck sheds snow over the
  edge. That change cascaded — the deck dropped from 4.9375 to 4.5625 m, the
  separate shopfront canopy went, the sign moved from a crown to the glazed
  slope, the render panels had to run up into the soffit instead of stopping at
  the wall head, and the deck and skirt were merged into one solid. Each of
  those is covered in its own section above.
- LOD pairs at 35, 70 and 120 m, and `LOD3` at 200 m.
- Mip-3 filtering stress at 75 m, face-on and oblique.
- GLB material bindings and image sources, all four tiers.
- Manifold and hidden-surface checks, all four tiers.
- Glazing measured against Style Direction's band, all four variants.
- Palette: muted red/brown/yellow/grey brick, off-white render, dark grey
  membrane, light anodised aluminium, galvanised plant. No saturated colour
  anywhere except the sign's blue, which is the one thing on the
  building that is meant to be seen from the road. No lighting or reflection is
  baked into any albedo.
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
  `scripts/validate_asset.py` still reports no failures or warnings. The
  rebuilt GLBs changed only in the render panels' side UVs; triangle counts
  are unchanged.
- The render panels' sides, before against after: every tier at 12 m, grazing
  and oblique, under noon. The concrete plinth now runs round each panel's
  foot at the wall's 0.375 m line, where white render used to reach the
  ground.

Pending, and outside this repository:

- Consumer import, LOD switching and runtime emission control.
- Consumer-side mipmap and anisotropic filtering review.
- Performance measurement in a representative scene.

## Tooling versions

- **Blender 5.2.2 LTS** (hash `d13f752e3b9c`, build date 2026-09-15). Recorded
  as a known-good diagnostic, not a pin; the repository's floor is 5.2 and
  `build.py` asserts both that floor and the presence of every glTF exporter
  flag it sets, so an upgrade that renames one fails with a message rather than
  a distant `TypeError`.
- **Blender MCP server addon: not used for this asset.** It was built headless,
  `blender --background source.blend --python build.py`, with the visual
  iteration done on rendered views rather than through a live viewport. The
  feedback loop CLAUDE.md asks for was run — the six views, eye-level views,
  LOD pairs and mip stress above, each fed back into the atlas and the massing —
  but through `render_views()` rather than through MCP screenshots. Anyone
  reproducing this can do the same without the addon installed.
- `source.blend` is saved by 5.2.2, which is why the repository's floor is
  5.2: Blender opens older files and not newer ones. The `.glb` and PNG exports
  are unaffected and stay portable.
- Textures baked standalone with CPython and numpy/Pillow:
  `python3 facade_atlas.py export`.

- **CPython 3.14.7 with numpy 2.5.3, scipy 1.18.1 and Pillow 12.3.0** for the
  texture export.

## Revision log

- **2026-09-25 — weathering.** `facade_atlas.py` gained `weather()`, which
  places the shared `scripts/weathering.py` fields: dirt, algae, rust, faded
  paint and rain runs (Texture set, Weathering). Every albedo and the ORM
  changed; the normal map and the emission mask did not. `source.blend`,
  `preview.png` and `variants.png` were regenerated; the GLBs changed only in
  the render panels' sides, which now wrap the render band instead of the flat
  `reveal_light` patch, so the plinth runs round each panel's foot. Triangle
  counts are unchanged.

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
