// sb_harp_white_wood_02
// Soundboard face "harp_white_wood_02".
// CONSTRUCTION: flat plate -> linear_extrude of the footprint outline.
// Justification (from analysis JSON):
//   obb_dims = [158.73, 56.69, 0.586]  ->  one dimension (0.586) is ~100x
//   smaller than the other two  =>  thin flat plate.
//   The thin axis is OBB axis 2 = principal axis e2 (the local v / thickness
//   direction). The broad face spans OBB axis 0 (=e0, local w, the long axis,
//   sectioned at s) and principal axis e1 (local u, the width).
//   Cross-sections are NOT rectangular: the half-width in u tapers from
//   +/-28.34 at the base down to +/-8.2 at the tip (a fan/wedge), so we
//   build the (u,w) footprint polygon and extrude it by the measured thickness.

module sb_harp_white_wood_02() {
    // ---- principal frame (from JSON: e0, e1, e2 + centroid) ----
    // multmatrix columns = [e1, e2, e0, centroid]; local (x=u, y=v, z=w).
    e0 = [4.474615656687517e-08, 0.5183353942269119,  0.8551774196572486];
    e1 = [0.9999999999999879,   -1.4964715064137968e-07, 3.8379472494624116e-08];
    e2 = [1.4786830315027656e-07, 0.8551774196572364, -0.5183353942269123];
    centroid = [0.44120035460671436, -0.16629279995937019, 64.67363399367734];

    // ---- key dimensions ----
    thickness = 0.5855388569197899;   // obb_dims[2] = plate thickness (v / e2)
    v_mid     = 0.03;                 // mean v offset of the broad face (~0.0..0.06)

    // Footprint outline in the (u, w) plane: [half_width_u, w_position].
    // half_width_u = max |e1-coord| per section; w_position = section s.
    hw = [ [28.343660,  -56.210922],   // base
           [28.343660,  -29.756280],
           [23.927787,   -3.301638],
           [17.721288,   23.153004],
           [14.789847,   49.607646],
           [11.399227,   76.062288],
           [ 8.199973,  102.516930] ]; // tip

    // Build the symmetric footprint: up the +u edge (base->tip), down the -u edge.
    foot_pos = [ for (p = hw) [ p[0], p[1] ] ];                 // x=u, y=w
    foot_neg = [ for (i = [len(hw)-1 : -1 : 0]) [ -hw[i][0], hw[i][1] ] ];
    footprint = concat(foot_pos, foot_neg);

    multmatrix([
        [e1[0], e2[0], e0[0], centroid[0]],
        [e1[1], e2[1], e0[1], centroid[1]],
        [e1[2], e2[2], e0[2], centroid[2]],
        [0,     0,     0,     1]
    ])
    // Extrude the (u,w) footprint by the thickness along local v (y).
    // rotate maps the 2D polygon plane (x=u, y=w) to (x=u, z=w) and the
    // extrude/thickness axis (z) to local y = v.
    translate([0, v_mid, 0])
        rotate([90, 0, 0])
            linear_extrude(height = thickness, center = true)
                polygon(points = footprint);
}

sb_harp_white_wood_02();
