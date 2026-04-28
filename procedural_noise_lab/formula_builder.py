"""Compile a sequence of named operations into a Blender shader node group.

The user picks operations from a fixed safe vocabulary (no eval / no Python
expressions are evaluated). Each operation appends nodes to a chain and
exposes its tweakable parameters on the group interface so the result is
indistinguishable from a hand-built node group.
"""

import bpy

from .interface_utils import (
    get_or_create_group,
    add_group_io,
    new_input,
    new_output,
)


# Safe whitelist of operation identifiers.
OP_TYPES = (
    ('NOISE',      "Noise",       "4D noise sample of the current vector"),
    ('VORONOI',    "Voronoi",     "4D Voronoi distance of the current vector"),
    ('WAVE',       "Wave",        "Wave texture of the current vector"),
    ('SINE',       "Sine",        "sin(value)"),
    ('MULTIPLY',   "Multiply",    "value * parameter"),
    ('ADD',        "Add",         "value + parameter"),
    ('POWER',      "Power",       "value ^ parameter"),
    ('CLAMP',      "Clamp",       "clamp(value, min, max)"),
    ('SMOOTHSTEP', "Smoothstep",  "smoothstep(edge0, edge1, value)"),
    ('COLORRAMP',  "ColorRamp",   "Map value through a ColorRamp"),
    ('DISTORTION', "Distortion",  "Perturb the current vector by a noise field"),
)
OP_LABELS = {k: v for k, v, _ in OP_TYPES}


def _link(tree, a, b):
    tree.links.new(a, b)


def _math(tree, op, loc):
    n = tree.nodes.new("ShaderNodeMath")
    n.operation = op
    n.location = loc
    return n


def _vmath(tree, op, loc):
    n = tree.nodes.new("ShaderNodeVectorMath")
    n.operation = op
    n.location = loc
    return n


