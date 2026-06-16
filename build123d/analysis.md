# Clements 49 — Acoustic + Structural Analysis (parametric model)

Driven entirely by `clements49_params.STRINGS` (49-string schedule) and
`parts/soundbox.py`. Adding/removing strings in `params_strings.json` +
`analysis/string_schedule.json` re-drives every number below — ΣT, the rake
distribution, and the soundboard load all recompute from the live data.

Units: model units (~8.86 mm/unit, `UNIT_MM = 8.8598`). `V_mm3 = V_units *
UNIT_MM**3`; `litres = V_mm3 / 1e6`.

## 1. Cavity volume + Helmholtz A0

**MEASURED (parametric solid, `soundbox()` — straight-sided half-cone loft):**
- V = **71483.4 model-units³** = **49,713,808 mm³** = **49.71 L**

**Cross-check vs reference mesh (`stl/soundbox_body.stl`, trimesh):**
- mesh V = 72339.8 units³ (mesh is NOT watertight; bbox 60.8×92.9×136.8 vs
  parametric 49.3×92.6×136.0).
- Difference ≈ **+1.2%** (mesh larger). The parametric body is a clean
  straight-sided half-cone (D-section, flat soundboard chord + elliptical
  belly); the mesh includes the slightly bulged back staves and wider X extent,
  so it reads marginally larger. Volumes agree to ~1%, confirming the
  parametric cavity.

**Helmholtz A0 (ESTIMATED — back sound-holes are NOT modeled yet):**
`f0 = (c/2π)·√(A / (V·L_eff))`, c = 343,000 mm/s, V = 49.71 L,
L_eff = wall t + flange end-correction (~1.7·r), assumed wall t ≈ 8 mm.
Hole area is the dominant unknown — these are assumptions, not measurements:

| assumed back holes | A (mm²) | L_eff (mm) | A0 (Hz) |
|---|---|---|---|
| 3 × ⌀40 mm | 3770 | 42.0 | **~73 Hz** |
| 3 × ⌀50 mm | 5890 | 50.5 | **~84 Hz** |
| 2 × ⌀60 mm | 5655 | 59.0 | **~76 Hz** |

So A0 lands in the **~70–85 Hz** band for typical harp sound-hole areas —
roughly D2–F2. To finalize A0, model the actual back sound-holes and feed their
true total area + wall thickness into the formula above.

## 2. Structural — string loads

From `params.STRINGS` (49 strings, all with `tension_N`):

- **ΣT = SIGMA_T_N = 9269.4 N** (sum of all 49 string tensions; recomputed sum
  matches exactly).
- per-string tension: **102.7 N (G7, treble) … 261.3 N**, mean 189.2 N.

**Rake distribution** (angle of each string's board→pin vector off the
soundboard long axis, ~+Z):
- range **0.8° … 6.4°**, mean **2.3°** (quartiles ~0.9° / 1.7° / 3.5°).
- Rake grows from bass (≈0.9°) toward treble (G7 ≈6.4°): the short treble
  strings splay most relative to the box axis.

**Load resolved at the soundboard anchors** (each string pulls along its
board→pin unit vector):
- in-plane, along board long axis (Z): **ΣT·|u_z| = 9261.3 N** — i.e. essentially
  all of ΣT pulls *along* the soundboard toward the neck. This is the dominant
  lengthwise load the box/neck/pillar must react.
- perpendicular, out of the soundboard face (along its ±Y normal):
  **ΣT·|u_y| = 66.4 N** — the small "lifting" component off the soundboard plane.
- scalar tension sum (reference): 9269.4 N.

Interpretation: the strings run almost parallel to the box axis (tiny Y
deflection), so the soundboard sees a large in-plane longitudinal pull (~9.26
kN) and only a small (~66 N) net out-of-plane pull. The perpendicular figure is
geometry-sensitive; the structurally governing number is ΣT ≈ **9.27 kN**
in-plane.

## 3. Measured vs estimated

| quantity | status | source |
|---|---|---|
| cavity volume 49.71 L | **measured** | `soundbox()` solid `.volume` × UNIT_MM³ |
| mesh volume 72340 units³ (+1.2%) | **measured** | trimesh on `stl/soundbox_body.stl` |
| ΣT = 9269.4 N | **measured** (from schedule) | `params.SIGMA_T_N` |
| tension range / rake distribution | **measured** (computed from params) | `STRINGS[*].board/pin/tension_N` |
| in-plane 9261.3 N / perp 66.4 N | **derived** (from params geometry) | board→pin direction × T |
| Helmholtz A0 ~70–85 Hz | **ESTIMATED** | needs real back sound-hole area + wall t |

**Re-analysis note:** all the above are functions of the live params. Add 2
strings to the schedule (+geometry) and ΣT, the load split, the rake range, and
(if box dims change) the cavity volume / A0 all recompute automatically by
re-running `_analysis_calc.py`.
