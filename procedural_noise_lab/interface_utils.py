"""Blender 4.x node tree interface helpers.

In Blender 4.0+ node group sockets live on ``node_tree.interface`` instead of
``node_tree.inputs`` / ``node_tree.outputs``. These helpers wrap that API so
the rest of the add-on can stay terse.
"""

import bpy


def new_input(tree, name, socket_type, default=None, min_value=None, max_value=None):
    sock = tree.interface.new_socket(name=name, in_out='INPUT', socket_type=socket_type)
    if default is not None and hasattr(sock, "default_value"):
        try:
            sock.default_value = default
        except Exception:
            pass
    if min_value is not None and hasattr(sock, "min_value"):
        sock.min_value = min_value
    if max_value is not None and hasattr(sock, "max_value"):
        sock.max_value = max_value
    return sock


def new_output(tree, name, socket_type):
    return tree.interface.new_socket(name=name, in_out='OUTPUT', socket_type=socket_type)


def _wipe_group(group):
    for n in list(group.nodes):
        group.nodes.remove(n)
    for item in list(group.interface.items_tree):
        group.interface.remove(item)


def get_or_create_group(name, tree_type='ShaderNodeTree', policy='REBUILD'):
    """Return a node group ready to be built into.

    policy:
      - 'REUSE'   : if a matching group exists, return it untouched (caller
                    should detect this and skip building).
      - 'REBUILD' : if an unused match exists, wipe and rebuild it. If the
                    existing group has users, create a fresh suffixed copy so
                    other materials are not changed unexpectedly.
      - 'SUFFIX'  : always create a fresh group (Blender adds .001 etc).
    """
    existing = bpy.data.node_groups.get(name)
    matches = existing is not None and existing.bl_idname == tree_type

    if policy == 'REUSE' and matches:
        return existing, True  # (group, reused)
    if policy == 'SUFFIX':
        return bpy.data.node_groups.new(name, tree_type), False
    # REBUILD (default). Do not mutate a group already used by materials,
    # modifiers, or appended node trees; rebuilding in place would change every
    # user of that datablock.
    if matches:
        if existing.users > 0:
            return bpy.data.node_groups.new(name, tree_type), False
        _wipe_group(existing)
        return existing, False
    return bpy.data.node_groups.new(name, tree_type), False


def add_group_io(tree):
    inp = tree.nodes.new("NodeGroupInput")
    out = tree.nodes.new("NodeGroupOutput")
    inp.location = (-900, 0)
    out.location = (900, 0)
    return inp, out
