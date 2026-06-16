"""Faithful, CLEAN third-angle plate straight from the mesh (plain venv; no build123d).

For each view, every frame body's triangles are projected to 2D and unioned (shapely)
so only the part's OUTER SILHOUETTE is stroked -- faithful to the real geometry with no
loft/facet seams. Strings are drawn as coloured lines (C red, F blue, others dark gray).

Layout matches the existing plates: FRONT | SIDE | REAR in a row (bottom-aligned, shared
Z), TOP above SIDE (shared Y axis -> column on the left in both), no border/labels, ~950px.

Run: .venv/bin/python build123d/recon/make_plate_silhouette.py [49|47]
Writes build123d/clements<N>.svg
"""
import sys, os, glob, json
import numpy as np, trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
BD = os.path.dirname(HERE)                       # build123d/
ROOT = os.path.dirname(BD)
SPLIT = os.path.join(HERE, "split")
STRING_SET = int(sys.argv[1]) if len(sys.argv) > 1 else 49

# view -> (right_dir, up_dir) in world coords; u=V.right, v=V.up
VIEWS = {
    "front": ((1, 0, 0), (0, 0, 1)),
    "side":  ((0, 1, 0), (0, 0, 1)),
    "rear":  ((-1, 0, 0), (0, 0, 1)),
    "top":   ((0, 1, 0), (1, 0, 0)),
}
GAP = 14.0
FIT_PX = 950.0
LETTERS = "ABCDEFG"   # A0,B0,C1,... -> letter = LETTERS[idx % 7]
COLOR = {"C": "rgb(216,0,0)", "F": "rgb(0,0,216)"}
COLOR_OTHER = "rgb(63,63,63)"


def proj_matrix(right, up):
    return np.column_stack([np.array(right, float), np.array(up, float)])  # (3,2)


def body_silhouette(mesh, P):
    """Return shapely geometry = union of all projected triangles (the part outline)."""
    V2 = mesh.vertices @ P
    tri = V2[mesh.faces]                          # (F,3,2)
    # drop near-degenerate triangles
    a = tri[:, 1] - tri[:, 0]; b = tri[:, 2] - tri[:, 0]
    area = np.abs(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])
    keep = area > 1e-9
    polys = [Polygon(t) for t in tri[keep]]
    return unary_union(polys)


def geom_to_paths(g):
    """shapely Polygon/MultiPolygon -> list of rings (each list of (u,v))."""
    rings = []
    geoms = g.geoms if g.geom_type == "MultiPolygon" else [g]
    for poly in geoms:
        if poly.is_empty:
            continue
        rings.append(list(poly.exterior.coords))
        for hole in poly.interiors:
            rings.append(list(hole.coords))
    return rings


def load_strings():
    d = json.load(open(os.path.join(BD, "params_strings.json")))
    out = []
    for s in d["strings"]:
        idx = s["idx"]
        if STRING_SET < 49 and idx < 2:           # 47-set drops the 2 bass extras
            continue
        letter = LETTERS[idx % 7]
        col = COLOR.get(letter, COLOR_OTHER)
        out.append((np.array(s["board_xyz"]), np.array(s["pin_xyz"]), col))
    return out


def build_view(name, bodies, strings):
    right, up = VIEWS[name]
    P = proj_matrix(right, up)
    rings = []                                     # (list-of-(u,v))
    for m in bodies:
        g = body_silhouette(m, P)
        rings += geom_to_paths(g)
    seg = [(b @ P, p @ P, c) for (b, p, c) in strings]   # projected string lines
    return rings, seg


def main():
    files = sorted(glob.glob(os.path.join(SPLIT, "body*.stl")))
    bodies = [trimesh.load(f) for f in files]
    strings = load_strings()

    views = {}
    allu = []; allv = []
    for name in VIEWS:
        rings, seg = build_view(name, bodies, strings)
        pts = np.array([p for r in rings for p in r] +
                       [tuple(b) for b, p, c in seg] + [tuple(p) for b, p, c in seg])
        views[name] = dict(rings=rings, seg=seg,
                           umin=pts[:, 0].min(), umax=pts[:, 0].max(),
                           vmin=pts[:, 1].min(), vmax=pts[:, 1].max())
    for V in views.values():
        V["w"] = V["umax"] - V["umin"]; V["h"] = V["vmax"] - V["vmin"]

    f, s, r, t = (views[k] for k in ("front", "side", "rear", "top"))
    fx = 0.0
    sx = fx + f["w"] + GAP
    rx = sx + s["w"] + GAP
    row_w = rx + r["w"]
    row_h = max(f["h"], s["h"], r["h"])
    top_h = t["h"]
    row_top = top_h + GAP
    row_bottom = row_top + row_h
    sheet_w, sheet_h = row_w, row_bottom
    px = FIT_PX / max(sheet_w, sheet_h)

    def emit(V, ox, oy):
        """Place view V with its (umin,vmax) corner at sheet (ox,oy); v flipped (page y-down)."""
        out = []
        for ring in V["rings"]:
            pts = " ".join(f"{ox + (u - V['umin']):.2f},{oy + (V['vmax'] - v):.2f}"
                           for u, v in ring)
            out.append(f'<polygon points="{pts}" fill="none" stroke="black" stroke-width="0.35"/>')
        for b, p, c in V["seg"]:
            out.append(f'<line x1="{ox + (b[0] - V["umin"]):.2f}" y1="{oy + (V["vmax"] - b[1]):.2f}" '
                       f'x2="{ox + (p[0] - V["umin"]):.2f}" y2="{oy + (V["vmax"] - p[1]):.2f}" '
                       f'stroke="{c}" stroke-width="0.35"/>')
        return out

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{sheet_w*px:.0f}" '
             f'height="{sheet_h*px:.0f}" viewBox="0 0 {sheet_w:.2f} {sheet_h:.2f}">']
    # row (bottom-aligned): each view's bottom at row_bottom
    parts += emit(f, fx, row_bottom - f["h"])
    parts += emit(s, sx, row_bottom - s["h"])
    parts += emit(r, rx, row_bottom - r["h"])
    # top above side, same x (shared Y axis), bottom of top at row_top
    parts += emit(t, sx, row_top - t["h"])
    parts.append("</svg>")

    out_path = os.path.join(BD, f"clements{STRING_SET}.svg")
    open(out_path, "w").write("\n".join(parts))
    print(f"wrote {out_path}  bodies={len(bodies)} strings={len(strings)} "
          f"sheet={sheet_w:.0f}x{sheet_h:.0f} -> {sheet_w*px:.0f}x{sheet_h*px:.0f}px")


if __name__ == "__main__":
    main()
