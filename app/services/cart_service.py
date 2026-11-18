from fastapi import HTTPException
from app.repositories import cart_repo, customer_repository
from app.services import restaurant_services
from app.schemas.cart import CartItem


def get_or_create_cart(customer_id: int):
    """Returns the customer's active cart or creates one."""

    customer = customer_repository.get_customer_by_id(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    if not customer.is_active:
        raise HTTPException(status_code=403, detail="Customer is deactivated")

    for cart in cart_repo.get_carts():
        if cart.customer_id == customer_id and cart.status == "active":
            return cart

    return cart_repo.create_cart(customer_id)


def add_item_to_cart(customer_id: int, restaurant_id: int, item_name: str, quantity: int):
    """Adds a menu item to the customer's active cart."""

    customer = customer_repository.get_customer_by_id(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    if not customer.is_active:
        raise HTTPException(status_code=403, detail="Customer is deactivated")

    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        raise HTTPException(status_code=422, detail="Quantity must be a positive integer")

    restaurant = restaurant_services.get_restaurant_by_id(restaurant_id)

    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    menu_item = None

    for item in restaurant.get("items", []):
        if item["name"] == item_name:
            menu_item = item
            break

    if menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    if not menu_item.get("available", True):
        raise HTTPException(status_code=400, detail="Menu item is unavailable")

    cart = cart_repo.get_cart_by_customer(customer_id)

    if cart is None:
        cart = get_or_create_cart(customer_id)

    if cart.restaurant_id is not None and cart.restaurant_id != restaurant_id:
        raise HTTPException(status_code=400, detail="Cart items must belong to the same restaurant")

    cart.restaurant_id = restaurant_id

    for item in cart.items:
        if item.name == item_name:
            item.quantity += quantity
            return cart_repo.update_cart(cart)

    cart.items.append(CartItem(
        name=menu_item["name"],
        price=menu_item["price"],
        quantity=quantity
    ))

    return cart_repo.update_cart(cart)

def update_cart_item_quantity(customer_id: int, item_name: str, quantity: int):
    """Updates the quantity of an item in the customer's cart."""

    customer = customer_repository.get_customer_by_id(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    if not customer.is_active:
        raise HTTPException(status_code=403, detail="Customer is deactivated")

    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        raise HTTPException(status_code=422, detail="Quantity must be a positive integer")

    cart = cart_repo.get_cart_by_customer(customer_id)

    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    item_found = False

    for item in cart.items:
        if item.name == item_name:
            item.quantity = quantity
            item_found = True
            break

    if not item_found:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart.subtotal = sum(item.price * item.quantity for item in cart.items)
    cart.tax = round(cart.subtotal * 0.12, 2)
    cart.total = round(cart.subtotal + cart.tax, 2)

    return cart_repo.update_cart(cart)


def update_cart_item_quantity(customer_id: int, item_name: str, quantity: int):
    """Updates the quantity of an item in the customer's cart."""

    customer = customer_repository.get_customer_by_id(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    if not customer.is_active:
        raise HTTPException(status_code=403, detail="Customer is deactivated")

    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        raise HTTPException(status_code=422, detail="Quantity must be a positive integer")

    cart = cart_repo.get_cart_by_customer(customer_id)

    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    item_found = False

    for item in cart.items:
        if item.name == item_name:
            item.quantity = quantity
            item_found = True
            break

    if not item_found:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart.subtotal = sum(item.price * item.quantity for item in cart.items)
    cart.tax = round(cart.subtotal * 0.12, 2)
    cart.total = round(cart.subtotal + cart.tax, 2)

    return cart_repo.update_cart(cart)

def remove_cart_item(customer_id: int, item_name: str):
    """Removes an item from the customer's active cart."""

    customer = customer_repository.get_customer_by_id(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    if not customer.is_active:
        raise HTTPException(status_code=403, detail="Customer is deactivated")

    cart = cart_repo.get_cart_by_customer(customer_id)

    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    item_found = False

    for item in cart.items:
        if item.name == item_name:
            cart.items.remove(item)
            item_found = True
            break

    if not item_found:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart.subtotal = sum(item.price * item.quantity for item in cart.items)
    cart.tax = round(cart.subtotal * 0.12, 2)
    cart.total = round(cart.subtotal + cart.tax, 2)

    return cart_repo.update_cart(cart)