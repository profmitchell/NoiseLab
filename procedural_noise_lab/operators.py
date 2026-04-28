"""Operators for Procedural Noise Lab (Infinite Noise Lab)."""

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty
from bpy.types import Operator

from .custom_4d_noise import build_custom_4d_noise, GROUP_NAME as CUSTOM_4D_NAME
from .formula_builder import build_formula_group
from . import recipe_infinite_4d
from . import recipe_domain_warp
from . import recipe_animated_mask
from .demo_material import create_demo_material
from .presets_data import PRESETS, flat_presets
from .presets_io import save_preset as _save_preset_json, load_user_presets
from .animation import (
    animate_time_keyframes, clear_time_animation, add_time_driver,
)
from .randomize import randomize_inputs
from .validation import validate_group, cleanup_unused_inl_groups


# =========================================================================
# Helpers
# =========================================================================
def _insert_group_into_active_editor(context, group):
    space = context.space_data
    if not space or space.type != 'NODE_EDITOR':
        return None
    tree = space.edit_tree
    if tree is None or tree.bl_idname != group.bl_idname:
        return None
    node_type = "ShaderNodeGroup" if tree.bl_idname == 'ShaderNodeTree' else "GeometryNodeGroup"
    node = tree.nodes.new(node_type)
    node.node_tree = group
    node.location = (0.0, 0.0)
    for n in tree.nodes:
        n.select = False
    node.select = True
    tree.nodes.active = node
    return node

def _get_tree_type(context):
    space = context.space_data
    if space and space.type == 'NODE_EDITOR' and space.tree_type == 'GeometryNodeTree':
        return 'GeometryNodeTree'
    return 'ShaderNodeTree'


def _active_group_node(context):
    """Return the active node if it is a ShaderNodeGroup (or None)."""
    space = context.space_data
    if not space or space.type != 'NODE_EDITOR':
        return None
    tree = space.edit_tree
    if tree is None:
        return None
    active = tree.nodes.active
    if active and active.type == 'GROUP':
        return active
    return None


def _policy(context):
    return context.scene.pnl_settings.duplicate_policy


# =========================================================================
# Create node groups
# =========================================================================
class PNL_OT_build_infinite_4d(Operator):
    bl_idname = "pnl.build_infinite_4d"
    bl_label = "Add Infinite 4D Noise"
    bl_description = "Create INL_Infinite_4D_Noise and insert it into the active shader tree"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        group, reused = recipe_infinite_4d.build(policy=_policy(context), tree_type=_get_tree_type(context))
        node = _insert_group_into_active_editor(context, group)
        tag = "reused" if reused else "built"
        self.report({'INFO'}, f"{recipe_infinite_4d.DISPLAY_NAME} {tag}.")
        return {'FINISHED'}


class PNL_OT_build_domain_warp(Operator):
    bl_idname = "pnl.build_domain_warp"
    bl_label = "Add Domain Warped Noise"
    bl_description = "Create INL_Domain_Warped_Noise and insert it"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        group, reused = recipe_domain_warp.build(policy=_policy(context), tree_type=_get_tree_type(context))
        _insert_group_into_active_editor(context, group)
        tag = "reused" if reused else "built"
        self.report({'INFO'}, f"{recipe_domain_warp.DISPLAY_NAME} {tag}.")
        return {'FINISHED'}


class PNL_OT_build_animated_mask(Operator):
    bl_idname = "pnl.build_animated_mask"
    bl_label = "Add Animated Mask Noise"
    bl_description = "Create INL_Animated_Mask_Noise and insert it"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        group, reused = recipe_animated_mask.build(policy=_policy(context), tree_type=_get_tree_type(context))
        _insert_group_into_active_editor(context, group)
        tag = "reused" if reused else "built"
        self.report({'INFO'}, f"{recipe_animated_mask.DISPLAY_NAME} {tag}.")
        return {'FINISHED'}


class PNL_OT_build_custom_4d(Operator):
    bl_idname = "pnl.build_custom_4d"
    bl_label = "Add Custom 4D Noise"
    bl_description = "Create the original Custom 4D Noise node group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        group = build_custom_4d_noise(tree_type=_get_tree_type(context))
        _insert_group_into_active_editor(context, group)
        self.report({'INFO'}, f"Built node group '{CUSTOM_4D_NAME}'.")
        return {'FINISHED'}


# =========================================================================
# Demo material
# =========================================================================
class PNL_OT_demo_material(Operator):
    bl_idname = "pnl.demo_material"
    bl_label = "Create Demo Material"
    bl_description = "Build a demo material wired to the selected INL group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        target = context.scene.pnl_settings.demo_target
        # Ensure the group exists first
        if target == "INL_Infinite_4D_Noise":
            recipe_infinite_4d.build(policy='REUSE')
        elif target == "INL_Domain_Warped_Noise":
            recipe_domain_warp.build(policy='REUSE')
        elif target == "INL_Animated_Mask_Noise":
            recipe_animated_mask.build(policy='REUSE')
        mat, msg = create_demo_material(target)
        level = 'INFO' if mat else 'ERROR'
        self.report({level}, msg)
        return {'FINISHED'} if mat else {'CANCELLED'}


