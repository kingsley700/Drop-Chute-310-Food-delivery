const customerId = getCustomerId();

const statusElement = document.getElementById("checkout-status");
const itemsElement = document.getElementById("checkout-items");
const totalElement = document.getElementById("checkout-total");
const placeOrderButton = document.getElementById("place-order-button");

if (customerId === null) {
    window.location.href = "login.html";
}

// Check the cart before checkout
async function validateCheckout() {
    try {
        const response = await apiFetch(
            `/customers/${customerId}/checkout/validate`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            statusElement.textContent =
                data.detail || "Your cart could not be checked.";
            return;
        }

        displayCheckout(data);
        placeOrderButton.disabled = false;

    } catch (error) {
        console.error("Could not validate checkout:", error);
        statusElement.textContent =
            "Could not reach the server. Please try again.";
    }
}

// Display the cart
function displayCheckout(cart) {
    itemsElement.replaceChildren();

    statusElement.textContent = "Review your order before placing it.";

    for (const item of cart.items) {
        const listItem = document.createElement("li");

        listItem.textContent =
            `${item.name} - ${formatPrice(item.price)} x ${item.quantity}`;

        itemsElement.appendChild(listItem);
    }

    document.getElementById("checkout-subtotal").textContent =
        `Subtotal: ${formatPrice(cart.subtotal)}`;

    document.getElementById("checkout-tax").textContent =
        `Tax: ${formatPrice(cart.tax)}`;

    document.getElementById("checkout-grand-total").textContent =
        `Total: ${formatPrice(cart.total)}`;

    totalElement.hidden = false;
}

// Create the order
placeOrderButton.addEventListener("click", async () => {
    placeOrderButton.disabled = true;
    statusElement.textContent = "Creating your order...";

    try {
        const response = await apiFetch(
            `/customers/${customerId}/orders`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            statusElement.textContent =
                data.detail || "Could not create your order.";
            placeOrderButton.disabled = false;
            return;
        }

        statusElement.textContent = "Order placed successfully!";
        itemsElement.replaceChildren();
        totalElement.hidden = true;

    } catch (error) {
        console.error("Could not create order:", error);
        statusElement.textContent =
            "Could not reach the server. Please try again.";
        placeOrderButton.disabled = false;
    }
});

// Cancel checkout and return to the cart
document.getElementById("cancel-button").addEventListener("click", () => {
    window.location.href = "customer.html";
});

// Format prices
function formatPrice(price) {
    return Number(price).toLocaleString("en-CA", {
        style: "currency",
        currency: "CAD"
    });
}

if (customerId !== null) {
    validateCheckout();
}