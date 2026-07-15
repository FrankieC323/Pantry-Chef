"""
Preset catalog of common food-bank stock items, grouped by category.

Deliberately NOT the same as pantry.models.IngredientCategory -- a home
pantry's free-text search doesn't fit a volunteer doing a fast shelf
check during a shift. This is a fixed checkbox list of what a typical
food bank actually stocks, so "marking today's inventory" takes seconds.

Single source of truth: the frontend fetches this from /api/foodbank/items
rather than hardcoding its own copy, so adding an item here is enough.
"""

CATALOG: dict[str, list[str]] = {
    "Canned Protein": [
        "canned black beans",
        "canned pinto beans",
        "canned chickpeas",
        "canned tuna",
        "canned chicken",
        "peanut butter",
    ],
    "Grains & Starch": [
        "white rice",
        "brown rice",
        "pasta",
        "instant oats",
        "cornmeal",
        "bread",
    ],
    "Canned Vegetables": [
        "canned corn",
        "canned green beans",
        "canned tomatoes",
        "canned mixed vegetables",
        "tomato sauce",
    ],
    "Dairy & Alternatives": [
        "shelf-stable milk",
        "powdered milk",
        "cheese",
        "eggs",
    ],
    "Fresh Produce": [
        "onions",
        "potatoes",
        "carrots",
        "bananas",
        "apples",
    ],
    "Pantry Staples": [
        "cooking oil",
        "salt",
        "sugar",
        "flour",
        "canned soup",
    ],
}

DIETARY_FLAGS: list[str] = [
    "vegetarian",
    "vegan",
    "halal",
    "kosher",
    "low_sodium",
    "nut_free",
    "dairy_free",
]

EQUIPMENT_CONSTRAINTS: list[str] = [
    "no_oven",
    "stovetop_only",
    "microwave_only",
    "no_fridge",
]
