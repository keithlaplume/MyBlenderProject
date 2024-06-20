import bpy
import os

bake_uvmap_name = "UVMap_Bake"


def bake_out_asset_maps(selection, bake_list, asset_name, publish_path, final_size=4096, oversample=2):
    for ob in selection:
        bake_uvmap = ob.data.uv_layers.new(name=bake_uvmap_name)
        bake_uvmap.active = True

    for bake_type in bake_list:
        size = final_size * oversample
        new_image = bpy.data.images.new("bake_" + bake_type, width=size, height=size)
        for ob in selection:
            for material in ob.material_slots:
                node_tree = material.material.node_tree
                nodes = node_tree.nodes
                tex_node = nodes.new("ShaderNodeTexImage")
                tex_node.image = new_image
                if bake_type == "diffuse" or bake_type == "emit":
                    new_image.colorspace_settings.name = "sRGB"
                else:
                    new_image.colorspace_settings.name = "Non-Color"
                uv_node = nodes.new("ShaderNodeUVMap")
                uv_node.uv_map = bake_uvmap_name
                node_tree.links.new(uv_node.outputs[0], tex_node.inputs[0])
                nodes.active = tex_node

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(island_margin=0.00001)
            bpy.ops.object.editmode_toggle()

            bpy.ops.object.bake(type=bake_type.upper())
            new_image.scale(final_size, final_size)

            # write image
            new_image.filepath_raw = os.path.join(publish_path, asset_name, bake_type + ".jpg")
            new_image.file_format = 'JPEG'
            new_image.save()


def create_material_from_folder(folder, bake_list):
    new_mat = bpy.data.materials.new(os.path.basename(folder))
    new_mat.use_nodes = True
    mat_nodes = new_mat.node_tree.nodes
    bsdf = mat_nodes["Principled BSDF"]
    text_to_input = {"diffuse": 0, "roughness": 2, "normal": 5, "emit": 26}

    for bake_type in bake_list:
        tex_node = mat_nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(os.path.join(folder, bake_type + ".jpg"))
        if bake_type == "diffuse" or bake_type == "emit":
            tex_node.image.colorspace_settings.name = "sRGB"
        else:
            tex_node.image.colorspace_settings.name = "Non-Color"
        if bake_type == "normal":
            normal_node = new_mat.node_tree.nodes.new("ShaderNodeNormalMap")
            new_mat.node_tree.links.new(tex_node.outputs[0], normal_node.inputs[1])
            new_mat.node_tree.links.new(normal_node.outputs[0], bsdf.inputs[text_to_input[bake_type]])
        else:
            new_mat.node_tree.links.new(tex_node.outputs[0], bsdf.inputs[text_to_input[bake_type]])

    return new_mat


def export_selection(publish_path, asset_name):
    bpy.ops.object.select_all(action='INVERT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    current_blend_file = bpy.data.filepath
    export_blend_path_full = os.path.join(publish_path, asset_name, asset_name + ".blend")
    bpy.ops.object.select_all(action='INVERT')
    bpy.ops.wm.save_as_mainfile(filepath=export_blend_path_full)
    bpy.ops.wm.open_mainfile(filepath=current_blend_file)

def main(selection, publish_path, asset_name, bake_list, options):
    bake_out_asset_maps(selection, bake_list, asset_name, publish_path)

    # duplicate
    bpy.ops.object.duplicate()
    selection = bpy.context.selected_objects

    new_material = create_material_from_folder(os.path.join(publish_path, asset_name), bake_list)

    for ob in selection:
        # clean material
        for i in range(len(ob.material_slots)):
            bpy.context.object.active_material_index = i
            bpy.ops.object.material_slot_remove()
        # clean uv maps
        uv_map_list = []
        for uvmap in ob.data.uv_layers:
            print(uvmap.name)
            uv_map_list.append(uvmap.name)

        for uvmap in uv_map_list:
            if uvmap == bake_uvmap_name:
                continue
            else:
                ob.data.uv_layers.remove(ob.data.uv_layers[uvmap])

        # set material
        ob.data.materials.append(new_material)
        # set location
        bpy.context.object.location = [0, 0, 0]

    export_selection(publish_path, asset_name)
