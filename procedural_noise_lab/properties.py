import bpy
from bpy.props import (
    StringProperty, FloatProperty, EnumProperty,
    CollectionProperty, IntProperty, BoolProperty,
)
from bpy.types import PropertyGroup

from .formula_builder import OP_TYPES
from .presets_data import PRESET_CATEGORIES, PRESETS, preset_names_for_category


# ---------------------------------------------------------------------------
# Dynamic enum callbacks for presets
# ---------------------------------------------------------------------------
def _preset_category_items(self, context):
    return [(cid, label, "") for cid, label in PRESET_CATEGORIES]


def _preset_name_items(self, context):
    s = context.scene.pnl_settings
    return preset_names_for_category(s.preset_category) or [("NONE", "(none)", "")]


# ---------------------------------------------------------------------------
# Formula builder operation item
# ---------------------------------------------------------------------------
class PNL_OperationItem(PropertyGroup):
    op: EnumProperty(
        name="Operation",
        items=[(k, label, desc) for k, label, desc in OP_TYPES],
        default='NOISE',
    )
    param1: FloatProperty(name="Param 1", default=0.0)
    param2: FloatProperty(name="Param 2", default=1.0)


# ---------------------------------------------------------------------------
# Main settings
# ---------------------------------------------------------------------------
class PNL_Settings(PropertyGroup):
    # Duplicate policy
    duplicate_policy: EnumProperty(
        name="Duplicate Policy",
        items=[
            ('REUSE',   "Reuse",   "Reuse existing group if it already exists"),
            ('REBUILD', "Rebuild", "Wipe and rebuild the group in place"),
            ('SUFFIX',  "New Copy","Always create a new copy (.001 etc)"),
        ],
        default='REUSE',
        description="What to do when the node group already exists",
    )

    # Demo material target
    demo_target: EnumProperty(
        name="Target Group",
        items=[
            ('INL_Infinite_4D_Noise',   "Infinite 4D Noise",   ""),
            ('INL_Domain_Warped_Noise', "Domain Warped Noise", ""),
            ('INL_Animated_Mask_Noise', "Animated Mask Noise", ""),
        ],
        default='INL_Infinite_4D_Noise',
    )

    # Preset system
    preset_category: EnumProperty(
        name="Category",
        items=_preset_category_items,
    )
    preset_name: EnumProperty(
        name="Preset",
        items=_preset_name_items,
    )

    # Animation
    anim_mode: EnumProperty(
        name="Mode",
        items=[
            ('KEYFRAMES', "Keyframes", "Insert start/end keyframes on Time"),
            ('DRIVER',    "Driver",    "Add a frame-based driver on Time"),
        ],
        default='KEYFRAMES',
    )
    anim_start_frame: IntProperty(name="Start", default=1, min=0)
    anim_end_frame: IntProperty(name="End", default=120, min=1)
    anim_speed: FloatProperty(name="Speed", default=1.0, min=0.01, max=100.0)

    # Randomise / mutate
    mutate_amount: FloatProperty(name="Mutation %", default=0.2, min=0.01, max=1.0,
                                 subtype='FACTOR')
    lock_scale: BoolProperty(name="Lock Scale", default=False)
    lock_time: BoolProperty(name="Lock Time", default=False)
    lock_warp: BoolProperty(name="Lock Warp", default=False)
    lock_output: BoolProperty(name="Lock Output", default=False)
    lock_animation: BoolProperty(name="Lock Animation", default=False)

    # Formula builder
    group_name: StringProperty(
        name="Group Name",
        default="My Procedural Noise",
        description="Name of the node group that will be (re)built",
    )
    operations: CollectionProperty(type=PNL_OperationItem)
    active_index: IntProperty(default=0)

    # Advanced sections visibility
    show_formula: BoolProperty(name="Show Formula Builder", default=False)
    show_advanced: BoolProperty(name="Show Advanced", default=False)


_classes = (PNL_OperationItem, PNL_Settings)


def register():
    for c in _classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(_classes):
        bpy.utils.unregister_class(c)
