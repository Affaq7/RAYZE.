import { getJSON } from "./api.js";

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function getInitials(name) {
  const parts = (name ?? "").trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  const first = parts[0][0] ?? "";
  const last = parts.length > 1 ? parts[parts.length - 1][0] ?? "" : "";
  return (first + last).toUpperCase();
}

function renderPortfolio(items) {
  const grid = document.getElementById("portfolio-grid");
  if (!items.length) {
    grid.innerHTML = `<div class="empty-state">No portfolio items yet</div>`;
    return;
  }

  grid.innerHTML = items
    .map((item) => {
      const tag = item.project_url ? "a" : "article";
      const linkAttrs = item.project_url
        ? `href="${escapeHtml(item.project_url)}" target="_blank" rel="noopener noreferrer"`
        : "";
      return `
      <${tag} class="card portfolio-card reveal in-view" ${linkAttrs}>
        <div class="cover">
          ${item.cover_image_url ? `<img src="${escapeHtml(item.cover_image_url)}" alt="${escapeHtml(item.title)}">` : "No image"}
        </div>
        <div class="category">${escapeHtml(item.category)}</div>
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.client_name)}</p>
        ${item.project_url ? `<span class="portfolio-link">View project &rarr;</span>` : ""}
      </${tag}>
    `;
    })
    .join("");
}

function renderReviews(items) {
  const grid = document.getElementById("reviews-grid");
  if (!items.length) {
    grid.innerHTML = `<div class="empty-state">No reviews yet</div>`;
    return;
  }

  grid.innerHTML = items
    .map(
      (item) => `
      <article class="card review-card reveal in-view">
        <div class="review-header">
          ${
            item.avatar_url
              ? `<img class="avatar" src="${escapeHtml(item.avatar_url)}" alt="${escapeHtml(item.client_name)}">`
              : `<div class="avatar avatar-initials">${escapeHtml(getInitials(item.client_name))}</div>`
          }
          <div class="client">
            <div class="client-name">${escapeHtml(item.client_name)}</div>
            ${item.company ? `<div class="client-company">${escapeHtml(item.company)}</div>` : ""}
          </div>
        </div>
        <div class="rating-row">
          <span class="stars">${"★".repeat(item.rating)}${"☆".repeat(5 - item.rating)}</span>
          <span class="score">${item.rating}/5</span>
        </div>
        <p class="quote">&ldquo;${escapeHtml(item.quote)}&rdquo;</p>
      </article>
    `
    )
    .join("");
}

async function init() {
  try {
    const portfolio = await getJSON("/api/v1/portfolio");
    renderPortfolio(portfolio);
  } catch (err) {
    document.getElementById("portfolio-grid").innerHTML =
      `<div class="empty-state">Couldn't load portfolio (${escapeHtml(err.message)})</div>`;
  }

  try {
    const reviews = await getJSON("/api/v1/reviews");
    renderReviews(reviews);
  } catch (err) {
    document.getElementById("reviews-grid").innerHTML =
      `<div class="empty-state">Couldn't load reviews (${escapeHtml(err.message)})</div>`;
  }
}

document.addEventListener("DOMContentLoaded", init);
