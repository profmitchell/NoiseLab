# NoiseLab Repository Dossier

Generated: 2026-04-28  
Repository path: `/Users/Shared/CohenConcepts/NoiseLab`  
Primary package: `procedural_noise_lab`  
Project type: Blender add-on for procedural shader and geometry node generation  
Blender target: 4.0 through 5.1+  
Add-on version: 0.3.0  
License: MIT

This document is a comprehensive, NotebookLM-friendly explanation of the NoiseLab repository. It is intended to replace direct upload of the Python source files by explaining the architecture, module responsibilities, runtime behavior, data flow, operator/UI surfaces, node recipe internals, preset system, tests, packaging, and extension points.

## Executive Summary

NoiseLab, branded in the add-on metadata as **Procedural Noise Lab** and described in the README as **Infinite Noise Lab**, is a Blender add-on that generates reusable procedural-noise node groups using only Blender-native nodes. It does not evaluate arbitrary Python expressions, does not generate custom shader code, and does not require external rendering dependencies. Instead, it programmatically constructs Blender `ShaderNodeTree` and `GeometryNodeTree` node groups.

The repository centers on a small set of recipe builders. Each recipe defines a stable interface of input and output sockets, builds a node tree using Blender's Python API, stamps the generated group with recipe metadata, and can be inserted into the active Shader Editor or Geometry Nodes editor. The add-on also provides a UI panel, menu entries, demo material generation, Geometry Nodes demo setup, preset browsing, user preset JSON storage, animation helpers for the `Time` input, randomization and mutation tools, validation utilities, cleanup, and smoke tests.

The most important design decision in this codebase is that generated noise systems are represented as editable Blender node groups rather than opaque code. A user can create a group from the add-on, inspect every node, modify the generated graph by hand, save it inside a `.blend`, append it into another `.blend`, or use it in a material or Geometry Nodes modifier.

## High-Level Product Behavior

The add-on appears in Blender under:

- `Shader Editor > N Panel > Noise Lab`
- Shader or Geometry Node add menus, depending on Blender version and available menu classes

Core user workflows:

1. Open a Shader Editor or Geometry Nodes editor.
2. Use the Noise Lab sidebar to add a procedural noise group.
3. Choose a duplicate policy: reuse an existing group, rebuild safely, or always create a suffixed copy.
4. Apply a built-in, pack, or user preset.
5. Optionally create a demo material or Geometry Nodes displacement setup.
6. Animate the `Time` input with keyframes or a driver.
7. Randomize or mutate input values, with lock categories.
8. Validate generated groups and clean unused INL groups.

## Repository Layout

```text
NoiseLab/
  README.md
  features.md
  other ideas.md
  LICENSE
  NOISELAB_REPO_DOSSIER.md
  procedural_noise_lab.zip
  scripts/
    package_addon.py
  tests/
    smoke.py
  procedural_noise_lab/
    __init__.py
    animation.py
    custom_4d_noise.py
    demo_material.py
    formula_builder.py
    interface_utils.py
    metadata.py
    node_layout.py
    operators.py
    preset_library.py
    preset_packs/
      geometry_surfaces.json
    presets_data.py
    presets_io.py
    properties.py
    randomize.py
    recipe_animated_mask.py
    recipe_domain_warp.py
    recipe_infinite_4d.py
    recipe_liquid_marble.py
    recipe_registry.py
    ui.py
    validation.py
```

Important generated or local artifacts:

- `procedural_noise_lab.zip`: installable Blender add-on archive built by `scripts/package_addon.py`.
- `__pycache__/` directories and `.pyc` files: Python bytecode artifacts, not source.
- `.DS_Store`: macOS metadata artifacts.

## Current Git State At Time Of Dossier Creation

The working tree had uncommitted changes when this dossier was created. These were not reverted or modified by the dossier generation.

Modified files:

- `README.md`
- `procedural_noise_lab/operators.py`
- `procedural_noise_lab/presets_io.py`
- `procedural_noise_lab/properties.py`
- `procedural_noise_lab/ui.py`
- `tests/smoke.py`

Untracked files/directories:

- `procedural_noise_lab/preset_library.py`
- `procedural_noise_lab/preset_packs/`

The dossier itself was added as:

- `NOISELAB_REPO_DOSSIER.md`

## Runtime Environment And Dependencies

The add-on is written in Python but depends on Blender's embedded Python runtime and the `bpy` module. Most modules cannot run in a normal system Python interpreter because `bpy` is only available inside Blender or a compatible Blender Python environment.

Runtime assumptions:

- Blender 4.0 or newer.
- Blender's node group interface API using `node_tree.interface`.
- Native Blender node classes such as:
  - `ShaderNodeTexNoise`
  - `ShaderNodeTexVoronoi`
  - `ShaderNodeTexWave`
  - `ShaderNodeMath`
  - `ShaderNodeVectorMath`
  - `ShaderNodeMix`
  - `ShaderNodeMapRange`
  - `ShaderNodeClamp`
  - `GeometryNodeMeshGrid`
  - `GeometryNodeSetPosition`
  - `GeometryNodeStoreNamedAttribute`

There is no `requirements.txt`, `pyproject.toml`, or external Python dependency list. The project intentionally relies on Blender-native APIs and standard-library modules such as `json`, `os`, `pathlib`, `zipfile`, `dataclasses`, `random`, and `re`.

## Add-On Entry Point

File: `procedural_noise_lab/__init__.py`

This file defines the Blender `bl_info` metadata and handles add-on registration.

Key metadata:

- Name: `Procedural Noise Lab`
- Author: `Cohen Concepts`
- Version: `(0, 3, 0)`
- Blender minimum: `(4, 0, 0)`
- Location: `Shader Editor > N Panel > Noise Lab`
- Category: `Node`

Registration flow:

1. Imports `properties`, `operators`, and `ui`.
2. Registers those modules in order.
3. Adds `bpy.types.Scene.pnl_settings` as a `PointerProperty` of type `PNL_Settings`.

Unregistration flow:

1. Deletes `bpy.types.Scene.pnl_settings`.
2. Unregisters `ui`, `operators`, and `properties` in reverse order.

This ordering matters because UI and operators rely on the settings registered by `properties.py`.

## Core Architecture

The repository is organized around five major layers:

1. **Recipe builders**
   - Build node groups for specific procedural effects.
   - Define socket interfaces.
   - Stamp groups with metadata.

2. **Registry**
   - Provides a central list of built-in recipes.
   - Gives operators, UI, validation, presets, demos, and tests one source of truth.

3. **Blender UI and operators**
   - Expose recipe creation, presets, demo setup, animation, randomization, validation, and formula builder actions.

4. **Preset and utility systems**
   - Manage built-in preset data, JSON pack presets, user presets, favorites, filtering, animation helpers, randomization, validation, and cleanup.

