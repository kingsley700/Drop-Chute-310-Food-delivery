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
        populateManagerRestaurantOptions();

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
function displayMenu(items) {
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

        name.textContent = item.name;

        price.textContent = Number(item.price).toLocaleString(
            "en-CA",
            {
                style: "currency",
                currency: "CAD"
            }
        );

        description.textContent =
            item.description || "No description available";

        listItem.append(name, price, description);
        menuList.appendChild(listItem);
    }
}

document.getElementById("back-button")
    .addEventListener("click", () => {
        document.getElementById("restaurant-details").hidden = true;
        document.getElementById("restaurant-view").hidden = false;
    });

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
        name: name,
        cuisine: cuisine
    };

    createStatus.textContent = "Creating Restaurant...";

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/CreateRestaurant",
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