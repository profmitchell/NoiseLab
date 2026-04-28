"""Recipe for INL_Domain_Warped_Noise (PRD §21 / other ideas §7.3).

Focused domain-warping group: secondary 4D noise displaces the sample
vector of a primary 4D noise.  Fewer controls than Infinite 4D Noise.
"""

import bpy
from .interface_utils import get_or_create_group, add_group_io, new_input, new_output
from .metadata import stamp_group
from .node_layout import STAGE_X, make_frame, attach

RECIPE_ID = "domain_warped_noise"
RECIPE_VERSION = "1.0.0"
DISPLAY_NAME = "Domain Warped Noise"
INTERNAL_NAME = "INL_Domain_Warped_Noise"

INPUT_SPEC = [
    ("Vector",            "NodeSocketVector", (0.0, 0.0, 0.0), None, None),
    ("Time",              "NodeSocketFloat",  0.0,   None, None),
    ("Seed",              "NodeSocketFloat",  0.0,   None, None),
    ("Base Scale",        "NodeSocketFloat",  5.0,   0.1, 50.0),
    ("Base Detail",       "NodeSocketFloat",  8.0,   0.0, 15.0),
    ("Roughness",         "NodeSocketFloat",  0.5,   0.0, 1.0),
    ("Lacunarity",        "NodeSocketFloat",  2.0,   0.0, 8.0),
    ("Distortion",        "NodeSocketFloat",  0.0,   0.0, 10.0),
    ("Warp Scale",        "NodeSocketFloat",  3.0,   0.1, 50.0),
    ("Warp Detail",       "NodeSocketFloat",  4.0,   0.0, 15.0),
    ("Warp Amount",       "NodeSocketFloat",  1.5,   0.0, 10.0),
    ("Warp Time Offset",  "NodeSocketFloat",  0.0,  None, None),
    ("Contrast",          "NodeSocketFloat",  1.2,   0.0, 8.0),
    ("Threshold",         "NodeSocketFloat",  0.5,   0.0, 1.0),
    ("Invert",            "NodeSocketFloat",  0.0,   0.0, 1.0),
]

