"""Pydantic schemas for the scaler/converter API."""
from pydantic import BaseModel

from app.pantry.models import Unit


class IngredientQuantity(BaseModel):
    name: str
    quantity: float | None = None
    unit: str | None = None


class ScaleRecipeRequest(BaseModel):
    ingredients: list[IngredientQuantity]
    original_servings: int
    target_servings: int


class ScaleRecipeResponse(BaseModel):
    ingredients: list[IngredientQuantity]


class ConvertUnitRequest(BaseModel):
    quantity: float
    from_unit: Unit
    to_unit: Unit


class ConvertUnitResponse(BaseModel):
    quantity: float
    unit: Unit
