# voimalan_konttori_brick

## Style brief

The office and control building of a small Nordic town's coal-fired heat and
power plant (*voimalan konttori*: the power plant's office), 1950s-60s. It
is one of the plant's separate buildings and holds its main entrance:
visitors and staff come in here, and the plant is run from the control room
on its ground floor. A generic composite of the type, not a portrait of any
one building.

- **Two storeys, 14 x 9 m**, long side to the front, red facing brick on a
  cast concrete plinth, in restrained post-war functionalism: a light cast
  band at the first floor right round the building, plain brick otherwise.
- **A flat roof** behind a 0.375 m brick parapet with a galvanised sheet
  coping, drained inside through two outlets in the deck: the box of an
  institutional or industrial building, not a house or a school.
- **Windows in bands of white steel lights.** Upstairs one continuous ribbon
  along each long side, 12 m of 1.5 m lights, brick only at its ends, a
  side-hung vent sash in every other light. Downstairs the control room's
  taller band of four lights fills the east half of front and rear, a row
  of top-hung vents across its head; the offices' two-light windows speak
  the same language smaller. One two-light window to each storey on the
  ends.
- **The main entrance** on the front, one bay west of the middle: a pair of
  glazed teak leaves under a transom light in a cast concrete surround,
  under a thin slab canopy carried 2.75 m out from the first-floor slab on
  two slim square steel posts, up three steps with a handrail.
- **The staff door** to the boiler house: a steel door on the rear, up
  three steps with a handrail.
- **Roof:** a galvanised ventilation housing, a short radio mast with a
  small directional aerial for the control room, two plain vent pipes. The
  housing is serviced from the roof, so a caged wall ladder climbs the west
  end next to its rear corner.

No signage, lettering or company marks anywhere on it: the plant's hall
carries the name.

## Category and secondary use

`buildings/industrial/`, as part of a heat and power plant. Secondary use:
**offices** (upper floor and the ground floor's west end) and the plant's
**control room** (ground floor, east half).

## Hero/landmark status

Not a hero. Ordinary triangle ceilings and the 1024 texture cap apply, and all
are met.

## Footprint

- **Walls: 14.0 x 9.0 m** (outer faces at x = +-7, y = +-4.5).
- **Coping:** 14.125 x 9.125 m, oversailing the walls by 0.0625 m.
- **Canopy:** 2.9 m wide, 2.75 m off the front wall, at 3.5-3.75 m; its
  two posts 0.15 m in from its outer corners, 0.8 m beyond the foot of the
  steps.
- **Steps:** front 2.6 m wide, 1.8 m out; rear 1.8 m wide, 1.6 m out.
- **Wall ladder:** on the west end, its cage standing 0.84 m off the wall.
- **Overall plan extent: 14.905 x 13.35 m**, the ladder's cage to the east
  coping, the canopy's edge to the rear steps. Coping top at 7.375 m;
  overall height **9.78 m** to the mast's aerial (8.375 m to the ladder's
  top, 7.94 m to the housing's lid).

The pivot is the centre of that plan box at ground level, 0.39 m west and
0.575 m in front of the walls' own centre: the cage stands further out west
than the coping does east, and the canopy further out than the rear steps.

## Story height

Two storeys. **Ground floor at 0.5 m** on the plinth, which shows 0.625 m
above the ground; **first floor at 3.75 m**: a **3.25 m** storey. The roof
deck is at **7.0 m**: **3.25 m** over the first floor. Both inside the
3.0-3.3 m band.

## Door leaf height

- **Entrance: a pair of 0.75 m leaves, 1.5 x 2.125 m clear**, in a
  1.625 x 2.6875 m opening; above the leaves a transom bar and a **0.5 m
  transom light** in two lights to the head, drawn in the atlas region. A
  0.1875 m cast surround runs round the jambs and 0.375 m over the head, up
  into the canopy.
- **Rear staff door: leaf 1.0 x 2.125 m**, plain steel with a small vision
  panel, in a 1.125 x 2.1875 m opening, the top 0.0625 m being the frame's
  head.
- Both thresholds are at the floor, 0.5 m; the landing in front of each is
  3 cm lower, at 0.469 m.

## Window sills

Heights above each storey's floor (ground floor at 0.5 m, first at 3.75 m):

- **Upper ribbon, 1.4375 m tall:** sill **0.875 m**, head 2.3125 m (6.0625 m
  above the ground). The head is 0.94 m under the deck and 1.31 m under the
  coping. A head 0.3-0.5 m under the coping, as first asked, does not fit
  the kept storeys: with the deck at 7.0 m it would need a 2.6 m upper
  storey or a ribbon 2.2 m tall; the slab, a lintel and the parapet take the
  difference.
- **Control-room band, 1.9375 m tall:** sill **0.75 m**, head 2.6875 m: the
  same head line as the entrance (3.1875 m above the ground), so the room's
  desks and panels look out over the yard.
- **Ground-floor office windows, 1.6875 m tall:** sill **1.0 m**, head on
  the same line; 0.56 m over the door leaf's head.
- Every ground-floor head is 0.31 m under the slab band; every upper sill
  0.875 m over it.

## Eave overhang

**None: a flat roof behind a parapet.** The galvanised coping oversails the
parapet's faces by 0.0625 m, with a folded drip; the rainwater goes down
two internal outlets in the deck, so there is no gutter and no downpipe.

## Construction

Closed solids unioned with Blender's exact boolean (`asset_build.union`):

1. **the shell**: four wall regions walked counter-clockwise, ground to
   7.3125 m, each opening built into its region as reveals round a closing
   plane (cut tiers) or flat quads (flush tiers), the ring capped by a
   floor on the ground and, at the top, the parapet's 0.25 m thick top, its
   inner faces down to the deck, and the deck at 7.0 m, so it is a solid of
   the building's whole volume with the roof sunk in it;
2. **the coping**: one closed ring 0.125 m deep, 7.25-7.375 m, oversailing
   both faces of the parapet by 0.0625 m; the parapet's top runs 0.0625 m
   up into it;
3. **the canopy**: a 0.25 m slab sunk 0.1 m into the front wall at the
   painted slab band's height, and **two 0.08 m square steel posts** from
   the ground into it;
4. **two flights of steps**, profiles extruded across the doors, their backs
   sunk 0.05 m into the wall below each threshold;
5. **two handrails** from `scripts/handrails.py`;
6. **the roof plant**: the ventilation housing (1.5 x 1.5 x 0.94 m), the
   mast and its aerial, two vent pipes, each sunk 0.1 m into the deck;
7. **the wall ladder and its cage** from `scripts/roof_safety.py`.

The union trims everything into the shell and leaves the boundary of one
empty volume. A 0.1 mm weld follows; at `LOD2` and `LOD3` a limited dissolve
(0.001 rad, UV seams kept) recovers coplanar boolean subdivisions. On
`LOD3` the ladder's bare rails and the cage's back strap are appended after
that (`roof_safety.append`).

Every number the mesh and the atlas share is in `facade_atlas.py`: the plan
(HX = 7, HY = 4.5), the floor, slab band, deck, coping, sill, leaf,
entrance and canopy heights, the parapet's thickness (PIN = 0.25), each
window band's light width and height, and every opening's size and reveal.
`build.py` keeps the elevations' opening lists, the canopy, post, step,
rail, plant and ladder positions, and `check_layout()`, which fails the
build if:

- an opening (the entrance with its surround) comes within 0.4 m of a corner
  or 0.3 m of another opening, within 0.4 m of the deck, or into the slab
  band;
- the ribbon's or the control band's mullions leave 1.2-1.5 m, the ribbon
  leaves 1.3-1.45 m tall, or the control band is not taller than the
  offices' windows;
- a leaf leaves 2.0-2.4 m, the entrance has no transom light, any sill
  leaves desk height, either storey leaves 3.0-3.3 m, or the parapet leaves
  0.3-0.5 m over the deck;
- the canopy leaves the surround, is not wider than it, leaves 2.5-3 m out,
  comes within 0.25 m of a window or does not cover the landing, or a post
  stands within 0.3 m of the steps;
- the entrance steps are narrower than the surround, or a riser exceeds
  0.18 m;
- a handrail crowds its door or its foot post leaves its tread
  (`handrails.problems()`);
- a piece of roof plant comes within 0.4 m of the parapet, 0.3 m of another
  or 0.4 m of an outlet;
- the ladder or its cage crowds a corner or a window of the west end
  (`roof_safety.problems()`).

### The parapet and the deck

The parapet is the walls' brick carried 0.3125 m above the deck. Its inner
face samples the upstand band (the deck's felt dressed up over a cant to a
termination bar under the coping), its top is buried in the coping. The
coping's ring carries a face, a top and a drip underside; it oversails the
deck side by the same 0.0625 m. The deck is level in the mesh; its falls to
the outlets are in the paint.

### Window bands

A band of n lights is one opening n light widths long, with one set of
reveals. Its closing plane is split at every mullion into n quads, each
mapped onto its own light's region (`facade_atlas.light_kind`): every light
carries half a mullion at each side, so two neighbours make a whole one and
the band's ends get a frame of the same width. The band's outline carries
the split points along its sill and head, so the sill and head reveals and
the wall around meet the lights on shared vertices. The ribbon alternates a
fixed light with one carrying a 0.44 m side-hung vent; its two-light end
windows are two fixed lights, since a vent between two lights read as a
house's casement. The control band and the offices' windows carry a
0.375 m row of top-hung vents across every light, one line along the
ground storey.

### The entrance

The entrance region in the atlas holds the cast surround and the doors
together. At `LOD0`/`LOD1` the surround is a U of concrete on the wall face
round the opening, the wall's hole is the surround's outline with the
opening's foot corners on it, and the reveals are concrete, the threshold
a grey sill. At `LOD2`/`LOD3` the whole surround is one quad. The canopy's
underside cuts the surround 6 cm below its top, so the two read as one
piece, and the canopy's fascia lines up with the painted first-floor band,
so it reads as the slab carried out over the door. Its two posts stand at
the outer corners, in line with the steps' sides and clear of them.

### Steps and handrails

Three risers of 0.156 m to a landing 1.2 m (front) or 1.0 m (rear) deep,
two 0.3 m treads below it. Three risers, so a handrail on each flight, on
the right going up (`scripts/handrails.py`, `MODES` unchanged: `LOD0` and
`LOD1`). The rails take the coping's galvanised colour (`PIPE_STRIP`, the
middle rows of the coping's top). The steps stay on every tier.

### Roof plant and the ladder

The ventilation housing over the stair is serviced from the roof, so the
deck needs a fixed route up (CLAUDE.md): a wall ladder only, the deck being
level. At the back, but the rear wall's ribbon leaves no run clear of
openings, so it climbs the blank part of the west end, 1.2 m from the rear
corner, out of the catalog view. It runs from the ground to 1.0 m above the
coping, **8.375 m**, over `roof_safety.CAGE_LADDER` (8 m), so it carries the
script's cage, hoops from 2.5 m. The kit samples `PIPE_STRIP` like the
rails. `roof_safety.MODES` and `CAGE_MODES` unchanged: every rung and hoop
at `LOD0`, thinning through `LOD2`; `LOD3` keeps the bare rails and the
cage's back strap, which set the plan's west extent. The mast and vents are
not serviced items.

### Rainwater

Internal drainage: two outlets painted in the deck at x = -3 and 3, y = -1.5,
with ponding stains round them. With no gutter there is no downpipe
(CLAUDE.md); an outlet piped down the outside was judged to add nothing the
box needs.

## Per-tier triangle counts

Measured on the exported GLBs by `scripts/validate_asset.py`:

| Tier | Triangles | Ceiling | Shell | Ladder and cage | Handrails | Mast and vents | Posts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `LOD0` | 2640 | 12,000 | 674 | 1408 | 312 | 214 | 32 |
| `LOD1` | 2136 | 4,000 | 674 | 920 | 312 | 198 | 32 |
| `LOD2` | 864 | 1,500 | 372 | 430 | 0 | 26 | 36 |
| `LOD3` | 412 | 500 | 372 | 24 | 0 | 16 | 0 |

Shell = walls with their 16 openings and 48 lights, the parapet, deck,
coping, canopy, steps and the ventilation housing; the split was measured by
rebuilding each tier without the rails, then the kit, then the mast and
vents, then the posts. The shell is a simple box, so the count is low for
two storeys (the catalog's two-storey terraces sit at 3,000-4,500). Over
half of `LOD0` is the 8.4 m caged ladder, `roof_safety.py`'s shape at its
default tiers, and the rails cost 312 more because their posts cut into the
treads: both scripts' output, left as they are. `LOD2` flattens the
openings and drops the rails and the mast; `LOD3` keeps only the ladder's
bare rails and strap, the larger vent, and drops the posts.

## LOD review

- **Switches:** `LOD0` under 35 m, `LOD1` 35-70 m, `LOD2` 70-120 m, `LOD3`
  beyond; no overrides.
- **Camera:** `scripts/review_asset.py`, perspective, 50 degree vertical FOV,
  1920 x 1080, distance along the view direction to the front wall.
- **Pairs compared:** every tier at 30, 70 and 120 m, front and oblique,
  noon; six orthographic views and the day cycle at `LOD0`.
- **Results:**
  - `LOD0`/`LOD1`: indistinguishable at 30-40 m; only the rungs, hoops and
    the vents' side counts change.
  - `LOD1`/`LOD2`: the flattened reveals lose their 0.15-0.2 m shadow line,
    about 2 px at 70 m, the handrails and the 6 cm mast go. The white
    frames and mullions, the slab band, the coping line, the canopy and its
    posts keep the bands' rhythm and the entrance.
  - `LOD2`/`LOD3`: at 120 m the ladder's rungs and the canopy's posts (about
    1 px) and the small vent go; the box, the coping line, the housing and
    the bands are unchanged.
- **The entrance at 40 m:** the light surround, the canopy and its posts and
  the steps are the only light vertical mark on the front and read as the
  way in from the front and the oblique, on every tier.
- **Geometry exceptions:** the handrails, the ladder and its cage, the
  posts and the mast, under the relief threshold, modelled per CLAUDE.md or
  as the canopy's and the control room's structure, on the tiers given
  above.

## Interior geometry

The shell is the boundary of one unioned volume, so there are no partitions
or duplicate surfaces. Hidden-surface test:

- **`LOD0`:** 32 of 2640 triangles flagged (1.2%), 0.1 m2 vertical. Most
  are the underside of the coping's inner lip, a 6 cm strip 0.25 m over the
  deck that the test's downward rays all find blocked by the deck or the
  upstand; then the back face of the front handrail's landing post, 5 cm
  off the brick, and the ladder's bracket ends at the wall. Exterior
  surface in narrow gaps, not buried faces.
- **`LOD1`:** 26 of 2136, the same.
- **`LOD2`:** 17 of 864, the coping's lip.
- **`LOD3`:** 24 of 412 (5.8%), 2.2 m2 vertical: the coping's lip, and the
  wall-facing sides of the ladder's bare rails and the cage's strap,
  0.17-0.8 m off the wall, which the rays from them all meet the wall.
  Exterior, seen from the side.

Kept closure faces: none visible. The floor cap is on the ground and the
parapet's top inside the coping, and the union removes them.

## Known simplifications

- Glazing bars, sashes, frames, the doors' glazing, kick plates and pull
  bars, the transom bars: textured.
- The deck is level; its falls, laps, outlets and gratings are painted.
  The upstand and its termination bar, the coping's joints and drip fold
  are painted on their faces.
- The first-floor slab band and the plinth's formwork joints are painted
  flush; the cast surround is flush, its arrises in the normal map.
- Windows and doors are flat at `LOD2`/`LOD3`.
- The housing's louvres are painted; it has no duct. The mast has no guys
  or cable.
- The vent pipes have no flashing collars at the felt.

## Texture set

- **1024 x 1024, 64 texels/m**, `atlas.SS` = 4 supersampling, lossless 8-bit
  RGB PNGs. One deviation: the deck region is 32 texels/m, seen only from
  above.
- **Bands** (tile in U, each starting on a 16-row boundary, 12 or more rows
  clear of the one below, so no mip 4 texel mixes two):
  - BRICK 0-468: cast plinth to 0.625 m with formwork joints, stretcher
    bond 0.25 x 0.078 m, the cast slab band at 3.5-3.75 m with tie holes
    every metre, brick to the parapet's top at 7.3125 m with the coping's
    shadow under its drip. Every wall samples it by its height from the
    ground, and its U runs on round the corners.
  - COPING 480-512: the coping's 0.125 m face with its drip fold, then its
    0.375 m top; lapped joint straps every 2 m. `PIPE_STRIP` = rows
    494-506, the top's middle.
  - UPSTAND 528-548: the felt dressed up the parapet's inner face over a
    cant, a termination bar, flashing under the coping.
  - CANOPY 560-576: the canopy's painted sheet fascia with its drip.
- **Regions** (from row 592): the entrance with its surround (128 x 196),
  the staff door, one light each of the ribbon (fixed, and with a side
  vent), the control band and the offices' windows, cast concrete for the
  steps and the canopy's top (2.625 x 2.0 m), the vent pipe and its open
  end, the housing's louvred side; the deck (432 x 272 at 32 px/m) and
  flat patches from row 744.
- **Relief** for the normal map: brick 6 mm, slab band 4 mm proud of the
  brick, frames and mullions 30 mm, vent sashes 45 mm, coping straps 6 mm,
  felt laps 4 mm, the deck's cant 20 mm, cast surround 15 mm, louvre blades
  20 mm, door rails 40-50 mm. Glass flat.
- **Weathering** at the moderate level through `scripts/weathering.py`:
  plinth soil, splash-back and salt bloom on the height band, dirt on the
  slab band's top with faint runs under it, a sheltered band and faint
  runs under the coping, dust on the coping, dirt at the upstand's foot,
  blotchy dirt on the deck and ponding stains round the outlets, runs on
  the canopy's fascia, dirt on the windows' bottom rails, door feet and
  handles, worn concrete, sooty vent pipes, dirt at the housing's foot.
- **Padding:** `atlas.pad()` last; `check_regions()` and `check_bands()`
  guard ownership.
- **Filtering:** review renders at 70 and 120 m on every tier (LOD review);
  the coping, slab band and window frames survive, no band leaks into
  another. A mip stress pass with `scripts/review_atlas_mips.py` was not
  repeated for this revision.
- **Unique textures:** 3 albedo + ORM + normal + emission = 6 PNGs at
  1024 x 1024.

## Glazing treatment

`glazing.rooms()` on the finished albedo: measured by the validator at
**sRGB 53 (linear 0.031)** in every variant, 0.24-0.26x the surrounding
trim. ORM roughness `glazing.ROUGHNESS` (0.08), metallic 0. Inside the Style
Direction band; no departure.

## Variant list

Low-rise, so three brick variants on shared geometry and UVs. The names
match the plant's other brick buildings:

- **`red_brick`** (default): the plant's shared red, white frames,
  teak-brown entrance leaves, grey-green steel staff door. The brick is the
  original red pulled 40% toward its own Rec.709 luma per channel and
  darkened by 0.94 (`facade_atlas.plant_brick`), the mortar a further 10%
  darker, as on the plant's other pieces: brick (115, 75, 63), darker
  brick (92, 61, 53), mortar (125, 123, 118). Mean plain-wall albedo
  sRGB (112, 83, 73): **R - G = 29**.
- **`yellow_brick`**: buff brick, white frames, darker teak, a green-grey
  staff door.
- **`brown_brick`**: brown brick, off-white frames, mid-brown teak, a
  brown-grey staff door. Mean plain-wall albedo (110, 83, 70), now close to
  the recoloured red's.

All three keep the felt deck, the galvanised coping, housing, ladder and
rails, the light canopy fascia, the dark steel posts, and the grey concrete
plinth, slab band, surround, canopy and steps. ORM, normal and emission are
shared.

## Night lighting

- **Mask:** `voimalan_konttori_brick_emission.png`, shared by every tier and
  colour: every window light, the entrance leaves' glazing and the transom
  lights, and the staff door's vision panel, each painted neutral grey by
  `glazing.night_rooms()`. Frames, brick, concrete and the roof are black.
  No sign or lamp is luminous.
- **Reference lit factor: linear (1.0, 0.88, 0.72)**, fluorescent office and
  control-room light, as the catalog's other offices.
- **Default off:** `emissiveFactor [0, 0, 0]` in all four tiers, with the
  `emissiveTexture` binding intact.
- **Control:** one factor per placed building. Each kind of light shares one
  region, so no window, and not the control room alone, can be lit by
  itself.
- **`variants.png`:** the three colours at `LOD0`, a day row (emission off)
  above a night row at the reference factor, by `scripts/variant_previews.py`
  with camera, framing, exposure and colour management fixed. Light on the
  ground in the night row is the preview's bounce, **simulated**; spill is
  the consumer's.
- **Pending in the consumer:** off/on behaviour on reimported tiers, distant
  filtering under emission, LOD switches when lit.

## Export

`.glb` + external PNGs through `scripts/asset_build.py`:
`export_format='GLB'`, `use_selection=True`, `export_yup=True`,
`export_apply=True`, `export_keep_originals=True`, `export_cameras=False`,
`export_lights=False`. Emission is exported lit and the factor rewritten to
zero. `strip_embedded_images()` removes the placeholder `bufferView`s.

Checked by the validator on all four tiers:

- one mesh, one material slot;
- `baseColorTexture` → `voimalan_konttori_brick_albedo_red_brick.png`;
- `metallicRoughnessTexture` and `occlusionTexture` → `..._orm.png`;
- `normalTexture` → `..._normal.png`, scale 1, no tangents;
- `emissiveTexture` → `..._emission.png`, `emissiveFactor [0, 0, 0]`;
- every image a `uri`, no `bufferView`.

Pivot: ground level, centre of `LOD0`'s plan bounds, applied to every tier.
Front faces `-Y` in Blender, `+Z` in the exported glTF frame.

The facts sidecar `export/voimalan_konttori_brick.model.json` lists:

- **footprint:** the 14 x 9 m outer wall faces; the coping's oversail, the
  canopy and its posts, the steps and rails and the caged ladder stand
  outside it;
- **storeys:** two, floors 0.5 m and 3.75 m, 126 m2 each (the upper one
  under the flat roof, 3.25 m to the deck);
- **dwellings:** 0;
- **doors:** `entrance` (main, kind entrance, front, the pair 1.5 m clear)
  and `staff` (kind service, rear).

Rebuild:

```bash
cd buildings/industrial/voimalan_konttori_brick
python3 facade_atlas.py export                          # every PNG in export/
blender --background source.blend --python build.py     # tiers, GLBs, preview, variants, sidecar
```

## Review status

Completed in this repository:

- `scripts/validate_asset.py`: 0 FAIL. One WARN: `source.dirty` on the
  sidecar, built from an uncommitted tree.
- `check_layout()`, `check_regions()` and `check_bands()` pass on every
  build.
- **Views inspected** at `LOD0`: the six pre-export views (orthographic
  front, rear, east, west and top, and a raised aerial off the front-east
  corner), plus a rear aerial and eye views at the entrance, at the staff
  door and along the front; the same set at `LOD3`.
- Every tier at 30, 70 and 120 m, front and oblique (LOD review); day cycle
  (morning, noon, dusk, night with emission) at `LOD0`; before/after sheets
  against the hipped-roof version with `scripts/review_compare.py`.
- Glazing measured against the band in all three colours.
- **Palette:** muted red, buff and brown brick; white steel frames; a grey
  felt deck; galvanised coping and kit; grey concrete. No saturated colour,
  and no baked light in any albedo.
- **Scale:** the door leaves are 2.125 m; the sills were checked against
  them and against both floors (Window sills).

Pending, outside this repository:

- Consumer import, LOD switching and runtime emission control.
- Consumer-side mipmap and anisotropic filtering; a mip stress pass for
  this revision.
- Performance in a representative scene.
- Placement beside the plant's other buildings, whose palettes this
  asset's variants are named to match.

## Tooling versions

- **Blender 5.3.0** (hash `02f0899d78e3`, built 2026-11-11), headless. This
  is a known-good diagnostic, not a pin. `source.blend` is saved by 5.3.0.
- **Blender MCP addon: not used.** Built and reviewed headless with
  `blender --background`, `build.py`'s `render_views()`,
  `scripts/review_asset.py`, `scripts/review_compare.py` and
  `scripts/validate_asset.py`.
- **CPython 3.14.10 with numpy 2.5.5, scipy 1.18.1 and Pillow 13.0.0** for
  the texture bake.

## Revision log

- **2026-11-21:** the hipped felt roof with eaves, gutter and four
  downpipes replaced by a flat roof behind a coped parapet, drained inside;
  residential casement-and-transom windows replaced by bands of steel
  lights (an upper ribbon, the control band, the offices' windows); the
  canopy lengthened from 1.5 to 2.75 m on two steel posts; roof plant and a
  caged wall ladder added; `red_brick` recoloured to the plant's shared red.
