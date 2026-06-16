"""Clean silhouette plate of a SINGLE tuning pin: profile view + end view.

The pin is axisymmetric (a lathe/revolve part), so the profile silhouette IS its turned
outline. Pulls one full-length pin from cad/parts_mesh/hardware_pins.stl, centers it, and
draws PROFILE (length x diameter) beside the END view (the circle). Views only, no labels.

Run (plain venv): .venv/bin/python build123d/recon/make_pin_plate.py
Writes build123d/pin.svg
"""
import os
import numpy as np, trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
BD = os.path.dirname(HERE)
ROOT = os.path.dirname(BD)
PINS = os.path.join(ROOT, "cad", "parts_mesh", "hardware_pins.stl")
GAP = 1.0
FIT_PX = 760.0
UNIT_MM = 8.86

def silhouette(mesh, right, up):
    P = np.column_stack([np.array(right, float), np.array(up, float)])
    tri = (mesh.vertices @ P)[mesh.faces]
    a = tri[:, 1] - tri[:, 0]; b = tri[:, 2] - tri[:, 0]
    keep = np.abs(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]) > 1e-9
    g = unary_union([Polygon(t) for t in tri[keep]])
    rings = []
    for poly in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
        if not poly.is_empty:
            rings.append(list(poly.exterior.coords))
            rings += [list(h.coords) for h in poly.interiors]
    return rings

# pick one full-length pin body and center it on the origin
m = trimesh.load(PINS)
bodies = m.split(only_watertight=False)
def longax(b): return (b.bounds[1] - b.bounds[0]).max()
pin = max((b for b in bodies if 6 < longax(b) < 10), key=lambda b: len(b.faces))
pin.apply_translation(-pin.centroid)
L = float((pin.bounds[1] - pin.bounds[0])[0])
D = float((pin.bounds[1] - pin.bounds[0])[1])
print(f"pin: length {L:.2f} u ({L*UNIT_MM:.1f} mm)  dia {D:.2f} u ({D*UNIT_MM:.1f} mm)  tris {len(pin.faces)}")

# PROFILE: long axis X horizontal, Z up.  END: looking down +X -> (Y right, Z up)
prof = silhouette(pin, (1, 0, 0), (0, 0, 1))
end = silhouette(pin, (0, 1, 0), (0, 0, 1))

def bounds(rings):
    pts = np.array([p for r in rings for p in r])
    return pts[:, 0].min(), pts[:, 0].max(), pts[:, 1].min(), pts[:, 1].max()

pu0, pu1, pv0, pv1 = bounds(prof); eu0, eu1, ev0, ev1 = bounds(end)
pw, ph = pu1 - pu0, pv1 - pv0
ew, eh = eu1 - eu0, ev1 - ev0
sheet_w = pw + GAP + ew
sheet_h = max(ph, eh)
px = FIT_PX / max(sheet_w, sheet_h)

def place(rings, u0, vmax, ox, oy):
    out = []
    for r in rings:
        s = " ".join(f"{ox + (u - u0):.3f},{oy + (vmax - v):.3f}" for u, v in r)
        out.append(f'<polygon points="{s}" fill="none" stroke="black" stroke-width="0.04"/>')
    return out

parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{sheet_w*px:.0f}" '
         f'height="{sheet_h*px:.0f}" viewBox="0 0 {sheet_w:.3f} {sheet_h:.3f}">']
# vertically center each view in the sheet
parts += place(prof, pu0, pv1, 0.0, (sheet_h - ph) / 2)
parts += place(end, eu0, ev1, pw + GAP, (sheet_h - eh) / 2)
parts.append("</svg>")
out_path = os.path.join(BD, "pin.svg")
open(out_path, "w").write("\n".join(parts))
print(f"wrote {out_path}  sheet {sheet_w:.2f}x{sheet_h:.2f}u -> {sheet_w*px:.0f}x{sheet_h*px:.0f}px")
