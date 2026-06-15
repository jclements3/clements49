#!/usr/bin/env python3
"""Custom hidden-line-removal (HLR) vector drawing of the harp mesh.

Approach (no GPU / embree needed):
  1. Rotate mesh into a view frame: (vx,vy)=drawing plane, vz=depth toward camera.
  2. Rasterise a FACE-ID buffer with the painter's algorithm (far->near) using
     matplotlib/Agg -> nearest face id per pixel = the occlusion buffer.
  3. Extract FEATURE edges: silhouette (front/back normal flip) + crease
     (dihedral > thresh) + boundary (edge used by one face).
  4. For each feature edge, sample along it; a sample is VISIBLE if its depth is
     >= the depth of the frontmost face at that pixel (minus a bias), else HIDDEN.
  5. Emit visible runs as solid polylines, hidden runs as dashed -> SVG.

Views: front (look +y), rear (look -y), side (look +x), top (look -z).
Run:  python hlr.py debug <view>     -> single-view /tmp/hlr_<view>.{svg,png}
      python hlr.py plate            -> renders/clements49_plate.svg
"""
import sys, numpy as np, trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

MESH = '/home/clementsj/projects/clements49/cad/reference/whole_harp.stl'
CREASE_DEG = 40.0
TARGET_PX_H = 1200          # raster height for the occlusion buffer
SAMPLES     = 28            # fixed samples per edge (was scaling to longest edge -> OOM)
USE_BOUNDARY = False        # boundary edges are noisy on this non-watertight art mesh

# View frames: 3x3 rows map model xyz -> (vx, vy, vz=depth toward camera).
VIEWS = {
    'front': np.array([[ 1,0,0],[0,0,1],[0, 1,0]]),   # see (x,z), depth +y (string side)
    'rear' : np.array([[-1,0,0],[0,0,1],[0,-1,0]]),   # see (-x,z), depth -y (back)
    'side' : np.array([[ 0,1,0],[0,0,1],[1, 0,0]]),   # see (y,z), depth +x
    'top'  : np.array([[ 1,0,0],[0,1,0],[0, 0,1]]),   # see (x,y), depth +z
}

_mesh = None
def mesh():
    global _mesh
    if _mesh is None:
        _mesh = trimesh.load(MESH)
    return _mesh

def feature_edges(m, R):
    """Return (K,2) vertex-index edges that are silhouette|crease|boundary."""
    fn_v = m.face_normals @ R.T            # face normals in view frame
    nz = fn_v[:, 2]
    fa  = m.face_adjacency                 # (A,2) face pairs
    fae = m.face_adjacency_edges           # (A,2) shared edge verts
    ang = m.face_adjacency_angles          # (A,) dihedral
    sil   = (nz[fa[:, 0]] * nz[fa[:, 1]]) < 0
    crease = ang > np.radians(CREASE_DEG)
    adj_e = fae[sil | crease]
    E = adj_e
    if USE_BOUNDARY:
        es = m.edges_sorted
        uniq, counts = np.unique(es, axis=0, return_counts=True)
        bnd = uniq[counts == 1]
        if len(bnd):
            E = np.vstack([adj_e, bnd])
    E = np.unique(np.sort(E, axis=1), axis=0)
    return E

def id_buffer(V, F, fdepth, minx, maxx, miny, maxy, W, H):
    """Painter's-algorithm face-id raster. Returns (H,W) int32 id (-1 bg)."""
    order = np.argsort(fdepth)             # far first, near drawn last (on top)
    polys = V[F[order]][:, :, :2]          # (F,3,2)
    ids   = order.astype(np.int64)         # face id drawn = order[k]
    # encode id+1 into 24-bit rgb
    v = ids + 1
    rgb = np.stack([(v >> 16) & 255, (v >> 8) & 255, v & 255], axis=1) / 255.0
    fig = plt.figure(figsize=(W/100.0, H/100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy)
    pc = PolyCollection(polys, facecolors=rgb, edgecolors='none',
                        antialiaseds=False, linewidths=0)
    ax.add_collection(pc)
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].astype(np.int64)
    plt.close(fig)
    # resize buffer to (H,W) if Agg gave a different size
    bh, bw = buf.shape[:2]
    idbuf = (buf[:, :, 0] << 16) | (buf[:, :, 1] << 8) | buf[:, :, 2]
    idbuf = idbuf - 1                       # -1 = background
    return idbuf, bw, bh

