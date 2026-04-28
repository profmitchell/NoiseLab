"""Animate the Time input of an INL group node (PRD §34 / other ideas §16)."""

import bpy


def _find_time_input(group_node):
    """Return the ``Time`` socket or None."""
    for inp in group_node.inputs:
        if inp.name == "Time":
            return inp
    return None


def animate_time_keyframes(group_node, start_frame=1, end_frame=120,
                           start_val=0.0, end_val=1.0):
    """Insert two linear keyframes on the Time input."""
    sock = _find_time_input(group_node)
    if sock is None:
        return "Group has no Time input."
    sock.default_value = start_val
    sock.keyframe_insert("default_value", frame=start_frame)
    sock.default_value = end_val
    sock.keyframe_insert("default_value", frame=end_frame)

    # Try to set interpolation to linear
    mat = group_node.id_data  # material / node tree owner
    if mat and mat.animation_data and mat.animation_data.action:
        for fc in mat.animation_data.action.fcurves:
            if fc.data_path.endswith(f'inputs[{_socket_index(group_node, sock)}].default_value'):
                for kp in fc.keyframe_points:
                    kp.interpolation = 'LINEAR'
                break
    return None


def clear_time_animation(group_node):
    """Remove keyframes / drivers from the Time input."""
    sock = _find_time_input(group_node)
    if sock is None:
        return "Group has no Time input."
    try:
        sock.keyframe_delete("default_value")
    except Exception:
        pass
    # Remove driver if present
    mat = group_node.id_data
    if mat and mat.animation_data:
        idx = _socket_index(group_node, sock)
        dp = f'nodes["{group_node.name}"].inputs[{idx}].default_value'
        try:
            mat.animation_data.drivers.find(dp)
            mat.node_tree.driver_remove(dp)
        except Exception:
            pass
    return None


def add_time_driver(group_node, speed=1.0):
    """Add a scripted expression driver: Time = frame * speed."""
    sock = _find_time_input(group_node)
    if sock is None:
        return "Group has no Time input."
    tree = group_node.id_data  # material
    if tree is None:
        return "Cannot determine owner node tree."
    idx = _socket_index(group_node, sock)
    dp = f'nodes["{group_node.name}"].inputs[{idx}].default_value'
    try:
        nt = tree.node_tree if hasattr(tree, 'node_tree') else tree
        drv = nt.driver_add(dp).driver
        drv.type = 'SCRIPTED'
        drv.expression = f"frame / bpy.context.scene.render.fps * {speed:.4f}"
        # Simpler fallback that always works without bpy import in driver:
        drv.expression = f"frame * {speed / 24.0:.6f}"
    except Exception as e:
        return str(e)
    return None


def _socket_index(node, socket):
    for i, s in enumerate(node.inputs):
        if s == socket:
            return i
    return 0
