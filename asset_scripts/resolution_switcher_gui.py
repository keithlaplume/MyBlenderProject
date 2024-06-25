import bpy
import sys
import os
from importlib import reload

sys.path.append("C:/Users/Keith/PycharmProjects/MyBlenderProject/asset_scripts/")
import resolution_switcher

reload(resolution_switcher)

from bpy.props import (PointerProperty,
                       EnumProperty,
                       )
from bpy.types import (Panel,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class ResolutionProperties(PropertyGroup):
    resolution: EnumProperty(
        name="Resolution",
        description="Resolution to Pick for the Selection",
        items=[("4k", "4k", "4096"),
               ("2k", "2k", "2048"),
               ("1k", "1k", "1024"),
               ("512", "512", "512"),
               ("256", "256", "256"),
               ("128", "128", "128"),]
    )


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class SwitchResolution(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.switch"
    bl_label = "Switch Resolution"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        switch = context.scene.SwitchResolution
        print(f"Switching to: {switch.resolution}")
        resolution_switcher.main(switch.resolution)
        return {'FINISHED'}


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class SwitchResolutionPanel(Panel):
    bl_idname = "OBJECT_PT_my_panel2"
    bl_label = "Resolution Switcher"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Resolution Switcher"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        switch = scn.SwitchResolution
        col1 = layout.column(align=True)
        col1.label(text="Resolution:")
        col1.prop(switch, "resolution", text="")

        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.switch")


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    ResolutionProperties,
    SwitchResolution,
    SwitchResolutionPanel,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.SwitchResolution = PointerProperty(type=ResolutionProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.SwitchResolution


if __name__ == "__main__":
    register()
