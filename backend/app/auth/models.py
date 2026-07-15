"""
Staff user model.

Deliberately minimal -- one flat table, no roles/permissions. This app is
used by a handful of staff/volunteers at a single food bank; anyone with an
account can do anything an account can do. If this ever needs to scale to
multiple organizations or role-based access, that's a real redesign, not an
incremental add.
"""
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
