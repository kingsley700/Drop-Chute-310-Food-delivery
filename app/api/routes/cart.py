from fastapi import APIRouter
from app.services.cart_service import *
from app.schemas.cart import *

router = APIRouter()


@router.get(
    "/customers/{customer_id}/cart",
    response_model=Cart,
    summary="Get customer's active cart",
    description="Returns the customer's active shopping cart. Creates one if none exists.",
    responses={
        403: {"description": "Customer is deactivated"},
        404: {"description": "Customer not found"}
    }
)
def get_customer_cart(customer_id: int):
    return get_or_create_cart(customer_id)


@router.post(
    "/customers/{customer_id}/cart",
    response_model=Cart,
    summary="Create or retrieve customer's active cart",
    description="Creates a new active cart if the customer does not already have one. Otherwise, returns the existing active cart.",
    responses={
        403: {"description": "Customer is deactivated"},
        404: {"description": "Customer not found"}
    }
)
def create_customer_cart(customer_id: int):
    return get_or_create_cart(customer_id)


@router.post(
    "/customers/{customer_id}/cart/items",
    response_model=Cart,
    summary="Add item to cart",
    description="Adds a menu item to the customer's active cart.",
    responses={
        400: {"description": "Item unavailable or restaurant mismatch"},
        403: {"description": "Customer is deactivated"},
        404: {"description": "Customer, restaurant, or menu item not found"},
        422: {"description": "Invalid quantity or request"}
    }
)
def add_cart_item(customer_id: int, item: CartItemCreate):
    return add_item_to_cart(
        customer_id,
        item.restaurant_id,
        item.item_name,
        item.quantity
    )