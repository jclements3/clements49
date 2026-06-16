// ======================================================================
//  Clements 49 — limaçon soundbox  (parametric generator)
//
//  OUTER cross-section = limaçon with a:b = 2  -> single FLAT point at
//  theta=180, so the stringbar seats on a flat (not a notch).
//  INNER cross-section = free-form graded wall (board / rib / belly);
//  it owes nothing to a:b and carries the structural job.
//
//  Sections are cut PERPENDICULAR to the raked stringbar and lofted
//  bass -> treble. Units mm, angles degrees.
// ======================================================================

// ---------------------------------------------------------------- FRAME
// (principal axis of the 49 board pins in strings_49.json)
U_AXIS  = [0.523, 0, 0.852];   // stringbar axis, raked 31.6 deg from vertical (x-z plane)
Y_MINOR = [0, 1, 0];           // soundboard WIDTH direction = limacon minor side (y)
N_BOARD = [-0.852, 0, 0.523];  // soundboard normal (x-z). belly = -N_BOARD = [0.852,0,-0.523] (-z, "underneath")

P_BASS   = [-297.4, -2.5,  111.8];   // bass   board pin  (loft start)
P_TREBLE = [ 417.2, -2.5, 1262.8];   // treble board pin  (loft end)

// ----------------------------------------------------------- PARAMETERS
AB        = 2.0;    // a:b for the OUTER. ==2 gives the flat seat.
                    //  >2 = rounder (no flat), <2 = concave dent. KEEP AT 2 for the outer.
NSEC      = 41;     // loft stations bass->treble
MPTS      = 160;    // points per ring (even, >=80)

// --- soundboard half-width profile  (FIRST-CUT teardrop) --------------
//     This is the ONLY thing the soundboard Bezier controls.
//     Replace the body of w_half(s) with your Bezier evaluation, s in [0,1].
HW_BASS   = 190;    // half-width at the bass (mm) -> 380 wide
HW_TREBLE = 35;     // half-width at the treble (mm) -> 70 wide (materials.md taper 380->70)
TEAR_EXP  = 0.6;    // teardrop taper exponent (first cut only)
// INTEGRATION FIX: original was HW_BASS*pow(1-s,TEAR_EXP), which hits 0 at s=1 ->
// the treble tip collapses to a point -> NaN in the inner-wall normal and the
// cavity cut fails ("mesh not closed"). Floored to HW_TREBLE (also matches spec taper).
// clamp s to [0,1] so the END EXTENSIONS (S_MIN<0 / S_MAX>1, used to reach the
// base and the neck) keep the end section width instead of pow(negative)->NaN.
function w_half(s) = HW_TREBLE + (HW_BASS - HW_TREBLE) * pow(1 - max(0,min(1,s)), TEAR_EXP);   // <<< BEZIER HOOK >>>

// --- wall thickness  (free-form INNER) --------------------------------
T_BOARD   = 3.5;    // thin radiating board (flanks of the stringbar)
T_BELLY   = 8.0;    // structural belly (closes the box)
T_RIB     = 24.0;   // string-anchor rib peak, at theta=180 (the stringbar line)
RIB_SIG   = 10;     // rib angular half-width (deg) -> narrower = sharper rib

// -------------------------------------------------------------- HELPERS
function vsum(v,i=0,a=0) = i<len(v) ? vsum(v,i+1,a+v[i]) : a;
function lim_Wunit(a,b)  = max([for(t=[0:2:359]) abs((a+b*cos(t))*sin(t))]);

// OUTER ring in section-plane coords [minor, depth]; flat top at depth 0
function outer2d(s) =
  let(a=AB, b=1,
      sc    = (2*w_half(s)) / (2*lim_Wunit(a,b)),  // UNIFORM scale -> stays a true limacon
      lxmin = -(a-b))                              // flat/dimple end of the symmetry axis
  [ for(i=[0:MPTS-1])
      let(t=360*i/MPTS, r=a+b*cos(t))
      [ (r*sin(t))*sc, -((r*cos(t))-lxmin)*sc ] ]; // depth: 0 at flat top -> -D at belly

