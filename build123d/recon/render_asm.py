import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "parts"))
from build123d import *
import util
from parts.strings import strings
PARTS=["harp_pole","harp_top_wood","harp_big_side_pivot","harp_base_body","harp_base_bottom","harp_leg"]
shapes=[import_brep(f"/tmp/{p}.brep") for p in PARTS]
shapes.append(strings(47))
asm=Compound(children=shapes)
bb=asm.bounding_box()
print("asm bbox size",[round(v,1) for v in bb.size],"Z",round(bb.min.Z,1),round(bb.max.Z,1))
util.hlr_svg(asm,"/tmp/asm_front.svg",view_dir=(0,-1,0),up=(0,0,1))
util.hlr_svg(asm,"/tmp/asm_side.svg", view_dir=(1,0,0), up=(0,0,1))
print("rendered")
