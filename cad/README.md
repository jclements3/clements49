# Clements 49 — Parametric OpenSCAD Baseline

Parametric OpenSCAD model of the Clements 49, a 49-string double-action concert
pedal harp (flax/CF structure, brass action). This baseline exists to support
**structural and acoustic analysis** — above all, **perfecting the new soundbox
shape** — and is driven by a single-source-of-truth **string schedule** so that
the 47→49 string change propagates automatically through neck length/curve,
string spacing, soundboard length/taper, and disc/action counts.

Built for **OpenSCAD 2021.01**, authored in **millimetres**, world frame z-up,
origin at the base footprint centre, z=0 at the floor.

> `import()` in OpenSCAD 2021.01 supports **STL only**, not OBJ. The wooden
> 47-string TurboSquid base was therefore parsed to anchors (`analysis/`) and
> separately exported to STL (`reference/`) for a ghost overlay.

-----

## Directory layout

```
cad/
├── README.md              ← this file
├── MODULE_CONTRACT.md     ← per-module signatures every component honours
├── params.scad            ← all dims / anchors / tunables / colour + MATERIAL SWITCH
├── strings.scad           ← THE STRING SCHEDULE (single source of truth) + placement laws
├── assembly.scad          ← TOP-LEVEL model; assembles every component; toggles
├── frame/
│   ├── pillar.scad        ← module pillar()                    (flax tube / wood column)
│   ├── neck.scad          ← module neck(), neck_spine()        (woven-flax + CF spine)
│   ├── soundboard.scad    ← module soundboard(), _spine(), _wing(side)  (spine + wings)
│   ├── soundbox.scad      ← module soundbox(), soundbox_cavity(), soundbox_holes()
│   └── base.scad          ← module base() (+ pedal slots, mech cavity, CF junction pads)
├── brass/
│   └── brass.scad         ← tuning_pins(), sharping_discs(), action_plates(), pedals(), brass()
├── analysis/
│   ├── string_schedule.json   ← 49-row schedule (canonical machine source)
│   ├── string_schedule.csv    ← same, spreadsheet form
│   ├── anchors.json           ← geometry anchors from the base mesh (mm, z-up)
│   ├── raw_anchors.json       ← raw centroids before scaling/cleanup
│   ├── parse_obj.py           ← OBJ → anchors extraction
│   ├── finalize.py            ← schedule/anchor finalization
│   ├── load_basis_49.md       ← recomputed 49-string structural load basis
│   └── acoustic_baseline.md   ← cavity volume / Helmholtz / soundbox acoustic targets
└── reference/
    ├── export_stl.py          ← OpenSCAD-import helper (OBJ→STL via trimesh/blender)
    ├── whole_harp.stl         ← 47-string wooden base, full
    └── frame_only.stl         ← 47-string wooden base, frame only (ghost overlay)
```

`params.scad` and `strings.scad` are **include-only** files (data + functions,
no top-level geometry). Every component file `include`s both, so each resolves
all of its dimensions from the same source. `assembly.scad` `use<>`s the
component files (modules only, no stray self-preview) and `include`s the two
data files.

-----

## The string schedule is the single source of truth

`strings.scad` (data mirrored in `analysis/string_schedule.json` /
`.csv`) is the **one place** the instrument's string set is defined: 49 rows,
idx 0..48, each with note, octave, `f0_hz`, `vib_len_mm`, `tension_N`, and
material class (wire / gut-or-nylon-low / -mid / nylon-high).

Everything geometric is derived from it through functions, never hard-coded:

- **`string_count()` / `indices()`** — drive every per-string loop.
- **`string_pin_pos(i)`** — tuning-pin point on the neck pin-line → neck curve
  length and the count of tuning pins, ferrule seats, and sharping discs.
- **`string_t_board(i)` / board span** — the soundboard eyelet positions and
  the `board_span_mm` length.
- **Spacing law** (parametric, see below) — neck pin-line length and the
  soundboard span + bass→treble width taper.

### How 47 → 49 propagates

Changing the schedule from 47 to 49 rows is a **single data edit** in
`strings.scad`. From there:

- **Neck** — `neck()` hulls section slabs between every `string_pin_pos(i)`, so
  two extra pins lengthen the pin-line (~+20 mm) and the harmonic curve grows
  automatically; ferrule seats are punched at every pin.
