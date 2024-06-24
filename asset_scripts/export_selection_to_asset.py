import bpy
import os

bake_uvmap_name = "UVMap_Bake"
non_native_bake_types = ["Metallic", "Alpha"]
bake_type_to_input = {"Diffuse": "Base Color",
                      "Metallic": "Metallic",
                      "Emit": "Emission Color",
                      "Roughness": "Roughness",
                      "Normal": "Normal",
                      "Alpha": "Alpha"}

def create_value_node(node_tree, default_value):
    value_node = node_tree.nodes.new("ShaderNodeValue")
    value_node.outputs.get("Value").default_value = default_value
    return value_node

def create_rgb_node(node_tree, default_value):
    rgb_node = node_tree.nodes.new("ShaderNodeRGB")
    rgb_node.outputs.get("Color").default_value = default_value
    return rgb_node

def pre_process_transparent(node_tree):
    transparent = node_tree.nodes.get("Transparent BSDF")
    if transparent:
        print("Found material with transparency")
        metallic_value = create_value_node(node_tree, 0.9)
        alpha_value = create_value_node(node_tree, 0.8)
        emit_color = create_rgb_node(node_tree, (1, 0.928203, 0.333327, 1))
        emit_strength = create_value_node(node_tree, 0.1)

        principled = node_tree.nodes.get("Principled BSDF")
        mat_out = node_tree.nodes.get("Material Output")

        if principled and mat_out:
            node_tree.links.new(principled.outputs.get("BSDF"), mat_out.inputs.get("Surface"))
            node_tree.links.new(metallic_value.outputs.get("Value"), principled.inputs.get("Metallic"))
            node_tree.links.new(alpha_value.outputs.get("Value"), principled.inputs.get("Alpha"))
            node_tree.links.new(emit_color.outputs.get("Color"), principled.inputs.get("Emission Color"))
            node_tree.links.new(emit_strength.outputs.get("Value"), principled.inputs.get("Emission Strength"))
        else:
            print("Unable to find required nodes for Transparency Preprocessing. Skipping...")

def bake_and_save_image(baked_image, path, img_format, bake_type, size, final_size):
    print(f"BAKING {bake_type}")
    if bake_type in non_native_bake_types:
        bake_type = "Emit"
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


def reset_material_after_non_native_bake(emit_nodes):
        print("Preparing to reset")
        for material_name, emit_node in emit_nodes.items():
            node_tree = bpy.data.materials[material_name].node_tree
            principled = node_tree.nodes.get("Principled BSDF")
            node_tree.links.new(emit_node[0].outputs[0], principled.inputs.get("Emission Color"))
            node_tree.links.new(emit_node[1].outputs[0], principled.inputs.get("Emission Strength"))

def prepare_non_native_bake_types(node_tree, bake_type):
    emit_nodes = {}
    nodes = node_tree.nodes
    principled = node_tree.nodes.get("Principled BSDF")

    if principled:
        try:
            emit_node = principled.inputs.get("Emission Color").links[0].from_socket.node
        except:
            emit_node = nodes.new("ShaderNodeRGB")
            emit_node.outputs.get("Color").default_value = principled.inputs.get("Emission Color").default_value

        try:
            strength_node = principled.inputs.get("Emission Strength").links[0].from_socket.node
        except:
            strength_node = nodes.new("ShaderNodeValue")
            strength_node.outputs.get("Value").default_value = principled.inputs.get("Emission Strength").default_value

        emit_nodes = [emit_node, strength_node]

        try:
            non_native_node = principled.inputs.get(bake_type).links[0].from_socket.node
        except:
            non_native_node = nodes.new("ShaderNodeValue")
            non_native_node.outputs.get("Value").default_value = principled.inputs.get(bake_type).default_value

        node_tree.links.new(non_native_node.outputs[0], principled.inputs.get("Emission Color"))
        bake_strength_node = nodes.new("ShaderNodeValue")
        bake_strength_node.outputs.get("Value").default_value = 1.0
        node_tree.links.new(bake_strength_node.outputs.get("Value"), principled.inputs.get("Emission Strength"))

    return emit_nodes

