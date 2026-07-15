"""Pantry CRUD endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.pantry import bulk_import, service
from app.pantry.schemas import (
    BulkImportRequest,
    BulkImportResult,
    PantryItemCreate,
    PantryItemOut,
    PantryItemUpdate,
    SkippedRow,
)

router = APIRouter(prefix="/api/pantry", tags=["pantry"])
settings = get_settings()


def _to_out(item) -> PantryItemOut:
    # PantryItemOut.days_until_expiration shares its name with the ORM
    # model's days_until_expiration() *method*, so from_attributes picks up
    # the bound method instead of calling it. Build the dict explicitly
    # instead of relying on model_validate's attribute auto-pickup.
    return PantryItemOut(
        id=item.id,
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        category=item.category,
        expiration_date=item.expiration_date,
        added_at=item.added_at,
        updated_at=item.updated_at,
        days_until_expiration=item.days_until_expiration(),
    )


@router.get("", response_model=list[PantryItemOut])
def list_pantry(db: Session = Depends(get_db)):
    return [_to_out(i) for i in service.list_items(db)]


@router.post("", response_model=PantryItemOut, status_code=201)
def add_pantry_item(payload: PantryItemCreate, db: Session = Depends(get_db)):
    item = service.create_item(db, payload)
    return _to_out(item)


# NOTE: this static route must be declared BEFORE /{item_id} below, otherwise
# FastAPI will match "expiring-soon" as a path parameter and try to look it
# up as an item ID.
@router.get("/expiring-soon", response_model=list[PantryItemOut])
def expiring_soon(db: Session = Depends(get_db)):
    items = service.get_expiring_soon(db, settings.expiring_soon_days)
    return [_to_out(i) for i in items]


# Same ordering note as above -- "bulk" must come before /{item_id}.
@router.post("/bulk", response_model=BulkImportResult)
def bulk_import_pantry(payload: BulkImportRequest, db: Session = Depends(get_db)):
    """
    Paste a tab-separated block from Excel/Google Sheets, a CSV-style paste,
    or a plain newline list of item names. Best-effort: rows that are missing
    or malformed fields still get created with a sane default (reported as a
    warning); only a genuinely empty item name is skipped entirely.
    """
    parsed_rows = bulk_import.parse_bulk_pantry_text(payload.raw_text)

    to_create: list[PantryItemCreate] = []
    row_warnings: list[SkippedRow] = []
    row_skipped: list[SkippedRow] = []

    for row in parsed_rows:
        if row.item is None:
            row_skipped.append(SkippedRow(line=row.raw_line, reason="; ".join(row.warnings)))
            continue
        to_create.append(row.item)
        if row.warnings:
            row_warnings.append(SkippedRow(line=row.raw_line, reason="; ".join(row.warnings)))

    created = service.bulk_create_items(db, to_create) if to_create else []

    return BulkImportResult(
        created=[_to_out(i) for i in created],
        warnings=row_warnings,
        skipped=row_skipped,
    )


@router.patch("/{item_id}", response_model=PantryItemOut)
def update_pantry_item(item_id: str, payload: PantryItemUpdate, db: Session = Depends(get_db)):
    item = service.update_item(db, item_id, payload)
    if item is None:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    return _to_out(item)


@router.delete("/{item_id}", status_code=204)
def delete_pantry_item(item_id: str, db: Session = Depends(get_db)):
    if not service.delete_item(db, item_id):
        raise HTTPException(status_code=404, detail="Pantry item not found")
