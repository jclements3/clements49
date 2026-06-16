"""3D parametric brass worm-drive harp tuner + its co-moulded receiver (build123d).

Sizing from recon/tuner_params.json (validated packaging/self-locking concept). Built in
MILLIMETRES, local frame:
  X = string-post axis (post sticks out +X; string winds + string hole there)
  Y = worm axis  (worm points +Y, OUTWARD toward the player; hex socket at +Y end)
  Z = worm offset (worm sits at +Z above the post; this is the neck-pitch direction)

Parts:
  spindle()  -> string post + integral worm wheel (one rotating brass piece)
  worm()     -> threaded worm + hex drive socket
  receiver() -> cast-brass body, co-moulded in the flax neck (post bore, worm bore,
                wheel cavity, resin-keying anchor holes, hex access)
  tuner()    -> Compound(spindle, worm);   assembly() -> Compound(receiver, spindle, worm)

Gear teeth + worm thread are REPRESENTATIONAL (recognisable, not cuttable involute/worm
geometry) -- final tooth generation + a root-stress check are a separate step.
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *

_BD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(_BD, "recon", "tuner_params.json")))
m = P["module"]; z2 = P["z2"]
WHEEL_OD = P["wheel_OD"]; WHEEL_PD = m * z2; FACE = 3.0
WORM_OD = P["worm_OD"]; WORM_PD = P["worm_pitch_dia"]; WLEN = P["worm_len"]
C = P["centre_dist"]; POST = P["post_dia"]; HOLE = P["string_hole"]
WALL = P["wall"]; HEXAF = P["hex_af"]; CLR = 0.4
POST_BACK, POST_FRONT = -6.0, 12.0      # post extents in X (back bearing .. string end)
LEAD = m * math.pi                      # single-start axial pitch = lead


def spindle():
    """String post (along X) + integral worm wheel (representational teeth)."""
    post = Rot(0, 90, 0) * Cylinder(POST / 2, POST_FRONT - POST_BACK,
                                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    post = Pos(POST_BACK, 0, 0) * post          # base at x=POST_BACK, extends +X
    # worm wheel: gear disc (axis Z) then rotate onto X; teeth = z2 notches cut polar
    disc = Cylinder(WHEEL_OD / 2, FACE)
    tooth = Box(WHEEL_OD, m * 1.6, FACE + 1)     # notch cutter at the rim
    for ang in [i * 360 / z2 for i in range(z2)]:
        disc -= Rot(0, 0, ang) * Pos(WHEEL_OD / 2, 0, 0) * Box(m * 2.2, m * 1.4, FACE + 1)
    wheel = Rot(0, 90, 0) * disc                 # axis -> X
    spin = post + wheel
    spin -= Pos(POST_FRONT - 3, 0, 0) * Cylinder(HOLE / 2, POST * 1.6)   # string hole (along Z)
    return spin


def worm():
    """Threaded worm (along Y) + hex drive socket at the +Y end."""
    core = Rot(90, 0, 0) * Cylinder(WORM_OD / 2, WLEN,
                                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    core = Pos(0, -WLEN / 2, 0) * Rot(-90, 0, 0) * Cylinder(
        WORM_OD / 2, WLEN, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # helical thread groove (representational): sweep a small profile along a helix
    try:
        turns = WLEN / LEAD
        helix = Helix(pitch=LEAD, height=WLEN, radius=WORM_PD / 2)
        cutter = Plane(origin=helix @ 0, z_dir=helix % 0).from_local_coords  # noqa
        prof = Pos(*(helix @ 0)) * Rot(90, 0, 0) * Circle(m * 0.7)
        groove = sweep(prof, path=helix)
        worm_s = (Pos(0, -WLEN / 2, 0) * Rot(-90, 0, 0) *
                  Cylinder(WORM_OD / 2, WLEN, align=(Align.CENTER, Align.CENTER, Align.MIN))) - groove
    except Exception:
        worm_s = core                         # fallback: plain core (thread noted separately)
    # hex socket at +Y end
    hexr = HEXAF / 2 / math.cos(math.radians(30))
    hexprism = Rot(-90, 0, 0) * extrude(RegularPolygon(hexr, 6), amount=5)
    worm_s -= Pos(0, WLEN / 2 - 4, 0) * hexprism
    return worm_s


def receiver():
    """Cast-brass receiver, co-moulded in the flax neck: bores + resin-keying anchors."""
    zlo, zhi = -WHEEL_OD / 2 - WALL, C + WORM_OD / 2 + WALL      # neck-pitch extent
    ylo, yhi = -WLEN / 2 - WALL, WLEN / 2 + WALL
    xlo, xhi = -FACE / 2 - WALL - 1, FACE / 2 + WALL + 1
    body = Pos((xlo + xhi) / 2, (ylo + yhi) / 2, (zlo + zhi) / 2) * \
        Box(xhi - xlo, yhi - ylo, zhi - zlo)
    body = fillet(body.edges().filter_by(Axis.X), 1.2)
    body -= Rot(0, 90, 0) * Cylinder((POST + CLR) / 2, 60)                   # post bore (X)
    body -= Pos(0, 0, C) * Rot(90, 0, 0) * Cylinder((WORM_OD + CLR) / 2, 60)  # worm bore (Y)
    body -= Cylinder((WHEEL_OD + CLR + 1) / 2, FACE + CLR) \
        .rotate(Axis.Y, 90)                                                  # wheel cavity (X)
    for sy in (ylo + 1.2, yhi - 1.2):
        for sz in (zlo + 1.2, zhi - 1.2):
            body -= Pos(0, sy, sz) * Rot(0, 90, 0) * Cylinder(0.6, 60)       # anchor holes (X)
    return body


def tuner():
    return Compound([spindle(), Pos(0, 0, C) * worm()])


def assembly():
    return Compound([receiver(), spindle(), Pos(0, 0, C) * worm()])


if __name__ == "__main__":
    for name, fn in [("spindle", spindle), ("worm", worm), ("receiver", receiver)]:
        s = fn(); bb = s.bounding_box()
        print(f"{name:9s} valid={s.is_valid} vol={s.volume:8.1f} "
              f"bbox=[{bb.size.X:.1f},{bb.size.Y:.1f},{bb.size.Z:.1f}]")
    a = assembly(); bb = a.bounding_box()
    print(f"assembly bbox Z(neck)={bb.size.Z:.2f} mm (fits 11.7 treble: {bb.size.Z<=11.7})")
