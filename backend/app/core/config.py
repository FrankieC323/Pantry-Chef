"""
Centralized application configuration.

All secrets/config are read from environment variables (or a local .env file
that is NOT committed to git -- see .env.example for the expected keys).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Database ---
    database_url: str = "sqlite:///./pantry_chef.db"  # swap for postgres in production

    # --- External APIs ---
    anthropic_api_key: str = ""
    spoonacular_api_key: str = ""

    # --- App behavior ---
    claude_model: str = "claude-sonnet-4-6"
    matcher_min_ingredient_overlap: float = 0.4  # 40% of recipe ingredients must be on hand
    expiring_soon_days: int = 3  # items expiring within N days get priority in suggestions

    # --- Food bank feature ---
    # Cheap, cheerful model for a bounded structured-output task (short item
    # list in, a handful of recipe cards out) -- no need for Sonnet/Opus here.
    foodbank_claude_model: str = "claude-haiku-4-5-20251001"
    # When true, /api/foodbank/generate returns the canned fixture instead of
    # calling the live API. Flip on while building/testing the UI so
    # iteration is free; flip off for real prompt tuning and the demo.
    use_mock_api: bool = False

    # --- Auth ---
    # MUST be overridden in production -- generate one with:
    #   python -c "import secrets; print(secrets.token_hex(32))"
    # and put it in backend/.env. Anyone who has this value can mint valid
    # login tokens for any username, so treat it like a password.
    jwt_secret_key: str = "dev-only-insecure-secret-change-me-before-deploying"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 12  # 12 hours -- roughly one shift
    # Once your staff accounts are created, set this to false so randoms
    # who find the URL can't self-register. There's no invite-code flow --
    # for a handful of staff, an admin creating accounts directly (e.g. via
    # the /docs Swagger UI while this is still true) is simplest.
    allow_open_registration: bool = True

    # --- CORS ---
    frontend_origin: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
