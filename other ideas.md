# PRD: Infinite Noise Lab — Blender Add-on for Parametric 4D Procedural Noise Nodes

## 1. Product Overview

Infinite Noise Lab is a Blender add-on that creates artist-friendly procedural noise node groups with many exposed “W-like” parameters.

The goal is to let artists build rich, animated, morphable, domain-warped procedural textures without needing to write shader code. The add-on does not create a new render engine and does not execute arbitrary user code. Instead, it generates native Blender Shader Node and/or Geometry Node groups using Blender’s built-in procedural nodes, math nodes, vector math nodes, mapping nodes, ramps, and value controls.

The add-on behaves like a procedural texture instrument: users can add a custom node group such as “Infinite 4D Noise,” then shape it with controls like Time, Seed, Morph, Warp, Flow, Twist, Stretch, Turbulence, Contrast, Threshold, and Detail.

The core idea is not true infinite-dimensional noise. Instead, the add-on gives artists many meaningful control axes that reshape how 4D noise is sampled, warped, mixed, and remapped.

## 2. Problem Statement

Blender’s built-in Noise Texture is powerful but limited as an artist-facing control surface. The 4D mode exposes W, which is excellent for animation and morphing, but artists often want more high-level parameters that feel like additional “dimensions” of procedural variation.

Current problems:

- Noise Texture is useful but generic.
- Complex procedural setups require manually wiring many nodes.
- Domain warping is powerful but tedious to build repeatedly.
- Animated noise can look like simple scrolling if users only animate coordinates.
- Artists want richer controls like morph, drift, warp, pulse, seed, flow, and turbulence.
- Reusing procedural node systems across projects is annoying unless users manually save node groups.
- Writing custom shader code or OSL is intimidating and may not work across all render modes.

Infinite Noise Lab solves this by generating reusable, named node groups that expose expressive procedural controls while remaining built from native Blender nodes.

## 3. Target Users

Primary users:

- Blender artists creating procedural materials.
- Motion designers using Blender for abstract visuals.
- VFX artists creating masks, displacement, fog, smoke-like effects, energy fields, liquid surfaces, and grunge.
- Educators teaching procedural texture concepts.
- Technical artists who want fast node group generation without repeatedly wiring boilerplate.

Secondary users:

- Shader artists who want quick starting templates.
- Geometry Nodes users who want animated procedural masks.
- Video artists using Blender as a compositing or visual effects tool.
- Music visualizer artists who want audio-reactive-looking procedural motion.

## 4. Product Goals

The add-on should:

- Generate powerful procedural noise node groups automatically.
- Provide many W-like control parameters.
- Stay compatible with Blender’s native shader/node workflow.
- Avoid arbitrary code execution.
- Work in Shader Editor first, with Geometry Nodes support as a later phase.
- Make advanced techniques like domain warping accessible.
- Allow users to save, reuse, and customize procedural noise presets.
- Support animated parameters, especially Time/W-style controls.
- Keep the interface artist-friendly and not overly technical.
- Make procedural noise feel like a synth patch: tweakable, expressive, and performable.

## 5. Non-Goals

The add-on should not initially:

- Create a custom render engine.
- Require OSL.
- Require GLSL editing.
- Execute raw text formulas as code.
- Replace Blender’s material system.
- Support every possible mathematical function at launch.
- Guarantee identical results across all future Blender versions.
- Build a full node-based shader language compiler in version 1.

Formula parsing may be explored later, but version 1 should focus on safe preset-based procedural node generation.

## 6. Core Concept

The user wants more controls like W. In Blender, W is a fourth coordinate used by 4D noise. It lets the user move through another axis of the noise field, often animated as time.

Infinite Noise Lab extends this feeling by exposing additional parameters that modify the sampling domain before the final noise is evaluated.

Conceptual model:

Noise does not only receive Vector and W.

Instead, the node group internally builds something like:

Noise(
  transformed Vector,
  transformed W
)

Where transformed Vector and transformed W are affected by user controls:

- Time
- Seed
- Morph
- Warp
- Drift
- Flow
- Twist
- Stretch
- Pulse
- Turbulence
- Secondary Noise
- Contrast
- Threshold

These are not true extra dimensions in the mathematical sense. They are artist-facing controls that reshape the procedural field.

## 7. MVP Feature Set

### 7.1 Add-on Panel

The add-on should add a panel to Blender’s Shader Editor sidebar.

Panel name:

Infinite Noise Lab

Suggested location:

