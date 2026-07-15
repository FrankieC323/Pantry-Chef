"""
Recipe scaler / unit converter.

Pure arithmetic, intentionally has no AI dependency -- scaling a recipe from
4 servings to 6 doesn't need an LLM call, and keeping this deterministic
makes it instant and free to run. The matcher module's
`explain_substitution()` is what handles the fuzzy "I don't have X" cases.
"""
from app.pantry.models import Unit

# (value in milliliters) for volume units, (value in grams) for mass units.
# Cross-category conversion (e.g. cup -> gram) is intentionally NOT supported
# here since it depends on ingredient density (1 cup flour != 1 cup honey by
# weight) -- that's a good candidate to hand off to Claude later if needed.
_VOLUME_TO_ML = {
    Unit.ml: 1.0,
    Unit.l: 1000.0,
    Unit.tsp: 4.92892,
    Unit.tbsp: 14.7868,
    Unit.cup: 236.588,
    Unit.fl_oz: 29.5735,
}

_MASS_TO_G = {
    Unit.g: 1.0,
    Unit.kg: 1000.0,
    Unit.oz: 28.3495,
    Unit.lb: 453.592,
}


class IncompatibleUnitsError(ValueError):
    pass


def scale_quantity(original_quantity: float, original_servings: int, target_servings: int) -> float:
    """Linearly scales a quantity from original_servings to target_servings."""
    if original_servings <= 0:
        raise ValueError("original_servings must be > 0")
    factor = target_servings / original_servings
    return round(original_quantity * factor, 4)


def convert_unit(quantity: float, from_unit: Unit, to_unit: Unit) -> float:
    """Converts a quantity between compatible units (volume<->volume or mass<->mass)."""
    if from_unit == to_unit:
        return quantity

    if from_unit in _VOLUME_TO_ML and to_unit in _VOLUME_TO_ML:
        ml = quantity * _VOLUME_TO_ML[from_unit]
        return round(ml / _VOLUME_TO_ML[to_unit], 4)

    if from_unit in _MASS_TO_G and to_unit in _MASS_TO_G:
        grams = quantity * _MASS_TO_G[from_unit]
        return round(grams / _MASS_TO_G[to_unit], 4)

    raise IncompatibleUnitsError(
        f"Cannot convert between {from_unit.value} and {to_unit.value} without ingredient "
        "density (e.g. cups of flour vs grams of flour differ by ingredient). "
        "Use the /api/matcher/substitute endpoint for an AI estimate instead."
    )


def scale_recipe_ingredients(
    ingredients: list[dict], original_servings: int, target_servings: int
) -> list[dict]:
    """
    ingredients: [{"name": str, "quantity": float|None, "unit": str|None}, ...]
    Returns the same shape with quantities scaled. Ingredients with no
    quantity (e.g. "salt to taste") are passed through unchanged.
    """
    scaled = []
    for ing in ingredients:
        new_ing = dict(ing)
        if ing.get("quantity") is not None:
            new_ing["quantity"] = scale_quantity(ing["quantity"], original_servings, target_servings)
        scaled.append(new_ing)
    return scaled
