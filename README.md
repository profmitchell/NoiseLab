
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
| **Liquid Marble Noise** | Dedicated warped-wave recipe for swirling marble and liquid-metal looks. |
| **Custom 4D Noise** | Legacy 4D Noise + Voronoi morphing group. |
| **Formula Builder** | Chain safe math/noise operations into custom node groups. |
| **Preset Browser** | 20+ built-in and pack-based presets with search, filters, favorites, user presets, and Geometry Nodes looks. |
| **Save / Load Presets** | Export the active node's settings as JSON; reload any time. |
| **Demo Material / Geometry Setup** | One-click shader material, generated-grid Geometry Nodes setup, or active-mesh displacement setup. |
| **Animate Time** | Insert keyframes or a frame-based driver on the Time input. |
| **Randomize / Mutate** | Full randomization with category lock toggles (Scale, Time, Warp, Output, Animation). |
| **Validate & Cleanup** | Check recipe metadata, socket types, internal output links, and unused INL groups. |

## Install

1. **Zip method** — run `python scripts/package_addon.py` from the repository
   root. The generated archive's top entry is `procedural_noise_lab/__init__.py`.
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
| **Create** | Build and insert node groups. Duplicate policy (Reuse / Rebuild Safe / New Copy). |
| **Demo Material** | Generate a complete material or Geometry Nodes modifier on the active object. Geometry demos can use a generated grid or the active mesh. |
| **Presets** | Search and filter a scrollable preset browser. Apply, Create + Apply, favorite, delete user presets, and save your own JSON presets. |
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

Motion, seed, drift, warp amount/speed, twist, stretch, distortion, and output
remap controls are intentionally open-ended where Blender supports it, so they
can be driven, keyframed, or pushed beyond the browser's randomization ranges.
Factor-style controls such as roughness, thresholds, inversion, and mix amounts
remain bounded.

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

### INL_Liquid_Marble_Noise

**Inputs:** Vector, Time, Scale, Warp Amount, Warp Scale, Wave Scale,
Wave Distortion, Detail, Roughness.

**Outputs:** Fac, Color.

## Development

- Recipe metadata lives in `recipe_registry.py`; use it when adding a new
  built-in recipe so operators, menus, demo targets, validation, and tests stay
  aligned.
- Geometry Nodes demos keep the generated grid workflow by default. Use the
  Active Mesh source when you want to displace the object's incoming geometry.
  Both modes store the chosen scalar output as a point float attribute named
  `inl_mask` by default.
- `REBUILD` is intentionally safe: if an existing node group already has users,
  the add-on creates a suffixed copy instead of mutating every material or
  modifier that references the original datablock.
- Generated local artifacts are ignored by Git: `.DS_Store`, `__pycache__/`,
  Python bytecode, and `procedural_noise_lab.zip`.
- Presets come from three sources: Python built-ins, JSON packs in
  `procedural_noise_lab/preset_packs/`, and user presets saved to Blender's
  user config directory. JSON packs use a top-level `presets` array with
  `name`, `category`, `target`, `tags`, `description`, optional
  `animation_hint`, and `values`.
- Run `python -m compileall procedural_noise_lab scripts tests` for a local
  syntax check.
- Run `blender --background --python tests/smoke.py` for Blender-side recipe,
  validation, and demo-material smoke tests.

## Project Layout

```
procedural_noise_lab/
  __init__.py              # bl_info + register / unregister
  interface_utils.py       # Blender 4.x node-tree interface helpers
  metadata.py              # Recipe-ID / version stamping on node groups
  node_layout.py           # Stage frames and node positioning
  recipe_registry.py       # Built-in recipe registry and metadata
  custom_4d_noise.py       # Legacy Custom 4D Noise builder
  formula_builder.py       # Operation-chain → node-group compiler
  recipe_infinite_4d.py    # Infinite 4D Noise recipe
  recipe_domain_warp.py    # Domain Warped Noise recipe
  recipe_animated_mask.py  # Animated Mask Noise recipe
  demo_material.py         # Demo material generator
  presets_data.py          # Built-in preset library
  preset_library.py        # Preset browser aggregation, filters, favorites
  preset_packs/            # JSON preset packs loaded into the browser
  presets_io.py            # JSON save / load for user presets
  animation.py             # Keyframe / driver helpers for Time
  randomize.py             # Randomize / mutate with lock groups
  validation.py            # Group validation + cleanup
  properties.py            # PropertyGroups for UI state
  operators.py             # All operators
  ui.py                    # Shader Editor N-panel (7 collapsible panels)
scripts/
  package_addon.py         # Rebuild procedural_noise_lab.zip
tests/
  smoke.py                 # Blender background smoke tests
```

## Compatibility

- **Blender 4.0 – 5.1+** (uses `node_tree.interface` API introduced in 4.0).
- Shader node groups are the primary supported target and are fully portable
  across `.blend` files via Append / Link.
- Geometry Nodes insertion is supported for all built-in noise recipes. The
  one-click Geometry setup can create a generated grid or displace active mesh
  geometry, and stores a reusable point attribute for material workflows.

## License

MIT — see `LICENSE` for details.
