import bpy

selection = bpy.context.selected_objects

for ob in selection:
    for material in ob.material_slots:
        node_tree = material.material.node_tree
        principled = node_tree.nodes.get("Principled BSDF")

        # fix transmission weight
        principled.inputs.get('Transmission Weight').default_value = 0

        # delete reflection texture
        try:
            metallic_node = principled.inputs.get("Metallic").links[0].from_socket.node
            node_tree.nodes.remove(metallic_node)
        except:
            pass

        # swap roughness
        try:
            roughness = principled.inputs.get("Specular IOR Level").links[0].from_socket.node
            node_tree.links.remove(principled.inputs.get("Specular IOR Level").links[0])

            color_ramp = node_tree.nodes.new("ShaderNodeValToRGB")
            color_ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
            color_ramp.color_ramp.elements[1].color = (0, 0, 0, 1)

            node_tree.links.new(roughness.outputs[0], color_ramp.inputs[0])
            node_tree.links.new(color_ramp.outputs[0], principled.inputs.get("Roughness"))
        except:
            pass

        # fix normal map
        try:
            normal_map = principled.inputs.get("Normal").links[0].from_socket.node
            normal_map.inputs[0].default_value = 0.5
            normal_map.inputs[1].links[0].from_socket.node.image.colorspace_settings.name = "Non-Color"
        except:
            pass