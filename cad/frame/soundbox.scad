// ============================================================================
// Clements 49 — frame/soundbox.scad
// THE SOUNDBOX / BODY — the acoustic focus (materials.md S6.2).
//
// Cored woven-flax doubly-curved monocoque shell, lofted through the seven
// measured cross-sections (params.soundbox_sections) and extended at the BASS
// end for the added low strings (A0, B0). This is the module that gets iterated to
// perfect the new 49-string shape: every lever in acoustic.tunable_params is a
// real parameter (consumed from params.scad), so re-tuning the box is a matter
// of editing params.scad / passing overrides, not rewriting geometry here.
//
//   include <../params.scad>;  include <../strings.scad>;
//
// Module contract:
//   module soundbox();        // hollow shell (wall wall_soundbox()) + back soundholes
//   module soundbox_cavity(); // inner air volume as a POSITIVE solid (analysis)
//   module soundbox_holes();  // back soundholes as POSITIVE solids (hook)
//
// Frame: mm, z-up, base-centred. Body long axis runs diagonally bass(low z,
// -x) -> treble(high z, +x); sections are perpendicular to z. The soundBOARD
// face sits near y = board_face_y_mm (~+1.9); the box bulges to -y (the back /
// player-far side), so the BACK soundholes are on the -y shell.
//
// NO casting molds / cavities generated here (hard constraint). The whole
// module is a clean hook: a future offset-shell can wrap soundbox() directly.
// ============================================================================

include <../params.scad>;
include <../strings.scad>;

// ----------------------------------------------------------------------------
// 0. DERIVED SECTION GEOMETRY (from the tunable-adjusted control sections)
// ----------------------------------------------------------------------------
// soundbox_section_eff(i) (params.scad) already applies body_width_profile,
// body_depth_profile, body_length_scale and the bass-weighted bass_corner_bulge
// and returns [z, x_center, width_x, depth_y]. We add a BASS EXTENSION station
// below section 0 so the box reaches ~50 mm farther down/over to host B0
// (acoustic_baseline.md: bass corner must reach ~50 mm farther for B0).

// Lowest measured section, projected one step farther toward the bass corner.
// Step taken from the gap between the two lowest measured sections, scaled by
// the bass-extension fraction so the added low string gets cavity + reach.
function _sbx_eff(i) = soundbox_section_eff(i);   // [z, xc, wx, dy]

// Bass cap aligned to the ACTUAL 49-string board bass corner (A0). The A0..G7
// refit extended the board ~81 mm into the bass; the box bass station now tracks
// string_board_pos(0) in z (was a fixed single-string B0 step), so the cavity
// reaches BOTH added low strings (A0,B0). x_center/width/depth extrapolate from
// the two lowest measured sections; bass_corner_bulge (params S8) still grows it.
sbx_bass_margin_mm = 6;     // box bass cap sits this far above the A0 eyelet [est]
function sbx_bass_cap_z() = string_board_pos(0)[2] + sbx_bass_margin_mm;

function sbx_bass_section() =
    let(s0 = _sbx_eff(0), s1 = _sbx_eff(1),
        zc    = sbx_bass_cap_z(),
        denom = (s1[0] - s0[0]),
        tt    = (denom == 0) ? 0 : (zc - s0[0]) / denom,  // <0 => extrapolate toward bass
        xc = s0[1] + (s1[1] - s0[1]) * tt,
        wx = s0[2] + (s1[2] - s0[2]) * tt,
        dy = s0[3] + (s1[3] - s0[3]) * tt)
    [ zc, xc,
      // bass cap stays nearly full (two low strings want cavity), lightly rounded:
      max(120, wx) * 0.95 * bass_corner_bulge_local(),
      max(180, dy) * 0.95 * bass_corner_bulge_local() ];

// Extra local boost applied ONLY to the synthetic bass cap on top of whatever
// soundbox_section_eff already baked in (kept separate so it is explicit).
function bass_corner_bulge_local() = 1.0;

// Treble cap: section list ends at frac 0.95; close it to a small rounded tip.
function sbx_treble_section() =
    let(sN = _sbx_eff(soundbox_section_count() - 1),
        sP = _sbx_eff(soundbox_section_count() - 2),
        dz = (sN[0] - sP[0]) * 0.30,
        dx = (sN[1] - sP[1]) * 0.30)
    [ sN[0] + dz, sN[1] + dx, sN[2] * 0.45, sN[3] * 0.45 ];

// Full ordered station list, bass cap -> measured 0..N-1 -> treble cap.
function sbx_stations() =
    concat( [ sbx_bass_section() ],
            [ for (i = [0 : soundbox_section_count() - 1]) _sbx_eff(i) ],
            [ sbx_treble_section() ] );