5. **Testing and packaging**
   - Smoke tests run inside Blender.
   - Packaging script creates the add-on zip.

## Data Flow: Creating A Built-In Node Group

The common built-in recipe creation path is:

```text
User clicks UI button
  -> operator in operators.py executes
  -> _build_registered_recipe(context, operator, recipe_key)
  -> recipe lookup in recipe_registry.RECIPES_BY_KEY
  -> _get_tree_type(context) chooses ShaderNodeTree or GeometryNodeTree
  -> recipe.build(policy=settings.duplicate_policy, tree_type=tree_type)
  -> interface_utils.get_or_create_group(...)
  -> recipe creates group sockets and internal nodes
  -> metadata.stamp_group(...)
  -> _insert_group_into_active_editor(...) inserts group node if compatible editor is open
```

The generated node group is a Blender datablock. The add-on either inserts it as a group node in the active node editor or reports that it was built but could not be inserted because the active editor was incompatible.

## Duplicate Policy System

Implemented mainly in `interface_utils.get_or_create_group`.

Supported policies:

- `REUSE`: If a matching group already exists, return it unchanged and mark it as reused.
- `REBUILD`: If a matching group exists and has zero users, wipe and rebuild it. If the existing group has users, create a fresh new group instead so existing materials or modifiers are not changed unexpectedly.
- `SUFFIX`: Always create a new group. Blender will automatically suffix names such as `.001`.

This is an important safety mechanism. It prevents the add-on from destructively mutating node groups that are already used elsewhere in the current Blender file.

## Node Interface Helpers

File: `procedural_noise_lab/interface_utils.py`

This module wraps Blender 4.x node group interface calls.

Functions:

- `new_input(tree, name, socket_type, default=None, min_value=None, max_value=None)`
  - Adds an input socket to `tree.interface`.
  - Applies default, min, and max values when supported.

- `new_output(tree, name, socket_type)`
  - Adds an output socket to `tree.interface`.

- `_wipe_group(group)`
  - Removes all internal nodes and all interface items.
  - Used only when safe rebuild is allowed.

- `get_or_create_group(name, tree_type='ShaderNodeTree', policy='REBUILD')`
  - Implements duplicate policy.
  - Returns `(group, reused)`.

- `add_group_io(tree)`
  - Adds internal `NodeGroupInput` and `NodeGroupOutput` nodes.

The helper layer keeps the recipe files readable and protects the rest of the add-on from Blender 4.x interface API verbosity.

## Metadata System

File: `procedural_noise_lab/metadata.py`

Generated node groups receive custom properties:

- `inl_recipe_id`
- `inl_recipe_version`
- `inl_generator_version`

The generator version is `(0, 3, 0)`.

Functions:

- `stamp_group(group, recipe_id, recipe_version)`
  - Writes recipe and generator metadata into a node group.

- `get_recipe_id(group)`
  - Reads `inl_recipe_id` from a group.

This metadata is used by validation and recipe lookup. It also makes generated groups self-describing inside a `.blend`.

## Node Layout System

File: `procedural_noise_lab/node_layout.py`

This module gives generated node groups a readable left-to-right structure with stage frames.

Stage anchors:

- Stage 1: Inputs
- Stage 2: Coordinate Transform
- Stage 3: Warp Field
- Stage 4: Primary 4D Noise
- Stage 5: Detail Layer
- Stage 6: Output Shaping
- Stage 7: Outputs

Functions:

- `make_frame(tree, label, color=None)`
  - Creates a `NodeFrame` with optional custom color.

- `make_stage_frames(tree)`
  - Creates frames for the standard seven-stage layout.

- `attach(node, frame)`
  - Parents a node to a frame.

This is a user-facing quality feature: generated graphs are not merely functional, but organized for inspection and editing.

## Recipe Registry

File: `procedural_noise_lab/recipe_registry.py`

The registry centralizes metadata for all built-in recipes.

Main dataclass:

```text
RecipeInfo
  key
  display_name
  internal_name
  recipe_id
  recipe_version
  input_spec
  output_spec
  build
  icon
  description
  supports_shader
  supports_geometry
  supports_demo
```

Registered built-in recipes:

- `INFINITE_4D`: Infinite 4D Noise
- `DOMAIN_WARP`: Domain Warped Noise
- `ANIMATED_MASK`: Animated Mask Noise
- `LIQUID_MARBLE`: Liquid Marble Noise

Derived lookup tables:

- `RECIPES_BY_KEY`
- `RECIPES_BY_ID`
- `RECIPES_BY_INTERNAL_NAME`
- `DEMO_TARGET_ITEMS`

Important functions:

- `RecipeInfo.group_name(tree_type='ShaderNodeTree')`
  - Returns internal name for shader groups or appends `_Geo` for Geometry Node groups.

- `RecipeInfo.all_group_names()`
  - Returns both shader and geometry group names.

- `recipe_for_group(group)`
  - Uses metadata first, then name matching.

- `recipe_for_target_name(target_name)`
  - Finds recipes from target group names, stripping `_Geo` when needed.

This registry prevents different parts of the add-on from maintaining separate hard-coded recipe lists.

## Built-In Recipe: Infinite 4D Noise

File: `procedural_noise_lab/recipe_infinite_4d.py`

Identifiers:

- Display name: `Infinite 4D Noise`
- Internal name: `INL_Infinite_4D_Noise`
- Recipe ID: `infinite_4d_noise`
- Recipe version: `1.0.0`

Purpose:

This is the flagship node group. It builds a 4D-style animated domain-warped noise system with artist controls for vector transform, seed, warp, time/morph, drift, stretch, twist, pulse, fine detail, contrast, thresholding, inversion, and output remapping.

Inputs:

- `Vector`
- `Time`
- `Seed`
- `Scale`
- `Detail`
- `Roughness`
- `Lacunarity`
- `Distortion`
- `Warp Amount`
- `Warp Scale`
- `Warp Speed`
- `Morph`
- `Drift X`
- `Drift Y`
- `Drift Z`
- `Stretch X`
- `Stretch Y`
- `Stretch Z`
- `Twist Amount`
- `Pulse Amount`
- `Fine Detail Amount`
- `Fine Detail Scale`
- `Contrast`
- `Threshold`
- `Invert`
- `Output Min`
- `Output Max`

Outputs:

- `Fac`
- `Mask`
- `Height`
- `Color`
- `Warped Vector`

Internal stages:

1. **Coordinate Transform**
   - Separates XYZ from the input vector.
   - Applies stretch multipliers per axis.
   - Adds drift per axis.
   - Adds deterministic seed offsets.
   - Applies a twist transform in XY based on Z and `Twist Amount`.
   - Recombines the result into a prepared vector.

2. **Warp Field**
   - Computes `Time * Warp Speed` for the warp noise W coordinate.
   - Samples 4D noise using the prepared vector.
   - Uses noise color as a vector field.
   - Recenters RGB from `0..1` to approximately `-0.5..0.5`.
   - Scales the warp field by `Warp Amount`.
   - Adds the scaled field to the prepared vector.

