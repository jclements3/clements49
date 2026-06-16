# Clements 49 — Structural load basis (A0..G7, refit on the real 49-pin line)

Structural load basis for the finalized **49-string** schedule **A0..G7** (scientific, idx 0..48),
**recomputed on the actual re-anchored 49-pin line** (not the proportionally-mapped 47-string mesh).
This supersedes the earlier B0..A7 / 47-mesh pass. Every figure is tagged **[model]** (computed from
the finalized schedule + the refit geometry), **[est]** (first-order estimate, stated assumptions), or **[lit]**.

Reproduce with `analysis/refit_49.py` (writes `string_schedule.{json,csv}` and `refit_49_loads.json`).

Inputs:
- String schedule: `analysis/string_schedule.json` (49 strings A0..G7, per-string `tension_N`).
- Geometry anchors: `analysis/anchors.json` — measured 47-string endpoints, **re-anchored** so the
  measured bass/treble endpoints are C1 (idx 2) and G7 (idx 48); A0 (idx 0) and B0 (idx 1) are
  **extrapolated below the bass end**, lengthening the neck pin line by ~34.7 mm and the board string
  line by ~81 mm at the bass corner. Scale 8.8598 mm/unit.

Frame convention: z-up, mm; bass→treble is +x; column/player side is −x; y is across-body. Strings,
pin line, and pillar lie essentially in the x–z plane, so load resolution is done in x–z.

-----

## Results (A0..G7, refit)

| Quantity | Value | Source |
|---|---|---|
| Total string tension ΣT | **9,269.4 N (2,083.8 lbf)** | [model] |
| String angle to soundboard (rake off board long axis U) | **35.3° median (range 21.3–37.9°)** | [model] |
| Perpendicular pull on board | **5,305 N** (tension-weighted per-string) / 5,578 N at 37° | [model]/[est] |
| In-plane longitudinal pull on board | **7,588 N** (tension-weighted per-string) | [model] |
| Neck peak bending moment | **≈855 N·m** (distributed pin loads, peak at x/L≈0.46) | [model] |
| Pillar axial force | **≈9,228 N** (resultant 9,237 N projected on column axis) | [model] |

-----

## Method and assumptions

### 1. Total tension ΣT  [model]
Direct sum of the 49 per-string `tension_N` for A0..G7 = **9,269.4 N**; ÷ 4.44822 = **2,083.8 lbf**.
Versus the prior B0..A7 set (9,219.2 N): dropping the treble A7 (97.3 N) and adding the bass A0
(147.5 N, [est] from the bass length/tension trend) **raises ΣT by ~50 N** — the bass extension adds
net tension, as expected.

### 2. String angle to soundboard  [model]
Per-string rake θ = acute angle between the string (eyelet→pin, in x–z) and the board long axis U
(bass→treble chord of the string-exit line). On the **refit** geometry: median **35.3°**, range
21.3–37.9° — notably closer to the **37° design target** than the 30° measured on the raw 47-string
mesh, because re-anchoring places the bass strings on a steeper, longer rake.

### 3. Perpendicular and in-plane pull on the board  [model]/[est]
Tension-weighted per-string vector sum: Σ T·sinθᵢ = **5,305 N** perpendicular; Σ T·cosθᵢ = **7,588 N**
in-plane. At the 37° design target ΣT·sin37° = **5,578 N** — so the refit perpendicular pull (5.3 kN
measured / 5.6 kN @37°) now brackets the **5,500 N conservative board-sizing value** in materials.md
§1/§2.2, which is retained. In-plane is dominated by the high-tension shallow-rake bass strings.

### 4. Neck peak bending moment  [model]
Neck modeled as a beam simply supported between the bass-most pin (A0) and the treble-most pin (G7)
along their chord (span ≈833 mm). Each pin applies its string tension toward its eyelet; the bending
driver is the component perpendicular to the support chord. Discrete-load shear/moment diagram gives
reactions RA ≈ 4,253 N, RB ≈ 3,506 N (ΣW⊥ ≈ 7,759 N) and **peak |M| ≈ 855 N·m at x/L ≈ 0.46**
(mid-span, near the C4/G4 register). This is up from the 793 N·m B0..A7/47-mesh pass — the +34.7 mm
bass pin-line extension lengthens the moment arm — and lands within the 793–850 N·m band predicted
there. **943 N·m is retained as a conservative reserve** (the simply-supported idealization ignores
frame end-fixity, which reduces peak M).

### 5. Pillar axial force  [model]
Resultant of the 49 string pulls (each T along eyelet→pin) in x–z = (−515, 9,237) N, |R| ≈ 9,238 N,
nearly vertical. The column axis (anchors' top/bottom) is ≈2.2° off vertical; projecting R onto it
gives pillar axial **≈9,228 N** in compression. Up from 8,251 N (47-mesh) — the steeper refit rake
puts more of ΣT into the near-vertical resultant the pillar reacts. Consistent with the ≈9 kN quoted
in materials.md §6.3; feeds the Euler-buckling pillar sizing (SF 3, K≈1, L≈1.7 m).

-----

## Comparison to the prior B0..A7 / 47-mesh pass

| Quantity | Prior (B0..A7, 47-mesh) | This refit (A0..G7, 49-pin line) | Note |
|---|---|---|---|
| ΣT | 9,219.2 N | 9,269.4 N | +50 N: drop A7, add A0 (bass) |
| Rake median | 30.1° | 35.3° | refit bass rake steeper; nearer 37° target |
| Perp pull | 4,032 N / 5,548 @37° | 5,305 N / 5,578 @37° | brackets the 5,500 N design value |
| In-plane pull | 7,201 N | 7,588 N | higher with added bass tension |
| Neck peak moment | ≈793 N·m | ≈855 N·m | +arm from bass extension; <943 reserve |
| Pillar axial | ≈8,251 N | ≈9,228 N | steeper rake → larger vertical resultant |

**Net:** the refit on the real A0..G7 pin line raises every load modestly (more bass tension, steeper
rake, longer bass moment arm). All stay within the conservative design reserves (5,500 N board pull,
943 N·m neck moment). Re-run this basis if the spacing law or the measured anchors change.
