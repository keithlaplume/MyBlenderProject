import bpy

for collection in bpy.data.collections:
    if collection.asset_data is not None:
        collection.asset_generate_preview()

bpy.ops.wm.save_mainfile()