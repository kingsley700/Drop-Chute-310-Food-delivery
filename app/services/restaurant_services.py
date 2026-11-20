from uuid import UUID

from app.repositories import restaurant_repository
from app.schemas.restaurantschemas import RestaurantCreate, RestaurantItem


def get_restaurants():
    """Returns all restaurants."""
    return restaurant_repository.get_restaurants()


def get_restaurant_by_id(restaurant_id: UUID):
    """Returns a restaurant based on ID."""
    return restaurant_repository.get_restaurant_by_id(restaurant_id)


def create_restaurant(restaurant: RestaurantCreate):
    """Creates a restaurant and assigns a permanent UUID."""
    return restaurant_repository.create_restaurant(restaurant.model_dump())


def update_restaurant_name(restaurant_id: UUID, name: str):
    """Updates a restaurants name."""
    result = restaurant_repository.update_restaurant_name(restaurant_id, name)
    if result is None:
        raise ValueError("Restaurant not found")

    return result

def update_restaurant_cuisine(restaurant_id: UUID, cuisine: str):
    """Updates a restaurants cuisine."""
    result = restaurant_repository.update_restaurant_cuisine(restaurant_id, cuisine)
    if result is None:
        raise ValueError("Restaurant not found")

    return result

def delete_restaurant(restaurant_id: UUID):
    """Deletes a restaurant."""
    return restaurant_repository.delete_restaurant(restaurant_id)


def add_restaurant_items(restaurant_id: UUID, item: RestaurantItem):
    """Adds a menu item to a restaurant. ex: (1, add_restaurant_items{"name": "soup", "price": 3000})"""
    result = restaurant_repository.add_restaurant_items(restaurant_id, item.model_dump())
    if result is None:
        raise ValueError("Restaurant not found")

    return result



def update_restaurant_item(restaurant_id: UUID, item_name: str, new_name: str | None = None, price: float | None = None, description: str | None = None, available: bool | None = None):
    """Updates a menu item's name, price, description, or availability."""
    result = restaurant_repository.update_restaurant_item(restaurant_id, item_name, new_name, price, description, available)
    if result is None:
        raise ValueError("Restaurant or menu item not found")

    return result


def delete_restaurant_item(restaurant_id: UUID, item_name: str):
    """Deletes a menu item from a restaurant."""
    result = restaurant_repository.delete_restaurant_item(restaurant_id, item_name)
    if result is False:
        raise ValueError("Restaurant not found")

    return result



def get_restaurant_by_name(name: str):
    """Returns a restaurant based on name."""
    return restaurant_repository.get_restaurant_by_name(name)
