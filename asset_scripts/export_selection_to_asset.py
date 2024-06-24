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
    saved_selection = bpy.context.selected_objects
    active_object = bpy.context.active_object
    for ob in selection:
        ob.select_set(True)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=0.00001)
    bpy.ops.object.editmode_toggle()
    # reset selection
    for ob in saved_selection:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = active_object


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

def get_render_settings():
    render_settings = {
        "engine": bpy.context.scene.render.engine,
        "samples": bpy.context.scene.cycles.samples,
        "direct_pass": bpy.context.scene.render.bake.use_pass_direct,
        "indirect_pass": bpy.context.scene.render.bake.use_pass_indirect,
        "margin": bpy.context.scene.render.bake.margin,
        "clear_image": bpy.context.scene.render.bake.use_clear,
        "selected_to_active": bpy.context.scene.render.bake.use_selected_to_active,
        "cage_extrusion": bpy.context.scene.render.bake.cage_extrusion
    }
    return render_settings

def set_render_settings(engine, samples, direct, indirect, margin, clear, selected_to_active, cage_extrusion):
    bpy.context.scene.render.engine = engine
    bpy.context.scene.cycles.samples = samples
    bpy.context.scene.render.bake.use_pass_direct = direct
    bpy.context.scene.render.bake.use_pass_indirect = indirect
    bpy.context.scene.render.bake.margin = margin
    bpy.context.scene.render.bake.use_clear = clear
    bpy.context.scene.render.bake.use_selected_to_active = selected_to_active
    bpy.context.scene.render.bake.cage_extrusion = cage_extrusion


def create_new_texture_node(node_tree, image, type="Diffuse"):
    tex_node = node_tree.nodes.new("ShaderNodeTexImage")
    tex_node.image = image
    if type in ["Diffuse", "Emit"]:
        image.colorspace_settings.name = "sRGB"
    else:
        image.colorspace_settings.name = "Non-Color"
    uv_node = node_tree.nodes.new("ShaderNodeUVMap")
    uv_node.uv_map = bake_uvmap_name
    node_tree.links.new(uv_node.outputs.get("UV"), tex_node.inputs.get("Vector"))
    node_tree.nodes.active = tex_node

    return tex_node


def bake_to_proxy(bake_list, asset_name, publish_path, final_size=1024, oversample=1):
    # Store original render settings
    render_settings = get_render_settings()

    # Set render settings for baking
    set_render_settings(engine="CYCLES",
                        samples=1,
                        direct=False,
                        indirect=False,
                        margin=1,
                        clear=True,
                        selected_to_active=True,
                        cage_extrusion=0.5)

    size = final_size * oversample

    proxy_object = bpy.context.active_object
    selection = bpy.context.selected_objects
    create_baking_uvs([proxy_object])
    proxy_object.data.materials.clear()
    new_mat = bpy.data.materials.new(asset_name)
    new_mat.use_nodes = True

    proxy_object.data.materials.append(new_mat)

    principled = new_mat.node_tree.nodes.get("Principled BSDF")

    emit_nodes_dict = {}
    prepared_materials = set()

    # prepare alpha
    for ob in selection:
        if ob.type != 'MESH':
            for material in ob.material_slots:
                if material.name in prepared_materials:
                    continue

                node_tree = material.material.node_tree
                pre_process_transparent(node_tree)
                prepared_materials.add(material.name)

    for bake_type in bake_list:
        new_image = bpy.data.images.new(bake_type, width=size, height=size)
        if bake_type == "Alpha":
            new_image.generated_color = (1, 1, 1, 1)
            bpy.context.scene.render.bake.use_clear = False
        else:
            bpy.context.scene.render.bake.use_clear = True

        path = os.path.join(publish_path, "4k", bake_type + ".png")
        img_format = 'PNG'

        tex_node = create_new_texture_node(new_mat.node_tree, new_image, type=bake_type)

        if bake_type == "Normal":
            normal_node = new_mat.node_tree.nodes.new("ShaderNodeNormalMap")
            new_mat.node_tree.links.new(tex_node.outputs.get("Color"), normal_node.inputs.get("Color"))
            new_mat.node_tree.links.new(normal_node.outputs.get("Normal"), principled.inputs.get("Normal"))
        else:
            new_mat.node_tree.links.new(tex_node.outputs.get("Color"), principled.inputs.get(bake_type_to_input[bake_type]))

        principled.inputs.get("Emission Strength").default_value = 1

        prepared_materials.clear()
        if bake_type in non_native_bake_types:
            print({f"NON_NATIVE BAKE TYPE DETECTED: {bake_type}"})
            for ob in selection:
                for material in ob.material_slots:
                    if material.name in prepared_materials:
                        continue
                    print(f"Preparing {material.name}")
                    node_tree = material.material.node_tree
                    emit_nodes = prepare_non_native_bake_types(node_tree, bake_type)
                    emit_node, strength_node = emit_nodes[0], emit_nodes[1]

                    emit_nodes_dict[material.name] = [emit_node, strength_node]
                    prepared_materials.add(material.name)

        print("selection".upper())
        print(selection)
        for ob in selection:
            if ob.type != 'MESH':
                ob.select_set(False)
                continue
        bake_and_save_image(new_image, path, img_format, bake_type, size, final_size)
        if bake_type in non_native_bake_types:
            print("EMIT NODES:")
            for node in emit_nodes_dict:
                print(emit_nodes_dict[node], node)
            reset_material_after_non_native_bake(emit_nodes_dict)


    # Restore original render settings
    set_render_settings(engine=render_settings["engine"],
                        samples=render_settings["samples"],
                        direct=render_settings["direct_pass"],
                        indirect=render_settings["indirect_pass"],
                        margin=render_settings["margin"],
                        clear=render_settings["clear_image"],
                        selected_to_active=render_settings["selected_to_active"],
                        cage_extrusion=render_settings["cage_extrusion"])


def bake_out_asset_maps(selection, bake_list, asset_name, publish_path, final_size=1024, oversample=1):
    # Store original render settings
    render_settings = get_render_settings()

    # Set render settings for baking
    set_render_settings(engine="CYCLES",
                        samples=1,
                        direct=False,
                        indirect=False,
                        margin=1,
                        clear=True,
                        selected_to_active=False,
                        cage_extrusion=0)

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
                create_new_texture_node(node_tree, new_image, type=bake_type)

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
    set_render_settings(engine=render_settings["engine"],
                        samples=render_settings["samples"],
                        direct=render_settings["direct_pass"],
                        indirect=render_settings["indirect_pass"],
                        margin=render_settings["margin"],
                        clear=render_settings["clear_image"],
                        selected_to_active=render_settings["selected_to_active"],
                        cage_extrusion=render_settings["cage_extrusion"])


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
