// ============================================================================
// Clements 49 — frame/neck.scad
// The NECK (harmonic curve) that carries the tuning pins.
//
// materials.md S6.4: a CF-UD spine placed at the bending extreme fibres inside
// a woven-flax SUPER-ELLIPSE (n=4) section. Section is 40 x 58 mm at the C4/G4
// moment peak, tapering to 40 x 33 mm at the ends.
//
// SECTION JUSTIFICATION (loads.neck_moment_Nm = 943 N*m conservative reserve;
// A0..G7 refit peak |M| = 855 N*m at x/L ~ 0.46, i.e. near C4/G4):
//   The neck is stiffness-governed, not strength-governed. At ~943 N*m the
//   40 x 58 mm cored section's peak bending stress is ~42-50 MPa [est] vs flax
//   UD flexural strength ~150-250 MPa [lit] (3-5x strength margin), but flax
//   alone deflects enough to detune the strings -> the CF-UD spine carries the
//   stiffness while the woven-flax n=4 super-ellipse forms the section/surface.
//   The 58 mm tall peak sits at the moment maximum (mid-span, near C4/G4) and
//   relaxes to 33 mm at the lightly-loaded ends. Width is held at 40 mm so the
//   tuning-pin line and ferrules have constant bearing depth.
//
// Module contract:
//   module neck();        // harmonic-curve neck shell + pin ferrule holes
//   module neck_spine();  // optional CF-UD spine solid (flax build only)
//
// Single source of truth: the curve and pin seats follow string_pin_pos(i)
// over indices() from strings.scad, so 47->49 propagates automatically.
//
// NO casting molds/cavities this run (hard constraint). neck() and neck_spine()
// are clean solid modules; a future offset-shell can wrap either as a pattern.
// ============================================================================

include <../params.scad>
include <../strings.scad>

// ----------------------------------------------------------------------------
// Local derived geometry
// ----------------------------------------------------------------------------
// Index of the section-height PEAK along the neck. Peak moment sits near C4/G4;
// in the schedule C4 = idx 22, G4 = idx 26 -> centre on idx 24 (E4). We locate
// it as a normalised position along the pin line for a smooth height blend.
neck_peak_idx   = 24;                       // E4, between C4(22) and G4(26)
neck_peak_t     = string_t_neck(neck_peak_idx);   // 0..1 along pin line

// End margin past the first/last pin so ferrules are not at the very tip.
neck_margin_t   = pin_end_margin_mm / max(neck_pin_span_mm(), 1);

// Ferrule (brass bushing bore) geometry — the pin bears in a brass ferrule,
// so the woven-flax/CF section gets a clearance bore for the bushing.
ferrule_bore_d  = 7.0;    // [est] bore through the neck for the brass ferrule
ferrule_depth   = neck_h_peak_mm + 10;   // long enough to punch the full section

// Render facets: modest for speed (super-ellipse polygon resolution).
se_facets       = 32;     // points per super-ellipse outline (smooth enough)
neck_fn         = fn_med;

// ----------------------------------------------------------------------------
// Super-ellipse section profile  |x/a|^n + |y/b|^n = 1   (n = neck_superellipse_n)
// Returns a closed 2D point list (a = half-width, b = half-height).
// ----------------------------------------------------------------------------
function _se_pt(theta, a, b, n) =
    let(c = cos(theta), s = sin(theta))
    [ a * sign(c) * pow(abs(c), 2/n),
      b * sign(s) * pow(abs(s), 2/n) ];

function superellipse_pts(a, b, n, fn) =
    [ for (k = [0 : fn-1]) _se_pt(k * 360 / fn, a, b, n) ];

// Section HEIGHT as a function of normalised position t along the pin line.
// 33 mm at the ends, blending up to 58 mm at the moment peak (neck_peak_t).
// Smooth (cosine) blend on each side of the peak so the sweep has no kink.
function neck_height_at(t) =
    let(tt   = clamp(t, 0, 1),
        // distance from peak, normalised to the longer side so both reach 0..1
        span = max(neck_peak_t, 1 - neck_peak_t),
        d    = abs(tt - neck_peak_t) / max(span, 1e-6),
        // cosine ease: 1 at peak -> 0 at far end
        w    = (1 + cos(clamp(d, 0, 1) * 180)) / 2)
    lerp(neck_h_end_mm, neck_h_peak_mm, w);

// ----------------------------------------------------------------------------
// One oriented section slab at string i.
// A thin extruded super-ellipse, positioned at the pin point and rotated so
// its long axis follows the pin-line tangent (in the x-z plane). The section
// plane is the neck cross-section; thickness `slab` is small so hull() between
// consecutive slabs yields a smooth swept body.
// ----------------------------------------------------------------------------
module _neck_section(i, slab) {
    p  = string_pin_pos(i);
    t  = string_t_neck(i);
    h  = neck_height_at(t);
    // Tangent of the pin line in the x-z plane (for sweep orientation).
    dir = pin_line_treble_mm - pin_line_bass_mm;
    ang = atan2(dir[2], dir[0]);   // angle of pin line in x-z plane (deg)
    translate(p)
        rotate([90, 0, 0])               // bring the section into the x-z plane
        rotate([0, 0, -ang])             // align long axis with the pin tangent
        linear_extrude(height = slab, center = true)
            // super-ellipse: width neck_w_mm (X), height h (Y, becomes world z)
            polygon(superellipse_pts(h/2, neck_w_mm/2,
                                     neck_superellipse_n, se_facets));
}