- **String spacing** — two-locus spacing law (parametric):
  - **Neck (pin line):** essentially constant pitch `s_neck ≈ 10.0 mm`
    center-to-center, so 49 pins span (49−1)·10.0 = 480 mm of pin line.
  - **Soundboard (eyelet line):** spacing *grows treble→bass*,
    `s_board(idx) = s_treble + (s_bass − s_treble)·((48−idx)/48)^0.85`, with
    `s_treble = 6.5 mm`, `s_bass = 24.0 mm`. Its cumulative sum sets the board
    span (~1078 mm) and drives the 380→70 mm bass→treble width taper.
  - All four knobs (`s_neck`, `s_treble`, `s_bass`, exponent) are parameters.
- **Soundboard** — `board_span_mm` and the eyelet line follow the schedule;
  `board_taper_coupling` ties the bass-wing growth to the spacing law.
- **Soundbox** — adds a synthetic bass-extension station below section 0 so the
  bass corner reaches ~50 mm farther to host the new bass string (B0).
- **Brass** — `tuning_pins()`=49, `action_discs()`=2·49=98, `pedals()`=7 (fixed
  by the diatonic-class system), action-plate segments `ceil(49/1.6)=31`.

### Resolving the "0G–7A" / 49-string spec naming

The spec calls for **49 strings labeled "0G–7A"**. The standard concert pedal
harp is **47 strings = C1..G7** (oct1 C1–B1 = 7; oct2–6 = 5×7 = 35; oct7 C7–G7
= 5; total 47). A strictly contiguous diatonic run does **not** cleanly give
"G..A" endpoints at exactly 49 from a single literal reading, so the spec is read
as octave-block extremes (bottom block "0", top block "7") rather than literal
end-string letters, and the conflict is stated rather than papered over.

**Adopted resolution (per project direction):** keep the standard 47-string
C1..G7 core and add **both** extra strings in the **bass** — **A0** and **B0**,
the two diatonic steps below C1. Treble caps at **G7** (no A7). Final range =
**A0 .. G7 = 49 strings** (idx 0 = A0, idx 48 = G7). Every string is a natural;
the double-action pedals raise each diatonic class 0/1/2 semitones, so the
schedule is the all-natural reference set, A4 = 440 Hz, equal temperament.

**Justification.** *Acoustic:* a two-string bass extension (A0 ≈ 27.5 Hz, B0 ≈
30.9 Hz) puts the most added fundamental weight exactly where the church/hymn
solo voice works hardest — the bottom octave — and grows the bass corner of the
soundbox/board where the extra cavity and radiating area are wanted. *Structural:*
both strings at the bass end extend the neck pin line (~+35 mm) and board (~+81 mm)
at one corner; the load basis is recomputed on this real geometry (see below).

**Mapping to the base model:** idx 0 (A0) and idx 1 (B0) are NEW groups inserted
below `harp_string_00`; idx 2..48 map to `harp_string_00..46` (the original
C1..G7). The measured 47-string anchor endpoints are re-anchored to C1 (idx 2)
and G7 (idx 48); A0,B0 extrapolate below the bass end (`strings.scad`
`ORIG_BASS_IDX`/`ORIG_TREBLE_IDX`). Disc/action and tuning-pin counts increase
from 47 to 49 (two new fork/discs + pins at the bass end).

-----

## Material switch: wood ↔ flax

The master switch is **one line** in `params.scad`: `material = "flax"`. It
selects the committed flax-resin structure (materials.md §6) or the wooden
47-string reference. Components **never branch on `material` directly** — they
read only the params accessors (`wall_soundbox()`, `soundboard_thickness()`,
`pillar_od()/pillar_wall()`, `wall_base()`, colour helpers `as_shell()`,
`as_carbon()`, `as_tonewood()`, `as_brass()`), so the switch drives thickness,
section, hidden CF spine presence, and colour uniformly.

Because each component `include`s its own copy of `params.scad` (an include is a
variable import; the last file-scope assignment wins), the canonical way to flip
the **whole** instrument is to edit that one line **or** drive it from the CLI:

```
openscad -D 'material="flax"' cad/assembly.scad   # committed flax-resin (default)
openscad -D 'material="wood"' cad/assembly.scad   # wooden 47-string-style reference
```

