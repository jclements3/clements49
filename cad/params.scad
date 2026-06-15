// ============================================================================
// Clements 49 — params.scad
// Single-source-of-truth PARAMETERS + FUNCTIONS for the parametric baseline.
//
// INCLUDE-ABLE: assignments + functions ONLY. No top-level geometry here.
//   use:     use <params.scad>;   // pulls functions only
//   include: include <params.scad> // pulls variables + functions
// Component files do `include <../params.scad>` then `include <../strings.scad>`.
//
// Units: MILLIMETRES, z-up. Origin = centre of base footprint in x,y; z=0 at
// the floor (base sits on z=0). Bass->treble = increasing +x. Column/player
// side at -x. y is the across-body (depth) axis. Frame matches anchors.json.
//
// Provenance tags in comments: [spec] README/materials.md target;
//   [model] measured from the 47-string source mesh (anchors); [est] estimate.
// Spec targets (materials.md S1) OVERRIDE 47-string model widths where they
// disagree — those are flagged inline.
// ============================================================================

// ----------------------------------------------------------------------------
// 0. RENDER QUALITY
// ----------------------------------------------------------------------------
$fn        = 48;   // default facet count for curved primitives
fn_low     = 16;   // coarse preview (strings, pins)
fn_med     = 48;   // normal parts
fn_high    = 120;  // smooth shells (soundbox, pillar)

// ----------------------------------------------------------------------------
// 1. GLOBAL SCALE / SPEC ENVELOPE
// ----------------------------------------------------------------------------
// Source OBJ scale anchor (height-anchored): 8.8598 mm per source unit.
scale_mm_per_unit = 8.8598;

// Spec overall envelope (README): 75.5 in H x 40.5 in extreme width, 96.5 lb.
spec_height_mm        = 75.5 * 25.4;   // 1917.7 mm   [spec]
spec_extreme_width_mm = 40.5 * 25.4;   // 1028.7 mm   [spec]
spec_mass_lb          = 96.5;          //             [spec]

// ----------------------------------------------------------------------------
// 2. MATERIAL / LAYUP SWITCH  (wood reference  <->  flax-resin structure)
// ----------------------------------------------------------------------------
// Flip this one variable to render the same geometry as the traditional
// WOODEN reference or the committed FLAX-RESIN structure (materials.md S6).
material = "flax";   // "flax"  or  "wood"

is_flax = (material == "flax");
is_wood = (material == "wood");

// --- Per-component WALL / LAYUP thicknesses (mm) ----------------------------
// Flax-resin values from materials.md S6 layup decisions; wood values are the
// equivalent solid-tonewood/ply thicknesses for the reference instrument.
// Each component module reads the matching wall_*() helper so the geometry
// stays identical and only the shell thickness/colour change with `material`.

// 2.1 Soundboard (materials.md S2.2, S6.1)
//   flax: spine-and-wings double-top. wing = skin+core+skin sandwich;
//         spine = CF-UD strip. wood: solid tonewood plate floor.
sb_wing_skin_mm_flax   = 1.6;   // tonewood radiating skin gauge   [spec S6.1 "a few mm total"]
sb_wing_core_mm_flax   = 7.0;   // Nomex/balsa core depth          [est, acoustic core_depth default]
sb_spine_mm_flax       = 9.0;   // CF-UD + woven-flax spine thickness [est]
sb_solid_mm_wood       = 13.1;  // solid-plate structural floor    [model materials.md S2.2]

// 2.2 Soundbox shell (materials.md S6.2) — cored woven-flax monocoque
box_wall_mm_flax       = 4.0;   // woven-flax shell wall (acoustic wall_thickness default) [est]
box_core_mm_flax       = 3.0;   // optional foam/cork damping core layer  [spec S6.2]
box_wall_mm_wood       = 6.0;   // solid wood soundbox shell        [est]

// 2.3 Pillar (materials.md S6.3) — flax tube, UD-axial + woven hoop
pillar_od_mm_flax      = 50.0;  // tube OD                          [spec S6.3 ~50 mm OD]
pillar_wall_mm_flax    = 8.0;   // tube wall thickness              [est]
pillar_od_mm_wood      = 60.0;  // solid-ish wooden column OD       [est]
pillar_wall_mm_wood    = 60.0;  // wood pillar is solid -> wall=OD/2 (solid)

