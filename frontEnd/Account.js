const LOGIN_PAGE = "login.html";

const customerId = getCustomerId();
if (customerId === null) {
    window.location.href = LOGIN_PAGE;
}

const pageError = document.getElementById("page-error");
const details = document.getElementById("account-details");
const addressForm = document.getElementById("address-form");
const addressInput = document.getElementById("delivery-address");
const addressError = document.getElementById("delivery-address-error");
const saveMessage = document.getElementById("save-message");
const saveButton = document.getElementById("save-button");
const deactivateButton = document.getElementById("deactivate-button");


// A 401 on a request that carried a token means it expired or the account is inactive

async function loadAccount() {
    try {
        const response = await apiFetch("/customers/" + customerId);

        if (response.status === 200) {
            const customer = await response.json();
            document.getElementById("name").textContent = customer.name;
            document.getElementById("email").textContent = customer.email;
            addressInput.value = customer.delivery_address;
            details.hidden = false;
        } else {
            pageError.textContent = errorMessageFor(response.status);
        }
    } catch (networkError) {
        pageError.textContent = "Could not reach the server. Check your connection and try again.";
    }
}

addressForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    addressError.textContent = "";
    addressInput.classList.remove("invalid");
    saveMessage.textContent = "";

    const address = addressInput.value.trim();
    if (address === "") {
        addressError.textContent = "Delivery address is required";
        addressInput.classList.add("invalid");
        return;
    }

    saveButton.disabled = true;

    try {
        const response = await apiFetch("/customers/" + customerId, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ delivery_address: address }),
        });

        if (response.status === 200) {
            const customer = await response.json();
            addressInput.value = customer.delivery_address;
            saveMessage.textContent = "Address saved.";
        } else if (response.status === 422) {
            addressError.textContent = "Delivery address must be 1 to 200 characters";
            addressInput.classList.add("invalid");
        } else {
            saveMessage.textContent = errorMessageFor(response.status);
        }
    } catch (networkError) {
        saveMessage.textContent = "Could not reach the server. Check your connection and try again.";
    }

    saveButton.disabled = false;
});

deactivateButton.addEventListener("click", async function () {
    const sure = window.confirm(
        "Deactivate your account? You will be signed out and will not be able to sign in again."
    );
    if (!sure) {
        return;
    }

    deactivateButton.disabled = true;

    try {
        const response = await apiFetch("/customers/" + customerId + "/deactivate", {
            method: "POST",
        });

        if (response.status === 204) {
            clearToken();
            window.location.href = LOGIN_PAGE;
            return;
        }
        pageError.textContent = errorMessageFor(response.status);
    } catch (networkError) {
        pageError.textContent = "Could not reach the server. Check your connection and try again.";
    }

    deactivateButton.disabled = false;
});

if (customerId !== null) {
    loadAccount();
}