function sbx_station_count() = len(sbx_stations());

// ----------------------------------------------------------------------------
// 1. CROSS-SECTION PROFILE  (the cavity_fill_factor / back_curvature lever)
// ----------------------------------------------------------------------------
// A station's outer cross-section is drawn in the local x-y plane centred on
// (x_center, 0). cavity_fill_factor blends between a slim rounded WEDGE (low
// fill) and a FULL ELLIPSE (high fill): we model it as a super-ellipse whose
// exponent maps fill 0.55..0.70 -> n 1.4..2.4 (n=2 is a pure ellipse). This
// directly sets the integrated cavity area -> Helmholtz support per
// acoustic_baseline.md (fill 0.62 default => ~ellipse-ish, V~45 L).
//
// back_curvature_radius adds a transverse crown to the BACK (-y) half: smaller
// radius = more domed/stiffer, 0 (or huge) = flat. We approximate the crown by
// pushing the back semi-axis out by the crown sagitta, leaving the board (+y)
// side governed by the flat soundboard plane.

function _fill_exp() =
    // map cavity_fill_factor in [0.55,0.70] to super-ellipse n in [1.4,2.4]
    let(f = clamp(cavity_fill_factor, 0.50, 0.75))
    1.4 + (f - 0.55) / (0.70 - 0.55) * (2.4 - 1.4);

// The super-ellipse shape fills only part of its (wx x dy) bounding box. We
// want the integrated cavity area to equal cavity_fill_factor of the FULL
// bounding ELLIPSE (pi/4 of the box) to match acoustic_baseline.md's V (~45 L
// at fill 0.62). So we rescale both semi-axes by _area_norm() = sqrt( target /
// natural ), where target = fill*(pi/4)*box and natural = se_box_frac(n)*box.
// se_box_frac(n) = area of the unit super-ellipse / area of its 2x2 box,
// estimated numerically from the same point sampling used to draw it.
function _se_box_frac(n, steps) =
    // shoelace area of the unit super-ellipse (half-axes 1), over box area 4.
    let(pts = [ for (k=[0:steps-1])
                let(t=360*k/steps, ct=cos(t), st=sin(t))
                [ sign(ct)*pow(abs(ct),2/n), sign(st)*pow(abs(st),2/n) ] ],
        m = len(pts),
        a2 = abs( _shoelace(pts, m) ) )
    a2 / 4;
function _shoelace(p, m) =
    _shoelace_acc(p, m, 0, 0);
function _shoelace_acc(p, m, i, acc) =
    (i >= m) ? acc/2 :
    let(j = (i+1)%m)
    _shoelace_acc(p, m, i+1, acc + (p[i][0]*p[j][1] - p[j][0]*p[i][1]));

// Linear rescale on each semi-axis to hit the fill-as-area-fraction target.
function _area_norm(n, steps) =
    let(target = clamp(cavity_fill_factor, 0.40, 0.80) * PI/4,
        natural = _se_box_frac(n, steps))
    (natural > 0) ? sqrt(target / natural) : 1;

// Crown sagitta added to the back depth for a transverse crown radius R over a
// chord = width_x. h = R - sqrt(R^2 - (w/2)^2). R<=0 OR R==inf treated as flat.
function _crown_sag(width_x) =
    (back_curvature_radius <= 0 || back_curvature_radius > 1e5) ? 0 :
    let(R = back_curvature_radius, c = width_x/2)
        (R <= c) ? R : (R - sqrt(R*R - c*c));

// 2D outer profile polygon for a station [z, xc, wx, dy], centred at xc in x.
// Drawn as a super-ellipse of half-axes (wx/2, dy/2 + crown) so that fill and
// crown both modulate the enclosed area. fn controls smoothness.
module sbx_profile_2d(station, fn) {
    wx = station[2];
    dy = station[3];
    xc = station[1];
    n  = _fill_exp();
    crown = _crown_sag(wx);
    steps = max(8, fn);
    norm = _area_norm(n, steps);   // rescale so enclosed area = fill * ellipse
    a  = (wx/2) * norm;            // x semi-axis (area-normalised)
    b  = (dy/2) * norm + crown;    // y semi-axis (depth, +crown on the back)
    pts = [ for (k = [0 : steps-1])
            let(t = 360 * k / steps,
                ct = cos(t), st = sin(t))
            [ xc + a * sign(ct) * pow(abs(ct), 2/n),
                   b * sign(st) * pow(abs(st), 2/n) ] ];
    polygon(pts);
}

