# Clements 49 — Limaçon Soundbox: Geometry Handoff

A flax-composite soundbox for the 49-string (A0–G7) "Clements 49" concert pedal harp,
voiced warm. The cross-section is a **limaçon of Pascal**. This document fixes the
geometry, the orientation frame, the wall logic, and where the soundboard Bézier plugs
in, and ends with a runnable SVG of the section and an OpenSCAD generator.

---

## 1. The one-line idea

> **Outer mold line = a limaçon at `a:b = 2`** (so the stringbar lands on a *flat*),
> **inner mold line = a free-form graded wall** (thin to sing, ribbed to hold the
> string tension). Sections are cut perpendicular to the raked stringbar and lofted
> bass→treble; the soundboard outline only sets how wide each section is.

---

## 2. Coordinate frame & orientation

All from the 49 board pins (the grommet line) in `strings_49.json`. The stringbar axis
is the principal axis of those pins.

| vector | value | meaning |
|---|---|---|
| `û` (U_AXIS) | `[0.523, 0, 0.852]` | stringbar axis, raked **31.6°** from vertical, lies in the x–z plane |
| `ŷ` (Y_MINOR) | `[0, 1, 0]` | soundboard **width** direction = limaçon **minor** side |
| `n̂` (N_BOARD) | `[-0.852, 0, 0.523]` | soundboard **normal**, in x–z |
| belly | `[0.852, 0, -0.523]` = −n̂ | dimple→belly, hangs **underneath** (−z) |

**Section plane is perpendicular to `û`.** Its two in-plane axes are `ŷ` and `n̂`, and
`ŷ × n̂ = û` (right-handed), which is why the two limaçon diameters land in *different*
coordinate planes:

- **minor axis (width)** runs along **`ŷ`** → reads in the **y–z** plane;
- **major axis (depth / belly)** runs along **`n̂`** → reads in the **x–z** plane, going −z.

That split is not a contradiction — it's what happens when the section plane is tilted
(perpendicular to a raked axis) instead of aligned to a coordinate plane.

---

## 3. Cross-section geometry

### 3.1 Outer = limaçon, `a:b = 2`  (the flat seat)

Polar form `r = a + b·cos θ`. Convexity is governed by the sign of
`g(θ) = r² + 2r′² − r·r″`, which for this curve reduces to

```
g(θ) = a² + 3ab·cos θ + 2b²
g_min = g(π) = a² − 3ab + 2b² = (a − b)(a − 2b)
```

| ratio | `g_min` | shape |
|---|---|---|
| `a < b` | — | inner loop (curve threads the origin) |
| `a = b` | — | cardioid (cusp at origin) |
| `b < a < 2b` | `< 0` | **dimpled** — genuine concave indentation |
| **`a = 2b`** | **`= 0`** | **flat point at θ=π — convex boundary** |
| `a > 2b` | `> 0` | strictly convex (egg) |

We use **`a = 2b`** for the outer: at θ=π the curvature is exactly zero, so the outer
surface is **flat** right where the stringbar meets it. A straight bar wants a flat seat,
not a pocket — that is the whole reason for the choice. (Earlier drafts used `a < 2b`,
which puts a *concave* dent there; wrong for a straight bar.)

At `a:b = 2` the section is **380 wide × 345 deep** at the bass, ratio **d/w = 0.91**.

### 3.2 Inner = free-form graded wall

The inner curve is **not** a limaçon and is not tied to `a:b`. It is the outer offset
inward by a thickness `t(θ)` that varies around the section. That single freedom carries
the structural job without touching the outer shape.

---

## 4. The proportions lesson (why this split is the fix)

A *true* limaçon has its width-to-depth ratio **locked** by `a:b` — for every dimpled
ratio the perpendicular width is the *larger* dimension and the dimple→belly depth the
*smaller* one. You cannot independently choose width and depth and still have a limaçon;
forcing it (scaling x and y by different factors) breaks `r = a + b·cos θ` and yields a
distorted egg, not a limaçon.

