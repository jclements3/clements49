"""Plate of the worm-drive tuner + its co-moulded brass receiver, as a mating PAIR.

Two parts side by side, both viewed along the string-post axis (the packing view):
  RIGHT  = TUNER     : string post + integral worm wheel + worm (hex-driven)
  LEFT   = RECEIVER  : cast-brass body co-moulded into the flax neck, with the post bore,
                       worm bore and resin-keying anchor holes the tuner drops into.
Reads recon/tuner_params.json (the validated sizing). Writes build123d/tuner_pair_concept.svg.

Run: .venv/bin/python build123d/recon/make_tuner_plate.py
"""
import os, json, math

HERE = os.path.dirname(os.path.abspath(__file__)); BD = os.path.dirname(HERE)
P = json.load(open(os.path.join(HERE, "tuner_params.json")))
m, z2 = P["module"], P["z2"]
Do2 = P["wheel_OD"]; dp2 = m * z2; Do1 = P["worm_OD"]; C = P["centre_dist"]
post, hole, wall = P["post_dia"], P["string_hole"], P["wall"]
wlen, hexaf, ratio = P["worm_len"], P["hex_af"], P["ratio"]
clr = 0.4                                   # bore running clearance

# envelope (U along neck, V outward) of the receiver body
u0 = -Do2/2 - wall; u1 = C + Do1/2 + wall
v1 = wlen/2 + wall; v0 = -Do2/2 - wall
EU, EV = u1 - u0, v1 - v0

SC = 17.0; GAP = 10.0; MX, MY = 12.0, 9.0
cellw = EU + 6.0
W = MX*2 + cellw*2 + GAP
H = MY*2 + EV
S = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*SC:.0f}" height="{H*SC:.0f}" '
     f'viewBox="0 0 {W*SC:.1f} {H*SC:.1f}">']
def C_(cx, cy, r, **k): S.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*SC:.1f}" fill="{k.get("f","none")}" '
     f'stroke="{k.get("s","black")}" stroke-width="{k.get("w",1.1)}"'+(f' stroke-dasharray="{k["d"]}"' if "d" in k else "")+'/>')
def R_(x, y, wd, ht, **k): S.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{wd:.1f}" height="{ht:.1f}" rx="{k.get("rx",0)*SC:.1f}" '
     f'fill="{k.get("f","none")}" stroke="{k.get("s","black")}" stroke-width="{k.get("w",1.1)}"/>')
def T_(x, y, s, sz=11, c="black", a="middle"): S.append(f'<text x="{x:.1f}" y="{y:.1f}" '
     f'font-family="sans-serif" font-size="{sz}" fill="{c}" text-anchor="{a}">{s}</text>')

def cell(cx_origin):
    """return mapping fns placing this cell's (u,v) origin (post centre) at sheet cx_origin,cy."""
    cy = (MY + v1) * SC
    return (lambda u: (cx_origin + u) * SC), (lambda v: cy - v * SC)

# centres: receiver post at left cell, tuner post at right cell
recv_cx = MX + (-u0)
tun_cx = MX + cellw + GAP + (-u0)

# ---------- RECEIVER (left) ----------
X, Y = cell(recv_cx)
R_(X(u0), Y(v1), (u1-u0)*SC, (v1-v0)*SC, rx=1.5, s="rgb(170,120,20)", w=1.6)   # body
C_(X(0), Y(0), (post+clr)/2, s="rgb(170,120,20)", w=1.0)                        # post bore
R_(X(C-(Do1+clr)/2), Y(wlen/2), (Do1+clr)*SC, wlen*SC, s="rgb(170,120,20)", w=1.0)  # worm bore
for au in (u0+0.9, u1-0.9):
    for av in (v0+1.2, v1-1.2):
        C_(X(au), Y(av), 0.45, s="rgb(170,120,20)", w=0.8)                     # anchor holes
T_(X((u0+u1)/2), Y(v0)+18, "RECEIVER", 12, "rgb(150,100,10)")
T_(X((u0+u1)/2), Y(v0)+31, "cast brass, co-moulded in flax neck", 9, "rgb(150,100,10)")

# ---------- TUNER (right) ----------
X, Y = cell(tun_cx)
C_(X(0), Y(0), Do2/2, w=1.8)                       # worm-wheel OD
C_(X(0), Y(0), dp2/2, w=0.5, d="4,2", s="rgb(120,120,120)")
C_(X(0), Y(0), post/2, w=1.2, s="rgb(60,60,140)")  # string post
C_(X(0), Y(0), hole/2, w=0.8, s="rgb(60,60,140)")  # string hole
R_(X(C-Do1/2), Y(wlen/2), Do1*SC, wlen*SC, s="rgb(40,120,40)", w=1.6)          # worm
C_(X(C), Y(wlen/2-1.4), 0.0, w=0)                                              # (anchor)
# hex socket on worm outboard end (a hexagon)
hx, hy, hr = X(C), Y(wlen/2-1.6), hexaf/2/math.cos(math.radians(30))*SC
pts = " ".join(f"{hx+hr*math.cos(math.radians(60*i+30)):.1f},{hy+hr*math.sin(math.radians(60*i+30)):.1f}" for i in range(6))
S.append(f'<polygon points="{pts}" fill="none" stroke="rgb(40,120,40)" stroke-width="1.0"/>')
T_(X(C), Y(wlen/2)-4, f"{hexaf:.0f}mm hex", 8, "rgb(40,120,40)")
T_(X(0), Y(v0)+18, "TUNER", 12, "black")
T_(X(0), Y(v0)+31, f"post+wheel+worm  {ratio:.0f}:1  self-locking", 9, "rgb(60,60,60)")

# title strip dims (top)
T_(W*SC/2, 13, f"worm-drive tuner + receiver  |  neck footprint {EU:.1f} mm  "
   f"wheel Ø{Do2:.1f}  worm Ø{Do1:.1f}  lead {P['lead_angle_deg']:.1f}°", 11, "rgb(40,40,40)")
S.append("</svg>")
open(os.path.join(BD, "tuner_pair_concept.svg"), "w").write("\n".join(S))
print(f"wrote build123d/tuner_pair_concept.svg  (tuner + receiver pair; footprint {EU:.1f}mm, {ratio:.0f}:1)")
