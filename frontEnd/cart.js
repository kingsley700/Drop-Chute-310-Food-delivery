
export async function loadCart(customerId, restaurants) {
    const cartStatus = document.getElementById("cart-status");
    const cartItems = document.getElementById("cart-items");
    const cartTotals = document.getElementById("cart-totals");

    cartStatus.textContent = "Loading cart...";
    cartItems.replaceChildren();
    cartTotals.hidden = true;

    try {
        const response = await apiFetch(
            `/customers/${customerId}/cart`
        );

        if (response.status === 404) {
            displayEmptyCart();
            return;
        }

        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }

        const cart = await response.json();

        displayCart(cart, restaurants, customerId);

    } catch (error) {
        console.error("Could not load cart:", error);
        cartStatus.textContent = "Unable to load your cart.";
    }
}


export function displayCart(cart, restaurants, customerId) {
    const cartStatus = document.getElementById("cart-status");
    const cartItems = document.getElementById("cart-items");
    const cartRestaurant = document.getElementById("cart-restaurant");
    const cartTotals = document.getElementById("cart-totals");

    cartItems.replaceChildren();

    if (!cart.items || cart.items.length === 0) {
        displayEmptyCart();
        return;
    }

    cartStatus.textContent = "Your selected items:";

    const restaurant = restaurants.find(restaurant => restaurant.id === cart.restaurant_id);

    cartRestaurant.textContent = restaurant
        ? `Restaurant: ${restaurant.name} - ${restaurant.cuisine}`
        : `Restaurant ID: ${cart.restaurant_id}`;

    for (const item of cart.items) {
        const listItem = document.createElement("li");
        const text = document.createElement("span");
        const button = document.createElement("button");

        text.textContent =
            `${item.name} - ${formatPrice(item.price)} x ${item.quantity}`;

        button.textContent = "Remove";
        button.addEventListener("click", () => {
            removeCartItem(customerId, item.name, restaurants);
        });

        listItem.append(text, button);
        cartItems.appendChild(listItem);
    }

    document.getElementById("cart-subtotal").textContent =
        `Subtotal: ${formatPrice(cart.subtotal)}`;

    document.getElementById("cart-tax").textContent =
        `Tax: ${formatPrice(cart.tax)}`;

    document.getElementById("cart-total").textContent =
        `Total: ${formatPrice(cart.total)}`;

    cartTotals.hidden = false;
}


// Removes an item from the cart
async function removeCartItem(customerId, itemName, restaurants) {
    try {
        const response = await apiFetch(
            `/customers/${customerId}/cart/items/${encodeURIComponent(itemName)}`,
            {
                method: "DELETE"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Could not remove item.");
            return;
        }

        await loadCart(customerId, restaurants);

    } catch (error) {
        console.error("Could not remove item:", error);
        alert("Unable to remove item from cart.");
    }
}


export function displayEmptyCart() {
    document.getElementById("cart-status").textContent = "Your cart is empty.";
    document.getElementById("cart-items").replaceChildren();
    document.getElementById("cart-restaurant").textContent = "";
    document.getElementById("cart-totals").hidden = true;
}


export function formatPrice(price) {
    return Number(price).toLocaleString("en-CA", {
        style: "currency",
        currency: "CAD"
    });
}


export async function clearCart(customerId, restaurants) {
    try {
        const response = await apiFetch(
            `/customers/${customerId}/cart`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }

        await loadCart(customerId, restaurants);

    } catch (error) {
        console.error("Could not clear cart:", error);
        alert("Could not clear your cart.");
    }
}