3. **Primary Noise**
   - Computes primary W as `Time + Morph`.
   - Samples a 4D noise texture using the warped vector.
   - Exposes scale, detail, roughness, lacunarity, and distortion controls.

4. **Fine Detail**
   - Computes `Scale * Fine Detail Scale`.
   - Samples a second 4D noise layer.
   - Mixes primary and fine noise by `Fine Detail Amount`.

5. **Output Shaping**
   - Adds a sine-based pulse from `Time` and `Pulse Amount`.
   - Applies contrast using `(x - 0.5) * Contrast + 0.5`.
   - Clamps the result.
   - Mixes between value and `1 - value` using `Invert`.
   - Remaps `Fac` to `Output Min..Output Max`.
   - Generates a smooth mask around `Threshold`.
   - Generates signed height with `value * 2 - 1`.

6. **Outputs**
   - Wires `Fac`, `Mask`, `Height`, `Color`, and `Warped Vector`.

Design notes:

- The recipe uses Blender `ShaderNodeTexNoise` with `noise_dimensions = '4D'`.
- `Time` drives W, producing evolution/morphing rather than simple translation.
- `Seed` is implemented through coordinate offsets, not random state.
- The graph is organized into stage frames for readability.

## Built-In Recipe: Domain Warped Noise

File: `procedural_noise_lab/recipe_domain_warp.py`

Identifiers:

- Display name: `Domain Warped Noise`
- Internal name: `INL_Domain_Warped_Noise`
- Recipe ID: `domain_warped_noise`
- Recipe version: `1.0.0`

Purpose:

This recipe is a more focused domain-warping group. It takes a vector, shifts it by a deterministic seed, samples a warp noise field, uses that to perturb the vector, and samples a primary base noise. It exposes fewer controls than Infinite 4D Noise.

Inputs:

- `Vector`
- `Time`
- `Seed`
- `Base Scale`
- `Base Detail`
- `Roughness`
- `Lacunarity`
- `Distortion`
- `Warp Scale`
- `Warp Detail`
- `Warp Amount`
- `Warp Time Offset`
- `Contrast`
- `Threshold`
- `Invert`

Outputs:

- `Fac`
- `Mask`
- `Height`
- `Warp Field`

Internal stages:

1. **Vector Prep**
   - Combines `Seed`, `Seed * 1.7`, and `Seed * 2.3` into a vector.
   - Adds that seed vector to the input vector.

2. **Warp Noise**
   - Computes `Time + Warp Time Offset`.
   - Samples 4D noise using `Warp Scale` and `Warp Detail`.
   - Recenters RGB to a signed vector.
   - Scales by `Warp Amount`.
   - Adds the warp vector to the prepared vector.

3. **Base Noise**
   - Samples 4D noise using warped coordinates.
   - Uses `Time` as W.
   - Exposes base scale/detail and standard noise controls.

4. **Output Shaping**
   - Applies contrast around 0.5.
   - Clamps.
   - Applies optional invert.
   - Creates a smooth mask around `Threshold`.
   - Creates signed height.

Design notes:

- `Warp Field` output returns the scaled warp vector, not the final warped coordinate.
- It is suitable for texture breakup, terrain-like fields, lava/crack patterns, chipped paint, and organic patches.

## Built-In Recipe: Animated Mask Noise

File: `procedural_noise_lab/recipe_animated_mask.py`

Identifiers:

- Display name: `Animated Mask Noise`
- Internal name: `INL_Animated_Mask_Noise`
- Recipe ID: `animated_mask_noise`
- Recipe version: `1.0.0`

Purpose:

This recipe is specialized for procedural masks. It produces soft, hard, and edge masks from an evolving 4D noise field.

Inputs:

- `Vector`
- `Time`
- `Seed`
- `Scale`
- `Speed`
- `Morph`
- `Detail`
- `Roughness`
- `Threshold`
- `Softness`
- `Contrast`
- `Edge Width`
- `Invert`

Outputs:

- `Soft Mask`
- `Hard Mask`
- `Edge Mask`
- `Height`

Internal stages:

1. **Prep**
   - Builds a seed vector from `Seed`, `Seed * 1.7`, and `Seed * 2.3`.
   - Adds the seed vector to the input vector.
   - Computes effective W as `Time * Speed + Morph`.

2. **Noise**
   - Samples 4D noise using the seeded vector and W coordinate.
   - Uses exposed `Scale`, `Detail`, and `Roughness`.

3. **Shaping**
   - Applies contrast around 0.5.
   - Clamps.
   - Applies optional invert.
   - Builds soft mask through smoothstep from `Threshold - Softness` to `Threshold + Softness`.
   - Builds hard mask through a greater-than threshold.
   - Builds edge mask by comparing soft and hard masks, scaling by `1 / Edge Width`, and clamping.
   - Builds signed height from the shaped value.

Use cases:

- Procedural reveals.
- Dust or dirt overlays.
- Animated growth masks.
- Attribute masks in Geometry Nodes.
- Edge-highlighted masks for motion graphics.

## Built-In Recipe: Liquid Marble Noise

File: `procedural_noise_lab/recipe_liquid_marble.py`

Identifiers:

- Display name: `Liquid Marble Noise`
- Internal name: `INL_Liquid_Marble_Noise`
- Recipe ID: `liquid_marble_noise`
- Recipe version: `1.0.0`

Purpose:

This recipe creates a classic liquid marble effect by warping coordinates with 4D noise and feeding the result into a wave texture.

Inputs:

- `Vector`
- `Time`
- `Scale`
- `Warp Amount`
- `Warp Scale`
- `Wave Scale`
- `Wave Distortion`
- `Detail`
- `Roughness`

Outputs:

- `Fac`
- `Color`

Internal stages:

1. **Warp Noise**
   - Samples 4D noise from `Vector`, `Time`, and `Warp Scale`.

2. **Warp Math**
   - Recenters the noise color into a signed vector.
   - Scales by `Warp Amount`.
   - Adds the warp to the original vector.

3. **Wave Texture**
   - Samples a Blender wave texture using the warped vector.
   - Exposes wave scale, distortion, detail, and roughness when the Blender socket exists.

4. **Output**
   - Wires wave `Fac` and `Color` directly to group outputs.

Use cases:

- Marble.
- Liquid metal.
- Swirled stone veins.
- Relief patterns for dense meshes or generated grids.

## Legacy Recipe: Custom 4D Noise

File: `procedural_noise_lab/custom_4d_noise.py`

Group name:

- Shader: `Custom 4D Noise`
- Geometry: `Custom 4D Noise Geo`

Recipe ID:

- `custom_4d_noise`

Purpose:

