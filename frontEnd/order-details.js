
const customerId = getCustomerId();
const orderId = new URLSearchParams(window.location.search).get("order_id");

const status = document.getElementById("order-status");
const details = document.getElementById("order-details");
const items = document.getElementById("order-items");



async function loadOrder() {
    if (customerId === null) {
        window.location.href = "login.html";
        return;
    }

    if (!orderId) {
        status.textContent = "No order ID provided.";
        return;
    }

    try {
        const response = await apiFetch(
            `/customers/${customerId}/orders/${orderId}`
        );

        const order = await response.json();

        if (!response.ok) {
            status.textContent = order.detail || "Could not load order.";
            return;
        }

        const restaurantResponse = await apiFetch("/restaurants");
        const restaurants = await restaurantResponse.json();

        const restaurant = restaurants.find(
            r => r.id === order.restaurant_id
        );

        displayOrder(order, restaurant);

    } catch (error) {
        console.error(error);
        status.textContent = "Unable to load order.";
    }
}



function displayOrder(order, restaurant) {
    status.textContent = "Order loaded successfully.";

    document.getElementById("restaurant-name").textContent =
        restaurant ? restaurant.name : "Restaurant unavailable";

    items.replaceChildren();

    for (const item of order.items) {
        const li = document.createElement("li");
        li.textContent = `${item.name} - ${formatPrice(item.price)} x ${item.quantity}`;
        items.appendChild(li);
    }

    document.getElementById("order-subtotal").textContent =
        `Subtotal: ${formatPrice(order.subtotal)}`;

    document.getElementById("order-tax").textContent =
        `Tax: ${formatPrice(order.tax)}`;

    document.getElementById("order-total").textContent =
        `Total: ${formatPrice(order.total)}`;

    document.getElementById("order-date").textContent =
        `Date: ${new Date(order.created_at).toLocaleString()}`;

    document.getElementById("order-number").textContent =
        `Order ID: ${order.id}`;

    details.hidden = false;
}



function formatPrice(price) {
    return Number(price).toLocaleString("en-CA", {
        style: "currency",
        currency: "CAD"
    });
}


// Return to shopping
document.getElementById("back-button").addEventListener("click", () => {
    window.location.href = "customer.html";
});

loadOrder();