def view_segments(view):
    """Return (solids, hiddens, bbox) for a view; polylines in (vx,vy) mm."""
    m = mesh(); R = VIEWS[view]
    V = m.vertices @ R.T
    F = m.faces
    fdepth = V[F][:, :, 2].mean(axis=1)
    fn_v = m.face_normals @ R.T
    minx, miny = V[:, 0].min(), V[:, 1].min()
    maxx, maxy = V[:, 0].max(), V[:, 1].max()
    zr = V[:, 2].max() - V[:, 2].min()
    bias = 0.006 * zr
    H = TARGET_PX_H
    W = int(round(H * (maxx - minx) / (maxy - miny)))
    idbuf, bw, bh = id_buffer(V, F, fdepth, minx, maxx, miny, maxy, W, H)

    E = feature_edges(m, R)
    print(f"  {view}: feature edges = {len(E)}")
    P0 = V[E[:, 0]]; P1 = V[E[:, 1]]
    S = SAMPLES
    ts = np.linspace(0, 1, S)
    P = P0[:, None, :] * (1 - ts)[None, :, None] + P1[:, None, :] * ts[None, :, None]  # (K,S,3)
    px = ((P[:, :, 0] - minx) / (maxx - minx) * (bw - 1)).astype(int)
    py = ((maxy - P[:, :, 1]) / (maxy - miny) * (bh - 1)).astype(int)
    px = np.clip(px, 0, bw - 1); py = np.clip(py, 0, bh - 1)
    fid = idbuf[py, px]                                            # (K,S)
    # depth of frontmost face at each sample
    valid = fid >= 0
    fid_c = np.clip(fid, 0, len(F) - 1)
    n = fn_v[fid_c]                                               # (K,S,3)
    v0 = V[F[fid_c][:, :, 0]]                                     # (K,S,3) first vtx of that face
    nz = n[:, :, 2]
    safe = np.abs(nz) > 1e-6
    num = (n[:, :, 0] * v0[:, :, 0] + n[:, :, 1] * v0[:, :, 1] + n[:, :, 2] * v0[:, :, 2]
           - n[:, :, 0] * P[:, :, 0] - n[:, :, 1] * P[:, :, 1])
    face_z = np.where(safe, num / np.where(safe, nz, 1.0), -1e18)
    face_z = np.where(valid, face_z, -1e18)                       # bg -> -inf (visible)
    visible = P[:, :, 2] >= (face_z - bias)                       # (K,S) bool

    solids, hiddens = [], []
    allv = visible.all(axis=1)
    allh = (~visible).all(axis=1)
    ep = P[:, [0, -1], :2]                       # endpoints only (K,2,2)
    for k in np.where(allv)[0]:                   # fully visible -> 2-point line
        solids.append(ep[k].tolist())
    for k in np.where(allh)[0]:                   # fully hidden -> 2-point line
        hiddens.append(ep[k].tolist())
    mixed = np.where(~(allv | allh))[0]           # crosses occlusion -> subdivide
    for k in mixed:
        vis = visible[k]; pts = P[k, :, :2]; start = 0
        for i in range(1, S + 1):
            if i == S or vis[i] != vis[start]:
                seg = pts[start:i + (0 if i == S else 1)]
                if len(seg) >= 2:
                    (solids if vis[start] else hiddens).append(seg.tolist())
                start = i
    return solids, hiddens, (minx, miny, maxx, maxy)

