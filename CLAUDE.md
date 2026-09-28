# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What RAYZE is

RAYZE is a media marketing agency. Its six services (as shown on the public
Services page) are: Social Media Management, Logo Design, Brand Design,
Video Editing & Animation, Website, and Automations. Tagline: **"Rise with
RAYZE."**

This repo is an early-phase foundation, not a finished product: a FastAPI
backend, a static-HTML public site prototype, and a standalone static admin
panel — all against a real Supabase project. Expect it to keep growing;
avoid over-engineering ahead of what's actually asked.

## Brand / design system

Used consistently across `frontend/` and `admin/` (see
`frontend/css/style.css` `:root` for the source of truth):

- **Colors**: near-black background `#0a0a0a` (raised surfaces `#141414`),
  one accent red `#e8241a`, white text, muted gray `#9a9a9a` for secondary
  text, `#262626` borders. No other colors — sharp corners, no rounded UI.
- **Typography**: **Delight** (a licensed font — see the licensing note
  below) for headings, loaded as three static weights via `@font-face` in
  `frontend/css/style.css` / `admin/css/style.css`, each mapped to a
  `font-weight` so plain CSS `font-weight` picks the right file: `h1` =
  Black (900), `h2` = ExtraBold (800), `h3` = Bold (700). Body copy uses
  **Inter** (Google Fonts). Headings are uppercase, sharp/blocky, not
  delicate.
- **Recurring patterns**: small uppercase "overline" labels with a dash
  before section headings (`.overline`); bold oversized numerals pairing
  with numbered sections (`.numbered-section`, "01", "02", ...); stat
  callouts with a big number + small label (`.stat`); solid-red full-bleed
  CTA blocks between black sections (`.cta-block`).
- **Motion**: subtle scroll-triggered reveal (`main.js`'s
  `IntersectionObserver` + `.reveal`/`.in-view` classes), a light hero
  parallax, nav/button hover states. Kept tasteful — no gimmicks.
- **Logo**: an angular geometric "R" mark. Source files live in
  `frontend/logos/` (multiple color variants provided by the client — solid
  red, white, black, gradient — plus two square red-gradient social/app-icon
  style assets, `rayze-20.png`/`rayze-21.png`, which are NOT used inline in
  the site). The actual asset used in nav/footer across the whole site is
  `frontend/logos/mark-red.png` — a tightly-cropped, transparent, red-only
  crop of the mark (no wordmark baked in), paired with plain "RAYZE." text
  styled via CSS. Favicons (`favicon-16.png`, `favicon-32.png`,
  `apple-touch-icon.png`) were generated from that same crop and exist at
  the root of both `frontend/` and `admin/`.
- **Licensing note**: the Delight font files were downloaded from a
  "free font" site at the user's direction; free-for-personal-use fonts
  frequently exclude commercial use — this has not been verified as cleared
  for production/commercial use and should be checked before shipping this
  site live.

## Repo layout — three independent things, one Supabase project

- **`app/`** — the FastAPI backend. Source of truth for all data.
- **`frontend/`** — the public marketing site. Plain HTML/CSS/JS, no build
  step, no framework. A prototype for visually testing the backend, not the
  final production frontend the team will build later.
