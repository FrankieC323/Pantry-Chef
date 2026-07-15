"""
Parser for bulk pantry input: a paste from Excel/Google Sheets (tab-separated
when copied), a CSV-style paste, or just a plain list of item names.

Deliberately forgiving rather than strict -- a volunteer pasting a
spreadsheet range shouldn't get a wall of errors over a messy unit string.
Anything we can't confidently parse falls back to a sane default (quantity 1,
unit "piece", category "other") and gets reported back as a warning rather
than rejected, so the caller can decide whether to fix it up after.
"""
from datetime import datetime

from app.pantry.schemas import PantryItemCreate

_CATEGORY_SYNONYMS = {
    "produce": "produce", "fruit": "produce", "vegetable": "produce", "veggies": "produce",
    "dairy": "dairy", "milk": "dairy",
    "meat_seafood": "meat_seafood", "meat": "meat_seafood", "seafood": "meat_seafood", "fish": "meat_seafood",
    "grain_starch": "grain_starch", "grain": "grain_starch", "grains": "grain_starch", "starch": "grain_starch",
    "spice_condiment": "spice_condiment", "spice": "spice_condiment", "condiment": "spice_condiment",
    "canned_jarred": "canned_jarred", "canned": "canned_jarred", "jarred": "canned_jarred", "can": "canned_jarred",
    "frozen": "frozen",
    "baking": "baking",
    "beverage": "beverage", "beverages": "beverage", "drink": "beverage", "drinks": "beverage",
    "other": "other",
}

_UNIT_SYNONYMS = {
    "g": "g", "gram": "g", "grams": "g",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "ml": "ml", "milliliter": "ml", "milliliters": "ml",
    "l": "l", "liter": "l", "liters": "l",
    "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "tbsp": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
    "cup": "cup", "cups": "cup",
    "fl_oz": "fl_oz", "floz": "fl_oz", "fl oz": "fl_oz",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    "piece": "piece", "pieces": "piece", "pc": "piece", "each": "piece", "count": "piece", "ct": "piece",
    "pinch": "pinch",
}

_HEADER_TOKENS = {"name", "item", "ingredient", "product"}

_DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%B %d %Y", "%b %d %Y"]


class ParsedRow:
    def __init__(self, item: PantryItemCreate | None, warnings: list[str], raw_line: str):
        self.item = item
        self.warnings = warnings
        self.raw_line = raw_line


def _split_line(line: str) -> list[str]:
    if "\t" in line:
        return [cell.strip() for cell in line.split("\t")]
    # A comma-separated paste is ambiguous with "2, chopped" style item
    # names, so only treat as CSV if it looks like a clean 2+ column row.
    if line.count(",") >= 1 and line.count(",") <= 4:
        cells = [cell.strip() for cell in line.split(",")]
        if all(cells):
            return cells
    return [line.strip()]


def _parse_quantity(raw: str) -> tuple[float, str | None]:
    if not raw:
        return 1.0, None
    try:
        return float(raw), None
    except ValueError:
        return 1.0, f"couldn't parse quantity '{raw}', defaulted to 1"


def _parse_unit(raw: str) -> tuple[str, str | None]:
    if not raw:
        return "piece", None
    key = raw.strip().lower()
    if key in _UNIT_SYNONYMS:
        return _UNIT_SYNONYMS[key], None
    return "piece", f"unrecognized unit '{raw}', defaulted to piece"


def _parse_category(raw: str) -> tuple[str, str | None]:
    if not raw:
        return "other", None
    key = raw.strip().lower().replace(" ", "_")
    if key in _CATEGORY_SYNONYMS:
        return _CATEGORY_SYNONYMS[key], None
    return "other", f"unrecognized category '{raw}', defaulted to other"


def _parse_date(raw: str) -> tuple[str | None, str | None]:
    if not raw:
        return None, None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw.strip(), fmt).date().isoformat(), None
        except ValueError:
            continue
    return None, f"couldn't parse expiration date '{raw}', left blank"


def parse_bulk_pantry_text(raw_text: str) -> list[ParsedRow]:
    rows: list[ParsedRow] = []

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue

        cells = _split_line(line)

        # Skip an obvious header row (only checked on the first non-empty line
        # per call site, but cheap enough to just check every line).
        if cells[0].strip().lower() in _HEADER_TOKENS:
            continue

        name = cells[0].strip()
        if not name:
            rows.append(ParsedRow(None, ["empty item name"], line))
            continue

        warnings: list[str] = []

        quantity, w = _parse_quantity(cells[1] if len(cells) > 1 else "")
        if w:
            warnings.append(w)
        unit, w = _parse_unit(cells[2] if len(cells) > 2 else "")
        if w:
            warnings.append(w)
        category, w = _parse_category(cells[3] if len(cells) > 3 else "")
        if w:
            warnings.append(w)
        expiration_date, w = _parse_date(cells[4] if len(cells) > 4 else "")
        if w:
            warnings.append(w)

        item = PantryItemCreate(
            name=name,
            quantity=quantity,
            unit=unit,
            category=category,
            expiration_date=expiration_date,
        )
        rows.append(ParsedRow(item, warnings, line))

    return rows
