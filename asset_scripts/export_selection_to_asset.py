import bpy
import os

bake_uvmap_name = "UVMap_Bake"

def bake_and_save_image(baked_image, path, img_format, bake_type, size, final_size):
    print(f"BAKING {bake_type}")
    bpy.ops.object.bake(type=bake_type.upper())

    if size != final_size:
        baked_image.scale(final_size, final_size)

    # write image
    baked_image.filepath_raw = path
    baked_image.file_format = img_format
    baked_image.save()


def create_baking_uvs(selection):
    for ob in selection:
        if ob.type == 'MESH':
            bake_uvmap = ob.data.uv_layers.new(name=bake_uvmap_name)
            bake_uvmap.active = True
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=0.00001)
    bpy.ops.object.editmode_toggle()


def bake_out_asset_maps(selection, bake_list, asset_name, publish_path, final_size=1024, oversample=1):
    #get render settings
    render_engine = bpy.context.scene.render.engine
    samples = bpy.context.scene.cycles.samples
    direct_pass = bpy.context.scene.render.bake.use_pass_direct
    indirect_pass = bpy.context.scene.render.bake.use_pass_indirect
    margin = bpy.context.scene.render.bake.margin

    #set render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.margin = 0

    size = final_size * oversample

    for bake_type in bake_list:
        new_image = bpy.data.images.new("bake_" + bake_type, width=size, height=size)
        path = os.path.join(publish_path, "4k", bake_type + ".png")
        img_format = 'PNG'
        emit_node = None
        non_obj_list = []

        for ob in selection:
            if ob.type == 'MESH':
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
                    if bake_type == "metallic":
                        bsdf = node_tree.nodes["Principled BSDF"]
                        try:
                            metallic_node = bsdf.inputs[1].links[0].from_socket.node
                        except:
                            metallic_node = nodes.new("ShaderNodeValue")
                            metallic_node.outputs[0].default_value = bsdf.inputs[1].default_value

                        # save emit connection or value
                        try:
                            emit_node = bsdf.inputs[26].links[0].from_socket.node
                        except:
                            emit_node = nodes.new("ShaderNodeRGB")
                            emit_node.outputs[0].default_value = bsdf.inputs[26].default_value

                        # connect metallic node to emit input
                        node_tree.links.new(metallic_node.outputs[0], bsdf.inputs[26])
                        # save emit connection
                        # connect metallic to emit

            else:
                non_obj_list.append(ob)
                ob.select_set(False)

        if bake_type == "metallic":
            bake_and_save_image(new_image, path, img_format, "emit", size, final_size)
        else:
            bake_and_save_image(new_image, path, img_format, bake_type, size, final_size)

        # reset from metallic bake
        # connect saved emit to emit
        if bake_type == "metallic":
            node_tree.links.new(emit_node.outputs[0], bsdf.inputs[26])

    #add non objects back into selection
    for ob in non_obj_list:
        ob.select_set(True)

    #reset render settings
    bpy.context.scene.render.engine = render_engine
    bpy.context.scene.cycles.samples = samples
    bpy.context.scene.render.bake.use_pass_direct = direct_pass
    bpy.context.scene.render.bake.use_pass_indirect = indirect_pass
    bpy.context.scene.render.bake.margin = margin


def create_material_from_folder(folder, bake_list):
    new_mat = bpy.data.materials.new(os.path.basename(folder))
    new_mat.use_nodes = True
    mat_nodes = new_mat.node_tree.nodes
    bsdf = mat_nodes["Principled BSDF"]
    text_to_input = {"diffuse": 0, "metallic": 1, "roughness": 2, "normal": 5, "emit": 26}

    for bake_type in bake_list:
        tex_node = mat_nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(os.path.join(folder, bake_type + ".png"))
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
    if not os.path.exists(publish_path):
        os.mkdir(publish_path)
    export_blend_path_full = os.path.normpath(os.path.join(publish_path, asset_name + ".blend"))
    bpy.ops.object.select_all(action='INVERT')
    bpy.ops.wm.save_as_mainfile(filepath=export_blend_path_full)
    if current_blend_file.endswith(".blend"):
        bpy.ops.wm.open_mainfile(filepath=current_blend_file)

def main(selection, publish_path, asset_name, bake_list, options):

    # override options to account for dependencies
    if not options["do_new_uvs"]:
        options["do_bake_textures"] = False
    if not options["do_export"]:
        options["do_center"] = False

    #let's do it
    if options["do_new_uvs"]:
        create_baking_uvs(selection)
    if options["do_bake_textures"]:
        bake_out_asset_maps(selection, bake_list, asset_name, publish_path)
        bpy.ops.object.duplicate()
        selection = bpy.context.selected_objects
        new_material = create_material_from_folder(os.path.join(publish_path, "4k"), bake_list)
        for ob in selection:
            if ob.type == 'MESH':
                # clean material
                ob.data.materials.clear()
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
    if options["do_center"]:
        bpy.context.object.location = [0, 0, 0]
    if options["do_export"]:
        export_selection(publish_path, asset_name)
