from fastapi import APIRouter
from app.services.restaurant_services import *
from app.schemas.restaurantschemas import *

router = APIRouter()


@router.get("/restaurants", response_model=list[Restaurant], summary = "List all restaurants",
            description = "Returns every restaurant with its cuisine and menu items. No parameters, returns empty list if no restaurants available.",
            responses = {500: {"description": "The restaurant data file could not be read"}}
            )

def restaurant_list():
    return get_restaurants()

@router.post("/CreateRestaurant",response_model=Restaurant, summary="Create a new restaurant",
    description="Creates a new restaurant with a name, cuisine, and optional menu items. The ID is assigned automatically.",
    status_code=201,
    responses={500: {"description": "The restaurant data file could not be written"}}
)
def create_new_restaurant(restaurant: Restaurant):
    return create_restaurant(restaurant)


@router.post("/restaurants/{restaurant_id}/items",summary="Create a new menu item",
    description="Adds a new menu item to the restaurant with the specified ID.",
    status_code=201,
    responses={
        404: {"description": "Restaurant not found"},
        500: {"description": "The restaurant data file could not be written"}
    })
def create_new_item(restaurant_id: int, item: RestaurantItem):
    return add_restaurant_items(restaurant_id, item)


@router.patch("/restaurants/{restaurant_id}",summary="Update a restaurant",
    description="Updates the name or cuisine of the restaurant with the specified ID. Only provided fields are updated.",
    responses={
        404: {"description": "Restaurant not found"},
        500: {"description": "The restaurant data file could not be written"}
    })
def update_restaurant(restaurant_id: int, updates: RestaurantUpdate):
    result = None
    if updates.name is not None:
        result = update_restaurant_name(restaurant_id, updates.name)
    if updates.cuisine is not None:
        result = update_restaurant_cuisine(restaurant_id, updates.cuisine)
    return result


@router.patch(
    "/restaurants/{restaurant_id}/items/{item_name}",
    summary="Update a menu item",
    description="Updates the name, price, or description of a menu item in the specified restaurant. Only provided fields are updated.",
    responses={
        404: {"description": "Restaurant or menu item not found"},
        500: {"description": "The restaurant data file could not be written"}
    }
)
def update_item(restaurant_id: int,item_name: str,updates: RestaurantItemUpdate):
    return update_restaurant_item(restaurant_id,item_name,new_name=updates.name,
            price=updates.price,description=updates.description)