"""
Pydantic schemas for the food bank recipe-card generator.

This is a staff-facing spinoff of the matcher feature: instead of a single
user's tracked pantry, a volunteer checks off what's on the shelves *today*
and gets back a small batch of printable, bilingual recipe cards built only
from that stock. Each generation is logged (see models.py) so staff can look
back at a previous day's batch without regenerating and re-spending.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class FoodBankGenerateRequest(BaseModel):
    # Names of items checked off as in-stock today, e.g. "canned black beans"
    available_items: list[str] = Field(..., min_length=1)
    # Subset of available_items staff flagged as near-expiry/overstocked --
    # the prompt asks Claude to prefer recipes that use these first.
    priority_items: list[str] = Field(default_factory=list)
    # e.g. "vegetarian", "halal", "low_sodium", "nut_free", "dairy_free"
    dietary_flags: list[str] = Field(default_factory=list)
    # e.g. "no_oven", "stovetop_only", "microwave_only", "no_fridge"
    equipment_constraints: list[str] = Field(default_factory=list)
    card_count: int = Field(default=4, ge=1, le=8)


class RecipeCard(BaseModel):
    title_en: str
    title_es: str
    ingredients_en: list[str]
    ingredients_es: list[str]
    steps_en: list[str]
    steps_es: list[str]
    dietary_tags: list[str] = Field(default_factory=list)
    uses_priority_items: bool = False
    notes_en: str = ""
    notes_es: str = ""


class FoodBankGenerateResponse(BaseModel):
    cards: list[RecipeCard]
    was_mocked: bool = False


class GenerationLogOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    created_at: datetime
    available_items: list[str]
    priority_items: list[str]
    dietary_flags: list[str]
    equipment_constraints: list[str]
    card_count_requested: int
    cards: list[RecipeCard]
    was_mocked: bool
