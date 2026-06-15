// ============================================================================
// Clements 49 — strings.scad
// SINGLE SOURCE OF TRUTH for the 49-string schedule + placement laws.
//
// INCLUDE-ABLE: data + functions ONLY, no top-level geometry.
//   Component modules iterate this so 47->49 is ONE data change here.
// Depends on params.scad for the spacing-law constants and world anchors:
//   include <params.scad>;  include <strings.scad>;
//
// Pitch range A0 (idx 0) .. G7 (idx 48), scientific pitch, all-naturals home
// tuning. Per user direction both extra strings are added in the BASS: A0 and
// B0 sit below the source model's C1; treble caps at G7 (no A7). The original
// 47 (C1..G7) map to idx 2..48; idx 0 = A0, idx 1 = B0 are the new bass strings.
//
// Row schema: [idx, note, octave, f0_hz, vib_len_mm, tension_N, material]
// Mirrors analysis/string_schedule.json (sigma_T = 9269.4 N).
// ============================================================================

// ----------------------------------------------------------------------------
// 1. THE SCHEDULE  (49 rows, bass idx 0 -> treble idx 48)
// ----------------------------------------------------------------------------
strings_schedule = [
    [ 0, "A", 0,    27.500,  1455.1,  147.5, "wire"],
    [ 1, "B", 0,    30.868,  1354.5,  153.7, "wire"],
    [ 2, "C", 1,    32.703,  1306.8,  159.7, "wire"],
    [ 3, "D", 1,    36.708,  1216.5,  172.6, "wire"],
    [ 4, "E", 1,    41.203,  1132.4,  185.5, "wire"],
    [ 5, "F", 1,    43.654,  1092.6,  192.0, "wire"],
    [ 6, "G", 1,    48.999,  1017.1,  204.9, "wire"],
    [ 7, "A", 1,    55.000,   946.8,  217.5, "wire"],
    [ 8, "B", 1,    61.735,   881.3,  230.1, "wire"],
    [ 9, "C", 2,    65.406,   850.3,  236.0, "wire"],
    [10, "D", 2,    73.416,   791.5,  241.7, "wire"],
    [11, "E", 2,    82.407,   736.8,  247.5, "wire"],
    [12, "F", 2,    87.307,   710.9,  250.4, "wire"],
    [13, "G", 2,    97.999,   661.8,  256.2, "wire"],
    [14, "A", 2,   110.000,   616.0,  258.2, "gut-or-nylon-low"],
    [15, "B", 2,   123.471,   573.4,  260.2, "gut-or-nylon-low"],
    [16, "C", 3,   130.813,   553.3,  261.3, "gut-or-nylon-low"],
    [17, "D", 3,   146.832,   515.0,  255.5, "gut-or-nylon-low"],
    [18, "E", 3,   164.814,   479.4,  249.6, "gut-or-nylon-low"],
    [19, "F", 3,   174.614,   462.6,  246.7, "gut-or-nylon-low"],
    [20, "G", 3,   195.998,   430.6,  240.8, "gut-or-nylon-low"],
    [21, "A", 3,   220.000,   400.8,  230.6, "gut-or-nylon-low"],
    [22, "B", 3,   246.942,   373.1,  220.4, "gut-or-nylon-low"],
    [23, "C", 4,   261.626,   360.0,  215.3, "gut-or-nylon-mid"],
    [24, "D", 4,   293.665,   335.1,  210.8, "gut-or-nylon-mid"],
    [25, "E", 4,   329.628,   312.0,  206.4, "gut-or-nylon-mid"],
    [26, "F", 4,   349.228,   301.0,  204.2, "gut-or-nylon-mid"],
    [27, "G", 4,   391.995,   280.2,  199.8, "gut-or-nylon-mid"],
    [28, "A", 4,   440.000,   260.8,  193.6, "gut-or-nylon-mid"],
    [29, "B", 4,   493.883,   242.8,  187.5, "gut-or-nylon-mid"],
    [30, "C", 5,   523.251,   234.2,  184.4, "gut-or-nylon-mid"],
    [31, "D", 5,   587.330,   218.1,  178.6, "gut-or-nylon-mid"],
    [32, "E", 5,   659.255,   203.0,  172.7, "gut-or-nylon-mid"],
    [33, "F", 5,   698.456,   195.8,  169.8, "gut-or-nylon-mid"],
    [34, "G", 5,   783.991,   182.3,  163.9, "gut-or-nylon-mid"],
    [35, "A", 5,   880.000,   169.7,  159.8, "gut-or-nylon-mid"],
    [36, "B", 5,   987.767,   158.0,  155.7, "gut-or-nylon-mid"],
    [37, "C", 6,  1046.502,   152.4,  153.7, "nylon-high"],
    [38, "D", 6,  1174.659,   141.9,  149.3, "nylon-high"],
    [39, "E", 6,  1318.510,   132.1,  144.9, "nylon-high"],
    [40, "F", 6,  1396.913,   127.4,  142.7, "nylon-high"],
    [41, "G", 6,  1567.982,   118.6,  138.3, "nylon-high"],
    [42, "A", 6,  1760.000,   110.4,  132.2, "nylon-high"],
    [43, "B", 6,  1975.533,   102.8,  126.0, "nylon-high"],
    [44, "C", 7,  2093.005,    99.2,  123.0, "nylon-high"],
    [45, "D", 7,  2349.318,    92.3,  116.8, "nylon-high"],
    [46, "E", 7,  2637.020,    85.9,  110.7, "nylon-high"],
    [47, "F", 7,  2793.826,    82.9,  108.0, "nylon-high"],
    [48, "G", 7,  3135.963,    77.2,  102.7, "nylon-high"],
];

