const API_URL = "http://127.0.0.1:8000";
const SIGN_IN_PAGE = "login.html";

const FIELDS = ["name", "email", "password", "delivery_address"];

const form = document.getElementById("register-form");
const submitButton = document.getElementById("submit-button");
const formError = document.getElementById("form-error");
const formSuccess = document.getElementById("form-success");


function showFieldError(field, message) {
    document.getElementById(field + "-error").textContent = message;
    document.getElementById(field).classList.add("invalid");
}

function clearErrors() {
    for (const field of FIELDS) {
        document.getElementById(field + "-error").textContent = "";
        document.getElementById(field).classList.remove("invalid");
    }
    formError.textContent = "";
    formSuccess.textContent = "";
}

function readValues() {
    return {
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value,
        delivery_address: document.getElementById("delivery_address").value.trim(),
    };
}

// Same rules as the API (CustomerCreate), so most mistakes are caught before sending.
function validate(values) {
    const errors = {};

    if (values.name === "") {
        errors.name = "Name is required";
    } else if (values.name.length < 3 || values.name.length > 40) {
        errors.name = "Name must be 3 to 40 characters";
    }

    if (values.email === "") {
        errors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
        errors.email = "Enter a valid email address";
    }

    if (values.password === "") {
        errors.password = "Password is required";
    } else if (values.password.length < 6 || values.password.length > 72) {
        errors.password = "Password must be 6 to 72 characters";
    }

    if (values.delivery_address === "") {
        errors.delivery_address = "Delivery address is required";
    } else if (values.delivery_address.length > 200) {
        errors.delivery_address = "Delivery address must be at most 200 characters";
    }

    return errors;
}

// Shows the API's 422 errors under the matching fields.
function showServerValidationErrors(detail) {
    let shown = false;
    for (const error of detail) {
        const field = error.loc[error.loc.length - 1];
        if (FIELDS.includes(field)) {
            showFieldError(field, error.msg);
            shown = true;
        }
    }
    if (!shown) {
        formError.textContent = "Some of the details you entered are not valid.";
    }
}

form.addEventListener("submit", async function (event) {
    event.preventDefault();
    clearErrors();

    const values = readValues();
    const errors = validate(values);
    const badFields = Object.keys(errors);
    if (badFields.length > 0) {
        for (const field of badFields) {
            showFieldError(field, errors[field]);
        }
        document.getElementById(badFields[0]).focus();
        return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Registering...";

    try {
        const response = await fetch(API_URL + "/customers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(values),
        });

        if (response.status === 201) {
            formSuccess.textContent = "Account created! Taking you to sign in...";
            setTimeout(function () {
                window.location.href = SIGN_IN_PAGE;
            }, 1200);
            return;
        }

        if (response.status === 409) {
            showFieldError("email", "An account with this email already exists");
        } else if (response.status === 422) {
            const data = await response.json();
            showServerValidationErrors(data.detail);
        } else {
            formError.textContent = "Something went wrong. Please try again.";
        }
    } catch (networkError) {
        formError.textContent = "Could not reach the server. Check your connection and try again.";
    }

    submitButton.disabled = false;
    submitButton.textContent = "Register";
});