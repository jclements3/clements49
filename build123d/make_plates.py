"""Third-angle HLR plates for the parametric harp: clements47.svg & clements49.svg.

Layout (views only -- no border, title block, or labels):
  FRONT | SIDE(right) | REAR in one row (bottom-aligned, sharing the vertical Z axis);
  TOP view directly ABOVE the SIDE view, oriented (up=+X) so it shares the SIDE view's
  horizontal depth (Y) axis -> the two align and projection lines connect.
All views share one scale. The sheet is sized to fit a monitor (max ~950 px).
Run:  ./py make_plates.py
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "parts"))
import assembly, util
from parts.strings import strings_by_color

# view -> (view_dir, up). TOP uses up=+X so its horizontal is the depth (Y), matching SIDE.
VIEWS = {
    "front": ((0, -1, 0), (0, 0, 1)),
    "side":  ((1, 0, 0),  (0, 0, 1)),
    "rear":  ((0, 1, 0),  (0, 0, 1)),
    "top":   ((0, 0, 1),  (1, 0, 0)),
}
GAP = 14.0          # model-unit gap between views
FIT_PX = 950.0      # longest plate dimension on screen

def _parse(path):
    a = re.search(r"<svg\s([^>]*)>(.*)</svg>", open(path).read(), re.S)
    attrs, inner = a.group(1), a.group(2)
    x0, y0, w, h = (float(v) for v in re.search(r'viewBox="([^"]+)"', attrs).group(1).split())
    return dict(vb=(x0, y0, w, h), w=w, h=h, inner=inner)

def _cell(v, x, y):    # nested svg box at (x,y), size = its own viewBox (1:1 -> shared scale)
    x0, y0, w, h = v["vb"]
    return (f'<svg x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'viewBox="{x0:.3f} {y0:.3f} {w:.3f} {h:.3f}">{v["inner"]}</svg>')

def make_plate(string_set, scale, out_path):
    # Frame only (no string rods) for black HLR; strings drawn as coloured overlay
    # lines on top (C red, F blue, others dark gray) -- no black string strokes.
    frame = assembly.harp(string_set=string_set, include_strings=False)
    overlays = strings_by_color(string_set=string_set)
    V = {}
    for name, (vd, up) in VIEWS.items():
        p = f"/tmp/_pl_{name}.svg"
        util.hlr_svg(frame, p, view_dir=vd, up=up, scale=scale, overlays=overlays)
        V[name] = _parse(p)
    f, s, r, t = V["front"], V["side"], V["rear"], V["top"]
    # x positions of the row
    fx = 0.0
    sx = fx + f["w"] + GAP
    rx = sx + s["w"] + GAP
    row_w = rx + r["w"]
    row_h = max(f["h"], s["h"], r["h"])
    # top sits above the row, aligned with the side (same x and width => shared Y axis)
    top_h = t["h"]
    row_top = top_h + GAP
    row_bottom = row_top + row_h
    sheet_w = row_w
    sheet_h = row_bottom
    parts = [None]  # header placeholder
    # TOP (above side). Mirror it horizontally so its depth(Y) direction matches the
    # SIDE view -> the column lands on the LEFT in both, aligned (was mirrored).
    parts.append(f'<g transform="matrix(-1,0,0,1,{2*sx + t["w"]:.3f},0)">')
    parts.append(_cell(t, sx, 0.0))
    parts.append("</g>")
    # ROW (bottom-aligned)
    parts.append(_cell(f, fx, row_bottom - f["h"]))
    parts.append(_cell(s, sx, row_bottom - s["h"]))
    parts.append(_cell(r, rx, row_bottom - r["h"]))
    px = FIT_PX / max(sheet_w, sheet_h)
    parts[0] = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{sheet_w*px:.0f}" '
                f'height="{sheet_h*px:.0f}" viewBox="0 0 {sheet_w:.2f} {sheet_h:.2f}">')
    parts.append("</svg>")
    open(out_path, "w").write("\n".join(parts))
    return sheet_w, sheet_h

if __name__ == "__main__":
    bb = assembly.harp(49).bounding_box()
    scale = 1.0   # viewBox stays in model units; sheet px-fit handles screen size
    for n, path in [(47, "clements47.svg"), (49, "clements49.svg")]:
        w, h = make_plate(n, scale, path)
        print(f"wrote {path}  (sheet {w:.0f}x{h:.0f} model-units, fit to ~{int(FIT_PX)}px)")