// 2.4 Neck (materials.md S6.4) — CF-UD spine in woven-flax super-ellipse n=4
neck_w_mm              = 40.0;  // section width (both ends + peak)  [spec S6.4]
neck_h_peak_mm         = 58.0;  // section height at C4/G4 moment peak [spec S6.4]
neck_h_end_mm          = 33.0;  // section height at the ends        [spec S6.4]
neck_superellipse_n    = 4;     // super-ellipse exponent            [spec S6.4]
neck_wall_mm_flax      = 5.0;   // woven-flax wall around CF spine   [est]
neck_spine_mm_flax     = 8.0;   // CF-UD spine thickness at extreme fibres [est]

// 2.5 Base (materials.md S6.5) — woven-flax/CF monocoque, low mass centre
base_wall_mm_flax      = 6.0;   // monocoque wall                    [est]
base_wall_mm_wood      = 18.0;  // wooden base box wall              [est]

// --- Layup-aware accessor helpers ------------------------------------------
// Return the active value for the current `material`. Component modules call
// these so they never branch on `material` themselves.
function wall_soundbox()      = is_flax ? box_wall_mm_flax   : box_wall_mm_wood;
function wall_base()          = is_flax ? base_wall_mm_flax  : base_wall_mm_wood;
function pillar_od()          = is_flax ? pillar_od_mm_flax  : pillar_od_mm_wood;
function pillar_wall()        = is_flax ? pillar_wall_mm_flax: pillar_wall_mm_wood;
// Soundboard total structural thickness (sandwich vs solid plate):
function soundboard_thickness() =
    is_flax ? (2*sb_wing_skin_mm_flax + sb_wing_core_mm_flax) : sb_solid_mm_wood;
function soundboard_spine_thickness() = is_flax ? sb_spine_mm_flax : sb_solid_mm_wood;

// ----------------------------------------------------------------------------
// 3. BRASS CASTING SHRINK  (lost-wax / lost-PLA)
// ----------------------------------------------------------------------------
// Brass shrinks ~1.5% on solidification+cooling; a future PATTERN (wax/PLA)
// must be scaled UP by this factor so the cast part lands at nominal size.
// NOTE: per the hard constraint NO molds/cavities are generated this run; this
// is only a hook. Apply only when producing a pattern, never to the as-used
// brass geometry in the assembly.
brass_shrink_pct    = 1.5;
brass_shrink_factor = 1.0 + brass_shrink_pct/100;   // 1.015 -> scale pattern up
function brass_pattern_scale() = brass_shrink_factor;

// ----------------------------------------------------------------------------
// 4. COLOUR HELPERS  (per material, for visual analysis)
// ----------------------------------------------------------------------------
// Warm naturals per materials.md S7: spruce/cedar honey, flax golden tan.
col_flax      = [0.80, 0.66, 0.40];   // golden tan natural flax
col_wood      = [0.74, 0.55, 0.35];   // warm tonewood brown
col_tonewood  = [0.86, 0.70, 0.46];   // spruce/cedar honey radiating skin
col_carbon    = [0.12, 0.12, 0.13];   // hidden CF spine
col_brass     = [0.78, 0.62, 0.24];   // cast brass (pins, discs, plates)
col_cork      = [0.62, 0.48, 0.32];   // cork/foam damping core
col_string_wire   = [0.72, 0.72, 0.76];
col_string_gut    = [0.92, 0.88, 0.74];
col_string_nylon  = [0.90, 0.92, 0.95];

// Active structural-surface colour for the current material.
function shell_color() = is_flax ? col_flax : col_wood;

// Colour for a string given its schedule material tag.
function string_color(mat) =
    (mat == "wire")        ? col_string_wire  :
    (mat == "nylon-high")  ? col_string_nylon :
                             col_string_gut;   // gut-or-nylon-low/-mid

// Convenience colour-wrap modules (optional sugar for component files).
module as_shell()    { color(shell_color())  children(); }
module as_tonewood() { color(col_tonewood)   children(); }
module as_carbon()   { color(col_carbon)     children(); }
module as_brass()    { color(col_brass)      children(); }
module as_cork()     { color(col_cork)       children(); }

