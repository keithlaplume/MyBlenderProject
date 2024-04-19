import bpy
import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2


selection = bpy.context.selected_objects

res = '4k'

for asset in selection:
    print(asset)
    for material in asset.material_slots:
        for shading_node in material.material.node_tree.nodes:
            if shading_node.type=='TEX_IMAGE':
                file_path = shading_node.image.filepath
                image_name = shading_node.image.name
                print('IMAGE PATH: {}'.format(file_path))
                base_path = os.path.dirname(os.path.dirname(file_path))
                new_path = os.path.join(base_path, res)
                new_image_name_full = os.path.join(new_path, image_name)
                if not os.path.exists(new_path):
                    os.mkdir(new_path)
                if not os.path.exists(new_image_name_full):
                    src = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
                    dsize = (4096, 4096)
                    # resize image
                    output = cv2.resize(src, dsize)
                    cv2.imwrite(new_image_name_full,output)

                print('NEW PATH: {}'.format(new_image_name_full))
                shading_node.image.filepath = new_image_name_full