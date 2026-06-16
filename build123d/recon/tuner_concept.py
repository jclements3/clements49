"""Compact brass worm-drive harp tuner -- concept layout + packaging fit check.

Adapts the worm-and-wheel principle of the guitar tuner (self-locking, geared fine
adjustment) into a slim brass unit sized for harp pin pitch. This computes the gear
sizing from the worm-drive relations, the assembly envelope, and whether it fits the
string pitch (tightest treble 11.7 mm). Pure plain-venv; writes build123d/tuner_concept.svg.

Worm self-locks (holds string tension) when the worm lead angle < ~ friction angle,
which a single-start worm at these diameters satisfies -- so tension can't back-drive it.
"""
import os, json, math

HERE = os.path.dirname(os.path.abspath(__file__)); BD = os.path.dirname(HERE)

# ---- design parameters (mm) ----
# Drive: worm turned by a HEX DRIVER (no finger knob) -- a hex socket on the worm's
# outboard end. Mount: gears run in brass bushings bonded SOLIDLY into the flax-resin
# (VARTM) neck -- the composite neck is the structure, so walls are just bushing shells.
P = dict(
    module=0.4,        # gear module (tooth size)
    z2=10,             # worm-wheel teeth  -> ratio = z2/z1
    z1=1,              # worm starts (1 = self-locking)
    worm_pitch_dia=5.0,   # larger worm dia -> low lead angle -> self-locking
    worm_len=10.0,     # worm length along its axis = OUTWARD (mesh + bearing + hex socket)
    post_dia=4.5,      # string post (the part the string winds on)
    string_hole=1.2,
    wall=0.8,          # brass bushing shell (neck carries the load, not a metal case)
    hex_af=4.0,        # hex-driver socket across-flats on the worm end (4mm driver)
)
PITCH = dict(treble=11.7, median=18.7, bass=30.0)   # adjacent-pin spacing along the neck

m, z2, z1 = P["module"], P["z2"], P["z1"]
dp2 = m * z2;              Do2 = m * (z2 + 2);   Df2 = m * (z2 - 2.5)   # wheel pitch/out/root
dp1 = P["worm_pitch_dia"]; Do1 = dp1 + 2 * m                            # worm pitch/outside
C = (dp1 + dp2) / 2                                                     # centre distance
ratio = z2 / z1
lead_angle = math.degrees(math.atan(z1 * m / dp1))                     # worm lead angle

# Envelope along the NECK pitch direction (U): wheel disc + the offset worm.
# Wheel spans +/-Do2/2 about the post; worm axis sits at U=C, worm spans Do1 wide there.
u_min = -Do2 / 2 - P["wall"]
u_max = C + Do1 / 2 + P["wall"]
env_U = u_max - u_min                                # neck footprint (the binding dim)
env_V = P["worm_len"] + Do2 / 2 + 2 * P["wall"]      # outward (toward player) -- has room
hex_corner = P["hex_af"] / math.cos(math.radians(30))
print(f"ratio {ratio:.0f}:1  lead {lead_angle:.1f} deg (self-locking if <~5-6)  "
      f"wheel Ø{Do2:.1f}  worm Ø{Do1:.1f}  centre {C:.1f}")
print(f"drive: {P['hex_af']:.0f}mm hex socket (corners Ø{hex_corner:.1f}); mount: brass bushings in flax-resin neck")
print(f"NECK footprint (U) = {env_U:.1f} mm   outward (V) = {env_V:.1f} mm")
for k, pitch in PITCH.items():
    ok = "FITS" if env_U <= pitch else "TOO WIDE"
    print(f"  {k:7s} pitch {pitch:4.1f} mm -> {ok}  (clearance {pitch-env_U:+.1f})")
# largest wheel teeth that still fit the tightest pitch (strength vs fit guide)
for zt in range(8, 20):
    eu = (m*(zt+2))/2 + P["wall"] + ((P["worm_pitch_dia"]+m*zt)/2) + Do1/2 + P["wall"]
    if eu > PITCH["treble"]:
        print(f"  -> at module {m}, max wheel that fits treble ~ z2={zt-1}"); break

