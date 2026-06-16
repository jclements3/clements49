"""tuner.svg -- third-angle HLR plate of the 3D build123d worm-drive tuner assembly.

Projects the real 3D solids (receiver + spindle + worm) with hidden-line removal, in the
standard plate layout: FRONT | SIDE | REAR on the bottom row, TOP above the SIDE view
(aligned, sharing the depth axis) -- same format as the harp plates. Views only.
The drawing is GENERATED FROM the 3D model, so it tracks the model.

Local frame: X = post axis, Y = worm/outward (depth), Z = neck-pitch (vertical here).

Run: build123d/py recon/make_tuner_svg.py
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "parts"))
import util
from parts.tuner import assembly

BD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# same view convention as the harp plates: front/side/rear in a row, top above side
VIEWS = {"front": ((0, -1, 0), (0, 0, 1)),
         "side":  ((1, 0, 0),  (0, 0, 1)),
         "rear":  ((0, 1, 0),  (0, 0, 1)),
         "top":   ((0, 0, 1),  (1, 0, 0))}
SCALE = 16.0       # svg units per mm
GAP = 8.0
FIT_PX = 900.0


def _parse(path):
    a = re.search(r"<svg\s([^>]*)>(.*)</svg>", open(path).read(), re.S)
    attrs, inner = a.group(1), a.group(2)
    x0, y0, w, h = (float(v) for v in re.search(r'viewBox="([^"]+)"', attrs).group(1).split())
    return dict(vb=(x0, y0, w, h), w=w, h=h, inner=inner)


def _cell(v, x, y):
    x0, y0, w, h = v["vb"]
    return (f'<svg x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'viewBox="{x0:.3f} {y0:.3f} {w:.3f} {h:.3f}">{v["inner"]}</svg>')


def main():
    asm = assembly()
    V = {}
    for name, (vd, up) in VIEWS.items():
        p = f"/tmp/_tn_{name}.svg"
        util.hlr_svg(asm, p, view_dir=vd, up=up, scale=SCALE)
        V[name] = _parse(p)
    f, s, r, t = V["front"], V["side"], V["rear"], V["top"]
    # bottom row: front | side | rear
    fx = 0.0
    sx = fx + f["w"] + GAP
    rx = sx + s["w"] + GAP
    row_w = rx + r["w"]
    row_h = max(f["h"], s["h"], r["h"])
    # top above the side view, aligned (shares the depth axis); mirror so it registers
    row_top = t["h"] + GAP
    row_bottom = row_top + row_h
    sheet_w, sheet_h = row_w, row_bottom
    parts = [None]
    parts.append(f'<g transform="matrix(-1,0,0,1,{2*sx + t["w"]:.3f},0)">')
    parts.append(_cell(t, sx, 0.0))
    parts.append("</g>")
    parts.append(_cell(f, fx, row_bottom - f["h"]))
    parts.append(_cell(s, sx, row_bottom - s["h"]))
    parts.append(_cell(r, rx, row_bottom - r["h"]))
    px = FIT_PX / max(sheet_w, sheet_h)
    parts[0] = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{sheet_w*px:.0f}" '
                f'height="{sheet_h*px:.0f}" viewBox="0 0 {sheet_w:.2f} {sheet_h:.2f}">')
    parts.append("</svg>")
    open(os.path.join(BD, "tuner.svg"), "w").write("\n".join(parts))
    print(f"wrote build123d/tuner.svg  (front|side|rear + top-above-side, "
          f"sheet {sheet_w:.0f}x{sheet_h:.0f} mm)")


if __name__ == "__main__":
    main()
