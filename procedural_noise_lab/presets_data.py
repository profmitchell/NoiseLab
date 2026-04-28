"""Built-in preset library (PRD §32 / other ideas §10, §18).

Each preset targets a specific node group and provides override values for
its group-input sockets.  Values not listed keep their recipe defaults.
"""

PRESET_CATEGORIES = [
    ("ORGANIC",  "Organic"),
    ("ABSTRACT", "Abstract"),
    ("SURFACE",  "Surface Imperfections"),
    ("MOTION",   "Video / Motion Design"),
    ("DISPLACE", "Displacement"),
]

# {category: [{name, target_group, values, description, animation_hint}, …]}
PRESETS = {
    "ORGANIC": [
        {
            "name": "Smoke Bloom",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 3.0, "Detail": 12.0, "Roughness": 0.6,
                       "Warp Amount": 1.5, "Warp Scale": 2.5, "Warp Speed": 0.15,
                       "Contrast": 0.8, "Threshold": 0.3},
            "desc": "Slow, soft volumetric bloom.",
            "anim": "Animate Time 0→2 over 240 frames.",
        },
        {
            "name": "Fog Breakup",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 2.0, "Detail": 6.0, "Roughness": 0.4,
                       "Warp Amount": 0.8, "Contrast": 0.6, "Threshold": 0.25},
            "desc": "Soft wisps for fog/haze layers.",
            "anim": "Animate Time slowly.",
        },
        {
            "name": "Moss Patches",
            "target": "INL_Domain_Warped_Noise",
            "values": {"Base Scale": 8.0, "Base Detail": 4.0, "Warp Amount": 0.5,
                       "Contrast": 1.5, "Threshold": 0.55},
            "desc": "Organic irregular patches.",
        },
    ],
    "ABSTRACT": [
        {
            "name": "Liquid Marble",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 7.5, "Detail": 14.0, "Roughness": 0.58,
                       "Lacunarity": 2.1, "Distortion": 8.0,
                       "Warp Amount": 2.5, "Warp Scale": 3.0, "Morph": 0.35,
                       "Contrast": 1.8, "Threshold": 0.45},
            "desc": "Fluid, warped texture for marble/liquid metal.",
            "anim": "Animate Time 0→2 over 240 frames.",
        },
        {
            "name": "Energy Field",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 6.0, "Detail": 10.0, "Pulse Amount": 0.6,
                       "Warp Amount": 1.2, "Warp Speed": 0.5,
                       "Contrast": 2.5, "Threshold": 0.6},
            "desc": "Pulsing energy suitable for emission masks.",
            "anim": "Animate Time + keyframe Pulse Amount.",
        },
        {
            "name": "Nebula Bloom",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 2.5, "Detail": 10.0, "Roughness": 0.7,
                       "Warp Amount": 2.0, "Warp Scale": 1.5, "Contrast": 1.0,
                       "Threshold": 0.35},
            "desc": "Cosmic gas cloud.",
        },
        {
            "name": "Cellular Drift",
            "target": "INL_Domain_Warped_Noise",
            "values": {"Base Scale": 10.0, "Warp Amount": 3.0, "Warp Scale": 5.0,
                       "Contrast": 2.0, "Threshold": 0.5},
            "desc": "Drifting cellular pattern.",
        },
    ],
    "SURFACE": [
        {
            "name": "Ceramic Speckle",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 30.0, "Detail": 4.0, "Warp Amount": 0.2,
                       "Contrast": 3.0, "Threshold": 0.7},
            "desc": "High-scale speckle for ceramics.",
        },
        {
            "name": "Chipped Paint",
            "target": "INL_Domain_Warped_Noise",
            "values": {"Base Scale": 6.0, "Warp Amount": 1.8, "Warp Scale": 4.0,
                       "Contrast": 2.5, "Threshold": 0.6},
            "desc": "Organic paint-chip edges.",
        },
        {
            "name": "Dust Mask",
            "target": "INL_Animated_Mask_Noise",
            "values": {"Scale": 15.0, "Contrast": 1.5, "Threshold": 0.4,
                       "Softness": 0.15},
            "desc": "Light dust / dirt overlay.",
        },
    ],
    "MOTION": [
        {
            "name": "VHS Dirt",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 25.0, "Detail": 6.0, "Stretch Y": 4.0,
                       "Contrast": 3.0, "Threshold": 0.65, "Drift Y": 0.5},
            "desc": "Analog video dirt streaks.",
            "anim": "Animate Time quickly.",
        },
        {
            "name": "Animated Reveal",
            "target": "INL_Animated_Mask_Noise",
            "values": {"Scale": 4.0, "Speed": 0.5, "Threshold": 0.5,
                       "Softness": 0.2, "Contrast": 1.5, "Edge Width": 0.08},
            "desc": "Procedural reveal/wipe mask.",
            "anim": "Keyframe Threshold 0→1 for reveal.",
        },
        {
            "name": "Glitch Grain",
            "target": "INL_Animated_Mask_Noise",
            "values": {"Scale": 40.0, "Speed": 5.0, "Contrast": 4.0,
                       "Threshold": 0.55, "Softness": 0.02},
            "desc": "Fast digital grain / glitch mask.",
        },
    ],
    "DISPLACE": [
        {
            "name": "Micro Bumps",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 20.0, "Detail": 8.0, "Warp Amount": 0.3,
                       "Contrast": 1.0, "Threshold": 0.5},
            "desc": "Fine micro-displacement.",
        },
        {
            "name": "Terrain Breakup",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 3.0, "Detail": 12.0, "Roughness": 0.65,
                       "Warp Amount": 2.0, "Contrast": 1.5},
            "desc": "Large-scale terrain height variation.",
        },
        {
            "name": "Lava Surface",
            "target": "INL_Domain_Warped_Noise",
            "values": {"Base Scale": 4.0, "Warp Amount": 3.5, "Warp Scale": 2.0,
                       "Contrast": 2.0, "Threshold": 0.4},
            "desc": "Glowing cracked lava look.",
            "anim": "Animate Time slowly for molten motion.",
        },
    ],
}


def flat_presets():
    """Return [(category_id, preset_dict), …] across all categories."""
    out = []
    for cat, items in PRESETS.items():
        for p in items:
            out.append((cat, p))
    return out


def preset_names_for_category(cat_id):
    return [(p["name"], p["name"], p.get("desc", "")) for p in PRESETS.get(cat_id, [])]
