# Metrum Models — CLAUDE.md

## Project Overview

Standalone AI-assisted 3D asset-authoring repository. An AI agent drives a
local Blender through an MCP (Model Context Protocol) server: it interprets
reference imagery, issues `bpy` operations, checks viewport renders, and
iterates toward game-ready meshes.

Output: exterior building shells (massing, roofline, facade texture), props
(street furniture, lighting, boundary pieces) and road vehicles, with
colour/material variants that share geometry where appropriate. No
interiors, rigging or animation: a vehicle's wheels and lamps are moved and
lit by the consumer from ids in its mesh (Vehicles).

The repository has its own git history, licence and workflow, and depends on no
other project's source, tooling, files or directory layout. Its primary
consumer is Metrum Rise; the coordinate conventions and budgets below match
that pipeline without depending on it.

## Style Direction

### How to apply this guidance

- **Hard requirements:** exterior-only assets, coordinates and pivots, required
  LODs, material and texture formats, licensing, export validation.
- **Art-direction defaults:** scale, palette, detail allocation. An exception
  needs documented views at the intended distances and must stay within the
  applicable ceilings.
- **Performance budgets are provisional.** Ceilings are authoring limits, not
  runtime acceptance. Changing them requires representative consumer-workload
  evidence.
- **Asset-specific lessons belong in that asset's `notes.md` or code**, not
  here. Construction techniques described here are examples unless stated as
  requirements.

### Visual target

Semi-realistic and grounded: legible silhouettes and believable proportions, so
building type, density and wealth read at normal play-camera distance.
Weathered, physically plausible materials with convincing light response.
Quality comes from texture and material craft within the Output Contract
budgets; style ambition never raises a ceiling.

- **Proportions over polycount.** Texture repeated shallow detail (window trim,
  brick coursing, panel seams). Model massing, opening depth, and features that
  visibly change the silhouette or lighting at intended distances. Thresholds
  are in Geometry and Construction; map roles in Texture Requirements.
- **Story height: ~3.0–3.3 m per floor**, the same across styles, so 4- and
  6-storey buildings read correctly side by side. Deviate only for an authored
  reason (e.g. a taller retail ground floor) and record it in `notes.md`.
- **Doors anchor human scale and do not stretch with storeys.** Door leaf
  **2.0–2.4 m**, up to ~2.6 m for a ceremonial civic entrance. A taller opening
  needs a **fanlight or transom above the leaf**, with a drawn or modelled
  transom line so the leaf height stays readable. Consumers may scale a building
  by matching its doors to characters, so an oversized door silently rescales
  the whole asset against the rest of the catalog.
  - Size windows against the door: a sill above ~1.4 m reads as chest-high.
  - **Fewer, larger windows.** On short walls (gable ends, porches, dormer
    fronts) prefer one large window per storey to two smaller ones side by
    side; a gable carries one window downstairs and one upstairs, besides any
    door. An entrance gable, with the front door centred on its ground
    storey, may instead carry one window on each side of the door, mirrored
    about it: the door splits the storey, so the three read as a door between
    flanking windows, not as a pair. Long walls are the exception and may
    carry several.
  - Props and vehicles have no doors to scale by; check them against a
    1.8 m standing figure instead.
- **Material palette:** muted, realistic brick, stucco, concrete, weathered
  wood, glass, metal trim, with believable baked wear and grime
  (`scripts/weathering.py`, Texture Requirements). No flat, clean,
  saturated "toy" colours, and no photoreal decay that suggests abandonment.
  Applies to every class; a vehicle's painted panels are neutral grey, and
  the consumer paints them (Vehicles).
- **ORM (occlusion/roughness/metallic) is required for every asset.** Roughness
  separation between glass, concrete and metal trim carries much of the realism
  at this budget.
