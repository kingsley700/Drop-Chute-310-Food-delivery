
import { loadCart, clearCart } from "./cart.js";
const statusElement = document.getElementById("restaurant-status");
const restaurantList = document.getElementById("restaurant-list");
let restaurants = [];
const customerId = 1; //TODO: Replace with actual customer ID when authentication is implemented


async function loadRestaurants() {
    statusElement.textContent = "Loading restaurants...";

    try {
        const response = await fetch("http://127.0.0.1:8000/restaurants");

        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }

        restaurants = await response.json();
        displayRestaurants();

        if (restaurants.length === 0) {
            statusElement.textContent = "No restaurants found.";
        } else {
            statusElement.textContent =
                `${restaurants.length} restaurant found.`;
        }

        await loadCart(customerId, restaurants);

    } catch (error) {
        console.error("Could not load restaurants:", error);
        statusElement.textContent = "Unable to load restaurants. Please try again.";
    }
}


function displayRestaurants() {
    restaurantList.replaceChildren();

    for (const restaurant of restaurants) {
        const listItem = document.createElement("li");
        const button = document.createElement("button");

        button.textContent = restaurant.name;
        button.addEventListener("click", () => {
            showRestaurantDetails(restaurant.id);
        });

        listItem.appendChild(button);
        restaurantList.appendChild(listItem);
    }
}


function showRestaurantDetails(restaurantId) {
    const restaurant = restaurants.find(restaurant => restaurant.id === restaurantId);

    if (!restaurant) {
        return;
    }

    document.getElementById("restaurant-view").hidden = true;
    document.getElementById("restaurant-details").hidden = false;
    document.getElementById("details-name").textContent = restaurant.name;
    document.getElementById("details-cuisine").textContent = restaurant.cuisine;

    displayMenu(restaurant.items, restaurant.id);
}


function displayMenu(items, restaurantId) {
    const menuList = document.getElementById("menu-list");
    const menuStatus = document.getElementById("menu-status");

    menuList.replaceChildren();

    if (!items || items.length === 0) {
        menuStatus.textContent = "No menu items available.";
        return;
    }

    menuStatus.textContent = `${items.length} menu items`;

    for (const item of items) {
        const listItem = document.createElement("li");
        const name = document.createElement("h4");
        const price = document.createElement("p");
        const description = document.createElement("p");
        const button = document.createElement("button");

        name.textContent = item.name;
        price.textContent = formatPrice(item.price);
        description.textContent = item.description || "No description available";

        button.textContent = item.available === false ? "Unavailable" : "Add to Cart";
        button.disabled = item.available === false;

        button.addEventListener("click", () => {
            addToCart(restaurantId, item.name);
        });

        listItem.append(name, price, description, button);
        menuList.appendChild(listItem);
    }
}


async function addToCart(restaurantId, itemName) {
    try {
        const response = await fetch(
            `http://127.0.0.1:8000/customers/${customerId}/cart/items`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    restaurant_id: restaurantId,
                    item_name: itemName,
                    quantity: 1
                })
            }
        );

        const data = await response.json();

        console.log("Status:", response.status);
        console.log("Response:", data);

        if (!response.ok) {
            alert(data.detail || "Could not add item to cart.");
            return;
        }

        await loadCart(customerId, restaurants);

    } catch (error) {
        console.error("Could not add item:", error);
        alert(error.message);
    }
}


// Goes back to restaurant list
document.getElementById("back-button").addEventListener("click", () => {
    document.getElementById("restaurant-details").hidden = true;
    document.getElementById("restaurant-view").hidden = false;
});


// Formats prices
function formatPrice(price) {
    return Number(price).toLocaleString("en-CA", {
        style: "currency",
        currency: "CAD"
    });
}


// Refresh cart
document.getElementById("refresh-cart-button").addEventListener("click", () => {
    loadCart(customerId, restaurants);
});

// Clear cart
document.getElementById("clear-cart-button").addEventListener("click", () => {
    clearCart(customerId, restaurants);
});


// Start page
loadRestaurants();
