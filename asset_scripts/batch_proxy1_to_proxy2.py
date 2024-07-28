import sys
sys.path.append("C:/Users/Keith/PycharmProjects/MyBlenderProject/asset_scripts/")
import resolution_switcher
import export_selection_to_asset
import bpy
import os

options = {"do_new_uvs": False,
           "do_bake_textures": False,
           "do_export": True,
           "do_center": False,
           "selected_to_active": False,
           "image_size": 4096,
           "oversample": 2
           }

bake_list = []

bpy.ops.object.select_all(action='SELECT')
selection = bpy.context.selected_objects
bpy.context.view_layer.objects.active = selection[0]

print("ADD DECIMATE")
# add decimate
for obj in selection:
    if obj.type == 'MESH':
        bpy.ops.object.modifier_remove(modifier="Subdiv for displacement")
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].ratio = 0.25
        bpy.ops.object.modifier_apply(modifier="Decimate")

print("SWAPPING TEXTURES")
# swap to 4k texture to 1k
resolution_switcher.main("1k")

asset_name = os.path.basename(bpy.data.filepath).split(".blend")[0].replace("_proxy1", "_proxy2")
publish_path = os.path.dirname(bpy.data.filepath)

print(publish_path)
print(asset_name)

export_selection_to_asset.main(selection, publish_path, asset_name, bake_list, options)