- **Glass is an opaque, closed-shell approximation:** neutral to slightly cool,
  low-saturation, nonmetallic.
  - **Base colour sRGB 45–70 per channel** (linear ~0.02–0.06), **never
    brighter than the trim or casing around the opening.** Glass that measures
    brighter than its casing is the usual symptom of getting this wrong.
  - **Roughness 0.05–0.12**, metallic 0.
  - From outside, a window is mostly the unlit room behind it; the renderer
    adds the sky reflection from roughness and the dielectric F0, so a pale base
    colour counts the sky twice and the pane reads as glossy white paint. The
    reasoning is in `scripts/glazing.py` and the
    [glTF material model](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#appendix-b-brdf-implementation).
  - **Paint panes with `scripts/glazing.py`, not a flat fill:** call `rooms()`
    on the finished albedo, after the id/shade/AO pass. It finds panes from the
    glass mask and gives each its own level, a falloff toward the floor and a
    lit patch of far wall, so windows match across the catalog. By night,
    `night_rooms()` does the same for the emission mask (Output Contract).
  - Variation that is the *room* (per-pane level, curtains, a lit interior
    wall) is allowed in albedo. Reflections, sun highlights and fixed sky
    gradients are not (Texture Requirements).
  - Calibrate under daylight, shade and oblique views; verify in the consumer
    when available.
  - These are defaults. A brief may call for something else (shopfronts,
    mirror-glazed towers, boarded windows); record the values and the reason in
    `notes.md`.
- **Colour/material variants stay within this palette:** per-building
  diversity, not stylistic range. See Color & Material Variants — Buildings,
  Props and Vehicles.
- **Sign lettering is Finnish:** the generic word for the business
  (`APTEEKKI`, `PARTURI`, `KAMPAAMO`, `KIOSKI`) or a fictional name, never a
  real brand or a chain's colours. Period matters: a sign form the era did
  not have (a barber pole on a 1980s shop) dates the building wrongly.

## Target Consumer

- The eventual output is game content packs. Packaging, pack manifests and
  pack tooling belong to the consumer.
- Handoff is by files: the `.glb` tiers, the textures and the facts sidecar
  `export/<asset_name>.model.json` (Output Contract), which the consumer's
  importer reads. The sidecar states geometry and files only and names no
  consumer concept; nothing here depends on the importer.
- This document owns per-class coordinates and budgets, so authoring and checks
  do not depend on consumer tooling.

## Scope

- **Classes: buildings (exterior shells only), props and vehicles.** No
  interiors, opening door/window meshes, rigging, animation or characters.
  One exception is reserved: a vehicle's optional, separate interior mesh
  (Vehicles).
- **Props v1: street furniture and lighting** (benches, bins, bollards,
  mailboxes, planters, lamp posts) and **boundary pieces** (wall runs,
  piers, gates) that the consumer assembles round a lot. Add signage,
  kiosks, shelters etc. only when work on them starts.
- **Vehicles:** cars, vans, trucks and buses in `vehicles/`, with their own
  section. The animation scope is settled: no rig; the consumer spins and
  steers the wheels and lights the lamps from ids in the mesh. Trailers,
  emergency and service vehicles get their rules when work on them starts.
- **Characters stay excluded.** They need real animation, typically baked to
  vertex animation textures; decide first whether that belongs here at all.

## Tech Stack

- **Blender 5.3 or newer.** This is a floor, not a pin; newer releases are
  expected to work. The newest of the catalog's `source.blend` files are saved
  by 5.3, and Blender cannot open files saved by a newer version, so 5.3 is
  the lowest version that can work on all of them (the MCP extension itself
  installs on 5.1).
  `asset_build.check_toolchain()`, which every `build.py` calls, asserts the
  floor as `BLENDER_MIN`. Record the actual version in `notes.md`.
- **Blender MCP server addon**, bound to `localhost` only. The MCP client
  (Claude Code) issues `bpy` calls, scene queries and viewport screenshots. In
  practice: the Blender Lab "MCP" extension's local socket server, driven by a
  separate MCP server process.
- **Git LFS** for all binary assets (`.blend`, `.glb`, texture images).
- **Python libraries:** numpy, scipy and Pillow for texture generation;
  shapely is available for 2D plan work. Official Blender builds bundle their
  own Python with numpy only, so anything `build.py` imports (an asset's
  `facade_atlas.py`, `scripts/atlas.py`) imports scipy and Pillow inside the
  functions that need them, never at module level. Only numpy is imported at
  the top.
- No engine toolchain: Blender, the MCP addon, the shared `scripts/` and
  optional per-asset scripts. Code is licensed separately from art (Licensing).

## Repository Structure

```text
metrum_models/
  buildings/
    residential/
      <asset_name>/
        source.blend        # authoring file, all LOD tiers as separate objects/collections
        build.py             # required; cleaned-up bpy build, not a session transcript
        <other>.py           # optional; further scripts for this asset alone, e.g. facade_atlas.py (texture generator)
        export/
          <asset_name>_lod0.glb
          <asset_name>_lod1.glb
          <asset_name>_lod2.glb
          <asset_name>_lod3.glb
          <asset_name>_albedo_<variant>.png   # one per colour/material variant, always named, e.g. _albedo_red_brick.png
          <asset_name>_orm.png                # required; shared by all variants (_orm_<variant>.png only if a variant changes the pattern)
          <asset_name>_normal.png             # required; shared likewise (_normal_<variant>.png only if the pattern changes)
          <asset_name>_emission.png           # night-lit buildings (the default for glazed buildings); see Output Contract
          <asset_name>.model.json             # required; geometry facts sidecar written by the build, see Output Contract
        notes.md             # see Notes.md & Catalog Template below — no reference material, images or prose
        preview.png          # required; LOD0, default variant, standard daytime catalog setup
        variants.png         # night-lit: day/night rows; other multi-variant assets: day row
    commercial/
      <asset_name>/           # same per-asset layout as residential/
    industrial/
      <asset_name>/           # same per-asset layout as residential/
    service/
      <asset_name>/           # same per-asset layout as residential/
    agricultural/
      <asset_name>/           # same per-asset layout as residential/
  props/
    street_furniture/
      <asset_name>/
        source.blend        # authoring file
        build.py             # required; cleaned-up bpy build, not a session transcript
        <other>.py           # optional; e.g. bench_atlas.py (texture generator)
        export/
          <asset_name>_lod0.glb
          <asset_name>_lod1.glb
          <asset_name>_lod2.glb               # optional for props, see Props
          <asset_name>_albedo_<variant>.png   # always named for its finish, even with one texture set, e.g. _albedo_green_steel.png
          <asset_name>_orm.png                # required; shared by all variants unless the pattern changes
          <asset_name>_normal.png             # optional; bound on every tier when present
        notes.md
        preview.png          # required; same standard preview setup as buildings
        variants.png         # night-lit: day/night rows; other multi-variant assets: day row
    lighting/
      <asset_name>/           # same per-asset layout as street_furniture/
    boundary/
      <asset_name>/           # as street_furniture/, plus _lod2.glb, _lod3.glb and the facts sidecar
  vehicles/
    car/
      <asset_name>/
        source.blend        # authoring file; each tier's pieces in <asset_name>_parts, wheels with the origin at the wheel centre
        build.py             # required; the parts, their ids and facts() for vehicle_build.VehicleAsset
        <other>.py           # required texture generator, e.g. car_atlas.py; also writes glass_texels.png
        export/
          <asset_name>_lod0.glb               # ... _lod3.glb, all four; ids in COLOR_0, see Vehicles
          <asset_name>_albedo_<variant>.png   # plain, and any livery
          <asset_name>_orm.png                # required
          <asset_name>_emission.png           # required: lit lenses and the lit cabin
          <asset_name>_normal.png             # optional
          <asset_name>_interior.glb           # reserved, optional; not built yet
          <asset_name>.model.json             # required; version 3, kind vehicle
        glass_texels.png     # required; the atlas's glass texels for the validator, not shipped
        notes.md
        preview.png          # required
        variants.png         # day/night rows
    van/
      <asset_name>/           # same per-asset layout as car/
    truck/
      <asset_name>/           # same per-asset layout as car/
    bus/
      <asset_name>/           # same per-asset layout as car/
  scripts/                  # helper scripts that are genuinely reusable across assets — see below
  CATALOG.md                 # running list of finished assets, one line each, linking each asset's preview.png as a browsable visual index
  .gitattributes             # LFS patterns
  .gitignore                 # Blender autosave/backup files, untracked local working material, etc.
  LICENSE.md                 # CC BY 4.0 for repository content; see Licensing
  README.md                  # public overview; CLAUDE.md is the contract
  AGENTS.md                  # symlink to CLAUDE.md
  CLAUDE.md
```

**Categories:** `residential/`, `commercial/`, `industrial/`, `service/`,
`agricultural/` under `buildings/`; `street_furniture/`, `lighting/` and
`boundary/` under `props/`; the body classes `car/`, `van/`, `truck/` and
`bus/` under `vehicles/`, fixed by the class boxes (Vehicles). Add
categories when needed. A mixed-use building
goes under its primary category, with the secondary use recorded in
`notes.md`.

**Names:** descriptive `snake_case`, e.g. `lowrise_brick_corner`; no numeric
IDs, no repeated category. The folder path is the asset's only identity, so the
name must stand alone.

**Asset-specific scripts stay with their asset; `scripts/` is for code a second
asset can call unmodified.** `build.py` and texture generators describe one
asset (region constants, palette, artwork). The atlas pixel layout and the UV
constants in `build.py` are the same numbers; keep them adjacent (e.g.
`build.py` imports `facade_atlas.py`) so a change to one prompts a check of the
other. When the same function appears in two assets' scripts, move it to
`scripts/`. Everything a `build.py` does that does not describe its building
(the toolchain check, the material, the export, the previews, the tier
bookkeeping, the facts sidecar's writing and the headless entry point) is
`scripts/asset_build.py`'s: `build.py` keeps the massing, UVs, layout checks
and its `facts()` and hands the rest to one `asset_build.Asset` (a vehicle's
to `vehicle_build.VehicleAsset`, its subclass).

### Shared scripts

| Script | Role |
| --- | --- |
| `atlas.py` | Rasterises every atlas: a supersampled `Canvas` with id, shade, AO and height channels, rect, bevel and shape primitives (stroke, disc, rounded rect), and `pad()`; periodic `noise()`; `cavity()`; and resolvers for albedo, ORM, normal map and emission (Texture Requirements); and the layout bookkeeping every generator shares: `region_problems()` for a `check_regions()`, `paint_patches()` for flat cells, `pad_periodic()` for a band that wraps in V. |
| `lettering.py` | The catalog's one sign alphabet: stroked-centreline capitals and figures (`GLYPHS`) on a unit em, `text()`, `text_width()`, `centred_text()` (ink-gap tracking at any weight, opt-in `join=` ligatures) and `arc()`. A new sign adds its missing letters here; no asset keeps its own glyphs. numpy only. |
| `weathering.py` | Weathering as per-sample fields (dirt, algae, rust, faded paint, rain runs, coal dust) that the canvas carries through `pad()` and `atlas.albedo()`/`orm()` resolve per variant, with helpers for a plinth, splash-back, a sheltered eave, runs under a drip, a roof band, a window and a door. Each atlas's `weather()` places them. |
| `brickwork.py` | The catalog's facing brick on an `atlas.Canvas`: the module (0.25 m stretcher on a 0.078125 m course, 16 x 5 px at 64 texels/m), `bond()` (course, brick index and joint masks over sample grids, for a painter that tones its own bricks) and `paint()` (toned stretcher bond over a rect; `y_ref=` counts courses from another row such as a chimney's cap, the darker and mortar ids are each optional (joints then stay on the brick id), `tone=`, `joint_shade=`, and `arris=` for a rounded brick edge in the height channel). Called by texture generators and `boundary_wall.py`; a painter on another module stays with its asset. |
| `asset_build.py` | The shared half of every `build.py`: `check_toolchain()`, the catalog preview constants, `open_stack()` (a chimney or stack open at the top round a sooted flue), `union()` (the exact boolean, which triangulates any keyhole face it returns round a hole before the build's weld can fold it; opt-in `snap=SNAP` first puts the operands on a 0.1 mm grid) and `difference()`, its subtracting twin, and an `Asset` (`night_lit=False` for one without lit regions; `pivot=` and `levels=` for a prop; `id_attribute`, set by `VehicleAsset`, exports a corner colour attribute as `COLOR_0`, compression off, rewritten as exact bytes) with `material()`, `build_all()`, `export_all()`, `render_preview()`, `render_variants()`, `write_facts()` (each door's floor measured on `LOD0`) and `main()`; and the door probes the facts and the validator share: `reveal_depth()`, `door_floor_state()` (the slab rule) and `threshold_floor()` (a door's `floor_y_m`). Runs inside Blender only. |
| `shell_build.py` | The mesh kit a building's `build.py` builds its closed solids with: `Builder` (a bmesh with a position-keyed vertex cache, faces with UVs in atlas pixels and a double-precision area test; `digits`, `snap`, `uv_point`), `Frame`/`InwardFrame` (a wall plane), `fill_planar()`/`fill_region()` (regions with holes, slivers repaired), `recess()`, `prism()`/`box()`/`circle()`, `rim_loops()`/`cap()`/`close_solid()`, `uv_patch()`/`uv_region()`, `rect_poly()`, `dedupe()`, `overlap()`, `item_rects()`, and `render_views()` (the six working views plus `orbit()`/`look()` views and a 1.8 m `figure()`). Face and vertex order match the copies it replaced, so a migrated asset exports byte-identically. Runs inside Blender only. |
| `model_facts.py` | The facts sidecar `export/<asset_name>.model.json`: its schema, the build-frame to glTF conversion, `wall_door()` (`floor=` and `storey=` override a door's measured floor and derived storey), `lane_passage()` and `roof_clear_width()` for a `build.py`'s `facts()`, `compose()` (its `floor_of` measures each door's floor, `storey_of()` derives its storey)/`write()`, and `check()`, which `validate_asset.py` runs on the file: version 4 for buildings and boundary props; version 3 (`kind: vehicle`) with `compose_vehicle()`, `wheel_part()`, `lamp_lens()`, `glass_group()`, `cargo_box()`, `side_doors()`, `rear_door()` and `interior_file()` for vehicles. Pure Python (numpy for vehicles). |
| `boundary_wall.py` | The brick perimeter wall pieces of `props/boundary/`: their shared 512 atlas (`export`, written into each piece's `export/`), the joint rule, `Run`/`Pier`/`Gate` and their four tiers, layout checks and facts; each piece's `build.py` names its piece and calls `piece_asset()`. |
| `rintamamiestalo.py` | The four `buildings/residential/rintamamiestalo_*` houses' shared half: their atlas (`Layout`, each house's optional regions and band rows; `paint()`/`export()`, run by each house's `facade_atlas.py`) and, inside Blender, `Kit` (walls and openings from `Wall` tables, gable slabs, the open chimney, canopy, steps, `tier()` with the union and cleanup, the common layout checks, `door()` for `facts()`); the tier policy (`ITEM_MODES`, `CANOPY_LAST`, `RAMP_FROM`, `DISSOLVE_FROM`), the ORM table (`SURFACE`) and the night `TINT` live here once. Each house's `build.py` names its layout and keeps its own massing. |
| `vehicle_ids.py` | The vehicle contract's numbers and the ids as they ship: class boxes, ceilings, atlas sizes, the part, lamp and glass tables, `encode()`/`decode()`, a GLB accessor reader (`tier()`), `convert_color0_to_ubyte()`, `steer()`, the lens axes, and `save_glass_texels()`/`load_glass_texels()`. numpy only; runs in Blender and in system Python. |
| `vehicle_build.py` | The vehicle half of `asset_build`: `Builder` (faces with surface and paint ids), `patch_face()`, `wheel_solid()`, `conform()` (inserts T-junction vertices and removes the edges it leaves without faces), `to_object()`, `Piece`, the id attribute's writing and checks, the paint and lamp-gate preview nodes, and `VehicleAsset` (`build_all()`, `write_facts()`, `material(paint=, lamps=)`, `steer()`). Runs inside Blender only. |
| `glazing.py` | Paints glass as the room behind it: `rooms()` on the finished albedo by day, `night_rooms()` on the emission mask by night. Called by texture generators. |
| `downpipes.py` | Downpipes as swept, mitred closed solids for `build.py` to union: a `Pipe` placed on a wall, swan-neck and shoe, UVs on the atlas's painted gutter (`PIPE_STRIP`), per-tier `MODES`, and `problems()` for `check_layout()`. Runs inside Blender only. |
| `roof_safety.py` | Roof safety equipment as closed solids for `build.py` to union: the wall ladder and its safety cage, the roof ladder and the walkway, UVs on the painted gutter (`PIPE_STRIP`) or a fixed patch, per-tier `MODES`, and `problems()` for `check_layout()`; an opt-in lean wall ladder and cage (`lean=True`), separate solids that cut nothing, added after the weld by `append(check=True)` at a fraction of the triangles. Runs inside Blender only. |
| `handrails.py` | Handrails on entrance flights as closed solids for `build.py` to union: one rail on posts, on the right going up (`side="left"` where that is blocked), level along the landing and down the nosing line, UVs on `PIPE_STRIP` through `roof_safety.Paint`, per-tier `MODES`, and `problems()` for `check_layout()`; an opt-in lean rail (`lean=True`), appended like the lean ladder. Runs inside Blender only. |
| `door_floor.py` | The concrete floor slab of every opening recessed at grade (Geometry and Construction, Openings): `T` (0.02 m) once; a `Floor` (its atlas region at the reveal's width and depth, the worn path and the occlusion at its edges); for the texture generator `COLOUR`, `SURFACE`, `paint()`, `grain()` and `weather()`; for `build.py` `notch()` (the wall foot's detour), `recess()` (the nosing on the wall plane, then `shell_build.recess()` from the slab's top, which is the reveal's foot) and `problems()` for `check_layout()`. numpy only at import; `recess()` runs inside Blender. |
| `window_emission.py` | Wires the emission mask into the material (`attach`, `set_state`), rewrites an exported GLB's emission factor (`rewrite_glb_emission`, which `asset_build` uses to ship it default-off), holds the reference `LIT_FACTOR`. |
| `glb_images.py` | `strip_embedded_images()`: removes the `bufferView` the exporter leaves beside each image `uri`; `asset_build`'s export runs it on every tier (Texture Requirements). |
| `variant_previews.py` | `render_sheet()`: the day/night (or, for unlit assets, day-only) `variants.png`, called by `asset_build`. |
| `validate_asset.py` | Mechanical export checks (Validation Checklist), a building's door floors probed on every tier and each door's `floor_y_m` against `LOD0` among them; the vehicle classes add `vehicle_checks.py`. |
| `vehicle_checks.py` | The vehicle checks on the exported files, for `validate_asset.py`: accessors, sidecar, PNGs and `glass_texels.png`, with exact point-to-triangle distances for steer clearance. numpy and Pillow. |
| `review_asset.py` | Renders exported tiers in a disposable scene: day cycle, LOD distance pairs, views, light states, optional mip textures, another colour by `--variant`. Run in a separate background Blender. |
| `review_atlas_mips.py` | Writes temporary atlas mips for filtering stress renders (`review_asset.py --texture-dir`). |
| `review_gallery.py` | Contact sheets and an HTML gallery from `review_asset.py` output. |
| `review_compare.py` | Before/after sheets and an HTML page from two `review_asset.py` runs with identical settings; `--ignore-distance` pairs by view where the fitted distance changed, `--pad` centres differing sizes. |
| `review_vehicle.py` | The vehicle review sheet (Vehicles) from the exported accessors, frames and a contact sheet. Run in a separate background Blender. |

Each script's docstring gives its command line.

## Notes.md & Catalog Template

`notes.md` records what later work would otherwise have to reconstruct. Its
sections are the `##` headings below, spelled and ordered exactly as given, so
any asset's notes can be diffed against any other's.
`scripts/validate_asset.py` checks presence, spelling and order, not content.
An unlisted `##` heading is a schema error, including a reference-policy
section (Reference Image Policy keeps references out of notes).

**Buildings — required, in order:**

1. **Style brief:** the design intent / generation prompt.
2. **Category and secondary use:** category folder, plus secondary use for
   mixed-use buildings.
3. **Hero/landmark status:** whether a budget exception is used, and why.
4. **Footprint:** actual width x depth in metres, including projecting windows
   and porticos.
5. **Story height:** actual per-floor height; explain departures from
   ~3.0–3.3 m.
6. **Door leaf height:** always recorded, with any fanlight/transom height
   separately.
7. **Window sills:** sill and head heights, checked against the door leaf and
   the occupied floor.
8. **Eave overhang:** projection in metres or "none"; explain departures from
   0.3–0.6 m.
9. **Construction:** massing method, resolved roof joins, and the authored
   parameters the tiers derive from.
10. **Per-tier triangle counts:** every tier, `LOD0` through `LOD3`, against its
    ceiling; where the triangles go, and why the count differs from comparable
    catalog assets if it does by much.
11. **LOD review:** intended switch distances, camera projection, vertical FOV
    or orthographic size, resolution, views; distance overrides, geometry
    exceptions, visible transition limitations. Keep authoring review separate
    from consumer performance measurements.
12. **Interior geometry:** hidden-surface findings, what was removed, and which
    closure faces are deliberately kept.
13. **Known simplifications:** what the shell does not model, and which
    features the textures carry instead.
14. **Texture set:** texel density and deviations, atlas layout and padding,
    supersampling factor, the relief heights the normal map is derived from,
    filtering/mip review, and the number and size of unique textures across
    variants.
15. **Glazing treatment:** measured glass base colour and roughness, and the
    treatment (`scripts/glazing.py` by default). Record any brief-driven
    departure from the Style Direction band, with the reason.
16. **Variant list:** names and meanings.
17. **Night lighting:** emission map and bindings, default state, reference lit
    factor, control granularity, preview lighting/exposure, pending consumer
    checks, and whether light spill was simulated in the preview.
18. **Export:** material bindings traced per tier, export options, and how to
    rebuild the asset from its scripts.
19. **Review status:** checks completed here, listed separately from those
    pending in the consumer.
20. **Tooling versions:** Blender and MCP addon versions used.

**Props — required, in order:** `Style brief`, `Category and secondary use`,
`Footprint`, `Construction`, `Per-tier triangle counts`, `LOD review`,
`Texture set`, `Variant list`, `Export`, `Review status`, `Tooling versions`;
add `Glazing treatment` when the prop has glass, `Night lighting` when it
emits, and `Interior geometry` (kept contact or closure faces) and `Known
simplifications` when there is something to record, each in its building
position. Other building-only sections are left out, not filled with "n/a".
`Footprint` gives width x depth x height against the 1.8 m standing figure;
`Construction` gives the pivot's attachment point and whether the asset has
an authored front. Inside a required section, an inapplicable field is
marked "n/a" rather than dropped.

**Vehicles — required, in order:** `Style brief`, `Body class` (the class
and its box), `Dimensions` (target and built length, width with and without
mirrors, height, wheelbase, track, overhangs and ground clearance, against
the 1.8 m figure, and the doors under `### Doors`), `Construction` (pieces, how lamp and glass faces are cut,
the front and the pivot), `Wheels` (parts, radius, width, sides per tier,
twin, arch clearance), `Ids` (each tier's ids and the encoding measured),
`Lamps` (lenses per group, colours, what each tier keeps), `Glass` (groups,
areas, measured colour and roughness, cabin level, the `LOD2` merge), `Paint`
(panels, grey level, plates), `Per-tier triangle counts`, `LOD review`,
`Interior geometry`, `Known simplifications`, `Texture set`, `Variant list`,
`Export`, `Review status`, `Tooling versions`. Vehicles have their own list:
a building or prop heading is a schema error in a vehicle's notes, and the
other way round.

**Notes describe the asset as it stands now.** A revision edits the section
that owns the change; it never appends a second, dated section that says
something different. Where the history is worth keeping, add one optional
`## Revision log` as the final section: dated entries, newest first, each
naming what changed.

**Asset-specific material is a `###` subsection under the section that owns
it**, never a new `##` (e.g. a distinctive roof form under `Construction`, a
curve anti-aliasing method under `Texture set`).

**`CATALOG.md`:** one line per asset with category/name, short description,
variant count, per-tier triangle counts, and an embedded `preview.png`
thumbnail, so the index is browsable without opening asset folders.

## Output Contract — Buildings

- **Format:** `.glb` plus external PNGs. Albedo, ORM and normal map required
  (Texture Requirements).
- **Night lighting: every building with glazing is night-lit by default** and
  ships `_emission.png`. A building without it needs a brief-driven reason in
  `notes.md` (e.g. a windowless shed, a derelict brief).
  - The mask marks candidate glazing, glazed doors included; frames, walls and
    roofs stay black. One mask serves every tier and colour unless the glazing
    itself changes.
  - **Each pane is the lit room behind it,** painted neutral grey by
    `scripts/glazing.py`'s `night_rooms()`: its own level, a soft lamp glow and
    a falloff toward the floor, every pane lit at no less than about a fifth.
    A flat full-white pane reads as a light panel, too bright and too pale.
    No curtains or blinds (they read as dark bars, not fabric) and no colour,
    which is the consumer's.
  - Other luminous regions (signs, lamps) only when the brief calls for them,
    with their mask regions and control scope in `notes.md`. They are
    written in their own colours (a sign's face, an obstruction lamp's red),
    which is how the validator tells them from glazing, and share the mask's
    one control. A building without glazing may be night-lit by them alone.
  - Export an intact `emissiveTexture` binding with the emission factor zero by
    default; keep the texture even at zero (`scripts/window_emission.py`).
  - The consumer controls per-building intensity, colour and occupancy
    schedule. Never bake schedules or random on/off occupancy into albedo or the
    mask. Shared window UVs generally prevent per-window control; document it.
  - Glow is an emissive surface only. Light spill onto nearby ground and walls
    depends on consumer lighting.
- **Coordinates:** Blender `Z`-up, front toward `-Y`; export right-handed
  `+Y`-up / `+X`-right. Verify orientation on reimport.
- **Pivot:** ground level, at the centre of `LOD0`'s plan bounds (eaves,
  steps and ladders included; not the sidecar's wall footprint), one
  origin shared by all tiers. Never recentre a simplified tier on its own
  bounds.
- **Assets that meet** (a gallery and the hall it enters) meet on a
  shared plan-bounds plane and never overlap: the whole plan bounds may
  be taken as solid, so an overhanging part enlarges the obstacle too.
- **Tiers:** all four, `LOD0` through `LOD3`.
- **Materials:** one render slot; at most two, only for a real UV/shading
  constraint (roof and walls counted together). Every tier uses its variant's
  one material/texture set; no per-tier textures.
- **Textures:** 1024 square; 2048 only for a documented hero/landmark exception.
  Target 64 texels/metre and record intentional local deviations.
- **Facts sidecar:** every building ships `export/<asset_name>.model.json`,
  version 4, written by `asset_build`'s `write_facts()` from the `build.py`'s
  `facts()` (`scripts/model_facts.py` holds the schema; vehicles write
  version 3, Vehicles).
  - It is in the frame of the exported `.glb` files: metres, `+Y` up, `+Z`
    front, origin at the pivot.
  - It states the `LOD0` bounds, the outer wall outline at ground level
    (without eaves, steps, fences and ladders), the occupied storeys with
    their floor areas (under a roof, only where the underside is 1.6 m or
    more over the floor), the dwellings, every door in an outer wall (its
    kind: entrance, service, vehicle, balcony or store; threshold centre on
    the outer wall plane, outward facing, the leaf's clear size, the
    walking surface's height at the threshold, `floor_y_m`, and the index
    of the storey it opens to, `storey`, or `null` for none; and, where
    there are doors, the one `main` door, an entrance the `build.py` tags),
    the hero status, and the name, triangle count and SHA-256 of every
    exported file, with the commit and Blender version it was written from.
    A structure without doors or occupied floors (a chimney) states none.
  - A door's `floor_y_m` is `LOD0`'s, measured by the build just behind
    the wall plane where the leaf stands: 0.02 on a floor slab, 0.0 at
    bare grade, the top of the step, landing, deck, sill or dock a raised
    door stands on, and a sill's own height where nothing is under it. Its
    `storey` is the listed storey whose floor is nearest, within 0.5 m;
    `wall_door(..., floor=, storey=)` states either where the measure
    cannot decide.
  - Optionally, every drivable lane through or under the building: one
    mouth's centre on the wall plane (under an overhanging part, on the edge
    of the plan bounds), the horizontal direction into the building, width,
    length, clear height, and whether it is open at the far end.
  - Geometry and files only: no zones, lots, capacities, anchors or other
    consumer terms.
  - A full rebuild rewrites it. `blender --background --python build.py --
    facts` rewrites it alone, after checking the build against the files in
    `export/`; run it from a committed tree, so `source.dirty` is false.
- No pack manifests or approval state. The Validation Checklist is the
  review gate.

### LOD Budgets and Review Assumptions

| Tier | Suggested camera distance | Ceiling | Hero/landmark ceiling |
| --- | --- | --- | --- |
| `LOD0` | under ~35 m | 12,000 | 20,000 |
| `LOD1` | ~35–70 m | 4,000 | 6,000 |
| `LOD2` | ~70–120 m | 1,500 | 2,500 |
| `LOD3` | beyond ~120 m | 500 | 700 |

- **Ceilings are binding; there is no floor.** A building's count follows from
  its massing, and geometry is never padded. For scale, `CATALOG.md` lists
  every asset's counts: sheds, shops and small industrial blocks sit at
  300–1,000 triangles at `LOD0`, detached houses about 2,600, two-storey
  terraces 5,600–6,600, the civic hall about 5,200. Mid-rise and larger
  buildings are expected to approach the ceilings. There is no fixed
  reduction ratio between tiers.
- **Review camera:** perspective, 1920x1080, **50° vertical FOV**, distance
  measured along the view direction to the assessed feature, plus oblique and
  elevated views. These are review assumptions, not game-camera claims; record
  any change and render scale in `notes.md`.
- **Projected size:** a small transverse extent `s` at view depth `d` spans
  about `p = H * s / (2 * d * tan(vfov / 2))` pixels (`H` = render height).
  With the review camera: 1 m ≈ 58 px at 20 m; 0.28 m ≈ 4.6 px at 70 m.
  Reveal depth is not transverse extent; the viewing angle matters.
- **Distances are starting points.** An asset's size or a visible transition
  may justify a recorded override. Test both sides of each switch; if a feature
  visibly flattens or vanishes, keep it within budget or move the switch.
  A consumer may switch by screen size instead, so a small asset's last
  tier is seen near: review it at its switch's screen size too.
- **The consumer switches by screen size, so a small asset changes tier
  much nearer than the table.** Measured in the consumer at 1080p and a
  75° vertical FOV (two assets, November 2026; a measurement, not a
  guarantee): the 6.75 m kiosk showed `LOD1` from about 12 m, `LOD2` from
  25 m and `LOD3` from 52 m; the 10.4 m salon from about 20, 45 and 85 m.
  As a rule of thumb the switches fall at about 1.8, 4 and 8 times the
  asset's largest bounds dimension.
  - Review every adjacent pair at those distances too, rendered at 75°
    and 1920x1080, face-on, oblique and from eye level, whenever they are
    nearer than the table's.
  - What a tier drops must not pop there. Counters, bins, benches, racks,
    canopies' fittings and other parts seen against the wall stay,
    simplified, until the tier whose switch hides their loss; record the
    distances used in `notes.md`.
- **20–150 m is a near-view review range**, not a consumer camera limit. Review
  `LOD3` into its intended distant range; the consumer owns culling and farther
  representations.
- **Runtime acceptance needs representative consumer scenes.** Record the
  workload, visible counts per tier, hardware, resolution, FOV, shadows,
  timings and resource use. Triangle counts and file sizes prove neither frame
  time nor VRAM; label unmeasured assumptions as such.

### Geometry and Construction

**Spend geometry on visible shape and depth.** The default facade-relief
threshold is about **0.25 m**, or a material effect on the roofline or
silhouette. Geometry below the threshold is allowed when intended-distance
comparisons show a contribution textures cannot give; record the reason, the
triangle cost and the tiers that keep it.

- **Openings:** recessed windows and doors at `LOD0`/`LOD1`, with jambs, head,
  sill and a closing glass/door plane; reveals may be shallower than the relief
  threshold. Glazing bars and ornament are textured. Detached buildings are
  seen from every side, so a flat secondary-elevation opening needs an
  intended-view justification.
  - **An opening recessed at grade gets a floor.** A recess at grade has
    no sill, and the shell has no upward face under it, so the consumer's
    terrain shows inside: grass between the paving and the door. Every
    opening recessed at grade, whatever its depth, gets a concrete slab
    filling its plan, built with `scripts/door_floor.py`: a door of any
    kind (entrance, service, vehicle, store), a lobby or set-back doorway,
    glazing or a portal set back at grade. Top 0.02 m above grade (a face
    at grade fights the terrain), a nosing on the wall plane, nothing past
    it, on its own atlas region, on every tier that keeps the recess.
    Bounds, footprint and the door's threshold stay as they are. None is
    needed where the opening is painted flat on the tier, stands on a
    step, landing, sill or plinth (that is its floor), opens off a lobby
    or porch already floored, or is a balcony door; nor in an open bay or
    a drivable lane (the sidecar's passages), whose floor is the
    consumer's ground by design.
- **Count full opening topology:** four reveal sides alone are eight
  triangles, before the closure and surrounding wall. Measure triangulated
  exports, walls included. Polygons with holes avoid needless wall grids.
- **Flat openings by default at `LOD2`/`LOD3`,** keeping positions, proportions,
  colour and material response. Review the transition under several light
  directions.
- **Repeated shallow detail** (string courses, sills, lintels, pilasters,
  mullions, shutters, siding, flashing, gutters) is textured, since repeated
  geometry adds up.
- **Downpipes are modelled**, though under the relief threshold: a tiling band
  cannot place a pipe, and a painted one lacks the shadow and the corner edge
  it is seen by. Build them with `scripts/downpipes.py`, which owns the shape,
  the UVs, the placing rules and the default tiers.
  - Hang each from a painted gutter and sample that gutter's middle rows,
    which the atlas names `PIPE_STRIP`.
  - Stand the pipe off the wall on its clips, never buried in it: a pipe cut
    into the wall splits the wall's triangles along its whole length.
  - Keep pipes clear of corners and openings, and check that in
    `check_layout()` with `downpipes.problems()`.
  - A tier that cannot afford its pipes drops them and records the vanishing
    in `notes.md`.
  - A building without a gutter has no downpipes.
- **Roof safety equipment is modelled** wherever a roof steeper than 1:8
  carries something serviced from it: a chimney, a ventilation housing,
  roof plant. Finnish building rules require a fixed route there from the
  ground, and the kit is part of how a Finnish roof reads. Like a downpipe it
  is under the relief threshold and placement-specific, seen by its outline
  over the eave and its rungs' shadows on the sheet. Build it with
  `scripts/roof_safety.py`, which owns the shapes, the UVs, the placing
  rules and the default tiers.
  - **At the back of the building**, away from the entrance and the street,
    as such kits usually are. Where the gables take the entrances, the eave
    wall away from the catalog view, on its rear half.
  - A **wall ladder** from the ground up an eave wall, on brackets, clear of
    corners, openings and downpipes, passing outside the eave and rising
    about 1 m above the roof edge. Where no eave wall has such a run (a
    terrace's bays), a blank gable next to its rear corner, passing outside
    the rake.
    - A wall ladder taller than 8 m carries a safety cage from about
      2.5 m up, thinned by tier before it goes.
  - A **roof ladder** from the eave up the slope above the wall ladder, on
    brackets clear of the sheet, to the height of what it serves.
  - A **walkway**: a level plank along the slope, on posts, from the roof
    ladder's top to each serviced item it does not reach directly. One
    walkway may serve several.
  - Plain vent pipes are not serviced items. A flat deck, or a slope of 1:8
    or less, needs only the wall ladder up to it. Access from inside through
    a roof hatch replaces the kit only where the brief says so, recorded in
    `notes.md`.
  - The kit takes the gutter's colour, as a matched rainwater and roof
    safety system does: it samples the atlas's `PIPE_STRIP` like the
    downpipes. An atlas without a gutter names another strip in the roof's
    or the trim's metal.
  - Check its place in `check_layout()` with `roof_safety.problems()`. Tiers
    thin the rungs before the kit goes; a tier that drops it records the
    vanishing in `notes.md`. A wall ladder that sets the building's extents
    keeps its bare rails on every tier, so the bounds and pivot hold.
- **Handrails are modelled** on every entrance flight of three risers or
  more, whose landing is a fall of half a metre or so: one rail, on the
  right-hand side going up, level along the landing and following the
  nosings down the flight, its top 0.9 m above them, on posts. Where the
  right side is blocked it goes on the left, with the reason in
  `notes.md`. Like the roof kit it is under the relief threshold and
  placement-specific, seen by its outline against the wall and its shadow
  on the treads. Build it with `scripts/handrails.py`, which owns the
  shape, the default tiers and `problems()` for `check_layout()`.
  - It takes the gutter's colour (`PIPE_STRIP`), like the roof kit.
  - Where a flight comes down from a railed deck, the rail meets the
    railing's end at its height, so the two read as one.
  - Balusters are left out: a see-through infill would need alpha.
  - Tiers keep the rails through `LOD1` by default; the tier that drops them
    records it in `notes.md`. Lower flights (one or two risers) have none.
- **Quoins and corner boards:** dedicated atlas regions or economical corner
  geometry, only at actual corners. Their depth may collapse below `LOD1`, but
  the contrasting paint must survive every later tier through suitable UVs.
- **Massing features** (balconies, projecting windows, porticos, porches,
  dormers, cupolas, roof lanterns) are modelled economically and kept through
  `LOD2`. At `LOD3`, small projections may simplify or go only after appearance
  review. Distinctive tower crowns and prominent dormer rows keep their shape.
- **Overhangs:** eaves and rakes 0.3–0.6 m with soffit and fascia by default;
  note deviations. Roof-edge cornices follow the same review; mid-facade
  cornices use the relief test.
- **Parapets** that conceal a roof or define the profile stay on every tier,
  `LOD3` included. Coping and panelling are textured. Pierced screens are
  opaque; skylights are flush opaque regions unless raised massing. No opening
  may expose an unmodelled interior.
- **Rooftop clutter:** small HVAC and vents may be `LOD0`/`LOD1` geometry and
  drop when insignificant at the switch. Installations that define the profile
  are massing.
- **Chimneys are hollow.** Every chimney is open at the top: a rim round a flue
  sunk about 1 m, lined and floored with a dark soot patch, so the shell stays
  closed and no interior shows. Keep the floor clear of the roof below it. A
  solid capped block reads as a post from any raised view. Unlike openings,
  the flue stays recessed on every tier that keeps the chimney: painted flush,
  sunlit soot reads as dark grey, barely apart from the cap.
- **Trim allocation:** roughly a quarter of the tier's ceiling, counting every
  repetition. Beyond that, simplify or document the visible value.

**An exported closed shell is required; the construction method is open.**
Union plan outlines, exact booleans on closed solids (`asset_build`'s
`union()`/`difference()`), direct exterior meshing, and disjoint closed
solids in one mesh that touch nothing (kits of thin bars built
`lean=True`, a bench's slats) are all valid. A new build passes
`snap=asset_build.SNAP` to its booleans, so walls that meet at a non-round
coordinate merge instead of leaving a double wall inside.

- Remove buried partitions and duplicate internal surfaces; close the exterior
  and check topology.
- Derive facade rhythm from the final visible wall runs; no subdivisions or
  openings on buried walls.
- Resolve roof intersections into intended valleys and ridges; overlapping
  primitives are not enough.
- Align intended flush surfaces. Judge intentional setbacks by proportion and
  shading. Recheck roof joins and corners after massing changes.
- Before removing a visible feature to save triangles, consider coplanar
  cleanup that keeps UV and material seams; recheck topology, bounds, UV
  sampling and appearance afterwards.

### Appearance Across LODs

At intended distances every tier keeps the asset's identity: silhouette,
characteristic roofline, major recesses, window rhythm, high-contrast paint and
trim, overall materials. Minor silhouette changes are fine if inconspicuous at
the switch. A low triangle count never excuses a profile change or the sudden
loss of white corner boards, dark windows or another dominant colour.

- Compare adjacent tiers, and each tier against `LOD0`, around each switch with
  identical camera, framing, lighting and variant, including elevated/oblique
  views and contrasting light directions. Inspect up close to find defects;
  accept at the intended screen size.
- Keep necessary artwork in lower-tier UVs: flatten geometry into suitable
  shared-atlas regions. Recheck normal-map shading after topology or UV
  changes.
- Derive tiers from shared architectural parameters, from `LOD0`, or from the
  preceding tier, as suits; neither decimation nor independent generation
  guarantees continuity, so compare actual results. One origin for all.
- Blender comparisons are authoring evidence, not proof of runtime switching,
  filtering or performance; record what is pending in the consumer.

## Texture Requirements

- **Format:** lossless PNG, 8 bits per channel, square, power of two, no alpha.
  Buildings 1024 (hero/landmark 2048); props 256–512 (Props); vehicles 1024
  (Vehicles). The consumer owns GPU compression and shipping mipmaps;
  authoring owns padding and filtering review.
- **Painting:** rasterise atlases with `scripts/atlas.py`, supersampled
  `atlas.SS` = 4 samples per pixel per axis and box-filtered down in linear
  light, so edges at fractional positions, curves and lettering are
  anti-aliased. Paint in final-pixel coordinates; the canvas handles the
  samples. Record the factor in `notes.md` if an asset uses another.
- **Normal maps are derived from a painted height channel** (metres, relative
  to the face the region maps onto) by `atlas.normal_map()`. Height carries
  only relief the mesh does not model: siding laps, board and casing arrises,
  standing seams, gutters, brick faces, panel mouldings. Keep physical
  heights (a lap is ~15 mm, a casing ~20 mm) rather than exaggerating; glass
  stays flat. Bind at strength/scale 1 through a tangent-space Normal Map
  node. Tangents are not exported; the consumer generates MikkTSpace tangents
  as glTF specifies.
- **Colour space:** albedo and emission sRGB; ORM and normal non-colour/linear.
  Set it in Blender before export; a mistake corrupts lighting silently.
- **Map roles:** albedo is surface colour and wear, with no directional light,
  reflections, or fixed sky gradients across glass; a lit top edge or a sunny
  board face is relief and belongs in the height channel. Occlusion that holds
  whatever the sun does (under a lap, in a joint) may darken albedo lightly;
  `atlas.cavity()` derives it from height. Normal is shallow relief; ORM is R
  occlusion, G roughness, B metallic. AO darkens indirect light; it is not a
  sun shadow.
- **Weathering** goes through `scripts/weathering.py` at its moderate level:
  each atlas's `weather()` says where, the module says what it looks like, so
  a plinth or a sill weathers alike across the catalog. A stronger level read
  as neglect. Weather that follows height (ground splash, a sheltered eave,
  dirt toward a gutter) goes only on a band whose V is height from the ground.
  On a band sampled from each storey's foot, or one that wraps in V, it would
  repeat up the wall, so there it stays noise on the band's period
  (`tile_y`). A roof band whose V direction differs between slopes gets
  weather that reads the same either way up. Streaks under one window or one
  corner cannot live in a shared band. Glass and lit signs stay clean.
- **Bindings, on every exported tier and every variant substitution:**
  `pbrMetallicRoughness.baseColorTexture` → albedo,
  `pbrMetallicRoughness.metallicRoughnessTexture` → ORM,
  `occlusionTexture` → ORM. Check the actual image URIs, UV sets and
  multiplying factors; an ORM file that exists but is not bound does not count.
  When used, verify `normalTexture` and tangents, and `emissiveTexture` with
  its factor.
- **Normals:** OpenGL tangent space (`+Y`/green up), as glTF and Blender use;
  `atlas.normal_map()` writes it. Flip green from DirectX-convention bake
  tools.
- **Fully opaque:** no alpha or masked transparency, glass included. A future
  prop cutout (e.g. ornate metalwork) needs a per-asset decision.
- **Consistent texel density** across the catalog, 64 texels/metre for
  buildings and props (vehicles: their 1024 atlas, Vehicles): an asset
  visibly sharper or blurrier than its neighbours is wrong even if it looks
  fine alone.
- **Seamless tiling:** repeating regions (brick, siding) tile at their edges;
  non-tiling regions avoid visible UV-boundary seams.
- **Atlas padding and filtering:**
  - Call `atlas.pad()` last: it fills every texel no region claims from the
    nearest region's own edge, in every channel, so albedo, ORM, normal and
    emission are padded consistently and the gutters need no hand-tuning. The
    padding keeps a flat normal. Bleed each region's height at its own edge
    height, or the normal map and cavity read the region border as a step.
    Assert region and material ownership in generators and inspect on the mesh.
  - A half-texel inset protects only base-level bilinear sampling. One texel at
    mip `L` covers about `2^L` source texels per axis, so size gutters for the
    intended footprint.
  - Repeating regions need periodic padding along the repeat direction;
    insetting both ends of a full-width band breaks the tiling. A band that
    also repeats vertically carries its opposite end into its gutter before
    `pad()` runs, and its noise uses `atlas.noise(tile_y=...)`.
  - Coarse mips can merge regions despite gutters: repack or enlarge critical
    regions. Never assume the consumer repairs it.
  - Review mipmapped appearance at the switches and beyond, face-on and oblique
    (`scripts/review_atlas_mips.py`): roof/trim colour leaks, dark seams,
    roughness shifts. Full-resolution screenshots alone cannot pass this.
- **External textures only.** Every glTF `image` has a `uri` to a PNG beside it
  in `export/` and no `bufferView`. All tiers share one set of PNGs.
  - Blender's exporter with **Keep Original Textures** writes both a `uri` and
    a placeholder `bufferView`. glTF allows one source per image; Godot drops
    such images. `asset_build`'s `export_all()` runs `scripts/glb_images.py`'s
    `strip_embedded_images()` on every tier; never repair a file by hand.

## Color & Material Variants — Buildings

Buildings only; Props and Vehicles have their own rules. Variation follows
scale and material uniformity, not category folder.

- **Low-rise / small-scale** (houses, most service buildings, small industrial
  sheds): 3–6 albedo variants (paint, brick/siding, roof, metal-panel colours)
  on shared geometry, UVs and LOD chain.
- **Large-scale / monolithic** (towers, large commercial or industrial
  complexes): a restrained, coherent treatment per instance. Alternative
  uniform brick/concrete/glass/cladding on the shared mesh is fine; a
  multicoloured building is not. Architectural variety needs distinct geometry.
  A singular landmark may have one variant.
- Ambiguous cases: decide from the actual massing and record it in `notes.md`.
- Assets meant to stand together (a plant's buildings, the walls round
  them, a farmstead) share variant names and palettes, so one name
  dresses the set.
- Variants change textures only (albedo, and ORM/emission if the pattern
  changes); geometry and UVs stay identical. Every tier uses its own variant's
  textures.
- Name files `<asset_name>_albedo_<variant>.png`, even for a single variant
  (e.g. `brick_clocktower_hall_albedo_red_brick.png`). ORM and normal stay
  unsuffixed and shared; add `_orm_<variant>`/`_normal_<variant>` only when a
  variant changes the surface pattern, never for colour alone. Record each
  variant's meaning (e.g. "red brick", "cream stucco") in `notes.md`.
- Size limits apply per texture. Record the number and size of all unique
  textures; co-resident variants cost memory, so share unchanged maps.

## Props

Props share format, colour spaces, licensing, reference policy, Texture
Requirements, `Z`-up authoring with `+Y`-up export, and the
`build.py`/`preview.png`/`notes.md` workflow with buildings. Pivot,
orientation, budgets and variants differ:

- **Categories:** `street_furniture/` (benches, bins, bollards, mailboxes,
  planters), `lighting/` (lamp posts) and `boundary/` (wall runs, piers,
  gates). Add more only when work starts.
- **Pivot:** on the ground at the centre of the ground-contact footprint
  (a bench's feet, a lamp's base plate), or a mounted prop's attachment
  point; not the plan bounds' centre. Record it in `notes.md`. Every tier
  keeps `LOD0`'s pivot and plan bounds, the consumer's obstacle.
- **Orientation:** front toward Blender `-Y` only for a genuinely asymmetric
  front (e.g. a backed bench). No invented front for bollards, bins or planters.
- **Budgets** (provisional):
  - Small (bench, bin, bollard, mailbox, planter): `LOD0` 50–300 triangles,
    `LOD1` 12–80, texture 256.
  - Medium (lamp post): `LOD0` 200–800, `LOD1` 40–200, texture 256–512.
  - `LOD0`/`LOD1` required, `LOD2` optional with no numeric band yet: record
    its cost and show a useful reduction that keeps identity.
  - Explain below-floor tiers; never pad.
  - Material slots: one, at most two.
  - Record intended switch/cull distances from projected size in
    representative views. Props usually need shorter ranges than buildings; the
    consumer implements culling.
- **A family shares one atlas:** related props paint it once and write it
  into each asset's `export/` under that asset's name (the boundary
  pieces), so every asset ships self-contained; the sidecar hashes let a
  consumer merge identical files.
- **Variants:** 1–2 named finishes by default (a single albedo is still a
  named variant); boundary pieces up to three. Municipal furniture is
  usually city-uniform. Record the reasoning in `notes.md`.
- **Glass on a prop** (e.g. a lamp cover) follows the building glass rules.
- **Boundary pieces** fence a lot as a building's neighbours, seen as far:
  - All four tiers, `LOD0`–`LOD3`. Provisional ceilings, no floors: `LOD0`
    200, `LOD1` 120, `LOD2` 80, `LOD3` 48. Texture 512. Every tier keeps
    the piers: a consumer switching by screen size shows `LOD3` near.
  - Long axis along `X`, the outer (street) face toward the front, the
    pivot on the ground on the wall's centre line, midway between the
    piece's two joint planes (a gate piece: on the opening's edge plane).
    Every tier keeps `LOD0`'s plan bounds: the consumer's obstacle.
  - Joint rule: a run brings the pier centred on its `-X` joint plane and
    none at `+X`, where its wall stops inside whatever closes it (the next
    run's pier, a pier piece, a gate pier); so a closed lot gets one pier
    per joint and corner. The run beyond a gate is pierless.
  - Up to three brick variants, matching the buildings they enclose.
  - They ship the buildings' facts sidecar, version 4, with no doors,
    storeys or dwellings; the
    footprint is the plan outline at ground level.

## Vehicles

Vehicles share format, colour spaces, licensing, reference policy, Texture
Requirements, `Z`-up authoring with `+Y`-up export, and the
`build.py`/`preview.png`/`notes.md` workflow with buildings and props. The
consumer turns the wheels, lights the lamps and paints the body itself, per
vehicle, from ids stored in the mesh, so everything else differs. Lamp and
glass groups the consumer does not use yet are still required, so no model is
reworked later.

### Scope, direction and layout

- **Road vehicles as closed exterior shells.** No rig and no animation: the
  wheels are parts of the one mesh, and the consumer spins and steers them.
  One mesh and one material per tier; no separate wheel files.
  - No interior and no seats in the body mesh, on any tier; glass stays
    opaque.
  - Reserved, not built yet: an optional `export/<asset_name>_interior.glb`
    in the body's frame and origin, one mesh and one material, about 400
    triangles (seat shapes, dashboard, steering wheel, optionally a driver's
    silhouette). The sidecar's `interior` is `null` until it exists; adding
    it later changes no body mesh.
  - Not yet: trailers, emergency and service vehicles; each gets its rules
    when work starts.
- **Direction (the owner's):** cars follow European and Japanese models,
  trucks European only, of 2005–2020: modern everyday vehicles. Generic
  composites with no recognisable make: no badge, signature grille, lamp
  graphic or real livery. Gather references before design in
  `reference/vehicles/` (Reference Image Policy).
- **Layout:** `vehicles/<class>/<asset_name>/`, class `car`, `van`, `truck`
  or `bus` (Repository Structure): the props' files with all four tiers,
  `_emission.png` required, `_normal.png` optional, the facts sidecar, and
  `glass_texels.png` beside `notes.md` (Glass).
- **A builder writes** each tier's parts as `vehicle_build.Piece`s (`body`,
  `mirror`, and `wheel` with its part, centre and steer flag), a texture
  generator that also writes `glass_texels.png`, `check_layout()` and
  `facts()`; everything else is `vehicle_build.VehicleAsset`'s.
- **Frame:** Blender `Z` up, front toward `-Y`; exported `+Y` up, nose toward
  `+Z`. `+X` is the driver's left in both frames, so a left lamp has `x > 0`
  and sits on the viewer's right in a front view. "Left" and "right" always
  mean the driver's.
  - Origin on the ground at the centre of the body's plan box (length x
    width, mirrors excluded), one origin for every tier.
  - Tyres touch the ground exactly and nothing is below it, on every tier.
  - Symmetric about `x = 0`: wheel and lens pairs mirror within 1 mm. Only
    a rear fog lamp, a single reverse lamp, a plate lamp, a beacon or a
    sign may stand alone off the centre line.

### Class boxes

Hard limits: the consumer parks and queues every vehicle of a class as its
box.

| Class | Length x width x height (m) | Mirrors, a side | Atlas |
| --- | --- | --- | --- |
| `car` | 4.50 x 1.80 x 1.95 | 0.12 | 1024 |
| `van` | 6.00 x 2.10 x 2.70 | 0.25 | 1024 |
| `truck` | 8.00 x 2.55 x 3.80 | 0.25 | 1024 |
| `bus` | 12.00 x 2.55 x 3.20 | 0.25 | 1024 |

- Width is without mirrors, and nothing but the mirrors reaches past it: the
  validator takes vertices outside it, above the lowest wheel centre and in
  the front half, for mirrors.
- The box holds for every tier as exported, wheels straight ahead; a steered
  wheel may leave it.
- Sizes are targets within ±0.05 m. A target that equals a class limit has
  −0.05 to 0, so it is built slightly under. Record targets and built sizes
  in `notes.md`.

### Wheels

- In `source.blend` each wheel is its own object with its origin at the
  wheel centre (the `<asset_name>_parts` collection); the tier that exports
  is the join of the tier's pieces.
- A closed solid (tyre, rim face, inner face) with a corner at the very
  bottom, so it rests on the ground exactly and a turned wheel shows no hole
  (`vehicle_build.wheel_solid()`). A twin rear pair is one part a side. At
  most 8 parts, numbered in sidecar order: front axle first, left before
  right (1 front left, 2 front right, 3 rear left, 4 rear right).
- `LOD0` 16–20 sides, `LOD1` 8–10; from `LOD2` the wheels are body (part 0).
- The arch is a dark recess. Each wheel straight ahead, and each front wheel
  turned 35° either way about the vertical through its centre, keeps 10 mm
  from every body triangle.
- Signs, in the exported frame: a positive steer angle turns the wheel's
  nose toward `+X`, the driver's left (a rotation about `+Y` through the
  wheel centre); a positive spin rolls it forward (about `+X`, the top of
  the tyre moving toward `+Z`).
- No brake discs, suspension or tread geometry.

### Ids

Every tier has one colour attribute, `COLOR_0`, normalised `UNSIGNED_BYTE`
`VEC4`, id n stored as the byte n:

| Channel | Meaning | Values |
| --- | --- | --- |
| R | part | 0 body; 1..8 the wheel parts |
| G | surface | 0 plain; 1..15 a lamp; 32..47 glass |
| B | paint | 255 on painted body panels, 0 elsewhere |
| A | unused | 255 |

- One R, one G and one B per triangle: ids never blend, and paint never
  fades across a panel edge. A lamp or glass face is unpainted body
  (R 0, B 0).
- Set each face's surface and paint as it is made
  (`vehicle_build.Builder.face(..., surface=, paint=)`) and each wheel's part
  on its piece. `VehicleAsset` writes them as the `FLOAT_COLOR` corner
  attribute `metrum_ids`, never `BYTE_COLOR` (sRGB bends it), on every piece
  before the join (a piece without it joins in as A = 0), and refuses a tier
  with A != 1 or two ids in one polygon.
- The export writes `metrum_ids` as `COLOR_0` and no other colour, Draco and
  meshopt off, then rewrites it as exact bytes
  (`vehicle_ids.convert_color0_to_ubyte()`, which refuses a value more than
  1e-3 off a byte). The consumer truncates any other form, so the byte form
  is required. No other custom attribute ships.
- Standard glTF viewers multiply `COLOR_0` into base colour and show these
  files dark, and Blender's importer reads it as sRGB bytes. Nothing here
  reads it that way: previews use the plain material, `review_asset.py`
  cuts `COLOR_0` out of the imported materials (so its mip renders work on
  vehicles), and the review sheet and the validator read the accessors
  (`scripts/vehicle_ids.py`).

### Lamps

Ordinary faces of the mesh with a lamp id in G, unlit in the albedo and lit
in their own colour in the emission. No glow, halo or beam geometry.

| Id | Group | Colour | Where |
| --- | --- | --- | --- |
| 1 | `tail` | red | rear, both sides |
| 2 | `brake` | red | rear, both sides; a car's high-mounted lamp |
| 3 | `tail_brake` | red | a rear lens that is both |
| 4 | `indicator_left` | amber | front, rear and side repeater, left |
| 5 | `indicator_right` | amber | the same, right |
| 6 | `reverse` | white | rear |
| 7 | `low_beam` | white | front, both sides |
| 8 | `high_beam` | white | front, both sides |
| 9 | `daytime` | white | front, both sides |
| 10 | `fog_front` | white | optional |
| 11 | `fog_rear` | red | optional |
| 12 | `plate` | white | rear plate lamp, optional |
| 13 | `beacon` | not defined yet; white, amber or red accepted | roof; reserved |
| 14 | `sign` | not defined yet; white, amber or red accepted | taxi sign, bus destination board; reserved |
| 15 | `marker` | amber, white, red | truck and bus outline lamps |

- Every vehicle has 3 (or 1 and 2), 4, 5, 6, 7, 8 and 9; a car also a
  high-mounted 2 on the centre line, a truck 15.
- Low beam, high beam and daytime are separate faces even inside one
  headlamp.
- A lens is a connected group of same-id faces; the sidecar lists each one,
  measured from `LOD0`.
- `LOD0` and `LOD1` carry every lamp face; `LOD2` keeps the ids on flat faces
  inside the same lens rectangles; `LOD3` has none.

### Glass

Opaque, dark and glossy, in the Style Direction glass band. It is painted
neutral dark, each pane a little darker at its foot and lighter at its head,
not with `glazing.rooms()`: a room's lit wall reads as a stain on a
windscreen. The seals round it are black rubber, so vehicle glass need not
be darker than its casing. Every pane is its own tagged faces, so tint, lit
cabins and see-through glass can come later without touching a model.

| Id | Group | Covers |
| --- | --- | --- |
| 32 | `glass_windscreen` | the windscreen |
| 33 | `glass_front_side` | front door windows; a cab's side windows |
| 34 | `glass_rear_side` | rear door and quarter windows |
| 35 | `glass_rear` | rear window or tailgate glass; a van's glazed rear doors |
| 36 | `glass_roof` | a glass roof or sunroof (optional) |
| 37 | `glass_cab_rear` | a truck or pickup cab's rear window |
| 38 | `glass_saloon` | a bus's passenger windows; a van's load-area windows |
| 39 | `glass_door` | a bus's glazed doors |
| 40–47 | reserved | |

- Separate faces, paint 0. Mirror glass, lenses and plates are not glass. A
  car has at least 32–35, a van and a truck 32 and 33, a bus 32.
- `LOD0` and `LOD1` carry every glass id. On `LOD2` a wholly glass face keeps
  its id, and the side glass may merge into one band a side, tagged 33.
  `LOD3` has none; its glass is in the texture.
- In the emission, glass texels hold a dim, neutral lit cabin:
  `glazing.night_rooms()` at about a quarter, no colour. The consumer keeps
  it dark until lit cabins are built.
- The texture generator writes `glass_texels.png` beside `notes.md` with
  `vehicle_ids.save_glass_texels()`: atlas size, 8-bit grey, 255 where glass
  covers half a texel or more, rows as the atlas PNGs. It is the validator's
  record of which texels are glass, and does not ship.

### Paint, textures and variants

- **Paint:** painted panels (B = 1) are neutral light grey in the albedo,
  about 0.75 linear, with panel gaps and light wear only; the consumer
  multiplies them by the vehicle's paint colour, so no body colour is baked.
  Plates are blank white rectangles, unpainted.
  - The level is the panel field of `LOD0` and `LOD1`: the area-weighted
    median of the painted texels, 0.70–0.80 linear, so every vehicle takes
    a paint alike. Seams and trim lines do not move it; never brighten the
    base or unpaint trim to reach it.
  - Every tier's area-weighted painted mean is within 10 % of `LOD0`'s, so
    a vehicle keeps its brightness at a tier switch. Far tiers give their
    painted faces flat light texels and their glass, wheels and underbody
    unpainted dark faces, each in its own block of the atlas.
- **Textures:** albedo per variant, ORM and emission required, a normal map
  optional; external PNGs, one set for every tier, one material slot. A
  1024 atlas for every class, exactly: about 64 texels/metre on a truck,
  about 128 on a car, with lamps and wheel faces denser still. Mirrored
  left/right UVs are fine
  except under lettering. The emission holds the lit lenses, the lit cabin on
  glass and black everywhere else, bound with factor zero.
- **Variants:** `plain` (paint true) on every vehicle. A livery is another
  albedo on the same geometry; one that paints its panels in full colour is
  marked paint false, and the consumer then paints it white. A livery names
  no real company and copies no real mark.

### Tiers

Ceilings, no floors; every tier shares the origin, plan box and textures.
The distances assume a 4.5 m car on a 1080p screen at a 75° vertical FOV:
about 105 px long at 30 m, 32 at 100 m, 8 at 400 m.

| Tier | Seen at | Car | Van | Truck, bus | Must keep |
| --- | --- | --- | --- | --- | --- |
| `LOD0` | under 30 m | 3,000 | 3,500 | 4,500 | wheel parts (16–20 sides), every lamp and glass face, mirrors, arches |
| `LOD1` | 30–100 m | 900 | 1,000 | 1,400 | wheel parts (8–10 sides), every lamp and glass face |
| `LOD2` | 100–400 m | 220 | 260 | 350 | silhouette; wheels as body; lamp ids on flat faces; glass ids on wholly glass faces; paint |
| `LOD3` | beyond 400 m | 40 | 40 | 60 | a box with the roofline; paint only (R 0, G 0) |

### Facts sidecar

`export/<asset_name>.model.json`, version 3 with `"kind": "vehicle"`
(`scripts/model_facts.py`); buildings and boundary props write version 4,
the next number in the one sequence. The
exported frame, geometry and files only. Version 3 is version 2 with the
`doors` list added.

- The `build.py`'s `facts()` states `cargo` (`model_facts.cargo_box()`;
  `None` for a car) and `doors` (`model_facts.side_doors()` and
  `rear_door()`, from the shut lines its atlas draws), and may override `lamps`, `glass`, `coupling` or
  `interior`. `VehicleAsset.write_facts()` measures the rest from `LOD0` and
  reads counts, bounds, id flags and hashes from the exported files.
- In order: `schema`, `version`, `kind`, `name`, `path`, `source`,
  `license`; `bounds` (`LOD0`, mirrors included); `body` (class, length,
  width without and with mirrors, height, wheelbase from the first to the
  last axle, front and rear overhang, ground clearance: the lowest body
  point); `axles`, front first (z, track, steer, twin); `wheels`, one per
  part in part order (id such as `front_left`, part, axle, side, centre,
  radius, width, steer; centre.y equals the radius); `attributes`
  (`{"set": "COLOR_0", "r": "part", "g": "surface", "b": "paint",
  "version": 1}`); `lamps`, one per lens (group, lamp id, side
  left/right/centre, position front/rear/side/roof from the facing's
  dominant axis, colour white/amber/red when lit (the group's own; a
  marker's is read from its emission texels or stated with
  `lamp_lens(colour=)`), centre, unit outward facing, width along up x facing,
  height across it); `glass`, one per group present (group, id, area in
  m²); `cargo` (a van's or truck's load box: min, max, door), `null` for a
  car; `doors`, one per door, front row first, left before right, the
  rear's last (side left/right/rear, row front/rear/cargo, centre, width
  of the opening along the body); `coupling`, `null` (reserved for
  trailers); `interior`, `null` or the
  file, its triangles and hash; `lods`, all four (file, triangles, hash, and
  whether the tier has wheel parts, lamp ids, glass ids); `textures` (orm,
  emission, normal or `null`); `variants` (name, albedo file and hash,
  paint); `default_variant`; `preview` (`preview.png` in the asset folder).
- The lists and `LOD0` agree both ways, every lens has a face, and its
  colour matches the emission texels its faces sample. No seats,
  weights, palettes or other consumer terms.
- **Doors** are where a person reaches the vehicle, as painted shut lines,
  not geometry. "Left" and "right" are the driver's; the drive side is the
  consumer's setting and is not stated.
  - `centre` is the middle of the opening on the body's skin, at ground
    level (y = 0), with no standing offset: a side door on the plan box's
    side or up to 0.15 m inside it (a cab narrower than its load box),
    never outside; a rear door on the centre line, on the plan box's rear.
  - `row` is `front` or `rear` for side doors and `cargo` for a load door
    or tailgate, on the rear or a side. A rear door is always `cargo`.
  - A car, van or truck has both front doors, a bus at least one door. The
    front row mirrors within 1 mm; the other rows mirror where both sides
    have a door (a van may have one sliding door).
  - A van or truck has a cargo door where `cargo.door` says, no wider than
    the load box.
- A full rebuild rewrites it; `build.py -- facts` rewrites it alone, from a
  committed tree.

### Previews and the review sheet

- `preview.png` is the catalog setup with the painted panels multiplied by
  the asset's `preview_paint`, or white (the albedo as shipped); a
  paint-false livery is always shown white, as the consumer paints it.
  `variants.png` has every variant by day and at night with the driving
  lamps lit (tail, tail and brake, low beam, daytime, markers).
- The review sheet is one command, `scripts/review_vehicle.py`, into
  `review/` and never committed: side, front, rear, top and three-quarter
  views; the front wheels turned ±35°; each lamp group lit in turn, and tail,
  low beam and brake together at night; the cabin lit; a false-colour view of
  the ids; white, dark grey and red paint through B; the four tiers side by
  side at 30, 100 and 400 m; a 1.8 m figure and the class's bay outline (car
  2.5 x 5.0 m, van and truck 3.0 x 8.0 m, bus 3.0 x 13.0 m). It stands in for
  the six pre-export views; the far side is the mirror check's.

## Determinism & Reproducibility

Bit-identical rebuilds are unnecessary; the goal is being able to reproduce and
iterate later.

- `notes.md` is the primary record.
- Every asset keeps a cleaned-up `build.py` beside `source.blend`: it
  writes the tiers, previews and facts sidecar. It cannot capture every
  screenshot-driven decision, so it replaces neither.
- **A rebuild is two steps.** The texture generator bakes the PNGs
  (the asset's generator, e.g. `python3 facade_atlas.py export`, or a
  family's script in `scripts/`; system Python with scipy and Pillow);
  the Blender build only reads them. A texture or palette change that skips
  the first step rebuilds the old textures without complaint.
- **Record Blender and addon versions as known-good diagnostics, not pins.**
  The glTF exporter keywords are the likeliest thing to break on upgrade;
  `asset_build.check_toolchain()` asserts the version floor and that each
  exporter flag `export_all()` passes still exists. Changed defaults fail
  silently, so record export settings in `notes.md`, not only in the call.
- **Saving a `source.blend` in a newer Blender raises the floor for that file.**
  `.glb` and PNG exports stay portable; `.blend` files do not. When it happens,
  raise the floor in Tech Stack and `asset_build.BLENDER_MIN` together, so
  the stated floor stays true.

## Reference Image Policy

Photos, screenshots and concept art are private guidance for proportions,
rooflines and window rhythm, never redistributed.

- **Never commit reference images, in any commit.** Keep them in the
  git-ignored `reference/` folder, and nothing else there.
- No reference-derived textures or tracing; textures are original or generated.
- Build generic or composite assets inspired by a style or region, never a
  recognisable real building, landmark or distinctively designed object.
- Prefer your own photos, clearly licensed stock, or AI-generated concepts, and
  settle sourcing before building.
- Keep references out of `notes.md`, prose included. Describe the asset on its
  own terms.

## Licensing

Two licences; the file format decides, not the location:

- **Content** (`.blend`, `.glb`, textures, rendered images, `notes.md`):
  **CC-BY-4.0**, with the full notice in `LICENSE.md`. No licence headers in
  art files.
- **Code:** every `.py` file, in `scripts/` or an asset folder, is
  **GPL-3.0-or-later** and begins with
  `# SPDX-License-Identifier: GPL-3.0-or-later`, then a blank line, then any
  docstring. No author names or boilerplate.

## Blender MCP Workflow

- Bind the MCP addon to `localhost` only.
- Keep `source.blend` textures external/linked, never packed.
- Gather references before designing, in `reference/` (Reference Image
  Policy); proportions and details come from them, and each review pass
  critiques the build against them and the brief. Never export a first
  pass.
- **Design from real examples, not from the catalog.** Research real Nordic
  buildings of the type and era, Finnish first, and take the form from
  them. Shared scripts and the set's material conventions are reused; an
  existing asset's massing and look are not, so a new asset is never a
  shrunken or restyled sibling of another.
- **Six pre-export views:** orthographic front, rear, both sides and top-down,
  plus a raised three-quarter aerial (~45° above the horizon, off the front
  corner, aimed at the building centre). The top view shows the whole roof;
  the aerial shows the roof and two elevations together, which exposes bad
  joins.
- **Working renders go in the git-ignored `review/` folder** at the repository
  root, one dated subfolder per pass, and per builder when several work at
  once (e.g. `review/review_YYYY_MM_DD/`). This covers the six views, LOD and
  distance comparisons, mip stress renders and galleries. Keep them out of
  asset folders and out of `reference/`. The only render deliverables are
  `preview.png` and `variants.png`.
- **Exterior views cannot rule out internal geometry.** Run the validator and
  inspect suspect surfaces by isolation, sections or topology.
- After `LOD0` passes, author the remaining tiers (Appearance Across LODs) and
  compare them at intended screen sizes.
- **Before changing a finished asset,** copy its folder into `review/` and
  render a before set with `review_asset.py`; render the same set afterwards
  and compare with `review_compare.py`.
- Finish every tier under the first variant before making further variant
  textures. Never regenerate geometry per variant.
- Before a destructive `bpy` operation (deleting objects outside the current
  asset, overwriting another asset's `.blend`, bulk scene changes), state the
  action and the reason plainly; treat it as irreversible.
- **`preview.png`:** fixed catalog camera orientation and lens, lighting and
  colour management, distance fitted to the bounds. Use a neutral world/sun
  (or an authoring-only studio HDRI), the same for every asset, and record it.
  A small prop's fitted preview is nearer than any use distance; judge its
  texture sharpness in review renders, not the preview.
- **`variants.png`** (night-lit buildings, single-variant ones included): every
  colour at `LOD0`, a labelled day row (emission off) above a matching night
  row (reference emission on), with camera, framing, exposure and colour
  management fixed between rows (`scripts/variant_previews.py`). Record the
  lighting and emission settings. Also check off/on behaviour on reimported
  tiers, including oblique/distant filtering and LOD switches; a `LOD0` sheet
  cannot show those. An unlit asset with more than one variant ships a
  day-only `variants.png` instead: one labelled row of every colour.
  `build.py -- variants` renders the sheet alone, after checking the build
  against `export/`.

## Validation Checklist Before Marking an Asset Done

### Mechanical Checks and Their Limits

Run `scripts/validate_asset.py` with the correct class and hero status, from the
repository root:

```bash
blender --background --python scripts/validate_asset.py -- buildings/residential/rintamamiestalo_porch
blender --background --python scripts/validate_asset.py -- buildings/service/brick_clocktower_hall building hero
blender --background --python scripts/validate_asset.py -- props/street_furniture/your_asset prop_small
blender --background --python scripts/validate_asset.py -- props/lighting/your_asset prop_medium
blender --background --python scripts/validate_asset.py -- props/boundary/tiilimuuri_run_10m prop_boundary
blender --background --python scripts/validate_asset.py -- vehicles/car/your_asset vehicle_car
```

It checks required exports, GLB structure, image references, material count and
transparency, triangle counts against the budgets, welded topology, pivot and
bounds, PNG size and format, `notes.md` section order, the facts sidecar
(schema, hashes, tier counts and bounds, door kinds, one `main` entrance
where there are doors, doors on the footprint, each door's `floor_y_m` and
`storey` well formed, passages within the bounds),
every prop tier's plan bounds against `LOD0`'s, and a sampled
hidden-surface test. On a building it probes every sidecar door on every
tier: the reveal's depth from rays across the leaf, and, where it is
recessed at grade, rays down across its plan between the jambs, which must
meet the slab's top at 0.02 m (a step, landing or sill higher passes; an
upward face at grade or the open rim fails). A flat door, one onto a
passage and one with no closing face within 3 m need none. Openings that
are not doors (set-back glazing, a portal) are not in the sidecar and stay
`MANUAL`. On `LOD0` the build's own threshold probe must find each door's
`floor_y_m` within 1 mm where a face lies under the threshold (a value
over no face is a `WARN`, an override to confirm); a door more than
0.25 m from its storey's floor is a `WARN`, and one opening to no listed
storey is printed. Where a normal or emission PNG exists, on any class,
it checks the binding on every tier (emission: its UV attribute and
default-off factor) and measures the albedo under the mask's neutral
pixels against the glazing band; coloured pixels are reported as luminous
fixtures. It does not check `variants.png` or variant naming. A `PASS`
covers only its printed check.

The vehicle classes (`vehicle_car`, `vehicle_van`, `vehicle_truck`,
`vehicle_bus`) take the class's ceilings and atlas size, one material, the
vehicle notes list and the version 3 sidecar (its doors included: order,
mirrored pairs, the plan box's side and rear, the cargo door), skip the
glazing measure
(their emission holds lamps), and add `scripts/vehicle_checks.py`, which
reads the accessors directly: the class box, mirror reach, ground contact,
origin and `LOD0`'s plan box on every tier; wheel and lens pairs mirrored;
`COLOR_0` as normalised `UNSIGNED_BYTE` `VEC4` with A 255, whole ids from the
allowed sets, one R and G per triangle, unpainted body under lamps and
glass; each tier's wheel parts, wheel sides and required and listed ids;
wheel vertices inside their sidecar cylinders and no body vertex inside one;
10 mm steer clearance; lamp faces inside their lens rectangles, no lens
without a face, lit lens texels; glass ids against `glass_texels.png` both
ways, lit cabin texels and the glass band; emission black under plain faces;
painted faces neutral grey.

- Geometry checks inspect only the first mesh in each tier. Multi-mesh exports
  need manual aggregate counts, bounds and material slots.
- The ORM check finds the file; it does not verify bindings, factors, UVs, mip
  safety or cross-tier materials. Trace those in the GLB (Texture
  Requirements).
- `MANUAL` lines are reminders, not the full list. Unresolved authoring checks
  block completion; consumer checks that cannot run here are recorded as
  pending.

**Hidden-surface results are inspection candidates, not proof.** The test casts
40 fixed directions from each face centre and can miss narrow escapes,
misjudge partly exposed faces, or miss interactions between objects. Inspect
candidates by sections, isolation or topology; weigh count, area, connected
extent and percentage together. Remove buried partitions, duplicate surfaces
and unused geometry; document the small closure faces you keep. Recessed glass
is exterior surface.

### Universal (every class)

- Required files open; the whole export has no loose geometry, unintended holes
  or non-manifold joins (checked on a welded copy; exported normal/UV splits
  are kept).
- Material slots within budget; every tier uses the intended variant's
  materials with correct bindings and factors.
- PNGs lossless, 8-bit, square, power of two, within size limits; colour
  spaces correct; normals OpenGL `+Y`; no alpha.
- ORM present and bound on every tier; the normal map too for buildings (for
  props and vehicles when used), at scale 1;
  emission binding checked when used; image URIs resolve to external files
  with no `bufferView`. Laps and seams read raised, not dented, in a lit
  render.
- Atlas ownership, padding, periodic boundaries and mipmapped appearance pass
  Texture Requirements, oblique and distant views included. Consumer filtering
  recorded as pending.
- Palette per Style Direction; no baked lighting or reflections in albedo;
  glass/material separation reviewed in representative lighting.
- Glazing inside the Style Direction band and darker than its surrounding trim,
  painted with `scripts/glazing.py`, or a brief-driven exception recorded
  (vehicle glass: Vehicles).
- No unexplained buried partitions or duplicate interior surfaces.
- All six views inspected (a vehicle: its review sheet); LODs compared at
  intended switches with fixed camera and lighting; dominant colours and
  materials consistent across tiers.
- Variants keep tier geometry and UVs; per-texture size limits met; unique
  texture inventory recorded.
- Reference Image Policy met; no recognisable real building or object.
- `preview.png` is `LOD0`, default variant, catalog setup. `notes.md` has the
  class's sections in order, describes the current state, marks inapplicable
  fields `n/a`, and keeps completed checks separate from pending ones.

### Buildings only

- Four tiers, `LOD0`–`LOD3`, within their ceilings (ordinary, or hero where
  documented), without padding.
- Switch distances and cameras recorded; Appearance Across LODs passes for
  adjacent pairs and against `LOD0`: roofs, recesses, window rhythm, corner
  contrast.
- Every tier faces `-Y` and shares the authored ground-level origin.
- The facts sidecar passes the validator with `source.dirty` false, and its
  doors (their floors and storeys too), footprint, storeys and dwellings
  describe the building as built.
- Geometry and Construction defaults followed, or exceptions carry comparison
  evidence and cost. Opaque glass and door closures; no exposed interior;
  roof-hiding parapets on every tier.
- Footprint includes projections; story height ~3.0–3.3 m or explained.
- Door leaves 2.0–2.4 m (~2.6 m ceremonial) with a transom/fanlight above
  taller openings; sills checked against the door and the floor.
- Every opening recessed at grade stands on its 0.02 m slab on every tier
  that keeps the recess: the validator's door floors for the doors, a look
  for set-back glazing and portals.
- Glazed buildings have correctly bound emission on every tier, default off and
  controllable on reimport, or a recorded reason for none. `variants.png`
  covers every colour; lit window patterns stay consistent across tiers except
  for documented, reviewed removals.
- Large-building variants coherent per instance, with the choice explained.

### Props only

- `LOD0`/`LOD1` present; optional `LOD2` cost and benefit recorded
  (boundary pieces: all four tiers, plan bounds equal, facts sidecar).
- Small/medium/boundary triangle bands met; below-floor counts explained.
- Pivot and plan bounds unchanged across tiers; `-Y` front only for
  genuinely asymmetric props, verified on reimport.
- Switch/cull distances and appearance reviewed at prop scale.
- Variants 1–2 (boundary up to 3), or a documented exception.

### Vehicles only

- Four tiers within the class's ceilings and what each must keep; the class
  box, mirrors and ground contact on every tier; `-Y` front, the origin at
  the body's plan centre.
- `COLOR_0` normalised `UNSIGNED_BYTE` `VEC4` on every tier, A 255, ids whole
  and per triangle; no other custom attribute.
- Wheels: parts, sides, cylinders and 35° clearance pass; the review sheet's
  turned wheels look right.
- Every required lamp and glass id present; lens rectangles and glass texels
  pass; each lamp group, the night set and the cabin checked lit on the
  review sheet.
- Painted panels neutral grey, their field 0.70–0.80 and every tier's
  painted mean within 10 % of `LOD0`'s; plates blank, no body colour baked;
  white, dark grey and red paint read right on the review sheet, with no
  brightness jump between tiers.
- Every lens states its lit colour, matching the emission.
- The facts sidecar passes with `source.dirty` false and describes the
  vehicle as built, its doors on the shut lines the atlas draws;
  `glass_texels.png` matches the atlas.
- A generic composite after the owner's direction, with no recognisable make
  or real livery; the review sheet looked at, and kept out of the commit.

## What Not To Do

Standing repo policy; finished-asset gates live in Validation Checklist,
with rationale in owning sections.

- Never commit reference images, in any commit.
- No pre-compressed source textures: clean/lossless PNG; consumer importer
  owns compression/mipmaps.
- No pack manifests or consumer terms: raw `.glb` + textures, plus facts
  sidecar holding geometry and file facts only (Output Contract).
- No large binary commits outside Git LFS.
- No tracked scratch/test `.blend` files.
- No `.py` commits without `# SPDX-License-Identifier:
  GPL-3.0-or-later` first line (Licensing).
- No new top-level docs beyond `README.md`, `LICENSE.md`, `CATALOG.md`,
  and per-asset `notes.md` without a durable distinct role.

## AI Behaviour Guidelines

- Act as a rigorous technical 3D generalist: flag budget violations, ambiguous
  references and reference-policy conflicts directly; no quiet workarounds.
- **Ask the owner before building a new asset.** Bring the researched
  examples and two or three design directions (type and era, form, size,
  one model or several, sign text) with a recommendation, and build only
  what the owner picks. A request relayed by another session or agent is a
  brief, not the owner's approval of a design.
- Check `CATALOG.md` before generating; no unjustified duplicate of an existing
  style or variant.
- Confirm Reference Image Policy compliance before importing any external
  reference image into Blender, not after.
