// ============================================================================
// soundbox.scad  --  Harp SOUNDBOX assembly (reverse-engineered parametric model)
// ============================================================================
//
// PIPELINE: This is the SOUNDBOX pass of a reusable reverse-engineering pipeline
//   (Blender clements49.blend -> per-part analysis JSON -> per-part OpenSCAD
//    module -> this assembly). Other subsystems (strings, neck, base, ...) are
//   handled in separate passes and are NOT included here.
//
// UNITS: model units (NOT mm). All geometry is kept in the original Blender
//   world coordinates so the rebuilt soundbox sits exactly where the original
//   model did; no re-centering or rescaling is applied.
//
// COORDINATE CONVENTION (matches the source model):
//   Z = up            (model spans z 0 .. 216.5)
//   X = front(-) / back(+)
//   Y = left / right  (about +/- 36)
//   Overall model bbox: x[-62.6,62.6] y[-36.1,36.1] z[0,216.5]
//
// SOUNDBOX union bbox (5 parts; harp_wood_inside1 excluded as neck-region):
//   min [-30.07, -35.38, 15.293]   max [30.694, 60.301, 152.295]   dims ~[60.76, 95.68, 137.0]
//
// NOTE ON include vs use:
//   Each sb_*.scad part file ends with a top-level self-call (so the part can be
//   rendered standalone for verification). We therefore use<> the part files
//   here instead of include<>: use<> imports the module DEFINITIONS only and
//   suppresses those top-level calls, so the assembly below controls exactly
//   what is rendered (no accidental double-render). Each module already places
//   its geometry at the original world coords via its own multmatrix, so the
//   assembly simply calls them with no extra transform.
// ============================================================================

// ---- part modules (definitions only; top-level self-calls suppressed) ----
use <parts/sb_harp_big_side_pivot.scad>   // body shell  (loft / hull)
use <parts/sb_harp_white_wood_01.scad>    // soundboard face 1 (flat plate)
use <parts/sb_harp_white_wood_02.scad>    // soundboard face 2 (flat plate)
use <parts/sb_harp_wood_plank.scad>       // plank        (flat bar)
use <parts/sb_harp_wood_inside.scad>      // inner lining (flat plate)
// harp_wood_inside1 REMOVED: it sits at z 174.6-189.8, ABOVE the soundboard top
// (151.9) -> it is a NECK-region piece, not soundbox. To be handled in the neck pass.

// ============================================================================
// KEY DIMENSION VARIABLES  (model units; informational / drive previews)
// ============================================================================

// --- expected soundbox envelope (union of the 6 part AABBs) ---
sb_bbox_min    = [-30.07, -35.38,  15.293];
sb_bbox_max    = [ 30.694, 60.301, 152.295];   // (harp_wood_inside1 excluded -> neck)
sb_dims        = [ sb_bbox_max[0]-sb_bbox_min[0],
                   sb_bbox_max[1]-sb_bbox_min[1],
                   sb_bbox_max[2]-sb_bbox_min[2] ];   // ~[60.76, 95.68, 174.47]
sb_center      = [ (sb_bbox_min[0]+sb_bbox_max[0])/2,
                   (sb_bbox_min[1]+sb_bbox_max[1])/2,
                   (sb_bbox_min[2]+sb_bbox_max[2])/2 ]; // ~[0.312, 12.46, 102.53]

// --- principal member dimensions (from analysis OBBs) ---
body_obb_dims        = [164.95, 60.76, 25.93];  // harp_big_side_pivot (tapered box shell)
soundboard1_obb_dims = [158.73, 58.26,  0.59];  // harp_white_wood_01  (flat face)
soundboard2_obb_dims = [158.73, 56.69,  0.59];  // harp_white_wood_02  (flat face)
plank_obb_dims       = [157.99,  2.60,  0.71];  // harp_wood_plank     (flat bar)
inside_obb_dims      = [ 42.12, 27.29,  0.65];  // harp_wood_inside    (flat plate)
// inside1 (harp_wood_inside1) excluded -> neck-region piece (z 174.6-189.8)

// --- render quality ---
$fn = 48;

// ============================================================================
// ASSEMBLY  --  all 5 soundbox members at original world coords
// ============================================================================
module soundbox() {
    // body shell -- the bulk of the soundbox (tapered/curved box, hull loft)
    sb_harp_big_side_pivot();

    // soundboard faces (the two flat front plates)
    sb_harp_white_wood_01();
    sb_harp_white_wood_02();

    // central plank running the length of the box
    sb_harp_wood_plank();

    // inner lining (bass-bottom plate)
    sb_harp_wood_inside();
}

soundbox();