Shader Editor > Sidebar > Infinite Noise Lab

The panel should include:

- Add Infinite 4D Noise Node Group
- Add Domain Warped Noise Node Group
- Add Animated Mask Noise Node Group
- Add Procedural Grunge Node Group
- Add Liquid Marble Node Group
- Add Energy Field Node Group
- Create Material From Selected Preset
- Save Current Node Group as Preset
- Refresh Preset Library

For MVP, only the first one or two node groups need to be fully implemented.

### 7.2 Generated Node Group: Infinite 4D Noise

This is the flagship node group.

Node group name:

INL_Infinite_4D_Noise

Inputs:

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
- Warp Speed
- Morph
- Drift X
- Drift Y
- Drift Z
- Stretch X
- Stretch Y
- Stretch Z
- Twist Amount
- Pulse Amount
- Contrast
- Threshold
- Invert
- Output Min
- Output Max

Outputs:

- Fac
- Mask
- Height
- Color
- Warped Vector

Input behavior:

Vector:
The spatial coordinate input. Usually connected to Texture Coordinate > Generated/Object/UV.

Time:
A W-like animation control. Users can keyframe it or drive it with frame number.

Seed:
Offsets the procedural field so users can find different variations.

Scale:
Main noise scale.

Detail:
Controls fractal depth of the main noise.

Roughness:
Controls strength of higher-frequency detail.

Lacunarity:
Controls frequency spacing between detail layers.

Distortion:
Controls built-in noise distortion.

Warp Amount:
Controls how strongly secondary noise bends the vector coordinates.

Warp Scale:
Controls size of the warping field.

Warp Speed:
Controls how quickly the warping field evolves over Time.

Morph:
A second W-like macro control. It changes the blend or offset between multiple noise layers.

Drift X/Y/Z:
Offsets the sample position over space. Useful for directional motion.

Stretch X/Y/Z:
Scales individual coordinate axes before noise evaluation.

Twist Amount:
Rotates or bends coordinates around an axis where possible. In MVP, this can be approximated with vector math and mapping rotation rather than true spatial twist.

Pulse Amount:
Adds rhythmic or sine-like modulation to the noise intensity or W input.

Contrast:
Sharpens or softens the final noise.

Threshold:
Turns soft noise into a stronger mask.

Invert:
Flips the output.

Output Min/Max:
Remaps the final range.

### 7.3 Generated Node Group: Domain Warped Noise

Node group name:

INL_Domain_Warped_Noise

Purpose:

A simpler node group focused on the classic domain-warping technique.

Internal structure:

- Texture Coordinate / Vector input
- Mapping or Vector Math stage
- Secondary 4D Noise creates warp field
- Warp field offsets Vector
- Main 4D Noise samples warped Vector
- ColorRamp or Map Range shapes final output

Inputs:

- Vector
- Time
- Base Scale
- Base Detail
- Warp Scale
- Warp Detail
- Warp Amount
- Warp Time Offset
- Contrast
- Threshold
- Seed

Outputs:

- Fac
- Mask
- Height
- Warp Field

### 7.4 Generated Node Group: Animated Mask Noise

Node group name:

INL_Animated_Mask_Noise

Purpose:

A procedural animated mask for reveal effects, abstract video textures, compositing, emissive patches, material transitions, grunge animation, and displacement masks.

Inputs:

- Vector
- Time
- Scale
- Speed
- Morph
- Threshold
- Softness
- Contrast
- Edge Width
- Invert
- Seed

Outputs:

- Soft Mask
- Hard Mask
- Edge Mask
- Height

This node group should make it easy to create animated procedural masks where the pattern evolves instead of merely sliding.

## 8. Recommended MVP Scope

Version 0.1 should include:

- Add-on registration.
- Shader Editor sidebar panel.
- Operator to create INL_Infinite_4D_Noise.
- Operator to create INL_Domain_Warped_Noise.
- Generated node groups using native Blender shader nodes.
- Automatic insertion of selected node group into the active material node tree.
- Optional creation of a demo material.
- Basic preset list stored as JSON.
- No formula parser yet.
- No OSL yet.
- No external dependencies.

This version should prove the core value: one click creates a complex, reusable procedural noise engine with many exposed controls.

## 9. User Flow

### 9.1 Basic Flow

