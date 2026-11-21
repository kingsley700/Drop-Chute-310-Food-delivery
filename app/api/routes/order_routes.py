from fastapi import APIRouter

from app.services import order_service
from app.schemas.order import OrderResponse

router = APIRouter()


@router.post("/customers/{customer_id}/orders", response_model=OrderResponse)
def create_order(customer_id: int):
    return order_service.create_order(customer_id)