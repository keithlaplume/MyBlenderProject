import subprocess

RENDER_QUEUE = [r"J:\UNTITLED_MARS_PROJECT\assets\materials\working_files\mars_sand_smallrocks_albedo.blend",
                r"J:\UNTITLED_MARS_PROJECT\assets\materials\working_files\mars_sand_smallrocks_roughness.blend",
                r"J:\UNTITLED_MARS_PROJECT\assets\materials\working_files\mars_sand_allrocks_albedo.blend",
                r"J:\UNTITLED_MARS_PROJECT\assets\materials\working_files\mars_sand_allrocks_roughness.blend",
                r"J:\UNTITLED_MARS_PROJECT\assets\materials\working_files\mars_sand_bigrocks_albedo.blend",
                r"J:\UNTITLED_MARS_PROJECT\assets\materials\working_files\mars_sand_bigrocks_roughness.blend",
                r"J:\UNTITLED_MARS_PROJECT\assets\materials\working_files\mars_sand_pebbles_albedo.blend",
                r"J:\UNTITLED_MARS_PROJECT\assets\materials\working_files\mars_sand_pebbles_roughness.blend"]

blender_path = '"C:/Program Files/Blender Foundation/Blender 3.4/blender.exe"'

for blender_file in RENDER_QUEUE:
    p = subprocess.Popen('{} -b {} -f 1'.format(blender_path, blender_file), stdout=subprocess.PIPE)

    # print output
    while True:
        output = p.stdout.readline()
        if output == '' and p.poll() is not None:
            break
        if output:
            print(output.strip())
