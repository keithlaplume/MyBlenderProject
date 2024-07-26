import bpy
import os

catalog_ids = {"original": "96aec234-1396-412e-83a0-009c8a364c54",
               "proxy1": "3ad2712c-e935-42c8-b6e8-67ab3d38b473",
               "proxy2": "d42e13d3-1926-4577-b380-38e31201cac6"}

asset_name = os.path.basename(bpy.data.filepath).split(".blend")[0]
proxy_level = asset_name.split("_")[-1]

bpy.ops.object.select_all(action='SELECT')
selection = bpy.context.selected_objects

# clear any old collections
for collection in bpy.data.collections:
    print(collection)
    for child in collection.all_objects:
        print(child)
        collection.objects.unlink(child)
    bpy.data.collections.remove(collection)

asset_collection = bpy.data.collections.new(asset_name)
bpy.context.scene.collection.children.link(asset_collection)

for obj in selection:
    asset_collection.objects.link(obj)
    try:
        bpy.context.scene.collection.objects.unlink(obj)
    except:
        pass

asset_collection.asset_mark()
asset_collection.asset_generate_preview()
asset_collection.asset_data.catalog_id = catalog_ids[proxy_level]

bpy.ops.wm.save_mainfile()