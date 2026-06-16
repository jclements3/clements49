# recon/ — faithful extraction of clements49.blend into build123d B-rep solids

Goal: turn the **actual** geometry of `clements49.blend` (the purchased TurboSquid
model, 541 objects / 87k verts) into clean build123d B-rep solids that match the real
shapes — so the harp can be parameterized, the 2 bass strings added, and the
acoustic/structural analysis re-run on faithful geometry. This complements the
*idealized* primitives under `build123d/parts/` (use those for clean parametrics; use
these when geometry must match the real model).

## Pipeline (two env-isolated stages)

The build123d env needs conda's libexpat (`build123d/py` sets `LD_LIBRARY_PATH`), but
that same lib breaks numpy/trimesh — so meshing and CAD run in **separate** Python envs:

1. **Export** per-object-family meshes from the blend (Blender 5.1 headless):
   `~/blender5/blender --background blender/clements49.blend --python <export>` joins each
   name-family (e.g. all `harp_string`) and writes `cad/parts_mesh/<family>.stl`.
2. **Slice** (`slice_part.py`, run with the **plain venv** `.venv/bin/python`): cut the
   mesh into `N` cross-sections along an axis; each section's largest-area polyline is
   closed (handles open shells like the soundbox), arc-length **resampled to `M` points**
   with consistent winding + start vertex (equal counts are what make the loft robust),
   and written as world-3D loops to `recon/sections/sec_<family>.json`.
3. **Loft** (`loft_part.py` / `loft_all.py` / `build_recon.py`, run with `build123d/py`):
   ThruSections (ruled) loft of the section faces → a B-rep solid → `recon/brep/<family>.brep`.

Regenerate everything: `build123d/py recon/build_recon.py` (needs `cad/parts_mesh/*.stl`).

## Functional mapping (see manifest.json for axis/N/M per part)

| function    | blend family            | notes |
|-------------|-------------------------|-------|
| column      | `harp_pole`             | real **tapered/waisted** post — NOT a plain cylinder |
| neck        | `harp_top_wood`         | harmonic-curve S over the top |
| soundbox    | `harp_big_side_pivot`   | open shell; sections closed across the soundboard face |
| base_body   | `harp_base_body`        | watertight |
| base_bottom | `harp_base_bottom`      | watertight |
| leg         | `harp_leg`              | watertight feet |
| strings     | `harp_string` ×47       | endpoints already in `clements49_params.STRINGS` (+2 bass for the 49-set) |

Not yet reconstructed (decorative/mechanism): bolts, gold pedal box, pedals, pivots,
string-holes, inner planks, the small `pole_top_pivot` finial (Z 211.5→216.4).

## Verification

Each part is checked by **bbox + volume vs its source mesh** (recorded in manifest.json),
and the assembled `recon_harp()` was rendered (HLR side view) and visually confirmed to
read as a real concert pedal harp. All 6 frame parts loft to **valid** solids.

## Use

```python
import sys; sys.path.insert(0, "recon")
from parts_recon import recon_harp, recon_part, recon_frame
asm   = recon_harp(string_set=49)     # faithful frame + 49 strings
col   = recon_part("column")          # one part
```

## Known limitations / next

- **Drawing cleanliness**: ruled-loft surfaces show facet/ring seams under HLR (geometry
  is faithful; the lines are cosmetic). A silhouette-only render or smooth loft is future
  work; the clean idealized plates remain `build123d/clements47.svg` / `clements49.svg`.
- Geometry files (`*.stl`, `*.brep`, `sections/`) are **derived from the licensed model**
  and are gitignored — only the pipeline code + manifest are tracked. Regenerate locally.
