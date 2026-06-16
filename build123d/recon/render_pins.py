import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "parts"))
from build123d import *
import util
from parts.pins import pin, pins
util.hlr_svg(pin(), "/tmp/pin1_prof.svg", view_dir=(0,-1,0), up=(0,0,1))  # profile
util.hlr_svg(pin(), "/tmp/pin1_end.svg",  view_dir=(1,0,0),  up=(0,0,1))  # end (circle)
# pins placed on neck: side view (along X) of all 49
util.hlr_svg(pins(49), "/tmp/pins_side.svg", view_dir=(1,0,0), up=(0,0,1))
print("rendered")
