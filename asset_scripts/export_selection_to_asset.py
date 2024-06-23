import bpy
import os

bake_uvmap_name = "UVMap_Bake"


def find_node(node_tree, node_name):
    try:
        return node_tree.nodes[node_name]
    except KeyError:
        return None


def create_value_node(node_tree, default_value):
    value_node = node_tree.nodes.new("ShaderNodeValue")
    value_node.outputs[0].default_value = default_value
    return value_node


def create_rgb_node(node_tree, default_value):
    rgb_node = node_tree.nodes.new("ShaderNodeRGB")
    rgb_node.outputs[0].default_value = default_value
    return rgb_node


def pre_process_transparent(node_tree):
    transparent = find_node(node_tree, "Transparent BSDF")
    if transparent:
        print("Found transparent")
        metallic_value = create_value_node(node_tree, 0.9)
        alpha_value = create_value_node(node_tree, 0.8)
        emit_color = create_rgb_node(node_tree, (1, 0.928203, 0.333327, 1))
        emit_strength = create_value_node(node_tree, 0.1)

        principled = node_tree.nodes["Principled BSDF"]
        mat_out = node_tree.nodes["Material Output"]

        node_tree.links.new(principled.outputs[0], mat_out.inputs[0])
        node_tree.links.new(metallic_value.outputs[0], principled.inputs[1])
        node_tree.links.new(alpha_value.outputs[0], principled.inputs[4])
        node_tree.links.new(emit_color.outputs[0], principled.inputs[26])
        node_tree.links.new(emit_strength.outputs[0], principled.inputs[27])


def bake_and_save_image(baked_image, path, img_format, bake_type, size, final_size):
    print(f"BAKING {bake_type}")
    if bake_type == "metallic" or bake_type == "alpha":
        bake_type = "emit"
    bpy.ops.object.bake(type=bake_type.upper())

    if size != final_size:
        baked_image.scale(final_size, final_size)

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


def reset_material_after_bake(node_tree, bake_type, emit_nodes):
    if bake_type == "metallic" or bake_type == "alpha":
        print("Preparing to reset")
        bsdf = node_tree.nodes["Principled BSDF"]
        for material_name, emit_node in emit_nodes.items():
            node_tree.links.new(emit_node[0].outputs[0], bsdf.inputs[26])
            node_tree.links.new(emit_node[1].outputs[0], bsdf.inputs[27])


