"""Dimensioned lathe TURNING drawing of the ORIGINAL (measured-cleaned) pin -> pin.svg.

Full longitudinal section (profile mirrored about the turning axis) + centreline +
dimensions of the real turned features (overall length, shaft Ø, head Ø, the two grooves).
Reads recon/pin_profile.json -- the same measured-cleaned profile parts/pins.py revolves.

Run: .venv/bin/python build123d/recon/make_pin_turning.py
"""
import os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BD = os.path.dirname(HERE)
mm = 8.86
P = np.array(json.load(open(os.path.join(HERE, "pin_profile.json")))["profile"]) * mm  # -> mm
x, r = P[:, 0], P[:, 1]
L = float(x.max())

def dia_in(a, b, fn):                 # diameter (2r) selected by fn over x in [a,b]
    m = (x >= a) & (x <= b)
    idx = np.where(m)[0]
    j = idx[fn(r[idx])]
    return 2 * r[j], x[j]

d_head, x_head = dia_in(0, 4, np.argmax)        # rounded head bulge
d_neck, x_neck = dia_in(3, 12, np.argmin)       # neck groove behind the head
d_shaft, _ = dia_in(24, 60, np.argmax)          # main shaft
d_sgrv, x_sgrv = dia_in(58, 70, np.argmin)      # string-winding groove near the tip
# first station past the neck where the shaft reaches ~full diameter
_after = np.where((x > x_neck) & (2 * r >= 0.97 * d_shaft))[0]
x_shaft = float(x[_after[0]]) if len(_after) else 24.0

# ---- canvas (mm, y-down) ----
rmax = r.max()
MT, MB, ML, MR = 22.0, 20.0, 16.0, 16.0
W = L + ML + MR
Hh = 2 * rmax + MT + MB
PX = 980.0 / W
cy = MT + rmax
ox = ML
X = lambda v: ox + v
S = []
def line(x1, y1, x2, y2, w=0.18, col="black", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    S.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{w}"{d}/>')
def text(x1, y1, s, sz=2.6, anc="middle"):
    S.append(f'<text x="{x1:.2f}" y="{y1:.2f}" font-family="sans-serif" font-size="{sz}" text-anchor="{anc}">{s}</text>')
def arrow(x1, y1, dx):
    S.append(f'<path d="M{x1:.2f},{y1:.2f} l{dx:.2f},-0.9 l0,1.8 z" fill="black"/>')

# part outline (full section)
top = [(X(xx), cy - rr) for xx, rr in P]
bot = [(X(xx), cy + rr) for xx, rr in P]
S.append('<polygon points="' + " ".join(f"{a:.2f},{b:.2f}" for a, b in top + bot[::-1]) +
         '" fill="none" stroke="black" stroke-width="0.3"/>')
# centreline
line(X(-6), cy, X(L + 6), cy, w=0.15, col="rgb(90,90,90)", dash="6,1.5,1,1.5")

def hdim(x1, x2, y, label):           # horizontal length dim with inward arrows + ext lines
    line(X(x1), y - 2.0, X(x1), y + 1.0, 0.1, "rgb(120,120,120)")   # extension ticks
    line(X(x2), y - 2.0, X(x2), y + 1.0, 0.1, "rgb(120,120,120)")
    line(X(x1), y, X(x2), y, 0.15); arrow(X(x1), y, 1.6); arrow(X(x2), y, -1.6)
    text((X(x1) + X(x2)) / 2, y - 1.0, label)

# chained segment lengths along the pin (head -> neck -> shaft start -> string groove -> tip)
ych = cy + rmax + 6
stations = [0.0, x_neck, x_shaft, x_sgrv, L]
for a, b in zip(stations[:-1], stations[1:]):
    hdim(a, b, ych, f"{b - a:.1f}")
# overall length (below the chain)
hdim(0.0, L, cy + rmax + 14, f"{L:.1f}")

# diameter callouts (above) -- leader line up to a label
def dia(xpos, rr, label, lift):
    line(X(xpos), cy - rr, X(xpos), cy - rmax - lift, 0.15)
    text(X(xpos), cy - rmax - lift - 1.0, label)
dia(x_head, d_head / 2, f"Ø{d_head:.1f}", 4)
dia(x_neck, d_neck / 2, f"Ø{d_neck:.1f}", 10)
dia((24 + 58) / 2, d_shaft / 2, f"Ø{d_shaft:.1f}", 4)
dia(x_sgrv, d_sgrv / 2, f"Ø{d_sgrv:.1f}", 10)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*PX:.0f}" height="{Hh*PX:.0f}" '
       f'viewBox="0 0 {W:.2f} {Hh:.2f}">\n' + "\n".join(S) + "\n</svg>\n")
open(os.path.join(BD, "pin.svg"), "w").write(svg)
print(f"wrote build123d/pin.svg | head Ø{d_head:.1f} neck Ø{d_neck:.1f} shaft Ø{d_shaft:.1f} "
      f"groove Ø{d_sgrv:.1f}@{x_sgrv:.0f}mm  L={L:.1f}mm")
