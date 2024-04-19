import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2

res = ["2K", 2048, 2048]
maps_folder = ""
root_folder = os.path.dirname(maps_folder)
new_res_folder = os.path.join(root_folder, res[0])
if not os.path.exists(new_res_folder):
    os.mkdir(new_res_folder)
for img in os.listdir(maps_folder):
    file_path = os.path.join(maps_folder, img)
    new_image_name_full = os.path.join(new_res_folder, img)
    src = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    dsize = (res[1], res[1])
    # resize image
    output = cv2.resize(src, dsize)
    cv2.imwrite(new_image_name_full, output)
