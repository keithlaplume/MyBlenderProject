import subprocess
import os
from pprint import pprint

paths = ['J:\\StandardAssets\\3D\\Published\\Dome_Buildings_Yellow\\Dome_Buildings_Yellow_original.blend',
 'J:\\StandardAssets\\3D\\Published\\Dome_Park_Red\\Dome_Park_Red_original.blend',
 'J:\\StandardAssets\\3D\\Published\\Dome_Trees_Blue\\Dome_Trees_Blue_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgLgCommsArray_A\\KB3D_MTM_BldgLgCommsArray_A_original.blend',
 'J:\\StandardAssets\\3D\Published\\KB3D_MTM_BldgLgCommsArray_SimpleBuilding_hilltop\\KB3D_MTM_BldgLgCommsArray_SimpleBuilding_hilltop_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgLgCommsArray_SimpleBuilding\\KB3D_MTM_BldgLgCommsArray_SimpleBuilding_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgLgCommsArray_SimpleBuilding_hilltop\\KB3D_MTM_BldgLgCommsArray_SimpleBuilding_hilltop_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgLgCommunityCenter_A\\KB3D_MTM_BldgLgCommunityCenter_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgLgLandingPad_A\\KB3D_MTM_BldgLgLandingPad_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgLgPowerStation_A\\KB3D_MTM_BldgLgPowerStation_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgLgPowerStation_A_LandingPad\\KB3D_MTM_BldgLgPowerStation_A_LandingPad_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgLgPowerStation_B\\KB3D_MTM_BldgLgPowerStation_B_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgLgTerraformer_A\\KB3D_MTM_BldgLgTerraformer_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgMdFamilyHousing_A\\KB3D_MTM_BldgMdFamilyHousing_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgMdGreenHouse_A\\KB3D_MTM_BldgMdGreenHouse_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgMdRoverGarage_A\\KB3D_MTM_BldgMdRoverGarage_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgSmResidentialAlt_A\\KB3D_MTM_BldgSmResidentialAlt_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_BldgSmScienceLab_A\\KB3D_MTM_BldgSmScienceLab_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_Equip3DPrinter_A\\KB3D_MTM_Equip3DPrinter_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_EquipCraneMobile_A\\KB3D_MTM_EquipCraneMobile_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_EquipCraneStationary_A\\KB3D_MTM_EquipCraneStationary_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_EquipScissorLift_A\\KB3D_MTM_EquipScissorLift_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_LightPole_Small\\KB3D_MTM_LightPole_Small_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropCargo_A\\KB3D_MTM_PropCargo_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropCargo_B\\KB3D_MTM_PropCargo_B_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropCargo_C\\KB3D_MTM_PropCargo_C_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropCargo_D\\KB3D_MTM_PropCargo_D_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropCrate_A\\KB3D_MTM_PropCrate_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropGenerator_A\\KB3D_MTM_PropGenerator_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropLandingPads_A\\KB3D_MTM_PropLandingPads_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropLargeStairs_A_grp\\KB3D_MTM_PropLargeStairs_A_grp_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropLeisureModule_A\\KB3D_MTM_PropLeisureModule_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropLivingCentral_A_grp\\KB3D_MTM_PropLivingCentral_A_grp_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropPlantingModule_A\\KB3D_MTM_PropPlantingModule_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropPlantingModule_B\\KB3D_MTM_PropPlantingModule_B_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropRaisedModules_A_grp\\KB3D_MTM_PropRaisedModules_A_grp_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropRaisedModules_B_grp\\KB3D_MTM_PropRaisedModules_B_grp_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropRoomModule_A\\KB3D_MTM_PropRoomModule_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropSmallStairs_A\\KB3D_MTM_PropSmallStairs_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropSmallStairs_B\\KB3D_MTM_PropSmallStairs_B_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropStorageModule_A\\KB3D_MTM_PropStorageModule_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropTanks_B\\KB3D_MTM_PropTanks_B_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_PropTowerControl_A\\KB3D_MTM_PropTowerControl_A_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_WalkwayCrossHigh\\KB3D_MTM_WalkwayCrossHigh_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_WalkwayDoubleHigh\\KB3D_MTM_WalkwayDoubleHigh_original.blend',
 'J:\\StandardAssets\\3D\\Published\\KB3D_MTM_WalkwaySingleNoLegs\\KB3D_MTM_WalkwaySingleNoLegs_original.blend',
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_Curved Building\\MaxHay_Curved Building_original.blend'",
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_Curved Building Short\\MaxHay_Curved Building Short_original.blend'",
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_HK Building 1\\MaxHay_HK Building 1_original.blend'",
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_HK Building 2\\MaxHay_HK Building 2_original.blend'",
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_HK Building 3\\MaxHay_HK Building 3_original.blend'",
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_HK Building 4\\MaxHay_HK Building 4_original.blend'",
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_Office Building Medium\\MaxHay_Office Building Medium_original.blend'",
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_Office Building Short\\MaxHay_Office Building Short_original.blend'",
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_Office Building Tall\\MaxHay_Office Building Tall_original.blend'",
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_Regular Building\\MaxHay_Regular Building_original.blend'",
 "'J:\\StandardAssets\\3D\\Published\\MaxHay_Regular Tall Building\\MaxHay_Regular Tall Building_original.blend'",
 'J:\\StandardAssets\\3D\\Published\\misc_buildingcomplex\\misc_buildingcomplex_original.blend',
 'J:\\StandardAssets\\3D\\Published\\misc_crane03\\misc_crane03_original.blend',
 'J:\\StandardAssets\\3D\\Published\\misc_tanks\\misc_tanks_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_apartment_01\\VC_apartment_01_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_apartment_02\\VC_apartment_02_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_building_01\\VC_building_01_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_building_02\\VC_building_02_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_building_03\\VC_building_03_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_building_04\\VC_building_04_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_building_05\\VC_building_05_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_building_06\\VC_building_06_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_building_08\\VC_building_08_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_edge_01\\VC_edge_01_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_edge_02\\VC_edge_02_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_edge_03\\VC_edge_03_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_edge_04\\VC_edge_04_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_edge_05\\VC_edge_05_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_edge_06\\VC_edge_06_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_edge_07\\VC_edge_07_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_industrial_building_01\\VC_industrial_building_01_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_industrial_building_02\\VC_industrial_building_02_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_industrial_hall\\VC_industrial_hall_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_low_building\\VC_low_building_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_low_industry_01\\VC_low_industry_01_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_low_industry_02\\VC_low_industry_02_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_low_industry_03\\VC_low_industry_03_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_low_industry_04\\VC_low_industry_04_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_office_01\\VC_office_01_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_office_02\\VC_office_02_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_office_03\\VC_office_03_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_office_04\\VC_office_04_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_skyscraper_01\\VC_skyscraper_01_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_skyscraper_02\\VC_skyscraper_02_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_skyscraper_03\\VC_skyscraper_03_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_skyscraper_04\\VC_skyscraper_04_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_skyscraper_05\\VC_skyscraper_05_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_skyscraper_06\\VC_skyscraper_06_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_skyscraper_07\\VC_skyscraper_07_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_skyscraper_08\\VC_skyscraper_08_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_skyscraper_09\\VC_skyscraper_09_original.blend',
 'J:\\StandardAssets\\3D\\Published\\VC_skyscraper_10\\VC_skyscraper_10_original.blend',
 'J:\\StandardAssets\\3D\\Published\\Worker_Brown\\Worker_Brown_original.blend',
 'J:\\StandardAssets\\3D\\Published\\Worker_Green\\Worker_Green_original.blend',
 'J:\\StandardAssets\\3D\\Published\\Worker_Grey\\Worker_Grey_original.blend']

paths_proxy1 = []
for path in paths:
    paths_proxy1.append(path.replace("_original", "_proxy1"))

paths_proxy2 = []
for path in paths:
    paths_proxy2.append(path.replace("_original", "_proxy2"))


RENDER_QUEUE = paths + paths_proxy1 + paths_proxy2
#RENDER_QUEUE = [paths[4]]

print("PROCESSING QUEUE:")
pprint(RENDER_QUEUE)

blender_path = '"C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"'
python_script = "C:/Users/Keith/PycharmProjects/MyBlenderProject/asset_scripts/batch_generate_preview.py"

for blender_file in RENDER_QUEUE:
    p = subprocess.Popen(f"{blender_path} {blender_file} --background --python {python_script}", stdout=subprocess.PIPE)

    # print output
    while True:
        output = p.stdout.readline()
        if 'Blender quit' in str(output.strip()):
            break
        if output:
            print(output.strip())
