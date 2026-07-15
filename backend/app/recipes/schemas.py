"""Pydantic schemas for the recipes API."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.recipes.models import RecipeSource


class RecipeIngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    raw_text: str
    quantity: float | None = None
    unit: str | None = None


class RecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    source: RecipeSource
    source_url: str | None = None
    instructions: str
    servings: int
    ready_in_minutes: int | None = None
    image_url: str | None = None
    cached_at: datetime
    ingredients: list[RecipeIngredientOut] = []


class RecipeSearchQuery(BaseModel):
    """Used for the /api/recipes/search endpoint (text search, not pantry matching)."""
    query: str
    max_results: int = 10
