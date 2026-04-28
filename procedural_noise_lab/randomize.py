"""Randomise / mutate group-node inputs (PRD §33 / other ideas §26)."""

import random
import math

# Input names that belong to each lock category.
LOCK_GROUPS = {
    "SCALE":     {"Scale", "Base Scale", "Warp Scale", "Fine Detail Scale"},
    "TIME":      {"Time", "Speed", "Warp Speed"},
    "WARP":      {"Warp Amount", "Warp Scale", "Warp Speed", "Warp Detail",
                  "Warp Time Offset", "Twist Amount"},
    "OUTPUT":    {"Contrast", "Threshold", "Invert", "Output Min", "Output Max",
                  "Edge Width", "Softness"},
    "ANIMATION": {"Time", "Speed", "Morph", "Pulse Amount"},
}

RANDOMIZE_RANGES = {
    "Time": (0.0, 8.0),
    "Seed": (-100.0, 100.0),
    "Scale": (0.5, 35.0),
    "Base Scale": (0.5, 35.0),
    "Warp Scale": (0.25, 20.0),
    "Wave Scale": (0.5, 35.0),
    "Fine Detail Scale": (1.0, 12.0),
    "Speed": (-4.0, 4.0),
    "Warp Speed": (-4.0, 4.0),
    "Warp Time Offset": (-8.0, 8.0),
    "Morph": (-8.0, 8.0),
    "Drift X": (-8.0, 8.0),
    "Drift Y": (-8.0, 8.0),
    "Drift Z": (-8.0, 8.0),
    "Stretch X": (-6.0, 6.0),
    "Stretch Y": (-6.0, 6.0),
    "Stretch Z": (-6.0, 6.0),
    "Warp Amount": (-8.0, 8.0),
    "Twist Amount": (-12.0, 12.0),
    "Distortion": (-8.0, 12.0),
    "Wave Distortion": (-8.0, 20.0),
    "Contrast": (0.0, 8.0),
    "Lacunarity": (0.0, 8.0),
    "Output Min": (-2.0, 1.0),
    "Output Max": (0.0, 3.0),
}


def _finite_ui_bound(value):
    return (
        isinstance(value, (int, float))
        and math.isfinite(value)
        and abs(value) < 1.0e12
    )


def _safe_range(sock):
    """Heuristic soft range for a float socket."""
    if sock.name in RANDOMIZE_RANGES:
        return RANDOMIZE_RANGES[sock.name]
    lo = getattr(sock, "min_value", 0.0)
    hi = getattr(sock, "max_value", 1.0)
    # Fallback if Blender exposes no practical min/max or uses huge float bounds
    if lo == hi or not (_finite_ui_bound(lo) and _finite_ui_bound(hi)):
        lo, hi = 0.0, 10.0
    return lo, hi


def randomize_inputs(group_node, mutate=False, mutate_pct=0.2,
                     locked_categories=None, rng_seed=None):
    """Randomise or mutate exposed float inputs on a group node.

    locked_categories: set of keys from LOCK_GROUPS to skip.
    """
    locked_categories = locked_categories or set()
    locked_names = set()
    for cat in locked_categories:
        locked_names |= LOCK_GROUPS.get(cat, set())

    rng = random.Random(rng_seed)

    changed = 0
    skipped = 0
    for inp in group_node.inputs:
        if inp.name in locked_names:
            skipped += 1
            continue
        if inp.type != 'VALUE':
            continue
        lo, hi = _safe_range(inp)
        cur = inp.default_value
        if mutate:
            delta = (hi - lo) * mutate_pct
            new_val = cur + rng.uniform(-delta, delta)
        else:
            new_val = rng.uniform(lo, hi)
        inp.default_value = new_val
        changed += 1
    return changed, skipped
