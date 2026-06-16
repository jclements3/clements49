"""Shared helpers: isometric (or arbitrary-direction) HLR SVG export per ANSI/ISO drafting."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build123d import *
# ---- switch the projection direction here (camera offset dir, relative to part centre) ----
ISO_DIR = (1, -1, 1)              # true isometric. e.g. front=(0,-1,0), top=(0,0,1), right=(1,0,0)
VIEWS = {"iso":(1,-1,1), "front":(0,-1,0), "rear":(0,1,0), "left":(-1,0,0),
         "right":(1,0,0), "top":(0,0,1), "bottom":(0,0,-1)}
def hlr_svg(shape, path, view_dir=ISO_DIR, scale=None, up=None, overlays=None):
    """Project `shape` along view_dir with hidden-line removal; write SVG with Visible+Hidden layers.

    up: optional explicit viewport up vector (page-vertical). If None, Z-up unless the view
    looks along Z, then Y-up. Set it to align stacked views (e.g. top above side share an axis).

    overlays: optional list of (shape, (r,g,b)) drawn as extra CONTINUOUS coloured layers,
    projected with the SAME camera (origin/up/look_at) as `shape` so they register exactly.
    Used to draw coloured string lines over the (strings-less) frame HLR.
    """
    bb = shape.bounding_box(); c = bb.center(); d = max(bb.size.X, bb.size.Y, bb.size.Z) or 1
    origin = (c.X + view_dir[0]*d*2, c.Y + view_dir[1]*d*2, c.Z + view_dir[2]*d*2)
    if up is None:
        up = (0,0,1) if abs(view_dir[2]) < 0.99 else (0,1,0)
    visible, hidden = shape.project_to_viewport(origin, viewport_up=up, look_at=c)   # focus=None => orthographic
    if scale is None:
        scale = 180.0 / d            # fit ~180 svg units
    exp = ExportSVG(scale=scale)
    exp.add_layer("Visible", line_color=Color(0,0,0),        line_type=LineType.CONTINUOUS, line_weight=0.4)
    exp.add_layer("Hidden",  line_color=Color(0.55,0.55,0.55), line_type=LineType.ISO_DASH, line_weight=0.25)
    exp.add_shape(visible, layer="Visible")
    exp.add_shape(hidden,  layer="Hidden")
    for i, (oshape, col) in enumerate(overlays or []):
        ov, _ = oshape.project_to_viewport(origin, viewport_up=up, look_at=c)
        name = f"String{i}"
        exp.add_layer(name, line_color=Color(*col), line_type=LineType.CONTINUOUS, line_weight=0.35)
        exp.add_shape(ov, layer=name)
    exp.write(path)
    return len(visible), len(hidden)
