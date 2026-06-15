// ============================================================================
// Clements 49 — frame/pillar.scad
// COMPONENT: the PILLAR / column.
//
// materials.md S6.3: hollow tube, UD-flax along the column axis + woven hoop
// layers; ~50 mm OD class; buckling-governed (buckling forgives flax's low
// modulus, S2.1). All-flax is viable. Wood mode = a solid carved column for
// the traditional reference instrument.
//
// Geometry: a slightly-leaning column on the pillar_bottom_mm -> pillar_top_mm
// axis (anchors), length pillar_length_mm, OD pillar_od(), wall pillar_wall().
// In wood mode pillar_wall() == OD (solid). Colour via as_shell().
//
// Module contract:  module pillar();   (no required args)
//
// CASTING HOOK: NONE generated this run (hard constraint). The pillar is one
// solid module a future offset-shell can wrap; no mold/cavity here.
//
// Include shared single-source params + schedule (do NOT redefine their vars).
// ============================================================================
include <../params.scad>
include <../strings.scad>

// ----------------------------------------------------------------------------
// Internal: place a child built along +z (length L) onto the leaning pillar
// axis, translated to pillar_bottom_mm and rotated so +z -> pillar_axis_dir().
// rotate to align unit +z with the (near-vertical) axis direction.
// ----------------------------------------------------------------------------
module _pillar_place() {
    dir = pillar_axis_dir();              // unit vector bottom->top
    // angle between +z and dir, about the axis perpendicular to both.
    ang = acos(dir[2]);                   // tilt off vertical (deg)
    rot_axis = (norm([dir[1], -dir[0], 0]) < 1e-6)
                 ? [0, 0, 1]              // already vertical: no rotation needed
                 : [dir[1], -dir[0], 0];  // = cross([0,0,1], dir)
    translate(pillar_bottom_mm)
        rotate(a = ang, v = rot_axis)
            children();
}

// ----------------------------------------------------------------------------
// PILLAR — the structural column.
//   flax: hollow UD-flax/woven-hoop tube, OD pillar_od(), wall pillar_wall().
//   wood: solid carved column, OD pillar_od_mm_wood (wall==OD/2 => solid).
// Capped slightly oversize at both ends so it visually seats into the neck
// (top) and base (bottom) joins; future offset-shell / join modules trim.
// ----------------------------------------------------------------------------
module pillar() {
    L    = pillar_length_mm;
    od   = pillar_od();
    wall = pillar_wall();
    id   = max(0, od - 2 * wall);         // bore (0 in wood/solid mode)
    solid = (id <= 0.01);

    as_shell()
    _pillar_place() {
        // Main shaft along +z.
        if (solid) {
            cylinder(h = L, d = od, $fn = fn_high);
        } else {
            difference() {
                cylinder(h = L, d = od, $fn = fn_high);
                // bore: lift off the ends so the tube reads as capped sockets
                // at the neck/base joins (leaves material for those junctions).
                translate([0, 0, od])
                    cylinder(h = L - 2 * od, d = id, $fn = fn_high);
            }
        }
    }

    // --- Echo key derived dimensions -----------------------------------------
    echo(str("[pillar] material=", material,
             "  OD=", od, " mm  wall=", wall, " mm  ID=", id, " mm"));
    echo(str("[pillar] length=", L, " mm  tilt-off-vertical=",
             acos(pillar_axis_dir()[2]), " deg"));
    // Buckling sanity (Euler, K=1 pinned-pinned) is informational only here:
    A_mm2 = solid ? PI/4*od*od : PI/4*(od*od - id*id);
    echo(str("[pillar] section area=", A_mm2, " mm^2   axial load (basis)=",
             load_pillar_axial_N, " N -> mean stress=",
             load_pillar_axial_N / A_mm2, " MPa"));
}

// ----------------------------------------------------------------------------
// Guarded self-preview. Renders the pillar ONLY when this file is the top file.
// An assembly that include<>s this file sets pillar_preview=false (or just
// defines it earlier) to suppress the stray preview geometry.
// ----------------------------------------------------------------------------
pillar_preview = is_undef(pillar_preview) ? true : pillar_preview;
if (pillar_preview) pillar();
