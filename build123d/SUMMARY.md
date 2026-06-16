# Clements 49 — build123d parametric harp: overnight summary

Goal: convert `clements49.blend` into a **parameterized build123d model** so the 2 bass
strings can be added and the acoustic/structural analysis re-run. Status below is split
into **SOLID** (built + independently verified) vs **APPROXIMATE/DESIGNED** (idealized or
a deliberate design choice, not a faithful trace of the mesh).

## How to run
- All build123d runs: `build123d/py <script.py>` (wrapper sets `LD_LIBRARY_PATH` for a
  libexpat fix and uses the venv with build123d 0.10). Plain `python3` won't import it.
- Parts: `build123d/parts/<part>.py` (each exposes `<part>()`). Shared schedule/dims:
  `build123d/clements49_params.py`. Assembly: `assembly.py` → `harp(string_set=49|47)`.
- Plates: `build123d/make_plates.py` → `clements47.svg`, `clements49.svg`.

## SOLID (verified)
- **Env**: build123d imports & runs; `project_to_viewport` HLR works on B-rep solids.
- **All 7 parts build as valid solids** (soundbox, soundboard, pillar, base, pedals,
  strings, neck). Bbox vs the mesh: base 0.1, neck 0.3, soundboard 4.8, pedals 2.4.
- **49 strings** = 47 endpoints **measured from the blend** + 2 bass extrapolated (A0,B0).
  `STRING_SET` toggle verified (47→47 rods, 49→49 rods). **ΣT = 9269.4 N** (from schedule).
- **Cavity volume = 49.7 L** measured from the parametric soundbox solid (~1% vs the mesh).
- **Plates** `clements47.svg` / `clements49.svg`: third-angle HLR (FRONT·SIDE·REAR row +
  TOP aligned above SIDE, column left in both), views-only, sized ~950 px. Render verified.

## APPROXIMATE / DESIGNED (not a faithful mesh trace)
- Surfaces are **idealized parametric solids**, not the mesh surfaces: soundbox = clean
  straight-sided half-cone (wings dropped); soundboard = clean tapered plate; neck = spline
  S-curve slab + box foot (captures the harmonic curve approximately).
- **Pillar** = cylinder (diameter 9.27 = narrowest `harp_pole`, measured) + grooved
  Archimedean/helical spiral — a **design choice you requested**, not the original column.
- **Helmholtz A0 ≈ 70–85 Hz** is **ESTIMATED** — back sound-holes are not modeled yet.
- The plates are HLR of this **parametric reconstruction**, not a projection of the blend's
  own mesh lines (the blend has no curves; build123d HLR segfaults on meshes).

## Open / recommended next (needs your call)
1. **Frame expansion for the 2 bass strings** — biggest remaining item. Today the 49 vs 47
   difference is only the 2 extra string *rods*; the soundboard/neck/soundbox do **not** yet
   lengthen at the bass. Making the frame extent a function of `STRING_SET` would make the
   49 plate structurally different (longer bass corner), which is the real "add 2 strings".
2. **Back sound-holes** — model them to finalize A0/Helmholtz.
3. **Mesh-faithful drawing** (optional) — if you want a plate that *is* the original mesh
   outline, that's a separate pipeline (decimate→sew-to-solid, or the earlier custom HLR).

I paused autonomous work here (a clean, verified, committed milestone) rather than guess at
the frame-expansion, since it's a design decision and you've been steering the details.
