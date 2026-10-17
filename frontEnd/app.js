const statusElement =
    document.getElementById("restaurant-status");
const restaurantList =
    document.getElementById("restaurant-list");

let restaurants = [];

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

        restaurants = await response.json();

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
        const button = document.createElement("button");

        button.type = "button";
        button.textContent =
            `${restaurant.name} - ${restaurant.cuisine}`;

        button.addEventListener("click", () => {
            showRestaurantDetails(restaurant.id);
        });

            listItem.appendChild(button);
            restaurantList.appendChild(listItem);
    }
}
function showRestaurantDetails(restaurantId) {
    const restaurant = restaurants.find(
        restaurant => restaurant.id === restaurantId
    );

    if (!restaurant) {
        statusElement.textContent = "Restaurant not found.";
        return;
    }

    document.getElementById("restaurant-view").hidden = true;
    document.getElementById("restaurant-details").hidden = false;

    document.getElementById("details-name").textContent = restaurant.name;
    document.getElementById("details-cuisine").textContent = restaurant.cuisine;

    displayMenu(restaurant.items);  
}

