"""Dimensioned lathe TURNING drawing of the designed pin (build123d/pin.svg).

Full longitudinal section (profile mirrored about the turning axis) + centreline +
drilled cross-hole (hidden) + diameter callouts and length dimensions. Reads the shared
design recon/pin_design.json (same data parts/pins.py revolves). Pure plain-venv.

Run: .venv/bin/python build123d/recon/make_pin_turning.py   -> build123d/pin.svg
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
BD = os.path.dirname(HERE)
D = {k: v for k, v in json.load(open(os.path.join(HERE, "pin_design.json"))).items()
     if not k.startswith("_")}

L, c = D["length"], D["chamfer"]
rs, rd, rc = D["d_shaft"]/2, D["d_drive"]/2, D["d_collar"]/2
ld, lc = D["l_drive"], D["l_collar"]

# half profile (x, r) drive -> collar -> shaft -> tip
prof = [(0, rd-c), (c, rd), (ld, rd), (ld, rc), (ld+lc, rc),
        (ld+lc, rs), (L-c, rs), (L, rs-c)]

# ---- canvas (mm, y-down); margins leave room for dimensions ----
MT, MB, ML, MR = 20.0, 20.0, 16.0, 16.0
W = L + ML + MR
H = D["d_collar"] + MT + MB
PX = 980.0 / W
cy = MT + rc                      # centreline y
ox = ML                           # part x-origin
def X(x): return ox + x
def Yt(r): return cy - r          # top
def Yb(r): return cy + r          # bottom

S = []
def line(x1, y1, x2, y2, w=0.18, col="black", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    S.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
             f'stroke="{col}" stroke-width="{w}"{da}/>')
def text(x, y, s, sz=2.6, anc="middle"):
    S.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="sans-serif" font-size="{sz}" '
             f'text-anchor="{anc}">{s}</text>')

# ---- part outline (full section) ----
top = [(X(x), Yt(r)) for x, r in prof]
bot = [(X(x), Yb(r)) for x, r in prof]
pts = top + bot[::-1]
S.append('<polygon points="' + " ".join(f"{x:.2f},{y:.2f}" for x, y in pts) +
         '" fill="none" stroke="black" stroke-width="0.3"/>')

# ---- centreline (dash-dot) ----
line(X(-6), cy, X(L+6), cy, w=0.15, col="rgb(90,90,90)", dash="6,1.5,1,1.5")

# ---- drilled cross-hole (hidden, dashed): walls span hole dia at hole_x ----
hx = L - D["hole_from_tip"]; hr = D["string_hole"]/2
line(X(hx-hr), Yt(rs), X(hx-hr), Yb(rs), w=0.15, col="rgb(60,60,60)", dash="1.4,1")
line(X(hx+hr), Yt(rs), X(hx+hr), Yb(rs), w=0.15, col="rgb(60,60,60)", dash="1.4,1")

# ---- dimension helpers ----
def arrow(x, y, dx):                       # small arrowhead at (x,y) pointing +/-x
    S.append(f'<path d="M{x:.2f},{y:.2f} l{dx:.2f},-0.9 l0,1.8 z" fill="black"/>')
def hdim(x1, x2, y, label):                # horizontal length dimension
    line(x1, y, x2, y, w=0.15)
    arrow(x1, y, 1.6); arrow(x2, y, -1.6)
    text((x1+x2)/2, y-1.0, label)
def lead(xf, yf, xt, yt, label, anc="middle"):   # diameter leader + label
    line(xf, yf, xt, yt, w=0.15)
    text(xt, yt-1.0 if yt < cy else yt+3.0, label, anc=anc)

# length dims (below)
yb1 = cy + rc + 7
hdim(X(0), X(L), cy + rc + 13, f"{L:.1f}")
hdim(X(0), X(ld), yb1, f"{ld:.0f}")
hdim(X(hx), X(L), yb1, f"{D['hole_from_tip']:.0f}")
# diameter callouts (above)
lead(X(ld/2), Yt(rd), X(ld/2), cy - rc - 5, f"Ø{D['d_drive']:.1f}")
lead(X(ld+lc/2), Yt(rc), X(ld+lc/2), cy - rc - 11, f"Ø{D['d_collar']:.1f}")
lead(X((ld+lc+L)/2), Yt(rs), X((ld+lc+L)/2), cy - rc - 5, f"Ø{D['d_shaft']:.1f}")
lead(X(hx), Yt(rs), X(hx), cy - rc - 11, f"Ø{D['string_hole']:.1f} thru")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*PX:.0f}" height="{H*PX:.0f}" '
       f'viewBox="0 0 {W:.2f} {H:.2f}">\n' + "\n".join(S) + "\n</svg>\n")
open(os.path.join(BD, "pin.svg"), "w").write(svg)
print(f"wrote build123d/pin.svg  ({L:.1f}mm pin, {W:.0f}x{H:.0f}mm sheet -> {W*PX:.0f}x{H*PX:.0f}px)")