# =========================================================================
# Presets – apply / save
# =========================================================================
class PNL_OT_apply_preset(Operator):
    bl_idname = "pnl.apply_preset"
    bl_label = "Apply Preset"
    bl_description = "Set default values on the active group node from a preset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = context.scene.pnl_settings
        cat_presets = PRESETS.get(s.preset_category, [])
        preset = None
        for p in cat_presets:
            if p["name"] == s.preset_name:
                preset = p
                break
        if preset is None:
            self.report({'WARNING'}, "No preset selected.")
            return {'CANCELLED'}

        node = _active_group_node(context)
        if node is None:
            self.report({'WARNING'}, "Select an INL group node first.")
            return {'CANCELLED'}

        applied = 0
        for key, val in preset["values"].items():
            if key in node.inputs:
                try:
                    node.inputs[key].default_value = val
                    applied += 1
                except Exception:
                    pass
        self.report({'INFO'}, f"Applied '{preset['name']}' ({applied} values).")
        return {'FINISHED'}


class PNL_OT_save_preset(Operator):
    bl_idname = "pnl.save_preset"
    bl_label = "Save Current as Preset"
    bl_description = "Save the active group node's current values as a user preset JSON"
    bl_options = {'REGISTER'}

    preset_name: StringProperty(name="Name", default="My Preset")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        node = _active_group_node(context)
        if node is None:
            self.report({'WARNING'}, "Select an INL group node first.")
            return {'CANCELLED'}
        values = {}
        for inp in node.inputs:
            if inp.type == 'VALUE':
                values[inp.name] = inp.default_value
        target = node.node_tree.name if node.node_tree else ""
        path = _save_preset_json(self.preset_name, target, values)
        self.report({'INFO'}, f"Saved preset '{self.preset_name}'.")
        return {'FINISHED'}


# =========================================================================
# Animation helpers
# =========================================================================
class PNL_OT_animate_time(Operator):
    bl_idname = "pnl.animate_time"
    bl_label = "Animate Time"
    bl_description = "Add keyframes or a driver to the Time input of the active group node"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        node = _active_group_node(context)
        if node is None:
            self.report({'WARNING'}, "Select an INL group node first.")
            return {'CANCELLED'}
        s = context.scene.pnl_settings
        if s.anim_mode == 'KEYFRAMES':
            err = animate_time_keyframes(node, s.anim_start_frame, s.anim_end_frame)
        else:
            err = add_time_driver(node, s.anim_speed)
        if err:
            self.report({'ERROR'}, err)
            return {'CANCELLED'}
        self.report({'INFO'}, "Time animation added.")
        return {'FINISHED'}


class PNL_OT_clear_time(Operator):
    bl_idname = "pnl.clear_time"
    bl_label = "Clear Time Animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        node = _active_group_node(context)
        if node is None:
            self.report({'WARNING'}, "Select an INL group node first.")
            return {'CANCELLED'}
        clear_time_animation(node)
        self.report({'INFO'}, "Time animation cleared.")
        return {'FINISHED'}


# =========================================================================
# Randomise / mutate
# =========================================================================
class PNL_OT_randomize(Operator):
    bl_idname = "pnl.randomize"
    bl_label = "Randomize All"
    bl_options = {'REGISTER', 'UNDO'}

    mutate: BoolProperty(default=False)

    def execute(self, context):
        node = _active_group_node(context)
        if node is None:
            self.report({'WARNING'}, "Select an INL group node first.")
            return {'CANCELLED'}
        s = context.scene.pnl_settings
        locks = set()
        if s.lock_scale:     locks.add("SCALE")
        if s.lock_time:      locks.add("TIME")
        if s.lock_warp:      locks.add("WARP")
        if s.lock_output:    locks.add("OUTPUT")
        if s.lock_animation: locks.add("ANIMATION")
        randomize_inputs(node, mutate=self.mutate,
                         mutate_pct=s.mutate_amount, locked_categories=locks)
        label = "Mutated" if self.mutate else "Randomized"
        self.report({'INFO'}, f"{label} group inputs.")
        return {'FINISHED'}


# =========================================================================
# Validation & cleanup
# =========================================================================
class PNL_OT_validate(Operator):
    bl_idname = "pnl.validate"
    bl_label = "Validate Active Group"
    bl_options = {'REGISTER'}

    def execute(self, context):
        node = _active_group_node(context)
        if node is None or node.node_tree is None:
            self.report({'WARNING'}, "Select an INL group node first.")
            return {'CANCELLED'}
        errors = validate_group(node.node_tree)
        if errors:
            for e in errors:
                self.report({'WARNING'}, e)
        else:
            self.report({'INFO'}, "Node group is valid.")
        return {'FINISHED'}


