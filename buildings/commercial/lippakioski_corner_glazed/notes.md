# lippakioski_corner_glazed

## Style brief

A classic Helsinki-type straight-front canopy kiosk (*lippakioski*), freshly
built and slightly enlarged so customers can also step inside. It is a
general kiosk selling sweets, papers and household small goods, not a grill
or a cafe. It is a generic composite: no real kiosk, business name, chain
colour or trade dress.

- **Body:** a 4.8 x 3.4 m box of narrow vertical ribbed boarding in one
  warm colour, on a low concrete plinth. The front-right corner (`+X`,
  `-Y`) is the serving corner, rounded at R 0.6 m.
- **The canopy (*lippa*), the asset's identity:** a thin flat slab 0.30 m
  thick, white underneath, with rounded plan corners. It projects 1.6 m over
  the front and over the serving side, but only 0.35 m at the rear and the
  left. Its fascia is clad in the same ribs, under a thin galvanised edge
  flashing; the flat felt roof is hidden behind it. Three surface-mounted
  drum downlights hang under the soffit.
- **The serving corner:** a multi-pane glazing band runs from a stainless
  counter at 1.05 m up to the soffit, in dark graphite frames. It covers the
  right half of the front, goes round the rounded corner in slim-mullioned
  facets and along the front of the serving side. The front's middle pane is
  a sliding hatch. The counter shelf follows the band round the corner.
  Folding shutter leaves, enamelled in the wall colour, stand folded open in
  a stack against the wall at each end of the band: their stepped edges,
  hinges and the shadow gap behind them show. Behind the glass, goods stand
  on shelves.
- **Doors:** at the left end of the front, a customer door (one glazed leaf
  with a transom light above it). At the rear, a painted steel staff door
  under a small wall lamp.
- **Sign:** a long, low lit board reading **KIOSKI** (the building type, in
  Finnish), wide-set between two short rules, in a slim galvanised frame on
  two short posts over the canopy's front edge, so a gap shows between the
  board and the flashing. Warm-white lit letters on a graphite face. The
  letters are drawn as stroked centrelines in `facade_atlas.py`, not from a
  font. The side fascia carries no sign.
- **Dressing, all under the canopy:** a wall-fixed newspaper and magazine
  rack on the serving side, two poster cases (abstract blocks, no text) on
  the blank left wall, a wall-fixed bench along the left wall, and a litter
  bin on a short post beside the counter.

## Category and secondary use

`buildings/commercial/`. No secondary use: one small sales room behind the
glazing, which the customer door also opens into.

## Hero/landmark status

Not a hero. Ordinary ceilings and the 1024 texture apply.

## Footprint

All coordinates are in the build frame (`Z` up, front `-Y`), before the
pivot shift.

- **Walls: 4.80 x 3.40 m.** x -2.4..2.4, y -1.7..1.7, with the serving corner
  rounded at R 0.6 m about (1.8, -1.1). The facts footprint is this outline
  at ground level, with `LOD0`'s four chords round the corner. It has eight
  points and an area of 16.24 m².
- **Plan bounds, which every tier shares: 6.75 x 5.35 m.** These are the
  canopy's: x -2.75..4.0, y -3.3..2.05. Its plan corner radii are 0.8 m at
  the front-right, front-left and rear-right corners and 0.3 m at the
  rear-left.
- Everything attached stays inside the canopy's plan: the counter (0.30 m
  out), the shutter stacks (0.10 m), the rack (0.22 m), the bench (0.32 m,
  under the 0.35 m left projection), the lamp (0.14 m) and the bin on its
  post (centre (-0.35, -2.55), r 0.17 m). `check_layout()` asserts this.
- **Heights:**
  - plinth 0.15 m;
  - counter 1.04 m (shelf top), with the band's sill at 1.05 m;
  - glazing and door head 2.84 m;
  - canopy underside **2.85 m**;
  - downlights' foot 2.75 m;
  - felt deck 3.09 m;
  - fascia top **3.15 m**;
  - sign board 3.25–**3.67 m**, on posts over a 0.10 m gap; its top is the
    bounds' height.
- **Clear approach:** the ground in front of the customer door is kept
  clear. Nothing modelled stands within 2 m of the front wall over a 2 m
  width centred on the door (x -2.65..-0.65); only the canopy and the
  downlight hung under it at 2.75 m pass over it. The nearest pieces are the front shutter stack (from x -0.34) and the
  bin (from x -0.52). `check_layout()` asserts this.

## Story height

One storey. Floor to soffit is **2.85 m**, and the canopy top is **3.15 m**.

A kiosk is a single sales room, not a storeyed building. Its height is set by
the canopy, not by a floor-to-floor rhythm. The canopy's top lies inside the
~3.0–3.3 m storey band, so the kiosk stands at one storey's height beside the
catalog's buildings. The 2.85 m soffit is the only ceiling-like line, and
human scale is held by the doors (below).

