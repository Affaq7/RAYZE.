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
    title: document.getElementById("portfolio-title").value,
    slug: document.getElementById("portfolio-slug").value,
    client_name: document.getElementById("portfolio-client").value,
    category: document.getElementById("portfolio-category").value,
    description: document.getElementById("portfolio-description").value,
    cover_image_url: document.getElementById("portfolio-cover").value || null,
    project_url: document.getElementById("portfolio-project-url").value || null,
    is_published: document.getElementById("portfolio-published").checked,
  };
}

function fillForm(item) {
  document.getElementById("portfolio-id").value = item.id;
  document.getElementById("portfolio-title").value = item.title;
  document.getElementById("portfolio-slug").value = item.slug;
  document.getElementById("portfolio-client").value = item.client_name;
  document.getElementById("portfolio-category").value = item.category;
  document.getElementById("portfolio-description").value = item.description;
  document.getElementById("portfolio-cover").value = item.cover_image_url || "";
  document.getElementById("portfolio-project-url").value = item.project_url || "";
  document.getElementById("portfolio-published").checked = item.is_published;
  document.getElementById("portfolio-form-title").textContent = "Edit portfolio item";
  document.getElementById("portfolio-cancel-edit").hidden = false;
}

function resetForm() {
  document.getElementById("portfolio-form").reset();
  document.getElementById("portfolio-id").value = "";
  document.getElementById("portfolio-form-title").textContent = "Add portfolio item";
  document.getElementById("portfolio-cancel-edit").hidden = true;
}

async function loadList() {
  const list = document.getElementById("portfolio-list");
  try {
    const items = await getJSON("/api/v1/admin/portfolio");
    if (!items.length) {
      list.innerHTML = `<div class="empty-state">No portfolio items yet</div>`;
      return;
    }
    list.innerHTML = items
      .map(
        (item) => `
        <div class="item-row" data-id="${item.id}">
          <div class="info">
            <div class="title">${escapeHtml(item.title)}
              <span class="badge ${item.is_published ? "published" : "draft"}">${item.is_published ? "Published" : "Draft"}</span>
            </div>
            <div class="meta">${escapeHtml(item.slug)} — ${escapeHtml(item.category)}</div>
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
        await patchJSON(`/api/v1/admin/portfolio/${id}`, { is_published: !item.is_published });
        await loadList();
      });

      row.querySelector('[data-action="delete"]').addEventListener("click", async () => {
        if (!confirm(`Delete "${item.title}"? This can't be undone.`)) return;
        await del(`/api/v1/admin/portfolio/${id}`);
        await loadList();
      });
    });
  } catch (err) {
    list.innerHTML = `<div class="empty-state">Couldn't load portfolio items (${escapeHtml(err.message)})</div>`;
  }
}

export function initPortfolioPanel() {
  const form = document.getElementById("portfolio-form");
  const status = document.getElementById("portfolio-form-status");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = document.getElementById("portfolio-id").value;
    const payload = readForm();

    try {
      if (id) {
        await patchJSON(`/api/v1/admin/portfolio/${id}`, payload);
        setStatus(status, "Portfolio item updated.", "success");
      } else {
        await postJSON("/api/v1/admin/portfolio", payload);
        setStatus(status, "Portfolio item created.", "success");
      }
      resetForm();
      await loadList();
    } catch (err) {
      setStatus(status, err.message, "error");
    }
  });

  document.getElementById("portfolio-cancel-edit").addEventListener("click", resetForm);

  loadList();
}
