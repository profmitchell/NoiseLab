# PRD: Blender Node Group Generator for Infinite Noise Lab

## 1. Product Name

Infinite Noise Lab: Node Group Generator

## 2. Product Summary

The Node Group Generator is the core engine of the Infinite Noise Lab Blender add-on.

Its job is to programmatically create reusable Blender node groups that behave like custom procedural noise nodes. Instead of asking the user to manually wire complex procedural setups, the generator builds complete, organized, native Blender node groups from predefined recipes.

The generator should create node groups such as:

- Infinite 4D Noise
- Domain Warped Noise
- Animated Mask Noise
- Liquid Marble Noise
- Ceramic Speckle Noise
- Energy Field Noise
- Procedural Grunge Noise

The generator should not execute arbitrary code, should not require OSL, and should not depend on a custom render engine. It should build everything using Blender’s native node system.

The main value is that users can click one button and receive a polished, reusable procedural node group with artist-facing controls.

## 3. Core Goal

The goal is to make complex procedural texture systems feel like custom nodes.

The user should be able to click:

Add Infinite 4D Noise

…and get a clean node group with inputs like:

- Vector
- Time
- Seed
- Scale
- Detail
- Warp Amount
- Morph
- Drift
- Stretch
- Contrast
- Threshold

…and outputs like:

- Fac
- Mask
- Height
- Color
- Warped Vector

The generated group should be editable, reusable, animatable, and compatible with normal Blender material workflows.

## 4. Why This Exists

Blender already has powerful procedural nodes, but advanced setups become messy quickly.

Artists repeatedly need the same procedural patterns:

- 4D animated noise
- Domain warping
- Noise masks
- Animated grunge
- Procedural bump
- Emission masks
- Organic texture breakup
- Time-based morphing
- Seeded variation

Doing this manually requires repetitive node wiring. The Node Group Generator solves this by creating organized, reusable node groups automatically.

This is especially useful because Blender’s Noise Texture gives a single W input, but artists often want many more W-like controls. The generator creates those controls by modifying coordinates, warping domains, layering noise, and shaping outputs.

## 5. Primary Users

The generator is primarily for:

- Blender material artists
- Motion designers
- VFX artists
- Procedural texture designers
- Shader-curious artists who do not want to write code
- Educators teaching procedural materials
- Technical artists who want repeatable node templates

It should be friendly enough for artists, but structured enough that technical users can inspect and modify the generated node trees.

## 6. Product Philosophy

The generator should follow one important principle:

Build native node groups, not black boxes.

The generated node groups should be made of normal Blender nodes. Users should be able to open them, inspect them, edit them, duplicate them, and learn from them.

The add-on should feel like a helper that creates excellent node architecture, not a closed proprietary system.

## 7. Non-Goals

The Node Group Generator should not initially:

- Execute user-written Python
- Execute GLSL
- Execute OSL
- Create a custom shader language
- Create a custom render engine
- Replace Blender’s Shader Editor
- Generate compositor node groups in the first version
- Generate Geometry Nodes groups in the first version
- Guarantee perfect mathematical equivalence to true higher-dimensional noise
- Build a formula parser in the MVP

The MVP should focus on reliable generation of native Shader Node groups.

## 8. Generator Responsibilities

The Node Group Generator is responsible for:

- Creating new Blender node groups
- Naming node groups consistently
- Adding group inputs
- Adding group outputs
- Creating internal nodes
- Connecting internal node links
- Setting default values
- Setting min/max ranges where possible
- Organizing internal nodes visually
- Adding frame labels
- Avoiding duplicate/conflicting node groups
- Inserting the generated node group into the active material
- Optionally creating demo materials
- Applying preset default values
- Supporting future recipe-based expansion

## 9. Generator Architecture

The generator should be recipe-driven.

A recipe defines:

- Node group name
- Node group type
- Description
- Input sockets
- Output sockets
- Internal node stages
- Node connections
- Default values
- UI labels
- Optional preset values
- Optional demo material wiring

The generator reads the recipe and creates the Blender node group.

This avoids hardcoding every node group manually in one large function.

## 10. Recipe Model

Each node group should be described by a structured recipe.

Conceptual recipe fields:

- id
- display_name
- internal_name
- version
- category
- description
- inputs
- outputs
- stages
- default_values
- tags
- compatibility
- demo_material_template

