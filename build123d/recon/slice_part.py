"""Stage A (plain venv, no conda libs): slice a mesh into world-3D section loops.

Usage: python slice_part.py <stl> <axis 0|1|2|pca> <N> <out.json> [simplify_pts]

Robust to OPEN shells: extracts every polyline in each section (not just closed
loops), closes open ones, and keeps the largest-area polyline per station.
Writes {"axis":.., "sections":[[[x,y,z],...], ...]} (world coords, one loop/station)."""
import sys, json, numpy as np, trimesh

stl, axis_arg, N, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
SIMP = int(sys.argv[5]) if len(sys.argv) > 5 else 28
m = trimesh.load(stl)
lo, hi = m.bounds

if axis_arg == "pca":
    v = m.vertices - m.vertices.mean(0)
    _, _, V = np.linalg.svd(v, full_matrices=False)
    normal = V[0]
    t = v @ normal
    cmin, cmax = t.min(), t.max(); base = m.vertices.mean(0)
    origin = lambda c: base + c * normal
else:
    axis = int(axis_arg); normal = np.eye(3)[axis]
    cmin, cmax = lo[axis], hi[axis]
    origin = lambda c: normal * c

# orthonormal in-plane basis (u,w) for 2D area computation
nrm = normal / np.linalg.norm(normal)
ref = np.array([1.0, 0, 0]) if abs(nrm[0]) < 0.9 else np.array([0, 1.0, 0])
u = np.cross(nrm, ref); u /= np.linalg.norm(u); w = np.cross(nrm, u)

def polylines(sec):
    """List of (N,3) world polylines from a Path3D section (open or closed)."""
    out = []
    for e in sec.entities:
        try:
            pts = sec.vertices[e.points]
            if len(pts) >= 2:
                out.append(np.asarray(pts, float))
        except Exception:
            pass
    return out

def area2d(P):
    x = P @ u; y = P @ w
    return abs(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)) / 2

def resample(P, M):
    """Arc-length resample a closed loop to exactly M points, CCW, consistent start.

    Equal vertex count + consistent winding/start across stations makes the
    downstream ThruSections loft robust (mismatch is what makes it fail)."""
    P = np.asarray(P, float)
    if np.linalg.norm(P[0] - P[-1]) > 1e-9:
        P = np.vstack([P, P[0]])
    # enforce CCW in the (u,w) plane
    if area2d_signed(P) < 0:
        P = P[::-1]
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)]); total = s[-1]
    if total < 1e-9:
        return None
    targ = np.linspace(0, total, M, endpoint=False)
    out = np.empty((M, 3))
    for d in range(3):
        out[:, d] = np.interp(targ, s, P[:, d])
    # rotate so the start vertex is the one with max projection on +u (stable anchor)
    a = (out @ u)
    j = int(np.argmax(a))
    return np.roll(out, -j, axis=0)

def area2d_signed(P):
    x = P @ u; y = P @ w
    return np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y) / 2

M_RESAMPLE = SIMP   # reuse the 5th arg as the fixed resample count
sections = []
for i in range(N):
    c = cmin + (i + 0.5) / N * (cmax - cmin)
    sec = m.section(plane_origin=origin(c), plane_normal=normal)
    if sec is None:
        continue
    pls = polylines(sec)
    if not pls:
        continue
    best = max(pls, key=area2d)
    if np.linalg.norm(best[0] - best[-1]) > 1e-6:      # close open polyline
        best = np.vstack([best, best[0]])
    rs = resample(best, M_RESAMPLE)
    if rs is None:
        continue
    pts = rs
    if len(pts) < 3:
        continue
    sections.append([[float(x) for x in p] for p in pts])
json.dump({"axis": axis_arg, "n": len(sections), "sections": sections}, open(out, "w"))
print("sliced", stl.split("/")[-1], "->", len(sections), "sections")
