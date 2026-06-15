# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

This is a **physical-instrument design project**, not a conventional software codebase. The goal (`README.md`) is to design **Clements 49** — a 49-string double-action concert pedal harp voiced for church solo hymn playing and jazz, with a resin-infused (VARTM) flax-fabric body, brass parts cast by lost-wax / lost-PLA, starting from a TurboSquid model as base geometry.

The repository currently holds:
- `cad/` — **the parametric OpenSCAD baseline** (the main working deliverable). `cad/README.md` documents it. The string schedule (`cad/strings.scad` / `cad/analysis/string_schedule.json`) is the single source of truth: change the 49-string set there and the neck/board/soundbox/brass geometry follows. `params.scad` holds the wood↔flax material switch, the soundbox acoustic levers, and the load-basis scalars. Render: `openscad cad/assembly.scad` (uses STL only — OpenSCAD 2021.01 can't import OBJ).
- `materials.md` — the substantive design document: load basis (§1), governing physics, material analysis, committed per-component layup decisions. **Read this first** before any structural or materials work.
- `README.md` — project goal and headline spec (49 strings 0G–7A, 96.5 lbs, 75.5″ H × 40.5″ ExW).
- `archive/` — the 8 TurboSquid "Pedal Harp Instrument" `.rar` archives (same model in `3ds/blend/c4d/fbx/mb/obj/scanline_max/vray_max`). **Base geometry, not project-authored.** Extract with `bsdtar -xf <file>.rar` (or `unrar`/`7z`).
- `extract/obj/` — the already-extracted OBJ working copy traced by the CAD baseline (`cad/reference/*.stl` were generated from it). The base model is a standard **47-string** wooden harp; the project extends it to 49 (A0–G7, both extras in the bass — see `cad/README.md`).
- `*:Zone.Identifier` files — Windows download-provenance markers; ignore them.

## Conventions that must be preserved

- **Number provenance tags.** Every quantity is tagged `[model]` (derived from the project structural model / string schedule), `[lit]` (handbook range for the material class), or `[est]` (first-order estimate with stated assumptions). Keep this discipline when adding numbers — never present an estimate as a model output. The `[model]` figures (string schedule, total tension ΣT, string angle, neck peak moment, soundboard span/taper, pillar buckling sizing) come from the project structural model; do not invent or assert structural numbers without it.
- **Measurement-first.** Material property ranges are class-typical and must be confirmed by test on the *actual* fibre/resin before committing a layup (`materials.md` §8). Flag unverified handbook values rather than treating them as decided.
- **Soundboard coordinate frame (UVW)** — used for all layup callouts (`materials.md` §5): **U** = board long axis (bass↔treble, the longitudinal load path); **V** = transverse, in-surface; **W** = through-thickness (ply stacking direction only — no fibres run along W).
- **Core design principle:** carbon hidden inside as structure, flax as the natural skin/shell where it works, tonewood only on the radiating soundboard face. The decision log (`materials.md` §9) records what is closed; respect those closures unless explicitly reopening one.

## String count and the provisional load basis

The project target is **49 strings (0G–7A)**; both `README.md` and `materials.md` now reflect this. `materials.md` was adapted from an earlier 47-string configuration, so its §1 load-basis figures (ΣT, neck peak moment, pillar force, soundboard span/taper) and every `[est]` derived from them are **carried-over working values, not yet recomputed for 49 strings**. They are flagged provisional in §1. When the project structural model is available, regenerate these `[model]` numbers for the 49-string schedule before treating any of them as committed, and update the provisional note accordingly.