Example recipe identity:

id:
infinite_4d_noise

display_name:
Infinite 4D Noise

internal_name:
INL_Infinite_4D_Noise

category:
Noise / Animated

description:
A domain-warped 4D procedural noise group with artist-facing controls for time, seed, warp, morph, drift, stretch, contrast, threshold, and mask generation.

## 11. Input Definition Requirements

Each input should define:

- socket name
- socket type
- default value
- min value
- max value
- soft min value
- soft max value
- description
- whether it should be keyframe-friendly
- whether it is advanced or basic
- optional grouping label

Example input definition:

Name:
Time

Type:
Float

Default:
0.0

Soft Range:
0.0 to 10.0

Hard Range:
-1000.0 to 1000.0

Description:
A W-like animation control used to morph the procedural field over time.

Group:
Animation

Keyframe-friendly:
true

## 12. Output Definition Requirements

Each output should define:

- socket name
- socket type
- description
- intended use

Example output:

Name:
Mask

Type:
Float

Description:
A contrast-shaped procedural mask based on the final noise result.

Intended uses:
Alpha, Mix Factor, Emission Strength, Roughness mask, Material transition mask.

## 13. Core Node Group: INL_Infinite_4D_Noise

This is the flagship generated group.

### Purpose

Create a high-control procedural noise node that feels like it has many W-like parameters.

It should use native Blender noise and math nodes to create:

- Animated 4D noise
- Domain warping
- Seed variation
- Coordinate drift
- Coordinate stretch
- Morph control
- Contrast shaping
- Threshold mask
- Height output
- Color output
- Warped vector output

### Inputs

Basic inputs:

- Vector
- Time
- Seed
- Scale
- Detail
- Roughness
- Lacunarity
- Distortion
- Warp Amount
- Warp Scale
- Morph
- Contrast
- Threshold
- Invert

Advanced inputs:

- Warp Speed
- Drift X
- Drift Y
- Drift Z
- Stretch X
- Stretch Y
- Stretch Z
- Pulse Amount
- Fine Detail Amount
- Fine Detail Scale
- Output Min
- Output Max

### Outputs

- Fac
- Mask
- Height
- Color
- Warped Vector

### Internal Stages

The group should be organized into labeled stages:

1. Input Preparation
2. Coordinate Transform
3. Warp Field
4. Primary Noise
5. Fine Detail
6. Output Shaping
7. Outputs

## 14. Stage 1: Input Preparation

The generator should create internal reroutes or value nodes as needed to organize incoming inputs.

Goals:

- Keep the group readable.
- Separate artist controls into logical regions.
- Avoid spaghetti wiring.
- Prepare values for later math operations.

Inputs involved:

- Vector
- Time
- Seed
- Morph
- Scale
- Drift values
- Stretch values

Expected result:

A clean input section feeding into coordinate transform and animation control stages.

## 15. Stage 2: Coordinate Transform

Purpose:

Modify the incoming Vector before sampling noise.

Operations:

- Apply Stretch X/Y/Z
- Apply Drift X/Y/Z
- Apply Seed offset
- Optionally include simple coordinate rotation or mapping transform later

Conceptual behavior:

Prepared Vector = Vector stretched by axis controls + drift offset + seed offset

This gives the user additional “parameter axes” that change the noise result without needing actual 5D or 6D noise.

Expected nodes:

- Separate XYZ
- Math nodes for multiply/stretch
- Combine XYZ
- Vector Math Add
- Vector Math Scale
- Optional Mapping node

## 16. Stage 3: Warp Field

Purpose:

Use a secondary noise layer to distort the coordinates of the primary noise.

This creates domain warping.

Conceptual behavior:

Warp Noise = noise(prepared vector * warp scale, time * warp speed)

Warp Offset = warp noise converted into vector movement

Warped Vector = prepared vector + warp offset * warp amount

Expected nodes:

- Noise Texture set to 4D
- Math nodes for Time * Warp Speed
- Math nodes for Warp Scale
- Vector Math Scale
- Vector Math Add
- Optional Combine XYZ for turning scalar noise into vector offset
- Optional second/third warp noise channels for richer vector displacement

Important:

A simple MVP can use one scalar warp noise duplicated into vector offset. A more advanced version can use three different noise samples or offset variations to create X/Y/Z warp components.

