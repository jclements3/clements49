// sb_harp_white_wood_01 — soundboard face (flat tapered plate)
//
// Construction choice: FLAT PLATE -> linear_extrude(thickness) of a 2D outline.
// Justification (from analysis JSON):
//   obb_dims = [158.728, 58.260, 0.586]. The third OBB extent (0.586) is ~270x
//   smaller than the other two -> a thin flat plate lying in the e0-e1 plane with
//   its thickness along e2. Every cross-section outline has an e2 spread of only
//   ~0.02-0.06 confirming the slab is essentially planar.
//   The outline is symmetric in e1 and tapers monotonically in width from 58.26
//   (at e0=-56.2) down to 16.86 (at e0=+102.5) -> a tapered trapezoid-ish plate.
//   So: build the tapered outline in the (e0,e1) plane and extrude it by the
//   measured thickness along e2. Placed at original world coords via multmatrix.

module sb_harp_white_wood_01() {
    // --- key dimensions (model world units), from JSON ---
    thickness = 0.5855474371629796;            // obb_dims[2], slab thickness (along e2)
    e2_mid    = (-0.06552327076825293 + 0.5200241663947267) / 2; // outline mid-plane offset in e2

    // principal frame (columns e1,e2,e0) + centroid, from JSON
    // world = centroid + u*e1 + v*e2 + w*e0 ; local: x=u(e1), y=v(e2), z=w(e0)
    // centroid
    cx = 0.44119784559796194;
    cy = -1.4524250851382396;
    cz = 64.66925852212562;
    // e1 (principal_axes[1])
    e1x = 0.9999999999999987;  e1y = 5.101571019845674e-08;  e1z = 1.1910700121443101e-08;
    // e2 (principal_axes[2])
    e2x = -3.7162652564615806e-08; e2y = 0.8510479848443533; e2z = -0.525087923582674;
    // e0 (principal_axes[0])
    e0x = -3.692431067464216e-08; e0y = 0.5250879235826725; e0z = 0.851047984844354;

    // --- tapered outline in the (e0 , e1) plane ---
    // each row: [s_along_e0, half_width_in_e1]   (outline is symmetric in e1)
    s_hw = [
        [ -56.210913273070176, 29.130 ],
        [ -29.756272516140438, 29.130 ],
        [  -3.3016317592107,   24.592 ],
        [  23.15300899771904,  18.213 ],
        [  49.607649754648776, 15.200 ],
        [  76.06229051157852,  11.716 ],
        [ 102.51693126850826,   8.427 ]
    ];
    n = len(s_hw);

    // build closed polygon in the (e1 , e0) plane: x = e1, y = e0
    // down the +e1 edge (top->bottom in e0), back up the -e1 edge
    pts_pos = [ for (i=[0:n-1])    [  s_hw[i][1], s_hw[i][0] ] ];
    pts_neg = [ for (i=[n-1:-1:0]) [ -s_hw[i][1], s_hw[i][0] ] ];
    poly = concat(pts_pos, pts_neg);   // (x=e1, y=e0)

    multmatrix([[e1x, e2x, e0x, cx],
                [e1y, e2y, e0y, cy],
                [e1z, e2z, e0z, cz],
                [0,   0,   0,   1]]) {
        // Local target frame: x=e1, y=e2(thickness), z=e0.
        // Extrude poly (x=e1, y=e0) along z by thickness, then rotate([90,0,0]):
        //   (x,y,z) -> (x, -z, y)  => local_x=e1, local_y=-thickness, local_z=e0.
        translate([0, e2_mid, 0])      // shift to outline mid-plane along local y (e2)
            rotate([90, 0, 0])         // map extrude axis -> local y, poly-y(e0) -> local z
                linear_extrude(height = thickness, center = true)
                    polygon(points = poly);
    }
}

sb_harp_white_wood_01();
