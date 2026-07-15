"""Food bank service layer -- thin wrapper so routes.py stays a plain HTTP shim."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.foodbank import claude_client
from app.foodbank.models import GenerationLog
from app.foodbank.schemas import FoodBankGenerateRequest


def generate_cards(payload: FoodBankGenerateRequest) -> tuple[dict, bool]:
    return claude_client.generate_cards(
        available_items=payload.available_items,
        priority_items=payload.priority_items,
        dietary_flags=payload.dietary_flags,
        equipment_constraints=payload.equipment_constraints,
        card_count=payload.card_count,
    )


def save_generation_log(
    db: Session,
    payload: FoodBankGenerateRequest,
    cards: list[dict],
    was_mocked: bool,
) -> GenerationLog:
    log = GenerationLog(
        available_items=payload.available_items,
        priority_items=payload.priority_items,
        dietary_flags=payload.dietary_flags,
        equipment_constraints=payload.equipment_constraints,
        card_count_requested=payload.card_count,
        cards=cards,
        was_mocked=was_mocked,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_generation_logs(db: Session, limit: int = 30) -> list[GenerationLog]:
    stmt = select(GenerationLog).order_by(GenerationLog.created_at.desc()).limit(limit)
    return list(db.scalars(stmt))
