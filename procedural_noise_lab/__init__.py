bl_info = {
    "name": "Procedural Noise Lab",
    "author": "Cohen Concepts",
    "version": (0, 2, 0),
    "blender": (4, 0, 0),
    "location": "Shader Editor > N Panel > Noise Lab",
    "description": (
        "Infinite Noise Lab — generate reusable procedural noise node groups "
        "(Infinite 4D Noise, Domain Warped Noise, Animated Mask Noise, "
        "formula chains) using only native Blender nodes.  Includes presets, "
        "animation helpers, randomize/mutate, demo material, and validation."
    ),
    "category": "Node",
}

import bpy

from . import properties
from . import operators
from . import ui


_modules = (properties, operators, ui)


def register():
    for m in _modules:
        m.register()
    bpy.types.Scene.pnl_settings = bpy.props.PointerProperty(type=properties.PNL_Settings)


def unregister():
    del bpy.types.Scene.pnl_settings
    for m in reversed(_modules):
        m.unregister()


if __name__ == "__main__":
    register()
