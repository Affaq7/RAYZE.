# RAYZE Frontend Prototype

A plain HTML/CSS/JS prototype for visually testing the FastAPI backend. This
is **not** the production frontend — placeholder copy/imagery, no build
step, no admin UI. It exists so you can click through all six pages and
confirm the Portfolio, Reviews, Careers, and Contact flows actually work
end-to-end against the real API.

## Run it

You need a real HTTP server (not just double-clicking the HTML files) so
`fetch` and ES module imports work correctly and so the browser sends a real
origin the backend's CORS config can allow. From this `frontend/` folder:

```bash
python -m http.server 5500
```

Then open **http://localhost:5500** in your browser.

## Point it at your backend

1. Make sure the FastAPI backend is running locally (see the root
   `README.md`), typically at `http://localhost:8000`.
2. Add `http://localhost:5500` to the backend's `ALLOWED_ORIGINS` in `.env`,
   then restart the backend. Without this, every fetch call will fail with a
   CORS error in the browser console.
3. If you ever need to point this prototype at a different backend (e.g.
   your Render deployment), change the single `API_BASE` constant in
   [`js/config.js`](js/config.js) — nothing else needs to change.

## What's wired up

- **Portfolio & Reviews** (`work.html`) — fetches `GET /api/v1/portfolio` and
  `GET /api/v1/reviews`, renders real cards, shows an empty state if either
  list is empty.
- **Careers** (`careers.html` → `role.html`) — fetches `GET /api/v1/careers`
  for the list, `GET /api/v1/careers/{slug}` for a role's detail page, and
  submits the apply form (including the resume file) via
  `POST /api/v1/careers/{job_id}/apply` as `multipart/form-data`.
- **Contact** (`contact.html`) — submits via `POST /api/v1/contact` as JSON,
  shows a real success/error message based on the response.

Both public forms include a hidden honeypot field (`website`) matching what
the backend expects — leave it empty as a human visitor would.

## What's not here (by design)

No admin UI — use the `/api/v1/admin/...` endpoints directly (curl, an API
client, or the auto-generated docs at `http://localhost:8000/docs`) to add
portfolio items, reviews, and job postings so there's something for this
prototype to display. No login screens, no final copy or real imagery.
