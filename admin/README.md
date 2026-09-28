# RAYZE Admin Panel

A small, standalone admin UI for managing Portfolio and Reviews content. It is
**deliberately separate from the public site** (`frontend/`) — its own
HTML/CSS/JS/fonts, no shared files, not linked from the public site's nav. It
can be deployed on its own subdomain or host later without touching
`frontend/` at all.

It does not add any new security of its own — every real permission check
happens server-side (`app/core/security.py`), verifying a Supabase-issued
JWT on every `/api/v1/admin/...` call. This panel is just a friendlier way to
get that token and use those endpoints than curl or Swagger.

## Run it locally

```bash
cd admin
python -m http.server 5501
```

Open **http://localhost:5501**.

Make sure:
1. The backend is running (see the root `README.md`).
2. `http://localhost:5501` is in the backend's `ALLOWED_ORIGINS` in `.env`
   (already added by default) — restart the backend after any `.env` change.
3. `admin/js/config.js`'s `API_BASE` points at your running backend.

## Logging in

Use the email/password of a real user created in the Supabase Auth dashboard
(Authentication → Users). There's no sign-up form here on purpose — the only
way to get an admin account is you creating one directly in Supabase, per
`SECURITY.md` in the project root.

A session lasts as long as the Supabase access token is valid (about an
hour, by default). This first pass doesn't implement silent token refresh —
once it expires, any admin action will drop you back to the login screen and
you just log in again. That's a deliberate simplification, not a bug.

## What it can do

- **Portfolio**: create, edit, publish/unpublish, and delete items. Cover
  images are set via a URL field here (paste a hosted image link, e.g. from
  Behance) — there's no file-upload button in this panel; use
  `POST /api/v1/admin/portfolio/{id}/image` directly (Swagger/curl) if you
  need to upload a file instead of linking one.
- **Reviews**: create, edit, publish/unpublish, and delete reviews, including
  an optional avatar image URL (leave blank to fall back to initials on the
  public site).

Job Postings, Job Applications, and Contact Submissions aren't in this panel
yet — use `/docs` (locally) or curl for those for now.

## Deploying

Once you have a domain: host this folder wherever you like (a separate
static host, a subdomain, or a private path — your call), set
`API_BASE` in `admin/js/config.js` to your deployed backend's URL, and add
that panel's real deployed origin to the backend's `ALLOWED_ORIGINS`. Nothing
else changes — the login flow and admin endpoints work identically against
your production Supabase project.
