"""Shader Editor N-panel for Infinite Noise Lab / Procedural Noise Lab.

Organised into sub-panels so each section is collapsible and the sidebar
stays tidy even with all features enabled.
"""

import bpy
from bpy.types import Panel, UIList


# =========================================================================
# Shared base
# =========================================================================
class _PNL_PanelBase:
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Noise Lab"

    @classmethod
    def poll(cls, context):
        return context.space_data and context.space_data.type == 'NODE_EDITOR'


# =========================================================================
# UIList for the formula builder
# =========================================================================
class PNL_UL_operations(UIList):
    bl_idname = "PNL_UL_operations"

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=f"{index+1}.")
        row.prop(item, "op", text="")
        row.prop(item, "param1", text="P1")
        row.prop(item, "param2", text="P2")


class PNL_UL_preset_browser(UIList):
    bl_idname = "PNL_UL_preset_browser"

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        row = layout.row(align=True)
        fav_icon = 'SOLO_ON' if item.favorite else 'SOLO_OFF'
        row.label(text="", icon=fav_icon)
        col = row.column(align=True)
        col.label(text=item.name)
        sub = col.row(align=True)
        sub.scale_y = 0.65
        sub.label(text=f"{item.category} · {item.source}")


# =========================================================================
# 1  Create
# =========================================================================
class PNL_PT_create(_PNL_PanelBase, Panel):
    bl_label = "Create"
    bl_idname = "PNL_PT_create"

    def draw(self, context):
        layout = self.layout
        s = context.scene.pnl_settings
        from .recipe_registry import RECIPES

        operator_ids = {
            "INFINITE_4D": "pnl.build_infinite_4d",
            "DOMAIN_WARP": "pnl.build_domain_warp",
            "ANIMATED_MASK": "pnl.build_animated_mask",
            "LIQUID_MARBLE": "pnl.build_liquid_marble",
        }
        for recipe in RECIPES:
            layout.operator(operator_ids[recipe.key], text=f"Add {recipe.display_name}", icon=recipe.icon)
        layout.separator()
        layout.operator("pnl.build_custom_4d", icon='TEXTURE')
        layout.separator()
        layout.prop(s, "duplicate_policy", text="If exists")


# =========================================================================
# 2  Demo Setup
# =========================================================================
class PNL_PT_demo(_PNL_PanelBase, Panel):
    bl_label = "Demo Setup"
    bl_idname = "PNL_PT_demo"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        s = context.scene.pnl_settings
        is_geo = context.space_data.tree_type == 'GeometryNodeTree'
        
        layout.prop(s, "demo_target", text="")
        
        op_text = "Create Demo Setup" if is_geo else "Create Demo Material"
        op_icon = 'MODIFIER' if is_geo else 'MATERIAL'

        if is_geo:
            layout.prop(s, "geo_demo_mode", text="Source")
            if s.geo_demo_mode == 'GRID':
                row = layout.row(align=True)
                row.prop(s, "geo_grid_size")
                row.prop(s, "geo_grid_vertices", text="Vertices")
            layout.prop(s, "geo_displacement_strength", slider=True)

        layout.operator("pnl.demo_material", text=op_text, icon=op_icon)


# =========================================================================
# 3  Presets
# =========================================================================
class PNL_PT_presets(_PNL_PanelBase, Panel):
    bl_label = "Presets"
    bl_idname = "PNL_PT_presets"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        s = context.scene.pnl_settings

        row = layout.row(align=True)
        row.prop(s, "preset_search", text="", icon='VIEWZOOM')
        row.operator("pnl.refresh_presets", text="", icon='FILE_REFRESH')

        row = layout.row(align=True)
        row.prop(s, "preset_browser_category", text="")
        row.prop(s, "preset_browser_recipe", text="")
        row = layout.row(align=True)
        row.prop(s, "preset_source", text="")
        row.prop(s, "preset_favorites_only", toggle=True, icon='SOLO_ON')
        layout.prop(s, "preset_tag_filter", text="Tag")

        if not s.preset_browser_items:
            layout.operator("pnl.refresh_presets", text="Load Presets", icon='FILE_REFRESH')
            return

        row = layout.row()
        row.template_list(
            "PNL_UL_preset_browser", "",
            s, "preset_browser_items",
            s, "preset_browser_index",
            rows=7,
        )
        col = row.column(align=True)
        col.operator("pnl.toggle_preset_favorite", icon='SOLO_ON', text="")
        col.operator("pnl.delete_user_preset", icon='TRASH', text="")

        item = None
        if 0 <= s.preset_browser_index < len(s.preset_browser_items):
            item = s.preset_browser_items[s.preset_browser_index]
        if item:
            box = layout.box()
            box.scale_y = 0.75
            box.label(text=item.name, icon='PRESET')
            box.label(text=item.target)
            if item.description:
                box.label(text=item.description, icon='INFO')
            if item.animation_hint:
                box.label(text=item.animation_hint, icon='TIME')
            if item.tags:
                box.label(text=item.tags, icon='BOOKMARKS')

        row = layout.row(align=True)
        row.operator("pnl.apply_preset", icon='CHECKMARK')
        row.operator("pnl.create_apply_preset", icon='ADD')
        row.operator("pnl.save_preset", icon='FILE_TICK')


