// ============================================================================
// Clements 49 — frame/base.scad
// COMPONENT: the BASE (plinth).
//
// materials.md S6.5: woven-flax / CF monocoque, low mass centre, houses the
// pedal mechanism; CF reinforcement at the pillar-foot and body-foot junctions.
// Footprint from anchors.base_footprint (989 x 533.8 mm, z 0..~140 mm).
//
// flax mode  -> hollow monocoque box: outer shell of wall_base() thickness,
//               with an internal mechanism cavity and 7 pedal slots on the
//               player (-x) face, plus CF junction pads under the pillar foot
//               and the soundbox/body foot.
// wood mode  -> SOLID base box (traditional reference), same outer envelope,
//               still slotted for the 7 pedals.
//
// Module contract:  module base();   (no required args)
//
// Define MODULES ONLY. include params + strings; do NOT redefine their vars.
// Units: millimetres, z-up. Origin = centre of base footprint in x,y; z=0 floor.
//
// CASTING-MOLD HOOK: none generated this run (hard constraint). Every solid
// here is authored as a positive part so a future offset-shell / mold wrapper
// can wrap module base() without edits.
// ============================================================================

include <../params.scad>
include <../strings.scad>

// ----------------------------------------------------------------------------
// Derived base dimensions (single-sourced from params anchors)
// ----------------------------------------------------------------------------
base_w_x   = base_xmax - base_xmin;          // 989.0 mm  span along bass->treble
base_d_y   = base_ymax - base_ymin;          // 533.8 mm  across-body depth
base_h_z   = base_footprint_z;               // ~140 mm   plinth height
base_cx    = (base_xmin + base_xmax) / 2;    // footprint x centre (~0)
base_cy    = (base_ymin + base_ymax) / 2;    // footprint y centre (~0)

base_wall  = wall_base();                    // flax 6 mm / wood 18 mm

// Mechanism cavity: interior void inset from the outer walls by the wall
// thickness, leaving a floor and a top deck for the pedal/action mechanism.
mech_top_deck = max(base_wall, 8.0);         // top deck thickness over the cavity
mech_floor    = max(base_wall, 8.0);         // floor thickness under the cavity

// Pedal slots: 7 openings on the player-side (-y) face for the pedal feet.
n_pedals          = 7;
pedal_slot_w      = 26.0;   // slot width  (along x)
pedal_slot_h      = 34.0;   // slot height (along z), within the cavity band
pedal_slot_zc     = base_h_z * 0.45;   // slot centre height
// Span the 7 slots across the central x-band of the player face.
pedal_band_frac   = 0.62;              // fraction of base width used by the slots
pedal_band_w      = base_w_x * pedal_band_frac;
function pedal_slot_x(i) =
    base_cx - pedal_band_w/2 + pedal_band_w * (i + 0.5) / n_pedals;

// CF junction pads (flax mode): local reinforcement footprints (materials.md
// S6.5). Pillar-foot pad under pillar_bottom_mm; body-foot pad under the
// soundbox bass corner. Authored as positive solids (a future layup/offset
// shell wraps these).
cf_pad_t        = 12.0;                 // pad thickness (sits on the floor)
pillar_pad_d    = 120.0;                // pillar-foot pad diameter
bodyfoot_pad_w  = 220.0;                // body-foot pad width  (x)
bodyfoot_pad_d  = 300.0;                // body-foot pad depth  (y)

// Body foot sits at the bass end of the soundbox: take the bass-most loft
// section x_center projected to the base, clamped into the footprint.
bodyfoot_x = clamp(soundbox_sections[0][2], base_xmin + bodyfoot_pad_w/2,
                                            base_xmax - bodyfoot_pad_w/2);

