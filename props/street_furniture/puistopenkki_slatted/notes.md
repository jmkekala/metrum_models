# puistopenkki_slatted

## Style brief

A plain Nordic municipal park and street bench (*puistonpenkki*) of the
mid-century-to-present type found across Finnish towns: two dark cast end
frames, each one flat casting (front leg, seat rail, rear leg and back stay)
with a raised rim round its outline; four timber seat slats and three back
slats, bolted to the frames with carriage bolts. Seat 0.45 m high and
0.44 m deep, the back leaning 14° from vertical to 0.82 m, 1.80 m long with
the slats overhanging each frame by 0.18 m. No armrests.

Weathered at the catalog's moderate level: the paint (or oil) chalked on
the upward faces and most where people sit, worn through to the wood in
flecks along the front seat slat's front arris and the top back slat's top
edge, soil splash and a little rust at the frames' feet, faint rust round
the bolt heads, road dust in the cavities.

Generic: no designer model, maker's mark, lettering or plaque.

## Category and secondary use

`props/street_furniture/`, a small prop. No secondary use.

## Footprint

LOD0 bounds (glTF, metres): x −0.900 … 0.900, y 0 … 0.824, z −0.306 … 0.290. So **1.80 × 0.60 m in plan and 0.82 m high**.

Against the 1.8 m standing figure (`review/followups_2026_11_21/bench/figure_1p8m_*.png`): the seat top (0.45 m) is at the figure's knee, the back's top (0.82 m) just under its hip. The bench is as long as the figure is tall.

| | glTF y (height) | glTF z (front +) |
| --- | --- | --- |
| Seat slats, 4 × 0.095 × 0.04, gaps 0.02 | 0.41 … 0.45 | 0.290 … −0.150 |
| Back slats, 3 × 0.085 × 0.025, gaps 0.0275, 14° | 0.52 … 0.82 | −0.16 … −0.26 |
| End frames, 0.045 thick at x ±0.70 | 0 … 0.82 | 0.290 … −0.306 |
| Front feet / rear feet (ground contact) | 0 | 0.290 … 0.235 / −0.235 … −0.290 |

## Construction

Built by `build.py` from the dimensions in `bench_atlas.py`. Each tier is several **disjoint closed solids in one mesh**, not a union: each part is built closed, the parts are joined, triangulated and checked closed (every edge on exactly two faces, no zero-area face). The validator's welded manifold check accepts this (0 boundary, 0 over-two edges on both tiers).

- **Pivot (attachment point):** on the ground at the centre of the four feet (between the front and rear feet's contact strips, on the bench's centre line). Authored at the build origin with `asset_build.Asset(pivot=(0, 0, 0))`. The plan's bounding box centre lies 8 mm behind it, because the back leans out 16 mm further than the rear feet. Every tier keeps LOD0's plan bounds, which `asset_build.build_all()` asserts.
- **Front:** authored. A backed bench is asymmetric, so the seat's front (the side you sit on) faces Blender −Y, glTF +Z.
- **Parameters:** slats 1.80 m; frames at x ±0.70, 0.045 thick; rail top 0.41, rail underside 0.355; seat slats 0.095 × 0.04, gap 0.02; back slats 0.085 × 0.025, gap 0.0275, on the stays' front faces from 0.11 to 0.42 m along them; stay 0.045 wide to 0.425 m along it, leaning 14°; front foot 0.055 long, rear foot 0.055 long, rear leg splayed 0.2 m per metre of height.

### End frame profile

Seen from the side, LOD0's 11-point outline runs: front foot, front leg's inner edge, the rail's underside, the rear leg's inner edge down to the rear foot, the rear leg's outer edge up to its kink with the stay's back edge, the stay's top, the stay's front edge down to the rail top, the rail top forward, and the front leg's front edge. It is extruded 0.045 m across the frame. The slats rest on the rail top and on the stay's front face. Those contact faces are coplanar and face opposite ways. They are not unioned: a union would cut every slat's underside round each frame for about 48 more triangles, and the contact can't be seen.

### Hidden contact faces

The validator's hidden-surface test reports 8 of LOD0's 164 triangles (4.9 %) and 8 of LOD1's 80 (10 %). They are the frames' rail tops under the slats (or the seat wedge), 0 m² of it vertical. These are the kept closure faces described above.

## Per-tier triangle counts

| Tier | Triangles | Band (`prop_small`) | Split |
| --- | --- | --- | --- |
| `LOD0` | 164 | 50–300 | frames 2 × 40, seat slats 4 × 12, back slats 3 × 12 |
| `LOD1` | 80 | 12–80 | frames 2 × 32, seat wedge 8, back wedge 8 |
| `LOD2` | none | optional | not made, see LOD review |