// ----------------------------------------------------------------------------
// 5. WORLD-FRAME ANCHORS  (from anchors.json; mm, z-up, base-centred)
// ----------------------------------------------------------------------------
// Base footprint (axis-aligned, harp_base_*/leg_*/metal_plate_*):
base_footprint_x      = 989.0;   // [model]
base_footprint_y      = 533.8;   // [model]
base_footprint_z      = 140.0;   // approx base height z 0..~140  [model]
base_xmin = -494.5; base_xmax = 494.5;   // [model]
base_ymin = -266.9; base_ymax = 266.9;   // [model]

// Pillar (column) axis — leans slightly in x-z; stands on bass/-x side.
pillar_top_mm    = [-303.11, 54.00, 1859.75];  // [model] joins neck bass end
pillar_bottom_mm = [-340.26,  1.56,  155.61];  // [model]
pillar_length_mm = 1705.4;                      // [model]
function pillar_axis_dir() =
    (pillar_top_mm - pillar_bottom_mm) /
    norm(pillar_top_mm - pillar_bottom_mm);

// Soundboard string-exit (board face) line, bass->treble, y~=1.9 (board face).
// Endpoints of the model string-exit line (z 186->1232, x -204->442) [model].
// These measured endpoints are the ORIGINAL 47 strings: C1 (=idx 2) and G7
// (=idx 48). strings.scad re-anchors here and extrapolates idx 0,1 (A0,B0) below.
board_string_line_bass_mm   = [-204.47, 1.88,  186.31];  // [model] C1 (idx 2)
board_string_line_treble_mm = [ 441.70, 1.88, 1232.23];  // [model] G7 (idx 48)
board_face_y_mm             = 1.88;                        // board plane y [model]

// Neck tuning-pin line endpoints, bass->treble (y~=20.84 pin plane) [model].
pin_line_bass_mm   = [-215.67, 20.84, 1802.06];   // [model] C1 (idx 2); A0,B0 extrapolate beyond
pin_line_treble_mm = [ 476.15, 20.84, 1404.38];   // [model] G7 (idx 48)
pin_plane_y_mm     = 20.84;                         // [model]

// ----------------------------------------------------------------------------
// 6. SOUNDBOARD SPEC GEOMETRY  (materials.md S1 OVERRIDES the 47-string model)
// ----------------------------------------------------------------------------
// These are the spec design targets and the single source for board span/taper.
// strings.scad recomputes board span from the schedule's cumulative spacing;
// these defaults are the acoustic-tunable variables (defaults in []).
board_span_mm        = 1078.0;  // [spec S1] base C1..G7 U-length; soundboard.scad extends it ~+71 mm at the bass for A0,B0
board_width_bass_mm  = 380.0;   // [spec S1] V-width at bass end
board_width_treble_mm= 70.0;    // [spec S1] V-width at treble end
string_rake_deg      = 37.0;    // [spec S1] string-to-board angle (design target)

// ----------------------------------------------------------------------------
// 7. STRING SPACING LAW PARAMETERS  (single-sourced; used by strings.scad)
// ----------------------------------------------------------------------------
// Two-locus law (see schedule.spacing_law):
//   NECK (pin line): constant pitch s_neck center-to-center.
//   BOARD (exit line): grows treble->bass per s_board(idx).
s_neck_mm        = 10.0;   // constant pin-line pitch            [spec law]
s_board_treble_mm= 6.5;    // board spacing at treble (idx 48)   [spec law]
s_board_bass_mm  = 24.0;   // board spacing at bass   (idx 0)    [spec law]
s_board_exp      = 0.85;   // grading exponent                   [spec law]
pin_end_margin_mm= 12.0;   // margin past end pins on neck       [est]

