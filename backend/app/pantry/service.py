"""
Pantry service layer.

Keeping DB logic here (rather than inline in routes) makes it easy to unit
test and reuse -- e.g. the matcher module calls `get_expiring_soon()`
directly without going through HTTP.
"""
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.pantry.models import PantryItem
from app.pantry.schemas import PantryItemCreate, PantryItemUpdate


def create_item(db: Session, data: PantryItemCreate) -> PantryItem:
    item = PantryItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def bulk_create_items(db: Session, items: list[PantryItemCreate]) -> list[PantryItem]:
    """Single commit for the whole batch -- avoids N round trips for a pasted list."""
    rows = [PantryItem(**data.model_dump()) for data in items]
    db.add_all(rows)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def list_items(db: Session) -> list[PantryItem]:
    return list(db.scalars(select(PantryItem).order_by(PantryItem.expiration_date.asc().nulls_last())))


def get_item(db: Session, item_id: str) -> PantryItem | None:
    return db.get(PantryItem, item_id)


def update_item(db: Session, item_id: str, data: PantryItemUpdate) -> PantryItem | None:
    item = db.get(PantryItem, item_id)
    if item is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: str) -> bool:
    item = db.get(PantryItem, item_id)
    if item is None:
        return False
    db.delete(item)
    db.commit()
    return True


def get_expiring_soon(db: Session, within_days: int) -> list[PantryItem]:
    """Items expiring within `within_days` days (or already expired)."""
    cutoff = date.today() + timedelta(days=within_days)
    stmt = (
        select(PantryItem)
        .where(PantryItem.expiration_date.is_not(None))
        .where(PantryItem.expiration_date <= cutoff)
        .order_by(PantryItem.expiration_date.asc())
    )
    return list(db.scalars(stmt))
