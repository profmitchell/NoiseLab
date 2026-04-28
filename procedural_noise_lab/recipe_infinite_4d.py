"""Recipe for INL_Infinite_4D_Noise (PRD §13-20).

Flagship procedural-noise group with W-like artist controls created via
coordinate transforms, domain warping, layered 4D noise, and output shaping.
"""

import bpy

from .interface_utils import get_or_create_group, add_group_io, new_input, new_output
from .metadata import stamp_group
from .node_layout import STAGE_X, make_stage_frames, attach


RECIPE_ID = "infinite_4d_noise"
RECIPE_VERSION = "1.0.0"
DISPLAY_NAME = "Infinite 4D Noise"
INTERNAL_NAME = "INL_Infinite_4D_Noise"


# ---------------------------------------------------------------------------
# Interface specification (PRD §13)
# ---------------------------------------------------------------------------
INPUT_SPEC = [
    # (name, type, default, soft_min, soft_max)
    # ---- Core ----
    ("Vector",            "NodeSocketVector", (0.0, 0.0, 0.0), None, None),
    ("Time",              "NodeSocketFloat",  0.0,             0.0, 10.0),
    ("Seed",              "NodeSocketFloat",  0.0,             0.0, 100.0),
    # ---- Noise ----
    ("Scale",             "NodeSocketFloat",  5.0,             0.0, 50.0),
    ("Detail",            "NodeSocketFloat",  8.0,             0.0, 15.0),
    ("Roughness",         "NodeSocketFloat",  0.55,            0.0, 1.0),
    ("Lacunarity",        "NodeSocketFloat",  2.0,             0.0, 8.0),
    ("Distortion",        "NodeSocketFloat",  0.0,             0.0, 10.0),
    # ---- Warp ----
    ("Warp Amount",       "NodeSocketFloat",  1.0,             0.0, 8.0),
    ("Warp Scale",        "NodeSocketFloat",  2.0,             0.0, 20.0),
    ("Warp Speed",        "NodeSocketFloat",  0.25,            0.0, 4.0),
    # ---- Motion ----
    ("Morph",             "NodeSocketFloat",  0.0,             -10.0, 10.0),
    ("Drift X",           "NodeSocketFloat",  0.0,             -10.0, 10.0),
    ("Drift Y",           "NodeSocketFloat",  0.0,             -10.0, 10.0),
    ("Drift Z",           "NodeSocketFloat",  0.0,             -10.0, 10.0),
    # ---- Shape ----
    ("Stretch X",         "NodeSocketFloat",  1.0,             0.01, 10.0),
    ("Stretch Y",         "NodeSocketFloat",  1.0,             0.01, 10.0),
    ("Stretch Z",         "NodeSocketFloat",  1.0,             0.01, 10.0),
    ("Twist Amount",      "NodeSocketFloat",  0.0,             -10.0, 10.0),
    ("Pulse Amount",      "NodeSocketFloat",  0.0,             0.0, 1.0),
    # ---- Detail layer ----
    ("Fine Detail Amount","NodeSocketFloat",  0.0,             0.0, 1.0),
    ("Fine Detail Scale", "NodeSocketFloat",  3.0,             1.0, 10.0),
    # ---- Output shaping ----
    ("Contrast",          "NodeSocketFloat",  1.2,             0.0, 8.0),
    ("Threshold",         "NodeSocketFloat",  0.5,             0.0, 1.0),
    ("Invert",            "NodeSocketFloat",  0.0,             0.0, 1.0),
    ("Output Min",        "NodeSocketFloat",  0.0,             -2.0, 2.0),
    ("Output Max",        "NodeSocketFloat",  1.0,             -2.0, 2.0),
]

