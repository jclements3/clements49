# Compact brass worm-drive harp tuner — design concept

Adapts the worm-and-wheel principle of the "Guitar tuners that actually work" design
(noamtsvi, CC-BY-NC — concept only, not their geometry) into a harp-appropriate
**brass** geared tuner that replaces the simple turned pin. Self-locking worm gearing
gives fine, stable tuning that holds string tension.

## Architecture (per string)
- **String post** — Ø4.5 mm brass post with a Ø1.2 mm string hole; the string winds on it
  (replaces the pin). The worm **wheel** is integral with / fixed to the post.
- **Worm wheel** — module 0.4, 10 teeth, pitch Ø4.0 / OD Ø4.8 mm.
- **Worm** — single-start (z1=1), pitch Ø5.0 / OD Ø5.8 mm; **lead angle 4.6°** → self-locking
  (< friction angle, so string tension cannot back-drive it). Ratio **10:1**.
- **Drive** — a **hex socket** (4 mm A/F) on the worm's outboard end; turned with a hex
  driver (no finger knob). Worm axis points OUTWARD (toward the player), where there's room.
- **Brass receiver** — cast brass body **co-moulded into the VARTM flax-resin neck**: placed
  in the mould, flax/resin infuses around it and keys into its anchor holes. Carries the
  string load into the composite and provides the post + worm bearing bores. The tuner
  assembles into the receiver.

## Packaging (the binding constraint: neck pitch)
Footprint **along the neck = 11.4 mm**; outward (toward player) = 14.0 mm (room there).
Adjacent-pin pitch on the neck: treble 11.7, median 18.7, bass ≥30 mm.

| region | pitch | fit |
|---|---|---|
| treble | 11.7 mm | FITS, **+0.3 mm only** — razor-thin, no tolerance margin |
| median | 18.7 mm | fits, +7.3 mm |
| bass   | ≥30 mm | fits, +18.6 mm |

The unit is asymmetric (worm to one side), so the post is **not centred** in its slot;
units must all nest the same handedness.

## Coupled trade-offs
- **Self-locking vs fit:** a low lead angle (self-locking) wants a larger worm; fit wants
  small gears. Reconciled at module 0.4 / worm Ø5.0 / wheel Ø4.8, but the teeth are small.
- **Strength:** worm-wheel torque ≈ string_tension × post_radius ≈ 261 N × 2.25 mm ≈ 587 N·mm
  at the bass. Module-0.4 brass teeth holding 100–261 N need a **tooth-root stress check**
  before finalising. The bass (highest load) has the most room → can use bigger gears there.

## Honest recommendation
Geared tuners are viable across the bass and mid. The **treble is marginal** (0.3 mm). Options:
1. **Two gear sizes** — robust gears on bass/mid, minimum gears on treble.
2. **Plain turned pins on the top ~octave** (lowest tension, easiest to tune) + geared elsewhere.
3. Push module to 0.35 and/or nest receivers front/back along the neck for the treble.

## Status / next
Packaging + gear sizing validated (`tuner_concept.py` → `tuner_concept.svg`,
`tuner_params.json`). NEXT: build the 3D parametric brass parts (receiver, post+wheel,
worm) in build123d, verify the assembly within the envelope, then tooth-stress check.
Tooth geometry in the concept is representational; cuttable involute/worm teeth are a
dedicated step (or sourced gears).
