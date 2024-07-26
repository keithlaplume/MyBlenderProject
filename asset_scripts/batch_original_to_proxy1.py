import sys
sys.path.append("C:/Users/Keith/PycharmProjects/MyBlenderProject/asset_scripts/")
import export_selection_to_asset
import bpy
import os

options = {"do_new_uvs": True,
           "do_bake_textures": True,
           "do_export": True,
           "do_center": False,
           "selected_to_active": False,
           "image_size": 4096,
           "oversample": 2
           }

bake_list = ["Diffuse", "Metallic", "Emit", "Roughness", "Normal"]

bpy.ops.object.select_all(action='SELECT')
selection = bpy.context.selected_objects
bpy.context.view_layer.objects.active = selection[0]
asset_name = os.path.basename(bpy.data.filepath).split(".blend")[0].replace("_original", "_proxy1")
publish_path = os.path.dirname(bpy.data.filepath)

print(publish_path)
print(asset_name)

export_selection_to_asset.main(selection, publish_path, asset_name, bake_list, options)
