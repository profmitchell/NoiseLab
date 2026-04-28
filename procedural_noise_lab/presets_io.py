"""Save / load user presets as JSON alongside the add-on (PRD §18)."""

import json
import os

_USER_PRESET_DIR = os.path.join(os.path.dirname(__file__), "user_presets")


def _ensure_dir():
    os.makedirs(_USER_PRESET_DIR, exist_ok=True)


def save_preset(name, target_group, values, description=""):
    """Persist a user preset to ``user_presets/<name>.json``."""
    _ensure_dir()
    data = {
        "name": name,
        "target": target_group,
        "values": values,
        "description": description,
    }
    path = os.path.join(_USER_PRESET_DIR, f"{name}.json")
    with open(path, "w") as fp:
        json.dump(data, fp, indent=2)
    return path


def load_user_presets():
    """Return list of dicts from the user_presets folder."""
    _ensure_dir()
    out = []
    for fname in sorted(os.listdir(_USER_PRESET_DIR)):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(_USER_PRESET_DIR, fname)) as fp:
                out.append(json.load(fp))
        except Exception:
            pass
    return out


def delete_preset(name):
    path = os.path.join(_USER_PRESET_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
