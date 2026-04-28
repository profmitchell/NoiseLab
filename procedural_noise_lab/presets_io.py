"""Save / load user presets as JSON in Blender's user config directory."""

import json
import os

import bpy

def _user_preset_dir():
    try:
        base = bpy.utils.user_resource('CONFIG', path="procedural_noise_lab", create=True)
        return os.path.join(base, "user_presets")
    except Exception:
        return os.path.join(os.path.expanduser("~"), ".procedural_noise_lab", "user_presets")


def _ensure_dir():
    os.makedirs(_user_preset_dir(), exist_ok=True)


def save_preset(name, target_group, values, description=""):
    """Persist a user preset to ``user_presets/<name>.json``."""
    _ensure_dir()
    data = {
        "name": name,
        "target": target_group,
        "values": values,
        "description": description,
    }
    path = os.path.join(_user_preset_dir(), f"{name}.json")
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)
    return path


def load_user_presets():
    """Return list of dicts from the user_presets folder."""
    _ensure_dir()
    out = []
    preset_dir = _user_preset_dir()
    for fname in sorted(os.listdir(preset_dir)):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(preset_dir, fname), encoding="utf-8") as fp:
                out.append(json.load(fp))
        except Exception:
            pass
    return out


def delete_preset(name):
    path = os.path.join(_user_preset_dir(), f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
