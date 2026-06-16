import sys, os, math
sys.path.insert(0, "/home/clementsj/projects/clements49/build123d")
from clements49_params import STRINGS, N_STRINGS, SIGMA_T_N, UNIT_MM
sys.path.insert(0, "/home/clementsj/projects/clements49/build123d/parts")
from soundbox import soundbox

s = soundbox()
V_units = s.volume
V_mm3 = V_units * UNIT_MM**3
litres = V_mm3 / 1e6
print(f"PARAMETRIC soundbox volume:")
print(f"  V_units = {V_units:.1f} model-units^3")
print(f"  V_mm3   = {V_mm3:.1f} mm^3")
print(f"  litres  = {litres:.4f} L")

# --- Helmholtz: f = (c/2pi) sqrt(A/(V*Leff)) ---
c = 343000.0  # mm/s
print("\nHelmholtz A0 (back sound-holes NOT modeled; assume circular holes):")
for ndia, nholes in [(40.0,3),(50.0,3),(60.0,2)]:
    r = ndia/2.0
    A = nholes * math.pi * r*r  # mm^2
    # effective length: thin wall ~ flanged correction 1.7*r per hole; assume t small
    t = 8.0  # mm wood thickness assumption
    # combined area single equivalent
    Leff = t + 1.7*r  # flanged one side, approx
    f = (c/(2*math.pi))*math.sqrt(A/(V_mm3*Leff))
    print(f"  {nholes}x dia {ndia}mm (A={A:.0f}mm2, Leff~{Leff:.1f}mm): f0 ~ {f:.1f} Hz")

# --- Structural ---
tens = [x["tension_N"] for x in STRINGS if x.get("tension_N")]
print(f"\nN_STRINGS={N_STRINGS}  with tension={len(tens)}")
print(f"SIGMA_T_N = {SIGMA_T_N} N (sum) ; recomputed = {sum(tens):.1f} N")
print(f"per-string tension range: {min(tens):.2f} .. {max(tens):.2f} N ; mean {sum(tens)/len(tens):.2f}")

# rake: board->pin vector. rake angle relative to soundboard plane.
# Compute the string direction and the perpendicular(to soundboard)/in-plane split.
# Soundboard flat side is at Y=yflat (varies), board points roughly +Z up the box.
# Define rake = angle between string and the soundboard surface (its long axis ~ Z).
# Pull on soundboard: each string pulls along board->pin direction at its board anchor.
# Perp component = component along soundboard normal; in-plane = along board axis.
# Soundboard plane: flat face faces -Y (belly arcs +Y). Normal ~ -Y direction. Long axis ~ +Z.
perp_sum = 0.0   # along soundboard normal (Y)
inplane_sum = 0.0 # along board long axis (Z)
axial_sum = 0.0
rakes = []
for x in STRINGS:
    T = x.get("tension_N")
    if not T: continue
    b = x["board"]; p = x["pin"]
    v = [p[0]-b[0], p[1]-b[1], p[2]-b[2]]
    L = math.sqrt(sum(c*c for c in v))
    u = [c/L for c in v]
    # rake angle = angle between string and the soundboard long axis (Z)
    cosz = abs(u[2])
    rake = math.degrees(math.acos(max(-1,min(1,cosz))))
    rakes.append(rake)
    # perpendicular pull = T * |component along Y normal| (out of soundboard plane)
    perp_sum += abs(T*u[1])
    inplane_sum += abs(T*u[2])
    axial_sum += T

rakes.sort()
print(f"\nstring rake (angle from soundboard long axis Z), board->pin:")
print(f"  range {min(rakes):.1f} .. {max(rakes):.1f} deg ; mean {sum(rakes)/len(rakes):.1f} deg")
print(f"  quartiles ~ {rakes[len(rakes)//4]:.1f} / {rakes[len(rakes)//2]:.1f} / {rakes[3*len(rakes)//4]:.1f}")
print(f"\nLoads resolved at soundboard anchors (board->pin direction):")
print(f"  perpendicular (out-of-board, along Y normal) sum T*|uy| = {perp_sum:.1f} N")
print(f"  in-plane (along board axis Z)             sum T*|uz| = {inplane_sum:.1f} N")
print(f"  total tension scalar sum                              = {axial_sum:.1f} N")

# trimesh mesh volume
try:
    import importlib.util
    print("\n(mesh volume measured separately by system python3)")
except Exception as e:
    print(e)
