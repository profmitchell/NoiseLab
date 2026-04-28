"""Builder for the 'Custom 4D Noise' node group.

Layered 4D Noise + Voronoi driven by a shared W coordinate so animating W
morphs the texture (rather than translating it). Exposes the artist
controls listed in the add-on spec and emits Fac / Color / Height / Mask.
"""

import bpy

from .interface_utils import (
    get_or_create_group,
    add_group_io,
    new_input,
    new_output,
)
from .metadata import stamp_group


GROUP_NAME = "Custom 4D Noise"
RECIPE_ID = "custom_4d_noise"
RECIPE_VERSION = "1.0.0"


def _math(tree, op, x=-400, y=0, clamp=False):
    n = tree.nodes.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    n.location = (x, y)
    return n


def _vmath(tree, op, x=-400, y=0):
    n = tree.nodes.new("ShaderNodeVectorMath")
    n.operation = op
    n.location = (x, y)
    return n


def _mix(tree, data_type, x=0, y=0):
    n = tree.nodes.new("ShaderNodeMix")
    n.data_type = data_type
    n.location = (x, y)
    return n


def _link(tree, a, b):
    tree.links.new(a, b)


def build_custom_4d_noise(tree_type='ShaderNodeTree'):
    group_name = GROUP_NAME if tree_type == 'ShaderNodeTree' else GROUP_NAME + " Geo"
    tree, _ = get_or_create_group(group_name, tree_type, policy='REBUILD')

    # ---- Interface (inputs) ----
    new_input(tree, "Vector",      "NodeSocketVector", default=(0.0, 0.0, 0.0))
    new_input(tree, "W",           "NodeSocketFloat",  default=0.0)
    new_input(tree, "Scale",       "NodeSocketFloat",  default=5.0)
    new_input(tree, "Detail",      "NodeSocketFloat",  default=8.0,  min_value=0.0, max_value=15.0)
    new_input(tree, "Roughness",   "NodeSocketFloat",  default=0.5,  min_value=0.0, max_value=1.0)
    new_input(tree, "Lacunarity",  "NodeSocketFloat",  default=2.0,  min_value=0.0, max_value=8.0)
    new_input(tree, "Distortion",  "NodeSocketFloat",  default=0.2,  min_value=0.0, max_value=4.0)
    new_input(tree, "Contrast",    "NodeSocketFloat",  default=1.2,  min_value=0.0, max_value=8.0)
    new_input(tree, "Seed Offset", "NodeSocketFloat",  default=0.0)
    new_input(tree, "Mix Amount",  "NodeSocketFloat",  default=0.35, min_value=0.0, max_value=1.0)

    # ---- Interface (outputs) ----
    new_output(tree, "Fac",    "NodeSocketFloat")
    new_output(tree, "Color",  "NodeSocketColor")
    new_output(tree, "Height", "NodeSocketFloat")
    new_output(tree, "Mask",   "NodeSocketFloat")

    g_in, g_out = add_group_io(tree)

    # ---- W with seed offset ----
    w_seed = _math(tree, 'ADD', x=-720, y=240)
    w_seed.label = "W + Seed"
    _link(tree, g_in.outputs["W"], w_seed.inputs[0])
    _link(tree, g_in.outputs["Seed Offset"], w_seed.inputs[1])

    # Phase shift for the secondary (Voronoi) layer so they decorrelate.
    w_voro = _math(tree, 'ADD', x=-720, y=120)
    w_voro.label = "W (voronoi phase)"
    w_voro.inputs[1].default_value = 13.37
    _link(tree, w_seed.outputs[0], w_voro.inputs[0])

    # ---- Vector distortion field (cheap noise displacing the lookup vector) ----
    distort_noise = tree.nodes.new("ShaderNodeTexNoise")
    distort_noise.noise_dimensions = '4D'
    distort_noise.location = (-720, -80)
    distort_noise.label = "Distortion Field"
    _link(tree, g_in.outputs["Vector"], distort_noise.inputs["Vector"])
    _link(tree, w_seed.outputs[0], distort_noise.inputs["W"])
    distort_noise.inputs["Scale"].default_value = 2.0
    distort_noise.inputs["Detail"].default_value = 2.0
    distort_noise.inputs["Roughness"].default_value = 0.5

    # noise.Color is RGB in 0..1; recentre to -0.5..0.5 then scale by Distortion.
    recenter = _vmath(tree, 'SUBTRACT', x=-520, y=-80)
    recenter.inputs[1].default_value = (0.5, 0.5, 0.5)
    _link(tree, distort_noise.outputs["Color"], recenter.inputs[0])

    scale_distort = _vmath(tree, 'SCALE', x=-340, y=-80)
    _link(tree, recenter.outputs[0], scale_distort.inputs[0])
    _link(tree, g_in.outputs["Distortion"], scale_distort.inputs["Scale"])

    distorted_vec = _vmath(tree, 'ADD', x=-160, y=-80)
    _link(tree, g_in.outputs["Vector"], distorted_vec.inputs[0])
    _link(tree, scale_distort.outputs[0], distorted_vec.inputs[1])

    # ---- Primary 4D Noise layer ----
    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = '4D'
    noise.location = (40, 200)
    _link(tree, distorted_vec.outputs[0], noise.inputs["Vector"])
    _link(tree, w_seed.outputs[0],        noise.inputs["W"])
    _link(tree, g_in.outputs["Scale"],      noise.inputs["Scale"])
    _link(tree, g_in.outputs["Detail"],     noise.inputs["Detail"])
    _link(tree, g_in.outputs["Roughness"],  noise.inputs["Roughness"])
    _link(tree, g_in.outputs["Lacunarity"], noise.inputs["Lacunarity"])
    _link(tree, g_in.outputs["Distortion"], noise.inputs["Distortion"])

    # ---- Secondary 4D Voronoi layer ----
    voro = tree.nodes.new("ShaderNodeTexVoronoi")
    voro.voronoi_dimensions = '4D'
    voro.feature = 'F1'
    voro.distance = 'EUCLIDEAN'
    voro.location = (40, -120)
    _link(tree, distorted_vec.outputs[0], voro.inputs["Vector"])
    _link(tree, w_voro.outputs[0],        voro.inputs["W"])
    _link(tree, g_in.outputs["Scale"],      voro.inputs["Scale"])
    if "Detail" in voro.inputs:
        _link(tree, g_in.outputs["Detail"],     voro.inputs["Detail"])
    if "Roughness" in voro.inputs:
        _link(tree, g_in.outputs["Roughness"],  voro.inputs["Roughness"])
    if "Lacunarity" in voro.inputs:
        _link(tree, g_in.outputs["Lacunarity"], voro.inputs["Lacunarity"])

    # Voronoi distance can exceed 1; tame it with a smoothstep into 0..1.
    voro_norm = tree.nodes.new("ShaderNodeMapRange")
    voro_norm.interpolation_type = 'SMOOTHSTEP'
    voro_norm.location = (260, -120)
    voro_norm.inputs["From Min"].default_value = 0.0
    voro_norm.inputs["From Max"].default_value = 1.2
    voro_norm.inputs["To Min"].default_value = 0.0
    voro_norm.inputs["To Max"].default_value = 1.0
    _link(tree, voro.outputs["Distance"], voro_norm.inputs["Value"])

    # ---- Mix the two factors ---- (ShaderNodeMix sockets: 0 Factor, 2 A, 3 B; out 0 Result Float)
    mix_fac = _mix(tree, 'FLOAT', x=460, y=120)
    _link(tree, g_in.outputs["Mix Amount"], mix_fac.inputs[0])
    _link(tree, noise.outputs["Fac"],       mix_fac.inputs[2])
    _link(tree, voro_norm.outputs["Result"], mix_fac.inputs[3])

    # ---- Mix the two colors ---- (sockets: 0 Factor, 6 A Color, 7 B Color; out 2 Result Color)
    mix_col = _mix(tree, 'RGBA', x=460, y=-80)
    mix_col.blend_type = 'MIX'
    _link(tree, g_in.outputs["Mix Amount"], mix_col.inputs[0])
    _link(tree, noise.outputs["Color"],     mix_col.inputs[6])
    _link(tree, voro.outputs["Color"],      mix_col.inputs[7])

    # ---- Contrast: (x - 0.5) * Contrast + 0.5, clamped ----
    sub_half = _math(tree, 'SUBTRACT', x=660, y=240)
    sub_half.inputs[1].default_value = 0.5
    _link(tree, mix_fac.outputs[0], sub_half.inputs[0])

    mul_c = _math(tree, 'MULTIPLY', x=820, y=240)
    _link(tree, sub_half.outputs[0],          mul_c.inputs[0])
    _link(tree, g_in.outputs["Contrast"],     mul_c.inputs[1])

    add_half = _math(tree, 'ADD', x=980, y=240)
    add_half.inputs[1].default_value = 0.5
    _link(tree, mul_c.outputs[0], add_half.inputs[0])

    fac_clamp = tree.nodes.new("ShaderNodeClamp")
    fac_clamp.location = (1140, 240)
    fac_clamp.inputs["Min"].default_value = 0.0
    fac_clamp.inputs["Max"].default_value = 1.0
    _link(tree, add_half.outputs[0], fac_clamp.inputs["Value"])

    # ---- Height: signed -1..1 from Fac ----
    height = _math(tree, 'MULTIPLY_ADD', x=1140, y=60)
    # value * 2 + (-1)
    _link(tree, fac_clamp.outputs[0], height.inputs[0])
    height.inputs[1].default_value = 2.0
    height.inputs[2].default_value = -1.0

    # ---- Mask: smoothstep around 0.5 ----
    mask = tree.nodes.new("ShaderNodeMapRange")
    mask.interpolation_type = 'SMOOTHSTEP'
    mask.location = (1140, -140)
    mask.inputs["From Min"].default_value = 0.45
    mask.inputs["From Max"].default_value = 0.55
    mask.inputs["To Min"].default_value = 0.0
    mask.inputs["To Max"].default_value = 1.0
    _link(tree, fac_clamp.outputs[0], mask.inputs["Value"])

    # ---- Wire to group output ----
    g_out.location = (1380, 60)
    _link(tree, fac_clamp.outputs[0],        g_out.inputs["Fac"])
    _link(tree, mix_col.outputs[2],          g_out.inputs["Color"])  # Result (Color)
    _link(tree, height.outputs[0],           g_out.inputs["Height"])
    _link(tree, mask.outputs["Result"],      g_out.inputs["Mask"])

    stamp_group(tree, RECIPE_ID, RECIPE_VERSION)
    return tree
