#resturaunt ids are non null numbered 1-2-3-4
#recommened upgrade later use some hashmap or similar


import json

filep = "data/restaurants.json"


def get_restaurants():
    """Returns all restaurants."""
    return _read_data()


def get_restaurant(restaurant_id: int):
    """Returns a restaurant based on ID."""
    for restaurant in get_restaurants():
        if restaurant["id"] == restaurant_id:
            return restaurant
    return None


def create_restaurant(restaurant: dict):
    """Creates a restaurant and assigns the next available id. requires a name at minimum"""
    restaurants = get_restaurants()
    new_restaurant = restaurant.copy()
    new_restaurant["id"] = len(restaurants) + 1
    new_restaurant.setdefault("items", [])

    restaurants.append(new_restaurant)
    _write_data(restaurants)

    return new_restaurant

def update_restaurant_name(restaurant_id: int, name: str):
    """Updates a restaurants name."""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            restaurant["name"] = name
            _write_data(restaurants)
            return restaurant

    return None


def update_restaurant_cuisine(restaurant_id: int, cuisine: str):
    """Updates a restaurants cuisine."""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            restaurant["cuisine"] = cuisine
            _write_data(restaurants)
            return restaurant

    return None


def delete_restaurant(restaurant_id: int):
    """Deletes a restaurant and renumbers IDs."""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            restaurants.remove(restaurant)
            for index, item in enumerate(restaurants):
                item["id"] = index + 1
            _write_data(restaurants)
            return True
        
    return False


def add_restaurant_items(restaurant_id: int, item: dict):
    """Adds a menu item to a restaurant. ex: (1, add_restaurant_items{"name": "soup", "price": 3000})"""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            if "items" not in restaurant:
                restaurant["items"] = []

            restaurant["items"].append(item)
            _write_data(restaurants)
            return item



def update_restaurant_item(restaurant_id: int, item_name: str, new_name: str | None = None, price: float | None = None, description: str | None = None):
    """Updates a menu item's name, price, or description."""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            for item in restaurant.get("items", []):
                if item["name"] == item_name:
                    if new_name is not None:
                        item["name"] = new_name
                    if price is not None:
                        item["price"] = price
                    if description is not None:
                        item["description"] = description

                    _write_data(restaurants)
                    return item

    return None



def delete_restaurant_item(restaurant_id: int, item_name: str):
    """Deletes a menu item from a restaurant."""
    restaurants = _read_data()

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            items = restaurant.get("items", [])

            for index, item in enumerate(items):
                if item["name"] == item_name:
                    del items[index]
                    _write_data(restaurants)


def swap_restaurant_id(restaurant_id: int, new_id: int):
    """Swaps a restaurants ID with the second resturaunts ID."""
    restaurants = _read_data()
    rest1 = None
    rest2 = None

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            rest1 = restaurant
        if restaurant["id"] == new_id:
            rest2 = restaurant

    if rest1 is None or rest2 is None:
        return None

    rest1["id"], rest2["id"] = rest2["id"], rest1["id"] #python made this so much easier than java

    restaurants.sort(key=lambda item: item["id"])
    _write_data(restaurants)



def _read_data():
    """Reads restaurants from the JSON file."""
    with open(filep, "r", encoding="utf-8") as file:
        return json.load(file)


def _write_data(restaurants):
    """Writes restaurants to the JSON file."""
    with open(filep, "w", encoding="utf-8") as file:
        json.dump(restaurants, file, indent=2, ensure_ascii=False)


def get_restaurant(name: str):
    """Returns a restaurant based on name."""
    for restaurant in get_restaurants():
        if restaurant["name"].lower() == name.lower():
            return restaurant
    return None