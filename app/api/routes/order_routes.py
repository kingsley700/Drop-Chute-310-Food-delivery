from fastapi import APIRouter
from app.services import order_service
from app.schemas.order import OrderResponse

router = APIRouter()


# Create order
@router.post("/customers/{customer_id}/orders", response_model=OrderResponse)
def create_order(customer_id: int):
    return order_service.create_order(customer_id)


# Retrieve order history
@router.get("/customers/{customer_id}/orders", response_model=list[OrderResponse])
def get_order_history(customer_id: int):
    return order_service.get_order_history(customer_id)


# Retrieve individual order
@router.get("/customers/{customer_id}/orders/{order_id}", response_model=OrderResponse)
def get_order(customer_id: int, order_id: int):
    return order_service.get_order_by_id(customer_id, order_id)