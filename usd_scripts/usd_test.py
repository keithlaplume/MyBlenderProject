import os
from pxr import Usd, UsdGeom
stage = Usd.Stage.CreateNew('HelloWorld.usda')
print(os.getcwd())
xformPrim = UsdGeom.Xform.Define(stage, '/hello')
spherePrim = UsdGeom.Sphere.Define(stage, '/hello/world')
stage.GetRootLayer().Save()
