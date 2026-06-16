"""Load the faithful (mesh-traced) B-rep harp parts and assemble them.

These are the parts extracted from clements49.blend (recon/manifest.json), in
contrast to the idealized parametric parts under build123d/parts/. Use these when
you need geometry that matches the real model (volume/mass/section analysis,
faithful drawings); use parts/ when you need a clean parametric primitive.

recon_harp(string_set=49, include_strings=True) -> Compound (model units, world coords).
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "parts"))
from build123d import import_brep, Compound
from parts.strings import strings, strings_by_color  # noqa: F401  (re-export)

MANIFEST = json.load(open(os.path.join(HERE, "manifest.json")))
BREP_DIR = os.path.join(HERE, "brep")


def recon_part(function):
    """Return one faithful B-rep part by functional name (e.g. 'column')."""
    entry = next(p for p in MANIFEST["parts"] if p["function"] == function)
    return import_brep(os.path.join(BREP_DIR, entry["blend"] + ".brep"))


def recon_frame():
    """Compound of all faithful frame parts (no strings)."""
    shapes = []
    for p in MANIFEST["parts"]:
        s = import_brep(os.path.join(BREP_DIR, p["blend"] + ".brep"))
        s.label = p["function"]
        shapes.append(s)
    return Compound(children=shapes)


def recon_harp(string_set=49, include_strings=True):
    shapes = list(recon_frame().children)
    if include_strings:
        st = strings(string_set=string_set); st.label = "strings"
        shapes.append(st)
    return Compound(children=shapes)


if __name__ == "__main__":
    asm = recon_harp()
    bb = asm.bounding_box()
    print("recon parts:", [p["function"] for p in MANIFEST["parts"]] + ["strings"])
    print("assembled bbox size", [round(v, 1) for v in bb.size],
          "Z", round(bb.min.Z, 1), "->", round(bb.max.Z, 1))