- `LOD0`: each frame is an 11-point profile prism (2 × 9 cap triangles + 11 side quads). Each slat is a closed box. The gaps between slats are real, so frames, ground and sky show through them.
- `LOD1`: each frame is a 9-point profile. Each foot becomes a point midway across it; the stay's top keeps both corners and the rear leg keeps its kink, so the side outline and the plan bounds hold. The rail top is raised at the back to meet the seat wedge's sloping underside, so no light shows between them. The seat is one right-triangle prism: a vertical front face, a flat top, and an underside sloping up to the stay. The back is one right-triangle prism: its rear face on the stays, full thickness at the top edge. Both wedges map onto composites of the LOD0 slats' faces with the gaps painted a neutral mid-dark. 80 is the band's ceiling exactly.
- 136 triangles of LOD0's 300 ceiling are unused. More would not change the silhouette at 5–20 m, and the geometry is not padded.

## LOD review

Review camera as the catalog's (`scripts/review_asset.py`): perspective, 50° vertical FOV, 1920 × 1080, distance along the view to the bench's front. Cycles, noon and reverse (sun behind) light.

- **Distances reviewed:** 3, 8 and 20 m front and oblique (`dist/`), six orthographic views (`six/`), LOD0 against LOD1 at 15, 20 and 30 m front, oblique and side under noon and reverse light (`lod/`, `lod_sheet2_x4.png`). Both variants at 3, 8 and 20 m (`brown/`).
- **Projected sizes:** the bench's 1.80 m spans ~105 px at 20 m and ~70 px at 30 m. A back gap (2.75 cm) spans ~1.6 px at 20 m and ~1.1 px at 30 m; a seat gap (2 cm) ~1.2 and ~0.8 px.
- **Proposed switches:** `LOD0` → `LOD1` at **~30 m**. Cull at ~70–80 m, where the bench is under ~30 px and LOD1's 80 triangles are cheap.
- **Seen at 30 m:**
  - Under noon light the two tiers match: silhouette, seat line, back rake, legs, colour and the painted slat rhythm.
  - Under reverse light LOD1's back reads as one dark board, where LOD0 still lets the ground show through its two gaps. This is a known limitation at the 80-triangle ceiling. Real back gaps at LOD1 need three back wedges (+16), which leaves the frames 7 points each: either a thick straight rear member or a back floating 4.7 cm off the stays at its top. Both are worse from the side. At 20 m the loss is plainly visible, which is why the switch is not proposed nearer.
  - The pointed feet show as tapered leg ends in a pure side view at 20 m and are inconspicuous at 30 m.
- **No `LOD2`:** a further tier (frames as 4-point plates, 40 triangles) would lose the legs' opening and save 40 triangles on an asset already culled at ~70–80 m. That is not a useful reduction for the identity it costs.
- Pending in the consumer: real switching and culling distances, and shadow-map behaviour of the slat gaps.

## Texture set

One 256 × 256 atlas at **64 texels/m on every modelled face**. Each slat has its own strip at full density: U along it, V round its section. Supersampling `atlas.SS` = 4, box-filtered in linear light; `atlas.pad()` last. About 35 % of the atlas is claimed; the rest is padding.

- rows 4–21 and 27–44: the four seat slats, two per row, 115.2 px long. V runs front face, top, back face, underside.
- rows 50–64 and 70–84: the three back slats. V runs front face, top edge, rear face, foot edge.
- (132–146, 70–84): slat end grain, sampled at its centre by every slat end. (152–166, 70–84): LOD1 seat underside.
- rows 92–121 (x 4) and rows 92–112 and 118–138 (x 132): **LOD1 composites**. These are the seat top and the back's front and rear faces, copied sample by sample from the strips, every channel and weather field included, with the gaps painted between. Wear and grain on LOD1 are therefore LOD0's.
- rows 144–197 (x 4): the frame's face, U and V its y and z. It is shared by both faces of both frames, mirrored on two of them, which a plain casting allows.
- rows 204–207 (x 4–220): the frames' edge strip. U is the distance round LOD0's outline and V runs across the casting. LOD1's edges sample it at LOD0's perimeter distances.

**Relief heights** for the normal map (`atlas.normal_map()`, OpenGL):

- slat arrises rounded 4 mm over 0.7 px, with grain 0.3 mm;
- worn wood 0.4 mm below the paint;
- carriage bolt heads 7 mm;
- the casting's rim 5 mm over a 2–3 px band, its outer arris rounded, with pitting 0.4 mm;
- frame edges bevelled 3 mm;
- LOD1 gap lines 2 mm down.

