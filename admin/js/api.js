import { API_BASE } from "./config.js";
import { getToken, logout } from "./auth.js";

export class SessionExpiredError extends Error {}

async function parseErrorDetail(response) {
  try {
    const body = await response.json();
    return body.detail || `Request failed (${response.status})`;
  } catch {
    return `Request failed (${response.status})`;
  }
}

async function authedRequest(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}), Authorization: `Bearer ${token}` };

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401) {
    logout();
    throw new SessionExpiredError("Session expired, please log in again");
  }

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }

  if (response.status === 204) return null;
  return response.json();
}

export function getJSON(path) {
  return authedRequest(path);
}

export function postJSON(path, payload) {
  return authedRequest(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function patchJSON(path, payload) {
  return authedRequest(path, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function del(path) {
  return authedRequest(path, { method: "DELETE" });
}

export function postForm(path, formData) {
  return authedRequest(path, { method: "POST", body: formData });
}
