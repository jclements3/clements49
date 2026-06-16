"""Regenerate the faithful B-rep parts from the exported meshes per recon/manifest.json.

Two-stage (env-isolated):
  slice_part.py runs in the PLAIN venv (trimesh/numpy; conda libs break numpy);
  the loft runs here under build123d/py (needs the conda libexpat fix).

Usage:  build123d/py recon/build_recon.py
Outputs recon/brep/<blend>.brep + recon/sections/sec_<blend>.json, prints verify table.
Requires the per-family STLs in cad/parts_mesh/ (exported from the blend; see README)."""
import sys, os, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from build123d import *

VENV_PY = os.path.join(os.path.dirname(os.path.dirname(HERE)), ".venv", "bin", "python")
MESH = os.path.join(os.path.dirname(os.path.dirname(HERE)), "cad", "parts_mesh")
M = json.load(open(os.path.join(HERE, "manifest.json")))

for part in M["parts"]:
    b = part["blend"]; stl = os.path.join(MESH, b + ".stl")
    secj = os.path.join(HERE, "sections", f"sec_{b}.json")
    # stage A: slice (plain venv)
    subprocess.run([VENV_PY, os.path.join(HERE, "slice_part.py"), stl,
                    str(part["axis"]), str(part["N"]), secj, str(part["M"])],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # stage B: loft (here)
    data = json.load(open(secj))
    faces = []
    for pts in data["sections"]:
        try:
            faces.append(Face(Wire(Polyline(*[tuple(q) for q in pts], close=True))))
        except Exception:
            pass
    solid = loft(faces, ruled=True)
    export_brep(solid, os.path.join(HERE, "brep", b + ".brep"))
    bb = solid.bounding_box()
    print(f"{part['function']:12s} {b:24s} valid={solid.is_valid} "
          f"vol={solid.volume:9.1f} bbox={[round(v,1) for v in bb.size]}")