**Weathering** (`scripts/weathering.py`, moderate): `grime()` and `fade()` overall, extra fade on seat tops (strongest over the middle 1.2 m) and back fronts, dust on undersides and top edges, splash and rust at the frame face's foot (V is height there), dirt and rust on the edge strip by height (interpolated from the outline), and rust round each bolt. After `pad()`, cavity dust. The bare-wood wear is painted as an id (`ID_WORN`) so each variant colours it.

**Mips:** not separately reviewed with `review_atlas_mips.py`. Regions keep ≥ 3 px apart (asserted in `check_layout()`), and the composites are padded from their own edges. At 30 m and beyond the bench samples mip 2–3, where neighbouring regions blend; all regions are the same dark paint or iron family. Pending in the consumer.

**Unique textures:** 4 PNGs at 256: 2 albedo, the ORM and the normal map, shared by both variants. Mean texel footprint matches the buildings' 64/m. The slats' 4 cm thickness is only 2.6 texels, and the catalog preview's close framing magnifies that softness (see Review status).

## Variant list

Two, the CLAUDE.md default for props. A town paints its benches one colour, so the pair covers the two finishes a municipal catalog actually uses rather than a colour range:

- `green_painted` (default): dark municipal green paint on the timber (50, 72, 56), wearing through to grey weathered wood (112, 104, 90); end grain (44, 60, 48); black paint on cast iron (46, 47, 48).
- `brown_oiled`: oiled timber (112, 82, 58), bleaching grey where the oil has gone (140, 126, 106); end grain (86, 62, 44); dark grey painted steel (64, 66, 68).

Fixed across both: the LOD1 gap tone (70, 70, 68) and the bolt heads (74, 74, 72). Roughness and metallic are shared, so the ORM is one file: paint or oiled wood 0.58, worn wood 0.82, end grain 0.78, iron 0.55, bolts 0.45 and metallic 0.6. Only the albedo differs between variants.

## Export

One material, `puistopenkki_slatted`, on both tiers:

- albedo → `baseColorTexture`;
- ORM → `metallicRoughnessTexture` and `occlusionTexture`;
- normal → `normalTexture` at scale 1.

All are external PNGs with a `uri` and no `bufferView`; traced in both GLBs and checked by the validator. Both tiers reference the default albedo; `brown_oiled` is the same mesh with that one file swapped. There is no emission (`night_lit=False`), no `variants.png` and no facts sidecar (plain props ship none).

glTF export by `asset_build.export_all()`: GLB, selection only, +Y up, modifiers applied, keep original textures, no cameras or lights. The image `bufferView`s are stripped afterwards.

Rebuild from the repository root:

```bash
python3 props/street_furniture/puistopenkki_slatted/bench_atlas.py export
blender --background --python props/street_furniture/puistopenkki_slatted/build.py
```

The second step builds both tiers, exports them, renders `preview.png` and saves `source.blend`.

## Review status

Done here:

- `scripts/validate_asset.py … prop_small`: 0 FAIL, 0 WARN. Both tiers pass container, bindings, one slot, manifold, budget, ground pivot and hidden surface; `LOD2` is SKIP (optional, absent). Textures pass 256 RGB, the normal encoding and the ORM's presence.
- The six orthographic views, oblique at 3, 8 and 20 m, LOD0 against LOD1 at 15–30 m in two lights, both variants, the 1.8 m figure (`review/followups_2026_11_21/bench/`).
- Orientation on reimport: the seat's front at glTF +Z (bounds z max 0.290 is the seat's front edge), the back toward −Z.
- The slat arrises and casting rim read raised in lit renders.
- The catalog `preview.png` (standard setup).

The validator does not check that a plain prop's tiers share LOD0's plan bounds; `asset_build.build_all()` asserts it at build time.

The standard preview, fitted to the bounds, frames the bench from about 3.5 m. At that distance one texel covers 2–3 screen pixels, so the preview shows the 256 atlas softer than the bench reads at its 5–20 m use distances. The preview also carries no scale cue.

Pending in the consumer: switch and cull distances, mip filtering, shadow-map treatment of the slat gaps, and placement against paths. The placement rule is pivot on the ground, front +Z toward the path.

## Tooling versions

Blender 5.3.0 (hash 02f0899d78e3), headless; the MCP addon was not used. System Python 3 with numpy 2.5.5, scipy 1.18.1, Pillow 13.0.0 for the atlas.