This is the original 4D noise builder preserved alongside the newer recipe system. It mixes a primary 4D Noise texture with a 4D Voronoi layer, both driven by a shared W coordinate. It includes a distortion field and outputs factor, color, signed height, and a mask.

Inputs:

- `Vector`
- `W`
- `Scale`
- `Detail`
- `Roughness`
- `Lacunarity`
- `Distortion`
- `Contrast`
- `Seed Offset`
- `Mix Amount`

Outputs:

- `Fac`
- `Color`
- `Height`
- `Mask`

Internal flow:

1. Adds `Seed Offset` to W.
2. Creates a secondary Voronoi phase by adding `13.37`.
3. Samples a 4D noise distortion field.
4. Recenters and scales the distortion by `Distortion`.
5. Adds distortion to the input vector.
6. Samples a primary 4D Noise texture.
7. Samples a 4D Voronoi texture.
8. Normalizes Voronoi distance through a smoothstep map range.
9. Mixes noise and Voronoi factor by `Mix Amount`.
10. Mixes noise and Voronoi colors by `Mix Amount`.
11. Applies contrast and clamp.
12. Outputs signed height and mask.

This builder does not use the central `RECIPES` tuple, so some registry-based features focus on the four newer recipe modules rather than this legacy group.

## Formula Builder

File: `procedural_noise_lab/formula_builder.py`

Purpose:

The formula builder compiles a user-selected chain of safe operations into a Blender node group. It explicitly avoids arbitrary `eval` or user-supplied code execution. The operation vocabulary is whitelisted.

Supported operation IDs:

- `NOISE`
- `VORONOI`
- `WAVE`
- `SINE`
- `MULTIPLY`
- `ADD`
- `POWER`
- `CLAMP`
- `SMOOTHSTEP`
- `COLORRAMP`
- `DISTORTION`

Base group interface:

- Inputs:
  - `Vector`
  - `W`
  - `Scale`
- Outputs:
  - `Fac`
  - `Color`

Operation-chain behavior:

- Texture operations create new source values or colors.
- Math operations transform the current scalar value.
- `DISTORTION` changes the current vector for later operations by sampling 4D noise and adding a scaled signed vector field.
- Some operations expose extra group inputs named like `Op3 Factor`, `Op5 Min`, or `Op5 Max`.

Design notes:

- The formula builder is an advanced/custom tool.
- It follows the same node-group approach as the recipes.
- It is less metadata-driven than the built-in recipe registry.

## Operators

File: `procedural_noise_lab/operators.py`

This module is the procedural command layer for Blender. It defines all operator classes users invoke from the UI or menus.

Important helper functions:

- `_insert_group_into_active_editor(context, group)`
  - Inserts a group node into the active node editor if editor type and tree type are compatible.
  - Chooses `ShaderNodeGroup` for shader trees and `GeometryNodeGroup` for geometry trees.
  - Places the node at the editor cursor location when possible.
  - Selects the inserted node.

- `_get_tree_type(context)`
  - Returns `GeometryNodeTree` if the active node editor is a Geometry Nodes editor.
  - Defaults to `ShaderNodeTree`.

- `_active_group_node(context)`
  - Returns the active group node from the active node editor.

- `_policy(context)`
  - Reads duplicate policy from `context.scene.pnl_settings`.

- `_refresh_preset_browser(context)`
  - Rebuilds the UI collection for filtered presets.

- `_apply_preset_to_node(operator, node, preset)`
  - Applies preset values to matching input sockets on a group node.
  - Warns if the preset target does not match the selected node's recipe.

- `_build_registered_recipe(context, operator, recipe_key)`
  - Shared implementation for built-in recipe creation.

Recipe creation operators:

- `PNL_OT_build_infinite_4d`
- `PNL_OT_build_domain_warp`
- `PNL_OT_build_animated_mask`
- `PNL_OT_build_liquid_marble`
- `PNL_OT_build_custom_4d`

Demo operator:

- `PNL_OT_demo_material`
  - Builds either a shader demo material or a Geometry Nodes setup based on the active editor tree type.

Preset operators:

- `PNL_OT_refresh_presets`
- `PNL_OT_apply_preset`
- `PNL_OT_create_apply_preset`
- `PNL_OT_toggle_preset_favorite`
- `PNL_OT_delete_user_preset`
- `PNL_OT_save_preset`

Animation operators:

- `PNL_OT_animate_time`
- `PNL_OT_clear_time`

Randomization operator:

- `PNL_OT_randomize`
  - Has a `mutate` boolean property to choose full randomization or mutation.

Validation and cleanup operators:

- `PNL_OT_validate`
- `PNL_OT_cleanup`

Group management operators:

- `PNL_OT_duplicate_group`
- `PNL_OT_rename_group`

Documentation operator:

- `PNL_OT_open_docs`
  - Opens the repository README in a browser using `file://`.

Formula builder operators:

- `PNL_OT_op_add`
- `PNL_OT_op_remove`
- `PNL_OT_op_move`
- `PNL_OT_op_clear`
- `PNL_OT_build_formula`

Menu integration:

- `menu_draw_textures(self, context)` adds Noise Lab entries into relevant Blender texture/node add menus.
- Registration attempts to append this menu function to several menu class names for Blender version compatibility.

## UI Panels

File: `procedural_noise_lab/ui.py`

All panels appear in the Node Editor sidebar under the `Noise Lab` tab.

Shared base:

- `_PNL_PanelBase`
  - `bl_space_type = 'NODE_EDITOR'`
  - `bl_region_type = 'UI'`
  - `bl_category = 'Noise Lab'`
  - Polls for Node Editor context.

UI lists:

- `PNL_UL_operations`
  - Displays formula builder operation rows.

- `PNL_UL_preset_browser`
  - Displays preset rows with favorite icon, name, category, and source.

Panels:

1. `PNL_PT_create`
   - Buttons for all built-in recipes.
   - Button for Custom 4D Noise.
   - Duplicate policy selector.

2. `PNL_PT_demo`
   - Demo target selector.
   - In shader context: create demo material.
   - In geometry context: choose grid or active mesh source and create Geometry Nodes setup.

3. `PNL_PT_presets`
   - Search box.
   - Refresh button.
   - Category, recipe, source, favorites-only, and tag filters.
   - Scrollable preset list.
   - Favorite/delete controls.
   - Selected preset details.
   - Apply, Create + Apply, and Save buttons.

4. `PNL_PT_animation`
   - Keyframe or driver mode.
   - Start/end frames for keyframes.
   - Speed control for driver mode.
   - Animate and clear buttons.

5. `PNL_PT_randomize`
   - Mutation amount.
   - Lock toggles for scale, time, warp, output, and animation.
   - Randomize and Mutate buttons.

6. `PNL_PT_utilities`
   - Validate active group.
   - Clean unused INL groups.
   - Duplicate and rename selected group.
   - Open docs.