## Door leaf height

- **Customer door (`kiosk`):** one glazed graphite-framed leaf,
  **0.90 x 2.10 m**, at grade (no step).
  - A drawn transom bar runs from 2.10 to 2.16 m, with a transom light
    above it from 2.16 to 2.78 m and the head frame to 2.84 m. The opening is
    1.04 m wide including its 0.07 m frame.
  - The leaf is recessed 0.10 m at `LOD0`/`LOD1`.
  - The transom bar is level with the glazing band's, so the leaf height
    reads on the front.
- **Staff door (`staff`, rear):** a painted steel leaf, **0.90 x 2.10 m**,
  at grade, cased 0.07 m to 2.17 m and recessed 0.06 m.

In the working views the 1.8 m figure in front of the customer door reaches
86 % of the leaf.

## Window sills

- **Glazing band:** sill **1.05 m**, head **2.84 m**.
  - The 1.05 m sill is a counter's height for a standing customer, under the
    1.4 m chest-high line.
  - A transom bar at 2.10–2.16 m, level with the door's, divides the panes
    into a tall lower tier and a shallow upper one.
  - Pane widths: three panes of 0.53 m on the front, four corner facets of
    0.23 m, and two panes of 0.60 m on the side.
  - The counter at the serving corner is checked against the 1.8 m figure
    standing at it: it reaches the figure's waist.
- **Poster cases** (not openings): 0.70 x 1.12 m from 1.05 to 2.17 m on the
  left wall, above the bench.

## Eave overhang

**None as an eave: the roof is a flat canopy slab.** It projects 1.6 m at
the front and the serving side and 0.35 m at the rear and the left, beyond
the 0.3–0.6 m eave default. That overhang is the building type, not an
eave, and the brief asks for it.

- The fascia is 0.30 m deep.
- There is no gutter: the slab drains inward to a hidden deck behind the
  fascia's flashing, so there are no downpipes.
- The deck's outlet is not modelled.

## Construction

Closed solids and one exact union, `asset_build.union(..., snap=SNAP)`, then
a 0.1 mm weld.

1. **Wall ring** (`build_ring()`): the outline is walked counter-clockwise
   from the front's left corner (front, the corner's chords, side, rear,
   left). Every segment is cut on one shared set of rows,
   `WALL_Z = 0, 1.05, 2.17, 2.84, 3.00`, so the corners carry the same
   vertices from both sides.
   - Each cell is boarding (wall band UV), a flush item (posters; every
     opening at `LOD2`/`LOD3`), or a recessed item with its back face, jambs,
     sill and head.
   - The glazing band is one recess running across the front's end, every
     corner chord and the side's start. Its back faces meet at mitred
     points behind each chord joint, so there are jambs only at the band's
     two ends.
   - The ring is capped by a triangulated floor (round the door notches) and
     by a lid at 3.00 m, which is buried in the canopy.
2. **Canopy** (`canopy()`), built directly as one closed solid:
   - the fascia round the rounded outline;
   - the soffit;
   - on top, the 0.08 m galvanised rim and an inner upstand down to the felt
     deck at 3.09 m (`LOD3`: one flat top).
   - Corner arcs have 6 / 4 / 2 / 2 segments at the 0.8 m corners and
     3 / 2 / 1 / 1 at the 0.3 m corner, by tier.
   - The fascia samples the fascia band all round, the serving side's
     straight run included.
3. **Sign board** (`sign()`): a closed box 2.8 x 0.42 m, 0.07 m deep, its
   face 0.01 m behind the canopy's front edge, centred on the front's
   straight run (x 0.625), from 3.25 to 3.67 m. It stands 0.10 m clear of
   the flashing on two 0.04 m square galvanised posts, 0.40 m in from its
   ends, 0.04 m behind the edge, so they stand on the canopy's 0.08 m rim
   and are sunk 0.04 m into it. Every tier keeps board and posts.
4. **Downlights** (`downlights()`), `LOD0`/`LOD1`: three closed drums
   r 0.13 m (12 sides at `LOD0`, 8 at `LOD1`), an opal band from 2.75 to
   2.805 m and an opal base under a white housing up to the soffit, sunk
   0.02 m into the slab. From `LOD2` the same discs are painted on the
   soffit.
