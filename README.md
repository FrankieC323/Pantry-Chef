# PantryChef

A pantry-aware recipe app with two modes:

- **Personal Mode** — track your own pantry, get AI-matched recipe suggestions that prioritize what's about to expire, and rate what you cook so future suggestions improve.
- **Food Bank Mode** — a staff/volunteer tool for generating printable, bilingual (EN/ES) recipe cards from today's shelf stock, built for distribution alongside food boxes.

Both modes share one codebase and one login system. Multiple staff can have their own accounts; each deployment (see [Deploying](#deploying) below) serves one organization — this isn't a shared multi-tenant service where different food banks share a database, so each org runs its own copy.

## For food banks: quick orientation

If you're a food bank adopting this rather than the person who built it:

1. Someone technical (a volunteer, a board member, whoever set this up) needs to deploy it once — see [Deploying](#deploying). After that, it's a normal website.
2. Each staff member who'll use it needs their own account — created via the sign-up screen the first time, or by an admin. See [Staff accounts](#staff-accounts--api-keys).
3. Day-to-day use is **Food Bank Mode**: a volunteer checks off what's on the shelves today, optionally flags near-expiry/overstocked items to prioritize, sets any dietary or equipment constraints, and generates a batch of recipe cards to print and hand out. Past batches are saved automatically so staff can look back without regenerating anything.
4. Cost is small and controllable — see [API costs](#api-costs) below.

## Features

1. **Pantry tracker** (Personal Mode) — CRUD for ingredients with quantity, unit, category, and expiration date, plus bulk-paste import (see below).
2. **AI-enhanced recipe matcher** (Personal Mode) — sends the current pantry plus a pre-filtered candidate set of cached recipes to Claude, which ranks matches, explains substitutions in plain language, and generates a new recipe when nothing in the cache fits.
3. **Recipe scaler / unit converter** — deterministic serving-size scaling and unit conversion, no AI involved.
4. **Personal ratings** — rate recipes 1–5 stars; a short preference summary is fed back into the matcher's prompt so suggestions improve over time.
5. **Food Bank Mode** — staff check off today's in-stock items from a preset catalog, flag priority (near-expiry/overstocked) items, set dietary/equipment constraints, and generate a batch of bilingual, printable recipe cards. Every batch is logged so staff can revisit a past day's cards for free.
6. **Bulk pantry import** — paste a range copied from Excel/Google Sheets (tab-separated), a comma-separated table, or a plain list of item names, and it parses each row with sensible fallbacks (unrecognized unit → defaults to "piece" with a warning shown, not a hard failure).
7. **Staff accounts** — real per-person logins (bcrypt-hashed passwords, JWT sessions), not a single shared password. Every route in the app requires being signed in.

## Staff accounts & API keys

### Accounts

- The first time the app is deployed, sign-up is open (`ALLOW_OPEN_REGISTRATION=true`) so the first few staff can create their own accounts from the login screen.
- **Once your staff are set up, turn this off.** Set `ALLOW_OPEN_REGISTRATION=false` in the backend's environment variables and redeploy. This closes the sign-up screen to new accounts — existing staff can still log in normally.
- There's no per-account role system (admin vs. volunteer) — anyone with an account can do anything in the app. For a single food bank's internal staff tool, that's an intentional simplification, not an oversight; if you need tiered permissions later, that's a real feature to add, not a config flip.
- Sessions expire after 12 hours (roughly one shift), so staff log in again each day rather than staying signed in indefinitely.

### Keeping API keys private

This app uses two secrets: an **Anthropic API key** (powers the AI features) and a **JWT secret key** (signs staff login sessions). Both must stay private. Here's how that's enforced, and what you need to double check:

- **They're never in the code.** Every secret is read from environment variables (`ANTHROPIC_API_KEY`, `JWT_SECRET_KEY`) — never hardcoded, never committed.
- **`.env` is git-ignored.** The repo's `.gitignore` excludes `.env` and `.env.local` by name, so `git add -A` will never pick them up. Only `.env.example` (which has the variable *names* but no real values) is tracked.
- **Where real values actually live:** on your own machine, in a local `.env` file you create by copying `.env.example`. In production, in your hosting platform's environment-variable settings (Render, Railway, Vercel, etc. all have a dashboard for this) — never in a file that gets deployed alongside your code.
- **Before your first push to GitHub**, run `git status` and confirm `.env` isn't listed as a tracked file. If it somehow already got committed in the past, deleting it in a new commit isn't enough — it's still in the git history. In that case, rotate the key (generate a new one and revoke the old one in the Anthropic Console) rather than trying to scrub history.
- **The JWT secret** needs to be a real random value before you deploy anywhere real — the default in `.env.example` is an obviously-fake placeholder on purpose, so it's easy to notice if you forgot to change it. Generate one with:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
  Anyone who has this value can forge a valid login for any username, so treat it exactly like a password.

### API costs

The food bank feature defaults to **Claude Haiku**, priced per-token specifically because this is a short, bounded task (a checked-off item list in, a handful of recipe cards out) — it doesn't need a larger model. A single "generate today's batch" call costs roughly a cent. Realistic usage (one generation per shift, not per client) means a modest monthly API budget goes a long way; set a hard spending cap in the [Anthropic Console](https://console.anthropic.com/) so usage can never exceed what you intend to spend.

While developing or demoing, set `USE_MOCK_API=true` in the backend's `.env` — this returns a canned example response instantly with no API call and no cost, so you can build and test the UI for free. Set it back to `false` for real output.

## Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite (swappable for Postgres)
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, React Query, React Router
- **AI**: Claude API (Anthropic) — ingredient matching, substitution reasoning, recipe generation, and food-bank recipe cards
- **Auth**: bcrypt password hashing + JWT sessions (`python-jose`)
- **Recipe data** (Personal Mode): Spoonacular API (primary) + a BeautifulSoup scraper reading Schema.org Recipe JSON-LD (supplemental) + Claude-generated recipes (fallback)

## Project structure

```
pantry-chef/
├── backend/
│   ├── app/
│   │   ├── auth/        # staff accounts -- models, hashing, JWT, login/register routes
│   │   ├── pantry/      # pantry CRUD, expiration logic, bulk-paste import parser
│   │   ├── recipes/     # recipe models, Spoonacular client, caching
│   │   ├── matcher/     # Claude integration for Personal Mode suggestions
│   │   ├── foodbank/    # Food Bank Mode -- catalog, Claude client, generation + history
│   │   ├── ratings/     # rating CRUD + preference summarization
│   │   ├── scaler/      # serving-size scaling + unit conversion
│   │   ├── scrapers/    # supplemental recipe scraper (JSON-LD based)
│   │   ├── core/        # settings
│   │   └── db/          # SQLAlchemy session setup
│   └── tests/
└── frontend/
    └── src/
        ├── pages/        # Pantry, Suggestions, History, Food Bank Mode, Login
        ├── components/   # shared UI (cards, ratings, scaler widget, bulk import panel)
        ├── auth/          # AuthContext -- session state, login/register/logout
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
cp .env.example .env              # then fill in ANTHROPIC_API_KEY, JWT_SECRET_KEY, etc.
uvicorn app.main:app --reload
```

API docs (Swagger UI) at `http://localhost:8000/docs`.

- Get a free Anthropic API key: https://console.anthropic.com/
- Get a free Spoonacular API key (150 requests/day, optional -- only needed for Personal Mode's recipe search): https://spoonacular.com/food-api/console#Dashboard

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Opens at `http://localhost:5173`. The first screen is a login/sign-up page — create a staff account, then you're in.

### Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

## Deploying

Three pieces, each hosted separately:

1. **Backend** — Render or Railway both work well: point at this repo, set the environment variables from `.env.example` (with real values) in their dashboard, not in a file. If using SQLite, make sure the database file is on a **persistent disk** — the default ephemeral filesystem on most free tiers resets on every redeploy, which would silently wipe your pantry/history data. A free hosted Postgres instance (offered by both platforms) avoids this entirely.
2. **Frontend** — Vercel or Netlify: build command `npm run build`, output directory `dist`, set `VITE_API_BASE_URL` to your backend's deployed URL.
3. **Domain** — both frontend platforms give you a free subdomain with HTTPS automatically; a custom domain is optional.

Before going live: set a real `JWT_SECRET_KEY`, set a spending cap in the Anthropic Console, and turn off `ALLOW_OPEN_REGISTRATION` once your staff accounts exist.

## Notes for future development

- **No role-based permissions**: any account can do anything. Fine for one org's internal staff; a real limitation if you need admin/volunteer tiers.
- **Single organization per deployment**: there's one shared pantry/history per deployment, not per-user or per-org data isolation. Multiple food banks would each need their own deployment, not a shared instance.
- **Image-based fridge/shelf scanner**: a natural next feature — snap a photo, use a vision model to identify items, and feed that straight into either mode instead of manual checkboxes.
- **Preference learning** (Personal Mode): the rating → preference-summary pipeline in `ratings/service.py` is intentionally simple (heuristic averaging). A trained model is a reasonable next step.
- **Production DB**: swap `DATABASE_URL` in `.env` to a Postgres connection string; the SQLAlchemy models don't need to change.
