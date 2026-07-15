"""Ratings endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ratings import service
from app.ratings.schemas import RatingCreate, RatingOut

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


@router.post("", response_model=RatingOut)
def rate_recipe(payload: RatingCreate, db: Session = Depends(get_db)):
    """Creates a rating, or updates it if this recipe was already rated (one rating per recipe)."""
    return service.create_or_update_rating(db, payload)


@router.get("", response_model=list[RatingOut])
def list_ratings(db: Session = Depends(get_db)):
    return service.list_ratings(db)
