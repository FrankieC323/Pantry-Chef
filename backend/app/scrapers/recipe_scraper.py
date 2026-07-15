"""
Supplemental recipe scraper.

This is a secondary data source for when Spoonacular's free-tier daily quota
is exhausted, or to demonstrate handling messier non-API HTML data.

IMPORTANT: scraping should be a deliberate, rate-limited batch job (e.g. run
via `python -m app.scrapers.recipe_scraper` as a one-off ingestion script),
NOT called live on every user request. Respect the target site's
robots.txt and terms of service, and add delays between requests.

Many recipe sites embed Schema.org Recipe JSON-LD in a <script
type="application/ld+json"> tag -- that's usually far more reliable to
parse than scraping the rendered HTML directly, and is what this module
prefers when available.
"""
import json
import time
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "PantryChefBot/0.1 (portfolio project; contact: replace-with-your-email@example.com)"
REQUEST_DELAY_SECONDS = 1.5  # be polite -- don't hammer the target site


@dataclass
class ScrapedRecipe:
    title: str
    source_url: str
    ingredients_raw: list[str]
    instructions: str
    image_url: str | None = None
    servings: int | None = None


def _extract_json_ld_recipe(soup: BeautifulSoup) -> dict | None:
    """Look for Schema.org Recipe structured data, which most recipe sites embed."""
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue

        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            graph = candidate.get("@graph") if isinstance(candidate, dict) else None
            items_to_check = graph if graph else [candidate]
            for item in items_to_check:
                if isinstance(item, dict) and item.get("@type") in ("Recipe", ["Recipe"]):
                    return item
    return None


def scrape_recipe_url(url: str) -> ScrapedRecipe | None:
    """
    Fetch a single recipe page and extract structured data.

    Returns None if no Recipe JSON-LD is found (rather than guessing from
    raw HTML, which is fragile and breaks silently when a site redesigns).
    """
    headers = {"User-Agent": USER_AGENT}
    resp = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    recipe_data = _extract_json_ld_recipe(soup)
    if recipe_data is None:
        return None

    ingredients_raw = recipe_data.get("recipeIngredient", [])

    instructions_field = recipe_data.get("recipeInstructions", "")
    if isinstance(instructions_field, list):
        steps = []
        for step in instructions_field:
            if isinstance(step, dict):
                steps.append(step.get("text", ""))
            else:
                steps.append(str(step))
        instructions = "\n".join(s for s in steps if s)
    else:
        instructions = str(instructions_field)

    image = recipe_data.get("image")
    if isinstance(image, list):
        image_url = image[0] if image else None
    elif isinstance(image, dict):
        image_url = image.get("url")
    else:
        image_url = image

    servings = None
    yield_field = recipe_data.get("recipeYield")
    if yield_field:
        digits = "".join(c for c in str(yield_field) if c.isdigit())
        servings = int(digits) if digits else None

    return ScrapedRecipe(
        title=recipe_data.get("name", "Untitled recipe"),
        source_url=url,
        ingredients_raw=ingredients_raw,
        instructions=instructions,
        image_url=image_url,
        servings=servings,
    )


def scrape_recipe_urls(urls: list[str]) -> list[ScrapedRecipe]:
    """Batch scrape with politeness delay between requests."""
    results = []
    for i, url in enumerate(urls):
        try:
            recipe = scrape_recipe_url(url)
            if recipe:
                results.append(recipe)
        except httpx.HTTPError as e:
            print(f"[scraper] failed to fetch {url}: {e}")

        if i < len(urls) - 1:
            time.sleep(REQUEST_DELAY_SECONDS)

    return results
