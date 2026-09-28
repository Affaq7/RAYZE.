// Shared behavior across every page: mobile nav toggle, the floating-navbar
// scroll effect, the sliding nav hover highlight, scroll-triggered reveal
// animations, and a subtle hero parallax shift.

function initNavToggle() {
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (!toggle || !links) return;

  toggle.addEventListener("click", () => {
    const isOpen = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });
}

function initNavScrollEffect() {
  const header = document.querySelector(".site-header");
  if (!header) return;

  let ticking = false;
  const update = () => {
    header.classList.toggle("scrolled", window.scrollY > 80);
    ticking = false;
  };

  update();
  window.addEventListener("scroll", () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(update);
  });
}

function initNavHoverHighlight() {
  const nav = document.querySelector(".site-header nav");
  const highlight = document.querySelector(".nav-highlight");
  if (!nav || !highlight) return;

  const links = nav.querySelectorAll(".nav-links a");

  links.forEach((link) => {
    link.addEventListener("mouseenter", () => {
      const navRect = nav.getBoundingClientRect();
      const linkRect = link.getBoundingClientRect();
      highlight.style.opacity = "1";
      highlight.style.width = `${linkRect.width}px`;
      highlight.style.transform = `translateX(${linkRect.left - navRect.left}px)`;
    });
  });

  nav.addEventListener("mouseleave", () => {
    highlight.style.opacity = "0";
  });
}

function initScrollReveal() {
  const elements = document.querySelectorAll(".reveal");
  if (!elements.length) return;

  if (!("IntersectionObserver" in window)) {
    elements.forEach((el) => el.classList.add("in-view"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  elements.forEach((el) => observer.observe(el));
}

function initHeroParallax() {
  const hero = document.querySelector(".hero");
  if (!hero) return;

  let ticking = false;
  window.addEventListener("scroll", () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const offset = Math.min(window.scrollY * 0.15, 60);
      hero.style.setProperty("--parallax", `${offset}px`);
      ticking = false;
    });
  });
}

function markActiveNavLink() {
  const current = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-links a").forEach((link) => {
    const href = link.getAttribute("href");
    if (href === current) link.classList.add("active");
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initNavToggle();
  initNavScrollEffect();
  initNavHoverHighlight();
  initScrollReveal();
  initHeroParallax();
  markActiveNavLink();
});
