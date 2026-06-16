// sb_harp_wood_inside
// SOUNDBOX inner lining piece "harp_wood_inside".
// Reverse-engineered from analysis JSON (model world units, NOT mm).
//
// Construction choice: FLAT PLATE (linear_extrude of a constant outline).
//   OBB dims = [42.12, 27.29, 0.646].  One OBB dim (0.646, along principal
//   axis e0) is ~42x/~66x smaller than the other two => thin flat plate.
//   The 7 cross-sections sliced along the long axis (e1) are essentially
//   identical (same outline within sub-0.1 unit jitter) => CONSTANT profile,
//   so a single outline swept along e1 reproduces the shape exactly.
//
// The 7 cross-sections are sliced along the SWEEP axis = e0 (= world X,
// section world_pos.x runs -20.75 .. +21.37 while y,z stay fixed).
// Each section outline is given in the (e1, e2) plane:
//   outline 1st coord = e1 (the 27.29-wide outline coordinate, ~world Y),
//   outline 2nd coord = e2 (the 0.646 thin/thickness coordinate, ~world Z).
//
// Local frame used to build geometry (per SHARED CONTRACT
// world = centroid + u*e1 + v*e2 + w*e0):
//   local x = u = e1 (outline width coordinate)
//   local y = v = e2 (outline thin/thickness coordinate)
//   local z = w = e0 (sweep axis)
// Placed back to world coords with multmatrix whose columns are
//   [ e1 | e2 | e0 | centroid ].

module sb_harp_wood_inside() {
    // --- principal axes from JSON (e0=thin, e1=long sweep, e2=width) ---
    e0 = [ 0.999999999999999, 4.080533203209976e-08, -5.195677116993409e-09 ];
    e1 = [ -4.079117591697188e-08, 0.9999963656460189, 0.0026960516967458603 ];
    e2 = [ 5.305671518725019e-09, -0.002696051696745555, 0.99999636564602 ];
    centroid = [ 0.31174035168980263, -18.940998050994775, 15.742848081661917 ];

    // --- key dimensions (model units) ---
    sweep_min = -21.06039328592594;   // obb_min along e0 (sweep axis)
    sweep_max =  21.06042008382528;   // obb_max along e0 (sweep axis)
    sweep_len = sweep_max - sweep_min; // ~42.12 long axis

    // Cross-section outline in (e1, e2) plane (first coord -> local x = e1
    // = width ~27.29; second coord -> local y = e2 = thickness ~0.646).
    // Taken from the mid-section (s ~= 0); all sections match to ~0.1 units.
    outline = [
        [ -12.98081096319675,   -0.0012004146546172184 ],
        [ -12.874776522523836,  -0.16576777850281812   ],
        [ -12.641078374338878,  -0.3725658134383558    ],
        [  14.095366556414852,  -0.4882501226337789    ],
        [  14.30897821146989,   -0.48882601782636426   ],
        [  14.308761640427582,  -0.26176333704600196   ],
        [  14.303445951094751,  -0.08202747384794523   ],
        [  14.287969748227038,   0.017577257752377187  ],
        [  14.257419992889528,   0.06228029785476115   ],
        [  14.18123671256184,    0.08592041681057808   ],
        [  13.926107364267846,   0.09864081380347323   ],
        [  13.31236823452081,    0.10473104760524393   ],
        [  12.077700923804764,   0.10869112129297366   ],
        [  11.926059988181972,   0.10910092342014076   ],
        [   4.950142847152765,   0.12790843002158353   ],
        [   2.356783781076516,   0.1349002872010575    ],
        [  -0.26820909907201795, 0.14197740760655003   ],
        [  -2.8519094283243756,  0.14894226890156992   ],
        [  -5.4142015490897055,  0.1552180776580507    ],
        [  -7.910553767061631,   0.1575137950631383    ],
        [ -10.219125788309363,   0.15170624829559382   ],
        [ -11.950139712218796,   0.1329374904585362    ],
        [ -12.78788193291687,    0.09148236649036412   ],
    ];

    multmatrix([
        [ e1[0], e2[0], e0[0], centroid[0] ],
        [ e1[1], e2[1], e0[1], centroid[1] ],
        [ e1[2], e2[2], e0[2], centroid[2] ],
        [ 0,     0,     0,     1           ],
    ])
    // extrude the (e1,e2) outline along local z (= e0 sweep axis)
    translate([0, 0, sweep_min])
        linear_extrude(height = sweep_len)
            polygon(points = outline);
}

sb_harp_wood_inside();