// ----------------------------------------------------------------------------
// Helper: pedal-slot cutter set (7 slots through the player-side -y wall)
// ----------------------------------------------------------------------------
module pedal_slots_centered() {
    for (i = [0 : n_pedals - 1]) {
        translate([pedal_slot_x(i), base_ymin - 1, pedal_slot_zc])
            translate([-pedal_slot_w/2, 0, -pedal_slot_h/2])
                cube([pedal_slot_w, base_wall + 2, pedal_slot_h]);
    }
}

// ----------------------------------------------------------------------------
// Helper: the mechanism cavity as an interior void (used by flax mode)
// ----------------------------------------------------------------------------
module mech_cavity_void() {
    translate([base_xmin + base_wall,
               base_ymin + base_wall,
               mech_floor])
        cube([base_w_x - 2*base_wall,
              base_d_y - 2*base_wall,
              base_h_z - mech_floor - mech_top_deck]);
}

// ----------------------------------------------------------------------------
// Helper: CF junction reinforcement pads (flax mode only)
// ----------------------------------------------------------------------------
module cf_junction_pads() {
    as_carbon() {
        // pillar-foot pad (round) under the leaning column foot
        translate([pillar_bottom_mm[0], pillar_bottom_mm[1], mech_floor])
            cylinder(h = cf_pad_t, d = pillar_pad_d, $fn = fn_med);
        // body-foot pad (rect) under the soundbox bass corner
        translate([bodyfoot_x, base_cy, mech_floor])
            translate([-bodyfoot_pad_w/2, -bodyfoot_pad_d/2, 0])
                cube([bodyfoot_pad_w, bodyfoot_pad_d, cf_pad_t]);
    }
}

// ----------------------------------------------------------------------------
// MAIN MODULE: base()
// ----------------------------------------------------------------------------
module base() {
    if (is_flax) {
        // --- Hollow monocoque shell with mechanism cavity + pedal slots ---
        as_shell() {
            difference() {
                // outer envelope
                translate([base_xmin, base_ymin, 0])
                    cube([base_w_x, base_d_y, base_h_z]);
                // interior mechanism cavity
                mech_cavity_void();
                // 7 pedal slots through the player-side wall
                pedal_slots_centered();
            }
        }
        // CF reinforcement at the load junctions (positive solids, in cavity)
        cf_junction_pads();
        // future offset-shell / mold hook: wrap module base() externally.
    } else {
        // --- Wood reference: SOLID base box, still slotted for the pedals ---
        as_shell() {
            difference() {
                translate([base_xmin, base_ymin, 0])
                    cube([base_w_x, base_d_y, base_h_z]);
                pedal_slots_centered();
            }
        }
    }
}

// ----------------------------------------------------------------------------
// Echo key derived dimensions (analysis aid)
// ----------------------------------------------------------------------------
echo(str("[base] material=", material,
         "  footprint=", base_w_x, " x ", base_d_y, " mm",
         "  height=", base_h_z, " mm  wall=", base_wall, " mm"));
echo(str("[base] mech-cavity inner = ",
         base_w_x - 2*base_wall, " x ", base_d_y - 2*base_wall, " x ",
         base_h_z - mech_floor - mech_top_deck, " mm",
         "  (floor=", mech_floor, " deck=", mech_top_deck, ")"));
echo(str("[base] pedal slots: ", n_pedals,
         " @ ", pedal_slot_w, "x", pedal_slot_h, " mm, band=", pedal_band_w,
         " mm, x0=", pedal_slot_x(0), " x6=", pedal_slot_x(n_pedals-1)));
echo(str("[base] CF pads (flax only): pillar-foot d=", pillar_pad_d,
         " @ [", pillar_bottom_mm[0], ",", pillar_bottom_mm[1],
         "]  body-foot ", bodyfoot_pad_w, "x", bodyfoot_pad_d,
         " @ x=", bodyfoot_x));

// ----------------------------------------------------------------------------
// Guarded self-preview (only when this file is the top-level rendered file)
// ----------------------------------------------------------------------------
PREVIEW_base = false;   // set true / override to preview standalone
if (PREVIEW_base) base();
