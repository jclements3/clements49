// ============================================================================
// Clements 49 — brass/brass.scad
// BRASS PARTS scaffolding (lost-wax / lost-PLA casting), parametric &
// count-driven so 47->49 propagates straight from the string schedule.
//
// MODULES ONLY (no top-level geometry except an optional guarded self-preview).
//   include <../params.scad>   // variables + functions (scale, colours, shrink)
//   include <../strings.scad>  // the 49-row schedule + placement laws
// Do NOT redefine any params/strings variables here.
//
// Contract (see cad/MODULE_CONTRACT.md):
//   module tuning_pins();
//   module sharping_discs();
//   module action_plates();
//   module pedals();
//   module brass(parts = "all");   // "pins"|"discs"|"plates"|"pedals"|"all"
//
// Count law: one pin + one fork-disc PAIR per string at string_pin_pos(i) over
//   indices(); double action => 2 discs/string => 2*string_count() = 98 discs.
//   7 pedals at the base (one per diatonic class C D E F G A B).
//
// Material switch: brass parts are brass in BOTH reference (wood) and flax
//   builds (real harps use brass action regardless of body material). We do NOT
//   branch geometry on `material`; we only honour the shared as_brass() colour
//   and the cork bushing colour helper from params.scad. Brass colour/feel is
//   constant; only seat/ferrule context changes with the body, handled by the
//   frame modules, not here.
//
// CASTING NOTE: render at NOMINAL (as-used) size. brass_pattern_scale() (=1.015,
//   the 1.5% lost-wax/lost-PLA shrink oversize) is a FUTURE opt-in pattern step
//   and is NEVER applied to the as-used geometry in the assembly. Each module
//   below is a clean solid that a future casting-pattern / mold-cavity step can
//   wrap (scale(brass_pattern_scale()) the pattern, then offset-shell for the
//   mold). NO molds / sprue / gating / cavities are generated in this run.
//
// Units: millimetres, z-up, base-centred frame (matches params/anchors).
// ============================================================================

include <../params.scad>
include <../strings.scad>

// ----------------------------------------------------------------------------
// 0. BRASS PART DIMENSIONS  (local, parametric; [est] unless tagged)
// ----------------------------------------------------------------------------
// Tuning pin (square-drive tapered pin in a brass ferrule). Modelled as a
// stepped cylinder: shank into the neck + a head/collar + a square wrest drive.
pin_shank_d_mm     = 6.0;    // pin shank diameter (into neck ferrule)   [est]
pin_shank_len_mm   = 22.0;   // length buried in the neck                [est]
pin_collar_d_mm    = 9.0;    // bearing collar at the neck face          [est]
pin_collar_h_mm    = 3.0;    // collar height                            [est]
pin_head_d_mm      = 5.0;    // square wrest-drive head across-flats      [est]
pin_head_h_mm      = 14.0;   // wrest-drive head height (proud of face)  [est]

// Fork / sharping disc (double-action). A thin brass disc with two pins
// (the "fork") that grip & shorten the string by a semitone when rotated.
disc_d_mm          = 17.0;   // disc outer diameter                       [est]
disc_t_mm          = 2.2;    // disc plate thickness                      [est]
disc_hub_d_mm      = 5.0;    // central rotation hub diameter             [est]
disc_hub_h_mm      = 4.0;    // hub height (off the neck face)            [est]
fork_pin_d_mm      = 1.8;    // the two fork pins that pinch the string   [est]
fork_pin_h_mm      = 4.0;    // fork pin height proud of disc face        [est]
fork_pin_radius_mm = 4.0;    // fork-pin pitch radius from disc centre    [est]
disc_pair_gap_mm   = 26.0;   // along-string spacing between the 2 discs  [est]
                             // (upper disc = full sharp, lower = nat/half)
disc_standoff_mm   = 6.0;    // disc face standoff off the neck pin plane [est]

// Action plate (brass cover/bedplate the disc spindles ride in). Modelled as
// a thin strip lying along the pin line, segmented like the source asset's
// gold_box groups. Count is derived from string_count() (see action_plates()).
plate_w_mm         = 24.0;   // across-neck width of the plate strip      [est]
plate_t_mm         = 2.5;    // plate thickness                           [est]
plate_seg_overlap_mm = 2.0;  // segment overlap so the strip reads solid  [est]
action_plate_count = ceil(string_count() / 1.6);  // ~31 for 49 (matches
                             // source harp_gold_box_01..31 segment density) [model]

