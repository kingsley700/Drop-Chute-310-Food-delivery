# Restaurant IDs are permanent UUIDs.
# if something breaks or is needed to be added email: vassilios.simeonidi@gmail.com


import json
from uuid import UUID, uuid4

filep = "data/restaurants.json"


def get_restaurants():
    """Returns all restaurants."""
    return _read_data()


def get_restaurant_by_name(name: str):
    """Returns a restaurant based on name."""
    for restaurant in get_restaurants():
        if restaurant["name"].lower() == name.lower():
            return restaurant


def get_restaurant_by_id(restaurant_id: UUID):
    """Returns a restaurant based on ID."""
    for restaurant in get_restaurants():
        if restaurant["id"] == str(restaurant_id):
            return restaurant
    return None


def get_restaurants_by_owner(owner_id: int):
    """Returns the restaurants created by this customer."""
    owned = []
    for restaurant in get_restaurants():
        if restaurant.get("owner_id") == owner_id:
            owned.append(restaurant)
    return owned


def create_restaurant(restaurant: dict):
    """Creates a restaurant and assigns a permanent UUID."""
    restaurants = get_restaurants()
    new_restaurant = restaurant.copy()
    new_restaurant["id"] = str(uuid4())
    new_restaurant.setdefault("items", [])

    restaurants.append(new_restaurant)
    _write_data(restaurants)

    return new_restaurant


def update_restaurant_name(restaurant_id: UUID, name: str):
    """Updates a restaurants name."""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == str(restaurant_id):
            restaurant["name"] = name
            _write_data(restaurants)
            return restaurant

    return None


def update_restaurant_cuisine(restaurant_id: UUID, cuisine: str):
    """Updates a restaurants cuisine."""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == str(restaurant_id):
            restaurant["cuisine"] = cuisine
            _write_data(restaurants)
            return restaurant

    return None


def delete_restaurant(restaurant_id: UUID):
    """Deletes a restaurant."""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == str(restaurant_id):
            restaurants.remove(restaurant)
            _write_data(restaurants)
            return True

    return False


def add_restaurant_items(restaurant_id: UUID, item: dict):
    """Adds a menu item to a restaurant. ex: (1, add_restaurant_items{"name": "soup", "price": 3000})"""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == str(restaurant_id):
            if "items" not in restaurant:
                restaurant["items"] = []

            restaurant["items"].append(item)
            _write_data(restaurants)
            return item

    return None


def update_restaurant_item(
    restaurant_id: UUID,
    item_name: str,
    new_name: str | None = None,
    price: float | None = None,
    description: str | None = None,
    available: bool | None = None,
):
    """Updates a menu item's name, price, description, or availability."""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == str(restaurant_id):
            for item in restaurant.get("items", []):
                if item["name"] == item_name:
                    if new_name is not None:
                        item["name"] = new_name
                    if price is not None:
                        item["price"] = price
                    if description is not None:
                        item["description"] = description
                    if available is not None:
                        item["available"] = available

                    _write_data(restaurants)
                    return item

    return None


def delete_restaurant_item(restaurant_id: UUID, item_name: str):
    """Deletes a menu item from a restaurant."""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == str(restaurant_id):
            items = restaurant.get("items", [])

            for index, item in enumerate(items):
                if item["name"] == item_name:
                    del items[index]
                    _write_data(restaurants)
                    return True
            return False
    return False


def _read_data():
    """Reads restaurants from the JSON file."""
    with open(filep, "r", encoding="utf-8") as file:
        return json.load(file)


def _write_data(restaurants):
    """Writes restaurants to the JSON file."""
    with open(filep, "w", encoding="utf-8") as file:
        json.dump(restaurants, file, indent=2, ensure_ascii=False)
