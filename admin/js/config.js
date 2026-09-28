// Standalone config for the admin panel -- deliberately not shared with
// frontend/js/config.js so this folder has zero dependency on the public site.

// Our FastAPI backend. Swap when deploying (e.g. "https://api.yourdomain.com").
export const API_BASE = "http://localhost:8001";

// Supabase project. The anon key is safe to embed client-side -- it's the
// same public key used for the Supabase Auth password-grant login below;
// it has no admin access on its own (all real authorization happens
// server-side against the JWT this login produces).
export const SUPABASE_URL = "https://vdcdyylzgdxtgkmglsux.supabase.co";
export const SUPABASE_ANON_KEY = "sb_publishable_qWDbB8xk9JBZZ_9zRwuEmg_ehbW6Eam";
