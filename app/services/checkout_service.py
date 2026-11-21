from fastapi import HTTPException

from app.repositories import customer_repository, cart_repo
from app.services import restaurant_services


# Validate checkout
def validate_checkout(customer_id: int):
    customer = customer_repository.get_customer_by_id(customer_id)

    if customer is None:
        raise HTTPException(404, "Customer not found")
    if not customer.is_active:
        raise HTTPException(403, "Customer is deactivated")

    cart = cart_repo.get_cart_by_customer(customer_id)

    if cart is None:
        raise HTTPException(404, "Cart not found")
    if cart.status != "active":
        raise HTTPException(400, "Cart is not active")
    if not cart.items:
        raise HTTPException(400, "Cart is empty")
    if cart.restaurant_id is None:
        raise HTTPException(400, "Cart has no restaurant")

    for item in cart.items:
        if not isinstance(item.quantity, int) or isinstance(item.quantity, bool) or item.quantity <= 0:
            raise HTTPException(400, "Invalid quantity")

    return cart


# Validate menu items and update prices
def validate_menu_items(cart):
    restaurant = restaurant_services.get_restaurant_by_id(cart.restaurant_id)

    if restaurant is None:
        raise HTTPException(404, "Restaurant not found")

    subtotal = 0

    for item in cart.items:
        menu_item = next(
            (menu for menu in restaurant.get("items", []) if menu["name"] == item.name),
            None
        )

        if menu_item is None:
            raise HTTPException(404, "Menu item not found")
        if not menu_item.get("available", True):
            raise HTTPException(400, "Menu item unavailable")

        item.price = menu_item["price"]
        subtotal += item.price * item.quantity

    cart.subtotal = round(subtotal, 2)
    cart.tax = round(subtotal * 0.12, 2)
    cart.total = round(cart.subtotal + cart.tax, 2)

    return cart