// ----------------------------------------------------------------------------
// 8. ACOUSTIC / SOUNDBOX TUNABLE PARAMETERS  (acoustic_baseline.md)
// ----------------------------------------------------------------------------
// Real variables with recommended defaults. soundbox.scad consumes these to
// loft + perfect the new (49-string) soundbox shape and cavity.
cavity_fill_factor    = 0.62;   // [0.55-0.70] cross-section fullness
body_depth_profile    = 1.00;   // [0.85-1.20] x model depth_y
body_width_profile    = 1.00;   // [0.85-1.20] x model width_x
body_length_scale     = 1.00;   // [1.00-1.10] long-axis stretch
bass_corner_bulge     = 1.00;   // [1.00-1.25] local bass-end depth+width boost
back_curvature_radius = 200.0;  // [200..inf]  transverse crown radius (use 0 = flat)
back_liveness         = 0.0;    // [0 dead .. 1 live] back-panel compliance
soundhole_count       = 5;      // [3-6] number of back soundholes
soundhole_scale       = 1.0;    // [0.7-1.4] global hole-area multiplier
soundhole_grade_exp   = 1.0;    // [0.5-1.5] bass->treble hole-size grading
soundhole_axis_offset = 0.5;    // [0.2-0.8] hole column along body length frac
wall_thickness        = 4.0;    // [3-6 mm] flax shell wall (mirrors box_wall_mm_flax)
board_crown_radius    = 8000.0; // longitudinal board crown radius, mm. 0=flat; must exceed the board
                                // half-length (~575mm) for the slice-and-raise camber in soundboard.scad.
                                // ~8000mm => ~21mm camber over the board (≈1.8%); larger = flatter. [est]
core_depth            = 7.0;    // [4-12 mm] sandwich core thickness (mirrors sb_wing_core)
skin_thickness        = 1.6;    // [0.8-2.5 mm] tonewood skin (mirrors sb_wing_skin)
board_taper_coupling  = 1.0;    // [0.0-1.0] couple board taper to schedule spacing

// Seven measured soundbox cross-sections (anchors.soundbox_sections) [model].
// Each: [z_mm, frac, x_center_mm, width_x_mm, depth_y_mm]. soundbox.scad lofts
// these (scaled by the tunables above) to build/perfect the shell + cavity.
soundbox_sections = [
    [ 257.7, 0.10, -34.5, 284.8, 539.1],
    [ 439.7, 0.25,  66.3, 248.4, 464.5],
    [ 621.8, 0.40, 154.9, 224.3, 369.4],
    [ 803.8, 0.55, 257.4, 205.0, 293.6],
    [ 985.9, 0.70, 352.2, 168.2, 238.1],
    [1167.9, 0.85, 467.5, 119.3, 172.9],
    [1289.3, 0.95, 535.6,  77.4, 133.8],
];

// Effective soundbox section after applying tunable multipliers. Returns
// [z, x_center, width_x, depth_y] for section row `i`. bass_corner_bulge is
// applied with weight ~ (1 - frac) so it concentrates at the bass end.
function soundbox_section_eff(i) =
    let(s    = soundbox_sections[i],
        frac = s[1],
        bulge= 1 + (bass_corner_bulge - 1) * (1 - frac))
    [ s[0] * body_length_scale,
      s[2] * body_length_scale,
      s[3] * body_width_profile * bulge,
      s[4] * body_depth_profile * bulge ];

function soundbox_section_count() = len(soundbox_sections);

// ----------------------------------------------------------------------------
// 9. ANALYSIS / LOAD BASIS  (load_basis_49.md; reference scalars for sizing)
// ----------------------------------------------------------------------------
// Refit on the actual A0..G7 49-pin line (cad/analysis/refit_49.py / load_basis_49.md).
load_sigma_T_N        = 9269.4;  // total string tension, A0..G7 [model]
load_perp_pull_N      = 5500.0;  // board perpendicular pull, conservative design value (refit: 5305 @35.3° / 5578 @37°) [est S1]
load_inplane_pull_N   = 7588.0;  // in-plane longitudinal pull, refit tension-weighted [model]
load_neck_moment_Nm   = 943.0;   // neck peak moment, conservative reserve (refit working value ≈855 N·m) [model]
load_pillar_axial_N   = 9227.7;  // pillar axial compression, refit [model]
load_string_angle_deg = 37.0;    // design-target string rake (refit median 35.3°) [spec S1]

// ----------------------------------------------------------------------------
// 10. SMALL UTILITY FUNCTIONS
// ----------------------------------------------------------------------------
function lerp(a, b, t)        = a + (b - a) * t;
function lerp3(a, b, t)       = [lerp(a[0],b[0],t), lerp(a[1],b[1],t), lerp(a[2],b[2],t)];
function deg2rad(d)           = d * PI / 180;
function clamp(x, lo, hi)     = max(lo, min(hi, x));