7. `PNL_PT_formula`
   - Custom formula group name.
   - Operation list.
   - Add/remove/move/clear operation controls.
   - Build formula group button.

## Properties And Add-On State

File: `procedural_noise_lab/properties.py`

This module defines `PropertyGroup` classes that back the UI and operators.

Classes:

- `PNL_OperationItem`
  - Represents one formula builder operation.
  - Properties:
    - `op`
    - `param1`
    - `param2`

- `PNL_PresetBrowserItem`
  - Represents one row in the preset browser UI collection.
  - Properties:
    - `preset_id`
    - `name`
    - `category`
    - `target`
    - `source`
    - `tags`
    - `description`
    - `animation_hint`
    - `favorite`

- `PNL_Settings`
  - Main settings object attached to `Scene` as `scene.pnl_settings`.

Important `PNL_Settings` sections:

- Duplicate policy:
  - `duplicate_policy`

- Demo setup:
  - `demo_target`
  - `geo_demo_mode`
  - `geo_grid_size`
  - `geo_grid_vertices`
  - `geo_displacement_strength`

- Preset browser:
  - `preset_category`
  - `preset_name`
  - `preset_search`
  - `preset_tag_filter`
  - `preset_browser_category`
  - `preset_browser_recipe`
  - `preset_source`
  - `preset_favorites_only`
  - `preset_browser_items`
  - `preset_browser_index`

- Animation:
  - `anim_mode`
  - `anim_start_frame`
  - `anim_end_frame`
  - `anim_speed`

- Randomize/mutate:
  - `mutate_amount`
  - `lock_scale`
  - `lock_time`
  - `lock_warp`
  - `lock_output`
  - `lock_animation`

- Formula builder:
  - `group_name`
  - `operations`
  - `active_index`

- Advanced visibility:
  - `show_formula`
  - `show_advanced`

Dynamic enum callbacks:

- `_preset_category_items`
- `_preset_name_items`

These allow preset lists to respond to the active node and selected category.

## Preset Data

File: `procedural_noise_lab/presets_data.py`

This module defines built-in preset categories and built-in presets.

Categories:

- `ORGANIC`: Organic
- `ABSTRACT`: Abstract
- `SURFACE`: Surface Imperfections
- `MOTION`: Video / Motion Design
- `DISPLACE`: Displacement
- `GEOMETRY`: Geometry Nodes

Built-in preset examples:

- Organic:
  - `Smoke Bloom`
  - `Fog Breakup`
  - `Moss Patches`

- Abstract:
  - `Classic Liquid Marble`
  - `Swirling Marble`
  - `Energy Field`
  - `Nebula Bloom`
  - `Cellular Drift`

- Surface:
  - `Ceramic Speckle`
  - `Chipped Paint`
  - `Dust Mask`

- Motion:
  - `VHS Dirt`
  - `Animated Reveal`
  - `Glitch Grain`

- Displacement:
  - `Micro Bumps`
  - `Terrain Breakup`
  - `Lava Surface`

- Geometry:
  - `Grid Dunes`
  - `Pebbled Sheet`
  - `Warped Ridge Field`
  - `Soft Attribute Mask`
  - `Marble Relief Grid`

Each preset generally includes:

- `name`
- `target`
- `values`
- `desc`
- optional `anim`

The `values` object maps group input socket names to default values.

Helper functions:

- `flat_presets()`
  - Returns category/preset pairs across all built-in categories.

- `preset_names_for_category(cat_id, target=None)`
  - Returns enum items for a category, optionally filtered by target group.

## Preset Library Aggregation

File: `procedural_noise_lab/preset_library.py`

This module unifies three preset sources:

1. Built-in Python presets from `presets_data.py`.
2. JSON pack presets from `procedural_noise_lab/preset_packs/`.
3. User presets loaded from Blender's user config directory.

Constants:

- `PACK_DIR`
- `FAVORITES_KEY`
- `SOURCE_BUILTIN`
- `SOURCE_PACK`
- `SOURCE_USER`

Functions:

- `_slug(value)`
  - Normalizes IDs for stable preset lookup.

- `recipe_items()`
  - Produces recipe enum items for filtering.

- `category_items()`
  - Produces category enum items for filtering.

- `_normalize_preset(preset, category='UNCATEGORIZED', source='BUILTIN', pack='')`
  - Converts presets from different sources into one normalized schema:
    - `id`
    - `name`
    - `category`
    - `target`
    - `values`
    - `desc`
    - `anim`
    - `tags`
    - `source`
    - `pack`
    - `preview`

- `_load_pack_presets()`
  - Reads `.json` files from `preset_packs`.
  - Ignores files that fail to parse.

- `all_presets()`
  - Combines built-ins, pack presets, and user presets.
  - Deduplicates by normalized ID.
  - Sorts by category, target, and name.

- `favorites()`
  - Reads favorite preset IDs from `bpy.context.window_manager`.

- `set_favorites(preset_ids)`
  - Stores favorites as a pipe-separated string.

- `is_favorite(preset_id)`
- `toggle_favorite(preset_id)`

- `filter_presets(settings, presets=None)`
  - Applies search, tag, category, recipe target, source, and favorites-only filters.

- `find_preset(preset_id)`

- `delete_user_preset_by_id(preset_id)`
  - Only deletes presets whose source is `USER`.

## JSON Preset Pack

File: `procedural_noise_lab/preset_packs/geometry_surfaces.json`

Pack name:

- `Geometry Surfaces`

Presets:

- `Eroded Plateau`
  - Category: `GEOMETRY`
  - Target: `INL_Infinite_4D_Noise`
  - Tags: geometry, terrain, grid, displacement

- `Cloth Pucker`
  - Category: `GEOMETRY`
  - Target: `INL_Domain_Warped_Noise`
  - Tags: geometry, fabric, surface, active mesh

- `Animated Growth Mask`
  - Category: `GEOMETRY`
  - Target: `INL_Animated_Mask_Noise`
  - Tags: geometry, attribute, mask, animation

- `Polished Stone Veins`
  - Category: `SURFACE`
  - Target: `INL_Liquid_Marble_Noise`
  - Tags: surface, marble, veins, relief

Pack schema:

```json
{
  "name": "Pack Name",
  "presets": [
    {
      "id": "stable-id",
      "name": "Preset Name",
      "category": "GEOMETRY",
      "target": "INL_Infinite_4D_Noise",
      "tags": ["tag"],
      "description": "Human-readable text",
      "animation_hint": "Optional hint",
      "values": {
        "Scale": 3.8
      }
    }
  ]
}
```

## User Preset Persistence

File: `procedural_noise_lab/presets_io.py`

User presets are saved as JSON files outside the repository, in Blender's user config area:

```text
<Blender user config>/procedural_noise_lab/user_presets/
```

Fallback outside Blender:

```text
~/.procedural_noise_lab/user_presets/
```

Functions:

- `_user_preset_dir()`
  - Determines and creates the config path.