5. **Counter** (`counter()`): a 0.04 m stainless plate from x 0.15 along the
   front, round the corner (outer radius 0.9 m, in the wall's chords) and
   along the side to y 0.15. Top at 1.04 m, 0.30 m proud, 0.05 m into the
   wall.
6. **Shutter stacks** (`shutter_stack()`): 0.52 m wide, 0.10 m proud, from
   1.08 m up into the soffit, against the wall at each end of the band
   (front: x -0.34..0.18; side: y 0.12..0.64). Each is one closed prism
   over a stepped plan (`L.SHUTTER_LAYERS`), at `LOD0`/`LOD1`:
   - a hinge rail 0.42 m wide, from 0.02 m inside the wall to 0.025 m out,
     so a 0.05 m shadow gap shows between the leaves and the wall at each
     side;
   - three 0.025 m leaves, 0.52, 0.496 and 0.472 m wide, so their edges
     step 0.012 m a side.

   `LOD2` keeps one 0.52 x 0.10 m block in the same box.
7. **Furniture:**
   - rack: 0.60 x 0.22 x 0.95 m on the side, y 0.85..1.45;
   - bench: seat 2.0 x 0.32 m at 0.42–0.47 m on the left wall, y -1.1..0.9,
     with two front legs at `LOD0`;
   - litter bin: r 0.17 m, 0.50–1.00 m, on a 0.035 m post;
   - wall lamp: a 0.16 x 0.14 x 0.14 m graphite bulkhead over the staff
     door, its opal lens in the lower part of its face and on its
     underside.

Openings, centre on the outer wall plane, build frame:

| Opening | Wall | Centre | Size | Recess `LOD0`/`LOD1` |
| --- | --- | --- | --- | --- |
| customer door (`kiosk`) | front, y -1.7 | x -1.65 | leaf 0.90 x 2.10, opening 1.04 x 2.84 | 0.10 |
| glazing band | front x 0.2..1.8, corner, side y -1.1..0.1 | see below | 3.736 m along the wall, 1.05–2.84 m | 0.06 |
| staff door (`staff`) | rear, y 1.7 | x 0.90 | leaf 0.90 x 2.10, cased to 2.17 | 0.06 |
| poster cases | left, x -2.4 | y 0.55, -0.45 | 0.70 x 1.12, flush | none |

### Serving counter

The serving counter is a window, not a door, so it is not in the facts
sidecar.

- **Centre**, at the middle of the band's length on the outer wall plane at
  counter height: **(2.058, -1.636, 1.05)** in the build frame, on the
  corner's second chord. That is (1.433, 1.05, 1.011) in the exported
  frame.
- The straight runs' own centres are:
  - front run (1.0, -1.7, 1.05);
  - side run (2.4, -0.5, 1.05).
- **Extent:** front x 0.15..1.80, then the corner, then side y -1.10..0.15.
  The shelf top is at 1.04 m, 0.30 m proud of the wall.

### Roof safety, downpipes, handrails

- **No roof safety kit.** The roof is flat (no slope over 1:8) and carries
  no serviced item: no chimney, no plant, no vent pipe. `scripts/roof_safety.py`
  is not used.
- **No downpipes:** there is no gutter. The slab drains inward.
- **No handrails:** both doors are at grade, with no risers.
- **No chimney.**

### Sign position

KIOSKI cannot go on the 0.30 m fascia: a cap height of at most about
0.22 m fits there, 3.6 px at 35 m with the review camera (16.5 px/m), which
is not legible. A small side-fascia panel with 0.15 m caps was tried and
was a smudge at 35 m by day, so the side fascia carries no sign.

The front sign is a long, low board over the canopy's front edge:

- 2.8 x 0.42 m, a 0.02 m galvanised frame round the face, on two short
  posts over a **0.10 m gap**, so the board reads as a separate signboard,
  not as a block sitting on the slab;
- KIOSKI with **0.32 m caps** as seen (strokes 0.055 m; 5.3 px at 35 m),
  wide-set (tracking 0.55 cap) between two 0.20 m rules, about 2.4 m of
  lettering in all;
- warm-white lit letters (emission (255,226,160)) on a graphite face.

Two treatments were rendered on the same geometry, front and oblique at 20
and 35 m by noon and at night: the one kept, and a lit cream opal face with
graphite letters (`SIGN_STYLE = "cream"` in `facade_atlas.py`). Both read
at 35 m. The graphite face is kept: by day it stands out against the sky and
the white soffit as the darkest thing on the kiosk, and at night only the
letters glow, so the word is the brightest thing in view; the cream face's
whole 1 m² glowed brighter than the glazing and drew the eye to a blank
rectangle. Neither uses a chain's colours.

The board raises the bounds' height from 3.61 to 3.67 m. The canopy stays
a thin slab.

### Authored parameters

All shared numbers live in `facade_atlas.py`: the plan, the canopy radii and
projections, the heights, the band rhythm, the opening sizes and the
furniture sizes. Positions live at the top of `build.py`.

`check_layout()` asserts:

- door leaves inside 2.0–2.4 m, and the order of head, soffit, wall top and
  deck;
- corner margins for both doors;
- band, shutters and rack in order on the side, and posters and bench on the
  left wall;
- every attached piece inside the canopy's plan;
- the customer door's clear approach;
- canopy thickness, and the rim leaving every corner rounded;
- the sign board on the straight part of the front edge, its posts on the
  rim and under the board, a gap of at least 0.06 m, and its capitals clear
  of the frame;
- the shutter stacks' layers inside the stack's box;
- the downlights under the soffit, no lower than 0.10 m below the door
  head, clear of the walls;
- the counter under the sill;
- plan bounds within 7.0 x 5.5 m;
- every region's pixel size against its metres.

The pivot is at ground level at the centre of `LOD0`'s plan bounds. The
build offset is (0.625, -0.625, 0), shared by every tier.

## Per-tier triangle counts

| Tier | Triangles | Ceiling | What it keeps or drops |
| --- | --- | --- | --- |
| `LOD0` | **1,080** | 12,000 | everything: four corner chords, recessed band and doors, 6-segment canopy corners with the hidden deck, sign board on its posts, three 12-sided drum downlights, counter, stepped shutter stacks, rack, bench with legs, 10-sided bin on a 6-sided post, wall lamp |
| `LOD1` | **890** | 4,000 | canopy corners 4 segments; downlights 8-sided; bench legs dropped; bin 6-sided on a 4-sided post; the rest as `LOD0` |
| `LOD2` | **248** | 1,500 | two corner chords; openings painted flat; canopy corners 2 segments; downlights painted on the soffit; counter, rack, bench, bin and lamp dropped; shutter stacks as plain blocks, sign board and posts, and the deck's rim kept; coplanar splits dissolved |
| `LOD3` | **166** | 500 | one chord (a chamfer) at the wall's corner; shutter stacks dropped; canopy as `LOD2` but with one flat top and no sunk deck; sign board and posts kept |

The triangles go mostly to the canopy (its rounded fascia, rim, upstand and
deck, which the union splits round the walls, the sign's posts and the
downlights), to the recessed glazing band across the corner chords, and at
`LOD0`/`LOD1` to the drum downlights and the stepped shutter stacks, which
with the sign's posts account for the rise from the earlier 732 / 616 /
220 / 130. The rest is small closed solids.

That is a little above the catalog's small-commercial range (300–1,000 at
`LOD0`), for a 4.8 x 3.4 m kiosk under a large canopy whose soffit, lamps and
shutters are seen at eye level. Every tier is a separate reduction. `LOD3`
differs from `LOD2` in the wall corner, the deck and the shutters.

