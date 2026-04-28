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
    ("GEOMETRY", "Geometry Nodes"),
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
            "name": "Classic Liquid Marble",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 7.5, "Detail": 14.0, "Roughness": 0.58,
                       "Lacunarity": 2.1, "Distortion": 8.0,
                       "Warp Amount": 2.5, "Warp Scale": 3.0, "Morph": 0.35,
                       "Contrast": 1.8, "Threshold": 0.45},
            "desc": "Fluid, warped texture for marble/liquid metal.",
            "anim": "Animate Time 0→2 over 240 frames.",
        },
        {
            "name": "Swirling Marble",
            "target": "INL_Liquid_Marble_Noise",
            "values": {"Warp Amount": 3.0, "Wave Scale": 8.0, "Wave Distortion": 5.0},
            "desc": "Dedicated liquid marble recipe with swirling wave patterns.",
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
    "GEOMETRY": [
        {
            "name": "Grid Dunes",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 2.8, "Detail": 9.0, "Roughness": 0.62,
                       "Warp Amount": 1.8, "Warp Scale": 1.6,
                       "Fine Detail Amount": 0.25, "Fine Detail Scale": 5.0,
                       "Contrast": 1.1, "Output Min": -0.25, "Output Max": 1.0},
            "desc": "Broad displaced grid terrain with subtle fine breakup.",
            "anim": "Use Geometry demo Source: Grid; raise Strength for taller dunes.",
        },
        {
            "name": "Pebbled Sheet",
            "target": "INL_Infinite_4D_Noise",
            "values": {"Scale": 22.0, "Detail": 6.0, "Roughness": 0.5,
                       "Warp Amount": 0.35, "Contrast": 2.2,
                       "Threshold": 0.48, "Fine Detail Amount": 0.35},
            "desc": "Small surface bumps for generated grids or dense meshes.",
        },
        {
            "name": "Warped Ridge Field",
            "target": "INL_Domain_Warped_Noise",
            "values": {"Base Scale": 5.5, "Base Detail": 11.0,
                       "Warp Scale": 2.2, "Warp Detail": 6.0,
                       "Warp Amount": 3.2, "Contrast": 1.8,
                       "Threshold": 0.42},
            "desc": "Strong directional terrain breakup from the warp field.",
        },
        {
            "name": "Soft Attribute Mask",
            "target": "INL_Animated_Mask_Noise",
            "values": {"Scale": 7.0, "Speed": 0.35, "Detail": 8.0,
                       "Threshold": 0.52, "Softness": 0.18,
                       "Contrast": 1.4, "Edge Width": 0.06},
            "desc": "Stored in Geometry Nodes as the inl_mask point attribute.",
            "anim": "Animate Time on the modifier or group node for evolving attributes.",
        },
        {
            "name": "Marble Relief Grid",
            "target": "INL_Liquid_Marble_Noise",
            "values": {"Scale": 6.0, "Warp Amount": 3.6, "Warp Scale": 2.4,
                       "Wave Scale": 9.5, "Wave Distortion": 7.0,
                       "Detail": 5.0, "Roughness": 0.58},
            "desc": "Swirled relief pattern for generated grids.",
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


def preset_names_for_category(cat_id, target=None):
    presets = PRESETS.get(cat_id, [])
    if target:
        presets = [p for p in presets if p.get("target") == target]
    return [(p["name"], p["name"], p.get("desc", "")) for p in presets]