def bake_out_asset_maps(selection, bake_list, asset_name, publish_path, final_size=1024, oversample=1):
    # Store original render settings
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
    prepared_materials = set()

    for ob in selection:
        if ob.type != 'MESH':
            non_mesh_list.append(ob)
            ob.select_set(False)
            continue

        for material in ob.material_slots:
            if material.name in prepared_materials:
                continue

            node_tree = material.material.node_tree
            pre_process_transparent(node_tree)
            prepared_materials.add(material.name)

    emit_nodes_dict = {}
    for bake_type in bake_list:
        new_image = bpy.data.images.new("bake_" + bake_type, width=size, height=size)
        if bake_type == "Alpha":
            new_image.generated_color = (1, 1, 1, 1)
            bpy.context.scene.render.bake.use_clear = False
        else:
            bpy.context.scene.render.bake.use_clear = True

        path = os.path.join(publish_path, "4k", bake_type + ".png")
        img_format = 'PNG'

        prepared_materials.clear()

        for ob in selection:
            if ob.type != 'MESH':
                continue

            for material in ob.material_slots:
                if material.name in prepared_materials:
                    continue

                node_tree = material.material.node_tree
                nodes = node_tree.nodes
                tex_node = nodes.new("ShaderNodeTexImage")
                tex_node.image = new_image
                if bake_type in ["Diffuse", "Emit"]:
                    new_image.colorspace_settings.name = "sRGB"
                else:
                    new_image.colorspace_settings.name = "Non-Color"
                uv_node = nodes.new("ShaderNodeUVMap")
                uv_node.uv_map = bake_uvmap_name
                node_tree.links.new(uv_node.outputs.get("UV"), tex_node.inputs.get("Vector"))
                nodes.active = tex_node

                if bake_type in non_native_bake_types:
                    emit_nodes = prepare_non_native_bake_types(node_tree, bake_type)
                    emit_node, strength_node = emit_nodes[0], emit_nodes[1]

                    emit_nodes_dict[material.name] = [emit_node, strength_node]

                prepared_materials.add(material.name)

        bake_and_save_image(new_image, path, img_format, bake_type, size, final_size)
        if bake_type in non_native_bake_types:
            reset_material_after_non_native_bake(emit_nodes_dict)

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
    principled = mat_nodes.get("Principled BSDF")

    for bake_type in bake_list:
        tex_node = mat_nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(os.path.join(folder, bake_type + ".png"))
        if bake_type in ["Diffuse", "Emit"]:
            tex_node.image.colorspace_settings.name = "sRGB"
        else:
            tex_node.image.colorspace_settings.name = "Non-Color"

        if bake_type == "Normal":
            normal_node = new_mat.node_tree.nodes.new("ShaderNodeNormalMap")
            new_mat.node_tree.links.new(tex_node.outputs.get("Color"), normal_node.inputs.get("Color"))
            new_mat.node_tree.links.new(normal_node.outputs.get("Normal"), principled.inputs.get("Normal"))
        else:
            new_mat.node_tree.links.new(tex_node.outputs.get("Color"), principled.inputs.get(bake_type_to_input[bake_type]))

        principled.inputs.get("Emission Strength").default_value = 1

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
    if not options.get("do_new_uvs"):
        options["do_bake_textures"] = False
    if not options.get("do_export"):
        options["do_center"] = False

    if options.get("do_new_uvs"):
        create_baking_uvs(selection)
    if options.get("do_bake_textures"):
        bake_out_asset_maps(selection, bake_list, asset_name, publish_path)
        bpy.ops.object.duplicate()
        selection = bpy.context.selected_objects
        new_material = create_material_from_folder(os.path.join(publish_path, "4k"), bake_list)
        for ob in selection:
            if ob.type == 'MESH':
                ob.data.materials.clear()
                uv_map_list = [uvmap.name for uvmap in ob.data.uv_layers]
                for uvmap in uv_map_list:
                    if uvmap == bake_uvmap_name:
                        continue
                    else:
                        ob.data.uv_layers.remove(ob.data.uv_layers.get(uvmap))
                ob.data.materials.append(new_material)
    if options.get("do_center"):
        bpy.context.object.location = [0, 0, 0]
    if options.get("do_export"):
        export_selection(publish_path, asset_name)
