/* =========================================================
   UNNAT KISAN
   Main JavaScript
   ========================================================= */

/* ================= MOBILE NAVIGATION ================= */

const menuToggle = document.getElementById("menuToggle");
const navMenu = document.querySelector(".nav-menu");

if (menuToggle && navMenu) {
  menuToggle.addEventListener("click", () => {
    navMenu.classList.toggle("active");
  });

  const navLinks = navMenu.querySelectorAll("a");

  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      navMenu.classList.remove("active");
    });
  });
}

/* ================= HEADER SHADOW ================= */

const navbar = document.querySelector(".navbar");

window.addEventListener("scroll", () => {
  if (!navbar) return;

  if (window.scrollY > 20) {
    navbar.style.boxShadow = "0 4px 20px rgba(0, 0, 0, 0.08)";
  } else {
    navbar.style.boxShadow = "none";
  }
});
/* =========================================================
   AUTHENTICATION UI
   ========================================================= */

/* ================= PASSWORD TOGGLE ================= */

const passwordToggle = document.getElementById("passwordToggle");

const passwordInput = document.getElementById("password");

if (passwordToggle && passwordInput) {
  passwordToggle.addEventListener("click", () => {
    if (passwordInput.type === "password") {
      passwordInput.type = "text";

      passwordToggle.textContent = "🙈";
    } else {
      passwordInput.type = "password";

      passwordToggle.textContent = "👁";
    }
  });
}
/* ================= LOGIN FORM ================= */

const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
      alert("Please fill in all required fields.");
      return;
    }

    try {
      const response = await fetch(
        "https://unnat-kisan.onrender.com/api/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            password: password,
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        alert(
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail),
        );
        return;
      }

      // Save login information
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("role", data.role);
      localStorage.setItem("full_name", data.full_name);

      alert("Login successful!");

      // Open the correct dashboard
      if (data.role === "farmer") {
        window.location.href = "farmer-dashboard.html";
      } else if (data.role === "bulk_buyer") {
        window.location.href = "bulk-buyer-dashboard.html";
      } else if (data.role === "customer") {
        window.location.href = "customer-dashboard.html";
      } else if (data.role === "admin") {
        window.location.href = "admin-dashboard.html";
      } else {
        alert("Unknown user role: " + data.role);
      }
    } catch (error) {
      console.error("Login error:", error);
      alert(
        "Unable to connect to the backend. " + "Make sure FastAPI is running.",
      );
    }
  });
}
/* ================= ROLE REGISTRATION ================= */

const roleButtons = document.querySelectorAll(".role-btn");

roleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const role = button.dataset.role;

    /*
     * Temporary frontend routing.
     *
     * Actual registration forms and
     * backend API will be connected next.
     */

    console.log("Selected role:", role);

    if (role === "farmer") {
      window.location.href = "register-farmer.html";
    } else if (role === "bulk-buyer") {
      window.location.href = "register-bulk-buyer.html";
    } else if (role === "customer") {
      window.location.href = "register-customer.html";
    }
  });
});
/* =========================================================
   REGISTRATION FORMS
   ========================================================= */

/* ================= GENERIC REGISTRATION ================= */
function setupRegistrationForm(formId) {
  const form = document.getElementById(formId);

  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const password = form.querySelector('input[name="password"]');
    const confirmPassword = form.querySelector(
      'input[name="confirm_password"]',
    );

    if (password.value !== confirmPassword.value) {
      alert("Passwords do not match.");
      return;
    }

    if (password.value.length < 8) {
      alert("Password must contain at least 8 characters.");
      return;
    }

    let endpoint = "";

    if (formId === "customerForm") {
      endpoint = "/api/auth/register/customer";
    } else if (formId === "farmerForm") {
      endpoint = "/api/auth/register/farmer";
    } else if (formId === "bulkBuyerForm") {
      endpoint = "/api/auth/register/bulk-buyer";
    }

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    delete data.confirm_password;

    try {
      const response = await fetch(
        `https://unnat-kisan.onrender.com${endpoint}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        },
      );

      const result = await response.json();

      if (!response.ok) {
        alert(
          typeof result.detail === "string"
            ? result.detail
            : JSON.stringify(result.detail),
        );
        return;
      }

      alert(result.message || "Registration successful!");

      window.location.href = "login.html";
    } catch (error) {
      console.error(error);

      alert(
        "Unable to connect to the backend. " + "Make sure FastAPI is running.",
      );
    }
  });
}
setupRegistrationForm("farmerForm");

setupRegistrationForm("bulkBuyerForm");

setupRegistrationForm("customerForm");
/* =========================================
   BULK BUYER LICENSE PHOTO PREVIEW
========================================= */

const licensePhoto = document.getElementById("licensePhoto");
const licensePreview = document.getElementById("licensePreview");

if (licensePhoto && licensePreview) {
  licensePhoto.addEventListener("change", function () {
    const file = this.files[0];

    if (!file) {
      licensePreview.innerHTML = "";
      licensePreview.classList.remove("active");
      return;
    }

    if (!file.type.startsWith("image/")) {
      alert("Please upload a valid image file.");
      this.value = "";
      licensePreview.innerHTML = "";
      licensePreview.classList.remove("active");
      return;
    }

    const reader = new FileReader();

    reader.onload = function (event) {
      licensePreview.innerHTML = `
                <strong>Selected Document</strong>
                <img src="${event.target.result}" alt="License Preview">
                <p>${file.name}</p>
            `;

      licensePreview.classList.add("active");
    };

    reader.readAsDataURL(file);
  });
}

/* =========================================
   CUSTOMER TYPE SELECTION
========================================= */

const customerTypeCards = document.querySelectorAll(".customer-type-card");

customerTypeCards.forEach((card) => {
  card.addEventListener("click", function () {
    customerTypeCards.forEach((item) => {
      item.classList.remove("selected");
    });

    this.classList.add("selected");
  });
});
