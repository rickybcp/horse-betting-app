# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this app is

A family horse-racing betting game ("Lekours"). Users pick horses across race day, and a scoring system awards points based on odds. One bet per day can be marked as a "banker" which doubles the user's total daily score if correct.

## Running the app

**Backend** (from repo root, with venv activated):
```bash
python server.py
```

**Frontend** (from `horse-betting-frontend/`):
```bash
npm start
```

**Install backend deps:**
```bash
pip install -r requirements.txt
```

**Install frontend deps:**
```bash
cd horse-betting-frontend && npm install
```

## Backend architecture

The backend is a Flask API deployed on Render. All routes delegate to a single shared `DataService` instance — routes themselves contain no business logic.

```
server.py              # App factory (create_app). Reads DATABASE_URL env var.
database.py            # Creates shared SQLAlchemy db instance
models.py              # 5 models: User, Race, Horse, Bet, UserScore
services/
  __init__.py          # Instantiates and exports shared data_service singleton
  data_service.py      # All DB operations — the only place that touches the DB
routes/
  users.py             # /api/users
  races.py             # /api/races — includes scraping and result entry
  betting.py           # /api/bet, /api/banker, /api/bets, /api/bankers
  race_days.py         # /api/race-days — leaderboard, historical data
  admin.py             # /api/admin — user management, data reset
utils/
  smspariaz_scraper.py # Selenium + BeautifulSoup scraper for race/horse data
  results_scraper.py   # Placeholder — results scraping not yet implemented
```

**Import order matters** in `server.py` to avoid circular imports: `database.py` → `init_db(app)` → then models and routes are imported inside `create_app()`.

## Database

- PostgreSQL on Render free tier
- Connection string injected automatically by Render as `DATABASE_URL`
- Render provides `postgres://` prefix; `server.py` rewrites it to `postgresql://` for SQLAlchemy
- Tables are created automatically via `create_tables(app)` on startup when run directly
- **Render free PostgreSQL expires after 90 days** — needs recreation when it does

## Scoring rules

Points per winning bet:
- odds ≥ 10 → 3 points
- odds ≥ 5 → 2 points
- otherwise → 1 point

If the user's banker bet wins, their entire day's score is doubled.

## Frontend architecture

React 19 SPA with Tailwind CSS, deployed separately (static site).

- `App.js` — root component, holds all shared state (users, races, bets, bankers, selectedRaceDay, selectedUserId), passes everything down as props
- `src/components/` — one file per tab: `RaceDayTab`, `UserBetsTab`, `LeaderboardTab`, `AdminTab`, `HomePage`
- API base URL switches automatically: `localhost:5000` in development, `horse-betting-backend.onrender.com` in production

## Environment variables

| Variable | Where set | Purpose |
|---|---|---|
| `DATABASE_URL` | Render (auto-injected) | PostgreSQL connection string |
| `PORT` | Render (auto-injected) | Flask listening port |

No `.env` file is needed in production. Locally, create a `.env` with `DATABASE_URL` pointing to your dev database.

## Known incomplete areas

- `utils/results_scraper.py` is a placeholder — scraping race results from smspariaz.com is not implemented
- Admin tab has file-editing UI state props (`backendFiles`, `fileContent`, etc.) that are wired up but the backend `/api/admin/files` endpoint returns a 404-style error since the app now uses a database instead of files
