import { getJSON } from "./api.js";

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function renderPortfolio(items) {
  const grid = document.getElementById("portfolio-grid");
  if (!items.length) {
    grid.innerHTML = `<div class="empty-state">No portfolio items yet</div>`;
    return;
  }

  grid.innerHTML = items
    .map(
      (item) => `
      <article class="card portfolio-card reveal in-view">
        <div class="cover">
          ${item.cover_image_url ? `<img src="${escapeHtml(item.cover_image_url)}" alt="${escapeHtml(item.title)}">` : "No image"}
        </div>
        <div class="category">${escapeHtml(item.category)}</div>
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.client_name)}</p>
      </article>
    `
    )
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
        <div class="stars">${"★".repeat(item.rating)}${"☆".repeat(5 - item.rating)}</div>
        <p class="quote">&ldquo;${escapeHtml(item.quote)}&rdquo;</p>
        <div class="client">${escapeHtml(item.client_name)}${item.company ? ` — ${escapeHtml(item.company)}` : ""}</div>
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