## LOD review

Setup: `scripts/review_asset.py` on the exported tiers.

- Perspective, 1920 x 1080, 50° vertical FOV, Cycles, 24 samples.
- Distance is measured along the view direction to the front wall's centre.
- Views: front (12° up) and oblique (40° round, 30° up), under noon.
- All four tiers at 20, 35, 70 and 120 m, rendered from the final build.
- Renders are in
  `review/small_shops_2026_11_22/lippakioski_corner_glazed_polish/lod/`,
  with pair sheets in `lod_front_pairs.png` and `lod_oblique_pairs.png`.

| Switch | Distance | Verdict |
| --- | --- | --- |
| `LOD0` → `LOD1` | 35 m | Indistinguishable. Two fewer canopy segments per corner and 8-sided downlights do not show at the switch; the bench legs and the bin's sides are sub-pixel. |
| `LOD1` → `LOD2` | 70 m | The recesses go flat; the counter, bin, bench and rack go; the downlight drums become painted discs and the shutter stacks plain blocks. The counter was a one-pixel light line here, so the band loses a faint underline; the drums and the stacks' steps are under a pixel. The glazing stays a dark band framed in graphite, the canopy keeps its shape, and the sign on its posts stays a readable block. Accepted. |
| `LOD2` → `LOD3` | 120 m | The chamfered corner, the flat roof top and the dropped shutter blocks cannot be told apart at ~130 px wide. |
| `LOD3` up close | 20 m | Reviewed because a consumer switching by screen size can show the last tier near. The chamfer reads as a corner, the canopy's corners as polygonal and the band as flat. The kiosk is still recognisable: thin asymmetric canopy, dark serving corner, ribbed ochre walls, the KIOSKI board on its posts. |

- The default switch distances are kept, with no override.
- Kept on every tier: the canopy's asymmetric plan and rounded corners, its
  thin white-soffited slab, the sign board, the glazing band's extent and
  rhythm, the doors' positions, the ribbed boards, the plinth, and the dark
  glass.
- The glazing band sits in the canopy's shadow, so it reads darker than the
  walls from raised oblique views. That matches the building type.

**Pending:** runtime switching and performance in a representative consumer
scene.

## Interior geometry

`scripts/validate_asset.py`'s sampled hidden-surface test and welded
manifold check are summarised under Review status.