def bake_out_asset_maps(selection, bake_list, asset_name, publish_path, final_size=1024, oversample=1):
    render_settings = {
        "engine": bpy.context.scene.render.engine,
        "samples": bpy.context.scene.cycles.samples,
        "direct_pass": bpy.context.scene.render.bake.use_pass_direct,
        "indirect_pass": bpy.context.scene.render.bake.use_pass_indirect,
        "margin": bpy.context.scene.render.bake.margin,
        "clear_image": bpy.context.scene.render.bake.use_clear
    }

    # Set render settings for baking
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.margin = 1

    size = final_size * oversample
    non_mesh_list = []

    prepared_materials = []
    for ob in selection:
        for material in ob.material_slots:
            if material.name not in prepared_materials:
                node_tree = material.material.node_tree
                pre_process_transparent(node_tree)
                prepared_materials.append(material.name)

    emit_nodes = {}
    for bake_type in bake_list:
        new_image = bpy.data.images.new("bake_" + bake_type, width=size, height=size)
        if bake_type == "alpha":
            new_image.generated_color = (1, 1, 1, 1)
            bpy.context.scene.render.bake.use_clear = False
        else:
            bpy.context.scene.render.bake.use_clear = True
        path = os.path.join(publish_path, "4k", bake_type + ".png")
        img_format = 'PNG'

        prepared_materials = []
        for ob in selection:
            if ob.type == 'MESH':
                for material in ob.material_slots:
                    if material.name not in prepared_materials:
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

                        if bake_type in ["metallic", "alpha"]:
                            bsdf = node_tree.nodes["Principled BSDF"]
                            try:
                                emit_node = bsdf.inputs[26].links[0].from_socket.node
                            except:
                                emit_node = nodes.new("ShaderNodeRGB" if bake_type == "metallic" else "ShaderNodeValue")
                                emit_node.outputs[0].default_value = bsdf.inputs[26].default_value
                            try:
                                strength_node = bsdf.inputs[27].links[0].from_socket.node
                            except:
                                strength_node = nodes.new("ShaderNodeValue")
                                strength_node.outputs[0].default_value = bsdf.inputs[27].default_value

                            emit_nodes[material.name] = [emit_node, strength_node]

                            if bake_type == "metallic":
                                try:
                                    metallic_node = bsdf.inputs[1].links[0].from_socket.node
                                except:
                                    metallic_node = nodes.new("ShaderNodeValue")
                                    metallic_node.outputs[0].default_value = bsdf.inputs[1].default_value
                                node_tree.links.new(metallic_node.outputs[0], bsdf.inputs[26])
                                bake_strength_node = nodes.new("ShaderNodeValue")
                                bake_strength_node.outputs[0].default_value = 1.0
                                node_tree.links.new(bake_strength_node.outputs[0], bsdf.inputs[27])

                            elif bake_type == "alpha":
                                try:
                                    alpha_node = bsdf.inputs[4].links[0].from_socket.node
                                except:
                                    alpha_node = nodes.new("ShaderNodeValue")
                                    alpha_node.outputs[0].default_value = bsdf.inputs[4].default_value
                                node_tree.links.new(alpha_node.outputs[0], bsdf.inputs[26])
                                bake_strength_node = nodes.new("ShaderNodeValue")
                                bake_strength_node.outputs[0].default_value = 1.0
                                node_tree.links.new(bake_strength_node.outputs[0], bsdf.inputs[27])

                        prepared_materials.append(material.name)

            else:
                non_mesh_list.append(ob)
                ob.select_set(False)

        bake_and_save_image(new_image, path, img_format, bake_type, size, final_size)
        reset_material_after_bake(node_tree, bake_type, emit_nodes)

    for ob in non_mesh_list:
        ob.select_set(True)

    # Restore original render settings
    bpy.context.scene.render.engine = render_settings["engine"]
    bpy.context.scene.cycles.samples = render_settings["samples"]
    bpy.context.scene.render.bake.use_pass_direct = render_settings["direct_pass"]
    bpy.context.scene.render.bake.use_pass_indirect = render_settings["indirect_pass"]
    bpy.context.scene.render.bake.margin = render_settings["margin"]
    bpy.context.scene.render.bake.use_clear = render_settings["clear_image"]


def create_material_from_folder(folder, bake_list):
    new_mat = bpy.data.materials.new(os.path.basename(os.path.dirname(folder)))
    new_mat.use_nodes = True
    mat_nodes = new_mat.node_tree.nodes
    bsdf = mat_nodes["Principled BSDF"]
    text_to_input = {"diffuse": 0, "metallic": 1, "roughness": 2, "alpha": 4, "normal": 5, "emit": 26}

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

        bsdf.inputs[27].default_value = 1

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
    # Override options to account for dependencies
    if not options["do_new_uvs"]:
        options["do_bake_textures"] = False
    if not options["do_export"]:
        options["do_center"] = False

    if options["do_new_uvs"]:
        create_baking_uvs(selection)
    if options["do_bake_textures"]:
        bake_out_asset_maps(selection, bake_list, asset_name, publish_path)
        bpy.ops.object.duplicate()
        selection = bpy.context.selected_objects
        new_material = create_material_from_folder(os.path.join(publish_path, "4k"), bake_list)
        for ob in selection:
            if ob.type == 'MESH':
                ob.data.materials.clear()
                uv_map_list = []
                for uvmap in ob.data.uv_layers:
                    uv_map_list.append(uvmap.name)
                for uvmap in uv_map_list:
                    if uvmap == bake_uvmap_name:
                        continue
                    else:
                        ob.data.uv_layers.remove(ob.data.uv_layers[uvmap])
                ob.data.materials.append(new_material)
    if options["do_center"]:
        bpy.context.object.location = [0, 0, 0]
    if options["do_export"]:
        export_selection(publish_path, asset_name)
