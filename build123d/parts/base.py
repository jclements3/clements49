"""Base pedestal -- chunky rounded box. build123d Solid, model units (original world coords)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *

# --- Parameters (model units; match base.stl bbox: x[-29.6,30.6] y[-61.9,-0.77] z[0.03,15.47]) ---
BASE_X_MIN = -29.6   # footprint min X (world)
BASE_X_MAX = 30.6    # footprint max X (world)
BASE_Y_MIN = -61.9   # footprint min Y (world)
BASE_Y_MAX = -0.8    # footprint max Y (world)
BASE_Z_MIN = 0.0     # bottom of pedestal
BASE_Z_MAX = 15.5    # top of pedestal
CORNER_R   = 6.0     # vertical-edge fillet radius (rounded box)

# Derived footprint dimensions / center
_LEN_X = BASE_X_MAX - BASE_X_MIN          # ~60.2
_LEN_Y = BASE_Y_MAX - BASE_Y_MIN          # ~61.1
_HEIGHT = BASE_Z_MAX - BASE_Z_MIN         # ~15.5
_CX = (BASE_X_MIN + BASE_X_MAX) / 2
_CY = (BASE_Y_MIN + BASE_Y_MAX) / 2
_CZ = (BASE_Z_MIN + BASE_Z_MAX) / 2


def base():
    """Return the base pedestal Solid: a rounded box at original world coords."""
    box = Solid.make_box(_LEN_X, _LEN_Y, _HEIGHT,
                         Plane(origin=(BASE_X_MIN, BASE_Y_MIN, BASE_Z_MIN)))
    # Round the four vertical edges for a clean pedestal look.
    vertical = box.edges().filter_by(Axis.Z)
    return fillet(vertical, radius=CORNER_R)


if __name__ == "__main__":
    s = base()
    bb = s.bounding_box()
    print("base volume", round(s.volume, 1), "valid", s.is_valid,
          "bbox dims", [round(v, 2) for v in bb.size],
          "z", [round(bb.min.Z, 2), round(bb.max.Z, 2)])
