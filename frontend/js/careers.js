import { getJSON } from "./api.js";

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function renderJobs(jobs) {
  const list = document.getElementById("jobs-list");
  if (!jobs.length) {
    list.innerHTML = `<div class="empty-state">No open roles right now</div>`;
    return;
  }

  list.innerHTML = jobs
    .map(
      (job) => `
      <a href="role.html?slug=${encodeURIComponent(job.slug)}" class="card job-card reveal in-view">
        <div>
          <h3>${escapeHtml(job.title)}</h3>
          <div class="meta">${escapeHtml(job.department)} — ${escapeHtml(job.location)} — ${escapeHtml(job.employment_type)}</div>
        </div>
        <span class="btn">View &amp; apply</span>
      </a>
    `
    )
    .join("");
}

async function init() {
  try {
    const jobs = await getJSON("/api/v1/careers");
    renderJobs(jobs);
  } catch (err) {
    document.getElementById("jobs-list").innerHTML =
      `<div class="empty-state">Couldn't load open roles (${escapeHtml(err.message)})</div>`;
  }
}

document.addEventListener("DOMContentLoaded", init);
