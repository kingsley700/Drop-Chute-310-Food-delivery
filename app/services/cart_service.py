from fastapi import HTTPException
from app.repositories import cart_repo, customer_repository


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