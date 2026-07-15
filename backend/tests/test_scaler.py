"""
Tests for the scaler module -- chosen as the first test target since it's
pure logic with no external dependencies (no DB, no API calls needed),
unlike pantry/recipes/matcher which need a test DB or mocked HTTP clients.
"""
import pytest

from app.pantry.models import Unit
from app.scaler.service import scale_quantity, convert_unit, IncompatibleUnitsError, scale_recipe_ingredients


def test_scale_quantity_doubles_when_servings_double():
    assert scale_quantity(2.0, original_servings=4, target_servings=8) == 4.0


def test_scale_quantity_halves_when_servings_halve():
    assert scale_quantity(2.0, original_servings=4, target_servings=2) == 1.0


def test_scale_quantity_rejects_zero_original_servings():
    with pytest.raises(ValueError):
        scale_quantity(2.0, original_servings=0, target_servings=4)


def test_convert_unit_same_unit_is_noop():
    assert convert_unit(3.0, Unit.cup, Unit.cup) == 3.0


def test_convert_unit_cups_to_ml():
    # 1 cup ~= 236.588 ml
    result = convert_unit(1.0, Unit.cup, Unit.ml)
    assert abs(result - 236.588) < 0.01


def test_convert_unit_lb_to_g():
    result = convert_unit(1.0, Unit.lb, Unit.g)
    assert abs(result - 453.592) < 0.01


def test_convert_unit_incompatible_categories_raises():
    with pytest.raises(IncompatibleUnitsError):
        convert_unit(1.0, Unit.cup, Unit.g)


def test_scale_recipe_ingredients_passes_through_missing_quantity():
    ingredients = [
        {"name": "salt", "quantity": None, "unit": None},
        {"name": "flour", "quantity": 2.0, "unit": "cup"},
    ]
    scaled = scale_recipe_ingredients(ingredients, original_servings=4, target_servings=8)
    assert scaled[0]["quantity"] is None
    assert scaled[1]["quantity"] == 4.0
