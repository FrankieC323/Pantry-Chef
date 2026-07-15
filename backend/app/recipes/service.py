"""
Recipe service layer: DB reads/writes plus ingestion helpers that normalize
data from Spoonacular and the scraper into our own schema.
"""
import re

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.recipes.models import Recipe, RecipeIngredient, RecipeSource
from app.scrapers.recipe_scraper import ScrapedRecipe

# crude unit/quantity parser for free-text ingredient lines like
# "1 1/2 cups diced onion" -- good enough for matching purposes, not meant
# to be a perfect NLP parser. Claude is used for the cases this misses
# (see matcher/service.py).
#
# NOTE: alternatives are ordered longest/most-specific first (e.g. "lb"
# before "l", "tbsp" before "tsp") because regex alternation picks the
# first match, not the longest one. A trailing word boundary (\b) stops a
# short unit like "l" from partially matching inside "lb".
_QTY_UNIT_RE = re.compile(
    r"^\s*(?P<qty>[\d/.\s]+)?\s*(?P<unit>tablespoons?|tbsp|teaspoons?|tsp|"
    r"cups?|grams?|kg|g|ml|liters?|lb|pounds?|oz|ounces?|cloves?|"
    r"pinch(?:es)?|l)\b\.?\s*(?P<rest>.*)$",
    re.IGNORECASE,
)

# fallback for lines with a leading quantity but no recognized unit word,
# e.g. "3 eggs" or "2 lemons" -- treated as countable/piece items.
_QTY_ONLY_RE = re.compile(r"^\s*(?P<qty>[\d/.\s]+)\s+(?P<rest>.+)$")


def _parse_qty_str(qty_str: str) -> float | None:
    """Parses a quantity string that may include simple fractions like '1 1/2'."""
    qty_str = qty_str.strip()
    if not qty_str:
        return None
    try:
        if "/" in qty_str:
            total = 0.0
            for part in qty_str.split():
                if "/" in part:
                    num, denom = part.split("/")
                    total += float(num) / float(denom)
                else:
                    total += float(part)
            return total
        return float(qty_str)
    except ValueError:
        return None


def _parse_ingredient_line(raw: str) -> tuple[str, float | None, str | None]:
    """Returns (normalized_name, quantity, unit) from a free-text ingredient line."""
    match = _QTY_UNIT_RE.match(raw)
    if match:
        qty_str = match.group("qty") or ""
        unit = (match.group("unit") or "").strip().lower() or None
        name = (match.group("rest") or raw).strip().lower()
        return name, _parse_qty_str(qty_str), unit

    # no recognized unit word -- try quantity + bare noun, e.g. "3 eggs"
    fallback = _QTY_ONLY_RE.match(raw)
    if fallback:
        name = fallback.group("rest").strip().lower()
        return name, _parse_qty_str(fallback.group("qty")), None

    return raw.strip().lower(), None, None


def get_recipe(db: Session, recipe_id: str) -> Recipe | None:
    stmt = select(Recipe).options(selectinload(Recipe.ingredients)).where(Recipe.id == recipe_id)
    return db.scalars(stmt).first()


def list_recipes(db: Session, limit: int = 50) -> list[Recipe]:
    stmt = select(Recipe).options(selectinload(Recipe.ingredients)).limit(limit)
    return list(db.scalars(stmt))


def get_all_ingredient_names(db: Session) -> list[str]:
    """Distinct normalized ingredient names across the cached recipe corpus."""
    stmt = select(RecipeIngredient.name).distinct()
    return list(db.scalars(stmt))


def ingest_spoonacular_recipe(db: Session, info: dict) -> Recipe:
    """
    Normalize one result from spoonacular_client.get_recipe_information()
    into our Recipe/RecipeIngredient tables. Upserts by source_url to avoid
    duplicate cache entries.
    """
    source_url = info.get("sourceUrl") or info.get("spoonacularSourceUrl", "")

    existing = db.scalars(select(Recipe).where(Recipe.source_url == source_url)).first()
    if existing:
        return existing

    instructions = info.get("instructions") or ""
    if not instructions and info.get("analyzedInstructions"):
        steps = []
        for block in info["analyzedInstructions"]:
            for step in block.get("steps", []):
                steps.append(step.get("step", ""))
        instructions = "\n".join(steps)

    recipe = Recipe(
        title=info.get("title", "Untitled recipe"),
        source=RecipeSource.spoonacular,
        source_url=source_url,
        instructions=instructions,
        servings=info.get("servings", 4),
        ready_in_minutes=info.get("readyInMinutes"),
        image_url=info.get("image"),
    )

    for ing in info.get("extendedIngredients", []):
        recipe.ingredients.append(
            RecipeIngredient(
                name=(ing.get("nameClean") or ing.get("name") or "").strip().lower(),
                raw_text=ing.get("original", ""),
                quantity=ing.get("amount"),
                unit=ing.get("unit"),
            )
        )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def ingest_scraped_recipe(db: Session, scraped: ScrapedRecipe) -> Recipe:
    """Normalize a ScrapedRecipe into our Recipe/RecipeIngredient tables."""
    existing = db.scalars(select(Recipe).where(Recipe.source_url == scraped.source_url)).first()
    if existing:
        return existing

    recipe = Recipe(
        title=scraped.title,
        source=RecipeSource.scraped,
        source_url=scraped.source_url,
        instructions=scraped.instructions,
        servings=scraped.servings or 4,
        image_url=scraped.image_url,
    )

    for raw_line in scraped.ingredients_raw:
        name, qty, unit = _parse_ingredient_line(raw_line)
        recipe.ingredients.append(
            RecipeIngredient(name=name, raw_text=raw_line, quantity=qty, unit=unit)
        )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def save_generated_recipe(
    db: Session,
    title: str,
    instructions: str,
    servings: int,
    ingredients: list[dict],
) -> Recipe:
    """
    Persist a Claude-generated recipe (see matcher/claude_client.py) so it
    shows up in recipe history / can be rated like any other recipe.
    `ingredients` is a list of {"name": str, "raw_text": str, "quantity": float|None, "unit": str|None}.
    """
    recipe = Recipe(
        title=title,
        source=RecipeSource.generated,
        instructions=instructions,
        servings=servings,
    )
    for ing in ingredients:
        recipe.ingredients.append(
            RecipeIngredient(
                name=ing["name"].strip().lower(),
                raw_text=ing.get("raw_text", ing["name"]),
                quantity=ing.get("quantity"),
                unit=ing.get("unit"),
            )
        )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe
