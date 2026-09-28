import { getJSON, postForm } from "./api.js";

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function getSlug() {
  return new URLSearchParams(window.location.search).get("slug");
}

async function loadJob() {
  const slug = getSlug();
  const detail = document.getElementById("job-detail");
  const form = document.getElementById("apply-form");

  if (!slug) {
    detail.innerHTML = `<div class="empty-state">No role specified</div>`;
    return null;
  }

  try {
    const job = await getJSON(`/api/v1/careers/${encodeURIComponent(slug)}`);
    detail.innerHTML = `
      <div class="overline">${escapeHtml(job.department)}</div>
      <h1>${escapeHtml(job.title)}</h1>
      <p style="margin-top:16px;">${escapeHtml(job.location)} — ${escapeHtml(job.employment_type)}</p>
      <p style="margin-top:24px; color: var(--white);">${escapeHtml(job.description)}</p>
    `;
    form.style.display = "block";
    form.dataset.jobId = job.id;
    return job;
  } catch (err) {
    detail.innerHTML = `<div class="empty-state">Couldn't load this role (${escapeHtml(err.message)})</div>`;
    return null;
  }
}

function initApplyForm() {
  const form = document.getElementById("apply-form");
  const status = document.getElementById("apply-status");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    status.textContent = "";
    status.className = "form-status";

    const jobId = form.dataset.jobId;
    if (!jobId) return;

    const formData = new FormData(form);
    const submitButton = form.querySelector("button[type=submit]");
    submitButton.disabled = true;

    try {
      await postForm(`/api/v1/careers/${encodeURIComponent(jobId)}/apply`, formData);
      status.textContent = "Application submitted — we'll be in touch.";
      status.classList.add("success");
      form.reset();
    } catch (err) {
      status.textContent = `Something went wrong: ${err.message}`;
      status.classList.add("error");
    } finally {
      submitButton.disabled = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  await loadJob();
  initApplyForm();
});
