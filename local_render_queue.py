import subprocess

RENDER_QUEUE = [r"J:\UNTITLED_MARS_PROJECT\assets\materials\working_files\mars_sand_smallrocks_albedo.blend"]

blender_path = '"C:/Program Files/Blender Foundation/Blender 3.4/blender.exe"'

for blender_file in RENDER_QUEUE:
    p = subprocess.Popen('{} -b {} -f 1'.format(blender_path, blender_file), stdout=subprocess.PIPE)

    # print output
    while True:
        output = p.stdout.readline()
        if 'Blender quit' in str(output.strip()):
            break
        if output:
            print(output.strip())
