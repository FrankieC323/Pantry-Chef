"""
Matcher endpoints -- the AI-enhanced ingredient-to-recipe matching feature.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.matcher import service, claude_client
from app.matcher.schemas import MatcherResponse, RankedMatch, SubstitutionRequest, SubstitutionResponse
from app.pantry.service import list_items
from app.recipes.schemas import RecipeOut

router = APIRouter(prefix="/api/matcher", tags=["matcher"])


@router.post("/suggest", response_model=MatcherResponse)
def suggest(db: Session = Depends(get_db)):
    """
    Core feature: given the current pantry, ask Claude to rank cached recipes
    (with substitution reasoning) and generate a new one if nothing fits well.
    """
    result = service.get_suggestions(db)
    recipes_by_id = result.pop("_recipes_by_id", {})

    matches = []
    for raw_match in result.get("ranked_matches", []):
        recipe_obj = recipes_by_id.get(raw_match.get("recipe_id"))
        match = RankedMatch(**raw_match, recipe=RecipeOut.model_validate(recipe_obj) if recipe_obj else None)
        matches.append(match)

    return MatcherResponse(ranked_matches=matches, generated_recipe=result.get("generated_recipe"))


@router.post("/substitute", response_model=SubstitutionResponse)
def substitute(payload: SubstitutionRequest, db: Session = Depends(get_db)):
    """Quick single-ingredient substitution helper, used by the recipe scaler UI."""
    pantry_names = [item.name for item in list_items(db)]
    suggestion = claude_client.explain_substitution(payload.missing_ingredient, pantry_names)
    return SubstitutionResponse(suggestion=suggestion)
