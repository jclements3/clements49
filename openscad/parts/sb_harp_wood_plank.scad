// sb_harp_wood_plank.scad
// Soundbox part: harp_wood_plank
//
// Construction: FLAT/THIN BAR -> linear_extrude of a constant cross-section.
// Justification from the analysis JSON:
//   obb_dims = [157.99, 2.60, 0.715]  (along principal axes e0, e1, e2).
//   The long axis e0 (157.99) >> the other two. Sections are sliced along e0
//   (s from -79.00 .. +78.99). All 7 cross-section outlines (outline_e1e2) are
//   essentially IDENTICAL: e1 spans +/-1.30 (width 2.60), e2 spans -0.481..0.234
//   (thickness ~0.715). So the profile is a constant 2D outline in the (e1,e2)
//   plane swept along e0  -> linear_extrude of that single outline.
//
// Local frame (per shared contract): x = e1, y = e2, z = e0.
//   world = centroid + x*e1 + y*e2 + z*e0
//   multmatrix columns: [e1, e2, e0, centroid]

module sb_harp_wood_plank() {
    // --- key dimensions (model world units) ---
    length_e0   = 157.99349936504035; // long axis extent (OBB dim along e0)
    s_min       = -79.00199779074894; // start of sweep along e0
    // width along e1 ~ 2.60, thickness along e2 ~ 0.715 are encoded in the outline

    // Representative constant cross-section in the (e1=x, e2=y) plane,
    // taken from the central section s ~= 0 (n_pts = 25).
    profile = [
        [-1.304068613138129,   0.039914452730746675],
        [-1.2988414417338716, -0.03920977952225879],
        [-1.2619292589382591, -0.10661357487112998],
        [-1.1647280374804423, -0.1698429468966287],
        [-0.99087463649703,   -0.24914266551218311],
        [-0.7315022194947558, -0.3551233613066156],
        [-0.3954583800005634, -0.44727456985152614],
        [-0.0038031597561305947, -0.48089703076206947],
        [ 0.3912742338218062, -0.4458243328934035],
        [ 0.73588004868243,   -0.3504180548228808],
        [ 1.0004441501844406, -0.24255720658648894],
        [ 1.1693076613345343, -0.16573332753383863],
        [ 1.2581205347344715, -0.10634987031153553],
        [ 1.2911667131536821, -0.0407195898591004],
        [ 1.295934128762341,   0.03816542762517994],
        [ 1.2912792546972822,  0.1270234519437894],
        [ 1.2912761508157018,  0.12705869741439013],
        [ 1.2583218280177508,  0.19833928175529536],
        [ 1.1695688953365784,  0.22829787676322244],
        [ 1.0007615422199547,  0.23266994191751955],
        [ 0.7362698133269031,  0.23285942284119],
        [-0.9904897736221766,  0.23400989818133677],
        [-1.164417047013931,   0.22985412235596048],
        [-1.26171150515054,    0.20002350118136558],
        [-1.2987277245542947,  0.12877525746163343]
    ];

    // Place the part at its original world coords.
    // multmatrix([[e1x,e2x,e0x,cx],[e1y,e2y,e0y,cy],[e1z,e2z,e0z,cz],[0,0,0,1]])
    multmatrix([
        [ 0.9999997748485234,    -0.0006710461244862703,  3.807473468457577e-08, 0.3513917557574726],
        [ 0.0005708356524937477,  0.8506949335985642,     0.5256593993227865,   10.44220652615824],
        [-0.0003527740926992308, -0.5256592809480621,     0.8506951251203959,   84.38742842926786],
        [ 0, 0, 0, 1]
    ]) {
        // Sweep the constant profile along z (= e0).
        translate([0, 0, s_min])
            linear_extrude(height = length_e0)
                polygon(points = profile);
    }
}

sb_harp_wood_plank();