## 17. Stage 4: Primary Noise

Purpose:

Generate the main 4D noise pattern.

Inputs:

- Warped Vector
- Time
- Morph
- Scale
- Detail
- Roughness
- Lacunarity
- Distortion

Conceptual behavior:

Primary Noise = 4D noise sampled using Warped Vector and W = Time + Morph

Expected nodes:

- Noise Texture set to 4D
- Math Add for Time + Morph
- Main Scale/Detail/Roughness/Lacunarity/Distortion connections

Expected outputs:

- Primary Fac
- Primary Color

## 18. Stage 5: Fine Detail

Purpose:

Add optional high-frequency noise detail.

Conceptual behavior:

Fine Noise = another 4D noise sampled at higher scale

Final Raw Noise = mix(primary noise, fine noise, fine detail amount)

Inputs:

- Fine Detail Amount
- Fine Detail Scale
- Time
- Warped Vector

Expected nodes:

- Secondary Noise Texture set to 4D
- Math Multiply for scale multiplier
- Mix or Math Add/Multiply nodes
- Clamp as needed

MVP note:

Fine Detail can be skipped in the earliest prototype if it makes the first implementation too complex. The generator should still reserve the architecture for it.

## 19. Stage 6: Output Shaping

Purpose:

Turn raw procedural noise into useful artist outputs.

Operations:

- Contrast adjustment
- Threshold mask generation
- Invert
- Output range remap
- Height output preparation

Expected outputs:

- Fac: shaped but still smooth
- Mask: thresholded or contrast-heavy output
- Height: bump/displacement-friendly grayscale
- Color: direct or colorized output
- Warped Vector: useful for downstream node groups

Expected nodes:

- Map Range
- Math Greater Than or ColorRamp-style thresholding
- Math Multiply/Add for contrast
- Math Subtract for invert
- Clamp
- Optional ColorRamp

Important:

The generated group should expose both soft and hard outputs. Artists often need both.

## 20. Stage 7: Outputs

The final output section should be clean and readable.

Outputs:

Fac:
Main grayscale procedural value.

Mask:
Contrast/threshold-shaped mask.

Height:
Grayscale height-friendly output for bump or displacement.

Color:
Color output from primary noise or colorized noise.

Warped Vector:
The transformed vector used internally.

## 21. Secondary Node Group: INL_Domain_Warped_Noise

This group is simpler and should be used as a focused domain-warping preset.

### Purpose

Create a clean domain-warped noise group with fewer controls than Infinite 4D Noise.

### Inputs

- Vector
- Time
- Seed
- Base Scale
- Base Detail
- Warp Scale
- Warp Detail
- Warp Amount
- Warp Speed
- Contrast
- Threshold
- Invert

### Outputs

- Fac
- Mask
- Height
- Warp Field

### Internal Stages

1. Vector preparation
2. Warp noise
3. Vector displacement
4. Base noise
5. Output shaping

### Use Cases

- Marble
- Smoke
- Abstract organic motion
- Flow fields
- Liquid-like patterns
- Terrain breakup

## 22. Tertiary Node Group: INL_Animated_Mask_Noise

This group should specialize in animated masks.

### Purpose

Create procedural masks that evolve over time.

### Inputs

- Vector
- Time
- Seed
- Scale
- Speed
- Morph
- Threshold
- Softness
- Contrast
- Edge Width
- Invert

### Outputs

- Soft Mask
- Hard Mask
- Edge Mask
- Height

### Use Cases

- Reveal effects
- Emission flicker
- Disintegration masks
- Fog breakup
- Glitch masks
- Video effects
- Animated material transitions

## 23. Generator UI Requirements

The Node Group Generator should be controlled from the Infinite Noise Lab add-on panel.

Panel section:

Node Group Generator

Buttons:

- Add Infinite 4D Noise
- Add Domain Warped Noise
- Add Animated Mask Noise
- Create Demo Material
- Duplicate Selected INL Group
- Rename Selected INL Group
- Clean Unused INL Groups

Preset controls:

- Category dropdown
- Preset dropdown
- Apply Preset
- Randomize Values
- Mutate Current Group

Developer/debug controls:

- Rebuild Node Group
- Print Recipe Info
- Validate Node Group
- Export Recipe JSON

