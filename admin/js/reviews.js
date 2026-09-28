import { getJSON, postJSON, patchJSON, del } from "./api.js";

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function setStatus(el, message, type) {
  el.textContent = message;
  el.className = `status-msg ${type ?? ""}`;
}

function readForm() {
  return {
    client_name: document.getElementById("review-client").value,
    company: document.getElementById("review-company").value || null,
    avatar_url: document.getElementById("review-avatar").value || null,
    quote: document.getElementById("review-quote").value,
    rating: Number(document.getElementById("review-rating").value),
    is_published: document.getElementById("review-published").checked,
  };
}

function fillForm(item) {
  document.getElementById("review-id").value = item.id;
  document.getElementById("review-client").value = item.client_name;
  document.getElementById("review-company").value = item.company || "";
  document.getElementById("review-avatar").value = item.avatar_url || "";
  document.getElementById("review-quote").value = item.quote;
  document.getElementById("review-rating").value = String(item.rating);
  document.getElementById("review-published").checked = item.is_published;
  document.getElementById("review-form-title").textContent = "Edit review";
  document.getElementById("review-cancel-edit").hidden = false;
}

function resetForm() {
  document.getElementById("review-form").reset();
  document.getElementById("review-id").value = "";
  document.getElementById("review-form-title").textContent = "Add review";
  document.getElementById("review-cancel-edit").hidden = true;
}

async function loadList() {
  const list = document.getElementById("reviews-list");
  try {
    const items = await getJSON("/api/v1/admin/reviews");
    if (!items.length) {
      list.innerHTML = `<div class="empty-state">No reviews yet</div>`;
      return;
    }
    list.innerHTML = items
      .map(
        (item) => `
        <div class="item-row" data-id="${item.id}">
          <div class="info">
            <div class="title">${escapeHtml(item.client_name)}
              <span class="badge ${item.is_published ? "published" : "draft"}">${item.is_published ? "Published" : "Draft"}</span>
            </div>
            <div class="meta">${"★".repeat(item.rating)}${"☆".repeat(5 - item.rating)} (${item.rating}/5)${item.company ? ` — ${escapeHtml(item.company)}` : ""}</div>
          </div>
          <div class="actions">
            <button class="btn btn-small" data-action="toggle">${item.is_published ? "Unpublish" : "Publish"}</button>
            <button class="btn btn-small" data-action="edit">Edit</button>
            <button class="btn btn-small btn-danger" data-action="delete">Delete</button>
          </div>
        </div>
      `
      )
      .join("");

    list.querySelectorAll(".item-row").forEach((row) => {
      const id = row.dataset.id;
      const item = items.find((i) => i.id === id);

      row.querySelector('[data-action="edit"]').addEventListener("click", () => fillForm(item));

      row.querySelector('[data-action="toggle"]').addEventListener("click", async () => {
        await patchJSON(`/api/v1/admin/reviews/${id}`, { is_published: !item.is_published });
        await loadList();
      });

      row.querySelector('[data-action="delete"]').addEventListener("click", async () => {
        if (!confirm(`Delete this review from ${item.client_name}? This can't be undone.`)) return;
        await del(`/api/v1/admin/reviews/${id}`);
        await loadList();
      });
    });
  } catch (err) {
    list.innerHTML = `<div class="empty-state">Couldn't load reviews (${escapeHtml(err.message)})</div>`;
  }
}

export function initReviewsPanel() {
  const form = document.getElementById("review-form");
  const status = document.getElementById("review-form-status");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = document.getElementById("review-id").value;
    const payload = readForm();

    try {
      if (id) {
        await patchJSON(`/api/v1/admin/reviews/${id}`, payload);
        setStatus(status, "Review updated.", "success");
      } else {
        await postJSON("/api/v1/admin/reviews", payload);
        setStatus(status, "Review created.", "success");
      }
      resetForm();
      await loadList();
    } catch (err) {
      setStatus(status, err.message, "error");
    }
  });

  document.getElementById("review-cancel-edit").addEventListener("click", resetForm);

  loadList();
}
