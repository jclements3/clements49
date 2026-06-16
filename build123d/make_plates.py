"""Compose third-angle HLR drawing PLATES for the parametric harp: clements47.svg & clements49.svg.

Layout: front | side(right) | rear in one row, TOP view above the side, with a title block.
Each view is a build123d project_to_viewport HLR (visible solid / hidden ISO_DASH), composed
as nested <svg> cells at a SHARED scale so the views (and the 47 vs 49 plates) are comparable.
Run:  ./py make_plates.py      (from build123d/)
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "parts"))
import assembly, util

DIRS = {"front": (0, -1, 0), "side": (1, 0, 0), "rear": (0, 1, 0), "top": (0, 0, 1)}
ROW = ["front", "side", "rear"]          # one row
GAP, MARGIN, TITLE_H = 18.0, 18.0, 60.0

def _parse(path):
    txt = open(path).read()
    a = re.search(r"<svg\s([^>]*)>(.*)</svg>", txt, re.S)
    attrs, inner = a.group(1), a.group(2)
    w = float(re.search(r'width="([\d.]+)mm"', attrs).group(1))
    h = float(re.search(r'height="([\d.]+)mm"', attrs).group(1))
    vb = re.search(r'viewBox="([^"]+)"', attrs).group(1)
    return dict(w=w, h=h, vb=vb, inner=inner)

def _cell(v, x, y_bottom):           # nested svg, bottom-aligned at y_bottom
    y = y_bottom - v["h"]
    return (f'<svg x="{x:.2f}" y="{y:.2f}" width="{v["w"]:.2f}" height="{v["h"]:.2f}" '
            f'viewBox="{v["vb"]}" preserveAspectRatio="xMidYMid meet">{v["inner"]}</svg>')

def make_plate(string_set, scale, out_path):
    asm = assembly.harp(string_set=string_set)
    views = {}
    for name, vd in DIRS.items():
        p = f"/tmp/_plate_{name}.svg"
        util.hlr_svg(asm, p, view_dir=vd, scale=scale)
        views[name] = _parse(p)
    f, s, r, t = views["front"], views["side"], views["rear"], views["top"]
    row_h = max(f["h"], s["h"], r["h"])
    fx = MARGIN; sx = fx + f["w"] + GAP; rx = sx + s["w"] + GAP
    sheet_w = rx + r["w"] + MARGIN
    topband = t["h"] + GAP + 14          # top view + label gap
    row_top = MARGIN + topband
    row_bottom = row_top + row_h
    sheet_h = row_bottom + TITLE_H + MARGIN
    sx_top = sx + (s["w"] - t["w"]) / 2.0   # top centred over side
    P = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{sheet_w:.1f}mm" height="{sheet_h:.1f}mm" '
         f'viewBox="0 0 {sheet_w:.1f} {sheet_h:.1f}">',
         f'<rect x="0" y="0" width="{sheet_w:.1f}" height="{sheet_h:.1f}" fill="white"/>',
         f'<rect x="{MARGIN/2:.1f}" y="{MARGIN/2:.1f}" width="{sheet_w-MARGIN:.1f}" height="{sheet_h-MARGIN:.1f}" fill="none" stroke="#111" stroke-width="0.7"/>']
    # top view (above side)
    P.append(_cell(t, sx_top, MARGIN + t["h"]))
    P.append(f'<text x="{sx + s["w"]/2:.1f}" y="{MARGIN + t["h"] + 9:.1f}" font-family="sans-serif" font-size="6" text-anchor="middle">TOP</text>')
    # row
    for name, x in (("front", fx), ("side", sx), ("rear", rx)):
        P.append(_cell(views[name], x, row_bottom))
        cx = x + views[name]["w"] / 2
        P.append(f'<text x="{cx:.1f}" y="{row_bottom + 8:.1f}" font-family="sans-serif" font-size="6" text-anchor="middle">{name.upper()}</text>')
    # title block
    nstr = 49 if string_set >= 49 else 47
    ty = sheet_h - MARGIN/2 - TITLE_H
    P.append(f'<rect x="{sheet_w-MARGIN/2-150:.1f}" y="{ty:.1f}" width="150" height="{TITLE_H:.1f}" fill="none" stroke="#111" stroke-width="0.7"/>')
    lines = [f"CLEMENTS {nstr} - CONCERT PEDAL HARP",
             f"{nstr} strings" + ("  (47 + 2 bass A0,B0)" if nstr == 49 else "  (baseline)"),
             "Projection: THIRD-ANGLE   build123d HLR",
             "Units: model (~8.86 mm/unit)",
             f"Scale {scale:.2f} px/unit"]
    for i, ln in enumerate(lines):
        P.append(f'<text x="{sheet_w-MARGIN/2-145:.1f}" y="{ty+10+i*10:.1f}" font-family="sans-serif" font-size="{6 if i else 7}">{ln}</text>')
    P.append("</svg>")
    open(out_path, "w").write("\n".join(P))
    return sheet_w, sheet_h

if __name__ == "__main__":
    bb = assembly.harp(49).bounding_box()
    scale = 150.0 / max(bb.size.X, bb.size.Y, bb.size.Z)   # shared scale for both plates
    for n, path in [(47, "clements47.svg"), (49, "clements49.svg")]:
        w, h = make_plate(n, scale, path)
        print(f"wrote {path}  ({w:.0f}x{h:.0f} mm)")
