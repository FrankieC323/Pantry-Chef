"""Pydantic schemas for ratings."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RatingCreate(BaseModel):
    recipe_id: str
    stars: int = Field(..., ge=1, le=5)
    notes: str | None = None
    would_make_again: bool | None = None


class RatingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recipe_id: str
    stars: int
    notes: str | None
    would_make_again: bool | None
    rated_at: datetime
