# Clements 49 — Soundbox re-loft data

**Units:** mm.  **Frame:** z-up; origin=base footprint centre (x,y), z=0 floor; +x bass->treble; soundboard face +y (front); body bulges -y (back)

**Enclosed cavity (air) volume:** **53.08 L**  (outer solid 56.76 L; wall 4.0 mm). Measured from the rendered `soundbox_cavity()` solid.

> NOTE on the y-axis: the current sections are super-ellipses **centred on y=0**, so the model box bulges symmetrically in front of (+y) and behind (−y) the soundboard plane (board face is at y≈+1.9). Physically the box should sit **behind** the board (−y only). The limaçon re-loft is the place to fix this: pin the FRONT edge at the board plane (y≈0) and bulge only to −y.

## 1. Cross-sections (horizontal slices, normal +z), bass→treble

`depth_y` = full front↔back extent; `y_front` = soundboard edge (+y), `y_back` = bulge (−y). Full ordered (x,y) outlines (≈100–150 pts each) are in `soundbox_reloft_data.json` → `sections[].outline_xy`.

| z | x_center | width_x | depth_y | y_front | y_back | pts |
|---|---|---|---|---|---|---|
| 130 | -104.4 | 236.5 | 580.6 | 290.3 | -290.3 | 149 |
| 258 | -11.2 | 227.9 | 549.8 | 274.9 | -274.9 | 107 |
| 440 | 87.4 | 198.7 | 457.6 | 228.8 | -228.8 | 105 |
| 622 | 155.1 | 179.6 | 364.0 | 182.0 | -182.0 | 153 |
| 804 | 256.4 | 164.1 | 291.2 | 145.6 | -145.6 | 149 |
| 986 | 351.7 | 134.7 | 227.4 | 113.7 | -113.7 | 149 |
| 1168 | 467.5 | 95.6 | 156.4 | 78.2 | -78.2 | 149 |
| 1290 | 536.7 | 61.5 | 113.8 | 56.9 | -56.9 | 149 |

## 2. Soundbox axis (centerline through section centroids)

Length **1329.2 mm** over z [130, 1290]. Points (x,0,z): (-104.4,130); (-11.2,258); (87.4,440); (155.1,622); (256.4,804); (351.7,986); (467.5,1168); (536.7,1290)

## 3. Soundboard

- String span A0→G7 (3D chord): **1310.4 mm**; U-length span ≈ 1149.0 mm.
- Width taper (bass→treble): **380.0 → 70.0 mm**.
- Rake to strings: **37.0° design** (35.3° measured on the mesh).
- 49 string-crossing (anchor) points on the board: see JSON `soundboard.string_crossings` (idx, note, xyz). First A0 = [-247.1, 1.9, 117.4], last G7 = [441.7, 1.9, 1232.2].

## 4. Sound-holes (back, −y)
| k | z | long | short |
|---|---|---|---|
| 0 | 393.9 | 120.0 | 85.0 |
| 1 | 559.2 | 105.0 | 74.8 |
| 2 | 724.5 | 90.0 | 64.5 |
| 3 | 889.9 | 75.0 | 54.2 |
| 4 | 1055.2 | 60.0 | 44.0 |

## 5. Construction notes
- continuous lofted super-ellipse shell (NOT faceted staves); no internal ribs/bulkheads modeled in the soundbox (soundboard carries a CF/woven spine; base has bulkheads). Back transverse crown radius = 200 mm (param).
- Source formats: SVG plate (renders/clements49_plate.svg); STL reference (cad/reference/*.stl, gitignored); original OBJ (extract/, gitignored). No STEP/BREP (geometry is mesh + parametric OpenSCAD).