Debug controls can be hidden behind an Advanced toggle.

## 24. Add Group Flow

When user clicks Add Infinite 4D Noise:

1. Check if there is an active material.
2. If no material exists, optionally create one.
3. Check whether node tree exists.
4. Check whether INL_Infinite_4D_Noise already exists.
5. If it exists, reuse or duplicate depending on user preference.
6. If it does not exist, create the node group from recipe.
7. Insert a group node into the active material node tree.
8. Place it near selected node or in a sensible default location.
9. Select the new group node.
10. Optionally connect basic output to material preview chain if user requested demo mode.

## 25. Demo Material Flow

When user clicks Create Demo Material:

1. Create or replace a material named INL_Demo_Material.
2. Enable nodes.
3. Create Texture Coordinate node.
4. Create INL_Infinite_4D_Noise group node.
5. Create ColorRamp.
6. Create Bump.
7. Create Principled BSDF.
8. Create Material Output.
9. Connect Texture Coordinate Object or Generated to Vector input.
10. Connect Fac to ColorRamp Fac.
11. Connect ColorRamp Color to Principled Base Color.
12. Connect Height to Bump Height.
13. Connect Bump Normal to Principled Normal.
14. Connect Principled BSDF to Material Output Surface.
15. Assign material to selected object.

Optional:

- Add Emission demo.
- Add roughness variation.
- Add displacement setup.

## 26. Node Group Duplicate Policy

If the node group already exists, the generator should not silently overwrite it.

Options:

- Reuse existing node group
- Create new copy with suffix
- Rebuild existing group
- Cancel

Default behavior:

Reuse existing group.

Advanced behavior:

If user holds a modifier or selects “Force Rebuild,” rebuild the group.

Suggested naming for duplicates:

- INL_Infinite_4D_Noise
- INL_Infinite_4D_Noise.001
- INL_Infinite_4D_Noise.002

## 27. Versioning Policy

Each generated node group should include version metadata where possible.

Metadata should include:

- Generator version
- Recipe ID
- Recipe version
- Created date if easy
- Add-on name

This helps future updates detect old groups.

Conceptual custom properties:

- inl_recipe_id
- inl_recipe_version
- inl_generator_version

## 28. Node Layout Requirements

Generated node groups should be readable.

Layout principles:

- Left-to-right flow
- Inputs on left
- Outputs on right
- Stages grouped in frames
- Avoid overlapping nodes
- Use consistent spacing
- Name important nodes clearly
- Label frames with plain-English names

Suggested horizontal stage layout:

Input Preparation:
x = 0

Coordinate Transform:
x = 300

Warp Field:
x = 700

Primary Noise:
x = 1100

Fine Detail:
x = 1500

Output Shaping:
x = 1900

Outputs:
x = 2300

Suggested vertical groupings:

Vector/control math near top

Noise textures in middle

Output shaping near bottom

## 29. Frame Labels

The generator should create frame nodes for internal organization.

Suggested frames:

- 01 Inputs
- 02 Coordinate Transform
- 03 Warp Field
- 04 Primary 4D Noise
- 05 Detail Layer
- 06 Output Shaping
- 07 Outputs

Each internal node should be parented to the relevant frame where possible.

## 30. Socket Naming Rules

Names should be artist-friendly.

Good names:

- Time
- Seed
- Morph
- Warp Amount
- Warp Scale
- Flow
- Drift X
- Stretch Y
- Contrast
- Threshold
- Mask
- Height

Avoid names like:

- Scalar A
- Vector Perturbation Coefficient
- Domain Offset Multiplier
- Fractal Coordinate Driver

The generated group can have technical internal node names, but public inputs should feel creative and understandable.

## 31. Parameter Grouping

The UI cannot always group node group inputs perfectly inside Blender’s node interface, so naming should help.

Recommended input order:

Core:

- Vector
- Time
- Seed

Noise:

- Scale
- Detail
- Roughness
- Lacunarity
- Distortion

Warp:

- Warp Amount
- Warp Scale
- Warp Speed

Motion:

- Morph
- Drift X
- Drift Y
- Drift Z

Shape:

- Stretch X
- Stretch Y
- Stretch Z
- Pulse Amount

Output:

- Contrast
- Threshold
- Invert
- Output Min
- Output Max

This keeps the node readable even if Blender shows one long input list.