The resolution: **only the outer is a true limaçon** (fixed `a:b = 2`, fixed 0.91 ratio,
scaled uniformly by the soundboard width). **The inner is free**, so all the
thick/thin tuning lives there. No stretching, no conflict.

---

## 5. Wall-thickness rationale

The strings pull **ΣT ≈ 9,269 N** total, of which **~5 kN** presses down through the
grommets onto the board, as a line load along the stringbar (θ=180). The grading follows
that load path:

| zone | θ | thickness | why |
|---|---|---|---|
| **rib** | ≈ 180° (stringbar line) | **~24 mm** | takes the concentrated string-anchor / down-bearing load |
| **radiating board** | flanks of θ=180° | **~3.5 mm** | this face is the radiator; thin = it moves freely |
| **structural belly** | ≈ 0° (back) | **~8 mm** | closes the box, carries the reaction, radiates less |

This is the "thick enough to hold / thin enough to sing" requirement, resolved by
**grading the inner wall**, not by one uniform thickness. The rib carries the load so the
board on either side can stay thin and vibrate.

> **Caveat — these thicknesses are first-pass.** They were set with representative
> flax-composite stiffness to fix the *proportions*, not your layup. Final values need
> your fiber fraction / ply schedule and an FEA pass. Treat them as the starting point,
> not the answer.

---

## 6. Soundboard Bézier control

The soundboard outline is (almost) a **teardrop**: fat rounded bass tapering to a treble
point. Its **half-width along the stringbar is the only thing it controls** — it sets how
wide each limaçon section is, station by station. Nothing else in the geometry depends on
it.

In the generator this is the single function:

```scad
function w_half(s) = HW_BASS * pow(1 - s, TEAR_EXP);   // first-cut teardrop
```

Replace the body with your Bézier evaluated at `s ∈ [0,1]` (bass→treble) returning the
**half-width in mm**. Everything downstream — outer scale, inner offset, the loft —
updates automatically. The outer `a:b` stays 2 regardless.

---

## 7. Acoustic note (independent of section shape)

The A0 cavity (Helmholtz) resonance is driven by **volume and the back sound-holes**, not
the cross-section profile. Target **A0 ≈ 130 Hz**, placed just under the first board mode
(~150 Hz), which wants **~35 L** behind the board plus the graded back holes
(~240 cm² total, 5 holes). The holes are **not** cut by the generator — subtract them from
the belly face afterward. Changing `a:b`, the teardrop, or the wall does not move A0 as
long as the enclosed volume is held.

---

## 8. Lessons learned (so they don't recur)

1. **Superellipses are not limaçons.** `y = D(1−|2x/W|ⁿ)^{1/n}` is a superellipse; don't
   label it limaçon-family.
2. **Sections are perpendicular to the *raked* stringbar**, not cut in horizontal
   (constant-z) planes. The board is raked ~32°.
3. **Axes:** width = `ŷ` (minor, y–z); depth/belly = `n̂` (major, x–z, −z). Don't swap
   them; the soundboard width is the y extent, not the x–z one.
4. **Never anisotropically scale a limaçon** to hit an arbitrary W×D box — it stops being
   a limaçon (the "weird ellipse"). Uniform scale only.
5. **The outer dimple is `a = 2b` (flat), not `a < 2b` (concave).** A straight stringbar
   seats on a flat. The tension thickening belongs to the **inner** wall, which is free.

---

## 9. Open items

- [ ] Replace `w_half(s)` with the real soundboard Bézier (half-width profile).
- [ ] Final wall thicknesses from your flax layup + FEA (current values are first-pass).
- [ ] Cut the 5 back sound-holes from the belly face; tune total area to hold A0 ≈ 130 Hz.
- [ ] Reconcile the ~10–20% frame scatter between `strings_49.json` and the earlier
      `soundbox_reloft_data.json` once rendered against the real STLs.
