import { login, logout, isLoggedIn } from "./auth.js";
import { getJSON, SessionExpiredError } from "./api.js";
import { initPortfolioPanel } from "./portfolio.js";
import { initReviewsPanel } from "./reviews.js";

const loginView = document.getElementById("login-view");
const dashboardView = document.getElementById("dashboard-view");

let panelsInitialized = false;

function showLogin() {
  loginView.hidden = false;
  dashboardView.hidden = true;
}

function showDashboard() {
  loginView.hidden = true;
  dashboardView.hidden = false;
  if (!panelsInitialized) {
    initPortfolioPanel();
    initReviewsPanel();
    panelsInitialized = true;
  }
}

function initTabs() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");
    });
  });
}

function initLoginForm() {
  const form = document.getElementById("login-form");
  const status = document.getElementById("login-status");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    status.textContent = "";
    status.className = "status-msg";

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      await login(email, password);
      form.reset();
      showDashboard();
    } catch (err) {
      status.textContent = err.message;
      status.className = "status-msg error";
    }
  });
}

function initLogout() {
  document.getElementById("logout-btn").addEventListener("click", () => {
    logout();
    showLogin();
  });
}

async function init() {
  initTabs();
  initLoginForm();
  initLogout();

  if (!isLoggedIn()) {
    showLogin();
    return;
  }

  // Verify the stored token still works before trusting it.
  try {
    await getJSON("/api/v1/admin/portfolio");
    showDashboard();
  } catch (err) {
    if (err instanceof SessionExpiredError) {
      showLogin();
    } else {
      // Token is fine but something else failed (e.g. backend down) --
      // still show the dashboard so the per-panel error states can explain.
      showDashboard();
    }
  }
}

document.addEventListener("DOMContentLoaded", init);
