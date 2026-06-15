// ============================================================================
// Clements 49 — frame/soundboard.scad
// THE SOUNDBOARD: spine-and-wings (materials.md S6.1).
//
//   Thin tonewood/skin WINGS over a light core, freed to radiate (S2.3),
//   carried by a CF-UD + woven-flax SPINE along the board long axis (U).
//   Outline length + taper come from the string schedule + spec anchors,
//   extended for the bass strings. String-exit holes run along the centre
//   spine at the schedule positions. Crown (longitudinal camber) and core
//   depth are exposed via params. Wood mode = solid spruce plate.
//
// COORDINATE FRAME (materials.md S5):
//   U = board long axis (bass<->treble), the load path to the end blocks.
//   V = transverse, in the board surface, into the wings (the taper axis).
//   W = through-thickness, normal to the board (ply-stacking direction).
// The board is BUILT in a local UVW frame (U=+x, V=+y, W=+z) with U starting
// at 0, then transformed onto the world board string line (params anchors).
//
// CONTRACT:
//   module soundboard();
//   module soundboard_spine();
//   module soundboard_wing(side);   // side = -1 (one wing) | +1 (other wing)
//
// Material switch is honoured ONLY via params accessors (soundboard_thickness(),
// soundboard_spine_thickness(), shell colour helpers) — this file never
// branches on `material` itself.
//
// NO casting molds / cavities this run (hard constraint). Each module is a
// solid a future offset-shell can wrap. -- mold hook: see comment at EOF.
// ============================================================================

include <../params.scad>
include <../strings.scad>

// ----------------------------------------------------------------------------
// DERIVED BOARD GEOMETRY (single-sourced)
// ----------------------------------------------------------------------------
// U-length: spec board_span_mm (materials.md S1) sizes the original C1..G7
// board; the A0..G7 refit EXTENDS it at the bass so the two added bass eyelets
// (A0,B0, at re-anchored t<0) land on the board instead of off its bass end.
// sb_U_len = spec span scaled by the full A0..G7 t-range; the treble (G7) end
// is unchanged, the bass end grows by the extension. 47->49 stays data-driven.
sb_t0      = string_t_board(0);                       // A0 (negative; bass extension)
sb_t1      = string_t_board(string_count() - 1);      // G7 (= 1.0 at the treble anchor)
sb_U_len   = board_span_mm * (sb_t1 - sb_t0);         // mm, extended bass(0=A0) -> treble(G7)
sb_W_thick = soundboard_thickness();        // total through-thickness (sandwich|solid)
sb_spine_W = soundboard_spine_thickness();  // spine through-thickness
sb_crownR  = board_crown_radius;            // longitudinal crown radius (0 = flat)

// V-width (transverse, the taper) as a function of U-fraction (0=bass .. 1=treble).
// Linear taper bass_width -> treble_width per spec S1; board_taper_coupling can
// later blend in the schedule s_board fan, but a clean linear taper is the
// baseline (coupling kept as a documented hook below).
function sb_width_at(u_frac) =
    lerp(board_width_bass_mm, board_width_treble_mm, clamp(u_frac, 0, 1));

// Spine width: a narrow central strip sized to host the grommet/eyelet bearing
// zone. Constant fraction of the local board width, floored so it never
// vanishes at the treble end where the board is narrowest.
sb_spine_frac = 0.30;                          // [est] spine = ~30% of local width
function sb_spine_width_at(u_frac) =
    max(28.0, sb_width_at(u_frac) * sb_spine_frac);   // mm, floored

// String-exit eyelet bore (where the string passes through the board face).
sb_eyelet_d   = 4.0;   // [est] grommet bore diameter, mm
sb_eyelet_pad = 2.5;   // [est] grommet boss radius beyond the bore, mm

// Local U-position of string i along the board (0..sb_U_len). Uses the
// schedule's normalised board parameter so the eyelet line tracks 47->49.
function sb_string_u(i) = ((string_t_board(i) - sb_t0) / (sb_t1 - sb_t0)) * sb_U_len;

// ----------------------------------------------------------------------------
// LOCAL <-> WORLD PLACEMENT
// ----------------------------------------------------------------------------
// World board string line lies at constant y = board_face_y_mm, tilted in the
// x-z plane. We build in local UVW (U=+x from 0, V=+y centred, W=+z up out of
// the face) then rotate about world Y so local +x aligns with the bass->treble
// chord, and translate the local origin onto the bass endpoint.
_sb_bass    = string_board_pos(0);                    // [x,y,z] world, U=0 (A0, extended bass end)
_sb_treble  = string_board_pos(string_count() - 1);   // [x,y,z] world, U=U_len (G7 treble end)
_sb_dx      = _sb_treble[0] - _sb_bass[0];
_sb_dz      = _sb_treble[2] - _sb_bass[2];
// Tilt of the board long axis from the world +x axis, measured in x-z (about Y).
// rotate([0,-angle,0]) maps local +x -> (cos a, 0, sin a) i.e. up-and-forward.
sb_tilt_deg = atan2(_sb_dz, _sb_dx);

