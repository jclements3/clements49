"""Stage B (build123d/conda env): loft world-3D section loops into a B-rep solid.
Usage: build123d/py loft_part.py <sections.json> <out.brep> [ruled 0|1]"""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *
data = json.load(open(sys.argv[1])); out = sys.argv[2]
ruled = bool(int(sys.argv[3])) if len(sys.argv) > 3 else True
faces = []
for pts in data["sections"]:
    try:
        w = Wire(Polyline(*[tuple(p) for p in pts], close=True))
        faces.append(Face(w))
    except Exception as e:
        pass
solid = loft(faces, ruled=ruled)
export_brep(solid, out)
bb = solid.bounding_box()
print(json.dumps({"sections": len(faces), "valid": solid.is_valid,
                  "volume": round(solid.volume, 1),
                  "bbox": [round(v, 1) for v in bb.size]}))
