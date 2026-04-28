"""Central registry for built-in Procedural Noise Lab recipes."""

from dataclasses import dataclass

from . import recipe_animated_mask
from . import recipe_domain_warp
from . import recipe_infinite_4d
from . import recipe_liquid_marble


@dataclass(frozen=True)
class RecipeInfo:
    key: str
    display_name: str
    internal_name: str
    recipe_id: str
    recipe_version: str
    input_spec: tuple
    output_spec: tuple
    build: object
    icon: str
    description: str
    supports_shader: bool = True
    supports_geometry: bool = True
    supports_demo: bool = True

    def group_name(self, tree_type="ShaderNodeTree"):
        if tree_type == "GeometryNodeTree":
            return self.internal_name + "_Geo"
        return self.internal_name

    def all_group_names(self):
        return {self.internal_name, self.internal_name + "_Geo"}


RECIPES = (
    RecipeInfo(
        key="INFINITE_4D",
        display_name=recipe_infinite_4d.DISPLAY_NAME,
        internal_name=recipe_infinite_4d.INTERNAL_NAME,
        recipe_id=recipe_infinite_4d.RECIPE_ID,
        recipe_version=recipe_infinite_4d.RECIPE_VERSION,
        input_spec=tuple(recipe_infinite_4d.INPUT_SPEC),
        output_spec=tuple(recipe_infinite_4d.OUTPUT_SPEC),
        build=recipe_infinite_4d.build,
        icon="FORCE_TURBULENCE",
        description="Flagship animated 4D-style domain-warped noise.",
    ),
    RecipeInfo(
        key="DOMAIN_WARP",
        display_name=recipe_domain_warp.DISPLAY_NAME,
        internal_name=recipe_domain_warp.INTERNAL_NAME,
        recipe_id=recipe_domain_warp.RECIPE_ID,
        recipe_version=recipe_domain_warp.RECIPE_VERSION,
        input_spec=tuple(recipe_domain_warp.INPUT_SPEC),
        output_spec=tuple(recipe_domain_warp.OUTPUT_SPEC),
        build=recipe_domain_warp.build,
        icon="MOD_WARP",
        description="Focused base noise displaced by a secondary warp field.",
    ),
    RecipeInfo(
        key="ANIMATED_MASK",
        display_name=recipe_animated_mask.DISPLAY_NAME,
        internal_name=recipe_animated_mask.INTERNAL_NAME,
        recipe_id=recipe_animated_mask.RECIPE_ID,
        recipe_version=recipe_animated_mask.RECIPE_VERSION,
        input_spec=tuple(recipe_animated_mask.INPUT_SPEC),
        output_spec=tuple(recipe_animated_mask.OUTPUT_SPEC),
        build=recipe_animated_mask.build,
        icon="MOD_MASK",
        description="Evolving masks with soft, hard, edge, and height outputs.",
    ),
    RecipeInfo(
        key="LIQUID_MARBLE",
        display_name=recipe_liquid_marble.DISPLAY_NAME,
        internal_name=recipe_liquid_marble.INTERNAL_NAME,
        recipe_id=recipe_liquid_marble.RECIPE_ID,
        recipe_version=recipe_liquid_marble.RECIPE_VERSION,
        input_spec=tuple(recipe_liquid_marble.INPUT_SPEC),
        output_spec=tuple(recipe_liquid_marble.OUTPUT_SPEC),
        build=recipe_liquid_marble.build,
        icon="MOD_OCEAN",
        description="Warped wave texture for liquid marble patterns.",
    ),
)

RECIPES_BY_KEY = {recipe.key: recipe for recipe in RECIPES}
RECIPES_BY_ID = {recipe.recipe_id: recipe for recipe in RECIPES}
RECIPES_BY_INTERNAL_NAME = {
    group_name: recipe
    for recipe in RECIPES
    for group_name in recipe.all_group_names()
}

DEMO_TARGET_ITEMS = tuple(
    (recipe.internal_name, recipe.display_name, recipe.description)
    for recipe in RECIPES
    if recipe.supports_demo
)


def recipe_for_group(group):
    if group is None:
        return None
    recipe_id = group.get("inl_recipe_id")
    if recipe_id in RECIPES_BY_ID:
        return RECIPES_BY_ID[recipe_id]
    base_name = group.name.removesuffix("_Geo")
    return RECIPES_BY_INTERNAL_NAME.get(base_name) or RECIPES_BY_INTERNAL_NAME.get(group.name)


def recipe_for_target_name(target_name):
    base_name = target_name.removesuffix("_Geo")
    return RECIPES_BY_INTERNAL_NAME.get(base_name) or RECIPES_BY_INTERNAL_NAME.get(target_name)
