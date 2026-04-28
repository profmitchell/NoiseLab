"""Recipe for INL_Liquid_Marble_Noise.

A classic procedural effect: a wave texture warped by a noise texture to 
create swirling, liquid-like patterns.
"""

import bpy

from .interface_utils import get_or_create_group, add_group_io, new_input, new_output
from .metadata import stamp_group
from .node_layout import STAGE_X, make_stage_frames, attach


RECIPE_ID = "liquid_marble_noise"
RECIPE_VERSION = "1.0.0"
DISPLAY_NAME = "Liquid Marble Noise"
INTERNAL_NAME = "INL_Liquid_Marble_Noise"


INPUT_SPEC = [
    ("Vector",            "NodeSocketVector", (0.0, 0.0, 0.0), None, None),
    ("Time",              "NodeSocketFloat",  0.0,             None, None),
    ("Scale",             "NodeSocketFloat",  5.0,             0.0, None),
    ("Warp Amount",       "NodeSocketFloat",  2.0,             None, None),
    ("Warp Scale",        "NodeSocketFloat",  1.5,             0.0, None),
    ("Wave Scale",        "NodeSocketFloat",  5.0,             0.0, None),
    ("Wave Distortion",   "NodeSocketFloat",  1.0,             None, None),
    ("Detail",            "NodeSocketFloat",  2.0,             0.0, 15.0),
    ("Roughness",         "NodeSocketFloat",  0.5,             0.0, 1.0),
]

OUTPUT_SPEC = [
    ("Fac",            "NodeSocketFloat"),
    ("Color",          "NodeSocketColor"),
]


def _math(tree, op, loc, frame=None, label=None):
    n = tree.nodes.new("ShaderNodeMath")
    n.operation = op
    n.location = loc
    if label:
        n.label = label
    attach(n, frame)
    return n


def _vmath(tree, op, loc, frame=None, label=None):
    n = tree.nodes.new("ShaderNodeVectorMath")
    n.operation = op
    n.location = loc
    if label:
        n.label = label
    attach(n, frame)
    return n


def _link(tree, a, b):
    tree.links.new(a, b)


def build(policy='REBUILD', tree_type='ShaderNodeTree'):
    group_name = INTERNAL_NAME if tree_type == 'ShaderNodeTree' else INTERNAL_NAME + "_Geo"
    tree, reused = get_or_create_group(group_name, tree_type, policy=policy)
    if reused:
        return tree, True

    # Interface
    for name, sock, default, smin, smax in INPUT_SPEC:
        new_input(tree, name, sock, default=default, min_value=smin, max_value=smax)
    for name, sock in OUTPUT_SPEC:
        new_output(tree, name, sock)

    g_in, g_out = add_group_io(tree)
    g_in.location = (STAGE_X[1] - 200, 0)
    g_out.location = (STAGE_X[6] + 200, 0)

    frames = make_stage_frames(tree)

    # 1. Warp Noise
    warp_noise = tree.nodes.new("ShaderNodeTexNoise")
    warp_noise.noise_dimensions = '4D'
    warp_noise.location = (STAGE_X[3], 0)
    attach(warp_noise, frames[3])
    _link(tree, g_in.outputs["Vector"], warp_noise.inputs["Vector"])
    _link(tree, g_in.outputs["Time"],   warp_noise.inputs["W"])
    _link(tree, g_in.outputs["Warp Scale"], warp_noise.inputs["Scale"])

    # 2. Warp Math
    recenter = _vmath(tree, 'SUBTRACT', (STAGE_X[3] + 200, 0), frames[3], "Recenter")
    recenter.inputs[1].default_value = (0.5, 0.5, 0.5)
    _link(tree, warp_noise.outputs["Color"], recenter.inputs[0])

    scale_warp = _vmath(tree, 'SCALE', (STAGE_X[3] + 400, 0), frames[3], "Apply Amount")
    _link(tree, recenter.outputs[0], scale_warp.inputs[0])
    _link(tree, g_in.outputs["Warp Amount"], scale_warp.inputs["Scale"])

    warped_vec = _vmath(tree, 'ADD', (STAGE_X[3] + 600, 0), frames[3], "Warped Vector")
    _link(tree, g_in.outputs["Vector"], warped_vec.inputs[0])
    _link(tree, scale_warp.outputs[0], warped_vec.inputs[1])

    # 3. Wave Texture
    wave = tree.nodes.new("ShaderNodeTexWave")
    wave.location = (STAGE_X[4], 0)
    attach(wave, frames[4])
    _link(tree, warped_vec.outputs[0], wave.inputs["Vector"])
    _link(tree, g_in.outputs["Wave Scale"], wave.inputs["Scale"])
    _link(tree, g_in.outputs["Wave Distortion"], wave.inputs["Distortion"])
    _link(tree, g_in.outputs["Detail"], wave.inputs["Detail"])
    detail_roughness = wave.inputs.get("Roughness") or wave.inputs.get("Detail Roughness")
    if detail_roughness:
        _link(tree, g_in.outputs["Roughness"], detail_roughness)

    # 4. Output
    _link(tree, wave.outputs["Fac"], g_out.inputs["Fac"])
    _link(tree, wave.outputs["Color"], g_out.inputs["Color"])

    stamp_group(tree, RECIPE_ID, RECIPE_VERSION)
    return tree, False
