"""Rating model -- one rating per (recipe) per user. Single-user app for now, no auth/user table yet."""
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint("recipe_id", name="uq_rating_per_recipe"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recipe_id: Mapped[str] = mapped_column(ForeignKey("recipes.id"), nullable=False)
    stars: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # e.g. "too spicy", "would make again"
    would_make_again: Mapped[bool | None] = mapped_column(nullable=True)
    rated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
