"""Carve pedal slots into harp_base_limacon by booleaning the actual pedal geometry
(/tmp/peds.stl, the harp_pedal_* parts at world coords) out of it -- i.e. slots exactly
where the pedals slide through. Temporarily zeroes the limacon's slide so its mesh overlaps
the pedals, applies the cut, then restores the slide.

Run: ~/blender5/blender -b blender/clements49.blend --python build123d/recon/cut_pedal_slots.py
"""
import bpy

lim = bpy.data.objects['harp_base_limacon']
slide = tuple(lim.location)
lim.location = (0.0, 0.0, 0.0)            # bring mesh to base coords (overlap the pedals)

before = set(o.name for o in bpy.data.objects)
bpy.ops.wm.stl_import(filepath="/tmp/peds.stl", global_scale=1.0)
cutter = [o for o in bpy.data.objects if o.name not in before][0]
cutter.name = "pedcut"

mod = lim.modifiers.new("pedslots", 'BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = cutter
mod.solver = 'EXACT'
bpy.context.view_layer.objects.active = lim
bpy.ops.object.modifier_apply(modifier="pedslots")
bpy.data.objects.remove(cutter, do_unlink=True)

lim.location = slide                      # restore slide
print("cut pedal slots; verts now=%d; slide restored=%s" % (len(lim.data.vertices), [round(v,2) for v in slide]))
bpy.ops.wm.save_mainfile()
print("SAVED")