def build_formula_group(group_name, operations):
    """Build a shader node group named ``group_name`` from a list of dicts:

    Each entry:  {"op": <OP id>, "param1": float, "param2": float}

    param1/param2 meanings depend on the op (see code).
    """
    tree, _ = get_or_create_group(group_name, "ShaderNodeTree", policy='REBUILD')

    # Base interface
    new_input(tree, "Vector", "NodeSocketVector", default=(0.0, 0.0, 0.0))
    new_input(tree, "W",      "NodeSocketFloat",  default=0.0)
    new_input(tree, "Scale",  "NodeSocketFloat",  default=5.0)
    new_output(tree, "Fac",   "NodeSocketFloat")
    new_output(tree, "Color", "NodeSocketColor")

    g_in, g_out = add_group_io(tree)

    # Running sockets along the chain.
    cur_vec = g_in.outputs["Vector"]
    cur_w   = g_in.outputs["W"]
    cur_val = None        # float socket
    cur_col = None        # color socket
    x = -700
    step = 220

    def expose_param(label, default, op_index, slot):
        name = f"Op{op_index+1} {label}"
        new_input(tree, name, "NodeSocketFloat", default=default)
        # Re-fetch the input socket from the (refreshed) group input node.
        return g_in.outputs[name]

    for i, entry in enumerate(operations):
        op = entry.get("op", "NOISE")
        p1 = float(entry.get("param1", 0.0))
        p2 = float(entry.get("param2", 1.0))
        x += step
        y = 0

        if op == 'NOISE':
            n = tree.nodes.new("ShaderNodeTexNoise")
            n.noise_dimensions = '4D'
            n.location = (x, y)
            _link(tree, cur_vec, n.inputs["Vector"])
            _link(tree, cur_w,   n.inputs["W"])
            _link(tree, g_in.outputs["Scale"], n.inputs["Scale"])
            n.inputs["Detail"].default_value = max(0.0, p1) if p1 else 6.0
            n.inputs["Roughness"].default_value = max(0.0, min(1.0, p2)) if p2 else 0.5
            cur_val = n.outputs["Fac"]
            cur_col = n.outputs["Color"]

        elif op == 'VORONOI':
            n = tree.nodes.new("ShaderNodeTexVoronoi")
            n.voronoi_dimensions = '4D'
            n.feature = 'F1'
            n.location = (x, y)
            _link(tree, cur_vec, n.inputs["Vector"])
            _link(tree, cur_w,   n.inputs["W"])
            _link(tree, g_in.outputs["Scale"], n.inputs["Scale"])
            if "Randomness" in n.inputs:
                n.inputs["Randomness"].default_value = max(0.0, min(1.0, p1)) if p1 else 1.0
            cur_val = n.outputs["Distance"]
            cur_col = n.outputs["Color"]

        elif op == 'WAVE':
            n = tree.nodes.new("ShaderNodeTexWave")
            n.location = (x, y)
            _link(tree, cur_vec, n.inputs["Vector"])
            _link(tree, g_in.outputs["Scale"], n.inputs["Scale"])
            n.inputs["Distortion"].default_value = p1
            n.inputs["Detail"].default_value = max(0.0, p2)
            cur_val = n.outputs["Fac"]
            cur_col = n.outputs["Color"]

        elif op == 'SINE':
            if cur_val is None:
                continue
            n = _math(tree, 'SINE', (x, y))
            _link(tree, cur_val, n.inputs[0])
            cur_val = n.outputs[0]

        elif op == 'MULTIPLY':
            if cur_val is None:
                continue
            sock = expose_param("Factor", p1 if p1 else 1.0, i, 1)
            n = _math(tree, 'MULTIPLY', (x, y))
            _link(tree, cur_val, n.inputs[0])
            _link(tree, sock,    n.inputs[1])
            cur_val = n.outputs[0]

        elif op == 'ADD':
            if cur_val is None:
                continue
            sock = expose_param("Offset", p1, i, 1)
            n = _math(tree, 'ADD', (x, y))
            _link(tree, cur_val, n.inputs[0])
            _link(tree, sock,    n.inputs[1])
            cur_val = n.outputs[0]

        elif op == 'POWER':
            if cur_val is None:
                continue
            sock = expose_param("Exponent", p1 if p1 else 2.0, i, 1)
            n = _math(tree, 'POWER', (x, y))
            _link(tree, cur_val, n.inputs[0])
            _link(tree, sock,    n.inputs[1])
            cur_val = n.outputs[0]

        elif op == 'CLAMP':
            if cur_val is None:
                continue
            smin = expose_param("Min", p1, i, 1)
            smax = expose_param("Max", p2 if p2 else 1.0, i, 2)
            n = tree.nodes.new("ShaderNodeClamp")
            n.location = (x, y)
            _link(tree, cur_val, n.inputs["Value"])
            _link(tree, smin,    n.inputs["Min"])
            _link(tree, smax,    n.inputs["Max"])
            cur_val = n.outputs[0]

        elif op == 'SMOOTHSTEP':
            if cur_val is None:
                continue
            e0 = expose_param("Edge0", p1, i, 1)
            e1 = expose_param("Edge1", p2 if p2 else 1.0, i, 2)
            n = tree.nodes.new("ShaderNodeMapRange")
            n.interpolation_type = 'SMOOTHSTEP'
            n.location = (x, y)
            _link(tree, cur_val, n.inputs["Value"])
            _link(tree, e0,      n.inputs["From Min"])
            _link(tree, e1,      n.inputs["From Max"])
            n.inputs["To Min"].default_value = 0.0
            n.inputs["To Max"].default_value = 1.0
            cur_val = n.outputs["Result"]

        elif op == 'COLORRAMP':
            if cur_val is None:
                continue
            n = tree.nodes.new("ShaderNodeValToRGB")
            n.location = (x, y)
            _link(tree, cur_val, n.inputs["Fac"])
            cur_col = n.outputs["Color"]
            cur_val = n.outputs["Alpha"]

        elif op == 'DISTORTION':
            sock = expose_param("Strength", p1 if p1 else 0.5, i, 1)
            dn = tree.nodes.new("ShaderNodeTexNoise")
            dn.noise_dimensions = '4D'
            dn.location = (x, y - 180)
            _link(tree, cur_vec, dn.inputs["Vector"])
            _link(tree, cur_w,   dn.inputs["W"])
            dn.inputs["Scale"].default_value = 2.0

            recenter = _vmath(tree, 'SUBTRACT', (x + 60, y - 180))
            recenter.inputs[1].default_value = (0.5, 0.5, 0.5)
            _link(tree, dn.outputs["Color"], recenter.inputs[0])

            scaled = _vmath(tree, 'SCALE', (x + 120, y - 180))
            _link(tree, recenter.outputs[0], scaled.inputs[0])
            _link(tree, sock, scaled.inputs["Scale"])

            add = _vmath(tree, 'ADD', (x + 180, y))
            _link(tree, cur_vec, add.inputs[0])
            _link(tree, scaled.outputs[0], add.inputs[1])
            cur_vec = add.outputs[0]

    # ---- Wire output ----
    g_out.location = (x + 320, 0)
    if cur_val is not None:
        _link(tree, cur_val, g_out.inputs["Fac"])
    if cur_col is not None:
        _link(tree, cur_col, g_out.inputs["Color"])
    elif cur_val is not None:
        # Fallback: grayscale color from the final value.
        combine = tree.nodes.new("ShaderNodeCombineColor")
        combine.location = (x + 160, -80)
        _link(tree, cur_val, combine.inputs[0])
        _link(tree, cur_val, combine.inputs[1])
        _link(tree, cur_val, combine.inputs[2])
        _link(tree, combine.outputs[0], g_out.inputs["Color"])

    return tree
