"""
Thin client around the Spoonacular API.

Free tier is capped at 150 requests/day, so callers should cache results in
our own DB (see recipes/service.py::ingest_spoonacular_results) rather than
re-querying Spoonacular on every pantry-matcher request.

Docs: https://spoonacular.com/food-api/docs
"""
import httpx

from app.core.config import get_settings

BASE_URL = "https://api.spoonacular.com"


class SpoonacularError(RuntimeError):
    pass


def _client() -> httpx.Client:
    settings = get_settings()
    if not settings.spoonacular_api_key:
        raise SpoonacularError(
            "SPOONACULAR_API_KEY is not set. Get a free key at "
            "https://spoonacular.com/food-api/console#Dashboard and add it to backend/.env"
        )
    return httpx.Client(base_url=BASE_URL, params={"apiKey": settings.spoonacular_api_key}, timeout=10.0)


def find_by_ingredients(ingredient_names: list[str], number: int = 10, ranking: int = 1) -> list[dict]:
    """
    Wraps GET /recipes/findByIngredients.

    ranking=1 maximizes used ingredients (good default for "what can I make
    with what I have"); ranking=2 minimizes missing ingredients instead.
    """
    with _client() as client:
        resp = client.get(
            "/recipes/findByIngredients",
            params={
                "ingredients": ",".join(ingredient_names),
                "number": number,
                "ranking": ranking,
                "ignorePantry": True,
            },
        )
        resp.raise_for_status()
        return resp.json()


def get_recipe_information(spoonacular_id: int) -> dict:
    """Wraps GET /recipes/{id}/information -- full ingredients + instructions."""
    with _client() as client:
        resp = client.get(f"/recipes/{spoonacular_id}/information")
        resp.raise_for_status()
        return resp.json()


def search_recipes(query: str, number: int = 10) -> list[dict]:
    """Wraps GET /recipes/complexSearch -- free-text recipe search."""
    with _client() as client:
        resp = client.get("/recipes/complexSearch", params={"query": query, "number": number})
        resp.raise_for_status()
        return resp.json().get("results", [])