- The shell is closed by construction: a closed ring and a closed canopy
  unioned with closed solids.
- The union removes the buried parts: the wall's top inside the slab, the
  counter's and the hinge rails' 0.02–0.05 m in the wall, the sign posts'
  feet in the rim and heads in the board, the downlights' tops in the slab,
  the bench and rack backs.
- The shutter stacks run 0.03 m up into the soffit. An earlier build left a
  5 cm gap there, whose top faces were hidden triangles.
- **The test's 5 hidden triangles on `LOD0`/`LOD1` (0.5 %, 0.2 m²)** are the
  hinge rails' sides in the shadow gap behind each shutter stack: 0.025 m
  deep, 0.05 m wide, 1.8 m tall. They are exterior surface, open to the
  air, in a slot too narrow for the test's 40 fixed rays; kept, since the
  gap is the point of the rail. `LOD2`/`LOD3`: 0 hidden.
- The door recesses have no floor of their own; the ring's floor closes under
  them.
- No closure faces are kept apart from the recessed glass and leaves, which
  are exterior surface.

## Known simplifications

- **Shutters:** only the open, folded stacks are modelled. The band cannot be
  shown shuttered; that would be a second state, and textures only, never
  geometry, change per variant. The leaves' hinges and panel lines are
  painted; the stack's steps and shadow gap are modelled.
- **Glazing:** opaque. The goods on their shelves are painted into the
  albedo as the room behind the glass, not modelled.
- **Texture-only detail:** the ribs, the board joints, the fascia's flashing
  and drip, the plinth's drip, the hatch's sashes, the push bar, the
  transom bar and the door hardware.
- **Soffit:** the downlights are plain drums with no trim ring; their sheet
  joints are painted. From `LOD2` the downlights are painted discs.
- **Roof:** the deck's outlet is painted (a galvanised ring round a dark
  grate, with a ponding stain), not modelled. There is no roof hatch or
  penetration: the kiosk is serviced from the ground.
- **Sign:** the stand-off posts are plain square bars, with no brackets.
- **Litter bin:** a plain prism with no lid detail or liner.
- **Rack:** the magazine covers are abstract colour blocks, with no titles or
  brands.

## Texture set

One 1024 atlas, supersampled `atlas.SS` = 4 per axis and box-filtered in
linear light.

Seven unique PNGs, all 1024 x 1024 RGB 8-bit:

- four albedos, one per variant;
- `_orm.png`, `_normal.png` and `_emission.png`, shared by every variant.

### Layout

Rows are V, counted up from the bottom.

- **Wall band**, rows 0–192, the full width, tiling in U (z 0–3.0 m at
  64 px/m):
  - plinth in rows 0–9.6, under a galvanised drip;
  - ribbed boarding above;
  - the soffit's shadow line just under 2.85 m.

  U runs round the wall outline as `LOD0` measures it, so the ribs carry on
  round the corner chords. The one seam is at the front-left corner.
- **Fascia band**, rows 198–217.2 (0.30 m), tiling in U:
  - ribs in the wall colour;
  - the galvanised flashing in the top 1.6 rows;
  - a drip at the foot.

  U runs round the canopy outline from the rear-left corner, where its seam
  hides.
- **Regions:**

  | Region | Size (px) | Mapping |
  | --- | --- | --- |
  | soffit, with its sheet joints every 1.2 m and the three downlight discs | 432 x 342 | plan, 64 px/m |
  | roof deck, felt in 1 m rolls inside the rounded rim, the outlet | 216 x 171 | plan, 32 px/m; also `LOD3`'s flat top |
  | glazing band | 239 x 115 | U is s along the band |
  | customer door | 67 x 182 | |
  | staff door | 67 x 139 | |
  | two poster cases | 45 x 72 each | |
  | shutter stack's front, all leaves | 33 x 115 | U along the wall |
  | shutter stack's side, rail and leaf edges | 8 x 115 | U outward from 0.02 m inside the wall |
  | rack face | 38 x 61 | |
  | bench top | 128 x 20 | |
  | wall lamp's face | 10 x 9 | |
  | sign board's face | 358 x 54 | 128 px/m |

  There are also thirteen 16 px flat patches, among them the downlights'
  opal and white housing.

  `check_regions()` keeps 4 px between regions. `check_layout()` holds each
  region's pixel size to its metres.

### Texel density

64 texels/m on the walls, the fascia, the soffit, the openings and the
dressing. The deviations are:

- the **sign board's face at 128**, so the stroked letters stay clean;
- the **deck at 32**, seen only from above.

### Relief and normal map

`atlas.normal_map()`, OpenGL (+Y green up), from the height channel, glass
flat. Relief heights:

- ribs 6 mm, at a 50 mm pitch (3.2 px; 320 to the sheet, so the bands
  tile), every eighth groove a board joint only a little deeper in tone;