- `_ensure_dir()`
  - Ensures the directory exists.

- `save_preset(name, target_group, values, description='')`
  - Writes `<name>.json`.

- `load_user_presets()`
  - Loads all `.json` files from the user preset directory.

- `delete_preset(name)`
  - Removes a user preset file by name.

Current user preset schema:

```json
{
  "name": "My Preset",
  "target": "INL_Infinite_4D_Noise",
  "values": {
    "Scale": 5.0
  },
  "description": ""
}
```

## Demo Material System

File: `procedural_noise_lab/demo_material.py`

The demo material helper creates a complete material on the active object. It is intended to let users quickly see a generated noise group.

Function:

- `create_demo_material(group_name='INL_Infinite_4D_Noise')`

Requirements:

- There must be an active object.
- The target node group must already exist in `bpy.data.node_groups`.

Material name:

- `INL_Demo_Material`

Node graph:

```text
Texture Coordinate Generated
  -> INL group Vector input
  -> group Fac output
  -> ColorRamp
  -> Principled BSDF Base Color

group Height output
  -> Bump Height
  -> Principled BSDF Normal

Principled BSDF
  -> Material Output Surface
```

The material is assigned to the active object if the object has material slots.

## Geometry Nodes Demo Setup

File: `procedural_noise_lab/demo_material.py`

Function:

- `create_demo_geometry_setup(group_name='INL_Infinite_4D_Noise_Geo', mode='GRID', grid_size=2.0, grid_vertices=100, displacement_strength=0.12)`

Purpose:

Creates a Geometry Nodes modifier named `INL_Demo_Setup` on the active object. The setup samples a generated INL group, displaces points along normals, and stores a float attribute for material workflows.

Supported modes:

- `GRID`
  - Creates a generated mesh grid.
  - Exposes `Grid Size` and `Grid Vertices`.

- `ACTIVE`
  - Uses the object's incoming geometry.
  - Exposes a `Geometry` input.

Common modifier inputs:

- `Displacement Strength`
- `Time`
- `Attribute Name`

Common output:

- `Geometry`

Scalar output priority:

1. `Height`
2. `Fac`
3. `Soft Mask`
4. `Mask`
5. `Hard Mask`
6. `Edge Mask`

Geometry graph behavior:

```text
Position
  -> INL geometry group Vector

optional Time input
  -> INL geometry group Time

selected scalar output
  -> multiply by Displacement Strength
  -> scale Normal vector
  -> Set Position Offset

selected scalar output
  -> Store Named Attribute Value

Attribute Name
  -> Store Named Attribute Name

Set Position Geometry
  -> Store Named Attribute
  -> Group Output Geometry
```

Default stored attribute name:

- `inl_mask`

## Animation Helpers

File: `procedural_noise_lab/animation.py`

Purpose:

Animate the `Time` input of an active group node.

Functions:

- `_find_time_input(group_node)`
  - Finds an input socket named `Time`.

- `animate_time_keyframes(group_node, start_frame=1, end_frame=120, start_val=0.0, end_val=1.0)`
  - Inserts two keyframes on the Time socket.
  - Attempts to set interpolation to linear.

- `clear_time_animation(group_node)`
  - Removes keyframes and driver from the Time input where possible.

- `add_time_driver(group_node, speed=1.0)`
  - Adds a scripted driver to Time.
  - Final driver expression is `frame * (speed / 24.0)`.

- `_socket_index(node, socket)`
  - Finds the socket index needed for animation data paths.

Limitations and details:

- The helpers assume the target group node has a socket named exactly `Time`.
- Driver path handling depends on the node tree ownership context.
- Driver expression uses a 24 FPS fallback rather than querying FPS at runtime inside the expression.

## Randomization And Mutation

File: `procedural_noise_lab/randomize.py`

Purpose:

Randomly change exposed float inputs on a selected group node, either by assigning entirely new values within the socket range or by mutating the current values by a percentage.

Lock categories:

- `SCALE`
  - `Scale`
  - `Base Scale`
  - `Warp Scale`
  - `Fine Detail Scale`

- `TIME`
  - `Time`
  - `Speed`
  - `Warp Speed`

- `WARP`
  - `Warp Amount`
  - `Warp Scale`
  - `Warp Speed`
  - `Warp Detail`
  - `Warp Time Offset`
  - `Twist Amount`

- `OUTPUT`
  - `Contrast`
  - `Threshold`
  - `Invert`
  - `Output Min`
  - `Output Max`
  - `Edge Width`
  - `Softness`

- `ANIMATION`
  - `Time`
  - `Speed`
  - `Morph`
  - `Pulse Amount`

Functions:

- `_safe_range(sock)`
  - Reads min/max from the socket.
  - Falls back to `0..10` if min and max are equal.

- `randomize_inputs(group_node, mutate=False, mutate_pct=0.2, locked_categories=None, rng_seed=None)`
  - Iterates over group inputs.
  - Skips locked names.
  - Only changes sockets whose type is `VALUE`.
  - If `mutate` is false, chooses a random value in the socket range.
  - If `mutate` is true, adds a random delta based on range and mutation percentage.
  - Returns `(changed, skipped)`.

## Validation And Cleanup

File: `procedural_noise_lab/validation.py`

Purpose:

Validate generated node groups and remove unused INL node groups.

Validation checks:

- Group is not `None`.
- Group has internal nodes.
- Required explicit input/output names are present when passed to the function.
- Registered recipe can be identified by metadata or name.
- Recipe ID matches expected metadata.
- Recipe version matches expected metadata.
- Interface inputs match recipe `input_spec`.
- Interface outputs match recipe `output_spec`.
- Internal `NodeGroupInput` exists.
- Internal `NodeGroupOutput` exists.
- Every recipe output is internally linked.

Functions:

- `_interface_sockets(group, in_out)`
- `_socket_type(item)`
- `_validate_spec(errors, sockets, spec, label)`
- `_group_output_links(group)`
- `validate_group(group, required_inputs=None, required_outputs=None)`
- `cleanup_unused_inl_groups()`

Cleanup behavior:

- Removes `bpy.data.node_groups` whose names start with `INL_` and whose `users` count is zero.
- Returns a list of removed group names.

## Packaging

File: `scripts/package_addon.py`

Purpose:

Creates an installable Blender add-on archive:

```text
procedural_noise_lab.zip
```

Command:

```bash
python scripts/package_addon.py
```

Packaging behavior:

- Root directory is the repository root.
- Package directory is `procedural_noise_lab`.
- Archive paths preserve the top-level `procedural_noise_lab/` directory.
- Excludes:
  - `__pycache__`
  - `.DS_Store`
  - `.pyc`
  - `.pyo`

The resulting zip can be installed in Blender through:

```text
Edit > Preferences > Add-ons > Install...
```

## Smoke Tests

File: `tests/smoke.py`

Run with:

```bash
blender --background --python tests/smoke.py
```

Test flow:

1. Adds repository root to `sys.path`.
2. Imports `procedural_noise_lab`.
3. Registers the add-on.
4. Imports recipe registry and validation modules.
5. Asserts recipes are registered.
6. Loads all presets and checks:
   - At least 20 presets exist.
   - At least one preset comes from a JSON pack.
7. Configures preset browser filters for Geometry grid presets and expects non-empty results.
8. For every registered recipe:
   - Builds a shader node group with `policy='SUFFIX'`.
   - Builds a geometry node group with `policy='SUFFIX'`.
   - Validates each generated group.
9. Deletes all objects.
10. Adds a plane.
11. Creates demo materials for every shader recipe.
12. Builds Infinite 4D Geometry group.
13. Creates Geometry Nodes demo setups in both `GRID` and `ACTIVE` modes.
14. Prints success.
15. Unregisters the add-on in a `finally` block.

The smoke test is valuable because it exercises Blender-specific APIs that normal Python syntax checks cannot cover.

## Recommended Development Checks

Syntax check:

```bash
python -m compileall procedural_noise_lab scripts tests
```

Blender integration smoke test:

```bash
blender --background --python tests/smoke.py
```

Package build:

```bash
python scripts/package_addon.py
```

Install test:

1. Build `procedural_noise_lab.zip`.
2. Install in Blender.
3. Enable the add-on.
4. Open Shader Editor.
5. Add each recipe.
6. Apply a preset.
7. Create demo material.
8. Open Geometry Nodes editor.
9. Create Geometry demo in both Grid and Active Mesh modes.

## Key Design Principles In The Codebase

### Native Blender Nodes Only

The add-on generates node trees made from Blender-native node types. This gives users editable and portable graphs.

### Safe Formula Builder

The formula builder uses a fixed operation list rather than evaluating user expressions. This avoids arbitrary code execution.

### Registry-Driven Recipes

Built-in recipes are centralized in `recipe_registry.py`, so operators, UI, demo targets, validation, presets, and tests can stay aligned.

### Metadata-Stamped Output

Generated groups carry custom properties identifying their recipe and generator version. This enables validation and future migration possibilities.

### Safe Rebuild Behavior

The `REBUILD` duplicate policy avoids mutating already-used node groups. If a group has users, a new suffixed group is created instead.

### Readable Generated Graphs

Node layout helpers organize generated graphs into stage frames, which makes the output more approachable to Blender users.

### Multi-Source Presets

The preset system can load built-in presets, shipped JSON preset packs, and user-saved presets.

## How To Add A New Built-In Recipe

Suggested steps:

1. Create a new file:

```text
procedural_noise_lab/recipe_new_effect.py
```

2. Define constants:

```python
RECIPE_ID = "new_effect"
RECIPE_VERSION = "1.0.0"
DISPLAY_NAME = "New Effect"
INTERNAL_NAME = "INL_New_Effect"
```

3. Define `INPUT_SPEC` and `OUTPUT_SPEC`.

4. Implement:

```python
def build(policy='REBUILD', tree_type='ShaderNodeTree'):
    ...
    return tree, reused_or_false
```

5. Use `interface_utils.get_or_create_group`.

6. Add sockets with `new_input` and `new_output`.

7. Create internal `NodeGroupInput` and `NodeGroupOutput`.

8. Build nodes and links using Blender's API.

9. Call:

```python
stamp_group(tree, RECIPE_ID, RECIPE_VERSION)
```

10. Register the recipe in `recipe_registry.RECIPES`.

11. Add an operator in `operators.py` or generalize the operator mapping.

12. Add a button in `ui.py` if the current UI mapping requires it.

13. Add presets in `presets_data.py` or a JSON pack.

14. Update tests if needed.

15. Run compile and Blender smoke tests.

## How To Add A Preset

Built-in preset option:

1. Edit `procedural_noise_lab/presets_data.py`.
2. Add a dict to the desired category list.
3. Include:
   - `name`
   - `target`
   - `values`
   - `desc`
   - optional `anim`

JSON pack option:

1. Add or edit a `.json` file in `procedural_noise_lab/preset_packs/`.
2. Use the pack schema described above.
3. Make sure values match actual group input socket names.

User preset option:

1. Select a group node in Blender.
2. Adjust input values.
3. Use `Save Current as Preset` in the Presets panel.

## How Preset Application Works

Preset application is socket-name based:

```text
for key, value in preset["values"].items():
  if key exists in node.inputs:
    node.inputs[key].default_value = value
```

Consequences:

- Preset keys must match group input socket names exactly.
- Extra preset keys are ignored.
- Missing preset values leave existing/default socket values unchanged.
- A preset can target only a subset of a recipe's inputs.

The operator warns and cancels if the selected group recipe does not match the preset target.

## How Geometry And Shader Variants Are Named

For registered recipes:

- Shader node group name:

```text
INL_Infinite_4D_Noise
```

- Geometry node group name:

```text
INL_Infinite_4D_Noise_Geo
```

The same builder supports both by switching `tree_type`.

The registry helper `RecipeInfo.group_name(tree_type)` encapsulates this convention, though individual build functions also compute names directly.

## Important Blender API Concepts Used

### Node Groups

Generated groups are stored in:

```python
bpy.data.node_groups
```

They are created with:

```python
bpy.data.node_groups.new(name, tree_type)
```

where `tree_type` is usually `ShaderNodeTree` or `GeometryNodeTree`.

### Group Interface

Blender 4.x uses:

```python
tree.interface.new_socket(...)
```

instead of older `tree.inputs` and `tree.outputs` APIs.

### Node Links

Links are created with:

```python
tree.links.new(output_socket, input_socket)
```

### Custom Properties

Recipe metadata is written as custom properties:

```python
group["inl_recipe_id"] = ...
```

### Operators

User actions are classes derived from `bpy.types.Operator`, registered through `bpy.utils.register_class`.

### Panels

UI panels derive from `bpy.types.Panel`.

### Property Groups

Persistent scene UI state is stored in a `bpy.types.PropertyGroup` attached to `Scene`.

## Strengths Of The Current Architecture

- Small, readable module boundaries.
- Central recipe registry.
- Clear separation between recipe construction and UI/operator code.
- Blender 4.x node interface helpers avoid repeated boilerplate.
- Safe duplicate policy avoids destructive rebuilds.
- Built-in validation catches missing sockets and unlinked outputs.
- Smoke tests exercise recipes, presets, validation, demo materials, and Geometry Nodes setup.
- Presets are extensible through JSON packs.
- Generated graphs are editable, inspectable, and portable.

## Potential Maintenance Risks

### Blender API Version Drift

Blender node socket names and node types can change across versions. The code already includes some compatibility checks, such as looking for both `Roughness` and `Detail Roughness` on the Wave Texture node.

Areas to monitor:

- Menu class names in `operators.register`.
- Geometry node socket names.
- Shader node socket indices for `ShaderNodeMix`.
- Animation driver data paths.
- Interface socket property names.

### Manual Operator/UI Mapping

Operators and UI buttons currently map recipe keys to operator IDs manually. Adding new recipes requires touching multiple files unless this is generalized.

### User Preset Filename Safety

User presets are saved as `<name>.json`. If names contain path separators or problematic filesystem characters, behavior may be undesirable. A slugified filename could be safer.

### Driver FPS Assumption

The driver helper first creates an expression involving scene FPS, then overwrites it with a 24 FPS fallback expression. This is robust but may surprise users in scenes with non-24 FPS timelines.

### Validation Scope

Validation checks structure and metadata, but it does not deeply verify semantic correctness of every internal node link beyond checking that outputs are linked.

### Formula Builder Metadata

Formula-built groups do not appear to be stamped with recipe metadata in the same registry-driven way as built-in recipes. This may be acceptable because formula groups are custom, but it limits validation and discovery.

## Extension Ideas

Possible future improvements:

- Make recipe operators dynamic so a new registered recipe automatically appears in the UI and add menu.
- Add migration helpers based on `inl_recipe_version`.
- Add preview thumbnails for presets.
- Add safer filename slugging for user presets.
- Add preset import/export UI.
- Add more validation checks for internal node existence and critical links.
- Add a formal schema validator for JSON preset packs.
- Add tests for user preset save/delete behavior using a temporary config path.
- Add tests for favorite toggling.
- Add configurable driver FPS behavior.
- Add generated documentation from the recipe registry.
- Add a richer material demo for color outputs, not only factor/height.
- Add support for applying presets to Geometry Nodes modifier inputs where appropriate.

## Quick Reference: Files And Responsibilities

| File | Responsibility |
|---|---|
| `procedural_noise_lab/__init__.py` | Blender add-on metadata and top-level register/unregister. |
| `procedural_noise_lab/interface_utils.py` | Blender 4.x group interface helpers and duplicate policy implementation. |
| `procedural_noise_lab/metadata.py` | Recipe/generator metadata constants and stamping helpers. |
| `procedural_noise_lab/node_layout.py` | Stage frames, layout anchors, and node-to-frame attachment. |
| `procedural_noise_lab/recipe_registry.py` | Central registry for built-in recipes and recipe lookup helpers. |
| `procedural_noise_lab/recipe_infinite_4d.py` | Flagship Infinite 4D Noise node group builder. |
| `procedural_noise_lab/recipe_domain_warp.py` | Focused domain-warped noise builder. |
| `procedural_noise_lab/recipe_animated_mask.py` | Animated procedural mask builder. |
| `procedural_noise_lab/recipe_liquid_marble.py` | Warped wave/liquid marble builder. |
| `procedural_noise_lab/custom_4d_noise.py` | Legacy Custom 4D Noise builder. |
| `procedural_noise_lab/formula_builder.py` | Safe operation-chain compiler into node groups. |
| `procedural_noise_lab/demo_material.py` | Demo material and Geometry Nodes demo setup builders. |
| `procedural_noise_lab/presets_data.py` | Built-in preset categories and values. |
| `procedural_noise_lab/preset_library.py` | Preset aggregation, filtering, favorites, and delete routing. |
| `procedural_noise_lab/preset_packs/geometry_surfaces.json` | Shipped JSON preset pack. |
| `procedural_noise_lab/presets_io.py` | User preset JSON save/load/delete. |
| `procedural_noise_lab/animation.py` | Time input keyframe and driver helpers. |
| `procedural_noise_lab/randomize.py` | Randomize/mutate exposed value inputs with lock groups. |
| `procedural_noise_lab/validation.py` | Node group validation and unused INL cleanup. |
| `procedural_noise_lab/properties.py` | Blender PropertyGroup definitions for settings and UI state. |
| `procedural_noise_lab/operators.py` | Blender operator classes and add-menu integration. |
| `procedural_noise_lab/ui.py` | Node Editor sidebar panels and UI lists. |
| `scripts/package_addon.py` | Builds installable add-on zip. |
| `tests/smoke.py` | Blender background smoke tests. |
| `README.md` | User-facing install, quick start, feature, and layout documentation. |
| `features.md` | Additional feature/spec notes. |
| `other ideas.md` | Additional planning/idea notes. |

## Mental Model For NotebookLM

If you need a compact mental model for this repository:

```text
Procedural Noise Lab is a Blender add-on.

Its main job is to programmatically build Blender node groups.

The built-in node groups are called recipes.

Each recipe declares:
  - a group name
  - a recipe ID
  - a recipe version
  - input sockets
  - output sockets
  - a build function

Operators call recipe build functions.

The UI calls operators.

Presets are dictionaries of socket-name/value pairs.

Applying a preset sets matching group-node input defaults.

Demo material and Geometry Nodes setup functions wire generated groups into usable examples.

Validation checks generated groups against recipe metadata and socket specs.

Packaging zips the procedural_noise_lab package for Blender installation.

Tests must run inside Blender because the code depends on bpy.
```

## Glossary

- **Blender add-on**: A Python package with `bl_info`, `register`, and `unregister` functions that extends Blender.
- **Node group**: A reusable Blender node tree with inputs and outputs.
- **ShaderNodeTree**: Blender node tree type used for shader/material node groups.
- **GeometryNodeTree**: Blender node tree type used for Geometry Nodes groups.
- **Recipe**: In this repo, a Python module/function that builds a specific node group.
- **INL**: Prefix used for Infinite Noise Lab/Procedural Noise Lab generated groups.
- **4D noise**: Blender noise texture sampled with XYZ vector coordinates plus W coordinate, often driven by time.
- **Domain warp**: A technique where one noise field perturbs the coordinates used to sample another noise field.
- **W coordinate**: Fourth coordinate used by Blender's 4D noise nodes.
- **Preset**: A named set of input socket values for a target recipe.
- **Pack preset**: A preset loaded from a shipped JSON file.
- **User preset**: A preset saved to Blender's user config directory.
- **Duplicate policy**: The strategy used when a node group with the desired name already exists.
- **Metadata stamp**: Custom properties written onto generated node groups identifying the recipe and generator version.

## Suggested Questions NotebookLM Can Answer From This Dossier

- What does this repository do?
- How does the Blender add-on register itself?
- What are the built-in noise recipes?
- How does Infinite 4D Noise work internally?
- How are presets loaded and filtered?
- How do JSON preset packs work?
- What is the difference between shader and geometry node groups?
- How does the demo material get created?
- How does the Geometry Nodes demo displace geometry?
- What does the smoke test verify?
- How would a developer add a new recipe?
- What are the main maintenance risks?
- Which files should be changed for a new preset?
- Which files should be changed for a new UI panel?
- Why does this project need Blender to test?

