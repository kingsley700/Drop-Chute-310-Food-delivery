const APP_PAGE = "customer.html";

const form = document.getElementById("login-form");
const submitButton = document.getElementById("submit-button");
const formError = document.getElementById("form-error");

const FIELDS = ["email", "password"];


function clearErrors() {
    for (const field of FIELDS) {
        document.getElementById(field + "-error").textContent = "";
        document.getElementById(field).classList.remove("invalid");
    }
    formError.textContent = "";
}

function showFieldError(field, message) {
    document.getElementById(field + "-error").textContent = message;
    document.getElementById(field).classList.add("invalid");
}

form.addEventListener("submit", async function (event) {
    event.preventDefault();
    clearErrors();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    // Basic checks before sending
    let valid = true;
    if (email === "") {
        showFieldError("email", "Email is required");
        valid = false;
    }
    if (password === "") {
        showFieldError("password", "Password is required");
        valid = false;
    }
    if (!valid) {
        return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Signing in...";

    try {
        const response = await apiFetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email, password: password }),
        });

        if (response.status === 200) {
            const data = await response.json();
            setToken(data.access_token);
            window.location.href = APP_PAGE;
            return;
        }

        if (response.status === 401 || response.status === 422) {
            // One generic message, so it never says which part was wrong
            formError.textContent = "Invalid email or password";
        } else {
            formError.textContent = "Something went wrong. Please try again.";
        }
    } catch (networkError) {
        formError.textContent = "Could not reach the server. Check your connection and try again.";
    }

    submitButton.disabled = false;
    submitButton.textContent = "Sign in";
});