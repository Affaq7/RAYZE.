# Security

## Implemented

- **Row Level Security (RLS), enabled by the migrations, not left as a manual step.**
  Supabase automatically exposes every table in the `public` schema through
  its auto-generated PostgREST API to anyone holding the `anon` or
  `authenticated` API key — entirely independent of, and bypassing, this
  FastAPI app's own JWT auth layer. Migration `0002_rls_policies` enables
  RLS on every table and adds deny-all policies for both the `anon` and
  `authenticated` Postgres roles. FastAPI itself is unaffected: it connects
  via the role bound to `SUPABASE_DB_URL`, which owns these tables and
  bypasses RLS entirely. Without this, something like `job_applications`
  (containing applicant PII and resumes) would be directly readable via the
  public anon key, regardless of anything FastAPI does.
- **JWT verification, not custom auth.** `app/core/security.py` verifies
  Supabase-issued access tokens against the project's published JWKS
  (`{SUPABASE_URL}/auth/v1/.well-known/jwks.json`) via `PyJWT`'s
  `PyJWKClient`, with the algorithm restricted explicitly to `ES256`/`RS256`
  to avoid algorithm-confusion attacks. This is deliberate, not just a fixed
  shared secret: Supabase now signs tokens with per-project asymmetric keys
  that rotate over time, so verifying against the live JWKS (rather than a
  `SUPABASE_JWT_SECRET` copied into `.env`) keeps working automatically
  through those rotations instead of silently breaking admin login after the
  next key rotation. Any validly signed, non-expired token is treated as
  admin — there is no roles table; admin identity is fully controlled by who
  exists in Supabase Auth. **Because of this, disabling public sign-ups
  (below) is not
  optional.**
- **Private resumes, no stored public links.** The `resumes` bucket is
  private. Uploads store only the object path in `job_applications.resume_path`.
  When an admin views an application, the API requests a fresh, short-lived
  (5–10 minute) signed URL from Supabase Storage on demand — no permanent
  public link to applicant resumes ever exists.
- **CORS** restricted via `ALLOWED_ORIGINS` — no wildcard, ever.
- **Security headers** on every response: CSP, `X-Content-Type-Options`,
  `X-Frame-Options`, `Referrer-Policy`, and HSTS (only when the request is
  HTTPS, correctly detected behind Render's proxy via `ProxyHeadersMiddleware`
  and the `--proxy-headers` uvicorn flag — see README).
- **Rate limiting** (5/hour/IP) on both public POST endpoints
  (`/contact`, `/careers/{id}/apply`).
- **Honeypot field** (`website`) on both public forms — filled-in submissions
  are silently accepted-and-discarded without revealing that they were
  detected.
- **Strict Pydantic validation** everywhere: explicit max lengths on every
  text field, `EmailStr` for email fields, slug pattern validation.
- **File upload validation**: portfolio images restricted to
  `jpeg/png/webp`; resumes restricted to `pdf/jpeg/png`; both size-limited
  (`MAX_IMAGE_SIZE_MB` / `MAX_RESUME_SIZE_MB`).
- **No stack traces in responses.** A global exception handler always
  returns a generic `{"detail": "Internal server error"}` body; full
  tracebacks go only to server logs (`logging.exception`), in every
  environment, not just production.
- **Structured logging** with no request bodies, tokens, or full applicant
  emails logged.
- **Secrets only via `.env`**, `.gitignore`d; `.env.example` ships with
  placeholders only.

## You still need to do this manually

1. **Disable public sign-ups in Supabase Auth** (Authentication → Settings →
   disable "Allow new users to sign up"). This is required, not optional:
   since any validly-authenticated Supabase user is treated as admin by this
   app, leaving sign-ups open would let anyone self-provision admin access
   to every CRUD endpoint.
2. **Create your first admin user** directly in the Supabase Auth dashboard
   (Authentication → Users → Add user). This is the only way to get a valid
   token once sign-ups are disabled.
3. **Create the two Supabase Storage buckets**, since bucket creation isn't
   something a SQL migration can do:
   - `portfolio-images` — **public**.
   - `resumes` — **private** (do not make this bucket public).
   Set bucket-level access policies so that only the service role can
   write, matching how `app/services/storage.py` uploads (via the service
   role key).
4. **Generate a Resend API key** (resend.com → API Keys) and **verify a
   sending domain** in Resend before `RESEND_FROM_EMAIL` will actually
   deliver mail.