// Pedal (one per diatonic class). Foot plate + stem + pivot lug at the base.
pedal_count        = 7;      // C D E F G A B — fixed by diatonic system   [spec]
pedal_plate_l_mm   = 70.0;   // foot-plate length                          [est]
pedal_plate_w_mm   = 22.0;   // foot-plate width                           [est]
pedal_plate_t_mm   = 6.0;    // foot-plate thickness                       [est]
pedal_stem_d_mm    = 8.0;    // stem rod diameter                          [est]
pedal_stem_h_mm    = 40.0;   // exposed stem height                        [est]
pedal_pitch_mm     = 34.0;   // center-to-center spacing in the base       [est]
pedal_base_z_mm    = 60.0;   // z height of the pedal row in the base      [est]

// Facets: keep modest so the full brass set (49 pins + 98 discs + plates +
// 7 pedals) renders fast.
brass_fn      = fn_low;       // 16: round brass primitives
brass_fn_disc = fn_med;       // 48: discs read smooth at viewing scale

// ----------------------------------------------------------------------------
// 1. PLACEMENT HELPERS  (orient a part to sit on the neck pin line)
// ----------------------------------------------------------------------------
// The neck pin line runs bass(-x,high-z) -> treble(+x,low-z) in the x-z plane
// at y = pin_plane_y_mm. We approximate the per-pin local frame by the chord
// direction of the pin line (good enough for the baseline; the neck module
// owns the true harmonic-curve normal). Returns the in-plane tilt in degrees
// of the pin line about the y axis (so parts can lie normal to the neck face).
function pin_line_dir() =
    (pin_line_treble_mm - pin_line_bass_mm) /
    norm(pin_line_treble_mm - pin_line_bass_mm);
// Tilt of the pin line in the x-z plane, measured from +x toward +z (deg).
function pin_line_tilt_deg() =
    let(d = pin_line_dir()) atan2(d[2], d[0]);

// Place children at string i's pin, with the part's +z pointing OUT of the
// neck face (i.e. along +y, the across-body normal of the pin plane). We point
// parts along +y so pins/discs stand proud of the neck face toward the player.
module at_pin(i) {
    p = string_pin_pos(i);
    translate(p)
        rotate([-90, 0, 0])   // local +z -> world +y (out of the neck face)
            children();
}

// ----------------------------------------------------------------------------
// 2. TUNING PINS  — one per string  (count = string_count())
// ----------------------------------------------------------------------------
// Future casting-pattern hook: a pattern step would scale(brass_pattern_scale())
// THIS solid before shelling a mold cavity. Not done here (NO molds this run).
module tuning_pin() {
    as_brass() {
        // shank (buried in the neck ferrule, points -z = into the face)
        translate([0, 0, -pin_shank_len_mm])
            cylinder(h = pin_shank_len_mm, d = pin_shank_d_mm, $fn = brass_fn);
        // bearing collar at the face
        cylinder(h = pin_collar_h_mm, d = pin_collar_d_mm, $fn = brass_fn);
        // square wrest-drive head, proud of the face
        translate([0, 0, pin_collar_h_mm])
            linear_extrude(height = pin_head_h_mm)
                square(pin_head_d_mm, center = true);
    }
}

module tuning_pins() {
    for (i = indices())
        at_pin(i) tuning_pin();
}

// ----------------------------------------------------------------------------
// 3. FORK / SHARPING DISCS  — double action, 2 discs per string
// ----------------------------------------------------------------------------
// fork_disc(): one rotating brass disc with its two fork pins + hub.
module fork_disc() {
    as_brass() {
        // disc plate
        cylinder(h = disc_t_mm, d = disc_d_mm, $fn = brass_fn_disc);
        // rotation hub
        translate([0, 0, disc_t_mm])
            cylinder(h = disc_hub_h_mm, d = disc_hub_d_mm, $fn = brass_fn);
        // the two fork pins that pinch the string (the "fork")
        for (a = [90, 270])
            translate([fork_pin_radius_mm * cos(a),
                       fork_pin_radius_mm * sin(a),
                       disc_t_mm])
                cylinder(h = fork_pin_h_mm, d = fork_pin_d_mm, $fn = brass_fn);
    }
}

// action_discs(): place the double-action PAIR (2 discs) per string near the
// neck pin, offset along the local string run. 2 * string_count() discs total.
module action_discs() {
    for (i = indices())
        at_pin(i) {
            // both discs stand off the neck face (+z local = +y world here)
            translate([0, 0, disc_standoff_mm]) {
                // upper disc (full sharp)
                translate([0, +disc_pair_gap_mm/2, 0]) fork_disc();
                // lower disc (natural / half stop)
                translate([0, -disc_pair_gap_mm/2, 0]) fork_disc();
            }
        }
}