// ----------------------------------------------------------------------------
// 2. ROW ACCESSORS
// ----------------------------------------------------------------------------
function string_count()      = len(strings_schedule);          // 49
function string_row(i)       = strings_schedule[i];
function string_idx(i)       = strings_schedule[i][0];
function string_note(i)      = strings_schedule[i][1];
function string_octave(i)    = strings_schedule[i][2];
function string_f0(i)        = strings_schedule[i][3];          // Hz
function string_vib_len(i)   = strings_schedule[i][4];          // mm
function string_tension(i)   = strings_schedule[i][5];          // N
function string_material(i)  = strings_schedule[i][6];
function string_label(i)     = str(string_note(i), string_octave(i));  // e.g. "A4"

// Total tension cross-check (should equal params load_sigma_T_N = 9269.4 N).
function total_tension_N() =
    let(n = string_count())
    [for (s = strings_schedule) s[5]] * [for (i=[0:n-1]) 1];   // dot -> sum

// ----------------------------------------------------------------------------
// 3. SPACING LAW
// ----------------------------------------------------------------------------
// 3.1 Board (bridge/exit line) center-to-center spacing for string idx.
//   s_board(idx) = s_treble + (s_bass - s_treble) * ((48 - idx)/48)^exp
function s_board(i) =
    s_board_treble_mm +
    (s_board_bass_mm - s_board_treble_mm) *
    pow((string_count() - 1 - i) / (string_count() - 1), s_board_exp);

// 3.2 Neck (pin line) spacing is constant.
function s_neck() = s_neck_mm;

// 3.3 Cumulative board distance from the bass end (idx 0) to string idx,
//   measured along the board string line as the running sum of half-gaps.
//   Position of string i = sum over gaps between consecutive strings 0..i.
function _board_gap(j) = (s_board(j) + s_board(j-1)) / 2;   // gap between j-1 and j
function board_cum(i) =
    (i <= 0) ? 0
             : board_cum(i-1) + _board_gap(i);

// Total board span occupied by the 49 strings (sum of all gaps).
function board_string_span_mm() = board_cum(string_count() - 1);

// 3.4 Neck pin-line cumulative distance (constant pitch).
function neck_cum(i) = i * s_neck();
function neck_pin_span_mm() = (string_count() - 1) * s_neck();

// ----------------------------------------------------------------------------
// 4. PLACEMENT MAPPING onto the world-frame anchor lines
// ----------------------------------------------------------------------------
// The schedule's cumulative spacing parameterises position ALONG each anchor
// line. We map the [0 .. span] running distance to a normalised t in [0,1]
// then lerp between the measured bass/treble endpoints (params anchors). This
// keeps strings.scad the single source: change count/spacing here and every
// module that calls string_board_pos()/string_pin_pos() follows.

// Re-anchor to the REAL 49-pin line. The measured anchor endpoints in
// params.scad are the ORIGINAL 47 strings: C1 (idx 2) and G7 (idx 48). We pin
// them at t=0 / t=1, so idx 0,1 (A0,B0) extrapolate to t<0 and lengthen the
// neck/board at the bass corner instead of squeezing the 49 into the 47 span.
ORIG_BASS_IDX   = 2;    // C1 -> measured *_bass_mm anchor
ORIG_TREBLE_IDX = 48;   // G7 -> measured *_treble_mm anchor

// Normalised board parameter for string i (0 at C1 anchor, 1 at G7 anchor; <0 in the bass extension).
function string_t_board(i) =
    let(a = board_cum(ORIG_BASS_IDX), b = board_cum(ORIG_TREBLE_IDX))
    (b > a) ? (board_cum(i) - a) / (b - a) : 0;

// Normalised neck parameter for string i (same re-anchoring on the pin line).
function string_t_neck(i) =
    let(a = neck_cum(ORIG_BASS_IDX), b = neck_cum(ORIG_TREBLE_IDX))
    (b > a) ? (neck_cum(i) - a) / (b - a) : 0;

// World-frame point of string i at the SOUNDBOARD exit line (board face).
function string_board_pos(i) =
    lerp3(board_string_line_bass_mm, board_string_line_treble_mm,
          string_t_board(i));

// World-frame point of string i at the NECK tuning-pin line.
function string_pin_pos(i) =
    lerp3(pin_line_bass_mm, pin_line_treble_mm, string_t_neck(i));

// Generic alias requested by the contract: 2D in-plane position helper.
// Returns the [x, z] of string i on the board string line (y is board_face_y).
function string_pos(i) =
    let(p = string_board_pos(i)) [p[0], p[2]];

// String full vector (pin -> board) and its length / rake angle for analysis.
function string_vec(i)      = string_board_pos(i) - string_pin_pos(i);
function string_chord_mm(i) = norm(string_vec(i));
// Rake angle off the board long axis (board bass->treble chord), in degrees.
function board_axis_dir() =
    (board_string_line_treble_mm - board_string_line_bass_mm) /
    norm(board_string_line_treble_mm - board_string_line_bass_mm);
function string_rake_model_deg(i) =
    let(v  = string_vec(i),
        vn = v / norm(v),
        d  = board_axis_dir())
    acos(abs(vn * d));

// ----------------------------------------------------------------------------
// 5. ITERATION HELPERS  (component modules use these)
// ----------------------------------------------------------------------------
// indices() -> [0 : count-1] for `for (i = indices())` loops.
function indices() = [0 : string_count() - 1];

// Classify a string into a coarse register for colour/sizing decisions.
function string_register(i) =
    (string_octave(i) <= 1) ? "bass" :
    (string_octave(i) <= 4) ? "mid"  : "treble";