- window frames 20 mm;
- flashing folds 10 mm, the sign's frame 10 mm;
- bench slats 8 mm;
- the pass rail and push bar 20–30 mm;
- shutter hinges 10 mm, the leaves' arrises 4 mm;
- felt laps 3 mm;
- sign letters 4 mm.

The ribs read as raised in the lit renders.

### Texture scale against the catalog

The rib pitch measured on the baked normal map (FFT along a wall row and a
fascia row) is **50.0 mm** (3.2 px), inside the 40–60 mm the brief allows.
Front renders at 20 and 35 m with identical `review_asset.py` settings,
cropped at native pixels beside `lahikauppa_corner`'s, show the same
sharpness at 64 px/m: frames, plinth and glazing bars are the same pixel
weight. The ribs are near the review camera's resolution at 20 m (2.9 px a
rib) and average to a flat colour by 35 m, as fine ribbing should. Before
this revision the board joints every eighth rib were 14 % darker and each
0.4 m board took its own tone, which read as wide planks at 20 m; the
joints are now 6 % darker and the board tones within ±0.6 %, so the wall
reads as one fine ribbed surface.

### Padding and filtering

`atlas.pad()` fills every unclaimed texel from the nearest region's edge, in
every channel. Each band holds only its own ids (`check_bands()`).

The mip stress review is under Review status.

### Weathering

`scripts/weathering.py` at its moderate level (`weather()`):

- a light grime film;
- paint fade on the boards, shutters, steel door and bench;
- faint rain wash on the boards;
- soil and algae at the plinth, and splash over it (the wall band's V is
  height, so this is exact on every wall);
- sheltered dust under the soffit;
- runs under the fascia's flashing;
- a little dust on the soffit, and dust on the deck;
- door wear at the push bar, handle and foot;
- dust on the band's sill frame and pass rail;
- wear on the bench seat;
- dust in the rib grooves (cavity).

The glass, the signs, the posters, the magazines, the downlights and the lamp
lens stay clean.

## Glazing treatment

- Measured by the validator over the neutral emission mask: **glass sRGB 56,
  linear 0.035**, in all four variants.
- Roughness `glazing.ROUGHNESS` **0.08**, metallic 0.
- Painted with `scripts/glazing.py`: `rooms()` on the finished albedo and
  `night_rooms()` on the emission mask.
- After `rooms()`, `goods()` paints the stock into the band's panes, albedo
  only: dim shelf edges at 1.32, 1.62, 1.92 and 2.48 m, and rows of packets
  in muted colours, mixed at the unlit room's level (45 % room, 55 % of the
  packet colour at 0.4). The measured mean above includes them.
- The casing is the graphite frame **(72, 74, 76)**, set a step above the
  glass so no pane measures brighter than its casing. The counter
  (stainless) and the boards are lighter still.
- No departure from the Style Direction band.

## Variant list

