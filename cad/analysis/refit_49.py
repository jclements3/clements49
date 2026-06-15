#!/usr/bin/env python3
"""Refit the 49-string set to A0..G7 (both extra strings in the bass) and
recompute the structural load basis on the actual re-anchored 49-pin line.

Re-anchor rule: the measured anchor endpoints in params.scad are the ORIGINAL
47 strings = C1 (bass) .. G7 (treble). In the A0..G7 set these are idx 2 and
idx 48. We pin the measured endpoints there and linearly extrapolate idx 0,1
(A0,B0) below the bass end -> the neck/board lengthen at the bass corner.
"""
import json, math, csv, os

D = os.path.dirname(os.path.abspath(__file__))

# ---- measured anchors (from params.scad, 47-string source mesh) ----
pin_bass_meas    = (-215.67, 20.84, 1802.06)   # = C1 (idx 2)
pin_treble_meas  = ( 476.15, 20.84, 1404.38)   # = G7 (idx 48)
board_bass_meas  = (-204.47,  1.88,  186.31)   # = C1 (idx 2)
board_treble_meas= ( 441.70,  1.88, 1232.23)   # = G7 (idx 48)
pillar_top       = (-303.11, 54.00, 1859.75)
pillar_bottom    = (-340.26,  1.56,  155.61)

ORIG_BASS_IDX, ORIG_TREBLE_IDX = 2, 48   # C1, G7 in the A0..G7 indexing

# ---- spacing law (params.scad section 7) ----
s_neck = 10.0
s_b_treble, s_b_bass, s_b_exp = 6.5, 24.0, 0.85
N = 49

def s_board(i):
    return s_b_treble + (s_b_bass - s_b_treble) * ((N - 1 - i) / (N - 1)) ** s_b_exp

def board_cum(i):
    c = 0.0
    for j in range(1, i + 1):
        c += (s_board(j) + s_board(j - 1)) / 2.0
    return c

def neck_cum(i):
    return i * s_neck

bc2, bc48 = board_cum(ORIG_BASS_IDX), board_cum(ORIG_TREBLE_IDX)
nc2, nc48 = neck_cum(ORIG_BASS_IDX), neck_cum(ORIG_TREBLE_IDX)

def t_board(i): return (board_cum(i) - bc2) / (bc48 - bc2)
def t_neck(i):  return (neck_cum(i) - nc2) / (nc48 - nc2)

def lerp3(a, b, t): return tuple(a[k] + (b[k] - a[k]) * t for k in range(3))
def sub(a, b):      return tuple(a[k] - b[k] for k in range(3))
def norm(v):        return math.sqrt(sum(c * c for c in v))
def unit(v):
    n = norm(v); return tuple(c / n for c in v)
def dot(a, b):      return sum(a[k] * b[k] for k in range(3))

def pin_pos(i):   return lerp3(pin_bass_meas,   pin_treble_meas,   t_neck(i))
def board_pos(i): return lerp3(board_bass_meas, board_treble_meas, t_board(i))

# ---------------------------------------------------------------------------
# 1. New schedule A0..G7  (drop A7, add A0 below B0)
# ---------------------------------------------------------------------------
old = json.load(open(os.path.join(D, "string_schedule.json")))
old_strings = old["strings"] if isinstance(old, dict) and "strings" in old else old
# old set = B0(idx0) .. A7(idx48). Keep idx0..47 (B0..G7), drop idx48 (A7).
keep = old_strings[0:48]   # B0..G7

# New bass string A0 (27.5 Hz), extrapolated from the bass trend:
#   length law in the deep bass ~ vib_len ∝ f0^-0.62 (fit B0->C1); tension
#   continues the bass taper (~ -6 N per diatonic step below B0). [est]
b0 = keep[0]
f_A0 = 27.500
len_A0 = round(b0["vib_len_mm"] * (f_A0 / b0["f0_hz"]) ** -0.62, 1)
ten_A0 = round(b0["tension_N"] - 6.2, 1)          # 153.7 -> ~147.5 N  [est]
A0 = {"idx": 0, "note": "A", "octave": 0, "f0_hz": f_A0,
      "vib_len_mm": len_A0, "tension_N": ten_A0, "material": "wire"}

new = [A0] + keep
for k, s in enumerate(new):
    s["idx"] = k                                   # reindex 0..48 (A0..G7)

sigma_T = round(sum(s["tension_N"] for s in new), 1)

# ---------------------------------------------------------------------------
# 2. Refit geometry extents
# ---------------------------------------------------------------------------
pins   = [pin_pos(i)   for i in range(N)]
boards = [board_pos(i) for i in range(N)]
neck_pin_span   = norm(sub(pins[-1],   pins[0]))
board_str_span  = norm(sub(boards[-1], boards[0]))
# how far the bass extension pushed past the measured C1 endpoint:
neck_bass_ext   = norm(sub(pins[0],   pin_bass_meas))
board_bass_ext  = norm(sub(boards[0], board_bass_meas))

# ---------------------------------------------------------------------------
# 3. Loads (method = load_basis_49.md)
# ---------------------------------------------------------------------------
U = unit(sub(board_treble_meas, board_bass_meas))      # board long axis
rakes, perp, inplane = [], 0.0, 0.0
for i, s in enumerate(new):
    v = sub(pins[i], boards[i])                        # string vector board->pin
    vn = unit(v)
    rake = math.degrees(math.acos(min(1.0, abs(dot(vn, U)))))
    rakes.append(rake)
    T = s["tension_N"]
    perp    += T * math.sin(math.radians(rake))
    inplane += T * math.cos(math.radians(rake))
