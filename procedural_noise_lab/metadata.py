"""Version metadata stamped onto every generated node group (PRD §27)."""

GENERATOR_VERSION = (0, 3, 0)

PROP_RECIPE_ID = "inl_recipe_id"
PROP_RECIPE_VERSION = "inl_recipe_version"
PROP_GENERATOR_VERSION = "inl_generator_version"


def stamp_group(group, recipe_id: str, recipe_version: str):
    group[PROP_RECIPE_ID] = recipe_id
    group[PROP_RECIPE_VERSION] = recipe_version
    group[PROP_GENERATOR_VERSION] = ".".join(str(x) for x in GENERATOR_VERSION)


def get_recipe_id(group):
    return group.get(PROP_RECIPE_ID)