def svg_polys(polys, stroke, width, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    out = []
    for seg in polys:
        pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in seg)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{stroke}" '
                   f'stroke-width="{width}"{d} stroke-linecap="round"/>')
    return "\n".join(out)

def emit_view_svg(view, path):
    sol, hid, (minx, miny, maxx, maxy) = view_segments(view)
    w = maxx - minx; h = maxy - miny
    # flip y for SVG (y-down): y' = maxy - y
    def fl(polys): return [[[x, maxy - y] for x, y in seg] for seg in polys]
    body = (svg_polys(fl(hid), "#888", 1.2, dash="6,4") + "\n" +
            svg_polys(fl(sol), "#111", 1.6))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}mm" '
           f'height="{h:.0f}mm" viewBox="{minx:.1f} 0 {w:.1f} {h:.1f}">\n'
           f'<rect x="{minx:.1f}" y="0" width="{w:.1f}" height="{h:.1f}" fill="white"/>\n'
           f'{body}\n</svg>\n')
    open(path, 'w').write(svg)
    return len(sol), len(hid)

def _xform(polys, sx, sy_top, vminx, vmaxy):
    """Map view-2D (vx,vy up) polylines to sheet coords (y-down)."""
    return [[[sx + (x - vminx), sy_top + (vmaxy - y)] for x, y in seg] for seg in polys]

