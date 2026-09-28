import { SUPABASE_URL, SUPABASE_ANON_KEY } from "./config.js";

const TOKEN_KEY = "rayze_admin_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function isLoggedIn() {
  return Boolean(getToken());
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function login(email, password) {
  const response = await fetch(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
    method: "POST",
    headers: {
      apikey: SUPABASE_ANON_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(body.error_description || body.msg || "Invalid email or password");
  }

  if (!body.access_token) {
    throw new Error("Supabase did not return an access token");
  }

  localStorage.setItem(TOKEN_KEY, body.access_token);
  return body.access_token;
}
