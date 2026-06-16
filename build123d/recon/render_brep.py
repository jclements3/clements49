import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *
import util
s=import_brep(sys.argv[1]); out=sys.argv[2]
util.hlr_svg(s, out+"_front.svg", view_dir=(0,-1,0), up=(0,0,1))
util.hlr_svg(s, out+"_side.svg",  view_dir=(1,0,0),  up=(0,0,1))
print("rendered", out)
