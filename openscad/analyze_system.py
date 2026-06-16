#!/usr/bin/env python3
"""Reusable headless Blender analysis for Clements 49 harp systems.

Run ONLY via the bundled blender 5.x python:
  /home/clementsj/blender5/blender -b <blend> --python analyze_system.py -- <system>

For each member object of the requested system it:
  - evaluates the mesh through its modifier stack (SubSurf etc.)
  - transforms verts to WORLD space (model units) via matrix_world
  - computes AABB min/max/dims, centroid, base + evaluated face/vert counts
  - computes principal axes via eigen-decomposition of the vertex covariance
    (ordered longest -> shortest: e0,e1,e2) and OBB extents on each axis
  - slices ~7 cross-section stations along the LONGEST axis e0, projecting each
    slab onto (e1,e2) and taking the 2D convex hull (monotone chain, numpy only)
  - writes <objname>.json into openscad/analysis/

The JSON carries principal_axes (rows e0,e1,e2) and centroid so OpenSCAD can
rebuild: local [u,v,w] -> world columns e1,e2,e0 then translate by centroid.
"""
import bpy
import sys
import os
import json
import numpy as np

# --- system -> object names. Extend as neck/pillar/base/strings follow. ---
SYSTEMS = {
    "soundbox": [
        "harp_big_side_pivot",
        "harp_white_wood_01",
        "harp_white_wood_02",
        "harp_wood_plank",
        "harp_wood_inside",
        # harp_wood_inside1 REMOVED: z 174.6-189.8, above soundboard top -> NECK piece.
    ],
    # "neck": [..., "harp_wood_inside1"],  # reclassified here from soundbox
    # "pillar": [...],
    # "base": [...],
    # "strings": [...],
}

OUT_DIR = "/home/clementsj/projects/clements49/openscad/analysis"
N_STATIONS = 7


def get_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    return argv[0] if argv else "soundbox"


def convex_hull_2d(pts):
    """Andrew's monotone chain. pts: (N,2). Returns ordered hull (M,2) CCW."""
    if len(pts) == 0:
        return pts
    # unique + lexsort by (x, y)
    pts = np.unique(pts, axis=0)
    if len(pts) <= 2:
        return pts
    order = np.lexsort((pts[:, 1], pts[:, 0]))
    p = pts[order]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for pt in p:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], pt) <= 0:
            lower.pop()
        lower.append(pt)
    upper = []
    for pt in p[::-1]:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], pt) <= 0:
            upper.pop()
        upper.append(pt)
    hull = np.array(lower[:-1] + upper[:-1])
    return hull


def world_vertices(obj, depsgraph):
    """Evaluated mesh verts in world space (model units)."""
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    mw = np.array(eval_obj.matrix_world)  # 4x4
    n = len(mesh.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    mesh.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    homog = np.column_stack([co, np.ones(n)])
    world = (homog @ mw.T)[:, :3]
    eval_faces = len(mesh.polygons)
    eval_obj.to_mesh_clear()
    return world, eval_faces


def analyze_object(obj, depsgraph):
    verts, eval_faces = world_vertices(obj, depsgraph)

    base_mesh = obj.data
    base_verts = len(base_mesh.vertices)
    base_faces = len(base_mesh.polygons)

    vmin = verts.min(axis=0)
    vmax = verts.max(axis=0)
    dims = vmax - vmin
    centroid = verts.mean(axis=0)

    # principal axes via covariance eigen-decomposition
    rel = verts - centroid
    cov = np.cov(rel, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)          # ascending eigenvalues
    order = np.argsort(evals)[::-1]             # longest -> shortest
    axes = evecs[:, order].T                    # rows e0,e1,e2
    # deterministic sign: make largest-magnitude component positive
    for i in range(3):
        k = np.argmax(np.abs(axes[i]))
        if axes[i, k] < 0:
            axes[i] = -axes[i]

    # OBB extents = min/max of rel projected on each axis
    proj = rel @ axes.T                          # (N,3) columns -> e0,e1,e2
    obb_min = proj.min(axis=0)
    obb_max = proj.max(axis=0)
    obb_dims = obb_max - obb_min

    # cross-sections along longest axis e0
    s0 = proj[:, 0]
    s_lo, s_hi = s0.min(), s0.max()
    stations = np.linspace(s_lo, s_hi, N_STATIONS)
    span = s_hi - s_lo
    half_slab = (span / (N_STATIONS - 1)) * 0.6 if span > 0 else 1.0

    sections = []
    for s in stations:
        mask = np.abs(s0 - s) <= half_slab
        slab = proj[mask]
        if len(slab) < 3:
            # widen once if too sparse
            mask = np.abs(s0 - s) <= half_slab * 2.0
            slab = proj[mask]
        outline = slab[:, 1:3] if len(slab) else np.empty((0, 2))
        hull = convex_hull_2d(outline)
        world_pos = centroid + s * axes[0]
        sections.append({
            "s": float(s),
            "world_pos": [float(x) for x in world_pos],
            "n_pts": int(len(hull)),
            "outline_e1e2": [[float(a), float(b)] for a, b in hull],
        })

    return {
        "name": obj.name,
        "base_verts": int(base_verts),
        "base_faces": int(base_faces),
        "eval_verts": int(len(verts)),
        "eval_faces": int(eval_faces),
        "bbox_min": [float(x) for x in vmin],
        "bbox_max": [float(x) for x in vmax],
        "dims": [float(x) for x in dims],
        "centroid": [float(x) for x in centroid],
        "principal_axes": [[float(v) for v in row] for row in axes],
        "obb_min": [float(x) for x in obb_min],
        "obb_max": [float(x) for x in obb_max],
        "obb_dims": [float(x) for x in obb_dims],
        "n_sections": len(sections),
        "sections": sections,
    }


def main():
    system = get_args()
    if system not in SYSTEMS:
        print(f"[analyze_system] unknown system '{system}'. Known: {list(SYSTEMS)}")
        sys.exit(1)
    names = SYSTEMS[system]
    os.makedirs(OUT_DIR, exist_ok=True)
    depsgraph = bpy.context.evaluated_depsgraph_get()

    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            print(f"[analyze_system] WARNING: object '{name}' not found, skipping")
            continue
        data = analyze_object(obj, depsgraph)
        out = os.path.join(OUT_DIR, f"{name}.json")
        with open(out, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[analyze_system] wrote {out}  dims={[round(d,2) for d in data['dims']]} "
              f"base_f={data['base_faces']} eval_f={data['eval_faces']} "
              f"sections={data['n_sections']}")


if __name__ == "__main__":
    main()
