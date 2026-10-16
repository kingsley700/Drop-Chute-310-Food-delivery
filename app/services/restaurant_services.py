#resturaunt ids are non null numbered and ordered 1-2-3-4
#recommened upgrade later use some hashmap or similar
from app.repositories import restaurant_repository
from app.schemas.restaurantschemas import Restaurant, RestaurantItem


def get_restaurants():
    """Returns all restaurants."""
    return restaurant_repository.get_restaurants()


def get_restaurant(restaurant_id: int):
    """Returns a restaurant based on ID."""
    return restaurant_repository.get_restaurant(restaurant_id)


def create_restaurant(restaurant: Restaurant):
    """Creates a restaurant and assigns the next available id. requires a name at minimum"""
    #note: id is automatically assigened at the repo level
    return restaurant_repository.create_restaurant(restaurant.model_dump(exclude={"id"}))


def update_restaurant_name(restaurant_id: int, name: str):
    """Updates a restaurants name."""
    return restaurant_repository.update_restaurant_name(restaurant_id, name)


def update_restaurant_cuisine(restaurant_id: int, cuisine: str):
    """Updates a restaurants cuisine."""
    return restaurant_repository.update_restaurant_cuisine(restaurant_id, cuisine)


def delete_restaurant(restaurant_id: int):
    """Deletes a restaurant and renumbers IDs."""
    return restaurant_repository.delete_restaurant(restaurant_id)


def add_restaurant_items(restaurant_id: int, item: RestaurantItem):
    """Adds a menu item to a restaurant. ex: (1, add_restaurant_items{"name": "soup", "price": 3000})"""
    return restaurant_repository.add_restaurant_items(restaurant_id, item.model_dump())


def update_restaurant_item(restaurant_id: int, item_name: str, new_name: str | None = None, price: float | None = None, description: str | None = None):
    """Updates a menu item's name, price, or description."""
    return restaurant_repository.update_restaurant_item(restaurant_id, item_name, new_name, price, description)


def delete_restaurant_item(restaurant_id: int, item_name: str):
    """Deletes a menu item from a restaurant."""
    return restaurant_repository.delete_restaurant_item(restaurant_id, item_name)


def swap_restaurant_id(restaurant_id: int, new_id: int):
    """Swaps a restaurants ID with the second resturaunts ID."""
    return restaurant_repository.swap_restaurant_id(restaurant_id, new_id)

def get_restaurant(name: str):
    """Returns a restaurant based on name."""
    return restaurant_repository.get_restaurant(name)
