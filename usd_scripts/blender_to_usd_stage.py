import bpy
import os
from pxr import Usd, UsdGeom

ASSET_LIBRARY_PATH = "J:/StandardAssets/3D/Published"


class usd_asset:
    def __init__(self, object):
        proxy_level = object.instance_collection.name.split('_')[-1]
        instance_name = object.instance_collection.name.split('_' + proxy_level)[0]

        self.name = object.name.replace(' ', '_').replace('.', '_')
        self.blend_path = os.path.join(instance_name, f"{instance_name}_{proxy_level}.blend")
        self.usdc_path = os.path.join(instance_name, f"{instance_name}_{proxy_level}.usdc")
        self.proxy_level = proxy_level
        self.instance_name = instance_name

        self.location = (object.location.x*100, object.location.z*100, object.location.y*-100)
        self.rotation = (object.rotation_euler.x, object.rotation_euler.y, object.rotation_euler.z)
        self.scale = (object.scale.x, object.scale.y, object.scale.z)

    def resolve_blender_units(self, xform):
        xform.AddRotateXOp(opSuffix='unitsResolve').Set(value=-90)
        xform.AddScaleOp(opSuffix='unitsResolve').Set((100, 100, 100))

    def add_basic_transform(self, xform):
        xform.AddTranslateOp().Set(self.location)
        xform.AddRotateXYZOp().Set(self.rotation)
        xform.AddScaleOp().Set(self.scale)

    def add_to_stage(self, stage):
        new_prim = stage.DefinePrim(f"/{self.name}")
        new_prim.SetInstanceable(True)
        new_prim.GetPayloads().AddPayload(os.path.join(ASSET_LIBRARY_PATH, self.usdc_path))

        xform = UsdGeom.Xformable(new_prim)

        self.add_basic_transform(xform)
        self.resolve_blender_units(xform)


usd_assets = []

stage = Usd.Stage.CreateNew('J:/Portfolio_2024/USD Practice/from_blender.usda')

for object in bpy.data.objects:
    if object.instance_type == "COLLECTION":
        usd_assets.append(usd_asset(object))

for usd_asset in usd_assets:
    usd_asset.add_to_stage(stage)

stage.GetRootLayer().Save()