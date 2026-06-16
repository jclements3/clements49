# Clements 49 — Back Sound-Hole Sizing & Placement Study

Companion to the soundbox handoff. This sizes and places the back sound-holes to land
the air resonance **A0 ≈ 130 Hz**, just under the first soundboard mode (~150 Hz), and
keeps the holes large enough to double as stringing access.

---

## 1. Model

Lumped Helmholtz resonator, calibrated to Le Carrou's concert-harp measurements (×1.123):

```
A0 = 1.123 · (c / 2π) · sqrt( A_total / ( V · L_eff ) )
L_eff = t_wall + 1.7 · a_eq        (a_eq = per-hole equivalent radius)
```

- `c` = 343 m/s, `t_wall` = 8 mm (the structural belly the holes pass through).
- `A_total` = sum of hole areas; `V` = enclosed cavity volume.
- `1.7·a_eq` is the two-sided orifice end correction; holes are treated as parallel necks.

This is a lumped estimate. The real instrument is a **coupled** air-cavity / soundboard
system, so treat A0 as a starting target to verify by measurement on the prototype, not a
guaranteed number.

---

## 2. Cavity volume (from the box as drawn)

The volume drives everything, so it's taken from the actual loft, not assumed:

| quantity | value |
|---|---|
| loft length (stringbar) | 1,355 mm |
| outer limaçon volume | 64.8 L |
| **cavity (inner, after the graded wall)** | **58.2 L** |

> **Correction to earlier notes.** I had been carrying a 35 L target and a ~240 cm² hole
> figure. Both were wrong for this box. The a = 2b limaçon is a large round section
> (380 × 345 at the bass), so the enclosed cavity is **58 L**, and the matching hole area
> is **smaller** than 240 cm². This study supersedes those numbers.

---

## 3. Required hole area

Solving the model for A0 = 130 Hz at V = 58.2 L, t_wall = 8 mm, 5 holes:

| target | result |
|---|---|
| A0 | 130 Hz |
| **total hole area** | **≈ 165 cm²** |
| per-hole equivalent radius | 32 mm |
| effective neck length L_eff | 63 mm |

---

## 4. Hole sizing (5 holes, graded bass→treble)

Areas graded larger at the bass (more low-end radiation, bigger body, easier hand access
where the heavy strings are). Ovals at ~1.6:1, long axis running along the body.

| hole | station s | area (cm²) | oval long × short (mm) |
|:--:|:--:|:--:|:--:|
| #1 (bass) | 0.12 | 43.5 | 94 × 59 |
| #2 | 0.30 | 39.2 | 89 × 56 |
| #3 | 0.48 | 34.3 | 84 × 52 |
| #4 | 0.66 | 28.3 | 76 × 47 |
| #5 (treble) | 0.84 | 20.2 | 64 × 40 |
| **total** | | **165.5** | |

The four bass-side holes clear ~75 mm in the long axis — a hand fits for stringing. #5 is
deliberately small (the treble strings need least access and the body is narrow there).

---

## 5. Placement (belly centerline)

Centers lie on the back/belly centerline, `P(s) + D(s)·belly`, with
`belly = [0.852, 0, -0.523]` and depth `D(s)` the dimple→belly distance. World mm:

| hole | x | y | z |
|:--:|:--:|:--:|:--:|
| #1 | 60 | −2 | 81 |
| #2 | 154 | −2 | 310 |
| #3 | 244 | −2 | 541 |
| #4 | 328 | −2 | 776 |
| #5 | 401 | −2 | 1018 |

Spacing leaves solid wall at both ends and between holes for the rib/ring structure. Cut
each oval through the 8 mm belly wall, long axis along the local body direction.

---

## 6. Sensitivity

| change | A0 |
|---|---|
| total area 132 cm² (−20%) | 122 Hz |
| **total area 165 cm² (nominal)** | **130 Hz** |
| total area 199 cm² (+20%) | 137 Hz |
| volume 46.6 L (−20%) | 145 Hz |
| **volume 58.2 L (nominal)** | **130 Hz** |
| volume 69.9 L (+20%) | 119 Hz |

A0 scales roughly with √(area) and 1/√(volume). The +20% area case (137 Hz) still clears
the ~150 Hz board mode; the −20% volume case (145 Hz) starts to crowd it, so if the built
cavity comes out smaller than modeled, trim hole area to drop A0 back down. **Tuning lever
on the finished box: shave hole area to lower A0, open it to raise A0** — easier than
changing volume after the fact.

See `holes.png` for the to-scale hole layout and the A0-vs-area curve with the V = 52–64 L
band.

---

## 7. Open items

- [ ] Verify A0 on the prototype (tap test / cavity excitation); adjust hole area to tune.
- [ ] Confirm the 8 mm belly thickness at each hole location after the wall study/FEA;
      L_eff (hence A0) moves with wall thickness.
- [ ] Check holes don't land on a soundboard-mode antinode or a structural rib once those
      are placed.
- [ ] If access needs push the holes larger than 165 cm² total, raise A0 above 130 —
      either accept it (stay < 150) or add cavity volume to compensate.
