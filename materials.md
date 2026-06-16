# Clements 49 — Materials Analysis & Design

Materials selection and construction design for the Clements 49 — a 49-string (0G–7A) carbon-reinforced flax concert pedal harp. Covers the governing physics, candidate material analysis, and the committed per-component decisions with layup specifications.

**Design priority:** best natural acoustic sound first, structural integrity as a hard constraint, natural/bio-based materials (flax, tonewood) preferred where they do not compromise either.

Numbers are tagged **[model]** (derived from the project structural model / string schedule), **[lit]** (literature/handbook ranges for the material class), or **[est]** (first-order estimate with stated assumptions). Material property ranges are class-typical and **must be confirmed by test on the actual fibre/resin/extraction used before committing to a layup.**

-----

## 1. Load basis

|Quantity                                       |Value                                           |Source |
|-----------------------------------------------|------------------------------------------------|-------|
|String set                                     |49 strings, A0–G7 (0G–7A spec; both added in bass; ~+30% over Erard)|[model]|
|Total string tension ΣT                        |9,269.4 N (2,083.8 lbf)                         |[model]|
|String angle to soundboard (rake off long axis U)|35.3° median (range 21.3–37.9°); 37° design target|[model]|
|Perpendicular pull on board                    |5,305 N measured; ≈ 5,500 N @37° (design value)  |[model]/[est]|
|In-plane longitudinal pull on board            |7,588 N measured                                |[model]|
|Neck peak bending moment (near C4/G4)          |≈ 855 N·m (943 N·m retained as reserve)         |[model]|
|Pillar axial force                             |≈ 9,228 N                                       |[model]|
|Soundboard span                                |1,078 mm (C1–G7); ~1,149 mm extended for A0–G7  |[model]|
|Soundboard width taper (bass→treble)           |380 → 70 mm                                     |[model]|

> **Load basis recomputed for the finalized A0–G7 49-string set on the actual refit 49-pin line** (idx 0..48), replacing the earlier B0–A7 / 47-mesh pass. Both extra strings were added in the **bass** (A0, B0 below C1; treble caps at G7), per the adopted reading of the "0G–7A" spec. Full method, assumptions, and comparison are in `analysis/load_basis_49.md` (reproduce with `analysis/refit_49.py`). The measured 47-string anchor endpoints are re-anchored to C1 (idx 2) and G7 (idx 48); A0,B0 extrapolate below, lengthening the pin line ~35 mm and the board ~81 mm at the bass. Effects of the refit: ΣT rises ~50 N (drop treble A7, add bass A0); the bass strings sit on a steeper rake so the **median rake moves to 35.3°** (nearer the 37° target) and the perpendicular pull rises to **5,305 N** (measured) / 5,578 N @37° — bracketing the **5,500 N conservative board-sizing value** (§2.2, §6.1), which is retained. The neck peak moment rises to **≈855 N·m** (longer bass moment arm); **943 N·m is retained as a conservative reserve** (§6.4). Pillar axial ≈9,228 N confirms the ≈9 kN in §6.3.

-----

## 2. Governing physics

Five principles drive every material decision below.

**2.1 Buckling forgives low modulus; bending punishes it.** A compression column sized against Euler buckling needs diameter `D ∝ E^(−1/4)` — flax’s ~5× lower modulus than carbon costs only ~1.5× the diameter (5^0.25 ≈ 1.5). A beam in bending deflects as `1/(EI)` — *linear* in modulus, so low-E flax deflects far more. Consequence: the **pillar tolerates all-flax**, the **neck does not** and needs a carbon spine.

**2.2 The soundboard has two conflicting jobs.** It must resist ~5,500 N of perpendicular string pull (wants thick/stiff) *and* radiate sound efficiently (wants light/compliant). A uniform solid flax plate sized for the load came out 13.1 mm (solid UD) or 10.0 mm (±45/90 cross-plied) **[model]** — structurally honest but acoustically dead. The conflict is resolved by **(a)** a sandwich core, **(b)** crown, and **(c)** a load-carrying spine, none of which a single solid plate offers.