// ----------------------------------------------------------------------------
// 2. OUTER SOLID  (lofted body)
// ----------------------------------------------------------------------------
// Loft = chain of hull()s between thin slab extrusions of consecutive station
// profiles, each placed at its station z. This handles the diagonal lean
// (x_center marches +x with z) and the smooth taper without a hand-built
// polyhedron, and renders fast at modest $fn.
SBX_SLAB = 0.6;   // thin slab thickness per station (mm) for hull chaining

module sbx_slab(station, fn) {
    translate([0, 0, station[0] - SBX_SLAB/2])
        linear_extrude(height = SBX_SLAB)
            sbx_profile_2d(station, fn);
}

module sbx_outer_solid(fn) {
    st = sbx_stations();
    n  = len(st);
    for (i = [0 : n - 2])
        hull() {
            sbx_slab(st[i],   fn);
            sbx_slab(st[i+1], fn);
        }
}

// Inner solid = outer scaled inward by the wall thickness. We build it by the
// same loft on INSET profiles (width/depth reduced by 2*wall) rather than a 3D
// offset, so the inner cavity follows the same lofted topology and stays a
// clean watertight-enough positive solid for volume/Helmholtz analysis.
function _inset_station(station, t) =
    [ station[0], station[1],
      max(1, station[2] - 2*t),
      max(1, station[3] - 2*t) ];

module sbx_inner_solid(fn, t) {
    st = sbx_stations();
    n  = len(st);
    for (i = [0 : n - 2])
        hull() {
            sbx_slab(_inset_station(st[i],   t), fn);
            sbx_slab(_inset_station(st[i+1], t), fn);
        }
}

// ----------------------------------------------------------------------------
// 3. BACK SOUNDHOLES  (count / scale / grade / placement levers)
// ----------------------------------------------------------------------------
// Holes are graded OVAL apertures on the BACK (-y) shell, arranged in a column
// along the body long axis. soundhole_axis_offset places the column centre as
// a fraction of body length; soundhole_count sets how many; soundhole_scale
// the global area; soundhole_grade_exp the bass->treble size grading (large at
// the bass per acoustic_baseline.md, 5 graded ovals 120x85..60x44, ~253 cm2).
//
// Returned as POSITIVE solids by soundbox_holes(); soundbox() subtracts them
// from the shell. Per contract the holes are NOT subtracted unless the caller
// opts in — soundbox() opts in by default (a real instrument has the holes),
// but soundbox_holes() alone yields the positive cutters for analysis/overlay.

// Base hole oval semi-axes (board-local mm), bass end, before grading/scale.
sbx_hole_bass_w = 120.0;   // long axis (along body) at bass  [model est]
sbx_hole_bass_h =  85.0;   // short axis (across)     at bass  [model est]
sbx_hole_treble_w = 60.0;  // long axis at treble
sbx_hole_treble_h = 44.0;  // short axis at treble

// z range of the back over which holes are distributed (the body extent).
function sbx_z_min() = sbx_bass_section()[0];
function sbx_z_max() = sbx_treble_section()[0];

// For hole k of N (0=bass .. N-1=treble): a grading fraction g in [0,1].
function _hole_grade(k, N) = (N <= 1) ? 0 : pow(k / (N - 1), soundhole_grade_exp);

// Station interpolation: given a z, find the [xc, wx, dy] by walking stations.
// Simple linear search + lerp between bracketing stations.
function _sbx_lerp_station(z) =
    let(st = sbx_stations(), n = len(st))
    (z <= st[0][0])     ? st[0] :
    (z >= st[n-1][0])   ? st[n-1] :
    _sbx_lerp_walk(st, z, 0);
function _sbx_lerp_walk(st, z, i) =
    (z <= st[i+1][0])
        ? let(t = (z - st[i][0]) / (st[i+1][0] - st[i][0]))
          [ z,
            lerp(st[i][1], st[i+1][1], t),
            lerp(st[i][2], st[i+1][2], t),
            lerp(st[i][3], st[i+1][3], t) ]
        : _sbx_lerp_walk(st, z, i+1);

