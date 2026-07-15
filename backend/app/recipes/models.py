"""
Recipe models.

A Recipe can originate from Spoonacular (source="spoonacular"), our scraper
(source="scraped"), or be generated on-demand by Claude (source="generated").
RecipeIngredient is a normalized line item so the matcher can do set-overlap
math against pantry items without re-parsing free text every time.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Float, Integer, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RecipeSource(str, enum.Enum):
    spoonacular = "spoonacular"
    scraped = "scraped"
    generated = "generated"


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source: Mapped[RecipeSource] = mapped_column(Enum(RecipeSource), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    servings: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    ready_in_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    cached_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recipe_id: Mapped[str] = mapped_column(ForeignKey("recipes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)  # normalized, e.g. "onion"
    raw_text: Mapped[str] = mapped_column(String, nullable=False)  # e.g. "1/2 cup diced yellow onion"
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String, nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
