let restaurants = [];

async function loadRestaurants() {

    try {
        const response = await apiFetch(
            "/restaurants" 
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


const createForm = document.getElementById(
    "create-restaurant-form"
);

const createStatus = document.getElementById(
    "create-status"
);
createForm.addEventListener("submit", async function (event) {

    event.preventDefault

    const name = document.getElementById(
        "new-restaurant-name"
    ).value.trim();

    const cuisine = document.getElementById(
        "new-restaurant-cuisine"
    ).value.trim();

    if (!name || !cuisine) {
        createStatus.textContent =
            "Please enter a name and cuisine.";
            return;
    }

    const newRestaurant = {
        id: restaurants.length+1,
        name: name,
        cuisine: cuisine,
        items: []
    };

    createStatus.textContent = "Creating Restaurant...";

    try {

        const response = await apiFetch(
            "/CreateRestaurant",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(newRestaurant)
            }
        );

        if (!response.ok) {
            throw new Error(
                `Request failed ${response.status}`
            );
        }

        const createdRestaurant = await response.json();

        createStatus.textContent =
            `Successfully created ${createdRestaurant.name}!`;

            createForm.reset();

            await loadRestaurants();
    } catch (error) {
        console.error("Could not create restaurant:", error);

        createStatus.textContent =
            "Could not create restaurant. Check API and try again.";
    }
});
const managerItemRestaurant =
    document.getElementById("manager-item-restaurant");

function populateManagerRestaurantOptions(){
    managerItemRestaurant.replaceChildren();

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Choose a restaurant";

    managerItemRestaurant.appendChild(placeholder);

    for (const restaurant of restaurants) {
        const option = document.createElement("option");

        option.value=restaurant.id
        option.textContent =
            `${restaurant.name} - ${restaurant.cuisine}`;

        managerItemRestaurant.appendChild(option);
    }
}
const restaurantManagerStatus =
    document.getElementById("restaurant-manager-status");
const itemManagerStatus =
    document.getElementById("item-manager-status");

document.getElementById("manager-restaurant-form")
    .addEventListener("submit", function(event) {
        event.preventDefault();

        restaurantManagerStatus.textContent =
            "Restaurant creation interface selected" +
            "This operation is not connected yet.";
    });

document.getElementById("edit-restaurant-button")
    .addEventListener("click", function() {
        restaurantManagerStatus.textContent =
            "Restaurant editiing interface selected" +
            "This operation is not connected yet.";
    });

document.getElementById("delete-restaurant-button")
    .addEventListener("click", function() {
        restaurantManagerStatus.textContent = 
            "Restaurant delete interface selected" +
            "This operation is not connected yet.";
    });
document.getElementById("manager-item-form")
    .addEventListener("submit", function(event) {
        event.preventDefault();

        itemManagerStatus.textContent =
            "Menu item creation interface selected" +
            "This operation is not connected yet.";
    });
document.getElementById("edit-item-button")
    .addEventListener("click", function() {
        itemManagerStatus.textContent =
        "Menu item interface selected" +
        "This operation is not connected yet.";
    });
document.getElementById("delete-item-button")
    .addEventListener("click", function() {
        itemManagerStatus.textContent =
        "Menu item delete interface selected" +
        "This operation is not connected yet.";
    });