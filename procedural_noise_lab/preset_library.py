"""Preset library aggregation, filtering, and user-state helpers."""

import json
import os
import re

import bpy

from .presets_data import PRESET_CATEGORIES, PRESETS
from .presets_io import delete_preset, load_user_presets
from .recipe_registry import RECIPES


PACK_DIR = os.path.join(os.path.dirname(__file__), "preset_packs")
FAVORITES_KEY = "pnl_preset_favorites"

SOURCE_BUILTIN = "BUILTIN"
SOURCE_PACK = "PACK"
SOURCE_USER = "USER"


def _slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def recipe_items():
    return [("ALL", "All Recipes", "")] + [
        (recipe.internal_name, recipe.display_name, recipe.description)
        for recipe in RECIPES
    ]


def category_items():
    return [("ALL", "All Categories", "")] + [
        (category_id, label, "") for category_id, label in PRESET_CATEGORIES
    ]


def _normalize_preset(preset, *, category="UNCATEGORIZED", source=SOURCE_BUILTIN, pack=""):
    name = preset.get("name", "Untitled")
    target = preset.get("target", "")
    preset_id = preset.get("id") or f"{source.lower()}:{pack}:{category}:{target}:{name}"
    tags = preset.get("tags", [])
    if isinstance(tags, str):
        tags = [part.strip() for part in tags.split(",") if part.strip()]
    return {
        "id": _slug(preset_id),
        "name": name,
        "category": preset.get("category", category),
        "target": target,
        "values": dict(preset.get("values", {})),
        "desc": preset.get("desc") or preset.get("description", ""),
        "anim": preset.get("anim") or preset.get("animation_hint", ""),
        "tags": tags,
        "source": source,
        "pack": pack,
        "preview": preset.get("preview", ""),
    }


def _load_pack_presets():
    presets = []
    if not os.path.isdir(PACK_DIR):
        return presets
    for fname in sorted(os.listdir(PACK_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(PACK_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
        except Exception:
            continue
        pack_name = data.get("name") or os.path.splitext(fname)[0]
        for item in data.get("presets", []):
            presets.append(
                _normalize_preset(
                    item,
                    category=item.get("category", "PACK"),
                    source=SOURCE_PACK,
                    pack=pack_name,
                )
            )
    return presets


def all_presets():
    presets = []
    for category_id, items in PRESETS.items():
        for item in items:
            presets.append(_normalize_preset(item, category=category_id, source=SOURCE_BUILTIN))
    for item in _load_pack_presets():
        presets.append(item)
    for item in load_user_presets():
        presets.append(
            _normalize_preset(
                item,
                category=item.get("category", "USER"),
                source=SOURCE_USER,
                pack="User",
            )
        )

    deduped = {}
    for preset in presets:
        deduped[preset["id"]] = preset
    return sorted(deduped.values(), key=lambda p: (p["category"], p["target"], p["name"]))


def favorites():
    favs = bpy.context.window_manager.get(FAVORITES_KEY, [])
    if isinstance(favs, str):
        return {item for item in favs.split("|") if item}
    return set(favs)


def set_favorites(preset_ids):
    bpy.context.window_manager[FAVORITES_KEY] = "|".join(sorted(preset_ids))


def is_favorite(preset_id):
    return preset_id in favorites()


def toggle_favorite(preset_id):
    favs = favorites()
    if preset_id in favs:
        favs.remove(preset_id)
        enabled = False
    else:
        favs.add(preset_id)
        enabled = True
    set_favorites(favs)
    return enabled


def filter_presets(settings, presets=None):
    presets = presets or all_presets()
    query = settings.preset_search.strip().lower()
    tag_query = settings.preset_tag_filter.strip().lower()
    category = settings.preset_browser_category
    target = settings.preset_browser_recipe
    source = settings.preset_source
    favs = favorites()

    result = []
    for preset in presets:
        if category != "ALL" and preset["category"] != category:
            continue
        if target != "ALL" and preset["target"] != target:
            continue
        if source != "ALL" and preset["source"] != source:
            continue
        if settings.preset_favorites_only and preset["id"] not in favs:
            continue
        haystack = " ".join(
            [
                preset["name"],
                preset["category"],
                preset["target"],
                preset["desc"],
                " ".join(preset["tags"]),
            ]
        ).lower()
        if query and query not in haystack:
            continue
        if tag_query and tag_query not in " ".join(preset["tags"]).lower():
            continue
        result.append(preset)
    return result


def find_preset(preset_id):
    for preset in all_presets():
        if preset["id"] == preset_id:
            return preset
    return None


def delete_user_preset_by_id(preset_id):
    preset = find_preset(preset_id)
    if not preset or preset["source"] != SOURCE_USER:
        return False
    return delete_preset(preset["name"])
