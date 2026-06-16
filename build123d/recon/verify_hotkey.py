"""Reopen-and-exercise test for the embedded STL-export hotkey.
Run: ~/blender5/blender -b blender/clements49.blend -y --python build123d/recon/verify_hotkey.py"""
import bpy, os

print("TEXT_PRESENT:", "stl_export.py" in bpy.data.texts)
op_ok = hasattr(bpy.ops.export_mesh, "selected_stl_named")
print("OPERATOR_REGISTERED_ON_LOAD:", op_ok)

# Functionally exercise it (EXEC_DEFAULT skips the file browser invoke)
out = "/tmp/hotkey_test_export.stl"
if os.path.exists(out):
    os.remove(out)
obj = bpy.data.objects.get("harp_pole")
if obj and op_ok:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    res = bpy.ops.export_mesh.selected_stl_named('EXEC_DEFAULT', filepath=out)
    print("EXEC_RESULT:", res, "FILE_WRITTEN:", os.path.exists(out),
          "BYTES:", os.path.getsize(out) if os.path.exists(out) else 0)
else:
    print("skip exercise: obj=%s op=%s" % (bool(obj), op_ok))