1. User opens Blender.
2. User installs and enables Infinite Noise Lab.
3. User selects an object.
4. User opens Shader Editor.
5. User opens the Infinite Noise Lab sidebar panel.
6. User clicks “Add Infinite 4D Noise.”
7. The add-on creates the node group if it does not already exist.
8. The add-on inserts the node group into the active material.
9. The user connects outputs to Principled BSDF, ColorRamp, Bump, Displacement, Roughness, Emission, or Mix nodes.
10. User animates the Time input.
11. Noise morphs organically.

### 9.2 Create Demo Material Flow

1. User selects an object.
2. User clicks “Create Demo Material.”
3. Add-on creates a new material named “INL Demo Material.”
4. Material contains:
   - Texture Coordinate
   - Infinite 4D Noise node group
   - ColorRamp
   - Bump
   - Principled BSDF
   - Material Output
5. Noise Fac connects to ColorRamp.
6. ColorRamp connects to Base Color.
7. Noise Height connects to Bump Height.
8. Bump Normal connects to Principled BSDF Normal.
9. User immediately sees a procedural animated-ready material.

### 9.3 Preset Flow

1. User selects a preset such as “Liquid Metal,” “VHS Dirt,” “Nebula Smoke,” or “Ceramic Speckle.”
2. User clicks “Apply Preset.”
3. Add-on creates the relevant node group with preset default values.
4. User tweaks exposed controls.

## 10. Preset Library

Initial preset categories:

### Organic

- Cloud Morph
- Smoke Field
- Fog Breakup
- Bark Grain
- Stone Veins
- Moss Patches

### Abstract

- Energy Field
- Plasma Sheet
- Liquid Marble
- Cellular Drift
- Nebula Bloom
- Vortex Noise

### Surface Imperfections

- Ceramic Speckle
- Dust Mask
- Scratches
- Fingerprint Grime
- Chipped Paint
- Oxidized Metal

### Video / Motion Design

- VHS Dirt
- Glitch Grain
- Light Leak Mask
- Animated Reveal
- Pulsing Scan Texture
- Heat Distortion Mask

### Displacement

- Micro Bumps
- Terrain Breakup
- Lava Surface
- Cloth Irregularity
- Rippled Glass
- Cracked Surface

## 11. Node Architecture

The generated node group should be built from native Blender nodes.

Potential internal nodes:

- Noise Texture
- Voronoi Texture
- Wave Texture
- Mapping
- Texture Coordinate
- Vector Math
- Math
- Map Range
- ColorRamp
- Mix
- Combine XYZ
- Separate XYZ
- Value
- RGB
- Bump
- Displacement, optionally outside group
- Frame nodes for organization
- Reroute nodes for readability

The first implementation should prioritize reliability over mathematical purity.

## 12. Internal Signal Design

The core group can be thought of as these stages:

### Stage 1: Coordinate Preparation

Inputs:

- Vector
- Drift X/Y/Z
- Stretch X/Y/Z
- Seed

Operations:

- Apply stretch/scaling to vector axes.
- Add drift offsets.
- Add seed offset.
- Optionally rotate or transform coordinates.

Output:

Prepared Vector

### Stage 2: Warp Field

Inputs:

- Prepared Vector
- Time
- Warp Scale
- Warp Amount
- Warp Speed
- Morph

Operations:

- Feed Prepared Vector into secondary 4D noise.
- Use Time and Warp Speed for W.
- Convert warp noise into vector offset.
- Multiply by Warp Amount.
- Add to Prepared Vector.

Output:

Warped Vector

### Stage 3: Primary Noise

Inputs:

- Warped Vector
- Time
- Scale
- Detail
- Roughness
- Lacunarity
- Distortion
- Morph

Operations:

- Feed Warped Vector into main 4D Noise Texture.
- Use Time plus Morph offset as W.
- Generate primary Fac and Color.

Output:

Raw Noise

### Stage 4: Detail Layer

Inputs:

- Warped Vector
- Time
- Detail Controls

Operations:

- Add optional secondary high-frequency noise.
- Mix with primary noise.
- Control amount with Turbulence or Detail Mix.

Output:

Detailed Noise

### Stage 5: Shaping

Inputs:

- Raw/Detailed Noise
- Contrast
- Threshold
- Output Min
- Output Max
- Invert

Operations:

- Apply contrast via math/remap.
- Apply threshold to make hard mask.
- Apply output min/max.
- Optional invert.

Outputs:

- Fac
- Mask
- Height
- Color
- Warped Vector

## 13. Important Technical Decision

The add-on should generate node groups instead of attempting to evaluate custom text formulas.

Reasons:

- Safer.
- Easier to ship.
- More compatible with Blender.
- Works with native material workflows.
- Users can inspect/edit generated nodes.
- Avoids security risks of arbitrary code.
- Avoids renderer limitations of OSL.
- Easier for Blender artists to understand.

Formula-like behavior can be added later as a visual preset builder, not raw code execution.

## 14. Formula System: Future Version

A later version can include a safe formula-inspired builder.

Instead of allowing arbitrary code like:

sin(noise(p * 4.0 + time) * 12.0)

The add-on can provide a controlled expression grammar:

Allowed functions:

- noise()
- voronoi()
- wave()
- sin()
- cos()
- add()
- multiply()
- power()
- clamp()
- smoothstep()
- abs()
- invert()
- mix()
- maprange()

Allowed variables:

- x
- y
- z
- time
- seed
- morph
- audio
- scale

The parser would convert expressions into Blender node trees.

Future example:

User enters:

smoothstep(0.4, 0.7, noise(vector * scale, time + morph))

The add-on builds:

- Vector scaling nodes
- Noise Texture
- Math nodes
- Map Range or ColorRamp approximation
- Output nodes

This should be considered version 2 or later.

## 15. UI Requirements

The UI should feel simple and creative.

Panel sections:

### Create

- Add Infinite 4D Noise
- Add Domain Warped Noise
- Add Animated Mask Noise
- Create Demo Material

### Presets

- Category dropdown
- Preset dropdown
- Apply Preset
- Save Current Setup

### Animation Helpers

- Add Time Driver
- Remove Time Driver
- Set Speed
- Bake Current Frame Value

### Utilities

- Rename Node Groups
- Clean Unused INL Node Groups
- Duplicate Selected INL Group
- Open Documentation

## 16. Time Driver Feature

The add-on should provide a button:

Add Time Driver

Purpose:

Automatically animate the Time input.

Possible behavior:

- Adds a driver expression based on frame number.
- User can set speed.
- Example concept:
  Time = frame * speed

The user should not need to manually keyframe Time for basic animation.

Important:

The add-on should avoid fragile driver setup in MVP if it slows development. A simpler MVP can set keyframes at frame 1 and frame 120.

Preferred MVP behavior:

- Add two keyframes to the Time input.
- Frame 1: Time = 0
- Frame 120: Time = 1
- Set interpolation to linear if possible.

Future behavior:

- True driver support with adjustable speed.

## 17. Compatibility Requirements

Primary target:

- Blender 5.1

Secondary target if easy:

- Blender 4.3+
- Blender 4.4+
- Blender 5.0+

Renderer expectations:

- Should work with Eevee where native nodes are supported.
- Should work with Cycles where native nodes are supported.
- Should avoid OSL in MVP.

The add-on should use Blender’s Python API and native node types only.

## 18. Data Storage

The preset library can be stored as JSON.

Example preset fields:

- preset_name
- category
- node_group_type
- default_values
- description
- suggested_outputs
- animation_hint

Example preset:

{
  "preset_name": "Liquid Marble",
  "category": "Abstract",
  "node_group_type": "INL_Infinite_4D_Noise",
  "default_values": {
    "Scale": 7.5,
    "Detail": 12.0,
    "Roughness": 0.58,
    "Lacunarity": 2.1,
    "Distortion": 8.0,
    "Warp Amount": 1.2,
    "Warp Scale": 3.0,
    "Morph": 0.35,
    "Contrast": 1.8,
    "Threshold": 0.45
  },
  "description": "Fluid, warped procedural texture for marble, liquid metal, and abstract motion.",
  "suggested_outputs": ["Base Color", "Bump", "Emission Mask"],
  "animation_hint": "Animate Time from 0 to 2 over 240 frames."
}

## 19. Safety Requirements

The add-on must not:

- Execute arbitrary user-entered Python.
- Execute arbitrary shader code.
- Load external scripts without explicit user permission.
- Modify files outside its own preset/config directory unless exporting presets.
- Automatically overwrite existing node groups without warning.

If a node group already exists:

Options:

- Reuse existing group.
- Create duplicate with incremented name.
- Replace only if user confirms.

## 20. Error Handling

The add-on should handle:

- No active object selected.
- Selected object has no material.
- Active material has no node tree.
- Shader Editor not open.
- Node group already exists.
- Unsupported Blender version.
- Missing preset JSON.
- Invalid preset values.
- Failed driver/keyframe assignment.

User-facing error messages should be clear:

- “Select an object with a material first.”
- “No active material found. Create one?”
- “This preset requires an Infinite 4D Noise group.”
- “A node group with this name already exists. Reusing existing group.”

## 21. Naming Conventions

Add-on name:

Infinite Noise Lab

Internal prefix:

INL_

Node groups:

- INL_Infinite_4D_Noise
- INL_Domain_Warped_Noise
- INL_Animated_Mask_Noise
- INL_Liquid_Marble
- INL_Procedural_Grunge
- INL_Energy_Field

Materials:

- INL_Demo_Material
- INL_Liquid_Marble_Material
- INL_Grunge_Material

Presets:

Use readable names, not technical names.

Example:

- Liquid Marble
- Smoke Bloom
- VHS Dirt
- Ceramic Speckle
- Nebula Pulse

## 22. UX Principles

The add-on should feel like an instrument, not a math textbook.

Controls should be named for artistic results:

Prefer:

- Flow
- Morph
- Warp
- Pulse
- Drift
- Grain
- Breakup
- Contrast
- Edge

Avoid overusing:

- Domain transform
- Scalar field
- Coordinate perturbation
- Fractal derivative
- High-dimensional sampling

Advanced users can inspect the generated node tree if they want the technical details.

## 23. Suggested Control Ranges

Time:
0.0 to 100.0

Seed:
0.0 to 1000.0

Scale:
0.1 to 100.0

Detail:
0.0 to 16.0

Roughness:
0.0 to 1.0

Lacunarity:
0.0 to 8.0

Distortion:
0.0 to 20.0

Warp Amount:
0.0 to 10.0

Warp Scale:
0.1 to 50.0

Warp Speed:
-10.0 to 10.0

Morph:
0.0 to 1.0, or 0.0 to 100.0 depending on implementation

Drift X/Y/Z:
-100.0 to 100.0

Stretch X/Y/Z:
0.01 to 10.0

Twist Amount:
-10.0 to 10.0

Pulse Amount:
0.0 to 1.0

Contrast:
0.0 to 10.0

Threshold:
0.0 to 1.0

Output Min:
0.0 to 1.0

Output Max:
0.0 to 1.0

## 24. MVP Implementation Milestones

### Milestone 1: Add-on Skeleton

Deliverables:

- Blender add-on folder.
- __init__.py.
- Add-on metadata.
- Register/unregister functions.
- Shader Editor sidebar panel.
- One test button.

Success criteria:

- Add-on installs and enables in Blender.
- Panel appears in Shader Editor.
- Test operator runs without error.

### Milestone 2: Create Basic Infinite 4D Noise Group

Deliverables:

- Function that creates INL_Infinite_4D_Noise node group.
- Exposed inputs and outputs.
- Basic internal Noise Texture.
- Group inserted into active material.

Success criteria:

- User clicks button.
- Node group appears in active material.
- Fac output works when connected to color/roughness.

### Milestone 3: Add Domain Warping

Deliverables:

- Secondary noise layer.
- Vector warping math.
- Warp Amount and Warp Scale controls.
- Warped Vector output.

Success criteria:

- Changing Warp Amount visibly changes the texture pattern.
- Changing Time morphs the noise.

### Milestone 4: Add Shaping Controls

Deliverables:

- Contrast.
- Threshold.
- Invert.
- Output Min/Max.
- Mask and Height outputs.

Success criteria:

- User can create both soft and hard masks from the same group.

### Milestone 5: Demo Material Creation

Deliverables:

- Operator to create material.
- Auto-wired ColorRamp.
- Auto-wired Bump.
- Auto-wired Principled BSDF.

Success criteria:

- Selected object immediately displays a useful procedural material.

### Milestone 6: Preset System

Deliverables:

- JSON preset file.
- Preset dropdown.
- Apply preset operator.
- Initial 10 presets.

Success criteria:

- User can choose a preset and generate a usable node group/material.

### Milestone 7: Animation Helper

Deliverables:

- Time keyframe helper.
- Optional driver helper.

Success criteria:

- User can click one button and see animated noise over timeline playback.

## 25. Nice-to-Have Features

- Geometry Nodes support.
- Compositor node support.
- Mini preview thumbnails for presets.
- Export/import preset library.
- Favorite presets.
- Randomize button.
- Mutate button for controlled random changes.
- Lock controls while randomizing.
- Batch apply to selected objects.
- Audio-reactive parameter mapping through drivers or baked values.
- “Explain this preset” panel.
- Node cleanup/organization button.
- Convert selected native nodes into an INL preset.
- Formula-to-node prototype.
- OSL export for Cycles-only advanced users.

