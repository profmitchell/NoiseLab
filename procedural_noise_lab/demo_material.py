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
