const LOGIN_PAGE = "login.html";

// Not signed in: go to the sign-in page
if (getToken() === null) {
    window.location.href = LOGIN_PAGE;
}

const pageError = document.getElementById("page-error");
const details = document.getElementById("account-details");
const restaurantSelect = document.getElementById("restaurant-select");
const settingsForm = document.getElementById("settings-form");
const nameInput = document.getElementById("restaurant-name");
const cuisineInput = document.getElementById("restaurant-cuisine");
const saveMessage = document.getElementById("save-message");
const saveButton = document.getElementById("save-button");

const FIELDS = ["restaurant-name", "restaurant-cuisine"];

let restaurants = [];
let restaurantId = null;


// A 401 on a request that carried a token means it is no longer valid
function sessionEnded() {
    clearToken();
    window.location.href = LOGIN_PAGE;
}

function errorMessageFor(status) {
    if (status === 403) {
        return "You do not have access to this restaurant.";
    }
    if (status === 404) {
        return "Restaurant not found.";
    }
    return "Something went wrong. Please try again.";
}

function clearErrors() {
    for (const field of FIELDS) {
        document.getElementById(field + "-error").textContent = "";
        document.getElementById(field).classList.remove("invalid");
    }
    saveMessage.textContent = "";
}

function showFieldError(field, message) {
    document.getElementById(field + "-error").textContent = message;
    document.getElementById(field).classList.add("invalid");
}

function fillSelect() {
    restaurantSelect.replaceChildren();
    for (const restaurant of restaurants) {
        const option = document.createElement("option");
        option.value = restaurant.id;
        option.textContent = restaurant.name + " - " + restaurant.cuisine;
        restaurantSelect.appendChild(option);
    }
}

function showRestaurant(restaurant) {
    restaurantId = restaurant.id;
    restaurantSelect.value = restaurant.id;
    document.getElementById("info-name").textContent = restaurant.name;
    document.getElementById("info-cuisine").textContent = restaurant.cuisine;
    nameInput.value = restaurant.name;
    cuisineInput.value = restaurant.cuisine;
    details.hidden = false;
}

async function loadRestaurants() {
    try {
        // Only the restaurants created by the signed-in account
        const response = await apiFetch("/restaurants/mine");

        if (response.status === 401) {
            sessionEnded();
            return;
        }
        if (response.status !== 200) {
            pageError.textContent = errorMessageFor(response.status);
            return;
        }

        restaurants = await response.json();
        if (restaurants.length === 0) {
            pageError.textContent = "You have not created any restaurants yet. Create one on the restaurant page.";
            return;
        }

        fillSelect();
        showRestaurant(restaurants[0]);
    } catch (networkError) {
        pageError.textContent = "Could not reach the server. Check your connection and try again.";
    }
}

restaurantSelect.addEventListener("change", function () {
    clearErrors();
    for (const restaurant of restaurants) {
        if (restaurant.id === restaurantSelect.value) {
            showRestaurant(restaurant);
            return;
        }
    }
});

settingsForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    clearErrors();

    const name = nameInput.value.trim();
    const cuisine = cuisineInput.value.trim();

    let valid = true;
    if (name === "") {
        showFieldError("restaurant-name", "Name is required");
        valid = false;
    }
    if (cuisine === "") {
        showFieldError("restaurant-cuisine", "Cuisine is required");
        valid = false;
    }
    if (!valid) {
        return;
    }

    saveButton.disabled = true;

    try {
        const response = await apiFetch("/restaurants/" + restaurantId, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name, cuisine: cuisine }),
        });

        if (response.status === 200) {
            const updated = await response.json();
            for (let i = 0; i < restaurants.length; i++) {
                if (restaurants[i].id === updated.id) {
                    restaurants[i] = updated;
                }
            }
            fillSelect();
            showRestaurant(updated);
            saveMessage.textContent = "Settings saved.";
        } else if (response.status === 401) {
            sessionEnded();
            return;
        } else if (response.status === 422) {
            saveMessage.textContent = "Some of the details you entered are not valid.";
        } else {
            saveMessage.textContent = errorMessageFor(response.status);
        }
    } catch (networkError) {
        saveMessage.textContent = "Could not reach the server. Check your connection and try again.";
    }

    saveButton.disabled = false;
});

if (getToken() !== null) {
    loadRestaurants();
}