"""
Pantry item model.

A pantry item represents one ingredient the user currently has on hand,
with an optional expiration date used to prioritize "use it before it
goes bad" recipe suggestions.
"""
import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, Float, Date, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class IngredientCategory(str, enum.Enum):
    produce = "produce"
    dairy = "dairy"
    meat_seafood = "meat_seafood"
    grain_starch = "grain_starch"
    spice_condiment = "spice_condiment"
    canned_jarred = "canned_jarred"
    frozen = "frozen"
    baking = "baking"
    beverage = "beverage"
    other = "other"


class Unit(str, enum.Enum):
    g = "g"
    kg = "kg"
    ml = "ml"
    l = "l"
    tsp = "tsp"
    tbsp = "tbsp"
    cup = "cup"
    fl_oz = "fl_oz"
    oz = "oz"
    lb = "lb"
    piece = "piece"  # for countable items like "3 eggs"
    pinch = "pinch"


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    unit: Mapped[Unit] = mapped_column(Enum(Unit), nullable=False, default=Unit.piece)
    category: Mapped[IngredientCategory] = mapped_column(
        Enum(IngredientCategory), nullable=False, default=IngredientCategory.other
    )
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def days_until_expiration(self) -> int | None:
        if self.expiration_date is None:
            return None
        return (self.expiration_date - date.today()).days