## 26. Randomization / Mutation Feature

This is a very valuable future feature.

Button:

Mutate Noise

Behavior:

- Randomly changes selected inputs within safe artistic ranges.
- Keeps the same node group.
- Does not destroy user wiring.
- Optional intensity slider.

Mutation controls:

- Mutation Amount
- Lock Scale
- Lock Time
- Lock Color
- Lock Threshold
- Lock Warp
- Lock Animation

This would make the add-on feel much more like a creative generator.

## 27. Future “Formula Text” Feature

The user originally asked about typing formulas/noise functions.

This should be treated as a later feature called:

Formula Builder

Important design:

The formula builder should not execute arbitrary code. It should parse a safe mini-language and generate node trees.

Example formulas:

noise(vector, time)

noise(vector * scale, time + morph)

sin(noise(vector, time) * amount)

smoothstep(low, high, noise(vector, time))

mix(noiseA, noiseB, morph)

This would turn the add-on into a no-code procedural shader builder.

## 28. Technical Risks

### Risk: Blender Python API changes

Mitigation:

- Target Blender 5.1 first.
- Keep node creation code modular.
- Avoid relying on obscure internal behavior.

### Risk: Complex node trees become unreadable

Mitigation:

- Use frame nodes.
- Use clear labels.
- Keep groups organized by stages.
- Prefix internal nodes clearly.

### Risk: Too many exposed inputs overwhelm users

Mitigation:

- Provide simple presets.
- Group controls visually in panel.
- Create Lite and Advanced node group variants.

### Risk: Driver setup is brittle

Mitigation:

- Use simple keyframes for MVP.
- Add advanced drivers later.

### Risk: Formula parsing becomes too big

Mitigation:

- Do not include it in MVP.
- Start with preset generation.

## 29. Recommended Version Strategy

### Version 0.1

Core add-on, one or two generated node groups, no presets.

### Version 0.2

Demo material creation, better controls, domain warping.

### Version 0.3

Preset library and mutation/randomization.

### Version 0.4

Animation helpers and improved UI.

### Version 0.5

Geometry Nodes support.

### Version 1.0

Polished release with documentation, examples, stable preset system, and compatibility testing.

### Version 2.0

Formula Builder.

## 30. Documentation Requirements

Documentation should include:

- What 4D noise means.
- Why Time/W creates morphing motion.
- Difference between scrolling and morphing.
- What domain warping is.
- How to use Fac, Mask, Height, Color, and Warped Vector outputs.
- How to animate Time.
- How to create a material.
- How to save presets.
- Examples for:
  - Clouds
  - Marble
  - Grunge
  - Animated masks
  - Displacement
  - Emission effects
  - Video/VFX textures

## 31. Example Artist Recipes

### Animated Smoke

Use:

- Scale: low to medium
- Detail: high
- Warp Amount: medium
- Warp Speed: slow
- Contrast: low
- Threshold: low
- Animate Time slowly

Connect:

- Fac to ColorRamp
- ColorRamp to Alpha or Volume Density

### Liquid Marble

Use:

- Scale: medium
- Distortion: high
- Warp Amount: high
- Warp Scale: low
- Contrast: medium
- Morph: animated slowly

Connect:

- Fac to ColorRamp
- Height to Bump

### Ceramic Speckle

Use:

- Scale: high
- Detail: medium
- Threshold: high
- Contrast: high
- Warp Amount: low

Connect:

- Mask to Base Color mix
- Height to Bump at low strength

### Energy Field

Use:

- Scale: medium
- Detail: high
- Pulse Amount: high
- Warp Speed: medium
- Threshold: medium-high

Connect:

- Edge Mask or Mask to Emission Strength

## 32. Success Metrics

The add-on is successful if:

- A user can create a complex procedural noise material in under 30 seconds.
- The generated node group is editable and understandable.
- Time animation creates morphing, not just scrolling.
- Presets provide visibly different results.
- Users can use outputs for color, bump, roughness, emission, displacement, and masks.
- No arbitrary code execution is required.
- The add-on feels creative rather than technical.

## 33. Final Product Vision

Infinite Noise Lab should become a procedural texture instrument for Blender.

Instead of thinking:

“I need to manually wire ten nodes to get interesting noise.”

The user thinks:

“I’ll add an Infinite Noise node, pick a vibe, animate Time, and sculpt the result.”

The add-on should make procedural noise feel like sound design: layered, animated, morphable, and expressive.