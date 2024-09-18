import bpy
import sys
from importlib import reload

sys.path.append("C:/Users/Keith/PycharmProjects/MyBlenderProject/usd_scripts/")
import blender_to_usd_stage

reload(blender_to_usd_stage)

from bpy.props import (StringProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):
    export_path: StringProperty(
        name="Export Path",
        description="Path to Directory",
        default="J:/StandardAssets/3D/Published",
        maxlen=1024,
        subtype='FILE_PATH'
    )

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class Export_USD(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.export_usd"
    bl_label = "EXPORT USD STAGE"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        export_usd_tool = context.scene.export_usd_tool
        print(f"Exporting USD Stage to {export_usd_tool.export_path}")
        blender_to_usd_stage.export(export_usd_tool.export_path)

        return {'FINISHED'}


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_idname = "OBJECT_PT_Export_USD_Stage"
    bl_label = "Export USD"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "USD Stage Export "
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        export_usd_tool = scn.export_usd_tool
        col1 = layout.column(align=True)
        col1.label(text="Export Path:")
        col1.prop(export_usd_tool, "export_path", text="")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.export_usd")


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    Export_USD,
    OBJECT_PT_CustomPanel,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.export_usd_tool = PointerProperty(type=MyProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.export_usd_tool


if __name__ == "__main__":
    register()