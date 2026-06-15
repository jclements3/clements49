# Clements 49 — Acoustic Baseline (soundbox shape definition)

Defines the current (47-string reference model) acoustic state and the parametric levers
to expose in `soundbox.scad` for perfecting the **new 49-string soundbox shape**.
All geometry in millimetres, z-up, frame per `anchors.json`. Numbers are tagged
**[model]** (from the extracted geometry / string schedule), **[lit]** (handbook/literature
class values) or **[est]** (first-order estimate with stated assumptions).

This document deliberately *improves conceptually* on the single-slice cavity placeholder
that `materials.md §8` flags: the cavity is integrated from the **seven measured
cross-sections** as a lofted, leaning taper, and the Helmholtz model uses the **back
soundhole array** combined into an equivalent aperture rather than one slice.

---

## 1. Current soundbox acoustic state (47-string reference)

### 1.1 Cavity volume — lofted from cross-sections **[est]**

The soundbox is a lofted taper between the seven measured sections (perpendicular to z,
marching +x with height because the body leans). Each station's cross-section is modelled
as an ellipse of semi-axes `wx/2 × dy/2` with a **fill factor 0.62** (the real harp
cross-section is a rounded wedge / half-ellipse, not a full ellipse), integrated
trapezoidally along the body arc length (Δx,Δz between section centroids), plus a bass-end
extension cap (~80 mm) and a treble tip cone.

| fill factor | cavity volume |
|-------------|---------------|
| 0.55        | 40.3 L        |
| **0.62 (adopted)** | **45.4 L** |
| 0.70        | 51.3 L        |

**Adopted cavity volume V ≈ 45 L (0.045 m³)**, with a defensible band of **40–51 L**
driven by the cross-section fill assumption. This supersedes the single-slice placeholder.

### 1.2 Soundhole (back) total area **[est]**

Concert-harp soundboxes vent through a graded column of **5 oval "eyes" on the back**,
large at the bass end, small toward treble. Modelled as ellipses (long × short axis):
120×85, 110×78, 95×68, 78×56, 60×44 mm.

**Total soundhole area S ≈ 253 cm² (25,300 mm²)**, equivalent single-hole radius
a_eq ≈ 90 mm. (The exact diameters live in the source asset's back panel/`harp_back_bolt_*`
region and should be re-measured against the asset; this is the order-correct estimate.)

### 1.3 Helmholtz cavity resonance **[est]**

`f_H = (c/2π)·√( S / (V·L_eff) )`, c = 343 m/s, the 5 holes combined into one equivalent
aperture of area S, effective neck length `L_eff = wall_thickness + 1.7·a_eq`
(≈ 4 mm shell + 153 mm end correction = 157 mm).

**f_Helmholtz ≈ 103 Hz** (G2–G♯2 region).

Sensitivity (fixed S, L_eff):

| cavity V | f_H |
|----------|-----|
| 30 L | 127 Hz |
| 40 L | 110 Hz |
| **45 L** | **103 Hz** |
| 50 L | 98 Hz |

So the air resonance lands in the **low-mid (~100 Hz, G2 ± a few semitones)** — it props
up the bottom-mid, not the true bass. This is normal for harps: the lowest strings
(B0 ≈ 31 Hz, C1 ≈ 33 Hz) radiate well below the air mode and rely on board/string
coupling, not the cavity, for their fundamentals.

### 1.4 Soundboard fundamental — order of magnitude **[est]**

The board is a spine-and-wings sandwich (thin spruce/cedar skins over Nomex/balsa core,
CF+flax spine; `materials.md §6.1`). Modelled bounds:

- Effective sandwich rigidity D ≈ 460 N·m (1.5 mm spruce skins, 6 mm core), areal mass
  μ ≈ 1.4 kg/m².
- Long-axis (U) pinned-beam mode over the 1,078 mm span → ~24 Hz (lower bound; ignores
  bracing/spine and transverse coupling).
- Simply-supported plate first mode (1.078 × 0.22 m) → ~600 Hz (upper bound; overstiff,
  too much transverse stiffness assumed).

The boundary conditions and orthotropy span more than an order of magnitude; the honest
statement is the **coupled whole-board first mode (T(1,1)) sits in the ~90–150 Hz region**
**[lit]** for instruments of this size, close to and coupling with the ~100 Hz Helmholtz
mode (the classic air/board doublet). **Order of magnitude: ~10² Hz.** Closing this number
needs measured flax/skin E, ρ, the chosen core depth and crown radius (`materials.md §8`).

---

## 2. Parametric levers for the new 49-string soundbox

Each lever below maps to a parameter name implemented in `soundbox.scad`. The soundbox is
generated as a **lofted taper between control sections** (improving on the single slice):
the control sections are driven by these parameters so the shape, cavity and apertures are
co-designed rather than fixed.

