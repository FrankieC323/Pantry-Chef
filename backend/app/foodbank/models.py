"""
Generation log model.

Every time staff hit "Generate today's cards," we save what was checked off
and what came back. This is what makes the feature auditable for the
application writeup ("we generated N batches over M days, here's what
they looked like") and lets staff glance back at a previous day's cards
without regenerating (and re-spending) anything.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class GenerationLog(Base):
    __tablename__ = "foodbank_generation_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    available_items: Mapped[list] = mapped_column(JSON, nullable=False)
    priority_items: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    dietary_flags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    equipment_constraints: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    card_count_requested: Mapped[int] = mapped_column(Integer, nullable=False)

    # Full card payload (title/ingredients/steps in both languages, tags, notes)
    # stored as-is so history can render without re-deriving anything.
    cards: Mapped[list] = mapped_column(JSON, nullable=False)
    was_mocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
