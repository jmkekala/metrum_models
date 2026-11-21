# tiilimuuri_run_2m

## Style brief

A 2.00 m straight run: the wall and one pier on its −X joint plane. It is the filler beside a gate: the run that arrives at `tiilimuuri_gate_left`.

A plain mid-century industrial brick perimeter wall (*tiilimuuri*),
1950s–60s, neutral enough for any works yard: it fences the power plant's
lot and later the mine's. A one-brick wall on a low cast-concrete plinth
course, a precast concrete coping with its top at 2.10 m, and brick piers
0.40 m square rising to 2.25 m under a plain flat concrete cap. No
buttresses, lamps, ground strip or vegetation. Nothing projects beyond the
piers, so the pieces' plan bounds stay thin: the consumer treats each
piece's whole plan rectangle as a solid obstacle and places 25–30 pieces
per lot by coordinates and 90° turns. An opening is a gap between pieces.

Generic: no lettering, brands or recognisable real wall. The gate's plate
is a plain no-entry roundel with no text.

## Category and secondary use

`props/boundary/`, the brick perimeter wall family (`tiilimuuri_*`): the 10, 5 and 2 m runs, the pierless 2 m run, the free-standing pier and the two gate sides. No secondary use.

## Footprint

LOD0 bounds (glTF): x −1.225 … 0.900, y 0 … 2.250, z −0.225 … 0.225, so 2.125 × 0.450 m in plan and 2.25 m high, against a 1.80 m standing figure: the wall top is 0.30 m over its head, the piers 0.45 m.

| | x | z (across) | height |
| --- | --- | --- | --- |
| Joint planes | −1.000 and 1.000 (pitch 2.000) | | |
| Wall body (brick on the plinth course) | −1.000 … 0.900 | ±0.125 (0.25 thick) | 0 … 2.02 |
| Coping (precast concrete) | same | ±0.175 (0.05 overhang) | 2.02 … 2.10 |
| Pier centred on x −1.000 | −1.200 … −0.800 | ±0.200 | 0 … 2.17 brick |
| its cap | −1.225 … −0.775 | ±0.225 | 2.17 … 2.25 |

The −X pier overhangs the −X joint plane by half a pier (0.225 m with its cap); the wall's +X end is 0.10 m short of the +X joint plane. Both are deliberate (Construction): the pivot is the joint planes' midpoint, not the plan's centre (x −0.163).

Footprint in the facts sidecar (ground-level plan outline, glTF [x, z]): (−1.200, −0.200), (−0.800, −0.200), (−0.800, −0.125), (0.900, −0.125), (0.900, 0.125), (−0.800, 0.125), (−0.800, 0.200), (−1.200, 0.200).

## Construction

Built by `scripts/boundary_wall.py`, shared by the whole family; `build.py` names the piece (`Run(2.0)`) and nothing else. Each tier is a set of closed solids joined by the exact boolean (`asset_build.union`) where they meet, welded, coplanar faces with continuous UVs dissolved, triangulated and checked closed.

- **Pivot (attachment point):** on the ground, on the wall's centre line, midway between the two joint planes. Authored, not the plan's centre: `asset_build.Asset(pivot=(0, 0, 0))`, and every tier keeps LOD0's plan bounds.
- **Front:** the street face, glTF +Z (Blender −Y). Every piece has one, since the joint rule needs a direction of travel; runs and piers are symmetric front to back in shape and texture.
- **Parameters:** wall 0.25 m, coping 0.35 × 0.08 m to 2.10 m, plinth course 0.25 m (painted, flush), run piers 0.40 m to 2.17 m under a 0.45 × 0.08 m cap, end inset 0.10 m, pier pitch 5.00 m; gate pier 0.50 m to 2.48 m under a 0.55 × 0.12 m cap, hinge post 0.08 × 0.07 m to 2.15 m, leaf 3.00 × 2.00 × 0.04 m from 0.05 m.

### Joint rule

All coordinates in these notes are in the exported glTF frame: metres, +Y
up, +Z toward the street (Blender −Y), origin at the pivot.