// Wrap children built in local UVW into world placement on the board line.
// W (local +z, board normal) ends up pointing roughly +y-ish-out; we keep the
// board face normal in the local +z and let the tilt rotation place it. Local
// +y (V) maps to world y (across-body) — the board face sits in the world x-z
// plane at y = board_face_y_mm, V fanning into +/-y.
module sb_to_world() {
    translate([_sb_bass[0], board_face_y_mm, _sb_bass[2]])
        rotate([0, -sb_tilt_deg, 0])      // tilt U up the harp
            rotate([90, 0, 0])            // bring local W (+z) to world -y (out of face)
                children();
}

// ----------------------------------------------------------------------------
// CROWN  (longitudinal camber along U)
// ----------------------------------------------------------------------------
// A live soundboard is crowned along its length to act as a shallow shell
// against the ~5500 N perpendicular pull (acoustic board_crown_radius lever).
// We realise the crown by intersecting the flat board solid with a large
// cylinder whose axis is parallel to V (local +y) and offset below the face by
// the crown radius, so the W (thickness) surface bows up by the sagitta.
// crownR <= 0  => flat board (no intersection).
// Longitudinal crown by SLICE-AND-RAISE: cut the board into thin U-strips and
// lift each by the cylindrical-arc rise (0 at the ends, +sagitta at mid-span),
// cambering the board UP in the middle while preserving its full length, content
// (spine/wings/eyelets) and constant thickness. Replaces the old slab∩cylinder,
// which only touched a ~2*sqrt(R*thick) band and clipped the board to a stub.
// rise(u) = sqrt(R^2-(u-U/2)^2) - sqrt(R^2-(U/2)^2).  R<=0 => flat (no-op).
sb_crown_nseg = 28;   // U-strips for the camber (more = smoother, slower)
function sb_crown_rise(u) =
    (sb_crownR <= 0) ? 0 :
    let(R = sb_crownR, a = sb_U_len/2,
        edge = (R > a) ? sqrt(R*R - a*a) : 0)
    ((R*R - pow(u - a, 2)) > 0 ? sqrt(R*R - pow(u - a, 2)) : 0) - edge;

module sb_apply_crown() {
    if (sb_crownR > sb_U_len/2)   // need R > half-length for a real (shallow) arc
        for (k = [0 : sb_crown_nseg - 1]) {
            u0 = k * sb_U_len / sb_crown_nseg;
            u1 = (k + 1) * sb_U_len / sb_crown_nseg;
            um = (u0 + u1) / 2;
            translate([0, 0, sb_crown_rise(um)])
                intersection() {
                    children();
                    translate([u0, -5e3, -5e3]) cube([u1 - u0, 1e4, 1e4]);
                }
        }
    else if (sb_crownR > 0)
        // R too small for the board length: fall back to the old (mild) carve.
        intersection() {
            children();
            // Cylinder axis along local y (V), centre below the face by crownR.
            translate([sb_U_len/2, 0, sb_W_thick - sb_crownR])
                rotate([90, 0, 0])
                    cylinder(h = board_width_bass_mm * 2.2,
                             r = sb_crownR, center = true, $fn = fn_med);
        }
    else
        children();
}

// ----------------------------------------------------------------------------
// OUTLINE  (the tapered board planform in the local UV plane)
// ----------------------------------------------------------------------------
// A trapezoid bass_width -> treble_width over U, extruded to the local board
// solid (full sandwich thickness). Built as a polygon so the wings/spine can
// share the exact same outline. The board is symmetric about the U axis in V.
sb_steps = 24;   // outline sampling along U (modest for fast render)

function _sb_outline_pts() =
    let(n = sb_steps)
    // upper edge (V = +half) bass->treble, then lower edge (V = -half) back.
    concat(
        [ for (k = [0:n]) let(u = k/n) [ u*sb_U_len,  sb_width_at(u)/2 ] ],
        [ for (k = [n:-1:0]) let(u = k/n) [ u*sb_U_len, -sb_width_at(u)/2 ] ]
    );

module sb_planform_solid(thick) {
    linear_extrude(height = thick)
        polygon(points = _sb_outline_pts());
}

// Spine planform: a narrow central strip following the same U taper law.
function _sb_spine_outline_pts() =
    let(n = sb_steps)
    concat(
        [ for (k = [0:n]) let(u = k/n) [ u*sb_U_len,  sb_spine_width_at(u)/2 ] ],
        [ for (k = [n:-1:0]) let(u = k/n) [ u*sb_U_len, -sb_spine_width_at(u)/2 ] ]
    );