// wall thickness as a function of ring index (free-form)
function t_of(i) =
  let(t=360*i/MPTS,
      base = (T_BELLY+T_BOARD)/2 + (T_BELLY-T_BOARD)/2*cos(t),  // thin top, thick belly
      rib  = (T_RIB-T_BOARD)*exp(-pow((t-180)/RIB_SIG,2)))      // rib spike at stringbar
  base + rib;

// INNER ring = OUTER offset inward by t_of() along the local inward normal
function inner2d(s) =
  let(o=outer2d(s), m=len(o),
      cx=vsum([for(p=o)p[0]])/m, cy=vsum([for(p=o)p[1]])/m)
  [ for(i=[0:m-1])
      let(p=o[i], pn=o[(i+1)%m], pp=o[(i+m-1)%m],
          tx=pn[0]-pp[0], ty=pn[1]-pp[1], L=norm([tx,ty]),
          nx=ty/L, ny=-tx/L,
          sg=sign((cx-p[0])*nx+(cy-p[1])*ny), tt=t_of(i))
      [ p[0]+nx*sg*tt, p[1]+ny*sg*tt ] ];

// map a section-plane point [minor, depth] to world 3D at station s
function P_at(s)      = P_BASS + s*(P_TREBLE - P_BASS);
function to3d(s,ring) = let(P=P_at(s)) [ for(p=ring) P + p[0]*Y_MINOR + p[1]*N_BOARD ];

// skin a list of equal-length 3D rings into a closed solid
module skin(rings) {
  n=len(rings); m=len(rings[0]);
  pts =[for(r=rings) for(p=r) p];
  side=[for(i=[0:n-2]) for(j=[0:m-1])
          [ i*m+j, i*m+(j+1)%m, (i+1)*m+(j+1)%m, (i+1)*m+j ]];
  cap0=[for(j=[0:m-1]) (m-1-j)];          // first cap (reversed winding)
  cap1=[for(j=[0:m-1]) (n-1)*m+j];        // last cap
  polyhedron(points=pts, faces=concat(side,[cap0],[cap1]), convexity=10);
}

// ---------------------------------------------------------------- BUILD
// ATTACHMENT: extend the loft past the string board-line (s in [0,1]) so the
// body meets the frame. Measured: the neck meets the loft axis at s≈1.07–1.19,
// and the bass end (s=0, z≈112) already sits in the base z-band (7–137).
S_MIN = -0.03;   // bass: seat slightly into the base
S_MAX =  1.20;   // treble: overlap the neck shoulder (closes the gap to the neck)
SS = [for(k=[0:NSEC-1]) S_MIN + (k/(NSEC-1))*(S_MAX - S_MIN)];

// hollow=false (default): the clean limaçon OUTER body — VERIFIED single watertight
//   solid (~74.7 L) by CGAL render here.
// hollow=true: the graded-wall version. KNOWN-BROKEN (verified): the difference
//   fragments the wall into ~109 disconnected bodies because the inner offset
//   (inner2d) crosses the outer along the raked loft. Outer and inner each loft
//   clean ALONE (1 body each); the WALL logic needs rework before hollowing.
//   Winding/skin() is NOT the problem (the author's stated worry) — it renders.
module soundbox_limacon(hollow=false) {
  if (hollow)
    difference() {
      skin([for(s=SS) to3d(s, outer2d(s))]);   // outer solid
      skin([for(s=SS) to3d(s, inner2d(s))]);   // remove the cavity  <-- fragments, see above
    }
  else
    skin([for(s=SS) to3d(s, outer2d(s))]);     // clean outer body
  // Back sound-holes are NOT cut here; subtract them from the belly face
  // (theta ~ 0 side) after this, sized per the acoustic note (~240 cm^2 total).
}

soundbox_limacon();   // self-renders standalone; ignored when this file is `use`d

// Notes for integration:
//  * Drop this into harp_scaffold.scad in place of the empty
//    `module soundbox_limacon(){}` slot; comment out the trailing
//    assembly calls if you only want to view the box.
//  * I cannot run OpenSCAD in my sandbox, so the polyhedron winding is
//    reasoned, not rendered. If it renders inside-out, swap cap0/cap1 or
//    reverse the side quad order. F6 + a manifold check is the acceptance test.

