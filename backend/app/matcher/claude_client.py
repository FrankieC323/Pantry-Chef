"""
Claude API integration for the matcher.

This is the "AI-enhanced" part of the project: rather than pure ingredient
set-overlap, we hand Claude the pantry + a candidate set of cached recipes
(plus rating history for personalization) and ask it to reason about fuzzy
matches, sensible substitutions, and -- when nothing in the cache fits well
-- generate a new recipe from scratch.

Uses structured JSON output (see docs/structured_outputs pattern) so the
response can be parsed straight into Pydantic models for the API response.
"""
import json

from anthropic import Anthropic

from app.core.config import get_settings

_SYSTEM_PROMPT = """You are a practical home-cooking assistant inside a recipe app. \
You will be given:
1. The user's current pantry (ingredients, quantities, units, and days until expiration)
2. A list of candidate recipes already in the app's cache (title + ingredients)
3. Optionally, the user's past ratings/preferences

Your job is to recommend the best matches and explain substitutions in plain, \
practical language a home cook would use -- not technical jargon.

Always respond with ONLY valid JSON, no markdown fences, no preamble, matching \
this exact shape:
{
  "ranked_matches": [
    {
      "recipe_id": "string, must be one of the candidate recipe ids given to you, \
or null if this is a newly generated recipe",
      "title": "string",
      "match_score": 0-100 integer,
      "have_ingredients": ["list of pantry ingredient names this recipe uses"],
      "missing_ingredients": ["list of ingredients the user does not have"],
      "substitution_notes": "string explaining any smart substitutions, or empty string",
      "uses_expiring_items": true/false,
      "reasoning": "one or two sentence plain-language explanation of why this is a good match"
    }
  ],
  "generated_recipe": {
    "title": "string",
    "servings": integer,
    "ingredients": [{"name": "string", "raw_text": "string e.g. '2 cloves garlic, minced'", \
"quantity": number or null, "unit": "string or null"}],
    "instructions": "string, numbered steps separated by newlines"
  } or null if no new recipe was needed
}

Only include "generated_recipe" if none of the candidate recipes are a reasonable \
match (match_score would be below 40 for all of them) AND the pantry has enough \
ingredients to make something coherent. Prefer ranking existing candidates when \
they're reasonably good matches -- only generate something new as a last resort.
"""


def _client() -> Anthropic:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to backend/.env -- get a key at "
            "https://console.anthropic.com/"
        )
    return Anthropic(api_key=settings.anthropic_api_key)


def get_ranked_matches(
    pantry_summary: list[dict],
    candidate_recipes: list[dict],
    rating_preferences: str | None = None,
) -> dict:
    """
    Calls Claude to rank candidate recipes against the pantry and optionally
    generate a new recipe. Returns the parsed JSON dict described in
    _SYSTEM_PROMPT above.

    pantry_summary: [{"name": str, "quantity": float, "unit": str, "days_until_expiration": int|None}]
    candidate_recipes: [{"id": str, "title": str, "ingredients": [str, ...]}]
    rating_preferences: free-text summary of what the user tends to like/dislike,
        e.g. "Rates spicy dishes highly. Has given low ratings to recipes with cilantro."
    """
    settings = get_settings()
    client = _client()

    user_message = {
        "pantry": pantry_summary,
        "candidate_recipes": candidate_recipes,
        "user_preferences": rating_preferences or "No rating history yet.",
    }

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=4000,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(user_message, default=str)}],
    )

    text_blocks = [block.text for block in response.content if block.type == "text"]
    raw_text = "".join(text_blocks).strip()

    # defensive: strip markdown fences if the model adds them despite instructions
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Claude returned non-JSON output: {raw_text[:500]}") from e


def explain_substitution(missing_ingredient: str, pantry_items: list[str]) -> str:
    """
    Lightweight helper for the recipe scaler/converter feature: 'I don't have
    buttermilk, what can I use instead given what's in my pantry?'
    """
    settings = get_settings()
    client = _client()

    prompt = (
        f"I'm cooking and don't have '{missing_ingredient}'. "
        f"Here's what's in my pantry: {', '.join(pantry_items) if pantry_items else 'nothing else notable'}. "
        "In one or two short sentences, suggest the best substitution, preferring something "
        "from my pantry if it would work. Be specific about ratios if relevant (e.g. '1 cup milk + 1 tbsp lemon juice')."
    )

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    text_blocks = [block.text for block in response.content if block.type == "text"]
    return "".join(text_blocks).strip()
