"""Split the curated whole-frame export (blender/clements49.stl) into per-body STLs.

The user hand-selects the frame in Blender and exports it via the Ctrl+Shift+E hotkey
as one merged STL. This splits it into connected-component bodies, labels each by the
nearest matching part-family (from cad/parts_mesh/*.stl bboxes), and writes
recon/split/body<NN>_<family>.stl -- the input for make_plate_silhouette.py and lofting.

Run (plain venv): .venv/bin/python build123d/recon/split_frame.py [path-to-frame.stl]
Geometry output is licensed-derived -> gitignored.
"""
import sys, os, glob
import numpy as np, trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "blender", "clements49.stl")
OUT = os.path.join(HERE, "split")
FAM = os.path.join(ROOT, "cad", "parts_mesh")

fam = {}
for f in glob.glob(os.path.join(FAM, "*.stl")):
    n = os.path.basename(f)[:-4]
    if n.startswith("hardware") or n == "clements49":
        continue
    fm = trimesh.load(f); lo, hi = fm.bounds
    fam[n] = ((lo + hi) / 2, hi - lo)

def match(b):
    lo, hi = b.bounds; c = (lo + hi) / 2; ext = hi - lo
    return min(fam, key=lambda n: np.linalg.norm(c - fam[n][0]) + 0.5 * np.linalg.norm(ext - fam[n][1]))

os.makedirs(OUT, exist_ok=True)
for old in glob.glob(os.path.join(OUT, "body*.stl")):
    os.remove(old)
m = trimesh.load(SRC)
bodies = m.split(only_watertight=False)
for i, b in enumerate(bodies):
    name = match(b)
    b.export(os.path.join(OUT, f"body{i:02d}_{name}.stl"))
print(f"split {os.path.basename(SRC)} -> {len(bodies)} bodies in {OUT}")