## 32. Preset Integration

The generator should be able to apply preset default values to generated groups.

Preset example:

Preset:
Liquid Marble

Target group:
INL_Infinite_4D_Noise

Values:

- Scale: 8.0
- Detail: 14.0
- Roughness: 0.55
- Lacunarity: 2.2
- Distortion: 10.0
- Warp Amount: 2.5
- Warp Scale: 3.0
- Warp Speed: 0.25
- Morph: 0.35
- Contrast: 1.8
- Threshold: 0.45

The generator should support:

- Default recipe values
- Preset override values
- User-randomized values
- Mutation values

## 33. Randomization Requirements

The generator should eventually support a Randomize button.

Randomize should:

- Change only exposed values
- Respect safe min/max ranges
- Avoid unusable extremes
- Keep user wiring intact
- Allow random seed locking
- Allow parameter locks

Controls:

- Randomize All
- Mutate Slightly
- Lock Scale
- Lock Time
- Lock Output Shaping
- Lock Warp
- Lock Animation

Mutation should be preferable to full randomization.

Mutation means:

Take current values and nudge them within a percentage range.

Example:

Mutation Amount:
20%

Scale:
Current 10.0 → random between 8.0 and 12.0

## 34. Time Animation Helper

The generator should support easy animation of the Time input.

MVP option:

- Insert keyframes on Time input.
- Frame 1: Time = 0
- Frame 120: Time = 1
- Set interpolation to linear if possible.

Advanced option:

- Add driver using frame number.
- Provide Speed parameter.
- Time = frame * speed

User-facing buttons:

- Animate Time
- Clear Time Animation
- Set Loop Length
- Set Speed

## 35. Looping Noise Consideration

A future feature should support loop-friendly animation.

Problem:

Animating W from 0 to 1 does not automatically loop seamlessly.

Possible solutions:

- Use circular sampling through sine/cosine controls.
- Blend start/end fields.
- Use 4D or higher conceptual mapping where time follows a loop path.
- Generate loop-specific node groups.

Future node group:

INL_Looping_4D_Noise

Inputs:

- Vector
- Frame
- Loop Length
- Scale
- Warp
- Morph

Outputs:

- Fac
- Mask
- Height

This is not MVP, but it is a very strong feature for motion design.

## 36. Error Handling Requirements

The generator should provide friendly messages for common failures.

Cases:

No active object:
“Select an object first.”

No material:
“No material found. Create a new material?”

No node tree:
“Active material does not use nodes. Enable nodes?”

Existing node group:
“INL_Infinite_4D_Noise already exists. Reusing existing group.”

Unsupported version:
“This add-on is designed for Blender 5.1. Some nodes may not work in this version.”

Invalid recipe:
“Node group recipe is invalid. Missing required input or output.”

Failed node creation:
“Could not create node group. Check console for details.”

## 37. Validation Requirements

The generator should include validation utilities.

Recipe validation:

- Recipe has ID.
- Recipe has display name.
- Recipe has internal name.
- Recipe has at least one output.
- Input names are unique.
- Output names are unique.
- Socket types are valid.
- Default values match socket type.
- Required internal nodes are available in current Blender version.

Node group validation:

- Group exists.
- Required inputs exist.
- Required outputs exist.
- Primary noise node exists.
- Required links exist.
- No missing sockets.
- No obvious orphaned critical nodes.

## 38. Supported Socket Types

MVP should support:

- Float
- Vector
- Color
- Boolean if Blender socket support is clean

Outputs:

- Float
- Vector
- Color

The most important are Float and Vector.

## 39. Blender Compatibility

Primary target:

- Blender 5.1

Secondary target:

- Blender 5.0 if easy
- Blender 4.4+ if easy

The generator should avoid using features that are too new unless necessary.

If a node type or socket behavior changes in Blender 5.1, the add-on should isolate that logic in a compatibility layer.

## 40. File Structure Recommendation

Suggested add-on structure:

infinite_noise_lab/
  __init__.py
  operators/
    create_node_group.py
    create_demo_material.py
    randomize_group.py
    animate_time.py
  panels/
    shader_editor_panel.py
  core/
    generator.py
    recipes.py
    sockets.py
    node_layout.py
    node_utils.py
    validation.py
    presets.py
  recipes/
    infinite_4d_noise.json
    domain_warped_noise.json
    animated_mask_noise.json
  presets/
    organic.json
    abstract.json
    surface_imperfections.json
    motion_design.json
  docs/
    README.md

