"""Recipe for INL_Animated_Mask_Noise (PRD §22 / other ideas §7.4).

Specialised group for evolving procedural masks with soft, hard, and
edge-detect outputs.
"""

import bpy
from .interface_utils import get_or_create_group, add_group_io, new_input, new_output
from .metadata import stamp_group
from .node_layout import make_frame, attach

RECIPE_ID = "animated_mask_noise"
RECIPE_VERSION = "1.0.0"
DISPLAY_NAME = "Animated Mask Noise"
INTERNAL_NAME = "INL_Animated_Mask_Noise"

INPUT_SPEC = [
    ("Vector",    "NodeSocketVector", (0.0, 0.0, 0.0), None, None),
    ("Time",      "NodeSocketFloat",  0.0,  None, None),
    ("Seed",      "NodeSocketFloat",  0.0,  None, None),
    ("Scale",     "NodeSocketFloat",  5.0,  0.0,  None),
    ("Speed",     "NodeSocketFloat",  1.0,  None, None),
    ("Morph",     "NodeSocketFloat",  0.0, None, None),
    ("Detail",    "NodeSocketFloat",  8.0,  0.0,  15.0),
    ("Roughness", "NodeSocketFloat",  0.5,  0.0,  1.0),
    ("Threshold", "NodeSocketFloat",  0.5,  0.0,  1.0),
    ("Softness",  "NodeSocketFloat",  0.1,  0.001, 0.5),
    ("Contrast",  "NodeSocketFloat",  1.2,  0.0,  None),
    ("Edge Width","NodeSocketFloat",  0.05, 0.001, 0.3),
    ("Invert",    "NodeSocketFloat",  0.0,  0.0,  1.0),
]

OUTPUT_SPEC = [
    ("Soft Mask", "NodeSocketFloat"),
    ("Hard Mask", "NodeSocketFloat"),
    ("Edge Mask", "NodeSocketFloat"),
    ("Height",    "NodeSocketFloat"),
]


def _math(tree, op, loc, frame=None, label=None):
    n = tree.nodes.new("ShaderNodeMath")
    n.operation = op; n.location = loc
    if label: n.label = label
    attach(n, frame); return n

def _vmath(tree, op, loc, frame=None, label=None):
    n = tree.nodes.new("ShaderNodeVectorMath")
    n.operation = op; n.location = loc
    if label: n.label = label
    attach(n, frame); return n

def _link(tree, a, b):
    tree.links.new(a, b)