**2.3 The radiating skin sets the voice; the core supports; the spine carries load.** What the ear reads as “natural” is dominated by the radiating surface. Put the tonewood voice in a thin skin, the stiffness in a light low-damping core, and the string load in a separate spine/bracing so the radiator stays free to move. This is the proven double-top (thin tonewood skins / honeycomb core) and lattice-braced (thin top / carbon lattice) architecture from high-end lutherie.

**2.4 Place damping by intent.** Low-damping materials where you want sound (the board face); high-damping materials where you want silence (the soundbox shell). Flax’s high damping is a liability on the board and an asset on the box.

**2.5 Fibre form decides everything for natural fibres.** Only *continuous, aligned, mechanically-extracted* fibre delivers structural properties. Chopped fibre, wood “fibre” (pulp/flour), and textile “bamboo/cedar fibre” (often regenerated rayon) act as mass-adding, property-reducing filler. To use the sound of a wood (cedar, spruce, bamboo) the material must stay a **continuous strip/lamella/veneer**, never a chopped fibre.

-----

## 3. Acoustic figures of merit

Two numbers rank a soundboard material:

- **Radiation coefficient** `R = √(E/ρ³)` — efficiency of converting string energy to radiated sound. High = loud, responsive.
- **Damping** `tan δ` — low gives sustain/brightness, high gives warmth/fast decay.

|Material (UD, in-fibre)    |E (GPa)|ρ (kg/m³)  |R ≈ √(E/ρ³)|Damping |Role / verdict                                         |
|---------------------------|-------|-----------|-----------|--------|-------------------------------------------------------|
|Spruce (along grain)       |~11    |~400       |~13        |low     |Benchmark radiator; unmatched (stiff + extremely light)|
|Cedar, W. red (along grain)|~8–10  |~350–400   |~12        |low     |Warmer tonewood; very responsive                       |
|Carbon UD                  |130–230|1,550–1,600|~6         |very low|Loud, bright, long sustain, even; “clinical”           |
|Aramid (Kevlar) UD         |70–80  |~1,440     |~5         |high    |Damped + weak in compression + hard to finish — avoid  |
|Bamboo (good fibre)        |~25    |~1,150     |~4         |high    |Slightly better radiator than flax; warm               |
|Flax UD                    |25–30  |~1,400     |~3         |high    |Warm, woody, less efficient; best of the naturals      |
|Glass / basalt UD          |73–90  |2,550–2,700|~2         |moderate|Too dense — dull; structural use only                  |

Values: spruce/cedar/glass/aramid E,ρ **[lit]**; R computed from those **[est]**. Bamboo and flax fibre properties are highly variable by source/extraction — **[lit]**, confirm by test.

**Key takeaway:** no composite fibre matches spruce’s radiation efficiency, because none combines high stiffness with spruce’s 0.4 g/cc lightness. Composites win on stability, durability, and tunability — not raw efficiency. Carbon beats flax for output/sustain but shifts the voice bright/clinical; Kevlar and glass are worse than flax for tone. The way to a genuinely *natural* sound is a **tonewood radiating skin**, not a fibre swap.

-----

## 4. Core materials (sandwich)

A sandwich gets bending stiffness from skin separation (`I ∝ separation²`) at low mass — the dominant lever on the soundboard’s structural-vs-acoustic conflict (§2.2).

|Core                           |ρ (kg/m³)|Shear stiffness  |Damping       |Verdict for radiating board                                           |
|-------------------------------|---------|-----------------|--------------|----------------------------------------------------------------------|
|Nomex honeycomb                |~30–60   |high             |low           |**Best** — lightest, stiffest; the double-top gold standard           |
|End-grain balsa                |~120–220 |high (for weight)|low-ish, woody|**Excellent**, easier to work; woody, lively                          |
|PMI/Rohacell foam              |~50–110  |good             |low-ish       |Stable, predictable; good all-composite option                        |
|PVC/SAN foam (Divinycell/Airex)|~60–200  |moderate         |higher        |OK structurally, less lively                                          |
|Cork                           |~120–240 |low (soft)       |**very high** |**Avoid in the board** — a dedicated damper; use it to *quiet* the box|

