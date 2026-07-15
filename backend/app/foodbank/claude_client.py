"""
Claude API integration for food-bank recipe cards.

Deliberately its own client (separate from app.matcher.claude_client)
rather than reusing the home-pantry prompt: the constraints are different
(fixed shelf list instead of a tracked pantry, bilingual output, "assume
basically no equipment," dietary/equipment flags instead of preference
history) and the two features are likely to evolve independently.

Uses Haiku by default (see core.config.Settings.foodbank_claude_model) --
this is a bounded, structured-output task (a short ingredient list in,
a handful of recipe cards out), which is exactly what Haiku is good at,
and it's a fraction of the cost of Sonnet/Opus for a feature meant to be
run once or twice a day by a single food bank.

Mock mode: set USE_MOCK_API=true in backend/.env (or Settings.use_mock_api)
to skip the live API call entirely and return the canned fixture in
fixtures/sample_cards.json instead. Use this while building/testing the
UI so iterating on the checkbox grid, card layout, or print styling costs
nothing -- flip it off only when you actually need to see live model output
(prompt tuning, the demo walkthrough, the real thing).
"""
import json
from pathlib import Path

from anthropic import Anthropic

from app.core.config import get_settings

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_cards.json"

_SYSTEM_PROMPT = """You are helping a food bank create take-home recipe cards for \
today's distribution. You will be given:
1. A list of items on the shelves today (available_items)
2. Optionally, items flagged as near-expiry or overstocked that should be used first (priority_items)
3. Dietary flags to respect (e.g. vegetarian, halal, low_sodium, nut_free)
4. Equipment constraints to respect (e.g. no_oven, stovetop_only, microwave_only, no_fridge)
5. How many recipe cards to generate

Write for someone who may have very limited kitchen equipment and may be a \
first-time reader of a recipe. Use short sentences and simple, common words in \
BOTH English and Spanish. You may assume salt, pepper, and water are available \
even if not listed, but do NOT assume any other ingredient that isn't in \
available_items.

Always respond with ONLY valid JSON, no markdown fences, no preamble, matching \
this exact shape:
{
  "cards": [
    {
      "title_en": "string",
      "title_es": "string",
      "ingredients_en": ["list of ingredient lines, e.g. '1 can black beans, drained'"],
      "ingredients_es": ["same list, in Spanish"],
      "steps_en": ["numbered-order list of short simple steps"],
      "steps_es": ["same steps, in Spanish"],
      "dietary_tags": ["list of dietary flags this recipe satisfies, from the request's dietary_flags"],
      "uses_priority_items": true/false,
      "notes_en": "one short sentence, e.g. serving size or an equipment swap -- or empty string",
      "notes_es": "same note, in Spanish, or empty string"
    }
  ]
}

Every ingredient used in every card MUST come from available_items -- do not \
invent ingredients. Prefer recipes that use priority_items when possible, and \
mark uses_priority_items accordingly. Respect every dietary flag and equipment \
constraint given; if a recipe can't satisfy all of them, don't include it.
"""


def _client() -> Anthropic:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to backend/.env -- get a key at "
            "https://console.anthropic.com/"
        )
    return Anthropic(api_key=settings.anthropic_api_key)


def _load_fixture() -> dict:
    with open(_FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_cards(
    available_items: list[str],
    priority_items: list[str],
    dietary_flags: list[str],
    equipment_constraints: list[str],
    card_count: int,
) -> tuple[dict, bool]:
    """
    Returns (parsed_json_dict, was_mocked). Shape of parsed_json_dict matches
    _SYSTEM_PROMPT's response schema (a dict with a "cards" key) whether it
    came from the fixture or a live call, so callers don't need to care which.
    """
    settings = get_settings()

    if settings.use_mock_api:
        return _load_fixture(), True

    client = _client()
    user_message = {
        "available_items": available_items,
        "priority_items": priority_items,
        "dietary_flags": dietary_flags,
        "equipment_constraints": equipment_constraints,
        "card_count": card_count,
    }

    response = client.messages.create(
        model=settings.foodbank_claude_model,
        max_tokens=3000,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(user_message)}],
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
        return json.loads(raw_text), False
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Claude returned non-JSON output: {raw_text[:500]}") from e
