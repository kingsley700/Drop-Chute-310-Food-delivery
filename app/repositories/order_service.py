from uuid import uuid4

from fastapi import HTTPException

from app.repositories import order_repo
from app.schemas.order import Order
from app.services import checkout_service, cart_service


# Create order from validated cart
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

    # Save order before clearing cart
    created_order = order_repo.create_order(order)

    cart_service.clear_cart(customer_id)

    return created_order