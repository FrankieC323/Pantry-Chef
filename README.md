# PantryChef

I built this because I kept standing in front of my kitchen with no idea what to make, while stuff in the back of the fridge quietly went bad. So PantryChef started as a pantry tracker with an AI-powered recipe matcher: track what you've got, get suggestions that use it up before it expires, rate what you actually cooked so it gets better at guessing what you'll like.

Then I realized the actual hard part of the app (reasoning well about what you can make from a fixed, limited set of ingredients) wasn't really about *my* fridge specifically. A food bank asks almost the exact same question every day, just at a bigger scale and with higher stakes. So there are two modes now:

- **Personal Mode** — the original idea. Track your pantry, get AI-matched recipes that prioritize what's about to expire, rate what you cook.
- **Food Bank Mode** — built for staff and volunteers. Check off what's on the shelves today, and get back a batch of printable, bilingual (English/Spanish) recipe cards to send home with the food boxes.

Same codebase, same login system, both modes. One thing worth being upfront about: each deployment is meant for one organization. This isn't some shared platform where multiple food banks all use the same database. If two different food banks want this, they each run their own copy.

## If you're a food bank looking at this

You're probably not the person who's going to touch the code, so here's the short version:

1. Somebody technical needs to deploy it once (see [Deploying](#deploying) below). After that it's just a website your staff log into.
2. Everyone who'll use it should have their own account: first-time setup is a normal sign-up screen, or an existing staff member can just tell someone their login works already.
3. Day to day, you're living in Food Bank Mode: check off what's actually on the shelf, flag anything that's about to expire or that you're overstocked on (the AI will try to build recipes around those first), set any dietary or equipment limits that matter, and hit generate. Print the cards, hand them out. Everything you generate gets saved automatically, so you can look back at last week's batch without regenerating it.
4. It's cheap to run: see [API costs](#api-costs) if you're curious how cheap.

## What's actually in here

1. **Pantry tracker** (Personal Mode) — add/edit/remove ingredients with quantity, unit, category, expiration date. You can also paste in a whole list at once instead of typing items one by one (see bulk import below).
2. **AI recipe matcher** (Personal Mode) — this is the part I'm most proud of. It sends your current pantry plus a filtered set of candidate recipes to Claude, which actually ranks how well each one fits, explains substitutions in plain language when you're missing something, and writes a brand-new recipe on the spot if nothing already in the cache is a good match.
3. **Recipe scaler** — just math, scales ingredient amounts to whatever serving size you need and converts between units. No AI needed for this one, it doesn't have to be smart, it just has to be right.
4. **Ratings** — rate what you cooked 1–5 stars, and a short summary of your taste gets folded back into future matching.
5. **Food Bank Mode** — the newer half of the app. Staff pick from a preset catalog of common food-bank items (way faster than typing during a shift), flag priority items, set constraints, and generate a batch of bilingual printable cards. Every batch gets logged.
6. **Bulk pantry import** — paste a range straight out of Excel or Google Sheets, a comma-separated table, or just a plain list of names, and it figures out what it can. If it can't confidently parse something (a weird unit, say), it doesn't just fail: it defaults to something sensible and tells you what it guessed.
7. **Real staff accounts** — not one shared password everybody uses. Actual per-person logins, hashed passwords, and every page in the app requires being signed in.

## Accounts and keeping your API keys private

### Accounts

When you first deploy this, sign-up is open by default (`ALLOW_OPEN_REGISTRATION=true`) so your first handful of staff can create their own accounts. **Turn that off once they're set up** — flip `ALLOW_OPEN_REGISTRATION` to `false` in your environment variables and redeploy, and the sign-up screen stops accepting new accounts from randoms who find the URL.

Heads up that there's no admin-vs-volunteer distinction right now: any account can do anything in the app. For a small internal staff tool that felt like the right amount of complexity to build; if you actually need tiered permissions down the line, that's a real feature to add, not a setting to flip.

Sessions last about 12 hours, roughly one shift, so people log back in the next day instead of staying signed in forever.

### Keeping your API keys private

There are two secrets this app cares about: your Anthropic API key (this is what actually powers the AI) and a JWT secret key (this is what signs staff login sessions so people can't fake being logged in). Neither should ever end up somewhere public. Here's how I've tried to make that hard to mess up, and what's still on you to double-check:

- Nothing is hardcoded: every secret is read from environment variables, never written into the code itself.
- `.env` is already in `.gitignore`, so a normal `git add -A` will never accidentally pick it up. Only `.env.example` gets committed, and that file just has the variable *names*, not real values.
- The real values live in two places: a `.env` file on your own machine that you create yourself (copy `.env.example` and fill it in), and your hosting platform's environment variable settings once you deploy. Never in a file that actually gets pushed anywhere.
- Before your first push, just run `git status` and make sure `.env` isn't sitting there as a tracked file. And if it somehow already got committed at some point in the past, deleting it in a later commit isn't enough, it's still sitting in your git history where anyone can find it. If that happens, the fix is to rotate the key (make a new one, revoke the old one in the Anthropic Console), not to try to scrub history.
- Generate a real JWT secret before deploying anywhere that matters: the placeholder in `.env.example` is obviously fake on purpose, so you notice if you forgot to replace it:
```bash
  python -c "import secrets; print(secrets.token_hex(32))"
```
  Whoever has that value can forge a login for literally any username, so treat it like a password, not a config detail.

### API costs

I made a point of not hand-waving this. Food Bank Mode defaults to Claude Haiku, the cheapest current model, and this is exactly the kind of bounded task it's good at (short list of items in, a handful of recipe cards out, nothing fancy needed). One generation costs roughly a cent. If you're using it the way it's meant to be used, once per shift to generate the day's batch and not once per person, a modest budget goes a genuinely long way. Set a hard spending cap in the [Anthropic Console](https://console.anthropic.com/) so you never have to worry about a bug or a weird traffic spike blowing past what you meant to spend.

And while you're actually building or testing anything, set `USE_MOCK_API=true` in the backend's `.env`. It returns a fake but realistic example response instantly, no API call, no cost, so you can mess with the UI as much as you want for free, and only flip it back to real calls when you actually need to see live output.

## Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite (works fine with Postgres too if you swap the connection string)
- **Frontend**: React, TypeScript, Vite, Tailwind, React Query, React Router
- **AI**: the Claude API, used for ingredient matching, substitution reasoning, recipe generation, and the food bank cards
- **Auth**: bcrypt for password hashing, JWT for sessions
- **Recipe data** (Personal Mode): Spoonacular API is the primary source, with a small scraper reading Schema.org recipe markup as backup, and Claude generating something from scratch as a last resort if neither has a good match

## How it's organized
pantry-chef/
├── backend/
│   ├── app/
│   │   ├── auth/        # staff accounts -- hashing, JWT, login/register
│   │   ├── pantry/      # pantry CRUD, expiration logic, bulk-paste import
│   │   ├── recipes/     # recipe models, Spoonacular client, caching
│   │   ├── matcher/     # the Claude integration behind Personal Mode
│   │   ├── foodbank/    # Food Bank Mode -- catalog, Claude prompt, history
│   │   ├── ratings/     # rating CRUD + preference summarization
│   │   ├── scaler/      # serving-size scaling + unit conversion
│   │   ├── scrapers/    # backup recipe scraper
│   │   ├── core/        # settings
│   │   └── db/          # SQLAlchemy session setup
│   └── tests/
└── frontend/
└── src/
├── pages/        # Pantry, Suggestions, History, Food Bank Mode, Login
├── components/   # shared UI pieces
├── auth/         # session state, login/register/logout
├── api/          # typed fetch wrappers per backend module
└── types/        # TS types mirroring the backend schemas

## Running it locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # fill in ANTHROPIC_API_KEY, JWT_SECRET_KEY, etc.
uvicorn app.main:app --reload
```

Swagger docs show up at `http://localhost:8000/docs` once it's running.

- Free Anthropic key: https://console.anthropic.com/
- Free Spoonacular key (150 requests/day, optional; only matters for Personal Mode's recipe search): https://spoonacular.com/food-api/console#Dashboard

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Runs at `http://localhost:5173`. First thing you'll see is the login screen: make an account and you're in. Everything's stored in the backend's database, so it's all still there next time you open the browser.

### Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

## Deploying

Three separate pieces to host:

1. **Backend** — Render or Railway both work. Point either one at this repo and set your real environment variable values in their dashboard, not in a file that gets deployed. One thing that'll bite you if you're not careful: if you're using SQLite, make sure the database file lives on a persistent disk. Most free tiers use an ephemeral filesystem that wipes on every redeploy, and you do not want to find that out after you've got real data in there. A free hosted Postgres from either platform sidesteps the problem entirely.
2. **Frontend** — Vercel or Netlify. Build command is `npm run build`, output directory is `dist`, and point `VITE_API_BASE_URL` at wherever you deployed the backend.
3. **Domain** — both platforms hand you a free subdomain with HTTPS out of the box. A custom domain is nice but optional.

Before you actually go live with this somewhere real: generate a proper `JWT_SECRET_KEY`, set a spending cap in the Anthropic Console, and turn off open registration once your staff have accounts.

## Things I know are missing

Being honest about what's not here yet:

- **No roles.** Every account can do everything. That's fine for a small team, but it's a real gap if you need to separate what an admin can do from what a volunteer can.
- **One org per deployment.** There's no data isolation between organizations: this app assumes it's serving one food bank, not several sharing an instance.
- **No image-based scanning yet.** Snapping a photo of a shelf or a fridge and having a vision model figure out what's there instead of checking boxes by hand feels like the obvious next step.
- **The preference-learning in Personal Mode is intentionally simple** — it's basically heuristic averaging of your ratings, not a trained model. Works fine, could be smarter.
- **The food bank catalog was reasoned out, not sourced from a real food bank's actual inventory.** If you're adopting this, you'll probably want to adjust the preset item list to match what you actually stock.

## License

MIT — see [LICENSE](./LICENSE). Use it, change it, adapt it for your own food bank or organization. I'd just like to hear about it if you do.
