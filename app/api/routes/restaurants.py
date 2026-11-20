from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from app.api.routes.dependencies import get_signed_in_customer
from app.schemas.customerschema import Customer
from app.services.restaurant_services import *
from app.schemas.restaurantschemas import *

router = APIRouter()

NOT_SIGNED_IN = {"description": "Not signed in, or the token is invalid or expired"}
NOT_YOUR_RESTAURANT = {"description": "The restaurant was created by someone else"}


def get_own_restaurant(restaurant_id: UUID, customer: Customer):
    """404 if the restaurant does not exist, 403 if it was created by someone else."""
    restaurant = get_restaurant_by_id(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.get("owner_id") != customer.id:
        raise HTTPException(
            status_code=403, detail="You do not have access to this restaurant"
        )
    return restaurant


@router.get(
    "/restaurants",
    response_model=list[Restaurant],
    summary="List all restaurants",
    description="Returns every restaurant with its cuisine and menu items. No parameters, returns empty list if no restaurants available.",
    responses={500: {"description": "The restaurant data file could not be read"}},
)
def restaurant_list():
    return get_restaurants()


@router.get(
    "/restaurants/mine",
    response_model=list[Restaurant],
    summary="List my restaurants",
    description="Returns only the restaurants created by the signed-in customer. Empty list if they have none.",
    responses={401: NOT_SIGNED_IN},
)
def my_restaurants(customer: Customer = Depends(get_signed_in_customer)):
    return get_restaurants_by_owner(customer.id)


@router.post(
    "/CreateRestaurant",
    response_model=Restaurant,
    summary="Create a new restaurant",
    description="Creates a new restaurant with a name, cuisine, and optional menu items. The ID is assigned automatically and the signed-in customer becomes its owner.",
    status_code=201,
    responses={
        401: NOT_SIGNED_IN,
        500: {"description": "The restaurant data file could not be written"},
    },
)
def create_new_restaurant(
    restaurant: RestaurantCreate, customer: Customer = Depends(get_signed_in_customer)
):
    return create_restaurant(restaurant, customer.id)


@router.post(
    "/restaurants/{restaurant_id}/items",
    summary="Create a new menu item",
    description="Adds a new menu item to the restaurant with the specified ID. Only the restaurant's owner can do this.",
    status_code=201,
    responses={
        401: NOT_SIGNED_IN,
        403: NOT_YOUR_RESTAURANT,
        404: {"description": "Restaurant not found"},
        500: {"description": "The restaurant data file could not be written"},
    },
)
def create_new_item(
    restaurant_id: UUID,
    item: RestaurantItem,
    customer: Customer = Depends(get_signed_in_customer),
):
    get_own_restaurant(restaurant_id, customer)
    try:
        return add_restaurant_items(restaurant_id, item)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.patch(
    "/restaurants/{restaurant_id}",
    summary="Update a restaurant",
    description="Updates the name or cuisine of the restaurant with the specified ID. Only provided fields are updated. Only the restaurant's owner can do this.",
    responses={
        401: NOT_SIGNED_IN,
        403: NOT_YOUR_RESTAURANT,
        404: {"description": "Restaurant not found"},
        500: {"description": "The restaurant data file could not be written"},
    },
)
def update_restaurant(
    restaurant_id: UUID,
    updates: RestaurantUpdate,
    customer: Customer = Depends(get_signed_in_customer),
):
    get_own_restaurant(restaurant_id, customer)
    try:
        if updates.name is not None:
            update_restaurant_name(restaurant_id, updates.name)
        if updates.cuisine is not None:
            update_restaurant_cuisine(restaurant_id, updates.cuisine)
        return get_restaurant_by_id(restaurant_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.patch(
    "/restaurants/{restaurant_id}/items/{item_name}",
    summary="Update a menu item",
    description="Updates the name, price, or description of a menu item in the specified restaurant. Only provided fields are updated. Only the restaurant's owner can do this.",
    responses={
        401: NOT_SIGNED_IN,
        403: NOT_YOUR_RESTAURANT,
        404: {"description": "Restaurant or menu item not found"},
        500: {"description": "The restaurant data file could not be written"},
    },
)
def update_item(
    restaurant_id: UUID,
    item_name: str,
    updates: RestaurantItemUpdate,
    customer: Customer = Depends(get_signed_in_customer),
):
    get_own_restaurant(restaurant_id, customer)
    try:
        return update_restaurant_item(
            restaurant_id,
            item_name,
            new_name=updates.name,
            price=updates.price,
            description=updates.description,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
