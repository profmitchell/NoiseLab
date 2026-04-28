"""Create a demo material wired to an INL node group (PRD §25)."""

import bpy


def create_demo_material(group_name="INL_Infinite_4D_Noise"):
    """Build INL_Demo_Material on the active object.

    Wires: TexCoord → group → ColorRamp → Base Color,
           group.Height → Bump → Normal.
    Returns the material or None on error.
    """
    obj = bpy.context.active_object
    if obj is None:
        return None, "Select an object first."

    group = bpy.data.node_groups.get(group_name)
    if group is None:
        return None, f"Node group '{group_name}' not found. Build it first."

    mat_name = "INL_Demo_Material"
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    tree = mat.node_tree

    # Clear existing nodes
    for n in list(tree.nodes):
        tree.nodes.remove(n)

    # Nodes
    tc = tree.nodes.new("ShaderNodeTexCoord")
    tc.location = (-600, 300)

    grp = tree.nodes.new("ShaderNodeGroup")
    grp.node_tree = group
    grp.location = (-300, 300)

    ramp = tree.nodes.new("ShaderNodeValToRGB")
    ramp.location = (100, 300)

    bump = tree.nodes.new("ShaderNodeBump")
    bump.location = (100, 0)
    bump.inputs["Strength"].default_value = 0.3

    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (450, 300)

    out = tree.nodes.new("ShaderNodeOutputMaterial")
    out.location = (750, 300)

    # Links
    tree.links.new(tc.outputs["Generated"], grp.inputs["Vector"])
    if "Fac" in grp.outputs:
        tree.links.new(grp.outputs["Fac"], ramp.inputs["Fac"])
    tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    if "Height" in grp.outputs:
        tree.links.new(grp.outputs["Height"], bump.inputs["Height"])
    tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Assign to active object
    if obj.data and hasattr(obj.data, "materials"):
        if mat.name not in [m.name for m in obj.data.materials if m]:
            obj.data.materials.append(mat)
        obj.active_material = mat

    return mat, f"Created '{mat_name}' on '{obj.name}'."


def create_demo_geometry_setup(group_name="INL_Infinite_4D_Noise_Geo"):
    """Build a Geometry Nodes modifier setup on the active object.

    Wires: Grid → Set Position (Displacement) → Group Output.
    """
    obj = bpy.context.active_object
    if obj is None:
        return None, "Select an object first."

    group = bpy.data.node_groups.get(group_name)
    if group is None:
        return None, f"Node group '{group_name}' not found. Build it first."

    mod_name = "INL_Demo_Setup"
    mod = obj.modifiers.get(mod_name)
    if mod is None:
        mod = obj.modifiers.new(mod_name, 'NODES')
    
    tree = mod.node_group
    if tree is None:
        tree = bpy.data.node_groups.new(mod_name + "_Tree", 'GeometryNodeTree')
        mod.node_group = tree

    # Clear existing nodes
    for n in list(tree.nodes):
        tree.nodes.remove(n)

    # Nodes
    grid = tree.nodes.new("GeometryNodeMeshGrid")
    grid.location = (-400, 0)
    grid.inputs["Size X"].default_value = 2.0
    grid.inputs["Size Y"].default_value = 2.0
    grid.inputs["Vertices X"].default_value = 100
    grid.inputs["Vertices Y"].default_value = 100

    set_pos = tree.nodes.new("GeometryNodeSetPosition")
    set_pos.location = (-100, 0)

    grp = tree.nodes.new("GeometryNodeGroup")
    grp.node_tree = group
    grp.location = (-400, -200)

    comb = tree.nodes.new("ShaderNodeCombineXYZ")  # CombineXYZ is used in Geo Nodes too
    comb.location = (-250, -200)

    out = tree.nodes.new("NodeGroupOutput")
    out.location = (200, 0)
    tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # Links
    tree.links.new(grid.outputs["Mesh"], set_pos.inputs["Geometry"])
    
    # Use position as vector if it exists
    pos_input = tree.nodes.new("GeometryNodeInputPosition")
    pos_input.location = (-600, -200)
    tree.links.new(pos_input.outputs["Position"], grp.inputs["Vector"])

    if "Height" in grp.outputs:
        tree.links.new(grp.outputs["Height"], comb.inputs["Z"])
        tree.links.new(comb.outputs["Vector"], set_pos.inputs["Offset"])

    tree.links.new(set_pos.outputs["Geometry"], out.inputs["Geometry"])

    return mod, f"Created '{mod_name}' on '{obj.name}'."
