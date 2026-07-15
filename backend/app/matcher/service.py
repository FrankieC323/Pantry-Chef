"""
Matcher orchestration.

Flow:
1. Pull current pantry from DB.
2. Pre-filter cached recipes by rough ingredient overlap (cheap, in-process --
   avoids sending Claude hundreds of irrelevant recipes and keeps token usage
   sane).
3. Pull a lightweight summary of the user's rating history for personalization.
4. Call Claude to do the actual reasoning: rank the pre-filtered candidates,
   explain substitutions, and generate a new recipe if nothing fits well.
5. Persist a generated recipe (if any) so it can be rated like any other recipe.
"""
from sqlalchemy.orm import Session

from app.matcher import claude_client
from app.pantry.models import PantryItem
from app.pantry.service import list_items, get_expiring_soon
from app.ratings.service import summarize_preferences
from app.recipes.models import Recipe
from app.recipes.service import list_recipes, save_generated_recipe
from app.core.config import get_settings

settings = get_settings()


def _pantry_to_summary(items: list[PantryItem]) -> list[dict]:
    return [
        {
            "name": item.name,
            "quantity": item.quantity,
            "unit": item.unit.value,
            "days_until_expiration": item.days_until_expiration(),
        }
        for item in items
    ]


def _prefilter_candidates(pantry_names: set[str], recipes: list[Recipe], top_n: int = 15) -> list[Recipe]:
    """
    Cheap in-process ranking by raw ingredient-name overlap, just to cut the
    candidate pool down before handing it to Claude. This is NOT the final
    ranking shown to the user -- Claude does the real reasoning (fuzzy
    matches, substitutions) on top of this shortlist.
    """
    scored = []
    for recipe in recipes:
        recipe_ingredient_names = {ing.name for ing in recipe.ingredients}
        if not recipe_ingredient_names:
            continue
        overlap = len(recipe_ingredient_names & pantry_names)
        score = overlap / len(recipe_ingredient_names)
        scored.append((score, recipe))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [recipe for _, recipe in scored[:top_n]]


def get_suggestions(db: Session, prioritize_expiring: bool = True) -> dict:
    """
    Main entry point used by the /api/matcher/suggest route.

    Returns the Claude-shaped dict from claude_client.get_ranked_matches(),
    plus the raw recipe objects keyed by id so the route can attach full
    recipe details to the response.
    """
    pantry_items = list_items(db)
    if not pantry_items:
        return {"ranked_matches": [], "generated_recipe": None, "_recipes_by_id": {}}

    pantry_names = {item.name.lower() for item in pantry_items}
    pantry_summary = _pantry_to_summary(pantry_items)

    all_recipes = list_recipes(db, limit=300)
    candidates = _prefilter_candidates(pantry_names, all_recipes)

    candidate_payload = [
        {
            "id": r.id,
            "title": r.title,
            "ingredients": [ing.name for ing in r.ingredients],
        }
        for r in candidates
    ]

    preference_summary = summarize_preferences(db)

    result = claude_client.get_ranked_matches(
        pantry_summary=pantry_summary,
        candidate_recipes=candidate_payload,
        rating_preferences=preference_summary,
    )

    # If Claude generated a new recipe (nothing in cache was a good fit),
    # persist it so it shows up in history and can be rated.
    generated = result.get("generated_recipe")
    if generated:
        saved = save_generated_recipe(
            db,
            title=generated["title"],
            instructions=generated["instructions"],
            servings=generated.get("servings", 4),
            ingredients=generated["ingredients"],
        )
        # backfill the recipe_id on any ranked_matches entry that referenced
        # the generated recipe (Claude sets recipe_id to null for it)
        for match in result.get("ranked_matches", []):
            if match.get("recipe_id") is None:
                match["recipe_id"] = saved.id
        result["generated_recipe"]["id"] = saved.id

    recipes_by_id = {r.id: r for r in candidates}
    if generated:
        recipes_by_id[result["generated_recipe"]["id"]] = saved

    result["_recipes_by_id"] = recipes_by_id
    return result
