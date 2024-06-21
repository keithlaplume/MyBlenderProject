import bpy
import sys
from importlib import reload

sys.path.append("C:/Users/Keith/PycharmProjects/MyBlenderProject/asset_scripts/")
import export_selection_to_asset

reload(export_selection_to_asset)

from bpy.props import (StringProperty,
                       BoolProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):
    publish_path: StringProperty(
        name="Publish Path",
        description="Path to Directory",
        default="J:/StandardAssets/3D/Published",
        maxlen=1024,
        subtype='DIR_PATH'
    )
    asset_name: StringProperty(
        name="Asset Name",
        description="Name of the Asset",
        default=bpy.context.active_object.name,
        maxlen=1024,
    )
    prefix: StringProperty(
        name="Prefix",
        description="Prefix for Asset Name",
        default="",
        maxlen=1024,
    )
    postfix: StringProperty(
        name="Postfix",
        description="Prefix for Asset Name",
        default="",
        maxlen=1024,
    )
    include_prefix: BoolProperty(
        name="Include Prefix in folder name",
        description="Bool property",
        default=False
    )
    include_postfix: BoolProperty(
        name="Include Postfix in folder name",
        description="Bool property",
        default=False
    )
    do_new_uvs: BoolProperty(
        name="Create New UVs for Baking",
        description="Bool property",
        default=True
    )
    do_bake_textures: BoolProperty(
        name="Bake Textures to new UVs",
        description="Bool property",
        default=True
    )
    diffuse: BoolProperty(
        name="Diffuse",
        description="Bool property",
        default=True
    )
    metallic: BoolProperty(
        name="Metallic",
        description="Bool property",
        default=True
    )
    emit: BoolProperty(
        name="Emit",
        description="Bool property",
        default=True
    )
    roughness: BoolProperty(
        name="Roughness",
        description="Bool property",
        default=True
    )
    normal: BoolProperty(
        name="Normal",
        description="Bool property",
        default=True
    )
    do_export: BoolProperty(
        name="Export Selection as Seperate Blend File",
        description="Bool property",
        default=True
    )
    do_center: BoolProperty(
        name="Center Objects on Exports",
        description="Bool property",
        default=True
    )


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class Publish(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.publish"
    bl_label = "PUBLISH"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        publish_tool = context.scene.publish_tool
        options = {"do_new_uvs": publish_tool.do_new_uvs,
                   "do_bake_textures": publish_tool.do_bake_textures,
                   "do_export": publish_tool.do_export,
                   "do_center": publish_tool.do_center,
                   }

        bake_list = []

        if publish_tool.diffuse:
            bake_list.append("diffuse")
        if publish_tool.metallic:
            bake_list.append("metallic")
        if publish_tool.emit:
            bake_list.append("emit")
        if publish_tool.roughness:
            bake_list.append("roughness")
        if publish_tool.normal:
            bake_list.append("normal")

        selection = bpy.context.selected_objects
        export_selection_to_asset.main(selection, publish_tool.publish_path, publish_tool.asset_name, bake_list,
                                       options)
        return {'FINISHED'}


class UpdateName(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.update_name"
    bl_label = "Name from Active"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        context.scene.publish_tool.asset_name = context.active_object.name
        return {'FINISHED'}


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_idname = "OBJECT_PT_my_panel"
    bl_label = "Asset Publish"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Asset Publsih"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        publish_tool = scn.publish_tool
        col1 = layout.column(align=True)
        col1.label(text="Publish Path:")
        col1.prop(publish_tool, "publish_path", text="")

        col1 = layout.column(align=True)
        col1.label(text="Asset Name:")
        row1 = col1.row(align=True)
        row1.prop(publish_tool, "asset_name", text="")
        row1.operator("object.update_name")
        row2 = col1.row(align=True)
        row2.prop(publish_tool, "prefix", text="Prefix")
        row2.prop(publish_tool, "include_prefix")
        row3 = col1.row(align=True)
        row3.prop(publish_tool, "postfix", text="Postfix")
        row3.prop(publish_tool, "include_postfix")

        col3 = layout.column(align=True)
        col3.prop(publish_tool, "do_new_uvs")

        col4 = layout.column(align=True)
        col4.prop(publish_tool, "do_bake_textures")
        col5 = layout.column(align=True)
        col5.prop(publish_tool, "diffuse")
        col5.prop(publish_tool, "metallic")
        col5.prop(publish_tool, "emit")
        col5.prop(publish_tool, "roughness")
        col5.prop(publish_tool, "normal")
        if publish_tool.do_new_uvs:
            col4.active = True
        else:
            col4.active = False
        if publish_tool.do_bake_textures and publish_tool.do_new_uvs:
            col5.active = True
        else:
            col5.active = False

        col6 = layout.column(align=True)
        col6.prop(publish_tool, "do_export")

        col7 = layout.column(align=True)
        col7.prop(publish_tool, "do_center")
        if publish_tool.do_export:
            col7.active = True
        else:
            col7.active = False

        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.publish")


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    Publish,
    OBJECT_PT_CustomPanel,
    UpdateName
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.publish_tool = PointerProperty(type=MyProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.publish_tool


if __name__ == "__main__":
    register()