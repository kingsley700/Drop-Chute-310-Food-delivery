from fastapi import APIRouter

from app.services import checkout_service

router = APIRouter()


# Validate checkout
@router.post("/customers/{customer_id}/checkout/validate")
def validate_checkout(customer_id: int):
    cart = checkout_service.validate_checkout(customer_id)
    cart = checkout_service.validate_menu_items(cart)

    return cart