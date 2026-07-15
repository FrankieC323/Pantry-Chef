"""Food bank endpoints -- staff-facing recipe card generator."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.foodbank import service
from app.foodbank.catalog import CATALOG, DIETARY_FLAGS, EQUIPMENT_CONSTRAINTS
from app.foodbank.schemas import (
    FoodBankGenerateRequest,
    FoodBankGenerateResponse,
    GenerationLogOut,
    RecipeCard,
)

router = APIRouter(prefix="/api/foodbank", tags=["foodbank"])


@router.get("/items")
def get_catalog():
    """Preset checkbox catalog + available flags, so the frontend has one source of truth."""
    return {
        "categories": CATALOG,
        "dietary_flags": DIETARY_FLAGS,
        "equipment_constraints": EQUIPMENT_CONSTRAINTS,
    }


@router.post("/generate", response_model=FoodBankGenerateResponse)
def generate(payload: FoodBankGenerateRequest, db: Session = Depends(get_db)):
    """Turn today's checked-off stock into a batch of printable recipe cards, and log it."""
    result, was_mocked = service.generate_cards(payload)
    raw_cards = result.get("cards", [])
    cards = [RecipeCard(**card) for card in raw_cards]
    service.save_generation_log(db, payload, raw_cards, was_mocked)
    return FoodBankGenerateResponse(cards=cards, was_mocked=was_mocked)


# NOTE: this static route must be declared BEFORE any /{log_id}-style route
# is ever added below, same reasoning as pantry/routes.py's expiring-soon.
@router.get("/history", response_model=list[GenerationLogOut])
def history(db: Session = Depends(get_db)):
    """Past batches, most recent first -- lets staff revisit a prior day's cards for free."""
    return service.list_generation_logs(db)