Representative differences the switch produces: pillar 50 mm OD / 8 mm wall hollow
flax tube vs 60 mm solid wood column; soundboard 10.2 mm flax sandwich
(2×1.6 skin + 7.0 core) vs 13.1 mm solid plate; base 6 mm flax monocoque vs 18 mm
solid wood; the CF spine in `neck`/`soundboard` is emitted only in flax mode.
**Brass action parts stay brass in both builds** (real harps use brass action
regardless), so brass geometry does not branch on `material`.

-----

## Soundbox tunables — perfecting the new shape

The soundbox is the analysis focus. All knobs live in `params.scad` (acoustic
group) and feed `frame/soundbox.scad`; the cross-section is a super-ellipse whose
exponent comes from `cavity_fill_factor` and whose semi-axes are area-normalised
so integrated cavity area = `cavity_fill_factor` × bounding-ellipse area.
`soundbox_cavity()` returns the inner air volume as a positive solid for
Helmholtz / volume analysis. At default `cavity_fill_factor = 0.62` the cavity
measures ~45.6 L (acoustic_baseline.md target ~45.4 L, band 40–51 L).

| Tunable | Effect | Range (default) |
|---|---|---|
| `cavity_fill_factor` | wedge↔full-ellipse cross-section → cavity volume / Helmholtz pitch | 0.55–0.70 (0.62) |
| `body_depth_profile` | per-station depth multiplier; deeper = more volume, lower f_H, warmer | 0.85–1.20× |
| `body_width_profile` | per-station across-string width; widens bass corner | 0.85–1.20× |
| `body_length_scale` | stretch of the bass→treble long axis (tracks schedule span) | 1.00–1.10 |
| `bass_corner_bulge` | extra depth+width at the lowest sections for the B0 extension | 1.00–1.25 |
| `back_curvature_radius` | transverse crown radius of the back shell | 200 mm → flat (∞) |
| `back_liveness` | back-panel compliance dead↔live (thins back skin) | 0 (dead) – 1 (live) |
| `soundhole_count` | number of back soundholes → total area S, f_H, Q | 3–6 (5) |
| `soundhole_scale` | global hole-area multiplier → Helmholtz pitch / damping | 0.7–1.4× |
| `soundhole_grade_exp` | bass→treble hole-size grading exponent | 0.5–1.5 |
| `soundhole_axis_offset` | hole-column placement along back centreline | 0.2–0.8 of length |
| `wall_thickness` | flax shell wall (Helmholtz L_eff, shell stiffness/mass) | 3–6 mm |

Coupled board knobs (`board_span`, `board_width_bass/treble`, `board_crown_radius`,
`core_depth`, `skin_thickness`, `board_taper_coupling`) also live in the same
group; `board_span` and the taper are single-sourced from the schedule.

-----

## Rendering

```
# Preview / render the whole instrument:
openscad cad/assembly.scad

# Headless STL render:
openscad -o /tmp/clements49.stl cad/assembly.scad
```

Top-level toggles in `assembly.scad` (override on the CLI with `-D name=true/false`):

| Toggle | Default | Shows |
|---|---|---|
| `show_frame` | true | pillar + neck + soundboard + soundbox + base |
| `show_brass` | true | tuning pins + sharping discs + action plates + pedals |
| `show_strings` | true | simple cylinders straight from the schedule |
| `show_reference` | false | faint STL ghost of the 47-string wooden base |
| `show_cavity` | false | soundbox inner air volume (analysis aid) |

Example: render just the soundbox cavity for volume study —
`openscad -D show_frame=false -D show_brass=false -D show_strings=false -D show_cavity=true cad/assembly.scad`.

Each component file also has a `$preview`-guarded self-preview, so opening it
alone in the GUI shows that part, while headless `-o` export of the bare file
emits nothing (by design — see verify notes below).

-----

## MOLDS DEFERRED

**No casting molds or mold cavities are generated in this baseline, by hard
directive.** The two added strings will move geometry (neck curve, board
span/taper, soundbox bass corner), so any mold authored now would be obsolete
the moment the schedule or soundbox tunables move. **Analysis and the parametric
baseline come first; molds come only after the geometry is frozen.**

What is in place instead are clean **hooks**, so adding molds later is additive,
not a rewrite:

- Every structural part is authored as a **single positive module** that a future
  offset-shell can wrap (`pillar()`, `neck()/neck_spine()`,
  `soundboard()/_spine()/_wing()`, `soundbox()/soundbox_cavity()`, `base()`).
  Each file carries a comment marking where a casting-pattern / mold-cavity
  offset-shell would attach.