| param | acoustic role | sensible range |
|-------|---------------|----------------|
| `cavity_fill_factor` | Cross-section fullness (full-ellipse vs rounded-wedge). Sets cavity volume → Helmholtz pitch and low-mid support. | 0.55–0.70 (default 0.62) |
| `body_depth_profile` | Multiplier vector on `depth_y` at each control station (back stand-off from board). Deeper = more volume, lower f_H, warmer; tapers fore-aft. | 0.85–1.20× of model depths |
| `body_width_profile` | Multiplier on `width_x` (across-string) per station. Widens bass corner for bass radiation; couples to board taper. | 0.85–1.20× |
| `body_length_scale` | Stretch of the body long axis (bass→treble span). Tracks the string-schedule span; +2 strings lengthens the bass corner. | 1.00–1.10 |
| `bass_corner_bulge` | Extra depth+width concentrated at the bass end (lowest 2 sections) to host the B0 extension without globally enlarging the box. | 1.00–1.25 |
| `back_curvature_radius` | Transverse crown radius of the back shell (cross-section curvature). Smaller R = stiffer, deader back; larger R = flatter, "live" back adds low end (`materials.md §6.2` open item). | 200 mm – flat (∞) |
| `back_liveness` | Effective back-panel compliance switch/scale (stiff/dead ↔ live), realised as back skin thickness/core. Live back broadens/lowers the air-coupled response. | 0 (dead) – 1 (live) |
| `soundhole_count` | Number of back soundholes. More holes raise S → raise f_H and lower Q (more damped, broader). | 3–6 (default 5) |
| `soundhole_scale` | Global multiplier on hole areas. Sets total S → f_H pitch and venting/damping. | 0.7–1.4× |
| `soundhole_grade_exp` | Bass→treble size grading exponent (large at bass). Shapes where venting happens along the body. | 0.5–1.5 |
| `soundhole_axis_offset` | Placement of the hole column along the back centreline (fraction of body length). Moves the acoustic centre of the aperture. | 0.2–0.8 of length |
| `wall_thickness` | Flax shell wall (enters L_eff and shell stiffness/mass). Thicker = lower f_H slightly, deader, heavier. | 3–6 mm |
| `board_span` | Soundboard U-length (bass→treble). Single-source from string schedule; drives board mode + body length. | 1000–1130 mm (spec 1078) |
| `board_width_bass` / `board_width_treble` | Board taper endpoints (V-width). Spec 380→70 mm; sets wing area → radiating efficiency and the 37° string rake fan. | bass 340–420, treble 55–90 mm |
| `board_crown_radius` | Longitudinal crown (camber) of the soundboard. Shell action against the ~5,500 N perpendicular pull; raises board stiffness/fundamental and projection. | 1500 mm – flat |
| `core_depth` | Sandwich core thickness in the wings. Dominant lever on board stiffness vs mass → board fundamental and radiation. | 4–12 mm |
| `skin_thickness` | Tonewood radiating-skin gauge. Trades stiffness/mass (board mode) vs cosmetic-veneer regime. | 0.8–2.5 mm |
| `board_taper_coupling` | Couples board span+taper to the string schedule's `s_board` law (bass extension grows the bass wing/corner automatically). | on/off + 0.0–1.0 blend |

These are the parameters returned in `tunable_params` (structured output) and to be
implemented in `soundbox.scad`. Material/layup choices (skin material, core type, back
liveness as a build) ride on the wood↔flax switch from `materials.md §6`.

---

## 3. Bass-extension implications (added low strings) **[est]**

The 49-string schedule adds **B0 (idx 0, f₀ ≈ 30.9 Hz, vibrating length 1,354.5 mm)** below
C1, and A7 above G7. The bass end is what grows.

- **Board length:** integrating the schedule's `s_board(idx)` spacing law, the board span
  grows **+~31 mm (+4.2%)** going 47→49 strings, almost entirely at the bass end (the
  bass-most gap B0–C1 is the widest at 24.0 mm; the added treble gap A7–G7 is only 6.5 mm).
- **Bass reach:** the new B0 is 47.7 mm longer in vibrating length than the old longest
  string (C1, 1,306.8 mm), so the **bass corner of the board + neck must reach ~50 mm
  farther** to host it.
- **Cavity / depth:** the cavity supports the low-mid via the ~100 Hz Helmholtz mode, not
  the 31 Hz bass fundamentals, so the box need not be tuned an octave lower. But the added
  bass weight wants proportionally more bass-end air and board area. To keep the
  air-resonance position relative to the (now lower) bass register, target
  **cavity volume +8–15% (≈ 49–52 L)**, concentrated at the bass end via `bass_corner_bulge`:
  **bass-corner depth_y ~539 → ~590–620 mm** and **body length +~50–65 mm** at the bass end.
  Globally the rest of the taper is unchanged — the parametric `bass_corner_bulge` and
  `body_length_scale` levers isolate this growth so the treble half of the box is untouched.

**Net:** the bass extension is a *bass-corner-local* change (~+4% board length, ~+10% bass-end
volume, ~+50 mm reach), not a whole-body rescale — consistent with the schedule's
"+1 bass / +1 treble" symmetric-ish resolution that keeps 47→49 propagation incremental.

---

## 4. Open / to-close (carry into the structural + coupled-acoustic run)

- Re-measure the actual back soundhole diameters/positions from the source asset (drives S, f_H).
- Measured flax/skin E, ρ, chosen core depth and crown radius to pin the board fundamental
  (currently OOM only).
- A coupled two-DOF air/board model (Helmholtz mode + T(1,1) board mode) to predict the
  doublet split — the single-slice and even this lofted-cavity model are still uncoupled.
- Confirm fill factor against a watertight cavity boolean once the parametric shell exists
  (the reference `frame_only.stl` is a surface mesh, not usable for boolean volume).