Cork is a deliberate damping/isolation material. In a radiating board it kills sustain and output. Its correct home is the soundbox shell, where deadness is wanted.

-----

## 5. Soundboard coordinate frame

Local axes used for all soundboard layup callouts:

- **U** — along the grommet / reinforcing strip; board long axis (bass↔treble); the longitudinal load path to the end blocks. Strings rake off U toward the neck.
- **V** — perpendicular to U, in the board surface; transverse, into the wings.
- **W** — through-thickness, normal to the board. Plies stack along W; **no fibres run along W** (it is only the stacking direction). Add z-reinforcement (stitching/z-pins) only if interlaminar peel appears at joints.

The board surface is the UV plane.

-----

## 6. Component design decisions

Cross-cutting principle: **carbon hidden inside as structure, flax as the natural skin/shell wherever it works, tonewood only on the radiating board face.**

### 6.1 Soundboard — double-top wings + composite spine

**Architecture:** spine-and-wings. A stiff narrow spine carries the string load longitudinally to the end blocks; the wings are freed to be thin radiators.

**Wings (radiator):**

- Thin **spruce** skins (classic harp voice, best projection) — **cedar** as the warmer, more-responsive alternative — over a **Nomex honeycomb** core (**balsa** as the easier near-equal substitute).
- Skin grain / principal stiffness run **across the strip (V)** to couple drive energy outward over the short transverse span and let the wing stay thin.
- Radiator gauge: a few mm total; far below the 13 mm solid-plate floor.

**Spine (grommet strip):**

- **CF-UD along U** — beam fibres carrying the string line to the end blocks.
- **Woven ±45 / 0/90** at the grommet bearing zone — multidirectional bearing and split-resistance at the eyelets (pure UD-U would cleave at the holes).
- Optional CF-UD reinforcement where flax stiffness falls short.

**Transition:** grade (drop/overlap) the UD-U spine plies into the wing UD-V so the stiffness step is a gradient, not a hinge/stress riser.

**Why:** tonewood skin = the natural voice (§3); light low-damping core = stiffness without mass (§4); load in the spine keeps the wings free to radiate (§2.3).

### 6.2 Soundbox (sides + back) — cored woven-flax monocoque

- **Quasi-isotropic woven flax** (0/90 + ±45), doubly-curved monocoque shell.
- Optional **foam or cork core** layer for stiffness + damping.
- **Why:** the box must be rigid, reflective, and dead so energy stays in the board and cavity. Flax’s high damping is an asset here; woven gives balanced shell stiffness with no soft axis to flap; curvature does most of the stiffening. Cork earns its place here as a damping layer — never in the board.
- *Open:* a slightly “live” back can add low end. Default to dead; keep liveness as a later tuning lever rather than over-stiffening on the assumption that rigid is always better.

### 6.3 Pillar — flax tube, UD-axial + woven hoop

- Hollow tube, ~50 mm OD **[est]**, **UD flax along the column axis** (buckling EI), with **woven ±45 / hoop** layers for torsional and local stability.
- **Why:** buckling-governed, and buckling forgives flax’s low modulus (§2.1) — ~1.5× the diameter of an equivalent carbon column. All-flax is viable; the tube is the efficient section. Add CF only if a visually slimmer column is wanted.
- Representative sizing (SF 3, K=1 pinned-pinned, L≈1.5 m, N≈9 kN) **[est]**: solid flax ≈ 47–50 mm OD vs solid CF ≈ 31 mm OD. Real axial force and length come from the project structural model.

### 6.4 Neck — CF spine in a woven-flax super-ellipse

- **CF-UD spine** along the neck length, placed at the bending extreme fibres, inside a **woven-flax super-ellipse (n=4)** section.
- Section: **40 × 58 mm** at the C4/G4 moment peak, tapering to **40 × 33 mm** at the ends **[model]**.
- **Brass ferrules/bushings at every tuning-pin hole** (pin bearing is the critical local failure mode; plate/section thickness alone cannot address it).
- **Why:** stiffness-governed at 943 N·m peak moment (§2.1). Peak bending stress on the section is ≈ 42–50 MPa **[est]** vs flax UD flexural strength ~150–250 MPa **[lit]** — so *strength* has a 3–5× margin, but *deflection* governs: flax alone deflects enough to detune the strings. CF carries the stiffness; woven flax forms the section and surface. This is the one component flax cannot do solo.

