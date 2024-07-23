import os
from pxr import Usd, UsdGeom

def resolve_blender_units(xform):
    xform.AddRotateXOp(opSuffix='unitsResolve').Set(value=-90)
    xform.AddScaleOp(opSuffix='unitsResolve').Set((100, 100, 100))

def add_basic_transform(xform, translation=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
    xform.AddTranslateOp().Set(translation)
    xform.AddRotateXYZOp().Set(rotation)
    xform.AddScaleOp().Set(scale)

stage = Usd.Stage.CreateNew('J:/Portfolio_2024/USD Practice/payload.usda')
building1 = stage.OverridePrim('/MaxHay_Office_Building_Tall_proxy2')
building1.GetPayloads().AddPayload('J:/StandardAssets/3D/Published/MaxHay_Office Building Tall/MaxHay_Office Building Tall_proxy2.usdc')
xform = UsdGeom.Xformable(building1)

add_basic_transform(xform)
resolve_blender_units(xform)

stage.GetRootLayer().Save()