def build(policy='REBUILD', tree_type='ShaderNodeTree'):
    group_name = INTERNAL_NAME if tree_type == 'ShaderNodeTree' else INTERNAL_NAME + "_Geo"
    tree, reused = get_or_create_group(group_name, tree_type, policy=policy)
    if reused:
        return tree, True

    for name, sock, default, smin, smax in INPUT_SPEC:
        new_input(tree, name, sock, default=default, min_value=smin, max_value=smax)
    for name, sock in OUTPUT_SPEC:
        new_output(tree, name, sock)

    g_in, g_out = add_group_io(tree)
    g_in.location = (-200, 0)
    g_out.location = (2200, 0)

    f_prep = make_frame(tree, "01 Prep", (0.18, 0.30, 0.45))
    f_noise = make_frame(tree, "02 Noise", (0.40, 0.20, 0.40))
    f_shape = make_frame(tree, "03 Shaping", (0.40, 0.35, 0.20))

    # Seed shift
    seed_vec = tree.nodes.new("ShaderNodeCombineXYZ")
    seed_vec.location = (50, -60); attach(seed_vec, f_prep)
    _link(tree, g_in.outputs["Seed"], seed_vec.inputs[0])
    s17 = _math(tree, 'MULTIPLY', (50, -180), f_prep)
    s17.inputs[1].default_value = 1.7
    _link(tree, g_in.outputs["Seed"], s17.inputs[0])
    _link(tree, s17.outputs[0], seed_vec.inputs[1])
    s23 = _math(tree, 'MULTIPLY', (50, -300), f_prep)
    s23.inputs[1].default_value = 2.3
    _link(tree, g_in.outputs["Seed"], s23.inputs[0])
    _link(tree, s23.outputs[0], seed_vec.inputs[2])
    vec_add = _vmath(tree, 'ADD', (250, 200), f_prep, "Vec + Seed")
    _link(tree, g_in.outputs["Vector"], vec_add.inputs[0])
    _link(tree, seed_vec.outputs[0], vec_add.inputs[1])

    # Effective W = Time * Speed + Morph
    ts = _math(tree, 'MULTIPLY', (250, 0), f_prep, "Time*Speed")
    _link(tree, g_in.outputs["Time"], ts.inputs[0])
    _link(tree, g_in.outputs["Speed"], ts.inputs[1])
    w_eff = _math(tree, 'ADD', (420, 0), f_prep, "W + Morph")
    _link(tree, ts.outputs[0], w_eff.inputs[0])
    _link(tree, g_in.outputs["Morph"], w_eff.inputs[1])

    # Primary 4D noise
    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = '4D'; noise.location = (650, 160)
    noise.label = "Mask Noise"; attach(noise, f_noise)
    _link(tree, vec_add.outputs[0], noise.inputs["Vector"])
    _link(tree, w_eff.outputs[0], noise.inputs["W"])
    _link(tree, g_in.outputs["Scale"], noise.inputs["Scale"])
    _link(tree, g_in.outputs["Detail"], noise.inputs["Detail"])
    _link(tree, g_in.outputs["Roughness"], noise.inputs["Roughness"])

    # --- Contrast ---
    sub = _math(tree, 'SUBTRACT', (900, 200), f_shape, "x-0.5")
    sub.inputs[1].default_value = 0.5
    _link(tree, noise.outputs["Fac"], sub.inputs[0])
    mulc = _math(tree, 'MULTIPLY', (1060, 200), f_shape, "*Contrast")
    _link(tree, sub.outputs[0], mulc.inputs[0])
    _link(tree, g_in.outputs["Contrast"], mulc.inputs[1])
    addc = _math(tree, 'ADD', (1220, 200), f_shape, "+0.5")
    addc.inputs[1].default_value = 0.5
    _link(tree, mulc.outputs[0], addc.inputs[0])
    clmp = tree.nodes.new("ShaderNodeClamp")
    clmp.location = (1380, 200); attach(clmp, f_shape)
    _link(tree, addc.outputs[0], clmp.inputs["Value"])

    # --- Invert ---
    inv = _math(tree, 'SUBTRACT', (1380, 40), f_shape, "1-x")
    inv.inputs[0].default_value = 1.0
    _link(tree, clmp.outputs[0], inv.inputs[1])
    inv_mix = tree.nodes.new("ShaderNodeMix"); inv_mix.data_type = 'FLOAT'
    inv_mix.location = (1540, 120); inv_mix.label = "Invert"; attach(inv_mix, f_shape)
    _link(tree, g_in.outputs["Invert"], inv_mix.inputs[0])
    _link(tree, clmp.outputs[0], inv_mix.inputs[2])
    _link(tree, inv.outputs[0], inv_mix.inputs[3])

    val = inv_mix.outputs[0]  # shaped value

    # --- Soft Mask = smoothstep(Threshold-Softness, Threshold+Softness, val) ---
    soft_lo = _math(tree, 'SUBTRACT', (1540, -100), f_shape, "Th - Soft")
    _link(tree, g_in.outputs["Threshold"], soft_lo.inputs[0])
    _link(tree, g_in.outputs["Softness"], soft_lo.inputs[1])
    soft_hi = _math(tree, 'ADD', (1540, -220), f_shape, "Th + Soft")
    _link(tree, g_in.outputs["Threshold"], soft_hi.inputs[0])
    _link(tree, g_in.outputs["Softness"], soft_hi.inputs[1])
    soft_mask = tree.nodes.new("ShaderNodeMapRange")
    soft_mask.interpolation_type = 'SMOOTHSTEP'; soft_mask.location = (1780, -160)
    soft_mask.label = "Soft Mask"; attach(soft_mask, f_shape)
    soft_mask.inputs["To Min"].default_value = 0.0
    soft_mask.inputs["To Max"].default_value = 1.0
    _link(tree, val, soft_mask.inputs["Value"])
    _link(tree, soft_lo.outputs[0], soft_mask.inputs["From Min"])
    _link(tree, soft_hi.outputs[0], soft_mask.inputs["From Max"])

    # --- Hard Mask = step(Threshold, val) via Greater Than ---
    hard = _math(tree, 'GREATER_THAN', (1780, -380), f_shape, "Hard Mask")
    _link(tree, val, hard.inputs[0])
    _link(tree, g_in.outputs["Threshold"], hard.inputs[1])

    # --- Edge Mask = abs(soft_mask - hard_mask) remapped by Edge Width ---
    edge_diff = _math(tree, 'SUBTRACT', (1940, -280), f_shape, "Soft-Hard")
    _link(tree, soft_mask.outputs["Result"], edge_diff.inputs[0])
    _link(tree, hard.outputs[0], edge_diff.inputs[1])
    edge_abs = _math(tree, 'ABSOLUTE', (2060, -280), f_shape, "abs")
    _link(tree, edge_diff.outputs[0], edge_abs.inputs[0])
    edge_scale = _math(tree, 'DIVIDE', (2060, -400), f_shape, "1/EdgeW")
    edge_scale.inputs[0].default_value = 1.0
    _link(tree, g_in.outputs["Edge Width"], edge_scale.inputs[1])
    edge_mul = _math(tree, 'MULTIPLY', (2200, -280), f_shape, "Edge Mask")
    edge_mul.use_clamp = True
    _link(tree, edge_abs.outputs[0], edge_mul.inputs[0])
    _link(tree, edge_scale.outputs[0], edge_mul.inputs[1])

    # --- Height ---
    height = _math(tree, 'MULTIPLY_ADD', (1780, -500), f_shape, "Height")
    height.inputs[1].default_value = 2.0; height.inputs[2].default_value = -1.0
    _link(tree, val, height.inputs[0])

    # --- Wire outputs ---
    _link(tree, soft_mask.outputs["Result"], g_out.inputs["Soft Mask"])
    _link(tree, hard.outputs[0], g_out.inputs["Hard Mask"])
    _link(tree, edge_mul.outputs[0], g_out.inputs["Edge Mask"])
    _link(tree, height.outputs[0], g_out.inputs["Height"])

    stamp_group(tree, RECIPE_ID, RECIPE_VERSION)
    return tree, False