Low-rise, so four albedos on one mesh. Only the boarding changes: walls,
fascia ribs and shutter leaves (shutters at 0.94 of the board colour,
enamelled at roughness 0.46 against the boards' 0.70). The soffit, frames,
plinth, flashing, doors, sign, posters and dressing are the same in all.

| Variant | Boards (sRGB) | Meaning |
| --- | --- | --- |
| `ochre_boards` (default) | (178,152,102) | muted warm yellow ochre: hue 40°, saturation 0.43 |
| `cream_boards` | (210,198,166) | cream |
| `green_boards` | (126,138,114) | muted grey-green |
| `red_boards` | (146,84,64) | muted red ochre |

None is yellow-and-blue or any chain's colours. The ochre was (176,142,84)
(hue 38°, saturation 0.52), which rendered orange-brown under the warm
review sun; it is now a little lighter, yellower and less saturated, so it
reads as painted ochre boarding, not orange.

## Night lighting

`lippakioski_corner_glazed_emission.png` is shared by every tier and variant.

- **Candidate glazing**, neutral grey, each pane its own lit room
  (`glazing.night_rooms()`):
  - every pane of the glazing band;
  - the customer door's leaf glass and transom light.

  The staff door, frames, walls, canopy and roof are black. The painted goods
  are not in the emission.
- **Luminous fixtures**, each in its own warm colour (channel spread far over
  24), which the validator reports as 19,193 coloured mask pixels, not
  glazing:
  - the KIOSKI letters and rules on the board **(255,226,160)**; the
    graphite face and its frame stay dark;
  - the three downlights **(255,212,146)**: at `LOD0`/`LOD1` the drums'
    opal band and base (the `light` patch), from `LOD2` the painted soffit
    discs;
  - the staff door lamp's lens, the lower part of its face and its
    underside **(255,194,118)**.
- **Eye-level check** (1.6 m camera, about 10 m off the serving corner, at
  night with emission on): the three drums glow as round lamps under the
  white soffit, at their plan positions in front of the door, in front of
  the band and on the serving side; the board's letters glow; the wall lamp
  reads as a bulkhead with a lit lens. Before this revision the downlights
  were flush 0.18 m discs that showed from there only as thin slivers. The
  glow is the emissive surface only: Cycles lets emissive faces light the
  scene, so the review renders show a faint bounce on the soffit and the
  ground, but no light spill is part of the asset.
- **Reference lit factor:** linear **(1.0, 0.88, 0.72)**, a fluorescent shop
  interior as the catalog's other shops use.
- **Control:** the exported `emissiveFactor` is `[0, 0, 0]` on all four tiers,
  with the `emissiveTexture` binding intact. The consumer owns intensity,
  colour and schedule.
  - Glazing, sign, downlights and lamp share one material and one factor, so
    they switch together. Separate control would need a second material slot
    or the consumer masking UV regions.
  - The lamp is modelled through `LOD1`. From `LOD2` it is gone, and so is
    its glow; this is recorded.
- **`variants.png`:** all four colours at `LOD0`, a day row (emission off)
  over a night row at the reference factor, by
  `scripts/variant_previews.render_sheet()` (Cycles, camera and exposure
  fixed between rows). The light on the ground in the night row is the
  preview scene's bounce, not part of the asset. Light spill is not
  simulated otherwise.
- Night renders of the reimported tiers are under Review status.

**Pending:** consumer emission control and light spill.

## Export

`.glb` plus external PNGs, through `asset_build.Asset.export_all()`. The
export settings:

- `export_format='GLB'`, `use_selection=True`, `export_yup=True`,
  `export_apply=True`;
- `export_keep_originals=True`, then `strip_embedded_images()`;
- cameras and lights off;
- the emission factor rewritten to zero.

Traced in `LOD0`'s GLB JSON chunk. One material, `lippakioski_corner_glazed`,
with these bindings:

- `pbrMetallicRoughness.baseColorTexture` → `..._albedo_ochre_boards.png`;
- `pbrMetallicRoughness.metallicRoughnessTexture` → `..._orm.png`;
- `occlusionTexture` → `..._orm.png` (the same texture);
- `normalTexture` → `..._normal.png`, default scale 1;
- `emissiveTexture` → `..._emission.png`, `emissiveFactor [0, 0, 0]`.

No multiplying factors or `texCoord` are written, so everything uses UV set
0. Every image has a `uri` and no `bufferView`. One sampler: mag linear
(9729), min linear-mipmap-linear (9987). Attributes: `POSITION`, `NORMAL`,
`TEXCOORD_0`, with no tangents.

The validator checks the image references, the emission binding and the
normal binding on every tier. Front `-Y` in Blender becomes `+Z` front, `+Y`
up on export, as the reimported review renders show.

Rebuild from the repository root:

```bash
python3 buildings/commercial/lippakioski_corner_glazed/facade_atlas.py export
blender --background buildings/commercial/lippakioski_corner_glazed/source.blend \
    --python buildings/commercial/lippakioski_corner_glazed/build.py
blender --background --python buildings/commercial/lippakioski_corner_glazed/build.py -- facts
```

The first line bakes the textures (system Python with scipy and Pillow). The
second builds the tiers, exports, renders the previews and writes the
sidecar. The third rewrites the sidecar alone, from a committed tree.

The facts sidecar (version 1) holds:

- the wall outline at ground level as the footprint (eight points, with
  `LOD0`'s corner chords);
- one storey of 16.24 m² at floor 0;
- 0 dwellings, hero false;
- `kiosk` (entrance, main): exported (-2.275, 0, 1.075), facing `+Z`,
  0.90 x 2.10 m;
- `staff` (service): exported (0.275, 0, -2.325), facing `-Z`,
  0.90 x 2.10 m.

## Review status

Completed here:

- **Working views** (`render_views()`), in three passes at `LOD0`, and at
  `LOD1`–`LOD3`:
  - the four orthographic elevations and the top;
  - a 45° three-quarter aerial off the serving corner, and one off the rear;
  - eye-level views off the front and off the serving corner, with 1.8 m
    figures at the customer door and at the counter.

  Each pass was critiqued against the brief and the building type:
  - **Pass 1:** the canopy's thickness, projection and rounded plan corners
    read as a lippakioski at a glance, and so do the glazed serving corner
    with its counter following the corner, and the ribbed warm walls. The
    door leaf reads against the figure, the counter is at waist height, the
    glass is darker than its graphite frames, the furniture sits under the
    canopy, and there are no holes.
  - **Pass 2:** the ochre was muted from (184,146,80) to (176,142,84). The
    wall lamp gained a front lens. The shutter stacks were run up into the
    soffit, closing the 5 cm gap behind the test's only hidden triangles.
  - **Pass 3:** the canopy's top rim was narrowed from 0.12 to 0.08 m. From
    above it had read as a thick band rather than a thin edge flashing.
- **Polishing round** (Revision log), with a before set rendered from a copy
  of the previous asset and an after set with identical settings, compared
  with `review_compare.py` (front and oblique at 20, 35 and 70 m by noon;
  20 and 35 m at night with emission on), and an eye-level set (1.6 m
  camera, 10–11 m off the serving corner, the front and the rear, and one
  under the canopy's edge; night and noon) from a script in the review
  folder that uses `review_asset.py`'s scene. Two passes of working views
  at `LOD0`, and at `LOD2`/`LOD3`:
  - **Pass 1:** the drums, the sign on its posts and the stepped shutter
    stacks read at eye level and in the elevations; the side fascia reads
    cleanly without its panel. The felt laps were too faint from the
    oblique views.
  - **Pass 2:** the felt laps were made lighter and wider and the rolls
    given more tone; the shutter leaves' edge gaps were darkened so the
    steps read on the front elevation.
- **Sign:** two treatments compared at 20 and 35 m, front and oblique, noon
  and night (Construction, Sign position); KIOSKI reads at 35 m in both.
- **Texture scale** against `lahikauppa_corner` at 20 and 35 m (Texture
  set).
- **LOD pairs** at 20, 35, 70 and 120 m, front and oblique, noon, all from
  the final build, with `LOD3` reviewed at 20 m (LOD review).
- **Night**, `review_asset.py --lights night --emission on` at 20 and 35 m,
  and at eye level (Night lighting): the panes, the door, the board's
  letters, the three downlights and the wall lamp glow.
- **Mip-3 stress:** `review_atlas_mips.py` with `review_asset.py
  --texture-dir`, `LOD1` and `LOD2` at 70 m, front, oblique and grazing,
  noon, after the atlas layout changed. No colour leaks and no dark seams.
  The ribs average to a flat colour. The fascia, rim and sign keep their
  colours, the board's letters stay apart, and the glass stays dark.
- **`scripts/validate_asset.py`:** 0 FAIL. The one WARN is the facts
  sidecar's `source.dirty`, which clears when the sidecar is rewritten from a
  committed tree. On every tier:
  - welded manifold: 0 boundary, 0 edges with more than two faces, no loose
    geometry;
  - hidden-surface test: 5 hidden triangles on `LOD0`/`LOD1`, the hinge
    rails' sides in the shutter stacks' shadow gap (Interior geometry); 0
    on `LOD2`/`LOD3`;
  - glazing in the band (sRGB 56, 0.25 x trim);
  - bindings, triangles, pivot and sidecar consistent.
- **GLB material bindings** traced (Export).
- **Palette:** muted boards (the ochre checked against the palette rule,
  Variant list), a white soffit, graphite frames and sign, galvanised and
  stainless trim. The only saturated colour is the posters' and magazines'
  small blocks. No baked light or reflection in any albedo.
- **Generic composite:** no real kiosk's name, chain colours or trade dress,
  and nothing traced. The textures are generated.

Pending, outside this repository:

- consumer import, LOD switching and emission control;
- consumer filtering review;
- performance in a representative scene.

## Tooling versions

- **Blender 5.3.0** (hash `02f0899d78e3`, built 2026-11-11), built headless:
  `blender --background source.blend --python build.py`. `source.blend` is
  saved by 5.3.0.
- **Blender MCP addon: not used for this build.** Every view was rendered
  headless with `render_views()` and `scripts/review_asset.py`.
- Textures: CPython 3.14.10, numpy 2.5.5, scipy 1.18.1, Pillow 13.0.0.

## Revision log

- **2026-11-22, polishing round.** Downlights modelled as drums (r 0.13 m,
  `LOD0`/`LOD1`), lit and checked at eye level. Sign rebuilt as a 2.8 x
  0.42 m board in a galvanised frame on two posts over a 0.10 m gap
  (was 2.2 x 0.46 m sunk into the slab), 0.32 m caps as seen, KIOSKI
  between rules; height 3.61 → 3.67 m. Side-fascia panel removed. Shutter
  stacks modelled as stepped leaves on a hinge rail with a shadow gap,
  hinges painted, enamel sheen. Rib board joints and tones softened (rib
  pitch measured 50 mm, unchanged). Ochre (176,142,84) → (178,152,102).
  Soffit sheet joints, felt laps and a painted outlet on the deck, the wall
  lamp's lens moved to the lower part of its face. Triangles 732 / 616 /
  220 / 130 → 1,080 / 890 / 248 / 166. Plan bounds, pivot, footprint,
  doors and variants unchanged.