The generator should be modular from the start. Do not put everything in one massive __init__.py file.

## 41. Core Generator API Concept

The core generator should expose clear internal functions.

Conceptual API:

create_node_group_from_recipe(recipe)

insert_group_into_active_material(group_name)

create_demo_material(recipe_or_group_name)

apply_preset_to_group(group_node, preset)

randomize_group_inputs(group_node, settings)

validate_recipe(recipe)

validate_generated_group(group)

No UI code should be mixed deeply into the generation logic.

The UI should call operators.

Operators should call generator functions.

Generator functions should call low-level node utilities.

## 42. Low-Level Utility Responsibilities

node_utils should handle:

- Create node group
- Create input socket
- Create output socket
- Create node by type
- Set node location
- Create link
- Set default value
- Find socket by name
- Create frame
- Parent node to frame
- Set node label
- Set node color if supported
- Clean node tree

sockets should handle:

- Socket type mapping
- Default values
- Min/max ranges
- Socket descriptions if supported
- Blender version-specific socket creation differences

node_layout should handle:

- Stage positions
- Node spacing
- Frame placement
- Auto-layout helper functions

validation should handle:

- Recipe validation
- Node group validation
- Compatibility checks

## 43. Implementation Priority

The first implementation should be deliberately simple.

Priority 1:

Generate one useful node group that works.

Priority 2:

Make it readable.

Priority 3:

Make it easy to insert into a material.

Priority 4:

Add presets.

Priority 5:

Add animation helpers.

Do not start with formula parsing, preview thumbnails, compositor support, or complex geometry node generation.

## 44. MVP Acceptance Criteria

The MVP is complete when:

- The add-on installs in Blender 5.1.
- The Shader Editor panel appears.
- Clicking “Add Infinite 4D Noise” creates a node group.
- The group has the planned inputs and outputs.
- The group uses native Blender nodes.
- The group can be inserted into an active material.
- The Fac output can drive Base Color or Roughness.
- The Height output can drive Bump.
- The Time input changes/morphs the noise.
- Warp Amount visibly affects the texture.
- Contrast and Threshold shape the output.
- Existing node groups are not accidentally overwritten.
- The generated internal node tree is organized into frames.

## 45. Example Generated Node Group Behavior

User creates Infinite 4D Noise.

They connect:

- Texture Coordinate Generated → Vector
- Fac → ColorRamp Fac
- ColorRamp Color → Base Color
- Height → Bump Height
- Bump Normal → Principled BSDF Normal

Then they change:

Time:
The pattern morphs.

Scale:
The pattern gets larger or smaller.

Warp Amount:
The pattern becomes more fluid and distorted.

Morph:
The character of the pattern shifts.

Threshold:
The mask becomes more graphic and high-contrast.

This is the desired core experience.

## 46. Example Presets for Testing

The MVP should include at least five test presets.

### Smoke Bloom

- Low scale
- High detail
- Medium warp
- Low contrast
- Slow time

### Liquid Marble

- Medium scale
- High distortion
- High warp
- Medium contrast
- Slow morph

### Ceramic Speckle

- High scale
- Low warp
- High threshold
- High contrast
- Low height strength

### Energy Veins

- Medium scale
- High contrast
- High threshold
- Medium warp
- Emission-friendly mask

### VHS Dirt

- High scale
- Medium detail
- Medium threshold
- Slight drift
- High contrast

## 47. Documentation for Developers

Developer documentation should explain:

- How recipes work.
- How to add a new node group recipe.
- How to add a new input.
- How to add a new output.
- How internal stages are laid out.
- How to create links safely.
- How presets override defaults.
- How to avoid overwriting user-modified node groups.
- How to test in Blender 5.1.

## 48. Documentation for Users

User documentation should explain:

- What the Node Group Generator does.
- How to add a generated node group.
- What Time/W means.
- Why Time morphs noise.
- What domain warping means.
- How to connect Fac, Mask, Height, Color, and Warped Vector.
- How to animate Time.
- How to use presets.
- How to duplicate and edit generated groups.
- How to use generated groups for materials, masks, displacement, and emission.

