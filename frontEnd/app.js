const statusElement =
    document.getElementById("restaurant-status");
const restaurantList =
    document.getElementById("restaurant-list");
async function loadRestaurants() {

    statusElement.textContent = "Loading restaurants...";


    try {
        const response = await fetch(
            "http://127.0.0.1:8000/restaurants" 
        );

        if(!response.ok) {
            throw new Error(
                `HTTP error ${response.status}`
            );

        }

        const restaurants = await response.json();

        displayRestaurants(restaurants);

        if (restaurants.length === 0) {
            statusElement.textContent = "No restaurants found.";
        } else {
            statusElement.textContent =
                `${restaurants.length} restaurant found.`;
        }

    } catch (error){
        console.error("Could not load restaurants: ", error);

        statusElement.textContent = 
            "Unable to load restaurants. Please try again.";
    }
}
loadRestaurants();
function displayRestaurants(restaurants) {
    restaurantList.replaceChildren();

    for (const restaurant of restaurants) {
        const listItem = document.createElement("li");

        listItem.textContent =
            `${restaurant.name} - ${restaurant.cuisine}`;

            restaurantList.appendChild(listItem);
    }
}
