#!/usr/bin/env python3
"""Export Clements 49 soundbox data for a parametric limaçon re-loft.

Coordinate frame (matches params.scad / anchors.json):
  Units = mm. z-up. Origin = centre of the base footprint in x,y; z=0 at the floor.
  +x = bass -> treble (also toward the body/back side). -x = pillar/player side.
  y  = across-body. Soundboard face at y ~ +1.9 (FRONT). Body bulges to -y (BACK).
  Body long axis runs diagonally: bass (low z, -x) -> treble (high z, +x).

Sections are horizontal slices (normal = +z). Cavity volume is measured from the
rendered soundbox_cavity() solid (the enclosed air). Section outlines are sliced
from the rendered sbx_outer_solid().
"""
import json, subprocess, os, numpy as np, trimesh

P = '/home/clementsj/projects/clements49'
SBX = f'{P}/cad/frame/soundbox.scad'
OUT_JSON = f'{P}/cad/analysis/soundbox_reloft_data.json'
OUT_MD   = f'{P}/cad/analysis/soundbox_reloft_data.md'

def render(call, stl):
    scad = f'/tmp/_{os.path.basename(stl)}.scad'
    open(scad, 'w').write(f'use<{SBX}>\n{call}\n')
    subprocess.run(['openscad', '-o', stl, '--export-format=binstl', scad],
                   check=True, capture_output=True, timeout=300)
    return trimesh.load(stl)

# ---- 1. render outer solid + cavity ----
outer = render('sbx_outer_solid(72);', '/tmp/sbx_outer.stl')
cavity = render('soundbox_cavity(72);', '/tmp/sbx_cav.stl')
shell = render('soundbox(72, cut_holes=false);', '/tmp/sbx_shell.stl')

vol_outer = abs(outer.volume) / 1e6          # mm^3 -> L
vol_cav   = abs(cavity.volume) / 1e6
print(f"outer solid volume = {vol_outer:.2f} L")
print(f"CAVITY (enclosed air) volume = {vol_cav:.2f} L   <-- key number")

# ---- 2. cross-section outlines at stations ----
zlo, zhi = outer.bounds[0][2], outer.bounds[1][2]
zs = [130, 258, 440, 622, 804, 986, 1168, 1290]
sections = []
for z in zs:
    sec = outer.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        continue
    loops = sec.discrete
    loop = max(loops, key=lambda L: len(L))     # largest loop
    xy = np.round(loop[:, :2], 1)
    ys = xy[:, 1]
    front_i = int(np.argmax(xy[:, 1]))          # FRONT = max +y (soundboard side)
    sections.append({
        'z_mm': z,
        'x_center_mm': round(float(xy[:, 0].mean()), 1),
        'width_x_mm': round(float(np.ptp(xy[:, 0])), 1),
        'depth_y_mm': round(float(np.ptp(xy[:, 1])), 1),
        'y_front_mm': round(float(ys.max()), 1),    # soundboard edge
        'y_back_mm':  round(float(ys.min()), 1),    # bulge / back
        'n_points': len(xy),
        'outline_xy': xy.tolist(),                  # ordered (x,y) mm
    })
    print(f"  z={z}: x_c={sections[-1]['x_center_mm']} w={sections[-1]['width_x_mm']} "
          f"d={sections[-1]['depth_y_mm']} front_y={sections[-1]['y_front_mm']} pts={len(xy)}")

# ---- 3. soundbox axis (centerline through section centroids) ----
axis = [[s['x_center_mm'], 0.0, s['z_mm']] for s in sections]
axis_len = float(np.sum(np.linalg.norm(np.diff(np.array(axis), axis=0), axis=1)))

# ---- 4. soundboard + 49 string board-crossing points (refit A0..G7 law) ----
bbass = np.array([-204.47, 1.88, 186.31])   # C1 (idx 2) measured
btreb = np.array([441.70, 1.88, 1232.23])   # G7 (idx 48) measured
def s_board(i): return 6.5 + (24.0 - 6.5) * ((48 - i) / 48.0) ** 0.85
def bcum(i):
    c = 0.0
    for j in range(1, i + 1):
        c += (s_board(j) + s_board(j - 1)) / 2.0
    return c
b2, b48 = bcum(2), bcum(48)
sched = json.load(open(f'{P}/cad/analysis/string_schedule.json'))['strings']
string_pts = []
for s in sched:
    i = s['idx']
    t = (bcum(i) - b2) / (b48 - b2)
    p = bbass + (btreb - bbass) * t
    string_pts.append({'idx': i, 'note': f"{s['note']}{s['octave']}",
                       'xyz_mm': [round(float(p[0]), 1), round(float(p[1]), 1), round(float(p[2]), 1)]})
board_span = float(np.linalg.norm(np.array(string_pts[-1]['xyz_mm']) - np.array(string_pts[0]['xyz_mm'])))

# ---- 5. soundholes (from soundbox.scad params) ----
holes = []
# mirror sbx_hole(): 5 graded ovals along the back, axis_offset 0.5, spread 0.55
zmin_h, zmax_h = 123.35, 1325.72
centre_z = zmin_h + 0.5 * (zmax_h - zmin_h); spread = 0.55 * (zmax_h - zmin_h)
N = 5
for k in range(N):
    zc = centre_z + spread * (k / (N - 1) - 0.5)
    g = (k / (N - 1)) ** 1.0
    w = 120.0 + (60.0 - 120.0) * g       # long axis (along body)
    h = 85.0 + (44.0 - 85.0) * g         # short axis
    holes.append({'k': k, 'z_mm': round(zc, 1), 'long_mm': round(w, 1), 'short_mm': round(h, 1),
                  'face': 'back (-y)'})

data = {
    'units': 'mm', 'frame': 'z-up; origin=base footprint centre (x,y), z=0 floor; '
        '+x bass->treble; soundboard face +y (front); body bulges -y (back)',
    'cavity_volume_L': round(vol_cav, 2),
    'outer_solid_volume_L': round(vol_outer, 2),
    'wall_thickness_mm': 4.0,
    'sections': sections,
    'soundbox_axis': {'points_xyz_mm': [[round(a, 1) for a in p] for p in axis],
                      'length_mm': round(axis_len, 1),
                      'z_range_mm': [sections[0]['z_mm'], sections[-1]['z_mm']]},
    'soundboard': {'string_span_mm': round(board_span, 1),
                   'width_taper_mm': [380.0, 70.0], 'span_U_mm': 1149.0,
                   'rake_deg_design': 37.0, 'rake_deg_measured': 35.3,
                   'string_crossings': string_pts},
    'soundholes': holes,
    'back_construction': 'continuous lofted super-ellipse shell (NOT faceted staves); '
        'no internal ribs/bulkheads modeled in the soundbox (soundboard carries a CF/woven spine; '
        'base has bulkheads). Back transverse crown radius = 200 mm (param).',
    'source_formats': 'SVG plate (renders/clements49_plate.svg); STL reference '
        '(cad/reference/*.stl, gitignored); original OBJ (extract/, gitignored). '
        'No STEP/BREP (geometry is mesh + parametric OpenSCAD).',
}
json.dump(data, open(OUT_JSON, 'w'), indent=2)
print(f"\nwrote {OUT_JSON}")
print(f"board string span (A0->G7) = {board_span:.1f} mm")
print(f"axis length = {axis_len:.1f} mm over z[{zs[0]},{zs[-1]}]")