// Contract alias: sharping_discs() == the placed double-action disc field.
module sharping_discs() { action_discs(); }

// ----------------------------------------------------------------------------
// 4. ACTION PLATES  — brass bedplate strip segments along the pin line
// ----------------------------------------------------------------------------
// action_plate(): a single segment of the action bedplate strip.
module action_plate(seg_len) {
    as_brass()
        translate([-(seg_len/2), -(plate_w_mm/2), 0])
            cube([seg_len + plate_seg_overlap_mm, plate_w_mm, plate_t_mm]);
}

// action_plates(): lay action_plate_count segments end-to-end along the pin
// line chord, centred on it, sitting just behind the disc field. Segment count
// (and thus length) is count-driven so 47->49 lengthens the strip.
module action_plates() {
    span    = norm(pin_line_treble_mm - pin_line_bass_mm);
    seg_len = span / action_plate_count;
    base    = pin_line_bass_mm;
    dir     = pin_line_dir();
    for (k = [0 : action_plate_count - 1]) {
        // segment centre parameter along the chord
        t   = (k + 0.5) * seg_len;
        pos = base + dir * t;
        translate(pos)
            rotate([-90, 0, 0])                 // plate lies in the neck face
                rotate([0, 0, pin_line_tilt_deg()])
                    // tuck the plate behind the disc standoff
                    translate([0, 0, -plate_t_mm])
                        action_plate(seg_len);
    }
}

// ----------------------------------------------------------------------------
// 5. PEDALS  — 7 brass foot pedals at the base
// ----------------------------------------------------------------------------
// pedal(): one foot plate + stem. (Pivot lug / mechanism interior is left as a
// clean hook for the base module — no mechanism this run.)
module pedal() {
    as_brass() {
        // foot plate (lies flat, long axis = x)
        translate([-pedal_plate_l_mm/2, -pedal_plate_w_mm/2, 0])
            cube([pedal_plate_l_mm, pedal_plate_w_mm, pedal_plate_t_mm]);
        // stem rising into the base column
        translate([0, 0, pedal_plate_t_mm])
            cylinder(h = pedal_stem_h_mm, d = pedal_stem_d_mm, $fn = brass_fn);
    }
}

// pedals(): place pedal_count pedals in a row across the base footprint, at the
// pedal row z height, centred in x, near the back face (player side, +/- y).
module pedals() {
    row_w = (pedal_count - 1) * pedal_pitch_mm;
    for (k = [0 : pedal_count - 1])
        translate([ -row_w/2 + k * pedal_pitch_mm,
                    base_ymax - pedal_plate_w_mm,   // near the back face
                    pedal_base_z_mm ])
            pedal();
}

// ----------------------------------------------------------------------------
// 6. AGGREGATE  — brass(parts) selector
// ----------------------------------------------------------------------------
module brass(parts = "all") {
    if (parts == "pins"   || parts == "all") tuning_pins();
    if (parts == "discs"  || parts == "all") sharping_discs();
    if (parts == "plates" || parts == "all") action_plates();
    if (parts == "pedals" || parts == "all") pedals();
}

// ----------------------------------------------------------------------------
// 7. DERIVED-DIMENSION ECHO  (sanity at parse/render)
// ----------------------------------------------------------------------------
echo(str("[brass] strings              = ", string_count()));
echo(str("[brass] tuning pins          = ", string_count()));
echo(str("[brass] sharping discs (2/s) = ", 2 * string_count()));
echo(str("[brass] action-plate segs    = ", action_plate_count));
echo(str("[brass] pedals               = ", pedal_count));
echo(str("[brass] pin-line span (mm)   = ",
         norm(pin_line_treble_mm - pin_line_bass_mm)));
echo(str("[brass] pin-line tilt (deg)  = ", pin_line_tilt_deg()));
echo(str("[brass] casting shrink scale = ", brass_pattern_scale(),
         " (FUTURE pattern only; as-used geometry is nominal)"));

// ----------------------------------------------------------------------------
// 8. GUARDED SELF-PREVIEW  (only when this file is the top-level model)
// ----------------------------------------------------------------------------
// Renders the full brass set standalone for visual check. Harmless when this
// file is included by an assembly (assemblies define their own top geometry).
brass_self_preview = true;
if (brass_self_preview) brass("all");