## 49. Testing Plan

Test cases:

### Installation

- Add-on installs.
- Add-on enables.
- Panel appears.

### Basic Generation

- Infinite 4D Noise group creates successfully.
- Domain Warped Noise group creates successfully.
- Animated Mask Noise group creates successfully.

### Material Insertion

- Group inserts into existing material.
- Group creates material if needed.
- Demo material works.

### Duplicate Handling

- Existing group is reused.
- Duplicate group can be created.
- Rebuild does not crash.

### Output Testing

- Fac output works.
- Mask output works.
- Height output works.
- Color output works.
- Warped Vector output works.

### Parameter Testing

- Time changes the result.
- Seed changes the result.
- Scale changes the result.
- Warp Amount changes the result.
- Threshold changes the mask.
- Invert flips the output.

### Preset Testing

- Presets load.
- Presets apply values.
- Invalid preset does not crash.

### Version Testing

- Blender 5.1 primary.
- Optional 5.0 and 4.4+ if feasible.

## 50. Performance Requirements

Generated node groups should not be absurdly heavy.

MVP performance guidelines:

- Use a reasonable number of Noise Texture nodes.
- Avoid huge stacks of unnecessary math nodes.
- Avoid recursive or driver-heavy setups.
- Keep the Infinite 4D Noise group powerful but not monstrous.
- Provide simpler group variants for lighter use.

Suggested node counts:

Domain Warped Noise:
Approx. 15–35 internal nodes.

Infinite 4D Noise:
Approx. 35–80 internal nodes.

Animated Mask Noise:
Approx. 20–45 internal nodes.

If a node group gets too complex, split it into Lite and Advanced versions.

## 51. Lite vs Advanced Groups

Future versions should include:

INL_Infinite_4D_Noise_Lite

Purpose:

Fast and readable.

Inputs:

- Vector
- Time
- Seed
- Scale
- Detail
- Warp Amount
- Warp Scale
- Contrast
- Threshold

Outputs:

- Fac
- Mask
- Height

INL_Infinite_4D_Noise_Advanced

Purpose:

Full procedural control.

Includes all advanced parameters.

This helps avoid overwhelming new users.

## 52. Risks

### Risk: Too many controls make the node intimidating

Mitigation:

- Provide Lite versions.
- Provide presets.
- Use clear naming.
- Use good defaults.

### Risk: Generated node tree becomes messy

Mitigation:

- Strong layout rules.
- Frame nodes.
- Modular stage-based generation.

### Risk: Blender socket API changes

Mitigation:

- Compatibility helper functions.
- Version checks.
- Keep socket creation centralized.

### Risk: Users expect true infinite-dimensional noise

Mitigation:

- Documentation should explain that the add-on creates W-like artistic controls through coordinate transforms, domain warping, and layered 4D noise.

### Risk: Formula parsing becomes tempting too early

Mitigation:

- Keep formula parser out of MVP.
- Build a stable recipe system first.

## 53. Future Expansion

Future generator features:

- Geometry Nodes group generation
- Compositor node group generation
- Looping noise group
- Audio-reactive driver templates
- Formula-to-node safe parser
- Preset thumbnail rendering
- Node group export/import
- Batch material creation
- Procedural texture library browser
- Integration with asset browser
- User-created recipe editor
- One-click “make this animated”
- One-click “make this tileable”
- One-click “make this loopable”
- Randomization/mutation engine
- Preset morphing between two generated node groups

## 54. Strong Recommendation

Build this in this order:

1. Hardcoded generator for INL_Infinite_4D_Noise.
2. Refactor hardcoded logic into reusable generator utilities.
3. Add recipe format.
4. Add Domain Warped Noise recipe.
5. Add demo material generation.
6. Add presets.
7. Add randomize/mutate.
8. Add animation helper.
9. Only then consider formula parsing.

This avoids over-engineering too early.

The first victory should be simple:

Click one button, get a powerful custom-looking node group, animate Time, and see the texture morph.

## 55. Final Vision

The Node Group Generator is the foundation of Infinite Noise Lab.

It turns procedural node design into a reusable creative system.

Instead of manually building complex node networks every time, users can generate polished procedural nodes that feel like custom shader instruments.

The generator should make Blender’s procedural texture system feel deeper, faster, and more musical without leaving Blender’s native node workflow.