OUTPUT_SPEC = [
    ("Fac",            "NodeSocketFloat"),
    ("Mask",           "NodeSocketFloat"),
    ("Height",         "NodeSocketFloat"),
    ("Color",          "NodeSocketColor"),
    ("Warped Vector",  "NodeSocketVector"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------
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
    g_out.location = (STAGE_X[7] + 200, 0)

    frames = make_stage_frames(tree)

    # ============================================================
    # Stage 2: Coordinate Transform (PRD §15)
    # ============================================================
    sep = tree.nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (STAGE_X[2], 200)
    attach(sep, frames[2])
    _link(tree, g_in.outputs["Vector"], sep.inputs[0])

    sx = _math(tree, 'MULTIPLY', (STAGE_X[2] + 180, 320), frames[2], "Stretch X")
    sy = _math(tree, 'MULTIPLY', (STAGE_X[2] + 180, 200), frames[2], "Stretch Y")
    sz = _math(tree, 'MULTIPLY', (STAGE_X[2] + 180, 80),  frames[2], "Stretch Z")
    _link(tree, sep.outputs[0], sx.inputs[0]); _link(tree, g_in.outputs["Stretch X"], sx.inputs[1])
    _link(tree, sep.outputs[1], sy.inputs[0]); _link(tree, g_in.outputs["Stretch Y"], sy.inputs[1])
    _link(tree, sep.outputs[2], sz.inputs[0]); _link(tree, g_in.outputs["Stretch Z"], sz.inputs[1])

    # Add drift
    dx = _math(tree, 'ADD', (STAGE_X[2] + 360, 320), frames[2], "+ Drift X")
    dy = _math(tree, 'ADD', (STAGE_X[2] + 360, 200), frames[2], "+ Drift Y")
    dz = _math(tree, 'ADD', (STAGE_X[2] + 360, 80),  frames[2], "+ Drift Z")
    _link(tree, sx.outputs[0], dx.inputs[0]); _link(tree, g_in.outputs["Drift X"], dx.inputs[1])
    _link(tree, sy.outputs[0], dy.inputs[0]); _link(tree, g_in.outputs["Drift Y"], dy.inputs[1])
    _link(tree, sz.outputs[0], dz.inputs[0]); _link(tree, g_in.outputs["Drift Z"], dz.inputs[1])

    # Seed offset (added to all axes for a simple deterministic shift)
    seed_add_x = _math(tree, 'ADD', (STAGE_X[2] + 540, 320), frames[2], "+ Seed")
    seed_add_y = _math(tree, 'ADD', (STAGE_X[2] + 540, 200), frames[2], "+ Seed")
    seed_add_z = _math(tree, 'ADD', (STAGE_X[2] + 540, 80),  frames[2], "+ Seed")
    seed_scaled_y = _math(tree, 'MULTIPLY', (STAGE_X[2] + 540, -40), frames[2], "Seed*1.7")
    seed_scaled_y.inputs[1].default_value = 1.7
    seed_scaled_z = _math(tree, 'MULTIPLY', (STAGE_X[2] + 540, -160), frames[2], "Seed*2.3")
    seed_scaled_z.inputs[1].default_value = 2.3
    _link(tree, g_in.outputs["Seed"], seed_scaled_y.inputs[0])
    _link(tree, g_in.outputs["Seed"], seed_scaled_z.inputs[0])
    _link(tree, dx.outputs[0], seed_add_x.inputs[0]); _link(tree, g_in.outputs["Seed"], seed_add_x.inputs[1])
    _link(tree, dy.outputs[0], seed_add_y.inputs[0]); _link(tree, seed_scaled_y.outputs[0], seed_add_y.inputs[1])
    _link(tree, dz.outputs[0], seed_add_z.inputs[0]); _link(tree, seed_scaled_z.outputs[0], seed_add_z.inputs[1])

    # Twist: rotate X/Y by angle = Z * Twist Amount
    twist_angle = _math(tree, 'MULTIPLY', (STAGE_X[2] + 720, -40), frames[2], "Z * Twist")
    _link(tree, seed_add_z.outputs[0], twist_angle.inputs[0])
    _link(tree, g_in.outputs["Twist Amount"], twist_angle.inputs[1])
    twist_cos = _math(tree, 'COSINE', (STAGE_X[2] + 880, 40), frames[2], "cos(twist)")
    _link(tree, twist_angle.outputs[0], twist_cos.inputs[0])
    twist_sin = _math(tree, 'SINE', (STAGE_X[2] + 880, -80), frames[2], "sin(twist)")
    _link(tree, twist_angle.outputs[0], twist_sin.inputs[0])
    # new_x = x*cos - y*sin
    xc = _math(tree, 'MULTIPLY', (STAGE_X[2] + 1040, 320), frames[2], "x*cos")
    _link(tree, seed_add_x.outputs[0], xc.inputs[0]); _link(tree, twist_cos.outputs[0], xc.inputs[1])
    ys = _math(tree, 'MULTIPLY', (STAGE_X[2] + 1040, 200), frames[2], "y*sin")
    _link(tree, seed_add_y.outputs[0], ys.inputs[0]); _link(tree, twist_sin.outputs[0], ys.inputs[1])
    new_x = _math(tree, 'SUBTRACT', (STAGE_X[2] + 1200, 320), frames[2], "new X")
    _link(tree, xc.outputs[0], new_x.inputs[0]); _link(tree, ys.outputs[0], new_x.inputs[1])
    # new_y = x*sin + y*cos
    xs = _math(tree, 'MULTIPLY', (STAGE_X[2] + 1040, 80), frames[2], "x*sin")
    _link(tree, seed_add_x.outputs[0], xs.inputs[0]); _link(tree, twist_sin.outputs[0], xs.inputs[1])
    yc = _math(tree, 'MULTIPLY', (STAGE_X[2] + 1040, -40), frames[2], "y*cos")
    _link(tree, seed_add_y.outputs[0], yc.inputs[0]); _link(tree, twist_cos.outputs[0], yc.inputs[1])
    new_y = _math(tree, 'ADD', (STAGE_X[2] + 1200, 80), frames[2], "new Y")
    _link(tree, xs.outputs[0], new_y.inputs[0]); _link(tree, yc.outputs[0], new_y.inputs[1])

    comb = tree.nodes.new("ShaderNodeCombineXYZ")
    comb.location = (STAGE_X[2] + 1380, 200)
    attach(comb, frames[2])
    _link(tree, new_x.outputs[0], comb.inputs[0])
    _link(tree, new_y.outputs[0], comb.inputs[1])
    _link(tree, seed_add_z.outputs[0], comb.inputs[2])

    prepared_vec = comb.outputs[0]

    # ============================================================
    # Stage 3: Warp Field (PRD §16)
    # ============================================================
    # W for warp = Time * Warp Speed
    w_warp = _math(tree, 'MULTIPLY', (STAGE_X[3], 320), frames[3], "Time * Warp Speed")
    _link(tree, g_in.outputs["Time"], w_warp.inputs[0])
    _link(tree, g_in.outputs["Warp Speed"], w_warp.inputs[1])

    warp_noise = tree.nodes.new("ShaderNodeTexNoise")
    warp_noise.noise_dimensions = '4D'
    warp_noise.location = (STAGE_X[3] + 180, 200)
    warp_noise.label = "Warp Noise"
    attach(warp_noise, frames[3])
    _link(tree, prepared_vec, warp_noise.inputs["Vector"])
    _link(tree, w_warp.outputs[0], warp_noise.inputs["W"])
    _link(tree, g_in.outputs["Warp Scale"], warp_noise.inputs["Scale"])
    warp_noise.inputs["Detail"].default_value = 2.0
    warp_noise.inputs["Roughness"].default_value = 0.5

    # noise.Color is RGB in 0..1; recentre to -0.5..0.5 then scale.
    recenter = _vmath(tree, 'SUBTRACT', (STAGE_X[3] + 360, 200), frames[3], "Recenter")
    recenter.inputs[1].default_value = (0.5, 0.5, 0.5)
    _link(tree, warp_noise.outputs["Color"], recenter.inputs[0])

    warp_scaled = _vmath(tree, 'SCALE', (STAGE_X[3] + 540, 200), frames[3], "* Warp Amount")
    _link(tree, recenter.outputs[0], warp_scaled.inputs[0])
    _link(tree, g_in.outputs["Warp Amount"], warp_scaled.inputs["Scale"])

    warped_vec = _vmath(tree, 'ADD', (STAGE_X[3] + 720, 200), frames[3], "Warped Vector")
    _link(tree, prepared_vec, warped_vec.inputs[0])
    _link(tree, warp_scaled.outputs[0], warped_vec.inputs[1])

    # ============================================================
    # Stage 4: Primary Noise (PRD §17)
    # ============================================================
    # W for primary = Time + Morph
    w_primary = _math(tree, 'ADD', (STAGE_X[4], 320), frames[4], "Time + Morph")
    _link(tree, g_in.outputs["Time"], w_primary.inputs[0])
    _link(tree, g_in.outputs["Morph"], w_primary.inputs[1])

    primary = tree.nodes.new("ShaderNodeTexNoise")
    primary.noise_dimensions = '4D'
    primary.location = (STAGE_X[4] + 180, 160)
    primary.label = "Primary 4D Noise"
    attach(primary, frames[4])
    _link(tree, warped_vec.outputs[0], primary.inputs["Vector"])
    _link(tree, w_primary.outputs[0], primary.inputs["W"])
    _link(tree, g_in.outputs["Scale"],      primary.inputs["Scale"])
    _link(tree, g_in.outputs["Detail"],     primary.inputs["Detail"])
    _link(tree, g_in.outputs["Roughness"],  primary.inputs["Roughness"])
    _link(tree, g_in.outputs["Lacunarity"], primary.inputs["Lacunarity"])
    _link(tree, g_in.outputs["Distortion"], primary.inputs["Distortion"])

    # ============================================================
    # Stage 5: Fine Detail (PRD §18)
    # ============================================================
    # Effective scale = Scale * Fine Detail Scale
    fine_scale = _math(tree, 'MULTIPLY', (STAGE_X[5], 320), frames[5], "Fine Scale")
    _link(tree, g_in.outputs["Scale"], fine_scale.inputs[0])
    _link(tree, g_in.outputs["Fine Detail Scale"], fine_scale.inputs[1])

    fine = tree.nodes.new("ShaderNodeTexNoise")
    fine.noise_dimensions = '4D'
    fine.location = (STAGE_X[5] + 180, 160)
    fine.label = "Fine Detail Noise"
    attach(fine, frames[5])
    _link(tree, warped_vec.outputs[0], fine.inputs["Vector"])
    _link(tree, w_primary.outputs[0],  fine.inputs["W"])
    _link(tree, fine_scale.outputs[0], fine.inputs["Scale"])
    fine.inputs["Detail"].default_value = 4.0
    fine.inputs["Roughness"].default_value = 0.6

    # Mix(primary.Fac, fine.Fac, Fine Detail Amount)
    mix_fine = tree.nodes.new("ShaderNodeMix")
    mix_fine.data_type = 'FLOAT'
    mix_fine.location = (STAGE_X[5] + 360, 160)
    mix_fine.label = "Mix Fine"
    attach(mix_fine, frames[5])
    _link(tree, g_in.outputs["Fine Detail Amount"], mix_fine.inputs[0])
    _link(tree, primary.outputs["Fac"], mix_fine.inputs[2])
    _link(tree, fine.outputs["Fac"],    mix_fine.inputs[3])

    # ============================================================
    # Stage 6: Output Shaping (PRD §19)
    # ============================================================
    # Pulse: add a sin(Time) * Pulse Amount * 0.5 to the value
    pulse_sin = _math(tree, 'SINE', (STAGE_X[6], 360), frames[6], "sin(Time)")
    _link(tree, g_in.outputs["Time"], pulse_sin.inputs[0])
    pulse_scaled = _math(tree, 'MULTIPLY', (STAGE_X[6] + 160, 360), frames[6], "* Pulse")
    _link(tree, pulse_sin.outputs[0], pulse_scaled.inputs[0])
    _link(tree, g_in.outputs["Pulse Amount"], pulse_scaled.inputs[1])
    pulse_half = _math(tree, 'MULTIPLY', (STAGE_X[6] + 320, 360), frames[6], "* 0.5")
    pulse_half.inputs[1].default_value = 0.5
    _link(tree, pulse_scaled.outputs[0], pulse_half.inputs[0])

    pulsed = _math(tree, 'ADD', (STAGE_X[6] + 480, 240), frames[6], "+ Pulse")
    _link(tree, mix_fine.outputs[0], pulsed.inputs[0])
    _link(tree, pulse_half.outputs[0], pulsed.inputs[1])

    # Contrast: (x - 0.5) * Contrast + 0.5
    sub = _math(tree, 'SUBTRACT', (STAGE_X[6], 120), frames[6], "x - 0.5")
    sub.inputs[1].default_value = 0.5
    _link(tree, pulsed.outputs[0], sub.inputs[0])
    mul_c = _math(tree, 'MULTIPLY', (STAGE_X[6] + 160, 120), frames[6], "* Contrast")
    _link(tree, sub.outputs[0], mul_c.inputs[0])
    _link(tree, g_in.outputs["Contrast"], mul_c.inputs[1])
    add_c = _math(tree, 'ADD', (STAGE_X[6] + 320, 120), frames[6], "+ 0.5")
    add_c.inputs[1].default_value = 0.5
    _link(tree, mul_c.outputs[0], add_c.inputs[0])
    contrasted_clamp = tree.nodes.new("ShaderNodeClamp")
    contrasted_clamp.location = (STAGE_X[6] + 480, 120)
    attach(contrasted_clamp, frames[6])
    _link(tree, add_c.outputs[0], contrasted_clamp.inputs["Value"])

    # Invert: lerp(x, 1-x, Invert)
    one_minus = _math(tree, 'SUBTRACT', (STAGE_X[6] + 640, 240), frames[6], "1 - x")
    one_minus.inputs[0].default_value = 1.0
    _link(tree, contrasted_clamp.outputs[0], one_minus.inputs[1])
    invert_mix = tree.nodes.new("ShaderNodeMix")
    invert_mix.data_type = 'FLOAT'
    invert_mix.location = (STAGE_X[6] + 800, 120)
    invert_mix.label = "Invert"
    attach(invert_mix, frames[6])
    _link(tree, g_in.outputs["Invert"],   invert_mix.inputs[0])
    _link(tree, contrasted_clamp.outputs[0], invert_mix.inputs[2])
    _link(tree, one_minus.outputs[0],     invert_mix.inputs[3])

    # Final Fac = Map Range(value, 0, 1, Output Min, Output Max)
    fac_remap = tree.nodes.new("ShaderNodeMapRange")
    fac_remap.interpolation_type = 'LINEAR'
    fac_remap.location = (STAGE_X[6] + 960, 120)
    fac_remap.label = "Output Remap"
    attach(fac_remap, frames[6])
    fac_remap.inputs["From Min"].default_value = 0.0
    fac_remap.inputs["From Max"].default_value = 1.0
    _link(tree, invert_mix.outputs[0], fac_remap.inputs["Value"])
    _link(tree, g_in.outputs["Output Min"], fac_remap.inputs["To Min"])
    _link(tree, g_in.outputs["Output Max"], fac_remap.inputs["To Max"])

    # Mask = smoothstep(Threshold-0.05, Threshold+0.05, value)
    th_lo = _math(tree, 'SUBTRACT', (STAGE_X[6], -120), frames[6], "Th - 0.05")
    th_lo.inputs[1].default_value = 0.05
    _link(tree, g_in.outputs["Threshold"], th_lo.inputs[0])
    th_hi = _math(tree, 'ADD', (STAGE_X[6], -240), frames[6], "Th + 0.05")
    th_hi.inputs[1].default_value = 0.05
    _link(tree, g_in.outputs["Threshold"], th_hi.inputs[0])
    mask = tree.nodes.new("ShaderNodeMapRange")
    mask.interpolation_type = 'SMOOTHSTEP'
    mask.location = (STAGE_X[6] + 320, -180)
    mask.label = "Mask"
    attach(mask, frames[6])
    mask.inputs["To Min"].default_value = 0.0
    mask.inputs["To Max"].default_value = 1.0
    _link(tree, invert_mix.outputs[0], mask.inputs["Value"])
    _link(tree, th_lo.outputs[0], mask.inputs["From Min"])
    _link(tree, th_hi.outputs[0], mask.inputs["From Max"])

    # Height = (Fac - 0.5) * 2
    height = _math(tree, 'MULTIPLY_ADD', (STAGE_X[6] + 480, -180), frames[6], "Height (-1..1)")
    height.inputs[1].default_value = 2.0
    height.inputs[2].default_value = -1.0
    _link(tree, invert_mix.outputs[0], height.inputs[0])

    # ============================================================
    # Stage 7: Outputs
    # ============================================================
    _link(tree, fac_remap.outputs["Result"], g_out.inputs["Fac"])
    _link(tree, mask.outputs["Result"],      g_out.inputs["Mask"])
    _link(tree, height.outputs[0],           g_out.inputs["Height"])
    _link(tree, primary.outputs["Color"],    g_out.inputs["Color"])
    _link(tree, warped_vec.outputs[0],       g_out.inputs["Warped Vector"])

    stamp_group(tree, RECIPE_ID, RECIPE_VERSION)
    return tree, False
