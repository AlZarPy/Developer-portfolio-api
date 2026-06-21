const form = document.querySelector("#contact-form");
const statusNode = document.querySelector("#form-status");

function setStatus(message, isError = false) {
  statusNode.textContent = message;
  statusNode.classList.toggle("error", isError);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Sending...");

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  if (!payload.phone) {
    payload.phone = null;
  }

  try {
    const response = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok) {
      setStatus(data.message || "Message was not sent.", true);
      return;
    }

    setStatus(`Message sent. Request type: ${data.category_label}.`);
    form.reset();
  } catch {
    setStatus("Message was not sent. Please try again later.", true);
  }
});
