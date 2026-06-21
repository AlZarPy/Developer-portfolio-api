const form = document.querySelector("#contact-form");
const statusNode = document.querySelector("#form-status");

const categoryLabels = {
  job_offer: "предложение о работе",
  project_request: "запрос на проект",
  partnership: "партнерство",
  support: "поддержка",
  spam: "спам",
  other: "другое",
};

const validationMessages = {
  name: {
    valueMissing: "Укажите имя.",
    tooShort: "Имя должно быть не короче 2 символов.",
  },
  email: {
    typeMismatch: "Введите корректный email.",
  },
  phone: {
    patternMismatch: "Введите телефон в международном формате или через 8.",
  },
  message: {
    valueMissing: "Напишите сообщение.",
    tooShort: "Сообщение должно быть не короче 10 символов.",
  },
};

function setStatus(message, isError = false) {
  statusNode.textContent = message;
  statusNode.classList.toggle("error", isError);
}

function getFieldError(input) {
  const messages = validationMessages[input.name] || {};
  if (input.validity.valueMissing) {
    return messages.valueMissing || "Заполните поле.";
  }
  if (input.validity.typeMismatch) {
    return messages.typeMismatch || "Проверьте формат.";
  }
  if (input.validity.patternMismatch) {
    return messages.patternMismatch || "Проверьте формат.";
  }
  if (input.validity.tooShort) {
    return messages.tooShort || `Минимум ${input.minLength} символов.`;
  }
  if (input.validity.customError) {
    return input.validationMessage;
  }
  return "";
}

function setFieldError(input, message) {
  const errorNode = form.querySelector(`[data-error-for="${input.name}"]`);
  input.setAttribute("aria-invalid", message ? "true" : "false");
  if (errorNode) {
    errorNode.textContent = message;
  }
}

function isPhoneShapeValid(value) {
  const trimmed = value.trim();
  if (!trimmed) {
    return true;
  }

  const hasOnlyPhoneChars = /^[+\d\s\-()]+$/.test(trimmed);
  const digits = trimmed.replace(/\D/g, "");
  const startsCorrectly =
    trimmed.startsWith("+") || trimmed.startsWith("8") || digits.startsWith("7");

  return hasOnlyPhoneChars && startsCorrectly && digits.length >= 10 && digits.length <= 15;
}

function validateContactMethod() {
  const email = form.elements.email;
  const phone = form.elements.phone;
  const hasEmail = email.value.trim().length > 0;
  const hasPhone = phone.value.trim().length > 0;
  const message = hasEmail || hasPhone ? "" : "Укажите email или телефон.";

  email.setCustomValidity(message);
  phone.setCustomValidity(message);

  if (hasPhone && !isPhoneShapeValid(phone.value)) {
    phone.setCustomValidity("Введите телефон в международном формате или через 8.");
  }
}

function validateContactFields() {
  const email = form.elements.email;
  const phone = form.elements.phone;
  validateContactMethod();
  setFieldError(email, getFieldError(email));
  setFieldError(phone, getFieldError(phone));
}

function validateField(input) {
  if (input.name === "email" || input.name === "phone") {
    validateContactFields();
    return;
  }

  setFieldError(input, getFieldError(input));
}

function validateForm() {
  validateContactMethod();
  const fields = form.querySelectorAll("input:not([type='hidden']), textarea");
  fields.forEach((input) => setFieldError(input, getFieldError(input)));
  return form.checkValidity();
}

function clearFieldErrors() {
  form.querySelectorAll("input:not([type='hidden']), textarea").forEach((input) => {
    setFieldError(input, "");
  });
}

function getServerFieldMessage(fieldName, message) {
  if (fieldName === "phone") {
    return "Введите корректный телефон.";
  }
  if (fieldName === "email") {
    return "Введите корректный email.";
  }
  if (fieldName === "name") {
    return "Проверьте имя.";
  }
  if (fieldName === "message") {
    return "Проверьте сообщение.";
  }
  return message || "Проверьте поле.";
}

function showServerValidationErrors(details = []) {
  let hasFieldError = false;

  details.forEach((detail) => {
    const location = detail.loc || [];
    const fieldName = location[location.length - 1];
    const input = form.elements[fieldName];

    if (input) {
      setFieldError(input, getServerFieldMessage(fieldName, detail.msg));
      hasFieldError = true;
    }
  });

  if (!hasFieldError) {
    setStatus("Проверьте поля формы.", true);
  }
}

form.querySelectorAll("input:not([type='hidden']), textarea").forEach((input) => {
  input.addEventListener("input", () => validateField(input));
  input.addEventListener("blur", () => validateField(input));
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!validateForm()) {
    setStatus("Проверьте поля формы.", true);
    return;
  }

  setStatus("Отправляем...");

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  if (!payload.email) {
    payload.email = null;
  }
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
      clearFieldErrors();
      if (data.error === "validation_error" && Array.isArray(data.details)) {
        showServerValidationErrors(data.details);
        setStatus("Проверьте поля формы.", true);
        return;
      }

      setStatus(data.message || "Сообщение не отправлено.", true);
      return;
    }

    const label = categoryLabels[data.category] || data.category_label || "другое";
    setStatus(`Сообщение отправлено. Тип обращения: ${label}.`);
    form.reset();
    form.querySelectorAll("input:not([type='hidden']), textarea").forEach((input) => {
      input.setCustomValidity("");
      setFieldError(input, "");
    });
  } catch {
    setStatus("Сообщение не отправлено. Попробуйте позже.", true);
  }
});
