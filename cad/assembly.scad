// ============================================================================
// Clements 49 — assembly.scad   (TOP-LEVEL MODEL)
//
// Assembles the whole 49-string double-action concert pedal harp in the shared
// WORLD FRAME (mm, z-up, origin = base footprint centre, z=0 at floor) by
// calling each component module per the module contract.
//
// Single source of truth:
//   params.scad   — all dims/anchors/tunables/colour + the material switch.
//   strings.scad  — the 49-row string schedule + placement laws.
// Both are include<>d here so the assembly can read anchors + iterate the
// schedule directly (for the simple-cylinder string render).
//
// Component files are use<>d (NOT include<>d): use<> imports their modules
// without running their top-level self-preview geometry, so opening this file
// previews the ASSEMBLY only. Each component already include<>s ../params.scad
// and ../strings.scad internally, so its module bodies resolve all dims from
// its own file scope (verified: a use<>d module reads its own file's vars).
//
// MATERIAL DEMO: the master switch lives in params.scad (`material="flax"`).
// Because each component include<>s its OWN copy of params, the canonical way
// to switch the WHOLE instrument wood<->flax is to edit that one line, or to
// drive it from the command line, which propagates into every file:
//     openscad -D 'material="wood"' assembly.scad   // wooden reference
//     openscad -D 'material="flax"' assembly.scad   // committed flax-resin
// (Setting `material` here in assembly scope only affects assembly-local
// colour helpers, not the use<>d component module bodies — by design.)
//
// HARD CONSTRAINT honoured: NO casting molds/cavities. Each component is a
// clean positive module a future offset-shell can wrap. Strings/discs/plates
// scale automatically from the schedule (47->49 is one data edit in strings).
// ============================================================================

// ----- Single source of truth (variables + functions) ----------------------
include <params.scad>
include <strings.scad>

// ----- Component modules (use<> = modules only, no stray self-preview) ------
use <frame/pillar.scad>
use <frame/neck.scad>
use <frame/soundboard.scad>
use <frame/soundbox.scad>
use <frame/base.scad>
use <brass/brass.scad>

// ----------------------------------------------------------------------------
// TOP-LEVEL TOGGLES  (override on the CLI with -D name=true/false)
// ----------------------------------------------------------------------------
show_frame     = true;    // pillar + neck + soundboard + soundbox + base
show_brass     = true;    // pins + discs + action plates + pedals
show_strings   = true;    // simple cylinders from the schedule
show_reference = false;   // faint STL overlay of the 47-string base geometry
show_cavity    = false;   // soundbox inner air volume (analysis aid)
brass_parts    = "all";   // "all"|"pins"|"discs"|"plates"|"pedals"

// Reference overlay: OpenSCAD import() supports STL only (not OBJ). This is the
// frame-only export of the wooden 47-string TurboSquid base, already placed in
// the same world frame, used to eyeball that the parametric model tracks it.
reference_stl  = "reference/frame_only.stl";
reference_alpha = 0.18;   // faint ghost

// String render sizing (simple cylinders; purely visual / placement check).
string_r_bass   = 1.6;    // mm radius at bass end (idx 0)
string_r_treble = 0.45;   // mm radius at treble end (idx 48)

// ----------------------------------------------------------------------------
// STRINGS  — simple cylinders straight from the schedule
// ----------------------------------------------------------------------------
// One cylinder per string from its tuning-pin point (neck) to its board-exit
// point (soundboard), coloured by the schedule material tag and radius-graded
// bass->treble. This is the visual placement/clearance check; the structural
// string load lives in params.load_* / strings.total_tension_N().
module strings_simple() {
    for (i = indices()) {
        p_pin   = string_pin_pos(i);     // world 3D at neck pin line
        p_board = string_board_pos(i);   // world 3D at board exit line
        t       = i / (string_count() - 1);
        r       = lerp(string_r_bass, string_r_treble, t);
        color(string_color(string_material(i)))
            _seg(p_pin, p_board, r);
    }
}

// Draw a capsule-ish cylinder between two world points a and b of radius r.
module _seg(a, b, r) {
    v   = b - a;
    L   = norm(v);
    if (L > 1e-6) {
        dir = v / L;
        // rotation taking +z onto dir
        ax  = cross([0, 0, 1], dir);
        ang = acos(clamp(dir[2], -1, 1));
        translate(a)
            // guard the degenerate (already-vertical) case
            if (norm(ax) < 1e-9)
                cylinder(h = L, r = r, $fn = fn_low);
            else
                rotate(a = ang, v = ax)
                    cylinder(h = L, r = r, $fn = fn_low);
    }
}

// ----------------------------------------------------------------------------
// FRAME  — structural shell components in the world frame
// ----------------------------------------------------------------------------
// All component modules are authored in the world frame already (they place
// themselves on the shared anchors from params), so no transforms here. Each
// contract module is called exactly once: soundboard() already renders its own
// spine+wings internally, and neck()/neck_spine() are distinct solids (spine
// only exists in the flax build), so there is no duplicate-geometry z-fight.
module frame_world() {
    pillar();        // leaning tube/column, pillar_bottom_mm -> pillar_top_mm
    neck();          // harmonic-curve neck on the pin line
    if (is_flax) neck_spine();        // CF-UD spine — flax build only
    soundboard();    // spine-and-wings on the board exit line
    soundbox();      // the lofted body shell — the shape to perfect
    base();          // monocoque plinth
}

// ----------------------------------------------------------------------------
// BRASS  — count-driven action hardware
// ----------------------------------------------------------------------------
module brass_world() {
    brass(brass_parts);   // pins + discs + plates + pedals, all from schedule
}

// ----------------------------------------------------------------------------
// REFERENCE OVERLAY  (STL only)
// ----------------------------------------------------------------------------
module reference_ghost() {
    color([0.5, 0.55, 0.62, reference_alpha])
        import(reference_stl, convexity = 8);
}

// ----------------------------------------------------------------------------
// ASSEMBLE
// ----------------------------------------------------------------------------
if (show_frame)     frame_world();
if (show_brass)     brass_world();
if (show_strings)   strings_simple();
if (show_cavity)    color([0.40, 0.70, 0.95, 0.25]) soundbox_cavity();
if (show_reference) reference_ghost();

// ----------------------------------------------------------------------------
// ECHO  — assembly-level sanity check (single-source-of-truth verification)
// ----------------------------------------------------------------------------
echo("=== Clements 49 assembly ===");
echo(material            = material);
echo(strings             = string_count());
echo(total_tension_N     = total_tension_N(),
     load_sigma_T_N       = load_sigma_T_N);
echo(neck_pin_span_mm     = neck_pin_span_mm(),
     board_string_span_mm = board_string_span_mm());
echo(spec_height_mm       = spec_height_mm,
     spec_extreme_width_mm = spec_extreme_width_mm);
echo(toggles = str("frame=", show_frame, " brass=", show_brass,
                   " strings=", show_strings, " reference=", show_reference,
                   " cavity=", show_cavity));
