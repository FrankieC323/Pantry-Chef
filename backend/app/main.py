"""
PantryChef API entrypoint.

Run locally with:
    uvicorn app.main:app --reload

Swagger docs available at http://localhost:8000/docs once running.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.session import Base, engine
from app.auth.security import get_current_user

# import models so Base.metadata knows about them before create_all()
from app.auth import models as auth_models  # noqa: F401
from app.pantry import models as pantry_models  # noqa: F401
from app.recipes import models as recipe_models  # noqa: F401
from app.ratings import models as rating_models  # noqa: F401
from app.foodbank import models as foodbank_models  # noqa: F401

from app.auth.routes import router as auth_router
from app.pantry.routes import router as pantry_router
from app.recipes.routes import router as recipes_router
from app.matcher.routes import router as matcher_router
from app.ratings.routes import router as ratings_router
from app.scaler.routes import router as scaler_router
from app.foodbank.routes import router as foodbank_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev convenience: auto-create tables on startup. For production, swap
    # this for Alembic migrations (alembic/ dir is already scaffolded).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="PantryChef API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# auth itself is public (you need to be able to log in before you have a
# token); every feature router below requires a valid staff session.
app.include_router(auth_router)

_auth_required = [Depends(get_current_user)]
app.include_router(pantry_router, dependencies=_auth_required)
app.include_router(recipes_router, dependencies=_auth_required)
app.include_router(matcher_router, dependencies=_auth_required)
app.include_router(ratings_router, dependencies=_auth_required)
app.include_router(scaler_router, dependencies=_auth_required)
app.include_router(foodbank_router, dependencies=_auth_required)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
