
const customerId = getCustomerId();

const statusElement = document.getElementById("checkout-status");
const itemsElement = document.getElementById("checkout-items");
const totalElement = document.getElementById("checkout-total");
const placeOrderButton = document.getElementById("place-order-button");

if (customerId === null) {
    window.location.href = "login.html";
}



async function validateCheckout() {
    try {
        const response = await apiFetch(
            `/customers/${customerId}/checkout/validate`,
            { method: "POST" }
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
        console.error(error);
        statusElement.textContent = "Could not reach the server. Please try again.";
    }
}


// Display cart
function displayCheckout(cart) {
    itemsElement.replaceChildren();
    statusElement.textContent = "Review your order before placing it.";

    for (const item of cart.items) {
        const li = document.createElement("li");
        li.textContent = `${item.name} - ${formatPrice(item.price)} x ${item.quantity}`;
        itemsElement.appendChild(li);
    }

    document.getElementById("checkout-subtotal").textContent =
        `Subtotal: ${formatPrice(cart.subtotal)}`;

    document.getElementById("checkout-tax").textContent =
        `Tax: ${formatPrice(cart.tax)}`;

    document.getElementById("checkout-grand-total").textContent =
        `Total: ${formatPrice(cart.total)}`;

    totalElement.hidden = false;
}


// Create order
placeOrderButton.addEventListener("click", async () => {
    placeOrderButton.disabled = true;
    statusElement.textContent = "Creating your order...";

    try {
        const response = await apiFetch(
            `/customers/${customerId}/orders`,
            { method: "POST" }
        );

        const data = await response.json();

        if (!response.ok) {
            statusElement.textContent =
                data.detail || "Could not create your order.";
            placeOrderButton.disabled = false;
            return;
        }

        window.location.href = `order-details.html?order_id=${data.id}`;

    } catch (error) {
        console.error(error);
        statusElement.textContent = "Could not reach the server. Please try again.";
        placeOrderButton.disabled = false;
    }
});


// Cancel checkout
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


// Start page
if (customerId !== null) {
    validateCheckout();
}