- **`admin/`** — a standalone admin panel (also plain HTML/CSS/JS). Fully
  decoupled from `frontend/` on purpose (separate CSS/JS/fonts/favicons, not
  linked from the public site's nav) so it can be hosted completely
  separately later. Its only real security boundary is the same backend JWT
  check every other admin route uses — the panel itself is just a friendlier
  UI than curl/Swagger, gated by a Supabase login screen, `noindex`'d and
  unlinked, not independently hardened.

All three point at the same Supabase project (one Postgres database, one
Auth user pool, one Storage account) and one FastAPI backend.

## Commands

Backend (run from repo root, with `.venv` active):
```bash
pip install -r requirements.txt
alembic upgrade head                 # apply migrations to Supabase Postgres
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pytest                               # run tests
pytest tests/test_auth.py -k expired # run a single test
```
`.env` (gitignored) holds real config; `.env.example` documents every var. A
change to `.env` requires restarting `uvicorn` — it's read once at import
time via `pydantic-settings`, `--reload` does not pick it up.

Frontend (from `frontend/`):
```bash
python -m http.server 5500
```

Admin panel (from `admin/`):
```bash
python -m http.server 5501
```

Both static sites need their origin present in the backend's
`ALLOWED_ORIGINS` (`.env`) or every `fetch` call fails on CORS — restart the
backend after changing it.

## Backend architecture

- **`app/main.py`** — app factory. Middleware order matters here: added via
  `add_middleware` in this order — `ExceptionHandlingMiddleware` (innermost),
  `ProxyHeadersMiddleware`, `SecurityHeadersMiddleware`, `CORSMiddleware`
  (outermost, since Starlette wraps in reverse of registration order).
  `ExceptionHandlingMiddleware` exists specifically because a plain
  `app.exception_handler(Exception)` gets special-cased by Starlette onto
  `ServerErrorMiddleware`, which sits *outside* CORS/security headers —
  meaning generic 500s would otherwise ship with no CORS or security headers
  at all. Don't reintroduce a bare `Exception` handler.
- **Auth (`app/core/security.py`)** — verifies Supabase JWTs against the
  project's live **JWKS** (`{SUPABASE_URL}/auth/v1/.well-known/jwks.json`),
  not a fixed shared secret. This is deliberate: Supabase now signs tokens
  with rotating asymmetric keys (ES256), so a fixed `SUPABASE_JWT_SECRET`
  would silently stop working after any key rotation. There is no roles
  table — any validly-signed, non-expired Supabase token is treated as
  admin, so disabling public sign-ups in the Supabase dashboard is load-
  bearing, not optional (see `SECURITY.md`).
- **Data model** — five tables (`app/models/`): `portfolio`, `reviews`,
  `job_postings`, `job_applications`, `contact_submissions`. Every table has
  Postgres Row Level Security enabled with deny-all policies for the `anon`
  and `authenticated` roles (migration `0002`) — this exists because
  Supabase auto-exposes every table via PostgREST to anyone holding the
  anon key, completely bypassing this app's own auth if RLS is off. FastAPI
  itself connects via the direct DB role (`SUPABASE_DB_URL`) and is
  unaffected by RLS.
- **Public vs admin routes** (`app/api/v1/`) — each resource file
  (`portfolio.py`, `reviews.py`, `careers.py`, `contact.py`) exports a
  `public_router` (only `is_published=true` / `is_open=true` rows, no auth)
  and an `admin_router` (full CRUD, `Depends(get_current_admin)` on the
  whole router). Public POST endpoints (`/contact`, `/careers/{id}/apply`)
  are rate-limited (slowapi, 5/hour/IP) and honeypot-protected — a filled
  honeypot field returns a fake success response without touching the DB.
- **Storage (`app/services/storage.py`)** — portfolio images go to a
  **public** Supabase Storage bucket (public URL stored directly). Resumes
  go to a **private** bucket; only the object path is stored
  (`job_applications.resume_path`), never a public URL — admins get a fresh
  5–10 minute signed URL generated on demand when viewing an application.
- **Migrations (`alembic/versions/`)** — sequential: `0001` initial schema,
  `0002` RLS policies, `0003` adds `portfolio.project_url` (external
  project link, e.g. Behance) and `reviews.avatar_url`. When adding enum
  types via raw SQL in a migration, use the guarded
  `DO $$ BEGIN CREATE TYPE ...; EXCEPTION WHEN duplicate_object THEN null; END $$;`
  pattern (see `0001`), not SQLAlchemy's `Enum(...).create()` — over the
  pooled Supabase connection, its check-then-create round trip left a real
  race window that intermittently raised spurious "already exists" errors.
- **Google Sheets sync** — `app/services/leads.py::sync_to_google_sheet` is
  called after every contact submission but is a documented no-op stub
  (no service account credentials configured yet).

## Database connection (Supabase-specific gotcha)

`SUPABASE_DB_URL` must use the **Session pooler** connection string, not
"Direct connection". Direct connections are IPv6-only by default on
Supabase now (a paid add-on is required for IPv4), which fails to connect
from most home networks and standard hosting. Session pooler is IPv4-
compatible and, unlike Transaction pooler, behaves like a normal Postgres
connection (supports prepared statements/session state), so no extra
asyncpg compatibility flags are needed. The pooler username is
`postgres.<project-ref>`, not just `postgres`.

## Frontend/admin conventions

- No build step anywhere — plain `<script type="module">` imports. Each
  page has its own small JS file (`frontend/js/work.js`,
  `admin/js/portfolio.js`, etc.) plus shared `api.js`/`config.js`.
- `frontend/js/config.js` and `admin/js/config.js` each hardcode `API_BASE`
  — no env-var injection for static files. Swapping backends (e.g. to a
  Render URL) means manually editing this constant before deploying.
- `admin/js/auth.js` logs in directly against Supabase's REST API
  (`/auth/v1/token?grant_type=password`) using the public anon key, storing
  the access token in `localStorage`. No refresh-token flow — the panel
  just bounces back to the login screen on any `401`, roughly every hour.
- Job applications' resumes and contact-form leads are stored/handled by
  the backend as described above; the admin panel currently only has
  CRUD for Portfolio and Reviews (not Careers/Applications/Contact yet).