module sb_spine_planform_solid(thick) {
    linear_extrude(height = thick)
        polygon(points = _sb_spine_outline_pts());
}

// ----------------------------------------------------------------------------
// STRING-EXIT EYELETS  (along the centre spine, from the schedule)
// ----------------------------------------------------------------------------
// Grommet bosses + through-bores at each string's U-position on the centreline.
// Modelled as POSITIVE bosses (boss solid) and the bore is subtracted from the
// board where called (see soundboard()). Kept separate so a future shell-wrap
// or brass grommet part can reuse the positions.
module sb_eyelet_bores() {
    for (i = indices())
        translate([sb_string_u(i), 0, -1])
            cylinder(h = sb_W_thick + 2, d = sb_eyelet_d, $fn = fn_low);
}
module sb_eyelet_bosses() {
    for (i = indices())
        translate([sb_string_u(i), 0, 0])
            cylinder(h = sb_W_thick, d = sb_eyelet_d + 2*sb_eyelet_pad, $fn = fn_low);
}

// ============================================================================
// CONTRACT MODULES
// ============================================================================

// ----------------------------------------------------------------------------
// soundboard_spine()  — CF-UD + woven-flax load-carrying strip along U.
//   Rendered as carbon (the hidden structural spine, materials.md S7). In wood
//   mode this collapses into the solid plate thickness (no separate spine) but
//   we still emit the strip so the assembly geometry is consistent.
// ----------------------------------------------------------------------------
module soundboard_spine() {
    as_carbon()
        sb_to_world()
            sb_apply_crown()
                difference() {
                    sb_spine_planform_solid(sb_spine_W);
                    sb_eyelet_bores();
                }
}

// ----------------------------------------------------------------------------
// soundboard_wing(side)  — one radiating wing (tonewood skin over light core).
//   side = +1 -> +V wing, side = -1 -> -V wing. Each wing is the board
//   planform on its side of the spine, full sandwich thickness, skinned as
//   tonewood. The narrow spine strip is removed so the wings butt the spine.
// ----------------------------------------------------------------------------
module soundboard_wing(side = 1) {
    s = (side >= 0) ? 1 : -1;
    as_tonewood()
        sb_to_world()
            sb_apply_crown()
                difference() {
                    // Half of the planform on the chosen V side.
                    intersection() {
                        sb_planform_solid(sb_W_thick);
                        translate([sb_U_len/2,
                                   s * (board_width_bass_mm),  // big offset block
                                   sb_W_thick/2])
                            cube([sb_U_len*1.2,
                                  board_width_bass_mm*2,
                                  sb_W_thick*2], center = true);
                    }
                    // Carve out the central spine corridor so wing meets spine.
                    sb_spine_planform_solid(sb_W_thick + 2);
                }
}

// ----------------------------------------------------------------------------
// soundboard()  — full assembly: two wings + spine, eyelets bored, crowned,
//   placed in the world frame. Honors wood<->flax via params accessors.
// ----------------------------------------------------------------------------
module soundboard() {
    soundboard_wing(+1);
    soundboard_wing(-1);
    soundboard_spine();
    // Grommet bosses sit on the spine at the string-exit line (in world frame).
    as_brass()
        sb_to_world()
            sb_apply_crown()
                difference() {
                    sb_eyelet_bosses();
                    sb_eyelet_bores();
                }
}

// -- MOLD HOOK (DO NOT BUILD THIS RUN) ---------------------------------------
// A future casting/layup tool wraps these solids with an offset shell, e.g.
//   minkowski()/offset on sb_planform_solid + sb_spine_planform_solid. Geometry
// WILL move with the 2 added strings, so no cavity is generated here.
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// ECHO key derived dimensions (renders fast; informational).
// ----------------------------------------------------------------------------
echo(str("[soundboard] material=", material,
         "  U_len(span)=", sb_U_len, " mm",
         "  V_taper=", board_width_bass_mm, "->", board_width_treble_mm, " mm"));
echo(str("[soundboard] thickness W=", sb_W_thick, " mm",
         "  spine_W=", sb_spine_W, " mm",
         "  crownR=", sb_crownR, " mm",
         "  tilt=", sb_tilt_deg, " deg"));
echo(str("[soundboard] eyelets=", string_count(),
         "  bass_string_u=", sb_string_u(0),
         "  treble_string_u=", sb_string_u(string_count()-1), " mm",
         "  spine_w(bass/treble)=", sb_spine_width_at(0), "/",
         sb_spine_width_at(1), " mm"));

// ----------------------------------------------------------------------------
// SELF-PREVIEW (guarded): only renders when this file is opened directly.
// ----------------------------------------------------------------------------
sb_preview = true;   // set false when included by the assembly
module _sb_selfpreview() { soundboard(); }
if (sb_preview && $preview) _sb_selfpreview();
