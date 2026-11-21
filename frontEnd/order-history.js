const customerId = getCustomerId();

const status = document.getElementById("order-status");
const history = document.getElementById("order-history");



async function loadOrderHistory() {
    if (customerId === null) {
        window.location.href = "login.html";
        return;
    }

    try {
        const response = await apiFetch(
            `/customers/${customerId}/orders`
        );

        const orders = await response.json();

        if (!response.ok) {
            status.textContent = orders.detail || "Could not load order history.";
            return;
        }

        if (orders.length === 0) {
            status.textContent = "You have no previous orders.";
            return;
        }

        const restaurantResponse = await apiFetch("/restaurants");
        const restaurants = await restaurantResponse.json();

        if (!restaurantResponse.ok) {
            status.textContent = "Could not load restaurant information.";
            return;
        }

        displayOrders(orders, restaurants);

    } catch (error) {
        console.error(error);
        status.textContent = "Unable to load order history.";
    }
}



function displayOrders(orders, restaurants) {
    status.textContent = "";

    history.replaceChildren();

    for (const order of orders) {
        const restaurant = restaurants.find(
            r => r.id === order.restaurant_id
        );

        const section = document.createElement("section");

        const title = document.createElement("h2");
        title.textContent = `Order #${order.id}`;

        const restaurantName = document.createElement("p");
        restaurantName.textContent = restaurant
            ? restaurant.name
            : "Restaurant unavailable";

        const date = document.createElement("p");
        date.textContent =
            `Date: ${new Date(order.created_at).toLocaleString()}`;

        const total = document.createElement("p");
        total.textContent = `Total: ${formatPrice(order.total)}`;

        const button = document.createElement("button");
        button.textContent = "View Details";
        button.addEventListener("click", () => {
            window.location.href = `order-details.html?order_id=${order.id}`;
        });

        section.appendChild(title);
        section.appendChild(restaurantName);
        section.appendChild(date);
        section.appendChild(total);
        section.appendChild(button);

        history.appendChild(section);
    }
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

loadOrderHistory();