"""Embed the STL-export hotkey script into clements49.blend (Method B, headless).

Usage:
  ~/blender5/blender --background blender/clements49.blend \
      --python build123d/recon/embed_hotkey.py -- build123d/recon/blender_stl_export.py

Creates a text datablock 'stl_export.py' inside the .blend with the Register flag
(use_module) + fake user, execs it for this session, enables auto-run, and saves.
On future *interactive* opens (with Auto Run Python Scripts enabled) the text
re-registers and binds Ctrl+Shift+E in the 3D viewport."""
import bpy, sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
src = argv[0] if argv else "build123d/recon/blender_stl_export.py"
CODE = open(src).read()

NAME = "stl_export.py"  # must end in .py for register-on-load

if NAME in bpy.data.texts:                       # replace any existing copy
    bpy.data.texts.remove(bpy.data.texts[NAME])

txt = bpy.data.texts.new(NAME)
txt.write(CODE)

# "Register" checkbox (run on .blend load). Property name has varied across builds.
reg_ok = False
for attr in ("use_module",):
    if hasattr(txt, attr):
        setattr(txt, attr, True); reg_ok = True
txt.use_fake_user = True                         # survive purge

# allow scripts to auto-execute on future opens (preference; user must also keep it on)
try:
    bpy.context.preferences.filepaths.use_scripts_auto_execute = True
except Exception as e:
    print("auto-exec pref note:", e)

# register for this session too (in --background, addon keyconfig may be absent, so the
# hotkey won't bind now; the class still registers and the embed/save is what matters)
try:
    exec(compile(CODE, NAME, 'exec'), {'__name__': '__main__'})
    print("exec register: ok")
except Exception as e:
    print("exec register note:", e)

bpy.ops.wm.save_mainfile()

# report what got embedded
t = bpy.data.texts[NAME]
print("EMBEDDED name=%s bytes=%d register(use_module)=%s fake_user=%s reg_flag_set=%s"
      % (NAME, len(t.as_string()), getattr(t, "use_module", "n/a"), t.use_fake_user, reg_ok))
print("OPERATOR registered:", hasattr(bpy.types, "EXPORT_OT_selected_stl_named"))