# =========================================================================
# 4  Animation
# =========================================================================
class PNL_PT_animation(_PNL_PanelBase, Panel):
    bl_label = "Animation"
    bl_idname = "PNL_PT_animation"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        s = context.scene.pnl_settings

        layout.prop(s, "anim_mode", expand=True)

        if s.anim_mode == 'KEYFRAMES':
            row = layout.row(align=True)
            row.prop(s, "anim_start_frame")
            row.prop(s, "anim_end_frame")
        else:
            layout.prop(s, "anim_speed")

        row = layout.row(align=True)
        row.operator("pnl.animate_time", icon='PLAY')
        row.operator("pnl.clear_time", icon='CANCEL', text="Clear")


# =========================================================================
# 5  Randomise / Mutate
# =========================================================================
class PNL_PT_randomize(_PNL_PanelBase, Panel):
    bl_label = "Randomize / Mutate"
    bl_idname = "PNL_PT_randomize"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        s = context.scene.pnl_settings

        layout.prop(s, "mutate_amount", slider=True)

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(s, "lock_scale", toggle=True)
        row.prop(s, "lock_time", toggle=True)
        row = col.row(align=True)
        row.prop(s, "lock_warp", toggle=True)
        row.prop(s, "lock_output", toggle=True)
        row = col.row(align=True)
        row.prop(s, "lock_animation", toggle=True)

        row = layout.row(align=True)
        row.operator("pnl.randomize", text="Randomize", icon='FILE_REFRESH').mutate = False
        row.operator("pnl.randomize", text="Mutate", icon='RNA').mutate = True


# =========================================================================
# 6  Utilities
# =========================================================================
class PNL_PT_utilities(_PNL_PanelBase, Panel):
    bl_label = "Utilities"
    bl_idname = "PNL_PT_utilities"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator("pnl.validate", icon='CHECKMARK')
        layout.operator("pnl.cleanup", icon='TRASH')
        row = layout.row(align=True)
        row.operator("pnl.duplicate_group", icon='DUPLICATE', text="Duplicate")
        row.operator("pnl.rename_group", icon='GREASEPENCIL', text="Rename")
        layout.separator()
        layout.operator("pnl.open_docs", icon='URL')


# =========================================================================
# 7  Formula Builder (collapsed by default)
# =========================================================================
class PNL_PT_formula(_PNL_PanelBase, Panel):
    bl_label = "Formula Builder"
    bl_idname = "PNL_PT_formula"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        s = context.scene.pnl_settings

        layout.prop(s, "group_name")

        row = layout.row()
        row.template_list(
            "PNL_UL_operations", "",
            s, "operations",
            s, "active_index",
            rows=4,
        )
        col = row.column(align=True)
        col.operator("pnl.op_add", icon='ADD', text="")
        col.operator("pnl.op_remove", icon='REMOVE', text="").index = -1
        col.separator()
        up = col.operator("pnl.op_move", icon='TRIA_UP', text="")
        up.direction = 'UP'; up.index = -1
        dn = col.operator("pnl.op_move", icon='TRIA_DOWN', text="")
        dn.direction = 'DOWN'; dn.index = -1
        col.separator()
        col.operator("pnl.op_clear", icon='TRASH', text="")

        layout.operator("pnl.build_formula", icon='NODETREE')


# =========================================================================
# Registration
# =========================================================================
_classes = (
    PNL_UL_preset_browser,
    PNL_UL_operations,
    PNL_PT_create,
    PNL_PT_demo,
    PNL_PT_presets,
    PNL_PT_animation,
    PNL_PT_randomize,
    PNL_PT_utilities,
    PNL_PT_formula,
)


def register():
    for c in _classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(_classes):
        bpy.utils.unregister_class(c)
