"""Randomise / mutate group-node inputs (PRD §33 / other ideas §26)."""

import random

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


def _safe_range(sock):
    """Heuristic soft range for a float socket."""
    lo = getattr(sock, "min_value", 0.0)
    hi = getattr(sock, "max_value", 1.0)
    # Fallback if Blender doesn't expose min/max on group sockets
    if lo == hi:
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

    for inp in group_node.inputs:
        if inp.name in locked_names:
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
        inp.default_value = max(lo, min(hi, new_val))
