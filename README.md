# PantryChef

A full-stack recipe app that suggests what to cook based on what's actually in your pantry — prioritizing ingredients that are about to expire, explaining smart substitutions, and learning your taste over time from ratings. When nothing in the recipe cache fits well, it generates a new recipe on the fly.

## Why this exists

Built as a portfolio project to demonstrate full-stack development with applied LLM reasoning — not just an API wrapper, but a system where the AI does real work: fuzzy ingredient matching, substitution reasoning, and recipe generation, on top of a normal CRUD app with a real database.

## Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite (swappable for Postgres)
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, React Query, React Router
- **AI**: Claude API (Anthropic) for ingredient matching, substitution reasoning, and recipe generation
- **Recipe data**: Spoonacular API (primary) + a BeautifulSoup scraper reading Schema.org Recipe JSON-LD (supplemental) + Claude-generated recipes (fallback)

## Features

1. **Pantry tracker** — CRUD for ingredients with quantity, unit, category, and expiration date. An `/expiring-soon` endpoint surfaces what needs to be used first.
2. **AI-enhanced recipe matcher** — sends the current pantry plus a pre-filtered candidate set of cached recipes to Claude, which ranks matches, explains substitutions in plain language, and generates a new recipe when nothing in the cache is a good fit.
3. **Recipe scaler / unit converter** — pure deterministic logic (no AI needed) to scale ingredient quantities to a target serving size and convert between compatible units.
4. **Personal ratings** — rate recipes 1–5 stars; rating history is summarized into a short preference profile that's fed back into the matcher's prompt, so suggestions improve over time without a separate training pipeline.

## Project structure

```
pantry-chef/
├── backend/
│   ├── app/
│   │   ├── pantry/      # pantry CRUD + expiration logic
│   │   ├── recipes/     # recipe models, Spoonacular client, caching
│   │   ├── matcher/     # Claude integration -- the core AI feature
│   │   ├── ratings/     # rating CRUD + preference summarization
│   │   ├── scaler/      # serving-size scaling + unit conversion
│   │   ├── scrapers/    # supplemental recipe scraper (JSON-LD based)
│   │   ├── core/        # settings
│   │   └── db/          # SQLAlchemy session setup
│   └── tests/
└── frontend/
    └── src/
        ├── pages/        # Pantry, Suggestions, History
        ├── components/   # shared UI (cards, ratings, scaler widget)
        ├── api/          # typed fetch wrappers per backend module
        └── types/        # TypeScript types mirroring backend schemas
```

## Running locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then fill in ANTHROPIC_API_KEY and SPOONACULAR_API_KEY
uvicorn app.main:app --reload
```

API docs (Swagger UI) at `http://localhost:8000/docs`.

- Get a free Anthropic API key: https://console.anthropic.com/
- Get a free Spoonacular API key (150 requests/day): https://spoonacular.com/food-api/console#Dashboard

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Opens at `http://localhost:5173`. Data is stored in the backend's SQLite database, so your pantry, recipes, and ratings persist across browser restarts — there's no browser storage involved.

### Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

## Notes for future development

- **Auth**: currently single-user, no login. Ratings/pantry are global, not per-user.
- **Image-based fridge scanner**: planned next feature — snap a photo of your fridge, use a vision model to identify ingredients, and feed that straight into the matcher.
- **Preference learning**: the rating → preference-summary pipeline in `ratings/service.py` is intentionally simple (heuristic averaging). A natural next step is replacing it with a small trained model.
- **Production DB**: swap `DATABASE_URL` in `.env` to a Postgres connection string; the SQLAlchemy models don't need to change.