def build_plate(path):
    M, GAP, LBL = 120.0, 150.0, 70.0      # margin, gap, label band (mm)
    SCALE = 10                            # print scale 1:SCALE (geometry stays real mm)
    data = {}
    for v in ('front', 'side', 'rear', 'top'):
        sol, hid, bb = view_segments(v)
        data[v] = (sol, hid, bb)
    def wh(v):
        x0, y0, x1, y1 = data[v][2]; return x1 - x0, y1 - y0
    fw, fh = wh('front'); sw, sh = wh('side'); rw, rh = wh('rear'); tw, th = wh('top')
    rowH = max(fh, sh, rh)
    # x positions of the three row views
    fsx = M
    ssx = fsx + fw + GAP
    rsx = ssx + sw + GAP
    sheet_w = rsx + rw + M
    # top view above the side view, centred on side
    top_sy = M
    row_top = top_sy + th + LBL + GAP
    row_bot = row_top + rowH
    side_cx = ssx + sw / 2.0
    tsx = side_cx - tw / 2.0
    title_h = 230.0
    sheet_h = row_bot + LBL + GAP + title_h + M

    def bare(polys):   # bare polylines; stroke style comes from the enclosing <g>
        return "\n".join('<polyline points="%s"/>'
                         % " ".join("%.1f,%.1f" % (x, y) for x, y in seg) for seg in polys)

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{sheet_w/SCALE:.2f}mm" '
             f'height="{sheet_h/SCALE:.2f}mm" viewBox="0 0 {sheet_w:.1f} {sheet_h:.1f}">',
             f'<!-- viewBox units = real mm; width/height = paper mm at 1:{SCALE} (full size / {SCALE}) -->',
             f'<rect x="0" y="0" width="{sheet_w:.1f}" height="{sheet_h:.1f}" fill="white"/>',
             f'<rect x="{M/2:.1f}" y="{M/2:.1f}" width="{sheet_w-M:.1f}" height="{sheet_h-M:.1f}" '
             f'fill="none" stroke="#111" stroke-width="3"/>']
    placed = [('front', fsx, row_top), ('side', ssx, row_top),
              ('rear', rsx, row_top), ('top', tsx, top_sy)]
    labels, sol_all, hid_all = [], [], []
    for v, sx, sy in placed:
        sol, hid, (x0, y0, x1, y1) = data[v]
        hid_all += _xform(hid, sx, sy, x0, y1)
        sol_all += _xform(sol, sx, sy, x0, y1)
        w, h = (x1 - x0), (y1 - y0)
        labels.append((sx + w / 2.0, sy + h + LBL * 0.6, v.upper() + " VIEW"))
    parts.append('<g fill="none" stroke="#999" stroke-width="1.4" stroke-dasharray="7,5" '
                 'stroke-linecap="round">')
    parts.append(bare(hid_all)); parts.append('</g>')
    parts.append('<g fill="none" stroke="#111" stroke-width="1.8" stroke-linecap="round">')
    parts.append(bare(sol_all)); parts.append('</g>')
    for cx, cy, txt in labels:
        parts.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-family="sans-serif" '
                     f'font-size="46" text-anchor="middle" fill="#111">{txt}</text>')
    # title block (bottom-right)
    tbw, tbh = 760.0, title_h
    tbx, tby = sheet_w - M / 2 - tbw, sheet_h - M / 2 - tbh
    parts.append(f'<rect x="{tbx:.1f}" y="{tby:.1f}" width="{tbw:.1f}" height="{tbh:.1f}" '
                 f'fill="none" stroke="#111" stroke-width="3"/>')
    lines = ["CLEMENTS 49  —  CONCERT PEDAL HARP",
             "Base geometry: TurboSquid reference model",
             "Projection: THIRD-ANGLE     Units: mm",
             "Views: hidden-line removed (visible solid / hidden dashed)",
             f"Drawn: 2026-06-15        SCALE 1:{SCALE}  (verify against bar)"]
    for i, ln in enumerate(lines):
        fs = 40 if i == 0 else 30
        parts.append(f'<text x="{tbx+20:.1f}" y="{tby+50+i*38:.1f}" font-family="sans-serif" '
                     f'font-size="{fs}" fill="#111">{ln}</text>')
    # graphic scale bar (real mm in the viewBox -> scales with the drawing)
    bar_len, seg, bar_h = 1000.0, 100.0, 34.0
    bx0 = M + 80.0
    by = tby + tbh * 0.42
    parts.append(f'<text x="{bx0:.1f}" y="{by-22:.1f}" font-family="sans-serif" '
                 f'font-size="40" fill="#111">SCALE 1:{SCALE}</text>')
    for i in range(int(bar_len / seg)):
        fillc = "#111" if i % 2 == 0 else "white"
        parts.append(f'<rect x="{bx0+i*seg:.1f}" y="{by:.1f}" width="{seg:.1f}" '
                     f'height="{bar_h:.1f}" fill="{fillc}" stroke="#111" stroke-width="1.5"/>')
    parts.append(f'<rect x="{bx0:.1f}" y="{by:.1f}" width="{bar_len:.1f}" height="{bar_h:.1f}" '
                 f'fill="none" stroke="#111" stroke-width="2.5"/>')
    for mmv in (0, 500, 1000):
        parts.append(f'<text x="{bx0+mmv:.1f}" y="{by+bar_h+38:.1f}" font-family="sans-serif" '
                     f'font-size="30" text-anchor="middle" fill="#111">{mmv}</text>')
    parts.append(f'<text x="{bx0+bar_len+30:.1f}" y="{by+bar_h+38:.1f}" font-family="sans-serif" '
                 f'font-size="30" fill="#111">mm (full size)</text>')
    parts.append('</svg>')
    open(path, 'w').write("\n".join(parts))
    print(f"plate -> {path}  ({sheet_w:.0f}x{sheet_h:.0f} mm)")

if __name__ == '__main__':
    if sys.argv[1] == 'debug':
        v = sys.argv[2]
        ns, nh = emit_view_svg(v, f'/tmp/hlr_{v}.svg')
        print(f"{v}: solid_polys={ns} hidden_polys={nh} -> /tmp/hlr_{v}.svg")
    elif sys.argv[1] == 'plate':
        build_plate('/home/clementsj/projects/clements49/renders/clements49_plate.svg')