### 6.5 Base — woven flax/CF monocoque, mass low

- **Quasi-isotropic woven flax** monocoque, **CF-reinforced** at the pillar-foot and body-foot load junctions, with internal bulkheads. Ballast kept low for stability. Houses the pedal mechanism.
- **Why:** concentrated loads from pillar and body, plus tip stability (the instrument is top-heavy under ~9 kN of string pull), plus mechanism housing. Acoustically irrelevant, so optimise junction strength/stiffness and a low centre of gravity. Mass is welcome here.

-----

## 7. Material & appearance summary

|Component       |Structural fibre                  |Radiating/skin material     |Visible surface        |
|----------------|----------------------------------|----------------------------|-----------------------|
|Soundboard wings|Nomex/balsa core                  |Thin spruce (or cedar) skins|Tonewood (spruce/cedar)|
|Soundboard spine|CF-UD + woven flax                |— (under strings)           |Strip line             |
|Soundbox        |Woven flax (+ core)               |—                           |Natural flax           |
|Pillar          |UD flax + woven flax (CF optional)|—                           |Natural flax           |
|Neck            |CF-UD spine + woven flax          |—                           |Natural flax           |
|Base            |Woven flax + CF at junctions      |—                           |Natural flax           |

The **only** non-flax visible surface is the spruce/cedar board face — a deliberate trade of flax aesthetics for the best natural sound exactly where it matters most. Everything else reads as natural flax, with carbon working out of sight. Spruce/cedar (warm reddish-brown to honey) and natural flax (golden tan) are both warm naturals and coordinate well.

-----

## 8. Open items & required measurements

Closure of the design depends on the following, consistent with the project’s measurement-first discipline:

**Soundboard**

- Real flax flexural strength/modulus on the actual layup (governs the spine and any remaining solid regions).
- Core depth (sandwich) — sets wing stiffness vs mass.
- Crown radius — shell action against the perpendicular pull.
- Rib-to-rail transverse span / bracing layout.
- Tonewood skin thickness for the radiator vs cosmetic-veneer regimes.
- Wood↔composite differential-movement detailing (thin sealed skin, no rigid bond across large stiff areas) to prevent checking/delamination.

**Soundbox**

- Cavity volume, hole size/placement → Helmholtz tuning (the current cavity model is a single-slice placeholder, not a coupled cavity analysis).
- Wall core/thickness for target rigidity.

**Pillar & neck**

- Exact pillar axial force, length, and buckling-sized diameter from the project structural model against the final geometry.
- CF spine sizing in the neck for the deflection (not strength) limit.

**Fibre/material qualification (before any committed layup)**

- Measure E and ρ on the actual flax (and any bamboo) fibre/resin system; natural-fibre properties are too variable to trust handbook values.
- Insert OD / drill diameter sized to the specific ferrule thread and section thickness.

-----

## 9. Decision log (closed in this analysis)

- Soundboard: spine-and-wings; thin spruce/cedar skins over Nomex/balsa core; CF-UD + woven-flax spine; wing fibre across the strip (V), spine fibre along the strip (U).
- Soundbox: cored woven-flax quasi-iso monocoque; cork allowed here as a damping layer.
- Pillar: UD-flax + woven-hoop tube; CF optional for slimness only.
- Neck: CF-UD spine in woven-flax super-ellipse (n=4); brass ferrules at all pins.
- Base: woven-flax/CF monocoque, low mass centre, houses mechanism.
- Rejected: Kevlar (damped, weak in compression, poor finish); glass/basalt (too dense for tone); chopped natural fibre / wood “fibre” (filler, not reinforcement); cork in the radiating board; uniform solid flax soundboard (acoustically dead).