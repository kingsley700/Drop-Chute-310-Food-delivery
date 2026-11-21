from uuid import uuid4

from fastapi import HTTPException

from app.repositories import order_repo
from app.schemas.order import Order
from app.services import checkout_service, cart_service



def create_order(customer_id: int):
    cart = checkout_service.validate_checkout(customer_id)
    cart = checkout_service.validate_menu_items(cart)

    if cart is None:
        raise HTTPException(400, "Unable to create order")

    order = Order(
        id=0,
        customer_id=cart.customer_id,
        restaurant_id=cart.restaurant_id,
        items=[item.model_copy() for item in cart.items],
        subtotal=cart.subtotal,
        tax=cart.tax,
        total=cart.total,
        transaction_id=str(uuid4())
    )


    created_order = order_repo.create_order(order)
    cart_service.clear_cart(customer_id)

    return created_order


def get_order_by_id(customer_id: int, order_id: int):
    order = order_repo.get_order_by_id(order_id)

    if order is None:
        raise HTTPException(404, "Order not found")

    if order.customer_id != customer_id:
        raise HTTPException(403, "You cannot access this order")

    return order



def get_order_history(customer_id: int):
    return order_repo.get_orders_by_customer(customer_id)