// One hole cutter: an oval prism punched through the back (-y) shell at the
// station for its z, oriented to pierce the back wall (along -y), sized by
// grade + global scale. Made long enough in y to fully cross the shell.
module sbx_hole(k, N, fn) {
    // distribute hole centres around soundhole_axis_offset along body length.
    span = sbx_z_max() - sbx_z_min();
    centre_z = sbx_z_min() + soundhole_axis_offset * span;
    spread = 0.55 * span;                 // column total length as frac of body
    z = (N <= 1) ? centre_z
                 : centre_z + spread * (k/(N-1) - 0.5);
    g  = _hole_grade(k, N);
    w  = lerp(sbx_hole_bass_w, sbx_hole_treble_w, g) * sqrt(soundhole_scale);
    h  = lerp(sbx_hole_bass_h, sbx_hole_treble_h, g) * sqrt(soundhole_scale);
    st = _sbx_lerp_station(z);
    xc = st[1];
    dy = st[3];
    // Cut the BACK (-y) wall ONLY. Extrude the oval from well outside the back
    // surface (y = -1.6*dy, guaranteed beyond the back even with the crown)
    // INWARD to the body centreline (y = 0): it traverses the back wall and ends
    // inside the cavity, so it never reaches the front (+y) wall -> no second
    // hole. (Was: a centred cutter 2*dy long that punched through BOTH walls.)
    translate([xc, -1.6 * dy, z])
        rotate([-90, 0, 0])              // oval in x-z, extrude +y (inward)
            scale([w/2, h/2, 1])
                cylinder(h = 1.6 * dy, r = 1, $fn = max(16, fn));
}

module soundbox_holes(fn = fn_med) {
    N = max(1, soundhole_count);
    for (k = [0 : N - 1]) sbx_hole(k, N, fn);
}

// ----------------------------------------------------------------------------
// 4. PUBLIC MODULES
// ----------------------------------------------------------------------------
// soundbox(): hollow lofted shell, wall = wall_soundbox(), with back soundholes
// subtracted. Coloured as the active shell material. back_liveness is carried
// as a (visual) wall-thinning of the BACK only — a live back is a thinner /
// more compliant back panel; here it reduces the effective back wall for the
// analysis hook without changing the outer mould line.
module soundbox(fn = fn_med, cut_holes = true) {
    t      = wall_soundbox();
    // live back -> thinner back wall (down to 55% at full liveness). This is a
    // first-order compliance hook; a proper core/skin model lands later.
    t_back = t * (1 - 0.45 * clamp(back_liveness, 0, 1));
    echo(str("[soundbox] material=", material,
             " wall=", t, "mm  back_wall(eff)=", t_back, "mm",
             "  stations=", sbx_station_count(),
             "  z=[", sbx_z_min(), "..", sbx_z_max(), "]mm"));
    echo(str("[soundbox] cavity_fill=", cavity_fill_factor,
             " fill_exp(n)=", _fill_exp(),
             "  back_R=", back_curvature_radius, "mm",
             "  liveness=", back_liveness));
    echo(str("[soundbox] soundholes: count=", soundhole_count,
             " scale=", soundhole_scale, " grade_exp=", soundhole_grade_exp,
             " axis_offset=", soundhole_axis_offset));
    as_shell()
        difference() {
            // shell = outer minus inner. Use the (thinner) back wall by insetting
            // the inner solid by the THINNER of the two so the back wall is the
            // governing (compliance) wall; sides keep full t via outer geometry.
            difference() {
                sbx_outer_solid(fn);
                sbx_inner_solid(fn, t_back);
            }
            if (cut_holes) soundbox_holes(fn);
        }
}

// soundbox_cavity(): the enclosed AIR volume as a POSITIVE solid, for Helmholtz
// / cavity-volume analysis (acoustic_baseline.md V~45 L). This is the inner
// loft (inset by the full wall) WITHOUT holes — a clean positive blob the
// analysis can measure (e.g. via trimesh on an exported STL). NOT a boolean
// against the shell this run, per the soundbox contract.
module soundbox_cavity(fn = fn_med) {
    t = wall_soundbox();
    echo(str("[soundbox_cavity] inset wall=", t,
             "mm  (measure exported volume for V_cavity)"));
    color([0.55, 0.75, 0.95, 0.35])
        sbx_inner_solid(fn, t);
}

// ----------------------------------------------------------------------------
// FUTURE-MOLD HOOK (NOT generated this run, per hard constraint):
//   A casting/lay-up tool would wrap soundbox() as an offset shell, e.g.
//   minkowski()/offset of sbx_outer_solid plus split lines. Left intentionally
//   empty. Geometry will change with the 2 added strings; keep this a hook only.
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// GUARDED SELF-PREVIEW  (renders only when this file is opened directly)
// ----------------------------------------------------------------------------
module _soundbox_selfpreview() {
    soundbox(fn = fn_med);
    // dim cavity ghost for visual sanity:
    %soundbox_cavity(fn = fn_low);
}
// $preview is true in the GUI / when no other file includes this one as a lib.
if ($preview) _soundbox_selfpreview();
