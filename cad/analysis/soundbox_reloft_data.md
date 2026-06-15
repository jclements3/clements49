# Clements 49 — Soundbox re-loft data

**Units:** mm.  **Frame:** z-up; origin=base footprint centre (x,y), z=0 floor; +x bass->treble; soundboard face +y (front); body bulges -y (back)

**Enclosed cavity (air) volume:** **53.08 L**  (outer solid 56.76 L; wall 4.0 mm). Measured from the rendered `soundbox_cavity()` solid.

> NOTE on the y-axis: current sections are super-ellipses **centred on y=0**, so the box bulges symmetrically in front of (+y) and behind (−y) the soundboard plane (board at y≈+1.9). Physically the box should sit **behind** the board (−y only). The limaçon re-loft should pin the FRONT edge at y≈0 and bulge only to −y.

## 1. Cross-sections (horizontal slices, normal +z), bass→treble

Full ordered (x,y) outlines in JSON → `sections[].outline_xy`.

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

## 2. Soundbox axis
Length **1329.2 mm** over z [130, 1290]. Points (x,0,z): (-104.4,130); (-11.2,258); (87.4,440); (155.1,622); (256.4,804); (351.7,986); (467.5,1168); (536.7,1290)

## 2b. Attachment footprints

**Soundbox→base** (join z=126.1): base part footprint x[-494.5, 494.5] y[-266.9, 266.9], base top z=140.0. Soundbox end outline (149 pts) in JSON `attachments.soundbox_to_base`. Soundbox bass cap seats onto the base top (base spans z 0..140). Contact = the soundbox end outline below, dropped onto the base top plane (z=140).


**Soundbox→neck** (join z=1323.0): neck pin-line treble end [476.15, 20.84, 1404.38], neck section [40, 33] mm, pillar top [-303.11, 54.0, 1859.75]. Soundbox end outline (149 pts) in JSON `attachments.soundbox_to_neck`. Neck (super-ellipse 40x33 mm at this end) ties into the treble-top of the body; the pillar top closes the frame triangle at the point above.

## 3. Soundboard

- String span A0→G7 (3D chord): **1310.4 mm**; U-length ≈ 1149.0 mm.
- Width taper: **380.0 → 70.0 mm**.
- Rake: **37.0° design** (35.3° measured).
- 49 string crossings in JSON `soundboard.string_crossings`. A0=[-247.1, 1.9, 117.4], G7=[441.7, 1.9, 1232.2].

## 4. Sound-holes (back, −y)
| k | z | long | short |
|---|---|---|---|
| 0 | 393.9 | 120.0 | 85.0 |
| 1 | 559.2 | 105.0 | 74.8 |
| 2 | 724.5 | 90.0 | 64.5 |
| 3 | 889.9 | 75.0 | 54.2 |
| 4 | 1055.2 | 60.0 | 44.0 |

## 5. Construction
- continuous lofted super-ellipse shell (NOT faceted staves); no internal ribs/bulkheads modeled in the soundbox (soundboard carries a CF/woven spine; base has bulkheads). Back transverse crown radius = 200 mm (param).
- Sources: SVG plate (renders/clements49_plate.svg); STL reference (cad/reference/*.stl, gitignored); original OBJ (extract/, gitignored). No STEP/BREP (geometry is mesh + parametric OpenSCAD).