# ---- 2D layout, looking ALONG the post axis (the packing view) ----
SC = 14.0; MAR = 14.0
W = (env_U + 2 * MAR); Hh = (env_V + 2 * MAR)
ox = MAR - u_min; oy = MAR + (P["worm_len"] + Do2/2)
def Xx(u): return (ox + u) * SC
def Yy(v): return (oy - v) * SC
S = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*SC:.0f}" height="{Hh*SC:.0f}" '
     f'viewBox="0 0 {W*SC:.1f} {Hh*SC:.1f}">']
def circ(u, v, r, **k): S.append(f'<circle cx="{Xx(u):.1f}" cy="{Yy(v):.1f}" r="{r*SC:.1f}" '
     f'fill="{k.get("f","none")}" stroke="{k.get("s","black")}" stroke-width="{k.get("w",1)}"'
     + (f' stroke-dasharray="{k["d"]}"' if "d" in k else "") + '/>')
def rect(u1, v1, u2, v2, **k): S.append(f'<rect x="{Xx(u1):.1f}" y="{Yy(v2):.1f}" '
     f'width="{(u2-u1)*SC:.1f}" height="{(v2-v1)*SC:.1f}" fill="none" stroke="{k.get("s","black")}" '
     f'stroke-width="{k.get("w",1)}"' + (f' stroke-dasharray="{k["d"]}"' if "d" in k else "") + '/>')
def txt(u, v, s, sz=11, c="black"): S.append(f'<text x="{Xx(u):.1f}" y="{Yy(v):.1f}" '
     f'font-family="sans-serif" font-size="{sz}" fill="{c}" text-anchor="middle">{s}</text>')

# neck pitch envelope (treble) -- the space this tuner may occupy
rect(-PITCH["treble"]/2, -env_V/2, PITCH["treble"]/2, env_V/2, s="rgb(210,40,40)", w=1.2, d="5,3")
txt(0, env_V/2+0.6, f"treble pitch {PITCH['treble']} mm", 11, "rgb(210,40,40)")
# brass RECEIVER (cast brass, co-moulded into the VARTM flax neck): holds the gear bores
# and the load path; resin keys into the anchor holes during infusion.
S.append(f'<rect x="{Xx(u_min):.1f}" y="{Yy(env_V/2):.1f}" width="{(u_max-u_min)*SC:.1f}" '
         f'height="{env_V*SC:.1f}" rx="{1.5*SC:.1f}" fill="rgb(218,165,32)" fill-opacity="0.16" '
         f'stroke="rgb(170,120,20)" stroke-width="1.4"/>')
for av in (-env_V/2+1.4, env_V/2-1.4):                 # resin-keying anchor holes
    circ(u_min+0.9, av, 0.45, s="rgb(170,120,20)", w=0.8)
    circ(u_max-0.9, av, 0.45, s="rgb(170,120,20)", w=0.8)
txt(0, -env_V/2-1.2, "brass receiver (co-moulded)", 10, "rgb(150,100,10)")
# wheel: outside + pitch + root circles
circ(0, 0, Do2/2, w=2); circ(0, 0, dp2/2, w=0.6, d="4,2", s="rgb(120,120,120)"); circ(0, 0, Df2/2, w=0.6, s="rgb(150,150,150)")
circ(0, 0, P["post_dia"]/2, w=1.2, s="rgb(60,60,140)")           # string post
circ(0, 0, P["string_hole"]/2, w=0.8, s="rgb(60,60,140)")        # string hole
# worm: rectangle at U=C, length along V (outward)
rect(C-Do1/2, -P["worm_len"]/2, C+Do1/2, P["worm_len"]/2, w=2, s="rgb(40,120,40)")
circ(C, 0, dp1/2, w=0.5, d="3,2", s="rgb(40,120,40)")
txt(C, P["worm_len"]/2+0.8, "worm (turn)", 10, "rgb(40,120,40)")
txt(0, -Do2/2-1.0, "worm wheel + post", 10)
S.append("</svg>")
open(os.path.join(BD, "tuner_concept.svg"), "w").write("\n".join(S))
json.dump({**P, "ratio": ratio, "wheel_OD": round(Do2,2), "worm_OD": round(Do1,2),
           "centre_dist": round(C,2), "neck_footprint": round(env_U,2),
           "outward": round(env_V,2), "lead_angle_deg": round(lead_angle,2)},
          open(os.path.join(HERE, "tuner_params.json"), "w"), indent=1)
print("wrote build123d/tuner_concept.svg + recon/tuner_params.json")
