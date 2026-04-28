"""Validation and cleanup utilities (PRD §37)."""

import bpy
from .metadata import PROP_RECIPE_ID


def validate_group(group, required_inputs=None, required_outputs=None):
    """Return list of error strings.  Empty list == valid."""
    errors = []
    if group is None:
        return ["Node group is None."]
    if not group.nodes:
        errors.append("Node group has no internal nodes.")
    input_names = {s.name for s in group.interface.items_tree
                   if getattr(s, 'in_out', None) == 'INPUT'}
    output_names = {s.name for s in group.interface.items_tree
                    if getattr(s, 'in_out', None) == 'OUTPUT'}
    for name in (required_inputs or []):
        if name not in input_names:
            errors.append(f"Missing required input: {name}")
    for name in (required_outputs or []):
        if name not in output_names:
            errors.append(f"Missing required output: {name}")
    return errors


def cleanup_unused_inl_groups():
    """Remove node groups with the INL_ prefix that have zero users."""
    removed = []
    for ng in list(bpy.data.node_groups):
        if ng.name.startswith("INL_") and ng.users == 0:
            removed.append(ng.name)
            bpy.data.node_groups.remove(ng)
    return removed
