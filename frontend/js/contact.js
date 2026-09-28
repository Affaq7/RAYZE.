import { postJSON } from "./api.js";

function initContactForm() {
  const form = document.getElementById("contact-form");
  const status = document.getElementById("contact-status");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    status.textContent = "";
    status.className = "form-status";

    const payload = {
      name: form.name.value,
      email: form.email.value,
      company: form.company.value || null,
      message: form.message.value,
      website: form.website.value,
    };

    const submitButton = form.querySelector("button[type=submit]");
    submitButton.disabled = true;

    try {
      await postJSON("/api/v1/contact", payload);
      status.textContent = "Message sent — we'll be in touch soon.";
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

document.addEventListener("DOMContentLoaded", initContactForm);
