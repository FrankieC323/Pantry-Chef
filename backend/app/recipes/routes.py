"""Recipe browsing + search endpoints (separate from the AI matcher, which lives in app/matcher)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.recipes import service
from app.recipes.schemas import RecipeOut
from app.recipes.spoonacular_client import search_recipes, get_recipe_information, SpoonacularError

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("", response_model=list[RecipeOut])
def list_cached_recipes(limit: int = 50, db: Session = Depends(get_db)):
    """Recipes already cached in our DB (from prior Spoonacular/scrape/generation calls)."""
    return service.list_recipes(db, limit=limit)


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: str, db: Session = Depends(get_db)):
    recipe = service.get_recipe(db, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/search-and-cache", response_model=list[RecipeOut])
def search_and_cache(query: str, max_results: int = 5, db: Session = Depends(get_db)):
    """
    Free-text search against Spoonacular, fetches full details for each hit,
    and caches them in our DB. Counts against the daily Spoonacular quota
    (~150/day on the free tier) so keep max_results modest.
    """
    try:
        hits = search_recipes(query, number=max_results)
    except SpoonacularError as e:
        raise HTTPException(status_code=503, detail=str(e))

    cached = []
    for hit in hits:
        info = get_recipe_information(hit["id"])
        cached.append(service.ingest_spoonacular_recipe(db, info))
    return cached
