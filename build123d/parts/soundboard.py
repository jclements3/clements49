"""Soundboard -- thin tapered PLATE on the front (flat side) of the body.

The board is a near-flat plate raked like the soundbox flat side: it runs from a
WIDE/THICK bass end to a NARROW/THIN treble end, lying on the string board-line
plane.  Built as a loft of two thin rectangular sketches (bass section -> treble
section), each placed on a plane whose normal points along the board (string axis)
so the plate follows the rake.

Cross-section convention (in each end plane):
  - local X  = plate WIDTH  (across the strings)
  - local Y  = plate THICKNESS (front face -> into the body)

Drives its length/rake from the string board-line params.STRINGS[*]['board'];
width/thickness taper measured from soundboard.stl.  Model units, world coords.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from build123d import *
from clements49_params import STRINGS

# --- Board-line endpoints (the plate surface line), from the string schedule ---
BASS_BOARD   = np.array(STRINGS[0]["board"])    # wide/thick bass end  (~z 12.6)
TREBLE_BOARD = np.array(STRINGS[-1]["board"])   # narrow/thin treble end (~z 142.6)

# --- Plate cross-section, measured from soundboard.stl (model units) ---
WIDTH_BASS     = 53.5   # plate width across strings at the bass end
WIDTH_TREBLE   = 14.3   # plate width at the treble end
THICK_BASS     = 2.7    # plate thickness (front->body) at the bass end
THICK_TREBLE   = 1.1    # plate thickness at the treble end

# Extend slightly past the board-line endpoints so the lofted z-extent matches the
# measured STL (~16.6..152.4) rather than the shorter pin/board node span.
END_EXTEND = 0.02       # fraction of board length added at each end


def _front_dir(axis_u):
    """Plate front-face outward direction: perpendicular to the board axis, in the
    Y-Z plane, pointing toward +Y (out the flat front of the body)."""
    f = np.array([0.0, axis_u[2], -axis_u[1]])  # rotate axis 90 deg in y-z
    if f[1] < 0:
        f = -f
    return f / np.linalg.norm(f)


def _section(center, axis_u, width, thick):
    """Thin rectangle (width x thickness) whose FRONT edge lies on `center` and
    which grows backward (into the body) by `thick`."""
    front = _front_dir(axis_u)
    back_center = center - front * (thick / 2.0)   # shift so front edge is on board line
    # Plane X = width (world X across strings); plane normal = board axis.
    plane = Plane(origin=tuple(back_center), x_dir=(1, 0, 0), z_dir=tuple(axis_u))
    with BuildSketch(plane) as sk:
        Rectangle(width, thick, align=(Align.CENTER, Align.CENTER))
    return sk.sketch


def soundboard():
    """Return the soundboard plate Solid (thin tapered loft, bass->treble)."""
    axis = TREBLE_BOARD - BASS_BOARD
    L = np.linalg.norm(axis)
    axis_u = axis / L
    bass_c   = BASS_BOARD   - axis_u * (END_EXTEND * L)   # extend past bass end
    treble_c = TREBLE_BOARD + axis_u * (END_EXTEND * L)   # extend past treble end

    s_bass   = _section(bass_c,   axis_u, WIDTH_BASS,   THICK_BASS)
    s_treble = _section(treble_c, axis_u, WIDTH_TREBLE, THICK_TREBLE)
    return loft([s_bass, s_treble])


if __name__ == "__main__":
    s = soundboard()
    print("soundboard volume", round(s.volume, 1),
          "valid", s.is_valid,
          "bbox", [round(v, 1) for v in s.bounding_box().size])
