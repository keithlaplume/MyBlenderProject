import subprocess

RENDER_QUEUE = [r"J:\StandardAssets\3D\Published\KB3D_MTM_BldgLgPowerStation_A\KB3D_MTM_BldgLgPowerStation_A_proxy1.blend"]

blender_path = '"C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"'
python_script = "C:/Users/Keith/PycharmProjects/MyBlenderProject/asset_scripts/build_collection_and_mark_asset.py"

for blender_file in RENDER_QUEUE:
    p = subprocess.Popen(f"{blender_path} {blender_file} --background --python {python_script}", stdout=subprocess.PIPE)

    # print output
    while True:
        output = p.stdout.readline()
        if 'Blender quit' in str(output.strip()):
            break
        if output:
            print(output.strip())