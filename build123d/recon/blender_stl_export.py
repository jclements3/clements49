bl_info = {
    "name": "Export Selected as STL (named, model units)",
    "author": "clements49",
    "version": (1, 1),
    "blender": (5, 0, 0),
    "location": "View3D > Ctrl+Shift+E",
    "description": "Export selected object(s) as a single STL; filename pre-filled "
                   "with the active object's name",
    "category": "Import-Export",
}

import bpy

# STL is unitless; build123d reads the raw coordinates. This clements49.blend is
# modelled in MODEL UNITS (~8.86 mm/unit; the harp is ~216 units tall) -- it is NOT
# metres. SCALE=1.0 keeps exports in the same native frame as the existing string
# schedule (clements49_params), the recon B-reps, and cad/parts_mesh/*.stl.
#   1.0   -> native model units (USE THIS for consistency with the repo pipeline)
#   8.86  -> convert model units -> real millimetres (then rescale the whole pipeline)
#   1000  -> only if the scene were actually in metres (it is not)
SCALE = 1.0


class EXPORT_OT_selected_stl_named(bpy.types.Operator):
    """Export selected object(s) as one STL; name pre-filled from active object"""
    bl_idname = "export_mesh.selected_stl_named"
    bl_label = "Export Selected as STL"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    filter_glob: bpy.props.StringProperty(default="*.stl", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        obj = context.active_object
        if obj is None:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}

        # Base name = active object; append "+N" when several objects are selected
        name = obj.name
        extra = len(context.selected_objects) - 1
        if extra > 0:
            name = "%s+%d" % (name, extra)
        self.filepath = name + ".stl"

        # Start in the folder next to the saved .blend, if any
        if bpy.data.filepath:
            import os
            self.filepath = os.path.join(
                os.path.dirname(bpy.data.filepath), self.filepath
            )

        context.window_manager.fileselect_add(self)  # opens the file browser
        return {'RUNNING_MODAL'}

    def execute(self, context):
        path = self.filepath
        if not path.lower().endswith(".stl"):
            path += ".stl"

        try:
            # Modern exporter (Blender 4.2+ / 5.x) - all selected go into one file
            bpy.ops.wm.stl_export(
                filepath=path,
                export_selected_objects=True,
                global_scale=SCALE,
            )
        except (AttributeError, TypeError):
            # Fallback for the legacy Python STL add-on
            bpy.ops.export_mesh.stl(
                filepath=path,
                use_selection=True,
                global_scale=SCALE,
            )

        self.report({'INFO'}, "Exported (x%g): %s" % (SCALE, path))
        return {'FINISHED'}


addon_keymaps = []


def register():
    # Idempotent: safe to re-run from the Text Editor while editing
    try:
        bpy.utils.register_class(EXPORT_OT_selected_stl_named)
    except (ValueError, RuntimeError):
        bpy.utils.unregister_class(EXPORT_OT_selected_stl_named)
        bpy.utils.register_class(EXPORT_OT_selected_stl_named)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        # remove any prior copy of this shortcut so it doesn't stack on re-run
        for kmi in list(km.keymap_items):
            if kmi.idname == EXPORT_OT_selected_stl_named.bl_idname:
                km.keymap_items.remove(kmi)
        kmi = km.keymap_items.new(
            EXPORT_OT_selected_stl_named.bl_idname,
            type='E', value='PRESS', ctrl=True, shift=True,  # change hotkey here
        )
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(EXPORT_OT_selected_stl_named)


if __name__ == "__main__":
    register()
