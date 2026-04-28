
# Procedural Noise Lab (Infinite Noise Lab)

A Blender add-on (4.0 – 5.1+) that generates reusable procedural-noise
**node groups** from pure native Blender shader nodes.  No `eval`, no custom
shading languages — just safe, recipe-driven node trees you can edit, save in
your `.blend`, append across files, or hand-tune further.

## Highlights

| Feature | Description |
|---------|-------------|
| **Infinite 4D Noise** | Flagship node group with Twist, domain warp, fine-detail layer, pulse, contrast/invert, and full output shaping. |
| **Domain Warped Noise** | Focused warp-driven noise with a Warp Field vector output. |
| **Animated Mask Noise** | Evolving procedural masks with Soft, Hard, and Edge outputs. |
| **Custom 4D Noise** | Legacy 4D Noise + Voronoi morphing group. |
| **Formula Builder** | Chain safe math/noise operations into custom node groups. |
| **Preset Library** | 15+ built-in presets in 5 categories (Organic, Abstract, Surface, Motion, Displacement). |
| **Save / Load Presets** | Export the active node's settings as JSON; reload any time. |
| **Demo Material** | One-click material wired to any INL group on the active object. |
| **Animate Time** | Insert keyframes or a frame-based driver on the Time input. |
| **Randomize / Mutate** | Full randomization with category lock toggles (Scale, Time, Warp, Output, Animation). |
| **Validate & Cleanup** | Check a group for missing sockets; remove unused INL groups. |

## Install

1. **Zip method** — zip the `procedural_noise_lab/` folder so the archive's
   top entry is `procedural_noise_lab/__init__.py`.
   In Blender: *Edit ▸ Preferences ▸ Add-ons ▸ Install…* → select the zip →
   enable **Procedural Noise Lab**.

2. **Manual method** — copy `procedural_noise_lab/` into Blender's
   `scripts/addons/` directory and enable from Preferences.

## Quick Start

1. Open the **Shader Editor**, press **N** to open the sidebar, and click
   the **Noise Lab** tab.
2. In the **Create** panel, click **Add Infinite 4D Noise** (or any other
   group).  The node group is built and inserted into the active material.
3. Use the **Presets** panel to browse categories and apply a look.
4. In the **Animation** panel choose Keyframes or Driver and click
   **Animate Time**.
5. Use **Randomize / Mutate** to explore variations.  Toggle locks to
   protect categories you like.

## Panel Overview

| Panel | What it does |
|-------|-------------|
| **Create** | Build and insert node groups. Duplicate policy (Reuse / Rebuild / New Copy). |
| **Demo Material** | Generate a complete material on the active object. |
| **Presets** | Pick category → preset → Apply.  Save your own as JSON. |
| **Animation** | Keyframe or driver on Time.  Set frame range or speed. |
| **Randomize / Mutate** | Randomize or nudge inputs with lock toggles. |
| **Utilities** | Validate active group; clean unused INL groups. |
| **Formula Builder** | Classic operation-chain compiler (advanced). |

## Node Group Inputs / Outputs

### INL_Infinite_4D_Noise

**Inputs:** Vector, Time, Seed, Scale, Detail, Roughness, Lacunarity,
Distortion, Warp Amount, Warp Scale, Warp Speed, Morph, Drift X/Y/Z,
Stretch X/Y/Z, Twist Amount, Pulse Amount, Fine Detail Amount/Scale,
Contrast, Threshold, Invert, Output Min, Output Max.

**Outputs:** Fac, Mask, Height, Color, Warped Vector.

### INL_Domain_Warped_Noise

**Inputs:** Vector, Time, Seed, Base Scale, Base Detail, Roughness,
Lacunarity, Distortion, Warp Scale, Warp Detail, Warp Amount,
Warp Time Offset, Contrast, Threshold, Invert.

**Outputs:** Fac, Mask, Height, Warp Field.

### INL_Animated_Mask_Noise

**Inputs:** Vector, Time, Seed, Scale, Speed, Morph, Detail, Roughness,
Threshold, Softness, Contrast, Edge Width, Invert.

**Outputs:** Soft Mask, Hard Mask, Edge Mask, Height.

## Project Layout

```
procedural_noise_lab/
  __init__.py              # bl_info + register / unregister
  interface_utils.py       # Blender 4.x node-tree interface helpers
  metadata.py              # Recipe-ID / version stamping on node groups
  node_layout.py           # Stage frames and node positioning
  custom_4d_noise.py       # Legacy Custom 4D Noise builder
  formula_builder.py       # Operation-chain → node-group compiler
  recipe_infinite_4d.py    # Infinite 4D Noise recipe
  recipe_domain_warp.py    # Domain Warped Noise recipe
  recipe_animated_mask.py  # Animated Mask Noise recipe
  demo_material.py         # Demo material generator
  presets_data.py          # Built-in preset library
  presets_io.py            # JSON save / load for user presets
  animation.py             # Keyframe / driver helpers for Time
  randomize.py             # Randomize / mutate with lock groups
  validation.py            # Group validation + cleanup
  properties.py            # PropertyGroups for UI state
  operators.py             # All operators
  ui.py                    # Shader Editor N-panel (7 collapsible panels)
```

## Compatibility

- **Blender 4.0 – 5.1+** (uses `node_tree.interface` API introduced in 4.0).
- All node groups are standard `ShaderNodeTree` groups — fully portable
  across `.blend` files via Append / Link.

## License

MIT — see `LICENSE` for details.