- [ ] Render the OpenSCAD (I can't here) and confirm the polyhedron is manifold /
      right-side-out.

---

## 10. Section — SVG (bass station)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 470" font-family="sans-serif">
  <!-- wall = outer with inner as even-odd hole -->
  <path d="M300.0,405.2 L310.9,404.9 L321.8,404.0 L332.6,402.5 L343.3,400.3 L353.8,397.6 L364.1,394.3 L374.2,390.5 L384.1,386.0 L393.6,381.1 L402.9,375.6 L411.8,369.7 L420.3,363.3 L428.3,356.5 L436.0,349.3 L443.2,341.7 L449.9,333.7 L456.2,325.5 L461.9,317.0 L467.1,308.2 L471.8,299.2 L475.9,290.1 L479.6,280.9 L482.6,271.5 L485.2,262.1 L487.2,252.6 L488.6,243.2 L489.6,233.8 L490.0,224.4 L489.9,215.2 L489.4,206.1 L488.4,197.1 L486.9,188.4 L485.0,179.8 L482.7,171.5 L480.0,163.4 L476.9,155.6 L473.5,148.1 L469.8,140.9 L465.8,134.0 L461.5,127.5 L457.0,121.3 L452.3,115.4 L447.4,109.8 L442.4,104.6 L437.2,99.8 L432.0,95.3 L426.6,91.1 L421.2,87.3 L415.8,83.7 L410.3,80.5 L404.8,77.6 L399.4,75.0 L394.0,72.7 L388.7,70.6 L383.4,68.8 L378.3,67.2 L373.2,65.8 L368.2,64.7 L363.3,63.7 L358.5,62.8 L353.9,62.1 L349.3,61.6 L344.9,61.1 L340.5,60.8 L336.3,60.5 L332.2,60.3 L328.2,60.2 L324.2,60.1 L320.4,60.1 L316.6,60.0 L312.8,60.0 L309.1,60.0 L305.5,60.0 L301.8,60.0 L298.2,60.0 L294.5,60.0 L290.9,60.0 L287.2,60.0 L283.4,60.0 L279.6,60.1 L275.8,60.1 L271.8,60.2 L267.8,60.3 L263.7,60.5 L259.5,60.8 L255.1,61.1 L250.7,61.6 L246.1,62.1 L241.5,62.8 L236.7,63.7 L231.8,64.7 L226.8,65.8 L221.7,67.2 L216.6,68.8 L211.3,70.6 L206.0,72.7 L200.6,75.0 L195.2,77.6 L189.7,80.5 L184.2,83.7 L178.8,87.3 L173.4,91.1 L168.0,95.3 L162.8,99.8 L157.6,104.6 L152.6,109.8 L147.7,115.4 L143.0,121.3 L138.5,127.5 L134.2,134.0 L130.2,140.9 L126.5,148.1 L123.1,155.6 L120.0,163.4 L117.3,171.5 L115.0,179.8 L113.1,188.4 L111.6,197.1 L110.6,206.1 L110.1,215.2 L110.0,224.4 L110.4,233.8 L111.4,243.2 L112.8,252.6 L114.8,262.1 L117.4,271.5 L120.4,280.9 L124.1,290.1 L128.2,299.2 L132.9,308.2 L138.1,317.0 L143.8,325.5 L150.1,333.7 L156.8,341.7 L164.0,349.3 L171.7,356.5 L179.7,363.3 L188.2,369.7 L197.1,375.6 L206.4,381.1 L215.9,386.0 L225.8,390.5 L235.9,394.3 L246.2,397.6 L256.7,400.3 L267.4,402.5 L278.2,404.0 L289.1,404.9 L300.0,405.2 Z M299.8,397.2 L310.5,396.9 L320.9,396.1 L331.2,394.6 L341.5,392.6 L351.6,390.0 L361.5,386.8 L371.2,383.2 L380.7,378.9 L389.9,374.2 L398.7,369.0 L407.3,363.4 L415.4,357.3 L423.2,350.8 L430.6,343.9 L437.6,336.6 L444.1,329.0 L450.1,321.2 L455.7,313.0 L460.7,304.6 L465.3,296.1 L469.3,287.3 L472.9,278.5 L475.9,269.5 L478.4,260.4 L480.4,251.4 L481.9,242.3 L482.9,233.3 L483.4,224.3 L483.4,215.4 L483.0,206.6 L482.1,198.0 L480.8,189.6 L479.0,181.3 L476.9,173.3 L474.4,165.5 L471.5,157.9 L468.3,150.7 L464.8,143.7 L461.0,137.0 L457.0,130.6 L452.7,124.5 L448.3,118.8 L443.6,113.4 L438.8,108.3 L433.9,103.5 L428.8,99.1 L423.7,95.0 L418.5,91.2 L413.3,87.7 L408.1,84.6 L402.8,81.7 L397.6,79.1 L392.4,76.7 L387.2,74.7 L382.1,72.8 L377.1,71.2 L372.2,69.8 L367.3,68.6 L362.6,67.6 L357.9,66.7 L353.3,66.0 L348.9,65.4 L344.5,64.9 L340.3,64.5 L336.1,64.3 L332.0,64.3 L328.0,64.6 L324.1,65.4 L320.3,67.1 L316.5,69.9 L312.8,73.6 L309.1,77.7 L305.5,81.5 L301.8,83.7 L298.2,83.7 L294.5,81.5 L290.9,77.7 L287.2,73.6 L283.5,69.9 L279.7,67.1 L275.9,65.4 L272.0,64.6 L268.0,64.3 L263.9,64.3 L259.7,64.5 L255.5,64.9 L251.1,65.4 L246.7,66.0 L242.1,66.7 L237.4,67.6 L232.7,68.6 L227.8,69.8 L222.9,71.2 L217.9,72.8 L212.8,74.7 L207.6,76.7 L202.4,79.1 L197.2,81.7 L191.9,84.6 L186.7,87.7 L181.5,91.2 L176.3,95.0 L171.2,99.1 L166.1,103.5 L161.2,108.3 L156.4,113.4 L151.7,118.8 L147.3,124.5 L143.0,130.6 L139.0,137.0 L135.2,143.7 L131.7,150.7 L128.5,157.9 L125.6,165.5 L123.1,173.3 L121.0,181.3 L119.2,189.6 L117.9,198.0 L117.0,206.6 L116.6,215.4 L116.6,224.3 L117.1,233.3 L118.1,242.3 L119.6,251.4 L121.6,260.4 L124.1,269.5 L127.1,278.5 L130.7,287.3 L134.7,296.1 L139.3,304.6 L144.3,313.0 L149.9,321.2 L155.9,329.0 L162.4,336.6 L169.4,343.9 L176.8,350.8 L184.6,357.3 L192.7,363.4 L201.3,369.0 L210.1,374.2 L219.3,378.9 L228.8,383.2 L238.5,386.8 L248.4,390.0 L258.5,392.6 L268.8,394.6 L279.1,396.1 L289.5,396.9 L300.2,397.2 Z" fill="#b9966a" fill-rule="evenodd" stroke="none"/>
  <path d="M300.0,405.2 L310.9,404.9 L321.8,404.0 L332.6,402.5 L343.3,400.3 L353.8,397.6 L364.1,394.3 L374.2,390.5 L384.1,386.0 L393.6,381.1 L402.9,375.6 L411.8,369.7 L420.3,363.3 L428.3,356.5 L436.0,349.3 L443.2,341.7 L449.9,333.7 L456.2,325.5 L461.9,317.0 L467.1,308.2 L471.8,299.2 L475.9,290.1 L479.6,280.9 L482.6,271.5 L485.2,262.1 L487.2,252.6 L488.6,243.2 L489.6,233.8 L490.0,224.4 L489.9,215.2 L489.4,206.1 L488.4,197.1 L486.9,188.4 L485.0,179.8 L482.7,171.5 L480.0,163.4 L476.9,155.6 L473.5,148.1 L469.8,140.9 L465.8,134.0 L461.5,127.5 L457.0,121.3 L452.3,115.4 L447.4,109.8 L442.4,104.6 L437.2,99.8 L432.0,95.3 L426.6,91.1 L421.2,87.3 L415.8,83.7 L410.3,80.5 L404.8,77.6 L399.4,75.0 L394.0,72.7 L388.7,70.6 L383.4,68.8 L378.3,67.2 L373.2,65.8 L368.2,64.7 L363.3,63.7 L358.5,62.8 L353.9,62.1 L349.3,61.6 L344.9,61.1 L340.5,60.8 L336.3,60.5 L332.2,60.3 L328.2,60.2 L324.2,60.1 L320.4,60.1 L316.6,60.0 L312.8,60.0 L309.1,60.0 L305.5,60.0 L301.8,60.0 L298.2,60.0 L294.5,60.0 L290.9,60.0 L287.2,60.0 L283.4,60.0 L279.6,60.1 L275.8,60.1 L271.8,60.2 L267.8,60.3 L263.7,60.5 L259.5,60.8 L255.1,61.1 L250.7,61.6 L246.1,62.1 L241.5,62.8 L236.7,63.7 L231.8,64.7 L226.8,65.8 L221.7,67.2 L216.6,68.8 L211.3,70.6 L206.0,72.7 L200.6,75.0 L195.2,77.6 L189.7,80.5 L184.2,83.7 L178.8,87.3 L173.4,91.1 L168.0,95.3 L162.8,99.8 L157.6,104.6 L152.6,109.8 L147.7,115.4 L143.0,121.3 L138.5,127.5 L134.2,134.0 L130.2,140.9 L126.5,148.1 L123.1,155.6 L120.0,163.4 L117.3,171.5 L115.0,179.8 L113.1,188.4 L111.6,197.1 L110.6,206.1 L110.1,215.2 L110.0,224.4 L110.4,233.8 L111.4,243.2 L112.8,252.6 L114.8,262.1 L117.4,271.5 L120.4,280.9 L124.1,290.1 L128.2,299.2 L132.9,308.2 L138.1,317.0 L143.8,325.5 L150.1,333.7 L156.8,341.7 L164.0,349.3 L171.7,356.5 L179.7,363.3 L188.2,369.7 L197.1,375.6 L206.4,381.1 L215.9,386.0 L225.8,390.5 L235.9,394.3 L246.2,397.6 L256.7,400.3 L267.4,402.5 L278.2,404.0 L289.1,404.9 L300.0,405.2 Z" fill="none" stroke="#5a2d0c" stroke-width="2.2"/>
  <path d="M299.8,397.2 L310.5,396.9 L320.9,396.1 L331.2,394.6 L341.5,392.6 L351.6,390.0 L361.5,386.8 L371.2,383.2 L380.7,378.9 L389.9,374.2 L398.7,369.0 L407.3,363.4 L415.4,357.3 L423.2,350.8 L430.6,343.9 L437.6,336.6 L444.1,329.0 L450.1,321.2 L455.7,313.0 L460.7,304.6 L465.3,296.1 L469.3,287.3 L472.9,278.5 L475.9,269.5 L478.4,260.4 L480.4,251.4 L481.9,242.3 L482.9,233.3 L483.4,224.3 L483.4,215.4 L483.0,206.6 L482.1,198.0 L480.8,189.6 L479.0,181.3 L476.9,173.3 L474.4,165.5 L471.5,157.9 L468.3,150.7 L464.8,143.7 L461.0,137.0 L457.0,130.6 L452.7,124.5 L448.3,118.8 L443.6,113.4 L438.8,108.3 L433.9,103.5 L428.8,99.1 L423.7,95.0 L418.5,91.2 L413.3,87.7 L408.1,84.6 L402.8,81.7 L397.6,79.1 L392.4,76.7 L387.2,74.7 L382.1,72.8 L377.1,71.2 L372.2,69.8 L367.3,68.6 L362.6,67.6 L357.9,66.7 L353.3,66.0 L348.9,65.4 L344.5,64.9 L340.3,64.5 L336.1,64.3 L332.0,64.3 L328.0,64.6 L324.1,65.4 L320.3,67.1 L316.5,69.9 L312.8,73.6 L309.1,77.7 L305.5,81.5 L301.8,83.7 L298.2,83.7 L294.5,81.5 L290.9,77.7 L287.2,73.6 L283.5,69.9 L279.7,67.1 L275.9,65.4 L272.0,64.6 L268.0,64.3 L263.9,64.3 L259.7,64.5 L255.5,64.9 L251.1,65.4 L246.7,66.0 L242.1,66.7 L237.4,67.6 L232.7,68.6 L227.8,69.8 L222.9,71.2 L217.9,72.8 L212.8,74.7 L207.6,76.7 L202.4,79.1 L197.2,81.7 L191.9,84.6 L186.7,87.7 L181.5,91.2 L176.3,95.0 L171.2,99.1 L166.1,103.5 L161.2,108.3 L156.4,113.4 L151.7,118.8 L147.3,124.5 L143.0,130.6 L139.0,137.0 L135.2,143.7 L131.7,150.7 L128.5,157.9 L125.6,165.5 L123.1,173.3 L121.0,181.3 L119.2,189.6 L117.9,198.0 L117.0,206.6 L116.6,215.4 L116.6,224.3 L117.1,233.3 L118.1,242.3 L119.6,251.4 L121.6,260.4 L124.1,269.5 L127.1,278.5 L130.7,287.3 L134.7,296.1 L139.3,304.6 L144.3,313.0 L149.9,321.2 L155.9,329.0 L162.4,336.6 L169.4,343.9 L176.8,350.8 L184.6,357.3 L192.7,363.4 L201.3,369.0 L210.1,374.2 L219.3,378.9 L228.8,383.2 L238.5,386.8 L248.4,390.0 L258.5,392.6 L268.8,394.6 L279.1,396.1 L289.5,396.9 L300.2,397.2 Z" fill="none" stroke="#7a3b10" stroke-width="1.3"/>
  <!-- stringbar on the flat outer -->
  <line x1="150" y1="58" x2="450" y2="58" stroke="#0f5c4d" stroke-width="4"/>
  <circle cx="300" cy="60" r="5" fill="#0f5c4d"/>
  <!-- string stubs -->
  <line x1="180" y1="44" x2="180" y2="58" stroke="#3b7bbf" stroke-width="1"/><line x1="210" y1="44" x2="210" y2="58" stroke="#3b7bbf" stroke-width="1"/><line x1="240" y1="44" x2="240" y2="58" stroke="#3b7bbf" stroke-width="1"/><line x1="270" y1="44" x2="270" y2="58" stroke="#3b7bbf" stroke-width="1"/><line x1="300" y1="44" x2="300" y2="58" stroke="#3b7bbf" stroke-width="1"/><line x1="330" y1="44" x2="330" y2="58" stroke="#3b7bbf" stroke-width="1"/><line x1="360" y1="44" x2="360" y2="58" stroke="#3b7bbf" stroke-width="1"/><line x1="390" y1="44" x2="390" y2="58" stroke="#3b7bbf" stroke-width="1"/><line x1="420" y1="44" x2="420" y2="58" stroke="#3b7bbf" stroke-width="1"/>
  <!-- labels -->
  <text x="300" y="20" text-anchor="middle" font-size="13" font-weight="bold">Clements 49 — limaçon section (bass)</text>
  <text x="455" y="50" font-size="11" fill="#0f5c4d">stringbar on FLAT outer (a=2b)</text>
  <text x="318" y="92" font-size="11" fill="#7a1f1f">rib (inner) — string tension</text>
  <text x="60" y="250" font-size="11" fill="#1f4e79">thin radiating</text>
  <text x="60" y="264" font-size="11" fill="#1f4e79">board ≈ 3.5 mm</text>
  <text x="300" y="450" text-anchor="middle" font-size="11" fill="#5a2d0c">structural belly ≈ 8 mm</text>
  <text x="300" y="40" text-anchor="middle" font-size="10" fill="#444">width 380 mm   ·   depth 345 mm   ·   d/w 0.91</text>
</svg>
```

---

## 11. OpenSCAD generator

```scad
// ======================================================================
//  Clements 49 — limaçon soundbox  (parametric generator)
//
//  OUTER cross-section = limaçon with a:b = 2  -> single FLAT point at
//  theta=180, so the stringbar seats on a flat (not a notch).
//  INNER cross-section = free-form graded wall (board / rib / belly);
//  it owes nothing to a:b and carries the structural job.
//
//  Sections are cut PERPENDICULAR to the raked stringbar and lofted
//  bass -> treble. Units mm, angles degrees.
// ======================================================================

// ---------------------------------------------------------------- FRAME
// (principal axis of the 49 board pins in strings_49.json)
U_AXIS  = [0.523, 0, 0.852];   // stringbar axis, raked 31.6 deg from vertical (x-z plane)
Y_MINOR = [0, 1, 0];           // soundboard WIDTH direction = limacon minor side (y)
N_BOARD = [-0.852, 0, 0.523];  // soundboard normal (x-z). belly = -N_BOARD = [0.852,0,-0.523] (-z, "underneath")

P_BASS   = [-297.4, -2.5,  111.8];   // bass   board pin  (loft start)
P_TREBLE = [ 417.2, -2.5, 1262.8];   // treble board pin  (loft end)

// ----------------------------------------------------------- PARAMETERS
AB        = 2.0;    // a:b for the OUTER. ==2 gives the flat seat.
                    //  >2 = rounder (no flat), <2 = concave dent. KEEP AT 2 for the outer.
NSEC      = 41;     // loft stations bass->treble
MPTS      = 160;    // points per ring (even, >=80)

// --- soundboard half-width profile  (FIRST-CUT teardrop) --------------
//     This is the ONLY thing the soundboard Bezier controls.
//     Replace the body of w_half(s) with your Bezier evaluation, s in [0,1].
HW_BASS   = 190;    // half-width at the bass (mm) -> 380 wide
TEAR_EXP  = 0.6;    // teardrop taper exponent (first cut only)
function w_half(s) = HW_BASS * pow(1 - s, TEAR_EXP);   // <<< BEZIER HOOK >>>

// --- wall thickness  (free-form INNER) --------------------------------
T_BOARD   = 3.5;    // thin radiating board (flanks of the stringbar)
T_BELLY   = 8.0;    // structural belly (closes the box)
T_RIB     = 24.0;   // string-anchor rib peak, at theta=180 (the stringbar line)
RIB_SIG   = 10;     // rib angular half-width (deg) -> narrower = sharper rib

// -------------------------------------------------------------- HELPERS
function vsum(v,i=0,a=0) = i<len(v) ? vsum(v,i+1,a+v[i]) : a;
function lim_Wunit(a,b)  = max([for(t=[0:2:359]) abs((a+b*cos(t))*sin(t))]);

// OUTER ring in section-plane coords [minor, depth]; flat top at depth 0
function outer2d(s) =
  let(a=AB, b=1,
      sc    = (2*w_half(s)) / (2*lim_Wunit(a,b)),  // UNIFORM scale -> stays a true limacon
      lxmin = -(a-b))                              // flat/dimple end of the symmetry axis
  [ for(i=[0:MPTS-1])
      let(t=360*i/MPTS, r=a+b*cos(t))
      [ (r*sin(t))*sc, -((r*cos(t))-lxmin)*sc ] ]; // depth: 0 at flat top -> -D at belly

// wall thickness as a function of ring index (free-form)
function t_of(i) =
  let(t=360*i/MPTS,
      base = (T_BELLY+T_BOARD)/2 + (T_BELLY-T_BOARD)/2*cos(t),  // thin top, thick belly
      rib  = (T_RIB-T_BOARD)*exp(-pow((t-180)/RIB_SIG,2)))      // rib spike at stringbar
  base + rib;

// INNER ring = OUTER offset inward by t_of() along the local inward normal
function inner2d(s) =
  let(o=outer2d(s), m=len(o),
      cx=vsum([for(p=o)p[0]])/m, cy=vsum([for(p=o)p[1]])/m)
  [ for(i=[0:m-1])
      let(p=o[i], pn=o[(i+1)%m], pp=o[(i+m-1)%m],
          tx=pn[0]-pp[0], ty=pn[1]-pp[1], L=norm([tx,ty]),
          nx=ty/L, ny=-tx/L,
          sg=sign((cx-p[0])*nx+(cy-p[1])*ny), tt=t_of(i))
      [ p[0]+nx*sg*tt, p[1]+ny*sg*tt ] ];

// map a section-plane point [minor, depth] to world 3D at station s
function P_at(s)      = P_BASS + s*(P_TREBLE - P_BASS);
function to3d(s,ring) = let(P=P_at(s)) [ for(p=ring) P + p[0]*Y_MINOR + p[1]*N_BOARD ];

// skin a list of equal-length 3D rings into a closed solid
module skin(rings) {
  n=len(rings); m=len(rings[0]);
  pts =[for(r=rings) for(p=r) p];
  side=[for(i=[0:n-2]) for(j=[0:m-1])
          [ i*m+j, i*m+(j+1)%m, (i+1)*m+(j+1)%m, (i+1)*m+j ]];
  cap0=[for(j=[0:m-1]) (m-1-j)];          // first cap (reversed winding)
  cap1=[for(j=[0:m-1]) (n-1)*m+j];        // last cap
  polyhedron(points=pts, faces=concat(side,[cap0],[cap1]), convexity=10);
}

// ---------------------------------------------------------------- BUILD
SS = [for(k=[0:NSEC-1]) k/(NSEC-1)];

module soundbox_limacon() {
  difference() {
    skin([for(s=SS) to3d(s, outer2d(s))]);   // outer solid
    skin([for(s=SS) to3d(s, inner2d(s))]);   // remove the cavity
  }
  // Back sound-holes are NOT cut here; subtract them from the belly face
  // (theta ~ 0 side) after this, sized per the acoustic note (~240 cm^2 total).
}

soundbox_limacon();

// Notes for integration:
//  * Drop this into harp_scaffold.scad in place of the empty
//    `module soundbox_limacon(){}` slot; comment out the trailing
//    assembly calls if you only want to view the box.
//  * I cannot run OpenSCAD in my sandbox, so the polyhedron winding is
//    reasoned, not rendered. If it renders inside-out, swap cap0/cap1 or
//    reverse the side quad order. F6 + a manifold check is the acceptance test.

```

---

## 12. Using it

1. Paste §11 into `harp_scaffold.scad` where the empty `module soundbox_limacon(){}`
   slot is. Comment out the five trailing assembly calls if you just want the box.
2. Tune `AB` (leave at 2), `HW_BASS`/`w_half`, and the `T_*` wall params.
3. `F6`, then run a manifold check. If it renders inside-out, reverse the cap or
   side-quad winding in `skin()`.
4. Subtract the back sound-holes from the belly face.
5. Drop in the soundboard Bézier when it's locked — only `w_half` changes.