OUTPUT_SPEC = [
    ("Fac",        "NodeSocketFloat"),
    ("Mask",       "NodeSocketFloat"),
    ("Height",     "NodeSocketFloat"),
    ("Warp Field", "NodeSocketVector"),
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
    g_out.location = (2000, 0)

    f_vec = make_frame(tree, "01 Vector Prep", (0.18, 0.30, 0.45))
    f_warp = make_frame(tree, "02 Warp Noise", (0.45, 0.30, 0.20))
    f_base = make_frame(tree, "03 Base Noise", (0.40, 0.20, 0.40))
    f_shape = make_frame(tree, "04 Output Shaping", (0.40, 0.35, 0.20))

    # --- Seed shift ---
    seed_shift = _vmath(tree, 'ADD', (100, 200), f_vec, "Seed Shift")
    seed_shift.inputs[1].default_value = (0.0, 0.0, 0.0)
    _link(tree, g_in.outputs["Vector"], seed_shift.inputs[0])
    # Seed → uniform XYZ offset
    seed_vec = tree.nodes.new("ShaderNodeCombineXYZ")
    seed_vec.location = (100, 0); attach(seed_vec, f_vec)
    _link(tree, g_in.outputs["Seed"], seed_vec.inputs[0])
    s17 = _math(tree, 'MULTIPLY', (100, -120), f_vec, "Seed*1.7")
    s17.inputs[1].default_value = 1.7
    _link(tree, g_in.outputs["Seed"], s17.inputs[0])
    _link(tree, s17.outputs[0], seed_vec.inputs[1])
    s23 = _math(tree, 'MULTIPLY', (100, -240), f_vec, "Seed*2.3")
    s23.inputs[1].default_value = 2.3
    _link(tree, g_in.outputs["Seed"], s23.inputs[0])
    _link(tree, s23.outputs[0], seed_vec.inputs[2])
    _link(tree, seed_vec.outputs[0], seed_shift.inputs[1])

    prep_vec = seed_shift.outputs[0]

    # --- Warp noise ---
    w_warp = _math(tree, 'ADD', (500, 300), f_warp, "Time + Warp Offset")
    _link(tree, g_in.outputs["Time"], w_warp.inputs[0])
    _link(tree, g_in.outputs["Warp Time Offset"], w_warp.inputs[1])

    wn = tree.nodes.new("ShaderNodeTexNoise")
    wn.noise_dimensions = '4D'; wn.location = (700, 200); wn.label = "Warp Noise"
    attach(wn, f_warp)
    _link(tree, prep_vec, wn.inputs["Vector"])
    _link(tree, w_warp.outputs[0], wn.inputs["W"])
    _link(tree, g_in.outputs["Warp Scale"], wn.inputs["Scale"])
    _link(tree, g_in.outputs["Warp Detail"], wn.inputs["Detail"])

    rc = _vmath(tree, 'SUBTRACT', (900, 200), f_warp, "Recenter")
    rc.inputs[1].default_value = (0.5, 0.5, 0.5)
    _link(tree, wn.outputs["Color"], rc.inputs[0])

    ws = _vmath(tree, 'SCALE', (1060, 200), f_warp, "* Warp Amt")
    _link(tree, rc.outputs[0], ws.inputs[0])
    _link(tree, g_in.outputs["Warp Amount"], ws.inputs["Scale"])

    warped = _vmath(tree, 'ADD', (1220, 200), f_warp, "Warped Vec")
    _link(tree, prep_vec, warped.inputs[0])
    _link(tree, ws.outputs[0], warped.inputs[1])

    # --- Base noise ---
    bn = tree.nodes.new("ShaderNodeTexNoise")
    bn.noise_dimensions = '4D'; bn.location = (1400, 160); bn.label = "Base Noise"
    attach(bn, f_base)
    _link(tree, warped.outputs[0], bn.inputs["Vector"])
    _link(tree, g_in.outputs["Time"], bn.inputs["W"])
    _link(tree, g_in.outputs["Base Scale"], bn.inputs["Scale"])
    _link(tree, g_in.outputs["Base Detail"], bn.inputs["Detail"])
    _link(tree, g_in.outputs["Roughness"], bn.inputs["Roughness"])
    _link(tree, g_in.outputs["Lacunarity"], bn.inputs["Lacunarity"])
    _link(tree, g_in.outputs["Distortion"], bn.inputs["Distortion"])

    # --- Output shaping ---
    sub = _math(tree, 'SUBTRACT', (1600, 200), f_shape, "x-0.5")
    sub.inputs[1].default_value = 0.5
    _link(tree, bn.outputs["Fac"], sub.inputs[0])
    mulc = _math(tree, 'MULTIPLY', (1740, 200), f_shape, "*Contrast")
    _link(tree, sub.outputs[0], mulc.inputs[0])
    _link(tree, g_in.outputs["Contrast"], mulc.inputs[1])
    addc = _math(tree, 'ADD', (1880, 200), f_shape, "+0.5")
    addc.inputs[1].default_value = 0.5
    _link(tree, mulc.outputs[0], addc.inputs[0])

    clmp = tree.nodes.new("ShaderNodeClamp")
    clmp.location = (2020, 200); attach(clmp, f_shape)
    _link(tree, addc.outputs[0], clmp.inputs["Value"])

    # Invert
    inv = _math(tree, 'SUBTRACT', (2020, 40), f_shape, "1-x")
    inv.inputs[0].default_value = 1.0
    _link(tree, clmp.outputs[0], inv.inputs[1])
    inv_mix = tree.nodes.new("ShaderNodeMix"); inv_mix.data_type = 'FLOAT'
    inv_mix.location = (2160, 120); inv_mix.label = "Invert"; attach(inv_mix, f_shape)
    _link(tree, g_in.outputs["Invert"], inv_mix.inputs[0])
    _link(tree, clmp.outputs[0], inv_mix.inputs[2])
    _link(tree, inv.outputs[0], inv_mix.inputs[3])

    # Mask
    th_lo = _math(tree, 'SUBTRACT', (1600, -100), f_shape, "Th-0.05")
    th_lo.inputs[1].default_value = 0.05
    _link(tree, g_in.outputs["Threshold"], th_lo.inputs[0])
    th_hi = _math(tree, 'ADD', (1600, -220), f_shape, "Th+0.05")
    th_hi.inputs[1].default_value = 0.05
    _link(tree, g_in.outputs["Threshold"], th_hi.inputs[0])
    mask = tree.nodes.new("ShaderNodeMapRange")
    mask.interpolation_type = 'SMOOTHSTEP'; mask.location = (1880, -160)
    mask.label = "Mask"; attach(mask, f_shape)
    mask.inputs["To Min"].default_value = 0.0; mask.inputs["To Max"].default_value = 1.0
    _link(tree, inv_mix.outputs[0], mask.inputs["Value"])
    _link(tree, th_lo.outputs[0], mask.inputs["From Min"])
    _link(tree, th_hi.outputs[0], mask.inputs["From Max"])

    # Height
    height = _math(tree, 'MULTIPLY_ADD', (2020, -160), f_shape, "Height")
    height.inputs[1].default_value = 2.0; height.inputs[2].default_value = -1.0
    _link(tree, inv_mix.outputs[0], height.inputs[0])

    # --- Outputs ---
    _link(tree, inv_mix.outputs[0], g_out.inputs["Fac"])
    _link(tree, mask.outputs["Result"], g_out.inputs["Mask"])
    _link(tree, height.outputs[0], g_out.inputs["Height"])
    _link(tree, ws.outputs[0], g_out.inputs["Warp Field"])

    stamp_group(tree, RECIPE_ID, RECIPE_VERSION)
    return tree, False
