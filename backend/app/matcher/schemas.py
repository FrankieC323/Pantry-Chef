"""Pydantic schemas for the matcher API."""
from pydantic import BaseModel

from app.recipes.schemas import RecipeOut


class RankedMatch(BaseModel):
    recipe_id: str | None
    title: str
    match_score: int
    have_ingredients: list[str]
    missing_ingredients: list[str]
    substitution_notes: str = ""
    uses_expiring_items: bool = False
    reasoning: str = ""
    recipe: RecipeOut | None = None  # filled in by the route after the Claude call


class GeneratedRecipeIngredient(BaseModel):
    name: str
    raw_text: str
    quantity: float | None = None
    unit: str | None = None


class GeneratedRecipe(BaseModel):
    id: str | None = None
    title: str
    servings: int
    ingredients: list[GeneratedRecipeIngredient]
    instructions: str


class MatcherResponse(BaseModel):
    ranked_matches: list[RankedMatch]
    generated_recipe: GeneratedRecipe | None = None


class SubstitutionRequest(BaseModel):
    missing_ingredient: str


class SubstitutionResponse(BaseModel):
    suggestion: str
