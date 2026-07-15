"""Pydantic schemas for the pantry API (request/response shapes)."""
from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict

from app.pantry.models import IngredientCategory, Unit


class PantryItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(default=1.0, gt=0)
    unit: Unit = Unit.piece
    category: IngredientCategory = IngredientCategory.other
    expiration_date: date | None = None


class PantryItemCreate(PantryItemBase):
    pass


class PantryItemUpdate(BaseModel):
    name: str | None = None
    quantity: float | None = Field(default=None, gt=0)
    unit: Unit | None = None
    category: IngredientCategory | None = None
    expiration_date: date | None = None


class PantryItemOut(PantryItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    added_at: datetime
    updated_at: datetime
    days_until_expiration: int | None = None


class BulkImportRequest(BaseModel):
    # Raw pasted text -- a tab-separated block copied from Excel/Sheets, a
    # CSV-style paste, or just a plain list of item names, one per line.
    raw_text: str = Field(..., min_length=1)


class SkippedRow(BaseModel):
    line: str
    reason: str


class BulkImportResult(BaseModel):
    created: list[PantryItemOut]
    warnings: list[SkippedRow]  # created, but something in the row needed a fallback
    skipped: list[SkippedRow]  # not created at all
