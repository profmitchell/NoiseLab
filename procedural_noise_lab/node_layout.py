"""Stage-based node layout helpers (PRD §28-29).

Generated groups are organized left-to-right into 7 stages, each wrapped in
a Frame node so the user can collapse/inspect them.
"""

# Horizontal anchor per stage (PRD §28).
STAGE_X = {
    1: 0,      # Inputs
    2: 300,    # Coordinate Transform
    3: 700,    # Warp Field
    4: 1100,   # Primary Noise
    5: 1500,   # Fine Detail
    6: 1900,   # Output Shaping
    7: 2300,   # Outputs
}

STAGE_LABELS = {
    1: "01 Inputs",
    2: "02 Coordinate Transform",
    3: "03 Warp Field",
    4: "04 Primary 4D Noise",
    5: "05 Detail Layer",
    6: "06 Output Shaping",
    7: "07 Outputs",
}


def make_frame(tree, label, color=None):
    f = tree.nodes.new("NodeFrame")
    f.label = label
    f.use_custom_color = color is not None
    if color is not None:
        f.color = color
    f.label_size = 18
    f.shrink = True
    return f


def make_stage_frames(tree):
    """Return dict[stage_id -> NodeFrame]."""
    palette = {
        1: (0.18, 0.30, 0.45),
        2: (0.20, 0.40, 0.30),
        3: (0.45, 0.30, 0.20),
        4: (0.40, 0.20, 0.40),
        5: (0.30, 0.30, 0.45),
        6: (0.40, 0.35, 0.20),
        7: (0.20, 0.20, 0.30),
    }
    return {sid: make_frame(tree, STAGE_LABELS[sid], palette[sid]) for sid in STAGE_LABELS}


def attach(node, frame):
    if frame is not None:
        node.parent = frame