rakes_sorted = sorted(rakes)
rake_med = rakes_sorted[len(rakes_sorted) // 2]

# 3b. neck peak moment: simply-supported beam between bass-most (A0) and
#     treble-most (G7) pins; point load at each pin = tension along the string
#     toward its eyelet; bending driver = component perpendicular to support chord.
A, B = pins[0], pins[-1]
chord = sub(B, A); L = norm(chord); cu = unit(chord)
loads = []   # (x along chord from A, perpendicular-to-chord force magnitude signed)
for i, s in enumerate(new):
    x = dot(sub(pins[i], A), cu)                       # position along chord
    f = tuple(s["tension_N"] * c for c in unit(sub(boards[i], pins[i])))  # pull on neck
    f_par = dot(f, cu)
    f_perp_vec = tuple(f[k] - f_par * cu[k] for k in range(3))
    f_perp = norm(f_perp_vec)                          # magnitude of transverse load
    loads.append((x, f_perp))
W = sum(f for _, f in loads)
# reactions (sum moments about A): RB = Σ f*x / L ; RA = W - RB
RB = sum(f * x for x, f in loads) / L
RA = W - RB
# moment diagram sampled along span
def moment_at(xq):
    M = RA * xq
    for x, f in loads:
        if x < xq:
            M -= f * (xq - x)
    return M
xs = [k * L / 400 for k in range(401)]
Ms = [(xq, moment_at(xq)) for xq in xs]
xpk, Mpk = max(Ms, key=lambda t: abs(t[1]))
neck_moment_Nm = abs(Mpk) / 1000.0                     # N*mm -> N*m

# 3c. pillar axial: resultant of string pulls (toward pins, +z) projected on axis
Rx = sum(s["tension_N"] * unit(sub(pins[i], boards[i]))[0] for i, s in enumerate(new))
Rz = sum(s["tension_N"] * unit(sub(pins[i], boards[i]))[2] for i, s in enumerate(new))
Ry = sum(s["tension_N"] * unit(sub(pins[i], boards[i]))[1] for i, s in enumerate(new))
R = (Rx, Ry, Rz)
ax = unit(sub(pillar_top, pillar_bottom))
pillar_axial = abs(dot(R, ax))

# ---------------------------------------------------------------------------
# 4. Emit
# ---------------------------------------------------------------------------
result = {
    "count": N, "range": "A0..G7", "sigma_T_N": sigma_T,
    "sigma_T_lbf": round(sigma_T / 4.44822, 1),
    "A0_row": A0,
    "rake_median_deg": round(rake_med, 1),
    "rake_min_deg": round(min(rakes), 1), "rake_max_deg": round(max(rakes), 1),
    "perp_pull_N": round(perp, 1), "inplane_pull_N": round(inplane, 1),
    "perp_at_37": round(sigma_T * math.sin(math.radians(37)), 1),
    "inplane_at_37": round(sigma_T * math.cos(math.radians(37)), 1),
    "neck_moment_Nm": round(neck_moment_Nm, 1),
    "neck_moment_peak_frac": round(xpk / L, 3),
    "RA_N": round(RA, 1), "RB_N": round(RB, 1), "W_perp_N": round(W, 1),
    "pillar_axial_N": round(pillar_axial, 1),
    "resultant_xz_N": [round(Rx, 1), round(Rz, 1)],
    "neck_pin_span_mm": round(neck_pin_span, 1),
    "board_string_span_mm": round(board_str_span, 1),
    "neck_bass_extension_mm": round(neck_bass_ext, 1),
    "board_bass_extension_mm": round(board_bass_ext, 1),
    "bass_endpoint_A0_pin": [round(c, 2) for c in pins[0]],
    "bass_endpoint_A0_board": [round(c, 2) for c in boards[0]],
}

# write regenerated schedule
sched_out = {
    "count": N,
    "naming_note": "Scientific pitch. Range A0 (idx 0, 27.5 Hz) .. G7 (idx 48). "
                   "All-naturals (C-major) home tuning; double-action pedals raise each.",
    "discrepancy_resolution": "Spec '0G-7A / 49 strings' resolved per user direction: keep the "
        "standard 47-string core C1..G7 and add BOTH extra strings in the BASS -> A0 and B0 below C1. "
        "Final range A0..G7 = 49 strings (idx 0=A0 .. idx 48=G7). The original 47 (C1..G7) map to "
        "idx 2..48; idx 0 (A0) and idx 1 (B0) are the new bass strings. Treble caps at G7 (no A7).",
    "spacing_law": "Neck pin line: constant 10 mm pitch. Board exit line: graded "
        "s_board(i)=6.5+(24-6.5)*((48-i)/48)^0.85 mm (treble->bass). Measured anchor endpoints "
        "(params.scad) are pinned at idx 2 (C1) and idx 48 (G7); idx 0,1 extrapolate below the bass end.",
    "sigma_T_N": sigma_T,
    "strings": new,
}
json.dump(sched_out, open(os.path.join(D, "string_schedule.json"), "w"), indent=2)
with open(os.path.join(D, "string_schedule.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["idx", "note", "octave", "f0_hz", "vib_len_mm", "tension_N", "material"])
    for s in new:
        w.writerow([s["idx"], s["note"], s["octave"], s["f0_hz"], s["vib_len_mm"], s["tension_N"], s["material"]])

json.dump(result, open(os.path.join(D, "refit_49_loads.json"), "w"), indent=2)
print(json.dumps(result, indent=2))