// ----------------------------------------------------------------------------
// Swept neck SHELL (solid; the woven-flax super-ellipse body).
// Built as the hull of consecutive thin section slabs along the pin curve.
// ----------------------------------------------------------------------------
module _neck_solid() {
    $fn = neck_fn;
    n = string_count();
    slab = 0.6;   // thin section slab thickness; hull bridges the gaps
    for (i = [0 : n-2])
        hull() {
            _neck_section(i,   slab);
            _neck_section(i+1, slab);
        }
    // End caps: small spherical-free closure already covered by end slabs.
}

// ----------------------------------------------------------------------------
// Ferrule bores — one brass-bushing clearance hole at every tuning-pin point.
// The brass ferrule itself is cast (brass.scad); here we only punch the seat.
// ----------------------------------------------------------------------------
module _neck_ferrule_bores() {
    for (i = indices()) {
        p = string_pin_pos(i);
        // Bore runs through the section thickness (world +y, the pin plane axis).
        translate(p)
            rotate([90, 0, 0])
            cylinder(h = ferrule_depth, d = ferrule_bore_d,
                     center = true, $fn = fn_low);
    }
}

// ----------------------------------------------------------------------------
// PUBLIC: neck()  — shell with ferrule bores, coloured per material.
// ----------------------------------------------------------------------------
module neck() {
    as_shell()
        difference() {
            _neck_solid();
            _neck_ferrule_bores();
        }
    // FUTURE-MOLD HOOK: a parametric offset-shell can wrap _neck_solid() to
    // produce a lost-PLA pattern; NOT generated this run (hard constraint).
}

// ----------------------------------------------------------------------------
// PUBLIC: neck_spine()  — CF-UD stiffening spine (flax build only).
// A slimmer super-ellipse core running the full curve, placed concentric with
// the section so it sits at the bending extreme fibres. materials.md S6.4: the
// CF spine carries the stiffness that flax cannot supply solo.
// ----------------------------------------------------------------------------
module neck_spine() {
    if (is_flax) {
        as_carbon()
            // Inset from the outer wall by the woven-flax wall thickness so the
            // spine reads as the hidden core. Width inset both faces.
            intersection() {
                _neck_spine_solid();
                // keep it inside the shell envelope (no ferrule subtraction so
                // the spine remains a continuous load path; pins clear it in
                // the as-built layup).
                _neck_solid();
            }
    }
    // wood build: no separate spine (solid plate behaviour) — nothing emitted.
}

// Spine core: same curve, section shrunk by the woven-flax wall on each side,
// and capped in height to the spine thickness band at the extreme fibres.
module _neck_spine_solid() {
    $fn = neck_fn;
    n   = string_count();
    slab = 0.6;
    w_in = neck_w_mm - 2*neck_wall_mm_flax;     // inner width
    for (i = [0 : n-2])
        hull() {
            _neck_spine_section(i,   slab, w_in);
            _neck_spine_section(i+1, slab, w_in);
        }
}

module _neck_spine_section(i, slab, w_in) {
    p   = string_pin_pos(i);
    t   = string_t_neck(i);
    h   = neck_height_at(t) - 2*neck_wall_mm_flax;   // inner height
    dir = pin_line_treble_mm - pin_line_bass_mm;
    ang = atan2(dir[2], dir[0]);
    translate(p)
        rotate([90, 0, 0])
        rotate([0, 0, -ang])
        linear_extrude(height = slab, center = true)
            // CF-UD spine sits at the extreme top+bottom fibres: model it as
            // two thin bands of thickness neck_spine_mm_flax inset in a slim
            // super-ellipse core. Here render as the full inner super-ellipse
            // (intersected with shell upstream); the load-bearing caps are the
            // top/bottom of this profile where bending stress is highest.
            polygon(superellipse_pts(h/2, w_in/2,
                                     neck_superellipse_n, se_facets));
}

// ----------------------------------------------------------------------------
// Echo key derived dimensions (build-time sanity).
// ----------------------------------------------------------------------------
echo(str("[neck] strings=",            string_count(),
         "  pin_span_mm=",             neck_pin_span_mm(),
         "  section WxH_peak=",        neck_w_mm, "x", neck_h_peak_mm,
         "  H_end=",                   neck_h_end_mm,
         "  superellipse_n=",          neck_superellipse_n));
echo(str("[neck] peak@idx=",           neck_peak_idx,
         " (", string_label(neck_peak_idx), ")",
         "  peak_t=",                  neck_peak_t,
         "  design_moment_Nm=",        load_neck_moment_Nm,
         "  material=",                material,
         is_flax ? str("  wall=", neck_wall_mm_flax,
                       " spine=", neck_spine_mm_flax) : "  (solid wood)"));
echo(str("[neck] pin_line bass=",      pin_line_bass_mm,
         "  treble=",                  pin_line_treble_mm,
         "  ferrule_bore_d=",          ferrule_bore_d));

// ----------------------------------------------------------------------------
// Guarded self-preview (only when this file is opened directly).
// ----------------------------------------------------------------------------
module _neck_preview() {
    neck();
    neck_spine();
}
// Render preview only if this is the top-level file (no caller defined a flag).
if (is_undef($preview_disabled)) _neck_preview();
