"""Blender background smoke tests for Procedural Noise Lab.

Run with:
  blender --background --python tests/smoke.py
"""

import importlib
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def fail(message):
    raise AssertionError(message)


def main():
    addon = importlib.import_module("procedural_noise_lab")
    addon.register()
    try:
        registry = importlib.import_module("procedural_noise_lab.recipe_registry")
        validation = importlib.import_module("procedural_noise_lab.validation")

        if not registry.RECIPES:
            fail("No recipes registered.")

        preset_library = importlib.import_module("procedural_noise_lab.preset_library")
        presets = preset_library.all_presets()
        if len(presets) < 20:
            fail(f"Expected larger preset library, found {len(presets)} presets.")
        if not any(preset["source"] == "PACK" for preset in presets):
            fail("Expected at least one JSON preset pack preset.")

        settings = bpy.context.scene.pnl_settings
        settings.preset_search = "grid"
        settings.preset_browser_category = "GEOMETRY"
        settings.preset_browser_recipe = "ALL"
        settings.preset_source = "ALL"
        settings.preset_favorites_only = False
        if not preset_library.filter_presets(settings, presets):
            fail("Preset browser filters returned no Geometry grid presets.")

        for recipe in registry.RECIPES:
            for tree_type in ("ShaderNodeTree", "GeometryNodeTree"):
                group, reused = recipe.build(policy="SUFFIX", tree_type=tree_type)
                if reused:
                    fail(f"{recipe.display_name} unexpectedly reused a group.")
                errors = validation.validate_group(group)
                if errors:
                    fail(f"{group.name} validation failed: {errors}")

        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()
        bpy.ops.mesh.primitive_plane_add()
        bpy.context.view_layer.objects.active = bpy.context.object

        demo = importlib.import_module("procedural_noise_lab.demo_material")

        for recipe in registry.RECIPES:
            group, _reused = recipe.build(policy="REUSE", tree_type="ShaderNodeTree")
            result, message = demo.create_demo_material(group.name)
            if result is None:
                fail(message)

        geo_group, _reused = registry.RECIPES_BY_KEY["INFINITE_4D"].build(
            policy="REUSE",
            tree_type="GeometryNodeTree",
        )
        for mode in ("GRID", "ACTIVE"):
            result, message = demo.create_demo_geometry_setup(geo_group.name, mode=mode)
            if result is None:
                fail(message)

        print("Procedural Noise Lab smoke tests passed.")
    finally:
        addon.unregister()


if __name__ == "__main__":
    main()