- `soundbox_cavity()` already returns the inner volume as a positive solid —
  the natural seed for a future core/cavity tool.
- Brass: `brass_pattern_scale()` (= 1.015, the 1.5 % shrink oversize) is defined
  and referenced **only in comments/echo** as a future opt-in pattern step; it is
  never applied to as-used geometry. No sprue, gating, or cavities exist.

When the geometry is frozen, mold work wraps these modules — it does not modify
them.

-----

## Verify results (honest)

OpenSCAD 2021.01. Each file was parse/eval-checked (`-o …csg`) and, where it
produces geometry, render-checked to STL.

| File | Parse/eval | Render | Notes |
|---|---|---|---|
| `params.scad` | PASS (exit 0, no errors) | n/a | Include-only (params + functions, no top-level geometry). STL export reports "Current top level object is empty" and exits non-zero — **expected and acceptable** for an include-only file. No ERROR. |
| `strings.scad` | PASS (exit 0, no errors) | n/a | Include-only (schedule data + functions). Empty-top-level on export, as designed. No ERROR. No code changes. |
| `frame/pillar.scad` | PASS | PASS | Renders in flax (default) and wood (`-D material="wood"`). |
| `frame/neck.scad` | PASS | PASS | Hull sweep renders to a valid non-empty STL (~86 KB). |
| `frame/soundboard.scad` | PASS (exit 0; 3 info ECHOes: material=flax, U_len=1078 mm, eyelets=49) | PASS | Bare-file headless export emits nothing — top-level geometry is guarded by `if (sb_preview && $preview)`; `$preview` is false under `-o`. A wrapper calling `soundboard();` renders a manifold solid (222 facets, 438 verts, 2 volumes, ~10 s, 46 KB). Guard is the idiomatic include-by-assembly pattern; not changed. |
| `frame/soundbox.scad` | PASS (exit 0; ECHO diagnostics only) | **`render_ok=false` for the bare file, BY DESIGN** | Top-level geometry is guarded at line 336 by `if ($preview) _soundbox_selfpreview();`; `$preview` is false under `-o`, so bare-file export yields an empty top level (~47 KB stub, no real geometry, exit 1). This is a library meant to be `use<>`d by the assembly, like `params`/`strings`. **The geometry itself is valid:** via the assembly / a direct call, `soundbox()` renders a watertight solid (2408 facets), wood override renders, and `soundbox_cavity()` measures **45.6 L** (target 45.4 L). No ERROR; no syntax fix applied (changing the guard would be a redesign, not a low-risk fix). |
| `frame/base.scad` | PASS (exit 0; ECHO diagnostics) | PASS | Module-definition file; top-level call guarded by `PREVIEW_base = false`. With `-D material="wood" -D PREVIEW_base=true` renders a valid manifold (41 facets, 2 volumes). |
| `brass/brass.scad` | PASS | PASS | Full STL render completes, no errors/warnings (~7.8 MB mesh; 49 pins, 98 discs, 31 plate segs, 7 pedals). |
| `assembly.scad` | PASS | PASS | Top-level model assembles cleanly. |

**Summary:** all nine files parse/eval with exit 0 and **no ERROR output**.
Every geometry-producing module renders to a valid manifold STL when invoked
(directly or via the assembly). The only `render_ok=false` is `soundbox.scad`'s
*bare-file* headless export, which is the intended `$preview`-guarded
empty-top-level condition for a library file — not a defect. No syntax errors
were found and no code was changed during verification.

### Known follow-ups (carried in the analysis, not yet applied)

- The neck curve currently lerps a straight chord between the measured 47-string
  pin-line endpoints rather than threading the full curved tuning-pin polyline;
  refitting the harmonic arc to the regenerated 49-pin polyline needs
  `strings.scad` to expose intermediate curve control points (out of scope here).
- `pin_line_bass/treble_mm` in `params.scad` are still the **47-string** anchor
  values; disc/plate counts already scale to 49, but the pin-line endpoints
  should be re-derived once the neck refits for +1 bass / +1 treble (~+20 mm).
- Part dimensions for brass (pin/disc/plate/pedal sizes) are `[est]` placeholders
  flagged inline.
- Per `analysis/load_basis_49.md`, the structural load basis should be re-run on
  the regenerated 49-pin line once the neck/board geometry is refit.
