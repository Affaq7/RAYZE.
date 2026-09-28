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

function cardHtml(item) {
  return `
    <a href="work.html#reviews" class="marquee-card review-card">
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
    </a>
  `;
}

const CARD_WIDTH_PX = 340 + 24; // .marquee-card flex-basis + track gap
const SPEED_PX_PER_SEC = 55; // constant visual speed regardless of review count

async function init() {
  const section = document.querySelector(".reviews-marquee-section");
  const track = document.getElementById("marquee-track");
  if (!section || !track) return;

  try {
    const reviews = await getJSON("/api/v1/reviews");

    if (!reviews.length) {
      section.remove();
      return;
    }

    // The track is rendered as two identical halves back-to-back so the
    // translateX(-50%) loop is seamless. Each HALF also needs to be wider
    // than the viewport on its own, or there's visibly empty space once the
    // handful of real cards runs out (exactly what happens with only 1-2
    // reviews on a wide screen) -- so repeat the review list enough times
    // per half to comfortably outrun the widest reasonable viewport.
    const repeats = Math.min(
      10,
      Math.max(1, Math.ceil((window.innerWidth * 1.5) / (reviews.length * CARD_WIDTH_PX)))
    );
    const half = Array.from({ length: repeats }, () => reviews)
      .flat()
      .map(cardHtml)
      .join("");
    track.innerHTML = half + half;

    // Keep visual speed constant (px/sec) regardless of how many cards ended
    // up in the track -- otherwise more repeats (more reviews, or a wider
    // screen) would make it noticeably faster since duration was fixed.
    const halfWidth = track.scrollWidth / 2;
    const duration = halfWidth / SPEED_PX_PER_SEC;
    track.style.animationDuration = `${duration}s`;
  } catch (err) {
    section.remove();
  }
}

document.addEventListener("DOMContentLoaded", init);
