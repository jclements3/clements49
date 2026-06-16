"""Clements 49 — shared parameters for the parametric build123d harp.

UNITS: Blender model units (the clements49.blend native units). 1 unit ~= 8.86 mm
(model is ~216 units / ~1915 mm tall). All geometry is built in these world units so
the parametric harp overlays the original model. Multiply by UNIT_MM for millimetres.

This is the single source of truth that drives the parameterized design: change the
string set / dims here and the parts follow. Reverse-engineered from clements49.blend.
"""
import json, os

PROJ = os.path.expanduser("~/projects/clements49")
HERE = os.path.dirname(os.path.abspath(__file__))
UNIT_MM = 8.8598

def _load(p):
    with open(p) as f:
        return json.load(f)

# --- 49-string schedule: physics (note/f0/tension) + geometry (board/pin, model units) ---
_geom = _load(f"{HERE}/params_strings.json")["strings"]          # 49 board/pin xyz (measured + 2 extrap)
try:
    _sched = _load(f"{PROJ}/analysis/string_schedule.json")["strings"]   # physical schedule (A0..G7)
except Exception:
    _sched = []

STRINGS = []
for i in range(len(_geom)):
    g = _geom[i]
    s = _sched[i] if i < len(_sched) else {}
    STRINGS.append({
        "idx": i,
        "note": f"{s.get('note','')}{s.get('octave','')}",
        "f0_hz": s.get("f0_hz"),
        "tension_N": s.get("tension_N"),
        "board": g["board_xyz"],   # [x,y,z] soundboard end (model units)
        "pin":   g["pin_xyz"],     # [x,y,z] tuning-pin / neck end
    })
N_STRINGS = len(STRINGS)                                          # 49
SIGMA_T_N = round(sum(x["tension_N"] for x in STRINGS if x.get("tension_N")), 1)

# --- SOUNDBOX body: straight-sided half-cone (D cross-section). Measured caps (model units). ---
# flat soundboard side at Y=yflat, arc belly to +Y, width W on X centred xc, at world z.
SOUNDBOX_CAPS = {
    "bass":   dict(z=15.9,  xc=0.3, yflat=-32.4, W=49.3, D=30.1),
    "treble": dict(z=151.9, xc=0.3, yflat=52.1,  W=14.0, D=8.1),
}

# --- per-part bounding boxes (model units) measured from the exported STLs ---
# dims=[X,Y,Z]; z=[min,max]. Part agents should re-measure their own STL for exact min/max.
PART_BBOX = {
    "soundbox_body": dict(dims=[60.8, 92.9, 136.8], z=[15.5, 152.3]),
    "soundboard":    dict(dims=[58.3, 84.1, 135.8], z=[16.6, 152.4]),
    "back_staves":   dict(dims=[2.4,  70.4, 115.9], z=[29.3, 145.2]),
    "neck":          dict(dims=[14.5, 97.7, 70.7],  z=[140.9, 211.6]),
    "pillar":        dict(dims=[48.4, 32.5, 201.0], z=[15.5, 216.4]),
    "base":          dict(dims=[60.2, 61.2, 15.4],  z=[0.0, 15.5]),
    "pedals":        dict(dims=[72.2, 32.3, 2.7],   z=[12.3, 15.0]),
    "strings":       dict(dims=[2.7,  79.4, 187.5], z=[19.3, 206.9]),
}

# overall model envelope (model units)
ENVELOPE = dict(x=[-62.6, 62.6], y=[-36.1, 60.3], z=[0.0, 216.5])

# STL reference meshes (for overlay / per-part measurement)
STL_DIR = f"{HERE}/stl"

if __name__ == "__main__":
    print(f"N_STRINGS={N_STRINGS}  SIGMA_T_N={SIGMA_T_N} N (model-unit geometry, mm via *{UNIT_MM})")
    print("bass string", STRINGS[0]["note"], STRINGS[0]["board"], "-> treble", STRINGS[-1]["note"], STRINGS[-1]["board"])
