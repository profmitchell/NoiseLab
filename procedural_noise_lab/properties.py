import bpy
from bpy.props import (
    StringProperty, FloatProperty, EnumProperty,
    CollectionProperty, IntProperty, BoolProperty,
)
from bpy.types import PropertyGroup

from .formula_builder import OP_TYPES
from .presets_data import PRESET_CATEGORIES, PRESETS, preset_names_for_category
from .recipe_registry import DEMO_TARGET_ITEMS, recipe_for_group


# ---------------------------------------------------------------------------
# Dynamic enum callbacks for presets
# ---------------------------------------------------------------------------
def _preset_category_items(self, context):
    return [(cid, label, "") for cid, label in PRESET_CATEGORIES]


def _preset_name_items(self, context):
    s = context.scene.pnl_settings
    target = None
    space = getattr(context, "space_data", None)
    if space and space.type == 'NODE_EDITOR' and space.edit_tree:
        active = space.edit_tree.nodes.active
        if active and active.type == 'GROUP':
            recipe = recipe_for_group(active.node_tree)
            if recipe:
                target = recipe.internal_name
    return preset_names_for_category(s.preset_category, target) or [("NONE", "(none)", "")]


# ---------------------------------------------------------------------------
# Formula builder operation item
# ---------------------------------------------------------------------------
class PNL_OperationItem(PropertyGroup):
    op: EnumProperty(
        name="Operation",
        items=[(k, label, desc) for k, label, desc in OP_TYPES],
        default='NOISE',
        description="Mathematical or noise operation to apply"
    )
    param1: FloatProperty(name="Param 1", default=0.0, description="First parameter for the operation (often Scale or Input A)")
    param2: FloatProperty(name="Param 2", default=1.0, description="Second parameter for the operation (often Detail or Input B)")


# ---------------------------------------------------------------------------
# Main settings
# ---------------------------------------------------------------------------
class PNL_Settings(PropertyGroup):
    # Duplicate policy
    duplicate_policy: EnumProperty(
        name="Duplicate Policy",
        items=[
            ('REUSE',   "Reuse",   "Reuse existing group if it already exists"),
            ('REBUILD', "Rebuild Safe", "Rebuild an unused group, or create a new copy if the existing group is in use"),
            ('SUFFIX',  "New Copy","Always create a new copy (.001 etc)"),
        ],
        default='REUSE',
        description="What to do when the node group already exists",
    )

    # Demo material target
    demo_target: EnumProperty(
        name="Target Group",
        items=DEMO_TARGET_ITEMS,
        default='INL_Infinite_4D_Noise',
        description="Target node group to generate a demo material for",
    )
    geo_demo_mode: EnumProperty(
        name="Geometry Source",
        items=[
            ('GRID', "Grid", "Generate a high-resolution demo grid"),
            ('ACTIVE', "Active Mesh", "Use and displace the active object's incoming geometry"),
        ],
        default='GRID',
        description="Geometry source for one-click Geometry Nodes demo setups",
    )
    geo_grid_size: FloatProperty(
        name="Grid Size",
        default=2.0,
        min=0.1,
        max=100.0,
        description="Generated grid size for Geometry Nodes demos",
    )
    geo_grid_vertices: IntProperty(
        name="Grid Vertices",
        default=100,
        min=2,
        max=1000,
        description="Vertex count per axis for generated Geometry Nodes demo grids",
    )
    geo_displacement_strength: FloatProperty(
        name="Strength",
        default=0.12,
        min=-10.0,
        max=10.0,
        description="Default normal displacement strength for Geometry Nodes demos",
    )

    # Preset system
    preset_category: EnumProperty(
        name="Category",
        items=_preset_category_items,
        description="Category of noise presets",
    )
    preset_name: EnumProperty(
        name="Preset",
        items=_preset_name_items,
        description="Specific noise preset to load",
    )

    # Animation
    anim_mode: EnumProperty(
        name="Mode",
        items=[
            ('KEYFRAMES', "Keyframes", "Insert start/end keyframes on Time"),
            ('DRIVER',    "Driver",    "Add a frame-based driver on Time"),
        ],
        default='KEYFRAMES',
        description="Method of animation: Keyframes on the timeline or a continuous Driver",
    )
    anim_start_frame: IntProperty(name="Start", default=1, min=0, description="Frame at which animation begins")
    anim_end_frame: IntProperty(name="End", default=120, min=1, description="Frame at which animation ends (keyframe mode only)")
    anim_speed: FloatProperty(name="Speed", default=1.0, min=0.01, max=100.0, description="Multiplier for the animation speed over time")

    # Randomise / mutate
    mutate_amount: FloatProperty(name="Mutation %", default=0.2, min=0.01, max=1.0,
                                 subtype='FACTOR', description="Percentage of mutation to apply when randomizing parameters")
    lock_scale: BoolProperty(name="Lock Scale", default=False, description="Prevent scale values from being randomized")
    lock_time: BoolProperty(name="Lock Time", default=False, description="Prevent time values from being randomized")
    lock_warp: BoolProperty(name="Lock Warp", default=False, description="Prevent warp values from being randomized")
    lock_output: BoolProperty(name="Lock Output", default=False, description="Prevent output values from being randomized")
    lock_animation: BoolProperty(name="Lock Animation", default=False, description="Prevent animation values from being randomized")

    # Formula builder
    group_name: StringProperty(
        name="Group Name",
        default="My Procedural Noise",
        description="Name of the node group that will be (re)built",
    )
    operations: CollectionProperty(type=PNL_OperationItem, description="List of operations defining the custom procedural noise")
    active_index: IntProperty(default=0, description="Currently selected operation index")

    # Advanced sections visibility
    show_formula: BoolProperty(name="Show Formula Builder", default=False, description="Toggle visibility of the Custom Formula Builder")
    show_advanced: BoolProperty(name="Show Advanced", default=False, description="Toggle visibility of advanced settings")


_classes = (PNL_OperationItem, PNL_Settings)


def register():
    for c in _classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(_classes):
        bpy.utils.unregister_class(c)
