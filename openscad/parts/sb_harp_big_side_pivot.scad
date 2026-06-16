// sb_harp_big_side_pivot - SOUNDBOX BODY = straight-sided HALF-CONE
// D cross-section in the world X(width)-Y(depth) plane: FLAT soundboard side at Y=yflat,
// arc belly bulging to +Y. Wings dropped (arc-only width). Straight sides = hull(bass,treble).
// Body rakes in Y-Z; the two caps sit at their world Z, so the hull reproduces the rake.
nh=48;
function _hc_arc(W,D,xc,yf)=[for(i=[0:nh]) let(t=180*i/nh)[ xc+(W/2)*cos(t), yf+D*sin(t) ]];
module _hc_cap(z,xc,yf,W,D,eps) translate([0,0,z]) linear_extrude(height=eps) polygon(_hc_arc(W,D,xc,yf));
module sb_harp_big_side_pivot(){
    eps=0.02;
    bz=15.856; bxc=0.312; byf=-32.440; bW=49.280; bD=30.077;
    tz=151.895; txc=0.312; tyf=52.058; tW=13.957; tD=8.078;
    hull(){ _hc_cap(bz,bxc,byf,bW,bD,eps); _hc_cap(tz,txc,tyf,tW,tD,eps); }
}
sb_harp_big_side_pivot();
