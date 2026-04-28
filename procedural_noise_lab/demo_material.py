"""Create demo material and Geometry Nodes setups wired to INL groups."""

import bpy

from .interface_utils import new_input, new_output


MASK_OUTPUT_PRIORITY = (
    "Height",
    "Fac",
    "Soft Mask",
    "Mask",
    "Hard Mask",
    "Edge Mask",
)


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


def create_demo_geometry_setup(
    group_name="INL_Infinite_4D_Noise_Geo",
    mode='GRID',
    grid_size=2.0,
    grid_vertices=100,
    displacement_strength=0.12,
):
    """Build a Geometry Nodes modifier setup on the active object.

    GRID mode creates a generated mesh grid, preserving the original quick demo.
    ACTIVE mode uses the object's incoming geometry. Both modes sample Position,
    displace along normals, and store a named float attribute for materials.
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

    for n in list(tree.nodes):
        tree.nodes.remove(n)
    for item in list(tree.interface.items_tree):
        tree.interface.remove(item)

    mode = mode if mode in {'GRID', 'ACTIVE'} else 'GRID'
    if mode == 'ACTIVE':
        new_input(tree, "Geometry", "NodeSocketGeometry")
    else:
        new_input(tree, "Grid Size", "NodeSocketFloat", default=grid_size, min_value=0.1, max_value=100.0)
        new_input(tree, "Grid Vertices", "NodeSocketInt", default=grid_vertices, min_value=2, max_value=1000)
    new_input(tree, "Displacement Strength", "NodeSocketFloat", default=displacement_strength, min_value=-10.0, max_value=10.0)
    new_input(tree, "Time", "NodeSocketFloat", default=0.0, min_value=None, max_value=None)
    new_input(tree, "Attribute Name", "NodeSocketString", default="inl_mask")
    new_output(tree, "Geometry", "NodeSocketGeometry")

    g_in = tree.nodes.new("NodeGroupInput")
    g_in.location = (-1000, 120)

    if mode == 'GRID':
        grid = tree.nodes.new("GeometryNodeMeshGrid")
        grid.location = (-760, 160)
        grid.inputs["Size X"].default_value = grid_size
        grid.inputs["Size Y"].default_value = grid_size
        grid.inputs["Vertices X"].default_value = grid_vertices
        grid.inputs["Vertices Y"].default_value = grid_vertices
        tree.links.new(g_in.outputs["Grid Size"], grid.inputs["Size X"])
        tree.links.new(g_in.outputs["Grid Size"], grid.inputs["Size Y"])
        tree.links.new(g_in.outputs["Grid Vertices"], grid.inputs["Vertices X"])
        tree.links.new(g_in.outputs["Grid Vertices"], grid.inputs["Vertices Y"])

    set_pos = tree.nodes.new("GeometryNodeSetPosition")
    set_pos.location = (120, 120)

    grp = tree.nodes.new("GeometryNodeGroup")
    grp.node_tree = group
    grp.location = (-620, -180)

    pos_input = tree.nodes.new("GeometryNodeInputPosition")
    pos_input.location = (-880, -180)

    normal_input = tree.nodes.new("GeometryNodeInputNormal")
    normal_input.location = (-240, -120)

    scale_normal = tree.nodes.new("ShaderNodeVectorMath")
    scale_normal.operation = 'SCALE'
    scale_normal.location = (-20, -120)

    scalar_scale = tree.nodes.new("ShaderNodeMath")
    scalar_scale.operation = 'MULTIPLY'
    scalar_scale.location = (-240, -360)

    store_attr = tree.nodes.new("GeometryNodeStoreNamedAttribute")
    store_attr.data_type = 'FLOAT'
    store_attr.domain = 'POINT'
    store_attr.location = (360, 120)

    out = tree.nodes.new("NodeGroupOutput")
    out.location = (620, 120)

    scalar_output_name = next((name for name in MASK_OUTPUT_PRIORITY if name in grp.outputs), None)
    if scalar_output_name is None:
        return None, f"Node group '{group_name}' has no usable scalar output."

    if mode == 'ACTIVE':
        tree.links.new(g_in.outputs["Geometry"], set_pos.inputs["Geometry"])
    else:
        tree.links.new(grid.outputs["Mesh"], set_pos.inputs["Geometry"])
    tree.links.new(pos_input.outputs["Position"], grp.inputs["Vector"])

    if "Time" in grp.inputs:
        tree.links.new(g_in.outputs["Time"], grp.inputs["Time"])

    scalar_socket = grp.outputs[scalar_output_name]
    tree.links.new(scalar_socket, scalar_scale.inputs[0])
    tree.links.new(g_in.outputs["Displacement Strength"], scalar_scale.inputs[1])
    tree.links.new(normal_input.outputs["Normal"], scale_normal.inputs[0])
    tree.links.new(scalar_scale.outputs[0], scale_normal.inputs["Scale"])
    tree.links.new(scale_normal.outputs["Vector"], set_pos.inputs["Offset"])

    tree.links.new(set_pos.outputs["Geometry"], store_attr.inputs["Geometry"])
    tree.links.new(g_in.outputs["Attribute Name"], store_attr.inputs["Name"])
    tree.links.new(scalar_socket, store_attr.inputs["Value"])
    tree.links.new(store_attr.outputs["Geometry"], out.inputs["Geometry"])

    source_label = "active geometry" if mode == 'ACTIVE' else "generated grid"
    return mod, f"Created '{mod_name}' on '{obj.name}' using {source_label} and '{scalar_output_name}'."
