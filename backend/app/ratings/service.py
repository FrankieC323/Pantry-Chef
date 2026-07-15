"""
Ratings service.

`summarize_preferences()` is the bridge between the ratings feature and the
AI matcher: it turns rating history into a short natural-language summary
that gets injected into Claude's prompt context, so suggestions improve over
time without needing a separate ML training pipeline. This is intentionally
simple (heuristic, not learned) -- a good "future work" talking point is
swapping this for an actual preference-learning model later.
"""
from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.ratings.models import Rating
from app.ratings.schemas import RatingCreate
from app.recipes.models import Recipe, RecipeIngredient


def create_or_update_rating(db: Session, data: RatingCreate) -> Rating:
    existing = db.scalars(select(Rating).where(Rating.recipe_id == data.recipe_id)).first()
    if existing:
        existing.stars = data.stars
        existing.notes = data.notes
        existing.would_make_again = data.would_make_again
        db.commit()
        db.refresh(existing)
        return existing

    rating = Rating(**data.model_dump())
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


def list_ratings(db: Session) -> list[Rating]:
    return list(db.scalars(select(Rating).order_by(Rating.rated_at.desc())))


def summarize_preferences(db: Session, min_ratings: int = 3) -> str | None:
    """
    Builds a short free-text summary like:
    "User tends to rate spicy/Thai dishes highly (avg 4.7/5). Has given low
    ratings to recipes containing cilantro (avg 2.0/5). Generally prefers
    quick recipes under 30 minutes."

    Returns None if there isn't enough rating history yet to say anything
    meaningful -- the matcher then just omits personalization from the prompt.
    """
    ratings = list_ratings(db)
    if len(ratings) < min_ratings:
        return None

    stmt = (
        select(Rating, Recipe)
        .join(Recipe, Rating.recipe_id == Recipe.id)
        .options(joinedload(Recipe.ingredients))
    )
    rows = db.execute(stmt).all()
    if not rows:
        return None

    ingredient_scores: dict[str, list[int]] = {}
    for rating, recipe in rows:
        for ing in recipe.ingredients:
            ingredient_scores.setdefault(ing.name, []).append(rating.stars)

    liked = []
    disliked = []
    for name, scores in ingredient_scores.items():
        if len(scores) < 2:
            continue
        avg = sum(scores) / len(scores)
        if avg >= 4.0:
            liked.append((name, avg))
        elif avg <= 2.5:
            disliked.append((name, avg))

    liked.sort(key=lambda x: -x[1])
    disliked.sort(key=lambda x: x[1])

    parts = []
    if liked:
        top_liked = ", ".join(f"{name} (avg {avg:.1f}/5)" for name, avg in liked[:5])
        parts.append(f"Tends to rate recipes containing these ingredients highly: {top_liked}.")
    if disliked:
        top_disliked = ", ".join(f"{name} (avg {avg:.1f}/5)" for name, avg in disliked[:5])
        parts.append(f"Tends to rate recipes containing these ingredients poorly: {top_disliked}.")

    overall_avg = sum(r.stars for r, _ in rows) / len(rows)
    parts.append(f"Overall average rating across {len(ratings)} rated recipes: {overall_avg:.1f}/5.")

    return " ".join(parts) if parts else None
