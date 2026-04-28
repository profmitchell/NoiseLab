"""Validation and cleanup utilities (PRD §37)."""

import bpy
from .metadata import PROP_RECIPE_ID, PROP_RECIPE_VERSION
from .recipe_registry import recipe_for_group


def _interface_sockets(group, in_out):
    return {
        item.name: item
        for item in group.interface.items_tree
        if getattr(item, 'in_out', None) == in_out
    }


def _socket_type(item):
    return getattr(item, "socket_type", None) or getattr(item, "bl_socket_idname", None)


def _validate_spec(errors, sockets, spec, label):
    for expected in spec:
        name, socket_type = expected[:2]
        socket = sockets.get(name)
        if socket is None:
            errors.append(f"Missing required {label}: {name}")
            continue
        actual_type = _socket_type(socket)
        if actual_type and actual_type != socket_type:
            errors.append(
                f"{label.title()} '{name}' has type {actual_type}; expected {socket_type}"
            )


def _group_output_links(group):
    linked = set()
    for node in group.nodes:
        if node.bl_idname != "NodeGroupOutput":
            continue
        for socket in node.inputs:
            if socket.is_linked:
                linked.add(socket.name)
    return linked


def validate_group(group, required_inputs=None, required_outputs=None):
    """Return list of error strings.  Empty list == valid."""
    errors = []
    if group is None:
        return ["Node group is None."]
    if not group.nodes:
        errors.append("Node group has no internal nodes.")
    inputs = _interface_sockets(group, 'INPUT')
    outputs = _interface_sockets(group, 'OUTPUT')
    input_names = set(inputs)
    output_names = set(outputs)
    for name in (required_inputs or []):
        if name not in input_names:
            errors.append(f"Missing required input: {name}")
    for name in (required_outputs or []):
        if name not in output_names:
            errors.append(f"Missing required output: {name}")

    recipe = recipe_for_group(group)
    if recipe is None:
        if group.name.startswith("INL_"):
            errors.append("Missing or unknown INL recipe metadata.")
        return errors

    if group.get(PROP_RECIPE_ID) != recipe.recipe_id:
        errors.append(
            f"Recipe metadata mismatch: expected {recipe.recipe_id}, "
            f"found {group.get(PROP_RECIPE_ID)!r}."
        )
    if group.get(PROP_RECIPE_VERSION) != recipe.recipe_version:
        errors.append(
            f"Recipe version mismatch: expected {recipe.recipe_version}, "
            f"found {group.get(PROP_RECIPE_VERSION)!r}."
        )

    _validate_spec(errors, inputs, recipe.input_spec, "input")
    _validate_spec(errors, outputs, recipe.output_spec, "output")

    has_group_input = any(n.bl_idname == "NodeGroupInput" for n in group.nodes)
    has_group_output = any(n.bl_idname == "NodeGroupOutput" for n in group.nodes)
    if not has_group_input:
        errors.append("Missing internal Group Input node.")
    if not has_group_output:
        errors.append("Missing internal Group Output node.")

    linked_outputs = _group_output_links(group)
    for name, _socket_type_name in recipe.output_spec:
        if name not in linked_outputs:
            errors.append(f"Output is not linked internally: {name}")
    return errors


def cleanup_unused_inl_groups():
    """Remove node groups with the INL_ prefix that have zero users."""
    removed = []
    for ng in list(bpy.data.node_groups):
        if ng.name.startswith("INL_") and ng.users == 0:
            removed.append(ng.name)
            bpy.data.node_groups.remove(ng)
    return removed