- **Straight joint.** A run of length L has its joint planes at x = ±L/2.
  The next run along the line has the same yaw and its pivot (L + L′)/2
  further along local +X, so the two joint planes coincide. Pitch = L.
- **Piers.** Each run carries one pier centred on its −X joint plane, and
  the 10 m run another at x = 0, so a line of 5 m and 10 m runs has a pier
  every 5.00 m. There is none at +X: the wall stops 0.10 m short of the +X
  joint plane (x = L/2 − 0.10), inside whatever closes it. No wall end face
  is ever coplanar with a pier face.
- **Corner.** Keep the street on each piece's local +Z: going round a lot
  with the outside on the right of the direction of travel (seen from
  above), the yaw about +Y steps by +90° at each convex corner (local +X
  turns from +X to −Z), −90° at a concave one. Both centre lines meet on
  the corner point, which is the arriving run's +X and the departing run's
  −X joint plane; the departing run's pier, centred on the corner, swallows
  both wall ends (pier 0.40 m against a 0.35 m coping and a wall end
  0.10 m inside it).
- **Free end.** Put `tiilimuuri_pier` with its pivot on the open +X joint
  plane (any yaw).
- **Gate.** For an opening of clear width W between caps: `tiilimuuri_gate_left`
  with its pivot on the opening's −X edge plane, `tiilimuuri_gate_right` on
  the +X edge plane, W apart, same yaw as the line. The run arriving at
  gate_left is any run, its +X joint plane on gate_left's pivot (the gate
  pier closes it; do not add a pier piece). The run leaving gate_right is
  `tiilimuuri_run_2m_pierless`, its −X joint plane on gate_right's pivot
  (pivot 1.00 m further on). A run with its own pier there would put that
  pier half into the opening, beside the gate pier. Each leaf lies along
  the yard face for 3.105 m from the opening edge: wall must continue that
  far on both sides. The work order's 6.0 m truck gate in a 10 m cell is,
  from the cell's −X joint plane: `tiilimuuri_run_2m` at +1.00,
  gate_left at +2.00, gate_right at +8.00, `tiilimuuri_run_2m_pierless`
  at +9.00; the next run's pier closes the cell at +10.00.

## Per-tier triangle counts

| Tier | Triangles | Ceiling (`prop_boundary`) |
| --- | --- | --- |
| `LOD0` | 60 | 200 |
| `LOD1` | 36 | 120 |
| `LOD2` | 28 | 80 |
| `LOD3` | 24 | 48 |

- `LOD0`: the wall as one prism of its T section (body and overhanging coping), each pier as its brick shaft under an overhanging cap; the union notches the piers' faces round the wall.
- `LOD1`: the coping flush (a box to 2.10 m, its sides painted with the coping), each pier one box of its cap's plan with an edge ring at 2.17 m: cap paint above, brick below.
- `LOD2`: the wall box and plain pier boxes of the cap's plan, the pier band stretched (×1.14 in V) so the cap's paint still lands on the top 0.08 m.
- `LOD3`: two closed boxes: the pier and the wall span beyond it (2 × 12). The piers are `LOD2`'s boxes of the cap's plan to 2.25 m, the band stretched so the cap's paint lands on their top; the wall body is a box 0.25 m thick to 2.10 m, the coping painted on its sides and its top, from a pier's face to the next or to the wall's `LOD0` end. Each wall span abuts a pier's face rather than passing into it, so no solid enters another, and no union is needed. Height and plan bounds are `LOD0`'s. The cost is 1 buried contact face (a wall end on a pier's face, 2 triangles each): the hidden-surface test lists 4 of 24 triangles (1.5 m² vertical), those wall ends and the pier faces they abut, which are half visible round the wall. A union of the same boxes is `LOD2`'s 28 triangles.

Geometry only where it changes the outline: the coping's and caps' overhangs (shadow lines), the piers' projection and rise, the leaf and its post. Brick, mortar, the plinth course, coping joints, the leaf's frame, ribs, hinges and plate are texture.

