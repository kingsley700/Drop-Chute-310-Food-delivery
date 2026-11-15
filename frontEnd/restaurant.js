let restaurants = [];

async function loadRestaurants() {

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
        populateManagerRestaurantOptions();

    } catch (error){
        console.error("Could not load restaurants: ", error);

        document.getElementById("restaurant-manager-status").textContent = 
            "Unable to load restaurants. Please try again.";
    }
}
loadRestaurants();