class PNL_OT_cleanup(Operator):
    bl_idname = "pnl.cleanup"
    bl_label = "Clean Unused INL Groups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        removed = cleanup_unused_inl_groups()
        if removed:
            self.report({'INFO'}, f"Removed: {', '.join(removed)}")
        else:
            self.report({'INFO'}, "No unused INL groups found.")
        return {'FINISHED'}


class PNL_OT_duplicate_group(Operator):
    bl_idname = "pnl.duplicate_group"
    bl_label = "Duplicate Selected INL Group"
    bl_description = "Create a copy of the active INL node group (appends .001)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        node = _active_group_node(context)
        if node is None or node.node_tree is None:
            self.report({'WARNING'}, "Select an INL group node first.")
            return {'CANCELLED'}
        original = node.node_tree
        copy = original.copy()
        node.node_tree = copy
        self.report({'INFO'}, f"Duplicated to '{copy.name}'.")
        return {'FINISHED'}


class PNL_OT_open_docs(Operator):
    bl_idname = "pnl.open_docs"
    bl_label = "Open Documentation"
    bl_description = "Open the Procedural Noise Lab README in a web browser"
    bl_options = {'REGISTER'}

    def execute(self, context):
        import webbrowser
        import os
        readme = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
        if os.path.exists(readme):
            webbrowser.open(f"file://{readme}")
            self.report({'INFO'}, "Opened README.")
        else:
            self.report({'WARNING'}, "README.md not found.")
        return {'FINISHED'}


# =========================================================================
# Formula builder (carried forward from v0.1)
# =========================================================================
class PNL_OT_op_add(Operator):
    bl_idname = "pnl.op_add"
    bl_label = "Add Operation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = context.scene.pnl_settings
        item = s.operations.add()
        item.op = 'NOISE'
        s.active_index = len(s.operations) - 1
        return {'FINISHED'}


class PNL_OT_op_remove(Operator):
    bl_idname = "pnl.op_remove"
    bl_label = "Remove Operation"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(default=-1)

    def execute(self, context):
        s = context.scene.pnl_settings
        idx = self.index if self.index >= 0 else s.active_index
        if 0 <= idx < len(s.operations):
            s.operations.remove(idx)
            s.active_index = max(0, min(s.active_index, len(s.operations) - 1))
        return {'FINISHED'}


class PNL_OT_op_move(Operator):
    bl_idname = "pnl.op_move"
    bl_label = "Move Operation"
    bl_options = {'REGISTER', 'UNDO'}

    direction: StringProperty(default='UP')
    index: IntProperty(default=-1)

    def execute(self, context):
        s = context.scene.pnl_settings
        idx = self.index if self.index >= 0 else s.active_index
        if not (0 <= idx < len(s.operations)):
            return {'CANCELLED'}
        new_idx = idx - 1 if self.direction == 'UP' else idx + 1
        if not (0 <= new_idx < len(s.operations)):
            return {'CANCELLED'}
        s.operations.move(idx, new_idx)
        s.active_index = new_idx
        return {'FINISHED'}


class PNL_OT_op_clear(Operator):
    bl_idname = "pnl.op_clear"
    bl_label = "Clear Operations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.pnl_settings.operations.clear()
        return {'FINISHED'}


class PNL_OT_build_formula(Operator):
    bl_idname = "pnl.build_formula"
    bl_label = "Build Formula Group"
    bl_description = "Compile the operation chain into a Blender node group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = context.scene.pnl_settings
        if not s.operations:
            self.report({'ERROR'}, "Add at least one operation first.")
            return {'CANCELLED'}
        ops = [{"op": it.op, "param1": it.param1, "param2": it.param2}
               for it in s.operations]
        name = s.group_name.strip() or "My Procedural Noise"
        group = build_formula_group(name, ops, tree_type=_get_tree_type(context))
        _insert_group_into_active_editor(context, group)
        self.report({'INFO'}, f"Built '{name}' from {len(ops)} operation(s).")
        return {'FINISHED'}


# =========================================================================
# Registration
# =========================================================================
_classes = (
    PNL_OT_build_infinite_4d,
    PNL_OT_build_domain_warp,
    PNL_OT_build_animated_mask,
    PNL_OT_build_custom_4d,
    PNL_OT_demo_material,
    PNL_OT_apply_preset,
    PNL_OT_save_preset,
    PNL_OT_animate_time,
    PNL_OT_clear_time,
    PNL_OT_randomize,
    PNL_OT_validate,
    PNL_OT_cleanup,
    PNL_OT_duplicate_group,
    PNL_OT_open_docs,
    PNL_OT_op_add,
    PNL_OT_op_remove,
    PNL_OT_op_move,
    PNL_OT_op_clear,
    PNL_OT_build_formula,
)


def register():
    for c in _classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(_classes):
        bpy.utils.unregister_class(c)
