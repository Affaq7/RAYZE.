# RAYZE Backend (Phase 1)

FastAPI backend for RAYZE, a media marketing agency. This is a first-phase
foundation: Portfolio, Reviews, Careers (postings + applications), and
Contact submissions, backed by Supabase Postgres, with Supabase Auth used for
admin login. Home/About/Services content stays frontend-driven for now.

## Stack

- FastAPI (async) + Uvicorn
- SQLAlchemy 2.0 (async, via asyncpg) talking directly to Supabase Postgres
- Alembic migrations
- Supabase Auth — FastAPI verifies Supabase-issued JWTs against the project's published JWKS (`PyJWT`), it does not implement its own auth or store a fixed JWT secret
- Resend for transactional email
- Supabase Storage for portfolio images (public) and resumes (private)
- slowapi for rate limiting
- Pydantic v2 for validation
- pytest for tests

## 1. Local setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # then fill in real values, see below
```

## 2. Environment variables

All variables live in `.env` (never committed — `.env.example` has placeholders).

| Variable | Where to find it | Notes |
|---|---|---|
| `SUPABASE_DB_URL` | Supabase Dashboard → Project Settings → Database → Connection string (URI) | Use `postgresql+asyncpg://...`. Use the **Transaction pooler** (port 6543) for the running app; use the **direct connection** (port 5432) when running Alembic migrations locally. |
| `SUPABASE_URL` | Project Settings → API | Used for Storage REST calls. |
| `SUPABASE_ANON_KEY` | Project Settings → API | Not currently used server-side, kept for completeness/future frontend use. |
| `SUPABASE_SERVICE_ROLE_KEY` | Project Settings → API | Used server-side only, for Storage uploads/signed URLs. Never expose this to the frontend. |
| `RESEND_API_KEY` | resend.com → API Keys | See SECURITY.md for the manual step of generating this. |
| `RESEND_FROM_EMAIL` | — | Must be a verified sending address/domain in Resend. |
| `TEAM_NOTIFICATION_EMAIL` | — | Where contact/application notifications are sent. |
| `ALLOWED_ORIGINS` | — | Comma-separated list of frontend origins allowed by CORS. Never `*`. |
| `ENVIRONMENT` | — | `development` or `production`. Controls Swagger docs visibility and log level. |
| `PORTFOLIO_BUCKET` / `RESUME_BUCKET` | — | Supabase Storage bucket names. Must be created manually (see SECURITY.md). |
| `MAX_IMAGE_SIZE_MB` / `MAX_RESUME_SIZE_MB` | — | Upload size limits. |
| `GOOGLE_SERVICE_ACCOUNT_JSON` / `GOOGLE_SHEET_ID` | — | Leave blank for now — see "Google Sheets sync" below. |

## 3. Running the migration against Supabase

The migrations enable `pgcrypto` (for UUID generation), create all five
tables, and enable Row Level Security with deny-all policies (see
SECURITY.md for why this matters).

```bash
# Point SUPABASE_DB_URL at the direct connection (port 5432) for this
alembic upgrade head
```

If you ever need to roll back: `alembic downgrade -1`.

## 4. Deploying to Render (free web service tier)

1. Push this repo to GitHub.
2. In the Render dashboard: **New → Web Service**, connect the GitHub repo.
3. Runtime: Python 3. Build command:
   ```
   pip install -r requirements.txt
   ```
4. Start command (the `--proxy-headers` flags are required — Render
   terminates TLS at its edge and forwards plain HTTP to the app, so without
   them the app can never correctly detect HTTPS and HSTS/client-IP
   detection silently break):
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'
   ```
5. In the service's **Environment** tab, add every variable from `.env` (use
   the production Supabase project's values, the production
   `ALLOWED_ORIGINS` — your real frontend domain(s) — and `ENVIRONMENT=production`).
6. Deploy. Note: Render's free tier spins the service down after a period of
   inactivity, so the first request after idling will be slow (cold start).

## 5. Google Sheets sync (not wired up yet)

`app/services/leads.py::sync_to_google_sheet` is called right after every
contact submission is saved, but is currently a no-op stub (just logs). To
wire it up for real, you'll need to provide:

1. A Google Cloud **service account** with the Sheets API enabled, and its
   JSON key (as `GOOGLE_SERVICE_ACCOUNT_JSON`).
2. The target spreadsheet's ID (`GOOGLE_SHEET_ID`), with that service
   account's email added as an editor on the sheet.

Once those are available, implement the actual `append row` call inside
`sync_to_google_sheet` using `google-api-python-client` or `gspread`.

## Running tests

```bash
pytest
```

Auth and honeypot tests run without any database. The portfolio filtering
test is a real integration test against Postgres and is skipped unless you
set `TEST_DATABASE_URL` to a scratch Postgres database (e.g. a local Docker
Postgres, or a separate Supabase branch/project) — never point it at
production data.
