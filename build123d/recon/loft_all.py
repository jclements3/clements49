import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *
parts = sys.argv[1:]
RES = open("/tmp/loft_results.txt", "w")
def emit(d):
    line = json.dumps(d); print(line, flush=True); RES.write(line + "\n"); RES.flush()
for p in parts:
    emit({"part": p, "status": "start"})
    data = json.load(open(f"/tmp/sec_{p}.json"))
    faces = []
    for pts in data["sections"]:
        try:
            faces.append(Face(Wire(Polyline(*[tuple(q) for q in pts], close=True))))
        except Exception:
            pass
    try:
        solid = loft(faces, ruled=True)
        export_brep(solid, f"/tmp/{p}.brep")
        bb = solid.bounding_box()
        emit({"part": p, "faces": len(faces), "valid": solid.is_valid,
              "vol": round(solid.volume, 1), "bbox": [round(v, 1) for v in bb.size]})
    except Exception as e:
        emit({"part": p, "error": str(e)[:120]})
emit({"status": "all_done"})
