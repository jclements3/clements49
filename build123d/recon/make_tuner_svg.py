"""tuner.svg -- orthographic HLR plate of the 3D build123d worm-drive tuner assembly.

Projects the real 3D solids (receiver + spindle + worm) with hidden-line removal into
END / SIDE / TOP views, laid out in a row (views only). This is the drawing GENERATED
FROM the 3D model -- as the model is refined, the plate follows.

Local frame: X = post axis, Y = worm/outward, Z = neck-pitch (the offset direction).
  END  (along X): looks down the post -> wheel + worm + receiver footprint
  SIDE (along Y): looks down the worm -> post length + wheel + receiver
  TOP  (along Z): looks down the neck offset -> post + worm from above

Run: build123d/py recon/make_tuner_svg.py
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "parts"))
import util
from parts.tuner import assembly

BD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWS = {"end": ((1, 0, 0), (0, 0, 1)),
         "side": ((0, 1, 0), (0, 0, 1)),
         "top": ((0, 0, 1), (1, 0, 0))}
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
    order = ["end", "side", "top"]
    xs, x = [], 0.0
    for n in order:
        xs.append(x); x += V[n]["w"] + GAP
    sheet_w = x - GAP
    sheet_h = max(V[n]["h"] for n in order)
    parts = [None]
    for n, xx in zip(order, xs):
        parts.append(_cell(V[n], xx, sheet_h - V[n]["h"]))   # bottom-aligned
    px = FIT_PX / max(sheet_w, sheet_h)
    parts[0] = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{sheet_w*px:.0f}" '
                f'height="{sheet_h*px:.0f}" viewBox="0 0 {sheet_w:.2f} {sheet_h:.2f}">')
    parts.append("</svg>")
    open(os.path.join(BD, "tuner.svg"), "w").write("\n".join(parts))
    print(f"wrote build123d/tuner.svg  ({len(order)} HLR views from the 3D model, "
          f"sheet {sheet_w:.0f}x{sheet_h:.0f} mm)")


if __name__ == "__main__":
    main()