## LOD review

Intended switches (prop scale, the catalog's review camera: perspective, 50° vertical FOV, 1920 × 1080): `LOD0` under ~25 m, `LOD1` ~25–50 m, `LOD2` ~50–150 m, `LOD3` beyond ~150 m by distance. The consumer picks a tier by the piece's size on screen, not by distance, so on these small pieces `LOD3` shows from about 25 m; every tier therefore keeps the piers (a 0.40 m pier spans ~18 px at 25 m and its 0.15 m rise over the coping ~7 px). The cap and coping overhangs (0.025 and 0.05 m) are under a pixel past ~35 m.

Reviewed for `tiilimuuri_run_10m` and `tiilimuuri_gate_left` at 10, 20, 40 and 80 m, front and oblique, noon sun, every tier (`review/boundary_wall_2026_11_21/lod_*`, `lod_sheet_*.png`): `LOD0`–`LOD2` hold the silhouette, pier rhythm, coping line and cap colour; the gate's tiers are indistinguishable from 20 m. The gate keeps pier and leaf on every tier.

`LOD3` at the consumer's ~25 m (`review/followups_2026_11_21/wall_lod3/`): `pairs_*.png` set `LOD0`, `LOD2` and `LOD3` side by side at 25 and 40 m, street and yard side, for `tiilimuuri_run_10m`, `tiilimuuri_run_5m`, `tiilimuuri_gate_left` and `tiilimuuri_run_2m_pierless`; `cmp_*.png` the assembled lots at `LOD0`, the new `LOD3` and the former `LOD3` box without piers. The runs' `LOD3` reads as the same wall with its piers and caps and is indistinguishable from `LOD2` at both distances; the pierless run's box and the gate's two boxes are indistinguishable from their `LOD0` at 25 m.

Assembled lots at `LOD3` (the closed 30 × 20 m lot, the gate cell with a free end, a corner with a free end; `review/followups_2026_11_21/wall_lod3/L3_*`, at 25, 40 and 80 m, top and aerial): one pier at every joint and corner, no gaps. A run's `LOD3` wall stops where its `LOD0` wall does, 0.10 m short of its +X joint plane inside the next piece's pier, 0.10 m inside that pier's faces and 0.15 m under its top, so no two neighbours' faces are coplanar: a triangle-by-triangle check of the assembled files finds no coplanar overlap above the ground (the former `LOD3` had 8.9 m² of it), only the bottoms meeting on the ground plane, as at `LOD0`. Renders from two camera positions 5 mm apart show no change at the joints, but Blender's rasteriser does not shimmer even on the former overlaps, so that is no proof; depth fighting is pending in the consumer.

## Texture set

One 512 × 512 atlas at 64 texels/m, shared by all seven pieces (painted once by `scripts/boundary_wall.py export` and written into each piece's `export/` under its own name). Supersampling `atlas.SS` = 4, box-filtered in linear light; `atlas.pad()` last.

- rows 0–140, **WALL** band, tiling in U (8 m period), V = height from the ground: plinth course 0–0.25 m, stretcher-bond brick (0.25 × 0.078 m courses) to 2.02 m, the coping's sides 2.02–2.10 m with a joint every 1.00 m.
- rows 142–314, **PIER** band, same brick and plinth to 2.48 m, then the gate cap's sides to 2.60 m (run caps map their 0.08 m onto its first rows).
- rows 318–460, unique: the leaf (192 × 128 px, U from the hinge end), the hinge post, a cap top, patches (blank, soffit, paint, concrete).
- rows 466–502, **TOP** strip, tiling in U, V across the wall: the coping's top ±0.175 m with 1 m joints, brick tops to ±0.225 m, which no tier samples since `LOD3` keeps the piers.

Relief heights for the normal map: brick faces 6 mm over the mortar, coping and cap arrises 20 mm, leaf frame 25 mm, pressed ribs 8 mm, hinges 30–40 mm. Weathering (`scripts/weathering.py`, moderate): soil and algae at the plinth, splash-back and a little salt bloom above it, light runs under the coping and the gate cap, dust on coping and cap tops, kicked-up dirt and grime at the leaf's foot and latch, rust at the steel's feet.

Mips: not separately reviewed with `review_atlas_mips.py`; the bands are full-width and wrap in U, the unique regions sit in ≥4 px of their own padding. Pending in the consumer.

Unique textures per piece: 5 PNGs at 512 (3 albedo, ORM, normal), identical across the seven pieces.

## Variant list

Three, the plant's brick, with the gate's paint as the transformer yard's gate pairs it:

- `red_brick` (default): brick (114, 73, 62), darker (90, 59, 51), mortar (125, 123, 118); grey-green paint (66, 82, 76).
- `yellow_brick`: (188, 166, 122), (164, 142, 104), mortar (160, 156, 148), as `muuntajakentta_walled`; oxide red-brown paint (104, 56, 44).
- `brown_brick`: (80, 59, 57), (62, 46, 45), mortar (108, 106, 102); blue-grey paint (60, 68, 76).

Three rather than CLAUDE.md's 0–2 for props: a boundary wall matches the buildings it encloses (Props, boundary pieces).

## Export

One material, `tiilimuuri_run_2m`, on every tier: albedo → `baseColorTexture`, ORM → `metallicRoughnessTexture` and `occlusionTexture`, normal → `normalTexture` at scale 1, all external PNGs with no `bufferView` (checked by the validator on every tier). No emission: unlit (`night_lit=False`), no `variants.png`. glTF export by `asset_build.export_all()`: GLB, selection only, +Y up, modifiers applied, keep original textures, no cameras or lights.

Rebuild from the repository root:

```bash
python3 scripts/boundary_wall.py export props/boundary/tiilimuuri_*
blender --background --python props/boundary/tiilimuuri_run_2m/build.py
blender --background --python props/boundary/tiilimuuri_run_2m/build.py -- facts
```

Facts sidecar `export/tiilimuuri_run_2m.model.json`: schema 1, hero false, dwellings 0, no doors, no storeys, no passages, the footprint above, bounds from `LOD0`.

## Review status

Done here:

- `scripts/validate_asset.py … prop_boundary`: 0 FAIL; the one WARN is the sidecar's `source.dirty` (written before commit).
- Front, top and oblique views (`review/boundary_wall_2026_11_21/views/`), the catalog preview.
- Test assemblies from the exported `LOD0` and `LOD3` files by the joint rule alone: a closed 30 × 20 m lot of 10 m and 5 m runs, a 6 m gate in a 10 m cell between 10 m runs, a free end and a corner (`assembly/`). One pier at every joint and corner, no gaps, no step in the coping line, no wall end showing.
- LOD comparisons at 10–80 m for the 10 m run and gate_left.
- `LOD3` against the consumer's screen-size switching (2026-11-21): the seven pieces rebuilt and validated (0 FAIL; the three runs' rewritten sidecars warn `source.dirty` until rewritten from a commit), the textures not rebaked, the `LOD0`–`LOD2` files and the other four pieces' `LOD3` byte-identical, every `preview.png` pixel-identical (the committed files kept), the assemblies and LOD pairs above at 25 and 40 m, a coplanarity check of the assembled `LOD3` and `LOD0` files.

Pending in the consumer: switch and cull distances, mip filtering, depth fighting at the joints (none expected: no coplanar faces above the ground), the obstacle rectangles against its pathing.

## Tooling versions

Blender 5.3.0 (hash 02f0899d78e3), headless; the MCP addon was not used. System Python 3 with numpy 2.5.5, scipy 1.18.1, Pillow 13.0.0 for the atlas.

## Revision log

- 2026-11-21: `LOD3` keeps the piers (12 → 24 triangles, height 2.10 → 2.25 m): the consumer switches tiers by screen size and showed the pierless box at ~25 m. Its wall stops where `LOD0`'s does, ending the coplanar overlaps at joints. `prop_boundary`'s `LOD3` ceiling 24 → 48.
